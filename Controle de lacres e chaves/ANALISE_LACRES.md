# Controle de Lacres — inconsistências e o que quebra ao crescer

Análise sobre `ScreenHome`, `scrPontoLacravelForm` e `ScreenOperaçãoLacres_new`, mais o `App.OnStart`.
Escrita em 08/09/2026, depois de aplicar as correções de exclusão de ponto lacrável.

---

## 1. O relógio: delegação na `tbl_Lacres_Aplicacao`

Este é o único item da lista que **não** se resolve com código. Vale ler primeiro.

O SharePoint só entrega ao app as primeiras 500 linhas (2.000 se você subir o limite nas
configurações). Consulta que o servidor não consegue executar sozinha é resolvida **em cima dessa
fatia** — e o Power Apps não avisa. Não dá erro: dá número menor.

Antes da correção de hoje, a tela de operações era não-delegável inteira. Agora as duas consultas
que ela faz são delegáveis:

| Coleção | Consulta | Delegável? |
|---|---|---|
| `col_ponto_lacravel` | `Excluido = false && Aeroporto = ...` | Sim |
| `col_aplicacao_bruta` | `Aeroporto = ...` | Sim |

Delegável significa que o *filtro* roda no servidor. Mas o **resultado** ainda precisa caber na
fatia. E é aqui que está o relógio: `col_aplicacao_bruta` traz **todas as aplicações e rompimentos
já registrados naquele aeroporto**, desde sempre. Essa lista só cresce.

### Com os seus números, isso não é urgente

Douglas informou em 08/09/2026: **20 a 30 pontos lacráveis no CWB**, o maior da rede, e
**rompimentos mensais na casa da metade disso ou menos** — digamos 10 a 15 por mês.

Cada aplicação é um registro; o rompimento é gravado *dentro* do registro da aplicação, não cria
um novo. Quem cria registro é a **relacragem**. Então:

```
15 relacragens/mês × 12 = ~180 registros por ano, por aeroporto
```

| Limite de linhas do app | Quando a conta estoura |
|---|---|
| 500 (padrão) | ~3 anos |
| 2.000 | ~11 anos |

**Conclusão: subir o limite para 2.000 resolve por uma década.** É uma configuração do app, não
custa colagem de tela. Faça isso e o assunto está encerrado por muito tempo.

Isso corrige o que eu te disse antes. Eu tinha estimado 50 a 200 pontos e alertado que o limite
chegaria em meses; com 20 a 30 pontos a ordem de grandeza é outra, e a reengenharia que eu ia
recomendar **não se justifica agora**.

Um cuidado que continua valendo: a consulta traz todas as aplicações **do aeroporto selecionado**.
Se algum dia o filtro de aeroporto ficar em branco, ela passa a trazer os 16 aeroportos de uma vez
e a conta acima é multiplicada por 16. Hoje isso não acontece — o `ComboboxCanvasAeroporto_2` tem
`Default: =varAeroUser`, e o botão de limpar faz `Reset`, que volta ao mesmo padrão. Só vale saber
que o "todos os aeroportos" existe como caminho no código.

### Se um dia precisar (não precisa agora)

1. **Trazer só uma janela de tempo.** Filtrar `col_aplicacao_bruta` pelos últimos N meses. Barato,
   mas tem um furo: o último movimento de um ponto pouco mexido pode ser mais antigo que a janela,
   e aí o ponto aparece como "sem lacre" tendo lacre. Só serve com um resgate para esses casos.

2. **Gravar o resumo no próprio ponto.** É a solução estrutural, e sairia quase de graça porque o
   `OnSuccess` dos dois formulários **já faz `Patch` no ponto** para atualizar o `Status`. Bastaria
   gravar junto o que o cartão mostra:

   ```
   Patch(tbl_Pontos_Lacraveis, <o ponto>, {
       Status: "Ativo",
       Ultimo_Lacre: <numero>,
       Ultima_Data: <data>,
       Ultimo_Responsavel: <nome>,
       ID_Ultima_Aplicacao: <id>
   })
   ```

   A tela de operações passaria a precisar de **uma** consulta — os pontos — e nunca mais tocaria na
   `tbl_Lacres_Aplicacao`. Aí ela fica imune ao crescimento: o número de pontos lacráveis de um
   aeroporto é estável, e o histórico pode crescer sem limite sem afetar a tela.

   O preço é o preço de todo dado repetido: se um `Patch` falhar, o resumo no ponto e o histórico
   divergem. Mas essa exposição **já existe hoje** para o `Status`, que é gravado no mesmo lugar.

**Recomendação:** subir o limite para 2.000 e parar por aí. Guardar esta seção para quando a rede
crescer muito ou algum aeroporto mudar de patamar de movimento.

---

## 2. ✅ `ComboboxCanvasAeroporto_9` — referências órfãs, corrigido em 08/09/2026

O controle **não existe**. Douglas confirmou: o seletor de aeroporto é o `_2` na tela de operações e
o `_8` no cadastro. As três referências eram herança de cópia, apontando para um controle apagado.

| Onde | Era | Ficou |
|---|---|---|
| `ComboboxPontos_2.Items` (form de rompimento) | `Filter(tbl_Pontos_Lacraveis, Aeroporto = _9.Selected.Aeroporto)` | `col_ponto_lacravel` |
| `ComboboxPontos_3.Items` (form de aplicação) | idem | `col_ponto_lacravel` |
| `DataCardValue39_1.Default` (campo Aeroporto) | `Coalesce(Parent.Default, _9.Selected.Aeroporto)` | `Coalesce(Parent.Default, ComboboxCanvasAeroporto_2.Selected.Value)` |

Os `DefaultSelectedItems` das duas combos também passaram a ler `col_ponto_lacravel`, e a casar por
`ID = var_AplicaLacres_dados.ID_Ponto` — número com número. Antes era
`ID = ...ID_Ponto_Lacravel`, que compara número com texto e depende de coerção.

**Por que isso nunca apareceu como defeito:** `DefaultSelectedItems` já traz o ponto do cartão que o
operador clicou. A combo abre com o ponto certo escolhido, e a lista quebrada só apareceria se
alguém abrisse o dropdown para **trocar** de ponto — que é justamente o que ninguém faz, porque o
ponto veio do cartão. O defeito estava escondido atrás do caminho feliz.

Ganho de tabela: como `col_ponto_lacravel` já exclui os pontos inativados, deixou de ser possível
aplicar lacre em ponto excluído.

---

## 3. ✅ Sobras do módulo de Chaves — removidas em 08/09/2026

Todas saíram: os dois botões **Extravios** (controles apagados, não escondidos), o `ClearCollect` de
`col_chave_especifico` a partir de `tb_local_especifico`, os dois blocos comentados de `col_chave`, e
o rodapé que dizia "N Chaves". `grep` por `col_chave|tbl_chave|tb_local_especifico|Extravio` nas três
telas: zero ocorrências. O texto abaixo fica como registro do que era.

### O que era

O submódulo nasceu por cópia, e vieram junto:

| Onde | O quê |
|---|---|
| `ScreenOperaçãoLacres_new` `ButtonCanvas12_19` | Botão **Extravios**: `LookUp(tbl_chave_extravio, id_chave = ThisItem.ID)` comparando id de chave com id de **aplicação de lacre**. Navega para `ScreenHistoricoExtravio` passando `var_chave_dados` |
| `scrPontoLacravelForm` `ButtonCanvas12_9` | O mesmo botão, agora comparando id de chave com id de **ponto lacrável** |
| `scrPontoLacravelForm` `ComboboxCanvasAeroporto_8.OnChange` | `ClearCollect(col_chave_especifico, ...tb_local_especifico...)` — coleção de chaves, montada toda vez que se troca de aeroporto na tela de lacres |
| `scrPontoLacravelForm` `TextCanvas4_2` | Rodapé escrito `"Quantidade de registros: " & ... & " Chaves"` |
| `GalleryLocal_5.Items` | Bloco comentado grande, do filtro de `col_chave` |

Nenhuma dessas comparações pode dar certo — são entidades diferentes. O botão Extravios ou nunca
aparece, ou aparece na linha errada por coincidência de ID. E as duas primeiras custam **um `LookUp`
remoto por linha visível da galeria**, refeito a cada rolagem.

Não mexi em nada disso: apagar controle é mudança visível e é decisão sua. Se quiser, tiro os dois
botões e a coleção numa passada só.

---

## 4. ✅ Filtro de aeroporto do histórico — resolvido em 08/09/2026

**Decisão do Douglas: o controle do aeroporto é sempre o do painel.** A `GalleryLocal_5` passou a
filtrar por `ComboboxCanvasAeroporto_2.Selected.Value`, o `Label10_76` passou a ler
`col_ponto_lacravel` (local, sem consulta remota por linha), e os dois dropdowns próprios do
histórico — `ComboboxCanvasBloco_13` e `ComboboxCanvasAeroporto_11` — foram **escondidos** junto com
seus containers, porque não controlavam mais nada. O botão-borracha do histórico agora só limpa a
busca por texto.

Escondidos e não apagados de propósito: se algum dia o histórico precisar de filtro próprio, o
controle está lá. Se depois de rodar um tempo ninguém sentir falta, dá para apagar de vez.

### O problema que isso resolveu

Na `GalleryLocal_5` (histórico de rompimentos), dois rótulos vizinhos buscam a mesma coisa em
lugares diferentes:

```
Label10_76:  LookUp(tbl_Pontos_Lacraveis, ID = Value(ThisItem.ID_Ponto_Lacravel), Localizacao)
Label10_78:  LookUp(col_ponto_lacravel, Value(ID) = Value(ThisItem.ID_Ponto_Lacravel), Porta_Emergencia_ARS.Value)
```

A galeria é filtrada pelo `ComboboxCanvasAeroporto_11`. A coleção `col_ponto_lacravel` é montada a
partir do `ComboboxCanvasAeroporto_2`. Os dois dropdowns são independentes — o `_11` chama
`Select(ButtonCanvas7_15)` no `OnChange`, não o `ButtonAtualizar_2`.

Então: troque o aeroporto no histórico sem trocar no painel, e a coluna
**Porta de Emergência ARS fica em branco** — justamente a coluna que a RFB olha.

Foi por isso que eu **não** troquei o `Label10_76` para a coleção local, apesar de ser a correção
óbvia de performance. Antes de otimizar essa galeria é preciso decidir se ela deve ter filtro de
aeroporto próprio ou seguir o do painel. **Qual dos dois?** Com a resposta, arrumo os dois rótulos e
a galeria de uma vez.

---

## 5. ✅ `OnFailure` — adicionado em 08/09/2026

Os **três** formulários ganharam `OnFailure` com `Notify` de erro, no padrão do workspace
(`Coalesce(<Form>.Error, "…")`, `NotificationType.Error`, 5000 ms). E os `Patch` de `Status` dentro
dos `OnSuccess` foram embrulhados em `IfError`, com mensagem que diz exatamente o que ficou
inconsistente: *"o lacre foi gravado, mas o status do ponto não foi atualizado"*.

De quebra: o `OnSuccess` da aplicação **reconsultava a lista** (`Filter` + `Sort` por ID) para
reencontrar o registro que ele mesmo acabara de gravar. Passou a usar `Self.LastSubmit` direto —
uma ida ao servidor a menos, e sem a corrida de duas gravações simultâneas pegarem o registro
uma da outra.

### Por que isso importava

`FormLacresAplicacao_1` e `FormRompimentoLacre_1` gravam em `tbl_Lacres_Aplicacao` e, no `OnSuccess`,
fazem `Patch` do `Status` em `tbl_Pontos_Lacraveis`. Se o `SubmitForm` funciona e o `Patch` falha —
permissão, rede, item bloqueado — o lacre fica registrado e **o ponto fica com o status antigo**,
sem nada na tela.

O sintoma é traiçoeiro: o cartão mostra o lacre aplicado (vem do registro) mas com a cor e o selo do
status anterior (vem do ponto). E o `Patch` não devolve erro para lugar nenhum.

Correção: `IfError` em volta do `Patch`, com `Notify` de erro, e `OnFailure` nos dois formulários.
Barato e cabe na mesma colagem da próxima rodada.

---

## 6. Validação de número de lacre: existe uma tentativa abandonada

Em `txtNumeroLacre_1.OnChange` há um bloco **inteiro comentado** que buscava a última aplicação
daquele número de lacre e o ponto correspondente. Foi escrito e desligado.

Hoje nada impede:

- aplicar o **mesmo número de lacre** em dois pontos ao mesmo tempo;
- reaplicar um número já rompido, o que num controle de lacre físico é exatamente o que a
  numeração serve para impedir.

Não sei se isso é um problema real na sua operação (depende de os lacres serem realmente
descartáveis e numerados de forma única) ou se o bloco foi abandonado por não ser necessário.
**Vale uma trava no SALVAR?** Se sim, dá para fazer sem consulta remota nova, reaproveitando o
`col_aplicacao_bruta` que a tela já tem.

### E há uma variável que ninguém lê

O `OnChange` das duas combos de ponto (`ComboboxPontos_2` e `_3`) monta `varUltimaAplicacao` com um
`LookUp` cuja *expressão de resultado* é outro `Filter` + `Sort` sobre a `tbl_Lacres_Aplicacao` —
duas consultas remotas a cada troca de ponto. **Nenhum controle das três telas lê essa variável.**

Pior: a condição é `ID_Ponto_Lacravel = varPontoSelecionado.ID`, que compara a coluna de texto com o
`ID` numérico do ponto. Provavelmente nunca casa, então `varUltimaAplicacao` já é sempre vazia.

⚠️ **Não removi, mesmo com a limpeza autorizada em 08/09/2026, e o motivo é honesto:** eu disse antes
que a variável "provavelmente já é sempre vazia" porque a condição compara texto com número. Fui
conferir e **não tenho como afirmar isso**: se o Power Fx coage texto para número nessa comparação,
ela casa e a variável tem conteúdo. `Set` cria variável global, e alguma tela do app que eu não
tenho pode estar lendo.

Custo de manter: duas consultas remotas quando o operador **troca o ponto dentro do formulário** —
uma ação rara, não é caminho quente. Custo de remover errado: quebrar uma tela que eu não vejo.

Fica para quando você confirmar duas coisas: que nenhuma outra tela lê `varUltimaAplicacao`, e o que
aquele `LookUp` devolve hoje (dá para ver pondo a variável num rótulo temporário).

---

## 7. `Recorrente` e `Alerta_Enviado` — metade do circuito está fora do app

O ponto tem `Recorrente` ("avisar de hora em hora que este ponto está sem lacre") e a aplicação tem
`Alerta_Enviado`. O app grava `Alerta_Enviado: false` no `OnSuccess` da aplicação, e nunca grava
`true`.

Ou seja: quem liga o alarme é o app, e quem desliga tem que ser um fluxo do Power Automate. Não
tenho esse fluxo. **Ele existe e está rodando?** Se não existir, `Recorrente` é um campo que o
usuário preenche achando que vai receber aviso, e não recebe.

---

## 8. `App.OnStart` — três consultas evitáveis

| O quê | Custo |
|---|---|
| `LookUp(User; ...)` roda **três vezes** | uma no `Set(varIdUser)`, mais duas dentro do `With`, todas trazendo o mesmo registro |
| `UsuáriosdoOffice365.SearchUser` + `UserPhoto` | duas idas ao conector para achar a foto pelo nome; `UserPhotoV2(User().Email)` faz numa |
| `col_colaboradores` | carrega a lista inteira de colaboradores do aeroporto **antes de qualquer tela precisar dela** |

Nada disso é do módulo de Lacres, e mexer no `OnStart` afeta os dois módulos e as outras telas que
eu não vi. Fica registrado, não mexido.

Só um detalhe que merece olho: no ramo `"CWB"` do `Switch`, o resultado de `col_colaboradores` é o
que o `Collect(CWB_ALL; CWB_2)` devolve. Funciona, mas por acidente da forma como o `Switch` avalia
o último comando do ramo — não porque alguém tenha decidido que é isso. Se um dia alguém acrescentar
uma linha depois do `Collect`, `col_colaboradores` muda de conteúdo em silêncio.

---

## 9. Miudezas

- `ButtonAtualizar_2` — o botão que recarrega a tela — tem o rótulo **"Aplicar"**. Não mudei porque
  texto é visível ao usuário; mudo se você quiser.
- `ButtonCanvas7_9` do cadastro faz só `Refresh(tbl_Pontos_Lacraveis)`, mas o `OnVisible` da tela o
  chama esperando recarregar estado. Funciona porque a galeria lê a lista direto.
- A exclusão só é permitida a **quem criou o registro** (`'Criado por'`). Num controle que responde
  a RFB e AVSEC, o normal seria o supervisor poder. Mantive a regra que já existia. **Muda?**
- O `Search()` da `Gallery4_2` busca em `Local`, `Numero_Lacre` e `Responsavel_Aplicacao`. Depois da
  correção de hoje, pontos sem lacre entram com esses dois últimos em branco — o que está certo,
  mas significa que buscar por número de lacre esconde os pontos sem lacre. É o comportamento
  esperado; anotado para não virar "bug" numa próxima leitura.

---

## 10. ✅ O `Status` deixou de ser fonte da verdade na tela — 08/09/2026

**Regra do Douglas: "se está ATIVO tem que estar com lacre; se não, fica como sem lacre."**

O campo `Status` de `tbl_Pontos_Lacraveis` é mantido por `Patch` do app — é uma *opinião* sobre o
dado, não o dado. A tela de operações agora **deriva** o estado do fato:

```
StatusPonto: If(
    IsBlank(U.ID),              "Criado",     // nenhuma aplicacao
    IsBlank(U.Data_Rompimento), "Ativo",      // aplicacao aberta
                                "Rompido"
)
```

Isso conserta de uma vez os cartões, o balde "Ativos", o KPI de percentual e o de atenção imediata —
todos liam `StatusPonto`.

✅ **Verificado em 08/09/2026: os dados estão certos.** Eu suspeitava que os 19 pontos estivessem
"Ativo" sem lacre; o Douglas conferiu e todos têm lacre aplicado de verdade — o histórico confirma,
29 aplicações no CWB. Então o campo `Status` e a derivação **concordam**, e o Power BI não tem
problema nenhum. Não há registro para corrigir.

O ganho da derivação continua valendo mesmo assim: a tela deixou de depender de um campo que só está
certo enquanto todo `Patch` funcionar. O campo segue sendo gravado pelos formulários, porque o
`RelatorioLacres.pbix` lê a coluna direto da lista e não passa por esta tela.

## Ordem sugerida

**Feito em 08/09/2026:** exclusão de ponto lacrável, item 2 (`_9` órfão), item 3 (sobras de Chaves),
item 4 (filtro do histórico), item 5 (`OnFailure`), item 10 (status derivado), mais a tela nova
`ScreenHistoricoLacres` e o alinhamento do cadastro.

**Sobre a `ScreenHistoricoLacres`** (validada no app em 08/09/2026, 29 movimentos no CWB): espelha a
`ScreenHistoricoOperacao` das chaves — `HtmlViewer` único com CSS grid, cabeçalho e `Concat`. Três
diferenças deliberadas:

1. **Período padrão de 24 meses**, não do mês corrente. Copiar o padrão das chaves deixou a tela
   vazia na primeira colagem: chave é retirada e devolvida no mesmo dia, lacre fica aplicado por
   meses. Um filtro de "este mês" esconde justamente o que interessa.
2. **Contador "X de Y movimentos do aeroporto"**, com Y ignorando período e busca. Existe para que
   "vazio" seja diagnosticável: 0 de 0 é aeroporto sem lacre ou coluna `Aeroporto` com outra
   grafia; 0 de 340 é filtro estreito demais.
3. **A cor significa o oposto da tela de chaves.** Lá, vermelho = chave não devolvida. Aqui o lacre
   intacto é o estado bom: verde para ATIVO, vermelho claro para ROMPIDO, vermelho forte reservado
   para VERIFICAR (rompimento sem autorizador ou marcado como não intencional) — o mesmo critério
   do KPI "exige atenção imediata". Isso alinha com os cartões da tela de operações, que já pintam
   `Ativo` de verde.

O `col_hist_pontos` que dá nome ao ponto **não filtra `Excluido`**, de propósito: ponto inativado
tem que continuar legível no histórico, e linhas dele aparecem com "(inativado)" ao lado do nome.
É exatamente para isso que a exclusão é lógica.

⚠️ **Achado no dado real, sem decisão ainda:** há registros com `Numero_Lacre` fora do padrão
numérico — `"0032-0033"`, `"0026-0027"`, `"0024-0025"` (dois lacres num registro só) e
`"Motiva/ Operações e Segurança"` (não é número). Isso afeta o item 6: uma trava de lacre duplicado
não pode ser comparação exata se a numeração admite faixa e texto livre.

**Falta:**

1. **Subir o limite de linhas para 2.000** (item 1). Configuração do app, não custa colagem, e com
   20–30 pontos por aeroporto resolve por uma década.
2. **Preencher `Excluido` = Não nos itens antigos** e conferir que a coluna tem padrão configurado.
   Some o aviso de delegação do `<> true`.
4. **Depende de resposta sua:** item 6 (trava de número de lacre duplicado), item 6b
   (`varUltimaAplicacao` — o que ele devolve hoje e se outra tela o lê), item 7 (o fluxo do Power
   Automate que desliga `Alerta_Enviado` existe?), e se a exclusão deve ganhar trava por perfil.
5. **Arquivado:** a reengenharia do item 1 (resumo no ponto). Não se paga nesta escala. Fica escrita
   para o dia em que a ordem de grandeza mudar.
