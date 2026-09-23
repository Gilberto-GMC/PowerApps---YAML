# -*- coding: utf-8 -*-
"""Variáveis escritas e nunca lidas — e variáveis de proteção nunca ligadas.

Duas lições (2026-08-27):
 - escrita sem leitura é lixo de estado: cada UpdateContext ainda dispara
   recálculo de dependências;
 - variável booleana que só é setada para false (ou só para true) é mecanismo
   morto que parece implementado: contar liga e desliga separadamente.

Escopo: Set() é global (lida em qualquer tela); UpdateContext() é da tela.
O universo é o app inteiro: msapp/Src com as telas de out/ por cima.

Uso: python build/checar_vars_mortas.py [--baseline] [--dir PASTA]
"""
import sys, os, re, glob, collections
sys.path.insert(0, os.path.dirname(__file__))
from checar_cross_screen import mascarar, texto_sem_cabecalho

PAT_SET = re.compile(r'\bSet\(\s*([A-Za-z_]\w*)\s*[,;]')
PAT_CTX = re.compile(r'UpdateContext\(\s*\{([^}]*)\}', re.S)
PAT_CHAVE = re.compile(r'(?:^|[,{\s])([A-Za-z_]\w*)\s*:')
PAT_NAV_CTX = re.compile(r'Navigate\([^{]*\{([^}]*)\}', re.S)


def texto_ativo(path):
    return mascarar(texto_sem_cabecalho(path))


def universo(pasta):
    telas = {}
    for f in glob.glob('msapp/Src/*.pa.yaml'):
        n = os.path.basename(f)[:-len('.pa.yaml')]
        if n in ('App', '_EditorState'):
            continue
        telas[n] = f
    if pasta != 'msapp/Src':
        for f in glob.glob(os.path.join(pasta, '*.pa.yaml')):
            m = re.match(r'^(?:\d+_)?(.+)\.pa\.yaml$', os.path.basename(f))
            if m and m.group(1) not in ('App', '_EditorState'):
                telas[m.group(1)] = f
    app = 'msapp/Src/App.pa.yaml'
    if pasta != 'msapp/Src':
        for c in (os.path.join(pasta, '01_App.pa.yaml'), os.path.join(pasta, 'App.pa.yaml')):
            if os.path.exists(c):
                app = c
    return telas, app


def main():
    baseline = '--baseline' in sys.argv
    pasta = 'msapp/Src' if baseline else 'out'
    if '--dir' in sys.argv:
        pasta = sys.argv[sys.argv.index('--dir') + 1]
    telas, app = universo(pasta)
    textos = {t: texto_ativo(f) for t, f in telas.items()}
    textos['App'] = texto_ativo(app)
    comps = glob.glob('msapp/Src/Components/*.pa.yaml') + glob.glob(os.path.join(pasta, 'Components', '*.pa.yaml'))
    for c in comps:
        textos['Components/' + os.path.basename(c)] = texto_ativo(c)
    tudo = '\n'.join(textos.values())

    from fx import find_call, split_args

    def chaves_topo(registro):
        """chaves de 1º nível de um literal de registro (ignora registros aninhados)"""
        out = []
        for arg in split_args(registro):
            m = re.match(r'^\s*([A-Za-z_]\w*)\s*:', arg)
            if m:
                out.append(m.group(1))
        return out

    globais = collections.Counter(); ctx = collections.defaultdict(collections.Counter)
    for t, txt in textos.items():
        for m in PAT_SET.finditer(txt):
            globais[m.group(1)] += 1
        pos = 0
        while True:
            r = find_call(txt, 'UpdateContext', pos)
            if not r:
                break
            a, b, c = r; pos = c
            corpo = txt[b:c - 1].strip()
            if corpo.startswith('{') and corpo.endswith('}'):
                for k in chaves_topo(corpo[1:-1]):
                    ctx[t][k] += 1
        pos = 0
        while True:
            r = find_call(txt, 'Navigate', pos)
            if not r:
                break
            a, b, c = r; pos = c
            args = split_args(txt[b:c - 1])
            if len(args) >= 3 and args[2].strip().startswith('{'):
                destino = args[0].strip()
                corpo = args[2].strip()[1:-1]
                for k in chaves_topo(corpo):
                    ctx[destino if destino in textos else t][k] += 1

    def leituras(nome, txt):
        # ocorrências que não são escrita: tira Set(nome, e {nome: dos UpdateContext
        n = len(re.findall(r'(?<![\w.\'])' + re.escape(nome) + r'(?![\w])', txt))
        n -= len(re.findall(r'\bSet\(\s*' + re.escape(nome) + r'\s*[,;]', txt))
        n -= len(re.findall(r'(?:[,{\s])' + re.escape(nome) + r'\s*:', txt))
        return max(0, n)

    mortas = []
    for v in sorted(globais):
        if leituras(v, tudo) == 0:
            mortas.append(('global', 'App/todas', v, globais[v]))
    for t in sorted(ctx):
        for v in sorted(ctx[t]):
            if v in globais:
                continue
            if leituras(v, textos[t]) == 0:
                mortas.append(('contexto', t, v, ctx[t][v]))

    # liga/desliga de booleanas de proteção/overlay
    presas = []
    for t, txt in textos.items():
        for v in set(re.findall(r'\b(var\w*(?:ocupado|Ocupado|salvando|Salvando|load|Load|visible|Visible)\w*)\s*:', txt)):
            liga = len(re.findall(re.escape(v) + r'\s*:\s*(true|Now\(\))', txt))
            desliga = len(re.findall(re.escape(v) + r'\s*:\s*(false|Blank\(\))', txt))
            if liga and not desliga:
                presas.append((t, v, 'só liga — estado pode ficar preso'))
            if desliga and not liga and leituras(v, txt) > 0:
                presas.append((t, v, 'só desliga — mecanismo morto'))

    # telas que a entrega manda excluir não contam; App.* só conta quando o App faz parte da entrega
    from checar_refs import TELAS_REMOVIDAS
    app_entregue = baseline or os.path.exists(os.path.join(pasta, '01_App.pa.yaml'))
    erros, avisos = [], []
    # allowlist do projeto (build/allow_vars_mortas.json): [{"variavel": ..., "motivo": ...}]
    import json
    permitidas = {}
    if not baseline and os.path.exists('build/allow_vars_mortas.json'):
        permitidas = {a['variavel']: a['motivo'] for a in json.load(open('build/allow_vars_mortas.json', encoding='utf-8'))}
    usadas = set()
    for tipo, t, v, n in mortas:
        if t in TELAS_REMOVIDAS:
            continue
        if v in permitidas:
            usadas.add(v)
            continue
        if tipo == 'global' and not app_entregue:
            avisos.append(f"global {v} (escrita {n}x, nunca lida) — App.OnStart não faz parte deste lote")
            continue
        erros.append(f"{tipo:8} {t:26} {v} (escrita {n}x, nunca lida)")
    for t, v, e in presas:
        if t not in TELAS_REMOVIDAS:
            avisos.append(f"liga/desliga {t:26} {v}: {e}")
    for v in sorted(set(permitidas) - usadas):
        erros.append(f"allowlist declarada que não ocorre: {v}")
    for e in erros:
        print(f"   {'!' if baseline else '✗'} {e}")
    for a in avisos:
        print(f"   ! {a}")
    print(f"   total: {len(erros)} variáveis mortas, {len(avisos)} avisos" + (' (baseline)' if baseline else ''))
    if erros and not baseline:
        sys.exit(1)
    if not erros:
        print("   ✓ nenhuma variável morta")


if __name__ == '__main__':
    main()
