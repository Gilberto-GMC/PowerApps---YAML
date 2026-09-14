#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o Manual de Uso (PDF) do modulo Due Diligence de Terceiros.

Roda de qualquer lugar; escreve DueDiligence/Manual_Due_Diligence_de_Terceiros.pdf
na raiz do projeto. As imagens reais (capturas de tela) devem estar em
./images/<nome>.png — na ausencia delas, um retangulo cinza com o nome do
arquivo esperado eh desenhado no lugar, para o rascunho do texto poder ser
revisado antes das imagens chegarem.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.frames import Frame
from PIL import Image as PILImage

HERE = Path(__file__).resolve().parent
IMAGES_DIR = HERE / "images"

# Caminho absoluto do projeto (evita depender de quantos parents subir).
PROJECT_DUEDILIGENCE = Path(
    r"C:\Users\60-00378\OneDrive - Motiva\Área de Trabalho\PROJETOS\Power Apps - IA\DueDiligence"
)
OUT = PROJECT_DUEDILIGENCE / "Manual_Due_Diligence_de_Terceiros.pdf"

TEAL_DEEP = colors.HexColor("#005864")
TEAL = colors.HexColor("#00879A")
INK = colors.HexColor("#0F172A")
TEXT_2 = colors.HexColor("#475569")
TEXT_3 = colors.HexColor("#64748B")
HAIRLINE = colors.HexColor("#E2E8F0")
RISK_ALTO = colors.HexColor("#D93025")
RISK_BAIXO = colors.HexColor("#118D5C")
BAND_BG = colors.HexColor("#EBF5F7")

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm


# ---------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------

def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=19,
        textColor=TEAL_DEEP, spaceBefore=4, spaceAfter=14, leading=23,
    ))
    styles.add(ParagraphStyle(
        "H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13.5,
        textColor=TEAL_DEEP, spaceBefore=16, spaceAfter=8, leading=17,
        borderPadding=0,
    ))
    styles.add(ParagraphStyle(
        "H3", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=11,
        textColor=INK, spaceBefore=10, spaceAfter=5, leading=14,
    ))
    styles.add(ParagraphStyle(
        "Body", parent=styles["Normal"], fontName="Helvetica", fontSize=10,
        textColor=INK, leading=15, spaceAfter=7, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        "BodyMuted", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=9.3,
        textColor=TEXT_3, leading=13, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        "Step", parent=styles["Normal"], fontName="Helvetica", fontSize=10,
        textColor=INK, leading=15, spaceAfter=4, leftIndent=2,
    ))
    styles.add(ParagraphStyle(
        "Caption", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.7,
        textColor=TEXT_3, alignment=TA_CENTER, spaceBefore=4, spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        "Callout", parent=styles["Normal"], fontName="Helvetica", fontSize=9.7,
        textColor=TEAL_DEEP, leading=14, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        "CoverTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=30,
        textColor=colors.white, leading=35,
    ))
    styles.add(ParagraphStyle(
        "CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=13,
        textColor=colors.HexColor("#CFEAEE"), leading=18, spaceBefore=10,
    ))
    styles.add(ParagraphStyle(
        "TocEntry", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5,
        textColor=INK, leading=20,
    ))
    return styles


STYLES = build_styles()


# ---------------------------------------------------------------------
# Utilitarios de conteudo
# ---------------------------------------------------------------------

def shot(filename: str, caption: str, max_width=15.5 * cm, max_height=9.5 * cm):
    """Insere a captura de tela pelo nome do arquivo em images/, com legenda.

    Se o arquivo ainda nao existir, desenha um retangulo cinza no lugar (para
    o rascunho poder ser revisado antes das imagens chegarem).
    """
    path = IMAGES_DIR / filename
    if path.is_file():
        with PILImage.open(path) as im:
            iw, ih = im.size
        scale = min(max_width / iw, max_height / ih)
        w, h = iw * scale, ih * scale
        img = Image(str(path), width=w, height=h)
        img.hAlign = "CENTER"
        border = Table([[img]], colWidths=[w + 4], rowHeights=[h + 4])
        border.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.75, HAIRLINE),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements = [border, Paragraph(caption, STYLES["Caption"])]
    else:
        placeholder = Table(
            [[Paragraph(f"[IMAGEM PENDENTE: {filename}]", STYLES["BodyMuted"])]],
            colWidths=[max_width], rowHeights=[4.2 * cm],
        )
        placeholder.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.75, HAIRLINE),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements = [placeholder, Paragraph(caption, STYLES["Caption"])]
    return KeepTogether(elements)


def bullets(items, style="Step", bullet="•"):
    return ListFlowable(
        [ListItem(Paragraph(text, STYLES[style]), leftIndent=14) for text in items],
        bulletType="bullet", bulletFontName="Helvetica", bulletFontSize=8,
        start=bullet, spaceBefore=2, spaceAfter=10,
    )


def numbered(items, style="Step"):
    return ListFlowable(
        [ListItem(Paragraph(text, STYLES[style]), leftIndent=16) for text in items],
        bulletType="1", start=1, spaceBefore=2, spaceAfter=10,
    )


def status_table():
    rows = [
        ["Status", "Quem define", "Quando"],
        ["Aguardando Terceiro", "Sistema", "Solicitação criada no Fluxo III; questionário enviado ao terceiro."],
        ["Pendente Compliance", "Sistema", "Resposta válida do terceiro recebida; aguardando análise."],
        ["Aprovado", "Sistema ou Compliance", "Automático nos Fluxos I e II, ou parecer do Compliance."],
        ["Aprovado com Ressalvas", "Compliance", "Parecer final, com condicionantes e prazo de reavaliação."],
        ["Reprovado Parcialmente", "Compliance", "Parecer final."],
        ["Reprovado", "Compliance", "Parecer final."],
        ["Cancelado", "Compliance", "Encerramento sem parecer."],
        ["Vencido", "Sistema", "Vigência da aprovação expirou."],
    ]
    t = Table(rows, colWidths=[4.3 * cm, 3.4 * cm, 8.2 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DEEP),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, HAIRLINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def callout_box(text, color=TEAL, bg=BAND_BG):
    p = Paragraph(text, ParagraphStyle(
        "CalloutInner", parent=STYLES["Body"], textColor=INK, spaceAfter=0,
    ))
    t = Table([[p]], colWidths=[16 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3, color),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return KeepTogether([t, Spacer(1, 10)])


# ---------------------------------------------------------------------
# Fluxograma (raias Solicitante / Fornecedor / Compliance)
# ---------------------------------------------------------------------

def _wrap(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _fc_box(d, x, y, w, h, text, fill, text_color=colors.white, font_size=8.3, radius=7,
            number=None, border=None):
    rect = Rect(x, y, w, h, rx=radius, ry=radius)
    rect.fillColor = fill
    rect.strokeColor = border or fill
    rect.strokeWidth = 0.75 if border else 0
    d.add(rect)
    max_chars = max(10, int(w / (font_size * 0.52)))
    lines = _wrap(text, max_chars)
    line_h = font_size + 2.8
    top = y + h / 2 + (len(lines) - 1) * line_h / 2
    for i, line in enumerate(lines):
        d.add(String(
            x + w / 2, top - i * line_h - font_size / 3, line,
            fontName="Helvetica-Bold", fontSize=font_size,
            fillColor=text_color, textAnchor="middle",
        ))
    if number is not None:
        bcx, bcy, br = x, y + h, 9.5
        badge = Circle(bcx, bcy, br)
        badge.fillColor = fill
        badge.strokeColor = colors.white
        badge.strokeWidth = 1.3
        d.add(badge)
        d.add(String(bcx, bcy - 3.1, str(number), fontName="Helvetica-Bold",
                      fontSize=8.6, fillColor=colors.white, textAnchor="middle"))


def _fc_chip(d, x, y, text, max_chars=22, font_size=6.8, text_color=TEXT_2,
             bg=colors.white, border_color=HAIRLINE, bold=True):
    """Rotulo de conexao com fundo solido — nunca fica ilegivel sobre uma linha."""
    lines = _wrap(text, max_chars)
    line_h = font_size + 2.6
    pad_x, pad_y = 7, 4.2
    text_w = max((len(line) for line in lines), default=1) * font_size * 0.54
    box_w = text_w + 2 * pad_x
    box_h = len(lines) * line_h + 2 * pad_y - (line_h - font_size)
    rect = Rect(x - box_w / 2, y - box_h / 2, box_w, box_h, rx=5, ry=5)
    rect.fillColor = bg
    rect.strokeColor = border_color
    rect.strokeWidth = 0.7
    d.add(rect)
    top = y + (len(lines) - 1) * line_h / 2
    font_name = "Helvetica-Bold" if bold else "Helvetica"
    for i, line in enumerate(lines):
        d.add(String(x, top - i * line_h - font_size / 3 + 1, line,
                      fontName=font_name, fontSize=font_size,
                      fillColor=text_color, textAnchor="middle"))


def _fc_arrowhead(d, x2, y2, ang, color):
    size = 6.5
    spread = math.pi / 7.5
    p2x, p2y = x2 - size * math.cos(ang - spread), y2 - size * math.sin(ang - spread)
    p3x, p3y = x2 - size * math.cos(ang + spread), y2 - size * math.sin(ang + spread)
    tri = Polygon([x2, y2, p2x, p2y, p3x, p3y])
    tri.fillColor = color
    tri.strokeColor = color
    d.add(tri)


def _fc_arrow(d, x1, y1, x2, y2, color=TEXT_2, dashed=False, width=1.4):
    ln = Line(x1, y1, x2, y2)
    ln.strokeColor = color
    ln.strokeWidth = width
    if dashed:
        ln.strokeDashArray = [4, 3]
    d.add(ln)
    _fc_arrowhead(d, x2, y2, math.atan2(y2 - y1, x2 - x1), color)


def _fc_elbow(d, points, color=TEXT_2, dashed=False, width=1.4):
    """Conector em angulo reto (cotovelo), para desviar de caixas no caminho."""
    for (x1, y1), (x2, y2) in zip(points[:-1], points[1:]):
        ln = Line(x1, y1, x2, y2)
        ln.strokeColor = color
        ln.strokeWidth = width
        if dashed:
            ln.strokeDashArray = [4, 3]
        d.add(ln)
    (x1, y1), (x2, y2) = points[-2], points[-1]
    _fc_arrowhead(d, x2, y2, math.atan2(y2 - y1, x2 - x1), color)


def build_flowchart() -> Drawing:
    W, H = 468, 660
    d = Drawing(W, H)

    col_w, gap_x = 148, 8
    c1x, c2x, c3x = 6, 6 + col_w + gap_x, 6 + 2 * (col_w + gap_x)
    c1_mid, c2_mid, c3_mid = c1x + col_w / 2, c2x + col_w / 2, c3x + col_w / 2
    full_w = c3x + col_w - c1x

    def bx(cx):
        return cx + 6

    bw = col_w - 12

    head_y, head_h = 618, 30
    lanes = [
        (c1x, "SOLICITANTE", TEAL_DEEP),
        (c2x, "FORNECEDOR (TERCEIRO)", colors.HexColor("#0F766E")),
        (c3x, "COMPLIANCE", colors.HexColor("#334155")),
    ]
    # fundo de cada raia (grupo de fundo, atrás das caixas)
    for x, _, _tint in lanes:
        band = Rect(x, 14, col_w, head_y - 14, rx=8, ry=8)
        band.fillColor = colors.HexColor("#F8FAFC")
        band.strokeColor = HAIRLINE
        band.strokeWidth = 0.6
        d.add(band)
    for x, label, tint in lanes:
        _fc_box(d, x, head_y, col_w, head_h, label, tint, font_size=8.6, radius=6)

    # ---- Passo 1: Solicitante cadastra ---------------------------------
    rA_y, rA_h = 560, 44
    _fc_box(d, bx(c1x), rA_y, bw, rA_h,
            "Cadastra a solicitação e responde o questionário interno",
            TEAL, font_size=8, border=TEAL_DEEP, number=1)

    # ---- Passo 2: calculo de risco --------------------------------------
    rB_y, rB_h = 480, 44
    _fc_box(d, bx(c1x), rB_y, bw, rB_h,
            "Sistema calcula o risco automaticamente",
            colors.HexColor("#0E7490"), font_size=8, border=TEAL_DEEP, number=2)
    _fc_arrow(d, c1_mid, rA_y, c1_mid, rB_y + rB_h, TEXT_2)

    # ---- Passo 3: Fornecedor responde (Fluxo III) -----------------------
    rC_y, rC_h = 480, 44  # mesma altura do passo 2: liga com um conector horizontal
    _fc_box(d, bx(c2x), rC_y, bw, rC_h,
            "Recebe o questionário por e-mail e responde",
            colors.HexColor("#0F766E"), font_size=8, border=colors.HexColor("#0B4F49"), number=3)
    mid_y = rB_y + rB_h / 2
    _fc_arrow(d, bx(c1x) + bw, mid_y, bx(c2x), mid_y, RISK_ALTO)
    _fc_chip(d, (bx(c1x) + bw + bx(c2x)) / 2, rA_y - 14,
             "Risco alto ou gatilho crítico", max_chars=20, text_color=RISK_ALTO)

    # ---- Passo 4: Compliance recebe e analisa ----------------------------
    rD_y, rD_h = 378, 50
    _fc_box(d, bx(c3x), rD_y, bw, rD_h,
            "Recebe as respostas já classificadas por risco e analisa",
            colors.HexColor("#334155"), font_size=8, border=colors.HexColor("#1E293B"), number=4)
    # entra pelo topo, deslocado do canto (o canto é ocupado pelo numero do passo)
    _fc_arrow(d, bx(c2x) + bw, rC_y, bx(c3x) + 24, rD_y + rD_h, TEXT_2)

    # ---- Passo 5: Aguardando esclarecimentos -----------------------------
    rE_y, rE_h = 300, 44
    _fc_box(d, bx(c3x), rE_y, bw, rE_h,
            "Aguardando esclarecimentos, se necessário",
            colors.HexColor("#64748B"), font_size=7.6, border=colors.HexColor("#334155"), number=5)
    _fc_arrow(d, c3_mid, rD_y, c3_mid, rE_y + rE_h, TEXT_2)

    # loop de esclarecimentos ate o fornecedor — roteado pelo corredor entre as
    # raias 2 e 3, em cotovelo, para nunca cruzar por cima de nenhuma caixa
    gx = c3x - gap_x / 2
    loop_y0 = rE_y + rE_h / 2
    loop_y1 = rC_y + rC_h / 2
    _fc_elbow(d, [
        (bx(c3x), loop_y0),
        (gx, loop_y0),
        (gx, 360),
        (gx, loop_y1),
        (bx(c2x) + bw, loop_y1),
    ], color=TEXT_3, dashed=True)
    _fc_chip(d, gx, 360, "Troca de mensagens", max_chars=24, text_color=TEXT_3, bold=False)

    # ---- Passo 6: Parecer final ------------------------------------------
    rF_y, rF_h = 226, 44
    _fc_box(d, bx(c3x), rF_y, bw, rF_h,
            "Registra o parecer final",
            colors.HexColor("#334155"), font_size=8, border=colors.HexColor("#1E293B"), number=6)
    _fc_arrow(d, c3_mid, rE_y, c3_mid, rF_y + rF_h, TEXT_2)

    # ---- Passo 7: decisao final (largura toda) -----------------------------
    rG_y, rG_h = 148, 52
    _fc_box(d, c1x, rG_y, full_w, rG_h,
            "Decisão: Aprovado · Aprovado com Ressalvas · Reprovado Parcialmente · "
            "Reprovado · Cancelado",
            colors.HexColor("#0F172A"), font_size=8.2, number=7)
    _fc_arrow(d, c3_mid, rF_y, c3_mid, rG_y + rG_h, TEXT_2)

    # atalho: risco baixo/medio sem gatilho vai direto para a decisao
    _fc_arrow(d, c1_mid, rB_y, c1_mid, rG_y + rG_h, RISK_BAIXO)
    _fc_chip(d, c1_mid, (rB_y + rG_y + rG_h) / 2,
             "Risco baixo/médio sem gatilho: aprovação automática",
             max_chars=20, text_color=RISK_BAIXO)

    # ---- Passo 8: laudo final -----------------------------------------------
    rH_y, rH_h = 68, 42
    _fc_box(d, c1x, rH_y, full_w, rH_h,
            "Laudo final disponível para download — qualquer usuário",
            TEAL_DEEP, font_size=8.4, number=8)
    _fc_arrow(d, c1x + full_w / 2, rG_y, c1x + full_w / 2, rH_y + rH_h, TEXT_2)

    # ---- legenda --------------------------------------------------------------
    leg_y = 24
    ln = Line(c1x, leg_y, c1x + 26, leg_y)
    ln.strokeColor = TEXT_2
    ln.strokeWidth = 1.4
    d.add(ln)
    d.add(String(c1x + 32, leg_y - 3, "fluxo principal", fontName="Helvetica", fontSize=7, fillColor=TEXT_3))
    ln2 = Line(c1x + 148, leg_y, c1x + 174, leg_y)
    ln2.strokeColor = TEXT_3
    ln2.strokeWidth = 1.4
    ln2.strokeDashArray = [4, 3]
    d.add(ln2)
    d.add(String(c1x + 180, leg_y - 3, "esclarecimento (troca de mensagens)",
                  fontName="Helvetica", fontSize=7, fillColor=TEXT_3))

    d.hAlign = "CENTER"
    return d


# ---------------------------------------------------------------------
# Cabecalho / rodape
# ---------------------------------------------------------------------

def draw_header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFillColor(TEXT_3)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(MARGIN, PAGE_H - 1.3 * cm, "DUE DILIGENCE DE TERCEIROS — MANUAL DE USO")
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.3 * cm, "Integrity Hub • Compliance")
        canvas.setStrokeColor(HAIRLINE)
        canvas.line(MARGIN, PAGE_H - 1.5 * cm, PAGE_W - MARGIN, PAGE_H - 1.5 * cm)
        canvas.line(MARGIN, 1.55 * cm, PAGE_W - MARGIN, 1.55 * cm)
        canvas.drawString(MARGIN, 1.15 * cm, "Uso interno — ASUR Brasil")
        canvas.drawRightString(PAGE_W - MARGIN, 1.15 * cm, f"Página {doc.page - 1}")
    canvas.restoreState()


def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(TEAL_DEEP)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 9 * cm, PAGE_W, 9 * cm, fill=1, stroke=0)
    canvas.setFillColor(TEAL_DEEP)
    canvas.rect(0, PAGE_H - 9 * cm, PAGE_W, 0.12 * cm, fill=1, stroke=0)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(MARGIN, PAGE_H - 2.2 * cm, "ASUR BRASIL")
    canvas.setFont("Helvetica", 9.5)
    canvas.setFillColor(colors.HexColor("#CFEAEE"))
    canvas.drawString(MARGIN, PAGE_H - 2.7 * cm, "COMPLIANCE & INTEGRIDADE")

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 30)
    canvas.drawString(MARGIN, PAGE_H - 5.6 * cm, "Manual de Uso")
    canvas.setFont("Helvetica-Bold", 20)
    canvas.drawString(MARGIN, PAGE_H - 6.5 * cm, "Due Diligence de Terceiros")
    canvas.setFont("Helvetica", 12)
    canvas.setFillColor(colors.HexColor("#E3F3F5"))
    canvas.drawString(MARGIN, PAGE_H - 7.4 * cm, "Guia completo para solicitantes e para a equipe de Compliance")

    canvas.setFillColor(INK)
    canvas.setFont("Helvetica", 10)
    canvas.drawString(MARGIN, 3.6 * cm, "Módulo Integrity Hub — Power Apps, SharePoint e Power Automate")
    canvas.setFillColor(TEXT_3)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(MARGIN, 3.1 * cm, "Documento de uso interno. Versão 1.0 — setembro de 2026.")
    canvas.restoreState()


# ---------------------------------------------------------------------
# Conteudo
# ---------------------------------------------------------------------

def build_story():
    S = STYLES
    story = [NextPageTemplate("normal"), PageBreak()]

    # ---- Sumario ---------------------------------------------------
    story.append(Paragraph("Sumário", S["H1"]))
    toc_items = [
        "1. Sobre o sistema",
        "2. Perfis de acesso",
        "3. Visão geral do fluxo",
        "4. Tela inicial",
        "5. Criando uma nova solicitação",
        "6. O que acontece depois do envio",
        "7. Acompanhando solicitações — Registros",
        "8. Entendendo os status",
        "9. Para o Compliance — analisando uma solicitação",
        "10. Aguardando esclarecimentos",
        "11. Registrando o parecer final",
        "12. Histórico e anexos",
        "13. Painel de indicadores",
        "14. Baixando o laudo final",
        "15. Perguntas frequentes",
    ]
    for item in toc_items:
        story.append(Paragraph(item, S["TocEntry"]))
    story.append(PageBreak())

    # ---- 1. Sobre o sistema ----------------------------------------
    story.append(Paragraph("1. Sobre o sistema", S["H1"]))
    story.append(Paragraph(
        "O módulo Due Diligence de Terceiros substitui o antigo sistema Esflow e organiza, num só lugar, "
        "toda a avaliação de integridade de fornecedores, clientes e outras contrapartes da ASUR Brasil. "
        "Ele cobre o ciclo inteiro: o cadastro da solicitação, o questionário respondido pelo terceiro, a "
        "análise do Compliance e o parecer final — com histórico completo e um laudo consolidado ao fim.",
        S["Body"],
    ))
    story.append(Paragraph(
        "O sistema calcula automaticamente o risco de cada contraparte e decide sozinho o caminho da "
        "solicitação: casos de baixo risco são encerrados sem intervenção manual, casos de risco médio "
        "seguem um caminho simplificado, e só os casos que realmente precisam de atenção chegam à mesa do "
        "Compliance.",
        S["Body"],
    ))
    story.append(callout_box(
        "<b>Por que isso importa:</b> due diligence de terceiros é um requisito legal e regulatório — um "
        "pilar obrigatório dos Programas de Integridade. Ter um processo estruturado e rastreável é o que "
        "protege a companhia em fiscalizações e auditorias.",
    ))

    # ---- 2. Perfis de acesso -----------------------------------------
    story.append(Paragraph("2. Perfis de acesso", S["H1"]))
    story.append(Paragraph(
        "O sistema reconhece automaticamente dois perfis, pelo login do usuário — não é preciso escolher "
        "um perfil ao entrar.",
        S["Body"],
    ))
    story.append(Paragraph("Solicitante", S["H3"]))
    story.append(Paragraph(
        "Qualquer colaborador pode abrir uma nova solicitação de due diligence para uma contraparte que "
        "vai contratar. Depois de enviada, o solicitante acompanha o andamento e recebe o resultado, mas "
        "não participa da análise interna do Compliance.",
        S["Body"],
    ))
    story.append(Paragraph("Compliance", S["H3"]))
    story.append(Paragraph(
        "Usuários cadastrados na lista de analistas de Compliance têm acesso à análise completa: veem as "
        "respostas do terceiro, registram esclarecimentos, lançam o parecer final e enxergam o histórico "
        "interno (inclusive anotações que não aparecem para o solicitante). Esse acesso é liberado pela "
        "área de Compliance, cadastrando o e-mail do analista na lista de perfis autorizados — não é algo "
        "que o próprio usuário ativa.",
        S["Body"],
    ))

    # ---- 3. Visão geral do fluxo -------------------------------------
    story.append(Paragraph("3. Visão geral do fluxo", S["H1"]))
    story.append(Paragraph(
        "Toda solicitação passa pelo mesmo raciocínio, ainda que o caminho final dependa do risco "
        "identificado:",
        S["Body"],
    ))
    story.append(numbered([
        "<b>Solicitação</b> — o colaborador cadastra a contraparte e responde um questionário interno "
        "sobre o contrato.",
        "<b>Cálculo de risco</b> — o sistema classifica a solicitação automaticamente e decide o fluxo: "
        "encerramento automático (risco baixo), monitoramento simplificado (risco médio) ou envio de "
        "questionário ao terceiro (risco alto ou gatilho crítico identificado).",
        "<b>Terceiro</b> — quando aplicável, a contraparte recebe por e-mail um questionário próprio, sem "
        "precisar de acesso ao sistema.",
        "<b>Compliance</b> — as respostas voltam classificadas por risco; o Compliance analisa, pode "
        "registrar esclarecimentos e, ao final, lança o parecer.",
        "<b>Decisão</b> — aprovado, aprovado com ressalvas, reprovado (total ou parcialmente) ou "
        "cancelado. Aprovações abrem uma vigência de 1 a 3 anos, conforme o risco.",
    ]))
    story.append(Paragraph(
        "Um gatilho crítico (por exemplo, o terceiro atuar em nome da companhia perante o poder público, "
        "ou ter sido indicado por um agente público) sempre força a análise do Compliance — mesmo quando "
        "existe uma obrigação legal de pagamento, que sozinha encerraria a solicitação automaticamente. "
        "Entre os dois, o gatilho crítico tem prioridade.",
        S["Body"],
    ))
    story.append(Spacer(1, 6))
    story.append(KeepTogether([
        build_flowchart(),
        Paragraph(
            "Figura 1 — Fluxograma do processo, por raia de responsabilidade "
            "(Solicitante, Fornecedor/Terceiro e Compliance).",
            S["Caption"],
        ),
    ]))

    # ---- 4. Tela inicial ----------------------------------------------
    story.append(Paragraph("4. Tela inicial", S["H1"]))
    story.append(Paragraph(
        "É a porta de entrada do módulo. Mostra o fluxo de conformidade em quatro etapas — Solicitação, "
        "Terceiro, Compliance e Decisão — e identifica o usuário que está com a sessão aberta, com data e "
        "hora do acesso.",
        S["Body"],
    ))
    story.append(shot("tela_inicial.png", "Figura 2 — Tela inicial do módulo Due Diligence."))
    story.append(Paragraph(
        "Dois botões levam ao restante do sistema: <b>Acessar o módulo de Due Diligence</b>, que abre a "
        "tela de registros e o formulário de nova solicitação, e <b>Painel de indicadores</b>, com a visão "
        "gerencial detalhada na seção 13.",
        S["Body"],
    ))

    # ---- 5. Criando uma nova solicitação -------------------------------
    story.append(Paragraph("5. Criando uma nova solicitação", S["H1"]))
    story.append(Paragraph(
        "No botão <b>+ Nova Solicitação</b>, no topo da tela de registros, o solicitante preenche um "
        "formulário único cobrindo a identificação da contraparte e as perguntas de avaliação de risco. "
        "Os principais campos:",
        S["Body"],
    ))
    story.append(bullets([
        "<b>Aeroporto</b> e <b>área solicitante</b> — de onde parte a demanda.",
        "<b>CNPJ/CPF e razão social</b> — identificação da contraparte.",
        "<b>Categoria da contraparte</b> — fornecedor, cliente, órgão público, associação/sindicato, "
        "entre outras. Essa escolha já direciona boa parte da classificação de risco.",
        "<b>Objeto da contratação</b> e <b>tipo de contrato</b> — o que está sendo contratado.",
        "<b>Perguntas de gatilho</b> — subcontratação, procuração, pagamento em nome de terceiro, "
        "representação perante o poder público, indicação por agente público, entre outras. Qualquer "
        "resposta \"Sim\" aqui é o que caracteriza um gatilho crítico.",
    ]))
    story.append(callout_box(
        "<b>Atenção:</b> depois de enviada, a solicitação fica somente leitura para o solicitante — a "
        "única exceção é quando o envio do questionário ao terceiro falha (por exemplo, e-mail incorreto), "
        "caso em que o solicitante pode corrigir os dados e reenviar.",
    ))
    story.append(Paragraph(
        "Ao salvar, o sistema calcula o risco na hora e decide o caminho — sem que o solicitante precise "
        "fazer nada além de preencher o formulário corretamente.",
        S["Body"],
    ))

    # ---- 6. O que acontece depois do envio -----------------------------
    story.append(Paragraph("6. O que acontece depois do envio", S["H1"]))
    story.append(Paragraph(
        "Três caminhos são possíveis, dependendo do resultado do cálculo de risco:",
        S["Body"],
    ))
    story.append(bullets([
        "<b>Risco baixo, sem gatilho</b> — a solicitação é aprovada automaticamente e já sai com vigência "
        "de 3 anos. Nenhuma ação humana é necessária.",
        "<b>Risco médio, sem gatilho</b> — mesma lógica, com vigência de 2 anos.",
        "<b>Risco alto ou gatilho identificado</b> — o sistema envia automaticamente, por e-mail, um "
        "questionário específico para o e-mail de contato informado da contraparte, usando Microsoft "
        "Forms. A contraparte responde sem precisar de acesso ao sistema; assim que envia, as respostas "
        "voltam classificadas por risco e a solicitação passa para a análise do Compliance.",
    ]))
    story.append(Paragraph(
        "Se o e-mail de envio falhar (endereço incorreto, por exemplo), a solicitação mostra \"Falha no "
        "envio\" e o solicitante pode corrigir o e-mail e pedir um novo envio pelo próprio registro.",
        S["Body"],
    ))

    # ---- 7. Registros --------------------------------------------------
    story.append(Paragraph("7. Acompanhando solicitações — Registros", S["H1"]))
    story.append(Paragraph(
        "A aba <b>Registros</b> lista todas as solicitações visíveis para o usuário, com busca por ID, "
        "razão social ou CNPJ/CPF, e filtro por status e por período de criação (data inicial e final). "
        "Cada linha mostra o número da solicitação, a data, a razão social, o documento, a pontuação, a "
        "classificação de risco (visível só para o Compliance) e o status atual, com um selo colorido.",
        S["Body"],
    ))
    story.append(shot("tela_registros.png", "Figura 3 — Lista de registros, com filtros e status."))
    story.append(Paragraph(
        "A coluna <b>Ações</b>, à direita de cada linha, oferece — conforme o status e o perfil do usuário "
        "— <b>Ver</b>, <b>Editar/Analisar</b>, <b>Reenviar Forms</b> (só quando aplicável), <b>Excluir</b> e "
        "<b>Baixar Laudo</b> (só depois do parecer final — ver seção 14).",
        S["Body"],
    ))

    # ---- 8. Status -------------------------------------------------------
    story.append(Paragraph("8. Entendendo os status", S["H1"]))
    story.append(Paragraph(
        "Toda solicitação está sempre em um destes oito status. A vigência (1, 2 ou 3 anos) começa a "
        "contar a partir da aprovação, conforme o risco identificado.",
        S["Body"],
    ))
    story.append(status_table())
    story.append(Spacer(1, 8))

    # ---- 9. Analisando -----------------------------------------------
    story.append(Paragraph("9. Para o Compliance — analisando uma solicitação", S["H1"]))
    story.append(Paragraph(
        "Assim que uma solicitação chega a <b>Pendente Compliance</b>, qualquer analista pode clicar em "
        "<b>Analisar</b>. O primeiro registro grava automaticamente o analista responsável. À direita, o "
        "painel <b>Respostas do terceiro</b> mostra cada pergunta, a resposta recebida e a classificação de "
        "risco individual — as respostas de risco alto aparecem destacadas.",
        S["Body"],
    ))
    story.append(shot("tela_respostas_terceiro.png",
                       "Figura 4 — Resumo da avaliação e respostas do terceiro."))
    story.append(Paragraph(
        "O resumo no topo da tela (Classificação da contraparte, Respostas do terceiro, Gatilho de due "
        "diligence e Situação da análise) dá o panorama da solicitação sem precisar rolar a tela inteira.",
        S["Body"],
    ))

    # ---- 10. Esclarecimentos ------------------------------------------
    story.append(Paragraph("10. Aguardando esclarecimentos", S["H1"]))
    story.append(Paragraph(
        "Quando a análise exige mais informação da contraparte, o Compliance registra um desdobramento do "
        "tipo <b>Aguardando esclarecimentos</b> — tanto para anotar a pergunta enviada quanto a resposta "
        "recebida depois. Esse tipo não altera o status da solicitação, que continua em Pendente "
        "Compliance durante toda a troca.",
        S["Body"],
    ))
    story.append(Paragraph("No formulário de análise, cada registro tem:", S["Body"]))
    story.append(bullets([
        "<b>Tipo de desdobramento</b> — Aguardando esclarecimentos, Parecer final ou Cancelamento.",
        "<b>Novo status</b> — preenchido automaticamente conforme o tipo escolhido.",
        "<b>Descrição / parecer / resposta</b> — o texto livre da pergunta, resposta ou parecer.",
        "<b>Visível ao solicitante</b> — controla se esse registro aparece no histórico que o solicitante "
        "enxerga. Por padrão, esclarecimentos ficam internos; parecer final e cancelamento sempre ficam "
        "visíveis.",
        "<b>Prazo para resposta</b> (opcional) — uma data de referência para cobrar o retorno.",
        "<b>Anexos</b> — para guardar o e-mail da troca ou qualquer documento de apoio.",
    ]))
    story.append(shot("tela_analise_compliance.png",
                       "Figura 5 — Formulário de análise do Compliance."))

    # ---- 11. Parecer final -----------------------------------------------
    story.append(Paragraph("11. Registrando o parecer final", S["H1"]))
    story.append(Paragraph(
        "Para concluir a análise, escolha o tipo <b>Parecer final</b>. O campo Novo status passa a aceitar "
        "só as quatro decisões possíveis:",
        S["Body"],
    ))
    story.append(bullets([
        "<b>Aprovado</b> — sem ressalvas.",
        "<b>Aprovado com Ressalvas</b> — exige condicionantes descritas e um prazo de reavaliação.",
        "<b>Reprovado Parcialmente</b>",
        "<b>Reprovado</b>",
    ]))
    story.append(Paragraph(
        "As três primeiras decisões abrem vigência (1 a 3 anos, conforme o risco); Reprovado não abre "
        "vigência. Para encerrar sem análise de mérito — por exemplo, se a contratação foi cancelada — use "
        "o tipo <b>Cancelamento</b> em vez de um parecer.",
        S["Body"],
    ))
    story.append(callout_box(
        "Depois do parecer final, a solicitação volta a ficar somente leitura. Para reavaliar uma "
        "contraparte depois de vencida a vigência, é preciso abrir uma nova solicitação — o histórico da "
        "anterior é preservado.",
    ))

    # ---- 12. Historico -----------------------------------------------------
    story.append(Paragraph("12. Histórico e anexos", S["H1"]))
    story.append(Paragraph(
        "Cada solicitação guarda uma linha do tempo completa: criação, envio ao terceiro, resposta "
        "recebida, esclarecimentos e o parecer final — cada entrada com data, autor e a mudança de status "
        "associada. Anotações internas do Compliance (marcadas como não visíveis ao solicitante) aparecem "
        "com um selo \"INTERNO COMPLIANCE\" e só quem tem esse perfil consegue vê-las.",
        S["Body"],
    ))
    story.append(shot("tela_historico.png", "Figura 6 — Histórico da solicitação."))
    story.append(Paragraph(
        "Quando um registro do histórico tem um arquivo anexado (o e-mail de uma troca com o terceiro, por "
        "exemplo), o anexo aparece logo abaixo do card correspondente e pode ser aberto com um clique.",
        S["Body"],
    ))

    # ---- 13. Painel -------------------------------------------------------
    story.append(Paragraph("13. Painel de indicadores", S["H1"]))
    story.append(Paragraph(
        "Disponível só para o perfil Compliance, o painel dá a visão gerencial do processo inteiro, "
        "combinando a situação do dia com uma janela de período configurável (padrão: últimos 12 meses).",
        S["Body"],
    ))
    story.append(Paragraph("Situação atual", S["H3"]))
    story.append(Paragraph(
        "Mostra, independentemente do período escolhido: vigências vencidas ou a vencer nos próximos 90 "
        "dias, e pendências fora do prazo — quanto tempo o terceiro ou o Compliance estão levando para "
        "responder, com destaque para quem já ultrapassou o prazo de referência (10 dias para o terceiro, "
        "5 dias para o Compliance).",
        S["Body"],
    ))
    story.append(shot("painel_situacao.png", "Figura 7 — Painel: situação atual e solicitações no período."))
    story.append(Paragraph("Solicitações no período", S["H3"]))
    story.append(Paragraph(
        "Quantidade total, quantas estão em andamento, aprovadas, reprovadas e canceladas, além da "
        "distribuição por aeroporto, área solicitante, classificação de risco, categoria da contraparte e "
        "tipo de contrato — útil para identificar onde o volume está concentrado.",
        S["Body"],
    ))
    story.append(Paragraph("Tempo de resposta e SLA", S["H3"]))
    story.append(Paragraph(
        "Média e mediana de dias em cada etapa do ciclo (envio do questionário, resposta do terceiro, "
        "análise do Compliance e ciclo completo), com o percentual de casos dentro do prazo de referência "
        "de cada etapa.",
        S["Body"],
    ))
    story.append(shot("painel_distribuicoes.png",
                       "Figura 8 — Painel: distribuições e tempo de resposta."))

    # ---- 14. Laudo -----------------------------------------------------
    story.append(Paragraph("14. Baixando o laudo final", S["H1"]))
    story.append(Paragraph(
        "É a entrega final do processo: um documento único que consolida a identificação da contraparte, "
        "a classificação de risco, o parecer do Compliance, as respostas do terceiro (quando houver) e a "
        "linha do tempo completa — pronto para arquivar como evidência em auditorias e fiscalizações.",
        S["Body"],
    ))
    story.append(Paragraph(
        "O botão <b>Baixar Laudo</b>, na lista de registros, fica disponível assim que a solicitação "
        "recebe uma das quatro decisões finais (Aprovado, Aprovado com Ressalvas, Reprovado Parcialmente ou "
        "Reprovado) — <b>qualquer usuário</b> com acesso à solicitação pode baixar, não só o Compliance, "
        "quantas vezes precisar.",
        S["Body"],
    ))
    story.append(shot("laudo_final.png", "Figura 9 — Laudo final de Due Diligence."))
    story.append(Paragraph(
        "O arquivo é aberto no navegador; para guardar como PDF, use Ctrl+P e escolha \"Salvar como PDF\" "
        "no destino da impressão.",
        S["Body"],
    ))

    # ---- 15. FAQ -----------------------------------------------------
    story.append(Paragraph("15. Perguntas frequentes", S["H1"]))

    faqs = [
        ("Enviei a solicitação e ela sumiu da minha lista, o que houve?",
         "Provavelmente não sumiu — confira o filtro de status e o período de data na tela de Registros. "
         "Solicitações aprovadas automaticamente continuam na lista, só que com status Aprovado."),
        ("O terceiro perdeu o e-mail do questionário, como reenviar?",
         "Na lista de Registros, com a solicitação em Aguardando Terceiro, use a ação Reenviar Forms. Se o "
         "problema for o e-mail cadastrado, edite a solicitação (opção disponível quando o envio anterior "
         "falhou) e corrija o endereço antes de reenviar."),
        ("Por que não vejo a classificação de risco nem o botão Analisar?",
         "Esses itens são exclusivos do perfil Compliance. Se você deveria ter esse acesso, peça à área de "
         "Compliance para confirmar seu cadastro na lista de analistas autorizados."),
        ("O botão Baixar Laudo está desabilitado, por quê?",
         "O laudo só fica disponível depois do parecer final (Aprovado, Aprovado com Ressalvas, Reprovado "
         "Parcialmente ou Reprovado). Enquanto a solicitação estiver em Aguardando Terceiro ou Pendente "
         "Compliance, o botão fica bloqueado — passe o mouse sobre ele para ver o motivo."),
        ("A vigência de uma aprovação venceu, o que fazer?",
         "Abra uma nova solicitação de due diligence para a mesma contraparte. O sistema marca "
         "automaticamente o registro anterior como Vencido e preserva todo o histórico e o laudo antigo "
         "para consulta."),
    ]
    for question, answer in faqs:
        story.append(KeepTogether([
            Paragraph(question, S["H3"]),
            Paragraph(answer, S["Body"]),
        ]))

    return story


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
        title="Manual de Uso — Due Diligence de Terceiros",
        author="ASUR Brasil — Compliance & Integridade",
    )
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0,
                         topPadding=0, bottomPadding=0)
    normal_frame = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN - 0.4 * cm, id="normal")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
        PageTemplate(id="normal", frames=[normal_frame], onPage=draw_header_footer),
    ])
    # SimpleDocTemplate comeca no primeiro template da lista ("cover"); um
    # unico Spacer ocupa essa pagina (o desenho da capa vem do onPage), e
    # build_story() troca para "normal" antes do Sumario.
    full_story = [Spacer(1, 0)] + build_story()
    doc.build(full_story)
    print(f"Gerado: {OUT}")


if __name__ == "__main__":
    main()
