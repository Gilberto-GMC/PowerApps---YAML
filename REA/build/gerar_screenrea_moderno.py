"""Gera a nova ScreenREA a partir das fórmulas funcionais do export atual."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "msapp/Src/ScreenREA.pa.yaml"
OUTPUT = ROOT / "out/ScreenREA_Moderno.pa.yaml"
screen = yaml.load(SOURCE.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)["Screens"]["ScreenREA"]


def find(name, nodes=None):
    top_level = nodes is None
    for item in nodes if nodes is not None else screen["Children"]:
        item_name, node = next(iter(item.items()))
        if item_name == name:
            return copy.deepcopy(node)
        match = find(name, node.get("Children", []))
        if match:
            return match
    if top_level:
        raise KeyError(name)
    return None


def control(name, kind, properties, children=None, variant=None):
    node = {"Control": kind}
    if variant:
        node["Variant"] = variant
    node["Properties"] = properties
    if children:
        node["Children"] = children
    return {name: node}


def html(markup):
    return "=" + json.dumps(markup, ensure_ascii=False)


def html_control(name, markup, x, y, width, height):
    return control(name, "HtmlViewer@2.1.0", {
        "HtmlText": html(markup), "X": x, "Y": y, "Width": width,
        "Height": height, "PaddingTop": "=0", "PaddingBottom": "=0",
        "PaddingLeft": "=0", "PaddingRight": "=0",
    })


def label(name, value, x, y, width, height, size=12, color="#17324d", weight=None):
    props = {"Text": value, "X": x, "Y": y, "Width": width, "Height": height,
             "Size": f"={size}", "Color": f"=ColorValue(\"{color}\")"}
    if weight:
        props["FontWeight"] = f"=FontWeight.{weight}"
    return control(name, "Label@2.5.1", props)


def native_icon(name, icon, color, x, y, size, visible=None, tooltip=None):
    props = {
        "Icon": f"=Icon.{icon}", "Color": f'=ColorValue("{color}")',
        "X": x, "Y": y, "Width": size, "Height": size,
        "DisplayMode": "=DisplayMode.View",
    }
    if visible:
        props["Visible"] = visible
    if tooltip:
        props["Tooltip"] = tooltip
    return control(name, "Classic/Icon@2.5.0", props)


def action(name, text, on_select, x, y, width, height, tooltip=None):
    props = {
        "Text": f"={json.dumps(text, ensure_ascii=False)}", "OnSelect": on_select,
        "X": x, "Y": y, "Width": width, "Height": height,
        "Fill": "=RGBA(255,255,255,0)", "HoverFill": "=RGBA(0,117,138,0.08)",
        "PressedFill": "=RGBA(0,117,138,0.14)", "Color": "=RGBA(0,0,0,0)",
        "HoverColor": "=RGBA(0,0,0,0)", "BorderStyle": "=BorderStyle.None",
        "BorderThickness": "=0", "RadiusTopLeft": "=12", "RadiusTopRight": "=12",
        "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12",
    }
    if tooltip:
        props["Tooltip"] = tooltip
    return control(name, "Classic/Button@2.2.0", props)


def section(name, title, sub, icon, accent, y, height, children):
    heading = (
        "<div style='font-family:Segoe UI,Arial,sans-serif;white-space:nowrap;padding:4px 2px'>"
        f"<strong style='font-size:16px;color:#102b43'>{title}</strong>"
        f"<span style='font-size:12px;color:#667b8e;margin-left:14px'>{sub}</span>"
        "</div>"
    )
    return control(name, "GroupContainer@1.5.0", {
        "Height": f"={height}", "Width": "=Parent.Width-8", "FillPortions": "=0",
        "DropShadow": "=DropShadow.None", "LayoutMinHeight": "=0",
        "Fill": "=RGBA(255,255,255,1)", "BorderColor": "=ColorValue(\"#e2eaf0\")",
        "BorderThickness": "=1", "RadiusTopLeft": "=15", "RadiusTopRight": "=15",
        "RadiusBottomLeft": "=15", "RadiusBottomRight": "=15",
    }, [native_icon(name + "Icone", icon, accent, "=17", "=11", "=22"),
        html_control(name + "Cabecalho", heading, "=49", "=5", "=Parent.Width-65", "=39")] + children,
        "ManualLayout")


def empty_state(name, gallery_name):
    item = label(name, '=\"Nenhum módulo corresponde à busca.\"',
                 "=20", "=66", "=Parent.Width-40", "=38", 11, "#6b8291")
    item[name]["Properties"]["Visible"] = f"={gallery_name}.AllItemsCount=0"
    return item


def source_icon(source_name, x, y, size, padding=4):
    original = find(source_name)
    source = original["Properties"]
    properties = {
        "Image": source["Image"], "X": x, "Y": y,
        "Width": size, "Height": size,
        "PaddingLeft": f"={padding}", "PaddingRight": f"={padding}",
        "PaddingTop": f"={padding}", "PaddingBottom": f"={padding}",
    }
    if "ImagePosition" in source:
        properties["ImagePosition"] = source["ImagePosition"]
    return control(source_name, original["Control"], properties)


def gallery_card(name, source_gallery, source_button, tint):
    gallery = find(source_gallery)
    gallery["Variant"] = "Vertical"
    gp = gallery["Properties"]
    gp.update({"X": "=16", "Y": "=46", "Width": "=Parent.Width-32",
               "Height": "=Parent.Height-52",
               "WrapCount": "=If(Self.Width<850,3,If(Self.Width<1100,4,5))" if source_gallery == "Gallery30_8" else "=If(Self.Width<850,3,5)",
               "TemplateSize": "=70", "TemplatePadding": "=5", "ShowScrollbar": "=false",
               "Visible": "=true"})
    gp.pop("BorderColor", None)
    image_name = {
        "Gallery30_8": "Image1_101",
        "Gallery30_7": "Image1_100",
        "Gallery30_6": "Image1_82",
    }[source_gallery]
    button = find(source_button)
    bp = button["Properties"]
    gallery["Children"] = [
        control("cntCard" + source_gallery, "GroupContainer@1.5.0", {
            "X": "=0", "Y": "=0", "Width": "=Parent.TemplateWidth-5",
            "Height": "=Parent.TemplateHeight-5", "Fill": "=RGBA(255,255,255,1)",
            "BorderColor": "=ColorValue(\"#dce7ef\")", "BorderThickness": "=1",
            "RadiusTopLeft": "=12", "RadiusTopRight": "=12",
            "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12",
            "DropShadow": "=DropShadow.None",
        }, [
            control("cntCardIcon" + source_gallery, "GroupContainer@1.5.0", {
                "X": "=11", "Y": "=11", "Width": "=42", "Height": "=42",
                "Fill": f'=ColorValue("{tint}")', "DropShadow": "=DropShadow.None",
                "RadiusTopLeft": "=12", "RadiusTopRight": "=12",
                "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12",
            }, None, "ManualLayout"),
            source_icon(image_name, "=11", "=11", "=42", 4),
            label("lblCard" + source_gallery, "=ThisItem.Titulo", "=62", "=9", "=Parent.Width-91", "=44", 10, "#17324d", "Semibold"),
            native_icon("icoCardArrow" + source_gallery, "ChevronRight", "#7192a5",
                        "=Parent.Width-25", "=24", "=15"),
        control("lblDev" + source_gallery, "Label@2.5.1", {
            "Text": '=\"Em desenvolvimento\"', "Visible": '=ThisItem.Status.Value = "Em desenvolvimento"',
            "X": "=62", "Y": "=47", "Width": "=Parent.Width-75", "Height": "=15",
            "Size": "=8", "Color": "=ColorValue(\"#9b6b08\")",
        }),
        control("btnCard" + source_gallery, "Classic/Button@2.2.0", {
            "Text": '=\"\"', "OnSelect": bp["OnSelect"], "Tooltip": "=ThisItem.Descricao",
            "X": "=0", "Y": "=0", "Width": "=Parent.Width", "Height": "=Parent.Height",
            "Fill": "=RGBA(0,0,0,0)", "HoverFill": "=RGBA(0,117,138,0.06)",
            "PressedFill": "=RGBA(0,117,138,0.12)", "Color": "=RGBA(0,0,0,0)",
            "BorderStyle": "=BorderStyle.None", "BorderThickness": "=0",
        }),
        ], "ManualLayout"),
    ]
    return {name: gallery}


def routine_card(period, title, x, suffix):
    image_name = {"Dia": "Image1_104", "Sem": "Image1_105", "Mes": "Image1_106"}[suffix]
    return control("cntRotina" + suffix, "GroupContainer@1.5.0", {
        "X": x, "Y": "=47", "Width": "=(Parent.Width-52)/3", "Height": "=64",
        "DropShadow": "=DropShadow.None", "Fill": "=RGBA(255,255,255,1)",
        "BorderColor": "=ColorValue(\"#dce7ef\")", "BorderThickness": "=1",
        "RadiusTopLeft": "=12", "RadiusTopRight": "=12",
        "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12",
    }, [
        control("cntRotinaIcon" + suffix, "GroupContainer@1.5.0", {
            "X": "=12", "Y": "=9", "Width": "=46", "Height": "=46",
            "Fill": "=ColorValue(\"#e4f7f9\")", "DropShadow": "=DropShadow.None",
            "RadiusTopLeft": "=12", "RadiusTopRight": "=12",
            "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12",
        }, None, "ManualLayout"),
        source_icon(image_name, "=12", "=9", "=46", 3),
        label("lblRotinaTitulo" + suffix, f'={json.dumps(title, ensure_ascii=False)}',
              "=74", "=10", "=Parent.Width-107", "=26", 12, "#16324a", "Semibold"),
        label("lblRotinaSub" + suffix, '=\"Abrir rotinas do período\"',
              "=74", "=35", "=Parent.Width-107", "=22", 9, "#718394"),
        native_icon("icoRotinaArrow" + suffix, "ChevronRight", "#007f91",
                    "=Parent.Width-24", "=24", "=16"),
        action("btnRotina" + suffix, "", f'=Reset(txtReaRotinasBusca); UpdateContext({{var_menuReaPeriodo:"{period}",var_visibleMenuReaPeriodo:true}})',
               "=0", "=0", "=Parent.Width", "=Parent.Height", f'=\"Abrir rotinas {title.lower()}\"'),
    ], "ManualLayout")


def status_formula(module_id, period):
    date = "DateValue(_ultimo.Data)"
    if period == "Diária":
        valid = f"{date} = Today()"
    elif period == "Semanal":
        valid = f"Year({date}) = Year(Today()) And WeekNum({date}) = WeekNum(Today())"
    else:
        valid = f"Year({date}) = Year(Today()) And Month({date}) = Month(Today())"
    return (
        "=With({_ultimo: First(SortByColumns(Filter(tbl_Checklist_REA_base, "
        f"ID_modulo = {module_id} And Aeroporto = ComboboxCanvasAeroSelectCalendar.Selected.Value), "
        f'"Data", SortOrder.Descending))}}, If(!IsBlank(_ultimo.Data) And {valid}, "✓", "✕"))'
    )


def calendar_row(index, title, module_id, period):
    y = 6 + index * 43
    suffix = period + str(index)
    return [
        control("linCalRow" + suffix, "GroupContainer@1.5.0", {
            "X": "=18", "Y": f"={y+40}", "Width": "=Parent.Width-36", "Height": "=1",
            "Fill": "=ColorValue(\"#edf2f6\")", "DropShadow": "=DropShadow.None",
        }, None, "ManualLayout"),
        label("lblCalRow" + suffix, f"={json.dumps(title, ensure_ascii=False)}",
              "=24", f"={y+4}", "=Parent.Width-78", "=33", 11, "#2e475c"),
        control("lblCalStatus" + suffix, "Label@2.5.1", {
            "Text": status_formula(module_id, period), "X": "=0",
            "Y": "=0", "Width": "=1", "Height": "=1", "Visible": "=false",
        }),
        native_icon("icoCalConcluida" + suffix, "CheckBadge", "#25a66c",
                    "=Parent.Width-55", f"={y+11}", "=20",
                    f'=lblCalStatus{suffix}.Text="✓"', '=\"Rotina realizada\"'),
        native_icon("icoCalPendente" + suffix, "CancelBadge", "#e24758",
                    "=Parent.Width-55", f"={y+11}", "=20",
                    f'=lblCalStatus{suffix}.Text="✕"', '=\"Rotina pendente\"'),
    ]


def calendar_group(period, rows):
    children = []
    for index, (title, module_id) in enumerate(rows):
        children.extend(calendar_row(index, title, module_id, period))
    return control("cntCal" + period, "GroupContainer@1.5.0", {
        "X": "=0", "Y": "=155", "Width": "=Parent.Width", "Height": "=Parent.Height-155",
        "Visible": f'=var_reaAbaCalendario="{period}"', "DropShadow": "=DropShadow.None",
    }, children, "ManualLayout")


def emit(node, indent=0):
    lines = []
    for name, value in node.items():
        lines.append(" " * indent + "- " + name + ":")
        lines.append(" " * (indent + 4) + "Control: " + value["Control"])
        if "ComponentName" in value:
            lines.append(" " * (indent + 4) + "ComponentName: " + value["ComponentName"])
        if "Variant" in value:
            lines.append(" " * (indent + 4) + "Variant: " + value["Variant"])
        lines.append(" " * (indent + 4) + "Properties:")
        for key, val in value["Properties"].items():
            if "\n" in val:
                lines.append(" " * (indent + 6) + key + ": |-")
                lines.extend(" " * (indent + 8) + line for line in val.splitlines())
            else:
                lines.append(" " * (indent + 6) + key + ": " + json.dumps(val, ensure_ascii=False))
        if value.get("Children"):
            lines.append(" " * (indent + 4) + "Children:")
            for child in value["Children"]:
                lines.extend(emit(child, indent + 6))
    return lines


search = find("TextInputCanvasBuscarREA")
search["Properties"] = {
    "X": "=Parent.Width-324", "Y": "=9", "Width": "=304", "Height": "=43",
    "Value": '=\"\"', "Placeholder": '=\"Buscar rotina, módulo ou termo...\"',
    "FontSize": "=12", "BorderRadius": "=0", "Fill": "=RGBA(255,255,255,1)",
    "BorderStyle": "=BorderStyle.None",
}
airport = find("ComboboxCanvasAeroSelectCalendar")
airport["Properties"].update({"X": "=20", "Y": "=55", "Width": "=Parent.Width-40",
                              "Height": "=35", "BorderRadius": "=8"})
for key in ("AlignInContainer", "LayoutMaxHeight", "LayoutMaxWidth", "LayoutMinHeight"):
    airport["Properties"].pop(key, None)

period_gallery = find("GalleryPeriodoRea")
period_gallery["Properties"].update({
    "X": "=20", "Y": "=184", "Width": "=Parent.Width-40", "Height": "=Parent.Height-204",
    "TemplateSize": "=98", "TemplatePadding": "=6",
    "WrapCount": "=If(Self.Width<520,1,2)", "Visible": "=true",
    "ShowScrollbar": "=true",
})
for key in ("LayoutMaxHeight", "LayoutMaxWidth", "LayoutMinHeight", "LayoutMinWidth"):
    period_gallery["Properties"].pop(key, None)
period_gallery["Properties"]["Items"] = period_gallery["Properties"]["Items"].replace(
    "TextInputCanvasBuscarREA.Value", "txtReaRotinasBusca.Value"
)
period_gallery["Children"] = [
    control("cntPeriodoItem", "GroupContainer@1.5.0", {
        "X": "=0", "Y": "=0", "Width": "=Parent.TemplateWidth-8",
        "Height": "=Parent.TemplateHeight-8", "Fill": "=RGBA(255,255,255,1)",
        "BorderColor": "=ColorValue(\"#e3ecf2\")", "BorderThickness": "=1",
        "DropShadow": "=DropShadow.None", "RadiusTopLeft": "=12",
        "RadiusTopRight": "=12", "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12",
    }, None, "ManualLayout"),
    control("cntPeriodoIconeFundo", "GroupContainer@1.5.0", {
        "X": "=13", "Y": "=16", "Width": "=48", "Height": "=48",
        "Fill": "=ColorValue(\"#e9f7f9\")", "DropShadow": "=DropShadow.None",
        "RadiusTopLeft": "=12", "RadiusTopRight": "=12",
        "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12",
    }, None, "ManualLayout"),
    source_icon("Image1_110", "=15", "=18", "=44", 3),
    label("lblPeriodoItem", "=ThisItem.Titulo", "=72", "=12", "=Parent.TemplateWidth-112", "=31", 11, "#17324d", "Semibold"),
    label("lblPeriodoDescricao", "=ThisItem.Descricao", "=72", "=44", "=Parent.TemplateWidth-112", "=34", 9, "#6a8290"),
    native_icon("icoPeriodoArrow", "ChevronRight", "#007f91",
                "=Parent.TemplateWidth-32", "=35", "=16"),
    control("btnPeriodoItem", "Classic/Button@2.2.0", {
        "Text": '=\"\"', "OnSelect": find("Button3_84")["Properties"]["OnSelect"],
        "Tooltip": "=ThisItem.Descricao", "X": "=0", "Y": "=0",
        "Width": "=Parent.TemplateWidth-8", "Height": "=Parent.TemplateHeight-8",
        "Fill": "=RGBA(0,0,0,0)", "HoverFill": "=RGBA(0,117,138,0.06)",
        "Color": "=RGBA(0,0,0,0)", "BorderStyle": "=BorderStyle.None",
    }),
]

routine_children = [
    routine_card("Diário", "Diárias", "=16", "Dia"),
    routine_card("Semanal", "Semanais", "=16+(Parent.Width-52)/3+10", "Sem"),
    routine_card("Mensal", "Mensais", "=16+2*((Parent.Width-52)/3+10)", "Mes"),
]

main_children = [
    control("cntReaIntro", "GroupContainer@1.5.0", {
        "Height": "=60", "Width": "=Parent.Width-8", "FillPortions": "=0",
        "DropShadow": "=DropShadow.None",
    }, [native_icon("icoReaIntro", "Warning", "#007f91", "=4", "=10", "=29"),
        label("lblReaIntroTitulo", '=\"Resposta à Emergência\"', "=44", "=0", "=Parent.Width-430", "=37", 19, "#0d2b43", "Semibold"),
        label("lblReaIntroSub", '=\"Acesse as rotinas, ferramentas e ocorrências do plano de emergência.\"',
              "=44", "=34", "=Parent.Width-430", "=27", 10, "#667c8d"),
        control("cntReaBuscaFundo", "GroupContainer@1.5.0", {
            "X": "=Parent.Width-360", "Y": "=9", "Width": "=340", "Height": "=43",
            "Fill": "=RGBA(255,255,255,1)", "DropShadow": "=DropShadow.None",
            "BorderColor": "=ColorValue(\"#e2eaf0\")", "BorderThickness": "=1",
            "RadiusTopLeft": "=10", "RadiusTopRight": "=10",
            "RadiusBottomLeft": "=10", "RadiusBottomRight": "=10",
        }, None, "ManualLayout"),
        native_icon("icoReaBusca", "Search", "#607a8a", "=Parent.Width-348", "=20", "=20"),
        {"TextInputCanvasBuscarREA": search}], "ManualLayout"),
    section("cntReaRotinas", "Rotinas", "Acesse as rotinas operacionais por período.", "CalendarBlank", "#007f91", "=0",
            "120", routine_children),
    section("cntReaGestao", "Gestão", "Ferramentas e painéis de apoio à resposta.", "Settings", "#5b50bb", "=0", "If(Parent.Width<850,280,198)",
            [gallery_card("Gallery30_8", "Gallery30_8", "Button3_118", "#f0eefe"),
             empty_state("lblGestaoVazio", "Gallery30_8")]),
    section("cntReaOcorrencias", "Ocorrências envolvendo", "Registros de acionamentos e ocorrências.", "Warning", "#dd5767", "=0", "If(Parent.Width<850,208,128)",
            [gallery_card("Gallery30_7", "Gallery30_7", "Button3_117", "#ffecf0"),
             empty_state("lblOcorrenciasVazio", "Gallery30_7")]),
    section("cntReaInspecoes", "Gerenciar Inspeções SCI", "Check-lists e inspeções operacionais.", "DockCheckProperties", "#007f91", "=0", "If(Parent.Width<850,208,128)",
            [gallery_card("Gallery30_6", "Gallery30_6", "Button3_76", "#e8f7f9"),
             empty_state("lblInspecoesVazio", "Gallery30_6")]),
]

daily = [("Check-list PCM", 69), ("Teste de Alarme", 78), ("Teste de Câmeras SCI", 77),
         ("Teste de Rádio", 75), ("Teste de Telefone", 76)]
weekly = [("Check-list Ferramenta de Suporte", 73)]
monthly = [("Teste de DEA", 123), ("Teste Eficácia do PLEM", 79),
           ("Teste Contatos de Emergência", 133), ("Atualização do controle de EPR", 147)]

tab_children = []
for i, (period, title) in enumerate((("Diária", "Diária"), ("Semanal", "Semanal"), ("Mensal", "Mensal"))):
    tab_children.extend([
        label("lblCalTab" + period, f"={json.dumps(title, ensure_ascii=False)}",
              f"={20+i*108}", "=107", "=103", "=36", 11, "#536c80", "Semibold"),
        control("linCalTab" + period, "GroupContainer@1.5.0", {
            "Fill": "=ColorValue(\"#008b9d\")", "DropShadow": "=DropShadow.None",
            "X": f"={20+i*108}", "Y": "=145", "Width": "=103", "Height": "=3",
            "Visible": f'=var_reaAbaCalendario="{period}"',
        }, None, "ManualLayout"),
        action("btnCalTab" + period, "", f'=Set(var_reaAbaCalendario,"{period}")',
               f"={20+i*108}", "=103", "=103", "=44"),
    ])

calendar_children = [
    native_icon("icoReaCalendario", "CalendarBlank", "#007f91", "=21", "=19", "=23"),
    label("lblReaCalendarioTitulo", '=\"Calendário de Rotinas\"',
          "=54", "=13", "=Parent.Width-75", "=35", 15, "#10334c", "Semibold"),
    {"ComboboxCanvasAeroSelectCalendar": airport},
    *tab_children,
    calendar_group("Diária", daily),
    calendar_group("Semanal", weekly),
    calendar_group("Mensal", monthly),
    control("cntCalNota", "GroupContainer@1.5.0", {
        "X": "=18", "Y": "=Parent.Height-110", "Width": "=Parent.Width-36", "Height": "=92",
        "Fill": "=ColorValue(\"#e8f7f9\")", "DropShadow": "=DropShadow.None",
        "RadiusTopLeft": "=12", "RadiusTopRight": "=12",
        "RadiusBottomLeft": "=12", "RadiusBottomRight": "=12",
    }, [
        control("cntCalNotaIcone", "GroupContainer@1.5.0", {
            "X": "=14", "Y": "=14", "Width": "=20", "Height": "=20",
            "Fill": "=ColorValue(\"#007f91\")", "DropShadow": "=DropShadow.None",
            "RadiusTopLeft": "=10", "RadiusTopRight": "=10",
            "RadiusBottomLeft": "=10", "RadiusBottomRight": "=10",
        }, None, "ManualLayout"),
        label("lblCalNotaIcone", '=\"i\"', "=20", "=13", "=10", "=20", 10, "#ffffff", "Bold"),
        label("lblCalNotaTitulo", '=\"Importante\"', "=42", "=12", "=Parent.Width-56", "=27", 12, "#245267", "Semibold"),
        label("lblCalNotaTexto", '=\"Mantenha as rotinas em dia para garantir a prontidão operacional.\"',
              "=14", "=40", "=Parent.Width-28", "=44", 10, "#245267"),
    ], "ManualLayout"),
]

modal_tabs = []
for tab_index, (period, title, suffix) in enumerate((
    ("Diário", "Diárias", "Dia"),
    ("Semanal", "Semanais", "Sem"),
    ("Mensal", "Mensais", "Mes"),
)):
    modal_tabs.append(control("btnReaModal" + suffix, "Classic/Button@2.2.0", {
        "Text": f'={json.dumps(title, ensure_ascii=False)}',
        "OnSelect": f'=Reset(txtReaRotinasBusca); UpdateContext({{var_menuReaPeriodo:"{period}"}})',
        "X": f'=20+{tab_index}*((Parent.Width-40)/3)', "Y": "=84",
        "Width": "=(Parent.Width-40)/3-8", "Height": "=38",
        "Fill": f'=If(var_menuReaPeriodo="{period}",ColorValue("#e5f6f8"),ColorValue("#f5f8fa"))',
        "Color": f'=If(var_menuReaPeriodo="{period}",ColorValue("#006f83"),ColorValue("#536c80"))',
        "BorderColor": f'=If(var_menuReaPeriodo="{period}",ColorValue("#8bd3dd"),ColorValue("#e2eaf0"))',
        "BorderThickness": "=1", "RadiusTopLeft": "=9", "RadiusTopRight": "=9",
        "RadiusBottomLeft": "=9", "RadiusBottomRight": "=9",
        "HoverFill": "=ColorValue(\"#d8f0f4\")",
    }))

period_modal = control("cntReaRotinasModal", "GroupContainer@1.5.0", {
    "X": "=0", "Y": "=50", "Width": "=Parent.Width", "Height": "=Parent.Height-50",
    "Fill": "=RGBA(9,31,43,0.46)", "DropShadow": "=DropShadow.None",
    "Visible": "=var_visibleMenuReaPeriodo",
}, [
    action("btnReaRotinasFundo", "", "=UpdateContext({var_visibleMenuReaPeriodo:false})",
           "=0", "=0", "=Parent.Width", "=Parent.Height", '=\"Fechar lista de rotinas\"'),
    control("cntReaRotinasPainel", "GroupContainer@1.5.0", {
        "X": "=Max(16,(Parent.Width-720)/2)", "Y": "=Max(24,(Parent.Height-560)/2)",
        "Width": "=Min(720,Parent.Width-32)", "Height": "=Min(560,Parent.Height-48)",
        "Fill": "=RGBA(255,255,255,1)", "DropShadow": "=DropShadow.Regular",
        "BorderColor": "=ColorValue(\"#dce8ee\")", "BorderThickness": "=1",
        "RadiusTopLeft": "=16", "RadiusTopRight": "=16",
        "RadiusBottomLeft": "=16", "RadiusBottomRight": "=16",
    }, [
        native_icon("icoReaRotinasModal", "CalendarBlank", "#007f91",
                    "=22", "=19", "=23"),
        label("lblReaRotinasModalTitulo", '=\"Rotinas operacionais\"',
              "=56", "=11", "=Parent.Width-116", "=34", 16, "#10334c", "Semibold"),
        label("lblReaRotinasModalAjuda", '=\"Escolha o período e abra a rotina desejada.\"',
              "=56", "=42", "=Parent.Width-116", "=27", 10, "#6a8290"),
        control("icoReaRotinasFechar", "Classic/Icon@2.5.0", {
            "Icon": "=Icon.Cancel", "Color": "=ColorValue(\"#607a8a\")",
            "X": "=Parent.Width-49", "Y": "=18", "Width": "=25", "Height": "=25",
            "OnSelect": "=UpdateContext({var_visibleMenuReaPeriodo:false})",
            "Tooltip": '=\"Fechar rotinas\"',
        }),
        control("linReaRotinasModal", "GroupContainer@1.5.0", {
            "X": "=20", "Y": "=75", "Width": "=Parent.Width-40", "Height": "=1",
            "Fill": "=ColorValue(\"#e3edf2\")", "DropShadow": "=DropShadow.None",
        }, None, "ManualLayout"),
        *modal_tabs,
        control("cntReaModalBusca", "GroupContainer@1.5.0", {
            "X": "=20", "Y": "=134", "Width": "=Parent.Width-40", "Height": "=39",
            "Fill": "=RGBA(255,255,255,1)", "DropShadow": "=DropShadow.None",
            "BorderColor": "=ColorValue(\"#dce8ee\")", "BorderThickness": "=1",
            "RadiusTopLeft": "=9", "RadiusTopRight": "=9",
            "RadiusBottomLeft": "=9", "RadiusBottomRight": "=9",
        }, None, "ManualLayout"),
        native_icon("icoReaModalBusca", "Search", "#607a8a", "=31", "=144", "=19"),
        control("txtReaRotinasBusca", "TextInput@0.0.54", {
            "X": "=58", "Y": "=134", "Width": "=Parent.Width-78", "Height": "=39",
            "Value": '=\"\"', "Placeholder": '=\"Buscar rotina neste período...\"',
            "FontSize": "=11", "Fill": "=RGBA(255,255,255,1)",
            "BorderStyle": "=BorderStyle.None", "BorderRadius": "=0",
        }),
        {"GalleryPeriodoRea": period_gallery},
        control("lblReaRotinasSemItens", "Label@2.5.1", {
            "Text": '=\"Nenhuma rotina encontrada. Experimente outro período ou termo.\"',
            "X": "=24", "Y": "=204", "Width": "=Parent.Width-48", "Height": "=46",
            "Size": "=11", "Color": "=ColorValue(\"#6a8290\")",
            "Visible": "=GalleryPeriodoRea.AllItemsCount=0",
        }),
    ], "ManualLayout"),
], "ManualLayout")

header_component = {
    "HeaderTitle_14": {
        "Control": "CanvasComponent",
        "ComponentName": "HeaderTitle",
        "Properties": {
            "Height": "=50", "Width": "=Parent.Width",
            "IconVisible": "=true", "ScreenNavigator": "=",
            "var_subtitulo1": "=", "var_subtitulo2": "=",
            "var_tituloModulo": "=var_tituloModulo",
        },
    }
}

new_screen = {
    "Properties": {
        "Fill": "=ColorValue(\"#f4f8fb\")",
        "OnVisible": '=Set(var_tituloModulo,"Resposta à Emergência"); Set(var_reaAbaCalendario,"Diária"); UpdateContext({var_visibleMenuReaPeriodo:false})',
    },
    "Children": [
        header_component,
        control("cntReaBody", "GroupContainer@1.5.0", {
            "X": "=16", "Y": "=62", "Width": "=Parent.Width-414", "Height": "=Parent.Height-74",
            "LayoutDirection": "=LayoutDirection.Vertical", "LayoutGap": "=8",
            "LayoutOverflowY": "=LayoutOverflow.Scroll", "DropShadow": "=DropShadow.None",
            "PaddingBottom": "=12", "PaddingRight": "=4",
        }, main_children, "AutoLayout"),
        control("cntReaCalendar", "GroupContainer@1.5.0", {
            "X": "=Parent.Width-382", "Y": "=62", "Width": "=366", "Height": "=Parent.Height-78",
            "DropShadow": "=DropShadow.None", "Fill": "=RGBA(255,255,255,1)",
            "BorderColor": "=ColorValue(\"#e2eaf0\")", "BorderThickness": "=1",
            "RadiusTopLeft": "=16", "RadiusTopRight": "=16",
            "RadiusBottomLeft": "=16", "RadiusBottomRight": "=16",
        }, calendar_children, "ManualLayout"),
        period_modal,
    ],
}

lines = [
    "# ScreenREA — painel moderno; gerado de msapp/Src/ScreenREA.pa.yaml.",
    "# Colar como substituição da ScreenREA existente no Power Apps Studio.",
    "Screens:", "  ScreenREA:", "    Properties:",
]
for key, val in new_screen["Properties"].items():
    lines.append("      " + key + ": " + json.dumps(val, ensure_ascii=False))
lines.append("    Children:")
for child in new_screen["Children"]:
    lines.extend(emit(child, 6))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(OUTPUT)
