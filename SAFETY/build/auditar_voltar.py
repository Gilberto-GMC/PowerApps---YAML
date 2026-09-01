# -*- coding: utf-8 -*-
"""Lista todo botão de voltar/cancelar das telas consolidadas, por visão."""
import sys, os, re
sys.path.insert(0, 'build')
from valida import carregar
from modulos import MODULOS

def varre(node, vista, achados, dentro_gal=False):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and len(item) == 1:
                nome = list(item)[0]
                corpo = item[nome]
                if isinstance(corpo, dict) and 'Control' in corpo:
                    p = corpo.get('Properties', {}) or {}
                    icone = str(p.get('Icon', ''))
                    txt = str(p.get('Text', ''))
                    sel = str(p.get('OnSelect', ''))
                    ehVoltar = ('BackArrow' in icone or 'DismissCircle' in icone
                                or 'Cancelar' in txt or 'Voltar' in txt)
                    if ehVoltar and not dentro_gal:
                        achados.append((vista, nome, icone or txt, ' '.join(sel.split())))
                    g = dentro_gal or corpo.get('Control', '').startswith('Gallery')
                    varre(corpo.get('Children', []), vista, achados, g)
    return achados

for m in MODULOS:
    d = carregar(f"out/{m['nova']}.pa.yaml")
    topo = d['Screens'][m['nova']]['Children']
    print(f"\n╔═ {m['nova']}")
    for filho in topo:
        nome = list(filho)[0]
        vis = str(filho[nome].get('Properties', {}).get('Visible', ''))
        vista = re.search(r'"(\w+)"', vis)
        vista = vista.group(1) if vista else '?'
        achados = varre(filho[nome].get('Children', []), vista, [])
        for v, ctrl, marca, acao in achados:
            print(f"║ [{v:8s}] {ctrl:22s} {marca[:28]:28s} -> {acao[:110]}")
