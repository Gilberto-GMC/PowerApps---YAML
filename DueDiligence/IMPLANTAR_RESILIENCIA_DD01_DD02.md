# Implantação controlada — Due Diligence DD01/DD02

Preparado em 21/10/2026 a partir dos exports ativos de 20/10. Os arquivos
foram gerados e validados **localmente**; não foram importados no tenant. A
validação final exige uma solicitação de teste no SharePoint e uma resposta
real de teste no Microsoft Forms. Faça primeiro em homologação.

## Arquivos desta entrega

| Artefato | Ação na importação |
| --- | --- |
| `DD01_EnviarQuestionario_RESILIENTE.zip` | **Atualizar** o DD01 existente. |
| `DD02_CapturarResposta_RESILIENTE.zip` | **Atualizar** o DD02 existente: ele passa a capturar, sem calcular risco. |
| `DD02_CapturarResposta_CRIAR_NOVO.zip` | **Criar como novo**, somente se a atualização do DD02 falhar ao remover a concorrência do gatilho Forms. |
| `DD02P_ProcessarInbox_RESILIENTE.zip` | **Criar como novo**: processa uma resposta pendente por minuto. |
| `DD02M_CapturarManual_RESILIENTE.zip` | **Criar como novo**: recebe `Response ID` numérico e põe uma resposta antiga na Inbox. Não tem gatilho automático. |
| `DD06_MonitorarPendencias_RESILIENTE.zip` | **Criar como novo**: verifica Inbox/Envios de hora em hora e falha visivelmente se houver revisão ou atraso. |
| `listgen_tb_dueDiligenceEnvios.json` | Nova lista SharePoint. |
| `listgen_tb_dueDiligenceRespostasInbox.json` | Nova lista SharePoint, com acesso restrito porque guarda a resposta integral. |
| `listgen_tb_dueDiligence_completo.json` | Adicionar `forms_resposta_envio_id` e `forms_destinatario_versao_id` à lista existente. |
| `listgen_tb_dueDiligenceDesdobramentos_completo.json` | Adicionar `forms_envio_id`, `email_envio` e `forms_evento_chave` se ainda não existirem. |
| `ScreenDueDiligence.yaml` | Atualização de três filtros de leitura da resposta aceita. |

**Não importe os pacotes `*_PRONTO.zip` antigos sobre estes fluxos.** O gerador
antigo do repositório não representa a versão ativa exportada em 20/10.

## 1. Preparar e conferir os backups

1. Exporte novamente os fluxos DD01 e DD02 do ambiente de destino em
   **Exportar > Pacote (.zip)**. Guarde os dois arquivos, a data, o ambiente e
   os IDs dos fluxos. Compare a definição com os exports de 20/10 antes de
   escolher Atualizar: se alguém editou os fluxos depois, interrompa a
   implantação e incorpore essa edição ao gerador.
2. Faça cópia do aplicativo e das quatro listas envolvidas
   (`tb_dueDiligence`, `tb_dueDiligenceDesdobramentos`,
   `tb_dueDiligenceTerceiroRespostas`, `tb_dueDiligenceParametros`).
3. Liste os fluxos com gatilho **When a new response is submitted** apontando
   para o Form ID abaixo. No final da implantação deve haver exatamente um
   gatilho Forms ativo para ele. O fluxo manual de recuperação da resposta 96
   deve estar desligado ou excluído.
4. Rode localmente:

   ```bash
   python DueDiligence/build_fluxos_resilientes.py
   python DueDiligence/validar_fluxos_resilientes.py
   ```

   O gerador trava os hashes dos exports usados; se um export for trocado,
   ele interrompe a geração para exigir revisão. O validador verifica ZIPs,
   IDs, dependências de ações, campos e filtros do app.

Form ID esperado:
`itUz0nOZp0OvaWdjYwVIoMoEbKAMYIZFqUAdth6B_EFURVRKSFdaVDE4Q1RIV0VTRkxFSjFZS0VEQS4u`.

## 2. Criar e conferir as colunas do SharePoint

No site `https://grupoccr.sharepoint.com/sites/ComplianceAeroportos`, use os
arquivos `listgen_*.json` acima na ferramenta de provisionamento do projeto ou
crie as colunas manualmente com os **nomes internos** exatos. Não recrie as
listas existentes.

| Lista | Campos que precisam existir antes dos fluxos | Chave |
| --- | --- | --- |
| `tb_dueDiligenceEnvios` | `envio_id` texto, `solicitacao_id` número, `forms_formulario_id` texto, `email_envio` texto, `destinatario_versao_id` texto, `estado_envio` texto, `criado_em` data/hora, `aceito_em` data/hora, `dd01_run_id` texto, `observacao` texto longo | `envio_id` indexado e único. |
| `tb_dueDiligenceRespostasInbox` | `forms_chave` texto, `forms_formulario_id` texto, `forms_resposta_id` texto, `codigo_acompanhamento` texto, `conteudo_json` texto longo simples, `capturado_em` data/hora, `estado` texto, `tentativas` número, `processado_em` data/hora, `ultimo_erro` texto longo | `forms_chave` indexado e único. |
| `tb_dueDiligence` | `forms_resposta_envio_id` texto, opcional e indexado; `forms_destinatario_versao_id` texto, opcional | Campos separados do último convite. |
| `tb_dueDiligenceDesdobramentos` | `forms_envio_id` texto, `email_envio` texto, `forms_evento_chave` texto; todos opcionais | `forms_evento_chave` indexado, sem unicidade obrigatória para não conflitar com registros antigos vazios. |

Confirme na tela de configurações da lista o **nome interno**, não só o nome
exibido. O serviço que executa DD01/DD02 precisa de leitura/gravação nas duas
listas novas. Restrinja `conteudo_json` a quem pode tratar os dados do
questionário; configure retenção e versionamento segundo a política do órgão.

## 3. Migrar convites antigos com evidência

Os convites emitidos antes desta entrega não entram automaticamente na lista
nova. Para que respostas por esses links sejam processadas, migre os códigos
após conferir o destinatário de cada envio.

1. Exporte `tb_dueDiligenceDesdobramentos` em CSV com `ID`,
   `solicitacao_id`, `tipo_desdobramento`, `descricao`, `forms_envio_id` e
   `email_envio` quando disponíveis.
2. Gere a lista de candidatos:

   ```bash
   python DueDiligence/preparar_envios_legados.py \
     --historico historico.csv --candidatos candidatos.csv
   ```

3. Confira cada código com a mensagem enviada ou outro registro confiável.
   Crie `conferidos.csv` com colunas
   `envio_id;solicitacao_id;email_envio`. Não deduza o e-mail pelo cadastro
   atual quando ele pode ter mudado.
4. Gere o CSV de importação:

   ```bash
   python DueDiligence/preparar_envios_legados.py \
     --historico historico.csv --candidatos candidatos.csv \
     --conferidos conferidos.csv --saida envios_legados.csv
   ```

5. Importe apenas as linhas conferidas para `tb_dueDiligenceEnvios` e verifique
   que cada `envio_id` aparece **uma vez** com o Form ID e solicitação corretos.
   A lista única rejeitará colisões. Os códigos sem prova ficam para revisão
   manual, sem associação automática por razão social ou horário.

## 4. Publicar os fluxos, nesta ordem

**Antes deste passo**, publique a alteração do aplicativo descrita na seção 5.
Ela grava uma versão nova do destinatário quando o e-mail muda; sem isso,
um endereço alterado de A para B e depois de volta para A poderia reativar
um link antigo de A. Mantenha a edição direta do e-mail na lista SharePoint
restrita: ela não executa a regra da tela.

1. Importe `DD02P_ProcessarInbox_RESILIENTE.zip` com **Criar como novo**.
   Mapeie a conexão SharePoint da conta de serviço e todas as demais conexões
   que o importador solicitar (o pacote base ainda declara Forms, sem usá-lo
   nas ações DD02P). Mantenha-o **desligado**
   até concluir as listas e a migração de convites.
2. Importe `DD02M_CapturarManual_RESILIENTE.zip` com **Criar como novo**.
   Mapeie Microsoft Forms e SharePoint. Ele só roda por botão.
   Importe `DD06_MonitorarPendencias_RESILIENTE.zip` com **Criar como novo**,
   mapeie as conexões solicitadas (o pacote base ainda declara Outlook, mas
   DD06 não envia mensagens) e confira que os proprietários recebem alertas de falha
   do fluxo. Ligue-o após a migração dos convites.
3. Importe `DD01_EnviarQuestionario_RESILIENTE.zip` com **Atualizar**,
   selecionando especificamente o DD01 existente. Mapeie SharePoint e Outlook.
   Confirme no editor: `HTTP_Registrar_Envio_Preparado` vem **antes** de
   `Enviar_Email_V2`; o e-mail usa o mesmo Form ID. Não use Criar como novo
   nesta etapa, pois isso deixaria dois envios automáticos para a mesma intenção.
4. Ligue DD02P. Sua Inbox ainda deve estar vazia ou conter somente registros
   de teste revisados.
5. Importe `DD02_CapturarResposta_RESILIENTE.zip` com **Atualizar** o DD02
   original. Confirme que o gatilho Forms aponta ao Form ID esperado, que
   `Obter detalhes da resposta` usa o mesmo ID e que o gatilho **não** tem
   `runtimeConfiguration.concurrency`. Esse pacote já remove esse atributo.
   A Microsoft documenta um erro do conector ao desligar a concorrência pelo
   designer; nesse caso, use o fallback do passo seguinte.
6. **Somente se o Update do DD02 falhar:** importe
   `DD02_CapturarResposta_CRIAR_NOVO.zip` com **Criar como novo**. Desligue o
   DD02 antigo e ligue o novo capturador de modo coordenado. Registre o
   intervalo da troca e confronte o Forms com a Inbox; qualquer Response ID
   submetido nesse intervalo pode ser capturado pelo DD02M. Nunca mantenha os
   dois gatilhos Forms ativos após a troca.

Se o novo designer apresentar erro de carregamento, abra o **designer
clássico** e inspecione as mesmas ações e conexões. O pacote Update deve
preservar o ID do fluxo; confirme isso na página de detalhes após importar.

## 5. Aplicativo e teste de ponta a ponta

Atualize o aplicativo com `ScreenDueDiligence.yaml` **depois de criar as
colunas da seção 2 e antes de atualizar o DD01/DD02**. A tela troca três
filtros de resposta para `forms_resposta_id = forms_ultima_resposta_id` e
acrescenta um DataCard oculto para `forms_destinatario_versao_id`. Ao criar a
solicitação ou alterar o e-mail do terceiro, grava um GUID novo nessa coluna;
um reenvio ao mesmo e-mail preserva o GUID. No Source Code YAML, o separador
de fórmulas é o formato invariante do arquivo. Verifique no Studio que a
tela compila e que o cartão oculto está conectado à coluna de nome interno
exato; então publique. O filtro novo também funciona com respostas do DD02
antigo, pois ele grava `forms_ultima_resposta_id`.

Use uma solicitação de teste em `FLUXO III`, `Aguardando Terceiro`, destinada
a um endereço de teste. Confira na sequência:

1. DD01 cria **um** item `envio_id` na lista Envios, envia o e-mail, marca
   `estado_envio = Aceito`, atualiza `forms_envio_processado_id` e grava o
   desdobramento com `forms_envio_id`, `email_envio` e `forms_evento_chave`.
2. Responda o Forms pelo link. DD02 captura **uma** linha na Inbox com
   `forms_chave = Form ID|Response ID`, `estado = Pendente` e `conteudo_json`
   não vazio.
3. DD02P muda a Inbox para `Processado`, cria 10 ou 11 respostas filhas,
   registra `forms_ultima_resposta_id` e `forms_resposta_envio_id` no pai,
   altera o status conforme o risco e grava `Resposta do terceiro` no
   histórico. Confirme que a ação `HTTP_Reler_Solicitacao` devolve
   `d.__metadata.etag`; sem ele, o DD02P deve falhar e **não** sobrescrever o
   item. Corrija o formato REST antes de prosseguir.
4. Confira a resposta na tela e no laudo. Ela deve continuar visível mesmo
   quando `forms_resposta_envio_id` for diferente do último
   `forms_envio_id`.
5. Em outro item de teste, envie duas vezes ao mesmo e-mail e responda pelo
   **primeiro** link. O pai deve preservar `forms_envio_id` do último convite e
   gravar o primeiro código em `forms_resposta_envio_id`.
6. Execute DD02M para um Response ID já capturado: não deve aparecer segunda
   linha da Inbox nem duplicar perguntas. Para um Response ID antigo ainda
   não capturado, ele deve criar a linha para DD02P processar.
7. Teste uma mudança de destinatário em homologação: uma resposta por convite
   do e-mail antigo deve permanecer na Inbox para revisão, sem alterar o pai.
   Após cinco tentativas, a linha fica em `Revisao`.
8. Teste a sequência de e-mail A → B → A. Cada troca deve gerar um
   `forms_destinatario_versao_id` diferente. Responder pelo **primeiro** link
   de A deve continuar em revisão, mesmo após o cadastro voltar para A.

O campo `capturado_em` registra quando o fluxo obteve a resposta. O conector
Forms não fornece aqui uma data de submissão comprovada; não apresente
`capturado_em` como hora original do envio pelo terceiro. Para respostas
históricas, preserve o horário do export do Forms separadamente.

## 6. Operação diária e recuperação

Exporte periodicamente os IDs do Forms, a solicitação, desdobramentos,
respostas filhas, Envios e Inbox. Rode:

```bash
python DueDiligence/auditar_respostas_pendentes.py \
  --solicitacoes solicitacoes.csv --historico historico.csv \
  --forms forms.csv --internas respostas_internas.csv \
  --envios envios.csv --inbox inbox.csv --saida auditoria.csv
```

Não inclua `conteudo_json` no CSV usado na auditoria. Investigue toda linha
`SEM_CAPTURA_INBOX`, `CAPTURADA_PENDENTE`, `EM_REVISAO`,
`INBOX_PROCESSADA_SEM_PAI`, `ENVIO_SEM_ACEITE` ou código ambíguo. Uma
resposta sem captura pode ser inserida pelo DD02M após confirmar Form ID e
Response ID. Para reprocessar uma linha `Revisao`, corrija a causa, zere
`tentativas` e mude `estado` para `Pendente`; guarde a justificativa da revisão.
Não rode novamente o DD01 para um envio de resultado incerto sem verificar
antes o item em Envios e a execução de e-mail.

DD06 executa a cada hora: falha quando há Inbox em `Revisao`, Inbox em
`Pendente` há mais de 15 minutos, convite `Preparado` há mais de 15 minutos
ou solicitação `Aguardando Terceiro` sem envio confirmado há mais de 15
minutos. Essa última verificação mostra também uma intenção cujo gatilho DD01
não iniciou.
Confira que o proprietário está inscrito nas notificações de falha e que a
execução mostra a lista afetada; a falha intencional só desaparece depois que
a pendência for tratada. Esse monitor não substitui o confronto periódico com
o export do Forms: o conector não lista todas as respostas para uma auditoria
retroativa automática neste desenho.

## Retorno ao estado anterior

Se a homologação ou o teste de produção falhar, desligue DD02P e o capturador
novo, guarde o conteúdo da Inbox e restaure os dois ZIPs exportados no passo 1
com **Atualizar** os fluxos originais. Ligue novamente somente o DD02
original. Confronte Forms e Inbox durante o intervalo da troca; recapture
manualmente os Response IDs ausentes. O filtro novo do aplicativo também lê
respostas processadas pelo DD02 anterior, pois ele grava
`forms_ultima_resposta_id`; pode permanecer publicado.

## Limites da verificação local

O validador confere JSON, ZIP, nomes de ações, dependências, parênteses das
expressões, chaves e filtros. Ele não consegue provar que o tenant aceitará a
importação, que as conexões têm permissão, que o Forms emitirá um webhook ou
que SharePoint retornará o mesmo formato de ETag. A prova final são os testes
de homologação e o cruzamento Forms × Inbox após a publicação.

O validador geral `validar_due_diligence.py` já falha em artefatos anteriores
à implantação (66 achados no `HEAD` do repositório); com esta alteração,
continua vermelho com 65 achados em áreas legadas. O validador específico
`validar_fluxos_resilientes.py` passa. Por isso, além da checagem específica,
abra e compile a tela no Power Apps Studio em homologação antes de publicar.

Referências: [conector Forms e concorrência](https://learn.microsoft.com/en-us/connectors/microsoftforms/),
[limite de execuções aguardando](https://learn.microsoft.com/en-us/power-automate/limits-and-config),
[ETag no SharePoint REST](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/complete-basic-operations-using-sharepoint-rest-endpoints).
