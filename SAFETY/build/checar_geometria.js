// Checa o padrao confirmado em 2026-10-09 (ver LICOES_APRENDIDAS_POWERAPPS_YAML.md):
//   1) GroupContainer ManualLayout filho de AutoLayout sem Width e/ou Height declaradas
//      -> RISCO, nao falha certa: no app o motor estica o filho e o valor nunca precisa
//         existir. Correlaciona com conteudo colapsado na colagem do YAML, mas as telas
//         *Forms tem o mesmo padrao e colam certo. Conferir em tela antes de concluir.
//   2) propriedade de geometria declarada vazia (ex. "Height: =")
//   3) informativo: AutoLayout com filhos que declaram X/Y (ali a geometria e ignorada)
// Uso: node build/checar_geometria.js <arquivo.pa.yaml> [...]
const fs = require('fs');
const path = require('path');

function parse(arq) {
  const L = fs.readFileSync(arq, 'utf8').split(/\r?\n/);
  const nos = [];
  for (let i = 0; i < L.length; i++) {
    const m = L[i].match(/^(\s*)- ([A-Za-z_][\w]*):\s*$/);
    if (!m) continue;
    const ind = m[1].length;
    let ctrl = '', variant = '';
    const props = {};
    for (let j = i + 1; j < L.length; j++) {
      const li = L[j];
      if (!li.trim()) continue;
      const cur = li.search(/\S/);
      if (cur <= ind) break;
      if (cur === ind + 4) {
        let mm = li.match(/^\s*Control:\s*(.+)$/);  if (mm) ctrl = mm[1].trim();
        mm = li.match(/^\s*Variant:\s*(.+)$/);      if (mm) variant = mm[1].trim();
      }
      if (cur === ind + 6) {
        const mm = li.match(/^\s*(X|Y|Width|Height):\s*(.*)$/);
        if (mm) props[mm[1]] = mm[2];
      }
    }
    nos.push({ ind, nome: m[2], ctrl, variant, props, linha: i + 1 });
  }
  for (let k = 0; k < nos.length; k++)
    for (let j = k - 1; j >= 0; j--)
      if (nos[j].ind < nos[k].ind) { nos[k].pai = nos[j]; break; }
  return nos;
}

let falhas = 0;
for (const arq of process.argv.slice(2)) {
  const nos = parse(arq);
  const msgs = [];
  for (const n of nos) {
    for (const p of ['X', 'Y', 'Width', 'Height'])
      if (p in n.props && n.props[p].trim() === '=')
        msgs.push('FALHA  ' + n.nome + ' L' + n.linha + ': ' + p + ' declarada vazia');

    if (n.variant === 'ManualLayout' && n.pai && n.pai.variant === 'AutoLayout') {
      const falta = ['Width', 'Height'].filter(p => !(p in n.props) || !n.props[p].trim() || n.props[p].trim() === '=');
      if (falta.length)
        msgs.push('risco  ' + n.nome + ' L' + n.linha + ': ManualLayout dentro de AutoLayout (' +
                  n.pai.nome + ') sem ' + falta.join(' e ') + ' declarada');
    }

    if (n.variant === 'AutoLayout') {
      const filhos = nos.filter(x => x.pai === n && ('X' in x.props || 'Y' in x.props));
      if (filhos.length)
        msgs.push('aviso  ' + n.nome + ' L' + n.linha + ': AutoLayout com ' + filhos.length +
                  ' filho(s) declarando X/Y (ignorados pelo motor de layout)');
    }
  }
  const erros = msgs.filter(m => m.startsWith('FALHA')).length;
  falhas += erros;
  console.log('\n' + path.basename(arq) + (msgs.length ? '' : '  ok'));
  for (const m of msgs) console.log('  ' + m);
}
console.log('\n' + (falhas ? falhas + ' falha(s)' : 'nenhuma falha'));
process.exit(falhas ? 1 : 0);
