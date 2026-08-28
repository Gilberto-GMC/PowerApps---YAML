# Arquitetura — Mapa de Alocação de Pátio (Motiva Aeroportos)

Documentos irmãos:
[ESTRUTURA_LISTA_MAPA.md](ESTRUTURA_LISTA_MAPA.md) (a lista SharePoint) ·
[AppFormulas_Mapa.fx.md](AppFormulas_Mapa.fx.md) (dados de referência e tema) ·
[FLUXO_EXPURGO_MAPA.md](FLUXO_EXPURGO_MAPA.md) (limpeza automática)

---

## 1. O problema

A alocação diária de aeronaves no pátio do SBNF vive hoje em `Mapa de Alocação - 2026.xlsx`: uma aba por dia,
47 abas. Os voos **não são dados** — são caixas de texto desenhadas à mão sobre a grade (cerca de 1 MB de shapes
por aba). O operador do APOC abre o Excel, desenha um retângulo esticado do horário de chegada ao de saída,
pinta com a cor da companhia, contorna com a cor do portão e digita `CIA nº-chegada/nº-saída`.

Da conversa com a operação (28/08/2026):

- **É visual, e o visual é o produto.** *"O importante é que tenha esse visual. As posições, que são as linhas;
  as colunas, que são os horários — e o cara consiga bater e ver em tal horário a posição 4 vai estar ocupada
  por esse voo e ele vai utilizar o portão."*
- **É multiusuário e vivo.** *"Fica no computador deles e eles vão mexendo."* Um mexe, o outro tem que ver.
- **Realocação por atraso é a operação do dia.** *"Tudo é 2 clique: alterar posição, alterar portão."*
- **Casos especiais.** Voo pesquisado (pintado de vermelho, costuma trocar de posição porque a 5 fica na frente
  do embarque e faz barulho); posição interditada por obra ou missão presidencial.
- **Não é sistema de registro.** *"Essa informação já tá no Ares."* Vale a programação futura, lançada com
  antecedência no fim do mês anterior.

O que o Excel **não** faz e o app faz: impede duas aeronaves na mesma posição no mesmo horário, impede o mesmo
portão em dois voos simultâneos, e mostra quem alterou o quê.

**A numeração dos portões saiu da própria gravação.** Douglas: *"essa aeronave que vai chegar às 10 horas, da
GOL 1214 e sai 1217, vai ser estacionada no tango 4 e vai utilizar o portão 4"*. Na aba `SEX 28.08` esse bloco
está na linha 9 (T4), das 10:00 às 11:40, com contorno `#FF0066` — logo **`#FF0066` = portão 4**. Os outros
quatro foram numerados por convenção, do frio para o quente: `#00FFFF` 1 · `#00B050` 2 · `#FFFF00` 3 ·
`#FF0066` 4 · `#FF0000` 5. Trocar a numeração é **uma linha** em `colPortoes`, porque a lista guarda o número,
nunca a cor.

> **Duas variantes de vermelho na planilha.** Os contornos aparecem como `#FF0000` e `#F22727` — a mesma
> intenção, com a deriva de quem escolhe a cor à mão a cada caixa. No app existe um vermelho só; ao transcrever
> os dias antigos, as duas viram portão 5.

## 2. O que virou dado local e o que virou lista

Critério do repositório: vai para `App.Formulas` quando **as três** forem verdadeiras — conteúdo estável (1–2
mudanças por ano), só o desenvolvedor altera, cabe em memória. Vira lista quando **qualquer uma** for
verdadeira — cresce sem parar, é alimentada pelo usuário final, precisa mudar sem republicar, o Power BI
precisa do histórico.

| Conjunto | Volume | Muda quando | Quem altera | Decisão |
|---|---|---|---|---|
| Aeroportos | 1 | Novo aeroporto entra no sistema | Desenvolvedor | `App.Formulas` |
| Pátios | 3 | Obra / novo aeroporto | Desenvolvedor | `App.Formulas` |
| Posições | 25 | Reforma de pátio / novo aeroporto | Desenvolvedor | `App.Formulas` |
| Portões e cores | 5 | Praticamente nunca | Desenvolvedor | `App.Formulas` |
| Companhias e cores | 6 | Cia nova opera no aeroporto (~1×/ano) | Desenvolvedor | `App.Formulas` |
| **Alocações** | ~40/dia, cresce sempre | O tempo todo | **Operador do APOC** | **`tb_alocacoesMapa`** |

São **40 registros estáticos** somados. Como listas seriam cinco conexões, cinco chamadas de rede na abertura,
cinco conjuntos de índices e uma tela de cadastro para construir e manter. Como named formula não custam nada.

**Isolamento que preserva a saída:** nenhuma tela lê a origem diretamente — todas leem `colAerosMapa`,
`colPatios`, `colPosicoes`, `colPortoes` e `colCias`. Se um dia o operador precisar cadastrar posição sem
republicar, cada uma vira lista trocando **só a definição em `App.Formulas`**; as telas não mudam uma linha.

> `colPosicoes.id` é identificador estável: é ele que vai gravado em `id_posicao`. Nunca reordenar nem
> reaproveitar. Quem muda quando o desenho do pátio muda é a coluna `ordem`.

## 3. Estratégia de coleções — o núcleo da performance

**Uma chamada de rede por dia carregado. Todo o resto em memória.**

| Coleção | Origem | Recalculada quando | Tamanho |
|---|---|---|---|
| `colDia` | Uma consulta delegável a `tb_alocacoesMapa` | Carregar o dia · salvar · excluir · ATUALIZAR | ~40 |
| `colGrade` | `colPosicoes` × `colDia`, em memória | Sempre que `colDia` muda | 25 (uma por posição) |

`colDia` é projetada com `ForAll(… As _r, {…})` — não `ShowColumns("…")`, que é erro de parsing e derruba a
fórmula inteira gerando dezenas de erros derivados sem relação com a causa.

`colGrade` guarda, por posição, o **HTML da linha já montado**. A galeria fica no mais barato que existe:

```
galPosicoesMap.Items  =Filter(colGrade, locPatio = "TODOS" Or patio = locPatio)
htmTrilhoMap.HtmlText =ThisItem.html
```

### As regras que as telas respeitam

1. **Nenhum `LookUp`, `Filter` ou `First(Sort(...))` sobre a fonte de dados dentro de template de galeria** —
   seria uma consulta por linha por render. Todo cruzamento (posição × cor da cia × cor do portão) é resolvido
   na montagem de `colGrade`. Reprovado pela regra 21 do validador.
2. **Nenhuma propriedade do template lê `galPosicoesMap.Selected`** — dependência circular; o Power Apps
   devolve branco em silêncio, sem erro. A seleção trafega por `varPosSel`, gravada no `OnSelect` do
   `HtmlViewer` da linha. Reprovado pela regra 23.
3. **Filtros de tela são em memória.** Trocar de pátio é `Filter(colGrade, …)` — zero rede. Só trocar de
   **data** ou de **aeroporto** vai ao SharePoint.
4. **Recarga governada por um único ponto.** `btnAtualizarMap.OnSelect` contém o bloco de recarga inteiro
   (`colDia` → `colGrade`); `OnVisible`, salvar, excluir e os botões de data chamam `Select(btnAtualizarMap)`.
   Isso também resolve a armadilha de `Navigate` para a própria tela não reexecutar o `OnVisible` — em vez de
   duplicar o bloco, existe uma cópia só.
5. **Nunca `CountRows`/`CountIf` sobre a lista.** Os contadores da barra contam `colDia`. Reprovado pela regra 22.
6. **Sincronismo multiusuário barato.** `tmrSyncMap` a cada 60 s compara o `Modificado` mais recente do dia no
   servidor com o mais recente em `colDia`. Diferente → aparece a faixa *"a programação foi alterada"* com o
   botão ATUALIZAR. **Não recarrega sozinho por baixo de quem está editando.** Uma consulta por minuto, e o
   timer é barrado por `varMapaVisivel` — `AutoStart` + `Repeat` continua rodando com a seção invisível
   (regra 27 do validador).
7. **`App.OnStart` vazio de propósito.** Named formula não custa nada até ser lida. Nada de `ClearCollect` de
   dado estático na abertura.
8. **Limite de linhas de dados = 2000.** Coleção maior que o limite trunca **em silêncio**.

Resultado na abertura: **uma** requisição HTTP.

## 4. Telas

| Tela | Papel |
|---|---|
| `scrMapaInicio` | Apresentação, como ler a grade, seleção de aeroporto e data, resolução de permissão |
| `scrMapaPatio` | A grade, o painel lateral de edição, os filtros e a legenda |
| `scrMapaReferencia` | Posições, portões e companhias em leitura, com as cores aplicadas |

Shell comum: trilho lateral roxo (`cntMenu*`, 236 px aberto / 76 recolhido) + barra de título de 72 px. O
trilho é **gerado com sufixo por tela** (`Map`, `Ref`), nunca copiado no Studio — copiar faz o Studio renomear
para `_1` e quebrar o YAML, e nome de controle é único no app inteiro, não por tela.

### Como a grade é desenhada

Power Apps não tem Gantt, e `HtmlViewer` não devolve clique por elemento — então desenho e clique são
separados, e é isso que torna a solução simples:

- Cada linha é um `<table style='table-layout:fixed'>` com um `<td>` por segmento e **largura em porcentagem**
  calculada de `hora_inicio`/`hora_fim`: `(fim − ini) × 100 / 1440`.
- `<table>` e não flexbox, e nenhum `<svg>` nem emoji — o sanitizador do `HtmlViewer` remove SVG e flexbox não
  sobrevive em todo cliente.
- `Text(x, "0.000", "en-US")` — **a tag de idioma é obrigatória**: em cliente pt-BR, `Text(3.47, "0.000")`
  devolve `3,470` e quebra o `width:` do CSS. Reprovado pela regra 26 do validador.
- Como a sobreposição é bloqueada ao salvar, cada posição é uma **faixa única** e os segmentos saem em ordem,
  sem cálculo acumulado: `Index(_bl, _i.Value - 1)` dá o bloco anterior e o vão é a subtração. As duas linhas
  por posição do Excel existiam justamente por falta de validação.
- Cor do `<td>`: `background` = `cor_hex` de `colCias`, `border: 3px solid` = `cor_hex` de `colPortoes`,
  `hxVermelho` + selo `P` quando `pesquisado = 1`, cinza `hxTextoFraco` + `INTERDITADO` quando o tipo não é
  `VOO`. **Nenhuma cor literal entra no `.pa.yaml`** (regra 16).

### Como se edita — os dois cliques pedidos

Toque na linha → `OnSelect` do `HtmlViewer` grava `varPosSel` e abre o painel com os voos daquela posição
(vindos de `colDia`). Toque no voo → o formulário carrega e o cabeçalho mostra `Modificado`/`Modificado por`.

O formulário é **controles avulsos com `Patch`**, não um `Form`/`DataCard`. Isso elimina de saída as
armadilhas de `MetadataKey: FieldValue` duplicado e da ordenação por `Y` dos DataCards.

Os quatro seletores usam o padrão do repositório: `Items` de **coluna única `Value`**,
`DefaultSelectedItems: =[valor]` e um **nonce** (`Items: =Filter(colXSel, locNonce >= 0)`, `locNonce`
incrementado a cada troca de seleção) — sem o nonce, o dropdown moderno não volta ao padrão quando o valor
novo é igual ao que ele já mostrava.

### Validação ao salvar

Toda sobre `colDia`, em memória — custo zero:

1. `HH:mm` válido, entre `00:00` e `24:00`.
2. Saída depois da chegada. Voo que vira o dia é lançado em **dois registros**, um até `24:00` e outro no dia
   seguinte — é como a planilha já faz.
3. **Sobreposição na posição** — bloqueia e nomeia o voo conflitante com horário e prefixo.
4. **Portão ocupado** no mesmo intervalo, em qualquer posição — bloqueia.
5. **Envergadura** acima do `env_max` da posição — **dormente**, ver abaixo.
6. **Posição de contingência** (o T3) — pede confirmação, não bloqueia.

A regra 5 nasce desligada por decisão da operação (28/08/2026): a planilha registra a classe A/B do pátio 2/3
por cor, não por metragem, e ninguém tem os números. Todas as 25 posições têm `env_max: 0`, e a regra só compara
quando `env_max > 0` — então nunca dispara. O campo *Envergadura* continua no formulário e continua sendo
gravado; ele só não bloqueia. Para armar a regra depois, basta preencher `env_max` das posições que se quiser
proteger: **nenhuma tela muda**. A restrição de aeronave (`aeronave_max`) continua visível no rótulo de cada
linha da grade, que é como o operador já lê hoje.

Botão SALVAR com **trava de reentrância por carimbo de hora** que expira sozinha em 30 s — booleana simples
deixa o botão morto até reabrir o app, e `DisplayMode` não serve porque depende de `Now()`, que não reavalia.
`locSalvando` é desligada em **todos** os ramos, inclusive os de validação, e **antes** de qualquer efeito
colateral. A gravação é medida por `IsError(Patch(...))`, e só o ramo sem erro recarrega e notifica sucesso.

Exclusão é **lógica** (`ativo: 0`) e em dois toques: o primeiro arma, o segundo confirma.

## 5. Segurança

Não há lista de acesso. A permissão é a do próprio SharePoint e o app a descobre sozinho:

```powerfx
Set(varPodeEditar; DataSourceInfo('tb_alocacoesMapa'; DataSourceInfo.EditPermission))
```

Quem tem **Editar** na lista lança e realoca; quem tem **Ler** vê a grade e a legenda com os controles
desabilitados. Herança de permissão quebrada na lista, com Editar só para o grupo da operação — o mesmo
controle protege contra edição direta pela interface do SharePoint.

Trilha de auditoria: **versionamento nativo** (50 versões), ligado antes da primeira carga. Sem lista de log.

## 6. Decisões transversais

| Decisão | Porquê |
|---|---|
| Hora em **minutos desde 00:00** (`0`–`1440`) | A grade é aritmética pura; elimina fuso, elimina conversão a cada render, delega com `>=`/`<=`, e sobreposição vira comparação de inteiros |
| **Sem coluna Sim/Não** | Nasce nula e `NULL` não casa com `eq false` no OData — `!coluna` devolve zero linhas sem erro. Flags são Número, positivo `= 1`, negativo `<> 1`, nunca `= 0` |
| **Sem coluna Escolha** | Enumeração local + coluna Texto: grava o texto direto, sem `Choices()`, sem `.Value` no `Patch`, indexável, filtro `=` delegável |
| **Sem coluna Pesquisa** | Limita a 12 por view, quebra delegação e trava exclusão do pai. Relacionamento por `id_posicao` numérico |
| **Sem coluna Título** | Desobrigada e oculta; o dado sempre em coluna própria |
| `posicao_txt` e `patio_txt` redundantes | Lista legível sem o app e filtro por pátio sem cruzamento |
| **Exclusão lógica** | `ativo = 0`; o expurgo apaga de vez depois de 30 dias |
| **Nenhum fluxo chamado pelo app** | Nada que possa travar a tela esperando resposta, e nenhuma assinatura de gatilho que possa quebrar o YAML. O único fluxo é agendado |

## 7. Locale — os dois formatos que não se misturam

| Onde | Formato |
|---|---|
| `.pa.yaml` das telas | **Invariante**: `,` separa argumentos, `.` decimal |
| `App.Formulas` e a barra de fórmulas | **pt-BR**: `;` separa argumentos, `;;` termina a definição, `,` decimal |

O validador reprova `;;` dentro de `.pa.yaml`.

> **Colunas nativas em site pt-BR.** As telas leem `_r.Modificado` e `_r.'Modificado por'.DisplayName`, que são
> os nomes que o conector do SharePoint expõe em site pt-BR. Em site en-US, trocar por `Modified` e
> `'Modified By'` — são as duas únicas ocorrências, em `btnAtualizarMap.OnSelect` e `tmrSyncMap.OnTimerEnd`.

## 8. Convenções de nomenclatura

| Item | Padrão | Exemplo |
|---|---|---|
| Lista | `tb_camelCase` | `tb_alocacoesMapa` |
| Coluna | `snake_case` sem acento | `data_operacao` |
| Named formula de dado | `col*` | `colPosicoes` |
| Named formula de tema | `thm*` / `hx*` | `thmPrimaria`, `hxVerde` |
| Constante da grade | `map*` | `mapMinutosDia` |
| Variável global / de tela | `var*` / `loc*` | `varPosSel`, `locNonce` |
| Tela | `scr*` | `scrMapaPatio` |
| Controle | `cnt` `htm` `gal` `btn` `drp` `txt` `lbl` `tmr` `tgl` + descritivo + sufixo da tela | `htmTrilhoMap` |

## 9. Arquivos

```
Mapa de Alocação/
├── ARQUITETURA_MAPA.md          este documento
├── ESTRUTURA_LISTA_MAPA.md      criação da lista SharePoint
├── AppFormulas_Mapa.fx.md       dados de referência e tokens, documentado (pt-BR)
├── App_Formulas_Mapa.txt        o mesmo, concatenado, pronto para Ctrl+V
├── FLUXO_EXPURGO_MAPA.md        o fluxo agendado
├── scrMapaInicio.pa.yaml
├── scrMapaPatio.pa.yaml
├── scrMapaReferencia.pa.yaml
└── validar_telas_mapa.py        guard-rail antes de colar no Studio
```

## 10. Ordem de execução

1. Criar `tb_alocacoesMapa` por [ESTRUTURA_LISTA_MAPA.md](ESTRUTURA_LISTA_MAPA.md); versionamento ligado
   **antes** de qualquer carga; `Título` oculto; 4 índices.
2. Colar `App_Formulas_Mapa.txt` em **App → Formulas** (não no `OnStart`) e confirmar **zero erro vermelho**
   antes de abrir qualquer tela. *Erro de nome desconhecido tem precedência sobre tudo: a primeira coisa a
   conferir num painel cheio de erros é se o `App.Formulas` foi colado.*
3. Conferir as contagens: `colPosicoes` = 25, `colPortoes` = 5, `colCias` = 6, `colPatios` = 3.
4. **Confirmar com a operação** a numeração dos portões 1, 2, 3 e 5 — o 4 já está provado pela gravação. É uma
   linha em `colPortoes` se a ordem for outra.
5. `App.StartScreen = scrMapaInicio`; Configurações → Geral → **Limite de linhas de dados = 2000**.
6. Adicionar a fonte de dados `tb_alocacoesMapa` — é a única.
7. Colar as telas na ordem que resolve os `Navigate`: `scrMapaReferencia` → `scrMapaPatio` → `scrMapaInicio`.
8. Criar o fluxo de expurgo — [FLUXO_EXPURGO_MAPA.md](FLUXO_EXPURGO_MAPA.md).

## 11. Verificação

**Antes de colar:** `python3 validar_telas_mapa.py` — 20 regras herdadas de `Frotas/validar_telas.py` mais as
regras 21, 22, 23, 25, 26 e 27 deste app.

**No Studio, conectado à lista real:**

1. Abrir com usuário sem permissão de edição → botões desabilitados, mapa visível.
2. Abrir 28/08 e **conferir a grade contra a aba `SEX 28.08` do Excel** — mesmas posições, mesmas cores, mesmos
   horários. Se a operação não reconhecer o desenho, o resto não vale.
3. **Monitor aberto na abertura do app: uma única chamada ao SharePoint.** Trocar de pátio no filtro →
   **nenhuma** chamada nova.
4. Lançar T4 09:00→09:40, portão 4. Reabrir e conferir.
5. Lançar T4 09:20→10:00 → **bloqueia** nomeando o conflitante.
6. Mesmo horário, outra posição, **mesmo portão** → bloqueia.
7. Lançar em T3 → pede confirmação de contingência no segundo toque em SALVAR.
8. Realocar um voo pelo painel; a grade redesenha e o painel mostra quem alterou e quando.
9. Marcar como pesquisado → selo `P` e borda vermelha. Criar `INTERDICAO` em A5 das 08:00 às 18:00 → faixa
   cinza e voo naquele intervalo bloqueado.
10. Dois navegadores no mesmo dia: um altera; no outro, em até 60 s, aparece a faixa — **sem** recarregar por
    baixo de quem está editando.
11. Testar com **limite de delegação = 1** → a grade continua completa.
12. Rodar o expurgo manualmente com data forjada e conferir as duas fases.
