#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a página de conferência das mensagens do acionamento PLEM/PRAI.

O conteúdo NÃO é recriado aqui: é extraído dos fluxos gerados
(previa_mensagens.extrair) e tem só as expressões @{...} do Power Automate
trocadas por dados de exemplo. Se a mensagem mudar no gerador, muda aqui.

Saída: REA/previa/mensagens_acionamento.html
"""
import html
import json
import os

from previa_mensagens import extrair, resolver

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, 'previa')
OUT = os.path.join(OUT_DIR, 'mensagens_acionamento.html')


# ------------------------------------------------- render do Adaptive Card
# Aproximação da renderização do Teams para os elementos que o cartão usa.
CARD_ESTILO = {'attention': '#C4314B', 'warning': '#DE7A22', 'emphasis': '#3B3B3B'}
CARD_TAM = {'Small': '11px', 'Default': '13.5px', 'Medium': '16px', 'Large': '20px'}
CARD_ESP = {'None': '0', 'Small': '4px', 'Default': '8px', 'Medium': '16px'}


def render_card(bloco, dentro=False):
    t = bloco['type']
    if t == 'Container':
        cor = CARD_ESTILO.get(bloco.get('style'), None)
        filhos = ''.join(render_card(x, True) for x in bloco['items'])
        borda = 'border-left:3px solid %s;' % cor if cor else ''
        fundo = 'background:rgba(255,255,255,.045);' if cor else ''
        sangra = 'margin:-14px -14px 0 -14px;' if bloco.get('bleed') else ''
        return ('<div style="%s%s%spadding:12px 14px;margin-top:%s;">%s</div>'
                % (sangra, borda, fundo, CARD_ESP.get(bloco.get('spacing'), '8px'), filhos))
    if t == 'TextBlock':
        return ('<div style="font-size:%s;line-height:1.45;font-weight:%s;color:%s;'
                'margin-top:%s;">%s</div>'
                % (CARD_TAM.get(bloco.get('size'), CARD_TAM['Default']),
                   700 if bloco.get('weight') == 'Bolder' else 400,
                   '#9E9E9E' if bloco.get('isSubtle') else '#F5F5F5',
                   CARD_ESP.get(bloco.get('spacing'), '8px'),
                   html.escape(bloco['text'])))
    if t == 'FactSet':
        linhas = ''.join(
            '<tr><td style="padding:2px 14px 2px 0;color:#9E9E9E;font-size:13px;'
            'white-space:nowrap;vertical-align:top;">%s</td>'
            '<td style="padding:2px 0;color:#F5F5F5;font-size:13px;font-weight:600;">'
            '%s</td></tr>' % (html.escape(f['title']), html.escape(f['value']))
            for f in bloco['facts'])
        return ('<table style="border-collapse:collapse;margin-top:%s;">%s</table>'
                % (CARD_ESP.get(bloco.get('spacing'), '8px'), linhas))
    return ''


def bolha(conteudo, hora='12:47'):
    """Bolha de mensagem do bot no Teams (tema escuro, como o do usuário)."""
    return ('<div class="tm-row"><div class="tm-av">FT</div><div>'
            '<div class="tm-meta">Fluxos de trabalho <span>%s</span></div>'
            '<div class="tm-bubble">%s</div></div></div>' % (hora, conteudo))


# ------------------------------------------------------------------ página
CSS = """
:root{
  --ground:#EEF1F4; --surface:#FFFFFF; --surface-2:#F7F9FB; --mat:#DDE3E9;
  --ink:#0F151B; --ink-2:#586673; --ink-3:#8494A1; --rule:#D5DCE3;
  --accent:#1B5C87; --accent-soft:#E3EDF4;
  --alerta:#B00020; --exercicio:#8A6100; --ok:#1F7A4D;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0D1319; --surface:#151D25; --surface-2:#1A242D; --mat:#080C10;
    --ink:#E7EDF2; --ink-2:#94A3B0; --ink-3:#6B7B89; --rule:#25313B;
    --accent:#7BB2D6; --accent-soft:#162835;
    --alerta:#FF7A8A; --exercicio:#E0A93B; --ok:#5FC08C;
  }
}
:root[data-theme="dark"]{
  --ground:#0D1319; --surface:#151D25; --surface-2:#1A242D; --mat:#080C10;
  --ink:#E7EDF2; --ink-2:#94A3B0; --ink-3:#6B7B89; --rule:#25313B;
  --accent:#7BB2D6; --accent-soft:#162835;
  --alerta:#FF7A8A; --exercicio:#E0A93B; --ok:#5FC08C;
}

*{box-sizing:border-box;}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:'IBM Plex Sans',-apple-system,Segoe UI,Roboto,sans-serif;
  font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:900px; margin:0 auto; padding:0 24px 96px;}

/* ---------- cabeçalho ---------- */
.top{padding:64px 0 40px; border-bottom:1px solid var(--rule);}
.eyebrow{
  font-family:'Barlow Condensed',sans-serif; font-size:14px; font-weight:600;
  letter-spacing:.22em; text-transform:uppercase; color:var(--accent);
  display:flex; align-items:center; gap:12px;
}
.eyebrow::after{content:""; flex:1; height:1px; background:var(--rule);}
h1{
  font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:clamp(38px,7vw,62px);
  line-height:1.02; letter-spacing:-.01em; margin:16px 0 0; text-wrap:balance;
}
.lede{max-width:62ch; color:var(--ink-2); font-size:17px; margin:18px 0 0;}

/* ---------- blocos de texto ---------- */
h2{
  font-family:'Barlow Condensed',sans-serif; font-weight:700;
  font-size:30px; letter-spacing:.01em; margin:0; text-wrap:balance;
}
h3{font-size:15px; font-weight:600; margin:0 0 6px;}
p{margin:0 0 14px; max-width:66ch;}
p:last-child{margin-bottom:0;}
a{color:var(--accent);}
code{
  font-family:'IBM Plex Mono',ui-monospace,monospace; font-size:.87em;
  background:var(--surface-2); border:1px solid var(--rule);
  border-radius:4px; padding:1px 5px;
}
.sec{padding:52px 0 0; display:flex; flex-direction:column; gap:20px;}
.note{
  background:var(--surface); border:1px solid var(--rule); border-radius:10px;
  padding:20px 22px; display:flex; flex-direction:column; gap:10px;
}
.note strong{color:var(--ink);}

/* ---------- linha do tempo ---------- */
.step{
  display:grid; grid-template-columns:82px 1fr; gap:28px;
  padding:44px 0 0; align-items:start;
}
.clock{
  font-family:'IBM Plex Mono',monospace; font-variant-numeric:tabular-nums;
  font-size:15px; font-weight:600; color:var(--ink); padding-top:2px;
}
.clock small{
  display:block; font-family:'Barlow Condensed',sans-serif; font-size:12px;
  font-weight:600; letter-spacing:.14em; text-transform:uppercase;
  color:var(--ink-3); margin-top:3px;
}
.step-body{display:flex; flex-direction:column; gap:14px; min-width:0;}
.chan{
  display:inline-flex; align-items:center; gap:7px; align-self:flex-start;
  font-family:'Barlow Condensed',sans-serif; font-size:13px; font-weight:600;
  letter-spacing:.14em; text-transform:uppercase;
  color:var(--accent); background:var(--accent-soft);
  border-radius:3px; padding:3px 9px;
}

/* ---------- moldura de espécime ---------- */
.spec{
  background:var(--mat); border:1px solid var(--rule); border-radius:12px;
  padding:18px; overflow-x:auto;
}
.spec-cap{
  font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--ink-3);
  margin:10px 2px 0;
}

/* ---------- inbox ---------- */
.inbox{
  background:#FFFFFF; border-radius:8px; padding:14px 18px;
  border-bottom:1px solid #E3E5E8; font-family:'Segoe UI',sans-serif;
}
.inbox .de{font-size:12px; color:#5B5B5B;}
.inbox .as{font-size:15px; font-weight:600; color:#1B1B1B; margin-top:2px;}

/* ---------- teams (escuro, como o do usuário) ---------- */
.teams{background:#1F1F1F; border-radius:8px; padding:18px 16px;}
.tm-row{display:flex; gap:11px; align-items:flex-start; margin-top:14px;}
.tm-row:first-child{margin-top:0;}
.tm-av{
  width:28px; height:28px; border-radius:6px; flex:none; background:#5B5FC7;
  color:#fff; font-size:10px; font-weight:700; display:flex;
  align-items:center; justify-content:center; font-family:'Barlow Condensed',sans-serif;
  letter-spacing:.06em;
}
.tm-meta{font-size:11.5px; color:#9E9E9E; margin-bottom:5px; font-family:'Segoe UI',sans-serif;}
.tm-meta span{margin-left:7px;}
.tm-bubble{
  background:#2B2B2B; border-radius:6px; padding:10px 14px; color:#F0F0F0;
  font-family:'Segoe UI',sans-serif; font-size:14px; line-height:1.5;
  display:inline-block; max-width:520px;
}
.tm-bubble p{margin:0 0 4px; max-width:none;}
.tm-bubble p:last-child{margin:0;}
.tm-bubble b{color:#FFFFFF;}
.tm-bubble blockquote{
  margin:7px 0 0; padding:2px 0 2px 11px; border-left:3px solid #6264A7;
  color:#D2D2D2; font-style:italic;
}
.tm-card{
  background:#292929; border-radius:6px; padding:14px; max-width:460px;
  font-family:'Segoe UI',sans-serif; overflow:hidden;
}
.tm-opts{display:flex; gap:8px; margin-top:14px; flex-wrap:wrap;}
.tm-opt{
  border:1px solid #4A4A4A; border-radius:4px; padding:6px 14px;
  font-size:13px; color:#F0F0F0; font-family:'Segoe UI',sans-serif;
}
.tm-opt.pri{background:#5B5FC7; border-color:#5B5FC7; color:#fff; font-weight:600;}
.tm-pre{
  white-space:pre-wrap; color:#E4E4E4; font-family:'Segoe UI',sans-serif;
  font-size:13.5px; line-height:1.55; margin:0;
}

/* ---------- grade do repertório ---------- */
.grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(255px,1fr)); gap:12px;}

/* ---------- tabela ---------- */
.tbl{width:100%; border-collapse:collapse; font-size:14.5px;}
.tbl th{
  text-align:left; font-family:'Barlow Condensed',sans-serif; font-size:13px;
  letter-spacing:.14em; text-transform:uppercase; color:var(--ink-3);
  border-bottom:1px solid var(--rule); padding:0 14px 8px 0; font-weight:600;
}
.tbl td{border-bottom:1px solid var(--rule); padding:11px 14px 11px 0; vertical-align:top;}
.tbl tr:last-child td{border-bottom:none;}
.was{color:var(--ink-3); text-decoration:line-through;}

@media (max-width:640px){
  .step{grid-template-columns:1fr; gap:12px;}
  .clock{display:flex; align-items:baseline; gap:10px;}
  .clock small{margin:0;}
}
"""


def pagina():
    d = extrair()
    email_real = resolver(d['email'], simulado=False)
    email_simul = resolver(d['email'], simulado=True)
    assunto_real = resolver(d['assunto'], simulado=False)
    assunto_simul = resolver(d['assunto'], simulado=True)
    cartao = json.loads(resolver(json.dumps(d['cartao'], ensure_ascii=False)))
    topico = resolver(d['topico'])
    posts = {n: resolver(t) for n, t in d['posts']}

    card_html = ''.join(render_card(b) for b in cartao['body'])

    opcoes = ''.join('<div class="tm-opt%s">%s</div>'
                     % (' pri' if i == 0 else '', html.escape(o))
                     for i, o in enumerate(d['escolha_opcoes']))

    # repertório do renderizador genérico
    from padrao_mensagens_teams import TIPOS
    exemplos = {
        'ACIONADO': ('Corpo de Bombeiros — Juliana do Nascimento', ''),
        'CHEGOU': ('Corpo de Bombeiros — Juliana do Nascimento', ''),
        'SOBREAVISO': ('Órgão de Saúde — Cristiane dos Santos', ''),
        'INFORMADO': ('Supervisão de Pátio — Marcos Lima', ''),
        'CONTATO_NR': ('Polícia Federal — Plantão', 'Tentativa de contato sem êxito'),
        'EQUIPAMENTO': ('Ambulância UTI móvel', 'Retirada: Hangar 3 · Prazo: 8 min'),
        'VITIMA_NOVA': ('Passageiro 14A', 'Prioridade Vermelha · Ambulância: SAMU 02 · Hospital: HUUFMA'),
        'MANUAL': ('Gilberto Marques Claudino', 'Pista 06 interditada para remoção da aeronave.'),
        'ENCERRADO': ('SLZ — Marechal Cunha Machado — Aeronave em emergência',
                      'Encerrado por Gilberto Marques Claudino em 24/08/2026 16:52'),
    }
    cartoes_rep = ''
    for tipo, (ator, det) in exemplos.items():
        corpo = ('<p><b>%s</b> &nbsp;·&nbsp; 13:04</p><p>%s</p>'
                 % (TIPOS[tipo], html.escape(ator)))
        if det:
            corpo += '<p>%s</p>' % html.escape(det)
        cartoes_rep += ('<div class="teams" style="padding:12px;">'
                        '<div class="tm-bubble" style="max-width:none;display:block;">'
                        '%s</div></div>' % corpo)

    return """<title>Mensagens do Acionamento PLEM/PRAI</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600;700&display=swap">
<style>%(css)s</style>

<div class="wrap">

<header class="top">
  <div class="eyebrow">Airport&nbsp;Now &middot; conferência antes de importar</div>
  <h1>Mensagens do acionamento PLEM/PRAI</h1>
  <p class="lede">Tudo o que uma pessoa acionada recebe, na ordem em que recebe.
  Cada peça abaixo foi extraída dos fluxos já gerados e teve só os campos
  dinâmicos preenchidos com um cenário de exemplo &mdash; é exatamente o que o
  Power Automate vai enviar.</p>
</header>

<section class="sec">
  <h2>O que mudou na comunicação</h2>
  <div class="note">
  <table class="tbl">
    <tr><th>Antes</th><th>Agora</th></tr>
    <tr>
      <td class="was">Dois e-mails quase idênticos por pessoa, em poucos segundos</td>
      <td><strong>Um e-mail</strong>, personalizado com o nome e a entidade de quem recebe</td>
    </tr>
    <tr>
      <td class="was">Texto corrido, sem hierarquia, sem hora, sem protocolo</td>
      <td>Faixa de severidade, fatos da ocorrência e <strong>o que fazer agora</strong> em três passos</td>
    </tr>
    <tr>
      <td class="was">Exercício simulado com a mesma cara de emergência real</td>
      <td><strong>Âmbar e prefixo [SIMULADO]</strong> no assunto, no cartão e no título do chat</td>
    </tr>
    <tr>
      <td class="was">No chat: <code>Gerente &gt; Fulano &gt; Notificado via Flow</code></td>
      <td>Rótulo, hora e ator; a fala da pessoa sai em citação, separada do texto do sistema</td>
    </tr>
    <tr>
      <td class="was">Emoji como ícone em e-mail, cartão, chat e nos rótulos do app</td>
      <td><strong>Zero emoji.</strong> Nenhum dos meios aceita ícone de verdade &mdash; a identidade vem de tipografia, cor e chips</td>
    </tr>
    <tr>
      <td class="was">Faixa de cor chapada no topo do e-mail</td>
      <td>Cabeçalho <strong>branco</strong> com wordmark navy, chip de severidade e barra fina de 3&nbsp;px</td>
    </tr>
    <tr>
      <td class="was">Uma única opção de resposta: &ldquo;Ciente&rdquo;</td>
      <td>Duas: <strong>a caminho</strong> ou <strong>não poderei comparecer</strong> &mdash; e a recusa some da lista de pendências</td>
    </tr>
  </table>
  </div>
</section>

<section class="sec">
  <h2>A sequência</h2>
  <p>Cenário: aeronave em emergência em São Luís, sete participantes,
  protocolo #1287.</p>
</section>

<div class="step">
  <div class="clock">12:47<small>abertura</small></div>
  <div class="step-body">
    <div class="chan">Teams &middot; chat do grupo</div>
    <h3>O chat é criado e recebe o cartão de abertura</h3>
    <p>O título do chat leva a severidade na frente, porque é o que aparece na
    lista de conversas do Teams antes de qualquer um abrir.</p>
    <div class="spec">
      <div class="teams">
        <div class="tm-row"><div class="tm-av">FT</div><div style="min-width:0;">
          <div class="tm-meta">Fluxos de trabalho <span>12:47</span></div>
          <div class="tm-card">%(card)s</div>
        </div></div>
      </div>
    </div>
    <div class="spec-cap">título do chat &nbsp;›&nbsp; %(topico)s</div>
  </div>
</div>

<div class="step">
  <div class="clock">12:47<small>notificação</small></div>
  <div class="step-body">
    <div class="chan">E-mail &middot; individual</div>
    <h3>Cada pessoa recebe um e-mail com o seu papel no acionamento</h3>
    <p>Quem abre no celular no meio de uma emergência lê as três primeiras
    linhas e nada mais &mdash; então elas precisam bastar: severidade, quem
    está sendo chamado e para quê.</p>
    <div class="spec">
      <div class="inbox">
        <div class="de">PROCESSOS AEROPORTUÁRIOS SERVICE &nbsp;·&nbsp; para Juliana do Nascimento</div>
        <div class="as">%(assunto_real)s</div>
      </div>
      %(email_real)s
    </div>
  </div>
</div>

<div class="step">
  <div class="clock">12:47<small>variante</small></div>
  <div class="step-body">
    <div class="chan">E-mail &middot; exercício simulado</div>
    <h3>O mesmo e-mail quando o ambiente é simulado</h3>
    <p>Um exercício nunca pode ser lido como emergência real. Muda a cor da
    faixa, o título, o ícone e o assunto ganha <code>[SIMULADO]</code>.</p>
    <div class="spec">
      <div class="inbox">
        <div class="de">PROCESSOS AEROPORTUÁRIOS SERVICE &nbsp;·&nbsp; para Juliana do Nascimento</div>
        <div class="as">%(assunto_simul)s</div>
      </div>
      %(email_simul)s
    </div>
  </div>
</div>

<div class="step">
  <div class="clock">12:47<small>pedido</small></div>
  <div class="step-body">
    <div class="chan">Teams &middot; conversa privada</div>
    <h3>E o bot pede a resposta, com duas saídas possíveis</h3>
    <div class="spec">
      <div class="teams">
        <div class="tm-row"><div class="tm-av">FT</div><div style="min-width:0;">
          <div class="tm-meta">Fluxos de trabalho <span>12:47</span></div>
          <div class="tm-card">
            <div style="font-size:16px;font-weight:700;color:#F5F5F5;margin-bottom:10px;">%(esc_titulo)s</div>
            <pre class="tm-pre">%(esc_corpo)s</pre>
            <div class="tm-opts">%(opcoes)s</div>
          </div>
        </div></div>
      </div>
    </div>
  </div>
</div>

<div class="step">
  <div class="clock">12:47<small>registro</small></div>
  <div class="step-body">
    <div class="chan">Teams &middot; chat do grupo</div>
    <h3>Cada notificação enviada vira uma linha no chat</h3>
    <p>Uma linha por pessoa &mdash; não sete linhas iguais para a mesma pessoa,
    que era o sintoma do bug de deduplicação.</p>
    <div class="spec"><div class="teams">%(notificado)s</div></div>
  </div>
</div>

<div class="step">
  <div class="clock">12:50<small>resposta</small></div>
  <div class="step-body">
    <div class="chan">Teams &middot; chat do grupo</div>
    <h3>A resposta da pessoa volta para o chat, com a fala dela em citação</h3>
    <p>O comentário sai em bloco de citação para não se confundir com texto do
    sistema. Quem recusa é removido da lista de pendências da tela.</p>
    <div class="spec"><div class="teams">%(ciente)s%(recusa)s</div></div>
  </div>
</div>

<div class="step">
  <div class="clock">12:57<small>operação</small></div>
  <div class="step-body">
    <div class="chan">Teams &middot; chat do grupo</div>
    <h3>O repertório completo do que o COE lança durante a ocorrência</h3>
    <p>Todas essas linhas saem do mesmo renderizador, com o mesmo formato:
    ícone, rótulo, hora, ator e detalhe. Mudar o visual de todas é editar um
    arquivo, não nove fórmulas espalhadas pela tela.</p>
    <div class="grid">%(repertorio)s</div>
  </div>
</div>

<div class="step">
  <div class="clock">16:47<small>4 horas</small></div>
  <div class="step-body">
    <div class="chan">Teams &middot; chat do grupo</div>
    <h3>Quem não respondeu aparece &mdash; e quem não tem e-mail também</h3>
    <p>Silêncio não pode passar despercebido em emergência. As duas linhas
    dizem o que fazer em seguida.</p>
    <div class="spec"><div class="teams">%(semresp)s%(sememail)s</div></div>
  </div>
</div>

<section class="sec">
  <h2>Como conferir</h2>
  <div class="note">
    <p>Esta página é gerada por <code>previa_artefato.py</code> a partir dos
    fluxos em <code>MigracaoAIRPORTNOW_src/Workflows</code>. O HTML do e-mail e
    o JSON do cartão são os mesmos que serão importados &mdash; só os campos
    dinâmicos foram preenchidos.</p>
    <p>O cartão do Teams e as bolhas de conversa são uma aproximação da
    renderização do cliente do Teams, feita para conferir hierarquia e texto.
    Espaçamentos e cantos podem sair ligeiramente diferentes no Teams real.</p>
    <p>O e-mail é tabela aninhada com estilo inline, porque o Outlook desktop
    renderiza com o motor do Word &mdash; sem flexbox, grid ou folha de estilo
    externa. Largura travada em 600&nbsp;px.</p>
  </div>
</section>

</div>
""" % dict(
        css=CSS, card=card_html, topico=html.escape(topico),
        assunto_real=html.escape(assunto_real), assunto_simul=html.escape(assunto_simul),
        email_real=email_real, email_simul=email_simul,
        esc_titulo=html.escape(resolver(d['escolha_titulo'])),
        esc_corpo=html.escape(resolver(d['escolha_corpo'])),
        opcoes=opcoes,
        notificado=bolha(posts['Chat_notificado_via_Flow'], '12:47'),
        ciente=bolha(posts['Post_ciente'], '12:50'),
        recusa=bolha(posts['Post_recusa'], '12:52'),
        semresp=bolha(posts['Post_message_SemResposta'], '16:47'),
        sememail=bolha(posts['Post_contato_sem_email'], '12:47'),
        repertorio=cartoes_rep,
    )


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(pagina())
    print('%s (%d KB)' % (os.path.relpath(OUT, HERE), os.path.getsize(OUT) // 1024))
