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

Os itens 11 e 12 dependem do ambiente Power Apps/SharePoint e não podem ser
substituídos apenas por validação local do arquivo.
