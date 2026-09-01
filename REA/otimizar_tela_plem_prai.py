#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizador da tela PLEM/PRAI — REA/ScreenAcionamentosNewPlemPrai.pa.yaml.

Escopo definido pelo usuário (2026-08-14): **não mexer no layout**. Só
performance, lógica e correção de fórmulas. Nenhuma propriedade visual
(X, Y, Width, Height, Fill, Color, Padding*, Radius*, Layout*, Font*, Size,
Align, Border*, DropShadow, Text, Visible, Variant...) é alterada — isso é
provado pela trava `guarda_layout()`, que compara as duas árvores YAML e
reprova qualquer diferença fora da lista explícita de mudanças esperadas.

Ganhos aplicados:

  P1  Timer de monitoramento: 5s -> 30s, `CountRows` sobre lista SharePoint
      trocado por comparação do maior ID (delegável) e disparo só quando o
      monitoramento está aberto. Era o maior gargalo: rodava a cada 5s mesmo
      com a seção fechada, varrendo a lista inteira de atividades.
  P2  25 galerias ganham `DelayItemLoading` + `LoadingSpinner` (carregam sob
      demanda em vez de tudo de uma vez).
  P3  Buscas em `Classic/TextInput` ganham `DelayOutput` (consulta ao soltar a
      tecla, não a cada caractere).
  P4  `Search()` sobre lista SharePoint -> `Filter(... StartsWith(...))`
      delegável (equipamentos e contatos).
  P5  `LookUp` repetidos na mesma fórmula -> um único `LookUp` via `With`
      (6->1, 3->1, 3->1, 3->1). Cada repetição era uma consulta por linha.
  P6  Statements duplicados removidos (exclusão de acionamento gravava 2x;
      excluir/restaurar atividade dava `Patch` 2x).

Correções de fórmula/lógica:

  C1  "Não atendeu" postava no chat usando `ID_chat.chat` (variável de sessão,
      em branco para quem não criou o acionamento) -> `var_dadosAcionamento.ID_chat`.
  C2  Log CONTATO_NR gravava `ID_contato: ThisItem.ID` (id do vínculo, não do
      contato) e `ID_entidade: var_acionarEntidade.ID` (em branco quando a ação
      vem da atividade) -> ids do próprio item + `ID_chat`.
  C3  Acionamentos PRAI: Continuar/Visualizar ligavam `var_visibleAcionamentoPRAI`,
      flag que NENHUM controle lê — nada abria. Agora abrem o monitoramento
      (`var_visibleFluxogramaAcionamentosReal`), que já atende PLEM e PRAI.
  C4  O fluxograma carregado no Continuar/Visualizar usava `varAeroUser` (e não
      o aeroporto do registro) e um `LookUp` em `col_emergencias`, coleção que
      pode estar vazia -> usa `var_dadosEmergencia.ID` e o aeroporto do item.
  C5  Guarda quando o fluxo do Teams não devolve o chat (antes falhava calado e
      todas as mensagens seguintes iam para um chat inexistente).

Executar duas vezes e conferir que o hash não muda (checklist LICOES).
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'ScreenAcionamentosNewPlemPrai.pa.yaml')
OUT = os.path.join(HERE, 'ScreenAcionamentosPlemPraiOtimizada.pa.yaml')


def die(msg):
    sys.stderr.write('ERRO: %s\n' % msg)
    sys.exit(1)


def indent_of(line):
    return len(line) - len(line.lstrip(' '))


# ------------------------------------------------------------------ patches
# cada entrada: (rótulo, texto_original, texto_novo, ocorrências_esperadas)

P_TIMER_DUR = (
    'P1a timer 5s->30s',
    '                                                Duration: =5000',
    '                                                Duration: =30000',
    1,
)

P_TIMER_END = (
    'P1b timer delegável e restrito ao monitoramento',
    '''                                                OnTimerEnd: |-
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
                                                  )''',
    '''                                                OnTimerEnd: |-
                                                  =If(
                                                      var_visibleFluxogramaAcionamentosReal And !IsBlank(var_dadosAcionamento),
                                                      If(
                                                          Coalesce(
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
                                                          ) > Coalesce(
                                                              First(
                                                                  Sort(
                                                                      GalleryAtividadesLancadas.AllItems,
                                                                      ID,
                                                                      SortOrder.Descending
                                                                  )
                                                              ).ID,
                                                              0
                                                          ),
                                                          Select(Function_consultarAtividades)
                                                      )
                                                  )''',
    1,
)

P_SEARCH_EQP = (
    'P4a busca de equipamentos delegável',
    '''                                                Items: |-
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
                                                  )''',
    '''                                                Items: |-
                                                  =Sort(
                                                      Filter(
                                                          tbl_equipamentosAcionamentos,
                                                          Aeroporto = ComboboxCanvasAeroSelectCadEqp.Selected.Value And (
                                                              IsBlank(TextInputCanvas3.Value) || StartsWith(
                                                                  Item,
                                                                  TextInputCanvas3.Value
                                                              )
                                                          )
                                                      ),
                                                      Item,
                                                      SortOrder.Ascending
                                                  )''',
    1,
)

P_SEARCH_CONTATOS = (
    'P4b busca de contatos delegável',
    '''                                                Items: |-
                                                  =Search(
                                                      Filter(
                                                          tbl_contatos_entidades,
                                                          Aeroporto = ComboboxCanvasAeroSelectCadFluxo.Selected.Value
                                                      ),
                                                      TextInput1.Text,
                                                      nome,
                                                      nome_orgao
                                                  )''',
    '''                                                Items: |-
                                                  =Filter(
                                                      tbl_contatos_entidades,
                                                      Aeroporto = ComboboxCanvasAeroSelectCadFluxo.Selected.Value And (
                                                          IsBlank(TextInput1.Text) || StartsWith(
                                                              nome,
                                                              TextInput1.Text
                                                          ) || StartsWith(
                                                              nome_orgao,
                                                              TextInput1.Text
                                                          )
                                                      )
                                                  )''',
    1,
)

P_HTML13 = (
    'P5a HtmlText13: 6 LookUp -> 1',
    '''                                                                  HtmlText: |-
                                                                    =If(
                                                                        ThisItem.Excluido,
                                                                        "<s><b>" & TimeValue(ThisItem.Hora) & "</b><br>" & If(
                                                                            !IsBlank(ThisItem.Acao),
                                                                            ThisItem.Atividade & Switch(
                                                                                true,
                                                                                ThisItem.Acao = "RESPONDEU AO FLOW" And LookUp(
                                                                                    tbl_FluxogramaAcionamentos,
                                                                                    ID = ThisItem.ID_entidade
                                                                                ).Nivel.Value = "ACIONAR",
                                                                                " > foi acionado",
                                                                                ThisItem.Acao = "RESPONDEU AO FLOW" And LookUp(
                                                                                    tbl_FluxogramaAcionamentos,
                                                                                    ID = ThisItem.ID_entidade
                                                                                ).Nivel.Value = "SOBREAVISO",
                                                                                " > foi colocado em estado de sobreaviso",
                                                                                ThisItem.Acao = "RESPONDEU AO FLOW" And LookUp(
                                                                                    tbl_FluxogramaAcionamentos,
                                                                                    ID = ThisItem.ID_entidade
                                                                                ).Nivel.Value = "INFORMAR",
                                                                                " > foi informado"
                                                                            )
                                                                        ) & "</s>",
                                                                        "<b>" & TimeValue(ThisItem.Hora) & "</b><br>" & If(
                                                                            !IsBlank(ThisItem.Acao),
                                                                            ThisItem.Atividade & Switch(
                                                                                true,
                                                                                ThisItem.Acao = "RESPONDEU AO FLOW" And LookUp(
                                                                                    tbl_FluxogramaAcionamentos,
                                                                                    ID = ThisItem.ID_entidade
                                                                                ).Nivel.Value = "ACIONAR",
                                                                                " > foi acionado",
                                                                                ThisItem.Acao = "RESPONDEU AO FLOW" And LookUp(
                                                                                    tbl_FluxogramaAcionamentos,
                                                                                    ID = ThisItem.ID_entidade
                                                                                ).Nivel.Value = "SOBREAVISO",
                                                                                " > foi colocado em estado de sobreaviso",
                                                                                ThisItem.Acao = "RESPONDEU AO FLOW" And LookUp(
                                                                                    tbl_FluxogramaAcionamentos,
                                                                                    ID = ThisItem.ID_entidade
                                                                                ).Nivel.Value = "INFORMAR",
                                                                                " > foi informado"
                                                                            )
                                                                        )
                                                                    )''',
    '''                                                                  HtmlText: |-
                                                                    =With(
                                                                        {
                                                                            _nivel: LookUp(
                                                                                tbl_FluxogramaAcionamentos,
                                                                                ID = ThisItem.ID_entidade
                                                                            ).Nivel.Value,
                                                                            _hora: TimeValue(ThisItem.Hora)
                                                                        },
                                                                        With(
                                                                            {
                                                                                _corpo: If(
                                                                                    !IsBlank(ThisItem.Acao),
                                                                                    ThisItem.Atividade & Switch(
                                                                                        true,
                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "ACIONAR",
                                                                                        " > foi acionado",
                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "SOBREAVISO",
                                                                                        " > foi colocado em estado de sobreaviso",
                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "INFORMAR",
                                                                                        " > foi informado"
                                                                                    )
                                                                                )
                                                                            },
                                                                            If(
                                                                                ThisItem.Excluido,
                                                                                "<s><b>" & _hora & "</b><br>" & _corpo & "</s>",
                                                                                "<b>" & _hora & "</b><br>" & _corpo
                                                                            )
                                                                        )
                                                                    )''',
    1,
)

P_LABEL115_8 = (
    'P5b Label115_8: 3 LookUp -> 1',
    '''                                                      Text: |-
                                                        =LookUp(
                                                            tbl_contatos_entidades,
                                                            ID = ThisItem.ID_contato
                                                        ).nome_orgao & " - " & LookUp(
                                                            tbl_contatos_entidades,
                                                            ID = ThisItem.ID_contato
                                                        ).nome
                                                        & " - " & LookUp(
                                                            tbl_contatos_entidades,
                                                            ID = ThisItem.ID_contato
                                                        ).tel_principal''',
    '''                                                      Text: |-
                                                        =With(
                                                            {
                                                                _contato: LookUp(
                                                                    tbl_contatos_entidades,
                                                                    ID = ThisItem.ID_contato
                                                                )
                                                            },
                                                            _contato.nome_orgao & " - " & _contato.nome & " - " & _contato.tel_principal
                                                        )''',
    1,
)

P_HTML11_1 = (
    'P5c HtmlText11_1: 3 LookUp -> 1',
    '''                                                      HtmlText: |-
                                                        ="<b>" & ThisItem.nome & "</b><br>" & LookUp(
                                                            tbl_contatos_entidades,
                                                            ID = ThisItem.ID_contato
                                                        ).nome_orgao & "<br>" & LookUp(
                                                            tbl_contatos_entidades,
                                                            ID = ThisItem.ID_contato
                                                        ).tel_principal & " ➖ " & LookUp(
                                                            tbl_contatos_entidades,
                                                            ID = ThisItem.ID_contato
                                                        ).tel_reserva''',
    '''                                                      HtmlText: |-
                                                        =With(
                                                            {
                                                                _contato: LookUp(
                                                                    tbl_contatos_entidades,
                                                                    ID = ThisItem.ID_contato
                                                                )
                                                            },
                                                            "<b>" & ThisItem.nome & "</b><br>" & _contato.nome_orgao & "<br>" & _contato.tel_principal & " ➖ " & _contato.tel_reserva
                                                        )''',
    1,
)

P_DUP_EXCLUIR = (
    'P6a exclusão de acionamento gravava 2x',
    '''                                                        =UpdateContext({var_visibleExcluirAcionamento: false});
                                                        RemoveIf(
                                                            tbl_ocorrenciaAcionamento,
                                                            ID = var_dadosAcionamento.ID
                                                        );
                                                        RemoveIf(
                                                            tbl_atividadesPlemPrai,
                                                            ID_acionamento = var_dadosAcionamento.ID
                                                        );
                                                        UpdateContext({var_visibleExcluirAcionamento: false});
                                                        RemoveIf(
                                                            tbl_ocorrenciaAcionamento,
                                                            ID = var_dadosAcionamento.ID
                                                        );
                                                        Notify(''',
    '''                                                        =UpdateContext({var_visibleExcluirAcionamento: false});
                                                        RemoveIf(
                                                            tbl_ocorrenciaAcionamento,
                                                            ID = var_dadosAcionamento.ID
                                                        );
                                                        RemoveIf(
                                                            tbl_atividadesPlemPrai,
                                                            ID_acionamento = var_dadosAcionamento.ID
                                                        );
                                                        Notify(''',
    1,
)

P_DUP_ICON45 = (
    'P6b excluir/restaurar atividade dava Patch 2x',
    '''                                                                    =If(
                                                                        ThisItem.Excluido,
                                                                        Patch(
                                                                            tbl_atividadesPlemPrai,
                                                                            ThisItem,
                                                                            {Excluido: false}
                                                                        );
                                                                        Patch(
                                                                            tbl_atividadesPlemPrai,
                                                                            ThisItem,
                                                                            {Excluido: false}
                                                                        ),
                                                                        Patch(
                                                                            tbl_atividadesPlemPrai,
                                                                            ThisItem,
                                                                            {Excluido: true}
                                                                        );
                                                                        Patch(
                                                                            tbl_atividadesPlemPrai,
                                                                            ThisItem,
                                                                            {Excluido: true}
                                                                        )
                                                                    );''',
    '''                                                                    =Patch(
                                                                        tbl_atividadesPlemPrai,
                                                                        ThisItem,
                                                                        {Excluido: !ThisItem.Excluido}
                                                                    );''',
    1,
)

P_CHATID_NR = (
    'C1 "Não atendeu" postava com ID_chat de sessão',
    '''                                                                  ) & " > contato não realizado",
                                                                  ID_chat.chat
                                                              );''',
    '''                                                                  ) & " > contato não realizado",
                                                                  var_dadosAcionamento.ID_chat
                                                              );''',
    1,
)

P_NR_IDS = (
    'C2 ids trocados no log CONTATO_NR',
    '''                                                                      Hora: Now(),
                                                                      ID_contato: ThisItem.ID,
                                                                      ID_entidade: var_acionarEntidade.ID
                                                                  }''',
    '''                                                                      Hora: Now(),
                                                                      ID_contato: ThisItem.ID_contato,
                                                                      ID_entidade: ThisItem.ID_entidade,
                                                                      ID_chat: var_dadosAcionamento.ID_chat
                                                                  }''',
    1,
)

P_PRAI_FLAG = (
    'C3 PRAI abria flag morta',
    '''                                                              If(
                                                                  ThisItem.Acionamento = "PLEM",
                                                                  UpdateContext({var_visibleFluxogramaAcionamentosReal: true}),
                                                                  UpdateContext({var_visibleAcionamentoPRAI: true})
                                                              );''',
    '''                                                              UpdateContext({var_visibleFluxogramaAcionamentosReal: true});''',
    2,  # Continuar e Visualizar
)

P_FLUXO_CONTINUAR = (
    'C4a fluxo do Continuar usava col_emergencias/varAeroUser',
    '''                                                              ClearCollect(
                                                                  col_emergenciaFluxo,
                                                                  Filter(
                                                                      tbl_FluxogramaAcionamentos,
                                                                      Aeroporto = varAeroUser And ID_emergencia = LookUp(
                                                                          col_emergencias,
                                                                          Titulo = var_dadosAcionamento.Emergencia,
                                                                          ID
                                                                      )
                                                                  )
                                                              )''',
    '''                                                              ClearCollect(
                                                                  col_emergenciaFluxo,
                                                                  Filter(
                                                                      tbl_FluxogramaAcionamentos,
                                                                      Aeroporto = ThisItem.Aeroporto And ID_emergencia = var_dadosEmergencia.ID
                                                                  )
                                                              )''',
    1,
)

P_FLUXO_VISUALIZAR = (
    'C4b fluxo do Visualizar usava varAeroUser',
    '''                                                              ClearCollect(
                                                                  col_emergenciaFluxo,
                                                                  Filter(
                                                                      tbl_FluxogramaAcionamentos,
                                                                      Aeroporto = varAeroUser And ID_emergencia = LookUp(
                                                                          tbl_Emergencias,
                                                                          Titulo = var_dadosAcionamento.Emergencia,
                                                                          ID
                                                                      )
                                                                  )
                                                              )''',
    '''                                                              ClearCollect(
                                                                  col_emergenciaFluxo,
                                                                  Filter(
                                                                      tbl_FluxogramaAcionamentos,
                                                                      Aeroporto = ThisItem.Aeroporto And ID_emergencia = var_dadosEmergencia.ID
                                                                  )
                                                              )''',
    1,
)

P_CHAT_GUARD = (
    'C5 guarda quando o chat do Teams não é criado',
    '''                                                              Set(
                                                                  varChatID,
                                                                  ID_chat.chat
                                                              );''',
    '''                                                              Set(
                                                                  varChatID,
                                                                  ID_chat.chat
                                                              );
                                                              If(
                                                                  IsBlank(varChatID),
                                                                  Notify(
                                                                      "Atenção: o chat do Teams não foi criado. As mensagens do acionamento não serão publicadas. Verifique o fluxo 'Criar chat de acionamentos PLEM/PRAI'.",
                                                                      NotificationType.Warning
                                                                  )
                                                              );''',
    1,
)

P_DEDUP_EMAILS = (
    'C6 dedup de participantes devolvia N copias do primeiro contato',
    """                                                          // REMOVE DUPLICADOS PELO EMAIL
                                                          ClearCollect(
                                                              col_emailsCcrFilter,
                                                              ForAll(
                                                                  Distinct(
                                                                      col_emailsCcrFilter,
                                                                      Email
                                                                  ),
                                                                  LookUp(
                                                                      col_emailsCcrFilter,
                                                                      Email = ThisRecord.Email
                                                                  )
                                                              )
                                                          );""",
    """                                                          // REMOVE DUPLICADOS PELO EMAIL
                                                          ClearCollect(
                                                              col_emailsUnicos,
                                                              ForAll(
                                                                  Distinct(
                                                                      col_emailsCcrFilter,
                                                                      Email
                                                                  ) As EMAIL_UNICO,
                                                                  LookUp(
                                                                      col_emailsCcrFilter,
                                                                      Email = EMAIL_UNICO.Value
                                                                  )
                                                              )
                                                          );
                                                          Clear(col_emailsCcrFilter);
                                                          Collect(
                                                              col_emailsCcrFilter,
                                                              col_emailsUnicos
                                                          );""",
    1,
)

P_FINALIZACAO_CHAT = (
    'C7 finalizacao nao subia para o chat e logava ID_chat de sessao',
    """                                                                  ID_chat: varChatID
                                                              }
                                                          );
""",
    """                                                                  ID_chat: var_dadosAcionamento.ID_chat
                                                              }
                                                          );
                                                          If(
                                                              var_acaoFormOcorrenciaAcionamento = "Finalizar" && !IsBlank(var_dadosAcionamento.ID_chat),
                                                              EnviarAtividadeparachatteams.Run(
                                                                  "ACIONAMENTO FINALIZADO > " & _registro.Ambiente & " > " & _aeroporto & " > por " & varNomeUser,
                                                                  var_dadosAcionamento.ID_chat
                                                              )
                                                          );
""",
    1,
)

PATCHES = [
    P_TIMER_DUR, P_TIMER_END,
    P_SEARCH_EQP, P_SEARCH_CONTATOS,
    P_HTML13, P_LABEL115_8, P_HTML11_1,
    P_DUP_EXCLUIR, P_DUP_ICON45,
    P_CHATID_NR, P_NR_IDS, P_PRAI_FLAG,
    P_FLUXO_CONTINUAR, P_FLUXO_VISUALIZAR, P_CHAT_GUARD,
    P_DEDUP_EMAILS, P_FINALIZACAO_CHAT,
]

# controles cujas propriedades mudam de propósito (trava de layout)
EXPECTED_CHANGES = {
    ('Timer1', 'Duration'), ('Timer1', 'OnTimerEnd'),
    ('GalleryEquipamento_1', 'Items'),
    ('GalleryContatosEntidadesExistente', 'Items'),
    ('HtmlText13', 'HtmlText'),
    ('Label115_8', 'Text'),
    ('HtmlText11_1', 'HtmlText'),
    ('ButtonCanvas27_58', 'OnSelect'),
    ('Icon45', 'OnSelect'),
    ('ButtonCanvas47_3', 'OnSelect'),          # C1 + C2
    ('ButtonCanvas49', 'OnSelect'),            # C3 + C4a
    ('ButtonCanvas49_1', 'OnSelect'),          # C3 + C4b
    ('FormOcorrenciaAcionamento', 'OnSuccess'),  # C5
}
# propriedades que podem ser ACRESCENTADAS (performance, sem efeito visual)
ADDABLE = {'DelayItemLoading', 'LoadingSpinner', 'DelayOutput'}


# ------------------------------------------------- transformações mecânicas

def _inject_after_properties(text, control_re, props, only_if=None):
    """Insere `props` logo após a linha `Properties:` de cada controle que casa
    `control_re`, quando ainda não existirem no bloco."""
    lines = text.split('\n')
    out, i, n = [], 0, 0
    while i < len(lines):
        ln = lines[i]
        out.append(ln)
        m = re.match(control_re, ln)
        if not m:
            i += 1
            continue
        ctl_ind = len(m.group(1))
        # bloco completo do controle
        j = i + 1
        block = []
        while j < len(lines):
            if lines[j].strip() and indent_of(lines[j]) < ctl_ind:
                break
            block.append(lines[j])
            j += 1
        blob = '\n'.join(block)
        props_line = ' ' * ctl_ind + 'Properties:'
        if props_line not in block or (only_if and not only_if(blob)):
            i += 1
            continue
        for ln2 in block:
            i += 1
            out.append(ln2)
            if ln2 == props_line:
                for p, v in props:
                    if not re.search(r'^\s*%s:' % p, blob, re.M):
                        out.append(' ' * (ctl_ind + 2) + '%s: =%s' % (p, v))
                        n += 1
        i = j - 1 + 1 - 1  # continua após o bloco já emitido
        i += 1
    return '\n'.join(out), n


def aplicar_mecanicas(text):
    text, n1 = _inject_after_properties(
        text, r'^(\s*)Control: Gallery@',
        [('DelayItemLoading', 'true'), ('LoadingSpinner', 'LoadingSpinner.Data')])
    text, n2 = _inject_after_properties(
        text, r'^(\s*)Control: Classic/TextInput@',
        [('DelayOutput', 'true')],
        # HintText pode ser bloco multilinha (|-), então a busca atravessa linhas
        only_if=lambda b: re.search(r'HintText:[\s\S]{0,80}?(Busc|Consult|Pesquis)', b))
    print('  P2/P3: %d propriedades de performance acrescentadas' % (n1 + n2))
    return text


# ------------------------------------------------------------- validações

def arvore(text):
    """{nome_controle: {prop: valor}} + lista de nomes, via parser YAML."""
    import yaml

    class L(yaml.SafeLoader):
        pass

    L.add_constructor('tag:yaml.org,2002:value', lambda l, n: '=')
    doc = yaml.load(text, Loader=L)
    props, ordem = {}, []

    def walk(node):
        for item in node.get('Children', []) or []:
            (name, body), = item.items()
            body = body or {}
            ordem.append(name)
            props[name] = dict(body.get('Properties', {}) or {})
            walk(body)

    scr = doc['Screens']['ScreenAcionamentosPlemPrai']
    props['#SCREEN#'] = dict(scr.get('Properties', {}) or {})
    ordem.append('#SCREEN#')
    walk(scr)
    return props, ordem


def guarda_layout(src_text, out_text):
    """Prova que nada além das mudanças declaradas foi tocado."""
    a, ordem_a = arvore(src_text)
    b, ordem_b = arvore(out_text)
    if ordem_a != ordem_b:
        die('a árvore de controles mudou (ordem/quantidade) — layout afetado')
    vistos = set()
    for name in a:
        pa, pb = a[name], b[name]
        for prop in set(pa) | set(pb):
            va, vb = pa.get(prop, '\0AUSENTE'), pb.get(prop, '\0AUSENTE')
            if va == vb:
                continue
            if va == '\0AUSENTE' and prop in ADDABLE:
                continue          # propriedade de performance acrescentada
            if (name, prop) in EXPECTED_CHANGES:
                vistos.add((name, prop))
                continue
            die('LAYOUT ALTERADO em %s.%s — mudança não declarada' % (name, prop))
    faltando = EXPECTED_CHANGES - vistos
    if faltando:
        die('mudanças declaradas que não ocorreram: %s' % sorted(faltando))
    print('  trava de layout: OK (%d propriedades alteradas, todas declaradas)'
          % len(vistos))


def validar(src_text, out_text):
    if not out_text.startswith(
            'Screens:\n  ScreenAcionamentosPlemPrai:\n    Properties:'):
        die('estrutura raiz inválida')

    nomes = [n.strip("'") for n in re.findall(
        r"^\s*- ('?[A-Za-z][A-Za-z0-9_ ']*)'?:$", out_text, re.M)]
    dup = sorted({n for n in nomes if nomes.count(n) > 1})
    if dup:
        die('nomes duplicados: %s' % ', '.join(dup))

    for pat, msg in [(r'^\s*Overflow:', 'Overflow:'),
                     (r'%DATACARD_', 'placeholder %DATACARD_')]:
        if re.search(pat, out_text, re.M):
            die('%s proibido' % msg)

    # C6: ThisRecord.<col> dentro de ForAll(Distinct(...)).
    # Distinct() devolve UMA coluna chamada 'Value'. Qualquer outro nome não
    # existe nesse escopo: dentro de um LookUp o ThisRecord religa ao escopo
    # interno, a condição vira sempre verdadeira e o LookUp devolve o PRIMEIRO
    # registro em toda iteração. Correto: 'As <alias>' + alias.Value, ou
    # ThisRecord.Value direto.
    for m in re.finditer(r'ForAll\(\s*Distinct\(', out_text):
        i, prof = m.end() - 1, 0
        for j in range(i, min(i + 4000, len(out_text))):
            if out_text[j] == '(':
                prof += 1
            elif out_text[j] == ')':
                prof -= 1
                if prof == 0:
                    corpo = out_text[i:j]
                    break
        else:
            continue
        ruim = [c for c in re.findall(r'ThisRecord\.(\w+)', corpo)
                if c != 'Value']
        if ruim:
            die('ThisRecord.%s dentro de ForAll(Distinct(...)) — Distinct só '
                'tem a coluna Value; use "As <alias>" (bug C6)' % ruim[0])

    # C6: ClearCollect não pode ler a própria coleção que está limpando
    for m in re.finditer(r'ClearCollect\(\s*(\w+)\s*,(.{0,600}?)\n\s*\);',
                         out_text, re.S):
        alvo, corpo = m.group(1), m.group(2)
        if re.search(r'\b%s\b' % re.escape(alvo), corpo):
            die('ClearCollect(%s, ...) lê a própria coleção — use coleção '
                'temporária (bug C6)' % alvo)

    # PA2108: nenhuma propriedade nova fora do que o export já comprova
    def control_props(blob):
        out = {}
        for m in re.finditer(r'^(\s*)Control: (\S+)\n', blob, re.M):
            ind, ctl = len(m.group(1)), m.group(2)
            for ln in blob[m.end():].split('\n'):
                if ln.strip() and indent_of(ln) < ind:
                    break
                pm = re.match(r'^\s{%d}([A-Za-z][A-Za-z0-9_]*):' % (ind + 2), ln)
                if pm:
                    out.setdefault(ctl, set()).add(pm.group(1))
        return out

    proven = control_props(src_text)
    for ctl, ps in control_props(out_text).items():
        unknown = ps - proven.get(ctl, set()) - ADDABLE
        if unknown:
            die('propriedade não comprovada em %s: %s (risco de PA2108)'
                % (ctl, ', '.join(sorted(unknown))))

    # nenhuma referência a controle inexistente nas fórmulas que reescrevi
    definidos = set(nomes)
    for ref in ['GalleryAtividadesLancadas', 'Function_consultarAtividades',
                'TextInputCanvas3', 'TextInput1', 'ComboboxCanvasAeroSelectCadEqp',
                'ComboboxCanvasAeroSelectCadFluxo']:
        if ref not in definidos:
            die('controle referenciado não existe: %s' % ref)

    # a flag morta não pode sobrar em nenhum lugar que a ligue
    if re.search(r'var_visibleAcionamentoPRAI: true', out_text):
        die('var_visibleAcionamentoPRAI (flag sem leitor) ainda é ligada')

    guarda_layout(src_text, out_text)


def main():
    with open(SRC, encoding='utf-8') as f:
        src = f.read()

    text = src
    for label, old, new, count in PATCHES:
        got = text.count(old)
        if got != count:
            die('patch "%s" casou %d vez(es), esperado %d' % (label, got, count))
        text = text.replace(old, new)
    print('  %d patches de fórmula aplicados' % len(PATCHES))

    text = aplicar_mecanicas(text)
    validar(src, text)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(text)
    print('OK: %s (%d linhas, sha256 %s)'
          % (os.path.basename(OUT), text.count('\n'),
             hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]))


if __name__ == '__main__':
    main()
