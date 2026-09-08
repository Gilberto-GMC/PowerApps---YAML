# -*- coding: utf-8 -*-
"""O que a tela de origem inicializava ao abrir tem que sobreviver à consolidação.

Navigate() dispara o OnVisible da tela de destino; Set(var_vista, ...) não
dispara nada. Juntar lista + formulário + detalhe numa tela só troca um pelo
outro, então tudo que os OnVisible das telas de origem faziam — carregar as
coleções do detalhe, ligar painéis, travar DisplayMode — evapora sem que
nenhum outro checador perceba: o YAML continua válido, as propriedades
continuam existindo e a galeria continua apontando para uma coleção com o
nome certo. Só que ninguém mais a preenche.

Verifica também que sair do módulo limpa var_redirectAN: frmHome.OnVisible
redireciona de volta enquanto a variável tiver valor, e Param() a mantém pela
sessão inteira.
"""
import sys, os, re, glob
sys.path.insert(0, 'build')
from pautil import split_screen, onvisible_de
from gerar import preparar_init
from modulos import MODULOS

SRC, OUT = "msapp/Src", "out"
erros = []


def ocorrencias(agulha, palheiro):
    """quantas vezes a lista `agulha` aparece contígua dentro de `palheiro`"""
    n, i = 0, 0
    while i + len(agulha) <= len(palheiro):
        if palheiro[i:i + len(agulha)] == agulha:
            n += 1
            i += len(agulha)
        else:
            i += 1
    return n


# ── 1. inicialização das visões consolidadas ────────────────────────────────
#    O corpo do OnVisible de origem tem que aparecer inteiro em CADA ponto que
#    entra na visão — não basta aparecer uma vez.
for m in MODULOS:
    novo = open(f"{OUT}/{m['nova']}.pa.yaml", encoding='utf-8').read()
    # a indentação muda conforme o ponto de injeção, e o ';' final aparece só
    # quando ainda vem alguma instrução depois — a comparação ignora os dois
    achatado = [l.strip().rstrip(';') for l in novo.split('\n')]
    for chave, vista in (('forms', 'form'), ('det', 'detalhe')):
        _, props, _ = split_screen(f"{SRC}/{m[chave]}.pa.yaml")
        corpo = onvisible_de(props)
        if not corpo:
            continue
        alvo = [l.strip().rstrip(';') for l in preparar_init(corpo, vista).split('\n')]
        entradas = len(re.findall(r'Set\(\s*\n\s*var_vista,\s*\n\s*"' + vista + r'"', novo))
        achou = ocorrencias(alvo, achatado)
        if achou == 0:
            erros.append(f"[{m['key']}/{vista}] o OnVisible de {m[chave]} sumiu na "
                         f"consolidação — a visão abre sem coleção e sem estado")
        elif achou < entradas:
            erros.append(f"[{m['key']}/{vista}] {entradas} pontos entram na visão mas "
                         f"só {achou} repõem o init de {m[chave]}")


# ── 2. toda saída para frmHome limpa o redirect de deep link ────────────────
for path in sorted(glob.glob(f"{OUT}/*.pa.yaml")):
    txt = open(path, encoding='utf-8').read()
    for mt in re.finditer(r'Navigate\(\s*\n?\s*frmHome', txt):
        antes = txt[max(0, mt.start() - 200):mt.start()]
        if 'var_redirectAN' not in antes:
            linha = txt[:mt.start()].count('\n') + 1
            erros.append(f"{os.path.basename(path)}:{linha} Navigate(frmHome) sem "
                         f"Set(var_redirectAN, Blank()) — laço com frmHome.OnVisible")


# ── 3. nenhum módulo limpa coleção filha de outro ───────────────────────────
for m in MODULOS:
    txt = open(f"{OUT}/{m['nova']}.pa.yaml", encoding='utf-8').read()
    for outro in MODULOS:
        if outro['key'] == m['key']:
            continue
        for col in outro['filhos']:
            if col in m['filhos']:
                continue
            if re.search(r'Clear\(\s*' + re.escape(col) + r'\s*\)', txt):
                erros.append(f"[{m['key']}] Clear({col}) — coleção de {outro['key']}")


if erros:
    print("\n".join("✗ " + e for e in erros))
    sys.exit(1)
print(f"   ✓ init das visões, saída para frmHome e coleções filhas conferidos "
      f"em {len(MODULOS)} módulos")
