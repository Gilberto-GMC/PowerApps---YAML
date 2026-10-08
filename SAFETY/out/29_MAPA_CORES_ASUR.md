# Mapa de cores — telas de Forms para a paleta Asur

Base: as 8 telas em `SAFETY/out/2*_Screen*Forms.pa.yaml`.
2.586 linhas de cor no total. O mapa herdado do commit `aa0f7bc` resolve 1.056
automaticamente; branco e transparente (913) ficam como estão; vermelho (177) é
regra direta. **Sobram 38 pares (propriedade + cor) para decidir** — é esta tabela.

Tokens disponíveis (definidos em `02_App_Formulas_ptBR.txt`):

| token | cor | observação |
|---|---|---|
| `nfCorPrimaria` | `#00879A` teal Asur | em uso |
| `nfCorPrimariaEsc` | `#005864` | em uso |
| `nfCorTexto` | `#1E293B` slate-800 | **definido, nunca usado** |
| `nfCorTextoFraco` | `#64748B` slate-500 | em uso |
| `nfCorFundo` | `#FFFFFF` | definido, nunca usado |
| `nfCorFundoFraco` | `#F8FAFC` slate-50 | em uso |
| `nfCorBorda` | `#CBD5E1` slate-300 | em uso |
| `nfCorErro` | `#D93025` | em uso |
| `nfCorOk` / `nfCorAlerta` | `#118D5C` / `#C47F00` | definidos, nunca usados |

---

## A — Azul do tema antigo → primária (telas 24, 26, 27)

Estas três telas nunca foram convertidas. O `#3860B2` é a primária delas.

| propriedade | cor atual | onde | nº | proposta |
|---|---|---|---|---|
| `Color` | `RGBA(56, 96, 178, 1)` | Label (títulos de seção) | 47 | `nfCorPrimaria` |
| `SelectionFill` | `RGBA(56, 96, 178, 1)` | DropDown / ComboBox | 25 | `nfCorPrimaria` |
| `PressedFill` | `RGBA(0, 18, 107, 1)` | DropDown / ComboBox | 25 | `nfCorPrimariaEsc` |
| `ChevronBackground` | `RGBA(56, 96, 178, 1)` | DropDown / ComboBox | 17 | `nfCorPrimaria` |
| `HoverFill` | `RGBA(0,18,107,0.1)` | Button | 12 | `nfCorFundoFraco` |
| `Fill` | `RGBA(56, 96, 178, 1)` | Button | 8 | `nfCorPrimaria` |
| `ChevronBackground` | `RGBA(50, 86, 160, 1)` | DropDown | 8 | `nfCorPrimaria` |
| `BorderColor` | `RGBA(56, 96, 178, 1)` | GroupContainer | 4 | `nfCorPrimaria` |
| `IconBackground` | `RGBA(56, 96, 178, 1)` | DatePicker | 3 | `nfCorPrimaria` |
| `Color` | `RGBA(40, 134, 222, 1)` | Label | 1 | `nfCorPrimaria` |
| `Fill` | `RGBA(56, 96, 178, 0.12)` | Rectangle | 1 | `nfCorFundoFraco` |

Cada linha segue a regra que o `aa0f7bc` já usou para a mesma propriedade em
preto (`SelectionFill` → primária, `PressedFill` → escura, etc.).

**Exceção:** `Color | RGBA(0, 18, 107, 0.03)` num Icon da tela 27 (1x) — alfa 3%,
praticamente invisível. **Proposta: deixar como está.** Parece intencional
(ícone apagado de propósito) e qualquer token sólido o tornaria visível.

---

## B — Bordas azul-claras de campo

| propriedade | cor atual | onde | nº | proposta |
|---|---|---|---|---|
| `DisabledBorderColor` | `RGBA(136, 160, 209, 1)` | TextInput | 32 | `nfCorBorda` |
| `HoverBorderColor` | `RGBA(136, 160, 209, 1)` | TextInput | 32 | `nfCorPrimaria` |
| `DisabledBorderColor` | `RGBA(175, 191, 224, 1)` | DropDown | 14 | `nfCorBorda` |
| `BorderColor` | `RGBA(153, 160, 196, 1)` | Image (galeria) | 7 | `nfCorBorda` |
| `BorderColor` | `RGBA(175, 191, 224, 1)` | DatePicker, GroupContainer | 5 | `nfCorBorda` |
| `BorderColor` | `RGBA(186, 202, 226, 1)` | Label | 1 | `nfCorBorda` |

`HoverBorderColor` vai para a primária porque é feedback de interação — é o que o
`aa0f7bc` fez com `HoverBorderColor | preto`.

---

## C — Nas 8 telas, inclusive as já convertidas

O `aa0f7bc` deixou estas duas passar. Conferido: continuam literais no
`msapp/Src` também.

| propriedade | cor atual | onde | nº | proposta |
|---|---|---|---|---|
| `Fill` | `RGBA(39, 67, 125, 1)` | AddMedia ("Toque para adicionar imagem") | 8 | `nfCorPrimaria` |
| `BorderColor` | `RGBA(30, 30, 100, 1)` | ContainerHeader | 8 | `nfCorBorda` |

---

## D — Cinzas de texto e ícone

| propriedade | cor atual | onde | nº | proposta |
|---|---|---|---|---|
| `Color` | `RGBA(51, 51, 51, 1)` | Label | 8 | `nfCorTexto` ← primeiro uso do token |
| `BorderColor` | `RGBA(77, 77, 77, 1)` | Rectangle | 7 | `nfCorBorda` |
| `CheckboxBorderColor` | `RGBA(77, 77, 77, 1)` | CheckBox | 7 | `nfCorBorda` |
| `Color` | `RGBA(77, 77, 77, 1)` | Icon | 5 | `nfCorTextoFraco` |
| `Color` | `RGBA(0, 0, 0, 1)` | Icon | 1 | `nfCorTexto` |
| `HoverBorderColor` | `RGBA(51, 51, 51, 1)` | TextInput | 1 | `nfCorPrimaria` |

---

## E — Fundos quase brancos

| propriedade | cor atual | onde | nº | proposta |
|---|---|---|---|---|
| `BorderColor` | `RGBA(241, 244, 249, 1)` | Label, Image | 8 | `nfCorBorda` |
| `Fill` | `RGBA(241, 244, 249, 1)` | Label, Gallery | 3 | `nfCorFundoFraco` |
| `Fill` | `RGBA(241, 244, 249, 0.43)` | GroupContainer (spinner) | 2 | `nfCorFundoFraco` |
| `Fill` | `RGBA(219, 219, 219, 1)` | Rectangle | 1 | `nfCorFundoFraco` |
| `Fill` | `RGBA(247, 247, 247, 1)` | GroupContainer | 1 | `nfCorFundoFraco` |
| `Fill` | `RGBA(167, 182, 203, 0.09)` | Rectangle | 1 | `nfCorFundoFraco` |

Atenção: os dois com alfa (`0.43` e `0.09`) hoje são **translúcidos** — deixam
ver o que está atrás. `nfCorFundoFraco` é opaco. Se o efeito de véu importa
(o `0.43` é o fundo do spinner), a alternativa é
`ColorFade(nfCorFundoFraco, ...)` ou manter o literal.

---

## F — DatePicker preto

| propriedade | cor atual | onde | nº | proposta |
|---|---|---|---|---|
| `IconBackground` | `RGBA(0, 0, 0, 1)` | DatePicker | 4 | `nfCorPrimaria` |

Coerente com `ChevronBackground | preto → nfCorPrimaria`, que já está no mapa.

---

## G — Alerta

| propriedade | cor atual | onde | nº | proposta |
|---|---|---|---|---|
| `Color` | `RGBA(255, 191, 0, 1)` | Icon (tela 27) | 1 | `nfCorAlerta` ← primeiro uso |

---

## H — Cores dentro de expressão (`ColorFade`)

131 linhas que o levantamento anterior não contou, porque a cor está dentro de
uma chamada de função e não sozinha na propriedade.

| propriedade | expressão atual | nº | proposta |
|---|---|---|---|
| `ChevronHoverBackground` | `ColorFade(RGBA(0, 0, 0, 1), -20%)` | 81 | `ColorFade(nfCorPrimaria, -20%)` |
| `ChevronHoverBackground` | `ColorFade(RGBA(56, 96, 178, 1), -20%)` | 25 | `ColorFade(nfCorPrimaria, -20%)` |
| `HoverFill` | `ColorFade(RGBA(0, 0, 0, 1), -20%)` | 17 | `ColorFade(nfCorPrimaria, -20%)` |
| `HoverFill` | `ColorFade(RGBA(56, 96, 178, 1), -20%)` | 8 | `ColorFade(nfCorPrimaria, -20%)` |

Mantém a derivação em vez de fixar uma cor: se a primária mudar, o hover
acompanha.

---

## Dependência

Nada disso pode ser colado antes de o `App.Formulas` existir no app com os
tokens. Hoje os `nfCor*` são referenciados 1.553 vezes no `msapp/Src` e
**não estão definidos em lugar nenhum do export** — a definição está só no
arquivo `02_App_Formulas_ptBR.txt`, que nunca foi aplicado.
