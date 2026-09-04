# Fluxo `Mapa - Expurgo Diário`

Único fluxo do sistema. É **agendado** — nunca chamado pelo app. Isso evita as duas armadilhas conhecidas:
tela travada esperando resposta de fluxo, e esquema de gatilho que muda e obriga a remover/re-adicionar a
conexão, com o Studio renomeando o fluxo para `_1` e quebrando o YAML.

## O que ele faz

| Fase | Condição | Ação | Efeito |
|---|---|---|---|
| 1 — ocultar | `data_fim` < hoje − **7 dias** e `ativo` = 1 | `ativo` = 0 | Sai do app; ainda recuperável pela view `⚠ Inativos` |
| 2 — apagar | `data_fim` < hoje − **30 dias** | Excluir item | Sai de vez |

> ⚠️ **A janela conta pela `data_fim`, nunca pela `data_operacao`.** Desde que o registro passou a poder
> cruzar dias, `data_operacao` é só o começo da ocupação: uma interdição lançada há 40 dias que termina
> amanhã ainda está valendo. Filtrar por `data_operacao` apagaria essa interdição enquanto ela ainda está
> em vigor, **sem erro nenhum** — o fluxo roda verde e o bloco some da grade de todo mundo. Para o registro
> de um dia só as duas colunas são iguais e o comportamento não muda.

A janela de 7 dias dá margem para desfazer um engano; a de 30 mantém a lista em torno de **1.500 itens**,
folgadamente abaixo do limite de 5.000 da view, e o filtro do dia continua rápido.

## Montagem

**Novo fluxo de nuvem → Agendado.** Nome: `Mapa - Expurgo Diário`. Repetir a cada **1 dia**, às **03:00**,
fuso `(UTC-03:00) Brasília`.

### Fase 1 — ocultar o que passou de 7 dias

**Ação:** *SharePoint → Obter itens*
- Endereço do site: o site do app
- Nome da lista: `tb_alocacoesMapa`
- **Consulta de filtro:**
  ```
  ativo eq 1 and data_fim lt '@{formatDateTime(addDays(utcNow(), -7), 'yyyy-MM-dd')}'
  ```
- Configurações → **Paginação ligada**, limite `5000`

**Ação:** *Aplicar a cada* → saída `value`
- Dentro: *SharePoint → Atualizar item*
  - Id: `@{items('Aplicar_a_cada')?['ID']}`
  - `ativo`: `0`
  - Deixar **todos os outros campos vazios** — campo preenchido à toa reescreve o registro e muda o
    `Modificado`, o que faria o app de todo mundo mostrar a faixa "a programação foi alterada" às 3 da manhã.
- Simultaneidade: **1** (evita corrida com a operação)

### Fase 2 — apagar o que passou de 30 dias

**Ação:** *SharePoint → Obter itens* (segunda instância)
- Nome da lista: `tb_alocacoesMapa`
- **Consulta de filtro:**
  ```
  data_fim lt '@{formatDateTime(addDays(utcNow(), -30), 'yyyy-MM-dd')}'
  ```
- Paginação ligada, limite `5000`

**Ação:** *Aplicar a cada* → *SharePoint → Excluir item*
- Id: `@{items('Aplicar_a_cada_2')?['ID']}`
- Simultaneidade: **1**

### Tratamento de falha

Na última ação, *Configurar execução após* → marcar **falhou** e **atingiu o tempo limite**, e ligar um
**Enviar email (V2)** para a caixa da equipe de sistemas com o link da execução. O expurgo pode falhar em
silêncio por semanas sem ninguém notar — até a lista passar de 5.000 itens e a view parar de filtrar.

## Conferência

- [ ] Rodar **manualmente** uma vez com a lista contendo um item de data antiga forjada e conferir as duas fases
- [ ] Conferir que a fase 1 muda **só** o `ativo` — abrir o histórico de versões do item e confirmar que
      nenhum outro campo foi tocado
- [ ] Conferir que a view `⚠ Inativos` mostra o que a fase 1 ocultou
- [ ] Conferir que o app não exibe o item oculto (o filtro do dia é `ativo = 1`)
- [ ] Deixar rodar uma noite e conferir o histórico de execuções
- [ ] Conferir que ninguém recebeu a faixa "a programação foi alterada" na manhã seguinte
- [ ] Forjar uma interdição com `data_operacao` de 40 dias atrás e `data_fim` de amanhã, rodar o fluxo e
      confirmar que ela **continua na lista** — é o teste que pega o filtro trocado para `data_operacao`

## Se um dia a retenção mudar

As duas janelas estão em `addDays(utcNow(), -7)` e `addDays(utcNow(), -30)`, uma em cada *Obter itens*. São os
dois únicos lugares a mexer. O texto que o usuário lê sobre a retenção está em `scrMapaInicio`, no controle
`htmRodapeIni` — atualizar junto.
