# -*- coding: utf-8 -*-
"""Padrões que quebram a delegação no conector SharePoint (teto silencioso de
500/2000 linhas). Regras das lições 2026-08-25/31:

 1. Search(<fonte SP ou envoltório dela>)            -> Search não delega
 2. IsBlank(x) || ... dentro de Filter(<SP>)          -> IsBlank não delega
 3. Year(/Month(/Day( sobre coluna dentro de Filter(<SP>)
 4. Distinct(<SP>), CountRows(<SP ou Filter(SP)>), CountIf(<SP>)
 5. `in` dentro de Filter(<SP>)
 6. Items de galeria sobre <SP> sem FirstN (sem teto)
 7. Max(<SP>, ...) / Sum / Min / Average sobre SP

Allowlist justificada em build/allow_delegacao.json:
    [{"tela": "frmHomePista", "controle": "GalleryX", "prop": "Items", "regra": 1, "motivo": "..."}]

Uso: python build/checar_delegacao.py [--baseline] [--dir PASTA]
"""
import sys, os, re, glob, json
sys.path.insert(0, os.path.dirname(__file__))
from valida import carregar
from fx import find_call, split_args
from fontes import fontes_sp, fonte_base
from checar_cross_screen import mascarar


def regras(fx, prop, eh_galeria):
    out = []
    m = mascarar(fx)
    # 1, 4, 7: funções não delegáveis sobre SP
    for fn, regra in (('Search', 1), ('Distinct', 4), ('CountRows', 4), ('CountIf', 4),
                      ('Max', 7), ('Sum', 7), ('Min', 7), ('Average', 7)):
        pos = 0
        while True:
            r = find_call(m, fn, pos)
            if not r:
                break
            a, b, c = r
            args = split_args(fx[b:c - 1]); pos = c
            if args and fonte_base(args[0]) in fontes_sp():
                out.append((regra, f"{fn}({fonte_base(args[0])}…)"))
    # 2, 3, 5: dentro de Filter(SP, ...)
    pos = 0
    while True:
        r = find_call(m, 'Filter', pos)
        if not r:
            break
        a, b, c = r
        args = split_args(fx[b:c - 1]); pos = c
        if not args or fonte_base(args[0]) not in fontes_sp():
            continue
        corpo = mascarar(','.join(args[1:]))
        if re.search(r'IsBlank\([^)]*\)\s*(\|\||Or\b)', corpo):
            out.append((2, f"IsBlank(x) || … em Filter({fonte_base(args[0])})"))
        # Year(coluna) não delega; Year(Today()) é escalar calculado no cliente
        if re.search(r'\b(Year|Month|Day|Weekday)\(\s*[A-Za-z_]\w*\s*\)', corpo):
            out.append((3, f"Year/Month(coluna) em Filter({fonte_base(args[0])})"))
        if re.search(r'\s+in\s+', corpo):
            out.append((5, f"`in` em Filter({fonte_base(args[0])})"))
    # 6: Items de galeria sobre SP sem FirstN
    if eh_galeria and prop == 'Items':
        f = fonte_base(fx)
        if f in fontes_sp() and not re.search(r'\bFirstN\(', m):
            out.append((6, f"Items sobre {f} sem FirstN"))
    return out


def varrer(node, saida, tela):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and len(item) == 1:
                nome = list(item)[0]; corpo = item[nome]
                if isinstance(corpo, dict) and 'Control' in corpo:
                    eh_gal = str(corpo.get('Control', '')).startswith('Gallery@')
                    for p, v in (corpo.get('Properties') or {}).items():
                        if isinstance(v, str) and v.startswith('='):
                            for regra, desc in regras(v[1:], p, eh_gal):
                                saida.append((tela, nome, p, regra, desc))
                    varrer(corpo.get('Children'), saida, tela)
                else:
                    varrer(corpo, saida, tela)
            else:
                varrer(item, saida, tela)


def main():
    baseline = '--baseline' in sys.argv
    pasta = 'msapp/Src' if baseline else 'out'
    if '--dir' in sys.argv:
        pasta = sys.argv[sys.argv.index('--dir') + 1]
    from fontes import filtrar_allow
    allow = filtrar_allow(json.load(open('build/allow_delegacao.json', encoding='utf-8'))) if os.path.exists('build/allow_delegacao.json') else []
    allow_k = {(a['tela'], a['controle'], a['prop'], a['regra']) for a in allow}
    achados = []
    for f in sorted(glob.glob(os.path.join(pasta, '*.pa.yaml'))):
        d = carregar(f)
        if not (isinstance(d, dict) and 'Screens' in d):
            continue
        tela = list(d['Screens'])[0]
        corpo = d['Screens'][tela] or {}
        for p, v in (corpo.get('Properties') or {}).items():
            if isinstance(v, str) and v.startswith('='):
                for regra, desc in regras(v[1:], p, False):
                    achados.append((tela, '<tela>', p, regra, desc))
        varrer(corpo.get('Children'), achados, tela)
        if tela == 'App' or f.endswith('App.pa.yaml'):
            pass
    # App.pa.yaml (OnStart/Formulas)
    app = os.path.join(pasta, '01_App.pa.yaml') if not baseline else 'msapp/Src/App.pa.yaml'
    if os.path.exists(app):
        d = carregar(app)
        for p, v in ((d.get('App') or {}).get('Properties') or {}).items():
            if isinstance(v, str) and v.startswith('='):
                for regra, desc in regras(v[1:], p, False):
                    achados.append(('App', 'App', p, regra, desc))
    usados = set(); problemas = []
    for tela, ctrl, prop, regra, desc in achados:
        k = (tela, ctrl, prop, regra)
        if k in allow_k:
            usados.add(k); continue
        problemas.append((tela, ctrl, prop, regra, desc))
    for tela, ctrl, prop, regra, desc in problemas:
        print(f"   {'!' if baseline else '✗'} {tela}: {ctrl}.{prop} [regra {regra}] {desc}")
    for k in sorted(allow_k - usados):
        problemas.append(k); print(f"   ✗ allowlist declarada que não ocorre: {k}")
    print(f"   total: {len(problemas)} padrões não delegáveis, {len(usados)} permitidos" + (' (baseline)' if baseline else ''))
    if problemas and not baseline:
        sys.exit(1)
    if not problemas:
        print("   ✓ delegação ok")


if __name__ == '__main__':
    main()
