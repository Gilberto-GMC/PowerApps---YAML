# Novo Hub AirportNow — tokens ASUR para o `App.Formulas`

**Cole este bloco no fim do `App.Formulas` que já existe, ANTES de colar qualquer
tela.** Uma tela que referencia `thmPrimaria` antes do token existir falha
inteira na colagem.

> Dialeto: **pt-BR**, igual ao resto do seu `App.Formulas` — `;` entre argumentos,
> `;;` entre declarações. O `.pa.yaml` das telas continua em vírgula: isso é
> normal, o arquivo de origem da tela é sempre invariante.

```powerfx
// ====================== identidade visual ASUR ======================
// Hex — para dentro do HTML dos HtmlViewer
hxPrimaria        = "#391694";;   // roxo institucional Motiva/ASUR
hxPrimariaEscura  = "#2A106E";;
hxPrimariaClara   = "#EDE9FB";;
hxBorda           = "#C9C5E6";;
hxFundo           = "#F8FAFC";;
hxSuperficie      = "#FFFFFF";;
hxTexto           = "#1E293B";;
hxTextoFraco      = "#64748B";;
hxAcao            = "#DD511A";;
hxVerde           = "#15803D";;
hxAmbar           = "#B45309";;
hxVermelho        = "#B91C1C";;

// Cores de controle nativo — derivadas dos hex acima, nunca redigitadas
thmPrimaria          = ColorValue(hxPrimaria);;
thmPrimariaEscura    = ColorValue(hxPrimariaEscura);;
thmPrimariaClara     = ColorValue(hxPrimariaClara);;
thmBorda             = ColorValue(hxBorda);;
thmFundo             = ColorValue(hxFundo);;
thmSuperficie        = ColorValue(hxSuperficie);;
thmTexto             = ColorValue(hxTexto);;
thmTextoFraco        = ColorValue(hxTextoFraco);;
thmAcao              = ColorValue(hxAcao);;
thmVerde             = ColorValue(hxVerde);;
thmAmbar             = ColorValue(hxAmbar);;
thmVermelho          = ColorValue(hxVermelho);;
thmTextoInverso      = RGBA(255; 255; 255; 1);;
thmTransparente      = RGBA(0; 0; 0; 0);;

// Estado desabilitado — estrutura, não marca. Igual ao original.
thmDesabilitado      = RGBA(166; 166; 166; 1);;
thmDesabilitadoFundo = RGBA(166; 166; 166; 0.5);;

// Tipografia — Sora é a fonte da marca, mas não existe no Power Apps.
// Segoe UI é a substituta e está em todos os clientes.
thmFonte             = Font.'Segoe UI';;
```

## De → para aplicado na tela Login

| Literal original | Token | Onde |
| --- | --- | --- |
| `RGBA(96, 70, 237, 1)` | `thmPrimaria` | spinner, bordas, rótulos do painel de senha, ícone de aviso |
| `RGBA(40, 134, 222, 1)` | `thmPrimaria` | ícones Person/Eye, rótulos ocultos |
| `RGBA(109, 49, 162, 1)` | `thmPrimaria` | borda do `Container43` |
| `RGBA(0, 18, 107, 1)` | `thmPrimariaEscura` | bordas, ícones Salvar/Cancelar |
| `RGBA(9, 33, 98, 1)` | `thmPrimariaEscura` | rótulo de versão |
| `RGBA(247, 247, 247, 1)` | `thmFundo` | fundo da tela, faixa do título |
| `RGBA(255, 255, 255, 1)` | `thmSuperficie` / `thmTextoInverso` | fundos / texto sobre botão |
| `RGBA(53, 61, 63, 1)` | `thmTexto` | texto digitado nos campos |
| `RGBA(197, 197, 197, 1)` | `thmBorda` | linha sob os campos |
| `RGBA(99, 99, 99, 1)`, `RGBA(124, 125, 125, 1)` | `thmTextoFraco` | textos de apoio |
| `RGBA(255, 0, 0, 1)`, `Color.Red` | `thmVermelho` | alertas e validação |
| `RGBA(166, 166, 166, …)` | `thmDesabilitado*` | preservado — estado, não marca |
| `RGBA(255, 255, 255, 0.8)`, `RGBA(0, 0, 0, 0)` | preservados | transparência estrutural |
| `color: orange`, `#474646` (HTML) | `hxAmbar`, `hxTextoFraco` | aviso de versão desatualizada |

## Cor que não sai pelo YAML da tela

- `Progress2.ProgressColor = 'Progress.ProgressColor'.Brand` — o `Progress@1.1.34`
  só aceita o enum; a cor vem do **tema do app no Studio**. Para a barra de
  carregamento ficar roxo ASUR, trocar a cor Brand no tema. Não há propriedade
  de cor para colar.
- `Button@0.0.45` **sem `BasePaletteColor` também cai no tema**, mesmo sem nenhum
  literal de cor no YAML. Os três botões da tela (`ButtonCanvas41`,
  `ButtonCanvas22_1`, `ButtonCanvas26`) já receberam `BasePaletteColor` ou
  `FontColor` explícito. Nas próximas telas, levantar esses controles **por tipo,
  não por busca de `RGBA(`**.
