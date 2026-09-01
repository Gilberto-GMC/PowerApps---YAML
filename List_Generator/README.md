# List_Generator — fluxo de provisionamento de listas SharePoint

Fluxo de botão do Power Automate que recebe um JSON e cria a lista, as colunas, os índices, a
validação e os registros iniciais. O JSON é produzido pela skill
[`list-generator`](../.claude/skills/list-generator/SKILL.md); as duas peças formam um contrato só.

| Arquivo | O que é |
|---|---|
| `List_Generator_v2.zip` | Pacote para importar no Power Automate |
| `src/` | O mesmo pacote descompactado, para ficar diffável no git |

**Importar:** Power Automate → *Meus fluxos* → **Importar** → *Pacote (.zip)* → escolher
`List_Generator_v2.zip` → em **Configuração relacionada**, apontar a conexão do SharePoint → em
**Recursos de importação**, escolher **Atualizar** sobre o `List_Generator` existente (ou *Criar como novo*).

**Usar:** *Executar* → preencher `siteUrl` e colar o JSON em `text`.

---

## O que mudou em relação ao pacote original (`List_Generator_20260828204254.zip`)

### 1. `ocultarTitle` era uma promessa vazia — agora existe

A skill exigia `"ocultarTitle": true` e afirmava que *"quem configura `Required=false`, `Hidden=true`,
remove dos formulários e das views é o fluxo"*. No fluxo original, `ocultarTitle` **não estava sequer
declarado** no `Parse_Definicao`, e não havia nenhuma ação tocando em `Title`. Toda lista provisionada saía
com `Title` obrigatório e na view padrão — exatamente o contrário da regra da casa.

Foi acrescentado o `Condicao_Ocultar_Title`, logo depois de `Definir_ListaId` e **antes** das colunas:

| Ação | Chamada | Obrigatória? |
|---|---|---|
| `HTTP_Title_Desobrigar` | `MERGE` no campo `Title` com `Required=false` | sim |
| `HTTP_Title_Ocultar` | `MERGE` no campo `Title` com `Hidden=true` | **melhor esforço** |
| `Titulo_Concluido` | `Compose` — existe só para tolerar a falha do passo acima | — |

`Hidden=true` é melhor esforço porque alguns tenants recusam ocultar o `Title`. Como ele é o último passo
útil da condição, uma falha dele derrubaria a condição inteira; o `Compose` no fim, com
`runAfter: [Succeeded, Failed]`, é o que absorve isso. Se o `Ocultar` falhar, o `Title` fica ao menos não
obrigatório.

> **Não existe `RemoveViewField('Title')`.** Ele existiu numa versão intermediária e **travava a execução**:
> `Hidden=true` **já retira o campo de todas as views**, então a chamada seguinte batia num campo que não
> estava mais lá. Redundante e prejudicial — foi removida.

### 2. Consequência disso: `registrosIniciais` não funcionava

Com `Title` obrigatório, todo `POST` em `/items` sem `Title` volta **400**. Como o `Para_cada_Registro`
está dentro do `ESCOPO_Provisionar_Lista`, a lista ficava criada pela metade e o fluxo caía no
`Compor_Erro`. Neutralizar o `Title` antes dos registros resolve a causa.

### 3. `Options: 4` não garantia o nome interno

`CreateFieldAsXml` usava `Options: 4`, que é só `AddToAllContentTypes`. Faltava
`AddFieldInternalNameHint` (8) — o sinalizador que manda o SharePoint usar o atributo `Name` como nome
interno. Sem ele, o nome interno pode ser derivado do `DisplayName` e nascer codificado (`_x0020_`), que é
justamente o que a skill e os projetos tentam evitar. Agora é **`Options: 12`**.

### 4. Lista criada com anexos ligados e sem limite de versão

Anexos e limite de versão passaram a ser configurados por um `HTTP_Ajustar_Lista` — um `MERGE` na lista
logo depois de `Definir_ListaId` — e **não** dentro do `POST` de criação.

> **Por que separado.** Na primeira versão desta alteração eu tinha colocado `"EnableAttachments": false` e
> `"MajorVersionLimit": 50` no próprio corpo do `HTTP_Criar_Lista`. Parte dos tenants recusa
> `MajorVersionLimit` num `POST` de criação — o versionamento ainda não está aplicado quando a propriedade é
> lida — e a chamada volta *Invalid request*. Como `HTTP_Criar_Lista` é a primeira ação do escopo, o efeito é
> o fluxo travar logo depois do `Parse_Definicao`. O `POST` de criação voltou a ser **exatamente** o payload
> original, que era comprovado.

O `HTTP_Ajustar_Lista` é **melhor esforço**: o `Condicao_Ocultar_Title` roda com
`runAfter: [Succeeded, Failed]`. Se o tenant recusar, a lista continua utilizável — `EnableVersioning` já
vem do `POST` de criação, que é o que realmente importa.

### 5. Não havia como aplicar validação de lista

Regra que enxerga **duas colunas** (`=[hora_fim]>[hora_inicio]`) é da lista, não da coluna, e não cabe no
`schemaXml`. Foi acrescentado o `Condicao_Validacao_Lista`, que faz `MERGE` em `ValidationFormula` e
`ValidationMessage` quando o JSON traz `validacaoLista`. Regra de **uma coluna só** continua no
`schemaXml`, como `<Validation Message='...'>`, e já funcionava.

### 6. `Compor_Resultado` mudo

Passou a devolver `colunasCriadas`, `registrosCriados`, `tituloNeutralizado` e `validacaoAplicada`, para
conferir o resultado sem abrir o histórico de execução.

---

## Contrato do trigger

```
siteUrl : URL do site SharePoint
text    : o JSON da skill list-generator
```

Schema aceito em `text` — seis propriedades, `nomeLista` e `colunas` obrigatórias:

```
nomeLista          string
descricao          string
ocultarTitle       boolean          (ausente = true)
colunas[]          { internalName, schemaXml }
registrosIniciais[]
validacaoLista     { formula, mensagem }   ({} quando não há)
```

## Ordem de execução dentro do escopo

```
HTTP_Verificar_Lista          ← barra nome repetido, antes de qualquer escrita
Condicao_Lista_Ja_Existe      ← Terminate com mensagem clara se já existir
ESCOPO_Provisionar_Lista
  HTTP_Criar_Lista
  Definir_ListaId
  HTTP_Ajustar_Lista          ← anexos e limite de versão, melhor esforço
  Condicao_Ocultar_Title      ← desobriga e oculta o Title
  Para_cada_Coluna            ← CreateFieldAsXml (Options 12) + AddViewField, sequencial
  HTTP_Obter_Tipo_Item
  Definir_TipoItem
  Condicao_Validacao_Lista    ← ValidationFormula / ValidationMessage
  Condicao_Registros_Iniciais
```

`Para_cada_Coluna` roda com `concurrency: 1` de propósito: a ordem do array `colunas` é a ordem das
colunas na view padrão.

### 7. Nome de lista repetido travava a execução

`POST _api/web/lists` com um `Title` que já existe volta erro, e o connector do SharePoint **faz retry** nesse
caso: a execução fica minutos em *running* sem dizer o motivo. Foi acrescentado, antes do escopo:

- `HTTP_Verificar_Lista` — `GET _api/web/lists?$select=Id,Title&$filter=Title eq '<nome>'`. Consulta com
  filtro sempre volta 200, com array vazio ou com um item, então não depende de tratar 404.
- `Condicao_Lista_Ja_Existe` — se veio algum item, `Terminate` com `runStatus: Failed` e a mensagem
  *"Já existe uma lista chamada X em Y. O fluxo não altera lista existente: exclua a lista e rode de novo."*

`HTTP_Criar_Lista` e `HTTP_Ajustar_Lista` passaram a ter `retryPolicy: none` — o erro real do SharePoint sobe
na hora, em vez de ficar escondido atrás de tentativas. No laço de colunas o retry continua ligado, onde é
útil contra throttling.

O `Compor_Erro` também mudou: devolve `acoesComFalha`, filtrando do `result()` do escopo só as ações que não
tiveram sucesso, com status e corpo da resposta.

### 8. Aspas duplas no `schemaXml` quebravam o corpo da criação de coluna

`HTTP_Criar_Coluna` montava o corpo por interpolação de texto:

```
{"parameters":{...,"SchemaXml":"@{items('Para_cada_Coluna')?['schemaXml']}","Options":12}}
```

Qualquer `"` dentro do `schemaXml` fecha a string e o JSON fica inválido. Isso acontece sempre que a coluna
tem `<Validation>` comparando com texto — `=OU([tipo_registro]="VOO";...)`. O corpo passou a ser montado com
`setProperty`, que escapa sozinho:

```
@string(setProperty(json('{}'), 'parameters', setProperty(
  json('{"__metadata":{"type":"SP.XmlSchemaFieldCreationInformation"},"Options":12}'),
  'SchemaXml', items('Para_cada_Coluna')?['schemaXml'])))
```

### 9. Retry escondendo o erro

A política padrão do connector é exponencial, com quatro tentativas: uma ação que falha fica **minutos** em
*running* sem dizer o motivo. Agora:

| Ação | Política |
|---|---|
| `HTTP_Verificar_Lista`, `HTTP_Criar_Lista`, `HTTP_Ajustar_Lista`, as do `Title`, `HTTP_Obter_Tipo_Item`, `HTTP_Aplicar_Validacao_Lista` | `none` |
| Dentro dos laços de coluna e de registro | `fixed`, 1 tentativa, 5 s |

O laço mantém uma tentativa curta porque é onde o throttling (429) de fato aparece. Se o volume crescer e o
429 voltar a incomodar, é ali que se afrouxa.

---

## O que o fluxo ainda não faz

- **Não é idempotente.** Rodar duas vezes com o mesmo `nomeLista` agora **para com mensagem clara** em vez de
  ficar em retry — mas continua sendo você quem exclui a lista antes de rodar de novo.
- **Não cria views adicionais** além da padrão.
- **Não quebra a herança de permissão** — isso continua manual.
- **Não altera lista existente.** É provisionamento, não migração.
