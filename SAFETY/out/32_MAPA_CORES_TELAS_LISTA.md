# Mapa de cores — 13 telas de lista e apoio (`SAFETY/out/31_*`)

Estas telas nunca passaram pelo script de recoloração. Passaram só pelo commit
`aa0f7bc`, que deixou os cabeçalhos pretos.

| | |
|---|---|
| já cobertos pelo mapa herdado do `aa0f7bc` | 80 |
| branco e transparente, ficam como estão | 338 |
| **fora do mapa — esta tabela** | **328, em 43 pares** |

Tokens: `nfCorPrimaria` `#0E7C8C` · `nfCorPrimariaEsc` `#0A5A66` ·
`nfCorPrimariaClara` `#E4F2F4` · `nfCorTexto` `#1E293B` · `nfCorTextoFraco`
`#64748B` · `nfCorFundoFraco` `#F8FAFC` · `nfCorBorda` `#B9D9DE` · `nfCorErro`
`#B91C1C` · `nfCorAlerta` `#B45309` · `nfCorAcao` `#DD511A` · `nfCorOk`
`#0E7C8C` *(igual à primária, por escolha sua)*

---

## A — Fundo dos campos de filtro — 63 linhas

| nº | propriedade | cor | onde | proposta |
|---|---|---|---|---|
| 46 | `Fill` | `RGBA(250, 250, 250, 1)` | DropDown, DatePicker | `nfCorFundoFraco` |
| 8 | `Fill` | `RGBA(240, 240, 240, 1)` | Icon | `nfCorFundoFraco` |
| 6 | `HoverFill` | `RGBA(247, 247, 247, 1)` | DropDown | `nfCorFundoFraco` |
| 2 | `Fill` | `RGBA(247, 247, 247, 1)` | ComboBox | `nfCorFundoFraco` |
| 1 | `DropTargetBackgroundColor` | `RGBA(245, 245, 245, 1)` | Attachments | `nfCorFundoFraco` |

Cinco cinzas quase idênticos virando um token só.

## B — Chevron e seleção dos filtros — 84 linhas

Atenção: nestas telas o chevron é **plano** — `ChevronBackground` é
transparente e o `ChevronHoverFill` **já é** `nfCorPrimaria`. Então o repouso
fica escuro e o hover teal, que é o comportamento que já existe.

| nº | propriedade | cor | onde | proposta |
|---|---|---|---|---|
| 33 | `ChevronFill` | `RGBA(0, 0, 0, 1)` | DropDown | `nfCorTexto` |
| 27 | `SelectionFill` | `RGBA(186, 202, 226, 1)` | DropDown | `nfCorPrimariaClara` |
| 6 | `ChevronHoverFill` | `RGBA(15, 84, 140, 1)` | DropDown | `nfCorPrimaria` |
| 6 | `SelectionColor` | `RGBA(0, 0, 0, 1)` | DropDown | `nfCorTexto` |
| 6 | `PressedColor` | `RGBA(0, 0, 0, 1)` | DropDown | `nfCorTexto` |
| 6 | `DisabledColor` | `RGBA(0, 0, 0, 1)` | DropDown | `nfCorTextoFraco` |
| 6 | `BorderColor` | `RGBA(215, 223, 240, 1)` | DropDown | `nfCorBorda` |

## C — DatePicker — 36 linhas

| nº | propriedade | cor | onde | proposta |
|---|---|---|---|---|
| 18 | `IconBackground` | `RGBA(219, 219, 219, 1)` | DatePicker | `nfCorFundoFraco` |
| 18 | `IconFill` | `RGBA(0, 0, 0, 1)` | DatePicker | `nfCorTexto` |

Escolhi o conservador: mantém o botãozinho de calendário claro, só troca o
cinza avulso pelo token. **Alternativa**, se quiser destacar: `IconBackground`
→ `nfCorPrimariaClara` e `IconFill` → `nfCorPrimaria`, que deixa o calendário
com um toque de teal.

## D — Cabeçalho e separadores — 20 linhas

| nº | propriedade | cor | onde | proposta |
|---|---|---|---|---|
| 13 | `BorderColor` | `RGBA(30, 30, 100, 1)` | GroupContainer (cabeçalho) | `nfCorBorda` |
| 4 | `Fill` | `RGBA(214, 221, 224, 1)` | Rectangle (separador) | `nfCorBorda` |
| 2 | `Fill` | `RGBA(9, 33, 98, 1)` | GroupContainer | `nfCorPrimaria` |
| 1 | `Fill` | `RGBA(40, 134, 222, 1)` | Rectangle (separador) | `nfCorPrimaria` |

Os **71 `Fill: =RGBA(0, 0, 0, 1)` dos cabeçalhos pretos** não entram aqui — já
estão no mapa herdado (`Fill | preto → nfCorPrimaria`) e são aplicados
automaticamente.

## E — Ícones de ação da barra de filtros — 34 linhas

| nº | propriedade | cor | onde | proposta |
|---|---|---|---|---|
| 12 | `DisabledBorderColor` | `RGBA(56, 56, 56, 1)` | Icon, HtmlViewer | `nfCorBorda` |
| 9 | `DisabledFill` | `RGBA(0, 18, 107, 0.1)` | Icon | `nfCorFundoFraco` |
| 9 | `HoverColor` | `RGBA(71, 158, 245, 1)` | Icon | `nfCorPrimaria` |
| 9 | `HoverFill` | `RGBA(71, 158, 245, 0.2)` | Icon | `nfCorPrimariaClara` |
| 3 | `DisabledColor` | `RGBA(119, 119, 119, 1)` | Icon | `nfCorTextoFraco` |
| 1 | `Color` | `RGBA(0, 18, 107, 1)` | Icon | `nfCorPrimaria` |

## F — O botão `Button11_29` (uma tela, seis propriedades) — 52 linhas

| nº | propriedade | cor | proposta |
|---|---|---|---|
| 12 | `Color` | `RGBA(0, 0, 0, 1)` | `nfCorTexto` |
| 8 | `BorderColor` | `RGBA(9, 33, 98, 0.05)` | `nfCorBorda` |
| 8 | `HoverBorderColor` | `RGBA(9, 33, 98, 0.05)` | `nfCorBorda` |
| 8 | `PressedBorderColor` | `RGBA(9, 33, 98, 0.05)` | `nfCorBorda` |
| 8 | `HoverColor` | `RGBA(0, 0, 0, 1)` | `nfCorTexto` |
| 8 | `PressedFill` | `RGBA(9, 33, 98, 0.5)` | `nfCorPrimariaEsc` |

## G — Textos — 16 linhas

| nº | propriedade | cor | onde | proposta |
|---|---|---|---|---|
| 4 | `Color` | `RGBA(50, 49, 48, 1)` | Label (título da galeria) | `nfCorTexto` |
| 3 | `FontColor` | `RGBA(135, 135, 135, 1)` | Button (ícone da linha) | `nfCorTextoFraco` |
| 3 | `FontColor` | `RGBA(12, 59, 94, 1)` | Button (badge IATA) | `nfCorPrimaria` |
| 3 | `FontColor` | `RGBA(0, 0, 0, 1)` | Button | `nfCorTexto` |
| 1 | `FontColor` | `RGBA(168, 168, 168, 1)` | Text | `nfCorTextoFraco` |
| 1 | `FontColor` | `RGBA(39, 113, 194, 1)` | Button | `nfCorPrimaria` |
| 1 | `Color` | `RGBA(39, 113, 194, 1)` | Button | `nfCorPrimaria` |
| 1 | `Color` | `RGBA(79, 79, 79, 1)` | Label | `nfCorTextoFraco` |

## H — Estados — 5 linhas

| nº | propriedade | cor | onde | proposta |
|---|---|---|---|---|
| 2 | `Color` | `RGBA(255, 0, 0, 1)` | Icon | `nfCorErro` |
| 1 | `Color` | `RGBA(168, 0, 0, 1)` | Label de erro do formulário | `nfCorErro` |
| 2 | `Color` | `RGBA(45, 128, 40, 1)` | Label (status "Finalizado") | **manter literal** |

O verde do status fica como está **de propósito**. O `nfCorOk` hoje é o mesmo
teal da primária, então mandar o status para lá apagaria a distinção entre
"Finalizado" e o resto da tela. Se quiser o status tokenizado, o caminho é
devolver um verde ao `nfCorOk` e apontar o botão Salvar para `nfCorPrimaria`.

## I — Já na paleta, não mexo — 2 linhas

| nº | propriedade | cor | motivo |
|---|---|---|---|
| 1 | `BasePaletteColor` | `RGBA(189, 178, 176, 1)` | `#BDB2B0` é o `hxBotaoBarra` do `App_Formulas_APAC.txt` |
| 1 | `Fill` | `RGBA(0, 0, 0, 0.05)` | sombra sutil de HtmlViewer, não é cor de marca |
