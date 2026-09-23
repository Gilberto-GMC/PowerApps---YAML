# -*- coding: utf-8 -*-
"""Tratamento de erro e contratos entre App e telas.

 1. todo Form@ tem OnFailure com conteúdo (erro a partir do Lote D; antes, aviso);
 2. todo Launch(...) que usa varIDhtmlCriado está dentro de If(IsBlank(varIDhtmlCriado), ...)
    (erro a partir do Lote C);
 3. toda named formula nf* usada nas telas está definida em out/_App_Formulas_invariante.fx;
    toda variável var* lida nas telas e definida só no OnStart novo existe lá
    (varModoFiltroAero/Bloco, varBlocoPadrao);
 4. IfError(Patch|Remove|Collect(...)) como argumento direto de If/Switch (lição 2026-09-15) -> erro;
 5. SubmitForm(F) seguido, na mesma fórmula, de Navigate/ResetForm -> aviso (D10: resolvido pelo offline).

Uso: python build/checar_erro.py [--baseline] [--dir PASTA]
"""
import sys, os, re, glob
sys.path.insert(0, os.path.dirname(__file__))
from valida import carregar
from checar_cross_screen import mascarar, texto_sem_cabecalho
from fontes import lote_ativo

erros, avisos = [], []


def forms(node, tela, saida):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and len(item) == 1:
                nome = list(item)[0]; corpo = item[nome]
                if isinstance(corpo, dict) and 'Control' in corpo:
                    if str(corpo['Control']).startswith('Form@'):
                        saida.append((tela, nome, (corpo.get('Properties') or {}).get('OnFailure')))
                    forms(corpo.get('Children'), tela, saida)
                else:
                    forms(corpo, tela, saida)
            else:
                forms(item, tela, saida)


def main():
    baseline = '--baseline' in sys.argv
    pasta = 'msapp/Src' if baseline else 'out'
    if '--dir' in sys.argv:
        pasta = sys.argv[sys.argv.index('--dir') + 1]
    lote = 'ABCD' if baseline else lote_ativo()
    arquivos = sorted(glob.glob(os.path.join(pasta, '*.pa.yaml')))
    lista_forms = []
    nf_usadas = set(); vars_lidas = set()
    for f in arquivos:
        d = carregar(f)
        if isinstance(d, dict) and 'Screens' in d:
            tela = list(d['Screens'])[0]
            forms((d['Screens'][tela] or {}).get('Children'), tela, lista_forms)
        m = mascarar(texto_sem_cabecalho(f))
        nome = os.path.basename(f)
        nf_usadas |= set(re.findall(r'\bnf[A-Z]\w*', m))
        vars_lidas |= set(re.findall(r'\bvar(?:ModoFiltroAero|ModoFiltroBloco|BlocoPadrao)\b', m))
        # 2. Launch com varIDhtmlCriado guardado
        for mt in re.finditer(r'\bLaunch\(', m):
            trecho = m[mt.start():mt.start() + 400]
            if 'varIDhtmlCriado' in trecho:
                antes = m[max(0, mt.start() - 300):mt.start()]
                if 'IsBlank(varIDhtmlCriado)' not in antes:
                    linha = m[:mt.start()].count('\n') + 1
                    (erros if 'C' in lote else avisos).append(f"{nome}:{linha} Launch do PDF sem guarda IsBlank(varIDhtmlCriado)")
        # 4. IfError(Patch...) como argumento direto de If/Switch
        for mt in re.finditer(r'\b(If|Switch)\(\s*[^()]*,\s*IfError\(\s*(Patch|Remove|RemoveIf|Collect)\(', m):
            linha = m[:mt.start()].count('\n') + 1
            erros.append(f"{nome}:{linha} IfError({mt.group(2)}(...)) como argumento direto de {mt.group(1)} — usar If(IsError(...))")
        # 5. SubmitForm seguido de Navigate/ResetForm na mesma fórmula (aviso)
        for mt in re.finditer(r'SubmitForm\((\w+)\)\s*;[^|]{0,200}?\b(Navigate|ResetForm)\(', m, re.S):
            linha = m[:mt.start()].count('\n') + 1
            avisos.append(f"{nome}:{linha} SubmitForm({mt.group(1)}) seguido de {mt.group(2)} na mesma fórmula (UI muda antes de confirmar) — D10, resolvido pela fila offline")
    # 1. OnFailure
    for tela, nome, onf in lista_forms:
        if not onf or str(onf).strip() in ('=', ''):
            msg = f"{tela}: {nome} sem OnFailure"
            (erros if 'D' in lote else avisos).append(msg)
    # 3. nf* definidas
    fx_path = os.path.join(pasta, '_App_Formulas_invariante.fx')
    definidas = set()
    if os.path.exists(fx_path):
        definidas = set(re.findall(r'^(nf\w+)\s*=', open(fx_path, encoding='utf-8').read(), re.M))
    faltam = sorted(nf_usadas - definidas)
    if faltam:
        erros.append(f"named formulas usadas mas não definidas em {fx_path}: {', '.join(faltam)}")
    app = os.path.join(pasta, '01_App.pa.yaml')
    if vars_lidas:
        if not os.path.exists(app):
            erros.append(f"telas leem {sorted(vars_lidas)} mas o App (OnStart novo) não está na entrega")
        else:
            onstart = open(app, encoding='utf-8').read()
            for v in sorted(vars_lidas):
                if not re.search(r'\bSet\(\s*' + v + r'\s*,', onstart):
                    erros.append(f"{v} é lida nas telas mas não é definida no OnStart entregue")
    for e in erros:
        print(f"   {'!' if baseline else '✗'} {e}")
    for a in avisos[:40]:
        print(f"   ! {a}")
    if len(avisos) > 40:
        print(f"   ! ... e mais {len(avisos) - 40} avisos")
    print(f"   total: {len(erros)} erros, {len(avisos)} avisos ({len(lista_forms)} formulários, {len(nf_usadas)} named formulas usadas)" + (' (baseline)' if baseline else ''))
    if erros and not baseline:
        sys.exit(1)
    if not erros:
        print("   ✓ tratamento de erro e contratos ok")


if __name__ == '__main__':
    main()
