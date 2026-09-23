# Auditoria — Airport Now · Inspeções

Data: 2026-09-16. Origem: `AirportNow-Inspeções_20260916201558.zip` (publicado em 14/09/2026, solução gerenciada "Grupo CCR (default)"), extraído em `extracted/` (solução) e `msapp/` (conteúdo do .msapp). Todos os caminhos abaixo são relativos a `Inspeções/msapp/Src/`, salvo indicação. Linhas referem-se ao export original; depois de qualquer entrega colada e reexportada elas mudam.

Plano de correção aprovado: `~/.claude/plans/fa-a-a-auditoria-completa-glittery-sonnet.md` (fases 0–6). Este documento é o inventário de evidências que o plano usa.

## 0. Resumo executivo

1. **Nenhuma persistência local e nenhum tratamento de erro.** Zero `SaveData/LoadData/ClearData`, zero `IfError/IsError`, zero `Timer`, `App.OnError` indefinido. `Connection.Connected` aparece só num ícone decorativo (`frmInspPistaCad:4295-4313`). Dos 19 formulários, 5 têm `OnFailure`; os outros 14 falham em silêncio.
2. **O ponto mais usado em campo duplica dados ao reexecutar.** "Finalizar inspeção em campo" de Pista (`frmInspPistaCad:2381` → botão oculto `4342`) grava o lote com `Patch(lista, ForAll(...))` sem identidade, protocolo igual para todos os itens e sem nenhuma verificação. O único caminho idempotente do app (botão "Salvar" item a item, `4440-4501`) usa uma coluna `Hash` cujo gerador devolve vazio (`Text(Rand(),"[$-en-US]########")`).
3. **Cadeias de gravação sem transação.** A cadeia de fauna (`frmHomePista:8798 → 5517 → 3809`) toca 5 listas em 2 sites, dispara 1 e-mail e apaga áudios, tudo encadeado por `OnSuccess`. Exclusões em cascata usam `Concurrent` (ordem indefinida) ou apagam o pai antes dos filhos.
4. **15 pontos limpam a tela, navegam ou avisam "sucesso" antes de a gravação ser confirmada.**
5. **Bugs de cópia entre telas clonadas:** TPS opera formulários e lista de Pátio; Apontamentos submete um formulário que só existe em outra tela; editar ZPA cria um registro de fotos novo a cada vez; o checklist de veículos nunca grava fotos; dois `Patch` idênticos em `Concurrent`.
6. **Peso:** 3.814 controles em 19 telas; 6 telas concentram 66%; ~39% é redundante (4 telas mortas = 429 controles; TPS clone de Pátio com similaridade 0,76; 3 formulários de fauna triplicados; 365 controles em subárvores invisíveis; 2,0 MB de 3,05 MB de mídia sem uso; 5 fontes de dados sem uso).
7. **Delay-load anulado:** 15 dependências de evento e 20 referências de layout entre telas fazem qualquer listagem carregar `frmHomePista` e `frmHomeApont` inteiras.
8. **Consultas por linha:** 15 fórmulas fazem `LookUp/Filter/First` em SharePoint dentro de templates de galeria; 9 `LookUp(...).Foto.Full` idênticos em `Default` de DataCards; 4 relatórios HTML ocultos recalculam a cada tecla (um deles com 3 `LookUp` por linha × 100).
9. **Delegação quebrada** nas galerias principais (`Search`, `IsBlank(x)||…`, `Year(Criado)`, `Distinct` sobre lista, N+1 duplo em `GalleryCLG`), nenhum campo de busca com `DelayOutput`.
10. **OnStart/OnVisible pesados e sem `App.Formulas`:** `Max()` não delegável para variável não usada, 3 `LookUp(User)` onde 1 basta, 18 registros literais no OnStart e 89 no OnVisible de Pista; 60 variáveis mortas.

## 1. Linha de base (medida no pacote)

| Métrica | Valor |
|---|---|
| Controles / telas | 3.814 / 19 (`msapp/Properties.json` `ControlCount`) |
| Telas com > 200 controles | frmHomePista 602, frmHomePatio 469, frmHomeApont 451, frmHomeTPS 439, frmApontFauna 319 (morta), frmInspPistaCad 229 |
| YAML | 60.015 linhas, 3,78 MB |
| HtmlViewer | 103 (32.796 chars de HtmlText) |
| TypedDataCard | 382 |
| Galerias | 51 |
| App Checker | 1.182 resultados: 995 `acc-*`, 187 `app-*` |
| Mídia empacotada | 3.050.645 B em 56 arquivos; 2.108.589 B (69,1%) não referenciados |
| `DefaultConnectedDataSourceMaxGetRowsCount` | 2000 |
| Flags relevantes | `delayloadscreens` true, `delaycontrolrendering` true, `keeprecentscreensloaded` true, `sharepointselectsenabled` **false**, `enablesaveloadcleardataonweb` true, `expandedsavedatasupport` true, `errorhandling` true, `pdffunction` true, `userdefinedfunctions` ausente (UDF não habilitado) |
| `App.Formulas` | inexistente (`App.pa.yaml` só tem `OnStart` e `Theme`) |
| Quebra de linha | 100% LF |
| Componentes | `HeaderTitle`, `HeaderTitle_1` definidos e **nunca instanciados** |

Fontes de dados: site `AIRPORTNOW` (18 listas + biblioteca `Documentos`), site `IntelignciaSafety` (4 listas de fauna), conectores `Criar-HTML`, `NotifyFauna`, `PowerAppV2->Criararquivo…` (= fluxo CRIAR-PDF-IMAGEM), `UsuáriosdoOffice365`. Esquema completo em `msapp/References/DataSources.json` (`DataEntityMetadataJson.schema.items.properties`). `Title` existe em todas as listas, não é obrigatória em nenhuma (`required=[]`) e não é lida nem escrita em tela alguma.

## 2. Persistência e escrita

### 2.1 Fatos transversais

| Item | Achado |
|---|---|
| `SaveData/LoadData/ClearData` | 0 ocorrências |
| `IfError/IsError/Errors` | 0 ocorrências |
| `App.OnError` | não definido |
| `Timer`, `OnTimerEnd` | 0 |
| `Connection.Connected` | 4 usos, todos decorativos, em `frmInspPistaCad:4295, 4297, 4300, 4313` |
| `OnFailure` em Form | 5 de 19 (`frmHomePista:3808`, `frmInspPistaCad:644`, `frmVeiculos_Equipamentos:1185`, `frmFormZPA:134`, `frmFormZPAeditar:130`); os de ZPA só desligam o spinner, sem avisar |
| `Refresh()` | 8 usos manuais (botões "atualizar") |
| `Concurrent()` | 7 usos; 5 envolvem escrita/exclusão sem ordem garantida |
| Coleções em memória | 23 (`col_itensApontados`, `col_anotacaoAudio`, `col_ZPASobstaculos`, `col_checkRespostasVE`, `col_veiculosEquipamenos`, caches de menu, relatórios, parâmetros) |

Contagem bruta de escritas por tela (`Patch` / `SubmitForm` / `Remove|RemoveIf`): frmHomePista 3/8/7, frmHomePatio 2/5/5, frmHomeTPS 2/5/5, frmHomeApont 0/4/2, frmInspPistaCad 8/2/6, frmCheckListGenericoEQP 10/1/2, frmVeiculos_Equipamentos 3/1/3, frmFormZPA 8 (6 comentados)/1/1, frmFormZPAeditar 1/1/1, frmFormZPAmenu 1 (coleção)/0/1, frmZPAapontamentos 0/1/1, frmHomeZPA 0/0/5.

### 2.2 Inventário por tela

**frmInspPistaCad (núcleo de Pista)**
- `FormInspPistaCad1_2` (629): `DataSource '7.4-tbl_InspPista'`; `OnFailure` (644) só notifica; `OnSuccess` (646, string de uma linha): `Clear(col_itensApontados); Clear(col_anotacaoAudio)` **antes** do `Patch` que grava `ID_pk` e `Protocolo = Upper(varIATAUser & "-INSP-PISTA-" & Self.LastSubmit.ID)` (2 round-trips obrigatórios). Gatilho `ButtonIniciar_3` (2341).
- `ButtonCanvas2_4` "Incluir Apontamento" (3719, Patch em 3742): grava na coleção local com `Location.Latitude/Longitude`, `Hash: Text(Now(),"yyyymmddhhmmss") & Text(Rand(),"[$-en-US]########")` e 3 fotos (`UploadedImage1_3/4/5.Image`); depois `Reset` dos 3 `AddMedia`.
- `Microphone1_1.OnStop` (3582): áudio vira base64 em `col_anotacaoAudio` (`Substitute(JSON(Microphone1_1.Audio, JSONFormat.IncludeBinaryData), Char(34), "")`).
- `ButtonCanvas5_27` normalizar (3920, Patch 3925): `Patch` em `'7.4.1-tbl_InspPistaItens'` e `RemoveIf` nas coleções locais sem verificar o resultado.
- `Button14_12` "Finalizar Inspeção em campo" (2381): muda a UI na 1ª instrução, `ForAll(col_anotacaoAudio, Patch(tbl_inspPistaAnotacao…))` (2437), define `var_statusInspecao`, `Select(ButtonCanvas3_2)` (2456).
- `ButtonCanvas3_2` "Salvar Todos" (4333, Patch 4342), dentro de `Container32` `Visible: =false`: `Patch('7.4.1-tbl_InspPistaItens', ForAll(col_itensApontados, {…}))` — sem identidade (sempre INSERT), `Hash` carregado mas não consultado, `Protocolo` com `Max(ID)` lido antes do lote (igual para todos), sem `OnFailure/Notify/retry`.
- `ButtonCanvas3` "Salvar" por linha (4440): `DisplayMode` (4444, fórmula sintaticamente quebrada), `Visible` (4501) e `OnSelect` (4459) fazem `LookUp('7.4.1-tbl_InspPistaItens', Hash = ThisItem.Hash)` — 2–3 consultas remotas por linha por render; offline retorna branco e o botão "habilita".
- `ButtonCanvas3_1` "Finalizar" (4522, Patch 4533): `Patch` do cabeçalho seguido de `Navigate(frmHomePista)` imediato — coleções morrem mesmo se o Patch falhar.
- `ButtonCanvas9_3` excluir apontamento (2235; Remove 2270/2274): `Remove(col_itensApontados, ThisItem); Remove('7.4.1-tbl_InspPistaItens', ThisItem)` — o 2º falha em silêncio se o item nunca subiu.

**frmHomePista**
- `FormInspPistaDetalhes` (1998): `Item: First(Filter(...))`; `OnSuccess` (2025) reseta e notifica; sem `OnFailure`; gatilho `Button1_27` (3291).
- `FormInspPistaItensDetalhes` (3788): `OnFailure` (3808) só notifica; `OnSuccess` (3809) encadeia `ForAll(col_ListaAnimais, Patch('AIRPORTNOW - FAUNA RELACIONAMENTO'…))` (3814), `Patch('7.4-tbl_InspPista', …, {Status:"Finalizado"})` (3848) quando `CountIf(GalleryInspPistaItensDetalhes.AllItems, Status="Pendente") = 1`, `RemoveIf(tbl_inspPistaAnotacao, ID_FK = Var_IDinspPistaInsert)` (3858, apaga áudios), `ResetForm` (3863).
- Forms de fauna: `FormInspPistaItensDetalhesColisao` (5499, `OnSuccess` 5517: `SubmitForm(FormInspPistaItensDetalhes)` + `NotifyFauna.Run` + `ResetForm`), `FormInspPistaItensDetalhesPRESENCA` (6946, 6955), `FormInspPistaItensDetalhesFOCO` (7786, 7802). Nenhum tem `OnFailure`. `ID_fauna` chega ao item por `Default: =var_idFormFauna` (5398-5399). Gatilho único `Button1_31` (8798, SubmitForms 8831-8836) via `Switch(var_tipoFauna…)`.
- `Patch(col_ListaAnimais…)` (9282) e `Remove(col_ListaAnimais, ThisItem)` (9421): só coleção.
- Exclusões: `Button1_28` (3302; 3317/3321) `RemoveIf(itens…); Remove(cabeçalho)` sem transação; `Button1_24` (8886; 8903).
- Relatório (1857-1888): `ForAll(... Remove(... LookUp(...)))` O(n·m), `'Criar-HTML'.Run(HtmlText3_5.HtmlText, …)`, `Launch(Substitute(LookUp(Documentos, ID = varIDhtmlCriado, Miniatura.Large), "thumbnail", "pdf"))`.

**frmHomeApont**
- `FormApontEdit` (1526): `Item: GalleryApontListagem.Selected`; sem `OnFailure`; gatilho 5946.
- Forms de fauna espelhados (`_1`): 2885, 4244, 5014; os 3 `OnSuccess` (2903/4259/5030) chamam `SubmitForm(FormInspPistaItensDetalhes)`, **form que só existe em frmHomePista:3788** — dispara de outra tela a cadeia com `Patch` de status do cabeçalho e `RemoveIf` de áudios avaliados no contexto da tela não visível.
- Exclusões: 6150/6155 (`Remove('7.4.1-tbl_InspPistaItens', GalleryApontListagem.Selected)`), 6292/6299 (`Remove('AIRPORTNOW - FAUNA RELACIONAMENTO', ThisItem)`).
- PDF: `ButtonCanvas4` (653, fluxo 663).

**frmHomePatio**
- `FormInspPatio` (1260): `Item: LookUp(tbl_inspPatio, ID = Var_IDinspPatio)`; `OnSuccess` (1276, Patch 1279) grava `Protocolo = varIATAUser & "-INSP-PAT-" & ID`; sem `OnFailure`; status via `Status_DataCard.Default = var_status` (1718). Gatilhos: 4069/4085 (Iniciar), 4115/4127-4128 (Finalizar), 4137/4148 (Salvar alteração).
- `FormInspPatioitens` (2110): sempre `NewForm`; FK `ID_insp` por `Default` (2883-2884); `OnSuccess` (2120, Patch 2121) grava `Protocolo -INSP-PAT-ITEM-`, notifica, `ResetForm` (2136). Gatilho 3111/3123; `NewForm` em 3907 e 4032. Anexos: `Anexos_DataCard15` (2694, `Attachments@2.3.0` em 2719) e `Anexos_DataCard1` (7388, 7416).
- `FormGerInspPatioitem` (6506): `Item: First(Filter(tbl_inspPatioItens, ID = var_idSelectItem))`; `OnSuccess` 6515; sem `OnFailure`; gatilho 7534/7546; entrada por `EditForm` em 5026/5044.
- Exclusões: 2024/2035 e 5488/5498 fecham o modal **antes** do `Remove` e notificam sucesso incondicional; cascata 4338-4344 `Concurrent(RemoveIf(itens), RemoveIf(pai))`.
- Relatório: `Collect/RemoveIf` em coleções (1049-1073); `ForAll(col_inspPatiomenu As MENU, ForAll(Filter(tbl_inspPatioItens, ID_insp = …)…))` (1021) faz 1 consulta por item do menu; fluxo 4882, `Launch` 4887.

**frmHomeTPS** (clone de Pátio): `FormInspTPS` 1211 (OnSuccess 1227, Patch 1230), `FormInspTPSitens` 1924 (FK 2383-2384, Patch 1935, `ResetForm` 1950), `FormGerInspTPSitem` 6051 (6066; gatilho 7093/7105), gatilhos do cabeçalho 3602/3618, 3648/3660-3661, 3670/3681, gatilho de item 2770, `Remove` 1850 e 5052/5062, cascata 3871-3877 `Concurrent`, fluxo 4419/4424. **Bugs de nome:** 3376-3388 `Filter(tbl_inspPatioItens, ID_insp = Var_IDinspTPS)`, 3400 `NewForm(FormInspPatioitens)`, 4896/4912 `EditForm(FormGerInspPatioitem)`, 6030/6046 `ResetForm(FormGerInspPatioitem)` — a tela TPS opera formulários e lista de Pátio.

**frmCheckListGenericoEQP**
- `FormCheckGenerico` (1121): `Item` comentado; FK `ID_FK` (1227-1228) e `Protocolo` (1286-1292) por `Default`; `OnSuccess` (1135, Patch 1150): fecha a UI, liga `var_limparChekList` e notifica "Salvo com sucesso" **antes** do `ForAll(col_checkRespostasVE, Patch(tbl_Checklist_generico_objeto…))`; `Foto: ThisRecord.Foto` está **comentada** (fotos nunca chegam ao SharePoint). Sem `OnFailure`.
- Gatilho `ButtonCanvas11_10` (2023; SubmitForm 2067): `var_protocoloVE` = `Max(ID) + 1` remoto (colisão em concorrência/offline).
- Patches em `col_checkRespostasVE`: 1884/1892, 1945/1953, 1992, 2134 ("Salvar Imagem" → `Foto: UploadedImage4.Image`).
- `ButtonCanvas40` normalizar (2436-2457): `Concurrent` com **dois Patches idênticos** em `tbl_Checklist_generico_objeto` + 1 na coleção.
- Cascata `ButtonCanvas12_9` (942/946): `RemoveIf(base)` **antes** de `RemoveIf(objeto)` — pai antes dos filhos.

**frmVeiculos_Equipamentos**
- `FormCadVeiEqui` (1174): `OnFailure` (1185) desliga spinner e notifica; `OnSuccess` (1188; Patches 1193/1204/1209) mantém cache espelho `col_veiculosEquipamenos` e grava `Protocolo -VEI-EQU-` em `Concurrent`; `ResetForm` (1220); gatilho 2434. Foto via `AddPicture20` (2082) no DataCard.
- Exclusões: 1017-1022 `Concurrent(RemoveIf(lista), RemoveIf(coleção))`; 1079 `RemoveIf(lista)` **sem** atualizar a coleção (cache fica desatualizado).

**ZPA**
- `frmFormZPA` `FormZpa` (127): `OnFailure` (134) só `UpdateContext({var_loadSave:false})`; `OnSuccess` (136): `Patch(tbl_inspZPAfotos, Defaults, {ID_FK, 6 LargeImage})` (137) + `ForAll(col_ZPASobstaculos, Patch(tbl_inspZPAitens, Defaults, {…Foto}))` (152) + `Navigate(frmHomeZPA)` + `Reset` dos 6 `AddMedia` + notify. Gatilho `ButtonCanvas1` (1978) valida as 6 mídias antes. Anexos: `Anexos_DataCard4` (1092, 1121). 6 blocos `Patch('7.5-tbl_InspZpa'…)` comentados (1313-1607).
- `frmFormZPAeditar` `FormZpaEdit` (122): `OnSuccess` (132, Patch 133) usa `Defaults(tbl_inspZPAfotos)` em modo edição → **novo registro de fotos a cada edição**, com imagens `ImageE1..D3` **de frmFormZPA**; `Form4` (1070) só exibe fotos; `Remove(tbl_inspZPAitens, Gallery5_2.Selected)` (1822); gatilho 1773.
- `frmFormZPAmenu`: `Patch(col_ZPASobstaculos…)` (1939, foto `UploadedImage1.Image`); `Remove` 978.
- `frmZPAapontamentos` `FormGerInspZpaItens` (1116): sem `OnFailure`; gatilho 2095; `Remove(tbl_inspZPAitens, var_gerItemExcluir)` 2149; **bugs de nome** 655/1111 (`FormGerInspPatioitem`), 1079 (`GalleryInspPatioitens`), 2163 (`Gallery5_2`).
- `frmHomeZPA`: cascata 1310/1314/1318 (itens → fotos → pai, sequencial, 3 chamadas); 1249-1254 `Concurrent(RemoveIf(tbl_inspTPSitens…), RemoveIf(tbl_inspTPS…))` — exclusão de **TPS** dentro da tela ZPA.

### 2.3 Uso de `Hash`/`hash`
8 ocorrências, todas em `frmInspPistaCad`: geração (3765), carga no lote (4369, nunca consultado), `DisplayMode` (4446-4449), `OnSelect` (4459), gravação (4488), `Visible` (4501). A coluna `hash` de `'7.4-tbl_InspPista'` existe no esquema e nunca é usada. As listas de Pátio, TPS, ZPA e Checklist não têm coluna de hash. Consequência: só o caminho item a item é idempotente, ao custo de 1 consulta remota por linha por render; o lote (que é o caminho automático) não é.

### 2.4 Mídia
- **AddMedia → `Image.Image` → coluna imagem via `Patch`** (padrão dominante): Pista (`AddMediaButton1_3/4/5` 3821/3844/3867 → `col_itensApontados` 3772-3774 → `'7.4.1-tbl_InspPistaItens'` 4377-4379/4489-4491); ZPA (`AddMediaButtonD3..E1` 1302-1597 → `tbl_inspZPAfotos` 137-146; editar 1117-1457 → 133-142; menu 1747 → `col_ZPASobstaculos` 1952 → `tbl_inspZPAitens` 160; apontamentos 1825); Checklist (`AddMediaButton4` 2116 → coleção 2134 → **nunca gravado**); Veículos (`AddPicture20` 2082 via DataCard); fauna (18 `AddMedia` em DataCards: frmHomePista 5100-8699, frmHomeApont 4081-5881; `Default` das imagens faz `LookUp('7.4.1-tbl_InspPistaItens', ID = …).Foto.Full` — download full-size a cada render, 6693/7532/8495).
- **Anexos nativos do SharePoint (`Attachments@2.3.0`)**: frmFormZPA 1092/1121; frmHomePatio 2694/2719 e 7388/7416; frmHomeTPS 2303/2330 e 7005/7033; cards de exibição de PDF com `MaxAttachments: =10` e `MaxAttachmentSize: =90` (frmHomePatio 6396, frmHomeTPS 5941). Só o runtime do formulário grava anexos; `Patch` não.
- **Microphone → base64 em coluna texto**: `Microphone1_1` (3570), `OnStop` 3582-3597, playback `Audio1_2` (~3648), gravação `frmInspPistaCad:2437` em `tbl_inspPistaAnotacao.Audio` (string).
- Não há `Camera`, `PenInput` nem barcode além do `BarcodeReader1` de Veículos (2472, `OnScan` 2476).

### 2.5 Location, Param, Launch
- `Location.Latitude/Longitude` só em `frmInspPistaCad:3735-3740` (gravado em 3753-3754 como texto); comentado em `App.pa.yaml:32-33`.
- `Param("USUARIO")` (`App.pa.yaml:168`, `frmHome:37`) e `Param("LOGADO")` (`frmHome:41`, token com data) só quando `Host.OSType = "Windows" And varControleIndex`; no mobile cai em `LookUp(User, Email = User().Email)`.
- `Launch()`: 13 usos — hub Airport Now (`frmHome:112, 125, 287, 1063, 1214`, app `a5af3add…`; app mobile de Pista `90a784ea…` em 287), PDF gerado (`frmHomeApont:668`, `frmHomePista:1879`, `frmHomePatio:4887`, `frmHomeTPS:4424`), anexos (`frmHomePatio:5163`, `frmHomeTPS:4614`, `frmZPAapontamentos:798`), QR externo `api.qrserver.com` (`frmVeiculos_Equipamentos:753`), Power BI (`ScreenConsultarV1:196-234`, tela morta).

### 2.6 As 8 sequências mais arriscadas
1. Finalizar inspeção de pista em campo (`frmInspPistaCad:2381 → 2437 → 4342`): UI muda, N áudios, M itens × 3 fotos, sem identidade, protocolo repetido, zero erro tratado.
2. Fauna → item → cabeçalho → delete de áudio (`frmHomePista:8798 → 5517 → 5531/5532 → 3809/3814/3848/3858`): 5 listas, 2 sites, 1 fluxo, 1 delete; e-mail já disparou se o item falhar.
3. ZPA "Finalizar Inspeção" (`frmFormZPA:1978 → 136-176`): 1 SubmitForm + 6 imagens + N itens com foto + `Navigate`; `OnFailure` não avisa; `col_ZPASobstaculos` some.
4. Checklist pai + N filhos (`frmCheckListGenericoEQP:2023 → 1135-1160`): "Salvo com sucesso" e limpeza antes dos filhos; `Max+1`.
5. Cabeçalho de Pista em 2 escritas (`frmInspPistaCad:2355 → 646`): coleções limpas antes; falha no 2º Patch deixa inspeção sem `Protocolo`/`ID_pk` (a busca e o relatório dependem do protocolo).
6. "Finalizar" pós-sincronização (`frmInspPistaCad:4522-4546`): `Navigate` roda mesmo se o Patch falhar.
7. Exclusões em cascata: `frmHomePista:3317/3321` (ordem certa, sem transação), `frmHomeZPA:1310-1318` (3 chamadas), `frmHomePatio:4338-4344`/`frmHomeTPS:3871-3877` (`Concurrent`), `frmCheckListGenericoEQP:942/946` (pai antes dos filhos).
8. Fauna disparada de `frmHomeApont` submetendo form de `frmHomePista` (2903/4259/5030): escrita fantasma no cabeçalho.

### 2.7 UI limpa/resetada antes de confirmar a gravação (15)
`frmInspPistaCad:646` (Clear das coleções antes do Patch), `:2381` (UI muda na 1ª instrução), `:3786-3789` (Reset dos AddMedia com foto só na coleção), `:4537-4546` (Navigate após Patch), `:3929-3960` (RemoveIf local sem verificar), `:2270-2277` (remove local antes do remoto); `frmCheckListGenericoEQP:1135-1148` (fecha form e notifica antes dos filhos), `:2219-2229` (descarta respostas ao abrir novo checklist); `frmFormZPA:151-176` e `frmFormZPAeditar:146-152` (Navigate/Reset no mesmo OnSuccess dos Patches); `frmHomePatio:2024-2040`, `:5490-5504`/`frmHomeTPS:5052-5070` (modal fecha antes do delete, sucesso incondicional); `frmHomePatio:4328-4350`/`frmHomeTPS`/`frmHomeZPA:1240-1262` (volta à listagem antes do delete); `frmHomeZPA:207-218` (descarta obstáculos); `frmHomePista:5542/6958/7805` e `frmHomeApont:2904/4260/5031` (`ResetForm` após `SubmitForm` assíncrono do pai).

### 2.8 Perfil dos dados lidos
Listas com colunas pesadas: `'7.4.1-tbl_InspPistaItens'` (39 colunas visíveis, 3 `LargeImage`, `Apontamento/Foto*` não filtráveis nem ordenáveis, `isOnlyServerPagable`), `tbl_inspPistaAnotacao` (`Audio` base64 em texto), `tbl_inspZPAfotos` (6 `LargeImage`), `tbl_Checklist_generico_objeto` (6 `LargeImage`), `tbl_inspZPAitens`/`tbl_Veiculos_equipamentos`/`tbl_inspMenu` (1 `LargeImage`). Cabeçalhos (`'7.4-tbl_InspPista'`, `tbl_inspPatio`, `tbl_inspTPS`, `tbl_inspZpa`, `tbl_Checklist_generico_base`) são leves (19-29 colunas de texto/data).
Galerias com teto (`FirstN(..., txtLimit)`): as 5 listagens-mestre. **Sem teto:** `frmHomePista:3561` (itens da inspeção, 3 imagens/linha), `:3496` (áudios base64), `frmHomePatio:2044`, `frmHomeTPS:1860`, `frmZPAapontamentos:530` (3º ramo, `Foto` por linha), `frmFormZPAeditar:1624`, `frmRelatorioZPA:744` (6 imagens), `frmCheckListGenericoEQP:2149`. Cache "grátis" já existente: `colAeros` (17 literais), `col_parametrosAnimais` (89 literais), menus por `inspecao`, `col_veiculosEquipamenos` (lista inteira), `col_userNotifyCriticidade` (lista inteira), `col_itensPouso/Taxi/Aids` (`frmHomePista:1250`, 3 downloads com imagens do ano corrente), reidratação `frmHomePista:1701`.

## 3. Performance e peso

### 3.1 App Checker (regras `app-*`, 187 resultados)
| Regra | Qtde | Onde |
|---|---|---|
| ScreenHasManyControls | 6 | frmHomePista 602, frmHomePatio 469, frmHomeApont 451, frmHomeTPS 439, frmApontFauna 319, frmInspPistaCad 229 (65,8% do app) |
| UnusedVariables | 60 | App 5 (`varEmailUser`, `varFuncaoUser`, `var_idItensZPA`, `var_ultimaVersao`, `var_usuarioID`), frmHomePista 12 (OnHidden 22-39), frmHome 9, frmHomeZPA 8, frmHomePatio 5, frmHomeTPS 5 (mesmos nomes), frmInspPistaCad 4, frmFormZPAmenu 2, frmFormZPAeditar 2, frmVeiculos 2, frmRelatorioVistoVeic 2, frmCheckList 1, ScreenConsultarV1 1 |
| InefficientDelayLoading | 20 | `MainContainerListar.Width` (frmHomePatio:369, frmHomeTPS:366, frmHomeZPA:385, frmVeiculos:254, frmCheckList:307, frmInspPistaCad:3982); `MainContainerListarApont.Width` (frmHomePatio:4446/4556, frmHomeTPS:3979/4089, frmZPAapontamentos:96/206); `CountRows(GalleryApontListagem.AllItems)` de outra tela (frmHomePatio:4608, frmHomeTPS:4109, frmZPAapontamentos:258); `Icon28_195.HoverColor` (frmHomePista:1651/1751/1812); frmZPAapontamentos:1079/2163 |
| CrossScreenEventDependencies | 15 | ver 3.10 |
| CountRowsGalleryAllItems | 14 | frmHomeApont:338/364, frmHomePatio:4608/5933/3791, frmHomeTPS:4109/5665/3434, frmZPAapontamentos:258, frmHomePista (Label13), frmInspPistaCad (Label1_51), frmFormZPAmenu (Label67_6), ScreenConsultarV1 ×2 |
| SuggestRemoteExecutionHint (+4 variantes) | 24 | `App.pa.yaml:25` `Max(tbl_controle_versoes)`; `frmHomePista:1234` `Year(Criado)` ×3; `Search` em frmHomePista:1401, frmHomePatio:703, frmHomeTPS:687; `GalleryCLG.Items` frmCheckList:620 e `:761` |
| CollectingReadOnlyTable | 9 | `App:35` colAeros; `frmHomePista:42/51`; `frmHomePatio:21`; `frmHomeTPS:15`; `frmHomeZPA:16/23`; `frmCheckList:481`; `frmHomePista:1812` |
| ForAllWithMutation | 7 | frmHomePatio:1021, frmHomeTPS:972, frmHomePista:1812 e 3789, frmFormZPA:127, frmCheckList:1121, frmInspPistaCad:2382 |
| TextInputIsNotDelayOutput | 3 | txtLimitApont (frmHomeApont:306), txtLimitApont_1 (frmHomePatio:4576), txtLimitApont_2 (frmHomeTPS:4135); **nenhum** dos 17 `txtLimit*`/`txtBuscar*` vivos tem `DelayOutput` |
| CollectDelegatableDataSource | 2 | `ClearCollect(col_userNotifyCriticidade, tbl_userNotify)` (frmVeiculos:17, frmCheckList:493) |
| NumericPropertySizeWarning | 2 | `DataCardValueAnexo_8/_9` (`MaxAttachmentSize 90` × `MaxAttachments 10`) |
| DataSourceDefaultMaxRowsLimit | 1 | 2000 |
| UnusedMediaResources | 23 | ver 3.7 |

### 3.2 Consultas SharePoint dentro de templates de galeria (1 requisição por linha renderizada)
| Controle | Local | Fórmula |
|---|---|---|
| `HtmlText1_22` | frmHomeApont:1250 | `Switch(ThisItem.sIten, … LookUp('AIRPORTNOW - Colisões…', ID = ThisItem.ID_fauna)…)` — 7 ramos, 3 listas |
| `HtmlText1_3` (oculto) | frmHomeApont:965 | `LookUp('7.4-tbl_InspPista', ID = ThisItem.IdInsp, Protocolo)` |
| `Icon28_209.DisplayMode` | frmHomePista:1751 | `LookUp('7.4.1-tbl_InspPistaItens', IdInsp = ThisItem.ID, ID) > 0 And …` |
| `ButtonCanvas39_1/3/4.Visible` | frmHomePatio:921, frmHomeTPS:872, frmHomeZPA:905 | `First(Filter(itens, ID_insp = ThisItem.ID)).ID > 0` |
| `HtmlText1_45`, `HtmlText1_72` | frmHomePatio:5225, frmHomeTPS:4666 | `LookUp(cabeçalho, ID = ThisItem.ID_insp, Protocolo)` |
| `Label19_158.Text` | frmCheckList:707 | `LookUp(objeto, … ID_item_classe = LookUp(classe, Item = "Estado geral", ID), Resposta)` — 2 listas |
| `ButtonCanvas7_17.FontColor` | frmCheckList:761 | `LookUp(Filter(objeto, ID_checkList = ThisItem.ID), Resposta = "Não conforme" And Status <> "Normalizado")` |
| `ButtonCanvas34/_1.DisplayMode` | frmHomePatio:4002, frmHomeTPS:3370 | `LookUp(Filter(itens, ID_insp = Var_IDinsp…), 'ID_item (ID_item0)' = ThisItem.ID)` — o `Filter` é invariante |
| `ButtonCanvas3.Visible/DisplayMode` | frmInspPistaCad:4441/4501 | 2 `LookUp` por `Hash` (coluna sem índice) |
| `Label20/_1.Text` | frmCheckList:2387, frmRelatorioVistoVeic:474 | `LookUp(classe, ID = ThisItem.ID_item_classe, Item)` |
Fora de galeria: 9 `Foto_DataCard*.Default = LookUp('7.4.1-tbl_InspPistaItens', ID = GalleryInspPistaItensDetalhes.Selected.ID).Foto.Full` (frmHomePista:6689, 6775, 6861, 7528, 7615, 7701, 8491, 8577, 8663); `Label10.Fill` (frmHomePista:1966) consulta lista para pintar fundo; `CountRows(Filter(Sort(col…)))` em `Button1*.Text` (frmInspPistaCad:2683/2820/2957/3139/3338); `Item` de forms com `First(Filter(T, ID = x))` (frmHomePista:1999/3789/5500/7787, frmHomePatio:6507, frmHomeTPS:6052).

### 3.3 Delegação
- Galerias-mestre: `FirstN(Search(Sort(Filter(lista, (IsBlank(cmb)||StartsWith(...)) && … && Data >= … && Data <= …), ID, Desc), txt, Protocolo, Usuario), Value(txtLimit.Text))` — `Search` não delega; o `FirstN` age sobre as 2000 primeiras linhas por ID (registros novos nunca aparecem quando a lista passa de 2000). frmHomePista:1401 (limite 10), frmHomePatio:703 (`If(Host.OSType="Windows",100,10)`), frmHomeTPS:687 (sem guardas `IsBlank`), frmHomeZPA:706 (`Sort` duplo + `Last(Split(...))` no filtro), frmHomeApont:693 (6 pares `IsBlank||StartsWith`, limite 100), frmHomePatio:4912/frmHomeTPS:4461 (`If()` dentro do `Filter`), frmZPAapontamentos:530 (**sem `FirstN`**), frmCheckListGenericoEQP:620 (`LookUp(Filter(objeto…))` por registro da base + `AddColumns(... First(SortByColumns(Filter(Sort(veículos)))))` por linha — N+1 duplo).
- `frmHomePista:1247-1283` (refresh): 3 × `Filter(Sort(SP), … Year(Criado) = Year(Today()))` → 3 downloads completos com todas as colunas.
- Dropdowns: `ForAll(Distinct(Filter(colAeros, Bloco = cmb.Selected.Value), Aeroporto), {Result: ThisRecord.Value})` ×9 (memória, ok); `Distinct('7.4.1-tbl_InspPistaItens', Local)` e derivados em bloco oculto (frmHomeApont:6008/6055/6104); ~40 `Choices([@lista].coluna)` nos 3 forms de fauna × 3 cópias; listas de hora/minuto inline ×8 pares.
- `frmHomePista:5520` `Concat(Filter(tbl_userNotify, … Or …), EMAIL_USER, "; ")` com `Or` + coluna Choice: não delegável (a lista já está em `col_userNotifyCriticidade`).

### 3.4 OnVisible / OnStart / OnSelect pesados
- `frmHomePista.OnVisible` (40-499): 459 linhas; `col_inspPistaMenu` (1 GET) e `col_parametrosAnimais` com 89 registros literais (451 linhas) usados só em 9095/9115/9132.
- `App.OnStart` (11-228): `Max(tbl_controle_versoes, Numero_versao)` não delegável para `var_ultimaVersao` não usada (25); `colAeros` 18 literais (35-163); `LookUp(User…)` em 169, 179 e 184 (3 GETs onde 1 basta).
- `Icon28_208.OnSelect` relatório de Pista (1812-1893): `ForAll + Remove + LookUp` O(n·m).
- Relatório de Pátio/TPS (frmHomePatio:1021-1075, frmHomeTPS:972-1030): `Filter(SP)` dentro de `ForAll` externo → 1 GET por item do menu.
- `frmVeiculos:16-17` e `frmCheckList:16` chamam `Select(botão)` no OnVisible → `ClearCollect` de `tbl_userNotify` inteira e (perfis não-Base) `tbl_Veiculos_equipamentos` inteira ordenada a cada entrada.

### 3.5 Relatórios HTML (4 `HtmlViewer` `Visible: =false`, sempre avaliados)
| Viewer | Local | Chars | Origem | Gatilho |
|---|---|---|---|---|
| `HtmlText3` | frmHomeApont:6340 | 6.203 | `Concat(Filter('7.4.1-tbl_InspPistaItens'…))` (mesmo filtro da galeria) com `If(... 3 LookUp em 3 listas de fauna por linha)` | `ButtonCanvas4` 664 |
| `HtmlText3_5` | frmHomePista:9476 | 3.864 | `Concat` sobre `col_relatorioPista*` | `Icon28_208` 1873 |
| `HtmlText3_1` | frmHomePatio:7564 | 3.804 | `Concat` sobre `col_relatorioPatio*` | 4883 |
| `HtmlText3_4` | frmHomeTPS:7123 | 3.797 | idem | 4420 |
Como `HtmlText` é declarativo e depende de combos/datas/limite, é recalculado a cada mudança de filtro (e a cada tecla, sem `DelayOutput`) — até 100 GETs extras em Apontamentos mesmo sem ninguém pedir PDF.

### 3.6 Duplicação estrutural
| Par | Similaridade (linhas comuns após normalizar sufixos) |
|---|---|
| frmHomePatio × frmHomeTPS | 0,759 |
| frmFormZPA × frmFormZPAeditar | 0,633 |
| frmRelatorioZPA × frmRelatorioZPA_1 | 0,619 |
| frmHomePista × frmHomeApont | 0,572 |
Forms de fauna: Colisão 128/120/117 controles, Presença 71/70/67, Focos 54/80/77 em frmApontFauna (morta)/frmHomePista/frmHomeApont = 784 controles (20,6%); 34 `TypedDataCard` byte a byte idênticos entre frmHomeApont e frmHomePista. Containers repetidos: `ContainerHeader*` 20× em 16 telas, `ContainerFilterPista*` 6×, `Container33*` 6× (3 idênticos), `ContainerFormNaoConform` 3×, `MainContainerGerNaoConf` 3×, `ContainerInspPatiocad1` 7×, `FooterContainer1` 12×. Redundância total estimada ≈ 1.487 controles (39%).

### 3.7 Peso morto
- 117 raízes `Visible: =false` arrastando 248 filhos = 365 controles (9,6%): os 4 `HtmlText3*`, `PdfViewer3/_1` (frmHomePatio:7555, frmHomeTPS:7114), `NavInspecao_1`/`LinkAirportNow_1`/`NavMob_1` (frmHome:1046/1058/1071), bloco `ContainerFiltarApontExcluir` (frmHomeApont:5983-6104), `HtmlText1_3/_4/_7/_14` ocultos dentro de template (frmHomeApont:965/987/1056/1108), `Container12` (frmHomePista:1492, só `TemplateSize`), 18 `Circle1_*` (frmHomePatio:3291-3992, frmHomeTPS:2876-3496, frmFormZPAmenu:202-675), ~70 `TypedDataCard` ocultos técnicos (ID, Protocolo, Bloco, IATA, Aeroporto, Status — **necessários** para `Form.Updates`).
- Telas mortas sem nenhuma referência (só em `_EditorState.pa.yaml:15,16,23,27`): frmApontFauna (319), ScreenConsultarV1 (22, links Power BI), frmRelatorioZPA_1 (88, `ID = 1436` fixo), Screen1 (0). Total 429 controles.
- Mídia não usada (2.108.589 B): `notificacao` 1.149.541, `Loading_41` 269.744, `check-icone-1-scaled` 267.567, `gifBlue` 107.446, `MOTIVA_RGB_Logo_VersaoPositiva_Anil` 91.781, `LogoZPA` 56.144 (o usado é `logoZPA`), `marca`, `200w`, 5 "Captura de tela", `LogoAN`, `camera1-6`, `BDV`, `areaExternas`, `pistaMenu`, `SamplePdf`, `SampleAudio`.
- Fontes conectadas sem uso em tela viva: `tblInspMenu`, `tbl_bdv`, `UsuáriosdoOffice365` (0 refs), `'7.5-tbl_InspZpa'`, `'7.5-tbl_InspZpaItens'` (só comentários e frmRelatorioZPA_1).

### 3.8 `Host.OSType` (30 usos)
frmHomePista 10 (732, 786, 844, 876, 978, 1094 `DefaultDate` 7 dias × 1 dia, 1488 aviso "Ações não disponível no Tablet", 1624, 1732, 1793), frmHome 5 (34, 111, 282 + 2 comentados), frmHomePatio 5 (298, 387, 396 `txtLimit` 100/10, 503), frmHomeTPS 4, frmHomeZPA 4, frmVeiculos 2, frmCheckList 2, frmInspPistaCad 2. `Visible = Host.OSType = "Windows"` não impede a avaliação das fórmulas dos filhos: `Icon28_209.DisplayMode` (1751) consulta a lista por linha mesmo no tablet, onde o ícone está oculto.

### 3.9 Fórmulas repetidas (candidatas a `App.Formulas`)
`If(varPerfilUser = "Base" Or varPerfilUser = "Bloco", DisplayMode.Disabled, DisplayMode.Edit)` ×12; `If(varPerfilUser = "Base", …)` ×12; bloco padrão por perfil ×10; `ForAll(Distinct(Filter(colAeros…)))` ×9; validação "não permite mais de 2.000 itens" (247 chars) ×10; contador "Itens apontados na inspeção" ×4 (3 cross-screen); hora/minuto ×8 pares; `UpdateContext({varLocal…})` + `ColorFade` ×12+12; cor por `Status` ×13; `Switch(Status, "Em andamento"…)` ×3; `UpdateContext({var_imagePendente…})` ×12; `DataSourceInfo(...)` dezenas nos 3 forms de fauna; 218 `ErrorMessage*.Visible` e 44 `AccessibleLabel` gerados pelo Studio (não mexer).

### 3.10 Dependências entre telas (com `delayloadscreens`, cada uma carrega a outra tela inteira)
frmHomePatio → frmHomePista (369), frmHomeApont (4446/4556/4608); frmHomeTPS → frmHomePista (366), frmHomeApont (3979/4089/4109), **frmHomePatio (3370 `FormInspPatioitens`, 4896/6030 `FormGerInspPatioitem`)**; frmHomeZPA → frmHomePista (385), **frmFormZPA (196 `FormZpa` + 6 `AddMediaButton*`), frmFormZPAeditar (949), frmHomeTPS (862 `FormInspTPS`)**; frmHomePista → **frmInspPistaCad (684/1651 `FormInspPistaCad1_2`)**, frmHomePatio (1651/1751/1812 `HoverColor`); **frmHomeApont → frmHomePista (2886/4245/5015 `SubmitForm(FormInspPistaItensDetalhes)`)**; frmZPAapontamentos → frmHomeApont (96/206/258), **frmHomePatio (633/1095/1079), frmFormZPAeditar (2163)**; frmVeiculos → frmHomePista (254), **frmFormZPA (168 `AddMediaButton*`)**; frmCheckList → frmHomePista (307); frmInspPistaCad → frmHomePista (3982); **frmFormZPAeditar → frmFormZPA (122 `ImageD1..E3`)**. Em negrito os 15 `CrossScreenEventDependencies`. Efeito: frmHomePista é puxada por 6 telas e frmHomeApont por 3; abrir ZPA carrega TPS, que carrega Pátio, que carrega Pista e Apontamentos.

### 3.11 Ranking de impacto
1. `GalleryApontListagem` (33 controles/linha, 17 HtmlViewers/linha, 2 com LookUp SP, limite 100). 2. Dependências entre telas anulam o delay-load. 3. `frmHomePista.OnVisible` 459 linhas. 4. 4 relatórios HTML sempre avaliados. 5. 4 telas mortas (−429). 6. TPS clone de Pátio (−437). 7. Fauna triplicada (−261 a −505). 8. `GalleryCLG.Items` N+1 duplo. 9. 2,0 MB de mídia inútil no cold start. 10. 12 consultas por linha em Visible/DisplayMode/Text. 11. `ForAll` com `Filter(SP)` interno nos relatórios de Pátio/TPS. 12. `Search` + ausência de `DelayOutput`. 13. 365 controles invisíveis. 14. `sharepointselectsenabled=false` + 2000 linhas. 15. 60 variáveis mortas + 5 fontes sem uso. 16. Sem `App.Formulas`. 17. OnStart com 3 `LookUp(User)` + `Max`. 18. `Host.OSType` ×30 sem curto-circuito.

## 4. Bugs funcionais consolidados
| # | Onde | Bug | Efeito |
|---|---|---|---|
| F1 | frmInspPistaCad:4342 | "Salvar Todos" sem identidade e sem verificação | reexecução duplica itens; falha silenciosa parcial |
| F2 | frmInspPistaCad:3765 | `Hash` gerado com máscara inteira sobre fração | chave vazia/`"0"` → colisão no mesmo segundo |
| F3 | frmInspPistaCad:4342 | Protocolo do lote com `Max(ID)` congelado | todos os itens do lote com o mesmo protocolo |
| F4 | frmInspPistaCad:4444 | `DisplayMode` com fórmula sintaticamente quebrada | ramo inalcançável |
| F5 | frmHomeApont:2903/4259/5030 | `SubmitForm` de form de outra tela | escrita fantasma no cabeçalho de Pista |
| F6 | frmHomeTPS:3376-3400, 4896, 6030 | TPS usa forms/lista de Pátio | "já lançado" sempre habilitado; `NewForm` não reseta o form TPS |
| F7 | frmZPAapontamentos:655/1111/1079/2163 | ZPA usa form/galerias de Pátio | normalização/labels sobre a tela errada |
| F8 | frmFormZPAeditar:133 | `Patch(Defaults)` em fotos ao editar, com imagens de frmFormZPA | registro de fotos duplicado a cada edição |
| F9 | frmCheckListGenericoEQP:1158 | `Foto` comentada no OnSuccess | fotos do checklist nunca gravadas |
| F10 | frmCheckListGenericoEQP:2436-2457 | dois `Patch` idênticos em `Concurrent` | escrita dobrada |
| F11 | frmCheckListGenericoEQP:942/946 | cascata apaga pai antes dos filhos | órfãos permanentes se cair no meio |
| F12 | frmCheckListGenericoEQP:2052-2064 | protocolo `Max(ID)+1` remoto | colisão em concorrência/offline |
| F13 | frmHomePatio:4338, frmHomeTPS:3871, frmHomeZPA:1249 | `Concurrent(RemoveIf filhos, RemoveIf pai)` | ordem indefinida |
| F14 | frmHomeZPA:1249-1254 | exclusão de TPS dentro da tela ZPA | alvo incoerente (a confirmar com o usuário) |
| F15 | frmVeiculos_Equipamentos:1079 | `RemoveIf(lista)` sem atualizar `col_veiculosEquipamenos` | cache desatualizado até refresh |
| F16 | frmHomePatio/TPS contadores (4608/4109), frmZPAapontamentos:258/1079/2163 | leem galeria/seleção de outra tela | número/protocolo exibidos errados |
| F17 | App.pa.yaml:25 | `Max(tbl_controle_versoes)` para variável não usada | consulta inútil a cada abertura |
| F18 | 14 forms | sem `OnFailure` | falha de gravação invisível |
| F19 | frmHomePista:5532 | `NotifyFauna.Run` antes de confirmar o item | e-mail enviado para registro que pode não existir |
| F20 | frmHomePista:3858 | `RemoveIf(tbl_inspPistaAnotacao)` no OnSuccess do item | áudios apagados sem confirmação |
| F21 | frmInspPistaCad:4342/4462 × app mobile | protocolo de item `IATA-INSP_PISTA_ITEM-<maior ID>` aqui, `IATA-INSP-PISTA-ITEM-<ID>` no app mobile de Pista (mesma lista) | dois formatos na mesma coluna; busca e conferência por protocolo quebram — ver `../Inspeção de Pista/AUDITORIA.md` |

## 5. Fatos de plataforma verificados (docs Microsoft, consultados em 2026-09-16)
- `SaveData/LoadData/ClearData`: sem limite fixo em Power Apps Mobile (iOS/Android/Windows nativo), memória prática 30–70 MB; 1 MB em navegador e Teams; não funcionam no Studio; dados em navegador não são criptografados. Canvas apps em navegador não rodam offline.
- Imagens de `AddMedia`/`Camera` são blobs que não sobrevivem a `SaveData`: converter com `Substitute(JSON(img, JSONFormat.IncludeBinaryData), """", "")` e exibir pelo data URI.
- Microsoft recomenda `App.Formulas` no lugar de `App.OnStart` (avaliação preguiçosa), evitar `ClearCollect` de listas grandes, `Concurrent` com moderação, primeira tela sem dependências, remover telas e mídia sem uso, manter referências entre telas baixas; `SaveData/LoadData` só para dados pequenos (por isso o escopo "em andamento").
- No repositório não existe precedente de offline; `Timer@2.1.0` e instância `Control: CanvasComponent`/`ComponentName` existem em exports de outros projetos (`Mapa de Alocação/scrMapaPatio.pa.yaml:771`, `Gestão de Chamados/ScreenMeusChamados.pa.yaml:74`); `AccessAppScope` e a chave `Formulas:` no `App.pa.yaml` não têm precedente e exigem sonda.

## 6. O que fazer
Ver o plano aprovado (fases 0–6). Em uma linha: primeiro tornar o app leve sem tocar no layout (dependências entre telas, delegação, consultas por linha, `App.Formulas`, relatórios sob demanda, bugs F4–F18), depois trocar toda escrita direta por uma fila local idempotente (chave em `Title`) sincronizada por um componente com Timer presente em todas as telas, módulo a módulo (Pátio/TPS → ZPA → Veículos/Checklist → Pista/Fauna).
