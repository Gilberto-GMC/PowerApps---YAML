# `App.Formulas` — Gestão de Frotas (Motiva Aeroportos)

Camada de dados estáticos e tokens de tema do app **Motiva — Gestão de Frotas**.

> **Locale:** este arquivo vai colado na **barra de fórmulas** do Power Apps Studio (propriedade `Formulas` do
> objeto `App`), portanto está em **pt-BR**: `;` separa argumentos, `;;` termina cada definição, decimal com
> vírgula. Os arquivos `.pa.yaml` das telas continuam em formato **invariante** (`,` e `.`) — não misture os dois.

> **Como colar:** Studio → árvore de objetos → selecionar **App** → propriedade **Formulas** → colar tudo.
> Não é o `OnStart`.

## Por que named formula e não `ClearCollect` no `OnStart`

| | `ClearCollect` no `OnStart` | Named formula (adotado) |
|---|---|---|
| Custo na abertura do app | Executa sempre, mesmo que a tela não use | Zero — só calcula quando alguém lê |
| Leitura no app | `Filter(colAeros; ...)` | **Idêntica** |
| Alterável em runtime | Sim | Não (é constante) |

Nenhuma fórmula de leitura muda ao migrar de um para o outro. A única restrição é que **nada pode `Collect`,
`Patch` ou `Clear` dentro dessas tabelas** — como são estáticas, não é limitação real. Se um dia alguma precisar
ser editável em runtime, basta devolvê-la ao `OnStart` como `ClearCollect`, sem tocar em quem a lê.

Isso vale para **dado estático**. O cache da lista mestre (`colFrota`) é outro assunto e é coleção de verdade —
ver seção 5.

---

## 1. Aeroportos

Os 16 aeroportos da rede. A **primeira linha em branco é intencional**: é ela que dá a opção vazia nos dropdowns
de filtro. Em dropdown de campo obrigatório, filtrar com `Filter(colAeros; IATA <> "")`.

`Cat` = categoria contraincêndio do aeródromo e `Classe` = classe do aeroporto — já atendem o módulo 21 (SESCINC)
sem coluna nem lista adicional.

```powerfx
// ✈️ Aeroportos da rede — 16 unidades + linha vazia para filtros
colAeros =
Table(
    {
        IATA: "";
        ICAO: "";
        Bloco: "";
        Aeroporto: "";
        Cat: 0;
        Classe: ""
    };
    {
        IATA: "GYN";
        ICAO: "SBGO";
        Bloco: "CENTRAL";
        Aeroporto: "GOIÂNIA";
        Cat: 7;
        Classe: "III"
    };
    {
        IATA: "IMP";
        ICAO: "SBIZ";
        Bloco: "CENTRAL";
        Aeroporto: "IMPERATRIZ";
        Cat: 6;
        Classe: "II"
    };
    {
        IATA: "PMW";
        ICAO: "SBPJ";
        Bloco: "CENTRAL";
        Aeroporto: "PALMAS";
        Cat: 7;
        Classe: "II"
    };
    {
        IATA: "PLU";
        ICAO: "SBBH";
        Bloco: "CENTRAL";
        Aeroporto: "PAMPULHA";
        Cat: 5;
        Classe: "II"
    };
    {
        IATA: "PNZ";
        ICAO: "SBPL";
        Bloco: "CENTRAL";
        Aeroporto: "PETROLINA";
        Cat: 6;
        Classe: "II"
    };
    {
        IATA: "SLZ";
        ICAO: "SBSL";
        Bloco: "CENTRAL";
        Aeroporto: "SÃO LUIS";
        Cat: 7;
        Classe: "III"
    };
    {
        IATA: "THE";
        ICAO: "SBTE";
        Bloco: "CENTRAL";
        Aeroporto: "TERESINA";
        Cat: 7;
        Classe: "III"
    };
    {
        IATA: "BFH";
        ICAO: "SBBI";
        Bloco: "SUL";
        Aeroporto: "BACACHERI";
        Cat: 5;
        Classe: "II"
    };
    {
        IATA: "CWB";
        ICAO: "SBCT";
        Bloco: "SUL";
        Aeroporto: "CURITIBA";
        Cat: 7;
        Classe: "IV"
    };
    {
        IATA: "JOI";
        ICAO: "SBJV";
        Bloco: "SUL";
        Aeroporto: "JOINVILLE";
        Cat: 6;
        Classe: "II"
    };
    {
        IATA: "NVT";
        ICAO: "SBNF";
        Bloco: "SUL";
        Aeroporto: "NAVEGANTES";
        Cat: 7;
        Classe: "III"
    };
    {
        IATA: "BGX";
        ICAO: "SBBG";
        Bloco: "SUL";
        Aeroporto: "BAGÉ";
        Cat: 0;
        Classe: "I"
    };
    {
        IATA: "IGU";
        ICAO: "SBFI";
        Bloco: "SUL";
        Aeroporto: "FOZ DO IGUAÇU";
        Cat: 7;
        Classe: "III"
    };
    {
        IATA: "LDB";
        ICAO: "SBLO";
        Bloco: "SUL";
        Aeroporto: "LONDRINA";
        Cat: 7;
        Classe: "II"
    };
    {
        IATA: "PET";
        ICAO: "SBPK";
        Bloco: "SUL";
        Aeroporto: "PELOTAS";
        Cat: 5;
        Classe: "I"
    };
    {
        IATA: "URG";
        ICAO: "SBUG";
        Bloco: "SUL";
        Aeroporto: "URUGUAIANA";
        Cat: 5;
        Classe: "I"
    }
);;

// Aeroportos válidos para dropdown de campo obrigatório (sem a linha vazia)
colAerosValidos = Sort(Filter(colAeros; IATA <> ""); Aeroporto; SortOrder.Ascending);;

// Blocos regionais distintos, para filtro de gestor de bloco
colBlocos = Sort(Distinct(colAerosValidos; Bloco); Value; SortOrder.Ascending);;
```

---

## 2. Enumerações do Módulo 1

Substituem colunas do tipo **Escolha** no SharePoint. As colunas correspondentes são **Texto (1 linha)** e o app
grava o texto direto — sem `Choices()`, sem `.Value` no `Patch`, coluna indexável e filtro `=` delegável.

### 2.1 Tipo de ativo — dirige o formulário

Esta é a tabela mais importante do arquivo. As colunas `ExigePlaca`, `MedidorPadrao` e `LadoAr` **substituem
`If` encadeado nas telas**: o formulário lê o tipo escolhido e já sabe o que exigir. É o que permite carro, GSE
sem placa e CCI conviverem na mesma lista mestre.

```powerfx
// 🚚 Tipos de ativo — ExigePlaca/MedidorPadrao/LadoAr dirigem a validação do formulário
colTipoAtivo =
Table(
    { Ordem: 1; Tipo: "Veículo Leve";         ExigePlaca: true;  MedidorPadrao: "Hodômetro (km)"; LadoAr: false };
    { Ordem: 2; Tipo: "Veículo Pesado";       ExigePlaca: true;  MedidorPadrao: "Hodômetro (km)"; LadoAr: true  };
    { Ordem: 3; Tipo: "Utilitário";           ExigePlaca: true;  MedidorPadrao: "Hodômetro (km)"; LadoAr: true  };
    { Ordem: 4; Tipo: "Motocicleta";          ExigePlaca: true;  MedidorPadrao: "Hodômetro (km)"; LadoAr: false };
    { Ordem: 5; Tipo: "Ônibus/Micro-ônibus";  ExigePlaca: true;  MedidorPadrao: "Hodômetro (km)"; LadoAr: true  };
    { Ordem: 6; Tipo: "Reboque/Semirreboque"; ExigePlaca: false; MedidorPadrao: "Não se aplica";  LadoAr: true  };
    { Ordem: 7; Tipo: "Máquina/Trator";       ExigePlaca: false; MedidorPadrao: "Horímetro (h)";  LadoAr: true  };
    { Ordem: 8; Tipo: "GSE";                  ExigePlaca: false; MedidorPadrao: "Horímetro (h)";  LadoAr: true  };
    { Ordem: 9; Tipo: "CCI/SESCINC";          ExigePlaca: true;  MedidorPadrao: "Ambos";          LadoAr: true  }
);;
```

**Sobre `Reboque/Semirreboque` com `ExigePlaca: false`:** semirreboque rodoviário tem placa, mas dolly e carreta
de bagagem do pátio não têm. `false` apenas **deixa de bloquear** — a placa continua preenchível quando existir.
O caminho inverso (`true`) impediria cadastrar dolly, que é o caso mais comum no sítio aeroportuário.

### 2.2 Demais enumerações

```powerfx
colCategoriaUso =
Table(
    { Ordem: 1; Valor: "Administrativo" };
    { Ordem: 2; Valor: "Operacional Lado Terra" };
    { Ordem: 3; Valor: "Operacional Lado Ar" };
    { Ordem: 4; Valor: "Emergência/SESCINC" };
    { Ordem: 5; Valor: "Manutenção" };
    { Ordem: 6; Valor: "Segurança/AVSEC" }
);;

colCombustivel =
Table(
    { Ordem: 1; Valor: "Gasolina" };
    { Ordem: 2; Valor: "Etanol" };
    { Ordem: 3; Valor: "Flex" };
    { Ordem: 4; Valor: "Diesel S10" };
    { Ordem: 5; Valor: "Diesel S500" };
    { Ordem: 6; Valor: "GNV" };
    { Ordem: 7; Valor: "Elétrico" };
    { Ordem: 8; Valor: "Híbrido" };
    { Ordem: 9; Valor: "Não se aplica" }
);;

// UsaKm / UsaHoras controlam quais campos de medidor o formulário exige
colTipoMedidor =
Table(
    { Ordem: 1; Valor: "Hodômetro (km)"; UsaKm: true;  UsaHoras: false };
    { Ordem: 2; Valor: "Horímetro (h)";  UsaKm: false; UsaHoras: true  };
    { Ordem: 3; Valor: "Ambos";          UsaKm: true;  UsaHoras: true  };
    { Ordem: 4; Valor: "Não se aplica";  UsaKm: false; UsaHoras: false }
);;

// Cor = controles nativos (RGBA) · Hex = HtmlViewer (string). As duas saem do MESMO token.
colStatusAtivo =
Table(
    { Ordem: 1; Valor: "Ativo";   Cor: thmVerde;      Hex: hxVerde      };
    { Ordem: 2; Valor: "Inativo"; Cor: thmAmbar;      Hex: hxAmbar      };
    { Ordem: 3; Valor: "Baixado"; Cor: thmTextoFraco; Hex: hxTextoFraco }
);;

colSituacaoOper =
Table(
    { Ordem: 1; Valor: "Disponível";    Cor: thmVerde;    Hex: hxVerde    };
    { Ordem: 2; Valor: "Em Uso";        Cor: thmPrimaria; Hex: hxPrimaria };
    { Ordem: 3; Valor: "Em Manutenção"; Cor: thmAmbar;    Hex: hxAmbar    };
    { Ordem: 4; Valor: "Indisponível";  Cor: thmVermelho; Hex: hxVermelho };
    { Ordem: 5; Valor: "Bloqueado";     Cor: thmVermelho; Hex: hxVermelho }
);;

colTipoPropriedade =
Table(
    { Ordem: 1; Valor: "Próprio" };
    { Ordem: 2; Valor: "Locado" };
    { Ordem: 3; Valor: "Comodato" };
    { Ordem: 4; Valor: "Terceiro/Contratada" }
);;

colMedidorOrigem =
Table(
    { Ordem: 1; Valor: "Cadastro" };
    { Ordem: 2; Valor: "BDV" };
    { Ordem: 3; Valor: "Abastecimento" };
    { Ordem: 4; Valor: "Manutenção" };
    { Ordem: 5; Valor: "Vistoria" }
);;

// Nivel: usado para comparar permissão sem encadear If
colPerfil =
Table(
    { Ordem: 1; Valor: "Administrador";   Nivel: 5 };
    { Ordem: 2; Valor: "Gestor de Frota"; Nivel: 4 };
    { Ordem: 3; Valor: "Operador";        Nivel: 3 };
    { Ordem: 4; Valor: "Condutor";        Nivel: 2 };
    { Ordem: 5; Valor: "Consulta";        Nivel: 1 }
);;

// Opções dos dropdowns do FORMULÁRIO — derivadas das tabelas acima, sem redigitar nenhum valor.
// Mesmo motivo dos filtros: o DropDown moderno exige tabela de uma coluna chamada `Value`.
colOpTipo        = ForAll(Sort(colTipoAtivo; Ordem; SortOrder.Ascending) As _t; { Value: _t.Tipo });;
colOpCategoria   = ForAll(colCategoriaUso As _c; { Value: _c.Valor });;
colOpCombustivel = ForAll(colCombustivel As _c; { Value: _c.Valor });;
colOpMedidor     = ForAll(colTipoMedidor As _m; { Value: _m.Valor });;
colOpStatus      = ForAll(colStatusAtivo As _s; { Value: _s.Valor });;
colOpSituacao    = ForAll(colSituacaoOper As _s; { Value: _s.Valor });;
colOpPropriedade = ForAll(colTipoPropriedade As _p; { Value: _p.Valor });;
// `colOpAero` não está aqui: depende do usuário logado. É coleção montada na `scrLoginContexto`.

// Dropdowns de filtro. O DropDown moderno (`DropDown@0.0.45`) só aceita tabela de UMA coluna de
// texto — `["a"; "b"]` — e é lido por `drp.Selected.Value`. Por isso estas três não têm `Ordem`.
// O filtro de aeroporto NÃO está aqui: depende do usuário logado, então é a coleção `colFiltroAero`,
// montada no `OnVisible` da `scrLoginContexto`.
colFiltroStatus = ["Todos"; "Ativo"; "Inativo"; "Baixado"];;

// Ordenação da consulta. "Medidor (maior)" ordena por texto com zero à esquerda,
// que é o jeito de ordenar número sem trocar o tipo da chave no meio do Sort.
colOpOrdem = ["Código"; "Placa"; "Aeroporto"; "Modelo"; "Medidor (maior)"];;

colFiltroSituacao = ["Todos"; "Disponível"; "Em Uso"; "Em Manutenção"; "Indisponível"; "Bloqueado"];;

colFiltroTipo =
[
    "Todos";
    "Veículo Leve";
    "Veículo Pesado";
    "Utilitário";
    "Motocicleta";
    "Ônibus/Micro-ônibus";
    "Reboque/Semirreboque";
    "Máquina/Trator";
    "GSE";
    "CCI/SESCINC"
];;
```

---

## 3. Design System Motiva — tokens

Fonte da verdade: `motiva-controle-de-aeroportos---nova-plataforma/CONTEXTO_POWERAPPS.md`. Roxo institucional
`#391694`, canto reto (`rounded-none`), bloco espaçado em 26 px, título de módulo em caixa alta.

**Duas famílias, uma fonte de cor.** `hx*` são strings hexadecimais — é o que o `HtmlViewer` entende. `thm*` são
as cores dos controles nativos e saem dos mesmos `hx*` por `ColorValue`. Trocar a marca = trocar 13 linhas.

```powerfx
// 🎨 Hex — usados dentro do HTML dos HtmlViewer
hxPrimaria        = "#391694";;   // roxo institucional Motiva
hxPrimariaEscura  = "#2A106E";;
hxPrimariaClara   = "#EDE9FB";;
hxAcao            = "#DD511A";;   // laranja de ação (instruções, CTA)
hxOperacional     = "#0891B2";;
hxSuperficie      = "#FFFFFF";;
hxFundo           = "#F8FAFC";;   // slate claro
hxBorda           = "#C9C5E6";;   // borda institucional clara
hxTexto           = "#1E293B";;
hxTextoFraco      = "#64748B";;
hxVerde           = "#15803D";;
hxAmbar           = "#B45309";;
hxVermelho        = "#B91C1C";;
hxVermelhoSuave   = "#FEF2F2";;   // fundo de aviso crítico
hxAmbarSuave      = "#FFFBEB";;   // fundo de atenção
hxTextoBarra      = "#D6DDE0";;   // texto sobre fundo escuro: barra, trilho, botão colorido
hxTextoBarraSuave = "rgba(214,221,224,.72)";;
hxTextoBarraFraco = "rgba(214,221,224,.5)";;
hxBordaBarra      = "rgba(214,221,224,.28)";;
hxBotaoBarra      = "#BDB2B0";;   // botão fantasma da barra roxa

// 🎨 Cores dos controles nativos — derivadas dos hex acima, nunca redigitadas
thmPrimaria       = ColorValue(hxPrimaria);;
thmPrimariaEscura = ColorValue(hxPrimariaEscura);;
thmPrimariaClara  = ColorValue(hxPrimariaClara);;
thmAcao           = ColorValue(hxAcao);;
thmOperacional    = ColorValue(hxOperacional);;
thmSuperficie     = ColorValue(hxSuperficie);;
thmFundo          = ColorValue(hxFundo);;
thmBorda          = ColorValue(hxBorda);;
thmTexto          = ColorValue(hxTexto);;
thmTextoFraco     = ColorValue(hxTextoFraco);;
thmVerde          = ColorValue(hxVerde);;
thmAmbar          = ColorValue(hxAmbar);;
thmVermelho       = ColorValue(hxVermelho);;
thmTextoBarra     = ColorValue(hxTextoBarra);;
thmBotaoBarra     = ColorValue(hxBotaoBarra);;
thmTextoInverso   = RGBA(255; 255; 255; 1);;
thmTransparente   = RGBA(0; 0; 0; 0);;

// 🔤 Tipografia
// Sora é a fonte da marca, mas não existe no Power Apps e o sanitizador do HtmlViewer não carrega
// webfont. Segoe UI é a substituta e está em todos os clientes.
thmFonte          = Font.'Segoe UI';;
htmlFonte         = "font-family:'Segoe UI',Arial,sans-serif;-webkit-font-smoothing:antialiased;";;
thmTamTitulo      = 19;;
thmTamSubtitulo   = 14;;
thmTamCorpo       = 12;;
thmTamRotulo      = 11;;

// 📐 Espaçamento e forma — Motiva usa canto reto
thmEsp            = 13;;
thmEspBloco       = 26;;
thmRaio           = 0;;
thmAlturaCampo    = 42;;
thmAlturaBarra    = 72;;
```

**Ordem de declaração não importa** em `App.Formulas` — o Power Apps resolve a dependência sozinho. Por isso
`colStatusAtivo` pode referenciar `hxVerde` mesmo estando declarado antes na leitura deste documento.

> **Texto sobre fundo escuro é `hxTextoBarra` (#D6DDE0), nunca branco puro.** Vale para a barra roxa, o trilho
> lateral e todo botão de fundo roxo ou laranja: `Color: =thmTextoBarra` no `HtmlViewer`,
> `FontColor: =thmTextoBarra` no `Button`, e dentro do HTML os tokens `hxTextoBarra`, `hxTextoBarraSuave`,
> `hxTextoBarraFraco` e `hxBordaBarra` no lugar de `rgba(255,255,255,…)`. O `validar_telas.py` reprova branco
> literal e controle claro faltando.
>
> **Nenhuma tela declara cor literal.** Se um `RGBA(` ou um `#` aparecer dentro de um `.pa.yaml`, é regressão —
> a única exceção são os `rgba(255,255,255,.34)` de opacidade sobre o roxo, dentro do HTML da tela de login.

---

## 4. Como as telas consomem

```powerfx
// Dropdown de tipo de ativo (Items)
Sort(colTipoAtivo; Ordem; SortOrder.Ascending)

// Regra de placa obrigatória — sem If encadeado
With(
    { _t: LookUp(colTipoAtivo; Tipo = drpTipoAtivo.Selected.Tipo) };
    _t.ExigePlaca And IsBlank(txtPlaca.Value)
)

// Bloco gravado junto com o aeroporto (a mestre precisa dele para o Power BI)
LookUp(colAeros; IATA = drpAeroporto.Selected.IATA).Bloco

// Cor do selo de status — .Cor num controle nativo, .Hex dentro do HTML
LookUp(colStatusAtivo; Valor = ThisItem.status).Cor
LookUp(colSituacaoOper; Valor = ThisItem.situacao_operacional; Hex)

// Aeroportos que o usuário logado enxerga
Filter(colAerosValidos; varUsuario.aeroportos = "TODOS" Or IATA in varAerosPermitidos)
```

### Dentro do `HtmlViewer`

Todo cartão, chip e barra das telas é HTML — é o que dá acabamento sem empilhar dezenas de controles (menos
controle na tela = menos render = tela mais rápida). Duas regras que vêm das lições:

```powerfx
// Aspas simples nos atributos do HTML; as duplas ficam para o Power Fx
"<div style='" & htmlFonte & "color:" & hxTexto & ";'>" & ThisItem.modelo & "</div>"
```

- **Sem `<svg>` e sem emoji.** O sanitizador remove SVG e emoji faz a peça parecer amadora — hierarquia vem de
  peso, cor e chip de texto (`<span>` com `background`/`border-left`).
- **`<table>` em vez de flexbox** para colunatura: sobrevive ao sanitizador em qualquer cliente.
- **Cor sempre por token `hx*`.** `#` literal dentro de tela é regressão.

**Cuidado com `LookUp` repetido:** `LookUp` chamado 3 vezes na mesma fórmula = 3 avaliações por linha de galeria.
Envolver em `With({ _x: LookUp(...) }; ...)` e reusar `_x` — lição já registrada em
`LICOES_APRENDIDAS_POWERAPPS_YAML.md`.

---

## 5. `App.OnStart` e `App.StartScreen`

```powerfx
// App.StartScreen
scrLoginContexto
```

```powerfx
// App.OnStart — vazio de propósito.
```

**Por que o `OnStart` está vazio.** Tudo que roda no `OnStart` acontece com o app já aberto e a tela em branco:
o usuário olha para o nada enquanto 16 consultas voltam. A resolução do usuário e a carga do cache foram para o
`OnVisible` da `scrLoginContexto`, que mostra spinner, contagem e o motivo do bloqueio quando o e-mail não está
cadastrado. O `App.OnStart` não é onde se ganha performance — é onde se esconde a espera.

### O que a `scrLoginContexto` resolve (uma vez por sessão)

| Passo | Consultas ao SharePoint |
|---|---|
| `LookUp('tb_usuariosFrota'; email_usuario = User().Email And ativo = 1)` | 1 |
| `varAerosPermitidos` a partir de `colAerosValidos` | 0 — já está em memória |
| `colFiltroAero` (dropdown de aeroporto do usuário) | 0 |
| `colFrota` — cache da mestre, uma consulta **delegável por aeroporto** | 1 por aeroporto do perfil |

**O cache carrega 27 colunas, não 52.** Só o que o Módulo 1 lê. Os campos-espelho dos módulos que ainda não
existem (`doc_situacao`, `doc_proximo_vencimento`, `conforme_lado_ar`, `credencial_validade`,
`manut_proxima_data`) ficam **fora da projeção**: continuam existindo na lista SharePoint, esperando o módulo
dono, mas não trafegam, não são exibidos e não entram em conta nenhuma. Quando o módulo 4 entrar, é uma linha a
mais na projeção e um cartão a mais no painel.

As **cinco** projeções (login, RECARREGAR, ATUALIZAR do painel, ATUALIZAR da lista, gravação do formulário)
precisam ser **idênticas** — `Collect` numa coleção com esquema diferente falha. O `validar_telas.py` compara as
cinco e reprova divergência.

A projeção das colunas é feita com `ForAll(Filter(...) As _r, { ... })`, **não** com `ShowColumns("coluna")`:
em app com *Nomes de coluna como identificadores* ligado (padrão nos apps novos), nome de coluna em string não
compila — é erro de parsing e derruba a fórmula inteira. Mesmo motivo para `Sort(t; coluna; ordem)` no lugar de
`SortByColumns(t; "coluna"; ordem)`. Registrado em `LICOES_APRENDIDAS_POWERAPPS_YAML.md` (2026-08-25).

Depois disso, **painel, busca, filtros e detalhe não fazem consulta nenhuma**: rodam sobre `colFrota`.

### Por que cache da mestre, se a regra é "não copiar lista"

A regra do `LICOES_APRENDIDAS_POWERAPPS_YAML.md` vale para lista **transacional** — BDV, abastecimento, OS:
crescem sem teto e não cabem em memória. A mestre é diferente: é **um registro por ativo**, limitada pelo
tamanho físico da frota dos 16 aeroportos. Cachear é o que permite KPI, contagem por aeroporto e busca
instantânea sem `CountRows` sobre SharePoint — que não delega e devolveria número errado.

**Limite que precisa ser respeitado:** cada consulta traz no máximo o *limite de linhas de dados* do app
(padrão **500**). Suba para **2000** em Configurações → Geral → Limite de linhas de dados. Se um aeroporto
passar de 2000 ativos, o cache trunca em silêncio — por isso `varCacheTruncado` acende o aviso na tela de login.

### Variáveis globais que ficam de pé

| Variável | Onde nasce | Papel |
|---|---|---|
| `varUsuario` | `scrLoginContexto.OnVisible` | Registro de `tb_usuariosFrota` |
| `varAcessoLiberado` | idem | `false` = e-mail não cadastrado |
| `varAeroUser` | idem | Aeroporto padrão |
| `varPerfilNivel` | idem | 1 a 5, comparado sem `If` encadeado |
| `varAerosPermitidos` | idem | Tabela de aeroportos do perfil |
| `varCacheEm` / `varCacheTruncado` | idem | Hora da carga e aviso de truncamento |
| `varAtivoSel` | `scrFrotaLista` | Ativo aberto no painel de detalhe |
| `varOcupadoDesde` | `scrFrotaPainel` | Trava de reentrância do botão ATUALIZAR |

Variáveis de tela usam `locX` (`UpdateContext`) — `locDetalhe`, `locReset`, `locTotal`, `locMaxAero`.

---

## Checklist pós-colagem

0. Use o arquivo pronto **`App_Formulas_Frotas.txt`** — é este documento com as 54 definições já concatenadas,
   em pt-BR, sem `;;` na última. Copie o arquivo inteiro de uma vez.
1. Colar em **App → Formulas** (não no `OnStart`). **Confirme que não sobrou nenhum erro vermelho aqui antes de
   colar qualquer tela** — named formula faltando vira dezenas de erros nas telas, todos longe da causa.
2. Definir `App.StartScreen = scrLoginContexto`.
3. Conferir se `colAeros` retorna **17 linhas** (16 aeroportos + a linha vazia) e `colAerosValidos`, **16**.
4. Adicionar as fontes de dados `tb_ativosFrota` e `tb_usuariosFrota` antes de abrir a tela de login.
5. Configurações → Geral → **Limite de linhas de dados = 2000**.
6. Colar as telas na ordem `scrFrotaLista` → `scrFrotaPainel` → `scrLoginContexto`. Erro de `Navigate` para tela
   ainda inexistente some quando a última entrar.
7. Confirmar que nenhuma tela contém cor literal `RGBA(...)` ou `#` fora dos tokens.
7b. Colunas Sim/Não não existem nesta base: `circula_lado_ar`, `conforme_lado_ar` e `pode_baixar_ativo` são
   **Número**. Teste positivo é `= 1`, negativo é `<> 1`.
8. Testar com **limite de delegação = 1** (Configurações → Próximos recursos) — nenhum aviso deve aparecer nas
   consultas da carga, porque `ativo = 1` e `aeroporto = ...` delegam.
