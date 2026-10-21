# Reconciliação de respostas pendentes

Para a arquitetura com Inbox e registro de convites, consulte também
`IMPLANTAR_RESILIENCIA_DD01_DD02.md`. O script abaixo agora aceita
`--envios envios.csv --inbox inbox.csv` e acrescenta ao relatório os estados
`SEM_CAPTURA_INBOX`, `CAPTURADA_PENDENTE`, `EM_REVISAO`,
`INBOX_PROCESSADA_SEM_PAI` e `ENVIO_SEM_ACEITE`.

Este procedimento preserva o Microsoft Forms, DD01 e DD02. A exportação e a auditoria são somente leitura. Nenhum status deve ser alterado apenas porque há um histórico de "Envio ao terceiro": esse evento confirma o envio do e-mail, não o recebimento ou a validação da resposta.

## Caso 36

- Status informado: `Aguardando Terceiro`; fluxo: `FLUXO III`.
- Código do último envio, também em `forms_envio_processado_id`: `71aad33a-62b4-47be-aa0e-03079d473071`.
- Há quatro códigos de envio anteriores no histórico. O DD02 ativo procura esses códigos na coluna estruturada `forms_envio_id` do histórico; os registros antigos do caso 36 não a tinham preenchida.
- A resposta 96 foi localizada no Forms com o código de um envio anterior. O DD02 falhou na correlação e a recuperação manual v3 foi confirmada pelo usuário. Consulte `INCIDENTE_36_RESPOSTA_TERCEIRO.md`.

## Exportar e cruzar todos os casos

Exportar como CSV, com cabeçalhos:

1. `tb_dueDiligence`: todos os itens, ao menos `ID`, `status`, `fluxo_classificacao`, `forms_envio_id`, `forms_envio_processado_id`, `forms_ultima_resposta_id`, `data_resposta_terceiro`.
2. `tb_dueDiligenceDesdobramentos`: todos os itens, ao menos `solicitacao_id`, `tipo_desdobramento`, `descricao`.
3. Microsoft Forms: todas as respostas do formulário correspondente, incluindo `ID` (Response Id) e `Código de acompanhamento`.
4. `tb_dueDiligenceTerceiroRespostas`: opcional para a primeira triagem, necessário antes de qualquer reparo. Incluir `solicitacao_id`, `forms_resposta_id`, `forms_envio_id`, `codigo_pergunta`, `resposta`, `forms_item_chave`.

Executar:

```bash
python DueDiligence/auditar_respostas_pendentes.py \
  --solicitacoes solicitacoes.csv \
  --historico historico.csv \
  --forms forms.csv \
  --internas respostas_internas.csv \
  --saida auditoria.csv
```

Se o export do Forms der outro nome às colunas, usar `--coluna-codigo` e `--coluna-resposta-id`. O relatório não inclui nome, e-mail nem respostas. **Não associar uma resposta de código vazio por similaridade de nome, e-mail ou data.**

## Tratar cada diagnóstico

| Diagnóstico | Verificação e ação |
|---|---|
| `CODIGO_DE_REENVIO_ANTIGO` | Conferir se o histórico possui `forms_envio_id` e `email_envio` estruturados e se a execução do DD02 aceitou o envio anterior. Para registros legados sem esses campos, validar o vínculo antes de recuperar a resposta. A recuperação deve manter o `Response ID`, as 10/11 respostas e o código do envio como evidência. |
| `CODIGO_VAZIO` | Conferir no Forms se a resposta realmente não contém o código. Não há vínculo seguro automático; identificar com o terceiro e a trilha de auditoria antes de qualquer reparo. Conferir, sem mudar o formulário, se o preenchimento prévio está habilitado para os próximos envios. |
| `RESPOSTA_ATUAL_SEM_PROCESSAMENTO` | Localizar a execução DD02 pelo `Response Id`. Se falhou, corrigir o dado/configuração que a execução apontar e reenviar **a execução**; verificar o resultado no pai e nas filhas. Se não houve execução, verificar se o gatilho está ativo e conectado. |
| `GRAVACAO_PARCIAL` ou `FILHAS_SEM_CONSOLIDACAO` | Conferir linhas por `forms_item_chave` e execução DD02. A retomada deve completar apenas linhas faltantes e só depois atualizar o pai. Não duplicar linhas nem concluir o pai com questionário incompleto. |
| `FLUXO_INCOMPATIVEL`, `STATUS_INCOMPATIVEL`, `ENVIO_ATUAL_NAO_CONFIRMADO` | Conferir versão atual do item e histórico antes de qualquer escrita. O DD02 rejeita esses estados por desenho. |
| `CODIGO_NAO_ENCONTRADO` ou `CODIGO_AMBIGUO` | Revisão manual da origem e integridade dos dados. Não atribuir a uma solicitação por aproximação. |
| `SEM_RESPOSTA_LOCALIZADA` | O export do Forms não prova resposta para esse item. Verificar se o export abrange todas as respostas e se o terceiro usou o formulário correto. |

Depois de cada reparo, comparar: questionário v2 completo (10 perguntas, ou 11 se T1=`Sim`), `forms_ultima_resposta_id`, `data_resposta_terceiro`, `terceiro_gatilho_risco`, `classificacao_risco`, `risco_final`, `status`, `data_conclusao`/`data_vencimento` quando aplicável, e desdobramento `Resposta do terceiro`. Risco alto ou gatilho segue para `Pendente Compliance`; risco baixo/médio sem gatilho pode ser `Aprovado` automaticamente conforme a regra existente.

## Prevenir novas pendências sem mudar o Forms ou os fluxos

- Antes de reenviar, conferir no Forms e no histórico DD02 se já existe resposta para algum código da solicitação. Reenviar somente quando a ausência de resposta for confirmada; o novo código não revoga tecnicamente os links anteriores.
- Informar ao terceiro qual é o link mais recente e conferir o código preenchido antes de submeter. Respostas por links antigos devem ser preservadas e avaliadas conforme a regra de negócio definida em `ESTRATEGIA_RESILIENCIA_DD01_DD02.md`.
- Rodar a auditoria após cada export periódico; investigar toda resposta atual que não produziu `Resposta do terceiro` e toda resposta com código antigo ou vazio.
