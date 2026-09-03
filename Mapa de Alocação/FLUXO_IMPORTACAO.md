# Fluxo `Importar programacao` — passo a passo

Fluxo do Power Automate que recebe o item criado pela tela `scrMapaImport`, chama o Office Script e
grava os registros em `tb_alocacoesMapa`, atualizando o progresso que a barra da tela lê.

**Pré-requisitos**, todos já feitos:

- `tb_importacaoMapa` criada, com anexos habilitados
- coluna `origem` em `tb_alocacoesMapa`, tipo Texto, indexada
- Office Script `Importar programacao` salvo e testado (698 registros / 7 pendências em setembro/26)
- uma biblioteca de documentos para guardar o anexo temporariamente — pode ser a **Documentos** do site

---

## Atalho: importar o pacote pronto

`Importarprogramacao_COMPLETO.zip` traz as **16 ações já montadas e ligadas**, com a condição de
gatilho, a simultaneidade 1 e as 19 colunas mapeadas. Foi construído sobre o pacote que o Douglas
exportou do próprio ambiente, então site e GUID de `tb_importacaoMapa` são os reais.

**Power Automate → Meus fluxos → Importar → Pacote (herdado)** → escolher o `.zip` → em *Recursos
relacionados*, clicar na conexão do SharePoint e selecioná-la → **Importar**.

> ⚠️ **O pacote tem que entrar como "Criar como novo", não como "Update".** O Power Automate não
> atualiza um fluxo existente por pacote quando a definição mudou — falha com *"To import this flow
> you'll need to save it as a new flow first"*. O `.zip` do repositório já vem marcado assim
> (`suggestedCreationType: New` no manifesto). Se algum dia reaparecer marcado como Update, a
> correção é a chave inglesa (🔧) na linha do fluxo → trocar o **IMPORT SETUP**.

> Como entra como fluxo novo, sobra o fluxo vazio original com o mesmo nome. Apague um dos dois
> depois de confirmar qual é qual — dois fluxos homônimos disparando na mesma lista seria ruim.

Depois da importação faltam **dois ajustes** — ver "A costura" logo abaixo.

O passo a passo manual que vem em seguida continua valendo: é ele que explica *por que* cada ação
está do jeito que está, e é o caminho se a importação não pegar.

### A costura

O pacote exportado declara **só** a conexão do SharePoint. Acrescentar o conector do Excel exigiria
inventar entradas no manifesto, e erro ali derruba a importação inteira — sem mensagem útil. Então a
chamada do Office Script ficou como uma junta que você liga na mão:

1. **Adicione a ação do Excel** entre `Salvar_planilha` e `Resultado_script`:
   **Excel Online (Business) → Executar script**, com os parâmetros do passo 5. O **Arquivo** é o
   `Id` da ação `Salvar_planilha`.
2. **Abra a ação `Resultado_script`** (é um *Compose* com um JSON de aviso dentro), apague o
   conteúdo e ponha a expressão:

```
@outputs('Executar_script')?['body/result']
```

Ajuste `Executar_script` para o nome interno real da ação que você acabou de criar — espaço vira
sublinhado.

Todas as ações seguintes já leem de `outputs('Resultado_script')`. Ligando essa junta, o resto anda
sozinho.

> Se você rodar sem ligar a costura, o fluxo **não quebra e não estraga nada**: importa zero
> registros e escreve o motivo no campo `mensagem` do item. Foi de propósito — falha barulhenta e
> inofensiva é melhor que falha silenciosa.

### O `operationId` não é o nome que aparece na tela

A importação do pacote **valida cada `operationId` contra o conector** e para no primeiro que não
existir, dizendo qual é:

```
The API operation GetAttachments could not be found in API sharepointonline
```

A ação chamada **"Obter anexos"** tem `operationId` **`GetItemAttachments`** — e os parâmetros dela
são `itemId`/`attachmentId`, não `id`/`fileId`. O nome visível e o nome interno divergem, e não há
como adivinhar qual dos dois é.

A tabela real, conferida em `learn.microsoft.com/connectors/sharepointonline`:

| ação na tela | operationId | parâmetros |
|---|---|---|
| Obter anexos | `GetItemAttachments` | `dataset`, `table`, `itemId` |
| Obter conteúdo do anexo | `GetAttachmentContent` | `dataset`, `table`, `itemId`, `attachmentId` |
| Criar arquivo | `CreateFile` | `dataset`, `folderPath`, `name`, `body` |
| Obter itens | `GetItems` | `dataset`, `table`, `$filter`, `$top` |
| Criar item | `PostItem` | `dataset`, `table`, `item/<coluna>` |
| Atualizar item | `PatchItem` | `dataset`, `table`, `id`, `item/<coluna>` |
| Excluir item | `DeleteItem` | `dataset`, `table`, `id` |

**Montando pelo designer isso não importa** — ele escreve o nome interno sozinho. Só pesa para quem
edita a definição fora da ferramenta. A lição é a mesma de sempre neste repositório: nome de
propriedade se confere na fonte, não se deduz do rótulo.

### `PatchItem` exige todas as colunas obrigatórias, mesmo as que não mudam

`tb_importacaoMapa` tem **8 de 9 colunas obrigatórias** — só `mensagem` é opcional. O conector
valida o item inteiro contra o esquema da lista, então uma atualização que mexe só no `status`
é recusada:

```
The API operation PatchItem is missing required property item/aeroporto
```

É o mesmo fato que obrigou os dois `TypedDataCard` invisíveis na tela de importação: **campo
obrigatório sem valor padrão precisa ser preenchido, mesmo quando ninguém quer mudá-lo.** Lá era o
`SubmitForm`, aqui é o `PatchItem`.

As colunas não alteradas vão com o valor de origem — mas **não dá para pegar todas do gatilho**. O
`total` no instante do gatilho é `0`; puxá-lo de lá nas ações que rodam depois do script zeraria o
denominador da barra bem no meio da importação. Cada ação declara de onde vem o que ela não muda:

| ação | de onde vem o `total` |
|---|---|
| `Marcar_processando` | gatilho — roda antes do script, ainda é 0 mesmo |
| `Guardar_total` | do script |
| `Gravar_processados` | do script |
| `Fechar` | do script |
| `Marcar_erro` | gatilho — o contador pode nem ter sido inicializado |

O gerador `montar_fluxo.js` confere isso sozinho: a cada geração ele varre todo `PatchItem` e
`PostItem` e lista qualquer obrigatória ausente. Era verificação que dava para fazer daqui e eu não
estava fazendo.

### Tirar o script do OneDrive pessoal

A ação padrão do Excel, **`Run script`**, só enxerga os scripts pessoais da conta conectada — eles
ficam em `personal › <usuário> › Scripts do Office`, no OneDrive de quem criou. Isso torna o script
**intransferível**: quando essa pessoa sai ou perde acesso, o fluxo mensal para, e o erro aparece
como "script não encontrado" para quem não faz ideia de onde ele estava.

**Sintoma correlato:** dropdown de scripts vazio ("Nenhum item") quase sempre é a conexão do Excel
autenticada numa conta diferente da dona do script.

**A correção, em três passos:**

1. No painel Scripts do Office, no **⋯ do cartão do script → Mover script** (não *Fazer uma cópia*:
   mover não deixa gêmeo para trás, e gêmeo é justamente o que queremos evitar).

   ⚠️ **Ele ignora a pasta que você escolher e usa a pasta padrão localizada — em português,
   `Documentos › Roteiros`.** Criar uma pasta `Scripts` antes não adianta; o arquivo não vai para
   ela. Foi o que aconteceu aqui, e custou duas rodadas procurando no lugar errado. O seletor do
   fluxo também chama o campo de *Roteiro*: a interface traduz "Script" por "Roteiro" em todo lugar,
   e é por aí que se acha o arquivo.
2. No fluxo, trocar a ação **`Run script`** por **`Run script from SharePoint library`**. Ela pede
   seis campos, porque separa onde está a planilha de onde está o script:

| campo | valor |
|---|---|
| Workbook Location | `Group - AIRPORT NOW` |
| Workbook Library | `Documentos` |
| Workbook | `corpo/ID` do `Salvar planilha` |
| Script Location | `Group - AIRPORT NOW` |
| Script Library | `Documentos` |
| Script | `Roteiros › Importar programacao.osts` |
| mesRef | `@{formatDateTime(triggerBody()?[mes_ref], yyyy-MM)}` |

3. **Corrigir o `Resultado_script`.** O nome interno da ação muda, e o `Compose` aponta para o antigo.
   Trocar para `@outputs(Run_script_from_SharePoint_library)?[body/result]` — ou renomear a ação
   nova para `Run script`, aí a expressão continua valendo.

⚠️ **Antes de mover, confira quantas cópias já existem.** Aqui havia quatro no OneDrive pessoal —
duas `Importar programa…` de dias diferentes, uma `Script` e uma `Cópia de Importar…`. Mover a errada
faria o fluxo rodar uma versão que não é a validada, **sem erro nenhum**, só com resultado diferente.

**Como distinguir:** abra cada uma e procure a palavra `origem`. Só a versão atual escreve essa
coluna — foi a última alteração feita, e é o que o fluxo mapeia. As que não têm são anteriores e
produziriam registros que o passo de limpeza não consegue apagar depois.

**Limitação que não nos afeta:** script salvo no SharePoint não pode fazer chamadas de rede. O
`importar_programacao.ts` só lê a planilha e devolve JSON — conferido, nenhum `fetch`.

### Detalhes que dependem do ambiente, não da definição

Duas coisas o pacote não tem como acertar sozinho, e ambas travam a primeira execução:

- **A pasta da biblioteca precisa existir e o caminho tem que bater.** O `Salvar planilha` grava numa
  pasta que o SharePoint **não cria sozinho**. Aqui a pasta real é `Documentos › Importar`, não o
  `/Documentos Compartilhados/importacoes` que eu havia chutado. Navegue pelo ícone de pasta em vez
  de digitar: o caminho interno de biblioteca em site português nem sempre é o que aparece na tela.
- **O campo `Arquivo` do Run script quer `corpo/ID`**, não `corpo/ItemId`. O `ItemId` é o ID do item
  de lista que representa o arquivo, usado para mexer em metadados; o conector do Excel quer o
  identificador do arquivo em si.

### Os 5 avisos de "loop circular" são esperados

O Verificador de fluxo acusa **loop circular em todas as ações que escrevem em `tb_importacaoMapa`**
— cinco delas. É falso positivo: o verificador não enxerga condições de gatilho, e a condição é
justamente a proteção. O fluxo *tem* que escrever na lista que o dispara, porque é de lá que a barra
de progresso lê.

**Mas o aviso vira verdade se a condição sumir.** Depois de qualquer importação de pacote ou
restauração, confira no gatilho → Configurações → Condições de gatilho:

```
@equals(triggerBody()?[status], PRONTO)
```

Erros (0) é o que importa. Avisos (5) é o normal deste fluxo.

### O que eu não consegui verificar daqui

- **`tb_alocacoesMapa` está referenciada pelo título, não pelo GUID** — eu só tinha o GUID de
  `tb_importacaoMapa`, que veio no gatilho exportado. Se alguma ação daquela lista abrir com o campo
  *Nome da lista* em branco ou com erro, é só reescolher a lista no dropdown.
- **Se a importação do pacote for recusada**, não insista: monte pelo passo a passo manual. O
  formato de pacote do Power Automate é malcriado com definição editada fora da ferramenta.

---

## ⚠️ Leia isto antes de começar

**O fluxo altera o item que o dispara.** Sem trava, ele se redispara em laço infinito: grava
`PROCESSANDO`, o que conta como modificação, o que dispara o fluxo, que grava de novo. A trava é a
**condição de gatilho** do passo 1 — não é opcional, e não é a mesma coisa que um `Condition` no corpo
do fluxo. Uma condição no corpo já executou o gatilho; a condição *de gatilho* impede a execução.

**O laço de gravação tem que ser sequencial.** Por padrão o `Aplicar a cada` roda em paralelo, e aí o
contador que move a barra vira corrida — dois ramos incrementam o mesmo valor e o número sai errado.
Sequencial custa tempo: ~700 itens levam de 8 a 12 minutos. É aceitável para algo mensal, e é o preço
de ter barra de progresso de verdade.

---

## 1. Gatilho

**Novo fluxo → Fluxo de nuvem automatizado.**

Gatilho: **SharePoint — Quando um item é criado ou modificado**

| campo | valor |
|---|---|
| Endereço do Site | o site do AirportNow |
| Nome da Lista | `tb_importacaoMapa` |

**Agora a trava.** No gatilho: **⋯ → Configurações → Condições de gatilho → Adicionar**:

```
@equals(triggerOutputs()?['body/status'], 'PRONTO')
```

Sem isso o fluxo entra em laço infinito na primeira execução.

---

## 2. Marcar como em processamento

**SharePoint — Atualizar item**

| campo | valor |
|---|---|
| Lista | `tb_importacaoMapa` |
| Id | `ID` (do gatilho) |
| status | `PROCESSANDO` |

Isso também é o que tira o item da condição de gatilho: da próxima modificação ele não volta a disparar.

---

## 3. Pegar o anexo

**SharePoint — Obter anexos**

| campo | valor |
|---|---|
| Lista | `tb_importacaoMapa` |
| Id | `ID` |

**SharePoint — Obter conteúdo do anexo**

| campo | valor |
|---|---|
| Lista | `tb_importacaoMapa` |
| Id | `ID` |
| Identificador do arquivo | `Id` (do "Obter anexos") |

> O "Obter anexos" devolve uma **lista**. O Power Automate vai envolver as ações seguintes num
> `Aplicar a cada` automaticamente. Está certo: a tela limita a um anexo (`MaxAttachments: =1`), então
> o laço roda uma vez só. Deixe assim.

---

## 4. Gravar o anexo numa biblioteca

O conector do Excel **não lê conteúdo binário direto** — precisa de um arquivo com caminho.

**SharePoint — Criar arquivo**

| campo | valor |
|---|---|
| Endereço do Site | o site do AirportNow |
| Caminho da Pasta | `/Documentos Compartilhados/importacoes` |
| Nome do Arquivo | `programacao-@{triggerOutputs()?['body/ID']}.xlsx` |
| Conteúdo do Arquivo | `Conteúdo do arquivo` (do passo 3) |

Nomear pelo `ID` evita duas importações simultâneas sobrescreverem o arquivo uma da outra.

---

## 5. Rodar o script

**Excel Online (Business) — Executar script**

| campo | valor |
|---|---|
| Localização / Biblioteca | onde você gravou no passo 4 |
| Arquivo | `Id` do "Criar arquivo" |
| Script | `Importar programacao` |
| mesRef | `@{formatDateTime(triggerOutputs()?['body/mes_ref'], 'yyyy-MM')}` |

O `mesRef` tem que sair no formato `aaaa-MM`. Digitar `09` não casa com nada e o script devolve zero
registros sem erro nenhum.

---

## 6. Guardar o total e conferir se deu certo

**SharePoint — Atualizar item**

| campo | valor |
|---|---|
| Lista | `tb_importacaoMapa` |
| Id | `ID` |
| total | `@{outputs('Executar_script')?['body/result']?['total']}` |
| mensagem | `@{outputs('Executar_script')?['body/result']?['mensagem']}` |

> Se o nome interno da ação for outro, ajuste o `'Executar_script'`. O nome interno usa sublinhado no
> lugar de espaço — veja em **Código-fonte** (⋯ → Exibição de código) se não tiver certeza.

Vale pôr um **Condition** aqui: se `ok` do retorno for `false`, grave `status = ERRO` com a `mensagem`
e encerre. O script devolve `ok: false` com motivo legível quando a planilha está errada — arquivo
trocado, por exemplo.

---

## 7. Apagar a importação anterior deste mês

Sem este passo, rodar duas vezes duplica ~700 registros.

**SharePoint — Obter itens**

| campo | valor |
|---|---|
| Lista | `tb_alocacoesMapa` |
| Consulta de Filtro | `origem eq 'IMPORTACAO @{formatDateTime(triggerOutputs()?['body/mes_ref'], 'yyyy-MM')}'` |
| Contagem Máxima | `5000` |

Em **⋯ → Configurações**, ligue a **Paginação** com limite 5000 — sem isso vêm só 100 itens e a
limpeza fica pela metade.

**Aplicar a cada** sobre `value` → **SharePoint — Excluir item** (`Id` = `ID` do item).

> Tem que filtrar pela `origem`, não pela `observacao`: `observacao` é coluna Nota, e o SharePoint
> **não aceita filtro OData em coluna de várias linhas**. Filtrar por data seria pior — apagaria
> também o que foi lançado à mão.

---

## 8. Preparar o contador da barra

**Inicializar variável**

| campo | valor |
|---|---|
| Nome | `contador` |
| Tipo | `Inteiro` |
| Valor | `0` |

---

## 9. Gravar os registros

**Aplicar a cada**, sobre:

```
@{outputs('Executar_script')?['body/result']?['registros']}
```

**Antes de pôr as ações dentro, configure o laço:** **⋯ → Configurações → Controle de Simultaneidade
→ Ligado, Grau de paralelismo = 1.** É isso que torna o contador confiável.

Dentro do laço, três ações:

### 9a. SharePoint — Criar item

Lista `tb_alocacoesMapa`. Mapeamento, campo por campo:

| coluna | valor |
|---|---|
| `aeroporto` | `items('Aplicar_a_cada_2')?['aeroporto']` |
| `data_operacao` | `items('Aplicar_a_cada_2')?['data_operacao']` |
| `data_fim` | `items('Aplicar_a_cada_2')?['data_fim']` |
| `id_posicao` | `items('Aplicar_a_cada_2')?['id_posicao']` |
| `posicao_txt` | `items('Aplicar_a_cada_2')?['posicao_txt']` |
| `patio_txt` | `items('Aplicar_a_cada_2')?['patio_txt']` |
| `cia_sigla` | `items('Aplicar_a_cada_2')?['cia_sigla']` |
| `voo_chegada` | `items('Aplicar_a_cada_2')?['voo_chegada']` |
| `voo_saida` | `items('Aplicar_a_cada_2')?['voo_saida']` |
| `equipamento` | `items('Aplicar_a_cada_2')?['equipamento']` |
| `hora_inicio` | `items('Aplicar_a_cada_2')?['hora_inicio']` |
| `hora_fim` | `items('Aplicar_a_cada_2')?['hora_fim']` |
| `portao` | `items('Aplicar_a_cada_2')?['portao']` |
| `tipo_registro` | `items('Aplicar_a_cada_2')?['tipo_registro']` |
| `pesquisado` | `items('Aplicar_a_cada_2')?['pesquisado']` |
| `internacional` | `items('Aplicar_a_cada_2')?['internacional']` |
| `observacao` | `items('Aplicar_a_cada_2')?['observacao']` |
| `origem` | `items('Aplicar_a_cada_2')?['origem']` |
| `ativo` | `items('Aplicar_a_cada_2')?['ativo']` |

`prefixo` e `envergadura_m` ficam **em branco** de propósito: o script não os devolve, e a envergadura
sai do catálogo pelo equipamento.

> ⚠️ **`ativo` tem que ser mapeado.** O default da coluna em produção é `0`, e registro com `ativo = 0`
> **some do app sem erro nenhum** — o filtro do dia exige `ativo = 1`. Foi o que aconteceu quando
> colamos os registros à mão pela grade do SharePoint.

> O `Aplicar_a_cada_2` é só um exemplo de nome. Se o Power Automate chamar o seu laço de outra coisa,
> use o nome real — ou simplesmente escolha o campo pelo **conteúdo dinâmico**, que ele resolve sozinho.

### 9b. Incrementar variável

`contador` += `1`

### 9c. Condition → atualizar a barra a cada 25

Condição:

```
@equals(mod(variables('contador'), 25), 0)
```

No ramo **Se sim** → **SharePoint — Atualizar item**:

| campo | valor |
|---|---|
| Lista | `tb_importacaoMapa` |
| Id | `ID` |
| processados | `variables('contador')` |

De 25 em 25 para não bater no limite de chamadas do SharePoint. A barra anda em degraus de ~3,5% —
mais que suficiente para o operador ver que está andando.

---

## 10. Fechar

**SharePoint — Atualizar item**

| campo | valor |
|---|---|
| Lista | `tb_importacaoMapa` |
| Id | `ID` |
| status | `CONCLUIDO` |
| processados | `variables('contador')` |
| criados | `variables('contador')` |
| pendencias | `@{length(outputs('Executar_script')?['body/result']?['pendencias'])}` |
| mensagem | `@{outputs('Executar_script')?['body/result']?['mensagem']}` |

---

## 11. Tratar falha

No escopo principal ou nas ações críticas: **⋯ → Configurar execução após → marcar "houve falha" e
"expirou"**, apontando para uma **Atualizar item** final com `status = ERRO` e a `mensagem` do erro.

Sem isso, uma falha no meio deixa o item em `PROCESSANDO` para sempre, e a tela fica com a barra
parada sem explicar por quê.

---

## Como testar sem risco

**Não teste com o mês inteiro na primeira vez.** Faça assim:

1. Duplique a planilha de setembro e apague tudo menos **dois ou três dias** de movimentos.
2. Anexe essa planilha reduzida pela tela, com o mês de referência de setembro.
3. Confira: o item vai a `CONCLUIDO`, a barra chega a 100%, e a `tb_alocacoesMapa` recebe umas
   40 linhas com `origem = IMPORTACAO 2026-09`.
4. Abra o **Mapa do Dia** num dos dias importados e veja se a grade desenha.
5. **Rode de novo com a mesma planilha.** O total tem que ficar igual, não dobrar — é o teste do
   passo 7.

Só depois solte o mês completo.

---

## O que ainda não existe

**Pendências não são gravadas em lugar nenhum.** O script devolve a lista com data, voo, rota e motivo,
e o fluxo só conta quantas são. O operador vê o número na tela, mas não *quais*. Para resolver de
verdade faltaria uma lista `tb_pendenciaImportacao` e um laço a mais no fluxo.

Ficou de fora de propósito: são 7 pendências em 700 registros, e enquanto a operação for uma importação
por mês dá para olhar o retorno do script no histórico do fluxo. Se a importação virar rotina de várias
pessoas, isso passa a incomodar rápido.
