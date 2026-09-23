# -*- coding: utf-8 -*-
"""Comparação por VALOR de cada propriedade: export do Studio (msapp/Src) x entrega (out/).

Por que existe (2026-09-17): a normalização de escalares entre aspas em blocos |-
apagava linhas só de espaços de fórmulas que nenhuma cirurgia tocava. O texto
mudava, a fórmula não, e nenhum checador percebia. Este checador lê os dois
lados como YAML (o que o Studio de fato consome) e cobra:

 1. nenhuma propriedade pode mudar SÓ em espaço em branco (sinal de efeito
    colateral do ferramental, nunca de cirurgia);
 2. se existir build/propriedades_esperadas_<LOTE>.json, o conjunto de propriedades
    alteradas/novas/removidas e de controles removidos/novos tem de ser
    exatamente o declarado ali (qualquer mudança não revisada reprova).

Uso: python build/checar_valores.py [--gravar]
     --gravar: grava build/propriedades_esperadas_<LOTE>.json com o estado atual
               (só depois de revisar a lista que o checador imprime).
"""
import sys, os, re, glob, json
import yaml

# uma lista por lote (o Inspeções gera A, AB, ABC ou ABCD; o mobile gera Q)
ESPERADAS = 'build/propriedades_esperadas' + ('_' + os.environ['LOTE'] if os.environ.get('LOTE') else '') + '.json'


class _Loader(yaml.SafeLoader):
    pass


# '=' sozinho é o tag 'value' do YAML 1.1; para o Studio é texto (mesmo loader de valida.py)
_Loader.add_constructor('tag:yaml.org,2002:value', lambda l, n: l.construct_scalar(n))


def ler(path):
    return yaml.load(open(path, encoding='utf-8'), Loader=_Loader)


def achatar(doc):
    """{(controle, propriedade): valor} e o conjunto de controles"""
    props, ctrls = {}, set()

    def walk(no, nome):
        # nó = tela, App, componente ou controle: {Control?, Properties?, Children?}
        if not isinstance(no, dict):
            return
        ctrls.add(nome)
        for p, val in (no.get('Properties') or {}).items():
            props[(nome, p)] = val
        for item in no.get('Children') or []:
            if isinstance(item, dict):
                for filho, sub in item.items():
                    walk(sub, filho)

    for k, v in (doc or {}).items():
        if k in ('Screens', 'ComponentDefinitions') and isinstance(v, dict):
            for tela, corpo in v.items():
                walk(corpo, tela)
        elif k == 'App' and isinstance(v, dict):
            walk(v, 'App')
    return props, ctrls


def trechos_so_espaco(a, b):
    """numa propriedade com mudança real, acha trechos de linhas que diferem só em
    espaço (ex.: linha '    ' virou ''): a cirurgia não mexe nisso, o ferramental sim"""
    import difflib
    if not (isinstance(a, str) and isinstance(b, str)):
        return []
    la, lb = a.split('\n'), b.split('\n')
    achados = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        va, vb = la[i1:i2], lb[j1:j2]
        # só linhas em branco dos dois lados, e ao menos uma com espaços: é o defeito
        # "linha só de espaços virou vazia" (linha vazia a mais/a menos num corpo
        # reescrito é formatação da cirurgia e não conta)
        if all(not x.strip() for x in va + vb) and any(x for x in va + vb):
            achados.append(f"linhas {i1 + 1}-{i2} {va!r} -> {vb!r}"[:160])
    return achados


def tela_de_out(path):
    m = re.match(r'^(?:\d+_)?(.+)\.pa\.yaml$', os.path.basename(path))
    return m.group(1) if m else None


def so_espaco(a, b):
    return isinstance(a, str) and isinstance(b, str) and a != b and ''.join(a.split()) == ''.join(b.split())


def main():
    gravar = '--gravar' in sys.argv
    erros, registro = [], []
    for f in sorted(glob.glob('out/*.pa.yaml')):
        tela = tela_de_out(f)
        doc_out = ler(f)
        p_out, c_out = achatar(doc_out)
        orig = os.path.join('msapp', 'Src', tela + '.pa.yaml')
        if not os.path.exists(orig):
            registro.append(f"{tela}: tela nova ({len(c_out)} controles, {len(p_out)} propriedades)")
            continue
        p_src, c_src = achatar(ler(orig))
        for c in sorted(c_src - c_out):
            registro.append(f"{tela}: controle removido {c}")
        for c in sorted(c_out - c_src):
            registro.append(f"{tela}: controle novo {c}")
        for chave in sorted(set(p_src) | set(p_out), key=lambda x: (str(x[0]), x[1])):
            ctrl, prop = chave
            if chave not in p_out:
                if ctrl in c_out:
                    registro.append(f"{tela}: propriedade removida {ctrl}.{prop}")
                continue
            if chave not in p_src:
                if ctrl in c_src:
                    registro.append(f"{tela}: propriedade nova {ctrl}.{prop}")
                continue
            a, b = p_src[chave], p_out[chave]
            if a == b:
                continue
            if so_espaco(a, b):
                erros.append(f"{tela}: {ctrl}.{prop} muda só em espaço em branco (efeito colateral do ferramental)")
            else:
                for trecho in trechos_so_espaco(a, b):
                    erros.append(f"{tela}: {ctrl}.{prop} perdeu/ganhou espaços fora do trecho alterado: {trecho}")
            registro.append(f"{tela}: propriedade alterada {ctrl}.{prop}")

    alteradas = sum(1 for r in registro if 'alterada' in r)
    print(f"   {alteradas} propriedades alteradas, {len(registro) - alteradas} outras mudanças estruturais")

    if gravar:
        if erros:
            for e in erros:
                print(f"   ✗ {e}")
            raise SystemExit("   ✗ não grava a lista esperada com erro pendente")
        with open(ESPERADAS, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(registro, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print(f"   gravado {ESPERADAS} ({len(registro)} entradas)")
    elif os.path.exists(ESPERADAS):
        esperado = json.load(open(ESPERADAS, encoding='utf-8'))
        for r in sorted(set(registro) - set(esperado)):
            erros.append(f"mudança não declarada: {r}")
        for r in sorted(set(esperado) - set(registro)):
            erros.append(f"mudança declarada que não ocorreu: {r}")
    else:
        for r in registro:
            print(f"   · {r}")
        print(f"   ! {ESPERADAS} ausente: revise a lista acima e grave com --gravar")

    for e in erros:
        print(f"   ✗ {e}")
    if erros:
        sys.exit(1)
    print("   ✓ valores conferidos: nenhuma mudança só de espaço" + (", conjunto igual ao declarado" if os.path.exists(ESPERADAS) else ""))


if __name__ == '__main__':
    main()
