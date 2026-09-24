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
