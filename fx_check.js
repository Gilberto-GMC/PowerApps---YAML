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

function analisa(arquivo, mortos) {
  const linhas = fs.readFileSync(arquivo, "utf8").replace(/\r\n/g, "\n").split("\n");
  const erros = [];
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

      for (const m of mortos) {
        if (new RegExp(`\\b${m}\\b`).test(formula)) erros.push(`${i + 1}: '${nome}' cita '${m}', que não existe mais`);
      }
      i = fim;
    }
  }
  return { erros, controles: nomes.size, linhas: linhas.length };
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
}
process.exit(falhou ? 1 : 0);
