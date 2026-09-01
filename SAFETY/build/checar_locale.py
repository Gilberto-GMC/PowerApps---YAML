# -*- coding: utf-8 -*-
"""Guarda de locale — obrigatória em toda entrega Power Apps.

Regra: o DESTINO decide o formato.
  .txt de barra de fórmulas -> pt-BR      (";" args, ";;" encadeia, "," decimal)
  .pa.yaml exibição código  -> invariante ("," args, ";" encadeia, "." decimal)
"""
import sys, os, glob, re
sys.path.insert(0, os.path.dirname(__file__))
from ptbr import conferir_ptbr, conferir_roundtrip

AVISO = 'LOCALE'
erros = []
avisos = []

# 1. todo .txt de barra de fórmulas está em pt-BR
for f in sorted(glob.glob('out/*ptBR*.txt')):
    txt = open(f, encoding='utf-8').read()
    p = conferir_ptbr(txt)
    if p:
        for num, tipo, linha in p[:5]:
            erros.append(f"{f}: linha {num} — {tipo} -> {linha}")
    else:
        print(f"   ✓ {f} em pt-BR")

# 2. existe um .txt pt-BR para cada propriedade de barra de fórmulas entregue
for prop, alvo in (('OnStart', 'out/01_App_OnStart_ptBR.txt'),
                   ('Formulas', 'out/02_App_Formulas_ptBR.txt')):
    if not os.path.exists(alvo):
        erros.append(f"App.{prop} entregue sem versão pt-BR pronta para colar ({alvo})")

# 3. o pt-BR do OnStart corresponde exatamente ao .pa.yaml (ida e volta)
sys.path.insert(0, os.path.dirname(__file__))
from gerar_ptbr import extrair_onstart
difs = conferir_roundtrip(extrair_onstart('out/01_App.pa.yaml'))
if difs:
    erros.append(f"OnStart pt-BR não bate com o invariante em {len(difs)} linha(s)")
else:
    print("   ✓ OnStart pt-BR ⇄ invariante idênticos na ida e volta")

# 4. todo .pa.yaml continua invariante e avisa disso no cabeçalho
for f in sorted(glob.glob('out/*.pa.yaml')):
    txt = open(f, encoding='utf-8').read()
    cab = '\n'.join(l for l in txt.split('\n')[:40] if l.lstrip().startswith('#'))
    if AVISO not in cab:
        erros.append(f"{f}: cabeçalho sem o aviso de locale")
    corpo = '\n'.join(l for l in txt.split('\n') if not l.lstrip().startswith('#'))
    # Power Fx desativado (// e /* */) não é código: o Studio não compila.
    # É onde sobra pt-BR colado por engano em algum momento do passado.
    ativo = re.sub(r'/\*.*?\*/', ' ', corpo, flags=re.S)
    ativo = re.sub(r'//[^\\\n]*', ' ', ativo)
    if re.search(r'(?<!;);;(?!;)', ativo):
        erros.append(f"{f}: contém ';;' em código ativo — convertido para pt-BR por engano")
    elif re.search(r'(?<!;);;(?!;)', corpo):
        avisos.append(f"{f}: há Power Fx em pt-BR dentro de comentário (herdado do export original, inofensivo)")
print(f"   ✓ {len(glob.glob('out/*.pa.yaml'))} .pa.yaml em invariante, com aviso no cabeçalho")

for a in avisos:
    print("   ! " + a)
if erros:
    print("\n".join("   ✗ " + e for e in erros))
    sys.exit(1)
