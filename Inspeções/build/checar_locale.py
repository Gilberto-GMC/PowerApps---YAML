# -*- coding: utf-8 -*-
"""Guarda de locale — obrigatória em toda entrega Power Apps.

Regra: o DESTINO decide o formato.
  .txt de barra de fórmulas -> pt-BR      (";" args, ";;" encadeia, "," decimal)
  .pa.yaml exibição código  -> invariante ("," args, ";" encadeia, "." decimal)
"""
import sys, os, glob, re
sys.path.insert(0, os.path.dirname(__file__))
from ptbr import conferir_ptbr, conferir_roundtrip
from gerar_ptbr import extrair_prop

AVISO = 'LOCALE'
erros, avisos = [], []

for f in sorted(glob.glob('out/*ptBR*.txt')):
    p = conferir_ptbr(open(f, encoding='utf-8').read())
    if p:
        for num, tipo, linha in p[:5]:
            erros.append(f"{f}: linha {num} — {tipo} -> {linha}")
    else:
        print(f"   ✓ {f} em pt-BR")

if os.path.exists('out/_App_Formulas_invariante.fx'):
    fx = open('out/_App_Formulas_invariante.fx', encoding='utf-8').read().strip('\n')
    if not os.path.exists('out/02_App_Formulas_ptBR.txt'):
        erros.append("App.Formulas entregue sem versão pt-BR (out/02_App_Formulas_ptBR.txt)")
    elif conferir_roundtrip(fx):
        erros.append("App.Formulas pt-BR não bate com o invariante")
    else:
        print("   ✓ App.Formulas pt-BR ⇄ invariante idênticos na ida e volta")

if os.path.exists('out/01_App.pa.yaml'):
    for prop, alvo in (('OnStart', 'out/01_App_OnStart_ptBR.txt'), ('Formulas', 'out/02_App_Formulas_ptBR.txt')):
        fx = extrair_prop('out/01_App.pa.yaml', prop)
        if fx is None:
            continue
        if not os.path.exists(alvo):
            erros.append(f"App.{prop} entregue sem versão pt-BR pronta para colar ({alvo})")
            continue
        difs = conferir_roundtrip(fx)
        if difs:
            erros.append(f"App.{prop} pt-BR não bate com o invariante em {len(difs)} linha(s)")
        else:
            print(f"   ✓ App.{prop} pt-BR ⇄ invariante idênticos na ida e volta")

for f in sorted(glob.glob('out/*.pa.yaml') + glob.glob('out/Components/*.pa.yaml')):
    txt = open(f, encoding='utf-8').read()
    cab = '\n'.join(l for l in txt.split('\n')[:40] if l.lstrip().startswith('#'))
    if AVISO not in cab:
        erros.append(f"{f}: cabeçalho sem o aviso de locale")
    corpo = '\n'.join(l for l in txt.split('\n') if not l.lstrip().startswith('#'))
    ativo = re.sub(r'/\*.*?\*/', ' ', corpo, flags=re.S)
    ativo = re.sub(r'//[^\\\n]*', ' ', ativo)
    if re.search(r'(?<!;);;(?!;)', ativo):
        erros.append(f"{f}: contém ';;' em código ativo — convertido para pt-BR por engano")
    elif re.search(r'(?<!;);;(?!;)', corpo):
        avisos.append(f"{f}: há Power Fx em pt-BR dentro de comentário (herdado do export, inofensivo)")
print(f"   ✓ {len(glob.glob('out/*.pa.yaml'))} .pa.yaml em invariante, com aviso no cabeçalho")
for a in avisos:
    print("   ! " + a)
if erros:
    print("\n".join("   ✗ " + e for e in erros))
    sys.exit(1)
