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
    BASE / "NotificarstatusDueDiligence_PRONTO.zip",
)
LAUDO_READY_FILE = BASE / "GerarLaudoDueDiligence_PRONTO.zip"
NOTIFY_READY_FILE = READY_FLOW_FILES[3]
# DD05: chaves de Montar_Campos e colunas que só o e-mail do Compliance pode usar
# (risco, pontuação e gatilhos são do perfil Compliance no app).
NOTIFY_SENSITIVE_TOKENS = (
    "['classificacao_risco']",
    "['risco_final']",
    "['pontuacao']",
    "['pontuacao_total']",
    "['pontuacao_solicitante']",
    "['gatilho_dd']",
    "['terceiro_risco_alto']",
    "['terceiro_gatilho_risco']",
)
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
# O SharePoint guarda no máximo 32 caracteres de nome interno e corta o excedente sem
# avisar. O DataField do Power Apps usa o nome interno: com o nome inteiro, o campo
# simplesmente não é gravado (2026-09-16).
SHAREPOINT_INTERNAL_NAME_LIMIT = 32
# Colunas criadas antes dessa regra; na lista real o nome interno já está cortado.
LEGACY_LONG_INTERNAL_NAMES = frozenset({
    "gatilho_representacao_orgao_publico",
    "gatilho_indicado_funcionario_publico",
})


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
    return scan_powerfx_literals(formula)[0]


def scan_powerfx_literals(formula: str) -> tuple[str, str | None]:
    """Devolve a fórmula mascarada e a aspa que ficou aberta no fim (ou None)."""
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
    return "".join(output), quote


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
        notify_text = json.dumps(definitions[READY_FLOW_FILES[3]], ensure_ascii=False)
        if "PREENCHER_" in combined + expiry_text + notify_text:
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
        # Aprovação automática depois da resposta (2026-09-16): risco baixo ou médio,
        # sem gatilho crítico e sem resposta de risco alto; o resto vai ao Compliance.
        for token in (
            "not(variables('varTerceiroAlto'))",
            "['gatilho_dd'], '')))), 'sim'))",
            "contains(createArray('baixo', 'médio', 'medio')",
            "\"status\": \"@if(outputs('Avaliar_Aprovacao_Automatica'), 'Aprovado', 'Pendente Compliance')\"",
            "\"status_novo\": \"@if(outputs('Avaliar_Aprovacao_Automatica'), 'Aprovado', 'Pendente Compliance')\"",
            "\"data_vencimento\": \"@if(outputs('Avaliar_Aprovacao_Automatica'), concat(formatDateTime(addToTime(",
            "\"data_conclusao\": \"@if(outputs('Avaliar_Aprovacao_Automatica'), utcNow(), null)\"",
            "risco_final,gatilho_dd,",
        ):
            if token not in process_text:
                findings.append(f"DD02 sem a regra de aprovação automática pós-resposta: {token!r}")
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
        return f"{len(definitions)} pacotes íntegros, correlacionados e sem placeholders"

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
                        clean, open_quote = scan_powerfx_literals(child)
                        if open_quote:
                            # Texto sem a aspa final: em geral, fórmula truncada pelo YAML.
                            findings.append(
                                f"{file_name}: {child_location}: literal {open_quote} não fechado"
                            )
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
        return f"{total} fórmula(s) com (), [], {{}} e aspas balanceados"

    validator.check("Delimitadores Power Fx balanceados", check_formula_delimiters)

    def check_nested_iferror(findings: list[str]) -> str:
        # IfError(Patch(...), Notify(...)) mistura Record e Boolean. O Studio aceita
        # quando o IfError é elo de uma cadeia ';' (ou corpo de With), mas recusa como
        # valor de um ramo de If/Switch: "Tipo de argumento inválido (Boolean).
        # Esperando um valor Record". Nesses ramos, usar If(IsError(Patch(...)), ...).
        checked = 0

        def enclosing_call(masked: str, position: int) -> str:
            depth = 0
            index = position - 1
            while index >= 0:
                char = masked[index]
                if char == ")":
                    depth += 1
                elif char == "(":
                    if depth == 0:
                        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", masked[:index])
                        return match.group(1) if match else ""
                    depth -= 1
                index -= 1
            return ""

        def walk(value: Any, location: str, file_name: str) -> None:
            nonlocal checked
            if isinstance(value, dict):
                for key, child in value.items():
                    child_location = f"{location}.{key}" if location else str(key)
                    if isinstance(child, str) and child.startswith("=") and "IfError(" in child:
                        masked = strip_powerfx_literals_and_comments(child)
                        for match in re.finditer(r"\bIfError\(", masked):
                            checked += 1
                            before = masked[: match.start()].rstrip()
                            if not before.endswith(","):
                                continue
                            if enclosing_call(masked, match.start()) not in ("If", "Switch"):
                                continue
                            first_argument = masked[match.end():].lstrip()
                            if re.match(r"(Patch|Remove|Collect|ClearCollect)\s*\(", first_argument):
                                findings.append(
                                    f"{file_name}: {child_location}: IfError({first_argument.split('(')[0]}(...)) "
                                    "como valor de ramo de If/Switch; use If(IsError(...), ...)"
                                )
                    walk(child, child_location, file_name)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{location}[{index}]", file_name)

        for path, document in yaml_documents.items():
            walk(document, "", display(path))
        return f"{checked} IfError(s) conferido(s), nenhum com Record x Boolean em ramo de If/Switch"

    validator.check("IfError aninhado com tipos compatíveis", check_nested_iferror)

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
        property_line = re.compile(r"^\s+[A-Za-z][A-Za-z0-9_.]*:\s+(=.*)$")
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
                # Espaço + '#' abre comentário YAML: o Studio corta a fórmula ali
                # (ex.: "border:1px dashed #d1d5db" colou sem o resto e sem as aspas).
                if re.search(r"[ \t]#", match.group(1)):
                    findings.append(
                        f"{display(path)}:{line_number}: ' #' em fórmula Power Fx inline vira comentário "
                        "YAML e trunca a fórmula; use bloco '|-'"
                    )
        return f"{total} fórmula(s) inline sem ': ' e sem ' #'"

    validator.check("Power Fx inline sem ': ' nem ' #'", check_inline_colon)

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
        # "Minhas solicitações" (2026-09-16): a condição do autor entra como ramificação,
        # nunca como "!_minhas || ..." dentro do Filter.
        for token in ("_minhas: togDdMinhasSolicitacoes.Checked", "_email: User().Email", "If( _minhas,"):
            if token not in re.sub(r"\s+", " ", items):
                findings.append(f"galDdRegistros.Items sem o filtro Minhas solicitações {token!r}")
        filters = [
            balanced_call(items, match.start() + len("Filter"))
            for match in re.finditer(r"Filter\(\s*tb_dueDiligence\b", items)
        ]
        if len(filters) != 12:
            findings.append(f"galDdRegistros.Items deve ter 12 Filter delegáveis; encontrado(s): {len(filters)}")
        author_filters = sum("'Criado por'.Email = _email" in body for body in filters)
        if author_filters != 6:
            findings.append(f"metade dos Filter deve restringir ao autor; encontrado(s): {author_filters}")
        for body in filters:
            for token in ("IsBlank(", "_minhas", "!"):
                if token in body:
                    findings.append(f"Filter da galeria com operação não delegável {token!r}")
                    break
        clear = str((main_controls.get("btnDdLimparFiltros", {}).get("Properties") or {}).get("OnSelect", ""))
        if "Reset(togDdMinhasSolicitacoes)" not in clear:
            findings.append("btnDdLimparFiltros não limpa o filtro Minhas solicitações")
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
        # A solicitação é editável até a resposta do terceiro (2026-09-15); depois
        # dela o status pertence ao DD02 e ao Compliance e não é recalculado.
        if "IsBlank(_statusAtual) || _antesDaResposta" not in compact:
            findings.append(
                "status_DataCard.Update só pode recalcular registro novo ou ainda sem resposta do terceiro"
            )
        for token in (
            'ThisItem.status = "Aguardando Terceiro"',
            "IsBlank(ThisItem.data_resposta_terceiro)",
            'varFluxoForm = "FLUXO I"',
        ):
            if token not in compact:
                findings.append(f"status_DataCard.Update sem o critério {token!r}")
        if "FLUXO II" in compact:
            findings.append("status_DataCard.Update não pode aprovar o Fluxo II: só o risco baixo automático dispensa o Forms")
        literals = set(re.findall(r'"([^"]*)"', update)) - {"", "FLUXO I"}
        # Pendente Compliance direto só no órgão público sem questionário (2026-09-18).
        if literals != {"Aguardando Terceiro", "Aprovado", "Pendente Compliance"}:
            findings.append(
                "status_DataCard.Update deve resultar só em Aprovado, Pendente Compliance "
                f"(órgão público sem questionário) ou Aguardando Terceiro; literais: {sorted(literals)}"
            )
        if '_versao = 2 && varDdSemQuestionarioForm, "Pendente Compliance",' not in compact:
            findings.append("status_DataCard.Update: Pendente Compliance só pelo caminho sem questionário")
        return "status recalculado na criação e em qualquer edição antes da resposta do terceiro"

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

    def check_status_notifications(findings: list[str]) -> str:
        """DD05 (2026-09-17): solicitante avisado a cada mudança de status e
        Compliance avisado em Pendente Compliance, com marcador status_notificado."""
        label = display(NOTIFY_READY_FILE)
        try:
            with zipfile.ZipFile(NOTIFY_READY_FILE) as archive:
                name = next(n for n in archive.namelist() if n.endswith("/definition.json"))
                document = json.loads(archive.read(name))
                manifest = json.loads(archive.read("manifest.json"))
            with zipfile.ZipFile(READY_FLOW_FILES[0]) as archive:
                name = next(n for n in archive.namelist() if n.endswith("/definition.json"))
                send_document = json.loads(archive.read(name))
        except (OSError, zipfile.BadZipFile, StopIteration, json.JSONDecodeError) as exc:
            findings.append(f"{label}: pacote inválido: {exc}")
            return ""

        flows = [r for r in manifest["resources"].values() if r["type"] == "Microsoft.Flow/flows"]
        if [r.get("suggestedCreationType") for r in flows] != ["New"]:
            findings.append(f"{label}: deve ser importado como fluxo novo (suggestedCreationType=New)")
        properties = document.get("properties") or {}
        if set(properties.get("connectionReferences") or {}) != {
            "shared_sharepointonline",
            "shared_office365",
        }:
            findings.append(f"{label}: conexões esperadas são SharePoint e Office 365 Outlook")

        def locate(actions: Any, name: str, path: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
            found: list[tuple[str, ...]] = []
            if not isinstance(actions, dict):
                return found
            for action_name, action in actions.items():
                if not isinstance(action, dict):
                    continue
                here = path + (action_name,)
                if action_name == name:
                    found.append(here)
                found += locate(action.get("actions"), name, here)
                found += locate((action.get("else") or {}).get("actions"), name, here)
            return found

        def action_at(actions: dict[str, Any], name: str) -> dict[str, Any] | None:
            paths = locate(actions, name)
            if len(paths) != 1:
                findings.append(f"{label}: esperado exatamente um {name}; encontrado(s): {len(paths)}")
                return None
            current: Any = {"actions": actions}
            for step in paths[0]:
                container = current.get("actions") or {}
                if step not in container:
                    container = (current.get("else") or {}).get("actions") or {}
                current = container[step]
            return current

        workflow = properties.get("definition") or {}
        actions = workflow.get("actions") or {}
        triggers = list((workflow.get("triggers") or {}).values())
        send_triggers = list(
            (((send_document.get("properties") or {}).get("definition") or {}).get("triggers") or {}).values()
        )
        if len(triggers) != 1 or len(send_triggers) != 1:
            findings.append(f"{label}: gatilho ausente no DD05 ou no DD01 de referência")
            return ""
        trigger = triggers[0]
        host = (trigger.get("inputs") or {}).get("host") or {}
        if host.get("operationId") != "GetOnUpdatedItems":
            findings.append(f"{label}: gatilho deve ser 'Quando um item é criado ou modificado'")
        if (trigger.get("inputs") or {}).get("parameters") != (send_triggers[0].get("inputs") or {}).get("parameters"):
            findings.append(f"{label}: gatilho não aponta para a mesma lista tb_dueDiligence do DD01")
        conditions = trigger.get("conditions") or [{}]
        expression = conditions[0].get("expression", "") if isinstance(conditions[0], dict) else ""
        for token in ("triggerBody()?['status']", "triggerBody()?['status_notificado']", "not(equals("):
            if token not in expression:
                findings.append(f"{label}: condição do gatilho sem {token!r} (evita laço e aviso repetido)")

        reading = action_at(actions, "HTTP_Obter_Solicitacao")
        uri = json.dumps(reading, ensure_ascii=False) if reading else ""
        for token in ("status_notificado", "Author/EMail", "$expand=Author"):
            if token not in uri:
                findings.append(f"{label}: HTTP_Obter_Solicitacao sem {token!r}")
        guard = action_at(actions, "Condicao_Status_Pendente_De_Aviso")
        if guard and "['status_notificado']" not in json.dumps(guard.get("expression"), ensure_ascii=False):
            findings.append(f"{label}: sem a releitura que confere status_notificado antes de enviar")

        requester = action_at(actions, "Enviar_Email_Solicitante")
        catalog = action_at(actions, "Montar_Mensagens_Solicitante")
        if requester and catalog:
            parameters = (requester.get("inputs") or {}).get("parameters") or {}
            if "['Author']?['EMail']" not in str(parameters.get("emailMessage/To")):
                findings.append(f"{label}: e-mail do solicitante deve ir para o autor (Criado por)")
            requester_text = json.dumps([parameters, catalog.get("inputs")], ensure_ascii=False)
            for token in NOTIFY_SENSITIVE_TOKENS:
                if token in requester_text:
                    findings.append(f"{label}: e-mail do solicitante expõe {token} (exclusivo do Compliance)")
            messages = catalog.get("inputs") if isinstance(catalog.get("inputs"), dict) else {}
            if set(messages) != set(CANONICAL_STATUSES):
                findings.append(
                    f"{label}: mensagens do solicitante não cobrem os 8 status; "
                    f"faltam {sorted(set(CANONICAL_STATUSES) - set(messages))}"
                )

        compliance_paths = locate(actions, "Enviar_Email_Compliance")
        if len(compliance_paths) != 1 or "Condicao_Notificar_Compliance" not in compliance_paths[0]:
            findings.append(f"{label}: e-mail do Compliance deve existir só dentro de Condicao_Notificar_Compliance")
        notify_compliance = action_at(actions, "Condicao_Notificar_Compliance")
        if notify_compliance and "'Pendente Compliance'" not in json.dumps(
            notify_compliance.get("expression"), ensure_ascii=False
        ):
            findings.append(f"{label}: Compliance deve ser avisado só em Pendente Compliance")
        listing = action_at(actions, "HTTP_Listar_Compliance")
        listing_text = json.dumps(listing, ensure_ascii=False) if listing else ""
        for token in ("tb_dueDiligenceCompliance", "ativo eq 1"):
            if token not in listing_text:
                findings.append(f"{label}: destinatários do Compliance sem {token!r}")
        compliance_email = action_at(actions, "Enviar_Email_Compliance")
        if compliance_email and "Selecionar_Emails_Compliance" not in str(
            ((compliance_email.get("inputs") or {}).get("parameters") or {}).get("emailMessage/To")
        ):
            findings.append(f"{label}: e-mail do Compliance deve ir para a lista de analistas ativos")

        marker_paths = locate(actions, "Montar_Marcador")
        marker = action_at(actions, "Montar_Marcador")
        if marker and marker.get("inputs") != {"status_notificado": "@body('HTTP_Obter_Solicitacao')?['status']"}:
            findings.append(f"{label}: Montar_Marcador deve gravar só status_notificado com o status relido")
        if len(marker_paths) == 1 and "Condicao_Envios_Concluidos" not in marker_paths[0]:
            findings.append(f"{label}: o marcador só pode ser gravado depois dos envios (Condicao_Envios_Concluidos)")
        sends_ok = action_at(actions, "Condicao_Envios_Concluidos")
        sends_text = json.dumps(sends_ok.get("expression"), ensure_ascii=False) if sends_ok else ""
        for token in ("Condicao_Tem_Solicitante", "Condicao_Notificar_Compliance", "'Failed'"):
            if token not in sends_text:
                findings.append(f"{label}: Condicao_Envios_Concluidos sem {token!r}")

        def writes_status(value: Any) -> bool:
            if isinstance(value, dict):
                if value.get("type") == "Compose" and isinstance(value.get("inputs"), dict) and "status" in value["inputs"]:
                    return True
                return any(writes_status(child) for child in value.values())
            if isinstance(value, list):
                return any(writes_status(child) for child in value)
            return False

        if writes_status(actions):
            findings.append(f"{label}: o DD05 não pode gravar status, só status_notificado")

        main_document = json_documents.get(MAIN_LIST_FILE)
        columns = columns_by_name(main_document) if isinstance(main_document, dict) else {}
        if "status_notificado" not in columns:
            findings.append(f"{display(MAIN_LIST_FILE)}: coluna status_notificado ausente (marcador do DD05)")
        # O app não grava o marcador: um cartão com valor antigo reabriria avisos.
        if "status_notificado" in main_yaml_text:
            findings.append("ScreenDueDiligence.yaml: o app não pode ler nem gravar status_notificado")

        return "solicitante em toda mudança, Compliance em Pendente Compliance, marcador depois dos envios"

    validator.check("Notificações de mudança de status (DD05)", check_status_notifications)

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
        stored_names = {name[:SHAREPOINT_INTERNAL_NAME_LIMIT] for name in main_internal_names}
        for field_name, cards in sorted(form_fields.items()):
            locations = ", ".join(f"{display(path)}:{name}" for path, name, _ in cards)
            if len(field_name) > SHAREPOINT_INTERNAL_NAME_LIMIT:
                findings.append(
                    f"DataField {field_name!r} passa de {SHAREPOINT_INTERNAL_NAME_LIMIT} caracteres: o "
                    f"SharePoint guarda {field_name[:SHAREPOINT_INTERNAL_NAME_LIMIT]!r} e o campo não é gravado ({locations})"
                )
            elif field_name not in stored_names:
                findings.append(
                    f"DataField {field_name!r} não existe em {display(MAIN_LIST_FILE)} ({locations})"
                )
        return f"{len(form_fields)} DataField(s) do formulário principal existem no JSON, pelo nome interno gravado"

    validator.check("DataFields do formulário principal", check_data_fields)

    def check_internal_name_length(findings: list[str]) -> str:
        total = 0
        for path, document in json_documents.items():
            for column in document.get("colunas") or []:
                name = column.get("internalName") if isinstance(column, dict) else None
                if not isinstance(name, str):
                    continue
                total += 1
                if len(name) <= SHAREPOINT_INTERNAL_NAME_LIMIT:
                    continue
                if name not in LEGACY_LONG_INTERNAL_NAMES:
                    findings.append(
                        f"{display(path)}: internalName {name!r} tem {len(name)} caracteres; o SharePoint "
                        f"corta em {SHAREPOINT_INTERNAL_NAME_LIMIT} e o formulário não grava o campo"
                    )
                elif name in form_fields:
                    findings.append(
                        f"DataField {name!r} deve usar o nome interno gravado "
                        f"{name[:SHAREPOINT_INTERNAL_NAME_LIMIT]!r}"
                    )
        return (
            f"{total} nome(s) interno(s) com até {SHAREPOINT_INTERNAL_NAME_LIMIT} caracteres "
            f"(exceto {len(LEGACY_LONG_INTERNAL_NAMES)} legado(s), gravados pelo nome cortado)"
        )

    validator.check("Nomes internos do SharePoint com até 32 caracteres", check_internal_name_length)

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
            '_fluxo = "FLUXO III" && (_envioFalhou || _emailAlterado)',
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
        # Editar (qualquer usuário, até a resposta do terceiro) e Analisar (só o
        # Compliance) são ações separadas desde 2026-09-15: com um item só, o rótulo
        # virava "Analisar" para o Compliance e o Editar sumia.
        for token in (
            'ItemKey: "editar", ItemDisplayName: "Editar", ItemIconName: "Edit", ItemDisabled: !_antesDaResposta,',
            'ItemKey: "analisar", ItemDisplayName: "Analisar",',
            '"Pendente Compliance", !varDdPodeAnalisarCompliance',
            '"Aguardando Terceiro", !varDdPodeAnalisarCompliance',
            'ItemKey <> "analisar" || varDdPodeAnalisarCompliance',
            '_antesDaResposta: ThisItem.status = "Aguardando Terceiro" && IsBlank(ThisItem.data_resposta_terceiro)',
        ):
            if token not in compact_items:
                findings.append(f"tbDdAcoes.Items não mantém a regra de edição/análise {token!r}")
        # Estados encerrados caem no padrão do Switch: análise sempre bloqueada.
        if not re.search(r"ItemDisabled: Switch\(.*?, true \),", compact_items):
            findings.append("tbDdAcoes.Items deve bloquear a análise dos estados encerrados por padrão")
        edit_start = compact_formula.find('"editar", With(')
        analyze_start = compact_formula.find('"analisar", If(', edit_start)
        next_branch = compact_formula.find('"terceiro",', analyze_start)
        if min(edit_start, analyze_start, next_branch) < 0:
            findings.append("tbDdAcoes.OnSelect deve ter os ramos \"editar\" e \"analisar\" antes de \"terceiro\"")
        else:
            edit_branch = compact_formula[edit_start:analyze_start]
            analyze_branch = compact_formula[analyze_start:next_branch]
            for token in (
                '_antesDaResposta: ThisItem.status = "Aguardando Terceiro" && IsBlank(ThisItem.data_resposta_terceiro)',
                "If( !_antesDaResposta, Notify(",
                'varAcaoDueDiligence: "edit"',
                "EditForm(frmDdSolicitante)",
            ):
                if token not in edit_branch:
                    findings.append(f"tbDdAcoes.OnSelect, ramo editar, sem {token!r}")
            for forbidden in ("NewForm(frmDdDesdobramento)", "varDdPodeAnalisarCompliance"):
                if forbidden in edit_branch:
                    findings.append(f"tbDdAcoes.OnSelect, ramo editar, não deve depender de {forbidden!r}")
            for token in (
                '!varDdPodeAnalisarCompliance || !(ThisItem.status in ["Aguardando Terceiro", "Pendente Compliance"])',
                'varAcaoDueDiligence: "analisar"',
                "ViewForm(frmDdSolicitante)",
                "NewForm(frmDdDesdobramento)",
            ):
                if token not in analyze_branch:
                    findings.append(f"tbDdAcoes.OnSelect, ramo analisar, sem {token!r}")
            if "EditForm(frmDdSolicitante)" in analyze_branch:
                findings.append("tbDdAcoes.OnSelect, ramo analisar, deve abrir a solicitação só para leitura")

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
        panel_visible = str((panel.get("Properties") or {}).get("Visible", ""))
        if "varDdPodeAnalisarCompliance" not in panel_visible:
            findings.append("cntDdDesdTitulo: o registro de desdobramento deve ser exclusivo do Compliance")
        # O painel de análise só abre pela ação Analisar; Editar mostra só os dados.
        if 'varAcaoDueDiligence = "analisar"' not in panel_visible:
            findings.append('cntDdDesdTitulo.Visible deve depender de varAcaoDueDiligence = "analisar"')
        register_mode = str((register_button.get("Properties") or {}).get("DisplayMode", ""))
        if "varDdPodeAnalisarCompliance" not in register_mode:
            findings.append("btnDdRegistrarDesdobramento.DisplayMode não exige o perfil Compliance")
        if 'varAcaoDueDiligence = "analisar"' not in register_mode:
            findings.append('btnDdRegistrarDesdobramento.DisplayMode deve depender de varAcaoDueDiligence = "analisar"')
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

        # Gatilho crítico > risco baixo automático (obrigação legal, tipo de contrato
        # ou SEM RISCO) > todo o resto recebe o Forms. Toda ocorrência do motor precisa
        # seguir a regra: o resumo e o botão Salvar já divergiram sem o validador perceber.
        flow_pattern = re.compile(
            r'_fluxo:\s*If\(\s*'
            r'_gatilhoDD,\s*"FLUXO III",\s*'
            r'_obrigacaoLegal,\s*"FLUXO I",\s*'
            r'_contratoBaixoAutomatico,\s*"FLUXO I",\s*'
            r'_classificacaoContraparte\s*=\s*"SEM RISCO",\s*"FLUXO I",\s*'
            r'_classificacaoContraparte\s*in\s*\[\s*"FLUXO II",\s*"ALTO",\s*"PONTUAR"\s*\],\s*"FLUXO III",\s*'
            # Nunca vazio: fluxo "" gravava Aguardando Terceiro que o DD02 recusa (só aceita
            # FLUXO III) e a solicitação travava. Sem classificação, vai para análise.
            r'"FLUXO III"\s*\)'
        )
        occurrences = compact.count("_fluxo: If(")
        matches = len(flow_pattern.findall(compact))
        if occurrences < 2 or matches != occurrences:
            findings.append(
                "prioridade de fluxo v2 divergente: gatilho crítico > obrigação legal/SEM RISCO "
                f"(Fluxo I) > demais com Forms (Fluxo III); {matches} de {occurrences} ocorrência(s) conferem"
            )
        # Tipos de contrato "Risco Baixo automático" na aba Config da planilha, só com a
        # categoria do prefixo: o combo de tipo de contrato não é filtrado pela categoria.
        contract_rule = (
            '_contratoBaixoAutomatico: (dd_categoria_contraparte.Selected.codigo_opcao = "categoria_contraparte_01" && '
            'dd_tipo_contrato.Selected.codigo_opcao in ["tipo_contrato_11", "tipo_contrato_12", "tipo_contrato_13"]) || '
            '(dd_categoria_contraparte.Selected.codigo_opcao = "categoria_contraparte_03" && '
            'dd_tipo_contrato.Selected.codigo_opcao = "tipo_contrato_08")'
        )
        if compact.count(contract_rule) != occurrences:
            findings.append(
                "regra do tipo de contrato de risco baixo automático ausente ou divergente em "
                f"{occurrences - compact.count(contract_rule)} ocorrência(s) do motor"
            )
        for token in (
            '_obrigacaoLegal, "Sem risco (obrigação legal)", _contratoBaixoAutomatico, "Sem risco (tipo de contrato)",',
            '_obrigacaoLegal, "Baixo", _contratoBaixoAutomatico, "Baixo",',
        ):
            if token not in compact:
                findings.append(f"risco do Salvar sem a regra do tipo de contrato: {token!r}")
        return f"filtro v1/v2, resultados, faixas 16/36 e prioridade em {occurrences} ocorrência(s) do motor"

    validator.check("Contratos centrais v2", check_v2_contracts)

    def check_public_body_direct(findings: list[str]) -> str:
        # 2026-09-18: órgão público em convênio, termo de cooperação ou cessão de área nunca
        # recebe o Forms. Sem gatilho é risco baixo automático; com gatilho vai direto para
        # Pendente Compliance. Doação e patrocínio seguem com o Forms (risco alto).
        compact = re.sub(r"\s+", " ", main_yaml_text)
        regra = (
            '_orgaoSemQuestionario: dd_categoria_contraparte.Selected.codigo_opcao = "categoria_contraparte_01" && '
            'dd_tipo_contrato.Selected.codigo_opcao in ["tipo_contrato_11", "tipo_contrato_12", "tipo_contrato_13"]'
        )
        if compact.count(regra) != 2:
            findings.append(f"regra do órgão público sem questionário deve estar no resumo e no Salvar; encontrada {compact.count(regra)}x")
        for token in (
            'varDdSemQuestionarioForm: _fluxo = "FLUXO III" && _orgaoSemQuestionario,',
            'varDdFormsEnvioForm: If( _fluxo = "FLUXO III" && _orgaoSemQuestionario, Coalesce( varDdFormsEnvioForm, varRegistroDueDiligence.forms_envio_id ),',
            '"Ao salvar, segue direto para o Compliance"',
            'ThisItem.classificacao_contraparte = "FLUXO II" && ThisItem.tipo_contrato in ["Órgão público — Convênio", "Órgão público — Termo de cooperação", "Órgão público — Cessão de área"]',
        ):
            if token not in compact:
                findings.append(f"caminho do órgão público sem {token!r}")
        if compact.count("varDdSemQuestionarioForm: false") < 2:
            findings.append("varDdSemQuestionarioForm deve ser desligado com varFluxoForm")
        with zipfile.ZipFile(NOTIFY_READY_FILE) as archive:
            name = next(n for n in archive.namelist() if n.endswith("/definition.json"))
            notify_text = archive.read(name).decode("utf-8")
        if "O terceiro respondeu ao questionário e a solicitação está com o Compliance" in notify_text:
            findings.append("DD05: o aviso de Pendente Compliance não pode supor resposta do terceiro")
        return "convênio, termo de cooperação e cessão de área de órgão público sem Forms"

    validator.check("Órgão público sem questionário", check_public_body_direct)

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
        # Parecer final vale em Aguardando Terceiro e em Pendente Compliance: o Compliance
        # decide mesmo sem resposta do terceiro. O botão limita os dois status.
        if '"Parecer final"' not in tipo_items:
            findings.append("cmbDdTipoDesdobramento.Items deve oferecer Parecer final")
        register = main_controls.get("btnDdRegistrarDesdobramento", {})
        register_mode = re.sub(r"\s+", " ", str((register.get("Properties") or {}).get("DisplayMode", "")))
        if 'varRegistroDueDiligence.status in ["Aguardando Terceiro", "Pendente Compliance"]' not in register_mode:
            findings.append("btnDdRegistrarDesdobramento deve registrar só em Aguardando Terceiro e Pendente Compliance")

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
                'varFluxoForm = "FLUXO I"',
            ):
                if token not in update:
                    findings.append(f"DataCard de data_vencimento sem {token!r}")
            if "FLUXO II" in update:
                findings.append("DataCard de data_vencimento não pode abrir vigência automática no Fluxo II")
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

    def check_airport_block(findings: list[str]) -> str:
        combo = main_controls.get("cmbDdAeroporto", {})
        airports = re.findall(r'"([^"]*)"', str((combo.get("Properties") or {}).get("Items", "")))
        if "SEDE" not in airports:
            findings.append('cmbDdAeroporto.Items sem a opção "SEDE"')
        if "bloco" not in main_internal_names:
            findings.append("coluna 'bloco' ausente no JSON principal")
        cards = form_fields.get("bloco", [])
        if len(cards) != 1:
            findings.append(f"bloco deve ter exatamente um DataCard; encontrado(s): {len(cards)}")
            return ""
        update = str((cards[0][2].get("Properties") or {}).get("Update", ""))
        if "cmbDdAeroporto.Selected.Value" not in update:
            findings.append("DataCard de bloco não deriva do aeroporto selecionado")
        groups = [
            set(re.findall(r'"([^"]*)"', group)) for group in re.findall(r"\[([^\]]*)\]", update)
        ]
        mapped = set().union(*groups) if groups else set()
        if len(groups) != 2 or groups[0] & groups[1]:
            findings.append("DataCard de bloco deve ter duas listas disjuntas (CENTRAL e SUL)")
        unmapped = set(airports) - mapped - {"SEDE"}
        if unmapped:
            findings.append(f"aeroporto(s) sem bloco: {sorted(unmapped)}")
        if "SEDE" in mapped:
            findings.append("SEDE é corporativa e não pertence a bloco")
        return f"{len(airports)} opção(ões) de aeroporto; bloco derivado para {len(mapped)}"

    validator.check("Bloco do aeroporto", check_airport_block)

    def check_required_and_edit_guard(findings: list[str]) -> str:
        save_button = main_controls.get("btnDdSalvarForm", {})
        properties = save_button.get("Properties") or {}
        formula = str(properties.get("OnSelect", ""))
        compact = re.sub(r"\s+", " ", formula)
        required_controls = (
            "cmbDdAeroporto", "cmb_tipo_pessoa", "txt_cnpj_cpf", "txt_razao_social", "cmb_area_solicitante",
            "txt_objeto_contratacao", "dd_categoria_contraparte", "dd_fornecedor_tipo",
            "dd_cliente_tipo", "dd_tipo_contrato", "txt_valor_contrato", "dd_vigencia_contrato",
            "cmb_adiantamento", "cmb_success_fee", "dd_interacao_poder_publico",
            "cmb_gatilho_subcontratacao", "cmb_gatilho_procuracao", "cmb_gatilho_pagamento_em_nome",
            "cmb_gatilho_representacao_orgao_publico", "cmb_gatilho_indicado_funcionario_publico",
            "cmb_pagamento_obrigacao_legal", "dd_tipo_obrigacao_legal", "txt_email_terceiro",
        )
        start = formula.find("_faltando:")
        end = formula.find("_registroAtual:", start)
        block = formula[start:end] if start >= 0 and end > start else ""
        missing = [name for name in required_controls if f"{name}." not in block]
        if missing:
            findings.append(f"validação de obrigatórios do Salvar não cobre: {missing}")
        for token in (
            'UpdateContext({varDdMostrarObrigatorios: true}); Notify( "Preencha os campos destacados em vermelho: " & _faltando',
            # Rede de segurança: SubmitForm confere Valid antes de gravar; se reprovar
            # ali, não grava e pode não disparar OnFailure, prendendo overlay e trava.
            "!frmDdSolicitante.Valid,",
            "If(!IsBlank(varRegistroDueDiligence.ID), Refresh(tb_dueDiligence));",
            "LookUp(tb_dueDiligence, ID = varRegistroDueDiligence.ID)",
            # Edição concorrente: status, resposta do terceiro e reenvio do Forms.
            "_registroAtual.status <> varRegistroDueDiligence.status",
            "!IsBlank(_registroAtual.data_resposta_terceiro)",
            "_registroAtual.forms_envio_id <> varRegistroDueDiligence.forms_envio_id",
            "varDdRegistroLido: _registroAtual",
            '_envioFalhou: _registroAtual.status = "Aguardando Terceiro"',
            "_emailAlterado: !IsBlank(_registroAtual.ID)",
        ):
            if token not in compact:
                findings.append(f"btnDdSalvarForm.OnSelect sem {token!r}")
        lock_position = compact.find("varDdOcupadoDesde: Now()")
        for label, token in (
            ("a validação de obrigatórios", "_faltando"),
            ("a releitura do registro", "LookUp(tb_dueDiligence, ID = varRegistroDueDiligence.ID)"),
        ):
            if not 0 <= compact.find(token) < lock_position:
                findings.append(f"{label} deve vir antes de ocupar a trava de reentrância")
        if compact.find("Refresh(tb_dueDiligence));") > compact.find(
            "LookUp(tb_dueDiligence, ID = varRegistroDueDiligence.ID)"
        ):
            findings.append("o Refresh deve preceder a releitura do registro no Salvar")
        if "frmDdSolicitante.Valid" in str(properties.get("DisplayMode", "")):
            findings.append(
                "btnDdSalvarForm.DisplayMode não deve depender de Valid: o botão precisa "
                "estar ativo para listar os campos que faltam"
            )
        # O DD01 grava data_envio_terceiro enquanto o formulário pode estar aberto;
        # devolver o Default (lido na abertura) apagaria o envio já feito.
        cards = form_fields.get("data_envio_terceiro", [])
        if len(cards) != 1:
            findings.append(
                f"data_envio_terceiro deve ter exatamente um DataCard; encontrado(s): {len(cards)}"
            )
        else:
            update = re.sub(r"\s+", " ", str((cards[0][2].get("Properties") or {}).get("Update", "")))
            for token in (
                "varDdRegistroLido.ID <> ThisItem.ID",
                "varDdFormsEnvioForm <> varDdRegistroLido.forms_envio_id, Blank()",
                "varDdRegistroLido.data_envio_terceiro",
            ):
                if token not in update:
                    findings.append(f"DataCard de data_envio_terceiro sem {token!r}")
        return (
            f"{len(required_controls)} campo(s) obrigatório(s) conferidos no Salvar, releitura antes de "
            "gravar e data de envio preservada"
        )

    validator.check("Obrigatórios e edição até a resposta", check_required_and_edit_guard)

    def check_required_highlight(findings: list[str]) -> str:
        # Cada item da lista de obrigatórios do Salvar tem de aparecer no próprio card:
        # asterisco pelo Required, mensagem no rótulo de erro do formulário e borda
        # vermelha amarrada a essa mensagem. O aviso sozinho não diz onde está o campo.
        save_formula = str(
            (main_controls.get("btnDdSalvarForm", {}).get("Properties") or {}).get("OnSelect", "")
        )
        entries = re.findall(r'\{campo: "([^"]+)", vazio: (.+?)\},?\s*$', save_formula, flags=re.M)
        if not entries:
            findings.append("lista de obrigatórios do Salvar não localizada")
            return ""
        form = next((body for _, _, body in main_forms), None)
        cards = dict(iter_controls((form or {}).get("Children")))
        owner: dict[str, tuple[str, dict[str, Any]]] = {}
        for card_name, card in cards.items():
            if not str(card.get("Control", "")).startswith("TypedDataCard"):
                continue
            for child_name, child in iter_controls(card.get("Children")):
                owner[child_name] = (card_name, card)
        for campo, expression in entries:
            referenced = re.findall(r"\b((?:cmbDd|cmb_|txt_|dd_)[A-Za-z0-9_]+)\.", expression)
            if not referenced:
                findings.append(f"obrigatório {campo!r}: controle não identificado em {expression!r}")
                continue
            control = referenced[-1]
            if control not in owner:
                findings.append(f"obrigatório {campo!r}: {control} não está em um card do formulário")
                continue
            card_name, card = owner[control]
            children = dict(iter_controls(card.get("Children")))
            by_role = {child.get("MetadataKey"): (name, child) for name, child in children.items()}
            if "ErrorMessage" not in by_role or "FieldName" not in by_role:
                findings.append(f"{card_name}: sem rótulo de campo ou de erro para {campo!r}")
                continue
            err_name, err = by_role["ErrorMessage"]
            err_props = err.get("Properties") or {}
            err_visible = str(err_props.get("Visible", ""))
            for token in ("varDdMostrarObrigatorios", "Parent.Required", f"{control}.", "Parent.Error"):
                if token not in err_visible:
                    findings.append(f"{err_name}.Visible sem {token!r}")
            if not str(err_props.get("Text", "")).startswith("=Coalesce(Parent.Error,"):
                findings.append(f"{err_name}.Text deve mostrar Parent.Error ou a mensagem de obrigatório")
            control_props = children[control].get("Properties") or {}
            highlight = str(control_props.get("ValidationState", "")) + str(control_props.get("BorderColor", ""))
            if f"{err_name}.Visible" not in highlight:
                findings.append(f"{control}: destaque do campo não segue {err_name}.Visible")
            label_text = str((by_role["FieldName"][1].get("Properties") or {}).get("Text", ""))
            if 'If(Parent.Required, " *", "")' not in label_text:
                findings.append(f"{by_role['FieldName'][0]}: rótulo sem o asterisco de obrigatório")
        compact_save = re.sub(r"\s+", " ", save_formula)
        if compact_save.count("UpdateContext({varDdMostrarObrigatorios: true})") < 2:
            findings.append("btnDdSalvarForm deve ligar varDdMostrarObrigatorios nos dois avisos de pendência")
        resets = {
            "OnVisible": str(
                (next(iter((main_document or {}).get("Screens", {}).values()), {}).get("Properties") or {}).get("OnVisible", "")
            ),
            "btnDdNovo": str((main_controls.get("btnDdNovo", {}).get("Properties") or {}).get("OnSelect", "")),
            "btnDdCancelarForm": str(
                (main_controls.get("btnDdCancelarForm", {}).get("Properties") or {}).get("OnSelect", "")
            ),
            "frmDdSolicitante.OnSuccess": str(
                (main_controls.get("frmDdSolicitante", {}).get("Properties") or {}).get("OnSuccess", "")
            ),
        }
        for place, formula in resets.items():
            if "varDdMostrarObrigatorios: false" not in formula:
                findings.append(f"{place} não desliga varDdMostrarObrigatorios")
        toolbar = str((main_controls.get("tbDdAcoes", {}).get("Properties") or {}).get("OnSelect", ""))
        if toolbar.count("varDdMostrarObrigatorios: false") < 3:
            findings.append("tbDdAcoes.OnSelect deve desligar varDdMostrarObrigatorios em Ver, Editar e Analisar")
        return f"{len(entries)} obrigatório(s) com asterisco, mensagem e borda no próprio campo"

    validator.check("Destaque de obrigatórios por campo", check_required_highlight)

    def check_form_rows(findings: list[str]) -> str:
        # 2026-09-18: cartão oculto (Visible=false) com largura total na mesma linha (Y)
        # de cartões visíveis entra na quebra de linha do formulário: a Razão social,
        # em X=1 ao lado do Aeroporto, caiu para a linha de baixo na coluna esquerda.
        form = next((body for _, _, body in main_forms), None)
        cards = [
            (name, card.get("Properties") or {})
            for name, card in iter_controls((form or {}).get("Children"))
            if str(card.get("Control", "")).startswith("TypedDataCard")
        ]
        visiveis: dict[str, list[str]] = {}
        for name, props in cards:
            if str(props.get("Visible", "")).strip() != "=false":
                visiveis.setdefault(str(props.get("Y", "")), []).append(name)
        for name, props in cards:
            if str(props.get("Visible", "")).strip() == "=false" and str(props.get("Y", "")) in visiveis:
                findings.append(
                    f"{name} está oculto na linha {props.get('Y')} junto de {visiveis[str(props.get('Y'))]}; "
                    "mova-o para uma linha só de ocultos"
                )
        pares = sum(1 for nomes in visiveis.values() if len(nomes) == 2)
        return f"{pares} linha(s) com dois campos lado a lado, sem cartão oculto no meio"

    validator.check("Linhas do formulário sem cartão oculto", check_form_rows)

    def check_contract_value_format(findings: list[str]) -> str:
        # Valor digitado só com números e formatado ao sair do campo (250000 -> 250.000,00).
        # A leitura fixa pt-BR: Value() sem idioma usaria o do navegador e leria o ponto
        # de milhar como decimal para quem usa en-US.
        control = main_controls.get("txt_valor_contrato", {})
        props = control.get("Properties") or {}
        if str(props.get("TriggerOutput", "")) != "='TextInputCanvas.TriggerOutput'.FocusOut":
            findings.append("txt_valor_contrato deve formatar ao sair do campo (TriggerOutput FocusOut)")
        on_change = re.sub(r"\s+", " ", str(props.get("OnChange", "")))
        for token in ('Value(Trim(Self.Value), "pt-BR")', "varDdValorEditado: true", "varDdValorTexto:"):
            if token not in on_change:
                findings.append(f"txt_valor_contrato.OnChange sem {token!r}")
        value = re.sub(r"\s+", " ", str(props.get("Value", "")))
        if not value.startswith("=If( varDdValorEditado, varDdValorTexto,") or "Parent.Default" not in value:
            findings.append("txt_valor_contrato.Value deve mostrar o texto editado ou o valor do registro formatado")
        for formula in (on_change, value):
            if not all(token in formula for token in ('Text(RoundDown(_c / 100, 0), "0")', 'Text(Mod(_c, 100), "00")', '"."', '","')):
                findings.append("formatação do valor deve ser montada com os formatos \"0\"/\"00\" (independe do idioma)")
            if re.search(r'"[#0][#0.,]*[.,][#0]+"', formula):
                findings.append("formatação do valor não pode usar máscara de milhar/decimal de Text()")
        readings = re.findall(r"Value\(\s*(?:Trim\()?txt_valor_contrato\.Value\)?\s*(,\s*\"[^\"]+\")?\)", main_yaml_text)
        if not readings or any(language.replace(" ", "") != ',"pt-BR"' for language in readings):
            findings.append("toda leitura de txt_valor_contrato.Value deve usar Value(..., \"pt-BR\")")
        if main_yaml_text.count("varDdValorEditado: false") < 8:
            findings.append("varDdValorEditado deve ser desligado ao abrir, criar, cancelar e salvar")
        return f"{len(readings)} leitura(s) do valor em pt-BR; formatação ao sair do campo"

    validator.check("Valor do contrato formatado", check_contract_value_format)

    def check_document_mask(findings: list[str]) -> str:
        # 2026-09-17: o tipo de pessoa vem antes do documento e decide a máscara:
        # Pessoa Física só formata com 11 dígitos, Pessoa Jurídica só com 14, e
        # Estrangeiro fica como digitado. Tipo em branco (registro antigo) usa a contagem.
        props = main_controls.get("txt_cnpj_cpf", {}).get("Properties") or {}
        if str(props.get("TriggerOutput", "")) != "='TextInputCanvas.TriggerOutput'.FocusOut":
            findings.append("txt_cnpj_cpf deve formatar ao sair do campo (TriggerOutput FocusOut)")
        on_change = re.sub(r"\s+", " ", str(props.get("OnChange", "")))
        value = re.sub(r"\s+", " ", str(props.get("Value", "")))
        cpf = 'Left(_d, 3) & "." & Mid(_d, 4, 3) & "." & Mid(_d, 7, 3) & "-" & Mid(_d, 10, 2)'
        cnpj = 'Left(_d, 2) & "." & Mid(_d, 3, 3) & "." & Mid(_d, 6, 3) & "/" & Mid(_d, 9, 4) & "-" & Mid(_d, 13, 2)'
        for formula, rotulo in ((on_change, "OnChange"), (value, "Value")):
            for token in (
                "IsMatch(_c.Value, Match.Digit)",
                '_tipo: Coalesce(cmb_tipo_pessoa.Selected.Value, "")',
                '_tipo <> "Estrangeiro" && _tipo <> "Pessoa Jurídica" && Len(_d) = 11, ' + cpf,
                '_tipo <> "Estrangeiro" && _tipo <> "Pessoa Física" && Len(_d) = 14, ' + cnpj,
                '_tipo in ["Pessoa Física", "Pessoa Jurídica"] && !IsBlank(_d), _d,',
            ):
                if token not in formula:
                    findings.append(f"txt_cnpj_cpf.{rotulo} sem {token!r}")
        for token in ("varDdDocEditado: true", "varDdDocTexto:"):
            if token not in on_change:
                findings.append(f"txt_cnpj_cpf.OnChange sem {token!r}")
        if not value.startswith("=If( varDdDocEditado, varDdDocTexto,"):
            findings.append("txt_cnpj_cpf.Value deve mostrar o texto editado ou o documento do registro formatado")
        if main_yaml_text.count("varDdDocEditado: false") < 8:
            findings.append("varDdDocEditado deve ser desligado ao abrir, criar, cancelar e salvar")

        tipo = main_controls.get("cmb_tipo_pessoa", {}).get("Properties") or {}
        if re.findall(r'"([^"]*)"', str(tipo.get("Items", ""))) != ["Pessoa Jurídica", "Pessoa Física", "Estrangeiro"]:
            findings.append("cmb_tipo_pessoa.Items deve ser Pessoa Jurídica, Pessoa Física e Estrangeiro")
        tipo_change = re.sub(r"\s+", " ", str(tipo.get("OnChange", "")))
        for token in ('_tipo: Coalesce(Self.Selected.Value, "")', "varDdDocTexto:", "11, " + cpf, "14, " + cnpj):
            if token not in tipo_change:
                findings.append(f"cmb_tipo_pessoa.OnChange (refaz a máscara ao trocar o tipo) sem {token!r}")
        tipo_card = (main_controls.get("tipo_pessoa_DataCard", {}).get("Properties") or {})
        doc_card = (main_controls.get("cnpj_cpf_DataCard", {}).get("Properties") or {})
        if str(tipo_card.get("Required")) != "=true" or "Visible" in tipo_card:
            findings.append("tipo_pessoa_DataCard deve ser obrigatório e visível nas duas versões do questionário")
        if (str(tipo_card.get("X")), str(tipo_card.get("Y"))) != ("=0", "=1") or (
            str(doc_card.get("X")), str(doc_card.get("Y"))
        ) != ("=1", "=1"):
            findings.append("o tipo de pessoa deve ficar logo antes do documento (linha 1: tipo à esquerda, documento à direita)")
        err_text = str((main_controls.get("err_cnpj_cpf", {}).get("Properties") or {}).get("Text", ""))
        for token in ("Informe os 11 dígitos do CPF", "Informe os 14 dígitos do CNPJ"):
            if token not in err_text:
                findings.append(f"err_cnpj_cpf.Text sem {token!r}")
        save = re.sub(r"\s+", " ", str((main_controls.get("btnDdSalvarForm", {}).get("Properties") or {}).get("OnSelect", "")))
        for token in (
            '{campo: "Tipo de pessoa", vazio: IsBlank(cmb_tipo_pessoa.Selected.Value)}',
            '(cmb_tipo_pessoa.Selected.Value = "Pessoa Física" && Len(_d) <> 11) || '
            '(cmb_tipo_pessoa.Selected.Value = "Pessoa Jurídica" && Len(_d) <> 14)',
        ):
            if token not in save:
                findings.append(f"Salvar sem a conferência do documento pelo tipo: {token!r}")
        card = next(
            (card for _, _, card in form_fields.get("cnpj_cpf", []) if isinstance(card.get("Properties"), dict)),
            None,
        )
        if card and "Trim(txt_cnpj_cpf.Value)" not in str((card.get("Properties") or {}).get("Update", "")):
            findings.append("o cartão de cnpj_cpf deve gravar o texto do campo (já mascarado)")

        # A busca por número curto continua sendo por ID; com 11 ou 14 dígitos, o
        # documento é procurado nas duas máscaras, porque a lista guarda mascarado.
        gallery = re.sub(r"\s+", " ", str((main_controls.get("galDdRegistros", {}).get("Properties") or {}).get("Items", "")))
        for token in ("_buscaCnpj: With(", "_buscaCpf: With(", "IsNumeric(_busca) && Len(_busca) <= 6,"):
            if token not in gallery:
                findings.append(f"busca da galeria sem {token!r}")
        combinada = (
            "(StartsWith(razao_social, _busca) || StartsWith(cnpj_cpf, _busca) || "
            "StartsWith(cnpj_cpf, _buscaCnpj) || StartsWith(cnpj_cpf, _buscaCpf))"
        )
        if gallery.count(combinada) != gallery.count("StartsWith(razao_social, _busca)"):
            findings.append("toda busca por texto deve procurar o documento também nas duas máscaras")
        return "tipo de pessoa antes do documento, máscara pelo tipo e busca por dígitos ou máscara"

    validator.check("Máscara de CNPJ/CPF", check_document_mask)

    def check_automatic_approval_display(findings: list[str]) -> str:
        # Auditoria de 2026-09-16: aprovação automática aparecia como "AGUARDANDO" no resumo
        # e como pendente no laudo; categoria por texto podia deixar o fluxo vazio.
        if re.search(r'dd_categoria_contraparte\.Selected\.texto_opcao\s*=\s*"', main_yaml_text):
            findings.append("categoria da contraparte deve ser comparada pelo codigo_opcao, não pelo texto")
        summary = re.sub(r"\s+", " ", str((main_controls.get("HtmlText1", {}).get("Properties") or {}).get("HtmlText", "")))
        for token in (
            '_semQuestionario: If( varAcaoDueDiligence in ["new", "edit"], _fluxo = "FLUXO I" || _orgaoSemQuestionario, '
            'varRegistroDueDiligence.fluxo_classificacao in ["FLUXO I", "FLUXO II"] || _orgaoSemQuestionario )',
            '"NÃO SE APLICA"',
            '_fluxoInvalido:',
            'varRegistroDueDiligence.status = "Aguardando Terceiro", "Aguardando a resposta do terceiro"',
            'varRegistroDueDiligence.status in ["Aprovado", "Vencido"] && IsBlank(varRegistroDueDiligence.decisao_compliance)',
            'Coalesce(varRegistroDueDiligence.gatilho_dd, "Não") = "Sim"',
            'Coalesce(varRegistroDueDiligence.classificacao_contraparte, _classificacaoContraparte)',
        ):
            if token not in summary:
                findings.append(f"HtmlText1 (resumo) sem o tratamento de aprovação automática {token!r}")
        for stale in (
            'If(IsBlank(varRegistroDueDiligence.data_resposta_terceiro), "AGUARDANDO"',
            'If(IsBlank(varRegistroDueDiligence.data_resposta_terceiro), _situacaoEnvio',
        ):
            if stale in summary:
                findings.append(f"HtmlText1 ainda mostra AGUARDANDO sem considerar a aprovação automática: {stale!r}")
        toolbar = str((main_controls.get("tbDdAcoes", {}).get("Properties") or {}).get("OnSelect", ""))
        # Laudo (2026-09-17): lido pelo solicitante e pelo Compliance. Aprovação
        # automática tem seção própria com o critério, sem campos vazios do parecer;
        # sem questionário, a seção do terceiro some; histórico sem ruído técnico.
        for token in (
            '_automatica: ThisItem.status = "Aprovado" && IsBlank(ThisItem.decisao_compliance)',
            "\"<div class='lbl'>Aprovação automática</div>",
            "Dispensa a análise do Compliance, conforme a Norma de Avaliação de Riscos de Terceiros.",
            'ThisItem.risco_final = "Sem risco (tipo de contrato)"',
            "\"<div class='lbl'>Parecer do Compliance</div>",
            "If(IsBlank(_vigencia), \"\", \"<div class='validity'>",
            '_semQuestionario, "Não se aplica"',
            '"Falha no envio ao terceiro", "Solicitação de reenvio ao terceiro"',
            "If(IsBlank(ThisItem.prazo_reavaliacao), \"\", \"<div>Prazo de reavaliação",
            'Substitute(Substitute(Substitute(Coalesce(ThisItem.razao_social, "-"), "&", "&amp;")',
        ):
            if token not in toolbar:
                findings.append(f"laudo sem o tratamento esperado {token!r}")
        # Sem questionário (Fluxo I/II), a seção do terceiro não entra no laudo.
        if not re.search(r"If\(\s*_semQuestionario,\s*\"\",\s*\"<div class='lbl'>Questionário do terceiro", toolbar):
            findings.append("laudo deve omitir a seção do questionário quando não houve questionário")
        for stale in (
            "Sem questionário ao terceiro respondido até o momento.",
            "Sem condicionantes.",
            "Fluxo de análise",
            "Linha do tempo",
            'Coalesce(ThisItem.fluxo_classificacao, "-")',
            "Coalesce(ThisItem.terceiro_gatilho_risco, If(",
        ):
            if stale in toolbar:
                findings.append(f"laudo ainda tem item que não faz sentido para o solicitante: {stale!r}")
        return "resumo e laudo distinguem aprovação automática, envio pendente, aguardando e sem resposta"

    validator.check("Aprovação automática no resumo e no laudo", check_automatic_approval_display)

    def check_attachment_links(findings: list[str]) -> str:
        # 2026-09-17: Items.Value = Id (ajuste feito no Studio) abria um endereço do
        # armazenamento interno do Power Apps (pafeblob...blob.core.windows.net/.../web/%252fLists...)
        # e o arquivo dava BlobNotFound. O link que abre é o AbsoluteUri do SharePoint.
        checked = 0
        for path, document in yaml_documents.items():
            screens = document.get("Screens") if isinstance(document, dict) else None
            controls = [
                pair
                for screen in (screens.values() if isinstance(screens, dict) else [])
                if isinstance(screen, dict)
                for pair in iter_controls(screen.get("Children"))
            ]
            for name, control in controls:
                if not str(control.get("Control", "")).startswith("Attachments@"):
                    continue
                checked += 1
                properties = control.get("Properties") or {}
                value = str(properties.get("Items.Value", "")).strip()
                if value and value != "=AbsoluteUri":
                    findings.append(
                        f"{display(path)}: {name}.Items.Value = {value!r}; use =AbsoluteUri para o anexo abrir"
                    )
        return f"{checked} controle(s) de anexos abrem pelo link do SharePoint"

    validator.check("Anexos abrem pelo link do SharePoint", check_attachment_links)

    def check_risk_reclassification(findings: list[str]) -> str:
        combo = main_controls.get("cmbDdReclassificarRisco", {})
        items = re.findall(r'"([^"]*)"', str((combo.get("Properties") or {}).get("Items", "")))
        if items != ["Baixo", "Médio", "Alto"]:
            findings.append(f"cmbDdReclassificarRisco.Items deve ser Baixo/Médio/Alto; encontrado: {items}")
        container = main_controls.get("cntDdReclassificarRisco", {})
        container_visible = str((container.get("Properties") or {}).get("Visible", ""))
        # Depois da resposta do terceiro, ou junto com o Parecer final (que encerra a
        # solicitação). Antes disso o solicitante ainda edita e o recálculo do motor
        # sobrescreveria a reclassificação.
        for token in (
            "cntDdDesdTitulo.Visible",
            '(varRegistroDueDiligence.status = "Pendente Compliance" || cmbDdTipoDesdobramento.Selected.Value = "Parecer final")',
        ):
            if token not in container_visible:
                findings.append(f"cntDdReclassificarRisco.Visible sem {token!r}")
        analysis_form = main_controls.get("frmDdDesdobramento", {})
        success = re.sub(
            r"\s+", " ", str((analysis_form.get("Properties") or {}).get("OnSuccess", ""))
        )
        for token in (
            '_riscoEscolhido: If( varRegistroDueDiligence.status = "Pendente Compliance" || '
            'Self.LastSubmit.tipo_desdobramento = "Parecer final", cmbDdReclassificarRisco.Selected.Value, Blank() )',
            "classificacao_risco: Coalesce(_riscoEscolhido, _registroBase.classificacao_risco)",
            "Lower(Coalesce(_riscoEscolhido, _registroBase.classificacao_risco, \"\"))",
            'tipo_desdobramento: "Reclassificação de risco"',
            # IfError(Patch, Notify) dentro de um If exige tipos iguais (Record x
            # Boolean deu erro no Studio); IsError devolve Boolean em qualquer posição.
            "If( IsError( Patch( tb_dueDiligenceDesdobramentos,",
        ):
            if token not in success:
                findings.append(f"frmDdDesdobramento.OnSuccess sem {token!r}")
        return "Compliance reclassifica o risco, com vigência e histórico interno"

    validator.check("Reclassificação de risco pelo Compliance", check_risk_reclassification)

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

    def check_dashboard_location_filters(findings: list[str]) -> str:
        document = yaml_documents.get(PANEL_FILE)
        if not isinstance(document, dict):
            findings.append(f"{display(PANEL_FILE)} ausente ou inválido")
            return ""
        screen = next(iter(document["Screens"].values()))
        controls = dict(iter_controls(screen.get("Children")))
        on_visible = str((screen.get("Properties") or {}).get("OnVisible", ""))

        def prop(name: str, key: str) -> str:
            return str((controls.get(name, {}).get("Properties") or {}).get(key, ""))

        # Combos: só o Compliance vê; trocar o bloco volta o aeroporto para "todos".
        if prop("cmbDdPainelBloco", "Items") != '=["Todos os blocos", "CENTRAL", "SUL"]':
            findings.append("cmbDdPainelBloco.Items deve ser Todos os blocos, CENTRAL e SUL")
        if prop("cmbDdPainelBloco", "OnChange") != "=Reset(cmbDdPainelAeroporto)":
            findings.append("cmbDdPainelBloco.OnChange deve resetar o combo de aeroporto")
        for name in ("cmbDdPainelBloco", "cmbDdPainelAeroporto"):
            if prop(name, "Visible") != '=varDdPainelAcesso = "sim"':
                findings.append(f"{name}.Visible deve seguir o perfil Compliance")
        airport_items = re.sub(r"\s+", " ", prop("cmbDdPainelAeroporto", "Items"))
        for token in ("colDdPainelAeroportos", "bloco = cmbDdPainelBloco.Selected.Value", "{Value: _a.aeroporto}"):
            if token not in airport_items:
                findings.append(f"cmbDdPainelAeroporto.Items sem {token!r}")

        # Tabela aeroporto -> bloco igual à do cadastro (DataCard de bloco).
        panel_map = dict(re.findall(r'\{ordem: \d+, aeroporto: "([^"]+)", bloco: "([^"]*)"\}', on_visible))
        panel_map.pop("Todos os aeroportos", None)
        combo = main_controls.get("cmbDdAeroporto", {})
        main_airports = re.findall(r'"([^"]*)"', str((combo.get("Properties") or {}).get("Items", "")))
        cards = form_fields.get("bloco", [])
        groups = []
        if cards:
            update = str((cards[0][2].get("Properties") or {}).get("Update", ""))
            groups = [re.findall(r'"([^"]*)"', group) for group in re.findall(r"\[([^\]]*)\]", update)]
        main_map = {airport: "" for airport in main_airports}
        if len(groups) == 2:
            main_map.update({airport: "CENTRAL" for airport in groups[0]})
            main_map.update({airport: "SUL" for airport in groups[1]})
        if panel_map != main_map:
            findings.append(
                "tabela aeroporto -> bloco do painel diverge do cadastro: "
                f"{sorted(set(panel_map.items()) ^ set(main_map.items()))}"
            )
        for alias in ("_r", "_v", "_a"):
            token = f"bloco: Coalesce({alias}.bloco, LookUp(colDdPainelAeroportos, aeroporto = {alias}.aeroporto, bloco))"
            if on_visible.count(token) != 1:
                findings.append(f"carga do painel sem o bloco completado pela tabela em {alias}")
        if "aeroporto: _a.aeroporto," not in on_visible:
            findings.append("colDdPainelAbertos precisa do aeroporto para o filtro")
        if "If( IsEmpty(colDdPainelAeroportos)," not in re.sub(r"\s+", " ", on_visible):
            findings.append("colDdPainelAeroportos deve ser montada só uma vez (os combos perderiam a seleção)")

        # Cada bloco HTML filtra pela seleção; nenhuma coleção é lida sem o recorte.
        location = '(_aeroF = "" || aeroporto = _aeroF) && (_blocoF = "" || bloco = _blocoF)'
        viewers = {
            "htmDdPainelAtual": ("colDdPainelVigencia", "colDdPainelAbertos"),
            "htmDdPainelPeriodoTitulo": ("colDdPainel",),
            "htmDdPainelKpis": ("colDdPainel",),
            "htmDdPainelLinha1": ("colDdPainel",),
            "htmDdPainelLinha2": ("colDdPainel",),
            "htmDdPainelLinha3": ("colDdPainel",),
        }
        for name, collections in viewers.items():
            html = re.sub(r"\s+", " ", prop(name, "HtmlText"))
            for token in ('cmbDdPainelAeroporto.Selected.Value = "Todos os aeroportos"',
                          'cmbDdPainelBloco.Selected.Value = "Todos os blocos"'):
                if token not in html:
                    findings.append(f"{name}.HtmlText não lê o filtro {token!r}")
            for collection in collections:
                uses = len(re.findall(rf"\b{collection}\b(?![A-Za-z])", html))
                filtered = html.count(f"Filter({collection}, {location})")
                if uses != 1 or filtered != 1:
                    findings.append(
                        f"{name}.HtmlText deve ler {collection} só pelo recorte de bloco/aeroporto "
                        f"({uses} leitura(s), {filtered} recortada(s))"
                    )
            if name != "htmDdPainelPeriodoTitulo" and not html.lstrip("= ").startswith("With("):
                findings.append(f"{name}.HtmlText fora do padrão With do recorte")
            if name != "htmDdPainelPeriodoTitulo" and "varDdPainelCss &" not in html:
                findings.append(f"{name}.HtmlText sem o CSS de hover/animação")

        # CSS progressivo: dentro de div oculta, sem nada que o conteúdo dependa.
        css = re.search(r'varDdPainelCss: (".*?"),\s*varDdPainelAcesso', on_visible, flags=re.S)
        if not css or not css.group(1).startswith("\"<div style='display:none'><style>"):
            findings.append("varDdPainelCss deve abrir com <div style='display:none'><style>")
        elif "prefers-reduced-motion" not in css.group(1):
            findings.append("varDdPainelCss sem o respeito a prefers-reduced-motion")
        return f"{len(panel_map)} aeroporto(s) mapeados; {len(viewers)} bloco(s) HTML recortados por bloco/aeroporto"

    validator.check("Filtros de bloco e aeroporto no painel", check_dashboard_location_filters)

    def check_dashboard_width(findings: list[str]) -> str:
        # 2026-09-17: o painel saía mais largo que a tela (card da direita e filtros
        # cortados). A tela de Registros, que cabe, tem LayoutMinWidth nos contêineres e
        # controles esticados; o painel quase não tinha.
        painel = yaml_documents.get(BASE / "ScreenDueDiligencePainel.yaml")
        screens = painel.get("Screens") if isinstance(painel, dict) else None
        controles = {
            name: body
            for screen in (screens.values() if isinstance(screens, dict) else [])
            if isinstance(screen, dict)
            for name, body in iter_controls(screen.get("Children"))
        }
        exigidos = (
            "cntDdPainelBarra", "cntDdPainelCorpo", "htmDdPainelAtual", "cntDdPainelPeriodo",
            "htmDdPainelPeriodoTitulo", "htmDdPainelKpis", "htmDdPainelLinha1", "htmDdPainelLinha2",
            "htmDdPainelLinha3", "htmDdPainelNotas", "htmDdPainelRestrito",
        )
        for nome in exigidos:
            props = (controles.get(nome) or {}).get("Properties") or {}
            if not props:
                findings.append(f"ScreenDueDiligencePainel.yaml: {nome} não encontrado")
            elif str(props.get("LayoutMinWidth", "")) != "=16":
                findings.append(f"ScreenDueDiligencePainel.yaml: {nome} sem LayoutMinWidth: =16")
        return f"{len(exigidos)} contêiner(es) e visualizador(es) podem encolher até a largura da tela"

    validator.check("Painel cabe na largura da tela", check_dashboard_width)

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
        for name in ("HtmlText1", "lblDdRiscoCab", "lblDdRisco", "btnDdPainel"):
            restricted += 1
            if "varDdPodeAnalisarCompliance" not in visible(main_controls, name):
                findings.append(f"ScreenDueDiligence: {name}.Visible não restringe ao Compliance")
        # A coluna de pontuação saiu da lista no Studio (2026-09-18). Se voltar, é só do Compliance.
        for name in ("lblDdPontuacaoCab", "lblDdPontuacao"):
            if name in main_controls:
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

    def check_delete_permission(findings: list[str]) -> str:
        # 2026-09-21: excluir apaga a solicitação e todo o histórico dela. Só o Compliance
        # ou quem abriu a solicitação pode; a comparação é por e-mail, nunca por nome.
        pode = (
            "varDdPodeAnalisarCompliance || Lower(Trim(Coalesce(ThisItem.'Criado por'.Email, \"\"))) "
            "= Lower(Trim(User().Email))"
        )
        toolbar_items = re.sub(r"\s+", " ", str((main_controls.get("tbDdAcoes", {}).get("Properties") or {}).get("Items", "")))
        toolbar_select = re.sub(r"\s+", " ", str((main_controls.get("tbDdAcoes", {}).get("Properties") or {}).get("OnSelect", "")))
        confirmar = re.sub(
            r"\s+", " ", str((main_controls.get("btnDdExcluirConfirmar", {}).get("Properties") or {}).get("OnSelect", ""))
        )
        if f"_podeExcluir: {pode}" not in toolbar_items:
            findings.append("tbDdAcoes.Items sem _podeExcluir (Compliance ou autor, por e-mail)")
        if "ItemDisabled: !_podeExcluir," not in toolbar_items:
            findings.append("o item Excluir deve ficar desabilitado para quem não pode excluir")
        if f'"excluir", If( {pode},' not in toolbar_select:
            findings.append("tbDdAcoes.OnSelect: o ramo excluir deve conferir a permissão antes de abrir a confirmação")
        registro = pode.replace("ThisItem.", "varRegistroDueDiligence.")
        if f"=If( !({registro})," not in confirmar:
            findings.append("btnDdExcluirConfirmar deve recusar a exclusão de quem não é o Compliance nem o autor")
        # Exibir o nome é legítimo; comparar a pessoa por nome, não. O campo "Criado por"
        # só pode ser comparado pelo e-mail (lição do Service Desk, 2026-09-11).
        for path, texto in yaml_texts.items():
            for autor in re.finditer(r"'Criado por'(?P<campo>\.\w+)?\s*(?:=|<>)", re.sub(r"\s+", " ", texto)):
                if autor.group("campo") != ".Email":
                    findings.append(
                        f"{display(path)}: 'Criado por'{autor.group('campo') or ''} comparado sem o e-mail; "
                        "use 'Criado por'.Email"
                    )
        return "excluir liberado só para o Compliance e para quem abriu, conferido nas três camadas"

    validator.check("Exclusão restrita ao Compliance e ao autor", check_delete_permission)

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
