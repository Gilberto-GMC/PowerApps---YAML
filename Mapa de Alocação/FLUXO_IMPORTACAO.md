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
