# Exclusão de ponto lacrável

Entregue e colado no Studio em 08/09/2026. Este documento descreve o estado final; as correções de
rota que aconteceram no caminho estão no fim, porque as lições valem mais que o histórico.

## O bug que originou tudo

A exclusão **já estava construída** no `scrPontoLacravelForm`: botão `ButtonCanvas12_11`, modal de
confirmação, `RemoveIf(tbl_Pontos_Lacraveis, ID = ...)`. Só estava com `Visible: =false`.

E era uma **exclusão física**. O problema não era o ponto continuar aparecendo — era que a tela de
operações nunca olhava para o ponto. Ela era dirigida pela `tbl_Lacres_Aplicacao`:

```
Filter(tbl_Lacres_Aplicacao As A, A.Data_Aplicacao = Max(Filter(...), Data_Aplicacao))
```

Apagar o ponto não apaga as aplicações dele. Elas sobrevivem órfãs, continuam entrando nesse
`Filter`, e o `LookUp` que deveria trazer o status não encontra ninguém e devolve **em branco**.

Por isso a correção não foi filtrar o excluído: foi **inverter o eixo da tela**. Quem manda é o
ponto; a aplicação só aparece através dele. Ponto excluído e aplicação órfã somem por construção,
não por filtro — não há como esquecer de filtrar num lugar.

## A regra final

A trava pergunta ao **dado real**, não ao campo `Status`:

| Situação real do ponto | O que acontece |
|---|---|
| Tem aplicação gravada **sem rompimento** (lacre aberto) | `Notify` amarelo: registre o rompimento primeiro. O modal não abre. |
| **Nunca teve** aplicação nenhuma | **Exclusão física** (`RemoveIf`), como já era. Não há histórico para orfanar. |
| Teve aplicações, todas já rompidas | **Exclusão lógica**: `Excluido = true`. Sai das telas, histórico intacto. |

⚠️ **O campo `Status` não serve como trava.** Todos os 19 pontos do CWB estão com `Status = "Ativo"`
inclusive os que nunca receberam lacre. Travar por `Status` obrigaria o operador a inventar um lacre
e rompê-lo só para poder apagar um ponto criado por engano. Foi o Douglas quem apontou isso.

Por que a exclusão lógica e não apagar tudo: o `Procedimento Controle de Lacres` e o documento de
desenvolvimento dizem, na governança, *"Apenas registro, nunca apagamento. Histórico sempre
preservado (RFB gosta disso)."* E apagar um ponto que já teve lacres apaga também a legibilidade do
histórico — a galeria de rompimentos e o Power BI passam a mostrar `Localizacao` em branco para
sempre, porque buscam a localização no ponto que não existe mais.

## Colunas em `tbl_Pontos_Lacraveis`

| Coluna | Tipo | Padrão |
|---|---|---|
| `Excluido` | Sim/Não | **Não** |
| `Excluido_em` | Data e Hora | — |
| `Excluido_por` | **Texto** (linha única) | — |

Três cuidados, todos aprendidos na prática:

1. **Sem acento no nome.** `Excluido`, não `Excluído` — o SharePoint transforma o acento no nome
   interno e o código para de achar a coluna. As colunas que já existem seguem essa regra
   (`Localizacao`, `Situacao_Normal`, `Orgao_Relacionado`).

2. ⚠️ **Criar a coluna com padrão "Não" NÃO preenche os itens que já existem.** Eu afirmei que
   preenchia; está errado. O padrão só vale para itens novos, e os 19 pontos ficaram com `Excluido`
   **em branco** — que não é `false`. Por isso as duas telas apareceram **vazias, sem nenhum erro**:
   `Excluido = false` não casou com ninguém. O filtro passou a ser `Excluido <> true`, que aceita
   branco. Vale preencher os itens antigos mesmo assim (Editar em modo de grade, "Não" na primeira
   célula, colar para baixo) e conferir que a coluna tem padrão configurado, senão ponto novo nasce
   em branco de novo.

3. **`Excluido_por` é Texto, não Pessoa.** Gravar coluna Pessoa por `Patch` exige montar o registro
   `SPListExpandedUser` na mão, e não há um único precedente disso em nenhum app deste workspace.
   Texto guarda `varNomeUser` e serve igual para o Power BI.

Não usei o nome `Ativo` de propósito: `Status = "Ativo"` já significa outra coisa. (O AVSEC usa
`ativo` como exclusão lógica, mas lá não há colisão.)

## O que mudou no código

### `scrPontoLacravelForm`

| Controle | Mudança |
|---|---|
| `GalleryLocal_2.Items` | Filtra `Excluido <> true`; `Excluido` entrou no `ShowColumns`; removido o bloco comentado do módulo de Chaves |
| `ButtonCanvas7_9` (recarregar) | Além do `Refresh`, monta `col_aplic_ponto` com os lacres do aeroporto. É o que permite testar lacre aberto sem consulta remota por linha na galeria |
| `ButtonCanvas12_11` (Excluir) | `Visible` passou a `true` |
| `ButtonCanvas12_11.DisplayMode` | `DisplayMode.Edit`, sem trava de autor — ver seção de permissão abaixo |
| `ButtonCanvas12_11.OnSelect` | Testa lacre aberto em `col_aplic_ponto`; se houver, `Notify` de aviso; se não, abre o modal e calcula `var_pontoTemHistorico` |
| `Label1_19.Text` | Mensagem do modal diz qual das duas exclusões vai acontecer |
| `ButtonCanvas2_16` (Sim) | Ramifica entre `Patch` (lógica) e `RemoveIf` (física) |
| `TextCanvas4_2` | Rodapé dizia "N **Chaves**"; agora "N pontos lacráveis" |

### `ScreenOperaçãoLacres_new`

| Controle | Mudança |
|---|---|
| `ButtonAtualizar_2.OnSelect` | Reescrito: dirigido pelo ponto, sem `Max()` correlacionado, sem `LookUp` remoto por linha |
| `Text2_10` (% de pontos ativos) | Duas consultas remotas → `col_ponto_lacravel` local |
| `Text2_13` (exige atenção imediata) | Consulta remota com `LookUp` por linha → `col_aplicacao` local |
| `ComboboxPontos_2` e `_3` | `Items` e `DefaultSelectedItems` apontavam para `ComboboxCanvasAeroporto_9`, **que não existe**. Agora leem `col_ponto_lacravel` |
| `DataCardValue39_1` (Aeroporto) | `Default` também dependia do `_9`; agora usa `ComboboxCanvasAeroporto_2.Selected.Value` |

Essa última fecha um buraco que a exclusão lógica sozinha deixaria aberto: como as duas listas de
ponto leem `col_ponto_lacravel`, que já exclui os inativados, **não dá para aplicar lacre em ponto
excluído**.

## A decisão de permissão

O botão Excluir exigia ser o **autor do registro**. Com isso ele ficava cinza nas 19 linhas, porque
os pontos foram criados por outra pessoa.

Tirei a trava. `Editar` e `Novo ponto lacrável`, na mesma tela, **nunca tiveram restrição nenhuma** —
qualquer um pode mudar a área de uma porta de ARS para Pública. Exigir autoria só para excluir não
protegia nada, e a edição sem trava é o caminho mais perigoso dos dois. A exclusão ainda tem três
defesas próprias: trava de lacre aberto, modal de confirmação, e inativação em vez de apagamento
quando há histórico. Quem manda na permissão passa a ser a lista do SharePoint.

**Se quiser uma trava de verdade, o eixo certo é o perfil, não a autoria.** Esta tela já usa
`varPerfilUser = "Sede"` para decidir quem troca o Bloco e `= "Base"` para quem troca o Aeroporto.
Basta dizer qual perfil pode excluir.

## Mudança de comportamento pendente de confirmação

O KPI **EXIGE ATENÇÃO IMEDIATA** contava *pontos distintos entre todos os rompimentos suspeitos já
gravados*, desde que o ponto ainda estivesse rompido. Agora conta *pontos cujo **último** movimento
é um rompimento suspeito*.

A diferença aparece num caso só: ponto rompido agora, cujo rompimento atual é autorizado e em hora
normal, mas que teve um rompimento suspeito no passado. Antes contava; agora não. Um card chamado
"exige atenção imediata" deveria falar do estado de agora, não de uma suspeita já resolvida — mas é
decisão do Douglas, e dá para voltar sem consulta remota.

## Notação

Os `.pa.yaml` desta pasta são para colar como **tela inteira** no Studio — vírgula separa argumentos,
`;` encadeia. Para editar propriedade por propriedade na barra de fórmulas, **não copie daqui**: lá o
separador é `;` e o encadeador é `;;`.

## Erros meus no caminho, e o que eles ensinam

1. **`ThisItem.Author` → `ThisItem.'Criado por'`.** Troquei alegando que `Author` não estava no
   `ShowColumns`. Errado: `'Criado por'` **é** o `Author` — nome de exibição e nome lógico são a
   mesma coluna no Power Fx. O original funcionava; a troca é que quebrou. E o Studio sublinhou a
   expressão booleana inteira, fazendo parecer que `varNomeUser` e `ThisItem.Status` também tinham
   problema. **Lição:** coluna referenciada pelo nome lógico num lugar e pelo de exibição noutro não
   é inconsistência. Antes de "corrigir", confirmar que a tela realmente acusa erro.

2. **Padrão de coluna Sim/Não não preenche item existente.** Detalhe 2 das colunas, acima.
   **Lição:** filtro novo contra coluna recém-criada tem que tolerar branco, ou a coluna tem que ser
   preenchida antes. Sintoma que identifica: tela vazia **sem nenhum erro de fórmula**.

3. **Travar por `Status` em vez de pelo dado.** Escrevi a regra assumindo que `Status = "Ativo"`
   significava lacre aplicado. Não significa. **Lição:** campo de estado mantido por `Patch` do app
   é uma opinião sobre o dado, não o dado. Trava de segurança pergunta ao fato.

4. **Botão desabilitado como forma de explicar.** A primeira versão desabilitava o Excluir. Botão
   cinza não diz por quê, e desabilitado pode nem disparar hover, então um `Tooltip` sumiria
   justamente quando fosse necessário. Virou botão clicável com `Notify`.
