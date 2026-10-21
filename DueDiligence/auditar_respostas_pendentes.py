#!/usr/bin/env python3
"""Cruza exportações CSV do SharePoint e Microsoft Forms sem alterar registros.

Exemplo:
  python auditar_respostas_pendentes.py \
    --solicitacoes solicitacoes.csv --historico historico.csv \
    --forms forms.csv --internas respostas_internas.csv \
    --saida auditoria.csv

O relatório contém identificadores e contagens, sem respostas nem dados pessoais.
Uma resposta sem código não é associada por nome, e-mail ou data.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path


UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.strip().lower())
    return "".join(char for char in value if not unicodedata.combining(char))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ";"
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError(f"{path}: cabeçalho CSV ausente")
        return [{normalized(key): (value or "").strip() for key, value in row.items() if key}
                for row in reader]


def get(row: dict[str, str], *aliases: str) -> str:
    for alias in aliases:
        value = row.get(normalized(alias), "")
        if value:
            return value
    return ""


def require_column(rows: list[dict[str, str]], path: Path, *aliases: str) -> None:
    if not rows:
        raise ValueError(f"{path}: CSV vazio")
    if not any(normalized(alias) in rows[0] for alias in aliases):
        raise ValueError(f"{path}: coluna obrigatória ausente ({', '.join(aliases)})")


def index_histories(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    codes: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        solicitation = get(row, "solicitacao_id")
        event = normalized(get(row, "tipo_desdobramento", "tipo", "tipo_acao", "acao"))
        if not solicitation or "envio ao terceiro" not in event:
            continue
        description = get(row, "descricao", "descrição")
        codes[solicitation].update(UUID.findall(description))
        structured = get(row, "forms_envio_id")
        if structured:
            codes[solicitation].add(structured)
    return codes


def index_internal(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    indexed: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        solicitation = get(row, "solicitacao_id")
        response = get(row, "forms_resposta_id")
        if solicitation and response:
            indexed[(solicitation, response)].append(row)
    return indexed


def audit(
    parents: list[dict[str, str]],
    histories: list[dict[str, str]],
    forms: list[dict[str, str]],
    internal: list[dict[str, str]],
    code_column: str,
    response_column: str,
    envios: list[dict[str, str]] | None = None,
    inbox: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    history_codes = index_histories(histories)
    internals = index_internal(internal)
    code_owners: dict[str, set[str]] = defaultdict(set)
    parent_by_id = {get(parent, "ID"): parent for parent in parents if get(parent, "ID")}
    for parent in parents:
        sid = get(parent, "ID")
        if not sid:
            continue
        codes = history_codes[sid] | {get(parent, "forms_envio_id")}
        for code in codes - {""}:
            code_owners[code].add(sid)
    send_by_code = {}
    if envios is not None:
        for row in envios:
            code = get(row, 'envio_id')
            sid = get(row, 'solicitacao_id')
            if code and sid:
                code_owners[code].add(sid)
                send_by_code[code] = row
    inbox_by_response: dict[str, list[dict[str, str]]] = defaultdict(list)
    if inbox is not None:
        for row in inbox:
            response = get(row, 'forms_resposta_id')
            if response:
                inbox_by_response[response].append(row)

    rows: list[dict[str, str]] = []
    for form in forms:
        code = get(form, code_column)
        response = get(form, response_column)
        inbox_rows = inbox_by_response.get(response, [])
        inbox_state = get(inbox_rows[0], 'estado') if len(inbox_rows) == 1 else ''
        inbox_attempts = get(inbox_rows[0], 'tentativas') if len(inbox_rows) == 1 else ''
        send_state = get(send_by_code.get(code, {}), 'estado_envio')
        owners = code_owners.get(code, set()) if code else set()
        if len(owners) != 1:
            rows.append({
                "solicitacao_id": "", "forms_resposta_id": response,
                "codigo_resposta": code, "codigo_atual": "", "status": "",
                "linhas_internas": "", "diagnostico": (
                    "CODIGO_VAZIO" if not code else
                    "CODIGO_AMBIGUO" if owners else "CODIGO_NAO_ENCONTRADO"
                ),
                "estado_inbox": inbox_state, "tentativas_inbox": inbox_attempts,
                "estado_envio": send_state,
            })
            continue
        sid = next(iter(owners))
        parent = parent_by_id[sid]
        current = get(parent, "forms_envio_id")
        status = get(parent, "status")
        child_rows = internals.get((sid, response), [])
        questions = {get(row, "codigo_pergunta") for row in child_rows}
        expected = 11 if any(
            get(row, "codigo_pergunta") == "terceiro_t01" and
            normalized(get(row, "resposta")) == "sim" for row in child_rows
        ) else 10
        if len(inbox_rows) > 1:
            diagnosis = 'INBOX_DUPLICADA'
        elif inbox is not None and not inbox_rows and get(parent, "forms_ultima_resposta_id") != response:
            diagnosis = 'SEM_CAPTURA_INBOX'
        elif get(parent, "forms_ultima_resposta_id") == response:
            diagnosis = "JA_PROCESSADA"
        elif inbox_state == 'Revisao':
            diagnosis = 'EM_REVISAO'
        elif inbox_state == 'Processado':
            diagnosis = 'INBOX_PROCESSADA_SEM_PAI'
        elif send_state and send_state != 'Aceito':
            diagnosis = 'ENVIO_SEM_ACEITE'
        elif code != current:
            diagnosis = "CODIGO_DE_REENVIO_ANTIGO"
        elif get(parent, "forms_envio_processado_id") != current:
            diagnosis = "ENVIO_ATUAL_NAO_CONFIRMADO"
        elif normalized(get(parent, "fluxo_classificacao")) != "fluxo iii":
            diagnosis = "FLUXO_INCOMPATIVEL"
        elif status != "Aguardando Terceiro" and get(parent, "forms_ultima_resposta_id") != response:
            diagnosis = "STATUS_INCOMPATIVEL"
        elif child_rows and len(questions) < expected:
            diagnosis = "GRAVACAO_PARCIAL"
        elif child_rows:
            diagnosis = "FILHAS_SEM_CONSOLIDACAO"
        elif inbox_state == 'Pendente':
            diagnosis = 'CAPTURADA_PENDENTE'
        else:
            diagnosis = "RESPOSTA_ATUAL_SEM_PROCESSAMENTO"
        rows.append({
            "solicitacao_id": sid, "forms_resposta_id": response,
            "codigo_resposta": code, "codigo_atual": current, "status": status,
            "linhas_internas": str(len(questions)), "diagnostico": diagnosis,
            "estado_inbox": inbox_state, "tentativas_inbox": inbox_attempts,
            "estado_envio": send_state,
        })

    response_sids = {row["solicitacao_id"] for row in rows if row["solicitacao_id"]}
    for parent in parents:
        sid = get(parent, "ID")
        if get(parent, "status") != "Aguardando Terceiro" or sid in response_sids:
            continue
        current = get(parent, "forms_envio_id")
        diagnosis = "SEM_RESPOSTA_LOCALIZADA"
        if not current:
            diagnosis = "SEM_CODIGO_ATUAL"
        elif get(parent, "forms_envio_processado_id") != current:
            diagnosis = "ENVIO_PENDENTE_OU_FALHOU"
        rows.append({
            "solicitacao_id": sid, "forms_resposta_id": "",
            "codigo_resposta": "", "codigo_atual": current,
            "status": "Aguardando Terceiro", "linhas_internas": "",
            "diagnostico": diagnosis,
            "estado_inbox": "", "tentativas_inbox": "", "estado_envio": get(send_by_code.get(current, {}), 'estado_envio'),
        })
    return sorted(rows, key=lambda row: (row["solicitacao_id"], row["forms_resposta_id"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solicitacoes", type=Path, required=True)
    parser.add_argument("--historico", type=Path, required=True)
    parser.add_argument("--forms", type=Path, required=True)
    parser.add_argument("--internas", type=Path, help="CSV opcional de tb_dueDiligenceTerceiroRespostas")
    parser.add_argument("--envios", type=Path, help="CSV opcional de tb_dueDiligenceEnvios")
    parser.add_argument("--inbox", type=Path, help="CSV opcional de tb_dueDiligenceRespostasInbox, sem conteudo_json")
    parser.add_argument("--coluna-codigo", default="Código de acompanhamento")
    parser.add_argument("--coluna-resposta-id", default="ID")
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    try:
        parents = read_csv(args.solicitacoes)
        histories = read_csv(args.historico)
        forms = read_csv(args.forms)
        internal = read_csv(args.internas) if args.internas else []
        sends = read_csv(args.envios) if args.envios else None
        captured = read_csv(args.inbox) if args.inbox else None
        require_column(parents, args.solicitacoes, "ID")
        require_column(histories, args.historico, "solicitacao_id")
        require_column(forms, args.forms, args.coluna_codigo)
        require_column(forms, args.forms, args.coluna_resposta_id)
        if args.internas:
            require_column(internal, args.internas, "solicitacao_id")
        if args.envios:
            require_column(sends, args.envios, "envio_id")
        if args.inbox:
            require_column(captured, args.inbox, "forms_resposta_id")
        results = audit(parents, histories, forms, internal,
                        args.coluna_codigo, args.coluna_resposta_id,
                        sends, captured)
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        with args.saida.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "solicitacao_id", "forms_resposta_id", "codigo_resposta",
                "codigo_atual", "status", "linhas_internas", "diagnostico",
                "estado_inbox", "tentativas_inbox", "estado_envio",
            ], delimiter=";")
            writer.writeheader()
            writer.writerows(results)
        print(f"{len(results)} ocorrências auditadas: {args.saida}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
