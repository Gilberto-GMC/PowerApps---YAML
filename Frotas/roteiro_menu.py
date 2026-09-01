# -*- coding: utf-8 -*-
"""Gera o bloco 'ROTEIRO DO SISTEMA' do trilho, com os 23 módulos do mapa.
Fonte: Gestao_Frotas_Mapa_Modulos.xlsx + ARQUITETURA_FROTAS.md secao 6."""

ONDAS = [
    ("ONDA 1 &middot; FUNDAÇÃO", [
        ("2",  "BDV &mdash; Boletim Diário"),
        ("3",  "Vistoria e checklist"),
        ("4",  "Documentação e licenciamento"),
    ]),
    ("ONDA 2 &middot; CONFORMIDADE", [
        ("16", "Credenciamento RBAC 107"),
        ("17", "Habilitação na área de movimento"),
        ("18", "Sinalização no lado ar"),
    ]),
    ("ONDA 3 &middot; OPERAÇÃO E CUSTO", [
        ("5",  "Motoristas e condutores"),
        ("6",  "Multas e infrações"),
        ("7",  "Manutenção preventiva e corretiva"),
        ("8",  "Combustível e abastecimento"),
        ("12", "Reserva e agendamento"),
        ("14", "Fornecedores"),
    ]),
    ("ONDA 4 &middot; ATIVOS ESPECIAIS", [
        ("19", "PESO &mdash; segurança operacional"),
        ("20", "GSE &mdash; apoio ao solo"),
        ("21", "SESCINC / CCI"),
    ]),
    ("ONDA 5 &middot; RISCO E INTELIGÊNCIA", [
        ("10", "Sinistros e acidentes"),
        ("22", "ESO com veículos"),
        ("13", "Custos e TCO"),
    ]),
    ("ONDA 6 &middot; COMPLEMENTOS", [
        ("9",  "Rastreamento e telemetria"),
        ("11", "Controle de pneus"),
        ("15", "Baixa e alienação"),
        ("23", "Frota de terceiros"),
    ]),
]

def bloco(recuo):
    i = " " * recuo
    L = []
    def s(txt): L.append(i + txt.rstrip() + ' &')
    L.append(i + '="<div style=\'" & htmlFonte & "padding-top:16px;\'>" &')
    s('"<div style=\'font-size:9px;letter-spacing:.16em;font-weight:700;color:" & hxTextoBarra & ";\'>ROTEIRO DO SISTEMA</div>" ')
    s('"<div style=\'font-size:9px;color:" & hxTextoBarraFraco & ";padding-bottom:12px;\'>23 módulos &middot; 604 H/H &middot; 16 aeroportos</div>" ')
    # módulo em uso
    s('"<div style=\'border-left:2px solid " & hxAcao & ";padding:1px 0 1px 8px;\'>" ')
    s('"<div style=\'font-size:10px;font-weight:700;color:" & hxTextoBarra & ";line-height:1.5;\'>1 &middot; Cadastro de ativos</div>" ')
    s('"<div style=\'font-size:9px;color:" & hxTextoBarraFraco & ";line-height:1.5;\'>em uso &middot; falta a ficha do ativo</div>" ')
    s('"</div>" ')
    for titulo, itens in ONDAS:
        s(f'"<div style=\'font-size:9px;letter-spacing:.14em;font-weight:700;color:" & hxTextoBarraSuave & ";padding:14px 0 4px;\'>{titulo}</div>" ')
        for num, nome in itens:
            s('"<div style=\'font-size:10px;color:" & hxTextoBarraFraco & ";line-height:1.45;padding:2px 0;\'>'
              f'<span style=\'display:inline-block;width:20px;font-weight:700;\'>{num}</span>{nome}</div>" ')
    L.append(i + '"</div>"')
    return "\n".join(L)

if __name__ == "__main__":
    import re, os
    BASE='/workspaces/codespaces-blank/Frotas'
    ANTIGO_INI = 'HtmlText: |-'
    for arq, suf in (('scrFrotaPainel.pa.yaml','Pnl'), ('scrFrotaLista.pa.yaml','Lst'), ('scrFrotaForm.pa.yaml','Frm')):
        p=os.path.join(BASE,arq); s=open(p,encoding='utf-8').read()
        if f'- htmMenuProximos{suf}:' not in s:
            print(f'{arq}: sem trilho ainda (rode aplicar_menu.py)'); continue
        i=s.index(f'- htmMenuProximos{suf}:')
        j=s.index('HtmlText: |-', i)+len('HtmlText: |-\n')
        k=s.index('\n'+' '*(len(s[:j].split("\n")[-2])-len(s[:j].split("\n")[-2].lstrip()))+'PaddingBottom:', j)
        recuo=len(s[j:].split('\n')[0]) - len(s[j:].split('\n')[0].lstrip())
        s=s[:j]+bloco(recuo)+s[k:]
        open(p,'w',encoding='utf-8').write(s)
        print(f'{arq}: roteiro com 23 módulos')
