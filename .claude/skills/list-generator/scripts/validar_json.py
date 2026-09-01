#!/usr/bin/env python3
"""Valida a definicao JSON de lista SharePoint para o fluxo List_Generator.

Uso:  python3 validar_json.py arquivo.json
      cat arquivo.json | python3 validar_json.py -

Sai com codigo 0 se estiver valido; 1 e lista de erros caso contrario.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET

NOME_LISTA = re.compile(r"^tb_[a-z][a-zA-Z0-9]*$")
INTERNAL = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
CHAVES = ["nomeLista", "descricao", "ocultarTitle", "colunas", "registrosIniciais",
          "validacaoLista"]
TIPOS_OK = {"Text", "Note", "Number", "DateTime"}
TIPOS_PROIBIDOS = {"Choice", "MultiChoice", "User", "UserMulti", "Boolean", "Lookup",
                   "LookupMulti", "Currency", "TaxonomyFieldType", "Calculated"}
MAX_INDICES = 20


def verdadeiro(v):
    return str(v).strip().upper() in ("TRUE", "1")


def validar(doc):
    erros = []
    e = erros.append

    faltando = [k for k in CHAVES if k not in doc]
    if faltando:
        e(f"propriedades ausentes: {', '.join(faltando)}")
    extras = [k for k in doc if k not in CHAVES]
    if extras:
        e(f"propriedades nao previstas: {', '.join(extras)}")
    ordem = [k for k in doc if k in CHAVES]
    if ordem != [k for k in CHAVES if k in doc]:
        e(f"propriedades fora da ordem do contrato: {', '.join(ordem)}")

    nome = doc.get("nomeLista", "")
    if not NOME_LISTA.match(str(nome)):
        e(f"nomeLista '{nome}' deve comecar com tb_ e seguir camelCase sem acento/espaco/hifen")

    if doc.get("ocultarTitle") is not True:
        e("ocultarTitle deve ser exatamente true")

    if not isinstance(doc.get("descricao", ""), str) or not doc.get("descricao", "").strip():
        e("descricao deve ser um texto nao vazio")

    colunas = doc.get("colunas")
    if not isinstance(colunas, list) or not colunas:
        e("colunas deve ser uma lista nao vazia")
        return erros

    nativas = {"id", "created", "modified", "author", "editor", "title"}
    nomes, indices = [], 0

    for i, col in enumerate(colunas):
        rot = f"colunas[{i}]"
        if not isinstance(col, dict):
            e(f"{rot}: deve ser um objeto")
            continue
        sobra = [k for k in col if k not in ("internalName", "schemaXml")]
        if sobra:
            e(f"{rot}: propriedades nao previstas: {', '.join(sobra)}")

        interno = col.get("internalName", "")
        rot = f"coluna '{interno or i}'"
        if not INTERNAL.match(str(interno)):
            e(f"{rot}: internalName fora do padrao minusculo snake_case")
        if str(interno).lower() in nativas:
            e(f"{rot}: duplica coluna nativa do SharePoint")
        if interno in nomes:
            e(f"{rot}: internalName duplicado")
        nomes.append(interno)

        xml = col.get("schemaXml", "")
        if "Title" in xml:
            e(f"{rot}: schemaXml nao pode mencionar Title")
        try:
            f = ET.fromstring(xml)
        except ET.ParseError as exc:
            e(f"{rot}: schemaXml invalido ({exc})")
            continue

        for attr in ("DisplayName", "Name", "StaticName"):
            valor = f.get(attr)
            if valor != interno:
                e(f"{rot}: {attr}='{valor}' deveria ser identico ao internalName '{interno}'")

        tipo = f.get("Type")
        if tipo in TIPOS_PROIBIDOS:
            e(f"{rot}: tipo {tipo} e proibido")
        elif tipo not in TIPOS_OK:
            e(f"{rot}: tipo '{tipo}' nao permitido (use Text, Note, Number ou DateTime)")

        if f.get("Group") != "AirportNow":
            e(f"{rot}: Group deve ser 'AirportNow'")
        if f.get("Required") is None:
            e(f"{rot}: Required nao declarado")

        indexado = verdadeiro(f.get("Indexed", "FALSE"))
        if indexado:
            indices += 1

        if tipo == "Text" and not f.get("MaxLength"):
            e(f"{rot}: campo Text sem MaxLength")
        if tipo == "Note":
            if verdadeiro(f.get("RichText", "FALSE")):
                e(f"{rot}: Note deve usar RichText='FALSE'")
            if verdadeiro(f.get("AppendOnly", "FALSE")):
                e(f"{rot}: Note deve usar AppendOnly='FALSE'")
            if indexado:
                e(f"{rot}: campo Note nunca pode ser indexado")
        if tipo == "Number" and f.get("Decimals") is None:
            e(f"{rot}: campo Number sem Decimals")
        if tipo == "DateTime" and f.get("Format") not in ("DateTime", "DateOnly"):
            e(f"{rot}: DateTime precisa de Format='DateTime' ou 'DateOnly'")

        v = f.find("Validation")
        if v is not None:
            if not (v.text or "").strip().startswith("="):
                e(f"{rot}: <Validation> precisa de uma formula comecando com '='")
            if not (v.get("Message") or "").strip():
                e(f"{rot}: <Validation> sem atributo Message")
            fora = [r for r in re.findall(r"\[([^\]]+)\]", v.text or "") if r != interno]
            if fora:
                e(f"{rot}: <Validation> referencia outra coluna ({', '.join(sorted(set(fora)))}) — "
                  f"regra entre colunas vai em validacaoLista")

    val = doc.get("validacaoLista")
    if not isinstance(val, dict):
        e("validacaoLista deve ser um objeto (use {} quando nao houver regra)")
    elif val:
        sobra = [k for k in val if k not in ("formula", "mensagem")]
        if sobra:
            e(f"validacaoLista: propriedades nao previstas: {', '.join(sobra)}")
        formula = str(val.get("formula", ""))
        if not formula.startswith("="):
            e("validacaoLista.formula deve comecar com '='")
        if not str(val.get("mensagem", "")).strip():
            e("validacaoLista: formula sem mensagem")
        for ref in re.findall(r"\[([^\]]+)\]", formula):
            if ref not in nomes:
                e(f"validacaoLista.formula referencia a coluna '{ref}', que nao esta em colunas")
        if len(set(re.findall(r"\[([^\]]+)\]", formula))) < 2:
            e("validacaoLista deve cruzar duas colunas — regra de uma coluna so vai no "
              "<Validation> do proprio schemaXml")

    if indices > MAX_INDICES:
        e(f"{indices} colunas indexadas — o SharePoint permite no maximo {MAX_INDICES}")

    registros = doc.get("registrosIniciais")
    if not isinstance(registros, list):
        e("registrosIniciais deve ser uma lista (use [] quando nao houver)")
    else:
        for i, reg in enumerate(registros):
            if not isinstance(reg, dict):
                e(f"registrosIniciais[{i}]: deve ser um objeto")
                continue
            for chave, valor in reg.items():
                if chave not in nomes:
                    e(f"registrosIniciais[{i}]: coluna '{chave}' nao declarada em colunas")
                if isinstance(valor, bool):
                    e(f"registrosIniciais[{i}].{chave}: use 1 ou 0, nunca true/false")
    return erros


def main():
    origem = sys.argv[1] if len(sys.argv) > 1 else "-"
    bruto = sys.stdin.read() if origem == "-" else open(origem, encoding="utf-8").read()
    try:
        doc = json.loads(bruto)
    except json.JSONDecodeError as exc:
        print(f"JSON invalido: {exc}")
        return 1
    erros = validar(doc)
    if erros:
        print(f"{len(erros)} problema(s):")
        for x in erros:
            print(f"  - {x}")
        return 1
    print("JSON valido para o List_Generator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
