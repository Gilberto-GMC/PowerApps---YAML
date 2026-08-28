# `App.Formulas` — Mapa de Alocação de Pátio (Motiva Aeroportos)

Camada de dados de referência e tokens de tema do app **Motiva — Mapa de Alocação de Pátio**.

Documentos irmãos:
[ARQUITETURA_MAPA.md](ARQUITETURA_MAPA.md) (decisões e estratégia de coleções) ·
[ESTRUTURA_LISTA_MAPA.md](ESTRUTURA_LISTA_MAPA.md) (criação da lista)

> **Locale:** este arquivo vai colado na **barra de fórmulas** do Power Apps Studio (propriedade `Formulas` do
> objeto `App`), portanto está em **pt-BR**: `;` separa argumentos, `;;` termina cada definição, decimal com
> vírgula. Os arquivos `.pa.yaml` das telas continuam em formato **invariante** (`,` e `.`) — não misture os dois.

> **Como colar:** Studio → árvore de objetos → selecionar **App** → propriedade **Formulas** → colar tudo.
> Não é o `OnStart`. Use o arquivo pronto [App_Formulas_Mapa.txt](App_Formulas_Mapa.txt).

---

## Por que named formula e não `ClearCollect` no `OnStart`

| | `ClearCollect` no `OnStart` | Named formula (adotado) |
|---|---|---|
| Custo na abertura do app | Executa sempre, mesmo que a tela não use | Zero — só calcula quando alguém lê |
| Leitura no app | `Filter(colPosicoes; ...)` | **Idêntica** |
| Alterável em runtime | Sim | Não (é constante) |

São **38 registros estáticos** somados. Como lista SharePoint seriam quatro conexões e quatro chamadas de rede
na abertura do app; como named formula não custam nada e não precisam de tela de cadastro, índice nem view.

**Isolamento:** nenhuma tela lê a origem diretamente — todas leem `colPatios`, `colPosicoes`, `colPortoes` e
`colCias`. Se um dia o operador precisar cadastrar posição sem republicar, cada uma vira lista trocando **só a
definição aqui**; as telas não mudam uma linha.

O cache do dia (`colDia`) e a grade derivada (`colGrade`) são outro assunto — são coleções de verdade,
montadas na tela. Ver seção 6.

---

## 1. Aeroportos

Só entra aeroporto que tem posições mapeadas em `colPosicoes`. Ao incluir um novo, acrescente aqui **e** lá.

```powerfx
// ✈️ Aeroportos com mapa de pátio publicado
colAerosMapa =
Table(
    { ICAO: "SBNF"; IATA: "NVT"; Aeroporto: "NAVEGANTES" }
);;
```

---

## 2. Pátios

```powerfx
// 🅿️ Pátios — a ordem manda no agrupamento visual da grade
colPatios =
Table(
    { patio: "PRINCIPAL";  nome_patio: "PÁTIO PRINCIPAL"; ordem: 1 };
    { patio: "PATIO23";    nome_patio: "PÁTIO 2 / 3";     ordem: 2 };
    { patio: "HELIPONTOS"; nome_patio: "HELIPONTOS";      ordem: 3 }
);;
```

---

## 3. Posições

As 25 posições do SBNF **na ordem visual exata da planilha** (`Mapa de Alocação - 2026.xlsx`, linhas 3 a 41):
`T1`…`T7`, depois `A6` `7` `A10` `A7` `A8` `8` `A9` `A5` `6A` `A1` `A2` `A3` `6B` `A4`, depois `H1`…`H4`.

> ⚠️ **`id` é identificador estável.** É ele que vai gravado em `id_posicao` na lista `tb_alocacoesMapa`.
> **Nunca reordene nem reaproveite um `id`** — quem muda quando o desenho do pátio muda é a coluna `ordem`.
> Aposentar uma posição = remover da tabela; os registros antigos expiram sozinhos no expurgo.

> **`env_max: 0` em todas as posições — validação de envergadura desligada por decisão da operação
> (28/08/2026).** A planilha registra a classe A/B do pátio 2/3 por cor, não por metragem, e ninguém tem os
> números. Com `0`, a regra 6 do `btnSalvarMap` simplesmente não dispara: o campo *Envergadura* continua no
> formulário e continua sendo gravado, só não bloqueia nada.
>
> **Para ligar depois**, basta preencher `env_max` das posições que se quiser proteger — nenhuma tela muda. A
> referência para o pátio principal, se um dia for útil, é a aeronave da coluna B da planilha: B-738 = 35,79 m e
> EMB. E-2 = 35,1 m. A restrição continua **visível** no rótulo de cada linha da grade (`aeronave_max`), que é
> como o operador já lê hoje.

```powerfx
// 🛩️ Posições do pátio — ordem visual idêntica à planilha
colPosicoes =
Table(
    { id: 1;  patio: "PRINCIPAL";  posicao: "T1";  ordem: 1;  aeronave_max: "B-738";    classe: "";            env_max: 0; tipo: "PONTE";     contingencia: 0 };
    { id: 2;  patio: "PRINCIPAL";  posicao: "T2";  ordem: 2;  aeronave_max: "EMB. E-2"; classe: "";            env_max: 0; tipo: "PONTE";     contingencia: 0 };
    { id: 3;  patio: "PRINCIPAL";  posicao: "T3";  ordem: 3;  aeronave_max: "EMB. E-2"; classe: "";            env_max: 0; tipo: "PONTE";     contingencia: 1 };
    { id: 4;  patio: "PRINCIPAL";  posicao: "T4";  ordem: 4;  aeronave_max: "B-738";    classe: "";            env_max: 0; tipo: "PONTE";     contingencia: 0 };
    { id: 5;  patio: "PRINCIPAL";  posicao: "T5";  ordem: 5;  aeronave_max: "B-738";    classe: "";            env_max: 0; tipo: "PONTE";     contingencia: 0 };
    { id: 6;  patio: "PRINCIPAL";  posicao: "T6";  ordem: 6;  aeronave_max: "B-738";    classe: "";            env_max: 0; tipo: "PONTE";     contingencia: 0 };
    { id: 7;  patio: "PRINCIPAL";  posicao: "T7";  ordem: 7;  aeronave_max: "B-738";    classe: "";            env_max: 0; tipo: "PONTE";     contingencia: 0 };
    { id: 8;  patio: "PATIO23";    posicao: "A6";  ordem: 8;  aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 9;  patio: "PATIO23";    posicao: "7";   ordem: 9;  aeronave_max: "";         classe: "B";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 10; patio: "PATIO23";    posicao: "A10"; ordem: 10; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 11; patio: "PATIO23";    posicao: "A7";  ordem: 11; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 12; patio: "PATIO23";    posicao: "A8";  ordem: 12; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 13; patio: "PATIO23";    posicao: "8";   ordem: 13; aeronave_max: "";         classe: "B";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 14; patio: "PATIO23";    posicao: "A9";  ordem: 14; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 15; patio: "PATIO23";    posicao: "A5";  ordem: 15; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 16; patio: "PATIO23";    posicao: "6A";  ordem: 16; aeronave_max: "";         classe: "B";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 17; patio: "PATIO23";    posicao: "A1";  ordem: 17; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 18; patio: "PATIO23";    posicao: "A2";  ordem: 18; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 19; patio: "PATIO23";    posicao: "A3";  ordem: 19; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 20; patio: "PATIO23";    posicao: "6B";  ordem: 20; aeronave_max: "";         classe: "B";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 21; patio: "PATIO23";    posicao: "A4";  ordem: 21; aeronave_max: "";         classe: "A";           env_max: 0; tipo: "REMOTA";    contingencia: 0 };
    { id: 22; patio: "HELIPONTOS"; posicao: "H1";  ordem: 22; aeronave_max: "";         classe: "HELICOPTERO"; env_max: 0; tipo: "HELIPONTO"; contingencia: 0 };
    { id: 23; patio: "HELIPONTOS"; posicao: "H2";  ordem: 23; aeronave_max: "";         classe: "HELICOPTERO"; env_max: 0; tipo: "HELIPONTO"; contingencia: 0 };
    { id: 24; patio: "HELIPONTOS"; posicao: "H3";  ordem: 24; aeronave_max: "";         classe: "HELICOPTERO"; env_max: 0; tipo: "HELIPONTO"; contingencia: 0 };
    { id: 25; patio: "HELIPONTOS"; posicao: "H4";  ordem: 25; aeronave_max: "";         classe: "HELICOPTERO"; env_max: 0; tipo: "HELIPONTO"; contingencia: 0 }
);;
```

---

## 4. Portões — a cor do **contorno** do bloco

As cinco cores saíram das bordas dos retângulos da planilha (`<a:ln>` dos shapes do `drawing47.xml`).

**O portão 4 é evidência, não palpite.** Na gravação de 28/08/2026 o Douglas diz: *"essa aeronave que vai chegar
às 10 horas, da GOL 1214 e sai 1217, vai ser estacionada no tango 4 e vai utilizar o portão 4"*. Na aba
`SEX 28.08` esse bloco está na linha 9 (T4), das 10:00 às 11:40, com contorno `#FF0066`. Logo `#FF0066` = **4**.

Os outros quatro foram numerados por convenção, do frio para o quente, para que a legenda se leia como uma
progressão: ciano → verde → amarelo → rosa → vermelho. Se a operação disser outra ordem, é trocar só a coluna
`portao` desta tabela — nenhuma outra linha do sistema muda, porque a lista guarda o **número**, não a cor.

> ⚠️ **Duas variantes de vermelho na planilha.** Os contornos aparecem como `#FF0000` e `#F22727` — é a mesma
> intenção, com a deriva natural de quem escolhe a cor à mão a cada caixa. No app existe um vermelho só. Ao
> transcrever os dias antigos, as duas viram portão 5.

```powerfx
// 🚪 Portões da sala de embarque — cor do contorno do bloco
// 1 ciano · 2 verde · 3 amarelo · 4 rosa (confirmado na gravação) · 5 vermelho
colPortoes =
Table(
    { portao: "1"; cor_hex: "#00FFFF"; ordem: 1 };
    { portao: "2"; cor_hex: "#00B050"; ordem: 2 };
    { portao: "3"; cor_hex: "#FFFF00"; ordem: 3 };
    { portao: "4"; cor_hex: "#FF0066"; ordem: 4 };
    { portao: "5"; cor_hex: "#FF0000"; ordem: 5 }
);;
```

---

## 5. Companhias — a cor do **preenchimento** do bloco

`cor_hex` veio do preenchimento dos retângulos da planilha. `cor_texto` é escolhida por contraste: sobre o azul
escuro da Azul, texto claro `#D6DDE0` (nunca branco puro); sobre os demais, o texto padrão `#1E293B`.

```powerfx
// 🎫 Companhias aéreas — cor do preenchimento do bloco
colCias =
Table(
    { sigla: "GLO"; nome_cia: "GOL";      cor_hex: "#FFC000"; cor_texto: "#1E293B"; ordem: 1 };
    { sigla: "AZU"; nome_cia: "AZUL";     cor_hex: "#1F497D"; cor_texto: "#D6DDE0"; ordem: 2 };
    { sigla: "TAM"; nome_cia: "LATAM";    cor_hex: "#FF99CC"; cor_texto: "#1E293B"; ordem: 3 };
    { sigla: "ONE"; nome_cia: "ONE";      cor_hex: "#C9C5E6"; cor_texto: "#1E293B"; ordem: 4 };
    { sigla: "FAB"; nome_cia: "FAB";      cor_hex: "#92D050"; cor_texto: "#1E293B"; ordem: 5 };
    { sigla: "GER"; nome_cia: "AV. GERAL"; cor_hex: "#E2E8F0"; cor_texto: "#1E293B"; ordem: 6 }
);;
```

`GER` é o rótulo da aviação geral e do cargueiro do pátio 2/3, que na planilha aparecem só como prefixo digitado
na célula. No app, esses registros levam `cia_sigla: "GER"` e o prefixo em `prefixo`.

---

## 6. Enumerações e constantes da grade

```powerfx
// 🗂️ Tipos de registro — enumeração local, gravada como Texto na lista
colTiposReg =
Table(
    { tipo: "VOO";        rotulo: "Voo" };
    { tipo: "INTERDICAO"; rotulo: "Interdição" };
    { tipo: "RESERVA";    rotulo: "Reserva" }
);;

// 🔽 Tabelas dos seletores — coluna única `Value`, que é o que o Dropdown moderno exibe.
// Derivadas das tabelas acima: uma fonte de verdade, sem redigitar nada.
colAerosSel =
ForAll(colAerosMapa As _a; { Value: _a.ICAO });;

colTiposSel =
ForAll(colTiposReg As _t; { Value: _t.rotulo });;

colPosicoesSel =
ForAll(Sort(colPosicoes; ordem; SortOrder.Ascending) As _p; { Value: _p.posicao });;

colCiasSel =
Ungroup(
    Table(
        { _s: Table({ Value: "—" }) };
        { _s: ForAll(Sort(colCias; ordem; SortOrder.Ascending) As _c; { Value: _c.sigla }) }
    );
    "_s"
);;

colPortoesSel =
Ungroup(
    Table(
        { _s: Table({ Value: "—" }) };
        { _s: ForAll(Sort(colPortoes; ordem; SortOrder.Ascending) As _p; { Value: _p.portao }) }
    );
    "_s"
);;

colPatiosSel =
Ungroup(
    Table(
        { _s: Table({ Value: "TODOS OS PÁTIOS" }) };
        { _s: ForAll(Sort(colPatios; ordem; SortOrder.Ascending) As _p; { Value: _p.nome_patio }) }
    );
    "_s"
);;

// 🕐 Régua do dia — 24 horas cheias
colHoras = ForAll(Sequence(24; 0) As _h; { hora: _h.Value });;

// 📏 Constantes da grade
mapMinutosDia   = 1440;;   // minutos de um dia — denominador de toda largura em %
mapLarguraRotulo = 132;;   // px da coluna de rótulo, à esquerda do trilho
mapAlturaLinha   = 56;;    // px de cada linha da grade
mapSyncSegundos  = 60;;    // intervalo do verificador de alteração de outros usuários
mapTravaSegundos = 30;;    // validade da trava de reentrância do botão salvar
```

> **Por que os seletores são de coluna única.** O Dropdown moderno (`DropDown@0.0.45`) exibe a coluna da tabela
> que recebe em `Items` e devolve o registro escolhido em `.Selected.Value`. Passando `{ Value: ... }` o rótulo
> exibido fica explícito e a leitura na tela é sempre `drpX.Selected.Value` — o mesmo padrão já usado no app de
> Frotas. O código correspondente volta por `LookUp` na tabela de origem, em memória.
>
> `"—"` é o rótulo de *sem companhia* e *sem portão*: a tela grava `""` quando o usuário deixa esse valor.

---

## 7. Design System Motiva — tokens

Duas famílias, uma fonte de cor: `hx*` (string hex, usada dentro do HTML dos `HtmlViewer`) e `thm*` (cor de
controle nativo, derivada por `ColorValue`). Nenhuma tela declara cor literal.

```powerfx
// 🎨 Hex — usados dentro do HTML dos HtmlViewer
hxPrimaria        = "#391694";;   // roxo institucional Motiva
hxPrimariaEscura  = "#2A106E";;
hxPrimariaClara   = "#EDE9FB";;
hxAcao            = "#DD511A";;   // laranja de ação
hxOperacional     = "#0891B2";;
hxSuperficie      = "#FFFFFF";;
hxFundo           = "#F8FAFC";;   // slate claro
hxBorda           = "#C9C5E6";;   // borda institucional clara
hxTexto           = "#1E293B";;
hxTextoFraco      = "#64748B";;
hxVerde           = "#15803D";;
hxAmbar           = "#B45309";;
hxVermelho        = "#B91C1C";;
hxVermelhoSuave   = "#FEF2F2";;
hxAmbarSuave      = "#FFFBEB";;
hxGradeLinha      = "#E2E8F0";;   // linha vertical de hora no trilho
hxTextoBarra      = "#D6DDE0";;   // texto sobre fundo escuro — nunca branco puro
hxBordaBarra      = "rgba(214,221,224,.28)";;
hxBotaoBarra      = "#BDB2B0";;

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

// 🔤 Tipografia — Sora é a fonte da marca, mas não existe no Power Apps e o sanitizador do
// HtmlViewer não carrega webfont. Segoe UI é a substituta e está em todos os clientes.
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

> **Texto sobre fundo escuro é `hxTextoBarra` (#D6DDE0), nunca branco puro.** Vale para a barra roxa, o trilho
> lateral e todo botão de fundo roxo: `Color: =thmTextoBarra` no `HtmlViewer`, `FontColor: =thmTextoBarra` no
> `Button`. O `validar_telas_mapa.py` reprova branco literal e controle claro faltando.

**O cromatismo dentro da grade é exceção declarada:** as cores dos blocos vêm de `colCias` e `colPortoes`, não
dos tokens, porque reproduzem o Excel que o operador já lê de relance. Continuam fora do `.pa.yaml` — a tela lê
`ThisItem.cor_hex`, nunca um literal.

---

## 8. Como as telas consomem

```powerfx
// dropdown de posições de um pátio
Sort(Filter(colPosicoes; patio = locPatio); ordem; SortOrder.Ascending)

// cor de preenchimento de um bloco
LookUp(colCias As _c; _c.sigla = ThisItem.cia).cor_hex

// contadores da barra — sobre a COLEÇÃO, nunca sobre a lista
CountRows(colDia)
```

**Proibido:** `LookUp`, `Filter` ou `First(Sort(...))` sobre `tb_alocacoesMapa` dentro de template de galeria —
é uma consulta por linha por render. Todo cruzamento é resolvido na montagem de `colGrade`.

---

## 9. `App.OnStart` e `App.StartScreen`

```powerfx
// App.StartScreen
scrMapaInicio
```

```powerfx
// App.OnStart — vazio de propósito.
```

Tudo que roda no `OnStart` acontece com o app já aberto e a tela em branco na frente do usuário. A resolução do
usuário, a permissão de edição e a carga do dia foram para o `OnVisible` da `scrMapaInicio`, que mostra spinner,
contagem e o motivo do bloqueio.

---

## Checklist pós-colagem

- [ ] Colar [App_Formulas_Mapa.txt](App_Formulas_Mapa.txt) em **App → Formulas** (não no `OnStart`) e confirmar
      **zero erro vermelho** antes de abrir qualquer tela.
- [ ] Conferir as contagens: `colPosicoes` = **25**, `colPortoes` = **5**, `colCias` = **6**, `colPatios` = **3**.
- [ ] Definir `App.StartScreen = scrMapaInicio`.
- [ ] Adicionar a fonte de dados `tb_alocacoesMapa` — é a única.
- [ ] Configurações → Geral → **Limite de linhas de dados = 2000**.
- [ ] Colar as telas na ordem `scrMapaReferencia` → `scrMapaPatio` → `scrMapaInicio` (resolve os `Navigate`).
- [ ] Conferir que nenhuma tela contém `RGBA(` ou `#` literal.
- [ ] Confirmar com a operação a correspondência **cor ↔ número do portão** (seção 4) e as envergaduras (seção 3).
