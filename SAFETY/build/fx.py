"""Cirurgia em fórmulas Power Fx dentro de blocos YAML, preservando indentação."""
import re

def split_args(s):
    """divide argumentos de topo de uma chamada (string interna aos parênteses)"""
    out, depth, cur, q = [], 0, [], None
    i = 0
    while i < len(s):
        c = s[i]
        if q:
            cur.append(c)
            if c == q:
                q = None
            i += 1
            continue
        if c in '"\'':
            q = c
            cur.append(c)
            i += 1
            continue
        if c == '/' and i + 1 < len(s) and s[i + 1] == '/':
            j = s.find('\n', i)
            j = len(s) if j < 0 else j
            cur.append(s[i:j])
            i = j
            continue
        if c in '([{':
            depth += 1
        elif c in ')]}':
            depth -= 1
        if c == ',' and depth == 0:
            out.append(''.join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    out.append(''.join(cur))
    return [a.strip() for a in out]

def find_call(text, name, start=0):
    """acha 'name(' fora de string/comentário; devolve (ini, ini_args, fim_call)"""
    i = start
    n = len(text)
    while i < n:
        j = text.find(name + '(', i)
        if j < 0:
            return None
        # não pode ser sufixo de identificador
        if j > 0 and (text[j - 1].isalnum() or text[j - 1] in '_.'):
            i = j + 1
            continue
        # ignora dentro de comentário de linha
        ls = text.rfind('\n', 0, j) + 1
        line_before = text[ls:j]
        if '//' in line_before:
            i = j + 1
            continue
        k = j + len(name)
        depth, q = 0, None
        while k < n:
            c = text[k]
            if q:
                if c == q:
                    q = None
                k += 1
                continue
            if c in '"\'':
                q = c
                k += 1
                continue
            if c == '/' and k + 1 < n and text[k + 1] == '/':
                nl = text.find('\n', k)
                k = len(text) if nl < 0 else nl
                continue
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return (j, j + len(name) + 1, k + 1)
            k += 1
        return None
    return None

def replace_calls(text, name, fn):
    """fn(args:list[str], raw:str, indent:int) -> str|None (None = não mexer)"""
    out = text
    pos = 0
    while True:
        r = find_call(out, name, pos)
        if not r:
            break
        a, b, c = r
        raw = out[b:c - 1]
        ls = out.rfind('\n', 0, a) + 1
        indent = len(out[ls:a]) - len(out[ls:a].lstrip())
        # indentação real = coluna onde a chamada começa
        col = a - ls
        rep = fn(split_args(raw), raw, col)
        if rep is None:
            pos = c
            continue
        out = out[:a] + rep + out[c:]
        pos = a + len(rep)
    return out

def indent_lines(txt, col, first=False):
    ls = txt.split('\n')
    return ('\n'.join([(ls[0] if not first else ' ' * col + ls[0])] +
                      [(' ' * col + l if l.strip() else l) for l in ls[1:]]))
