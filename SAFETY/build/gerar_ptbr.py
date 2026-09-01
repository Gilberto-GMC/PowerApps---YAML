# -*- coding: utf-8 -*-
"""Gera os snippets de BARRA DE FÓRMULAS (pt-BR) a partir dos .pa.yaml."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from ptbr import para_ptbr, conferir_ptbr, conferir_roundtrip

CAB = '''// ══════════════════════════════════════════════════════════════════════════════
// AirportNow — Safety & Fauna  ·  App.OnStart
// ══════════════════════════════════════════════════════════════════════════════
// LOCALE pt-BR — este arquivo é para a BARRA DE FÓRMULAS.
//   ";"  separa argumentos          (invariante usa ",")
//   ";;" encadeia/termina instrução (invariante usa ";")
//   ","  é o separador decimal      (invariante usa ".")
//
// COLAR EM: Studio > árvore de controles > App > propriedade "OnStart".
//
// NÃO cole este conteúdo na exibição de código (.pa.yaml). Lá o Studio lê e
// grava sempre no formato INVARIANTE, mesmo com o Studio em pt-BR — a versão
// invariante correspondente está em 01_App.pa.yaml e as duas dizem a mesma coisa.
//
// PRÉ-REQUISITO: colar antes o App.Formulas (02_App_Formulas_ptBR.txt), que
// define nfAeros, nfBlocos, nfDataPiso e os tokens de cor.
// ══════════════════════════════════════════════════════════════════════════════

'''


def extrair_onstart(path):
    linhas = open(path, encoding='utf-8').read().split('\n')
    for i, l in enumerate(linhas):
        if re.match(r'^\s*OnStart: \|', l):
            base = len(l) - len(l.lstrip())
            corpo = []
            for s in linhas[i + 1:]:
                if not s.strip():
                    corpo.append('')
                    continue
                if (len(s) - len(s.lstrip())) <= base:
                    break
                corpo.append(s[base + 2:])
            while corpo and not corpo[-1].strip():
                corpo.pop()
            txt = '\n'.join(corpo)
            return txt[1:] if txt.startswith('=') else txt
    raise SystemExit(f"OnStart não encontrado em {path}")


if __name__ == '__main__':
    fx = extrair_onstart('out/01_App.pa.yaml')
    ptbr = para_ptbr(fx)
    destino = 'out/01_App_OnStart_ptBR.txt'
    open(destino, 'w', encoding='utf-8').write(CAB + ptbr + '\n')

    print(f"{destino}  ({len(ptbr.splitlines())} linhas)")

    difs = conferir_roundtrip(fx)
    if difs:
        for num, a, b in difs[:10]:
            print(f"   ✗ ida e volta divergiu na linha {num}:\n       origem: {a}\n       volta : {b}")
        sys.exit(1)
    print("   ✓ ida e volta idêntica ao invariante (nenhum separador perdido ou inventado)")

    problemas = conferir_ptbr(ptbr)
    if problemas:
        for num, tipo, linha in problemas[:20]:
            print(f"   ✗ linha {num}: {tipo} -> {linha}")
        sys.exit(1)
    print("   ✓ nenhuma vírgula separadora sobrou")

    # o App.Formulas foi escrito à mão em pt-BR: confere pela mesma régua
    form = open('out/02_App_Formulas_ptBR.txt', encoding='utf-8').read()
    p2 = conferir_ptbr(form)
    print("out/02_App_Formulas_ptBR.txt")
    if p2:
        for num, tipo, linha in p2[:20]:
            print(f"   ✗ linha {num}: {tipo} -> {linha}")
        sys.exit(1)
    print("   ✓ nenhum separador invariante fora de string/comentário")
