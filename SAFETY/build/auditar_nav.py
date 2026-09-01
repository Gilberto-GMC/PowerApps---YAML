# -*- coding: utf-8 -*-
"""Audita TODA navegação das telas entregues.

Duas regras:
 1. Navigate nunca aponta para um CONTROLE (nome de container). Bug herdado do
    export: o "voltar" dos Detalhes de Derramamento fazia
    Navigate(ScreenContainerDerramementoFluido) — container, não tela. Nunca
    funcionou, e o Studio não acusa.
 2. Nas 7 telas consolidadas não sobra Navigate interno: alternar
    lista/form/detalhe é Set(var_vista, ...). Navigate só para SAIR do módulo.

Comentário Power Fx (// e /* */) é ignorado — é onde mora código morto.
"""
import re, sys, os, glob
sys.path.insert(0, 'build')
from fx import find_call, split_args
from valida import carregar, nomes_de
from modulos import MODULOS


def sem_comentarios(fx):
    fx = re.sub(r'/\*.*?\*/', ' ', fx, flags=re.S)
    return re.sub(r'//[^\n]*', ' ', fx)


telas = set()
for f in glob.glob('out/*.pa.yaml'):
    d = carregar(f)
    if isinstance(d, dict) and 'Screens' in d:
        telas |= set(d['Screens'])
for p in glob.glob('msapp/Src/*.pa.yaml'):
    telas.add(os.path.basename(p)[:-len('.pa.yaml')])

consolidadas = {m['nova']: m for m in MODULOS}
problemas = []

for f in sorted(glob.glob('out/*.pa.yaml')):
    d = carregar(f)
    if not (isinstance(d, dict) and 'Screens' in d):
        continue
    tela = list(d['Screens'])[0]
    ctrls = []; nomes_de(d, ctrls); ctrls = set(ctrls)
    txt = sem_comentarios(
        '\n'.join(l for l in open(f, encoding='utf-8') if not l.lstrip().startswith('#')))
    pos = 0
    while True:
        r = find_call(txt, 'Navigate', pos)
        if not r:
            break
        a, b, c = r
        alvo = split_args(txt[b:c - 1])[0].strip()
        linha = txt[:a].count('\n') + 1
        pos = c
        if alvo.startswith('var'):          # Navigate(var_navigateSucess, ...)
            continue
        if alvo in ctrls and alvo not in telas:
            problemas.append((tela, linha, alvo, 'aponta para um CONTROLE, não uma tela'))
        elif alvo not in telas:
            problemas.append((tela, linha, alvo, 'tela inexistente'))
        elif tela in consolidadas:
            m = consolidadas[tela]
            if alvo in (m['lista'], m['forms'], m['det'], tela):
                problemas.append((tela, linha, alvo,
                                  'navegação interna sobrando — deveria ser Set(var_vista, ...)'))

if problemas:
    for t, l, alvo, tipo in problemas:
        print(f"   ✗ {t}:{l}  Navigate({alvo}) — {tipo}")
    sys.exit(1)
print(f"   ✓ navegação conferida em {len(glob.glob('out/*.pa.yaml'))} telas")
