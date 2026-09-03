/**
 * Office Script — Importação da programação de voos para o Mapa de Alocação.
 *
 * Onde roda: Excel Online → Automatizar → Novo Script, colar e salvar como
 * "Importar programacao". O Power Automate o chama com a ação "Executar script".
 *
 * O que faz, nesta ordem:
 *   1. lê a planilha de movimentos (uma linha por POUSO ou DECOLAGEM);
 *   2. pareia cada pouso com a decolagem correspondente;
 *   3. aloca posição e portão pela preferência da companhia, com queda;
 *   4. devolve os registros prontos e as pendências, sem gravar nada.
 *
 * Ele NÃO grava no SharePoint: quem grava é o fluxo, que recebe este retorno.
 * Assim dá para rodar o script sozinho e conferir a saída antes de existir fluxo.
 *
 * ⚠️ As tabelas de configuração abaixo são um ESPELHO do App.Formulas
 * (colPrefPosicao, colPosicoes, colCias). O Office Script não consegue ler o app,
 * então as duas convivem. Mexeu numa, mexa na outra — e a divergência não dá erro,
 * só produz alocação diferente da que a tela recusaria depois.
 */

// ============================================================ configuração
const AEROPORTO = "NAVEGANTES";

/** Preferência por companhia: espelha colPrefPosicao. */
const PREF: { [nomePlanilha: string]: { sigla: string; posicoes: string[]; portoes: string[] } } = {
  GOL: { sigla: "GLO", posicoes: ["T4", "T3", "T5", "T2"], portoes: ["4", "5"] },
  LATAM: { sigla: "TAM", posicoes: ["T6", "T5", "T4", "T3"], portoes: ["1", "2", "3", "5"] },
  AZUL: { sigla: "AZU", posicoes: ["T5", "T3", "T2", "T6"], portoes: ["3", "2", "4", "1"] },
  ABSA: { sigla: "ABS", posicoes: ["T6C"], portoes: [] },
};

/** Queda quando a preferência está toda ocupada: a linha cia "*" de colPrefPosicao. */
const QUEDA_POSICOES = ["T6", "T5", "T4", "T3", "T2", "T1"];
const QUEDA_PORTOES = ["1", "2", "3", "4", "5"];

/** id_posicao e pátio: espelha colPosicoes. */
const POSICAO: { [codigo: string]: { id: number; patio: string } } = {
  T1: { id: 1, patio: "PRINCIPAL" }, T2: { id: 2, patio: "PRINCIPAL" },
  T3: { id: 3, patio: "PRINCIPAL" }, T4: { id: 4, patio: "PRINCIPAL" },
  T5: { id: 5, patio: "PRINCIPAL" }, T6: { id: 6, patio: "PRINCIPAL" },
  T7: { id: 7, patio: "PRINCIPAL" }, T6C: { id: 26, patio: "PRINCIPAL" },
};

/** Posição que consome outras: espelha a coluna 'ocupa'. Declarado num lado só. */
const OCUPA: { [codigo: string]: string[] } = { T6C: ["T5", "T6"] };

/** Equivalência IATA da planilha → código do catálogo tb_equipamentos. */
const EQUIPAMENTO: { [iata: string]: string } = {
  "73H": "B738", "7M8": "B38M", "320": "A320", "319": "A319", "295": "E295", "76V": "B763",
};

/** Rotas internacionais: aparecendo na chegada ou na saída, o registro nasce com internacional = 1. */
const DESTINOS_INTERNACIONAIS = ["AGT"];

/** Acima disso não é a mesma aeronave girando — o pouso fica sem par. */
const MAX_SOLO_MIN = 24 * 60;

/** Penalidades do pareamento. Tempo em solo é o sinal forte; rota e tipo desempatam. */
const PENA_ROTA = 90;
const PENA_AERONAVE = 30;

// ============================================================ tipos
interface Movimento {
  abs: number;      // minutos desde a época do Excel — pernoite cai naturalmente no mesmo par
  serial: number;   // dia (serial do Excel)
  min: number;      // minuto dentro do dia
  cia: string; voo: string; rota: string; aeronave: string; movimento: string;
}
interface Registro {
  aeroporto: string; data_operacao: string; data_fim: string;
  id_posicao: number; posicao_txt: string; patio_txt: string;
  cia_sigla: string; voo_chegada: string; voo_saida: string;
  equipamento: string; hora_inicio: number; hora_fim: number;
  portao: string; tipo_registro: string; pesquisado: number;
  internacional: number; observacao: string; origem: string; ativo: number;
}
interface Pendencia {
  tipo: string; data: string; hora: string; empresa: string;
  voo: string; rota: string; aeronave: string; motivo: string;
}
interface Resultado {
  ok: boolean; mensagem: string; mes_ref: string;
  total: number; registros: Registro[]; pendencias: Pendencia[];
}

// ============================================================ utilidades
function semAcento(t: string): string {
  return t.toLowerCase()
    .replace(/[áàâã]/g, "a").replace(/[éê]/g, "e").replace(/í/g, "i")
    .replace(/[óôõ]/g, "o").replace(/ú/g, "u").replace(/ç/g, "c").trim();
}
function dataIso(serial: number): string {
  const d = new Date(Date.UTC(1899, 11, 30) + serial * 86400000);
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${d.getUTCFullYear()}-${mm}-${dd}`;
}
function hhmm(min: number): string {
  return String(Math.floor(min / 60)).padStart(2, "0") + ":" + String(min % 60).padStart(2, "0");
}
/** Posições cuja ocupação impede <codigo>: as que ele consome, mais as que o consomem. */
function bloqueadasPor(codigo: string): string[] {
  const fora: string[] = [codigo];
  const consome = OCUPA[codigo];
  if (consome) { for (const c of consome) fora.push(c); }
  for (const chave of Object.keys(OCUPA)) {
    if (OCUPA[chave].indexOf(codigo) >= 0 && fora.indexOf(chave) < 0) fora.push(chave);
  }
  return fora;
}

// ============================================================ principal
function main(workbook: ExcelScript.Workbook, mesRef: string = ""): Resultado {
  const planilha = workbook.getWorksheets()[0];
  const dados = planilha.getUsedRange().getValues();
  if (dados.length < 2) {
    return { ok: false, mensagem: "A planilha não tem linhas de dados.", mes_ref: mesRef, total: 0, registros: [], pendencias: [] };
  }

  // --- cabeçalho por nome, não por posição: a ordem das colunas pode mudar entre meses
  const cab = dados[0].map(c => semAcento(String(c)));
  const col = { hora: -1, data: -1, empresa: -1, voo: -1, rota: -1, aeronave: -1, movimento: -1 };
  for (let i = 0; i < cab.length; i++) {
    const c = cab[i];
    if (col.hora < 0 && c.indexOf("horario") >= 0) col.hora = i;
    else if (c === "data") col.data = i;
    else if (c === "empresa") col.empresa = i;
    else if (c === "voo") col.voo = i;
    else if (c === "rota") col.rota = i;
    else if (c === "aeronave") col.aeronave = i;
    else if (c.indexOf("pouso") >= 0) col.movimento = i;
  }
  const faltando: string[] = [];
  if (col.hora < 0) faltando.push("Horário");
  if (col.data < 0) faltando.push("Data");
  if (col.empresa < 0) faltando.push("Empresa");
  if (col.voo < 0) faltando.push("Voo");
  if (col.rota < 0) faltando.push("Rota");
  if (col.aeronave < 0) faltando.push("Aeronave");
  if (col.movimento < 0) faltando.push("POUSO ou DECOLAGEM");
  if (faltando.length) {
    return { ok: false, mensagem: "Colunas não encontradas na planilha: " + faltando.join(", "), mes_ref: mesRef, total: 0, registros: [], pendencias: [] };
  }

  // --- leitura
  const movimentos: Movimento[] = [];
  for (let l = 1; l < dados.length; l++) {
    const linha = dados[l];
    const serial = Number(linha[col.data]);
    const fracao = Number(linha[col.hora]);
    if (!serial || isNaN(serial) || isNaN(fracao)) continue;
    const min = Math.round(fracao * 1440);
    movimentos.push({
      abs: serial * 1440 + min, serial: serial, min: min,
      cia: String(linha[col.empresa]).trim(),
      voo: String(linha[col.voo]).trim(),
      rota: String(linha[col.rota]).trim(),
      aeronave: String(linha[col.aeronave]).trim(),
      movimento: semAcento(String(linha[col.movimento])),
    });
  }
  if (!movimentos.length) {
    return { ok: false, mensagem: "Nenhuma linha com data e horário válidos.", mes_ref: mesRef, total: 0, registros: [], pendencias: [] };
  }

  const pousos = movimentos.filter(m => m.movimento.indexOf("pouso") >= 0).sort((a, b) => a.abs - b.abs);
  const decolagens = movimentos.filter(m => m.movimento.indexOf("decolagem") >= 0).sort((a, b) => a.abs - b.abs);

  // --- pareamento: menor tempo em solo, com rota e aeronave como desempate
  const usada: boolean[] = decolagens.map(() => false);
  const pares: { p: Movimento; d: Movimento }[] = [];
  const pousoSolto: Movimento[] = [];
  for (const p of pousos) {
    let melhor = -1;
    let custoMelhor = Number.MAX_SAFE_INTEGER;
    for (let i = 0; i < decolagens.length; i++) {
      const d = decolagens[i];
      if (usada[i] || d.abs <= p.abs || d.cia !== p.cia) continue;
      const solo = d.abs - p.abs;
      if (solo > MAX_SOLO_MIN) break;
      const custo = solo + (d.rota !== p.rota ? PENA_ROTA : 0) + (d.aeronave !== p.aeronave ? PENA_AERONAVE : 0);
      if (custo < custoMelhor) { custoMelhor = custo; melhor = i; }
    }
    if (melhor < 0) pousoSolto.push(p);
    else { usada[melhor] = true; pares.push({ p: p, d: decolagens[melhor] }); }
  }

  // --- mês escolhido: filtra pela data do POUSO, para o pernoite não se partir ao meio
  const paresDoMes = mesRef
    ? pares.filter(x => dataIso(x.p.serial).substring(0, 7) === mesRef)
    : pares;

  // --- alocação
  const ocupPosicao: { [k: string]: number[][] } = {};
  const ocupPortao: { [k: string]: number[][] } = {};
  const livre = (mapa: { [k: string]: number[][] }, chave: string, ini: number, fim: number): boolean => {
    const faixas = mapa[chave];
    if (!faixas) return true;
    for (const f of faixas) { if (f[0] < fim && f[1] > ini) return false; }
    return true;
  };
  const marcar = (mapa: { [k: string]: number[][] }, chave: string, ini: number, fim: number): void => {
    if (!mapa[chave]) mapa[chave] = [];
    mapa[chave].push([ini, fim]);
  };

  const registros: Registro[] = [];
  const pendencias: Pendencia[] = [];
  for (const par of paresDoMes.sort((a, b) => a.p.abs - b.p.abs)) {
    const pref = PREF[par.p.cia];
    if (!pref) {
      pendencias.push(pendencia("EMPRESA DESCONHECIDA", par.p, par.d, "empresa sem preferência cadastrada"));
      continue;
    }
    const ini = par.p.abs;
    const fim = par.d.abs;

    // posição: preferência da companhia, depois a queda geral. Cargueiro não cai — só T6C serve.
    const candidatas = pref.portoes.length ? pref.posicoes.concat(QUEDA_POSICOES) : pref.posicoes;
    let posicao = "";
    for (const c of candidatas) {
      let cabe = true;
      for (const b of bloqueadasPor(c)) { if (!livre(ocupPosicao, b, ini, fim)) { cabe = false; break; } }
      if (cabe) { posicao = c; break; }
    }
    if (!posicao) {
      pendencias.push(pendencia("SEM POSICAO", par.p, par.d, "nenhuma posição livre na preferência nem na queda"));
      continue;
    }
    for (const b of bloqueadasPor(posicao)) marcar(ocupPosicao, b, ini, fim);

    // portão: preferência, depois qualquer um livre. Melhor um portão fora do habitual que nenhum.
    let portao = "";
    if (pref.portoes.length) {
      for (const g of pref.portoes.concat(QUEDA_PORTOES)) {
        if (livre(ocupPortao, g, ini, fim)) { portao = g; break; }
      }
      if (portao) marcar(ocupPortao, portao, ini, fim);
    }

    let internacional = 0;
    for (const d of DESTINOS_INTERNACIONAIS) {
      if (par.p.rota.indexOf(d) >= 0 || par.d.rota.indexOf(d) >= 0) { internacional = 1; break; }
    }

    registros.push({
      aeroporto: AEROPORTO,
      data_operacao: dataIso(par.p.serial),
      data_fim: dataIso(par.d.serial),
      id_posicao: POSICAO[posicao].id,
      posicao_txt: posicao,
      patio_txt: POSICAO[posicao].patio,
      cia_sigla: pref.sigla,
      voo_chegada: par.p.voo,
      voo_saida: par.d.voo,
      equipamento: EQUIPAMENTO[par.p.aeronave] || "",
      hora_inicio: par.p.min,
      hora_fim: par.d.min,
      portao: portao,
      tipo_registro: "VOO",
      pesquisado: 0,
      internacional: internacional,
      observacao: "IMPORTACAO " + (mesRef || dataIso(par.p.serial).substring(0, 7)),
      origem: "IMPORTACAO " + (mesRef || dataIso(par.p.serial).substring(0, 7)),
      ativo: 1,
    });
  }

  // --- o que não pareou entra como pendência: nada some em silêncio
  for (const p of pousoSolto) {
    if (mesRef && dataIso(p.serial).substring(0, 7) !== mesRef) continue;
    pendencias.push(pendencia("POUSO SEM PAR", p, p, "decolagem fora do arquivo ou do período"));
  }
  for (let i = 0; i < decolagens.length; i++) {
    if (usada[i]) continue;
    const d = decolagens[i];
    if (mesRef && dataIso(d.serial).substring(0, 7) !== mesRef) continue;
    pendencias.push(pendencia("DECOLAGEM SEM PAR", d, d, "pouso fora do arquivo ou do período"));
  }

  const semEquip = registros.filter(r => !r.equipamento).length;
  const avisos: string[] = [];
  if (semEquip) avisos.push(semEquip + " registro(s) sem equivalência de equipamento");
  if (pendencias.length) avisos.push(pendencias.length + " pendência(s)");

  const resultado: Resultado = {
    ok: true,
    mensagem: registros.length + " registro(s) prontos" + (avisos.length ? " — " + avisos.join(", ") : ""),
    mes_ref: mesRef,
    total: registros.length,
    registros: registros,
    pendencias: pendencias,
  };

  // O editor do Office Scripts nao mostra o valor de retorno — so o console.log. Estes logs
  // existem para dar para conferir o script rodando sozinho, antes de existir fluxo.
  // O Power Automate ignora o log e usa o retorno.
  // Uma chamada por bloco, nao uma por linha: console.log dentro de laco e lento e o editor avisa.
  const log: string[] = [];
  log.push(resultado.mensagem);
  log.push("mes: " + (mesRef || "todos") + " | registros: " + registros.length + " | pendencias: " + pendencias.length);
  if (pendencias.length) {
    log.push("--- pendencias ---");
    log.push(pendencias.map(p =>
      p.tipo + " | " + p.data + " " + p.hora + " | " + p.empresa + " " + p.voo + " | " + p.rota + " | " + p.motivo
    ).join("\n"));
  }
  log.push("--- amostra dos 5 primeiros ---");
  log.push(registros.slice(0, 5).map(r =>
    r.data_operacao + " " + hhmm(r.hora_inicio) + "-" + hhmm(r.hora_fim) +
    " | " + r.posicao_txt + " portao " + (r.portao || "-") +
    " | " + r.cia_sigla + " " + r.voo_chegada + "/" + r.voo_saida + " | " + r.equipamento
  ).join("\n"));
  const porPosicao: { [k: string]: number } = {};
  for (const r of registros) porPosicao[r.posicao_txt] = (porPosicao[r.posicao_txt] || 0) + 1;
  log.push("--- uso por posicao ---");
  log.push(Object.keys(porPosicao).sort().map(k => k + ": " + porPosicao[k]).join(" | "));
  console.log(log.join("\n"));

  return resultado;
}

function pendencia(tipo: string, p: Movimento, d: Movimento, motivo: string): Pendencia {
  return {
    tipo: tipo, data: dataIso(p.serial), hora: hhmm(p.min), empresa: p.cia,
    voo: p.voo === d.voo ? p.voo : p.voo + "/" + d.voo,
    rota: p.rota, aeronave: p.aeronave, motivo: motivo,
  };
}
