#!/usr/bin/env python3
"""Gera App_Formulas_Mapa.txt (colável) a partir de AppFormulas_Mapa.fx.md.

Regra de seleção: entra todo bloco ```powerfx``` que declare pelo menos uma
named formula (`nome =`) e termine definições com `;;`. Os blocos de exemplo
(seção "Como as telas consomem") e os de App.OnStart/StartScreen ficam de fora
por não atenderem esse critério.

Rodar duas vezes tem que produzir o mesmo hash.
"""
import hashlib
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(BASE, 'AppFormulas_Mapa.fx.md')
SAIDA = os.path.join(BASE, 'App_Formulas_Mapa.txt')

CABECALHO = (
    "// ============================================================================\n"
    "// App.Formulas — Motiva | Mapa de Alocacao de Patio\n"
    "// Colar em: Studio > App > propriedade Formulas   (NAO e o OnStart)\n"
    "// Locale pt-BR: ';' separa argumentos, ';;' termina cada definicao.\n"
    "// Documentacao: AppFormulas_Mapa.fx.md\n"
    "// ============================================================================\n\n"
)

md = open(FONTE, encoding='utf-8').read()
blocos = re.findall(r'```powerfx\n(.*?)```', md, re.S)
selecionados = [b for b in blocos if ';;' in b and re.search(r'^\w+\s*=', b, re.M)]
conteudo = CABECALHO + '\n'.join(b.rstrip() + '\n' for b in selecionados)

nomes = re.findall(r'^(\w+)\s*=', '\n'.join(selecionados), re.M)
if len(nomes) != len(set(nomes)):
    vistos = set()
    dup = {n for n in nomes if n in vistos or vistos.add(n)}
    print(f'ERRO: definição duplicada no .fx.md: {sorted(dup)}')
    sys.exit(1)

open(SAIDA, 'w', encoding='utf-8', newline='\n').write(conteudo)
print(f'{os.path.basename(SAIDA)}: {len(selecionados)} blocos, {len(nomes)} definições, '
      f'sha256 {hashlib.sha256(conteudo.encode()).hexdigest()[:16]}')
