# -*- coding: utf-8 -*-
"""Compara dois AppCheckerResult.sarif (antes/depois) nas regras app-*.

Uso: python build/comparar_sarif.py [depois.sarif]   (antes = msapp/AppCheckerResult.sarif)
"""
import sys, json, collections

ANTES = 'msapp/AppCheckerResult.sarif'


def contar(path):
    d = json.load(open(path, encoding='utf-8'))
    c = collections.Counter()
    for run in d.get('runs', []):
        for r in run.get('results', []):
            rid = r.get('ruleId', '?')
            if rid.startswith('app-'):
                c[rid] += 1
    return c


def main():
    a = contar(ANTES)
    b = contar(sys.argv[1]) if len(sys.argv) > 1 else None
    regras = sorted(set(a) | set(b or {}))
    print(f"{'regra':52} {'antes':>6} {'depois':>7} {'delta':>6}")
    for r in regras:
        x = a.get(r, 0); y = b.get(r, 0) if b is not None else None
        print(f"{r:52} {x:6d} {'' if y is None else y:>7} {'' if y is None else y - x:>6}")
    print(f"{'TOTAL app-*':52} {sum(a.values()):6d} {'' if b is None else sum(b.values()):>7}")


if __name__ == '__main__':
    main()
