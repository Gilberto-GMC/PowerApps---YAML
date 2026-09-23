# -*- coding: utf-8 -*-
"""Tabela declarativa das cirurgias da frente "app leve".

Cada cirurgia: id, lote (A/B/C/D), tipo, descrição, telas, e quantas vezes tem
de casar por tela (esperado). Divergência aborta o gerador. Evidência de cada
número está em AUDITORIA.md e nos comentários abaixo (caminho:linha do export
de 2026-09-16).

Tipos:
  regex            localizar/substituir só em texto ativo (strings/comentários mascarados)
  set_prop         insere propriedade em ordem alfabética (só propriedade do propdict)
  remover_controle apaga bloco '- Nome:' se Visible for literal false e ninguém o referenciar
  remover_var      apaga toda escrita da variável (UpdateContext/Navigate/Set); exige 0 leituras
  prop             substituições dentro de UMA propriedade de UM controle (cada par casa 1x)
"""
import lote_cd as CD

APP_WIDTH = 'Max(App.Width, App.MinScreenWidth)'   # o que ScreenContainerMain/ContainerMain usam

# strings ficam mascaradas na busca: os literais são conferidos por 'verificar' no texto original
RE_MODO_BLOCO = r'If\(varPerfilUser = "[^"]*" Or varPerfilUser = "[^"]*" , DisplayMode\.Disabled,DisplayMode\.Edit\)'
RE_MODO_AERO = r'If\(varPerfilUser = "[^"]*" , DisplayMode\.Disabled,DisplayMode\.Edit\)'
RE_BLOCO_PADRAO = r'If\(\s*varPerfilUser = "[^"]*",\s*varBlocoUser,\s*varPerfilUser = "[^"]*",\s*varBlocoUser,\s*Blank\(\)\s*\)'
RESETS_ZPA = (r';\s*Reset\(AddMediaButtonD3\);\s*Reset\(AddMediaButtonD2\);\s*Reset\(AddMediaButtonD1\);'
              r'\s*Reset\(AddMediaButtonE3\);\s*Reset\(AddMediaButtonE2\);\s*Reset\(AddMediaButtonE1\)')
FORMS_SEM_ONFAILURE = {
    'frmCheckListGenericoEQP': ['FormCheckGenerico'],
    'frmFormZPAeditar': ['Form4', 'FormZpaEdit'],
    'frmHomeApont': ['FormApontEdit', 'FormInspPistaItensDetalhesColisao_1', 'FormInspPistaItensDetalhesPRESENCA_1',
                     'FormInspPistaItensDetalhesFOCO_1'],
    'frmHomePatio': ['FormInspPatio', 'FormInspPatioitens', 'FormGerInspPatioitem'],
    'frmHomePista': ['FormInspPistaDetalhes', 'FormInspPistaItensDetalhesColisao', 'FormInspPistaItensDetalhesPRESENCA',
                     'FormInspPistaItensDetalhesFOCO'],
    'frmHomeTPS': ['FormInspTPS', 'FormInspTPSitens', 'FormGerInspTPSitem'],
    'frmZPAapontamentos': ['FormGerInspZpaItens'],
}

# ── helpers do Lote B (delegação) ─────────────────────────────────────────────
# "IsBlank(x) || StartsWith(col, y)": StartsWith(col, "") é verdadeiro para toda
# linha (lição 2026-08-31), então o guarda IsBlank é redundante — e é ele que
# derruba a delegação. Fica StartsWith(col, Text(y)).
RE_GUARDA_STARTSWITH = (r'\(?IsBlank\(([^()]+)\)\s*\|\|\s*StartsWith\(\s*(\w+),\s*'
                        r'(Text\([^()]+\)|[^(),]+?)\s*\)\)?')


def _sem_guarda_startswith(mt):
    col, arg = mt.group(2), mt.group(3).strip()
    if not arg.startswith('Text('):
        arg = f'Text({arg})'
    return f'StartsWith({col}, {arg})'


# "IsBlank(dtp.SelectedDate) || col >= dtp.SelectedDate": piso/teto fixos
# tornam o intervalo obrigatório e delegável (mesmo resultado com data preenchida;
# com data vazia, deixa de incluir registros SEM data — coluna sempre preenchida).
RE_GUARDA_DATA = r'\(?IsBlank\((\w+)\.SelectedDate\)\s*\|\|\s*(\w+)\s*(>=|<=)\s*\1\.SelectedDate\)?'


def _sem_guarda_data(mt):
    dtp, col, op = mt.group(1), mt.group(2), mt.group(3)
    piso = 'Date(2000, 1, 1)' if op == '>=' else 'Date(2099, 12, 31)'
    return f'{col} {op} Coalesce({dtp}.SelectedDate, {piso})'


ITEMS_ZPA_HOME = '''=FirstN(
    Sort(
        Sort(
            // busca por ID em ramo próprio: "IsBlank(x) || ID = x" não delega (lição 2026-08-31)
            Switch(
                true,
                IsBlank(txtBuscarInspPatio_2.Text),
                Filter(
                    tbl_inspZpa,
                    StartsWith(Aeroporto, Text(cmbHomeAeroporto_8.Selected.Result)),
                    StartsWith(Bloco, Text(cmbHomeBloco_8.Selected.Value)),
                    StartsWith(Status, Text(cmbHomeStatus_6.Selected.Value)),
                    Periodo = Last(Split(var_tituloModulo, " ")).Value,
                    Inicio >= dtpHomeDtfInicio_8.SelectedDate && Termino <= dtpHomeDtfTermino_8.SelectedDate
                ),
                Filter(
                    tbl_inspZpa,
                    StartsWith(Aeroporto, Text(cmbHomeAeroporto_8.Selected.Result)),
                    StartsWith(Bloco, Text(cmbHomeBloco_8.Selected.Value)),
                    StartsWith(Status, Text(cmbHomeStatus_6.Selected.Value)),
                    Periodo = Last(Split(var_tituloModulo, " ")).Value,
                    Inicio >= dtpHomeDtfInicio_8.SelectedDate && Termino <= dtpHomeDtfTermino_8.SelectedDate,
                    ID = Value(txtBuscarInspPatio_2.Text)
                )
            ),
            Status,
            SortOrder.Ascending
        ),
        ID,
        SortOrder.Descending
    ),
    Value(txtLimit_3.Text)
)'''

ITEMS_GALLERY_CLG = '''=If(
    tgMostraApontamentos.Checked,
    // Exibe apenas os apontamentos com erro
    With(
        {
            blocoFiltro: Text(cmbCLGbloco.Selected.Value),
            aeroportoFiltro: Text(cmbCLGaeroporto.Selected.Result)
        },
        FirstN(
            Filter(
                Sort(tbl_Checklist_generico_base, ID, SortOrder.Descending) As Base,
                StartsWith(Base.Bloco, blocoFiltro) &&
                StartsWith(Base.Aeroporto, aeroportoFiltro) &&
                // col_clgNaoConf: itens "Não conforme" não normalizados, carregados 1x em ButtonRefreshCLG
                !IsBlank(LookUp(col_clgNaoConf, ID_checkList = Base.ID))
            ),
            Value(txtLimit_5.Text)
        )
    ),
    // Exibe todos com filtros opcional de empresa
    With(
        {
            blocoFiltro: Text(cmbCLGbloco.Selected.Value),
            aeroportoFiltro: Text(cmbCLGaeroporto.Selected.Result),
            empresaBusca: txtBuscarInspPatio_4.Text
        },
        FirstN(
            SortByColumns(
                Filter(
                    AddColumns(
                        Sort(tbl_Checklist_generico_base, ID, SortOrder.Descending),
                        EmpresaNome,
                        // col_clgVeiculosEmpresa: (ID, Empresa) de todos os veículos, carregado 1x em ButtonRefreshCLG
                        Coalesce(LookUp(col_clgVeiculosEmpresa, ID = ID_FK).Empresa, "")
                    ),
                    StartsWith(Bloco, blocoFiltro) &&
                    StartsWith(Aeroporto, aeroportoFiltro) &&
                    (IsBlank(empresaBusca) || StartsWith(EmpresaNome, empresaBusca))
                ),
                "ID",
                SortOrder.Descending
            ),
            Value(txtLimit_5.Text)
        )
    )
)'''

ONSELECT_REFRESH_CLG = '''=//Refresh(tbl_Checklist_generico_objeto);;
//Refresh(tbl_Checklist_generico_base);;
ClearCollect(
    col_veic_equip,
    Filter(
        Sort(
            tbl_Veiculos_equipamentos,
            ID,
            SortOrder.Descending
        ),
        Aeroporto = cmbCLGaeroporto.Selected.Result
    )
);
// carregadas uma vez por atualização; substituem consultas por linha nas galerias
ClearCollect(
    col_clgNaoConf,
    Filter(
        tbl_Checklist_generico_objeto,
        Resposta = "Não conforme",
        Status <> "Normalizado"
    )
);
ClearCollect(
    col_clgVeiculosEmpresa,
    ForAll(
        tbl_Veiculos_equipamentos As V,
        {ID: V.ID, Empresa: V.Empresa}
    )
);
ClearCollect(col_clgClasses, tbl_Checklist_generico_classe);
UpdateContext({var_clgIdEstadoGeral: LookUp(col_clgClasses, Item = "Estado geral", ID)});
If(
    IsEmpty(col_userNotifyCriticidade),
    ClearCollect(
        col_userNotifyCriticidade,
        tbl_userNotify
    )
)'''

CIRURGIAS = [
    # ── Lote A: mecânico, mesmo valor em runtime ─────────────────────────────
    dict(id='A1', lote='A', tipo='regex',
         descricao='MainContainerListar.Width (frmHomePista) -> largura da tela',
         # MainContainerListar é filho de ContainerTelas > ContainerMain (Width = Max(App.Width, ...)),
         # todos SetByContainer sem Width: a largura dele é a da tela.
         telas=['frmHomePatio', 'frmHomeTPS', 'frmHomeZPA', 'frmVeiculos_Equipamentos',
                'frmCheckListGenericoEQP', 'frmInspPistaCad'],
         localizar=r'(?<![\w.\'])MainContainerListar\.Width', substituir=APP_WIDTH,
         esperado={'frmHomePatio': 1, 'frmHomeTPS': 1, 'frmHomeZPA': 1, 'frmVeiculos_Equipamentos': 1,
                   'frmCheckListGenericoEQP': 1, 'frmInspPistaCad': 1}),
    dict(id='A1b', lote='A', tipo='regex',
         descricao='MainContainerListarApont.Width (frmHomeApont) -> largura da tela',
         telas=['frmHomePatio', 'frmHomeTPS', 'frmZPAapontamentos'],
         localizar=r'(?<![\w.\'])MainContainerListarApont\.Width', substituir=APP_WIDTH,
         esperado={'frmHomePatio': 2, 'frmHomeTPS': 2, 'frmZPAapontamentos': 2}),
    dict(id='A2', lote='A', tipo='regex',
         descricao='Icon28_195.HoverColor (frmHomePatio:190) -> literal RGBA(96, 70, 237, 1)',
         telas=['frmHomePista'],
         localizar=r'(?<![\w.\'])Icon28_195\.HoverColor', substituir='RGBA(96, 70, 237, 1)',
         esperado={'frmHomePista': 3}),
    dict(id='A3', lote='A', tipo='prop',
         descricao='contador "Itens apontados" lia galeria/lista de outra tela -> locais (var_directDetInsp é sempre 0 aqui: texto continua vazio)',
         alvos=[
             ('frmHomePatio', 'Label9_15', 'Text', [
                 ('CountRows(GalleryApontListagem.AllItems)', 'GalleryInspPatioitens.AllItemsCount'),
                 ("'7.4-tbl_InspPista'", 'tbl_inspPatio')]),
             ('frmHomeTPS', 'Label9_17', 'Text', [
                 ('CountRows(GalleryApontListagem.AllItems)', 'GalleryInspTPSnc.AllItemsCount'),
                 ("'7.4-tbl_InspPista'", 'tbl_inspTPS')]),
         ]),
    dict(id='A3z', lote='A', tipo='prop_regex',
         descricao='idem para frmZPAapontamentos (tbl_inspZpa não tem Protocolo: mostra o ID; ramo nunca executa, var = 0)',
         alvos=[('frmZPAapontamentos', 'Label9_63', 'Text', [
             (r'CountRows\(GalleryApontListagem\.AllItems\)', 'GalleryInspPatioitens_1.AllItemsCount', 1),
             (r"LookUp\(\s*'[^']*',\s*ID = var_directDetInsp,\s*Protocolo\s*\)", 'var_directDetInsp', 1)])]),
    dict(id='A3b', lote='A', tipo='prop',
         descricao='frmZPAapontamentos lia seleção de galerias de frmHomePatio/frmFormZPAeditar -> seleção local',
         alvos=[
             ('frmZPAapontamentos', 'Label18_9', 'Text', [
                 ('GalleryInspPatioitens.Selected.Aeroporto', 'GalleryInspPatioitens_1.Selected.Aeroporto'),
                 ('"-INSP-PAT-ITEM-" & GalleryInspPatioitens.Selected.ID', '"-INSP-ZPA-ITEM-" & GalleryInspPatioitens_1.Selected.ID')]),
             ('frmZPAapontamentos', 'Label5_8', 'Text', [
                 ('Gallery5_2.Selected.ID', 'var_gerItemExcluir.ID')]),
         ]),
    dict(id='A4', lote='A', tipo='regex',
         descricao='CountRows(G.AllItems) -> G.AllItemsCount (não materializa a galeria)',
         localizar=r'CountRows\(([A-Za-z_]\w*)\.AllItems\)', substituir=r'\1.AllItemsCount',
         # (contagem em texto ativo, depois de A3 ter tratado os 3 contadores cross-screen;
         #  as demais ocorrências do export estão em código comentado)
         esperado={'frmFormZPAmenu': 1, 'frmHomeApont': 3, 'frmHomePatio': 2, 'frmHomePista': 1,
                   'frmHomeTPS': 2, 'frmInspPistaCad': 1}),
    dict(id='A5', lote='A', tipo='set_prop',
         descricao='DelayOutput nos campos de busca/limite (evita re-consulta a cada tecla)',
         prop='DelayOutput', valor='=true',
         controles={
             'frmCheckListGenericoEQP': ['txtLimit_5', 'txtBuscarInspPatio_4'],
             'frmHomeApont': ['txtLimitApont'],
             'frmHomePatio': ['txtLimit_1', 'txtBuscarInspPatio', 'txtLimitApont_1'],
             'frmHomePista': ['txtLimit', 'txtBuscarInspPista'],
             'frmHomeTPS': ['txtLimit_2', 'txtBuscarInspPatio_1', 'txtLimitApont_2'],
             'frmHomeZPA': ['txtLimit_3', 'txtBuscarInspPatio_2'],
             'frmInspPistaCad': ['txtBuscarInspPistaProtocolo_4'],
             'frmVeiculos_Equipamentos': ['txtLimit_4', 'txtBuscarInspPatio_3'],
             'frmZPAapontamentos': ['txtLimitApont_3'],
         },
         esperado_total=17),
    dict(id='A6', lote='A', tipo='remover_var',
         descricao='variáveis escritas e nunca lidas (App Checker UnusedVariables, reconferido)',
         # App.* fica para o Lote C (OnStart reescrito); ScreenConsultarV1 é tela morta.
         variaveis={
             'frmCheckListGenericoEQP': ['var_visibleExcluirInspZpa'],
             'frmFormZPAeditar': ['var_loadSave', 'var_zpa_acao'],
             'frmFormZPAmenu': ['var_visibleCntZpa1', 'var_visibleCntZpa2'],
             'frmHome': ['var_visibleContinue', 'var_visibleFilterInspPista', 'var_visibleFormItensDetalhes',
                         'var_visibleInspPistaDetalhes', 'var_visibleInspecaoCad', 'var_visibleInspecaoCad1',
                         'var_visibleInspecaoCad2', 'var_visibleInspecaoCad3', 'var_visibleInspecaoPista',
                         'var_usuarioID'],
             'frmHomeApont': ['var_formSelect', 'var_idFormFauna'],
             'frmHomePatio': ['varCategoria', 'varSubCategoria', 'var_visibleInspPatio',
                              'var_visibleInspPatiocad3', 'var_visibleInspecaoCad3'],
             'frmHomePista': ['var_acaoFormItensDetalhes', 'var_preencherApont', 'var_visibleContinue',
                              'var_visibleFilterInspPista', 'var_visibleFormItensDetalhes',
                              'var_visibleInspecaoCad', 'var_visibleInspecaoCad1', 'var_visibleInspecaoCad2',
                              'var_visibleInspecaoCad3', 'var_visibleInspecaoPista', 'var_visibleRelatorio',
                              'var_visibleSalvarManual'],
             'frmHomeTPS': ['varCategoria', 'varSubCategoria', 'var_visibleInspPatio',
                            'var_visibleInspPatiocad3', 'var_visibleInspecaoCad3'],
             'frmHomeZPA': ['Var_IDinspTPS', 'var_acao', 'var_status', 'var_visibleInspPatio',
                            'var_visibleInspPatiocad', 'var_visibleInspPatiocad1', 'var_visibleInspPatiocad2',
                            'var_visibleInspPatiocadMenu', 'var_usuarioID', 'var_idItensZPA'],
             'frmInspPistaCad': ['varCategoria', 'varSubCategoria', 'var_visibleInspecaoPista', 'var_visibleModal'],
             'frmRelatorioVistoVeic': ['var_detalhaItens', 'var_detalhaVE'],
             'frmVeiculos_Equipamentos': ['var_loadSave', 'var_visibleInspPatio'],
         },
         # escritas removidas por tela (inclui chaves em Navigate(tela, ..., {...}) de outras telas)
         esperado={'frmCheckListGenericoEQP': 1, 'frmFormZPAeditar': 4, 'frmFormZPAmenu': 10, 'frmHome': 10,
                   'frmHomeApont': 6, 'frmHomePatio': 20, 'frmHomePista': 25, 'frmHomeTPS': 18, 'frmHomeZPA': 10,
                   'frmInspPistaCad': 11, 'frmRelatorioVistoVeic': 2, 'frmVeiculos_Equipamentos': 2}),
    dict(id='A7', lote='A', tipo='remover_controle',
         descricao='controles Visible=false sem nenhuma referência (peso morto)',
         controles={
             'frmHome': ['NavInspecao_1', 'LinkAirportNow_1', 'NavMob_1'],
             'frmHomePatio': ['PdfViewer3', 'Circle1_10', 'Circle1_11', 'Circle1_12', 'Circle1_13',
                              'Circle1_14', 'Circle1_15', 'Circle1_20'],
             'frmHomeTPS': ['PdfViewer3_1', 'Circle1_16', 'Circle1_17', 'Circle1_18', 'Circle1_19',
                            'Circle1_22', 'Circle1_23'],
             'frmFormZPAmenu': ['Circle1_21', 'Circle1_24', 'Circle1_25', 'Circle1_26', 'Circle1_30'],
             # bloco de "busca específica" oculto, com 3 Distinct sobre lista SharePoint;
             # só se referenciam entre si — remover do dependente para o dependido
             'frmHomeApont': ['cmbHomeSubitem_3', 'cmbHomeItem_3', 'cmbHomeLocal_3',
                              'Label20_761', 'Label20_760', 'Label20_759', 'Toggle1BuscEsp_3'],
         },
         esperado_total=30),

    # ── Lote B: delegação e consultas por linha ──────────────────────────────
    dict(id='B1', lote='B', tipo='prop_regex',
         descricao='galerias: tira "IsBlank(x) ||" (não delega) dos StartsWith e das datas',
         alvos=[
             ('frmHomePista', 'GalleryInspPistaListagem', 'Items',
              [(RE_GUARDA_STARTSWITH, _sem_guarda_startswith, 3), (RE_GUARDA_DATA, _sem_guarda_data, 2)]),
             ('frmHomePatio', 'GalleryInspPatioListagem_1', 'Items',
              [(RE_GUARDA_STARTSWITH, _sem_guarda_startswith, 3), (RE_GUARDA_DATA, _sem_guarda_data, 2)]),
             ('frmHomePatio', 'GalleryInspPatioitens', 'Items',
              [(RE_GUARDA_STARTSWITH, _sem_guarda_startswith, 5)]),
             ('frmHomeTPS', 'GalleryInspTPSnc', 'Items',
              [(RE_GUARDA_STARTSWITH, _sem_guarda_startswith, 5)]),
             ('frmHomeApont', 'GalleryApontListagem', 'Items',
              [(RE_GUARDA_STARTSWITH, _sem_guarda_startswith, 6)]),
             ('frmZPAapontamentos', 'GalleryInspPatioitens_1', 'Items',
              [(RE_GUARDA_STARTSWITH, _sem_guarda_startswith, 5),
               # 3º ramo sem teto: passa a respeitar txtLimitApont_3 como as demais telas
               (r'(\n(\s*))SortByColumns\(\s*\n(\s*)Filter\(\s*\n\s*tbl_inspZPAitens,',
                lambda mt: f"{mt.group(1)}FirstN({mt.group(1)}SortByColumns(\n{mt.group(3)}Filter(\n{mt.group(3)}    tbl_inspZPAitens,", 1),
               # (strings ficam mascaradas na busca: "ID" vira "[^"]*"; o texto original é o que entra no resultado)
               (r'("[^"]*",\s*\n\s*SortOrder\.Descending\s*\n)(\s*)\)',
                lambda mt: f'{mt.group(1)}{mt.group(2)}),\n{mt.group(2)}Value(txtLimitApont_3.Text)\n{mt.group(2)})', 1)]),
         ]),
    dict(id='B1b', lote='B', tipo='prop_set',
         descricao='frmHomeZPA: busca por ID em ramo próprio (Switch de Filters delegáveis)',
         alvos=[('frmHomeZPA', 'GalleryInspTPSListagem_1', 'Items', ITEMS_ZPA_HOME)]),
    dict(id='B2', lote='B', tipo='regex',
         descricao='Year(Criado) = Year(Today()) -> Criado >= Date(Year(Today()), 1, 1) (delegável)',
         telas=['frmHomePista'],
         localizar=r'Year\(Criado\) = Year\(Today\(\)\)', substituir='Criado >= Date(Year(Today()), 1, 1)',
         esperado={'frmHomePista': 3}),
    dict(id='B3b', lote='B', tipo='prop',
         descricao='ícone/botão por linha: condição barata antes da consulta (curto-circuito) e LookUp em vez de First(Filter)',
         alvos=[
             ('frmHomePista', 'Icon28_209', 'DisplayMode', [
                 ("=If(\n    LookUp(\n        '7.4.1-tbl_InspPistaItens',\n        IdInsp = ThisItem.ID,\n        ID\n    ) > 0 And ThisItem.Status = \"Finalizado\",",
                  "=If(\n    ThisItem.Status = \"Finalizado\" And !IsBlank(\n        LookUp(\n            '7.4.1-tbl_InspPistaItens',\n            IdInsp = ThisItem.ID,\n            ID\n        )\n    ),")]),
             ('frmHomePatio', 'ButtonCanvas39_1', 'Visible', [
                 ("=First(\n    Filter(\n        tbl_inspPatioItens,\n        ID_insp = ThisItem.ID\n    )\n).ID > 0 And ThisItem.Status = \"Finalizado\"",
                  "=ThisItem.Status = \"Finalizado\" And !IsBlank(LookUp(tbl_inspPatioItens, ID_insp = ThisItem.ID, ID))")]),
             ('frmHomeTPS', 'ButtonCanvas39_3', 'Visible', [
                 ("=First(\n    Filter(\n        tbl_inspTPSitens,\n        ID_insp = ThisItem.ID\n    )\n).ID > 0 And ThisItem.Status = \"Finalizado\"",
                  "=ThisItem.Status = \"Finalizado\" And !IsBlank(LookUp(tbl_inspTPSitens, ID_insp = ThisItem.ID, ID))")]),
             ('frmHomeZPA', 'ButtonCanvas39_4', 'Visible', [
                 ('=First(Filter(tbl_inspZPAitens, ID_FK = ThisItem.ID)).ID > 0 And ThisItem.Status = "Finalizado"',
                  '=ThisItem.Status = "Finalizado" And !IsBlank(LookUp(tbl_inspZPAitens, ID_FK = ThisItem.ID, ID))')]),
         ]),
    dict(id='B3c', lote='B', tipo='prop_regex',
         descricao='menu de procedimentos: LookUp(Filter(lista, pai), item) por linha -> um LookUp delegável',
         alvos=[
             # (identificadores entre aspas simples ficam mascarados na busca: '[^']*')
             ('frmHomePatio', 'ButtonCanvas34', 'DisplayMode',
              [(r"LookUp\(\s*Filter\(\s*tbl_inspPatioItens,\s*ID_insp = Var_IDinspPatio\s*\),\s*'[^']*' = ThisItem\.ID,\s*ID\s*\)",
                "LookUp(tbl_inspPatioItens, ID_insp = Var_IDinspPatio And 'ID_item (ID_item0)' = ThisItem.ID, ID)", 1)]),
             ('frmHomeTPS', 'ButtonCanvas34_1', 'DisplayMode',
              [(r"LookUp\(\s*Filter\(\s*tbl_inspPatioItens,\s*ID_insp = Var_IDinspTPS\s*\),\s*'[^']*' = ThisItem\.ID,\s*ID\s*\)",
                "LookUp(tbl_inspPatioItens, ID_insp = Var_IDinspTPS And 'ID_item (ID_item0)' = ThisItem.ID, ID)", 1)]),
         ]),
    dict(id='B3d', lote='B', tipo='prop_set',
         descricao='GalleryCLG: N+1 duplo -> coleções carregadas 1x no botão Refresh',
         alvos=[
             ('frmCheckListGenericoEQP', 'GalleryCLG', 'Items', ITEMS_GALLERY_CLG),
             ('frmCheckListGenericoEQP', 'ButtonRefreshCLG', 'OnSelect', ONSELECT_REFRESH_CLG),
             ('frmCheckListGenericoEQP', 'ButtonCanvas7_17', 'FontColor',
              '=If(\n    !IsBlank(LookUp(col_clgNaoConf, ID_checkList = ThisItem.ID).ID),\n    Color.Red,\n    RGBA(\n        0,\n        0,\n        0,\n        1\n    )\n)'),
             ('frmCheckListGenericoEQP', 'Label19_158', 'Text',
              '=LookUp(\n    tbl_Checklist_generico_objeto,\n    ID_checkList = ThisItem.ID And ID_item_classe = var_clgIdEstadoGeral,\n    Resposta\n)'),
             ('frmCheckListGenericoEQP', 'Label20', 'Text',
              '=LookUp(col_clgClasses, ID = ThisItem.ID_item_classe, Item)'),
             ('frmRelatorioVistoVeic', 'Label20_1', 'Text',
              '=LookUp(col_clgClasses, ID = ThisItem.ID_item_classe, Item)'),
         ]),
    dict(id='B3f', lote='B', tipo='prop_set',
         descricao='frmInspPistaCad ButtonCanvas3.DisplayMode: fórmula quebrada com 1 LookUp por linha -> Edit (ramo Disabled inalcançável: o botão só é visível quando o hash não existe)',
         alvos=[('frmInspPistaCad', 'ButtonCanvas3', 'DisplayMode', '=DisplayMode.Edit')]),
    dict(id='B3g', lote='B', tipo='prop_set',
         descricao='protocolo do cabeçalho por linha: derivado do próprio item (IATA-INSP-PAT-ID_insp) em vez de LookUp na lista-pai',
         alvos=[
             ('frmHomePatio', 'HtmlText1_45', 'HtmlText',
              '="<font style=\'color: #0080ff; font-weight: 600\'> Protocolo inspeção</font><br>" & ThisItem.IATA & "-INSP-PAT-" & ThisItem.ID_insp'),
             ('frmHomeTPS', 'HtmlText1_72', 'HtmlText',
              '="<font style=\'color: #0080ff; font-weight: 600\'> Protocolo inspeção</font><br>" & ThisItem.IATA & "-INSP-TPS-" & ThisItem.ID_insp'),
         ]),
    dict(id='B3h', lote='B', tipo='remover_controle',
         descricao='HtmlText1_3 (frmHomeApont): oculto dentro do template, 1 LookUp por linha, ninguém lê',
         controles={'frmHomeApont': ['HtmlText1_3']}, esperado_total=1),
    dict(id='B4', lote='B', tipo='regex',
         descricao='First(Filter(T, ID = x)) -> LookUp(T, ID = x)',
         localizar=r"First\(\s*Filter\(\s*('[^']+'|[A-Za-z_]\w*),\s*ID = ([^()]+?)\s*\)\s*\)",
         substituir=r'LookUp(\1, ID = \2)',
         # vale também para coleções (mesma semântica) — frmCheckListGenericoEQP/frmInspPistaCad
         esperado={'frmHomePista': 5, 'frmHomePatio': 1, 'frmHomeTPS': 1, 'frmCheckListGenericoEQP': 9, 'frmInspPistaCad': 2}),
    dict(id='B5', lote='B', tipo='regex',
         descricao="Foto*.Default: LookUp(...).Foto.Full -> GalleryInspPistaItensDetalhes.Selected.Foto.Full (registro já em memória)",
         telas=['frmHomePista'],
         localizar=r"LookUp\('[^']*', ID = GalleryInspPistaItensDetalhes\.Selected\.ID\)\.(Foto\d?)\.Full",
         substituir=r'GalleryInspPistaItensDetalhes.Selected.\1.Full',
         esperado={'frmHomePista': 9}),
    dict(id='B6', lote='B', tipo='regex',
         descricao='tbl_userNotify inteira a cada entrada na tela -> uma vez por sessão',
         telas=['frmVeiculos_Equipamentos'],
         localizar=r'ClearCollect\(\s*col_userNotifyCriticidade,\s*tbl_userNotify\s*\)',
         substituir='If(IsEmpty(col_userNotifyCriticidade), ClearCollect(col_userNotifyCriticidade, tbl_userNotify))',
         esperado={'frmVeiculos_Equipamentos': 1}),

    # ── Lote C: App.Formulas, OnStart, derivados do perfil, relatórios ──────
    dict(id='C1', lote='C', tipo='func', descricao='App.Formulas: nfAeros extraída byte a byte do OnStart',
         telas=['App'], fn=CD.c1_tabelas, esperado={'App': 1}),
    dict(id='C2', lote='C', tipo='func',
         descricao='App.OnStart enxuto: 1 LookUp(User), sem Max() não delegável, derivados do perfil calculados 1x',
         telas=['App'], fn=CD.c2_onstart, esperado={'App': 1}),
    dict(id='C4', lote='C', tipo='func',
         descricao='frmHomePista.OnVisible: 89 registros literais de espécies -> nfParametrosAnimais (App.Formulas)',
         telas=['frmHomePista'], fn=CD.c4_parametros_animais, esperado={'frmHomePista': 1}),
    dict(id='C4b', lote='C', tipo='regex', descricao='leitores de col_parametrosAnimais -> nfParametrosAnimais',
         # (3 leitores; as 2 ocorrências do bloco ClearCollect já saíram em C4)
         telas=['frmHomePista'], localizar=r'\bcol_parametrosAnimais\b', substituir='nfParametrosAnimais',
         esperado={'frmHomePista': 3}),
    dict(id='C5a', lote='C', tipo='regex',
         descricao='DisplayMode por perfil (Base/Bloco) repetido -> varModoFiltroBloco (calculado 1x no OnStart)',
         telas=['frmCheckListGenericoEQP', 'frmHomeApont', 'frmHomePatio', 'frmHomePista', 'frmHomeTPS', 'frmHomeZPA',
                'frmInspPistaCad', 'frmVeiculos_Equipamentos', 'frmZPAapontamentos'],
         localizar=RE_MODO_BLOCO, substituir='varModoFiltroBloco', verificar=r'"Base" Or varPerfilUser = "Bloco"',
         esperado={'frmCheckListGenericoEQP': 1, 'frmHomeApont': 1, 'frmHomePatio': 2, 'frmHomePista': 1, 'frmHomeTPS': 2,
                   'frmHomeZPA': 1, 'frmInspPistaCad': 1, 'frmVeiculos_Equipamentos': 1, 'frmZPAapontamentos': 1}),
    dict(id='C5b', lote='C', tipo='regex',
         descricao='DisplayMode por perfil (Base) repetido -> varModoFiltroAero',
         telas=['frmCheckListGenericoEQP', 'frmHomeApont', 'frmHomePatio', 'frmHomePista', 'frmHomeTPS', 'frmHomeZPA',
                'frmInspPistaCad', 'frmVeiculos_Equipamentos', 'frmZPAapontamentos'],
         localizar=RE_MODO_AERO, substituir='varModoFiltroAero', verificar=r'"Base"',
         esperado={'frmCheckListGenericoEQP': 1, 'frmHomeApont': 1, 'frmHomePatio': 2, 'frmHomePista': 1, 'frmHomeTPS': 2,
                   'frmHomeZPA': 1, 'frmInspPistaCad': 1, 'frmVeiculos_Equipamentos': 1, 'frmZPAapontamentos': 1}),
    dict(id='C5c', lote='C', tipo='regex',
         descricao='bloco padrão do combo por perfil repetido -> varBlocoPadrao',
         telas=['frmHomeApont', 'frmHomePatio', 'frmHomePista', 'frmHomeTPS', 'frmHomeZPA', 'frmInspPistaCad', 'frmZPAapontamentos'],
         localizar=RE_BLOCO_PADRAO, substituir='varBlocoPadrao', verificar=r'"Base"[\s\S]*"Bloco"',
         esperado={'frmHomeApont': 1, 'frmHomePatio': 2, 'frmHomePista': 1, 'frmHomeTPS': 2, 'frmHomeZPA': 1,
                   'frmInspPistaCad': 1, 'frmZPAapontamentos': 1}),
    dict(id='C6a', lote='C', tipo='prop_regex',
         descricao='relatório Pátio/TPS: Filter(SP) dentro de ForAll(menu) (1 consulta por item do menu) -> 1 consulta antes',
         alvos=[
             ('frmHomePatio', 'ButtonCanvas7_8', 'OnSelect',
              # (o grupo de indentação só aceita espaços: a linha de comentário acima do ForAll não entra nele)
              [(r'Filter\(\s*(tbl_insp\w+),\s*ID_insp = Var_InspRelatorios\.ID\s*\) As ITEM', 'col_relatorioItensInsp As ITEM', 1),
               (r'(\n([ \t]*))ForAll\([ \t]*\n[ \t]*(col_insp\w+) As MENU,',
                lambda mt: f"{mt.group(1)}ClearCollect(col_relatorioItensInsp, Filter(tbl_inspPatioItens, ID_insp = Var_InspRelatorios.ID));{mt.group(1)}ForAll(\n{mt.group(2)}    {mt.group(3)} As MENU,", 1)]),
             ('frmHomeTPS', 'ButtonCanvas7_11', 'OnSelect',
              [(r'Filter\(\s*(tbl_insp\w+),\s*ID_insp = Var_InspRelatorios\.ID\s*\) As ITEM', 'col_relatorioItensInsp As ITEM', 1),
               (r'(\n([ \t]*))ForAll\([ \t]*\n[ \t]*(col_insp\w+) As MENU,',
                lambda mt: f"{mt.group(1)}ClearCollect(col_relatorioItensInsp, Filter(tbl_inspTPSitens, ID_insp = Var_InspRelatorios.ID));{mt.group(1)}ForAll(\n{mt.group(2)}    {mt.group(3)} As MENU,", 1)]),
         ]),
    dict(id='C6b', lote='C', tipo='func',
         descricao='relatório Pista: ForAll+Remove+LookUp O(n·m) -> Filter único; HTML montado só no clique; guarda do PDF',
         telas=['frmHomePista'],
         fn=lambda t, x, c, ctx: CD.c6_relatorio(t, x, c, ctx, 'HtmlText3_5', 'Icon28_208', 'var_htmlRelPista', CD.ONSELECT_RELATORIO_PISTA),
         esperado={'frmHomePista': 1}),
    dict(id='C6c', lote='C', tipo='func',
         descricao='relatório Apontamentos: HTML montado só no clique; guarda do PDF',
         telas=['frmHomeApont'],
         fn=lambda t, x, c, ctx: CD.c6_relatorio(t, x, c, ctx, 'HtmlText3', 'ButtonCanvas4', 'var_htmlRelApont'),
         esperado={'frmHomeApont': 1}),
    dict(id='C6d', lote='C', tipo='func',
         descricao='relatório Pátio: HTML montado só no clique; guarda do PDF',
         telas=['frmHomePatio'],
         fn=lambda t, x, c, ctx: CD.c6_relatorio(t, x, c, ctx, 'HtmlText3_1', 'ButtonCanvas4_1', 'var_htmlRelPatio'),
         esperado={'frmHomePatio': 1}),
    dict(id='C6e', lote='C', tipo='func',
         descricao='relatório TPS: HTML montado só no clique; guarda do PDF',
         telas=['frmHomeTPS'],
         fn=lambda t, x, c, ctx: CD.c6_relatorio(t, x, c, ctx, 'HtmlText3_4', 'ButtonCanvas4_2', 'var_htmlRelTPS'),
         esperado={'frmHomeTPS': 1}),

    # ── Lote D: bugs de cópia, navegação sem referência a outra tela, erro visível ──
    dict(id='D1', lote='D', tipo='prop_set',
         descricao='Checklist: dois Patch idênticos em Concurrent -> um',
         alvos=[('frmCheckListGenericoEQP', 'ButtonCanvas40', 'OnSelect', CD.ONSELECT_NORMALIZAR_VE)]),
    dict(id='D2', lote='D', tipo='prop_regex',
         descricao='frmHomeTPS operava formulários e lista de PÁTIO -> equivalentes TPS',
         alvos=[
             ('frmHomeTPS', 'ButtonCanvas34_1', 'DisplayMode', [(r'\btbl_inspPatioItens\b', 'tbl_inspTPSitens', 1)]),
             ('frmHomeTPS', 'ButtonCanvas34_1', 'OnSelect', [(r'NewForm\(FormInspPatioitens\)', 'NewForm(FormInspTPSitens)', 1)]),
             ('frmHomeTPS', 'ButtonCanvas8_3', 'OnSelect', [(r'EditForm\(FormGerInspPatioitem\)', 'EditForm(FormGerInspTPSitem)', 1)]),
             ('frmHomeTPS', 'Icon1_24', 'OnSelect', [(r'ResetForm\(FormGerInspPatioitem\)', 'ResetForm(FormGerInspTPSitem)', 1)]),
         ]),
    dict(id='D2t', lote='D', tipo='regex',
         descricao='frmHomeTPS: cabeçalho do formulário de normalização dizia "-INSP-PAT-ITEM-" (protocolo de Pátio) -> "-INSP-TPS-ITEM-"',
         # (só a ocorrência que vem logo depois de LookUp(colAeros, ..., IATA): ") & "…")
         telas=['frmHomeTPS'], localizar=r'\)\s*&\s*"[^"]*" & GalleryInspTPSnc\.Selected\.ID', verificar=r'-INSP-PAT-ITEM-',
         substituir=lambda mt: mt.group(0).split('&', 1)[0] + '& "-INSP-TPS-ITEM-" & GalleryInspTPSnc.Selected.ID',
         esperado={'frmHomeTPS': 1}),
    dict(id='D2z', lote='D', tipo='prop_regex',
         descricao='frmZPAapontamentos usava o formulário de normalização de PÁTIO -> FormGerInspZpaItens (local)',
         alvos=[
             ('frmZPAapontamentos', 'ButtonCanvas8_6', 'OnSelect', [(r'EditForm\(FormGerInspPatioitem\)', 'EditForm(FormGerInspZpaItens)', 1)]),
             ('frmZPAapontamentos', 'Icon1_29', 'OnSelect', [(r'ResetForm\(FormGerInspPatioitem\)', 'ResetForm(FormGerInspZpaItens)', 1)]),
         ]),
    dict(id='D3', lote='D', tipo='prop_regex',
         descricao='frmHomeApont: SubmitForm de formulário que só existe em frmHomePista (escrita fantasma) removido',
         alvos=[(('frmHomeApont'), f, 'OnSuccess', [(r'SubmitForm\(FormInspPistaItensDetalhes\);\s*', '', 1)])
                for f in ('FormInspPistaItensDetalhesColisao_1', 'FormInspPistaItensDetalhesPRESENCA_1', 'FormInspPistaItensDetalhesFOCO_1')]),
    dict(id='D4', lote='D', tipo='prop_set',
         descricao='frmFormZPAeditar: fotos gravadas com Defaults() a cada edição (duplicava) e imagens de outra tela -> atualiza o registro existente com as imagens locais',
         alvos=[('frmFormZPAeditar', 'FormZpaEdit', 'OnSuccess', CD.ONSUCCESS_ZPA_EDITAR)]),
    dict(id='D7a', lote='D', tipo='prop_regex',
         descricao='preparação de formulário de OUTRA tela antes do Navigate -> sai daqui e vai para o OnVisible da tela de destino',
         alvos=[
             ('frmHomeZPA', 'Icon28_200', 'OnSelect',
              [(r';\s*ResetForm\(FormZpa\);\s*NewForm\(FormZpa\)' + RESETS_ZPA, '', 1),
               (r'\{var_zpa_acao: "[^"]*"\}', '{var_zpa_acao: "cad", var_zpa_modo: "novo"}', 1)]),
             ('frmHomeZPA', 'ButtonCanvas35_3', 'OnSelect', [(r';\s*EditForm\(FormInspTPS\)', '', 1)]),
             ('frmHomeZPA', 'ButtonCanvas7_13', 'OnSelect', [(r';\s*EditForm\(FormZpaEdit\)', '', 1)]),
             ('frmHomePista', 'Icon28_201', 'OnSelect', [(r';\s*ResetForm\(FormInspPistaCad1_2\);\s*NewForm\(FormInspPistaCad1_2\)', '', 1)]),
             ('frmHomePista', 'Icon28_210', 'OnSelect', [(r';\s*EditForm\(FormInspPistaCad1_2\)', '', 1)]),
             ('frmVeiculos_Equipamentos', 'Icon28_202', 'OnSelect', [(RESETS_ZPA, '', 1)]),
         ]),
    dict(id='D7b', lote='D', tipo='prop_add',
         descricao='OnVisible das telas de destino faz a preparação (NewForm/EditForm/Reset) que a origem fazia',
         alvos=[
             ('frmFormZPA', 'frmFormZPA', 'OnVisible', CD.ONVISIBLE_FORMZPA),
             ('frmFormZPAeditar', 'frmFormZPAeditar', 'OnVisible', CD.ONVISIBLE_FORMZPA_EDITAR),
             ('frmInspPistaCad', 'frmInspPistaCad', 'OnVisible', CD.ONVISIBLE_INSPPISTACAD),
         ]),
    dict(id='D8', lote='D', tipo='set_prop',
         descricao='OnFailure em todo formulário que não tinha (falha de gravação deixa de ser silenciosa)',
         prop='OnFailure', valor=CD.ONFAILURE_PADRAO, controles=FORMS_SEM_ONFAILURE, esperado_total=18),
    dict(id='D8z', lote='D', tipo='prop_add',
         descricao='FormZpa: OnFailure só desligava o spinner -> também avisa',
         alvos=[('frmFormZPA', 'FormZpa', 'OnFailure', CD.ONFAILURE_ZPA)]),
]
