import re,sys,collections,yaml,os
BASE='/workspaces/codespaces-blank'
EXPORT=f'{BASE}/REA/ScreenAcionamentosPlemPraiV2.pa.yaml'
TELAS=[f'{BASE}/Frotas/{n}' for n in ('scrLoginContexto.pa.yaml','scrFrotaPainel.pa.yaml','scrFrotaLista.pa.yaml','scrFrotaForm.pa.yaml')]
FX=f'{BASE}/Frotas/AppFormulas_Frotas.fx.md'
erros=[];avisos=[]

# ---- catálogo comprovado a partir do export do Studio ----
def catalogo(path):
    props=collections.defaultdict(set); icons=set()
    cur=None
    for l in open(path,encoding='utf-8'):
        m=re.match(r'^(\s*)Control:\s*(\S+)',l)
        if m: cur=m.group(2); continue
        m2=re.match(r'^\s*([A-Za-z][A-Za-z0-9_]*):\s*(=|\||$|")',l)
        if m2 and cur: props[cur].add(m2.group(1))
        mi=re.match(r'^\s*Icon:\s*=(.+?)\s*$',l)
        if mi and mi.group(1): icons.add(mi.group(1))
    return props,icons
PROV,ICONS=catalogo(EXPORT)
# Comprovado no round-trip do app de Frotas (Studio gravou, exportou e manteve) — 2026-08-26
PROV['Button@0.0.45'].add('PaddingTop')
PROV['DatePicker@0.0.46'].add('FillPortions')
PROV['DropDown@0.0.45'].add('FillPortions')
ICONS.add('"ArrowExit"')
ESTRUT={'Properties','Children','Control','Variant','MetadataKey'}

nomes=collections.Counter(); usados=set(); definidos=set()
for t in TELAS:
    txt=open(t,encoding='utf-8').read()
    nome=os.path.basename(t)
    # 2 estrutura raiz
    linhas=txt.split('\n')
    if not linhas[0].startswith('Screens:'): erros.append(f'{nome}: raiz')
    if txt.startswith('﻿'): erros.append(f'{nome}: BOM')
    if not re.match(r'^  scr\w+:$',linhas[1]): erros.append(f'{nome}: nome da tela fora do recuo 2')
    # 6 proibições
    for proib in ('Overflow:','%DATACARD','DelayItemLoading','LoadingSpinner'):
        if proib in txt: erros.append(f'{nome}: contém {proib}')
    # 10 locale
    if ';;' in txt: erros.append(f'{nome}: ";;" (pt-BR) dentro de YAML invariante')
    # 3/4/7 percorre controles
    cur=None
    for i,l in enumerate(linhas,1):
        m=re.match(r'^\s*Control:\s*(\S+)',l)
        if m:
            cur=m.group(1)
            if cur not in PROV: erros.append(f'{nome}:{i} tipo não comprovado {cur}')
            continue
        mn=re.match(r'^\s*- ([A-Za-z]\w*):$',l)
        if mn: nomes[mn.group(1)]+=1; definidos.add(mn.group(1)); continue
        mp=re.match(r'^\s*([A-Z][A-Za-z0-9_]*):\s*(=|\|-)',l)
        if mp and cur:
            p=mp.group(1)
            if p in ESTRUT: continue
            if p not in PROV.get(cur,set()):
                erros.append(f'{nome}:{i} {cur} não comprova a propriedade {p}')
            if cur=='TextInput@0.0.54' and p=='Default':
                erros.append(f'{nome}:{i} Default em TextInput moderno')
        mi=re.match(r'^\s*Icon:\s*=(.+?)\s*$',l)
        if mi and mi.group(1) not in ICONS:
            erros.append(f'{nome}:{i} ícone não comprovado {mi.group(1)}')
    # 9 parênteses por fórmula (bloco escalar + linha simples)
    d=yaml.safe_load(txt)
    def anda(o,path=''):
        if isinstance(o,dict):
            for k,v in o.items():
                if isinstance(v,str) and v.startswith('='):
                    s=re.sub(r'"[^"]*"','',v)
                    if s.count('(')!=s.count(')'): erros.append(f'{nome}: parênteses em {path}.{k}')
                    for ref in re.findall(r'\b([a-z]{3}[A-Z]\w*)\.',s): usados.add(ref)
                    for ref in re.findall(r'\b(scr[A-Z]\w*)\b',s): usados.add(ref)
                anda(v,f'{path}.{k}')
        elif isinstance(o,list):
            for it in o: anda(it,path)
    anda(d)

# 4 duplicados
for n,c in nomes.items():
    if c>1: erros.append(f'nome de controle duplicado: {n} ({c}x)')

# 5 referências a controles/telas
telas={'scrLoginContexto','scrFrotaPainel','scrFrotaLista','scrFrotaForm'}
prefixos=('thm','hxP','col','htm')
for r in sorted(usados):
    if r in definidos or r in telas: continue
    if re.match(r'^(thm|hx|col|html|var|loc)',r): continue
    if r in ('ThisItem','Parent','Self','User','Now','Today','Value'): continue
    erros.append(f'referência a controle/tela inexistente: {r}')

# 8 tokens e tabelas nomeadas
fx=open(FX,encoding='utf-8').read()
declarados=set(re.findall(r'^(\w+)\s*=',fx,re.M))|set(re.findall(r'^(\w+)\s+=',fx,re.M))
locais={'colFrota','colFiltroAero','colDistAero','colOpAero'}
usados_fx=set()
for t in TELAS:
    for m in re.findall(r'\b((?:thm|hx|html|col)[A-Z][A-Za-z0-9_]*)\b',open(t,encoding='utf-8').read()):
        usados_fx.add(m)
for u in sorted(usados_fx):
    if u in locais: continue
    if u not in declarados: erros.append(f'nome não declarado no App.Formulas: {u}')


# 11 contraste: nada de branco puro sobre o escuro; texto claro obrigatório
ESCURO={'=thmPrimaria','=thmPrimariaEscura','=thmAcao'}
def _contraste(no, fundo, nome_arq):
    for item in (no or []):
        n=list(item)[0]; c=item[n]
        props=c.get('Properties') or {}
        meu=props.get('Fill', fundo); ctrl=c.get('Control','')
        base=props.get('BasePaletteColor','')
        escuro = meu in ESCURO or (ctrl.startswith('Button')
                 and props.get('Appearance','').endswith('.Primary') and base in ESCURO)
        if escuro:
            if ctrl.startswith('HtmlViewer') and props.get('Color') != '=thmTextoBarra':
                erros.append(f'{nome_arq}: {n} HtmlViewer sobre escuro sem Color=thmTextoBarra')
            if ctrl.startswith('Button') and props.get('FontColor') != '=thmTextoBarra':
                erros.append(f'{nome_arq}: {n} Button sobre escuro sem FontColor=thmTextoBarra')
        _contraste(c.get('Children'), meu, nome_arq)
for t in TELAS:
    nome=os.path.basename(t); d=yaml.safe_load(open(t,encoding='utf-8'))
    tela=list(d['Screens'])[0]
    _contraste(d['Screens'][tela].get('Children'), None, nome)
for t in TELAS:
    txt=open(t,encoding='utf-8').read()
    if '#FFFFFF' in txt or '255,255,255' in txt:
        erros.append(f'{os.path.basename(t)}: branco literal no HTML — use hxTextoBarra')


# 12 PA1001/YamlInvalidSyntax: TODA propriedade tem que começar com '='
def _prefixo(no, nome_arq):
    for item in (no or []):
        n=list(item)[0]; c=item[n]
        for prop, val in (c.get('Properties') or {}).items():
            if not isinstance(val, str) or not val.startswith('='):
                erros.append(f"{nome_arq}: {n}.{prop} não começa com '=' ({str(val)[:40]!r})")
        _prefixo(c.get('Children'), nome_arq)
for t in TELAS:
    nome=os.path.basename(t); d=yaml.safe_load(open(t,encoding='utf-8'))
    tela=list(d['Screens'])[0]
    for prop, val in (d['Screens'][tela].get('Properties') or {}).items():
        if not isinstance(val, str) or not val.startswith('='):
            erros.append(f"{nome}: {tela}.{prop} não começa com '='")
    _prefixo(d['Screens'][tela].get('Children'), nome)


# 13 AutoLayout: filho sem tamanho no eixo do pai colapsa (form em branco, 2026-08-25)
CONTEINER=('GroupContainer','Gallery')
def _tamanho(no, dir_pai, nome_arq):
    for item in (no or []):
        n=list(item)[0]; c=item[n]
        props=c.get('Properties') or {}
        ctrl=c.get('Control','')
        if dir_pai and ctrl.startswith(CONTEINER):
            fp=props.get('FillPortions')   # ausente = 1 (padrão que o Studio omite)
            eixo='Height' if 'Vertical' in dir_pai else 'Width'
            if eixo not in props and fp == '=0':
                erros.append(f'{nome_arq}: {n} ({ctrl}) sem {eixo} nem FillPortions dentro de pai {dir_pai.split(".")[-1]}')
        _tamanho(c.get('Children'), props.get('LayoutDirection') if ctrl.startswith('GroupContainer') else None, nome_arq)
for t in TELAS:
    nome=os.path.basename(t); d=yaml.safe_load(open(t,encoding='utf-8'))
    tela=list(d['Screens'])[0]
    _tamanho(d['Screens'][tela].get('Children'), None, nome)


# 15 estrutura: item de Children com mais de uma chave = subárvore desanexada por recuo
def _um_por_item(no, nome_arq):
    tot=0
    for item in (no or []):
        ks=list(item)
        if len(ks)!=1:
            erros.append(f'{nome_arq}: item de Children com chaves irmãs {ks} — recuo quebrado'); continue
        tot+=1+_um_por_item(item[ks[0]].get('Children'), nome_arq)
    return tot
for t in TELAS:
    nome=os.path.basename(t); d=yaml.safe_load(open(t,encoding='utf-8'))
    tela=list(d['Screens'])[0]
    na_arvore=_um_por_item(d['Screens'][tela].get('Children'), nome)
    no_texto=len(re.findall(r'^\s*- [A-Za-z]\w*:\s*$', open(t,encoding='utf-8').read(), re.M))
    if na_arvore != no_texto:
        erros.append(f'{nome}: {no_texto} controles no texto, {na_arvore} na árvore — recuo desanexou subárvore')


# 16 cor: hex literal em tela é regressão — toda cor vem de token hx*/thm*
for t in TELAS:
    txt=open(t,encoding='utf-8').read()
    for m in sorted(set(re.findall(r'#[0-9A-Fa-f]{6}', txt))):
        erros.append(f'{os.path.basename(t)}: cor literal {m} — crie/reuse um token hx*')


# 17 escopo do Módulo 1: campo-espelho de módulo inexistente não pode aparecer em tela
ESPELHOS_FUTUROS = ('doc_situacao','doc_proximo_vencimento','conforme_lado_ar',
                    'credencial_validade','manut_proxima_data','id_fornecedor')
for t in TELAS:
    txt=open(t,encoding='utf-8').read()
    for campo in ESPELHOS_FUTUROS:
        if re.search(rf'\b{campo}\b', txt):
            erros.append(f'{os.path.basename(t)}: usa {campo} — campo do módulo que ainda não existe')

# 18 cache: as projeções de colFrota têm que ter esquema idêntico (senão Collect quebra)
_esquemas=set()
for t in TELAS:
    for m in re.finditer(r'\{\s*\n(\s*ID: _r\.ID,.*?)\n\s*\}', open(t,encoding='utf-8').read(), re.S):
        _esquemas.add(tuple(re.findall(r'(\w+): _r\.', m.group(1))))
if len(_esquemas) > 1:
    erros.append(f'projeções de colFrota com esquemas diferentes ({len(_esquemas)} variantes) — Collect vai falhar')


# 19 trilho: as três telas internas têm que ter o mesmo bloco de navegação
def _tri(arq, suf):
    d=yaml.safe_load(open(os.path.join(BASE,'Frotas',arq),encoding='utf-8'))
    tela=list(d['Screens'])[0]
    def sub(no,alvo):
        for it in (no or []):
            n=list(it)[0]
            if n==alvo: return it[n]
            r=sub(it[n].get('Children'),alvo)
            if r: return r
    raiz=sub(d['Screens'][tela].get('Children'),'cntMenu'+suf)
    if not raiz: return None
    out={}
    def anda(nos,path=''):
        for it in (nos or []):
            n=list(it)[0]; c=it[n]; k=(path+'/'+n).replace(suf,'')
            out[k]=dict(c.get('Properties') or {}); anda(c.get('Children'),k)
    anda(raiz.get('Children')); out['/']=dict(raiz.get('Properties') or {})
    return out
_molde=_tri('scrFrotaPainel.pa.yaml','Pnl')
for _arq,_suf in (('scrFrotaLista.pa.yaml','Lst'),('scrFrotaForm.pa.yaml','Frm')):
    _t=_tri(_arq,_suf)
    if _molde and _t:
        for _k in sorted(set(_molde)|set(_t)):
            _a,_b=_molde.get(_k),_t.get(_k)
            if _a is None or _b is None:
                erros.append(f'{_arq}: trilho difere do painel — {_k} só em uma tela'); continue
            for _p in sorted(set(_a)|set(_b)):
                if _a.get(_p)!=_b.get(_p) and not ('btnMenu' in _k and _p in ('Appearance','BasePaletteColor')):
                    erros.append(f'{_arq}: trilho difere do painel em {_k}.{_p}')


# 20 justaposição: ')' seguido de função sem operador é sintaxe inválida em Power Fx
OPERADORES = {'And','Or','Not','in','exactin','As'}
for t in TELAS:
    d=yaml.safe_load(open(t,encoding='utf-8'))
    tela=list(d['Screens'])[0]
    def _just(no, nome_arq, caminho=''):
        for item in (no or []):
            n=list(item)[0]; c=item[n]
            for prop, val in (c.get('Properties') or {}).items():
                if isinstance(val, str):
                    limpo=re.sub(r'"[^"]*"', '""', val)
                    for m in re.finditer(r'\)\s+([A-Za-z_]\w*)\s*\(', limpo):
                        if m.group(1) not in OPERADORES:
                            erros.append(f'{nome_arq}: {n}.{prop} — ")" seguido de {m.group(1)}( sem vírgula/operador')
            _just(c.get('Children'), nome_arq, caminho+'/'+n)
    _just(d['Screens'][tela].get('Children'), os.path.basename(t))

print('CONTROLES:',sum(nomes.values()),'| TIPOS:',len({c for c in PROV}))
if erros:
    print('\n'.join(f'ERRO  {e}' for e in erros)); sys.exit(1)
print('OK — todas as validações passaram')
