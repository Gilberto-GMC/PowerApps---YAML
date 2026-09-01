# -*- coding: utf-8 -*-
"""Configuração dos módulos consolidados do AirportNow Safety & Fauna."""

# Geometria do corpo do formulário, medida do próprio export:
#   'fluxo'  -> container AutoLayout que empilhava blocos de ~500px numa coluna
#               só, deixando o resto da tela vazio. Vira Horizontal + wrap.
#   'centro' -> container ManualLayout de largura fixa 1138 encostado à esquerda.
#               Vira responsivo e centralizado, com largura = conteúdo real medido
#               (JetBlast tinha 1214px de conteúdo dentro de 1138: estava cortando).
LAYOUT_FORM = {
 "ColVei":   [("Container4", "fluxo", 0)],
 "DerFlu":   [("Container3_22", "centro", 1040)],
 "ExcPista": [("Container3_38", "centro", 1120)],
 "IncPista": [("Container3_26", "centro", 1120)],
 "IntExt":   [("Container3_34", "centro", 1160)],
 "JetBlast": [("Container3_50", "centro", 1260)],
 "OcoSolo":  [("Container3_18", "centro", 1140), ("Container35", "centro", 780)],
}

MODULOS = [
 dict(key="ColVei", nova="ScreenModColisaoVeiculos", titulo="Colisão de Veículos",
      lista="ScreenColisaoVeiculos", forms="ScreenColisaoVeiculosForms", det="ScreenColisaoVeiculosDetalhes",
      tabela="'14.4-tbl_ColVeiculos'", pfx="colVei", proto="COL-VEIC",
      gal="GalleryColVeiRegistros", varId="var_colVeiId",
      fBloco="cmbHomeBloco_1", fAero="cmbHomeAeroporto_1", fIni="dtpHomeDtfInicio_1",
      fFim="dtpHomeDtfTermino_1", fStatus="cmbHomeStatus_1", fBusca="txtBuscar1_1",
      extraFiltros=[], contForm="ScreenContainerForms_2"),
 dict(key="DerFlu", nova="ScreenModDerramamento", titulo="Derramamento de Fluidos",
      lista="ScreenDerramamentoFluido", forms="ScreenDerramamentoForms", det="ScreenDerramamentoDetalhes",
      tabela="'14.2-tbl_DerramamentoDeFluidos'", pfx="derFlu", proto="DER-FLUI",
      gal="GalleryDerFlu", varId="varDerFluId",
      fBloco="cmbDerFluBloco", fAero="cmbDerFluAeroporto", fIni="dtpDerFluDtfInicio",
      fFim="dtpDerFluDtfTermino", fStatus="cmbStatus_2", fBusca="txtDerFluBuscar",
      extraFiltros=[], contForm=None),
 dict(key="ExcPista", nova="ScreenModExcursaoPista", titulo="Excursão de Pista",
      lista="ScreenExcursaoPista", forms="ScreenExcursaoPistaForms", det="ScreenExcursaoPistaDetalhes",
      tabela="'14.6-tbl_ExcPista'", pfx="excPista", proto="EXC-PIST",
      gal="GalleryExcPistaRegistros", varId="var_excPistaId",
      fBloco="cmbExcPistaBloco", fAero="cmbExcPistaAeroporto", fIni="dtpExcPistaDtfInicio",
      fFim="dtpExcPistaDtfTermino", fStatus="cmbStatus_4", fBusca="txtExcPistaBuscar",
      extraFiltros=[], contForm=None),
 dict(key="IncPista", nova="ScreenModIncursaoPista", titulo="Incursão de Pista",
      lista="ScreenIncursaoPista", forms="ScreenIncursaoPistaForms", det="ScreenIncursaoPistaDetalhes",
      tabela="'14.3-tbl_IncPista'", pfx="incPista", proto="INC-PIST",
      gal="GalleryIncPistaRegistros", varId="var_incPistaId",
      fBloco="cmbIncPistaBloco", fAero="cmbIncPistaAeroporto", fIni="dtpIncPistaDtfInicio",
      fFim="dtpIncPistaDtfTermino", fStatus="cmbStatus_5", fBusca="txtIncPistaBuscar",
      extraFiltros=[], contForm=None),
 dict(key="IntExt", nova="ScreenModInterferenciaExterna", titulo="Interferência Externa",
      lista="ScreenInterferenciaExterna", forms="ScreenInterferenciaExternaForms", det="ScreenInterferenciaExternaDetalhes",
      tabela="'14.5-tbl_IntExterna'", pfx="intExt", proto="INT-EXT",
      gal="GalleryIntExtRegistros", varId="var_intExtId",
      fBloco="cmbIntExtBloco", fAero="cmbIntExtAeroporto", fIni="dtpIntExtDtfInicio",
      fFim="dtpIntExtDtfTermino", fStatus="cmbStatus_7", fBusca="txtIntExtBuscar",
      extraFiltros=[("intExt_tipo", "cmbTipo")], contForm=None),
 dict(key="JetBlast", nova="ScreenModJetBlast", titulo="Jet Blast",
      lista="ScreenJetBlast", forms="ScreenJetBlastForms", det="ScreenJetBlastDetalhes",
      tabela="'14.8-tbl_JetBlast'", pfx="jetBlast", proto="JET-BLAS",
      gal="GalleryJetBlastRegistros", varId="var_jetBlastId",
      fBloco="cmbJetBlastBloco", fAero="cmbJetBlastAeroporto", fIni="dtpJetBlastDtfInicio",
      fFim="dtpJetBlastDtfTermino", fStatus="cmbStatus_8", fBusca="txtJetBlastBuscar",
      extraFiltros=[], contForm=None),
 dict(key="OcoSolo", nova="ScreenModOcorrenciaSolo", titulo="Ocorrência de Solo",
      lista="ScreenOcorrenciaSolo", forms="ScreenOcorrenciaSoloForms", det="ScreenOcorrenciaSoloDetalhes",
      tabela="'16.1-tbl_OcoSolo'", pfx="ocoSolo", proto="OCO-SOLO",
      gal="GalleryOcoSoloListar", varId="varOcoSoloId",
      fBloco="cmbOcoSoloBloco", fAero="cmbOcoSoloAeroporto", fIni="dtpOcoSoloDtfInicio",
      fFim="dtpOcoSoloDtfTermino", fStatus="cmbStatus_9", fBusca="txtOcoSoloBuscar",
      extraFiltros=[], contForm=None),
]
