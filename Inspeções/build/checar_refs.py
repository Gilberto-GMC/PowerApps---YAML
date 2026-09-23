# -*- coding: utf-8 -*-
"""Toda tela referenciada em Navigate/col_NavTelas/ScreenNavigator tem que existir
no app final (originais − removidas ∪ entregues).

Importável: outros checadores leem TELAS_REMOVIDAS daqui sem disparar a checagem."""
import re, glob, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from valida import carregar
from checar_cross_screen import mascarar, texto_sem_cabecalho

# telas que a entrega manda excluir no Studio (passo manual do LEIA-ME)
TELAS_REMOVIDAS = {'frmApontFauna', 'ScreenConsultarV1', 'frmRelatorioZPA_1', 'Screen1'}


def main():
    entregues = set()
    for f in glob.glob('out/*.pa.yaml'):
        d = carregar(f)
        if isinstance(d, dict) and 'Screens' in d:
            entregues |= set(d['Screens'])
    originais = {os.path.basename(p)[:-len('.pa.yaml')] for p in glob.glob('msapp/Src/*.pa.yaml')}
    originais -= {'App', '_EditorState'}
    existentes = (originais - TELAS_REMOVIDAS) | entregues
    pasta = 'out'
    if '--baseline' in sys.argv:
        pasta = 'msapp/Src'; existentes = originais
    print(f"   {len(existentes)} telas existirão no app")

    faltando = {}
    for f in sorted(glob.glob(f'{pasta}/*.pa.yaml')):
        txt = mascarar(texto_sem_cabecalho(f))
        refs = set()
        for m in re.finditer(r'\bNavigate\(\s*([A-Za-z_]\w*)', txt):
            refs.add(m.group(1))
        for m in re.finditer(r'\bTelaListar:\s*([A-Za-z_]\w*)', txt):
            refs.add(m.group(1))
        for m in re.finditer(r'\bScreenNavigator:\s*=?\s*([A-Za-z_]\w*)', txt):
            refs.add(m.group(1))
        ruins = {r for r in refs if r not in existentes and not r.startswith('var') and r not in ('Self', 'Parent')}
        if ruins:
            faltando[os.path.basename(f)] = sorted(ruins)
    if faltando:
        for arq, r in faltando.items():
            print(f"   ✗ {arq}: referencia tela inexistente -> {', '.join(r)}")
        sys.exit(1)
    print("   ✓ nenhuma referência a tela inexistente")


if __name__ == '__main__':
    main()
