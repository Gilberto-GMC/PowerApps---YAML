# -*- coding: utf-8 -*-
"""Referências entre telas: um controle de OUTRA tela citado em fórmula.

Com delayloadscreens=true, cada referência dessas obriga o Power Apps a carregar
a outra tela inteira (InefficientDelayLoading) e, quando é SubmitForm/EditForm/
NewForm/ResetForm/Reset/Select de um controle alheio, vira escrita fantasma
(CrossScreenEventDependencies). Meta da entrega: zero.

Uso:
    python build/checar_cross_screen.py            # checa out/ (falha se houver)
    python build/checar_cross_screen.py --baseline # mede msapp/Src (só relata)
    python build/checar_cross_screen.py --dir X    # checa outra pasta
"""
import sys, os, re, glob, collections
sys.path.insert(0, os.path.dirname(__file__))
from valida import carregar, nomes_de

FUNCS_EVENTO = ('SubmitForm', 'EditForm', 'NewForm', 'ResetForm', 'ViewForm', 'Reset', 'Select')


def mascarar(fx, manter_comentarios=False):
    """apaga strings e comentários mantendo o tamanho (posições e linhas preservadas).
    Com manter_comentarios=True, só as strings são apagadas."""
    out, i, n = [], 0, len(fx)
    while i < n:
        c = fx[i]
        if manter_comentarios and c == '/' and fx[i + 1:i + 2] in ('/', '*'):
            j = _fim_de_linha(fx, i) if fx[i + 1] == '/' else fx.find('*/', i + 2)
            j = n if j < 0 else (j if fx[i + 1] == '/' else j + 2)
            out.append(fx[i:j]); i = j; continue
        if c == '"':
            j = i + 1
            while j < n:
                if fx[j] == '"':
                    if fx[j + 1:j + 2] == '"':
                        j += 2; continue
                    break
                j += 1
            out.append('"' + ' ' * max(0, j - i - 1) + '"'); i = j + 1; continue
        if c == "'":
            j = fx.find("'", i + 1)
            j = n - 1 if j < 0 else j
            out.append("'" + ' ' * (j - i - 1) + "'"); i = j + 1; continue
        if c == '/' and fx[i + 1:i + 2] == '/':
            j = _fim_de_linha(fx, i); j = n if j < 0 else j
            out.append(' ' * (j - i)); i = j; continue
        if c == '/' and fx[i + 1:i + 2] == '*':
            j = fx.find('*/', i + 2); j = n if j < 0 else j + 2
            out.append(''.join(ch if ch in '\n\r' else ' ' for ch in fx[i:j])); i = j; continue
        out.append(c); i += 1
    return ''.join(out)


def _fim_de_linha(fx, i):
    """posição do próximo \\n ou \\r (o \\r marca quebra dentro de escalar YAML decodificado)"""
    a, b = fx.find('\n', i), fx.find('\r', i)
    if a < 0:
        return b
    if b < 0:
        return a
    return min(a, b)


_PAT_ESCALAR_ASPAS = None


def texto_sem_cabecalho(path):
    """conteúdo do arquivo pronto para varredura lexical, com a numeração de
    linhas do arquivo original preservada:
     - linhas de comentário YAML (#) em branco;
     - fórmula gravada pelo Studio como escalar YAML entre aspas ("=..." ou '=...')
       é decodificada na própria linha. Sem isso a máscara de strings trata a
       fórmula inteira como uma string e ela fica invisível aos checadores (caso
       do App.OnStart do app mobile de Pista). As quebras de linha internas viram
       \\r, que encerra comentário // mas não conta como linha nova."""
    import yaml
    global _PAT_ESCALAR_ASPAS
    if _PAT_ESCALAR_ASPAS is None:
        _PAT_ESCALAR_ASPAS = re.compile(r'''^(\s*[A-Za-z_][\w.']*: )(".*"|'=.*')\s*$''')
    linhas = []
    for l in open(path, encoding='utf-8').read().split('\n'):
        if l.lstrip().startswith('#'):
            linhas.append(''); continue
        m = _PAT_ESCALAR_ASPAS.match(l)
        if m and m.group(2)[1:2] == '=':
            try:
                val = yaml.safe_load(m.group(2))
            except Exception:
                val = None
            if isinstance(val, str):
                l = m.group(1) + val.replace('\r\n', '\r').replace('\n', '\r')
        linhas.append(l)
    return '\n'.join(linhas)


def telas_e_controles(pasta):
    """{tela: set(controles)} a partir dos .pa.yaml da pasta"""
    res = {}
    for f in sorted(glob.glob(os.path.join(pasta, '*.pa.yaml'))):
        d = carregar(f)
        if isinstance(d, dict) and 'Screens' in d:
            tela = list(d['Screens'])[0]
            nomes = []; nomes_de(d, nomes)
            res[tela] = (f, set(nomes))
    return res


def main():
    baseline = '--baseline' in sys.argv
    pasta = 'msapp/Src' if baseline else 'out'
    if '--dir' in sys.argv:
        pasta = sys.argv[sys.argv.index('--dir') + 1]
    # universo de controles: sempre o app inteiro (origem + entregues)
    universo = telas_e_controles('msapp/Src')
    entregues = telas_e_controles(pasta)
    for t, v in entregues.items():
        universo[t] = v
    dono = collections.defaultdict(set)
    for tela, (_, ctrls) in universo.items():
        for c in ctrls:
            dono[c].add(tela)
    telas_nome = set(universo)
    problemas = []
    for tela, (arq, proprios) in sorted(entregues.items()):
        txt = mascarar(texto_sem_cabecalho(arq))
        alheios = {c for c, ts in dono.items() if tela not in ts and c not in proprios and c not in telas_nome}
        # 1) Nome.Propriedade
        for m in re.finditer(r"(?<![\w.'])([A-Za-z_][\w]*)\.[A-Za-z]", txt):
            nome = m.group(1)
            if nome in alheios:
                linha = txt[:m.start()].count('\n') + 1
                problemas.append((tela, linha, nome, 'propriedade', sorted(dono[nome])))
        # 2) SubmitForm(Nome) etc.
        for m in re.finditer(r"\b(" + '|'.join(FUNCS_EVENTO) + r")\(\s*([A-Za-z_][\w]*)", txt):
            nome = m.group(2)
            if nome in alheios:
                linha = txt[:m.start()].count('\n') + 1
                problemas.append((tela, linha, nome, m.group(1) + '()', sorted(dono[nome])))
    problemas.sort()
    # allowlist temporária (build/allow_cross_screen.json): {tela, nome, motivo}
    allow = {}
    import json
    from fontes import filtrar_allow
    if os.path.exists('build/allow_cross_screen.json') and not baseline:
        for a in filtrar_allow(json.load(open('build/allow_cross_screen.json', encoding='utf-8'))):
            allow[(a['tela'], a['nome'])] = a['motivo']
    usados = set(); restantes = []
    for p in problemas:
        if (p[0], p[2]) in allow:
            usados.add((p[0], p[2]))
        else:
            restantes.append(p)
    por_tela = collections.Counter(p[0] for p in restantes)
    for tela, linha, nome, tipo, donos in restantes:
        print(f"   {'!' if baseline else '✗'} {tela}:{linha}  {nome} [{tipo}] pertence a {', '.join(donos)}")
    for k in sorted(set(allow) - usados):
        restantes.append(k); print(f"   ✗ allowlist declarada que não ocorre: {k}")
    print(f"   total: {len(restantes)} referências entre telas em {len(por_tela)} telas"
          + (f", {len(problemas) - len(restantes)} permitidas temporariamente (Lote D)" if usados else '')
          + (' (baseline)' if baseline else ''))
    if restantes and not baseline:
        sys.exit(1)
    if not restantes:
        print("   ✓ nenhuma referência a controle de outra tela fora da allowlist")


if __name__ == '__main__':
    main()
