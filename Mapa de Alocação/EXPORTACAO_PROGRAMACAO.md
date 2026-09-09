# Exportação da programação — item 6 da supervisão

Gera um CSV da movimentação de um período, com filtros, que abre direto no Excel. Serve para enviar a
programação a quem não usa o app e para consultar o que já passou — **não** é ciclo de reimportação.
Isso foi decidido: o importador existente lê programação de companhia e *calcula* posição; exportar
naquele formato jogaria fora exatamente o trabalho que o app faz.

## Desenho

Três peças, no mesmo padrão da importação:

| peça | o quê |
|---|---|
| lista `tb_exportacaoMapa` | a fila de pedidos. O app escreve um pedido, o fluxo responde nele |
| tela (parte de baixo da `scrMapaImport`) | filtros, botão GERAR, e a lista dos últimos pedidos |
| fluxo `Exportar programacao` | lê os filtros, monta o CSV, grava na biblioteca, devolve o link |

**A tela não chama o fluxo por nome.** Ela grava um registro com `status = PRONTO` e o fluxo dispara
na criação do item. É de propósito: chamar por nome (`Fluxo.Run(...)`) faria a colagem da tela falhar
enquanto o fluxo não existisse, e amarraria o YAML ao nome exato que o fluxo tem no ambiente.

## Ordem de instalação

1. Criar a lista `tb_exportacaoMapa` pelo `lista_tb_exportacaoMapa.json`.
2. **Adicionar a lista ao app como fonte de dados** no Studio.
3. Colar a `scrMapaImport.pa.yaml`. *(Sem os passos 1 e 2 a colagem falha: o YAML cita a lista.)*
4. Montar o fluxo abaixo.

Até o fluxo existir, a tela funciona e os pedidos ficam em `PRONTO` — nada quebra, só não sai arquivo.

## Colunas da lista de pedidos

Obrigatórias: **só** `aeroporto`, `status` e `ativo`. Todas as outras são opcionais, de propósito —
na `tb_importacaoMapa` oito colunas obrigatórias tornaram cada `Atualizar item` do fluxo um exercício
de repreencher campos que não mudaram. Aqui o `Atualizar item` precisa devolver apenas essas três.

## Caminho curto: importar o pacote

`Exportarprogramacao.zip` traz o fluxo montado. Em **Power Automate › Meus fluxos › Importar › Pacote
(.zip)**, escolha o arquivo, confirme a conexão do SharePoint como **Existente** e importe.

**Antes de rodar, crie a pasta `exportacoes`** na biblioteca *Documentos Compartilhados* do site. O
`Criar arquivo` grava lá e não cria a pasta sozinho — se ela faltar, o pedido vira `ERRO` com a
mensagem, que é o comportamento certo, mas custa uma volta.

O pacote foi montado sobre o `Importarprogramacao_COMPLETO.zip`, que já entrou neste ambiente:
mesmas referências de conexão, entradas com `/` e na mesma ordem, e `suggestedCreationType: New`. O
gerador está versionado em `montar_zip_exportacao.js`.

⚠️ **Duas coisas que só o primeiro teste responde**, porque não há como conferir daqui:

1. `arquivo_url` é montado como `https://grupoccr.sharepoint.com` + o `Path` devolvido pelo
   `Criar arquivo`. Se o botão ABRIR O ÚLTIMO não abrir nada, é aqui — o campo pode vir num formato
   diferente e a correção é trocar `Path` por `{Link}` na ação `Concluir`.
2. O nome da lista é usado no lugar do GUID (`table: "tb_exportacaoMapa"`). Isso **funciona** no fluxo
   de importação, que usa `tb_alocacoesMapa` assim há dias — mas se o gatilho reclamar da lista, é
   só reabrir a ação e escolhê-la no menu, que o designer troca pelo GUID.

---

## O fluxo, passo a passo — referência

O pacote acima já traz tudo isto montado. Esta seção fica para conferir o que cada ação faz, e para
remontar à mão se o pacote for recusado.

**Gatilho:** SharePoint › *Quando um item é criado* › site do AirportNow › lista `tb_exportacaoMapa`.

> Só *criado*, não *criado ou modificado*. O fluxo escreve de volta no mesmo item, e com o gatilho de
> modificação isso viraria laço infinito.

---

**1. Atualizar item — marcar como PROCESSANDO**

Lista `tb_exportacaoMapa`, Id = `ID` do gatilho. Preencher os três obrigatórios:

- `aeroporto` = `aeroporto` do gatilho
- `status` = `PROCESSANDO`
- `ativo` = `1`

---

**2. Obter itens — a programação do período**

Lista `tb_alocacoesMapa`. **Consulta de filtro:**

```
aeroporto eq '@{triggerOutputs()?['body/aeroporto']}' and ativo eq 1 and data_operacao ge '@{formatDateTime(triggerOutputs()?['body/data_de'],'yyyy-MM-dd')}' and data_operacao le '@{formatDateTime(triggerOutputs()?['body/data_ate'],'yyyy-MM-dd')}'
```

**Contagem máxima: 5000.** E ligue *Obter todos* (paginação) nas configurações da ação — sem isso ela
para em 100 itens, que é o mesmo tipo de teto silencioso que já nos custou uma sessão inteira.

> Os filtros opcionais (internacional, pesquisado, finalizados, pátio) **não** entram aqui. Ficam no
> passo 3, porque montar OData condicional à mão é onde esse fluxo quebraria.

---

**3. Filtrar matriz — aplicar os filtros opcionais**

De: `@{outputs('Obter_itens')?['body/value']}`

Condição, em **modo avançado**, colada inteira:

```
@and(or(equals(triggerOutputs()?['body/so_internacional'], 0), equals(item()?['internacional'], 1)), or(equals(triggerOutputs()?['body/so_pesquisado'], 0), equals(item()?['pesquisado'], 1)), or(equals(triggerOutputs()?['body/incluir_finalizados'], 1), not(equals(item()?['condicao'], 'FINALIZADO'))), or(empty(triggerOutputs()?['body/patio']), equals(item()?['patio_txt'], triggerOutputs()?['body/patio'])))
```

Cada linha diz "ou o filtro está desligado, ou o registro passa nele".

---

**4. Selecionar — uma linha de texto por registro**

De: `@{body('Filtrar_matriz')}`

Clique no ícone à direita do mapa para **alternar para modo de texto** (a saída passa a ser uma lista
de strings em vez de objetos). No campo único, cole:

```
@{concat('"',formatDateTime(item()?['data_operacao'],'dd/MM/yyyy'),'";"',item()?['posicao_txt'],'";"',item()?['patio_txt'],'";"',formatNumber(div(item()?['hora_inicio'],60),'00'),':',formatNumber(mod(item()?['hora_inicio'],60),'00'),'";"',formatNumber(div(item()?['hora_fim'],60),'00'),':',formatNumber(mod(item()?['hora_fim'],60),'00'),'";"',item()?['tipo_registro'],'";"',coalesce(item()?['cia_sigla'],''),'";"',coalesce(item()?['voo_chegada'],''),'";"',coalesce(item()?['voo_saida'],''),'";"',coalesce(item()?['prefixo'],''),'";"',coalesce(item()?['equipamento'],''),'";"',coalesce(item()?['portao'],''),'";"',coalesce(item()?['condicao'],'PREVISTO'),'";"',if(equals(item()?['internacional'],1),'SIM','NAO'),'";"',if(equals(item()?['pesquisado'],1),'SIM','NAO'),'";"',if(equals(item()?['alternativa'],1),'SIM','NAO'),'";"',coalesce(item()?['responsavel'],''),'";"',coalesce(item()?['contato'],''),'";"',replace(coalesce(item()?['observacao'],''),'"',''''),'"')}
```

**Por que montar a linha à mão em vez de usar *Criar tabela CSV*:** aquela ação separa por vírgula, e
o Excel em português espera **ponto e vírgula**. Um CSV com vírgulas abre com tudo numa coluna só.

Cada campo sai entre aspas, então ponto e vírgula dentro de uma observação não quebra a coluna. As
aspas que houver na observação viram apóstrofo — é o único campo livre e o único que precisa disso.

---

**5. Criar arquivo**

Biblioteca do site (a mesma da importação serve). 

- **Nome:** `@{concat('programacao_', triggerOutputs()?['body/aeroporto'], '_', formatDateTime(triggerOutputs()?['body/data_de'],'yyyyMMdd'), '_a_', formatDateTime(triggerOutputs()?['body/data_ate'],'yyyyMMdd'), '.csv')}`
- **Conteúdo:**

```
@{concat(decodeUriComponent('%EF%BB%BF'),'"Data";"Posicao";"Patio";"Inicio";"Fim";"Tipo";"Companhia";"Voo chegada";"Voo saida";"Prefixo";"Equipamento";"Portao";"Condicao";"Internacional";"Pesquisado";"Alternativa";"Responsavel";"Contato";"Observacao"',decodeUriComponent('%0D%0A'),join(body('Selecionar'),decodeUriComponent('%0D%0A')))}
```

O `%EF%BB%BF` é a marca UTF-8. **Sem ela o Excel abre "Navegantes" como "NavegaÃ§Ã£o"** — e o operador
conclui que o arquivo está corrompido. É um detalhe de três bytes que decide se a entrega serve.

---

**6. Atualizar item — concluir**

Lista `tb_exportacaoMapa`, Id do gatilho:

- `aeroporto` = do gatilho · `ativo` = `1` · `status` = `CONCLUIDO`
- `total` = `@{length(body('Filtrar_matriz'))}`
- `arquivo_nome` = `Name` da ação Criar arquivo
- `arquivo_url` = `Path` (ou o link do item) da ação Criar arquivo

---

**7. Atualizar item — em caso de erro**

Acrescente uma última ação `Atualizar item` e, no menu ⋯ dela, **Configurar execução após** →
marque apenas *falhou* e *tempo limite atingido* do passo 5. Preencha:

- `aeroporto` = do gatilho · `ativo` = `1` · `status` = `ERRO`
- `mensagem` = `@{result('Criar_arquivo')}`

Sem esse ramo, uma falha deixa o pedido eternamente em `PROCESSANDO` e o operador não sabe se espera
ou refaz.

## Limites, e por que estão onde estão

**Período máximo de 62 dias por arquivo.** A trava está na tela, e é sobre o app, não sobre o fluxo:
a contagem que a tela mostra antes de gerar é lida no cliente, sujeita ao limite de linhas do app
(2000). Com um mês típico de ~705 registros, 62 dias cabem com folga e a conta bate; acima disso a
tela mostraria um número menor que o real sem dizer que truncou.

⚠️ **O `62` está escrito na tela, não no `App.Formulas`** — contra a convenção do projeto, que é
manter constante em um lugar só. Foi para não custar mais uma colagem agora. **Move na próxima vez que
o `App_Formulas_Mapa.txt` for ao Studio por outro motivo**, como `mapExportDiasMax`. Mesma regra do
`ASUR BRASIL`.

## Verificação

1. Pedir um dia que você conhece e conferir a contagem do arquivo contra o "N registro(s)" da grade.
2. Abrir no Excel e conferir se **as colunas separaram** e se os acentos saíram certos — são os dois
   defeitos que o formato causa, e ambos aparecem na primeira linha.
3. Pedir um período com `Somente internacionais` ligado e conferir que o total cai.
4. Pedir um período **futuro** — é metade do pedido dele ("para planejar algo que irá acontecer") e é
   o caso que passa despercebido se só se testar com histórico.
5. Forçar um erro (apagar a biblioteca de destino por um instante) e conferir que o pedido vira `ERRO`
   com mensagem, em vez de ficar preso em `PROCESSANDO`.
