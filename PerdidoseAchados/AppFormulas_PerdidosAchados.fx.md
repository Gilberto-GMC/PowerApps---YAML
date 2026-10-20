# App.Formulas — Airport Now / Perdidos e Achados

Migração do `App.OnStart` para fórmulas nomeadas (`App.Formulas`).

Data: 23/09/2026. Sintaxe em locale pt-BR (`;` separa argumentos, `;;` separa instruções).

## Por que

O `App.OnStart` atual bloqueia a abertura do app montando 16 registros de aeroporto, consultando a lista `User`, lendo `tbl_controle_versoes` e **baixando a foto do usuário no Office 365** — tudo antes da primeira tela aparecer.

Fórmulas nomeadas são declarativas e calculadas **sob demanda**: cada uma só é avaliada quando algum controle a lê. A foto, por exemplo, só vai ao conector se realmente for exibida. O `Concurrent` deixa de ser necessário, porque não existe mais ordem de execução a paralelizar.

## O que pode migrar e o que não pode

| Permanece no OnStart | Motivo |
|---|---|
| `varSessaoAtiva` | reatribuída em `ScreenHome` (Timer2) e `scrSessaoExpirada` |
| `varUltimaAtividade` | reatribuída 88 vezes nas telas |
| `varForcarExpiracao` | reatribuída em `ScreenHome` (Timer2) |

Fórmula nomeada é imutável — um `Set()` nela é erro de compilação. Todo o restante do OnStart é leitura derivada e pode migrar.

**Verificação feita antes da proposta:** nenhuma das variáveis migradas recebe `Set()` em nenhuma tela de nenhum módulo deste repositório, e `colAeros` é somente leitura em todos os usos (`Distinct`, `Filter`, `LookUp`, `AddColumns/SortByColumns`).

## Correção aplicada — identificação do usuário

O código original era:

```
Set(varIdUser; Coalesce(584; LookUp(User; usrNome = User().FullName).ID))
```

`Coalesce` devolve o primeiro argumento não vazio. `584` nunca é vazio, então o `LookUp` **jamais executava**: todo usuário que abria o app era identificado como o usuário 584, e `varNomeUser`, `varAeroUser`, `varPerfilUser` e `varAutUser` eram sempre os dele. Isso também explica por que a coluna `usuario` do cadastro gravava sempre o mesmo nome.

Era valor fixado para teste, conforme o comentário do próprio código (`// Value(Param("USUARIO"));//584; 589`). A versão abaixo restaura o comportamento previsto:

```
varIdUser =
Coalesce(
    IfError(Value(Param("USUARIO")); Blank());
    LookUp(User; usrNome = User().FullName).ID
);;
```

O `IfError` é defensivo: se o app for aberto sem o parâmetro (direto pelo Studio, ou fora do hub), `Value()` de um texto vazio pode devolver erro em vez de branco, e sem ele o `Coalesce` não cairia no `LookUp`. Com a proteção, a cadeia é: **parâmetro do hub → senão, usuário logado**.

### Impacto — testar antes de publicar

Esta correção muda quem o app acha que você é. Consequências diretas:

- `varAeroUser` / `varBlocoUser` passam a ser os reais → filtros de aeroporto nas telas mudam de resultado
- `varPerfilUser` (`Sede` / `Base`) controla se o usuário pode trocar de bloco/aeroporto no cadastro e na consulta
- `varAutUser` (`Admin`) libera a exclusão de itens
- `usuario` e `descarte_usuario` passam a gravar o nome de quem de fato operou

**Testar com pelo menos dois usuários, um `Sede` e um `Base`**, antes de publicar — é o cenário que a `AUDITORIA-TELAS.md` já recomenda no checklist.

### Para voltar a forçar um usuário em teste

Trocar temporariamente a primeira linha do `Coalesce`, sem apagar o resto:

```
varIdUser =
Coalesce(
    584;  // <<< APENAS TESTE - remover antes de publicar
    IfError(Value(Param("USUARIO")); Blank());
    LookUp(User; usrNome = User().FullName).ID
);;
```

## App.Formulas

> **Para colar no Studio use o [App_Formulas_PerdidosAchados.txt](App_Formulas_PerdidosAchados.txt)**,
> que e so o bloco abaixo, sem o markdown em volta. Ele e gerado por
> `node gerar_formulas_txt.mjs` — rode depois de qualquer mudanca aqui, senao os
> dois divergem. O script recusa gravar se houver parentese, chave ou aspa
> desbalanceada, ou definicao repetida.

```
// ===== Contexto de execução =====
varHub = Param("HUB");;

// ===== Aeroportos (tabela estática) =====
colAeros =
Table(
    {IATA: "GYN"; ICAO: "SBGO"; Bloco: "CENTRAL"; Aeroporto: "GOIÂNIA"; Cluster: "GOIÂNIA"};
    {IATA: "IMP"; ICAO: "SBIZ"; Bloco: "CENTRAL"; Aeroporto: "IMPERATRIZ"; Cluster: "GOIÂNIA"};
    {IATA: "PMW"; ICAO: "SBPJ"; Bloco: "CENTRAL"; Aeroporto: "PALMAS"; Cluster: "GOIÂNIA"};
    {IATA: "PLU"; ICAO: "SBBH"; Bloco: "CENTRAL"; Aeroporto: "PAMPULHA"; Cluster: "GOIÂNIA"};
    {IATA: "PNZ"; ICAO: "SBPL"; Bloco: "CENTRAL"; Aeroporto: "PETROLINA"; Cluster: "SÃO LUÍS"};
    {IATA: "SLZ"; ICAO: "SBSL"; Bloco: "CENTRAL"; Aeroporto: "SÃO LUIS"; Cluster: "SÃO LUÍS"};
    {IATA: "THE"; ICAO: "SBTE"; Bloco: "CENTRAL"; Aeroporto: "TERESINA"; Cluster: "SÃO LUÍS"};
    {IATA: "BFH"; ICAO: "SBBI"; Bloco: "SUL"; Aeroporto: "BACACHERI"; Cluster: "CURITIBA"};
    {IATA: "CWB"; ICAO: "SBCT"; Bloco: "SUL"; Aeroporto: "CURITIBA"; Cluster: "CURITIBA"};
    {IATA: "JOI"; ICAO: "SBJV"; Bloco: "SUL"; Aeroporto: "JOINVILLE"; Cluster: "CURITIBA"};
    {IATA: "NVT"; ICAO: "SBNF"; Bloco: "SUL"; Aeroporto: "NAVEGANTES"; Cluster: "CURITIBA"};
    {IATA: "BGX"; ICAO: "SBBG"; Bloco: "SUL"; Aeroporto: "BAGÉ"; Cluster: "FOZ DO IGUAÇU"};
    {IATA: "IGU"; ICAO: "SBFI"; Bloco: "SUL"; Aeroporto: "FOZ DO IGUAÇU"; Cluster: "FOZ DO IGUAÇU"};
    {IATA: "LDB"; ICAO: "SBLO"; Bloco: "SUL"; Aeroporto: "LONDRINA"; Cluster: "FOZ DO IGUAÇU"};
    {IATA: "PET"; ICAO: "SBPK"; Bloco: "SUL"; Aeroporto: "PELOTAS"; Cluster: "FOZ DO IGUAÇU"};
    {IATA: "URG"; ICAO: "SBUG"; Bloco: "SUL"; Aeroporto: "URUGUAIANA"; Cluster: "FOZ DO IGUAÇU"}
);;

// ===== Usuário =====
// Parâmetro vindo do hub; se ausente, cai no usuário logado.
varIdUser =
Coalesce(
    IfError(Value(Param("USUARIO")); Blank());
    LookUp(User; usrNome = User().FullName).ID
);;

varDadosUser = LookUp(User; ID = Value(varIdUser));;
varDadosAeroUser = LookUp(colAeros; Aeroporto = varDadosUser.Aeroporto);;

varNomeUser = varDadosUser.usrNome;;
varEmailUser = varDadosUser.Email;;
varFuncaoUser = varDadosUser.Funcao;;
varBlocoUser = varDadosUser.Bloco;;
varClusterUser = varDadosUser.Cluster;;
varAeroUser = varDadosUser.Aeroporto;;
varPerfilUser = varDadosUser.Perfil;;
varAutUser = varDadosUser.Autorizacao;;
varICAOUser = varDadosAeroUser.ICAO;;
varIATAUser = varDadosAeroUser.IATA;;

varFotoUser =
IfError(
    UsuáriosdoOffice365.UserPhoto(
        First(UsuáriosdoOffice365.SearchUser({searchTerm: varNomeUser})).Id
    );
    Blank()
);;

// ===== Versão do app =====
var_ultimaVersao =
Value(
    First(
        Sort(tbl_controle_versoes; ID; SortOrder.Descending)
    ).Numero_versao
);;
// ===== Design System ASUR Brasil — tokens =====
// Mesma fonte do projeto "Mapa de Alocacao" (AppFormulas_Mapa.fx.md, secao 7).
// Nenhuma tela deve declarar cor literal: trocar a marca = editar so este bloco.

// Hex — usados dentro do HTML dos HtmlViewer
hxPrimaria        = "#0A5A66";;   // verde-petroleo institucional ASUR
hxPrimariaEscura  = "#06424B";;
hxPrimariaClara   = "#E3F1F3";;
hxAcao            = "#007382";;   // teal de acao (botao primario do Mapa)
hxFundo           = "#F5F8F9";;
hxBorda           = "#B9D6DB";;
hxTexto           = "#1E293B";;
hxTextoFraco      = "#64748B";;
hxVerde           = "#15803D";;
hxAmbar           = "#B45309";;
hxVermelho        = "#B91C1C";;
hxTextoBarra      = "#D6DDE0";;   // texto sobre fundo escuro — nunca branco puro

// Cores dos controles nativos — derivadas dos hex acima, nunca redigitadas
thmPrimaria       = ColorValue(hxPrimaria);;
thmPrimariaEscura = ColorValue(hxPrimariaEscura);;
thmPrimariaClara  = ColorValue(hxPrimariaClara);;
thmAcao           = ColorValue(hxAcao);;
thmFundo          = ColorValue(hxFundo);;
thmBorda          = ColorValue(hxBorda);;
thmTexto          = ColorValue(hxTexto);;
thmTextoFraco     = ColorValue(hxTextoFraco);;
thmVerde          = ColorValue(hxVerde);;
thmAmbar          = ColorValue(hxAmbar);;
thmVermelho       = ColorValue(hxVermelho);;
thmTextoBarra     = ColorValue(hxTextoBarra);;


// ===== Destinacao final — PRO Perdidos e Achados Rev. 03 =====
// Plano em PLANO-DESTINACAO-FINAL.md. As tres listas abaixo sao as unicas
// fontes: tela nenhuma deve repetir categoria, motivo ou modalidade.

// Categorias que PODEM ser doadas. E a regra dos itens 5.13 e 5.16 do PRO
// (nada de eletronicos nem documentos), que ate 20/10/2026 vivia escrita a mao
// dentro da ScreenInventarioSeparar. Nao doavel = o que NAO esta aqui, entao
// categoria nova nasce fora da doacao ate alguem decidir o contrario.
colCatDoaveis =
Table(
    {Value: "Artigos religiosos"};
    {Value: "Artigos sexuais"};
    {Value: "Bagagem"};
    {Value: "Bebidas/Alimentos"};
    {Value: "Bijuterias/Joias"};
    {Value: "Cama, mesa e banho"};
    {Value: "Cortantes"};
    {Value: "Ferramenta"};
    {Value: "Fumígeno"};
    {Value: "Infantil"};
    {Value: "Itens esportivos"};
    {Value: "Itens médico"};
    {Value: "Objetos de arte"};
    {Value: "Óculos"};
    {Value: "Papelaria"};
    {Value: "Pessoais"};
    {Value: "Pet"};
    {Value: "Produtos de uso pessoal"};
    {Value: "Produtos químicos"};
    {Value: "Regionais"};
    {Value: "Souvenir"};
    {Value: "Veículo"};
    {Value: "Vestuário"}
);;

// Modalidades de destinacao final gravadas em dest_modalidade.
// O item 5.12 do PRO lista Devolucao ao Usuario, Doacao, Descarte e Destruicao.
// "Encaminhamento a Justica" e o termo que a operacao usa e que ja esta nas abas
// da ScreenInventario; no PRO ele aparece no 5.15 como "encaminhamento a orgao
// publico" e no 5.1.3 como Correios / Policia Federal / orgao competente.
colDestModalidades =
Table(
    {Value: "Destruição"};
    {Value: "Encaminhamento à Justiça"};
    {Value: "Descarte"}
);;

// Motivos — alineas "a" a "j" do item 5.11, mais a hipotese do 5.14.
// Aprovados pela Carmen Mamani Orosco em 09/10/2026.
// Cuidado com a alinea "c": em desembarque internacional o PRO manda confirmar
// a destinacao junto a ANVISA e ao VIGIAGRO.
colDestMotivos =
Table(
    {Value: "Roupas molhadas ou contaminadas"};
    {Value: "Peças íntimas"};
    {Value: "Alimentos e bebidas, abertos ou fechados"};
    {Value: "Medicamentos perecíveis ou com necessidade de refrigeração"};
    {Value: "Itens de higiene pessoal de uso individual"};
    {Value: "Almofadas de pescoço, tapa-olhos e travesseiros"};
    {Value: "Fones de ouvido descartáveis"};
    {Value: "Embalagens violadas"};
    {Value: "Produtos com prazo de validade vencido ou ilegível"};
    {Value: "Estado de conservação inadequado, odor forte ou contaminação aparente"};
    {Value: "Não apresenta condições de doação"}
);;

// Status do ciclo. Dois intermediarios porque o fluxo do item 5.15 tem duas maos
// diferentes: a Gerencia do Aeroporto aprova, o SGI Meio Ambiente executa.
stDestAprovacao   = "Aguardando aprovação";;
stDestDestinacao  = "Aguardando destinação";;

// Quem pode registrar destinacao final. A Carmen confirmou que o acesso e
// restrito, mas ainda nao disse a qual perfil (ponto 3 do e-mail de 09/10).
// Ate la vale o Admin, que ja e o precedente do app. TROCAR SO AQUI.
varPodeDestinar = varAutUser = "Admin";;

```

## App.OnStart — o que sobra

```
Set(varSessaoAtiva; true);;
Set(varUltimaAtividade; Now());;
Set(varForcarExpiracao; false)
```

## Limpezas que caem por consequência

- O `With` original calculava `dadosAero` refazendo `LookUp(User; ID = Value(varIdUser))` por dentro, em vez de reaproveitar o `dados` que já tinha em escopo — uma segunda consulta à mesma lista, sem necessidade. Aqui `varDadosAeroUser` parte de `varDadosUser`.
- `viewSafety: dados.View_safety` era declarado no `With` mas **nunca** entrava em nenhum `Set` — código morto. Não foi migrado. Se algum módulo ler um `varViewSafety`, ele nunca existiu de fato e estaria vazio.

## Cuidados na colagem

1. Confirmar que **Fórmulas nomeadas** está habilitado em Configurações → Próximos recursos, se o ambiente ainda pedir.
2. **Testar `varFotoUser` isoladamente primeiro.** É a única que chama conector, e imagem via conector em fórmula nomeada é o caso menos trivial. Se falhar, é a única que volta para o `OnStart` sem afetar as demais.
3. Os nomes foram mantidos idênticos aos das variáveis atuais **de propósito** — nenhuma tela precisa ser alterada. O prefixo `var` num nome que deixou de ser variável fica estranho, mas renomear exigiria mexer em todas as telas de todos os módulos.
4. **Escopo da verificação:** os usos foram validados contra os arquivos deste repositório (Perdidos e Achados, Mapa de Alocação, AVSEC, AirportNow 2.0). Como `User`, `tbl_controle_versoes` e `Param("HUB")` sugerem um shell compartilhado, fazer um Ctrl+F por `Set(varAeroUser`, `Set(varPerfilUser` e `Set(varNomeUser` no app completo antes de publicar.
