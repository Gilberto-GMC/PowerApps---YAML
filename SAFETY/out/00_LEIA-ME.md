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

Agora que as 7 existem, cole (qualquer ordem):

| Arquivo | Tela |
|---|---|
| `03_ScreenExcluir.pa.yaml` | `ScreenExcluir` |
| `04_ScreenAnaliseSafety.pa.yaml` | `ScreenAnaliseSafety` |
| `05_ScreenFOD.pa.yaml` | `ScreenFOD` |
| `06_ScreenCSO.pa.yaml` | `ScreenCSO` |
| `07_ScreenVistoriaSafetyFauna.pa.yaml` | `ScreenVistoriaSafetyFauna` |
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
O spinner é desligado em todos os ramos de saída, inclusive validação e erro.

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

---

## Bugs de cópia encontrados no export

| Onde | O quê |
|---|---|
| `ScreenExcursaoPista` | galeria lia `ThisItem.derFlu_aeroporto`, `derFlu_data`, `derFlu_hora` — colunas da lista de Derramamento. Protocolo e data saíam em branco. |
| `ScreenJetBlast` | protocolo lia `ThisItem.derFlu_aeroporto`. IATA errado/branco. |
| `ScreenExcluir`, ramo Colisão | filhos apagados por `var_item.derFlu_id` — coluna inexistente ali. Envolvidos, imagens e desdobramentos **nunca** eram apagados. |
| `ScreenExcluir`, todos os ramos | filhos apagados por `var_item.ID` (ID do SharePoint), mas os formulários gravaram os filhos com `<mod>_id` (max+1). Os dois divergem depois da primeira exclusão → apagava os filhos da ocorrência errada. |
| `ScreenIncursaoPista` | `IsBlank(cmbStatus_4...)` testava um controle de outra tela (já vinha comentado no export). |

Todos corrigidos nos arquivos entregues.

---

## Pendências que precisam da sua confirmação

1. **`ScreenVistoriaSafetyFauna`** — a galeria consulta `'1 - CSO'` mas o
   formulário grava em `tbl_vistoriaSafetyFauna`. A tela lista reunião de CSO e
   salva vistoria; o que é gravado nunca aparece. Detalhes no cabeçalho de
   `07_ScreenVistoriaSafetyFauna.pa.yaml`.
2. **`ScreenCSO`** — as fórmulas usam `Aeroporto` e `'Data/Hora'` em `'1 - CSO'`,
   mas o esquema exportado só tem `Data` e nenhuma coluna de aeroporto. Confirmar
   no SharePoint se o cache do `.msapp` está velho ou se o filtro nunca funcionou.
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
