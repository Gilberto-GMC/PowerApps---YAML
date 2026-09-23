# -*- coding: utf-8 -*-
"""Habilita o botão "Editar" (hoje travado e sem ação em todos os 7 módulos).

Levantamento em 2026-09-22 (ver mensagens da sessão): FOD/CSO/Vistoria já editam
de verdade via Form nativo (EditForm/SubmitForm) — não mexemos nessas. Os 7
módulos gravam campo a campo com Patch() direto, sem Form nativo, então "editar"
precisa ser construído: carregar o registro escolhido, pré-preencher os campos,
e no Salvar decidir Patch(tab, registro_existente, ...) em vez de sempre
Patch(tab, Defaults(tab), ...).

Cada módulo tem uma mistura de campos "simples" (um controle, uma coluna) e
campos "compostos/complexos" (dois controles combinados, campo condicionado a
outro, checkbox virando texto, sub-registro codificado como string). Decisão do
usuário em 2026-09-22: campos complexos NÃO entram nesta rodada — ficam do jeito
que estão, só visíveis, não editáveis. O campo `EDICAO` abaixo é a lista exata
do que cada módulo libera, extraída automaticamente do próprio Patch() de
gravação (script de extração não faz parte da entrega, só do processo).

Filhos (envolvidos/fotos/itens atingidos): todo módulo tem pelo menos uma
coleção de FOTOS, sempre no mesmo formato simples ({id, img}) — essa entra
editável (adicionar/remover) nos 7. Os filhos "envolvidos"/"itens atingidos"
só entram nos módulos onde o formato da coleção é simples (Colisão de Veículos,
Jet Blast); o de Incursão de Pista funde 3 sub-blocos (aeronave/veículo/pessoa)
num texto só — fica só leitura, mesmo critério dos campos complexos do pai.

Mecanismo de conciliação ao salvar (evita duplicar/perder registro filho):
cada linha da coleção carrega um `dbId` — Blank() se foi adicionada nesta
edição, ou o ID real do SharePoint se já existia. Ao salvar: dbId em branco ->
Patch(tab, Defaults(tab), ...) cria; dbId preenchido -> Patch(tab,
LookUp(tab, ID=dbId), ...) atualiza. Uma cópia da coleção como estava ao abrir
a edição (`<colecao>_orig`) permite achar o que foi removido e apagar do
SharePoint. Mesma ideia teria que valer pra qualquer filho editável futuro.
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from pautil import ind, block_end, find_ctrl, set_prop, prop_block
from fx import find_call, split_args, indent_lines

# ─────────────────────────────────────────────────────────────────────────────
# Metadado por módulo — extraído do Patch() de gravação de cada um.
# campos: (coluna, controle, propriedade) — 1 controle, 1 coluna, sem "&"/If()/LookUp().
# hora: (coluna, controle_hora, controle_minuto) — "H:M", padrão repetido nos 7.
# extras: lista de (coluna, [controles...], junção) para compostos conhecidos e
#         seguros de reverter (hoje só o mapaGrade "X-Y" da Colisão de Veículos).
# filhos: lista de dicts — colecao (nome da coleção), tabela, fk (coluna que
#         aponta pro pai), campos (coluna da tabela -> campo da coleção),
#         somente_leitura (não entra na conciliação, só carrega pra mostrar).
# ─────────────────────────────────────────────────────────────────────────────
EDICAO = {
    'ColVei': dict(
        campos=[
            ('colVei_local', 'TxtColVeiLocal', 'Text'),
            ('colVei_tipoColisao', 'cmbColVeiTipColisao', 'Selected.Value'),
            ('colVei_descOcorrencia', 'TxtColVeiDescOcorrencia', 'Text'),
            ('colVei_danos', 'TxtColVeiDanos', 'Text'),
        ],
        data=('colVei_data', 'dtpColVeiDataCadastro'),
        hora=('colVei_hora', 'cmbColVeiHoraCadastro', 'cmbColVeiMinuCadastro'),
        extras=[('colVei_mapaGrade', ['ComboBoxMG1', 'ComboBoxMG2'], '-')],
        filhos=[
            dict(colecao='col_colVeiEnvolvidos', tabela="'14.4-tbl_ColVeiculosEnvolvidos'",
                 fk='colVeiEnv_idOcorrencia',
                 campos={'nome': 'colVeiEnv_nome', 'colete': 'colVeiEnv_colete',
                         'empresa': 'colVeiEnv_empresa', 'codVeiculo': 'colVeiEnv_codVeiculo',
                         'empresaProp': 'colVeiEnv_empresaProp', 'cnhCompativel': 'colVeiEnv_cnhComp',
                         'boaCondicao': 'colVeiEnv_boaCondicoes'}),
            dict(colecao='col_colVeiGalleryImg', tabela="'14.4-tbl_ColVeiculosImg'",
                 fk='colVeiImg_idOcorrencia', campos={'img': 'colVeiImg_imagem'}),
        ],
    ),
    'DerFlu': dict(
        campos=[
            ('derFlu_fluido', 'dropDerFluFluido', 'Selected.Value'),
            ('derFlu_tipo', 'dropDerFluOrigemVazamento', 'Selected.Value'),
            ('derFlu_matricula', 'TxtDerFluMatAero', 'Text'),
            ('derFlu_modelo', 'TxtDerFluModAero', 'Text'),
            ('derFlu_ciaAerea', 'dropDerFluCiaAerea', 'Selected.Value'),
            ('derFlu_prefixoNome', 'TxtDerFluPrefixoNome', 'Text'),
            ('derFlu_origemVoo', 'TxtDerFluOrigem', 'Text'),
            ('derFlu_numVooOrigem', 'TxtDerFluOrigemNumVoo', 'Text'),
            ('derFlu_destinoVoo', 'TxtDerFluDestino', 'Text'),
            ('derFlu_numVooDestino', 'TxtDerFluDestinoNumVoo', 'Text'),
            ('derFlu_relato', 'TxtDerFluRelatoFiscal', 'Text'),
            ('derFlu_causaDanos', 'TxtDerFluCausaDano', 'Text'),
            ('derFlu_medIsolamento', 'TxtDerFluMedIsolamento', 'Text'),
            ('derFlu_equipa', 'TxtDerFluDescEquipa', 'Text'),
            ('derFlu_empresa', 'TxtDerFluEmpresa', 'Text'),
            ('derFlu_atendVoo', 'cmbDerFluAtendVoo', 'Selected.Value'),
            ('derFlu_condutor', 'TxtDerFluCondNome', 'Text'),
            ('derFlu_matCondutor', 'TxtDerFluCondMat', 'Text'),
            ('derFlu_relCondutor', 'TxtDerFluRelatoCondutor', 'Text'),
        ],
        data=('derFlu_data', 'dtpDerFluDataCadastro'),
        hora=('derFlu_hora', 'cmbDerFluHoraCadastro', 'cmbDerFluMinuCadastro'),
        extras=[],
        filhos=[
            dict(colecao='col_derFluImg', tabela="'14.2-tbl_DerFluidosImg'",
                 fk='derFluFK_id', campos={'img': 'derFluImg_imagem'}),
        ],
    ),
    'ExcPista': dict(
        campos=[
            ('excPista_local', 'TxtExcPistaLocal', 'Text'),
            ('excPista_condPista', 'cmbExcPistaCondPista', 'Selected.Value'),
            ('excPista_condMeteo', 'cmbExcPistaCondMeteor', 'Selected.Value'),
            ('excPista_teto', 'TxtExcPistaTeto', 'Text'),
            ('excPista_visibilidade', 'TxtExcPistaVisibi', 'Text'),
            ('excPista_matricula', 'TxtExcPistaMatAero', 'Text'),
            ('excPista_tipOperacao', 'cmbExcPistaTipOperacao', 'Selected.Value'),
            ('excPista_pontoSaida', 'TxtExcPistaPontoSaida', 'Text'),
            ('excPista_distPercorrida', 'TxtExcPistaDistPercorrida', 'Text'),
            ('excPista_posFinalAero', 'TxtExcPistaPosFinalAero', 'Text'),
            ('excPista_evacEmergencia', 'cmbExcPistaEvacEmergencia', 'Selected.Value'),
            ('excPista_danosAero', 'TxtExcPistaDanosAero', 'Text'),
            ('excPista_aeroImpraticavel', 'cmbExcPistaAeroImpraticavel', 'Selected.Value'),
            ('excPista_descOcorrencia', 'TxtExcPistaDescOcorrencia', 'Text'),
        ],
        data=('excPista_data', 'dtpExcPistaDataCadastro'),
        hora=('excPista_hora', 'cmbExcPistaHoraCadastro', 'cmbExcPistaMinuCadastro'),
        extras=[],
        filhos=[
            dict(colecao='col_excPistaImg', tabela="'14.6-tbl_ExcPistaImg'",
                 fk='excPistaImg_idOcorrencia', campos={'img': 'excPistaImg_imagem'}),
        ],
    ),
    'IncPista': dict(
        campos=[
            ('incPista_localOcorrencia', 'TxtIncPistaLocal', 'Text'),
            ('incPista_descOcorrencia', 'TxtIncPistaDescOcorrencia', 'Text'),
            ('incPista_condPista', 'cmbIncPistaCondPista', 'Selected.Value'),
            ('incPista_condMeteor', 'cmbIncPistaCondMeteor', 'Selected.Value'),
            ('incPista_condTeto', 'TxtIncPistaTeto', 'Text'),
            ('incPista_condVisib', 'TxtIncPistaVisibi', 'Text'),
            ('incPista_distVertical', 'TxtIncPistaDistVertical', 'Text'),
            ('incPista_distHorizontal', 'TxtIncPistaDistHorizontal', 'Text'),
            ('Agravante', 'cmbIncPistaAgravante', 'Selected.Value'),
        ],
        data=('incPista_data', 'dtpIncPistaDataCadastro'),
        hora=('incPista_hora', 'cmbIncPistaHoraCadastro', 'cmbIncPistaMinuCadastro'),
        extras=[],
        filhos=[
            # envolvidos funde aeronave/veículo/pessoa em texto só (ex.: incPistaEnv_acaoEvasiva
            # = aer_acaoEvasiva & vei_acaoEvasiva & pes_acaoEvasiva) — decifrar de volta é a
            # mesma classe de risco dos campos compostos do pai. Só leitura por enquanto.
            dict(colecao='col_incPistaEnvolvidos', tabela="'14.3-tbl_IncPistaEnvolvidos'",
                 fk='incPistaEnv_idOcorrencia', campos={}, somente_leitura=True),
            dict(colecao='col_incPistaImg', tabela="'14.3-tbl_IncPistaImg'",
                 fk='incPistaImg_idOcorrencia', campos={'img': 'incPistaImg_imagem'}),
        ],
    ),
    'IntExt': dict(
        # só "Dados gerais" — os blocos Balão/Laser são condicionados por intExt_tipo
        # (uma variável, não um controle: não dá pra pré-selecionar de forma confiável
        # qual bloco mostrar) e student ficariam com campo editável de um bloco que não
        # é o exibido. Mesmo critério dos módulos "complexos".
        campos=[
            ('intExt_descOcorrencia', 'TxtIntExtDescOcorrencia', 'Text'),
            ('intExt_local', 'TxtIntExtLocal', 'Text'),
            ('intExt_mapaGrade', 'TxtIntExtMapaGrade', 'Text'),
            ('intExt_fechaAero', 'cmbIntExtFechaAer', 'Selected.Value'),
            ('intExt_impVoo', 'cmbIntExtImpVoo', 'Selected.Value'),
            ('intExt_impVooDesc', 'TxtIntExtImpVooDesc', 'Text'),
            ('intExt_danoAero', 'cmbIntExtDanoAeronave', 'Selected.Value'),
            ('intExt_danoAeroDesc', 'TxtIntExtDanoAeronaveDesc', 'Text'),
            ('intExt_encInspecao', 'cmbIntExtEncInspecao', 'Selected.Value'),
            ('intExt_acionSeguranca', 'cmbIntExtAcionaSegur', 'Selected.Value'),
            ('intExt_reportadoPor', 'cmbIntExtReportado', 'Selected.Value'),
            ('intExt_reportadoPorDesc', 'TxtIntExtReportadoOutros', 'Text'),
            ('intExt_recAparelho', 'cmbIntExtRecAparelho', 'Selected.Value'),
        ],
        data=('intExt_data', 'dtpIntExtDataCadastro'),
        hora=('intExt_hora', 'cmbIntExtHoraCadastro', 'cmbIntExtMinuCadastro'),
        extras=[],
        filhos=[
            dict(colecao='col_intExtGalleryImg', tabela="'14.5-tbl_IntExternaImg'",
                 fk='intExtImg_idOcorrencia', campos={'img': 'intExtImg_imagem'}),
        ],
    ),
    'JetBlast': dict(
        campos=[
            ('jetBlast_opeAereo', 'dropJetBlastOpeAereo', 'Selected.Value'),
            ('jetBlast_opePrefixo', 'TxtJetBlastPrefixoNome', 'Text'),
            ('jetBlast_voo', 'TxtJetBlastVoo', 'Text'),
            ('jetBlast_matAereo', 'TxtJetBlastMatAero', 'Text'),
            ('jetBlast_faseOperacao', 'cmbJetBlastFaseOpAero', 'Selected.Value'),
            ("'jetBlast_local (jetBlast_local0)'", 'TxtJetBlastLocal', 'Text'),
            ('jetBlast_mapaGrade', 'TxtJetBlastMapaGrade', 'Text'),
            ('jetBlast_dano', 'cmbJetBlastDano', 'Selected.Value'),
            ('jetBlast_danoDesc', 'TxtJetBlastDanoDesc', 'Text'),
            ('jetBlast_acoesIniciais', 'TxtJetBlastAcoesTomadas', 'Text'),
            ('jetBlast_ocorrenciaDesc', 'TxtJetBlastDescOcorrencia', 'Text'),
        ],
        data=('jetBlast_data', 'dtpJetBlastDataCadastro'),
        hora=('jetBlast_hora', 'cmbJetBlastHoraCadastro', 'cmbJetBlastMinuCadastro'),
        extras=[],
        filhos=[
            dict(colecao='col_jetBlastImg', tabela="'14.8-tbl_JetBlastImg'",
                 fk='jetBlastImg_idOcorrencia', campos={'img': 'jetBlastImg_imagem'}),
            dict(colecao='col_jetBlastItemAtingido', tabela="'14.8-tbl_JetBlastItemAtingido'",
                 fk='jetBlastIA_idOcorrencia', campos={'item': 'jetBlastIA_item', 'info': 'jetBlastIA_info'}),
        ],
    ),
    'OcoSolo': dict(
        campos=[
            ('ocoSolo_ciaAerea', 'dropOcoSoloCiaAerea', 'Selected.Value'),
            ('OcoSolo_prefixoNome', 'TxtOcoSoloPrefixoNome', 'Text'),
            ('ocoSolo_voo', 'TxtOcoSoloVoo', 'Text'),
            ('ocoSolo_matAeronave', 'TxtOcoSoloMatAero', 'Text'),
            ('ocoSolo_numPosEstacion', 'TxtOcoSoloPosiAeronave', 'Text'),
            ('ocoSolo_esata', 'TxtOcoSoloEsata', 'Text'),
            ('ocoSolo_impOcorrencia', 'dropOcoSoloImpOcorre', 'Selected.Value'),
            ('ocoSolo_impVoo', 'cmbOcoSoloImpVoo', 'Selected.Value'),
            ('ocoSolo_impVooDesc', 'TxtOcoSoloImpVooDesc', 'Text'),
            ('ocoSolo_natAtividade', 'dropOcoSoloNatAtividade', 'Selected.Value'),
            ('ocoSolo_condTempo', 'cmbOcoSoloCondTempo', 'Selected.Value'),
            ('ocoSolo_tipEquipa', 'dropOcoSoloTipoEquipa', 'Selected.Value'),
            ('ocoSolo_IdenEquipa', 'TxtOcoSoloIdenEquipa', 'Text'),
            ('ocoSolo_comandante', 'TxtOcoSoloNomeComand', 'Text'),
            ('ocoSolo_anacComandante', 'TxtOcoSoloAnacComand', 'Text'),
            ('ocoSolo_copiloto', 'TxtOcoSoloNomeCopilo', 'Text'),
            ('ocoSolo_anacCopiloto', 'TxtOcoSoloAnacCopilo', 'Text'),
            ('ocoSolo_dano', 'cmbOcoSoloDano', 'Selected.Value'),
            ('ocoSolo_danNivel', 'dropOcoSoloDanoNivel', 'Selected.Value'),
            ('ocoSolo_danoDesc', 'TxtOcoSoloDanoDesc', 'Text'),
            ('ocoSolo_danTipAero', 'cmbOcoSoloTipoAero', 'Selected.Value'),
            ('ocoSolo_relFisca', 'TxtOcoSoloRelFisc', 'Text'),
        ],
        data=('ocoSolo_data', 'dtpOcoSoloData'),
        hora=('ocoSolo_hora', 'cmbOcoSoloHora', 'cmbOcoSoloMinuto'),
        # origem/destino são Upper(Texto) — reversível sem risco, o valor gravado já é maiúsculo.
        extras=[('ocoSolo_origem', ['TxtOcoSoloOrigem'], 'upper'), ('ocoSolo_destino', ['TxtOcoSoloDestino'], 'upper')],
        filhos=[
            dict(colecao='col_ocoSoloImg', tabela="'16.1-tbl_OcoSoloImagens'",
                 fk='ocoSoloFK_id', campos={'img': 'ocoSoloImg_imagem'}),
        ],
    ),
}

# nome do controle "Editar" na tela de lista de cada módulo (achado por texto,
# não segue um padrão de nome previsível entre módulos).
BOTAO_EDITAR = {
    'ColVei': 'ButtonCanvas7_7', 'DerFlu': 'ButtonCanvas7_14', 'ExcPista': 'ButtonCanvas7_28',
    'IncPista': 'ButtonCanvas7_36', 'IntExt': 'ButtonCanvas7_52', 'JetBlast': 'ButtonCanvas7_60',
    'OcoSolo': 'ButtonCanvas7_68',
}


def _ev(k):
    return f'var_editando{k}'


def _reg(k):
    return f'var_registro{k}'


# ─────────────────────────────────────────────────────────────────────────────
# Botão Editar (tela de lista): destrava e carrega o registro + filhos.
# ─────────────────────────────────────────────────────────────────────────────
def onselect_editar(m, edic):
    k, pfx = m['key'], m['pfx']
    partes = [
        f"Navigate(\n    {m['forms']},\n    ScreenTransition.Fade,\n    {{\n        {_ev(k)}: true,\n        {_reg(k)}: ThisItem\n    }}\n)"
    ]
    for f in edic['filhos']:
        col = f['colecao']
        if f.get('somente_leitura'):
            # não carrega (decifrar o formato daria o mesmo risco dos campos
            # complexos) — mas tem que começar vazio, senão sobra do
            # collection algum resíduo de uma sessão anterior (ex.: um
            # "Cadastrar" abandonado sem salvar) e isso viraria filho novo
            # deste registro ao salvar, sem o usuário ter digitado nada aqui.
            partes.append(f"Clear({col})")
            continue
        # campo direto (ID, sem prefixo) — o mesmo padrão que o resto desta base
        # já usa dentro de ForAll (ex.: "colVeiEnv_nome: nome"), sem ThisRecord.
        # 'id' além de 'dbId': o botão "Adicionar" original desta coleção (na
        # tela de formulário) já grava cada linha com um campo 'id' (contador
        # local, Filter(col, id>=0)+1) que este ClearCollect não tinha — duas
        # formas diferentes de povoar a MESMA coleção, o Studio unifica o tipo
        # e reprova Clear/ClearCollect em todo lugar que usa col_xxx (achado
        # via Verificador de aplicativo: ~48 erros por módulo). Repetir ID
        # também em 'id' fecha os dois formatos no mesmo conjunto de colunas
        # sem mudar o botão "Adicionar" (ver aplicar_dbid_blank, que fecha o
        # mesmo buraco do outro lado).
        campos_txt = ',\n            '.join(
            ['dbId: ID', 'id: ID'] + [f'{cf}: {tf}' for cf, tf in f['campos'].items()]
        )
        partes.append(
            f"ClearCollect(\n    {col},\n    ForAll(\n        Filter(\n            {f['tabela']},\n            {f['fk']} = ThisItem.{pfx}_id\n        ),\n        {{\n            {campos_txt}\n        }}\n    )\n)"
        )
        partes.append(f"ClearCollect(\n    {col}_orig,\n    {col}\n)")
    return '=' + ';\n'.join(partes)


def aplicar_lista(path, m, edic):
    # linhas soltas, sem terminador embutido — mesma convenção de split_screen()
    # (universal newlines na leitura, \r\n explícito na gravação no final).
    lines = open(path, encoding='utf-8').read().split('\n')
    nome_ctrl = BOTAO_EDITAR[m['key']]
    ctrl_idx = find_ctrl(lines, nome_ctrl)
    if ctrl_idx < 0:
        raise SystemExit(f"[{m['key']}] botao Editar '{nome_ctrl}' nao encontrado em {path}")
    set_prop(lines, ctrl_idx, 'DisplayMode', '=DisplayMode.Edit')
    novo_onselect = onselect_editar(m, edic)
    # conteúdo do bloco '|-' tem que ficar MAIS indentado que a própria chave
    # "OnSelect:" (senão o YAML não é válido) — mesma conta que _pad() usa em
    # gerar.py: indentação do Properties: + 4.
    pi, _ = prop_block(lines, ctrl_idx)
    pind = ind(lines[pi]) + 4
    set_prop(lines, ctrl_idx, 'OnSelect', '|-\n' + '\n'.join(
        (' ' * pind + l) if l.strip() else '' for l in novo_onselect.split('\n')
    ))

    # reset do estado de edição ao clicar em "Cadastrar" (Novo) — garante que uma
    # edição abandonada sem salvar não vaza pro próximo cadastro novo. Acha o
    # Navigate(<forms>, ...) pelo 1º argumento via find_call — não por uma regex
    # prevendo o formato exato: alguns módulos passam um 3º argumento de
    # contexto (ex.: Interferência Externa manda {var_visiblePainelTipo: true}),
    # outros não.
    texto = '\n'.join(lines)
    k = m['key']
    rn = find_call(texto, 'Navigate')
    fim_nav = None
    while rn:
        na, nb, nc = rn
        nargs = split_args(texto[nb:nc - 1])
        if nargs and nargs[0].strip() == m['forms']:
            fim_nav = nc
            break
        rn = find_call(texto, 'Navigate', nc)
    if fim_nav is None:
        raise SystemExit(f"[{k}] Navigate de Cadastrar nao encontrado para resetar estado de edicao")
    # indentação: mesma coluna onde o Navigate começa — mas o "=" do início da
    # fórmula (Navigate é sempre o 1º statement do OnSelect do Cadastrar) fica
    # imediatamente antes de "Navigate" na mesma linha e NÃO é recuo, é
    # conteúdo; contar esse caractere no pad gera 1 espaço a mais que a coluna
    # real do bloco '|-' (achado comparando bytes com cat -A: "Set(" saía na
    # coluna 27 enquanto "=Navigate(" está na 26) — YAML de bloco literal só
    # exige recuo >= o da 1ª linha, então o espaço extra não quebra o arquivo,
    # mas fica com um espaço perdido no começo de cada linha desse trecho.
    ls = texto.rfind('\n', 0, na) + 1
    col_eq = na - 1 if na > ls and texto[na - 1] == '=' else na
    pad = ' ' * (col_eq - ls)
    insercao = f";\n{pad}Set(\n{pad}    {_ev(k)},\n{pad}    false\n{pad});\n{pad}Set(\n{pad}    {_reg(k)},\n{pad}    Blank()\n{pad})"
    texto = texto[:fim_nav] + insercao + texto[fim_nav:]

    open(path, 'w', encoding='utf-8', newline='\r\n').write(texto)


# ─────────────────────────────────────────────────────────────────────────────
# Tela de formulário: pré-preencher campo a campo, gravação condicional
# (atualizar x criar) e reconciliação dos filhos editáveis.
# ─────────────────────────────────────────────────────────────────────────────
def _default_simples(coluna, k):
    return f'=If({_ev(k)}, {_reg(k)}.{coluna}, "")'


def _tipo_controle(lines, idx):
    """lê a linha 'Control: X' logo abaixo de lines[idx] ('- Nome:')."""
    for j in range(idx + 1, min(idx + 3, len(lines))):
        if lines[j].strip().startswith('Control:'):
            return lines[j].split('Control:', 1)[1].strip()
    return ''


def aplicar_campos(lines, m, edic):
    k = m['key']
    pulados = []
    for coluna, controle, *_ in edic['campos']:
        idx = find_ctrl(lines, controle)
        if idx < 0:
            raise SystemExit(f"[{k}] controle '{controle}' (campo {coluna}) nao encontrado")
        tipo = _tipo_controle(lines, idx)
        if tipo.startswith('Classic/ComboBox'):
            # ComboBox (controles "drop*" nesta base) não usa 'Default' — usa
            # 'DefaultSelectedItems', que espera uma TABELA no formato exato de
            # Items/DisplayFields. Sem conseguir testar no Studio, arriscar essa
            # forma é o mesmo tipo de risco dos campos compostos: melhor pular.
            # O campo continua sendo GRAVADO normalmente ao salvar — só não vem
            # pré-preenchido ao abrir a edição; o usuário re-seleciona à mão.
            pulados.append(controle)
            continue
        set_prop(lines, idx, 'Default', _default_simples(coluna, k))

    # data: Classic/DatePicker usa 'DefaultDate', não 'Default' — único campo
    # deste tipo em cada módulo, sempre confirmado no dicionário de propriedades.
    coluna_d, ctrl_d = edic['data']
    idx_d = find_ctrl(lines, ctrl_d)
    if idx_d < 0:
        raise SystemExit(f"[{k}] controle de data '{ctrl_d}' nao encontrado")
    if not _tipo_controle(lines, idx_d).startswith('Classic/DatePicker'):
        raise SystemExit(f"[{k}] controle de data '{ctrl_d}' nao e Classic/DatePicker — confirmar propriedade certa")
    set_prop(lines, idx_d, 'DefaultDate', _default_simples(coluna_d, k))

    if pulados:
        print(f"   {k}: pré-preenchimento pulado em {len(pulados)} campo(s) ComboBox "
              f"(continuam sendo salvos): {', '.join(pulados)}")

    # hora composta: "H:M" -> dois combos (sentinela "hor"/"min", igual ao Default original)
    coluna_h, ctrl_h, ctrl_m = edic['hora']
    ih, im = find_ctrl(lines, ctrl_h), find_ctrl(lines, ctrl_m)
    if ih < 0 or im < 0:
        raise SystemExit(f"[{k}] controles de hora '{ctrl_h}'/'{ctrl_m}' nao encontrados")
    reg, ev = _reg(k), _ev(k)
    set_prop(lines, ih, 'Default',
             f'=If({ev}, Left({reg}.{coluna_h}, Find(":", {reg}.{coluna_h}) - 1), "hor")')
    set_prop(lines, im, 'Default',
             f'=If({ev}, Mid({reg}.{coluna_h}, Find(":", {reg}.{coluna_h}) + 1, 2), "min")')

    # extras: compostos conhecidos e seguros de reverter — mesma checagem de
    # tipo dos campos simples (ex.: o mapaGrade da Colisão de Veículos é
    # ComboBoxMG1/MG2, Classic/ComboBox — mesmo caso, mesma decisão de pular).
    for coluna, controles, modo in edic['extras']:
        idxs = [find_ctrl(lines, c) for c in controles]
        if any(i < 0 for i in idxs):
            raise SystemExit(f"[{k}] controles extras {controles} nao encontrados")
        if any(_tipo_controle(lines, i).startswith('Classic/ComboBox') for i in idxs):
            pulados.append('+'.join(controles))
            print(f"   {k}: pré-preenchimento pulado no extra ComboBox "
                  f"{'+'.join(controles)} (continua sendo salvo)")
            continue
        if modo == '-':
            i1, i2 = idxs
            set_prop(lines, i1, 'Default',
                     f'=If({ev}, Left({reg}.{coluna}, Find("-", {reg}.{coluna}) - 1), "")')
            set_prop(lines, i2, 'Default',
                     f'=If({ev}, Mid({reg}.{coluna}, Find("-", {reg}.{coluna}) + 1, 10), "")')
        elif modo == 'upper':
            (i1,) = idxs
            set_prop(lines, i1, 'Default', f'=If({ev}, {reg}.{coluna}, "")')
        else:
            raise SystemExit(f"[{k}] modo de extra desconhecido: {modo}")
    return lines


def _coluna(texto, pos):
    """coluna (distância do \\n anterior) de uma posição — pra reindentar texto
    inserido com indent_lines() e não quebrar a detecção de bloco por
    indentação (block_end/split_screen), que é ingênua: qualquer linha minha
    com menos recuo do que o contexto ao redor faz o bloco "Children:" (ou o
    "|-" da formula) parecer terminado ali, cortando o resto do arquivo fora
    do que os passos seguintes conseguem enxergar. Foi exatamente esse bug na
    primeira tentativa: texto inserido com só 4 espaços de recuo, dentro de um
    OnSelect que está a 30+ colunas de profundidade."""
    ls = texto.rfind('\n', 0, pos) + 1
    return pos - ls


def aplicar_gravacao(texto, m, edic):
    """Aplica no TEXTO CRU (antes do cirurgia_gravacao rodar):
       1. Patch do pai: Defaults(tab) -> condicional editar/criar.
       2. Patch de cada filho reconciliável: Defaults(childTab) -> condicional
          atualizar/criar por dbId, mais a exclusão dos que sumiram da coleção.
       cirurgia_gravacao() continua detectando os dois (a checagem dele foi
       afrouxada para aceitar 'Defaults(' em qualquer lugar do 2º argumento,
       não só no começo), e a reindentação dele preserva o que escrevemos aqui.
       TODO texto inserido passa por indent_lines() na coluna exata de onde
       entra — ver _coluna() acima.
    """
    k, tab = m['key'], m['tabela']
    ev, reg = _ev(k), _reg(k)

    # 1. Patch do pai — localiza Defaults(...) por posição exata (find_call), não
    #    por comparar string "stripada" contra o texto cru: split_args() tira os
    #    espaços/quebras de cada argumento, então um .replace(arg_stripado, ...)
    #    no texto cru pode não achar nada — falha calada, sem exceção — e o Patch
    #    nunca fica condicional. find_call() devolve posição, não string, então
    #    não tem esse risco.
    r = find_call(texto, 'Patch')
    achou_pai = False
    while r:
        a, b, c = r
        args = split_args(texto[b:c - 1])
        if len(args) >= 2 and args[0].strip() == tab and 'Defaults(' in args[1]:
            rdef = find_call(texto, 'Defaults', b)
            if not rdef or rdef[2] > c:
                raise SystemExit(f"[{k}] Defaults(...) do Patch do pai nao localizado com precisao")
            da, _, dc = rdef
            bruto = f'If(\n    {ev},\n    {reg},\n    {texto[da:dc]}\n)'
            novo = indent_lines(bruto, _coluna(texto, da))
            texto = texto[:da] + novo + texto[dc:]
            achou_pai = True
            break
        r = find_call(texto, 'Patch', c)
    if not achou_pai:
        raise SystemExit(f"[{k}] Patch do pai nao encontrado para tornar condicional")

    # 2. Patch de cada filho reconciliável + exclusão dos removidos
    for f in edic['filhos']:
        if f.get('somente_leitura'):
            continue
        col, childTab, fk = f['colecao'], f['tabela'], f['fk']
        # acha o ForAll(col, ...) pelo 1º argumento — não pela 1ª ocorrência do
        # texto "col," (que pode casar em outro lugar, ex. dentro de um comentário
        # ou de outro filho) — mesmo motivo do find_call acima.
        rf = find_call(texto, 'ForAll')
        forall_fim = None
        while rf:
            fa, fb, fc = rf
            fargs = split_args(texto[fb:fc - 1])
            if fargs and fargs[0].strip() == col:
                forall_fim = fc
                break
            rf = find_call(texto, 'ForAll', fc)
        if forall_fim is None:
            raise SystemExit(f"[{k}] ForAll do filho '{col}' nao encontrado")
        # dentro desse ForAll, o Patch(childTab, Defaults(childTab), {...}) — acha
        # por posição exata do mesmo jeito que o Patch do pai.
        rp = find_call(texto, 'Patch', fb)
        if not rp or rp[2] > forall_fim:
            raise SystemExit(f"[{k}] Patch do filho '{col}' nao encontrado dentro do ForAll")
        pa, pb, pc = rp
        rdef = find_call(texto, 'Defaults', pb)
        if not rdef or rdef[2] > pc:
            raise SystemExit(f"[{k}] Defaults(...) do filho '{col}' nao localizado com precisao")
        da, _, dc = rdef
        # dbId direto (sem ThisRecord.) — 'childTab' (a lista do SharePoint) não
        # tem nenhuma coluna chamada dbId, então não há ambiguidade: o campo bare
        # sobe pro escopo do ForAll de fora (col_xxx), mesmo padrão do resto da base.
        bruto = f'If(\n    IsBlank(dbId),\n    {texto[da:dc]},\n    LookUp(\n        {childTab},\n        ID = dbId\n    )\n)'
        novo = indent_lines(bruto, _coluna(texto, da))
        delta = len(novo) - (dc - da)
        texto = texto[:da] + novo + texto[dc:]
        forall_fim += delta

        # exclusão: logo depois de fechar o ForAll (posição já achada e ajustada
        # acima), insere um novo passo — só roda em edição — pra apagar do
        # SharePoint quem existia na abertura da edição e sumiu da coleção.
        # Reindenta na coluna de onde o ForAll deste filho começou (fa) — é o
        # próximo statement do mesmo nível na cadeia, mesma coluna que ele.
        bruto_del = (
            f'If(\n    {ev},\n    ForAll(\n        Filter(\n            {col}_orig,\n'
            f'            !(dbId in {col}.dbId)\n        ),\n        Remove(\n            {childTab},\n'
            f'            LookUp(\n                {childTab},\n                ID = dbId\n            )\n        )\n    )\n)'
        )
        delecao = ';\n' + indent_lines(bruto_del, _coluna(texto, fa), first=True)
        texto = texto[:forall_fim] + delecao + texto[forall_fim:]
    return texto


def aplicar_dbid_blank(texto, m, edic):
    """Insere 'dbId: Blank(),' como 1º campo do Collect(col, {...}) original do
    botão "Adicionar" de cada filho reconciliável (achado por posição exata via
    find_call, igual ao resto do módulo — não string-match). É o outro lado do
    mesmo problema que o 'id: ID' em onselect_editar() fecha: sem isso, um item
    adicionado à coleção DURANTE uma edição não carrega dbId nenhum, e o Studio
    reprova Clear/ClearCollect por causa da coleção ter dois formatos diferentes
    pra registros diferentes (achado via Verificador de aplicativo)."""
    k = m['key']
    for f in edic['filhos']:
        if f.get('somente_leitura'):
            continue
        col = f['colecao']
        r = find_call(texto, 'Collect')
        achou = False
        while r:
            a, b, c = r
            args = split_args(texto[b:c - 1])
            if args and args[0].strip() == col:
                brace = texto.find('{', b)
                if brace < 0 or brace > c:
                    raise SystemExit(f"[{k}] registro do Collect('{col}', ...) nao encontrado")
                nl = texto.find('\n', brace)
                if nl < 0 or nl > c:
                    raise SystemExit(f"[{k}] Collect('{col}', ...) fora do formato multi-linha esperado")
                ls = nl + 1
                j = ls
                while j < len(texto) and texto[j] == ' ':
                    j += 1
                pad = texto[ls:j]
                texto = texto[:nl] + f'\n{pad}dbId: Blank(),' + texto[nl:]
                achou = True
                break
            r = find_call(texto, 'Collect', c)
        if not achou:
            raise SystemExit(f"[{k}] Collect('{col}', ...) do botao Adicionar nao encontrado")
    return texto


def aplicar_forms(path, m, edic):
    # leitura em modo universal (\r\n -> \n) pra processar como o resto do
    # gerador processa (linhas soltas, sem terminador embutido) — igual ao que
    # split_screen() já faz. Grava de volta com \r\n explícito no final, porque
    # o resto do msapp/Src está em CRLF e é isso que ficou preservado nas outras
    # edições desta sessão.
    import gerar
    texto = open(path, encoding='utf-8').read()
    lines = texto.split('\n')
    lines = gerar.normalizar_escalares(lines)  # aspas-com-\n -> bloco '|-'; sem perda
    texto = '\n'.join(lines)
    texto = aplicar_gravacao(texto, m, edic)
    texto = aplicar_dbid_blank(texto, m, edic)
    lines = texto.split('\n')
    aplicar_campos(lines, m, edic)
    open(path, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(lines))


def main():
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(__file__))
    from modulos import MODULOS
    for m in MODULOS:
        edic = EDICAO[m['key']]
        aplicar_lista(f"msapp/Src/{m['lista']}.pa.yaml", m, edic)
        aplicar_forms(f"msapp/Src/{m['forms']}.pa.yaml", m, edic)
        print(f"{m['key']:10s} edição habilitada "
              f"({len(edic['campos']) + 2 + len(edic['extras'])} campos, "
              f"{sum(1 for f in edic['filhos'] if not f.get('somente_leitura'))} filho(s) reconciliável(eis))")


if __name__ == '__main__':
    main()
