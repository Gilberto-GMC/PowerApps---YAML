# -*- coding: utf-8 -*-
"""Correção pontual (roda 1x) dos 3 bugs achados no Verificador de aplicativo do
Studio em 2026-09-22, nos arquivos msapp/Src/*.pa.yaml que já passaram pelo
gerar_editar.py (e por cima disso já levaram recoloração + outros ajustes
manuais) — por isso NÃO re-roda gerar_editar.py do zero (não é idempotente:
duplicaria as inserções). Em vez disso, aplica os 3 ajustes diretamente no
texto já existente.

Os 3 bugs, todos no mesmo lugar: a coleção local de cada filho reconciliável
(ex. col_colVeiEnvolvidos) é povoada de duas formas incompatíveis —

  a) botão "Adicionar" (tela de formulário, já existia antes desta sessão):
     Collect(col, {id: <contador local>, <campos>})
  b) botão "Editar" (tela de lista, escrito por gerar_editar.py nesta sessão):
     ClearCollect(col, ForAll(Filter(...), {dbId: ID, <campos>}))

O Studio unifica o tipo da coleção em TODOS os pontos onde ela aparece; "id" só
existir em (a) e "dbId" só em (b) deixa o tipo ambíguo, e isso reprova Clear()/
ClearCollect() em cascata (~48 erros por módulo, 321 no total — achado via
Verificador de aplicativo, catalogado tela por tela em 2026-09-22).

Fix: (a) ganha "dbId: Blank()," também; (b) ganha "id: ID," também — as duas
formas passam a ter o mesmo conjunto de colunas.

Bug 3 (cosmético, sem risco de erro real, mas junto já que a causa é a mesma
sessão): o texto que reseta o estado de edição no botão "Cadastrar" (Set(
var_editandoX, false); Set(var_registroX, Blank())) saiu com 1 espaço de recuo
a mais que o resto do bloco '|-' — contava o "=" do início da fórmula como
recuo. Corrigido na fonte (gerar_editar.py) para qualquer geração futura; aqui
só reindenta o que já foi escrito nos arquivos atuais.
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from modulos import MODULOS
from gerar_editar import EDICAO, _ev, _reg
from fx import find_call, split_args

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def corrigir_lista(path, m, edic):
    texto = open(path, encoding='utf-8').read()
    k = m['key']
    alteracoes = []

    # --- bug (b): "id: ID" que falta em cada ClearCollect(col, ForAll(...)) ---
    for f in edic['filhos']:
        if f.get('somente_leitura'):
            continue
        col = f['colecao']
        r = find_call(texto, 'ClearCollect')
        achou = False
        while r:
            a, b, c = r
            args = split_args(texto[b:c - 1])
            if args and args[0].strip() == col and 'ForAll(' in args[1]:
                trecho = texto[a:c]
                if 'id: ID' in trecho:
                    achou = True  # já corrigido antes (rodada repetida) — ok
                    break
                m_dbid = re.search(r'\n( *)dbId: ID,\n', trecho)
                if not m_dbid:
                    raise SystemExit(f"[{k}] 'dbId: ID,' nao encontrado dentro do ClearCollect('{col}', ...)")
                pad = m_dbid.group(1)
                novo_trecho = trecho[:m_dbid.end()] + f'{pad}id: ID,\n' + trecho[m_dbid.end():]
                texto = texto[:a] + novo_trecho + texto[c:]
                alteracoes.append(f"id: ID em ClearCollect({col}, ...)")
                achou = True
                break
            r = find_call(texto, 'ClearCollect', c)
        if not achou:
            raise SystemExit(f"[{k}] ClearCollect('{col}', ForAll(...)) nao encontrado em {path}")

    # --- bug 3: reindentação do reset de edição no Cadastrar (1 espaço a mais) ---
    for kk in (k,):
        ev, reg = _ev(kk), _reg(kk)
        padrao = re.compile(
            r'\n( +)Set\(\n\1    ' + re.escape(ev) + r',\n\1    false\n\1\);\n'
            r'\1Set\(\n\1    ' + re.escape(reg) + r',\n\1    Blank\(\)\n\1\)'
        )
        mobj = padrao.search(texto)
        if not mobj:
            # já corrigido antes, ou padrão não bate — não é erro fatal aqui,
            # a reindentação é cosmética; só avisa.
            print(f"  [{k}] aviso: bloco de reset do Cadastrar nao casou com o padrao esperado (pode ja estar certo)")
            continue
        pad_atual = mobj.group(1)
        if not pad_atual.endswith(' '):
            continue
        pad_certo = pad_atual[:-1]
        texto_velho = mobj.group(0)
        texto_novo = texto_velho.replace('\n' + pad_atual, '\n' + pad_certo)
        texto = texto[:mobj.start()] + texto_novo + texto[mobj.end():]
        alteracoes.append("reindentacao do reset do Cadastrar")

    open(path, 'w', encoding='utf-8', newline='\r\n').write(texto)
    return alteracoes


def corrigir_forms(path, m, edic):
    texto = open(path, encoding='utf-8').read()
    k = m['key']
    alteracoes = []

    for f in edic['filhos']:
        if f.get('somente_leitura'):
            continue
        col = f['colecao']
        r = find_call(texto, 'Collect')
        achou = False
        while r:
            a, b, c = r
            args = split_args(texto[b:c - 1])
            if args and args[0].strip() == col:
                trecho = texto[a:c]
                if 'dbId: Blank()' in trecho:
                    achou = True  # já corrigido
                    break
                m_id = re.search(r'\n( *)id: Value\(\n', trecho)
                if not m_id:
                    raise SystemExit(f"[{k}] 'id: Value(' nao encontrado dentro do Collect('{col}', ...) original")
                pad = m_id.group(1)
                ins_pos = m_id.start() + 1  # logo depois do \n, antes do recuo
                novo_trecho = trecho[:ins_pos] + f'{pad}dbId: Blank(),\n' + trecho[ins_pos:]
                texto = texto[:a] + novo_trecho + texto[c:]
                alteracoes.append(f"dbId: Blank() em Collect({col}, ...)")
                achou = True
                break
            r = find_call(texto, 'Collect', c)
        if not achou:
            raise SystemExit(f"[{k}] Collect('{col}', ...) do Adicionar nao encontrado em {path}")

    open(path, 'w', encoding='utf-8', newline='\r\n').write(texto)
    return alteracoes


def main():
    total = 0
    for m in MODULOS:
        edic = EDICAO[m['key']]
        p_lista = os.path.join(RAIZ, 'msapp', 'Src', f"{m['lista']}.pa.yaml")
        p_forms = os.path.join(RAIZ, 'msapp', 'Src', f"{m['forms']}.pa.yaml")
        alt1 = corrigir_lista(p_lista, m, edic)
        alt2 = corrigir_forms(p_forms, m, edic)
        total += len(alt1) + len(alt2)
        print(f"{m['key']:10s} {len(alt1)+len(alt2)} ajuste(s): {', '.join(alt1 + alt2)}")
    print(f"\nTotal: {total} ajustes em {len(MODULOS)} modulos.")


if __name__ == '__main__':
    main()
