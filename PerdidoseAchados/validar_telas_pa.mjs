import fs from 'fs';

let falhas = 0;
function check(ok, msg) {
  console.log((ok ? '  OK   ' : '  FALHA') + '  ' + msg);
  if (!ok) falhas++;
}

for (const P of process.argv.slice(2)) {
  console.log('\n=== ' + P + ' ===');
  const raw = fs.readFileSync(P, 'utf8');
  const lines = raw.replace(/\r\n/g, '\n').split('\n');

  // 1. estrutura raiz
  check(lines[lines.findIndex(l => l.startsWith('Screens:'))] === 'Screens:',
    'Screens: na coluna 1');
  const telas = lines.filter(l => /^ {2}\S.*:$/.test(l));
  check(telas.length === 1, 'exatamente 1 tela por arquivo (achei ' + telas.length + ': ' + telas.map(t => t.trim()).join(',') + ')');

  // 2. proibidos pelas licoes aprendidas
  check(!/^\s*Overflow:/m.test(raw), 'nenhum "Overflow:" (deve ser LayoutOverflowY)');
  check(raw.indexOf('%DATACARD_') < 0, 'nenhum placeholder %DATACARD_');
  check(raw.indexOf('\t') < 0, 'nenhum caractere TAB');

  // 3. nomes de controle duplicados (PA2110)
  const nomes = [];
  for (const l of lines) {
    const m = l.match(/^\s*- ([A-Za-z_][A-Za-z0-9_]*):\s*$/);
    if (m) nomes.push(m[1]);
  }
  const vistos = new Set(), dup = new Set();
  for (const n of nomes) { if (vistos.has(n)) dup.add(n); vistos.add(n); }
  check(dup.size === 0, 'nenhum nome de controle duplicado' + (dup.size ? ' -> ' + [...dup].join(', ') : ' (' + nomes.length + ' controles)'));

  // 4. TextInput@0.0.54 nao pode ter Default:
  let badDefault = [];
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].indexOf('Control: TextInput@0.0.54') >= 0) {
      for (let j = i + 1; j < Math.min(i + 25, lines.length); j++) {
        if (/^\s*- \S+:\s*$/.test(lines[j])) break;
        if (/^\s*Default:/.test(lines[j])) badDefault.push(j + 1);
      }
    }
  }
  check(badDefault.length === 0, 'nenhum TextInput@0.0.54 com "Default:"' + (badDefault.length ? ' -> linhas ' + badDefault.join(',') : ''));

  // 5. no maximo um MetadataKey: FieldValue por DataCard
  //    (so conta dentro de blocos cujo Control e TypedDataCard, delimitados pela indentacao)
  const ruins = [];
  let nCards = 0;
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(\s*)- (\S+):\s*$/);
    if (!m) continue;
    if (!(lines[i + 1] || '').includes('Control: TypedDataCard')) continue;
    nCards++;
    const ind = m[1].length;
    let cont = 0;
    for (let j = i + 1; j < lines.length; j++) {
      const mm = lines[j].match(/^(\s*)- \S+:\s*$/);
      if (mm && mm[1].length <= ind) break;            // proximo card irmao/superior
      if (/MetadataKey: FieldValue\s*$/.test(lines[j])) cont++;
    }
    if (cont > 1) ruins.push(m[2] + ' (' + cont + ')');
  }
  check(ruins.length === 0, 'no maximo 1 MetadataKey: FieldValue por DataCard (' + nCards + ' cards)' + (ruins.length ? ' -> ' + ruins.join(', ') : ''));

  // 6. balanceamento de parenteses/chaves/colchetes nas formulas
  let par = 0, chv = 0, col = 0;
  for (const ch of raw) {
    if (ch === '(') par++; else if (ch === ')') par--;
    else if (ch === '{') chv++; else if (ch === '}') chv--;
    else if (ch === '[') col++; else if (ch === ']') col--;
  }
  check(par === 0 && chv === 0 && col === 0,
    'parenteses/chaves/colchetes balanceados (() ' + par + ', {} ' + chv + ', [] ' + col + ')');

  // 7. indentacao par — apenas em linhas de CHAVE, ignorando conteudo de block scalar (|- / |)
  const impar = [];
  let blockInd = -1;   // indentacao da chave que abriu um block scalar
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (l.trim() === '') continue;
    const n = l.length - l.replace(/^ +/, '').length;
    if (blockInd >= 0) {
      if (n > blockInd) continue;      // ainda dentro do texto da formula
      blockInd = -1;                   // saiu do bloco
    }
    if (/:\s*\|-?\s*$/.test(l)) { blockInd = n; continue; }
    if (!/^\s*(- )?[A-Za-z_'"][^:]*:/.test(l)) continue;  // nao e linha de chave
    if (n % 2 !== 0) impar.push(i + 1);
  }
  check(impar.length === 0, 'indentacao par nas linhas de chave' + (impar.length ? ' -> ' + impar.slice(0, 5).join(',') : ''));

  // 8. arvore de indentacao bem formada: cada chave e irma do topo, filha dele, ou
  //    volta para um nivel ancestral existente. Pega bloco inserido em profundidade errada.
  const orfas = [];
  const pilha = [];
  let bi = -1;
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (l.trim() === '' || /^\s*#/.test(l)) continue;
    const n = l.length - l.replace(/^ +/, '').length;
    if (bi >= 0) { if (n > bi) continue; bi = -1; }
    if (/:\s*\|-?\s*$/.test(l)) { bi = n; }
    if (!/^\s*(- )?[A-Za-z_'"][^:]*:/.test(l)) continue;
    while (pilha.length && pilha[pilha.length - 1] > n) pilha.pop();
    if (pilha.length && pilha[pilha.length - 1] !== n) {
      if (n < pilha[pilha.length - 1]) orfas.push(i + 1);
    }
    if (!pilha.length || pilha[pilha.length - 1] !== n) pilha.push(n);
  }
  check(orfas.length === 0, 'arvore de indentacao bem formada' + (orfas.length ? ' -> linhas ' + orfas.slice(0, 5).join(',') : ''));

  // 9. dentro do template de galeria: Parent.Width/Height nao resolvem a linha
  //    renderizada -> usar Parent.TemplateWidth / Parent.TemplateHeight.
  //    (licao registrada em 23/09/2026: ScreenCadastrar / Table2)
  const galerias = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(\s*)- (\S+):\s*$/);
    if (!m) continue;
    if (!/Control: Gallery@/.test(lines[i + 1] || '')) continue;
    const ind = m[1].length;
    let fim = i + 1;
    while (fim < lines.length) {
      const mm = lines[fim].match(/^(\s*)- \S+:\s*$/);
      if (mm && mm[1].length <= ind) break;
      fim++;
    }
    // a galeria declara Width propria? (antes do primeiro Children:)
    let temWidth = false;
    for (let j = i + 1; j < g_fimProps(lines, i, ind); j++) {
      if (/^\s*Width:\s*=/.test(lines[j])) { temWidth = true; break; }
    }
    galerias.push({ nome: m[2], ini: i, fim, temWidth });
  }
  function g_fimProps(arr, ini, ind) {
    for (let j = ini + 1; j < arr.length; j++) {
      if (/^\s*Children:\s*$/.test(arr[j])) return j;
      const mm = arr[j].match(/^(\s*)- \S+:\s*$/);
      if (mm && mm[1].length <= ind) return j;
    }
    return arr.length;
  }

  // Uma linha dentro das PROPRIAS propriedades de uma galeria (antes do
  // Children:) tem como Parent a galeria de FORA, nao ela mesma.
  for (const g of galerias) g.propsFim = g_fimProps(lines, g.ini,
    lines[g.ini].length - lines[g.ini].replace(/^ +/, '').length);

  // Um GroupContainer entre a linha e a galeria troca o Parent: passa a ser o
  // container, que tem Width propria. Ali Parent.Width esta correto.
  const containers = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(\s*)- (\S+):\s*$/);
    if (!m || !/Control: GroupContainer@/.test(lines[i + 1] || '')) continue;
    const ind = m[1].length;
    let fim = i + 1;
    while (fim < lines.length) {
      const mm = lines[fim].match(/^(\s*)- \S+:\s*$/);
      if (mm && mm[1].length <= ind) break;
      fim++;
    }
    containers.push({ nome: m[2], ini: i, fim, propsFim: g_fimProps(lines, i, ind) });
  }

  const risco = [], ok = [];
  for (let j = 0; j < lines.length; j++) {
    if (!/\bParent\.(Width|Height)\b/.test(lines[j])) continue;
    let dono = null;
    for (const g of galerias)
      if (j > g.propsFim && j < g.fim && (!dono || g.ini > dono.ini)) dono = g;
    if (!dono) continue;
    // ha container mais interno que a galeria dona? entao o Parent e ele
    let cont = null;
    for (const c of containers)
      if (j > c.propsFim && j < c.fim && c.ini > dono.ini && (!cont || c.ini > cont.ini)) cont = c;
    if (cont) continue;
    (dono.temWidth ? ok : risco).push('L' + (j + 1) + ' em ' + dono.nome);
  }
  // 11. cor por palavra-chave CSS dentro do HTML (green, red...) escapa de
  //     qualquer busca por '#' e fura o design system. Usar o hex da paleta.
  const KW = ['black','silver','gray','grey','white','maroon','red','purple',
    'fuchsia','green','lime','olive','yellow','navy','blue','teal','aqua','orange'];
  const kws = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/\bcolor\s*[:=]\s*'?\s*([A-Za-z]+)/);
    if (m && KW.includes(m[1].toLowerCase())) kws.push('L' + (i + 1) + ' (' + m[1] + ')');
  }
  check(kws.length === 0,
    'sem cor por palavra-chave CSS no HTML (usar hex da paleta)' +
    (kws.length ? ' -> ' + kws.slice(0, 6).join(', ') : ''));

  // 12. propriedade dentro de bloco escalar. Inserir uma propriedade por ordem
  //     alfabetica sem pular o corpo de um "|-" a enfia no meio da formula.
  //     YAML continua valido (vira texto do escalar) e so o Studio reclama.
  const dentro = [];
  {
    let bloco = -1;
    for (let i = 0; i < lines.length; i++) {
      const l = lines[i];
      if (l.trim() === '') continue;
      const n = l.length - l.replace(/^ +/, '').length;
      if (bloco >= 0) {
        if (n > bloco) {
          if (/^\s*(X|Y|Width|Height|Fill|Visible|BasePaletteColor|Appearance)\s*:\s*=/.test(l))
            dentro.push('L' + (i + 1) + ' (' + l.trim().split(':')[0] + ')');
          continue;
        }
        bloco = -1;
      }
      if (/:\s*\|[-+]?\s*$/.test(l)) bloco = n;
    }
  }
  check(dentro.length === 0,
    'nenhuma propriedade dentro de bloco escalar' +
    (dentro.length ? ' -> ' + dentro.slice(0, 6).join(', ') : ''));

  // 13. Select(Parent) sob GroupContainer. GroupContainer nao tem OnSelect,
  //     entao Select(Parent) ali e erro do Studio. Acontece ao mover controles
  //     para dentro de um container: o Parent deixa de ser a galeria.
  const selPai = [];
  for (let j = 0; j < lines.length; j++) {
    if (!/Select\(\s*Parent\s*\)/.test(lines[j])) continue;
    let cont = null;
    for (const c of containers)
      if (j > c.propsFim && j < c.fim && (!cont || c.ini > cont.ini)) cont = c;
    if (!cont) continue;
    // so acusa se o container for mais interno que qualquer galeria que envolva a linha
    let gal = null;
    for (const g of galerias)
      if (j > g.propsFim && j < g.fim && (!gal || g.ini > gal.ini)) gal = g;
    if (gal && gal.ini > cont.ini) continue;
    selPai.push('L' + (j + 1) + ' em ' + cont.nome);
  }
  check(selPai.length === 0,
    'sem Select(Parent) sob GroupContainer (use o nome da galeria)' +
    (selPai.length ? ' -> ' + selPai.slice(0, 6).join(', ') : ''));

  // 14. corpo de bloco escalar orfao. Remover a CHAVE de uma propriedade
  //     escrita como "|-" sem remover o corpo deixa as linhas penduradas na
  //     propriedade anterior, que passa a ter um valor multi-linha invalido.
  //     O YAML continua valido; so o Studio reclama ("Valor Color esperado").
  const orfasEscalar = [];
  {
    let ultima = -1;
    for (let i = 0; i < lines.length; i++) {
      const l = lines[i];
      if (l.trim() === '') continue;
      const n = l.length - l.replace(/^ +/, '').length;
      if (ultima >= 0) {
        const k = lines[ultima];
        const kn = k.length - k.replace(/^ +/, '').length;
        const abre = /:\s*[|>][-+]?\s*$/.test(k);
        const temValor = /:\s*=/.test(k);
        if (n > kn && !abre && temValor) {
          orfasEscalar.push('L' + (i + 1) + ' sob ' + k.trim().split(':')[0]);
          continue;
        }
      }
      if (/^ *(- )?[A-Za-z_'"][^:]*:/.test(l)) ultima = i;
    }
  }
  check(orfasEscalar.length === 0,
    'nenhum corpo de bloco escalar orfao' +
    (orfasEscalar.length ? ' -> ' + orfasEscalar.slice(0, 4).join(', ') : ''));

  // 10. PA2108: Text@0.0.51 nao tem propriedade 'Color' (usar FontColor)
  const cor = [];
  for (let i = 0; i < lines.length; i++) {
    if (!/Control: Text@0\.0\.51/.test(lines[i])) continue;
    for (let j = i + 1; j < lines.length; j++) {
      if (/^\s*- \S+:\s*$/.test(lines[j])) break;
      if (/^\s*Color: =/.test(lines[j])) cor.push('L' + (j + 1));
    }
  }
  check(cor.length === 0,
    "sem 'Color' em Text@0.0.51 (PA2108 - usar FontColor)" +
    (cor.length ? ' -> ' + cor.slice(0, 6).join(', ') : ''));

  // 18. propriedade de cor deixada VAZIA cai no tema do Studio (que e roxo).
  // A passada de paleta cobriu Appearance e BasePaletteColor, mas nao os estados
  // Hover/Pressed — e foi por ai que o roxo voltou a aparecer na ScreenCadastrar.
  const vazias = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^s*([A-Za-z]*(?:Color|Fill)): =s*$/);
    if (!m) continue;
    vazias.push("L" + (i + 1) + " " + m[1]);
  }
  check(vazias.length === 0,
    "nenhuma propriedade de cor vazia (cai no tema do Studio)" +
    (vazias.length ? " -> " + vazias.slice(0, 8).join(", ") : ""));

  check(risco.length === 0,
    'sem Parent.Width/Height em galeria SEM Width proprio (' + galerias.length + ' galerias)' +
    (risco.length ? ' -> ' + risco.slice(0, 8).join(', ') : ''));
  if (ok.length) {
    console.log('  nota   ' + ok.length + ' uso(s) de Parent.Width em galeria COM Width proprio ' +
      '(baixo risco, conferir visualmente): ' + ok.slice(0, 4).join(', '));
  }
}

console.log('\n' + (falhas === 0 ? 'TODAS AS VERIFICACOES PASSARAM' : falhas + ' VERIFICACAO(OES) FALHARAM'));
process.exit(falhas === 0 ? 0 : 1);
