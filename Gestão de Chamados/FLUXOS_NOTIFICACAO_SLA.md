# Fluxos de notificação e SLA — Onda 4 | Gestão de Chamados

Especificação dos dois fluxos do Power Automate que fecham a onda 4. Complementa
[ARQUITETURA_CHAMADOS.md](ARQUITETURA_CHAMADOS.md) §8 e
[ROTEIRO_NOVO_MODULO.md](ROTEIRO_NOVO_MODULO.md) §4.

> **Estado: especificado, não construído.** Nada aqui existe no tenant ainda.
> Este documento é o que se constrói, não o que já roda.

---

## 0. Premissas assumidas

As quatro pendências de negócio do ARQUITETURA §8 continuam abertas. Para não
travar a construção, cada uma recebe um **padrão explícito** — todos escolhidos
para serem uma linha de mudança, não uma refatoração:

| Pergunta aberta | Padrão adotado | Onde muda se a resposta for outra |
|---|---|---|
| Quem aprova demanda | quem tem `usr_papel_chamados = "GESTOR"` em `User` | destinatário do evento `APROVACAO_PENDENTE`, resolvido por consulta à lista `User` dentro do fluxo |
| SLA de demanda | **previsão, não prazo** — `desk_data_limite` fica em branco no ciclo DEMANDA | `nfCategorias.SlaSolucao` já é `0` para as quatro categorias de demanda; passar a valer é preencher a coluna |
| Teams além de e-mail | **só e-mail** na onda 4 | ramo novo no fim do `NotificarChamado`, depois do envio — nunca antes do `Responder ao app` |
| Prazo de reabertura | **7 dias** | variável `varDiasReabertura` no topo do `VarrerSlaChamados` |

Adotar padrão não é decidir pela área. É deixar o fluxo construído e a decisão
reduzida a um campo.

---

## 1. Por que dois fluxos, e não um nem cinco

| Fluxo | Gatilho | Papel |
|---|---|---|
| `NotificarChamado` | PowerApps V2 (`.Run()`) | tudo que nasce de **ação de gente** na tela |
| `VarrerSlaChamados` | Recorrência diária | tudo que nasce da **passagem do tempo** |

Só existem duas origens de evento no módulo, então só existem dois fluxos. Um
fluxo por evento multiplicaria a mesma lógica de montagem de e-mail por quinze;
um fluxo só obrigaria o gatilho agendado a fingir ser chamado pelo app.

**As transições automáticas do diagrama de estados são do fluxo agendado, não do
app.** `Aguardando usuário → Fechado` (5 dias) e `Resolvido → Fechado` (7 dias)
não têm ninguém para clicar — se o app fosse dono delas, um chamado de quem nunca
mais abriu o app ficaria aberto para sempre.

---

## 2. `NotificarChamado` — gatilho do app

### 2.1 Assinatura: um parâmetro de texto, e só

```
NotificarChamado.Run(varDeskPayload)
```

**Um único parâmetro de texto**, com os campos separados por `§`:

```
evento § desk_id § destinatario § cc § ator § detalhe
```

Isto não é economia de digitação — é a lição
*"não mude a assinatura do gatilho"* aplicada **antes** de doer. O gatilho
PowerApps V2 guarda o esquema **dentro do app**: acrescentar um parâmetro depois
obriga a remover e re-adicionar o fluxo em *Dados > Power Automate*, e nesse passo
o Studio renomeia para `NotificarChamado_1` e todo o YAML colado deixa de
encontrar a referência. Com um parâmetro só, **todo evento futuro é grátis**.

Regras do payload:

1. O app **remove `§` de todo texto digitado** antes de concatenar:
   `Substitute(varDeskDetalhe; "§"; " ")`. Um `§` colado numa descrição
   desalinharia todos os índices seguintes.
2. `cc` e `detalhe` podem vir vazios — o campo existe, o conteúdo não.
3. No fluxo, o `split` recebe padding para os índices existirem sempre:

```
@split(concat(coalesce(triggerBody()?['text'], ''), '§§§§§'), '§')
```

Sem o padding, um payload curto estoura o índice — e `if()` no Logic Apps
**avalia os dois ramos**, então índice fora de faixa quebra o fluxo mesmo no ramo
que não seria usado.

### 2.2 Ordem das ações — `Responder ao app` é a primeira

```
1. Responder ao Power App        →  {resultado: "ok"}
2. Inicializar variáveis (split do payload)
3. Compor: catálogo de eventos (json)
4. Resolver o evento (coalesce → PADRAO)
5. Obter item de tbl_ServiceDesk por desk_id
6. [se evento = ABERTURA] Obter anexos + conteúdo
7. Enviar e-mail (V2)
8. [reservado] postar no Teams
```

`.Run()` só devolve o controle ao app quando o fluxo chega em **Responder ao
Power App**. Se essa ação estivesse no fim, a tela de detalhe ficaria congelada a
cada clique de transição pelo tempo de montar e enviar e-mail. Respondendo
primeiro, o clique volta instantâneo.

**Efeito colateral aceito:** o app deixa de saber se o e-mail falhou. Para
notificação é troca boa — a fonte da verdade do que aconteceu com o chamado é
`tb_chamadoHistorico`, gravado pelo app **antes** de chamar o fluxo. E-mail
perdido é um aviso perdido, não um estado perdido. Todo envio leva `retryPolicy`
exponencial.

### 2.3 O corpo se monta no fluxo

O app manda **evento e dados**. Assunto, saudação e corpo saem de um `json()`
indexado pelo evento, com `coalesce` para a chave `PADRAO` — evento desconhecido
nunca deixa a mensagem sem enviar.

```
@coalesce(
    json(variables('catalogo'))?[variables('evento')],
    json(variables('catalogo'))?['PADRAO']
)
```

Catálogo (ação **Compor**, um só lugar no módulo inteiro que sabe o que cada
e-mail diz):

| Evento | Quem dispara | Para | Assunto |
|---|---|---|---|
| `ABERTURA` | `OnSuccess` da abertura, ciclo SUPORTE | solicitante · cc TI | `#000123 — Chamado aberto` |
| `RESET_OK` | auto-atendimento de senha | solicitante · cc TI | `#000123 — Senha temporária` |
| `ASSUMIDO` | Aberto → Em atendimento | solicitante | `#000123 — Em atendimento` |
| `PEDIDO_INFO` | → Aguardando usuário / informações | solicitante | `#000123 — Precisamos de mais informações` |
| `RESOLVIDO` | → Resolvido | solicitante | `#000123 — Resolvido` |
| `REABERTO` | → Reaberto | atendente que resolveu | `#000123 — Reaberto pelo solicitante` |
| `DEMANDA_RECEBIDA` | `OnSuccess` do wizard | solicitante + patrocinador | `#000123 — Demanda recebida` |
| `APROVACAO_PENDENTE` | → Aguardando aprovação | gestores | `#000123 — Demanda aguardando sua aprovação` |
| `APROVADA` | → Em backlog | solicitante + patrocinador | `#000123 — Demanda aprovada` |
| `REPROVADA` | → Reprovado | solicitante + patrocinador | `#000123 — Demanda não aprovada` |
| `HOMOLOGACAO` | → Em homologação | solicitante | `#000123 — Pronto para o seu teste` |
| `AJUSTE` | → Ajustes solicitados | atendente | `#000123 — Ajustes solicitados` |
| `ENTREGUE` | → Entregue | solicitante + patrocinador | `#000123 — Entregue` |
| `FECHADO_AUTO` | varredura | solicitante | `#000123 — Fechado automaticamente` |
| `LEMBRETE` | varredura | solicitante | `#000123 — Aguardando o seu retorno` |
| `SLA_ESTOURADO` | varredura | atendente + gestores | `#000123 — Prazo de SLA estourado` |
| `PADRAO` | — | destinatário do payload | `#000123 — Atualização do chamado` |

**Um e-mail por transição de etapa, nunca por transição de status interno.**
`Em backlog → Em desenvolvimento` e `Ajustes solicitados → Em desenvolvimento`
não notificam ninguém: são movimentos internos de TI. Notificar cinco vezes num
dia é ensinar o usuário a não ler.

### 2.4 Os endereços fixos de cópia saem da tela e entram no catálogo

Hoje `ScreenServiceDeskForm` carrega isto embutido em dois `SendEmailV2`:

```powerfx
Cc: "douglas.nardelli@motiva.com.br; gilberto.claudino@motiva.com.br"
```

Duas cópias do mesmo dado numa tela, e mais uma em cada tela futura que notifique.
Entrando de TI ou saindo alguém, são N edições de YAML e um republish do app.
No catálogo do fluxo é um campo e uma versão de fluxo — sem tocar no app.

### 2.5 Anexos: por que `ABERTURA` só pode ser chamado de `OnSuccess`

O e-mail de abertura leva os anexos do chamado. Chamado do `OnSelect`, o item
ainda não existe na lista e o fluxo não tem de onde ler anexo nenhum. Chamado do
`OnSuccess`, o `SubmitForm` já gravou item e anexos, e o fluxo os lê com
*Obter anexos* + *Obter conteúdo do anexo* pelo `ID` do item.

É o motivo de o payload levar `desk_id` e o fluxo reabrir o item em vez de o app
mandar o conteúdo: mandar anexo dentro de parâmetro de texto não cabe, e
duplicaria em base64 no tráfego do app o que o SharePoint já tem.

---

## 3. `VarrerSlaChamados` — gatilho agendado

### 3.1 Configuração

- **Recorrência:** diária, 07:00, fuso `E. South America Standard Time`.
- Roda antes do horário comercial: o atendente encontra o alerta de SLA ao abrir
  o dia, não no meio dele.
- Variáveis no topo, todas as regras de prazo em um só lugar:

```
varDiasSemResposta   = 3    // lembrete
varDiasFechaEspera   = 5    // Aguardando usuário → Fechado
varDiasReabertura    = 7    // Resolvido → Fechado
```

### 3.2 As quatro varreduras

Cada uma é um *Obter itens* com filtro **OData na origem** — nunca traz a lista
inteira para filtrar no `Apply to each`. A mestre já passou de 1.100 itens.

| # | Filtro OData | Ação |
|---|---|---|
| 1 | `desk_data_limite ne null and desk_data_limite lt '@{utcNow()}'` e status aberto | `SLA_ESTOURADO` para o atendente e os gestores |
| 2 | `desk_status eq 'Aguardando usuário' or desk_status eq 'Aguardando informações'`, `Modified lt` hoje−3 | `LEMBRETE` para o solicitante |
| 3 | `desk_status eq 'Aguardando usuário'`, `Modified lt` hoje−5 | fecha: `desk_status = "Fechado"` + histórico + `FECHADO_AUTO` |
| 4 | `desk_status eq 'Resolvido'`, `Modified lt` hoje−7 | fecha: idem |

`ne null` é obrigatório na varredura 1. Sem ele, `desk_data_limite` em branco
compara como o começo dos tempos e **toda demanda sem prazo apareceria estourada
todos os dias** — a mesma coerção de `Blank() = 0`, agora num campo de data.

### 3.3 Quem fecha, escreve no histórico

As varreduras 3 e 4 movem status. Toda transição de status grava
`tb_chamadoHistorico` — inclusive as do fluxo:

| Coluna | Valor |
|---|---|
| `id_fk_chamado` | `desk_id` do item |
| `status_de` | status atual |
| `status_para` | `Fechado` |
| `autor_email` | `sistema@airportnow` |
| `observacao` | `Fechado automaticamente após N dias sem retorno.` |

Sem isso a linha do tempo da tela de detalhe tem um buraco exatamente no evento
que o usuário mais vai questionar — o chamado dele fechou e nada explica por quê.
`autor_email` fixo e reconhecível é o que permite a tela pintar o evento como do
sistema em vez de atribuí-lo a uma pessoa.

### 3.4 Nenhuma varredura recalcula espelho

A varredura **lê** `desk_data_limite`, nunca o preenche. Espelho grava junto com
a origem, no mesmo `Patch` — espelho que depende de fluxo posterior passa metade
do tempo desatualizado. O prazo é calculado na abertura, pelo app.

---

## 4. `desk_data_limite` — cálculo no app, em horas úteis

`nfCategorias.SlaResposta` e `.SlaSolucao` são **horas úteis**. Jornada
08:00–18:00, segunda a sexta: 10 horas úteis por dia.

Vai no `OnSuccess` da abertura, junto com os outros espelhos:

```powerfx
With(
    {
        locSla: LookUp(nfCategorias; Chave = varDeskCategoriaChave).SlaSolucao;
        locHoje: DateValue(Text(Now(); "dd/mm/yyyy"))
    };
    If(
        Coalesce(locSla; 0) = 0;
        Blank();                                  // demanda: previsão, não prazo
        With(
            {
                // dia-base: hoje, ou o dia seguinte se a jornada já encerrou
                locBase: If(Hour(Now()) >= 18; DateAdd(locHoje; 1; TimeUnit.Days); locHoje)
            };
            With(
                {
                    // rola sábado (+2) e domingo (+1) para a segunda
                    locDia: DateAdd(
                        locBase;
                        Switch(Weekday(locBase; StartOfWeek.Monday); 6; 2; 7; 1; 0);
                        TimeUnit.Days
                    )
                };
                With(
                    {
                        // início efetivo: agora, se estamos dentro da jornada de hoje
                        locIni: If(
                            locDia = locHoje And Hour(Now()) >= 8;
                            Now();
                            DateAdd(locDia; 8; TimeUnit.Hours)
                        )
                    };
                    With(
                        {
                            locRestaHoje: DateDiff(
                                locIni;
                                DateAdd(DateValue(Text(locIni; "dd/mm/yyyy")); 18; TimeUnit.Hours);
                                TimeUnit.Minutes
                            ) / 60
                        };
                        If(
                            locSla <= locRestaHoje;
                            DateAdd(locIni; locSla * 60; TimeUnit.Minutes);
                            With(
                                {locFalta: locSla - locRestaHoje};
                                With(
                                    {
                                        locDias: RoundDown(locFalta / 10; 0) + 1;
                                        locResto: Mod(locFalta; 10)
                                    };
                                    DateAdd(
                                        DateAdd(
                                            DateValue(Text(locIni; "dd/mm/yyyy"));
                                            locDias + 2 * RoundDown(
                                                (Weekday(locIni; StartOfWeek.Monday) - 1 + locDias) / 5;
                                                0
                                            );
                                            TimeUnit.Days
                                        );
                                        (8 + locResto) * 60;
                                        TimeUnit.Minutes
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )
)
```

### Por que a normalização do início tem três passos

A primeira versão desta fórmula testava `Weekday > 5` e depois `Hour >= 18` como
ramos irmãos de um mesmo `If`. **Sexta-feira às 19:00 caía em sábado 08:00** — o
teste de fim de semana olhava para *hoje*, e o dia que precisava ser testado era
o *dia seguinte*, que a outra condição acabava de escolher.

Por isso os passos são encadeados, não paralelos: escolher o dia-base **primeiro**,
rolar o fim de semana **desse** dia depois. Casos conferidos:

| Agora | `locBase` | `locDia` | `locIni` |
|---|---|---|---|
| segunda 10:00 | segunda | segunda | agora (10:00) |
| segunda 07:00 | segunda | segunda | segunda 08:00 |
| sexta 17:00 | sexta | sexta | agora (17:00) |
| **sexta 19:00** | sábado | **segunda** | segunda 08:00 |
| sábado 10:00 | sábado | segunda | segunda 08:00 |
| domingo 20:00 | segunda | segunda | segunda 08:00 |

### Por que a soma de dias úteis é essa conta

`D + N + 2 × RoundDown((Weekday(D) − 1 + N) / 5)` — pular fim de semana somando
dois dias a cada semana atravessada. Conferido nos quatro casos que importam:

| `D` | `N` | Conta | Resultado | Certo? |
|---|---|---|---|---|
| segunda | 1 | `(0+1)/5 → 0` | terça | ✅ |
| sexta | 1 | `(4+1)/5 → 1` | segunda | ✅ |
| quinta | 2 | `(3+2)/5 → 1` | segunda | ✅ |
| segunda | 5 | `(0+5)/5 → 1` | segunda seguinte | ✅ |

### Limite conhecido: feriado não é considerado

Não existe lista de feriados no projeto, e inventar uma para isto seria criar a
quinta lista do módulo por causa de um campo. O prazo pode cair num feriado
nacional e a varredura vai acusar estouro um dia antes do justo.

Se isso incomodar na operação, o conserto é uma lista `tb_feriado` de uma coluna
e um `CountRows(Filter(...))` somado a `locDias` — **não** é mexer nesta fórmula.
Registrado aqui para a decisão ser tomada com o custo na mesa, não descoberta
depois pelo atendente.

---

## 5. O que muda no app

| Tela | Mudança |
|---|---|
| `ScreenServiceDeskForm` | os dois `Office365Outlook.SendEmailV2` inline saem; entram `NotificarChamado.Run("ABERTURA§...")` e `("RESET_OK§...")`. `desk_data_limite` passa a ser gravado |
| `ScreenChamadoDetalhe` | cada transição chama o fluxo **depois** de gravar `tb_chamadoHistorico`, dentro do mesmo `IfError` |
| `ScreenNovoModuloWizard` | `DEMANDA_RECEBIDA` no `OnSuccess`, com `patrocinador_email` no campo `cc` |
| `frmServiceDesk` | idem detalhe, para as transições feitas da fila |

Ordem de corte, e ela importa: **construir os dois fluxos, testar com um chamado
de mentira, e só então tirar o `SendEmailV2` da tela de abertura.** Trocar o envio
antes de o fluxo estar provado deixa a abertura de chamado — a única coisa do
módulo que já está em produção — sem nenhum aviso ao usuário.

---

## 6. Checklist antes de publicar os fluxos

- [ ] `Responder ao Power App` é a **primeira** ação do `NotificarChamado`.
- [ ] Um só parâmetro no gatilho, e o `split` com padding de 5 `§`.
- [ ] O app remove `§` de todo texto do usuário antes de montar o payload.
- [ ] `coalesce` para a chave `PADRAO` em toda leitura do catálogo.
- [ ] Todo *Obter itens* tem filtro OData na origem e `Obter tudo` desligado.
- [ ] `desk_data_limite ne null` na varredura de SLA.
- [ ] As varreduras que fecham chamado gravam `tb_chamadoHistorico`.
- [ ] `retryPolicy` exponencial em todo envio de e-mail.
- [ ] `ABERTURA` e `DEMANDA_RECEBIDA` chamados de `OnSuccess`, nunca de `OnSelect`.
- [ ] Nenhum endereço de e-mail fixo restou em YAML de tela.
- [ ] Fluxos publicados na **mesma solução gerenciada**, com a versão
      incrementada — nunca importados como pacote novo, que cria `WorkflowId`
      novo e obriga a reapontar o app.
