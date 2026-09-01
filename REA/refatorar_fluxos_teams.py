#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refatora os 3 fluxos do acionamento PLEM/PRAI que falam com o Teams.

Fonte e destino: REA/MigracaoAIRPORTNOW_src/Workflows/*.json
Backup da versão anterior: REA/MigracaoAIRPORTNOW_src/Workflows_backup/

O que muda (ver PADRAO_MENSAGENS_TEAMS.md):

  M1  Toda mensagem publicada no chat passa a usar o MESMO formato
      (ícone + rótulo + hora local + ator + detalhe). Antes cada ponto do
      app montava a frase à mão ("foi acionado.", "> chegou.", "Notificado
      via Flow"), sem hora e sem hierarquia visual.
  M2  A renderização sai do app e vem para o fluxo: o app manda dados
      (Tipo, Ator, Detalhe) e o fluxo monta o HTML. Mudar o layout da
      mensagem passa a ser 1 alteração, não 9.

  T1  ANTI-TRAVAMENTO — "Responder ao app" passa a ser a PRIMEIRA ação dos
      fluxos disparados em massa. Antes o app ficava parado esperando envio
      de e-mail + post no Teams a cada contato dentro do ForAll (N contatos =
      N x ~3s de tela congelada).
  T2  ANTI-TRAVAMENTO — "Criar chat" responde logo depois de criar o chat;
      cartão, e-mail e log rodam depois da resposta.

  V1  Chat em branco -> o fluxo não posta (antes tentava postar em um chat
      inexistente e falhava).
  V2  E-mails em branco/sem "@" são descartados antes de criar o chat; se
      não sobrar ninguém o fluxo responde chat="" em vez de estourar.
  V3  Deduplicação de e-mails também no fluxo (union), defesa em profundidade.
  V4  Falha no envio do e-mail não derruba mais o acionamento (o post no
      chat e a escolha de opções continuam).
  V5  Contato sem e-mail válido gera aviso no chat + log, em vez de sumir.
  V6  Retry exponencial explícito nos posts do Teams.

  O1  A escolha de opções ganha "Não poderei comparecer", que grava
      Acao="NAO COMPARECERA"/Ativo=1 (some dos botões de ação da tela).
  O2  O cartão de abertura destaca AMBIENTE SIMULADO x EMERGÊNCIA REAL.

Rodar duas vezes deve dar o mesmo resultado (idempotente).
"""
import json
import os
import shutil
import sys

from padrao_mensagens_teams import (TIPOS, SEP, COR_REAL, COR_SIMULADO,
                                    email_acionamento, mapa_json_logicapps)

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, 'MigracaoAIRPORTNOW_src', 'Workflows')
BACKUP = os.path.join(HERE, 'MigracaoAIRPORTNOW_src', 'Workflows_backup')

F_CHAT = 'CriarchatdeacionamentosPLEMPRAI-205429A0-97CC-F011-8543-00224835DFFB.json'
F_OPCAO = 'EnviarAcionamentocomOpcao-9FC77DAD-97CC-F011-8543-00224835DFFB.json'
F_ATIV = 'EnviarAtividadeparachatteams-5554D88E-97CC-F011-8543-00224835DFFB.json'

TZ = 'E. South America Standard Time'
AUTH = {
    'value': "@json(decodeBase64(triggerOutputs().headers['X-MS-APIM-Tokens']))['$ConnectionKey']",
    'type': 'Raw',
}
RETRY = {'type': 'exponential', 'count': 4, 'interval': 'PT10S'}

HORA = "formatDateTime(convertFromUtc(utcNow(), '%s'), 'HH:mm')" % TZ
HORA_COMPLETA = "formatDateTime(convertFromUtc(utcNow(), '%s'), 'dd/MM/yyyy HH:mm:ss')" % TZ


def host(api, conn, op):
    return {'apiId': '/providers/Microsoft.PowerApps/apis/' + api,
            'connectionName': conn, 'operationId': op}


def post_teams(nome, run_after, recipient, corpo, conn='shared_teams'):
    """Ação padrão de post no chat do acionamento."""
    return nome, {
        'runAfter': run_after,
        'type': 'OpenApiConnection',
        'inputs': {
            'parameters': {
                'poster': 'Flow bot',
                'location': 'Group chat',
                'body/recipient': recipient,
                'body/messageBody': corpo,
            },
            'host': host('shared_teams', conn, 'PostMessageToConversation'),
            'authentication': AUTH,
            'retryPolicy': RETRY,
        },
    }


def corpo_msg(tipo, ator_expr, detalhe_expr=None, citacao=None):
    """
    HTML do padrão único. `citacao` recebe a EXPRESSÃO do texto que a própria
    pessoa escreveu — sai em <blockquote> e só aparece se não estiver vazia,
    para a fala dela não se confundir com texto do sistema.
    """
    html = '<p><b>%s</b> &nbsp;&#183;&nbsp; @{%s}</p>' % (TIPOS[tipo], HORA)
    html += '<p>%s</p>' % ator_expr
    if detalhe_expr:
        html += '<p>%s</p>' % detalhe_expr
    if citacao:
        html += ("@{if(empty(trim(coalesce(%s, ''))), '', "
                 "concat('<blockquote>', trim(%s), '</blockquote>'))}" % (citacao, citacao))
    return html


def severidade(param='text_4'):
    """Expressões de severidade — exercício simulado NÃO pode se parecer com
    emergência real, é a coisa mais importante da comunicação."""
    simul = "contains(toLower(coalesce(triggerBody()?['%s'], '')), 'simul')" % param
    return dict(
        cor="@{if(%s, '%s', '%s')}" % (simul, COR_SIMULADO, COR_REAL),
        titulo="@{if(%s, 'EXERCÍCIO SIMULADO', 'EMERGÊNCIA REAL')}" % simul,
        estilo="@{if(%s, 'warning', 'attention')}" % simul,
        assunto="@{if(%s, '[SIMULADO] ', '')}" % simul,
    )


def log_sp(nome, run_after, campos):
    """Create item em tbl_atividadesPlemPrai."""
    params = {
        'dataset': 'https://grupoccr.sharepoint.com/sites/AIRPORTNOW',
        'table': '7fbfd875-2edd-4599-8603-90fec5c54333',
    }
    params.update(campos)
    return nome, {
        'runAfter': run_after,
        'type': 'OpenApiConnection',
        'inputs': {
            'parameters': params,
            'host': host('shared_sharepointonline', 'shared_sharepointonline', 'PostItem'),
            'authentication': AUTH,
            'retryPolicy': RETRY,
        },
    }


def resposta_powerapp(nome, run_after, props, body):
    return nome, {
        'runAfter': run_after,
        'type': 'Response',
        'kind': 'PowerApp',
        'inputs': {
            'schema': {'type': 'object', 'properties': props, 'additionalProperties': {}},
            'statusCode': 200,
            'body': body,
        },
    }


def prop_texto(titulo):
    return {'title': titulo, 'type': 'string', 'x-ms-dynamically-added': True,
            'description': ' ""', 'x-ms-content-hint': 'TEXT'}


# ===================================================================== ATIVIDADE
def refatorar_atividade(props):
    """
    Fluxo genérico usado 9x pela tela. Vira um RENDERIZADOR.

    O ESQUEMA DO GATILHO NÃO MUDA — continua .Run(Mensagem, ID_chat). O tipo e
    o ator viajam codificados dentro de "Mensagem" como TIPO§ATOR§DETALHE.
    Ver padrao_mensagens_teams.SEP para o porquê: trocar a assinatura obrigaria
    a remover e re-adicionar o fluxo no Studio, que é onde o Power Apps
    renomeia para "..._1" e quebra o YAML colado.

    Mensagem sem "§" é publicada como sempre foi (app antigo continua
    funcionando com o fluxo novo).
    """
    d = props['definition']
    schema_antes = json.dumps(d['triggers']['manual']['inputs']['schema'],
                              sort_keys=True, ensure_ascii=False)

    mapa = mapa_json_logicapps()

    acoes = {}
    n, a = resposta_powerapp('Responder_ao_app', {},
                             {'status': {'title': 'status', 'type': 'string',
                                         'x-ms-content-hint': 'TEXT',
                                         'x-ms-dynamically-added': True}},
                             {'status': 'OK'})
    acoes[n] = a

    internas = {
        # padding com dois separadores garante índices 0/1/2 mesmo em mensagem
        # legada (sem "§"), sem estourar o split
        'Partes': {
            'runAfter': {},
            'type': 'Compose',
            'inputs': "@split(concat(coalesce(triggerBody()?['text'], ''), '%s%s'), '%s')" % (SEP, SEP, SEP),
        },
        'Estruturada': {
            'runAfter': {'Partes': ['Succeeded']},
            'type': 'Compose',
            'inputs': "@contains(coalesce(triggerBody()?['text'], ''), '%s')" % SEP,
        },
        'Rotulo': {
            'runAfter': {'Estruturada': ['Succeeded']},
            'type': 'Compose',
            'inputs': "@coalesce(json('%s')?[toupper(trim(outputs('Partes')[0]))], 'REGISTRO')" % mapa,
        },
        'Corpo': {
            'runAfter': {'Rotulo': ['Succeeded']},
            'type': 'Compose',
            'inputs': (
                "@if(outputs('Estruturada'), "
                "concat("
                "'<p><b>', outputs('Rotulo'), '</b> &nbsp;&#183;&nbsp; ', %s, '</p>', "
                "if(empty(trim(outputs('Partes')[1])), '', concat('<p>', trim(outputs('Partes')[1]), '</p>')), "
                "if(empty(trim(outputs('Partes')[2])), '', concat('<p>', trim(outputs('Partes')[2]), '</p>'))"
                "), "
                "concat('<p>', coalesce(triggerBody()?['text'], ''), '</p>')"
                ")" % HORA
            ),
        },
    }
    n, a = post_teams('Postar_mensagem_em_um_chat_ou_canal',
                      {'Corpo': ['Succeeded']},
                      "@triggerBody()?['text_1']",
                      "@outputs('Corpo')")
    internas[n] = a

    acoes['Condicao_chat_valido'] = {
        'runAfter': {'Responder_ao_app': ['Succeeded']},
        'type': 'If',
        'expression': {'and': [
            {'not': {'equals': ["@trim(coalesce(triggerBody()?['text_1'], ''))", '']}}
        ]},
        'actions': internas,
        'else': {'actions': {}},
    }
    d['actions'] = acoes

    schema_depois = json.dumps(d['triggers']['manual']['inputs']['schema'],
                               sort_keys=True, ensure_ascii=False)
    if schema_antes != schema_depois:
        raise SystemExit('ERRO: o esquema do gatilho mudou — o app quebraria.')


# ======================================================================== OPCAO
def refatorar_opcao(props):
    """Notificação individual + escolha de opções (1 execução por contato).

    É AQUI que mora o e-mail do acionamento. O fluxo de criação do chat
    mandava um segundo e-mail para a mesma lista: todo participante recebia
    duas mensagens quase idênticas em poucos segundos. Ficou só esta, que é
    personalizada (sabe o nome da pessoa e a entidade dela) e é a que
    acompanha o pedido de resposta no Teams.
    """
    d = props['definition']
    sev = severidade('text_4')
    chat = "@triggerBody()?['text_6']"
    entidade = "@{triggerBody()?['text_7']}"
    pessoa = "@{triggerBody()?['text_2']}"
    ator = '%s &#8212; %s' % (entidade, pessoa)
    protocolo = "#@{triggerBody()?['number_1']}"

    corpo_email = email_acionamento(
        cor=sev['cor'],
        kicker='ACIONAMENTO PLEM/PRAI',
        titulo=sev['titulo'],
        saudacao='Ol&#225;, <b>%s</b>.' % pessoa,
        chamada=('Voc&#234; foi acionado como <b>%s</b> para a emerg&#234;ncia abaixo, '
                 'registrada agora no aeroporto.' % entidade),
        fatos=[
            ('Aeroporto', "@{triggerBody()?['text_3']}"),
            ('Emerg&#234;ncia', "@{triggerBody()?['text_1']}"),
            ('Protocolo', protocolo),
            ('Acionado &#224;s', '@{%s}' % HORA_COMPLETA),
        ],
        ocorrencia_titulo='OCORR&#202;NCIA',
        ocorrencia="@{triggerBody()?['text_5']}",
        passos=[
            'Responda no <b>Teams</b>: o bot do Flow acabou de enviar a voc&#234; uma '
            'mensagem com as op&#231;&#245;es <b>Ciente - estou a caminho</b> e '
            '<b>N&#227;o poderei comparecer</b>. Se puder, escreva no coment&#225;rio '
            'o tempo estimado de chegada.',
            'Se tiver disponibilidade, <b>dirija-se ao COE</b> para auxiliar no '
            'gerenciamento da crise.',
            'Acompanhe tudo pelo <b>chat do acionamento</b> no Teams. Evite contato com '
            'a equipe operacional por outros canais, a fim de n&#227;o comprometer a '
            'gest&#227;o da ocorr&#234;ncia.',
        ],
        rodape=('Mensagem autom&#225;tica do <b>Airport Now</b> &#183; protocolo %s '
                '&#183; n&#227;o responda a este e-mail.' % protocolo),
    )

    acoes = {}

    # T1 — responde ANTES de qualquer I/O: o ForAll do app não trava mais.
    n, a = resposta_powerapp('Responder_ao_app', {}, {}, {})
    acoes[n] = a

    # ------------------------------------------------------- ramo e-mail válido
    ok = {}
    ok['Enviar_um_email_(V2)'] = {
        'runAfter': {},
        'type': 'OpenApiConnection',
        'inputs': {
            'host': host('shared_office365', 'shared_office365', 'SendEmailV2'),
            'parameters': {
                'emailMessage/To': "@triggerBody()?['text']",
                'emailMessage/Subject': (
                    "%sAcionamento PLEM/PRAI - @{triggerBody()?['text_3']} - "
                    "@{triggerBody()?['text_1']}" % sev['assunto']),
                'emailMessage/Body': corpo_email,
                'emailMessage/Importance': 'High',
            },
            'authentication': AUTH,
            'retryPolicy': RETRY,
        },
    }

    # V4 — o e-mail pode falhar; o acionamento segue.
    n, a = post_teams('Chat_notificado_via_Flow',
                      {'Enviar_um_email_(V2)': ['Succeeded', 'Failed', 'Skipped', 'TimedOut']},
                      chat, corpo_msg('NOTIFICADO', ator,
                                      'Aguardando confirma&#231;&#227;o'))
    ok[n] = a

    ok['Postar_uma_escolha_de_opções'] = {
        'runAfter': {'Chat_notificado_via_Flow': ['Succeeded', 'Failed', 'Skipped', 'TimedOut']},
        'limit': {'timeout': 'PT4H'},
        'type': 'OpenApiConnectionWebhook',
        'inputs': {
            'parameters': {
                'UserMessageWithOptionsSubscriptionRequest/body/options': [
                    'Ciente - estou a caminho',
                    'Não poderei comparecer',
                ],
                'UserMessageWithOptionsSubscriptionRequest/body/recipient/to': "@triggerBody()?['text']",
                'UserMessageWithOptionsSubscriptionRequest/body/messageBody': (
                    "@{triggerBody()?['text_3']} · @{triggerBody()?['text_1']}\n"
                    "Protocolo %s · @{triggerBody()?['text_4']}\n\n"
                    "Você foi acionado como @{triggerBody()?['text_7']}.\n\n"
                    "OCORRÊNCIA\n@{triggerBody()?['text_5']}\n\n"
                    "Responda abaixo. Se puder, escreva no comentário o tempo "
                    "estimado de chegada." % protocolo
                ),
                'UserMessageWithOptionsSubscriptionRequest/body/messageTitle':
                    '%s - Acionamento PLEM/PRAI' % sev['titulo'],
            },
            'host': host('shared_teams', 'shared_teams', 'SubscribeUserMessageWithOptions'),
            'authentication': AUTH,
        },
    }

    comentario = "outputs('Postar_uma_escolha_de_opções')?['body/comments']"
    hora_resp = ("@{formatDateTime(convertFromUtc(coalesce("
                 "outputs('Postar_uma_escolha_de_opções')?['body/responseTime'], utcNow()), "
                 "'%s'), 'dd/MM/yyyy HH:mm:ss')}" % TZ)
    detalhe_log = ("@{if(empty(trim(coalesce(%s, ''))), '', "
                   "concat(' · ', trim(%s)))}" % (comentario, comentario))

    # ------------------------------------------- ramo resposta: ciente x recusa
    aceite, recusa = {}, {}
    n, a = post_teams('Post_ciente', {}, chat,
                      corpo_msg('CIENTE', ator, citacao=comentario))
    aceite[n] = a
    n, a = log_sp('Log_ciente', {'Post_ciente': ['Succeeded', 'Failed', 'TimedOut']}, {
        'item/ID_acionamento': "@triggerBody()?['number_1']",
        'item/ID_entidade': "@triggerBody()?['number']",
        'item/ID_contato': "@triggerBody()?['number_2']",
        'item/ID_chat': chat,
        'item/Acao': 'RESPONDEU AO FLOW',
        'item/Atividade': 'CIENTE · %s%s' % (ator.replace('&#8212;', '—'), detalhe_log),
        'item/Hora': hora_resp,
        'item/Excluido': 0,
        'item/Ativo': 0,
    })
    aceite[n] = a

    n, a = post_teams('Post_recusa', {}, chat,
                      corpo_msg('RECUSADO', ator, citacao=comentario))
    recusa[n] = a
    n, a = log_sp('Log_recusa', {'Post_recusa': ['Succeeded', 'Failed', 'TimedOut']}, {
        'item/ID_acionamento': "@triggerBody()?['number_1']",
        'item/ID_entidade': "@triggerBody()?['number']",
        'item/ID_contato': "@triggerBody()?['number_2']",
        'item/ID_chat': chat,
        'item/Acao': 'NAO COMPARECERA',
        'item/Atividade': 'NÃO COMPARECERÁ · %s%s' % (ator.replace('&#8212;', '—'), detalhe_log),
        'item/Hora': hora_resp,
        'item/Excluido': 0,
        'item/Ativo': 1,
    })
    recusa[n] = a

    ok['Condicao_resposta'] = {
        'runAfter': {'Postar_uma_escolha_de_opções': ['Succeeded']},
        'type': 'If',
        'expression': {'and': [{'equals': [
            "@outputs('Postar_uma_escolha_de_opções')?['body/selectedOption']",
            'Não poderei comparecer',
        ]}]},
        'actions': recusa,
        'else': {'actions': aceite},
    }

    # ------------------------------------------------------------ sem resposta
    n, a = post_teams('Post_message_SemResposta',
                      {'Postar_uma_escolha_de_opções': ['TimedOut']},
                      chat, corpo_msg('SEM_RESPOSTA', ator,
                                      'Sem retorno ap&#243;s 4 horas &#8212; '
                                      'tente contato por telefone'))
    ok[n] = a
    n, a = log_sp('Create_item_SemResposta',
                  {'Post_message_SemResposta': ['Succeeded', 'Failed', 'TimedOut']}, {
                      'item/ID_acionamento': "@triggerBody()?['number_1']",
                      'item/ID_entidade': "@triggerBody()?['number']",
                      'item/ID_contato': "@triggerBody()?['number_2']",
                      'item/ID_chat': chat,
                      'item/Acao': 'SEM RESPOSTA',
                      'item/Atividade': 'SEM RESPOSTA · %s · sem retorno em 4 horas'
                                        % ator.replace('&#8212;', '—'),
                      'item/Hora': '@{%s}' % HORA_COMPLETA,
                      'item/Excluido': 0,
                      'item/Ativo': 0,
                  })
    ok[n] = a

    # ------------------------------------------------------ ramo e-mail inválido
    ruim = {}
    n, a = post_teams('Post_contato_sem_email', {}, chat,
                      corpo_msg('CONTATO_NR', ator,
                                'Sem e-mail v&#225;lido cadastrado &#8212; '
                                'acione por telefone'))
    ruim[n] = a
    n, a = log_sp('Log_contato_sem_email',
                  {'Post_contato_sem_email': ['Succeeded', 'Failed', 'TimedOut']}, {
                      'item/ID_acionamento': "@triggerBody()?['number_1']",
                      'item/ID_entidade': "@triggerBody()?['number']",
                      'item/ID_contato': "@triggerBody()?['number_2']",
                      'item/ID_chat': chat,
                      'item/Acao': 'CONTATO_NR',
                      'item/Status': 'Sem e-mail válido',
                      'item/Atividade': 'CONTATO NÃO REALIZADO · %s · sem e-mail válido cadastrado'
                                        % ator.replace('&#8212;', '—'),
                      'item/Hora': '@{%s}' % HORA_COMPLETA,
                      'item/Excluido': 0,
                      'item/Ativo': 0,
                  })
    ruim[n] = a

    acoes['Condicao_email_valido'] = {
        'runAfter': {'Responder_ao_app': ['Succeeded']},
        'type': 'If',
        'expression': {'and': [
            {'not': {'equals': ["@trim(coalesce(triggerBody()?['text'], ''))", '']}},
            {'contains': ["@coalesce(triggerBody()?['text'], '')", '@']},
        ]},
        'actions': ok,
        'else': {'actions': ruim},
    }

    d['actions'] = acoes


# ========================================================================= CHAT
def refatorar_chat(props):
    """Cria o chat do acionamento e devolve o ID para o app.

    NÃO manda mais e-mail: quem manda é o EnviarAcionamentocomOpcao, uma vez
    por pessoa e personalizado. Aqui saía um segundo e-mail para a mesma lista
    ao mesmo tempo, o que fazia todo participante receber duas mensagens quase
    iguais em poucos segundos.
    """
    d = props['definition']
    sev = severidade('text_4')
    emerg = "@{triggerBody()?['text_1']}"
    ambiente = "@{triggerBody()?['text_4']}"
    aero = "@{triggerBody()?['text_3']}"
    usuario = "@{triggerBody()?['text_2']}"
    ocorr = "@{triggerBody()?['text_5']}"
    ident = "#@{triggerBody()?['number_1']}"

    cartao = {
        '$schema': 'https://adaptivecards.io/schemas/adaptive-card.json',
        'type': 'AdaptiveCard',
        'version': '1.4',
        'body': [
            # faixa de severidade sangrando até a borda do cartão
            {'type': 'Container', 'style': sev['estilo'], 'bleed': True, 'items': [
                {'type': 'TextBlock', 'text': 'AIRPORT NOW · ACIONAMENTO PLEM/PRAI',
                 'size': 'Small', 'weight': 'Bolder', 'isSubtle': True,
                 'spacing': 'None', 'wrap': True},
                {'type': 'TextBlock', 'text': sev['titulo'],
                 'size': 'Large', 'weight': 'Bolder', 'spacing': 'None', 'wrap': True},
            ]},
            {'type': 'TextBlock', 'text': emerg, 'size': 'Medium', 'weight': 'Bolder',
             'spacing': 'Medium', 'wrap': True},
            {'type': 'FactSet', 'spacing': 'Small', 'facts': [
                {'title': 'Aeroporto', 'value': aero},
                {'title': 'Protocolo', 'value': ident},
                {'title': 'Ambiente', 'value': ambiente},
                {'title': 'Aberto por', 'value': usuario},
                {'title': 'Aberto às', 'value': '@{%s}' % HORA_COMPLETA},
            ]},
            {'type': 'TextBlock', 'text': 'OCORRÊNCIA', 'size': 'Small',
             'weight': 'Bolder', 'isSubtle': True, 'spacing': 'Medium', 'wrap': True},
            {'type': 'TextBlock', 'text': ocorr, 'spacing': 'None', 'wrap': True},
            {'type': 'Container', 'style': 'emphasis', 'spacing': 'Medium', 'items': [
                {'type': 'TextBlock', 'weight': 'Bolder', 'wrap': True,
                 'text': 'Dirija-se ao COE se tiver disponibilidade.'},
                {'type': 'TextBlock', 'isSubtle': True, 'wrap': True, 'spacing': 'Small',
                 'text': 'Toda a comunicação da ocorrência acontece neste chat. '
                         'Evite contato com a equipe operacional por outros canais, '
                         'a fim de não comprometer a gestão da ocorrência.'},
            ]},
        ],
    }

    try_actions = {}
    try_actions['Parse_JSON'] = {
        'runAfter': {},
        'type': 'ParseJson',
        'inputs': {
            'content': "@triggerBody()?['text']",
            'schema': {'type': 'array', 'items': {'type': 'object', 'properties': {
                'Email': {'type': 'string'},
                'ID_contato': {'type': 'integer'},
                'ID_entidade': {'type': 'integer'},
                'Nivel': {'type': 'string'},
                'Nome': {'type': 'string'},
            }}},
        },
    }
    try_actions['SelecionarEmails'] = {
        'runAfter': {'Parse_JSON': ['Succeeded']},
        'type': 'Select',
        'inputs': {'from': "@body('Parse_JSON')",
                   'select': "@toLower(trim(coalesce(item()?['Email'], '')))"},
    }
    # V2 — descarta em branco / sem "@"
    try_actions['EmailsValidos'] = {
        'runAfter': {'SelecionarEmails': ['Succeeded']},
        'type': 'Query',
        'inputs': {'from': "@body('SelecionarEmails')",
                   'where': "@and(not(empty(item())), contains(item(), '@'))"},
    }
    # V3 — union() com ela mesma remove duplicados
    try_actions['EmailsUnicos'] = {
        'runAfter': {'EmailsValidos': ['Succeeded']},
        'type': 'Compose',
        'inputs': "@union(body('EmailsValidos'), body('EmailsValidos'))",
    }

    com_gente = {}
    com_gente['EmailsFinal'] = {
        'runAfter': {},
        'type': 'Compose',
        'inputs': "@join(outputs('EmailsUnicos'), ';')",
    }
    com_gente['Criar_um_chat'] = {
        'runAfter': {'EmailsFinal': ['Succeeded']},
        'type': 'OpenApiConnection',
        # O app fica ESPERANDO esta ação (precisa do ID do chat) e o Power Apps
        # desiste em ~120s com 502 NoResponse. Retry exponencial de 4 tentativas
        # (10+20+40+80s) estoura esse teto sozinho. Aqui é falhar rápido: uma
        # tentativa extra e teto duro de 60s. Quem tem retry generoso são as
        # ações DEPOIS da resposta, que não seguram o app.
        'limit': {'timeout': 'PT60S'},
        'inputs': {
            'parameters': {
                'item/members': "@outputs('EmailsFinal')",
                # o título do chat é o que aparece na lista do Teams: severidade
                # primeiro, para não confundir exercício com emergência real
                'item/topic': '%s · %s · %s · %s' % (sev['titulo'], aero, ident, emerg),
            },
            'host': host('shared_teams', 'shared_teams', 'CreateChat'),
            'authentication': AUTH,
            'retryPolicy': {'type': 'fixed', 'count': 1, 'interval': 'PT5S'},
        },
    }
    depois = {}
    depois['Post_card_in_a_chat_or_channel'] = {
        'runAfter': {},
        'type': 'OpenApiConnection',
        'inputs': {
            'parameters': {
                'poster': 'Flow bot',
                'location': 'Group chat',
                'body/recipient': "@outputs('Criar_um_chat')?['body/id']",
                'body/messageBody': json.dumps(cartao, ensure_ascii=False, indent=2),
            },
            'host': host('shared_teams', 'shared_teams', 'PostCardToConversation'),
            'authentication': AUTH,
            'retryPolicy': RETRY,
        },
    }
    n, a = log_sp('Create_item',
                  {'Post_card_in_a_chat_or_channel': ['Succeeded', 'Failed', 'TimedOut']}, {
                      'item/ID_acionamento': "@triggerBody()?['number_1']",
                      'item/ID_chat': "@outputs('Criar_um_chat')?['body/id']",
                      'item/Acao': 'CHAT',
                      'item/Atividade': "Chat do acionamento criado com @{length(outputs('EmailsUnicos'))} participante(s)",
                      'item/Hora': '@{%s}' % HORA_COMPLETA,
                      'item/Excluido': 0,
                      'item/Ativo': 1,
                  })
    depois[n] = a

    # ------------------------------------------------------------------------
    # Estrutura PLANA, sem Scope/Try-Catch. Motivo: a resposta ao app precisa
    # ser alcançável a partir de QUALQUER caminho de execução. Na versão
    # anterior ela estava aninhada dentro de um If dentro de um Scope e só
    # rodava se `Criar_um_chat` desse Succeeded; o resgate ficava no
    # Scope_Catch, que precisava do Scope inteiro falhar primeiro — e, se a
    # resposta já tivesse sido enviada, o Respond_erro ainda tentava responder
    # de novo. Qualquer buraco aí vira 502 NoResponse no app.
    #
    # Agora `Respond_to_a_Power_App_or_flow` está no topo com runAfter aceitando
    # os QUATRO status. Não existe execução que não passe por ela:
    #   Parse_JSON falha  -> tudo Skipped -> responde chat ""
    #   sem participantes -> If pula      -> responde chat ""
    #   CreateChat falha  -> If Failed    -> responde chat ""
    #   caminho feliz     -> responde o ID do chat
    # ------------------------------------------------------------------------
    try_actions['Condicao_tem_participantes'] = {
        'runAfter': {'EmailsUnicos': ['Succeeded']},
        'type': 'If',
        'expression': {'and': [
            {'greaterOrEquals': ["@length(outputs('EmailsUnicos'))", 1]}
        ]},
        'actions': com_gente,
        'else': {'actions': {}},
    }
    n, a = resposta_powerapp(
        'Respond_to_a_Power_App_or_flow',
        {'Condicao_tem_participantes': ['Succeeded', 'Failed', 'Skipped', 'TimedOut']},
        {'chat': {'title': 'CHAT', 'type': 'string',
                  'x-ms-content-hint': 'TEXT', 'x-ms-dynamically-added': True}},
        {'chat': "@{coalesce(outputs('Criar_um_chat')?['body/id'], '')}"})
    try_actions[n] = a

    # Sem chat, registra o MOTIVO no log do acionamento. Antes a falha era
    # silenciosa: o app avisava "o chat não foi criado" e não havia onde
    # descobrir por quê sem abrir o histórico de execução do fluxo.
    sem_chat = {}
    motivo = ("@if(empty(coalesce(string(body('Criar_um_chat')), '')), "
              "'Nenhum participante valido, ou o Teams recusou a criacao do chat', "
              "string(body('Criar_um_chat')))")
    sem_chat['Motivo_falha_chat'] = {
        'runAfter': {}, 'type': 'Compose', 'inputs': motivo,
    }
    n, a = log_sp('Log_falha_chat', {'Motivo_falha_chat': ['Succeeded']}, {
        'item/ID_acionamento': "@triggerBody()?['number_1']",
        'item/Acao': 'ERRO CHAT',
        'item/Status': 'Chat do Teams não criado',
        # trunca em 300 para não estourar coluna de texto do SharePoint
        'item/Atividade': ("@{concat('ERRO AO CRIAR O CHAT · ', substring("
                           "outputs('Motivo_falha_chat'), 0, "
                           "min(300, length(outputs('Motivo_falha_chat')))))}"),
        'item/Hora': '@{%s}' % HORA_COMPLETA,
        'item/Excluido': 0,
        'item/Ativo': 1,
    })
    sem_chat[n] = a

    # cartão e log só fazem sentido se o chat existe; rodam depois da resposta
    try_actions['Condicao_chat_criado'] = {
        'runAfter': {'Respond_to_a_Power_App_or_flow': ['Succeeded']},
        'type': 'If',
        'expression': {'and': [
            {'not': {'equals': ["@coalesce(outputs('Criar_um_chat')?['body/id'], '')", '']}}
        ]},
        'actions': depois,
        'else': {'actions': sem_chat},
    }

    d['actions'] = try_actions


# ========================================================================= MAIN
def podar_conexoes(props):
    """Remove connection reference de conector que o fluxo não usa mais.

    O CriarChat deixou de mandar e-mail; sem podar, a importação continuaria
    pedindo uma conexão do Outlook que nunca seria usada.
    """
    usados = set()

    def varrer(acoes):
        for a in acoes.values():
            ent = a.get('inputs')
            cn = ent.get('host', {}).get('connectionName') if isinstance(ent, dict) else None
            if cn:
                usados.add(cn)
            if 'actions' in a:
                varrer(a['actions'])
            if 'else' in a:
                varrer(a['else'].get('actions', {}))

    varrer(props['definition']['actions'])
    refs = props.get('connectionReferences') or {}
    removidos = [k for k in refs if k not in usados]
    for k in removidos:
        del refs[k]
    return removidos


def carregar(nome):
    with open(os.path.join(WF, nome), encoding='utf-8') as f:
        return json.load(f)


def gravar(nome, obj):
    """CRLF e sem BOM, igual ao que o export da solução produz."""
    txt = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
    with open(os.path.join(WF, nome), 'wb') as f:
        f.write(txt.replace('\n', '\r\n').encode('utf-8'))


def main():
    if not os.path.isdir(BACKUP):
        shutil.copytree(WF, BACKUP)
        print('backup -> %s' % os.path.relpath(BACKUP, HERE))

    for nome, fn in ((F_ATIV, refatorar_atividade),
                     (F_OPCAO, refatorar_opcao),
                     (F_CHAT, refatorar_chat)):
        doc = carregar(nome)
        fn(doc['properties'])
        podados = podar_conexoes(doc['properties'])
        gravar(nome, doc)
        conectores = sorted(doc['properties'].get('connectionReferences') or {})
        print('%-32s %s%s' % (nome.split('-')[0], ', '.join(conectores),
                              '   (podado: %s)' % ', '.join(podados) if podados else ''))


if __name__ == '__main__':
    main()
