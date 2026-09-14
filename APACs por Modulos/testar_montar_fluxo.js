// testar_montar_fluxo.js — prova que as conferências do montar_fluxo_importacao.js RECUSAM defeito.
//
// Uso:  node testar_montar_fluxo.js
//
// Para cada defeito: planta a mudança numa cópia do gerador, roda a cópia e exige três coisas —
//   1. a mudança aconteceu (a cópia difere do original; senão o teste não testou nada);
//   2. a cópia saiu com erro;
//   3. o erro veio da CONFERÊNCIA ("definição com problema") e cita o que foi plantado —
//      erro de sintaxe ou exceção não conta: isso é o gerador quebrando, não recusando.
//
// ⚠️ Existe porque, em 14/09/2026, a primeira versão deste teste foi feita em linha de shell e
// estava errada: lia os argumentos do `node -e` a partir de process.argv[2] (é [1]), trocava o texto
// errado e contava erro de sintaxe como "recusou". Quatro defeitos passaram e dois "recusados" eram
// falsos. Teste de verificação também precisa ser verificado.
//
// A cópia roda com SAÍDA desviada para uma pasta temporária: um defeito que passasse não pode
// sobrescrever o pacote verdadeiro em fluxo/.

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const AQUI = __dirname;
const ORIGINAL = fs.readFileSync(path.join(AQUI, "montar_fluxo_importacao.js"), "utf8");
const SAIDA_REAL = 'path.join(__dirname, "fluxo")';
if (!ORIGINAL.includes(SAIDA_REAL)) { console.error("não achei a linha da pasta de saída no gerador"); process.exit(2); }

const DEFEITOS = [
  {
    nome: "obrigatória faltando no PostItem (ativo do voo)",
    de: `"item/ativo": "@items('Gravar_lote')?['ativo']",`,
    para: ``,
    espera: "falta a obrigatória ativo",
  },
  {
    nome: "obrigatória faltando no PatchItem (total_gravados da tb_apacImportacao)",
    de: `"item/total_gravados": T("total_gravados"),`,
    para: ``,
    espera: "falta a obrigatória total_gravados",
  },
  {
    nome: "referência a ação que não existe",
    de: `foreach: "@outputs('Obter_malha_anterior')?['body/value']",`,
    para: `foreach: "@outputs('Obter_malha_velha')?['body/value']",`,
    espera: "ação inexistente: Obter_malha_velha",
  },
  {
    nome: "coluna que não existe na lista",
    de: `"item/rota": "@items('Gravar_lote')?['rota']",`,
    para: `"item/rotaX": "@items('Gravar_lote')?['rota']",`,
    espera: "coluna 'rotaX' não existe",
  },
  {
    nome: "runAfter para ação de outro nível",
    de: `runAfter: { Apagar_anteriores: ["Succeeded"] },`,
    para: `runAfter: { Salvar_planilha: ["Succeeded"] },`,
    espera: "'Salvar_planilha', que não está no mesmo nível",
  },
  {
    nome: "variável não inicializada",
    de: `"item/total_gravados": "@variables('gravados')",\n  "item/mensagem": "A importacao falhou`,
    para: `"item/total_gravados": "@variables('gravadoss')",\n  "item/mensagem": "A importacao falhou`,
    espera: "variável não inicializada: gravadoss",
  },
  {
    nome: "items() usado fora do próprio laço",
    de: `"item/total_lidos": RN("total"),\n  "item/total_gravados": "@variables('gravados')",\n  "item/total_descartados": RN("descartados"),\n  "item/mensagem": "@{outputs('Resultado_script')?['mensagem']} Gravados`,
    para: `"item/total_lidos": "@items('Gravar_lotes')?['x']",\n  "item/total_gravados": "@variables('gravados')",\n  "item/total_descartados": RN("descartados"),\n  "item/mensagem": "@{outputs('Resultado_script')?['mensagem']} Gravados`,
    espera: "usa items('Gravar_lotes') fora desse laço",
  },
  {
    nome: "InitializeVariable fora do nível de cima",
    de: `gravar.Obter_malha_anterior = sp("GetItems", {`,
    para: `gravar.Var_escondida = { runAfter: {}, type: "InitializeVariable", inputs: { variables: [{ name: "gravados", type: "integer", value: 0 }] } };\ngravar.Obter_malha_anterior = sp("GetItems", {`,
    espera: "InitializeVariable fora do nível de cima",
  },
];

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "neg-fluxo-"));
let falhas = 0;

// controle: a cópia SEM defeito tem de passar — senão o harness em si está quebrado
{
  const copia = ORIGINAL.replace(SAIDA_REAL, JSON.stringify(path.join(tmp, "controle")));
  const arq = path.join(AQUI, "_controle_montar_fluxo.js");
  fs.writeFileSync(arq, copia);
  const r = spawnSync(process.execPath, [arq], { encoding: "utf8" });
  fs.unlinkSync(arq);
  const ok = r.status === 0 && /0 problemas/.test(r.stdout);
  console.log(`${ok ? "✓" : "✗"} controle: a cópia sem defeito gera o pacote${ok ? "" : " — " + (r.stderr || r.stdout).trim().split("\n")[0]}`);
  if (!ok) falhas++;
}

for (const d of DEFEITOS) {
  const n = ORIGINAL.split(d.de).length - 1;
  if (n !== 1) { console.log(`✗ ${d.nome} — o trecho a plantar aparece ${n} vez(es) no gerador; o teste não testaria nada`); falhas++; continue; }
  let copia = ORIGINAL.replace(d.de, () => d.para).replace(SAIDA_REAL, JSON.stringify(path.join(tmp, "saida")));
  if (copia === ORIGINAL) { console.log(`✗ ${d.nome} — a cópia ficou igual ao original`); falhas++; continue; }

  const arq = path.join(AQUI, "_negativo_montar_fluxo.js");   // na mesma pasta: o gerador lê os JSON das listas por __dirname
  fs.writeFileSync(arq, copia);
  const r = spawnSync(process.execPath, [arq], { encoding: "utf8" });
  fs.unlinkSync(arq);

  const saida = (r.stdout || "") + (r.stderr || "");
  const recusouPelaConferencia = r.status !== 0 && saida.includes("definição com problema");
  const citou = saida.includes(d.espera);
  if (recusouPelaConferencia && citou) {
    console.log(`✓ ${d.nome} — recusado: "${d.espera}"`);
  } else if (r.status === 0) {
    console.log(`✗ ${d.nome} — PASSOU pela conferência`); falhas++;
  } else if (!recusouPelaConferencia) {
    console.log(`✗ ${d.nome} — o gerador QUEBROU em vez de recusar: ${saida.trim().split("\n").slice(0, 2).join(" | ")}`); falhas++;
  } else {
    console.log(`✗ ${d.nome} — recusado, mas por outro motivo: ${saida.trim().split("\n").slice(1, 3).join(" | ")}`); falhas++;
  }
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log(falhas ? `\n✗ ${falhas} caso(s) com problema` : `\n✓ controle passa e os ${DEFEITOS.length} defeitos plantados são recusados pela conferência`);
process.exit(falhas ? 1 : 0);
