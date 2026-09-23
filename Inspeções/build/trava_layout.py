# -*- coding: utf-8 -*-
"""Trava de layout: prova que a entrega não mexeu no que o usuário vê.

Compara, tela a tela, a árvore de controles de msapp/Src (origem) com a de out/
(entrega): nomes, tipos, ordem e as propriedades visuais listadas em VISUAIS.
Qualquer diferença fora das exceções declaradas reprova. Exceção declarada que
não ocorreu também reprova (pega cirurgia que virou no-op).

Diff por Counter, nunca por lista ordenada (lição 2026-08-24).

Uso:
    python build/trava_layout.py              # compara out/*.pa.yaml com msapp/Src
    python build/trava_layout.py --autoteste  # compara msapp/Src consigo mesmo (0 diffs)

Exceções: out/_excecoes_layout.json, escrito pelo gerador:
    {"somem": [["frmHome", "NavInspecao_1"], ...],
     "surgem": [["frmHomePatio", "cmpSyncPatio"], ...],
     "mudam": [["frmHomePatio", "Label9_15", "Text"], ...]}
"""
import sys, os, glob, json, collections
sys.path.insert(0, os.path.dirname(__file__))
from valida import carregar

# Propriedades que definem o que o usuário vê. Fórmulas de comportamento
# (OnSelect, OnVisible, Items, Default, DisplayMode...) ficam fora: são o
# objeto das cirurgias. Text e Visible entram porque mudam o que se vê.
VISUAIS = {
    'X', 'Y', 'Width', 'Height', 'FillPortions', 'AlignInContainer',
    'LayoutDirection', 'LayoutAlignItems', 'LayoutJustifyContent', 'LayoutWrap',
    'LayoutGap', 'LayoutMinWidth', 'LayoutMinHeight', 'LayoutMaxWidth', 'LayoutMaxHeight',
    'LayoutOverflowX', 'LayoutOverflowY', 'LayoutMode',
    'PaddingTop', 'PaddingBottom', 'PaddingLeft', 'PaddingRight',
    'Fill', 'Color', 'BorderColor', 'BorderStyle', 'BorderThickness',
    'RadiusTopLeft', 'RadiusTopRight', 'RadiusBottomLeft', 'RadiusBottomRight',
    'Font', 'FontWeight', 'Italic', 'Underline', 'Strikethrough', 'Size', 'Align', 'VerticalAlign',
    'HoverFill', 'HoverColor', 'HoverBorderColor', 'PressedFill', 'PressedColor',
    'PressedBorderColor', 'DisabledFill', 'DisabledColor', 'DisabledBorderColor',
    'Image', 'ImagePosition', 'Icon', 'Rotation', 'Transparency', 'DropShadow',
    'Text', 'Visible', 'HintText', 'Appearance', 'TemplateSize', 'TemplatePadding',
    'WrapCount', 'ShowScrollbar', 'Layout', 'NumberOfColumns', 'Variant',
}

def _arvore(node, caminho, saida, tela):
    """percorre Children recursivamente; saida[(tela, caminho)] = (Control, {prop: valor})"""
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and len(item) == 1:
                nome = list(item)[0]
                corpo = item[nome]
                if isinstance(corpo, dict) and 'Control' in corpo:
                    ctrl = corpo.get('Control')
                    if corpo.get('Variant'):
                        ctrl = f"{ctrl}|{corpo['Variant']}"
                    props = corpo.get('Properties') or {}
                    vis = {k: str(v) for k, v in props.items() if k in VISUAIS}
                    saida[(tela, caminho + (nome,))] = (ctrl, vis)
                    _arvore(corpo.get('Children'), caminho + (nome,), saida, tela)
                else:
                    _arvore(corpo, caminho, saida, tela)
            else:
                _arvore(item, caminho, saida, tela)


def carregar_tela(path):
    d = carregar(path)
    if not (isinstance(d, dict) and 'Screens' in d):
        return None, {}
    tela = list(d['Screens'])[0]
    corpo = d['Screens'][tela] or {}
    saida = {}
    _arvore(corpo.get('Children'), (), saida, tela)
    return tela, saida


def comparar(orig, novo, excecoes):
    """devolve lista de problemas (str). excecoes: dict somem/surgem/mudam."""
    problemas = []
    somem = {tuple(x) for x in excecoes.get('somem', [])}
    surgem = {tuple(x) for x in excecoes.get('surgem', [])}
    mudam = {tuple(x) for x in excecoes.get('mudam', [])}
    usadas = set()

    chaves_o = set(orig); chaves_n = set(novo)
    for (tela, cam) in sorted(chaves_o - chaves_n):
        chave = (tela, cam[-1])
        # controle removido: ok se ele ou um ancestral estiver em "somem"
        if any((tela, a) in somem for a in cam):
            usadas |= {(tela, a) for a in cam if (tela, a) in somem}
            continue
        problemas.append(f"{tela}: controle SUMIU sem exceção declarada -> {'/'.join(cam)}")
    for (tela, cam) in sorted(chaves_n - chaves_o):
        if any((tela, a) in surgem for a in cam):
            usadas |= {(tela, a) for a in cam if (tela, a) in surgem}
            continue
        problemas.append(f"{tela}: controle SURGIU sem exceção declarada -> {'/'.join(cam)}")

    # ordem dos irmãos: o Studio desenha na ordem de Children
    def irmaos(d):
        pais = collections.defaultdict(list)
        for (tela, cam) in d:
            pais[(tela, cam[:-1])].append(cam[-1])
        return pais
    io, inn = irmaos(orig), irmaos(novo)
    for pai in io:
        a = [x for x in io[pai] if (pai[0], pai[1] + (x,)) in novo]
        b = [x for x in inn.get(pai, []) if (pai[0], pai[1] + (x,)) in orig]
        if a != b:
            problemas.append(f"{pai[0]}: ORDEM dos filhos mudou em {'/'.join(pai[1]) or '<raiz>'}")

    for chave in sorted(chaves_o & chaves_n):
        tela, cam = chave
        (co, po), (cn, pn) = orig[chave], novo[chave]
        if co != cn:
            problemas.append(f"{tela}: {'/'.join(cam)} mudou de tipo {co} -> {cn}")
        # Counter das propriedades visuais
        dif_o = collections.Counter(po.items()) - collections.Counter(pn.items())
        dif_n = collections.Counter(pn.items()) - collections.Counter(po.items())
        props = {k for k, _ in dif_o} | {k for k, _ in dif_n}
        for p in sorted(props):
            exc = (tela, cam[-1], p)
            if exc in mudam:
                usadas.add(exc)
                continue
            problemas.append(f"{tela}: {'/'.join(cam)}.{p}: {po.get(p, '<ausente>')!r} -> {pn.get(p, '<ausente>')!r}")

    for exc in sorted((somem | surgem | mudam) - usadas):
        problemas.append(f"exceção declarada que NÃO ocorreu: {exc}")
    return problemas


def main():
    autoteste = '--autoteste' in sys.argv
    origem = {}
    for p in glob.glob('msapp/Src/*.pa.yaml'):
        tela, arv = carregar_tela(p)
        if tela:
            origem.update(arv)
    if autoteste:
        problemas = comparar(origem, dict(origem), {})
        print(f"   autoteste: {len(origem)} controles, {len(problemas)} diferenças (esperado 0)")
        sys.exit(1 if problemas else 0)

    arquivos = [f for f in sorted(glob.glob('out/*.pa.yaml'))]
    if not arquivos:
        print("   (out/ sem telas — nada a comparar)")
        return
    exc_path = 'out/_excecoes_layout.json'
    excecoes = json.load(open(exc_path, encoding='utf-8')) if os.path.exists(exc_path) else {}
    novo = {}; telas_entregues = set()
    for f in arquivos:
        tela, arv = carregar_tela(f)
        if tela:
            novo.update(arv); telas_entregues.add(tela)
    # só compara as telas entregues
    orig_sub = {k: v for k, v in origem.items() if k[0] in telas_entregues}
    exc_sub = {g: [x for x in excecoes.get(g, []) if x[0] in telas_entregues] for g in ('somem', 'surgem', 'mudam')}
    problemas = comparar(orig_sub, novo, exc_sub)
    n_exc = sum(len(v) for v in exc_sub.values())
    if problemas:
        for p in problemas[:80]:
            print("   ✗ " + p)
        if len(problemas) > 80:
            print(f"   ... e mais {len(problemas) - 80}")
        sys.exit(1)
    print(f"   ✓ layout idêntico em {len(telas_entregues)} telas ({len(novo)} controles), {n_exc} exceções declaradas e confirmadas")


if __name__ == '__main__':
    main()
