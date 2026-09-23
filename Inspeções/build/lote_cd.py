# -*- coding: utf-8 -*-
"""Funções dos Lotes C (App.Formulas, OnStart, relatórios) e D (bugs de cópia,
navegação sem referência a outra tela). Cada função recebe (tela, texto, contar,
ctx) e devolve (texto, n). ctx é um dicionário compartilhado entre cirurgias
(guarda as tabelas extraídas do export para o App.Formulas)."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fx import find_call, split_args
from pautil import find_ctrl, prop_block, block_end, ind


class Abortar(SystemExit):
    pass


# ─────────────────────────────────────────────────────────────────────────────
# utilitários locais
# ─────────────────────────────────────────────────────────────────────────────
def _prop_span(linhas, controle, prop):
    """(k, ke) da propriedade prop do controle; ke exclusivo"""
    i = find_ctrl(linhas, controle)
    if i < 0:
        raise Abortar(f"controle {controle} não encontrado")
    pi, pe = prop_block(linhas, i)
    if pi < 0:
        raise Abortar(f"{controle} sem Properties")
    pind = ind(linhas[pi]) + 2
    for k in range(pi + 1, pe):
        if ind(linhas[k]) == pind and re.match(r'^\s*' + re.escape(prop) + r':', linhas[k]):
            return k, block_end(linhas, k)
    raise Abortar(f"{controle}.{prop} não encontrada")


def ler_prop(texto, controle, prop):
    """corpo dedentado da propriedade (sem o '=' inicial)"""
    linhas = texto.split('\n')
    k, ke = _prop_span(linhas, controle, prop)
    if ke == k + 1:
        val = re.match(r'^\s*' + re.escape(prop) + r': (.*)$', linhas[k]).group(1).strip()
        if val.startswith(('"', "'")):
            # escalar YAML entre aspas que a normalização não converteu: decodifica
            # (sem isso a cirurgia recebia o texto com escapes \n e \" — bug de 2026-09-17)
            import yaml
            val = yaml.safe_load(val)
            if not isinstance(val, str):
                raise Abortar(f"ler_prop: {controle}.{prop} entre aspas não é texto")
            val = val.strip('\n')
        return val[1:] if val.startswith('=') else val
    corpo = linhas[k + 1:ke]
    reais = [l for l in corpo if l.strip()]
    base = min(ind(l) for l in reais)
    txt = '\n'.join(l[base:] for l in corpo).strip('\n')
    return txt[1:] if txt.startswith('=') else txt


def gravar_prop(texto, controle, prop, corpo):
    """substitui o valor da propriedade por um bloco |- com o corpo (que já começa com '=')"""
    linhas = texto.split('\n')
    k, ke = _prop_span(linhas, controle, prop)
    pind = ind(linhas[k])
    novo = [f"{' ' * pind}{prop}: |-"] + [(' ' * (pind + 2) + t) if t else '' for t in corpo.strip('\n').split('\n')]
    linhas[k:ke] = novo
    return '\n'.join(linhas)


def indentar(txt, n):
    return '\n'.join((' ' * n + l) if l else '' for l in txt.split('\n'))


def registros_de_clearcollect(fx, colecao):
    """argumentos (registros) do ClearCollect(colecao, {...}, {...}) dentro de fx"""
    pos = 0
    while True:
        r = find_call(fx, 'ClearCollect', pos)
        if not r:
            raise Abortar(f"ClearCollect({colecao}, ...) não encontrado")
        a, b, c = r
        args = split_args(fx[b:c - 1])
        if args and args[0].strip() == colecao:
            return [x.strip() for x in args[1:]], (a, c)
        pos = c


# ─────────────────────────────────────────────────────────────────────────────
# Lote C
# ─────────────────────────────────────────────────────────────────────────────
ONSTART_NOVO = '''=// 🔄 Inicializa carregamentos
Set(var_load, true);
Set(varControleIndex, true);
// ✈️ Aeroportos fixos: a tabela mora em App.Formulas (nfAeros); a coleção mantém o
// nome porque 30+ fórmulas das telas a leem.
ClearCollect(colAeros, nfAeros);
// 👤 Usuário: parâmetro do hub, senão o nome completo (como antes)
Set(
    varIdUser,
    Coalesce(
        Value(Param("USUARIO")),
        LookUp(User, usrNome = User().FullName).ID
    )
);
// Um único LookUp em User alimenta todas as variáveis de perfil
With(
    {usuario: LookUp(User, ID = varIdUser)},
    Set(varNomeUser, usuario.usrNome);
    Set(varBlocoUser, usuario.Bloco);
    Set(varAeroUser, usuario.Aeroporto);
    Set(varPerfilUser, usuario.Perfil);
    Set(varAutUser, usuario.Autorizacao);
    Set(varIATAUser, LookUp(nfAeros, Aeroporto = usuario.Aeroporto).IATA)
);
// Derivados do perfil, calculados uma vez (antes: a mesma fórmula em 42 controles)
Set(varModoFiltroAero, If(varPerfilUser = "Base", DisplayMode.Disabled, DisplayMode.Edit));
Set(varModoFiltroBloco, If(varPerfilUser = "Base" Or varPerfilUser = "Bloco", DisplayMode.Disabled, DisplayMode.Edit));
Set(varBlocoPadrao, If(varPerfilUser = "Base", varBlocoUser, varPerfilUser = "Bloco", varBlocoUser, Blank()));
// ── GANCHO OFFLINE: o motor de sincronização insere aqui (LoadData / fila / flags). Não mover a linha abaixo.
// ✅ Finaliza carregamento
Set(var_load, false)'''

FORMULAS_CAB = '''// ══════════════════════════════════════════════════════════════════════════════
// App.Formulas — Inspeções. Named formulas são avaliadas sob demanda e memoizadas:
// tiram carga do OnStart e do OnVisible. Tabelas copiadas byte a byte do export.
// ══════════════════════════════════════════════════════════════════════════════
'''


def c1_tabelas(tela, txt, contar, ctx):
    """extrai colAeros (App.OnStart) para nfAeros — guarda em ctx; não altera a tela"""
    onstart = ler_prop(txt, 'App', 'OnStart')
    recs, _ = registros_de_clearcollect(onstart, 'colAeros')
    if len(recs) < 10:
        raise Abortar(f"colAeros: só {len(recs)} registros encontrados")
    ctx['nfAeros'] = 'nfAeros = Table(\n' + ',\n'.join(indentar(r, 4) for r in recs) + '\n);'
    ctx['n_aeros'] = len(recs)
    return txt, 1


def c2_onstart(tela, txt, contar, ctx):
    if contar:
        return txt, 1
    return gravar_prop(txt, 'App', 'OnStart', ONSTART_NOVO), 1


def c4_parametros_animais(tela, txt, contar, ctx):
    """frmHomePista.OnVisible: tabela literal de espécies -> nfParametrosAnimais"""
    onvis = ler_prop(txt, 'frmHomePista', 'OnVisible')
    recs, (a, c) = registros_de_clearcollect(onvis, 'col_parametrosAnimais')
    if len(recs) < 50:
        raise Abortar(f"col_parametrosAnimais: só {len(recs)} registros")
    ctx['nfParametrosAnimais'] = 'nfParametrosAnimais = Table(\n' + ',\n'.join(indentar(r, 4) for r in recs) + '\n);'
    ctx['n_animais'] = len(recs)
    if contar:
        return txt, 1
    # remove a instrução If(CountRows(col_parametrosAnimais) = 0, ClearCollect(...)) inteira
    pos = 0
    while True:
        r = find_call(onvis, 'If', pos)
        if not r:
            raise Abortar("If(CountRows(col_parametrosAnimais) = 0, ...) não encontrado")
        ia, ib, ic = r
        if 'CountRows(col_parametrosAnimais)' in onvis[ib:ic]:
            break
        pos = ic
    # consome o ';' anterior (a instrução é a última do OnVisible) ou o seguinte
    antes = onvis[:ia].rstrip()
    depois = onvis[ic:].lstrip()
    if depois.startswith(';'):
        novo = onvis[:ia] + depois[1:].lstrip()
    elif antes.endswith(';'):
        novo = antes[:-1] + ('\n' + depois if depois else '')
    else:
        novo = antes + '\n' + depois
    txt = gravar_prop(txt, 'frmHomePista', 'OnVisible', '=' + novo.strip('\n'))
    return txt, 1


def c6_relatorio(tela, txt, contar, ctx, viewer, botao, var, template=None):
    """HtmlViewer oculto de relatório vira variável montada só no clique do botão
    de PDF; o retorno do fluxo ganha guarda antes do Launch (D9)."""
    if contar:
        return txt, 1
    corpo = ler_prop(txt, viewer, 'HtmlText')          # sem o '='
    ctx.setdefault('relatorios', {})[(tela, viewer)] = corpo
    txt = gravar_prop(txt, viewer, 'HtmlText', '=' + var)
    if template is not None:
        novo = template.replace('{HTML}', indentar(corpo, 4).lstrip())
        return gravar_prop(txt, botao, 'OnSelect', novo), 1
    onsel = ler_prop(txt, botao, 'OnSelect')
    # Set(varIDhtmlCriado, 'Criar-HTML'.Run(<viewer>.HtmlText, ...))
    r = find_call(onsel, 'Set', 0)
    if not r or split_args(onsel[r[1]:r[2] - 1])[0].strip() != 'varIDhtmlCriado':
        raise Abortar(f"{tela} {botao}: Set(varIDhtmlCriado, ...) não é a 1ª chamada")
    a, b, c = r
    trecho = onsel[a:c]
    if trecho.count(f'{viewer}.HtmlText') != 1:
        raise Abortar(f"{tela} {botao}: {viewer}.HtmlText não aparece 1x no Set")
    trecho = trecho.replace(f'{viewer}.HtmlText', var)
    montagem = ('// Monta o HTML só agora: o visor não recalcula mais a cada mudança de filtro\n'
                f'UpdateContext({{{var}: ' + indentar(corpo, 4).lstrip() + '});\n')
    onsel = onsel[:a] + montagem + trecho + onsel[c:]
    # guarda do Launch (D9)
    r = find_call(onsel, 'Launch', 0)
    if not r:
        raise Abortar(f"{tela} {botao}: Launch(...) não encontrado")
    a, b, c = r
    launch = onsel[a:c]
    guarda = ('If(\n    IsBlank(varIDhtmlCriado),\n'
              '    Notify("Não foi possível gerar o PDF. Tente novamente.", NotificationType.Error, 4000),\n'
              '    ' + indentar(launch, 4).lstrip() + '\n)')
    onsel = onsel[:a] + guarda + onsel[c:]
    return gravar_prop(txt, botao, 'OnSelect', '=' + onsel.strip('\n')), 1


ONSELECT_RELATORIO_PISTA = '''=// 1. Define o item selecionado
UpdateContext({Var_InspPistaRelatorios: GalleryInspPistaListagem.Selected});
// 2. Itens reais da inspeção (uma consulta delegável)
ClearCollect(
    col_relatorioPistaNaoConforme,
    Filter(
        '7.4.1-tbl_InspPistaItens' As itemInsp,
        itemInsp.IdInsp = Var_InspPistaRelatorios.ID
    )
);
// 3. Itens do menu sem apontamento = conformes (um passe; antes: ForAll + Remove + LookUp por linha)
ClearCollect(
    col_relatorioPistaConforme,
    Filter(
        col_inspPistaMenu As conf,
        !IsBlank(conf.item) &&
        IsBlank(
            LookUp(
                col_relatorioPistaNaoConforme As nc,
                nc.Local = conf.local && nc.Item = conf.categoria && nc.sIten = conf.item
            )
        )
    )
);
// 4. Monta o HTML só agora (o visor não recalcula mais a cada mudança de filtro)
UpdateContext({var_htmlRelPista: {HTML}});
// 5. Gera o HTML e salva no SharePoint
Set(
    varIDhtmlCriado,
    'Criar-HTML'.Run(
        var_htmlRelPista,
        "INSP-PISTA-" & varIATAUser & "-" & Text(Now(), "yyyymmddhhmmss")
    ).idhtml
);
// 6. Abre o PDF gerado (só se o fluxo devolveu o ID)
If(
    IsBlank(varIDhtmlCriado),
    Notify("Não foi possível gerar o PDF. Tente novamente.", NotificationType.Error, 4000),
    Launch(
        Substitute(
            LookUp(Documentos, ID = varIDhtmlCriado, Miniatura.Large),
            "thumbnail",
            "pdf"
        )
    )
)'''


def escrever_formulas(ctx, destino_invariante):
    """grava o App.Formulas em invariante (gerar_ptbr converte para pt-BR)"""
    partes = [FORMULAS_CAB, '// ── TABELAS FIXAS (saem do OnStart e do OnVisible de frmHomePista)',
              ctx['nfAeros'], '', ctx['nfParametrosAnimais'], '',
              '// ── GANCHO OFFLINE: named formulas do motor de sincronização entram abaixo desta linha', '']
    open(destino_invariante, 'w', encoding='utf-8', newline='\n').write('\n'.join(partes))


# ─────────────────────────────────────────────────────────────────────────────
# Lote D
# ─────────────────────────────────────────────────────────────────────────────
ONSELECT_NORMALIZAR_VE = '''=// antes: dois Patch idênticos na lista dentro de Concurrent (escrita dobrada)
Patch(
    tbl_Checklist_generico_objeto,
    LookUp(tbl_Checklist_generico_objeto, ID = ThisItem.ID),
    {Status: "Normalizado"}
);
Patch(
    col_detalhesVEitens,
    LookUp(col_detalhesVEitens, ID = ThisItem.ID),
    {Status: "Normalizado"}
)'''

ONSUCCESS_ZPA_EDITAR = '''=With(
    {_fotos: LookUp(tbl_inspZPAfotos, ID_FK = Self.LastSubmit.ID)},
    // atualiza o registro de fotos desta inspeção; cria só se ainda não existir
    // (antes: Defaults() sempre -> um registro novo a cada edição, com imagens lidas de outra tela)
    Patch(
        tbl_inspZPAfotos,
        If(IsBlank(_fotos), Defaults(tbl_inspZPAfotos), _fotos),
        {
            ID_FK: Self.LastSubmit.ID,
            zpa_fotoCabE1: Image3.Image,
            zpa_fotoCabE2: Image17.Image,
            zpa_fotoCabE3: Image18.Image,
            zpa_fotoCabD1: Image19.Image,
            zpa_fotoCabD2: Image20.Image,
            zpa_fotoCabD3: Image21.Image
        }
    )
);
Navigate(
    frmHomeZPA,
    ScreenTransition.Fade
);
Notify(
    "Inspeção finalizada com sucesso!",
    NotificationType.Success
)'''

ONVISIBLE_FORMZPA = '''=// preparação que antes era feita pela tela de origem (frmHomeZPA) antes do Navigate
If(
    var_zpa_modo = "novo",
    ResetForm(FormZpa);
    NewForm(FormZpa);
    Reset(AddMediaButtonD3);
    Reset(AddMediaButtonD2);
    Reset(AddMediaButtonD1);
    Reset(AddMediaButtonE3);
    Reset(AddMediaButtonE2);
    Reset(AddMediaButtonE1);
    UpdateContext({var_zpa_modo: ""})
)'''

ONVISIBLE_FORMZPA_EDITAR = '''=// preparação que antes era feita pela tela de origem (frmHomeZPA) antes do Navigate
EditForm(FormZpaEdit)'''

ONVISIBLE_INSPPISTACAD = '''=// preparação que antes era feita pela tela de origem (frmHomePista) antes do Navigate
Switch(
    var_acao,
    "Nova Inspeção",
    ResetForm(FormInspPistaCad1_2);
    NewForm(FormInspPistaCad1_2),
    "Finalizar",
    EditForm(FormInspPistaCad1_2)
)'''

ONFAILURE_PADRAO = '=Notify("Não foi possível gravar. Verifique a conexão e os campos obrigatórios.", NotificationType.Error, 6000)'
ONFAILURE_ZPA = ('=UpdateContext({var_loadSave: false});\n'
                 'Notify("Não foi possível gravar a inspeção. Verifique a conexão e os campos obrigatórios.", NotificationType.Error, 6000)')
