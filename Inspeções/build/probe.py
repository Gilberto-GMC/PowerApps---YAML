# -*- coding: utf-8 -*-
"""Sonda de leitura: imprime o bloco de uma propriedade de um controle.

Uso: python build/probe.py tela controle prop [tela controle prop ...]
     python build/probe.py --out tela controle prop   (lê de out/ em vez de msapp/Src)
"""
import sys, os, re, glob
sys.path.insert(0, os.path.dirname(__file__))
from pautil import find_ctrl, prop_block, block_end, ind


def bloco(path, controle, prop):
    linhas = open(path, encoding='utf-8').read().split('\n')
    i = find_ctrl(linhas, controle)
    if i < 0:
        return None, f"controle {controle} não encontrado"
    pi, pe = prop_block(linhas, i)
    if pi < 0:
        return None, "sem Properties"
    pind = ind(linhas[pi]) + 2
    for k in range(pi + 1, pe):
        if ind(linhas[k]) == pind and re.match(r'^\s*' + re.escape(prop) + r':', linhas[k]):
            ke = block_end(linhas, k)
            return (k + 1, '\n'.join(linhas[k:ke])), None
    return None, f"propriedade {prop} não encontrada"


if __name__ == '__main__':
    args = sys.argv[1:]
    pasta = 'msapp/Src'
    if args and args[0] == '--out':
        pasta = 'out'; args = args[1:]
    for t, c, p in zip(args[0::3], args[1::3], args[2::3]):
        path = f"{pasta}/{t}.pa.yaml"
        if pasta == 'out':
            cands = glob.glob(f"out/*_{t}.pa.yaml")
            path = cands[0] if cands else path
        r, err = bloco(path, c, p)
        print(f"═══ {t} › {c}.{p}" + (f"  (linha {r[0]})" if r else f"  ✗ {err}"))
        if r:
            print(r[1])
