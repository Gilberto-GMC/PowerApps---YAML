# Empréstimo e devolução de várias chaves de uma vez

Entregue e validado no app em 08/09/2026, em duas colagens da `ScreenOperação`.

## O que mudou, em uma frase

O módulo emprestava uma chave por vez. Agora o operador marca várias clicando nos cartões e retira
ou devolve todas numa operação, com **uma assinatura só** — mas **cada chave continua sendo um
registro próprio** em `tbl_movimentacoes`.

## A decisão que fez o resto ser barato

Cinco chaves = cinco movimentações, criadas juntas. Não uma movimentação com cinco chaves.

Isso preserva, sem tocar em nada:

| A jusante | Por quê continua valendo |
|---|---|
| `ScreenHistoricoOperacao` | Lê `id_chave` escalar e faz `LookUp(tbl_chave, ID = id_chave)`. Uma linha por chave, como sempre |
| `tbl_chave_extravio.id_entrega` (1:1 com a movimentação) | Extraviar uma chave de um lote de 5 deixa as outras 4 abertas — o comportamento certo |
| `RemoveIf(tbl_movimentacoes, id_chave = ...)` do cascade delete de `ScreenChaves` | Apagar uma chave apaga só as linhas dela |
| Power BI | Mesmo formato de sempre |
| **Devolução parcial** | Sai de graça: devolver 2 de 5 é `Patch` em 2 linhas |

A única coluna nova é `lote` (Texto, sem acento) em `tbl_movimentacoes`, com o mesmo valor nas N.
Ela existe porque a assinatura é a mesma nas cinco: sem um código, não haveria como provar depois
que aquela assinatura cobriu aquelas chaves.

Código do lote, gerado sem `GUID()` (que não tem um único uso neste workspace):

```
"L" & Text(Year(Now()), "0000") & Text(Month(Now()), "00") & Text(Day(Now()), "00")
    & "-" & Text(Hour(Now()), "00") & Text(Minute(Now()), "00") & Text(Second(Now()), "00")
    & "-" & Left(Coalesce(ComboboxCanvasAeroporto.Selected.Value, varAeroUser), 3)
```

Montado componente a componente de propósito: em `Text(Now(), "yyyymmdd-HHmmss")` o `mm` significa
mês depois de `yyyy` e minuto depois de `HH`. `Text(Hour(Now()), "00")` tem precedente literal na
própria tela.

## Como funciona

**Marcar:** clique no cartão. Nenhum controle novo entrou nas galerias — a marca é desenhada no HTML
que o cartão já montava (retirada) ou pela borda e fundo do container (devolução). Isso foi
deliberado: os templates são ManualLayout com `X` explícito, e há lição no workspace de que o Studio
pode descartar `X` de filho de galeria ao colar.

**Dois caminhos convivem.** O botão "Retirar"/"Devolver" de cada cartão continua sendo o atalho de
uma chave e continua passando por `SubmitForm` — o caminho provado, intocado. Ele apenas marca
`var_modoLote`/`var_modoLoteDev` como `false`, então ignora a seleção **sem apagá-la**.

**Gravar em lote** usa `ForAll` + `Patch(tabela, Defaults(tabela), {...})`, padrão com precedente
forte no SAFETY. Cada campo do `Patch` é cópia literal do `Update` do DataCard correspondente — se
um dia um card mudar, há um só lugar a espelhar.

**Confirmação:** painel listando as chaves, no padrão do modal de exclusão do cadastro de pontos.

**Legenda:** a dica e a barra de contagem ocupam o mesmo lugar. Sem seleção aparece *"Toque no
cartão para marcar várias chaves…"*; ao marcar a primeira, vira *"N selecionada(s)"* com os botões.

## Travas

- Chave já retirada não aparece na lista de disponíveis (já era assim).
- `ButtonAtualizar` **reinterseca as duas seleções** com o que continua disponível, então a trava
  vale continuamente e não só no clique.
- **Revalidação no servidor antes de gravar a retirada**: se outro operador levou uma chave entre
  marcar e confirmar, **aborta o lote inteiro** e desmarca as conflitantes. Abortar tudo em vez de
  gravar o que dá, porque a assinatura foi colhida para aquele conjunto.
- A devolução não tem revalidação de propósito: tudo naquela lista já é retirada em aberto, e dois
  operadores devolvendo a mesma chave gravam o mesmo resultado.

Delegação: os predicados delegáveis (`aeroporto`, `operacao`) vão no `Filter` contra a tabela; a
interseção com a seleção acontece **depois, local**. `id_chave in col_chaveSel.ID` não delega — é o
mesmo arranjo que o `ButtonAtualizar` já usava.

## Quem devolveu, quando o lote mistura pessoas

Campo de colaborador em branco → cada chave mantém quem a retirou
(`Coalesce(ComboBoxRazaoSocial_4.Selected.Nome, M.sequencial_colaborador)`). Nome escolhido → vale
para todas. O painel avisa em amarelo quando a seleção junta pessoas diferentes.

## Três defeitos encontrados no caminho

1. **YAML inválido, não Power Fx.** `OnSelect: =UpdateContext({var: false})` num escalar simples
   quebra o parser: o `: ` dentro do valor vira mapeamento. Tem que ser bloco (`|-`). Passei a rodar
   duas verificações novas em todos os arquivos — `: ` em escalar simples e indentação estrutural.
2. **Cartão de confirmação sem `Height`.** A lista do meio tinha altura fixa e o cartão dependia do
   conteúdo; a linha de botões ficava cortada. Cartão ganhou altura própria e a lista virou
   `FillPortions: =1`.
3. **`FormDevolucao` abria vazio em lote.** Ele fica em modo Edit e seu `Item` procurava
   `var_dadosMovimentacao`, que só o botão do cartão preenche. O `Item` passou a ramificar e ancorar
   na primeira da seleção. ⚠️ A correção óbvia — setar `var_dadosMovimentacao: First(col_movSel)` —
   daria **conflito de tipo**: essa variável recebe o `ThisItem` inteiro da galeria em outro ponto,
   e `col_movSel` guarda quatro colunas.

## O risco que não se concretizou

`assinatura: Image3.Image` dentro de um `ForAll` **não tinha precedente em nenhum arquivo do
workspace**, e falharia calado — N registros com assinatura em branco e nenhuma mensagem. Validado
no app: grava corretamente em todas as chaves do lote.

## Correção de higiene feita de passagem

O botão "Devolver" de cada cartão fazia `ResetForm(FormRetirada)` — formulário errado. Inofensivo,
porque o de devolução está em modo Edit e lê o `Item`, mas a linha ia ser tocada de qualquer jeito.

## Ficou de fora

- **`lote_devolucao`**: distinguiria "5 devolvidas juntas" de "5 ao longo do dia". Não criei — sem
  assinatura na devolução, o valor de auditoria é bem menor. Uma coluna e uma linha, se quiser.
- **Mostrar o lote no histórico**: uma coluna a mais no grid da `ScreenHistoricoOperacao`. Só faz
  sentido depois que houver lotes reais para olhar.
- **`lote_qtd`** foi recusado de propósito: o cascade delete de `ScreenChaves` apaga uma linha do
  lote sem tocar nas irmãs, e o campo viraria mentira em silêncio. Quando precisar do total, derive
  com `CountRows(Filter(tbl_movimentacoes, lote = X))`.

## Duas coisas que valem saber

- **A busca esconde a seleção.** Marque 3 chaves, digite no campo de busca, e os cartões marcados
  podem sumir da lista continuando marcados. A contagem na barra e a lista do painel tornam isso
  recuperável, mas é um susto na primeira vez.
- **`ForAll` + `Patch` não é transação.** Falhando na terceira de cinco, duas já foram gravadas e o
  SharePoint não desfaz. A mensagem de erro diz isso ao operador em vez de fingir que nada
  aconteceu. Na prática, manter lotes na casa de 5 a 10 chaves.
