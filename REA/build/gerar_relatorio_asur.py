"""Aplica somente os ajustes de PDF sobre a edição final enviada pelo usuário."""

from pathlib import Path
from powerapps_yaml import controls, parse_studio, set_property

ROOT = Path(__file__).resolve().parents[1]
MODELO = ROOT / "modelos" / "frmRelatoriosOcorrencias_usuario.pa.yaml"
DESTINOS = (
    ROOT / "out" / "frmRelatoriosOcorrencias_FINAL.pa.yaml",
    ROOT / "out" / "frmRelatoriosOcorrencias_ASUR.pa.yaml",
    ROOT / "msapp" / "Src" / "frmRelatoriosOcorrencias.pa.yaml",
)


def gerar():
    texto = MODELO.read_text(encoding="utf-8")
    for nome in ("cntDocumentoRelatorioRea", "cntAcoesRelatorioRea"):
        for propriedade, valor in (
            ("AlignInContainer", "=AlignInContainer.Center"),
            ("LayoutMinWidth", "=820"),
            ("LayoutMaxWidth", "=820"),
        ):
            texto = set_property(texto, nome, propriedade, valor)

    arvore, _ = parse_studio(texto)
    criar = controls(arvore)["btnCriarPdfRea"][0]["Properties"]["OnSelect"]
    alvo = '                    ExpandContainers: true,'
    if criar.count(alvo) != 1:
        raise ValueError("A fórmula PDF do modelo mudou; revisar antes de gerar.")
    criar = criar.replace(alvo, '                    Size: "A4",\n                    DPI: 96,\n' + alvo)
    texto = set_property(texto, "btnCriarPdfRea", "OnSelect", criar)
    texto = set_property(texto, "btnAbrirPdfRea", "OnSelect", '''=If(
    IsBlank(TrimEnds(varUrlPdfRea)),
    Notify("Gere o PDF antes de abrir.", NotificationType.Warning),
    Launch(TrimEnds(varUrlPdfRea), {}, LaunchTarget.New)
)''')
    parse_studio(texto)
    for destino in DESTINOS:
        destino.write_text(texto, encoding="utf-8", newline="\n")
        print(destino.relative_to(ROOT))
    entrega = '''# Relatório REA — versão final ajustada

Base: TXT editado pelo usuário. Código completo da tela para substituir a versão
atual de `frmRelatoriosOcorrencias` no Power Apps Studio.

```yaml
''' + texto + '''```

## O que eu ajustei

- [cntDocumentoRelatorioRea / AlignInContainer, LayoutMinWidth, LayoutMaxWidth] —
  largura sem limites explícitos no AutoLayout → centro e mínimo/máximo de 820 →
  fixar a grade usada pelo documento exportado.
- [cntAcoesRelatorioRea / mesmas propriedades] — barra sem os limites do documento →
  centro e mínimo/máximo de 820 → alinhar os botões à largura do relatório.
- [btnCriarPdfRea.OnSelect] — tamanho do papel e resolução implícitos → A4 e 96 DPI →
  tornar explícitos os parâmetros da exportação. Mantidos margem de 12 mm, retrato,
  expansão de conteúdo, fluxo, parâmetros, retorno e tratamento de erro.
- [btnAbrirPdfRea.OnSelect] — link compartilhado aberto com Download → Launch em
  nova aba, com verificação de URL → abrir o endereço retornado pelo SharePoint.

Preservados: 37 controles, HeaderTitle_11, paleta verde do corpo, textos, dimensões
dos campos, espaçamentos, altura dinâmica e botão Abrir PDF visível/desabilitado.
O identificador longo do fluxo veio do código funcional do usuário; o nome exibido
CRIAR-PDF-IMAGEM não foi usado para renomear sua chamada.

## Checklist pós-colagem

- Substitua a tela atual pelo YAML acima; evite manter uma segunda tela com os
  mesmos nomes de controles.
- Use o mesmo app, com HeaderTitle, GalleryOcorrenciasREA, tbl_ReaOcorrencias e o
  fluxo já vinculado. São dependências existentes na edição enviada. As 16 colunas
  referenciadas foram conferidas no esquema local da lista.
- Abra o relatório a partir de uma ocorrência selecionada. Confira no Studio que
  cntDocumentoRelatorioRea.Width é 820 e que não há erros no Verificador do aplicativo.
- Clique em **Criar PDF** e então **Abrir PDF**. É necessário gerar um arquivo novo:
  o PDF já aberto não reflete mudanças no código.
- Confira legibilidade e espaço ocupado, e uma ocorrência com textos longos para
  verificar o conteúdo completo. A4 mantém a altura da folha; um registro curto pode
  deixar espaço em branco. O ajuste não garante preenchimento integral da página.

Validação realizada: estrutura YAML, comparação com a edição original, referências
de campos, alinhamentos e fórmulas de exportação. O Studio e o fluxo não foram
executados nesta revisão; a escala visual precisa ser confirmada no novo arquivo.

Referências: [opções da função PDF](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-pdf)
e [alinhamento em contêineres](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-horizontal-container).
'''
    (ROOT / "out" / "ENTREGA_RELATORIO_REA_FINAL.md").write_text(entrega, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    gerar()
