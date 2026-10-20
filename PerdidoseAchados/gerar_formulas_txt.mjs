// Extrai o bloco colavel do AppFormulas_PerdidosAchados.fx.md para um .txt.
// O .fx.md tem a narrativa (por que cada coisa esta ali, o que testar antes de
// publicar); o .txt e o que vai para o Studio. Rodar depois de toda mudanca no
// bloco, senao os dois divergem.
import fs from 'fs';
const MD = 'AppFormulas_PerdidosAchados.fx.md';
const TXT = 'App_Formulas_PerdidosAchados.txt';

const a = fs.readFileSync(MD, 'utf8').replace(/\r\n/g, '\n').split('\n');
const i = a.findIndex(l => l.trim() === '## App.Formulas');
if (i < 0) throw new Error('secao "## App.Formulas" nao encontrada');
let ini = i; while (a[ini].trim() !== '```') ini++;
let fim = ini + 1; while (a[fim].trim() !== '```') fim++;

const corpo = a.slice(ini + 1, fim).join('\n').replace(/\n+$/, '') + '\n';

// conferencias que ja custaram caro
const par = (x, y) => (corpo.split(x).length - 1) === (corpo.split(y).length - 1);
const erros = [];
if (!par('(', ')')) erros.push('parenteses desbalanceados');
if (!par('{', '}')) erros.push('chaves desbalanceadas');
if ((corpo.split('"').length - 1) % 2) erros.push('aspas duplas impares');
const nomes = corpo.split('\n').filter(l => /^[a-zA-Z_][A-Za-z0-9_]* *=/.test(l)).map(l => l.split('=')[0].trim());
const dup = [...new Set(nomes.filter((n, k) => nomes.indexOf(n) !== k))];
if (dup.length) erros.push('definicoes duplicadas: ' + dup.join(', '));
if (erros.length) { console.error('NAO GRAVEI:\n  ' + erros.join('\n  ')); process.exit(1); }

fs.writeFileSync(TXT, corpo, 'utf8');
console.log(TXT + ': ' + corpo.split('\n').length + ' linhas, ' + nomes.length + ' definicoes, sem duplicata');
