# -*- coding: utf-8 -*-
"""Sintaxe que o Studio recusa (ou aceita e quebra): checagem local antes de colar.

Regras (todas de lições registradas em LICOES_APRENDIDAS_POWERAPPS_YAML.md):
 1. parênteses/colchetes/chaves e aspas balanceados em cada fórmula;
 2. vírgula faltando entre argumentos: `f(...) g(...)` sem operador entre eles
    (o Studio reporta o erro na função de fora, longe da causa);
 3. propriedade de linha única contendo `: ` ou ` #` sem aspas YAML (o Studio
    grava essas como bloco `|-` ou com aspas simples; escrito à mão, quebra o YAML);
 4. `;;` em código ativo (pt-BR colado por engano);
 5. `ThisRecord.<coluna de origem>` dentro de ForAll(Distinct(...)) — Distinct devolve Value;
 6. teto de data `col <= Today()` (direto ou via `If(IsBlank(dtp), Today(), ...)`): Today() é
    00:00 de hoje, então registro data/hora criado hoje fica fora (lição 2026-10-13).

Uso: python build/checar_sintaxe.py [--baseline] [--dir PASTA]
"""
import sys, os, re, glob, yaml
sys.path.insert(0, os.path.dirname(__file__))
from checar_cross_screen import mascarar

PAT_PROP = re.compile(r'^(\s*)([A-Za-z_][\w.\']*):\s*(.*)$')


def formulas_de(path):
    """gera (linha, nome_prop, texto_formula, linha_unica) para cada propriedade =..."""
    linhas = open(path, encoding='utf-8').read().split('\n')
    i = 0
    while i < len(linhas):
        l = linhas[i]
        if l.lstrip().startswith('#'):
            i += 1; continue
        m = PAT_PROP.match(l)
        if not m:
            i += 1; continue
        ind, nome, val = len(m.group(1)), m.group(2), m.group(3)
        if val in ('|', '|-', '|+', '>', '>-'):
            corpo = []
            j = i + 1
            while j < len(linhas) and (not linhas[j].strip() or len(linhas[j]) - len(linhas[j].lstrip()) > ind):
                corpo.append(linhas[j]); j += 1
            txt = '\n'.join(corpo)
            yield i + 1, nome, txt, False
            i = j; continue
        if val.startswith('=') or val.startswith("'=") or val.startswith('"='):
            yield i + 1, nome, val, True
        i += 1


def balanco(fx):
    m = mascarar(fx)
    pilha = []
    pares = {')': '(', ']': '[', '}': '{'}
    for c in m:
        if c in '([{':
            pilha.append(c)
        elif c in ')]}':
            if not pilha or pilha[-1] != pares[c]:
                return f"'{c}' sem abertura"
            pilha.pop()
    if pilha:
        return f"'{pilha[-1]}' sem fechamento"
    # aspas: a máscara deixa as aspas nas pontas; contagem de " tem de ser par
    if m.count('"') % 2:
        return 'aspas duplas desbalanceadas'
    return None


def main():
    baseline = '--baseline' in sys.argv
    pasta = 'msapp/Src' if baseline else 'out'
    if '--dir' in sys.argv:
        pasta = sys.argv[sys.argv.index('--dir') + 1]
    problemas = []; avisos = []
    arquivos = sorted(glob.glob(os.path.join(pasta, '*.pa.yaml')) + glob.glob(os.path.join(pasta, 'Components', '*.pa.yaml')))
    for f in arquivos:
        nome_arq = os.path.basename(f)
        for linha, prop, fx, unica in formulas_de(f):
            if unica:
                bruto = fx
                if not (bruto.startswith("'") or bruto.startswith('"')):
                    if ': ' in bruto or ' #' in bruto:
                        problemas.append((nome_arq, linha, prop, "linha única com ': ' ou ' #' sem aspas YAML"))
                    fx = bruto
                else:
                    # valor YAML entre aspas: decodifica escapes (\n, \", '') como o Studio
                    try:
                        fx = str(yaml.safe_load(bruto))
                    except Exception:
                        problemas.append((nome_arq, linha, prop, 'valor YAML entre aspas inválido'))
                        continue
            corpo = fx[1:] if fx.lstrip().startswith('=') else fx
            e = balanco(corpo)
            if e:
                problemas.append((nome_arq, linha, prop, e))
                continue
            m = mascarar(corpo)
            if re.search(r'\)\s*\n\s*[A-Za-z_][\w]*\s*\(', m) or re.search(r'\)[ \t]+[A-Za-z_][\w]*\s*\(', m):
                # `)` seguido de identificador e `(` sem operador: vírgula faltando
                problemas.append((nome_arq, linha, prop, 'vírgula faltando entre argumentos (`) f(`)'))
            if re.search(r'(?<!;);;(?!;)', m):
                problemas.append((nome_arq, linha, prop, "';;' em código ativo (pt-BR)"))
            # ';' encostado em ')' sem nem um comentário no meio: sobra de remoção
            # (o export original tem "instrução; // comentário\n)" e o Studio aceita)
            # (o export original já traz 2 casos assim e o Studio os aceita: é aviso, não erro)
            mc = mascarar(corpo, manter_comentarios=True)
            if re.search(r';[ \t\r\n]*\)', mc):
                avisos.append((nome_arq, linha, prop, "';' logo antes de ')' — instrução vazia"))
            if re.search(r'[(,][ \t\r\n]*;', mc):
                problemas.append((nome_arq, linha, prop, "';' logo depois de '(' ou ',' — instrução vazia"))
            for md in re.finditer(r'ForAll\(\s*Distinct\(', m):
                trecho = m[md.start():md.start() + 600]
                mm = re.search(r'ThisRecord\.([A-Za-z_]\w*)', trecho)
                if mm and mm.group(1) != 'Value':
                    problemas.append((nome_arq, linha, prop, f"ForAll(Distinct(...)) lendo ThisRecord.{mm.group(1)} — Distinct devolve Value"))
            if re.search(r'<=\s*(If\(\s*IsBlank\([^()]*\)\s*,\s*)?Today\(\)', m):
                # aviso (não erro) enquanto frmHomeTPS/frmZPAapontamentos/out/ não forem corrigidos
                avisos.append((nome_arq, linha, prop, "teto de data '<= Today()' exclui o dia de hoje — use '< DateAdd(Coalesce(dtp, Today()), 1, TimeUnit.Days)'"))
    for a, l, p, e in problemas:
        print(f"   {'!' if baseline else '✗'} {a}:{l}  {p}: {e}")
    for a, l, p, e in avisos:
        print(f"   ! {a}:{l}  {p}: {e} (aviso)")
    print(f"   total: {len(problemas)} problemas de sintaxe, {len(avisos)} avisos em {len(arquivos)} arquivos" + (' (baseline)' if baseline else ''))
    if problemas and not baseline:
        sys.exit(1)
    if not problemas:
        print("   ✓ sintaxe ok")


if __name__ == '__main__':
    main()
