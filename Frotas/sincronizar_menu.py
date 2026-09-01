# -*- coding: utf-8 -*-
"""O trilho da scrFrotaPainel é o MOLDE — é a versão ajustada no Studio.
Este script copia esse bloco para as outras telas, trocando só o sufixo dos
nomes de controle e o item aceso. Nada de recompor por gerador: qualquer
refinamento visual feito no painel se propaga igual para as demais."""
import os, sys

BASE   = os.path.dirname(os.path.abspath(__file__))
MOLDE  = ('scrFrotaPainel.pa.yaml', 'Pnl', 'cntPainelRaiz')
DESTINO = [('scrFrotaLista.pa.yaml', 'Lst', 'cntListaRaiz',  'btnMenuFrota'),
           ('scrFrotaForm.pa.yaml',  'Frm', 'cntFrmRaiz',    'btnMenuNovo')]
ATIVO_MOLDE = 'btnMenuPainel'
NAV = ('btnMenuPainel', 'btnMenuFrota', 'btnMenuNovo')

def bloco_trilho(arq, suf, raiz):
    s = open(os.path.join(BASE, arq), encoding='utf-8').read()
    i = s.index(f'            - cntMenu{suf}:')
    j = s.index(f'            - {raiz}:')
    return s[i:j]

def acende(bloco, nome, ligado):
    """Troca Appearance/BasePaletteColor apenas dentro do bloco do botão."""
    ini = bloco.index(f'- {nome}')
    resto = bloco[ini + 10:]
    fim = ini + 10 + (resto.index('\n                  - ') if '\n                  - ' in resto else len(resto))
    t = bloco[ini:fim]
    if ligado:
        t = (t.replace("'ButtonCanvas.Appearance'.Secondary", "'ButtonCanvas.Appearance'.Primary")
              .replace("BasePaletteColor: =thmTextoBarra", "BasePaletteColor: =thmPrimaria"))
    else:
        t = (t.replace("'ButtonCanvas.Appearance'.Primary", "'ButtonCanvas.Appearance'.Secondary")
              .replace("BasePaletteColor: =thmPrimaria", "BasePaletteColor: =thmTextoBarra"))
    return bloco[:ini] + t + bloco[fim:]

def sincronizar():
    molde = bloco_trilho(*MOLDE)
    sufm = MOLDE[1]
    for arq, suf, raiz, ativo in DESTINO:
        t = molde.replace(sufm + ':', suf + ':').replace(sufm + '.', suf + '.').replace('Marca' + sufm, 'Marca' + suf)
        assert sufm not in t, [l for l in t.split('\n') if sufm in l][:3]
        for b in NAV:
            t = acende(t, b + suf, b == ativo)
        p = os.path.join(BASE, arq)
        s = open(p, encoding='utf-8').read()
        i = s.index(f'            - cntMenu{suf}:')
        j = s.index(f'            - {raiz}:')
        open(p, 'w', encoding='utf-8').write(s[:i] + t + s[j:])
        print(f'  {arq}: trilho sincronizado com o painel (aceso: {ativo})')

if __name__ == '__main__':
    sincronizar()
