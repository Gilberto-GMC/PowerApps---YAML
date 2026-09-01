# App.Formulas — Tokens de tema PLEM/PRAI

A tela única `REA/ScreenAcionamentosPlemPraiUnica.pa.yaml` referencia os tokens
`thm*` abaixo. **Cole o bloco no `App.Formulas` do app ANTES de colar a tela**
(App → Fórmulas, no painel do Studio). Sem isso a tela acusa nome desconhecido.

Bloco no **padrão pt-BR do Studio** (argumentos com `;`, terminador de
definição com `;;`, decimais com vírgula, comentários `//` e `/* */`):

```powerfx
// ===== Tokens de tema PLEM/PRAI =====
// Azuis consolidados (a tela antiga usava 5+ azuis; ficaram 4 papéis)
thmPrimary = RGBA(15; 108; 189; 1);;
thmPrimaryLight = RGBA(40; 134; 222; 1);;
thmPrimarySoft = RGBA(180; 214; 250; 1);;
thmPrimaryDark = RGBA(9; 33; 98; 1);;
thmPrimaryFade05 = RGBA(0; 18; 107; 0,05);;
thmPrimaryFade10 = RGBA(0; 18; 107; 0,1);;
thmPrimaryFade20 = RGBA(0; 18; 107; 0,2);;
// Texto
thmText = RGBA(0; 0; 0; 1);;
thmTextStrong = RGBA(61; 61; 61; 1);;
thmTextSoft = RGBA(0; 0; 0; 0,7);;
thmTextMuted = RGBA(0; 0; 0; 0,5);;
thmTextFaint = RGBA(0; 0; 0; 0,3);;
thmShade10 = RGBA(0; 0; 0; 0,1);;
// Superfícies
thmSurface = RGBA(255; 255; 255; 1);;
thmSurfaceAlt = RGBA(249; 249; 249; 1);;
thmSurfaceSoft = RGBA(247; 247; 247; 1);;
thmBackground = RGBA(242; 242; 242; 1);;
thmBackgroundAlt = RGBA(240; 240; 240; 1);;
thmBorder = RGBA(167; 182; 203; 1);;
thmBorderSoft = RGBA(237; 237; 237; 1);;
// Semânticas
thmDanger = RGBA(255; 0; 0; 1);;
thmWarning = RGBA(255; 191; 0; 1);;
thmSuccess = RGBA(52; 152; 47; 1);;
// Status de prioridade/etapas do fluxograma (cores originais preservadas)
thmStatusYellow = RGBA(255; 255; 0; 1);;
thmStatusOrange = RGBA(247; 116; 38; 1);;
thmStatusRed = RGBA(249; 83; 109; 1);;
thmStatusBlue = RGBA(56; 96; 178; 1);;
thmTransparent = RGBA(0; 0; 0; 0)
```

> Atenção: a ÚLTIMA definição não leva `;;`. Se você já tiver outras fórmulas
> no `App.Formulas`, cole este bloco antes delas e acrescente `;;` ao
> `thmTransparent`.
>
> **Importante — só a barra de fórmulas é pt-BR.** O arquivo
> `ScreenAcionamentosPlemPraiUnica.pa.yaml` fica no formato invariante
> (argumentos com `,`, encadeamento com `;`, decimais com ponto) — é assim que
> o Studio grava e lê o Source Code YAML. Não converta o YAML para `;`.

## Variáveis

Nenhuma variável global nova. A tela única mantém as flags de contexto
`var_visible*` originais (o trilho de navegação zera todas e liga só a da
seção destino) e as variáveis de dados (`var_dadosAcionamento`,
`var_dadosEmergencia`, `var_acao`, `var_tipoPrai` etc.) com os mesmos nomes.

## Ordem de colagem no Studio

1. Este bloco no `App.Formulas`.
2. **Backup + exclusão da tela antiga `ScreenAcionamentosPlemPrai`** — a nova
   tela usa o MESMO nome de tela e os MESMOS nomes de controles; com a antiga
   presente, a colagem acusa `PA2110` (nome duplicado). Antes de excluir,
   confirme que `REA/ScreenAcionamentosNewPlemPrai.pa.yaml` (export atual) está
   guardado — ele é o backup e a fonte de extração do gerador.
3. Colar `ScreenAcionamentosPlemPraiUnica.pa.yaml` via exibição de código.
   Como o nome da tela é o mesmo, `Navigate` de outras telas continua válido.
4. Testar com limite de delegação = 1 (Configurações → Próximos recursos).

> O gerador valida cada propriedade e cada nome de ícone contra o que o export
> original do Studio já usa naquele mesmo tipo de controle, então não há mais
> palpites de esquema na tela (ver `LICOES_APRENDIDAS_POWERAPPS_YAML.md`,
> PA2108 — `Tooltip` em `Button@0.0.45`).
