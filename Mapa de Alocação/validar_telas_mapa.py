#!/usr/bin/env python3
"""Validador das telas do Mapa de Alocação de Pátio.

Adaptado de Frotas/validar_telas.py. Mantém as regras do
LICOES_APRENDIDAS_POWERAPPS_YAML.md e acrescenta três regras de performance
próprias deste app (21, 22 e 23) mais duas de integridade do registro
multi-dia (28 e 29).
"""
import re, sys, os, collections, yaml

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
EXPORT = os.path.join(RAIZ, 'REA', 'ScreenAcionamentosPlemPraiV2.pa.yaml')
TELAS = [os.path.join(BASE, n) for n in
         ('scrMapaInicio.pa.yaml', 'scrMapaPatio.pa.yaml', 'scrMapaReferencia.pa.yaml')]
FX = os.path.join(BASE, 'AppFormulas_Mapa.fx.md')
FONTE = "'tb_alocacoesMapa'"
TELAS_NOMES = {'scrMapaInicio', 'scrMapaPatio', 'scrMapaReferencia'}
# coleções montadas em runtime — não são named formulas
RUNTIME = {'colDia', 'colGrade', 'colValida'}

erros = []


# ---- catálogo comprovado a partir do export do Studio ----
def catalogo(path):
    props = collections.defaultdict(set)
    icons = set()
    cur = None
    for l in open(path, encoding='utf-8'):
        m = re.match(r'^(\s*)Control:\s*(\S+)', l)
        if m:
            cur = m.group(2)
            continue
        m2 = re.match(r'^\s*([A-Za-z][A-Za-z0-9_]*):\s*(=|\||$|")', l)
        if m2 and cur:
            props[cur].add(m2.group(1))
        mi = re.match(r'^\s*Icon:\s*=(.+?)\s*$', l)
        if mi and mi.group(1):
            icons.add(mi.group(1))
    return props, icons


PROV, ICONS = catalogo(EXPORT)
# comprovado no round-trip do app de Frotas (Studio gravou, exportou e manteve) — 2026-08-26
# Só entra aqui o que foi conferido em um .pa.yaml real do repositório, na posição
# alfabética (prova de round-trip do Studio). Conferido em 2026-08-28 por
# varredura de todos os .pa.yaml/.yaml do workspace, exceto os deste projeto.
PROV['Button@0.0.45'].add('PaddingTop')      # Frotas/scrFrotaPainel.pa.yaml
PROV['Button@0.0.45'].add('FillPortions')    # Frotas/scrFrotaForm.pa.yaml, REA
PROV['DatePicker@0.0.46'].add('FillPortions')  # Frotas/scrFrotaForm.pa.yaml
ICONS.add('"ArrowExit"')                     # Frotas/scrFrotaPainel.pa.yaml
ESTRUT = {'Properties', 'Children', 'Control', 'Variant', 'MetadataKey'}

nomes = collections.Counter()
definidos = set()
usados = set()
arvores = {}

for t in TELAS:
    nome = os.path.basename(t)
    txt = open(t, encoding='utf-8').read()
    linhas = txt.split('\n')

    # 2 estrutura raiz
    if not linhas[0].startswith('Screens:'):
        erros.append(f'{nome}: raiz')
    if txt.startswith('﻿'):
        erros.append(f'{nome}: BOM')
    if not re.match(r'^  scr\w+:$', linhas[1]):
        erros.append(f'{nome}: nome da tela fora do recuo 2')

    # 6 proibições
    for proib in ('Overflow:', '%DATACARD', 'DelayItemLoading', 'LoadingSpinner'):
        if proib in txt:
            erros.append(f'{nome}: contém {proib}')

    # 10 locale — .pa.yaml é invariante
    if ';;' in txt:
        erros.append(f'{nome}: ";;" (pt-BR) dentro de YAML invariante')

    # 28 o filtro do dia é por FAIXA — igualdade some com o registro multi-dia
    if re.search(r'data_operacao\s*=\s*varData', txt):
        erros.append(f'{nome}: filtro do dia com "data_operacao = varData"; desde o registro '
                     f'multi-dia tem que ser "data_operacao <= varData And data_fim >= varData", '
                     f'senão pernoite e interdição de vários dias somem da grade sem erro')
    if 'data_operacao' in txt and 'data_fim' not in txt:
        erros.append(f'{nome}: usa data_operacao sem nunca citar data_fim — filtro de faixa incompleto')

    # 29 atributo title do HTML só pode ser alimentado por texto já escapado
    for i, l in enumerate(linhas, 1):
        if 'title=' in l and '.dica' not in l:
            erros.append(f'{nome}:{i}: title do HTML sem o campo .dica; texto livre cru fecha '
                         f'o atributo numa aspa simples e desmonta a linha inteira da grade — '
                         f'monte a dica em colDia, com escape de & < > e aspa, e leia _b.dica aqui')

    # 3/4/7 propriedades, tipos e ícones comprovados
    cur = None
    for i, l in enumerate(linhas, 1):
        m = re.match(r'^\s*Control:\s*(\S+)', l)
        if m:
            cur = m.group(1)
            if cur not in PROV:
                erros.append(f'{nome}:{i} tipo não comprovado {cur}')
            continue
        mn = re.match(r'^\s*- ([A-Za-z]\w*):$', l)
        if mn:
            nomes[mn.group(1)] += 1
            definidos.add(mn.group(1))
            continue
        mp = re.match(r'^\s*([A-Z][A-Za-z0-9_]*):\s*(=|\|-)', l)
        if mp and cur:
            p = mp.group(1)
            if p in ESTRUT:
                continue
            if p not in PROV.get(cur, set()):
                erros.append(f'{nome}:{i} {cur} não comprova a propriedade {p}')
            if cur == 'TextInput@0.0.54' and p == 'Default':
                erros.append(f'{nome}:{i} Default em TextInput moderno')
        mi = re.match(r'^\s*Icon:\s*=(.+?)\s*$', l)
        if mi and mi.group(1) not in ICONS:
            erros.append(f'{nome}:{i} ícone não comprovado {mi.group(1)}')

    d = yaml.safe_load(txt)
    arvores[nome] = d

    # 9 parênteses balanceados por fórmula
    def anda(o, path=''):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and v.startswith('='):
                    s = re.sub(r'"[^"]*"', '', v)
                    if s.count('(') != s.count(')'):
                        erros.append(f'{nome}: parênteses em {path}.{k}')
                    for ref in re.findall(r'\b([a-z]{3}[A-Z]\w*)\.', s):
                        usados.add(ref)
                    for ref in re.findall(r'\b(scr[A-Z]\w*)\b', s):
                        usados.add(ref)
                anda(v, f'{path}.{k}')
        elif isinstance(o, list):
            for it in o:
                anda(it, path)
    anda(d)

# 4 nome de controle é único no APP inteiro, não por tela
for n, c in nomes.items():
    if c > 1:
        erros.append(f'nome de controle duplicado no app: {n} ({c}x)')

# 5 referências a controles/telas inexistentes
for r in sorted(usados):
    if r in definidos or r in TELAS_NOMES:
        continue
    if re.match(r'^(thm|hx|col|html|map|var|loc)', r):
        continue
    if r in ('ThisItem', 'Parent', 'Self', 'User', 'Now', 'Today', 'Value'):
        continue
    erros.append(f'referência a controle/tela inexistente: {r}')

# 8 todo token thm*/hx*/col*/map* usado nas telas está declarado no App.Formulas
fx = open(FX, encoding='utf-8').read()
declarados = set(re.findall(r'^(\w+)\s*=', fx, re.M)) | set(re.findall(r'^(\w+)\s+=', fx, re.M))
usados_fx = set()
for t in TELAS:
    for m in re.findall(r'\b((?:thm|hx|html|col|map)[A-Z][A-Za-z0-9_]*)\b',
                        open(t, encoding='utf-8').read()):
        usados_fx.add(m)
for u in sorted(usados_fx):
    if u in RUNTIME:
        continue
    if u not in declarados:
        erros.append(f'nome não declarado no App.Formulas: {u}')

# 11 contraste: texto claro obrigatório sobre fundo escuro; nada de branco literal
ESCURO = {'=thmPrimaria', '=thmPrimariaEscura', '=thmAcao', '=thmAmbar', '=thmVermelho'}


def contraste(no, fundo, nome_arq):
    for item in (no or []):
        n = list(item)[0]
        c = item[n]
        props = c.get('Properties') or {}
        meu = props.get('Fill', fundo)
        ctrl = c.get('Control', '')
        base = props.get('BasePaletteColor', '')
        escuro = meu in ESCURO or (ctrl.startswith('Button')
                                   and props.get('Appearance', '').endswith('.Primary')
                                   and base in ESCURO)
        if escuro:
            if ctrl.startswith('HtmlViewer') and props.get('Color') != '=thmTextoBarra':
                erros.append(f'{nome_arq}: {n} HtmlViewer sobre escuro sem Color=thmTextoBarra')
            if ctrl.startswith('Button') and props.get('FontColor') != '=thmTextoBarra':
                erros.append(f'{nome_arq}: {n} Button sobre escuro sem FontColor=thmTextoBarra')
        contraste(c.get('Children'), meu, nome_arq)


for t in TELAS:
    nome = os.path.basename(t)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    contraste(d['Screens'][tela].get('Children'), None, nome)
    txt = open(t, encoding='utf-8').read()
    if '#FFFFFF' in txt or '255,255,255' in txt:
        erros.append(f'{nome}: branco literal — use hxTextoBarra ou hxSuperficie')

# 12 PA1001: TODA propriedade começa com '='
def prefixo(no, nome_arq):
    for item in (no or []):
        n = list(item)[0]
        c = item[n]
        for prop, val in (c.get('Properties') or {}).items():
            if not isinstance(val, str) or not val.startswith('='):
                erros.append(f"{nome_arq}: {n}.{prop} não começa com '=' ({str(val)[:40]!r})")
        prefixo(c.get('Children'), nome_arq)


for t in TELAS:
    nome = os.path.basename(t)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    for prop, val in (d['Screens'][tela].get('Properties') or {}).items():
        if not isinstance(val, str) or not val.startswith('='):
            erros.append(f"{nome}: {tela}.{prop} não começa com '='")
    prefixo(d['Screens'][tela].get('Children'), nome)

# 13 AutoLayout: filho sem tamanho no eixo do pai colapsa
CONTEINER = ('GroupContainer', 'Gallery')


def tamanho(no, dir_pai, nome_arq):
    for item in (no or []):
        n = list(item)[0]
        c = item[n]
        props = c.get('Properties') or {}
        ctrl = c.get('Control', '')
        if dir_pai and ctrl.startswith(CONTEINER):
            fp = props.get('FillPortions')   # ausente = 1 (padrão que o Studio omite)
            eixo = 'Height' if 'Vertical' in dir_pai else 'Width'
            if eixo not in props and fp == '=0':
                erros.append(f'{nome_arq}: {n} ({ctrl}) sem {eixo} nem FillPortions '
                             f'dentro de pai {dir_pai.split(".")[-1]}')
        tamanho(c.get('Children'),
                props.get('LayoutDirection') if ctrl.startswith('GroupContainer') else None,
                nome_arq)


for t in TELAS:
    nome = os.path.basename(t)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    tamanho(d['Screens'][tela].get('Children'), None, nome)

# 15 item de Children com mais de uma chave = subárvore desanexada por recuo
def um_por_item(no, nome_arq):
    tot = 0
    for item in (no or []):
        ks = list(item)
        if len(ks) != 1:
            erros.append(f'{nome_arq}: item de Children com chaves irmãs {ks} — recuo quebrado')
            continue
        tot += 1 + um_por_item(item[ks[0]].get('Children'), nome_arq)
    return tot


for t in TELAS:
    nome = os.path.basename(t)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    na_arvore = um_por_item(d['Screens'][tela].get('Children'), nome)
    no_texto = len(re.findall(r'^\s*- [A-Za-z]\w*:\s*$', open(t, encoding='utf-8').read(), re.M))
    if na_arvore != no_texto:
        erros.append(f'{nome}: {no_texto} controles no texto, {na_arvore} na árvore — '
                     f'recuo desanexou subárvore')

# 16 cor literal em tela é regressão — toda cor vem de token hx*/thm*
for t in TELAS:
    txt = open(t, encoding='utf-8').read()
    for m in sorted(set(re.findall(r'#[0-9A-Fa-f]{6}', txt))):
        erros.append(f'{os.path.basename(t)}: cor literal {m} — use um token hx*')
    for m in sorted(set(re.findall(r'RGBA\(', txt))):
        erros.append(f'{os.path.basename(t)}: RGBA( literal — use um token thm*')

# 20 ')' seguido de função sem operador é sintaxe inválida em Power Fx
OPERADORES = {'And', 'Or', 'Not', 'in', 'exactin', 'As'}


def justaposicao(no, nome_arq):
    for item in (no or []):
        n = list(item)[0]
        c = item[n]
        for prop, val in (c.get('Properties') or {}).items():
            if isinstance(val, str):
                limpo = re.sub(r'"[^"]*"', '""', val)
                for m in re.finditer(r'\)\s+([A-Za-z_]\w*)\s*\(', limpo):
                    if m.group(1) not in OPERADORES:
                        erros.append(f'{nome_arq}: {n}.{prop} — ")" seguido de '
                                     f'{m.group(1)}( sem vírgula/operador')
        justaposicao(c.get('Children'), nome_arq)


for t in TELAS:
    nome = os.path.basename(t)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    justaposicao(d['Screens'][tela].get('Children'), nome)


# 25 escopo implícito: função de escopo com aninhamento tem que declarar `As`.
# Sem alias, `patio` dentro de um LookUp resolve para a coluna homônima do escopo
# MAIS INTERNO — o Power Apps não acusa, só devolve a linha errada.
ESCOPO = ('Concat', 'ForAll', 'Filter', 'LookUp', 'Sort', 'With')
ANINHA = re.compile(r'\b(LookUp|Filter|Concat|ForAll)\s*\(')


def escopo_implicito(no, nome_arq):
    for item in (no or []):
        n = list(item)[0]
        c = item[n]
        for prop, val in (c.get('Properties') or {}).items():
            if not isinstance(val, str):
                continue
            for m in re.finditer(r'\b(Concat|ForAll)\s*\(', val):
                # recorta o argumento da tabela até a vírgula de primeiro nível
                i = m.end()
                nivel = 1
                j = i
                while j < len(val) and nivel > 0:
                    if val[j] == '(':
                        nivel += 1
                    elif val[j] == ')':
                        nivel -= 1
                    elif val[j] == ',' and nivel == 1:
                        break
                    j += 1
                arg = val[i:j]
                corpo = val[j:]
                if ' As ' not in arg and ANINHA.search(corpo[:1200]):
                    erros.append(f'{nome_arq}: {n}.{prop} — {m.group(1)}( sem "As <alias>" '
                                 f'com função aninhada no corpo; o nome de coluna liga ao '
                                 f'escopo mais interno')
        escopo_implicito(c.get('Children'), nome_arq)


for t_ in TELAS:
    nome = os.path.basename(t_)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    escopo_implicito(d['Screens'][tela].get('Children'), nome)


# 27 timer com AutoStart+Repeat continua rodando com a seção invisível —
# tem que ser barrado por uma variável de visibilidade dentro do OnTimerEnd.
def timer_gated(no, nome_arq):
    for item in (no or []):
        n = list(item)[0]
        c = item[n]
        props = c.get('Properties') or {}
        if c.get('Control', '').startswith('Timer'):
            if props.get('AutoStart') == '=true' and props.get('Repeat') == '=true':
                corpo = props.get('OnTimerEnd', '')
                if 'varMapaVisivel' not in corpo:
                    erros.append(f'{nome_arq}: {n} tem AutoStart+Repeat sem porteiro de '
                                 f'visibilidade no OnTimerEnd')
        timer_gated(c.get('Children'), nome_arq)


for t_ in TELAS:
    nome = os.path.basename(t_)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    timer_gated(d['Screens'][tela].get('Children'), nome)


# ============================================================================
# Regras de performance próprias deste app
# ============================================================================

def percorre(no, nome_arq, dentro_galeria=None):
    for item in (no or []):
        n = list(item)[0]
        c = item[n]
        ctrl = c.get('Control', '')
        props = c.get('Properties') or {}
        gal = dentro_galeria

        for prop, val in props.items():
            if not isinstance(val, str):
                continue
            limpo = re.sub(r'"[^"]*"', '""', val)

            # 21 nenhuma consulta à fonte de dados dentro de template de galeria
            if gal and FONTE in val:
                erros.append(f'{nome_arq}: {n}.{prop} consulta {FONTE} dentro do template '
                             f'da galeria {gal} — uma consulta por linha por render')

            # 22 nunca CountRows/CountIf sobre a lista
            for m in re.finditer(r'\b(CountRows|CountIf)\s*\(\s*' + re.escape(FONTE), val):
                erros.append(f'{nome_arq}: {n}.{prop} usa {m.group(1)} sobre {FONTE} — '
                             f'conte sobre colDia')

            # 23 template não pode ler o .Selected da própria galeria
            if gal and re.search(re.escape(gal) + r'\.Selected', limpo):
                erros.append(f'{nome_arq}: {n}.{prop} lê {gal}.Selected dentro do próprio '
                             f'template — dependência circular, devolve branco em silêncio')

        if ctrl.startswith('Gallery'):
            gal = n
        percorre(c.get('Children'), nome_arq, gal)


for t in TELAS:
    nome = os.path.basename(t)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    percorre(d['Screens'][tela].get('Children'), nome, None)

# 26 Text() com formato decimal dentro de CSS precisa de tag de idioma.
# Em cliente pt-BR, Text(3.47, "0.000") devolve "3,470" e quebra o `width:` do HTML.
def miolo(txt, abre):
    prof = 0
    for i in range(abre, len(txt)):
        if txt[i] == '(':
            prof += 1
        elif txt[i] == ')':
            prof -= 1
            if prof == 0:
                return txt[abre + 1:i]
    return ''


def texto_locale(no, nome_arq):
    for item in (no or []):
        n = list(item)[0]
        c = item[n]
        for prop, val in (c.get('Properties') or {}).items():
            if not isinstance(val, str):
                continue
            for m in re.finditer(r'\bText\s*\(', val):
                corpo = miolo(val, m.end() - 1)
                if re.search(r'"[0#]+[.,][0#]+"', corpo) and '"en-US"' not in corpo:
                    erros.append(f'{nome_arq}: {n}.{prop} — Text() com formato decimal sem '
                                 f'tag de idioma; em pt-BR sai vírgula e quebra o CSS')
        texto_locale(c.get('Children'), nome_arq)


for t_ in TELAS:
    nome = os.path.basename(t_)
    d = arvores[nome]
    tela = list(d['Screens'])[0]
    texto_locale(d['Screens'][tela].get('Children'), nome)


# 24 o .txt colável tem que refletir o .fx.md
txt_fx = os.path.join(BASE, 'App_Formulas_Mapa.txt')
if os.path.exists(txt_fx):
    conteudo = open(txt_fx, encoding='utf-8').read()
    for d in sorted(declarados):
        if not re.search(r'^' + re.escape(d) + r'\s*=', conteudo, re.M):
            erros.append(f'App_Formulas_Mapa.txt: falta a definição {d} que está no .fx.md')
else:
    erros.append('App_Formulas_Mapa.txt não existe — gere a partir do .fx.md')

print('CONTROLES:', sum(nomes.values()), '| TELAS:', len(TELAS),
      '| TIPOS COMPROVADOS:', len(PROV))
if erros:
    print('\n'.join(f'ERRO  {e}' for e in erros))
    sys.exit(1)
print('OK — todas as validações passaram')
