// testar_montar_fluxo_importacao.js — prova que as conferências do montar_fluxo_importacao.js RECUSAM defeito.
//
// Uso:  node testar_montar_fluxo_importacao.js
//
// Cada caso planta UM defeito numa cópia da definição (alterando o JSON como objeto, sem texto de shell),
// roda o gerador contra a cópia com saída numa pasta temporária, e exige:
//   1. a cópia difere da definição original — senão o teste não testou nada;
//   2. o gerador saiu com erro;
//   3. o erro é o da CONFERÊNCIA ("definição com problema") e cita o defeito plantado —
//      exceção ou erro de sintaxe não contam como recusa.
// Um caso de controle, sem defeito, tem de passar.
//
// Por que tanto cuidado: em 14/09/2026, um teste negativo feito em linha de shell leu os argumentos do
// node -e a partir de process.argv[2] (é [1]), trocou o texto errado e contou quebra como recusa.
// Verificação que não foi verificada aprova o que devia recusar.

const fs = require("fs");
const os = require("os");
const path = require("path");
const crypto = require("crypto");
const { spawnSync } = require("child_process");

const AQUI = __dirname;
const GERADOR = path.join(AQUI, "montar_fluxo_importacao.js");
const DEF = path.join(AQUI, "fluxo_importar_programacao.definition.json");
const ZIP = path.join(AQUI, "Importarprogramacao_COMPLETO.zip");
const hash = (p) => crypto.createHash("md5").update(fs.readFileSync(p)).digest("hex");
const hashAntes = [hash(DEF), hash(ZIP)];

const ORIGINAL = fs.readFileSync(DEF, "utf8");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "neg-mapa-"));

// acha uma ação pelo nome em qualquer nível (a definição pode estar plana ou já com o escopo)
function acao(wf, nome) {
  let achada = null;
  (function anda(as) {
    for (const [k, v] of Object.entries(as || {})) {
      if (k === nome) achada = v;
      if (v.actions) anda(v.actions);
      if (v.else) anda(v.else.actions);
    }
  })(wf.actions);
  if (!achada) throw new Error("caso de teste mal escrito: ação " + nome + " não existe na definição");
  return achada;
}

const CASOS = [
  {
    nome: "obrigatória faltando no PatchItem (pendencias do Fechar)",
    planta: (wf) => { delete acao(wf, "Fechar").inputs.parameters["item/pendencias"]; },
    espera: "Fechar: falta a obrigatória pendencias",
  },
  {
    nome: "obrigatória faltando no PostItem (ativo do Criar_registro)",
    planta: (wf) => { delete acao(wf, "Criar_registro").inputs.parameters["item/ativo"]; },
    espera: "Criar_registro: falta a obrigatória ativo",
  },
  {
    nome: "referência a ação que não existe",
    planta: (wf) => { acao(wf, "Apagar_anteriores").foreach = "@outputs('Obter_importacao_velha')?['body/value']"; },
    espera: "referência a ação inexistente: Obter_importacao_velha",
  },
  {
    nome: "coluna que não existe na lista",
    planta: (wf) => { acao(wf, "Criar_registro").inputs.parameters["item/origemX"] = "x"; },
    espera: "coluna 'origemX' não existe em tb_alocacoesMapa",
  },
  {
    nome: "runAfter para ação de outro nível",
    planta: (wf) => { acao(wf, "Fechar").runAfter = { Marcar_processando: ["Succeeded"] }; },
    espera: "Fechar: runAfter aponta para 'Marcar_processando', que não está no mesmo nível",
  },
  {
    nome: "variável não inicializada",
    planta: (wf) => { acao(wf, "Gravar_processados").inputs.parameters["item/processados"] = "@variables('contadorX')"; },
    espera: "variável não inicializada: contadorX",
  },
  {
    nome: "items() usado fora do próprio laço",
    planta: (wf) => { acao(wf, "Guardar_total").inputs.parameters["item/total"] = "@items('Gravar_registros')?['x']"; },
    espera: "Guardar_total: usa items('Gravar_registros') fora desse laço",
  },
  {
    nome: "ação desconhecida não é descartada calada",
    planta: (wf) => { wf.actions.Acao_nova = { runAfter: {}, type: "Compose", inputs: "x" }; },
    espera: "ação não prevista no nível de cima: Acao_nova",
  },
  {
    nome: "costura do Office Script removida",
    planta: (wf) => {
      const alvo = wf.actions.Processar && wf.actions.Processar.actions ? wf.actions.Processar.actions : wf.actions;
      delete alvo.Resultado_script;
    },
    espera: "falta a ação Resultado_script",
  },
  {
    nome: "trava do gatilho removida",
    planta: (wf) => { for (const t of Object.values(wf.triggers)) delete t.conditions; },
    espera: "condição de gatilho status = PRONTO ausente",
  },
  {
    nome: "$filter com coluna que não existe na lista",
    planta: (wf) => { acao(wf, "Obter_posicoes").inputs.parameters.$filter = "aeroportoX eq 'NAVEGANTES'"; },
    espera: "Obter_posicoes: coluna 'aeroportoX' do $filter não existe em tb_posicoes",
  },
  {
    nome: "trava do ok trocada por condição sempre verdadeira",
    planta: (wf) => { acao(wf, "Conferir_resultado").expression = { equals: [1, 1] }; },
    espera: "Conferir_resultado tem de testar outputs('Resultado_script')?['ok']",
  },
  {
    nome: "recusa do script sem gravar ERRO",
    planta: (wf) => {
      const s = acao(wf, "Conferir_resultado").else.actions;
      delete s.Gravar_recusa;
      s.Encerrar_recusa.runAfter = {};
    },
    espera: "Conferir_resultado: o ramo senão tem de gravar ERRO e encerrar",
  },
  {
    nome: "apagar a importação anterior pulando a trava do ok",
    planta: (wf) => { acao(wf, "Obter_importacao_anterior").runAfter = { Guardar_total: ["Succeeded"] }; },
    espera: "Obter_importacao_anterior: tem de vir logo depois de Conferir_resultado",
  },
  {
    nome: "script sem a configuração do aeroporto",
    planta: (wf) => { acao(wf, "Montar_config").inputs = "{}"; },
    espera: "Montar_config tem de levar Obter_preposicoes e Obter_posicoes",
  },
];

let falhas = 0;
function roda(defTexto, pasta) {
  const entrada = path.join(tmp, pasta + ".definition.json");
  fs.writeFileSync(entrada, defTexto);
  const r = spawnSync(process.execPath, [GERADOR, "--entrada=" + entrada, "--pacote=" + ZIP, "--saida=" + path.join(tmp, pasta)], { encoding: "utf8" });
  return { status: r.status, saida: (r.stdout || "") + (r.stderr || "") };
}

// controle
{
  const r = roda(ORIGINAL, "controle");
  const ok = r.status === 0 && /0 problemas/.test(r.saida);
  console.log(`${ok ? "✓" : "✗"} controle: a definição sem defeito gera o pacote${ok ? "" : " — " + r.saida.trim().split("\n").slice(0, 3).join(" | ")}`);
  if (!ok) falhas++;
  // idempotência: rodar o gerador sobre a própria saída produz a mesma definição
  if (ok) {
    const gerada = fs.readFileSync(path.join(tmp, "controle", "fluxo_importar_programacao.definition.json"), "utf8");
    const r2 = roda(gerada, "controle2");
    const igual = r2.status === 0 &&
      fs.readFileSync(path.join(tmp, "controle2", "fluxo_importar_programacao.definition.json"), "utf8") === gerada;
    console.log(`${igual ? "✓" : "✗"} idempotência: rodar sobre a definição já corrigida não muda nada`);
    if (!igual) falhas++;
  }
}

CASOS.forEach((c, i) => {
  const def = JSON.parse(ORIGINAL);
  try { c.planta(def.properties.definition); }
  catch (e) { console.log(`✗ ${c.nome} — ${e.message}`); falhas++; return; }
  const texto = JSON.stringify(def, null, 2);
  if (JSON.stringify(JSON.parse(texto)) === JSON.stringify(JSON.parse(ORIGINAL))) {
    console.log(`✗ ${c.nome} — a cópia ficou igual ao original; o teste não testaria nada`); falhas++; return;
  }
  const r = roda(texto, "caso" + i);
  const pelaConferencia = r.status !== 0 && r.saida.includes("definição com problema");
  if (pelaConferencia && r.saida.includes(c.espera)) {
    console.log(`✓ ${c.nome} — recusado: "${c.espera}"`);
  } else if (r.status === 0) {
    console.log(`✗ ${c.nome} — PASSOU pela conferência`); falhas++;
  } else if (!pelaConferencia) {
    console.log(`✗ ${c.nome} — o gerador QUEBROU em vez de recusar: ${r.saida.trim().split("\n").slice(0, 2).join(" | ")}`); falhas++;
  } else {
    console.log(`✗ ${c.nome} — recusado por outro motivo: ${r.saida.trim().split("\n").slice(1, 3).join(" | ")}`); falhas++;
  }
});

fs.rmSync(tmp, { recursive: true, force: true });
const intactos = hash(DEF) === hashAntes[0] && hash(ZIP) === hashAntes[1];
console.log(`${intactos ? "✓" : "✗"} definição e pacote do repositório não foram tocados pelo teste`);
if (!intactos) falhas++;

console.log(falhas ? `\n✗ ${falhas} verificação(ões) com problema` : `\n✓ controle e idempotência passam; os ${CASOS.length} defeitos plantados são recusados pela conferência`);
process.exit(falhas ? 1 : 0);
