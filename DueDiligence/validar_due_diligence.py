#!/usr/bin/env python3
"""Valida os artefatos do módulo Due Diligence sem modificá-los."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable
from xml.etree import ElementTree

try:
    import yaml
except ImportError:  # pragma: no cover - depende do ambiente de execução
    yaml = None


BASE = Path(__file__).resolve().parent
PANEL_FILE = BASE / "ScreenDueDiligencePainel.yaml"
YAML_FILES = (
    BASE / "ScreenDueDiligence.yaml",
    BASE / "ScreenDueDiligenceInicio.yaml",
    PANEL_FILE,
)
MAIN_LIST_FILE = BASE / "listgen_tb_dueDiligence_completo.json"
PARAMETERS_LIST_FILE = BASE / "listgen_tb_dueDiligenceParametros_completo.json"
THIRD_PARTY_RESPONSES_FILE = BASE / "listgen_tb_dueDiligenceTerceiroRespostas.json"
COMPLIANCE_LIST_FILE = BASE / "listgen_tb_dueDiligenceCompliance.json"
DESDOBRAMENTOS_LIST_FILE = BASE / "listgen_tb_dueDiligenceDesdobramentos_completo.json"
# Regra de acesso do perfil Compliance: chave não vazia e registro achado
# (lição de 2026-09-02), envolvida em IfError para falhar fechada.
COMPLIANCE_ACCESS_TOKENS = (
    "IfError( With( {_email: Lower(Trim(User().Email))},",
    "!IsBlank(_email) && !IsBlank(LookUp(tb_dueDiligenceCompliance, email = _email && ativo = 1, ID))",
    "), false )",
)
READY_FLOW_FILES = (
    BASE / "EnviarquestionarioDueDiligence_PRONTO.zip",
    BASE / "ProcessarrespostaDueDiligence_PRONTO.zip",
    BASE / "VencervigenciaDueDiligence_PRONTO.zip",
)
LAUDO_READY_FILE = BASE / "GerarLaudoDueDiligence_PRONTO.zip"
LAUDO_DECISION_STATUSES = ("Aprovado", "Aprovado com Ressalvas", "Reprovado Parcialmente", "Reprovado")
FORM_ID = "itUz0nOZp0OvaWdjYwVIoMoEbKAMYIZFqUAdth6B_EFURVRKSFdaVDE4Q1RIV0VTRkxFSjFZS0VEQS4u"
FORM_QUESTION_IDS = {
    "rc17ec46a782c4e9bb8577f1776f7b6a5",
    "rc8315faaa6674c8584da070ee5350001",
    "reabf29569f654ca7876bd8dd6470ef47",
    "r41b1c93b2d5c4cb090fe93048d907b04",
    "rdefccd229818492b9bbe6727758760a7",
    "ra29396cc8af3475eab68360908138053",
    "r26254dcbbf9b4275aa3b824059f6c571",
    "r631326ae893c4c17b3a4c3c627cf6df3",
    "r7eb11f1294d7429391236b5d533ad22c",
    "rf48abfb5124f4eedaf80b66c72091c0c",
    "r37e5d456c486487e91f8e39948d26375",
    "rf6e81f83fe194d4c80dbfd30fc7b8301",
}
RESULT_FIELDS = {
    "classificacao_contraparte": "varClassificacaoContraparteForm",
    "gatilho_dd": "varGatilhoDdForm",
    "fluxo_classificacao": "varFluxoForm",
    "risco_final": "varRiscoFinalTextoForm",
}
PHASE2_MAIN_FIELDS = {
    "terceiro_gatilho_risco": "Text",
    "forms_correlacao_id": "Text",
    "forms_formulario_id": "Text",
    "forms_envio_id": "Text",
    "forms_envio_processado_id": "Text",
    "forms_ultima_resposta_id": "Text",
    "decisao_compliance": "Text",
    "condicionantes_compliance": "Note",
    "justificativa_compliance": "Note",
    "decisao_compliance_por_email": "Text",
    "data_decisao_compliance": "DateTime",
    "prazo_reavaliacao": "DateTime",
    "data_vencimento": "DateTime",
}
PHASE2_RESPONSE_FIELDS = {
    "codigo_opcao": "Text",
    "versao_questionario": "Number",
    "ordem": "Number",
    "forms_formulario_id": "Text",
    "forms_resposta_id": "Text",
    "forms_envio_id": "Text",
    "forms_item_chave": "Text",
}
# Modelo de status definido pelo Compliance em 2026-09-10, na ordem do filtro.
CANONICAL_STATUSES = (
    "Aguardando Terceiro",
    "Pendente Compliance",
    "Aprovado",
    "Aprovado com Ressalvas",
    "Reprovado Parcialmente",
    "Reprovado",
    "Cancelado",
    "Vencido",
)
LEGACY_STATUSES = (
    "Rascunho",
    "Aguardando envio ao terceiro",
    "Aguardando terceiro",
    "Em análise Compliance",
    "Aguardando esclarecimento",
    "Em homologação",
    "Encerrado - risco baixo",
    "Aprovado automaticamente - Fluxo I",
    "Cadastrado - monitoramento (Fluxo II)",
    "Aprovado com ressalvas",
    "Reprovado parcialmente",
    "Erro no envio ao terceiro",
)
DECISION_STATUSES = ("Aprovado", "Aprovado com Ressalvas", "Reprovado Parcialmente", "Reprovado")
VALIDITY_STATUSES = ("Aprovado", "Aprovado com Ressalvas", "Reprovado Parcialmente")
MANUAL_HISTORY_TYPES = ("Aguardando esclarecimentos", "Parecer final", "Cancelamento")
REMOVED_HISTORY_TYPES = (
    "Envio ao terceiro",
    "Resposta do terceiro",
    "Início da análise",
    "Encaminhamento para homologação",
    "Retorno da homologação",
    "Reabertura",
)
# Vigência: baixo 3 anos, médio 2, alto ou ausente 1.
VALIDITY_RULE_POWERFX = '"baixo", 3, "médio", 2, "medio", 2, 1)'


class PowerAppsSafeLoader(yaml.SafeLoader if yaml else object):
    """SafeLoader que aceita o escalar especial ``=`` do Source Code."""


if yaml:
    PowerAppsSafeLoader.add_constructor(
        "tag:yaml.org,2002:value",
        lambda loader, node: loader.construct_scalar(node),
    )


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.passed = 0
        self.failed = 0

    def check(self, label: str, operation: Callable[[list[str]], str | None]) -> None:
        findings: list[str] = []
        detail: str | None = None
        try:
            detail = operation(findings)
        except Exception as exc:  # torna falhas do próprio validador visíveis
            findings.append(f"erro inesperado no check: {type(exc).__name__}: {exc}")

        if findings:
            self.failed += 1
            print(f"[FALHA] {label}")
            for finding in findings:
                message = f"{label}: {finding}"
                self.errors.append(message)
                print(f"        - {finding}")
        else:
            self.passed += 1
            suffix = f" — {detail}" if detail else ""
            print(f"[OK]    {label}{suffix}")


def display(path: Path) -> str:
    try:
        return str(path.relative_to(BASE))
    except ValueError:
        return str(path)


def xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def columns_by_name(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    columns = document.get("colunas")
    if not isinstance(columns, list):
        return {}
    return {
        column["internalName"]: column
        for column in columns
        if isinstance(column, dict) and isinstance(column.get("internalName"), str)
    }


def formula_value(value: Any) -> str | None:
    """Extrai um literal simples de uma fórmula como ``=\"campo\"``."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value.startswith("="):
        return None
    value = value[1:].strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('""', '"')
    return value


def is_main_data_source(value: Any) -> bool:
    source = formula_value(value)
    if source is None:
        return False
    source = re.sub(r"\s+", "", source)
    if source.startswith("[@") and source.endswith("]"):
        source = source[2:-1]
    if len(source) >= 2 and source[0] == source[-1] == "'":
        source = source[1:-1].replace("''", "'")
    return source == "tb_dueDiligence"


def iter_controls(children: Any):
    """Percorre uma árvore de Children já validada, tolerando erros parciais."""
    if not isinstance(children, list):
        return
    for item in children:
        if not isinstance(item, dict) or len(item) != 1:
            continue
        name, body = next(iter(item.items()))
        if not isinstance(body, dict):
            continue
        yield str(name), body
        yield from iter_controls(body.get("Children"))


def iter_json_items(value: Any):
    """Percorre todos os pares chave/valor de um JSON aninhado."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from iter_json_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_json_items(child)


def balanced_call(text: str, open_index: int) -> str:
    """Conteúdo entre o parêntese em ``open_index`` e o seu par, ignorando strings."""
    depth = 0
    quote: str | None = None
    for index in range(open_index, len(text)):
        char = text[index]
        if quote:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[open_index + 1:index]
    return text[open_index + 1:]


def strip_powerfx_literals_and_comments(formula: str) -> str:
    """Mascara strings, identificadores citados e comentários de uma fórmula."""
    output: list[str] = []
    index = 0
    quote: str | None = None
    line_comment = False
    block_comment = False
    while index < len(formula):
        char = formula[index]
        following = formula[index + 1] if index + 1 < len(formula) else ""
        if line_comment:
            if char in "\r\n":
                line_comment = False
                output.append(char)
            else:
                output.append(" ")
            index += 1
            continue
        if block_comment:
            if char == "*" and following == "/":
                output.extend((" ", " "))
                index += 2
                block_comment = False
            else:
                output.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if quote:
            if char == quote and following == quote:
                output.extend((" ", " "))
                index += 2
                continue
            if char == quote:
                quote = None
            output.append(" ")
            index += 1
            continue
        if char == "/" and following == "/":
            output.extend((" ", " "))
            index += 2
            line_comment = True
            continue
        if char == "/" and following == "*":
            output.extend((" ", " "))
            index += 2
            block_comment = True
            continue
        if char in ('"', "'"):
            quote = char
            output.append(" ")
            index += 1
            continue
        output.append(char)
        index += 1
    return "".join(output)


def main() -> int:
    validator = Validator()
    json_documents: dict[Path, dict[str, Any]] = {}
    json_texts: dict[Path, str] = {}
    yaml_documents: dict[Path, dict[str, Any]] = {}
    yaml_texts: dict[Path, str] = {}

    print("Validador — Due Diligence")
    print(f"Diretório: {BASE}")

    def check_json_syntax(findings: list[str]) -> str:
        paths = sorted(BASE.glob("*.json"))
        if not paths:
            findings.append("nenhum arquivo JSON encontrado")
            return ""
        for path in paths:
            try:
                text = path.read_text(encoding="utf-8")
                document = json.loads(text)
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                findings.append(f"{display(path)}: JSON inválido: {exc}")
                continue
            if not isinstance(document, dict):
                findings.append(f"{display(path)}: a raiz JSON deve ser um objeto")
                continue
            json_texts[path] = text
            json_documents[path] = document
        return f"{len(json_documents)} arquivo(s) válido(s)"

    validator.check("JSON válido", check_json_syntax)

    def check_internal_names(findings: list[str]) -> str:
        total = 0
        for path, document in json_documents.items():
            columns = document.get("colunas")
            if not isinstance(columns, list):
                findings.append(f"{display(path)}: 'colunas' deve ser uma lista")
                continue
            names: list[str] = []
            for index, column in enumerate(columns, start=1):
                if not isinstance(column, dict):
                    findings.append(f"{display(path)}: colunas[{index}] deve ser um objeto")
                    continue
                name = column.get("internalName")
                if not isinstance(name, str) or not name.strip():
                    findings.append(
                        f"{display(path)}: colunas[{index}].internalName ausente ou inválido"
                    )
                    continue
                names.append(name)
            duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
            for name in duplicates:
                findings.append(f"{display(path)}: internalName duplicado: {name}")
            total += len(names)
        return f"{total} nome(s) interno(s), sem duplicatas"

    validator.check("Nomes internos únicos", check_internal_names)

    def check_schema_xml(findings: list[str]) -> str:
        total = 0
        for path, document in json_documents.items():
            columns = document.get("colunas")
            if not isinstance(columns, list):
                continue
            for index, column in enumerate(columns, start=1):
                if not isinstance(column, dict):
                    continue
                internal_name = column.get("internalName")
                schema = column.get("schemaXml")
                location = f"{display(path)}: colunas[{index}]"
                if not isinstance(schema, str) or not schema.strip():
                    findings.append(f"{location}: schemaXml ausente ou inválido")
                    continue
                try:
                    field = ElementTree.fromstring(schema)
                except ElementTree.ParseError as exc:
                    findings.append(f"{location}: schemaXml inválido: {exc}")
                    continue
                if xml_local_name(field.tag) != "Field":
                    findings.append(f"{location}: raiz do schemaXml deve ser <Field>")
                    continue
                for attribute in ("Name", "StaticName"):
                    actual = field.attrib.get(attribute)
                    if actual != internal_name:
                        findings.append(
                            f"{location}: {attribute}={actual!r}, esperado {internal_name!r}"
                        )
                total += 1
        return f"{total} schema(s) XML coerente(s)"

    validator.check("schemaXml: Name/StaticName correspondem", check_schema_xml)

    def check_no_validation(findings: list[str]) -> str:
        pattern = re.compile(r"<\s*Validation(?:\s|>)", re.IGNORECASE)
        for path, text in json_texts.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{display(path)}:{line}: elemento <Validation> proibido")
        return "nenhum elemento <Validation>"

    validator.check("JSON sem <Validation>", check_no_validation)

    def check_phase2_schemas(findings: list[str]) -> str:
        contracts = (
            (MAIN_LIST_FILE, PHASE2_MAIN_FIELDS),
            (THIRD_PARTY_RESPONSES_FILE, PHASE2_RESPONSE_FIELDS),
        )
        checked = 0
        for path, expected_fields in contracts:
            document = json_documents.get(path)
            if not isinstance(document, dict):
                findings.append(f"{display(path)}: JSON ausente ou inválido")
                continue
            columns = columns_by_name(document)
            for internal_name, expected_type in expected_fields.items():
                column = columns.get(internal_name)
                if column is None:
                    findings.append(
                        f"{display(path)}: campo obrigatório da Fase 2 ausente: {internal_name}"
                    )
                    continue
                try:
                    field = ElementTree.fromstring(str(column.get("schemaXml", "")))
                except ElementTree.ParseError:
                    continue  # o check geral de schemaXml já informa o detalhe
                actual_type = field.attrib.get("Type")
                if actual_type != expected_type:
                    findings.append(
                        f"{display(path)}: {internal_name} usa Type={actual_type!r}; "
                        f"esperado {expected_type!r}"
                    )
                checked += 1

        main_columns = columns_by_name(json_documents.get(MAIN_LIST_FILE, {}))
        response_columns = columns_by_name(
            json_documents.get(THIRD_PARTY_RESPONSES_FILE, {})
        )
        unique_contracts = (
            (MAIN_LIST_FILE, main_columns.get("forms_correlacao_id")),
            (THIRD_PARTY_RESPONSES_FILE, response_columns.get("forms_item_chave")),
        )
        for path, column in unique_contracts:
            if not isinstance(column, dict):
                continue
            try:
                field = ElementTree.fromstring(str(column.get("schemaXml", "")))
            except ElementTree.ParseError:
                continue
            for attribute, expected in (
                ("Required", "TRUE"),
                ("Indexed", "TRUE"),
                ("EnforceUniqueValues", "TRUE"),
            ):
                if field.attrib.get(attribute) != expected:
                    findings.append(
                        f"{display(path)}: {column['internalName']} exige "
                        f"{attribute}={expected!r}"
                    )
        return f"{checked} campo(s) da Fase 2 com tipos e chaves coerentes"

    validator.check("Schemas da Fase 2", check_phase2_schemas)

    def check_third_party_parameters(findings: list[str]) -> str:
        document = json_documents.get(PARAMETERS_LIST_FILE)
        if not isinstance(document, dict):
            findings.append(f"{display(PARAMETERS_LIST_FILE)}: JSON ausente ou inválido")
            return ""
        records = document.get("registrosIniciais")
        if not isinstance(records, list):
            findings.append(f"{display(PARAMETERS_LIST_FILE)}: registrosIniciais inválido")
            return ""
        phase2_records = [
            record
            for record in records
            if isinstance(record, dict)
            and str(record.get("codigo_pergunta", "")).startswith("terceiro_")
            and record.get("versao_questionario") == 2
        ]
        actual = {
            (record.get("codigo_pergunta"), record.get("codigo_opcao")): record
            for record in phase2_records
        }
        if len(actual) != len(phase2_records):
            findings.append("há chaves duplicadas nos parâmetros categóricos do terceiro")
        expected: dict[tuple[str, str], str] = {}
        for question in ("terceiro_t01", "terceiro_t01_2"):
            expected[(question, f"{question}_sim")] = "Risco Baixo"
            expected[(question, f"{question}_nao")] = "Risco Baixo"
        for question in (
            "terceiro_t02",
            "terceiro_t03_pep",
            "terceiro_t03_processos",
            "terceiro_t04",
            "terceiro_t06",
            "terceiro_t07",
            "terceiro_t08",
        ):
            expected[(question, f"{question}_sim")] = "Risco Alto"
            expected[(question, f"{question}_nao")] = "Risco Baixo"
        expected[("terceiro_t05", "terceiro_t05_texto")] = "Sem pontuação"
        for answer in ("sim", "nao"):
            expected[("terceiro_t09", f"terceiro_t09_{answer}")] = "Sem pontuação"

        if set(actual) != set(expected):
            missing = sorted(set(expected) - set(actual))
            extra = sorted(set(actual) - set(expected))
            if missing:
                findings.append(f"parâmetros categóricos ausentes: {missing}")
            if extra:
                findings.append(f"parâmetros categóricos inesperados: {extra}")
        for key, expected_classification in expected.items():
            record = actual.get(key)
            if not isinstance(record, dict):
                continue
            if record.get("classificacao") != expected_classification:
                findings.append(
                    f"{key}: classificação {record.get('classificacao')!r}; "
                    f"esperado {expected_classification!r}"
                )
            for field_name, expected_value in (
                ("pontuacao", 0),
                ("encerra_risco_baixo", 0),
                ("ativo", 1),
            ):
                if record.get(field_name) != expected_value:
                    findings.append(
                        f"{key}: {field_name}={record.get(field_name)!r}; "
                        f"esperado {expected_value!r}"
                    )
        high_questions = {
            question
            for (question, option), classification in expected.items()
            if option.endswith("_sim") and classification == "Risco Alto"
        }
        if len(high_questions) != 7:
            findings.append(
                f"esperadas 7 perguntas-gatilho de risco alto; encontrado(s): {len(high_questions)}"
            )
        return f"{len(expected)} opção(ões), com 7 perguntas-gatilho categóricas"

    validator.check("Parâmetros categóricos do terceiro", check_third_party_parameters)

    def check_ready_flows(findings: list[str]) -> str:
        definitions: dict[Path, dict[str, Any]] = {}
        for path in READY_FLOW_FILES:
            if not path.is_file():
                findings.append(f"{display(path)}: pacote pronto não encontrado")
                continue
            try:
                with zipfile.ZipFile(path) as archive:
                    damaged = archive.testzip()
                    if damaged:
                        findings.append(f"{display(path)}: entrada ZIP corrompida: {damaged}")
                        continue
                    names = [name for name in archive.namelist() if name.endswith("/definition.json")]
                    if len(names) != 1:
                        findings.append(
                            f"{display(path)}: esperado um definition.json; encontrado(s): {len(names)}"
                        )
                        continue
                    definitions[path] = json.loads(archive.read(names[0]))
            except (OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
                findings.append(f"{display(path)}: pacote inválido: {exc}")

        if len(definitions) != len(READY_FLOW_FILES):
            return ""

        send = definitions[READY_FLOW_FILES[0]]
        process = definitions[READY_FLOW_FILES[1]]
        expiry = definitions[READY_FLOW_FILES[2]]
        send_text = json.dumps(send, ensure_ascii=False)
        process_text = json.dumps(process, ensure_ascii=False)
        expiry_text = json.dumps(expiry, ensure_ascii=False)
        combined = send_text + process_text
        if "PREENCHER_" in combined + expiry_text:
            findings.append("os fluxos prontos ainda contêm placeholder PREENCHER_*")
        for token in (
            "'Aguardando Terceiro'",
            "Falha no envio ao terceiro",
            "SendEmailV2",
            "forms_envio_processado_id",
        ):
            if token not in send_text:
                findings.append(f"DD01 sem contrato obrigatório: {token!r}")
        for token in (
            "GetFormResponseById",
            "tb_dueDiligenceTerceiroRespostas",
            "tb_dueDiligenceParametros",
            "forms_item_chave",
            "'Aguardando Terceiro'",
            "Pendente Compliance",
            "terceiro_t05_texto",
        ):
            if token not in process_text:
                findings.append(f"DD02 sem contrato obrigatório: {token!r}")
        if FORM_ID not in send_text or FORM_ID not in process_text:
            findings.append("Form ID real não está presente nos dois fluxos")
        if "origin=lprLink" not in send_text:
            findings.append(
                "DD01 não usa a origem obrigatória dos links pré-preenchidos do Forms"
            )
        missing_ids = sorted(FORM_QUESTION_IDS - {qid for qid in FORM_QUESTION_IDS if qid in combined})
        if missing_ids:
            findings.append(f"IDs internos do Forms ausentes: {missing_ids}")

        def find_action(value: Any, name: str) -> dict[str, Any] | None:
            if not isinstance(value, dict):
                return None
            actions = value.get("actions")
            if isinstance(actions, dict) and isinstance(actions.get(name), dict):
                return actions[name]
            for child in value.values():
                if isinstance(child, dict):
                    found = find_action(child, name)
                    if found is not None:
                        return found
                elif isinstance(child, list):
                    for nested in child:
                        found = find_action(nested, name)
                        if found is not None:
                            return found
            return None

        response_compose = find_action(process, "Montar_Item_Resposta")
        response_inputs = (
            response_compose.get("inputs")
            if isinstance(response_compose, dict)
            else None
        )
        for field_name in (
            "codigo_pergunta",
            "codigo_opcao",
            "texto_pergunta",
            "resposta",
            "classificacao",
            "forms_resposta_id",
            "forms_envio_id",
            "forms_item_chave",
        ):
            value = (
                response_inputs.get(field_name)
                if isinstance(response_inputs, dict)
                else None
            )
            if not isinstance(value, str) or not value.startswith("@string("):
                findings.append(
                    f"DD02: Montar_Item_Resposta.{field_name} deve converter "
                    "explicitamente para string"
                )

        request_update = find_action(process, "Montar_Atualizacao_Solicitacao")
        request_inputs = (
            request_update.get("inputs") if isinstance(request_update, dict) else None
        )
        last_response_id = (
            request_inputs.get("forms_ultima_resposta_id")
            if isinstance(request_inputs, dict)
            else None
        )
        if not isinstance(last_response_id, str) or not last_response_id.startswith(
            "@string("
        ):
            findings.append(
                "DD02: forms_ultima_resposta_id deve converter o responseId para string"
            )

        # DD01 sem status de erro: o sucesso não regrava status (desfaria um
        # cancelamento concorrente) e o catch consome a intenção de envio.
        send_update = find_action(send, "Montar_Atualizacao_Envio")
        send_update_inputs = send_update.get("inputs") if isinstance(send_update, dict) else None
        if not isinstance(send_update_inputs, dict) or "status" in send_update_inputs:
            findings.append("DD01: Montar_Atualizacao_Envio não pode regravar status")
        consume = find_action(send, "Montar_Consumo_Intencao")
        consume_inputs = consume.get("inputs") if isinstance(consume, dict) else None
        if not isinstance(consume_inputs, dict) or set(consume_inputs) != {"forms_envio_processado_id"}:
            findings.append(
                "DD01: o catch deve consumir a intenção gravando só forms_envio_processado_id"
            )

        # DD03: vigência por risco e vencimento diário.
        expiry_workflow = (expiry.get("properties") or {}).get("definition") or {}
        expiry_triggers = list((expiry_workflow.get("triggers") or {}).values())
        if [trigger.get("type") for trigger in expiry_triggers] != ["Recurrence"]:
            findings.append("DD03 deve ter exatamente um gatilho Recurrence")
        for token in (
            "'baixo'), 3",
            "'medio')), 2, 1)",
            "'Year'",
            "data_vencimento eq null",
            "data_vencimento lt datetime",
            "Vencimento da vigência",
            "E. South America Standard Time",
        ):
            if token not in expiry_text:
                findings.append(f"DD03 sem contrato obrigatório: {token!r}")
        for status in VALIDITY_STATUSES:
            if not re.search(rf"status eq '{{1,2}}{re.escape(status)}'{{1,2}}", expiry_text):
                findings.append(f"DD03 não filtra o status com vigência {status!r}")
        expiry_status = find_action(expiry, "Montar_Status_Vencido")
        if not isinstance(expiry_status, dict) or expiry_status.get("inputs") != {"status": "Vencido"}:
            findings.append("DD03: Montar_Status_Vencido deve gravar status 'Vencido'")
        with zipfile.ZipFile(READY_FLOW_FILES[2]) as archive:
            expiry_manifest = json.loads(archive.read("manifest.json"))
        flow_resources = [
            resource
            for resource in expiry_manifest.get("resources", {}).values()
            if resource.get("type") == "Microsoft.Flow/flows"
        ]
        if [resource.get("suggestedCreationType") for resource in flow_resources] != ["New"]:
            findings.append("DD03 deve ser importado como fluxo novo (suggestedCreationType=New)")

        for path, document in definitions.items():
            properties = document.get("properties")
            workflow = properties.get("definition") if isinstance(properties, dict) else None
            if not isinstance(workflow, dict) or not isinstance(workflow.get("actions"), dict):
                findings.append(f"{display(path)}: estrutura properties.definition.actions inválida")
                continue
            if not workflow["actions"]:
                findings.append(f"{display(path)}: fluxo continua sem ações")
            trigger_values = list((workflow.get("triggers") or {}).values())
            if len(trigger_values) != 1:
                findings.append(f"{display(path)}: esperado exatamente um gatilho")
            else:
                trigger = trigger_values[0]
                if ((trigger.get("runtimeConfiguration") or {}).get("concurrency") or {}).get("runs") != 1:
                    findings.append(f"{display(path)}: concorrência do gatilho deve ser 1")
                conditions = trigger.get("conditions", [])
                if not isinstance(conditions, list):
                    findings.append(f"{display(path)}: trigger.conditions deve ser uma lista")
                for index, trigger_condition in enumerate(conditions):
                    if not isinstance(trigger_condition, dict) or not isinstance(
                        trigger_condition.get("expression"), str
                    ):
                        findings.append(
                            f"{display(path)}: trigger.conditions[{index}] deve ser objeto com expression"
                        )

            expression_count = 0

            def validate_wdl(value: Any, location: str = "") -> None:
                nonlocal expression_count
                if isinstance(value, dict):
                    for key, child in value.items():
                        validate_wdl(child, f"{location}.{key}" if location else str(key))
                    return
                if isinstance(value, list):
                    for index, child in enumerate(value):
                        validate_wdl(child, f"{location}[{index}]")
                    return
                if not isinstance(value, str) or not value.startswith("@"):
                    return
                expression_count += 1
                stack: list[str] = []
                pairs = {")": "(", "]": "[", "}": "{"}
                in_string = False
                index = 0
                while index < len(value):
                    char = value[index]
                    following = value[index + 1] if index + 1 < len(value) else ""
                    if in_string:
                        if char == "'" and following == "'":
                            index += 2
                            continue
                        if char == "'":
                            in_string = False
                        index += 1
                        continue
                    if char == "'":
                        in_string = True
                    elif char == '"':
                        findings.append(
                            f"{display(path)}: {location}: aspas duplas fora de literal WDL"
                        )
                        return
                    elif char in pairs.values():
                        stack.append(char)
                    elif char in pairs:
                        if not stack or stack[-1] != pairs[char]:
                            findings.append(
                                f"{display(path)}: {location}: delimitador {char!r} sem par"
                            )
                            return
                        stack.pop()
                    index += 1
                if in_string:
                    findings.append(f"{display(path)}: {location}: literal WDL não fechado")
                elif stack:
                    findings.append(
                        f"{display(path)}: {location}: delimitador {stack[-1]!r} não fechado"
                    )

            validate_wdl(workflow)
            if expression_count == 0:
                findings.append(f"{display(path)}: nenhuma expressão WDL encontrada")

            def check_terminate_location(value: Any, inside_foreach: bool = False) -> None:
                if not isinstance(value, dict):
                    return
                current_foreach = inside_foreach or value.get("type") == "Foreach"
                if current_foreach and value.get("type") == "Terminate":
                    findings.append(
                        f"{display(path)}: ação Terminate não pode ficar dentro de Foreach"
                    )
                for child in value.values():
                    if isinstance(child, dict):
                        check_terminate_location(child, current_foreach)
                    elif isinstance(child, list):
                        for nested in child:
                            check_terminate_location(nested, current_foreach)

            check_terminate_location(workflow)
        return "3 pacotes íntegros, correlacionados e sem placeholders"

    validator.check("Pacotes Power Automate prontos", check_ready_flows)

    def check_line_endings(findings: list[str]) -> str:
        for path in YAML_FILES:
            if not path.is_file():
                findings.append(f"{display(path)}: arquivo não encontrado")
                continue
            raw = path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                findings.append(f"{display(path)}: contém BOM UTF-8")
            without_crlf = raw.replace(b"\r\n", b"")
            if b"\n" in without_crlf or b"\r" in without_crlf:
                findings.append(f"{display(path)}: há quebra de linha fora do padrão CRLF")
            if b"\r\n" not in raw:
                findings.append(f"{display(path)}: não contém quebras de linha CRLF")
        return f"{len(YAML_FILES)} tela(s) em CRLF e sem BOM"

    validator.check("CRLF íntegro e ausência de BOM", check_line_endings)

    def check_yaml_syntax(findings: list[str]) -> str:
        if yaml is None:
            findings.append("PyYAML não está instalado; não foi possível validar a sintaxe YAML")
            return ""
        for path in YAML_FILES:
            if not path.is_file():
                findings.append(f"{display(path)}: arquivo não encontrado")
                continue
            try:
                text = path.read_text(encoding="utf-8")
                # SafeLoader confirma sintaxe/tipos; BaseLoader preserva chaves como Y.
                yaml.load(text, Loader=PowerAppsSafeLoader)
                document = yaml.load(text, Loader=yaml.BaseLoader)
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                findings.append(f"{display(path)}: YAML inválido: {exc}")
                continue
            if not isinstance(document, dict):
                findings.append(f"{display(path)}: a raiz YAML deve ser um mapa")
                continue
            yaml_texts[path] = text
            yaml_documents[path] = document
        return f"{len(yaml_documents)} tela(s) válida(s)"

    validator.check("YAML válido", check_yaml_syntax)

    def check_root(findings: list[str]) -> str:
        for path, document in yaml_documents.items():
            if list(document) != ["Screens"]:
                findings.append(
                    f"{display(path)}: raiz deve conter somente 'Screens' (encontrado: {list(document)})"
                )
                continue
            screens = document.get("Screens")
            if not isinstance(screens, dict) or len(screens) != 1:
                findings.append(f"{display(path)}: 'Screens' deve conter exatamente uma tela")
                continue
            screen_name, screen = next(iter(screens.items()))
            if not isinstance(screen, dict):
                findings.append(f"{display(path)}: tela {screen_name!r} deve ser um mapa")
            if not yaml_texts[path].startswith(f"Screens:\n  {screen_name}:\n"):
                # read_text normaliza CRLF para \n; aqui validamos a coluna/recuo.
                findings.append(
                    f"{display(path)}: raiz/recuo inicial incompatível com Screens/{screen_name}"
                )
        return "estrutura raiz Screens confirmada"

    validator.check("Raiz Screens", check_root)

    def check_properties(findings: list[str]) -> str:
        count = 0

        def walk(value: Any, path: str, file_name: str) -> None:
            nonlocal count
            if isinstance(value, dict):
                for key, child in value.items():
                    child_path = f"{path}.{key}" if path else str(key)
                    if key == "Properties":
                        if not isinstance(child, dict):
                            findings.append(f"{file_name}: {child_path} deve ser um mapa")
                        else:
                            for property_name, property_value in child.items():
                                count += 1
                                if not isinstance(property_value, str) or not property_value.startswith("="):
                                    preview = repr(property_value)[:80]
                                    findings.append(
                                        f"{file_name}: {child_path}.{property_name} não começa com '=' ({preview})"
                                    )
                    walk(child, child_path, file_name)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{path}[{index}]", file_name)

        for path, document in yaml_documents.items():
            walk(document, "", display(path))
        return f"{count} propriedade(s) começam com '='"

    validator.check("Prefixo '=' em propriedades", check_properties)

    def check_formula_delimiters(findings: list[str]) -> str:
        total = 0
        pairs = {")": "(", "]": "[", "}": "{"}
        openings = set(pairs.values())

        def walk(value: Any, location: str, file_name: str) -> None:
            nonlocal total
            if isinstance(value, dict):
                for key, child in value.items():
                    child_location = f"{location}.{key}" if location else str(key)
                    if isinstance(child, str) and child.startswith("="):
                        total += 1
                        stack: list[tuple[str, int]] = []
                        clean = strip_powerfx_literals_and_comments(child)
                        for offset, char in enumerate(clean):
                            if char in openings:
                                stack.append((char, offset))
                            elif char in pairs:
                                if not stack or stack[-1][0] != pairs[char]:
                                    findings.append(
                                        f"{file_name}: {child_location}: delimitador {char!r} sem par"
                                    )
                                    break
                                stack.pop()
                        else:
                            if stack:
                                findings.append(
                                    f"{file_name}: {child_location}: delimitador {stack[-1][0]!r} não fechado"
                                )
                    walk(child, child_location, file_name)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{location}[{index}]", file_name)

        for path, document in yaml_documents.items():
            walk(document, "", display(path))
        return f"{total} fórmula(s) com (), [] e {{}} balanceados"

    validator.check("Delimitadores Power Fx balanceados", check_formula_delimiters)

    control_locations: defaultdict[str, list[str]] = defaultdict(list)

    def check_children(findings: list[str]) -> str:
        count = 0

        def validate(children: Any, location: str, file_name: str) -> None:
            nonlocal count
            if not isinstance(children, list):
                findings.append(f"{file_name}: {location} deve ser uma lista")
                return
            for index, item in enumerate(children):
                item_location = f"{location}[{index}]"
                if not isinstance(item, dict):
                    findings.append(f"{file_name}: {item_location} deve ser um mapa")
                    continue
                keys = list(item)
                if len(keys) != 1:
                    findings.append(
                        f"{file_name}: {item_location} deve ter um único controle; chaves={keys}"
                    )
                    continue
                control_name = keys[0]
                body = item[control_name]
                control_location = f"{location}/{control_name}"
                count += 1
                control_locations[str(control_name)].append(f"{file_name}:{control_location}")
                if not isinstance(control_name, str) or not control_name.strip():
                    findings.append(f"{file_name}: {item_location}: nome de controle inválido")
                if not isinstance(body, dict):
                    findings.append(f"{file_name}: {control_location} deve ser um mapa")
                    continue
                if not isinstance(body.get("Control"), str) or not body["Control"].strip():
                    findings.append(f"{file_name}: {control_location}: 'Control' ausente ou inválido")
                if "Properties" in body and not isinstance(body["Properties"], dict):
                    findings.append(f"{file_name}: {control_location}.Properties deve ser um mapa")
                if "Children" in body:
                    validate(body["Children"], f"{control_location}.Children", file_name)

        for path, document in yaml_documents.items():
            screens = document.get("Screens")
            if not isinstance(screens, dict):
                continue
            for screen_name, screen in screens.items():
                if not isinstance(screen, dict):
                    continue
                if "Children" not in screen:
                    findings.append(f"{display(path)}: tela {screen_name} sem 'Children'")
                    continue
                validate(screen["Children"], f"{screen_name}.Children", display(path))
        return f"{count} controle(s) em árvores bem formadas"

    validator.check("Children bem formados", check_children)

    def check_unique_controls(findings: list[str]) -> str:
        for name, locations in sorted(control_locations.items()):
            if len(locations) > 1:
                findings.append(
                    f"controle {name!r} duplicado ({len(locations)}x): " + "; ".join(locations)
                )
        return f"{len(control_locations)} nome(s) de controle único(s) entre as telas"

    validator.check("Nomes de controle únicos", check_unique_controls)

    def check_raw_prohibitions(findings: list[str]) -> str:
        for path, text in yaml_texts.items():
            for line_number, line in enumerate(text.splitlines(), start=1):
                if "%DATACARD_" in line:
                    findings.append(f"{display(path)}:{line_number}: placeholder %DATACARD_ proibido")
                if re.match(r"^\s*Overflow\s*:", line):
                    findings.append(f"{display(path)}:{line_number}: propriedade Overflow proibida")
        return "sem %DATACARD_ e sem Overflow"

    validator.check("Proibições do Source Code", check_raw_prohibitions)

    def check_text_inputs(findings: list[str]) -> str:
        total = 0
        for path, document in yaml_documents.items():
            screens = document.get("Screens")
            if not isinstance(screens, dict):
                continue
            for screen in screens.values():
                if not isinstance(screen, dict):
                    continue
                for name, body in iter_controls(screen.get("Children")):
                    if body.get("Control") != "TextInput@0.0.54":
                        continue
                    total += 1
                    properties = body.get("Properties")
                    if isinstance(properties, dict) and "Default" in properties:
                        findings.append(
                            f"{display(path)}: {name}.Default é proibido em TextInput@0.0.54; use Value"
                        )
        return f"{total} TextInput(s) moderno(s) sem Default"

    validator.check("TextInput@0.0.54 sem Default", check_text_inputs)

    def check_field_value(findings: list[str]) -> str:
        cards = 0
        for path, document in yaml_documents.items():
            screens = document.get("Screens")
            if not isinstance(screens, dict):
                continue
            for screen in screens.values():
                if not isinstance(screen, dict):
                    continue
                for card_name, card in iter_controls(screen.get("Children")):
                    if "DataCard@" not in str(card.get("Control", "")):
                        continue
                    cards += 1
                    field_values = [
                        child_name
                        for child_name, child in iter_controls(card.get("Children"))
                        if child.get("MetadataKey") == "FieldValue"
                    ]
                    if len(field_values) > 1:
                        findings.append(
                            f"{display(path)}: {card_name} contém MetadataKey FieldValue duplicada: "
                            + ", ".join(field_values)
                        )
        return f"{cards} DataCard(s) sem FieldValue duplicada"

    validator.check("MetadataKey FieldValue por DataCard", check_field_value)

    def check_inline_colon(findings: list[str]) -> str:
        total = 0
        property_line = re.compile(r"^\s+[A-Za-z][A-Za-z0-9_]*:\s+(=.*)$")
        for path, text in yaml_texts.items():
            for line_number, line in enumerate(text.splitlines(), start=1):
                match = property_line.match(line)
                if not match:
                    continue
                total += 1
                if ": " in match.group(1):
                    findings.append(
                        f"{display(path)}:{line_number}: ': ' em fórmula Power Fx inline; use bloco '|-'"
                    )
        return f"{total} fórmula(s) inline sem ': '"

    validator.check("Power Fx inline sem ': '", check_inline_colon)

    main_yaml_text = yaml_texts.get(BASE / "ScreenDueDiligence.yaml", "")
    main_controls: dict[str, dict[str, Any]] = {}
    main_document = yaml_documents.get(BASE / "ScreenDueDiligence.yaml")
    if isinstance(main_document, dict):
        screens = main_document.get("Screens")
        if isinstance(screens, dict):
            for screen in screens.values():
                if isinstance(screen, dict):
                    main_controls.update(iter_controls(screen.get("Children")))

    def check_delegable_gallery(findings: list[str]) -> str:
        legacy_patterns = (
            "IsBlank(cmbDdFiltroStatus.Selected.Value) || status =",
            "IsBlank(dpDdDataInicio.SelectedDate) || Created >=",
            "IsBlank(dpDdDataFim.SelectedDate) || Created <",
        )
        for pattern in legacy_patterns:
            if pattern in main_yaml_text:
                findings.append(
                    f"galDdRegistros ainda usa filtro opcional não delegável: {pattern!r}"
                )
        gallery = main_controls.get("galDdRegistros", {})
        items = str((gallery.get("Properties") or {}).get("Items", ""))
        for token in (
            "_idBusca:",
            "_status:",
            "_dataInicio:",
            "_dataFimExclusiva:",
            "ID = _idBusca",
            "status = _status",
        ):
            if token not in items:
                findings.append(f"galDdRegistros.Items não contém o contrato delegável {token!r}")
        for prohibited in ("Date(9999, 12, 31)", "ID = Value(_busca)"):
            if prohibited in items:
                findings.append(
                    f"galDdRegistros.Items mantém expressão ambígua para delegação/conector: {prohibited!r}"
                )
        counter = main_controls.get("lblDdQtd", {})
        counter_text = str((counter.get("Properties") or {}).get("Text", ""))
        if "CARREGADO(S)" not in counter_text or "ENCONTRADO(S)" in counter_text:
            findings.append(
                "lblDdQtd deve identificar AllItemsCount como REGISTRO(S) CARREGADO(S)"
            )
        return "filtros opcionais ramificados fora do Filter e contador sem total enganoso"

    validator.check("Galeria delegável e contador correto", check_delegable_gallery)

    def check_reentrancy(findings: list[str]) -> str:
        guarded_controls = (
            "btnDdSalvarForm",
            "tbDdAcoes",
            "btnDdRegistrarDesdobramento",
            "btnDdExcluirConfirmar",
        )
        for control_name in guarded_controls:
            control = main_controls.get(control_name)
            if not isinstance(control, dict):
                findings.append(f"controle de escrita {control_name!r} não localizado")
                continue
            formula = str((control.get("Properties") or {}).get("OnSelect", ""))
            for token in (
                "DateDiff(varDdOcupadoDesde, Now(), TimeUnit.Seconds) < 30",
                "varDdOcupadoDesde: Now()",
            ):
                if token not in formula:
                    findings.append(f"{control_name}.OnSelect sem trava de reentrância {token!r}")
        for form_name in ("frmDdSolicitante", "frmDdDesdobramento"):
            form = main_controls.get(form_name)
            if not isinstance(form, dict):
                findings.append(f"formulário {form_name!r} não localizado")
                continue
            properties = form.get("Properties") or {}
            for property_name in ("OnSuccess", "OnFailure"):
                if "varDdOcupadoDesde: Blank()" not in str(properties.get(property_name, "")):
                    findings.append(
                        f"{form_name}.{property_name} não libera varDdOcupadoDesde"
                    )
        return f"{len(guarded_controls)} ação(ões) protegida(s) e formulários liberam a trava"

    validator.check("Trava de reentrância nas gravações", check_reentrancy)

    def check_status_progression(findings: list[str]) -> str:
        card = main_controls.get("status_DataCard", {})
        update = str((card.get("Properties") or {}).get("Update", ""))
        if not update:
            findings.append("status_DataCard.Update não foi localizado")
            return ""
        compact = re.sub(r"\s+", " ", update)
        # Recalcular um Aguardando Terceiro já enviado regrediria a fila; só o
        # registro novo ou o envio com falha voltam a passar pelo motor.
        if "IsBlank(_statusAtual) || _envioFalhou" not in compact:
            findings.append(
                "status_DataCard.Update só pode recalcular registro novo ou com falha no envio"
            )
        for token in (
            'ThisItem.status = "Aguardando Terceiro"',
            "ThisItem.forms_envio_id = ThisItem.forms_envio_processado_id",
            "IsBlank(ThisItem.data_envio_terceiro)",
        ):
            if token not in compact:
                findings.append(f"status_DataCard.Update sem o critério de falha no envio {token!r}")
        literals = set(re.findall(r'"([^"]*)"', update)) - {"", "FLUXO I", "FLUXO II"}
        if literals != {"Aguardando Terceiro", "Aprovado"}:
            findings.append(
                "status_DataCard.Update deve resultar só em Aprovado ou Aguardando Terceiro; "
                f"literais: {sorted(literals)}"
            )
        return "status recalculado só na criação ou após falha no envio"

    validator.check("Progressão do status do terceiro", check_status_progression)

    def check_reachable_risk_trigger(findings: list[str]) -> str:
        button = main_controls.get("btnDdSalvarForm", {})
        formula = str((button.get("Properties") or {}).get("OnSelect", ""))
        text_start = formula.find("_riscoTexto: If(")
        category_start = formula.find("_riscoCategoria: If(")
        variables_end = formula.find("varPontuacaoSolicitanteForm:", category_start)
        if min(text_start, category_start, variables_end) < 0:
            findings.append("não foi possível localizar _riscoTexto/_riscoCategoria no motor v2")
            return ""
        text_formula = formula[text_start:category_start]
        category_formula = formula[category_start:variables_end]
        for label, fragment in (
            ("_riscoTexto", text_formula),
            ("_riscoCategoria", category_formula),
        ):
            trigger_position = fragment.find("_gatilhoDD")
            exhaustive_position = fragment.find('_classificacaoContraparte = "FLUXO II"')
            if trigger_position < 0:
                findings.append(f"{label} não trata _gatilhoDD")
            elif exhaustive_position >= 0 and trigger_position > exhaustive_position:
                findings.append(
                    f"{label}: ramo _gatilhoDD fica depois das classificações válidas e é inalcançável"
                )
        return "gatilho DD alcançável nos campos de risco"

    validator.check("Coerência entre gatilho DD e risco", check_reachable_risk_trigger)

    def wdl_literal_check(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def check_laudo_dd04(findings: list[str]) -> str:
        if not LAUDO_READY_FILE.is_file():
            findings.append(f"{display(LAUDO_READY_FILE)}: pacote pronto não encontrado")
            return ""
        try:
            with zipfile.ZipFile(LAUDO_READY_FILE) as archive:
                damaged = archive.testzip()
                if damaged:
                    findings.append(f"{display(LAUDO_READY_FILE)}: entrada ZIP corrompida: {damaged}")
                    return ""
                name = next(n for n in archive.namelist() if n.endswith("/definition.json"))
                document = json.loads(archive.read(name))
                manifest = json.loads(archive.read("manifest.json"))
        except (OSError, zipfile.BadZipFile, StopIteration, json.JSONDecodeError) as exc:
            findings.append(f"{display(LAUDO_READY_FILE)}: pacote inválido: {exc}")
            return ""

        raw = json.dumps(document, ensure_ascii=False)
        if "PREENCHER_" in raw:
            findings.append(f"{display(LAUDO_READY_FILE)}: ainda contém placeholder PREENCHER_*")
        if "wordonlinebusiness" in raw.lower():
            findings.append(f"{display(LAUDO_READY_FILE)}: depende do conector premium Word Online")

        flows = [r for r in manifest["resources"].values() if r["type"] == "Microsoft.Flow/flows"]
        if [r.get("suggestedCreationType") for r in flows] != ["New"]:
            findings.append(f"{display(LAUDO_READY_FILE)}: deve ser importado como fluxo novo (suggestedCreationType=New)")

        try:
            workflow = document["properties"]["definition"]
            trigger = next(iter(workflow["triggers"].values()))
            condicao = workflow["actions"]["Condicao_Decisao_Final"]
            expressao = condicao["expression"]["and"][0]["equals"][0]
        except (KeyError, IndexError, StopIteration, TypeError):
            findings.append(f"{display(LAUDO_READY_FILE)}: estrutura de ações inesperada")
            return ""

        if trigger.get("type") != "Request" or trigger.get("kind") != "PowerAppV2":
            findings.append(f"{display(LAUDO_READY_FILE)}: gatilho deve ser Power Apps (V2)")
        trigger_props = (trigger.get("inputs", {}).get("schema", {}) or {}).get("properties", {})
        if set(trigger_props) != {"number", "text"}:
            findings.append(
                f"{display(LAUDO_READY_FILE)}: gatilho deve ter as entradas 'number' (id) e "
                f"'text' (html); encontrado: {sorted(trigger_props)}"
            )

        for status in LAUDO_DECISION_STATUSES:
            if wdl_literal_check(status) not in expressao:
                findings.append(
                    f"{display(LAUDO_READY_FILE)}: Condicao_Decisao_Final não contempla {status!r}"
                )
        for token in (
            "triggerBody()?['number']",
            "triggerBody()?['text']",
            "laudo_url",
            "RootFolder/Files/add",
        ):
            if token not in raw:
                findings.append(f"{display(LAUDO_READY_FILE)}: sem contrato obrigatório {token!r}")

        main_document = json_documents.get(MAIN_LIST_FILE)
        if isinstance(main_document, dict) and "laudo_url" not in columns_by_name(main_document):
            findings.append(f"{display(MAIN_LIST_FILE)}: coluna laudo_url ausente (necessária ao DD04)")

        # O botão do app precisa chamar o fluxo com os dois parâmetros (ID e o
        # HTML já montado) e tratar os dois campos de resposta do DD04.
        for token in (
            "DD04GerarLaudo.Run(ThisItem.ID, _html)",
            "_laudo.saida_erro",
            "_laudo.saida_laudo_url",
        ):
            if token not in main_yaml_text:
                findings.append(f"ScreenDueDiligence.yaml: botão do laudo sem {token!r}")

        return "pacote DD04 pronto, coerente com o gatilho real e com o botão do app"

    validator.check("Pacote DD04 e botão do laudo", check_laudo_dd04)

    main_internal_names: set[str] = set()
    if MAIN_LIST_FILE in json_documents:
        columns = json_documents[MAIN_LIST_FILE].get("colunas")
        if isinstance(columns, list):
            main_internal_names = {
                column["internalName"]
                for column in columns
                if isinstance(column, dict) and isinstance(column.get("internalName"), str)
            }

    main_forms: list[tuple[Path, str, dict[str, Any]]] = []
    for path, document in yaml_documents.items():
        screens = document.get("Screens")
        if not isinstance(screens, dict):
            continue
        for screen in screens.values():
            if not isinstance(screen, dict):
                continue
            for name, body in iter_controls(screen.get("Children")):
                properties = body.get("Properties")
                if (
                    str(body.get("Control", "")).startswith("Form@")
                    and isinstance(properties, dict)
                    and is_main_data_source(properties.get("DataSource"))
                ):
                    main_forms.append((path, name, body))

    def main_form_fields() -> dict[str, list[tuple[Path, str, dict[str, Any]]]]:
        result: defaultdict[str, list[tuple[Path, str, dict[str, Any]]]] = defaultdict(list)
        for path, form_name, form in main_forms:
            for card_name, card in iter_controls(form.get("Children")):
                properties = card.get("Properties")
                if not isinstance(properties, dict) or "DataField" not in properties:
                    continue
                field_name = formula_value(properties["DataField"])
                if field_name:
                    result[field_name].append((path, f"{form_name}/{card_name}", card))
        return dict(result)

    form_fields = main_form_fields()

    def check_data_fields(findings: list[str]) -> str:
        if MAIN_LIST_FILE not in json_documents:
            findings.append(f"{display(MAIN_LIST_FILE)}: JSON principal ausente ou inválido")
        if len(main_forms) != 1:
            findings.append(
                f"esperado exatamente 1 Form ligado a tb_dueDiligence; encontrado(s): {len(main_forms)}"
            )
        for field_name, cards in sorted(form_fields.items()):
            if field_name not in main_internal_names:
                locations = ", ".join(f"{display(path)}:{name}" for path, name, _ in cards)
                findings.append(
                    f"DataField {field_name!r} não existe em {display(MAIN_LIST_FILE)} ({locations})"
                )
        return f"{len(form_fields)} DataField(s) do formulário principal existem no JSON"

    validator.check("DataFields do formulário principal", check_data_fields)

    def check_desdobramento_fields(findings: list[str]) -> str:
        document = json_documents.get(DESDOBRAMENTOS_LIST_FILE)
        if not isinstance(document, dict):
            findings.append(f"{display(DESDOBRAMENTOS_LIST_FILE)}: JSON ausente ou inválido")
            return ""
        known = set(columns_by_name(document)) | {"{Attachments}"}
        desdobramento_forms: list[tuple[Path, str, dict[str, Any]]] = []
        for path, document_yaml in yaml_documents.items():
            screens = document_yaml.get("Screens")
            if not isinstance(screens, dict):
                continue
            for screen in screens.values():
                if not isinstance(screen, dict):
                    continue
                for name, body in iter_controls(screen.get("Children")):
                    properties = body.get("Properties")
                    if not (str(body.get("Control", "")).startswith("Form@") and isinstance(properties, dict)):
                        continue
                    source = formula_value(properties.get("DataSource"))
                    if source and re.sub(r"\s+", "", source) == "tb_dueDiligenceDesdobramentos":
                        desdobramento_forms.append((path, name, body))
        if len(desdobramento_forms) != 1:
            findings.append(
                f"esperado exatamente 1 Form ligado a tb_dueDiligenceDesdobramentos; "
                f"encontrado(s): {len(desdobramento_forms)}"
            )
        total = 0
        for path, form_name, form in desdobramento_forms:
            for card_name, card in iter_controls(form.get("Children")):
                properties = card.get("Properties")
                if not isinstance(properties, dict) or "DataField" not in properties:
                    continue
                field_name = formula_value(properties["DataField"])
                if not field_name:
                    continue
                total += 1
                if field_name not in known:
                    findings.append(
                        f"DataField {field_name!r} não existe em {display(DESDOBRAMENTOS_LIST_FILE)} "
                        f"({display(path)}:{form_name}/{card_name})"
                    )
        return f"{total} DataField(s) do formulário de desdobramento existem no JSON"

    validator.check("DataFields do formulário de desdobramento", check_desdobramento_fields)

    def check_forms_queue_contract(findings: list[str]) -> str:
        expected_cards = {
            "forms_correlacao_id": "varDdFormsCorrelacaoForm",
            "forms_envio_id": "varDdFormsEnvioForm",
        }
        for field_name, variable_name in expected_cards.items():
            cards = form_fields.get(field_name, [])
            if len(cards) != 1:
                findings.append(
                    f"campo {field_name!r} deve ter exatamente um DataCard; encontrado(s): {len(cards)}"
                )
                continue
            properties = cards[0][2].get("Properties") or {}
            if variable_name not in str(properties.get("Update", "")):
                findings.append(
                    f"DataCard {field_name!r} não grava {variable_name}"
                )

        new_button = main_controls.get("btnDdNovo", {})
        new_formula = str((new_button.get("Properties") or {}).get("OnSelect", ""))
        for token in ("varDdFormsCorrelacaoForm: Text(GUID())", "varDdFormsEnvioForm: Blank()"):
            if token not in new_formula:
                findings.append(f"btnDdNovo.OnSelect sem {token!r}")

        save_button = main_controls.get("btnDdSalvarForm", {})
        save_formula = str((save_button.get("Properties") or {}).get("OnSelect", ""))
        for token in (
            "varDdFormsCorrelacaoForm: Coalesce(",
            "varDdFormsEnvioForm: If(",
            'varFluxoForm: _fluxo',
            '_fluxo = "FLUXO III" && _envioFalhou',
        ):
            if token not in save_formula:
                findings.append(f"btnDdSalvarForm.OnSelect sem contrato Forms {token!r}")

        toolbar = main_controls.get("tbDdAcoes", {})
        toolbar_formula = str((toolbar.get("Properties") or {}).get("OnSelect", ""))
        for token in (
            "forms_correlacao_id: Coalesce(",
            "forms_envio_id: Text(GUID())",
            "data_envio_terceiro: Blank()",
            '_registroBase.status <> "Aguardando Terceiro"',
        ):
            if token not in toolbar_formula:
                findings.append(f"tbDdAcoes.OnSelect sem contrato de reenvio {token!r}")
        return "correlação estável e nova intenção idempotente por envio/reenvio"

    validator.check("Contrato da fila Microsoft Forms", check_forms_queue_contract)

    def check_phase2_screen_guards(findings: list[str]) -> str:
        # A fonte do perfil é conferida no grupo "Perfil Compliance".
        for unsupported_identity in (
            "userRecord",
            "LookUp(User, ID = varIdUser, Area)",
            "varIdUser",
            "varFuncaoUser",
            "varPerfilUser",
        ):
            if unsupported_identity in main_yaml_text:
                findings.append(
                    "ScreenDueDiligence depende de identidade não comprovada no app: "
                    f"{unsupported_identity!r}"
                )

        summary = main_controls.get("HtmlText1", {})
        summary_formula = str((summary.get("Properties") or {}).get("HtmlText", ""))
        for token in (
            "_gatilhoTerceiro:",
            "varRegistroDueDiligence.terceiro_gatilho_risco",
            "_gatilhoDD || _gatilhoTerceiro",
            "RESPOSTAS DO TERCEIRO",
            "_qtdRespostasTerceiro:",
            "_qtdRiscoAltoTerceiro:",
            "SITUAÇÃO DA ANÁLISE",
            "varRegistroDueDiligence.responsavel_compliance_email",
        ):
            if token not in summary_formula:
                findings.append(f"HtmlText1.HtmlText não contém o resumo operacional obrigatório: {token!r}")

        for obsolete_label in (
            "PONTUAÇÃO DO CONTRATO",
            "FLUXO / TRATAMENTO",
        ):
            if obsolete_label in summary_formula:
                findings.append(
                    f"HtmlText1.HtmlText ainda exibe o cartão removido: {obsolete_label!r}"
                )

        toolbar = main_controls.get("tbDdAcoes", {})
        toolbar_properties = toolbar.get("Properties") or {}
        toolbar_formula = str(toolbar_properties.get("OnSelect", ""))
        toolbar_items = str(toolbar_properties.get("Items", ""))
        compact_items = re.sub(r"\s+", " ", toolbar_items)
        compact_formula = re.sub(r"\s+", " ", toolbar_formula)
        if "varDdPodeAnalisarCompliance" not in toolbar_items:
            findings.append("tbDdAcoes.Items não protege a análise pelo perfil Compliance")
        for token in (
            '"Pendente Compliance", !varDdPodeAnalisarCompliance',
            '"Aguardando Terceiro", !(varDdPodeAnalisarCompliance || _envioFalhou)',
        ):
            if token not in compact_items:
                findings.append(f"tbDdAcoes.Items não mantém a regra de edição {token!r}")
        # Estados encerrados caem no padrão do Switch: edição sempre bloqueada.
        if not re.search(r"ItemDisabled: Switch\(.*?, true \),", compact_items):
            findings.append("tbDdAcoes.Items deve bloquear a edição dos estados encerrados por padrão")
        for token in (
            '"Pendente Compliance", varDdPodeAnalisarCompliance',
            '"Aguardando Terceiro", varDdPodeAnalisarCompliance || _envioFalhou',
            "_envioFalhou, EditForm(frmDdSolicitante), ViewForm(frmDdSolicitante)",
        ):
            if token not in compact_formula:
                findings.append(f"tbDdAcoes.OnSelect não reaplica a regra de edição {token!r}")

        responses = main_controls.get("htmlDdRespostasTerceiro", {})
        responses_formula = str((responses.get("Properties") or {}).get("HtmlText", ""))
        for token in (
            "tb_dueDiligenceTerceiroRespostas",
            "forms_envio_id = varRegistroDueDiligence.forms_envio_id",
            "R.classificacao",
            "R.resposta",
        ):
            if token not in responses_formula:
                findings.append(
                    f"htmlDdRespostasTerceiro não apresenta o contrato de resposta: {token!r}"
                )

        history = main_controls.get("galDdHistorico", {})
        history_formula = str((history.get("Properties") or {}).get("Items", ""))
        if not all(
            token in history_formula
            for token in ("varDdPodeAnalisarCompliance", "visivel_solicitante = 1")
        ):
            findings.append(
                "galDdHistorico não separa histórico interno do histórico público"
            )
        if "htmlDdHistoricoItem" not in main_controls or "attDdHistoricoItem" not in main_controls:
            findings.append("galDdHistorico sem os itens htmlDdHistoricoItem/attDdHistoricoItem")

        analysis_form = main_controls.get("frmDdDesdobramento", {})
        success_formula = str((analysis_form.get("Properties") or {}).get("OnSuccess", ""))
        for field_name in (
            "decisao_compliance",
            "condicionantes_compliance",
            "justificativa_compliance",
            "decisao_compliance_por_email",
            "data_decisao_compliance",
            "prazo_reavaliacao",
        ):
            if field_name not in success_formula:
                findings.append(
                    f"frmDdDesdobramento.OnSuccess não grava {field_name!r}"
                )

        register_button = main_controls.get("btnDdRegistrarDesdobramento", {})
        register_formula = str(
            (register_button.get("Properties") or {}).get("OnSelect", "")
        )
        for token in ("Parecer final", "Aprovado com Ressalvas", "dpDdPrazoResposta", "Cancelamento"):
            if token not in register_formula:
                findings.append(
                    f"btnDdRegistrarDesdobramento não valida a decisão: {token!r}"
                )

        # Decisão e cancelamento são atividades do Compliance: o registro de
        # desdobramento não pode ficar ao alcance de quem só edita a solicitação.
        panel = main_controls.get("cntDdDesdTitulo", {})
        if "varDdPodeAnalisarCompliance" not in str((panel.get("Properties") or {}).get("Visible", "")):
            findings.append("cntDdDesdTitulo: o registro de desdobramento deve ser exclusivo do Compliance")
        register_mode = str((register_button.get("Properties") or {}).get("DisplayMode", ""))
        if "varDdPodeAnalisarCompliance" not in register_mode:
            findings.append("btnDdRegistrarDesdobramento.DisplayMode não exige o perfil Compliance")
        if "_registroBase.status <> _desdobramento.status_anterior" not in success_formula:
            findings.append(
                "frmDdDesdobramento.OnSuccess não reverte quando o status mudou em paralelo"
            )
        save_button = main_controls.get("btnDdSalvarForm", {})
        save_mode = str((save_button.get("Properties") or {}).get("DisplayMode", ""))
        if "frmDdSolicitante.Mode = FormMode.View" not in save_mode:
            findings.append(
                "btnDdSalvarForm deve ficar desabilitado com o formulário em visualização "
                "(SubmitForm não roda e o overlay ficaria preso)"
            )
        return "respostas visíveis, análise autorizada, decisão persistida e histórico segregado"

    validator.check("Guardas visuais da Fase 2", check_phase2_screen_guards)

    def check_v2_contracts(findings: list[str]) -> str:
        main_yaml = main_yaml_text
        if not main_yaml:
            findings.append("ScreenDueDiligence.yaml ausente ou inválido")
            return ""

        if not re.search(
            r"versao_questionario\s*=\s*1\s*\|\|\s*versao_questionario\s*=\s*2",
            main_yaml,
        ):
            findings.append("filtro de parâmetros não contempla versões 1 e 2")

        for field_name, variable_name in RESULT_FIELDS.items():
            if field_name not in main_internal_names:
                findings.append(f"campo de resultado {field_name!r} ausente no JSON principal")
                continue
            cards = form_fields.get(field_name, [])
            if not cards:
                findings.append(f"campo de resultado {field_name!r} ausente no formulário principal")
                continue
            if not any(
                isinstance(card.get("Properties"), dict)
                and variable_name in str(card["Properties"].get("Update", ""))
                for _, _, card in cards
            ):
                findings.append(
                    f"campo de resultado {field_name!r} não grava a variável {variable_name}"
                )

        compact = re.sub(r"\s+", " ", main_yaml)
        band_pattern = re.compile(
            r'_faixaPontos:\s*If\(\s*_totalPontos\s*>=\s*36,\s*"Alto",\s*'
            r'If\(\s*_totalPontos\s*>=\s*16,\s*"Médio",\s*"Baixo"\s*\)\s*\)'
        )
        if not band_pattern.search(compact):
            findings.append("faixas v2 devem ser Alto >= 36, Médio >= 16 e Baixo abaixo de 16")

        flow_pattern = re.compile(
            r'_fluxo:\s*If\(\s*'
            r'_gatilhoDD,\s*"FLUXO III",\s*'
            r'_obrigacaoLegal,\s*"FLUXO I",\s*'
            r'_classificacaoContraparte\s*=\s*"FLUXO II",\s*"FLUXO II",\s*'
            r'_classificacaoContraparte\s*=\s*"ALTO",\s*"FLUXO III",\s*'
            r'_classificacaoContraparte\s*=\s*"SEM RISCO",\s*"FLUXO I",\s*'
            r'_classificacaoContraparte\s*=\s*"PONTUAR",\s*'
            r'If\(\s*_faixaPontos\s*=\s*"Baixo",\s*"FLUXO I",\s*"FLUXO III"\s*\)'
        )
        if not flow_pattern.search(compact):
            findings.append(
                "prioridade de fluxo v2 divergente: gatilho DD > obrigação legal > "
                "classificação FLUXO II/ALTO/SEM RISCO/PONTUAR"
            )
        return "filtro v1/v2, resultados, faixas 16/36 e prioridades preservados"

    validator.check("Contratos centrais v2", check_v2_contracts)

    def check_status_model(findings: list[str]) -> str:
        for path, text in yaml_texts.items():
            for legacy in LEGACY_STATUSES:
                for match in re.finditer(re.escape(f'"{legacy}"'), text):
                    line = text.count("\n", 0, match.start()) + 1
                    findings.append(f"{display(path)}:{line}: status legado {legacy!r}")
            for match in re.finditer(r'\bstatus(?:_novo|_anterior)?:\s*"([^"]*)"', text):
                if match.group(1) not in CANONICAL_STATUSES:
                    line = text.count("\n", 0, match.start()) + 1
                    findings.append(
                        f"{display(path)}:{line}: grava status fora do modelo {match.group(1)!r}"
                    )

        flow_texts: dict[str, str] = {}
        for path in READY_FLOW_FILES:
            try:
                with zipfile.ZipFile(path) as archive:
                    name = next(n for n in archive.namelist() if n.endswith("/definition.json"))
                    flow_texts[display(path)] = archive.read(name).decode("utf-8")
            except (OSError, zipfile.BadZipFile, StopIteration):
                continue  # o check dos pacotes já informa o detalhe
        for path in sorted((BASE / "PowerAutomate").glob("*.json")):
            flow_texts[display(path)] = path.read_text(encoding="utf-8")
        for location, text in flow_texts.items():
            for legacy in LEGACY_STATUSES:
                if f"'{legacy}'" in text or f'"{legacy}"' in text:
                    findings.append(f"{location}: status legado {legacy!r}")
            try:
                document = json.loads(text)
            except json.JSONDecodeError as exc:
                findings.append(f"{location}: JSON inválido: {exc}")
                continue
            for key, value in iter_json_items(document):
                if (
                    key in ("status", "status_novo", "status_anterior")
                    and isinstance(value, str)
                    and not value.startswith("@")
                    and value not in CANONICAL_STATUSES
                ):
                    findings.append(f"{location}: {key} grava status fora do modelo: {value!r}")

        combo = main_controls.get("cmbDdFiltroStatus", {})
        items = str((combo.get("Properties") or {}).get("Items", ""))
        if tuple(re.findall(r'"([^"]*)"', items)) != CANONICAL_STATUSES:
            findings.append(
                f"cmbDdFiltroStatus.Items deve listar exatamente {list(CANONICAL_STATUSES)}"
            )
        return f"{len(CANONICAL_STATUSES)} status canônicos; nenhum legado nas telas e nos fluxos"

    validator.check("Modelo de status canônico", check_status_model)

    def check_history_dropdowns(findings: list[str]) -> str:
        tipo = main_controls.get("cmbDdTipoDesdobramento", {})
        tipo_items = str((tipo.get("Properties") or {}).get("Items", ""))
        offered = set(re.findall(r'"([^"]*)"', tipo_items)) - {"Pendente Compliance"}
        if offered != set(MANUAL_HISTORY_TYPES):
            findings.append(
                f"cmbDdTipoDesdobramento.Items deve oferecer só {list(MANUAL_HISTORY_TYPES)}; "
                f"encontrado: {sorted(offered)}"
            )
        for removed in REMOVED_HISTORY_TYPES:
            if f'"{removed}"' in tipo_items:
                findings.append(f"cmbDdTipoDesdobramento.Items ainda oferece {removed!r}")
        branches = [
            re.findall(r'"([^"]*)"', group) for group in re.findall(r"\[([^\]]*)\]", tipo_items)
        ]
        if len(branches) != 2 or "Parecer final" not in branches[0] or "Parecer final" in branches[1]:
            findings.append("Parecer final só pode ser oferecido em Pendente Compliance")

        status_combo = main_controls.get("cmbDdDesdStatusNovo", {})
        status_items = str((status_combo.get("Properties") or {}).get("Items", ""))
        offered_status = set(re.findall(r'"([^"]*)"', status_items)) - {"Parecer final", "Cancelamento"}
        if offered_status != set(DECISION_STATUSES) | {"Cancelado"}:
            findings.append(
                "cmbDdDesdStatusNovo.Items deve oferecer só as decisões e Cancelado; "
                f"encontrado: {sorted(offered_status)}"
            )
        compact_status = re.sub(r"\s+", " ", status_items)
        for token in (
            "!varDdPodeAnalisarCompliance, [varRegistroDueDiligence.status]",
            "cmbDdTipoDesdobramento.Selected.Value",
        ):
            if token not in compact_status:
                findings.append(f"cmbDdDesdStatusNovo.Items sem {token!r}")
        return "tipos manuais enxutos; status do desdobramento derivado do tipo e restrito ao Compliance"

    validator.check("Dropdowns de desdobramento", check_history_dropdowns)

    def check_validity_rule(findings: list[str]) -> str:
        cards = form_fields.get("data_vencimento", [])
        if len(cards) != 1:
            findings.append(
                f"data_vencimento deve ter exatamente um DataCard; encontrado(s): {len(cards)}"
            )
        else:
            update = re.sub(r"\s+", " ", str((cards[0][2].get("Properties") or {}).get("Update", "")))
            for token in (
                VALIDITY_RULE_POWERFX,
                "TimeUnit.Years",
                'varFluxoForm = "FLUXO I" || varFluxoForm = "FLUXO II"',
            ):
                if token not in update:
                    findings.append(f"DataCard de data_vencimento sem {token!r}")
        analysis_form = main_controls.get("frmDdDesdobramento", {})
        success = re.sub(
            r"\s+", " ", str((analysis_form.get("Properties") or {}).get("OnSuccess", ""))
        )
        match = re.search(r"data_vencimento: If\( _statusNovo in \[([^\]]*)\]", success)
        if not match or tuple(re.findall(r'"([^"]*)"', match.group(1))) != VALIDITY_STATUSES:
            findings.append(
                f"frmDdDesdobramento.OnSuccess deve abrir vigência só para {list(VALIDITY_STATUSES)}"
            )
        if VALIDITY_RULE_POWERFX not in success or "TimeUnit.Years" not in success:
            findings.append("frmDdDesdobramento.OnSuccess sem a regra de vigência 1/2/3 anos")
        return "vigência 1/2/3 anos por risco no cadastro automático e no parecer"

    validator.check("Regra de vigência", check_validity_rule)

    def check_dashboard(findings: list[str]) -> str:
        text = yaml_texts.get(PANEL_FILE, "")
        document = yaml_documents.get(PANEL_FILE)
        if not text or not isinstance(document, dict):
            findings.append(f"{display(PANEL_FILE)} ausente ou inválido")
            return ""
        screen = next(iter(document["Screens"].values()))
        controls = dict(iter_controls(screen.get("Children")))
        on_visible = str((screen.get("Properties") or {}).get("OnVisible", ""))
        refresh = str(
            (controls.get("btnDdPainelAtualizar", {}).get("Properties") or {}).get("OnSelect", "")
        )

        # Navigate para a própria tela não reexecuta o OnVisible: o botão repete a carga.
        def without_comments(formula: str) -> list[str]:
            return re.sub(r"//[^\n]*", "", formula).split()

        if not on_visible or without_comments(on_visible) != without_comments(refresh):
            findings.append("OnVisible e btnDdPainelAtualizar.OnSelect têm que ser a mesma carga")
        if on_visible.rfind("varDdPainelCarregando: false") < on_visible.rfind("FirstError"):
            findings.append("a carga não libera varDdPainelCarregando depois do tratamento de erro")

        queries = 0
        for match in re.finditer(r"Filter\(\s*tb_dueDiligence\b", on_visible):
            arguments = balanced_call(on_visible, match.start() + len("Filter"))
            queries += 1
            if "ativo = 1" not in arguments:
                findings.append("consulta a tb_dueDiligence sem ativo = 1")
            for token in (" in ", "IsBlank(", "Search(", "Len(", "Lower(", "Upper(", "Trim("):
                if token in arguments:
                    findings.append(
                        f"consulta a tb_dueDiligence com operação não delegável {token.strip()!r}"
                    )
        if queries != 3:
            findings.append(f"esperadas 3 consultas delegáveis a tb_dueDiligence; encontrada(s): {queries}")
        for status in VALIDITY_STATUSES + ("Vencido",):
            if f'status = "{status}"' not in on_visible:
                findings.append(f"consulta de vigências não inclui {status!r}")
        for literal in re.findall(r'status\s*(?:=|<>)\s*"([^"]+)"', text):
            if literal not in CANONICAL_STATUSES:
                findings.append(f"painel compara com status fora do modelo: {literal!r}")

        for match in re.finditer(r"\bDistinct\(", text):
            arguments = balanced_call(text, match.end() - 1)
            if not re.match(r"\s+As\s+\w+", text[match.end() + len(arguments) + 1:]):
                findings.append("Distinct sem alias As (a coluna devolvida é Value)")
        # Agregado sobre tabela vazia: Average devolve erro (não Blank) e o erro
        # atravessa a concatenação, apagando o cartão inteiro. Coalesce não o captura.
        if re.search(r"\bAverage\(", text):
            findings.append("Average sobre tabela vazia é erro; use If(_n = 0, Blank(), Sum(t, c) / _n)")
        table_names = set(
            re.findall(r"\b(_\w+):\s*(?:Sort|ForAll|Filter|FirstN|LastN|Distinct|Table)\(", text)
        )
        for match in re.finditer(r"\b(Max|Min|Sum)\(\s*(_\w+|col\w+)\s*,", text):
            name = match.group(2)
            if name.startswith("_") and name not in table_names:
                continue  # sobrecarga escalar, como Max(_total, 1)
            before = text[max(0, match.start() - 100):match.start()]
            count_guard = f"_n{name[1:2].upper()}{name[2:]} = 0" if name.startswith("_") else None
            if f"IsEmpty({name})" not in before and not (count_guard and count_guard in before):
                findings.append(f"{match.group(1)}({name}, …) sem proteção para tabela vazia")
        if re.search(r"\b(ShowColumns|RenameColumns|AddColumns|DropColumns|SortByColumns)\(", text):
            findings.append("painel usa função de colunas por nome; use ForAll e Sort")
        # No Power Apps o % do formato de Text() não multiplica por 100: 0,33 vira "0%".
        for path, screen_text in yaml_texts.items():
            if re.search(r'"[0#.,]+%"', screen_text):
                findings.append(
                    f'{display(path)}: Text(x, "0%") não multiplica por 100; '
                    'use Text(Round(x * 100, 0)) & "%"'
                )
        if re.search(r'"[#0,]*0[.,]0+"', text):
            findings.append("formato decimal em Text() depende do idioma; arredonde e use inteiro")

        parameters = (json_documents.get(PARAMETERS_LIST_FILE) or {}).get("registrosIniciais", [])
        for code in ("config_sla_terceiro_dias", "config_sla_compliance_dias"):
            if f'"{code}"' not in on_visible:
                findings.append(f"painel não lê o parâmetro {code}")
            if not any(
                isinstance(record, dict)
                and record.get("codigo_opcao") == code
                and record.get("ativo") == 1
                and isinstance(record.get("pontuacao"), (int, float))
                and record["pontuacao"] > 0
                for record in parameters
            ):
                findings.append(f"{display(PARAMETERS_LIST_FILE)} sem o parâmetro ativo {code}")

        main_nav = str((main_controls.get("btnDdPainel", {}).get("Properties") or {}).get("OnSelect", ""))
        if "ScreenDueDiligencePainel" not in main_nav:
            findings.append("a barra de abas da ScreenDueDiligence não leva ao painel")
        if "ScreenDueDiligencePainel" not in yaml_texts.get(BASE / "ScreenDueDiligenceInicio.yaml", ""):
            findings.append("a tela inicial não leva ao painel")

        # Dicionário de propriedades: só o que já foi visto num export real do repositório.
        if yaml is not None:
            dictionary: defaultdict[str, set[str]] = defaultdict(set)
            screen_properties: set[str] = set()
            for other in BASE.parent.rglob("*.yaml"):
                if other.resolve() == PANEL_FILE.resolve():
                    continue
                try:
                    other_document = yaml.load(
                        other.read_text(encoding="utf-8-sig"), Loader=PowerAppsSafeLoader
                    )
                except Exception:
                    continue
                screens = other_document.get("Screens") if isinstance(other_document, dict) else None
                if not isinstance(screens, dict):
                    continue
                for other_screen in screens.values():
                    if not isinstance(other_screen, dict):
                        continue
                    screen_properties.update((other_screen.get("Properties") or {}).keys())
                    for _, body in iter_controls(other_screen.get("Children")):
                        dictionary[str(body.get("Control"))].update(
                            (body.get("Properties") or {}).keys()
                        )
            unproven = [
                f"Screen.{name}"
                for name in (screen.get("Properties") or {})
                if name not in screen_properties
            ]
            for name, body in controls.items():
                properties = list((body.get("Properties") or {}).keys())
                unproven += [
                    f"{name}.{prop}"
                    for prop in properties
                    if prop not in dictionary.get(str(body.get("Control")), set())
                ]
                if properties != sorted(properties):
                    findings.append(f"{name}: propriedades fora da ordem alfabética do Studio")
            if unproven:
                findings.append(
                    "propriedades sem export comprovado no repositório: " + ", ".join(unproven)
                )
        return f"{len(controls)} controles, {queries} consultas delegáveis, carga espelhada"

    validator.check("Painel de indicadores", check_dashboard)

    def check_compliance_profile(findings: list[str]) -> str:
        columns = columns_by_name(json_documents.get(COMPLIANCE_LIST_FILE) or {})
        email = columns.get("email")
        if not isinstance(email, dict):
            findings.append(f"{display(COMPLIANCE_LIST_FILE)} sem a coluna email")
        else:
            field = ElementTree.fromstring(str(email.get("schemaXml", "")))
            for attribute in ("Required", "Indexed", "EnforceUniqueValues"):
                if field.attrib.get(attribute) != "TRUE":
                    findings.append(f"tb_dueDiligenceCompliance.email exige {attribute}='TRUE'")
        if "ativo" not in columns:
            findings.append(f"{display(COMPLIANCE_LIST_FILE)} sem a coluna ativo")

        for path in YAML_FILES:
            compact = re.sub(r"\s+", " ", yaml_texts.get(path, ""))
            for token in COMPLIANCE_ACCESS_TOKENS:
                if token not in compact:
                    findings.append(f"{display(path)}: regra do perfil Compliance sem {token!r}")

        def controls_of(path: Path) -> dict[str, dict[str, Any]]:
            document = yaml_documents.get(path)
            if not isinstance(document, dict):
                return {}
            screen = next(iter(document["Screens"].values()))
            return dict(iter_controls(screen.get("Children")))

        def visible(controls: dict[str, dict[str, Any]], name: str) -> str:
            return str((controls.get(name, {}).get("Properties") or {}).get("Visible", ""))

        restricted = 0
        for name in ("HtmlText1", "lblDdPontuacaoCab", "lblDdRiscoCab", "lblDdPontuacao", "lblDdRisco", "btnDdPainel"):
            restricted += 1
            if "varDdPodeAnalisarCompliance" not in visible(main_controls, name):
                findings.append(f"ScreenDueDiligence: {name}.Visible não restringe ao Compliance")
        inicio_controls = controls_of(BASE / "ScreenDueDiligenceInicio.yaml")
        restricted += 1
        if "varDdPodeAnalisarCompliance" not in visible(inicio_controls, "btnInicioDdPainel"):
            findings.append("ScreenDueDiligenceInicio: btnInicioDdPainel.Visible não restringe ao Compliance")
        panel_controls = controls_of(PANEL_FILE)
        restricted += 2
        if visible(panel_controls, "cntDdPainelCorpo") != '=varDdPainelAcesso = "sim"':
            findings.append('painel: cntDdPainelCorpo tem que exigir varDdPainelAcesso = "sim"')
        if visible(panel_controls, "htmDdPainelRestrito") != '=varDdPainelAcesso = "nao"':
            findings.append('painel: htmDdPainelRestrito tem que aparecer com varDdPainelAcesso = "nao"')
        panel_compact = re.sub(r"\s+", " ", yaml_texts.get(PANEL_FILE, ""))
        if 'varDdPainelAcesso <> "sim", Clear(colDdPainel);' not in panel_compact:
            findings.append("painel: a carga não limpa os dados quando o usuário não é do Compliance")
        return f"perfil pela lista tb_dueDiligenceCompliance, falha fechada, {restricted} itens restritos"

    validator.check("Perfil Compliance", check_compliance_profile)

    print()
    if validator.errors:
        print(
            f"RESULTADO: FALHA — {len(validator.errors)} erro(s) em "
            f"{validator.failed} grupo(s); {validator.passed} grupo(s) passaram."
        )
        return 1
    print(f"RESULTADO: OK — {validator.passed} grupo(s) de validação passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
