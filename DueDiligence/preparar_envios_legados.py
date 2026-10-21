#!/usr/bin/env python3
"""Prepara CSV de convites antigos sem inferir destinatário por proximidade.

Etapa 1: --historico e --candidatos geram códigos/solicitações do histórico.
Etapa 2: preencher --conferidos com envio_id,solicitacao_id,email_envio após
verificar a mensagem ou outra evidência confiável e gerar --saida.
Não altera SharePoint.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

from auditar_respostas_pendentes import UUID, get, normalized, read_csv, require_column
from build_power_automate_flows import FORM_ID

EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)


def candidates(histories: list[dict[str, str]]) -> list[dict[str, str]]:
    result = []
    for row in histories:
        if normalized(get(row, 'tipo_desdobramento')) != 'envio ao terceiro':
            continue
        sid = get(row, 'solicitacao_id')
        structured = get(row, 'forms_envio_id').lower()
        extracted = sorted({code.lower() for code in UUID.findall(get(row, 'descricao', 'descrição'))})
        if not sid or (structured and (not UUID.fullmatch(structured) or (extracted and structured not in extracted))):
            raise ValueError(f"Histórico ID {get(row, 'ID')}: solicitação/código estruturado divergente")
        if len(extracted) > 1 and not structured:
            raise ValueError(f"Histórico ID {get(row, 'ID')}: mais de um código na descrição")
        code = structured or (extracted[0] if extracted else '')
        if not code:
            continue
        result.append({
            'envio_id': code.lower(), 'solicitacao_id': sid,
            'historico_id': get(row, 'ID'),
            'email_registrado': get(row, 'email_envio'),
        })
    return result


def prepare(rows: list[dict[str, str]], checked: list[dict[str, str]]) -> list[dict[str, str]]:
    by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_code[row['envio_id']].append(row)
    approved: dict[str, tuple[str, str]] = {}
    for row in checked:
        code = get(row, 'envio_id').lower()
        sid = get(row, 'solicitacao_id')
        email = get(row, 'email_envio').strip().lower()
        if not UUID.fullmatch(code) or not sid.isdigit() or not EMAIL.fullmatch(email):
            raise ValueError(f"Conferência inválida: código={code!r}, solicitação={sid!r}")
        if code in approved:
            raise ValueError(f"Código repetido no CSV conferido: {code}")
        approved[code] = (sid, email)
    result = []
    for code, (sid, email) in approved.items():
        matches = by_code.get(code, [])
        if len(matches) != 1 or matches[0]['solicitacao_id'] != sid:
            raise ValueError(f"Código {code}: esperado um único envio histórico da solicitação {sid}; encontrado {len(matches)}")
        source = matches[0]
        if source['email_registrado'] and normalized(source['email_registrado']) != normalized(email):
            raise ValueError(f"Código {code}: e-mail conferido difere do histórico estruturado")
        result.append({
            'envio_id': code,
            'solicitacao_id': sid,
            'forms_formulario_id': FORM_ID,
            'email_envio': email,
            'estado_envio': 'Aceito',
            'observacao': f"Migração conferida do desdobramento ID {source['historico_id']}; conferir mensagem antes de importar.",
        })
    return sorted(result, key=lambda row: (int(row['solicitacao_id']), row['envio_id']))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historico', type=Path, required=True)
    parser.add_argument('--candidatos', type=Path, required=True)
    parser.add_argument('--conferidos', type=Path)
    parser.add_argument('--saida', type=Path)
    args = parser.parse_args()
    try:
        history = read_csv(args.historico)
        require_column(history, args.historico, 'solicitacao_id')
        rows = candidates(history)
        write_rows(args.candidatos,
                   ['envio_id','solicitacao_id','historico_id','email_registrado'], rows)
        print(f'{len(rows)} convite(s) candidato(s): {args.candidatos}')
        if args.conferidos:
            if not args.saida:
                raise ValueError('--saida é obrigatório com --conferidos')
            checked = read_csv(args.conferidos)
            require_column(checked, args.conferidos, 'envio_id')
            require_column(checked, args.conferidos, 'solicitacao_id')
            require_column(checked, args.conferidos, 'email_envio')
            ready = prepare(rows, checked)
            write_rows(args.saida,
                       ['envio_id','solicitacao_id','forms_formulario_id','email_envio','estado_envio','observacao'],
                       ready)
            print(f'{len(ready)} convite(s) conferido(s): {args.saida}')
        return 0
    except (OSError, ValueError) as exc:
        print(f'Erro: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
