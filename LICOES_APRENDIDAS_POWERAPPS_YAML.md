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

### PA2110 quando dois geradores escrevem a mesma tela (2026-09-24)

- Projeto/tela: SAFETY / os 7 módulos de ocorrência.
- Contexto: `build/gerar_aeroporto_forms.py` passou a inserir o seletor de
  aeroporto (`cmbFrm<K>Aeroporto`) direto em `msapp/Src`, que é a **fonte** lida
  por `build/gerar.py` — e o `gerar.py` já inseria um controle de mesmo nome na
  tela consolidada que produz. Rodar o pipeline depois colocaria os dois na
  mesma tela.
- Não chegou ao Studio: `valida.py` reprova nome duplicado antes. A causa, porém,
  é genérica: **quando um gerador passa a escrever no arquivo-fonte de outro,
  toda inserção por nome vira candidata a duplicata.**
- Correção: a inserção passou a ser condicionada à ausência do nome no texto de
  origem.
- Prevenção: todo gerador que INSERE controle precisa ser idempotente por nome
  *e* verificar se a fonte já traz aquele nome — nunca assumir que a fonte é o
  export intocado.

### YAML: bloco literal `|-` sem recuo derruba o arquivo inteiro (2026-09-24)

- Projeto: SAFETY / formulários dos módulos.
- Mensagem (PyYAML, antes de chegar ao Studio): `while scanning a simple key` +
  `could not find expected ':'`.
- Causa confirmada: o gerador escreveu `Default: |-` e as linhas da fórmula no
  MESMO recuo da chave. Bloco literal exige recuo **maior** que o da chave; no
  mesmo nível, a primeira linha da fórmula (`=If(`) é lida como uma nova chave e
  o parser quebra dezenas de linhas adiante.
- Correção: linhas de continuação recebem o recuo da chave + 2.
- Prevenção: carregar todo arquivo gerado com o PyYAML antes de entregar.
  O Studio recusa a colagem inteira sem dizer onde está o erro; o PyYAML aponta a
  linha.
- **Correção (2026-09-24, mesmo dia):** usar `yaml.load(f, Loader=yaml.BaseLoader)`,
  **não** `yaml.safe_load`. O `SafeLoader` recusa o `=` sozinho de
  `LayoutMaxHeight: =` (resolve para a tag `tag:yaml.org,2002:value` e diz *could
  not determine a constructor*) — e o Studio exporta essa linha em quase todo
  controle de AutoLayout. Com `safe_load`, o próprio export original reprova e o
  checador vira ruído. O `BaseLoader` continua pegando o erro de recuo do `|-`.
  Visto em `SAFETY/build/validar_aeroporto.py`: as 12 telas reprovaram no
  `safe_load` e passaram no `BaseLoader`.

### Coluna com prefixo de outro módulo NÃO é, sozinha, bug de cópia (2026-09-24)

- Data: 2026-09-24. Projeto/tela: SAFETY / `ScreenAcessIndFaunaDetalhes` (e, por
  tabela, `ScreenExcursaoPista`, `ScreenJetBlast`, `ScreenColisaoVeiculos`).
- Sintoma aparente: a tela de detalhes lia
  `var_aceIndFaunaSelect.derFlu_aeroporto`, `.derFlu_data`, `.colVei_danos`,
  `.intExt_tempo` — prefixos de **outros** módulos. Diagnóstico natural (e
  errado): "bug de copiar/colar, o campo sai em branco".
- Causa confirmada, lendo `msapp/References/DataSources.json`: **cinco das oito
  listas deste app foram criadas copiando a lista de Derramamento**. No
  SharePoint, renomear uma coluna muda só o **nome de exibição**; o **nome
  interno** fica o da criação. O export registra os dois:

  ```json
  "properties": { "derFlu_aeroporto": { "title": "aceIndFauna_aeroporto", ... } }
  //                ^ nome interno              ^ nome de exibição
  ```

  E há o mapa explícito `ConnectedDataSourceInfoNameMapping`
  (`{"derFlu_data": "aceIndFauna_data", ...}`).
- O Power Apps aceita **as duas formas** em fórmula sobre SharePoint. Neste app
  as duas convivem: a tela de detalhes usa o nome interno e o `Patch` do
  formulário, a galeria e os filtros usam o de exibição — tudo em produção.
- Correção aplicada: padronizar pelo nome de exibição **depois de conferir par a
  par no mapeamento do export** — nunca deduzindo pelo rótulo da tela.
- **Risco real do diagnóstico apressado**: "consertar" `derFlu_numVooOrigem`
  para `colVei_numVooOrigem` quebraria a tela, porque em `14.4-tbl_ColVeiculos`
  esse interno é, na verdade, `colVei_descOcorrencia`. O nome "óbvio" não existe.

Prevenção (implementada em `SAFETY/build/checar_escopo_safety.py`): validar toda
coluna citada contra a **união** de nomes internos e de exibição extraída do
`DataEntityMetadataJson` da lista. Reprovar por prefixo é falso positivo; o que
reprova de verdade é o nome não existir em nenhuma das duas formas.

Impacto global: antes de tratar `<prefixo alheio>_<campo>` como bug de cópia em
qualquer projeto deste workspace, abrir `References/DataSources.json` e conferir
se aquele é o nome interno da própria lista.

### "Nenhum tipo encontrado para a variável X" — contexto do Navigate × Set global (2026-09-24)

- Data: 2026-09-24. Projeto/tela: SAFETY / as 7 telas de lista dos módulos
  (`ScreenColisaoVeiculos` e irmãs). Erro visto no Studio, em produção.
- Mensagem completa:

  ```text
  Nenhum tipo encontrado para a variável 'var_registroColVei'. Certifique-se de
  que ela esteja Set como um valor que não esteja em Blank em algum lugar no
  aplicativo.
  ```

- Causa confirmada: dois botões da MESMA tela alimentavam os MESMOS nomes por
  mecanismos diferentes —

  ```powerfx
  // botão "Editar" — 3º argumento do Navigate cria variável de CONTEXTO
  Navigate(ScreenColisaoVeiculosForms, ScreenTransition.Fade,
           {var_editandoColVei: true, var_registroColVei: ThisItem})

  // botão "Cadastrar" — Set cria variável GLOBAL
  Set(var_editandoColVei, false); Set(var_registroColVei, Blank())
  ```

  São **duas variáveis distintas com o mesmo nome**. A global só recebia
  `Blank()`; sem nenhum valor tipado em lugar nenhum, o Studio não infere o tipo.

- Agravante silencioso, pior que o erro: os `Default` do formulário liam
  `var_registro<K>.<coluna>`. Qual das duas o controle enxerga depende do
  escopo — o formulário só tinha dado vindo pelo caminho do "Editar".
- Correção: o "Editar" passou a `Set(var_editando<K>, true); Set(var_registro<K>,
  ThisItem);` **antes** do `Navigate`, e o `Navigate` perdeu o 3º argumento.
  Nenhuma fórmula de controle mudou — os nomes continuam os mesmos, só deixam
  de ser de contexto.
- Validação preventiva (`SAFETY/build/checar_variaveis.py`, reaproveitável):
  1. varrer todo `Set(nome, valor)` do app e reprovar nome cujo conjunto de
     valores seja **somente** `Blank()`;
  2. reprovar nome usado como contexto de `Navigate` que também apareça em
     `Set()` em qualquer tela.

  Rodado contra a versão anterior do arquivo, reproduz exatamente a mensagem do
  Studio — antes da colagem.
- Impacto global: esse par é **indetectável tela a tela**; o Verificador de
  fórmula de cada controle passa. Só aparece varrendo o app inteiro. Vale para
  qualquer projeto que use `Navigate` com contexto.

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

## Casar pessoa por nome de exibição é casar por chave instável — e o remédio abre um segundo buraco (2026-09-02)

- Projeto/tela: Gestão de Chamados / `ScreenServiceDeskForm`, ramo `RESET_SENHA`
  do `OnSuccess`.
- Sem erro do Studio: o defeito só aparece em produção, e como um falso
  "usuário não localizado".

O `OnSuccess` casava o solicitante com o cadastro por
`LookUp(User; usrNome = varDeskUsuario)`, onde `varDeskUsuario` é o
`DisplayName` do campo Pessoa. **Nome de exibição do AAD e `usrNome` da lista são
duas grafias da mesma pessoa mantidas por processos diferentes** — abreviação,
nome social, sobrenome de casada, acento. Quando divergem, o `LookUp` volta
branco, o `Error()` sobe e o usuário vê a falha **depois** de o chamado já estar
gravado. O e-mail da pessoa está disponível nas duas pontas (`.Email` do campo
Pessoa, coluna `Email` da lista) e é a única chave estável entre elas.

**A troca ingênua da chave introduz um bug pior que o original.** Trocar só o
`LookUp` deixa isto:

```powerfx
With({locUsr: LookUp(User; Email = varDeskUsuEmail)};
    If(IsBlank(locUsr); Error(...); Patch(User; locUsr; {Senha: varNovaSenha})))
```

Se `varDeskUsuEmail` vier branco, `Email = Blank()` **casa** com o primeiro
registro de `User` que estiver com o e-mail vazio — `locUsr` não é branco, a
guarda não dispara, e a senha temporária é aplicada **na conta errada**. É a
lição `Blank() = 0` na versão texto: branco não é "não casa com nada", é um valor
que casa com outros brancos.

**Correção:** a guarda cobre a chave antes de cobrir o resultado.

```powerfx
If(IsBlank(varDeskUsuEmail) Or IsBlank(locUsr); Error(...); Patch(...))
```

`Or` curto-circuita antes de olhar o registro, e o `LookUp` continua delegável —
nada de `IsBlank()` dentro do `Filter`/`LookUp`, que derrubaria a delegação.

**Regra:** todo `LookUp` que ancora uma **escrita sensível** exige as duas
guardas — *a chave de busca não pode estar em branco* e *o registro tem que ter
sido achado*. Uma sozinha não cobre a outra: a segunda deixa passar o casamento
branco-com-branco, e a primeira não prova que achou.

**Verificação para as próximas telas:** procurar todo `LookUp(<lista>; <col> =
<var>)` cujo resultado alimenta um `Patch` de coluna sensível (senha, papel,
autorização, valor financeiro) e exigir um `IsBlank(<var>)` no caminho, não só o
`IsBlank(<registro>)`. E procurar todo casamento entre fonte externa e lista
local feito por nome — `usrNome = <DisplayName>`, `usrNome = User().FullName` —
e trocar por e-mail. `SAFETY/msapp/Src/App.pa.yaml:204` ainda tem essa segunda
forma; é o mesmo risco, em outro módulo.

## `": "` dentro de string Power Fx quebra o YAML — mas só em propriedade de linha única (2026-09-03)

- Data: 2026-09-03. Projeto/tela: DueDiligence / `ScreenDueDiligence` (motor v2).
- Mensagem (pega em lint local com PyYAML, antes de chegar ao Studio):
  `mapping values are not allowed here`, apontando para o `.` de
  `Placeholder: ="Ex.: 250000"`.

Causa confirmada: no Source Code, o valor de cada propriedade de linha única é um
**plain scalar YAML não citado** — as aspas duplas ali dentro são caracteres
literais do Power Fx, não citação YAML. Plain scalar não pode conter `": "`
(dois-pontos seguido de espaço): o parser interpreta como um mapeamento aninhado
e recusa o arquivo inteiro. O `"Ex.: 250000"` do placeholder tinha exatamente
essa sequência.

A regra tem duas metades, e é fácil registrar só uma:

1. **Propriedade de linha única** (`Placeholder: ="..."`, `Text: ="..."`):
   nenhuma string Power Fx pode conter `": "`. Reescrever o texto (`"Ex. 250000"`)
   ou promover a propriedade a bloco `|-`.
2. **Bloco literal `|-`** (`HtmlText: |-`, `OnSelect: |-`): tudo é texto literal
   para o YAML — `": "` é livre. É por isso que os HTMLs gigantes com
   `style='font-size:11px'` e textos como `"Referência de risco alto: "` sempre
   funcionaram: estavam todos dentro de `|-`.

Correção aplicada: placeholder trocado para `"Ex. 250000"`.

Validação preventiva: rodar `yaml.safe_load` (com o constructor para a tag
`tag:yaml.org,2002:value`, que o valor `=` sozinho exige) sobre o arquivo antes
de entregar — foi esse lint que pegou o erro. Para checagem dirigida: em toda
linha `Chave: =...` (fora de bloco `|-`), reprovar a sequência `": "` dentro do
valor.

Impacto global: qualquer gerador/tela que escreva rótulos, placeholders ou
mensagens com dois-pontos em propriedade de linha única. Vale também para
`Tooltip:`, `InputTextPlaceholder:` e `Text:` de labels.

## `<Validation>` no List_Generator: fórmula localizada (`OU`/`;`) é recusada pelo `CreateFieldAsXml` (2026-09-04)

- Projeto/lista: DueDiligence / `tb_dueDiligenceTerceiroRespostas`, coluna `ativo`.
- Sintoma: o fluxo `List_Generator` roda, cria a lista, cria as primeiras colunas
  e **falha numa coluna com `BadGateway`**. O erro do conector é genérico e não diz
  nada — a causa real só aparece no `body` do OUTPUTS do passo `HTTP Criar Coluna`:

```text
statusCode 502 · SPException -2130575270
"Não há suporte para a fórmula ou ela contém um erro de sintaxe."
source: .../_api/web/lists(guid'...')/fields/CreateFieldAsXml
```

XML que causou:

```xml
<Field Type='Number' DisplayName='ativo' ... Required='TRUE'>
  <Default>1</Default>
  <Validation Message='use 1 ou 0'>=OU([ativo]=0;[ativo]=1)</Validation>
</Field>
```

Causa confirmada: a fórmula com **nome de função localizado e separador `;`**
(`=OU(...;...)`, padrão pt-BR) foi rejeitada pelo SharePoint neste tenant. A
`SKILL.md` do `list-generator` orienta "na dúvida, pt-BR" — mas a interface do
SharePoint aparecer em português é **preferência de idioma do usuário**, não o
locale do site; o `CreateFieldAsXml` avalia a fórmula pelo locale do *site*.
Nenhuma das listas criadas antes na mesma sessão (`tb_dueDiligence`,
`tb_dueDiligenceParametros`) tinha `<Validation>` — por isso passaram, e por isso
o problema só apareceu na primeira lista que de fato usou fórmula.

Correção aplicada: **remover o `<Validation>`**. As colunas `ativo` das duas listas
irmãs já existiam sem validação nenhuma, então tirar deixou o schema consistente e
não custou nada — o app/fluxo sempre grava `1` ou `0` explicitamente. `<Default>1</Default>`
foi mantido: valor literal não é fórmula e não dispara o erro.

Prevenção:

1. **`<Validation>` é opcional — só usar quando houver ganho real.** Guardrail
   contra digitação manual no SharePoint não compensa arriscar o provisionamento
   inteiro, ainda mais porque o fluxo falha no meio e deixa a lista pela metade.
2. Se for mesmo necessário, **não assumir o locale**: criar a coluna à mão pela UI
   do SharePoint uma vez, exportar/inspecionar o XML gerado e usar exatamente
   aquela sintaxe (`OR`/`,` num site en-US, `OU`/`;` num pt-BR).
3. Quando o `List_Generator` devolver `BadGateway`, **nunca parar no erro do
   conector** — abrir `HTTP Criar Coluna` → Run results → OUTPUTS → `body` →
   `innerError.message`. É lá que está o motivo real; o `BadGateway` é só o
   envelope.
4. Falha no meio do loop `Para cada Coluna` deixa a lista **parcialmente criada**.
   Se ela ainda não tem dados, o caminho limpo é excluir a lista e rodar de novo
   com o JSON corrigido — reexecutar por cima gera erro de coluna duplicada.

## Power Automate: `trigger.conditions` exige objetos com `expression` (2026-09-08)

- Projeto/fluxo: DueDiligence / `Enviar questionário Due Diligence`.
- Erro na importação: `MalformedFlowAssetFlowDefinition` — “A definição de fluxo
  para o ativo `88fccf2d-dc50-421b-b4a1-8061581e1091` não pôde ser
  desserializada.” Tracking ID:
  `61ae0a77-326e-4383-b5c0-fb81a5a9b08c`.

Causa confirmada: o pacote gerado escreveu a condição do gatilho como uma lista
de strings:

```json
"conditions": ["@and(...)"]
```

Na Workflow Definition Language, cada entrada de `conditions` é um objeto JSON
com a propriedade `expression`. A forma correta é:

```json
"conditions": [
  {
    "expression": "@and(...)"
  }
]
```

O JSON era sintaticamente válido, por isso `json.loads` e a verificação do ZIP
passaram, mas o ativo não correspondia ao contrato tipado esperado pelo Power
Automate e falhou antes de criar/atualizar o fluxo.

Correção aplicada no gerador `DueDiligence/build_power_automate_flows.py` e no
pacote DD01. Validação preventiva adicionada a
`DueDiligence/validar_due_diligence.py`: toda entrada de
`trigger.conditions` agora precisa ser um objeto com `expression` textual. A
mesma validação também rejeita `Terminate` dentro de `Foreach` e expressões WDL
com literais/delimitadores malformados.

## Microsoft Forms: parâmetro na URL não preenche sem ativar `AllowPrefill` (2026-09-09)

- Projeto/fluxo: DueDiligence / `Enviar questionário Due Diligence` (DD01).
- Sintoma: o e-mail contém o código na URL, por exemplo
  `&rf6e...=<forms_envio_id>`, mas a pergunta obrigatória
  `Código de acompanhamento` abre vazia no Microsoft Forms.

Causa confirmada: o link foi montado a partir da URL comum do formulário. O
runtime público retornou as configurações do formulário sem `AllowPrefill`, e o
DD01 também não informava `origin=lprLink`. O Forms preserva parâmetros
desconhecidos na barra de endereço, mas só aplica respostas da query string
quando o proprietário habilita o recurso de URL pré-preenchida.

Correção:

1. No formulário, usar `...` → `Obter URL pré-preenchida`, preencher a pergunta
   de controle com um valor de teste e gerar o link uma vez. Isso habilita o
   preenchimento no formulário.
2. Montar links dinâmicos com `&origin=lprLink` antes dos pares
   `<question-id>=<valor codificado>`.
3. Manter o valor dinâmico protegido por `uriComponent()` no Power Automate.

Prevenção adicionada: `DueDiligence/validar_due_diligence.py` reprova o pacote
DD01 quando `origin=lprLink` não está presente. A ativação de `AllowPrefill`
continua sendo uma configuração externa do Microsoft Forms e deve constar do
checklist de implantação.

## SharePoint REST: `responseId` do Forms precisa de `string()` em coluna Text (2026-09-09)

- Projeto/fluxo: DueDiligence / `Processar resposta Due Diligence` (DD02), ação
  `HTTP Criar Item Resposta`.
- Erro: HTTP 400, `Microsoft.SharePoint.Client.InvalidClientQueryException` —
  `Cannot convert a primitive value to the expected type 'Edm.String'`.
- Endpoint: lista `tb_dueDiligenceTerceiroRespostas`.

Causa: o gatilho do Forms pode devolver `resourceData/responseId` como número,
mas `forms_resposta_id` e `forms_ultima_resposta_id` são colunas SharePoint
`Text`. O objeto de criação repassava o valor bruto para `forms_resposta_id`.
Embora o JSON seja válido, o OData não converte automaticamente esse primitivo
numérico para `Edm.String`.

Correção aplicada: envolver `responseId` com `string()` e tipar explicitamente
todos os campos `Text`/`Note` do objeto `Montar_Item_Resposta`. A mesma conversão
foi aplicada a `forms_ultima_resposta_id`, que seria gravado posteriormente na
solicitação principal.

Prevenção: o validador agora deve inspecionar `Montar_Item_Resposta` e reprovar
o DD02 se qualquer campo textual dinâmico perder o `@string(...)`; também deve
verificar a conversão de `forms_ultima_resposta_id`.

## Status de fila não pode bloquear a ação da área responsável (2026-09-09)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`.
- Sintoma: o Power Automate processava o Forms, criava o histórico e mudava a
  solicitação para `Pendente Compliance`, mas a ação `Editar` permanecia
  desabilitada. A analista conseguia visualizar a solicitação, porém não havia
  caminho para iniciar a análise ou emitir parecer.

Causa confirmada: `tbDdAcoes.Items` incluía todos os estados internos de
Compliance diretamente em `ItemDisabled`, junto dos estados terminais. O
próprio tooltip dizia que o perfil ainda precisava ser configurado. O formulário
de desdobramento existia, mas era inalcançável nesses estados; as respostas do
terceiro também não eram renderizadas na tela.

Correção aplicada:

1. Manter `varDdPodeAnalisarCompliance` bloqueado até a fonte real de
   autorização do app ser confirmada; não inferir lista ou variável de outro
   módulo do workspace.
2. Exibir a ação `Analisar` nos estados internos somente para esse perfil,
   mantendo o formulário do solicitante em `ViewForm`.
3. Mostrar as respostas de `tb_dueDiligenceTerceiroRespostas` do envio atual.
4. Gravar decisão, justificativa, condicionantes, autor, data e prazo de
   reavaliação nos campos estruturados da solicitação, além do histórico.
5. Exibir notas internas apenas ao perfil Compliance; os demais usuários veem
   somente desdobramentos com `visivel_solicitante = 1`.

Prevenção adicionada a `DueDiligence/validar_due_diligence.py`: a tela deve ter
guarda de perfil no toolbar e no evento, respostas do terceiro visíveis, decisão
estruturada persistida e histórico interno segregado. Regra geral: estado de
fila e estado terminal são categorias diferentes; não devem compartilhar uma
lista única de bloqueio de edição.

## Variável criada numa tela não é contrato global do app (2026-09-09)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`.
- Mensagem do Studio: `O nome não é válido. 'userRecord' não é reconhecido.`
- Fórmula afetada: inicialização de `varDdPodeAnalisarCompliance` no
  `OnVisible`.

Causa confirmada: a autorização foi implementada lendo diretamente
`userRecord.Area`, `userRecord.Funcao` e `userRecord.Perfil`. `userRecord` é um
registro temporário criado durante o login em outra implementação; ele não faz
parte do contrato global garantido para a tela importada. A tentativa seguinte
de usar `varIdUser`, `varFuncaoUser` e `varPerfilUser`, encontrada em outro app
do workspace, também não era uma prova de que esses nomes existiam no app de
destino.

Correção aplicada: remover todas as dependências de identidade não comprovadas
e manter `varDdPodeAnalisarCompliance: false` até o responsável informar a
fonte real de autorização. Esse padrão falha fechado: bloqueia a ação sem
conceder acesso indevido.

Validação preventiva: `DueDiligence/validar_due_diligence.py` agora reprova
`userRecord`, a lista `User` inferida e as variáveis de login não comprovadas;
até a fonte ser definida, exige o bloqueio explícito. Regra global: antes de
reutilizar uma variável ou fonte encontrada em outra tela, confirmar no próprio
app de destino que ela existe; referência em outro projeto do workspace não é
contrato.

## Fonte de dados de outro app não existe por herança (2026-09-09)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`.
- Mensagem do Studio: `O nome não é válido. 'User' não é reconhecido.`
- Erros associados no mesmo trecho: `ID`, `varIdUser`, `Area`,
  `varFuncaoUser` e `varPerfilUser` também não reconhecidos.

Causa confirmada: `User` era uma lista SharePoint usada por outro aplicativo do
workspace. Fontes de dados, conectores e variáveis globais não são herdados
quando uma tela é colada em outro app. Inspecionar um módulo vizinho comprova o
contrato daquele módulo, não o contrato do destino.

Correção aplicada: retirar a consulta e deixar a autorização em `false` até a
fonte real dos usuários do Compliance ser indicada. Não usar `User().Email`
com uma lista de endereços inventada, nem liberar todos temporariamente.

Validação preventiva: o validador bloqueia os nomes inferidos e exige modo
fechado enquanto `PREENCHER_FONTE_PERFIL_COMPLIANCE` estiver pendente. Impacto
global: toda tela importável que tenha controle de acesso precisa declarar sua
dependência de identidade no checklist de implantação; quando a dependência não
for fornecida, deve compilar em modo somente leitura.

## Status técnico não é status de negócio — e o `catch` tem que consumir a intenção (2026-09-10)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`, fluxos DD01, DD02 e DD03.
- Origem: o Compliance reduziu o ciclo a oito status. Não é erro do Studio: são
  dois defeitos encontrados ao aplicar a mudança.

**1. Remover o status de erro reabriria um reenvio automático.** O DD01 dispara
em "item criado ou modificado" com a condição
`forms_envio_id <> forms_envio_processado_id`. O `catch` só gravava
`status = Erro no envio ao terceiro`; era o status, e não os IDs, que impedia o
disparo seguinte. Sem esse status, a intenção continuaria aberta e qualquer
alteração posterior no item (uma nota do Compliance, por exemplo) reenviaria o
e-mail sem ninguém pedir.

Correção: o `catch` grava `forms_envio_processado_id = forms_envio_id` e deixa
`data_envio_terceiro` vazia. O app deriva "em processamento" (IDs diferentes) e
"falha no envio" (IDs iguais e data vazia) e limpa a data a cada reenvio. O
sucesso deixou de regravar `status`, para não desfazer um cancelamento feito
entre a leitura e a gravação.

**2. Qualquer usuário em modo edição podia aprovar.** Fora dos estados de
Compliance, `cmbDdDesdStatusNovo` oferecia todos os status, e `Parecer final`
estava sempre no combo de tipo. Quem abrisse uma solicitação em
`Aguardando envio ao terceiro` ou `Erro no envio ao terceiro` podia registrar
`Parecer final` com `Aprovado`. Correção: o painel de registro só aparece para
`varDdPodeAnalisarCompliance`, e o status oferecido é derivado do tipo
(`Parecer final` → decisões, `Cancelamento` → `Cancelado`, demais → status
atual).

Validação preventiva em `DueDiligence/validar_due_diligence.py`: literais de
status legados reprovam em telas e fluxos; o filtro tem que listar exatamente os
oito status; o `catch` do DD01 tem que consumir a intenção e o sucesso não pode
gravar `status`; os tipos manuais de desdobramento são uma lista fechada; a
regra de vigência (1/2/3 anos) tem que ser a mesma no app e no DD03.

Impacto global: todo fluxo com gatilho "criado ou modificado" e condição de
intenção precisa que **todos** os ramos, inclusive o de erro, fechem a
intenção. Estado técnico de fila (enviando, erro de envio) cabe num campo
derivado; status é vocabulário de negócio e pertence a quem decide.

## `Average` sobre tabela vazia é erro, não branco — e apaga o `HtmlText` inteiro (2026-09-10)

- Projeto/tela: DueDiligence / `ScreenDueDiligencePainel`, `htmDdPainelLinha3.HtmlText`.
- Mensagem do Studio: `A função Average não pode ser usada com uma tabela
  vazia`, sublinhando `Average(_anal; dias)`.

Causa confirmada: com os dados de teste, nenhuma solicitação do período tinha
resposta do terceiro e parecer, então `_anal` estava vazia. `Average` de tabela
vazia devolve **erro** (é uma divisão por zero), não `Blank()`. As medianas
logo acima usavam a mesma tabela e não acusaram nada, porque já estavam
protegidas por `If(_nAnal = 0, Blank(), ...)` — é essa diferença que confirma a
causa. Como o erro atravessa a concatenação do HTML, o cartão inteiro ficaria
vazio em qualquer período sem pareceres.

Correção: média calculada como `If(_n = 0, Blank(), Sum(t, col) / _n)`; `Max`
sobre tabela passou a `If(IsEmpty(t), 1, Max(t, col))`; o aviso de corte trocou
`Max(colDdPainelLotes, qtd)` por `CountIf(colDdPainelLotes, qtd >= 500) > 0`.
`Coalesce` não resolvia: ele pula branco, mas devolve o erro adiante.

Validação preventiva em `DueDiligence/validar_due_diligence.py`: o painel
reprova `Average(` e qualquer `Max`/`Min`/`Sum` sobre tabela sem `IsEmpty(t)` ou
contagem zero logo antes.

Impacto global: todo painel que agrega coleção recortada por período ou filtro
pode receber tabela vazia. Proteger o agregado com `If` **antes** de chamá-lo.
Conferir `Frotas/scrFrotaPainel` (`Max(Max(colDistAero, Qtd), 1)`) e o painel de
chamados.

## `Text(x, "0%")` não multiplica por 100: 33% aparece como "0%" (2026-09-10)

- Projeto/tela: DueDiligence / `ScreenDueDiligencePainel` — legenda de risco,
  percentuais das barras e medidores de SLA.
- Sintoma relatado pelo usuário: "1 0%", "0 0%", "2 1%" na legenda de risco e
  "1 0%" em todas as barras. Nenhum erro no Studio.

Causa confirmada: no Power Apps o `%` do formato de `Text()` não multiplica por
100 como no Excel — o valor é arredondado e o `%` entra como texto. A legenda
tinha Baixo 1, Médio 0 e Alto 2 (proporções 0,33, 0 e 0,67) e mostrou
exatamente "0%", "0%" e "1%". A prévia HTML não pegou o defeito porque o gerador
da prévia calculava o percentual em Python, e não com a fórmula da tela.

Correção: `Text(Round(x * 100, 0)) & "%"`, com "<1%" quando a parcela existe mas
arredonda para zero e "—" quando a contagem é zero. As larguras das barras já
usavam `x * 100` e estavam certas; só os rótulos erravam.

Validação preventiva: `DueDiligence/validar_due_diligence.py` reprova qualquer
formato `"0%"`, `"0.0%"` ou `"#%"` nas telas do módulo.

Impacto global: `Frotas/scrFrotaPainel` usa `Text(locDisponivel / locTotal, "0%")`
no KPI de disponíveis — mesmo padrão, conferir. Regra: prévia montada fora do
Power Apps não prova formatação; o número tem que ser conferido na tela real.

## `" #"` em propriedade de linha única vira comentário YAML e corta a fórmula (2026-09-15)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`, `htmlDdHistoricoVazio.HtmlText`.
- Sintoma: depois de colar a tela, o Studio acusa "Caracteres inesperados" e
  "Valor Text esperado". A fórmula aparece cortada em
  `...background:#f9fafb;border:1px dashed`, sem o resto do HTML e sem a aspa final.

Causa confirmada: a propriedade estava em linha única
(`HtmlText: ="<div style='...;border:1px dashed #d1d5db;...'>...</div>"`). Em
escalar YAML sem aspas, espaço seguido de `#` abre comentário: tudo a partir de
` #d1d5db` foi descartado na colagem. O `background:#f9fafb` passou porque o `#`
vem colado aos dois-pontos, sem espaço antes.

É a regra irmã do `": "` (seção de 2026-09-03), com uma diferença que a torna
pior: comentário é YAML válido, então o `yaml.safe_load` **não reclama** — só
entrega o valor truncado. O defeito ficou no repositório desde a primeira
versão, e o export do Studio devolveu o texto já cortado, que parecia edição do
usuário.

Correção: promover a propriedade a bloco `|-`, onde `#` é texto literal.

Validação preventiva (`DueDiligence/validar_due_diligence.py`):
1. em toda linha `Chave: =...` fora de bloco `|-`, reprovar espaço ou tab
   seguido de `#`;
2. depois do parse, reprovar fórmula com string ou identificador citado ainda
   aberto no fim — pega qualquer truncamento, venha de onde vier.

Impacto global: HTML e cores `#RRGGBB` escritos em linha única, em qualquer
tela gerada. Cor dentro de `RGBA(...)` não tem o problema; `"... #fff"` com
espaço antes tem.

## `IfError(Patch(...), Notify(...))` só aceita tipos diferentes fora de ramo de `If` (2026-09-15)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`, `frmDdDesdobramento.OnSuccess`
  (histórico da reclassificação de risco).
- Sintoma: "Tipo de argumento inválido (Boolean). Esperando um valor Record, em
  vez disso", apontando o `Notify` do fallback.

Causa confirmada pela comparação com a mesma tela: `IfError(Patch(...),
Notify(...))` mistura Record (`Patch`) e Boolean (`Notify`). O Studio aceita
quando o `IfError` é elo de uma cadeia `;` (ex.: primeiro comando do corpo de um
`With`), e o `frmDdSolicitante.OnSuccess` usa exatamente isso há semanas. Dentro
de um ramo `If(condição, IfError(...))`, o resultado precisa de tipo único e o
Studio recusa.

Correção: `If(condição, If(IsError(Patch(...)), Notify(...)))`. `IsError`
devolve Boolean em qualquer posição e já estava comprovado em
`Mapa de Alocação/scrMapaPatio`.

Validação preventiva (`DueDiligence/validar_due_diligence.py`, grupo "IfError
aninhado com tipos compatíveis"): reprovar `IfError(Patch|Remove|Collect(...))`
quando ele é argumento direto de `If`/`Switch`. Os 14 usos comprovados, em cadeia
ou corpo de `With`, continuam passando.

Impacto global: qualquer `IfError` de gravação escrito como ramo de `If`. Na
dúvida, `If(IsError(...), ...)`.

## Motor com resultado vazio e fluxo que exige valor: solicitação trava sem erro (2026-09-16)

- Projeto/tela: DueDiligence / `ScreenDueDiligence` + fluxos DD01/DD02.
- Achado de auditoria, ainda sem ocorrência relatada.

O motor de fluxo terminava em `""` quando a classificação da contraparte não
batia com nenhum ramo, e a categoria era identificada pelo **texto** exibido
("Fornecedor", "Órgão da administração pública"). Uma edição de texto na lista
de parâmetros deixava o fluxo vazio. O app gravava `Aguardando Terceiro`; o DD01,
que só confere status e IDs, enviava o Forms; o DD02, que exige `FLUXO III`,
recusava a resposta. Resultado: solicitação parada, sem erro visível para
ninguém.

Regras que ficam:
1. **Motor de decisão não termina em vazio.** O ramo "não identificado" escolhe
   o caminho seguro (aqui, análise do Compliance) e fica visível.
2. **Pré-condição de um fluxo tem de ser garantida por quem grava.** Se o DD02
   exige `FLUXO III` para `Aguardando Terceiro`, o app não pode gravar esse
   status com outro fluxo, e a tela deve apontar registros que já estão assim.
3. **Comparar parâmetro pelo código estável, nunca pelo rótulo.** O rótulo é
   editável na lista; o código é contrato.

Mesma auditoria, lado da interface: um resumo com três estados ("aguardando",
número, sim/não) mostrava "AGUARDANDO" em aprovação automática, que nunca terá
resposta. Cartão de status precisa de um estado explícito "não se aplica" e
precisa ler o valor **gravado** quando a tela está em visualização.

## Nome interno com mais de 32 caracteres: o formulário não grava e não avisa (2026-09-16)

- Projeto/lista: DueDiligence / `tb_dueDiligence`, colunas
  `gatilho_representacao_orgao_publico` (35) e
  `gatilho_indicado_funcionario_publico` (36).
- Sintoma relatado: registro criado com as respostas preenchidas; ao abrir em
  Ver ou Editar, as duas perguntas voltavam vazias. Nenhum erro no Studio nem na
  gravação.

Causa: o SharePoint limita o nome interno a 32 caracteres e corta o excedente,
mesmo com `AddFieldInternalNameHint` no `CreateFieldAsXml`. O nome de exibição
continua inteiro. As fórmulas (`ThisItem.coluna`, `DataSourceInfo`) resolvem
pelo nome de exibição e funcionam; o `DataField` do card é o nome interno. Com o
nome inteiro, o card não corresponde a nenhuma coluna e o `SubmitForm`
simplesmente não grava o valor. A prova veio do próprio print: o campo vizinho,
de 25 caracteres, gravou "Sim"; só os dois acima de 32 ficaram vazios.

Correção: `DataField` com o nome cortado (`gatilho_indicado_funcionario_pub`),
mantendo as fórmulas com o nome de exibição.

Validação preventiva:
- `.claude/skills/list-generator` (regra e `scripts/validar_json.py`): reprovar
  `internalName` com mais de 32 caracteres;
- `DueDiligence/validar_due_diligence.py`: reprovar `DataField` acima de 32 e
  comparar os `DataField` com o nome interno efetivamente gravado.

Impacto global: toda lista gerada antes da regra. A varredura de 2026-09-16 só
achou essas duas colunas no repositório.

## Cirurgia por regex sobre texto mascarado: o literal some da busca e do resultado (2026-09-17)

Projeto Inspeções, `build/gerar_leve.py`. Para não tocar em código comentado nem em
strings, o gerador localiza os padrões numa cópia **mascarada** do YAML (strings e
comentários viram espaços, posições preservadas) e aplica a troca no texto original.
Três armadilhas pagas nesse dia:

1. **O padrão não pode citar o conteúdo de uma string.** `'7.4-tbl_InspPista'` e
   `"ID"` viram `'                '` e `"  "` na busca: casam zero vezes. O padrão
   escreve `'[^']*'` / `"[^"]*"` e o literal de verdade é conferido à parte, num
   regex `verificar` aplicado ao trecho **original** de cada match — match que não
   confirma o literal é pulado, não substituído (o mesmo padrão casava o rótulo
   certo `"-INSP-TPS-ITEM-"` e o errado `"-INSP-PAT-ITEM-"`).
2. **Grupo capturado tem de vir do texto original**, nunca do mascarado — senão a
   substituição injeta os espaços da máscara no lugar do literal.
3. **Grupo de indentação é `[ \t]*`, não `\s*`.** `(\n(\s*))ForAll\(` engoliu a
   linha de comentário acima do `ForAll` (mascarada, ela é só espaços), e o
   comentário reapareceu três vezes no resultado.

Regra irmã: identificador entre aspas simples (`'ID_item (ID_item0)'`) também é
mascarado — pelo mesmo motivo (o parêntese dentro dele quebraria o balanceamento).

## Contexto passado por `Navigate` é escrita na tela de DESTINO (2026-09-17)

`Navigate(frmX, transição, {var_a: 1})` escreve `var_a` no escopo de **frmX**, não da
tela que chama. Um checador de "variável escrita e nunca lida" que atribui essa
escrita à origem acusa falso positivo (a origem nunca lê mesmo) e deixa passar o
caso real (frmX não lê). O App Checker lista corretamente
`frmRelatorioVistoVeic.var_detalhaItens` como não usada embora a única escrita
esteja em `frmCheckListGenericoEQP`. Ao remover a variável morta, a chave sai do
registro do `Navigate` na tela de origem. Corolário: `UpdateContext` numa tela para
"preparar" outra (`Var_IDinspTPS` em frmHomeZPA antes de ir para frmHomeTPS) não faz
nada — variável de contexto não atravessa telas; só o terceiro argumento do
`Navigate` atravessa.

## `IsBlank(x) || StartsWith(col, x)` é só `StartsWith(col, Text(x))` (2026-09-17)

`StartsWith(col, "")` é verdadeiro para toda linha (lição 2026-08-31), então o guarda
`IsBlank(x) ||` não muda o resultado — só derruba a delegação. Trocar por
`StartsWith(col, Text(x))` (o `Text()` garante `""` quando o combo está vazio) é uma
reescrita **semanticamente idêntica** e delegável; não precisa do `Switch` de
`Filter`s, que só é necessário quando a condição não tem um "elemento neutro"
(ex.: `ID = Value(txt)`). Para datas o neutro é um piso/teto fixo:
`col >= Coalesce(dtp.SelectedDate, Date(2000, 1, 1))`.

## Preparar formulário de outra tela antes do `Navigate` não é confiável (2026-09-17)

`ResetForm(FormZpa); NewForm(FormZpa)` em frmHomeZPA, com `FormZpa` em frmFormZPA:
com `delayloadscreens` a tela de destino pode nem estar carregada, e a referência
força o carregamento dela inteira (App Checker `CrossScreenEventDependencies`). O
lugar da preparação é o `OnVisible` da tela de destino, guiado por um valor passado
no contexto do `Navigate` (`{var_zpa_modo: "novo"}`) e zerado no fim do próprio
`OnVisible`. Cópia entre telas deixa lixo do tipo `Reset(AddMediaButtonD3)` (controle
de outra tela) em telas que não têm nada a ver — remover.

## Entrega por lotes: allowlist com validade por lote (2026-09-17)

Quando a mesma origem gera entregas cumulativas (`entregar.sh A|AB|ABC|ABCD`), o que
é aceitável no lote B (referências entre telas que o lote D corrige) tem de reprovar
no lote D. Cada entrada de allowlist leva `"ate": "B"` ou `"desde": "C"`, e o
checador filtra pelo lote em curso (`LOTE` no ambiente). Entrada declarada que não
ocorre continua reprovando — inclusive quando "some" por ter mudado de lote.

## Cartão oculto na mesma linha do formulário empurra o campo visível (2026-09-18)

- **Projeto/tela:** DueDiligence, `ScreenDueDiligence` (`frmDdSolicitante`,
  `Form@2.4.4` com `SnapToColumns = false`).
- **Sintoma:** Aeroporto (`X=0`, `Y=0`) e Razão social (`X=1`, `Y=0`), cada um
  com meia largura, apareceram um embaixo do outro, os dois na coluna esquerda.
  A linha seguinte, com as mesmas larguras, saiu lado a lado.
- **Causa confirmada pelo print:** os 17 cartões ocultos (`Visible = false`) do
  formulário também estavam em `X=0`, `Y=0`, com `Width = Parent.Width`. Dentro
  da linha, os cartões seguem a ordem de `X` e depois a do YAML, e o formulário
  quebra a linha pela largura mesmo dos cartões ocultos: o primeiro oculto de
  largura total depois do Aeroporto quebrou a linha, e a Razão social (`X=1`, a
  última da fila) começou uma linha nova à esquerda.
- **Correção:** cartões ocultos numa linha só deles (`Y = 200`), longe da grade
  visível. Não muda nada na tela nem na gravação.
- **Validação preventiva:** grupo "Linhas do formulário sem cartão oculto" no
  `validar_due_diligence.py`: nenhum cartão com `Visible = false` pode ter o
  mesmo `Y` de um cartão visível.

## Anexo com `Items.Value = Id` abre endereço inexistente (2026-09-17)

- **Projeto/tela:** DueDiligence, `ScreenDueDiligence` (galeria do histórico,
  controle `Attachments@2.3.0`).
- **Sintoma:** clicar no anexo abre
  `https://pafeblobprod….blob.core.windows.net/…/web/%252fLists%252f…` e o
  navegador mostra `BlobNotFound`. Nenhum erro no app nem no Verificador.
- **Causa confirmada:** o controle abre o que estiver em `Items.Value`. Com
  `=Id`, o valor é o caminho interno do arquivo no SharePoint, que o Power Apps
  procura no armazenamento temporário dele — onde o arquivo não existe. O
  mapeamento foi feito pelo painel de propriedades do Studio, não por fórmula.
- **Correção:** `Items.Value: =AbsoluteUri`, o endereço completo do arquivo no
  SharePoint. `=Value` também abre, mas passa pelo cache do Power Apps, que
  expira; `AbsoluteUri` é permanente.
- **Validação preventiva:** grupo "Anexos abrem pelo link do SharePoint" no
  `validar_due_diligence.py`: todo controle `Attachments@*` das telas precisa ter
  `Items.Value` vazio (padrão) ou `=AbsoluteUri`.

## Converter escalar entre aspas em bloco `|-` pode mudar a fórmula sem nenhum checador ver (2026-09-17)

O Studio grava como `"=...\n..."` (escalar entre aspas) toda fórmula que tem uma linha
só de espaços ou que termina em quebra de linha — o emissor YAML dele nunca escreve
esses casos como bloco. Para cirurgia, o gerador converte em bloco `|-`, e dois
detalhes mudam o valor:

- linha só de espaços escrita como linha vazia perde os espaços (`'    '` vira `''`);
- `|-` corta a quebra final; valor que termina em uma quebra precisa de `|`.

Escrever a linha só de espaços com a indentação do bloco + os espaços é YAML válido e
relê o valor exato; leitores e escritores de bloco usam uma regra só: ao ler,
`linha[base:]`; ao escrever, indentar toda linha não vazia. A conversão se prova
relendo o bloco com um parser YAML (documento terminado em `\n`, como no arquivo
real) e, se não bater, deixa a propriedade entre aspas como o Studio gravou.

Pior que o espaço perdido: o leitor de propriedade de linha única devolvia o escalar
entre aspas **cru**, com `\n` e `\"` literais. O corpo de um relatório HTML foi movido
assim para o `OnSelect` e passou pelo checador de sintaxe; só apareceu porque uma
entrada de allowlist parou de ocorrer. Leitor tem de decodificar o escalar (ou
abortar), e troca de texto num escalar entre aspas tem de abortar.

Checadores que olham texto não veem nada disso. Comparar **por valor** (os dois lados
lidos como YAML, propriedade a propriedade) pega: (1) propriedade que muda só em
espaço em branco é sempre efeito colateral do ferramental; (2) numa propriedade com
mudança real, trecho de linhas em branco que ganhou ou perdeu espaços também; (3) o
conjunto de propriedades alteradas/novas/removidas é gravado numa lista revisada por
lote e qualquer diferença reprova (`build/checar_valores.py`).

## Hora e minuto em dropdown: branco vira 00:00 em três lugares, e filtrar a lista não valida ordem (2026-09-18)

- Projeto/tela: REA (Resposta à Emergência) / `ScreenAPH`, 9 horários do formulário de APH, cada um com data + dropdown de hora + dropdown de minuto.
- Sintoma relatado: os operadores "erram muito" a sequência de horas. Nenhum erro do Studio. Uma remoção com chegada 14:31, saída 14:32 e retorno 14:33 foi aceita, e a galeria tinha registro às 00:00.

Causa confirmada pela leitura do export. São três defeitos independentes que produzem 00:00 sem ninguém escolher:

1. **`Update` com `Value(Hora.Selected.Value)`.** Com a hora em branco, `Value(Blank())` é 0, e o card grava a data às 00:00. O `Required` do card não pega, porque o `Update` nunca fica em branco quando a data está preenchida (e a data nasce preenchida).
2. **`DefaultSelectedItems: [Text(Hour(Parent.Default), "00")]` em modo edição.** Num registro antigo sem aquele horário, `Hour(Blank())` é 0, e o dropdown **mostra "00"**. A validação do botão (`IsBlank(Hora.Selected.Value)`) passa e o Salvar grava um horário que ninguém digitou.
3. **Default de registro novo `[0]` (número) contra itens de texto (`"00"`).** O resultado depende de como o controle trata o valor que não casa. Não é contrato.

E a ordem era "garantida" filtrando as opções de cada lista pelo campo anterior (`Value(Value) >= hora_anterior - 1`). Isso não valida nada:

- a folga de −1 h e o filtro de minuto só com hora igual aceitam 13:55 depois de 14:50;
- depois da meia-noite o "00" some, porque a data do campo seguinte nasce igual à do primeiro;
- corrigir um campo de cima tira da lista a hora já escolhida embaixo;
- no bloco "em voo" o filtro estava invertido em relação à ordem da tela.

Correção aplicada (`REA/build/gerar_aph.py`):

- `Update` só monta a data/hora quando data, hora e minuto estão preenchidos e o card está visível; senão devolve branco e o `Required` passa a funcionar;
- `DefaultSelectedItems: If(newMode Or IsBlank(ThisItem.<coluna>), Blank(), [Text(Hour(ThisItem.<coluna>), "00")])`;
- listas completas, sem filtro;
- a ordem é validada no Salvar, par a par, e **cada campo mostra a própria mensagem** ("Está antes do horário de acionamento da ambulância (18/09 14:15)"), com dica de meia-noite quando a diferença passa de 12 h;
- a data de cada campo nasce igual à do campo **anterior**, não à do primeiro;
- a borda vermelha, que era fixa, passou a ser só do campo com problema.

Validação preventiva: `REA/build/verificar_aph.sh` reprova `Hour(Parent.Default)`, `Minute(Parent.Default)` e `Value(HourValueN.Selected.Value), Second(`. No export original a regra acusa 26 ocorrências; na entrega, zero.

**Regra geral:** filtro de opções é conforto, nunca validação. Ordem entre campos se valida no envio, com a mensagem no campo que está errado. E todo `Value()`, `Hour()` ou `Minute()` sobre algo que pode estar em branco precisa de guarda **antes** (lição "`Blank() = 0`", 2026-08-27).

Impacto global: o mesmo trio data/hora/minuto existe em `ScreenCheckListREA`, `ScreenCheckListVeiculoCCI`, `ScreenCheckListERSCI`, `ScreenCheckListEpiEpr`, `ScreenCheckListSme`, `ScreenAcionamentosPlemPrai`, `ScreenOcorrenciasNaoAeronauticas` e `ScreenTesteContatos` (REA). Conferir os três pontos em cada uma.

## Excel Online aceita uma condição por consulta: a segunda derruba o `Filter` em tempo de execução (2026-09-18)

- Projeto/tela: REA / `ScreenAPH`, `OnVisible` e `cmbAeroporto.OnChange`. A fonte é `Cessionarios`, uma tabela do Excel Online (Business).
- Mensagem (Studio, logo depois de colar a tela):
  `Erro ao tentar recuperar dados da rede: [Cessionarios] A operação solicitada é inválida. Resposta do Servidor: [Cessionarios] Cláusula de filtro inválida: operação sem suporte. No momento, há suporte apenas para 'eq', 'ne', 'contém', 'startswith' ou 'endswith' únicos.`

Causa confirmada: a entrega acrescentou uma segunda condição a um `Filter` que tinha uma só:

```powerfx
Filter(Cessionarios, AeroportoDeConcessao = cmbAeroporto.Selected.IATA, SituacaoDaConcessao = "Ativa")
```

O conector do Excel delega o `Filter` ao servidor, mas só com **uma** comparação simples (`eq`, `ne`, `contains`, `startswith`, `endswith`). Com duas, o servidor recusa a consulta inteira. Não é o aviso amarelo de delegação: é erro de rede, e a coleção fica vazia. A sintaxe estava certa e todos os verificadores locais passaram; o defeito é do conector, não da fórmula.

Correção: voltar a consulta para uma condição só (a do export original). O filtro `SituacaoDaConcessao = "Ativa"` continua valendo em memória, no `Items` do combo, sobre a coleção já carregada.

Validação preventiva: `REA/build/checar_excel.py` lê as fontes Excel de `msapp/References/DataSources.json` (ApiId `shared_excelonlinebusiness`). Ele reprova todo `Filter`/`LookUp`/`CountIf`/`RemoveIf` sobre elas com mais de uma condição ou com `And`/`Or`/`&&`/`||` na condição. Foi provado nos dois sentidos: acusa as 2 fórmulas da entrega com defeito e passa o export original e a correção. Está no `REA/build/verificar_aph.sh`.

**Regra:** antes de acrescentar condição a uma consulta, confirme o conector da fonte em `DataSources.json`. SharePoint combina condições; Excel Online, não. Para Excel, a consulta ao servidor leva uma condição e o resto do filtro roda sobre a coleção.

## Coleção ou variável de contexto povoada por pontos com formatos diferentes: o Studio unifica o tipo e reprova tudo (2026-09-22)

- Projeto/tela: SAFETY / `ScreenModColisaoVeiculos` e os outros 6 módulos (botões Cadastrar e Editar), `ScreenExcluir` (30 erros), `ScreenFauna` (21) e `ScreenAcessIndFaunaForms` (2). Achado no Verificador de aplicativo do Studio, 410 erros de fórmula.
- Mensagens: "Nenhum tipo encontrado para ...", "Tipo de argumento inválido", "O primeiro argumento de 'Clear' ...", "A função 'ClearCollect' tem alguns argumentos inválidos", "O nome não é válido".

Causas confirmadas (quatro, todas invisíveis para os validadores locais, porque o YAML e as propriedades estavam corretos):

1. **Coleção com dois formatos.** `ClearCollect(col, ForAll(..., {dbId: ID, ...}))` (botão Editar) e `Collect(col, {id: <contador>, ...})` (botão Adicionar, já existente) povoavam a mesma coleção com colunas diferentes. O Studio unifica o tipo de `col_xxx` no app todo e reprova `Clear`/`ClearCollect` em cascata, em toda tela que a usa. Correção: os dois pontos escrevem as duas colunas (`dbId` e `id`).
2. **Variável de contexto recebendo registros de tabelas diferentes.** `Navigate(ScreenExcluir, ..., {var_item: ThisItem})` chamado de 9 origens, cada uma com `ThisItem` de uma lista do SharePoint diferente. Mesmo problema do item 1, agora numa variável de contexto: `var_item.colVei_id`, `var_item.derFlu_id` etc. viram "tipo não encontrado". Correção: mandar só valores escalares homogêneos (`var_item_id`, `var_item_chave`) e trocar os `Remove(tabela, var_item)` por `Remove(tabela, LookUp(tabela, ID = var_item_id))`.
3. **Tela existente só no export, nunca entregue.** `ScreenFaunaForms` (5.452 linhas) ficou em `msapp/Src` e nenhum script a levava para `out/`. Os 8 `Navigate(ScreenFaunaForms, ...)` de `ScreenFauna` e os `ResetForm`/`NewForm` sobre controles dela davam "O nome não é válido". O `checar_refs.py` não pegou: ele trata como existente toda tela de `msapp/Src` que não foi consolidada, entregue ou não.
4. **Nome de coleção copiado de outro módulo.** `BorderColor: =If(CountRows(col_incPistaImg) = 0, ...)` em `ScreenAcessIndFaunaForms`, onde a coleção da tela é `col_aceIndFauGalleryImg`.

Validação preventiva: **não automatizada ainda.** Ficou pendente um verificador que, para cada coleção, compare as chaves dos registros de todo `Collect`/`ClearCollect`/`Patch` que a povoa, e outro que confira que toda tela citada em `Navigate` tem arquivo em `out/`. O Verificador do Studio é hoje o único que pega o defeito; ele pode só reavaliar a checagem de tipo entre telas depois de salvar (não confirmado: com o código corrigido colado e sem salvar, os erros continuaram).

**Regra:** uma coleção ou variável de contexto tem um formato só, em todos os pontos que a escrevem. Para passar dados entre telas, mande escalares ou uma tabela de formato fixo, nunca `ThisItem` de fontes diferentes na mesma variável. Antes de dizer que uma entrega está completa, conferir que toda tela referenciada existe em `out/`.

## Tela de entrega em lote colada isolada: variável do OnStart novo "não é reconhecida" (2026-09-23)

- Projeto/tela: Inspeções / `frmCheckListGenericoEQP` (`out/15_…`), `cmbCLGbloco.DisplayMode`.
- Mensagem: `O nome não é válido. 'varModoFiltroBloco' não é reconhecido.`

Causa confirmada: a tela veio da entrega ABCD, em que a cirurgia C5 trocou a
fórmula de perfil repetida em cada combo por variáveis calculadas uma vez no
**App.OnStart novo** (`varModoFiltroAero`, `varModoFiltroBloco`, `varBlocoPadrao`).
A tela foi colada sozinha, com o OnStart antigo ainda no app: nenhum `Set` da
variável existe, e o Studio acusa nome desconhecido. O erro de entrega foi meu:
o checklist de outra tela mandou "colar a out/15 primeiro" sem dizer que ela
depende do OnStart da mesma entrega.

Correção: acrescentar ao OnStart atual só os `Set` que faltam (mesmo texto do
OnStart novo, para a colagem completa posterior não mudar nada) e executar o
OnStart no Studio.

Validação preventiva: `Inspeções/build/checar_dependencias_app.py` (no
`entregar.sh`) lista, por tela de `out/`, as variáveis que só existem no OnStart
novo e as `nf*` do App.Formulas novo. Aceita arquivo avulso como argumento.

**Regra:** tela de entrega em lote não é autônoma. Ao recomendar colar uma tela
fora da ordem do LEIA-ME, listar junto o que ela exige do App (variáveis do
OnStart, named formulas, coleções carregadas por outra tela) e entregar o trecho
mínimo para suprir isso.


## Fórmula invariante colada na barra pt-BR: `;` vira `,` e muda o sentido SEM erro (2026-10-13)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`, `btnDdExcluirConfirmar.OnSelect`.
- Sintoma: nenhum erro no Studio. Achado comparando o export enviado
  (commit "Atualização 13-10-2026") com a versão anterior: os encadeamentos
  `UpdateContext(...); Notify(...)` e `RemoveIf(...); Remove(...); Notify(...)`
  voltaram como `UpdateContext(...), Notify(...)` e `RemoveIf(...), Remove(...), ...`.

Causa confirmada pelo diff: é o caminho inverso da lição de locale (2026-08-13).
Uma fórmula no formato invariante (`;` encadeia) foi colada na **barra de
fórmulas pt-BR**, onde `;` é separador de **argumento**. O Studio aceitou porque
`If` e `IfError` são variádicos, e reexportou cada `;` como `,`. O resultado
compila e faz outra coisa:

```powerfx
If(!pode, UpdateContext(...), Notify("Só o Compliance..."), ...)
//         resultado 1        condição 2 (!): Notify roda e devolve true
```

Para quem PODE excluir, o botão mostrava "Só o Compliance ou quem abriu a
solicitação pode excluir." e não excluía nada. O `IfError` com 6 argumentos
virou pares valor/fallback: o `Remove` da solicitação passou a ser fallback.

Correção: restaurar os quatro `;` (fórmula idêntica à versão anterior, conferida
token a token).

Validação preventiva (`DueDiligence/validar_due_diligence.py`, grupo "Encadeamento
';' preservado"): reprovar `If` com função de ação (`UpdateContext`, `Notify`,
`Patch`, `Remove`, `Set`, `Reset`...) na **posição de condição**, e `IfError` com
4+ argumentos. Rodado no workspace inteiro: zero falso positivo na versão anterior
do Due Diligence; reprova exatamente o botão quebrado na versão enviada.

Impacto global: a mesma varredura acusou suspeitos em Inspeções
(`frmHomePatio`, `frmHomePista`, `frmHomeTPS`) e REA (`ScreenGestaoViaturas`,
`ScreenOcorrenciasNaoAeronauticas`), ainda não corrigidos.

**Regra:** fórmula para a barra de fórmulas sai convertida para pt-BR (`;;`
encadeia). Não basta dizer "converta": fórmula invariante colada lá **não dá erro**
quando a função aceita argumentos extras.

## Export do Studio traz `%DATACARD_` e reformata as fórmulas (2026-10-13)

- Projeto: DueDiligence / `ScreenDueDiligence` (export enviado em 2026-10-13).
- O export do Studio escreveu `MaxLength: =DataSourceInfo(%DATACARD_DATASOURCE_NAME.ID%, ...)`
  em 52 `TypedDataCard`. É o mesmo placeholder da lição "Placeholders internos do
  template": o Studio exporta, mas não aceita de volta na colagem. Antes de
  reentregar um export, remover essas linhas (são o padrão do cartão, sem efeito).
- O mesmo export quebra a linha depois de cada `(`/`[`/`{`, um argumento por
  linha. Validador que compara token depois de só colapsar espaços (`"If( x"` ≠
  `"If(x"`) passou a acusar 65 falsos positivos. Correção: `fx()` no validador
  também tira o espaço colado aos delimitadores, aplicado ao token e à fórmula.
- `Created` virou `Criado` (nome de exibição no Studio pt-BR). As duas formas
  funcionam no SharePoint (ver a lição de nome interno × exibição); não reverter.


## Toolbar@2.0.5: nome de ícone desconhecido vira círculo vazio, sem erro (2026-10-13)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`, `tbDdAcoes` (menu "…" da galeria).
- Sintoma (print do app publicado): "Baixar Laudo" (`"Download"`), "Analisar"
  (`"ShieldCheckmark"`) e "Assumir" (`"PersonAdd"`) com um círculo vazio no lugar do
  ícone. `"Eye"`, `"Edit"`, `"Send"` e `"Delete"` aparecem normalmente. Nenhum aviso
  no Studio.
- Causa confirmada pelo print: `ItemIconName` não aceita qualquer nome do catálogo
  Fluent. `Download` nem existe no Fluent (lá é `ArrowDownload`). `PersonAdd` e
  `ShieldCheckmark` existem e também não renderizaram.
- Correção: só nomes que aparecem em **export real do Studio** (`*/msapp/Src`):
  `DocumentBulletList` (Analisar), `People`/`DismissCircle` (Assumir/Liberar),
  `DocumentPdf` (Baixar Laudo).
- Validação preventiva (`DueDiligence/validar_due_diligence.py`, grupo "Analista do
  Compliance na listagem"): lista de ícones permitidos para `tbDdAcoes`.
- Regra global: ícone de controle moderno (`Icon` de Button, `ItemIconName` de
  Toolbar) vem de export real do Studio, nunca do catálogo Fluent nem da memória.

## Combo fora do formulário lendo `Items` de combo dentro do formulário abriu vazio (2026-10-13)

- Projeto/tela: DueDiligence / `ScreenDueDiligence`, `cmbDdFiltroArea` (filtro da
  listagem) com `Items: =cmb_area_solicitante.Items` (combo dentro de um cartão do
  `frmDdSolicitante`).
- Sintoma (print do app): o filtro abriu sem nenhuma opção.
- Causa **não confirmada**. Hipótese: o formulário está oculto na visão de
  registros e o controle do cartão não expõe `Items` fora dele.
- Correção: lista literal repetida no filtro. O validador reprova a referência
  ao combo do formulário e exige que as duas listas sejam idênticas. Assim a
  repetição não diverge quando entrar área nova.
- Regra: para reaproveitar opções entre controles, usar lista literal conferida
  por validador (ou named formula no `App.Formulas`), nunca a propriedade de
  controle que mora dentro de cartão de formulário.
