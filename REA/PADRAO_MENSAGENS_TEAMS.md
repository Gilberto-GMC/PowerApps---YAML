# Padrão de comunicação do acionamento PLEM/PRAI no Teams

Refatoração de 2026-08-24. Cobre as mensagens do chat, os e-mails, os 3 fluxos
do Power Automate e a tela `ScreenAcionamentosPlemPrai`.

Gerado por (nunca editar as saídas à mão):

| Script | Saída |
|---|---|
| `padrao_mensagens_teams.py` | fonte única do formato (importado pelos outros dois) |
| `refatorar_fluxos_teams.py` | `MigracaoAIRPORTNOW_src/Workflows/*.json` (backup em `Workflows_backup/`) |
| `gerar_pacotes_fluxos_individuais.py` | `fluxos_individuais/*.zip` |
| `gerar_solucao_migracao.py` | `MigracaoAIRPORTNOW_1_0_0_6_managed.zip` — só se um dia os fluxos forem para solução |
| `gerar_solucoes_fluxos_individuais.py` | `solucoes_fluxos/*.zip` |
| `previa_mensagens.py` + `previa_artefato.py` | `previa/mensagens_acionamento.html` — confere o design antes de importar |
| `refatorar_msgs_teams.py` | `ScreenAcionamentosPlemPraiV2.pa.yaml` |

---

## 1. O problema que originou a refatoração

Na conversa do Teams do acionamento de teste apareceu:

```
Gerente Teste > Gilberto Marques Claudino > Notificado via Flow
Gerente Teste > Gilberto Marques Claudino > Notificado via Flow
Gerente Teste > Gilberto Marques Claudino > Notificado via Flow
Gerente Teste > Gilberto Marques Claudino > Notificado via Flow
```

Não era um problema de exibição. A rotina que remove participantes duplicados
era:

```
ClearCollect(
    col_emailsCcrFilter,
    ForAll(
        Distinct(col_emailsCcrFilter, Email),
        LookUp(col_emailsCcrFilter, Email = ThisRecord.Email)
    )
)
```

Dentro do `LookUp`, tanto `Email` quanto `ThisRecord.Email` resolvem para a
linha **do próprio `LookUp`** — o escopo interno vence o externo. A condição
vira `Email = Email`, sempre verdadeira, e o `LookUp` devolve **sempre o
primeiro registro**. Com 4 participantes distintos, a coleção virava 4 cópias
do primeiro: uma pessoa era notificada 4 vezes e **as outras três não recebiam
nada**. Num acionamento real isso é o COE achando que chamou o corpo de
bombeiros quando não chamou.

A correção usa alias explícito e normaliza o e-mail:

```
ClearCollect(
    col_participantesUnicos,
    ForAll(
        Distinct(col_emailsCcrFilter, Lower(Trim(Email))) As EMAIL_UNICO,
        LookUp(col_emailsCcrFilter, Lower(Trim(Email)) = EMAIL_UNICO.Value)
    )
);
ClearCollect(col_emailsCcrFilter, col_participantesUnicos);
```

O `Distinct` sobre uma **expressão** garante a coluna `Value` em qualquer modo
de compatibilidade, e a coleção intermediária evita `ClearCollect` de uma
coleção a partir dela mesma.

---

## 2. O formato único

Antes cada ponto do app montava a frase à mão: `"> chegou."`,
`"foi colocado em estado de sobreaviso."`, `"EQUIPAMENTO SOLICITADO > "`,
`"Notificado via Flow"`. Sem hora, sem hierarquia, com um `>` fazendo três
papéis diferentes na mesma linha.

Agora **o app manda dados e o fluxo monta a mensagem**. A chamada continua
tendo **os mesmos 2 parâmetros de sempre** — tipo, ator e detalhe viajam
codificados dentro de "Mensagem":

```
EnviarAtividadeparachatteams.Run( "CHEGOU§" & _ator & "§" & _detalhe , _chat )
```

Isso é deliberado. O gatilho **PowerApps V2 guarda o esquema dentro do app**:
trocar 2 parâmetros por 4 obrigaria a remover e re-adicionar o fluxo no Studio,
e é aí que o Power Apps renomeia para `EnviarAtividadeparachatteams_1` e o YAML
colado deixa de achar a referência. Mantendo o esquema **byte a byte**, a
atualização do fluxo é invisível para o app.

A compatibilidade vale nos dois sentidos:

| | fluxo antigo | fluxo novo |
|---|---|---|
| **app antigo** | como sempre foi | mensagem sem `§` publicada como sempre foi |
| **app novo** | aparece `CHEGOU§Entidade — Nome§` no chat: feio, nunca um erro | formato novo |

O app remove `§` de qualquer texto digitado (atividade manual, nome do
contatado, dados da vítima) antes de montar o payload, então os campos nunca
se embaralham.

O chat recebe sempre:

> **🟢 CHEGOU** · 12:57
> Corpo de Bombeiros — Juliana do Nascimento
> *(linha de detalhe, quando existe)*

| Tipo | Chat | Onde nasce |
|---|---|---|
| `ABERTURA` | 🚨 ACIONAMENTO ABERTO | cartão do fluxo Criar chat |
| `NOTIFICADO` | 📨 NOTIFICADO | fluxo Enviar Acionamento com Opção |
| `CIENTE` | ✅ CIENTE | resposta do participante no Teams |
| `RECUSADO` | ⛔ NÃO COMPARECERÁ | resposta do participante / botão da tela |
| `SEM_RESPOSTA` | ⏱️ SEM RESPOSTA | timeout de 4h |
| `ACIONADO` | 🔴 ACIONADO | botão "Sim, realizou contato" |
| `SOBREAVISO` | 🟡 SOBREAVISO | botão "Sim", ação SOBREAVISO |
| `INFORMADO` | 🔵 INFORMADO | botão "Sim", ação INFORMAR |
| `CHEGOU` | 🟢 CHEGOU | botão "Chegou" |
| `CONTATO_NR` | ⚠️ CONTATO NÃO REALIZADO | botão "Não atendeu" / contato sem e-mail |
| `EQUIPAMENTO` | 📦 EQUIPAMENTO SOLICITADO | galeria de equipamentos |
| `VITIMA_NOVA` | 🚑 VÍTIMA REGISTRADA | formulário MÉTODO START |
| `VITIMA_ALTERADA` | ✏️ VÍTIMA ATUALIZADA | formulário MÉTODO START |
| `VITIMA_EXCLUIDA` | 🗑️ VÍTIMA REMOVIDA | lixeira da galeria de vítimas |
| `MANUAL` | 📝 REGISTRO MANUAL | "Lançar atividade" |
| `ENCERRADO` | 🏁 ACIONAMENTO ENCERRADO | Finalizar Fluxo de Acionamento |

Um tipo desconhecido cai em `▫️ REGISTRO` — nunca deixa a mensagem sem publicar.

**No SharePoint o mesmo evento é gravado sem emoji**, para não sujar relatório
e Power BI: `CHEGOU · Corpo de Bombeiros — Juliana do Nascimento`.

A fala da pessoa (o comentário que ela escreve ao responder) sai em
`<blockquote>`, separada do texto do sistema, e some quando está vazia.

### O e-mail

O e-mail antigo era texto corrido com quatro linhas em branco no meio, sem
hora, sem protocolo e sem dizer o que a pessoa devia fazer. O novo segue a
ordem que importa para quem abre no celular no meio de uma emergência e lê só
as três primeiras linhas:

1. **faixa de severidade** — `EMERGÊNCIA REAL` ou `EXERCÍCIO SIMULADO`
2. **quem está sendo chamado e para quê** — "Olá, Juliana. Você foi acionado
   como Corpo de Bombeiros…"
3. **fatos** — aeroporto, emergência, protocolo, hora
4. **ocorrência**, em bloco destacado
5. **o que fazer agora**, em três passos numerados
6. rodapé com protocolo e "não responda a este e-mail"

Restrição do meio: o Outlook desktop renderiza com o motor do **Word** — sem
flexbox, grid, float ou folha de estilo externa. O template é tabela aninhada
com `cellpadding`/`cellspacing` zerados, tudo em `style` inline e largura
travada em 600 px. Vive em `padrao_mensagens_teams.email_acionamento()`.

**Um e-mail por pessoa, não dois.** O fluxo de criação do chat mandava um
e-mail para a lista inteira e, segundos depois, o fluxo de notificação mandava
outro individual — todo participante recebia duas mensagens quase idênticas. O
do chat foi removido; ficou o individual, que sabe o nome e a entidade de quem
recebe. Isso também tirou o conector do Outlook do fluxo de chat, que agora
pede uma conexão a menos na importação.

### O cartão de abertura

Adaptive Card com faixa de severidade sangrada (`bleed`), `FactSet` com os
dados da ocorrência e um bloco final em `emphasis` com a instrução. O título do
**chat** leva a severidade na frente, porque é o que aparece na lista de
conversas do Teams antes de alguém abrir.

### Conferir antes de importar

`previa/mensagens_acionamento.html` mostra tudo na ordem em que a pessoa
recebe, com um cenário de exemplo. O HTML do e-mail e o JSON do cartão são
extraídos dos fluxos gerados — não são recriados para a prévia.

Mudar o visual de todas as mensagens agora é editar `padrao_mensagens_teams.py`
e regerar — não são mais 9 fórmulas espalhadas pela tela.

---

## 3. Anti-travamento

Dois travamentos diferentes foram tratados.

### 3.1 A tela congelava esperando os fluxos

`EnviarAcionamentocomOpcao` fazia **envio de e-mail + post no Teams antes de
responder ao app**, e a tela chama esse fluxo dentro de um `ForAll` sobre os
participantes. Com 20 contatos, o Power Apps ficava parado somando o tempo de
20 e-mails.

Agora **"Responder ao app" é a primeira ação** desse fluxo e do
`EnviarAtividadeparachatteams`; no `CriarchatdeacionamentosPLEM/PRAI` a
resposta vem logo depois de criar o chat (o app precisa do ID) e o cartão, o
e-mail e o log rodam depois.

### 3.2 A tela ficava presa em estados sem saída

| Situação | Antes | Agora |
|---|---|---|
| Duplo clique em "Iniciar Fluxo de Acionamento" | dois acionamentos, dois chats | 2º clique recusado com aviso |
| Erro ao gravar a ocorrência | overlay de carregamento girando para sempre | `OnFailure` avisa, fecha o overlay e solta a trava |
| Nenhum participante no fluxograma | overlay girando para sempre | mensagem clara e overlay fechado |
| Botões de atividade clicados em sequência rápida | registros duplicados no log e no chat | trava de reentrância |

A trava é uma variável de contexto com carimbo de hora:

```
If(
    !IsBlank(var_ocupadoDesde) && DateDiff(var_ocupadoDesde, Now(), TimeUnit.Seconds) < 30,
    Notify("Aguarde: a ação anterior ainda está sendo processada.", NotificationType.Warning, 3000),
    UpdateContext({var_ocupadoDesde: Now()});
    ...trabalho...;
    UpdateContext({var_ocupadoDesde: Blank()})
)
```

Ela **se solta sozinha** depois de 30s (120s no botão de acionamento). É de
propósito: se qualquer coisa falhar no meio e a trava não for limpa, a tela
volta a funcionar em vez de ficar morta até o usuário reabrir o app.
`OnVisible` também limpa a trava e o overlay ao entrar na tela.

---

## 4. Validações acrescentadas

| # | Onde | Regra |
|---|---|---|
| V1 | 8 botões e 2 formulários | trava de reentrância |
| V2 | formulários de ocorrência e de vítima | `OnFailure` avisa, fecha overlay, solta trava |
| V3 | todas as 9 chamadas do chat | não chama o fluxo com `ID_chat` em branco; avisa que o registro foi salvo mas não publicado |
| V4 | "Lançar atividade" | exige texto (antes publicava `ATIVIDADE MANUAL:` vazio) |
| V5 | `OnVisible` da tela | limpa trava e overlay |
| C2 | início do acionamento | exige ao menos um participante **além do operador** — o teste antigo (`CountRows = 0`) nunca dava 0 porque o operador já tinha sido inserido |
| C7 | montagem dos participantes | operador sem e-mail válido não entra na lista (e-mail em branco derrubava o `CreateChat` inteiro) |
| V2f | fluxo Criar chat | e-mails em branco/sem `@` descartados; sem ninguém válido, responde `chat: ""` em vez de estourar |
| V4f | fluxo Enviar Acionamento | falha de e-mail não derruba mais o acionamento |
| V5f | fluxo Enviar Acionamento | contato sem e-mail vira ⚠️ no chat + log `CONTATO_NR`, em vez de sumir |
| V6f | todos os posts do Teams | retry exponencial explícito (4 tentativas) |

---

## 5. Correções de lógica

| # | Correção |
|---|---|
| C1 | deduplicação de participantes (seção 1) |
| C2 | validação de participantes que nunca validava + overlay preso |
| C3 | `LOG FINALIZAÇÃO` gravava `ID_chat: varChatID` — variável global da sessão que **criou** o acionamento. Quem finalizava depois gravava chat em branco. Agora usa o `ID_chat` do próprio registro. Também corrige `"Finalizado ás " & Now()` e passa a gravar `Hora`/`Ativo` |
| C4 | botão "Não vai comparecer" postava em `ThisItem.ID_chat` (podia estar em branco) e gravava em `Acao` o **nível da entidade** |
| C5 | exclusão de vítima lia `ThisItem` **depois** do `Remove()` e não gravava log nenhum |
| C6 | alteração de vítima era registrada como `REGISTRO DE VÍTIMA` |
| M3 | o encerramento do acionamento não era publicado no chat — o chat simplesmente parava |

---

## 6. Como aplicar sem quebrar o sistema

**Nenhuma assinatura de fluxo mudou.** Os 3 gatilhos saem byte a byte iguais
aos de hoje — o gerador aborta se algum mudar. Consequência prática: **não é
preciso remover nem re-adicionar fluxo nenhum no Power Apps Studio.**

### Rota — pacote herdado, escolhendo *Atualizar*

Os fluxos deste ambiente não estão em solução, então a importação é por
pacote herdado, um zip por fluxo, em **Power Automate > Meus fluxos >
Importar > Importar Pacote (Legado)**:

| Zip | Fluxo |
|---|---|
| `fluxos_individuais/CriarChatAcionamentosPLEMPRAI.zip` | Criar chat de acionamentos PLEM/PRAI |
| `fluxos_individuais/EnviarAcionamentoComOpcao.zip` | Enviar Acionamento com Opcao |
| `fluxos_individuais/EnviarAtividadeParaChatTeams.zip` | Enviar Atividade para chat teams |

O ponto que decide tudo é a caixa **Configuração de Importação** do fluxo:

> escolha **Atualizar** e selecione o fluxo que já existe no ambiente — **não**
> "Criar como novo".

Com *Atualizar*, a definição do fluxo é substituída e o **ID é preservado**:
o app continua apontando para ele e nada precisa ser mexido no Studio. Com
*Criar como novo*, entra uma cópia com ID novo, o app continua chamando a
antiga, e reapontá-lo exige remover/re-adicionar — que é onde o Studio
renomeia para `EnviarAtividadeparachatteams_1` e o YAML colado quebra.

Os pacotes já vêm com `Atualizar` como opção sugerida, então é o que o wizard
abre por padrão. Em *Recursos Relacionados*, mapeie as conexões (o nome da
connection reference original aparece como rótulo). O chat agora pede **duas**
conexões em vez de três — o Outlook saiu junto com o e-mail duplicado.

Envie o zip exatamente como está: não descompacte e recompacte, senão o
`manifest.json` sai da raiz.

### Depois dos fluxos

1. **Confirme no Power Automate** que os 3 fluxos continuam ativados e que a
   última execução não deu erro.
2. **Cole `ScreenAcionamentosPlemPraiV2.pa.yaml`** na tela pela *Exibição de
   código*. Nada mais no app precisa mudar.
3. **Teste em Ambiente Simulado** (seção 7).

Se você inverter a ordem nada quebra: o app novo mandando payload para o fluxo
antigo só produz mensagem feia no chat por alguns minutos.

### Rota alternativa — solução

`MigracaoAIRPORTNOW_1_0_0_6_managed.zip` continua sendo gerado (mesma solução
gerenciada, versão 1.0.0.5 → 1.0.0.6, mesmos `WorkflowId`, só 4 dos 14
arquivos diferentes). Serve se um dia os fluxos forem migrados para solução.

### Rollback

| Camada | Como voltar |
|---|---|
| Fluxos | O Power Automate guarda a versão anterior de cada fluxo; as definições originais também estão em `MigracaoAIRPORTNOW_src/Workflows_backup/` |
| Tela | Colar de volta `ScreenAcionamentosNewPlemPrai.pa.yaml` (o export intocado, que continua no repositório) |

As duas camadas voltam de forma independente: como as assinaturas não mudaram,
tela nova com fluxo velho e tela velha com fluxo novo continuam funcionando.

## 7. Teste de aceite sugerido

1. Abrir acionamento em Ambiente Simulado com 3+ participantes de entidades
   diferentes → o chat deve ter **um cartão** e **uma linha 📨 por pessoa**,
   sem repetição.
2. Clicar duas vezes rápido em "Iniciar Fluxo de Acionamento" → um único
   acionamento e o aviso "já está sendo processado".
3. Responder "Não poderei comparecer" no Teams → linha ⛔ no chat e os botões
   de ação daquela pessoa somem da tela.
4. Deixar um participante sem responder → ⏱️ após 4h (ou baixe o `timeout`
   para `PT5M` no fluxo para testar).
5. Emergência sem fluxograma cadastrado → mensagem clara e **tela liberada**
   (sem spinner preso).
6. Finalizar o acionamento → 🏁 no chat.

---

## 8. `DelayItemLoading` / `LoadingSpinner` — investigado e resolvido

A rodada anterior (`otimizar_tela_plem_prai.py`, ganho "P2") injetava
`DelayItemLoading: =true` + `LoadingSpinner: =LoadingSpinner.Data` nas 25
galerias. O arquivo foi colado no Studio e o reexport voltou **sem nenhuma das
duas**, sem erro nenhum.

Diagnóstico: o Studio grava as propriedades em **ordem alfabética**.
Propriedade fora dessa ordem foi injetada por script; em ordem alfabética foi
escrita pelo próprio Studio — e isso prova que o controle a suporta. Varrendo
todos os exports do repositório:

| Propriedade | Onde aparece | Em ordem alfabética? |
|---|---|---|
| `LoadingSpinner` | 7 galerias `Gallery@2.15.0` em 3 telas de PerdidoseAchados, com os mesmos `Variant` desta tela | **sim** — Studio escreveu |
| `DelayItemLoading` | 3 ocorrências, todas em arquivos gerados por script | **não, em nenhuma** |

`DelayItemLoading` é propriedade da galeria **clássica**. Todas as galerias
deste repositório são `Gallery@2.15.0` (moderna), que não a tem — o Studio
descarta em silêncio, e levou `LoadingSpinner` junto no mesmo bloco.

**O ganho P2 nunca existiu.** Não foi reaplicado, e a injeção foi retirada
também de `otimizar_tela_contatos.py` (que ainda produzia
`ScreenContatosOtimizada.txt` com a propriedade inválida).

`LoadingSpinner` sozinho é válido e ficou disponível como opção explícita,
**desligada por padrão** — é cosmético (spinner enquanto carrega), não é
performance, e mexe no que o operador vê:

```
python3 refatorar_msgs_teams.py --spinner --sonda   # 1 galeria, para testar
python3 refatorar_msgs_teams.py --spinner           # as 25
```

A sonda existe para fechar o ciclo que faltou da primeira vez: colar,
**reexportar e conferir que a propriedade continua lá** antes de valer para 25
galerias. A inserção é feita na posição alfabética, como o Studio faz, então o
reexport sai idêntico.

## 9. Rodada corporativa (2026-08-24) — identidade, auditoria e app

### Zero emoji, em todos os meios

Nenhum dos quatro meios aceita ícone de verdade: o Outlook renderiza com o motor
do Word (sem SVG, imagem externa bloqueada), o Adaptive Card 1.4 não tem `Icon`
(é 1.5+) e `Image` exigiria URL hospedada, o chat do Teams remove estilo, e o
`HtmlViewer` do Power Apps remove `<svg>`. Então o emoji saiu e a identidade
passou a vir de **tipografia, cor e chips de texto** — inclusive nos rótulos do
próprio app (`Editar`, `Excluir`, `Salvar`, `Consultar…`, `Deseja realmente
excluir?`…). As setas `⬇` do fluxograma viraram `↓` tipográfico: o caractere
carrega significado (direção), então foi **substituído**, não removido.

São 19 linhas ao todo — 12 rótulos que perderam o emoji e 7 setas trocadas — e
a tela sai com **zero** caracteres da faixa emoji, verificado por
`verificar_tela.py`.

### Paleta

Tokens em `padrao_mensagens_teams.py`, derivados do azul que os componentes HTML
mais recentes já usavam (`#0B2E4F`):

| Papel | Cor |
|---|---|
| Navy de marca | `#0B2E4F` |
| Azul de ação | `#155E8F` |
| Emergência real | `#A62639` |
| Exercício simulado | `#8A6100` |
| Texto / secundário | `#22303B` / `#5D6B77` |
| Fundo / linhas | `#F5F7F9` / `#DFE5EA` |

Status no app: `ACIONAR #B98900` (mata o `#FFFF00` puro), `SOBREAVISO #C05621`,
`INFORMAR #155E8F`, `CHEGOU #1F7A4D`, `CONTATO_NR #A62639`, `NOTIFICADO #E8EDF2`.
As ações que antes caíam no transparente (`CRIAÇÃO`, `FINALIZAÇÃO`, `ATIVIDADE
MANUAL`, `REGISTRO DE VÍTIMA`) ganharam cor própria.

#### Dois pesos, uma paleta (F1–F11, 2026-08-24)

A tela ficou com duas paletas convivendo: a lista de atividades já usava os
chips corporativos, e a legenda + o fluxograma continuavam nos tons vivos do
export original (`#FFFF00`, `#FF0000`, verde `#349730`). Agora é uma paleta só,
em dois pesos — **mesmo matiz, papel diferente**:

| Estado | Chip / borda / CTA (forte) | Legenda e pílula (superfície) |
|---|---|---|
| Nenhuma ação | — | `#FFFFFF` |
| Notificado | `#E8EDF2` | `#E8EDF2` (o chip já é claro) |
| Acionado | `#B98900` | `#E8C25E` |
| Sobreaviso | `#C05621` | `#E59468` |
| Informado | `#155E8F` | `#6BA7D1` |
| Chegou | `#1F7A4D` | `#6BBF95` |
| Contato não realizado / Não comparecerá | `#A62639` | `#E08E9C` |

**Por que dois pesos e não um só.** O chip da atividade é pequeno e leva texto
branco sobre cor cheia. A legenda e as pílulas do fluxograma são superfícies
grandes que herdam texto **preto** do controle. Pintar essas superfícies com a
cor forte obrigaria a calcular também a cor do texto — e `Color` é outra
propriedade, ou seja, **outra consulta ao SharePoint por linha** do fluxograma
(hoje é 1 por pílula; viraria 2 em N entidades × 3 colunas). Numa tela que já
teve queixa de travamento, o preço não se paga. Todas as superfícies têm
contraste ≥ 4,5:1 com o texto `#22303B`.

Onde cada peso entra:

- **superfície** — os 7 rótulos da legenda (`Label11_1`, `_8`…`_13`) e as três
  pílulas do fluxograma (`Button1_1` ACIONAR, `Button1_4` SOBREAVISO,
  `Button1_7` INFORMAR);
- **forte** — a borda dos cabeçalhos de coluna (`Button1_11`, `_17`, `_16`:
  1 px vazado, a versão clara sumiria no branco), os CTAs `ButtonChegou`
  (`#1F7A4D`) e `ButtonNaoVaiComparecer` (`#A62639`), o chip do timeline
  (`HtmlText13`) e a faixa de status (`Container33`).

Fonte de verdade: `STATUS_APP` e `SUPERFICIE_APP` em `padrao_mensagens_teams.py`
— os mesmos dicionários que os fluxos consomem. `verificar_tela.py` confere a
tela contra eles e reprova se a legenda ou as pílulas saírem da paleta.

Fora do escopo de propósito: o vermelho/amarelo das **Prioridades I–IV** de
vítimas é o código de triagem START, não decoração — continua como está.

### E-mail: cabeçalho branco, não bloco de cor

Barra fina de 3 px no topo + wordmark **AIRPORT NOW** em navy + **chip** de
severidade contornado. A cor forte aparece só na barra, no chip e no acento da
ocorrência — o bloco chapado saiu.

### Auditoria implementada (B1–B19)

| # | Correção |
|---|---|
| **B1** | **Iniciar um acionamento PRAI caía no ramo `else`** — gravava `FINALIZAÇÃO` imediata e notificava "finalizado com sucesso". O teste passou a ser só `var_acaoFormOcorrenciaAcionamento = "Iniciar"`, e o protocolo usa o tipo real |
| B2 | Log `CRIAÇÃO` perdeu o hack `DateAdd(Now(), -1, Minutes)` (que invertia a ordem se o `ForAll` passasse de 1 min) e ganhou `Ativo`/`ID_emergencia` |
| B3 | `NOTIFICADO` ganhou `Ativo: 0` — nulo nunca casava com `Ativo = 0` e o botão "Acionar" não aparecia |
| B4 | Botão "Sim" gravava `Acao` do **nível do contato** com texto da **coluna clicada**: clicar em SOBREAVISO num contato ACIONAR gravava `Acao="ACIONAR"` com texto de sobreaviso |
| B5 | Galeria de atividades: `SortByColumns` saiu de cima do `If` (rodava em memória sobre a 1ª página) e `StartsWith` virou igualdade (o filtro "ACIONAR" trazia `ACIONAR_SOBREAVISO`). O combo lista as 13 ações |
| B6 | Cor de status da entidade passa a ignorar atividade `Excluido` |
| B7 | `Select(Function_consultarAtividades)` restaurado ao excluir/restaurar (a galeria só atualizava no timer de 30 s) |
| B8 | Busca de acionamento tolera texto não numérico e recuperou o `Sort` |
| B9 | `RemoveIf` não é delegável: exclusão parcial agora é detectada e avisada |
| **B10** | O "Sim" do diálogo de exclusão tinha o `OnSelect` **inteiro comentado**, colado em sintaxe pt-BR (`;` e `;;`) que nunca compilou: clicar não fazia absolutamente nada |
| B11 | Botão PRAI não definia `var_aeroSelect`/`var_acao` — a galeria filtrava pelo aeroporto da sessão PLEM anterior |
| B12 | "Acionar" pela galeria de atividades não definia `var_acionarEntidade` — listava os contatos da entidade anterior |
| B13 | Ramo PLEM voltou a popular `col_emergencias` (só o PRAI populava; 6 galerias leem a coleção) |
| B14 | Cards de telefone exibiam `tel_principal`/`tel_reserva` e gravavam `tel_fixo`/`tel_cel_institucional` |
| B15 | Data de término e relatório final obrigatórios ao finalizar |
| B16 | `OnSuccess` do form de equipamento gravava numa coleção que a galeria não lê |
| B17 | `ClearCollect` re-consultava o SharePoint em corrida com o `RemoveIf` (a linha excluída podia reaparecer) |
| B18 | `OnFailure` nos formulários restantes |
| B19 | Script de ligação não reconhecia `MAYDAY … - TESTE` (igualdade em lista → detecção por conteúdo) |

### Pendências residuais, agora fechadas (E)

| # | Correção |
|---|---|
| **E1** | **Excluir vítima de Prioridade II, III ou IV não gerava log nem aviso no chat.** Só a Prioridade I registrava; nas outras três o `Remove` era mudo. As três passaram a gravar `EXCLUSÃO DE VÍTIMA` e publicar no chat, como a primeira |
| E2 | Busca de equipamentos voltou a filtrar pelo aeroporto do acionamento (o `Filter` estava comentado no meio da expressão e a busca listava **todos** os aeroportos) |
| E3 | `OnVisible` deixou de carregar ~947 contatos em `col_contatos_acionamentos` — coleção que nem esta tela nem a de Contatos lê |
| E4 | O status por entidade passou a ser calculado **uma vez** em `col_statusEntidade`, dentro de `Function_consultarAtividades`. Antes cada uma das 3 pílulas do fluxograma rodava `First(Sort(Filter(tbl_atividadesPlemPrai…)))` dentro da própria `Fill`: uma consulta por linha, a cada render |
| E5 | O timer comparava o último ID da lista com o da galeria — **os dois vindos do mesmo cache**, sempre iguais, então o `Refresh` quase nunca acontecia. Agora o `Refresh` é o passo, não a consequência |

### Comunicação (C)

17 mensagens `Notify` padronizadas: acentuação correta, exclusão sempre
`Warning`, sucesso específico, erro dizendo o que fazer, durações
3000/5000/8000.

### Componentes HTML do app (D)

`HtmlText13` (timeline) ganhou chip de status cobrindo todos os valores de
`Acao`; `HtmlText11_3` perdeu o `<font color>` legado; `HtmlText9` (script de
ligação) e `HtmlText11_1` (cartão de contato) foram alinhados à paleta.

### Trava de layout com exceções declaradas

A guarda continua reprovando qualquer mudança visual, mas agora aceita
**exceções nominais** (4 linhas que somem, 5 que surgem) e uma **regra
declarada** para rótulos que perderam apenas o emoji. Exceção declarada que não
se aplica também reprova — não existe liberação genérica.

### O que continua em aberto

Duas coisas, ambas por serem mudança de **estrutura de controles** — o layout
que você pediu para não mexer:

- **~20 variáveis de contexto mortas** (`var_acaoFluxoPrai`,
  `var_visibleAcaoFluxoPrai`, `var_viewAtividades`…). São `UpdateContext`, ou
  seja, escopo de tela — removê-las é seguro, mas mexe em muitas fórmulas de
  uma vez e rende pouco. Vale uma rodada própria.
- **4 galerias de vítimas duplicadas** (Prioridade I a IV, ~130 linhas cada,
  diferindo só na string). Consolidar exige remover controles. Elas também
  divergem entre si no visual: a Prioridade I mostra `às {hora}` e as outras
  não; II/III/IV têm um ícone de pessoa que a I não tem. Os **bugs** dessas
  galerias já foram corrigidos (E1) — resta a duplicação estrutural.

### Como verificar

```
python3 verificar_tela.py     # YAML, árvore de 934 controles, emoji, aridade, parênteses
python3 auditar_pacotes.py    # 69 checagens nos zips que serão importados
```

## 10. Sugestões que ficaram fora deste pacote

Estão fora porque mudam contrato ou custam mais teste do que a correção valia
agora. Em ordem de retorno:

1. **Um fluxo em lote no lugar do `ForAll`.** Hoje a tela chama
   `EnviarAcionamentocomOpcao` uma vez por participante. Mesmo com a resposta
   imediata, são N chamadas HTTP. Um único fluxo recebendo o JSON inteiro e
   fazendo `Apply to each` com concorrência tira isso do app: 1 chamada em vez
   de 20, e a tela volta a responder em ~1s.
2. **Fila de reenvio.** Se o `CreateChat` falhar, o acionamento hoje segue sem
   chat e as mensagens ficam sem destino. Um campo `ID_chat` vazio +
   um botão "recriar chat" na tela de monitoramento resolveria sem retrabalho.
3. **Painel de resposta no cabeçalho do monitoramento.** `3 cientes · 1 a
   caminho · 2 sem resposta` calculado a partir de `tbl_atividadesPlemPrai`. É
   a informação que o COE mais procura e hoje ela só existe rolando a lista.
4. **`Acao` como enumeração local.** Hoje convivem `ACIONAR`,
   `ACIONAR_SOBREAVISO`, `SOBREAVISO`, `RESPONDEU AO FLOW`, `NAO COMPARECERA`,
   `CONTATO_NR`, `CRIAÇÃO`, `FINALIZAÇÃO`… com grafias e acentos inconsistentes,
   e os `Switch` de cor/visibilidade da galeria dependem dessa string. Vale uma
   tabela em `App.Formulas` com chave → rótulo → cor, e a galeria lendo dali.
5. **Cartão adaptativo com botões no chat** (Ciente / A caminho / Não vou), em
   vez da mensagem de escolha individual. Uma mensagem só no chat do grupo,
   todo mundo vê quem respondeu o quê, e some o e-mail individual.
6. **Registrar quem clicou.** Nenhum log de atividade grava o usuário que
   executou a ação (só o nome do contatado). Um campo `Usuario` em
   `tbl_atividadesPlemPrai` resolveria a auditoria do acionamento.
