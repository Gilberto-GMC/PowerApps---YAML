#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificação completa da tela gerada: YAML, árvore de controles, emoji,
aridade das chamadas de fluxo e balanceamento de parênteses das fórmulas."""
import io, re, sys, yaml

FONTE = 'ScreenAcionamentosNewPlemPrai.pa.yaml'
SAIDA = 'ScreenAcionamentosPlemPraiV2.pa.yaml'
EMOJI = re.compile('[\U0001F300-\U0001FAFF⚙⚠❌➕❗⬇]')


class L(yaml.SafeLoader):
    pass


L.add_constructor('tag:yaml.org,2002:value', lambda l, n: l.construct_scalar(n))


def arvore(f):
    d = yaml.load(open(f, encoding='utf-8'), Loader=L)
    out = []

    def w(nd, pt):
        for it in nd or []:
            for nm, bd in (it or {}).items():
                out.append(pt + '/' + nm)
                w((bd or {}).get('Children'), pt + '/' + nm)
    w(d['Screens']['ScreenAcionamentosPlemPrai'].get('Children'), '')
    return out, d


def sem_comentario(x):
    out, i, ins = [], 0, False
    while i < len(x):
        c = x[i]
        if ins:
            out.append(c)
            if c == '"':
                ins = False
            i += 1
            continue
        if c == '"':
            ins = True
            out.append(c)
            i += 1
            continue
        if x.startswith('//', i):
            while i < len(x) and x[i] != '\n':
                i += 1
            continue
        if x.startswith('/*', i):
            j = x.find('*/', i + 2)
            i = (j + 2) if j >= 0 else len(x)
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def balanco(x):
    x = sem_comentario(x)
    d, ins = 0, False
    for c in x:
        if c == '"':
            ins = not ins
        elif not ins:
            if c in '([{':
                d += 1
            elif c in ')]}':
                d -= 1
                if d < 0:
                    return -1
    return d if not ins else -2


def main():
    falhas = 0
    a, _ = arvore(FONTE)
    b, doc = arvore(SAIDA)
    print('YAML da saída é válido')
    ok = a == b
    falhas += not ok
    print('%s árvore de controles idêntica (%d controles)'
          % ('ok  ' if ok else 'FALHA', len(b)))

    s = io.open(SAIDA, encoding='utf-8').read()
    n = len(EMOJI.findall(s))
    falhas += n != 0
    print('%s nenhum emoji na tela (%d)' % ('ok  ' if n == 0 else 'FALHA', n))

    # aridade das chamadas ao fluxo: o gatilho tem 2 parâmetros
    i, tot, ruins = 0, 0, 0
    while True:
        i = s.find('EnviarAtividadeparachatteams.Run(', i)
        if i < 0:
            break
        j = i + len('EnviarAtividadeparachatteams.Run')
        d, k = 0, j
        while k < len(s):
            if s[k] == '(':
                d += 1
            elif s[k] == ')':
                d -= 1
                if d == 0:
                    break
            k += 1
        corpo, dd, args, ins = s[j + 1:k], 0, 1, False
        for ch in corpo:
            if ch == '"':
                ins = not ins
            elif not ins:
                if ch in '({[':
                    dd += 1
                elif ch in ')}]':
                    dd -= 1
                elif ch == ',' and dd == 0:
                    args += 1
        tot += 1
        ruins += args != 2
        i = k
    falhas += ruins != 0
    print('%s %d chamadas ao fluxo, todas com 2 argumentos (%d erradas)'
          % ('ok  ' if ruins == 0 else 'FALHA', tot, ruins))

    # balanceamento de TODAS as fórmulas da tela
    scr = doc['Screens']['ScreenAcionamentosPlemPrai']
    ruins, chk = [], 0

    def visita(node, path):
        nonlocal chk
        for it in node or []:
            for nm, bd in (it or {}).items():
                for k, v in ((bd or {}).get('Properties') or {}).items():
                    if isinstance(v, str) and v.startswith('='):
                        chk += 1
                        if balanco(v) != 0:
                            ruins.append('%s.%s' % (nm, k))
                visita((bd or {}).get('Children'), path + '/' + nm)
    for k, v in (scr.get('Properties') or {}).items():
        if isinstance(v, str) and v.startswith('='):
            chk += 1
            if balanco(v) != 0:
                ruins.append('Screen.%s' % k)
    visita(scr.get('Children'), '')
    falhas += len(ruins) > 0
    print('%s %d fórmulas balanceadas (%d com problema) %s'
          % ('ok  ' if not ruins else 'FALHA', chk, len(ruins), ruins[:5]))

    # NOMES DESCONHECIDOS: toda fonte de dados (tbl_*) e coleção (col_*) citada
    # tem que existir. Foi assim que o patch B10 quebrou no Studio — ele
    # descomentava código que referenciava tbl_GRUPO_ORDEM, col_grupos_ordem e
    # var_contato_fluxo, e nenhum dos três existe neste app.
    # sem comentários dos dois lados: nome citado só num // ou /* */ não conta
    origem = sem_comentario(io.open(FONTE, encoding='utf-8').read())
    codigo = sem_comentario(s)
    tbls_saida = set(re.findall(r'\btbl_[A-Za-z0-9_]+', codigo))
    # uma fonte de dados é "conhecida" se o export original a usa como
    # DataSource de formulário ou dentro de Filter/LookUp/Sort/Search
    conhecidas = set()
    for t in tbls_saida:
        usos = len(re.findall(r'\b%s\b' % re.escape(t), origem))
        # citada uma única vez no original = provavelmente só dentro de um
        # bloco comentado; não é fonte conectada
        if usos > 1 or re.search(r'DataSource:\s*=%s\b' % re.escape(t), origem):
            conhecidas.add(t)
    orfas_tbl = sorted(tbls_saida - conhecidas)

    cols_saida = set(re.findall(r'\bcol_[A-Za-z0-9_]+', codigo))
    criadas = set(re.findall(r'(?:ClearCollect|Collect)\(\s*(col_[A-Za-z0-9_]+)', codigo))
    criadas |= set(re.findall(r'Items:\s*=(col_[A-Za-z0-9_]+)', codigo))
    orfas_col = sorted(cols_saida - criadas)

    falhas += bool(orfas_tbl or orfas_col)
    print('%s nenhuma fonte/coleção órfã %s'
          % ('ok  ' if not (orfas_tbl or orfas_col) else 'FALHA',
             (orfas_tbl + orfas_col) or ''))

    # PALETA ÚNICA: legenda, pílulas do fluxograma e chips da lista de
    # atividades têm que sair do MESMO dicionário. Foi a queixa do usuário —
    # duas paletas convivendo na mesma tela. Aqui a tela é conferida contra
    # padrao_mensagens_teams.py, que é a fonte de verdade também dos fluxos.
    from padrao_mensagens_teams import SUPERFICIE_APP, rgba
    # rótulo da legenda -> chave do estado
    LEGENDA = {
        'NENHUMA AÇÃO': 'NENHUMA', 'NOTIFICADO': 'NOTIFICADO',
        'ACIONADO': 'ACIONAR', 'CHEGOU': 'CHEGOU', 'SOBREAVISO': 'SOBREAVISO',
        'INFORMADO': 'INFORMAR', 'CONTATO NÃO REALIZADO': 'CONTATO_NR',
    }
    linhas = s.split('\n')
    desvios = []
    vistos = set()
    for i, l in enumerate(linhas):
        m = re.match(r'^\s*- (Label11_\d+):$', l)
        if not m:
            continue
        bloco = linhas[i:i + 30]
        rot = [x.split('="')[1].rstrip('"') for x in bloco
               if x.strip().startswith('Text: ="')]
        if not rot or rot[0] not in LEGENDA:
            continue
        chave = LEGENDA[rot[0]]
        vistos.add(chave)
        fi = [k for k, x in enumerate(bloco) if x.strip().startswith('Fill:')][0]
        ind = len(bloco[fi]) - len(bloco[fi].lstrip())
        fim = fi + 1
        while fim < len(bloco) and (not bloco[fim].strip()
                                    or len(bloco[fim]) - len(bloco[fim].lstrip()) > ind):
            fim += 1
        achado = re.sub(r'\s+', ' ', ' '.join(x.strip() for x in bloco[fi:fim]))
        esperado = rgba(SUPERFICIE_APP[chave])
        if esperado.replace(' ', '') not in achado.replace(' ', ''):
            desvios.append('legenda %s: esperava %s' % (rot[0], esperado))
    faltando = sorted(set(LEGENDA.values()) - vistos)
    if faltando:
        desvios.append('rótulos da legenda não encontrados: %s' % faltando)

    # as pílulas do fluxograma só podem usar cores de SUPERFICIE_APP
    permitidas = {rgba(h).replace(' ', '') for h in set(SUPERFICIE_APP.values())}
    for nome in ('Button1_1', 'Button1_4', 'Button1_7'):
        i = [k for k, x in enumerate(linhas) if x.strip() == '- %s:' % nome][0]
        bloco = linhas[i:i + 130]
        fi = [k for k, x in enumerate(bloco) if x.strip() == 'Fill: |-'][0]
        ind = len(bloco[fi]) - len(bloco[fi].lstrip())
        fim = fi + 1
        while fim < len(bloco) and (not bloco[fim].strip()
                                    or len(bloco[fim]) - len(bloco[fim].lstrip()) > ind):
            fim += 1
        corpo = ' '.join(x.strip() for x in bloco[fi:fim])
        for c in re.findall(r'RGBA\([^)]*\)', corpo):
            if re.sub(r'\s+', '', c) not in permitidas:
                desvios.append('pílula %s usa %s fora da paleta' % (nome, c))

    falhas += bool(desvios)
    print('%s paleta única (legenda = pílulas = padrao_mensagens_teams) %s'
          % ('ok  ' if not desvios else 'FALHA', desvios[:4] or ''))

    print('\n%s' % ('TUDO OK' if not falhas else '%d VERIFICAÇÃO(ÕES) FALHARAM' % falhas))
    return falhas


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
