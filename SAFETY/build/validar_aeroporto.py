# -*- coding: utf-8 -*-
"""Validador da entrega "campo Aeroporto em todos os modulos" (out/ x msapp/Src).

1. YAML valido e estrutura raiz exata.
2. Diff por valor, controle a controle: o conjunto de mudancas tem que ser
   exatamente o declarado em ESPERADO (nada a mais, nada a menos).
3. Nomes de controle unicos no app inteiro (telas de out/ no lugar das de msapp/Src).
4. Propriedades dos controles novos comprovadas no export do mesmo Control@versao.
5. Proibidos: %DATACARD_, Overflow:, Default em TextInput@0.0.54, " #" em linha unica.
6. Regras do campo: combo travado por varPerfilSafety, Patch sem varAeroUser solto,
   validacao e Reset presentes, referencias a cmbFrm*Aeroporto resolvidas na tela.
7. Dependencias do App.OnStart existentes (a entrega nao mexe no OnStart).

Uso: python build/validar_aeroporto.py   (sai com codigo 1 se algo reprovar)
"""
import glob
import os
import re
import sys

import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'msapp', 'Src')
OUT = os.path.join(BASE, 'out')
RAIZ = os.path.dirname(BASE)

TRAVA = '=If(varPerfilSafety, DisplayMode.Edit, DisplayMode.Disabled)'
# tela: chave, prefixo das colunas, botao Salvar, botao de reset, container do campo
PATCH = {
    'ScreenColisaoVeiculosForms': ('ColVei', 'colVei', 'ButtonCanvas7_4', 'ButtonResetFormColVei', 'Container4'),
    'ScreenDerramamentoForms': ('DerFlu', 'derFlu', 'ButtonCanvas7_18', 'ButtonResetFormDerFlu', 'Container3_22'),
    'ScreenExcursaoPistaForms': ('ExcPista', 'excPista', 'ButtonCanvas7_33', 'ButtonResetFormExcPista', 'Container3_38'),
    'ScreenIncursaoPistaForms': ('IncPista', 'incPista', 'ButtonCanvas7_49', 'ButtonResetFormIncPista', 'Container3_26'),
    'ScreenInterferenciaExternaForms': ('IntExt', 'intExt', 'ButtonCanvas7_57', 'ButtonResetFormIntExt', 'Container3_34'),
    'ScreenOcorrenciaSoloForms': ('OcoSolo', 'ocoSolo', 'ButtonCanvas7_73', 'ButtonResetForm', 'Container3_18'),
    'ScreenAcessIndFaunaForms': ('AceIndFau', 'aceIndFauna', 'ButtonCanvas7_82', 'ButtonResetFormAceIndFauna', 'Container3_46'),
    'ScreenJetBlastForms': ('JetBlast', 'jetBlast', 'ButtonCanvas7_65', 'ButtonResetFormJetBlast', 'Container3_50'),
}

# mudanca obrigatoria: ('~', controle, propriedade) alterada; ('+', controle, None) controle novo
ESPERADO = {}
# mudanca permitida alem das obrigatorias: posicao/tamanho dos filhos diretos do
# container da linha de cima (padrao de duas linhas) e largura do proprio container
POSICAO = {'X', 'Y', 'Width', 'Height'}
for tela, (k, _, salvar, reset, cont) in PATCH.items():
    ESPERADO[tela] = {('+', f'lblFrm{k}Aeroporto', None), ('+', f'cmbFrm{k}Aeroporto', None),
                      ('~', salvar, 'OnSelect'), ('~', reset, 'OnSelect')}
    if cont.startswith('Container3_'):
        ESPERADO[tela].add(('+', f'rctFrm{k}Aeroporto', None))
ESPERADO['ScreenFOD'] = {('+', 'cmbFrmFODAeroporto', None), ('~', 'aeroporto_DataCard1', 'Default'),
                         ('~', 'aeroporto_DataCard1', 'Update'), ('~', 'DataCardValue11', 'Visible')}
ESPERADO['ScreenCSO'] = {('+', 'cmbFrmCSOAeroporto', None), ('~', 'Aeroporto_DataCard2', 'DisplayMode'),
                         ('~', 'Aeroporto_DataCard2', 'Update'), ('~', 'DataCardValue34', 'Visible')}
ESPERADO['ScreenVistoriaSafetyFauna'] = {
    ('+', 'cmbFrmVistoriaAeroporto', None), ('~', 'Aeroporto_DataCard3', 'Visible'),
    ('~', 'Aeroporto_DataCard3', 'Required'), ('~', 'Aeroporto_DataCard3', 'Update'),
    ('~', 'DataCardValue47', 'Visible'), ('~', 'Bloco_DataCard1', 'Update')}
ESPERADO['ScreenFaunaForms'] = {('~', f'ComboboxCanvas{t}_{s}', p)
                                for s in '432' for t in ('Bloco', 'Aeroporto')
                                for p in ('DisplayMode', 'Default')}

falhas = []


def reprovar(msg):
    falhas.append(msg)


def carregar(caminho, loader=yaml.BaseLoader):
    with open(caminho, encoding='utf-8') as f:
        return yaml.load(f, Loader=loader)


def controles(tela_yaml):
    """{nome: (Control, Properties, pai)} de uma tela."""
    out = {}

    def walk(ch, pai):
        for it in ch or []:
            for n, b in it.items():
                out[n] = (b.get('Control'), b.get('Properties') or {}, pai, [list(c)[0] for c in b.get('Children') or []])
                walk(b.get('Children'), n)
    for nome, corpo in tela_yaml['Screens'].items():
        out[nome] = ('Screen', corpo.get('Properties') or {}, None, [list(c)[0] for c in corpo.get('Children') or []])
        walk(corpo.get('Children'), nome)
    return out


def dicionario_propriedades():
    d = {}
    for f in glob.glob(os.path.join(RAIZ, '**', 'Src', '*.pa.yaml'), recursive=True):
        if os.path.normpath(f).startswith(os.path.normpath(OUT)):
            continue
        try:
            y = carregar(f)
        except Exception:
            continue
        for tela in (y or {}).get('Screens', {}).values():
            def walk(ch):
                for it in ch or []:
                    if not isinstance(it, dict):
                        continue
                    for _, b in it.items():
                        if isinstance(b, dict) and b.get('Control'):
                            d.setdefault(b['Control'], set()).update((b.get('Properties') or {}).keys())
                            walk(b.get('Children'))
            walk(tela.get('Children'))
    return d


def main():
    dic = dicionario_propriedades()
    telas_out = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(OUT, '*.pa.yaml')))
    if set(telas_out) != set(ESPERADO):
        reprovar(f'telas em out/ {sorted(telas_out)} <> esperadas {sorted(ESPERADO)}')

    for tela in telas_out:
        caminho = os.path.join(OUT, tela + '.pa.yaml')
        txt = open(caminho, encoding='utf-8').read()
        # 1. sintaxe e raiz (BaseLoader: o SafeLoader recusa o "=" sozinho de
        #    "LayoutMaxHeight: =", que o proprio Studio exporta)
        try:
            novo = carregar(caminho)
        except Exception as e:
            reprovar(f'{tela}: YAML invalido: {e}')
            continue
        util = [l for l in txt.split('\n') if not l.startswith('#')]
        if util[:2] != ['Screens:', f'  {tela}:'] or util[2] not in ('    Properties:', '    Children:'):
            reprovar(f'{tela}: estrutura raiz {util[:3]}')
        # 5. proibidos (Overflow so e proibido em GroupContainer; Label@2.5.1 tem)
        if '%DATACARD_' in txt:
            reprovar(f'{tela}: contem %DATACARD_')
        for n, l in enumerate(txt.split('\n'), 1):
            if re.match(r'^ *[A-Za-z.]+: =', l) and re.search(r'[ \t]#', l):
                reprovar(f'{tela}:{n}: " #" em propriedade de linha unica')

        # 2. diff por valor
        velho = controles(carregar(os.path.join(SRC, tela + '.pa.yaml')))
        cn = controles(novo)
        mud = set()
        for n in cn.keys() - velho.keys():
            mud.add(('+', n, None))
        for n in velho.keys() - cn.keys():
            mud.add(('-', n, None))
        for n in cn.keys() & velho.keys():
            cv, pv, paiv, fv = velho[n]
            cN, pN, paiN, fN = cn[n]
            if cv != cN or paiv != paiN:
                mud.add(('tipo/pai', n, None))
            for p in pv.keys() | pN.keys():
                if pv.get(p) != pN.get(p):
                    mud.add(('~', n, p))
            filhos_v = [f for f in fN if f in velho]
            if filhos_v != fv:
                mud.add(('ordem', n, None))
        extra = mud - ESPERADO[tela]
        if tela in PATCH and PATCH[tela][4].startswith('Container3_'):
            cont = PATCH[tela][4]
            extra = {m for m in extra
                     if not (m[0] == '~' and m[2] in POSICAO and (cn[m[1]][2] == cont
                             or (m[1] == cont and m[2] == 'Width')))}
        if extra or ESPERADO[tela] - mud:
            reprovar(f'{tela}: mudancas fora do declarado: a mais {sorted(extra, key=str)}, '
                     f'faltando {sorted(ESPERADO[tela] - mud, key=str)}')

        # 4. dicionario para os controles novos
        for (_, n, _) in [m for m in mud if m[0] == '+']:
            tipo, props, _, _ = cn[n]
            fora = sorted(set(props) - dic.get(tipo, set()))
            if fora:
                reprovar(f'{tela}: {n} ({tipo}) com propriedade nao comprovada: {fora}')
            if list(props) != sorted(props, key=str.lower):
                reprovar(f'{tela}: {n} com propriedades fora da ordem alfabetica')
        for n, (tipo, props, _, _) in cn.items():
            if tipo == 'TextInput@0.0.54' and 'Default' in props:
                reprovar(f'{tela}: Default em TextInput@0.0.54 ({n})')
            if (tipo or '').startswith('GroupContainer') and 'Overflow' in props:
                reprovar(f'{tela}: Overflow em GroupContainer ({n})')

        # 6. regras do campo
        combos = [n for n in cn if re.fullmatch(r'cmbFrm\w+Aeroporto', n)]
        for c in combos:
            p = cn[c][1]
            if p.get('DisplayMode') != TRAVA:
                reprovar(f'{tela}: {c}.DisplayMode = {p.get("DisplayMode")}')
            if p.get('Items') != '=Filter(colAeros, !IsBlank(Aeroporto))' or p.get('Items.Value') != '=Aeroporto':
                reprovar(f'{tela}: {c} sem a lista de aeroportos')
        for ref in set(re.findall(r'\bcmbFrm\w+Aeroporto\b', txt)):
            if ref not in cn:
                reprovar(f'{tela}: referencia a {ref} inexistente na tela')

        if tela in PATCH:
            k, pref, salvar, reset, cont = PATCH[tela]
            cmb = f'cmbFrm{k}Aeroporto'
            novos = [f'lblFrm{k}Aeroporto', cmb] + ([f'rctFrm{k}Aeroporto'] if cont.startswith('Container3_') else [])
            for n in novos:
                if cn.get(n, (None, None, None))[2] != cont:
                    reprovar(f'{tela}: {n} fora de {cont}')
            if cont.startswith('Container3_'):
                # padrao do ScreenJetBlastForms: Aeroporto na linha da Data, logo a
                # direita dela; nenhuma caixa sobrepoe outra; tudo dentro do
                # container; corpo do formulario abaixo da ultima linha de caixas
                def num(v):
                    return int(v[1:])
                rn = f'rctFrm{k}Aeroporto'
                cx = {n: (num(p['X']), num(p['Y']), num(p['Width']), 45) for n, (t, p, pai, _) in cn.items()
                      if pai == cont and t == 'Rectangle@2.3.0' and p.get('Height') == '=45'}
                larg = num(cn[cont][1]['Width'])
                data = min((v for n, v in cx.items() if n != rn), key=lambda v: (v[1], v[0]))
                r = cx[rn]
                if r[1] != data[1] or not (data[0] + data[2] < r[0] <= data[0] + data[2] + 30):
                    reprovar(f'{tela}: caixa Aeroporto nao esta logo a direita da Data ({r}, Data {data})')
                nomes = sorted(cx)
                for i, a in enumerate(nomes):
                    ax, ay, aw, ah = cx[a]
                    if ax < 0 or ax + aw > larg:
                        reprovar(f'{tela}: {a} sai de {cont} (largura {larg})')
                    for b in nomes[i + 1:]:
                        bx, by, bw, bh = cx[b]
                        if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                            reprovar(f'{tela}: caixas {a} e {b} se sobrepoem')
                for n in (f'lblFrm{k}Aeroporto', cmb):
                    p = cn[n][1]
                    if not (r[0] <= num(p['X']) and num(p['X']) + num(p['Width']) <= r[0] + r[2]):
                        reprovar(f'{tela}: {n} fora da caixa Aeroporto')
                fundo = max(y + h for _, y, _, h in cx.values())
                for n, (t, p, pai, _) in cn.items():
                    if pai == cont and t.startswith('GroupContainer') and num(p['Y']) < fundo:
                        reprovar(f'{tela}: corpo {n} (Y={p["Y"]}) invade as caixas (fim em {fundo})')
            f = cn[salvar][1]['OnSelect']
            exig = [f'{pref}_aeroporto: If(varPerfilSafety, {cmb}.Selected.Aeroporto, varAeroUser)',
                    f'{pref}_bloco: If(varPerfilSafety, {cmb}.Selected.Bloco, varBlocoUser)',
                    f'varPerfilSafety And IsBlank({cmb}.Selected.Aeroporto),']
            for e in exig:
                if f.count(e) != 1:
                    reprovar(f'{tela}: Salvar sem "{e}"')
            if re.search(r'_aeroporto: varAeroUser', f) or re.search(r'_bloco: varBlocoUser', f):
                reprovar(f'{tela}: Patch ainda grava varAeroUser/varBlocoUser direto')
            if f'Reset({cmb});' not in cn[reset][1]['OnSelect']:
                reprovar(f'{tela}: {reset} nao reseta {cmb}')
            if tela == 'ScreenDerramamentoForms' and f.count('varIATAUser') != 1:
                reprovar(f'{tela}: notificacao ainda usa so o aeroporto do usuario')
        if tela == 'ScreenFaunaForms' and 'varPerfilUser = "Base", DisplayMode.Disabled' in txt:
            reprovar(f'{tela}: combo de aeroporto/bloco ainda travado pelo perfil Base')

    # 3. nomes unicos no app inteiro
    donos = {}
    arquivos = {os.path.basename(p)[:-8]: p for p in glob.glob(os.path.join(SRC, '*.pa.yaml'))
                if not os.path.basename(p).startswith('_')}
    arquivos.update({t: os.path.join(OUT, t + '.pa.yaml') for t in telas_out})
    for tela, p in arquivos.items():
        y = carregar(p)
        if not y or 'Screens' not in y:
            continue
        for n in controles(y):
            if n in donos:
                reprovar(f'nome duplicado no app: {n} ({donos[n]} e {tela})')
            donos[n] = tela
    for p in glob.glob(os.path.join(SRC, 'Components', '*.pa.yaml')):
        for n in re.findall(r'(?m)^ *- (\w+):$', open(p, encoding='utf-8').read()):
            if n in donos and n.startswith(('cmbFrm', 'lblFrm')):
                reprovar(f'nome novo {n} colide com componente {os.path.basename(p)}')

    # 7. dependencias do OnStart
    onstart = carregar(os.path.join(SRC, 'App.pa.yaml'))['App']['Properties']['OnStart']
    for v in ('varPerfilSafety', 'varAeroUser', 'varBlocoUser', 'varIATAUser', 'colAeros'):
        if not re.search(r'(Set|ClearCollect)\(\s*' + v + r'\s*,', onstart):
            reprovar(f'App.OnStart nao define {v}')

    if falhas:
        print('REPROVADO:')
        for f in falhas:
            print(' -', f)
        sys.exit(1)
    print(f'OK: {len(telas_out)} telas validadas, mudancas exatamente as declaradas.')


if __name__ == '__main__':
    main()
