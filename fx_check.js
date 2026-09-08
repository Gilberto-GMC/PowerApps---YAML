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
const PROIBIDO = {
  "Button@0.0.45": ["Tooltip"], // 04/09/2026 e de novo em 05/09 — PA2108
};

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

    // Propriedade não suportada pelo tipo do controle.
    const tipo = l.match(/^\s*Control: (\S+)\s*$/);
    if (tipo && PROIBIDO[tipo[1]]) {
      const rc = r;
      for (let j = i + 1; j < linhas.length; j++) {
        if (!linhas[j].trim()) continue;
        if (recuoDe(linhas[j]) < rc) break;
        const p = linhas[j].match(/^\s*([A-Za-z_][A-Za-z0-9_]*):/);
        if (p && PROIBIDO[tipo[1]].includes(p[1])) {
          erros.push(`${j + 1}: '${p[1]}' não existe em ${tipo[1]} — o Studio recusa com PA2108`);
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
      i = fim;
    }
  }
  return { erros, avisos, controles: nomes.size, linhas: linhas.length };
}

const args = process.argv.slice(2);
const mortos = (args.find((a) => a.startsWith("--mortos=")) || "").replace("--mortos=", "").split(",").filter(Boolean);
const arquivos = args.filter((a) => !a.startsWith("--"));
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
