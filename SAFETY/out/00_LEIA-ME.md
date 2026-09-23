# AirportNow — Safety & Fauna · Refatoração 2026-08-31

Origem: `SAFETY/AirportNow-Safety&Fauna-2025_20260831145316.zip`
(42 telas, 50.360 linhas de `.pa.yaml`).

---

## Ordem de aplicação

O Studio valida nome de tela **na hora em que você cola**. Colar algo que chama
`Navigate(ScreenModJetBlast, ...)` antes dessa tela existir dá erro de identificador
desconhecido — e às vezes o Studio devolve só um **ID de sessão** em vez da mensagem
(esse ID só a Microsoft abre; leia o painel de erros).

Por isso a ordem abaixo cria primeiro os nomes, depois o conteúdo, e o App por último.

### Passo 1 — App.Formulas

Cole `02_App_Formulas_ptBR.txt` em **App → Formulas**. Não depende de nada e é o que
define `nfAeros`, `nfBlocos`, `nfDataPiso` e os tokens de cor. Named formula ausente
derruba todas as telas que a usam, então esta vem antes de tudo.

### Passo 2 — Criar as 7 telas VAZIAS, já com o nome final

Nova tela em branco × 7, renomeando cada uma antes de colar qualquer coisa:

```
ScreenModColisaoVeiculos     ScreenModIncursaoPista        ScreenModJetBlast
ScreenModDerramamento        ScreenModInterferenciaExterna ScreenModOcorrenciaSolo
ScreenModExcursaoPista
```

O nome tem que existir antes do conteúdo porque **cada tela referencia a si mesma**
(`{var_navigateSucess: ScreenModJetBlast}` está dentro da própria ScreenModJetBlast).

### Passo 3 — Colar o conteúdo das 7 telas

Em qualquer ordem entre si: **nenhuma das 7 depende das outras 6**. Cada uma só precisa
de `ScreenSucesso`, `ScreenErro`, `ScreenExcluir`, `ScreenDesdobramentos`,
`ScreenAnaliseSafety` e `frmHome`, que já existem no app.

### Passo 4 — Telas de apoio e corrigidas

Antes de colar `08_ScreenFauna.pa.yaml`: crie uma tela nova em branco chamada
**`ScreenFaunaForms`** (ela não existe no app hoje — ver item 19) e cole
`10_ScreenFaunaForms.pa.yaml` nela. Só depois disso cole `08_ScreenFauna.pa.yaml`,
porque os botões de `ScreenFauna` navegam pra lá.

Agora que as 7 existem, cole (qualquer ordem):

| Arquivo | Tela |
|---|---|
| `03_ScreenExcluir.pa.yaml` | `ScreenExcluir` |
| `04_ScreenAnaliseSafety.pa.yaml` | `ScreenAnaliseSafety` |
| `05_ScreenFOD.pa.yaml` | `ScreenFOD` |
| `06_ScreenCSO.pa.yaml` | `ScreenCSO` |
| `07_ScreenVistoriaSafetyFauna.pa.yaml` | `ScreenVistoriaSafetyFauna` |
| `10_ScreenFaunaForms.pa.yaml` | `ScreenFaunaForms` **(colar antes de `08_ScreenFauna`, ver item 19)** |
| `08_ScreenFauna.pa.yaml` | `ScreenFauna` |
| `09_ScreenAcessIndFaunaForms.pa.yaml` | `ScreenAcessIndFaunaForms` |

### Passo 5 — App.OnStart

Cole `01_App_OnStart_ptBR.txt` em **App → OnStart**. Vem por último porque a
`col_NavTelas` cita as 11 telas de módulo de uma vez; qualquer uma faltando derruba
o OnStart inteiro.

> Alternativa: `01_App.pa.yaml` pela exibição de código. Mesmo conteúdo, formato
> invariante. Use um **ou** o outro, não os dois.

### Passo 6 — Rodar o app antes de apagar nada

`Alt` + testar cada módulo: abrir a lista, cadastrar, visualizar, excluir. Só depois
de tudo passando é que se apaga.

### Passo 7 — Excluir as telas antigas

As 21 telas consolidadas:

```
ScreenColisaoVeiculos          ScreenColisaoVeiculosForms          ScreenColisaoVeiculosDetalhes
ScreenDerramamentoFluido       ScreenDerramamentoForms             ScreenDerramamentoDetalhes
ScreenExcursaoPista            ScreenExcursaoPistaForms            ScreenExcursaoPistaDetalhes
ScreenIncursaoPista            ScreenIncursaoPistaForms            ScreenIncursaoPistaDetalhes
ScreenInterferenciaExterna     ScreenInterferenciaExternaForms     ScreenInterferenciaExternaDetalhes
ScreenJetBlast                 ScreenJetBlastForms                 ScreenJetBlastDetalhes
ScreenOcorrenciaSolo           ScreenOcorrenciaSoloForms           ScreenOcorrenciaSoloDetalhes
```

E, **antes** delas, estas sobras de template — que apontam para as antigas e não são
usadas por ninguém:

```
Screen1   Screen1_1   ScreenLista_1   ScreenForms_1   ScreenDetalhes_1
```

> `ScreenLista_1` e `ScreenForms_1` referenciam `ScreenDerramamentoForms` e
> `ScreenDerramamentoDetalhes`. Se ficarem no app, a exclusão das antigas deixa
> referência quebrada. Confirme que não são usadas antes de apagar.

### Locale — a regra, em uma frase

**O destino decide o formato, não o Studio.**

| Destino | Formato | Arquivos |
|---|---|---|
| **Barra de fórmulas** (App.OnStart, App.Formulas, fórmula solta) | **pt-BR**: `;` argumentos, `;;` encadeia, `,` decimal | `01_App_OnStart_ptBR.txt`, `02_App_Formulas_ptBR.txt` |
| **Exibição de código** (`.pa.yaml`) | **invariante**: `,` argumentos, `;` encadeia, `.` decimal | todos os `.pa.yaml` |

O Studio está em pt-BR, mas ele **lê e grava `.pa.yaml` em invariante** — é o formato
do arquivo, não da interface. Converter um `.pa.yaml` para `;`/`;;` faz ele parar de
compilar. Cada `.pa.yaml` entregue traz esse aviso no próprio cabeçalho.

`01_App_OnStart_ptBR.txt` e `01_App.pa.yaml` são o **mesmo código**, gerados da mesma
origem: o conversor produz o pt-BR e uma segunda conversão de volta tem que devolver o
invariante caractere a caractere. Se divergir, a entrega falha (`build/entregar.sh`).

> Aliás: dentro de `ScreenFauna` há um bloco `/* ... */` comentado escrito em pt-BR,
> que veio assim do export original. Está inerte (o Studio não compila comentário), mas
> é sinal de que esse trecho já foi colado no lugar errado alguma vez. Se um dia for
> reativado, precisa voltar para invariante antes.

---

## O que mudou

### 1 · Uma tela por módulo

7 módulos × 3 telas → 7 telas. A visão é controlada pela variável global `var_vista`
(`"lista"` / `"form"` / `"detalhe"`). `OnVisible` força `"lista"`, então chegar de
fora sempre abre na galeria; alternar dentro da tela não dispara `OnVisible` e o
estado se mantém.

| Nova tela | Substitui |
|---|---|
| `ScreenModColisaoVeiculos` | ScreenColisaoVeiculos + Forms + Detalhes |
| `ScreenModDerramamento` | ScreenDerramamentoFluido + Forms + Detalhes |
| `ScreenModExcursaoPista` | ScreenExcursaoPista + Forms + Detalhes |
| `ScreenModIncursaoPista` | ScreenIncursaoPista + Forms + Detalhes |
| `ScreenModInterferenciaExterna` | ScreenInterferenciaExterna + Forms + Detalhes |
| `ScreenModJetBlast` | ScreenJetBlast + Forms + Detalhes |
| `ScreenModOcorrenciaSolo` | ScreenOcorrenciaSolo + Forms + Detalhes |

Fauna, FOD, CSO e Vistoria já eram tela única e continuam assim.

**O init de cada visão anda junto com a troca de visão.** `Navigate()` dispara o
`OnVisible` da tela de destino; `Set(var_vista, ...)` não dispara nada. Tudo que os
`OnVisible` das telas de Forms e Detalhes faziam ao abrir — carregar
`col_<mod>DetImagens`, `col_incPistaEnvolvidosDetalhes`, `col_jetBlastItensDetalhes`,
os quatro `col_ocoSoloOpEnvolv0x`, ligar os painéis do formulário, travar o
`DisplayMode` dos campos de Ocorrência de Solo — foi reinjetado em **cada ponto que
entra na visão**, com o comentário `// ── INIT DA VISÃO`.

Sem isso a galeria do detalhe fica ligada a uma coleção que ninguém preenche: o YAML
continua válido, a propriedade continua lá, o nome da coleção está certo — e a tela
abre vazia. `build/checar_init.py` existe exatamente para travar essa regressão, e
falha se algum ponto de entrada ficar sem o init.

### 2 · Campo de aeroporto no cadastro

Faixa nova no topo de cada formulário (`cntFaixaAero<Modulo>`): **Bloco**,
**Aeroporto** e prévia do protocolo. Regra de permissão:

| Perfil | Bloco | Aeroporto |
|---|---|---|
| Base | travado (View) | travado no `varAeroUser` (View) |
| Bloco | travado no próprio bloco | escolhe dentro do bloco |
| Sede | livre | livre |

O `Patch` deixou de gravar `varAeroUser` fixo:

```
<mod>_aeroporto: cmbFrm<Mod>Aeroporto.Selected.Aeroporto
<mod>_bloco:     LookUp(colAeros, Aeroporto = cmbFrm<Mod>Aeroporto.Selected.Aeroporto).Bloco
```

O bloco é **derivado** do aeroporto escolhido — não dá para gravar um par
bloco/aeroporto incoerente.

### 3 · Segurança: o vazamento que existia em todas as galerias

Todas as galerias filtravam o aeroporto de forma opcional:

```
IsBlank(cmbAeroporto.Selected.Aeroporto) || <mod>_aeroporto = cmbAeroporto.Selected.Aeroporto
```

Com o combo em branco a condição é sempre verdadeira. O `OnVisible` restringia
uma coleção por perfil, mas **a galeria consultava a lista direto** — então um
usuário de perfil "Base" via as ocorrências de todos os 16 aeroportos, bastando
não escolher nada no filtro. Valia para os 7 módulos, mais Fauna, FOD, CSO e
Vistoria.

Agora `App.OnStart` define `varEscopoAero`, `varEscopoBloco` e `varEscopoIATA`,
que **não dependem de nenhum controle de tela**, e toda galeria consulta o escopo
antes do filtro do usuário.

### 4 · Protocolos duplicados

O ID era calculado no cliente:

```
var_jetBlastId: Value(First(SortByColumns(Filter(tbl, jetBlast_id > 0), "ID", Desc)).jetBlast_id + 1)
```

Dois usuários salvando ao mesmo tempo liam o mesmo máximo e geravam o **mesmo
protocolo**; os filhos (imagens, envolvidos, itens atingidos) de um iam parar na
ocorrência do outro. Agora:

```
UpdateContext({var_regNovo<Mod>: Patch(tbl, Defaults(tbl), { ... })});   // grava
UpdateContext({var_<mod>Id: Coalesce(var_regNovo<Mod>.ID, 0)});          // lê o ID real
If(var_<mod>Id <= 0, Notify(erro); libera a tela,
   Patch(tbl, var_regNovo<Mod>, {<mod>_id: var_<mod>Id}));               // carimba de volta
```

Cada `ForAll` de filho ficou dentro de `If(var_<mod>Id > 0, ...)` — nenhum
registro órfão se o pai falhar. O reset do formulário e a tela de sucesso também.
Antes, uma falha de gravação **limpava o formulário** e mostrava
"Operação realizada com sucesso".

### 5 · Trava de reentrância

Todo botão que grava tem trava com carimbo de hora que **expira sozinha em 60s** —
duplo clique não grava duas vezes, e nenhuma falha deixa o botão morto.

> A trava também zera `var_visibleSpiner` em todos os ramos de saída, inclusive
> validação e erro — mas isso é higiene, não funcionalidade: essa variável vem do
> export e **nenhum controle do app a lê**. Não há spinner ligado a ela. O que o
> usuário vê enquanto grava é o `LoadingSpinner.Data` da própria tela, que o Studio
> controla sozinho. Se quiser um indicador explícito de "gravando", é preciso criar
> o controle e ligá-lo à variável — ela já é atualizada nos lugares certos.

### 6 · Delegação

Nas 7 telas `ScreenMod*`, a galeria virou:

```
With({_aero: ..., _bloco: ..., _ini: ..., _fim: ...},
  SortByColumns(
    Filter(
      Switch(true,
        !IsBlank(_aero),  Filter(tbl, <mod>_aeroporto = _aero, <mod>_data >= _ini, <mod>_data < _fim),
        !IsBlank(_bloco), Filter(tbl, <mod>_bloco    = _bloco, <mod>_data >= _ini, <mod>_data < _fim),
                          Filter(tbl,                          <mod>_data >= _ini, <mod>_data < _fim)),
      <status>, <tipo>, <busca por ID>),
    "ID", SortOrder.Descending))
```

Os três ramos são **delegáveis** (igualdade + intervalo de datas). Status, tipo e
busca por ID rodam localmente, já sobre o conjunto recortado. Antes, o
`IsBlank() ||` no primeiro filtro derrubava a delegação inteira e a lista parava
silenciosamente nas primeiras 500/2000 linhas.

Piso de data: `nfDataPiso` (1º de janeiro de dois anos atrás) quando o usuário
não escolhe data inicial.

### 7 · OnStart mais leve

Saíram por serem **código morto** (nenhuma tela lê): `ImgBase64` / `ImgBase64Limpo`
(um `JSON()` de imagem binária a cada abertura), `var_ultimaVersao` (consulta ao
SharePoint) e `var_sideBarWidth`. A tabela fixa de 17 aeroportos saiu do OnStart e
virou a named formula `nfAeros` — 120 linhas a menos no caminho de abertura.
`varFotoUser` ficou por último, dentro de `IfError`.

### 8 · Botões de voltar

Com o módulo em uma tela só, "voltar" dentro do módulo não é mais navegação:

| Onde | O que faz |
|---|---|
| Voltar na **lista** | `Navigate(frmHome)` — sai do módulo, é o único que ainda navega |
| Voltar / Cancelar no **formulário** | `Set(var_vista, "lista")` |
| Voltar no **detalhe** | fecha o zoom da imagem se estiver aberto; senão `Set(var_vista, "lista")` |

Corrigido aqui um bug herdado do export: o voltar dos **Detalhes de Derramamento**
fazia `Navigate(ScreenContainerDerramementoFluido)` — nome de um **container**, não
de uma tela. Nunca funcionou, e o Studio não acusa esse tipo de erro. Os outros seis
módulos estavam certos.

> O logotipo Motiva no cabeçalho continua com `Navigate(frmHome)` em todas as visões,
> inclusive dentro do formulário — comportamento original, preservado. Se preferir que
> ele respeite o formulário em preenchimento, dá para trocar por um aviso de confirmação.

**Toda saída para `frmHome` agora limpa `var_redirectAN`** — nas 7 telas de módulo e
também em FOD, CSO, Vistoria, Fauna, Análise Safety e Acesso Indevido de Fauna.

`frmHome.OnVisible` faz `If(!IsBlank(var_redirectAN), Select(ButtonCanvasredirect))`,
e `ButtonCanvasredirect` navega para a tela do `Param("ID_MODULO")`. Como `Param()`
devolve o mesmo valor pela sessão inteira, quem abrisse o app por deep link e
apertasse "voltar" era jogado de volta no módulo — laço sem saída. Seis módulos já
limpavam a variável no botão de voltar da lista; faltavam Ocorrência de Solo, as
quatro telas de apoio e o logotipo Motiva de **todas** as telas. `checar_init.py`
agora reprova qualquer `Navigate(frmHome)` sem a limpeza.

### 9 · Layout

O corpo dos formulários foi medido a partir do próprio export antes de qualquer
mudança. Apareceram dois problemas distintos:

**Colisão de Veículos** — o container do formulário (`Container4`) era
`AutoLayout Vertical`, então os quatro blocos de ~500px (dados, mapa de grade,
envolvidos, fotos) empilhavam numa coluna só e sobrava mais de metade da tela
vazia à direita. Virou `Horizontal` com `LayoutWrap: =true`, `LayoutGap: =24` e
largura total: os blocos fluem lado a lado e quebram sozinhos conforme a janela —
três por linha no desktop, um por linha no celular.

**Os outros seis** — o corpo era `ManualLayout` com `Width: =1138` fixo, encostado
à esquerda. Virou `Width: =Min(Parent.Width - 48, <largura do conteúdo>)` com
`AlignInContainer.Center`: acompanha a janela e fica centralizado.

O teto de largura é o conteúdo real de cada formulário, medido controle a controle:

| Módulo | Conteúdo vai até | Largura antiga | Largura nova |
|---|---|---|---|
| Derramamento | 975 px | 1138 | 1040 |
| Excursão de Pista | 1065 px | 1138 | 1120 |
| Incursão de Pista | 1067 px | 1138 | 1120 |
| Interferência Externa | 1104 px | 1138 | 1160 |
| **Jet Blast** | **1214 px** | **1138** | **1260** |
| Ocorrência de Solo | 1081 px | 1138 | 1140 |

O Jet Blast tinha **1214 px de conteúdo dentro de uma caixa de 1138** — estava
cortando o lado direito do formulário. Só apareceu porque a largura foi medida.

**Identidade visual**: os 21 cabeçalhos (3 por módulo) e a faixa divisória sob os
filtros saíram do preto puro para o roxo Motiva, via o token `nfCorPrimaria` — que
está em `App.Formulas`, então trocar a cor num lugar reflete nas 7 telas. Canto
reto e Segoe UI preservados.

**O que não foi mexido**: nenhuma posição, tamanho ou agrupamento de campo dentro
dos blocos. Os controles continuam exatamente onde estavam; o que mudou é como os
blocos se distribuem no espaço da tela.

### 10 · `View_safety = 1` destrava o seletor de aeroporto (2026-09-22)

A permissão `View_safety` (lida em `App.OnStart` como `varPerfilSafety`) já existia
e já controlava duas coisas: mostrar os itens **CSO** e **Vistoria Safety Fauna** no
menu, e um painel dentro do formulário do FOD. Mas o **seletor de aeroporto** — o
combo de filtro em cada galeria, mais o combo de Bloco ao lado — continuava travado
só pelo `Perfil` (`Base`/`Bloco`/`Sede`), sem olhar essa permissão. Um usuário com
`Perfil = "Base"` e `View_safety = 1` via o combo travado no próprio aeroporto,
como se não tivesse a permissão.

Corrigido nas **11 telas** que têm esse seletor (os 7 módulos de ocorrência, FOD,
CSO, Vistoria Safety Fauna e Fauna), em dois pontos:

- **O combo** — `DisplayMode` passou a considerar `varPerfilSafety`: com
  `View_safety = 1`, o combo fica editável mesmo com `Perfil = "Base"` ou `"Bloco"`.
- **Os dados** — `varEscopoAero` e `varEscopoBloco` (definidas uma vez em
  `App.OnStart`, usadas por todas as galerias) passaram a ficar `Blank()` quando
  `varPerfilSafety` é verdadeiro. Sem isso o combo destravado seria cosmético: a
  consulta continuaria presa ao aeroporto do usuário. Agora quem tem a permissão
  enxerga qualquer aeroporto, igual ao perfil `Sede`.

**O que não mudou**: o combo de aeroporto/bloco do **formulário de cadastro**
(`cmbFrm<Mod>Aeroporto`, onde se escolhe em nome de qual aeroporto uma nova
ocorrência é registrada) continua travado só pelo `Perfil`. `View_safety` é uma
permissão de leitura — não dá a quem a tem o direito de lançar ocorrências como se
fosse de outro aeroporto.

### 11 · Paleta trocada para o tema Asur (2026-09-22)

O roxo `#5E22F3` ("Cores Motiva", com comentário dizendo ter sido extraído de um
tema de PPT/Word) saiu de `App.Formulas`. Entrou o teal `#00879A` + cinzas slate
que o **Due Diligence** já usa em produção (`ScreenDueDiligence.yaml`,
`ScreenDueDiligencePainel.yaml`) — pedido do usuário, que apontou o Due Diligence
como referência do sistema de design da Asur. `nfCorErro`/`nfCorOk`/`nfCorAlerta`
passaram a usar as cores documentadas em `PAINEL_INDICADORES.md` como "as mesmas
cores do app" (`#D93025` / `#118D5C` / `#C47F00`).

> Aviso: o comentário antigo dizia que o roxo veio do tema oficial
> (`Base PPT ASUR Temp.pptx` / `Timbrado ASUR_temp.docx`). Se essa extração
> estiver certa, pode haver duas paletas Asur válidas para contextos diferentes
> (documento vs. aplicativo) — vale confirmar antes de considerar o roxo
> definitivamente descartado.

Só os **tokens** (`nfCorPrimaria`, `nfCorPrimariaEsc`, `nfCorTexto`,
`nfCorTextoFraco`, `nfCorFundoFraco`, `nfCorBorda`, `nfCorErro`, `nfCorOk`,
`nfCorAlerta`) mudaram de valor — isso já recolore sozinho tudo que os referencia
(cabeçalhos, faixa de aeroporto no cadastro, faixa divisória sob os filtros).

**2026-09-22, segunda rodada — recolorido em todas as 25 telas-fonte** (os 7
módulos × lista/forms/detalhes, mais FOD, CSO, Vistoria Safety Fauna e Fauna):
todo campo que usava cor fixa (principalmente `RGBA(0,0,0,1)` preto, e em
FOD/CSO/Vistoria o cinza-azulado `RGBA(215,223,240,…)`/`RGBA(245,245,245,1)`,
e em Fauna o azul-marinho `RGBA(0,18,107,1)`) passou a usar token: borda,
fundo em foco/hover, seta do combo, seleção e estados de erro. 1.514 trocas de
propriedade ao todo. **Nada de posição, tamanho, ordem, texto ou quantidade de
componentes mudou** — só cor, em cima da estrutura original de cada tela.

O primeiro teste desse recolorido no Derramamento (piloto) revelou um problema
de sobreposição de campos que **já existia antes desta mudança** (ver aviso
abaixo) — cores fortes deixaram um bug antigo visível. Uma primeira tentativa
de correção (remover 21 retângulos decorativos + deslocar campos) foi revertida
a pedido do usuário: "não gostei, volte a versão original, só mude as cores em
todas as telas". É o que este item descreve — estrutura 100% original, só cor.

> ⚠️ **Bug de sobreposição conhecido, não corrigido nesta entrega** — no
> formulário de Derramamento, e **muito provavelmente nos outros 6 módulos
> também**: conferido que em todos eles o corpo rolável do formulário começa
> em `Y` absoluto entre 13 e 56 — menor ou perto da altura da faixa
> `cntFaixaAero<Mod>` (52px), que foi inserida por cima sem deslocar nada para
> baixo. Com a cor antiga (preto fino) isso passava despercebido; com cor mais
> forte fica visível. Ver o print enviado pelo usuário em 2026-09-22. Correção
> disponível (a mesma que foi revertida no Derramamento: deslocar `Y` em
> +52px nos campos afetados) — avisar antes de reaplicar em qualquer módulo.

### 13 · Cabeçalho preto em FOD/CSO/Vistoria/Fauna/frmHome (2026-09-22)

O segundo teste ("não veio com a cor") mostrou o cabeçalho de FOD ainda preto.
Causa: os **21 cabeçalhos dos 7 módulos** já viravam `nfCorPrimaria`
automaticamente porque `build/gerar.py` reescreve `Fill` de todo controle
`ContainerHeader*` (função `passe_layout`, "identidade visual Motiva" da
entrega anterior). Mas **FOD, CSO, Vistoria Safety Fauna, Fauna e `frmHome`
nunca passam por `gerar.py`** — FOD/CSO/Vistoria vão por `gerar_forms.py`
(que só mexe em filtro de segurança, não em cor), Fauna também, e `frmHome`
não passa por nenhum gerador. O cabeçalho dessas 5 telas sempre foi preto
fixo e nunca esteve amarrado ao token, em nenhuma entrega anterior.

Corrigido diretamente nos 5 arquivos-fonte: `Fill` do container de cabeçalho
(`HeaderContainer1` / `HeaderContainer1_1` / `HeaderContainer1_2` em
FOD/CSO/Vistoria, `ContainerHeader_11` em Fauna, `ContainerHeader_8` em
`frmHome`) passou de `RGBA(0,0,0,1)` para `nfCorPrimaria`. Fauna também tinha
a faixa divisória de 10px (`Rectangle6_3`) na mesma situação — corrigida
junto, mesmo tratamento que os 7 módulos já tinham.

### 14 · `frmHome` recriada (2026-09-22)

`frmHome` nunca fez parte desta entrega — nunca foi alterada, por isso nunca
teve versão em `out/`. O usuário apagou a tela por engano no Studio em
2026-09-22. [00_frmHome.pa.yaml](00_frmHome.pa.yaml) é o conteúdo original do
export (2026-08-31) com três correções:

1. Recolorido do item 13 (só o `Fill` do cabeçalho, `ContainerHeader_8`).
2. **Bug de laço de redirect, achado ao incluir `frmHome` na varredura pela
   primeira vez**: o logo Motiva do próprio cabeçalho fazia
   `Navigate(frmHome, ...)` sem `Set(var_redirectAN, Blank())` antes — o mesmo
   bug que o item 8 da entrega original já tinha corrigido em **todas as
   outras telas**, mas `frmHome` nunca passou por aquela correção porque
   nunca esteve em `out/`. Corrigido com o mesmo padrão das demais.
3. Nenhum outro campo, posição ou fórmula foi tocado.

**Colar por último**: os botões do menu navegam para os módulos pelo nome
(`ScreenModColisaoVeiculos` etc.), que precisam existir antes — já existem no
app do usuário, então a ordem só importa se o app estiver sendo remontado do
zero.

> `build/auditar_nav.py` acusa 2 falsos positivos em `frmHome` (linhas 435 e
> 565, `Navigate(LookUp(col_NavTelas, ...))`): é navegação dinâmica, a tela é
> escolhida em tempo de execução pelo `Id` do módulo, então o script não
> consegue resolver o nome estaticamente. Comportamento correto, não é bug.

### 15 · `Container38_3` sem `Width` em `ScreenColisaoVeiculosDetalhes` (2026-09-22)

O print da tela de Detalhes de Colisão de Veículos mostrou os três blocos
(`Ocorrido em:` / `Descrição` / `Cadastrado por:`) sobrepostos — as três
colunas usam `X` absoluto (17 / 345 / 875) dentro de um container
`ManualLayout` (`Container38_3`) que **não tinha `Width` definido**, ao
contrário de todo container irmão nesta e nas outras telas. Sem largura, o
container não tinha onde acomodar colunas que vão até X=1075.

**Pré-existente, não relacionado a cor** — nunca toquei posição ou tamanho
nesta tela antes disso. Corrigido com `Width: =Parent.Width`, a mesma
convenção já usada pelo container pai. Não removi nem reposicionei nada.

Testei as outras 6 telas de Detalhes e as 7 de Lista/Forms atrás do mesmo
padrão (container `ManualLayout` com filho a `X > 400` sem `Width` próprio) —
nenhuma outra ocorrência encontrada. Não é o mesmo bug do item 12 (aquele é a
faixa de aeroporto sem espaço reservado); isso aqui parece ter sido um erro
pontual desta tela específica, não sistêmico.

### 16 · `ScreenExcluir`, `ScreenAnaliseSafety` e `ScreenDesdobramentos` recoloridas (2026-09-22)

As três eram telas de apoio nunca tocadas por esta entrega, então tinham
ficado de fora do lote de cor do item 11 (que só cobriu os 7 módulos + FOD/
CSO/Vistoria/Fauna). Mesmo tratamento das demais: cor via token, cabeçalho
preto (`ContainerHeader_4` em AnaliseSafety, `ContainerHeader_3` em
Desdobramentos — ScreenExcluir não tem cabeçalho desse padrão) e verificação
do bug de sobreposição — nenhuma ocorrência nas três.

`ScreenDesdobramentos` também tinha o **mesmo bug de laço de redirect** da
`frmHome` (item 14): o logo do cabeçalho navegava para `frmHome` sem limpar
`var_redirectAN`. Corrigido com o mesmo padrão. É a tela de anotação/anexo
aberta pelo botão "Desdobramentos" na lista de cada módulo — nunca tinha
estado em `out/`, por isso nunca tinha passado por essa checagem.
[00_ScreenDesdobramentos.pa.yaml](00_ScreenDesdobramentos.pa.yaml) é a
entrega, mesma lógica da `frmHome`: conteúdo original + essas correções, mais
nada tocado.

### 17 · Botão "Editar" habilitado nos 7 módulos (2026-09-22)

**O que havia antes**: em FOD, CSO e Vistoria Safety Fauna o "Editar" já
funcionava de verdade (Form nativo, `EditForm`/`SubmitForm`). Nos **7 módulos
de ocorrência**, o botão existia visualmente mas estava **sempre travado e sem
nenhuma ação** (`DisplayMode.Disabled`, `OnSelect` vazio) — não era uma
condição bloqueando, era um recurso nunca implementado. Esses módulos não
usam Form nativo: gravam campo a campo com `Patch()` direto, então "editar"
precisou ser construído do zero: carregar o registro escolhido, pré-preencher
os campos, e no Salvar decidir entre atualizar o registro existente ou criar
um novo.

**Decisões do usuário (2026-09-22)**: habilitar nos 7 módulos de uma vez;
incluir os registros filhos (envolvidos/fotos/itens atingidos) na edição,
não só os campos do pai; mesma regra de permissão de quem já pode ver o
registro (sem trava nova).

**O que cada módulo libera** — só campos "simples" (um controle, uma coluna),
nunca campos compostos por dois controles, condicionados a outro campo,
checkbox virando texto, ou sub-registro codificado como string:

| Módulo | Campos editáveis | Filhos reconciliáveis |
|---|---|---|
| Colisão de Veículos | 7 (todos) | Envolvidos + Fotos |
| Excursão de Pista | 16 (todos) | Fotos |
| Incursão de Pista | 11 (todos os do pai) | Fotos — **Envolvidos só leitura** |
| Jet Blast | 13 (todos) | Fotos + Itens atingidos |
| Derramamento | 21 de ~27 | Fotos |
| Interferência Externa | 15 de ~45 ("Dados gerais" só) | Fotos |
| Ocorrência de Solo | 26 de ~30 | Fotos |

**Por que Derramamento/Interferência Externa/Ocorrência de Solo ficaram
parciais**: têm campos que juntam dois controles (`local` = Aero **ou**
Outros, um dos dois sempre vazio), blocos inteiros condicionados por uma
variável em vez de um controle (Balão/Laser da Interferência Externa), ou
dado codificado como texto solto (`ocoSolo_danIdentific` é até 23 checkboxes
concatenadas numa string só; `ocoSolo_opEnvolv01`–`04` guardam um "envolvido"
inteiro como `"Nome: X;-;Matrícula: Y;-;..."` dentro da própria coluna, sem
ser registro filho de verdade). Decifrar essas strings de volta pra
pré-preencher um campo é o mesmo tipo de risco de silenciosamente corromper
o formato — ficaram como estão, só visíveis, não editáveis.

**Por que a "Envolvidos" da Incursão de Pista ficou só leitura**: ao gravar,
funde três sub-blocos (aeronave/veículo/pessoa) na mesma coluna — ex.:
`incPistaEnv_acaoEvasiva: aer_acaoEvasiva & vei_acaoEvasiva & pes_acaoEvasiva`,
só um dos três nunca é vazio. Mesma classe de risco dos campos compostos do
pai. A coleção é explicitamente esvaziada ao abrir a edição (`Clear(...)`),
pra garantir que não sobre nenhum resíduo de uma sessão anterior que viraria
filho novo desta ocorrência ao salvar.

**Limitação encontrada ao validar o build**: `Classic/DatePicker` usa
`DefaultDate`, não `Default` (corrigido — o campo `data` de todo módulo usa a
propriedade certa). Mas `Classic/ComboBox` (controles com prefixo `drop`
nesta base — diferente de `Classic/DropDown`, prefixo `cmb`) **não aceita
pré-preenchimento simples** — precisaria de `DefaultSelectedItems` com uma
tabela no formato exato de `Items`/`DisplayFields`, e sem conseguir testar no
Studio, montar essa tabela errada é risco sem necessidade. Esses campos
**continuam sendo gravados normalmente ao salvar** — só não vêm com o valor
atual preenchido ao abrir a edição; é preciso reselecionar. Afetados:

| Módulo | Campo(s) ComboBox sem pré-preenchimento |
|---|---|
| Colisão de Veículos | Mapa de grade (as duas letras) |
| Derramamento | Fluído, Origem do vazamento, Companhia aérea |
| Jet Blast | Operador aéreo |
| Ocorrência de Solo | Companhia aérea, Impacto na operação, Natureza da atividade, Tipo de equipe |

**Mecanismo de conciliação dos filhos** (evita duplicar ou perder registro):
cada linha da coleção carrega um `dbId` — vazio se foi adicionada nesta
edição, ou o ID real do SharePoint se já existia antes. Ao salvar: `dbId`
vazio grava novo; `dbId` preenchido atualiza o existente. Uma cópia da
coleção como estava ao abrir a edição (`<coleção>_orig`) permite achar o que
foi removido durante a edição e apagar do SharePoint.

**Onde mexeu**: `build/gerar_editar.py` (novo arquivo, todo o mecanismo) +
uma linha em `build/gerar.py` (a checagem que localiza o `Patch()` do pai em
`cirurgia_gravacao` foi afrouxada para aceitar `Defaults(` em qualquer parte
do argumento, não só no início — necessário porque `gerar_editar.py` já
embrulha esse argumento antes do `cirurgia_gravacao` rodar).

> ⚠️ **Não testado no Studio.** Validado o que dá pra validar sem abrir o
> Studio: YAML válido, propriedades conferidas contra o dicionário de 42
> exports, navegação, init das visões, build idempotente. O que **não** dá
> pra confirmar sem testar de verdade: se o pré-preenchimento mostra o valor
> certo em cada campo, se salvar uma edição atualiza o registro certo (e não
> cria um duplicado), se remover uma foto/envolvido durante a edição
> realmente apaga do SharePoint e não só da tela. **Teste com um registro que
> não seja de produção, ou que você possa conferir/desfazer, antes de
> confiar nisso com dado real.**

**Achado testando no Studio (2026-09-22)**: exatamente o tipo de erro que o
aviso acima previa. A conciliação dos filhos usava `ThisRecord.dbId` — válido
em Power Fx em geral, mas **não reconhecido nesta versão/app** ("'ThisRecord'
não é reconhecido"). Corrigido para referenciar o campo direto (`dbId`, sem
prefixo), o mesmo padrão que o resto desta base inteira já usa dentro de
`ForAll` (ex.: `colVeiEnv_nome: nome`). Reconstruído e revalidado nos 7
módulos. Reforça o aviso acima: ainda não é hora de assumir que o resto está
certo sem testar campo a campo.

### 18 · `ScreenAcessIndFaunaForms` recolorida (2026-09-22)

Última tela que faltava — ficou de fora de todas as rodadas de cor porque não
é gerada por nenhum script (`out/09_*`, manual, mesma situação do
`01_App.pa.yaml`). Diferente das outras: já tinha uma paleta azul própria
(`#3860B2`/`#00126B` e variações), aplicada antes desta sessão — não preto
puro. Mapeei essas cores específicas para os mesmos tokens (61 propriedades),
mais o cabeçalho (`ContainerHeader_32.Fill`). Nenhum campo, posição ou
fórmula tocado.

### 19 · Erros achados pelo Verificador de aplicativo do Studio (2026-09-22)

Depois do item 17 (botão Editar), usei o **Verificador de aplicativo** do
próprio Studio (ícone de estetoscópio, painel direito — acesso direto ao app
ligado, só para *análise*; toda correção foi feita aqui nos arquivos-fonte,
não editando dentro do Studio) para achar erros de fórmula reais, não só o que
os meus próprios checadores locais cobrem. Achou **410 erros** em 12 telas.
Catalogados um a um, caem em 4 causas — as 3 primeiras eram bugs meus, desta
mesma sessão (item 17); a 4ª e a 5ª (CSO/Vistoria) já eram conhecidas.

**a) Coleção com dois formatos incompatíveis (321 erros — 48/48/48/48/41/45/43
nos 7 módulos)**
O botão "Editar" (item 17) carrega cada filho com `ClearCollect(col, ForAll(...,
{dbId: ID, ...}))`. O botão "Adicionar", que já existia antes desta sessão,
grava com `Collect(col, {id: <contador local>, ...})`. Duas formas de povoar a
**mesma** coleção com colunas diferentes (`dbId` só numa, `id` só na outra) — o
Studio unifica o tipo de `col_xxx` no app inteiro e reprova `Clear`/
`ClearCollect` em cascata, em toda tela que usa essa coleção. Corrigido nos 9
filhos reconciliáveis: as duas formas agora escrevem `dbId` **e** `id`
(`build/gerar_editar.py`, função `onselect_editar` e nova `aplicar_dbid_blank`;
aplicado aos arquivos já gerados por `build/corrigir_shape_colecoes.py`, script
de uso único, não faz parte do pipeline de regeneração).

**b) Indentação do reset do "Cadastrar" (cosmético, sem erro funcional)**
O texto que zera `var_editando<mod>`/`var_registro<mod>` ao clicar em
"Cadastrar" saía com 1 espaço a mais de recuo (contava o `=` do início da
fórmula como se fosse recuo). YAML de bloco `|-` tolera — não quebrava nada —
mas ficava um espaço perdido no início de 6 linhas por módulo. Corrigido na
origem (`aplicar_lista`) e nos arquivos já gerados.

**c) `var_item` com tipo ambíguo em `ScreenExcluir` (30 erros) + `Remove` quebrado (8 pontos)**
Os botões "Excluir" de 9 origens diferentes (7 módulos + Fauna + Desdobramentos)
navegam pra `ScreenExcluir` passando `{var_item: ThisItem, ...}` — `ThisItem` é
um registro de uma tabela do SharePoint diferente em cada origem. Mesmo
problema do item (a), só que numa variável de contexto em vez de coleção:
`var_item.colVei_id`, `var_item.derFlu_id` etc. viravam "tipo não encontrado".
`var_item` só era lido de duas formas (`.ID` e `.<mod>_id`, nunca o registro
inteiro) — exceto em **8 pontos** que eu só achei ao ler o arquivo depois da
1ª correção: `Remove(tabela, var_item)`, passando o registro inteiro direto
pro `Remove`. Como parte da correção troquei `var_item` por dois números
homogêneos:
- `var_item_id: ThisItem.ID` (substitui `var_item.ID`)
- `var_item_chave: ThisItem.<mod>_id` (substitui `var_item.<mod>_id`, só nos
  7 módulos com filhos)

e os 8 `Remove(tabela, var_item)` viraram
`Remove(tabela, LookUp(tabela, ID = var_item_id))`. Mudado em `build/gerar_apoio.py`
(função `corrigir_excluir`, que já fazia a reescrita por ramo — só troquei o
que ela escreve) e nos 9 botões de origem, em `msapp/Src`. Script de uso único:
`build/corrigir_var_item.py`.

**d) `ScreenFauna` (21 erros) — a tela de cadastro nunca foi colada**
Todos os 21 eram "o nome não é válido" para `ScreenFaunaForms` e pra controles
dela (ex.: `FormInspPistaItensDetalhesPRESENCA`) — porque essa tela **nunca
esteve em `out/`**: existe em `msapp/Src/ScreenFaunaForms.pa.yaml` (5.452
linhas) mas nenhum script a levava pra `out/`, e ninguém colou ela no Studio.
Sem ela colada, o botão "Cadastrar"/"Afugentar" de Fauna literalmente não abre
nada — não era só o Verificador reclamando, era funcionalidade quebrada.
Entreguei como `10_ScreenFaunaForms.pa.yaml` (ver Passo 4), com o mesmo bug de
laço de redirect do logo (item 8) corrigido. **Pendência:** ainda está com a
paleta azul original, não a teal da Asur — ver aviso no cabeçalho do arquivo.

Junto, achei um bug de cópia separado (não fazia parte dos 410, achei lendo o
código ao lado): em `ScreenAcessIndFaunaForms`, uma `BorderColor` comparava
`CountRows(col_incPistaImg)` — coleção de **Incursão de Pista**, que não
existe nesta tela — em vez de `col_aceIndFauGalleryImg`, a coleção certa (as
outras 3 referências na mesma tela já usavam a certa). Corrigido em
`msapp/Src` e em `09_ScreenAcessIndFaunaForms.pa.yaml`.

**Não mexidos — já documentados, aguardando sua decisão (ver "Pendências" abaixo):**
- `ScreenCSO` (16 erros do Verificador): mesma causa do item 2 de
  "Pendências" — `Aeroporto`/`'Data/Hora'` não existem no esquema exportado de
  `'1 - CSO'`. Você já confirmou manter como está.
- `ScreenVistoriaSafetyFauna` (20 erros do Verificador): mesma causa do item 1
  de "Pendências" — lista de `'1 - CSO'`, grava em `tbl_vistoriaSafetyFauna`.

---

## Bugs de cópia encontrados no export

| Onde | O quê |
|---|---|
| `ScreenExcursaoPista` | galeria lia `ThisItem.derFlu_aeroporto`, `derFlu_data`, `derFlu_hora` — colunas da lista de Derramamento. Protocolo e data saíam em branco. |
| `ScreenJetBlast` | protocolo lia `ThisItem.derFlu_aeroporto`. IATA errado/branco. |
| `ScreenExcluir`, ramo Colisão | filhos apagados por `var_item.derFlu_id` — coluna inexistente ali. Envolvidos, imagens e desdobramentos **nunca** eram apagados. |
| `ScreenExcluir`, todos os ramos | filhos apagados por `var_item.ID` (ID do SharePoint), mas os formulários gravaram os filhos com `<mod>_id` (max+1). Os dois divergem depois da primeira exclusão → apagava os filhos da ocorrência errada. |
| `ScreenIncursaoPista` | `IsBlank(cmbStatus_4...)` testava um controle de outra tela (já vinha comentado no export). |
| `ScreenDerramamentoFluido`, `ScreenExcursaoPista`, `ScreenIncursaoPista` | o botão "Cadastrar" abria o formulário limpando `col_colVeiEnvolvidos` e `col_colVeiGalleryImg` — coleções de **Colisão de Veículos**. As coleções do próprio módulo ficavam com o conteúdo do cadastro anterior, e as de Colisão eram zeradas de fora. Agora cada módulo limpa as suas (campo `filhos` em `build/modulos.py`). |
| `ScreenFauna` | o botão "Atualizar galeria" montava `col_presenca` com `StartsWith(Aeroporto, combo.Selected.IATA)` e nada mais. Com o combo em branco `StartsWith` casa toda linha, então a coleção do cliente recebia os 17 aeroportos mesmo no perfil Base. A galeria filtrava `varEscopoIATA` depois — nada vazava na tela, mas o dado saía do SharePoint. O escopo virou a primeira condição do `Filter`. |

Todos corrigidos nos arquivos entregues.

---

## Pendências que precisam da sua confirmação

1. **`ScreenVistoriaSafetyFauna`** — a galeria consulta `'1 - CSO'` mas o
   formulário grava em `tbl_vistoriaSafetyFauna`. A tela lista reunião de CSO e
   salva vistoria; o que é gravado nunca aparece. Detalhes no cabeçalho de
   `07_ScreenVistoriaSafetyFauna.pa.yaml`.
2. ~~**`ScreenCSO`**~~ — **decidido em 2026-09-22: manter como está.** As fórmulas
   usam `Aeroporto` e `'Data/Hora'` em `'1 - CSO'`, mas o esquema exportado só tem
   `Data` e nenhuma coluna de aeroporto — o usuário confirmou que não é para mexer,
   sem verificar no SharePoint. Nenhum código desta tela foi alterado.
3. **Dados legados** — `<mod>_id` passa a ser igual ao `ID` do SharePoint só nos
   registros **novos**. Os antigos mantêm o valor sequencial. Por isso a exclusão
   compara por `<mod>_id`: é a única chave válida para os dois conjuntos. Se quiser
   unificar, é um script de correção em massa nas listas.
4. **Índices SharePoint** — criar índice em `<mod>_data`, `<mod>_aeroporto` e
   `<mod>_bloco` nas 7 listas, senão a consulta delegável esbarra no limite de
   5.000 itens por view.

---

## O que foi validado localmente

- YAML sintaticamente válido nas 13 telas.
- Estrutura raiz `Screens:` / 2 espaços / 4 espaços conferida.
- Toda propriedade conferida contra um dicionário `{Control@versão: propriedades}`
  montado a partir dos 42 exports originais (32 tipos de controle) — defesa contra
  `PA2108`.
- Parênteses e aspas balanceados em cada uma das ~22 mil fórmulas.
- 1.552 nomes de controle, nenhum duplicado entre as 7 telas novas.
- Nenhuma referência residual às telas antigas fora dos comentários.
- Nenhum `ForAll` de filho fora do guard `<mod>_id > 0`.
- **Init das visões**: o corpo do `OnVisible` de cada tela de Forms/Detalhes de origem
  aparece, inteiro e contíguo, em **todos** os pontos que entram naquela visão. É o
  que impede a consolidação de engolir a carga das coleções do detalhe — nenhum outro
  checador percebia, porque o YAML continua válido e o nome da coleção continua certo.
- Nenhum `Navigate(frmHome)` sem `Set(var_redirectAN, Blank())` antes.
- Nenhum módulo limpando coleção filha de outro módulo.
- Gerador idempotente (mesmo hash em duas execuções).
- Navegação auditada nas 15 telas: nenhum `Navigate` aponta para nome de controle,
  nenhuma tela consolidada tem navegação interna sobrando, nenhuma tela referenciada
  deixa de existir. Comentário Power Fx (`//`, `/* */`) é ignorado na varredura — é
  onde mora código morto do export.
- Snippet pt-BR conferido por conversão de ida e volta (pt-BR → invariante devolve o
  original exato) e por varredura de vírgula separadora remanescente. Strings e
  comentários preservados: `Notify("a, b; c", ...)` e `// vírgula em prosa` não são
  tocados.

**Não validado**: nada disso substitui colar no Studio conectado às listas reais e
testar criar / visualizar / excluir / anexar / filtrar em cada módulo, com um
usuário de cada perfil (Base, Bloco, Sede).
