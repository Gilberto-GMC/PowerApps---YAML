# Auditoria — Airport Now · Resposta à Emergência · Atendimento Pré-hospitalar (APH)

> Esta auditoria documenta o export de 18/09/2026. A base atual do aplicativo
> é a exportação de 19/10/2026 descrita em `BASE_ATUAL.md`. Os caminhos
> `msapp/` e `extracted/` abaixo agora apontam para a base atual; para rever
> a versão auditada, use o pacote de 18/09/2026 ou o histórico do Git.

Data: 2026-09-18. Origem: `AirportNow-RespostaàEmergência_20260918135434.zip`, extraído em `extracted/` (pacote) e `msapp/` (conteúdo do .msapp). Caminhos relativos a `REA/msapp/Src/`, salvo indicação. As linhas referem-se ao export original e mudam depois de qualquer entrega colada e reexportada.

**Status:** as decisões de negócio estão no §5. O Nível 1, a cobrança e a garantia do registro foram gerados e verificados em `out/ScreenAPH.pa.yaml` (§6), mas ainda não foram colados no Studio.

Escopo do módulo:

- a tela `ScreenAPH.pa.yaml`, com 5.817 linhas, 287 controles e o item 95 do menu em `App.pa.yaml:392`;
- a lista `tbl_atendimentoPreHospitalar`, com 9 colunas de data/hora;
- o fluxo `Criar - HTML` (`extracted/Microsoft.Flow/flows/ce070a73-…`), usado pelo botão "Relatório";
- a tabela Excel `Cessionarios`, que alimenta o campo empresa/CNPJ.

O fluxo `Exportar_servicos_APH` existe na solução antiga (`MigracaoAIRPORTNOW_src/`), mas nenhuma tela deste app o chama.

## 0. Resumo executivo

1. **A sequência de horários não é validada de verdade.** O Salvar confere só se hora e minuto estão vazios (`ScreenAPH:5128`). A ordem é "controlada" filtrando as opções da lista de cada campo pelo campo anterior, com folga de **−1 hora**. Com essa folga, 13:55 depois de 14:50 é aceito. A regra também esconde "00" depois da meia-noite e troca as opções debaixo do usuário quando ele corrige um horário anterior.
2. **Tudo parece erro, e o erro real não diz onde está.** Os 27 controles de data/hora têm `BorderColor: =RGBA(255, 0, 0, 1)` fixo. A única mensagem é "Erro Verifique se todos os horários obrigatórios foram preenchidos corretamente." (`:5199`), sem dizer qual campo.
3. **O formulário é desenhado para ser preenchido depois do atendimento.** `STATUS` é sempre "Finalizado" (`:4914`, oculto), e todos os horários são exigidos no Salvar. Os 9 horários são transcritos de memória ou do papel. Essa é a causa estrutural dos horários errados.
4. **Cobrança com três defeitos.**
   - O preço usa o aeroporto de **quem está logado** (`varAeroUser = "CURITIBA"`, `:1043`), não o do registro.
   - O valor só é gravado na **criação** (`OnSuccess`, `:1178`). Editar a categoria, o local ou a ambulância não recalcula.
   - A tabela de preços está dentro do app (100 / 150 / 523,25 / 2.500).

   A isenção depende de ID de usuário fixo ("30" e "505", `:884`) e não registra motivo, autor nem data.
5. **O campo empresa força dado errado.** Ele é obrigatório para toda categoria exceto VISITANTE, mas só lista cessionários ativos (`:2835`). Ao editar, o campo aparece vazio mesmo com valor gravado (`:2880`).
6. **Dado sensível exposto.** Nome do paciente e diagnóstico provável ficam:
   - na lista, pesquisáveis na galeria;
   - em arquivos HTML que o botão "Relatório" deixa na biblioteca `Exportar pdf`, que nunca são apagados.
7. **Um alerta de tempo-resposta está pronto e desligado.** `Container39` (`:5533`) monta um aviso de tempos suspeitos. O gatilho está comentado no Salvar (`:5205-5333`).

## 1. Linha de base

| Item | Valor |
|---|---|
| Controles na tela | 287, sem contar os 18 `DropDownDataField` (App Checker: `app-ScreenHasManyControls`) |
| Campos no formulário | 33 `TypedDataCard`, dos quais 9 são `DateTimeEdit` |
| Controles só para horários | 27: 9 `DatePicker@0.0.46`, 9 `DropDown` de hora (25 opções) e 9 de minuto (61 opções) |
| Colunas de data/hora | todas `date-time` no SharePoint, ou seja, o armazenamento está certo e o problema é a entrada |
| Mesmo padrão hora/minuto em outras telas do REA | `ScreenCheckListREA` (38 refs), `ScreenCheckListVeiculoCCI` (32), `ScreenCheckListERSCI`, `ScreenCheckListEpiEpr` e `ScreenCheckListSme` (24 cada), `ScreenAcionamentosPlemPrai` e `ScreenOcorrenciasNaoAeronauticas` (16 cada), `ScreenTesteContatos` (5) |
| App Checker na tela | 13 `acc-TabIndex…`, 11 `acc-FocusBorder…`, 2 `app-CollectingReadOnlyTable`, 2 variáveis sem uso (`CurrentItem`, `var_cnpjAPH`) |

## 2. Sequência de horários

### 2.1 Os 9 horários, na ordem em que aparecem

| # (Y) | Rótulo na tela | Coluna | Nome interno | Quando aparece | Linha |
|---|---|---|---|---|---|
| 7 | HORÁRIO DE ACIONAMENTO EM VOO | idem | `HOR_x00c1_RIODEACIONAMENTOEMVOO` | em voo | 1623 |
| 8 | HORÁRIO DO ACIONAMENTO DA EQUIPE APH | HORÁRIO DO ACIONAMENTO | `HOR_x00c1_RIODOACIONAMENTO` | sempre | 1858 |
| 9 | HORÁRIO DE ABERTURA DE PORTA DA AERONAVE | HORÁRIO DE CALÇO | `HOR_x00c1_RIODECAL_x00c7_O` | em voo | 2117 |
| 10 | HORÁRIO DE INÍCIO DO ATENDIMENTO | HORÁRIO DO ATENDIMENTO | `DataehoradoAcionamento` | sempre | 2374 |
| 22 | HORÁRIO DE ACIONAMENTO DA AMBULÂNCIA | idem | `HOR_x00c1_RIODEACIONAMENTODAAMBU` | remoção | 3434 |
| 23 | HORÁRIO DE CHEGADA NO LOCAL DA OCORRÊNCIA | HORÁRIO DA CHEGADA DA AMBULÂNCIA | `Dataehoradachegada` | remoção | 3681 |
| 24 | HORÁRIO DE SAÍDA DA AMBULÂNCIA DO AEROPORTO | HORÁRIO DA SAÍDA DA AMBULÂNCIA | `Dataehoradoatendimento` | remoção | 3929 |
| 25 | HORÁRIO DO RETORNO DA AMBULÂNCIA | idem | `HOR_x00c1_RIODORETORNODAAMBUL_x0` | remoção com ambulância interna | 4177 |
| 28 | HORÁRIO DO ENCERRAMENTO DO ATENDIMENTO | idem | `Dataehoradoencerramentodoatendim` | sempre | 4582 |

Rótulo da tela, nome da coluna e rótulo do relatório (`HtmlText3`, `:5522`) divergem em 4 dos 9 campos. O nome interno de 3 colunas não corresponde ao conteúdo:

- `DataehoradoAcionamento` guarda o **início do atendimento**;
- `Dataehoradoatendimento` guarda a **saída da ambulância**;
- `Dataehoradachegada` guarda a chegada **da ambulância**.

Quem monta relatório ou Power BI pelo nome interno pega a coluna errada.

### 2.2 Como cada campo funciona hoje

Os 9 campos repetem o mesmo desenho:

- `Update = DateTime(Year(data), Month(data), Day(data), Value(Hora.Selected.Value), Value(Minuto.Selected.Value), Second(data))`;
- a data de todos, exceto o primeiro e o calço, nasce como `Coalesce(Parent.Default, DateValue12_1.SelectedDate)`, isto é, a data do acionamento;
- a lista de horas de cada campo é filtrada por `Value(Value) >= Value(<hora do campo anterior>) - 1` quando as datas são iguais;
- a lista de minutos é filtrada por `>= <minuto anterior>` só quando a hora é igual à do campo anterior.

### 2.3 Defeitos

| # | Defeito | Evidência | Efeito no usuário |
|---|---|---|---|
| H1 | **Ordem não validada no Salvar**; o filtro de lista tem folga de −1 h e só compara minutos quando a hora é igual | `SubmitButton1_1:5128` só testa `IsBlank`; filtros em `HourValue*`/`MinuteValue*` | Ambulância acionada 14:50 e chegada 13:55 é gravado sem aviso: a lista de hora oferece ≥ 13 e, como 13 ≠ 14, os minutos não são filtrados |
| H2 | **Opções mudam por baixo do usuário.** Cada lista depende do campo anterior, e corrigir um horário de cima muda as opções de todos os de baixo | `Items` de 16 dos 18 dropdowns | O valor escolhido pode deixar de existir na lista; o usuário não entende por que "sumiu" a hora |
| H3 | **Meia-noite sem saída visível.** A data dos campos seguintes nasce igual à do acionamento, e o filtro só vale com datas iguais | `DateValue1_2`, `DateValue14_1`, `DateValue2_10`, `DateValue3_6`, `DateValue17`, `DateValue4_2` | Acionamento 23:50, chegada 00:05: a lista de hora só oferece 22 e 23 até o usuário descobrir que tem de mudar a data daquele campo. Nada na tela explica |
| H4 | **Dependência invertida no bloco "em voo".** O acionamento da equipe (Y8) é filtrado pela abertura de porta (Y9), que aparece **abaixo** dele; a abertura de porta é filtrada pelo acionamento em voo (Y7) | `HourValue12_1`/`MinuteValue12_1` (1858), `HourValue15_1` (2117) | A regra embutida é "em voo → abertura de porta → acionamento da equipe", mas a tela mostra o acionamento antes da porta. Quem preenche de cima para baixo vê o acionamento mudar depois de preencher a porta |
| H5 | **Data da abertura de porta presa à data do "em voo"** | `DateValue15_1.SelectedDate: =DateValue16_1.SelectedDate` (`:2151`), sem ler o valor gravado | Ao editar, a data gravada é substituída pela do "em voo" |
| H6 | **Borda vermelha fixa** nos 27 controles | `BorderColor: =RGBA(255, 0, 0, 1)` ×27 | Vermelho vira decoração; erro de verdade fica igual a campo certo (é o que aparece no print) |
| H7 | **Mensagem genérica** | `:5199` | O usuário procura o erro em até 9 blocos de 3 controles |
| H8 | **27 controles para 9 horários.** 7 datas repetidas, listas de 25 e 61 opções. O default de hora/minuto em registro novo é `[0]` (número) contra itens de texto; a abertura de porta usa `[00]` e `Blank()` | todos os `DefaultSelectedItems` | Muitos cliques e rolagem; "00" é a primeira opção real da lista, fácil de clicar sem querer. Vale conferir o registro de 18/09/2026 00:00 que aparece no topo da galeria do print |
| H9 | **Hora vazia vira 00:00 silenciosamente.** `Value(Blank())` é 0 | `Update` dos 9 cards | Hoje só o Salvar impede isso. Qualquer caminho que chame `SubmitForm` sem passar por ele grava 00:00, inclusive o botão "Confirmar" do alerta desligado (`:5813`) |
| H10 | **Trocar o tipo de ambulância apaga** as horas e os minutos dos 4 horários da ambulância | `DataCardValueRemocao_1.OnChange` (`:3382`) | Retrabalho e horários digitados de novo às pressas |
| H11 | **Alerta de plausibilidade pronto e desligado**, com limites fixos (APH ≤ 2 min, ambulância ≤ 10 min) e emoji | `Container39:5533`, `HtmlText4`; gatilho comentado em `:5205-5333` | Nenhuma checagem de tempo improvável |
| H12 | **Registro só depois do fato.** `STATUS` é sempre "Finalizado" e todos os horários são exigidos para salvar | `STATUS_DataCard1_1:4914` | O operador reconstrói até 9 horários de memória. No print, chegada 14:31, saída 14:32 e retorno 14:33 são aceitos sem aviso: uma ida e volta de 1 minuto |

## 3. Demais achados

### 3.1 Cobrança e protocolo

| # | Achado | Evidência |
|---|---|---|
| C1 | Preço do posto médico usa `varAeroUser = "CURITIBA"`, o aeroporto do usuário logado. Perfil não-Base escolhe outro aeroporto no filtro e o preço sai pelo aeroporto dele | `ValueAtendimento_1:1034` |
| C2 | `VALOR_ATENDIMENTO`/`VALOR_REMOÇÃO` só são gravados quando `newMode`. Editar categoria, local ou ambulância mantém o valor antigo | `FormAphEdt.OnSuccess:1178` |
| C3 | Tabela de preços dentro do app, sem vigência: 100, 150 (CWB posto médico), 523,25 (básica) e 2.500 (UTI). Mudar preço exige republicar | `:1034-1101` |
| C4 | "Isentar" visível só para `varIdUser` "30" ou "505"; grava `ISENTO` e zera os valores sem motivo, autor nem data; sem aviso de sucesso ou falha | `EditButton1_3:872`, `ConfirmDeleteButton1_2:5479` |
| C5 | Moeda exibida como `$` em vez de `R$` (rótulos e relatório) | `:1030`, `HtmlText3` |
| C6 | O protocolo usa `varIATAUser` (usuário), não o IATA do registro. É gravado num segundo `Patch` depois do `SubmitForm`, sem checar erro; se esse `Patch` falhar, o registro fica sem protocolo | `:1188` |
| C7 | O campo PROTOCOLO nunca aparece no formulário: `Visible: =var_formTitle = "Detalhes"`, mas nesta tela `var_formTitle` só recebe "Editar" | `:1394`, `:691` |

### 3.2 Formulário

| # | Achado | Evidência |
|---|---|---|
| F1 | Empresa obrigatória para toda categoria exceto VISITANTE, mas a lista só tem cessionários ativos. Passageiro, tripulante e órgão público precisam escolher algum cessionário | `INFORME A EMPRESA…:2835` |
| F2 | Ao editar ou visualizar, o combo de empresa aparece vazio: `DefaultSelectedItems: =[Parent.Default]` é texto e os itens são registros. O valor gravado sobrevive pelo `Coalesce` do campo oculto, mas o usuário vê em branco e escolhe de novo | `ComboBoxRazaoSocial_1:2880` |
| F3 | `colEmpresasAtivas` só é carregada no `OnVisible`. Trocar o aeroporto no filtro não recarrega, e a lista mostra empresas do aeroporto anterior. `Cessionarios` é Excel: filtro não delegável, limitado ao teto de linhas | `ScreenAPH.OnVisible`, `DataSources.json` |
| F4 | Depois de salvar uma edição, `editMode` vira falso e o Salvar some, mas o formulário continua em modo de edição (não há `ViewForm`). Os campos ficam editáveis sem botão de salvar | `OnSuccess:1201-1207` |
| F5 | Marcar "EM VOO" e depois trocar "ACIONADO POR" para CHEGADA ESPONTÂNEA esconde o toggle, mas ele continua ligado. Número do voo e os 2 horários de voo continuam visíveis e obrigatórios | `EM VOO_DataCard1_1`, `NÚMERO DO VOO_DataCard1_1` |
| F6 | Anexos (ficha de atendimento) estão ocultos (`Visible: =false`) | `Anexos_DataCard1_1:4432` |
| F7 | "ATENDIDO POR" é texto livre (coluna com erro de digitação `ANTENDIDOPOR`). O mesmo profissional pode ser escrito de vários jeitos, o que atrapalha contagens por profissional | `:2980` |

### 3.3 Lista e filtros

| # | Achado | Evidência |
|---|---|---|
| L1 | Três filtros sem rótulo (tipo, categoria, ambulância), só com tooltip; a do tipo diz "Remoção". Os `Default` foram copiados de outros controles (`varAeroUser` no tipo e na ambulância, `varBlocoUser` na categoria) | `cmbtip:276`, `cmbCat:313`, `cmbAmb:355` |
| L2 | O filtro de categoria usa "COLABORADOR CCR"/"TERCEIRO CCR", e a ajuda do campo fala em "COLABORADOR MOTIVA"/"TERCEIRO MOTIVA". Se as opções da lista foram renomeadas, o filtro nunca acha nada | `:337-343`, `InfoButtonCanvas1_15` |
| L3 | A data inicial do filtro é montada como texto, `DateValue("01/" & Text(Today(), "mm/yyyy"))`, e depende do idioma do navegador | `dtpBuscarIni:449` |
| L4 | `Excluir` aparece mesmo sem registro selecionado, não tem restrição de perfil e falha em silêncio (sem `Notify` quando `Errors` não está vazio) | `DeleteButton1_1:846`, `ConfirmDeleteButton1_1:5388` |

### 3.4 Relatório (botão "Relatório")

| # | Achado | Evidência |
|---|---|---|
| R1 | O nome do arquivo é `"APH-" & varIATAUser & "-" & Now()`, com `Now()` sem formato (contém `/` e `:`, que o SharePoint não aceita em nome de arquivo). Confirmar se o botão funciona hoje | `EditButton1_2:886`, fluxo `Criar - HTML` |
| R2 | Não há guarda se o fluxo falhar (faz `Launch` de vazio) nem trava contra duplo clique | `:895-912` |
| R3 | O PDF sai de um truque com a URL da miniatura (`Substitute(Miniatura.Large, "thumbnail", "pdf")`), comportamento não documentado | `:902-911` |
| R4 | O HTML com nome e diagnóstico do paciente fica em `Documentos Partilhados/Exportar pdf` e nunca é apagado | fluxo `Criar - HTML` |
| R5 | O relatório não mostra os intervalos de tempo e usa rótulos diferentes do formulário | `HtmlText3:5522` |

### 3.5 Privacidade

Nome do paciente e "motivo do atendimento (diagnóstico provável)" são dados de saúde. Hoje:

- ficam em lista pesquisável pela galeria do módulo;
- viram arquivos HTML permanentes na biblioteca `Exportar pdf`;
- quando se usa o fluxo antigo de exportação (`Exportar_servicos_APH`), saem por e-mail em planilha.

Vale revisar com a área de privacidade quem precisa ver esses campos e por quanto tempo.

## 4. Proposta para a sequência de horários

Três níveis. Cada um funciona sozinho e o seguinte aproveita o anterior. Nenhum exige mudar a lista do SharePoint.

### Nível 1: corrigir sem mudar o layout (mesmos controles e mesma posição)

1. **Tirar os filtros das listas** de hora e minuto (H2, H3, H4): lista completa sempre.
2. **Validar a ordem de verdade**:
   - uma fórmula monta os horários ativos (conforme em voo, remoção e tipo de ambulância) e compara cada par consecutivo;
   - cada campo com problema mostra no próprio `ErrorMessage` o texto "Está antes de *Acionamento da ambulância* (14:15)";
   - o Salvar lista os problemas pelo nome.
3. **Borda vermelha só no campo com problema** (H6).
4. **Meia-noite**: a data de cada campo nasce igual à do campo **anterior**, não à do acionamento. Quando o horário fica menor que o anterior, a mensagem sugere a data do dia seguinte.
5. **Ligar o alerta que já existe** (H11), com os limites definidos pela coordenação de APH e sem emoji. Ele passa a mostrar os intervalos calculados antes de gravar.
6. **Corrigir H5, H9 e H10**:
   - a data da abertura de porta passa a ler o valor gravado;
   - hora vazia bloqueia, em vez de virar 00;
   - trocar o tipo de ambulância não apaga horários.
7. **Rótulos numerados na ordem real**, iguais no formulário e no relatório:
   1. acionamento da equipe;
   2. início do atendimento;
   3. acionamento da ambulância;
   4. chegada da ambulância ao local;
   5. saída do aeroporto com o paciente;
   6. retorno ao aeroporto;
   7. encerramento.

### Nível 2: um campo por horário

- Troca data + hora + minuto por **um campo "HH:MM"** que aceita `1415`, `14:15` ou `14h15`, e um botão **"Agora"**.
- Uma **data da ocorrência** no topo. Os demais campos só mostram "+1 dia" quando passam da meia-noite.
- Ao lado de cada horário, o intervalo desde o anterior ("+9 min").
- No rodapé, os tempos-resposta:
  - equipe: acionamento → início;
  - ambulância: acionamento → chegada;
  - total.

Os 27 controles viram 9. Continua gravando nas mesmas 9 colunas `date-time`.

### Nível 3: registro em tempo real

- Status **"Em andamento"**: salva no acionamento, e cada marco é registrado com "Agora" no momento em que acontece.
- A validação completa roda só ao **finalizar**.
- Os horários passam a vir do relógio, não da memória.
- Depende de haver quem registre durante o atendimento (tablet/celular da equipe ou do COE).

### Ordem sugerida

1. Nível 1, junto com C1, C2 e C6, porque é onde erro vira valor cobrado errado.
2. F1–F5, L1–L4, R1–R2.
3. Nível 2.
4. Nível 3, se o processo permitir.

O mesmo padrão de hora/minuto aparece em outras 8 telas do app (seção 1). A correção do Nível 1 serve de modelo para elas.

## 5. Decisões de negócio (respondidas em 2026-09-18)

1. **Ordem no voo** (regra final, depois de dois complementos do usuário no mesmo dia): a **equipe e a ambulância podem ser acionadas antes ou depois da abertura de porta**. O que o app confere:

   | Horário | Tem de vir depois de |
   |---|---|
   | acionamento da equipe | notificação em voo |
   | abertura de porta | notificação em voo |
   | início do atendimento | abertura de porta **e** acionamento da equipe (as duas regras valem) |
   | acionamento da ambulância | notificação em voo (fora de voo: início do atendimento) |
   | chegada da ambulância | acionamento da ambulância |
   | saída da ambulância com o paciente | chegada da ambulância **e** início do atendimento |
   | retorno da ambulância | saída da ambulância |
   | encerramento | saída da ambulância (sem remoção: início do atendimento) |

   A primeira versão desta entrega seguia a ordem da tela (acionamento da equipe → abertura de porta), e o filtro antigo exigia o contrário; nenhuma das duas estava certa.

   Conferir a saída com o paciente contra o início do atendimento é consequência da regra: em voo a ambulância pode chegar antes de a porta abrir, mas o paciente não sai antes de ser atendido.
2. **Quando se preenche:** em geral depois do atendimento. Por isso o Nível 3 (tempo real) fica fora; o foco é validar bem o que é transcrito.
3. **Empresa/CNPJ:** para **cessionário comercial** (é quem paga), **passageiro** e **tripulante** (identificados pela companhia aérea, que tem CNPJ — correção do usuário em 2026-09-25). Nas demais categorias (colaborador, terceiro, órgão público e visitante) o campo não aparece e não é exigido.
   - A empresa vem do combo, que lista as concessões ativas do aeroporto na planilha `Cessionarios`, e o CNPJ é preenchido a partir dela (o campo é somente leitura). Para passageiro e tripulante, a companhia aérea precisa estar nessa planilha; senão não há como selecionar, e agora o campo é obrigatório.
4. **R$ 150:** só para o posto médico de Curitiba, pelo aeroporto do registro.
5. **Limites dos alertas:** o usuário delegou a decisão. Ficaram assim (em `LIMITES`, no gerador):

   | Alerta (pede confirmação, não bloqueia) | Limite |
   |---|---|
   | notificação em voo → abertura de porta | mais de 3 h |
   | acionamento da equipe → início do atendimento (em voo, a partir do que ocorreu por último: acionamento ou abertura de porta) | mais de 30 min |
   | acionamento da ambulância → chegada no local | mais de 60 min |
   | saída da ambulância → retorno (ida e volta) | menos de 10 min |
   | acionamento da equipe → encerramento | mais de 12 h |

   O alerta antigo (≤ 2 min para a equipe, ≤ 10 min para a ambulância) foi descartado: com o formulário preenchido depois, tempo curto costuma ser verdadeiro (posto médico, chegada espontânea); o erro típico é tempo longo demais (hora ou dia errado) ou ida e volta impossível.

## 6. Entrega de 2026-09-18

Arquivos:

| Arquivo | O que é |
|---|---|
| `out/ScreenAPH.pa.yaml` | a tela nova, pronta para colar (invariante; não converter para pt-BR) |
| `build/gerar_aph.py` | gera a tela a partir de `msapp/Src/ScreenAPH.pa.yaml`; só as 148 propriedades declaradas mudam |
| `build/verificar_aph.sh` | roda tudo: gerador 2× (hash igual), dicionário de propriedades, sintaxe, trava de layout, valores, tratamento de erro, variáveis de estado e a guarda de 00:00 |
| `build/propriedades_esperadas.json`, `out/_excecoes_layout.json` | lista revisada das mudanças; qualquer diferença reprova |

Resultado da verificação:

- 305 controles com a árvore idêntica: nenhum controle entrou nem saiu;
- 56 mudanças visuais declaradas e confirmadas;
- zero problemas de sintaxe;
- zero propriedades fora do dicionário do app;
- zero variáveis mortas ou presas na tela (o export tinha 3).

### 6.1 O que foi corrigido

| Achado | Correção |
|---|---|
| H1, H2, H4 | listas de hora e minuto completas, sem filtro. A ordem é validada no Salvar pelas regras do §5; em voo, equipe e ambulância podem ser acionadas antes ou depois da abertura de porta. Cada campo mostra a própria mensagem, e o Salvar lista os campos com problema pelo nome. As regras estão em `GRUPOS`, no gerador |
| H3 | a data de cada campo nasce igual à do campo anterior. A mensagem dá a dica "Se passou da meia-noite, mude a data deste campo" quando a diferença passa de 12 h |
| H5 | a data da abertura de porta lê o valor gravado e, sem ele, herda a do acionamento da equipe |
| H6 | borda vermelha só no campo com problema; nos demais, o azul dos outros campos do formulário |
| H7 | mensagens específicas: faltando, horário no futuro, fora de ordem e aeroporto não selecionado |
| H8, H9 | hora vazia não vira mais 00:00. O `Update` fica em branco e o campo acusa. Registro antigo sem o horário abre vazio, não com "00:00" (antes, editar e salvar fabricava o horário) |
| H10 | trocar o tipo de ambulância não apaga mais os horários |
| H11 | alerta de plausibilidade ligado, com os limites do §5 e sem emoji; botões "Ajustar" e "Salvar assim" |
| C1 | preço do posto médico pelo aeroporto do registro |
| C2 | valores recalculados também na edição, respeitando a isenção; protocolo gerado se estiver em branco |
| C5 | moeda como R$ nos rótulos e no relatório |
| C6 | protocolo com o IATA do registro. A segunda gravação é conferida (`IsError`) e avisa se falhar; salvar de novo corrige |
| F1, F2 | empresa/CNPJ aparecem e são exigidos para cessionário comercial, passageiro e tripulante (§5); ao editar, a empresa gravada aparece selecionada |
| F3 | lista de empresas recarregada ao trocar o aeroporto. A consulta ao Excel leva uma condição só; o filtro de concessão ativa fica em memória, no combo (ver §6.5) |
| F4 | depois de salvar uma edição, o formulário volta para visualização (`ViewForm`) |
| F5 | "em voo" escondido por chegada espontânea deixa de valer e esconde o número e os horários do voo |
| L1, L3 | defaults copiados de outro controle removidos; tooltips corrigidos; data inicial do filtro por `Date(Year, Month, 1)`, sem depender do idioma |
| L4 | Editar e Excluir só aparecem com registro selecionado; excluir e isentar avisam sucesso ou falha |
| R1, R2 | nome do arquivo do relatório sem `/` e `:`, trava contra duplo clique e aviso se o fluxo falhar ou o PDF ainda não existir |
| Garantia do registro | trava contra duplo clique no Salvar, que se solta sozinha em 30 s e é liberada em `OnSuccess`/`OnFailure`. `OnFailure` mostra o erro real (`Self.Error`). Falha não limpa o formulário. Registro novo sem aeroporto é bloqueado |
| Performance | 16 listas deixaram de ser recalculadas a cada mudança de hora. O alerta oculto (`HtmlText4`), que antes recalculava a cada clique em hora ou minuto, depende agora só da variável do alerta. O filtro de data da galeria compara data/hora direto, sem converter texto em cada linha. Na edição, a segunda gravação só acontece se protocolo ou valor mudaram |

### 6.2 Fora desta entrega

- **C3:** tabela de preços em lista com vigência. Exige lista nova.
- **C4:** registrar motivo, autor e data da isenção. Exige colunas novas.
- **C7:** mostrar o protocolo no formulário. Muda o layout.
- **F6:** anexos ocultos. Confirmar se é intencional.
- **F7:** "atendido por" como lista em vez de texto livre.
- **L2:** CCR × MOTIVA nas opções de categoria. Conferir na lista.
- **R3, R4:** fluxo `Criar - HTML`, com o PDF pela URL da miniatura e os HTML que nunca são apagados.
- Restrição de quem pode excluir.
- Níveis 2 e 3 do §4.
- O mesmo trio data/hora/minuto nas outras 8 telas do app.

### 6.3 Como colar

1. O zip do export (`AirportNow-RespostaàEmergência_20260918135434.zip`) é o backup: a tela antiga volta dele.
2. No Studio, **exclua a `ScreenAPH`** atual. Renomear não basta, porque nome de controle é único no app inteiro e a colagem daria PA2110 em massa.
3. Cole `out/ScreenAPH.pa.yaml` pela exibição de código. Confirme que a tela se chama exatamente `ScreenAPH`, porque é o nome que o menu (item 95) usa.
4. Publique só depois dos testes abaixo.
5. Se a tela for alterada no Studio depois, envie o export novo antes da próxima rodada: o gerador parte do export, e editar à mão o arquivo gerado se perde.

### 6.4 Testes de aceite

1. Registro novo sem remoção, sem o encerramento: o Salvar avisa "Preencha data, hora e minuto de: encerramento." e o campo mostra a mensagem.
2. Acionamento 14:20 e início 14:10: o início fica com borda vermelha e "Está antes do horário de acionamento da equipe (…14:20)". O Salvar é bloqueado.
3. Acionamento 23:50 e início 00:05 na mesma data: aparece a dica da meia-noite. Ao mudar a data do início para o dia seguinte, a mensagem some e as datas seguintes acompanham.
4. Remoção interna com saída 14:32 e retorno 14:33: abre o alerta de ida e volta. "Ajustar" volta ao formulário; "Salvar assim" grava.
5. Editar um registro antigo sem encerramento: o campo abre vazio, não 00:00, e o Salvar pede o horário.
6. Cessionário comercial, posto médico: Curitiba sai R$ 150 e outro aeroporto R$ 100. Editar e trocar o tipo de ambulância atualiza o valor (reabrir e conferir).
7. Passageiro e tripulante: empresa e CNPJ aparecem, são exigidos e a companhia aérea é selecionável no combo. Colaborador, terceiro e órgão público: os dois campos não aparecem.
8. Duplo clique em Salvar num registro novo: um registro só.
9. Relatório: o PDF abre.
10. Sem registro selecionado, Editar e Excluir não aparecem.
11. Em voo com remoção:
    - equipe e ambulância antes da porta: notificação 13:00, equipe 13:02, ambulância 13:05, chegada da ambulância 13:15, porta 13:40, início 13:42. Grava sem aviso de ordem;
    - equipe e ambulância depois da porta: notificação 13:00, porta 13:40, equipe 13:45, ambulância 13:47, início 13:50. Grava sem aviso de ordem;
    - no segundo caso, com o início às 13:43 (antes do acionamento): o início é barrado com "Está antes do horário de acionamento da equipe";
    - com a porta às 12:50 (antes da notificação): a abertura de porta é barrada;
    - com a saída às 13:30 (antes do início): a saída é barrada.
12. Trocar o aeroporto no filtro, num perfil que pode trocar: a lista de empresas passa a ser a do aeroporto novo, sem erro de rede.

### 6.5 Correção depois da primeira colagem (2026-09-18)

O Studio acusou, no `OnVisible`: "[Cessionarios] Cláusula de filtro inválida: operação sem suporte".

A causa foi a segunda condição (`SituacaoDaConcessao = "Ativa"`) acrescentada à consulta a `Cessionarios`, que é uma tabela do **Excel Online**. Esse conector só aceita uma condição por consulta.

Correção feita no gerador: a consulta volta a ter uma condição só, como no original, e "Ativa" continua filtrado em memória no combo. Duas formas de aplicar:

- **Tela já colada:** trocar só o `OnVisible` da `ScreenAPH` e o `OnChange` do `cmbAeroporto` pelas versões pt-BR de `out/ScreenAPH_correcao_Cessionarios_ptBR.txt`, que são para a barra de fórmulas.
- **Colando de novo:** usar `out/ScreenAPH.pa.yaml`, que já está corrigido.

A verificação `build/checar_excel.py` (no `verificar_aph.sh`) impede que isso volte.

### 6.6 Regra da abertura de porta (2026-09-18, depois da colagem)

Equipe e ambulância podem ser acionadas antes ou depois da abertura de porta (§5). Mudaram quatro propriedades em relação à tela colada:

- `DateValue15_1.SelectedDate`: a data da porta nasce igual à da notificação;
- `ErrorMessage108_2.Text` e `ErrorMessage8_2.Text`: mensagens da porta e do início;
- `SubmitButton1_1.OnSelect`: ordem e alerta de tempo de resposta.

Formas de aplicar:

- **Colar a tela inteira de novo (recomendado):** `out/ScreenAPH.pa.yaml`, que já traz também a correção do §6.5. O Salvar tem 11 mil caracteres; colar à mão na barra de fórmulas é onde mais se erra.
- **Só as quatro fórmulas:** as versões pt-BR, para a barra de fórmulas, estão em `out/ScreenAPH_correcao_porta_ptBR.txt`.

### 6.7 Empresa e CNPJ por categoria (2026-09-25)

Passageiro e tripulante voltaram a exigir empresa e CNPJ, porque são identificados pela companhia aérea (§5). Mudaram quatro propriedades: `Required` e `Visible` dos cartões `INFORME A EMPRESA/RAZÃO SOCIAL_DataCard1_2` e `CNPJ_DataCard1_2`, todas com a mesma fórmula. As versões pt-BR estão em `out/ScreenAPH_correcao_empresa_ptBR.txt`; `out/ScreenAPH.pa.yaml` já está atualizado.

Os literais das categorias (`CESSIONARIO COMERCIAL`, `PASSAGEIRO`, `TRIPULANTE`) têm de ser idênticos aos da coluna CATEGORIA. É o mesmo risco do achado L2, de CCR × MOTIVA: se as opções forem renomeadas na lista, a regra para de casar.
