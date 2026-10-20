# REA — base atual de trabalho

O pacote `AirportNow-RespostaàEmergência–2025_20261019210154.zip`, exportado
em **19/10/2026 às 18:01:54 (Brasília)**, é a referência atual do aplicativo.

## Arquivos de referência

- `msapp/Src/`: 20 telas, 3 componentes, App e estado do editor, extraídos do
  novo pacote sem alterações nas fórmulas.
- `msapp/`: aplicativo completo, incluindo controles, recursos, referências
  de dados e resultado do Verificador do aplicativo exportado pelo Studio.
- `extracted/`: conteúdo completo do pacote, incluindo o `.msapp` e 6 fluxos.
- `base_atual.json`: origem, SHA-256, inventário de telas, componentes e fluxos.
- `out/`: entregas preparadas. Os arquivos de APH já existentes nessa pasta
  pertencem à entrega anterior e são mantidos por causa da auditoria.

## Histórico preservado

O export anterior permanece no histórico do Git e no pacote
`AirportNow-RespostaàEmergência_20260918135434.zip`. A cópia local em
`historico/antes_do_export_20261019210154.local/` não é publicada porque
duplica arquivos já preservados. Os artefatos de APH em `out/` continuam
versionados para manter válidas as referências de `AUDITORIA_APH.md`.

Os auxiliares em `build/`, `modelos/` e na raiz foram mantidos. Alguns geradores
usam modelos anteriores: antes de executá-los, conferir suas entradas e saídas
contra esta base. Em particular, o relatório de referência agora é
`msapp/Src/frmRelatoriosOcorrencias.pa.yaml`; as antigas entregas ASUR/FINAL
estão apenas na cópia local ignorada pelo Git. Não reaplicar ajustes antigos
automaticamente.

## Telas diferentes da base local anterior

- ScreenAPH
- ScreenCheckListREA
- ScreenCheckListVeiculoCCI
- ScreenContatos
- ScreenOcorrencias
- ScreenREA
- ScreenTesteContatos
- frmRelatoriosOcorrencias

A importação conferiu CRC dos dois arquivos ZIP (pacote e `.msapp` interno),
inventário e igualdade byte a byte dos arquivos extraídos. Esta conferência
verifica a cópia do export; não executa o app nem certifica suas fórmulas.
