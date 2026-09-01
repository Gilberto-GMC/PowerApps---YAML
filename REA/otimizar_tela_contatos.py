#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizador da tela de contatos — REA/ScreenContatos.txt.

Mesmo contrato da tela de acionamentos (2026-08-14): **não mexer no layout**.
Só performance, lógica e validade de fórmulas. A trava `guarda_layout()`
compara as duas árvores YAML e reprova qualquer propriedade alterada fora da
lista declarada — e também reprova mudança declarada que não aconteceu.

O arquivo de origem usa quebras CRLF; o processamento normaliza para LF e a
gravação restaura CRLF, para não alterar nenhum byte além do pretendido.

Ganhos:

  P1  `DelayOutput` na caixa de busca. É o maior ganho da tela: sem ele, cada
      tecla digitada recalculava DUAS coisas caras — o `Items` da galeria
      (7 `Lower(Coalesce(...))` por linha + `AddColumns` + `SortByColumns` de
      3 chaves) e o `HtmlText` do relatório `HtmlText3_2`, que refaz filtro,
      ordenação, `CountRows`/`CountIf` e um `Concat` sobre todos os contatos.
  P2  RETIRADO em 2026-08-24. Injetava `DelayItemLoading` + `LoadingSpinner`
      na galeria, mas `DelayItemLoading` é propriedade da galeria CLÁSSICA e
      não existe em `Gallery@2.15.0` (a moderna, única usada neste repo). O
      Studio descarta a propriedade em silêncio na colagem: o ganho nunca
      existiu. Ver a lição "Propriedade que o Studio descarta em silêncio" em
      LICOES_APRENDIDAS_POWERAPPS_YAML.md.
  P3  Botão Atualizar: `Refresh(tbl_contatos_entidades_log)` era desnecessário
      (o log só alimenta o painel de histórico, que já se atualiza sozinho) e o
      `Sort` do `ClearCollect` era descartado logo em seguida, porque a galeria
      e o relatório reordenam tudo. Esse botão roda no `OnVisible`, na troca de
      aeroporto e após salvar/excluir.
  P4  `OnSuccess` do formulário dava `Refresh` nas duas listas e, na sequência,
      chamava o botão Atualizar — que dava os mesmos `Refresh` de novo.
  P5  `Set(varContatoHistorico, LookUp(tbl, ID = -1))` repetia uma consulta
      idêntica à que acabara de preencher `varContatoAntes`; passa a reusar a
      variável (mesmo padrão que o botão "Atualizar" da galeria já usa).
  P6  `Reset(txtBuscarPlemPrai_2)` duplicado no botão Limpar.

Correções de fórmula:

  C1  `cmbContatosTipo` é o filtro de **Tipificação**, mas o `Default` era um
      nome de *aeroporto* (`varAeroUser`) — valor que nunca existe em
      `Choices(...tipo_entidade)`. Copiar/colar do filtro de aeroporto.
  C2  O cartão da galeria testava um campo e imprimia outro: mostrava o rótulo
      "Email:" conforme `ThisItem.email`, mas imprimia `ThisItem.email_ccr.Email`.

Executar duas vezes e conferir que o hash não muda (checklist LICOES).
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'ScreenContatos.txt')
OUT = os.path.join(HERE, 'ScreenContatosOtimizada.txt')
SCREEN = 'ScreenContatos'


def die(msg):
    sys.stderr.write('ERRO: %s\n' % msg)
    sys.exit(1)


def indent_of(line):
    return len(line) - len(line.lstrip(' '))


# ------------------------------------------------------------------ patches
PATCHES = [
    ('P5a OnVisible: reusa varContatoAntes em vez de repetir a consulta',
     '''        Set(
            varContatoHistorico,
            LookUp(
                tbl_contatos_entidades,
                ID = -1
            )
        );''',
     '''        Set(
            varContatoHistorico,
            varContatoAntes
        );''', 1),

    ('P5b Novo Contato: idem',
     '''                                Set(
                                    varContatoHistorico,
                                    LookUp(
                                        tbl_contatos_entidades,
                                        ID = -1
                                    )
                                );''',
     '''                                Set(
                                    varContatoHistorico,
                                    varContatoAntes
                                );''', 1),

    ('P3 botão Atualizar: sem refresh do log e sem sort descartado',
     '''                          =Refresh(tbl_contatos_entidades);
                          Refresh(tbl_contatos_entidades_log);

                          ClearCollect(
                              col_gerenciarContatos,
                              Sort(
                                  Filter(
                                      tbl_contatos_entidades,
                                      (
                                          IsBlank(cmbCKREAbloco_3.Selected.Value) ||
                                          Bloco = cmbCKREAbloco_3.Selected.Value
                                      ) &&
                                      (
                                          IsBlank(cmbCKREAaeroporto_3.Selected.Value) ||
                                          Aeroporto = cmbCKREAaeroporto_3.Selected.Value
                                      )
                                  ),
                                  status,
                                  SortOrder.Ascending
                              )
                          )''',
     '''                          =Refresh(tbl_contatos_entidades);

                          ClearCollect(
                              col_gerenciarContatos,
                              Filter(
                                  tbl_contatos_entidades,
                                  (
                                      IsBlank(cmbCKREAbloco_3.Selected.Value) ||
                                      Bloco = cmbCKREAbloco_3.Selected.Value
                                  ) &&
                                  (
                                      IsBlank(cmbCKREAaeroporto_3.Selected.Value) ||
                                      Aeroporto = cmbCKREAaeroporto_3.Selected.Value
                                  )
                              )
                          )''', 1),

    ('P4 OnSuccess: remove refresh duplicado pelo botão Atualizar',
     '''                              Refresh(tbl_contatos_entidades);
                              Refresh(tbl_contatos_entidades_log);

                              UpdateContext(
                                  {
                                      var_visibleFormContatos: false,
                                      var_dadosContatos: Blank()
                                  }
                              );''',
     '''                              UpdateContext(
                                  {
                                      var_visibleFormContatos: false,
                                      var_dadosContatos: Blank()
                                  }
                              );''', 1),

    ('P6 botão Limpar: Reset duplicado',
     '''                          Reset(txtBuscarPlemPrai_2);
                          Reset(txtBuscarPlemPrai_2)''',
     '''                          Reset(txtBuscarPlemPrai_2)''', 1),

    ('C1 filtro Tipificação tinha aeroporto como padrão',
     '''                              Default: |-
                                =If(varPerfilUser = "Base", varAeroUser ,
                                "")''',
     '''                              Default: =""''', 1),

    ('C2 cartão testava .email e imprimia .email_ccr.Email',
     '''"<strong>" & If(!IsBlank(ThisItem.email), "Email: ") & "</strong> ", ThisItem.email_ccr.Email,''',
     '''"<strong>" & If(!IsBlank(ThisItem.email_ccr.Email), "Email: ") & "</strong> ", ThisItem.email_ccr.Email,''', 1),
]

EXPECTED_CHANGES = {
    ('#SCREEN#', 'OnVisible'),
    ('Icon28_163', 'OnSelect'),
    ('ButtonRefreshChekREAcontatos_2', 'OnSelect'),
    ('FormCadastrarContato', 'OnSuccess'),
    ('ButtonCanvas11_29', 'OnSelect'),
    ('cmbContatosTipo', 'Default'),
    ('HtmlText7', 'HtmlText'),
}
# DelayItemLoading saiu da lista: não existe em Gallery@2.15.0 (2026-08-24)
ADDABLE = {'DelayOutput'}


# ------------------------------------------------- transformações mecânicas

def _inject(text, control_re, props, only_if=None):
    lines = text.split('\n')
    out, i, n = [], 0, 0
    while i < len(lines):
        ln = lines[i]
        out.append(ln)
        m = re.match(control_re, ln)
        if not m:
            i += 1
            continue
        ctl_ind = len(m.group(1))
        j, block = i + 1, []
        while j < len(lines):
            if lines[j].strip() and indent_of(lines[j]) < ctl_ind:
                break
            block.append(lines[j])
            j += 1
        blob = '\n'.join(block)
        props_line = ' ' * ctl_ind + 'Properties:'
        if props_line not in block or (only_if and not only_if(blob)):
            i += 1
            continue
        for ln2 in block:
            i += 1
            out.append(ln2)
            if ln2 == props_line:
                for p, v in props:
                    if not re.search(r'^\s*%s:' % p, blob, re.M):
                        out.append(' ' * (ctl_ind + 2) + '%s: =%s' % (p, v))
                        n += 1
        i += 1
    return '\n'.join(out), n


def aplicar_mecanicas(text):
    # A injeção em Gallery@ foi removida (P2): DelayItemLoading é da galeria
    # clássica e o Studio a descarta em silêncio em Gallery@2.15.0.
    n1 = 0
    text, n2 = _inject(
        text, r'^(\s*)Control: Classic/TextInput@',
        [('DelayOutput', 'true')],
        only_if=lambda b: re.search(r'HintText:[\s\S]{0,80}?(Busc|Consult|Pesquis)', b))
    print('  P1: %d propriedade(s) de performance acrescentada(s)' % (n1 + n2))
    return text


# ------------------------------------------------------------- validações

def arvore(text):
    import yaml

    class L(yaml.SafeLoader):
        pass

    L.add_constructor('tag:yaml.org,2002:value', lambda l, n: '=')
    doc = yaml.load(text, Loader=L)
    props, ordem = {}, []

    def walk(node):
        for item in node.get('Children') or []:
            (name, body), = item.items()
            body = body or {}
            ordem.append(name)
            props[name] = dict(body.get('Properties') or {})
            walk(body)

    scr = doc['Screens'][SCREEN]
    props['#SCREEN#'] = dict(scr.get('Properties') or {})
    ordem.append('#SCREEN#')
    walk(scr)
    return props, ordem


def guarda_layout(src_text, out_text):
    a, ordem_a = arvore(src_text)
    b, ordem_b = arvore(out_text)
    if ordem_a != ordem_b:
        die('a árvore de controles mudou — layout afetado')
    vistos = set()
    for name in a:
        for prop in set(a[name]) | set(b[name]):
            va = a[name].get(prop, '\0AUSENTE')
            vb = b[name].get(prop, '\0AUSENTE')
            if va == vb:
                continue
            if va == '\0AUSENTE' and prop in ADDABLE:
                continue
            if (name, prop) in EXPECTED_CHANGES:
                vistos.add((name, prop))
                continue
            die('LAYOUT ALTERADO em %s.%s — mudança não declarada' % (name, prop))
    faltando = EXPECTED_CHANGES - vistos
    if faltando:
        die('mudanças declaradas que não ocorreram: %s' % sorted(faltando))
    print('  trava de layout: OK (%d propriedades alteradas, todas declaradas)'
          % len(vistos))


def validar(src_text, out_text):
    if not out_text.startswith('Screens:\n  %s:\n    Properties:' % SCREEN):
        die('estrutura raiz inválida')

    nomes = [n.strip("'") for n in re.findall(
        r"^\s*- ('?[A-Za-z][A-Za-z0-9_ ']*)'?:$", out_text, re.M)]
    dup = sorted({n for n in nomes if nomes.count(n) > 1})
    if dup:
        die('nomes duplicados: %s' % ', '.join(dup))

    for pat, msg in [(r'^\s*Overflow:', 'Overflow:'),
                     (r'%DATACARD_', 'placeholder %DATACARD_')]:
        if re.search(pat, out_text, re.M):
            die('%s proibido' % msg)

    def control_props(blob):
        out = {}
        for m in re.finditer(r'^(\s*)Control: (\S+)\n', blob, re.M):
            ind, ctl = len(m.group(1)), m.group(2)
            for ln in blob[m.end():].split('\n'):
                if ln.strip() and indent_of(ln) < ind:
                    break
                pm = re.match(r'^\s{%d}([A-Za-z][A-Za-z0-9_]*):' % (ind + 2), ln)
                if pm:
                    out.setdefault(ctl, set()).add(pm.group(1))
        return out

    proven = control_props(src_text)
    for ctl, ps in control_props(out_text).items():
        unknown = ps - proven.get(ctl, set()) - ADDABLE
        if unknown:
            die('propriedade não comprovada em %s: %s (risco de PA2108)'
                % (ctl, ', '.join(sorted(unknown))))

    definidos = set(nomes)
    for ref in ['txtBuscarPlemPrai_2', 'cmbCKREAbloco_3', 'cmbCKREAaeroporto_3',
                'cmbContatosTipo', 'ButtonRefreshChekREAcontatos_2',
                'FormCadastrarContato', 'GalleryContatos', 'HtmlText3_2']:
        if ref not in definidos:
            die('controle referenciado não existe: %s' % ref)

    guarda_layout(src_text, out_text)


def main():
    with open(SRC, encoding='utf-8', newline='') as f:
        bruto = f.read()
    crlf = '\r\n' in bruto
    src = bruto.replace('\r\n', '\n')

    text = src
    for label, old, new, count in PATCHES:
        got = text.count(old)
        if got != count:
            die('patch "%s" casou %d vez(es), esperado %d' % (label, got, count))
        text = text.replace(old, new)
    print('  %d patches de fórmula aplicados' % len(PATCHES))

    text = aplicar_mecanicas(text)
    validar(src, text)

    final = text.replace('\n', '\r\n') if crlf else text
    with open(OUT, 'w', encoding='utf-8', newline='') as f:
        f.write(final)
    print('OK: %s (%d linhas, CRLF=%s, sha256 %s)'
          % (os.path.basename(OUT), text.count('\n'), crlf,
             hashlib.sha256(final.encode('utf-8')).hexdigest()[:16]))


if __name__ == '__main__':
    main()
