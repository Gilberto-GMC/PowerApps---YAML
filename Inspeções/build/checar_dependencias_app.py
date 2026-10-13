"""Lista, para cada tela entregue em out/, as variáveis globais e named formulas
que só passam a existir com o App.OnStart / App.Formulas NOVOS da entrega.

Motivo (2026-09-23): out/15 foi colada sozinha, com o OnStart antigo no app, e o
Studio acusou "'varModoFiltroBloco' não é reconhecido". Tela de lote C não é
autônoma: quem colar uma tela isolada precisa saber o que ela exige do App.

Uso: python build/checar_dependencias_app.py [arquivo.pa.yaml ...]
"""
import glob, os, re, sys

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SET = re.compile(r'\bSet\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*[,;]')
NF = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=', re.M)


def ler(p):
    return open(p, encoding='utf-8').read()


def main():
    antigos = set(SET.findall(ler(os.path.join(RAIZ, 'msapp', 'Src', 'App.pa.yaml'))))
    novos_set = set(SET.findall(ler(os.path.join(RAIZ, 'out', '01_App.pa.yaml')))) - antigos
    fx = os.path.join(RAIZ, 'out', '_App_Formulas_invariante.fx')
    nfs = set(n for n in NF.findall(re.sub(r'//.*', '', ler(fx))) if n.startswith('nf')) if os.path.exists(fx) else set()

    arquivos = sys.argv[1:] or sorted(glob.glob(os.path.join(RAIZ, 'out', '[0-9]*.pa.yaml')))
    algum = False
    for arq in arquivos:
        nome = os.path.basename(arq)
        if nome.startswith('01_App'):
            continue
        txt = ler(arq)
        usa_set = sorted(v for v in novos_set if re.search(r'\b' + v + r'\b', txt))
        usa_nf = sorted(v for v in nfs if re.search(r'\b' + v + r'\b', txt))
        if usa_set or usa_nf:
            algum = True
            partes = []
            if usa_set:
                partes.append('OnStart novo: ' + ', '.join(usa_set))
            if usa_nf:
                partes.append('App.Formulas: ' + ', '.join(usa_nf))
            print(f'   {nome:42} {" | ".join(partes)}')
    if not algum:
        print('   ✓ nenhuma tela depende do OnStart/Formulas novos')


if __name__ == '__main__':
    main()
