#!/usr/bin/env python3
"""Gera os pacotes importaveis DD01/DD02 a partir dos rascunhos exportados.

Os pacotes legados do Power Automate sao arquivos ZIP. Este gerador preserva
manifestos, IDs e conexoes ja existentes, substitui somente a definicao dos
fluxos e acrescenta os conectores que faltam.
"""

from __future__ import annotations

import copy
import json
import uuid
import zipfile
from pathlib import Path
from urllib.parse import quote as url_quote


BASE = Path(__file__).resolve().parent
SITE_URL = "https://grupoccr.sharepoint.com/sites/ComplianceAeroportos"
MAIN_LIST_ID = "ad57d68b-addf-466d-a86e-034035c412d6"
MAIN_LIST = "tb_dueDiligence"
PARAM_LIST = "tb_dueDiligenceParametros"
RESPONSE_LIST = "tb_dueDiligenceTerceiroRespostas"
HISTORY_LIST = "tb_dueDiligenceDesdobramentos"
TIME_ZONE = "E. South America Standard Time"

# Status definidos pelo Compliance em 2026-09-10. A grafia é contrato: o app
# compara com `=`, que diferencia maiúsculas de minúsculas.
STATUS_AGUARDANDO_TERCEIRO = "Aguardando Terceiro"
STATUS_PENDENTE_COMPLIANCE = "Pendente Compliance"
STATUS_APROVADO = "Aprovado"
STATUS_VENCIDO = "Vencido"
# Decisões que abrem vigência: 1 ano (risco alto), 2 (médio) e 3 (baixo).
STATUS_COM_VIGENCIA = ("Aprovado", "Aprovado com Ressalvas", "Reprovado Parcialmente")
# As quatro decisões do parecer final: o laudo existe para todas, inclusive Reprovado.
STATUS_DECISOES_FINAIS = ("Aprovado", "Aprovado com Ressalvas", "Reprovado Parcialmente", "Reprovado")
# Os oito status do modelo; o DD05 tem uma mensagem ao solicitante para cada um.
STATUS_TODOS = (
    STATUS_AGUARDANDO_TERCEIRO,
    STATUS_PENDENTE_COMPLIANCE,
    *STATUS_DECISOES_FINAIS,
    "Cancelado",
    STATUS_VENCIDO,
)

FORM_ID = (
    "itUz0nOZp0OvaWdjYwVIoMoEbKAMYIZFqUAdth6B_EFURVRKSFdaVDE4Q1RIV0VTRkxFSjFZS0VEQS4u"
)
TRACKING_QUESTION_ID = "rf6e81f83fe194d4c80dbfd30fc7b8301"
FORM_URL = (
    "https://forms.office.com/Pages/ResponsePage.aspx?"
    f"id={FORM_ID}&origin=lprLink"
)

SEND_DRAFT = BASE / "EnviarquestionarioDueDiligence_20260908155750.zip"
SEND_DRAFT_UTF8 = BASE / "EnviarquestionárioDueDiligence_20260908155750.zip"
SEND_READY = BASE / "EnviarquestionarioDueDiligence_PRONTO.zip"
PROCESS_DRAFT = BASE / "ProcessarrespostaDueDiligence_20260908193843.zip"
PROCESS_READY = BASE / "ProcessarrespostaDueDiligence_PRONTO.zip"
EXPIRY_READY = BASE / "VencervigenciaDueDiligence_PRONTO.zip"
EXPIRY_NAME = "Vencer vigência Due Diligence"
SOURCE_DIR = BASE / "PowerAutomate"
LAUDO_READY = BASE / "GerarLaudoDueDiligence_PRONTO.zip"
LAUDO_LIBRARY = "Laudos Due Diligence"
NOTIFY_READY = BASE / "NotificarstatusDueDiligence_PRONTO.zip"
NOTIFY_NAME = "Notificar status Due Diligence"
COMPLIANCE_LIST = "tb_dueDiligenceCompliance"

QUESTIONS = [
    {
        "action": "T01",
        "id": "rc17ec46a782c4e9bb8577f1776f7b6a5",
        "code": "terceiro_t01",
        "order": 1,
        "text": "T1) A empresa possui um programa de integridade implementado?",
    },
    {
        "action": "T01_2",
        "id": "rc8315faaa6674c8584da070ee5350001",
        "code": "terceiro_t01_2",
        "order": 2,
        "text": (
            "T1.2) Caso positivo, esse programa conta com certificações como "
            "ISO 37001 e ISO 37301 ou realiza auditorias independentes?"
        ),
        "conditional": True,
    },
    {
        "action": "T02",
        "id": "reabf29569f654ca7876bd8dd6470ef47",
        "code": "terceiro_t02",
        "order": 3,
        "text": (
            "T2) Atualmente, há no quadro de colaboradores algum ex-funcionário "
            "da ASUR Brasil desligado nos últimos dois anos?"
        ),
    },
    {
        "action": "T03_PEP",
        "id": "r41b1c93b2d5c4cb090fe93048d907b04",
        "code": "terceiro_t03_pep",
        "order": 4,
        "text": (
            "T3) Algum sócio, administrador ou diretor é funcionário público, "
            "PEP ou parente de alguém nessas condições?"
        ),
    },
    {
        "action": "T03_PROCESSOS",
        "id": "rdefccd229818492b9bbe6727758760a7",
        "code": "terceiro_t03_processos",
        "order": 5,
        "text": (
            "T3) A empresa, seus sócios ou diretores estão ou estiveram envolvidos "
            "em processos relacionados a fraude, corrupção, improbidade, lavagem "
            "de dinheiro, trabalho escravo, crime ambiental ou outros crimes?"
        ),
    },
    {
        "action": "T04",
        "id": "ra29396cc8af3475eab68360908138053",
        "code": "terceiro_t04",
        "order": 6,
        "text": "T4) A empresa faz parte de algum grupo econômico?",
    },
    {
        "action": "T05",
        "id": "r26254dcbbf9b4275aa3b824059f6c571",
        "code": "terceiro_t05",
        "order": 7,
        "text": "T5) Qual é a quantidade atual de funcionários da empresa?",
        "text_answer": True,
    },
    {
        "action": "T06",
        "id": "r631326ae893c4c17b3a4c3c627cf6df3",
        "code": "terceiro_t06",
        "order": 8,
        "text": (
            "T6) Algum sócio, administrador ou diretor possui parentesco com "
            "colaboradores, diretores ou conselheiros da ASUR Brasil?"
        ),
    },
    {
        "action": "T07",
        "id": "r7eb11f1294d7429391236b5d533ad22c",
        "code": "terceiro_t07",
        "order": 9,
        "text": (
            "T7) A empresa ou outra empresa do grupo é concorrente direta ou "
            "participa de consórcios concorrentes da ASUR Brasil?"
        ),
    },
    {
        "action": "T08",
        "id": "rf48abfb5124f4eedaf80b66c72091c0c",
        "code": "terceiro_t08",
        "order": 10,
        "text": (
            "T8) A empresa, seus sócios ou diretores já foram mencionados em mídias "
            "relacionadas a fraude, corrupção ou outros fatos relevantes?"
        ),
    },
    {
        "action": "T09",
        "id": "r37e5d456c486487e91f8e39948d26375",
        "code": "terceiro_t09",
        "order": 11,
        "text": "T9) Declara ciência e concordância com o Código de Ética do Fornecedor?",
    },
]


def stable_uuid(label: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"asur-due-diligence:{label}"))


def wdl_literal(value: str) -> str:
    """Codifica literal de texto da Workflow Definition Language."""
    return "'" + value.replace("'", "''") + "'"


def conn_action(api: str, connection: str, operation: str, parameters: dict, run_after=None):
    return {
        "runAfter": run_after or {},
        "type": "OpenApiConnection",
        "inputs": {
            "parameters": parameters,
            "host": {
                "apiId": f"/providers/Microsoft.PowerApps/apis/{api}",
                "connectionName": connection,
                "operationId": operation,
            },
            "authentication": "@parameters('$authentication')",
        },
    }


def sp_http(method: str, uri: str, *, body=None, headers=None, run_after=None, retry="none"):
    params = {
        "dataset": SITE_URL,
        "parameters/method": method,
        "parameters/uri": uri,
        "parameters/headers": headers
        or {"Accept": "application/json;odata=nometadata"},
    }
    if body is not None:
        params["parameters/body"] = body
    action = conn_action(
        "shared_sharepointonline",
        "shared_sharepointonline",
        "HttpRequest",
        params,
        run_after,
    )
    action["inputs"]["retryPolicy"] = {"type": retry}
    return action


def condition(expression: str, yes: dict, no: dict, run_after=None):
    return {
        "runAfter": run_after or {},
        "type": "If",
        "expression": {"and": [{"equals": [expression, True]}]},
        "actions": yes,
        "else": {"actions": no},
    }


def compose(inputs, run_after=None):
    return {"runAfter": run_after or {}, "type": "Compose", "inputs": inputs}


def terminate(status: str, code: str, message: str, run_after=None):
    data = {"runStatus": status}
    if status == "Failed":
        data["runError"] = {"code": code, "message": message}
    return {"runAfter": run_after or {}, "type": "Terminate", "inputs": data}


def initialize_variable(name: str, var_type: str, value, run_after=None):
    return {
        "runAfter": run_after or {},
        "type": "InitializeVariable",
        "inputs": {"variables": [{"name": name, "type": var_type, "value": value}]},
    }


def append_question(q: dict, run_after=None):
    answer = f"@body('Obter_detalhes_da_resposta')?['{q['id']}']"
    if q.get("text_answer"):
        option = f"{q['code']}_texto"
    else:
        option = (
            "@concat('"
            + q["code"]
            + "_', if(equals(toLower(trim(string(body('Obter_detalhes_da_resposta')?['"
            + q["id"]
            + "']))), 'sim'), 'sim', 'nao'))"
        )
    return {
        "runAfter": run_after or {},
        "type": "AppendToArrayVariable",
        "inputs": {
            "name": "varRespostas",
            "value": {
                "codigo_pergunta": q["code"],
                "codigo_opcao": option,
                "texto_pergunta": q["text"],
                "resposta": answer,
                "ordem": q["order"],
            },
        },
    }


def send_actions():
    trigger_id = "@triggerBody()?['ID']"
    current = "body('HTTP_Obter_Item_Atual')"
    valid = (
        "@and("
        f"equals({current}?['status'], {wdl_literal(STATUS_AGUARDANDO_TERCEIRO)}),"
        f"not(empty({current}?['forms_envio_id'])),"
        f"not(equals({current}?['forms_envio_id'], {current}?['forms_envio_processado_id'])),"
        f"not(empty({current}?['forms_correlacao_id'])),"
        f"not(empty({current}?['email_terceiro']))"
        ")"
    )

    link = (
        f"@concat('{FORM_URL}&{TRACKING_QUESTION_ID}=', "
        "uriComponent(string(body('HTTP_Obter_Item_Atual')?['forms_envio_id'])))"
    )
    email_body = (
        "<p>Olá,</p>"
        "<p>A ASUR Brasil solicita o preenchimento do questionário de Due Diligence "
        "referente à empresa <strong>@{body('HTTP_Obter_Item_Atual')?['razao_social']}</strong>.</p>"
        "<p><a href=\"@{outputs('Montar_Link_Questionario')}\">Acessar questionário</a></p>"
        "<p>O código de acompanhamento já está preenchido no link. Não o altere.</p>"
        "<p>Mensagem enviada automaticamente. Em caso de dúvida, responda ao solicitante da contratação.</p>"
    )

    # O status já é Aguardando Terceiro. Regravá-lo desfaria um cancelamento
    # feito pelo Compliance entre a leitura e esta atualização.
    update_body = {
        "forms_formulario_id": FORM_ID,
        "forms_envio_processado_id": "@body('HTTP_Obter_Item_Atual')?['forms_envio_id']",
        "data_envio_terceiro": "@utcNow()",
    }

    main_item_prefix = f"_api/web/lists/getbytitle('{MAIN_LIST}')/items("
    main_uri = (
        f"@concat({wdl_literal(main_item_prefix)}, "
        f"string(triggerBody()?['ID']), {wdl_literal(')')})"
    )
    get_uri = (
        f"@concat({wdl_literal(main_item_prefix)}, "
        "string(triggerBody()?['ID']), "
        f"{wdl_literal(')?$select=ID,status,forms_envio_id,forms_envio_processado_id,forms_correlacao_id,email_terceiro,razao_social')})"
    )

    send_email = conn_action(
        "shared_office365",
        "shared_office365",
        "SendEmailV2",
        {
            "emailMessage/To": "@body('HTTP_Obter_Item_Atual')?['email_terceiro']",
            "emailMessage/Subject": (
                "Questionário de Due Diligence — "
                "@{body('HTTP_Obter_Item_Atual')?['razao_social']}"
            ),
            "emailMessage/Body": email_body,
            "emailMessage/Importance": "Normal",
        },
        {"Montar_Link_Questionario": ["Succeeded"]},
    )
    send_email["inputs"]["retryPolicy"] = {"type": "none"}

    valid_actions = {
        "Montar_Link_Questionario": compose(link),
        "Enviar_Email_V2": send_email,
        "Montar_Atualizacao_Envio": compose(
            update_body, {"Enviar_Email_V2": ["Succeeded"]}
        ),
        "HTTP_Atualizar_Item_Enviado": sp_http(
            "POST",
            main_uri,
            body="@string(outputs('Montar_Atualizacao_Envio'))",
            headers={
                "Accept": "application/json;odata=nometadata",
                "Content-Type": "application/json;odata=nometadata",
                "X-HTTP-Method": "MERGE",
                "IF-MATCH": "*",
            },
            run_after={"Montar_Atualizacao_Envio": ["Succeeded"]},
        ),
        "Montar_Historico_Envio": compose(
            {
                "solicitacao_id": "@int(triggerBody()?['ID'])",
                "tipo_desdobramento": "Envio ao terceiro",
                "status_anterior": "@body('HTTP_Obter_Item_Atual')?['status']",
                "status_novo": STATUS_AGUARDANDO_TERCEIRO,
                "descricao": (
                    "@concat('Questionário enviado ao terceiro. Identificador do envio: ', "
                    "string(body('HTTP_Obter_Item_Atual')?['forms_envio_id']), '.')"
                ),
                # O DD02 localiza por aqui a resposta dada por um link anterior.
                "forms_envio_id": "@string(body('HTTP_Obter_Item_Atual')?['forms_envio_id'])",
                "email_envio": "@string(body('HTTP_Obter_Item_Atual')?['email_terceiro'])",
                "visivel_solicitante": 1,
                "ativo": 1,
            },
            {"HTTP_Atualizar_Item_Enviado": ["Succeeded"]},
        ),
        "HTTP_Registrar_Historico_Envio": sp_http(
            "POST",
            f"_api/web/lists/getbytitle('{HISTORY_LIST}')/items",
            body="@string(outputs('Montar_Historico_Envio'))",
            headers={
                "Accept": "application/json;odata=nometadata",
                "Content-Type": "application/json;odata=nometadata",
            },
            run_after={"Montar_Historico_Envio": ["Succeeded"]},
        ),
        "Envio_Concluido": compose(
            "Questionário enviado; consulte o histórico para confirmar o registro auxiliar.",
            {
                "HTTP_Registrar_Historico_Envio": [
                    "Succeeded",
                    "Failed",
                    "TimedOut",
                ]
            },
        ),
    }
    process_scope = {
        "runAfter": {},
        "type": "Scope",
        "actions": {
            "HTTP_Obter_Item_Atual": sp_http("GET", get_uri),
            "Condicao_Item_Valido": condition(
                valid,
                valid_actions,
                {
                    "Ignorar_Item_Sem_Intencao_Nova": compose(
                        "Item ignorado: status ou identificadores não autorizam novo envio."
                    )
                },
                {"HTTP_Obter_Item_Atual": ["Succeeded"]},
            ),
        },
    }

    # Não existe status de erro: o catch consome a intenção (processado = envio)
    # e deixa data_envio_terceiro vazia, que é como o app reconhece a falha. Sem
    # consumir, qualquer alteração posterior no item reativaria o gatilho e
    # reenviaria o e-mail sem ninguém pedir.
    catch_get_uri = get_uri
    reread = "body('HTTP_Reler_Item_Apos_Erro')"
    failure_actions = {
        "Montar_Consumo_Intencao": compose(
            {"forms_envio_processado_id": "@string(triggerBody()?['forms_envio_id'])"}
        ),
        "HTTP_Consumir_Intencao_Com_Falha": sp_http(
            "POST",
            main_uri,
            body="@string(outputs('Montar_Consumo_Intencao'))",
            headers={
                "Accept": "application/json;odata=nometadata",
                "Content-Type": "application/json;odata=nometadata",
                "X-HTTP-Method": "MERGE",
                "IF-MATCH": "*",
            },
            run_after={"Montar_Consumo_Intencao": ["Succeeded"]},
        ),
        "Montar_Historico_Falha": compose(
            {
                "solicitacao_id": "@int(triggerBody()?['ID'])",
                "tipo_desdobramento": "Falha no envio ao terceiro",
                "status_anterior": f"@{reread}?['status']",
                "status_novo": f"@{reread}?['status']",
                "descricao": (
                    "@concat('O questionário não foi confirmado como enviado ao terceiro. "
                    "Corrija o e-mail, se necessário, e use Reenviar Forms. "
                    "Execução do Power Automate: ', string(workflow()?['run']?['name']), '.')"
                ),
                "visivel_solicitante": 1,
                "ativo": 1,
            },
            {"HTTP_Consumir_Intencao_Com_Falha": ["Succeeded", "Failed", "TimedOut"]},
        ),
        "HTTP_Registrar_Historico_Falha": sp_http(
            "POST",
            f"_api/web/lists/getbytitle('{HISTORY_LIST}')/items",
            body="@string(outputs('Montar_Historico_Falha'))",
            headers={
                "Accept": "application/json;odata=nometadata",
                "Content-Type": "application/json;odata=nometadata",
            },
            run_after={"Montar_Historico_Falha": ["Succeeded"]},
        ),
    }
    catch_actions = {
        "HTTP_Reler_Item_Apos_Erro": sp_http("GET", catch_get_uri),
        "Condicao_Intencao_Ainda_Atual": condition(
            (
                "@and("
                "equals(body('HTTP_Reler_Item_Apos_Erro')?['forms_envio_id'], "
                "triggerBody()?['forms_envio_id']),"
                "not(equals(body('HTTP_Reler_Item_Apos_Erro')?['forms_envio_processado_id'], "
                "triggerBody()?['forms_envio_id']))"
                ")"
            ),
            failure_actions,
            {"Ignorar_Erro_De_Intencao_Antiga": compose("A intenção de envio já mudou.")},
            {"HTTP_Reler_Item_Apos_Erro": ["Succeeded"]},
        ),
        # Skipped: se a releitura falhar, a condição é pulada e a execução ainda
        # precisa terminar como falha.
        "Encerrar_Com_Falha": terminate(
            "Failed",
            "DD01_ENVIO_FALHOU",
            "O questionário não foi confirmado como enviado. Consulte a ação que falhou.",
            {"Condicao_Intencao_Ainda_Atual": ["Succeeded", "Failed", "TimedOut", "Skipped"]},
        ),
    }
    catch_scope = {
        "runAfter": {"ESCOPO_Processar_Envio": ["Failed", "TimedOut"]},
        "type": "Scope",
        "actions": catch_actions,
    }
    return {
        "ESCOPO_Processar_Envio": process_scope,
        "ESCOPO_Tratar_Erro": catch_scope,
    }


def process_actions():
    response_id = "@triggerOutputs()?['body/resourceData/responseId']"
    code = f"@trim(string(body('Obter_detalhes_da_resposta')?['{TRACKING_QUESTION_ID}']))"
    # A solicitação vem do envio atual ou, na falta dele, de um envio anterior
    # registrado no histórico; a partir daqui todo o fluxo lê a variável.
    first_parent = "variables('varSolicitacao')"
    previous_link = "variables('varEnvioAnterior')"
    tracking = "outputs('Codigo_Acompanhamento')"

    actions = {
        "Obter_detalhes_da_resposta": conn_action(
            "shared_microsoftforms",
            "shared_microsoftforms",
            "GetFormResponseById",
            {"form_id": FORM_ID, "response_id": response_id},
        ),
        "Inicializar_Respostas": initialize_variable(
            "varRespostas",
            "array",
            [],
            {"Obter_detalhes_da_resposta": ["Succeeded"]},
        ),
        "Inicializar_Data_Resposta": initialize_variable(
            "varDataResposta",
            "string",
            "@utcNow()",
            {"Inicializar_Respostas": ["Succeeded"]},
        ),
        "Inicializar_Risco_Alto": initialize_variable(
            "varTerceiroAlto",
            "boolean",
            False,
            {"Inicializar_Data_Resposta": ["Succeeded"]},
        ),
        "Inicializar_Erro_Parametro": initialize_variable(
            "varErroParametro",
            "boolean",
            False,
            {"Inicializar_Risco_Alto": ["Succeeded"]},
        ),
        "Inicializar_Quantidade_Risco_Alto": initialize_variable(
            "varQuantidadeRiscoAlto",
            "integer",
            0,
            {"Inicializar_Erro_Parametro": ["Succeeded"]},
        ),
        "Inicializar_Solicitacao": initialize_variable(
            "varSolicitacao",
            "object",
            {},
            {"Inicializar_Quantidade_Risco_Alto": ["Succeeded"]},
        ),
        "Inicializar_Envio_Anterior": initialize_variable(
            "varEnvioAnterior",
            "boolean",
            False,
            {"Inicializar_Solicitacao": ["Succeeded"]},
        ),
        "Inicializar_Email_Envio_Anterior": initialize_variable(
            "varEmailEnvioAnterior",
            "string",
            "",
            {"Inicializar_Envio_Anterior": ["Succeeded"]},
        ),
        "Codigo_Acompanhamento": compose(
            code, {"Inicializar_Email_Envio_Anterior": ["Succeeded"]}
        ),
    }
    main_select = (
        "$select=ID,status,fluxo_classificacao,classificacao_risco,risco_final,gatilho_dd,"
        "forms_correlacao_id,forms_envio_id,forms_envio_processado_id,forms_ultima_resposta_id,"
        "email_terceiro"
    )
    lookup_prefix = (
        f"_api/web/lists/getbytitle('{MAIN_LIST}')/items?{main_select}"
        "&$filter=forms_envio_id eq '"
    )
    escaped_code = (
        f"replace({tracking}, {wdl_literal(chr(39))}, {wdl_literal(chr(39) * 2)})"
    )
    lookup_uri = (
        f"@concat({wdl_literal(lookup_prefix)}, {escaped_code}, {wdl_literal(chr(39))})"
    )
    actions["HTTP_Localizar_Solicitacao"] = sp_http(
        "GET", lookup_uri, run_after={"Codigo_Acompanhamento": ["Succeeded"]}
    )

    # Link de um envio anterior (2026-10-14): o app gera um código novo a cada
    # reenvio ou troca de e-mail, e o terceiro que respondia pelo e-mail antigo
    # perdia a resposta. O DD01 grava código e e-mail de cada envio no
    # histórico; o DD02 usa esse registro quando o código não é o atual.
    history_prefix = (
        f"_api/web/lists/getbytitle('{HISTORY_LIST}')/items?"
        "$select=ID,solicitacao_id,forms_envio_id,email_envio&$top=10"
        "&$filter=forms_envio_id eq '"
    )
    history_uri = (
        f"@concat({wdl_literal(history_prefix)}, {escaped_code}, {wdl_literal(chr(39))})"
    )
    previous_send = "first(body('HTTP_Localizar_Envio_Anterior')?['value'])"
    by_id_prefix = f"_api/web/lists/getbytitle('{MAIN_LIST}')/items?{main_select}&$filter=ID eq "
    by_id_uri = (
        f"@concat({wdl_literal(by_id_prefix)}, string(int({previous_send}?['solicitacao_id'])))"
    )
    previous_found_actions = {
        "HTTP_Obter_Solicitacao_Envio_Anterior": sp_http("GET", by_id_uri),
        "Definir_Solicitacao_Envio_Anterior": {
            "runAfter": {"HTTP_Obter_Solicitacao_Envio_Anterior": ["Succeeded"]},
            "type": "SetVariable",
            "inputs": {
                "name": "varSolicitacao",
                "value": (
                    "@if(equals(length(body('HTTP_Obter_Solicitacao_Envio_Anterior')?['value']), 1), "
                    "first(body('HTTP_Obter_Solicitacao_Envio_Anterior')?['value']), json('{}'))"
                ),
            },
        },
        "Definir_Envio_Anterior": {
            "runAfter": {"Definir_Solicitacao_Envio_Anterior": ["Succeeded"]},
            "type": "SetVariable",
            "inputs": {"name": "varEnvioAnterior", "value": True},
        },
        "Definir_Email_Envio_Anterior": {
            "runAfter": {"Definir_Envio_Anterior": ["Succeeded"]},
            "type": "SetVariable",
            "inputs": {
                "name": "varEmailEnvioAnterior",
                "value": f"@string(coalesce({previous_send}?['email_envio'], ''))",
            },
        },
    }
    search_previous_actions = {
        "HTTP_Localizar_Envio_Anterior": sp_http("GET", history_uri),
        "Condicao_Envio_Anterior_Encontrado": condition(
            "@greater(length(body('HTTP_Localizar_Envio_Anterior')?['value']), 0)",
            previous_found_actions,
            {"Envio_Anterior_Nao_Registrado": compose("Código ausente do histórico de envios.")},
            {"HTTP_Localizar_Envio_Anterior": ["Succeeded"]},
        ),
    }
    actions["Condicao_Envio_Atual"] = condition(
        "@equals(length(body('HTTP_Localizar_Solicitacao')?['value']), 1)",
        {
            "Definir_Solicitacao_Atual": {
                "runAfter": {},
                "type": "SetVariable",
                "inputs": {
                    "name": "varSolicitacao",
                    "value": "@first(body('HTTP_Localizar_Solicitacao')?['value'])",
                },
            }
        },
        {
            # Código duplicado em duas solicitações continua sendo recusado.
            "Condicao_Buscar_Envio_Anterior": condition(
                (
                    "@and(equals(length(body('HTTP_Localizar_Solicitacao')?['value']), 0), "
                    f"not(empty({tracking})))"
                ),
                search_previous_actions,
                {"Sem_Busca_Envio_Anterior": compose("Código vazio ou duplicado.")},
            )
        },
        {"HTTP_Localizar_Solicitacao": ["Succeeded"]},
    )

    # Valida todas as respostas antes de gravar a primeira linha.
    binary_checks = []
    for q in QUESTIONS:
        if q.get("text_answer") or q.get("conditional"):
            continue
        binary_checks.append(
            "contains(createArray('sim','não'), "
            f"toLower(trim(string(body('Obter_detalhes_da_resposta')?['{q['id']}']))))"
        )
    q_t1 = QUESTIONS[0]["id"]
    q_t12 = QUESTIONS[1]["id"]
    q_t5 = next(q["id"] for q in QUESTIONS if q.get("text_answer"))
    check_status = f"equals({first_parent}?['status'], {wdl_literal(STATUS_AGUARDANDO_TERCEIRO)})"
    check_fluxo = f"equals(toUpper(trim(string({first_parent}?['fluxo_classificacao']))), 'FLUXO III')"
    check_envio = f"equals(string({first_parent}?['forms_envio_id']), {tracking})"
    check_processado = f"equals(string({first_parent}?['forms_envio_processado_id']), {tracking})"
    # Link anterior: só enquanto não há resposta, sem envio novo em andamento
    # e se o e-mail que recebeu aquele link é o e-mail atual do terceiro (um
    # link mandado para o endereço errado não vale).
    check_sem_envio_pendente = (
        f"and(not(empty(string(coalesce({first_parent}?['forms_envio_id'], '')))), "
        f"equals(string(coalesce({first_parent}?['forms_envio_processado_id'], '')), "
        f"string(coalesce({first_parent}?['forms_envio_id'], ''))))"
    )
    check_sem_resposta = (
        f"empty(string(coalesce({first_parent}?['forms_ultima_resposta_id'], '')))"
    )
    check_email = (
        "and(not(empty(trim(variables('varEmailEnvioAnterior')))), "
        "equals(toLower(trim(variables('varEmailEnvioAnterior'))), "
        f"toLower(trim(string(coalesce({first_parent}?['email_terceiro'], ''))))))"
    )
    check_link = (
        f"or(and(not({previous_link}),{check_envio},{check_processado}),"
        f"and({previous_link},{check_sem_envio_pendente},{check_sem_resposta},{check_email}))"
    )
    check_answers = (
        "and("
        + ",".join(binary_checks)
        + ","
        f"or(not(equals(toLower(trim(string(body('Obter_detalhes_da_resposta')?['{q_t1}']))), 'sim')),"
        "contains(createArray('sim','não'), "
        f"toLower(trim(string(body('Obter_detalhes_da_resposta')?['{q_t12}']))))),"
        f"not(empty(trim(string(body('Obter_detalhes_da_resposta')?['{q_t5}']))))"
        ")"
    )
    validation = f"@and({check_status},{check_fluxo},{check_link},{check_answers})"

    # A rejeição continua a mesma; a mensagem diz qual regra barrou e com que
    # valor, para o Compliance decidir sem abrir o SharePoint às cegas.
    def stored(field: str) -> str:
        return f"string(coalesce({first_parent}?['{field}'], '(vazio)'))"

    invalid_reason = (
        "@concat("
        f"'Solicitação ID ', string({first_parent}?['ID']), ' recusou a resposta. ', "
        f"if({previous_link}, concat('Código ', {tracking}, ' é de um envio anterior; o atual é ', "
        f"{stored('forms_envio_id')}, '. '), ''), "
        f"if(not({check_status}), concat('Status atual = ', {stored('status')}, "
        f"' (esperado {STATUS_AGUARDANDO_TERCEIRO}). '), ''), "
        f"if(not({check_fluxo}), concat('Fluxo = ', {stored('fluxo_classificacao')}, "
        "' (esperado FLUXO III). '), ''), "
        f"if(and(not({previous_link}), not({check_processado})), concat('Envio ainda não processado pelo DD01 "
        f"(forms_envio_processado_id = ', {stored('forms_envio_processado_id')}, '). '), ''), "
        f"if(and({previous_link}, not({check_sem_envio_pendente})), "
        "'Há um envio novo em processamento pelo DD01. ', ''), "
        f"if(and({previous_link}, not({check_email})), concat('O link anterior foi enviado para ', "
        "if(empty(trim(variables('varEmailEnvioAnterior'))), '(e-mail não registrado)', "
        "variables('varEmailEnvioAnterior')), ' e o e-mail atual do terceiro é ', "
        f"{stored('email_terceiro')}, '. '), ''), "
        f"if(not({check_answers}), 'Resposta obrigatória vazia ou diferente de Sim/Não. ', ''), "
        f"if({check_sem_resposta}, '', "
        "concat('Já existe resposta processada (Response ID ', "
        f"{stored('forms_ultima_resposta_id')}, '); provável segundo envio do terceiro. ')), "
        f"'Forms Response ID: ', string({response_id[1:]}), '.')"
    )
    not_found_reason = (
        "@concat("
        f"if(empty({tracking}), "
        "'Código de acompanhamento vazio na resposta do Forms', "
        "concat('Não há exatamente uma solicitação com o Código de acompanhamento ', "
        f"{tracking}, ' (', "
        "string(length(body('HTTP_Localizar_Solicitacao')?['value'])), "
        "' encontrada(s)) e o código não está no histórico de envios. Causas comuns: "
        "envio feito antes do registro do código no histórico, código alterado no Forms "
        "ou solicitação excluída')), "
        f"'. Forms Response ID: ', string({response_id[1:]}), '.')"
    )

    valid_actions = build_valid_response_actions(first_parent, response_id)
    not_duplicate = condition(
        validation,
        valid_actions,
        {
            "Diagnostico_Resposta_Invalida": compose(invalid_reason),
            "Falha_Resposta_Invalida": terminate(
                "Failed",
                "DD02_RESPOSTA_INVALIDA",
                "@outputs('Diagnostico_Resposta_Invalida')",
                {"Diagnostico_Resposta_Invalida": ["Succeeded"]},
            ),
        },
    )
    duplicate_check = condition(
        (
            f"@equals(string({first_parent}?['forms_ultima_resposta_id']), "
            "string(triggerOutputs()?['body/resourceData/responseId']))"
        ),
        {
            "Ignorar_Resposta_Ja_Processada": compose(
                "Resposta já processada; execução encerrada sem duplicar linhas."
            )
        },
        {"Condicao_Resposta_Valida": not_duplicate},
    )
    found = condition(
        f"@not(empty({first_parent}))",
        {"Condicao_Resposta_Repetida": duplicate_check},
        {
            "Diagnostico_Correlacao": compose(not_found_reason),
            "Falha_Correlacao": terminate(
                "Failed",
                "DD02_CORRELACAO_INVALIDA",
                "@outputs('Diagnostico_Correlacao')",
                {"Diagnostico_Correlacao": ["Succeeded"]},
            ),
        },
        {"Condicao_Envio_Atual": ["Succeeded"]},
    )
    actions["Condicao_Correlacao_Encontrada"] = found
    return actions


def build_valid_response_actions(first_parent: str, response_id: str):
    result = {}
    previous = None
    for q in QUESTIONS:
        name = f"Adicionar_{q['action']}"
        if q.get("conditional"):
            branch_name = "Condicao_T01_Positiva"
            result[branch_name] = condition(
                (
                    "@equals(toLower(trim(string(body('Obter_detalhes_da_resposta')?"
                    f"['{QUESTIONS[0]['id']}']))), 'sim')"
                ),
                {name: append_question(q)},
                {"Ignorar_T01_2": compose("T1.2 não se aplica quando T1 = Não.")},
                {previous: ["Succeeded"]} if previous else None,
            )
            previous = branch_name
        else:
            result[name] = append_question(
                q, {previous: ["Succeeded"]} if previous else None
            )
            previous = name

    loop = build_response_loop(first_parent, response_id)
    loop["runAfter"] = {previous: ["Succeeded"]}
    result["Para_Cada_Resposta"] = loop

    # Aprovação automática depois da resposta (2026-09-16): risco calculado baixo ou
    # médio, sem gatilho crítico do solicitante e nenhuma resposta de risco alto.
    # Qualquer outro caso segue para a análise do Compliance.
    automatic = "outputs('Avaliar_Aprovacao_Automatica')"
    today_local = f"convertFromUtc(utcNow(), {wdl_literal(TIME_ZONE)}, 'yyyy-MM-dd')"
    parent_risk = f"{first_parent}?['classificacao_risco']"
    validity_end = f"addToTime({today_local}, {risk_years(parent_risk)}, 'Year')"
    automatic_rule = (
        "@and("
        "not(variables('varTerceiroAlto')),"
        f"not(equals(toLower(trim(string(coalesce({first_parent}?['gatilho_dd'], '')))), 'sim')),"
        "contains(createArray('baixo', 'médio', 'medio'), "
        f"toLower(trim(string(coalesce({first_parent}?['classificacao_risco'], '')))))"
        ")"
    )
    status_after_response = (
        f"@if({automatic}, {wdl_literal(STATUS_APROVADO)}, {wdl_literal(STATUS_PENDENTE_COMPLIANCE)})"
    )
    parent_body = {
        "terceiro_gatilho_risco": "@if(variables('varTerceiroAlto'), 'Sim', 'Não')",
        "classificacao_risco": (
            "@if(variables('varTerceiroAlto'), 'Alto', "
            f"{first_parent}?['classificacao_risco'])"
        ),
        "risco_final": (
            "@if(variables('varTerceiroAlto'), 'Alto (gatilho do terceiro)', "
            f"{first_parent}?['risco_final'])"
        ),
        "data_resposta_terceiro": "@variables('varDataResposta')",
        "forms_ultima_resposta_id": f"@string({response_id[1:]})",
        # O app só mostra as respostas do forms_envio_id atual: quando o terceiro
        # usa um link anterior, esse código passa a ser o da solicitação. Os dois
        # campos mudam juntos, então o DD01 não vê intenção de envio.
        "forms_envio_id": "@string(outputs('Codigo_Acompanhamento'))",
        "forms_envio_processado_id": "@string(outputs('Codigo_Acompanhamento'))",
        "status": status_after_response,
        "data_conclusao": f"@if({automatic}, utcNow(), null)",
        # Meio-dia UTC: a coluna é só data e não pode recuar um dia no fuso local.
        "data_vencimento": (
            f"@if({automatic}, concat(formatDateTime({validity_end}, 'yyyy-MM-dd'), 'T12:00:00Z'), null)"
        ),
    }
    consolidate_actions = {
        "Avaliar_Aprovacao_Automatica": compose(automatic_rule),
        "Montar_Atualizacao_Solicitacao": compose(
            parent_body, {"Avaliar_Aprovacao_Automatica": ["Succeeded"]}
        ),
    }
    parent_item_prefix = f"_api/web/lists/getbytitle('{MAIN_LIST}')/items("
    parent_uri = (
        f"@concat({wdl_literal(parent_item_prefix)}, "
        f"string({first_parent}?['ID']), {wdl_literal(')')})"
    )
    consolidate_actions["HTTP_Atualizar_Solicitacao"] = sp_http(
        "POST",
        parent_uri,
        body="@string(outputs('Montar_Atualizacao_Solicitacao'))",
        headers={
            "Accept": "application/json;odata=nometadata",
            "Content-Type": "application/json;odata=nometadata",
            "X-HTTP-Method": "MERGE",
            "IF-MATCH": "*",
        },
        run_after={"Montar_Atualizacao_Solicitacao": ["Succeeded"]},
    )
    consolidate_actions["Montar_Historico_Resposta"] = compose(
        {
            "solicitacao_id": f"@int({first_parent}?['ID'])",
            "tipo_desdobramento": "Resposta do terceiro",
            "status_anterior": f"@{first_parent}?['status']",
            "status_novo": status_after_response,
            "descricao": (
                "@concat('Resposta do terceiro processada. ', "
                "string(length(variables('varRespostas'))), ' resposta(s); ', "
                "string(variables('varQuantidadeRiscoAlto')), "
                "' classificação(ões) de risco alto. Forms Response ID: ', "
                "string(triggerOutputs()?['body/resourceData/responseId']), '.', "
                "if(variables('varEnvioAnterior'), concat(' Recebida pelo link de um envio anterior (código ', "
                "outputs('Codigo_Acompanhamento'), '), que passou a ser o código da solicitação.'), ''), "
                f"if({automatic}, "
                f"concat(' Aprovação automática: risco ', string({first_parent}?['classificacao_risco']), "
                "', sem gatilho crítico e sem resposta de risco alto do terceiro. Vigência até ', "
                f"formatDateTime({validity_end}, 'dd/MM/yyyy'), '.'), "
                "' Encaminhada para a análise do Compliance.'))"
            ),
            "visivel_solicitante": 1,
            "ativo": 1,
        },
        {"HTTP_Atualizar_Solicitacao": ["Succeeded"]},
    )
    consolidate_actions["HTTP_Registrar_Historico_Resposta"] = sp_http(
        "POST",
        f"_api/web/lists/getbytitle('{HISTORY_LIST}')/items",
        body="@string(outputs('Montar_Historico_Resposta'))",
        headers={
            "Accept": "application/json;odata=nometadata",
            "Content-Type": "application/json;odata=nometadata",
        },
        run_after={"Montar_Historico_Resposta": ["Succeeded"]},
    )
    consolidate_actions["Resposta_Processada"] = compose(
        f"@concat('Solicitação ', string({first_parent}?['ID']), "
        "' processada com ', string(length(variables('varRespostas'))), ' respostas.')",
        {
            "HTTP_Registrar_Historico_Resposta": [
                "Succeeded",
                "Failed",
                "TimedOut",
            ]
        },
    )
    result["Condicao_Parametros_Validos"] = condition(
        "@equals(variables('varErroParametro'), false)",
        consolidate_actions,
        {
            "Falha_Parametro_Ausente_Ou_Duplicado": terminate(
                "Failed",
                "DD02_PARAMETRO_INVALIDO",
                "Uma ou mais respostas não possuem exatamente um parâmetro v2 ativo.",
            )
        },
        {"Para_Cada_Resposta": ["Succeeded"]},
    )
    return result


def build_response_loop(first_parent: str, response_id: str):
    item = "items('Para_Cada_Resposta')"
    key = (
        f"@concat('{FORM_ID}|', string(triggerOutputs()?['body/resourceData/responseId']), "
        "'|', items('Para_Cada_Resposta')?['codigo_pergunta'])"
    )
    param_prefix = (
        f"_api/web/lists/getbytitle('{PARAM_LIST}')/items?"
        "$select=ID,classificacao,codigo_pergunta,codigo_opcao&$filter="
        "versao_questionario eq 2 and ativo eq 1 and codigo_pergunta eq '"
    )
    param_uri = (
        f"@concat({wdl_literal(param_prefix)}, "
        f"replace(items('Para_Cada_Resposta')?['codigo_pergunta'], {wdl_literal(chr(39))}, "
        f"{wdl_literal(chr(39) * 2)}), {wdl_literal(chr(39) + ' and codigo_opcao eq ' + chr(39))}, "
        f"replace(items('Para_Cada_Resposta')?['codigo_opcao'], {wdl_literal(chr(39))}, "
        f"{wdl_literal(chr(39) * 2)}), {wdl_literal(chr(39))})"
    )
    response_prefix = (
        f"_api/web/lists/getbytitle('{RESPONSE_LIST}')/items?"
        "$select=ID,forms_item_chave&$filter=forms_item_chave eq '"
    )
    response_uri = (
        f"@concat({wdl_literal(response_prefix)}, "
        f"replace(outputs('Montar_Chave_Item'), {wdl_literal(chr(39))}, "
        f"{wdl_literal(chr(39) * 2)}), {wdl_literal(chr(39))})"
    )
    create_uri = f"_api/web/lists/getbytitle('{RESPONSE_LIST}')/items"
    response_item_prefix = f"_api/web/lists/getbytitle('{RESPONSE_LIST}')/items("
    update_uri = (
        f"@concat({wdl_literal(response_item_prefix)}, "
        "string(first(body('HTTP_Consultar_Item_Resposta')?['value'])?['ID']), "
        f"{wdl_literal(')')})"
    )

    response_body = {
        "solicitacao_id": f"@int({first_parent}?['ID'])",
        "codigo_pergunta": f"@string({item}?['codigo_pergunta'])",
        "codigo_opcao": f"@string({item}?['codigo_opcao'])",
        "texto_pergunta": f"@string({item}?['texto_pergunta'])",
        "resposta": f"@string({item}?['resposta'])",
        "classificacao": (
            "@string(first(body('HTTP_Consultar_Parametro')?['value'])?['classificacao'])"
        ),
        "data_resposta": "@variables('varDataResposta')",
        "versao_questionario": 2,
        "ordem": f"@int({item}?['ordem'])",
        "forms_formulario_id": FORM_ID,
        "forms_resposta_id": f"@string({response_id[1:]})",
        "forms_envio_id": "@string(outputs('Codigo_Acompanhamento'))",
        "forms_item_chave": "@string(outputs('Montar_Chave_Item'))",
        "ativo": 1,
    }
    create = sp_http(
        "POST",
        create_uri,
        body="@string(outputs('Montar_Item_Resposta'))",
        headers={
            "Accept": "application/json;odata=nometadata",
            "Content-Type": "application/json;odata=nometadata",
        },
    )
    update = sp_http(
        "POST",
        update_uri,
        body="@string(outputs('Montar_Item_Resposta'))",
        headers={
            "Accept": "application/json;odata=nometadata",
            "Content-Type": "application/json;odata=nometadata",
            "X-HTTP-Method": "MERGE",
            "IF-MATCH": "*",
        },
    )
    upsert = condition(
        "@equals(length(body('HTTP_Consultar_Item_Resposta')?['value']), 0)",
        {"HTTP_Criar_Item_Resposta": create},
        {"HTTP_Atualizar_Item_Resposta": update},
        {"HTTP_Consultar_Item_Resposta": ["Succeeded"]},
    )
    high = condition(
        (
            "@equals(first(body('HTTP_Consultar_Parametro')?['value'])?['classificacao'], "
            "'Risco Alto')"
        ),
        {
            "Definir_Risco_Alto": {
                "runAfter": {},
                "type": "SetVariable",
                "inputs": {"name": "varTerceiroAlto", "value": True},
            },
            "Incrementar_Quantidade_Risco_Alto": {
                "runAfter": {"Definir_Risco_Alto": ["Succeeded"]},
                "type": "IncrementVariable",
                "inputs": {"name": "varQuantidadeRiscoAlto", "value": 1},
            },
        },
        {"Manter_Classificacao": compose("Classificação sem gatilho alto.")},
        {"Montar_Item_Resposta": ["Succeeded"]},
    )
    valid_param_actions = {
        "Montar_Chave_Item": compose(key),
        "HTTP_Consultar_Item_Resposta": sp_http(
            "GET", response_uri, run_after={"Montar_Chave_Item": ["Succeeded"]}
        ),
        "Montar_Item_Resposta": compose(
            response_body, {"HTTP_Consultar_Item_Resposta": ["Succeeded"]}
        ),
        "Condicao_Classificacao_Alta": high,
        "Condicao_Criar_Ou_Atualizar": upsert,
    }
    # O upsert só começa depois da avaliação da classificação.
    valid_param_actions["Condicao_Criar_Ou_Atualizar"]["runAfter"] = {
        "Condicao_Classificacao_Alta": ["Succeeded"]
    }
    validate_param = condition(
        "@equals(length(body('HTTP_Consultar_Parametro')?['value']), 1)",
        valid_param_actions,
        {
            "Registrar_Erro_Parametro": {
                "runAfter": {},
                "type": "SetVariable",
                "inputs": {"name": "varErroParametro", "value": True},
            }
        },
        {"HTTP_Consultar_Parametro": ["Succeeded"]},
    )
    return {
        "foreach": "@variables('varRespostas')",
        "actions": {
            "HTTP_Consultar_Parametro": sp_http("GET", param_uri),
            "Condicao_Parametro_Unico": validate_param,
        },
        "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
        "type": "Foreach",
    }


def risk_years(risk: str) -> str:
    """Anos de vigência pela classificação de risco: baixo 3, médio 2, demais 1.

    Risco alto ou ausente fica com 1 ano: na dúvida, a vigência mais curta.
    """
    value = f"toLower(trim(string(coalesce({risk}, ''))))"
    return (
        f"if(equals({value}, 'baixo'), 3, "
        f"if(or(equals({value}, 'médio'), equals({value}, 'medio')), 2, 1))"
    )


def main_item_uri(item: str) -> str:
    prefix = f"_api/web/lists/getbytitle('{MAIN_LIST}')/items("
    return f"@concat({wdl_literal(prefix)}, string({item}?['ID']), {wdl_literal(')')})"


def expiry_actions():
    main_items = f"_api/web/lists/getbytitle('{MAIN_LIST}')/items"
    with_validity = "(" + " or ".join(f"status eq '{s}'" for s in STATUS_COM_VIGENCIA) + ")"
    merge_headers = {
        "Accept": "application/json;odata=nometadata",
        "Content-Type": "application/json;odata=nometadata",
        "X-HTTP-Method": "MERGE",
        "IF-MATCH": "*",
    }
    post_headers = {
        "Accept": "application/json;odata=nometadata",
        "Content-Type": "application/json;odata=nometadata",
    }

    # 1. Decisões sem data de vencimento: registros anteriores à coluna ou
    #    qualquer caminho que não a tenha gravado.
    fill = "items('Para_Cada_Sem_Vencimento')"
    start = (
        f"convertFromUtc(coalesce({fill}?['data_decisao_compliance'], "
        f"{fill}?['data_conclusao'], {fill}?['Created']), "
        f"{wdl_literal(TIME_ZONE)}, 'yyyy-MM-dd')"
    )
    years = risk_years(f"{fill}?['classificacao_risco']")
    fill_scope = {
        "HTTP_Listar_Sem_Vencimento": sp_http(
            "GET",
            (
                f"{main_items}?$select=ID,status,classificacao_risco,"
                "data_decisao_compliance,data_conclusao,Created"
                f"&$filter={with_validity} and data_vencimento eq null&$top=5000"
            ),
        ),
        "Para_Cada_Sem_Vencimento": {
            "runAfter": {"HTTP_Listar_Sem_Vencimento": ["Succeeded"]},
            "type": "Foreach",
            "foreach": "@body('HTTP_Listar_Sem_Vencimento')?['value']",
            "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
            "actions": {
                # Meio-dia UTC: a coluna é só data e não pode recuar um dia no fuso local.
                "Montar_Vencimento": compose(
                    {
                        "data_vencimento": (
                            f"@concat(formatDateTime(addToTime({start}, {years}, 'Year'), "
                            "'yyyy-MM-dd'), 'T12:00:00Z')"
                        )
                    }
                ),
                "HTTP_Gravar_Vencimento": sp_http(
                    "POST",
                    main_item_uri(fill),
                    body="@string(outputs('Montar_Vencimento'))",
                    headers=merge_headers,
                    run_after={"Montar_Vencimento": ["Succeeded"]},
                ),
            },
        },
    }

    # 2. Vigência encerrada: vencimento anterior à data de hoje em Brasília.
    due = "items('Para_Cada_Vencido')"
    due_prefix = (
        f"{main_items}?$select=ID,status,classificacao_risco,data_vencimento"
        f"&$filter={with_validity} and data_vencimento lt datetime'"
    )
    due_suffix = "T00:00:00Z'&$top=5000"
    expire_scope = {
        "HTTP_Listar_Vencidos": sp_http(
            "GET",
            (
                f"@concat({wdl_literal(due_prefix)}, outputs('Hoje_Local'), "
                f"{wdl_literal(due_suffix)})"
            ),
        ),
        "Para_Cada_Vencido": {
            "runAfter": {"HTTP_Listar_Vencidos": ["Succeeded"]},
            "type": "Foreach",
            "foreach": "@body('HTTP_Listar_Vencidos')?['value']",
            "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
            "actions": {
                "Montar_Status_Vencido": compose({"status": STATUS_VENCIDO}),
                "HTTP_Marcar_Vencido": sp_http(
                    "POST",
                    main_item_uri(due),
                    body="@string(outputs('Montar_Status_Vencido'))",
                    headers=merge_headers,
                    run_after={"Montar_Status_Vencido": ["Succeeded"]},
                ),
                "Montar_Historico_Vencimento": compose(
                    {
                        "solicitacao_id": f"@int({due}?['ID'])",
                        "tipo_desdobramento": "Vencimento da vigência",
                        "status_anterior": f"@string({due}?['status'])",
                        "status_novo": STATUS_VENCIDO,
                        "descricao": (
                            "@concat('Vigência encerrada em ', "
                            f"convertFromUtc({due}?['data_vencimento'], "
                            f"{wdl_literal(TIME_ZONE)}, 'dd/MM/yyyy'), "
                            "' (classificação de risco: ', "
                            f"string(coalesce({due}?['classificacao_risco'], 'não informada')), "
                            "'). Para manter o relacionamento com o terceiro, "
                            "abra uma nova solicitação de due diligence.')"
                        ),
                        "visivel_solicitante": 1,
                        "ativo": 1,
                    },
                    {"HTTP_Marcar_Vencido": ["Succeeded"]},
                ),
                "HTTP_Registrar_Historico_Vencimento": sp_http(
                    "POST",
                    f"_api/web/lists/getbytitle('{HISTORY_LIST}')/items",
                    body="@string(outputs('Montar_Historico_Vencimento'))",
                    headers=post_headers,
                    run_after={"Montar_Historico_Vencimento": ["Succeeded"]},
                ),
            },
        },
    }

    scopes = ("ESCOPO_Preencher_Vencimento", "ESCOPO_Vencer_Vigencia")
    any_scope_failed = (
        "@or("
        + ", ".join(
            f"equals(actions('{scope}')?['status'], '{state}')"
            for scope in scopes
            for state in ("Failed", "TimedOut")
        )
        + ")"
    )
    every_outcome = ["Succeeded", "Failed", "Skipped", "TimedOut"]
    return {
        "Hoje_Local": compose(
            f"@convertFromUtc(utcNow(), {wdl_literal(TIME_ZONE)}, 'yyyy-MM-dd')"
        ),
        "ESCOPO_Preencher_Vencimento": {
            "runAfter": {"Hoje_Local": ["Succeeded"]},
            "type": "Scope",
            "actions": fill_scope,
        },
        # Roda mesmo que o preenchimento falhe: um item problemático não pode
        # impedir que os demais vençam.
        "ESCOPO_Vencer_Vigencia": {
            "runAfter": {"ESCOPO_Preencher_Vencimento": every_outcome},
            "type": "Scope",
            "actions": expire_scope,
        },
        "Condicao_Alguma_Etapa_Falhou": condition(
            any_scope_failed,
            {
                "Encerrar_Com_Falha": terminate(
                    "Failed",
                    "DD03_VIGENCIA_FALHOU",
                    "O preenchimento ou o vencimento de vigências falhou. Consulte a execução.",
                )
            },
            {"Execucao_Concluida": compose("Vigências preenchidas e vencimentos processados.")},
            {"ESCOPO_Vencer_Vigencia": every_outcome},
        ),
    }


# --------------------------------------------------------------------------
# DD04 — Gerar laudo. Sem conector premium: o Power Apps monta o HTML do
# laudo (a mesma lógica de string já usada nos outros previews da tela) e
# manda pronto pro fluxo; o fluxo só grava esse HTML como arquivo na
# biblioteca de laudos e devolve o link. Não precisa de nenhum conector além
# do SharePoint que DD01-03 já usam — gatilho e resposta são ações nativas.
#
# O formato do gatilho "Power Apps (V2)" e da ação "Responder..." abaixo não
# é inventado: veio de um fluxo esqueleto real, exportado do Studio deste
# ambiente (dd04GerarLaudo_20260914134244.zip), com duas entradas (Number
# "id", Text "html") e as duas saídas de resposta. Um detalhe não-óbvio que
# só esse esqueleto revelou: o Power Automate nomeia o campo internamente
# pelo TIPO da entrada, não pelo nome dado — "id" vira a chave "number" e
# "html" vira a chave "text" no schema (o nome escolhido fica só no "title",
# usado como rótulo). Por isso o restante das ações lê
# triggerBody()?['number'] / triggerBody()?['text'], não ?['id'] / ?['html'].
# --------------------------------------------------------------------------

def laudo_trigger() -> dict:
    return {
        "manual": {
            "type": "Request",
            "kind": "PowerAppV2",
            "inputs": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "number": {
                            "description": "Please enter a number",
                            "title": "id",
                            "type": "number",
                            "x-ms-content-hint": "NUMBER",
                            "x-ms-dynamically-added": True,
                        },
                        "text": {
                            "description": "Please enter your input",
                            "title": "html",
                            "type": "string",
                            "x-ms-content-hint": "TEXT",
                            "x-ms-dynamically-added": True,
                        },
                    },
                    "required": ["number", "text"],
                }
            },
        }
    }


def laudo_response(run_after: dict, *, laudo_url: str = "", erro: str = "") -> dict:
    return {
        "runAfter": run_after,
        "type": "Response",
        "kind": "PowerApp",
        "inputs": {
            "schema": {
                "type": "object",
                "properties": {
                    "saida_laudo_url": {
                        "title": "saida_laudo_url",
                        "type": "string",
                        "x-ms-content-hint": "TEXT",
                        "x-ms-dynamically-added": True,
                    },
                    "saida_erro": {
                        "title": "saida_erro",
                        "type": "string",
                        "x-ms-content-hint": "TEXT",
                        "x-ms-dynamically-added": True,
                    },
                },
                "additionalProperties": {},
            },
            "statusCode": 200,
            "body": {
                "saida_laudo_url": laudo_url,
                "saida_erro": erro,
            },
        },
    }


def laudo_status_uri() -> str:
    prefix = f"_api/web/lists/getbytitle('{MAIN_LIST}')/items("
    return (
        f"@concat({wdl_literal(prefix)}, string(triggerBody()?['number']), "
        f"{wdl_literal(')?$select=ID,status')})"
    )


def laudo_update_uri() -> str:
    prefix = f"_api/web/lists/getbytitle('{MAIN_LIST}')/items("
    return f"@concat({wdl_literal(prefix)}, string(triggerBody()?['number']), {wdl_literal(')')})"


def laudo_arquivo_uri() -> str:
    """Nome do arquivo é DD-000123.html; a biblioteca é referenciada por título,
    igual às demais listas do projeto — não depende do caminho relativo real.

    O título tem espaço ("Laudos Due Diligence"), diferente de todo o resto
    deste gerador (as outras listas são tb_algumaCoisa, sem espaço). Por isso
    aqui — só aqui — o espaço precisa ir como %20: a ação "Enviar uma
    solicitação HTTP ao SharePoint" não codifica a URI para você.
    """
    prefix = (
        "_api/web/lists/getbytitle('"
        f"{url_quote(LAUDO_LIBRARY)}"
        "')/RootFolder/Files/add(url='DD-"
    )
    suffix = ".html',overwrite=true)"
    return (
        f"@concat({wdl_literal(prefix)}, formatNumber(int(triggerBody()?['number']), '000000'), "
        f"{wdl_literal(suffix)})"
    )


def laudo_actions() -> dict:
    decision_check = "@or(" + ", ".join(
        f"equals(body('HTTP_Obter_Item_Laudo')?['status'], {wdl_literal(s)})"
        for s in STATUS_DECISOES_FINAIS
    ) + ")"

    merge_headers = {
        "Accept": "application/json;odata=nometadata",
        "Content-Type": "application/json;odata=nometadata",
        "X-HTTP-Method": "MERGE",
        "IF-MATCH": "*",
    }
    html_headers = {
        "Accept": "application/json;odata=nometadata",
        "Content-Type": "text/html;charset=utf-8",
    }

    return {
        "HTTP_Obter_Item_Laudo": sp_http("GET", laudo_status_uri()),
        "Condicao_Decisao_Final": condition(
            decision_check,
            {
                "HTTP_Criar_Arquivo_Html": sp_http(
                    "POST",
                    laudo_arquivo_uri(),
                    body="@triggerBody()?['text']",
                    headers=html_headers,
                ),
                "Montar_Atualizacao_Laudo": compose(
                    {
                        "laudo_url": (
                            "@concat('https://grupoccr.sharepoint.com', "
                            "body('HTTP_Criar_Arquivo_Html')?['ServerRelativeUrl'])"
                        )
                    },
                    {"HTTP_Criar_Arquivo_Html": ["Succeeded"]},
                ),
                "HTTP_Gravar_Laudo_Url": sp_http(
                    "POST",
                    laudo_update_uri(),
                    body="@string(outputs('Montar_Atualizacao_Laudo'))",
                    headers=merge_headers,
                    run_after={"Montar_Atualizacao_Laudo": ["Succeeded"]},
                ),
                "Responder_Com_Laudo": laudo_response(
                    {"HTTP_Gravar_Laudo_Url": ["Succeeded"]},
                    laudo_url="@{outputs('Montar_Atualizacao_Laudo')?['laudo_url']}",
                ),
            },
            {
                "Responder_Sem_Decisao": laudo_response(
                    {},
                    erro=(
                        "Laudo disponível somente após o parecer final do Compliance "
                        "(Aprovado, Aprovado com Ressalvas, Reprovado Parcialmente ou Reprovado)."
                    ),
                ),
            },
            {"HTTP_Obter_Item_Laudo": ["Succeeded"]},
        ),
    }


def configure_laudo():
    # Mesmo molde SharePoint-only do DD03: DD04 não precisa de nenhum
    # conector além do já mapeado nesse rascunho.
    draft = SEND_DRAFT if SEND_DRAFT.exists() else SEND_DRAFT_UTF8
    package = read_package(draft, "DD04")
    rekey_as_new_flow(package, "DD04", "DD04 Gerar Laudo")
    definition = package["definition"]["properties"]["definition"]
    definition["triggers"] = laudo_trigger()
    definition["actions"] = laudo_actions()
    write_package(package, LAUDO_READY, "DD04_GerarLaudo.definition.json")


# --------------------------------------------------------------------------
# DD05 — Notificar mudança de status (2026-09-17). O gatilho compara `status`
# com `status_notificado`, o último status já avisado, no mesmo molde de
# `forms_envio_processado_id` do DD01: pega a mudança venha de onde vier (app,
# DD02, DD03, parecer do Compliance ou visão em grade) e a gravação do
# marcador no fim não reativa o fluxo, porque os dois campos ficam iguais.
# --------------------------------------------------------------------------

# Risco, pontuação e gatilhos são do perfil Compliance no app: só o e-mail do
# Compliance usa estas chaves de Montar_Campos (e as colunas de origem).
NOTIFY_SENSITIVE = {
    "classificacao_risco": "classificacao_risco",
    "risco_final": "risco_final",
    "pontuacao": "pontuacao_total",
    "gatilho_dd": "gatilho_dd",
    "terceiro_risco_alto": "terceiro_gatilho_risco",
}


def notify_pending(item: str) -> str:
    """Status preenchido e diferente do último status avisado."""
    status = f"trim(string(coalesce({item}?['status'], '')))"
    marker = f"trim(string(coalesce({item}?['status_notificado'], '')))"
    return f"@and(not(empty({status})), not(equals({status}, {marker})))"


def html_text(value: str, empty: str = "-") -> str:
    """Texto de coluna pronto para o corpo HTML: escapa &, < e >, troca quebra
    de linha por <br> e usa `empty` quando vazio. Os dois ramos do if() aceitam
    valor nulo, porque a expressão não pode depender de qual ramo é avaliado."""
    text = f"trim(string(coalesce({value}, '')))"
    escaped = f"replace(replace(replace({text}, '&', '&amp;'), '<', '&lt;'), '>', '&gt;')"
    lines = (
        f"replace(replace({escaped}, decodeUriComponent('%0D%0A'), '<br>'), "
        "decodeUriComponent('%0A'), '<br>')"
    )
    return f"if(empty({text}), {wdl_literal(empty)}, {lines})"


def local_date(value: str, fmt: str = "dd/MM/yyyy", prefix: str = "", empty: str = "-") -> str:
    """Data no fuso de Brasília; com `prefix`, vira trecho de frase que some quando vazia."""
    date = (
        f"convertFromUtc(coalesce({value}, '2000-01-01T00:00:00Z'), "
        f"{wdl_literal(TIME_ZONE)}, {wdl_literal(fmt)})"
    )
    filled = f"concat({wdl_literal(prefix)}, {date})" if prefix else date
    return f"if(empty({value}), {wdl_literal(empty)}, {filled})"


def notify_email_html(intro: str, rows: list[tuple[str, str, bool]], closing: str, note: str) -> str:
    cells = "".join(
        '<tr><td style="padding:6px 10px;border:1px solid #E2E8F0;background:#F8FAFC;'
        f'width:38%;color:#475569">{label}</td>'
        '<td style="padding:6px 10px;border:1px solid #E2E8F0">'
        + (f'<strong style="color:#005864">{value}</strong>' if strong else value)
        + "</td></tr>"
        for label, value, strong in rows
    )
    return (
        '<div style="font-family:Segoe UI,Arial,sans-serif;font-size:14px;line-height:1.5;'
        'color:#0F172A;max-width:640px">'
        '<div style="background:#005864;color:#FFFFFF;padding:14px 20px;font-size:16px;'
        'font-weight:600">Due Diligence de Terceiros · ASUR Brasil</div>'
        '<div style="border:1px solid #E2E8F0;border-top:0;padding:20px">'
        f"{intro}"
        '<table role="presentation" cellpadding="0" cellspacing="0" '
        f'style="border-collapse:collapse;width:100%;font-size:13px">{cells}</table>'
        f'<p style="margin:16px 0 0">{closing}</p>'
        f'<p style="margin:20px 0 0;font-size:12px;color:#64748B">{note}</p>'
        "</div></div>"
    )


def notify_messages(show) -> dict:
    """Uma mensagem por status para o solicitante, sem risco nem pontuação."""
    laudo = "O laudo pode ser baixado no app, em Registros › Ações › Baixar Laudo."
    return {
        STATUS_AGUARDANDO_TERCEIRO: (
            f"O questionário de due diligence segue para o terceiro ({show('email_terceiro')}). "
            "A análise continua depois da resposta. Enquanto o terceiro não responder, você pode "
            "corrigir os dados da solicitação pelo botão Editar."
        ),
        # Neutro: órgão público com gatilho chega aqui sem questionário (2026-09-18).
        STATUS_PENDENTE_COMPLIANCE: (
            "A solicitação está com o Compliance para análise. Você receberá outro e-mail "
            "quando houver parecer."
        ),
        "Aprovado": f"A solicitação foi aprovada{show('vigencia_frase')}. {laudo}",
        "Aprovado com Ressalvas": (
            f"A solicitação foi aprovada com ressalvas{show('vigencia_frase')}"
            f"{show('reavaliacao_frase')}.<br><br><strong>Condicionantes:</strong>"
            f"<br>{show('condicionantes')}<br><br>{laudo}"
        ),
        "Reprovado Parcialmente": (
            f"A solicitação foi reprovada parcialmente{show('vigencia_frase')}. "
            "Consulte o parecer no laudo, em Registros › Ações › Baixar Laudo."
        ),
        "Reprovado": (
            "A solicitação foi reprovada. Consulte o parecer no laudo, em Registros › Ações › "
            "Baixar Laudo."
        ),
        "Cancelado": (
            "A solicitação foi cancelada pelo Compliance. O motivo está no histórico da "
            "solicitação, no app."
        ),
        STATUS_VENCIDO: (
            f"A vigência da aprovação terminou{show('vencimento_frase')}. Para manter o relacionamento "
            "com o terceiro, abra uma nova solicitação de due diligence."
        ),
    }


def without_retry_override(action: dict) -> dict:
    """Leitura e marcador são idempotentes: ficam com a repetição padrão."""
    action["inputs"].pop("retryPolicy", None)
    return action


def notify_actions():
    item = "body('HTTP_Obter_Solicitacao')"
    fields = "outputs('Montar_Campos')"

    def field(name: str) -> str:
        return f"{item}?['{name}']"

    def show(key: str) -> str:
        return "@{" + fields + "?['" + key + "']}"

    status_raw = f"trim(string(coalesce({field('status')}, '')))"
    author_name = f"{item}?['Author']?['Title']"
    author_email = f"{item}?['Author']?['EMail']"
    every_outcome = ["Succeeded", "Failed", "Skipped", "TimedOut"]

    main_item_prefix = f"_api/web/lists/getbytitle('{MAIN_LIST}')/items("
    select = (
        ")?$select=ID,status,status_notificado,razao_social,cnpj_cpf,aeroporto,"
        "area_solicitante,email_terceiro,classificacao_risco,risco_final,pontuacao_total,"
        "pontuacao_solicitante,gatilho_dd,terceiro_gatilho_risco,data_resposta_terceiro,"
        "data_vencimento,prazo_reavaliacao,condicionantes_compliance,Author/Title,Author/EMail"
        "&$expand=Author"
    )
    get_uri = (
        f"@concat({wdl_literal(main_item_prefix)}, string(triggerBody()?['ID']), "
        f"{wdl_literal(select)})"
    )

    campos = {
        "codigo": f"@concat('DD-', formatNumber(int({field('ID')}), '000000'))",
        "saudacao": (
            f"@if(empty(trim(string(coalesce({author_name}, '')))), 'Olá.', "
            f"concat('Olá, ', {html_text(author_name)}, '.'))"
        ),
        "introducao": (
            f"@if(empty(trim(string(coalesce({field('status_notificado')}, '')))), "
            "'foi registrada', 'mudou de status')"
        ),
        "status_anterior": "@" + html_text(field("status_notificado"), "Novo registro"),
        "status_novo": "@" + html_text(field("status")),
        "razao_social": "@" + html_text(field("razao_social")),
        "cnpj_cpf": "@" + html_text(field("cnpj_cpf")),
        "aeroporto": "@" + html_text(field("aeroporto")),
        "email_terceiro": "@" + html_text(field("email_terceiro")),
        "vigencia_frase": "@" + local_date(
            field("data_vencimento"), prefix=", com vigência até ", empty=""
        ),
        "vencimento_frase": "@" + local_date(field("data_vencimento"), prefix=" em ", empty=""),
        "reavaliacao_frase": "@" + local_date(
            field("prazo_reavaliacao"), prefix="; reavaliação em ", empty=""
        ),
        "condicionantes": "@" + html_text(
            field("condicionantes_compliance"), "Consulte o laudo no app."
        ),
        "area_solicitante": "@" + html_text(field("area_solicitante")),
        "solicitante": "@" + html_text(
            f"concat(coalesce({author_name}, ''), ' (', coalesce({author_email}, ''), ')')"
        ),
        "classificacao_risco": "@" + html_text(field("classificacao_risco")),
        "risco_final": "@" + html_text(field("risco_final")),
        "pontuacao": "@" + html_text(
            f"coalesce({field('pontuacao_total')}, {field('pontuacao_solicitante')})"
        ),
        "gatilho_dd": "@" + html_text(field("gatilho_dd")),
        "terceiro_risco_alto": "@" + html_text(field("terceiro_gatilho_risco")),
        "data_resposta": "@" + local_date(field("data_resposta_terceiro"), "dd/MM/yyyy HH:mm"),
    }
    assert set(NOTIFY_SENSITIVE) <= set(campos)

    messages = notify_messages(show)
    assert tuple(messages) == STATUS_TODOS

    requester_body = notify_email_html(
        (
            f'<p style="margin:0 0 12px">{show("saudacao")}</p>'
            f'<p style="margin:0 0 16px">A solicitação <strong>{show("codigo")}</strong> '
            f'{show("introducao")}.</p>'
        ),
        [
            ("Terceiro", show("razao_social"), False),
            ("CNPJ/CPF", show("cnpj_cpf"), False),
            ("Aeroporto", show("aeroporto"), False),
            ("Status anterior", show("status_anterior"), False),
            ("Novo status", show("status_novo"), True),
        ],
        "@{outputs('Montar_Mensagem_Solicitante')}",
        "Acompanhe pelo app Due Diligence, na tela Registros (chave Minhas solicitações). "
        "Mensagem automática; não é preciso responder.",
    )
    compliance_body = notify_email_html(
        (
            f'<p style="margin:0 0 16px">A solicitação <strong>{show("codigo")}</strong> está em '
            "<strong>Pendente Compliance</strong> e aguarda a análise.</p>"
        ),
        [
            ("Terceiro", show("razao_social"), False),
            ("CNPJ/CPF", show("cnpj_cpf"), False),
            ("Aeroporto", show("aeroporto"), False),
            ("Área solicitante", show("area_solicitante"), False),
            ("Solicitante", show("solicitante"), False),
            ("Classificação de risco", show("classificacao_risco"), True),
            ("Risco final", show("risco_final"), False),
            ("Pontuação", show("pontuacao"), False),
            ("Gatilho crítico do solicitante", show("gatilho_dd"), False),
            ("Resposta de risco alto do terceiro", show("terceiro_risco_alto"), False),
            ("Resposta do terceiro em", show("data_resposta"), False),
        ],
        "Para analisar, abra o app Due Diligence, localize a solicitação em Registros e use "
        "Ações › Analisar.",
        f"Mensagem automática para os analistas ativos da lista {COMPLIANCE_LIST}.",
    )
    subject_counterparty = "@{coalesce(" + field("razao_social") + ", '-')}"

    requester_email = conn_action(
        "shared_office365",
        "shared_office365",
        "SendEmailV2",
        {
            "emailMessage/To": f"@{author_email}",
            "emailMessage/Subject": (
                f"Due Diligence {show('codigo')} · {subject_counterparty} — "
                "@{" + field("status") + "}"
            ),
            "emailMessage/Body": requester_body,
            "emailMessage/Importance": "Normal",
        },
    )
    compliance_email = conn_action(
        "shared_office365",
        "shared_office365",
        "SendEmailV2",
        {
            "emailMessage/To": "@join(body('Selecionar_Emails_Compliance'), ';')",
            "emailMessage/Subject": (
                f"Due Diligence {show('codigo')} aguardando análise do Compliance · "
                f"{subject_counterparty}"
            ),
            "emailMessage/Body": compliance_body,
            "emailMessage/Importance": "Normal",
        },
    )

    compliance_actions = {
        "HTTP_Listar_Compliance": without_retry_override(
            sp_http(
                "GET",
                f"_api/web/lists/getbytitle('{COMPLIANCE_LIST}')/items"
                "?$select=email&$filter=ativo eq 1&$top=500",
            )
        ),
        "Selecionar_Emails_Compliance": {
            "runAfter": {"HTTP_Listar_Compliance": ["Succeeded"]},
            "type": "Select",
            "inputs": {
                "from": "@body('HTTP_Listar_Compliance')?['value']",
                "select": "@trim(string(item()?['email']))",
            },
        },
        "Condicao_Tem_Compliance_Ativo": condition(
            "@greater(length(body('Selecionar_Emails_Compliance')), 0)",
            {"Enviar_Email_Compliance": compliance_email},
            {
                "Marcar_Sem_Compliance": {
                    "runAfter": {},
                    "type": "SetVariable",
                    "inputs": {"name": "varSemCompliance", "value": True},
                }
            },
            {"Selecionar_Emails_Compliance": ["Succeeded"]},
        ),
    }

    # O marcador só é gravado se nenhum envio falhou: assim a execução com falha
    # pode ser reenviada e a próxima alteração do item tenta de novo. Skipped
    # também é falha, porque as duas condições sempre rodam no caminho normal.
    def sent(action: str) -> str:
        return (
            "not(contains(createArray('Failed', 'TimedOut', 'Skipped'), "
            f"actions('{action}')?['status']))"
        )

    marker_actions = {
        "Montar_Marcador": compose({"status_notificado": f"@{field('status')}"}),
        "HTTP_Gravar_Status_Notificado": without_retry_override(
            sp_http(
                "POST",
                main_item_uri("triggerBody()"),
                body="@string(outputs('Montar_Marcador'))",
                headers={
                    "Accept": "application/json;odata=nometadata",
                    "Content-Type": "application/json;odata=nometadata",
                    "X-HTTP-Method": "MERGE",
                    "IF-MATCH": "*",
                },
                run_after={"Montar_Marcador": ["Succeeded"]},
            )
        ),
        "Condicao_Sem_Compliance_Ativo": condition(
            "@variables('varSemCompliance')",
            {
                "Encerrar_Sem_Compliance_Ativo": terminate(
                    "Failed",
                    "DD05_SEM_COMPLIANCE_ATIVO",
                    "A solicitação chegou a Pendente Compliance, mas não há e-mail ativo em "
                    f"{COMPLIANCE_LIST}.",
                )
            },
            {"Notificacao_Concluida": compose("Avisos enviados e status marcado como avisado.")},
            {"HTTP_Gravar_Status_Notificado": ["Succeeded"]},
        ),
    }

    pending_actions = {
        "Montar_Campos": compose(campos),
        "Montar_Mensagens_Solicitante": compose(messages, {"Montar_Campos": ["Succeeded"]}),
        "Montar_Mensagem_Solicitante": compose(
            f"@coalesce(outputs('Montar_Mensagens_Solicitante')?[{status_raw}], "
            "'Consulte os detalhes da solicitação no app.')",
            {"Montar_Mensagens_Solicitante": ["Succeeded"]},
        ),
        "Condicao_Tem_Solicitante": condition(
            f"@not(empty(trim(string(coalesce({author_email}, '')))))",
            {"Enviar_Email_Solicitante": requester_email},
            {
                "Solicitante_Sem_Email": compose(
                    "O autor da solicitação não tem e-mail; o aviso ao solicitante não foi enviado."
                )
            },
            {"Montar_Mensagem_Solicitante": ["Succeeded"]},
        ),
        "Condicao_Notificar_Compliance": condition(
            f"@equals({status_raw}, {wdl_literal(STATUS_PENDENTE_COMPLIANCE)})",
            compliance_actions,
            {},
            {"Condicao_Tem_Solicitante": every_outcome},
        ),
        "Condicao_Envios_Concluidos": condition(
            f"@and({sent('Condicao_Tem_Solicitante')}, {sent('Condicao_Notificar_Compliance')})",
            marker_actions,
            {
                "Encerrar_Com_Falha_No_Envio": terminate(
                    "Failed",
                    "DD05_ENVIO_FALHOU",
                    "Um aviso não foi enviado; o status continua pendente de aviso. "
                    "Reenvie a execução depois de corrigir a causa.",
                )
            },
            {"Condicao_Notificar_Compliance": every_outcome},
        ),
    }

    return {
        "Inicializar_Sem_Compliance": initialize_variable("varSemCompliance", "boolean", False),
        # Relê o item: com a fila do gatilho, o status pode já ter sido avisado
        # por uma execução anterior. Sem a coluna status_notificado a leitura
        # falha e nenhum e-mail sai.
        "HTTP_Obter_Solicitacao": without_retry_override(
            sp_http("GET", get_uri, run_after={"Inicializar_Sem_Compliance": ["Succeeded"]})
        ),
        "Condicao_Status_Pendente_De_Aviso": condition(
            notify_pending(item),
            pending_actions,
            {"Ignorar_Status_Ja_Avisado": compose("O status atual já foi avisado; nada a enviar.")},
            {"HTTP_Obter_Solicitacao": ["Succeeded"]},
        ),
        # Item excluído logo depois da mudança não é falha. Qualquer outro erro
        # (por exemplo, a coluna status_notificado ainda não criada) é.
        "Condicao_Leitura_Falhou": condition(
            "@equals(outputs('HTTP_Obter_Solicitacao')?['statusCode'], 404)",
            {"Encerrar_Item_Excluido": terminate("Succeeded", "", "")},
            {
                "Encerrar_Falha_Na_Leitura": terminate(
                    "Failed",
                    "DD05_LEITURA_FALHOU",
                    "Não foi possível reler a solicitação. Confira se a coluna status_notificado "
                    "existe na tb_dueDiligence e se a conexão SharePoint está válida.",
                )
            },
            {"HTTP_Obter_Solicitacao": ["Failed", "TimedOut"]},
        ),
    }


def configure_notify():
    # Molde do DD01: mesmo gatilho SharePoint da tb_dueDiligence; o Outlook é
    # acrescentado como no DD01. Fluxo novo, importado com "Criar como novo".
    draft = SEND_DRAFT if SEND_DRAFT.exists() else SEND_DRAFT_UTF8
    package = read_package(draft, "DD05")
    rekey_as_new_flow(package, "DD05", NOTIFY_NAME)
    definition = package["definition"]["properties"]["definition"]
    trigger = definition["triggers"]["When_an_item_is_created_or_modified"]
    trigger["inputs"]["parameters"] = {"dataset": SITE_URL, "table": MAIN_LIST_ID}
    trigger["conditions"] = [{"expression": notify_pending("triggerBody()")}]
    trigger["runtimeConfiguration"] = {"concurrency": {"runs": 1}}
    definition["actions"] = notify_actions()
    add_connector(
        package,
        "shared_office365",
        "Office 365 Outlook",
        "https://static.powerapps.com/resource/connectorassets/office365/icon.png",
    )
    write_package(package, NOTIFY_READY, "DD05_NotificarStatus.definition.json")


def add_connector(package: dict, logical: str, display: str, icon: str):
    manifest = package["manifest"]
    flow_resource_id = next(
        key for key, value in manifest["resources"].items() if value["type"] == "Microsoft.Flow/flows"
    )
    api_resource_id = stable_uuid(f"{package['label']}:{logical}:api")
    conn_resource_id = stable_uuid(f"{package['label']}:{logical}:connection")
    api_full_id = f"/providers/Microsoft.PowerApps/apis/{logical}"

    manifest["resources"][api_resource_id] = {
        "id": api_full_id,
        "name": logical,
        "type": "Microsoft.PowerApps/apis",
        "suggestedCreationType": "Existing",
        "details": {"displayName": display, "iconUri": icon},
        "configurableBy": "System",
        "hierarchy": "Child",
        "dependsOn": [],
    }
    manifest["resources"][conn_resource_id] = {
        "type": "Microsoft.PowerApps/apis/connections",
        "suggestedCreationType": "Existing",
        "creationType": "Existing",
        "details": {
            "displayName": "processos.aeroservice@grupoccr.com.br",
            "iconUri": icon,
        },
        "configurableBy": "User",
        "hierarchy": "Child",
        "dependsOn": [api_resource_id],
    }
    deps = manifest["resources"][flow_resource_id].setdefault("dependsOn", [])
    for dep in (api_resource_id, conn_resource_id):
        if dep not in deps:
            deps.append(dep)
    package["apis_map"][logical] = api_resource_id
    package["connections_map"][logical] = conn_resource_id
    package["definition"]["properties"]["connectionReferences"][logical] = {
        "connectionName": f"{logical}-due-diligence",
        "source": "Embedded",
        "id": api_full_id,
        "tier": "NotSpecified",
        "apiName": logical.removeprefix("shared_"),
        "isProcessSimpleApiReferenceConversionAlreadyDone": False,
    }


def read_package(path: Path, label: str):
    with zipfile.ZipFile(path) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    definition_name = next(
        name for name in files if name.startswith("Microsoft.Flow/flows/") and name.endswith("/definition.json")
    )
    base = definition_name.rsplit("/", 1)[0]
    return {
        "label": label,
        "files": files,
        "definition_name": definition_name,
        "apis_name": f"{base}/apisMap.json",
        "connections_name": f"{base}/connectionsMap.json",
        "definition": json.loads(files[definition_name]),
        "apis_map": json.loads(files[f"{base}/apisMap.json"]),
        "connections_map": json.loads(files[f"{base}/connectionsMap.json"]),
        "manifest": json.loads(files["manifest.json"]),
    }


def write_package(package: dict, output: Path, source_name: str):
    files = copy.deepcopy(package["files"])
    encoded = lambda value: json.dumps(
        value, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    files[package["definition_name"]] = encoded(package["definition"])
    files[package["apis_name"]] = encoded(package["apis_map"])
    files[package["connections_name"]] = encoded(package["connections_map"])
    files["manifest.json"] = encoded(package["manifest"])
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)

    source_path = SOURCE_DIR / source_name
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(
        json.dumps(package["definition"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def configure_send():
    draft = SEND_DRAFT if SEND_DRAFT.exists() else SEND_DRAFT_UTF8
    package = read_package(draft, "DD01")
    definition = package["definition"]["properties"]["definition"]
    trigger = definition["triggers"]["When_an_item_is_created_or_modified"]
    trigger["inputs"]["parameters"] = {"dataset": SITE_URL, "table": MAIN_LIST_ID}
    trigger["conditions"] = [
        {
            "expression": (
                f"@and(equals(triggerBody()?['status'], {wdl_literal(STATUS_AGUARDANDO_TERCEIRO)}), "
                "not(empty(triggerBody()?['forms_envio_id'])), "
                "not(equals(triggerBody()?['forms_envio_id'], "
                "triggerBody()?['forms_envio_processado_id'])))"
            )
        }
    ]
    trigger["runtimeConfiguration"] = {"concurrency": {"runs": 1}}
    definition["actions"] = send_actions()
    add_connector(
        package,
        "shared_office365",
        "Office 365 Outlook",
        "https://static.powerapps.com/resource/connectorassets/office365/icon.png",
    )
    write_package(package, SEND_READY, "DD01_EnviarQuestionario.definition.json")


def configure_process():
    package = read_package(PROCESS_DRAFT, "DD02")
    definition = package["definition"]["properties"]["definition"]
    trigger = definition["triggers"]["When_a_new_response_is_submitted"]
    trigger["inputs"]["parameters"] = {"form_id": FORM_ID}
    trigger["runtimeConfiguration"] = {"concurrency": {"runs": 1}}
    definition["actions"] = process_actions()
    add_connector(
        package,
        "shared_sharepointonline",
        "SharePoint",
        "https://static.powerapps.com/resource/connectorassets/sharepointonline/icon.png",
    )
    write_package(package, PROCESS_READY, "DD02_ProcessarResposta.definition.json")


def rekey_as_new_flow(package: dict, label: str, display_name: str):
    """Transforma um pacote-molde em fluxo novo.

    Mantém as conexões já mapeadas, mas troca os identificadores e sugere
    "Criar como novo": com "Atualizar", o import sobrescreveria o fluxo escolhido.
    """
    manifest = package["manifest"]
    old_key = next(
        key for key, value in manifest["resources"].items() if value["type"] == "Microsoft.Flow/flows"
    )
    new_key = stable_uuid(f"{label}:pacote")
    resource = manifest["resources"].pop(old_key)
    resource["suggestedCreationType"] = "New"
    resource["details"]["displayName"] = display_name
    manifest["resources"][new_key] = resource
    manifest["details"]["displayName"] = display_name
    manifest["details"]["packageTelemetryId"] = stable_uuid(f"{label}:telemetria")

    old_prefix = f"Microsoft.Flow/flows/{old_key}/"
    new_prefix = f"Microsoft.Flow/flows/{new_key}/"
    package["files"] = {
        name.replace(old_prefix, new_prefix, 1): data for name, data in package["files"].items()
    }
    for key in ("definition_name", "apis_name", "connections_name"):
        package[key] = package[key].replace(old_prefix, new_prefix, 1)
    package["files"]["Microsoft.Flow/flows/manifest.json"] = json.dumps(
        {"packageSchemaVersion": "1.0", "flowAssets": {"assetPaths": [new_key]}},
        separators=(",", ":"),
    ).encode("utf-8")

    flow_id = stable_uuid(f"{label}:fluxo")
    package["definition"]["name"] = flow_id
    package["definition"]["id"] = f"/providers/Microsoft.Flow/flows/{flow_id}"
    package["definition"]["properties"]["displayName"] = display_name


def configure_expiry():
    # O rascunho do DD01 é só o molde: já traz a conexão SharePoint mapeada.
    draft = SEND_DRAFT if SEND_DRAFT.exists() else SEND_DRAFT_UTF8
    package = read_package(draft, "DD03")
    rekey_as_new_flow(package, "DD03", EXPIRY_NAME)
    definition = package["definition"]["properties"]["definition"]
    schedule = {
        "frequency": "Day",
        "interval": 1,
        "timeZone": TIME_ZONE,
        "schedule": {"hours": ["6"], "minutes": [0]},
    }
    definition["triggers"] = {
        "Recorrencia_Diaria": {
            "recurrence": schedule,
            "evaluatedRecurrence": copy.deepcopy(schedule),
            "type": "Recurrence",
            "runtimeConfiguration": {"concurrency": {"runs": 1}},
        }
    }
    definition["actions"] = expiry_actions()
    write_package(package, EXPIRY_READY, "DD03_VencerVigencia.definition.json")


def validate():
    for path in (SEND_READY, PROCESS_READY, EXPIRY_READY, LAUDO_READY, NOTIFY_READY):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            name = next(x for x in archive.namelist() if x.endswith("/definition.json"))
            data = json.loads(archive.read(name))
            raw = json.dumps(data, ensure_ascii=False)
            assert "PREENCHER_" not in raw
            assert data["properties"]["definition"]["actions"]
    for path, expected_trigger_types in (
        (EXPIRY_READY, ["Recurrence"]),
        (LAUDO_READY, ["Request"]),
        (NOTIFY_READY, ["OpenApiConnection"]),
    ):
        with zipfile.ZipFile(path) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            flows = [r for r in manifest["resources"].values() if r["type"] == "Microsoft.Flow/flows"]
            assert [r["suggestedCreationType"] for r in flows] == ["New"]
            name = next(x for x in archive.namelist() if x.endswith("/definition.json"))
            triggers = json.loads(archive.read(name))["properties"]["definition"]["triggers"]
            assert [t["type"] for t in triggers.values()] == expected_trigger_types
    assert len({q["id"] for q in QUESTIONS}) == 11
    assert len({q["code"] for q in QUESTIONS}) == 11

    # DD04: contrato mínimo — recebe o HTML pronto do app, grava como arquivo
    # e devolve o link; nenhuma peça deve depender de conector premium.
    with zipfile.ZipFile(LAUDO_READY) as archive:
        name = next(x for x in archive.namelist() if x.endswith("/definition.json"))
        laudo_definition = json.loads(archive.read(name))
    raw_laudo = json.dumps(laudo_definition, ensure_ascii=False)
    assert "wordonlinebusiness" not in raw_laudo.lower()
    assert '"kind": "PowerAppV2"' in raw_laudo or "'kind': 'PowerAppV2'" in raw_laudo or "PowerAppV2" in raw_laudo
    for token in (
        "triggerBody()?['text']",
        "triggerBody()?['number']",
        "laudo_url",
        "RootFolder/Files/add",
        url_quote(LAUDO_LIBRARY),
    ):
        assert token in raw_laudo, f"DD04 sem contrato obrigatório: {token!r}"
    assert LAUDO_LIBRARY not in laudo_arquivo_uri(), (
        "URI do arquivo do laudo tem o título da biblioteca sem codificar (espaço cru)"
    )
    for status in STATUS_DECISOES_FINAIS:
        assert wdl_literal(status) in raw_laudo, f"DD04 não contempla a decisão {status!r}"

    # DD05: aviso ao solicitante sem campos do perfil Compliance e marcador
    # gravado só depois dos envios.
    with zipfile.ZipFile(NOTIFY_READY) as archive:
        name = next(x for x in archive.namelist() if x.endswith("/definition.json"))
        notify_definition = json.loads(archive.read(name))
    notify = notify_definition["properties"]["definition"]
    pending = notify["actions"]["Condicao_Status_Pendente_De_Aviso"]["actions"]
    requester = pending["Condicao_Tem_Solicitante"]["actions"]["Enviar_Email_Solicitante"]
    requester_text = json.dumps(
        [requester["inputs"]["parameters"], pending["Montar_Mensagens_Solicitante"]["inputs"]],
        ensure_ascii=False,
    )
    for key, column in NOTIFY_SENSITIVE.items():
        for token in (f"['{key}']", f"['{column}']"):
            assert token not in requester_text, f"DD05: e-mail do solicitante expõe {token!r}"
    assert tuple(pending["Montar_Mensagens_Solicitante"]["inputs"]) == STATUS_TODOS
    marker = pending["Condicao_Envios_Concluidos"]["actions"]["Montar_Marcador"]["inputs"]
    assert set(marker) == {"status_notificado"}
    assert "status_notificado" in notify["triggers"]["When_an_item_is_created_or_modified"][
        "conditions"
    ][0]["expression"]


def main():
    configure_send()
    configure_process()
    configure_expiry()
    configure_laudo()
    configure_notify()
    validate()
    print(SEND_READY)
    print(PROCESS_READY)
    print(EXPIRY_READY)
    print(LAUDO_READY)
    print(NOTIFY_READY)


if __name__ == "__main__":
    main()
