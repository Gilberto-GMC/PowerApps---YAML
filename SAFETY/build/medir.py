# -*- coding: utf-8 -*-
"""Mede a geometria dos formulários: containers ManualLayout e grupos de campos."""
import sys, re, glob, os
sys.path.insert(0, 'build')
from valida import carregar
from modulos import MODULOS

def num(v):
    if v is None: return None
    s = str(v).lstrip('=').strip()
    try: return float(s)
    except: return s

def anda(node, caminho, prof, saida):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and len(item) == 1:
                nome = list(item)[0]; c = item[nome]
                if isinstance(c, dict) and 'Control' in c:
                    p = c.get('Properties', {}) or {}
                    saida.append(dict(nome=nome, ctrl=c['Control'], var=c.get('Variant',''),
                                      grupo=c.get('Group'), prof=prof, pai=caminho,
                                      x=num(p.get('X')), y=num(p.get('Y')),
                                      w=num(p.get('Width')), h=num(p.get('Height'))))
                    anda(c.get('Children', []), nome, prof+1, saida)
    return saida

m = [x for x in MODULOS if x['key'] == 'ColVei'][0]
d = carregar(f"out/{m['nova']}.pa.yaml")
topo = d['Screens'][m['nova']]['Children']
form = [t for t in topo if 'form' in str(list(t.values())[0].get('Properties',{}).get('Visible',''))][0]
nome = list(form)[0]
print(f"container do formulário: {nome}")
itens = anda(form[nome].get('Children', []), nome, 1, [])
for i in itens:
    if i['ctrl'].startswith('GroupContainer'):
        print(f"{'  '*i['prof']}{i['nome']:28s} {i['var']:12s} X={i['x']} Y={i['y']} W={i['w']} H={i['h']}")
print("\n=== grupos de campos (Group:) ===")
import collections
g = collections.defaultdict(list)
for i in itens:
    if i['grupo']: g[i['grupo']].append(i)
for nome_g, membros in g.items():
    xs = [x['x'] for x in membros if isinstance(x['x'], float)]
    ys = [x['y'] for x in membros if isinstance(x['y'], float)]
    print(f"  {nome_g:20s} n={len(membros):2d} pai={membros[0]['pai']:22s} x=[{min(xs) if xs else '?'},{max(xs) if xs else '?'}] y=[{min(ys) if ys else '?'},{max(ys) if ys else '?'}]")
