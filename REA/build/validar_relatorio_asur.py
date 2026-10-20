"""Valida a tela REA/ASUR antes de colar no Studio."""

from collections import Counter
from pathlib import Path
import json
import re
import sys
from copy import deepcopy
from powerapps_yaml import parse_studio, controls


ROOT = Path(__file__).resolve().parents[1]
TELA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "frmRelatoriosOcorrencias_FINAL.pa.yaml"
TELA_FONTE = ROOT / "msapp" / "Src" / "frmRelatoriosOcorrencias.pa.yaml"
FONTES = ROOT / "msapp" / "References" / "DataSources.json"
ORIGEM = ROOT / "msapp" / "Src" / "ScreenOcorrencias.pa.yaml"

MODELO = ROOT / "modelos" / "frmRelatoriosOcorrencias_usuario.pa.yaml"
texto = TELA.read_text(encoding="utf-8")
modelo = MODELO.read_text(encoding="utf-8")
erros = []
try:
    arvore, _ = parse_studio(texto)
    arvore_modelo, _ = parse_studio(modelo)
    mapa = controls(arvore)
    mapa_modelo = controls(arvore_modelo)
except (ValueError, KeyError, IndexError) as exc:
    sys.exit(f"ERRO: estrutura YAML: {exc}")

# A versão do usuário é a base: qualquer mudança fora destes pontos é regressão.
permitidas = {
    "cntDocumentoRelatorioRea": {"AlignInContainer", "LayoutMinWidth", "LayoutMaxWidth"},
    "cntAcoesRelatorioRea": {"AlignInContainer", "LayoutMinWidth", "LayoutMaxWidth"},
    "btnCriarPdfRea": {"OnSelect"},
    "btnAbrirPdfRea": {"OnSelect"},
}
comparacoes = []
for original in (arvore, arvore_modelo):
    copia = deepcopy(original)
    for nome, (controle, _) in controls(copia).items():
        for prop in permitidas.get(nome, set()):
            controle["Properties"].pop(prop, None)
    comparacoes.append(copia)
if comparacoes[0] != comparacoes[1]:
    erros.append("A entrega alterou propriedades, controles ou hierarquia fora dos ajustes autorizados.")
if len(sys.argv) == 1 and (ROOT / "out" / "frmRelatoriosOcorrencias_ASUR.pa.yaml").read_text(encoding="utf-8") != texto:
    erros.append("O alias ASUR diverge da versão FINAL.")

if len(sys.argv) == 1 and TELA_FONTE.read_text(encoding="utf-8") != texto:
    erros.append("Fonte do app e YAML de entrega do relatório estão diferentes.")

if not texto.startswith("Screens:\n  frmRelatoriosOcorrencias:\n    Properties:\n"):
    erros.append("Raiz YAML inválida para a tela frmRelatoriosOcorrencias.")

nomes = re.findall(r"(?m)^\s+- ([A-Za-z][A-Za-z0-9_]*):\s*$", texto)
for nome, total in Counter(nomes).items():
    if total > 1:
        erros.append(f"Controle duplicado: {nome} ({total} vezes).")

if "GalleryRelatorio" in texto or "ThisItem." in texto:
    erros.append("Relatório de um único registro não deve usar galeria/ThisItem.")

if "var_dadosRelatorio" in texto:
    erros.append("Dependência de var_dadosRelatorio: tela colada isoladamente não reconhece a variável.")

formulas = list(arvore["Screens"]["frmRelatoriosOcorrencias"]["Properties"].values())
for controle, _ in mapa.values():
    formulas.extend(controle.get("Properties", {}).values())
formulas_texto = "\n".join(formulas)
variaveis = set(re.findall(r"\bvar[A-Za-z_][A-Za-z0-9_]*\b", formulas_texto))
variaveis_definidas = set(re.findall(r"\bSet\(\s*(var[A-Za-z_][A-Za-z0-9_]*)\s*,", formulas_texto))
variaveis_definidas.update(re.findall(r"\b(var[A-Za-z_][A-Za-z0-9_]*):\s*", formulas_texto))
modulo = (ROOT / "msapp" / "Src" / "ScreenREA.pa.yaml").read_text(encoding="utf-8")
if re.search(r"Set\(\s*var_tituloModulo\s*,", modulo):
    variaveis_definidas.add("var_tituloModulo")
for variavel in sorted(variaveis - variaveis_definidas):
    erros.append(f"Variável sem definição confirmada no app: {variavel}.")
if not (ROOT / "msapp" / "Src" / "Components" / "HeaderTitle.pa.yaml").exists():
    erros.append("O componente HeaderTitle do usuário não existe no export.")

if "ID = GalleryOcorrenciasREA.Selected.ID" not in texto:
    erros.append("O registro deve ser consultado pelo ID da seleção existente na tela de origem.")

origem = ORIGEM.read_text(encoding="utf-8")
if "- GalleryOcorrenciasREA:" not in origem or "tbl_ReaOcorrencias" not in origem:
    erros.append("A galeria de origem ou a fonte SharePoint não foi encontrada no app exportado.")
if "var_dadosRelatorio" in origem:
    erros.append("Navegação ainda passa a variável de contexto removida do relatório.")

fluxos = re.findall(r"'([^']+)'\.Run\s*\(", texto)
fluxos_modelo = re.findall(r"'([^']+)'\.Run\s*\(", modelo)
if len(fluxos) != 1 or fluxos != fluxos_modelo:
    erros.append("O identificador do fluxo deve ser o da versão que funcionou no Studio.")

if "%DATACARD_" in texto:
    erros.append("Placeholder interno do Studio no YAML.")

if not all(nome in nomes for nome in ("cntDocumentoRelatorioRea", "btnCriarPdfRea", "btnAbrirPdfRea")):
    erros.append("Contêiner do relatório ou botões de PDF ausentes.")

for cor_antiga in ("RGBA(31, 67, 138", "RGBA(201, 32, 80"):
    if cor_antiga in texto:
        erros.append(f"Cor antiga fora do design system Due Diligence: {cor_antiga}.")
if "RGBA(0, 135, 154, 1)" not in texto or "RGBA(0, 88, 100, 1)" not in texto:
    erros.append("Paleta principal verde do Due Diligence não aplicada.")
if "Font.'Segoe UI'" not in texto:
    erros.append("Tipografia do Due Diligence não aplicada.")

fonte = next(
    item for item in json.loads(FONTES.read_text(encoding="utf-8"))["DataSources"]
    if item["Name"] == "tbl_ReaOcorrencias"
)
metadados = json.loads(next(iter(fonte["DataEntityMetadataJson"].values())))
campos = set(metadados["schema"]["items"]["properties"])
referencias = set(re.findall(r"varRelatorioReaRegistro\.([A-Za-z][A-Za-z0-9_]*)", texto))
for campo in sorted(referencias - campos):
    erros.append(f"Campo ausente da lista tbl_ReaOcorrencias: {campo}.")


controles = {nome: node["Properties"] for nome, (node, _) in mapa.items()}

if controles.get("cntDocumentoRelatorioRea", {}).get("Width") != "=820":
    erros.append("Largura do documento deve ser 820 para manter a grade validada.")

for nome in ("cntDocumentoRelatorioRea", "cntAcoesRelatorioRea"):
    p = controles.get(nome, {})
    if p.get("AlignInContainer") != "=AlignInContainer.Center":
        erros.append(f"{nome}: centralizar explicitamente para evitar esticamento no auto layout.")
    if p.get("LayoutMinWidth") != "=820" or p.get("LayoutMaxWidth") != "=820":
        erros.append(f"{nome}: limites de largura devem manter a grade de 820 px.")

criar_pdf = controles.get("btnCriarPdfRea", {}).get("OnSelect", "")
criar_modelo = mapa_modelo["btnCriarPdfRea"][0]["Properties"]["OnSelect"]
criar_sem_opcoes = re.sub(r'\s*Size:\s*"A4",', '', criar_pdf)
criar_sem_opcoes = re.sub(r'\s*DPI:\s*96,', '', criar_sem_opcoes)
if re.sub(r"\s+", "", criar_sem_opcoes) != re.sub(r"\s+", "", criar_modelo):
    erros.append("Criar PDF mudou a lógica ou o contrato do fluxo além das opções A4/DPI.")
for trecho in ('PDF(cntDocumentoRelatorioRea,', 'Size: "A4"', 'DPI: 96',
               'Orientation: "Portrait"', 'Margin: "12mm"', 'ExpandContainers: true',
               'IfError(', 'contentBytes: arquivoPdf'):
    if re.sub(r"\s+", "", trecho) not in re.sub(r"\s+", "", criar_pdf):
        erros.append(f"Geração do PDF sem configuração obrigatória: {trecho}.")
abrir_pdf = controles.get("btnAbrirPdfRea", {}).get("OnSelect", "")
if "Download(" in abrir_pdf or "Launch(TrimEnds(varUrlPdfRea), {}, LaunchTarget.New)" not in abrir_pdf:
    erros.append("Abrir PDF deve navegar ao link SharePoint usando Launch em nova aba.")

for titulo, valor in (
    ("lblStatusTituloRea", "lblStatusValorRea"),
    ("lblAeroportoTituloRea", "lblAeroportoValorRea"),
    ("lblTipoTituloRea", "lblTipoValorRea"),
    ("lblCriadoTituloRea", "lblCriadoValorRea"),
    ("lblResponsavelTituloRea", "lblResponsavelValorRea"),
    ("lblPeriodoTituloRea", "lblPeriodoValorRea"),
    ("lblVeiculoTituloRea", "lblVeiculoValorRea"),
):
    for eixo in ("X", "Width"):
        if controles.get(titulo, {}).get(eixo) != controles.get(valor, {}).get(eixo):
            erros.append(f"Desalinhamento {titulo}/{valor} no eixo {eixo}.")

for linha_campos in (
    ("lblStatusTituloRea", "lblAeroportoTituloRea"),
    ("lblTipoTituloRea", "lblCriadoTituloRea", "lblResponsavelTituloRea"),
    ("lblPeriodoTituloRea", "lblVeiculoTituloRea"),
):
    fim_anterior = None
    for nome in linha_campos:
        p = controles.get(nome, {})
        try:
            x, largura = (int(p[eixo][1:]) for eixo in ("X", "Width"))
        except (KeyError, ValueError, TypeError):
            erros.append(f"Geometria estática não validável: {nome}.")
            continue
        if x < 32 or x + largura > 788:
            erros.append(f"Margem lateral fora da grade de 32 px: {nome}.")
        if fim_anterior is not None and x - fim_anterior < 24:
            erros.append(f"Espaçamento horizontal inferior a 24 px antes de {nome}.")
        fim_anterior = x + largura

    valores_y = {controles.get(nome, {}).get("Y") for nome in linha_campos}
    if len(valores_y) != 1:
        erros.append(f"Títulos da mesma linha com Y diferentes: {', '.join(linha_campos)}.")

for nome in ("lblDescricaoTituloRea", "lblDescricaoValorRea",
             "lblAcaoTituloRea", "lblAcaoValorRea",
             "lblSolucaoTituloRea", "lblSolucaoValorRea"):
    p = controles.get(nome, {})
    if p.get("X") != "=32" or p.get("Width") != "=Parent.Width - 64":
        erros.append(f"Bloco de conteúdo fora da grade: {nome}.")

for titulo, valor in (("lblDescricaoTituloRea", "lblDescricaoValorRea"),
                      ("lblAcaoTituloRea", "lblAcaoValorRea"),
                      ("lblSolucaoTituloRea", "lblSolucaoValorRea")):
    if titulo != "lblDescricaoTituloRea" and controles.get(valor, {}).get("Y") != f"={titulo}.Y + 48":
        erros.append(f"Espaçamento vertical título/corpo incorreto: {titulo}.")

if controles.get("lblAcaoTituloRea", {}).get("Y", "").find("+ 24") < 0:
    erros.append("Falta separação de 24 px antes da seção Ação.")
if controles.get("lblSolucaoTituloRea", {}).get("Y", "").find("+ 24") < 0:
    erros.append("Falta separação de 24 px antes da seção Solução.")

if controles.get("btnCriarPdfRea", {}).get("X") != "=Parent.Width - 352" or \
   controles.get("btnAbrirPdfRea", {}).get("X") != "=Parent.Width - 176":
    erros.append("Botões de PDF fora da grade de 16 px do rodapé.")


def propriedades_por_tipo(caminhos):
    encontrados = {}
    for caminho in caminhos:
        tipo = None
        recuo_propriedade = None
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            controle = re.match(r"^( +)Control: ([^\s]+)", linha)
            if controle:
                tipo = controle.group(2)
                recuo_propriedade = len(controle.group(1)) + 2
                encontrados.setdefault(tipo, set())
                continue
            if tipo:
                propriedade = re.match(r"^( +)([A-Za-z][A-Za-z0-9_]*):", linha)
                if propriedade and len(propriedade.group(1)) == recuo_propriedade:
                    encontrados[tipo].add(propriedade.group(2))
    return encontrados


# O arquivo sendo validado não pode comprovar suas próprias propriedades novas.
caminhos_esquema = [p for p in (ROOT / "msapp" / "Src").rglob("*.pa.yaml") if p != TELA_FONTE]
esquema_controles = propriedades_por_tipo(caminhos_esquema + [MODELO])
propriedades_tela = propriedades_por_tipo([TELA])
for tipo, propriedades in propriedades_tela.items():
    for propriedade in sorted(propriedades - esquema_controles.get(tipo, set())):
        erros.append(f"Propriedade não comprovada no export: {tipo}.{propriedade}.")

for formula in formulas:
    if not isinstance(formula, str) or not formula.startswith("="):
        erros.append(f"Propriedade sem fórmula válida: {formula!r}")
        continue
    # Confere delimitadores, ignorando strings e identificadores entre aspas.
    sem_strings = re.sub(r'"(?:[^"\n]|"")*"|\'(?:[^\'\n]|\'\')*\'', '', formula)
    pilha = []
    pares = {')': '(', '}': '{', ']': '['}
    for char in sem_strings:
        if char in "({[":
            pilha.append(char)
        elif char in pares:
            if not pilha or pilha.pop() != pares[char]:
                erros.append("Delimitadores Power Fx não balanceados.")
                break
    if pilha:
        erros.append("Delimitadores Power Fx não fechados.")

if erros:
    for erro in erros:
        print("ERRO:", erro)
    sys.exit(1)

print(f"Validação estática do relatório: {len(nomes)} controles, {len(referencias)} campos verificados.")

print("Edição do usuário preservada; 8 propriedades ajustadas em 4 controles.")
print("A importação, o fluxo e a escala final ainda exigem novo PDF no Studio.")
