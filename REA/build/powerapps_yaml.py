"""Leitor do subconjunto YAML exportado nesta tela (sem dependências).

Suporta mapas, Children em lista, escalares simples/JSON e blocos literais.
Não substitui o compilador Power Fx nem o importador do Power Apps Studio.
"""

import json
import re


def parse_studio(text):
    lines = text.splitlines()
    if "\t" in text or text.startswith("\ufeff"):
        raise ValueError("YAML com TAB ou BOM")
    spans = {}

    def level(i):
        return len(lines[i]) - len(lines[i].lstrip(" "))

    def block(i, indent, path):
        result = [] if lines[i].lstrip().startswith("- ") else {}
        while i < len(lines) and level(i) >= indent:
            if not lines[i].strip():
                i += 1
                continue
            if level(i) != indent:
                raise ValueError(f"Linha {i + 1}: recuo inesperado")
            raw = lines[i][indent:]
            if isinstance(result, list):
                match = re.fullmatch(r"- ([A-Za-z][A-Za-z0-9_]*):", raw)
                if not match:
                    raise ValueError(f"Linha {i + 1}: item Children inválido")
                name = match[1]
                value, i = block(i + 1, indent + 4, path + (len(result), name))
                result.append({name: value})
                continue
            match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*):(?: (.*))?", raw)
            if not match:
                raise ValueError(f"Linha {i + 1}: chave YAML inválida")
            key, value = match.groups()
            if key in result:
                raise ValueError(f"Linha {i + 1}: chave duplicada {key}")
            start = i
            i += 1
            if value is None or value == "":
                if i >= len(lines) or level(i) != indent + 2:
                    raise ValueError(f"Linha {start + 1}: mapa/lista sem conteúdo")
                value, i = block(i, indent + 2, path + (key,))
            elif value in ("|", "|-", "|+"):
                body_start = i
                while i < len(lines) and (not lines[i].strip() or level(i) > indent):
                    if lines[i].strip() and level(i) < indent + 2:
                        raise ValueError(f"Linha {i + 1}: bloco literal sem recuo")
                    i += 1
                if body_start == i:
                    raise ValueError(f"Linha {start + 1}: bloco literal vazio")
                value = "\n".join(line[indent + 2:] for line in lines[body_start:i])
            elif value.startswith('"'):
                value = json.loads(value)
            elif ": " in value or " #" in value:
                raise ValueError(f"Linha {start + 1}: escalar deve ser literal ou entre aspas")
            result[key] = value
            spans[path + (key,)] = (start, i, indent)
        return result, i

    root, end = block(0, 0, ())
    if end != len(lines):
        raise ValueError("YAML não consumido integralmente")
    return root, spans


def controls(root):
    """Controles em ordem, com tipo, propriedades e caminho na árvore."""
    result = {}

    def walk(node, path):
        for index, item in enumerate(node.get("Children", [])):
            for name, child in item.items():
                if name in result:
                    raise ValueError(f"Controle duplicado: {name}")
                child_path = path + ("Children", index, name)
                result[name] = (child, child_path)
                walk(child, child_path)

    for name, screen in root["Screens"].items():
        walk(screen, ("Screens", name))
    return result


def set_property(text, name, key, value):
    root, spans = parse_studio(text)
    node, path = controls(root)[name]
    properties = path + ("Properties",)
    if key in node["Properties"]:
        start, end, indent = spans[properties + (key,)]
    else:
        first = next(iter(node["Properties"]))
        start, _, indent = spans[properties + (first,)]
        end = start
    prefix = " " * indent
    if "\n" in value or ": " in value:
        emitted = [f"{prefix}{key}: |-"] + [prefix + "  " + line for line in value.splitlines()]
    else:
        emitted = [f"{prefix}{key}: {value}"]
    lines = text.splitlines()
    return "\n".join(lines[:start] + emitted + lines[end:]) + "\n"
