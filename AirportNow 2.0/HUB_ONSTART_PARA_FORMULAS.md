# Hub do AirportNow — o que sai do `OnStart` e vira `App.Formulas`

Regra que decide tudo: **fórmula nomeada é declaração, não ação.** Entra o que é sempre a mesma
coisa (constante, tabela fixa, consulta); fica no `OnStart` o que *acontece* (`Set` que muda depois,
`Launch`, `Navigate`) e o que alguém reescreve durante o uso.

Ganho principal: o que vira fórmula **não atrasa a abertura** — é calculado quando alguém usa, e só
na primeira vez. Hoje o hub resolve tudo isso antes de mostrar a primeira tela.

---

## 1. `App.Formulas` — pode colar

Dialeto pt-BR (`;` entre argumentos, `;;` entre declarações), igual ao `OnStart` atual.

```
// ====================== identidade do hub ======================
varHUB = "a5af3add-12da-4107-b027-23daea7b0056";;

// ID do usuário na lista User, vindo do hub que abriu este app. Sem parâmetro, 0.
varIdUser = Value(Param("USUARIO"));;

var_versao = 1667;;

// Largura do menu lateral — ele não recolhe, então é constante (confirmado em 19/10/2026).
var_sideBarWidth = 250;;

// Última versão publicada, direto da lista — era Set no OnStart.
var_ultimaVersao =
Value(
    First(
        Sort(
            tbl_controle_versoes;
            ID;
            SortOrder.Descending
        )
    ).Numero_versao
);;

// Histórico de versões, sempre atual.
col_historicoVersao =
Sort(
    tbl_controle_versoes;
    Numero_versao;
    SortOrder.Descending
);;

// ====================== rede de aeroportos ======================
// As duas linhas em branco são os separadores de bloco das listas suspensas — mantidas.
colAeros =
Table(
    { IATA: ""; ICAO: ""; Bloco: "CENTRAL"; Aeroporto: "" };
    { IATA: "GYN"; ICAO: "SBGO"; Bloco: "CENTRAL"; Aeroporto: "GOIÂNIA" };
    { IATA: "IMP"; ICAO: "SBIZ"; Bloco: "CENTRAL"; Aeroporto: "IMPERATRIZ" };
    { IATA: "PMW"; ICAO: "SBPJ"; Bloco: "CENTRAL"; Aeroporto: "PALMAS" };
    { IATA: "PLU"; ICAO: "SBBH"; Bloco: "CENTRAL"; Aeroporto: "PAMPULHA" };
    { IATA: "PNZ"; ICAO: "SBPL"; Bloco: "CENTRAL"; Aeroporto: "PETROLINA" };
    { IATA: "SLZ"; ICAO: "SBSL"; Bloco: "CENTRAL"; Aeroporto: "SÃO LUIS" };
    { IATA: "THE"; ICAO: "SBTE"; Bloco: "CENTRAL"; Aeroporto: "TERESINA" };
    { IATA: ""; ICAO: ""; Bloco: "SUL"; Aeroporto: "" };
    { IATA: "BFH"; ICAO: "SBBI"; Bloco: "SUL"; Aeroporto: "BACACHERI" };
    { IATA: "CWB"; ICAO: "SBCT"; Bloco: "SUL"; Aeroporto: "CURITIBA" };
    { IATA: "JOI"; ICAO: "SBJV"; Bloco: "SUL"; Aeroporto: "JOINVILLE" };
    { IATA: "NVT"; ICAO: "SBNF"; Bloco: "SUL"; Aeroporto: "NAVEGANTES" };
    { IATA: "BGX"; ICAO: "SBBG"; Bloco: "SUL"; Aeroporto: "BAGÉ" };
    { IATA: "IGU"; ICAO: "SBFI"; Bloco: "SUL"; Aeroporto: "FOZ DO IGUAÇU" };
    { IATA: "LDB"; ICAO: "SBLO"; Bloco: "SUL"; Aeroporto: "LONDRINA" };
    { IATA: "PET"; ICAO: "SBPK"; Bloco: "SUL"; Aeroporto: "PELOTAS" };
    { IATA: "URG"; ICAO: "SBUG"; Bloco: "SUL"; Aeroporto: "URUGUAIANA" }
);;

// ====================== usuário conectado ======================
// Era consultado duas vezes dentro do col_menu, uma para Root e outra para View_safety.
usrHub = LookUp(User; usrNome = User().FullName);;
usrEhRoot = Value(usrHub.Root) = 1;;
usrVeSafety = Value(usrHub.View_safety) = 1;;

// ====================== telas de navegação ======================
col_NavTelas =
Table(
    { Id: 26; TelaListar: '7.1.1-frmDesenbHibrid' };
    { Id: 27; TelaListar: '7.2-frmTestMotorres' };
    { Id: 32; TelaListar: '6.2-frmNaoAcomPaxListar' };
    { Id: 34; TelaListar: '12.1-frmImpObras' };
    { Id: 35; TelaListar: '11-frmPerdAcha' };
    { Id: 51; TelaListar: frmOcorrenciasGerais };
    { Id: 52; TelaListar: frmOcorrenciasGerais };
    { Id: 53; TelaListar: frmOcorrenciasGerais };
    { Id: 54; TelaListar: frmOcorrenciasGerais };
    { Id: 55; TelaListar: frmOcorrenciasGerais };
    { Id: 56; TelaListar: frmOcorrenciasGerais };
    { Id: 57; TelaListar: frmOcorrenciasGerais };
    { Id: 59; TelaListar: frmCheckListGenericoEQP };
    { Id: 63; TelaListar: frmFollowMe };
    { Id: 66; TelaListar: frmTesteBalizamento }
);;

// ====================== menu lateral ======================
col_menu =
Table(
    { Icon: Icon.Home; Nome: "Home"; Tela: Home };
    { Icon: Icon.Waffle; Nome: "Resumo Diário"; Tela: frmResumoDiario };
    If(usrEhRoot; { Icon: Icon.Settings; Nome: "Admin"; Tela: frmAdmin });
    { Icon: Icon.Airplane; Nome: "Pátios e Pistas"; Tela: frmPatiosPistas };
    { Icon: Icon.OfficeBuilding; Nome: "Terminal de Passageiros"; Tela: frmTerminalPassageiro };
    { Icon: Icon.Hospital; Nome: "Resposta emergência"; Tela: Home };
    { Icon: Icon.Lock; Nome: "AVSEC"; Tela: Home };
    If(usrVeSafety; { Icon: Icon.Warning; Nome: "Safety & Fauna"; Tela: Home });
    { Icon: Icon.GlobeWarning; Nome: "SGI"; Tela: Home };
    { Icon: Icon.Folder; Nome: "Lições Aprendidas"; Tela: Home };
    { Icon: Icon.Video; Nome: "Treinamentos"; Tela: Home };
    { Icon: Icon.Leave; Nome: "Sair"; Tela: Login }
);;
```

---

## 2. `OnStart` — o que sobra

```
If(
    IsBlank(Param("hidenavbar"));
    Launch(
        "https://apps.powerapps.com/play/e/default-d233d58a-9973-43a7-af69-6763630548a0/a/a5af3add-12da-4107-b027-23daea7b0056?tenantId=d233d58a-9973-43a7-af69-6763630548a0&hint=bfceed7a-bad1-47b6-874a-8cc49015d7f0&sourcetime=1752170432674&hidenavbar=true";
        {
            LOGADO: "z0x9c8v7b6n5" & Text(
                Now();
                "ddmmyyyy"
            ) & Rand() * 100;
            USUARIO: varIdUser
        };
        LaunchTarget.Replace
    )
);;
If(
    Host.OSType = "Windows";
    Set(
        var_adminEdit;
        false
    );;
    ClearCollect(
        col_menuModulos;
        tbl_Modulos
    )
);;
Set(
    varSessaoAtiva;
    true
);;
Set(
    varUltimaAtividade;
    Now()
);;
Set(
    varForcarExpiracao;
    false
)
```

---

## ⚠️ Revisão de 19/10/2026 — três voltaram para o OnStart

A primeira colagem deixou o menu lateral do Home vazio. A tela Home mostra por quê: os três são
reescritos durante o uso, e fórmula nomeada não se reescreve.

| o quê | a prova, na própria tela |
|---|---|
| `var_sideBarWidth` | `Icon11` (hambúrguer) faz `Set(var_sideBarWidth, 60)` — **o menu recolhe sim** |
| `col_historicoVersao` | `Icon17` faz `Clear(col_historicoVersao)` ao fechar o painel de versões |
| `col_menu` | o `menuLoad` do componente diz: *collect criada no select do botão de login*. E `Table()` com `If(cond; registro)` sem senão não engole a linha em branco como o `ClearCollect` engolia |

Os três voltaram ao `OnStart`. O `usrEhRoot` e o `usrVeSafety` continuam no `Formulas` e são usados
de lá pelo `col_menu`, então a dedução do `LookUp` repetido não se perdeu.

Lição: antes de mover um nome, procurar `Set(`, `ClearCollect(`, `Collect(` e `Clear(` dele em
**todas** as telas — não basta olhar o `OnStart`.

## 3. O que **não** pode virar fórmula, e por quê

| o quê | por quê fica |
|---|---|
| `Launch` do `hidenavbar` | é ação: reabre o app com a barra escondida |
| `varSessaoAtiva`, `varUltimaAtividade`, `varForcarExpiracao` | mudam o tempo todo — o `Timer` e cada clique reescrevem |
| `var_adminEdit` | é botão de liga/desliga da edição da index |
| `col_menuModulos` | ver a observação de delegação abaixo |

### `col_menuModulos`: dá para virar fórmula, mas eu não faria agora

`col_menuModulos = tbl_Modulos` funcionaria, e teria a vantagem de o cadastro feito no Admin
aparecer sem reabrir o app. O preço: as galerias fazem `Search(Sort(Filter(col_menuModulos; …)))`
com filtro em coluna de escolha, que **não delega** — hoje isso é inofensivo porque a coleção já
está na memória, mas contra a lista viva vira consulta ao SharePoint a cada tecla digitada na busca,
com o teto de 500 linhas por baixo.

Enquanto a lista de módulos for pequena, funciona; é uma troca consciente, não uma melhoria óbvia.
Deixei como `ClearCollect`.

---

## 4. Antes de colar — três conferências

1. **Nenhum `Set` pode sobrar com esses nomes.** Fórmula nomeada e variável não convivem: se alguma
   tela fizer `Set(varHUB; …)`, `Set(varIdUser; …)`, `Set(var_versao; …)`, `Set(var_ultimaVersao; …)`,
   `Set(var_sideBarWidth; …)`,
   `ClearCollect(colAeros; …)`, `ClearCollect(col_menu; …)`, `ClearCollect(col_NavTelas; …)` ou
   `ClearCollect(col_historicoVersao; …)`, o Studio recusa. Procure cada nome no app inteiro
   (Ctrl+F, "Pesquisar em todas as telas") antes de colar.
2. **Referência de tela dentro de tabela fixa** (`Tela: Home`, `TelaListar: frmOcorrenciasGerais`)
   não tem precedente no nosso repositório como fórmula nomeada. É o único item desta lista com
   risco real de o Studio recusar. Cole `col_NavTelas` e `col_menu` **por último e separados**: se
   recusar, esses dois voltam para o `OnStart` e o resto continua valendo.
3. **`var_versao` e `var_ultimaVersao`** passam a ser lidos direto da lista. Confirme que ninguém
   escreve neles no fluxo de publicação de versão.

---

## 5. Dois defeitos que apareceram na leitura

**O histórico de versões nunca é carregado.** No `OnStart` está:

```
If(
    CountRows(col_historicoVersao) > 0;
    ClearCollect(col_historicoVersao; …)
)
```

Ele só preenche a coleção **se ela já estiver preenchida** — e na abertura ela está vazia, então
nunca entra. Como fórmula nomeada o problema desaparece sozinho, porque não há mais carga: a
consulta é o próprio `col_historicoVersao`. Se preferir manter no `OnStart`, a condição certa é
`CountRows(col_historicoVersao) = 0`.

**O mesmo `LookUp(User; …)` roda duas vezes** dentro do `col_menu`, uma para `Root` e outra para
`View_safety`. Virou `usrHub`, consultado uma vez. E vale notar: esse `LookUp` compara
`usrNome = User().FullName` — nome de pessoa como chave. Homônimo e mudança de nome quebram calados.
O Mapa usa o **e-mail** pela mesma razão (`usrMapa` no `App_Formulas_Mapa.txt`). Não mexi, mas fica
registrado.
