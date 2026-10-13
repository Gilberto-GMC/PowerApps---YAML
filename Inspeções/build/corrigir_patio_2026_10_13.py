# -*- coding: utf-8 -*-
"""Correção pontual de frmHomePatio sobre o código colado pelo usuário em 2026-10-13.

Entrada : correcoes/2026-10-13_frmHomePatio_entrada.pa.yaml (Exibição de código do Studio, CRLF->LF)
Saída   : correcoes/2026-10-13_frmHomePatio.pa.yaml

Cada substituição é exata e exige o número de ocorrências declarado; qualquer
divergência aborta sem gravar. Determinístico: rodar duas vezes dá o mesmo hash.
"""
import sys, os, re, hashlib

RAIZ = os.path.join(os.path.dirname(__file__), '..')
ENTRADA = os.path.join(RAIZ, 'correcoes', '2026-10-13_frmHomePatio_entrada.pa.yaml')
SAIDA = os.path.join(RAIZ, 'correcoes', '2026-10-13_frmHomePatio.pa.yaml')

I_DD = ' ' * 30   # indentação das propriedades dos dropdowns de filtro


def combo(ctrl, coluna):
    """Ungroup(Table(...Distinct...)) + Default "Todos" -> padrão já compilado em frmHomeApont.cmbHomeLocal."""
    antes = (
        f"                        - {ctrl}:\n"
        f"                            Control: Classic/DropDown@2.3.1\n"
        f"                            Properties:\n"
        f"{I_DD}BorderColor: =RGBA(96, 70, 237, 1)\n"
    )
    depois = (
        f"                        - {ctrl}:\n"
        f"                            Control: Classic/DropDown@2.3.1\n"
        f"                            Properties:\n"
        f"{I_DD}AllowEmptySelection: =true\n"
        f"{I_DD}BorderColor: =RGBA(96, 70, 237, 1)\n"
    )
    items_antes = (
        f"{I_DD}Default: =\"Todos\"\n"
        f"{I_DD}Fill: =RGBA(245, 245, 245, 1)\n"
        f"{I_DD}Height: =30\n"
        f"{I_DD}HoverFill: =RGBA(241, 244, 249, 1)\n"
        f"{I_DD}Items: |-\n"
        f"{I_DD}  =Ungroup(\n"
        f"{I_DD}      Table(\n"
        f"{I_DD}          {{opcoes: Table({{Value: \"\"}})}},\n"
        f"{I_DD}          {{opcoes: Distinct(\n"
        f"{I_DD}              col_inspPatiomenu,\n"
        f"{I_DD}              {coluna}\n"
        f"{I_DD}          )}}\n"
        f"{I_DD}      ),\n"
        f"{I_DD}      \"opcoes\"\n"
        f"{I_DD}  )\n"
    )
    items_depois = (
        f"{I_DD}Default: =\"\"\n"
        f"{I_DD}Fill: =RGBA(245, 245, 245, 1)\n"
        f"{I_DD}Height: =30\n"
        f"{I_DD}HoverFill: =RGBA(241, 244, 249, 1)\n"
        f"{I_DD}Items: |-\n"
        f"{I_DD}  =Distinct(\n"
        f"{I_DD}      col_inspPatiomenu,\n"
        f"{I_DD}      {coluna}\n"
        f"{I_DD}  )\n"
    )
    return [(antes, depois, 1), (items_antes, items_depois, 1)]


def filtro_galeria():
    """GalleryInspPatioitens.Items: IsBlank(x) || StartsWith(col, x) -> StartsWith(col, Text(x));
    teto de data Today() (00:00) -> fim do dia."""
    p = ' ' * 42
    antes = (
        f"{p}(IsBlank(cmbHomeAeroporto_5.Selected.Result) || StartsWith(\n"
        f"{p}    Aeroporto,\n"
        f"{p}    Text(cmbHomeAeroporto_5.Selected.Result)\n"
        f"{p})) && (IsBlank(cmbHomeBloco_5.Selected.Value) || StartsWith(\n"
        f"{p}    Bloco,\n"
        f"{p}    Text(cmbHomeBloco_5.Selected.Value)\n"
        f"{p})) && (IsBlank(cmbApontStatus_1.Selected.Value) || StartsWith(\n"
        f"{p}    Status,\n"
        f"{p}    cmbApontStatus_1.Selected.Value\n"
        f"{p})) && (IsBlank(cmbHomeLocal_1.Selected.Value) || StartsWith(\n"
        f"{p}    Local,\n"
        f"{p}    cmbHomeLocal_1.Selected.Value\n"
        f"{p})) && (IsBlank(cmbHomeItem_2.Selected.Value) || StartsWith(\n"
        f"{p}    Item,\n"
        f"{p}    cmbHomeItem_2.Selected.Value\n"
        f"{p})) && Criado >= dtpHomeDtfInicio_5.SelectedDate && Criado <= If(\n"
        f"{p}    IsBlank(dtpHomeDtfTermino_5.SelectedDate),\n"
        f"{p}    Today(),\n"
        f"{p}    DateAdd(\n"
        f"{p}        dtpHomeDtfTermino_5.SelectedDate,\n"
        f"{p}        1,\n"
        f"{p}        TimeUnit.Days\n"
        f"{p}    )// Inclui a data de término\n"
        f"{p})\n"
    )
    depois = (
        f"{p}StartsWith(Aeroporto, Text(cmbHomeAeroporto_5.Selected.Result)) &&\n"
        f"{p}StartsWith(Bloco, Text(cmbHomeBloco_5.Selected.Value)) &&\n"
        f"{p}StartsWith(Status, Text(cmbApontStatus_1.Selected.Value)) &&\n"
        f"{p}StartsWith(Local, Text(cmbHomeLocal_1.Selected.Value)) &&\n"
        f"{p}StartsWith(Item, Text(cmbHomeItem_2.Selected.Value)) &&\n"
        f"{p}Criado >= dtpHomeDtfInicio_5.SelectedDate &&\n"
        f"{p}Criado < DateAdd(\n"
        f"{p}    Coalesce(dtpHomeDtfTermino_5.SelectedDate, Today()),\n"
        f"{p}    1,\n"
        f"{p}    TimeUnit.Days\n"
        f"{p})// Inclui o dia de término inteiro (sem término = até o fim de hoje)\n"
    )
    return [(antes, depois, 1)]


def filtro_relatorio():
    """HtmlText3_1.HtmlText (PDF): mesma consulta da galeria, mesma correção (PDF = tela)."""
    p = ' ' * 38
    antes = (
        f"{p}(IsBlank(cmbHomeAeroporto_5.Selected.Result) || StartsWith(\n"
        f"{p}    Aeroporto,\n"
        f"{p}    Text(cmbHomeAeroporto_5.Selected.Result)\n"
        f"{p})) && \n"
        f"{p}(IsBlank(cmbHomeBloco_5.Selected.Value) || StartsWith(\n"
        f"{p}    Bloco,\n"
        f"{p}    Text(cmbHomeBloco_5.Selected.Value)\n"
        f"{p})) && \n"
        f"{p}(IsBlank(cmbApontStatus_1.Selected.Value) || StartsWith(\n"
        f"{p}    Status,\n"
        f"{p}    cmbApontStatus_1.Selected.Value\n"
        f"{p})) && \n"
        f"{p}(IsBlank(cmbHomeLocal_1.Selected.Value) || StartsWith(\n"
        f"{p}    Local,\n"
        f"{p}    cmbHomeLocal_1.Selected.Value\n"
        f"{p})) && \n"
        f"{p}(IsBlank(cmbHomeItem_2.Selected.Value) || StartsWith(\n"
        f"{p}    Item,\n"
        f"{p}    cmbHomeItem_2.Selected.Value\n"
        f"{p})) && \n"
        f"{p}Criado >= dtpHomeDtfInicio_5.SelectedDate && \n"
        f"{p}Criado <= If(\n"
        f"{p}    IsBlank(dtpHomeDtfTermino_5.SelectedDate),\n"
        f"{p}    Today(),\n"
        f"{p}    DateAdd(dtpHomeDtfTermino_5.SelectedDate, 1, TimeUnit.Days)\n"
        f"{p})\n"
    )
    depois = (
        f"{p}StartsWith(Aeroporto, Text(cmbHomeAeroporto_5.Selected.Result)) &&\n"
        f"{p}StartsWith(Bloco, Text(cmbHomeBloco_5.Selected.Value)) &&\n"
        f"{p}StartsWith(Status, Text(cmbApontStatus_1.Selected.Value)) &&\n"
        f"{p}StartsWith(Local, Text(cmbHomeLocal_1.Selected.Value)) &&\n"
        f"{p}StartsWith(Item, Text(cmbHomeItem_2.Selected.Value)) &&\n"
        f"{p}Criado >= dtpHomeDtfInicio_5.SelectedDate &&\n"
        f"{p}Criado < DateAdd(Coalesce(dtpHomeDtfTermino_5.SelectedDate, Today()), 1, TimeUnit.Days)\n"
    )
    return [(antes, depois, 1)]


def filtro_inspecoes():
    """GalleryInspPatioListagem_1.Items: mesma troca B1 da entrega de 2026-09-17 (out/08)."""
    p = ' ' * 42
    antes = (
        f"{p}IsBlank(cmbHomeAeroporto_1.Selected.Result) || StartsWith(\n"
        f"{p}    Aeroporto,\n"
        f"{p}    Text(cmbHomeAeroporto_1.Selected.Result)\n"
        f"{p}),\n"
        f"{p}IsBlank(cmbHomeBloco_1.Selected.Value) || StartsWith(\n"
        f"{p}    Bloco,\n"
        f"{p}    Text(cmbHomeBloco_1.Selected.Value)\n"
        f"{p}),\n"
        f"{p}IsBlank(cmbHomeStatus_3.Selected.Value) || StartsWith(\n"
        f"{p}    Status,\n"
        f"{p}    cmbHomeStatus_3.Selected.Value\n"
        f"{p}),\n"
        f"{p}IsBlank(dtpHomeDtfInicio_1.SelectedDate) || Inicio >= dtpHomeDtfInicio_1.SelectedDate,\n"
        f"{p}IsBlank(dtpHomeDtfTermino_1.SelectedDate) || Inicio <= dtpHomeDtfTermino_1.SelectedDate\n"
    )
    depois = (
        f"{p}StartsWith(Aeroporto, Text(cmbHomeAeroporto_1.Selected.Result)),\n"
        f"{p}StartsWith(Bloco, Text(cmbHomeBloco_1.Selected.Value)),\n"
        f"{p}StartsWith(Status, Text(cmbHomeStatus_3.Selected.Value)),\n"
        f"{p}Inicio >= Coalesce(dtpHomeDtfInicio_1.SelectedDate, Date(2000, 1, 1)),\n"
        f"{p}Inicio <= Coalesce(dtpHomeDtfTermino_1.SelectedDate, Date(2099, 12, 31))\n"
    )
    return [(antes, depois, 1)]


def cross_screen():
    """Mesmas trocas A1/A1b/A3 da entrega de 2026-09-17 (out/08): mesmo valor, sem carregar outra tela."""
    return [
        ("                        Width: =MainContainerListar.Width - 20\n",
         "                        Width: =Max(App.Width, App.MinScreenWidth) - 20\n", 1),
        ("                        Width: =MainContainerListarApont.Width - 20\n",
         "                        Width: =Max(App.Width, App.MinScreenWidth) - 20\n", 2),
        ("                                    CountRows(GalleryApontListagem.AllItems)&\n",
         "                                    GalleryInspPatioitens.AllItemsCount&\n", 1),
        ("                                        '7.4-tbl_InspPista',\n"
         "                                        ID = var_directDetInsp,\n",
         "                                        tbl_inspPatio,\n"
         "                                        ID = var_directDetInsp,\n", 1),
    ]


def limpar_filtros():
    return [("                                Reset(cmbHomeLocal_1);\n                                Reset(cmbHomeLocal_1);\n",
             "                                Reset(cmbHomeLocal_1);\n", 1)]


def main():
    txt = open(ENTRADA, encoding='utf-8').read().replace('\r\n', '\n')
    trocas = combo('cmbHomeLocal_1', 'local') + combo('cmbHomeItem_2', 'item') \
        + filtro_galeria() + filtro_relatorio() + filtro_inspecoes() + cross_screen() + limpar_filtros()
    for antes, depois, n in trocas:
        achou = txt.count(antes)
        if achou != n:
            sys.exit(f"✗ esperado {n}x, achado {achou}x:\n{antes[:200]}")
        txt = txt.replace(antes, depois)
    if not txt.startswith('Screens:\n  frmHomePatio:\n    Properties:'):
        sys.exit('✗ estrutura raiz')
    ativo = re.sub(r'/\*.*?\*/', '', txt, flags=re.S)   # trechos comentados não contam
    for proibido in ('Ungroup(', 'MainContainerListar', 'GalleryApontListagem', "'7.4-tbl_InspPista'",
                     'IsBlank(cmbHome', 'IsBlank(cmbApont', 'Today(),\n'):
        if proibido in ativo:
            sys.exit(f'✗ resíduo: {proibido!r}')
    open(SAIDA, 'w', encoding='utf-8', newline='\n').write(txt)
    print(f"✓ {len(trocas)} substituições; sha256 {hashlib.sha256(txt.encode()).hexdigest()[:16]}")


if __name__ == '__main__':
    main()
