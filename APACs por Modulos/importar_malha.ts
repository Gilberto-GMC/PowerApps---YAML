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
 * TRÊS MODOS, pelo parâmetro mesRef:
 *   - ""          → descoberta: devolve as competências do arquivo e quantos voos tem cada uma,
 *                   com `registros` vazio. Serve para conferir o arquivo rodando o script à mão.
 *   - "TODAS"     → devolve todos os voos do arquivo, de todas as competências. É o padrão da tela:
 *                   um anexo importa a temporada inteira.
 *   - "2026-10"   → devolve só os voos daquela competência.
 *
 * Tamanho: a temporada de verão 2027 tem 3.841 voos, cerca de 850 KB de retorno — abaixo do
 * limite de retorno do Office Script no Power Automate. O fluxo grava em lotes de 50.
 *
 * `filtro` sai pronto para o $filter do "Obter itens" que apaga a importação anterior:
 *   competencia eq '2026-10' or competencia eq '2026-11' ...
 * Montar isso aqui, e não no fluxo, deixa a parte perigosa (o que apagar) testável sem fluxo.
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
  filtro: string;
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

function main(workbook: ExcelScript.Workbook, mesRef: string = "", aeroporto: string = ""): Resultado {
  const aero = (aeroporto || AEROPORTO).trim().toUpperCase();
  const modo = (mesRef || "").trim().toUpperCase();
  const vazio: Resultado = {
    ok: false, mensagem: "", aeroporto: aero, mes_ref: modo,
    total: 0, descartados: 0, competencias: [], filtro: "", registros: [],
  };

  // Competência escrita errado ("12/2026", "dez") não casaria com nada e o fluxo gravaria zero
  // registros sem erro. Recusar aqui dá mensagem legível na tela.
  if (modo !== "" && modo !== "TODAS" && !/^\d{4}-\d{2}$/.test(modo)) {
    vazio.mensagem = "Competência inválida: \"" + mesRef + "\". Use TODAS ou o formato AAAA-MM.";
    return vazio;
  }

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
    vazio.mensagem = "Colunas não encontradas na planilha: " + faltando.join(", ") +
      ". Confira se o arquivo é o export de DECOLAGENS do Power BI.";
    return vazio;
  }

  // --- leitura
  const registros: Registro[] = [];
  const contagem: { [comp: string]: number } = {};
  const devolvidas: { [comp: string]: boolean } = {};
  let descartados = 0;

  for (let l = 1; l < dados.length; l++) {
    const linha = dados[l];
    const serial = Number(linha[col.data]);
    const fracao = Number(linha[col.hora]);

    // O rodapé do export do Power BI traz linhas de "Filtros aplicados:" sem data — caem aqui.
    if (!serial || isNaN(serial) || isNaN(fracao)) {
      descartados++;
      continue;
    }

    const data = serialParaData(serial);
    const competencia = data.substring(0, 7);
    contagem[competencia] = (contagem[competencia] || 0) + 1;

    if (modo === "" || (modo !== "TODAS" && competencia !== modo)) continue;

    // Math.round e não Math.floor: 0,2152777… × 1440 = 309,99996, que é 05:10 e não 05:09.
    const min = Math.round(fracao * 1440);

    devolvidas[competencia] = true;
    registros.push({
      aeroporto: aero,
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

  if (modo === "") {
    return {
      ok: true,
      mensagem: "Encontradas " + competencias.length + " competências na planilha: " +
        competencias.map(c => c.competencia + " (" + c.voos + ")").join(", ") + ".",
      aeroporto: aero,
      mes_ref: "",
      total: 0,
      descartados: descartados,
      competencias: competencias,
      filtro: "",
      registros: [],
    };
  }

  if (!registros.length) {
    return {
      ok: false,
      mensagem: (modo === "TODAS" ? "Nenhum voo lido no arquivo." : "Nenhum voo em " + modo + ".") +
        " A planilha tem: " + (chaves.length ? chaves.join(", ") : "nenhuma competência reconhecível") + ".",
      aeroporto: aero,
      mes_ref: modo,
      total: 0,
      descartados: descartados,
      competencias: competencias,
      filtro: "",
      registros: [],
    };
  }

  // Só as competências que ESTE retorno grava entram no filtro: importar dezembro não pode apagar
  // outubro. E o aeroporto fica de fora de propósito — o fluxo o acrescenta pelo item da tela.
  const gravadas = Object.keys(devolvidas).sort();
  const filtro = gravadas.map(c => "competencia eq '" + c + "'").join(" or ");

  return {
    ok: true,
    mensagem: registros.length + " voos lidos (" + gravadas.join(", ") + ")" +
      (descartados ? "; " + descartados + " linha(s) sem data ignorada(s)" : "") + ".",
    aeroporto: aero,
    mes_ref: modo,
    total: registros.length,
    descartados: descartados,
    competencias: competencias,
    filtro: filtro,
    registros: registros,
  };
}
