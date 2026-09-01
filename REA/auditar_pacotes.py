#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audita os zips de fluxos_individuais/ — os arquivos que serão importados de
fato, não a pasta de origem. Cada item é uma mudança prometida; a evidência
sai do JSON de dentro do zip.
"""
import json
import zipfile

PACOTES = {
    'CriarChat': 'fluxos_individuais/CriarChatAcionamentosPLEMPRAI.zip',
    'AcionamentoComOpcao': 'fluxos_individuais/EnviarAcionamentoComOpcao.zip',
    'AtividadeParaChat': 'fluxos_individuais/EnviarAtividadeParaChatTeams.zip',
}


def definicao(zpath):
    z = zipfile.ZipFile(zpath)
    n = [x for x in z.namelist() if x.endswith('definition.json')][0]
    return json.loads(z.read(n).decode('utf-8'))['properties']


def achatar(acoes, saida=None):
    saida = {} if saida is None else saida
    for nome, a in acoes.items():
        saida[nome] = a
        if 'actions' in a:
            achatar(a['actions'], saida)
        if 'else' in a:
            achatar(a['else'].get('actions', {}), saida)
    return saida


def main():
    p = {k: definicao(v) for k, v in PACOTES.items()}
    a = {k: achatar(v['definition']['actions']) for k, v in p.items()}
    bruto = {k: json.dumps(v, ensure_ascii=False) for k, v in p.items()}

    checagens = []

    def ok(grupo, item, cond, evidencia=''):
        checagens.append((grupo, item, bool(cond), evidencia))

    # ------------------------------------------------------------- E-MAIL
    em = [x for x in a['AcionamentoComOpcao'].values()
          if isinstance(x.get('inputs'), dict)
          and x['inputs'].get('host', {}).get('operationId') == 'SendEmailV2']
    corpo = em[0]['inputs']['parameters']['emailMessage/Body'] if em else ''
    assunto = em[0]['inputs']['parameters']['emailMessage/Subject'] if em else ''
    ok('E-MAIL', 'existe um e-mail no fluxo de notificação', len(em) == 1,
       '%d ação(ões) SendEmailV2' % len(em))
    ok('E-MAIL', 'e-mail duplicado removido do CriarChat',
       'SendEmailV2' not in bruto['CriarChat'], 'nenhuma ação de e-mail')
    ok('E-MAIL', 'layout em tabela (Outlook = motor do Word)',
       corpo.count('<table') >= 5, '%d <table>' % corpo.count('<table'))
    ok('E-MAIL', 'sem flexbox/grid/float/<style>',
       not any(x in corpo for x in ('display:flex', 'display:grid', 'float:', '<style')))
    ok('E-MAIL', 'largura travada em 600px', 'width="600"' in corpo)
    ok('E-MAIL', 'severidade por chip + barra fina (não bloco chapado)',
       '#A62639' in corpo and '#8A6100' in corpo and 'height:3px' in corpo,
       'vermelho institucional + âmbar')
    ok('E-MAIL', 'cabeçalho branco com wordmark navy',
       'AIRPORT NOW' in corpo and '#0B2E4F' in corpo and 'letter-spacing:2px' in corpo)
    ok('E-MAIL', 'saudação pelo nome da pessoa',
       "Ol&#225;, <b>@{triggerBody()?['text_2']}</b>" in corpo)
    ok('E-MAIL', 'diz a entidade pela qual foi acionado',
       "acionado como <b>@{triggerBody()?['text_7']}</b>" in corpo)
    ok('E-MAIL', 'bloco de fatos (aeroporto/emergência/protocolo/hora)',
       corpo.count('Protocolo') >= 1 and 'Acionado &#224;s' in corpo)
    ok('E-MAIL', 'ocorrência em bloco destacado', 'border-left:3px solid' in corpo)
    ok('E-MAIL', '"O QUE FAZER AGORA" em passos numerados',
       'O QUE FAZER AGORA' in corpo)
    ok('E-MAIL', 'rodapé com "não responda a este e-mail"',
       'n&#227;o responda a este e-mail' in corpo)
    ok('E-MAIL', 'assunto marca [SIMULADO] quando é exercício',
       "'[SIMULADO] '" in assunto)
    ok('E-MAIL', 'texto antigo "Prezados" eliminado', 'Prezados' not in corpo)

    import re as _re
    _EM = _re.compile('[\U0001F300-\U0001FAFF\u2699\u26a0\u274c\u2795\u2757\u2705\u26d4\u23f1\u25ab]')
    ok('E-MAIL', 'sem emoji no corpo', not _EM.search(corpo))
    ok('E-MAIL', 'sem emoji no assunto', not _EM.search(assunto), assunto[:60])

    # -------------------------------------------------------------- CARTÃO
    card = [x for x in a['CriarChat'].values()
            if isinstance(x.get('inputs'), dict)
            and x['inputs'].get('host', {}).get('operationId') == 'PostCardToConversation']
    cj = card[0]['inputs']['parameters']['body/messageBody'] if card else '{}'
    c = json.loads(cj)
    tipos = [b['type'] for b in c.get('body', [])]
    ok('CARTÃO', 'é Adaptive Card', c.get('type') == 'AdaptiveCard',
       'versão %s' % c.get('version'))
    ok('CARTÃO', 'faixa de severidade sangrada (bleed)',
       any(b.get('bleed') for b in c.get('body', [])))
    ok('CARTÃO', 'estilo muda com o ambiente (warning x attention)',
       "'warning', 'attention'" in cj)
    ok('CARTÃO', 'FactSet com os dados da ocorrência', 'FactSet' in tipos)
    ok('CARTÃO', 'bloco final de instrução em emphasis',
       any(b.get('style') == 'emphasis' for b in c.get('body', [])))
    ok('CARTÃO', 'mensagem separada de "Ocorrência" foi absorvida',
       bruto['CriarChat'].count('PostMessageToConversation') == 0)

    topico = [x for x in a['CriarChat'].values()
              if isinstance(x.get('inputs'), dict)
              and x['inputs'].get('host', {}).get('operationId') == 'CreateChat'][0]
    tp = topico['inputs']['parameters']['item/topic']
    ok('CARTÃO', 'título do chat leva severidade na frente',
       "'EXERCÍCIO SIMULADO', 'EMERGÊNCIA REAL'" in tp)

    # --------------------------------------------------------------- CHAT
    posts = {k: v['inputs']['parameters']['body/messageBody']
             for k, v in a['AcionamentoComOpcao'].items()
             if isinstance(v.get('inputs'), dict)
             and v['inputs'].get('host', {}).get('operationId') == 'PostMessageToConversation'}
    todos = ' '.join(posts.values())
    ok('CHAT', 'ícone + rótulo em negrito nas linhas', todos.count('<b>') == len(posts),
       '%d de %d' % (todos.count('<b>'), len(posts)))
    ok('CHAT', 'hora local em toda linha',
       all("formatDateTime" in v and "'HH:mm'" in v for v in posts.values()))
    ok('CHAT', 'fala da pessoa em <blockquote>', '<blockquote>' in todos)
    ok('CHAT', 'citação some quando o comentário está vazio',
       "if(empty(trim(coalesce(outputs(" in todos)
    ok('CHAT', 'texto antigo "Notificado via Flow" eliminado',
       'Notificado via Flow' not in todos)
    ok('CHAT', 'texto antigo "Respondeu ao Flow" eliminado',
       'Respondeu ao Flow' not in todos)
    for rot in ('NOTIFICADO', 'CIENTE', 'NÃO COMPARECERÁ', 'SEM RESPOSTA',
                'CONTATO NÃO REALIZADO'):
        ok('CHAT', 'rótulo "%s" presente' % rot, rot in todos)

    # ------------------------------------------------------- RENDERIZADOR
    ren = a['AtividadeParaChat']['Corpo']['inputs']
    rot = a['AtividadeParaChat']['Rotulo']['inputs']
    ok('RENDERIZADOR', 'mapa de tipos com ícone + rótulo', rot.count('": "') >= 16,
       '%d tipos' % rot.count('": "'))
    for t in ('ACIONADO', 'CHEGOU', 'SOBREAVISO', 'INFORMADO', 'EQUIPAMENTO',
              'VÍTIMA REGISTRADA', 'REGISTRO MANUAL', 'ACIONAMENTO ENCERRADO'):
        ok('RENDERIZADOR', 'tipo "%s"' % t, t in rot)
    ok('RENDERIZADOR', 'tipo desconhecido cai em padrão', 'REGISTRO' in rot and 'coalesce' in rot)
    ok('RENDERIZADOR', 'mensagem legada (sem §) continua publicando',
       "contains(coalesce(triggerBody()?['text'], ''), '§')" in a['AtividadeParaChat']['Estruturada']['inputs'])
    ok('RENDERIZADOR', 'hora local na linha', "'HH:mm'" in ren)

    # ------------------------------------------------------------ OPÇÕES
    esc = [x for x in a['AcionamentoComOpcao'].values()
           if x.get('type') == 'OpenApiConnectionWebhook'][0]['inputs']['parameters']
    opc = esc['UserMessageWithOptionsSubscriptionRequest/body/options']
    ok('OPÇÕES', 'duas opções de resposta', len(opc) == 2, ' | '.join(opc))
    ok('OPÇÕES', 'recusa grava Acao NAO COMPARECERA',
       'NAO COMPARECERA' in bruto['AcionamentoComOpcao'])
    ok('OPÇÕES', 'recusa some das pendências (Ativo=1)',
       a['AcionamentoComOpcao']['Log_recusa']['inputs']['parameters']['item/Ativo'] == 1)
    ok('OPÇÕES', 'título da mensagem marca severidade',
       "'EXERCÍCIO SIMULADO', 'EMERGÊNCIA REAL'" in
       esc['UserMessageWithOptionsSubscriptionRequest/body/messageTitle'])

    # ---------------------------------------------------- ROBUSTEZ / APP
    for k in PACOTES:
        topo = [n for n, v in p[k]['definition']['actions'].items()
                if v.get('type') == 'Response']
        ok('ROBUSTEZ', '%s: resposta ao app no nível superior' % k, len(topo) == 1,
           topo[0] if topo else '—')
    resp = p['CriarChat']['definition']['actions']['Respond_to_a_Power_App_or_flow']
    ok('ROBUSTEZ', 'CriarChat: resposta alcançável nos 4 status',
       sorted(list(resp['runAfter'].values())[0]) ==
       ['Failed', 'Skipped', 'Succeeded', 'TimedOut'])
    cc = a['CriarChat']['Criar_um_chat']
    ok('ROBUSTEZ', 'CreateChat com teto de 60s', cc.get('limit', {}).get('timeout') == 'PT60S')
    ok('ROBUSTEZ', 'CreateChat sem retry longo',
       cc['inputs']['retryPolicy']['type'] == 'fixed')
    ok('ROBUSTEZ', 'AcionamentoComOpcao responde antes de qualquer I/O',
       p['AcionamentoComOpcao']['definition']['actions']['Responder_ao_app']['runAfter'] == {})
    ok('ROBUSTEZ', 'AtividadeParaChat responde antes de postar',
       p['AtividadeParaChat']['definition']['actions']['Responder_ao_app']['runAfter'] == {})
    ok('ROBUSTEZ', 'falha de e-mail não derruba o acionamento',
       'Failed' in a['AcionamentoComOpcao']['Chat_notificado_via_Flow']['runAfter']['Enviar_um_email_(V2)'])
    ok('ROBUSTEZ', 'AtividadeParaChat não posta com chat em branco',
       'Condicao_chat_valido' in a['AtividadeParaChat'])
    ok('ROBUSTEZ', 'CriarChat descarta e-mail inválido', 'EmailsValidos' in a['CriarChat'])
    ok('ROBUSTEZ', 'CriarChat deduplica e-mails (union)',
       'union(' in a['CriarChat']['EmailsUnicos']['inputs'])
    ok('ROBUSTEZ', 'contato sem e-mail vira aviso no chat',
       'Post_contato_sem_email' in a['AcionamentoComOpcao'])
    ok('ROBUSTEZ', 'CriarChat não pede mais conexão do Outlook',
       'shared_office365' not in (p['CriarChat'].get('connectionReferences') or {}))
    for k in PACOTES:
        props = list(p[k]['definition']['triggers']['manual']['inputs']['schema']['properties'])
        esperado = {'CriarChat': 7, 'AcionamentoComOpcao': 11, 'AtividadeParaChat': 2}[k]
        ok('ROBUSTEZ', '%s: gatilho com %d parâmetros (inalterado)' % (k, esperado),
           len(props) == esperado, ', '.join(props))

    # ------------------------------------------------------------ relatório
    grupo_atual = None
    falhas = 0
    for g, item, passou, ev in checagens:
        if g != grupo_atual:
            print('\n\033[1m%s\033[0m' % g)
            grupo_atual = g
        marca = ' ok ' if passou else 'FALHA'
        print('  [%s] %-52s %s' % (marca, item, ev))
        falhas += not passou
    bruto_tudo = ' '.join(bruto.values())
    for g, item, passou, ev in [('SEM EMOJI', 'nenhum emoji nos 3 fluxos',
                                 not _EM.search(bruto_tudo), '')]:
        checagens.append((g, item, passou, ev))
        print('\n\033[1m%s\033[0m' % g)
        print('  [%s] %-52s %s' % (' ok ' if passou else 'FALHA', item, ev))
        falhas += not passou

    print('\n%d verificações · %d falha(s)' % (len(checagens), falhas))
    return falhas


if __name__ == '__main__':
    raise SystemExit(1 if main() else 0)
