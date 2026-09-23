# Entrega — Airport Now · Inspeções — frente "app leve" (Lotes A, B, C e D)

Origem: `AirportNow-Inspeções_20260916201558.zip` (publicado em 14/09/2026), 19 telas, 60.015 linhas de YAML, 3.814 controles.
Gerado por `build/entregar.sh ABCD` em 2026-09-17. Auditoria completa em `../AUDITORIA.md`; plano aprovado em `~/.claude/plans/fa-a-a-auditoria-completa-glittery-sonnet.md` (esta entrega cobre as Fases 1 e 2; a camada offline vem nas Fases 3–5, sobre o reexport desta).

**Nada que o usuário vê mudou**, com as exceções listadas na seção 3 (todas correções de bug ou de dado errado). A trava de layout provou isso comparando 3.160 controles antes e depois (69 exceções, todas declaradas e cobradas).

Se preferir aplicar em duas etapas, `build/entregar.sh AB` gera só a Fase 1 (sem App, sem bugs de cópia) e `build/entregar.sh ABCD` a entrega completa. Os arquivos em `out/` hoje são da entrega completa.

## 1. Ordem de aplicação (a ordem importa por causa das named formulas)

1. **App.Formulas** — Studio → App (árvore de controles) → propriedade **Formulas** → colar `02_App_Formulas_ptBR.txt` inteiro (substituir). Define `nfAeros` e `nfParametrosAnimais`. Vai primeiro porque named formula ausente derruba a tela que a usa com dezenas de erros longe da causa.
2. **Telas** — para cada `NN_<Tela>.pa.yaml` (14 arquivos, qualquer ordem entre si): Studio → tela → **Exibição de código** → selecionar tudo → colar → confirmar. Conferir o painel de erros.
3. **App.OnStart** — App → propriedade **OnStart** → colar `01_App_OnStart_ptBR.txt` inteiro. Por último porque define `varModoFiltroAero`, `varModoFiltroBloco` e `varBlocoPadrao`, que as telas já leem. (`01_App.pa.yaml` é a mesma coisa em formato invariante, só para referência — **não** colar os dois.)
4. **Salvar → Executar (Alt) → testar (seção 6) → Publicar → Exportar o .msapp** e me devolver o zip. O reexport vira a origem das próximas fases.

| Arquivo | Tela | Cirurgias |
|---|---|---|
| 03_frmHome.pa.yaml | frmHome | A6, A7 |
| 04_frmInspPistaCad.pa.yaml | frmInspPistaCad | A1, A4, A5, A6, B3f, B4, C5a, C5b, C5c, D7b, D8 (via D7b) |
| 05_frmFormZPA.pa.yaml | frmFormZPA | D7b, D8z |
| 06_frmHomePista.pa.yaml | frmHomePista | A2, A4, A5, A6, B1, B2, B3b, B4, B5, C4, C4b, C5a-c, C6b, D7a, D8 |
| 07_frmHomeApont.pa.yaml | frmHomeApont | A4, A5, A6, A7, B1, B3h, C5a-c, C6c, D3, D8 |
| 08_frmHomePatio.pa.yaml | frmHomePatio | A1, A1b, A3, A4, A5, A6, A7, B1, B3b, B3c, B3g, B4, C5a-c, C6a, C6d, D8 |
| 09_frmHomeTPS.pa.yaml | frmHomeTPS | A1, A1b, A3, A4, A5, A6, A7, B1, B3b, B3c, B3g, B4, C5a-c, C6a, C6e, D2, D2t, D8 |
| 10_frmHomeZPA.pa.yaml | frmHomeZPA | A1, A5, A6, B1b, B3b, C5a-c, D7a |
| 11_frmFormZPAeditar.pa.yaml | frmFormZPAeditar | A6, D4, D7b, D8 |
| 12_frmFormZPAmenu.pa.yaml | frmFormZPAmenu | A4, A6, A7 |
| 13_frmZPAapontamentos.pa.yaml | frmZPAapontamentos | A1b, A3z, A3b, A5, B1, C5a-c, D2z, D8 |
| 14_frmVeiculos_Equipamentos.pa.yaml | frmVeiculos_Equipamentos | A1, A5, A6, B6, C5a, C5b, D7a |
| 15_frmCheckListGenericoEQP.pa.yaml | frmCheckListGenericoEQP | A1, A5, A6, B3d, B4, C5a, C5b, D1, D8 |
| 17_frmRelatorioVistoVeic.pa.yaml | frmRelatorioVistoVeic | B3d |

Sem arquivo (não mudaram): frmRelatorioZPA e as 4 telas mortas (Screen1, ScreenConsultarV1, frmApontFauna, frmRelatorioZPA_1 — seção 5).

## 2. O que mudou

### Lote A — mecânico, mesmo valor em runtime
| Id | O quê | Onde (vezes) |
|---|---|---|
| A1 / A1b | `MainContainerListar.Width` (container de **frmHomePista**) e `MainContainerListarApont.Width` (**frmHomeApont**) → `Max(App.Width, App.MinScreenWidth)`. É a largura exata daqueles containers (toda a cadeia até eles é "SetByContainer" sem Width, a partir de `ScreenContainerMain.Width = Max(App.Width, App.MinScreenWidth)`). Abrir Pátio/TPS/ZPA/Veículos/Checklist/Cadastro deixa de carregar frmHomePista e frmHomeApont inteiras. | 6 + 6 |
| A2 | `Icon28_195.HoverColor` (ícone de frmHomePatio) → literal `RGBA(96, 70, 237, 1)` (valor lido em frmHomePatio:190). | frmHomePista 3 |
| A3 / A3z | Contador "N Itens apontados na inspeção: protocolo" lia `GalleryApontListagem` (frmHomeApont) e `'7.4-tbl_InspPista'` → galeria e lista locais. Texto continua vazio: `var_directDetInsp` só recebe 0 nessas telas. | frmHomePatio, frmHomeTPS, frmZPAapontamentos |
| A3b | frmZPAapontamentos: `Label18_9` lia a seleção de `GalleryInspPatioitens` (**frmHomePatio**) e `Label5_8` lia `Gallery5_2` (**frmFormZPAeditar**) → seleção local. Ver seção 3. | 2 |
| A4 | `CountRows(G.AllItems)` → `G.AllItemsCount`. | 10 |
| A5 | `DelayOutput: =true` nos 17 campos `txtLimit*`/`txtBuscar*` (`Classic/TextInput@2.3.2`; propriedade já usada no export). | 17 |
| A6 | 130 escritas de 55 variáveis que nenhuma fórmula lê (lista do App Checker, reconferida com 0 leituras no escopo), incluindo o bloco de `OnHidden` de frmHome/frmHomePista, `Set(var_usuarioID)`, `Set(var_idItensZPA)` e chaves de contexto passadas por `Navigate` para variáveis que a tela de destino nunca lia. | 12 telas |
| A7 | 30 controles com `Visible: =false` literal e zero referências: `PdfViewer3/_1`, `NavInspecao_1`, `LinkAirportNow_1`, `NavMob_1`, 18 `Circle1_*`, e o bloco oculto de "busca específica" de Apontamentos (`Toggle1BuscEsp_3`, 3 rótulos, 3 dropdowns com `Distinct` sobre a lista de itens inteira). | frmHome 3, frmHomePatio 8, frmHomeTPS 7, frmFormZPAmenu 5, frmHomeApont 7 |

### Lote B — delegação e consultas por linha
| Id | O quê | Onde |
|---|---|---|
| B1 | Galerias: `IsBlank(x) \|\| StartsWith(col, x)` → `StartsWith(col, Text(x))` (`StartsWith(col, "")` é verdadeiro para toda linha; o `IsBlank` era redundante e impedia a delegação: a lista voltava truncada nas 2.000 primeiras por ID e os registros novos sumiam). Datas: `IsBlank(dtp) \|\| col >= dtp` → `col >= Coalesce(dtp.SelectedDate, Date(2000, 1, 1))` (teto 2099). frmZPAapontamentos passa a respeitar `txtLimitApont_3` (100). | frmHomePista 5, frmHomePatio 10, frmHomeTPS 5, frmHomeApont 6, frmZPAapontamentos 7 |
| B1b | frmHomeZPA: `IsBlank(txt) \|\| ID = Value(txt)` → `Switch(true, IsBlank(txt), Filter(sem ID), Filter(com ID))`. | 1 |
| B2 | `Year(Criado) = Year(Today())` → `Criado >= Date(Year(Today()), 1, 1)` (antes baixava a lista de itens inteira 3 vezes no Atualizar). | frmHomePista 3 |
| B3b | Ícone/botão por linha: `Status = "Finalizado" And !IsBlank(LookUp(...))` — só linhas finalizadas consultam a lista; `First(Filter(...))` → `LookUp`. | 4 |
| B3c | Menu de procedimentos: `LookUp(Filter(lista, pai), item)` → um `LookUp` delegável com as duas condições. | frmHomePatio, frmHomeTPS |
| B3d | `GalleryCLG.Items` (checklist de veículos) fazia `LookUp(Filter(objeto…))` **por linha da base** e `AddColumns` com `First(SortByColumns(Filter(Sort(veículos))))` **por linha** — N+1 duplo sobre a base inteira. Agora `ButtonRefreshCLG` (que roda no OnVisible e nos filtros) carrega uma vez `col_clgNaoConf`, `col_clgVeiculosEmpresa`, `col_clgClasses` e `var_clgIdEstadoGeral`; galeria, `ButtonCanvas7_17.FontColor`, `Label19_158`, `Label20` e `Label20_1` (relatório) leem as coleções. Mesmas linhas, mesma ordem. | frmCheckListGenericoEQP 5, frmRelatorioVistoVeic 1 |
| B3f | frmInspPistaCad `ButtonCanvas3.DisplayMode` tinha fórmula sintaticamente quebrada com 1 LookUp por linha; o ramo Disabled é inalcançável → `=DisplayMode.Edit`. | 1 |
| B3g | "Protocolo inspeção" por linha: `LookUp(cabeçalho, ID = ID_insp, Protocolo)` → `ThisItem.IATA & "-INSP-PAT-" & ThisItem.ID_insp` (é exatamente como o protocolo do cabeçalho é gerado). Zero consultas. | frmHomePatio, frmHomeTPS |
| B3h | `HtmlText1_3` (frmHomeApont): oculto dentro do template, 1 LookUp por linha, ninguém lê → removido. | 1 |
| B4 | `First(Filter(T, ID = x))` → `LookUp(T, ID = x)` (listas e coleções). | 18 |
| B5 | `Foto*.Default` dos 3 formulários de fauna: `LookUp('7.4.1-tbl_InspPistaItens', ID = …Selected.ID).Foto.Full` → `GalleryInspPistaItensDetalhes.Selected.Foto.Full` (9 downloads full-size a menos ao abrir o detalhe). | frmHomePista 9 |
| B6 | `ClearCollect(col_userNotifyCriticidade, tbl_userNotify)` a cada entrada na tela → `If(IsEmpty(…), ClearCollect(…))`. | frmVeiculos, frmCheckList |

### Lote C — App.Formulas, OnStart, derivados do perfil, relatórios
| Id | O quê |
|---|---|
| C1 | **App.Formulas** novo com `nfAeros` (18 registros, copiados byte a byte do OnStart) e `nfParametrosAnimais` (89 registros, copiados do OnVisible de frmHomePista). Named formulas são avaliadas sob demanda e memoizadas. Marcador `// GANCHO OFFLINE` no fim para o motor de sincronização. |
| C2 | **App.OnStart** 228 → 31 linhas: some `Max(tbl_controle_versoes)` (não delegável, alimentava variável que ninguém lia), somem `varEmailUser`/`varFuncaoUser` (não lidas), `LookUp(User)` 3 → 2 (o terceiro virava `usuario.Aeroporto`), `colAeros` passa a `ClearCollect(colAeros, nfAeros)` (nome mantido: 30+ fórmulas a leem), identificação do usuário **igual à de antes** (parâmetro do hub, senão nome completo). Novos: `varModoFiltroAero`, `varModoFiltroBloco`, `varBlocoPadrao` calculados uma vez. Marcador `// GANCHO OFFLINE` antes de `Set(var_load, false)`. |
| C4 | frmHomePista.OnVisible 459 → 9 linhas: a tabela de espécies saiu para `nfParametrosAnimais`; os 3 leitores (`Distinct`/`LookUp` do combo de espécie) apontam para ela. |
| C5 | 42 fórmulas repetidas de perfil → variáveis do OnStart: `If(varPerfilUser = "Base" Or "Bloco", Disabled, Edit)` ×11 → `varModoFiltroBloco`; `If(varPerfilUser = "Base", Disabled, Edit)` ×11 → `varModoFiltroAero`; bloco padrão do combo ×9 → `varBlocoPadrao`. |
| C6a | Relatório de Pátio/TPS: o `ForAll(menu, ForAll(Filter(SP, ID_insp = …)))` fazia **1 consulta por item do menu** → uma consulta antes (`col_relatorioItensInsp`), mesma iteração e mesma ordem. |
| C6b–e | Os 4 relatórios HTML (`HtmlText3_5`, `HtmlText3`, `HtmlText3_1`, `HtmlText3_4`) eram visores ocultos **recalculados a cada mudança de filtro** (o de Apontamentos com 3 LookUps por linha × 100). O corpo HTML foi movido **byte a byte** para o clique do botão de PDF (`UpdateContext({var_htmlRel…: …})`) e o visor lê a variável. Em Pista, o `ForAll + Remove + LookUp` O(n·m) que montava os "conformes" virou um `Filter` único (mesmo conjunto). PDF sai igual. |
| D9 (junto) | Retorno de `'Criar-HTML'.Run` sem guarda: se o fluxo falhar, agora aparece "Não foi possível gerar o PDF" em vez de um `Launch` com URL em branco. |

### Lote D — bugs de cópia, navegação entre telas, erro visível
| Id | O quê |
|---|---|
| D1 | Checklist "Normalizar": dois `Patch` idênticos em `Concurrent` (escrita dobrada) → um. |
| D2 | **frmHomeTPS operava formulários e lista de Pátio**: "Lançar não conformidade" fazia `NewForm(FormInspPatioitens)` (o form TPS não era resetado), o menu de procedimentos consultava `tbl_inspPatioItens` (item "já lançado" nunca desabilitava em TPS), normalizar/cancelar usavam `FormGerInspPatioitem` → equivalentes TPS. O cabeçalho do formulário de normalização dizia "-INSP-PAT-ITEM-" → "-INSP-TPS-ITEM-". |
| D2z | frmZPAapontamentos: normalizar/cancelar usavam `FormGerInspPatioitem` (Pátio) → `FormGerInspZpaItens` (local). |
| D3 | frmHomeApont: os 3 formulários de fauna chamavam `SubmitForm(FormInspPistaItensDetalhes)`, formulário que só existe em frmHomePista — submetia, de outra tela, o item que estivesse selecionado lá (e a cadeia de status/exclusão de áudios). Removido; editar fauna em Apontamentos grava só a fauna. |
| D4 | frmFormZPAeditar: cada edição criava um **registro novo** de fotos (`Defaults`) lendo as imagens de **frmFormZPA**. Agora atualiza o registro existente (`LookUp(ID_FK)`; cria só se não houver) com as imagens do próprio formulário (`Image3`, `Image17`…`Image21`, que mostram a foto existente ou a nova). |
| D7 | 15 `ResetForm/NewForm/EditForm/Reset` de controles de **outra** tela antes do `Navigate` (obrigavam a carregar a outra tela e não funcionam se ela ainda não foi carregada) → saem da origem; a tela de destino faz a preparação no seu `OnVisible` (`frmFormZPA` com `var_zpa_modo`, `frmFormZPAeditar`, `frmInspPistaCad` por `var_acao`). Em frmVeiculos os 6 `Reset(AddMediaButton*)` eram de frmFormZPA (cópia sem sentido) e saíram. Em frmHomeZPA o botão "Continuar" da lista fazia `EditForm(FormInspTPS)` (cópia): continua inerte, agora sem a referência. |
| D8 | `OnFailure` nos 18 formulários que não tinham (`Notify` de erro); em `FormZpa`, que só desligava o spinner, agora também avisa. |

Não feito de propósito: **C3** (`Host.OSType` → variável) — com o OnStart não bloqueante a variável ficaria em branco por um instante e os filtros piscariam; `Host.OSType` inline custa nada. **D10** (15 pontos que limpam a tela antes de confirmar a gravação) fica para a fila offline, que resolve isso estruturalmente.

## 3. Mudanças que o usuário PODE notar (todas declaradas na trava de layout)

1. **frmZPAapontamentos, normalizar**: cabeçalho passa a mostrar o item ZPA selecionado ("…-INSP-ZPA-ITEM-N"); antes mostrava um item de Pátio ou nada. **Confirmação de exclusão**: "ID: N" passa a ser o item certo. **Lista**: respeita o limite (100) como as demais telas.
2. **frmHomeTPS, normalizar**: cabeçalho "…-INSP-TPS-ITEM-N" (antes "-INSP-PAT-ITEM-"); o item já lançado fica desabilitado no menu (antes nunca ficava); "Lançar não conformidade" abre o formulário limpo.
3. **Listagens com mais de 2.000 registros**: passam a mostrar os mais recentes.
4. **Filtro de data em branco**: inclui registros entre 2000 e 2099 (na prática todos).
5. **Campos de busca/limite**: refiltram ~1 s depois de parar de digitar.
6. **Falha de gravação**: aparece uma notificação vermelha (antes nada).
7. **PDF**: se o fluxo falhar, aviso em vez de link em branco.
8. **Editar ZPA**: não cria mais um registro de fotos duplicado por edição.

## 4. Decisões que dependem de você

- **D5** — checklist de veículos: `Foto: ThisRecord.Foto` está comentada no `OnSuccess` de `FormCheckGenerico` (linha ~1158 do export): as fotos anexadas nas respostas **nunca** chegam ao SharePoint. Descomentar? (a lista tem `Foto1..Foto6`.) Não mexi.
- **frmHomeZPA:1249** apaga `tbl_inspTPSitens`/`tbl_inspTPS` de dentro da tela ZPA (exclusão de TPS num botão da tela ZPA). Mantive; confirmar se é intencional.
- **Fase 3 em diante (offline)** precisa das sondas S1, S2, S3, S5, S8 e S12 de `build/sondas_offline.md` executadas por você no Studio/tablet.

## 5. Passos manuais no Studio (depois de colar e testar)

1. Excluir 4 telas mortas (nenhuma fórmula viva as referencia): `frmApontFauna`, `ScreenConsultarV1`, `frmRelatorioZPA_1`, `Screen1`.
2. Remover 5 fontes de dados sem uso: `tblInspMenu`, `tbl_bdv`, `UsuáriosdoOffice365`, `'7.5-tbl_InspZpa'`, `'7.5-tbl_InspZpaItens'` (as duas últimas só depois de excluir `frmRelatorioZPA_1`).
3. Remover 25 mídias sem uso (2,0 MB de 3,05 MB): `notificacao`, `Loading_41`, `check-icone-1-scaled`, `gifBlue`, `MOTIVA_RGB_Logo_VersaoPositiva_Anil`, `LogoZPA` (maiúsculo; o usado é `logoZPA`), `marca`, `200w`, as 5 "Captura de tela …", `LogoAN`, `camera1`…`camera6`, `BDV`, `areaExternas`, `pistaMenu`, `SamplePdf`, `SampleAudio`.

## 6. O que testar depois de colar

Perfis Base, Bloco e Sede; Windows e tablet.
- **Início**: o app abre; combos de bloco/aeroporto vêm com o padrão do perfil e travados para Base/Bloco (como antes).
- **Pista**: listar/filtrar/buscar; abrir detalhes com fotos; **nova inspeção** (formulário vem limpo) e **continuar inspeção** (formulário vem preenchido) — D7; combo de espécie no registro de fauna lista as espécies (C4); relatório PDF de uma inspeção **igual** ao de antes (comparar com um gerado antes de colar).
- **Apontamentos**: filtrar; editar um apontamento de fauna (grava a fauna; o item de pista não é tocado); PDF igual ao de antes.
- **Pátio e TPS**: iniciar inspeção; lançar não conformidade **duas vezes seguidas** (TPS: formulário limpo na 2ª; item lançado desabilita no menu); normalizar (cabeçalho com o protocolo certo); relatório de inspeção e PDF iguais aos de antes.
- **ZPA**: nova inspeção (formulário e 6 fotos limpos), editar inspeção (fotos existentes aparecem; ao salvar **não** surge registro novo em `tbl_inspZPAfotos`); apontamentos ZPA: normalizar (cabeçalho certo), excluir (ID certo).
- **Veículos/Checklist**: cadastrar veículo (formulário limpo); lista de vistorias com e sem "mostrar apontamentos" (mesmas linhas; empresa preenchida; botão vermelho para não conformidade aberta); normalizar item; relatório de vistoria.
- **Falha forçada**: desligar a rede e tentar gravar em cada formulário → notificação de erro (D8); gerar PDF sem rede → aviso (D9).
- **App Checker** (metas): `InefficientDelayLoading` 20 → 0; `CrossScreenEventDependencies` 15 → 0; `CountRowsGalleryAllItems` 14 → 2 (0 após excluir ScreenConsultarV1); `TextInputIsNotDelayOutput` 3 → 0; `UnusedVariables` 60 → 1 (a da tela morta); `UnusedMediaResources` 23 → 0 após o passo 5.3.
- **Delegação** (5 min): Configurações → Geral → Limite de linha de dados = 1; abrir a listagem de Pista: o registro mais recente aparece. Voltar para 2000.

## 7. Validado localmente (`build/entregar.sh ABCD`)

- YAML parseável; 3.160 controles sem nome duplicado; toda propriedade existe no dicionário extraído deste export (41 tipos) — nenhum PA2108 provável. Só duas propriedades foram acrescentadas (`DelayOutput`, `OnFailure`), ambas já usadas no export, inseridas em ordem alfabética.
- Trava de layout: árvore, ordem e 50 propriedades visuais idênticas ao export fora as 69 exceções declaradas (31 controles removidos, 38 propriedades de texto/largura/cor listadas nas seções 2 e 3).
- Valor de cada propriedade comparado com o export (lido como YAML, como o Studio lê): 193 propriedades alteradas, 37 novas (`DelayOutput`, `OnFailure`, 3 `OnVisible`), 31 controles removidos — conjunto igual à lista revisada em `build/propriedades_esperadas_ABCD.json`; nenhuma propriedade muda só em espaço em branco. (Revisão de 17/09: 4 fórmulas recuperaram uma linha só de espaços que a geração anterior apagava — sem efeito no app; se você já colou a versão anterior, não precisa colar de novo.)
- Sintaxe: parênteses/aspas balanceados, sem vírgula faltando, sem `;;` ativo, sem instrução vazia deixada pelas remoções.
- Referências entre telas: 54 → **0**. Consultas SharePoint por linha: 46 → 9, todas justificadas (`build/allow_por_linha.json`). Padrões não delegáveis: 38 → 14 justificados (`build/allow_delegacao.json`).
- Todo formulário tem `OnFailure`; todo `Launch` de PDF tem guarda; toda `nf*` usada existe no App.Formulas; toda `var*` nova lida nas telas é definida no OnStart. Variáveis mortas: 0.
- `App.OnStart` e `App.Formulas` em pt-BR com prova de ida e volta (invariante → pt-BR → invariante idêntico). Idempotência (2 execuções, mesmo hash). 0 CR.

## 8. NÃO validado (depende do Studio conectado às listas reais)

- Compilação pelo Studio e App Checker.
- `App.Formulas` com `Table({...})` de 89 registros: compila, mas confira o painel de erros logo depois de colar o passo 1.
- Larguras (A1/A1b): substituição formalmente equivalente; confira a faixa de filtros de Pátio/TPS/ZPA/Veículos/Checklist e as barras de Apontamentos.
- `StartsWith(col, Text(Blank()))` no servidor (equivale a `StartsWith(col, "")`; é o que frmHomeTPS já fazia).
- `Status <> "Normalizado"` delegado ao servidor em `col_clgNaoConf` (itens com Status vazio).
- Os 4 PDFs: mesmo HTML, mas gerado no clique — compare um de cada tipo com um gerado antes.
- `OnVisible` novo em frmFormZPA/frmFormZPAeditar/frmInspPistaCad roda **depois** do `Navigate` (antes, a preparação rodava antes): confira que o formulário abre limpo/preenchido conforme o caso.
