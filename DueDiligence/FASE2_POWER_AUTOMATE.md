# Due Diligence — Fase 2

> **Fluxos DD01/DD02 em produção:** os pacotes `*_PRONTO.zip` e o gerador
> `build_power_automate_flows.py` abaixo são a versão anterior à arquitetura
> de captura durável. Para novas implantações, use
> [IMPLANTAR_RESILIENCIA_DD01_DD02.md](IMPLANTAR_RESILIENCIA_DD01_DD02.md)
> e os pacotes `*_RESILIENTE.zip` gerados a partir dos exports ativos de 20/10.
> Não use `Update` com um pacote antigo sobre os fluxos publicados.

## Contrato aprovado

- A fonte funcional é a planilha `Canal Confidencial.url` (arquivo XLSX com extensão incorreta).
- O questionário v2 do terceiro é categórico; `pontuacao_terceiro` não participa da regra v2.
- Sete perguntas podem produzir `Risco Alto`.
- Qualquer gatilho crítico do solicitante (subcontratação, procuração, pagamento em nome da Companhia, representação perante órgão público ou indicação por funcionário público) ou do terceiro resulta em risco `Alto` e `FLUXO III`, mesmo havendo obrigação legal: o gatilho tem peso maior que a obrigação legal.
- Só o **risco baixo automático** dispensa o questionário ao terceiro (2026-09-15): obrigação legal sem gatilho crítico, contraparte classificada como `SEM RISCO` ou, desde 2026-09-17, tipo de contrato classificado como "Risco Baixo automático" na aba Config da planilha — Órgão público — Convênio, Órgão público — Termo de cooperação, Órgão público — Cessão de área e Cliente — Fornecimento de treinamento. O tipo de contrato só vale com a categoria do prefixo (o combo de tipo de contrato não é filtrado pela categoria) e perde para o gatilho crítico; vence a categoria, então órgão público com cessão de área é aprovado na hora, sem Forms. Os tipos marcados como "Risco Alto automático" na mesma coluna continuam sem efeito no cálculo.
- Órgão público (2026-09-18): dos cinco tipos de contrato "Órgão público — …", só **Doação** e **Patrocínio** recebem o Forms (risco `Alto`). **Convênio**, **Termo de cooperação** e **Cessão de área** nunca recebem: sem gatilho crítico são risco baixo automático; com gatilho crítico o app grava `FLUXO III` já em `Pendente Compliance`, sem abrir intenção de envio (`forms_envio_id` fica vazio) — o DD01 não envia e o DD05 avisa o Compliance. O solicitante não edita depois de salvar, como em qualquer solicitação que já chegou ao Compliance. O resumo e o laudo mostram o questionário como "Não se aplica".
- Todo o resto recebe o Forms (`FLUXO III`): contraparte `ALTO`, órgão público (antigo Fluxo II, agora com risco `Alto (órgão público)`) e `PONTUAR` em qualquer faixa de pontos. A faixa continua definindo o risco e a vigência.
- O Compliance pode reclassificar o risco (Baixo, Médio ou Alto) a seu critério ao registrar a análise, depois da resposta do terceiro (`Pendente Compliance`). Antes dela a opção não aparece, porque o solicitante ainda pode editar e o recálculo sobrescreveria a escolha. A vigência passa a seguir a classificação escolhida e a mudança fica no histórico interno (`Reclassificação de risco`).
- Resposta válida do terceiro (2026-09-16): se o risco calculado é `Baixo` ou `Médio`, não há gatilho crítico do solicitante e nenhuma resposta do terceiro é `Risco Alto`, o DD02 aprova automaticamente (`Aprovado`, com `data_conclusao` e vigência de 3 ou 2 anos). Qualquer outro caso segue para `Pendente Compliance`.
- As decisões do parecer final são `Aprovado`, `Aprovado com Ressalvas`,
  `Reprovado Parcialmente` e `Reprovado` (grafia exata; ver o modelo abaixo).
- Avisos por e-mail (2026-09-17): quem abriu a solicitação recebe e-mail a cada mudança de status, inclusive no registro; os analistas ativos da `tb_dueDiligenceCompliance` recebem quando a solicitação chega a `Pendente Compliance`. Fluxo DD05.

## Modelo de status (2026-09-10)

O Compliance reduziu o ciclo a oito status. A grafia é contrato: o app compara
texto com `=`, que diferencia maiúsculas de minúsculas.

| Status | Quem define | Quando |
|---|---|---|
| `Aguardando Terceiro` | App | Solicitação criada no Fluxo III; o questionário segue para o terceiro. |
| `Pendente Compliance` | DD02 ou App | DD02: resposta válida do terceiro com risco alto (risco calculado `Alto`, gatilho crítico ou alguma resposta `Risco Alto`). App: órgão público com gatilho crítico em convênio, termo de cooperação ou cessão de área, que vai direto ao Compliance sem questionário. Permanece durante toda a análise. |
| `Aprovado` | App, DD02 ou Compliance | App: automático no Fluxo I (e no v1 com encerramento por risco baixo). DD02: resposta do terceiro sem risco alto em solicitação de risco baixo ou médio. Compliance: parecer final. |
| `Aprovado com Ressalvas` | Compliance | Parecer final; exige condicionantes e prazo de reavaliação. |
| `Reprovado Parcialmente` | Compliance | Parecer final. |
| `Reprovado` | Compliance | Parecer final. |
| `Cancelado` | Compliance | A partir de `Aguardando Terceiro` ou `Pendente Compliance`. |

As quatro decisões do parecer final também podem ser registradas a partir de
`Aguardando Terceiro`, quando o terceiro não responde.
| `Vencido` | DD03 | Fim da vigência: 1 ano (risco alto), 2 (médio) e 3 (baixo). |

Desde 2026-09-15 o app não gera mais `FLUXO II`: órgão público recebe o Forms
como qualquer caso fora do risco baixo automático. Registros antigos com
`fluxo_classificacao = "FLUXO II"` continuam aprovados e vencem em 1 ano (risco
`Alto`). No resumo da solicitação, a aprovação automática aparece como
"Aprovação automática (FLUXO I)", sem status próprio.

### Edição até a resposta do terceiro

Enquanto a solicitação está em `Aguardando Terceiro` e sem
`data_resposta_terceiro`, qualquer usuário pode editá-la pela ação **Editar**.
**Analisar** é outra ação, visível só ao Compliance: abre a solicitação somente
leitura com o painel de desdobramentos. Com um item só, o rótulo virava
"Analisar" para o Compliance e o Editar sumia. Ao salvar uma edição:

- o motor recalcula fluxo e risco; se virar risco baixo automático, a
  solicitação é aprovada na hora e uma resposta tardia do terceiro é rejeitada
  pelo DD02 (status diferente de `Aguardando Terceiro`);
- se o e-mail do terceiro mudou (ou o envio anterior falhou), o app gera um novo
  `forms_envio_id`, limpa `data_envio_terceiro` e o DD01 reenvia o questionário
  ao endereço novo;
- antes de gravar, o app relê o registro. Se o status mudou, se o terceiro
  respondeu ou se houve reenvio do Forms enquanto a tela estava aberta, o
  salvamento é recusado e o usuário precisa reabrir a solicitação;
- a data de envio gravada pelo DD01 nesse intervalo é preservada: o formulário
  usa o valor relido, não o da abertura da tela.

Depois da resposta, o formulário fica somente leitura para todos.

O botão Salvar confere todos os campos do questionário v2 antes de gravar e
lista na notificação os que faltam (inclusive tipo de fornecedor/cliente e tipo
de obrigação legal quando aplicáveis, valor numérico e e-mail válido). Cada
campo obrigatório tem `*` no rótulo (pelo `Required` do card). Depois de uma
tentativa de salvar com pendência, o rótulo de erro do próprio card mostra
"Campo obrigatório" (ou "Informe um e-mail válido" / "Informe um valor numérico
válido") e a borda do campo fica vermelha até ele ser preenchido. A variável
`varDdMostrarObrigatorios` liga esse destaque e é desligada ao abrir, criar,
cancelar ou salvar.

### Auditoria do resumo e da aprovação automática (2026-09-16)

**Travamento corrigido.** Se a classificação da contraparte não fosse
identificada, o motor devolvia fluxo `""`. O app gravava `Aguardando Terceiro`, o
DD01 enviava o Forms (confere só status e IDs) e o DD02 **recusava** a resposta,
porque exige `fluxo_classificacao = FLUXO III`. A solicitação ficava parada para
sempre. Isso acontecia sempre que alguém editava o texto de uma categoria ou a
classificação de um tipo em `tb_dueDiligenceParametros`. Agora:

- a categoria é comparada pelo `codigo_opcao` (`categoria_contraparte_01` a
  `_04`), e não pelo texto exibido;
- a classificação do tipo passa por `Upper(Trim(...))`;
- sem classificação, o fluxo é `FLUXO III` (vai para análise), nunca vazio.

Registros gravados antes com fluxo vazio mostram no resumo "Atenção: fluxo não
identificado". Para destravar, use Editar e salve (recalcula o fluxo) e depois
Reenviar Forms. Para localizá-los na grade do SharePoint, filtre `status` =
`Aguardando Terceiro` e confira `fluxo_classificacao` diferente de `FLUXO III`.

**O que o resumo mostra.**

| Situação | Respostas do terceiro | Gatilho · Terceiro | Situação da análise |
|---|---|---|---|
| Nova, sem categoria | — | — | Preencha a solicitação |
| Nova, risco baixo automático | NÃO SE APLICA | NÃO SE APLICA | Será aprovada automaticamente ao salvar |
| Nova, demais casos | A ENVIAR | A ENVIAR | Ao salvar, segue para o questionário do terceiro |
| Aprovada ou vencida automaticamente (Fluxo I/II) | NÃO SE APLICA | NÃO SE APLICA | Aprovação automática (FLUXO I) |
| Aguardando Terceiro | AGUARDANDO + situação do envio | AGUARDANDO | Aguardando a resposta do terceiro |
| Encerrada sem resposta (ex.: cancelada) | SEM RESPOSTA | SEM RESPOSTA | Responsável pelo encerramento |
| Com resposta | nº de respostas e de risco alto | SIM/NÃO | Responsável ou aguardando atribuição |
| Aprovada automaticamente após a resposta (risco baixo/médio, sem risco alto) | nº de respostas | NÃO | Aprovação automática após a resposta do terceiro |

Em Ver/Analisar, gatilho e classificação vêm do que está **gravado**
(`gatilho_dd`, `classificacao_contraparte`). O recálculo pela tela vale só em
Nova/Editar. Registros antigos perderam duas respostas de gatilho (nome interno
com mais de 32 caracteres), e o recálculo mostraria "NÃO" onde o gravado é "Sim".

No laudo, a aprovação automática aparece como "Aprovado automaticamente", com
justificativa "Aprovação automática (FLUXO I), sem análise do Compliance",
respostas "Não se aplica" e a data de conclusão como data da decisão.

### CNPJ/CPF mascarado (2026-09-17)

- O campo `tipo_pessoa` (antes só do questionário v1) voltou, obrigatório e
  logo antes do documento: linha 1 da grade com **Tipo de pessoa** à esquerda e o
  documento à direita; Aeroporto e Razão social dividem a linha 0. Opções:
  `Pessoa Jurídica`, `Pessoa Física` e `Estrangeiro`.
- O usuário digita só os números; ao sair do campo a máscara segue o tipo:
  Pessoa Física formata com 11 dígitos (`000.000.000-00`) e Pessoa Jurídica com
  14 (`00.000.000/0000-00`). Com a quantidade errada ficam só os dígitos e o
  Salvar recusa ("Informe os 11 dígitos do CPF" / "os 14 dígitos do CNPJ").
  Estrangeiro não tem máscara nem conferência de tamanho. O rótulo e o texto de
  ajuda do campo mudam com o tipo, e trocar o tipo refaz a máscara.
- Registros antigos sem tipo de pessoa continuam formatados pela contagem de
  dígitos; ao editar, o tipo passa a ser exigido.
- A lista guarda o texto mascarado, que é o que aparece na tela, no laudo e nos
  e-mails. Por isso a busca de Registros mudou: número com até 6 dígitos
  continua sendo busca por ID e, acima disso, o texto digitado é convertido nas
  duas máscaras (CPF e CNPJ) e procurado no documento. Assim a busca funciona
  com ou sem pontuação, e continua delegável (`StartsWith`).
- Registros antigos gravados sem máscara passam a aparecer formatados quando
  forem editados e salvos.

### Valor do contrato e "Minhas solicitações" (2026-09-16)

- **Valor total do contrato:** o usuário digita só os números; ao sair do campo
  (`TriggerOutput` = `FocusOut`), o texto é reformatado para `250.000,00`. A
  formatação é montada com os formatos `"0"`/`"00"`, que não dependem do idioma,
  e toda leitura usa `Value(..., "pt-BR")`. Sem isso, um navegador em inglês
  leria o ponto de milhar como decimal. `varDdValorEditado` volta a `false` ao
  abrir, criar, cancelar ou salvar, e aí o campo mostra o valor do registro.
- **Minhas solicitações:** chave na barra de filtros de Registros. Filtra por
  `'Criado por'.Email = User().Email`, que é delegável no SharePoint. Seguindo a
  lição de delegação, a condição entra como ramificação da consulta (12 `Filter`
  completos), nunca como `IsBlank(...) ||` dentro do `Filter`. O botão de limpar
  filtros desliga a chave.

### Colunas com nome interno cortado (2026-09-16)

O SharePoint guarda no máximo 32 caracteres de nome interno e corta o
excedente sem avisar. Duas colunas da `tb_dueDiligence` passavam do limite:

| Nome de exibição (usado nas fórmulas) | Nome interno gravado (usado no `DataField`) |
|---|---|
| `gatilho_representacao_orgao_publico` | `gatilho_representacao_orgao_publ` |
| `gatilho_indicado_funcionario_publico` | `gatilho_indicado_funcionario_pub` |

Como o formulário grava pelo `DataField`, essas duas respostas **nunca foram
salvas** até esta correção: nas solicitações antigas elas estão vazias, embora
o gatilho consolidado (`gatilho_dd`) e o risco tenham sido calculados com os
valores da tela. Para conferir o nome interno: Configurações da lista → clicar
na coluna → o endereço termina em `Field=<nome interno>`. O JSON da lista não
muda: numa instalação nova o SharePoint repete o mesmo corte.

### Bloco do aeroporto

A coluna `bloco` (Texto, 20, indexada) é preenchida pelo app a partir do
aeroporto: `CENTRAL` (Goiânia, TECA GYN, Imperatriz, Palmas, Pampulha,
Petrolina, São Luís, Teresina) ou `SUL` (Bacacheri, Bagé, Curitiba, Foz do
Iguaçu, Joinville, Londrina, Navegantes, Pelotas, Uruguaiana). A opção `SEDE`
(sede corporativa) fica sem bloco. Serve para filtros futuros do painel.

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
`data_envio_terceiro`. Até a resposta do terceiro, o solicitante pode editar a
solicitação (por exemplo, para corrigir o e-mail); ao salvar com e-mail novo ou
depois de uma falha no envio, um novo envio é solicitado automaticamente.

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
- `NotificarstatusDueDiligence_PRONTO.zip`: DD05, importar como **Criar como
  novo** e mapear as conexões SharePoint e Office 365 Outlook, depois de criar
  a coluna `status_notificado` (ver "Fluxo DD05").

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
12. Criar `bloco` na `tb_dueDiligence` conforme o JSON completo (`Text`,
   `MaxLength='20'`, indexada) **antes** de colar a tela; sem ela a tela não
   compila. Registros existentes podem ter o bloco preenchido pela visão em
   grade, com o mapeamento da seção "Bloco do aeroporto".
13. Criar `status_notificado` na `tb_dueDiligence` conforme o JSON completo
   (`Text`, `MaxLength='60'`, opcional) **antes** de ativar o DD05 e copiar
   `status` para ela em todos os registros existentes (visão em grade). O app
   não usa essa coluna; não acrescente cartão para ela no formulário.

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
O e-mail do DD01 também mostra o código esperado; o terceiro deve conferir o
campo no formulário e preenchê-lo se estiver vazio ou diferente. Quando houver
reenvio, o e-mail avisa para usar somente o convite mais recente, pois o DD02
recusa códigos dos links anteriores.

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
4. Enviar o e-mail em HTML ao `email_terceiro`, com o código atual visível para
   conferência no Forms.
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
   - `status`: `Aprovado` quando `Avaliar_Aprovacao_Automatica` é verdadeiro
     (não `varTerceiroAlto`, `gatilho_dd` diferente de "Sim" e
     `classificacao_risco` baixo ou médio); senão `Pendente Compliance`;
   - na aprovação automática, também `data_conclusao = utcNow()` e
     `data_vencimento` = hoje + 3 anos (baixo) ou 2 (médio), gravada ao meio-dia UTC.
4. Não preencher `pontuacao_terceiro` no v2.
5. Criar desdobramento `Resposta do terceiro` (status novo igual ao gravado) com o total de respostas e a
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

## Fluxo DD05 — notificar mudança de status

Gatilho: "Quando um item é criado ou modificado" na `tb_dueDiligence` (a mesma
lista do DD01), concorrência 1, com a condição `status` preenchido e diferente
de `status_notificado`. A coluna guarda o último status avisado, no mesmo molde
de `forms_envio_processado_id` do DD01: o aviso sai venha a mudança de onde
vier (app, DD02, DD03, parecer do Compliance ou visão em grade), e a gravação do
próprio marcador não reativa o fluxo, porque os dois campos ficam iguais. Não
depende do histórico: se o registro do desdobramento falhar, o aviso sai mesmo
assim.

1. Relê o item com `Author` ("Criado por") e confere de novo
   `status ≠ status_notificado`: com a fila do gatilho, uma execução anterior
   pode já ter avisado o mesmo status.
2. Solicitante (autor do item): um e-mail a cada mudança, inclusive no registro
   da solicitação, com o status anterior, o novo status e uma orientação por
   status (vigência, condicionantes e prazo de reavaliação quando houver). O
   e-mail não leva risco, pontuação nem gatilhos, que no app são exclusivos do
   Compliance.
3. Compliance: quando o novo status é `Pendente Compliance`, um e-mail para
   todos os `email` com `ativo = 1` da `tb_dueDiligenceCompliance`, com
   terceiro, solicitante, classificação de risco, risco final, pontuação,
   gatilho do solicitante e resposta de risco alto do terceiro.
4. `status_notificado` recebe o status relido só se nenhum envio falhou. Com
   falha, a execução termina como `DD05_ENVIO_FALHOU` e pode ser reenviada; a
   próxima alteração do item também tenta de novo.
5. Sem analista ativo, o solicitante é avisado, o marcador é gravado e a
   execução termina como `DD05_SEM_COMPLIANCE_ATIVO`, para aparecer no
   histórico de execuções.
6. Item excluído antes da releitura encerra sem falha. Qualquer outro erro de
   leitura (por exemplo, a coluna `status_notificado` ainda não criada) termina
   como `DD05_LEITURA_FALHOU`, sem enviar nada.

Não geram aviso, porque não mudam o status: `Aguardando esclarecimentos`,
reclassificação de risco, envio e falha de envio do questionário e reenvio do
Forms. Os e-mails saem pela conexão Office 365 Outlook mapeada na importação e
chegam alguns minutos depois da mudança, conforme o intervalo do gatilho.

Implantação, nesta ordem:

1. Criar `status_notificado` (passo 13 da migração das listas).
2. Copiar `status` para `status_notificado` nos registros existentes. Sem essa
   cópia, cada solicitação antiga dispara um único aviso com o status atual na
   próxima vez que for alterada.
3. Importar `NotificarstatusDueDiligence_PRONTO.zip` como **Criar como novo**,
   mapear SharePoint e Office 365 Outlook, salvar e ativar.
4. Testar: criar uma solicitação (aviso "foi registrada" ao solicitante),
   responder o Forms com uma resposta de risco alto (avisos ao Compliance e ao
   solicitante) e registrar o parecer final (aviso ao solicitante).

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
internas, o resumo da avaliação, a reclassificação de risco, as colunas de
pontuação e risco da lista de registros e o painel de indicadores.

A ação `Excluir` (2026-09-21) apaga a solicitação e todo o histórico dela, e é
do Compliance ou de quem abriu a solicitação. A tela confere isso em três
camadas — item desabilitado na barra de ações, ramo `excluir` do `OnSelect` e
botão de confirmação —, sempre por `'Criado por'.Email`, nunca pelo nome. O formulário
principal é editável até a resposta do terceiro e somente leitura depois dela.

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
   decisões. `Aprovado com Ressalvas` também exige prazo de reavaliação. Se
   necessário, ajustar a `Classificação de risco` antes de registrar: ela vale
   em `Pendente Compliance` e junto com o `Parecer final`, e define a vigência.
   Desde 2026-09-17 o `Parecer final` também vale em `Aguardando Terceiro`,
   para o terceiro que não responde (por exemplo, órgão público). O laudo
   registra o questionário como "Sem resposta".
4. Para encerrar sem parecer, escolher `Cancelamento` (status `Cancelado`),
   disponível também em `Aguardando Terceiro`.
5. A conclusão grava os campos estruturados do Compliance e a vigência, mantém
   o parecer no histórico e volta a tela para somente leitura.

Tipos manuais de desdobramento: `Aguardando esclarecimentos`, `Parecer final`
e `Cancelamento`. Os demais são gravados pelo sistema:
`Criação`, `Atualização do solicitante`, `Solicitação de reenvio ao terceiro`,
`Envio ao terceiro`, `Falha no envio ao terceiro`, `Resposta do terceiro`,
`Reclassificação de risco` (interno) e `Vencimento da vigência`.

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
