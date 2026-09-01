#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrai as mensagens REAIS de dentro dos fluxos gerados e substitui as
expressões @{...} do Power Automate por dados de exemplo, para conferir o
design antes de importar. Não inventa markup: o que sai aqui é exatamente o
que o Power Automate vai mandar.

Saída: REA/previa/previa_mensagens.html
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, 'MigracaoAIRPORTNOW_src', 'Workflows')
F_CHAT = 'CriarchatdeacionamentosPLEMPRAI-205429A0-97CC-F011-8543-00224835DFFB.json'
F_OPCAO = 'EnviarAcionamentocomOpcao-9FC77DAD-97CC-F011-8543-00224835DFFB.json'
F_ATIV = 'EnviarAtividadeparachatteams-5554D88E-97CC-F011-8543-00224835DFFB.json'

EXEMPLO = {
    'text': 'juliana.nascimento@motiva.com.br',
    'text_1': 'Aeronave em emergência — pouso forçado',
    'text_2': 'Juliana do Nascimento',
    'text_3': 'SLZ — Marechal Cunha Machado',
    'text_4': 'Ambiente Real',
    'text_5': ('Aeronave ATR-72, 68 pessoas a bordo, reportou falha hidráulica e '
               'solicita pouso prioritário. Previsão de toque em 14 minutos. '
               'Pista 06 liberada, SCI a postos.'),
    'text_6': '19:meeting_abc123@thread.v2',
    'text_7': 'Corpo de Bombeiros',
    'number': '412',
    'number_1': '1287',
    'number_2': '3391',
}
HORA = '12:47'
HORA_COMPLETA = '24/08/2026 12:47:31'


def resolver(txt, simulado=False):
    """Troca as expressões do Logic Apps pelos valores de exemplo."""
    # severidade: @{if(contains(...'simul'), 'A', 'B')} -> A ou B
    txt = re.sub(
        r"@\{if\(contains\(toLower\(coalesce\(triggerBody\(\)\?\['text_4'\], ''\)\), "
        r"'simul'\), '([^']*)', '([^']*)'\)\}",
        lambda m: m.group(1) if simulado else m.group(2), txt)
    # hora
    txt = re.sub(r"@\{formatDateTime\(convertFromUtc\(utcNow\(\)[^}]*'dd/MM/yyyy HH:mm:ss'\)\}",
                 HORA_COMPLETA, txt)
    txt = re.sub(r"@\{formatDateTime\(convertFromUtc\(utcNow\(\)[^}]*'HH:mm'\)\}", HORA, txt)
    # parâmetros do gatilho
    for k, v in EXEMPLO.items():
        txt = txt.replace("@{triggerBody()?['%s']}" % k, v)
        txt = txt.replace("@{triggerBody()['%s']}" % k, v)
    # blocos opcionais (comentário da pessoa) -> mostra preenchido
    txt = re.sub(r"@\{if\(empty\(trim\(coalesce\(outputs\('[^']+'\)\?\['body/comments'\], ''\)\)\), '', "
                 r"concat\('<blockquote>', trim\(outputs\('[^']+'\)\?\['body/comments'\]\), '</blockquote>'\)\)\}",
                 '<blockquote>Saindo agora do posto 2, chego ao COE em 10 minutos.</blockquote>', txt)
    txt = txt.replace("@{length(outputs('EmailsUnicos'))}", '7')
    return txt


def achar(acoes, cond, saida=None):
    saida = saida if saida is not None else []
    for nome, a in acoes.items():
        if cond(nome, a):
            saida.append((nome, a))
        if 'actions' in a:
            achar(a['actions'], cond, saida)
        if 'else' in a:
            achar(a['else'].get('actions', {}), cond, saida)
    return saida


def carregar(f):
    return json.load(open(os.path.join(WF, f), encoding='utf-8'))['properties']['definition']


def extrair():
    chat = carregar(F_CHAT)
    opcao = carregar(F_OPCAO)
    ativ = carregar(F_ATIV)

    email = achar(opcao['actions'], lambda n, a: isinstance(a.get('inputs'), dict)
                  and a['inputs'].get('host', {}).get('operationId') == 'SendEmailV2')[0][1]
    cartao = achar(chat['actions'], lambda n, a: isinstance(a.get('inputs'), dict)
                   and a['inputs'].get('host', {}).get('operationId') == 'PostCardToConversation')[0][1]
    escolha = achar(opcao['actions'], lambda n, a: a.get('type') == 'OpenApiConnectionWebhook')[0][1]
    posts = achar(opcao['actions'], lambda n, a: isinstance(a.get('inputs'), dict)
                  and a['inputs'].get('host', {}).get('operationId') == 'PostMessageToConversation')
    topico = achar(chat['actions'], lambda n, a: isinstance(a.get('inputs'), dict)
                   and a['inputs'].get('host', {}).get('operationId') == 'CreateChat')[0][1]

    return dict(
        assunto=email['inputs']['parameters']['emailMessage/Subject'],
        email=email['inputs']['parameters']['emailMessage/Body'],
        cartao=json.loads(cartao['inputs']['parameters']['body/messageBody']),
        topico=topico['inputs']['parameters']['item/topic'],
        escolha_titulo=escolha['inputs']['parameters'][
            'UserMessageWithOptionsSubscriptionRequest/body/messageTitle'],
        escolha_corpo=escolha['inputs']['parameters'][
            'UserMessageWithOptionsSubscriptionRequest/body/messageBody'],
        escolha_opcoes=escolha['inputs']['parameters'][
            'UserMessageWithOptionsSubscriptionRequest/body/options'],
        posts=[(n, a['inputs']['parameters']['body/messageBody']) for n, a in posts],
        renderizador=achar(ativ['actions'],
                           lambda n, a: n == 'Corpo')[0][1]['inputs'],
    )


if __name__ == '__main__':
    d = extrair()
    print('assunto :', resolver(d['assunto']))
    print('tópico  :', resolver(d['topico']))
    print('e-mail  : %d chars de HTML' % len(d['email']))
    print('cartão  : %d blocos' % len(d['cartao']['body']))
    print('posts   :', [n for n, _ in d['posts']])
