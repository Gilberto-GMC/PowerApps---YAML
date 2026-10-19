# Novo Hub AirportNow — identidade visual ASUR

O entregável é o **`App_Formulas_Hub.txt`**: o `App.Formulas` inteiro, pronto
para substituir o que está no Studio de uma vez. Este arquivo aqui é só a
documentação da troca — não copie daqui.

**Ordem de colagem: `App_Formulas_Hub.txt` primeiro, as telas depois.** Uma tela
que referencia `thmPrimaria` antes do token existir falha inteira na colagem.

> Dialeto: o `.txt` sai em **pt-BR** (`;` entre argumentos, `;;` entre
> declarações), igual ao resto do seu `App.Formulas`. O `.pa.yaml` das telas
> continua em vírgula — isso está certo, o arquivo de origem da tela é sempre
> invariante.

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
  literal de cor no YAML. Os três botões do Login (`ButtonCanvas41`,
  `ButtonCanvas22_1`, `ButtonCanvas26`) já receberam `BasePaletteColor` ou
  `FontColor` explícito. Nas próximas telas, levantar esses controles **por tipo,
  não por busca de `RGBA(`**.

## Validação

```bash
node "Novo Hub AirportNow/validate_hub.js"
```

Lê os tokens do `App_Formulas_Hub.txt` e reprova tela que use token inexistente,
literal de cor fora dos preservados, `Button@0.0.45` sem cor fixada, referência a
controle inexistente, nome duplicado ou consulta não delegável. Roda um autoteste
antes: se alguma regra deixar de reprovar o caso construído, o validador aborta.
