# -*- coding: utf-8 -*-
"""Navigate nunca aponta para um CONTROLE (nome de container) nem para tela
inexistente. Bug herdado de outro app: Navigate(ScreenContainerX) nunca funcionou
e o Studio não acusa. Comentário Power Fx é ignorado (é onde mora código morto)."""
import re, sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
from fx import find_call, split_args
from valida import carregar, nomes_de
from checar_cross_screen import mascarar, texto_sem_cabecalho
from checar_refs import TELAS_REMOVIDAS

pasta = 'msapp/Src' if '--baseline' in sys.argv else 'out'
telas = {os.path.basename(p)[:-len('.pa.yaml')] for p in glob.glob('msapp/Src/*.pa.yaml')} - {'App', '_EditorState'}
if pasta == 'out':
    telas -= TELAS_REMOVIDAS
for f in glob.glob('out/*.pa.yaml'):
    d = carregar(f)
    if isinstance(d, dict) and 'Screens' in d:
        telas |= set(d['Screens'])

problemas = []
n = 0
for f in sorted(glob.glob(f'{pasta}/*.pa.yaml')):
    d = carregar(f)
    if not (isinstance(d, dict) and 'Screens' in d):
        continue
    tela = list(d['Screens'])[0]
    ctrls = []; nomes_de(d, ctrls); ctrls = set(ctrls)
    txt = mascarar(texto_sem_cabecalho(f))
    pos = 0
    while True:
        r = find_call(txt, 'Navigate', pos)
        if not r:
            break
        a, b, c = r
        alvo = split_args(txt[b:c - 1])[0].strip()
        linha = txt[:a].count('\n') + 1
        pos = c; n += 1
        if alvo.startswith('var') or alvo.startswith('HeaderTitle') or '.' in alvo:
            continue
        if alvo in ctrls and alvo not in telas:
            problemas.append((tela, linha, alvo, 'aponta para um CONTROLE, não uma tela'))
        elif alvo not in telas:
            problemas.append((tela, linha, alvo, 'tela inexistente'))
if problemas:
    for t, l, alvo, tipo in problemas:
        print(f"   ✗ {t}:{l}  Navigate({alvo}) — {tipo}")
    sys.exit(1)
print(f"   ✓ {n} Navigate conferidos em {len(glob.glob(f'{pasta}/*.pa.yaml'))} telas")
