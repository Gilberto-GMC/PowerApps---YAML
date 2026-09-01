#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador das telas PLEM/PRAI a partir de REA/ScreenAcionamentosPlemPrai.pa.yaml.

Estratégia (fidelidade máxima): extração dos containers-overlay por blocos de
texto (sem round-trip YAML), reindentação para o esqueleto da nova tela e
transformações mecânicas controladas:

  T1. UpdateContext({...}) -> Set(a, x); Set(b, y)   (parser ciente de parênteses/aspas)
  T2. Cruzamentos de tela: Set(var_visibleX, true) ganha "; Navigate(TelaDestino, ...)"
  T3. Tokens de tema: RGBA literais -> thm* (definidos em App.Formulas)
  T4. Galerias: DelayItemLoading + LoadingSpinner quando ausentes
  T5. Buscas: DelayOutput: =true em Classic/TextInput de busca
  T6. Referência cruzada ao combo de aeroporto da Home -> var_aeroSelect

Ajustes semânticos pontuais (timer, delegação, IfError, OnVisible) são feitos
manualmente após a geração — este script não tenta reescrevê-los.

Executar duas vezes e conferir que o hash das saídas não muda (checklist LICOES).
"""
import re, hashlib, sys, os

SRC = os.path.join(os.path.dirname(__file__), 'ScreenAcionamentosPlemPrai.pa.yaml')
OUT_DIR = os.path.dirname(__file__) or '.'

# ---------------------------------------------------------------- composição
# containers por tela, em ordem de z (ordem do arquivo original)
SCREENS = {
    'ScreenPlemPraiHome': dict(
        containers=['Container83_78', 'Container83_76', 'Container135_1',
                    'ContainerFormAcionaDetail', 'ContainerExcluirAcionamneto'],
        entry_flags=[],  # Home não tem overlay de entrada: conteúdo é fixo
    ),
    'ScreenPlemPraiNovoAcionamento': dict(
        containers=['ContainerNovoAcionamento', 'ContainerFormOcorrenciaAcionamentos',
                    'ContainerAcionamentoEscolha', 'PopUpLoadConfigFLuxo'],
        entry_flags=['var_visibleEscolhaAcionamento', 'var_visibleNovoAcionamento',
                     'var_visibleFormOcorrenciaAcionamento'],
    ),
    'ScreenPlemPraiMonitoramento': dict(
        containers=['ContainerEmergenciaFluxo', 'PopListaEqp', 'PopLancarAtvManual',
                    'ContainerAcionar', 'PopLancarVitimas', 'ContainerPopUpPrai'],
        entry_flags=['var_visibleFluxogramaAcionamentosReal'],
    ),
    'ScreenPlemPraiFluxogramas': dict(
        containers=['ContainerFluxogramaPRAI', 'ContainerFluxogramaPLEM',
                    'ContainerFluxogramaEscolha'],
        entry_flags=['var_visibleEscolhaFluxograma', 'var_visibleFluxogramaPLEM',
                     'var_visibleFluxogramaPRAI'],
        onvisible_prefix=['Reset(ComboboxCanvasAeroSelectCadFluxo)'],
    ),
    'ScreenPlemPraiFormFluxograma': dict(
        containers=['ContainerFormFluxograma', 'ContainerFluxogramaContatos'],
        entry_flags=['var_visibleFormFluxograma'],
    ),
    'ScreenPlemPraiEquipamentos': dict(
        containers=['ContainerGerenciarEquipamento', 'ContainerFormCadastrarEquipamento',
                    'ContainerExcluirOcoGerais_8', 'ContainerFilterOcoGerais_8',
                    'ContainerEqpEscolha'],
        entry_flags=['var_visibleEscolhaEqp', 'var_visibleGenciarEquipamento'],
    ),
    'ScreenPlemPraiContatos': dict(
        containers=['ContainerConsultarContatos', 'ContainerContatosEscolha'],
        entry_flags=['var_visibleEscolhaContatos', 'var_visibleFormContatosEntidade'],
        onvisible_prefix=['Reset(TextInput1)'],
    ),
}

# flag de overlay -> tela dona (cruzamento gera Navigate)
FLAG_SCREEN = {
    'var_visibleEscolhaAcionamento': 'ScreenPlemPraiNovoAcionamento',
    'var_visibleNovoAcionamento': 'ScreenPlemPraiNovoAcionamento',
    'var_visibleFormOcorrenciaAcionamento': 'ScreenPlemPraiNovoAcionamento',
    'var_visibleConfigFluxo': 'ScreenPlemPraiNovoAcionamento',
    'var_visibleFluxogramaAcionamentosReal': 'ScreenPlemPraiMonitoramento',
    'var_visibleAcionar': 'ScreenPlemPraiMonitoramento',
    'var_visibleLancarAtividade': 'ScreenPlemPraiMonitoramento',
    'var_visibleLancarVitimas': 'ScreenPlemPraiMonitoramento',
    'var_visibleListarEquipamentos': 'ScreenPlemPraiMonitoramento',
    'var_visiblePrai': 'ScreenPlemPraiMonitoramento',
    'var_visibleEscolhaFluxograma': 'ScreenPlemPraiFluxogramas',
    'var_visibleFluxogramaPLEM': 'ScreenPlemPraiFluxogramas',
    'var_visibleFluxogramaPRAI': 'ScreenPlemPraiFluxogramas',
    'var_visibleFormFluxograma': 'ScreenPlemPraiFormFluxograma',
    'var_visibleFluxogramaContatos': 'ScreenPlemPraiFormFluxograma',
    'var_visibleEscolhaEqp': 'ScreenPlemPraiEquipamentos',
    'var_visibleGenciarEquipamento': 'ScreenPlemPraiEquipamentos',
    'var_visibleFormEquipamento': 'ScreenPlemPraiEquipamentos',
    'var_visibleEscolhaContatos': 'ScreenPlemPraiContatos',
    'var_visibleFormContatosEntidade': 'ScreenPlemPraiContatos',
    'var_visibleFormAciona': 'ScreenPlemPraiHome',
    'var_visibleExcluirAcionamento': 'ScreenPlemPraiHome',
}

# tokens de tema (mesmos nomes do AppFormulas_PlemPrai.fx.md)
COLOR_TOKENS = {
    'RGBA(255, 255, 255, 1)': 'thmSurface',
    'RGBA(0, 0, 0, 1)': 'thmText',
    'RGBA(0, 0, 0, 0.7)': 'thmTextSoft',
    'RGBA(0, 0, 0, 0.5)': 'thmTextMuted',
    'RGBA(0, 0, 0, 0.3)': 'thmTextFaint',
    'RGBA(0, 0, 0, 0.1)': 'thmShade10',
    'RGBA(61, 61, 61, 1)': 'thmTextStrong',
    'RGBA(242, 242, 242, 1)': 'thmBackground',
    'RGBA(240, 240, 240, 1)': 'thmBackgroundAlt',
    'RGBA(249, 249, 249, 1)': 'thmSurfaceAlt',
    'RGBA(247, 247, 247, 1)': 'thmSurfaceSoft',
    'RGBA(237, 237, 237, 1)': 'thmBorderSoft',
    'RGBA(167, 182, 203, 1)': 'thmBorder',
    'RGBA(15, 108, 189, 1)': 'thmPrimary',
    'RGBA(5, 102, 178, 1)': 'thmPrimary',
    'RGBA(39, 113, 194, 1)': 'thmPrimary',
    'RGBA(40, 134, 222, 1)': 'thmPrimaryLight',
    'RGBA(180, 214, 250, 1)': 'thmPrimarySoft',
    'RGBA(9, 33, 98, 1)': 'thmPrimaryDark',
    'RGBA(0, 18, 107, 1)': 'thmPrimaryDark',
    'RGBA(39, 67, 125, 1)': 'thmPrimaryDark',
    'RGBA(30, 30, 100, 1)': 'thmPrimaryDark',
    'RGBA(9, 33, 98, 0.05)': 'thmPrimaryFade05',
    'RGBA(0, 18, 107, 0.05)': 'thmPrimaryFade05',
    'RGBA(0, 18, 107, 0.1)': 'thmPrimaryFade10',
    'RGBA(0, 18, 107, 0.2)': 'thmPrimaryFade20',
    'RGBA(255, 0, 0, 1)': 'thmDanger',
    'RGBA(255, 191, 0, 1)': 'thmWarning',
    'RGBA(255, 255, 0, 1)': 'thmStatusYellow',
    'RGBA(52, 152, 47, 1)': 'thmSuccess',
    'RGBA(247, 116, 38, 1)': 'thmStatusOrange',
    'RGBA(249, 83, 109, 1)': 'thmStatusRed',
    'RGBA(56, 96, 178, 1)': 'thmStatusBlue',
    'RGBA(0, 0, 0, 0)': 'thmTransparent',
}
VAR_COLOR_READS = {  # leituras das antigas vars de tema
    'var_colorPrimary': 'thmTextStrong',
    'var_colorSecond': 'thmPrimary',
    'var_colorTertiary': 'thmBackground',
}

NAV_TRANSITION = 'ScreenTransition.Fade'

# OnVisible da Home (única tela com conteúdo fixo): liga o container principal,
# publica o aeroporto selecionado como variável global e mantém a coleção de
# contatos usada por outras telas do app (comportamento preservado do original)
HOME_ONVISIBLE = [
    '      OnVisible: |-',
    '        =Set(',
    '            var_visiblePrincipal,',
    '            true',
    '        );',
    '        Set(',
    '            var_aeroSelectMain,',
    '            Coalesce(',
    '                ComboboxCanvasAeroSelectMain.Selected.Value,',
    '                varAeroUser',
    '            )',
    '        );',
    '        Switch(',
    '            varPerfilUser,',
    '            "Base",',
    '            ClearCollect(',
    '                col_contatos_acionamentos,',
    '                Sort(',
    '                    Filter(',
    '                        tbl_contatos_entidades,',
    '                        Aeroporto = varAeroUser',
    '                    ),',
    '                    ID,',
    '                    SortOrder.Descending',
    '                )',
    '            ),',
    '            "Bloco",',
    '            ClearCollect(',
    '                col_contatos_acionamentos,',
    '                Sort(',
    '                    Filter(',
    '                        tbl_contatos_entidades,',
    '                        Bloco = varBlocoUser',
    '                    ),',
    '                    ID,',
    '                    SortOrder.Descending',
    '                )',
    '            ),',
    '            ClearCollect(',
    '                col_contatos_acionamentos,',
    '                Sort(',
    '                    tbl_contatos_entidades,',
    '                    ID,',
    '                    SortOrder.Descending',
    '                )',
    '            )',
    '        )',
]

# ------------------------------------------------------- patches semânticos
# aplicados APÓS as transformações mecânicas; cada patch deve casar exatamente
# uma vez (o gerador falha se não casar — proteção contra regressão silenciosa)
PATCHES = {
    'ScreenPlemPraiHome': [
        # combo de aeroporto publica a seleção como global (lida pelas demais telas)
        ("DefaultSelectedItems: '=[varAeroUser]  '",
         "DefaultSelectedItems: '=[varAeroUser]  '\n"
         "                              OnChange: =Set(var_aeroSelectMain, Self.Selected.Value)"),
        # Reset cross-screen movido para o OnVisible de ScreenPlemPraiFluxogramas
        (";Reset(ComboboxCanvasAeroSelectCadFluxo)", ""),
    ],
    'ScreenPlemPraiMonitoramento': [
        # P1: timer 5s com CountRows não-delegável -> 30s comparando o maior ID (delegável)
        ("""                              AutoPause: =false
                              AutoStart: =true
                              Duration: =5000
                              LayoutMaxHeight: =
                              LayoutMaxWidth: =
                              OnTimerEnd: |-
                                =If(
                                    Value(
                                        CountRows (
                                            Filter(
                                                Sort(
                                                    tbl_atividadesPlemPrai,
                                                    ID,
                                                    SortOrder.Descending
                                                ),
                                                ID_acionamento = Value(var_dadosAcionamento.ID)
                                            )
                                        )
                                    ) > Value(GalleryAtividadesLancadas.AllItemsCount),
                                    Select(Function_consultarAtividades)
                                )""",
         """                              AutoPause: =false
                              AutoStart: =true
                              Duration: =30000
                              LayoutMaxHeight: =
                              LayoutMaxWidth: =
                              OnTimerEnd: |-
                                =With(
                                    {
                                        _maxId: Coalesce(
                                            First(
                                                Sort(
                                                    Filter(
                                                        tbl_atividadesPlemPrai,
                                                        ID_acionamento = Value(var_dadosAcionamento.ID)
                                                    ),
                                                    ID,
                                                    SortOrder.Descending
                                                )
                                            ).ID,
                                            0
                                        )
                                    },
                                    If(
                                        _maxId > Coalesce(var_maxIdAtividadePlemPrai, -1),
                                        Set(
                                            var_maxIdAtividadePlemPrai,
                                            _maxId
                                        );
                                        Select(Function_consultarAtividades)
                                    )
                                )"""),
        # fechar/finalizar o monitoramento volta para a Home (antes revelava o Principal)
        ("=Set(var_visibleFormOcorrenciaAcionamento, false); Set(var_visibleFluxogramaAcionamentosReal, false); Set(var_miliSegundos, Blank());",
         "=Set(var_visibleFormOcorrenciaAcionamento, false); Set(var_visibleFluxogramaAcionamentosReal, false); Set(var_miliSegundos, Blank()); Navigate(ScreenPlemPraiHome, ScreenTransition.Fade);"),
    ],
    'ScreenPlemPraiNovoAcionamento': [
        # fluxo 1.0.0.5 pode devolver chat vazio (Try/Catch) -> avisa o operador
        ("""                                            Set(
                                                varChatID,
                                                ID_chat.chat
                                            );
                                            //-----------------------------------------------------
                                            // SALVA ID CHAT
                                            //-----------------------------------------------------
                                            Patch(
                                                tbl_ocorrenciaAcionamento,
                                                _registro,
                                                {ID_chat: varChatID}
                                            );""",
         """                                            Set(
                                                varChatID,
                                                ID_chat.chat
                                            );
                                            If(
                                                IsBlank(varChatID),
                                                Notify(
                                                    "Não foi possível criar o chat do acionamento no Teams. O acionamento segue sem chat vinculado.",
                                                    NotificationType.Warning
                                                )
                                            );
                                            //-----------------------------------------------------
                                            // SALVA ID CHAT
                                            //-----------------------------------------------------
                                            IfError(
                                                Patch(
                                                    tbl_ocorrenciaAcionamento,
                                                    _registro,
                                                    {ID_chat: varChatID}
                                                ),
                                                Notify(
                                                    "Erro ao salvar o ID do chat: " & FirstError.Message,
                                                    NotificationType.Error
                                                )
                                            );"""),
        # cancelar a escolha do tipo volta para a tela de origem
        ("=Set(var_visibleEscolhaAcionamento, false)\n",
         "=Set(var_visibleEscolhaAcionamento, false); Back()\n"),
        # finalização do acionamento PLEM volta para a Home
        ("Set(var_visibleFormOcorrenciaAcionamento, false); Set(var_visibleFluxogramaAcionamentosReal, false);\n                                        Notify(",
         "Set(var_visibleFormOcorrenciaAcionamento, false); Set(var_visibleFluxogramaAcionamentosReal, false); Navigate(ScreenPlemPraiHome, ScreenTransition.Fade);\n                                        Notify("),
    ],
    'ScreenPlemPraiFluxogramas': [
        # Reset cross-screen movido para o OnVisible de ScreenPlemPraiContatos
        ("Reset(TextInput1)", "false", 3),
        ("=Set(var_visibleEscolhaFluxograma, false)\n",
         "=Set(var_visibleEscolhaFluxograma, false); Back()\n"),
        ("=Set(var_visibleFluxogramaPRAI, false)\n",
         "=Set(var_visibleFluxogramaPRAI, false); Navigate(ScreenPlemPraiHome, ScreenTransition.Fade)\n"),
        ("=Set(var_visibleFluxogramaPLEM, false)\n",
         "=Set(var_visibleFluxogramaPLEM, false); Navigate(ScreenPlemPraiHome, ScreenTransition.Fade)\n"),
    ],
    'ScreenPlemPraiFormFluxograma': [
        ("=Set(var_visibleFormFluxograma, false)\n",
         "=Set(var_visibleFormFluxograma, false); Back()\n"),
        ("=Set(var_visibleFormFluxograma, false);\n                          Notify(",
         "=Set(var_visibleFormFluxograma, false); Back();\n                          Notify("),
        ("=Set(var_visibleEmergenciaFluxoExcluir, false); Set(var_visibleFormFluxograma, false);\n                                RemoveIf(",
         "=Set(var_visibleEmergenciaFluxoExcluir, false); Set(var_visibleFormFluxograma, false); Back();\n                                RemoveIf("),
    ],
    'ScreenPlemPraiEquipamentos': [
        # P3: Search() não-delegável -> StartsWith delegável no SharePoint
        ("""                              Items: |-
                                =Sort(
                                    Search(
                                        Filter(
                                            tbl_equipamentosAcionamentos,
                                            Aeroporto = ComboboxCanvasAeroSelectCadEqp.Selected.Value
                                        ),
                                        TextInputCanvas3.Value,
                                        Item
                                    ),
                                    Item,
                                    SortOrder.Ascending
                                )""",
         """                              Items: |-
                                =Sort(
                                    Filter(
                                        tbl_equipamentosAcionamentos,
                                        Aeroporto = ComboboxCanvasAeroSelectCadEqp.Selected.Value && StartsWith(
                                            Item,
                                            TextInputCanvas3.Value
                                        )
                                    ),
                                    Item,
                                    SortOrder.Ascending
                                )"""),
        ("=Set(var_visibleGenciarEquipamento, false)\n",
         "=Set(var_visibleGenciarEquipamento, false); Navigate(ScreenPlemPraiHome, ScreenTransition.Fade)\n"),
        ("=Set(var_visibleEscolhaEqp, false)\n",
         "=Set(var_visibleEscolhaEqp, false); Back()\n"),
    ],
    'ScreenPlemPraiContatos': [
        # P3: Search() em duas colunas -> StartsWith com Or (delegável)
        ("""                              Items: |-
                                =Search(
                                    Filter(
                                        tbl_contatos_entidades,
                                        Aeroporto = var_AeroSelectCadFluxo
                                    ),
                                    TextInput1.Text,
                                    nome,
                                    nome_orgao
                                )""",
         """                              Items: |-
                                =Filter(
                                    tbl_contatos_entidades,
                                    Aeroporto = var_AeroSelectCadFluxo && (StartsWith(
                                        nome,
                                        TextInput1.Text
                                    ) || StartsWith(
                                        nome_orgao,
                                        TextInput1.Text
                                    ))
                                )"""),
        ("=Set(var_visibleFormContatosEntidade, false)\n",
         "=Set(var_visibleFormContatosEntidade, false); Back()\n"),
        ("=Set(var_visibleEscolhaContatos, false)\n",
         "=Set(var_visibleEscolhaContatos, false); Back()\n"),
    ],
}


def load_lines():
    with open(SRC, encoding='utf-8') as f:
        return f.read().splitlines()


def find_blocks(lines):
    """nome -> (inicio, fim, indent) de todo item '- Nome:' do arquivo (1-based)."""
    starts = []
    for i, ln in enumerate(lines, 1):
        m = re.match(r'^( +)- ([A-Za-z0-9_]+):\s*$', ln)
        if m:
            starts.append((i, len(m.group(1)), m.group(2)))
    blocks = {}
    for idx, (i, ind, name) in enumerate(starts):
        end = len(lines)
        for (i2, ind2, _n2) in starts[idx + 1:]:
            if ind2 <= ind:
                end = i2 - 1
                break
        else:
            # até o fim, mas recua linhas com indent <= ind (fecham o pai)
            pass
        # ajusta fim: linha não vazia com indent <= ind encerra o bloco
        j = i
        for k in range(i + 1, end + 1):
            ln = lines[k - 1]
            if ln.strip() == '':
                continue
            cur = len(ln) - len(ln.lstrip(' '))
            if cur <= ind:
                break
            j = k
        blocks.setdefault(name, []).append((i, j, ind))
    return blocks


def slice_block(lines, blocks, name):
    occ = blocks.get(name)
    if not occ:
        sys.exit(f'container não encontrado: {name}')
    if len(occ) > 1:
        sys.exit(f'nome ambíguo: {name} -> {occ}')
    s, e, ind = occ[0]
    return lines[s - 1:e], ind


def reindent(block, from_indent, to_indent):
    delta = to_indent - from_indent
    out = []
    for ln in block:
        if ln.strip() == '':
            out.append('')
        elif delta >= 0:
            out.append(' ' * delta + ln)
        else:
            out.append(ln[-delta:] if ln[:len(ln) - len(ln.lstrip(' '))].startswith(' ' * -delta) else ln.lstrip(' '))
    return out


# ------------------------------------------------------- T1: UpdateContext -> Set
def split_top_level(s):
    """divide pares 'chave: valor' de um record Power Fx por vírgulas de nível 0."""
    parts, depth, cur, instr = [], 0, [], False
    i = 0
    while i < len(s):
        c = s[i]
        if instr:
            cur.append(c)
            if c == '"':
                if i + 1 < len(s) and s[i + 1] == '"':
                    cur.append(s[i + 1]); i += 1
                else:
                    instr = False
        else:
            if c == '"':
                instr = True; cur.append(c)
            elif c in '([{':
                depth += 1; cur.append(c)
            elif c in ')]}':
                depth -= 1; cur.append(c)
            elif c == ',' and depth == 0:
                parts.append(''.join(cur)); cur = []
            else:
                cur.append(c)
        i += 1
    if ''.join(cur).strip():
        parts.append(''.join(cur))
    return parts


def strip_line_comments(s):
    """remove comentários //-até-fim-de-linha fora de strings (mantém /* */)."""
    out, instr, i = [], False, 0
    while i < len(s):
        c = s[i]
        if instr:
            out.append(c)
            if c == '"':
                if i + 1 < len(s) and s[i + 1] == '"':
                    out.append(s[i + 1]); i += 1
                else:
                    instr = False
        else:
            if c == '"':
                instr = True; out.append(c)
            elif c == '/' and i + 1 < len(s) and s[i + 1] == '/':
                nl = s.find('\n', i)
                if nl < 0:
                    break
                i = nl  # mantém a quebra de linha
                out.append('\n')
            else:
                out.append(c)
        i += 1
    return ''.join(out)


def compact(expr):
    """colapsa uma expressão multiline em linha única (sem // comments)."""
    expr = strip_line_comments(expr)
    return re.sub(r'\s+', ' ', expr).strip()


def convert_updatecontext(text):
    """substitui UpdateContext({...}) por cadeia Set(...) em LINHA ÚNICA
    (preserva a validade dos block scalars YAML)."""
    out = []
    i = 0
    while True:
        j = text.find('UpdateContext', i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        k = text.find('(', j)
        depth, instr = 0, False
        m = k
        while m < len(text):
            c = text[m]
            if instr:
                if c == '"':
                    if m + 1 < len(text) and text[m + 1] == '"':
                        m += 1
                    else:
                        instr = False
            else:
                if c == '"':
                    instr = True
                elif c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        break
            m += 1
        inner = text[k + 1:m].strip()
        if not (inner.startswith('{') and inner.endswith('}')):
            out.append(text[j:m + 1])
            i = m + 1
            continue
        record = strip_line_comments(inner[1:-1])
        pairs = split_top_level(record)
        sets = []
        for p in pairs:
            if ':' not in p or not p.strip():
                continue
            key, val = p.split(':', 1)
            sets.append(f'Set({key.strip()}, {compact(val)})')
        out.append('; '.join(sets) if sets else 'false')
        i = m + 1
    return ''.join(out)


def convert_updatecontext_yaml(block_text):
    return convert_updatecontext(block_text)


# ------------------------------------------------------- T2: Navigate nos cruzamentos
def add_navigations(text, screen_name):
    for flag, target in FLAG_SCREEN.items():
        if target == screen_name:
            continue
        pat = re.compile(r'Set\(\s*' + flag + r'\s*,\s*true\s*\)', re.S)
        text = pat.sub(f'Set({flag}, true); Navigate({target}, {NAV_TRANSITION})', text)
    return text


# ------------------------------------------------------- T3: cores
RGBA_ML = re.compile(r'RGBA\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)', re.S)


def tokenize_colors(text):
    # normaliza RGBA multilinha para forma canônica em linha única
    text = RGBA_ML.sub(lambda m: f'RGBA({m.group(1)}, {m.group(2)}, {m.group(3)}, {m.group(4)})', text)
    for rgba, token in COLOR_TOKENS.items():
        text = text.replace(rgba, token)
    for var, token in VAR_COLOR_READS.items():
        text = re.sub(r'\b' + var + r'\b', token, text)
    return text


# ------------------------------------------------------- T4/T5: galerias e buscas
def enhance_galleries(lines):
    out = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        out.append(ln)
        m = re.match(r'^( +)Control: Gallery@', ln)
        if m:
            ind = m.group(1)
            # bloco de Properties começa depois de Variant/Properties
            j = i + 1
            props_idx = None
            while j < len(lines):
                if re.match(r'^' + ind + r'Properties:\s*$', lines[j]):
                    props_idx = j
                    break
                if re.match(r'^' + ind + r'\S', lines[j]) and 'Variant' not in lines[j] and 'IsLocked' not in lines[j]:
                    break
                j += 1
            if props_idx is not None:
                # já tem?
                end = props_idx + 1
                have_delay = have_spin = False
                while end < len(lines):
                    cur = lines[end]
                    if cur.strip() == '' or len(cur) - len(cur.lstrip(' ')) > len(ind):
                        if 'DelayItemLoading' in cur:
                            have_delay = True
                        if 'LoadingSpinner' in cur:
                            have_spin = True
                        end += 1
                    else:
                        break
                inject = []
                if not have_delay:
                    inject.append(ind + '  DelayItemLoading: =true')
                if not have_spin:
                    inject.append(ind + '  LoadingSpinner: =LoadingSpinner.Data')
                # injeta logo após Properties:
                for k in range(i + 1, props_idx + 1):
                    out.append(lines[k])
                out.extend(inject)
                i = props_idx + 1
                continue
        i += 1
    return out


def add_delayoutput(lines):
    out = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        out.append(ln)
        m = re.match(r'^( +)- (txt[A-Za-z0-9_]*[Bb]usc[A-Za-z0-9_]*):\s*$', ln)
        if m:
            ind = m.group(1)
            # localizar Properties: e injetar DelayOutput se ausente no bloco
            j = i + 1
            while j < n and (len(lines[j]) - len(lines[j].lstrip(' '))) > len(ind):
                out.append(lines[j])
                if re.match(r'^ +Properties:\s*$', lines[j]):
                    # verifica se o bloco já tem DelayOutput
                    blk = []
                    k = j + 1
                    while k < n and (len(lines[k]) - len(lines[k].lstrip(' '))) > len(ind):
                        blk.append(lines[k]); k += 1
                    if not any('DelayOutput' in b for b in blk):
                        pind = len(lines[j]) - len(lines[j].lstrip(' '))
                        out.append(' ' * (pind + 2) + 'DelayOutput: =true')
                j += 1
            i = j
            continue
        i += 1
    return out


# ------------------------------------------------------- montagem da tela
def build_screen(name, cfg, lines, blocks):
    parts = []
    parts.append('Screens:')
    parts.append(f'  {name}:')
    parts.append('    Properties:')
    parts.append('      Fill: =thmBackground')
    if name == 'ScreenPlemPraiHome':
        parts.extend(HOME_ONVISIBLE)
    if cfg['entry_flags']:
        conds = ' && '.join(f'!{f}' for f in cfg['entry_flags'])
        first = cfg['entry_flags'][0]
        parts.append('      OnVisible: |-')
        prefix = cfg.get('onvisible_prefix', [])
        for n_, stmt in enumerate(prefix):
            lead = '=' if n_ == 0 else ''
            parts.append(f'        {lead}{stmt};')
        parts.append('        ' + ('If(' if prefix else '=If('))
        parts.append(f'            {conds},')
        parts.append('            Set(')
        parts.append(f'                {first},')
        parts.append('                true')
        parts.append('            )')
        parts.append('        )')
    parts.append('    Children:')
    root = 'ContainerRaiz' + name.replace('ScreenPlemPrai', '')
    parts.append(f'      - {root}:')
    parts.append('          Control: GroupContainer@1.5.0')
    parts.append('          Variant: ManualLayout')
    parts.append('          Properties:')
    parts.append('            DropShadow: =DropShadow.None')
    parts.append('            Fill: =thmSurface')
    parts.append('            Height: =Parent.Height')
    parts.append('            RadiusBottomLeft: =0')
    parts.append('            RadiusBottomRight: =0')
    parts.append('            RadiusTopLeft: =0')
    parts.append('            RadiusTopRight: =0')
    parts.append('            Width: =Parent.Width')
    parts.append('          Children:')
    child_indent = 12
    for cname in cfg['containers']:
        block, ind = slice_block(lines, blocks, cname)
        block = reindent(block, ind, child_indent)
        parts.extend(block)
    text = '\n'.join(parts) + '\n'
    # transformações
    text = convert_updatecontext_yaml(text)
    text = add_navigations(text, name)
    text = tokenize_colors(text)
    tl = text.splitlines()
    tl = enhance_galleries(tl)
    tl = add_delayoutput(tl)
    text = '\n'.join(tl) + '\n'
    # T6: combo de aeroporto da Home vira variável global nas demais telas
    # (var_aeroSelectMain: nome novo — var_aeroSelect já existia no app com outro papel)
    if name != 'ScreenPlemPraiHome':
        text = text.replace('ComboboxCanvasAeroSelectMain.Selected.Value', 'var_aeroSelectMain')
    # T7: combo de aeroporto da escolha de fluxograma -> var já existente no app
    if name != 'ScreenPlemPraiFluxogramas':
        text = text.replace('ComboboxCanvasAeroSelectCadFluxo.Selected.Value', 'var_AeroSelectCadFluxo')
    # patches semânticos (cada um deve casar o número esperado de vezes)
    for patch in PATCHES.get(name, []):
        old, new = patch[0], patch[1]
        expected = patch[2] if len(patch) > 2 else 1
        n = text.count(old)
        if n != expected:
            sys.exit(f'PATCH {name}: esperado {expected} match(es), encontrado {n}:\n{old[:120]}...')
        text = text.replace(old, new)
    return text


def main():
    lines = load_lines()
    blocks = find_blocks(lines)
    report = []
    for name, cfg in SCREENS.items():
        text = build_screen(name, cfg, lines, blocks)
        path = os.path.join(OUT_DIR, f'{name}.pa.yaml')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        h = hashlib.sha256(text.encode()).hexdigest()[:12]
        report.append(f'{name}: {len(text.splitlines())} linhas  sha256:{h}')
    print('\n'.join(report))


if __name__ == '__main__':
    main()
