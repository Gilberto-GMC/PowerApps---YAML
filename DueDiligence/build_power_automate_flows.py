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


BASE = Path(__file__).resolve().parent
SITE_URL = "https://grupoccr.sharepoint.com/sites/ComplianceAeroportos"
MAIN_LIST_ID = "ad57d68b-addf-466d-a86e-034035c412d6"
MAIN_LIST = "tb_dueDiligence"
PARAM_LIST = "tb_dueDiligenceParametros"
RESPONSE_LIST = "tb_dueDiligenceTerceiroRespostas"
HISTORY_LIST = "tb_dueDiligenceDesdobramentos"

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
SOURCE_DIR = BASE / "PowerAutomate"

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
        f"equals({current}?['status'], 'Aguardando envio ao terceiro'),"
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

    update_body = {
        "forms_formulario_id": FORM_ID,
        "forms_envio_processado_id": "@body('HTTP_Obter_Item_Atual')?['forms_envio_id']",
        "data_envio_terceiro": "@utcNow()",
        "status": "Aguardando terceiro",
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
                "status_novo": "Aguardando terceiro",
                "descricao": (
                    "@concat('Questionário enviado ao terceiro. Identificador do envio: ', "
                    "string(body('HTTP_Obter_Item_Atual')?['forms_envio_id']), '.')"
                ),
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

    catch_get_uri = get_uri
    catch_update = sp_http(
        "POST",
        main_uri,
        body='{"status":"Erro no envio ao terceiro"}',
        headers={
            "Accept": "application/json;odata=nometadata",
            "Content-Type": "application/json;odata=nometadata",
            "X-HTTP-Method": "MERGE",
            "IF-MATCH": "*",
        },
    )
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
            {"HTTP_Marcar_Erro_Envio": catch_update},
            {"Ignorar_Erro_De_Intencao_Antiga": compose("A intenção de envio já mudou.")},
            {"HTTP_Reler_Item_Apos_Erro": ["Succeeded"]},
        ),
        "Encerrar_Com_Falha": terminate(
            "Failed",
            "DD01_ENVIO_FALHOU",
            "O questionário não foi confirmado como enviado. Consulte a ação que falhou.",
            {"Condicao_Intencao_Ainda_Atual": ["Succeeded", "Failed", "TimedOut"]},
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
    first_parent = "first(body('HTTP_Localizar_Solicitacao')?['value'])"

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
        "Codigo_Acompanhamento": compose(
            code, {"Inicializar_Quantidade_Risco_Alto": ["Succeeded"]}
        ),
    }
    lookup_prefix = (
        f"_api/web/lists/getbytitle('{MAIN_LIST}')/items?"
        "$select=ID,status,fluxo_classificacao,classificacao_risco,risco_final,"
        "forms_correlacao_id,forms_envio_id,forms_envio_processado_id,forms_ultima_resposta_id"
        "&$filter=forms_envio_id eq '"
    )
    lookup_uri = (
        f"@concat({wdl_literal(lookup_prefix)}, "
        f"replace(outputs('Codigo_Acompanhamento'), {wdl_literal(chr(39))}, "
        f"{wdl_literal(chr(39) * 2)}), {wdl_literal(chr(39))})"
    )
    actions["HTTP_Localizar_Solicitacao"] = sp_http(
        "GET", lookup_uri, run_after={"Codigo_Acompanhamento": ["Succeeded"]}
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
    validation = (
        "@and("
        f"equals({first_parent}?['status'], 'Aguardando terceiro'),"
        f"equals(toUpper(trim(string({first_parent}?['fluxo_classificacao']))), 'FLUXO III'),"
        f"equals(string({first_parent}?['forms_envio_id']), outputs('Codigo_Acompanhamento')) ,"
        f"equals(string({first_parent}?['forms_envio_processado_id']), outputs('Codigo_Acompanhamento')) ,"
        + ",".join(binary_checks)
        + ","
        f"or(not(equals(toLower(trim(string(body('Obter_detalhes_da_resposta')?['{q_t1}']))), 'sim')),"
        "contains(createArray('sim','não'), "
        f"toLower(trim(string(body('Obter_detalhes_da_resposta')?['{q_t12}']))))),"
        f"not(empty(trim(string(body('Obter_detalhes_da_resposta')?['{q_t5}']))))"
        ")"
    )

    valid_actions = build_valid_response_actions(first_parent, response_id)
    not_duplicate = condition(
        validation,
        valid_actions,
        {
            "Falha_Resposta_Invalida": terminate(
                "Failed",
                "DD02_RESPOSTA_INVALIDA",
                (
                    "O código, o status, o fluxo ou uma das respostas não corresponde "
                    "à solicitação atualmente aguardada."
                ),
            )
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
        "@equals(length(body('HTTP_Localizar_Solicitacao')?['value']), 1)",
        {"Condicao_Resposta_Repetida": duplicate_check},
        {
            "Falha_Correlacao": terminate(
                "Failed",
                "DD02_CORRELACAO_INVALIDA",
                "Nenhuma solicitação única foi localizada pelo Código de acompanhamento.",
            )
        },
        {"HTTP_Localizar_Solicitacao": ["Succeeded"]},
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
        "status": "Pendente Compliance",
    }
    consolidate_actions = {
        "Montar_Atualizacao_Solicitacao": compose(parent_body),
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
            "status_novo": "Pendente Compliance",
            "descricao": (
                "@concat('Resposta do terceiro processada. ', "
                "string(length(variables('varRespostas'))), ' resposta(s); ', "
                "string(variables('varQuantidadeRiscoAlto')), "
                "' classificação(ões) de risco alto. Forms Response ID: ', "
                "string(triggerOutputs()?['body/resourceData/responseId']), '.')"
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
        "@concat('Solicitação ', string(first(body('HTTP_Localizar_Solicitacao')?['value'])?['ID']), "
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
                "@and(equals(triggerBody()?['status'], 'Aguardando envio ao terceiro'), "
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


def validate():
    for path in (SEND_READY, PROCESS_READY):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            name = next(x for x in archive.namelist() if x.endswith("/definition.json"))
            data = json.loads(archive.read(name))
            raw = json.dumps(data, ensure_ascii=False)
            assert "PREENCHER_" not in raw
            assert data["properties"]["definition"]["actions"]
    assert len({q["id"] for q in QUESTIONS}) == 11
    assert len({q["code"] for q in QUESTIONS}) == 11


def main():
    configure_send()
    configure_process()
    validate()
    print(SEND_READY)
    print(PROCESS_READY)


if __name__ == "__main__":
    main()
