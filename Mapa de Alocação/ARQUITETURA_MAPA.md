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
quatro tinham sido numerados por convenção, do frio para o quente. **A operação confirmou a numeração real**
(31/08/2026): `#00B050` 1 · `#FFFF00` 2 · `#00FFFF` 3 · `#FF0066` 4 · `#C9C5E6` 5. Trocar a numeração é **uma
linha** em `colPortoes`, porque a lista guarda o número, nunca a cor.

> **Duas variantes de vermelho na planilha — mapeamento agora em aberto.** Os contornos aparecem como `#FF0000`
> e `#F22727` — a mesma intenção, com a deriva de quem escolhe a cor à mão a cada caixa. A nota original dizia
> que as duas viram portão 5 ao transcrever os dias antigos, porque na heurística frio-para-quente o portão 5
> era vermelho. **Não é mais**: a numeração confirmada usa `#C9C5E6` (um lilás/cinza) no portão 5, e nenhuma
> cor de `colPortoes` é vermelha. Falta confirmar com a operação para qual portão os blocos vermelhos das 47
> abas antigas devem ser transcritos antes de migrar o histórico.
>
> **Portão 5 e a companhia ONE compartilham `#C9C5E6`.** É a mesma cor de `hxBorda` e do preenchimento da
> companhia ONE em `colCias`. Um voo da ONE no portão 5 tem contorno e preenchimento idênticos — vale confirmar
> se isso é aceitável na leitura da grade ou se o portão 5 precisa de outro tom.

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

> **Preparado para um segundo aeroporto, ainda cadastrado só pelo desenvolvedor (31/08/2026).** `colPatios` e
> `colPosicoes` carregam uma coluna `aeroporto` (ICAO). Nenhuma tela lê essas duas direto — todas leem
> `colPosicoesAero`/`colPatiosAero`, que filtram por `varAero` e caem de volta para a tabela inteira se o filtro
> não achar nada (rede de segurança contra tela em branco — ver `AppFormulas_Mapa.fx.md` seção 6). Hoje só
> existe `SBNF`, então não muda nada visível — mas incluir o segundo aeroporto é acrescentar linhas em
> `App.Formulas` com o novo ICAO, sem tocar em tela nenhuma. Continua **fora de escopo** dar à operação uma tela
> para cadastrar posição/pátio sozinha — isso só vira necessário (e só então compensa migrar para lista
> SharePoint, pelo mesmo critério da tabela acima) quando um segundo aeroporto realmente entrar.

## 3. Estratégia de coleções — o núcleo da performance

**Uma chamada de rede por dia carregado. Todo o resto em memória.**

| Coleção | Origem | Recalculada quando | Tamanho |
|---|---|---|---|
| `colDia` | Uma consulta delegável a `tb_alocacoesMapa` — `data_operacao <= dia And data_fim >= dia` | Carregar o dia · salvar · excluir · ATUALIZAR | ~40 |
| `colGrade` | `colPosicoes` × `colDia`, em memória | Sempre que `colDia` muda | 25 (uma por posição) |

`colDia` é projetada com `ForAll(… As _r, {…})` — não `ShowColumns("…")`, que é erro de parsing e derruba a
fórmula inteira gerando dezenas de erros derivados sem relação com a causa.

`colGrade` guarda, por posição, o **HTML da linha já montado**. A galeria fica no mais barato que existe:

```
galPosicoesMap.Items =Filter(colGrade, locPatio = "TODOS" Or patio = locPatio)
htmLinhaMap.HtmlText =ThisItem.html
htmLinhaMap.Fill     =If(varPosSel.id_posicao = ThisItem.id_posicao, thmPrimariaClara, thmSuperficie)
```

**Uma linha da grade é um controle só.** Rótulo da posição e trilho de horas moram na mesma tabela HTML, no
mesmo `HtmlViewer` — 25 controles no template, não 50. E o realce da posição selecionada é o `Fill` do
controle, não HTML: trocar de posição não remonta string nenhuma, só repinta o fundo.

### As regras que as telas respeitam

1. **Nenhum `LookUp`, `Filter` ou `First(Sort(...))` sobre a fonte de dados dentro de template de galeria** —
   seria uma consulta por linha por render. Todo cruzamento (posição × cor da cia × cor do portão) é resolvido
   na montagem de `colGrade`. Reprovado pela regra 21 do validador.
2. **Nenhuma propriedade do template lê `galPosicoesMap.Selected`** — dependência circular; o Power Apps
   devolve branco em silêncio, sem erro. A seleção trafega por `varPosSel`, gravada no `OnSelect` do
   `HtmlViewer` da linha. Reprovado pela regra 23.
3. **Filtros de tela são em memória.** Trocar de pátio é `Filter(colGrade, …)` — zero rede. Só trocar de
   **data** ou de **aeroporto** vai ao SharePoint.
6. **Recarga governada por um único ponto.** `btnAtualizarMap.OnSelect` contém o bloco de recarga inteiro
   (`colDia` → `colGrade`); `OnVisible`, salvar, excluir e os botões de data chamam `Select(btnAtualizarMap)`.
   Isso também resolve a armadilha de `Navigate` para a própria tela não reexecutar o `OnVisible` — em vez de
   duplicar o bloco, existe uma cópia só.
7. **Nunca `CountRows`/`CountIf` sobre a lista.** Os contadores da barra contam `colDia`. Reprovado pela regra 22.
8. **Sincronismo multiusuário barato.** `tmrSyncMap` a cada 60 s compara o `Modificado` mais recente do dia no
   servidor com o mais recente em `colDia`. Diferente → aparece a faixa *"a programação foi alterada"* com o
   botão ATUALIZAR. **Não recarrega sozinho por baixo de quem está editando.** Uma consulta por minuto, e o
   timer é barrado por `varMapaVisivel` — `AutoStart` + `Repeat` continua rodando com a seção invisível
   (regra 27 do validador).
9. **`App.OnStart` vazio de propósito.** Named formula não custa nada até ser lida. Nada de `ClearCollect` de
   dado estático na abertura.
10. **Limite de linhas de dados = 2000.** Coleção maior que o limite trunca **em silêncio**.

Resultado na abertura: **uma** requisição HTTP.

## 4. Telas

| Tela | Papel |
|---|---|
| `scrMapaInicio` | Apresentação, como ler a grade, seleção de aeroporto e data, resolução de permissão |
| `scrMapaPatio` | A grade, o painel de edição (popup), os filtros e a legenda |
| `scrMapaReferencia` | Posições, portões e companhias em leitura, com as cores aplicadas |

Shell comum: trilho lateral roxo (`cntMenu*`, 236 px aberto / 76 recolhido) + barra de título de 72 px. O
trilho é **gerado com sufixo por tela** (`Map`, `Ref`), nunca copiado no Studio — copiar faz o Studio renomear
para `_1` e quebrar o YAML, e nome de controle é único no app inteiro, não por tela.

### Como a grade é desenhada

Power Apps não tem Gantt, e `HtmlViewer` não devolve clique por elemento — então desenho e clique são
separados, e é isso que torna a solução simples:

- **Uma geometria só, definida no HTML.** A linha é uma tabela `table-layout:fixed` de duas colunas: rótulo
  com `width:132px` e trilho com o que sobrar. A régua do topo é **a mesma tabela**, com a mesma primeira
  coluna em px. Como as duas ocupam a mesma largura de controle, o navegador resolve o alinhamento — nenhuma
  conta de `X`/`Width`/padding em Power Fx precisa bater com outra.
- **A largura de controle é a mesma porque as duas descontam a mesma constante.** `htmReguaMap` reserva
  `mapLarguraBarra` em `PaddingRight`; `htmLinhaMap` usa `galPosicoesMap.Width - mapLarguraBarra`. É o espaço
  da barra de rolagem da galeria. *Era exatamente aqui que a grade antiga desalinhava: régua e trilho eram
  controles independentes, cada um com seu padding — e o `HtmlViewer` tem padding próprio diferente de zero,
  que precisa ser zerado explicitamente nos quatro lados.*
- Dentro do trilho, um `<td>` por segmento com **largura em porcentagem** de `hora_inicio`/`hora_fim`:
  `(fim − ini) × 100 / 1440`.
- `<table>` e não flexbox, e nenhum `<svg>` nem emoji — o sanitizador do `HtmlViewer` remove SVG e flexbox não
  sobrevive em todo cliente. `background-image: repeating-linear-gradient` **passa** pelo sanitizador (o mesmo
  recurso já roda em `DueDiligence/ScreenDueDiligenceInicio.yaml`) e é o que desenha as linhas verticais de
  hora por baixo dos vãos.
- **A régua e a grade desenham a linha de hora com o mesmo mecanismo, a partir da mesma definição:**
  `mapFundoHoras`, no `App.Formulas`. Não é preciosismo. A régua desenhava com `border-left` de célula e a
  grade com gradiente; borda de célula o navegador **encaixa em pixel inteiro**, gradiente ele rasteriza em
  **espaço contínuo**. Em 100 % numa tela comum os dois caem no mesmo lugar e parece resolvido — em zoom de
  110 %/125 % ou tela HiDPI cada um arredonda para um lado e a linha de baixo sai até 1,25 px da de cima,
  desalinhada de um jeito que varia coluna a coluna. Com a mesma declaração CSS sobre elementos de mesma
  largura, o erro medido cai para 0,03 px em qualquer zoom. A porcentagem da coluna de hora sai da mesma
  fonte (`mapPctHora`), então largura de célula e período do gradiente não podem divergir.
- `border-collapse:separate;border-spacing:0` com `box-sizing:border-box` em toda célula: no layout fixo a
  largura declarada é a da caixa **com** a borda, então os 3 px de contorno do portão saem de dentro do bloco
  e não empurram o vizinho.
- **As linhas horizontais são `border-top` das células, nunca `border-bottom`.** A borda de baixo cai no
  limite recortado pela altura do controle e some; a de cima sempre aparece. A primeira posição de cada pátio
  leva uma borda mais forte, que é o único separador de grupo da grade.
- `Text(x, "0.000", "en-US")` — **a tag de idioma é obrigatória**: em cliente pt-BR, `Text(3.47, "0.000")`
  devolve `3,470` e quebra o `width:` do CSS. Reprovado pela regra 26 do validador.
- **Cursor monotônico, e não a subtração do bloco anterior.** O início efetivo de cada bloco é
  `Max(ini, cursor)` e o cursor é `Max(FirstN(_bl, i-1), Max(ini, fim))`, tudo grampeado em `[0; 1440]`. Some
  a possibilidade de largura negativa: dois registros sobrepostos, ou um com saída antes da chegada, davam um
  `width:-12.500%` que o navegador descarta — e aí o layout fixo redistribuía a linha inteira, jogando os
  blocos seguintes **horas para a esquerda**. A validação ao salvar impede a sobreposição pelo app, mas não
  impede edição direta no SharePoint nem dado herdado da planilha. Com o cursor, o pior caso é um bloco
  desenhado truncado — a linha continua correta, e o rótulo continua mostrando o horário real gravado.
  A soma das larguras é exatamente 100 % em qualquer entrada (provado por teste de propriedade sobre 5000
  casos aleatórios mais os dirigidos: sobreposto, engolido, empate, invertido, fora do dia).
- Cor do `<td>`: `background` = `cor_hex` de `colCias`; `border: 3px solid` = `cor_hex` de `colPortoes`, **sempre**
  — nunca muda por causa de pesquisado ou bloqueio, porque a legenda diz "contorno = portão" e trocar a borda
  junto confundiria as duas informações (decisão da operação, 31/08/2026). Quando `pesquisado = 1`, o `background`
  vira `hxVermelho` com selo `P`; quando o tipo não é `VOO`, vira cinza `hxTextoFraco` + `INTERDITADO`. **Nenhuma
  cor literal entra no `.pa.yaml`** (regra 16).
- **`varForm` é montado em um lugar só, por dois botões-função.** `btnAbrirEdicaoMap` traduz `varAlocSel`
  em formulário; `btnAbrirNovoMap` monta o formulário em branco com a posição e, se houver, o `HH:00` que
  veio de `varNovoIni`. Os quatro pontos de entrada (bloco na grade, hora livre na grade, NOVO REGISTRO,
  item da lista do painel) só preparam a variável e chamam `Select`. Antes disso, o clique na linha abria o
  painel **sem tocar em `varForm`** e o formulário mostrava o que tivesse sobrado da edição anterior.
  `varNovoIni` é **global de propósito**, e não variável de contexto: numa mesma fórmula, `Set` chega ao
  `OnSelect` chamado por `Select()` e `UpdateContext` **não** chega — o alvo lê o valor anterior. Foi
  exatamente esse o defeito da primeira versão: a posição (via `Set`) vinha, a hora (via `UpdateContext`)
  vinha sempre `-1`.
  Os dois botões são `Visible: =true` de propósito, com 1×1 px atrás do container da tela: **`Select()` num
  controle invisível é no-op** — erro já cometido no PlemPrai (`ScreenAcionamentosPlemPraiV2.pa.yaml`).
- **A dica de mouse é o atributo `title` do `<td>`, e é a única forma que existe.** O `HtmlViewer` não devolve
  evento por elemento — nem clique nem `hover` —, então não há como o Power Fx saber sobre qual bloco o
  ponteiro está. Balão em CSS (`:hover` + filho absoluto) também não serve: cada linha da grade é um
  `HtmlViewer` de `mapAlturaLinha` px de altura e o balão seria **recortado na borda do controle**. O
  `title` nativo é desenhado pelo navegador **fora** da caixa da página, e é o que escapa do recorte.
  **Confirmado no app em 02/09/2026:** o sanitizador do `HtmlViewer` **preserva** o atributo `title` do
  `<td>`, e o balão aparece. Era a única premissa da funcionalidade que não dava para provar fora do
  Studio; até então não havia precedente de atributo `title` em nenhum módulo do repositório.
- **O texto da dica é montado em `colDia`, não no HTML.** Uma vez por registro no carregamento, em vez de
  uma vez por render — e é o que permite escapar o conteúdo num ponto só. Todo campo livre
  (`observacao`, `prefixo`, `voo_*`, nome de quem alterou) entra escapado: `&` → `&amp;` **primeiro**,
  depois `<`, `>` e `'` → `&#39;`, e por último `Char(10)` → `&#10;`, que é o que quebra linha dentro do
  `title`. A ordem não é estética: escapar `&` depois de `<` transformaria o `&lt;` recém-criado em
  `&amp;lt;`, e converter `Char(10)` antes de escapar `&` transformaria o `&#10;` em `&amp;#10;`.
  Sem isso, **uma aspa simples digitada na observação fecha o atributo e desmonta a linha inteira da grade**.
- **O clique sabe onde caiu por uma camada de células de hora, não pelo HTML.** O `HtmlViewer` devolve um
  único `OnSelect` por linha, sem coordenada — ele diz *qual posição*, nunca *que hora*. Por cima de cada
  linha fica `cntFaixaMap`, um container **AutoLayout** com um vão fixo da largura da coluna de rótulo e
  **24 células iguais**, uma por hora. Cada célula pergunta a `trechos` se algum bloco cruza aquela hora:
  se cruza, o clique abre **aquele** registro com o formulário preenchido; se não cruza, abre registro novo
  já com a posição e `HH:00`.
- **A camada é AutoLayout porque `X` não sobrevive à colagem.** A primeira versão posicionava um rótulo por
  bloco em absoluto, com `X` calculado de `trechos` — exato ao minuto. O Studio **descarta o `X` dos filhos
  do template da galeria ao colar a tela** e grava `1` no lugar (o `Width`, na mesma colagem, é mantido).
  Os 33 rótulos empilhavam no canto esquerdo e o clique caía sempre no mesmo. Digitado à mão no Studio o
  `X` funciona e persiste — o que não dá é entregá-lo por YAML. Em AutoLayout a posição vem de
  `FillPortions`, que é da mesma família do `Width` e sobrevive.
- **A compatibilidade do equipamento é checada em três degraus, nesta ordem.** `EQUIPAMENTO` é
  obrigatório para `tipo_registro = "VOO"`; depois vem o **veto da própria posição**
  (`tb_regrasPosicao` com `vizinha` vazia), depois o **veto de par** — que só dispara quando a posição
  vizinha está ocupada por um equipamento da lista `equip_b` **e** os dois períodos se cruzam em
  minutos absolutos. A envergadura é o último degrau, e não o primeiro, porque existe regra que
  nenhuma medida produz: T4 aceita um 737-800 de 35,79 m e recusa um E195-E2 de 35,10 m.
- **`envergadura_m` virou derivada.** No salvar vale o que foi digitado; em branco, herda
  `tb_equipamentos[equipamento].envergadura_m`. **Desde 04/09/2026 o campo é só de leitura**, a pedido da supervisão: se a envergadura
  vem do catálogo, o operador não precisa e não deve mexer. Ele mostra a do equipamento escolhido no
  momento, não a que estava gravada.

  **O que se perdeu:** a saída para cauda fora do padrão. Quem tiver uma corrige a envergadura em
  `tb_equipamentos`, que é onde ela mora — mais certo que corrigir registro a registro, mas é um passo
  a mais e vale saber que existe.
  Enquanto `env_max` estiver `0` em todas as posições, esse degrau não recusa nada — está ligado e
  inerte, esperando o dado.
- **As regras não são delegáveis e não precisam ser.** `colEquip` e `colRegras` são carregadas uma vez
  no `OnVisible` da tela, não a cada ATUALIZAR — é o que mantém a invariante de que abrir um dia
  continua sendo uma única chamada ao SharePoint. O veto de par lê `colValida`, que o salvar já monta.
- **Registro novo aberto pelo clique já vem com chegada e saída.** A chegada é o `HH:00` da célula; a
  saída é `chegada + mapDuracaoPadrao`. É sugestão de formulário, não regra: quem digita sobrescreve, e a
  validação de conflito continua sendo a mesma na hora de salvar. Aberto pelo botão NOVO REGISTRO ou pela
  coluna de rótulo — onde não há hora nenhuma — os dois campos continuam vazios.
- **`TextInput@0.0.54` não tem cor de placeholder.** Só `FontColor`, que pinta também o valor digitado. Por
  isso o placeholder que parecia dado preenchido virou `ex. 09:00`, `ex. PSESP`: o prefixo é o que separa
  exemplo de valor, já que a cor não separa. Cuidado ao editar: `ex.: 09:00` **quebra o YAML** — dois-pontos
  seguido de espaço num escalar simples abre um mapeamento.
- **O preço da célula de hora:** a hora que contém qualquer parte de um bloco pertence a ele por inteiro, e
  dois registros dentro da mesma hora abrem o mais cedo. É deliberado: o erro cai sempre para o lado de
  *abrir um registro existente*, nunca para o de criar um novo por cima de um bloco visível. Em troca, não
  há teto de blocos por posição — a busca varre `trechos` inteiro.
- **`trechos` é a mesma conta que pinta e que recebe o clique.** A geometria de cada bloco (recorte ao dia,
  clamp em 0 e 1440, telescopagem quando dois registros se sobrepõem) é calculada **uma vez** em `colGrade`,
  e dali sai tanto o `<td>` pintado quanto a resposta de *que bloco está nesta hora* que cada célula da
  camada faz. Recalcular a geometria dos dois lados faria a pintura e o clique divergirem no primeiro
  arredondamento diferente.
- **O rótulo de bloco carrega a dica em `Tooltip`, não no `title` do `<td>`.** Cobrindo o HTML, ele passaria
  a frente do `title` e a dica sumiria. `Label@2.5.1` tem `Tooltip` comprovado (`Rectangle@2.3.0` **não**
  tem — foi o que decidiu o tipo de controle da camada). Por isso `colDia` publica a dica em duas versões:
  `dica_txt` crua para o `Tooltip` e `dica` escapada para o `title`, que continua no HTML e volta a valer
  quando a camada se desliga.
- **Posição pode consumir outra: a coluna `ocupa` em `colPosicoes`.** `T6C` é a área de carga que
  ocupa fisicamente `T5` e `T6`, e declara isso em `ocupa: "T5,T6"`. **O fato é declarado num lugar
  só** — `T5` e `T6` não têm nada escrito — porque a gravação resolve nos dois sentidos: quem eu
  consumo e quem me consome. Declarar dos dois lados criaria duas verdades para manter, e a que
  ficasse desatualizada silenciaria o bloqueio.
- **Posição composta não vira linha da grade.** `colGrade` desenha só `Filter(colPosicoesAero,
  IsBlank(ocupa))`. O registro que está no `T6C` é desenhado **como bloco normal nas linhas do `T5` e
  do `T6`** — na tela isso lê como um retângulo único cobrindo as duas, que é o que fisicamente
  acontece no pátio. Ela continua no seletor do formulário: some do desenho, não do cadastro.
- **A primeira tentativa foi linha própria com bloco-sombra e foi descartada** (02/09/2026): a `T6C`
  aparecia como faixa e cada ocupação era desenhada duas vezes, uma real e uma tracejada, nos dois
  sentidos. Ficou mais poluído do que informativo. **Uma posição que é o mesmo espaço físico de outras
  duas não é uma terceira linha — é o mesmo lugar.** O desenho tinha que dizer isso.
- **A mensagem de conflito nomeia a posição que conflitou, não a escolhida.** Quando o choque é
  cruzado, ela acrescenta *e ela ocupa o mesmo espaço físico de T5* — senão o operador leria
  "T6C já ocupada" tendo escolhido `T5`, e não entenderia.
- **Dois selos convivem no bloco: `P` de pesquisado e `I` de internacional.** São marcas independentes
  — um voo pode ter as duas. A diferença de tratamento é deliberada: **pesquisado repinta o bloco**
  inteiro de vermelho, porque é condição operacional que muda a leitura da grade inteira;
  **internacional é só o selo amarelo**, porque é atributo do voo e não deve competir com a cor da
  companhia, que é o que a legenda promete. Se os dois pintassem o fundo, a grade perderia a regra de
  que preenchimento = companhia.
- **Internacional tem padrão, pesquisado não.** `internacional` é obrigatória com `Default 0`: todo voo
  é doméstico até dizerem o contrário, e o acervo antigo já nasce correto sem migração nenhuma.
- **Bloco que continua noutro dia leva `«` na entrada e `»` na saída**, e o rótulo de horas mostra o
  intervalo **recortado ao dia** (`22:00–24:00»`, `«00:00–06:10`), nunca o intervalo real. É o que mantém o
  bloco coerente com a régua: o desenho e o texto dizem a mesma coisa. O intervalo real, com as duas datas,
  está na dica e no painel.

### Como se edita — os dois cliques pedidos

Toque na linha → `OnSelect` do `HtmlViewer` grava `varPosSel` e abre o painel com os voos daquela posição
(vindos de `colDia`). Toque no voo → o formulário carrega e o cabeçalho mostra `Modificado`/`Modificado por`.

**O painel é popup, não coluna fixa.** Ele e o véu (`recVeuMap`) são filhos **da tela**, depois do
`cntShellMap` — em `.pa.yaml` quem vem depois desenha por cima. Fora do AutoLayout eles aceitam `X`/`Y`, e o
painel ancora à direita com `X: =Parent.Width - Self.Width`. Ficam invisíveis enquanto `varPainelAberto` for
falso, então a grade usa a largura inteira da tela o tempo todo — que é o que dá espaço aos blocos estreitos.
Tocar no véu fecha. O `Visible` mora **só** no véu e no container do painel: os filhos herdam, e cada
`Visible` a menos é uma expressão a menos para reavaliar.

O formulário é **controles avulsos com `Patch`**, não um `Form`/`DataCard`. Isso elimina de saída as
armadilhas de `MetadataKey: FieldValue` duplicado e da ordenação por `Y` dos DataCards.

Os quatro seletores usam o padrão do repositório: `Items` de **coluna única `Value`**,
`DefaultSelectedItems: =[valor]` e um **nonce** (`Items: =Filter(colXSel, locNonce >= 0)`, `locNonce`
incrementado a cada troca de seleção) — sem o nonce, o dropdown moderno não volta ao padrão quando o valor
novo é igual ao que ele já mostrava.

### Validação ao salvar

Uma consulta por salvamento — não por render:

1. `HH:mm` válido, entre `00:00` e `24:00`; chegada obrigatoriamente antes de `24:00`.
2. `data_fim >= data_operacao`, e o intervalo total dentro de `mapDiasMax`.
3. Saída depois da chegada **na linha do tempo absoluta** — pernoite é um registro só, com a DATA FINAL no
   dia da saída.
4. **Sobreposição na posição** — bloqueia e nomeia o registro conflitante com data, horário e prefixo.
5. **Portão ocupado** no mesmo intervalo, em qualquer posição — **avisa e pede confirmação** no segundo toque em SALVAR. Era bloqueio; virou aviso em 03/09/2026, porque a operação reaproveita portão e o bloqueio impedia lançamento legítimo. Conflito de *posição* continua bloqueando: dois aviões não cabem no mesmo lugar, mas dois voos podem compartilhar um portão.
6. **Envergadura** acima do `env_max` da posição — **dormente**, ver abaixo.
7. **Posição de contingência** (a **T7**) — pede confirmação, não bloqueia. Era a T3 até 03/09/2026.

**Por que deixou de ser custo zero.** Sobreposição só é comparável entre registros que estejam na mesma
linha do tempo, e `colDia` só tem o dia carregado. Um registro que vai de 03/09 a 07/09 tem que ser
confrontado com o que existe nos cinco dias, e quatro deles não estão em memória. Validar só contra
`colDia` seria uma **validação furada silenciosa** — o app deixaria gravar em cima de uma interdição que
ele simplesmente não carregou. Então o SALVAR faz uma consulta delegável pela faixa
(`data_operacao <= fim And data_fim >= ini`), projeta em `colValida` e compara tudo em **minutos absolutos**
(`DateDiff(mapDataBase; data; Days) * 1440 + minuto`), que é a mesma aritmética de inteiros de antes, só que
sem o teto de 1440. Uma chamada a mais numa ação que já fazia duas (o `Patch` e a recarga); a **renderização**
continua com uma consulta por dia carregado, que é onde o custo importava.

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
| **Intervalo em duas datas** (`data_operacao`+`hora_inicio` → `data_fim`+`hora_fim`) | Pernoite e interdição de vários dias são **um** registro, não N. Editar é editar um item; excluir é excluir um item; o histórico do Power BI não precisa reagrupar nada. A alternativa — gerar um registro por dia — multiplicaria a gravação por N sem transação, e deixaria a edição dependente de um `grupo_id` |
| **A grade recorta o registro ao dia** (`ini`/`fim` calculados) | A régua é de 24 h por definição do produto: coluna é hora do dia. Um registro de 5 dias vira 5 barras, uma por grade, com `«`/`»` nas pontas. As colunas cruas (`h_ini`/`h_fim`/`data_*`) andam junto em `colDia` porque o **painel de edição tem que mostrar o valor real**, não o recortado — editar a partir do dia do meio e gravar `00:00` seria destruir o registro |
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
| Controle | `cnt` `htm` `gal` `btn` `drp` `txt` `lbl` `tmr` `tgl` `rec` + descritivo + sufixo da tela | `htmLinhaMap` |

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
4. ~~Confirmar com a operação a numeração dos portões 1, 2, 3 e 5~~ — **confirmado em 31/08/2026** (seção 1). O 4
   já estava provado pela gravação. **Pendente:** para qual portão transcrever os blocos vermelhos das 47 abas
   antigas do Excel, já que nenhuma cor de `colPortoes` é mais vermelha.
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
3. **Alinhamento:** com um voo às 10:00, a borda esquerda do bloco tem que encostar no traço da coluna `10` da
   régua. Encolher a janela e conferir de novo — a régua é percentual, o alinhamento tem que sobreviver.
   Conferir também que **toda** posição mostra a linha horizontal, inclusive as sem nenhum voo.
4. **Painel:** tocar numa posição abre o painel **sobre** a grade, e a grade continua com a largura toda.
   Tocar fora (no véu) fecha. Com o painel fechado não existe coluna vazia à direita.
5. **Monitor aberto na abertura do app: uma única chamada ao SharePoint.** Trocar de pátio no filtro →
   **nenhuma** chamada nova.
6. Lançar T4 09:00→09:40, portão 4. Reabrir e conferir.
7. Lançar T4 09:20→10:00 → **bloqueia** nomeando o conflitante.
8. Mesmo horário, outra posição, **mesmo portão** → avisa; segundo toque em SALVAR grava.
9. Lançar em T7 → pede confirmação de contingência no segundo toque em SALVAR.
10. Realocar um voo pelo painel; a grade redesenha e o painel mostra quem alterou e quando.
11. Marcar como pesquisado → selo `P` e borda vermelha. Criar `INTERDICAO` em A5 das 08:00 às 18:00 → faixa
    cinza e voo naquele intervalo bloqueado.
12. Dois navegadores no mesmo dia: um altera; no outro, em até 60 s, aparece a faixa — **sem** recarregar por
    baixo de quem está editando.
13. Testar com **limite de delegação = 1** → a grade continua completa.
14. Rodar o expurgo manualmente com data forjada e conferir as duas fases.
15. **Dica de mouse:** parar o ponteiro sobre um bloco → aparece o balão com posição, pátio, companhia por
    extenso, prefixo, envergadura, período com as duas datas, portão, observação e quem alterou. Confirmado
    em 02/09/2026. **Se o balão parar de aparecer depois de alguma atualização da plataforma, é o sanitizador
    do `HtmlViewer` removendo o `title`** — testar isso antes de procurar erro na montagem do texto.
16. **Clique no bloco:** clicar em cima de um bloco abre o painel com **aquele** registro marcado na lista e
    o formulário preenchido — tipo, posição, as duas datas, chegada e saída reais, companhia, voos, portão,
    envergadura e observação. Com dois blocos na mesma hora, conferir que abre o que está debaixo do ponteiro,
    não o primeiro da hora. Num pernoite aberto **pelo dia seguinte**, conferir que a chegada mostra `22:00`
    e não `00:00` (o formulário lê `h_ini`/`h_fim`, não o recorte do dia).
17. **Clique em espaço livre:** clicar numa hora vaga abre registro novo com a posição da linha e a chegada
    em `HH:00` daquela faixa. Testar também numa **posição vazia o dia inteiro** — clicar às 14h tem que
    trazer `14:00`, não `00:00`. Clicar na coluna de rótulo (à esquerda) abre registro novo **sem** hora.
18. **Posição cheia:** numa posição com muitos blocos no dia, conferir que **todos** abrem pelo clique — a
    camada não tem teto de blocos. Conferir também que hora com dois registros abre o mais cedo.
19. **Alinhamento da camada:** clicar bem na borda esquerda e na borda direita de um bloco. Se o clique na
    borda abrir *novo registro* em vez do bloco, a camada está deslocada do HTML — conferir
    `mapLarguraRotulo` e `mapLarguraBarra`, que são o que as duas geometrias têm em comum.
20. **Dica com aspa:** gravar uma observação contendo `'` e `&` (por exemplo `manutenção d'asa & motor`) e
    conferir que a linha da grade **continua inteira** e o balão mostra o texto literal. É o teste que pega
    escape faltando — sem ele o atributo fecha no meio e a linha se desmonta.
21. **Pernoite:** lançar T4 chegada 22:00 com DATA FINAL no dia seguinte, saída 06:10. No dia D o bloco vai de
    22:00 até a borda direita com `»`; no dia D+1 começa na borda esquerda com `«` e termina 06:10. Abrir o
    registro pelo painel **no dia D+1** e conferir que o formulário mostra `22:00`/`06:10` e as duas datas —
    não `00:00`. Salvar sem mudar nada e conferir que o desenho não se altera.
22. **Interdição de vários dias:** `INTERDICAO` em A5 de D a D+4, 08:00 → 17:00. Conferir os cinco dias: D com
    `»`, D+1 a D+3 cheios com `«`…`»`, D+4 com `«`. Tentar lançar um voo em A5 em D+2 → **bloqueia**, mesmo
    com o dia D+2 nunca tendo sido aberto na sessão.
23. **Conflito só visível fora do dia carregado:** com a grade aberta em D, lançar um registro em D+3 que
    conflita com algo que só existe em D+3 → bloqueia. É o teste que prova que a validação consulta a faixa e
    não `colDia`.
24. **DATA FINAL antes da inicial** e **período acima de `mapDiasMax`** → bloqueia nos dois casos.
25. Conferir no Monitor que **abrir um dia continua sendo uma única chamada**, e que o SALVAR faz três
    (validação, `Patch`, recarga) — não uma por dia do intervalo.

## Telas de cadastro: `scrMapaEquip` e `scrMapaRegra`

O SharePoint já dá CRUD de graça nas duas listas. **Estas telas não existem pelo formulário, existem
pelas travas** — sem elas, um código de equipamento digitado errado em `tb_regrasPosicao` produz uma
regra que nunca dispara, e isso é indistinguível de *não há regra*. Ninguém percebe até o dia em que
a alocação proibida passa e o sistema não reclama.

O que as telas garantem e a interface do SharePoint não:

| trava | onde | por quê |
|---|---|---|
| equipamento escolhido em `ComboBox`, nunca digitado | `cmbEqaRgr` / `cmbEqbRgr` | código inexistente = regra morta |
| posição escolhida em `DropDown` de `colPosicoesAero` | `drpPosRgr` / `drpVizRgr` | idem, e impede posição de outro aeroporto |
| código de equipamento duplicado é recusado | `btnSalvarEqp` | o contrato do `List_Generator` não carrega `EnforceUniqueValues`; duplicata faz o `LookUp` depender da ordem de inserção |
| regra de par sem os dois lados é recusada | `btnSalvarRgr` | regra pela metade nunca dispara |
| vizinha igual à própria posição é recusada | `btnSalvarRgr` | regra que se auto-satisfaz |
| mensagem obrigatória | `btnSalvarRgr` | é o texto que o operador lê quando o salvar é recusado; sem ele a recusa fica muda |

**Nada é apagado: `ativo` faz o desligamento.** Equipamento inativo some do seletor sem quebrar
registro antigo que o referencia; regra inativa para de valer sem perder o histórico de que existiu.

**Quem pode editar é o SharePoint que decide.** `varPodeCatalogo` sai de
`DataSourceInfo(<lista>; DataSourceInfo.EditPermission)`, então a permissão de cada lista controla o
acesso — não há papel replicado dentro do app. Sem permissão, as telas abrem em somente leitura e a
barra diz isso.

**O que ainda não existe, e é o próximo passo natural:** um botão *testar regra*, que varreria os
registros já gravados e diria quantos aquela regra teria recusado. É o que pega regra larga demais
**antes** de ela travar a operação. Ficou de fora desta entrega de propósito, para não estrear duas
coisas ao mesmo tempo.

---

## Por que a checagem de envergadura continua inerte

Tentativa de 04/09/2026, medida e descartada.

A ideia era dispensar o preenchimento de 25 `env_max` à mão: cada posição já declara `aeronave_max`
em texto (`"B-738"`, `"EMB. E-2"`, `"B-767 CARGO"`), e o catálogo `tb_equipamentos` tem envergadura por
equipamento. Bastaria cruzar os dois. A coluna **`equip_max`** foi acrescentada a `colPosicoes` com o
código do catálogo correspondente, e ficou — é dado correto e útil.

**O que a medição mostrou:** ligada assim, a checagem rejeitaria **399 dos 698 voos de setembro, 57%**.

| quantos | caso |
|---|---|
| 166 | A320 (35,80 m) na T6, limite B738 = 35,79 m |
| 125 | B738 (35,79 m) na T3, limite E295 = 35,10 m |
| 33 | A319 (35,80 m) na T6 |
| 32 | A320 na T4 |
| 43 | outros |

São dois defeitos diferentes de premissa:

1. **`aeronave_max` nomeia uma classe de porte, não um teto em centímetros.** A320 e 737-800 diferem
   em **1 cm** e são operacionalmente do mesmo tamanho. Comparar envergadura exata transforma isso em
   proibição.
2. **A T3 recebe 737 rotineiramente** — é a segunda preferência da GOL — mas declara `"EMB. E-2"`. Ou a
   declaração está errada, ou significa outra coisa que não "maior aeronave aceita".

**O que seria preciso decidir**, e não é decisão de quem programa: uma tolerância resolveria o primeiro
caso (1 m já bastaria), mas escolher esse número olhando para os dados que se quer aprovar é fabricar
uma margem de segurança aeronáutica a partir de estatística. **O limite real não é envergadura, é
distância de ponta de asa**, e esse número tem que vir da operação.

Enquanto isso: `locEnvMax` fica **calculado** no `btnSalvarMap`, pronto para uso, e a validação segue
comparando `env_max`, que é `0` em todas as posições — inerte, como antes. Trocar uma linha liga tudo,
quando os limites existirem.

---

## Dois testes físicos, com pesos diferentes

Enquadramento dado pelo Douglas em 04/09/2026, a partir do **RBAC 154 da ANAC**. Ele corrige a
premissa da tentativa anterior — que comparava envergadura contra um rótulo de classe e rejeitava 57%
dos voos reais.

**Comprimento bloqueia.** É limite físico medido do box: cabe ou não cabe. Compara
`comprimento_m` do catálogo contra `comp_max` da posição.

**Envergadura pergunta.** No pátio principal a restrição do RBAC 154 é sobre **distância entre
aeronaves lado a lado**, não sobre a aeronave sozinha. Uma aeronave mais larga que o previsto pode
entrar **desde que a posição vizinha fique livre** — e isso é decisão da operação, não do sistema.
Então a mensagem diz o que está em jogo e pede confirmação no segundo toque em SALVAR.

Essa é a diferença que a tentativa anterior não tinha: **o limite de envergadura não é uma proibição,
é uma condição.** Bloquear apagava a única saída legítima que o operador tem.

### Ambos inertes até haver medida

`comp_max` nasce `0` em todas as 25 posições e `env_max` continua `0` — com isso nenhum dos dois
dispara. **É de propósito:** o número tem que vir de medição do pátio, não de tradução de rótulo. Foi
exatamente derivar limite de rótulo que produziu os 57% de rejeição.

O catálogo `tb_equipamentos` ganhou **`comprimento_m`**, e a tela de cadastro ganhou o campo. Os 25
comprimentos vieram de especificação publicada de fabricante — **mesma ressalva das envergaduras**:
não é fonte aeronáutica, e variante muda o número.

---

## O botão TESTAR da tela de regras

Regra é a única coisa deste app que **falha em silêncio**: um código de equipamento digitado errado
produz regra que nunca dispara, e nada distingue isso de não haver regra. O botão responde a pergunta
que o cadastro sozinho não responde — *isso aqui pega alguma coisa?*

Ele varre os lançamentos dos últimos `mapTesteRegraDias` dias (60) e responde em três formas:

| resposta | significa |
|---|---|
| *teria recusado N de M* | a regra funciona e tem alcance conhecido |
| *não recusaria nenhum dos M* | os equipamentos existem na posição, mas a condição nunca se deu |
| *nenhum lançamento tem esses equipamentos* | ⚠️ provável código errado — a regra é inerte |

A terceira é a que justifica o botão. As outras duas são informação; essa é diagnóstico.

**A conta é a mesma da validação do SALVAR**, de propósito: `Find` sobre a lista de códigos entre
vírgulas para pertinência, e cruzamento de intervalos (`ini_a < fim_b And fim_a > ini_b`) para
sobreposição. Se o teste usasse lógica própria, ele poderia dizer que a regra pega algo que na hora de
gravar não pega.

**Custo:** dois conjuntos pequenos (uma posição cada) cruzados entre si, não a lista inteira ao
quadrado. A janela é o que mantém isso barato — e é uma constante, não um número solto.

**Ela caiu de 90 para 60 dias em 05/09/2026**, e não por desempenho: a ~705 voos/mês, 90 dias passam
dos 2000 registros que o app aceita numa consulta, e o TESTAR responderia um número menor que o real
**sem dizer que truncou** — que é o pior tipo de resposta para um botão cuja função é dar confiança.

---

## Por que o menu continua duplicado nas cinco telas

Avaliado e mantido em 04/09/2026, a pedido do Douglas. **Não reabrir sem fato novo.**

O menu lateral é copiado nas cinco telas que o têm, com sufixo por tela (`btnNavRefMap`,
`btnNavRefEqp`…). Mudar o menu exige colar as cinco. A alternativa óbvia é um componente canvas.

**O que existe de precedente:** `SAFETY/msapp/Src/Components/HeaderTitle.pa.yaml`, com
`ComponentDefinitions:` / `DefinitionType: CanvasComponent`, e até um `OnSelect: =Back()` dentro. Mas
YAML exportado prova que alguém *escreveu* aquilo, não que executa.

**A restrição real é da plataforma:** componente canvas não chama `Navigate()`. Os contornos:

| contorno | resolve o problema? |
|---|---|
| propriedade de comportamento de saída, ligada ao `Navigate` em cada tela | **não** — acrescentar item ainda toca as cinco telas |
| componente faz `Set(varDestino, …)` e cada tela tem um gatilho que navega | sim, mas exige um `Timer` observando variável |

**Duas coisas práticas pesaram mais que a teoria:**

1. **Componente não se cola como tela.** Todo o fluxo de trabalho aqui é colar YAML no Studio.
   Componentes vivem em árvore própria, e não há evidência de que se criem por colagem.
2. **O custo atual é menor do que parece.** A alteração é aplicada por script nas cinco telas; o custo
   humano é colar cinco em vez de uma.

**Se for reabrir**, o caminho é medir antes de converter: um componente mínimo com um botão que faz
`Set` e uma tela que reage, só para ver se navega. Mesmo método que funcionou no pacote do fluxo —
montar pequeno e medir, em vez de converter e descobrir.

**O gatilho que justificaria reabrir** é o segundo aeroporto: mais telas, mais cópias.

---

## Absorção do app "Reserva e Alocação de Pátios"

Existiam dois aplicativos alocando aeronaves **nas mesmas posições, sem se enxergarem** — risco real
de dupla marcação que nenhum dos dois detectava. O Douglas decidiu em 04/09/2026 unificar num app só,
com o Mapa como base: o outro estava parado, sem histórico a migrar nem usuários a mover.

### O que veio de lá

**O ciclo de vida do registro.** Uma aeronave alocada não está só marcada — ela ainda vai chegar,
está no pátio, ou já saiu. A coluna `condicao` (`PREVISTO` / `NO PATIO` / `FINALIZADO`) e o selo no
bloco vieram daí, mais `responsavel` e `contato`, que faltavam para reserva pedida por terceiro.

**`PREVISTO` não ganha selo.** É o estado da esmagadora maioria dos registros; marcá-lo seria repetir
o erro que o tracejado quase cometeu. Selo só para o que foge do esperado.

O `SALVAR` **não** valida `condicao`: é estado, não restrição.

### O que foi deliberadamente deixado para trás

**As restrições codificadas no desenho.** Lá, `block_P3_A2.Visible = If(Cat_B_6A.Visible Or ...)` — a
regra de bloqueio vivia na visibilidade de uma imagem, por posição, e boa parte estava comentada. O
`tb_regrasPosicao` já resolve isso como dado, e é o que permite o botão TESTAR.

**A validação de conflito só na criação.** O ramo de edição fazia `SubmitForm` direto, sem checar
sobreposição. Editar um horário podia produzir o choque que o cadastro tinha impedido.

**O croqui feito de ~100 controles posicionados à mão** por pátio, dois por posição, mais variantes
por tipo de aeronave. Cada aeroporto novo era recomeçar do zero. O croqui **vai** ser absorvido, mas
com a geometria como dado na posição — ver o plano da unificação.

### O que ainda não veio

O croqui e o modelo de perfil por aeroporto (`varAeroUser`, `varPerfilUser`, `varBlocoUser`). Os dois
dependem do cadastro de posições virar lista, porque exigem campo novo por posição — é a mesma obra
que o lembrete de 19/09 trata.

---

## `ocupa` e `bloqueia`: duas coisas parecidas que não são a mesma

O Mapa tinha `ocupa` — uma posição que **substitui** outras. A T6C é a única: ela consome T5 e T6, e
por isso **não é desenhada como linha da grade**; o retângulo aparece sobre as duas que ela consome.

A aviação geral pede outra coisa. Uma aeronave grande numa posição **classe B** inutiliza as **classe
A** vizinhas enquanto estiver lá — mas as duas continuam sendo posições de verdade, e as duas
precisam continuar aparecendo na grade para o operador poder alocar nelas.

Por isso a coluna **`bloqueia`**, separada do `ocupa`:

| coluna | significa | efeito na grade |
|---|---|---|
| `ocupa` | esta posição **substitui** as listadas | some da grade; o bloco é desenhado sobre as outras |
| regra `BLOQUEIO` em `tb_regrasPosicao` | esta posição **inutiliza** as listadas enquanto ocupada | todas continuam na grade; a impedida ganha um bloco cinza `INDISPONÍVEL` |

As duas são **bidirecionais**: declarar num lado basta. Ocupar A2 impede a 6A, e ocupar a 6A impede
A2 — sem precisar escrever a relação duas vezes.

**Como o operador vê.** O bloco cinza `INDISPONÍVEL &middot; 6A` aparece na linha da posição impedida,
no intervalo exato, e clicar nele abre o registro que causa o impedimento. É a mesma máquina do bloco
da T6C: geometria, `trechos` e camada de clique, sem nada novo.

### ⚠️ As relações precisam ser confirmadas

Foram extraídas do croqui do app de reserva, e **a fonte se contradiz**. Lá a regra vivia na
visibilidade de imagens: `block_P3_7` dizia que a `7` é impedida por A6, A7, A9 e A10, mas `block_P3_A9`
dizia que A9 só é impedida pela `8`. Três posições — A1, A3, A6 — tinham a regra comentada.

Foi semeada a direção que é internamente consistente (`block_P3_6A/6B/7/8`), porque o mecanismo é
bidirecional e um lado basta:

| posição | inutiliza |
|---|---|
| `6A` | A1, A2, A4, A5 |
| `6B` | A2, A3, A4, A5 |
| `7` | A6, A7, A9, A10 |
| `8` | A7, A8, A9, A10 |

O Douglas descreveu **duas** posições classe A por classe B; o croqui declara **quatro**. Isso precisa
ser conferido no pátio. Não bloqueia nada hoje: a importação não usa nenhuma posição de aviação geral.

---

## O bloqueio entre posições virou regra, não coluna

Em 04/09/2026 a relação saiu de `colPosicoes.bloqueia` — tabela literal no `App.Formulas` — e foi para
a lista **`tb_regrasPosicao`**, a pedido do Douglas. O motivo é multi-aeroporto: **cada aeroporto tem
a sua geometria de pátio**, e mudá-la não pode exigir editar fórmula e republicar o app.

A lista já servia para veto por equipamento e passou a servir para os dois casos:

| campo | veto por equipamento (como era) | bloqueio entre posições (novo) |
|---|---|---|
| `posicao` | onde está o `equip_a` | a posição que, ocupada, inutiliza outras |
| `vizinha` | onde está o `equip_b` | **lista** das que ficam indisponíveis |
| `equip_a` / `equip_b` | os equipamentos proibidos juntos | **em branco: qualquer aeronave** |
| `tipo_regra` | `BLOQUEIO` | `BLOQUEIO` ou `AVISO` |

Duas mudanças de esquema sustentam isso: `vizinha` foi de 10 para 255 caracteres, para virar lista
como `equip_a` já era, e entrou `tipo_regra`.

**A regra se escreve numa direção, e vale nas duas.** "6A inutiliza A1, A2, A4, A5" é o que se cadastra;
o efeito é mútuo, porque é o mesmo espaço físico: com a 6A ocupada não cabe aeronave na A1, e com a A1
ocupada não cabe a grande na 6A. Escrever num sentido só é mais fácil de manter e não perde nada.

### As regras semeadas para NAVEGANTES

| posição | inutiliza |
|---|---|
| `6A` | A1, A2, A4, A5 |
| `6B` | A2, A3, A4, A5 |
| `7` | A6, A7, A9, A10 |
| `8` | A7, A8, A9, A10 |
| `T6C` | **6A, 6B** |

A da T6C veio do Douglas em 04/09/2026 e **não existia em lugar nenhum antes** — nem no `bloqueia`, nem
no croqui do app de reserva. O cargueiro consome T5 e T6 pelo `ocupa`, e agora também impede 6A e 6B.

As quatro primeiras continuam **a confirmar**: ele descreveu duas posições classe A por classe B, e o
croqui declarava quatro.

### `ocupa` continua sendo outra coisa

Não foi absorvido pelas regras, e não deve ser. `ocupa` diz que a posição **substitui** as outras e
por isso some da grade — é a T6C desenhada sobre T5 e T6. Bloqueio diz que ela **inutiliza**, e todas
continuam sendo linhas alocáveis. Confundir os dois faria a 6A desaparecer da grade.

### O que falta

A tela de restrições foi reformada em 04/09/2026 e cadastra os dois tipos. O que mudou nela:

- **POSIÇÕES AFETADAS virou lista**, com o mesmo padrão de adicionar-e-remover que os equipamentos já
  usavam. Substituiu um seletor de posição única.
- **O QUE A REGRA FAZ**: `Bloqueio` ou `Aviso`.
- **Equipamento deixou de ser obrigatório.** Vazio significa *qualquer aeronave* — é o que torna a
  regra de posição expressável sem enumerar a frota.

A validação aceita três formatos, e recusa o resto:

| formato | o que diz |
|---|---|
| posição + equipamentos | veto na própria posição |
| posição + posições afetadas, **sem equipamento** | a posição ocupada inutiliza as afetadas |
| posição + equipamentos + afetadas + equipamentos da afetada | veto de par, como sempre foi |

O que ela recusa, e por quê: **equipamento de um lado só numa regra de par** nunca dispara e some igual
a regra nenhuma; **equipamento na afetada sem afetada escolhida** não tem onde valer; e **regra sem
equipamento e sem afetada** não diz nada.

Uma armadilha que apareceu na reforma e vale saber: `colVizSel` já era o nome de uma coleção — o
seletor que o dropdown antigo usava, com coluna `Value`. Reusar o nome para a lista de posições
afetadas teria dado colisão silenciosa, porque o `btnRecarregarRgr` a reconstrói a cada recarga. A nova
chama-se `colAfetadasRgr`, e o seletor antigo foi removido junto com o dropdown.

---

## Condição em um toque, na lista do painel

Pedido do supervisor. A condição já existia como campo do formulário, mas mudar "previsto" para "no
pátio" exigia abrir o registro, trocar no seletor e salvar — três passos para um fato que o operador
constata olhando pela janela.

A lista de voos do painel ganhou dois botões por linha: **avião** alterna previsto ↔ no pátio, e
**visto** alterna para finalizado. Os dois gravam direto e recarregam a grade; a cor do ícone diz o
estado atual. Ambos são alternadores, não ações de mão única — errar o toque se desfaz com outro.

Os ícones são `Classic/Icon@2.5.0`, **não o botão moderno** — `Button@0.0.45` não tem `Tooltip`, e sem
balão dois ícones sem rótulo não dizem o que fazem. `Classic/Icon` tem a propriedade, com 35
precedentes, e 173 usos dentro de container moderno.

### Finalizado sai do mapa

Marcar como finalizado tira o registro da grade **e libera a posição**: o filtro do `colDia` e o do
`colValida` excluem `condicao = "FINALIZADO"`. Movimento encerrado não disputa espaço com o próximo.

O detector de alteração no servidor **não** filtra, de propósito: alguém finalizando noutra máquina é
exatamente o tipo de mudança que a grade precisa sinalizar como desatualizada.

⚠️ **Consequência a conhecer:** o registro some da grade e da lista do painel, e não há como
alcançá-lo de volta pelo app. Um toque errado no visto só se desfaz pelo SharePoint. O botão é
alternador, mas depois do primeiro toque não há mais onde tocar.

**A linha virou container AutoLayout** para isso. Não dá para posicionar os botões com `X` dentro de
galeria: o Studio descarta a propriedade ao colar a tela, e todos empilhariam no canto. É o mesmo
desenho da camada de clique da grade, e pelo mesmo motivo.

**Uma armadilha de edição que apareceu aqui**, e que vale para qualquer transformação parecida: o
botão da linha tinha uma propriedade `Width` **depois** do bloco multilinha de `Text`. Inserir os
botões novos ancorando no fim do texto deixou esse `Width` órfão, colado no último botão inserido —
YAML com chave duplicada, tela quebrada. Ao inserir irmãos depois de um controle, a âncora tem que ser
o fim do controle, não o fim da propriedade mais visível dele.
## O aviso de "alterado por outra pessoa" saiu (04/09/2026)

A grade tinha um detector de alteração no servidor: um `Timer` invisível relia a lista a cada
`mapSyncSegundos` e, se o `Modificado` mais recente do servidor não batesse com o `varUltimaAlt`
guardado na última carga, mostrava a faixa âmbar *"A programação deste dia foi alterada por outra
pessoa"*.

**Ele passou a alarmar sozinho, e o defeito foi introduzido aqui.** Quando `colDia` ganhou o filtro
`condicao <> "FINALIZADO"` — para que movimento finalizado saísse do mapa e liberasse a posição —, a
consulta do detector **não** ganhou o mesmo filtro. A partir daí:

- `varUltimaAlt` = maior `Modificado` **entre os não-finalizados** (vem de `colDia`);
- `locServidorAlt` = maior `Modificado` **de todos** (vem do servidor).

Basta um registro finalizado ser o mais recentemente alterado — que é o caso normal, já que finalizar
*é* uma alteração — e os dois nunca mais empatam. O aviso voltava a cada ciclo do timer, logo depois
de cada ATUALIZAR. Não havia segunda pessoa mexendo; não havia como haver.

**Removido inteiro** em vez de corrigido, por decisão do Douglas: **um operador por aeroporto**. O
detector defendia contra edição simultânea que a operação não tem. Saíram `cntAvisoMap`, `tmrSyncMap`,
`varUltimaAlt`, `locDesatualizado` e `locServidorAlt`. O botão ATUALIZAR continua, e é a única forma
de reler — que é o que já era, na prática.

⚠️ **`mapSyncSegundos` continua no `App.Formulas` e agora não é lido por ninguém.** Ficou de
propósito: tirá-lo obrigaria a uma colagem do `App.Formulas` no Studio que nada mais justifica. Sai na
próxima vez que esse arquivo for ao Studio por outro motivo — mesma regra da marca ASUR BRASIL.

Se um dia houver dois operadores no mesmo aeroporto, o detector volta com **a mesma condição de
`colDia` nos dois lados** — é essa igualdade, e não o timer, que era a parte difícil.

## A grade virou uma janela de horas (05/09/2026)

Pedidos 1 e 1b da supervisão, que só fazem sentido juntos: colunas de 10 minutos **e** bloco maior.
Separados, o primeiro piora o segundo — 144 colunas na mesma largura deixariam o retângulo do voo
menor ainda.

**O pedido literal era rolagem horizontal, e ela não foi entregue.** O Power Apps não expõe a posição
de rolagem de um container: dá para rolar, não dá para dizer "role até as 14h" nem para ler onde o
usuário está. Metade do pedido — *a rolagem acompanhando a passagem da hora* — seria impossível assim.
Pior, régua e linhas vivem em controles diferentes (um `HtmlViewer` e uma `Gallery`), e dois
containers rolando de forma independente desalinhariam as colunas.

**O que foi feito:** a grade desenha uma **janela** de 6h, 12h ou o dia inteiro, e a janela anda. Como
toda largura já era calculada em % sobre `mapMinutosDia`, passou a ser calculada sobre `locJanMin` —
**mudou o denominador, não a arquitetura.** Régua, linhas de fundo, blocos e camada de clique leem os
mesmos três números (`locJanIni`, `locJanMin`, `locJanFim`), então continuam alinhados por construção.

Ganhos sobre a rolagem: o app **sabe** onde a janela está, então o botão AGORA e o avanço automático
na virada da hora são possíveis. Perda: não se vê o dia inteiro de relance — por isso o botão
**DIA INTEIRO**, que reproduz exatamente o comportamento anterior.

### Carregar e desenhar viraram dois botões

`btnAtualizarMap` fazia as duas coisas: ler o SharePoint (`colDia`) e montar o HTML (`colGrade`).
Andar com a janela precisa **só** da segunda. Sem separar, cada toque na seta releria a lista inteira.

Agora `btnAtualizarMap` lê e chama `btnDesenharMap`; as setas, o zoom e o timer chamam **só**
`btnDesenharMap`. É a mesma separação que já existia entre dado e desenho em `colDia` → `colGrade`,
agora também no tempo.

### Camada de clique: 36 células, precisão que acompanha o zoom

O número de controles é fixo no YAML — não dá para gerar 144 células quando a janela abre e 36 quando
fecha. São **36**, sempre, cada uma cobrindo `locJanMin / 36`:

| janela | minutos por célula |
|---|---|
| 6 horas | 10 |
| 12 horas | 20 |
| dia inteiro | 40 |

Em 6 horas isso entrega o "ganho de brinde" previsto no pedido: clicar às 09h40 propõe 09:40, não
09:00. E mesmo no dia inteiro a precisão melhorou — eram 60 minutos por célula.

36 células por linha contra 24 antes: **+50% de controles**, não os +500% que 144 células custariam.

### Três detalhes que só aparecem depois de errados

1. **Ordem dos gradientes.** No CSS, o primeiro `background-image` fica por **cima**. Escrevendo a
   linha de 10 minutos primeiro, ela apagaria a linha da hora em cada marca de hora cheia. A hora
   cheia vem primeiro; a fina, depois.
2. **Bloco fora da janela não pode virar `<td>` de largura zero.** Ele tem `border:3px`, então
   renderizaria como uma lasca de 6px encostada na borda. O `<td>` do bloco só é emitido quando
   `_z > _a`; o vão continua sendo emitido, e é ele que mantém a soma em 100%.
3. **Os chevrons `«` `»` passaram a marcar dois cortes.** Antes só a virada do dia; agora também o
   corte da janela. É a mesma informação — "isto continua fora do que você está vendo" — e por isso
   reusa o mesmo símbolo em vez de inventar outro.

   ⚠️ **E a legenda ficou mentindo por quatro dias.** Ela dizia *"« » continua noutro dia"*, e passou
   a aparecer em voo do próprio dia que começou antes da faixa. Corrigido em 09/09/2026 para *"começa
   ou termina fora da faixa"*. **Símbolo que ganha significado novo obriga a revisitar a legenda na
   mesma passada** — a legenda é código de leitura, e ninguém a testa.

### O que saiu do `App.Formulas`

`mapPctHora` e `mapFundoHoras` dependiam de 24 colunas fixas. Agora dependem da janela, que é
variável, e **fórmulas nomeadas não enxergam variáveis** — foram para a tela como `locPct10`,
`locPctHora` e `locFundo`, calculados uma vez por desenho. `colHoras` saiu junto: a régua é montada
sobre a janela. E `mapSyncSegundos`, órfão desde a remoção do aviso de concorrência, saiu de carona —
era a "próxima vez que o arquivo fosse ao Studio" prometida ontem.

## Reserva de alternativa: a única exceção à regra de que posição ocupada bloqueia (05/09/2026)

Aviação geral pode reservar posição declarando o aeroporto como **alternativa do plano de voo** — a
aeronave só vem se precisar desviar, e provavelmente não vem. Coluna `alternativa` (0/1, não
obrigatória) na `tb_alocacoesMapa`.

**Por que mereceu exceção.** Toda reserva ocupava a posição igual. Uma alternativa segurando um box
que provavelmente não será usado tira capacidade real do pátio — o oposto do que o mapa existe para
fazer.

**A regra, e a assimetria que ela tem de propósito:**

| conflito com | o que acontece |
|---|---|
| registro firme (voo, interdição, reserva comum) | **bloqueia**, como sempre |
| reserva de alternativa | **avisa e pede confirmação** no segundo toque em SALVAR |

A segunda linha vale independentemente do que está entrando — inclusive quando quem chega é outra
alternativa. Já a primeira vale **inclusive quando quem chega é uma alternativa**: segurar um voo
confirmado por causa de uma reserva que provavelmente não vem seria o inverso do pedido.

Isso é implementado pela **ordem dos ramos** no `SALVAR`, não por uma condição composta: `locConflito`
agora busca só conflitos com `alt <> 1` e bloqueia; `locConflitoAlt` busca os com `alt = 1` e é
avaliado depois. Se existe conflito firme, o ramo do aviso nunca é alcançado. Ler a ordem é ler a
regra.

A trava de confirmação (`locConfirmaAlt`) guarda o **id do registro em conflito**, igual à do portão.
Mudou a posição ou o horário e o conflito passou a ser com outro registro, ele pergunta de novo — o
operador nunca herda uma confirmação que deu para outra coisa.

**No visual:** selo `A` ardósia (`hxAlternativa`), na frente do texto ao lado de `P` e `I`, porque o
bloco trunca no fim; o texto do bloco diz `ALTERNATIVA` em vez de `RESERVADO`; a dica de mouse
explica. O preenchimento **não** muda — a regra de que preenchimento é companhia (ou classe, na
aviação geral) já foi defendida três vezes e continua valendo.

**No cabeçalho:** `BLOQUEIOS` deixou de contar alternativas e elas ganharam KPI próprio. Misturá-las
faria o número de bloqueios sugerir uma ocupação que não existe.

## Delegação: o recorte de FINALIZADO saiu do filtro (05/09/2026)

`colDia` e `colValida` filtram a `tb_alocacoesMapa` no servidor. O termo `condicao <> "FINALIZADO"`,
acrescentado em 04/09 para tirar o movimento finalizado do mapa, **não delega** — desigualdade em
coluna de texto no conector SharePoint — e derrubava a consulta inteira para o modo local: primeiras
500 linhas por ID, filtradas na memória.

Com ~705 registros de setembro, as 500 primeiras cobriam o mês até cerca do dia 21. A grade parecia
certa, e **todo registro criado depois da importação era invisível para o app**.

Agora o filtro do servidor tem só termos delegáveis, e o `FINALIZADO` sai com `RemoveIf` na coleção
já baixada — uma linha depois de cada `ClearCollect`.

⚠️ **No `colValida` isso não era só cosmético.** Ele é a checagem de conflito: com a amostra cega
para os registros recentes, o app deixaria gravar duas aeronaves na mesma posição sem avisar. Quem
for mexer em qualquer um dos dois filtros: o que vai ao servidor tem de continuar 100% delegável.

O botão TESTAR do `scrMapaRegra` é consulta delegável, mas o volume podia passar do limite de linhas
do app. Resolvido pelos dois lados: o limite subiu para 2000 e a janela caiu para 60 dias.

## Mostrar finalizados: ver e ocupar são coisas diferentes (09/09/2026)

Marcar um movimento como finalizado tira o registro da grade e da lista do painel, e até aqui não
havia como alcançá-lo de volta pelo app — um visto errado só se desfazia pelo SharePoint. O botão
`FINALIZADOS` na barra da janela devolve esses registros à tela.

**A regra que dá sentido ao resto:** o interruptor é **de visualização**. O `RemoveIf` que tira
`FINALIZADO` do `colDia` passou a depender de `varVerFinalizados`; o do `colValida` — a coleção que
detecta conflito — é **incondicional**.

Movimento finalizado quer dizer que a aeronave saiu e a posição está livre. Se ligar o histórico
voltasse a bloquear, o operador perderia um box vazio por ter olhado o passado. Ver o que houve e
ocupar o que existe são perguntas diferentes, e o código responde uma de cada vez.

Isso está comentado no próprio `colValida`, porque a assimetria entre os dois `RemoveIf` parece
descuido para quem lê rápido e é exatamente o oposto.

**No visual:** bloco finalizado sai desbotado (`opacity:.45`) além do visto de condição que já tinha,
e o cabeçalho passa a dizer `COM FINALIZADOS` — a contagem de registros sobe com o filtro ligado, e um
número que muda precisa dizer por quê.

⚠️ **Efeito conhecido:** a linha é desenhada como uma sequência de células, e blocos sobrepostos no
tempo são recortados. Posição reusada por cima do horário de um movimento finalizado mostra o segundo
bloco truncado enquanto o filtro estiver ligado. Consertar pediria dar precedência ao bloco vivo numa
segunda passada — não vale o custo enquanto for visão de exceção, e some ao desligar.

## A barra de filtros quebra em vez de cortar (09/09/2026)

O Douglas viu no player que o **+ NOVO REGISTRO estava cortado** — o botão de ação principal da tela.
Nos prints anteriores ele cabia porque o Studio estava a 60% de zoom; a 100%, numa janela de ~1280px,
não cabe.

A conta: oito controles de largura fixa somam **1076px**, mais 70 de vãos e 52 de padding — **1198**,
mais o AMANHÃ, que era o único sem largura declarada. Container AutoLayout horizontal **não quebra
linha sozinho**: o que não cabe é cortado, em silêncio, e some quem estiver por último.

Agora `LayoutWrap: =true`, com a altura respondendo à largura disponível:
`Height: =If(Parent.Width < 1330, 120, 62)`. Numa janela larga fica em uma linha como sempre; numa
estreita passa a duas e a grade cede 58px. **O AMANHÃ ganhou largura explícita (110)** para o limiar
de 1330 ser uma conta e não um chute.

⚠️ **A classe do defeito importa mais que ele:** barra de ações com largura fixa é uma bomba-relógio
de layout, porque falha só na janela de quem usa, nunca na de quem constrói. Toda vez que um botão
novo entrar nessa barra, a conta acima muda e o limiar tem de mudar junto.

## Posições e pátios saíram do código (09/09/2026)

Antecipação do lembrete do dia 19. O pedido dele foi **"o mínimo que torna possível"** — segundo
aeroporto ainda é hipótese —, então a entrega é só tirar os dados do `App.Formulas` e pô-los em lista.

**Sem tela de cadastro.** Configurar um aeroporto é tarefa de uma vez, não de operação diária, e a
interface do SharePoint já serve de editor. Se um dia virar rotina, a tela é incremento barato: o
caminho de leitura já está pronto.

**Pátios entraram junto e não por capricho:** posição referencia código de pátio, e sem a tabela o
aeroporto novo teria posições apontando para pátio inexistente — a grade perderia nome e cor.

### Por que nenhuma tela mudou

As cinco telas nunca leram `colPosicoes`; leem `colPosicoesAero`. Como **fórmula nomeada lê variável
global** (ver a lição corrigida em 09/09), ela continua sendo fórmula nomeada e apenas passou a mapear
a lista para os mesmos nomes de campo:

```
colPosicoesTodas = ForAll(Filter(tb_posicoes; ativo = 1) As _p; { ...; id: _p.id_posicao; ... });;
colPosicoesAero  = (inalterada, agora sobre colPosicoesTodas)
```

Os 47 usos de `.id`, 21 de `.posicao` e 13 de `.patio` espalhados pelas telas seguem intactos.

### ⚠️ `id_posicao` não é o ID do SharePoint, e não se renumera

A `tb_alocacoesMapa` grava esse número em `id_posicao` em mais de 700 lançamentos. A coluna é própria
da lista justamente para não depender do ID que o SharePoint gera sozinho. **Renumerar aponta o
histórico inteiro para a posição errada e nada na tela denuncia** — a grade continua desenhando, só
que no lugar errado.

O seed foi **gerado a partir da tabela literal**, não redigitado, e o gerador confere ids sem buraco
nem repetição, pátio referenciado existindo, e a ordem fracionária do T6C (6,5), que é o que o coloca
entre T6 e T7.

### A cor do pátio virou dado

Era `Switch(_p.patio, "PRINCIPAL", ..., "PATIO3", ..., hxVerde)` dentro do `scrMapaPatio` — uma regra
específica de um aeroporto morando na tela. Virou a coluna `cor_hex`. Sem isso, aeroporto novo sairia
com todos os pátios verdes, e "multi-aeroporto" seria meia verdade.

### O que continua exigindo desenvolvedor

Ficaram de fora de propósito, e é honesto listá-los:

| ainda no `App.Formulas` | consequência para um segundo aeroporto |
|---|---|
| `colPortoes` | herda os mesmos 5 portões e cores |
| `colPrefPosicao` | herda as preferências de alocação de Navegantes |
| `colAerosMapa` | o aeroporto novo precisa ser acrescentado no código |

⚠️ **E a pior das três não está nessa tabela:** o `importar_programacao.ts` tem a sua própria cópia das
preferências. Com um aeroporto isso é dívida conhecida; com dois, **o script aloca usando a tabela do
aeroporto errado, sem erro nenhum**. Resolver isso é pré-requisito de importar programação num segundo
aeroporto — não de ter um segundo aeroporto na grade.

### Ordem de instalação, e como conferir

1. Criar `tb_patios` e `tb_posicoes` pelos JSONs (eles trazem os registros).
2. Adicionar as duas ao app como fonte de dados.
3. Colar o `App_Formulas_Mapa.txt`.
4. Colar o `scrMapaPatio.pa.yaml`.

**Três conferências, e a primeira é a que decide:**

1. **Abrir um dia com movimento e comparar com antes.** Os blocos têm de estar nas mesmas linhas. Se
   algum mudou de posição, o `id_posicao` não veio como devia — voltar atrás antes de gravar
   qualquer coisa.
2. **Rolar até o fim da grade:** as linhas do PÁTIO 3 e dos HELIPONTOS têm de existir, com a borda
   esquerda laranja-azulada e verde. É o teste da coluna `cor_hex` — se saírem todas iguais, a cor
   não está vindo do dado.
3. **Abrir o formulário e o seletor de posição:** o **T6C tem de aparecer entre T6 e T7**. É o teste
   da ordem 6,5.

⚠️ **O T6C não aparece como linha da grade, e isso é o certo.** Ele tem `ocupa: "T5,T6"`, e a grade só
desenha posições sem `ocupa` — o bloco do cargueiro é desenhado *sobre* T5 e T6. Procurá-lo na grade
é procurar o que nunca esteve lá; a ordem 6,5 só se observa no seletor. Escrevi a verificação errada
na primeira versão deste documento.

> A `tbl_posicoes_patio` do app antigo foi avaliada como fonte e descartada: `ID`, código de pátio e
> nomes de posição divergem dos nossos, e ela está vazia. Pode ser aposentada junto com o App B.

## Faixa do pátio e marca do T6C (09/09/2026)

Três pedidos dele depois de ver a migração funcionando.

**A faixa vertical com o nome do pátio.** Uma coluna de 22px à esquerda, pintada com a `cor_hex` do
pátio, com as letras da sigla **uma por linha, centradas no grupo** — é isso que produz o efeito de
texto vertical sem depender de `writing-mode` nem de `transform`, que não têm precedente no
`HtmlViewer` deste app e poderiam ser removidos pelo sanitizador.

Cada linha sabe quantas linhas o pátio tem (`_qtdPatio`) e qual é a sua dentro dele (`_idxPatio`), e
imprime a letra correspondente quando cai na faixa central. Grupo de 7 linhas com sigla de 2 letras
imprime nas linhas 3 e 4.

⚠️ **A faixa e o rótulo somam os mesmos 132px (`mapLarguraRotulo`) que a régua reserva** — 22 + 110.
Mexer num sem o outro desalinha todas as colunas da grade, e o sintoma aparece longe da causa.

**A cor não é mais escolha de código.** O Pátio 3 virou âmbar por pedido dele, e a troca foi feita
**na lista**, não aqui. Foi o primeiro retorno concreto de ter tirado as posições do `App.Formulas`
horas antes: mudança de aparência do pátio deixou de precisar de colagem no Studio.

A `tb_patios` ganhou `cor_texto` e `sigla`, seguindo o padrão que `colCias` já usava (fundo + texto no
mesmo registro). O texto sobre fundo escuro usa `#D6DDE0` e não branco puro, que é a convenção
declarada no próprio `App.Formulas`.

**`(T6C)` ao lado de T5 e T6.** A T6C consome as duas e por isso **nunca aparece como linha** — o
operador não tinha como lembrar, olhando a T5, que aquele espaço é do cargueiro. Agora a linha de
restrição mostra a posição que a consome, apagada. Vem de `ocupa`, então funciona para qualquer par
que um aeroporto novo venha a declarar, sem código adicional.

## Cadastro de posições e pátios (09/09/2026)

A `scrMapaReferencia` deixou de ser consulta e virou cadastro. **Reaproveitar a tela foi decisão de
custo:** ela já ocupa a vaga POSIÇÕES E CORES no menu, e o menu é duplicado nas cinco telas que o têm
— tela nova custaria sete colagens antes de qualquer teste.

Um seletor no topo alterna **POSIÇÕES** e **PÁTIOS**; cada modo tem a sua galeria e o seu formulário,
no mesmo desenho do `scrMapaEquip`.

⚠️ **Saiu dali o conteúdo de consulta** — a legenda de cores de companhia e portão. Ela continua na
legenda do Mapa do Dia, então a informação não se perdeu do app; mas quem usava esta tela para
consultar vai estranhar.

### As travas, que são o motivo da tela existir

Editar estas listas pelo SharePoint já era possível. A tela existe pelo que ele não verifica:

- **Nome de posição único no aeroporto.** O nome vai gravado em cada lançamento; duplicar embaralha a
  grade sem erro.
- **Cada nome em `OCUPA` tem de existir.** Errar aqui produz regra muda: a posição não some da grade e
  ninguém descobre até duas aeronaves disputarem o mesmo espaço. É a mesma classe de defeito que
  justificou o botão TESTAR da tela de regras.
- **Código de pátio único**, porque é ele que cada posição referencia.
- **Cores no formato `#RRGGBB`**, com amostra ao vivo da faixa ao lado dos campos.
- **`id_posicao` é atribuído pelo sistema** (`Max + 1`) e **nunca editável** num registro existente. O
  formulário mostra o número e explica por quê.

### Não há botão de excluir, e é de propósito

Posição se **desativa**, não se apaga. O `id_posicao` está gravado em mais de 700 lançamentos: apagar
deixaria o histórico apontando para o vazio, e a grade continuaria desenhando como se nada fosse. O
mesmo vale para pátio, que as posições referenciam pelo código.

Quem quiser mesmo apagar tem o SharePoint — mas aí é decisão deliberada, não um toque a mais no lugar
errado.

## Paleta de cores no cadastro de pátios (09/09/2026)

Digitar `#RRGGBB` à mão é onde alguém erra um dígito e o pátio some do desenho. Cada campo de cor
ganhou **18 amostras clicáveis** abaixo dele, com as cores do próprio app mais um conjunto padrão.

**`Fill` não existe em `Button@0.0.45`** — zero usos em 651 instâncias no repositório. A amostra é um
botão com `Appearance.Primary` e `BasePaletteColor: =ColorValue("#XXXXXX")`, que é como este app já
pinta botão colorido.

Clicar numa amostra **reconstrói o registro inteiro do formulário a partir dos controles**, trocando só
a cor. É verboso — dezoito vezes dois — mas é gerado por script, e evita `Patch` sobre registro, que
não tem precedente aqui. O efeito colateral desejado: o que estiver digitado e ainda não salvo
sobrevive ao clique.

Por isso `varFormPat` passou a nascer como registro vazio em vez de `Blank()`: reconstruir um registro
a partir de `Blank()` daria erro no primeiro clique, antes de qualquer pátio ser selecionado.

O campo de texto continua ali para quem tiver o hex exato, e a amostra ao vivo ao lado mostra o
resultado antes de salvar.

⚠️ **O que NÃO foi feito, e é limitação da plataforma:** as sugestões que aparecem ao digitar num
campo de texto são o **preenchimento automático do navegador**, não do app. `TextInput@0.0.54` não
expõe `autocomplete`, e desligar isso é configuração do navegador de cada pessoa. Ficou registrado
para não voltar como pedido de código.
