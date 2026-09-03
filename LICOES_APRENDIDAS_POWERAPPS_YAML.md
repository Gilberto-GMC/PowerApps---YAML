# Lições aprendidas — Power Apps Source Code YAML

Este documento é a memória global de erros e padrões para todos os projetos
Power Apps deste workspace. Cada nova ocorrência deve acrescentar causa,
correção e uma validação preventiva para impedir regressão nas próximas telas,
independentemente do projeto ou módulo.

## Padrão para registrar novos aprendizados

Cada novo erro deve informar:

- Data da ocorrência.
- Projeto e tela afetados.
- Código e mensagem completa do Power Apps Studio.
- Causa confirmada, sem hipóteses apresentadas como fato.
- Correção aplicada.
- Validação automatizada adicionada.
- Impacto global: quais outros projetos ou geradores precisam da mesma proteção.

## Estrutura raiz obrigatória

Formato correto:

```yaml
Screens:
  NomeDaTela:
    Properties:
```

Regras:

- `Screens:` deve começar na coluna 1, sem espaços, tabulação ou BOM.
- O nome da tela deve ter exatamente dois espaços de recuo.
- `Properties:` e `Children:` devem ter quatro espaços de recuo.
- Não envolver uma tela individual em outra chave ou indentar todo o arquivo.

### PA1001 — propriedade da tela não encontrada em `PaModule`

Exemplo:

```text
Property 'FocoAtracaoFauna' not found on type '...PaModule'
```

Causa encontrada: `Screens:` possuía espaços antes da chave e o nome da tela
ficou no mesmo nível. O Studio passou a interpretar o nome da tela como uma
propriedade direta de `PaModule`.

Correção: restaurar a estrutura raiz mostrada acima.

Prevenção: todo gerador deve normalizar a raiz e falhar se o arquivo não
começar literalmente com:

```text
Screens:\n  NomeDaTela:\n    Properties:
```

## Compatibilidade de controles modernos

### PA2108 — `Overflow` em `GroupContainer@1.5.0` AutoLayout

Causa: `Overflow` não é uma propriedade reconhecida nessa versão e variante.

Correção: usar somente as propriedades suportadas pelo modelo, como
`LayoutOverflowY`, quando ela já estiver presente em um controle compatível.

Prevenção: rejeitar qualquer linha `Overflow:` nos YAMLs gerados.

### PA2108 — `Tooltip` em `Button@0.0.45`

- Data: 2026-08-14. Projeto/tela: REA / tela única PLEM/PRAI.
- Mensagem: `Unknown property 'Tooltip' for control type 'Button@0.0.45'`.

Causa confirmada: `Tooltip` existe nos controles `Classic/*` (e em
`HtmlViewer@2.1.0`), mas não no botão moderno. A propriedade foi escrita por
analogia com o botão clássico, sem verificação.

Correção: remover a propriedade. `AccessibleLabel` **não** serve de
substituto — apesar de válida em `TextInput@0.0.54`, `ComboBox@0.0.51`,
`Toggle@1.1.5` e `DatePicker@0.0.46`, ela não aparece em nenhum
`Button@0.0.45` do export, ou seja, é igualmente não comprovada.

Validação preventiva (regra geral, vale para qualquer gerador): **o export do
Studio é a única fonte confiável do esquema**. Extrair do arquivo original o
conjunto de propriedades usadas por CADA tipo de controle e reprovar qualquer
propriedade fora desse conjunto no arquivo gerado. Adições deliberadas
(`DelayItemLoading`, `LoadingSpinner`, `DelayOutput`) ficam numa allowlist
explícita e justificada. Nunca supor que uma propriedade existe porque existe
em um controle parecido ou em outra versão do controle.

A mesma regra vale para **catálogos de valores**, não só nomes de
propriedades: o enum `Icon.*` dos controles clássicos e os nomes Fluent dos
ícones dos controles modernos (`Icon: ="Search"`) variam por versão. Na mesma
data, `Icon.Home`, `Icon.FilterFlat`, `Icon.RadarActivityMonitor` e
`Icon: ="Info"` foram escritos sem comprovação e trocados por valores presentes
no export (`Icon.DocumentWithContent`, `Icon.LogJournal`, `Icon: ="Search"`).
Truque útil: quando um controle é apenas alvo de clique transparente, reusar o
ícone que o próprio bloco já usa — assim ele é comprovado por construção.

### PA2108 — `Default` em `TextInput@0.0.54`

Causa: o TextInput moderno usa `Value`, não `Default`.

Correção:

```yaml
Value: =Parent.Default
```

Prevenção: inspecionar separadamente cada bloco `TextInput@0.0.54` e rejeitar
`Default:` dentro dele. `Default:` continua válido no DataCard pai.

## Nomes e referências

### PA2116 — `MetadataKey` repetida no mesmo DataCard

- Data: 2026-08-05.
- Projeto/tela: AirportNow 2.0 / `FocoAtracaoFauna`.
- Mensagem: `MetadataKey 'FieldValue' is already used`.

Causa confirmada: os dois ComboBox usados para formar `mapa_grade` estavam
marcados como `MetadataKey: FieldValue`. Dentro de um mesmo DataCard, o esquema
do Studio aceita somente um filho como valor canônico do campo.

Correção: manter `MetadataKey: FieldValue` somente no primeiro controle de
entrada (`cmbFocoAtracaoFaunaMapaLetra`). O segundo ComboBox continua dentro do
DataCard e participa da fórmula `Update`, mas sem `MetadataKey`.

Validação preventiva: para cada DataCard, contar as ocorrências de
`MetadataKey: FieldValue` e reprovar quando houver mais de uma. Em campos
compostos, controles auxiliares não devem repetir essa chave.

Impacto global: aplicar a mesma regra a DataCards compostos por data/hora,
coordenadas, intervalos, códigos segmentados ou múltiplos seletores.

### PA2110 — entidade com nome duplicado

Causa: dois controles com o mesmo nome dentro do módulo.

Correção: usar nomes descritivos e exclusivos para labels, entradas, erros,
containers e controles de galeria.

Prevenção: extrair todos os nomes definidos por `- NomeControle:` e reprovar
qualquer repetição antes da entrega.

### Referência a controle inexistente

Exemplo encontrado: `txtPresencaFaunaQuantidade` permaneceu na validação do
botão, embora a nova lista não tivesse o campo quantidade.

Correção: remover toda validação, `Update`, `Reset`, `SetFocus` ou fórmula
herdada de campos que não fazem parte do novo módulo.

Prevenção: comparar as referências de controles usadas nas fórmulas com os
nomes realmente definidos na tela e procurar campos residuais do módulo-base.

## Placeholders internos do template

Erro encontrado:

```powerfx
DataSourceInfo(%DATACARD_DATASOURCE_NAME.ID%; ...)
```

Causa: `%DATACARD_*%` pertence ao template interno do Studio e não é uma
fórmula Power Fx válida no Source Code colado pelo usuário.

Correção: remover o placeholder. Para TextInput moderno, não adicionar
`MaxLength` baseado nesse template.

Prevenção: rejeitar qualquer ocorrência de `%DATACARD_`.

## Estado vazio e galeria

Erro encontrado: a mensagem "Nenhum registro encontrado" e a galeria apareciam
simultaneamente.

Padrão correto:

```powerfx
GalleryModulo.AllItemsCount = 0
```

para o estado vazio, e:

```powerfx
GalleryModulo.AllItemsCount > 0
```

para cabeçalho e galeria.

`AllItemsCount` representa itens carregados, não o total da lista. O texto da
interface deve dizer "REGISTROS CARREGADOS", nunca "REGISTROS ENCONTRADOS".

## Performance e SharePoint

Padrão obrigatório para todas as telas históricas:

- Não executar `ClearCollect(ListaSharePoint, ...)` para copiar o histórico.
- A galeria deve consultar diretamente a lista com `Filter` delegável.
- Limitar a consulta inicial por `data_evento`.
- Usar filtros simples por `ativo`, `aeroporto` e intervalo de datas.
- Ativar `DelayItemLoading` e `LoadingSpinner` na galeria.
- Não usar `CountRows` ou `CountIf` sobre listas SharePoint grandes.
- Não executar `Refresh` apenas para trocar de aba.
- Manter `Refresh` somente depois de gravação/exclusão ou em ação explícita.
- Criar índices SharePoint para `data_evento`, `aeroporto` e `ativo`.
- Testar delegação no Studio com limite de linhas temporariamente definido como
  `1`.

## Locale de fórmulas: barra de fórmulas pt-BR × Source Code invariante

- Data: 2026-08-13. Projeto: REA / AppFormulas_PlemPrai.
- O Studio deste workspace opera no **padrão pt-BR**: tudo que for colado na
  **barra de fórmulas** (App.Formulas, App.OnStart, fórmulas avulsas em
  propriedades) usa `;` como separador de argumentos, `;;` como encadeador/
  terminador de definição, **vírgula como decimal** (`0,05`, nunca `0.05`) e
  comentários `//` e `/* */`.
- Já o **Source Code YAML** (`.pa.yaml` colado via exibição de código) fica no
  formato **invariante**: `,` nos argumentos, `;` no encadeamento, ponto no
  decimal — é assim que o Studio grava e lê, independentemente do locale.
- Correção aplicada: snippet de `App.Formulas` entregue em pt-BR; YAMLs
  mantidos invariantes.
- Validação preventiva: todo snippet destinado à barra de fórmulas deve ser
  revisado para pt-BR antes da entrega; todo YAML deve permanecer invariante.

## Padrões da refatoração PLEM/PRAI (2026-08-13)

Registrados na divisão de `REA/ScreenAcionamentosPlemPrai.pa.yaml` (14.878
linhas, 934 controles) em 7 telas geradas por `REA/gerar_telas_plem_prai.py`:

- **Divisão de tela-monólito**: extrair containers-overlay por blocos de texto
  (nunca round-trip YAML — PyYAML converte a chave `Y:` em booleano e perde
  formatação). Validar com `yaml.safe_load` + constructor para a tag
  `tag:yaml.org,2002:value` (o valor `=` sozinho é válido para o Studio, mas o
  PyYAML precisa do constructor).
- **`UpdateContext` → `Set` preservando nomes**: contexto vira global com o
  MESMO nome; nenhuma fórmula de leitura muda. Navegação entre telas =
  `Set(flag, true); Navigate(Tela, ScreenTransition.Fade)` — o flag continua
  controlando o overlay dentro da tela destino.
- **OnVisible de segurança**: toda tela composta só de overlays precisa de
  `If(!flagA && !flagB..., Set(flagEntrada, true))` no OnVisible — sem isso a
  tela pode abrir vazia.
- **Timer de monitoramento delegável**: nunca `CountRows(Filter(...))` sobre
  lista SharePoint em timer; comparar o maior `ID`
  (`First(Sort(Filter(lista, chave = x), ID, SortOrder.Descending)).ID`) com o
  último visto em variável; intervalo ≥ 30s.
- **Busca delegável**: `Search()` sobre lista SharePoint vira
  `Filter(... && StartsWith(coluna, txt))`; `StartsWith` com `||` de duas
  colunas continua delegável. `Search()` sobre coleção em memória pode ficar.
- **Controles referenciados de outra tela**: promover o valor a variável
  global (`Set` no `OnChange` + default no `OnVisible`); `EditForm`/`NewForm`
  antes de `Navigate` para form de outra tela é padrão aceito. `Reset()` de
  controle de outra tela: mover para o `OnVisible` da tela dona.
- **Tokens de tema em `App.Formulas`** (`thm*`): telas `.pa.yaml` não declaram
  named formulas — entregar snippet separado (ex.:
  `REA/AppFormulas_PlemPrai.fx.md`) e colar antes das telas.
- **Colagem com tela antiga presente** = `PA2110` em massa (nomes idênticos):
  remover/renomear a tela original no app antes de colar as novas.

## Otimização sem tocar no layout — PLEM/PRAI (2026-08-14)

Duas reescritas de layout desta tela foram **recusadas pelo usuário**, que
pediu explicitamente: manter a interface exatamente como está e melhorar só
performance, lógica e validade das fórmulas. Registro do que funcionou
(`REA/otimizar_tela_plem_prai.py` sobre
`REA/ScreenAcionamentosNewPlemPrai.pa.yaml`):

- **Trava de layout como prova, não como promessa**: quando o pedido é "não
  mexa no visual", o gerador deve *provar* isso. Técnica: parsear as duas
  árvores YAML, comparar propriedade a propriedade de cada controle e reprovar
  qualquer diferença que não esteja numa lista explícita de mudanças
  declaradas — e também reprovar mudança declarada que não ocorreu (pega patch
  que virou no-op). Propriedades puramente de performance
  (`DelayItemLoading`, `LoadingSpinner`, `DelayOutput`) entram numa allowlist
  de "pode ser acrescentada".
- **Timer de polling**: além de delegável (maior `ID`, nunca `CountRows`), tem
  de ser *gated* pela flag da seção (`If(var_visibleMonitor And ..., ...)`).
  Timer com `AutoStart: =true` + `Repeat: =true` **continua rodando com a
  seção invisível** — aqui varria a lista de atividades a cada 5s o app
  inteiro. Vira 30s + condição de visibilidade.
- **Galerias**: `DelayItemLoading: =true` + `LoadingSpinner: =LoadingSpinner.Data`
  em todas (aqui: 25 galerias, nenhuma tinha). Não altera layout.
- **Buscas**: `DelayOutput: =true` no `Classic/TextInput` de busca — sem isso
  cada tecla dispara consulta. Atenção: `HintText` pode ser bloco multilinha
  (`|-`), então detectar o campo de busca com regex de linha única falha.
- **`LookUp` repetido na mesma fórmula = uma consulta por repetição por
  linha da galeria.** Trocar por um `With({_x: LookUp(...)}, ...)`. Casos
  reais: 6→1 num `HtmlViewer`, 3→1 em três outros controles.
- **Statements duplicados** por copiar/colar: exclusão que roda `RemoveIf` duas
  vezes, `Patch` idêntico repetido nos dois ramos de um `If`. Além de lentos,
  dobram a escrita no SharePoint. `If(x, Patch(a,{c:false}), Patch(a,{c:true}))`
  vira `Patch(a, {c: !x})`.
- **Bugs de lógica achados (padrões a caçar em telas irmãs)**: variável de
  sessão usada onde devia ser o dado persistido (`ID_chat.chat` vs
  `var_dadosAcionamento.ID_chat` — quebra para quem não criou o registro);
  flag setada que nenhum controle lê (`var_visibleAcionamentoPRAI`, caminho
  morto de UI); ids trocados em `Patch` de log (`ThisItem.ID` no lugar de
  `ThisItem.ID_contato`); filtro por `varAeroUser` onde devia ser o aeroporto
  do registro aberto; `LookUp` em coleção que pode estar vazia quando o mesmo
  dado já está numa variável recém-atribuída.
- **Retorno de fluxo sem guarda**: `Set(var, Fluxo.Run(...).campo)` seguido de
  uso incondicional. Se o fluxo falha, o valor fica em branco e todas as ações
  seguintes falham caladas — colocar `If(IsBlank(var), Notify(...))`.

### Aplicado também na tela de contatos (`REA/otimizar_tela_contatos.py`)

- **Quebra de linha do arquivo é parte da fidelidade**: o export do Studio pode
  vir em **CRLF** (a tela de contatos veio 100% CRLF; a de acionamentos veio
  LF). `open()` em modo texto normaliza na leitura e regrava em LF — o gerador
  reescreveria silenciosamente **todas** as linhas. Ler e gravar com
  `newline=''`, normalizar para `\n` só durante o processamento e restaurar o
  final original na gravação. Conferir com `grep -c $'\r'` antes e depois.
- **Um `DelayOutput` pode valer por tudo**: aqui a caixa de busca alimentava a
  galeria *e* um `HtmlViewer` de relatório que refazia filtro, ordenação,
  `CountRows`/`CountIf` e um `Concat` sobre a base inteira. Antes de otimizar
  fórmula por fórmula, procurar **quem depende do campo de texto** — cada
  dependente é recalculado a cada tecla.
- **`Refresh` em cascata**: `OnSuccess` de form dando `Refresh` e logo depois
  `Select(BotãoAtualizar)`, que dá os mesmos `Refresh`. Mapear quem já
  atualiza o quê antes de acrescentar `Refresh`.
- **`Sort` dentro de `ClearCollect` que a galeria reordena** é trabalho jogado
  fora; a ordenação de exibição pertence ao `Items`.
- **`ClearCollect` de lista grande é um teto silencioso**: `tbl_contatos_entidades`
  tem ~947 registros e o limite padrão de linhas é **500** — com o filtro de
  aeroporto vazio a coleção trunca e a busca deixa de achar contatos que
  existem. Isso **não se resolve na fórmula**: ou eleva-se o limite para 2000
  em Configurações → Geral, ou o filtro passa a ser obrigatório.

## `Distinct()` + `ThisRecord` — dedup que devolve N cópias do primeiro registro (2026-08-24)

- Projeto/tela: REA / `ScreenAcionamentosNewPlemPrai` — `FormOcorrenciaAcionamento.OnSuccess`.
- Sintoma em produção: o acionamento de teste disparou **4 cartões idênticos**
  para a mesma pessoa no Teams e 4 linhas iguais
  `Gerente Teste > Gilberto Marques Claudino > Notificado via Flow` no chat do
  grupo. **Não houve erro no Studio nem no Power Automate** — os dois fizeram
  exatamente o que foi pedido.

Código que causou:

```powerfx
ClearCollect(
    col_emailsCcrFilter,
    ForAll(
        Distinct(col_emailsCcrFilter, Email),
        LookUp(col_emailsCcrFilter, Email = ThisRecord.Email)
    )
)
```

Causa confirmada — **dois defeitos somados**:

1. `Distinct()` devolve uma tabela de **uma coluna chamada `Value`**, nunca com
   o nome da coluna de origem. `ThisRecord.Email` não existe nesse escopo; como
   está dentro de um `LookUp`, o `ThisRecord` **religa ao escopo interno do
   próprio `LookUp`** (o mais interno vence). A condição vira `Email = Email`,
   sempre verdadeira, e o `LookUp` devolve o **primeiro registro** em toda
   iteração. Resultado: N cópias do primeiro contato.
2. `ClearCollect` cujo alvo é **a mesma coleção que está sendo lida** na
   expressão de origem. O `Clear` acontece antes de a origem terminar de ser
   avaliada — comportamento não definido pela documentação.

Correção:

```powerfx
ClearCollect(
    col_emailsUnicos,
    ForAll(
        Distinct(col_emailsCcrFilter, Email) As EMAIL_UNICO,
        LookUp(col_emailsCcrFilter, Email = EMAIL_UNICO.Value)
    )
);
Clear(col_emailsCcrFilter);
Collect(col_emailsCcrFilter, col_emailsUnicos)
```

`As <alias>` elimina a ambiguidade de escopo; `.Value` usa o nome real da coluna
do `Distinct`; a coleção temporária remove a autorreferência.

**Impacto real, maior que a duplicidade:** a coleção corrompida alimentava
`JSON_PARTICIPANTES`, que criava o chat do Teams. O grupo foi criado com **uma
única pessoa repetida** — os demais participantes **nunca foram notificados nem
entraram no chat**. Em sistema de emergência, "notificação duplicada" era o
sintoma visível de "notificação não entregue".

Validação preventiva (implementada em `REA/otimizar_tela_plem_prai.py`):

- Reprovar `ThisRecord.<col>` dentro de `ForAll(Distinct(...))` quando `<col>`
  não for `Value` — varredura por balanceamento de parênteses, não regex de
  linha, porque a fórmula é multilinha. `ThisRecord.Value` **sem** alias é
  legítimo e não pode ser falso positivo.
- Reprovar `ClearCollect(x, ...)` cuja expressão de origem cita `x`.

**Regra geral que fica:** `Distinct`, `Split`, `Ungroup` e `Search` devolvem
tabelas com **nomes de coluna próprios** (`Value`, `Result`). Nunca supor que a
coluna manteve o nome de origem. E em `ForAll`/`Filter`/`LookUp` aninhados,
sempre usar `As <alias>` — `ThisRecord` sem alias liga ao escopo mais interno,
que quase nunca é o que se quer.

**Impacto global:** procurar o mesmo padrão em qualquer tela que monte lista de
destinatários, participantes ou aprovadores. Bug silencioso — não gera erro,
gera notificação faltando.

## Power Apps trava esperando o fluxo: "Responder ao app" tem que vir primeiro (2026-08-24)

- Projeto/tela: REA / `ScreenAcionamentosPlemPrai` — `EnviarAcionamentocomOpcao`,
  chamado dentro de `ForAll(col_emailsCcrFilter, ...)`.
- Sintoma: ao iniciar um acionamento a tela ficava congelada vários segundos,
  às vezes dezenas, proporcional ao número de participantes.

Num gatilho **PowerApps V2**, `.Run()` só devolve o controle ao app quando o
fluxo chega à ação **Responder ao Power App**. Se não houver nenhuma, devolve
quando o fluxo inteiro termina. O fluxo fazia, nessa ordem: enviar e-mail →
postar no Teams → responder. Multiplicado por N participantes dentro de um
`ForAll`, o app somava N × (e-mail + post).

**Regra:** em fluxo disparado pelo app, `Responder ao app` é a **primeira**
ação, a menos que o app precise de um valor calculado — e aí ela vem
imediatamente depois da ação que produz esse valor, nunca no fim.

- `EnviarAtividadeparachatteams`: responde primeiro, posta depois.
- `EnviarAcionamentocomOpcao`: responde primeiro; e-mail, post e a espera de 4h
  correm depois.
- `CriarchatdeacionamentosPLEM/PRAI`: o app precisa do `ID_chat`, então a
  resposta vem logo após `Criar um chat`; cartão, e-mail e log vêm depois dela.

Efeito colateral aceito: o app deixa de saber se o post falhou. Para
notificação isso é troca boa — a fonte da verdade é o log no SharePoint, e os
posts ganharam `retryPolicy` exponencial.

Corolário: **um fluxo por item dentro de `ForAll` é sempre N viagens HTTP.**
Quando a lista é grande, mandar o JSON inteiro para um fluxo que faz
`Apply to each` com concorrência troca N chamadas por uma.

## Trava de reentrância com carimbo de hora — e por que ela precisa se soltar sozinha (2026-08-24)

- Sintoma: duplo clique em "Iniciar Fluxo de Acionamento" abria dois
  acionamentos e criava dois chats no Teams.

`UpdateContext` vale imediatamente para as instruções seguintes da **mesma**
fórmula, mas a UI só repinta quando o `OnSelect` termina. Um segundo clique
enfileirado durante a execução roda o `OnSelect` de novo. Por isso a trava tem
que estar **dentro** do `OnSelect`, no topo:

```powerfx
If(
    !IsBlank(var_ocupadoDesde) && DateDiff(var_ocupadoDesde, Now(), TimeUnit.Seconds) < 30,
    Notify("Aguarde: a ação anterior ainda está sendo processada.", NotificationType.Warning, 3000),
    UpdateContext({var_ocupadoDesde: Now()});
    ...trabalho...;
    UpdateContext({var_ocupadoDesde: Blank()})
)
```

O carimbo de hora é o ponto que importa. Uma trava booleana (`var_ocupado:
true`) que não seja limpa por causa de um erro no meio do `OnSelect` deixa o
botão **morto até o app ser reaberto** — o remédio vira pior que a doença. Com
`Now()` a trava expira sozinha; e `OnVisible` da tela limpa por garantia.

Não usar `DisplayMode` para isso: a fórmula depende de `Now()`, que não é
reavaliado sozinho, então o botão pode ficar desabilitado sem nada que o
reative.

## Todo overlay de carregamento precisa de um caminho de saída (2026-08-24)

- Projeto/tela: REA / `ScreenAcionamentosPlemPrai` — `PopUpLoadConfigFLuxo`,
  controlado por `var_visibleConfigFluxo`.

`OnSuccess` ligava o overlay logo no começo e só o desligava no ramo de sucesso
final. Qualquer saída antecipada — nenhum participante encontrado — deixava o
spinner girando **para sempre**, com a tela inteira coberta. E o formulário não
tinha `OnFailure`: erro de gravação no SharePoint dava o mesmo resultado.

**Regra:** para cada variável que liga um overlay/spinner, procurar **todos** os
ramos que saem da rotina — inclusive os de validação e os de erro — e desligar
em cada um. `OnFailure` de formulário não é opcional quando `OnSuccess` liga
estado de UI.

## A mensagem se monta no fluxo, não no app (2026-08-24)

Nove pontos da tela montavam a frase enviada ao Teams com concatenação inline
(`" > chegou."`, `"foi colocado em estado de sobreaviso."`). Resultado: nenhuma
hora, nenhuma hierarquia visual, `>` fazendo três papéis na mesma linha, e
qualquer ajuste de formato virava nove edições.

Passou a ser: o app manda **dados** e o fluxo resolve o ícone/rótulo por um
`json(...)` indexado pelo tipo, com `coalesce` para um valor padrão — tipo
desconhecido nunca deixa a mensagem sem publicar.

## Não mude a assinatura do gatilho: codifique dentro de um parâmetro existente (2026-08-24)

A primeira versão dessa refatoração trocou `.Run(Mensagem, ID_chat)` por
`.Run(Detalhe, ID_chat, Tipo, Ator)`. Parecia limpo e era a coisa mais cara
da entrega.

O gatilho **PowerApps V2 guarda o esquema dentro do app**. Mudar o número de
parâmetros obriga a **remover e re-adicionar o fluxo** em *Dados > Power
Automate* — e nesse passo o Studio renomeia para `NomeDoFluxo_1` se o antigo
ainda estiver lá, o que faz o YAML colado não encontrar mais a referência. Vira
uma janela de indisponibilidade num sistema de emergência, por causa de
cosmética de mensagem.

Solução: **manter o esquema byte a byte** e codificar os campos novos dentro do
parâmetro de texto que já existe.

```
"CHEGOU§" & _ator & "§" & _detalhe        // app
@split(concat(coalesce(triggerBody()?['text'], ''), '§§'), '§')   // fluxo
```

- O padding com dois separadores garante os índices 0/1/2 mesmo em mensagem
  legada, sem estourar o `split` — importante porque `if()` no Logic Apps
  **avalia os dois ramos**, então índice fora de faixa quebra mesmo no ramo
  que não seria usado.
- `contains(texto, '§')` distingue payload novo de mensagem antiga: o fluxo
  novo publica mensagem antiga como sempre publicou.
- O app remove `§` de todo texto digitado antes de montar o payload.
- Resultado: app e fluxo podem ser atualizados **em qualquer ordem**. O pior
  caso é uma mensagem feia por alguns minutos, nunca um erro de compilação.

O gerador tem asserção que compara o esquema do gatilho antes e depois e
**aborta** se mudar. Ver `REA/PADRAO_MENSAGENS_TEAMS.md`.

## Atualizar fluxo de solução gerenciada: subir a versão, não importar cópia (2026-08-24)

Importar os fluxos como **pacote herdado** (`Meus fluxos > Importar Pacote`)
cria fluxos **novos, com IDs novos**. O app continua chamando os antigos, e
reapontá-lo exige justamente o remover/re-adicionar que se quer evitar.

O caminho sem impacto é reempacotar a **mesma solução gerenciada** com a versão
incrementada e os mesmos `WorkflowId` do `customizations.xml`
(`REA/gerar_solucao_migracao.py`, 1.0.0.5 → 1.0.0.6). O Power Platform trata
como atualização: as definições são substituídas no lugar, IDs e connection
references intactos, app sem nenhum ajuste.

Duas armadilhas ao reempacotar:

1. **Ler e gravar em binário.** O export original vem com **CRLF** e BOM no
   `[Content_Types].xml`. Lendo em modo texto, o Python normaliza para LF e
   descarta o BOM, e aí *todos* os 14 arquivos aparecem como alterados — o que
   esconde o que de fato mudou e faz a solução tocar fluxos que não deveria.
2. **Conferir o diff contra o pacote anterior.** O gerador compara os dois zips
   e a entrega só é válida se os únicos arquivos diferentes forem os fluxos
   realmente refatorados e a tag `<Version>`.

## Propriedade que o Studio descarta em silêncio: `DelayItemLoading` não existe em `Gallery@2.15.0` (2026-08-24)

- Projeto/tela: REA / `ScreenAcionamentosPlemPrai` e `ScreenContatos`.
- Sintoma: `otimizar_tela_plem_prai.py` injetava `DelayItemLoading: =true` +
  `LoadingSpinner: =LoadingSpinner.Data` nas 25 galerias. O arquivo foi colado
  no Studio e o **reexport voltou sem nenhuma das duas**. Sem erro, sem
  PA2108, sem aviso — o `DelayOutput` injetado no mesmo passo em
  `Classic/TextInput@` sobreviveu normalmente.

Como diagnosticar sem ambiente: **o Studio grava as propriedades de cada
controle em ordem alfabética.** Propriedade fora da ordem alfabética foi
injetada por script e nunca passou por um round-trip; propriedade em ordem
alfabética foi escrita pelo próprio Studio, e isso é prova de que o controle a
suporta.

Varredura em todos os exports do repositório:

| Propriedade | Onde aparece | Ordem alfabética? |
|---|---|---|
| `LoadingSpinner` | 7 galerias `Gallery@2.15.0` em 3 telas de PerdidoseAchados | **sim** — Studio escreveu |
| `DelayItemLoading` | 3 ocorrências, todas em arquivos gerados por script | **não, em nenhuma** |

Conclusão: `DelayItemLoading` é propriedade da galeria **clássica**. Todas as
galerias deste repositório são `Gallery@2.15.0` (moderna), que não a tem — o
Studio descarta em silêncio. `LoadingSpinner` é válido na moderna, mas foi
descartado junto no mesmo bloco.

**O ganho de performance prometido nunca existiu.** Pior que não ganhar:
ficou documentado como entregue.

**Regras que ficam:**

1. Nunca acrescentar propriedade que o export de origem não comprove. Se o
   gerador precisa de uma lista `ADDABLE`, cada item dela é uma **aposta**, não
   um fato — e tem que estar comprovado em algum export real do mesmo
   `Control:` e versão.
2. Para conferir se o controle suporta a propriedade, procurar a propriedade em
   **posição alfabética** dentro do bloco `Properties:` de algum export do
   Studio. Fora de ordem = injetada, não comprova nada.
3. Ao injetar, inserir na posição alfabética. Além de imitar o Studio, faz o
   reexport sair idêntico e mantém o diff seguinte limpo.
4. Propriedade que some no reexport é o único aviso que se vai receber.
   Fechar o ciclo: colar, reexportar, **conferir que a propriedade continua
   lá** — de preferência numa sonda de um controle só antes de valer para 25.

`refatorar_msgs_teams.py` passou a oferecer `--spinner` (e `--spinner --sonda`)
como opção explícita, desligada por padrão: `LoadingSpinner` é cosmético,
não é performance, e mexe no que o usuário vê.

## Ícone não existe: nos quatro meios do Power Platform, identidade é tipografia e cor (2026-08-24)

Pedido do usuário: "evite emoji, use ícones se puder". Levantei o que cada meio
aceita antes de decidir:

| Meio | Ícone real? | Por quê |
|---|---|---|
| E-mail | Não | Outlook desktop renderiza com o motor do **Word**: sem SVG; imagem externa é bloqueada por padrão |
| Adaptive Card (Teams 1.4) | Não | `Icon` só existe no schema 1.5+; `Image` exigiria URL hospedada |
| Post HTML no chat | Não | o Teams remove estilo das mensagens de bot |
| `HtmlViewer` (Power Apps) | Não | o sanitizador remove `<svg>` |

Conclusão que vale como regra: **quando o meio não tem ícone, a hierarquia vem
de peso tipográfico, cor e chips de texto** (`<span>` com `background`,
`border-radius`, `font-size` menor) — não de emoji, que é a saída fácil e o que
faz a peça parecer amadora.

E a distinção que importa na hora de limpar: **emoji decorativo sai; sinal
gráfico é substituído, não removido**. `📝 Editar` e `❌ Excluir` viraram
`Editar` e `Excluir`. Já as setas `⬇` entre nós do fluxograma comunicam a
direção do fluxo, então viraram `↓` (U+2193): mesma informação, sem
apresentação emoji — que em vários clientes renderiza colorida e quebra o tom
corporativo. Depois disso a tela sai com **zero** caracteres da faixa emoji.

## Trava de layout com exceções declaradas — e a regra que vale mais que a lista (2026-08-24)

Quando o usuário autorizou mexer nas cores, a trava que reprovava toda mudança
visual precisou abrir — sem virar liberação genérica. O desenho que ficou:

1. `EXCECOES_SOMEM` / `EXCECOES_SURGEM`: pares nominais, linha exata. A guarda
   exige que **cada exceção declarada de fato tenha ocorrido** — exceção
   declarada e não aplicada reprova igual a mudança não declarada. Isso pega o
   caso em que um patch para de casar e passaria despercebido.
2. Para mudanças repetitivas, lista nominal seria ruído. Entraram duas
   **regras**: a linha que sumiu tem que casar com a que surgiu *depois de
   remover o emoji*, ou *depois de aplicar o mapa de substituição de glifo*
   (`⬇` → `↓`). Qualquer outra diferença de texto continua reprovando. Uma
   regra cobriu 19 linhas sem virar lista de 19 itens; a guarda conta quantas
   casaram e imprime o número.

Duas armadilhas na implementação:

- **Diff por `Counter`, não por lista ordenada.** A mesma linha visual aparece
  dezenas de vezes no YAML; comparar listas ordenadas esconde a mudança de uma
  ocorrência entre N idênticas.
- **Contexto único.** Patch de linha curta (`Fill: "=\n RGBA(255,255,0..."`)
  casava em 2 controles diferentes. A solução foi ampliar o `old` até incluir a
  propriedade vizinha, não relaxar a contagem.
- **Substring por indentação.** `texto.count(linha)` devolveu 4 onde havia 3
  ocorrências reais: uma linha menos indentada é substring de uma mais
  indentada. Ancorar o `old` com `\n` dos dois lados resolve — vale para
  qualquer patch de linha única em YAML indentado.
- **Range que corta no lugar errado.** Dois patches recortaram o bloco sem
  incluir a linha `Items: |-` (ou o `)` final): o YAML virou inválido e a
  fórmula ficou com parêntese sobrando. Calcular o fim do bloco por
  **balanceamento de parênteses**, não por "primeira linha que parece o fim", e
  validar o YAML + o balanço de toda fórmula depois de gerar.

Também caiu uma checagem que parecia defensiva e era falso positivo: "o texto
novo já existe na origem → patch já aplicado". Num patch de rótulo curto, o
texto novo (`Text: ="Excluir"`) legitimamente já existe em outro controle. A
asserção de contagem sobre o `old` já prova que o patch não foi aplicado.

## Ordem de gravação define ordenação: o "hack do -1 minuto" (2026-08-24)

O log de `CRIAÇÃO` gravava `Hora: DateAdd(Now(), -1, TimeUnit.Minutes)` só para
ficar acima dos `NOTIFICADO` numa galeria ordenada por `Hora` desc. O `ForAll`
de notificações roda um `Patch` por participante — se passasse de um minuto, a
ordem invertia de novo e o hack se voltava contra si.

**Regra:** quando a ordenação depende do relógio, corrija a **ordem de
gravação**, não o valor gravado. Aqui bastou mover o log de criação para antes
do `ForAll` e usar `Now()` limpo.

Corolário do mesmo dia: campo omitido no `Patch` fica **nulo, não zero**.
`NOTIFICADO` sem `Ativo` nunca casava com `ThisItem.Ativo = 0` e o botão
"Acionar" simplesmente não aparecia para essas linhas — sem erro, sem aviso.

## Auditoria de tela grande: o que só aparece cruzando escrita com leitura (2026-08-24)

Numa tela de 14.9k linhas, os bugs que mais custaram não estavam em fórmula
errada — estavam em **contrato quebrado entre quem escreve e quem lê**:

- Um `If(Acionamento = "PLEM" && acao = "Iniciar", <criar>, <finalizar>)`:
  iniciar um acionamento **PRAI** caía no `else` e gravava FINALIZAÇÃO na hora,
  notificando "finalizado com sucesso". O ramo `else` estava fazendo dois
  papéis.
- `Acao` gravado com o **nível do contato** enquanto o texto e o `Ativo` vinham
  da **coluna clicada** na UI.
- Campo gravado sem `Ativo` fica **nulo**, e `nulo ≠ 0`: os testes
  `ThisItem.Ativo = 0` nunca casavam e o botão simplesmente não aparecia.
- `StartsWith(Acao, filtro)` num combo de filtro fazia "ACIONAR" trazer também
  "ACIONAR_SOBREAVISO".
- Quatro galerias copiadas: o bug foi corrigido **em uma** e ficou nas outras
  três (excluir vítima de Prioridade II, III e IV não gerava log nem aviso).

**Método que achou tudo isso:** listar todos os literais **gravados** numa
coluna e todos os literais **comparados** na leitura, e cruzar. Divergência dos
dois lados é bug silencioso — não gera erro, gera dado faltando.

## Otimização que parece cache mas não é (2026-08-24)

Um timer de 30 s comparava "maior ID na lista" com "maior ID na galeria" para
só então dar `Refresh`. Os dois lados liam o **mesmo cache** do datasource:
sempre iguais, refresh quase nunca. Quem traz dado novo é justamente o
`Refresh` — ele é o passo, não a consequência.

Padrão irmão: `First(Sort(Filter(tbl, ...)))` dentro da propriedade `Fill` de
uma galeria é **uma consulta por linha, a cada render**. A correção é calcular
uma vez numa coleção (`ClearCollect(col_status, ForAll(Distinct(...), ...))`) no
mesmo lugar que já faz o `Refresh`, e a `Fill` virar `LookUp(col_status, ...)`.
Ao fazer isso, garanta que a coleção é populada **antes do primeiro render** —
senão as cores abrem vazias até o timer rodar.

## Checklist obrigatório antes da entrega

1. Executar o gerador duas vezes e confirmar que o hash do YAML não muda.
2. Validar sintaxe YAML.
3. Confirmar a estrutura raiz e a indentação exata.
4. Verificar nomes duplicados.
5. Verificar referências a controles inexistentes.
6. Rejeitar `Overflow:`, `%DATACARD_` e `Default` em TextInput moderno.
7. Validar todos os `DataField` contra os nomes internos da lista.
8. Procurar campos, controles, coleções e mensagens residuais da tela-base.
9. Validar estado vazio, galeria e contador.
10. Validar filtros delegáveis e limites da consulta inicial.
11. Colar no Power Apps Studio conectado à lista real.
12. Testar criar, visualizar, editar, excluir, anexar e filtrar.
13. Conferir `Distinct`/`Split`/`Ungroup`: coluna é `Value`/`Result`, não o
    nome de origem. Em `ForAll`/`LookUp` aninhados, exigir `As <alias>`.
14. Em fluxo disparado pelo app: `Responder ao app` é a primeira ação (ou logo
    após a ação que produz o valor de retorno), nunca no fim.
15. Todo botão que chama fluxo ou grava vários registros tem trava de
    reentrância com carimbo de hora que expira sozinha.
16. Toda variável que liga overlay/spinner é desligada em **todos** os ramos de
    saída, inclusive validação e `OnFailure`.
17. Nenhuma chamada a fluxo de chat com `ID_chat` em branco.
18. Esquema de gatilho de fluxo inalterado — se precisar de campo novo,
    codificar dentro de um parâmetro existente com fallback nos dois sentidos.
19. Atualização de fluxo de solução gerenciada = mesma solução com versão
    incrementada e mesmos `WorkflowId`; conferir que só os arquivos esperados
    diferem do pacote anterior (ler/gravar em binário para não falsear o diff).
20. Toda propriedade acrescentada tem que estar comprovada em **posição
    alfabética** num export do Studio do mesmo `Control:` e versão. Depois de
    colar, reexportar e confirmar que ela continua lá.
21. Cruzar literais gravados × literais lidos em cada coluna de enumeração
    (`Acao`, `Status`): divergência é bug silencioso.
22. Campo numérico não gravado fica **nulo**, e `nulo ≠ 0` — se algum teste
    compara com `0`, gravar `0` explicitamente.
23. Patch de linha única em YAML indentado: ancorar com `\n` nos dois lados,
    senão a linha menos indentada casa dentro da mais indentada.
24. Bug encontrado em galeria copiada: procurar as outras cópias antes de
    considerar corrigido.
21. Exceção visual é **declarada nominalmente** e a guarda exige que ela tenha
    ocorrido; para mudanças repetitivas, declarar uma **regra** verificável em
    vez de lista. Diff de linhas visuais sempre por `Counter`, nunca por lista
    ordenada.
22. Ordenação que depende de relógio se corrige na **ordem de gravação**, não
    no valor. E campo omitido em `Patch` fica **nulo**, não zero — todo teste
    `= 0` sobre coluna opcional é um bug latente.

Os itens 11 e 12 dependem do ambiente Power Apps/SharePoint e não podem ser
substituídos apenas por validação local do arquivo.

## Sim/Não do SharePoint: `!Coluna` não é o mesmo que `Coluna <> true`

Sintoma: as pílulas do fluxograma pararam de pintar. A fórmula compilava, a
legenda estava certa, as atividades apareciam na lista — mas o `Filter` da cor
voltava vazio e o `Switch` caía no default (branco).

Causa: o predicado tinha ganhado `And !Excluido`. `Excluido` é uma coluna
**Sim/Não** do SharePoint e **nenhum** dos 19 `Patch` que criam atividade a
preenche — ela nasce **NULA**, não `false`. Delegado, `!Excluido` vira
`Excluido eq false`, e no SharePoint **NULL não casa com `eq false`**. Resultado:
zero linhas.

Regra: para coluna Sim/Não que pode estar em branco, use sempre

```
Filter(tbl; ... And Coluna <> true)     // OData: ne true -> casa NULL e false
```

e nunca `!Coluna` / `Coluna = false`. Vale para qualquer coluna adicionada
depois que a lista já tinha itens, ou nunca escrita no `Patch` de criação.

Como isso passou pelas verificações: sintaxe válida, YAML válido, árvore de
controles idêntica, fórmula balanceada. É um defeito de **dados**, não de forma
— só aparece rodando contra a lista real. Quando um patch acrescenta predicado
a um `Filter` já existente, conferir antes se a coluna é sempre preenchida.

## Nomes de coluna como identificadores: `ShowColumns("col")` não compila (2026-08-25)

- Projeto/telas: Frotas / `scrLoginContexto`, `scrFrotaPainel`, `scrFrotaLista`.
- Mensagens: `Nome do identificador esperado` apontando para `"ID"` dentro de
  `ShowColumns`; `A coluna especificada 'Qtd' não existe` num `SortByColumns`.

Causa confirmada: apps criados com **"Nomes de coluna como identificadores"**
ligado (padrão nos apps novos) não aceitam mais nome de coluna como **string**
em `ShowColumns`, `RenameColumns`, `AddColumns`, `DropColumns` e
`SortByColumns`. O erro é de **parsing**, então ele derruba a fórmula inteira e
gera dezenas de erros derivados (`Caracteres inesperados`, `Eof`, nomes
"não reconhecidos") que não têm nada a ver com a causa.

Correção adotada — formas que funcionam **nos dois modos**, sem depender da
configuração do app:

| Em vez de | Use |
|---|---|
| `ShowColumns(t, "a", "b")` | `ForAll(t As _r, { a: _r.a, b: _r.b })` |
| `RenameColumns(t, "a", "Value")` | `ForAll(t As _r, { Value: _r.a })` |
| `SortByColumns(t, "a", SortOrder.Ascending)` | `Sort(t, a, SortOrder.Ascending)` |

`Sort` recebe **fórmula de escopo**, não string, e por isso é imune. O `As`
explícito ainda é obrigatório em `ForAll` aninhado (item 13 do checklist).

Validação preventiva: reprovar `"` como argumento de coluna em
`ShowColumns|RenameColumns|AddColumns|DropColumns|SortByColumns` no YAML gerado.

## 97 erros, uma causa: named formula ausente derruba a tela inteira (2026-08-25)

Mesma ocorrência. O painel de erros do Studio mostrava 97 itens em 3 telas:
`'colPerfil' não é reconhecido`, `A função 'LookUp' tem argumentos inválidos`,
`'Valor' não é reconhecido`, `O operador "." não pode ser usado em valores
Unknown`, `Tipo de argumento inválido (Boolean). Esperando um valor Table`.

Nenhum deles era um erro real de tela: o `App.Formulas` não estava colado, e
sem `colPerfil`/`colAerosValidos` o `Set(varAerosPermitidos, If(...))` resolve
para **Boolean** — daí o `CountRows(varAerosPermitidos)` reclamar de tipo em
outra tela, a três saltos de distância da causa.

Regra: **erro de nome desconhecido tem precedência sobre todo o resto.** Antes
de mexer em qualquer fórmula, conferir na ordem — (1) `App.Formulas` colado e
sem erro, (2) fontes de dados adicionadas, (3) só então ler o painel de erros.
Contagem de erros não é medida de gravidade; uma linha ausente produz dezenas.

## Sim/Não do SharePoint: a saída definitiva é não usar Sim/Não (2026-08-25)

Complementa a seção anterior sobre `!Coluna` × `Coluna <> true`. Em Frotas as
três colunas booleanas (`circula_lado_ar`, `conforme_lado_ar`,
`pode_baixar_ativo`) foram criadas como **Número** com padrão `0`.

Motivo: Sim/Não sem valor gravado nasce **NULA**, e `NULL` não casa com
`eq false` no OData — o filtro volta vazio, sem erro. Número com valor padrão
nasce preenchido.

Como o app testa: positivo `= 1`; negativo `<> 1`. Nunca `= 0` — isso perderia
o nulo de qualquer registro criado fora do app (importação, edição na lista).

## PA1001 / YamlInvalidSyntax: fórmula sem `=` (2026-08-25)

- Projeto/telas: Frotas / trilho de navegação nas três telas internas.
- Mensagem: `(172,39) : error PA1001 : An error occurred while parsing PaYaml.
  Error code: YamlInvalidSyntax; Reason: Power Fx expressions must start with '='.`

Causa confirmada: o gerador do trilho recebia o corpo do `OnSelect` como string
e só um dos botões foi escrito sem o `=` inicial. YAML válido, indentação certa,
fórmula correta — e mesmo assim o Studio recusa o arquivo inteiro.

**Toda** propriedade de controle no Source Code é expressão Power Fx e começa
com `=`, inclusive dentro de bloco escalar `|-`: a primeira linha é `=Set(...)`,
não `Set(...)`. Vale igual para `Text:`, `Visible:`, `Height:` — `Height: 40`
sem `=` também reprova.

Validação preventiva adicionada em `Frotas/validar_telas.py`: percorre a árvore
e reprova qualquer valor dentro de `Properties:` que não seja string começando
com `=` (o parser YAML entrega `40` como int e `true` como bool, então o teste
`isinstance(val, str) and val.startswith('=')` pega os dois casos).

Regra para geradores: quando o corpo da fórmula vem de constante/parâmetro,
o `=` é responsabilidade de **quem monta a linha**, não de quem escreve a
constante — ou o gerador acrescenta sempre, ou a guarda reprova. Neste caso as
duas coisas foram feitas.

## Formulário em branco: container AutoLayout não cresce com o conteúdo (2026-08-25)

- Projeto/tela: Frotas / `scrFrotaForm`.
- Sintoma: as 7 seções do formulário apareciam com cabeçalho e **espaço vazio**.
  Nenhum erro no Studio, YAML válido, 142 controles na árvore.

Causa confirmada: as grades de campos eram `GroupContainer@1.5.0` AutoLayout
com `LayoutWrap: =true`, `FillPortions: =0` e **sem `Height`**. Container
AutoLayout do Power Apps **não tem "hug contents"**: sem `Height` (eixo
vertical) ou `Width` (eixo horizontal) e sem `FillPortions`, ele fica com a
altura padrão e o conteúdo não aparece. `LayoutWrap` piora, porque a quebra
depende de uma caixa com tamanho conhecido.

Correção: trocar a grade que quebra por **linhas de altura explícita** — cada
linha um container horizontal com `Height` fixo e 3 campos com
`FillPortions: =1` (largura responsiva, altura determinística). A altura da
seção passou a ser calculada pelo gerador:
`18 + 46 (cabeçalho) + 16*n_linhas + soma(alturas) + 20`.

Validação preventiva em `Frotas/validar_telas.py`: todo `GroupContainer`/
`Gallery` filho de um AutoLayout precisa ter, **no eixo do pai**, `Height`
(pai vertical) ou `Width` (pai horizontal), ou `FillPortions` diferente de 0.
A mesma regra pegou dois containers do login que tinham perdido o
`FillPortions: =1` num round-trip pelo Studio.

`HtmlViewer` é exceção legítima: `AutoHeight: =true` dá altura própria a ele.

## Round-trip pelo Studio renomeia controle copiado: `cntMenuPnl_1` (2026-08-25)

Ao replicar o trilho de navegação copiando/colando **dentro do Studio**, a
tela de destino voltou no export com `cntMenuPnl_1`, `htmMenuMarcaPnl_1`,
`btnMenuPainelPnl_1` — o Studio renomeia porque **nome de controle é único no
app inteiro**, não por tela.

Consequência prática: o arquivo local e o app saem de sincronia, e o gerador
não reconhece mais o bloco que ele mesmo escreveu (`cntMenuLst` não existe;
existe `cntMenuPnl_1`). Além disso o item ativo do trilho fica errado, porque
veio da tela copiada.

Regra: bloco replicado em várias telas é **gerado**, nunca copiado no Studio.
`Frotas/desfazer_menu.py` remove o shell e devolve o container raiz ao topo,
para o `aplicar_menu.py` reinjetar com os nomes canônicos.

Armadilha de implementação nos dois scripts: recuo de bloco YAML medido "de
cabeça". `s.index("        Properties:")` (8 espaços) casa dentro de uma linha
de 10 ou 12 espaços, porque é substring — e o patch entra com o recuo errado,
gerando `Properties:` seguido de propriedade fora de nível. Ancorar sempre com
`\n` + o recuo exato, e conferir o YAML depois de cada passo.

## Auditoria 2026-08-25: três defeitos que nenhuma regra anterior via

**1. YAML válido com subárvore desanexada.** Um `Children:` reindentado com 2
espaços a menos vira **chave irmã do controle** dentro do item da lista — o
YAML continua válido, o Studio até aceita, mas o parse entrega o container com
zero filhos. Efeito duplo: as regras baseadas em árvore (tamanho, contraste,
prefixo `=`) pularam a tela inteira em silêncio, enquanto a contagem por regex
seguia batendo. Regra 15: item de `Children:` com mais de uma chave reprova, e
a contagem de controles por regex tem que bater com a contagem pela árvore.

**2. `Navigate` para a própria tela não reexecuta o `OnVisible`.** RECARREGAR
(login) e ATUALIZAR (painel) "recarregavam" navegando para a tela em que já
estavam — a tela nunca fica invisível, o `OnVisible` não dispara, e o usuário
vê dado velho com cara de recarregado. Correção: o botão duplica o bloco do
`OnVisible` (comentário `// espelho do OnVisible` marca o par a manter em
sincronia). Navegar para si mesmo só sobrou no item de menu da tela ativa,
onde é inofensivo por definição.

**3. Dropdown moderno não limpa por variável já igual ao padrão.**
`DefaultSelectedItems: =[Coalesce(varX, "Todos")]` só re-aplica quando a
variável **muda**; se ela já era "Todos" e o usuário mexeu no dropdown, LIMPAR
que faz `Set(varX, "Todos")` não altera nada e a seleção fica. Saída adotada:
`Items: =Filter(colX, locNonce >= 0)` — incrementar `locNonce` recria a tabela
de Items, e troca de Items reseta a seleção para o default. O filtro do
`Filter` é sempre-verdadeiro; ele existe só para criar a dependência.

Também desta auditoria: número não é booleano em Power Fx —
`If(varUsuario.pode_baixar_ativo, ...)` com coluna Número reprova; sempre
`= 1`. E fundo suave de aviso (`#FEF2F2`, `#FFFBEB`) agora é token
(`hxVermelhoSuave`, `hxAmbarSuave`); a regra 16 reprova qualquer hex literal
em tela.

## `FillPortions` ausente é 1, não 0 — a regra estava invertida (2026-08-26)

O export do Studio do app de Frotas voltou **sem** os `FillPortions: =1` que o
gerador escrevia: o Studio omite a propriedade quando ela vale o padrão. A
regra 13 tratava "ausente" como 0 e passou a reprovar 40 containers saudáveis.

Correção: só reprova quando `FillPortions` for **explicitamente `=0`** e não
houver `Height` (pai vertical) ou `Width` (pai horizontal). Foi exatamente esse
o caso do formulário em branco — a grade tinha `=0` escrito.

Regra geral para validador de export: **ausência de propriedade significa
valor padrão**, não zero. Antes de reprovar por ausência, confirme qual é o
padrão — o Studio grava só o que difere dele.

## Round-trip como fonte de prova de esquema (2026-08-26)

O usuário editou no Studio e reexportou: apareceram `Icon: ="ArrowExit"`,
`PaddingTop` em `Button@0.0.45` e `FillPortions` em `DatePicker@0.0.46` e
`DropDown@0.0.45` — nada disso existia no export antigo que serve de catálogo.

Não são palpites: o Studio **gravou e devolveu**, que é o critério de prova
adotado neste repositório. Foram para uma allowlist nomeada no
`validar_telas.py`, com data e origem no comentário. Catálogo velho não
invalida propriedade nova — mas só entra o que passou por um round-trip real.

## Divisão por branco = divisão por zero (2026-08-26)

`ThisItem.Qtd / locMaxAero` numa galeria disparou "Operação inválida: divisão
por zero" no painel. `locMaxAero` vem de `UpdateContext` no fim do `OnVisible`,
e a galeria **renderiza antes** — com a variável ainda em branco. Em Power Fx
branco no denominador é zero.

Regra: variável de contexto usada como denominador dentro de galeria ou de
propriedade que renderiza cedo precisa de guarda **no ponto de uso**
(`Max(varX, 1)`), não só no ponto de atribuição. O mesmo vale para `Sqrt`,
`Mod` e índices.

## Não calcule sobre coluna que nenhum módulo preenche (2026-08-26)

O painel de Frotas mostrava "Lado ar não conforme: 1" com **um** ativo
cadastrado. A conta era `circula_lado_ar = 1 And conforme_lado_ar <> 1`, e
`conforme_lado_ar` é preenchido pelo módulo 18, que não existe. Toda a frota
caía na contagem, e o número tinha cara de irregularidade regulatória.

Regra: **coluna sem módulo dono é ausência de dado, não valor `0`.** Enquanto
o módulo não entra, o campo fica fora da projeção do cache, fora dos KPIs e
fora da ficha. O que sobra é o que o módulo atual preenche — em Frotas virou
integridade de cadastro (sem código FRT, sem leitura de medidor, sem placa
onde o tipo exige, sem gestor).

Guardas adicionadas em `Frotas/validar_telas.py`:
- **17** — reprova qualquer uso de campo-espelho de módulo futuro nas telas.
- **18** — as N projeções que alimentam a mesma coleção têm que ter esquema
  **idêntico**; `Collect` numa coleção com outro esquema falha em runtime, e
  o defeito só aparece no segundo ponto de carga (o botão de atualizar, não a
  abertura do app).

Ganho colateral: a projeção caiu de 32 para 27 colunas por linha em 5 pontos
de carga.

## Bloco replicado: o molde é a tela, não o gerador (2026-08-26)

O trilho de navegação era composto por `aplicar_menu.py` e replicado nas três
telas. O usuário refinou o visual **no Studio** (fonte 14 nos itens,
`PaddingLeft: =18`, gap 10, marca colapsada "GF" alinhada à esquerda, ícone
`ArrowExit`, remoção do bloco de próximos módulos) e reexportou. Na rodada
seguinte o formulário foi regerado — e voltou com a versão do gerador. Duas
telas com o trilho ajustado, uma com o antigo.

Correção estrutural: `Frotas/sincronizar_menu.py` passou a **copiar o bloco da
`scrFrotaPainel`** para as outras telas, trocando só o sufixo dos nomes de
controle e o item aceso. O gerador não recompõe mais o trilho; ele existe só
para o primeiro embrulho (shell) de uma tela nova.

Regra: quando um bloco visual é replicado em N telas e o usuário edita no
Studio, **uma das telas vira o molde** e as outras são cópias dela. Gerador que
recompõe do zero desfaz refinamento manual sem avisar — e o diff só aparece
comparando tela contra tela.

Guarda: regra 19 do `validar_telas.py` compara o trilho das três telas
propriedade por propriedade (ignorando `Appearance`/`BasePaletteColor` dos
itens de navegação, que mudam de propósito no item aceso) e reprova qualquer
divergência.

## Vírgula faltando entre argumentos: o erro se reporta na função de fora (2026-08-26)

Sintoma no Studio: `Sort(` marcado com **"Número inválido de argumentos: 10
recebidos, 2-3 esperados"**. A fórmula era

```
Sort(
    Filter(colFrota, c1, c2, ..., c9)     ← faltava a vírgula aqui
    Switch(...)
)
```

Sem a vírgula, o parser não vê `Filter(...)` como **um** argumento: ele recupera
achatando a lista de argumentos do `Filter` dentro do `Sort`. Daí "10 recebidos"
— exatamente `colFrota` + as 9 condições. **O erro aponta a função de fora; o
defeito está na de dentro.**

Origem: gerador que montava o bloco do `Filter` por função e esquecia a vírgula
ao concatenar com o argumento seguinte. A checagem de parênteses **não pega**,
porque abrem e fecham na conta certa.

Guarda (regra 20 do `validar_telas.py`): depois de remover os literais de texto,
procurar `\)\s+Nome\(` em toda propriedade. Em Power Fx, `)` só pode ser seguido
de vírgula, ponto e vírgula, operador ou outro `)`. A allowlist de operadores é
`And`, `Or`, `Not`, `in`, `exactin`, `As`. Testada reintroduzindo o defeito: a
regra acusa e nomeia o controle e a propriedade.

Duas correções de robustez no mesmo lugar:
- `Filter(t, c1, ..., c9)` virou `Filter(t, (c1) And (c2) And ...)` — **dois**
  argumentos. Com um argumento só não há como achatar lista nenhuma.
- `Sort(t, chave, If(cond, SortOrder.Descending, SortOrder.Ascending))` virou
  `Sort(t, chave)` com a chave do medidor invertida por complemento
  (`Text(9999999 - valor, "0000000")`). Enum dinâmico no 3º argumento é aposta;
  ordenação decrescente por chave complementar é aritmética.

## `ID` dentro de galeria: escopo ambíguo pede `As` (2026-08-26)

`LookUp('tb_ativosFrota', ID = ThisItem.ID)` dentro do template de uma galeria
deu **"O nome não é válido. 'ID' não é reconhecido"**. Fora da galeria a mesma
fórmula compila.

Causa: dois escopos de linha aninhados — o da galeria (`ThisItem`) e o do
`LookUp`. O `ID` solto fica ambíguo e o resolvedor desiste.

Correção: `LookUp('tb_ativosFrota' As _reg, _reg.ID = ThisItem.ID)`. É o item 13
do checklist ("em `ForAll`/`LookUp` aninhados, exigir `As <alias>`") — que vale
também quando o aninhamento é **implícito**, dado pelo template da galeria.

## Auditoria Service Desk 2026-08-27: dois defeitos que só aparecem cruzando escrita com leitura de variável

- Projeto/tela: Gestão de Chamados / `ScreenServiceDeskForm`.

### Variável de proteção que nunca é ligada

`varDeskRegistroCriado` e `varDeskErroFluxo` governavam quatro coisas visíveis: o
aviso laranja `cntDeskWarning`, o texto do botão ("Cancelar" → "Voltar"), o
rodapé e o `DisplayMode` do "Confirmar". As duas apareciam em cinco lugares — e
em **todos os cinco sendo setadas como `false`**. Nenhum ponto do arquivo as
ligava. O mecanismo inteiro de proteção contra reenvio era código morto que
parecia implementado na revisão visual.

**Verificação:** para cada variável de estado, contar separadamente as escritas
que **ligam** (`: true`, `: Now()`) e as que **desligam** (`: false`, `: Blank()`).
Zero do lado que liga = mecanismo morto. Zero do lado que desliga = estado preso.
É uma regra que roda sozinha sobre o YAML, sem abrir o Studio:

```python
liga    = len(re.findall(v + r'\s*:\s*(true|Now\(\))', blob))
desliga = len(re.findall(v + r'\s*:\s*(false|Blank\(\))', blob))
```

### `OnSuccess` que liga estado de UI e chama conector precisa de `IfError` — e a ordem importa

O `OnSuccess` ligava `varDeskProcessando` (que controla o overlay
`cntDeskLoading`) antes de chamar `Office365Outlook.SendEmailV2`, e só desligava
**depois** do e-mail. Sem `IfError` — o arquivo inteiro tinha zero ocorrências.
Falha no conector aborta a fórmula: o registro já está gravado no SharePoint, o
`UpdateContext({varDeskProcessando: false})` final nunca roda e o usuário fica com
a tela coberta pelo spinner **para sempre**.

Isto é a lição "Todo overlay de carregamento precisa de um caminho de saída"
(2026-08-24) vista de outro ângulo: lá o buraco era um ramo de saída antecipada;
aqui é uma exceção de conector. A regra que cobre os dois casos:

**Em `OnSuccess`/`OnFailure` que ligam estado de UI, o desligamento vem ANTES do
primeiro efeito colateral, e todo efeito colateral vive dentro de `IfError`.** O
`IfError` não precisa unificar tipos entre o valor e o fallback — o próprio
exemplo da Microsoft mistura `Patch()` com `Notify()`.

Corolário do mesmo `OnSuccess`: `Patch(User, LookUp(User, ...), {...})` sem
verificar o `LookUp` gravava sobre registro em branco e o e-mail seguia enviando
uma senha temporária **que não foi aplicada**. O remédio é
`With({locUsr: LookUp(...)}, If(IsBlank(locUsr), Error({Kind: ErrorKind.NotFound, ...}), Patch(...)))`
— o `Error()` sobe para o `IfError` de fora e vira aviso na tela.

### Ordinal `Y` repetido entre DataCards

`desk_categoria` e `desk_id` ambos `Y: =0`; `desk_descricao` e `desk_status`
ambos `Y: =2`. Em `Form` com `Layout: Vertical` o `Y` do DataCard é o índice de
ordenação, não uma coordenada: repetido, a ordem fica indeterminada.

**Verificação:** os `Y` dos `TypedDataCard` de um mesmo form têm que formar uma
sequência de valores únicos. Cards ocultos (`Height: =0` + `Visible: =false`)
podem ser empurrados para o fim sem impacto visual — é a exceção que a trava de
layout aceita, desde que declarada nominalmente.

### Numeração calculada no app: o guard `IsBlank` é o bug

`If(IsBlank(varNumChamado), Set(varNumChamado, <último + 1>))` num `OnVisible`
com variável **global** só calcula uma vez por sessão do app. Segundo chamado sem
recarregar = `desk_id` duplicado. Recalcular sempre no `OnVisible` **e** revalidar
no clique antes do `SubmitForm`; e o card oculto lê a variável direto
(`Update: =varNumChamado`) em vez de depender da propagação de `Default` para um
`TextInput` invisível.

Continua sendo paliativo: dois usuários simultâneos ainda colidem. A saída
definitiva é usar a coluna `ID` nativa do SharePoint como protocolo.

### Corolário: `Coalesce` depois da aritmética nunca dispara

Escrevendo a própria correção desta auditoria eu caí na armadilha irmã da lição
"Divisão por branco = divisão por zero": guardei `Find` com
`Coalesce(Find("@", email) - 1, Len(email))`. Não funciona. `Find` devolve
branco quando não acha, mas **branco em aritmética vira zero**, então
`branco - 1` é `-1` — um valor perfeitamente não-branco. O `Coalesce` nunca
dispara e `Left(texto, -1)` estoura.

Regra: o `Coalesce` (ou `IsBlank`) tem que envolver a **função que pode devolver
branco**, nunca a expressão que já fez conta com ela.

```powerfx
// errado — o Coalesce nunca vê branco
Left(email, Coalesce(Find("@", email) - 1, Len(email)))

// certo — guarda o Find, depois faz a conta
Left(email, Coalesce(Find("@", email), Len(email) + 1) - 1)
```

Vale para todo par guarda/operador: `Coalesce(x, d) + 1`, `Max(Coalesce(x, 1), 1)`,
`If(IsBlank(f(x)), ...)`. Se a conta vem antes da guarda, a guarda é decorativa.

## `Blank() = 0` é verdadeiro — e isso virou desvio de autenticação (2026-08-27)

- Projeto/tela: AirPort Now / `Login`, encontrado ao levantar o contrato do
  usuário logado para o módulo de Gestão de Chamados.

A tela valida assim:

```powerfx
Set(userRecord; LookUp(Sort(User; ID; SortOrder.Descending); Usuarios = txtUser_2.Value));;
If(IsBlank(userRecord);
    Notify("Usuário não encontrado"; NotificationType.Error);
    If(LookUp(User; Usuarios = txtUser_2.Value And Senha = txtSenha_2.Value).Validacao = 0;
        UpdateContext({varUpdSenha: true});;   // abre o pop-up de cadastrar nova senha
        ...
```

`userRecord` é achado **só pelo nome de usuário**. O segundo `LookUp` filtra por
usuário **e senha** — com a senha errada ele devolve **branco**, e `.Validacao`
vem branco. Em Power Fx **`Blank() = 0` é verdadeiro**. Logo a condição
`... .Validacao = 0` é verdadeira para *toda* senha errada de *qualquer* usuário
existente, e o pop-up de cadastrar nova senha abre.

O pop-up grava assim:

```powerfx
Patch(User; First(Filter(User; Usuarios = txtUser_2.Value)); {Senha: <nova>; Validacao: 1})
```

Sem nenhuma verificação da senha anterior. Resultado: **quem souber um nome de
usuário troca a senha dele e entra na conta.**

É a mesma coerção da lição "Divisão por branco = divisão por zero", só que num
lugar onde o efeito não é um erro visível — é uma porta aberta.

**Regra:** comparação com `0`, `""` ou `false` sobre o resultado de um `LookUp`
que pode não achar nada exige `IsBlank` **antes**, nunca depois:

```powerfx
// errado — senha errada cai no ramo do "= 0"
If(LookUp(User; Usuarios = u And Senha = s).Validacao = 0; <trocar senha>; <erro>)

// certo — separa "não achou" de "achou com Validacao = 0"
With({locAuth: LookUp(User; Usuarios = u And Senha = s)};
    If(IsBlank(locAuth); Notify("Usuário ou senha inválidos"; NotificationType.Error);
       locAuth.Validacao = 0; <trocar senha>;
       <seguir para o app>)
)
```

Corolário de arquitetura: **a ação que troca a senha tem que reusar o registro
já autenticado** (`locAuth`/`userRecord` validado), nunca refazer o `Filter` só
pelo nome de usuário. Toda escrita sensível ancora no registro que passou pela
verificação, não numa nova busca pela chave pública.

**Verificação para as próximas telas:** procurar todo `LookUp(...).<coluna> =`
comparado com `0`/`""`/`false` e exigir que exista um `IsBlank` do próprio
`LookUp` no caminho. E procurar todo `Patch` de coluna sensível cujo segundo
argumento seja um `LookUp`/`First(Filter(...))` refeito em vez do registro
autenticado.

## Galeria que consulta a própria seleção não renderiza nada (2026-08-27)

- Projeto/tela: Gestão de Chamados / `frmCadUser`, galeria `galUser`.
- Sintoma: a galeria carregava (o contador dizia "613 de 613"), a barra de
  rolagem existia, mas **as linhas vinham em branco** — só apareciam os ícones
  filhos, empilhados no vazio. Nenhum erro no Studio.

A causa estava no template:

```powerfx
// dentro de htmCadLinha, filho de galUser
If(galUser.Selected.ID = ThisItem.ID; "#6046ED"; "#FFFFFF")
```

`galUser.Selected` depende de qual linha está selecionada; a linha depende do que
o template renderiza. É **dependência circular**, e o Power Apps resolve isso
devolvendo branco em silêncio em vez de acusar erro.

**Regra:** nenhuma propriedade dentro do template de uma galeria pode ler
`<galeria>.Selected`. O estado de seleção sai por variável, setada no `OnSelect`
do próprio template:

```powerfx
// no OnSelect do item
Select(Parent);;
UpdateContext({varSelId: ThisItem.ID})

// no HtmlText / Fill / BorderColor do item
If(varSelId = ThisItem.ID; hxPrimaria; hxSuperficie)
```

É o mesmo motivo pelo qual `Frotas/scrFrotaLista` usa `varAtivoSel.ID` e não
`galFrota.Selected.ID`. Fora do template, `galUser.Selected` continua válido e é
o certo — o problema é só a auto-referência.

**Verificação automática:** para cada `Gallery`, varrer as propriedades dos
filhos procurando o nome da própria galeria. Qualquer ocorrência é bug.

## Dicionário de propriedades: a única defesa real contra PA2108 (2026-08-27)

Escrevendo `frmCadUser` eu inventei `Value` em `Classic/DropDown@2.3.1` — o
Studio recusou com `PA2108 : Unknown property 'Value'`. A forma correta,
`Items.Value: =Aeroporto`, estava **no próprio export original da tela**.

O item 20 do checklist ("propriedade comprovada em posição alfabética num export
do Studio") só funciona se existir o dicionário. Montando um a partir de todos os
`*.yaml` do repositório (41 tipos de controle) e conferindo o arquivo novo contra
ele, apareceram **mais três** propriedades inventadas que ainda não tinham dado
erro só porque o Studio para no primeiro:

- `HoverBorderColor` em `Classic/DropDown@2.3.1` — não existe (é `HoverFill`).
- `Tooltip` em `Classic/DropDown@2.3.1` — não existe.
- `OnChange` em `Classic/TextInput@2.3.2` — não aparece em nenhum export; foi
  substituído por um botão "Buscar" com `OnSelect`, que além de comprovado
  trocou N chamadas ao conector por uma explícita.

**Procedimento antes de colar qualquer tela:**

1. Construir o dicionário `{Control: {propriedades}}` a partir dos exports reais
   já existentes no repositório.
2. Conferir cada propriedade do arquivo novo contra o dicionário do **mesmo
   `Control@versão`**.
3. Tratar ausência como suspeita, não como permissão: ou se acha o nome certo num
   export, ou se troca a abordagem por uma comprovada.
4. Ordenar as propriedades alfabeticamente, que é como o Studio exporta.

Ausência no dicionário não prova que a propriedade é inválida — prova que ela
**não foi vista funcionando**, e num arquivo colado à mão isso já basta para não
arriscar.

## Filtro opcional de aeroporto é um vazamento de acesso, não um filtro (2026-08-31)

- Projeto: SAFETY / AirportNow Safety & Fauna. 11 galerias, 4 telas diferentes.

Padrão encontrado em **todas** as galerias do app:

```powerfx
Filter(
    tbl,
    IsBlank(cmbAeroporto.Selected.Aeroporto) ||
    <mod>_aeroporto = cmbAeroporto.Selected.Aeroporto,
    ...
)
```

O `OnVisible` da tela restringia uma coleção por perfil
(`ClearCollect(col_x, Filter(tbl, aeroporto = varAeroUser))`), mas **a galeria
consultava a lista direto** e ignorava essa coleção — que, aliás, ninguém lia.
Com o combo em branco a primeira condição é sempre verdadeira: o perfil "Base"
via os 16 aeroportos, bastando não escolher nada no filtro.

**A regra que fica:** controle de acesso nunca pode depender do estado de um
controle de tela. O escopo tem que vir de variável definida no `OnStart`
(`varEscopoAero`, `varEscopoBloco`) e entrar na consulta **antes** do filtro
escolhido pelo usuário. Coleção de segurança que nenhuma galeria lê é pior que
inútil: dá a impressão de que a restrição existe.

Variante do mesmo bug com outra cara: `StartsWith(Aeroporto, Text(cmb.Selected.Value))`.
Com o combo vazio, `StartsWith(x, "")` é verdadeiro para toda linha.

## `IsBlank(x) || col = x` derruba a delegação inteira (2026-08-31)

O mesmo filtro opcional acima não é delegável no conector do SharePoint —
`IsBlank()` não delega. Resultado: a galeria parava silenciosamente nas
primeiras 500/2000 linhas e a lista ficava **incompleta sem nenhum aviso**.

Forma delegável para "filtro opcional": não usar `||` dentro do `Filter`, e sim
escolher a consulta com `Switch` — cada ramo é um `Filter` delegável:

```powerfx
With(
    {_aero: ..., _bloco: ..., _ini: ..., _fim: ...},
    Filter(
        Switch(
            true,
            !IsBlank(_aero),  Filter(tbl, col_aeroporto = _aero, col_data >= _ini, col_data < _fim),
            !IsBlank(_bloco), Filter(tbl, col_bloco    = _bloco, col_data >= _ini, col_data < _fim),
                              Filter(tbl,                        col_data >= _ini, col_data < _fim)
        ),
        <filtros baratos, já sobre o conjunto recortado>
    )
)
```

O intervalo de datas passa a ser **obrigatório** (com piso vindo de named
formula), que é o que garante um recorte delegável mesmo sem aeroporto.

## ID calculado no app: `max + 1` gera protocolo duplicado (2026-08-31)

```powerfx
var_jetBlastId: Value(First(SortByColumns(Filter(tbl, jetBlast_id > 0), "ID", Desc)).jetBlast_id + 1)
```

Dois usuários salvando ao mesmo tempo leem o mesmo máximo. Os dois gravam o
mesmo `<mod>_id`, e os filhos (imagens, envolvidos) de um vão parar na ocorrência
do outro. Além disso é uma consulta não delegável a cada gravação.

Correção sem mexer no esquema da lista: gravar primeiro, ler o `ID` real que o
`Patch` devolve e carimbá-lo de volta na coluna de negócio.

```powerfx
UpdateContext({var_regNovo: Patch(tbl, Defaults(tbl), { ...sem <mod>_id... })});
UpdateContext({var_id: Coalesce(var_regNovo.ID, 0)});
If(
    var_id <= 0,
    Notify("Não foi possível gravar...", NotificationType.Error);
    UpdateContext({var_visibleSpiner: false, var_salvando: false}),
    Patch(tbl, var_regNovo, {<mod>_id: var_id})
);
If(var_id > 0, ForAll(colFilhos, Patch(...)))
```

**Corolário que passou despercebido por anos:** enquanto `<mod>_id` (max+1) e
`ID` (SharePoint) divergem, qualquer tela que grave o filho por um e apague pelo
outro está quebrada. Era o caso do `ScreenExcluir`: gravava filho com `<mod>_id`
e apagava com `var_item.ID`. Os dois números só coincidem antes da primeira
exclusão na lista pai.

## Falha de gravação não pode limpar o formulário (2026-08-31)

O `Patch` do pai não era checado: em qualquer falha, os `ForAll` dos filhos
rodavam mesmo assim (órfãos), o `Select(ButtonReset...)` limpava tudo o que o
usuário digitou e o app navegava para "Operação realizada com sucesso".

Reset e tela de sucesso são ramo do `If` de gravação confirmada, nunca instrução
solta depois dele.

## Prefixo de coluna colado de outro módulo: erro que o Studio não acusa (2026-08-31)

Encontrados por varredura `ThisItem\.([A-Za-z]+)_([A-Za-z]+)` cruzada com o
prefixo esperado da tela:

- `ScreenExcursaoPista` lia `ThisItem.derFlu_aeroporto`, `derFlu_data`, `derFlu_hora`.
- `ScreenJetBlast` lia `ThisItem.derFlu_aeroporto` no protocolo.
- `ScreenExcluir`, ramo de Colisão, apagava filhos por `var_item.derFlu_id`.

Coluna inexistente devolve **branco**, não erro. O rótulo fica vazio e o
`RemoveIf` nunca casa — bug silencioso em produção.

**Validação preventiva:** para cada tela de módulo, listar todo
`ThisItem.<prefixo>_<campo>` e reprovar prefixo que não seja o do módulo.

## Tela que lista de uma lista e grava em outra (2026-08-31)

`ScreenVistoriaSafetyFauna`: galeria em `'1 - CSO'`, formulário em
`tbl_vistoriaSafetyFauna`. Nada do que se grava aparece na listagem, e nenhum
erro é levantado.

**Validação preventiva:** conferir `Gallery.Items` × `Form.DataSource` da mesma
tela. Divergência só é legítima em tela de consulta cruzada declarada.

O esquema real das listas está dentro do próprio `.msapp`, em
`References/DataSources.json` (`schema.items.properties`) — dá para conferir
nome e caixa de cada coluna sem abrir o SharePoint. Foi assim que apareceu que
`'1 - CSO'` não tem coluna `Aeroporto` nem `'Data/Hora'`, embora as fórmulas da
tela usem as duas.

## Locale: passar a conversão para o usuário conta como erro de entrega (2026-08-31)

Segunda ocorrência do mesmo problema (a primeira foi em 2026-08-13, PLEM/PRAI).
Desta vez o `App.OnStart` do AirportNow Safety saiu **só** como `.pa.yaml`
invariante, com um comentário de cabeçalho dizendo *"OU copiar para a barra de
fórmulas (neste caso converta para pt-BR)"*. O usuário colou na barra de
fórmulas e tomou erro de sintaxe em cima do primeiro `Set(`.

**A regra não é "usar pt-BR". É: o destino decide o formato.**

| Destino | Formato | Separadores |
|---|---|---|
| Barra de fórmulas (`App.OnStart`, `App.Formulas`, fórmula avulsa) | pt-BR | `;` args · `;;` encadeia · `,` decimal |
| Exibição de código (`.pa.yaml`) | invariante | `,` args · `;` encadeia · `.` decimal |

O Studio em pt-BR **lê e grava `.pa.yaml` em invariante**. Converter o YAML para
`;`/`;;` quebra o arquivo. As duas metades da regra são igualmente obrigatórias e
é fácil acertar uma e errar a outra — foi o que aconteceu aqui.

**O que passou a ser obrigatório:**

1. `App.OnStart` e `App.Formulas` saem como `.txt` em pt-BR, prontos para colar.
   A versão `.pa.yaml` é complemento, nunca substituta.
2. Todo `.pa.yaml` entregue leva no cabeçalho o aviso de que está em invariante e
   de que **não** deve ser convertido.
3. A conversão é feita por script (`SAFETY/build/ptbr.py`), nunca à mão.

**Conversão correta preserva string e comentário.** `Notify("a, b; c", ...)` e
`// vírgula em prosa` não podem ser tocados — a varredura tem que ser lexical
(rastreando aspas, `//` e `/* */`), não regex de linha. Decimal só muda entre
dígitos: `(?<=\d)\.(?=\d)`, senão `usuario.usrNome` e `DisplayMode.Edit` viram lixo.

**Como provar que a conversão está certa.** Não dá para validar `;` por varredura:
em pt-BR, `;` simples é separador de argumento legítimo e `;;` é encadeador — um
checker que reprova "`;` sozinho" acusa o arquivo inteiro (foi o primeiro checker
que escrevi, e ele reprovou 244 linhas corretas). A prova real é **ida e volta**:

```python
para_invariante(para_ptbr(origem)) == origem   # caractere a caractere
```

Se o conversor perder ou inventar um separador, a volta diverge. Só a **vírgula**
é verificável por varredura direta: fora de string, comentário e decimal, ela não
existe em pt-BR.

## Duas grades que se olham têm que usar o mesmo mecanismo de desenho (2026-09-01)

O Mapa de Alocação tem uma régua de horas no topo e 25 linhas de grade embaixo,
cada uma num `HtmlViewer` diferente. A régua traçava a divisão de hora com
`border-left: 1px` nas células da tabela; as linhas traçavam com
`background-image: repeating-linear-gradient`. **Em 100 %, numa tela comum, os
dois caem exatamente no mesmo pixel** — e o desenho passa como resolvido.

Em zoom de 110 %/125 %, ou em tela HiDPI, não caem: borda de célula o navegador
**encaixa em pixel inteiro** (a coluna da tabela e a caixa da borda são
arredondadas no layout), gradiente ele **rasteriza em espaço contínuo**, a partir
do período em float. Medido em Chromium sobre a página renderizada, o erro foi a
até **1,25 px**, variando coluna a coluna — que é justamente o que o olho lê como
"quase alinhado", pior do que um erro constante.

A correção não é ajustar número: é **um mecanismo só**. O mesmo gradiente na
célula da régua e na célula de cada linha, com a declaração vindo de uma única
named formula (`mapFundoHoras`), e a porcentagem da coluna de hora saindo da
mesma constante que o período do gradiente (`mapPctHora`). Erro medido depois:
**0,03 px** em todas as combinações de zoom (100/110/125 %) e DPI (1×, 2×).

Duas regras que valem para qualquer grade montada em HTML no Power Apps:

1. **Elementos que precisam se alinhar entre controles não podem depender de
   duas contas diferentes.** Nem duas contas de CSS, nem uma conta de CSS contra
   uma de Power Fx (`X`/`Width`/padding). Se a geometria pode ser expressa uma vez
   no HTML e herdada pelos dois, é assim que ela tem que ser expressa.
2. **Testar em 100 %/1× não prova alinhamento.** É a condição em que os
   arredondamentos empatam. O teste tem que varrer zoom e DPI — e a medição é em
   pixel renderizado (screenshot + varredura de coluna), não em `getBoundingClientRect`,
   que devolve a caixa de layout e não onde a tinta caiu.

## Texto do usuário dentro de atributo HTML: uma aspa desmonta a linha inteira (2026-09-01)

Mapa de Alocação, `scrMapaPatio`. A grade é montada como string HTML e jogada
num `HtmlViewer`. Até aqui, tudo que entrava na string vinha de enumeração:
sigla de companhia escolhida em dropdown, número de portão, número de voo. Ao
acrescentar a dica de mouse (`title='…'`), entrou pela primeira vez **campo
de texto livre** — `observacao` e `prefixo`, digitados pelo operador.

O atributo é delimitado por aspa simples (é a convenção do arquivo, porque a
aspa dupla é o delimitador de string do Power Fx). Uma observação como
`manutenção d'asa` fecha o atributo no meio, e o resto do texto vira atributo
solto: o navegador descarta a célula, o `table-layout:fixed` redistribui a
linha e **a linha inteira da grade sai errada**. Sem erro no Studio, sem erro
no console — só o desenho errado, e só para o registro que tem a aspa.

**A correção é escapar, e a ordem do escape é parte da correção:**

```
&  ->  &amp;     PRIMEIRO, sempre
<  ->  &lt;
>  ->  &gt;
'  ->  &#39;
Char(10) -> &#10;   POR ÚLTIMO, sempre
```

Escapar `&` depois de `<` transforma o `&lt;` recém-criado em `&amp;lt;` e o
usuário lê `&lt;` na tela. Converter `Char(10)` antes de escapar `&`
transforma o `&#10;` em `&amp;#10;` e a quebra de linha vira texto. As duas
inversões produzem lixo visível, não erro — que é o que faz elas passarem em
revisão.

**Onde escapar:** na projeção da coleção, não na montagem do HTML. Uma vez por
registro no carregamento em vez de uma vez por render, e um ponto só para
auditar em vez de um por campo.

**Validação preventiva:** teste dirigido com `'`, `&`, `<` e quebra de linha na
observação, conferindo que a linha continua inteira. Vale para qualquer tela do
workspace que monte HTML com campo de texto livre — hoje `DueDiligence` e
`Mapa de Alocação`.

## Coluna obrigatória nova num filtro de faixa: o registro some sem erro (2026-09-01)

Mapa de Alocação. A grade passou a aceitar registro que cruza dias, e o filtro
do dia mudou de

```
data_operacao = varData
```

para

```
data_operacao <= varData And data_fim >= varData
```

`data_fim` é coluna nova. Numa lista que já tem dados, ela nasce **nula** em
todos os registros existentes — e `NULL >= data` não casa. Resultado: a grade
abre **vazia**, com zero registro, sem nenhum erro na tela, no Studio ou no
Monitor. É o mesmo mecanismo do Sim/Não que já está registrado neste documento
(`NULL` não casa com `eq false`), só que agora numa coluna de data e num filtro
de faixa.

**A ordem de implantação é a correção:**

1. Criar a coluna **opcional**.
2. Preencher em 100% dos itens — inclusive os inativos, que o expurgo lê.
3. Conferir zero itens em branco.
4. **Só então** marcar obrigatória, indexar e publicar a tela que usa o filtro novo.

Publicar a tela antes do passo 3 é apagar a grade de todo mundo até alguém
perceber.

**Dois efeitos colaterais na mesma mudança, ambos silenciosos:**

- **A validação de lista do SharePoint rejeitava todo pernoite.** Era
  `=[hora_fim]>[hora_inicio]`. Um voo que chega 22:00 e sai 06:10 do dia
  seguinte grava `1320` e `370` — fim menor que início. A gravação é barrada
  pelo SharePoint, e o app só consegue reportar "não foi possível gravar",
  porque `IsError(Patch(...))` não devolve a mensagem da validação de coluna.
  Correção: `=OU([data_fim]>[data_operacao];[hora_fim]>[hora_inicio])`.
- **O expurgo agendado apagaria interdição em vigor.** O fluxo filtrava por
  `data_operacao lt hoje-30`. Uma interdição lançada há 40 dias que termina
  amanhã casa com esse filtro. O fluxo roda verde, e o bloco some da grade.
  Correção: filtrar por `data_fim`.

**A regra geral:** quando uma coluna passa a participar do filtro que decide o
que aparece na tela, ela vira dependência de **tudo** que lê ou apaga a lista —
validação de coluna, validação de lista, views, fluxo agendado. Trocar o filtro
sem varrer esses quatro é deixar bug silencioso plantado.

## Coleção recortada para exibição não pode alimentar o formulário (2026-09-01)

Ainda no Mapa de Alocação. `colDia` passou a trazer duas versões do horário: a
**real** (`h_ini`/`h_fim`, com as datas) e a **recortada ao dia desenhado**
(`ini`/`fim`, que é `0` quando o registro começou ontem e `1440` quando termina
amanhã). A recortada existe porque a grade é uma régua de 24 h e o bloco tem
que caber nela.

O painel de edição lia `ThisItem.ini`/`ThisItem.fim` — que antes eram a mesma
coisa que o valor real. Depois do recorte, abrir um pernoite **pelo dia**
**seguinte** carregaria `00:00` no formulário, e salvar gravaria `00:00`:
**a edição destrói o registro**, e o operador não tem como perceber, porque
`00:00` é exatamente o que o bloco daquele dia mostra.

**A regra:** valor derivado para desenho e valor de origem para edição são
colunas diferentes, com nomes diferentes, na mesma coleção. Quando uma coleção
ganha uma projeção "para exibir", varrer **todo** consumidor dela e decidir, um
por um, qual das duas ele quer — o compilador não ajuda, porque os dois campos
existem e os dois são números.

## "Esperando: Number, Date, Time, DateTime" não é só do `Text()` — comparação também (2026-09-02)

Mapa de Alocação. A tela nova não compilava: *"Tipo de argumento inválido.
Esperando um dos seguintes: Number, Date, Time, DateTime, Dynamic"*, dentro do
`ClearCollect(colDia; ...)` do `btnAtualizarMap.OnSelect` — uma expressão de
~60 linhas com `Text()`, `DateDiff()`, `Int()`, `Mod()`, `Hour()` e comparações.

Eu deduzi que aquela lista de tipos era a assinatura do `Text(valor; formato)` e
apontei para o `Text(_r.data_fim; "dd/mm/yyyy")`, por ser o token novo da entrega.
**Estava errado.** O culpado era

```
If(_r.envergadura_m > 0; ...)
```

e a correção foi `If(Value(Text(_r.envergadura_m)) > 0; ...)`.

**A lição de diagnóstico:** essa mesma lista de tipos é emitida por *dois*
lugares diferentes — o primeiro argumento do `Text(valor; formato)` **e os
operadores de comparação** (`>` `<` `>=` `<=`). Deduzir a função a partir da
lista de tipos estreita menos do que parece: num bloco grande, todo `>` contra
literal numérico é suspeito no mesmo nível que todo `Text()`.

**A lição de código:** `envergadura_m` é `Number` no esquema do SharePoint
(`Decimals=2`, `Required=FALSE`), e ainda assim a comparação direta não passou.
A própria tela já tinha o precedente três telas abaixo — `If(Value(ThisItem.env) > 0; ...)`
no painel de edição — escrito na mesma entrega, por ter batido no mesmo
problema. **Precedente de coerção dentro do próprio arquivo é sinal, não
coincidência:** quando uma coluna já aparece envolvida em `Value()` num ponto,
todo novo consumidor dela precisa da mesma coerção, e vale varrer o arquivo
por outros usos crus da mesma coluna antes de colar no Studio.

## O `HtmlViewer` preserva o atributo `title`: dica de mouse é viável (2026-09-02)

Confirmado no app, no Mapa de Alocação: o sanitizador do `HtmlViewer` **não**
remove o atributo `title` do `<td>`, e o navegador desenha o balão normalmente.
Até 01/09/2026 não havia precedente disso em nenhum módulo do repositório, e a
funcionalidade inteira dependia de uma premissa que só o Studio responderia.

**Por que isso destrava mais do que uma tela:** o `HtmlViewer` não devolve evento
por elemento — nem clique nem `hover` —, então o Power Fx nunca sabe sobre qual
pedaço do HTML está o ponteiro. Balão em CSS (`:hover` + filho absoluto) também
não resolve quando o controle é baixo, porque o balão é **recortado na borda do
controle**. O `title` nativo é desenhado pelo navegador **fora** da caixa da
página e escapa do recorte. É a única forma de detalhar um elemento de HTML
gerado sem abrir painel — vale para qualquer grade, timeline ou cartão montado
em `HtmlViewer`, não só para este módulo.

**O preço:** todo campo livre do usuário passa a viver dentro de um atributo
HTML, e uma aspa simples fecha o atributo e desmonta a linha inteira. A ordem de
escape (`&` primeiro, depois `<`, `>`, `'`, e `Char(10)` → `&#10;` por último) é
obrigatória — ver a lição de 01/09/2026 sobre texto do usuário dentro de atributo
HTML.

## `X` de filho de galeria não sobrevive à colagem da tela (2026-09-02)

Mapa de Alocação, camada de clique sobre a grade. Colei 33 rótulos transparentes por linha da
galeria, cada um com `X` e `Width` calculados, para virar caixa de clique de cada bloco e de cada
hora. Nada funcionava: o clique caía sempre no mesmo rótulo.

No Studio, com o controle selecionado, o `Width` estava com a fórmula que eu tinha escrito e o **`X`
estava com o literal `1`**. Mesma colagem, mesmas referências (`galPosicoesMap.Width`,
`mapLarguraRotulo`), mesmo controle: um sobreviveu, o outro foi descartado. Com todos os `X` valendo
`1`, os 33 rótulos empilharam no canto esquerdo da linha.

Digitando a **mesma** fórmula à mão na barra de fórmulas, ela é aceita, persiste e o controle vai
para o lugar certo. Ou seja: não é fórmula inválida, não é referência circular, não é a largura do
pai vista de dentro do template. **É a colagem que descarta o `X` dos filhos do template da galeria.**

**Como aplicar:** dentro de template de galeria, não entregar posição por `X` num arquivo colado —
vale para qualquer camada, sobreposição ou timeline. Usar container **AutoLayout** e deixar a posição
sair de `FillPortions`, que é da mesma família do `Width` e sobrevive. Custa precisão (a célula passa
a ser de largura fixa em vez de recorte ao minuto), e essa troca tem que ser assumida no desenho da
interação, não descoberta depois.

**O que mais custou aqui foi diagnosticar, não consertar.** Três hipóteses erradas antes desta —
ordem dos filhos na árvore, rótulo transparente não receber clique, e `UpdateContext` não propagar
antes do `Select()` — todas plausíveis e todas com o mesmo sintoma. O que resolveu foi parar de
remendar e pedir **duas leituras diretas no Studio**: onde a seleção do controle cai na tela, e o que
a barra de fórmulas mostra para aquela propriedade. Num controle colado à mão, o que o Studio tem
pode não ser o que o arquivo diz — e é o Studio que manda.

## O aeroporto se identifica pelo nome, não pelo ICAO (2026-09-02)

**Regra do repositório, para todo módulo novo:** a chave do aeroporto gravada em lista e carregada
em variável é o **nome** — `NAVEGANTES` —, não o código ICAO — `SBNF`. ICAO e IATA continuam
existindo como referência na tabela de aeroportos, mas não são chave de nada.

> **Não sair convertendo módulo antigo por causa desta regra.** `Frotas`, `Gestão de Chamados` e
> `SAFETY` gravam ICAO e **continuam assim** — decisão do Douglas em 02/09/2026. Cada um tem acervo
> próprio, e a conversão exige migrar o dado antes de colar o app: feita de enfiada, derruba três
> aplicações de uma vez. A regra vale para módulo novo e para quem for migrado sob pedido, um a um.
> No Mapa de Alocação ela já está aplicada.

**Por quê.** O nome é o que o usuário escolhe no seletor e o que toda tela já exibia. Usar ICAO por
baixo criava uma camada de tradução em duas direções — nome → ICAO ao entrar, ICAO → nome ao
exibir — que existia só para ser mantida, e que obrigava a carregar **duas** variáveis (`varAero` e
`varAeroNome`) para o mesmo conceito. Some a tradução, some a chance de as duas divergirem.

É também a mesma razão que já tinha feito `posicao_txt` e `patio_txt` serem texto redundante em
`tb_alocacoesMapa`: **a lista tem que ser legível sem o app**. Com ICAO gravado, toda exportação,
view do SharePoint e relatório de Power BI precisava do dicionário para dizer de que aeroporto é a
linha.

**A armadilha ao migrar, e ela é silenciosa.** Trocar a chave sem converter o acervo faz **todo
registro antigo sumir da tela sem erro nenhum** — o filtro `aeroporto = varAero` simplesmente não
casa mais. É a mesma classe de falha da coluna obrigatória nova num filtro de faixa. A ordem é:
converter o dado primeiro, **conferir zero linhas com o valor antigo**, e só então colar o app.

**Confira o tamanho da coluna antes.** `aeroporto` era `Text` com `MaxLength=10`: `NAVEGANTES` tem
exatamente 10 caracteres e passaria raspando, mas `FLORIANOPOLIS` não entraria. Trocar de código de
4 letras para nome livre é mudança de domínio, não só de conteúdo — a coluna foi para 60.

## Carga de dados antes da inicialização de estado derruba a tela inteira (2026-09-02)

Mapa de Alocação. A grade abriu **vazia**, sem erro nenhum no Studio, com o cabeçalho dizendo
"4 registro(s)". As coleções contavam a história: `colDia` 4 linhas, `colGrade` **25 linhas** — e a
galeria mostrando zero.

O `OnVisible` tinha ficado assim, com a carga dos catálogos novos colocada logo no começo:

```
Set(varMapaVisivel; true);
ClearCollect(colEquip; ...);        // <- falhou aqui
ClearCollect(colEquipSel; ...);
UpdateContext({ locPatio: "TODOS"; ... });   // <- nunca rodou
Select(btnAtualizarMap)
```

**Quando uma instrução da cadeia falha, o que vem depois não roda.** `locPatio` ficou em branco, e
`Filter(colGrade; locPatio = "TODOS" Or patio = locPatio)` não casa com nada quando `locPatio` é
branco — 25 linhas na coleção, nenhuma na tela. O `colDia`/`colGrade` populados vieram de o operador
ter clicado em ATUALIZAR, que é caminho separado. Nada disso aparece como erro: o Studio não acusa
falha de execução, só de compilação.

**A regra:** no `OnVisible`, **estado primeiro, carga de dados depois**. Variável que a tela usa para
filtrar, mostrar ou habilitar precisa nascer antes de qualquer coisa que possa falhar — conector,
coleção derivada, o que for. Inverter a ordem transforma qualquer falha de carga em tela vazia sem
explicação, que é o pior modo de falhar: parece que não há dado.

**O diagnóstico veio de contar linhas, não de ler fórmula.** `colEquipSel` estava com **0 linhas**
e por construção nunca pode ter menos de 1 — ele começa com o item `"—"`. Coleção com contagem
impossível é a evidência mais barata que existe: aponta a instrução exata que morreu, sem depender
de reproduzir o erro. Vale abrir **Configurações → Coleções** antes de reler qualquer expressão.

**De quebra, o padrão que falhou tinha um índice inútil.** `ForAll(Sequence(CountRows(col) + 1) As _i;
{ Value: If(_i.Value = 1; "—"; Index(col; _i.Value - 1).campo) })` existe para pôr um "—" na frente
de uma lista. Em named formula com tabela fixa ele funciona; em coleção que pode vir vazia, não vale
o risco. `ClearCollect(colSel; Table({ Value: "—" })); Collect(colSel; ForAll(col As _e; ...))` faz o
mesmo sem `Sequence` e sem `Index`.

## Um precedente só não é garantia: o corolário do dicionário (2026-09-02)

A regra do dicionário de propriedades dizia *ausência não é permissão*. Faltava o outro lado:
**presença em um único export não é garantia**.

Caso: a tela de restrições precisava escolher vários equipamentos de uma vez. `ComboBox@0.0.51` não
tem `SelectMultiple` em lugar nenhum do repositório, mas `Classic/ComboBox@2.4.0` tem — em **um**
controle, o `cmbWizAeros` do Service Desk. Copiei o padrão. O controle abriu com as 25 linhas (dava
para ver a barra de rolagem e a linha destacada) e **nenhum texto**: o `DisplayFields` não renderizou.

Gastei três colagens do Douglas nisso:

1. `DisplayFields: =["nome_equip"]` com coleção vinda do SharePoint — nada.
2. Alinhado ao precedente: coleção local com coluna `Value`, `DisplayFields: =["Value"]`, `Items` sem
   `Filter` por cima — nada.
3. Troquei de abordagem: `DropDown` + botão adicionar + galeria dos escolhidos, tudo com controle de
   uso corriqueiro. Funcionou.

**O erro foi insistir na segunda.** Quando a cópia fiel de um precedente único não funciona, a
hipótese mais provável deixa de ser *eu copiei errado* e passa a ser *aquele precedente depende de
algo que não está no YAML* — versão do controle no ambiente, ordem de propriedades no export
original, ou simplesmente sorte. Insistir é apostar contra a evidência.

**Como aplicar:** ao montar o dicionário, contar **em quantos arquivos distintos** cada propriedade
aparece, não só se aparece. Propriedade com contagem 1 é sinal amarelo: ou se escolhe outro caminho
desde o começo, ou se tem o plano B pronto **antes** da primeira colagem. Se o controle está no
caminho crítico da tela — como estava aqui, sem ele não dá para cadastrar regra — vale ir direto no
caminho corriqueiro, mesmo que a interface fique com mais cliques.

É a mesma família da lição do `X` em filho de galeria: as duas são sobre confiar demais num export
isolado. A diferença é que lá o Studio descartava a propriedade em silêncio, e aqui ele a aceitou e
não a honrou — que é pior, porque não há nada para inspecionar.

## Carga em massa não pode depender de default de coluna (2026-09-02)

Gerei um CSV de 698 registros para colar na exibição em grade da lista e **omiti a coluna `ativo`**,
confiando no `<Default>1</Default>` que está no `schemaXml` do repositório. As linhas entraram com
**`ativo = 0`** e **sumiram do app sem erro nenhum** — o filtro do dia exige `ativo = 1`.

A causa raiz não é o CSV: é que **o JSON do repositório descreve a lista que documentamos, não a que
existe no tenant.** A `tb_alocacoesMapa` foi criada antes desse arquivo, com `Default 0`. Os dois
divergiram e ninguém tinha por que notar, porque o app sempre gravou `ativo` explicitamente.

**A regra:** em carga em massa — colagem em grade, fluxo, script — **escreva todo campo que o filtro
da tela lê**, mesmo os que têm default. O que vale é a coluna que existe, não a documentada. Custa uma
coluna a mais no arquivo e elimina uma classe inteira de falha silenciosa.

**E o sintoma vale registrar:** flag errada não dá erro, só torna o registro invisível. É a mesma
família do `data_fim` em branco e do `aeroporto` gravado com ICAO depois da troca para nome — três
vezes na mesma entrega, sempre igual: **o dado entra, o filtro não casa, e a tela abre vazia como se
não houvesse nada para mostrar.** Quando algo não aparece e não há erro, o primeiro lugar a olhar é
cada termo do filtro contra o valor real gravado, um por um.

---

## Não desabilite a saída de emergência

Na tela de importação eu desabilitei o botão **NOVA IMPORTAÇÃO** enquanto o status fosse `PRONTO` ou
`PROCESSANDO`. O raciocínio parecia bom: tocá-lo durante uma execução limpa o acompanhamento, e o
operador ficaria sem a barra sem entender por quê.

Junto disso, o `OnVisible` tinha deixado de resetar o formulário, para o progresso sobreviver à
navegação entre telas.

**As duas mudanças combinadas criaram um beco sem saída.** Um item que ficasse em `PRONTO` sem ser
processado travava a tela inteira: `GERAR` desabilitado porque `varImportId` existe, `NOVA IMPORTAÇÃO`
desabilitado porque o status é `PRONTO`. E sair e voltar não devolvia o controle, porque o `OnVisible`
não resetava mais nada.

O erro de julgamento foi comparar mal os dois custos. **Perder o acompanhamento de algo que continua
rodando no servidor é um aborrecimento; não conseguir recomeçar é um bloqueio.** Botão que devolve a
tela ao estado inicial é a saída de emergência da tela — desabilitá-lo remove a única coisa que
socorre quando o resto deu errado.

**A correção certa não foi escolher entre os dois, foi tirar o caráter destrutivo do botão.** Ele
voltou a ficar sempre disponível, e o `OnVisible` passou a procurar uma importação em `PRONTO` ou
`PROCESSANDO` quando abre sem acompanhamento, reconectando-se a ela. Tocar o botão por engano deixou
de custar qualquer coisa: sair da tela e voltar traz a barra de volta.

**Regra prática:** antes de desabilitar um controle por causa de um estado, pergunte o que acontece se
esse estado ficar preso. Se a resposta for "o usuário não tem mais o que fazer nesta tela", o controle
não pode ser desabilitado — no máximo pedir confirmação. E prefira sempre tornar a ação recuperável a
impedi-la.

**Recorte do que preservar.** A raiz do problema foi eu ter preservado o estado errado. O que precisava
sobreviver à navegação era o **painel de progresso** (`varImportId` e `locImp`), não o estado inteiro
do formulário. Preservar o formulário junto trouxe de brinde um anexo velho que continuava contando na
validação `CountRows(attImportImp.Attachments) = 0`, deixando o `GERAR` submeter achando que havia
planilha. Ao decidir "isto tem que sobreviver", vale nomear exatamente o quê — preservar demais tem
efeitos que preservar de menos não tem.

---

## `App.Formulas` é pt-BR inteiro, decimal incluído

O `App.Formulas` do Studio usa o idioma do autor. Em pt-BR isso já era conhecido para o separador de
argumentos — é por isso que o arquivo usa `;` e termina definição com `;;`. **O que passou
despercebido é que o separador decimal muda junto.**

Escrevi `ordem: 6.5` para a posição T6C. O Studio recusou; o Douglas corrigiu para `ordem: 6,5`.

O erro é sutil porque o arquivo *parecia* consistente: `;` por toda parte, dialeto pt-BR à vista. Um
único número decimal escrito no dialeto invariante bastou para quebrar. **Não existe "meio pt-BR"** —
escolhido o idioma, ele vale para vírgula decimal, separador de argumentos e terminador.

**A exceção que confunde:** `mapPctHora = "4.1666"` continua com ponto, e está certo. É uma *string*
montada dentro de CSS, e CSS exige ponto. A regra é pelo tipo, não pela aparência: **número Power Fx
segue o idioma do Studio; texto que vai virar CSS, HTML ou parâmetro de outra linguagem segue as
regras daquela linguagem.**

Vale a mesma vigilância para qualquer `Text(v; "0.000"; "en-US")` do repositório — ali o `"en-US"`
explícito é justamente o que garante ponto na saída, independentemente do idioma do autor.

**Como conferir antes de colar:** procurar `[0-9]+\.[0-9]+` no arquivo, depois de remover o conteúdo
das strings. Sobrando alguma coisa, é decimal no dialeto errado.

**Detalhe que não é erro:** `ocupa: "T5,T6"` tem vírgula dentro de aspas e é conteúdo, não sintaxe. O
`.pa.yaml` das telas, por outro lado, é invariante e usa `,` de separador — as duas metades do mesmo
projeto falam dialetos diferentes, e é preciso saber em qual arquivo se está.
