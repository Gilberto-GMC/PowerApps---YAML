# -*- coding: utf-8 -*-
"""Gera os snippets de BARRA DE FÓRMULAS (pt-BR) a partir de out/01_App.pa.yaml.

O destino decide o formato (lição 2026-08-29): o .txt vai para a barra de
fórmulas em pt-BR; o .pa.yaml fica invariante. A conversão é por script, com
prova de ida e volta."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from ptbr import para_ptbr, conferir_ptbr, conferir_roundtrip

CAB_ONSTART = '''// ══════════════════════════════════════════════════════════════════════════════
// AirportNow — {PROJETO}  ·  App.OnStart
// ══════════════════════════════════════════════════════════════════════════════
// LOCALE pt-BR — este arquivo é para a BARRA DE FÓRMULAS.
//   ";"  separa argumentos          (invariante usa ",")
//   ";;" encadeia/termina instrução (invariante usa ";")
//   ","  é o separador decimal      (invariante usa ".")
//
// COLAR EM: Studio > árvore de controles > App > propriedade "OnStart".
//
// NÃO cole este conteúdo na exibição de código (.pa.yaml). Lá o Studio lê e
// grava sempre no formato INVARIANTE — a versão invariante correspondente está
// em 01_App.pa.yaml e as duas dizem a mesma coisa. Use um OU o outro.
//
{PREREQ}// ══════════════════════════════════════════════════════════════════════════════

'''

CAB_FORMULAS = '''// ══════════════════════════════════════════════════════════════════════════════
// AirportNow — {PROJETO}  ·  App.Formulas
// ══════════════════════════════════════════════════════════════════════════════
// LOCALE pt-BR — barra de fórmulas: ";" separa argumentos, ";;" encadeia.
// COLAR EM: Studio > App > propriedade "Formulas" (substituir tudo).
// Colar ANTES de qualquer tela: named formula ausente derruba a tela inteira
// com dezenas de erros longe da causa (lição 2026-08-25).
// ══════════════════════════════════════════════════════════════════════════════

'''


def extrair_prop(path, prop):
    """corpo (invariante, sem '=') de uma propriedade em bloco '|' do App.pa.yaml"""
    linhas = open(path, encoding='utf-8').read().split('\n')
    for i, l in enumerate(linhas):
        if re.match(r'^\s*' + prop + r': \|', l):
            base = len(l) - len(l.lstrip())
            corpo = []
            for s in linhas[i + 1:]:
                if not s.strip():
                    # linha só de espaços: o que passa da indentação do bloco é conteúdo
                    corpo.append(s[base + 2:]); continue
                if (len(s) - len(s.lstrip())) <= base:
                    break
                corpo.append(s[base + 2:])
            while corpo and not corpo[-1].strip():
                corpo.pop()
            txt = '\n'.join(corpo)
            return txt[1:] if txt.startswith('=') else txt
    return None


def extrair_onstart(path):
    txt = extrair_prop(path, 'OnStart')
    if txt is None:
        raise SystemExit(f"OnStart não encontrado em {path}")
    return txt


def gerar(prop, destino, cab, obrigatorio):
    fx = extrair_prop('out/01_App.pa.yaml', prop)
    if fx is None:
        if obrigatorio:
            raise SystemExit(f"App.{prop} não encontrado em out/01_App.pa.yaml")
        return
    ptbr = para_ptbr(fx)
    open(destino, 'w', encoding='utf-8', newline='\n').write(cab + ptbr + '\n')
    print(f"{destino}  ({len(ptbr.splitlines())} linhas)")
    difs = conferir_roundtrip(fx)
    if difs:
        for num, a, b in difs[:10]:
            print(f"   ✗ ida e volta divergiu na linha {num}:\n       origem: {a}\n       volta : {b}")
        sys.exit(1)
    print("   ✓ ida e volta idêntica ao invariante")
    problemas = conferir_ptbr(ptbr)
    if problemas:
        for num, tipo, linha in problemas[:20]:
            print(f"   ✗ linha {num}: {tipo} -> {linha}")
        sys.exit(1)
    print("   ✓ nenhuma vírgula separadora sobrou")


def gerar_de_fx(origem, destino, cab):
    """converte um arquivo invariante (.fx) para pt-BR, com prova de ida e volta"""
    fx = open(origem, encoding='utf-8').read().strip('\n')
    ptbr = para_ptbr(fx)
    open(destino, 'w', encoding='utf-8', newline='\n').write(cab + ptbr + '\n')
    print(f"{destino}  ({len(ptbr.splitlines())} linhas)")
    difs = conferir_roundtrip(fx)
    if difs:
        for num, a, b in difs[:10]:
            print(f"   ✗ ida e volta divergiu na linha {num}:\n       origem: {a}\n       volta : {b}")
        sys.exit(1)
    print("   ✓ ida e volta idêntica ao invariante")
    problemas = conferir_ptbr(ptbr)
    if problemas:
        for num, tipo, linha in problemas[:20]:
            print(f"   ✗ linha {num}: {tipo} -> {linha}")
        sys.exit(1)
    print("   ✓ nenhuma vírgula separadora sobrou")


if __name__ == '__main__':
    # nome do projeto no cabeçalho (entregar.sh do projeto exporta PROJETO_NOME)
    _proj = os.environ.get('PROJETO_NOME', 'Inspeções')
    _tem_formulas = os.path.exists('out/_App_Formulas_invariante.fx')
    _prereq = '// PRÉ-REQUISITO: colar antes o App.Formulas (02_App_Formulas_ptBR.txt).\n'
    CAB_ONSTART = CAB_ONSTART.replace('{PROJETO}', _proj).replace('{PREREQ}', _prereq if _tem_formulas else '')
    CAB_FORMULAS = CAB_FORMULAS.replace('{PROJETO}', _proj)
    if not os.path.exists('out/01_App.pa.yaml'):
        print("   (out/01_App.pa.yaml ausente: App não faz parte deste lote — nada a converter)")
        sys.exit(0)
    gerar('OnStart', 'out/01_App_OnStart_ptBR.txt', CAB_ONSTART, True)
    if os.path.exists('out/_App_Formulas_invariante.fx'):
        gerar_de_fx('out/_App_Formulas_invariante.fx', 'out/02_App_Formulas_ptBR.txt', CAB_FORMULAS)
    else:
        gerar('Formulas', 'out/02_App_Formulas_ptBR.txt', CAB_FORMULAS, False)
