#!/usr/bin/env python3
"""Gera DD01, DD02 (captura) e DD02P a partir dos exports ativos de 20/10.

Os ZIPs de origem são imutáveis. As duas primeiras saídas são para Update dos
fluxos existentes; DD02P é um fluxo novo. Nenhuma importação é feita aqui.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from build_power_automate_flows import (
    BASE, FORM_ID, HISTORY_LIST, MAIN_LIST, QUESTIONS, RESPONSE_LIST,
    SITE_URL, TRACKING_QUESTION_ID, compose, condition, read_package,
    rekey_as_new_flow, sp_http, terminate, wdl_literal, write_package,
)

SEND_SOURCE = BASE / "EnviarquestionárioDueDiligence_20261020221632.zip"
PROCESS_SOURCE = BASE / "ProcessarrespostaDueDiligence_20261020214134.zip"
SEND_OUTPUT = BASE / "DD01_EnviarQuestionario_RESILIENTE.zip"
CAPTURE_OUTPUT = BASE / "DD02_CapturarResposta_RESILIENTE.zip"
CAPTURE_NEW_OUTPUT = BASE / "DD02_CapturarResposta_CRIAR_NOVO.zip"
WORKER_OUTPUT = BASE / "DD02P_ProcessarInbox_RESILIENTE.zip"
MANUAL_OUTPUT = BASE / "DD02M_CapturarManual_RESILIENTE.zip"
MONITOR_OUTPUT = BASE / "DD06_MonitorarPendencias_RESILIENTE.zip"
SEND_LIST = "tb_dueDiligenceEnvios"
INBOX_LIST = "tb_dueDiligenceRespostasInbox"

# O hash identifica o export de origem; alterações futuras no ambiente exigem
# reexportar e revisar o diff antes de reconstruir um pacote Update.
SOURCE_SHA256 = {
    "send": "7589d60074010516a15a4b0bee266aeefa50c221b5e5c07d5b68e2205c01e21f",
    "process": "6c732d7b25802ca1aa026fb921ffe36c0f132a10e37d236511979d02354c6d3f",
}


def headers(*, merge: bool = False, etag: str = "*") -> dict[str, str]:
    result = {
        "Accept": "application/json;odata=nometadata",
        "Content-Type": "application/json;odata=nometadata",
    }
    if merge:
        result.update({"X-HTTP-Method": "MERGE", "IF-MATCH": etag})
    return result


def item_uri(list_name: str, id_expr: str) -> str:
    return f"@concat('_api/web/lists/getbytitle(''{list_name}'')/items(', string({id_expr}), ')')"


def main_item() -> str:
    return "first(body('HTTP_Listar_Pendentes')?['value'])"


def inbox_update_action(after: str, compose_name: str) -> dict:
    return sp_http(
        "POST", item_uri(INBOX_LIST, f"{main_item()}?['ID']"),
        body=f"@string(outputs('{compose_name}'))",
        headers=headers(merge=True), run_after={after: ["Succeeded"]},
    )


def replace_strings(value, old: str, new: str):
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, dict):
        return {key: replace_strings(item, old, new) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_strings(item, old, new) for item in value]
    return value


def source_package(path: Path, label: str) -> dict:
    expected = SOURCE_SHA256["send" if label == "DD01" else "process"]
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected and actual != expected:
        raise RuntimeError(f"Export {label} mudou ({actual}); revisar antes de gerar Update")
    return read_package(path, label)


def mark_package(package: dict, display_name: str) -> None:
    package["definition"]["properties"]["displayName"] = display_name
    package["manifest"]["details"]["displayName"] = display_name
    for resource in package["manifest"]["resources"].values():
        if resource.get("type") == "Microsoft.Flow/flows":
            resource["details"]["displayName"] = display_name


def write_resilient_package(package: dict, output: Path, source_name: str) -> None:
    package["definition"]["properties"]["flowFailureAlertSubscribed"] = True
    write_package(package, output, source_name)


def build_send() -> dict:
    package = source_package(SEND_SOURCE, "DD01")
    definition = package["definition"]["properties"]["definition"]
    actions = definition["actions"]["ESCOPO_Processar_Envio"]["actions"]["Condicao_Item_Valido"]["actions"]
    original_select = "forms_correlacao_id,email_terceiro,razao_social"
    extended_select = original_select + ",forms_destinatario_versao_id"
    get_current = definition["actions"]["ESCOPO_Processar_Envio"]["actions"]["HTTP_Obter_Item_Atual"]
    get_current["inputs"]["parameters"]["parameters/uri"] = (
        get_current["inputs"]["parameters"]["parameters/uri"].replace(original_select, extended_select)
    )
    code = "body('HTTP_Obter_Item_Atual')?['forms_envio_id']"
    mail = "body('HTTP_Obter_Item_Atual')?['email_terceiro']"
    actions["Montar_Registro_Envio"] = compose({
        "envio_id": f"@string({code})",
        "solicitacao_id": "@int(triggerBody()?['ID'])",
        "forms_formulario_id": FORM_ID,
        "email_envio": f"@string({mail})",
        "destinatario_versao_id": "@string(coalesce(body('HTTP_Obter_Item_Atual')?['forms_destinatario_versao_id'], ''))",
        "estado_envio": "Preparado",
        "criado_em": "@utcNow()",
        "dd01_run_id": "@string(workflow()?['run']?['name'])",
    }, {"Montar_Link_Questionario": ["Succeeded"]})
    actions["HTTP_Registrar_Envio_Preparado"] = sp_http(
        "POST", f"_api/web/lists/getbytitle('{SEND_LIST}')/items",
        body="@string(outputs('Montar_Registro_Envio'))",
        headers=headers(), run_after={"Montar_Registro_Envio": ["Succeeded"]},
    )
    actions["Enviar_Email_V2"]["runAfter"] = {"HTTP_Registrar_Envio_Preparado": ["Succeeded"]}
    actions["Montar_Envio_Aceito"] = compose({
        "estado_envio": "Aceito",
        "aceito_em": "@utcNow()",
    }, {"Enviar_Email_V2": ["Succeeded"]})
    actions["HTTP_Marcar_Envio_Aceito"] = sp_http(
        "POST", item_uri(SEND_LIST, "body('HTTP_Registrar_Envio_Preparado')?['ID']"),
        body="@string(outputs('Montar_Envio_Aceito'))",
        headers=headers(merge=True), run_after={"Montar_Envio_Aceito": ["Succeeded"]},
    )
    actions["Montar_Atualizacao_Envio"]["runAfter"] = {"HTTP_Marcar_Envio_Aceito": ["Succeeded"]}
    actions["Montar_Historico_Envio"]["inputs"]["forms_evento_chave"] = f"@concat('ENVIO|', string({code}))"
    actions["Envio_Concluido"]["runAfter"] = {"HTTP_Registrar_Historico_Envio": ["Succeeded"]}
    actions["Enviar_Email_V2"]["inputs"]["parameters"]["emailMessage/Body"] = (
        "<p>Olá,</p><p>A ASUR Brasil solicita o preenchimento do questionário de Due Diligence "
        "referente à empresa <strong>@{body('HTTP_Obter_Item_Atual')?['razao_social']}</strong>.</p>"
        "<p><a href=\"@{outputs('Montar_Link_Questionario')}\">Acessar questionário</a></p>"
        "<p>Código de acompanhamento: <strong>@{body('HTTP_Obter_Item_Atual')?['forms_envio_id']}</strong>.</p>"
        "<p>Confira se esse código aparece no formulário. Se estiver vazio ou diferente, informe o código acima.</p>"
        "<p>Se recebeu mais de um convite, use preferencialmente o link mais recente. "
        "Se já respondeu, não é necessário responder novamente.</p>"
        "<p>Mensagem enviada automaticamente. Em caso de dúvida, responda ao solicitante da contratação.</p>"
    )
    catch = definition["actions"]["ESCOPO_Tratar_Erro"]["actions"]
    failure = catch["Condicao_Intencao_Ainda_Atual"]["actions"]
    failure["Montar_Historico_Falha"]["inputs"]["descricao"] = (
        "@concat('Envio não confirmado integralmente. Verifique o registro de convites e a "
        "execução antes de reenviar: o e-mail pode ter sido aceito. Execução: ', "
        "string(workflow()?['run']?['name']), '.')"
    )
    catch["Encerrar_Com_Falha"]["inputs"]["runError"]["message"] = (
        "Envio não confirmado integralmente. Verifique o registro de convites antes de reenviar."
    )
    mark_package(package, "Enviar questionário Due Diligence")
    write_resilient_package(package, SEND_OUTPUT, "DD01_EnviarQuestionario_RESILIENTE.definition.json")
    return package


def build_capture() -> dict:
    package = source_package(PROCESS_SOURCE, "DD02")
    definition = package["definition"]["properties"]["definition"]
    trigger = definition["triggers"]["When_a_new_response_is_submitted"]
    trigger.pop("runtimeConfiguration", None)
    response_id = "triggerOutputs()?['body/resourceData/responseId']"
    key = f"@concat('{FORM_ID}|', string({response_id}))"
    query = (
        f"@concat('_api/web/lists/getbytitle(''{INBOX_LIST}'')/items?"
        "$select=ID,forms_chave&$filter=forms_chave eq ''', "
        "replace(outputs('Montar_Chave_Resposta'), '''', ''''''), '''')"
    )
    original_get = copy.deepcopy(definition["actions"]["Obter_detalhes_da_resposta"])
    actions = {
        "Obter_detalhes_da_resposta": original_get,
        "Montar_Chave_Resposta": compose(key, {"Obter_detalhes_da_resposta": ["Succeeded"]}),
        "HTTP_Consultar_Inbox": sp_http("GET", query, run_after={"Montar_Chave_Resposta": ["Succeeded"]}),
    }
    create = {
        "Montar_Entrada": compose({
            "forms_chave": "@string(outputs('Montar_Chave_Resposta'))",
            "forms_formulario_id": FORM_ID,
            "forms_resposta_id": f"@string({response_id})",
            "codigo_acompanhamento": f"@trim(string(body('Obter_detalhes_da_resposta')?['{TRACKING_QUESTION_ID}']))",
            "conteudo_json": "@string(body('Obter_detalhes_da_resposta'))",
            "capturado_em": "@utcNow()",
            "estado": "Pendente",
            "tentativas": 0,
        }),
        "HTTP_Criar_Entrada": sp_http(
            "POST", f"_api/web/lists/getbytitle('{INBOX_LIST}')/items",
            body="@string(outputs('Montar_Entrada'))", headers=headers(),
            run_after={"Montar_Entrada": ["Succeeded"]},
        ),
        "HTTP_Conferir_Inbox_Apos_Falha": sp_http(
            "GET", query, run_after={"HTTP_Criar_Entrada": ["Failed", "TimedOut"]},
        ),
        "Condicao_Entrada_Existe_Apos_Falha": condition(
            "@equals(length(body('HTTP_Conferir_Inbox_Apos_Falha')?['value']), 1)",
            {"Entrada_Ja_Capturada": compose("Response ID já consta na Inbox.")},
            {"Falha_Captura": terminate("Failed", "DD02_CAPTURA_FALHOU", "Resposta não confirmada na Inbox.")},
            {"HTTP_Conferir_Inbox_Apos_Falha": ["Succeeded"]},
        ),
    }
    existing = condition(
        "@equals(length(body('HTTP_Consultar_Inbox')?['value']), 1)",
        {"Resposta_Ja_Registrada": compose("Response ID já capturado.")},
        {"Falha_Chave_Ambigua": terminate("Failed", "DD02_CHAVE_DUPLICADA", "Mais de uma entrada para o Response ID.")},
    )
    actions["Condicao_Inbox_Vazia"] = condition(
        "@equals(length(body('HTTP_Consultar_Inbox')?['value']), 0)",
        create, {"Condicao_Registro_Existente": existing},
        {"HTTP_Consultar_Inbox": ["Succeeded"]},
    )
    definition["actions"] = actions
    mark_package(package, "Capturar resposta Due Diligence (DD02)")
    write_resilient_package(package, CAPTURE_OUTPUT, "DD02_CapturarResposta_RESILIENTE.definition.json")
    return package


def build_capture_new() -> dict:
    package = read_package(CAPTURE_OUTPUT, "DD02N")
    rekey_as_new_flow(package, "DD02N_Resiliente", "Capturar resposta Due Diligence (DD02N)")
    write_resilient_package(package, CAPTURE_NEW_OUTPUT, "DD02N_CapturarResposta_RESILIENTE.definition.json")
    return package


def build_manual_capture() -> dict:
    package = read_package(CAPTURE_OUTPUT, "DD02M")
    rekey_as_new_flow(package, "DD02M_Resiliente", "Capturar resposta manual Due Diligence (DD02M)")
    definition = package["definition"]["properties"]["definition"]
    definition["triggers"] = {
        "manual": {
            "type": "Request", "kind": "Button",
            "inputs": {"schema": {
                "type": "object",
                "properties": {"number": {
                    "description": "ID numérico da resposta no Microsoft Forms",
                    "title": "Response ID", "type": "number",
                    "x-ms-content-hint": "NUMBER", "x-ms-dynamically-added": True,
                }},
                "required": ["number"],
            }},
        }
    }
    definition["actions"] = replace_strings(
        definition["actions"],
        "triggerOutputs()?['body/resourceData/responseId']",
        "triggerBody()?['number']",
    )
    write_resilient_package(package, MANUAL_OUTPUT, "DD02M_CapturarManual_RESILIENTE.definition.json")
    return package


def answer_validation() -> str:
    checks = [
        "equals(variables('varSolicitacao')?['status'], 'Aguardando Terceiro')",
        "equals(toUpper(trim(string(variables('varSolicitacao')?['fluxo_classificacao']))), 'FLUXO III')",
        "equals(first(body('HTTP_Localizar_Envio')?['value'])?['estado_envio'], 'Aceito')",
        "empty(string(coalesce(variables('varSolicitacao')?['forms_ultima_resposta_id'], '')))",
        "equals(toLower(trim(string(first(body('HTTP_Localizar_Envio')?['value'])?['email_envio']))), "
        "toLower(trim(string(variables('varSolicitacao')?['email_terceiro']))))",
        "equals(string(coalesce(first(body('HTTP_Localizar_Envio')?['value'])?['destinatario_versao_id'], '')), "
        "string(coalesce(variables('varSolicitacao')?['forms_destinatario_versao_id'], '')))" ,
    ]
    for question in QUESTIONS:
        if question.get("text_answer") or question.get("conditional"):
            continue
        checks.append(
            "contains(createArray('sim','não'), toLower(trim(string("
            f"outputs('Obter_detalhes_da_resposta')?['{question['id']}']))))"
        )
    first, conditional = QUESTIONS[0]["id"], QUESTIONS[1]["id"]
    employees = next(q["id"] for q in QUESTIONS if q.get("text_answer"))
    checks.append(
        "or(not(equals(toLower(trim(string(outputs('Obter_detalhes_da_resposta')?"
        f"['{first}']))), 'sim')), contains(createArray('sim','não'), "
        "toLower(trim(string(outputs('Obter_detalhes_da_resposta')?"
        f"['{conditional}'])))))"
    )
    checks.append(f"not(empty(trim(string(outputs('Obter_detalhes_da_resposta')?['{employees}']))))")
    return "@and(" + ",".join(checks) + ")"


def update_inbox_after_success(previous: str, *, suffix: str = "") -> dict:
    compose_name = "Montar_Estado_Inbox" + suffix
    http_name = "HTTP_Marcar_Inbox_Processado" + suffix
    return {
        compose_name: compose({
            "estado": "Processado", "processado_em": "@utcNow()", "ultimo_erro": "",
        }, {previous: ["Succeeded"]}),
        http_name: inbox_update_action(compose_name, compose_name),
    }


def build_worker() -> dict:
    package = source_package(PROCESS_SOURCE, "DD02")
    rekey_as_new_flow(package, "DD02P_Resiliente", "Processar Inbox Due Diligence (DD02P)")
    definition = package["definition"]["properties"]["definition"]
    definition["triggers"] = {
        "Recorrencia_Processamento": {
            "recurrence": {"frequency": "Minute", "interval": 1},
            "type": "Recurrence", "runtimeConfiguration": {"concurrency": {"runs": 1}},
        }
    }
    source = replace_strings(
        copy.deepcopy(definition["actions"]),
        "triggerOutputs()?['body/resourceData/responseId']",
        f"{main_item()}?['forms_resposta_id']",
    )
    source = replace_strings(source, "body('Obter_detalhes_da_resposta')", "outputs('Obter_detalhes_da_resposta')")
    source = replace_strings(source, "HTTP_Localizar_Solicitacao", "HTTP_Localizar_Envio")
    original_get = source.pop("Obter_detalhes_da_resposta")
    assert original_get["type"] == "OpenApiConnection"
    variables = {}
    variable_names = [
        "Inicializar_Respostas", "Inicializar_Data_Resposta", "Inicializar_Risco_Alto",
        "Inicializar_Erro_Parametro", "Inicializar_Quantidade_Risco_Alto",
        "Inicializar_Solicitacao", "Inicializar_Envio_Anterior", "Inicializar_Email_Envio_Anterior",
    ]
    previous = "HTTP_Listar_Pendentes"
    for name in variable_names:
        action = source.pop(name)
        action["runAfter"] = {previous: ["Succeeded"]}
        if name == "Inicializar_Data_Resposta":
            action["inputs"]["variables"][0]["value"] = f"@coalesce({main_item()}?['capturado_em'], utcNow())"
        variables[name] = action
        previous = name
    variables["Inicializar_Envio"] = {
        "type": "InitializeVariable", "runAfter": {previous: ["Succeeded"]},
        "inputs": {"variables": [{"name": "varEnvio", "type": "object", "value": {}}]},
    }
    source["Obter_detalhes_da_resposta"] = compose(
        f"@json({main_item()}?['conteudo_json'])", {"HTTP_Marcar_Tentativa": ["Succeeded"]},
    )
    source["Codigo_Acompanhamento"]["runAfter"] = {"Obter_detalhes_da_resposta": ["Succeeded"]}
    source.pop("HTTP_Localizar_Solicitacao")
    source.pop("Condicao_Envio_Atual")
    query = (
        f"@concat('_api/web/lists/getbytitle(''{SEND_LIST}'')/items?"
        "$select=ID,solicitacao_id,envio_id,email_envio,estado_envio,forms_formulario_id,destinatario_versao_id"
        "&$filter=envio_id eq ''', replace(outputs('Codigo_Acompanhamento'), '''', ''''''), '''')"
    )
    source["HTTP_Localizar_Envio"] = sp_http(
        "GET", query, run_after={"Codigo_Acompanhamento": ["Succeeded"]},
    )
    lookup_parent = sp_http(
        "GET",
        f"@concat('_api/web/lists/getbytitle(''{MAIN_LIST}'')/items(', "
        "string(first(body('HTTP_Localizar_Envio')?['value'])?['solicitacao_id']), "
        "')?$select=ID,status,fluxo_classificacao,classificacao_risco,risco_final,gatilho_dd,"
        "forms_correlacao_id,forms_envio_id,forms_envio_processado_id,"
        "forms_ultima_resposta_id,email_terceiro,forms_destinatario_versao_id')",
    )
    found_actions = {
        "HTTP_Obter_Solicitacao": lookup_parent,
        "Definir_Solicitacao": {
            "type": "SetVariable", "runAfter": {"HTTP_Obter_Solicitacao": ["Succeeded"]},
            "inputs": {"name": "varSolicitacao", "value": "@body('HTTP_Obter_Solicitacao')"},
        },
        "Definir_Envio": {
            "type": "SetVariable", "runAfter": {"Definir_Solicitacao": ["Succeeded"]},
            "inputs": {"name": "varEnvio", "value": "@first(body('HTTP_Localizar_Envio')?['value'])"},
        },
        "Definir_Envio_Anterior": {
            "type": "SetVariable", "runAfter": {"Definir_Envio": ["Succeeded"]},
            "inputs": {"name": "varEnvioAnterior", "value": "@not(equals(string(variables('varSolicitacao')?['forms_envio_id']), outputs('Codigo_Acompanhamento')))"},
        },
        "Definir_Email_Envio_Anterior": {
            "type": "SetVariable", "runAfter": {"Definir_Envio_Anterior": ["Succeeded"]},
            "inputs": {"name": "varEmailEnvioAnterior", "value": "@string(variables('varEnvio')?['email_envio'])"},
        },
    }
    source["Condicao_Envio_Unico"] = condition(
        "@and(equals(length(body('HTTP_Localizar_Envio')?['value']), 1), "
        f"equals(first(body('HTTP_Localizar_Envio')?['value'])?['forms_formulario_id'], '{FORM_ID}'))",
        found_actions,
        {"Falha_Envio_Nao_Encontrado": terminate("Failed", "DD02_ENVIO_INVALIDO", "Código não tem um convite único registrado.")},
        {"HTTP_Localizar_Envio": ["Succeeded"]},
    )
    correlation = source["Condicao_Correlacao_Encontrada"]
    correlation["runAfter"] = {"Condicao_Envio_Unico": ["Succeeded"]}
    repeated = correlation["actions"]["Condicao_Resposta_Repetida"]
    repeated["actions"] = duplicate_response_actions()
    valid = repeated["else"]["actions"]["Condicao_Resposta_Valida"]
    valid["expression"] = {"and": [{"equals": [answer_validation(), True]}]}
    positive = valid["actions"]
    response_loop = positive.pop("Para_Cada_Resposta")
    item_actions = response_loop["actions"]["Condicao_Parametro_Unico"]["actions"]
    item_query = item_actions["HTTP_Consultar_Item_Resposta"]["inputs"]["parameters"]["parameters/uri"]
    item_actions["HTTP_Consultar_Item_Resposta"]["inputs"]["parameters"]["parameters/uri"] = (
        item_query.replace(
            "$select=ID,forms_item_chave",
            "$select=ID,forms_item_chave,resposta,codigo_opcao,classificacao,forms_resposta_id,forms_envio_id",
        )
    )
    upsert = item_actions["Condicao_Criar_Ou_Atualizar"]
    stored = "first(body('HTTP_Consultar_Item_Resposta')?['value'])"
    expected = "outputs('Montar_Item_Resposta')"
    same_row = (
        "@and(equals(length(body('HTTP_Consultar_Item_Resposta')?['value']), 1),"
        f"equals(string({stored}?['resposta']), string({expected}?['resposta'])),"
        f"equals(string({stored}?['codigo_opcao']), string({expected}?['codigo_opcao'])),"
        f"equals(string({stored}?['classificacao']), string({expected}?['classificacao'])),"
        f"equals(string({stored}?['forms_resposta_id']), string({expected}?['forms_resposta_id'])),"
        f"equals(string({stored}?['forms_envio_id']), string({expected}?['forms_envio_id'])))"
    )
    upsert["else"]["actions"] = {
        "Condicao_Item_Existente_Identico": condition(
            same_row,
            {"Item_Ja_Registrado": compose("Linha da resposta já existe e é idêntica.")},
            {"Registrar_Item_Divergente": {
                "type": "SetVariable", "runAfter": {},
                "inputs": {"name": "varErroParametro", "value": True},
            }},
        ),
    }
    # Uma primeira passagem valida todos os parâmetros antes da primeira escrita.
    precheck = {
        "type": "Foreach", "foreach": "@variables('varRespostas')",
        "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
        "runAfter": {"Adicionar_T09": ["Succeeded"]},
        "actions": {
            "HTTP_Consultar_Parametro_Pre": copy.deepcopy(response_loop["actions"]["HTTP_Consultar_Parametro"]),
            "Condicao_Parametro_Unico_Pre": condition(
                "@equals(length(body('HTTP_Consultar_Parametro_Pre')?['value']), 1)",
                {"Parametro_Encontrado_Pre": compose("Parâmetro validado.")},
                {"Registrar_Erro_Parametro_Pre": {
                    "type": "SetVariable", "runAfter": {},
                    "inputs": {"name": "varErroParametro", "value": True},
                }},
                {"HTTP_Consultar_Parametro_Pre": ["Succeeded"]},
            ),
        },
    }
    precheck["actions"]["HTTP_Consultar_Parametro_Pre"] = replace_strings(
        precheck["actions"]["HTTP_Consultar_Parametro_Pre"],
        "items('Para_Cada_Resposta')", "items('Para_Cada_Validacao')",
    )
    precheck["actions"]["HTTP_Consultar_Parametro_Pre"]["runAfter"] = {}
    positive["Para_Cada_Validacao"] = precheck
    old_final = positive.pop("Condicao_Parametros_Validos")
    response_loop["runAfter"] = {}
    old_final["runAfter"] = {"Para_Cada_Resposta": ["Succeeded"]}
    old_final["else"]["actions"]["Falha_Parametro_Ausente_Ou_Duplicado"]["inputs"]["runError"]["message"] = (
        "Parâmetro ausente/duplicado ou resposta previamente gravada divergente; revisão necessária."
    )
    positive["Condicao_Prevalidacao_Valida"] = condition(
        "@equals(variables('varErroParametro'), false)",
        {"Para_Cada_Resposta": response_loop, "Condicao_Parametros_Validos": old_final},
        {"Falha_Prevalidacao_Parametro": terminate("Failed", "DD02_PARAMETRO_INVALIDO", "Parâmetro ausente ou duplicado; nenhuma resposta filha foi gravada.")},
        {"Para_Cada_Validacao": ["Succeeded"]},
    )
    # O campo de último convite fica intacto; a resposta aceita aponta ao
    # convite que de fato foi usado.
    consolidate = old_final["actions"]
    parent = consolidate["Montar_Atualizacao_Solicitacao"]["inputs"]
    parent.pop("forms_envio_id", None)
    parent.pop("forms_envio_processado_id", None)
    parent["forms_resposta_envio_id"] = "@string(outputs('Codigo_Acompanhamento'))"
    history = consolidate["Montar_Historico_Resposta"]["inputs"]
    history["forms_evento_chave"] = (
        f"@concat('RESPOSTA|{FORM_ID}|', string({main_item()}?['forms_resposta_id']))"
    )
    # Releitura com metadados fornece ETag para recusar sobrescrita de
    # cancelamento, reenvio ou processamento concorrente.
    parent_uri = item_uri(MAIN_LIST, "variables('varSolicitacao')?['ID']")
    reread = sp_http(
        "GET", parent_uri,
        headers={"Accept": "application/json;odata=verbose"},
        run_after={"Montar_Atualizacao_Solicitacao": ["Succeeded"]},
    )
    consolidate["HTTP_Reler_Solicitacao"] = reread
    update = consolidate.pop("HTTP_Atualizar_Solicitacao")
    update["runAfter"] = {}
    update["inputs"]["parameters"]["parameters/headers"]["IF-MATCH"] = (
        "@body('HTTP_Reler_Solicitacao')?['d']?['__metadata']?['etag']"
    )
    history_compose = consolidate.pop("Montar_Historico_Resposta")
    history_post = consolidate.pop("HTTP_Registrar_Historico_Resposta")
    done = consolidate.pop("Resposta_Processada")
    done["runAfter"] = {"HTTP_Marcar_Inbox_Processado": ["Succeeded"]}
    success = update_inbox_after_success("HTTP_Registrar_Historico_Resposta")
    safe_update = {
        "HTTP_Atualizar_Solicitacao": update,
        "Montar_Historico_Resposta": history_compose,
        "HTTP_Registrar_Historico_Resposta": history_post,
        **success,
        "Resposta_Processada": done,
    }
    reread_body = "body('HTTP_Reler_Solicitacao')?['d']"
    safe = (
        "@and("
        f"equals({reread_body}?['status'], 'Aguardando Terceiro'),"
        f"equals(toUpper(trim(string({reread_body}?['fluxo_classificacao']))), 'FLUXO III'),"
        f"empty(string(coalesce({reread_body}?['forms_ultima_resposta_id'], ''))),"
        f"equals(toLower(trim(string({reread_body}?['email_terceiro']))), "
        "toLower(trim(variables('varEmailEnvioAnterior')))),"
        f"equals(string({reread_body}?['forms_correlacao_id']), string(variables('varSolicitacao')?['forms_correlacao_id'])),"
        f"equals(string({reread_body}?['classificacao_risco']), string(variables('varSolicitacao')?['classificacao_risco'])),"
        f"equals(string({reread_body}?['risco_final']), string(variables('varSolicitacao')?['risco_final'])),"
        f"equals(string({reread_body}?['gatilho_dd']), string(variables('varSolicitacao')?['gatilho_dd'])),"
        f"equals(string(coalesce({reread_body}?['forms_destinatario_versao_id'], '')), "
        "string(coalesce(variables('varSolicitacao')?['forms_destinatario_versao_id'], ''))),"
        f"not(empty({reread_body}?['__metadata']?['etag']))"
        ")"
    )
    consolidate["Condicao_Consolidacao_Segura"] = condition(
        safe, safe_update,
        {"Falha_Estado_Alterado": terminate("Failed", "DD02_CONFLITO_ESTADO", "Solicitação mudou durante o processamento; revisar antes de repetir.")},
        {"HTTP_Reler_Solicitacao": ["Succeeded"]},
    )
    valid["else"]["actions"]["Diagnostico_Resposta_Invalida"]["inputs"] = (
        "@concat('Solicitação ID ', string(variables('varSolicitacao')?['ID']), "
        "' recusou o Forms Response ID ', string(" + main_item() + "?['forms_resposta_id']), "
        "'. Verifique status, FLUXO III, estado e destinatário do convite, "
        "resposta já aceita e perguntas obrigatórias.')"
    )
    correlation["else"]["actions"]["Diagnostico_Correlacao"]["inputs"] = (
        "@concat('Código sem convite único na lista de envios: ', "
        "outputs('Codigo_Acompanhamento'), '. Forms Response ID: ', "
        f"string({main_item()}?['forms_resposta_id']), '.')"
    )
    # A ocorrência é escolhida depois de incrementar tentativas. Cinco falhas
    # deixam a linha em Revisao; uma execução bem-sucedida marca Processado.
    pending_uri = (
        f"_api/web/lists/getbytitle('{INBOX_LIST}')/items?"
        "$select=ID,forms_chave,forms_resposta_id,conteudo_json,capturado_em,tentativas,codigo_acompanhamento"
        "&$filter=estado eq 'Pendente' and tentativas lt 5&$orderby=ID asc&$top=1"
    )
    top = {
        "HTTP_Listar_Pendentes": sp_http("GET", pending_uri),
        **variables,
    }
    yes = {
        "Montar_Tentativa": compose({
            "tentativas": f"@add(int(coalesce({main_item()}?['tentativas'], 0)), 1)",
            "estado": f"@if(greaterOrEquals(add(int(coalesce({main_item()}?['tentativas'], 0)), 1), 5), 'Revisao', 'Pendente')",
            "ultimo_erro": "@concat('Em processamento. Execução: ', string(workflow()?['run']?['name']))",
        }),
        "HTTP_Marcar_Tentativa": sp_http(
            "POST", item_uri(INBOX_LIST, f"{main_item()}?['ID']"),
            body="@string(outputs('Montar_Tentativa'))", headers=headers(merge=True),
            run_after={"Montar_Tentativa": ["Succeeded"]},
        ),
        **source,
    }
    top["Condicao_Tem_Pendente"] = condition(
        "@greater(length(body('HTTP_Listar_Pendentes')?['value']), 0)",
        yes, {"Nenhuma_Pendencia": compose("Inbox sem resposta pendente.")},
        {"Inicializar_Envio": ["Succeeded"]},
    )
    definition["actions"] = top
    write_resilient_package(package, WORKER_OUTPUT, "DD02P_ProcessarInbox_RESILIENTE.definition.json")
    return package


def duplicate_response_actions() -> dict:
    event_key = f"@concat('RESPOSTA|{FORM_ID}|', string({main_item()}?['forms_resposta_id']))"
    query = (
        f"@concat('_api/web/lists/getbytitle(''{HISTORY_LIST}'')/items?"
        "$select=ID,forms_evento_chave&$filter=forms_evento_chave eq ''', "
        "replace(outputs('Chave_Evento_Repetido'), '''', ''''''), '''')"
    )
    return {
        "Chave_Evento_Repetido": compose(event_key),
        "HTTP_Consultar_Evento_Repetido": sp_http(
            "GET", query, run_after={"Chave_Evento_Repetido": ["Succeeded"]},
        ),
        "Condicao_Evento_Repetido_Existe": condition(
            "@equals(length(body('HTTP_Consultar_Evento_Repetido')?['value']), 0)",
            {
                "Montar_Evento_Reparado": compose({
                    "solicitacao_id": "@int(variables('varSolicitacao')?['ID'])",
                    "tipo_desdobramento": "Resposta do terceiro",
                    "status_anterior": "@variables('varSolicitacao')?['status']",
                    "status_novo": "@variables('varSolicitacao')?['status']",
                    "descricao": f"@concat('Registro de auditoria reparado para Forms Response ID: ', string({main_item()}?['forms_resposta_id']), '.')",
                    "forms_evento_chave": "@outputs('Chave_Evento_Repetido')",
                    "visivel_solicitante": 1, "ativo": 1,
                }),
                "HTTP_Registrar_Evento_Reparado": sp_http(
                    "POST", f"_api/web/lists/getbytitle('{HISTORY_LIST}')/items",
                    body="@string(outputs('Montar_Evento_Reparado'))", headers=headers(),
                    run_after={"Montar_Evento_Reparado": ["Succeeded"]},
                ),
            },
            {"Evento_Ja_Existe": compose("Auditoria já registrada.")},
            {"HTTP_Consultar_Evento_Repetido": ["Succeeded"]},
        ),
        **update_inbox_after_success("Condicao_Evento_Repetido_Existe", suffix="_Duplicado"),
    }


def build_monitor() -> dict:
    package = source_package(SEND_SOURCE, "DD01")
    rekey_as_new_flow(package, "DD06_Resiliente", "Monitorar pendências Due Diligence (DD06)")
    definition = package["definition"]["properties"]["definition"]
    definition["triggers"] = {
        "Recorrencia_Monitoramento": {
            "recurrence": {"frequency": "Hour", "interval": 1},
            "type": "Recurrence", "runtimeConfiguration": {"concurrency": {"runs": 1}},
        }
    }
    definition["actions"] = {
        "HTTP_Buscar_Revisao": sp_http(
            "GET",
            f"_api/web/lists/getbytitle('{INBOX_LIST}')/items?"
            "$select=ID,estado,forms_resposta_id&$top=1&$filter=estado eq 'Revisao'",
        ),
        "HTTP_Buscar_Pendente_Antiga": sp_http(
            "GET",
            f"_api/web/lists/getbytitle('{INBOX_LIST}')/items?"
            "$select=ID,estado,capturado_em&$top=1&$orderby=capturado_em asc&$filter=estado eq 'Pendente'",
            run_after={"HTTP_Buscar_Revisao": ["Succeeded"]},
        ),
        "HTTP_Buscar_Convite_Preparado": sp_http(
            "GET",
            f"_api/web/lists/getbytitle('{SEND_LIST}')/items?"
            "$select=ID,estado_envio,criado_em&$top=1&$orderby=ID asc&$filter=estado_envio eq 'Preparado'",
            run_after={"HTTP_Buscar_Pendente_Antiga": ["Succeeded"]},
        ),
        "HTTP_Buscar_Solicitacao_Sem_Envio": sp_http(
            "GET",
            f"_api/web/lists/getbytitle('{MAIN_LIST}')/items?"
            "$select=ID,status,forms_envio_id,forms_envio_processado_id,data_envio_terceiro,Modified"
            "&$top=1&$orderby=Modified asc"
            "&$filter=status eq 'Aguardando Terceiro' and forms_envio_id ne null and data_envio_terceiro eq null",
            run_after={"HTTP_Buscar_Convite_Preparado": ["Succeeded"]},
        ),
    }
    pending = "first(body('HTTP_Buscar_Pendente_Antiga')?['value'])"
    prepared = "first(body('HTTP_Buscar_Convite_Preparado')?['value'])"
    no_send = "first(body('HTTP_Buscar_Solicitacao_Sem_Envio')?['value'])"
    alert = (
        "@or("
        "greater(length(body('HTTP_Buscar_Revisao')?['value']), 0),"
        "and(greater(length(body('HTTP_Buscar_Pendente_Antiga')?['value']), 0),"
        f"less(ticks(coalesce({pending}?['capturado_em'], utcNow())), "
        "ticks(addMinutes(utcNow(), -15)))),"
        "and(greater(length(body('HTTP_Buscar_Convite_Preparado')?['value']), 0),"
        f"less(ticks(coalesce({prepared}?['criado_em'], utcNow())), "
        "ticks(addMinutes(utcNow(), -15)))),"
        "and(greater(length(body('HTTP_Buscar_Solicitacao_Sem_Envio')?['value']), 0),"
        f"less(ticks(coalesce({no_send}?['Modified'], utcNow())), "
        "ticks(addMinutes(utcNow(), -15)))))"
    )
    definition["actions"]["Condicao_Pendencias"] = condition(
        alert,
        {"Falha_Pendencias": terminate(
            "Failed", "DD06_PENDENCIAS",
            "Há resposta em revisão, resposta pendente, convite preparado ou solicitação sem envio há mais de 15 minutos. Verifique Inbox, Envios, tb_dueDiligence e DD01/DD02P.",
        )},
        {"Sem_Pendencias": compose("Inbox e convites sem atraso acima do limite.")},
        {"HTTP_Buscar_Solicitacao_Sem_Envio": ["Succeeded"]},
    )
    write_resilient_package(package, MONITOR_OUTPUT, "DD06_MonitorarPendencias_RESILIENTE.definition.json")
    return package


def main() -> None:
    for path in (SEND_SOURCE, PROCESS_SOURCE):
        if not path.exists():
            raise SystemExit(f"Export ativo não encontrado: {path}")
    build_send()
    build_capture()
    build_capture_new()
    build_manual_capture()
    build_worker()
    build_monitor()
    for path in (SEND_OUTPUT, CAPTURE_OUTPUT, CAPTURE_NEW_OUTPUT, MANUAL_OUTPUT, WORKER_OUTPUT, MONITOR_OUTPUT):
        print(path)


if __name__ == "__main__":
    main()
