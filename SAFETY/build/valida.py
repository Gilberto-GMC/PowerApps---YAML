import sys, yaml, re, json, collections
class L(yaml.SafeLoader): pass
L.add_constructor('tag:yaml.org,2002:value', lambda l,n: l.construct_scalar(n))

def carregar(path):
    return yaml.load(open(path, encoding='utf-8'), Loader=L)

def props_de(node, saco):
    if isinstance(node, dict):
        ctrl = node.get('Control')
        if ctrl and isinstance(node.get('Properties'), dict):
            for k in node['Properties']:
                saco.append((ctrl, k))
        for v in node.values():
            props_de(v, saco)
    elif isinstance(node, list):
        for v in node:
            props_de(v, saco)

def nomes_de(node, out):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and len(item) == 1:
                n = list(item)[0]
                if isinstance(item[n], dict) and 'Control' in item[n]:
                    out.append(n)
                nomes_de(item[n], out)
            else:
                nomes_de(item, out)
    elif isinstance(node, dict):
        for v in node.values():
            nomes_de(v, out)

if __name__ == '__main__':
    dic = json.load(open('build/propdict.json'))
    falhou = False
    for path in sys.argv[1:]:
        print(f"── {path}")
        try:
            d = carregar(path)
        except Exception as e:
            print(f"   ✗ YAML inválido: {e}"); falhou = True; continue
        txt = open(path, encoding='utf-8').read()
        if 'Screens' in d:
            if not re.search(r'(?m)^Screens:\n  \w+:\n    Properties:', txt):
                print("   ✗ estrutura raiz fora do padrão"); falhou = True
            tela = list(d['Screens'])[0]
            print(f"   tela: {tela}")
        saco = []; props_de(d, saco)
        desconhecidas = collections.Counter()
        for ctrl, k in saco:
            if ctrl in dic and k not in dic[ctrl]:
                desconhecidas[(ctrl, k)] += 1
        if desconhecidas:
            falhou = True
            for (c, k), n in desconhecidas.items():
                print(f"   ✗ PA2108 provável: '{k}' em {c} (x{n})")
        nomes = []; nomes_de(d, nomes)
        dup = [n for n, c in collections.Counter(nomes).items() if c > 1]
        if dup:
            falhou = True
            print(f"   ✗ nomes de controle duplicados: {dup}")
        print(f"   ✓ {len(nomes)} controles, {len(saco)} propriedades")
    sys.exit(1 if falhou else 0)
