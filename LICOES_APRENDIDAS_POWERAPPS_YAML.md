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

## PA2108: `Text@0.0.51` não tem `Color` — a propriedade é `FontColor`

Projeto/tela: Perdidos e Achados, `ScreenEntregaListar`, cabeçalho de colunas
(23/09/2026).

Mensagem do Studio na colagem:
`error PA2108 : Unknown property 'Color' for control type 'Text@0.0.51'`
— uma linha por rótulo, e a tela inteira é rejeitada.

Causa: o controle moderno `Text@0.0.51` expõe a cor do texto como **`FontColor`**.
`Color` existe em `Label@2.5.1` (clássico), e a confusão vem de copiar de um
para o outro.

Correção: trocar `Color: =RGBA(...)` por `FontColor: =RGBA(...)`.

Referência no próprio app: `DataCardKey20_1` em `ScreenCadastrar` usa
`FontColor: =RGBA(255, 0, 0, 1)`.

Validação preventiva: rejeitar `Color:` dentro de qualquer bloco cujo
`Control` seja `Text@0.0.51`.

## Posicionamento dentro de galeria: `Parent.TemplateWidth`, nunca `Parent.Width`

Projeto/tela: Perdidos e Achados, `ScreenCadastrar`, galeria `Table2` (23/09/2026).

Sintoma: controles de uma linha da galeria renderizavam **empilhados no canto
esquerdo**, sobrepondo-se uns aos outros, enquanto os rótulos vizinhos ocupavam
a linha inteira normalmente. O Studio não emite erro nem aviso — a tela
simplesmente aparece errada.

Causa confirmada: dentro do template de uma galeria, `Parent.Width` **não**
devolve a largura renderizada da linha, principalmente quando a galeria está
dentro de um container AutoLayout e não tem propriedade `Width` própria. A
referência correta é `Parent.TemplateWidth`.

No caso, dois controles do mesmo template usavam a referência errada:

```
ButtonCanvas3   X: =Parent.Width - 160        -> ia para o canto esquerdo
Button2         Width: =Parent.Width - 10     -> ~160px em vez de ~540px
```

O segundo tinha efeito funcional, não só visual: `Button2` é o botão
transparente que seleciona a linha, e com a largura errada **clicar na parte
direita da linha não selecionava nada**.

Correção: trocar por `Parent.TemplateWidth` nos dois.

Sinal de diagnóstico: se controles irmãos do mesmo template se comportam de
forma diferente, compare qual referência cada um usa. No caso, os rótulos usavam
`Parent.TemplateWidth` e renderizavam certo; só os dois com `Parent.Width`
saíam do lugar.

Validação preventiva: rejeitar `Parent.Width` e `Parent.Height` em qualquer
controle que esteja dentro de `Children:` de um `Gallery@`. Usar
`Parent.TemplateWidth` e `Parent.TemplateHeight`.

### Complemento obrigatório: o `X` pode chegar zerado na colagem

A regra acima está certa, mas sozinha **não resolve** — e acreditar que resolve
custou três tentativas frustradas na mesma tela.

Em galerias de variante `BrowseLayout_Vertical_TwoTextOneImage`, **o Studio
descarta o `X` que vem no YAML e o traz zerado**. Confirmado ao selecionar um
controle cujo arquivo dizia `X: =90` e a barra de fórmulas mostrar `1`.

Consequência prática: **editar `X` no YAML não tem efeito nessas galerias.**
O valor precisa ser conferido e, se necessário, redigitado no Studio depois de
colar a tela.

Fluxo que funciona:

1. colar a tela;
2. selecionar cada controle posicionado da galeria e conferir o `X` na barra de
   fórmulas — se vier `0` ou `1`, foi zerado;
3. digitar o valor correto no Studio, onde o resultado aparece na hora;
4. **gravar os valores finais de volta no YAML**, para não se perderem na
   próxima colagem.

Referência de ancoragem que funcionou (`ScreenEntregaListar`, `Gallery2`):
rótulos da linha-pai alinhados à direita por `Parent.TemplateWidth - N`
(protocolo `- 300`, data `- 460`, status `- 560`, botão `- 160`) e o texto do
item da galeria aninhada em `X` fixo pequeno (`50`).

Antipadrão: aplicar a troca `Parent.Width` → `Parent.TemplateWidth` em massa,
sem medir. Em `Table2` da `ScreenCadastrar` isso corrigiu; na `Gallery2` da
`ScreenEntregaListar` a mesma troca **piorou**, jogando o botão para a esquerda.
Medir antes, uma galeria por vez.

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
11. Rejeitar `Parent.Width`/`Parent.Height` dentro do template de galeria.
12. Colar no Power Apps Studio conectado à lista real.
13. Testar criar, visualizar, editar, excluir, anexar e filtrar.

Os itens 12 e 13 dependem do ambiente Power Apps/SharePoint e não podem ser
substituídos apenas por validação local do arquivo.

## Cor literal em tela é dívida: usar tokens do design system

Projeto/tela: Perdidos e Achados, 13 telas (24/09/2026).

Sintoma: pedido de "trocar para as cores da ASUR" esbarrou em 236 literais
`RGBA(...)` espalhados por 13 arquivos, mais `App.Theme.Colors.Primary` em 27
pontos (que só muda pelo tema do Studio, não pelo YAML). Não existia um ponto
único de troca, e a mesma cor aparecia em variações próximas — `RGBA(39, 113,
194, 1)`, `RGBA(15, 108, 189, 1)`, `RGBA(5, 102, 178, 1)` eram todas "o azul".

Causa: cor declarada no controle, não no tema.

Correção: adotar o padrão já estabelecido em `Mapa de Alocação`
(`AppFormulas_Mapa.fx.md`, seção 7) — duas famílias de Named Formula,
`hx*` (string hex, para dentro do HTML dos `HtmlViewer`) e `thm*`
(`ColorValue(hx*)`, para controle nativo). Nenhuma tela declara cor literal.
Trocar a marca passa a ser editar um bloco no `App.Formulas`.

Paleta institucional Motiva/ASUR: `#391694` primária, `#2A106E` escura,
`#EDE9FB` clara, `#C9C5E6` borda, `#F8FAFC` fundo, `#1E293B` texto,
`#64748B` texto fraco, `#DD511A` ação, `#15803D`/`#B45309`/`#B91C1C`
verde/âmbar/vermelho.

Preservar sem tokenizar: branco, preto, transparências (`RGBA(0,0,0,0.05)` e
afins) e cinzas de estado desabilitado. São estrutura, não marca.

Ordem de colagem obrigatória: **`App.Formulas` primeiro, telas depois.** Uma
tela que referencia `thmPrimaria` antes do token existir falha inteira na
colagem.

Validação preventiva: extrair todo `\bthm[A-Za-z]+` das telas e conferir que
cada nome está definido no `App.Formulas` do projeto.

## Armadilha de validador: atribuir a linha à galeria mais interna

Mesma data. O verificador de `Parent.Width` em galeria percorria cada galeria e
marcava todas as linhas dentro do seu intervalo. Em galeria aninhada, a mesma
linha era atribuída às duas — a de fora (sem `Width` própria) gerava falso
positivo, ainda que o `Parent` real fosse a de dentro (com `Width` própria).

Correção: para cada linha, escolher como dona a galeria **mais interna** que a
contém, e só então avaliar se essa galeria tem `Width` própria.

Lição geral: verificação de escopo em estrutura aninhada tem que resolver o
dono mais próximo, nunca todos os ancestrais. Um falso positivo recorrente
treina o operador a ignorar o validador — custa mais caro que não ter.

## Falha silenciosa: `\b` em heredoc vira backspace

Projeto: Perdidos e Achados, script de troca de cores (24/09/2026).

Sintoma: o script reportou "236 substituicoes" e gravou os arquivos, mas as
9 trocas de hex dentro do HTML dos `HtmlViewer` nao aconteceram. Nenhum erro.
Descoberto so quando o usuario apontou que a cor nao mudou.

Causa: o script foi escrito em disco por heredoc e a sequencia `'\b'` chegou
ao arquivo como `'\b'`. Em JavaScript `"\b"` **nao** e a borda de palavra do
regex — e o caractere backspace (U+0008). O padrao virou `#FFA500<BS>`, que
nunca casa. Como o codigo era `if (c) { ...substitui... }`, zero ocorrencias
significava simplesmente nao fazer nada.

Correcao: `split(literal).join(novo)` em vez de `new RegExp(literal + '\b')`.
Para trocar texto literal, regex nao acrescenta nada e introduz uma camada de
escape a mais.

Prevencao, em duas frentes:

1. Nao escrever escape de regex atraves de heredoc. Se precisar de regex no
   script, montar com `String.raw` ou gravar o arquivo com a ferramenta de
   escrita, nunca por `cat <<EOF`.
2. **Todo script de substituicao em massa deve falhar alto quando uma regra nao
   casa nada.** Uma regra que nao encontra ocorrencia e quase sempre bug de
   padrao, nao ausencia legitima. Contar por regra e imprimir as que ficaram em
   zero — a contagem total agregada esconde exatamente esse caso.

Lição geral: contador agregado e a pior metrica para validar substituicao em
lote. 236 "sucessos" mascararam 9 falhas porque ninguem contou por regra.

## `Button@0.0.45`: sem `Appearance` o padrao e Primary, e a cor vem do tema

Projeto: Perdidos e Achados, 13 telas (24/09/2026).

Sintoma: depois de trocar a paleta, 34 botoes continuaram na cor antiga. Nao
havia literal de cor neles para substituir, e o YAML nao dava nenhum sinal.

Causa: `Button@0.0.45` resolve a cor por `BasePaletteColor`. Sem essa
propriedade, cai na paleta do **tema do app no Studio** — que nao e editavel
pelo YAML da tela. Tres situacoes distintas, e so a primeira e obvia:

1. `Appearance: ='ButtonCanvas.Appearance'.Primary` declarado — botao solido.
2. **`Appearance` ausente** — o padrao do controle ja e Primary. Este e o que
   escapa, porque nao ha linha nenhuma para o padrao de busca encontrar.
3. `Appearance.Secondary` — parece "sem cor" por ser vazado, mas a borda e o
   texto saem do tema igual.

`Appearance.Transparent` normalmente tem `FontColor` proprio; conferir antes de
incluir, porque pintar um icone que esta sobre fundo escuro o faz sumir.

Correcao: fixar `BasePaletteColor` em todos, por aparencia — solido na cor de
acao, vazado na cor institucional.

Validação preventiva: para cada `Button@0.0.45`, reprovar quando nao houver
`BasePaletteColor` e a aparencia for ausente, `Primary` ou `Secondary`.

Lição geral, que vale para qualquer troca de identidade visual em Canvas App:
**substituir literais de cor nao termina o trabalho.** Todo controle cuja cor
vem do tema — `BasePaletteColor` ausente, `App.Theme.Colors.*`, `Accent` —
continua com a aparencia antiga e nao aparece em busca por `RGBA(`. Levantar
esses controles por tipo, nao por cor.

## Verificacao que nunca falha nao e verificacao — autoteste e obrigatorio

Projeto: Perdidos e Achados, validador das telas (24/09/2026).

Sintoma: o validador reportou "TODAS AS VERIFICACOES PASSARAM" varias vezes
seguidas enquanto **dois** de seus checks estavam mortos. Descoberto so ao
testar de proposito uma copia quebrada.

Causa, a mesma duas vezes: escape de regex escrito atraves do shell (heredoc e
`node -e`). O `\b` chegou ao arquivo como o **caractere backspace** (0x08) e o
`\s` perdeu a barra. O padrao `/\bParent\.(Width|Height)\b/` virou
`/<BS>Parent.(Width|Height)<BS>/`, que nao casa nada. `cat -A` mostra o `^H`;
um editor comum e o proprio `Read` nao mostram.

Agravante: a lição sobre esse mesmo bug ja estava escrita neste arquivo e eu a
repeti pelo outro caminho. Escrever a licao nao basta — o conserto tem que
ser estrutural.

Correcao estrutural, em tres frentes:

1. **Nunca escrever escape de regex atraves do shell.** Usar a ferramenta de
   escrita de arquivo, e `String.raw` no codigo.
2. **Autoteste obrigatorio.** Para cada check novo, quebrar uma copia da tela
   de proposito e confirmar que o check ACUSA. Um check que so foi visto
   passando nunca foi testado.
3. **Varredura de caractere de controle** no proprio script:
   `/[\x00-\x08\x0b\x0c\x0e-\x1f]/` em cada linha, apos qualquer edicao
   automatizada.

Bonus da correcao: com o check vivo, ele encontrou 7 ocorrencias reais de
`Parent.Width` em galeria sem `Width` propria, em 3 telas — inclusive um
`Button2_6.Width` que e o botao transparente de selecao de linha, o mesmo bug
funcional ja confirmado duas vezes em outras telas.

Segundo furo do mesmo check, achado junto: a propria propriedade `Width` de uma
galeria aninhada estava sendo avaliada contra ela mesma. Ali o `Parent` e a
galeria de FORA. Corrigido restringindo a atribuicao a linhas depois do
`Children:` da galeria dona.

> O validador agora vive em `PerdidoseAchados/validar_telas_pa.mjs`, versionado.
> Antes existia so no scratchpad da sessao — por isso quebrava sem deixar
> rastro e ninguem percebia entre uma sessao e outra.

## Inserir propriedade por ordem alfabetica sem pular bloco escalar

Projeto: Perdidos e Achados, `ScreenConsultListar` / `Image2_2` (24/09/2026).

Mensagem do Studio: `Caracteres inesperados. Caracteres sao usados na formula de
forma inesperada.`

Causa: um script inseriu `X: =45` na posicao alfabetica dentro das propriedades
do controle, varrendo linha a linha por `^ *([A-Za-z]+):`. As linhas do corpo de
um `OnSelect: |-` tem essa mesma forma (`var_item: TBL_ITENS,`), entao a
insercao caiu **dentro da formula**, no meio de um `UpdateContext`.

O YAML continua valido — a linha vira texto do escalar — e so o Power Fx
reclama, ao abrir a tela. Nenhum validador de sintaxe YAML pega isso.

Correcao: ao varrer propriedades de um controle, manter estado de bloco escalar.
Uma linha que termina em `|`, `|-` ou `|+` abre o bloco; tudo mais indentado que
ela e corpo, nao chave.

Dois erros irmaos no mesmo dia, que valem como um so aprendizado:

1. Procurar `Y: =` no bloco inteiro de um controle achou o `Y` de um **filho**,
   porque a busca nao parou no `Children:`. Escreveu no controle errado.
2. Inserir por ordem alfabetica sem pular o escalar escreveu **dentro da
   formula**.

Regra geral: **os limites de um controle sao do `- Nome:` ate o `Children:`
dele, e dentro disso so contam as chaves no nivel exato de indentacao das
propriedades, fora de bloco escalar.** Qualquer script que edite YAML de tela
precisa dos tres cortes: nivel, `Children:` e escalar.

Validacao preventiva (check 12): rejeitar `X`, `Y`, `Width`, `Height`, `Fill`,
`Visible`, `BasePaletteColor` ou `Appearance` seguidos de `: =` quando estiverem
dentro de um bloco escalar. Em CSS dentro de `HtmlText` aparece `width:` sem o
`=`, entao nao ha falso positivo.

## A solucao definitiva para o `X` zerado: `GroupContainer` dentro do template

Projeto/tela: Perdidos e Achados, `ScreenConsultListar` / `Gallery2_1`
(24/09/2026).

Historico: o `X` dos filhos diretos do template de galeria
`BrowseLayout`/`VariableHeight` e descartado na colagem. Documentado antes com
o fluxo "colar, conferir, redigitar no Studio, gravar de volta no YAML". **Esse
fluxo nao se sustenta:** a cada nova colagem da tela tudo zera outra vez. Nesta
tela aconteceu tres vezes, e na terceira os controles sumiram — caidos todos em
`X=0`, ficaram cobertos pela galeria aninhada, que tem `Fill` branco e
renderiza depois deles.

Confirmado pelo usuario no Studio: `X = 0`, `Visible` intacto.

Correcao estrutural: envolver os controles posicionados num
`GroupContainer@1.5.0` variante `ManualLayout` **dentro do template**. Eles
deixam de ser filhos diretos da galeria e o `X` passa a ser preservado.

```
Gallery2_1
  RowContainer          <- GroupContainer ManualLayout, Height fixa
    ButtonCanvas3_6       X preservado
    Subtitle1_13
    Subtitle1_14
    Button2_6
    EntregarButton_2
  Table2_5              <- empilhado por Y, X irrelevante
  HtmlTextRastreio
```

Ganhos, alem do `X`: o container tem `Height` explicita, entao a linha para de
colapsar e o que vem abaixo deixa de ser cortado; e a sobreposicao some, porque
a ordem de renderizacao passa a ser resolvida dentro do container.

**Armadilha na conversao:** dentro do container o `Parent` deixa de ser a
galeria. `Parent.TemplateWidth` **nao existe** ali e precisa virar
`Parent.Width` — o container tem largura propria. Só o `Width` do proprio
container continua usando `Parent.TemplateWidth`, porque o Parent dele e a
galeria.

Controle de texto dentro de galeria tem uma saida mais barata, quando serve:
posicionar por `PaddingLeft` em vez de `X`. Padding nao e descartado na
colagem. Nao funciona para botao.

Validacao preventiva: o check de `Parent.Width` em galeria precisa reconhecer
`GroupContainer` intermediario, senao acusa falso positivo justamente na
estrutura correta.

### Contrapartida obrigatoria do `RowContainer`: `Select(Parent)` quebra

Mensagem do Studio: `Select um controle que nao tem uma propriedade OnSelect`.

Ao mover controles para dentro do `GroupContainer`, o `Parent` deles deixa de
ser a galeria e passa a ser o container — que **nao tem `OnSelect`**. Todo
`OnSelect: =Select(Parent)` dos controles movidos vira erro.

Correcao: trocar por `Select(<NomeDaGaleria>)`. O objetivo continua sendo o
mesmo, propagar o clique do rotulo para a selecao da linha.

Checklist ao converter uma linha de galeria para `GroupContainer` — sao tres
coisas que mudam de significado junto, e esquecer qualquer uma quebra a tela:

1. `X` passa a ser preservado (esse e o ganho).
2. `Parent.TemplateWidth` -> `Parent.Width` (container tem largura propria).
3. `Select(Parent)` -> `Select(<Galeria>)` (container nao tem `OnSelect`).

Validacao preventiva (check 13): rejeitar `Select(Parent)` quando o ancestral
mais proximo for um `GroupContainer` e nao uma galeria.

### Correcao da correcao: `Y` tambem e descartado, e mover metade nao resolve

Primeira tentativa: mover so os controles posicionados para o `GroupContainer`,
deixando a galeria aninhada e o acordeao como filhos diretos. **Nao mudou
nada.**

Causa: o `Y` sofre o mesmo descarte que o `X`. A galeria aninhada tinha
`Y: =40` e `Fill: =RGBA(255, 255, 255, 1)` — branco opaco. Caindo em `Y=0`, ela
cobria o container inteiro, que esta em `Y=0` com fundo transparente. Os cinco
controles continuavam invisiveis, agora por outro motivo.

Diagnostico que teria poupado a rodada: quando um controle some por inteiro em
vez de aparecer fora do lugar, procure **quem tem `Fill` opaco e renderiza
depois dele**, nao so o proprio controle.

Regra corrigida: **ou todos os filhos do template vao para o container, ou
nenhum.** Deixar um irmao de fora mantem o problema, e um irmao com `Fill`
opaco o piora.

Estrutura final que funciona:

```
Gallery2_1
  RowContainer                Height = 40 + Table2_5.Height + HtmlTextRastreio.Height
    ButtonCanvas3_6           X=11   Y=5
    Subtitle1_13              X=141  Y=5
    Subtitle1_14              X=292  Y=5
    Button2_6                 X=0
    EntregarButton_2          X=510  Y=5
    Table2_5                  Y=40
    HtmlTextRastreio          Y = Table2_5.Y + Table2_5.Height
```

A `Height` do container soma as tres faixas, entao a linha cresce com o
conteudo em vez de cortar o acordeao.

### Conclusao: `X` e insalvavel em template de galeria — use AutoLayout

Confirmado no Studio pelo usuario: `EntregarButton_2` e `Subtitle1_13` vieram
ambos com `X = 0` **mesmo dentro de um `GroupContainer` ManualLayout**. O
Studio zera `X` de **todos os descendentes** do template, em qualquer
profundidade. O container nao protege.

Isso invalida as duas estrategias anteriores registradas aqui:

- "colar, conferir, redigitar no Studio" — nao sobrevive a proxima colagem;
- "envolver num `GroupContainer` ManualLayout" — o `X` zera igual.

O que o container resolveu de fato foi outro problema: impedir que um irmao com
`Fill` opaco cobrisse os controles. Util, mas nao era o problema do `X`.

**A unica solucao que se sustenta e nao usar `X`:**

| Controle | Como posicionar |
|---|---|
| texto (`HtmlViewer`, `Label`) | `PaddingLeft` — nao e descartado |
| qualquer controle, em linha | `GroupContainer` **AutoLayout** Horizontal |
| empilhamento vertical | `GroupContainer` **AutoLayout** Vertical |

Em AutoLayout nao existe `X` para ser zerado: a posicao vem da ordem dos
filhos, da `Width` de cada um, do `LayoutGap` e do `FillPortions`. Um controle
com `FillPortions: =1` vira o espacador flexivel que empurra o resto para a
direita — foi assim que o botao de selecao da linha, que antes cobria tudo por
`X`, virou o vao entre o status e o botao de acao.

Estrutura final que funciona em `ScreenConsultListar`:

```
Gallery2_1
  RowContainer          AutoLayout Vertical, Width = Parent.TemplateWidth
    HeaderRow           AutoLayout Horizontal, Height 40, LayoutGap 10
      ButtonCanvas3_6   Width 110
      Subtitle1_13      Width 130
      Subtitle1_14      Width 200
      Button2_6         FillPortions 1      <- espacador + Tooltip
      EntregarButton_2  Width 100
    Table2_5            AlignInContainer Stretch
    HtmlTextRastreio    AlignInContainer Stretch
```

O realce da linha selecionada subiu para o `Fill` do `RowContainer`, ja que o
botao transparente deixou de cobrir a linha inteira.

**Altura nunca pode depender do render.** `Height: =Self.AllItemsCount * 52`
numa galeria aninhada cria circularidade — `AllItemsCount` depende da altura
disponivel, que depende de `AllItemsCount` — e o Power Apps resolve como zero,
fazendo o conteudo sumir. Contar nos dados:
`CountRows(Filter(colecao, chave = ThisItem.ID)) * 52`. O mesmo vale para
`Visible: =Galeria.AllItemsCount > 0`, que deve virar
`!IsEmpty(Filter(colecao, chave = ThisItem.ID))`.

## Remover uma propriedade `|-` sem remover o corpo

Projeto: Perdidos e Achados, `ScreenConsultListar` / `Button2_6` (24/09/2026).

Mensagem do Studio: `Valor Color esperado. ... a formula usa escopo que nao tem
suporte para avaliacao no momento.` — na propriedade **errada**, `DisabledFill`.

Causa: um script removeu a chave `Fill: |-` de um controle mas manteve as 15
linhas do corpo. Elas passaram a pender de `DisabledFill: =RGBA(247,247,247,1)`,
que virou um valor multi-linha invalido. O YAML continua valido; so o Studio
reclama, e reclama apontando para a propriedade vizinha, nao para a removida.

Correcao no script: ao remover uma propriedade que abre bloco escalar, consumir
tambem todas as linhas mais indentadas que ela.

Validacao preventiva (check 14): linha com indentacao maior que a chave
anterior, sendo que a chave anterior tem valor proprio (`: =`) e nao abre
escalar (`|`, `|-`, `|+`, `>`), e corpo orfao.

### O autoteste pagou sozinho

Ao testar o check 14 contra uma copia quebrada de proposito, ele nao acusou.
Motivo: `const orfas` colidia com uma variavel ja declarada no check 8, e o
arquivo inteiro quebrava com `SyntaxError` — **o validador nao rodava nenhuma
verificacao**. Sem o autoteste isso teria passado como "todas as verificacoes
passaram" na proxima execucao.

Regra: depois de acrescentar um check, rodar contra uma copia com o defeito
reintroduzido. Ver o check ACUSAR e a unica prova de que ele existe.

### Em AutoLayout, `Height` so manda com `FillPortions: =0`

Sintoma: convertido o template para AutoLayout Vertical, a linha-cabecalho
ficou perfeita, mas a galeria aninhada e o acordeao nao renderizavam — a linha
inteira colapsava para a altura do cabecalho.

Causa: num `GroupContainer` AutoLayout, o eixo principal e distribuido por
`FillPortions`. Enquanto `FillPortions` nao for `0`, a `Height` explicita do
filho e ignorada e ele recebe a fatia que o fluxo decidir. Com o container
dimensionado pelo conteudo, essa fatia acaba sendo zero.

Correcao: `FillPortions: =0` em todo filho cuja altura deve valer.

```
RowContainer        AutoLayout Vertical
  HeaderRow         FillPortions 0   Height 40
  Table2_5          FillPortions 0   Height CountRows(...) * 52
  HtmlTextRastreio  FillPortions 0   Height If(ThisItem.IsSelected, 46, 0)
```

No eixo transversal quem manda e `AlignInContainer`: `Stretch` para ocupar a
largura toda, `Center` para centralizar.

Inverso util: `FillPortions: =1` num filho o transforma no **espacador
flexivel** que empurra os seguintes para o fim — foi assim que o botao
transparente de selecao virou o vao entre o status e o botao de acao, sem
precisar de `X`.

## Barra invertida em heredoc some — verificar SEMPRE o que foi gravado (25/09/2026)

Neste ambiente (Git Bash no Windows), **um `\` escrito dentro de heredoc chega ao
arquivo pela metade**, mesmo com o delimitador entre aspas (`<<'EOF'`). `\s` vira
`s`; `\\s` vira `\s`.

Consequencia real: o check 18 do `validar_telas_pa.mjs` nasceu com
`/^s*(...)/` em vez de `/^\s*(...)/`. Casava com nada, e o validador anunciou
"TODAS AS VERIFICACOES PASSARAM" por um dia inteiro. **Foi a terceira vez que o
mesmo erro passou.**

Duas regras, nessa ordem:

1. **Nao usar `\` em regex de script gerado.** A indentacao dos `.pa.yaml` e sempre
   espaco (o proprio check 5 rejeita TAB), entao ` *` substitui `\s*`, e `[^ ]+`
   substitui `\S+`. Nenhuma barra, nenhum problema.
2. **Todo check novo nasce com auto-teste.** Plantar a violacao numa copia do arquivo
   e conferir que o validador ACUSA. Um check que so sabe dizer "passou" nao prova
   nada — e exatamente assim que ele falha em silencio.

## `Button@0.0.45` nao tem `Tooltip` (25/09/2026)

Studio: `PA2108 : Unknown property 'Tooltip' for control type 'Button@0.0.45'`.
Quem tem `Tooltip` e o `Classic/Button@2.2.0` e o `Classic/Icon@2.5.0`. No
`Button@0.0.45` o equivalente e `AccessibleLabel`, que aceita a mesma formula.

Regra geral: **nao adivinhar propriedade**. Antes de escrever uma que voce nunca
usou naquele tipo de controle, varrer o repositorio em busca de um controle igual
que ja a tenha. O par entrou no check 10 do validador, que virou tabela.

## PA1001: `{ chave: valor }` em valor de linha unica quebra a colagem (20/10/2026)

Studio: `error PA1001 : An error occurred while parsing PaYaml. Error code:
YamlInvalidSyntax; Reason: While scanning a plain scalar value, found invalid
mapping.`

Causa: o `": "` dentro das chaves faz o YAML tratar o resto da linha como mapa.

```yaml
# QUEBRA
OnSelect: =UpdateContext({var_visibleFormDest: false})

# CERTO
OnSelect: |-
  =UpdateContext({var_visibleFormDest: false})
```

Vale para `UpdateContext`, `Patch`, `Set` com registro, `Table({...})` — qualquer
valor em uma linha so que contenha chave e dois-pontos entre chaves. O Studio sempre
emite esses casos como escalar de bloco; quem escreve YAML a mao e que cai nisso.

Virou o **check 19** do `validar_telas_pa.mjs`, com auto-teste.

## Membro de enum com caixa errada (20/10/2026)

Studio: `O nome nao e valido. 'MultiLine' nao e reconhecido.`

Era `Mode: ='TextInputCanvas.Mode'.MultiLine`. O certo e **`Multiline`**, com L
minusculo — e o que as dez outras ocorrencias do repositorio ja usavam.

Nao adivinhar a grafia de membro de enum. Antes de escrever, rodar
`grep -rh "<NomeDoEnum>" --include='*.pa.yaml' .` e copiar a grafia que ja existe:
o que esta nos arquivos foi emitido pelo proprio Studio e por definicao esta certo.

Virou o **check 20** do `validar_telas_pa.mjs`, que e uma tabela de pares
(grafia errada, grafia certa). Cada erro novo desses acrescenta uma linha.

## Procurar propriedade so por `Nome: =` nao enxerga o escalar de bloco (20/10/2026)

Conferi se os date pickers da `ScreenInventarioSeparar` tinham `OnChange` com
`grep "^ *OnChange: ="` — nao acharam nada, concluí que faltava e inseri. Os dois
**ja tinham**, na forma `OnChange: |-` com o corpo embaixo. Resultado: propriedade
declarada duas vezes.

Em YAML a ultima declaracao vence, **em silencio**. Nao ha erro de colagem: a
propriedade simplesmente passa a valer outra coisa. Foi sorte o efeito ser nenhum
neste caso, porque as duas formulas faziam o mesmo.

Uma propriedade pode aparecer de tres formas, e a busca tem que cobrir as tres:

```yaml
Nome: =formula          # valor em linha
Nome: |-                # escalar de bloco, o corpo vem indentado embaixo
Nome: "=formula\r\n..." # string serializada, formato antigo
```

Busque sempre por `^ *Nome:` — sem o `=`. Virou o **check 21** do
`validar_telas_pa.mjs`, que acusa propriedade repetida dentro do mesmo controle.

## O campo de anexos nao tem o mesmo nome em toda lista (21/10/2026)

`Default: =ThisItem.Anexos` funciona em `tb_focoAtracaoFauna`, em `PresencaFauna` e
na Inspecao — tres listas do mesmo tenant. **Nao funciona** em
`tbl_perdidosAchadosDestinacao`: Studio responde "'Anexos' nao e reconhecido".

A diferenca e como a lista nasceu. As que vieram pela interface do SharePoint em
pt-BR tem o campo de anexos com rotulo `Anexos`; a que o fluxo **List_Generator**
criou por REST ficou com `Attachments`.

Ou seja: tres precedentes concordando **nao** garantem o quarto caso. Para o campo de
anexos, conferir na lista especifica. O `DataField` nao muda — e sempre
`="{Attachments}"` — so o `Default` e que segue o rotulo.

Se der erro e nao houver como conferir, **apagar o `Default`** e uma saida boa: o
upload continua funcionando e o `Update` grava; perde-se apenas exibir anexo que ja
exista.

## `ModernTabList@1.0.0` se pinta com `BasePaletteColor` (21/10/2026)

A pilha da guia selecionada, com `Appearance: =TabListAppearance.FilledCircular`,
vinha do tema do Studio — roxo Motiva. A propriedade e `BasePaletteColor`, a mesma
do `Button@0.0.45`.

Nao havia nenhum outro `ModernTabList` no workspace para copiar. O jeito de
descobrir, sem adivinhar: selecionar o controle no Studio e abrir o **dropdown de
propriedades** (canto superior esquerdo), que lista todas pelo nome real.
