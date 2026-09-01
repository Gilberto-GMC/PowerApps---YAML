# -*- coding: utf-8 -*-
import sys, os, re, io, yaml
sys.path.insert(0, os.path.dirname(__file__))
from pautil import HDR, ind, block_end, find_line, split_screen, reindent, prop_block, set_prop, find_ctrl
from fx import replace_calls, find_call, split_args
from modulos import MODULOS, LAYOUT_FORM

SRC = "msapp/Src"
OUT = "out"

# ─────────────────────────────────────────────────────────────────────────────
# 0. normaliza escalar entre aspas -> bloco literal
# ─────────────────────────────────────────────────────────────────────────────
def normalizar_escalares(lines):
    out = []
    for l in lines:
        m = re.match(r'^(\s*)([A-Za-z_][\w.\']*): (".*")\s*$', l)
        if m and '\\n' in m.group(3):
            pad, nome, val = m.groups()
            texto = yaml.safe_load(val)
            out.append(f"{pad}{nome}: |-")
            for t in texto.split('\n'):
                out.append((pad + '  ' + t) if t.strip() else '')
            continue
        out.append(l)
    return out

# ─────────────────────────────────────────────────────────────────────────────
# 1. galeria: Items delegável + escopo de segurança obrigatório
# ─────────────────────────────────────────────────────────────────────────────
def items_galeria(m):
    pfx, tab = m['pfx'], m['tabela']
    extra = ""
    for col, ctrl in m['extraFiltros']:
        extra += f"""
                            IsBlank({ctrl}.Selected.Value) ||
                            {col} = {ctrl}.Selected.Value,"""
    return f'''=// ═══════════════════════════════════════════════════════════════════
// ESCOPO DE SEGURANÇA (não é filtro de usuário — é regra de acesso).
//   varEscopoAero  <> branco  -> perfil Base, travado no próprio aeroporto
//   varEscopoBloco <> branco  -> perfil Bloco, travado no próprio bloco
// Antes esta galeria consultava a lista inteira quando o filtro de aeroporto
// ficava em branco, e o perfil Base enxergava todos os aeroportos.
//
// DELEGAÇÃO: o recorte por aeroporto/bloco + intervalo de datas é feito no
// SharePoint (delegável). Só status, tipo e busca por ID — que já operam sobre
// o conjunto recortado — rodam localmente.
// ═══════════════════════════════════════════════════════════════════
With(
    {{
        _aero: If(
            !IsBlank(varEscopoAero),
            varEscopoAero,
            {m['fAero']}.Selected.Aeroporto
        ),
        _bloco: If(
            !IsBlank(varEscopoBloco),
            varEscopoBloco,
            {m['fBloco']}.Selected.Value
        ),
        _ini: Coalesce(
            {m['fIni']}.SelectedDate,
            nfDataPiso
        ),
        _fim: DateAdd(
            Coalesce(
                {m['fFim']}.SelectedDate,
                Today()
            ),
            1,
            TimeUnit.Days
        )
    }},
    SortByColumns(
        Filter(
            Switch(
                true,
                !IsBlank(_aero),
                Filter(
                    {tab},
                    {pfx}_aeroporto = _aero,
                    {pfx}_data >= _ini,
                    {pfx}_data < _fim
                ),
                !IsBlank(_bloco),
                Filter(
                    {tab},
                    {pfx}_bloco = _bloco,
                    {pfx}_data >= _ini,
                    {pfx}_data < _fim
                ),
                Filter(
                    {tab},
                    {pfx}_data >= _ini,
                    {pfx}_data < _fim
                )
            ),{extra}
            IsBlank({m['fStatus']}.Selected.Value) ||
            Status = {m['fStatus']}.Selected.Value,
            IsBlank({m['fBusca']}.Text) ||
            ID = Value({m['fBusca']}.Text)
        ),
        "ID",
        SortOrder.Descending
    )
)'''

def trocar_prop_multilinha(lines, ctrl_idx, nome, novo_valor):
    """substitui uma propriedade (bloco literal) inteira por novo conteúdo"""
    pi, pe = prop_block(lines, ctrl_idx)
    if pi < 0:
        return False
    pind = ind(lines[pi]) + 2
    k = pi + 1
    while k < pe:
        if ind(lines[k]) == pind and re.match(r'^\s*' + re.escape(nome) + r':', lines[k]):
            ke = block_end(lines, k)
            novo = [f"{' ' * pind}{nome}: |-"]
            for t in novo_valor.split('\n'):
                novo.append((' ' * (pind + 2) + t) if t.strip() else '')
            lines[k:ke] = novo
            return True
        k += 1
    return False

# ─────────────────────────────────────────────────────────────────────────────
# 2. dropdowns de filtro: escopo travado por perfil
# ─────────────────────────────────────────────────────────────────────────────
def ajustar_filtros(lines, m):
    i = find_ctrl(lines, m['fBloco'])
    if i >= 0:
        set_prop(lines, i, 'Default', '|-\n' + _pad("""=If(
    varPerfilUser = "Base" || varPerfilUser = "Bloco",
    varBlocoUser,
    Blank()
)""", lines, i))
        set_prop(lines, i, 'DisplayMode', '|-\n' + _pad("""=If(
    varPerfilUser = "Base" || varPerfilUser = "Bloco",
    DisplayMode.View,
    DisplayMode.Edit
)""", lines, i))
        set_prop(lines, i, 'Items', '=nfBlocos')
        set_prop(lines, i, 'Items.Value', '=Value')
    j = find_ctrl(lines, m['fAero'])
    if j >= 0:
        set_prop(lines, j, 'Default', '|-\n' + _pad("""=If(
    varPerfilUser = "Base",
    varAeroUser,
    Blank()
)""", lines, j))
        set_prop(lines, j, 'DisplayMode', '|-\n' + _pad("""=If(
    varPerfilUser = "Base",
    DisplayMode.View,
    DisplayMode.Edit
)""", lines, j))
        set_prop(lines, j, 'Items', '|-\n' + _pad(f"""=Sort(
    Filter(
        colAeros,
        !IsBlank(Aeroporto),
        IsBlank({m['fBloco']}.Selected.Value) || Bloco = {m['fBloco']}.Selected.Value
    ),
    Aeroporto
)""", lines, j))
        set_prop(lines, j, 'Items.Value', '=Aeroporto')
    return lines

def _pad(txt, lines, ctrl_idx):
    pi, _ = prop_block(lines, ctrl_idx)
    pind = ind(lines[pi]) + 4
    return '\n'.join((' ' * pind + t) if t.strip() else '' for t in txt.split('\n'))

# ─────────────────────────────────────────────────────────────────────────────
# 3. faixa de aeroporto no formulário
# ─────────────────────────────────────────────────────────────────────────────
def faixa_aeroporto(m, base):
    k = m['key']
    p = ' ' * base
    return f'''{p}- cntFaixaAero{k}:
{p}    Control: GroupContainer@1.5.0
{p}    Variant: AutoLayout
{p}    Properties:
{p}      BorderStyle: =BorderStyle.None
{p}      DropShadow: =DropShadow.None
{p}      Fill: =nfCorFundoFraco
{p}      FillPortions: =0
{p}      Height: =52
{p}      LayoutAlignItems: =LayoutAlignItems.Center
{p}      LayoutDirection: =LayoutDirection.Horizontal
{p}      LayoutGap: =12
{p}      LayoutMaxHeight: =
{p}      LayoutMaxWidth: =
{p}      PaddingBottom: =10
{p}      PaddingLeft: =20
{p}      PaddingRight: =20
{p}      PaddingTop: =10
{p}      RadiusBottomLeft: =0
{p}      RadiusBottomRight: =0
{p}      RadiusTopLeft: =0
{p}      RadiusTopRight: =0
{p}      Width: =Parent.Width
{p}    Children:
{p}      - lblFaixaAero{k}:
{p}          Control: Label@2.5.1
{p}          Properties:
{p}            AlignInContainer: =AlignInContainer.Center
{p}            Color: =nfCorTextoFraco
{p}            Font: =Font.'Segoe UI'
{p}            FontWeight: =FontWeight.Semibold
{p}            Height: =32
{p}            LayoutMaxHeight: =
{p}            LayoutMaxWidth: =
{p}            LayoutMinWidth: =0
{p}            Size: =11
{p}            Text: ="Registrar ocorrência em:"
{p}            VerticalAlign: =VerticalAlign.Middle
{p}            Width: =170
{p}      - cmbFrm{k}Bloco:
{p}          Control: Classic/DropDown@2.3.1
{p}          Properties:
{p}            AllowEmptySelection: =false
{p}            BorderColor: =nfCorBorda
{p}            BorderThickness: =1
{p}            ChevronBackground: =RGBA(0, 0, 0, 0)
{p}            ChevronFill: =nfCorPrimaria
{p}            ChevronHoverBackground: =RGBA(0, 0, 0, 0)
{p}            ChevronHoverFill: =nfCorPrimaria
{p}            Default: =varBlocoUser
{p}            DisplayMode: |-
{p}              =// Só o perfil Sede escolhe o bloco. Base e Bloco ficam travados.
{p}              If(
{p}                  varPerfilUser = "Sede",
{p}                  DisplayMode.Edit,
{p}                  DisplayMode.View
{p}              )
{p}            Fill: =RGBA(250, 250, 250, 1)
{p}            Height: =32
{p}            HoverFill: =RGBA(255, 255, 255, 1)
{p}            Items: =nfBlocos
{p}            Items.Value: =Value
{p}            LayoutMaxHeight: =
{p}            LayoutMaxWidth: =
{p}            LayoutMinHeight: =0
{p}            LayoutMinWidth: =0
{p}            SelectionColor: =RGBA(255, 255, 255, 1)
{p}            SelectionFill: =nfCorPrimaria
{p}            Size: =11
{p}            Width: =150
{p}      - cmbFrm{k}Aeroporto:
{p}          Control: Classic/DropDown@2.3.1
{p}          Properties:
{p}            AllowEmptySelection: =false
{p}            BorderColor: |-
{p}              =If(
{p}                  IsBlank(Self.Selected.Aeroporto),
{p}                  varBordaDefault,
{p}                  nfCorBorda
{p}              )
{p}            BorderThickness: =1
{p}            ChevronBackground: =RGBA(0, 0, 0, 0)
{p}            ChevronFill: =nfCorPrimaria
{p}            ChevronHoverBackground: =RGBA(0, 0, 0, 0)
{p}            ChevronHoverFill: =nfCorPrimaria
{p}            Default: =varAeroUser
{p}            DisplayMode: |-
{p}              =// Perfil Base grava sempre no próprio aeroporto (só leitura).
{p}              // Bloco e Sede escolhem dentro do que o bloco acima permite.
{p}              If(
{p}                  varPerfilUser = "Base",
{p}                  DisplayMode.View,
{p}                  DisplayMode.Edit
{p}              )
{p}            Fill: =RGBA(250, 250, 250, 1)
{p}            Height: =32
{p}            HoverFill: =RGBA(255, 255, 255, 1)
{p}            Items: |-
{p}              =Sort(
{p}                  Filter(
{p}                      colAeros,
{p}                      !IsBlank(Aeroporto),
{p}                      Bloco = cmbFrm{k}Bloco.Selected.Value
{p}                  ),
{p}                  Aeroporto
{p}              )
{p}            Items.Value: =Aeroporto
{p}            LayoutMaxHeight: =
{p}            LayoutMaxWidth: =
{p}            LayoutMinHeight: =0
{p}            LayoutMinWidth: =0
{p}            SelectionColor: =RGBA(255, 255, 255, 1)
{p}            SelectionFill: =nfCorPrimaria
{p}            Size: =11
{p}            Width: =230
{p}      - lblProto{k}:
{p}          Control: Label@2.5.1
{p}          Properties:
{p}            AlignInContainer: =AlignInContainer.Center
{p}            Color: =nfCorPrimaria
{p}            Font: =Font.'Segoe UI'
{p}            FontWeight: =FontWeight.Semibold
{p}            Height: =32
{p}            LayoutMaxHeight: =
{p}            LayoutMaxWidth: =
{p}            LayoutMinWidth: =0
{p}            Size: =11
{p}            Text: |-
{p}              =LookUp(
{p}                  colAeros,
{p}                  Aeroporto = cmbFrm{k}Aeroporto.Selected.Aeroporto
{p}              ).IATA & "-{m['proto']}-<novo>"
{p}            Tooltip: ="Protocolo que será gerado ao salvar."
{p}            VerticalAlign: =VerticalAlign.Middle
{p}            Width: =210
'''

# ─────────────────────────────────────────────────────────────────────────────
# 4. reescrita de navegação interna do módulo
# ─────────────────────────────────────────────────────────────────────────────
def reescrever_nav(texto, m):
    alvos = {m['lista']: 'lista', m['forms']: 'form', m['det']: 'detalhe'}

    def fn(args, raw, col):
        if not args:
            return None
        alvo = args[0].strip()
        if alvo not in alvos:
            return None
        vista = alvos[alvo]
        ctx = args[2].strip() if len(args) > 2 else ''
        p = ' ' * col
        if ctx and ctx.startswith('{'):
            return (f'Set(\n{p}    var_vista,\n{p}    "{vista}"\n{p});\n'
                    f'{p}UpdateContext(\n{p}    ' +
                    '\n'.join((p + '    ' + l.strip()) if i else l.strip()
                              for i, l in enumerate(ctx.split('\n'))) +
                    f'\n{p})')
        return f'Set(\n{p}    var_vista,\n{p}    "{vista}"\n{p})'

    texto = replace_calls(texto, 'Navigate', fn)
    # var_navigateSucess aponta para a tela consolidada
    texto = texto.replace(f'var_navigateSucess: {m["lista"]}',
                          f'var_navigateSucess: {m["nova"]}')
    return texto

# ─────────────────────────────────────────────────────────────────────────────
# 5. cirurgia na gravação: ID real do SharePoint + trava + guardas
# ─────────────────────────────────────────────────────────────────────────────
def remover_campo(texto, nome):
    """remove 'nome: <expr>' de um literal de registro, com balanceamento.

    Trata os dois casos: campo no meio (consome a vírgula seguinte) e campo
    no fim (consome a vírgula anterior, mantendo a chave de fechamento na
    própria linha).
    """
    pat = re.compile(r'\n(\s*)' + re.escape(nome) + r':\s')
    m = pat.search(texto)
    if not m:
        return texto, False
    i = m.end()
    depth, q, ultimo_nl = 0, None, i
    while i < len(texto):
        c = texto[i]
        if q:
            if c == q:
                q = None
            i += 1
            continue
        if c in '"\'':
            q = c; i += 1; continue
        if c == '\n':
            ultimo_nl = i
        if c in '([{':
            depth += 1
        elif c in ')]}':
            if depth == 0:
                # era o último campo do registro
                pre = texto[:m.start()].rstrip()
                if pre.endswith(','):
                    pre = pre[:-1]
                return pre + texto[ultimo_nl:], True
            depth -= 1
        elif c == ',' and depth == 0:
            return texto[:m.start()] + texto[i + 1:], True
        i += 1
    return texto, False


def cirurgia_gravacao(texto, m):
    tab, pfx, k, vid = m['tabela'], m['pfx'], m['key'], m['varId']

    if vid not in texto:
        raise SystemExit(f"[{k}] variável de ID '{vid}' não existe no formulário de origem")

    # 5-. o cálculo do ID no cliente (max + 1) some: era uma consulta não
    #     delegável a cada gravação e a origem dos protocolos duplicados.
    texto, achou = remover_campo(texto, vid)
    if not achou:
        raise SystemExit(f"[{k}] cálculo do ID '{vid}' não localizado para remoção")

    # 5a. aeroporto e bloco vêm do formulário, não mais do perfil do usuário
    texto = re.sub(
        r'(\n(\s*))' + pfx + r'_aeroporto:\s*varAeroUser',
        lambda mt: f"{mt.group(1)}{pfx}_aeroporto: cmbFrm{k}Aeroporto.Selected.Aeroporto",
        texto)
    texto = re.sub(
        r'(\n(\s*))' + pfx + r'_bloco:\s*varBlocoUser',
        lambda mt: (f"{mt.group(1)}{pfx}_bloco: LookUp(\n"
                    f"{mt.group(2)}    colAeros,\n"
                    f"{mt.group(2)}    Aeroporto = cmbFrm{k}Aeroporto.Selected.Aeroporto\n"
                    f"{mt.group(2)}).Bloco"),
        texto)

    # 5b. o Patch do pai passa a devolver o registro gravado
    r = find_call(texto, 'Patch')
    while r:
        a, b, c = r
        args = split_args(texto[b:c - 1])
        if len(args) >= 2 and args[0].strip() == tab and args[1].strip().startswith('Defaults('):
            break
        r = find_call(texto, 'Patch', c)
    if not r:
        raise SystemExit(f"[{k}] Patch do pai não encontrado")
    a, b, c = r
    ls = texto.rfind('\n', 0, a) + 1
    col = a - ls
    p = ' ' * col
    corpo = texto[a:c]
    # remove o campo <pfx>_id: <var> do registro (passa a ser o ID do SharePoint)
    corpo = re.sub(r'\n\s*' + pfx + r'_id:\s*' + re.escape(vid) + r',', '', corpo)
    _ls = corpo.split('\n')
    corpo_ind = '\n'.join([_ls[0]] + [(' ' * 8 + l) if l.strip() else '' for l in _ls[1:]])
    novo = f'''// ── GRAVAÇÃO ────────────────────────────────────────────────────
{p}// O ID deixou de ser calculado no cliente (max + 1): dois usuários
{p}// salvando ao mesmo tempo geravam o MESMO protocolo e os filhos
{p}// (imagens/envolvidos) iam parar na ocorrência errada.
{p}// Agora grava-se primeiro, lê-se o ID real devolvido pelo SharePoint
{p}// e só então ele é carimbado de volta em {pfx}_id.
{p}UpdateContext(
{p}    {{
{p}        var_regNovo{k}: {corpo_ind}
{p}    }}
{p});
{p}UpdateContext(
{p}    {{{vid}: Coalesce(
{p}        var_regNovo{k}.ID,
{p}        0
{p}    )}}
{p});
{p}If(
{p}    {vid} <= 0,
{p}    // falhou: avisa, libera a tela e não cria nenhum filho órfão
{p}    Notify(
{p}        "Não foi possível gravar a ocorrência. Verifique a conexão e tente novamente.",
{p}        NotificationType.Error,
{p}        6000
{p}    );
{p}    UpdateContext(
{p}        {{
{p}            var_visibleSpiner: false,
{p}            var_salvando{k}: false
{p}        }}
{p}    ),
{p}    Patch(
{p}        {tab},
{p}        var_regNovo{k},
{p}        {{{pfx}_id: {vid}}}
{p}    )
{p})'''
    texto = texto[:a] + novo + texto[c:]

    # 5c. guarda em cada ForAll de filho: nada é gravado sem pai válido
    def guarda(args, raw, col):
        p = ' ' * col
        if 'Defaults(' not in raw or vid not in raw:
            return None
        _ls = ('ForAll(' + raw + ')').split('\n')
        corpo = '\n'.join([_ls[0]] + [(' ' * 4 + l) if l.strip() else '' for l in _ls[1:]])
        return (f'If(\n{p}    {vid} > 0,\n{p}    ' + corpo + f'\n{p})')
    texto = replace_calls(texto, 'ForAll', guarda)

    # 5d. reset do formulário e tela de sucesso só depois de gravação confirmada.
    #     Antes, uma falha no Patch ainda limpava o formulário (perdendo tudo o
    #     que o usuário digitou) e mostrava "Operação realizada com sucesso".
    mm = re.search(r'\n(\s*)Select\((\w+)\);\n\s*Navigate\(', texto)
    if mm:
        r2 = find_call(texto, 'Navigate', mm.end() - len('Navigate('))
        if r2:
            _, _, fimnav = r2
            col = len(mm.group(1))
            ini = mm.start() + 1 + col
            p2 = ' ' * col
            miolo = texto[ini:fimnav]
            _ls = miolo.split('\n')
            miolo = '\n'.join([_ls[0]] + [(' ' * 4 + l) if l.strip() else '' for l in _ls[1:]])
            texto = (texto[:ini] +
                     f'If(\n{p2}    {vid} > 0,\n{p2}    ' + miolo + f'\n{p2})' +
                     texto[fimnav:])
    return texto

# ─────────────────────────────────────────────────────────────────────────────
# 6. trava de reentrância no botão que grava
# ─────────────────────────────────────────────────────────────────────────────
def trava_reentrancia(lines, m):
    k = m['key']
    alvo = f'var_regNovo{k}'
    for i, l in enumerate(lines):
        if re.match(r'^\s*OnSelect: \|', l):
            e = block_end(lines, i)
            corpo = lines[i + 1:e]
            if not any(alvo in c for c in corpo):
                continue
            pind = ind(l)
            cind = pind + 2
            texto = [c[cind:] if c.strip() else '' for c in corpo]
            if texto and texto[0].startswith('='):
                texto[0] = texto[0][1:]
            novo = [
                '=// ── TRAVA DE REENTRÂNCIA ──────────────────────────────────────',
                '// Clique duplo / toque repetido no celular gravava a ocorrência',
                '// duas vezes. A trava expira sozinha em 60s para nunca deixar o',
                '// botão morto se algo falhar no meio.',
                'If(',
                f'    var_salvando{k} And DateDiff(',
                f'        var_salvandoEm{k},',
                '        Now(),',
                '        TimeUnit.Seconds',
                '    ) < 60,',
                '    Notify(',
                '        "Gravação em andamento, aguarde.",',
                '        NotificationType.Warning',
                '    ),',
                '    UpdateContext(',
                '        {',
                f'            var_salvando{k}: true,',
                f'            var_salvandoEm{k}: Now()',
                '        }',
                '    );',
            ]
            corpo_t = ['    ' + t if t.strip() else '' for t in texto]
            while corpo_t and not corpo_t[-1].strip():
                corpo_t.pop()
            if corpo_t and not corpo_t[-1].rstrip().endswith(';'):
                corpo_t[-1] = corpo_t[-1].rstrip() + ';'
            novo += corpo_t
            novo += [
                '    UpdateContext(',
                '        {',
                f'            var_salvando{k}: false,',
                '            var_visibleSpiner: false',
                '        }',
                '    )',
                ')',
            ]
            lines[i + 1:e] = [(' ' * cind + t) if t.strip() else '' for t in novo]
            return lines, True
    return lines, False

# ─────────────────────────────────────────────────────────────────────────────
# 7. montagem da tela consolidada
# ─────────────────────────────────────────────────────────────────────────────
CAB = """# ************************************************************************************************
# AirportNow — Safety & Fauna  ·  {titulo}
#
# ⚠️ LOCALE — ARQUIVO NO FORMATO INVARIANTE ("," para argumentos, ";" para encadear,
#    "." decimal). É assim que a EXIBIÇÃO DE CÓDIGO do Studio lê e grava, mesmo com o
#    Studio em pt-BR. NÃO converta para ";" / ";;": o arquivo para de compilar.
#    A conversão para pt-BR (";" / ";;" / vírgula decimal) só vale para o que é colado
#    na BARRA DE FÓRMULAS — aqui, nada é.
#
# Tela consolidada: {lista} + {forms} + {det}
#
# COLAR EM: Power Apps Studio > nova tela em branco renomeada para "{nova}"
#           > exibição de código (Source Code) > substituir todo o conteúdo.
#
# ESTADO DA TELA — variável global var_vista:
#   "lista"    galeria de ocorrências (padrão ao entrar na tela)
#   "form"     formulário de cadastro
#   "detalhe"  visualização de uma ocorrência
# OnVisible força "lista": ao chegar de fora a tela sempre abre na galeria;
# alternar entre as três visões não dispara OnVisible, então o estado se mantém.
#
# DEPENDE DE (App.Formulas — ver 02_App_Formulas_ptBR.txt):
#   nfAeros · nfBlocos · nfDataPiso
# DEPENDE DE (App.OnStart — ver 01_App.pa.yaml):
#   colAeros · varAeroUser · varBlocoUser · varPerfilUser
#   varEscopoAero · varEscopoBloco · var_vista
# ************************************************************************************************
"""

ONVISIBLE = '''=// Chegando de fora, a tela sempre abre na galeria.
Set(
    var_vista,
    "lista"
);
// Zera o estado de validação do formulário: as bordas vermelhas do
// cadastro anterior não podem reaparecer num formulário novo.
UpdateContext(
    {{
        varBordaDefault: nfCorBorda,
        var_formErro: false,
        var_visibleSpiner: false,
        var_salvando{k}: false,
        var_salvandoEm{k}: Now()
    }}
)
// O ClearCollect(col_{pfx}Registros, ...) que existia aqui foi removido:
// copiava a lista inteira do SharePoint a cada visita à tela e nenhuma
// galeria lia essa coleção. A galeria consulta a lista diretamente,
// com filtro delegável e escopo de segurança por perfil.'''

PREFIXOS = ('colVei', 'derFlu', 'excPista', 'incPista', 'intExt',
            'jetBlast', 'ocoSolo', 'aceIndFauna')


def corrigir_prefixos(texto, m):
    """Conserta colunas coladas de outro módulo.

    Bug real encontrado no export: a galeria de Excursão de Pista lia
    ThisItem.derFlu_aeroporto / _data / _hora e a de Jet Blast lia
    ThisItem.derFlu_aeroporto — colunas que não existem nessas listas, então
    protocolo e data saíam em branco em produção, sem erro no Studio.
    """
    pfx = m['pfx']

    def troca(mt):
        outro, campo = mt.group(1), mt.group(2)
        if outro in PREFIXOS and outro != pfx:
            return f'ThisItem.{pfx}_{campo}'
        return mt.group(0)

    return re.sub(r'ThisItem\.([A-Za-z]+)_([A-Za-z]+)', troca, texto)


def passe_layout(finais, m):
    """Passe de layout: distribuição dos campos e identidade visual Motiva."""
    for vista, ch in finais:
        # 1. Cabeçalho preto -> roxo Motiva. Três por módulo (lista/form/detalhe).
        i = 0
        while i < len(ch):
            if ch[i].strip().startswith('- ContainerHeader'):
                set_prop(ch, i, 'Fill', '=nfCorPrimaria')
            # 2. Faixa preta de 10px sob os filtros: mesma cor do cabeçalho,
            #    para ler como moldura e não como buraco.
            if re.match(r'^\s*- Rectangle6(_\d+)?:$', ch[i]):
                set_prop(ch, i, 'Fill', '=nfCorPrimaria')
            i += 1

    # 3. Corpo do formulário
    fch = finais[1][1]
    for nome, modo, larg in LAYOUT_FORM[m['key']]:
        i = find_ctrl(fch, nome)
        if i < 0:
            raise SystemExit(f"[{m['key']}] container de layout {nome} não encontrado")
        if modo == 'centro':
            # Largura responsiva com teto no conteúdo real medido, e centralizado.
            # Antes: Width fixo 1138 encostado à esquerda, sobrando meia tela vazia.
            set_prop(fch, i, 'Width', f'=Min(Parent.Width - 48, {larg})')
            set_prop(fch, i, 'AlignInContainer', '=AlignInContainer.Center')
            set_prop(fch, i, 'LayoutMinWidth', '=320')
        else:
            # Os blocos de ~500px deixam de empilhar numa coluna e passam a fluir
            # em linha, quebrando sozinhos conforme a largura da janela.
            set_prop(fch, i, 'LayoutDirection', '=LayoutDirection.Horizontal')
            set_prop(fch, i, 'LayoutWrap', '=true')
            set_prop(fch, i, 'LayoutAlignItems', '=LayoutAlignItems.Stretch')
            set_prop(fch, i, 'LayoutJustifyContent', '=LayoutJustifyContent.Center')
            set_prop(fch, i, 'LayoutGap', '=24')
            set_prop(fch, i, 'PaddingLeft', '=24')
            set_prop(fch, i, 'PaddingRight', '=24')
            set_prop(fch, i, 'PaddingTop', '=16')
            set_prop(fch, i, 'PaddingBottom', '=16')
            set_prop(fch, i, 'Width', '=Parent.Width')
    finais[1][1] = fch
    return finais


def montar(m):
    k, pfx = m['key'], m['pfx']
    partes = []
    for chave, vista in (('lista', 'lista'), ('forms', 'form'), ('det', 'detalhe')):
        nome, props, ch = split_screen(f"{SRC}/{m[chave]}.pa.yaml")
        ch = normalizar_escalares(ch)
        partes.append((vista, ch))

    finais = []
    for vista, ch in partes:
        set_prop(ch, 0, 'Visible', f'=var_vista = "{vista}"')
        txt = '\n'.join(ch)
        txt = re.sub(
            r'UpdateContext\(\s*\{\s*var_visibleForms:\s*true,\s*var_visibleMain:\s*false\s*,?\s*\}\s*\)',
            'Set(\n                              var_vista,\n                              "form"\n                          )',
            txt)
        txt = re.sub(r'\n\s*Visible: =var_visibleMain(?=\n)', '', txt)
        txt = corrigir_prefixos(txt, m)
        txt = reescrever_nav(txt, m)
        if vista == 'form':
            txt = cirurgia_gravacao(txt, m)
        finais.append([vista, txt.split('\n')])

    # formulário: faixa de aeroporto logo após o cabeçalho
    fch = finais[1][1]
    ci = find_line(fch, lambda l: l.strip() == 'Children:' and ind(l) == 10)
    if ci < 0:
        raise SystemExit(f"[{k}] Children do container de topo não encontrado")
    j = ci + 1
    while j < len(fch) and not fch[j].strip().startswith('- '):
        j += 1
    fim1 = block_end(fch, j)
    base = ind(fch[j])
    fch[fim1:fim1] = faixa_aeroporto(m, base).rstrip('\n').split('\n')
    finais[1][1] = fch

    # lista: galeria + filtros
    lch = finais[0][1]
    gi = find_ctrl(lch, m['gal'])
    if gi < 0:
        raise SystemExit(f"[{k}] galeria {m['gal']} não encontrada")
    if not trocar_prop_multilinha(lch, gi, 'Items', items_galeria(m)):
        raise SystemExit(f"[{k}] Items da galeria não substituído")
    ajustar_filtros(lch, m)
    finais[0][1] = lch

    # ── Navigate para o CONTAINER de outra visão vira troca de estado ────────
    #    Bug herdado do export: o "voltar" dos Detalhes de Derramamento fazia
    #    Navigate(ScreenContainerDerramementoFluido) — nome de um CONTAINER, não
    #    de uma tela. Nunca funcionou. Depois da consolidação esses containers
    #    são as três visões da mesma tela, então a navegação vira var_vista.
    conteineres = {}
    for vista, ch in finais:
        for l in ch:
            if l.strip().startswith('- ') and ind(l) == 6:
                conteineres[l.strip()[2:-1]] = vista
                break

    def nav_container(args, raw, col):
        if not args:
            return None
        alvo = args[0].strip()
        if alvo not in conteineres:
            return None
        p2 = ' ' * col
        return f'Set(\n{p2}    var_vista,\n{p2}    "{conteineres[alvo]}"\n{p2})'

    for i, (vista, ch) in enumerate(finais):
        finais[i][1] = replace_calls('\n'.join(ch), 'Navigate', nav_container).split('\n')

    finais = passe_layout(finais, m)

    finais[1][1], ok = trava_reentrancia(finais[1][1], m)
    if not ok:
        raise SystemExit(f"[{k}] botão de gravação não encontrado para a trava")

    out = [CAB.format(titulo=m['titulo'], lista=m['lista'], forms=m['forms'],
                      det=m['det'], nova=m['nova']).rstrip('\n')]
    out.append('Screens:')
    out.append(f"  {m['nova']}:")
    out.append('    Properties:')
    out.append('      Fill: =RGBA(255, 255, 255, 1)')
    out.append('      LoadingSpinner: =LoadingSpinner.Data')
    out.append('      OnVisible: |-')
    for t in ONVISIBLE.format(k=k, pfx=pfx).split('\n'):
        out.append(('        ' + t) if t.strip() else '')
    out.append('    Children:')
    for vista, ch in finais:
        out.append(f'      # ══════════════════ VISÃO: {vista.upper()} ══════════════════')
        out += ch
    return '\n'.join(out).rstrip('\n') + '\n'


if __name__ == '__main__':
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    for m in MODULOS:
        if alvo and m['key'] != alvo:
            continue
        txt = montar(m)
        path = f"{OUT}/{m['nova']}.pa.yaml"
        open(path, 'w', encoding='utf-8').write(txt)
        print(f"{m['key']:10s} -> {path}  ({len(txt.splitlines())} linhas)")
