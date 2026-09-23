# -*- coding: utf-8 -*-
"""Gera out/ScreenAPH.pa.yaml a partir do export do Studio (msapp/Src/ScreenAPH.pa.yaml).

Cirurgia por propriedade: só as propriedades listadas em OPERACOES mudam, o resto
do arquivo sai byte a byte igual ao export. O próprio gerador prova isso relendo
os dois arquivos como YAML (ver conferir()).

Rodar a partir de REA/:
    python build/gerar_aph.py
    sh build/verificar_aph.sh

Decisões de negócio (respostas do usuário em 2026-09-18, ver AUDITORIA_APH.md §5):
  1. em voo, tudo depois da notificação; equipe e ambulância podem ser acionadas
     antes ou depois da abertura de porta; o início do atendimento vem depois do
     acionamento da equipe e da abertura de porta; fora de voo, a ambulância vem
     depois do início do atendimento;
  2. o formulário é preenchido depois do atendimento, a partir da ficha;
  3. empresa/CNPJ só para CESSIONARIO COMERCIAL;
  4. R$ 150 só para posto médico de CURITIBA (aeroporto do registro);
  5. limites dos alertas decididos aqui (LIMITES).
"""
import json
import os
import re
import sys

import yaml

SRC = 'msapp/Src/ScreenAPH.pa.yaml'
OUT = 'out/ScreenAPH.pa.yaml'
EXC = 'out/_excecoes_layout.json'
TELA = 'ScreenAPH'

sys.path.insert(0, os.path.join('..', 'Inspeções', 'build'))
from trava_layout import VISUAIS  # noqa: E402  (mesmo conjunto que a trava usa)

CABECALHO_EXTRA = (
    "# Gerado por REA/build/gerar_aph.py a partir do export de 2026-09-18. Não editar à mão.\n"
    "# Formato invariante (vírgula entre argumentos, ponto e vírgula entre comandos, ponto decimal).\n"
    "# Colar como está pela exibição de código, sem converter para pt-BR.\n"
)

# limites dos alertas de plausibilidade (minutos). Alerta pede confirmação, não bloqueia.
LIMITES = {
    '_limPortaMin': 180,      # notificação em voo -> abertura de porta
    '_limEquipeMin': 30,      # acionamento (em voo: o mais tarde entre ele e a porta) -> início
    '_limAmbulanciaMin': 60,  # acionamento da ambulância -> chegada no local
    '_minIdaVoltaMin': 10,    # saída da ambulância -> retorno (ida e volta ao hospital)
    '_limTotalMin': 720,      # acionamento da equipe -> encerramento (12 h)
}

AZUL = 'RGBA(40, 134, 222, 1)'      # borda dos demais campos do formulário
VERMELHO = 'RGBA(255, 0, 0, 1)'     # borda que já existia, agora só com problema
TEXTO_ERRO = 'RGBA(184, 0, 0, 1)'   # vermelho escuro já usado na galeria (Label4_3)

# ----------------------------------------------------------------------------
# Os 9 horários do formulário
# ----------------------------------------------------------------------------
CARDS = {
    'voo': dict(card='HORÁRIO DE ACIONAMENTO EM VOO_DataCard1_1', col='HORÁRIO DE ACIONAMENTO EM VOO',
                d='DateValue16_1', h='HourValue16_1', m='MinuteValue16_1', err='ErrorMessage144_1',
                nome='notificação em voo'),
    'acion': dict(card='HORÁRIO DO ACIONAMENTO_DataCard1_1', col='HORÁRIO DO ACIONAMENTO',
                  d='DateValue12_1', h='HourValue12_1', m='MinuteValue12_1', err='ErrorMessage68_1',
                  nome='acionamento da equipe'),
    'porta': dict(card='HORÁRIO DE CALÇO_DataCard1_1', col='HORÁRIO DE CALÇO',
                  d='DateValue15_1', h='HourValue15_1', m='MinuteValue15_1', err='ErrorMessage108_2',
                  nome='abertura de porta'),
    'inicio': dict(card='HÓRARIO DO ATENDIMENTO_DataCard1_2', col='HORÁRIO DO ATENDIMENTO',
                   d='DateValue1_2', h='HourValue1_2', m='MinuteValue1_2', err='ErrorMessage8_2',
                   nome='início do atendimento'),
    'ambAcion': dict(card='HORÁRIO DE ACIONAMENTO DA AMBULÂNCIA_DataCard1_1', col='HORÁRIO DE ACIONAMENTO DA AMBULÂNCIA',
                     d='DateValue14_1', h='HourValue14_1', m='MinuteValue14_1', err='ErrorMessage71_1',
                     nome='acionamento da ambulância'),
    'ambCheg': dict(card='HORÁRIO DA CHEGADA DA AMBULÂNCIA_DataCard1_2', col='HORÁRIO DA CHEGADA DA AMBULÂNCIA',
                    d='DateValue2_10', h='HourValue2_10', m='MinuteValue2_10', err='ErrorMessage9_2',
                    nome='chegada da ambulância'),
    'ambSaida': dict(card='HORÁRIO DA SAÍDA DA AMBULÂNCIA_DataCard1_2', col='HORÁRIO DA SAÍDA DA AMBULÂNCIA',
                     d='DateValue3_6', h='HourValue3_6', m='MinuteValue3_6', err='ErrorMessage10_2',
                     nome='saída da ambulância'),
    'ambRet': dict(card='HORÁRIO DO RETORNO DA AMBULÂNCIA_DataCard1', col='HORÁRIO DO RETORNO DA AMBULÂNCIA',
                   d='DateValue17', h='HourValue17', m='MinuteValue17', err='ErrorMessage17',
                   nome='retorno da ambulância'),
    'enc': dict(card='HORÁRIO DO ENCERRAMENTO DO ATENDIMENTO_DataCard1_2', col='HORÁRIO DO ENCERRAMENTO DO ATENDIMENTO',
                d='DateValue4_2', h='HourValue4_2', m='MinuteValue4_2', err='ErrorMessage11_3',
                nome='encerramento'),
}
ORDEM = ['voo', 'acion', 'porta', 'inicio', 'ambAcion', 'ambCheg', 'ambSaida', 'ambRet', 'enc']

# Marcos que cada horário tem de seguir. Cada grupo é uma regra independente;
# dentro do grupo vale o primeiro marco preenchido (Coalesce). Marco de card
# oculto é branco, então o grupo ['voo', 'inicio'] vira "notificação em voo"
# quando é voo e "início do atendimento" quando não é.
GRUPOS = {
    'voo': [],
    'acion': [['voo']],
    # em voo a equipe e a ambulância podem ser acionadas antes OU depois da
    # abertura de porta (usuário, 2026-09-18): a porta só segue a notificação
    'porta': [['voo']],
    # a equipe só atende depois de acionada e, em voo, depois de a porta abrir
    'inicio': [['porta'], ['acion']],
    # ambulância: em voo, depois da notificação; fora de voo, depois do início
    'ambAcion': [['voo', 'inicio']],
    'ambCheg': [['ambAcion']],
    # sai com o paciente: depois da chegada da ambulância e depois do início do
    # atendimento (em voo a ambulância pode chegar antes de a porta abrir)
    'ambSaida': [['ambCheg'], ['inicio']],
    'ambRet': [['ambSaida']],
    'enc': [['ambSaida', 'inicio']],
}

REMOCAO = 'DataCardValueHouveRemocao_1.Checked'
VOO_VISIVEL = "'HORÁRIO DE ACIONAMENTO EM VOO_DataCard1_1'.Visible"
PORTA_VISIVEL = "'HORÁRIO DE CALÇO_DataCard1_1'.Visible"

# data que cada marco herda quando o registro ainda não tem valor gravado
DATA_PADRAO = {
    'voo': None,  # mantém Parent.Default (hoje, quando "em voo" está marcado)
    'acion': f"Coalesce(ThisItem.'HORÁRIO DO ACIONAMENTO', If({VOO_VISIVEL}, DateValue16_1.SelectedDate), Today())",
    'porta': "Coalesce(Parent.Default, DateValue16_1.SelectedDate)",
    'inicio': f"Coalesce(Parent.Default, If({PORTA_VISIVEL}, DateValue15_1.SelectedDate, DateValue12_1.SelectedDate))",
    # em voo a ambulância costuma ser acionada junto com a equipe
    'ambAcion': f"If({REMOCAO}, Coalesce(Parent.Default, If({VOO_VISIVEL}, DateValue12_1.SelectedDate, DateValue1_2.SelectedDate)))",
    'ambCheg': f"If({REMOCAO}, Coalesce(Parent.Default, DateValue14_1.SelectedDate))",
    'ambSaida': f"If({REMOCAO}, Coalesce(Parent.Default, DateValue2_10.SelectedDate))",
    'ambRet': f"If({REMOCAO}, Coalesce(Parent.Default, DateValue3_6.SelectedDate))",
    'enc': f"Coalesce(Parent.Default, If({REMOCAO}, DateValue3_6.SelectedDate, DateValue1_2.SelectedDate))",
}


def ref(k):
    return f"'{CARDS[k]['card']}'"


def T(k, vis):
    """data/hora do marco k, ou branco se o card está oculto ou incompleto (uma linha)"""
    c = CARDS[k]
    d, h, m = c['d'], c['h'], c['m']
    return (f"If({vis} And !IsBlank({d}.SelectedDate) And !IsBlank({h}.Selected.Value) And !IsBlank({m}.Selected.Value), "
            f"DateTime(Year({d}.SelectedDate), Month({d}.SelectedDate), Day({d}.SelectedDate), "
            f"Value({h}.Selected.Value), Value({m}.Selected.Value), 0))")


def T_update(k):
    c = CARDS[k]
    d, h, m = c['d'], c['h'], c['m']
    return f"""If(
    Self.Visible And
    !IsBlank({d}.SelectedDate) And
    !IsBlank({h}.Selected.Value) And
    !IsBlank({m}.Selected.Value),
    DateTime(
        Year({d}.SelectedDate),
        Month({d}.SelectedDate),
        Day({d}.SelectedDate),
        Value({h}.Selected.Value),
        Value({m}.Selected.Value),
        0
    )
)"""


def lista(n):
    itens = ['""'] + [f'"{i:02d}"' for i in range(n)]
    return '[\n' + ',\n'.join('    ' + x for x in itens) + '\n]'


def default_itens(k, funcao):
    col = CARDS[k]['col']
    return f"""If(
    newMode Or IsBlank(ThisItem.'{col}'),
    Blank(),
    [
        Text(
            {funcao}(ThisItem.'{col}'),
            "00"
        )
    ]
)"""


def var_marco(k):
    return '_p' + k[0].upper() + k[1:]


def referencia(grupo, nomear):
    """(expressão do marco de referência, expressão do nome) de um grupo de GRUPOS"""
    if len(grupo) == 1:
        return nomear(grupo[0]), f'"{CARDS[grupo[0]]["nome"]}"'
    valor = 'Coalesce(' + ', '.join(nomear(p) for p in grupo) + ')'
    ramos = ', '.join(f'!IsBlank({nomear(p)}), "{CARDS[p]["nome"]}"' for p in grupo[:-1])
    return valor, f'If({ramos}, "{CARDS[grupo[-1]]["nome"]}")'


def mensagem(k):
    """texto do ErrorMessage do card: erro do formulário, campo faltando, futuro ou fora de ordem"""
    grupos = GRUPOS[k]
    ramos = [
        '!IsBlank(Parent.Error)',
        'Parent.Error',
        'var_tentouSalvar And Parent.Required And IsBlank(_atual)',
        '"Informe data, hora e minuto."',
        '!IsBlank(_atual) And _atual > Now()',
        '"Horário no futuro. Confira a data e a hora."',
    ]
    if not grupos:
        corpo = ',\n        '.join(ramos + ['""'])
        return f"""With(
    {{
        _atual: {T(k, 'Parent.Visible')}
    }},
    If(
        {corpo}
    )
)"""
    marcos = []
    for g in grupos:
        marcos += [p for p in g if p not in marcos]
    campos = [f"_atual: {T(k, 'Parent.Visible')}"] + [f"{var_marco(p)}: {T(p, ref(p) + '.Visible')}" for p in marcos]
    antes = []
    for i, g in enumerate(grupos, 1):
        valor, nome = referencia(g, var_marco)
        antes += [f'_ant{i}: {valor}', f'_nome{i}: {nome}']
        ramos += [
            f'!IsBlank(_atual) And !IsBlank(_ant{i}) And _atual < _ant{i}',
            f'"Está antes do horário de " & _nome{i} & " (" & Text(_ant{i}, "dd/mm hh:mm") & ")." & '
            f'If(DateDiff(_atual, _ant{i}, TimeUnit.Hours) >= 12, " Se passou da meia-noite, mude a data deste campo.", "")',
        ]
    campos_txt = ',\n        '.join(campos)
    antes_txt = ',\n            '.join(antes)
    corpo = ',\n            '.join(ramos + ['""'])
    return f"""With(
    {{
        {campos_txt}
    }},
    With(
        {{
            {antes_txt}
        }},
        If(
            {corpo}
        )
    )
)"""


def borda(k):
    return f"If({CARDS[k]['err']}.Visible, {VERMELHO}, {AZUL})"


# ----------------------------------------------------------------------------
# Botão Salvar
# ----------------------------------------------------------------------------
def salvar():
    tv = {k: '_t' + k[0].upper() + k[1:] for k in ORDEM}
    tempos = ',\n            '.join(f"{tv[k]}: {T(k, ref(k) + '.Visible')}" for k in ORDEM)
    faltando = ',\n                            '.join(
        f'{{n: "{CARDS[k]["nome"]}", f: {ref(k)}.Required And IsBlank({tv[k]})}}' for k in ORDEM)
    futuro = ',\n                            '.join(f'{{n: "{CARDS[k]["nome"]}", a: {tv[k]}}}' for k in ORDEM)
    fora = []
    for k in ORDEM:
        if not GRUPOS[k]:
            continue
        regras = []
        for g in GRUPOS[k]:
            b, _ = referencia(g, lambda p: tv[p])
            regras.append(f'(!IsBlank({tv[k]}) And !IsBlank({b}) And {tv[k]} < {b})')
        # sem ") And (" / ") Or (": o checar_sintaxe lê isso como vírgula faltando
        fora.append(f'{{n: "{CARDS[k]["nome"]}", f: {" || ".join(regras)}}}')
    fora_txt = ',\n                            '.join(fora)
    limites = ',\n        '.join(f'{k}: {v}' for k, v in LIMITES.items())
    return f"""If(
    !IsBlank(var_salvandoDesde) And DateDiff(var_salvandoDesde, Now(), TimeUnit.Seconds) < 30,
    Notify("Aguarde: o atendimento ainda está sendo salvo.", NotificationType.Warning, 3000),
    UpdateContext({{var_tentouSalvar: true, var_visibleAlerta: false}});
    // limites dos alertas de horário (minutos): o alerta pede confirmação, não bloqueia
    With(
    {{
        {limites}
    }},
    With(
        {{
            {tempos}
        }},
        // base do tempo de resposta da equipe: o que aconteceu por último entre o
        // acionamento e, em voo, a abertura de porta (pode vir antes ou depois)
        With(
        {{
            _tBaseEquipe: If(!IsBlank(_tPorta) And _tPorta > _tAcion, _tPorta, _tAcion)
        }},
        With(
            {{
                _faltando: Concat(
                    Filter(
                        Table(
                            {faltando}
                        ),
                        f
                    ),
                    n,
                    ", "
                ),
                _futuro: Concat(
                    Filter(
                        Table(
                            {futuro}
                        ),
                        !IsBlank(a) And a > Now()
                    ),
                    n,
                    ", "
                ),
                _foraDeOrdem: Concat(
                    Filter(
                        Table(
                            {fora_txt}
                        ),
                        f
                    ),
                    n,
                    ", "
                ),
                _alertas: Filter(
                    Table(
                        {{m: If(!IsBlank(_tVoo) And !IsBlank(_tPorta) And DateDiff(_tVoo, _tPorta, TimeUnit.Minutes) > _limPortaMin, "Abertura de porta " & DateDiff(_tVoo, _tPorta, TimeUnit.Minutes) & " min depois da notificação em voo (alerta acima de " & _limPortaMin & " min).")}},
                        {{m: If(!IsBlank(_tInicio) And !IsBlank(_tBaseEquipe) And DateDiff(_tBaseEquipe, _tInicio, TimeUnit.Minutes) > _limEquipeMin, "Início do atendimento " & DateDiff(_tBaseEquipe, _tInicio, TimeUnit.Minutes) & " min depois " & If(_tBaseEquipe = _tPorta, "da abertura de porta", "do acionamento da equipe") & " (alerta acima de " & _limEquipeMin & " min).")}},
                        {{m: If(!IsBlank(_tAmbAcion) And !IsBlank(_tAmbCheg) And DateDiff(_tAmbAcion, _tAmbCheg, TimeUnit.Minutes) > _limAmbulanciaMin, "Chegada da ambulância " & DateDiff(_tAmbAcion, _tAmbCheg, TimeUnit.Minutes) & " min depois do acionamento da ambulância (alerta acima de " & _limAmbulanciaMin & " min).")}},
                        {{m: If(!IsBlank(_tAmbSaida) And !IsBlank(_tAmbRet) And DateDiff(_tAmbSaida, _tAmbRet, TimeUnit.Minutes) < _minIdaVoltaMin, "Retorno da ambulância " & DateDiff(_tAmbSaida, _tAmbRet, TimeUnit.Minutes) & " min depois da saída (ida e volta com menos de " & _minIdaVoltaMin & " min).")}},
                        {{m: If(!IsBlank(_tAcion) And !IsBlank(_tEnc) And DateDiff(_tAcion, _tEnc, TimeUnit.Minutes) > _limTotalMin, "Encerramento " & RoundDown(DateDiff(_tAcion, _tEnc, TimeUnit.Minutes) / 60, 0) & " h depois do acionamento da equipe (alerta acima de " & RoundDown(_limTotalMin / 60, 0) & " h).")}}
                    ),
                    !IsBlank(m)
                )
            }},
            If(
                newMode And IsBlank(DataCardValue4_3.Value),
                Notify("Selecione o aeroporto no filtro à esquerda antes de registrar o atendimento.", NotificationType.Error, 8000),
                !IsBlank(_faltando),
                Notify("Preencha data, hora e minuto de: " & _faltando & ".", NotificationType.Error, 8000),
                !IsBlank(_futuro),
                Notify("Horário no futuro em: " & _futuro & ". Confira a data e a hora.", NotificationType.Error, 8000),
                !IsBlank(_foraDeOrdem),
                Notify("Horário fora de ordem em: " & _foraDeOrdem & ". A mensagem abaixo de cada campo explica o problema.", NotificationType.Error, 8000),
                !IsEmpty(_alertas),
                UpdateContext({{var_alertasAPH: _alertas, var_visibleAlerta: true}}),
                UpdateContext({{var_salvandoDesde: Now()}});
                SubmitForm(FormAphEdt)
            )
        )
        )
    )
    )
)"""


ALERTA_HTML = '\n'.join([
    '"<div style=\'font-family:Arial, sans-serif;padding:18px;border-radius:12px;background-color:#fff;color:#212529;border:1px solid #e9ecef;\'>" &',
    '"<div style=\'background:#fff3cd;color:#664d03;padding:12px 14px;border-radius:10px;margin-bottom:12px;\'>" &',
    '"<strong>Confira os horários antes de salvar</strong>" &',
    '"</div>" &',
    '"<ul style=\'margin:0;padding-left:18px;line-height:1.6;\'>" &',
    'Concat(var_alertasAPH, "<li>" & m & "</li>") &',
    '"</ul>" &',
    '"<p style=\'margin-top:12px;\'>Se os horários estão certos, clique em <strong>Salvar assim</strong>. Para corrigir, clique em <strong>Ajustar</strong>.</p>" &',
    '"</div>"',
])

ONSUCCESS = """UpdateContext({var_salvandoDesde: Blank(), var_tentouSalvar: false});
With(
    {
        _rec: Self.LastSubmit,
        _va: If(Self.LastSubmit.ISENTO, 0, Coalesce(Value(ValueAtendimento_1.Text), 0)),
        _vr: If(Self.LastSubmit.ISENTO, 0, Coalesce(Value(ValueRemocao_1.Text), 0))
    },
    // protocolo (novo) e valores (novo ou editado) numa segunda gravação, só se mudaram
    If(
        IsBlank(_rec.PROTOCOLO) Or Coalesce(_rec.VALOR_ATENDIMENTO, -1) <> _va Or Coalesce(_rec.VALOR_REMOÇÃO, -1) <> _vr,
        If(
            IsError(
                Patch(
                    tbl_atendimentoPreHospitalar,
                    _rec,
                    {
                        PROTOCOLO: Coalesce(_rec.PROTOCOLO, Coalesce(_rec.IATA, varIATAUser) & "-OCO-APH-" & _rec.ID),
                        VALOR_ATENDIMENTO: _va,
                        VALOR_REMOÇÃO: _vr
                    }
                )
            ),
            Notify(
                "O atendimento foi salvo, mas o protocolo e os valores não foram gravados. Abra o registro e salve de novo.",
                NotificationType.Warning,
                8000
            )
        )
    );
    If(
        newMode,
        Select(CancelButton1_1),
        ViewForm(FormAphEdt);
        UpdateContext(
            {
                var_dadosAPH: LookUp(tbl_atendimentoPreHospitalar, ID = _rec.ID),
                editMode: false,
                viewMode: true
            }
        )
    )
);
Notify(
    "Atendimento salvo.",
    NotificationType.Success,
    3000
);
Select(BtnUpdateAPH)"""

ONFAILURE = """UpdateContext({var_salvandoDesde: Blank()});
Notify(
    "Não foi possível salvar. " & Coalesce(Self.Error, "Verifique os campos obrigatórios marcados em vermelho."),
    NotificationType.Error,
    8000
)"""

ONVISIBLE = """UpdateContext(
    {
        newMode: false,
        editMode: false,
        viewMode: false,
        isItemSelected: false,
        deleteMode: false,
        var_visibleIsentar: false,
        var_visibleAlerta: false,
        var_tentouSalvar: false,
        var_salvandoDesde: Blank()
    }
);
ClearCollect(
    colEmpresasAtivas,
    Filter(
        Cessionarios,
        AeroportoDeConcessao = cmbAeroporto.Selected.IATA
    )
);
Select(BtnUpdateAPH)"""

# Cessionarios é tabela do Excel Online: o conector aceita UMA condição por consulta
# ("Cláusula de filtro inválida", 2026-09-18). "Ativa" continua filtrado em memória,
# no Items do ComboBoxRazaoSocial_1, sobre a coleção.
AERO_ONCHANGE = """ClearCollect(
    colEmpresasAtivas,
    Filter(
        Cessionarios,
        AeroportoDeConcessao = cmbAeroporto.Selected.IATA
    )
);
Select(BtnUpdateAPH)"""

RELATORIO = """If(
    !IsBlank(var_gerandoRelatorioDesde) And DateDiff(var_gerandoRelatorioDesde, Now(), TimeUnit.Seconds) < 60,
    Notify("O relatório já está sendo gerado. Aguarde.", NotificationType.Warning, 3000),
    UpdateContext({var_gerandoRelatorioDesde: Now()});
    Set(varIDhtmlCriado, Blank());
    // nome sem "/" nem ":" (o SharePoint não aceita esses caracteres em nome de arquivo)
    IfError(
        Set(
            varIDhtmlCriado,
            'Criar-HTML'.Run(
                HtmlText3.HtmlText,
                "APH-" & Coalesce(var_dadosAPH.PROTOCOLO, Text(var_dadosAPH.ID)) & "-" & Text(Now(), "yyyymmdd-hhmmss")
            ).idhtml
        ),
        Notify("Não foi possível gerar o relatório. Tente de novo em instantes.", NotificationType.Error, 6000)
    );
    If(
        !IsBlank(varIDhtmlCriado),
        With(
            {_url: LookUp(Documentos, ID = varIDhtmlCriado, Miniatura.Large)},
            If(
                IsBlank(_url),
                Notify("O relatório foi criado, mas o PDF ainda não está disponível. Tente de novo em instantes.", NotificationType.Warning, 6000),
                Launch(Substitute(_url, "thumbnail", "pdf"))
            )
        )
    );
    UpdateContext({var_gerandoRelatorioDesde: Blank()})
)"""

EXCLUIR = """If(
    IsBlank(var_dadosAPH.ID),
    Notify("Selecione um atendimento para excluir.", NotificationType.Warning, 3000);
    UpdateContext({deleteMode: false}),
    If(
        IsError(
            Remove(
                tbl_atendimentoPreHospitalar,
                var_dadosAPH
            )
        ),
        Notify("Não foi possível excluir o atendimento. Tente de novo.", NotificationType.Error, 6000),
        Notify("Atendimento excluído.", NotificationType.Success, 3000);
        UpdateContext(
            {
                var_dadosAPH: Blank(),
                isItemSelected: false,
                newMode: false,
                editMode: false,
                viewMode: false,
                deleteMode: false
            }
        );
        Select(BtnUpdateAPH)
    )
)"""

ISENTAR = """With(
    {_reg: LookUp(tbl_atendimentoPreHospitalar, ID = var_dadosAPH.ID)},
    If(
        IsBlank(var_dadosAPH.ID) Or IsBlank(_reg),
        Notify("Atendimento não encontrado. Atualize a lista e tente de novo.", NotificationType.Error, 6000),
        If(
            IsError(
                Patch(
                    tbl_atendimentoPreHospitalar,
                    _reg,
                    {
                        VALOR_REMOÇÃO: 0,
                        VALOR_ATENDIMENTO: 0,
                        ISENTO: true
                    }
                )
            ),
            Notify("Não foi possível isentar o atendimento. Tente de novo.", NotificationType.Error, 6000),
            Notify("Atendimento isento.", NotificationType.Success, 3000);
            Select(BtnUpdateAPH);
            UpdateContext(
                {
                    var_dadosAPH: Blank(),
                    isItemSelected: false,
                    newMode: false,
                    editMode: false,
                    viewMode: false,
                    deleteMode: false,
                    var_visibleIsentar: false
                }
            )
        )
    )
)"""

GALERIA_ONSELECT = """UpdateContext(
    {
        isItemSelected: true,
        newMode: false,
        editMode: false,
        viewMode: true,
        var_dadosAPH: Table.Selected,
        var_formTitle: "Editar",
        var_tentouSalvar: false,
        var_visibleAlerta: false
    }
);
ViewForm(FormAphEdt)"""

NOVO = """NewForm(FormAphEdt);
UpdateContext(
    {
        newMode: true,
        editMode: false,
        viewMode: false,
        var_dadosAPH: Blank(),
        var_tentouSalvar: false,
        var_visibleAlerta: false
    }
)"""

EDITAR = """UpdateContext(
    {
        newMode: false,
        editMode: true,
        viewMode: false,
        var_tentouSalvar: false,
        var_visibleAlerta: false
    }
);
EditForm(FormAphEdt)"""

CANCELAR = """ResetForm(FormAphEdt);
UpdateContext(
    {
        newMode: false,
        editMode: false,
        viewMode: false,
        isItemSelected: false,
        var_dadosAPH: Blank(),
        var_tentouSalvar: false,
        var_visibleAlerta: false,
        var_salvandoDesde: Blank()
    }
);"""

VOLTAR = """ResetForm(FormAphEdt);
UpdateContext(
    {
        newMode: false,
        editMode: false,
        isItemSelected: false,
        var_tentouSalvar: false,
        var_visibleAlerta: false
    }
);"""

CESSIONARIO = 'DataCardValue10_2.Selected.Value = "CESSIONARIO COMERCIAL"'


# ----------------------------------------------------------------------------
# Operações. set = substitui a fórmula inteira; sub = troca trecho exato.
# O 4º campo de set é um trecho que tem de existir no valor atual (prova que a
# cirurgia está no lugar certo); None para propriedade nova.
# ----------------------------------------------------------------------------
def operacoes():
    ops = []

    def s(ctrl, prop, formula, espera):
        ops.append(('set', ctrl, prop, formula, espera))

    def sub(ctrl, prop, velho, novo, n=1):
        ops.append(('sub', ctrl, prop, velho, novo, n))

    # --- tela e filtros ---------------------------------------------------
    s('__tela__', 'OnVisible', ONVISIBLE, 'isItemSelected: false')
    s('cmbAeroporto', 'OnChange', AERO_ONCHANGE, 'Select(BtnUpdateAPH)')
    s('cmbtip', 'Default', 'Blank()', 'varAeroUser')
    s('cmbtip', 'Tooltip', '"Tipo (atendimento ou remoção)"', '"Remoção"')
    s('cmbCat', 'Default', 'Blank()', 'varBlocoUser')
    s('cmbAmb', 'Default', 'Blank()', 'varAeroUser')
    s('cmbAmb', 'Tooltip', '"Tipo de ambulância"', '"Remoção"')
    s('dtpBuscarIni', 'DefaultDate', 'Date(Year(Today()), Month(Today()), 1)', 'DateValue("01/"')
    sub('Table', 'Items',
        "DateValue('HORÁRIO DO ACIONAMENTO') >= dtpBuscarIni.SelectedDate",
        "'HORÁRIO DO ACIONAMENTO' >= dtpBuscarIni.SelectedDate")
    sub('Table', 'Items',
        "DateValue('HORÁRIO DO ACIONAMENTO') <= dtpBuscarFin.SelectedDate",
        "'HORÁRIO DO ACIONAMENTO' < DateAdd(dtpBuscarFin.SelectedDate, 1, TimeUnit.Days)")
    s('Button2', 'OnSelect', GALERIA_ONSELECT, 'var_cnpjAPH')

    # --- barra de ações -----------------------------------------------------
    s('AddNewButton1_1', 'OnSelect', NOVO, 'NewForm(FormAphEdt)')
    s('NewRecordButton1_1', 'OnSelect', NOVO, 'NewForm(FormAphEdt)')
    s('EditButton1_1', 'OnSelect', EDITAR, 'EditForm(FormAphEdt)')
    s('EditButton1_1', 'Visible', 'And(!newMode, !deleteMode, !IsBlank(var_dadosAPH))', 'And(!newMode, !deleteMode)')
    s('DeleteButton1_1', 'Visible', 'And(!newMode, !deleteMode, !IsBlank(var_dadosAPH))', 'And(!newMode, !deleteMode)')
    s('BackIcon1_1', 'OnSelect', VOLTAR, 'CurrentItem: Table.Selected')
    s('CancelButton1_1', 'OnSelect', CANCELAR, 'var_dadosAPH: Blank()')
    s('EditButton1_2', 'OnSelect', RELATORIO, "'Criar-HTML'.Run(")
    s('ConfirmDeleteButton1_1', 'OnSelect', EXCLUIR, 'Remove(')
    s('ConfirmDeleteButton1_2', 'OnSelect', ISENTAR, 'ISENTO: true')

    # --- valores e moeda ----------------------------------------------------
    sub('ValueAtendimento_1', 'Text', 'varAeroUser = "CURITIBA"', 'DataCardValue4_3.Value = "CURITIBA"')
    for ctrl, rotulo in (('Label129_3', 'ATENDIMENTO: '), ('Label129_5', 'REMOÇÃO: '), ('Label129_6', 'TOTAL: ')):
        sub(ctrl, 'Text', f'"{rotulo}" & Text(', f'"{rotulo}R$ " & Text(')
        sub(ctrl, 'Text', '"$ #,##0.00",', '"#,##0.00",')

    # --- formulário ---------------------------------------------------------
    s('FormAphEdt', 'OnSuccess', ONSUCCESS, 'Self.LastSubmit.ID')
    s('FormAphEdt', 'OnFailure', ONFAILURE, 'Verifique os campos obrigatórios')

    # em voo: toggle escondido (chegada espontânea) não pode continuar valendo
    s('EM VOO_DataCard1_1', 'Update', 'DataCardValue71_1.Checked And Self.Visible', 'DataCardValue71_1.Checked')
    s('NÚMERO DO VOO_DataCard1_1', 'Visible', "DataCardValue71_1.Checked And 'EM VOO_DataCard1_1'.Visible", 'DataCardValue71_1.Checked')
    s('NÚMERO DO VOO_DataCard1_1', 'Required', 'Self.Visible', 'DataCardValue71_1.Checked')

    # empresa/CNPJ: só para cessionário comercial (resposta 3)
    s('INFORME A EMPRESA/RAZÃO SOCIAL_DataCard1_2', 'Required', CESSIONARIO, '<> "VISITANTE"')
    s('INFORME A EMPRESA/RAZÃO SOCIAL_DataCard1_2', 'Visible', CESSIONARIO, '<> "VISITANTE"')
    s('ComboBoxRazaoSocial_1', 'DefaultSelectedItems', 'Filter(colEmpresasAtivas, RazaoSocial = Parent.Default)', '[Parent.Default]')
    s('ComboBoxRazaoSocial_1', 'OnChange', '', 'var_cnpjAPH')
    s('CNPJ_DataCard1_2', 'Required', CESSIONARIO, '<> "VISITANTE"')
    s('CNPJ_DataCard1_2', 'Visible', CESSIONARIO, None)

    # trocar o tipo de ambulância não apaga mais os horários digitados
    s('DataCardValueRemocao_1', 'OnChange', '', 'Reset(HourValue14_1)')

    # encerramento já era exigido pelo Salvar; agora o card diz isso (estrela)
    s('HORÁRIO DO ENCERRAMENTO DO ATENDIMENTO_DataCard1_2', 'Required', 'Self.Visible', 'false')

    # rótulo ambíguo ("chegada no local" de quem?)
    s('DataCardKey9_2', 'Text', '"HORÁRIO DE CHEGADA DA AMBULÂNCIA NO LOCAL"', 'HORÁRIO DE CHEGADA NO LOCAL DA OCORRÊNCIA')

    # --- os 9 horários --------------------------------------------------------
    for k in ORDEM:
        c = CARDS[k]
        s(c['card'], 'Update', T_update(k), 'DateTime(')
        if DATA_PADRAO[k]:
            s(c['d'], 'SelectedDate', DATA_PADRAO[k], '.SelectedDate' if k != 'acion' else 'Parent.Default')
        if k != 'voo':  # o primeiro marco já tinha a lista completa, sem filtro
            s(c['h'], 'Items', lista(24), '"23"')
            s(c['m'], 'Items', lista(60), '"59"')
        s(c['h'], 'DefaultSelectedItems', default_itens(k, 'Hour'), 'Hour(Parent.Default)')
        s(c['m'], 'DefaultSelectedItems', default_itens(k, 'Minute'), 'Minute(Parent.Default)')
        for ctrl in (c['d'], c['h'], c['m']):
            s(ctrl, 'BorderColor', borda(k), 'RGBA(255, 0, 0, 1)')
        s(c['err'], 'Text', mensagem(k), 'Parent.Error')
        s(c['err'], 'Visible', 'And(!IsBlank(Self.Text), Parent.DisplayMode = DisplayMode.Edit)', '!IsBlank(Parent.Error)')
        s(c['err'], 'FontColor', TEXTO_ERRO, None)

    # --- alerta de plausibilidade (já existia, sem gatilho) -------------------
    s('SubmitButton1_1', 'OnSelect', salvar(), 'SubmitForm(FormAphEdt)')
    s('HtmlText4', 'HtmlText', ALERTA_HTML, 'limiteAPH_min')
    s('ButtonCanvas5_1', 'OnSelect', 'UpdateContext({var_visibleAlerta: false, var_salvandoDesde: Now()});\nSubmitForm(FormAphEdt)', 'SubmitForm(FormAphEdt)')
    s('ButtonCanvas5_1', 'Text', '"Salvar assim"', '"Confirmar"')

    # --- relatório: moeda e rótulos iguais aos do formulário -------------------
    for campo in ('Registro.VALOR_ATENDIMENTO', 'Registro.VALOR_REMOÇÃO', 'Registro.VALOR_ATENDIMENTO + Registro.VALOR_REMOÇÃO'):
        sub('HtmlText3', 'HtmlText',
            'Text(' + campo + r', \"$ #,##0.00\", \"pt-BR\")',
            r'\"R$ \" & Text(' + campo + r', \"#,##0.00\", \"pt-BR\")')
    sub('HtmlText3', 'HtmlText', 'Data/Hora do Atendimento:', 'Início do Atendimento:')
    sub('HtmlText3', 'HtmlText', 'Chegada da Ambulância:', 'Chegada da Ambulância no Local:')
    return ops


# ----------------------------------------------------------------------------
# Cirurgia em texto
# ----------------------------------------------------------------------------
def ind(linha):
    return len(linha) - len(linha.lstrip(' '))


def fim_bloco(linhas, i):
    base = ind(linhas[i])
    j, ultimo = i + 1, i + 1
    while j < len(linhas):
        s = linhas[j]
        if not s.strip():
            j += 1
            continue
        if ind(s) <= base:
            break
        j += 1
        ultimo = j
    return ultimo


def bloco_props(linhas, ctrl):
    """(inicio, fim, recuo_das_propriedades) do Properties do controle"""
    if ctrl == '__tela__':
        i = linhas.index(f'  {TELA}:')
        filho = 4
    else:
        achados = [n for n, l in enumerate(linhas) if l.strip() == f'- {ctrl}:']
        if len(achados) != 1:
            raise SystemExit(f'✗ controle {ctrl!r}: {len(achados)} ocorrências')
        i = achados[0]
        filho = ind(linhas[i]) + 4
    fim = fim_bloco(linhas, i)
    for j in range(i + 1, fim):
        if linhas[j].strip() == 'Properties:' and ind(linhas[j]) == filho:
            return j, fim_bloco(linhas, j), filho + 2
    raise SystemExit(f'✗ controle {ctrl!r} sem Properties')


def achar_prop(linhas, ini, fim, recuo, prop):
    pat = re.compile(r'^ {' + str(recuo) + r'}' + re.escape(prop) + r':(\s|$)')
    for k in range(ini + 1, fim):
        if pat.match(linhas[k]):
            return k, fim_bloco(linhas, k)
    return None, None


def renderizar(prop, recuo, formula):
    corpo = '=' + formula
    unica = ('\n' not in corpo and ': ' not in corpo and ' #' not in corpo
             and corpo == corpo.rstrip() and len(corpo) <= 120)
    if unica:
        return [' ' * recuo + f'{prop}: {corpo}']
    out = [' ' * recuo + f'{prop}: |-']
    for linha in corpo.split('\n'):
        out.append((' ' * (recuo + 2) + linha) if linha.strip() else '')
    return out


def aplicar(linhas, op):
    tipo, ctrl, prop = op[0], op[1], op[2]
    ini, fim, recuo = bloco_props(linhas, ctrl)
    k, kf = achar_prop(linhas, ini, fim, recuo, prop)
    if tipo == 'set':
        formula, espera = op[3], op[4]
        novas = renderizar(prop, recuo, formula)
        if k is None:
            if espera:
                raise SystemExit(f'✗ {ctrl}.{prop} não existe, mas a operação esperava {espera!r}')
            pos = fim
            for j in range(ini + 1, fim):
                if ind(linhas[j]) == recuo:
                    m = re.match(r"^\s*([A-Za-z_][\w.']*):", linhas[j])
                    if m and m.group(1).lower() > prop.lower():
                        pos = j
                        break
            linhas[pos:pos] = novas
        else:
            atual = '\n'.join(linhas[k:kf])
            if espera and espera not in atual:
                raise SystemExit(f'✗ {ctrl}.{prop}: trecho esperado {espera!r} não está no valor atual')
            linhas[k:kf] = novas
    else:
        velho, novo, n = op[3], op[4], op[5]
        if k is None:
            raise SystemExit(f'✗ {ctrl}.{prop} não existe')
        bloco = '\n'.join(linhas[k:kf])
        if bloco.count(velho) != n:
            raise SystemExit(f'✗ {ctrl}.{prop}: {velho!r} ocorre {bloco.count(velho)}x (esperado {n})')
        linhas[k:kf] = bloco.replace(velho, novo).split('\n')


# ----------------------------------------------------------------------------
# Conferência por valor (lição 2026-09-17: comparar lendo como YAML)
# ----------------------------------------------------------------------------
class _Loader(yaml.SafeLoader):
    pass


_Loader.add_constructor('tag:yaml.org,2002:value', lambda l, n: l.construct_scalar(n))


def achatar(doc):
    props, arvore = {}, []

    def walk(no, nome, caminho):
        for p, v in (no.get('Properties') or {}).items():
            props[(nome, p)] = v
        for item in no.get('Children') or []:
            for filho, sub in item.items():
                arvore.append((caminho + (filho,), sub.get('Control'), sub.get('Variant')))
                walk(sub, filho, caminho + (filho,))

    corpo = doc['Screens'][TELA]
    walk(corpo, '__tela__', ())
    return props, arvore


def conferir(txt_src, txt_out, ops):
    src, out = yaml.load(txt_src, Loader=_Loader), yaml.load(txt_out, Loader=_Loader)
    p_src, a_src = achatar(src)
    p_out, a_out = achatar(out)
    assert a_src == a_out, 'árvore de controles mudou'
    esperado = dict(p_src)
    for op in ops:
        chave = (op[1], op[2])
        if op[0] == 'set':
            esperado[chave] = '=' + op[3]
        else:
            velho = yaml.load('x: "' + op[3] + '"', Loader=_Loader)['x'] if '\\"' in op[3] else op[3]
            novo = yaml.load('x: "' + op[4] + '"', Loader=_Loader)['x'] if '\\"' in op[4] else op[4]
            assert velho in esperado[chave], f'{chave}: trecho decodificado ausente'
            esperado[chave] = esperado[chave].replace(velho, novo)
    erros = []
    for chave in sorted(set(esperado) | set(p_out), key=str):
        if esperado.get(chave) != p_out.get(chave):
            erros.append(f'{chave}: valor relido difere do pretendido')
    mudadas = sorted({(op[1], op[2]) for op in ops})
    for chave in mudadas:
        if p_src.get(chave) == p_out.get(chave):
            erros.append(f'{chave}: operação declarada não mudou nada')
    if erros:
        raise SystemExit('✗ ' + '\n✗ '.join(erros))
    return mudadas, len(a_out)


def main():
    txt_src = open(SRC, encoding='utf-8', newline='').read()
    assert '\r' not in txt_src, 'export com CRLF: tratar antes'
    linhas = txt_src.split('\n')
    ops = operacoes()
    for op in ops:
        aplicar(linhas, op)
    txt = '\n'.join(linhas)
    i = txt.index('Screens:\n')
    txt = txt[:i] + CABECALHO_EXTRA + txt[i:]
    mudadas, n_ctrl = conferir(txt_src, txt, ops)
    os.makedirs('out', exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(txt)
    excecoes = {'somem': [], 'surgem': [],
                'mudam': sorted([TELA, c, p] for c, p in mudadas if p in VISUAIS and c != '__tela__')}
    with open(EXC, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(excecoes, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print(f'   ✓ {OUT}: {n_ctrl} controles, {len(mudadas)} propriedades alteradas '
          f'({len(excecoes["mudam"])} visuais declaradas em {EXC})')


if __name__ == '__main__':
    main()
