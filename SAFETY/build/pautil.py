"""Utilitários de manipulação de .pa.yaml preservando formatação original."""
import re

HDR = """# ************************************************************************************************
# Warning: YAML source code for Canvas Apps should only be used to review changes made within Power Apps Studio and for minor edits (Preview).
# Use the maker portal to create and edit your Power Apps.
# 
# The schema file for Canvas Apps is available at https://go.microsoft.com/fwlink/?linkid=2304907
# 
# For more information, visit https://go.microsoft.com/fwlink/?linkid=2292623
# ************************************************************************************************
"""

def ind(line):
    return len(line) - len(line.lstrip())

def block_end(lines, i):
    """índice (exclusivo) do fim do bloco iniciado na linha i"""
    base = ind(lines[i])
    j = i + 1
    last = i + 1
    while j < len(lines):
        s = lines[j]
        if not s.strip():
            j += 1
            continue
        if ind(s) <= base:
            break
        j += 1
        last = j
    return last

def find_line(lines, pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    return -1

def split_screen(path):
    """devolve (nome_tela, linhas_de_Properties, linhas_de_Children)"""
    txt = open(path, encoding='utf-8').read()
    lines = txt.split('\n')
    i = find_line(lines, lambda l: l.rstrip() == 'Screens:')
    nome = lines[i + 1].strip().rstrip(':')
    props, children = [], []
    j = i + 2
    while j < len(lines):
        s = lines[j]
        if not s.strip():
            j += 1
            continue
        if ind(s) <= 2:
            break
        if s.strip() == 'Properties:':
            e = block_end(lines, j)
            props = lines[j + 1:e]
            j = e
            continue
        if s.strip() == 'Children:':
            e = block_end(lines, j)
            children = lines[j + 1:e]
            j = e
            continue
        j += 1
    while props and not props[-1].strip():
        props.pop()
    while children and not children[-1].strip():
        children.pop()
    return nome, props, children

def reindent(lines, delta):
    out = []
    for l in lines:
        out.append((' ' * delta + l) if l.strip() else l)
    return out

def prop_block(lines, i):
    """dado i = índice da linha do controle, devolve (ini,fim) do bloco Properties.

    Item de lista ("      - Nome:") tem as chaves filhas 4 espaços à frente;
    chave simples ("Nome:") tem 2. Deduz-se pela primeira linha filha real.
    """
    base = ind(lines[i])
    e = block_end(lines, i)
    filho = None
    for j in range(i + 1, e):
        if lines[j].strip():
            filho = ind(lines[j])
            break
    if filho is None:
        return -1, -1
    for j in range(i + 1, e):
        if lines[j].strip() == 'Properties:' and ind(lines[j]) == filho:
            return j, block_end(lines, j)
    return -1, -1


def set_prop(lines, ctrl_idx, nome, valor):
    """insere/substitui 'nome: valor' em ordem alfabética no Properties do controle."""
    pi, pe = prop_block(lines, ctrl_idx)
    if pi < 0:
        return lines
    pind = ind(lines[pi]) + 2
    nova = f"{' ' * pind}{nome}: {valor}"
    # remove existente
    k = pi + 1
    while k < pe:
        if ind(lines[k]) == pind and re.match(r'^\s*' + re.escape(nome) + r':', lines[k]):
            ke = block_end(lines, k)
            del lines[k:ke]
            pe -= (ke - k)
            break
        k += 1
    # insere em ordem alfabética
    pos = pe
    k = pi + 1
    while k < pe:
        if ind(lines[k]) == pind:
            m = re.match(r"^\s*([A-Za-z_][\w.']*):", lines[k])
            if m and m.group(1).lower() > nome.lower():
                pos = k
                break
        k += 1
    lines.insert(pos, nova)
    return lines

def find_ctrl(lines, nome, indent=None):
    """índice da linha '- nome:' (child) ou 'nome:'"""
    for i, l in enumerate(lines):
        s = l.strip()
        if s == f'- {nome}:' or s == f'{nome}:':
            if indent is None or ind(l) == indent:
                return i
    return -1
