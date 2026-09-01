# -*- coding: utf-8 -*-
"""Remove o shell + trilho de uma tela, devolvendo o container raiz ao topo.
Usado quando o export do Studio volta com o trilho renomeado (cntMenuPnl_1)."""
import re, os, sys
BASE = os.path.dirname(os.path.abspath(__file__))

def desfazer(arq):
    p = os.path.join(BASE, arq)
    s = open(p, encoding='utf-8').read()
    if '- cntShell' not in s:
        print(f'  {arq}: sem shell, nada a fazer'); return
    i = s.index('      - cntShell')
    m = re.search(r'\n            - (cnt\w+Raiz):\n', s[i:])
    j = i + m.start() + 1
    corpo = s[j:]
    corpo = "\n".join(l[6:] if l.startswith("      ") else l for l in corpo.split("\n"))
    # devolve as propriedades de tamanho do container raiz
    k = corpo.index("\n          Properties:\n") + len("\n          Properties:\n")
    fim = corpo.index("\n          Children:") + 1
    props = corpo[k:fim]
    props = props.replace("            AlignInContainer: =AlignInContainer.Stretch\n", "")
    props = props.replace("            FillPortions: =1\n", "            Height: =Parent.Height\n")
    if "Height: =Parent.Height" not in props:
        props = "            Height: =Parent.Height\n" + props
    if "Width: =Parent.Width" not in props:
        props = props + "            Width: =Parent.Width\n"
    open(p, 'w', encoding='utf-8').write(s[:i] + corpo[:k] + props + corpo[fim:])
    print(f'  {arq}: shell removido, {m.group(1)} de volta ao topo')

if __name__ == '__main__':
    for a in (sys.argv[1:] or ['scrFrotaPainel.pa.yaml','scrFrotaLista.pa.yaml','scrFrotaForm.pa.yaml']):
        desfazer(a)
