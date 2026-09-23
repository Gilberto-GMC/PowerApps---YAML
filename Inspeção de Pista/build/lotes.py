# -*- coding: utf-8 -*-
"""Correções rápidas do app mobile "Inspeção de Pista" (2026-09-17).

Objetivo: parar a perda e a duplicação de dados sem depender de sonda nem de
mudança de esquema. Nada de SaveData/ParseJSON/Title aqui (nunca apareceram num
export deste repositório); só construções que o Studio já aceitou:
If(IsError(Patch(...))), IfError em cadeia, alias As, ForAll com projeção de
registro, AddColumns com identificador, "toque de novo para confirmar".

Roda com o gerador do projeto principal, com cwd nesta pasta:
    python ../Inspeções/build/gerar_leve.py --lote Q --lotes build/lotes.py

Toda troca de fórmula inteira confere marcadores do texto de origem e aborta se
o export tiver mudado (ex.: alguém editou a tela no Studio e reexportou).
"""
import lote_cd as CD

PROJETO = 'Inspeção de Pista'
NUM = {'App': 1, 'frmInspPistaMob': 3, 'ScreenLogin': 4}
TELAS_MORTAS = set()


class Abortar(SystemExit):
    pass


def _ind(txt, n):
    # linha só de espaços mantém os espaços (mesma regra do gerador: valor da fórmula intacto)
    return '\n'.join((' ' * n + l) if l else '' for l in txt.split('\n'))


def _trocas(*itens):
    """itens: (controle, prop, novo | callable(atual) -> novo, [marcadores do original])"""
    def fn(tela, txt, contar, ctx):
        n = 0
        for controle, prop, novo, marcadores in itens:
            atual = CD.ler_prop(txt, controle, prop)
            faltam = [m for m in marcadores if m not in atual]
            if faltam:
                raise Abortar(f"{tela}.{controle}.{prop}: o texto de origem não é o esperado "
                              f"(faltam {faltam}) — conferir o export antes de gerar")
            if not contar:
                corpo = novo(atual) if callable(novo) else novo
                txt = CD.gravar_prop(txt, controle, prop, corpo)
            n += 1
        return txt, n
    return fn


# ─────────────────────────────────────────────────────────────────────────────
# Proteção contra descarte: com apontamentos ainda não enviados, o 1º toque avisa
# e o 2º toque em até 10 s confirma (mesmo padrão já usado em Mapa de Alocação).
# ─────────────────────────────────────────────────────────────────────────────
GUARDA = '''// Proteção contra perda (2026-09-17): com apontamentos ainda não enviados neste
// aparelho, o 1º toque só avisa; o 2º toque em até 10 segundos confirma o descarte.
If(
    (
        !IsEmpty(Filter(col_inspPista_mob_temp As B, IsBlank(B.ID))) ||
        !IsEmpty(Filter(col_inspPistaItens_mob_temp As B, IsBlank(B.ID))) ||
        !IsEmpty(col_anotacaoAudio_mob)
    ) && !var_envioOk && (IsBlank(var_confirmaDescarte) || DateDiff(var_confirmaDescarte, Now(), TimeUnit.Seconds) > 10),
    UpdateContext({var_confirmaDescarte: Now()});
    Notify(
        "Há uma inspeção com apontamentos que ainda não foram enviados neste aparelho. Toque de novo em até 10 segundos para descartá-la.",
        NotificationType.Warning,
        8000
    ),
    UpdateContext({var_confirmaDescarte: Blank()});
{CORPO}
)'''


def com_guarda(corpo):
    return '=' + GUARDA.replace('{CORPO}', _ind(corpo.strip().rstrip(';'), 4))


CORPO_CADASTRAR = '''Set(
    var_visibleHome,
    false
);
UpdateContext(
    {
        var_visibleInspecaoCad: true,
        var_visibleInspecaoCad1: true,
        var_statusInspecao: "Em andamento",
        Var_IDinspPistaInsert: 0,
        varTopico: "0",
        var_acao: "Nova Inspeção",
        var_idInspContinuar: 0,
        var_envioOk: false,
        var_envioErro: ""
    }
);
Clear(col_anotacaoAudio_mob);
Clear(col_addProtocoloItens);
Clear(col_inspPistaItens_mob_temp);
Clear(col_inspPista_mob_temp);
ResetForm(FormInspPistaCad1_3);
NewForm(FormInspPistaCad1_3)'''

CORPO_CONTINUAR = '''Set(
    var_visibleHome,
    false
);
UpdateContext(
    {
        var_visibleInspecaoCad: true,
        var_visibleInspecaoCad1: true,
        var_statusInspecao: "Em andamento",
        Var_IDinspPistaInsert: 0,
        varTopico: "0",
        var_acao: "Continuar Inspeção",
        // a inspeção continuada já existe no servidor: o envio usa este ID e não cria cabeçalho
        var_idInspContinuar: ThisItem.ID,
        var_envioOk: false,
        var_envioErro: "",
        var_hash: Coalesce(
            ThisItem.hash,
            Text(
                Now(),
                "yyyymmddhhmmss"
            ) & RoundDown(
                Rand() * 100000,
                0
            )
        )
    }
);
// o buffer passa a conter só esta inspeção (antes: os itens do servidor entravam sem
// InspHash, não apareciam no resumo e eram recriados como novos no envio)
ClearCollect(
    col_inspPista_mob_temp,
    ThisItem
);
Patch(
    col_inspPista_mob_temp,
    LookUp(col_inspPista_mob_temp As B, B.ID = ThisItem.ID),
    {hash: var_hash}
);
Clear(col_anotacaoAudio_mob);
ClearCollect(
    col_inspPistaItens_mob_temp,
    AddColumns(
        Filter(
            Sort(
                '7.4.1-tbl_InspPistaItens',
                ID,
                SortOrder.Descending
            ),
            Aeroporto = varAeroUser And IdInsp = ThisItem.ID
        ),
        InspHash,
        var_hash
    )
);
EditForm(FormInspPistaCad1_3)'''

ENVIO = '''=// Envio idempotente (2026-09-17). Cada passo confere no servidor antes de criar, então
// repetir o envio depois de uma falha não duplica nada. O "Finalizar" só limpa o aparelho
// quando var_envioOk confirma que cabeçalho, itens, protocolos e áudios estão no servidor.
UpdateContext({var_loadVincularInspPista: true, var_envioOk: false, var_envioErro: ""});
// 1. cabeçalho: a inspeção continuada já existe; a nova é procurada pelo hash antes de ser criada
If(
    var_idInspContinuar > 0,
    UpdateContext({var_idInspRegister: LookUp('7.4-tbl_InspPista', ID = var_idInspContinuar)}),
    IsBlank(var_hash) || IsBlank(LookUp(col_inspPista_mob_temp As B, B.hash = var_hash).hash),
    UpdateContext({var_idInspRegister: Blank(), var_envioErro: "a inspeção não está mais neste aparelho"}),
    UpdateContext({var_idInspRegister: LookUp('7.4-tbl_InspPista', hash = var_hash)});
    If(
        IsBlank(var_idInspRegister.ID),
        If(
            IsError(
                Patch(
                    '7.4-tbl_InspPista',
                    Defaults('7.4-tbl_InspPista'),
                    LookUp(col_inspPista_mob_temp As B, B.hash = var_hash)
                )
            ),
            UpdateContext({var_envioErro: "não foi possível gravar a inspeção"})
        );
        UpdateContext({var_idInspRegister: LookUp('7.4-tbl_InspPista', hash = var_hash)})
    )
);
If(
    IsBlank(var_idInspRegister.ID),
    If(
        IsBlank(var_envioErro),
        UpdateContext({var_envioErro: "sem resposta do SharePoint"})
    ),
    // 2. ID_pk e protocolo da inspeção, só se ainda não gravados
    If(
        IsBlank(LookUp('7.4-tbl_InspPista', ID = var_idInspRegister.ID).Protocolo),
        If(
            IsError(
                Patch(
                    '7.4-tbl_InspPista',
                    LookUp('7.4-tbl_InspPista', ID = var_idInspRegister.ID),
                    {
                        ID_pk: var_idInspRegister.ID,
                        Protocolo: varIATAUser & "-INSP-PISTA-" & var_idInspRegister.ID
                    }
                )
            ),
            UpdateContext({var_envioErro: "não foi possível gravar o protocolo da inspeção"})
        )
    );
    // 3. itens criados neste aparelho (sem ID), cada um só se o Hash ainda não existir no servidor
    ForAll(
        Filter(col_inspPistaItens_mob_temp As F, F.InspHash = var_hash && IsBlank(F.ID)) As IT,
        If(
            IsBlank(IT.Hash) || IsBlank(LookUp('7.4.1-tbl_InspPistaItens', Hash = IT.Hash).ID),
            Patch(
                '7.4.1-tbl_InspPistaItens',
                Defaults('7.4.1-tbl_InspPistaItens'),
                {
                    IdInsp: var_idInspRegister.ID,
                    Bloco: IT.Bloco,
                    IATA: IT.IATA,
                    Aeroporto: IT.Aeroporto,
                    Local: IT.Local,
                    Item: IT.Item,
                    sIten: IT.sIten,
                    Latitude: IT.Latitude,
                    Longitude: IT.Longitude,
                    Status: "Pendente",
                    DataInicioApont: IT.DataInicioApont,
                    HoraInicioApont: IT.HoraInicioApont,
                    UsuarioCriador: IT.UsuarioCriador,
                    Hash: IT.Hash,
                    Foto: IT.Foto,
                    Foto2: IT.Foto2,
                    Foto3: IT.Foto3
                }
            )
        )
    );
    // 4. protocolo dos itens que ainda não têm (não reescreve protocolo existente)
    ClearCollect(
        col_addProtocoloItens,
        ForAll(
            Filter('7.4.1-tbl_InspPistaItens', IdInsp = var_idInspRegister.ID) As R,
            {ID: R.ID, Hash: R.Hash, Protocolo: R.Protocolo}
        )
    );
    ForAll(
        Filter(col_addProtocoloItens As F, IsBlank(F.Protocolo)) As P,
        Patch(
            '7.4.1-tbl_InspPistaItens',
            LookUp('7.4.1-tbl_InspPistaItens', ID = P.ID),
            {Protocolo: varIATAUser & "-INSP-PISTA-ITEM-" & P.ID}
        )
    );
    // 5. áudios desta inspeção. A lista de áudios não tem chave própria: um áudio já enviado
    // é reconhecido por local, item, subitem e tamanho do conteúdo
    ClearCollect(
        col_envioAudiosSrv,
        ForAll(
            Filter(tbl_inspPistaAnotacao, ID_FK = var_idInspRegister.ID) As R,
            {ID: R.ID, Local: R.Local, Item: R.Item, SItem: R.SItem, Tamanho: Len(R.Audio)}
        )
    );
    ForAll(
        Filter(col_anotacaoAudio_mob As F, F.ID_HASH = var_hash) As A,
        If(
            IsBlank(LookUp(col_envioAudiosSrv As S, S.Local = A.LOCAL && S.Item = A.ITEM && S.SItem = A.SITEM && S.Tamanho = Len(A.AUDIO)).ID),
            Patch(
                tbl_inspPistaAnotacao,
                Defaults(tbl_inspPistaAnotacao),
                {
                    ID_FK: var_idInspRegister.ID,
                    Audio: A.AUDIO,
                    Local: A.LOCAL,
                    Item: A.ITEM,
                    SItem: A.SITEM
                }
            )
        )
    );
    // 6. conferência no servidor: só com tudo confirmado o "Finalizar" limpa o aparelho
    ClearCollect(
        col_addProtocoloItens,
        ForAll(
            Filter('7.4.1-tbl_InspPistaItens', IdInsp = var_idInspRegister.ID) As R,
            {ID: R.ID, Hash: R.Hash, Protocolo: R.Protocolo}
        )
    );
    ClearCollect(
        col_envioAudiosSrv,
        ForAll(
            Filter(tbl_inspPistaAnotacao, ID_FK = var_idInspRegister.ID) As R,
            {ID: R.ID, Local: R.Local, Item: R.Item, SItem: R.SItem, Tamanho: Len(R.Audio)}
        )
    );
    UpdateContext(
        {
            var_envioOk: IsBlank(var_envioErro) &&
                IsEmpty(
                    Filter(
                        col_inspPistaItens_mob_temp As IT,
                        IT.InspHash = var_hash && IsBlank(IT.ID) &&
                        IsBlank(LookUp(col_addProtocoloItens As S, S.Hash = IT.Hash).ID)
                    )
                ) &&
                IsEmpty(Filter(col_addProtocoloItens As S, IsBlank(S.Protocolo))) &&
                IsEmpty(
                    Filter(
                        col_anotacaoAudio_mob As A,
                        A.ID_HASH = var_hash &&
                        IsBlank(LookUp(col_envioAudiosSrv As S, S.Local = A.LOCAL && S.Item = A.ITEM && S.SItem = A.SITEM && S.Tamanho = Len(A.AUDIO)).ID)
                    )
                )
        }
    )
);
UpdateContext({var_loadVincularInspPista: false});
If(
    !var_envioOk,
    Notify(
        "Nem tudo foi enviado" & If(IsBlank(var_envioErro), "", ": " & var_envioErro) & ". Os apontamentos continuam neste aparelho; toque em Finalizar para tentar de novo.",
        NotificationType.Error,
        8000
    )
)'''

FINALIZAR = '''=If(
    var_envioOk && !IsBlank(var_idInspRegister.ID),
    // envio confirmado no servidor: atualiza o status e só então limpa o aparelho
    Set(
        var_visibleHome,
        true
    );
    UpdateContext(
        {
            var_visibleSalvarManual: false,
            var_visibleInspecaoCad: false
        }
    );
    If(
        !IsBlank(LookUp(col_inspPista_mob As L, L.ID = var_idInspRegister.ID).ID),
        Patch(
            col_inspPista_mob,
            LookUp(col_inspPista_mob As L, L.ID = var_idInspRegister.ID),
            {
                Status: If(
                    CountRows(col_inspPistaItens_mob_temp) > 0,
                    "Pendente",
                    "Finalizado"
                ),
                DataFim: Today(),
                Fim: TimeValue(Now())
            }
        )
    );
    If(
        IsError(
            Patch(
                '7.4-tbl_InspPista',
                LookUp(
                    '7.4-tbl_InspPista',
                    ID = var_idInspRegister.ID
                ),
                {
                    Status: If(
                        CountRows(col_inspPistaItens_mob_temp) > 0,
                        "Pendente",
                        "Finalizado"
                    ),
                    DataFim: Today(),
                    Fim: TimeValue(Now())
                }
            )
        ),
        Notify(
            "Os apontamentos foram enviados, mas o status da inspeção não foi atualizado. Use Continuar para finalizá-la depois.",
            NotificationType.Warning,
            8000
        )
    );
    Clear(col_inspPista_mob_temp);
    Clear(col_inspPistaItens_mob_temp);
    RemoveIf(col_anotacaoAudio_mob, ID_HASH = var_hash);
    UpdateContext({var_envioOk: false, var_idInspContinuar: 0});
    Select(IconRefreshInspPistaMob),
    Connection.Connected,
    // envio não confirmado e há conexão: reenvia (o envio é idempotente)
    Notify(
        "O envio ainda não foi confirmado. Tentando enviar de novo…",
        NotificationType.Warning,
        5000
    );
    Select(ButtonCanvasSalvarTodos),
    Notify(
        "Sem conexão: os apontamentos continuam neste aparelho. Não feche o app e toque em Finalizar quando houver sinal.",
        NotificationType.Error,
        8000
    )
)'''

FECHAR_PAINEL = '''=If(
    var_envioOk,
    Set(
        var_visibleHome,
        true
    );
    UpdateContext(
        {
            var_visibleSalvarManual: false,
            var_visibleInspecaoCad: false
        }
    ),
    // envio não confirmado: volta ao passo 1 desta inspeção, onde "Finalizar Inspeção" reenvia
    // (antes ia para a lista, sem caminho de volta aos apontamentos que só estavam na memória)
    UpdateContext(
        {
            var_visibleSalvarManual: false,
            var_visibleInspecaoCad: true,
            var_visibleInspecaoCad1: true,
            var_visibleInspecaoCad2: false,
            var_visibleInspecaoCad3: false,
            var_acao: "Finalizar Inspeção"
        }
    );
    EditForm(FormInspPistaCad1_3)
)'''

HASH_ANTES = '''        Hash: Text(
            Now(),
            "yyyymmddhhmmss"
        ) & Text(
            Rand(),
            "[$-en-US]########"
        ),'''
HASH_DEPOIS = '''        // chave única: data e hora, usuário e 6 dígitos aleatórios (antes a máscara
        // "########" sobre uma fração devolvia no máximo 1 dígito)
        Hash: Text(
            Now(),
            "yyyymmddhhmmss"
        ) & "-" & varIdUser & "-" & Text(
            RoundDown(Rand() * 1000000, 0),
            "000000"
        ),'''

CIRURGIAS = [
    dict(id='Q1', lote='Q', tipo='func', telas=['frmInspPistaMob'], esperado={'frmInspPistaMob': 1},
         descricao='envio idempotente com conferência no servidor (sem duplicar, sem apagar o que não subiu)',
         fn=_trocas(('ButtonCanvasSalvarTodos', 'OnSelect', ENVIO,
                     ["novoRegistro: Patch(", "col_addProtocoloItens", "tbl_inspPistaAnotacao", "var_loadVincularInspPista"]))),
    dict(id='Q2', lote='Q', tipo='func', telas=['frmInspPistaMob'], esperado={'frmInspPistaMob': 2},
         descricao='"Finalizar" só limpa com envio confirmado (senão reenvia); fechar o painel volta à inspeção',
         fn=_trocas(('ButtonCanvas3_5', 'OnSelect', FINALIZAR,
                     ["Clear(col_inspPista_mob_temp)", "Clear(col_inspPistaItens_mob_temp)", "var_idInspRegister.ID"]),
                    ('Icon10_1', 'OnSelect', FECHAR_PAINEL,
                     ["var_visibleSalvarManual: false", "var_visibleInspecaoCad: false"]))),
    dict(id='Q3', lote='Q', tipo='prop', descricao='Hash do apontamento com unicidade real',
         alvos=[('frmInspPistaMob', 'ButtonCanvas2_6', 'OnSelect', [(HASH_ANTES, HASH_DEPOIS)])]),
    dict(id='Q4', lote='Q', tipo='func', telas=['frmInspPistaMob'], esperado={'frmInspPistaMob': 2},
         descricao='"Cadastrar" e voltar ao hub pedem confirmação se houver apontamento não enviado',
         fn=_trocas(('Icon28_214', 'OnSelect', com_guarda(CORPO_CADASTRAR),
                     ['var_acao: "Nova Inspeção"', "Clear(col_inspPista_mob_temp)", "NewForm(FormInspPistaCad1_3)"]),
                    ('Icon1_18', 'OnSelect', lambda atual: com_guarda(atual),
                     ["cca968cd-f5f6-4c5d-9e06-60371be130be", "LaunchTarget.Replace"]))),
    dict(id='Q5', lote='Q', tipo='func', telas=['frmInspPistaMob'], esperado={'frmInspPistaMob': 1},
         descricao='"Continuar" carrega a inspeção certa e marca os itens do servidor como já enviados',
         fn=_trocas(('ButtonCanvas9', 'OnSelect', com_guarda(CORPO_CONTINUAR),
                     ['var_acao: "Continuar Inspeção"', "EditForm(FormInspPistaCad1_3)", "IdInsp = ThisItem.ID"]))),
    dict(id='Q6', lote='Q', tipo='func', telas=['frmInspPistaMob'], esperado={'frmInspPistaMob': 1},
         descricao='passo "Item" lê o menu já carregado (sem consulta ao SharePoint a cada toque)',
         fn=_trocas(('Gallery13_12', 'Items',
                     '=// lê o menu já carregado no OnVisible (antes: consulta ao SharePoint a cada toque, parava sem sinal)\n'
                     'Filter(\n    col_inspPistaMenu,\n    local = varLocal And categoria = varMenu And !IsBlank(item)\n)',
                     ["tbl_inspMenu", "categoria = varMenu", "!IsBlank(item)"]))),
    dict(id='Q7', lote='Q', tipo='func', telas=['frmInspPistaMob'], esperado={'frmInspPistaMob': 4},
         descricao='painel de envio: status por item sem consulta por linha, erro de envio visível',
         mudam=[('frmInspPistaMob', 'Label12_3', 'Text'), ('frmInspPistaMob', 'ButtonCanvas3_4', 'Visible'),
                ('frmInspPistaMob', 'TextCanvas2_2', 'Text')],
         fn=_trocas(('Label12_3', 'Text',
                     '=If(\n    !IsBlank(ThisItem.ID) || !IsBlank(ThisItem.Protocolo) ||\n'
                     '    (!IsBlank(ThisItem.Hash) && !IsBlank(LookUp(col_addProtocoloItens As S, S.Hash = ThisItem.Hash).ID)),\n'
                     '    "Salvo",\n    "Processando"\n)',
                     ['"Salvo"', '"Processando"', "Hash = ThisItem.Hash"]),
                    # "Salvar manual": nunca ficava visível (exige Protocolo, que o buffer não tem) e
                    # gravaria item órfão; saem as 3 consultas por linha
                    ('ButtonCanvas3_4', 'Visible', '=false', ["IsBlank(ThisItem.Protocolo)", "false,true"]),
                    ('ButtonCanvas3_4', 'DisplayMode', '=DisplayMode.Disabled', ["DisplayMode.Disabled", "DisplayMode.Edit"]),
                    ('TextCanvas2_2', 'Text',
                     '=If(\n    !IsBlank(var_envioErro),\n    "Falha no envio: " & var_envioErro,\n'
                     '    If(Connection.Connected, "Conectado", "Não Conectado")\n)',
                     ['Connection.Connected', '"Não Conectado"']))),
    dict(id='Q8', lote='Q', tipo='prop_regex',
         descricao='não conformidades do ano com filtro delegável (antes: só as 500 linhas mais antigas da lista)',
         alvos=[('App', 'App', 'OnStart',
                 [(r'Year\(Criado\) = Year\(Today\(\)\)', 'Criado >= Date(Year(Today()), 1, 1)', 3)])]),
]
