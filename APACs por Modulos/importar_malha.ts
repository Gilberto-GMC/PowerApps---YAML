/**
 * Office Script — Importação da malha planejada de decolagens para o app APACs por Módulos.
 *
 * Onde roda: Excel Online → Automatizar → Novo Script, colar e salvar como "Importar malha APAC".
 * O Power Automate o chama com a ação "Executar script do SharePoint".
 *
 * ⚠️ O script deve ficar em `Documentos › Roteiros` do site, e a ação é
 * *Run script from SharePoint library*. O "Mover script" do Excel ignora a pasta escolhida e
 * usa a padrão LOCALIZADA — em português, `Roteiros`. Criar uma pasta `Scripts` antes não adianta.
 * (Lição da importação do Mapa de Alocação, 03/09/2026.)
 *
 * O que faz:
 *   1. lê o export do Power BI (uma linha por DECOLAGEM);
 *   2. converte data serial e hora fracionária em data + minutos desde 00:00;
 *   3. devolve os registros de UMA competência, prontos para gravar — sem gravar nada.
 *
 * Ele NÃO grava no SharePoint: quem grava é o fluxo, que recebe este retorno. Assim dá para
 * rodar o script sozinho e conferir a saída antes de existir fluxo.
 *
 * DOIS MODOS:
 *   - `mesRef` vazio  → modo descoberta: devolve as competências encontradas e quantos voos tem
 *                        cada uma, com `registros` vazio. É o que a tela usa para montar a lista.
 *   - `mesRef` = "2026-10" → devolve os registros daquele mês.
 *
 * O modo descoberta existe por causa do tamanho: uma temporada tem ~3.800 voos, e devolver tudo
 * de uma vez estoura o que o fluxo aguenta com folga. Um mês são ~730 — a mesma ordem de grandeza
 * dos 698 que a importação do Mapa já processa sem reclamar.
 *
 * ⚠️ O fluxo tem de APAGAR os registros da competência antes de gravar, senão reimportar duplica.
 *    O `competencia` devolvido aqui é o que ele usa para filtrar.
 */

const AEROPORTO = "NAVEGANTES";

interface Registro {
  aeroporto: string;
  competencia: string;
  data: string;        // AAAA-MM-DD
  hora_min: number;    // minutos desde 00:00
  empresa: string;
  voo: string;
  rota: string;
  aeronave: string;
  assentos: number;
  tipo_voo: string;
  dia_semana: string;
  ativo: number;
}

interface Competencia {
  competencia: string;
  voos: number;
}

interface Resultado {
  ok: boolean;
  mensagem: string;
  aeroporto: string;
  mes_ref: string;
  total: number;
  descartados: number;
  competencias: Competencia[];
  registros: Registro[];
}

function semAcento(t: string): string {
  return t
    .toLowerCase()
    .replace(/[áàâã]/g, "a")
    .replace(/[éê]/g, "e")
    .replace(/[í]/g, "i")
    .replace(/[óôõ]/g, "o")
    .replace(/[úü]/g, "u")
    .replace(/[ç]/g, "c")
    .trim();
}

/** Serial do Excel para AAAA-MM-DD. 25569 = 01/01/1970; 86400000 ms por dia. */
function serialParaData(serial: number): string {
  const ms = Math.round((serial - 25569) * 86400000);
  const d = new Date(ms);
  const mes = d.getUTCMonth() + 1;
  const dia = d.getUTCDate();
  return (
    d.getUTCFullYear() + "-" + (mes < 10 ? "0" + mes : "" + mes) + "-" + (dia < 10 ? "0" + dia : "" + dia)
  );
}

function main(workbook: ExcelScript.Workbook, mesRef: string = ""): Resultado {
  const vazio: Resultado = {
    ok: false, mensagem: "", aeroporto: AEROPORTO, mes_ref: mesRef,
    total: 0, descartados: 0, competencias: [], registros: [],
  };

  const planilha = workbook.getWorksheets()[0];
  const dados = planilha.getUsedRange().getValues();
  if (dados.length < 2) {
    vazio.mensagem = "A planilha não tem linhas de dados.";
    return vazio;
  }

  // --- cabeçalho por NOME, não por posição: o Power BI pode reordenar o relatório.
  const cab = dados[0].map(c => semAcento(String(c)));
  const col = { hora: -1, data: -1, empresa: -1, voo: -1, rota: -1, aeronave: -1, assentos: -1, tipo: -1, dia: -1 };
  for (let i = 0; i < cab.length; i++) {
    const c = cab[i];
    if (col.hora < 0 && c.indexOf("horario") >= 0) col.hora = i;
    else if (c === "data") col.data = i;
    else if (c === "empresa") col.empresa = i;
    else if (c === "voo") col.voo = i;
    else if (c === "rota") col.rota = i;
    else if (c === "aeronave") col.aeronave = i;
    else if (c === "assentos") col.assentos = i;
    else if (c.indexOf("tipo") >= 0) col.tipo = i;
    else if (c === "dia") col.dia = i;
  }

  const faltando: string[] = [];
  if (col.hora < 0) faltando.push("Horário");
  if (col.data < 0) faltando.push("Data");
  if (col.voo < 0) faltando.push("Voo");
  if (col.assentos < 0) faltando.push("Assentos");
  if (faltando.length) {
    vazio.mensagem = "Colunas não encontradas na planilha: " + faltando.join(", ");
    return vazio;
  }

  // --- leitura
  const registros: Registro[] = [];
  const contagem: { [comp: string]: number } = {};
  let descartados = 0;

  for (let l = 1; l < dados.length; l++) {
    const linha = dados[l];
    const serial = Number(linha[col.data]);
    const fracao = Number(linha[col.hora]);

    // O rodapé do export do Power BI traz uma linha de "Filtros aplicados:" sem data — cai aqui.
    if (!serial || isNaN(serial) || isNaN(fracao)) {
      descartados++;
      continue;
    }

    const data = serialParaData(serial);
    const competencia = data.substring(0, 7);
    contagem[competencia] = (contagem[competencia] || 0) + 1;

    if (mesRef && competencia !== mesRef) continue;

    // Math.round e não Math.floor: 0,2152777… × 1440 = 309,99996, que é 05:10 e não 05:09.
    const min = Math.round(fracao * 1440);

    registros.push({
      aeroporto: AEROPORTO,
      competencia: competencia,
      data: data,
      hora_min: min < 0 ? 0 : min > 1439 ? 1439 : min,
      empresa: col.empresa >= 0 ? String(linha[col.empresa] || "") : "",
      voo: String(linha[col.voo] || ""),
      rota: col.rota >= 0 ? String(linha[col.rota] || "") : "",
      aeronave: col.aeronave >= 0 ? String(linha[col.aeronave] || "") : "",
      // Cargueiro vem com 0 assentos. Fica: não gera volumetria nem conta decolagem, mas
      // sumir com voo da malha é pior que mostrá-lo valendo zero.
      assentos: Number(linha[col.assentos]) || 0,
      tipo_voo: col.tipo >= 0 ? String(linha[col.tipo] || "") : "",
      dia_semana: col.dia >= 0 ? String(linha[col.dia] || "") : "",
      ativo: 1,
    });
  }

  const competencias: Competencia[] = [];
  const chaves = Object.keys(contagem).sort();
  for (let i = 0; i < chaves.length; i++) {
    competencias.push({ competencia: chaves[i], voos: contagem[chaves[i]] });
  }

  if (!mesRef) {
    return {
      ok: true,
      mensagem: "Encontradas " + competencias.length + " competências na planilha.",
      aeroporto: AEROPORTO,
      mes_ref: "",
      total: 0,
      descartados: descartados,
      competencias: competencias,
      registros: [],
    };
  }

  if (!registros.length) {
    return {
      ok: false,
      mensagem: "Nenhum voo em " + mesRef + ". A planilha tem: " + chaves.join(", "),
      aeroporto: AEROPORTO,
      mes_ref: mesRef,
      total: 0,
      descartados: descartados,
      competencias: competencias,
      registros: [],
    };
  }

  return {
    ok: true,
    mensagem: registros.length + " voos lidos para " + mesRef + ".",
    aeroporto: AEROPORTO,
    mes_ref: mesRef,
    total: registros.length,
    descartados: descartados,
    competencias: competencias,
    registros: registros,
  };
}
