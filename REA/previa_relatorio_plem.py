# -*- coding: utf-8 -*-
"""Prévia estática do relatório PLEM (mesma marcação do HtmlText do HtmlViewer).
Serve só para conferir o visual no navegador antes de colar no Power Apps."""
from datetime import datetime, timedelta

AC = dict(ID=752, Acionamento="PLEM", Protocolo="CWB-ACI-PLEM-752", Bloco="SUL",
          IATA="CWB", Aeroporto="CURITIBA", Status="Em andamento",
          Ambiente="Ambiente Simulado", Emergencia="PANPAN - CONDIÇÃO DE URGÊNCIA",
          Usuario="Jose Clovis da Silva",
          Descricao="TWR informou ANV A321 - voo TAM5523 - Informou PANPAN por pane hidráulica.",
          Data=datetime(2026, 8, 25, 9, 0), Data_termino=None, Relatorio_final="",
          Matricula="prttf", Modelo="a321", POB=132, Comb=10000, RWY="33",
          TempoPouso=10, Pane="HIDRÁULICA", Carga=False, Municiada=False)

T0 = AC["Data"]
def m(mi, se=0): return T0 + timedelta(minutes=mi, seconds=se)

# ordem, acao, texto, ator, nivel, prazo, minuto, gatilho(min)
ATIV = [
 (1,"CRIAÇÃO","Acionamento PLEM - Ambiente Simulado CWB - CURITIBA devido a emergência: PANPAN - CONDIÇÃO DE URGÊNCIA","","",0,0,None),
 (2,"CHAT","Criação do chat com os participantes","","",0,0,None),
 (3,"ACIONAR","Serviço de Salvamento e Combate a Incêndio","SESCINC","ACIONAR",5,1,None),
 (4,"ACIONAR","Coordenação Operacional do Aeroporto","COA","ACIONAR",5,1,None),
 (5,"INFORMAR","Diretoria de Operações","DIROP","INFORMAR",0,2,None),
 (6,"NOTIFICADO","Wilson Rocha Gomes","SESCINC","ACIONAR",5,2,None),
 (7,"CHEGOU","SESCINC confirmou posicionamento no ponto de espera","SESCINC","ACIONAR",5,4,1),
 (8,"RESPONDEU AO FLOW","COA > foi acionado","COA","ACIONAR",5,7,1),
 (9,"ATIVIDADE MANUAL","Aeronave em aproximação final - RWY 33 liberada e interditada para demais operações","","",0,9,None),
 (10,"CHEGOU","COA assumiu a coordenação no CGE","COA","ACIONAR",5,12,1),
 (11,"CONTATO_NR","Ambulância municipal não atendeu ao contato telefônico","SAMU","INFORMAR",15,14,2),
]

COR = {"ACIONAR":"#B98900","ACIONAR_SOBREAVISO":"#B98900","RESPONDEU AO FLOW":"#B98900",
 "SOBREAVISO":"#C05621","INFORMAR":"#155E8F","NOTIFICADO":"#A9BCCB","CHEGOU":"#1F7A4D",
 "CONTATO_NR":"#A62639","NAO COMPARECERA":"#A62639","ERRO CHAT":"#A62639","SEM RESPOSTA":"#5D6B77",
 "CRIAÇÃO":"#0B2E4F","FINALIZAÇÃO":"#0B2E4F","CHAT":"#5D6B77","ATIVIDADE MANUAL":"#5D6B77"}

def dur(s):
    if s is None: return "—"
    if s < 60: return f"{s}s"
    if s < 3600: return f"{s//60}m {s%60}s"
    return f"{s//3600}h {(s%3600)//60}m"

FNT = "font-family:'Segoe UI',Arial,sans-serif;"
LBL = "font-size:9px;letter-spacing:.13em;font-weight:700;color:#5D6B77;"
VAL = "font-size:13px;font-weight:600;color:#22303B;margin-top:3px;"
TDC = "padding:9px 16px 9px 0;vertical-align:top;width:33%;"
SEC = "background:#FFFFFF;border:1px solid #E1E7EC;border-top:3px solid #155E8F;padding:14px 16px;margin-top:12px;"
HS  = "font-size:11px;font-weight:800;letter-spacing:.16em;color:#0B2E4F;border-bottom:1px solid #EDF1F4;padding-bottom:8px;margin-bottom:2px;"
KPI = "padding:12px 14px;border-right:1px solid #E1E7EC;vertical-align:top;"

resp = [a for a in ATIV if a[1] in ("CHEGOU","RESPONDEU AO FLOW") and a[7] is not None]
acion = [a for a in ATIV if a[1] in ("ACIONAR","ACIONAR_SOBREAVISO","SOBREAVISO","INFORMAR")]
segs = [(a[6]-a[7])*60 for a in resp]
tot = 14

h = [f"<div style=\"{FNT}color:#22303B;font-size:12px;line-height:1.45;background:#F5F7F9;padding:0 0 14px 0;\">"]
h.append(f"""<div style='background:#0B2E4F;padding:16px 18px;'>
<table cellspacing='0' cellpadding='0' style='width:100%;'><tr>
<td style='vertical-align:top;'>
<div style='font-size:9px;letter-spacing:.20em;font-weight:700;color:#7FA6C4;'>RELATÓRIO DE ACIONAMENTO &nbsp;&middot;&nbsp; {AC['Acionamento']}</div>
<div style='font-size:21px;font-weight:800;color:#FFFFFF;margin-top:4px;letter-spacing:.01em;'>{AC['Protocolo']}</div>
<div style='font-size:12px;color:#C7D8E5;margin-top:3px;'>{AC['Aeroporto']} &nbsp;&middot;&nbsp; {AC['IATA']} &nbsp;&middot;&nbsp; BLOCO {AC['Bloco']}</div></td>
<td style='vertical-align:top;text-align:right;white-space:nowrap;'>
<span style='display:inline-block;padding:3px 10px;background:#B98900;color:#FFFFFF;font-size:10px;font-weight:700;letter-spacing:.08em;border-radius:10px;'>{AC['Status'].upper()}</span>
&nbsp;<span style='display:inline-block;padding:3px 10px;background:#C05621;color:#FFFFFF;font-size:10px;font-weight:700;letter-spacing:.08em;border-radius:10px;'>{AC['Ambiente'].upper()}</span>
<div style='font-size:11px;color:#C7D8E5;margin-top:8px;'>registro {AC['ID']}</div></td></tr></table>
<div style='margin-top:12px;background:#12456F;border-left:3px solid #4FA3E3;padding:8px 12px;'>
<span style='font-size:9px;letter-spacing:.14em;color:#9FC4DE;font-weight:700;'>EMERGÊNCIA</span>
<div style='font-size:14px;font-weight:700;color:#FFFFFF;margin-top:2px;'>{AC['Emergencia']}</div></div></div>""")

kpis = [("DURAÇÃO", f"{tot} min", "em andamento", "#0B2E4F"),
        ("ATIVIDADES", str(len(ATIV)), "registros na linha do tempo", "#0B2E4F"),
        ("ACIONADOS", str(len(acion)), f"{len(acion)-len(resp)} sem retorno", "#0B2E4F"),
        ("TEMPO MÉDIO", dur(round(sum(segs)/len(segs))), "resposta dos acionados", "#1F7A4D"),
        ("MENOR / MAIOR", f"{dur(min(segs))} <span style='color:#C9D3DB;'>/</span> {dur(max(segs))}", "1ª e última resposta", "#0B2E4F")]
h.append("<table cellspacing='0' cellpadding='0' style='width:100%;border-collapse:collapse;background:#FFFFFF;border:1px solid #E1E7EC;border-top:0;'><tr>")
for i,(l,v,s,c) in enumerate(kpis):
    st = KPI if i < len(kpis)-1 else "padding:12px 14px;vertical-align:top;"
    h.append(f"<td style='{st}'><div style='{LBL}'>{l}</div><div style='font-size:16px;font-weight:800;color:{c};margin-top:3px;'>{v}</div><div style='font-size:10px;color:#8A98A4;'>{s}</div></td>")
h.append("</tr></table>")

def cell(l, v): return f"<td style='{TDC}'><div style='{LBL}'>{l}</div><div style='{VAL}'>{v}</div></td>"
h.append(f"""<div style='{SEC}'><div style='{HS}'>DADOS DO ACIONAMENTO</div>
<table cellspacing='0' cellpadding='0' style='width:100%;'>
<tr>{cell('ABERTURA', AC['Data'].strftime('%d/%m/%Y %H:%M'))}{cell('TÉRMINO', "<span style='color:#B98900;'>em andamento</span>")}{cell('RESPONSÁVEL PELO REGISTRO', AC['Usuario'])}</tr>
<tr>{cell('PROTOCOLO', AC['Protocolo'])}{cell('TIPO DE ACIONAMENTO', AC['Acionamento'])}{cell('AMBIENTE', AC['Ambiente'])}</tr></table>
<div style='margin-top:10px;background:#F7F9FB;border-left:3px solid #C9D8E4;padding:10px 12px;'>
<div style='{LBL}'>DESCRIÇÃO DA OCORRÊNCIA</div>
<div style='font-size:12.5px;color:#22303B;margin-top:4px;'>{AC['Descricao']}</div></div></div>""")

chip = lambda on: f"<span style='display:inline-block;padding:2px 9px;border-radius:9px;font-size:10px;font-weight:700;background:{'#A62639' if on else '#E8EDF2'};color:{'#FFFFFF' if on else '#22303B'};'>{'SIM' if on else 'NÃO'}</span>"
h.append(f"""<div style='{SEC}border-top-color:#C05621;'><div style='{HS}'>AERONAVE ENVOLVIDA</div>
<table cellspacing='0' cellpadding='0' style='width:100%;'>
<tr>{cell('MATRÍCULA', AC['Matricula'].upper())}{cell('MODELO', AC['Modelo'].upper())}{cell('PESSOAS A BORDO (POB)', AC['POB'])}</tr>
<tr>{cell('COMBUSTÍVEL / AUTONOMIA', AC['Comb'])}{cell('PISTA PARA POUSO', 'RWY ' + AC['RWY'])}{cell('TEMPO ESTIMADO DE POUSO', str(AC['TempoPouso']) + ' min')}</tr>
<tr>{cell('TIPO DE PANE', AC['Pane'])}<td style='{TDC}'><div style='{LBL}'>CARGA PERIGOSA</div><div style='margin-top:4px;'>{chip(AC['Carga'])}</div></td>
<td style='{TDC}'><div style='{LBL}'>ACFT MUNICIADA</div><div style='margin-top:4px;'>{chip(AC['Municiada'])}</div></td></tr></table></div>""")

h.append(f"<div style='{SEC}border-top-color:#1F7A4D;'><div style='{HS}'>TEMPO DE RESPOSTA POR ACIONADO</div>"
         "<table cellspacing='0' cellpadding='0' style='width:100%;border-collapse:collapse;margin-top:8px;'><tr style='background:#F2F6F9;'>")
for t,al in [("ACIONADO","left"),("ACIONADO ÀS","left"),("RESPOSTA ÀS","left"),("TEMPO","right"),("PRAZO","right")]:
    h.append(f"<th style='text-align:{al};padding:7px 10px;font-size:9px;letter-spacing:.12em;color:#5D6B77;border-bottom:1px solid #E1E7EC;'>{t}</th>")
h.append("</tr>")
for a in sorted(resp, key=lambda x: (x[6]-x[7])):
    s = (a[6]-a[7])*60; ok = a[5] == 0 or s <= a[5]*60
    h.append(f"""<tr><td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;font-size:12px;font-weight:600;color:#22303B;'>{a[3]} <span style='font-size:9px;color:#8A98A4;font-weight:600;'>{a[4]}</span></td>
<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;font-size:12px;color:#5D6B77;'>{m(a[7]).strftime('%H:%M')}</td>
<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;font-size:12px;color:#5D6B77;'>{m(a[6]).strftime('%H:%M')}</td>
<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;text-align:right;'><span style='display:inline-block;padding:2px 9px;border-radius:9px;font-size:11px;font-weight:700;background:{'#E3F2E9' if ok else '#FBE7EA'};color:{'#1F7A4D' if ok else '#A62639'};'>{dur(s)}</span></td>
<td style='padding:8px 10px;border-bottom:1px solid #EDF1F4;text-align:right;font-size:11px;color:#8A98A4;'>{'sem prazo' if a[5]==0 else str(a[5]) + ' min'}</td></tr>""")
h.append("</table></div>")

h.append(f"<div style='{SEC}border-top-color:#0B2E4F;'><div style='{HS}'>LINHA DO TEMPO DAS ATIVIDADES</div>"
         "<table cellspacing='0' cellpadding='0' style='width:100%;border-collapse:collapse;margin-top:10px;'>")
ant = 0
for a in ATIV:
    ordem, acao, texto, ator, nivel, prazo, minuto, gat = a
    c = COR.get(acao, "#5D6B77"); mm = m(minuto)
    sresp = (minuto-gat)*60 if gat is not None and acao in ("CHEGOU","RESPONDEU AO FLOW","CONTATO_NR","NAO COMPARECERA","SEM RESPOSTA") else None
    ok = prazo == 0 or (sresp is not None and sresp <= prazo*60)
    badges = f"<span style='display:inline-block;padding:1px 7px;background:#F2F6F9;color:#5D6B77;font-weight:700;'>T+ {dur(minuto*60)}</span>"
    if ordem > 1:
        badges += f" &nbsp;<span style='display:inline-block;padding:1px 7px;background:#F2F6F9;color:#8A98A4;'>intervalo {dur((minuto-ant)*60)}</span>"
    if sresp is not None:
        badges += (f" &nbsp;<span style='display:inline-block;padding:1px 7px;font-weight:700;background:{'#E3F2E9' if ok else '#FBE7EA'};"
                   f"color:{'#1F7A4D' if ok else '#A62639'};'>RESPOSTA EM {dur(sresp)}{'' if prazo==0 else f' (prazo {prazo} min)'}</span>")
    ant = minuto
    h.append(f"""<tr><td style='width:88px;padding:0 10px 0 0;text-align:right;vertical-align:top;'>
<div style='font-size:13px;font-weight:700;color:#22303B;'>{mm.strftime('%H:%M')}</div>
<div style='font-size:10px;color:#A2AFB9;'>{mm.strftime('%d/%m')}</div></td>
<td style='width:16px;padding:0;border-left:2px solid #E1E7EC;vertical-align:top;'>
<div style='width:11px;height:11px;background:{c};border:2px solid #FFFFFF;border-radius:50%;margin-left:-7px;margin-top:4px;'></div></td>
<td style='padding:0 0 12px 8px;vertical-align:top;'>
<div style='background:#FFFFFF;border:1px solid #E8EDF1;border-left:3px solid {c};padding:9px 12px;'>
<span style='display:inline-block;padding:1px 9px;border-radius:9px;background:{c};color:{'#22303B' if c=='#A9BCCB' else '#FFFFFF'};font-size:9.5px;font-weight:700;letter-spacing:.06em;'>{acao}</span>
{f" <span style='font-size:12px;font-weight:700;color:#0B2E4F;'>{ator}</span>" if ator else ""}
{f" <span style='font-size:9px;color:#8A98A4;font-weight:600;'>&middot; {nivel}</span>" if nivel else ""}
<div style='font-size:12.5px;color:#22303B;margin-top:5px;'>{texto}</div>
<div style='margin-top:7px;font-size:10px;color:#8A98A4;'>{badges}</div></div></td></tr>""")
h.append("</table></div>")
h.append(f"<div style='margin-top:12px;padding:10px 4px;border-top:1px solid #E1E7EC;font-size:10px;color:#8A98A4;'>"
         f"Relatório gerado em {datetime(2026,8,26,9,14).strftime('%d/%m/%Y %H:%M')} &nbsp;&middot;&nbsp; AIRPORTNOW / REA &nbsp;&middot;&nbsp; {AC['Protocolo']}</div></div>")

open("REA/previa/relatorio_plem.html","w",encoding="utf-8").write(
    "<!doctype html><meta charset='utf-8'><title>Prévia - Relatório PLEM</title>"
    "<body style='margin:0;background:#DDE3E8;padding:24px;'><div style='max-width:1000px;margin:0 auto;'>"
    + "".join(h) + "</div></body>")
print("REA/previa/relatorio_plem.html")
