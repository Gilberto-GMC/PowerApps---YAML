// montar_fluxo_importacao.js — refaz o pacote do fluxo "Importar programacao" com tratamento de erro
// que funciona.
//
// Uso:  node montar_fluxo_importacao.js
//         [--entrada=fluxo_importar_programacao.definition.json]
//         [--pacote=Importarprogramacao_COMPLETO.zip]      pacote-base: manifestos e ids são mantidos
//         [--saida=.]                                        onde gravar definição e .zip
//
// ⚠️ O DEFEITO QUE ISTO CORRIGE (14/09/2026). O Marcar_erro tinha runAfter apontando para seis ações ao
// mesmo tempo, cada uma com ["Failed","TimedOut"]. Com várias ações no runAfter, o Power Automate só
// executa quando TODAS terminam num dos estados listados. Quando uma falha, as seguintes ficam
// "Skipped" — que não está na lista — e o Marcar_erro é pulado. O item de tb_importacaoMapa ficava em
// PROCESSANDO para sempre, com a barra da scrMapaImport parada.
//
// A CORREÇÃO. O trabalho (Obter_anexos … Fechar) vai para um Scope "Processar", e o Marcar_erro depende
// só dele: { Processar: ["Failed","TimedOut"] }. O escopo falha se qualquer ação de dentro falhar.
// Inicializar_contador sai do fluxo de trabalho e sobe para o nível de cima, antes do escopo: variável
// não pode ser inicializada dentro de escopo.
//
// O que NÃO muda: a costura do Office Script (Compose Resultado_script), a condição de gatilho
// status = PRONTO, os ids e manifestos do pacote (que importou neste tenant), a ordem das entradas do zip.
//
// Idempotente: aceita a definição plana (a antiga) ou já com o escopo, e produz a mesma saída.

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const AQUI = __dirname;
const arg = (nome, padrao) => {
  const a = process.argv.find((x) => x.startsWith("--" + nome + "="));
  return a ? a.slice(nome.length + 3) : padrao;
};
const ENTRADA = arg("entrada", path.join(AQUI, "fluxo_importar_programacao.definition.json"));
const PACOTE = arg("pacote", path.join(AQUI, "Importarprogramacao_COMPLETO.zip"));
const SAIDA = arg("saida", AQUI);

const erros = [];
const clone = (o) => JSON.parse(JSON.stringify(o));

// ------------------------------------------------------------------ entrada
const def = JSON.parse(fs.readFileSync(ENTRADA, "utf8"));
const wf = def.properties && def.properties.definition;
if (!wf || !wf.actions || !wf.triggers) { console.error("✗ definição com problema — nada foi gravado:\n   arquivo sem properties.definition"); process.exit(1); }

const TOPO = ["Marcar_processando", "Inicializar_contador", "Marcar_erro"];
const TRABALHO = ["Obter_anexos", "Obter_conteudo_do_anexo", "Salvar_planilha",
  "Obter_preposicoes", "Obter_posicoes", "Montar_config", "Resultado_script",
  "Guardar_total", "Conferir_resultado", "Obter_importacao_anterior", "Apagar_anteriores", "Gravar_registros", "Fechar"];

// planifica: se já existe o escopo Processar, as ações dele voltam para o mesmo saco
const plano = {};
for (const [k, v] of Object.entries(wf.actions)) {
  if (k === "Processar" && v.type === "Scope") {
    for (const [k2, v2] of Object.entries(v.actions || {})) plano[k2] = v2;
  } else {
    plano[k] = v;
  }
}
for (const k of Object.keys(plano)) {
  if (!TOPO.includes(k) && !TRABALHO.includes(k)) erros.push(`ação não prevista no nível de cima: ${k} — acrescente-a em TRABALHO ou TOPO conscientemente`);
}
// ------------------------------------------------------------------ 15/09/2026: aeroporto vindo das listas + trava da recusa
// Inseridas SÓ se faltarem (migração da definição antiga). Se já existem, ficam como estão e passam pelas
// conferências lá embaixo — regenerar apagaria o defeito que o teste planta e a conferência nunca veria nada.
//
// ⚠️ A trava corrige um defeito anterior a esta mudança: com ok = false (planilha errada, costura não ligada)
// o fluxo seguia, APAGAVA a importação anterior do mês, gravava zero e fechava como CONCLUIDO.
const INSERIDAS = [];
if (plano.Guardar_total) {
  const SITE = plano.Guardar_total.inputs.parameters.dataset;
  const obterLista = (tabela) => ({
    runAfter: {}, type: "OpenApiConnection",
    inputs: {
      parameters: { dataset: SITE, table: tabela, $filter: "aeroporto eq '@{triggerBody()?['aeroporto']}' and ativo eq 1", $top: 5000 },
      host: { apiId: "/providers/Microsoft.PowerApps/apis/shared_sharepointonline", connectionName: "shared_sharepointonline", operationId: "GetItems" },
      authentication: "@parameters('$authentication')",
    },
  });
  const insere = (nome, fabrica) => { if (!plano[nome]) { plano[nome] = fabrica(); INSERIDAS.push(nome); } };
  insere("Obter_preposicoes", () => obterLista("tb_prePosicao"));
  insere("Obter_posicoes", () => obterLista("tb_posicoes"));
  insere("Montar_config", () => ({
    runAfter: {}, type: "Compose",
    inputs: "@string(setProperty(setProperty(setProperty(json('{}'), 'aeroporto', triggerBody()?['aeroporto']), 'preposicoes', outputs('Obter_preposicoes')?['body/value']), 'posicoes', outputs('Obter_posicoes')?['body/value']))",
  }));
  insere("Conferir_resultado", () => {
    const recusa = clone(plano.Guardar_total);
    recusa.runAfter = {};
    recusa.inputs.parameters["item/status"] = "ERRO";
    recusa.inputs.parameters["item/mensagem"] = "@outputs('Resultado_script')?['mensagem']";
    return {
      runAfter: {}, type: "If",
      expression: { equals: ["@outputs('Resultado_script')?['ok']", true] },
      actions: {},
      else: {
        actions: {
          Gravar_recusa: recusa,
          Encerrar_recusa: { runAfter: { Gravar_recusa: ["Succeeded"] }, type: "Terminate", inputs: { runStatus: "Cancelled" } },
        },
      },
    };
  });
}

for (const n of TOPO.concat(TRABALHO)) if (!plano[n]) erros.push(`falta a ação ${n}`);

if (erros.length) {
  console.error("✗ definição com problema — nada foi gravado:");
  erros.forEach((e) => console.error("   " + e));
  process.exit(1);
}

// ------------------------------------------------------------------ remonta
const processar = {};
for (const n of TRABALHO) processar[n] = clone(plano[n]);
processar.Obter_anexos.runAfter = {};                                   // primeira do escopo
processar.Gravar_registros.runAfter = { Apagar_anteriores: ["Succeeded"] }; // antes vinha depois do Inicializar_contador
// Só as ações inseridas nesta rodada, e a seguinte a cada uma, são religadas na cadeia. NÃO reescrever a
// cadeia inteira: um runAfter errado que chegasse na definição seria consertado calado e a conferência
// nunca o veria (foi o que o teste "runAfter para ação de outro nível" pegou em 15/09/2026).
for (const n of INSERIDAS) {
  const i = TRABALHO.indexOf(n);
  processar[n].runAfter = { [TRABALHO[i - 1]]: ["Succeeded"] };
  const prox = TRABALHO[i + 1];
  if (prox && !INSERIDAS.includes(prox)) processar[prox].runAfter = { [n]: ["Succeeded"] };
}

const acoes = {};
acoes.Marcar_processando = Object.assign(clone(plano.Marcar_processando), { runAfter: {} });
acoes.Inicializar_contador = Object.assign(clone(plano.Inicializar_contador), { runAfter: { Marcar_processando: ["Succeeded"] } });
acoes.Processar = { runAfter: { Inicializar_contador: ["Succeeded"] }, type: "Scope", actions: processar };

const erro = clone(plano.Marcar_erro);
erro.runAfter = { Processar: ["Failed", "TimedOut"] };
// o contador já existe (foi inicializado antes do escopo): a tela mostra até onde chegou
erro.inputs.parameters["item/processados"] = "@variables('contador')";
erro.inputs.parameters["item/mensagem"] =
  "A importacao falhou no meio. Veja o historico do fluxo Importar programacao e importe de novo: a reimportacao apaga o que ficou pela metade.";
acoes.Marcar_erro = erro;

wf.actions = acoes;

// ------------------------------------------------------------------ conferências
const LISTAS = {
  "7b5a100a-e601-4ce5-894b-04daee5318c6": "lista_tb_importacaoMapa.json",   // GUID de tb_importacaoMapa, do gatilho
  tb_importacaoMapa: "lista_tb_importacaoMapa.json",
  tb_alocacoesMapa: "lista_tb_alocacoesMapa.json",
  tb_prePosicao: "lista_tb_prePosicao.json",
  tb_posicoes: "lista_tb_posicoes.json",
};
const esquema = {};
for (const [tabela, arq] of Object.entries(LISTAS)) {
  const d = JSON.parse(fs.readFileSync(path.join(AQUI, arq), "utf8"));
  esquema[tabela] = {
    nome: d.nomeLista,
    todas: d.colunas.map((c) => c.internalName),
    obrigatorias: d.colunas.filter((c) => /Required=.TRUE/i.test(c.schemaXml)).map((c) => c.internalName),
  };
}

// a trava contra laço infinito continua lá
const trg = Object.values(wf.triggers)[0];
if (!(trg.conditions || []).some((c) => /status'\]\s*,\s*'PRONTO'/.test(c.expression || ""))) erros.push("condição de gatilho status = PRONTO ausente");

// a costura continua sendo um Compose
if (processar.Resultado_script.type !== "Compose") erros.push("Resultado_script deixou de ser Compose — a costura do Office Script sumiu");

const nomes = new Map();
const iniciadas = new Set();
(function anda(as, nivel) {
  const irmas = new Set(Object.keys(as));
  for (const [n, a] of Object.entries(as)) {
    if (nomes.has(n)) erros.push(`nome de ação repetido: ${n}`);
    nomes.set(n, nivel);
    for (const dep of Object.keys(a.runAfter || {})) {
      if (!irmas.has(dep)) erros.push(`${n}: runAfter aponta para '${dep}', que não está no mesmo nível`);
    }
    if (a.type === "InitializeVariable") {
      if (nivel > 0) erros.push(`${n}: InitializeVariable fora do nível de cima`);
      for (const v of (a.inputs && a.inputs.variables) || []) iniciadas.add(v.name);
    }
    const op = a.inputs && a.inputs.host && a.inputs.host.operationId;
    if (op === "PatchItem" || op === "PostItem") {
      const p = a.inputs.parameters;
      const e = esquema[p.table];
      if (!e) erros.push(`${n}: lista desconhecida '${p.table}'`);
      else {
        for (const c of e.obrigatorias) if (!(("item/" + c) in p)) erros.push(`${n}: falta a obrigatória ${c}`);
        for (const k of Object.keys(p).filter((k) => k.startsWith("item/"))) {
          if (!e.todas.includes(k.slice(5))) erros.push(`${n}: coluna '${k.slice(5)}' não existe em ${e.nome}`);
        }
      }
    }
    if (op === "GetItems") {
      const p = a.inputs.parameters;
      const e = esquema[p.table];
      if (!e) erros.push(`${n}: lista desconhecida '${p.table}'`);
      else {
        for (const m of String(p.$filter || "").matchAll(/([A-Za-z_][A-Za-z0-9_]*)\s+(?:eq|ne|lt|le|gt|ge)\s/g)) {
          if (!e.todas.includes(m[1])) erros.push(`${n}: coluna '${m[1]}' do $filter não existe em ${e.nome}`);
        }
      }
    }
    if (a.actions) anda(a.actions, nivel + 1);
    if (a.else) anda(a.else.actions, nivel + 1);
  }
})(acoes, 0);

const texto = JSON.stringify(acoes);
for (const m of texto.matchAll(/(?:outputs|body|items|result)\('([^']+)'\)/g)) {
  if (!nomes.has(m[1])) erros.push(`referência a ação inexistente: ${m[1]}`);
}
for (const m of texto.matchAll(/variables\('([^']+)'\)/g)) {
  if (!iniciadas.has(m[1])) erros.push(`variável não inicializada: ${m[1]}`);
}
(function varre(as) {
  for (const a of Object.values(as)) {
    if (a.type === "IncrementVariable" && !iniciadas.has(a.inputs.name)) erros.push(`variável não inicializada: ${a.inputs.name}`);
    if (a.actions) varre(a.actions);
    if (a.else) varre(a.else.actions);
  }
})(acoes);
// items('X') só vale dentro do laço X
(function itens(as, lacos) {
  for (const [n, a] of Object.entries(as)) {
    const proprio = JSON.stringify(Object.assign({}, a, { actions: undefined, else: undefined }));
    for (const m of proprio.matchAll(/items\('([^']+)'\)/g)) {
      if (!lacos.includes(m[1])) erros.push(`${n}: usa items('${m[1]}') fora desse laço`);
    }
    const dentro = a.type === "Foreach" ? lacos.concat(n) : lacos;
    if (a.actions) itens(a.actions, dentro);
    if (a.else) itens(a.else.actions, dentro);
  }
})(acoes, []);

// o próprio defeito corrigido não pode voltar
const rae = Object.keys(acoes.Marcar_erro.runAfter);
if (rae.length !== 1 || rae[0] !== "Processar") erros.push("Marcar_erro tem de depender só do escopo Processar");

// a ordem do escopo é a de TRABALHO: cada ação depende só da anterior — é o que garante que a trava do ok
// vem antes do Obter_importacao_anterior, e a configuração antes do script
TRABALHO.forEach((n, i) => {
  const esperado = i === 0 ? "" : TRABALHO[i - 1] + ":Succeeded";
  const real = Object.entries(processar[n].runAfter || {}).map(([k, v]) => k + ":" + v.join("/")).join(",");
  if (real !== esperado) erros.push(`${n}: tem de vir logo depois de ${TRABALHO[i - 1] || "(início do escopo)"} — runAfter atual: ${real || "(vazio)"}`);
});

// a recusa do script tem de parar o fluxo ANTES de apagar a importação anterior
const cr = processar.Conferir_resultado;
if (!cr || cr.type !== "If" || !/Resultado_script'\)\?\['ok'\]/.test(JSON.stringify(cr.expression || ""))) {
  erros.push("Conferir_resultado tem de testar outputs('Resultado_script')?['ok']");
} else {
  const senao = Object.values((cr.else && cr.else.actions) || {});
  const gravaErro = senao.some((x) => x.inputs && x.inputs.parameters && x.inputs.parameters["item/status"] === "ERRO");
  const encerra = senao.some((x) => x.type === "Terminate");
  if (!gravaErro || !encerra) erros.push("Conferir_resultado: o ramo senão tem de gravar ERRO e encerrar");
  if (Object.keys(cr.actions || {}).length) erros.push("Conferir_resultado: o ramo sim tem de ficar vazio — o trabalho segue depois da condição");
}
// o script recebe a configuração do aeroporto
const mc = JSON.stringify((processar.Montar_config && processar.Montar_config.inputs) || "");
if (!/outputs\('Obter_preposicoes'\)/.test(mc) || !/outputs\('Obter_posicoes'\)/.test(mc)) {
  erros.push("Montar_config tem de levar Obter_preposicoes e Obter_posicoes");
}

// nenhuma ação sumiu nem apareceu na remontagem
const antes = Object.keys(plano).sort().join(",");
const depois = [...nomes.keys()].filter((n) => nomes.get(n) <= 1 && n !== "Processar").sort().join(",");
if (antes !== depois) erros.push(`a remontagem mudou o conjunto de ações: antes [${antes}] depois [${depois}]`);

if (erros.length) {
  console.error("✗ definição com problema — nada foi gravado:");
  erros.forEach((e) => console.error("   " + e));
  process.exit(1);
}

// ------------------------------------------------------------------ pacote
function lerZip(caminho) {
  const buf = fs.readFileSync(caminho);
  const entradas = [];
  let i = 0;
  while ((i = buf.indexOf(Buffer.from("PK\x03\x04"), i)) !== -1) {
    const metodo = buf.readUInt16LE(i + 8), tamComp = buf.readUInt32LE(i + 18);
    const tamNome = buf.readUInt16LE(i + 26), tamExtra = buf.readUInt16LE(i + 28);
    const nome = buf.slice(i + 30, i + 30 + tamNome).toString("utf8");
    const ini = i + 30 + tamNome + tamExtra;
    const d = buf.slice(ini, ini + tamComp);
    entradas.push([nome, metodo === 0 ? d.toString("utf8") : zlib.inflateRawSync(d).toString("utf8")]);
    i = ini + tamComp;
  }
  return entradas;
}
const base = lerZip(PACOTE);
// A pasta do fluxo no pacote tem id PRÓPRIO do pacote (6920fa71-…), diferente do name da definição
// (110540bd-…, o id do fluxo no ambiente de onde foi exportado). Acha-se pelo caminho, não pelo name.
const defsNoPacote = base.map(([n], i) => [n, i]).filter(([n]) => /^Microsoft\.Flow\/flows\/[^/]+\/definition\.json$/.test(n));
if (defsNoPacote.length !== 1) { console.error(`✗ o pacote-base tem ${defsNoPacote.length} definições de fluxo; esperava 1`); process.exit(1); }
const alvo = defsNoPacote[0][1];
const idNoPacote = defsNoPacote[0][0].split("/")[2];
const entradas = base.map(([n, c], i) => [n, i === alvo ? JSON.stringify(def) : c]);

function crc32(buf) {
  if (!crc32.t) {
    crc32.t = [];
    for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; crc32.t[n] = c >>> 0; }
  }
  let c = 0xffffffff;
  for (const b of buf) c = crc32.t[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
const locais = [], centrais = [];
let off = 0;
for (const [nome, conteudo] of entradas) {
  if (nome.includes("\\")) throw new Error("entrada com barra invertida: " + nome);   // o Power Automate recusa
  const dados = Buffer.from(conteudo, "utf8");
  const comp = zlib.deflateRawSync(dados, { level: 9 });
  const nb = Buffer.from(nome, "utf8");
  const crc = crc32(dados);
  const lh = Buffer.alloc(30);
  lh.writeUInt32LE(0x04034b50, 0); lh.writeUInt16LE(20, 4); lh.writeUInt16LE(0, 6); lh.writeUInt16LE(8, 8);
  lh.writeUInt16LE(0, 10); lh.writeUInt16LE(0, 12); lh.writeUInt32LE(crc, 14); lh.writeUInt32LE(comp.length, 18);
  lh.writeUInt32LE(dados.length, 22); lh.writeUInt16LE(nb.length, 26); lh.writeUInt16LE(0, 28);
  locais.push(lh, nb, comp);
  const ch = Buffer.alloc(46);
  ch.writeUInt32LE(0x02014b50, 0); ch.writeUInt16LE(20, 4); ch.writeUInt16LE(20, 6); ch.writeUInt16LE(0, 8);
  ch.writeUInt16LE(8, 10); ch.writeUInt16LE(0, 12); ch.writeUInt16LE(0, 14); ch.writeUInt32LE(crc, 16);
  ch.writeUInt32LE(comp.length, 20); ch.writeUInt32LE(dados.length, 24); ch.writeUInt16LE(nb.length, 28);
  ch.writeUInt16LE(0, 30); ch.writeUInt16LE(0, 32); ch.writeUInt16LE(0, 34); ch.writeUInt16LE(0, 36);
  ch.writeUInt32LE(0, 38); ch.writeUInt32LE(off, 42);
  centrais.push(ch, nb);
  off += 30 + nb.length + comp.length;
}
const corpo = Buffer.concat(locais), central = Buffer.concat(centrais), fim = Buffer.alloc(22);
fim.writeUInt32LE(0x06054b50, 0); fim.writeUInt16LE(0, 4); fim.writeUInt16LE(0, 6);
fim.writeUInt16LE(entradas.length, 8); fim.writeUInt16LE(entradas.length, 10);
fim.writeUInt32LE(central.length, 12); fim.writeUInt32LE(corpo.length, 16); fim.writeUInt16LE(0, 20);

// manifesto do pacote tem de continuar pedindo fluxo NOVO
const man = JSON.parse(entradas.find(([n]) => n === "manifest.json")[1]);
if (!man.resources[idNoPacote] || man.resources[idNoPacote].suggestedCreationType !== "New") {
  console.error(`✗ manifesto do pacote-base não declara o fluxo ${idNoPacote} como New`); process.exit(1);
}

fs.mkdirSync(SAIDA, { recursive: true });
fs.writeFileSync(path.join(SAIDA, "Importarprogramacao_COMPLETO.zip"), Buffer.concat([corpo, central, fim]));
fs.writeFileSync(path.join(SAIDA, "fluxo_importar_programacao.definition.json"), JSON.stringify(def, null, 2) + "\n");

console.log(`✓ ${nomes.size} ações (${Object.keys(processar).length} dentro do escopo Processar), 0 problemas nas conferências`);
console.log(`✓ Marcar_erro depende só de Processar; Inicializar_contador no nível de cima`);
console.log(`✓ Conferir_resultado para o fluxo antes de apagar quando o script recusa; config do aeroporto montada das listas`);
if (INSERIDAS.length) console.log(`  inseridas nesta rodada: ${INSERIDAS.join(", ")}`);
console.log(`✓ ${path.join(SAIDA, "Importarprogramacao_COMPLETO.zip")} (${entradas.length} entradas, mesma ordem do pacote-base)`);
