# Entrega — Airport Now · Inspeção de Pista (app mobile) — correções rápidas + tela de sondas

Origem: `AirportNow-InspeçãodePista_20260916202747.zip` (publicado em 14/09/2026), 2 telas, 269 controles, tablet 1366×768.
Gerado por `build/entregar.sh` em 2026-09-17. Auditoria em `../AUDITORIA.md` (achados M1–M14, L1–L8); plano em `~/.claude/plans/fa-a-a-auditoria-completa-glittery-sonnet.md`, adendo de 2026-09-17.

**O que esta entrega resolve**: o envio passa a ser idempotente (repetir não duplica) e o "Finalizar" deixa de apagar apontamentos que não chegaram ao SharePoint. "Cadastrar", "Continuar" e a volta ao hub pedem um segundo toque antes de descartar apontamentos não enviados. "Continuar" carrega a inspeção certa.

**O que ela ainda NÃO resolve**: os apontamentos continuam só na memória do aparelho até o envio. Se o app for fechado, o tablet reiniciar ou a bateria acabar antes do envio, eles se perdem, como hoje. Guardar no aparelho (`SaveData`) é a fase offline, que depende das sondas da seção 6.

**Nada mais que o usuário vê mudou**, fora o que está na seção 3. A trava de layout comparou os 242 controles de `frmInspPistaMob` antes e depois; as únicas diferenças são as 3 exceções declaradas.

## 1. Ordem de aplicação

Publicar fora do horário de inspeção: quem estiver com uma inspeção aberta perde o que não enviou quando o app reiniciar na versão nova (é o comportamento de hoje).

1. **Limite de linhas** — Studio → Configurações → Geral → **Limite de linhas de dados**: 500 → **2000** (é o valor do app principal). Sem isso, as não conformidades do ano continuam limitadas a 500 registros (L1).
2. **Tela** — `frmInspPistaMob` → **Exibição de código** → selecionar tudo → colar `03_frmInspPistaMob.pa.yaml` → confirmar. Conferir o painel de erros.
3. **App.OnStart** — App → propriedade **OnStart** → colar `01_App_OnStart_ptBR.txt` inteiro. (`01_App.pa.yaml` é o mesmo conteúdo no formato invariante, só para referência — **não** colar os dois.)
4. **Salvar → testar (seção 5) → Publicar → Exportar** e me devolver o zip. O reexport vira a origem da fase offline.

| Arquivo | Destino | Cirurgias |
|---|---|---|
| 03_frmInspPistaMob.pa.yaml | tela `frmInspPistaMob` | Q1, Q2, Q3, Q4, Q5, Q6, Q7 |
| 01_App_OnStart_ptBR.txt | App.OnStart (barra de fórmulas, pt-BR) | Q8 |
| 01_App.pa.yaml | referência (invariante) | Q8 |
| 90_scrSondaOffline.pa.yaml | **só numa CÓPIA do app** (seção 6) | — |

`ScreenLogin` não mudou (inalcançável; ver seção 4).

## 2. O que mudou

| Id | Controle | O quê |
|---|---|---|
| Q1 | `ButtonCanvasSalvarTodos.OnSelect` (envio) | Cada passo confere o servidor antes de gravar. O cabeçalho é procurado pelo `hash` antes de ser criado; o da inspeção continuada é lido pelo ID. `ID_pk` e `Protocolo` só são gravados se estiverem em branco. Cada item só é criado se o `Hash` não existir. O protocolo `IATA-INSP-PISTA-ITEM-<ID>` só vai nos itens que ainda não têm. Só os áudios desta inspeção são enviados, e só os que faltam: como a lista de áudios não tem chave, um áudio já enviado é reconhecido por local, item, subitem e tamanho. No fim, o envio relê os itens e os áudios no servidor. `var_envioOk` só fica verdadeiro sem erro, sem item faltando, sem protocolo em branco e sem áudio faltando. Se não, aparece "Nem tudo foi enviado: <motivo>". Todo `Patch` de cabeçalho está em `IsError`. Some a conferência por `CountRows(FirstN(…100))`, que prendia o spinner (M4, M10, M14). |
| Q2 | `ButtonCanvas3_5.OnSelect` ("Finalizar" do painel) | Com o envio confirmado, atualiza o status (Pendente/Finalizado) na lista local e no SharePoint e só então limpa o aparelho; se o status falhar, avisa e mantém a inspeção "Em andamento" para ser continuada. Sem confirmação e com conexão: avisa e **reenvia**. Sem conexão: avisa e **não apaga nada** (M2). |
| Q2 | `Icon10_1.OnSelect` (fechar o painel) | Com o envio confirmado, igual a antes (volta à lista). Sem confirmação: volta ao passo 1 **desta** inspeção, onde "Finalizar Inspeção" reenvia (antes ia para a lista e os apontamentos ficavam inalcançáveis). |
| Q3 | `ButtonCanvas2_6.OnSelect` ("Incluir Apontamento") | `Hash` = `aaaammddhhmmss-<ID do usuário>-<6 dígitos>`. Antes, a máscara `"########"` sobre `Rand()` devolvia no máximo 1 dígito: dois apontamentos no mesmo segundo tinham o mesmo `Hash` (M5). |
| Q4 | `Icon28_214.OnSelect` ("Cadastrar"), `Icon1_18.OnSelect` (voltar ao hub) | Com apontamento, cabeçalho novo ou áudio ainda não enviados, o 1º toque só avisa; o 2º toque em até 10 s descarta (M8, M9). "Cadastrar" zera também o estado do envio. |
| Q5 | `ButtonCanvas9.OnSelect` ("Continuar") | Mesmo aviso de descarte. Carrega o `hash` da inspeção escolhida (ou gera um, se ela não tiver), põe no buffer só essa inspeção e traz os itens dela do servidor já com o `hash` — aparecem no resumo como "Salvo" e o envio não os recria. Antes: formulário com a inspeção errada, itens do servidor duplicados e cabeçalho novo (M7). |
| Q6 | `Gallery13_12.Items` (passo "Item") | Lê `col_inspPistaMenu`, já carregada ao abrir a tela, como o passo "Categoria" já fazia. Antes consultava `tbl_inspMenu` no SharePoint a cada toque (L2). |
| Q7 | `Label12_3.Text` (status por item no painel) | "Salvo" quando o item tem ID/protocolo ou quando o envio o confirmou no servidor; sem consulta por linha (antes 1 `LookUp` por item, e "Salvo" podia aparecer para item não enviado por causa do `Hash` repetido) (L3, M5). |
| Q7 | `ButtonCanvas3_4.Visible` / `DisplayMode` ("Salvar manual") | `false` / `Disabled` fixos. Nunca ficava visível (exigia `Protocolo`, que o buffer não tem) e gravaria item sem inspeção se aparecesse; saem 2 consultas por linha (M13, L3). |
| Q7 | `TextCanvas2_2.Text` (texto do painel) | Mostra "Falha no envio: <motivo>" quando o envio falhou; senão "Conectado"/"Não Conectado" como antes. |
| Q8 | `App.OnStart` | `Year(Criado) = Year(Today())` → `Criado >= Date(Year(Today()), 1, 1)` nos 3 filtros de não conformidades (delegável; antes só as 500 primeiras linhas da lista, de todos os aeroportos, eram avaliadas no aparelho) (L1). |

## 3. Mudanças que o usuário PODE notar

1. **Aviso de descarte**: "Cadastrar", "Continuar" e o ícone de voltar ao hub, com apontamentos não enviados, mostram "Há uma inspeção com apontamentos que ainda não foram enviados neste aparelho. Toque de novo em até 10 segundos para descartá-la." Sem apontamento pendente, funcionam como antes, num toque só.
2. **"Finalizar" sem envio confirmado**: com sinal, avisa "Tentando enviar de novo…" e reenvia; depois que os itens aparecerem como "Salvo", tocar em "Finalizar" de novo. Sem sinal, mostra "Sem conexão: os apontamentos continuam neste aparelho…" e **não limpa** (antes limpava).
3. **Fechar o painel sem envio confirmado** volta ao passo 1 da mesma inspeção, e não à lista.
4. **Painel de envio** mostra "Falha no envio: …" quando algo não subiu.
5. **Contadores de não conformidade** por local (Pista de Pouso, Pista de taxi, NAV AIDS) e a lista de normalização passam a mostrar as do ano do aeroporto do usuário. Os números podem **subir**: antes, as mais novas ficavam fora.
6. **"Continuar"** abre a inspeção escolhida com os apontamentos já gravados no resumo.
7. **Formato do `Hash`** dos apontamentos novos (não aparece na tela; só na lista): `20260917143015-12-048213`.

## 4. Decisões que dependem de você

Da auditoria (seção 9), nenhuma foi tomada nesta entrega:
1. **Piloto offline neste app** antes de Pátio/TPS? A tela de sondas (seção 6) já foi feita pensando nisso.
2. **"Normalizar"** (`ButtonCanvas5_33`) continua sem gravar nada e dizendo "foi normalizado com sucesso". Implementar a gravação ou retirar o botão? Não mexi porque as duas saídas mudam o que o inspetor vê.
3. **Protocolo de item**: padronizar `IATA-INSP-PISTA-ITEM-<ID>` (este app) também no app principal, que grava `IATA-INSP_PISTA_ITEM-<maior ID>` igual para o lote inteiro?
4. **"Continuar"**: hoje continua qualquer inspeção "Em andamento" de hoje, inclusive as iniciadas no Windows. Manter ou restringir às do próprio aparelho?
5. **Lista do dia**: só as de hoje (como está) ou também as em andamento de dias anteriores (hoje uma inspeção de ontem não pode ser continuada no mobile)?
6. **Senhas do hub** (auditoria, seção 5): levar ao responsável pelo Airport Now.

Não feito de propósito: limpeza das 18 variáveis mortas e da `ScreenLogin` (a tela define a estrutura das coleções do buffer; sai junto com a fase offline, que leva essa estrutura para o `App.OnStart`); `ID_Modulo` e o formato de `Fim` (M12), que dependem de conferir o dado gravado pelo app principal.

## 5. O que testar depois de colar

Num tablet, com um aeroporto de teste. Conferir o SharePoint depois de cada caso (`7.4-tbl_InspPista`, `7.4.1-tbl_InspPistaItens` filtrada por `IdInsp`, `tbl_inspPistaAnotacao` filtrada por `ID_FK`).

1. **Caminho normal**: Cadastrar → Iniciar → 2 apontamentos (um com 2 fotos, outro com áudio) → Finalizar Inspeção → todos "Salvo" → Finalizar. Esperado: 1 cabeçalho com `Protocolo` e `ID_pk`; 2 itens com `Protocolo` `IATA-INSP-PISTA-ITEM-<ID>` e `Hash` no formato novo; 1 áudio; inspeção "Pendente" na lista.
2. **Reenvio não duplica**: repetir o caso 1 e, no painel, tocar em "Salvar Todos" mais duas vezes (cada toque repete o envio inteiro) antes de "Finalizar". Esperado: mesmos 1 cabeçalho, 2 itens e 1 áudio.
3. **Queda no meio do envio**: 5 apontamentos com foto; tocar em "Finalizar Inspeção" e ligar o modo avião logo em seguida. Esperado: "Nem tudo foi enviado…", nada apagado. Tocar "Finalizar" ainda sem sinal: "Sem conexão…", nada apagado. Desligar o modo avião, tocar "Finalizar": reenvia; tocar de novo com todos "Salvo". SharePoint: 5 itens, nenhum duplicado.
4. **Sem sinal desde o início**: modo avião, inspeção com 2 apontamentos, "Finalizar Inspeção" → painel "Não Conectado" → "Finalizar": aviso, nada apagado → fechar o painel: volta ao passo 1 → sair do modo avião → "Finalizar Inspeção" → "Finalizar". Anote se, sem sinal, apareceu "Nem tudo foi enviado" ao abrir o painel (isso responde a sonda S16).
5. **Aviso de descarte**: com apontamento não enviado, tocar "Cadastrar" (aviso) e de novo em 10 s (formulário limpo). Repetir no ícone de voltar ao hub e no "Continuar" de outra inspeção. Sem apontamento pendente: um toque basta.
6. **Continuar**: com uma inspeção "Em andamento" de hoje (feita no Windows ou interrompida aqui), "Continuar" → formulário com os dados dela → resumo com os itens já gravados como "Salvo" → incluir 1 apontamento → enviar. Esperado: nenhum cabeçalho novo; só 1 item novo na lista.
7. **Hash**: dois "Incluir Apontamento" no mesmo segundo (toques rápidos). Esperado: `Hash` diferentes (sonda S18).
8. **Passo "Item" sem sinal**: modo avião, Local → Categoria → a lista de itens aparece (antes ficava vazia).
9. **Contadores**: comparar o número de "Pista de Pouso" com a lista de itens filtrada por aeroporto, Local = Pista de Pouso, Status = Não conforme, criados este ano.

## 6. Tela de sondas (fase offline) — só numa CÓPIA

`90_scrSondaOffline.pa.yaml` prova no tablet o que o motor offline precisa antes de ser gerado. **Não colar no app de produção** (o botão S3 grava e apaga um registro de teste na lista de itens).

Montagem: Arquivo → **Salvar como** (cópia) → nova tela em branco → renomear para `scrSondaOffline` → Exibição de código → substituir tudo → arrastar a tela para o topo da árvore (vira a inicial) → publicar a cópia → abrir **no tablet, pelo Power Apps Mobile** (no Studio `SaveData`/`LoadData` não valem).

| Botão | O que fazer | Anotar |
|---|---|---|
| S2 · Gravar / Ler dados | Gravar → **fechar o app de verdade** (deslizar para fechar) → abrir → Ler | se voltou `sonda / 1.5 / data / true` ou a mensagem de erro |
| (quadro 1) | tocar no quadro e tirar uma foto | — |
| S6 · Converter foto e guardar | depois da foto | tamanho em MB e se houve erro |
| S4 · Ler foto convertida | fechar e reabrir o app antes | se a foto aparece no quadro 2 |
| S4b · Guardar / Ler foto sem converter | Guardar → fechar e reabrir → Ler | se a foto aparece no quadro 3 (esperado: **não**; confirma que a conversão é necessária) |
| S3 · Gravar foto lida na lista | depois de S4, com sinal | "no servidor: sim/NÃO", tempo em ms, foto no quadro 4 |
| S3 · Apagar sonda | **sempre** depois de S3 | conferir na lista que o item `SONDA-S3` sumiu |
| S13 · Rand em ForAll | tocar | se os 3 números são diferentes |
| S16 · Select em botão oculto | tocar | "oculto e desabilitado: RODOU / não rodou" |
| S17 · Tamanho das listas | com sinal | os dois maiores IDs (o 3º número fica 0 porque a tela principal não abriu) |
| Apagar arquivos da sonda | no fim | — |

Mande os resultados (pode ser uma foto da tela de cada caso). Com S2, S3, S4 e S6 aprovadas, gero o piloto offline deste app; S16 e S17 ajustam detalhes.

## 7. Validado localmente (`build/entregar.sh`)

- YAML parseável; nomes únicos; toda propriedade existe no dicionário extraído deste export (20 tipos de controle), então nenhum PA2108 provável.
- Trava de layout: árvore, ordem e propriedades visuais dos 242 controles de `frmInspPistaMob` idênticas ao export, fora 3 exceções declaradas (`Label12_3.Text`, `ButtonCanvas3_4.Visible`, `TextCanvas2_2.Text`); os 31 controles da tela de sondas estão declarados como novos.
- **Valor de cada propriedade** comparado com o export: mudaram exatamente as 13 da seção 2 (12 da tela + `App.OnStart`), nenhuma mudou só em espaço em branco, e `App.OnStart` é o original com exatamente as 3 trocas de Q8.
- Consultas SharePoint por linha de galeria: 3 → 0. Padrões não delegáveis nas telas entregues: 5 → 0. (A `ScreenLogin`, inalcançável e não entregue, mantém 3 filtros com `Year(Criado)`.)
- Sintaxe (parênteses, aspas, vírgulas), referências entre telas 0, navegação, locale; `App.OnStart` em pt-BR com prova de ida e volta; 2 execuções com o mesmo hash; 0 CR.
- Variáveis mortas: as 18 que já existiam estão declaradas em `build/allow_vars_mortas.json`; nenhuma nova.

## 8. NÃO validado (depende do Studio e das listas reais)

- Compilação pelo Studio e App Checker.
- `ForAll(Filter(lista, IdInsp = …) As R, {ID: R.ID, Hash: R.Hash, Protocolo: R.Protocolo})` com a seleção explícita de colunas ligada neste app: a projeção existe para que `Hash`/`Protocolo` venham na consulta; confira no painel (Q7) que os itens enviados mudam para "Salvo".
- `Len(R.Audio)` sobre a coluna de áudio (texto longo) dentro da projeção dos áudios: se o SharePoint devolver o texto truncado, o áudio seria reenviado — o caso 2 da seção 5 mostra.
- `Select(ButtonCanvasSalvarTodos)` a partir do "Finalizar": o reenvio roda depois da fórmula do "Finalizar" terminar, por isso o segundo toque.
- Comportamento sem sinal do botão de envio desabilitado (sonda S16).
