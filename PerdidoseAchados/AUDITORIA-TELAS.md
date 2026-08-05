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

Observacao: parser YAML generico puro falha em valores como `LayoutMaxHeight: =`, que sao emitidos pelo proprio Power Apps. Por isso foi usado um loader tolerante a tags/formulas do formato Power Apps.
