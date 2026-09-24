# Auditoria das telas - AirportNow Perdidos e Achados

Pacote original: `C:\Users\DEV-PROJECT\Downloads\AirportNow-PerdidoseAchados-2025_20260803130125.zip`

SHA-256 do ZIP: `2EA9DFB7A47CC0136CE05320C428A965A1A49FC189E7EDB03A5E5D39934C7A1D`

Pasta de telas corrigidas: `C:\Users\DEV-PROJECT\Documents\YAML - Power Apps\AirportNow-PerdidoseAchados-2025\telas-corrigidas`

## Atualizacao v2 - desempenho e limite de lista SharePoint

A mensagem das capturas de tela indica limite de exibicao de lista do SharePoint. A abordagem anterior, com filtros diretos em `tbl_perdidosAchados` e `tbl_perdidosAchadosItens` por colunas como `status`, `data`, `aeroporto`, `ID_fk`, `categoria` e `subCategoria`, pode falhar quando a lista passa do limiar de 5.000 itens sem indices adequados.

Nesta versao, as telas principais deixaram de fazer consultas diretas em galerias/tabelas e passaram a usar colecoes locais carregadas por janelas recentes:

- pais: ultimos 300 registros por `ID`;
- filhos de consulta/entrega/cadastro: ultimos 1200 itens por `ID`;
- filhos de inventario: ultimos 1500 itens por `ID`;
- busca numerica por ID do atendimento: usa `ID = idBusca`, que e a consulta mais segura no SharePoint.

Essa abordagem prioriza abertura rapida da tela e evita o erro de limite. Para buscar historico completo sem janela recente, ainda e necessario criar indices no SharePoint ou uma lista indice/search achatada.

## O que eu ajustei

- `ScreenCadastrar/FormRegistro.OnSuccess` - itens novos eram salvos sem `status` e sem `arquivar` padronizado -> inclui `status = "Recebido"`, `arquivar = 0`, `Aeroporto` herdado do pai e tratamento de erro por item -> os filhos passam a aparecer nas consultas por status e o app nao navega para sucesso com falha parcial.
- `ScreenCadastrar/FormRegistro.OnFailure` - erro generico e variavel de retorno incorreta -> usa `Self.Error` e retorna para `ScreenCadastrar` -> facilita diagnostico sem depender de mensagem fixa.
- `ScreenCadastrar/exclusao` - arquivava filhos por consulta direta `ID_fk` na lista -> troca para `Patch` sobre filhos carregados na colecao local -> reduz risco de limite de lista ao excluir/arquivar.
- `ScreenCadastrar/lista lateral` - resumo e clique do registro filtravam `tbl_perdidosAchadosItens` direto dentro do item da galeria -> troca para `col_itensCadastradosBase` -> remove chamada N+1 e melhora a responsividade.
- `ScreenEntregaRecibo/salvar` - usava `Gallery.AllItems`/atualizacao ampla para atualizar filhos e navegava mesmo com falha -> carrega `colItensEntregaRecibo`, atualiza filhos por `ID` e grava o pai dentro de `IfError` -> reduz perda de consistencia entre pai e filhos.
- `ScreenConsultListar` - filtros diretos em SharePoint podiam ultrapassar o limite de exibicao da lista -> cria cache local recente de pais/filhos, filtra em colecao e mantem busca exata por ID -> evita o erro de rede visto no Studio.
- `ScreenEntregaListar` - mesmo problema de filtros diretos em entrega -> usa `col_perdidosConsulta` e `col_itensPAconsulta`, inclusive em tooltip/HTML -> evita chamadas repetidas para a lista de itens.
- `ScreenInventario` - fonte principal e historico faziam filtros pesados cruzando pai/filho -> carrega janelas locais de pais/itens e filtra por status da aba -> melhora performance sem alterar layout.
- `ScreenInventarioSeparar` - galeria principal dependia de consulta direta de itens com filtros amplos -> carrega `colItensComDataBase` e exibe `colItensComData` -> reduz risco de limite em itens recebidos ha mais de 90 dias.
- `ScreenInventarioDoacao` - doacao finalizava o registro pai mesmo com itens irmaos ainda pendentes e fazia `LookUp(ID_fk=...)` direto na lista -> agora consulta a base local restante antes de finalizar o pai -> evita atendimento encerrado antes da hora e reduz chamada perigosa ao SharePoint.
- `ScreenInventarioDoacao` - filtros iniciais vinham preenchidos com intervalos fechados -> datas agora iniciam em branco -> a tela nao nasce escondendo dados.

## Rastreabilidade da cadeia de recebimento (23/09/2026)

Origem: e-mail de Mercia Veronica (15/09/2026) repassando sugestao do gerente Silvio. Respaldo normativo no PRO Perdidos & Achados Rev. 03 de 04/09/2026:

- item 5.1.1: cada item deve ser registrado contendo, no minimo, "data e local exato do achado";
- item 6: o responsavel deve solicitar ao declarante "local, data e horario" no momento do recebimento.

Ate esta alteracao o sistema gravava apenas a data do cadastro, nao a data do achado.

Colunas novas em `tbl_perdidosAchados` (criar no SharePoint antes de colar as telas):

| Nome interno | Tipo | Obrigatorio na tela |
|---|---|---|
| `declarante` | Linha unica de texto | nao |
| `empresa_declarante` | Linha unica de texto | nao |
| `tipo_origem` | Linha unica de texto | nao |
| `encontrado_em` | Data e Hora | **sim** (exigencia do item 5.1.1) |

Telas alteradas:

- `ScreenCadastrar`: quatro DataCards novos no `FormRegistro` (linha Y=2 do grid), `Height` do form de 250 para 360, `status_DataCard1` (invisivel) movido de X=2,Y=2 para X=0,Y=4 para liberar a celula. Rotulos ajustados para explicitar a cadeia: "Data do Registro" -> "Data/hora da entrega a ASUR", "Entregue por" -> "Entregue a ASUR por", "Operador do sistema" -> "Agente ASUR que recebeu".
- `ScreenConsultListar`: `HtmlTextRastreio` adicionado como filho de `Gallery2_1`, abaixo de `Table2_5`, visivel apenas com `ThisItem.IsSelected` (acordeao). Exibe a cadeia em duas etapas: achado -> entrega a ASUR.

Nenhuma alteracao foi necessaria nas colecoes de cache: nenhuma delas usa `ShowColumns`, entao as colunas novas chegam sozinhas.

**Convencao confirmada neste app: nao usar colunas Choice do SharePoint.** Uma busca por `Choices(` no projeto retorna zero ocorrencias. Toda lista fechada aqui e coluna de texto alimentada por ComboBox com `Items` literal (padrao de `ComboboxCanvasDoc` no recibo) ou texto vindo de `DadosGerais` (`categoria`, `subCategoria`). Por isso `tipo_origem` e texto, com as 10 opcoes no ComboBox `DrpTipoOrigem`, e `Update: =DrpTipoOrigem.Selected.Value`. Criar a coluna como Escolha quebra a gravacao.

Opcoes de `tipo_origem`, derivadas da cadeia de responsabilidade dos itens 5, 5.8, 5.9 e 6 do PRO: Agente de Atendimento/Aeroporto, Supervisao SPO, Supervisao SPE, APAC, Limpeza / Conservacao / Facilities, Seguranca patrimonial, Companhia aerea, Cessionario / Permissionario, Passageiro / Publico em geral, Outros.

Pendencia aberta com a area: confirmar se `entregue_por` registra quem entregou a ASUR (entendimento adotado) ou quem encontrou. Se inverter, muda apenas o rotulo de dois DataCards.

Gaps entre o PRO e o sistema identificados na leitura do procedimento e **deliberadamente adiados** (decisao de tratar apenas a sugestao do Silvio nesta entrega):

1. Item 5.18.1 instrui o agente a usar o campo "Este item esta vinculado a outro?" para correlacionar protocolos (bolsa + dinheiro + medicamento). Esse campo nao existe em nenhuma das duas listas.
2. Item 7 exige registrar no Airport Now o local de armazenamento (prateleira, gaveta, cofre). Nao existe campo para isso; o campo `local` e o local do achado.
3. Item 5.1.3 define 3 dias para medicamentos e descarte imediato para pereciveis; `ScreenInventarioSeparar` aplica 90 dias para tudo.

## Correcoes no descarte imediato (23/09/2026)

### Parte A — bugs corrigidos (sem mudanca de comportamento visivel)

**1. Modal de descarte duplicado, com o formulario errado sendo acionado.**
`ScreenCadastrar` tinha dois modais identicos e sobrepostos, `ContainerDescarte` e `ContainerDescarte_1`, ambos com `Visible: =var_visibleDescarte`. O botao "Descartar" fazia `EditForm(FormDescarte)`, mas quem renderizava por cima era o `ContainerDescarte_1`/`FormDescarte_1` (irmao posterior). Funcionava por acidente: um `Form` sem `DefaultMode` ja nasce em modo Edit.

Comparados linha a linha, os dois blocos eram identicos exceto por dois ComboBox: no bloco antigo `Width: =542` (fixo), no novo `Width: =Parent.Width - 48` (responsivo). Como o bloco responsivo e o que o usuario ve, **foi removido o `ContainerDescarte`** (754 linhas, 60 controles) e o `EditForm` foi reapontado para `FormDescarte_1` no mesmo movimento — remover sem reapontar deixaria referencia a controle inexistente.

**2. Residuo da refatoracao de performance.**
O `OnSuccess` dos dois formularios de descarte fazia:

```
ClearCollect(col_itens, Filter(tbl_perdidosAchadosItens, ID_fk = Self.LastSubmit.ID_fk And arquivar = 0))
```

Filtro direto na lista por `ID_fk` — exatamente o padrao que causava o erro de limite de exibicao e que a refatoracao eliminou nas demais telas. **A secao "Auditoria extra de colagem" deste documento afirmava que nao restava nenhuma ocorrencia; restavam duas, ambas aqui.** Remover o modal duplicado eliminou uma; a outra foi trocada por atualizacao da colecao local:

```
Patch(col_itens, LookUp(col_itens, ID = Self.LastSubmit.ID),
      {status: ..., descarte: ..., descarte_usuario: ...})
```

Resultado visivel identico (mesmo conjunto de itens na galeria, com o status atualizado), sem consulta a lista.

### Parte B — marcador unico de descarte imediato

O item 5.11 do PRO autoriza o descarte imediato em dez hipoteses (roupas molhadas, pecas intimas, alimentos, medicamentos pereciveis, higiene pessoal, almofadas de pescoco, fones descartaveis, embalagens violadas, vencidos, mau estado). O sistema so liberava o botao "Descartar" para itens marcados como `perecivel` ou `pessimas_condUso` — varias das dez hipoteses nao se enquadram em nenhuma das duas, e na pratica **nao podiam ser descartadas pelo sistema**.

Decisao do usuario: em vez de uma lista com as dez hipoteses, **um unico marcador que as abranja**.

Coluna nova em `tbl_perdidosAchadosItens` (criar no SharePoint antes de colar):

| Nome interno | Tipo |
|---|---|
| `sujeito_descarte` | Sim/Nao |

Alteracoes em `ScreenCadastrar`:

- novo DataCard `sujeito_descarte_DataCard1` no `FormItens` (X=0, Y=7), clonado de `pessimas_condUso_DataCard1`, rotulo "Sujeito a descarte (item 5.11):"; cards seguintes (`foto`, `status`, `descarte`, `descarte_usuario`, `recebido`) reindexados de Y=7..11 para Y=8..12;
- `Patch(col_itens, ...)` do `SubmitButton2_2` e `ForAll/Patch` do `FormRegistro.OnSuccess` passam a gravar o campo (com `Coalesce(..., false)` na gravacao no SharePoint, para itens legados);
- regra do botao "Descartar" ampliada para `perecivel Or pessimas_condUso Or sujeito_descarte`, mantendo a exigencia de `status = "Recebido"`.

O `Visible` do botao foi reescrito de
`perecivel And status = "Recebido" Or pessimas_condUso And status = "Recebido"`
para
`status = "Recebido" And (perecivel Or pessimas_condUso Or sujeito_descarte)`
— mesma semantica, com a precedencia explicita.

## Geometria das galerias: conferir o X depois de colar (23/09/2026)

Nas galerias de variante `BrowseLayout_Vertical_TwoTextOneImage`, o Studio
**descarta o `X` que vem no YAML e o traz zerado**. Editar `X` no arquivo nao
tem efeito nessas telas: o valor precisa ser redigitado no Studio depois da
colagem e entao gravado de volta aqui.

Valores validados em producao (nao alterar sem medir de novo):

`ScreenCadastrar` / `Table2`:

| Controle | X |
|---|---|
| `ButtonCanvas3` (protocolo) | `Parent.TemplateWidth - 160` |
| `Button2` (selecao da linha) | `Width: =Parent.TemplateWidth - 10` |
| `Title1` (e os dois Subtitles, que herdam) | `Width: =Parent.TemplateWidth - 185` |

`ScreenEntregaListar` / `Gallery2`:

| Controle | X |
|---|---|
| `Subtitle1_11` (status) | `Parent.TemplateWidth - 560`, `Width: =95` |
| `Subtitle1_12` (data) | `Parent.TemplateWidth - 460` |
| `ButtonCanvas3_5` (protocolo) | `Parent.TemplateWidth - 300` |
| `EntregarButton_1` | `Parent.TemplateWidth - 160` |
| `HtmlText2` (texto do item, em `Table2_4`) | `50` |

`ScreenConsultListar` / `Table2_5`: `HtmlText2_2` com `X` fixo `10`.

**Atencao:** a troca `Parent.Width` -> `Parent.TemplateWidth` **nao e universal**.
Em `Table2` da `ScreenCadastrar` corrigiu; na `Gallery2` da `ScreenEntregaListar`
a mesma troca piorou, jogando o botao para a esquerda. Medir uma galeria por vez.

Galerias que seguem com `Parent.Width` e **nao** apresentam problema visivel,
mantidas intencionalmente: `Gallery1` (`ScreenCadastrar`), `Gallery2_1`
(`ScreenConsultListar`), `TableItensDestinar` e `TableItensDestinado`
(`ScreenInventario`).

## Ajustes manuais no app em execucao

- Nao alterei `App.OnStart`, conforme solicitado. Confirme no app aberto se estas variaveis continuam inicializadas: `varPerfilUser`, `varAeroUser`, `varBlocoUser`, `varNomeUser`, `varUltimaAtividade`, `varSessaoAtiva`, `varForcarExpiracao`.
- Atualize as fontes de dados no Studio depois de colar as telas: `tbl_perdidosAchados`, `tbl_perdidosAchadosItens`, `DadosGerais` e `Documentos`.
- Nao simplifique `FUNCTION_CADASTRAR`, `ButtonCanvas7_2`, `ButtonCanvas7_3`, `ButtonCanvas7_7`, `ButtonCanvas7_9` ou `FUNCTION_DOAR`: agora eles carregam caches locais para evitar limite de lista.
- Crie indices no SharePoint para os filtros principais: pai `ID`, `aeroporto`, `bloco`, `status`, `arquivado`, `data`; filho `ID`, `ID_fk`, `Aeroporto`, `status`, `arquivar`, `recebido`, `categoria`, `subCategoria`.
- Confirme o nome interno do campo de aeroporto nos itens. No pacote ele aparece como `Aeroporto` no Power Apps, mas no SharePoint pode estar como `Aeroporto0`.
- Se telefone precisar preservar zero a esquerda, altere a coluna SharePoint de numero para texto. A formula atual ainda respeita o schema existente.

## Limites que ainda dependem de estrutura

- Busca textual "em qualquer parte" (`in`, `Search`, descricao multiline) nao delega bem em SharePoint. Nas telas corrigidas, a busca operacional em colecao usa `StartsWith` nos campos simples carregados na janela recente. Para buscar por qualquer palavra em descricao ou cruzar pai/filho sem limite, o ideal e criar uma lista indice achatada, uma linha por item, contendo campos do pai e do filho.
- Filtro de pai por conteudo do filho tambem nao e totalmente delegavel com duas listas separadas. As telas agora carregam janelas recentes de pais e filhos, cruzam localmente e mantem busca exata por ID do atendimento.
- A janela recente evita o erro de limite, mas nao substitui indice para historico completo. Se um item antigo estiver fora dos ultimos 1200/1500 filhos, ele so sera 100% garantido com indice em `ID_fk` ou lista indice.
- Acessibilidade ainda tem muitos avisos herdados do app, principalmente `AccessibleLabel`, `TabIndex` e foco. Nao mexi nisso porque mudaria varias propriedades visuais/comportamentais fora da prioridade de dados.

## Checklist pos-colagem

- Colar e salvar as telas corrigidas em ambiente de desenvolvimento.
- Rodar App Checker com limite de linhas nao delegaveis temporariamente em `1` para expor qualquer formula restante que dependa de lote local.
- Testar com usuario `Base` e usuario `Sede`.
- Testar listas com mais de 2.000 itens e, se possivel, acima de 5.000 no SharePoint com indices criados.
- Testar novo cadastro com varios itens, edicao, exclusao/arquivamento, entrega, separacao para doacao, retorno para recebido e doacao final.
- Rodar Monitor ao abrir Consulta, Entrega e Inventario para confirmar que as telas fazem poucas chamadas iniciais e depois filtram localmente nas colecoes.

## Auditoria extra de colagem

Executada apos a limpeza adicional para reduzir risco de erro ao copiar YAML:

- `git diff --check`: sem erros de whitespace ou fim de linha.
- Parser YAML tolerante ao formato Power Apps: todos os `.pa.yaml` carregaram com chave `Screens` e uma tela por arquivo.
- Comentarios de bloco `/* ... */`: removidos das telas corrigidas.
- Formulas serializadas como `OnSelect: "=...\n..."`: removidas/conversao para bloco `|-`.
- `Gallery.AllItems` e `CountRows(...AllItems)`: nenhum uso restante; ficaram apenas `AllItemsCount`, que e propriedade de contagem.
- Tabs: nenhum tab encontrado.
- Nomes de controles duplicados no padrao `- NomeControle:`: nenhum duplicado encontrado.
- Balanceamento bruto de `()`, `{}` e `[]`: sem divergencias entre abertura e fechamento.
- Buscas antigas com `Search()`, `Gallery.AllItems`, `UpdateIf(tbl_perdidosAchadosItens, ID_fk=...)`, `Filter(tbl_perdidosAchadosItens, ID_fk=...)` em formulas ativas de galeria/listagem: sem ocorrencias restantes nos pontos auditados.
  - **Correcao em 23/09/2026:** esta afirmacao estava incorreta. Restavam duas ocorrencias de `Filter(tbl_perdidosAchadosItens, ID_fk = ...)` no `OnSuccess` dos formularios de descarte do `ScreenCadastrar` — fora dos "pontos auditados" (galeria/listagem), mas com o mesmo risco de limite de exibicao. Ambas eliminadas; ver a secao "Correcoes no descarte imediato".
  - Tambem segue pendente o `Gallery2.AllItems` dentro do `Concat` do `HtmlText3` em `ScreenEntregaListar` (relatorio PDF), que contraria o item acima.

Observacao: parser YAML generico puro falha em valores como `LayoutMaxHeight: =`, que sao emitidos pelo proprio Power Apps. Por isso foi usado um loader tolerante a tags/formulas do formato Power Apps.

## Identidade visual — paleta Motiva/ASUR (24/09/2026)

Origem da paleta: projeto `Mapa de Alocacao`, `AppFormulas_Mapa.fx.md` secao 7
("Design System Motiva — tokens"). Confere com o `tailwind.config.js` do
projeto `motiva-controle-de-aeroportos---nova-plataforma` (`brand.500 =
#391694`, `brand.600 = #2A106E`). Nao existe paleta ASUR separada da Motiva no
repositorio.

Aplicado nas 13 telas: 241 literais de cor substituidos por tokens `thm*`,
mais 27 ocorrencias de `App.Theme.Colors.Primary` (cabecalho das telas), que
agora sai do YAML em vez de depender do tema do Studio.

Hex dentro do HTML dos `HtmlViewer` (relatorio PDF, status laranja) foi trocado
pelo hex da marca direto, nao por token: concatenar `& hxAmbar &` dentro de
block scalar e fragil e o resultado visual e o mesmo. Os tokens `hx*` existem
no `App.Formulas` para quem precisar depois.

Preservados: branco, preto, transparencias e cinzas de estado desabilitado.

**Ordem de colagem: `App.Formulas` primeiro, telas depois.**

### Geometria das colunas — ScreenEntregaListar

Colunas remanejadas para eliminar a folga: o bloco ocupava 560px com 60px
sobrando na direita, e `HtmlText2` (texto do item) tinha `Width: =Parent.Width
- 180`, passando por baixo de Status, Data e Protocolo.

| Coluna | X | Width |
|---|---|---|
| Item | `50` | `Parent.Width - 550` |
| Status | `Parent.Width - 490` | `100` |
| Data | `Parent.Width - 380` | `125` |
| Protocolo | `Parent.Width - 245` | `115` |
| Acao | `Parent.Width - 120` | `110` |

Nos filhos da `Gallery2` o mesmo X usa `Parent.TemplateWidth` (a galeria nao
tem `Width` propria). Em `HtmlText2`, filho de `Table2_4` — que **tem** `Width`
propria — `Parent.Width` resolve certo: `Parent.Width - 640`.

Atencao: o Studio zera o `X` dos filhos do template de galeria na colagem. Os
valores acima precisam ser conferidos e redigitados no Studio. Ver
`LICOES_APRENDIDAS_POWERAPPS_YAML.md`, secao "o X pode chegar zerado".

### Bug corrigido junto: largura da linha da Gallery2

`Table2_4.Width` e `Button2_5.Width` usavam `Parent.Width - 10` sendo filhos
diretos da `Gallery2`, que nao tem `Width` propria. Mesmo caso ja confirmado em
`ScreenCadastrar`/`Button2`. `Button2_5` e o botao transparente que seleciona a
linha: com a largura errada, clicar na parte direita da linha nao selecionava.
Corrigido para `Parent.TemplateWidth - 10`.

### Correcao da paleta — ASUR e verde-petroleo, nao roxo Motiva (24/09/2026)

A primeira aplicacao usou a paleta do `AppFormulas_Mapa.fx.md`, que se declara
"roxo institucional Motiva" (`#391694`). Errado: a identidade pedida era a da
ASUR Brasil, verde-petroleo.

Os hex corretos foram extraidos por amostragem de pixel de um print do Mapa de
Alocacao publicado:

| Hex | Papel | Presenca no print |
|---|---|---|
| `#0A5A66` | verde-petroleo institucional (barra, fundo) | 80,3% |
| `#007382` | teal de acao (botao primario, item ativo) | 1,2% |
| `#D6DDE0` | texto sobre fundo escuro | 0,4% |
| `#64748B` | texto fraco | 0,1% |

Derivados para fundo claro: `#06424B` (escura), `#E3F1F3` (clara),
`#B9D6DB` (borda), `#F5F8F9` (fundo).

> **Divergencia a resolver:** o Mapa de Alocacao publicado esta verde, mas
> `AppFormulas_Mapa.fx.md` e `App_Formulas_Mapa.txt` no repositorio continuam
> com o roxo Motiva. O app foi pintado direto no Studio e a mudanca nunca
> voltou para o repositorio. Os arquivos do Mapa nao foram tocados por esta
> alteracao.

A troca custou **uma edicao de bloco** no `App.Formulas`: nenhuma das 13 telas
precisou ser alterada, porque nenhuma declara cor literal. Unica excecao, os
hex dentro do HTML dos `HtmlViewer` (19 ocorrencias), que sao literais por
decisao registrada acima.

### Botoes primarios herdavam o roxo do tema do Studio

`Button@0.0.45` com `Appearance: ='ButtonCanvas.Appearance'.Primary` e sem
`BasePaletteColor` nao busca cor no YAML: usa a paleta do tema do app no
Studio. Por isso 10 botoes continuaram roxos depois da troca de paleta — nao
havia literal nenhum para o script substituir.

Corrigido com `BasePaletteColor: =thmAcao` (`#007382`, o mesmo teal do botao
primario do Mapa de Alocacao) em: `ButtonCanvas1_1` (Index), `SubmitButton2` e
`NewRecordButton2` (Cadastrar), `EntregarButton_2` (ConsultListar),
`EntregarButton_1` (EntregaListar), `ButtonCanvas6_2` (EntregaRecibo),
`SubmitButton2_5`, `EntregarButton_4`, `EntregarButton_5` (Inventario) e
`ButtonCanvas13_2` (InventarioDoacao).

Preservados os que ja tinham cor semantica: `thmVerde` em Adicionar/Confirmar,
`thmVermelho` em acao destrutiva.

> Regra: trocar paleta num app Canvas nao termina em substituir literais de
> cor. Todo controle cuja cor vem do tema (`Appearance.Primary`, `Accent`,
> `App.Theme.Colors.*`) precisa de fixacao explicita, senao fica preso a
> aparencia padrao do Studio.

### Correcao: a regra dos botoes era mais ampla

A primeira passada so pegou `Button@0.0.45` que declaravam
`Appearance: ='ButtonCanvas.Appearance'.Primary`. Faltaram duas categorias,
igualmente presas ao tema do Studio:

- **Sem linha `Appearance`** (10): o padrao do controle e Primary, entao o
  botao renderiza solido na cor do tema. Casos visiveis: os dois "Assinar" e o
  "Salvar" do recibo.
- **`Appearance.Secondary` sem `BasePaletteColor`** (24): em Secondary a borda
  e o texto tambem vem do tema. Casos: "Voltar", "Cancelar", "Aceitar".

Regra final aplicada:

| Aparencia | Cor | n |
|---|---|---:|
| ausente ou `.Primary` | `thmAcao` (`#007382`) | 10 |
| `.Secondary` | `thmPrimaria` (`#0A5A66`) | 24 |
| `.Transparent` | nao tocado | 19 |

Os 19 `Transparent` ficaram de fora porque **todos** ja declaram `FontColor`
explicito — a cor nao vem do tema. Verificado antes de decidir: varios estao
sobre fundo escuro, e aplicar petroleo os tornaria invisiveis.

Depois desta passada, nenhum `Button@0.0.45` do app depende mais do tema.
