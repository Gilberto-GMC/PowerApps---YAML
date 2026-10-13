# -*- coding: utf-8 -*-
"""Campo Aeroporto nos formularios de todos os modulos do SAFETY.

Le o export intocado (msapp/Src) e grava as telas alteradas em out/.

Regra: o campo nasce com o aeroporto do usuario (varAeroUser); so quem tem
View_safety = 1 (varPerfilSafety, definido no App.OnStart) pode troca-lo.
Para os demais usuarios a gravacao continua exatamente como no export:
varAeroUser e varBlocoUser.

Tres familias de tela:
- 8 formularios com Patch (7 modulos de Safety + Acesso Indevido de Fauna):
  nao tinham campo; ganham uma caixa "Aeroporto:" ao lado da Data (padrao do
  ScreenJetBlastForms ajustado no Studio, que vem de studio/; em Colisao, que e
  uma coluna so, logo abaixo da Data), validacao, Patch e Reset.
- FOD, CSO e Vistoria (EditForm): o cartao de aeroporto era texto livre
  (FOD), travado (CSO) ou oculto (Vistoria); ganha combo com a mesma regra.
- ScreenFaunaForms (3 EditForms): ja tinha combos Bloco/Aeroporto travados
  por perfil "Base"; a trava passa a ser View_safety.

Uso: python build/adicionar_aeroporto.py   (idempotente: sempre parte do export)
"""
import os
import re
import sys

import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'msapp', 'Src')
OUT = os.path.join(BASE, 'out')

AVISO = (
    '# Source Code YAML em formato INVARIANTE: virgula separa argumentos,\n'
    '# ponto e virgula encadeia, ponto e o decimal. Colar pela exibicao de\n'
    '# codigo do Power Apps Studio. NAO converter para pt-BR.\n'
    '# Gerado por SAFETY/build/adicionar_aeroporto.py a partir de msapp/Src.\n'
)

ITENS_AERO = '=Filter(colAeros, !IsBlank(Aeroporto))'
TRAVA = '=If(varPerfilSafety, DisplayMode.Edit, DisplayMode.Disabled)'


def falhar(msg):
    sys.exit('ERRO: ' + msg)


def ler(tela):
    with open(os.path.join(SRC, tela + '.pa.yaml'), encoding='utf-8', newline='') as f:
        return f.read().replace('\r\n', '\n')


def gravar(tela, txt):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, tela + '.pa.yaml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(AVISO + txt)


def sub(txt, velho, novo, rotulo, n=1):
    achados = txt.count(velho)
    if achados != n:
        falhar(f'{rotulo}: esperado {n}, achado {achados}')
    return txt.replace(velho, novo)


def faixa(txt, nome):
    """Inicio/fim do bloco YAML do controle `nome` e a indentacao do '- nome:'."""
    ms = list(re.finditer(r'(?m)^( *)- ' + re.escape(nome) + r':\n', txt))
    if len(ms) != 1:
        falhar(f'controle {nome}: {len(ms)} definicoes')
    m = ms[0]
    ind = len(m.group(1))
    for mm in re.finditer(r'(?m)^( *)\S', txt[m.end():]):
        if len(mm.group(1)) <= ind:
            return m.start(), m.end() + mm.start(), ind
    return m.start(), len(txt), ind


def sub_em(txt, nome, velho, novo, rotulo, n=1):
    ini, fim, _ = faixa(txt, nome)
    return txt[:ini] + sub(txt[ini:fim], velho, novo, rotulo, n) + txt[fim:]


def inserir_antes(txt, nome, linhas):
    """Insere `linhas` (relativas ao '- ') imediatamente antes do controle `nome`."""
    ini, _, ind = faixa(txt, nome)
    bloco = ''.join(' ' * ind + l + '\n' for l in linhas)
    return txt[:ini] + bloco + txt[ini:]


def garantir_ausente(txt, nomes, tela):
    for n in nomes:
        if re.search(r'\b' + re.escape(n) + r'\b', txt):
            falhar(f'{tela}: {n} ja existe na fonte (gerador rodaria duas vezes?)')


def controle(nome, tipo, props):
    linhas = [f'- {nome}:', f'    Control: {tipo}', '    Properties:']
    for k in sorted(props, key=str.lower):
        linhas.append(f'      {k}: {props[k]}')
    return linhas


# ---------------------------------------------------------------------------
# 1) Formularios com Patch: caixa "Aeroporto:" no fim da linha de cima
# ---------------------------------------------------------------------------

# tela, chave, onde entra, botao de reset, variavel de erro, prefixo das
# colunas, primeira condicao do Switch de validacao.
# "onde entra": ('linha', <container da linha de cima>) ou
#               ('coluna', <entra antes deste>, <rotulo modelo>, <combo modelo>)
PATCH = [
    ('ScreenColisaoVeiculosForms', 'ColVei',
     ('coluna', 'Label20_439', 'Label20_358', 'cmbColVeiTipColisao'),
     'ButtonResetFormColVei', 'var_formErro', 'colVei',
     'IsBlank(cmbColVeiHoraCadastro.Selected.Value) = true,'),
    ('ScreenDerramamentoForms', 'DerFlu', ('linha', 'Container3_22'),
     'ButtonResetFormDerFlu', 'varFormErro', 'derFlu',
     'cmbDerFluHoraCadastro.Selected.Value = "hor",'),
    ('ScreenExcursaoPistaForms', 'ExcPista', ('linha', 'Container3_38'),
     'ButtonResetFormExcPista', 'var_formErro', 'excPista',
     'IsBlank(cmbExcPistaHoraCadastro.Selected.Value) = true,'),
    ('ScreenIncursaoPistaForms', 'IncPista', ('linha', 'Container3_26'),
     'ButtonResetFormIncPista', 'var_formErro', 'incPista',
     'IsBlank(cmbIncPistaAgravante.Selected.Value) = true,'),
    ('ScreenInterferenciaExternaForms', 'IntExt', ('linha', 'Container3_34'),
     'ButtonResetFormIntExt', 'var_formErro', 'intExt',
     'cmbIntExtHoraCadastro.Selected.Value = "hor",'),
    ('ScreenOcorrenciaSoloForms', 'OcoSolo', ('linha', 'Container3_18'),
     'ButtonResetForm', 'varCampoVazio', 'ocoSolo',
     'IsBlank(cmbOcoSoloHora.Selected.Value),'),
    ('ScreenAcessIndFaunaForms', 'AceIndFau', ('linha', 'Container3_46'),
     'ButtonResetFormAceIndFauna', 'var_formErro', 'aceIndFauna',
     'cmbAceIndFauHoraCadastro.Selected.Value = "hor",'),
]

# Telas ajustadas a mao no Studio: o export salvo em studio/ e a entrega.
# ScreenJetBlastForms (2026-09-24) e o MODELO do padrao aplicado abaixo.
DO_STUDIO = ['ScreenJetBlastForms']

# Padrao medido no ScreenJetBlastForms ajustado no Studio:
# linha 1 = Data/hora + Aeroporto; as demais caixas descem para a linha 2,
# alinhadas a esquerda com a Data; o corpo desce e encolhe.
FOLGA_AERO = 16       # entre a caixa da Data e a do Aeroporto
LARG_CAIXA = 240      # caixa Aeroporto (combo = 220)
LARG_LEGENDA = 95
DESCE_LINHA = 71      # linha 2 = linha 1 + 71
DESCE_CORPO = 69
ENCOLHE_CORPO = 60
LARG_DATA = 350       # caixa da Data (Acesso Indevido tinha 1030, vazia a direita)


def props_combo(k):
    """Regra do campo (igual em todas as telas); o estilo vem da propria tela."""
    return {
        'AllowEmptySelection': '=true',
        'BorderColor': '=If(varPerfilSafety And IsBlank(Self.Selected.Aeroporto), varBordaDefault, RGBA(175, 191, 224, 1))',
        'Default': '=varAeroUser',
        'DisabledColor': '=RGBA(0, 0, 0, 1)',
        'DisabledFill': '=RGBA(235, 235, 235, 1)',
        'DisplayMode': TRAVA,
        'Items': ITENS_AERO,
        'Items.Value': '=Aeroporto',
    }


def filhos(tela_yaml, nome):
    def achar(ch):
        for it in ch or []:
            for n, b in it.items():
                if n == nome:
                    return b
                r = achar(b.get('Children'))
                if r:
                    return r
    b = achar(list(tela_yaml['Screens'].values())[0].get('Children'))
    if not b:
        falhar(f'{nome} nao encontrado')
    return [(n, cb) for it in b.get('Children') or [] for n, cb in it.items()], b


def estilo(props, tirar):
    return {k: v for k, v in props.items() if k not in tirar and '\n' not in v}


def num(v, rotulo):
    if not re.fullmatch(r'=-?\d+', v or ''):
        falhar(f'{rotulo}: valor nao numerico {v!r}')
    return int(v[1:])


def trocar_prop(txt, nome, prop, velho, novo, tela):
    _, _, ind = faixa(txt, nome)
    return sub_em(txt, nome, f'\n{" " * (ind + 6)}{prop}: {velho}\n',
                  f'\n{" " * (ind + 6)}{prop}: {novo}\n', f'{tela}: {nome}.{prop}')


def caixa_na_linha(txt, tela, k, cont):
    """Padrao do ScreenJetBlastForms: Aeroporto ao lado da Data na linha 1,
    demais caixas na linha 2, corpo mais abaixo."""
    y = yaml.load(txt, Loader=yaml.BaseLoader)
    ch, cb = filhos(y, cont)
    larg_cont = num(cb['Properties']['Width'], f'{tela}: {cont}.Width')
    caixas = sorted(((n, b) for n, b in ch if b['Control'] == 'Rectangle@2.3.0'
                     and b['Properties'].get('Height') == '=45'),
                    key=lambda t: num(t[1]['Properties']['X'], t[0]))
    if not caixas:
        falhar(f'{tela}: linha de cima sem caixas')
    data_n, data = caixas[0]
    outras = caixas[1:]
    dx0 = num(data['Properties']['X'], data_n)
    dw = num(data['Properties']['Width'], data_n)
    ry = num(data['Properties']['Y'], data_n)
    grupo_data = data.get('Group')
    membros_data = [(n, b) for n, b in ch if grupo_data and b.get('Group') == grupo_data and n != data_n]
    legenda = [b for n, b in membros_data if b['Control'] == 'Label@2.5.1'
               and num(b['Properties']['Y'], n) < ry]
    hora = [b for n, b in membros_data if b['Control'] == 'Classic/DropDown@2.3.1'
            and re.search(r'Hora(Cadastro)?$', n)]
    if len(legenda) != 1 or len(hora) != 1:
        falhar(f'{tela}: caixa da Data sem legenda/combo de hora unicos')
    legenda = legenda[0]['Properties']

    # caixa da Data larga e vazia a direita (Acesso Indevido): volta para a largura padrao
    if dw > LARG_DATA:
        fim_membros = max(num(b['Properties']['X'], n) + num(b['Properties']['Width'], n)
                          for n, b in membros_data)
        if fim_membros > dx0 + LARG_DATA - 5:
            falhar(f'{tela}: campos da Data nao cabem em {LARG_DATA}')
        txt = trocar_prop(txt, data_n, 'Width', f'={dw}', f'={LARG_DATA}', tela)
        dw = LARG_DATA

    x = dx0 + dw + FOLGA_AERO
    rct = estilo(data['Properties'], {'X', 'Y', 'Width'})
    rct.update({'Width': f'={LARG_CAIXA}', 'X': f'={x}', 'Y': f'={ry}'})
    lbl = estilo(legenda, {'X', 'Y', 'Width', 'Text', 'Tooltip'})
    lbl.update({'Text': '="Aeroporto:"', 'Width': f'={LARG_LEGENDA}', 'X': f'={x + 8}',
                'Y': legenda['Y']})
    cmb = estilo(hora[0]['Properties'], {'X', 'Y', 'Width', 'Default', 'DisplayMode',
                                         'BorderColor', 'Items', 'Items.Value'})
    cmb.update(props_combo(k))
    cmb.update({'Width': f'={LARG_CAIXA - 20}', 'X': f'={x + 10}', 'Y': f'={ry + 8}'})
    if x + LARG_CAIXA > larg_cont:
        falhar(f'{tela}: caixa Aeroporto nao cabe em {cont}')

    if outras:
        grupos = {b.get('Group') for _, b in outras}
        if None in grupos or grupo_data in grupos:
            falhar(f'{tela}: caixa da linha de cima sem grupo proprio')
        desl_x = dx0 - num(outras[0][1]['Properties']['X'], outras[0][0])
        for n, b in ch:
            p = b['Properties']
            if b.get('Group') in grupos:
                nx = num(p['X'], n) + desl_x
                if nx + num(p['Width'], n) > larg_cont:
                    falhar(f'{tela}: {n} sai de {cont} na linha 2')
                txt = trocar_prop(txt, n, 'X', p['X'], f'={nx}', tela)
                txt = trocar_prop(txt, n, 'Y', p['Y'], f'={num(p["Y"], n) + DESCE_LINHA}', tela)
            elif b['Control'].startswith('GroupContainer') and not b.get('Group'):
                txt = trocar_prop(txt, n, 'Y', p['Y'], f'={num(p["Y"], n) + DESCE_CORPO}', tela)
                h = p['Height']
                m = re.fullmatch(r'=Parent\.Height - (\d+)', h)
                if m:
                    nh = f'=Parent.Height - {int(m.group(1)) + ENCOLHE_CORPO}'
                else:
                    nh = f'={num(h, n) - ENCOLHE_CORPO}'
                txt = trocar_prop(txt, n, 'Height', h, nh, tela)
            elif b.get('Group') != grupo_data:
                falhar(f'{tela}: {n} fora de grupo e fora do corpo; nao sei para onde vai')

    _, fim_c, ind = faixa(txt, cont)
    novos = (controle(f'rctFrm{k}Aeroporto', 'Rectangle@2.3.0', rct)
             + controle(f'lblFrm{k}Aeroporto', 'Label@2.5.1', lbl)
             + controle(f'cmbFrm{k}Aeroporto', 'Classic/DropDown@2.3.1', cmb))
    return txt[:fim_c] + ''.join(' ' * (ind + 6) + l + '\n' for l in novos) + txt[fim_c:]


def campo_na_coluna(txt, tela, k, antes_de, rotulo_modelo, combo_modelo):
    """Rotulo + combo numa coluna AutoLayout, logo depois do campo de Data."""
    y = yaml.load(txt, Loader=yaml.BaseLoader)

    def props_de(nome):
        def achar(ch):
            for it in ch or []:
                for n, b in it.items():
                    if n == nome:
                        return b['Properties']
                    r = achar(b.get('Children'))
                    if r:
                        return r
        return achar(list(y['Screens'].values())[0].get('Children'))
    lbl = estilo(props_de(rotulo_modelo), {'X', 'Y', 'Text'})
    lbl['Text'] = '="Aeroporto:"'
    cmb = estilo(props_de(combo_modelo), {'X', 'Y', 'Default', 'DisplayMode', 'BorderColor',
                                          'Items', 'Items.Value', 'OnChange'})
    cmb.update(props_combo(k))
    return inserir_antes(txt, antes_de,
                         controle(f'lblFrm{k}Aeroporto', 'Label@2.5.1', lbl)
                         + controle(f'cmbFrm{k}Aeroporto', 'Classic/DropDown@2.3.1', cmb))


def editar_formula_salvar(txt, k, err, prefixo, cond):
    """Validacao + Patch. `txt` pode ser o arquivo (blocos |) ou o valor decodificado."""
    cmb = f'cmbFrm{k}Aeroporto'
    padrao = re.compile(r'\n([ ]*)Switch\(\n\1    true,\n\1    ' + re.escape(cond))
    ms = list(padrao.finditer(txt))
    if len(ms) != 1:
        falhar(f'{k}: Switch de validacao achado {len(ms)} vezes')
    m = ms[0]
    b = m.group(1) + '    '
    ramo = (
        f'{b}varPerfilSafety And IsBlank({cmb}.Selected.Aeroporto),\n'
        f'{b}UpdateContext(\n'
        f'{b}    {{\n'
        f'{b}        {err}: true,\n'
        f'{b}        varBordaDefault: Color.Red\n'
        f'{b}    }}\n'
        f'{b}),\n'
    )
    pos = m.end() - len(cond) - len(b)
    txt = txt[:pos] + ramo + txt[pos:]
    txt = sub(txt, f'{prefixo}_bloco: varBlocoUser',
              f'{prefixo}_bloco: If(varPerfilSafety, {cmb}.Selected.Bloco, varBlocoUser)',
              f'{k}: Patch bloco')
    txt = sub(txt, f'{prefixo}_aeroporto: varAeroUser',
              f'{prefixo}_aeroporto: If(varPerfilSafety, {cmb}.Selected.Aeroporto, varAeroUser)',
              f'{k}: Patch aeroporto')
    return txt


def codificar_aspas(valor):
    return '"' + valor.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def editar_onselect_entre_aspas(txt, marcador, funcao, rotulo):
    """OnSelect gravado pelo Studio como escalar entre aspas numa linha so."""
    linhas = txt.split('\n')
    idx = [i for i, l in enumerate(linhas)
           if l.lstrip().startswith('OnSelect: "') and marcador in l]
    if len(idx) != 1:
        falhar(f'{rotulo}: OnSelect entre aspas achado {len(idx)} vezes')
    linha = linhas[idx[0]]
    prefixo, escalar = linha.split('OnSelect: ', 1)
    valor = yaml.safe_load('v: ' + escalar)['v']
    if codificar_aspas(valor) != escalar:
        falhar(f'{rotulo}: codificador nao reproduz o escalar do Studio; abortando')
    linhas[idx[0]] = prefixo + 'OnSelect: ' + codificar_aspas(funcao(valor))
    return '\n'.join(linhas)


def formulario_patch(tela, k, onde, reset, err, prefixo, cond):
    txt = ler(tela)
    cmb = f'cmbFrm{k}Aeroporto'
    garantir_ausente(txt, [cmb, f'lblFrm{k}Aeroporto', f'rctFrm{k}Aeroporto'], tela)

    if onde[0] == 'linha':
        txt = caixa_na_linha(txt, tela, k, onde[1])
    else:
        txt = campo_na_coluna(txt, tela, k, *onde[1:])

    marcador = f'{prefixo}_aeroporto: varAeroUser'
    linha = [l for l in txt.split('\n') if marcador in l]
    if len(linha) == 1 and linha[0].lstrip().startswith('OnSelect: "'):
        txt = editar_onselect_entre_aspas(
            txt, marcador, lambda v: editar_formula_salvar(v, k, err, prefixo, cond), tela)
    else:
        txt = editar_formula_salvar(txt, k, err, prefixo, cond)

    ini, fim, _ = faixa(txt, reset)
    seg, n = re.subn(r'(OnSelect: \|[-+]?\n)( *)=',
                     lambda m: f'{m.group(1)}{m.group(2)}=Reset({cmb});\n{m.group(2)}',
                     txt[ini:fim], count=1)
    if n != 1:
        falhar(f'{tela}: OnSelect de {reset} nao encontrado')
    txt = txt[:ini] + seg + txt[fim:]

    if tela == 'ScreenDerramamentoForms':
        txt = sub(txt,
                  '"Aeroporto: " & varIATAUser & " - " & varAeroUser & " - Bloco " & varBlocoUser,',
                  f'"Aeroporto: " & If(varPerfilSafety, {cmb}.Selected.IATA & " - " & '
                  f'{cmb}.Selected.Aeroporto & " - Bloco " & {cmb}.Selected.Bloco, '
                  'varIATAUser & " - " & varAeroUser & " - Bloco " & varBlocoUser),',
                  'DerFlu: texto da notificacao')
    gravar(tela, txt)


# ---------------------------------------------------------------------------
# 2) EditForms com cartao de aeroporto em texto: combo dentro do cartao
# ---------------------------------------------------------------------------

def combo_cartao(nome, chave_rotulo):
    return controle(nome, 'Classic/DropDown@2.3.1', {
        'AllowEmptySelection': '=true',
        'BorderColor': '=RGBA(122, 138, 143, 1)',
        'BorderThickness': '=1',
        'ChevronBackground': '=RGBA(0, 0, 0, 0)',
        'ChevronFill': '=RGBA(122, 138, 143, 1)',
        'ChevronHoverFill': '=RGBA(0, 0, 0, 1)',
        'Default': '=Parent.Default',
        'DisabledColor': '=RGBA(0, 0, 0, 1)',
        'DisabledFill': '=RGBA(235, 235, 235, 1)',
        'DisplayMode': TRAVA,
        'Font': "=Font.'Open Sans'",
        'Height': '=32',
        'HoverFill': '=RGBA(186, 202, 226, 1)',
        'Items': ITENS_AERO,
        'Items.Value': '=Aeroporto',
        'Size': '=11',
        'Visible': '=Parent.DisplayMode = DisplayMode.Edit',
        'Width': '=Parent.Width - 48',
        'X': '=24',
        'Y': f'={chave_rotulo}.Y + {chave_rotulo}.Height + 4',
    })


def cartao_texto(txt, tela, cartao, valor, chave_rotulo, erro, cmb):
    """Texto do cartao so aparece fora da edicao; na edicao aparece o combo."""
    garantir_ausente(txt, [cmb], tela)
    txt = sub_em(txt, cartao, f'Update: ={valor}.Value',
                 f'Update: =If(varPerfilSafety, {cmb}.Selected.Aeroporto, {valor}.Value)',
                 f'{tela}: Update de {cartao}')
    ini, fim, ind = faixa(txt, valor)
    seg = sub(txt[ini:fim], '\n' + ' ' * (ind + 6) + 'Value: =Parent.Default\n',
              '\n' + ' ' * (ind + 6) + 'Value: =Parent.Default\n'
              + ' ' * (ind + 6) + 'Visible: =Parent.DisplayMode <> DisplayMode.Edit\n',
              f'{tela}: Value de {valor}')
    txt = txt[:ini] + seg + txt[fim:]
    return inserir_antes(txt, erro, combo_cartao(cmb, chave_rotulo))


def tela_fod():
    tela = 'ScreenFOD'
    txt = ler(tela)
    cmb = 'cmbFrmFODAeroporto'
    # O default "Sede pega o aeroporto do filtro" vira a regra geral: nasce com
    # o aeroporto do usuario e so o View_safety troca, no proprio combo.
    a, b = ' ' * 48, ' ' * 52
    txt = sub_em(txt, 'aeroporto_DataCard1',
                 f'ThisItem.aeroporto,\n{a}If(\n{b}varPerfilUser = "Sede",\n'
                 f'{b}ComboboxCanvasAeroporto.Selected.Value,\n{b}varAeroUser\n{a})\n',
                 f'ThisItem.aeroporto,\n{a}varAeroUser\n',
                 'FOD: Default do aeroporto')
    txt = cartao_texto(txt, tela, 'aeroporto_DataCard1', 'DataCardValue11',
                       'DataCardKey11', 'ErrorMessage11', cmb)
    gravar(tela, txt)


def tela_cso():
    tela = 'ScreenCSO'
    txt = ler(tela)
    cmb = 'cmbFrmCSOAeroporto'
    txt = sub_em(txt, 'Aeroporto_DataCard2', 'DisplayMode: =DisplayMode.View',
                 'DisplayMode: =If(varPerfilSafety, Parent.DisplayMode, DisplayMode.View)',
                 'CSO: DisplayMode do cartao')
    txt = cartao_texto(txt, tela, 'Aeroporto_DataCard2', 'DataCardValue34',
                       'DataCardKey39', 'ErrorMessage39', cmb)
    gravar(tela, txt)


def tela_vistoria():
    tela = 'ScreenVistoriaSafetyFauna'
    txt = ler(tela)
    cmb = 'cmbFrmVistoriaAeroporto'
    txt = sub_em(txt, 'Aeroporto_DataCard3', 'Visible: =false', 'Visible: =true',
                 'Vistoria: cartao visivel')
    txt = sub_em(txt, 'Aeroporto_DataCard3', 'Required: =false', 'Required: =true',
                 'Vistoria: aeroporto obrigatorio')
    txt = cartao_texto(txt, tela, 'Aeroporto_DataCard3', 'DataCardValue47',
                       'DataCardKey53', 'ErrorMessage55', cmb)
    # Bloco (cartao oculto) acompanha o aeroporto escolhido
    txt = sub_em(txt, 'Bloco_DataCard1', 'Update: =DataCardValue46.Value',
                 f'Update: =If(varPerfilSafety, {cmb}.Selected.Bloco, DataCardValue46.Value)',
                 'Vistoria: Update do Bloco')
    gravar(tela, txt)


# ---------------------------------------------------------------------------
# 3) ScreenFaunaForms: trava por View_safety no lugar do perfil "Base"
# ---------------------------------------------------------------------------

def tela_fauna():
    tela = 'ScreenFaunaForms'
    txt = ler(tela)
    for s in ('4', '3', '2'):
        for nome in (f'ComboboxCanvasBloco_{s}', f'ComboboxCanvasAeroporto_{s}'):
            txt = sub_em(txt, nome,
                         'DisplayMode: =If(varPerfilUser = "Base", DisplayMode.Disabled, DisplayMode.Edit)',
                         'DisplayMode: ' + TRAVA, f'Fauna: DisplayMode de {nome}')
        # sem View_safety: sempre o bloco/aeroporto do usuario;
        # com View_safety: o default de antes (Sede em branco, Base no proprio)
        txt = sub_em(txt, f'ComboboxCanvasBloco_{s}', 'varPerfilUser = "Sede",',
                     'varPerfilSafety And varPerfilUser = "Sede",', f'Fauna: Default Bloco_{s}')
        txt = sub_em(txt, f'ComboboxCanvasAeroporto_{s}', 'varPerfilUser = "Base",',
                     '!varPerfilSafety Or varPerfilUser = "Base",', f'Fauna: Default Aeroporto_{s}')
    gravar(tela, txt)


def copiar_do_studio(tela):
    """Tela ajustada a mao no Studio: entrega o export salvo em studio/."""
    with open(os.path.join(BASE, 'studio', tela + '.pa.yaml'), encoding='utf-8') as f:
        txt = f.read().replace('\r\n', '\n')
    if '%DATACARD_' in txt:
        falhar(f'{tela}: export do Studio com %DATACARD_ (tirar antes)')
    gravar(tela, txt)


def main():
    for args in PATCH:
        formulario_patch(*args)
    for tela in DO_STUDIO:
        copiar_do_studio(tela)
    tela_fod()
    tela_cso()
    tela_vistoria()
    tela_fauna()
    print('ok:', len(PATCH) + len(DO_STUDIO) + 4, 'telas em', OUT)


if __name__ == '__main__':
    main()
