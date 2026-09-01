# -*- coding: utf-8 -*-
"""Injeta o trilho de navegação (menu lateral) nas telas internas do app de Frotas.
Idempotente: aborta se o menu já existir. Determinístico."""
import re, sys, os
from roteiro_menu import bloco as roteiro_bloco

BASE = '/workspaces/codespaces-blank/Frotas'
TELAS = [  # arquivo, sufixo único de controle, tela raiz, item ativo
    ('scrFrotaPainel.pa.yaml', 'Pnl', 'cntPainelRaiz', 'painel'),
    ('scrFrotaLista.pa.yaml',  'Lst', 'cntListaRaiz',  'frota'),
    ('scrFrotaForm.pa.yaml',   'Frm', 'cntFrmRaiz',    'novo'),
]

NOVO_ATIVO = """=Set(varFormModo, "Novo");
Set(
    varFormRec,
    Patch(
        Defaults('tb_ativosFrota'),
        {
            aeroporto: varAeroUser,
            status: "Ativo",
            situacao_operacional: "Disponível",
            tipo_propriedade: "Próprio",
            circula_lado_ar: 0,
            medidor_km: 0,
            medidor_horas: 0
        }
    )
);
Navigate(scrFrotaForm, ScreenTransition.Fade)"""

def ind(txt, n):
    return "\n".join((" " * n + l) if l.strip() else l for l in txt.split("\n"))

def botao(nome, icone, rotulo, ativo, on_select, base=14, perfil=False):
    L = [f"                      - {nome}:",
         "                          Control: Button@0.0.45",
         "                          Properties:",
         "                            Align: =Align.Left",
         "                            AlignInContainer: =AlignInContainer.Stretch",
         f"                            Appearance: ='ButtonCanvas.Appearance'.{'Primary' if ativo else 'Secondary'}",
         f"                            BasePaletteColor: ={'thmPrimaria' if ativo else 'thmTextoBarra'}",
         "                            BorderRadius: =0",
         "                            FontColor: =thmTextoBarra",
         "                            FontSize: =12",
         "                            FontWeight: =FontWeight.Semibold",
         "                            Height: =44",
         f'                            Icon: ="{icone}"',
         "                            IconStyle: ='ButtonCanvas.IconStyle'.Filled",
         "                            LayoutMinWidth: =0"]
    if perfil:
        L.append("                            DisplayMode: =If(varPerfilNivel >= 3, DisplayMode.Edit, DisplayMode.Disabled)")
        L.sort(key=lambda x: x)  # mantém ordem alfabética das propriedades
        L = [l for l in L if not l.startswith("                      - ")]
        L = [f"                      - {nome}:",
             "                          Control: Button@0.0.45",
             "                          Properties:"] + sorted(
             [l for l in L if l.startswith("                            ")])
    if "\n" in on_select:
        L.append("                            OnSelect: |-")
        L.append(ind(on_select, 30))
    else:
        L.append(f"                            OnSelect: ={on_select}")
    L.append(f'                            PaddingLeft: =18')
    L.append(f'                            Text: =If(varMenuAberto, "{rotulo}", "")')
    return "\n".join(L)

def trilho(suf, ativo):
    b = []
    b.append(f"            - cntMenu{suf}:")
    b.append("                Control: GroupContainer@1.5.0")
    b.append("                Variant: AutoLayout")
    b.append("                Properties:")
    b.append("                  AlignInContainer: =AlignInContainer.Stretch")
    b.append("                  DropShadow: =DropShadow.None")
    b.append("                  Fill: =thmPrimariaEscura")
    b.append("                  FillPortions: =0")
    b.append("                  LayoutAlignItems: =LayoutAlignItems.Stretch")
    b.append("                  LayoutDirection: =LayoutDirection.Vertical")
    b.append("                  LayoutGap: =10")
    b.append("                  LayoutMinHeight: =0")
    b.append("                  PaddingBottom: =14")
    b.append("                  PaddingLeft: =12")
    b.append("                  PaddingRight: =12")
    b.append("                  PaddingTop: =16")
    b.append("                  RadiusBottomLeft: =0")
    b.append("                  RadiusBottomRight: =0")
    b.append("                  RadiusTopLeft: =0")
    b.append("                  RadiusTopRight: =0")
    b.append("                  Width: =If(varMenuAberto, 236, 76)")
    b.append("                Children:")
    # marca
    b.append(f"                  - htmMenuMarca{suf}:")
    b.append("                      Control: HtmlViewer@2.1.0")
    b.append("                      Properties:")
    b.append("                        AlignInContainer: =AlignInContainer.Start")
    b.append("                        AutoHeight: =true")
    b.append("                        Color: =thmTextoBarra")
    b.append("                        Fill: =thmPrimariaEscura")
    b.append("                        Font: =thmFonte")
    b.append("                        HtmlText: |-")
    b.append("""                          ="<div style='" & htmlFonte & "color:" & hxTextoBarra & ";'>" &""")
    b.append("""                          If(""")
    b.append("""                              varMenuAberto,""")
    b.append("""                              "<div style='font-size:10px;letter-spacing:.24em;font-weight:700;opacity:.6;'>MOTIVA</div><div style='font-size:16px;font-weight:800;letter-spacing:.01em;margin-top:2px;'>GESTÃO DE FROTAS</div>",""")
    b.append("""                              "<div style='font-size:17px;font-weight:800;text-align:center;'>MF</div>\"""")
    b.append("""                          ) &""")
    b.append("""                          "</div>\"""")
    b.append("                        PaddingBottom: =14")
    b.append("                        PaddingLeft: =4")
    b.append("                        PaddingRight: =0")
    b.append("                        PaddingTop: =0")
    b.append("                        Size: =11")
    # navegação
    b.append(f"                  - cntMenuNav{suf}:")
    b.append("                      Control: GroupContainer@1.5.0")
    b.append("                      Variant: AutoLayout")
    b.append("                      Properties:")
    b.append("                        AlignInContainer: =AlignInContainer.Stretch")
    b.append("                        DropShadow: =DropShadow.None")
    b.append("                        Fill: =thmPrimariaEscura")
    b.append("                        FillPortions: =1")
    b.append("                        LayoutAlignItems: =LayoutAlignItems.Stretch")
    b.append("                        LayoutDirection: =LayoutDirection.Vertical")
    b.append("                        LayoutGap: =10")
    b.append("                        LayoutMinHeight: =0")
    b.append("                        LayoutOverflowY: =LayoutOverflow.Scroll")
    b.append("                        RadiusBottomLeft: =0")
    b.append("                        RadiusBottomRight: =0")
    b.append("                        RadiusTopLeft: =0")
    b.append("                        RadiusTopRight: =0")
    b.append("                      Children:")
    b.append(botao(f"btnMenuPainel{suf}", "Eye", "PAINEL", ativo == "painel",
                   "Navigate(scrFrotaPainel, ScreenTransition.Fade)"))
    b.append(botao(f"btnMenuFrota{suf}", "Search", "CONSULTAR FROTA", ativo == "frota",
                   '=Set(varFiltroAero, "Todos");\nNavigate(scrFrotaLista, ScreenTransition.Fade)'))
    b.append(botao(f"btnMenuNovo{suf}", "Add", "NOVO ATIVO", ativo == "novo",
                   NOVO_ATIVO, perfil=True))
    # próximos módulos
    b.append(f"                      - htmMenuProximos{suf}:")
    b.append("                          Control: HtmlViewer@2.1.0")
    b.append("                          Properties:")
    b.append("                            AlignInContainer: =AlignInContainer.Stretch")
    b.append("                            AutoHeight: =true")
    b.append("                            Color: =thmTextoBarra")
    b.append("                            Fill: =thmPrimariaEscura")
    b.append("                            FillPortions: =0")
    b.append("                            Font: =thmFonte")
    b.append("                            HtmlText: |-")
    # o roteiro dos 23 módulos foi retirado do trilho pelo usuário (2026-08-26)
    b.append("                            PaddingBottom: =0")
    b.append("                            PaddingLeft: =6")
    b.append("                            PaddingRight: =0")
    b.append("                            PaddingTop: =0")
    b.append("                            Size: =11")
    b.append("                            Visible: =varMenuAberto")
    # rodapé: usuário
    b.append(f"                  - htmMenuUsuario{suf}:")
    b.append("                      Control: HtmlViewer@2.1.0")
    b.append("                      Properties:")
    b.append("                        AlignInContainer: =AlignInContainer.Stretch")
    b.append("                        AutoHeight: =true")
    b.append("                        Color: =thmTextoBarra")
    b.append("                        Fill: =thmPrimariaEscura")
    b.append("                        FillPortions: =0")
    b.append("                        Font: =thmFonte")
    b.append("                        HtmlText: |-")
    b.append("""                          ="<div style='" & htmlFonte & "border-top:1px solid " & hxBordaBarra & ";padding-top:12px;'>" &""")
    b.append("""                          If(""")
    b.append("""                              varMenuAberto,""")
    b.append("""                              "<div style='font-size:12px;font-weight:700;color:" & hxTextoBarra & ";'>" & varUsuario.nome_usuario & "</div><div style='font-size:10px;color:" & hxTextoBarraFraco & ";margin-top:2px;'>" & Upper(varUsuario.perfil) & " &middot; " & varAeroUser & "</div>",""")
    b.append("""                              "<div style='font-size:11px;font-weight:700;color:" & hxTextoBarraSuave & ";text-align:center;'>" & varAeroUser & "</div>\"""")
    b.append("""                          ) &""")
    b.append("""                          "</div>\"""")
    b.append("                        PaddingBottom: =10")
    b.append("                        PaddingLeft: =4")
    b.append("                        PaddingRight: =0")
    b.append("                        PaddingTop: =0")
    b.append("                        Size: =11")
    # recolher + sair
    b.append(f"                  - btnMenuRecolher{suf}:")
    b.append("                      Control: Button@0.0.45")
    b.append("                      Properties:")
    b.append("                        Align: =Align.Left")
    b.append("                        AlignInContainer: =AlignInContainer.Stretch")
    b.append("                        Appearance: ='ButtonCanvas.Appearance'.Secondary")
    b.append("                        BasePaletteColor: =thmTextoBarra")
    b.append("                        BorderRadius: =0")
    b.append("                        FontColor: =thmTextoBarra")
    b.append("                        FontSize: =11")
    b.append("                        FontWeight: =FontWeight.Semibold")
    b.append("                        Height: =38")
    b.append('                        Icon: ="ChevronRight"')
    b.append("                        IconStyle: ='ButtonCanvas.IconStyle'.Filled")
    b.append("                        LayoutMinWidth: =0")
    b.append("                        OnSelect: =Set(varMenuAberto, !varMenuAberto)")
    b.append("                        PaddingLeft: =18")
    b.append('                        Text: =If(varMenuAberto, "RECOLHER MENU", "")')
    b.append(f"                  - btnMenuSair{suf}:")
    b.append("                      Control: Button@0.0.45")
    b.append("                      Properties:")
    b.append("                        Align: =Align.Left")
    b.append("                        AlignInContainer: =AlignInContainer.Stretch")
    b.append("                        Appearance: ='ButtonCanvas.Appearance'.Secondary")
    b.append("                        BasePaletteColor: =thmTextoBarra")
    b.append("                        BorderRadius: =0")
    b.append("                        FontColor: =thmTextoBarra")
    b.append("                        FontSize: =11")
    b.append("                        FontWeight: =FontWeight.Semibold")
    b.append("                        Height: =38")
    b.append('                        Icon: ="ArrowExit"')
    b.append("                        IconStyle: ='ButtonCanvas.IconStyle'.Filled")
    b.append("                        LayoutMinWidth: =0")
    b.append("                        OnSelect: =Navigate(scrLoginContexto, ScreenTransition.Fade)")
    b.append("                        PaddingLeft: =18")
    b.append('                        Text: =If(varMenuAberto, "SAIR DO SISTEMA", "")')
    return "\n".join(b)

def remove_bloco(txt, marcador):
    """Remove o bloco '- nome:' inteiro (até o próximo irmão de mesmo recuo)."""
    i = txt.index(marcador)
    recuo = len(marcador) - len(marcador.lstrip())
    linhas = txt[i:].split("\n")
    fim = len(linhas)
    for k, l in enumerate(linhas[1:], 1):
        if l.strip() and (len(l) - len(l.lstrip())) <= recuo:
            fim = k
            break
    return txt[:i] + "\n".join(linhas[fim:])

for arquivo, suf, raiz, ativo in TELAS:
    p = os.path.join(BASE, arquivo)
    s = open(p, encoding='utf-8').read()
    if f"cntMenu{suf}" in s:
        print(f"  {arquivo}: menu já existe, pulando"); continue

    # 2) recorta o container raiz e re-indenta
    marca = f"      - {raiz}:\n"
    i = s.index(marca)
    cabeca, corpo = s[:i], s[i:]
    corpo = ind(corpo.rstrip("\n"), 6) + "\n"

    # 3) raiz vira coluna flexível dentro do shell
    assert corpo.count("                  Height: =Parent.Height\n") >= 1
    corpo = corpo.replace("                  Height: =Parent.Height\n", "                  FillPortions: =1\n", 1)
    corpo = corpo.replace("                  Width: =Parent.Width\n", "", 1)
    corpo = corpo.replace("                Properties:\n",
                          "                Properties:\n                  AlignInContainer: =AlignInContainer.Stretch\n", 1)

    shell = [f"      - cntShell{suf}:",
             "          Control: GroupContainer@1.5.0",
             "          Variant: AutoLayout",
             "          Properties:",
             "            DropShadow: =DropShadow.None",
             "            Fill: =thmFundo",
             "            Height: =Parent.Height",
             "            LayoutAlignItems: =LayoutAlignItems.Stretch",
             "            LayoutDirection: =LayoutDirection.Horizontal",
             "            LayoutGap: =0",
             "            LayoutMinHeight: =0",
             "            RadiusBottomLeft: =0",
             "            RadiusBottomRight: =0",
             "            RadiusTopLeft: =0",
             "            RadiusTopRight: =0",
             "            Width: =Parent.Width",
             "          Children:",
             trilho(suf, ativo)]
    s = cabeca + "\n".join(shell) + "\n" + corpo
    open(p, 'w', encoding='utf-8').write(s)
    print(f"  {arquivo}: trilho cntMenu{suf} injetado")
