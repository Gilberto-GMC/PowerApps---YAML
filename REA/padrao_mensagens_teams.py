#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Padrão único das mensagens do acionamento PLEM/PRAI — e a paleta corporativa.

Este módulo é a ÚNICA fonte da verdade do formato e das cores. Importado por:
  - refatorar_fluxos_teams.py  (renderização dentro do Power Automate)
  - refatorar_msgs_teams.py    (chamadas .Run() e componentes HTML da tela)
  - previa_artefato.py         (página de conferência)
  - a documentação PADRAO_MENSAGENS_TEAMS.md

SEM EMOJI em nenhum canal (decisão do usuário, 2026-08-24): Outlook não aceita
SVG nem imagem externa, Adaptive Card 1.4 não tem Icon, o chat do Teams remove
estilo e o HtmlViewer do Power Apps remove <svg>. Ícone de verdade não existe
em nenhum dos meios — então a identidade é tipografia + cor + chips de texto.

Formato publicado no chat (uma mensagem = um evento):

    <b>{RÓTULO}</b> · {HH:mm}
    {Ator}
    {Detalhe}            (só quando existe)

No SharePoint (tbl_atividadesPlemPrai.Atividade) grava-se o mesmo:

    {RÓTULO} · {Ator} · {Detalhe}
"""

# ============================================================ paleta corporativa
# Derivada dos azuis já usados nos componentes HTML mais recentes do app
# (#0B2E4F em HtmlText9/HtmlText11_1). Um navy de marca, um azul de ação e
# semânticos dessaturados — nada de #FFFF00/#FF0000 puros.
NAVY = '#0B2E4F'          # marca / títulos
ACAO = '#155E8F'          # azul de ação / links
COR_REAL = '#A62639'      # vermelho institucional — emergência real
COR_SIMULADO = '#8A6100'  # âmbar sóbrio — exercício simulado (AA sobre branco)

TXT = '#22303B'           # texto principal
TXT2 = '#5D6B77'          # texto secundário
FUNDO = '#F5F7F9'         # fundo de página / bloco
LINHA = '#DFE5EA'         # divisores / bordas
FONTE = "'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

# Cores de status DENTRO do app (Fill/Color por Acao + chips dos HtmlText).
# Cada entrada: fundo do chip/faixa, cor do texto sobre esse fundo.
STATUS_APP = {
    'ACIONAR':            ('#B98900', '#FFFFFF'),  # substitui o #FFFF00 puro
    'ACIONAR_SOBREAVISO': ('#B98900', '#FFFFFF'),
    'RESPONDEU AO FLOW':  ('#B98900', '#FFFFFF'),  # nuance por Nivel fica nos Switch
    'SOBREAVISO':         ('#C05621', '#FFFFFF'),
    'INFORMAR':           ('#155E8F', '#FFFFFF'),
    'NOTIFICADO':         ('#E8EDF2', '#22303B'),
    'CHEGOU':             ('#1F7A4D', '#FFFFFF'),
    'CONTATO_NR':         ('#A62639', '#FFFFFF'),
    'NAO COMPARECERA':    ('#A62639', '#FFFFFF'),
    'CRIAÇÃO':            ('#0B2E4F', '#FFFFFF'),
    'FINALIZAÇÃO':        ('#0B2E4F', '#FFFFFF'),
    'ATIVIDADE MANUAL':   ('#5D6B77', '#FFFFFF'),
    'REGISTRO DE VÍTIMA': ('#7A4E82', '#FFFFFF'),
    'ALTERAÇÃO DE VÍTIMA': ('#7A4E82', '#FFFFFF'),
    'EXCLUSÃO DE VÍTIMA': ('#7A4E82', '#FFFFFF'),
    'CHAT':               ('#5D6B77', '#FFFFFF'),
    'ERRO CHAT':          ('#A62639', '#FFFFFF'),
    'SEM RESPOSTA':       ('#5D6B77', '#FFFFFF'),
}
STATUS_APP_DEFAULT = ('#E8EDF2', '#22303B')

# ---------------------------------------------------------------- superfícies
# MESMOS matizes do STATUS_APP, em versão clara.
#
# Por que dois pesos e não um só: o chip da lista de atividades é pequeno e
# leva texto branco sobre cor forte; a legenda e as pílulas do fluxograma são
# superfícies grandes que carregam texto PRETO (Color herdado do controle).
# Usar a cor forte nelas obrigaria a calcular também a cor do texto — e o
# texto é outra propriedade, ou seja, outra consulta ao SharePoint por linha
# do fluxograma (hoje é 1, viraria 2 em ~N entidades x 3 colunas). Numa tela
# que já teve queixa de travamento, o preço não se paga.
#
# Então: mesmo matiz = mesmo significado; peso diferente = papel diferente
# (chip x superfície). Contraste de todas com o texto #22303B >= 4.5:1.
SUPERFICIE_APP = {
    'NENHUMA':            '#FFFFFF',   # sem atividade registrada
    'NOTIFICADO':         '#E8EDF2',   # idêntico ao chip (o chip já é claro)
    'ACIONAR':            '#E8C25E',   # âmbar   <- #B98900
    'ACIONAR_SOBREAVISO': '#E8C25E',
    'RESPONDEU AO FLOW':  '#E8C25E',
    'SOBREAVISO':         '#E59468',   # laranja <- #C05621
    'INFORMAR':           '#6BA7D1',   # azul    <- #155E8F
    'CHEGOU':             '#6BBF95',   # verde   <- #1F7A4D
    'CONTATO_NR':         '#E08E9C',   # vermelho<- #A62639
    'NAO COMPARECERA':    '#E08E9C',
}


def rgba(hexcor, alfa=1):
    """'#E8C25E' -> 'RGBA(232, 194, 94, 1)' (sintaxe invariante do .pa.yaml)."""
    h = hexcor.lstrip('#')
    return 'RGBA(%d, %d, %d, %s)' % (
        int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alfa)

# ================================================================ tipos de evento
# chave -> rótulo (sem emoji; a hierarquia vem do <b> e da hora)
TIPOS = {
    'ABERTURA':        'ACIONAMENTO ABERTO',
    'NOTIFICADO':      'NOTIFICADO',
    'CIENTE':          'CIENTE',
    'RECUSADO':        'NÃO COMPARECERÁ',
    'SEM_RESPOSTA':    'SEM RESPOSTA',
    'ACIONADO':        'ACIONADO',
    'SOBREAVISO':      'SOBREAVISO',
    'INFORMADO':       'INFORMADO',
    'CHEGOU':          'CHEGOU',
    'CONTATO_NR':      'CONTATO NÃO REALIZADO',
    'EQUIPAMENTO':     'EQUIPAMENTO SOLICITADO',
    'VITIMA_NOVA':     'VÍTIMA REGISTRADA',
    'VITIMA_ALTERADA': 'VÍTIMA ATUALIZADA',
    'VITIMA_EXCLUIDA': 'VÍTIMA REMOVIDA',
    'MANUAL':          'REGISTRO MANUAL',
    'ENCERRADO':       'ACIONAMENTO ENCERRADO',
}

FALLBACK = 'REGISTRO'

# Separador do payload que o app manda no parâmetro "Mensagem" do fluxo
# EnviarAtividadeparachatteams:
#
#     TIPO§ATOR§DETALHE
#
# Por que codificar em vez de criar parâmetros novos: o gatilho PowerApps V2
# guarda o esquema no app. Trocar 2 parâmetros por 4 obrigaria a REMOVER e
# RE-ADICIONAR o fluxo no Studio — e é aí que o Power Apps renomeia para
# "EnviarAtividadeparachatteams_1" e o YAML colado deixa de encontrar a
# referência. Mantendo o esquema byte a byte, a atualização do fluxo é
# invisível para o app.
#
# Compatibilidade nos dois sentidos:
#   fluxo novo + app velho -> mensagem sem "§", publicada como sempre foi
#   fluxo velho + app novo -> aparece "CHEGOU§Entidade — Nome§" no chat:
#                             feio por alguns minutos, nunca um erro
#
# O app remove "§" de qualquer texto livre antes de montar o payload, então
# os índices 0/1/2 são sempre confiáveis.
SEP = '§'


def payload(tipo, ator_powerfx, detalhe_powerfx='""'):
    """Monta a expressão Power Fx do payload (usada pelo gerador da tela)."""
    return '"%s%s" & %s & "%s" & %s' % (tipo, SEP, ator_powerfx, SEP, detalhe_powerfx)


def rotulo(tipo):
    """Rótulo do evento, como a tela grava em tbl_atividadesPlemPrai.Atividade."""
    return TIPOS[tipo]


def mapa_json_logicapps():
    """String JSON compacta consumida por json(...) dentro do Power Automate."""
    import json
    return json.dumps(TIPOS, ensure_ascii=False)


def chip_html(texto, fundo, texto_cor, tamanho=10):
    """Chip de texto (usado nos HtmlText do app — o HtmlViewer remove <svg>)."""
    return ("<span style=\"display:inline-block;padding:1px 8px;border-radius:9px;"
            "background:%s;color:%s;font-size:%dpx;font-weight:600;"
            "letter-spacing:0.4px;\">%s</span>" % (fundo, texto_cor, tamanho, texto))


# =============================================================== e-mail (HTML)
# Regras do meio: o Outlook desktop renderiza com o motor do Word — nada de
# flexbox, grid, float ou <style> confiável. Layout = tabelas aninhadas com
# cellpadding/cellspacing zerados e TUDO em style inline. Largura travada em
# 600px. Cabeçalho BRANCO com wordmark navy + chip de severidade + barra fina
# de 3px no topo (decisão do usuário: nada de bloco de cor chapado).

def _fato(rotulo_, valor):
    return (
        '<tr>'
        '<td valign="top" style="padding:6px 12px 6px 0;font-family:%(f)s;font-size:13px;'
        'line-height:18px;color:%(t2)s;white-space:nowrap;">%(r)s</td>'
        '<td valign="top" style="padding:6px 0;font-family:%(f)s;font-size:14px;'
        'line-height:20px;color:%(t)s;font-weight:600;">%(v)s</td>'
        '</tr>'
    ) % dict(f=FONTE, t=TXT, t2=TXT2, r=rotulo_, v=valor)


def email_acionamento(cor, kicker, titulo, saudacao, chamada, fatos,
                      ocorrencia_titulo, ocorrencia, passos, rodape):
    """
    Ordem narrativa: o que aconteceu -> onde -> o que EU tenho a ver com isso
    -> o que faço agora -> por onde respondo. Quem abre no celular no meio de
    uma emergência lê as três primeiras linhas e nada mais; elas têm que bastar.

    `cor` é a cor de severidade (COR_REAL/COR_SIMULADO ou expressão do Logic
    Apps que resolve para uma delas); aparece só na barra de 3px, no chip e
    nos acentos — nunca como bloco.
    """
    linhas_fatos = ''.join(_fato(r, v) for r, v in fatos)
    itens = ''.join(
        '<tr>'
        '<td valign="top" width="22" style="padding:3px 0;font-family:%(f)s;font-size:14px;'
        'line-height:20px;color:%(c)s;font-weight:700;">%(n)d.</td>'
        '<td valign="top" style="padding:3px 0;font-family:%(f)s;font-size:14px;'
        'line-height:20px;color:%(t)s;">%(p)s</td>'
        '</tr>' % dict(f=FONTE, c=cor, t=TXT, n=i + 1, p=p)
        for i, p in enumerate(passos))

    return (
'<table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" '
'style="background-color:%(fundo)s;margin:0;padding:0;"><tr>'
'<td align="center" style="padding:24px 12px;">'

'<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" '
'style="width:600px;max-width:600px;background-color:#FFFFFF;'
'border:1px solid %(linha)s;">'

# barra fina de severidade — o único uso "cheio" da cor
'<tr><td bgcolor="%(cor)s" style="background-color:%(cor)s;height:3px;'
'font-size:0;line-height:0;">&nbsp;</td></tr>'

# cabeçalho branco: wordmark + chip
'<tr><td style="padding:22px 28px 0 28px;">'
'<table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0"><tr>'
'<td style="font-family:%(f)s;font-size:15px;font-weight:700;letter-spacing:2px;'
'color:%(navy)s;">AIRPORT NOW</td>'
'<td align="right" style="font-family:%(f)s;">'
'<span style="display:inline-block;padding:4px 12px;border:1px solid %(cor)s;'
'color:%(cor)s;font-size:11px;font-weight:700;letter-spacing:1.2px;">%(titulo)s</span>'
'</td></tr></table>'
'<div style="font-family:%(f)s;font-size:12px;letter-spacing:1.2px;color:%(txt2)s;'
'padding-top:4px;">%(kicker)s</div>'
'</td></tr>'

# divisor sob o cabeçalho
'<tr><td style="padding:16px 28px 0 28px;"><div style="border-top:1px solid '
'%(linha)s;font-size:0;line-height:0;">&nbsp;</div></td></tr>'

# saudação + chamada
'<tr><td style="padding:18px 28px 4px 28px;font-family:%(f)s;font-size:16px;'
'line-height:24px;color:%(txt)s;">%(saudacao)s</td></tr>'
'<tr><td style="padding:6px 28px 18px 28px;font-family:%(f)s;font-size:15px;'
'line-height:23px;color:%(txt)s;">%(chamada)s</td></tr>'

# fatos
'<tr><td style="padding:0 28px;">'
'<table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" '
'style="border-top:1px solid %(linha)s;border-bottom:1px solid %(linha)s;">'
'<tr><td style="padding:10px 0;"><table role="presentation" cellpadding="0" '
'cellspacing="0" border="0">%(fatos)s</table></td></tr></table></td></tr>'

# ocorrência, destacada
'<tr><td style="padding:20px 28px 0 28px;">'
'<div style="font-family:%(f)s;font-size:11px;letter-spacing:1.2px;font-weight:700;'
'color:%(txt2)s;padding-bottom:7px;">%(oc_titulo)s</div>'
'<table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" '
'bgcolor="%(fundo)s" style="background-color:%(fundo)s;"><tr>'
'<td style="padding:13px 16px;border-left:3px solid %(cor)s;font-family:%(f)s;'
'font-size:15px;line-height:23px;color:%(txt)s;">%(ocorrencia)s</td>'
'</tr></table></td></tr>'

# o que fazer agora
'<tr><td style="padding:22px 28px 0 28px;">'
'<div style="font-family:%(f)s;font-size:11px;letter-spacing:1.2px;font-weight:700;'
'color:%(txt2)s;padding-bottom:8px;">O QUE FAZER AGORA</div>'
'<table role="presentation" cellpadding="0" cellspacing="0" border="0">%(passos)s'
'</table></td></tr>'

# rodapé
'<tr><td style="padding:24px 28px 0 28px;"><div style="border-top:1px solid '
'%(linha)s;font-size:0;line-height:0;">&nbsp;</div></td></tr>'
'<tr><td style="padding:14px 28px 24px 28px;font-family:%(f)s;font-size:12px;'
'line-height:18px;color:%(txt2)s;">%(rodape)s</td></tr>'

'</table></td></tr></table>'
    ) % dict(f=FONTE, txt=TXT, txt2=TXT2, fundo=FUNDO, linha=LINHA, cor=cor,
             navy=NAVY, kicker=kicker, titulo=titulo, saudacao=saudacao,
             chamada=chamada, fatos=linhas_fatos, oc_titulo=ocorrencia_titulo,
             ocorrencia=ocorrencia, passos=itens, rodape=rodape)


if __name__ == '__main__':
    for k in TIPOS:
        print('%-18s %s' % (k, rotulo(k)))
    print('\npaleta: navy %s · acao %s · real %s · simulado %s'
          % (NAVY, ACAO, COR_REAL, COR_SIMULADO))
