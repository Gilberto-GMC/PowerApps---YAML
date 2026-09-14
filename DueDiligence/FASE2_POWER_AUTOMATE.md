# Due Diligence — Fase 2

## Contrato aprovado

- A fonte funcional é a planilha `Canal Confidencial.url` (arquivo XLSX com extensão incorreta).
- O questionário v2 do terceiro é categórico; `pontuacao_terceiro` não participa da regra v2.
- Sete perguntas podem produzir `Risco Alto`.
- Qualquer gatilho crítico do solicitante ou do terceiro resulta em risco `Alto` e `FLUXO III`, mesmo havendo obrigação legal: o gatilho tem peso maior que a obrigação legal.
- Sem gatilho crítico, a obrigação legal mantém a precedência e encerra no Fluxo I.
- Toda resposta válida de uma solicitação do Fluxo III segue para `Pendente Compliance`, mesmo quando `terceiro_gatilho_risco = "Não"`.
- As decisões do parecer final são `Aprovado`, `Aprovado com Ressalvas`,
  `Reprovado Parcialmente` e `Reprovado` (grafia exata; ver o modelo abaixo).

## Modelo de status (2026-09-10)

O Compliance reduziu o ciclo a oito status. A grafia é contrato: o app compara
texto com `=`, que diferencia maiúsculas de minúsculas.

| Status | Quem define | Quando |
|---|---|---|
| `Aguardando Terceiro` | App | Solicitação criada no Fluxo III; o questionário segue para o terceiro. |
| `Pendente Compliance` | DD02 | Resposta válida do terceiro. Permanece durante toda a análise. |
| `Aprovado` | App ou Compliance | Automático nos Fluxos I e II (e no v1 com encerramento por risco baixo) ou parecer do Compliance. |
| `Aprovado com Ressalvas` | Compliance | Parecer final; exige condicionantes e prazo de reavaliação. |
| `Reprovado Parcialmente` | Compliance | Parecer final. |
| `Reprovado` | Compliance | Parecer final. |
| `Cancelado` | Compliance | A partir de `Aguardando Terceiro` ou `Pendente Compliance`. |
| `Vencido` | DD03 | Fim da vigência: 1 ano (risco alto), 2 (médio) e 3 (baixo). |

O Fluxo II continua identificado por `fluxo_classificacao = "FLUXO II"` e risco
`Alto`; por isso vence em 1 ano. No resumo da solicitação, a aprovação
automática aparece como "Aprovação automática (FLUXO I/II)", sem status próprio.

### Vigência

- `data_vencimento` (coluna nova, somente data) = data da aprovação + 1, 2 ou 3
  anos conforme `classificacao_risco`: `Alto` ou vazio = 1, `Médio` = 2,
  `Baixo` = 3.
- O app grava a data na aprovação automática e no parecer final. Recebem
  vigência `Aprovado`, `Aprovado com Ressalvas` e `Reprovado Parcialmente`;
  `Reprovado` e `Cancelado` não vencem.
- O DD03 preenche a data que faltar (registros antigos) e marca `Vencido` quando
  ela fica para trás. Para renovar, abre-se uma nova solicitação.

### Estados técnicos que deixaram de ser status

O envio ao terceiro é controlado pelo par `forms_envio_id` /
`forms_envio_processado_id`. Dentro de `Aguardando Terceiro`, o app mostra:

| Situação exibida | Condição |
|---|---|
| Envio em processamento | `forms_envio_id` diferente de `forms_envio_processado_id` |
| Falha no envio | IDs iguais e `data_envio_terceiro` vazia |
| Enviado | IDs iguais e `data_envio_terceiro` preenchida |

A cada reenvio, o app gera um novo `forms_envio_id` e limpa
`data_envio_terceiro`. Com falha no envio, o solicitante pode editar a
solicitação (por exemplo, para corrigir o e-mail); ao salvar, um novo envio é
solicitado automaticamente.

### Migração dos status existentes

| Status antigo | Status novo |
|---|---|
| `Aguardando envio ao terceiro`, `Aguardando terceiro` | `Aguardando Terceiro` |
| `Erro no envio ao terceiro` | `Aguardando Terceiro` (ver o passo 4) |
| `Rascunho` (o app não grava; só se existir) | `Aguardando Terceiro` |
| `Em análise Compliance`, `Aguardando esclarecimento`, `Em homologação` | `Pendente Compliance` |
| `Encerrado - risco baixo`, `Aprovado automaticamente - Fluxo I`, `Cadastrado - monitoramento (Fluxo II)` | `Aprovado` |
| `Aprovado com ressalvas` | `Aprovado com Ressalvas` |
| `Reprovado parcialmente` | `Reprovado Parcialmente` |

Ordem obrigatória:

1. Criar a coluna `data_vencimento` (Data e Hora, somente data, indexada) na
   `tb_dueDiligence`. Sem ela, a tela não compila.
2. Importar os três pacotes (DD02, DD01 e DD03) e ativá-los.
3. Colar a tela nova no Studio.
4. Trocar os status na visão em grade do SharePoint (filtrar por status e colar
   o valor novo). Em `Erro no envio ao terceiro`, copie **primeiro**
   `forms_envio_id` para `forms_envio_processado_id` e só **depois** troque o
   status; na ordem inversa, o DD01 reenvia o e-mail sozinho. Registros em
   `Aguardando envio ao terceiro` são enviados assim que o status muda: esse é o
   comportamento esperado.
5. Na primeira execução, o DD03 calcula `data_vencimento` das aprovações antigas
   a partir de `data_decisao_compliance`, `data_conclusao` ou `Created` e marca
   como `Vencido` o que já passou da vigência.

O histórico (`tb_dueDiligenceDesdobramentos`) mantém os status antigos, porque
registra o que aconteceu.

## Valores que ainda precisam ser configurados

| Configuração | Valor |
|---|---|
| Site SharePoint | `https://grupoccr.sharepoint.com/sites/ComplianceAeroportos` |
| Form ID do Microsoft Forms | `itUz0nOZp0OvaWdjYwVIoMoEbKAMYIZFqUAdth6B_EFURVRKSFdaVDE4Q1RIV0VTRkxFSjFZS0VEQS4u` |
| Pergunta de correlação | `Código de acompanhamento` (`rf6e81f83fe194d4c80dbfd30fc7b8301`) |
| URL do Código de Ética aprovada pelo Compliance | `PREENCHER_URL_CODIGO_ETICA` |
| URL do Canal Confidencial da ASUR Brasil | `PREENCHER_URL_CANAL_CONFIDENCIAL` |
| Fonte que autoriza o perfil Compliance | Lista `tb_dueDiligenceCompliance` (`email` = login do usuário, `ativo = 1`) |

## Pacotes dos fluxos

- `ProcessarrespostaDueDiligence_PRONTO.zip`: DD02, importar primeiro e mapear
  as conexões Microsoft Forms e SharePoint.
- `EnviarquestionarioDueDiligence_PRONTO.zip`: DD01, importar depois e mapear
  as conexões SharePoint e Office 365 Outlook.
- `VencervigenciaDueDiligence_PRONTO.zip`: DD03, importar por último, como
  **Criar como novo**, e mapear a conexão SharePoint. Não existe rascunho para
  atualizar.

Para DD01 e DD02, na importação legada, selecionar **Atualizar** e apontar para
os dois fluxos rascunho existentes. Não criar cópias, pois isso deixaria
gatilhos duplicados.
Depois da importação, abrir cada fluxo, salvar e ativar. O gerador reproduzível
está em `build_power_automate_flows.py`; as definições expandidas ficam em
`PowerAutomate/`.

O PDF oficial do Grupo ASUR localizado é
<https://www.asur.com.mx/media/Inversionistas/ASUR-Aeropuertos-Codigo-de-Etica-20.pdf>.
Ele não deve ser publicado como Código de Ética do Fornecedor da ASUR Brasil
sem aprovação do Compliance. Não foi localizado um portal público oficial do
Canal Confidencial específico para o Brasil.

## Migração das listas existentes

Os três JSONs completos foram atualizados para instalações novas. O
`List_Generator` atual recusa listas existentes; portanto, não execute os JSONs
completos novamente sobre listas com dados.

Para listas existentes, a migração deve ser aditiva e idempotente:

1. Consultar cada campo pelo `InternalName`.
2. Criar somente campos ausentes com o `schemaXml` correspondente no JSON completo.
3. Criar os novos campos inicialmente como opcionais.
4. Preencher `forms_correlacao_id` com um GUID diferente em cada registro já existente.
5. Confirmar que não existem valores duplicados.
6. Somente então tornar `forms_correlacao_id` obrigatório, indexado e único.
7. Na `tb_dueDiligenceTerceiroRespostas`, adicionar os sete campos novos e
   atualizar os campos já existentes conforme o JSON: `codigo_pergunta` passa
   a aceitar 40 caracteres, e `codigo_pergunta`, `texto_pergunta`, `resposta`,
   `classificacao` e `data_resposta` passam a ser obrigatórios.
8. Se essa lista continuar comprovadamente vazia, o caminho mais simples é
   excluí-la e recriá-la pelo JSON completo atualizado. Não faça isso se já
   houver qualquer resposta.
9. Aplicar a unicidade de `forms_item_chave` somente após validar os dados
   existentes.
10. Inserir os 21 parâmetros por upsert usando a chave composta
   `(versao_questionario, codigo_pergunta, codigo_opcao)`.
11. Criar `data_vencimento` na `tb_dueDiligence` conforme o JSON completo
   (`DateTime`, `Format='DateOnly'`, indexada).

Não usar `<Validation>` no `CreateFieldAsXml`.

## Perguntas e códigos estáveis

Os códigos não repetem o `T3` duplicado da planilha. O texto mostrado no Forms
pode continuar igual ao documento aprovado; o fluxo e o SharePoint usam os
códigos abaixo.

| Ordem | Código | Regra |
|---:|---|---|
| 1 | `terceiro_t01` | Sim/Não → `Risco Baixo` |
| 2 | `terceiro_t01_2` | Condicional a T1=Sim; Sim/Não → `Risco Baixo` |
| 3 | `terceiro_t02` | Sim → `Risco Alto`; Não → `Risco Baixo` |
| 4 | `terceiro_t03_pep` | Sim → `Risco Alto`; Não → `Risco Baixo` |
| 5 | `terceiro_t03_processos` | Sim → `Risco Alto`; Não → `Risco Baixo` |
| 6 | `terceiro_t04` | Sim → `Risco Alto`; Não → `Risco Baixo` |
| 7 | `terceiro_t05` | Texto livre → `Sem pontuação` |
| 8 | `terceiro_t06` | Sim → `Risco Alto`; Não → `Risco Baixo` |
| 9 | `terceiro_t07` | Sim → `Risco Alto`; Não → `Risco Baixo` |
| 10 | `terceiro_t08` | Sim → `Risco Alto`; Não → `Risco Baixo` |
| 11 | `terceiro_t09` | Sim/Não → `Sem pontuação` |

T1.2 não deve ser contada quando T1=`Não`. Uma resposta completa contém dez
linhas nesse caso e onze quando T1=`Sim`.

Além das perguntas de negócio, o Forms recebe apenas uma pergunta obrigatória:
`Código de acompanhamento`. O link enviado pelo DD01 preenche essa pergunta com
o `forms_envio_id` atual. O `solicitacao_id` e o `forms_correlacao_id` não são
pedidos ao terceiro: o DD02 os recupera da `tb_dueDiligence` depois de localizar
exatamente um registro pelo código.

### Ativação obrigatória do preenchimento no Forms

Não basta acrescentar o ID da pergunta manualmente à URL. Antes do primeiro
envio, abra o formulário como proprietário e use `...` →
`Obter URL pré-preenchida` (`Get a pre-filled URL`). Marque a opção para
habilitar o preenchimento, informe qualquer valor de teste em
`Código de acompanhamento` e clique em `Obter link pré-preenchido`. O valor de
teste pode ser descartado: esse procedimento habilita `AllowPrefill` no
formulário.

O DD01 já monta o endereço com `origin=lprLink` e substitui o valor de teste
pelo `forms_envio_id` de cada solicitação. Se a ativação acima não for feita, o
parâmetro aparece na barra de endereço, mas o Forms deixa a pergunta vazia.

O código continua visível e editável no Forms. Ele serve para correlação, não
como prova de identidade; o DD02 rejeita código inexistente, duplicado, antigo
ou que não pertença a uma solicitação em `Aguardando Terceiro` no `FLUXO III`.

O `responseId` devolvido pelo gatilho do Forms pode ser numérico. Nos corpos
REST enviados ao SharePoint, o DD02 converte explicitamente esse valor e todos
os demais campos `Text`/`Note` com `string()`. Não remova essas conversões: o
SharePoint rejeita números em colunas `Edm.String` com HTTP 400.

## Fluxo DD01 — enviar questionário

### Gatilho

SharePoint: `When an item is created or modified`, lista `tb_dueDiligence`.
Configure concorrência do gatilho como `1` e use:

```text
@and(
  equals(triggerBody()?['status'], 'Aguardando Terceiro'),
  not(empty(triggerBody()?['forms_envio_id'])),
  not(equals(
    triggerBody()?['forms_envio_id'],
    triggerBody()?['forms_envio_processado_id']
  ))
)
```

### Caminho principal

1. `Get item` pelo `ID` do gatilho.
2. Revalidar no item atual:
   - status = `Aguardando Terceiro`;
   - `forms_envio_id` preenchido;
   - `forms_envio_id <> forms_envio_processado_id`;
   - `forms_correlacao_id` preenchido;
   - `email_terceiro` preenchido.
3. Montar o link do Forms preenchendo `rf6e81f83fe194d4c80dbfd30fc7b8301`
   com o `forms_envio_id` atual usando `uriComponent()`.
4. Enviar o e-mail em HTML ao `email_terceiro`.
5. Atualizar o item principal:
   - `forms_formulario_id = itUz0nOZp0OvaWdjYwVIoMoEbKAMYIZFqUAdth6B_EFURVRKSFdaVDE4Q1RIV0VTRkxFSjFZS0VEQS4u`;
   - `forms_envio_processado_id = forms_envio_id`;
   - `data_envio_terceiro = utcNow()`.

   O status não é regravado: já é `Aguardando Terceiro`, e regravá-lo
   desfaria um cancelamento feito entre a leitura e esta atualização.
6. Criar desdobramento `Envio ao terceiro`, incluindo o identificador da
   intenção de envio na descrição.

Use retry `None` no envio de e-mail. Um timeout depois de o Outlook aceitar a
mensagem não fornece um identificador que permita provar se o e-mail saiu; um
retry automático pode duplicá-lo. O reenvio deve ser uma nova intenção criada
pelo botão do app.

### Erro

Dentro de um Scope `Catch`, configurado com `run after` para falha/timeout,
somente se o `forms_envio_id` ainda for o mesmo:

- gravar `forms_envio_processado_id = forms_envio_id` (consome a intenção) e
  manter `data_envio_terceiro` vazia, que é como o app mostra "Falha no envio";
- registrar o desdobramento `Falha no envio ao terceiro`, visível ao
  solicitante, com o run id;
- finalizar com `Terminate = Failed`.

Consumir a intenção é obrigatório. O gatilho é "item criado ou modificado" com a
condição `forms_envio_id <> forms_envio_processado_id`; sem o consumo, qualquer
alteração posterior no item reenviaria o e-mail sem ninguém pedir.

## Fluxo DD02 — processar resposta

### Gatilho e correlação

1. Microsoft Forms: `When a new response is submitted`.
   Configure a concorrência do gatilho como `1`.
2. `Get response details`, usando o `Response Id` do gatilho.
3. Obter o `forms_envio_id` da resposta `Código de acompanhamento`.
4. Localizar na `tb_dueDiligence` exatamente um item cujo `forms_envio_id`
   corresponda ao código. Recuperar desse item o `ID` da solicitação e o
   `forms_correlacao_id`.
5. Se `forms_ultima_resposta_id` já for igual ao `Response Id`, terminar com
   sucesso como no-op antes de validar o status. Isso torna uma repetição do
   gatilho inofensiva mesmo depois de o registro já estar em
   `Pendente Compliance`.
6. Rejeitar a resposta se `forms_envio_id <> forms_envio_processado_id`, se o
   fluxo não for `FLUXO III`, se o status não for `Aguardando Terceiro` ou se
   qualquer resposta obrigatória estiver vazia/inválida.

### Normalização e idempotência

Criar um array com uma linha por resposta:

```json
{
  "solicitacao_id": 123,
  "codigo_pergunta": "terceiro_t03_pep",
  "codigo_opcao": "terceiro_t03_pep_sim",
  "texto_pergunta": "Texto integral exibido no Forms",
  "resposta": "Sim",
  "classificacao": "Risco Alto",
  "data_resposta": "2026-09-08T12:00:00Z",
  "versao_questionario": 2,
  "ordem": 4,
  "forms_formulario_id": "FORM_ID",
  "forms_resposta_id": "RESPONSE_ID",
  "forms_envio_id": "ENVIO_ID",
  "forms_item_chave": "FORM_ID|RESPONSE_ID|terceiro_t03_pep",
  "ativo": 1
}
```

A classificação deve vir dos registros v2 de
`tb_dueDiligenceParametros`, nunca de texto hardcoded no fluxo. Para cada linha:

1. localizar por `versao_questionario=2`, `codigo_pergunta`, `codigo_opcao` e `ativo=1`;
2. exigir exatamente um parâmetro;
3. procurar `forms_item_chave` na lista de respostas;
4. atualizar a linha existente ou criar uma nova;
5. processar sequencialmente.

A unicidade de `forms_item_chave` é a última barreira contra execuções repetidas
do gatilho.

### Consolidação do pai

Depois de persistir e reler todas as linhas da resposta:

1. Validar dez respostas obrigatórias e T1.2 somente quando T1=`Sim`.
2. Definir `_terceiroAlto` quando existir ao menos uma classificação
   `Risco Alto`.
3. Atualizar `tb_dueDiligence`:
   - `terceiro_gatilho_risco = if(_terceiroAlto, 'Sim', 'Não')`;
   - `classificacao_risco = 'Alto'` quando `_terceiroAlto`; caso contrário,
     recalcular/preservar a classificação do solicitante;
   - `risco_final = 'Alto (gatilho do terceiro)'` quando `_terceiroAlto`;
   - `data_resposta_terceiro = utcNow()`;
   - `forms_ultima_resposta_id = Response Id`;
   - `status = Pendente Compliance`.
4. Não preencher `pontuacao_terceiro` no v2.
5. Criar desdobramento `Resposta do terceiro` com o total de respostas e a
   quantidade classificada como risco alto.

O pai só pode ser atualizado depois de as dez/onze linhas terem sido confirmadas.

## Fluxo DD03 — vencer vigência

Gatilho: recorrência diária às 06:00 (`E. South America Standard Time`),
concorrência 1. Não há rascunho: o pacote é gerado a partir do molde do DD01 e
deve ser importado como fluxo novo.

1. `Hoje_Local`: data de hoje em Brasília.
2. Preencher vencimentos ausentes: itens em `Aprovado`, `Aprovado com Ressalvas`
   ou `Reprovado Parcialmente` com `data_vencimento` vazia recebem a data de
   partida + 1, 2 ou 3 anos conforme o risco. A data de partida é
   `data_decisao_compliance`, senão `data_conclusao`, senão `Created`.
3. Vencer: os mesmos status com `data_vencimento` anterior a hoje passam a
   `Vencido`, com o desdobramento `Vencimento da vigência` visível ao
   solicitante.
4. A etapa 3 roda mesmo que a 2 falhe; a execução termina como falha se
   qualquer etapa falhar, para aparecer no histórico de execuções.

A data é gravada ao meio-dia UTC para não recuar um dia na coluna "somente
data". As consultas usam `$top=5000`; acima do limite de exibição da lista,
indexe `status` e `data_vencimento`.

## Decisão do Compliance

Campos atuais do cabeçalho:

- `decisao_compliance`;
- `condicionantes_compliance`;
- `justificativa_compliance`;
- `decisao_compliance_por_email`;
- `data_decisao_compliance`;
- `prazo_reavaliacao`.

Mapeamento:

| Decisão | Status |
|---|---|
| `Aprovado` | `Aprovado` |
| `Aprovado com Ressalvas` | `Aprovado com Ressalvas` |
| `Reprovado Parcialmente` | `Reprovado Parcialmente` |
| `Reprovado` | `Reprovado` |

A decisão e a justificativa são obrigatórias. Na aprovação com ressalvas,
condicionantes e prazo de reavaliação também são obrigatórios. O parecer grava
`data_vencimento` quando a decisão abre vigência.

O perfil Compliance vem da lista `tb_dueDiligenceCompliance`
(`listgen_tb_dueDiligenceCompliance.json`). É do Compliance quem tem uma linha
com `email` igual ao login do usuário (`User().Email`, em minúsculas) e
`ativo = 1`. As três telas calculam o perfil no próprio `OnVisible`, com chave
não vazia e falha fechada: qualquer erro na consulta resulta em "não é
Compliance".

Só esse perfil vê a ação `Analisar`, o painel de desdobramentos, as notas
internas, o resumo da avaliação, as colunas de pontuação e risco da lista de
registros e o painel de indicadores. O formulário principal continua somente
leitura durante todo o ciclo interno; a única exceção é a falha no envio ao
terceiro.

Implantação da lista:

1. Criar a lista pelo List_Generator com o JSON.
2. Permissões da lista: interromper a herança, dar **Leitura** a todos os
   usuários do app (o app precisa consultá-la) e **Edição** só ao Compliance.
   Sem isso, qualquer pessoa poderia se incluir.
3. Cadastrar cada analista com o login exatamente como o app o enxerga. Quem
   não está cadastrado vê esse login no aviso do painel de indicadores.
4. Adicionar `tb_dueDiligenceCompliance` como fonte de dados do app **antes**
   de colar as telas.

Fluxo da analista:

1. Em `Pendente Compliance`, clicar em `Analisar` e conferir as respostas do
   terceiro, ordenadas pela pergunta e sinalizadas quando classificadas como
   risco alto. O status permanece `Pendente Compliance` durante toda a análise;
   o primeiro registro da analista a grava como responsável.
2. Registrar em `Aguardando esclarecimentos` os pedidos de esclarecimento
   enviados ao terceiro e as respostas recebidas, com anexos. Esse tipo não
   muda o status e, por padrão, fica interno; a analista pode torná-lo visível
   ao solicitante.
3. Para concluir, escolher `Parecer final`: o novo status só aceita as quatro
   decisões. `Aprovado com Ressalvas` também exige prazo de reavaliação.
4. Para encerrar sem parecer, escolher `Cancelamento` (status `Cancelado`),
   disponível também em `Aguardando Terceiro`.
5. A conclusão grava os campos estruturados do Compliance e a vigência, mantém
   o parecer no histórico e volta a tela para somente leitura.

Tipos manuais de desdobramento: `Aguardando esclarecimentos`, `Parecer final`
e `Cancelamento`. Os demais são gravados pelo sistema:
`Criação`, `Atualização do solicitante`, `Solicitação de reenvio ao terceiro`,
`Envio ao terceiro`, `Falha no envio ao terceiro`, `Resposta do terceiro` e
`Vencimento da vigência`.

Se outra pessoa (ou o DD02) mudar o status enquanto a analista registra, o
desdobramento é revertido e a tela pede para reabrir a solicitação.

O histórico interno aparece apenas para o perfil Compliance; os demais usuários
continuam vendo somente `visivel_solicitante = 1`. As permissões das listas
SharePoint ainda precisam aplicar a mesma separação: `Visible` e `DisplayMode`
são proteção de interface, não segurança na fonte.

## Referências oficiais

- Microsoft Forms + Power Automate:
  <https://learn.microsoft.com/en-us/power-automate/forms/overview>
- Conector Microsoft Forms:
  <https://learn.microsoft.com/pt-br/connectors/microsoftforms/>
- Duplicidade de execuções e idempotência:
  <https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/triggers-troubleshoot#flow-or-actions-run-multiple-times>
- Tratamento de erros no Power Automate:
  <https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling>
- Colunas únicas no SharePoint:
  <https://support.microsoft.com/en-us/sharepoint/lists/data-and-lists/create-list-relationships-by-using-lookup-columns#unique-columns>
- Links pré-preenchidos do Forms:
  <https://techcommunity.microsoft.com/blog/microsoftformsblog/pre-fill-responses-in-your-microsoft-forms/4144232>
