// Validador das telas do Novo Hub AirportNow.
// Checklist global (LICOES_APRENDIDAS_POWERAPPS_YAML.md) + o que e especifico
// da troca de identidade visual ASUR.
//
// Uso: node validate_hub.js [arquivo.pa.yaml ...]   (sem argumento: todos os .pa.yaml daqui)

const fs = require('fs');
const path = require('path');

// Fonte unica dos tokens: o App.Formulas inteiro, do jeito que vai ser colado.
const TOKENS_FX = path.join(__dirname, 'App_Formulas_Hub.txt');

// Tokens definidos no bloco do App.Formulas (dialeto pt-BR: "nome =" no inicio da linha).
function tokensDefinidos() {
  const fx = fs.readFileSync(TOKENS_FX, 'utf8');
  const nomes = new Set();
  for (const m of fx.matchAll(/^\s*((?:hx|thm)[A-Za-z]+)\s*=/gm)) nomes.add(m[1]);
  return nomes;
}

// Nomes que vem do App.Formulas/OnStart do app e nao deste bloco.
const EXTERNOS = new Set([
  'varHUB', 'var_versao', 'var_ultimaVersao', 'colAeros',
  'usrHub', 'usrEhRoot', 'usrVeSafety', 'col_menu', 'col_menuModulos',
]);

// O App.Formulas e colado na barra de formulas do Studio, em pt-BR: separador
// decimal e VIRGULA. "RGBA(166; 166; 166; 0.5)" nao e reconhecido e derruba a
// declaracao inteira, e so aparece como "o nome nao e valido" no controle que usa.
function validarFormulas() {
  const erros = [];
  const linhas = fs.readFileSync(TOKENS_FX, 'utf8').split(/\r?\n/);
  linhas.forEach((l, i) => {
    if (/^\s*\/\//.test(l)) return;
    const semTexto = l.replace(/'[^']*'/g, "''").replace(/"[^"]*"/g, '""');
    if (/\b\d+\.\d+\b/.test(semTexto)) {
      erros.push(`App_Formulas_Hub.txt:${i + 1} decimal com ponto em dialeto pt-BR — usar virgula: ${l.trim()}`);
    }
  });
  return erros;
}

function validar(arquivo) {
  const txt = fs.readFileSync(arquivo, 'utf8');
  const linhas = txt.split(/\r?\n/);
  const erros = [];
  const avisos = [];
  const e = (i, msg) => erros.push(`${path.basename(arquivo)}:${i + 1} ${msg}`);

  // 1. Estrutura raiz exata.
  if (!/^Screens:\r?\n {2}\S.*:\r?\n {4}Properties:/.test(txt)) {
    erros.push(`${path.basename(arquivo)}:1 raiz invalida — exige "Screens:\\n  Tela:\\n    Properties:"`);
  }
  if (txt.charCodeAt(0) === 0xfeff) erros.push(`${path.basename(arquivo)}:1 BOM no inicio do arquivo`);

  // 2. Propriedades recusadas pelo Studio.
  linhas.forEach((l, i) => {
    if (/^\s*Overflow:/.test(l)) e(i, 'propriedade "Overflow" nao existe em GroupContainer@1.5.0');
    if (/%DATACARD_/.test(l)) e(i, 'placeholder %DATACARD_ residual');
  });

  // 3. Default dentro de TextInput@0.0.54 (moderno) — usa Value.
  // 4. Color dentro de Text@0.0.51 — a propriedade e FontColor.
  let ctrlAtual = null;
  let ctrlIndent = 0;
  linhas.forEach((l, i) => {
    const mc = l.match(/^(\s*)Control:\s*(\S+)/);
    if (mc) { ctrlAtual = mc[2]; ctrlIndent = mc[1].length; return; }
    if (ctrlAtual && l.trim() && (l.match(/^\s*/)[0].length < ctrlIndent)) ctrlAtual = null;
    if (!ctrlAtual) return;
    if (ctrlAtual === 'TextInput@0.0.54' && /^\s*Default:/.test(l)) e(i, 'TextInput@0.0.54 usa Value, nao Default');
    if (ctrlAtual === 'Text@0.0.51' && /^\s*Color:/.test(l)) e(i, 'Text@0.0.51 usa FontColor, nao Color');
  });

  // 5. Todo thm*/hx* usado na tela tem que existir no bloco de tokens.
  const definidos = tokensDefinidos();
  const usados = new Map();
  linhas.forEach((l, i) => {
    for (const m of l.matchAll(/\b((?:hx|thm)[A-Za-z]+)\b/g)) {
      if (!usados.has(m[1])) usados.set(m[1], i);
    }
  });
  for (const [nome, i] of usados) {
    if (!definidos.has(nome)) e(i, `token "${nome}" usado na tela e nao definido no App.Formulas`);
  }

  // 6. Nenhum literal de cor sobrando (branco, preto e transparencia sao estrutura).
  const PRESERVADOS = new Set([
    'RGBA(255, 255, 255, 0.8)', 'RGBA(0, 0, 0, 0)',
  ]);
  linhas.forEach((l, i) => {
    for (const m of l.matchAll(/RGBA\(\s*\d+,\s*\d+,\s*\d+,\s*[\d.]+\s*\)/g)) {
      if (!PRESERVADOS.has(m[0])) e(i, `literal de cor fora do token: ${m[0]}`);
    }
    if (/\bColor\.(Red|Blue|Green|Black|Orange)\b/.test(l)) e(i, 'cor nomeada literal — usar token');
    if (/['"]#[0-9A-Fa-f]{6}/.test(l)) e(i, 'hex literal — usar hx*');
  });

  // 7. Button@0.0.45 sem BasePaletteColor cai no tema do Studio e nao muda de cor.
  const blocos = txt.split(/(?=^\s*- \w+:$)/m);
  for (const b of blocos) {
    if (!/Control:\s*Button@0\.0\.45/.test(b)) continue;
    const nome = (b.match(/- (\w+):/) || [, '?'])[1];
    const transparente = /Appearance:\s*='ButtonCanvas\.Appearance'\.Transparent/.test(b);
    if (transparente) {
      if (!/FontColor:/.test(b)) erros.push(`${path.basename(arquivo)} ${nome}: Button transparente sem FontColor`);
    } else if (!/BasePaletteColor:/.test(b)) {
      erros.push(`${path.basename(arquivo)} ${nome}: Button@0.0.45 sem BasePaletteColor — a cor vem do tema`);
    }
  }

  // 8. Toda referencia a controle existe na tela.
  const declarados = new Set();
  for (const m of txt.matchAll(/^\s*- (\w+):$/gm)) declarados.add(m[1]);
  linhas.forEach((l, i) => {
    for (const m of l.matchAll(/\bSelect\((\w+)\)/g)) {
      if (!declarados.has(m[1])) e(i, `Select(${m[1]}) — controle inexistente nesta tela`);
    }
  });

  // 9. Nome de controle duplicado.
  const vistos = new Map();
  for (const m of txt.matchAll(/^\s*- (\w+):$/gm)) {
    const n = m[1];
    if (vistos.has(n)) erros.push(`${path.basename(arquivo)} nome duplicado: ${n}`);
    vistos.set(n, true);
  }

  // 10. Delegacao: Sort/Filter/LookUp direto sobre lista SharePoint.
  linhas.forEach((l, i) => {
    if (/Sort\(\s*$/.test(l) && /Sort\(/.test(l)) { /* multilinha, tratado abaixo */ }
  });
  const semQuebra = txt.replace(/\s+/g, ' ');
  if (/LookUp\( Sort\(/.test(semQuebra)) {
    erros.push(`${path.basename(arquivo)} LookUp sobre Sort da lista inteira — nao delegavel`);
  }
  if (/FirstN\( Sort\(/.test(semQuebra)) {
    avisos.push(`${path.basename(arquivo)} FirstN sobre Sort — conferir delegacao`);
  }

  return { erros, avisos, tokens: usados.size };
}

// --- autoteste: cada regra precisa reprovar pelo menos um caso construido ---
function autoteste() {
  const casos = [
    ['raiz', 'Screens:\n Login:\n  Properties:\n', /raiz invalida/],
    ['overflow', 'Screens:\n  L:\n    Properties:\n      Overflow: =1\n', /Overflow/],
    ['token', 'Screens:\n  L:\n    Properties:\n      Fill: =thmInventado\n', /nao definido/],
    ['literal', 'Screens:\n  L:\n    Properties:\n      Fill: =RGBA(1, 2, 3, 1)\n', /literal de cor/],
    ['select', 'Screens:\n  L:\n    Properties:\n      OnVisible: =Select(btnFantasma)\n', /controle inexistente/],
  ];
  const tmp = path.join(__dirname, '.autoteste.pa.yaml');
  let ok = true;
  for (const [nome, conteudo, padrao] of casos) {
    fs.writeFileSync(tmp, conteudo, 'utf8');
    const { erros } = validar(tmp);
    if (!erros.some((x) => padrao.test(x))) {
      console.error(`AUTOTESTE FALHOU: a regra "${nome}" nao reprovou o caso construido`);
      ok = false;
    }
  }
  fs.unlinkSync(tmp);
  return ok;
}

const alvos = process.argv.slice(2).length
  ? process.argv.slice(2)
  : fs.readdirSync(__dirname).filter((f) => f.endsWith('.pa.yaml')).map((f) => path.join(__dirname, f));

if (!autoteste()) process.exit(2);
console.log('autoteste: 5 regras reprovaram os casos construidos\n');

let falhou = false;
const errosFx = validarFormulas();
console.log('App_Formulas_Hub.txt');
errosFx.forEach((x) => console.log(`  ERRO:  ${x}`));
if (!errosFx.length) console.log('  ok');
else falhou = true;

for (const alvo of alvos) {
  const { erros, avisos, tokens } = validar(alvo);
  console.log(`${path.basename(alvo)} — ${tokens} tokens distintos em uso`);
  avisos.forEach((a) => console.log(`  aviso: ${a}`));
  erros.forEach((x) => console.log(`  ERRO:  ${x}`));
  if (!erros.length) console.log('  ok');
  if (erros.length) falhou = true;
}
process.exit(falhou ? 1 : 0);
