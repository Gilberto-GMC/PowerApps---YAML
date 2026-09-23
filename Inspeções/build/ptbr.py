# -*- coding: utf-8 -*-
"""Converte Power Fx do formato invariante para o locale pt-BR do Studio.

Regras (barra de fórmulas pt-BR):
    ,  separador de argumentos   ->  ;
    ;  encadeador de instruções  ->  ;;
    .  decimal entre dígitos     ->  ,

Nada é convertido dentro de string literal nem dentro de comentário
(// até o fim da linha, /* */ em bloco) — comentário em português tem
vírgula em prosa e não pode virar separador.
"""
import re


def para_ptbr(fx: str) -> str:
    saida = []
    i, n = 0, len(fx)
    aspa = None
    while i < n:
        c = fx[i]

        if aspa:                                   # dentro de string
            saida.append(c)
            if c == aspa:
                # "" escapado dentro de string
                if fx[i + 1:i + 2] == aspa:
                    saida.append(aspa)
                    i += 2
                    continue
                aspa = None
            i += 1
            continue

        if c in '"\'':                             # abre string
            aspa = c
            saida.append(c)
            i += 1
            continue

        if c == '/' and fx[i + 1:i + 2] == '/':    # comentário de linha
            fim = fx.find('\n', i)
            fim = n if fim < 0 else fim
            saida.append(fx[i:fim])
            i = fim
            continue

        if c == '/' and fx[i + 1:i + 2] == '*':    # comentário de bloco
            fim = fx.find('*/', i + 2)
            fim = n if fim < 0 else fim + 2
            saida.append(fx[i:fim])
            i = fim
            continue

        if c == ',':
            saida.append(';')
            i += 1
            continue

        if c == ';':
            saida.append(';;')
            i += 1
            continue

        if c == '.' and fx[i - 1:i].isdigit() and fx[i + 1:i + 2].isdigit():
            saida.append(',')
            i += 1
            continue

        saida.append(c)
        i += 1
    return ''.join(saida)


def para_invariante(fx: str) -> str:
    """Volta de pt-BR para invariante. Serve para provar, por ida e volta, que a
    conversão não perdeu nem inventou separador."""
    saida = []
    i, n = 0, len(fx)
    aspa = None
    while i < n:
        c = fx[i]

        if aspa:
            saida.append(c)
            if c == aspa:
                if fx[i + 1:i + 2] == aspa:
                    saida.append(aspa)
                    i += 2
                    continue
                aspa = None
            i += 1
            continue

        if c in '"\'':
            aspa = c
            saida.append(c)
            i += 1
            continue

        if c == '/' and fx[i + 1:i + 2] == '/':
            fim = fx.find('\n', i)
            fim = n if fim < 0 else fim
            saida.append(fx[i:fim])
            i = fim
            continue

        if c == '/' and fx[i + 1:i + 2] == '*':
            fim = fx.find('*/', i + 2)
            fim = n if fim < 0 else fim + 2
            saida.append(fx[i:fim])
            i = fim
            continue

        if c == ';':
            if fx[i + 1:i + 2] == ';':
                saida.append(';')
                i += 2
            else:
                saida.append(',')
                i += 1
            continue

        if c == ',' and fx[i - 1:i].isdigit() and fx[i + 1:i + 2].isdigit():
            saida.append('.')
            i += 1
            continue

        saida.append(c)
        i += 1
    return ''.join(saida)


def conferir_ptbr(fx: str):
    """Confere um texto que deve estar em pt-BR.

    Só a vírgula é verificável por varredura: fora de string, comentário e
    decimal, ela não existe em pt-BR. O ";" NÃO é verificável assim — ";" simples
    é separador de argumento legítimo e ";;" é encadeador; distinguir os dois exige
    analisar a fórmula. Para isso existe a prova de ida e volta em conferir_roundtrip.
    """
    problemas = []
    for num, linha in enumerate(fx.split('\n'), 1):
        limpa, aspa, j = [], None, 0
        while j < len(linha):
            c = linha[j]
            if aspa:
                if c == aspa:
                    aspa = None
                limpa.append(' ')
                j += 1
                continue
            if c in '"\'':
                aspa = c
                limpa.append(' ')
                j += 1
                continue
            if c == '/' and linha[j + 1:j + 2] == '/':
                break
            limpa.append(' ' if (c == ',' and linha[j-1:j].isdigit() and linha[j+1:j+2].isdigit()) else c)
            j += 1
        if ',' in ''.join(limpa):
            problemas.append((num, 'vírgula como separador (invariante)', linha.strip()))
    return problemas


def conferir_roundtrip(invariante: str):
    """pt-BR -> invariante tem que devolver exatamente o texto de origem."""
    volta = para_invariante(para_ptbr(invariante))
    if volta == invariante:
        return []
    orig = invariante.split('\n')
    novo = volta.split('\n')
    difs = []
    for i in range(max(len(orig), len(novo))):
        a = orig[i] if i < len(orig) else '<ausente>'
        b = novo[i] if i < len(novo) else '<ausente>'
        if a != b:
            difs.append((i + 1, a.strip(), b.strip()))
    return difs
