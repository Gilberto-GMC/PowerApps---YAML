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
  // 09/09/2026 'Default' — o moderno usa Value.
  // 10/09/2026 'HintText' e 'Label' — PA2108 no projeto APACs por Módulos, 14 erros de uma vez.
  // Os nomes certos são 'Placeholder' e, para o rótulo, um controle separado; 'AccessibleLabel'
  // existe neste controle (7 usos na scrMapaPatio validada) mas é acessibilidade, não rótulo visível.
  // ⚠️ As três TINHAM precedente no repositório e passaram pelo aviso de raridade. É a terceira
  // vez que este controle engana pelo precedente: ele aparece em apps antigos com outra versão.
  "TextInput@0.0.54": ["Default", "HintText", "Label"],
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

      // ';' como separador de ARGUMENTO. O .pa.yaml é sempre en-US: vírgula separa argumento,
      // ';' só encadeia instruções no nível de cima. O que se digita no Studio segue o locale
      // (pt-BR usa ';' e ';;'), e é daí que vem a confusão — o App.Formulas é pt-BR, a tela não.
      // 10/09/2026: as duas telas do projeto APAC nasceram com 395 separadores errados.
      // Conta profundidade de parênteses e ignora o que está dentro de string, senão todo
      // ponto-e-vírgula de CSS dentro de HtmlViewer viraria falso positivo.
      // ⚠️ A PRIMEIRA versão desta trava marcava todo ';' em profundidade > 0 e acusava 41 vezes
      // a scrMapaPatio, que está validada no app. O motivo: dentro de If(), Switch() e afins,
      // ';' encadeia INSTRUÇÕES e é legítimo —
      //     If(cond, Set(varX, 1); Select(btn))
      // O que decide não é a profundidade, é QUAL função envolve o ';'. Numa função que só
      // recebe valores, ';' só pode ser separador de argumento, e aí é erro.
      {
        const SO_VALOR = new Set(["Set", "Max", "Min", "Coalesce", "Sum", "Filter", "Text", "Value",
          "Date", "DateAdd", "DateValue", "Sort", "LookUp", "Round", "Mod", "Int", "Sequence",
          "CountRows", "ForAll", "With", "Concat", "Left", "Right", "Mid", "Upper", "Lower",
          "Patch", "ClearCollect", "Collect", "Notify", "Navigate", "Day", "Month", "Year", "Hour"]);
        const pilha = [];
        let str = false, achou = null;
        for (let k = 0; k < formula.length && !achou; k++) {
          const c = formula[k];
          if (str) { if (c === '"') { if (formula[k + 1] === '"') k++; else str = false; } continue; }
          if (c === '"') { str = true; continue; }
          if (c === "(") {
            const antes = formula.slice(0, k).match(/([A-Za-z][A-Za-z0-9_]*)\s*$/);
            pilha.push(antes ? antes[1] : "");
          } else if (c === "{" || c === "[") pilha.push("{}");
          else if (c === ")" || c === "}" || c === "]") pilha.pop();
          else if (c === ";" && pilha.length) {
            const dono = pilha[pilha.length - 1];
            if (SO_VALOR.has(dono)) achou = dono;
          }
        }
        if (achou) {
          erros.push(`${i + 1}: '${nome}' usa ';' dentro de ${achou}() — no .pa.yaml o separador de argumento é ','`);
        }
      }
      i = fim;
    }
  }

  // Linha órfã dentro de um bloco Properties: sobra de propriedade removida sem o corpo dela.
  // Não é erro de Power Fx, é YAML inválido — e o fx_check passava por cima porque a linha
  // não casa com o padrão de propriedade e por isso simplesmente não era olhada.
  // 10/09/2026: 26 linhas assim ficaram nas telas do APAC ao tirar OnChange de 13 campos.
  for (let i = 0; i < linhas.length; i++) {
    const m = linhas[i].match(/^(\s*)Properties:\s*$/);
    if (!m) continue;
    const P = m[1].length;
    for (let k = i + 1; k < linhas.length; k++) {
      if (!linhas[k].trim()) continue;
      const q = linhas[k].match(/^(\s*)\S/);
      if (!q) continue;
      if (q[1].length <= P) break;
      if (q[1].length !== P + 2) continue; // mais fundo = corpo de bloco escalar, legítimo
      if (!/^\s*[A-Za-z][\w.]*:/.test(linhas[k])) {
        erros.push(`${k + 1}: linha solta dentro de Properties — '${linhas[k].trim().slice(0, 40)}'`);
      }
    }
  }

  // Valor de UMA linha (Chave: =...) é escalar YAML sem aspas: ": " dentro dele vira outra chave
  // e " #" vira comentário. As aspas do Power Fx não protegem — o YAML não sabe o que é Power Fx.
  // 14/09/2026: "(rótulo, ex.: VIII)" derrubou a colagem da scrApacCadastro com PA1001.
  for (let i = 0; i < linhas.length; i++) {
    const m = linhas[i].match(/^s*[A-Za-z][w.]*: (=.*)$/);
    if (!m) continue;
    const v = m[1];
    const c = v.indexOf(": ");
    if (c >= 0) erros.push(`${i + 1}: ": " no valor de uma linha (coluna ${linhas[i].indexOf(v) + c + 1}) — o YAML lê como chave; use bloco |- ou reescreva`);
    const h = v.indexOf(" #");
    if (h >= 0) erros.push(`${i + 1}: " #" no valor de uma linha — o YAML corta ali como comentário; use bloco |-`);
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
