# Roteiro guiado — Solicitação de novo módulo

O que o usuário preenche, o que ele vê depois e o que se espera dele em cada
etapa. Complementa [ARQUITETURA_CHAMADOS.md](ARQUITETURA_CHAMADOS.md) §4.2 e as
colunas de `tbl_ChamadoDemanda` em
[ESTRUTURA_LISTAS_CHAMADOS.md](ESTRUTURA_LISTAS_CHAMADOS.md).

---

## 1. Catálogo de temas

Dez categorias, dois ciclos. O catálogo vive em `App.Formulas` — ver
[AppFormulas_Chamados.fx.md](AppFormulas_Chamados.fx.md).

### Ciclo A — Suporte

| Chave | Tema | Prioridade padrão | 1ª resposta | Solução | Roteiro? |
|---|---|---|---|---|---|
| `RESET_SENHA` | Reset de senha | — | imediata | imediata | auto-atendimento |
| `ACESSO` | Acesso e permissão | ALTA | 4 h | 1 dia útil | não |
| `ERRO` | Erro no sistema | ALTA | 4 h | 1 dia útil | não |
| `DUVIDA` | Dúvida de uso | BAIXA | 1 dia útil | 5 dias úteis | não |
| `DADO` | Correção de dado ou registro | MEDIA | 8 h | 3 dias úteis | não |
| `DESEMPENHO` | Lentidão ou desempenho | MEDIA | 8 h | 3 dias úteis | não |

### Ciclo B — Demanda de produto

| Chave | Tema | Prioridade padrão | 1ª resposta | Solução | Roteiro? |
|---|---|---|---|---|---|
| `NOVO_MODULO` | Solicitação de novo módulo | MEDIA | 2 dias úteis | previsão na aprovação | **sim, 5 passos** |
| `MELHORIA` | Melhoria em módulo existente | MEDIA | 2 dias úteis | previsão na aprovação | **sim, 5 passos** |
| `RELATORIO` | Novo relatório ou indicador | BAIXA | 3 dias úteis | previsão na aprovação | **sim, reduzido** |
| `INTEGRACAO` | Integração com outro sistema | MEDIA | 3 dias úteis | previsão na aprovação | **sim, 5 passos** |

O ciclo B **não tem SLA de solução**. Tem SLA de primeira resposta e, depois da
aprovação, uma **previsão de entrega** (`desk_previsao_entrega`). Prometer prazo
de solução na abertura de uma demanda é prometer o que não se sabe.

`RELATORIO` usa o roteiro reduzido: passos 1, 3 e 5. Não faz sentido perguntar
"como é feito hoje" para um indicador que ainda não existe.

---

## 2. O roteiro — 5 passos

Regras que valem para os cinco:

- Um passo por tela, com barra de progresso `Passo N de 5`.
- **Voltar nunca perde o que foi digitado.** As respostas vivem em variáveis de
  contexto até o envio final; só o botão Enviar grava.
- O botão Avançar só habilita com os campos obrigatórios do passo preenchidos.
  Nada de deixar avançar e reclamar no fim.
- Cada passo tem um bloco de ajuda com **um exemplo real**, não uma instrução
  genérica. Exemplo é o que faz o usuário entender o que se espera.
- Rascunho: sair do wizard pergunta se quer descartar. Não há "salvar rascunho"
  na onda 3 — se virar necessidade, é uma coluna `dem_rascunho` e um filtro.

### Passo 1 — O que você precisa

> **Ajuda na tela:** "Dê um nome ao que você imagina. Não precisa ser o nome
> final — precisa ser reconhecível. Ex.: *Controle de Ordens de Serviço da
> Manutenção*."

| Campo | Tipo na tela | Obrig. | Coluna |
|---|---|---|---|
| Nome do módulo | Texto (uma linha, 80) | sim | `dem_nome_modulo` |
| Área solicitante | ComboBox do catálogo de áreas | sim | `dem_area` |
| Aeroportos impactados | ComboBox múltiplo + opção `TODOS` | sim | `dem_aeroportos` |

### Passo 2 — Como é hoje

> **Ajuda:** "Descreva o caminho que o dado faz hoje, do início ao fim. Se hoje
> não existe nada, escreva *não existe* — isso também é resposta. Ex.: *o
> encarregado anota a ocorrência num caderno, digita numa planilha no fim do
> turno e envia por e-mail para a coordenação.*"

| Campo | Tipo na tela | Obrig. | Coluna |
|---|---|---|---|
| Como é feito hoje | Texto multilinha (1000) | sim | `dem_como_e_hoje` |
| Ferramenta atual | ComboBox: Excel / Papel / E-mail / Outro sistema / Não existe | sim | `dem_ferramenta_atual` |
| Volume mensal aproximado | Número | não | `dem_volume_mensal` |
| Tempo gasto por registro | ComboBox: <5 min / 5–15 min / 15–60 min / >1 h | não | `dem_tempo_gasto` |
| Quem executa hoje | Texto (uma linha) | não | `dem_quem_executa` |

**Volume e tempo são o que transforma a demanda em prioridade.** Não são
obrigatórios porque o usuário nem sempre sabe — mas a tela mostra, ao lado, o
ganho estimado (`volume × tempo`) assim que os dois são preenchidos. Ver o número
aparecer é o que faz o usuário se dar ao trabalho de estimar.

### Passo 3 — O que precisa mudar

> **Ajuda:** "Liste as informações que precisam ficar registradas e quem vai
> consultá-las. Pense em quem lê, não em quem digita."

| Campo | Tipo na tela | Obrig. | Coluna |
|---|---|---|---|
| O que precisa ser registrado | Texto multilinha (1000) | sim | `dem_o_que_registrar` |
| Quem consulta | Texto multilinha (500) | sim | `dem_quem_consulta` |
| Decisões que dependem disso | Texto multilinha (500) | não | `dem_decisoes` |
| Indicadores esperados | Texto multilinha (500) | não | `dem_indicadores` |

### Passo 4 — Regras e obrigações

> **Ajuda:** "Se existe norma, auditoria ou prazo legal por trás, diga qual. Isso
> muda a prioridade da demanda."

| Campo | Tipo na tela | Obrig. | Coluna |
|---|---|---|---|
| É exigência regulatória? | Toggle SIM/NAO | sim | `dem_regulatorio` |
| Norma / referência | Texto (uma linha) | **se regulatória = SIM** | `dem_norma` |
| Exige evidência ou anexo? | Toggle SIM/NAO | não | `dem_exige_evidencia` |
| Exige aprovação no fluxo? | Toggle SIM/NAO | não | `dem_exige_aprovacao` |

Os três toggles gravam **Texto** `"SIM"`/`"NAO"`, nunca Sim/Não do SharePoint.

### Passo 5 — Patrocínio e urgência

> **Ajuda:** "O patrocinador é quem responde pela demanda quando TI precisar
> decidir escopo. Precisa saber que foi indicado."

| Campo | Tipo na tela | Obrig. | Coluna |
|---|---|---|---|
| Patrocinador | ComboBox de pessoas | sim | `dem_patrocinador_email` |
| Prazo desejado | DatePicker | não | `dem_prazo_desejado` |
| Impacto se não for feito | Texto multilinha (1000) | sim | `dem_impacto_sem` |
| Anexos | Attachments | não | anexos de `tbl_ChamadoDemanda` |

### Revisão e envio

Tela final somente-leitura com tudo o que foi respondido, cada bloco com um link
"editar" que volta ao passo. O botão Enviar:

1. Grava o chamado em `tbl_ServiceDesk` com `desk_ciclo = "DEMANDA"`,
   `desk_status = "Aberto"`, `desk_etapa = 1`.
2. Grava o registro 1-para-1 em `tbl_ChamadoDemanda`.
3. Grava a abertura em `tbl_ChamadoHistorico`.
4. Envia e-mail ao solicitante **e ao patrocinador**.

Os quatro passos numa ordem que resiste a falha: o chamado primeiro. Se a gravação
da demanda ou o e-mail falhar, existe um chamado rastreável — nunca uma demanda
órfã sem chamado. O tratamento é o mesmo já aplicado na tela de abertura:
overlay desligado antes dos efeitos, tudo dentro de `IfError`, aviso na tela em
vez de navegação silenciosa.

---

## 3. Acompanhamento — as 7 etapas

É isto que o usuário vê na tela de detalhe: uma trilha com sete marcos, o atual
destacado, os anteriores com data, os seguintes em cinza. `desk_etapa` guarda o
número; o status detalhado continua em `desk_status`.

| Etapa | Nome na tela | Status internos | O que TI faz | O que se espera do usuário |
|---|---|---|---|---|
| 1 | **Recebida** | `Aberto` | Confirma recebimento e faz a leitura inicial | Nada. Aguardar |
| 2 | **Em análise** | `Em análise`, `Aguardando informações` | Avalia viabilidade, esforço e encaixe com o que já existe | **Responder rápido** se voltar como *Aguardando informações* — o relógio para aqui |
| 3 | **Em aprovação** | `Aguardando aprovação` | Leva ao gestor com estimativa | Nada. O patrocinador pode ser consultado |
| 4 | **Aprovada e priorizada** | `Em backlog` | Define a previsão de entrega | Acompanhar a previsão. Se mudou a urgência, dizer aqui |
| 5 | **Em desenvolvimento** | `Em desenvolvimento` | Constrói | Ficar disponível para dúvidas de regra de negócio |
| 6 | **Em homologação** | `Em homologação`, `Ajustes solicitados` | Entrega para teste | **Testar e dar o aceite** — ou apontar o que está errado. É a etapa que mais trava por falta de resposta |
| 7 | **Entregue** | `Entregue`, `Fechado` | Publica e acompanha o uso | Usar. Reportar problema abre chamado novo, não reabre este |

Caminhos de saída fora da trilha:

- **Reprovada** (`Reprovado`, a partir da etapa 3) — a trilha fica cinza e a tela
  mostra `desk_motivo_recusa` em destaque. Motivo é obrigatório: demanda
  reprovada sem motivo escrito volta como demanda nova em três meses.
- **Cancelada** (`Cancelado`, até a etapa 3) — o solicitante cancela pela própria
  tela de detalhe, com confirmação.

### O que a tela mostra em cada etapa

Além da trilha, três blocos fixos:

1. **Onde está** — etapa atual, há quantos dias, e quem é o responsável agora
   (TI ou o próprio usuário, quando está *Aguardando informações* ou
   *Em homologação*). Deixar explícito que a bola está com o usuário é o que faz
   a demanda andar.
2. **Linha do tempo** — de `tbl_ChamadoHistorico`, mais recente no topo.
3. **Conversa** — de `tbl_ChamadoInteracao`, com campo para responder e anexar.

---

## 4. Notificações

Um e-mail por transição de etapa, nunca por transição de status interno — senão o
usuário recebe cinco e-mails em um dia e para de ler.

| Evento | Para | Assunto |
|---|---|---|
| Abertura | solicitante + patrocinador | `#000123 — Demanda recebida` |
| Entra em *Aguardando informações* | solicitante | `#000123 — Precisamos de mais informações` |
| Aprovada | solicitante + patrocinador | `#000123 — Demanda aprovada — previsão dd/mm` |
| Reprovada | solicitante + patrocinador | `#000123 — Demanda não aprovada` |
| Entra em homologação | solicitante | `#000123 — Pronto para seu teste` |
| Entregue | solicitante + patrocinador | `#000123 — Entregue` |
| Sem resposta há 3 dias em *Aguardando informações* ou *Em homologação* | solicitante | lembrete |

O corpo do e-mail se monta **no fluxo, não no app** — lição já registrada em
`LICOES_APRENDIDAS_POWERAPPS_YAML.md`. O app manda `desk_id`, evento e destinatário;
o fluxo resolve texto e formatação por um `json()` indexado pelo evento, com
`coalesce` para um padrão. Evento desconhecido nunca deixa a mensagem sem enviar.

O lembrete de 3 dias é o único que não nasce de ação do usuário: é um fluxo
agendado diário que varre a mestre por status e `desk_data_limite`.

---

## 5. Pendências antes de construir a onda 3

- Quem aprova: gestor de TI, comitê ou o patrocinador da área?
- Existe catálogo de áreas da Motiva para o ComboBox do passo 1, ou digita livre?
- O aceite da etapa 6 é do solicitante ou do patrocinador?
- Reabertura de demanda entregue: permitida ou sempre chamado novo? (a proposta
  acima é sempre chamado novo)
