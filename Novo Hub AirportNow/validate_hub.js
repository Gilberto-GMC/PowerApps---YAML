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
// Token html* entra dentro de style='...' nas telas. Aspa simples no valor fecha o
// atributo no meio e o resto do estilo e descartado, sem erro nenhum.
function htmlTokenComAspaSimples(linha) {
  const m = linha.match(/^\s*(html\w+)\s*=\s*"([^"]*)"/);
  return !!(m && m[2].includes("'"));
}

function validarFormulas() {
  const erros = [];
  const linhas = fs.readFileSync(TOKENS_FX, 'utf8').split(/\r?\n/);
  linhas.forEach((l, i) => {
    if (/^\s*\/\//.test(l)) return;
    if (htmlTokenComAspaSimples(l)) {
      erros.push(`App_Formulas_Hub.txt:${i + 1} token html* com aspa simples — fecha o style='...' no meio: ${l.trim()}`);
    }
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

  // 1. Estrutura raiz exata — tela ou componente.
  const ehComponente = /^ComponentDefinitions:/.test(txt);
  if (ehComponente) {
    if (!/^ComponentDefinitions:\r?\n {2}\S.*:\r?\n {4}DefinitionType: CanvasComponent/.test(txt)) {
      erros.push(`${path.basename(arquivo)}:1 raiz de componente invalida — exige "ComponentDefinitions:\\n  Nome:\\n    DefinitionType: CanvasComponent"`);
    }
    // Sem AccessAppScope o componente nao enxerga o App.Formulas: todo thm*/hx*
    // dentro dele fica "nome nao reconhecido".
    if (/\b(?:thm|hx)[A-Za-z]+\b/.test(txt) && !/^\s*AccessAppScope: true\s*$/m.test(txt)) {
      erros.push(`${path.basename(arquivo)} usa token do App.Formulas sem "AccessAppScope: true"`);
    }
    // PA2231: propriedade de entrada com Default vazio e recusada na colagem,
    // mesmo que o componente ja rode assim no app. Texto -> ="", Screen -> =Blank().
    // Nao vale para Default: = de CONTROLE, so dentro de CustomProperties.
    {
      const ini = linhas.findIndex((l) => /^\s*CustomProperties:\s*$/.test(l));
      if (ini >= 0) {
        const indentCP = linhas[ini].match(/^\s*/)[0].length;
        let kind = null;
        let nome = null;
        for (let i = ini + 1; i < linhas.length; i++) {
          const l = linhas[i];
          if (l.trim() && l.match(/^\s*/)[0].length <= indentCP) break;
          const mNome = l.match(/^\s{2,}(\w+):\s*$/);
          if (mNome && l.match(/^\s*/)[0].length === indentCP + 2) { nome = mNome[1]; kind = null; continue; }
          const mKind = l.match(/^\s*PropertyKind:\s*(\w+)/);
          if (mKind) { kind = mKind[1]; continue; }
          if (/^\s*Default:\s*=\s*$/.test(l) && kind === 'Input') {
            e(i, `PA2231: propriedade de entrada "${nome}" com Default vazio`);
          }
        }
      }
    }
  } else if (!/^Screens:\r?\n {2}\S.*:\r?\n {4}Properties:/.test(txt)) {
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
  // Branco e preto com alfa < 1 sao transparencia estrutural (veu, hover, sombra),
  // nao cor de marca. Tudo o mais tem que ser token.
  const estrutural = (lit) => {
    const m = lit.match(/RGBA\(\s*(\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\s*\)/);
    if (!m) return false;
    const [r, g, b, a] = m.slice(1).map(Number);
    const brancoOuPreto = (r === 255 && g === 255 && b === 255) || (r === 0 && g === 0 && b === 0);
    return brancoOuPreto && a < 1;
  };
  linhas.forEach((l, i) => {
    for (const m of l.matchAll(/RGBA\(\s*\d+,\s*\d+,\s*\d+,\s*[\d.]+\s*\)/g)) {
      if (!estrutural(m[0])) e(i, `literal de cor fora do token: ${m[0]}`);
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

  // 7a. Controle classico que pinta o fundo por token mas nao declara a cor do
  // TEXTO (ou o fundo da seta) deixa essa parte com a cor do TEMA do Studio, que
  // continua Motiva. Foi o que escondeu os nomes do combo de usuario: Color nunca
  // esteve no YAML, nem no original, entao tokenizar o que existia nao bastava.
  const EXIGE_SE_PINTADO = [
    { tipo: /Control:\s*Classic\/ComboBox@/, se: /(^|\n)\s*(Fill|SelectionFill):/, exige: ['Color'] },
    { tipo: /Control:\s*Classic\/ComboBox@/, se: /(^|\n)\s*ChevronFill:/, exige: ['ChevronBackground'] },
    { tipo: /Control:\s*Classic\/TextInput@/, se: /(^|\n)\s*Fill:/, exige: ['Color', 'HoverFill'] },
  ];
  for (const b of blocos) {
    for (const r of EXIGE_SE_PINTADO) {
      if (!r.tipo.test(b) || !r.se.test(b)) continue;
      const nome = (b.match(/- (\w+):/) || [, '?'])[1];
      for (const p of r.exige) {
        if (!new RegExp('(^|\\n)\\s*' + p + ':').test(b)) {
          erros.push(`${path.basename(arquivo)} ${nome}: declara cor mas nao ${p} — essa parte fica com a cor do tema`);
        }
      }
    }
  }

  // 7c. Classic/ComboBox com mais de um DisplayFields rende a lista VAZIA, sem
  // erro nenhum no Studio. Visto tres vezes no combo de usuario do Service Desk.
  // Para mostrar dois dados, concatenar em Items e exibir um campo so.
  for (const b of blocos) {
    if (!/Control:\s*Classic\/ComboBox@/.test(b)) continue;
    const m = b.match(/DisplayFields:\s*=\[([^\]]*)\]/);
    if (!m) continue;
    const campos = m[1].split(',').filter((x) => x.trim().length);
    if (campos.length > 1) {
      const nome = (b.match(/- (\w+):/) || [, '?'])[1];
      erros.push(`${path.basename(arquivo)} ${nome}: DisplayFields com ${campos.length} campos — a lista rende vazia; usar um campo so`);
    }
  }

  // 7b. Dentro do template de galeria, Parent.Width/Height nao existe — e TemplateWidth
  // /TemplateHeight. Dono da linha e a galeria MAIS INTERNA que a contem, nunca todas
  // as ancestrais (falso positivo recorrente treina o operador a ignorar o validador).
  {
    const pilha = []; // { indent, tipo }
    linhas.forEach((l, i) => {
      const mNome = l.match(/^(\s*)- \w+:$/);
      if (mNome) {
        const ind = mNome[1].length;
        while (pilha.length && pilha[pilha.length - 1].indent >= ind) pilha.pop();
        pilha.push({ indent: ind, tipo: null });
        return;
      }
      const mCtrl = l.match(/^\s*Control:\s*(\S+)/);
      if (mCtrl && pilha.length) { pilha[pilha.length - 1].tipo = mCtrl[1]; return; }
      if (!/Parent\.(Width|Height)\b/.test(l)) return;
      const ind = l.match(/^\s*/)[0].length;
      // A linha pertence ao controle donos[ultimo]; o "Parent" da formula e o
      // controle imediatamente acima dele — donos[ultimo - 1].
      const donos = pilha.filter((p) => p.indent < ind);
      const dono = donos[donos.length - 2];
      if (dono && /^Gallery@/.test(dono.tipo || '')) {
        e(i, 'Parent.Width/Height dentro do template de galeria — usar Parent.TemplateWidth/TemplateHeight');
      }
    });
  }

  // 8. Toda referencia a controle existe na tela.
  const declarados = new Set();
  for (const m of txt.matchAll(/^\s*- (\w+):$/gm)) declarados.add(m[1]);
  linhas.forEach((l, i) => {
    for (const m of l.matchAll(/\bSelect\((\w+)\)/g)) {
      // Parent e Self sao palavras-chave, nao controles declarados.
      if (m[1] === 'Parent' || m[1] === 'Self') continue;
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
  // 10b. Carga inicial sem recorte por data. Ordenar a lista inteira por ID e
  // cortar com FirstN traz os N mais recentes de TODOS os aeroportos — lento, e
  // o corte ainda descarta registro do usuario. O checklist manda limitar a
  // consulta inicial por data, que e o que delega no SharePoint.
  linhas.forEach((l, i) => {
    const m = l.match(/Sort\(\s*$/);
    if (!m) return;
    const fonte = (linhas[i + 1] || '').trim().replace(/,$/, '');
    const ordenaPorId = /^ID,?$/.test((linhas[i + 2] || '').trim());
    if (!ordenaPorId) return;
    if (/^Filter\($/.test(fonte)) return;
    if (/^col_/.test(fonte)) return; // colecao em memoria, nao e consulta
    e(i + 1, `consulta sem recorte inicial por data: Sort(${fonte}, ID, ...)`);
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
let totalCasos = 0;
function autoteste() {
  const casos = [
    ['raiz', 'Screens:\n Login:\n  Properties:\n', /raiz invalida/],
    ['overflow', 'Screens:\n  L:\n    Properties:\n      Overflow: =1\n', /Overflow/],
    ['token', 'Screens:\n  L:\n    Properties:\n      Fill: =thmInventado\n', /nao definido/],
    ['literal', 'Screens:\n  L:\n    Properties:\n      Fill: =RGBA(1, 2, 3, 1)\n', /literal de cor/],
    ['select', 'Screens:\n  L:\n    Properties:\n      OnVisible: =Select(btnFantasma)\n', /controle inexistente/],
    ['cor translucida de marca', 'Screens:\n  L:\n    Properties:\n      Fill: =RGBA(96, 70, 237, 0.5)\n', /literal de cor/],
    ['consulta sem recorte por data', [
      'Screens:',
      '  L:',
      '    Properties:',
      '      OnVisible: |-',
      '        =ClearCollect(',
      '            col_x,',
      '            FirstN(',
      '                Sort(',
      '                    tbl_Alguma,',
      '                    ID,',
      '                    SortOrder.Descending',
      '                ),',
      '                100',
      '            )',
      '        )',
      '',
    ].join('\n'), /recorte inicial por data/],
    ['classico pintado sem Color', [
      'Screens:',
      '  L:',
      '    Children:',
      '      - cmbX:',
      '          Control: Classic/ComboBox@2.4.0',
      '          Properties:',
      '            Fill: =thmFundo',
      '',
    ].join('\n'), /nao Color/],
    ['combo com varios DisplayFields', [
      'Screens:',
      '  L:',
      '    Children:',
      '      - cmbY:',
      '          Control: Classic/ComboBox@2.4.0',
      '          Properties:',
      '            Color: =thmTexto',
      '            DisplayFields: =["DisplayName","Email"]',
      '',
    ].join('\n'), /rende vazia/],
    ['componente sem AccessAppScope', [
      'ComponentDefinitions:',
      '  Comp1:',
      '    DefinitionType: CanvasComponent',
      '    Properties:',
      '      Fill: =thmPrimaria',
      '',
    ].join('\n'), /AccessAppScope/],
    ['default vazio em propriedade de entrada', [
      'ComponentDefinitions:',
      '  Comp1:',
      '    DefinitionType: CanvasComponent',
      '    AccessAppScope: true',
      '    CustomProperties:',
      '      Sub1:',
      '        PropertyKind: Input',
      '        DataType: Text',
      '        Default: =',
      '    Properties:',
      '      Fill: =thmPrimaria',
      '',
    ].join('\n'), /PA2231/],
    ['parent em galeria', [
      'Screens:',
      '  L:',
      '    Properties:',
      '      Fill: =thmFundo',
      '    Children:',
      '      - Gal1:',
      '          Control: Gallery@2.15.0',
      '          Properties:',
      '            Items: =col_x',
      '          Children:',
      '            - Lbl1:',
      '                Control: Label@2.5.1',
      '                Properties:',
      '                  Width: =Parent.Width',
      '',
    ].join('\n'), /template de galeria/],
  ];
  totalCasos = casos.length;
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
  // Regra do App.Formulas: testada direto na funcao, nos dois sentidos.
  totalCasos += 1;
  if (!htmlTokenComAspaSimples(`htmlFonte = "font-family:'Segoe UI',Arial;"`)
      || htmlTokenComAspaSimples(`htmlFonte = "font-family:Segoe UI,Arial;"`)) {
    console.error('AUTOTESTE FALHOU: a regra "html* com aspa simples" nao discrimina os dois casos');
    ok = false;
  }
  return ok;
}

const alvos = process.argv.slice(2).length
  ? process.argv.slice(2)
  : fs.readdirSync(__dirname).filter((f) => f.endsWith('.pa.yaml')).map((f) => path.join(__dirname, f));

if (!autoteste()) process.exit(2);
console.log(`autoteste: ${totalCasos} regras reprovaram os casos construidos\n`);

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
