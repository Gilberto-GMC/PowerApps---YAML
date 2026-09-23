# Auditoria — Airport Now · Inspeção de Pista (app mobile)

Data: 2026-09-17. Origem: `AirportNow-InspeçãodePista_20260916202747.zip` (publicado em 14/09/2026, solução "Grupo CCR (default)"), extraído em `extracted/` (solução) e `msapp/` (conteúdo do .msapp). Caminhos abaixo relativos a `msapp/Src/`; linhas do export original.

Contexto: é o app que o tile "Inspeção de pista" do Airport Now abre fora do Windows (o app principal `Inspeções` lança o app `90a784ea…` nesse caso; o pacote não traz o GUID do ambiente, mas o nome e a função batem). Ou seja: **é o app que o inspetor usa na pista, no tablet**. O app principal, auditado em `../Inspeções/AUDITORIA.md`, cobre o mesmo módulo no Windows e o que vem depois da captura (detalhe, fauna, normalização, relatórios).

## 0. Resumo executivo

1. **A inspeção inteira vive só na memória até o fim.** Cabeçalho, apontamentos (com as 3 fotos e a posição GPS) e áudios ficam em 3 coleções (`col_inspPista_mob_temp`, `col_inspPistaItens_mob_temp`, `col_anotacaoAudio_mob`) e só vão para o SharePoint no botão final. Não há `SaveData`: se o app fechar, o tablet matar o processo, a bateria acabar ou o usuário voltar ao hub, **tudo o que foi apontado em campo se perde**.
2. **O botão "Finalizar" apaga o buffer mesmo se o envio falhou** (`ButtonCanvas3_5`, linha 4276). Sem conexão, o botão de envio fica desabilitado; o usuário vê "Não Conectado", toca em "Finalizar" e as coleções são limpas. Com conexão instável, o envio para no meio (sem `IfError`) e o "Finalizar" apaga o resto.
3. **O envio não é idempotente.** Tocar de novo, ou reenviar depois de falha parcial, duplica cabeçalho e itens: nada consulta o `hash` do cabeçalho nem o `Hash` do item antes de criar. O `Hash` do item ainda é gerado com a mesma fórmula quebrada do app principal (unicidade praticamente só no segundo).
4. **"Normalizar" não grava nada.** O `Patch` na lista está comentado; o botão só tira o item da tela e mostra "foi normalizado com sucesso" (linha 3677). No próximo acesso o item reaparece como não conforme.
5. **"Continuar" uma inspeção em andamento corrompe dados**: não carrega o `var_hash` da inspeção e põe os itens que já estão no servidor dentro do buffer; no envio, esses itens são recriados como novos (duplicados) sob um cabeçalho novo.
6. **Contadores e lista de não conformidades provavelmente vazios.** O `App.OnStart` carrega as não conformidades do ano com um filtro não delegável (`Year(Criado)`), sem ordenação, e o app tem limite de **500** linhas: só as 500 primeiras linhas da lista de itens (as mais antigas, de todos os aeroportos) são avaliadas.
7. **O passo "Item" depende de rede a cada toque**: `Gallery13_12` consulta `tbl_inspMenu` direto no SharePoint, ignorando a coleção `col_inspPistaMenu` que a tela já carregou. Offline, o fluxo trava no passo 2.
8. **Formato de protocolo de item diferente do app principal**: aqui `IATA-INSP-PISTA-ITEM-<ID>` (correto), no Windows `IATA-INSP_PISTA_ITEM-<maior ID da lista>` (errado e repetido no lote). A mesma lista tem dois formatos.
9. **Tela de login morta com um problema de segurança do ecossistema**: `ScreenLogin` só é alcançável por um ícone invisível, mas mostra o esquema de senha do hub — a senha pode ser remontada a partir do valor gravado na lista `User`, que todo app lê.
10. **O lado bom**: é pequeno (2 telas, 269 controles, 465 KB), usa só 3 listas para escrever, sem fluxos e sem anexos nativos, e **já tem o desenho de buffer local** — é o melhor lugar para pilotar o motor offline do plano.

## 1. Linha de base

| Métrica | Valor |
|---|---|
| Telas | `frmInspPistaMob` (tela inicial, 4.423 linhas) e `ScreenLogin` (383 linhas, só alcançável por ícone invisível) |
| Controles | 269 (galerias 7, formulário 1 com 17 DataCards, AddMedia 3, Microphone 1) |
| Pacote | 465 KB; 5 imagens (72 KB), 2 mídias sem uso (`LogoAN`, `CCRAeroportosImg`) |
| Conexões | 1 (SharePoint, site AIRPORTNOW). **Sem fluxos**, sem Office 365 |
| Listas | `User`, `tbl_Modulos`, `tbl_inspMenu`, `'7.4-tbl_InspPista'`, `'7.4.1-tbl_InspPistaItens'`, `tbl_inspPistaAnotacao` — **as mesmas listas (mesmo GUID) do app principal** |
| Escreve em | `'7.4-tbl_InspPista'`, `'7.4.1-tbl_InspPistaItens'`, `tbl_inspPistaAnotacao` (todas com `Title` livre; cabeçalho tem `hash`, item tem `Hash`) |
| Limite de linhas | **500** (`DefaultConnectedDataSourceMaxGetRowsCount`; o principal usa 2000) |
| Flags | `delayloadscreens` true, `keeprecentscreensloaded` false, `sharepointselectsenabled` **true** (seleção explícita de colunas ligada), `enablesaveloadcleardataonweb` true, `errorhandling` true |
| Tema | `CCR` (o principal usa `MOTIVA`) |
| `SaveData/LoadData/Timer/IfError` | 0 / 0 / 0 / 0. `Connection.Connected` em 2 pontos (texto do painel e `DisplayMode` do botão de envio) |
| App Checker | 327 resultados: 279 de acessibilidade, 48 `app-*` (22 SuggestRemoteExecutionHint, 18 UnusedVariables, 2 CountRowsGalleryAllItems, 2 CollectingReadOnlyTable, 2 UnusedMediaResources, 1 ForAllWithMutation, 1 ScreenHasManyControls) |
| Checadores do projeto principal (baseline) | 0 referências entre telas; 3 consultas SharePoint por linha de galeria; 8 padrões não delegáveis; 18 variáveis escritas e nunca lidas; 0 erros de sintaxe |

## 2. Como o app funciona hoje

1. **Início** (`frmInspPistaMob.OnVisible`, 12): `Select(IconRefreshInspPistaMob)` carrega em `col_inspPista_mob` as inspeções **de hoje** do aeroporto do usuário (delegável); carrega `col_inspPistaMenu` (`tbl_inspMenu` de PISTA). A galeria lista só as de hoje; as "Em andamento" mostram "Continuar".
2. **Cadastrar** (`Icon28_214`, 257): limpa os 3 buffers e abre o formulário (usado só como interface; nunca é submetido).
3. **Iniciar Inspeção** (`ButtonCanvas4`, 2453): valida os campos, gera `var_hash = Text(Now(),"yyyymmddhhmmss") & RoundDown(Rand()*100000, 0)` e grava o cabeçalho **no buffer** (`col_inspPista_mob_temp`) com `hash`.
4. **Passo 2 — Local / Categoria / Item** (2630–3225): botões com contadores de não conformidades abertas (das coleções `col_itensPouso/Taxi/Aids` do OnStart).
5. **Passo 3 — Apontamento** (3371–3559): áudio (base64 em `col_anotacaoAudio_mob`), até 3 fotos (`AddMedia`), GPS no "Incluir Apontamento" → item no buffer com `InspHash = var_hash` e `Hash`. Na mesma tela, lista das não conformidades abertas daquele item com "Normalizar".
6. **Finalizar Inspeção** (`ButtonCanvas4_1`, 2430): abre o painel "Salvar itens apontados" e faz `Select(ButtonCanvasSalvarTodos)` — o envio (4065), desabilitado sem conexão.
7. **Envio** (4065): cria o cabeçalho a partir do buffer → grava `ID_pk` e `Protocolo` → cria todos os itens do buffer → relê os itens da inspeção e grava o protocolo de cada um → cria os áudios → desliga o spinner só se a contagem bater.
8. **Finalizar** (painel, `ButtonCanvas3_5`, 4276): atualiza o status (Pendente se houve apontamento, senão Finalizado), **limpa os buffers** e recarrega a lista.

## 3. Achados — persistência e escrita

| # | Onde | Achado | Efeito |
|---|---|---|---|
| M1 | App inteiro | Buffers só em memória; nenhum `SaveData`. Fotos guardadas como referência de blob da sessão (`UploadedImage1_6.Image`, 3469). | Perda total da inspeção em campo ao fechar o app, trocar de app com pouca memória, reiniciar o tablet ou voltar ao hub. |
| M2 | `ButtonCanvas3_5.OnSelect` (4276) | `Clear(col_inspPista_mob_temp); Clear(col_inspPistaItens_mob_temp)` incondicional, depois de dois `Patch` sem verificação (o do SharePoint usa `var_idInspRegister`, que fica em branco se o envio não rodou). | Sem conexão ou com envio parcial, o toque em "Finalizar" apaga o que não subiu. É o caminho de perda mais provável no uso real (pista sem sinal). |
| M3 | `ButtonCanvasSalvarTodos.DisplayMode` (4053) + `ButtonCanvas4_1` (2437) | Envio desabilitado offline e disparado por `Select`. Se `Select` roda ou não um botão desabilitado não está documentado (sonda S16). | Offline, ou nada é enviado (e M2 apaga) ou o envio falha em silêncio (e M2 apaga). |
| M4 | `ButtonCanvasSalvarTodos.OnSelect` (4065) | 1 + 1 + N + 1 consulta + N + M escritas encadeadas, sem `IfError`, sem consulta por `hash`/`Hash` antes de criar, `ForAll` com escrita (App Checker). | Queda de rede no meio deixa cabeçalho sem itens, itens sem protocolo, áudios faltando; reenvio duplica tudo. |
| M5 | `ButtonCanvas2_6.OnSelect` (3559) | `Hash: Text(Now(),"yyyymmddhhmmss") & Text(Rand(),"[$-en-US]########")` — a máscara inteira sobre uma fração devolve no máximo um dígito. | Dois apontamentos no mesmo segundo têm o mesmo `Hash`; o indicador "Salvo/Processando" por linha (4137) mostra "Salvo" para um item que não subiu. |
| M6 | `ButtonCanvas5_33.OnSelect` (3677) | `Patch` de normalização comentado; só `RemoveIf` na coleção local e `Notify("… foi normalizado com sucesso")`. | Falsa confirmação: o SharePoint não muda, o item volta a aparecer. |
| M7 | `ButtonCanvas9.OnSelect` (557) — "Continuar" | Não define `var_hash` da inspeção escolhida; carrega os itens do servidor para o buffer sem `InspHash`. No envio, `LookUp(col_inspPista_mob_temp, hash = var_hash)` sai em branco e o `ForAll` percorre o buffer inteiro. | Formulário abre vazio ou com a inspeção anterior; itens já gravados são recriados como novos; cabeçalho novo vazio ou erro. |
| M8 | `Icon28_214.OnSelect` (257) — "Cadastrar" | Limpa os 3 buffers sem perguntar. | Uma inspeção deixada no meio (usuário voltou à lista) some ao começar outra. |
| M9 | `Icon1_18.OnSelect` (105) | Volta ao hub com `Launch(…, LaunchTarget.Replace)` sem confirmar se há buffer não enviado. | Perda silenciosa do buffer. |
| M10 | `ButtonCanvasSalvarTodos` (4065) | Spinner só desliga se `CountRows(Filter(FirstN(Sort(itens, ID desc), 100), IdInsp = novo))` bater com a galeria. | Com mais de 100 itens novos na lista (outros inspetores) ou falha parcial, o spinner não para (não bloqueia a tela, mas engana). |
| M11 | Cabeçalho criado só no envio, status "Em andamento" até o "Finalizar" | Se o app fechar entre o envio e o "Finalizar", a inspeção fica "Em andamento" no servidor e cai no caminho quebrado de M7. |
| M12 | Temp do cabeçalho (2453) | `ID_Modulo` nunca é gravado (o Windows grava via DataCard); `Fim: TimeValue(Now())` numa coluna texto (4300, também no app principal) — formato diferente do `HH:MM` do início (a confirmar no dado). | Dado inconsistente entre os dois apps. |
| M13 | `ButtonCanvas3_4` (4162–4223), `Button14_13` (2320) | "Salvar manual" nunca fica visível (exige `Protocolo` que o buffer nunca tem) e grava `IdInsp` em branco; "Finalizar Inspeção em campo" exige `Var_IDinspPistaInsert <> 0`, que nunca é definido. | Código morto; o "Salvar manual" criaria item órfão se fosse reativado como está. |
| M14 | Áudio (3371, envio 4138) | Base64 em coluna texto, gravado com `ID_FK` do cabeçalho novo; o `ForAll` do envio não filtra por `ID_HASH`. | Ao "Continuar" sem "Cadastrar" antes, áudios de outra inspeção podem ir para o cabeçalho errado. |

## 4. Achados — leitura, delegação e desempenho

| # | Onde | Achado | Efeito / correção |
|---|---|---|---|
| L1 | `App.OnStart` (App.pa.yaml:11) | `Filter('7.4.1-tbl_InspPistaItens', Aeroporto = … && Local = … && Status = "Não conforme" && Year(Criado) = Year(Today()))` ×3 em `Concurrent`, sem `Sort`, limite 500. | Só as 500 primeiras linhas (mais antigas, todos os aeroportos) são filtradas no aparelho → contadores e lista de normalização vazios ou incompletos. Trocar por `Criado >= Date(Year(Today()), 1, 1)` (delegável) e subir o limite para 2000. |
| L2 | `Gallery13_12.Items` (3116) | `Filter(tbl_inspMenu, local = … And categoria = … And !IsBlank(item))` direto no SharePoint; `!IsBlank` não delega. | Rede a cada toque em categoria; offline o passo 2 não avança; acima de 500 linhas em `tbl_inspMenu` faltam itens. Usar `col_inspPistaMenu` como `Gallery13_11` já faz. |
| L3 | `GalleryResumo_7` (`Label12_3.Text` 4137, `ButtonCanvas3_4` 4162/4223) | 3 `LookUp` por `Hash` no SharePoint por linha. | N consultas por render no painel de envio; somem quando o status de envio vier do buffer. |
| L4 | `Button1_7/1_8/1_9/1_10/1_11.Text` (2630–3174) | `CountRows(Filter(Sort(col…)))` por botão e por linha, repetindo `Year(Criado)`. | Barato (coleção), mas `Sort` inútil dentro de `CountRows`. |
| L5 | `ID_modulo_DataCard1_3.Default` (2051) | `LookUp(tbl_Modulos, …)` na renderização de um formulário que nunca é submetido. | Consulta inútil; offline devolve branco. |
| L6 | `GalleryInspPistaListagem_1` (420) | Só as inspeções de hoje. | Inspeção iniciada ontem e não finalizada nunca pode ser continuada no mobile (comportamento a confirmar com o negócio). |
| L7 | `frmInspPistaMob.OnVisible` (12) | Bloco copiado do `frmHome` do app principal (`Param("LOGADO")`, `var_visibleErro`, `var_visibleContaErro`) cujas variáveis ninguém lê; faz `LookUp(User, Email = User().Email)` no Windows. | Consulta e código mortos. |
| L8 | 18 variáveis mortas | `Logado`, `var_load`, `varAutUser`, `varEmailUser`, `varFuncaoUser`, `varICAOUser`, `var_usuarioID`, `Var_inspPistaHash`, `varCategoria`, `varSubCategoria`, `varTopico`, `var_visibleAnotacaoAudio`, `var_visibleContaErro`, `var_visibleErro`, `var_visibleFilterInspPista`, `var_visibleInspecaoPista`, `var_visibleRelatorio`, `var_visibleSpinLoader`. | Limpeza. |

## 5. Segurança (fora deste app, mas grave)

`ScreenLogin` (Icon39.OnSelect, 183) valida usuário e senha contra a lista `User`: o valor gravado em `Senha` é comparado com a senha digitada intercalada com trechos do próprio valor gravado, em posições fixas. Consequências:
- a senha de cada usuário pode ser remontada a partir do que está gravado na lista;
- a lista `User` é lida por todos os apps do Airport Now (inclusive este e o principal), então qualquer usuário com acesso ao app tem acesso de leitura a ela;
- a tela ainda baixa o valor gravado para o aparelho (`varTempPass`).

A tela é inalcançável neste app (só por `Icon1_16`, invisível), mas o esquema é o do hub ("Efetuar Login" do app principal leva a ele). Recomendação: autenticar pela conta Microsoft (`User().Email`), que os dois apps já usam como alternativa, e retirar a coluna `Senha` do alcance dos apps. É uma decisão de arquitetura do hub, fora do escopo deste app.

**Não excluir `ScreenLogin` sem cuidado**: o `OnSelect` do login é o único lugar que define a estrutura de `col_inspPista_mob_temp` (`FirstN(col_inspPista_mob, 0)`) e de `col_inspPistaItens_mob_temp` (`FirstN(AddColumns('7.4.1-tbl_InspPistaItens', InspHash, ""), 0)`). Apagar a tela quebra a compilação da tela principal. A estrutura tem de ir antes para o `App.OnStart`.

## 6. Relação com o app principal (Inspeções)

| Aspecto | Mobile (esta auditoria) | Principal (Windows) |
|---|---|---|
| Quando o cabeçalho vai ao SharePoint | No fim (envio) | No "Iniciar" (`SubmitForm`) |
| Protocolo do cabeçalho | `IATA-INSP-PISTA-<ID>` | `IATA-INSP-PISTA-<ID>` (com `Upper`) |
| Protocolo do item | `IATA-INSP-PISTA-ITEM-<ID do item>` | `IATA-INSP_PISTA_ITEM-<maior ID da lista antes do lote>` (igual para todo o lote); o relatório de Apontamentos exibe `IATA-INSP-PISTA-<ID>` |
| `ID_Modulo` | não grava | grava |
| Idempotência | nenhuma (hash gravado e não consultado) | só no "Salvar" item a item (por `Hash`) |
| Normalizar | não grava (comentado) | grava |
| Fauna, detalhe, relatórios | não tem | tem |
| Limite de linhas | 500 | 2000 |

Três convenções de protocolo de item na mesma lista quebram busca e conferência. A do mobile é a única correta.

## 7. Sondas específicas deste app (somam às de `../Inspeções/build/sondas_offline.md`)

| # | O que fazer | Critério |
|---|---|---|
| S16 | Neste app, com o tablet em modo avião, abrir uma inspeção de teste até o painel de envio e observar se o envio roda (`Select` de botão desabilitado). | Anotar se `var_loadVincularInspPista` liga e se aparece erro. Decide se M3 é "não envia" ou "falha em silêncio". |
| S17 | `CountRows('7.4.1-tbl_InspPistaItens')` e `CountRows(tbl_inspMenu)` online. | Confirma L1/L2: acima de 500, os contadores de não conformidade do mobile estão errados hoje. |
| S18 | Apontar 2 itens no mesmo segundo (dois toques rápidos) e ver o `Hash` gravado. | Confirma M5. |

## 8. O que fazer

### 8.1 Correções rápidas (não dependem de sonda; nada visível muda além dos bugs)
1. `ButtonCanvas3_5` só limpa o buffer quando o servidor confirmar cabeçalho, itens e áudios (M2).
2. Envio idempotente: `LookUp('7.4-tbl_InspPista', hash = var_hash)` antes de criar o cabeçalho; `LookUp('7.4.1-tbl_InspPistaItens', Hash = …)` antes de cada item; `Title` do áudio com uma chave; tudo em `IfError`; o painel mostra o que falhou (M4).
3. `Hash` com unicidade real: `Text(Now(),"yyyymmddhhmmss") & "-" & varIdUser & "-" & Text(RoundDown(Rand()*1000000, 0), "000000")` (M5).
4. `Gallery13_12` lê `col_inspPistaMenu` (L2); `App.OnStart` com `Criado >= Date(Year(Today()), 1, 1)` e limite 2000 (L1).
5. Confirmação antes de descartar buffer em "Cadastrar" e na volta ao hub (M8, M9).
6. Estrutura das coleções no `App.OnStart` (pré-requisito para qualquer limpeza de `ScreenLogin`).

### 8.2 Offline (recomendo que seja o piloto da Fase 3)
Por que aqui primeiro: é onde o inspetor está sem sinal; é uma tela só (o Timer do motor vai direto na tela, sem depender da sonda de componente); escreve em 3 listas que já têm chave de idempotência (`hash`, `Hash`, `Title`); não tem anexos nativos nem fluxos; e o buffer já existe. O motor provado aqui é reaproveitado no app principal, porque as listas são as mesmas.

Desenho resumido (mesmos princípios do plano, sem mudar esquema):
1. `SaveData` dos 3 buffers a cada mudança (Iniciar, Incluir Apontamento, gravar/excluir áudio, excluir apontamento); `LoadData` no `App.OnStart`. Fotos convertidas para base64 no "Incluir Apontamento" (um arquivo por inspeção para não carregar todas as fotos na memória).
2. "Finalizar Inspeção" marca a inspeção como finalizada **no aparelho** e volta à lista; ninguém espera rede.
3. Timer na tela, 1 passo por disparo, quando houver conexão: cabeçalho (por `hash`) → `ID_pk`/`Protocolo` se em branco → itens (por `Hash`) → protocolo do item se em branco → áudios (por `Title`) → status final → remove do buffer só o que o servidor confirmou → `SaveData`.
4. Indicador no cabeçalho: pendentes / enviando / erro; toque reenvia.
5. Leitura offline: `col_inspPistaMenu`, perfil do usuário, não conformidades do ano e inspeções de hoje em cache (`SaveData`), mesclando as inspeções do buffer na lista.
6. "Normalizar" entra na fila como atualização (se você confirmar que o mobile deve normalizar).
7. "Continuar": só para inspeções do próprio aparelho (buffer) ou carregando a do servidor com o `hash` dela e os itens marcados como já enviados.

## 9. Decisões que dependem de você

1. **Piloto offline no mobile de Pista** antes de Pátio/TPS (muda a ordem aprovada da Fase 3)?
2. **Normalizar no mobile**: implementar a gravação (hoje é só aparência) ou retirar o botão?
3. **Formato do protocolo de item**: padronizar em `IATA-INSP-PISTA-ITEM-<ID>` (o do mobile) também no app principal?
4. **"Continuar" no mobile**: restringir às inspeções iniciadas no próprio aparelho, ou permitir continuar as do Windows (mais trabalho, risco de conflito)?
5. **Lista do dia**: mostrar só as de hoje (como está) ou também as em andamento de dias anteriores?
6. **Senhas do hub** (seção 5): levar ao responsável pelo Airport Now.
