# Due Diligence — Fase 2

## Contrato aprovado

- A fonte funcional é a planilha `Canal Confidencial.url` (arquivo XLSX com extensão incorreta).
- O questionário v2 do terceiro é categórico; `pontuacao_terceiro` não participa da regra v2.
- Sete perguntas podem produzir `Risco Alto`.
- Sem obrigação legal, qualquer gatilho do solicitante ou do terceiro resulta em risco `Alto`.
- A obrigação legal mantém a precedência da Fase 1 e encerra no Fluxo I.
- Toda resposta válida de uma solicitação do Fluxo III segue para `Pendente Compliance`, mesmo quando `terceiro_gatilho_risco = "Não"`.
- As decisões novas são `Aprovação`, `Aprovação condicionada` e `Reprovação`.

## Valores que ainda precisam ser configurados

| Configuração | Valor |
|---|---|
| Site SharePoint | `https://grupoccr.sharepoint.com/sites/ComplianceAeroportos` |
| Form ID do Microsoft Forms | `itUz0nOZp0OvaWdjYwVIoMoEbKAMYIZFqUAdth6B_EFURVRKSFdaVDE4Q1RIV0VTRkxFSjFZS0VEQS4u` |
| Pergunta de correlação | `Código de acompanhamento` (`rf6e81f83fe194d4c80dbfd30fc7b8301`) |
| URL do Código de Ética aprovada pelo Compliance | `PREENCHER_URL_CODIGO_ETICA` |
| URL do Canal Confidencial da ASUR Brasil | `PREENCHER_URL_CANAL_CONFIDENCIAL` |
| Fonte/grupo que autoriza o perfil Compliance | `PREENCHER_FONTE_PERFIL_COMPLIANCE` |

## Pacotes dos fluxos

- `ProcessarrespostaDueDiligence_PRONTO.zip`: DD02, importar primeiro e mapear
  as conexões Microsoft Forms e SharePoint.
- `EnviarquestionarioDueDiligence_PRONTO.zip`: DD01, importar depois e mapear
  as conexões SharePoint e Office 365 Outlook.

Na importação legada, selecionar **Atualizar** e apontar para os dois fluxos
rascunho existentes. Não criar cópias, pois isso deixaria gatilhos duplicados.
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
ou que não pertença a uma solicitação em `Aguardando terceiro` no `FLUXO III`.

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
  equals(triggerBody()?['status'], 'Aguardando envio ao terceiro'),
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
   - status = `Aguardando envio ao terceiro`;
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
   - `data_envio_terceiro = utcNow()`;
   - `status = Aguardando terceiro`.
6. Criar desdobramento `Envio ao terceiro`, incluindo o identificador da
   intenção de envio na descrição.

Use retry `None` no envio de e-mail. Um timeout depois de o Outlook aceitar a
mensagem não fornece um identificador que permita provar se o e-mail saiu; um
retry automático pode duplicá-lo. O reenvio deve ser uma nova intenção criada
pelo botão do app.

### Erro

Dentro de um Scope `Catch`, configurado com `run after` para falha/timeout:

- atualizar o status para `Erro no envio ao terceiro` somente se o
  `forms_envio_id` ainda for o mesmo;
- registrar um desdobramento com o run id e a ação que falhou;
- finalizar com `Terminate = Failed`.

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
   fluxo não for `FLUXO III`, se o status não for `Aguardando terceiro` ou se
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
| `Aprovado com ressalvas` | `Aprovado com ressalvas` |
| `Reprovado parcialmente` | `Reprovado parcialmente` |
| `Reprovado` | `Reprovado` |

A decisão e a justificativa são obrigatórias. Na aprovação com ressalvas,
condicionantes e prazo de reavaliação também são obrigatórios.

A fonte real que identifica os usuários do Compliance ainda não foi informada
para este app. Até essa definição, `varDdPodeAnalisarCompliance` permanece
como `false`: a ação `Analisar` fica desabilitada para todos, evitando conceder
acesso por engano. Depois de conectar a fonte indicada no item
`PREENCHER_FONTE_PERFIL_COMPLIANCE`, a ação será liberada apenas para os
usuários autorizados. O formulário principal continua somente leitura durante
todo o ciclo interno.

Fluxo da analista:

1. Em `Pendente Compliance`, clicar em `Analisar`.
2. Conferir as respostas do terceiro, ordenadas pela pergunta e sinalizadas
   quando classificadas como risco alto.
3. Registrar `Início da análise` e mudar para `Em análise Compliance`.
4. Registrar dúvidas, respostas, anexos e encaminhamentos como
   desdobramentos. O padrão é nota interna; a analista pode marcar o item como
   visível ao solicitante.
5. Para concluir, escolher `Parecer final`, informar uma decisão conclusiva e
   escrever a justificativa. `Aprovado com ressalvas` também exige prazo de
   reavaliação.
6. A conclusão grava os campos estruturados do Compliance, mantém o parecer no
   histórico e volta a tela para somente leitura.

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
