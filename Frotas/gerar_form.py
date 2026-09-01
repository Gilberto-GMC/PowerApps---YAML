# -*- coding: utf-8 -*-
"""Gera Frotas/scrFrotaForm.pa.yaml — cadastro/edição do Módulo 1.
Determinístico: rodar duas vezes tem que dar o mesmo hash."""
import io

# Só os campos do Módulo 1. Campo-espelho de módulo que ainda não existe fica fora
# do cache: não é lido, não é escrito, não entra em conta nenhuma.
COLS = ["ID","codigo_ativo","identificacao_visual","placa","tipo_ativo","categoria_uso","marca","modelo",
        "ano_fabricacao","combustivel","aeroporto","bloco","base_operacional","centro_custo","setor_responsavel",
        "gestor_nome","gestor_email","status","situacao_operacional","motivo_situacao","tipo_medidor",
        "medidor_km","medidor_horas","medidor_data","tipo_propriedade","fornecedor_txt","circula_lado_ar"]

# nome, rótulo, tipo, obrigatório, largura, itens(drp), visible
CAMPOS = [
 ("IDENTIFICAÇÃO","O código FRT é gerado pelo app na gravação — não se digita.",[
   ("identificacao_visual","Identificação Visual","txt",False,300,None,None),
   ("placa","Placa","txt",None,300,None,None),          # obrigatório dinâmico
   ("renavam","RENAVAM","txt",False,300,None,None),
   ("chassi","Chassi","txt",False,300,None,None),
   ("n_serie","Número de Série","txt",False,300,None,None),
   ("n_patrimonio","Nº Patrimônio Contábil","txt",False,300,None,None),
 ]),
 ("CLASSIFICAÇÃO","O tipo de ativo dirige placa e medidor.",[
   ("tipo_ativo","Tipo de Ativo","drp",True,300,"colOpTipo",None),
   ("categoria_uso","Categoria de Uso","drp",True,300,"colOpCategoria",None),
   ("marca","Marca","txt",True,300,None,None),
   ("modelo","Modelo","txt",True,300,None,None),
   ("ano_fabricacao","Ano de Fabricação","num",True,300,None,None),
   ("ano_modelo","Ano do Modelo","num",False,300,None,None),
   ("cor","Cor","txt",False,300,None,None),
   ("combustivel","Combustível","drp",True,300,"colOpCombustivel",None),
   ("capacidade_tanque","Capacidade do Tanque (L)","num",False,300,None,None),
   ("qtd_passageiros","Lotação (passageiros)","num",False,300,None,None),
   ("capacidade_carga_kg","Capacidade de Carga (kg)","num",False,300,None,None),
 ]),
 ("MEDIÇÃO","Hodômetro, horímetro ou nenhum — quem decide é o tipo de ativo.",[
   ("tipo_medidor","Tipo de Medidor","drp",True,300,"colOpMedidor",None),
   ("medidor_km","Hodômetro Atual (km)","num",False,300,None,
      "=LookUp(colTipoMedidor, Valor = drpFrmTipoMedidor.Selected.Value).UsaKm"),
   ("medidor_horas","Horímetro Atual (h)","num",False,300,None,
      "=LookUp(colTipoMedidor, Valor = drpFrmTipoMedidor.Selected.Value).UsaHoras"),
   ("medidor_data","Data da Última Leitura","data",False,300,None,None),
 ]),
 ("LOCALIZAÇÃO E RESPONSABILIDADE","O bloco é gravado junto com o aeroporto, sem digitação.",[
   ("aeroporto","Aeroporto de Lotação","drp",True,300,"colOpAero",None),
   ("base_operacional","Base / Local","txt",False,300,None,None),
   ("centro_custo","Centro de Custo","txt",True,300,None,None),
   ("setor_responsavel","Setor Responsável","txt",True,300,None,None),
   ("gestor_nome","Gestor Responsável","txt",False,300,None,None),
   ("gestor_email","E-mail do Gestor","txt",False,300,None,None),
 ]),
 ("SITUAÇÃO","Status é ciclo de vida patrimonial; situação é o dia a dia.",[
   ("status","Status do Ativo","drp",True,300,"colOpStatus",None),
   ("situacao_operacional","Situação Operacional","drp",True,300,"colOpSituacao",None),
   ("motivo_situacao","Motivo da Situação","multi",False,616,None,None),
 ]),
 ("AQUISIÇÃO E PROPRIEDADE","Fornecedor em texto livre nesta fase — a lista entra na Onda 3.",[
   ("tipo_propriedade","Tipo de Propriedade","drp",True,300,"colOpPropriedade",None),
   ("fornecedor_txt","Fornecedor / Locadora","txt",False,300,None,None),
   ("contrato_numero","Nº do Contrato","txt",False,300,None,None),
   ("data_aquisicao","Data de Aquisição","data",False,300,None,None),
   ("valor_aquisicao","Valor de Aquisição","num",False,300,None,None),
   ("data_fim_contrato","Fim do Contrato / Locação","data",False,300,None,None),
 ]),
 ("CONFORMIDADE","Define se os módulos 16, 17 e 18 vão se aplicar a este ativo.",[
   ("circula_lado_ar","Circula no Lado Ar","tgl",False,300,None,None),
   ("observacoes","Observações","multi",False,616,None,None),
 ]),
]

def pascal(n):
    especiais = {"n_serie":"NSerie","n_patrimonio":"NPatrimonio","capacidade_carga_kg":"CapacidadeCarga",
                 "qtd_passageiros":"QtdPassageiros","tipo_medidor":"TipoMedidor","tipo_ativo":"Tipo",
                 "identificacao_visual":"IdVisual","situacao_operacional":"Situacao","motivo_situacao":"Motivo",
                 "tipo_propriedade":"Propriedade","fornecedor_txt":"Fornecedor","circula_lado_ar":"LadoAr",
                 "aeroporto":"Aero","centro_custo":"CentroCusto","setor_responsavel":"Setor",
                 "gestor_nome":"GestorNome","gestor_email":"GestorEmail","base_operacional":"Base",
                 "medidor_km":"MedidorKm","medidor_horas":"MedidorHoras","medidor_data":"MedidorData",
                 "data_aquisicao":"DataAquisicao","valor_aquisicao":"ValorAquisicao",
                 "data_fim_contrato":"DataFimContrato","contrato_numero":"Contrato",
                 "ano_fabricacao":"AnoFab","ano_modelo":"AnoModelo","capacidade_tanque":"Tanque",
                 "categoria_uso":"Categoria","observacoes":"Observacoes"}
    if n in especiais: return especiais[n]
    return "".join(p.capitalize() for p in n.split("_"))

def ctrl(campo, tipo):
    pre = {"txt":"txt","num":"txt","multi":"txt","drp":"drp","data":"dtp","tgl":"tgl"}[tipo]
    return f"{pre}Frm{pascal(campo)}"

def leitura(campo, tipo):
    c = ctrl(campo, tipo)
    if tipo == "drp":  return f"{c}.Selected.Value"
    if tipo == "data": return f"{c}.SelectedDate"
    if tipo == "tgl":  return f"If({c}.Checked, 1, 0)"
    if tipo == "num":  return f"If(IsNumeric({c}.Value), Value({c}.Value), 0)"
    if campo == "placa": return f"Upper(Trim({c}.Value))"
    return f"Trim({c}.Value)"

L = []
def w(t=""): L.append(t)

w("Screens:")
w("  scrFrotaForm:")
w("    Properties:")
w("      OnVisible: |-")
w('        =UpdateContext({locErro: ""})')
w("    Children:")
w("      - cntFrmRaiz:")
w("          Control: GroupContainer@1.5.0")
w("          Variant: AutoLayout")
w("          Properties:")
w("            DropShadow: =DropShadow.None")
w("            Fill: =thmFundo")
w("            Height: =Parent.Height")
w("            LayoutDirection: =LayoutDirection.Vertical")
w("            LayoutGap: =0")
w("            LayoutMinHeight: =0")
w("            Width: =Parent.Width")
w("          Children:")
# ---------------- barra superior ----------------
w("            - cntFrmTopo:")
w("                Control: GroupContainer@1.5.0")
w("                Variant: AutoLayout")
w("                Properties:")
w("                  DropShadow: =DropShadow.None")
w("                  Fill: =thmPrimaria")
w("                  FillPortions: =0")
w("                  Height: =72")
w("                  LayoutAlignItems: =LayoutAlignItems.Center")
w("                  LayoutDirection: =LayoutDirection.Horizontal")
w("                  LayoutGap: =12")
w("                  LayoutJustifyContent: =LayoutJustifyContent.SpaceBetween")
w("                  LayoutMinHeight: =0")
w("                  PaddingLeft: =26")
w("                  PaddingRight: =26")
w("                  RadiusBottomLeft: =0")
w("                  RadiusBottomRight: =0")
w("                  RadiusTopLeft: =0")
w("                  RadiusTopRight: =0")
w("                Children:")
w("                  - htmFrmTitulo:")
w("                      Control: HtmlViewer@2.1.0")
w("                      Properties:")
w("                        AutoHeight: =true")
w("                        Color: =thmTextoBarra")
w("                        Fill: =thmPrimaria")
w("                        FillPortions: =1")
w("                        Font: =thmFonte")
w("                        HtmlText: |-")
w("""                          ="<div style='" & htmlFonte & "color:" & hxTextoBarra & ";'>" &""")
w("""                          "<div style='font-size:19px;font-weight:800;letter-spacing:.02em;line-height:1.1;'>" & If(varFormModo = "Editar", "EDITAR ATIVO", "NOVO ATIVO") & "</div>" &""")
w("""                          "<div style='font-size:11px;opacity:.75;margin-top:3px;'>" & If(varFormModo = "Editar", Coalesce(varFormRec.codigo_ativo, "sem código") & " &nbsp;&middot;&nbsp; registro " & varFormRec.ID, "O código FRT é gerado na gravação, a partir do ID do SharePoint") & "</div>" &""")
w("""                          "</div>" """.rstrip())
w("                        PaddingBottom: =0")
w("                        PaddingLeft: =0")
w("                        PaddingRight: =0")
w("                        PaddingTop: =0")
w("                        Size: =11")
w("                  - btnFrmCancelar:")
w("                      Control: Button@0.0.45")
w("                      Properties:")
w("                        Appearance: ='ButtonCanvas.Appearance'.Secondary")
w("                        BasePaletteColor: =thmSuperficie")
w("                        BorderRadius: =0")
w("                        FontColor: =thmTextoBarra")
w("                        FontSize: =12")
w("                        FontWeight: =FontWeight.Semibold")
w("                        Height: =40")
w("                        OnSelect: =Navigate(scrFrotaLista, ScreenTransition.Fade)")
w('                        Text: ="CANCELAR"')
w("                        Width: =130")
w("                  - btnFrmSalvar:")
w("                      Control: Button@0.0.45")
w("                      Properties:")
w("                        Appearance: ='ButtonCanvas.Appearance'.Primary")
w("                        BasePaletteColor: =thmAcao")
w("                        BorderRadius: =0")
w("                        DisplayMode: =If(varPerfilNivel >= 3, DisplayMode.Edit, DisplayMode.Disabled)")
w("                        FontColor: =thmTextoBarra")
w("                        FontSize: =12")
w("                        FontWeight: =FontWeight.Semibold")
w("                        Height: =40")
w('                        Icon: ="Save"')
w("                        IconStyle: ='ButtonCanvas.IconStyle'.Filled")
w("                        OnSelect: |-")
i = "                          "
w(i + "=If(")
w(i + "    !IsBlank(varOcupadoDesde) && DateDiff(varOcupadoDesde, Now(), TimeUnit.Seconds) < 20,")
w(i + '    Notify("Aguarde: a gravação anterior ainda está em andamento.", NotificationType.Warning, 3000),')
w(i + "    UpdateContext(")
w(i + "        {")
w(i + "            locErro: If(")
w(i + '                IsBlank(drpFrmTipo.Selected.Value), "Escolha o tipo de ativo.",')
w(i + '                IsBlank(drpFrmCategoria.Selected.Value), "Escolha a categoria de uso.",')
w(i + '                IsBlank(Trim(txtFrmMarca.Value)), "Informe a marca.",')
w(i + '                IsBlank(Trim(txtFrmModelo.Value)), "Informe o modelo.",')
w(i + '                !IsNumeric(txtFrmAnoFab.Value) Or Value(txtFrmAnoFab.Value) < 1950 Or Value(txtFrmAnoFab.Value) > Year(Today()) + 1,')
w(i + '                    "Ano de fabricação inválido — use o ano com 4 dígitos.",')
w(i + '                IsBlank(drpFrmCombustivel.Selected.Value), "Escolha o combustível.",')
w(i + '                IsBlank(drpFrmTipoMedidor.Selected.Value), "Escolha o tipo de medidor.",')
w(i + '                IsBlank(drpFrmAero.Selected.Value), "Escolha o aeroporto de lotação.",')
w(i + '                IsBlank(Trim(txtFrmCentroCusto.Value)), "Informe o centro de custo.",')
w(i + '                IsBlank(Trim(txtFrmSetor.Value)), "Informe o setor responsável.",')
w(i + '                IsBlank(drpFrmStatus.Selected.Value), "Escolha o status do ativo.",')
w(i + '                IsBlank(drpFrmSituacao.Selected.Value), "Escolha a situação operacional.",')
w(i + '                IsBlank(drpFrmPropriedade.Selected.Value), "Escolha o tipo de propriedade.",')
w(i + "                LookUp(colTipoAtivo, Tipo = drpFrmTipo.Selected.Value).ExigePlaca And IsBlank(Trim(txtFrmPlaca.Value)),")
w(i + '                    "Este tipo de ativo exige placa.",')
w(i + '                !IsBlank(Trim(txtFrmPlaca.Value)) And !IsMatch(Upper(Trim(txtFrmPlaca.Value)), "([A-Z]{3}[0-9]{4})|([A-Z]{3}[0-9][A-Z][0-9]{2})"),')
w(i + '                    "Placa inválida — use o formato AAA0000 ou AAA0A00, sem hífen.",')
w(i + '                !IsBlank(Trim(txtFrmGestorEmail.Value)) And !IsMatch(Trim(txtFrmGestorEmail.Value), Match.Email),')
w(i + '                    "E-mail do gestor inválido.",')
w(i + '                drpFrmStatus.Selected.Value <> "Ativo" And IsBlank(Trim(txtFrmMotivo.Value)),')
w(i + '                    "Ativo fora do status Ativo exige o motivo da situação.",')
w(i + '                ""')
w(i + "            )")
w(i + "        }")
w(i + "    );")
w(i + "    If(")
w(i + "        !IsBlank(locErro),")
w(i + "        Notify(locErro, NotificationType.Error, 4000),")
w(i + "        Set(varOcupadoDesde, Now());")
w(i + "        Set(")
w(i + "            varAtivoGravado,")
w(i + "            Patch(")
w(i + "                'tb_ativosFrota',")
w(i + '                If(varFormModo = "Editar", varFormRec, Defaults(\'tb_ativosFrota\')),')
w(i + "                {")
linhas = []
for _sec, _sub, campos in CAMPOS:
    for (nome, rot, tipo, obrig, larg, itens, vis) in campos:
        linhas.append(f"{nome}: {leitura(nome, tipo)}")
linhas.append("bloco: LookUp(colAeros, IATA = drpFrmAero.Selected.Value).Bloco")
linhas.append('medidor_origem: If(varFormModo = "Editar" And If(IsNumeric(txtFrmMedidorKm.Value), Value(txtFrmMedidorKm.Value), 0) = Coalesce(varFormRec.medidor_km, 0) And If(IsNumeric(txtFrmMedidorHoras.Value), Value(txtFrmMedidorHoras.Value), 0) = Coalesce(varFormRec.medidor_horas, 0), Coalesce(varFormRec.medidor_origem, "Cadastro"), "Cadastro")')
linhas.append('data_situacao: If(varFormModo = "Editar" And drpFrmStatus.Selected.Value = varFormRec.status And drpFrmSituacao.Selected.Value = varFormRec.situacao_operacional, varFormRec.data_situacao, Now())')
linhas.append("ativo: 1")
# conforme_lado_ar é do módulo 18: o app do módulo 1 não escreve nem lê
for k, ln in enumerate(linhas):
    w(i + "                    " + ln + ("," if k < len(linhas) - 1 else ""))
w(i + "                }")
w(i + "            )")
w(i + "        );")
w(i + "        If(")
w(i + "            IsBlank(varAtivoGravado.ID),")
w(i + '            Notify("Falha ao gravar. Nenhum registro foi salvo.", NotificationType.Error, 5000);')
w(i + "            Set(varOcupadoDesde, Blank()),")
w(i + "            If(")
w(i + "                IsBlank(varAtivoGravado.codigo_ativo),")
w(i + "                Patch(")
w(i + "                    'tb_ativosFrota',")
w(i + "                    varAtivoGravado,")
w(i + '                    {codigo_ativo: "FRT-" & Text(varAtivoGravado.ID, "00000")}')
w(i + "                )")
w(i + "            );")
w(i + "            RemoveIf(colFrota, ID = varAtivoGravado.ID);")
w(i + "            Collect(")
w(i + "                colFrota,")
w(i + "                ForAll(")
w(i + "                    Filter(")
w(i + "                        'tb_ativosFrota',")
w(i + "                        ID = varAtivoGravado.ID")
w(i + "                    ) As _r,")
w(i + "                    {")
for k, c in enumerate(COLS):
    w(i + f"                        {c}: _r.{c}" + ("," if k < len(COLS) - 1 else ""))
w(i + "                    }")
w(i + "                )")
w(i + "            );")
w(i + "            Notify(")
w(i + '                If(varFormModo = "Editar", "Ativo atualizado: ", "Ativo cadastrado: ") & LookUp(colFrota, ID = varAtivoGravado.ID).codigo_ativo,')
w(i + "                NotificationType.Success,")
w(i + "                3000")
w(i + "            );")
w(i + "            Set(varOcupadoDesde, Blank());")
w(i + "            // a lista abre no recorte onde o ativo salvo aparece")
w(i + "            Set(varFiltroAero, drpFrmAero.Selected.Value);")
w(i + '            Set(varFiltroTipo, "Todos");')
w(i + '            Set(varFiltroSituacao, "Todos");')
w(i + '            Set(varFiltroStatus, "Ativo");')
w(i + "            Navigate(scrFrotaLista, ScreenTransition.Fade)")
w(i + "        )")
w(i + "    )")
w(i + ")")
w('                        Text: =If(varFormModo = "Editar", "SALVAR ALTERAÇÕES", "CADASTRAR ATIVO")')
w("                        Width: =230")
# ---------------- corpo ----------------
w("            - cntFrmCorpo:")
w("                Control: GroupContainer@1.5.0")
w("                Variant: AutoLayout")
w("                Properties:")
w("                  DropShadow: =DropShadow.None")
w("                  Fill: =thmFundo")
w("                  FillPortions: =1")
w("                  LayoutAlignItems: =LayoutAlignItems.Stretch")
w("                  LayoutDirection: =LayoutDirection.Vertical")
w("                  LayoutGap: =26")
w("                  LayoutMinHeight: =0")
w("                  LayoutOverflowY: =LayoutOverflow.Scroll")
w("                  PaddingBottom: =26")
w("                  PaddingLeft: =26")
w("                  PaddingRight: =26")
w("                  PaddingTop: =26")
w("                  RadiusBottomLeft: =0")
w("                  RadiusBottomRight: =0")
w("                  RadiusTopLeft: =0")
w("                  RadiusTopRight: =0")
w("                Children:")
w("                  - htmFrmErro:")
w("                      Control: HtmlViewer@2.1.0")
w("                      Properties:")
w("                        AlignInContainer: =AlignInContainer.Stretch")
w("                        AutoHeight: =true")
w("                        Fill: =thmFundo")
w("                        FillPortions: =0")
w("                        Font: =thmFonte")
w("                        HtmlText: |-")
w("""                          ="<div style='" & htmlFonte & "background:" & hxVermelhoSuave & ";border:1px solid " & hxVermelho & ";border-left:4px solid " & hxVermelho & ";padding:13px 16px;'>" &""")
w("""                          "<div style='font-size:10px;font-weight:800;letter-spacing:.14em;color:" & hxVermelho & ";'>CORRIJA PARA CONTINUAR</div>" &""")
w("""                          "<div style='font-size:13px;color:" & hxTexto & ";margin-top:5px;'>" & locErro & "</div></div>" """.rstrip())
w("                        PaddingBottom: =0")
w("                        PaddingLeft: =0")
w("                        PaddingRight: =0")
w("                        PaddingTop: =0")
w("                        Size: =11")
w("                        Visible: =!IsBlank(locErro)")

ALT_CAMPO = 80      # rótulo 20 + gap 6 + entrada 42 + folga
ALT_MULTI = 140
ALT_CABEC = 46
POR_LINHA = 3

def linhas_da_secao(campos):
    """Agrupa em linhas de 3; campo largo ocupa a linha inteira."""
    linhas, atual = [], []
    for c in campos:
        if c[4] >= 600:
            if atual: linhas.append(atual); atual = []
            linhas.append([c])
        else:
            atual.append(c)
            if len(atual) == POR_LINHA: linhas.append(atual); atual = []
    if atual: linhas.append(atual)
    return linhas

for idx, (sec, sub, campos) in enumerate(CAMPOS):
    n = idx + 1
    linhas_sec = linhas_da_secao(campos)
    alt_linhas = [ALT_MULTI if any(c[2] == "multi" for c in ln) else ALT_CAMPO for ln in linhas_sec]
    alt_secao = 18 + ALT_CABEC + 16 * len(linhas_sec) + sum(alt_linhas) + 20
    w(f"                  - cntFrmSec{n}:")
    w("                      Control: GroupContainer@1.5.0")
    w("                      Variant: AutoLayout")
    w("                      Properties:")
    w("                        AlignInContainer: =AlignInContainer.Stretch")
    w("                        BorderColor: =thmBorda")
    w("                        BorderStyle: =BorderStyle.Solid")
    w("                        BorderThickness: =1")
    w("                        DropShadow: =DropShadow.None")
    w("                        Fill: =thmSuperficie")
    w("                        FillPortions: =0")
    w(f"                        Height: ={alt_secao}")
    w("                        LayoutAlignItems: =LayoutAlignItems.Stretch")
    w("                        LayoutDirection: =LayoutDirection.Vertical")
    w("                        LayoutGap: =16")
    w("                        LayoutMinHeight: =0")
    w("                        PaddingBottom: =20")
    w("                        PaddingLeft: =20")
    w("                        PaddingRight: =20")
    w("                        PaddingTop: =18")
    w("                        RadiusBottomLeft: =0")
    w("                        RadiusBottomRight: =0")
    w("                        RadiusTopLeft: =0")
    w("                        RadiusTopRight: =0")
    w("                      Children:")
    w(f"                        - htmFrmSec{n}:")
    w("                            Control: HtmlViewer@2.1.0")
    w("                            Properties:")
    w("                              AlignInContainer: =AlignInContainer.Stretch")
    w("                              AutoHeight: =false")
    w("                              Fill: =thmSuperficie")
    w("                              FillPortions: =0")
    w("                              Font: =thmFonte")
    w(f"                              Height: ={ALT_CABEC}")
    w("                              HtmlText: |-")
    w(f"""                                ="<div style='" & htmlFonte & "border-bottom:1px solid " & hxBorda & ";padding-bottom:8px;'>" &""")
    w(f"""                                "<div style='font-size:12px;font-weight:800;letter-spacing:.14em;color:" & hxPrimaria & ";'>{sec}</div>" &""")
    w(f"""                                "<div style='font-size:11px;color:" & hxTextoFraco & ";margin-top:2px;'>{sub}</div></div>" """.rstrip())
    w("                              PaddingBottom: =0")
    w("                              PaddingLeft: =0")
    w("                              PaddingRight: =0")
    w("                              PaddingTop: =0")
    w("                              Size: =11")
    for li, (ln, alt) in enumerate(zip(linhas_sec, alt_linhas), 1):
        w(f"                        - cntFrmLin{n}_{li}:")
        w("                            Control: GroupContainer@1.5.0")
        w("                            Variant: AutoLayout")
        w("                            Properties:")
        w("                              AlignInContainer: =AlignInContainer.Stretch")
        w("                              DropShadow: =DropShadow.None")
        w("                              Fill: =thmSuperficie")
        w("                              FillPortions: =0")
        w(f"                              Height: ={alt}")
        w("                              LayoutAlignItems: =LayoutAlignItems.Stretch")
        w("                              LayoutDirection: =LayoutDirection.Horizontal")
        w("                              LayoutGap: =16")
        w("                              LayoutMinHeight: =0")
        w("                              RadiusBottomLeft: =0")
        w("                              RadiusBottomRight: =0")
        w("                              RadiusTopLeft: =0")
        w("                              RadiusTopRight: =0")
        w("                            Children:")
        for (nome, rot, tipo, obrig, larg, itens, vis) in ln:
            P = pascal(nome)
            w(f"                              - cntFrm{P}:")
            w("                                  Control: GroupContainer@1.5.0")
            w("                                  Variant: AutoLayout")
            w("                                  Properties:")
            w("                                    AlignInContainer: =AlignInContainer.Stretch")
            w("                                    DropShadow: =DropShadow.None")
            w("                                    Fill: =thmSuperficie")
            w("                                    FillPortions: =1")
            w(f"                                    Height: ={alt}")
            w("                                    LayoutAlignItems: =LayoutAlignItems.Stretch")
            w("                                    LayoutDirection: =LayoutDirection.Vertical")
            w("                                    LayoutGap: =6")
            w("                                    LayoutMinHeight: =0")
            w("                                    LayoutMinWidth: =0")
            w("                                    RadiusBottomLeft: =0")
            w("                                    RadiusBottomRight: =0")
            w("                                    RadiusTopLeft: =0")
            w("                                    RadiusTopRight: =0")
            if vis:
                w(f"                                    Visible: {vis}")
            w("                                  Children:")
            w(f"                                    - lblFrm{P}:")
            w("                                        Control: Text@0.0.51")
            w("                                        Properties:")
            w("                                          AlignInContainer: =AlignInContainer.Stretch")
            w("                                          FillPortions: =0")
            w("                                          FontColor: =thmTexto")
            w("                                          Height: =20")
            w("                                          LayoutMinWidth: =0")
            w("                                          Size: =11")
            if nome == "placa":
                w('                                          Text: =If(LookUp(colTipoAtivo, Tipo = drpFrmTipo.Selected.Value).ExigePlaca, "Placa *", "Placa")')
            else:
                w(f'                                          Text: ="{rot}{" *" if obrig else ""}"')
            w("                                          Weight: =FontWeight.Semibold")
            c = ctrl(nome, tipo)
            w(f"                                    - {c}:")
            if tipo in ("txt", "num", "multi"):
                w("                                        Control: TextInput@0.0.54")
                w("                                        Properties:")
                w("                                          AlignInContainer: =AlignInContainer.Stretch")
                w("                                          FillPortions: =1")
                w("                                          FontSize: =12")
                w("                                          LayoutMinWidth: =0")
                if tipo == "multi":
                    w("                                          Mode: ='TextInputCanvas.Mode'.Multiline")
                else:
                    w("                                          Mode: ='TextInputCanvas.Mode'.SingleLine")
                w(f'                                          Placeholder: ="{rot}"')
                if tipo == "num":
                    w(f"                                          Value: =If(IsBlank(varFormRec.{nome}), \"\", Text(varFormRec.{nome}))")
                else:
                    w(f"                                          Value: =varFormRec.{nome}")
            elif tipo == "drp":
                w("                                        Control: DropDown@0.0.45")
                w("                                        Properties:")
                if nome == "tipo_medidor":
                    w("                                          DefaultSelectedItems: |-")
                    w("                                            =[")
                    w("                                                Coalesce(")
                    w("                                                    varFormRec.tipo_medidor,")
                    w("                                                    LookUp(colTipoAtivo, Tipo = drpFrmTipo.Selected.Value).MedidorPadrao,")
                    w('                                                    ""')
                    w("                                                )")
                    w("                                            ]")
                else:
                    w(f'                                          DefaultSelectedItems: =[Coalesce(varFormRec.{nome}, "")]')
                w("                                          Height: =42")
                w(f"                                          Items: ={itens}")
                w("                                          Width: =Parent.Width")
            elif tipo == "data":
                w("                                        Control: DatePicker@0.0.46")
                w("                                        Properties:")
                w("                                          Format: =DateTimeFormat.ShortDate")
                w(f"                                          SelectedDate: =varFormRec.{nome}")
                w("                                          Width: =Parent.Width")
            elif tipo == "tgl":
                w("                                        Control: Toggle@1.1.5")
                w("                                        Properties:")
                w("                                          BasePaletteColor: =thmPrimaria")
                w(f"                                          Checked: =varFormRec.{nome} = 1")
                w("                                          Height: =38")
                w('                                          Label: =If(tglFrmLadoAr.Checked, "Sim, circula no lado ar", "Não circula")')
                w("                                          LabelPosition: ='Toggle.LabelPosition'.Before")
                w("                                          Width: =Parent.Width")

open('/workspaces/codespaces-blank/Frotas/scrFrotaForm.pa.yaml', 'w', encoding='utf-8').write("\n".join(L) + "\n")
print("gerado:", len(L), "linhas")
