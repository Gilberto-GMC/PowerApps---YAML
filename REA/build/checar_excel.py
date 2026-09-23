# -*- coding: utf-8 -*-
"""Consultas a fontes do Excel Online: uma condição por Filter/LookUp/CountIf/RemoveIf.

O conector Excel Online (Business) delega só UMA comparação por consulta ('eq',
'ne', 'contém', 'startswith', 'endswith'). Duas condições (vírgula, And, &&, Or, ||)
falham em tempo de execução com "Cláusula de filtro inválida: operação sem
suporte", e o Studio não acusa nada ao colar. Lição de 2026-09-18 (ScreenAPH,
fonte Cessionarios).

As fontes Excel são lidas de msapp/References/DataSources.json (ApiId
shared_excelonlinebusiness), não de uma lista fixa.

Uso (a partir de REA/):  python build/checar_excel.py [--baseline] [--dir PASTA]
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join('..', 'Inspeções', 'build'))
from checar_sintaxe import formulas_de  # noqa: E402
from checar_cross_screen import mascarar  # noqa: E402
from fx import split_args  # noqa: E402


def fontes_excel():
    d = json.load(open('msapp/References/DataSources.json', encoding='utf-8-sig'))
    return sorted(ds['Name'] for ds in d['DataSources']
                  if 'excelonlinebusiness' in (ds.get('ApiId') or '').lower())


def argumentos(m, abre):
    """texto entre o '(' na posição abre e o ')' que fecha"""
    prof = 0
    for i in range(abre, len(m)):
        if m[i] == '(':
            prof += 1
        elif m[i] == ')':
            prof -= 1
            if prof == 0:
                return m[abre + 1:i]
    return None


def main():
    pasta = 'msapp/Src' if '--baseline' in sys.argv else 'out'
    if '--dir' in sys.argv:
        pasta = sys.argv[sys.argv.index('--dir') + 1]
    excel = fontes_excel()
    if not excel:
        print('   (nenhuma fonte Excel no app)')
        return
    pat = re.compile(r'\b(Filter|LookUp|CountIf|RemoveIf)\(\s*(' + '|'.join(re.escape(n) for n in excel) + r')\s*,')
    problemas, consultas = [], 0
    for f in sorted(glob.glob(os.path.join(pasta, '*.pa.yaml'))):
        for linha, prop, fx, _ in formulas_de(f):
            corpo = fx[1:] if fx.lstrip().startswith('=') else fx
            m = mascarar(corpo)
            for mm in pat.finditer(m):
                args = argumentos(m, m.index('(', mm.start()))
                if args is None:
                    continue
                consultas += 1
                partes = split_args(args)
                conds = partes[1:2] if mm.group(1) == 'LookUp' else partes[1:]
                if len(conds) > 1 or any(re.search(r'\bAnd\b|\bOr\b|&&|\|\|', c) for c in conds):
                    problemas.append(f"{os.path.basename(f)}:{linha} {prop}: {mm.group(1)}({mm.group(2)}, ...) "
                                     f"com {len(conds)} condição(ões) — o Excel Online só aceita uma")
    for p in problemas:
        print(('   ! ' if '--baseline' in sys.argv else '   ✗ ') + p)
    print(f"   {consultas} consultas a {', '.join(excel)} em {pasta}, {len(problemas)} com mais de uma condição")
    if problemas and '--baseline' not in sys.argv:
        sys.exit(1)
    if not problemas:
        print('   ✓ uma condição por consulta ao Excel')


if __name__ == '__main__':
    main()
