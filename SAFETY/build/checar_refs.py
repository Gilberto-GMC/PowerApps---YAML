# -*- coding: utf-8 -*-
"""Toda tela referenciada em Navigate/col_NavTelas tem que existir no app final."""
import re, glob, sys, os
sys.path.insert(0, 'build')
from valida import carregar

# telas que vão existir depois de aplicar a entrega
entregues = set()
for f in glob.glob('out/*.pa.yaml'):
    d = carregar(f)
    if isinstance(d, dict) and 'Screens' in d:
        entregues |= set(d['Screens'])

# telas do app original que continuam existindo (não foram consolidadas)
consolidadas = set()
from modulos import MODULOS
for m in MODULOS:
    consolidadas |= {m['lista'], m['forms'], m['det']}
originais = {os.path.basename(p)[:-len('.pa.yaml')] for p in glob.glob('msapp/Src/*.pa.yaml')}
originais -= {'App', '_EditorState'}
existentes = (originais - consolidadas) | entregues

print(f"{len(existentes)} telas existirão no app\n")
faltando = {}
for f in sorted(glob.glob('out/*.pa.yaml')):
    txt = '\n'.join(l for l in open(f, encoding='utf-8') if not l.lstrip().startswith('#'))
    refs = set(re.findall(r'(?<![A-Za-z0-9_.\'])(Screen[A-Za-z0-9_]*|frmHome)(?![A-Za-z0-9_])', txt))
    # nomes de controle da própria tela podem começar com "Screen" (ex.: ScreenContainer...)
    ruins = {r for r in refs if r not in existentes and not r.startswith('ScreenContainer')}
    ruins = {r for r in ruins if r in {x for x in refs} and re.search(
        r'(Navigate\(\s*' + r + r'\b|TelaListar:\s*' + r + r'\b|var_navigate\w*:\s*' + r + r'\b)', txt)}
    if ruins:
        faltando[os.path.basename(f)] = sorted(ruins)

if faltando:
    for arq, r in faltando.items():
        print(f"✗ {arq}: referencia tela inexistente -> {', '.join(r)}")
    sys.exit(1)
print("✓ nenhuma referência a tela inexistente")
