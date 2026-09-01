#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refatora as mensagens de Teams, as validações e as travas da tela PLEM/PRAI.

  fonte : REA/ScreenAcionamentosNewPlemPrai.pa.yaml   (export do Studio, intocado)
  saída : REA/ScreenAcionamentosPlemPraiV2.pa.yaml    (colar em Exibição de código)

Continua o trabalho de REA/otimizar_tela_plem_prai.py (performance/lógica, já
aplicado e reexportado). Aqui o escopo é comunicação + robustez:

MENSAGENS (ver PADRAO_MENSAGENS_TEAMS.md)
  M1  As 9 chamadas de EnviarAtividadeparachatteams passam a mandar DADOS
      (Detalhe, ID_chat, Tipo, Ator) em vez de uma frase pronta. Quem monta a
      mensagem agora é o fluxo — formato único, com hora e hierarquia visual.
  M2  O texto gravado em tbl_atividadesPlemPrai.Atividade segue o mesmo padrão,
      sem emoji: "<RÓTULO> · <Ator> · <Detalhe>".
  M3  O encerramento do acionamento passa a ser publicado no chat (antes o chat
      simplesmente parava, sem ninguém saber que acabou).

CORREÇÕES
  C1  **Deduplicação de participantes quebrada.** `LookUp(col; Email =
      ThisRecord.Email)` compara a linha do LookUp com ela mesma: a condição é
      sempre verdadeira, o LookUp devolve sempre o 1º contato e a coleção vira
      N cópias dele. Resultado observado no Teams: "Notificado via Flow"
      repetido para a mesma pessoa e ninguém mais avisado. Agora usa
      `Distinct(...) As EMAIL_UNICO` + coleção intermediária.
  C2  "VALIDA PARTICIPANTES" testava CountRows depois de já ter inserido o
      operador na coleção — nunca dava 0, ou seja, nunca validava nada. Agora
      ignora o operador. E, ao abortar, fecha o overlay de carregamento
      (antes o app ficava preso no spinner para sempre).
  C3  LOG FINALIZAÇÃO gravava `ID_chat: varChatID`, variável global que só
      existe na sessão que criou o acionamento — quem finalizava depois
      gravava chat em branco. Passa a usar o ID_chat do próprio registro.
      Também corrige "ás" -> hora formatada e passa a gravar Hora/Ativo.
  C4  Botão "Não vai comparecer" postava em `ThisItem.ID_chat` (podia estar em
      branco) e gravava Acao com o nível da entidade. Agora usa o chat do
      acionamento e Acao "NAO COMPARECERA".
  C5  Exclusão de vítima lia `ThisItem` DEPOIS do `Remove()` e não gravava log.
      Agora captura os dados antes, grava o log e publica no chat.
  C6  Vítima alterada era registrada com Acao "REGISTRO DE VÍTIMA".
  C7  Operador sem e-mail válido não entra mais na lista de participantes
      (e-mail em branco fazia o CreateChat do Teams falhar inteiro).

TRAVAS / VALIDAÇÕES
  V1  Trava de reentrância `var_ocupadoDesde` nos 8 pontos que chamam fluxo ou
      gravam vários registros. O 2º clique é recusado com aviso enquanto o 1º
      roda, e a trava se auto-limpa por tempo (30s / 120s no acionamento), para
      nunca deixar a tela travada se algo falhar no meio.
  V2  `OnFailure` nos formulários de ocorrência e de vítima: avisa o erro,
      fecha o overlay e solta a trava (antes um erro de gravação deixava o
      spinner girando).
  V3  Nenhuma chamada ao Teams é feita com ID_chat em branco; o usuário recebe
      aviso de que o registro foi salvo mas não foi publicado.
  V4  Atividade manual exige texto.
  V5  OnVisible da tela limpa a trava e o overlay ao entrar.

Rodar duas vezes e conferir que o hash não muda.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'ScreenAcionamentosNewPlemPrai.pa.yaml')
OUT = os.path.join(HERE, 'ScreenAcionamentosPlemPraiV2.pa.yaml')

AVISO_OCUPADO = 'Aguarde: a ação anterior ainda está sendo processada.'

PATCHES = []


def P(rotulo, velho, novo, n=1):
    PATCHES.append((rotulo, velho, novo, n))


# ============================================================ V5  OnVisible
P('V5 OnVisible limpa trava e overlay',
  '''                var_visibleAcionar: false,
                var_emergenciaSelect: "",''',
  '''                var_visibleAcionar: false,
                // trava de reentrância dos botões que chamam fluxo (V1) —
                // sempre limpa ao entrar na tela, para não abrir travada
                var_ocupadoDesde: Blank(),
                var_visibleConfigFluxo: false,
                var_emergenciaSelect: "",''')

# ================================================= C1  dedup de participantes
P('C1 dedup de participantes (LookUp tautológico)',
  '''                                                          Collect(
                                                              col_emailsCcrFilter,
                                                              {
                                                                  ID_contato: 0,
                                                                  ID_entidade: 0,
                                                                  Email: varEmailUser,
                                                                  Nome: varNomeUser,
                                                                  Nivel: "OPERADOR"
                                                              }
                                                          );
                                                          // REMOVE DUPLICADOS PELO EMAIL
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
                                                          );''',
  '''                                                          // C7 - operador só entra se tiver e-mail válido
                                                          If(
                                                              !IsBlank(varEmailUser) && "@" in varEmailUser,
                                                              Collect(
                                                                  col_emailsCcrFilter,
                                                                  {
                                                                      ID_contato: 0,
                                                                      ID_entidade: 0,
                                                                      Email: Lower(Trim(varEmailUser)),
                                                                      Nome: varNomeUser,
                                                                      Nivel: "OPERADOR"
                                                                  }
                                                              )
                                                          );
                                                          // C1 - REMOVE DUPLICADOS PELO EMAIL
                                                          // A versão anterior comparava o e-mail da linha com ele mesmo
                                                          // dentro do LookUp (o escopo interno vencia o externo), então a
                                                          // condição era sempre verdadeira, o LookUp devolvia sempre o 1º
                                                          // contato e a coleção virava N cópias dele. Era isso que repetia
                                                          // "Notificado via Flow" para a mesma pessoa e deixava os demais
                                                          // participantes sem aviso nenhum.
                                                          ClearCollect(
                                                              col_emailsUnicos,
                                                              ForAll(
                                                                  Distinct(
                                                                      col_emailsCcrFilter,
                                                                      Lower(Trim(Email))
                                                                  ) As EMAIL_UNICO,
                                                                  LookUp(
                                                                      col_emailsCcrFilter,
                                                                      Lower(Trim(Email)) = EMAIL_UNICO.Value
                                                                  )
                                                              )
                                                          );
                                                          Clear(col_emailsCcrFilter);
                                                          Collect(
                                                              col_emailsCcrFilter,
                                                              col_emailsUnicos
                                                          );''')

# ============================================== C2  valida participantes real
P('C2 valida participantes ignorando o operador + fecha overlay',
  '''                                                          If(
                                                              CountRows(col_emailsCcrFilter) = 0,
                                                              Notify(
                                                                  "Nenhum participante encontrado para acionamento.",
                                                                  NotificationType.Error
                                                              ),''',
  '''                                                          If(
                                                              CountRows(
                                                                  Filter(
                                                                      col_emailsCcrFilter,
                                                                      Nivel <> "OPERADOR"
                                                                  )
                                                              ) = 0,
                                                              // C2 - antes o teste era CountRows(col) = 0, mas o operador já
                                                              // tinha sido inserido acima: nunca dava 0 e a validação era
                                                              // letra morta. E, ao abortar, o overlay de carregamento ficava
                                                              // aberto para sempre (tela travada).
                                                              Notify(
                                                                  "Nenhum participante encontrado para esta emergência neste aeroporto. Revise o fluxograma de acionamento antes de iniciar.",
                                                                  NotificationType.Error,
                                                                  8000
                                                              );
                                                              UpdateContext(
                                                                  {
                                                                      var_visibleConfigFluxo: false,
                                                                      var_ocupadoDesde: Blank()
                                                                  }
                                                              ),''')

# ================================================ variável de retorno do chat
P('C3a nome da variável de retorno do fluxo de chat',
  '''                                                              Set(
                                                                  ID_chat,
                                                                  \'CriarchatdeacionamentosPLEM/PRAI\'.Run(''',
  '''                                                              Set(
                                                                  var_retornoFluxoChat,
                                                                  \'CriarchatdeacionamentosPLEM/PRAI\'.Run(''')

P('C3b varChatID com Trim',
  '''                                                              Set(
                                                                  varChatID,
                                                                  ID_chat.chat
                                                              );''',
  '''                                                              Set(
                                                                  varChatID,
                                                                  Trim(var_retornoFluxoChat.chat)
                                                              );''')

# ==================================================== M2  logs padronizados
P('M2 log de criação no padrão',
  '''                                                                      Acao: "CRIAÇÃO",
                                                                      Atividade: "Criação do Acionamento PLEM > " & _registro.Ambiente & " > " & _aeroporto & " > devido a emergência: " & _registro.Emergencia,''',
  '''                                                                      Acao: "CRIAÇÃO",
                                                                      Atividade: "ACIONAMENTO ABERTO · " & _aeroporto & " — " & _registro.Emergencia & " · " & _registro.Ambiente,''')

P('M2 log de notificação no padrão',
  '''                                                                          Atividade: LookUp(
                                                                              tbl_FluxogramaAcionamentos,
                                                                              ID = PARTICIPANTE.ID_entidade
                                                                          ).Titulo & " > " & PARTICIPANTE.Nome & " > Notificado via Flow",''',
  '''                                                                          Atividade: "NOTIFICADO · " & Coalesce(
                                                                              LookUp(
                                                                                  tbl_FluxogramaAcionamentos,
                                                                                  ID = PARTICIPANTE.ID_entidade
                                                                              ).Titulo,
                                                                              If(
                                                                                  PARTICIPANTE.Nivel = "OPERADOR",
                                                                                  "Operador do acionamento",
                                                                                  "Entidade não identificada"
                                                                              )
                                                                          ) & " — " & PARTICIPANTE.Nome,''')

# ============================================== finaliza UI solta a trava
P('V1 finaliza UI solta a trava',
  '''                                                              UpdateContext(
                                                                  {
                                                                      var_visibleConfigFluxo: false,
                                                                      var_inicarTemp: true,''',
  '''                                                              UpdateContext(
                                                                  {
                                                                      var_visibleConfigFluxo: false,
                                                                      var_ocupadoDesde: Blank(),
                                                                      var_inicarTemp: true,''')

# ================================================ C3/M3  log de finalização
P('C3c/M3 encerramento: chat do registro, hora formatada e aviso no Teams',
  '''                                                          Patch(
                                                              tbl_atividadesPlemPrai,
                                                              Defaults(tbl_atividadesPlemPrai),
                                                              {
                                                                  ID_acionamento: _registro.ID,
                                                                  Acao: "FINALIZAÇÃO",
                                                                  Atividade: "Acionamento PLEM Finalizado ás " & Now(),
                                                                  ID_chat: varChatID
                                                              }
                                                          );
                                                          UpdateContext(
                                                              {
                                                                  var_visibleFormOcorrenciaAcionamento: false,
                                                                  var_visibleFluxogramaAcionamentosReal: false
                                                              }
                                                          );''',
  '''                                                          // C3 - varChatID é global da sessão que CRIOU o acionamento; quem
                                                          // finalizasse depois gravava chat em branco. M3 - o chat também
                                                          // passa a ser avisado do encerramento.
                                                          With(
                                                              {
                                                                  _chatFinal: Coalesce(
                                                                      _registro.ID_chat,
                                                                      var_dadosAcionamento.ID_chat,
                                                                      varChatID
                                                                  )
                                                              },
                                                              Patch(
                                                                  tbl_atividadesPlemPrai,
                                                                  Defaults(tbl_atividadesPlemPrai),
                                                                  {
                                                                      ID_acionamento: _registro.ID,
                                                                      Acao: "FINALIZAÇÃO",
                                                                      Atividade: "ACIONAMENTO ENCERRADO · " & _aeroporto & " — " & _registro.Emergencia,
                                                                      Hora: Now(),
                                                                      Ativo: 1,
                                                                      ID_chat: _chatFinal
                                                                  }
                                                              );
                                                              If(
                                                                  !IsBlank(_chatFinal),
                                                                  EnviarAtividadeparachatteams.Run(
                                                                      "ENCERRADO§" & _aeroporto & " — " & _registro.Emergencia & "§Encerrado por " & varNomeUser & " em " & Text(
                                                                          Now(),
                                                                          DateTimeFormat.ShortDateTime
                                                                      ),
                                                                      _chatFinal
                                                                  )
                                                              )
                                                          );
                                                          UpdateContext(
                                                              {
                                                                  var_visibleFormOcorrenciaAcionamento: false,
                                                                  var_visibleFluxogramaAcionamentosReal: false,
                                                                  var_ocupadoDesde: Blank()
                                                              }
                                                          );''')

# ================================================ V2  OnFailure da ocorrência
P('V2 OnFailure do formulário de ocorrência',
  '''                                                LayoutMinWidth: =0
                                                OnSuccess: |
                                                  =With(''',
  '''                                                LayoutMinWidth: =0
                                                OnFailure: |-
                                                  =Notify(
                                                      "Não foi possível salvar o acionamento: " & Self.Error,
                                                      NotificationType.Error,
                                                      8000
                                                  );
                                                  UpdateContext(
                                                      {
                                                          var_visibleConfigFluxo: false,
                                                          var_ocupadoDesde: Blank()
                                                      }
                                                  )
                                                OnSuccess: |
                                                  =With(''')

# ============================================ V1  trava no botão de acionar
P('V1 trava do botão Iniciar/Finalizar Fluxo',
  '''                                                OnSelect: =SubmitForm(FormOcorrenciaAcionamento)''',
  '''                                                OnSelect: |-
                                                  =// V1 - trava de reentrância: 120s cobrem a criação do chat e a
                                                  // notificação de todos os participantes; passado esse tempo a
                                                  // trava se solta sozinha para nunca deixar o botão morto.
                                                  If(
                                                      !IsBlank(var_ocupadoDesde) && DateDiff(
                                                          var_ocupadoDesde,
                                                          Now(),
                                                          TimeUnit.Seconds
                                                      ) < 120,
                                                      Notify(
                                                          "O acionamento já está sendo processado. Aguarde.",
                                                          NotificationType.Warning,
                                                          3000
                                                      ),
                                                      UpdateContext({var_ocupadoDesde: Now()});
                                                      SubmitForm(FormOcorrenciaAcionamento)
                                                  )''')


# ================= C8  parâmetro em branco derruba a chamada do fluxo
# Gatilho PowerApps V2 recusa Blank() em parâmetro obrigatório: "A função Run
# tem um valor inválido para o parâmetro X - um valor em branco foi passado
# para onde ele não era esperado". Dois campos caíam nisso:
#   text_7 (Entidade) - o operador entra na coleção com ID_entidade = 0, e
#     LookUp(tbl_FluxogramaAcionamentos, ID = 0).Titulo volta branco;
#   text_6 (ID_chat)  - branco sempre que a criação do chat falha, e aí a
#     falha do chat derrubava TAMBÉM a notificação de todos os participantes.
# Agora todo argumento de texto tem um fallback com significado.
P('C8 fallback nos argumentos do fluxo de chat',
  '                                                                      JSON_PARTICIPANTES,\n                                                                      _registro.Emergencia,\n                                                                      _registro.Ambiente,\n                                                                      _registro.Usuario,\n                                                                      _aeroporto,\n                                                                      _registro.Descricao_da_ocorrencia,\n                                                                      _registro.ID\n                                                                  )',
  '                                                                      JSON_PARTICIPANTES,\n                                                                      Coalesce(\n                                                                          _registro.Emergencia,\n                                                                          "Emergência não informada"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          _registro.Ambiente,\n                                                                          "Ambiente Real"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          _registro.Usuario,\n                                                                          varNomeUser,\n                                                                          "-"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          _aeroporto,\n                                                                          varAeroUser,\n                                                                          "-"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          _registro.Descricao_da_ocorrencia,\n                                                                          "(sem descrição informada)"\n                                                                      ),\n                                                                      _registro.ID\n                                                                  )')

P('C8 fallback nos argumentos da notificação por participante',
  '                                                                  EnviarAcionamentocomOpcao.Run(\n                                                                      CONTATO.Email,\n                                                                      _registro.Emergencia,\n                                                                      _registro.Ambiente,\n                                                                      _aeroporto,\n                                                                      _registro.Descricao_da_ocorrencia,\n                                                                      _registro.ID,\n                                                                      varChatID,\n                                                                      CONTATO.Nome,\n                                                                      CONTATO.ID_entidade,\n                                                                      CONTATO.ID_contato,\n                                                                      LookUp(\n                                                                          tbl_FluxogramaAcionamentos,\n                                                                          ID = CONTATO.ID_entidade\n                                                                      ).Titulo\n                                                                  )',
  '                                                                  EnviarAcionamentocomOpcao.Run(\n                                                                      Coalesce(\n                                                                          CONTATO.Email,\n                                                                          "-"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          _registro.Emergencia,\n                                                                          "Emergência não informada"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          _registro.Ambiente,\n                                                                          "Ambiente Real"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          _aeroporto,\n                                                                          varAeroUser,\n                                                                          "-"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          _registro.Descricao_da_ocorrencia,\n                                                                          "(sem descrição informada)"\n                                                                      ),\n                                                                      _registro.ID,\n                                                                      // sem chat criado o fluxo ainda manda o e-mail e pede\n                                                                      // a resposta; só os posts no chat falham, e as ações\n                                                                      // seguintes toleram essa falha\n                                                                      Coalesce(\n                                                                          varChatID,\n                                                                          "-"\n                                                                      ),\n                                                                      Coalesce(\n                                                                          CONTATO.Nome,\n                                                                          CONTATO.Email,\n                                                                          "-"\n                                                                      ),\n                                                                      CONTATO.ID_entidade,\n                                                                      CONTATO.ID_contato,\n                                                                      Coalesce(\n                                                                          LookUp(\n                                                                              tbl_FluxogramaAcionamentos,\n                                                                              ID = CONTATO.ID_entidade\n                                                                          ).Titulo,\n                                                                          If(\n                                                                              CONTATO.Nivel = "OPERADOR",\n                                                                              "Operador do acionamento",\n                                                                              "Entidade não identificada"\n                                                                          )\n                                                                      )\n                                                                  )')

# =========================================================== M1  ButtonChegou
P('M1/V1 ButtonChegou',
  '''                                                                  OnSelect: |
                                                                    =// Atualiza o item atual na tabela, definindo o campo "Ativo" como 1.
                                                                    Patch(
                                                                        tbl_atividadesPlemPrai,
                                                                        ThisItem,
                                                                        {Ativo: 1}
                                                                    );
                                                                    // Verifica se o campo ID_equipamento não está vazio.
                                                                    If(
                                                                        !IsBlank(ThisItem.ID_equipamento),
                                                                        // Insere um novo registro na tabela com informações relacionadas ao equipamento.
                                                                        Patch(
                                                                            tbl_atividadesPlemPrai,
                                                                            Defaults(tbl_atividadesPlemPrai),// Cria um novo registro padrão.
                                                                            {
                                                                                ID_acionamento: ThisItem.ID_acionamento,
                                                                                // Relaciona com acionamento atual.
                                                                    ID_chat: var_dadosAcionamento.ID_chat,
                                                                                // Associa ao ID do chat.
                                                                    ID_equipamento: ThisItem.ID_equipamento,
                                                                                // Registra o equipamento.
                                                                    Acao: "CHEGOU",
                                                                                // Define a ação como "CHEGOU".
                                                                    Atividade: LookUp(// Busca o nome do equipamento para descrever a atividade.
                                                                                    tbl_equipamentosAcionamentos,
                                                                                    ID = ThisItem.ID_equipamento
                                                                                ).Item & " > chegou.",
                                                                                Hora: Now(),
                                                                                // Registra a hora atual.
                                                                    Ativo: 1// Marca como ativo.
                                                                            }
                                                                        );
                                                                        // Envia mensagem para o Teams com o nome do equipamento.
                                                                    EnviarAtividadeparachatteams.Run(
                                                                            LookUp(
                                                                                tbl_equipamentosAcionamentos,
                                                                                ID = ThisItem.ID_equipamento
                                                                            ).Item & " > chegou.",
                                                                            var_dadosAcionamento.ID_chat
                                                                        ),
                                                                        // Insere um registro relacionado a contatos e entidades.
                                                                        Patch(
                                                                            tbl_atividadesPlemPrai,
                                                                            Defaults(tbl_atividadesPlemPrai),// Cria um novo registro padrão.
                                                                            {
                                                                                ID_acionamento: ThisItem.ID_acionamento,
                                                                                // Relaciona com acionamento atual.
                                                                    ID_contato: ThisItem.ID_contato,
                                                                                // Associa ao contato.
                                                                    ID_chat: var_dadosAcionamento.ID_chat,
                                                                                // Relaciona ao ID do chat.
                                                                    ID_entidade: ThisItem.ID_entidade,
                                                                                // Associa à entidade.
                                                                    Acao: "CHEGOU",
                                                                                // Define a ação como "CHEGOU".
                                                                    Atividade: LookUp(// Busca título e nome relacionados à entidade e contato.
                                                                                    tbl_FluxogramaAcionamentos,
                                                                                    ID = ThisItem.ID_entidade
                                                                                ).Titulo & " > " & LookUp(
                                                                                    tbl_EntidadeContatoRelacionamento,
                                                                                    ID_contato = ThisItem.ID_contato
                                                                                ).nome & " > chegou.",
                                                                                Hora: Now(),
                                                                                // Registra a hora atual.
                                                                    Ativo: 1// Marca como ativo.
                                                                            }
                                                                        );
                                                                        // Envia mensagem para o Teams com informações da entidade e do contato.
                                                                    EnviarAtividadeparachatteams.Run(
                                                                            LookUp(
                                                                                tbl_FluxogramaAcionamentos,
                                                                                ID = ThisItem.ID_entidade
                                                                            ).Titulo & " > " & LookUp(
                                                                                tbl_EntidadeContatoRelacionamento,
                                                                                ID_contato = ThisItem.ID_contato
                                                                            ).nome & " > chegou.",
                                                                            var_dadosAcionamento.ID_chat
                                                                        )
                                                                    )''',
  '''                                                                  OnSelect: |
                                                                    =// Confirma a chegada do recurso (equipamento ou pessoa).
                                                                    // V1 - trava de reentrância: recusa o 2º clique enquanto o 1º roda
                                                                    // e se solta sozinha após 30s.
                                                                    If(
                                                                        !IsBlank(var_ocupadoDesde) && DateDiff(
                                                                            var_ocupadoDesde,
                                                                            Now(),
                                                                            TimeUnit.Seconds
                                                                        ) < 30,
                                                                        Notify(
                                                                            "Aguarde: a ação anterior ainda está sendo processada.",
                                                                            NotificationType.Warning,
                                                                            3000
                                                                        ),
                                                                        UpdateContext({var_ocupadoDesde: Now()});
                                                                        With(
                                                                            {
                                                                                _chat: var_dadosAcionamento.ID_chat,
                                                                                _ator: If(
                                                                                    !IsBlank(ThisItem.ID_equipamento),
                                                                                    LookUp(
                                                                                        tbl_equipamentosAcionamentos,
                                                                                        ID = ThisItem.ID_equipamento
                                                                                    ).Item,
                                                                                    LookUp(
                                                                                        tbl_FluxogramaAcionamentos,
                                                                                        ID = ThisItem.ID_entidade
                                                                                    ).Titulo & " — " & LookUp(
                                                                                        tbl_EntidadeContatoRelacionamento,
                                                                                        ID_contato = ThisItem.ID_contato
                                                                                    ).nome
                                                                                )
                                                                            },
                                                                            // fecha a pendência que originou a chegada
                                                                            Patch(
                                                                                tbl_atividadesPlemPrai,
                                                                                ThisItem,
                                                                                {Ativo: 1}
                                                                            );
                                                                            Patch(
                                                                                tbl_atividadesPlemPrai,
                                                                                Defaults(tbl_atividadesPlemPrai),
                                                                                {
                                                                                    ID_acionamento: ThisItem.ID_acionamento,
                                                                                    ID_chat: _chat,
                                                                                    ID_equipamento: ThisItem.ID_equipamento,
                                                                                    ID_contato: ThisItem.ID_contato,
                                                                                    ID_entidade: ThisItem.ID_entidade,
                                                                                    Acao: "CHEGOU",
                                                                                    Atividade: "CHEGOU · " & _ator,
                                                                                    Hora: Now(),
                                                                                    Ativo: 1
                                                                                }
                                                                            );
                                                                            If(
                                                                                IsBlank(_chat),
                                                                                Notify(
                                                                                    "Chegada registrada, mas este acionamento não tem chat do Teams — publique manualmente.",
                                                                                    NotificationType.Warning,
                                                                                    5000
                                                                                ),
                                                                                EnviarAtividadeparachatteams.Run(
                                                                                    "CHEGOU§" & _ator & "§",
                                                                                    _chat
                                                                                )
                                                                            )
                                                                        );
                                                                        UpdateContext({var_ocupadoDesde: Blank()})
                                                                    )''')

# ================================================= C4  ButtonNaoVaiComparecer
P('C4/M1/V1 ButtonNaoVaiComparecer',
  '''                                                                  OnSelect: |-
                                                                    =Patch(
                                                                        tbl_atividadesPlemPrai,
                                                                        ThisItem,
                                                                        {Ativo: 1}
                                                                    );
                                                                    Patch(
                                                                        tbl_atividadesPlemPrai,
                                                                        Defaults(tbl_atividadesPlemPrai),
                                                                        {
                                                                            ID_acionamento: ThisItem.ID_acionamento,
                                                                            ID_entidade: ThisItem.ID_entidade,
                                                                            ID_contato: ThisItem.ID_contato,
                                                                            ID_chat: var_dadosAcionamento.ID_chat,
                                                                            Hora: Now(),
                                                                            Acao: LookUp(
                                                                                tbl_EntidadeContatoRelacionamento,
                                                                                ID_contato = ThisItem.ID_contato,
                                                                                nivel
                                                                            ),
                                                                            Atividade: "Não vai comparecer",
                                                                            Ativo: 1
                                                                        }
                                                                    );
                                                                    EnviarAtividadeparachatteams.Run(
                                                                        ThisItem.Atividade & " Não vai comparecer",
                                                                        ThisItem.ID_chat
                                                                    )''',
  '''                                                                  OnSelect: |-
                                                                    =If(
                                                                        !IsBlank(var_ocupadoDesde) && DateDiff(
                                                                            var_ocupadoDesde,
                                                                            Now(),
                                                                            TimeUnit.Seconds
                                                                        ) < 30,
                                                                        Notify(
                                                                            "Aguarde: a ação anterior ainda está sendo processada.",
                                                                            NotificationType.Warning,
                                                                            3000
                                                                        ),
                                                                        UpdateContext({var_ocupadoDesde: Now()});
                                                                        With(
                                                                            {
                                                                                _chat: var_dadosAcionamento.ID_chat,
                                                                                _ator: LookUp(
                                                                                    tbl_FluxogramaAcionamentos,
                                                                                    ID = ThisItem.ID_entidade
                                                                                ).Titulo & " — " & LookUp(
                                                                                    tbl_EntidadeContatoRelacionamento,
                                                                                    ID_contato = ThisItem.ID_contato
                                                                                ).nome
                                                                            },
                                                                            Patch(
                                                                                tbl_atividadesPlemPrai,
                                                                                ThisItem,
                                                                                {Ativo: 1}
                                                                            );
                                                                            Patch(
                                                                                tbl_atividadesPlemPrai,
                                                                                Defaults(tbl_atividadesPlemPrai),
                                                                                {
                                                                                    ID_acionamento: ThisItem.ID_acionamento,
                                                                                    ID_entidade: ThisItem.ID_entidade,
                                                                                    ID_contato: ThisItem.ID_contato,
                                                                                    ID_chat: _chat,
                                                                                    Hora: Now(),
                                                                                    Acao: "NAO COMPARECERA",
                                                                                    Atividade: "NÃO COMPARECERÁ · " & _ator,
                                                                                    Ativo: 1
                                                                                }
                                                                            );
                                                                            If(
                                                                                !IsBlank(_chat),
                                                                                EnviarAtividadeparachatteams.Run(
                                                                                    "RECUSADO§" & _ator & "§",
                                                                                    _chat
                                                                                )
                                                                            )
                                                                        );
                                                                        UpdateContext({var_ocupadoDesde: Blank()})
                                                                    )''')

# ============================================== M1  equipamento solicitado
P('M1/V1/V3 equipamento solicitado',
  '''                                                      OnSelect: |-
                                                        =EnviarAtividadeparachatteams.Run(
                                                            "EQUIPAMENTO SOLICITADO > " & ThisItem.Item,
                                                            var_dadosAcionamento.ID_chat
                                                        );
                                                        Patch(
                                                            tbl_atividadesPlemPrai,
                                                            Defaults(tbl_atividadesPlemPrai),
                                                            {
                                                                ID_acionamento: var_dadosAcionamento.ID,
                                                                Acao: "ACIONAR",
                                                                //"ACIONAR";
                                                                Atividade: "EQUIPAMENTO SOLICITADO > " & ThisItem.Item,
                                                                Hora: Now(),
                                                                ID_equipamento: ThisItem.ID,
                                                                ID_chat: var_dadosAcionamento.ID_chat
                                                            }
                                                        );
                                                        //Select(Function_consultarAtividades);;
                                                        UpdateContext(
                                                            {
                                                                var_visibleAcionarTelefoneACIONAR: false,
                                                                var_visibleAcionar: false,
                                                                var_visibleListarEquipamentos: false
                                                            }
                                                        )''',
  '''                                                      OnSelect: |-
                                                        =If(
                                                            !IsBlank(var_ocupadoDesde) && DateDiff(
                                                                var_ocupadoDesde,
                                                                Now(),
                                                                TimeUnit.Seconds
                                                            ) < 30,
                                                            Notify(
                                                                "Aguarde: a ação anterior ainda está sendo processada.",
                                                                NotificationType.Warning,
                                                                3000
                                                            ),
                                                            UpdateContext({var_ocupadoDesde: Now()});
                                                            With(
                                                                {_chat: var_dadosAcionamento.ID_chat},
                                                                // grava primeiro; publicar no chat é o efeito, não a fonte
                                                                Patch(
                                                                    tbl_atividadesPlemPrai,
                                                                    Defaults(tbl_atividadesPlemPrai),
                                                                    {
                                                                        ID_acionamento: var_dadosAcionamento.ID,
                                                                        Acao: "ACIONAR",
                                                                        Atividade: "EQUIPAMENTO SOLICITADO · " & ThisItem.Item,
                                                                        Hora: Now(),
                                                                        ID_equipamento: ThisItem.ID,
                                                                        ID_chat: _chat,
                                                                        Ativo: 0
                                                                    }
                                                                );
                                                                If(
                                                                    !IsBlank(_chat),
                                                                    EnviarAtividadeparachatteams.Run(
                                                                        "EQUIPAMENTO§" & ThisItem.Item & "§Retirada: " & ThisItem.Local_de_retirada & " · Prazo: " & ThisItem.Prazo_de_chegada_em_minutos & " min",
                                                                        _chat
                                                                    )
                                                                );
                                                                Notify(
                                                                    "Equipamento solicitado: " & ThisItem.Item,
                                                                    NotificationType.Success,
                                                                    3000
                                                                )
                                                            );
                                                            UpdateContext(
                                                                {
                                                                    var_visibleAcionarTelefoneACIONAR: false,
                                                                    var_visibleAcionar: false,
                                                                    var_visibleListarEquipamentos: false,
                                                                    var_ocupadoDesde: Blank()
                                                                }
                                                            )
                                                        )''')

# ============================================== V4/M1  atividade manual
P('V4/M1/V1 atividade manual',
  '''                                                      );*/
                                                  Patch(
                                                      tbl_atividadesPlemPrai,
                                                      Defaults(tbl_atividadesPlemPrai),
                                                      {
                                                          ID_acionamento: var_dadosAcionamento.ID,
                                                          Acao: "ATIVIDADE MANUAL",
                                                          Atividade: TextInputCanvas2.Value,
                                                          Hora: /*If(
                                                              var_dadosAcionamento.Ambiente = "Ambiente Simulado";
                                                              First(
                                                                  Sort(
                                                                      col_timeBarra;
                                                                      Value;
                                                                      SortOrder.Descending
                                                                  )
                                                              ).Value;*/
                                                  Now(),
                                                          Ativo: 1
                                                      }
                                                  );
                                                  EnviarAtividadeparachatteams.Run(
                                                      "ATIVIDADE MANUAL:  " & TextInputCanvas2.Value,
                                                      var_dadosAcionamento.ID_chat
                                                  );
                                                  //Select(Function_consultarAtividades);;
                                                  Notify(
                                                      "Atividade lançada com sucesso!",
                                                      NotificationType.Success
                                                  );
                                                  Reset(TextInputCanvas2);
                                                  Reset(ToggleNovoAcionamento);
                                                  Reset(TextInputCanvasNomeAcionadoManual);
                                                  UpdateContext({var_visibleLancarAtividade: false});''',
  '''                                                      );*/
                                                  // V4 - exige texto; V1 - trava de reentrância
                                                  If(
                                                      IsBlank(Trim(TextInputCanvas2.Value)),
                                                      Notify(
                                                          "Descreva a atividade antes de enviar.",
                                                          NotificationType.Error,
                                                          3000
                                                      ),
                                                      !IsBlank(var_ocupadoDesde) && DateDiff(
                                                          var_ocupadoDesde,
                                                          Now(),
                                                          TimeUnit.Seconds
                                                      ) < 30,
                                                      Notify(
                                                          "Aguarde: a ação anterior ainda está sendo processada.",
                                                          NotificationType.Warning,
                                                          3000
                                                      ),
                                                      UpdateContext({var_ocupadoDesde: Now()});
                                                      With(
                                                          {
                                                              _chat: var_dadosAcionamento.ID_chat,
                                                              _texto: Substitute(
                                                                  Trim(TextInputCanvas2.Value),
                                                                  "§",
                                                                  "/"
                                                              )
                                                          },
                                                          Patch(
                                                              tbl_atividadesPlemPrai,
                                                              Defaults(tbl_atividadesPlemPrai),
                                                              {
                                                                  ID_acionamento: var_dadosAcionamento.ID,
                                                                  Acao: "ATIVIDADE MANUAL",
                                                                  Atividade: "REGISTRO MANUAL · " & varNomeUser & " · " & _texto,
                                                                  Hora: Now(),
                                                                  ID_chat: _chat,
                                                                  Ativo: 1
                                                              }
                                                          );
                                                          If(
                                                              !IsBlank(_chat),
                                                              EnviarAtividadeparachatteams.Run(
                                                                  "MANUAL§" & varNomeUser & "§" & _texto,
                                                                  _chat
                                                              )
                                                          )
                                                      );
                                                      Notify(
                                                          "Atividade lançada com sucesso!",
                                                          NotificationType.Success,
                                                          3000
                                                      );
                                                      Reset(TextInputCanvas2);
                                                      Reset(ToggleNovoAcionamento);
                                                      Reset(TextInputCanvasNomeAcionadoManual);
                                                      UpdateContext(
                                                          {
                                                              var_visibleLancarAtividade: false,
                                                              var_ocupadoDesde: Blank()
                                                          }
                                                      )
                                                  );''')

# ================================================== M1  "Sim, realizou contato"
P('M1/V1/V3 botão Sim (realizou contato)',
  '''                                                            OnSelect: |-
                                                              =If(
                                                                  var_idAtividade > 0,
                                                                  Patch(
                                                                      tbl_atividadesPlemPrai,
                                                                      First(
                                                                          Filter(
                                                                              tbl_atividadesPlemPrai,
                                                                              ID = var_idAtividade
                                                                          )
                                                                      ),
                                                                      {Ativo: 1}
                                                                  )
                                                              );
                                                              Patch(
                                                                  tbl_atividadesPlemPrai,
                                                                  Defaults(tbl_atividadesPlemPrai),
                                                                  {
                                                                      ID_acionamento: var_dadosAcionamento.ID,
                                                                      ID_entidade: ThisItem.ID_entidade,
                                                                      ID_contato: ThisItem.ID_contato,
                                                                      ID_chat: var_dadosAcionamento.ID_chat,
                                                                      Hora: Now(),
                                                                      Acao: If(
                                                                          var_idAtividade > 0,
                                                                          "ACIONAR_SOBREAVISO",
                                                                          ThisItem.nivel
                                                                      ),
                                                                      Atividade: LookUp(
                                                                          tbl_FluxogramaAcionamentos,
                                                                          ID = ThisItem.ID_entidade
                                                                      ).Titulo & " > " & If(
                                                                          IsBlank(TextInputCanvasContatado.Value),
                                                                          ThisItem.nome,
                                                                          TextInputCanvasContatado.Value
                                                                      ) & " > " & Switch(
                                                                          var_acaoFluxo,
                                                                          "ACIONAR",//Or !IsBlank(var_idAtividade);
                                                                          "foi acionado.",
                                                                          "ACIONAR_SOBREAVISO",
                                                                          "foi acionado.",
                                                                          "SOBREAVISO",//And IsBlank(var_idAtividade);
                                                                          "foi colocado em estado de sobreaviso.",
                                                                          "INFORMAR",// And IsBlank(var_idAtividade);
                                                                          "foi informado."
                                                                      ),
                                                                      Ativo: If(
                                                                          var_acaoFluxo = "INFORMAR",
                                                                          1,
                                                                          0
                                                                      )
                                                                  }
                                                              );
                                                              EnviarAtividadeparachatteams.Run(
                                                                  LookUp(
                                                                      tbl_FluxogramaAcionamentos,
                                                                      ID = ThisItem.ID_entidade
                                                                  ).Titulo & " > " & If(
                                                                      IsBlank(TextInputCanvasContatado.Value),
                                                                      ThisItem.nome,
                                                                      TextInputCanvasContatado.Value
                                                                  ) & " > " & Switch(
                                                                      var_acaoFluxo,
                                                                      "ACIONAR",//Or !IsBlank(var_idAtividade);
                                                                      "foi acionado.",
                                                                      "ACIONAR_SOBREAVISO",
                                                                      "foi acionado.",
                                                                      "SOBREAVISO",//And IsBlank(var_idAtividade);
                                                                      "foi colocado em estado de sobreaviso.",
                                                                      "INFORMAR",// And IsBlank(var_idAtividade);
                                                                      "foi informado."
                                                                  ),
                                                                  var_dadosAcionamento.ID_chat
                                                              );
                                                              UpdateContext(
                                                                  {
                                                                      var_visibleAcionarTelefoneACIONAR: false,
                                                                      var_visibleAcionar: false,
                                                                      var_idAtividade: Blank()
                                                                  }
                                                              );
                                                              //Select(Function_consultarAtividades)''',
  '''                                                            OnSelect: |-
                                                              =If(
                                                                  !IsBlank(var_ocupadoDesde) && DateDiff(
                                                                      var_ocupadoDesde,
                                                                      Now(),
                                                                      TimeUnit.Seconds
                                                                  ) < 30,
                                                                  Notify(
                                                                      "Aguarde: a ação anterior ainda está sendo processada.",
                                                                      NotificationType.Warning,
                                                                      3000
                                                                  ),
                                                                  UpdateContext({var_ocupadoDesde: Now()});
                                                                  With(
                                                                      {
                                                                          _chat: var_dadosAcionamento.ID_chat,
                                                                          _tipo: Switch(
                                                                              var_acaoFluxo,
                                                                              "ACIONAR",
                                                                              "ACIONADO",
                                                                              "ACIONAR_SOBREAVISO",
                                                                              "ACIONADO",
                                                                              "SOBREAVISO",
                                                                              "SOBREAVISO",
                                                                              "INFORMAR",
                                                                              "INFORMADO",
                                                                              "ACIONADO"
                                                                          ),
                                                                          _ator: LookUp(
                                                                              tbl_FluxogramaAcionamentos,
                                                                              ID = ThisItem.ID_entidade
                                                                          ).Titulo & " — " & Substitute(
                                                                              If(
                                                                                  IsBlank(TextInputCanvasContatado.Value),
                                                                                  ThisItem.nome,
                                                                                  TextInputCanvasContatado.Value
                                                                              ),
                                                                              "§",
                                                                              "/"
                                                                          )
                                                                      },
                                                                      If(
                                                                          var_idAtividade > 0,
                                                                          Patch(
                                                                              tbl_atividadesPlemPrai,
                                                                              First(
                                                                                  Filter(
                                                                                      tbl_atividadesPlemPrai,
                                                                                      ID = var_idAtividade
                                                                                  )
                                                                              ),
                                                                              {Ativo: 1}
                                                                          )
                                                                      );
                                                                      Patch(
                                                                          tbl_atividadesPlemPrai,
                                                                          Defaults(tbl_atividadesPlemPrai),
                                                                          {
                                                                              ID_acionamento: var_dadosAcionamento.ID,
                                                                              ID_entidade: ThisItem.ID_entidade,
                                                                              ID_contato: ThisItem.ID_contato,
                                                                              ID_chat: _chat,
                                                                              Hora: Now(),
                                                                              // B4 - Acao vinha de ThisItem.nivel (nível do CONTATO)
                                                                              // enquanto texto e Ativo vinham de var_acaoFluxo (a
                                                                              // coluna clicada): clicar em SOBREAVISO num contato de
                                                                              // nível ACIONAR gravava Acao="ACIONAR" com o texto
                                                                              // "foi colocado em estado de sobreaviso".
                                                                              Acao: If(
                                                                                  var_idAtividade > 0,
                                                                                  "ACIONAR_SOBREAVISO",
                                                                                  Coalesce(
                                                                                      var_acaoFluxo,
                                                                                      ThisItem.nivel
                                                                                  )
                                                                              ),
                                                                              Atividade: _tipo & " · " & _ator,
                                                                              Ativo: If(
                                                                                  var_acaoFluxo = "INFORMAR",
                                                                                  1,
                                                                                  0
                                                                              )
                                                                          }
                                                                      );
                                                                      If(
                                                                          IsBlank(_chat),
                                                                          Notify(
                                                                              "Registro salvo, mas este acionamento não tem chat do Teams — publique manualmente.",
                                                                              NotificationType.Warning,
                                                                              5000
                                                                          ),
                                                                          EnviarAtividadeparachatteams.Run(
                                                                              _tipo & "§" & _ator & "§",
                                                                              _chat
                                                                          )
                                                                      )
                                                                  );
                                                                  UpdateContext(
                                                                      {
                                                                          var_visibleAcionarTelefoneACIONAR: false,
                                                                          var_visibleAcionar: false,
                                                                          var_idAtividade: Blank(),
                                                                          var_ocupadoDesde: Blank()
                                                                      }
                                                                  )
                                                              );''')

# ====================================================== M1  "Não atendeu"
P('M1/V1 botão Não atendeu',
  '''                                                            OnSelect: |
                                                              =If(
                                                                  var_idAtividade > 0,
                                                                  Patch(
                                                                      tbl_atividadesPlemPrai,
                                                                      First(
                                                                          Filter(
                                                                              tbl_atividadesPlemPrai,
                                                                              ID = var_idAtividade
                                                                          )
                                                                      ),
                                                                      {Ativo: 1}
                                                                  )
                                                              );
                                                              Patch(
                                                                  tbl_atividadesPlemPrai,
                                                                  Defaults(tbl_atividadesPlemPrai),
                                                                  {
                                                                      ID_acionamento: var_dadosAcionamento.ID,
                                                                      Acao: "CONTATO_NR",
                                                                      Status: "Contato não realizado",
                                                                      Atividade: LookUp(
                                                                          tbl_FluxogramaAcionamentos,
                                                                          ID = ThisItem.ID_entidade
                                                                      ).Titulo & " > " & If(
                                                                          IsBlank(TextInputCanvasContatado.Value),
                                                                          ThisItem.nome,
                                                                          TextInputCanvasContatado.Value
                                                                      ) & " > contato não realizado",
                                                                      Hora: Now(),
                                                                      ID_contato: ThisItem.ID_contato,
                                                                      ID_entidade: ThisItem.ID_entidade,
                                                                      ID_chat: var_dadosAcionamento.ID_chat
                                                                  }
                                                              );
                                                              EnviarAtividadeparachatteams.Run(
                                                                  LookUp(
                                                                      tbl_FluxogramaAcionamentos,
                                                                      ID = ThisItem.ID_entidade
                                                                  ).Titulo & " > " & If(
                                                                      IsBlank(TextInputCanvasContatado.Value),
                                                                      ThisItem.nome,
                                                                      TextInputCanvasContatado.Value
                                                                  ) & " > contato não realizado",
                                                                  var_dadosAcionamento.ID_chat
                                                              );
                                                              //Select(Function_consultarAtividades);;
                                                              UpdateContext(
                                                                  {
                                                                      var_visibleAcionarTelefoneACIONAR: false,
                                                                      var_visibleAcionar: false
                                                                  }
                                                              );''',
  '''                                                            OnSelect: |
                                                              =If(
                                                                  !IsBlank(var_ocupadoDesde) && DateDiff(
                                                                      var_ocupadoDesde,
                                                                      Now(),
                                                                      TimeUnit.Seconds
                                                                  ) < 30,
                                                                  Notify(
                                                                      "Aguarde: a ação anterior ainda está sendo processada.",
                                                                      NotificationType.Warning,
                                                                      3000
                                                                  ),
                                                                  UpdateContext({var_ocupadoDesde: Now()});
                                                                  With(
                                                                      {
                                                                          _chat: var_dadosAcionamento.ID_chat,
                                                                          _ator: LookUp(
                                                                              tbl_FluxogramaAcionamentos,
                                                                              ID = ThisItem.ID_entidade
                                                                          ).Titulo & " — " & Substitute(
                                                                              If(
                                                                                  IsBlank(TextInputCanvasContatado.Value),
                                                                                  ThisItem.nome,
                                                                                  TextInputCanvasContatado.Value
                                                                              ),
                                                                              "§",
                                                                              "/"
                                                                          )
                                                                      },
                                                                      If(
                                                                          var_idAtividade > 0,
                                                                          Patch(
                                                                              tbl_atividadesPlemPrai,
                                                                              First(
                                                                                  Filter(
                                                                                      tbl_atividadesPlemPrai,
                                                                                      ID = var_idAtividade
                                                                                  )
                                                                              ),
                                                                              {Ativo: 1}
                                                                          )
                                                                      );
                                                                      Patch(
                                                                          tbl_atividadesPlemPrai,
                                                                          Defaults(tbl_atividadesPlemPrai),
                                                                          {
                                                                              ID_acionamento: var_dadosAcionamento.ID,
                                                                              Acao: "CONTATO_NR",
                                                                              Status: "Contato não realizado",
                                                                              Atividade: "CONTATO NÃO REALIZADO · " & _ator,
                                                                              Hora: Now(),
                                                                              ID_contato: ThisItem.ID_contato,
                                                                              ID_entidade: ThisItem.ID_entidade,
                                                                              ID_chat: _chat,
                                                                              Ativo: 0
                                                                          }
                                                                      );
                                                                      If(
                                                                          !IsBlank(_chat),
                                                                          EnviarAtividadeparachatteams.Run(
                                                                              "CONTATO_NR§" & _ator & "§Tentativa de contato sem êxito",
                                                                              _chat
                                                                          )
                                                                      )
                                                                  );
                                                                  UpdateContext(
                                                                      {
                                                                          var_visibleAcionarTelefoneACIONAR: false,
                                                                          var_visibleAcionar: false,
                                                                          var_ocupadoDesde: Blank()
                                                                      }
                                                                  )
                                                              );''')

# ================================================ C6/M1  registro de vítima
P('C6/M1/V2 formulário de vítima (OnFailure + OnSuccess)',
  '''                                                      NumberOfColumns: =4
                                                      OnSuccess: |-
                                                        =Notify(
                                                            "Operação realizada com sucesso!",
                                                            NotificationType.Success,
                                                            3000
                                                        );
                                                        Patch(
                                                            tbl_atividadesPlemPrai,
                                                            Defaults(tbl_atividadesPlemPrai),
                                                            {
                                                                ID_acionamento: var_dadosAcionamento.ID,
                                                                Acao: "REGISTRO DE VÍTIMA",
                                                                Atividade: If(
                                                                    varAcaoVitima = "cad",
                                                                    "REGISTRO DE VÍTIMA > ",
                                                                    "ALTERAÇÃO DE VÍTIMA > "
                                                                ) & Self.LastSubmit.prioridade.Value & " > " & Self.LastSubmit.vitima & " > " & Self.LastSubmit.ambulancia & " > " & Self.LastSubmit.hospital,
                                                                Hora: Now(),
                                                                Ativo: 1,
                                                                ID_chat: var_dadosAcionamento.ID_chat
                                                            }
                                                        );
                                                        EnviarAtividadeparachatteams.Run(
                                                            If(
                                                                varAcaoVitima = "cad",
                                                                "REGISTRO DE VÍTIMA > ",
                                                                "ALTERAÇÃO DE VÍTIMA > "
                                                            ) & Self.LastSubmit.prioridade.Value & " > " & Self.LastSubmit.vitima & " > " & Self.LastSubmit.ambulancia & " > " & Self.LastSubmit.hospital,
                                                            var_dadosAcionamento.ID_chat
                                                        );
                                                        UpdateContext(
                                                            {
                                                                varItemVitima: Blank(),
                                                                varAcaoVitima: Blank()
                                                            }
                                                        );
                                                        ResetForm(Self);
                                                        NewForm(Self)''',
  '''                                                      NumberOfColumns: =4
                                                      OnFailure: |-
                                                        =Notify(
                                                            "Não foi possível salvar o registro da vítima: " & Self.Error,
                                                            NotificationType.Error,
                                                            8000
                                                        );
                                                        UpdateContext({var_ocupadoDesde: Blank()})
                                                      OnSuccess: |-
                                                        =Notify(
                                                            "Operação realizada com sucesso!",
                                                            NotificationType.Success,
                                                            3000
                                                        );
                                                        With(
                                                            {
                                                                _chat: var_dadosAcionamento.ID_chat,
                                                                _novo: varAcaoVitima = "cad",
                                                                _ator: Substitute(
                                                                    Self.LastSubmit.vitima,
                                                                    "§",
                                                                    "/"
                                                                ),
                                                                _detalhe: Substitute(
                                                                    "Prioridade " & Self.LastSubmit.prioridade.Value & " · Ambulância: " & Self.LastSubmit.ambulancia & " · Hospital: " & Self.LastSubmit.hospital,
                                                                    "§",
                                                                    "/"
                                                                )
                                                            },
                                                            Patch(
                                                                tbl_atividadesPlemPrai,
                                                                Defaults(tbl_atividadesPlemPrai),
                                                                {
                                                                    ID_acionamento: var_dadosAcionamento.ID,
                                                                    // C6 - alteração era gravada como "REGISTRO DE VÍTIMA"
                                                                    Acao: If(
                                                                        _novo,
                                                                        "REGISTRO DE VÍTIMA",
                                                                        "ALTERAÇÃO DE VÍTIMA"
                                                                    ),
                                                                    Atividade: If(
                                                                        _novo,
                                                                        "VÍTIMA REGISTRADA · ",
                                                                        "VÍTIMA ATUALIZADA · "
                                                                    ) & _ator & " · " & _detalhe,
                                                                    Hora: Now(),
                                                                    Ativo: 1,
                                                                    ID_chat: _chat
                                                                }
                                                            );
                                                            If(
                                                                !IsBlank(_chat),
                                                                EnviarAtividadeparachatteams.Run(
                                                                    If(
                                                                        _novo,
                                                                        "VITIMA_NOVA",
                                                                        "VITIMA_ALTERADA"
                                                                    ) & "§" & _ator & "§" & _detalhe,
                                                                    _chat
                                                                )
                                                            )
                                                        );
                                                        UpdateContext(
                                                            {
                                                                varItemVitima: Blank(),
                                                                varAcaoVitima: Blank(),
                                                                var_ocupadoDesde: Blank()
                                                            }
                                                        );
                                                        ResetForm(Self);
                                                        NewForm(Self)''')

P('V1 trava do botão Registrar/Alterar vítima',
  '''                                                      OnSelect: |-
                                                        =If(
                                                            IsBlank(varItemVitima),
                                                            UpdateContext({varAcaoVitima: "cad"}),
                                                            UpdateContext({varAcaoVitima: "edit"})
                                                        );
                                                        SubmitForm(FormMetodoStart)''',
  '''                                                      OnSelect: |-
                                                        =If(
                                                            !IsBlank(var_ocupadoDesde) && DateDiff(
                                                                var_ocupadoDesde,
                                                                Now(),
                                                                TimeUnit.Seconds
                                                            ) < 30,
                                                            Notify(
                                                                "Aguarde: a ação anterior ainda está sendo processada.",
                                                                NotificationType.Warning,
                                                                3000
                                                            ),
                                                            UpdateContext(
                                                                {
                                                                    varAcaoVitima: If(
                                                                        IsBlank(varItemVitima),
                                                                        "cad",
                                                                        "edit"
                                                                    ),
                                                                    var_ocupadoDesde: Now()
                                                                }
                                                            );
                                                            SubmitForm(FormMetodoStart)
                                                        )''')

# =================================================== C5  exclusão de vítima
P('C5/M1 exclusão de vítima',
  '''                                                                  OnSelect: |
                                                                    =Remove(
                                                                        tbl_metodoStart,
                                                                        ThisItem
                                                                    );
                                                                    EnviarAtividadeparachatteams.Run(
                                                                        "EXCLUSÃO DE VÍTIMA > " & ThisItem.prioridade.Value & " > " & ThisItem.vitima & " > " & ThisItem.ambulancia & " > " & ThisItem.hospital,
                                                                        var_dadosAcionamento.ID_chat
                                                                    );''',
  '''                                                                  OnSelect: |
                                                                    =// C5 - os dados eram lidos de ThisItem DEPOIS do Remove() e a
                                                                    // exclusão não gerava registro no log. O With captura antes.
                                                                    With(
                                                                        {
                                                                            _chat: var_dadosAcionamento.ID_chat,
                                                                            _ator: Substitute(
                                                                                ThisItem.vitima,
                                                                                "§",
                                                                                "/"
                                                                            ),
                                                                            _detalhe: Substitute(
                                                                                "Prioridade " & ThisItem.prioridade.Value & " · Ambulância: " & ThisItem.ambulancia & " · Hospital: " & ThisItem.hospital,
                                                                                "§",
                                                                                "/"
                                                                            )
                                                                        },
                                                                        Remove(
                                                                            tbl_metodoStart,
                                                                            ThisItem
                                                                        );
                                                                        Patch(
                                                                            tbl_atividadesPlemPrai,
                                                                            Defaults(tbl_atividadesPlemPrai),
                                                                            {
                                                                                ID_acionamento: var_dadosAcionamento.ID,
                                                                                Acao: "EXCLUSÃO DE VÍTIMA",
                                                                                Atividade: "VÍTIMA REMOVIDA · " & _ator & " · " & _detalhe,
                                                                                Hora: Now(),
                                                                                Ativo: 1,
                                                                                ID_chat: _chat
                                                                            }
                                                                        );
                                                                        If(
                                                                            !IsBlank(_chat),
                                                                            EnviarAtividadeparachatteams.Run(
                                                                                "VITIMA_EXCLUIDA§" & _ator & "§" & _detalhe,
                                                                                _chat
                                                                            )
                                                                        )
                                                                    );''')



# ==================== FRENTE C2 - emoji fora da interface ====================
# Pedido do usuário: "evite emoji, use ícones se puder, senão deixe sem".
# Nenhum meio aqui aceita ícone de verdade (o HtmlViewer remove <svg> e
# acrescentar a propriedade Icon a estes controles é risco de PA2108), então
# o emoji sai e fica o rótulo limpo. A seta "⬇" do fluxograma NÃO entra:
# ela é sinal de fluxo entre nós, não emoji decorativo.
P('C2.01 emoji fora de Text: ="Configurar Fluxo - PRAI"&If(!IsBlank',
  '                                                Text: ="⚙️ Configurar Fluxo - PRAI"&If(!IsBlank(var_AeroSelectCadFluxo)," - "&var_AeroSelectCadFluxo)',
  '                                                Text: ="Configurar Fluxo - PRAI"&If(!IsBlank(var_AeroSelectCadFluxo)," - "&var_AeroSelectCadFluxo)')

P('C2.02 emoji fora de "" & var_dadosEmergencia.Titulo',
  '                                                            "⚙️ " & var_dadosEmergencia.Titulo',
  '                                                            "" & var_dadosEmergencia.Titulo')

P('C2.03 emoji fora de Text: ="Deseja realmente excluir?"',
  '                                                      Text: ="⚠️ Deseja realmente excluir?"',
  '                                                      Text: ="Deseja realmente excluir?"')

P('C2.04 emoji fora de Text: ="Nenhum contato registrado..."',
  '                                                Text: ="⚠️ Nenhum contato registrado..."',
  '                                                Text: ="Nenhum contato registrado..."', 2)

P('C2.05 emoji fora de Text: ="Deseja realmente excluir?"',
  '                                                Text: ="⚠️ Deseja realmente excluir?"',
  '                                                Text: ="Deseja realmente excluir?"', 3)

P('C2.06 emoji fora de ="Cadastrar Contatos"',
  '                                                        ="📳 Cadastrar Contatos"',
  '                                                        ="Cadastrar Contatos"')

P('C2.07 emoji fora de Text: ="Deseja realmente excluir?"',
  '                                          Text: ="⚠️ Deseja realmente excluir?"',
  '                                          Text: ="Deseja realmente excluir?"', 2)

P('C2.08 emoji fora de Text: ="Excluir"',
  '                                                            Text: ="❌ Excluir"',
  '                                                            Text: ="Excluir"')

P('C2.09 emoji fora de ="Contatos"',
  '                                                              ="📳 Contatos"',
  '                                                              ="Contatos"', 3)

P('C2.10 emoji fora de ="Editar"',
  '                                                              ="📝 Editar"',
  '                                                              ="Editar"', 7)

P('C2.11 emoji fora de ="Consultar..."',
  '                                                        ="🔍 Consultar..."',
  '                                                        ="Consultar..."')

P('C2.12 emoji fora de "Escolha o tipo de emergência",',
  '                                    "⚠️ Escolha o tipo de emergência",',
  '                                    "Escolha o tipo de emergência",')

P('C2.13 emoji fora de Text: ="Novo"',
  '                                                      Text: ="➕ Novo"',
  '                                                      Text: ="Novo"')

P('C2.14 emoji fora de "Escolha o tipo de ocorrência"',
  '                                    "⚠️ Escolha o tipo de ocorrência"',
  '                                    "Escolha o tipo de ocorrência"')

P('C2.15 emoji fora de ="Consultar..."',
  '                                                  ="🔍 Consultar..."',
  '                                                  ="Consultar..."')

P('C2.16 emoji fora de ="Salvar"',
  '                                                  ="💾 Salvar"',
  '                                                  ="Salvar"')

P('C2.17 emoji fora de Text: ="Excluir"',
  '                                          Text: ="❌ Excluir"',
  '                                          Text: ="Excluir"')

P('C2.18 emoji fora de ="Salvar"',
  '                                            ="💾 Salvar"',
  '                                            ="Salvar"', 2)


# ============ FRENTES B e C - dados, lógica e comunicação (auditoria) ============
# B* = correções de dados/lógica apontadas pela auditoria de 2026-08-24.
# C* = padronização das mensagens Notify (acento correto, exclusão sempre
#      Warning, sucesso específico, erro que diz o que fazer, 3000/5000/8000).
P('B1a iniciar PRAI caía no ramo de finalizar',
  '                                                      If(\n                                                          Self.LastSubmit.Acionamento = "PLEM" && var_acaoFormOcorrenciaAcionamento = "Iniciar",',
  '                                                      If(\n                                                          // B1 - iniciar um acionamento PRAI caía no ramo "else" (o de\n                                                          // finalizar): gravava FINALIZAÇÃO imediata e notificava\n                                                          // "finalizado com sucesso". O início vale para PLEM e PRAI.\n                                                          var_acaoFormOcorrenciaAcionamento = "Iniciar",')

P('B1b protocolo com o tipo do acionamento',
  '{Protocolo: _registro.IATA & "-ACI-PLEM-" & _registro.ID}',
  '{Protocolo: _registro.IATA & "-ACI-" & Coalesce(_registro.Acionamento, "PLEM") & "-" & _registro.ID}')

P('B2 log CRIAÇÃO sem o hack de -1 minuto + ID_emergencia',
  '                                                                      Hora: DateAdd(\n                                                                          Now(),\n                                                                          -1,\n                                                                          TimeUnit.Minutes\n                                                                      ),\n                                                                      ID_chat: varChatID,',
  '                                                                      // B2 - fim do hack de "-1 minuto": este log é gravado antes\n                                                                      // dos NOTIFICADO, então Now() já ordena certo por Hora\n                                                                      Hora: Now(),\n                                                                      ID_emergencia: var_dadosEmergencia.ID,\n                                                                      ID_chat: varChatID,')

P('B3 log NOTIFICADO ganha Ativo e ID_emergencia',
  '                                                                          ID_contato: PARTICIPANTE.ID_contato,\n                                                                          ID_entidade: PARTICIPANTE.ID_entidade,\n                                                                          ID_chat: varChatID',
  '                                                                          ID_contato: PARTICIPANTE.ID_contato,\n                                                                          ID_entidade: PARTICIPANTE.ID_entidade,\n                                                                          ID_emergencia: var_dadosEmergencia.ID,\n                                                                          // B3 - sem Ativo o registro ficava nulo e os testes\n                                                                          // "Ativo = 0" dos botões nunca casavam\n                                                                          Ativo: 0,\n                                                                          ID_chat: varChatID')

P('B5a galeria de atividades: sort delegável + filtro por igualdade exata',
  '                                                      Items: |-\n                                                        =SortByColumns(\n                                                            If(\n                                                                IsBlank(ComboboxCanvas1.Selected.Value),\n                                                                Filter(\n                                                                    tbl_atividadesPlemPrai,\n                                                                    ID_acionamento = var_dadosAcionamento.ID\n                                                                ),\n                                                                Filter(\n                                                                    tbl_atividadesPlemPrai,\n                                                                    StartsWith(\n                                                                        Acao,\n                                                                        ComboboxCanvas1.Selected.Value\n                                                                    ) && ID_acionamento = var_dadosAcionamento.ID\n                                                                )\n                                                            ),\n                                                            "Hora", \n                                                            SortOrder.Descending,\n                                                            "Created", // Coluna de criação para o desempate\n                                                            SortOrder.Descending\n                                                        )',
  '                                                      Items: |-\n                                                        =// B5 - o If externo materializava a tabela e o SortByColumns rodava\n                                                        // em memória sobre a primeira página; e StartsWith fazia o filtro\n                                                        // "ACIONAR" trazer também ACIONAR_SOBREAVISO\n                                                        If(\n                                                            IsBlank(ComboboxCanvas1.Selected.Value),\n                                                            SortByColumns(\n                                                                Filter(\n                                                                    tbl_atividadesPlemPrai,\n                                                                    ID_acionamento = var_dadosAcionamento.ID\n                                                                ),\n                                                                "Hora",\n                                                                SortOrder.Descending,\n                                                                "Created",\n                                                                SortOrder.Descending\n                                                            ),\n                                                            SortByColumns(\n                                                                Filter(\n                                                                    tbl_atividadesPlemPrai,\n                                                                    ID_acionamento = var_dadosAcionamento.ID And Acao = ComboboxCanvas1.Selected.Value\n                                                                ),\n                                                                "Hora",\n                                                                SortOrder.Descending,\n                                                                "Created",\n                                                                SortOrder.Descending\n                                                            )\n                                                        )')

P('B5b filtro de atividades lista todas as ações',
  '                                                            Items: |-\n                                                              =[\n                                                                  "",\n                                                                  "ACIONAR",\n                                                                  "ATIVIDADE MANUAL",\n                                                                  "CHEGOU",\n                                                                  "INFORMAR",\n                                                                  "NOTIFICADO",\n                                                                  "RESPONDEU AO FLOW",\n                                                                  "SOBREAVISO"\n                                                              ]',
  '                                                            Items: |-\n                                                              =[\n                                                                  "",\n                                                                  "ACIONAR",\n                                                                  "ACIONAR_SOBREAVISO",\n                                                                  "ATIVIDADE MANUAL",\n                                                                  "CHEGOU",\n                                                                  "CONTATO_NR",\n                                                                  "CRIAÇÃO",\n                                                                  "FINALIZAÇÃO",\n                                                                  "INFORMAR",\n                                                                  "NAO COMPARECERA",\n                                                                  "NOTIFICADO",\n                                                                  "REGISTRO DE VÍTIMA",\n                                                                  "RESPONDEU AO FLOW",\n                                                                  "SOBREAVISO"\n                                                              ]')

P('B7 excluir/restaurar atividade atualiza a galeria na hora',
  '                                                                  OnSelect: |-\n                                                                    =Patch(\n                                                                        tbl_atividadesPlemPrai,\n                                                                        ThisItem,\n                                                                        {Excluido: !ThisItem.Excluido}\n                                                                    );\n                                                                    //Select(Function_consultarAtividades)',
  '                                                                  OnSelect: |-\n                                                                    =Patch(\n                                                                        tbl_atividadesPlemPrai,\n                                                                        ThisItem,\n                                                                        {Excluido: !ThisItem.Excluido}\n                                                                    );\n                                                                    Select(Function_consultarAtividades)')

P('B8 busca de acionamento tolera texto e mantém a ordenação',
  '                                                  =If(\n                                                      IsBlank(txtBuscarPlemPrai.Text),\n                                                      Sort(\n                                                          Filter(\n                                                              tbl_ocorrenciaAcionamento,\n                                                              Aeroporto = ComboboxCanvasAeroSelectMain.Selected.Value\n                                                          ),\n                                                          ID,\n                                                          SortOrder.Descending\n                                                      ),\n                                                      Filter(\n                                                          tbl_ocorrenciaAcionamento,\n                                                          Aeroporto = ComboboxCanvasAeroSelectMain.Selected.Value And ID = Value(txtBuscarPlemPrai.Text)\n                                                      )\n                                                  )',
  '                                                  =If(\n                                                      IsBlank(txtBuscarPlemPrai.Text),\n                                                      Sort(\n                                                          Filter(\n                                                              tbl_ocorrenciaAcionamento,\n                                                              Aeroporto = ComboboxCanvasAeroSelectMain.Selected.Value\n                                                          ),\n                                                          ID,\n                                                          SortOrder.Descending\n                                                      ),\n                                                      // B8 - texto não numérico estourava o Value(); e o ramo de busca\n                                                      // tinha perdido o Sort\n                                                      !IsMatch(\n                                                          Trim(txtBuscarPlemPrai.Text),\n                                                          "^\\d+$"\n                                                      ),\n                                                      Sort(\n                                                          Filter(\n                                                              tbl_ocorrenciaAcionamento,\n                                                              Aeroporto = ComboboxCanvasAeroSelectMain.Selected.Value\n                                                          ),\n                                                          ID,\n                                                          SortOrder.Descending\n                                                      ),\n                                                      Sort(\n                                                          Filter(\n                                                              tbl_ocorrenciaAcionamento,\n                                                              Aeroporto = ComboboxCanvasAeroSelectMain.Selected.Value And ID = Value(Trim(txtBuscarPlemPrai.Text))\n                                                          ),\n                                                          ID,\n                                                          SortOrder.Descending\n                                                      )\n                                                  )')

P('B9 exclusão de acionamento verifica o limite de delegação',
  '                                                      OnSelect: |-\n                                                        =UpdateContext({var_visibleExcluirAcionamento: false});\n                                                        RemoveIf(\n                                                            tbl_ocorrenciaAcionamento,\n                                                            ID = var_dadosAcionamento.ID\n                                                        );\n                                                        RemoveIf(\n                                                            tbl_atividadesPlemPrai,\n                                                            ID_acionamento = var_dadosAcionamento.ID\n                                                        );\n                                                        Notify(\n                                                            "Registro excluido com sucesso!",\n                                                            NotificationType.Success\n                                                        )',
  '                                                      OnSelect: |-\n                                                        =UpdateContext({var_visibleExcluirAcionamento: false});\n                                                        RemoveIf(\n                                                            tbl_ocorrenciaAcionamento,\n                                                            ID = var_dadosAcionamento.ID\n                                                        );\n                                                        RemoveIf(\n                                                            tbl_atividadesPlemPrai,\n                                                            ID_acionamento = var_dadosAcionamento.ID\n                                                        );\n                                                        // B9 - RemoveIf não é delegável no SharePoint: com muitas\n                                                        // atividades a exclusão pode ser parcial. Verifica e orienta.\n                                                        If(\n                                                            !IsBlank(\n                                                                LookUp(\n                                                                    tbl_atividadesPlemPrai,\n                                                                    ID_acionamento = var_dadosAcionamento.ID\n                                                                )\n                                                            ),\n                                                            Notify(\n                                                                "Exclusão parcial: ainda restam atividades deste acionamento. Exclua novamente para remover o restante.",\n                                                                NotificationType.Warning,\n                                                                8000\n                                                            ),\n                                                            Notify(\n                                                                "Acionamento excluído com sucesso.",\n                                                                NotificationType.Warning,\n                                                                5000\n                                                            )\n                                                        )')

P('B11 PRAI passa a definir aeroporto e modo como o PLEM',
  '                                                              =UpdateContext(\n                                                                  {\n                                                                      var_visibleNovoAcionamento: true,\n                                                                      var_visibleEscolhaAcionamento: false,\n                                                                      var_tipoAcionamento: "PRAI",\n                                                                      var_dadosEmergencia: Blank()\n                                                                  }\n                                                              );',
  '                                                              =UpdateContext(\n                                                                  {\n                                                                      var_acao: "new",\n                                                                      var_visibleNovoAcionamento: true,\n                                                                      var_visibleEscolhaAcionamento: false,\n                                                                      var_tipoAcionamento: "PRAI",\n                                                                      var_aeroSelect: ComboboxCanvasAeroSelectAcionamento.Selected.Value,\n                                                                      var_dadosEmergencia: Blank()\n                                                                  }\n                                                              );')

P('B13 ramo PLEM volta a popular col_emergencias',
  '                                                              );\n                                                              /*\n                                                              ClearCollect(\n                                                                  col_emergencias;\n                                                                  Sort(\n                                                                      Filter(\n                                                                          tbl_Emergencias;\n                                                                          Aeroporto = ComboboxCanvasAeroSelectAcionamento.Selected.Value And Acionamento = var_tipoAcionamento\n                                                                      );\n                                                                      Titulo;\n                                                                      SortOrder.Ascending\n                                                                  )\n                                                              )*/',
  '                                                              );\n                                                              // B13 - só o PRAI populava col_emergencias, e 6 galerias leem\n                                                              // a coleção; o bloco estava comentado em sintaxe pt-BR\n                                                              ClearCollect(\n                                                                  col_emergencias,\n                                                                  Sort(\n                                                                      Filter(\n                                                                          tbl_Emergencias,\n                                                                          Aeroporto = ComboboxCanvasAeroSelectAcionamento.Selected.Value And Acionamento = var_tipoAcionamento\n                                                                      ),\n                                                                      Titulo,\n                                                                      SortOrder.Ascending\n                                                                  )\n                                                              )')

P('B14a card de telefone exibe a coluna que grava (tel_fixo)',
  '                                                      DataField: ="tel_fixo"\n                                                      Default: =ThisItem.tel_principal',
  '                                                      DataField: ="tel_fixo"\n                                                      Default: =ThisItem.tel_fixo')

P('B14b card de telefone reserva exibe a coluna que grava',
  '                                                      DataField: ="tel_cel_institucional"\n                                                      Default: =ThisItem.tel_reserva',
  '                                                      DataField: ="tel_cel_institucional"\n                                                      Default: =ThisItem.tel_cel_institucional')

P('B15a data de término obrigatória ao finalizar',
  '                                                      Required: =false\n                                                      Update: =If(Not IsBlank(DateValue21.SelectedDate), Date(Year(DateValue21.SelectedDate), Month(DateValue21.SelectedDate), Day(DateValue21.SelectedDate)) + Time(Value(HourValue21.Selected.Value), Value(MinuteValue21.Selected.Value), Value(Second(DateValue21.SelectedDate))))',
  '                                                      Required: =var_acaoFormOcorrenciaAcionamento = "Finalizar"\n                                                      Update: =If(Not IsBlank(DateValue21.SelectedDate), Date(Year(DateValue21.SelectedDate), Month(DateValue21.SelectedDate), Day(DateValue21.SelectedDate)) + Time(Value(HourValue21.Selected.Value), Value(MinuteValue21.Selected.Value), Value(Second(DateValue21.SelectedDate))))')

P('B15b relatório final obrigatório ao finalizar',
  '                                                      Required: =false\n                                                      Update: =DataCardValue198.Value',
  '                                                      Required: =var_acaoFormOcorrenciaAcionamento = "Finalizar"\n                                                      Update: =DataCardValue198.Value')

P('B16 OnSuccess do form de equipamento sem Patch morto + OnFailure',
  '                                          OnSuccess: |-\n                                            =Patch(\n                                                col_equipamentosAcionamentos,\n                                                Coalesce(\n                                                    var_dadosEquipamento,\n                                                    Defaults(col_equipamentosAcionamentos)\n                                                ),\n                                                Self.LastSubmit\n                                            );\n                                            UpdateContext({var_visibleFormEquipamento: false})',
  '                                          OnFailure: |-\n                                            =Notify(\n                                                "Não foi possível salvar o equipamento: " & Self.Error,\n                                                NotificationType.Error,\n                                                8000\n                                            )\n                                          OnSuccess: |-\n                                            =// B16 - o Patch antigo gravava numa coleção que a galeria não lê\n                                            // (GalleryEquipamento_1 lê tbl_equipamentosAcionamentos direto)\n                                            UpdateContext({var_visibleFormEquipamento: false});\n                                            Notify(\n                                                "Equipamento salvo com sucesso.",\n                                                NotificationType.Success,\n                                                3000\n                                            )')

P('B17 exclusão de entidade sem re-consulta em corrida com o delete',
  '                                                        Notify(\n                                                            "Entidade excluida com sucesso!",\n                                                            NotificationType.Warning\n                                                        );\n                                                        ClearCollect(\n                                                            col_emergenciaFluxo,\n                                                            Filter(\n                                                                tbl_FluxogramaAcionamentos,\n                                                                Aeroporto = varAeroUser And ID_emergencia = LookUp(\n                                                                    col_emergencias,\n                                                                    Titulo = var_emergenciaSelectFluxo,\n                                                                    ID\n                                                                )\n                                                            )\n                                                        )',
  '                                                        Notify(\n                                                            "Entidade excluída com sucesso.",\n                                                            NotificationType.Warning,\n                                                            5000\n                                                        )\n                                                        // B17 - o ClearCollect re-consultava o SharePoint em corrida com o\n                                                        // RemoveIf (a linha excluída podia reaparecer); o RemoveIf na\n                                                        // coleção, acima, já mantém o espelho local correto', 2)

P('B18a OnFailure no formulário de entidade do fluxograma',
  '                                          NumberOfColumns: =1\n                                          OnSuccess: |-\n                                            =UpdateContext({var_visibleFormFluxograma: false});',
  '                                          NumberOfColumns: =1\n                                          OnFailure: |-\n                                            =Notify(\n                                                "Não foi possível salvar a entidade: " & Self.Error,\n                                                NotificationType.Error,\n                                                8000\n                                            )\n                                          OnSuccess: |-\n                                            =UpdateContext({var_visibleFormFluxograma: false});')

P('B18b OnFailure no formulário de contato da entidade',
  '                                                NumberOfColumns: =1\n                                                OnSuccess: |-\n                                                  =UpdateContext(\n                                                      {\n                                                          var_visibleNovoContatosEntidade: false',
  '                                                NumberOfColumns: =1\n                                                OnFailure: |-\n                                                  =Notify(\n                                                      "Não foi possível salvar o contato: " & Self.Error,\n                                                      NotificationType.Error,\n                                                      8000\n                                                  )\n                                                OnSuccess: |-\n                                                  =UpdateContext(\n                                                      {\n                                                          var_visibleNovoContatosEntidade: false')

P('C1 exclusão de equipamento com acento e duração',
  '                                                              Notify(\n                                                                  "Equipamento excluido com sucesso!",\n                                                                  NotificationType.Warning\n                                                              )',
  '                                                              Notify(\n                                                                  "Equipamento excluído com sucesso.",\n                                                                  NotificationType.Warning,\n                                                                  5000\n                                                              )')

P('C2 "excluida" com acento (ponto restante)',
  '"Entidade excluida com sucesso!",',
  '"Entidade excluída com sucesso.",')

P('C3 aviso de contato já vinculado sem prefixo "Erro:"',
  '                                                            Notify(\n                                                                "Erro: Este contato já está vinculado",\n                                                                NotificationType.Error,\n                                                                4000\n                                                            ),',
  '                                                            Notify(\n                                                                "Este contato já está vinculado a esta entidade.",\n                                                                NotificationType.Error,\n                                                                8000\n                                                            ),')

P('C4 OnFailure do detalhe com orientação',
  '                                          OnFailure: =Notify("Erro! verifique todos os campos.",NotificationType.Error)',
  '                                          OnFailure: =Notify("Não foi possível salvar. Verifique os campos obrigatórios.", NotificationType.Error, 8000)')

P('B12 acionar pela atividade define a entidade do diálogo',
  '                                                                    =UpdateContext(\n                                                                        {\n                                                                            var_visibleAcionar: true,\n                                                                            var_idAtividade: ThisItem.ID,\n                                                                            var_idEntidadeAtividade: ThisItem.ID_entidade,\n                                                                            var_acaoFluxo: "ACIONAR_SOBREAVISO",\n                                                                            var_visibleAcionarTelefoneACIONAR: false,\n                                                                            var_visibleAcionarTelefone: false\n                                                                        }\n                                                                    )',
  '                                                                    =UpdateContext(\n                                                                        {\n                                                                            var_visibleAcionar: true,\n                                                                            var_idAtividade: ThisItem.ID,\n                                                                            var_idEntidadeAtividade: ThisItem.ID_entidade,\n                                                                            // B12 - sem isto a galeria de contatos caía no\n                                                                            // var_acionarEntidade da entidade anterior\n                                                                            var_acionarEntidade: LookUp(\n                                                                                tbl_FluxogramaAcionamentos,\n                                                                                ID = ThisItem.ID_entidade\n                                                                            ),\n                                                                            var_acaoFluxo: "ACIONAR_SOBREAVISO",\n                                                                            var_visibleAcionarTelefoneACIONAR: false,\n                                                                            var_visibleAcionarTelefone: false\n                                                                        }\n                                                                    )')


# ==================== FRENTE D - identidade corporativa no app ====================
P('D5 timeline: chip de status corporativo no HtmlText13',
  '                                                                  HtmlText: |-\n                                                                    =With(\n                                                                        {\n                                                                            _nivel: LookUp(\n                                                                                tbl_FluxogramaAcionamentos,\n                                                                                ID = ThisItem.ID_entidade\n                                                                            ).Nivel.Value,\n                                                                            _hora: TimeValue(ThisItem.Hora)\n                                                                        },\n                                                                        With(\n                                                                            {\n                                                                                _corpo: If(\n                                                                                    !IsBlank(ThisItem.Acao),\n                                                                                    ThisItem.Atividade & Switch(\n                                                                                        true,\n                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "ACIONAR",\n                                                                                        " > foi acionado",\n                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "SOBREAVISO",\n                                                                                        " > foi colocado em estado de sobreaviso",\n                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "INFORMAR",\n                                                                                        " > foi informado"\n                                                                                    )\n                                                                                )\n                                                                            },\n                                                                            If(\n                                                                                ThisItem.Excluido,\n                                                                                "<s><b>" & _hora & "</b><br>" & _corpo & "</s>",\n                                                                                "<b>" & _hora & "</b><br>" & _corpo\n                                                                            )\n                                                                        )\n                                                                    )',
  '                                                                  HtmlText: |-\n                                                                    =With(\n                                                                        {\n                                                                            _nivel: LookUp(\n                                                                                tbl_FluxogramaAcionamentos,\n                                                                                ID = ThisItem.ID_entidade\n                                                                            ).Nivel.Value,\n                                                                            _hora: TimeValue(ThisItem.Hora),\n                                                                            _chipBg: Switch(\n                                                                                ThisItem.Acao,\n                                                                                "ACIONAR", "#B98900",\n                                                                                "ACIONAR_SOBREAVISO", "#B98900",\n                                                                                "RESPONDEU AO FLOW", "#B98900",\n                                                                                "SOBREAVISO", "#C05621",\n                                                                                "INFORMAR", "#155E8F",\n                                                                                "CHEGOU", "#1F7A4D",\n                                                                                "CONTATO_NR", "#A62639",\n                                                                                "NAO COMPARECERA", "#A62639",\n                                                                                "ERRO CHAT", "#A62639",\n                                                                                "NOTIFICADO", "#E8EDF2",\n                                                                                "CRIAÇÃO", "#0B2E4F",\n                                                                                "FINALIZAÇÃO", "#0B2E4F",\n                                                                                "REGISTRO DE VÍTIMA", "#7A4E82",\n                                                                                "ALTERAÇÃO DE VÍTIMA", "#7A4E82",\n                                                                                "EXCLUSÃO DE VÍTIMA", "#7A4E82",\n                                                                                "#5D6B77"\n                                                                            )\n                                                                        },\n                                                                        With(\n                                                                            {\n                                                                                _chipFg: If(\n                                                                                    _chipBg = "#E8EDF2",\n                                                                                    "#22303B",\n                                                                                    "#FFFFFF"\n                                                                                ),\n                                                                                _corpo: If(\n                                                                                    !IsBlank(ThisItem.Acao),\n                                                                                    ThisItem.Atividade & Switch(\n                                                                                        true,\n                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "ACIONAR",\n                                                                                        " > foi acionado",\n                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "SOBREAVISO",\n                                                                                        " > foi colocado em estado de sobreaviso",\n                                                                                        ThisItem.Acao = "RESPONDEU AO FLOW" And _nivel = "INFORMAR",\n                                                                                        " > foi informado"\n                                                                                    )\n                                                                                )\n                                                                            },\n                                                                            "<div style=""font-family: \'Segoe UI\', Arial, sans-serif;"">" &\n                                                                            If(\n                                                                                ThisItem.Excluido,\n                                                                                "<s>",\n                                                                                ""\n                                                                            ) &\n                                                                            "<span style=\'display: inline-block; padding: 1px 8px; border-radius: 9px; background: " & _chipBg & "; color: " & _chipFg & "; font-size: 10px; font-weight: 600; letter-spacing: 0.4px;\'>" & Coalesce(\n                                                                                ThisItem.Acao,\n                                                                                "REGISTRO"\n                                                                            ) & "</span> &nbsp;<b>" & _hora & "</b><br>" & _corpo & If(\n                                                                                ThisItem.Excluido,\n                                                                                "</s>",\n                                                                                ""\n                                                                            ) & "</div>"\n                                                                        )\n                                                                    )')

P('D1 faixa de status do timeline na paleta (todos os valores de Acao)',
  '                                                                  Fill: "=Switch(\\n    true,\\n    ThisItem.Acao = \\"RESPONDEU AO FLOW\\" And LookUp(\\n        tbl_FluxogramaAcionamentos,\\n        ID = ThisItem.ID_entidade\\n    ).Nivel.Value = \\"ACIONAR\\",\\n    RGBA(\\n        255,\\n        255,\\n        0,\\n        1\\n    ),\\n    ThisItem.Acao = \\"RESPONDEU AO FLOW\\" And LookUp(\\n        tbl_FluxogramaAcionamentos,\\n        ID = ThisItem.ID_entidade\\n    ).Nivel.Value = \\"SOBREAVISO\\",\\n    RGBA(\\n        247,\\n        116,\\n        38,\\n        1\\n    ),\\n    ThisItem.Acao = \\"RESPONDEU AO FLOW\\" And LookUp(\\n        tbl_FluxogramaAcionamentos,\\n        ID = ThisItem.ID_entidade\\n    ).Nivel.Value = \\"INFORMAR\\",\\n    RGBA(\\n        56,\\n        96,\\n        178,\\n        1\\n    ),\\n    ThisItem.Acao = \\"CONTATO_NR\\",\\n    Color.Red,\\n    ThisItem.Acao = \\"CHEGOU\\",\\n    RGBA(\\n        52,\\n        152,\\n        47,\\n        1\\n    ),\\n    ThisItem.Acao = \\"ACIONAR\\",\\n    RGBA(\\n        255,\\n        255,\\n        0,\\n        1\\n    ),\\n    ThisItem.Acao = \\"ACIONAR_SOBREAVISO\\",\\n    RGBA(\\n        255,\\n        255,\\n        0,\\n        1\\n    ),\\n    ThisItem.Acao = \\"SOBREAVISO\\",\\n    RGBA(\\n        247,\\n        116,\\n        38,\\n        1\\n    ),\\n    ThisItem.Acao = \\"INFORMAR\\",\\n    RGBA(\\n        56,\\n        96,\\n        178,\\n        1\\n    ),\\n   \\n        RGBA(\\n            0,\\n            0,\\n            0,\\n            0\\n        \\n    )\\n)\\n"',
  '                                                                  Fill: "=Switch(\\n    ThisItem.Acao,\\n    \\"ACIONAR\\",\\n    RGBA(185, 137, 0, 1),\\n    \\"ACIONAR_SOBREAVISO\\",\\n    RGBA(185, 137, 0, 1),\\n    \\"RESPONDEU AO FLOW\\",\\n    RGBA(185, 137, 0, 1),\\n    \\"SOBREAVISO\\",\\n    RGBA(192, 86, 33, 1),\\n    \\"INFORMAR\\",\\n    RGBA(21, 94, 143, 1),\\n    \\"NOTIFICADO\\",\\n    RGBA(200, 211, 220, 1),\\n    \\"CHEGOU\\",\\n    RGBA(31, 122, 77, 1),\\n    \\"CONTATO_NR\\",\\n    RGBA(166, 38, 57, 1),\\n    \\"NAO COMPARECERA\\",\\n    RGBA(166, 38, 57, 1),\\n    \\"SEM RESPOSTA\\",\\n    RGBA(93, 107, 119, 1),\\n    \\"CRIAÇÃO\\",\\n    RGBA(11, 46, 79, 1),\\n    \\"FINALIZAÇÃO\\",\\n    RGBA(11, 46, 79, 1),\\n    \\"CHAT\\",\\n    RGBA(93, 107, 119, 1),\\n    \\"ERRO CHAT\\",\\n    RGBA(166, 38, 57, 1),\\n    \\"ATIVIDADE MANUAL\\",\\n    RGBA(93, 107, 119, 1),\\n    \\"REGISTRO DE VÍTIMA\\",\\n    RGBA(122, 78, 130, 1),\\n    \\"ALTERAÇÃO DE VÍTIMA\\",\\n    RGBA(122, 78, 130, 1),\\n    \\"EXCLUSÃO DE VÍTIMA\\",\\n    RGBA(122, 78, 130, 1),\\n    RGBA(223, 229, 234, 1)\\n)\\n"')

P('D2 CTA Acionar: azul de ação + texto branco (Switch sem default devolvia Blank)',
  '                                                                  Color: |-\n                                                                    =Switch(\n                                                                        ThisItem.Acao,\n                                                                        "SOBREAVISO",\n                                                                        Color.Black,\n                                                                        "INFORMAR",\n                                                                        Color.White\n                                                                    )\n                                                                  Fill: "=\\n    RGBA(\\n        255,\\n        255,\\n        0,\\n        1\\n    )\\n   "',
  '                                                                  Color: =RGBA(255, 255, 255, 1)\n                                                                  Fill: =ColorValue("#155E8F")')

P('D3 status de equipamento na paleta (Label122)',
  '                                                      Color: =If(ThisItem.Status.Value = "Disponível", RGBA(52, 152, 47, 1), Color.Red)',
  '                                                      Color: =If(ThisItem.Status.Value = "Disponível", ColorValue("#1F7A4D"), ColorValue("#A62639"))')

P('D4 Title3_9 ganha a mesma cor de status do Label122',
  '                                                            FillPortions: =1\n                                                            Height: =Self.Size * 1.8\n                                                            OnSelect: =\n                                                            Size: =12\n                                                            Text: =ThisItem.Status.Value\n                                                            Width: =110\n                                                            X: =996\n                                                            Y: =12',
  '                                                            FillPortions: =1\n                                                            Height: =Self.Size * 1.8\n                                                            OnSelect: =\n                                                            Color: =If(ThisItem.Status.Value = "Disponível", ColorValue("#1F7A4D"), ColorValue("#A62639"))\n                                                            Size: =12\n                                                            Text: =ThisItem.Status.Value\n                                                            Width: =110\n                                                            X: =996\n                                                            Y: =12')

P('D6 cartão de equipamento sem <font> legado',
  '                                                        ="<font color=\'#0b3375\'><b>Item: "&ThisItem.Item &"</b></font><br>QTD: "&ThisItem.Quantidade&"<br>Local: "&ThisItem.Local_de_retirada&"<br>Prazo de chegada: "&ThisItem.Prazo_de_chegada_em_minutos&" min"',
  '                                                        ="<div style=""font-family: \'Segoe UI\', Arial, sans-serif; line-height: 1.5;""><div style=\'font-size: 13px; font-weight: 600; color: #0B2E4F;\'>" & ThisItem.Item & "</div><span style=\'color: #5D6B77;\'>Qtd </span><b style=\'color: #22303B;\'>" & ThisItem.Quantidade & "</b><span style=\'color: #5D6B77;\'> &nbsp;&middot;&nbsp; Local </span><b style=\'color: #22303B;\'>" & ThisItem.Local_de_retirada & "</b><span style=\'color: #5D6B77;\'> &nbsp;&middot;&nbsp; Chegada </span><b style=\'color: #22303B;\'>" & ThisItem.Prazo_de_chegada_em_minutos & " min</b></div>"')

P('D7 script de ligação: paleta + MAYDAY/PANPAN por conteúdo (B19)',
  '                                                      {\n                                                          _ehAeronave: var_dadosEmergencia.Titulo in ["MAYDAY - CONDIÇÃO DE SOCORRO", "PANPAN - CONDIÇÃO DE URGÊNCIA"],\n                                                          _fonte: "font-family: \'Segoe UI\', Arial, sans-serif;",\n                                                          _azul: "#0B2E4F",\n                                                          _vermelho: "#C8102E",\n                                                          _texto: "#1F2937",\n                                                          _cinza: "#6B7280",\n                                                          _fundo: "#F3F5F9",\n                                                          _borda: "#E1E5EB",\n                                                          _rotulo: "font-size: 11px; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; color: #6B7280;",\n                                                          _celRotulo: "padding: 8px 10px; border-bottom: 1px solid #E1E5EB; color: #6B7280; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; width: 40%;",\n                                                          _celValor: "padding: 8px 10px; border-bottom: 1px solid #E1E5EB; color: #1F2937; font-size: 14px; font-weight: 600;"\n                                                      },',
  '                                                      {\n                                                          // B19 - por conteúdo: reconhece também títulos com sufixo ("- TESTE")\n                                                          _ehAeronave: "MAYDAY" in Upper(Coalesce(var_dadosEmergencia.Titulo, "")) || "PANPAN" in Upper(Coalesce(var_dadosEmergencia.Titulo, "")),\n                                                          _fonte: "font-family: \'Segoe UI\', Arial, sans-serif;",\n                                                          _azul: "#0B2E4F",\n                                                          _vermelho: "#A62639",\n                                                          _texto: "#22303B",\n                                                          _cinza: "#5D6B77",\n                                                          _fundo: "#F5F7F9",\n                                                          _borda: "#DFE5EA",\n                                                          _rotulo: "font-size: 11px; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; color: #5D6B77;",\n                                                          _celRotulo: "padding: 8px 10px; border-bottom: 1px solid #DFE5EA; color: #5D6B77; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; width: 40%;",\n                                                          _celValor: "padding: 8px 10px; border-bottom: 1px solid #DFE5EA; color: #22303B; font-size: 14px; font-weight: 600;"\n                                                      },')

P('D8 cartão de contato: paleta + telefone sem dingbat',
  '                                                                _chip: "display: inline-block; background: #F3F5F9; border: 1px solid #E1E5EB; border-radius: 4px; padding: 3px 10px; font-size: 15px; color: #1F2937; margin: 4px 6px 0 0;"\n                                                            },\n                                                            "<div style=""font-family: \'Segoe UI\', Arial, sans-serif; line-height: 1.4;"">" &\n                                                                "<div style=\'font-size: 20px; font-weight: 600; color: #0B2E4F;\'>" & ThisItem.nome & "</div>" &\n                                                                "<div style=\'font-size: 14px; letter-spacing: 1.5px; text-transform: uppercase; color: #6B7280; margin-top: 2px;\'>" & _contato.nome_orgao & "</div>" &\n                                                                "<span style=\'" & _chip & "\'>&#9742;&nbsp; " & _contato.tel_principal & "</span>" &\n                                                                If(\n                                                                    !IsBlank(_contato.tel_reserva),\n                                                                    "<span style=\'" & _chip & "\'>Reserva: " & _contato.tel_reserva & "</span>"\n                                                                ) &',
  '                                                                _chip: "display: inline-block; background: #F5F7F9; border: 1px solid #DFE5EA; border-radius: 4px; padding: 3px 10px; font-size: 15px; color: #22303B; margin: 4px 6px 0 0;"\n                                                            },\n                                                            "<div style=""font-family: \'Segoe UI\', Arial, sans-serif; line-height: 1.4;"">" &\n                                                                "<div style=\'font-size: 20px; font-weight: 600; color: #0B2E4F;\'>" & ThisItem.nome & "</div>" &\n                                                                "<div style=\'font-size: 14px; letter-spacing: 1.5px; text-transform: uppercase; color: #5D6B77; margin-top: 2px;\'>" & _contato.nome_orgao & "</div>" &\n                                                                "<span style=\'" & _chip & "\'>Tel&nbsp;" & _contato.tel_principal & "</span>" &\n                                                                If(\n                                                                    !IsBlank(_contato.tel_reserva),\n                                                                    "<span style=\'" & _chip & "\'>Reserva: " & _contato.tel_reserva & "</span>"\n                                                                ) &')

# ATENÇÃO ao predicado de exclusão: tem que ser "Excluido <> true", NUNCA
# "!Excluido". A coluna Excluido é Sim/Não do SharePoint e NENHUM dos 19
# Patch que criam atividade a preenche — ou seja, ela nasce NULA. Delegado ao
# SharePoint, "!Excluido" vira "Excluido eq false", e no SharePoint NULL não
# casa com eq false: a consulta voltava vazia e TODAS as pílulas ficavam
# brancas. "Excluido ne true" casa com NULL e com false.
P('B6/D9 pílula ACIONAR: cores da legenda + ignora atividade excluída',
  '                                                                        Fill: |-\n                                                                          =With(\n                                                                              {\n                                                                                  ACAO: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai,\n                                                                                              ID_acionamento = var_dadosAcionamento.ID And ID_entidade = ThisItem.ID\n                                                                                          ),\n                                                                                          ID,\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Acao\n                                                                              },\n                                                                              Switch(\n                                                                                  true,\n                                                                                  ACAO = "NOTIFICADO",\n                                                                                  RGBA(\n                                                                                      253,\n                                                                                      207,\n                                                                                      180,\n                                                                                      0.7\n                                                                                  ),\n                                                                                  ACAO = "ACIONAR",\n                                                                                  RGBA(\n                                                                                      255,\n                                                                                      255,\n                                                                                      0,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "RESPONDEU AO FLOW",\n                                                                                  RGBA(\n                                                                                      255,\n                                                                                      255,\n                                                                                      0,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "CHEGOU",\n                                                                                  RGBA(\n                                                                                      52,\n                                                                                      152,\n                                                                                      47,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "CONTATO_NR",\n                                                                                  Color.Red,\n                                                                                  Color.White\n                                                                              )\n                                                                          )',
  '                                                                        Fill: |-\n                                                                          =With(\n                                                                              {\n                                                                                  // Consulta direta ao SharePoint. A versão com coleção dependia de\n                                                                                  // Select(Function_consultarAtividades), e esse control fica dentro\n                                                                                  // de um container com Visible = var_acao <> "view": no modo\n                                                                                  // Visualizar ele some, o Select vira no-op e as pílulas ficavam\n                                                                                  // sem cor nenhuma.\n                                                                                  ACAO: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai,\n                                                                                              ID_acionamento = var_dadosAcionamento.ID And ID_entidade = ThisItem.ID And Excluido <> true\n                                                                                          ),\n                                                                                          ID,\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Acao\n                                                                              },\n                                                                              Switch(\n                                                                                  true,\n                                                                                  ACAO = "NOTIFICADO",\n                                                                                  RGBA(232, 237, 242, 1),\n                                                                                  ACAO = "ACIONAR",\n                                                                                  RGBA(232, 194, 94, 1),\n                                                                                  ACAO = "RESPONDEU AO FLOW",\n                                                                                  RGBA(232, 194, 94, 1),\n                                                                                  ACAO = "CHEGOU",\n                                                                                  RGBA(107, 191, 149, 1),\n                                                                                  ACAO = "CONTATO_NR",\n                                                                                  RGBA(224, 142, 156, 1),\n                                                                                  ACAO = "NAO COMPARECERA",\n                                                                                  RGBA(224, 142, 156, 1),\n                                                                                  Color.White\n                                                                              )\n                                                                          )')

P('B6/D10 pílula SOBREAVISO: cores da legenda + ignora excluída + remove bloco morto',
  '                                                                        Fill: |-\n                                                                          =With(\n                                                                              {\n                                                                                  ACAO: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai,\n                                                                                              ID_acionamento = var_dadosAcionamento.ID And ID_entidade = ThisItem.ID\n                                                                                          ),\n                                                                                          ID,\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Acao\n                                                                              },\n                                                                              Switch(\n                                                                                  true,\n                                                                                  ACAO = "NOTIFICADO",\n                                                                                  RGBA(\n                                                                                      253,\n                                                                                      207,\n                                                                                      180,\n                                                                                      0.7\n                                                                                  ),\n                                                                                  ACAO = "ACIONAR",\n                                                                                  RGBA(\n                                                                                      255,\n                                                                                      255,\n                                                                                      0,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "ACIONAR_SOBREAVISO",\n                                                                                  RGBA(\n                                                                                      255,\n                                                                                      255,\n                                                                                      0,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "SOBREAVISO",\n                                                                                  RGBA(\n                                                                                      247,\n                                                                                      116,\n                                                                                      38,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "RESPONDEU AO FLOW",\n                                                                                  RGBA(\n                                                                                      247,\n                                                                                      116,\n                                                                                      38,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "CHEGOU",\n                                                                                  RGBA(\n                                                                                      52,\n                                                                                      152,\n                                                                                      47,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "CONTATO_NR",\n                                                                                  Color.Red,\n                                                                                  Color.White\n                                                                              )\n                                                                          )\n                                                                          /*With(\n                                                                              {\n                                                                                  STATUS: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai;\n                                                                                              ID_entidade = ThisItem.ID\n                                                                                          );\n                                                                                          ID;\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Status;\n                                                                                  ATIVIDADE: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai;\n                                                                                              ID_entidade = ThisItem.ID\n                                                                                          );\n                                                                                          ID;\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Atividade;\n                                                                                  ACAO: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai;\n                                                                                              ID_entidade = ThisItem.ID\n                                                                                          );\n                                                                                          ID;\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Acao\n                                                                              };\n                                                                              Switch(\n                                                                                  true;\n                                                                                  ACAO = "NOTIFICADO";\n                                                                                  RGBA(\n                                                                                      253;\n                                                                                      207;\n                                                                                      180;\n                                                                                      0,7\n                                                                                  );\n                                                                                  ACAO = "ACIONAR";\n                                                                                  RGBA(\n                                                                                      255;\n                                                                                      255;\n                                                                                      0;\n                                                                                      1\n                                                                                  );\n                                                                                  ACAO = "ACIONAR_SOBREAVISO";\n                                                                                  RGBA(\n                                                                                      255;\n                                                                                      255;\n                                                                                      0;\n                                                                                      1\n                                                                                  );\n                                                                                  ACAO = "SOBREAVISO";\n                                                                                  RGBA(\n                                                                                      247;\n                                                                                      116;\n                                                                                      38;\n                                                                                      1\n                                                                                  );\n                                                                                  ACAO = "RESPONDEU AO FLOW";\n                                                                                  RGBA(\n                                                                                      255;\n                                                                                      255;\n                                                                                      0;\n                                                                                      1\n                                                                                  );\n                                                                                  STATUS = "Avisado" And IsBlank(ATIVIDADE);\n                                                                                  RGBA(\n                                                                                      255;\n                                                                                      255;\n                                                                                      0;\n                                                                                      1\n                                                                                  );\n                                                                                  ATIVIDADE = "Não vai comparecer";\n                                                                                  RGBA(\n                                                                                      255;\n                                                                                      0;\n                                                                                      0;\n                                                                                      1\n                                                                                  );\n                                                                                  STATUS = "Aguardando" And IsBlank(ATIVIDADE);\n                                                                                  RGBA(\n                                                                                      255;\n                                                                                      255;\n                                                                                      0;\n                                                                                      1\n                                                                                  );\n                                                                                  STATUS = "Contato não realizado" And IsBlank(ATIVIDADE);\n                                                                                  RGBA(\n                                                                                      255;\n                                                                                      0;\n                                                                                      0;\n                                                                                      1\n                                                                                  );\n                                                                                  ACAO = "CHEGOU";\n                                                                                  RGBA(\n                                                                                      52;\n                                                                                      152;\n                                                                                      47;\n                                                                                      1\n                                                                                  );\n                                                                                  ATIVIDADE = "Não chegou";\n                                                                                  RGBA(\n                                                                                      255;\n                                                                                      0;\n                                                                                      0;\n                                                                                      1\n                                                                                  );\n                                                                                  Color.White\n                                                                              )\n                                                                          )*/',
  '                                                                        Fill: |-\n                                                                          =With(\n                                                                              {\n                                                                                  // Consulta direta ao SharePoint. A versão com coleção dependia de\n                                                                                  // Select(Function_consultarAtividades), e esse control fica dentro\n                                                                                  // de um container com Visible = var_acao <> "view": no modo\n                                                                                  // Visualizar ele some, o Select vira no-op e as pílulas ficavam\n                                                                                  // sem cor nenhuma.\n                                                                                  ACAO: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai,\n                                                                                              ID_acionamento = var_dadosAcionamento.ID And ID_entidade = ThisItem.ID And Excluido <> true\n                                                                                          ),\n                                                                                          ID,\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Acao\n                                                                              },\n                                                                              Switch(\n                                                                                  true,\n                                                                                  ACAO = "NOTIFICADO",\n                                                                                  RGBA(232, 237, 242, 1),\n                                                                                  ACAO = "ACIONAR",\n                                                                                  RGBA(232, 194, 94, 1),\n                                                                                  ACAO = "ACIONAR_SOBREAVISO",\n                                                                                  RGBA(232, 194, 94, 1),\n                                                                                  ACAO = "SOBREAVISO",\n                                                                                  RGBA(229, 148, 104, 1),\n                                                                                  ACAO = "RESPONDEU AO FLOW",\n                                                                                  RGBA(229, 148, 104, 1),\n                                                                                  ACAO = "CHEGOU",\n                                                                                  RGBA(107, 191, 149, 1),\n                                                                                  ACAO = "CONTATO_NR",\n                                                                                  RGBA(224, 142, 156, 1),\n                                                                                  ACAO = "NAO COMPARECERA",\n                                                                                  RGBA(224, 142, 156, 1),\n                                                                                  Color.White\n                                                                              )\n                                                                          )')

P('B6/D11 pílula INFORMAR: cores da legenda + ignora atividade excluída',
  '                                                                        Fill: |-\n                                                                          =With(\n                                                                              {\n                                                                                  ACAO: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai,\n                                                                                              ID_acionamento = var_dadosAcionamento.ID And ID_entidade = ThisItem.ID\n                                                                                          ),\n                                                                                          ID,\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Acao\n                                                                              },\n                                                                              Switch(\n                                                                                  true,\n                                                                                  ACAO = "RESPONDEU AO FLOW" And ThisItem.Nivel.Value = "INFORMAR",\n                                                                                  RGBA(\n                                                                                      56,\n                                                                                      96,\n                                                                                      178,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "INFORMAR",\n                                                                                  RGBA(\n                                                                                      56,\n                                                                                      96,\n                                                                                      178,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "NOTIFICADO",\n                                                                                  RGBA(\n                                                                                      253,\n                                                                                      207,\n                                                                                      180,\n                                                                                      0.7\n                                                                                  ),\n                                                                                  ACAO = "ACIONAR",\n                                                                                  RGBA(\n                                                                                      255,\n                                                                                      255,\n                                                                                      0,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "CHEGOU",\n                                                                                  RGBA(\n                                                                                      52,\n                                                                                      152,\n                                                                                      47,\n                                                                                      1\n                                                                                  ),\n                                                                                  ACAO = "CONTATO_NR",\n                                                                                  Color.Red,\n                                                                                  Color.White\n                                                                              )\n                                                                          )',
  '                                                                        Fill: |-\n                                                                          =With(\n                                                                              {\n                                                                                  // Consulta direta ao SharePoint. A versão com coleção dependia de\n                                                                                  // Select(Function_consultarAtividades), e esse control fica dentro\n                                                                                  // de um container com Visible = var_acao <> "view": no modo\n                                                                                  // Visualizar ele some, o Select vira no-op e as pílulas ficavam\n                                                                                  // sem cor nenhuma.\n                                                                                  ACAO: First(\n                                                                                      Sort(\n                                                                                          Filter(\n                                                                                              tbl_atividadesPlemPrai,\n                                                                                              ID_acionamento = var_dadosAcionamento.ID And ID_entidade = ThisItem.ID And Excluido <> true\n                                                                                          ),\n                                                                                          ID,\n                                                                                          SortOrder.Descending\n                                                                                      )\n                                                                                  ).Acao\n                                                                              },\n                                                                              Switch(\n                                                                                  true,\n                                                                                  ACAO = "RESPONDEU AO FLOW" And ThisItem.Nivel.Value = "INFORMAR",\n                                                                                  RGBA(107, 167, 209, 1),\n                                                                                  ACAO = "INFORMAR",\n                                                                                  RGBA(107, 167, 209, 1),\n                                                                                  ACAO = "NOTIFICADO",\n                                                                                  RGBA(232, 237, 242, 1),\n                                                                                  ACAO = "ACIONAR",\n                                                                                  RGBA(232, 194, 94, 1),\n                                                                                  ACAO = "CHEGOU",\n                                                                                  RGBA(107, 191, 149, 1),\n                                                                                  ACAO = "CONTATO_NR",\n                                                                                  RGBA(224, 142, 156, 1),\n                                                                                  ACAO = "NAO COMPARECERA",\n                                                                                  RGBA(224, 142, 156, 1),\n                                                                                  Color.White\n                                                                              )\n                                                                          )')

# ---------------------------------------------------------------------------
# F* = alinhamento cromático (pedido do usuário em 2026-08-24: "mudar as cores
#      da legenda e das entidades para conversar com atividades").
#
# Uma paleta só na tela inteira, em dois pesos:
#   chip da atividade / borda / CTA -> cor FORTE  (STATUS_APP)
#   legenda e pílula do fluxograma  -> cor CLARA  (SUPERFICIE_APP, mesmo matiz)
# As pílulas já foram remapeadas dentro de B6/D9-D11; aqui vai a legenda (que
# é a referência que o usuário lê), os cabeçalhos das colunas e os dois CTAs
# da lista de atividades, que ainda usavam verde/vermelho puros.
# ---------------------------------------------------------------------------
P('F1 legenda NOTIFICADO -> mesmo neutro do chip (#E8EDF2)',
  '                                                                  Fill: |-\n                                                                    =RGBA(\n                                                                                253,\n                                                                                207,\n                                                                                180,\n                                                                                0.7\n                                                                            )',
  '                                                                  Fill: |-\n                                                                    =RGBA(\n                                                                                232,\n                                                                                237,\n                                                                                242,\n                                                                                1\n                                                                            )')

P('F2 legenda ACIONADO -> âmbar da paleta (#E8C25E, matiz do chip #B98900)',
  '                                                                  Fill: |-\n                                                                    =RGBA(\n                                                                                255,\n                                                                                255,\n                                                                                0,\n                                                                                1\n                                                                            )',
  '                                                                  Fill: |-\n                                                                    =RGBA(\n                                                                                232,\n                                                                                194,\n                                                                                94,\n                                                                                1\n                                                                            )')

P('F3 legenda CHEGOU -> verde da paleta (#6BBF95, matiz do chip #1F7A4D)',
  '                                                            - Label11_10:\n                                                                Control: Label@2.5.1\n                                                                Properties:\n                                                                  Align: =Align.Center\n                                                                  AlignInContainer: =AlignInContainer.Stretch\n                                                                  Fill: =RGBA(52, 152, 47, 1)',
  '                                                            - Label11_10:\n                                                                Control: Label@2.5.1\n                                                                Properties:\n                                                                  Align: =Align.Center\n                                                                  AlignInContainer: =AlignInContainer.Stretch\n                                                                  Fill: =RGBA(107, 191, 149, 1)')

P('F4 legenda SOBREAVISO -> laranja da paleta (#E59468, matiz do chip #C05621)',
  '                                                                  Fill: =RGBA(247, 116, 38, 1)',
  '                                                                  Fill: =RGBA(229, 148, 104, 1)')

P('F5 legenda INFORMADO -> azul da paleta (#6BA7D1, matiz do chip #155E8F)',
  '                                                                  Fill: |-\n                                                                    =RGBA(\n                                                                                56,\n                                                                                96,\n                                                                                178,\n                                                                                1\n                                                                            )',
  '                                                                  Fill: |-\n                                                                    =RGBA(\n                                                                                107,\n                                                                                167,\n                                                                                209,\n                                                                                1\n                                                                            )')

P('F6 legenda CONTATO NÃO REALIZADO -> vermelho da paleta (#E08E9C <- #A62639)',
  '                                                                  Fill: |-\n                                                                    =RGBA(\n                                                                                255,\n                                                                                0,\n                                                                                0,\n                                                                                1\n                                                                            )',
  '                                                                  Fill: |-\n                                                                    =RGBA(\n                                                                                224,\n                                                                                142,\n                                                                                156,\n                                                                                1\n                                                                            )')

# Cabeçalhos das colunas do fluxograma: pílula vazada, só borda. Borda de 1px
# pede a cor FORTE (a clara some no branco), e é a mesma cor do chip.
P('F7 cabeçalho da coluna ACIONAR: borda âmbar em vez de amarelo puro',
  '                                                                  BorderColor: |-\n                                                                    =RGBA(\n                                                                        255,\n                                                                        255,\n                                                                        0,\n                                                                        1\n                                                                    )',
  '                                                                  BorderColor: |-\n                                                                    =RGBA(\n                                                                        185,\n                                                                        137,\n                                                                        0,\n                                                                        1\n                                                                    )')

P('F8 cabeçalho da coluna SOBREAVISO: borda na paleta',
  '                                                                  BorderColor: |-\n                                                                    =RGBA(\n                                                                        247,\n                                                                        116,\n                                                                        38,\n                                                                        1\n                                                                    )',
  '                                                                  BorderColor: |-\n                                                                    =RGBA(\n                                                                        192,\n                                                                        86,\n                                                                        33,\n                                                                        1\n                                                                    )')

P('F9 cabeçalho da coluna INFORMAR: borda na paleta',
  '                                                                  BorderColor: =RGBA(56, 96, 178, 1)\n                                                                  Color: =RGBA(0, 0, 0, 1)\n                                                                  DisplayMode: =DisplayMode.View',
  '                                                                  BorderColor: =ColorValue("#155E8F")\n                                                                  Color: =RGBA(0, 0, 0, 1)\n                                                                  DisplayMode: =DisplayMode.View')

# CTAs da lista de atividades: texto branco sobre cor cheia -> cor FORTE,
# idêntica ao chip do evento que o botão gera.
P('F10 CTA "Chegou": verde da paleta (#1F7A4D) em vez do #349730',
  '                                                            - ButtonChegou:\n                                                                Control: Classic/Button@2.2.0\n                                                                Properties:\n                                                                  BorderColor: =RGBA(255, 255, 255, 1)\n                                                                  Color: =RGBA(255, 255, 255, 1)\n                                                                  Fill: =RGBA(52, 152, 47, 1)\n                                                                  FontWeight: =FontWeight.Normal\n                                                                  HoverColor: =RGBA(255, 255, 255, 1)\n                                                                  HoverFill: =RGBA(72, 222, 64, 1)',
  '                                                            - ButtonChegou:\n                                                                Control: Classic/Button@2.2.0\n                                                                Properties:\n                                                                  BorderColor: =RGBA(255, 255, 255, 1)\n                                                                  Color: =RGBA(255, 255, 255, 1)\n                                                                  Fill: =ColorValue("#1F7A4D")\n                                                                  FontWeight: =FontWeight.Normal\n                                                                  HoverColor: =RGBA(255, 255, 255, 1)\n                                                                  HoverFill: =ColorValue("#2E9463")')

P('F11 CTA "Não vai comparecer": vermelho institucional (#A62639)',
  '                                                            - ButtonNaoVaiComparecer:\n                                                                Control: Classic/Button@2.2.0\n                                                                Properties:\n                                                                  BorderColor: =RGBA(255, 255, 255, 1)\n                                                                  Color: =RGBA(255, 255, 255, 1)\n                                                                  Fill: =RGBA(255, 0, 0, 1)\n                                                                  FontWeight: =FontWeight.Normal\n                                                                  HoverColor: =RGBA(255, 255, 255, 1)\n                                                                  HoverFill: =RGBA(255, 120, 120, 1)',
  '                                                            - ButtonNaoVaiComparecer:\n                                                                Control: Classic/Button@2.2.0\n                                                                Properties:\n                                                                  BorderColor: =RGBA(255, 255, 255, 1)\n                                                                  Color: =RGBA(255, 255, 255, 1)\n                                                                  Fill: =ColorValue("#A62639")\n                                                                  FontWeight: =FontWeight.Normal\n                                                                  HoverColor: =RGBA(255, 255, 255, 1)\n                                                                  HoverFill: =ColorValue("#C4404F")')


# ====== FRENTE E - pendencias residuais da auditoria (rodada final) ======

P('E4b abrir o monitoramento já calcula o status das entidades',
  '\n                                                              UpdateContext({var_visibleFluxogramaAcionamentosReal: true});\n',
  '\n                                                              UpdateContext({var_visibleFluxogramaAcionamentosReal: true});\n                                                              // Recarrega as atividades ao abrir o monitoramento, para a lista\n                                                              // não abrir com dado velho\n                                                              Select(Function_consultarAtividades);\n', 2)

P('E1.II exclusão de vítima Prioridade II registra log e avisa o chat',
  '                                                            - Icon4_11:\n                                                                Control: Classic/Icon@2.5.0\n                                                                Properties:\n                                                                  Color: =RGBA(0, 0, 0, 1)\n                                                                  Height: =20\n                                                                  Icon: =Icon.Trash\n                                                                  OnSelect: =Remove(tbl_metodoStart,ThisItem)',
  '                                                            - Icon4_11:\n                                                                Control: Classic/Icon@2.5.0\n                                                                Properties:\n                                                                  Color: =RGBA(0, 0, 0, 1)\n                                                                  Height: =20\n                                                                  Icon: =Icon.Trash\n                                                                  OnSelect: |-\n                                                                    =// E1 - só a Prioridade I registrava a exclusão: nas outras\n                                                                    // três o Remove era mudo, sem log e sem aviso no chat.\n                                                                    With(\n                                                                        {\n                                                                            _chat: var_dadosAcionamento.ID_chat,\n                                                                            _ator: Substitute(\n                                                                                ThisItem.vitima,\n                                                                                "§",\n                                                                                "/"\n                                                                            ),\n                                                                            _detalhe: Substitute(\n                                                                                "Prioridade " & ThisItem.prioridade.Value & " · Ambulância: " & ThisItem.ambulancia & " · Hospital: " & ThisItem.hospital,\n                                                                                "§",\n                                                                                "/"\n                                                                            )\n                                                                        },\n                                                                        Remove(\n                                                                            tbl_metodoStart,\n                                                                            ThisItem\n                                                                        );\n                                                                        Patch(\n                                                                            tbl_atividadesPlemPrai,\n                                                                            Defaults(tbl_atividadesPlemPrai),\n                                                                            {\n                                                                                ID_acionamento: var_dadosAcionamento.ID,\n                                                                                Acao: "EXCLUSÃO DE VÍTIMA",\n                                                                                Atividade: "VÍTIMA REMOVIDA · " & _ator & " · " & _detalhe,\n                                                                                Hora: Now(),\n                                                                                Ativo: 1,\n                                                                                ID_chat: _chat\n                                                                            }\n                                                                        );\n                                                                        If(\n                                                                            !IsBlank(_chat),\n                                                                            EnviarAtividadeparachatteams.Run(\n                                                                                "VITIMA_EXCLUIDA§" & _ator & "§" & _detalhe,\n                                                                                _chat\n                                                                            )\n                                                                        )\n                                                                    )')

P('E1.III exclusão de vítima Prioridade III registra log e avisa o chat',
  '                                                            - Icon4_12:\n                                                                Control: Classic/Icon@2.5.0\n                                                                Properties:\n                                                                  Color: =RGBA(0, 0, 0, 1)\n                                                                  Height: =20\n                                                                  Icon: =Icon.Trash\n                                                                  OnSelect: =Remove(tbl_metodoStart,ThisItem)',
  '                                                            - Icon4_12:\n                                                                Control: Classic/Icon@2.5.0\n                                                                Properties:\n                                                                  Color: =RGBA(0, 0, 0, 1)\n                                                                  Height: =20\n                                                                  Icon: =Icon.Trash\n                                                                  OnSelect: |-\n                                                                    =// E1 - só a Prioridade I registrava a exclusão: nas outras\n                                                                    // três o Remove era mudo, sem log e sem aviso no chat.\n                                                                    With(\n                                                                        {\n                                                                            _chat: var_dadosAcionamento.ID_chat,\n                                                                            _ator: Substitute(\n                                                                                ThisItem.vitima,\n                                                                                "§",\n                                                                                "/"\n                                                                            ),\n                                                                            _detalhe: Substitute(\n                                                                                "Prioridade " & ThisItem.prioridade.Value & " · Ambulância: " & ThisItem.ambulancia & " · Hospital: " & ThisItem.hospital,\n                                                                                "§",\n                                                                                "/"\n                                                                            )\n                                                                        },\n                                                                        Remove(\n                                                                            tbl_metodoStart,\n                                                                            ThisItem\n                                                                        );\n                                                                        Patch(\n                                                                            tbl_atividadesPlemPrai,\n                                                                            Defaults(tbl_atividadesPlemPrai),\n                                                                            {\n                                                                                ID_acionamento: var_dadosAcionamento.ID,\n                                                                                Acao: "EXCLUSÃO DE VÍTIMA",\n                                                                                Atividade: "VÍTIMA REMOVIDA · " & _ator & " · " & _detalhe,\n                                                                                Hora: Now(),\n                                                                                Ativo: 1,\n                                                                                ID_chat: _chat\n                                                                            }\n                                                                        );\n                                                                        If(\n                                                                            !IsBlank(_chat),\n                                                                            EnviarAtividadeparachatteams.Run(\n                                                                                "VITIMA_EXCLUIDA§" & _ator & "§" & _detalhe,\n                                                                                _chat\n                                                                            )\n                                                                        )\n                                                                    )')

P('E1.IV exclusão de vítima Prioridade IV registra log e avisa o chat',
  '                                                            - Icon4_13:\n                                                                Control: Classic/Icon@2.5.0\n                                                                Properties:\n                                                                  Color: =RGBA(0, 0, 0, 1)\n                                                                  Height: =20\n                                                                  Icon: =Icon.Trash\n                                                                  OnSelect: =Remove(tbl_metodoStart,ThisItem)',
  '                                                            - Icon4_13:\n                                                                Control: Classic/Icon@2.5.0\n                                                                Properties:\n                                                                  Color: =RGBA(0, 0, 0, 1)\n                                                                  Height: =20\n                                                                  Icon: =Icon.Trash\n                                                                  OnSelect: |-\n                                                                    =// E1 - só a Prioridade I registrava a exclusão: nas outras\n                                                                    // três o Remove era mudo, sem log e sem aviso no chat.\n                                                                    With(\n                                                                        {\n                                                                            _chat: var_dadosAcionamento.ID_chat,\n                                                                            _ator: Substitute(\n                                                                                ThisItem.vitima,\n                                                                                "§",\n                                                                                "/"\n                                                                            ),\n                                                                            _detalhe: Substitute(\n                                                                                "Prioridade " & ThisItem.prioridade.Value & " · Ambulância: " & ThisItem.ambulancia & " · Hospital: " & ThisItem.hospital,\n                                                                                "§",\n                                                                                "/"\n                                                                            )\n                                                                        },\n                                                                        Remove(\n                                                                            tbl_metodoStart,\n                                                                            ThisItem\n                                                                        );\n                                                                        Patch(\n                                                                            tbl_atividadesPlemPrai,\n                                                                            Defaults(tbl_atividadesPlemPrai),\n                                                                            {\n                                                                                ID_acionamento: var_dadosAcionamento.ID,\n                                                                                Acao: "EXCLUSÃO DE VÍTIMA",\n                                                                                Atividade: "VÍTIMA REMOVIDA · " & _ator & " · " & _detalhe,\n                                                                                Hora: Now(),\n                                                                                Ativo: 1,\n                                                                                ID_chat: _chat\n                                                                            }\n                                                                        );\n                                                                        If(\n                                                                            !IsBlank(_chat),\n                                                                            EnviarAtividadeparachatteams.Run(\n                                                                                "VITIMA_EXCLUIDA§" & _ator & "§" & _detalhe,\n                                                                                _chat\n                                                                            )\n                                                                        )\n                                                                    )')

P('E2 busca de equipamentos volta a filtrar pelo aeroporto do acionamento',
  '                                                Items: |-\n                                                  =Search(\n                                                      //Filter(\n                                                          col_equipamentosAcionamentos, \n                                                          //Aeroporto = varAeroUser);\n                                                      TextInputConsultarEQP.Text, \n                                                      Item\n                                                  )',
  '                                                Items: |-\n                                                  =// E2 - o Filter por aeroporto estava comentado no meio da\n                                                  // expressão: a busca listava equipamento de TODOS os aeroportos.\n                                                  Search(\n                                                      Filter(\n                                                          col_equipamentosAcionamentos,\n                                                          Aeroporto = Coalesce(\n                                                              var_dadosAcionamento.Aeroporto,\n                                                              varAeroUser\n                                                          )\n                                                      ),\n                                                      TextInputConsultarEQP.Text,\n                                                      Item\n                                                  )')

P('E3 OnVisible não carrega mais ~947 contatos numa coleção que ninguém lê',
  '        //Select(ButtonAcionamentosPlem);;\n        Switch(\n            varPerfilUser,\n            "Base",\n            ClearCollect(\n                col_contatos_acionamentos,\n                Sort(\n                    Filter(\n                        tbl_contatos_entidades,\n                        Aeroporto = varAeroUser\n                    ),\n                    ID,\n                    SortOrder.Descending\n                )\n            ),\n            "Bloco",\n            ClearCollect(\n                col_contatos_acionamentos,\n                Sort(\n                    Filter(\n                        tbl_contatos_entidades,\n                        Bloco = varBlocoUser\n                    ),\n                    ID,\n                    SortOrder.Descending\n                )\n            ),\n            ClearCollect(\n                col_contatos_acionamentos,\n                Sort(\n                    tbl_contatos_entidades,\n                    ID,\n                    SortOrder.Descending\n                )\n            )\n        )',
  '        //Select(ButtonAcionamentosPlem);;\n        // E3 - o Switch que ficava aqui carregava tbl_contatos_entidades\n        // inteira em col_contatos_acionamentos a cada OnVisible (~947\n        // registros) e nenhum controle desta tela, nem a tela de Contatos,\n        // lê essa coleção.')

P('E5 timer recarrega de fato (a comparação lia o mesmo cache dos dois lados)',
  '                                                OnTimerEnd: |-\n                                                  =If(\n                                                      var_visibleFluxogramaAcionamentosReal And !IsBlank(var_dadosAcionamento),\n                                                      If(\n                                                          Coalesce(\n                                                              First(\n                                                                  Sort(\n                                                                      Filter(\n                                                                          tbl_atividadesPlemPrai,\n                                                                          ID_acionamento = Value(var_dadosAcionamento.ID)\n                                                                      ),\n                                                                      ID,\n                                                                      SortOrder.Descending\n                                                                  )\n                                                              ).ID,\n                                                              0\n                                                          ) > Coalesce(\n                                                              First(\n                                                                  Sort(\n                                                                      GalleryAtividadesLancadas.AllItems,\n                                                                      ID,\n                                                                      SortOrder.Descending\n                                                                  )\n                                                              ).ID,\n                                                              0\n                                                          ),\n                                                          Select(Function_consultarAtividades)\n                                                      )\n                                                  )',
  '                                                OnTimerEnd: |-\n                                                  =// E5 - a comparação anterior lia o ID mais recente da lista e o da\n                                                  // galeria: os dois vinham do MESMO cache do datasource, então eram\n                                                  // sempre iguais e o Refresh quase nunca acontecia. Quem traz dado\n                                                  // novo é justamente o Refresh, então ele é o passo, não a\n                                                  // consequência. Só roda com o monitoramento aberto, a cada 30s.\n                                                  If(\n                                                      var_visibleFluxogramaAcionamentosReal And !IsBlank(var_dadosAcionamento),\n                                                      Select(Function_consultarAtividades)\n                                                  )')

P('B10 diálogo de exclusão fecha sem referências inexistentes',
  '                                                  =/*UpdateContext({var_visibleExcluir: false});;\n                                                  Concurrent(\n                                                      RemoveIf(\n                                                          tbl_GRUPO_ORDEM;\n                                                          ID = var_contato_fluxo.ID\n                                                      );\n                                                      RemoveIf(\n                                                          col_grupos_ordem;\n                                                          ID = var_contato_fluxo.ID\n                                                      )\n                                                  );;\n                                                  Notify(\n                                                      "Item excluido com sucesso!";\n                                                      NotificationType.Warning\n                                                  )*/',
  '                                                  =// B10 - o OnSelect original estava inteiramente comentado. O código\n                                                  // dentro do comentário referenciava tbl_GRUPO_ORDEM,\n                                                  // col_grupos_ordem e var_contato_fluxo — NENHUM dos três existe\n                                                  // neste app (a fonte de dados não está conectada, a coleção nunca\n                                                  // é criada e a variável nunca é definida). Descomentar quebrava a\n                                                  // fórmula com três nomes desconhecidos.\n                                                  // Além disso var_visibleExcluir só é definido como false: este\n                                                  // diálogo nunca chega a aparecer. Fica apenas fechando.\n                                                  UpdateContext({var_visibleExcluir: false})')

P('C2.19 seta do fluxograma sem emoji (3 ocorrencias)',
  '\n                                                                        Text: ="⬇"\n',
  '\n                                                                        Text: ="↓"\n', 3)

P('C2.19 seta do fluxograma sem emoji (1 ocorrencias)',
  '\n                                                Text: ="⬇"\n',
  '\n                                                Text: ="↓"\n')

P('C2.19 seta do fluxograma sem emoji (3 ocorrencias)',
  '\n                                                            Text: ="⬇"\n',
  '\n                                                            Text: ="↓"\n', 3)

P('E4c iniciar acionamento já calcula o status das entidades',
  '                                                                      var_visibleFluxogramaAcionamentosReal: true,\n                                                                      var_viewAtividades: 1\n                                                                  }\n                                                              )',
  '                                                                      var_visibleFluxogramaAcionamentosReal: true,\n                                                                      var_viewAtividades: 1\n                                                                  }\n                                                              );\n                                                              // Recarrega as atividades logo após criar o acionamento\n                                                              Select(Function_consultarAtividades)')


# ===== C9 - operador duplicado na criação do chat (BadRequest do Teams) =====
P('C9 operador fora da lista de membros (ele é o criador do chat)',
  '                                                              Set(\n                                                                  JSON_PARTICIPANTES,\n                                                                  JSON(\n                                                                      col_emailsCcrFilter,\n                                                                      JSONFormat.Compact\n                                                                  )\n                                                              );',
  '                                                              // C9 - o operador NÃO entra na lista de membros do chat: o Teams\n                                                              // cria o chat com a conexão dele e já o inclui como criador.\n                                                              // Mandá-lo junto devolve "Duplicate chat members is specified\n                                                              // in the request body" e o chat não é criado.\n                                                              // Ele continua na coleção para receber a notificação e\n                                                              // aparecer no log de NOTIFICADO.\n                                                              Set(\n                                                                  JSON_PARTICIPANTES,\n                                                                  JSON(\n                                                                      Filter(\n                                                                          col_emailsCcrFilter,\n                                                                          Nivel <> "OPERADOR"\n                                                                      ),\n                                                                      JSONFormat.Compact\n                                                                  )\n                                                              );')

# ==================================================================== runner
VISUAIS = re.compile(
    r'^\s*(X|Y|Width|Height|Fill|HoverFill|PressedFill|Color|HoverColor|PressedColor|'
    r'BorderColor|DisabledBorderColor|BasePaletteColor|Padding\w*|Radius\w*|BorderRadius\w*|'
    r'Layout\w*|Font\w*|FontWeight|FontSize|Size|Align|Border\w*|DropShadow|Text|Visible|'
    r'Variant|Icon|IconStyle|Appearance|Weight|Wrap|TemplateSize|FillPortions|'
    r'AlignInContainer|AutoHeight|Placeholder|Tooltip|Mode|HtmlText|Label|Control):')


# Exceções visuais AUTORIZADAS pelo usuário em 2026-08-24 ("melhore as cores
# de tudo"): cada linha visual que muda é declarada aqui nominalmente, nos dois
# sentidos. A guarda exige que (a) nada fora desta lista mude e (b) TUDO que
# está aqui de fato mude — exceção declarada e não aplicada também reprova.
# Fórmulas multi-linha (Fill: |- / HtmlText: |-) não aparecem aqui porque a
# guarda compara apenas linhas de propriedade; o conteúdo delas é validado
# pelos próprios patches (contagem exata de old/new).
EXCECOES_SOMEM = [
    ('F3 legenda CHEGOU (verde puro)', '                                                                  Fill: =RGBA(52, 152, 47, 1)'),
    ('F4 legenda SOBREAVISO (laranja puro)', '                                                                  Fill: =RGBA(247, 116, 38, 1)'),
    ('F9 borda da coluna INFORMAR (azul legado)', '                                                                  BorderColor: =RGBA(56, 96, 178, 1)'),
    ('F10 CTA Chegou (verde puro)', '                                                                  Fill: =RGBA(52, 152, 47, 1)'),
    ('F10 CTA Chegou hover (verde neon)', '                                                                  HoverFill: =RGBA(72, 222, 64, 1)'),
    ('F11 CTA Não comparecerá (vermelho puro)', '                                                                  Fill: =RGBA(255, 0, 0, 1)'),
    ('F11 CTA Não comparecerá hover', '                                                                  HoverFill: =RGBA(255, 120, 120, 1)'),
    ('D1 faixa de status do timeline (fórmula antiga)', '                                                                  Fill: "=Switch(\\n    true,\\n    ThisItem.Acao = \\"RESPONDEU AO FLOW\\" And LookUp(\\n        tbl_FluxogramaAcionamentos,\\n        ID = ThisItem.ID_entidade\\n    ).Nivel.Value = \\"ACIONAR\\",\\n    RGBA(\\n        255,\\n        255,\\n        0,\\n        1\\n    ),\\n    ThisItem.Acao = \\"RESPONDEU AO FLOW\\" And LookUp(\\n        tbl_FluxogramaAcionamentos,\\n        ID = ThisItem.ID_entidade\\n    ).Nivel.Value = \\"SOBREAVISO\\",\\n    RGBA(\\n        247,\\n        116,\\n        38,\\n        1\\n    ),\\n    ThisItem.Acao = \\"RESPONDEU AO FLOW\\" And LookUp(\\n        tbl_FluxogramaAcionamentos,\\n        ID = ThisItem.ID_entidade\\n    ).Nivel.Value = \\"INFORMAR\\",\\n    RGBA(\\n        56,\\n        96,\\n        178,\\n        1\\n    ),\\n    ThisItem.Acao = \\"CONTATO_NR\\",\\n    Color.Red,\\n    ThisItem.Acao = \\"CHEGOU\\",\\n    RGBA(\\n        52,\\n        152,\\n        47,\\n        1\\n    ),\\n    ThisItem.Acao = \\"ACIONAR\\",\\n    RGBA(\\n        255,\\n        255,\\n        0,\\n        1\\n    ),\\n    ThisItem.Acao = \\"ACIONAR_SOBREAVISO\\",\\n    RGBA(\\n        255,\\n        255,\\n        0,\\n        1\\n    ),\\n    ThisItem.Acao = \\"SOBREAVISO\\",\\n    RGBA(\\n        247,\\n        116,\\n        38,\\n        1\\n    ),\\n    ThisItem.Acao = \\"INFORMAR\\",\\n    RGBA(\\n        56,\\n        96,\\n        178,\\n        1\\n    ),\\n   \\n        RGBA(\\n            0,\\n            0,\\n            0,\\n            0\\n        \\n    )\\n)\\n"'),
    ('D2 Color sem default do CTA Acionar', '                                                                  Color: |-'),
    ('D2 faixa amarela do CTA Acionar', '                                                                  Fill: "=\\n    RGBA(\\n        255,\\n        255,\\n        0,\\n        1\\n    )\\n   "'),
    ('D3 verde/vermelho puros do status de equipamento', '                                                      Color: =If(ThisItem.Status.Value = "Disponível", RGBA(52, 152, 47, 1), Color.Red)'),
]
EXCECOES_SURGEM = [
    ('F3 legenda CHEGOU (superfície #6BBF95)', '                                                                  Fill: =RGBA(107, 191, 149, 1)'),
    ('F4 legenda SOBREAVISO (superfície #E59468)', '                                                                  Fill: =RGBA(229, 148, 104, 1)'),
    ('F9 borda da coluna INFORMAR (#155E8F)', '                                                                  BorderColor: =ColorValue("#155E8F")'),
    ('F10 CTA Chegou (#1F7A4D)', '                                                                  Fill: =ColorValue("#1F7A4D")'),
    ('F10 CTA Chegou hover (#2E9463)', '                                                                  HoverFill: =ColorValue("#2E9463")'),
    ('F11 CTA Não comparecerá (#A62639)', '                                                                  Fill: =ColorValue("#A62639")'),
    ('F11 CTA Não comparecerá hover (#C4404F)', '                                                                  HoverFill: =ColorValue("#C4404F")'),
    ('D1 faixa de status do timeline (paleta nova)', '                                                                  Fill: "=Switch(\\n    ThisItem.Acao,\\n    \\"ACIONAR\\",\\n    RGBA(185, 137, 0, 1),\\n    \\"ACIONAR_SOBREAVISO\\",\\n    RGBA(185, 137, 0, 1),\\n    \\"RESPONDEU AO FLOW\\",\\n    RGBA(185, 137, 0, 1),\\n    \\"SOBREAVISO\\",\\n    RGBA(192, 86, 33, 1),\\n    \\"INFORMAR\\",\\n    RGBA(21, 94, 143, 1),\\n    \\"NOTIFICADO\\",\\n    RGBA(200, 211, 220, 1),\\n    \\"CHEGOU\\",\\n    RGBA(31, 122, 77, 1),\\n    \\"CONTATO_NR\\",\\n    RGBA(166, 38, 57, 1),\\n    \\"NAO COMPARECERA\\",\\n    RGBA(166, 38, 57, 1),\\n    \\"SEM RESPOSTA\\",\\n    RGBA(93, 107, 119, 1),\\n    \\"CRIAÇÃO\\",\\n    RGBA(11, 46, 79, 1),\\n    \\"FINALIZAÇÃO\\",\\n    RGBA(11, 46, 79, 1),\\n    \\"CHAT\\",\\n    RGBA(93, 107, 119, 1),\\n    \\"ERRO CHAT\\",\\n    RGBA(166, 38, 57, 1),\\n    \\"ATIVIDADE MANUAL\\",\\n    RGBA(93, 107, 119, 1),\\n    \\"REGISTRO DE VÍTIMA\\",\\n    RGBA(122, 78, 130, 1),\\n    \\"ALTERAÇÃO DE VÍTIMA\\",\\n    RGBA(122, 78, 130, 1),\\n    \\"EXCLUSÃO DE VÍTIMA\\",\\n    RGBA(122, 78, 130, 1),\\n    RGBA(223, 229, 234, 1)\\n)\\n"'),
    ('D2 CTA Acionar texto branco fixo', '                                                                  Color: =RGBA(255, 255, 255, 1)'),
    ('D2 CTA Acionar azul de ação', '                                                                  Fill: =ColorValue("#155E8F")'),
    ('D3 status de equipamento na paleta', '                                                      Color: =If(ThisItem.Status.Value = "Disponível", ColorValue("#1F7A4D"), ColorValue("#A62639"))'),
    ('D4 Title3_9 ganha a mesma cor de status', '                                                            Color: =If(ThisItem.Status.Value = "Disponível", ColorValue("#1F7A4D"), ColorValue("#A62639"))'),
]
EXCECOES_PARES_PREFIXO = []

# preenchido pela guarda: rótulos que só perderam o emoji (Frente C2)
EMOJI_REMOVIDOS = []


# Emoji -> glifo tipográfico equivalente (o caractere carrega significado,
# então é substituído em vez de removido).
SUBSTITUICOES_GLIFO = {'\u2b07': '\u2193'}   # seta para baixo do fluxograma


def guarda_layout(antes, depois):
    """Prova que nenhuma propriedade visual mudou fora das exceções declaradas."""
    def visuais(txt):
        return sorted(l for l in txt.split('\n') if VISUAIS.match(l))
    a, d = visuais(antes), visuais(depois)
    from collections import Counter
    ca, cd = Counter(a), Counter(d)
    so_a = list((ca - cd).elements())   # linhas que sumiram
    so_d = list((cd - ca).elements())   # linhas que surgiram

    for rotulo, linha in EXCECOES_SOMEM:
        if linha not in so_a:
            die('exceção declarada não aplicada (nada sumiu): %s' % rotulo)
        so_a.remove(linha)
    for rotulo, linha in EXCECOES_SURGEM:
        if linha not in so_d:
            die('exceção declarada não aplicada (nada surgiu): %s' % rotulo)
        so_d.remove(linha)
    for rotulo, prefixo in EXCECOES_PARES_PREFIXO:
        vel = [x for x in so_a if x.startswith(prefixo)]
        nov = [x for x in so_d if x.startswith(prefixo)]
        if len(vel) != 1 or len(nov) != 1:
            die('exceção de par não casou: %s (sumiu %d, surgiu %d)'
                % (rotulo, len(vel), len(nov)))
        so_a.remove(vel[0]); so_d.remove(nov[0])

    # Regra declarada (não lista fixa): rótulos que perderam APENAS o emoji.
    # Cada linha que sumiu tem que casar com uma que surgiu depois de remover o
    # emoji — qualquer outra diferença de texto continua reprovando.
    import re as _re
    _EMO = _re.compile('(?:[\U0001F300-\U0001FAFF\u2699\u26a0\u274c\u2795\u2757])\ufe0f?\\s*')
    for _linha in list(so_a):
        _limpa = _EMO.sub('', _linha)
        if _limpa != _linha and _limpa in so_d:
            so_a.remove(_linha)
            so_d.remove(_limpa)
            EMOJI_REMOVIDOS.append(_limpa.strip()[:60])

    # Segunda regra declarada: glifos emoji trocados pelo equivalente
    # tipográfico. Diferente da regra acima, aqui o caractere é SUBSTITUÍDO,
    # não removido — a seta do fluxograma carrega significado (direção), então
    # sai o emoji e entra o sinal de texto.
    for _linha in list(so_a):
        _troca = _linha
        for _de, _para in SUBSTITUICOES_GLIFO.items():
            _troca = _troca.replace(_de, _para)
        if _troca != _linha and _troca in so_d:
            so_a.remove(_linha)
            so_d.remove(_troca)
            EMOJI_REMOVIDOS.append(_troca.strip()[:60])

    if so_a or so_d:
        die('a trava de layout reprovou.\n  sumiu: %s\n  surgiu: %s'
            % (so_a[:5], so_d[:5]))


ADDABLE = set()   # esta rodada não acrescenta nenhuma propriedade nova


# ------------------------------------------------- LoadingSpinner (opcional)
# Investigação de 2026-08-24: a rodada anterior injetava DelayItemLoading +
# LoadingSpinner nas 25 galerias e as duas sumiram no reexport do Studio.
# Motivo: DelayItemLoading é propriedade da galeria CLÁSSICA e não existe em
# Gallery@2.15.0 — o Studio descarta em silêncio. LoadingSpinner, por outro
# lado, É válido: aparece em posição alfabética (portanto escrito pelo próprio
# Studio) em 7 galerias Gallery@2.15.0 de PerdidoseAchados, inclusive com os
# mesmos Variants desta tela.
#
# Fica opcional porque é COSMÉTICO (mostra spinner enquanto carrega), não é
# ganho de performance, e mexe no que o usuário vê — e a regra desta tela é
# não mexer no visual sem pedido explícito.
#
#   --spinner          aplica nas 25 galerias
#   --spinner --sonda  aplica só na 1ª, para colar e confirmar que sobrevive
#                      ao reexport antes de valer para todas
SPINNER_VALOR = 'LoadingSpinner.Data'


def injetar_spinner(texto, valor=SPINNER_VALOR, sonda=False):
    """Insere LoadingSpinner na POSIÇÃO ALFABÉTICA do bloco Properties de cada
    Gallery@ — é assim que o Studio grava, então o reexport sai idêntico e o
    diff seguinte fica limpo."""
    linhas = texto.split('\n')
    saida, i, n = [], 0, 0
    while i < len(linhas):
        ln = linhas[i]
        saida.append(ln)
        m = re.match(r'^(\s*)Control: Gallery@', ln)
        if not m or (sonda and n >= 1):
            i += 1
            continue
        ind = len(m.group(1))
        # bloco do controle
        j = i + 1
        while j < len(linhas):
            if linhas[j].strip() and indent_of(linhas[j]) < ind:
                break
            j += 1
        bloco = linhas[i + 1:j]
        if any(re.match(r'^\s{%d}LoadingSpinner:' % (ind + 2), l) for l in bloco):
            i += 1
            continue
        try:
            p_rel = next(k for k, l in enumerate(bloco)
                         if re.match(r'^\s{%d}Properties:$' % ind, l))
        except StopIteration:
            i += 1
            continue
        # propriedades diretas do controle, na ordem em que aparecem
        diretas = [(k, re.match(r'^\s{%d}([A-Za-z][A-Za-z0-9_]*):' % (ind + 2), l))
                   for k, l in enumerate(bloco)]
        diretas = [(k, mm.group(1)) for k, mm in diretas if mm]
        alvo = next((k for k, nome in diretas if nome > 'LoadingSpinner'), None)
        if alvo is None:
            alvo = (diretas[-1][0] + 1) if diretas else (p_rel + 1)
        nova = ' ' * (ind + 2) + 'LoadingSpinner: =%s' % valor
        bloco = bloco[:alvo] + [nova] + bloco[alvo:]
        saida.extend(bloco)
        n += 1
        i = j
    return '\n'.join(saida), n


def indent_of(linha):
    return len(linha) - len(linha.lstrip(' '))


def validar(src_text, out_text):
    """Mesmas travas de otimizar_tela_plem_prai.py, reaplicadas aqui."""
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

    # Distinct() só tem a coluna Value; ThisRecord sem alias religa ao escopo
    # mais interno (bug C6 das LICOES).
    for m in re.finditer(r'ForAll\(\s*Distinct\(', out_text):
        i, prof = m.end() - 1, 0
        corpo = None
        for j in range(i, min(i + 4000, len(out_text))):
            if out_text[j] == '(':
                prof += 1
            elif out_text[j] == ')':
                prof -= 1
                if prof == 0:
                    corpo = out_text[i:j]
                    break
        if corpo is None:
            continue
        ruim = [c for c in re.findall(r'ThisRecord\.(\w+)', corpo)
                if c != 'Value']
        if ruim:
            die('ThisRecord.%s dentro de ForAll(Distinct(...)) — use "As <alias>"'
                % ruim[0])

    for m in re.finditer(r'ClearCollect\(\s*(\w+)\s*,(.{0,600}?)\n\s*\);',
                         out_text, re.S):
        alvo, corpo = m.group(1), m.group(2)
        if re.search(r'\b%s\b' % re.escape(alvo), corpo):
            die('ClearCollect(%s, ...) lê a própria coleção' % alvo)

    # PA2108: nenhuma propriedade que o export original não comprove
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


def die(msg):
    sys.stderr.write('ERRO: %s\n' % msg)
    sys.exit(1)


def main():
    spinner = '--spinner' in sys.argv
    sonda = '--sonda' in sys.argv
    if sonda and not spinner:
        die('--sonda só faz sentido junto com --spinner')

    with open(SRC, encoding='utf-8') as f:
        origem = f.read()
    texto = origem

    for rotulo, velho, novo, n in PATCHES:
        achou = texto.count(velho)
        if achou != n:
            die('%s: esperava %d ocorrência(s) do trecho original, achei %d.\n'
                'Primeira linha procurada:\n%s' % (rotulo, n, achou, velho.split('\n')[0]))
        # (checagem "novo já existe na origem" removida: a asserção de contagem
        # sobre `velho`, acima, já prova que o patch não foi aplicado ainda, e
        # em patches de linha curta o texto novo legitimamente já existe em
        # outro controle — ex.: outro botão que já se chamava "Excluir")
        texto = texto.replace(velho, novo, n)
        print('  ok  %s' % rotulo)

    if spinner:
        texto, n = injetar_spinner(texto, sonda=sonda)
        ADDABLE.add('LoadingSpinner')
        print('  ok  LoadingSpinner (%s) em %d galeria(s)%s'
              % (SPINNER_VALOR, n, ' [SONDA]' if sonda else ''))
        if n != (1 if sonda else 25):
            die('esperava %d galeria(s), apliquei %d' % (1 if sonda else 25, n))

    guarda_layout(origem, texto)
    validar(origem, texto)

    # conferências de resultado
    chamadas = texto.count('EnviarAtividadeparachatteams.Run(')
    if chamadas != 12:
        die('esperava 12 chamadas de EnviarAtividadeparachatteams (8 botões + encerramento + 3 exclusões de vítima), achei %d' % chamadas)
    # toda chamada tem que continuar com 2 argumentos — o esquema do gatilho
    # não mudou, e é isso que dispensa remover/re-adicionar o fluxo no Studio
    i = 0
    while True:
        i = texto.find('EnviarAtividadeparachatteams.Run(', i)
        if i < 0:
            break
        j = i + len('EnviarAtividadeparachatteams.Run')
        prof, k = 0, j
        while k < len(texto):
            c = texto[k]
            if c == '(':
                prof += 1
            elif c == ')':
                prof -= 1
                if prof == 0:
                    break
            k += 1
        corpo, d, args, ins = texto[j + 1:k], 0, 1, False
        for ch in corpo:
            if ch == '"':
                ins = not ins
            elif not ins:
                if ch in '({[':
                    d += 1
                elif ch in ')}]':
                    d -= 1
                elif ch == ',' and d == 0:
                    args += 1
        if args != 2:
            die('chamada ao fluxo de chat com %d argumentos (tem que ser 2, '
                'senão o Studio precisa recriar a conexão do fluxo)' % args)
        i = k

    if 'ThisRecord.Email' in texto:
        die('o LookUp tautológico do dedup ainda está no arquivo')
    if re.search(r'\bID_chat\.chat\b', texto):
        die('ainda há referência à variável global ID_chat')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(texto)

    print('\n%s' % os.path.relpath(OUT, HERE))
    print('  %d linhas | %d patches | sha256 %s'
          % (texto.count('\n') + 1, len(PATCHES),
             hashlib.sha256(texto.encode('utf-8')).hexdigest()[:16]))
    print('  chamadas ao fluxo de chat: %d' % chamadas)
    print('  exceções visuais declaradas: %d somem, %d surgem, %d rótulos sem emoji'
          % (len(EXCECOES_SOMEM), len(EXCECOES_SURGEM), len(EMOJI_REMOVIDOS)))


if __name__ == '__main__':
    main()
