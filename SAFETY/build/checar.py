import sys, re, json, collections, glob
sys.path.insert(0, 'build')
from valida import carregar, nomes_de
from modulos import MODULOS

erros = []
todos = collections.Counter()
antigas = set()
for m in MODULOS:
    antigas |= {m['lista'], m['forms'], m['det']}

for m in MODULOS:
    path = f"out/{m['nova']}.pa.yaml"
    txt = open(path, encoding='utf-8').read()
    # ignora o cabeçalho de documentação, que cita as telas de origem de propósito
    codigo = '\n'.join(l for l in txt.split('\n') if not l.lstrip().startswith('#'))
    d = carregar(path)
    k, pfx = m['key'], m['pfx']

    # 1. nenhuma navegação sobrou para as telas antigas do módulo
    for alvo in (m['lista'], m['forms'], m['det']):
        if re.search(r'(?<![A-Za-z])' + alvo + r'(?![A-Za-z_])', codigo):
            erros.append(f"[{k}] ainda referencia a tela antiga {alvo}")

    # 2. gravação usa o combo do formulário, não mais o perfil do usuário
    if f'{pfx}_aeroporto: varAeroUser' in codigo:
        erros.append(f"[{k}] Patch ainda grava varAeroUser")
    if f'cmbFrm{k}Aeroporto' not in codigo:
        erros.append(f"[{k}] combo de aeroporto do formulário ausente")

    # 3. escopo de segurança presente na galeria
    if 'varEscopoAero' not in codigo:
        erros.append(f"[{k}] galeria sem escopo de segurança")

    # 4. ID vem do SharePoint
    if f'var_regNovo{k}' not in codigo:
        erros.append(f"[{k}] gravação não usa o ID devolvido pelo SharePoint")
    if re.search(re.escape(m['varId']) + r':\s*Value\(\s*First', codigo):
        erros.append(f"[{k}] cálculo max+1 do ID ainda presente")

    # 5. parênteses balanceados em cada fórmula
    def anda(node, caminho=''):
        if isinstance(node, dict):
            for kk, v in node.items():
                anda(v, f'{caminho}.{kk}')
        elif isinstance(node, list):
            for i, v in enumerate(node):
                anda(v, caminho)
        elif isinstance(node, str) and node.startswith('='):
            s, dep, q = node, 0, None
            i = 0
            while i < len(s):
                c = s[i]
                if q:
                    if c == q: q = None
                    i += 1; continue
                if c in '"\'': q = c; i += 1; continue
                if c == '/' and s[i+1:i+2] == '/':
                    nl = s.find('\n', i); i = len(s) if nl < 0 else nl; continue
                if c in '([{': dep += 1
                elif c in ')]}':
                    dep -= 1
                    if dep < 0:
                        erros.append(f"[{k}] parêntese fecha demais em {caminho}"); break
                i += 1
            if dep > 0:
                erros.append(f"[{k}] parêntese não fechado em {caminho} (+{dep})")
            if q:
                erros.append(f"[{k}] aspas não fechadas em {caminho}")
    anda(d)

    # 6. instrução vazia
    if re.search(r';\s*\n\s*;', codigo):
        erros.append(f"[{k}] instrução vazia ';;' na fórmula")

    nomes = []; nomes_de(d, nomes)
    todos.update(nomes)

dup = [n for n, c in todos.items() if c > 1]
if dup:
    erros.append(f"nomes de controle repetidos entre telas: {dup}")

# 7. referências a controles inexistentes (dos nomes que geramos)
for m in MODULOS:
    txt = open(f"out/{m['nova']}.pa.yaml", encoding='utf-8').read()
    for ctrl in (m['fBloco'], m['fAero'], m['fIni'], m['fFim'], m['fStatus'], m['fBusca'], m['gal']):
        if f'- {ctrl}:' not in txt:
            erros.append(f"[{m['key']}] controle {ctrl} referenciado mas não definido")

print(f"{len(todos)} controles no total nas 7 telas")
if erros:
    print("\n".join("✗ " + e for e in erros)); sys.exit(1)
print("✓ todas as verificações passaram")
