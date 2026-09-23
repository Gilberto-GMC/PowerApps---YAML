# -*- coding: utf-8 -*-
"""Gerador da frente "app leve": aplica as cirurgias de build/lotes.py sobre
msapp/Src/*.pa.yaml e grava out/NN_<Tela>.pa.yaml (só telas que mudaram).

Regras:
 - cada cirurgia declara quantas vezes tem de casar por tela; divergência aborta;
 - texto ativo apenas: strings e comentários Power Fx são mascarados antes de
   localizar (posições preservadas), então nada dentro deles é tocado;
 - exceções visuais vão para out/_excecoes_layout.json e a trava de layout
   cobra cada uma delas;
 - grava com newline='\n' e cabeçalho com aviso de LOCALE.

Uso: python build/gerar_leve.py --lote A|AB|ABC|ABCD [--contar] [--lotes caminho/lotes.py]
     --contar: só imprime quantas vezes cada cirurgia casa (não grava, não aborta)
     --lotes:  tabela de cirurgias de outro projeto (ex.: o app mobile de Pista roda
               este gerador com cwd na pasta dele e --lotes build/lotes.py). O módulo
               pode definir NUM, TELAS_MORTAS e PROJETO; sem eles valem os do Inspeções.
"""
import sys, os, re, glob, json
sys.path.insert(0, os.path.dirname(__file__))
from pautil import HDR, ind, block_end, find_ctrl, set_prop, prop_block
from fx import find_call, split_args
from checar_cross_screen import mascarar


def _carregar_lotes():
    if '--lotes' in sys.argv:
        import importlib.util
        caminho = os.path.abspath(sys.argv[sys.argv.index('--lotes') + 1])
        sys.path.insert(1, os.path.dirname(caminho))
        spec = importlib.util.spec_from_file_location('lotes', caminho)
        mod = importlib.util.module_from_spec(spec)
        sys.modules['lotes'] = mod
        spec.loader.exec_module(mod)
        return mod
    import lotes as mod
    return mod


lotes = _carregar_lotes()

NUM = getattr(lotes, 'NUM', {
    'App': 1,
    'frmHome': 3, 'frmInspPistaCad': 4, 'frmFormZPA': 5, 'frmHomePista': 6, 'frmHomeApont': 7,
    'frmHomePatio': 8, 'frmHomeTPS': 9, 'frmHomeZPA': 10, 'frmFormZPAeditar': 11,
    'frmFormZPAmenu': 12, 'frmZPAapontamentos': 13, 'frmVeiculos_Equipamentos': 14,
    'frmCheckListGenericoEQP': 15, 'frmRelatorioZPA': 16, 'frmRelatorioVistoVeic': 17,
})
TELAS_MORTAS = getattr(lotes, 'TELAS_MORTAS', {'frmApontFauna', 'ScreenConsultarV1', 'frmRelatorioZPA_1', 'Screen1'})
PROJETO = getattr(lotes, 'PROJETO', 'Inspeções')


class Abortar(SystemExit):
    pass


# ─────────────────────────────────────────────────────────────────────────────
# normalização: escalar YAML entre aspas com \n vira bloco literal |-
# (o Studio aceita as duas formas; o bloco é o que ele mesmo grava para
# fórmulas de várias linhas — e é a única forma em que a máscara de
# strings/comentários funciona sem se perder nos escapes \" e \n)
# ─────────────────────────────────────────────────────────────────────────────
MANTIDAS_ENTRE_ASPAS = []   # (tela, propriedade, motivo): fórmulas de várias linhas que ficam como o Studio gravou


def normalizar_escalares(texto, tela=''):
    import yaml
    linhas = texto.split('\n')
    out = []
    n = 0
    for l in linhas:
        m = re.match(r'^(\s*)([A-Za-z_][\w.\']*): (".*")\s*$', l)
        if m and '\\n' in m.group(3):
            try:
                val = yaml.safe_load(m.group(3))
            except Exception:
                out.append(l); continue
            if not isinstance(val, str) or '\r' in val:
                # escalar com \r embutido: um bloco literal perderia o \r na
                # leitura; fica entre aspas como o Studio gravou
                MANTIDAS_ENTRE_ASPAS.append((tela, m.group(2), 'tem quebra CR embutida'))
                out.append(l); continue
            pind = len(m.group(1))
            # "|-" tira a quebra final; valor que termina em 1 quebra usa "|" (mantém 1)
            corpo_val, estilo = (val[:-1], '|') if val.endswith('\n') else (val, '|-')
            bloco = [f"{m.group(1)}{m.group(2)}: {estilo}"]
            for t in corpo_val.split('\n'):
                # linha só de espaços mantém os espaços (conteúdo da fórmula); só a vazia fica vazia
                bloco.append((' ' * (pind + 2) + t) if t else '')
            # prova: o bloco relido tem de dar exatamente o mesmo valor; senão fica entre aspas
            try:
                # + '\n': no arquivo real sempre vem outra linha depois (sem ela o "|" não teria quebra a manter)
                relido = yaml.safe_load('\n'.join(x[pind:] for x in bloco) + '\n')
            except Exception:
                relido = None
            if not isinstance(relido, dict) or relido.get(m.group(2)) != val:
                MANTIDAS_ENTRE_ASPAS.append((tela, m.group(2), 'bloco literal não reproduz o valor'))
                out.append(l); continue
            out.extend(bloco)
            n += 1
        else:
            out.append(l)
    return '\n'.join(out), n


# ─────────────────────────────────────────────────────────────────────────────
# primitivas de cirurgia
# ─────────────────────────────────────────────────────────────────────────────
PAT_PROP_LINHA = re.compile(r'^(\s*)([A-Za-z_][\w.\']*): (\||=|"|\')')
PAT_CTRL_LINHA = re.compile(r'^(\s*)- ([A-Za-z_]\w*):\s*$')


def dono_de(texto, pos):
    """(controle, propriedade) que contêm a posição pos do texto"""
    linhas = texto[:pos].split('\n')
    # linha da posição e sua indentação
    i = len(linhas) - 1
    prop = None; ind_prop = None
    for k in range(i, -1, -1):
        l = linhas[k]
        m = PAT_PROP_LINHA.match(l)
        if m and (ind_prop is None or len(m.group(1)) < ind_prop) and (k == i or len(m.group(1)) < len(l) - len(l.lstrip()) or True):
            # primeira linha de propriedade acima com indentação menor que a da fórmula
            if k == i or len(m.group(1)) < (len(linhas[i]) - len(linhas[i].lstrip())):
                prop = m.group(2); ind_prop = len(m.group(1)); break
    ctrl = None
    for k in range(i, -1, -1):
        m = PAT_CTRL_LINHA.match(linhas[k])
        if m and (ind_prop is None or len(m.group(1)) < ind_prop):
            ctrl = m.group(2); break
    return ctrl, prop


def substituir_regex(texto, padrao, substituto, verificar=None):
    """substitui só em texto ativo; devolve (texto, n, donos[(ctrl, prop)]).
    verificar: regex que o trecho ORIGINAL de cada match tem de satisfazer
    (as strings ficam mascaradas na busca; isto confere o literal de verdade)."""
    m = mascarar(texto)
    pos = 0; n = 0; out = []; donos = []

    class _Grupos:
        """grupos do match lidos do texto ORIGINAL (a máscara apaga strings)"""
        def __init__(self, mt):
            self.mt = mt
        def group(self, i=0):
            return texto[self.mt.start(i):self.mt.end(i)]
        def expand(self, tpl):
            return re.sub(r'\\(\d)', lambda g: self.group(int(g.group(1))), tpl)

    for mt in re.finditer(padrao, m):
        if verificar and not re.search(verificar, texto[mt.start():mt.end()]):
            continue     # o literal original não é o esperado: não é este o alvo (não conta)
        donos.append(dono_de(texto, mt.start()))
        out.append(texto[pos:mt.start()])
        g = _Grupos(mt)
        if callable(substituto):
            out.append(substituto(g))
        else:
            out.append(g.expand(substituto) if '\\' in substituto else substituto)
        pos = mt.end(); n += 1
    out.append(texto[pos:])
    return ''.join(out), n, donos


def definir_prop(texto, controle, prop, novo_valor):
    """substitui o valor inteiro de uma propriedade por um bloco literal |-"""
    linhas = texto.split('\n')
    i = find_ctrl(linhas, controle)
    if i < 0:
        raise Abortar(f"definir_prop: controle {controle} não encontrado")
    pi, pe = prop_block(linhas, i)
    pind = ind(linhas[pi]) + 2
    k = pi + 1
    while k < pe:
        if ind(linhas[k]) == pind and re.match(r'^\s*' + re.escape(prop) + r':', linhas[k]):
            ke = block_end(linhas, k)
            novo = [f"{' ' * pind}{prop}: |-"]
            for t in novo_valor.strip('\n').split('\n'):
                novo.append((' ' * (pind + 2) + t) if t else '')
            linhas[k:ke] = novo
            return '\n'.join(linhas)
        k += 1
    raise Abortar(f"definir_prop: {controle}.{prop} não encontrada")


def substituir_na_prop(texto, controle, prop, pares):
    """aplica pares (velho, novo) só dentro da propriedade prop do controle;
    cada par tem de casar exatamente 1 vez. Devolve texto."""
    linhas = texto.split('\n')
    i = find_ctrl(linhas, controle)
    if i < 0:
        raise Abortar(f"substituir_na_prop: controle {controle} não encontrado")
    pi, pe = prop_block(linhas, i)
    if pi < 0:
        raise Abortar(f"substituir_na_prop: {controle} sem Properties")
    pind = ind(linhas[pi]) + 2
    k = pi + 1
    while k < pe:
        if ind(linhas[k]) == pind and re.match(r'^\s*' + re.escape(prop) + r':', linhas[k]):
            ke = block_end(linhas, k)
            cab = linhas[k]
            if ke == k + 1:
                # valor em linha única: "Prop: =..."
                m = re.match(r'^(\s*' + re.escape(prop) + r': )(.*)$', cab)
                valor = m.group(2)
                if valor.lstrip().startswith(('"', "'")):
                    raise Abortar(f"substituir_na_prop: {controle}.{prop} é escalar YAML entre aspas "
                                  f"(a normalização não converteu); trocar texto nele corromperia os escapes")
                for velho, novo in pares:
                    if valor.count(velho) != 1:
                        raise Abortar(f"substituir_na_prop: {controle}.{prop}: '{velho[:50]}' casou {valor.count(velho)}x (esperado 1)")
                    valor = valor.replace(velho, novo)
                if '\n' in valor:
                    novo_bloco = [f"{' ' * pind}{prop}: |-"] + [(' ' * (pind + 2) + t) if t else '' for t in valor.split('\n')]
                    linhas[k:ke] = novo_bloco
                else:
                    linhas[k] = m.group(1) + valor
                return '\n'.join(linhas)
            # bloco literal: compara e substitui no texto DEDENTADO
            corpo = linhas[k + 1:ke]
            reais = [l for l in corpo if l.strip()]
            base = min(ind(l) for l in reais)
            ded = '\n'.join(l[base:] for l in corpo)
            for velho, novo in pares:
                if ded.count(velho) != 1:
                    raise Abortar(f"substituir_na_prop: {controle}.{prop}: '{velho[:50]}' casou {ded.count(velho)}x (esperado 1)")
                ded = ded.replace(velho, novo)
            linhas[k + 1:ke] = [(' ' * base + t) if t else '' for t in ded.split('\n')]
            return '\n'.join(linhas)
        k += 1
    raise Abortar(f"substituir_na_prop: {controle}.{prop} não encontrada")


def contar_regex(texto, padrao, verificar=None):
    m = mascarar(texto)
    return sum(1 for mt in re.finditer(padrao, m)
               if not verificar or re.search(verificar, texto[mt.start():mt.end()]))


def remover_controle(texto, nome, outros_mascarados):
    """remove o bloco '- nome:' inteiro. Exige Visible: =false literal e zero
    referências ao nome fora do próprio bloco (na tela e nas outras telas)."""
    linhas = texto.split('\n')
    i = find_ctrl(linhas, nome)
    if i < 0:
        return texto, 0
    e = block_end(linhas, i)
    bloco = '\n'.join(linhas[i:e])
    # Visible literal false: "Visible: =false" ou bloco "Visible: |\n  =false"
    if not (re.search(r'^\s*Visible: =false\s*$', bloco, re.M)
            or re.search(r'^\s*Visible: \|-?\s*\n\s*=false\s*$', bloco, re.M)):
        raise Abortar(f"remover_controle({nome}): Visible não é literal false — não remove")
    del linhas[i:e]
    novo = '\n'.join(linhas)
    resto = mascarar(novo) + '\n' + outros_mascarados
    if re.search(r'(?<![\w.\'])' + re.escape(nome) + r'(?![\w])', resto):
        raise Abortar(f"remover_controle({nome}): ainda há referência ao nome fora do bloco")
    return novo, 1


def remover_campo(texto, nome):
    """remove 'nome: <expr>' de um literal de registro, com balanceamento
    (portado de SAFETY/build/gerar.py). Devolve (texto, achou)."""
    pat = re.compile(r'\n(\s*)' + re.escape(nome) + r':\s')
    m = pat.search(texto)
    if not m:
        return texto, False
    i = m.end()
    depth, q, ultimo_nl = 0, None, i
    while i < len(texto):
        c = texto[i]
        if q:
            if c == q:
                q = None
            i += 1; continue
        if c in '"\'':
            q = c; i += 1; continue
        if c == '\n':
            ultimo_nl = i
        if c in '([{':
            depth += 1
        elif c in ')]}':
            if depth == 0:
                pre = texto[:m.start()].rstrip()
                if pre.endswith(','):
                    pre = pre[:-1]
                return pre + texto[ultimo_nl:], True
            depth -= 1
        elif c == ',' and depth == 0:
            return texto[:m.start()] + texto[i + 1:], True
        i += 1
    return texto, False


def _limpar_linha_vazia(texto, pos):
    """se a linha que contém pos ficou só com espaços, apaga a linha inteira"""
    ls = texto.rfind('\n', 0, pos) + 1
    le = texto.find('\n', pos)
    le = len(texto) if le < 0 else le
    if texto[ls:le].strip() == '' and ls > 0:
        return texto[:ls - 1] + texto[le:]
    return texto


def remover_statement(texto, a, c):
    """remove texto[a:c] (uma chamada inteira) e o ';' que a encadeia.
    Preferência: consome o ';' seguinte; se não houver, o anterior."""
    j = c
    while j < len(texto) and texto[j] in ' \t\r\n':
        j += 1
    if j < len(texto) and texto[j] == ';':
        novo = texto[:a] + texto[j + 1:]
        # o que vinha depois do ';' começa na coluna certa? tira espaços à esquerda
        # até a próxima quebra e a linha vazia que sobrou
        k = a
        while k < len(novo) and novo[k] in ' \t':
            k += 1
        novo = novo[:a] + novo[k:]
        return _limpar_linha_vazia(novo, a)
    i = a
    while i > 0 and texto[i - 1] in ' \t\r\n':
        i -= 1
    if i > 0 and texto[i - 1] == ';':
        novo = texto[:i - 1] + texto[c:]
        return _limpar_linha_vazia(novo, i - 1)
    novo = texto[:a] + texto[c:]
    return _limpar_linha_vazia(novo, a)


def _chave_de(arg):
    # comentários antes da chave (// ...) são apagados pela máscara
    m = re.match(r'^\s*([A-Za-z_]\w*)\s*:', mascarar(arg))
    return m.group(1) if m else None


def remover_chave_registro(texto, ini, fim, var):
    """texto[ini:fim] é um literal de registro '{...}'. Remove a chave var.
    Devolve (texto, removeu, ficou_vazio)."""
    reg = texto[ini:fim]
    assert reg.startswith('{') and reg.endswith('}')
    corpo = reg[1:-1]
    args = split_args(corpo)
    chaves = [_chave_de(a) for a in args]
    if var not in chaves:
        return texto, False, False
    if '\n' in corpo and re.search(r'\n\s*' + re.escape(var) + r':\s', reg):
        # registro de várias linhas com a chave na própria linha: remoção preservando formato
        novo_reg, ok = remover_campo(reg, var)
        if not ok:
            raise Abortar(f"remover_chave_registro: falhou em {var}")
    else:
        restantes = [a for a in args if _chave_de(a) != var]
        novo_reg = '{' + ', '.join(a.strip() for a in restantes) + '}' if restantes else '{}'
    vazio = re.fullmatch(r'\{\s*\}', novo_reg) is not None
    return texto[:ini] + novo_reg + texto[fim:], True, vazio


def remover_escritas_var(texto, var, alvo_navigate=None):
    """apaga toda escrita da variável nesta tela: chave em UpdateContext({...}),
    contexto de Navigate(alvo, ..., {...}) (quando alvo_navigate é dado, só
    Navigate para essa tela) e Set(var, ...). Devolve (texto, n)."""
    n = 0
    for fn in (('Navigate',) if alvo_navigate is not None else ('UpdateContext', 'Navigate')):
        pos = 0
        while True:
            r = find_call(texto, fn, pos)
            if not r:
                break
            a, b, c = r
            args_raw = texto[b:c - 1]
            args = split_args(args_raw)
            if fn == 'UpdateContext':
                idx = 0
            else:
                if alvo_navigate is not None and (not args or args[0].strip() != alvo_navigate):
                    pos = c; continue
                idx = 2
            if len(args) <= idx or not args[idx].strip().startswith('{'):
                pos = c; continue
            # posição absoluta do registro dentro do texto
            off = 0
            for k in range(idx):
                off = args_raw.index(args[k], off) + len(args[k])
                off = args_raw.index(',', off) + 1
            ini = b + args_raw.index(args[idx], off)
            fim = ini + len(args[idx].rstrip())
            texto2, removeu, vazio = remover_chave_registro(texto, ini, fim, var)
            if not removeu:
                pos = c; continue
            texto = texto2; n += 1
            if vazio and fn == 'UpdateContext':
                r2 = find_call(texto, 'UpdateContext', a)
                a2, b2, c2 = r2
                texto = remover_statement(texto, a2, c2)
                pos = a2
            else:
                pos = a + 1
    if alvo_navigate is None:
        pos = 0
        while True:
            r = find_call(texto, 'Set', pos)
            if not r:
                break
            a, b, c = r
            args = split_args(texto[b:c - 1])
            if args and args[0].strip() == var:
                texto = remover_statement(texto, a, c)
                n += 1
                pos = a
                continue
            pos = c
    return texto, n


# ─────────────────────────────────────────────────────────────────────────────
# execução
# ─────────────────────────────────────────────────────────────────────────────
def carregar_origem():
    telas = {}
    for p in sorted(glob.glob('msapp/Src/*.pa.yaml')):
        n = os.path.basename(p)[:-len('.pa.yaml')]
        if n == '_EditorState' or n in TELAS_MORTAS:
            continue
        telas[n] = open(p, encoding='utf-8').read()     # inclui 'App'
    return telas


VISUAIS_TRAVA = None
aplicadas_extra = {}   # {tela: {ids}} cirurgias que tocaram outra tela (contexto de Navigate)
CTX = {}               # estado compartilhado entre cirurgias 'func' (tabelas extraídas etc.)


def _visuais():
    global VISUAIS_TRAVA
    if VISUAIS_TRAVA is None:
        from trava_layout import VISUAIS
        VISUAIS_TRAVA = VISUAIS
    return VISUAIS_TRAVA


def leituras_na_tela(txt_mascarado, var):
    n = len(re.findall(r'(?<![\w.\'])' + re.escape(var) + r'(?![\w])', txt_mascarado))
    n -= len(re.findall(r'\bSet\(\s*' + re.escape(var) + r'\s*[,;]', txt_mascarado))
    n -= len(re.findall(r'(?:[,{\s])' + re.escape(var) + r'\s*:', txt_mascarado))
    return max(0, n)


def aplicar(cir, telas, mascaras, app_mascarado, contar):
    """aplica uma cirurgia; devolve ({tela: n}, excecoes_mudam[(tela, ctrl, prop)])"""
    tipo = cir['tipo']
    if tipo in ('prop', 'prop_regex', 'prop_set', 'prop_add'):
        alvo = sorted({a[0] for a in cir['alvos']})
    elif tipo in ('set_prop', 'remover_controle'):
        alvo = sorted(cir['controles'])
    elif tipo == 'remover_var':
        alvo = sorted(cir['variaveis'])
    else:
        alvo = cir.get('telas') or list(telas)
    achados = {}; mudam = []
    for tela in alvo:
        if tela not in telas:
            raise Abortar(f"[{cir['id']}] tela {tela} não existe")
        txt = telas[tela]
        if tipo == 'regex':
            if contar:
                n = contar_regex(txt, cir['localizar'], cir.get('verificar'))
            else:
                txt, n, donos = substituir_regex(txt, cir['localizar'], cir['substituir'], cir.get('verificar'))
                for ctrl, prop in donos:
                    if prop in _visuais() and ctrl:
                        mudam.append((tela, ctrl, prop))
        elif tipo == 'prop':
            n = 0
            for t, ctrl, prop, pares in cir['alvos']:
                if t != tela:
                    continue
                if not contar:
                    txt = substituir_na_prop(txt, ctrl, prop, pares)
                    if prop in _visuais():
                        mudam.append((tela, ctrl, prop))
                n += 1
        elif tipo in ('prop_set', 'prop_add'):
            # valor inteiro de uma propriedade substituído (bloco |-); prop_add cria a
            # propriedade em ordem alfabética se ela não existir (ex.: OnVisible de tela)
            n = 0
            for t, ctrl, prop, novo in cir['alvos']:
                if t != tela:
                    continue
                if not contar:
                    if tipo == 'prop_add':
                        linhas = txt.split('\n')
                        i = find_ctrl(linhas, ctrl)
                        if i < 0:
                            raise Abortar(f"[{cir['id']}] {ctrl} não encontrado em {tela}")
                        set_prop(linhas, i, prop, '=')
                        txt = '\n'.join(linhas)
                    txt = definir_prop(txt, ctrl, prop, novo)
                    if prop in _visuais():
                        mudam.append((tela, ctrl, prop))
                n += 1
        elif tipo == 'prop_regex':
            # regex dentro de UMA propriedade de UM controle; cada (padrão, substituto, n) casa n vezes
            n = 0
            for t, ctrl, prop, regras in cir['alvos']:
                if t != tela:
                    continue
                linhas = txt.split('\n')
                i = find_ctrl(linhas, ctrl)
                if i < 0:
                    raise Abortar(f"[{cir['id']}] controle {ctrl} não encontrado em {tela}")
                pi, pe = prop_block(linhas, i)
                pind = ind(linhas[pi]) + 2
                k = pi + 1; achou = False
                while k < pe:
                    if ind(linhas[k]) == pind and re.match(r'^\s*' + re.escape(prop) + r':', linhas[k]):
                        ke = block_end(linhas, k)
                        bloco = '\n'.join(linhas[k:ke])
                        for padrao, subst, esperado_n in regras:
                            if contar:
                                nn = contar_regex(bloco, padrao)
                            else:
                                bloco, nn, _ = substituir_regex(bloco, padrao, subst)
                            if nn != esperado_n:
                                raise Abortar(f"[{cir['id']}] {tela} {ctrl}.{prop}: padrão '{padrao[:40]}' casou {nn}x, esperado {esperado_n}")
                            n += nn
                        if not contar:
                            linhas[k:ke] = bloco.split('\n')
                            if prop in _visuais():
                                mudam.append((tela, ctrl, prop))
                        achou = True
                        break
                    k += 1
                if not achou:
                    raise Abortar(f"[{cir['id']}] {tela} {ctrl}.{prop} não encontrada")
                txt = '\n'.join(linhas)
        elif tipo == 'set_prop':
            n = 0
            linhas = txt.split('\n')
            for nome in cir['controles'].get(tela, []):
                i = find_ctrl(linhas, nome)
                if i < 0:
                    raise Abortar(f"[{cir['id']}] controle {nome} não encontrado em {tela}")
                if not contar:
                    set_prop(linhas, i, cir['prop'], cir['valor'])
                n += 1
            txt = '\n'.join(linhas)
        elif tipo == 'remover_controle':
            n = 0
            for nome in cir['controles'].get(tela, []):
                if contar:
                    n += 1 if find_ctrl(txt.split('\n'), nome) >= 0 else 0
                else:
                    outros = '\n'.join(v for t, v in mascaras.items() if t != tela) + '\n' + app_mascarado
                    txt, k = remover_controle(txt, nome, outros)
                    n += k
                    mascaras[tela] = mascarar(txt)
        elif tipo == 'remover_var':
            n = 0
            m = mascarar(txt)
            for var in cir['variaveis'].get(tela, []):
                # global (Set) é lida em qualquer tela; contexto só nesta
                eh_global = bool(re.search(r'\bSet\(\s*' + re.escape(var) + r'\s*[,;]', m))
                escopo = ('\n'.join(mascaras.values()) + '\n' + app_mascarado) if eh_global else m
                if leituras_na_tela(escopo, var) > 0:
                    raise Abortar(f"[{cir['id']}] {tela}: {var} ainda é lida ({'global' if eh_global else 'contexto'}) — não remove")
                if contar:
                    n += len(re.findall(r'(?:[,{\s])' + re.escape(var) + r'\s*:', m)) + \
                         len(re.findall(r'\bSet\(\s*' + re.escape(var) + r'\s*,', m))
                    # contexto passado por Navigate(tela, ..., {var: ...}) a partir de outras telas
                    for t2, m2 in mascaras.items():
                        if t2 != tela:
                            n += len(re.findall(r'Navigate\(\s*' + tela + r'\b[^{]*\{[^}]*\b' + re.escape(var) + r'\s*:', m2))
                else:
                    txt, k = remover_escritas_var(txt, var)
                    n += k
                    if not eh_global:
                        for t2 in list(telas):
                            if t2 == tela:
                                continue
                            telas[t2], k2 = remover_escritas_var(telas[t2], var, alvo_navigate=tela)
                            if k2:
                                n += k2
                                mascaras[t2] = mascarar(telas[t2])
                                aplicadas_extra.setdefault(t2, set()).add(cir['id'])
                if n == 0 and not contar:
                    raise Abortar(f"[{cir['id']}] {tela}: nenhuma escrita de {var} encontrada")
            if not contar:
                mascaras[tela] = mascarar(txt)
        elif tipo == 'func':
            txt, n = cir['fn'](tela, txt, contar, CTX)
            for t, c, p in cir.get('mudam', []):
                if t == tela:
                    mudam.append((t, c, p))
        else:
            raise Abortar(f"[{cir['id']}] tipo desconhecido {tipo}")
        achados[tela] = n
        if not contar:
            telas[tela] = txt
    return achados, mudam


def conferir(cir, achados):
    esperado = cir.get('esperado', {})
    total_esp = cir.get('esperado_total')
    erros = []
    for tela, n in achados.items():
        e = esperado.get(tela, 0 if esperado else None)
        if e is not None and n != e:
            erros.append(f"{tela}: casou {n}x, esperado {e}")
    if total_esp is not None and sum(achados.values()) != total_esp:
        erros.append(f"total {sum(achados.values())}, esperado {total_esp}")
    if erros:
        raise Abortar(f"[{cir['id']}] " + '; '.join(erros))


def cabecalho(tela, aplicadas):
    if tela == 'App':
        destino = (f'# ENTREGA {PROJETO} — App: NÃO colar este arquivo. Ele é a referência invariante do OnStart;\n'
                   '# cole 01_App_OnStart_ptBR.txt em App > OnStart'
                   + (' e 02_App_Formulas_ptBR.txt em App > Formulas.' if 'nfAeros' in CTX else '.'))
    else:
        destino = f'# ENTREGA {PROJETO} — {tela}: colar em Studio > tela {tela} > Exibição de código > substituir tudo.'
    linhas = [
        HDR.rstrip('\n'),
        '#',
        destino,
        '# LOCALE: este arquivo está em formato INVARIANTE ("," separa argumentos, ";" encadeia,',
        '#         "." decimal). É assim que a exibição de código lê e grava. NÃO converter para pt-BR.',
        '# Cirurgias aplicadas nesta tela: ' + ', '.join(aplicadas),
        '#',
    ]
    return '\n'.join(linhas) + '\n'


def main():
    lote = 'ABCD'
    if '--lote' in sys.argv:
        lote = sys.argv[sys.argv.index('--lote') + 1].upper()
    contar = '--contar' in sys.argv
    telas = carregar_origem()
    # escalares entre aspas viram blocos (só nas telas que tiverem)
    normalizadas = {}
    for t in telas:
        telas[t], n = normalizar_escalares(telas[t], t)
        if n:
            normalizadas[t] = n
    original = dict(telas)
    mascaras = {t: mascarar(v) for t, v in telas.items() if t != 'App'}
    app_mascarado = mascarar(telas['App'])
    aplicadas = {t: [] for t in telas}
    excecoes = {'somem': [], 'surgem': [], 'mudam': []}
    for cir in lotes.CIRURGIAS:
        if cir['lote'] not in lote:
            continue
        achados, mudam = aplicar(cir, telas, mascaras, app_mascarado, contar)
        if contar:
            print(f"[{cir['id']}] " + (', '.join(f"{t}={n}" for t, n in achados.items() if n) or '0'))
            continue
        conferir(cir, achados)
        for t, n in achados.items():
            if n:
                aplicadas[t].append(cir['id'])
        for t, ids in aplicadas_extra.items():
            for i in ids:
                if i not in aplicadas[t]:
                    aplicadas[t].append(i)
        if cir['tipo'] == 'remover_controle':
            for t, nomes in cir['controles'].items():
                excecoes['somem'].extend([t, nm] for nm in nomes)
        for t, c, p in mudam:
            if [t, c, p] not in excecoes['mudam']:
                excecoes['mudam'].append([t, c, p])
        for g in ('somem', 'surgem', 'mudam'):
            excecoes[g].extend(cir.get('excecoes', {}).get(g, []))
        print(f"   {cir['id']:4} {cir.get('descricao', '')[:70]:70} " + ', '.join(f"{t}:{n}" for t, n in achados.items() if n))
    if contar:
        return
    os.makedirs('out', exist_ok=True)
    escritas = 0
    for t, txt in telas.items():
        if txt == original[t] and t not in normalizadas:
            continue
        if not aplicadas[t]:
            continue     # só normalização, sem cirurgia: não entrega
        corpo = txt
        # tira o cabeçalho do Studio (vai de novo pelo nosso)
        if corpo.startswith('# ****'):
            corpo = corpo[len(HDR):] if corpo.startswith(HDR) else corpo
        destino = f"out/{NUM[t]:02d}_{t}.pa.yaml"
        for tl, prop, motivo in MANTIDAS_ENTRE_ASPAS:
            if tl == t:
                print(f"   ! {t}: uma propriedade {prop} ficou entre aspas como o Studio gravou ({motivo}); troca de texto nela aborta")
        open(destino, 'w', encoding='utf-8', newline='\n').write(cabecalho(t, aplicadas[t]) + corpo.lstrip('\n'))
        escritas += 1
    if 'nfAeros' in CTX and 'nfParametrosAnimais' in CTX:
        import lote_cd
        lote_cd.escrever_formulas(CTX, 'out/_App_Formulas_invariante.fx')
        print(f"   App.Formulas: nfAeros ({CTX['n_aeros']} registros), nfParametrosAnimais ({CTX['n_animais']} registros) -> out/_App_Formulas_invariante.fx")
    json.dump(excecoes, open('out/_excecoes_layout.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"   {escritas} telas gravadas em out/ (lote {lote}); exceções de layout: "
          + ', '.join(f"{g}={len(v)}" for g, v in excecoes.items()))


if __name__ == '__main__':
    main()
