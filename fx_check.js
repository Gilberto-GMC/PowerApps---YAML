// fx_check.js — conferência estrutural de uma tela .pa.yaml sem abrir o Studio.
// Uso: node fx_check.js <arquivo.pa.yaml> [...]
//
// Não substitui o Studio: ele valida nomes de propriedade e de função, que aqui não dá para saber.
// O que este script pega é o que já custou colagem recusada neste projeto:
//   - parênteses e aspas desbalanceados dentro de uma fórmula
//   - chave YAML duplicada entre irmãos (o erro de âncora que orfanou um Width)
//   - recuo que não fecha
//   - nome de controle repetido no arquivo
//   - "==" no começo de uma fórmula
//   - referência a nome que não existe mais (passar a lista com --mortos=a,b,c)

const fs = require("fs");

// Pares controle/propriedade que o Studio REJEITA, aprendidos a duras penas neste repositório.
// Cada linha custou uma colagem recusada. Acrescente quando descobrir outra.
//
// Esta tabela existe porque o aviso de precedente lá embaixo NÃO basta. Ele conta ocorrências
// no repositório, e o repositório tem apps diferentes, com versões diferentes do mesmo
// controle e arquivos que talvez nunca tenham sido aceitos pelo Studio. Em 09/09/2026
// 'Default' em TextInput@0.0.54 tinha 12 precedentes — todos em outros apps — e foi recusado
// aqui, onde o certo é 'Value'.
//
// Precedente é pista. Esta lista é fato.
const PROIBIDO = {
  "Button@0.0.45": ["Tooltip"], // 04/09/2026 e de novo em 05/09 — PA2108
  "DatePicker@0.0.46": ["StartYear"], // 09/09/2026 — é do DatePicker clássico, não deste
  "TextInput@0.0.54": ["Default"], // 09/09/2026 — o moderno usa Value
};

// Dicionário de propriedades observadas por tipo de controle, montado a partir de TODOS os
// .pa.yaml do repositório. Serve à regra que mais custou colagem aqui: propriedade sem
// precedente é sinal amarelo. Não dá para saber o que o Studio aceita — dá para saber o que
// ele já aceitou.
const RARIDADE = 2; // total de ocorrências no repositório abaixo do qual vira aviso

function montaDicionario(raiz) {
  const dic = new Map();
  const arquivos = [];
  (function anda(dir, prof) {
    if (prof > 4) return;
    let itens = [];
    try {
      itens = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const it of itens) {
      if (it.name === "node_modules" || it.name.startsWith(".")) continue;
      const p = require("path").join(dir, it.name);
      if (it.isDirectory()) anda(p, prof + 1);
      else if (it.name.endsWith(".pa.yaml")) arquivos.push(p);
    }
  })(raiz, 0);

  for (const a of arquivos) {
    const linhas = fs.readFileSync(a, "utf8").replace(/\r\n/g, "\n").split("\n");
    for (let i = 0; i < linhas.length; i++) {
      const t = linhas[i].match(/^(\s*)Control: (\S+)\s*$/);
      if (!t) continue;
      const rc = t[1].length;
      if (!dic.has(t[2])) dic.set(t[2], new Map());
      const props = dic.get(t[2]);
      for (let j = i + 1; j < linhas.length; j++) {
        if (!linhas[j].trim()) continue;
        const rj = linhas[j].search(/\S/);
        if (rj < rc) break;
        if (rj !== rc + 2) continue; // filhos diretos do Properties: do controle
        const p = linhas[j].match(/^\s*([A-Za-z_][A-Za-z0-9_]*):/);
        if (p) props.set(p[1], (props.get(p[1]) || 0) + 1);
      }
    }
  }
  return dic;
}

let dicionario = null;

function analisa(arquivo, mortos) {
  const linhas = fs.readFileSync(arquivo, "utf8").replace(/\r\n/g, "\n").split("\n");
  const erros = [];
  const avisos = [];
  const nomes = new Map();
  const pilha = []; // { recuo, chaves:Set }

  const recuoDe = (l) => l.search(/\S/);

  for (let i = 0; i < linhas.length; i++) {
    const l = linhas[i];
    if (!l.trim()) continue;
    const r = recuoDe(l);

    // controle: "- Nome:"
    const ctrl = l.match(/^\s*- ([A-Za-z_][A-Za-z0-9_]*):\s*$/);
    if (ctrl && /^\s*Control: /.test(linhas[i + 1] || "")) {
      if (nomes.has(ctrl[1])) {
        erros.push(`${i + 1}: controle duplicado '${ctrl[1]}' (já em ${nomes.get(ctrl[1])})`);
      }
      nomes.set(ctrl[1], i + 1);
    }

    // Chave de bloco (nada depois dos dois pontos) tem que ser seguida de linha MAIS recuada.
    // Foi isto que passou batido em 05/09/2026: 'Children:' em 28 com os filhos gerados em 26.
    if (/^\s*[A-Za-z_][A-Za-z0-9_]*:\s*$/.test(l) && !/^\s*- /.test(l)) {
      let j = i + 1;
      while (j < linhas.length && !linhas[j].trim()) j++;
      if (j < linhas.length && recuoDe(linhas[j]) <= r) {
        erros.push(`${i + 1}: bloco '${l.trim()}' não tem filho recuado (linha ${j + 1} está em ${recuoDe(linhas[j])}, precisa passar de ${r})`);
      }
    }

    // Chave solta depois de uma lista, no mesmo recuo dos itens: o Studio recusa com PA1001
    // ("did not find expected '-' indicator"). Foi o que aconteceu em 17/09/2026 com um
    // 'Visible:' que caiu depois do 'Children:' em vez de entrar em 'Properties:'.
    if (/^\s*[A-Za-z_][A-Za-z0-9_]*:/.test(l) && !/^\s*- /.test(l)) {
      let j = i - 1;
      while (j >= 0 && (!linhas[j].trim() || recuoDe(linhas[j]) > r)) j--;
      if (j >= 0 && recuoDe(linhas[j]) === r && /^\s*- \S/.test(linhas[j])) {
        erros.push(`${i + 1}: '${l.trim().split(":")[0]}' vem depois de uma lista no mesmo recuo — o Studio recusa com PA1001`);
      }
    }

    // Itens de uma mesma lista têm que compartilhar o recuo.
    if (/^\s*- \S/.test(l)) {
      let j = i + 1;
      while (j < linhas.length && (!linhas[j].trim() || recuoDe(linhas[j]) > r)) j++;
      if (j < linhas.length && recuoDe(linhas[j]) < r && /^\s*- \S/.test(linhas[j] || "")) {
        // item seguinte menos recuado é fim de lista, não erro
      }
    }

    // Propriedade não suportada pelo tipo do controle, e propriedade sem precedente.
    const tipo = l.match(/^\s*Control: (\S+)\s*$/);
    if (tipo) {
      const rc = r;
      const conhecidas = dicionario ? dicionario.get(tipo[1]) : null;
      for (let j = i + 1; j < linhas.length; j++) {
        if (!linhas[j].trim()) continue;
        const rj = recuoDe(linhas[j]);
        if (rj < rc) break;
        if (rj !== rc + 2) continue;
        const p = linhas[j].match(/^\s*([A-Za-z_][A-Za-z0-9_]*):/);
        if (!p) continue;
        if ((PROIBIDO[tipo[1]] || []).includes(p[1])) {
          erros.push(`${j + 1}: '${p[1]}' não existe em ${tipo[1]} — o Studio recusa com PA2108`);
        } else if (conhecidas && (conhecidas.get(p[1]) || 0) <= RARIDADE) {
          avisos.push(`${j + 1}: '${p[1]}' em ${tipo[1]} aparece ${conhecidas.get(p[1]) || 0}x no repositório — sem precedente firme, confira antes de colar`);
        }
      }
    }

    // Propriedade repetida dentro de UM bloco Properties:.
    // É o defeito que orfanou um Width em 04/09/2026 — âncora colada no fim de uma
    // propriedade multilinha em vez de no fim do controle.
    if (/^\s*Properties:\s*$/.test(l)) {
      const vistas = new Map();
      for (let j = i + 1; j < linhas.length; j++) {
        if (!linhas[j].trim()) continue;
        const rj = recuoDe(linhas[j]);
        if (rj <= r) break;
        if (rj !== r + 2) continue; // só filhos diretos
        const p = linhas[j].match(/^\s*([A-Za-z_][A-Za-z0-9_]*):/);
        if (!p) continue;
        if (vistas.has(p[1])) {
          erros.push(`${j + 1}: propriedade '${p[1]}' repetida no mesmo controle (já em ${vistas.get(p[1])})`);
        }
        vistas.set(p[1], j + 1);
      }
    }

    // fórmulas
    let formula = null;
    let fim = i;
    const bloco = l.match(/^(\s*)([A-Za-z_][A-Za-z0-9_]*): \|-\s*$/);
    const inline = l.match(/^\s*([A-Za-z_][A-Za-z0-9_]*): (=.*)$/);
    if (bloco) {
      const corpo = [];
      let j = i + 1;
      while (j < linhas.length && (!linhas[j].trim() || recuoDe(linhas[j]) > r)) {
        corpo.push(linhas[j]);
        j++;
      }
      formula = corpo.join("\n");
      fim = j - 1;
    } else if (inline) {
      formula = inline[2];
      // Valor inline é escalar YAML simples: ": " (ou " #") dentro dele vira chave/comentário e o Studio
      // recusa com PA1001 "found invalid mapping". Aconteceu em 16/09/2026 num AccessibleLabel com
      // "alterações: quem fez". Dentro de bloco |- pode — é por isso que só o inline é conferido.
      if (/: | #/.test(inline[2])) {
        erros.push(`${i + 1}: '${inline[1]}' inline contém ': ' ou ' #' — o YAML quebra (PA1001); troque o caractere ou use bloco |-`);
      }
    }

    if (formula !== null) {
      const nome = (bloco || inline)[bloco ? 2 : 1];
      if (/^\s*==/.test(formula)) erros.push(`${i + 1}: '${nome}' começa com '==' `);
      // aspas: conta pares por linha lógica
      const aspas = (formula.match(/"/g) || []).length;
      if (aspas % 2 !== 0) erros.push(`${i + 1}: '${nome}' tem número ímpar de aspas (${aspas})`);
      // parênteses fora de string
      const semStr = formula.replace(/"(?:[^"\\]|\\.)*"/g, '""').replace(/'[^']*'/g, "''");
      let p = 0, quebrou = false;
      for (const c of semStr) {
        if (c === "(") p++;
        else if (c === ")") p--;
        if (p < 0) { quebrou = true; break; }
      }
      if (quebrou) erros.push(`${i + 1}: '${nome}' fecha parêntese a mais`);
      else if (p !== 0) erros.push(`${i + 1}: '${nome}' tem ${p} parêntese(s) sem fechar`);
      // chaves de registro
      let b = 0;
      for (const c of semStr) { if (c === "{") b++; else if (c === "}") b--; }
      if (b !== 0) erros.push(`${i + 1}: '${nome}' tem ${b} chave(s) {} sem fechar`);

      // Divisão por variável nua. Variável global nasce em branco, e o Studio avalia as
      // fórmulas da tela antes de qualquer OnVisible rodar — dá "divisão por zero" na colagem.
      // Envolva o divisor em Max(x, <mínimo>) ou Coalesce(x, <padrão>).
      // Aviso, e não erro: um If() por fora testando o divisor já protege, porque o If do
      // Power Fx é preguiçoso e o ramo da divisão nem chega a ser avaliado. O regex daqui
      // não enxerga essa guarda, então isto aponta candidatos — não veredictos.
      // Só o divisor conta: '/ Max(...)' e '/ Coalesce(...)' estão protegidos na posição certa.
      // Tentei deduzir a guarda de um If() em volta e o heurístico anulou o check — passava a
      // suprimir sempre que a variável aparecesse em qualquer Max/If da mesma fórmula.
      for (const d of new Set(semStr.match(/\/\s*(?:var|loc)[A-Za-z0-9_.]+/g) || [])) {
        const alvo = d.replace(/^\/\s*/, "");
        avisos.push(`${i + 1}: '${nome}' divide por ${alvo} — em branco vira divisão por zero. Proteja com Max()/Coalesce() no divisor, ou confirme que um If() por fora já barra o caso`);
      }

      for (const m of mortos) {
        if (new RegExp(`\\b${m}\\b`).test(formula)) erros.push(`${i + 1}: '${nome}' cita '${m}', que não existe mais`);
      }
      i = fim;
    }
  }
  return { erros, avisos, controles: nomes.size, linhas: linhas.length };
}

const args = process.argv.slice(2);
const mortos = (args.find((a) => a.startsWith("--mortos=")) || "").replace("--mortos=", "").split(",").filter(Boolean);
const arquivos = args.filter((a) => !a.startsWith("--"));
dicionario = montaDicionario(require("path").dirname(process.argv[1]));
let falhou = false;

for (const a of arquivos) {
  const r = analisa(a, mortos);
  if (r.erros.length) {
    falhou = true;
    console.log(`\n✗ ${a} — ${r.erros.length} problema(s)`);
    r.erros.forEach((e) => console.log("   " + e));
  } else {
    console.log(`✓ ${a} — ${r.controles} controles, ${r.linhas} linhas`);
  }
  if (r.avisos.length) {
    console.log(`  ⚠ ${r.avisos.length} aviso(s) — confira, podem já estar protegidos por um If() em volta`);
    r.avisos.forEach((e) => console.log("     " + e));
  }
}
process.exit(falhou ? 1 : 0);
