# -*- coding: utf-8 -*-
"""Consulta ao SharePoint dentro de template de galeria = 1 requisição por linha.

Procura, nos filhos de cada Gallery, propriedades que chamem LookUp/Filter/
First/CountRows/CountIf/Distinct/Search/Sum/Max sobre uma fonte SharePoint.
Allowlist justificada em build/allow_por_linha.json:
    [{"tela": "frmHomePista", "controle": "Icon28_209", "prop": "DisplayMode", "motivo": "..."}]

Uso: python build/checar_por_linha.py [--baseline] [--dir PASTA]
"""
import sys, os, re, glob, json
sys.path.insert(0, os.path.dirname(__file__))
from valida import carregar
from fx import find_call, split_args
from fontes import fontes_sp, fonte_base
from checar_cross_screen import mascarar

FUNCS = ('LookUp', 'Filter', 'First', 'Last', 'CountRows', 'CountIf', 'Distinct', 'Search', 'Sum', 'Max', 'Min', 'Sort', 'SortByColumns')


def consultas_sp(fx):
    """lista de (função, fonte) para chamadas cuja fonte de base é SharePoint"""
    achados = []
    m = mascarar(fx)
    for fn in FUNCS:
        pos = 0
        while True:
            r = find_call(m, fn, pos)
            if not r:
                break
            a, b, c = r
            args = split_args(fx[b:c - 1])
            pos = c
            if not args:
                continue
            f = fonte_base(args[0])
            if f in fontes_sp():
                achados.append((fn, f))
    return achados


def galerias(node, caminho, dentro, saida, tela):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and len(item) == 1:
                nome = list(item)[0]; corpo = item[nome]
                if isinstance(corpo, dict) and 'Control' in corpo:
                    eh_gal = str(corpo.get('Control', '')).startswith('Gallery@')
                    if dentro:
                        for p, v in (corpo.get('Properties') or {}).items():
                            # propriedades de comportamento (OnSelect...) rodam no clique, não por linha
                            if p.startswith('On'):
                                continue
                            if isinstance(v, str) and v.startswith('='):
                                for fn, f in consultas_sp(v[1:]):
                                    saida.append((tela, dentro, nome, p, fn, f))
                    galerias(corpo.get('Children'), caminho + (nome,), dentro or (nome if eh_gal else None), saida, tela)
                else:
                    galerias(corpo, caminho, dentro, saida, tela)
            else:
                galerias(item, caminho, dentro, saida, tela)


def main():
    baseline = '--baseline' in sys.argv
    pasta = 'msapp/Src' if baseline else 'out'
    if '--dir' in sys.argv:
        pasta = sys.argv[sys.argv.index('--dir') + 1]
    allow = []
    if os.path.exists('build/allow_por_linha.json'):
        from fontes import filtrar_allow
        allow = filtrar_allow(json.load(open('build/allow_por_linha.json', encoding='utf-8')))
    allow_k = {(a['tela'], a['controle'], a['prop']) for a in allow}
    achados = []
    for f in sorted(glob.glob(os.path.join(pasta, '*.pa.yaml'))):
        d = carregar(f)
        if not (isinstance(d, dict) and 'Screens' in d):
            continue
        tela = list(d['Screens'])[0]
        galerias((d['Screens'][tela] or {}).get('Children'), (), None, achados, tela)
    usados = set(); problemas = []
    for tela, gal, ctrl, prop, fn, fonte in achados:
        if (tela, ctrl, prop) in allow_k:
            usados.add((tela, ctrl, prop)); continue
        problemas.append((tela, gal, ctrl, prop, fn, fonte))
    for tela, gal, ctrl, prop, fn, fonte in problemas:
        print(f"   {'!' if baseline else '✗'} {tela}: {gal} > {ctrl}.{prop}: {fn}({fonte}…) por linha")
    for k in sorted(allow_k - usados):
        problemas.append(k)
        print(f"   ✗ allowlist declarada que não ocorre: {k}")
    print(f"   total: {len(problemas)} consultas por linha, {len(usados)} permitidas com justificativa" + (' (baseline)' if baseline else ''))
    if problemas and not baseline:
        sys.exit(1)
    if not problemas:
        print("   ✓ nenhuma consulta SharePoint por linha de galeria")


if __name__ == '__main__':
    main()
