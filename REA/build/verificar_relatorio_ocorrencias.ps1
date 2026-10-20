param(
    [string]$Sarif = (Join-Path $PSScriptRoot '..\msapp\AppCheckerResult.sarif'),
    [string]$Tela = (Join-Path $PSScriptRoot '..\msapp\Src\frmRelatoriosOcorrencias.pa.yaml')
)

$ErrorActionPreference = 'Stop'
$problemas = [System.Collections.Generic.List[string]]::new()

if (-not (Test-Path -LiteralPath $Tela)) { throw "Tela não encontrada: $Tela" }
if (-not (Test-Path -LiteralPath $Sarif)) { throw "Verificador do Studio não encontrado: $Sarif" }

$yaml = Get-Content -LiteralPath $Tela -Raw
$dados = Get-Content -LiteralPath $Sarif -Raw | ConvertFrom-Json
$codigos = @('app-ErrUnknownNamespaceFunction', 'app-ErrIncompatibleCtxtVariableTypes', 'app-ErrInvalidDot')

foreach ($run in $dados.runs) {
    foreach ($resultado in $run.results) {
        if ($resultado.ruleId -notin $codigos) { continue }
        $locais = @($resultado.locations | ForEach-Object { $_.physicalLocation.address.fullyQualifiedName })
        if (-not (@($locais | Where-Object { $_ -like 'frmRelatoriosOcorrencias.*' }).Count)) { continue }
        $argumentos = @($resultado.message.arguments) -join ', '
        $problemas.Add("$($resultado.ruleId): $($locais -join ', ') $argumentos")
    }
}

if ($yaml -match 'UpdateContext\(\{var_loadSave:\s*true\}\)') {
    $problemas.Add('Criar PDF: var_loadSave é ativada sem conferir o retorno do fluxo e a URL.')
}

if ($yaml -match '(?s)- GalleryRelatorio:.*?TemplateSize:\s*=150.*?- Container59_3:.*?Height:\s*=Parent\.Height') {
    $problemas.Add('GalleryRelatorio: o contêiner do item usa a altura da galeria, maior que o template.')
}

if ($problemas.Count -gt 0) {
    $problemas | ForEach-Object { Write-Output "ERRO: $_" }
    exit 1
}

Write-Output 'Relatório de ocorrências REA: sem erros de fórmula conhecidos no SARIF.'
