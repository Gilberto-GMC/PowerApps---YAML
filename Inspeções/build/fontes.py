# -*- coding: utf-8 -*-
"""Nomes das fontes de dados SharePoint do app (lidos de DataSources.json) e
utilitários para reconhecer a fonte de base de uma expressão Power Fx."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from fx import find_call, split_args

_DS = None


def fontes_sp():
    """set de nomes de fontes SharePoint conforme aparecem em Power Fx (sem aspas)."""
    global _DS
    if _DS is None:
        d = json.load(open('msapp/References/DataSources.json', encoding='utf-8'))
        _DS = {s['Name'] for s in d['DataSources'] if s.get('Type') == 'ConnectedDataSourceInfo'}
    return _DS


def fluxos():
    d = json.load(open('msapp/References/DataSources.json', encoding='utf-8'))
    return {s['Name'] for s in d['DataSources']
            if s.get('Type') == 'ServiceInfo' and 'logicflows' in (s.get('ApiId') or '')}


def limpar_ident(s):
    s = s.strip()
    if s.startswith('[@') and s.endswith(']'):
        s = s[2:-1]
    return s.strip("'\"").strip()


ENVOLTORIOS = ('Filter', 'Sort', 'SortByColumns', 'Search', 'AddColumns', 'ShowColumns',
               'DropColumns', 'RenameColumns', 'FirstN', 'LastN', 'Distinct', 'GroupBy',
               'Ungroup', 'First', 'Last', 'LookUp', 'CountRows', 'CountIf', 'Concat', 'ForAll',
               'Sum', 'Max', 'Min', 'Average', 'Table', 'If', 'Switch', 'With')


def fonte_base(expr, profundidade=0):
    """Desce pelo 1º argumento das funções de tabela até um identificador.
    Devolve o nome (sem aspas) ou None."""
    e = expr.strip()
    if profundidade > 12 or not e:
        return None
    m = re.match(r"^([A-Za-z_][\w]*)\s*\(", e)
    if m and m.group(1) in ENVOLTORIOS:
        r = find_call(e, m.group(1), 0)
        if not r:
            return None
        a, b, c = r
        args = split_args(e[b:c - 1])
        if m.group(1) in ('If', 'Switch'):
            # ramos: 2º argumento (e seguintes pares) — devolve o 1º que for fonte
            for arg in args[1:]:
                f = fonte_base(arg, profundidade + 1)
                if f in fontes_sp():
                    return f
            return None
        if m.group(1) == 'With':
            return fonte_base(args[-1], profundidade + 1) if len(args) > 1 else None
        return fonte_base(args[0], profundidade + 1) if args else None
    m = re.match(r"^('[^']+'|\[@'[^']+'\]|\[@[A-Za-z_]\w*\]|[A-Za-z_][\w]*)", e)
    if m:
        return limpar_ident(m.group(1))
    return None


def eh_sp(expr):
    f = fonte_base(expr)
    return f in fontes_sp(), f


def lote_ativo():
    """lote da entrega em curso (variável LOTE exportada por entregar.sh); padrão ABCD"""
    return (os.environ.get('LOTE') or 'ABCD').upper()


def filtrar_allow(entradas):
    """mantém só as entradas de allowlist válidas para o lote em curso:
    'ate': 'B' -> vale até o lote B (some quando C/D entram);
    'desde': 'C' -> só vale quando o lote C entrou."""
    lote = lote_ativo()
    ultimo = lote[-1]
    out = []
    for e in entradas:
        if 'ate' in e and ultimo > e['ate']:
            continue
        if 'desde' in e and ultimo < e['desde']:
            continue
        out.append(e)
    return out
