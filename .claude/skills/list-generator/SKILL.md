---
name: list-generator
description: Gera a definição JSON de uma lista SharePoint para colar no fluxo List_Generator do Power Automate (AirportNow/Motiva). Use sempre que o usuário pedir para criar/gerar uma lista SharePoint, o JSON de uma lista, colunas de lista, "gerador de listas", List_Generator, tb_ alguma coisa, ou passar os campos de uma nova tabela do projeto.
---

# Gerador de listas SharePoint (List_Generator)

Recebe a descrição de uma lista e devolve **um único bloco de código JSON válido**,
pronto para colar no fluxo `List_Generator` do Power Automate, que cria a lista e as colunas.

## Formato da resposta

A resposta é **somente** o bloco JSON. Sem introdução, sem explicação, sem "o que eu ajustei",
sem observações depois. Se alguma decisão precisou ser tomada, ela já está refletida no JSON.

Exceção única: quando faltar um dado sem o qual o JSON não pode ser gerado, faça **uma**
pergunta objetiva e nada mais. Falta de dado é só isso — nome da lista impossível de inferir,
ou nenhum campo informado. Tipo, tamanho e obrigatoriedade nunca são motivo de pergunta:
decida pelo padrão desta skill.

## Contrato do JSON

Exatamente estas seis propriedades, nesta ordem, e nenhuma outra:

```json
{
  "nomeLista": "tb_exemploOperacional",
  "descricao": "texto curto em minusculas sem acento descrevendo o proposito da lista",
  "ocultarTitle": true,
  "colunas": [
    {
      "internalName": "aeroporto",
      "schemaXml": "<Field Type='Text' DisplayName='aeroporto' Name='aeroporto' StaticName='aeroporto' Group='AirportNow' MaxLength='10' Required='TRUE' Indexed='TRUE'/>"
    }
  ],
  "registrosIniciais": [],
  "validacaoLista": {}
}
```

Cada item de `colunas` tem **apenas** `internalName` e `schemaXml`. Não existe propriedade
`indexada`, `tipo` ou `descricao` na coluna — a indexação vai em `Indexed='TRUE'` dentro do XML.

## Regras invioláveis

### Title
- `"ocultarTitle": true` sempre.
- A palavra `Title` **nunca** aparece em `colunas`, em `registrosIniciais` nem em nenhum `schemaXml`.
- Nunca criar, recriar ou alterar `Title` via schemaXml. `ocultarTitle` é só o sinal; quem age é o fluxo,
  em três chamadas, logo depois de criar a lista e **antes** das colunas e dos registros iniciais:
  `Required=false` → `Hidden=true` → `RemoveViewField('Title')` da view padrão.
- O passo `Hidden=true` é **melhor esforço**: alguns tenants recusam ocultar o `Title`, e o fluxo segue assim
  mesmo. Quando isso acontece, `Title` fica não obrigatório e fora da view — que é o efeito que importa.
  Os dois outros passos são obrigatórios; se falharem, o fluxo inteiro falha.
- É esse bloco que faz `registrosIniciais` funcionar: com `Title` obrigatório, todo `POST` em `/items` sem
  `Title` volta 400 e a lista fica criada pela metade.

### Nomenclatura
- `nomeLista`: começa com `tb_` e segue em camelCase — sem espaço, acento, hífen ou caractere
  especial. Ex.: `tb_controleSobrecarga`, `tb_avsecOcorrencias`.
- `internalName`: minúsculas, `snake_case`, sem acento, espaço, hífen ou caractere especial.
- Em cada coluna, `internalName`, `DisplayName`, `Name` e `StaticName` são **literalmente
  idênticos**. Nunca gere rótulo amigável.
  - Certo: `DisplayName='id_fk_ocorrencia' Name='id_fk_ocorrencia' StaticName='id_fk_ocorrencia'`
  - Errado: `DisplayName='ID da ocorrência'`, `'Aeroporto'`, `'Categoria do desdobramento'`
- Antes de emitir a coluna, valide que os quatro valores batem com `^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$`
  e são iguais entre si. Maiúscula, acento, espaço, hífen ou rótulo descritivo → corrija em
  silêncio para minúsculas e snake_case.

### Tipos permitidos
Somente `Text`, `Note`, `Number` e `DateTime`.
**Proibidos:** `Choice`, `User`, `Boolean`, `Lookup`, `Currency`, `Taxonomy`, `Calculated`.

| Necessidade funcional | Tipo a usar |
|---|---|
| seleção controlada (status, unidade, categoria, área, tipo) | `Text` com `MaxLength` do maior valor esperado |
| responsável / usuário | `Text` guardando o e-mail corporativo — uma coluna só, não crie nome + e-mail |
| campo lógico / flag / `ativo` | `Number` com `1` = verdadeiro, `0` = falso — nunca `true`/`false` |
| texto longo, descrição, observação | `Note` |
| data | `DateTime` |
| relacionamento com outra lista | `Number` com o `id` (`id_fk_...`), nunca Lookup |

### Atributos por tipo
- Todas as colunas: `Group='AirportNow'`.
- `Text`: `MaxLength` compatível com o conteúdo esperado.
- `Note`: `RichText='FALSE'` e `AppendOnly='FALSE'`. **Nunca indexado.**
- `DateTime`: `Format='DateTime'` ou `Format='DateOnly'` conforme a necessidade funcional.
- `Number`: `Decimals` conforme a precisão (`0` para flags, ids e contagens) e `Min` quando
  houver limite mínimo.
- `Required='TRUE'` ou `Required='FALSE'` em toda coluna personalizada, conforme a
  obrigatoriedade funcional. Sem informação → `Required='FALSE'`.
- `Default` quando houver valor inicial definido (status inicial, `ativo` = 1).

### Modelagem
- Não duplicar coluna nativa: `ID`, `Created`, `Modified`, `Author`, `Editor`.
- Preferir **uma lista centralizada** contendo a coluna `aeroporto`.
- Incluir `ativo` (`Number`, `Decimals='0'`, `Default='1'`) para soft-delete quando a lista
  representar registros operacionais.
- Incluir `status` (`Text`) quando houver fluxo de situação ou aprovação, com `Default` se
  houver status inicial.

### Índices
- Indexar só o que é realmente usado em filtro delegável, ordenação ou exibição frequente.
  Prioridade: `aeroporto`, `status`, `DateTime` de filtro.
- Limite de **20 índices** por lista.
- **Nunca** indexar `Note`.

### Validação
Rede de segurança para quem editar a lista fora do app.

- **Regra de uma coluna só** vai dentro do próprio `schemaXml`, como elemento filho de `Field`:
  `<Field ...><Validation Message='mensagem curta'>=OU([coluna]=0;[coluna]=1)</Validation></Field>`
  Quando há `Validation`, o `Field` deixa de ser auto-fechado.
- **Regra que enxerga duas colunas** vai em `validacaoLista`, porque no SharePoint ela é da lista, não da
  coluna: `{"formula": "=[hora_fim]>[hora_inicio]", "mensagem": "o fim tem que ser maior que o inicio"}`.
  Sem regra → `"validacaoLista": {}`.
- A fórmula segue o separador do **site**: `;` em site pt-BR (`=OU(...)`, `=E(...)`), `,` em en-US
  (`=OR(...)`, `=AND(...)`). Na dúvida, pt-BR.
- Validação não substitui a regra no app — ela pega a edição feita pela interface do SharePoint.

### Registros iniciais
- Usam somente colunas personalizadas declaradas em `colunas`.
- Texto entre aspas, número sem aspas. Flags persistidas como `Number` usam `1` ou `0`.
- Sem registros pedidos → `"registrosIniciais": []`.
- Não inclua `Title`: o fluxo já o desobrigou antes de chegar aqui.

### O que o fluxo já faz — não repita no JSON
- Cria a lista com **versionamento ligado (50 versões)** e **anexos desabilitados**.
- Cria cada coluna por `CreateFieldAsXml` com `Options=12` — `AddToAllContentTypes` mais
  `AddFieldInternalNameHint`, que é o que **garante o nome interno** vindo do atributo `Name` e elimina o
  `_x0020_` de nome codificado.
- Acrescenta cada coluna personalizada à view padrão, na ordem em que aparecem em `colunas` — então a ordem
  do array é a ordem da view.
- Neutraliza o `Title` e aplica a `validacaoLista`.

Não gere ação, índice nem view por fora: só o JSON.

### Power Automate
Nada de expressão, conteúdo dinâmico, referência de ação ou variável do fluxo dentro do JSON.
Só valores literais.

## Antes de responder

Rode o validador — ele checa todas as regras acima de uma vez:

```bash
python3 .claude/skills/list-generator/scripts/validar_json.py caminho/do/arquivo.json
```

Se o validador não estiver disponível, confira manualmente: as seis propriedades estão presentes e nesta
ordem; `ocultarTitle` é `true`; a palavra `Title` não aparece em lugar nenhum; `nomeLista` começa com `tb_` e é
camelCase sem acento; todo `internalName` é minúsculo e snake_case; `internalName`/`DisplayName`/`Name`/
`StaticName` são idênticos em cada coluna; nenhum `DisplayName` tem maiúscula, acento, espaço ou rótulo
amigável; só há `Text`, `Note`, `Number`, `DateTime`; toda coluna tem `Group='AirportNow'`; nenhum `Note`
indexado; flags são `Number` com 1/0; `validacaoLista` é `{}` ou tem `formula` e `mensagem`.

Corrija e revalide em silêncio. O usuário vê só o JSON final.

## Exemplo completo

```json
{
  "nomeLista": "tb_avsecDesdobramentos",
  "descricao": "desdobramentos das ocorrencias avsec com prazo e responsavel",
  "ocultarTitle": true,
  "colunas": [
    {
      "internalName": "id_fk_ocorrencia",
      "schemaXml": "<Field Type='Number' DisplayName='id_fk_ocorrencia' Name='id_fk_ocorrencia' StaticName='id_fk_ocorrencia' Group='AirportNow' Decimals='0' Min='1' Required='TRUE' Indexed='TRUE'/>"
    },
    {
      "internalName": "aeroporto",
      "schemaXml": "<Field Type='Text' DisplayName='aeroporto' Name='aeroporto' StaticName='aeroporto' Group='AirportNow' MaxLength='10' Required='TRUE' Indexed='TRUE'/>"
    },
    {
      "internalName": "categoria",
      "schemaXml": "<Field Type='Text' DisplayName='categoria' Name='categoria' StaticName='categoria' Group='AirportNow' MaxLength='60' Required='TRUE'/>"
    },
    {
      "internalName": "conteudo",
      "schemaXml": "<Field Type='Note' DisplayName='conteudo' Name='conteudo' StaticName='conteudo' Group='AirportNow' RichText='FALSE' AppendOnly='FALSE' NumLines='6' Required='TRUE'/>"
    },
    {
      "internalName": "responsavel_email",
      "schemaXml": "<Field Type='Text' DisplayName='responsavel_email' Name='responsavel_email' StaticName='responsavel_email' Group='AirportNow' MaxLength='120' Required='TRUE'/>"
    },
    {
      "internalName": "prazo",
      "schemaXml": "<Field Type='DateTime' DisplayName='prazo' Name='prazo' StaticName='prazo' Group='AirportNow' Format='DateOnly' Required='FALSE' Indexed='TRUE'/>"
    },
    {
      "internalName": "prazo_fim",
      "schemaXml": "<Field Type='DateTime' DisplayName='prazo_fim' Name='prazo_fim' StaticName='prazo_fim' Group='AirportNow' Format='DateOnly' Required='FALSE'/>"
    },
    {
      "internalName": "status",
      "schemaXml": "<Field Type='Text' DisplayName='status' Name='status' StaticName='status' Group='AirportNow' MaxLength='30' Required='TRUE' Indexed='TRUE'><Default>aberto</Default><Validation Message='use aberto, em andamento ou concluido'>=OU([status]=\"aberto\";[status]=\"em andamento\";[status]=\"concluido\")</Validation></Field>"
    },
    {
      "internalName": "ativo",
      "schemaXml": "<Field Type='Number' DisplayName='ativo' Name='ativo' StaticName='ativo' Group='AirportNow' Decimals='0' Min='0' Required='TRUE'><Default>1</Default><Validation Message='use 1 ou 0'>=OU([ativo]=0;[ativo]=1)</Validation></Field>"
    }
  ],
  "registrosIniciais": [],
  "validacaoLista": {
    "formula": "=SE(EBRANCO([prazo]);VERDADEIRO;[prazo_fim]>=[prazo])",
    "mensagem": "o fim do prazo nao pode ser antes do inicio"
  }
}
```
