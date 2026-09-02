# Estrutura da lista SharePoint — Mapa de Alocação de Pátio

Documentos irmãos:
[ARQUITETURA_MAPA.md](ARQUITETURA_MAPA.md) (decisões) ·
[AppFormulas_Mapa.fx.md](AppFormulas_Mapa.fx.md) (dados de referência e tema) ·
[FLUXO_EXPURGO_MAPA.md](FLUXO_EXPURGO_MAPA.md) (limpeza automática)

O app tem **uma única lista**. Pátios, posições, portões e companhias não são listas — são dados de referência
locais em `App.Formulas`, porque não crescem, não são alimentados pelo usuário final e cabem em memória
(critério em `ARQUITETURA_MAPA.md` §2). Isso significa **uma conexão, uma chamada de rede na abertura, nenhuma
tela de cadastro e nenhum índice de manutenção**.

---

## Dois caminhos para criar a lista

**A — pelo fluxo `List_Generator` (recomendado, ~2 min).** [lista_tb_alocacoesMapa.json](lista_tb_alocacoesMapa.json)
já tem as 18 colunas, os 5 índices, as validações de coluna e a validação de lista. Importe
[List_Generator_v2.zip](../List_Generator/List_Generator_v2.zip), execute o fluxo, informe o `siteUrl` e cole o
JSON. Ele cria a lista com versionamento ligado, anexos desabilitados, desobriga e esconde o `Título`, e tira
o `Título` da view padrão. Depois só restam os passos 8 e 9 da *Ordem de execução* — as views extras e a
permissão.

> **Uma diferença a saber.** O padrão do `List_Generator` é **nome interno igual ao nome de exibição**, tudo
> em `snake_case`: a coluna aparece como `data_operacao`, não como "Data da Operação". Isso é proposital — é o
> que elimina de vez o risco de nome codificado. Se preferir os rótulos amigáveis da tabela abaixo, renomeie a
> exibição depois de criada; o nome interno não muda junto e o app continua funcionando.

**B — manual.** Siga o resto deste documento. Mais lento e com o risco do nome codificado, mas não depende do
fluxo estar importado no ambiente.

---

## ⚠️ Leia antes de criar a primeira coluna

Quando você digita o nome de exibição direto na criação, o SharePoint codifica o nome interno:

```
"Data da Operação"  →  Data_x0020_da_x0020_Opera_x00e7_x00e3_o
```

O app referencia **nome interno**. Se ele nascer codificado, toda fórmula quebra.

### Procedimento obrigatório para CADA coluna

1. **+ Adicionar coluna** → escolher o tipo → digitar **exatamente o nome interno** em `snake_case` da tabela abaixo.
2. **Salvar.**
3. Cabeçalho da coluna → **Editar** → trocar o nome para o nome de exibição.

**Não pule o passo 2.**

### Como conferir depois

`.../_layouts/15/FldEdit.aspx?List={GUID}&Field=data_operacao` — se abrir a coluna, o nome interno está certo.
Se aparecer qualquer `_x00`, a coluna precisa ser **excluída e recriada**. Não tem conserto.

### Neutralizar a coluna `Título`

Não usamos `Title`. Para desobrigá-la:

1. Configurações da lista → **Configurações avançadas** → *Permitir gerenciamento de tipos de conteúdo* = **Sim**.
2. Voltar → **Tipos de conteúdo** → **Item** → coluna **Título**.
3. Marcar **Oculto** → OK.
4. Configurações avançadas → gerenciamento de tipos de conteúdo de volta para **Não**.
5. Remover `Título` de **todas** as views.

*Fallback,* se o passo 3 não estiver disponível: marcar **Opcional** em vez de Oculto.

### Nenhuma coluna Sim/Não

Coluna Sim/Não do SharePoint **nasce nula**, e `NULL` não casa com `eq false` no OData: `!coluna` e
`coluna = false` devolvem **zero linhas, sem erro**. Toda flag deste projeto é **Número**, 0 casas decimais,
com valor padrão explícito. Positivo é `= 1`; negativo é `<> 1`, **nunca `= 0`**.

### Nenhuma coluna Escolha e nenhuma coluna Pesquisa

Enumeração vem de `App.Formulas` e é gravada como **Texto** — o app grava o texto direto, sem `Choices()`, sem
`.Value` no `Patch`, indexável e com filtro `=` delegável. Relacionamento com as posições é por **número**
(`id_posicao` ↔ `colPosicoes.id`), não por coluna Pesquisa.

---

# Lista — `tb_alocacoesMapa`

**Como criar:** site do SharePoint → **Novo** → **Lista** → **Lista em branco** → nome `tb_alocacoesMapa`.

**Por que é lista e não `App.Formulas`:** cresce ~40 registros por dia, é alimentada pelo usuário final e
precisa ser vista por todo mundo ao mesmo tempo. Falha nos três testes de dado estático.

## 1. Identificação e recorte

| # | Nome interno | Nome de exibição | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|---|
| 1 | `aeroporto` | Aeroporto | Texto (uma linha) | Sim | ICAO, 4 caracteres · **Indexada** |
> ⚠️ **`aeroporto` guarda o NOME, não o ICAO** — `NAVEGANTES`, não `SBNF`. Ver a lição de 02/09/2026
> no `LICOES_APRENDIDAS_POWERAPPS_YAML.md`. A coluna foi de `MaxLength=10` para `60`: nome de
> aeroporto não cabe em 10 caracteres com folga nenhuma.
>
> **Migração obrigatória antes de colar o app**, e ela é silenciosa se esquecida:
> 1. Ampliar `aeroporto` para 60 caracteres nas configurações da coluna.
> 2. Na exibição em grade, trocar **todos** os `SBNF` por `NAVEGANTES` — inclusive nos inativos
>    (`ativo = 0`), que o expurgo ainda lê.
> 3. Filtrar por `aeroporto = SBNF` e conferir **zero** linhas.
> 4. Só então colar `App.Formulas` e as telas.
>
> Pulando isso, o filtro `aeroporto = varAero` deixa de casar e **a grade abre vazia, sem erro**.

| 2 | `data_operacao` | Data Inicial | Data e Hora → **Somente data** | Sim | **Indexada** — dia em que a ocupação **começa**; o fim é `data_fim` (#18) |
| 3 | `id_posicao` | ID da Posição | Número | Sim | 0 casas · **Indexada** · aponta para `colPosicoes.id` |
| 4 | `posicao_txt` | Posição | Texto (uma linha) | Sim | `T4` — redundante, para leitura humana e Power BI |
| 5 | `patio_txt` | Pátio | Texto (uma linha) | Sim | `PRINCIPAL` · `PATIO3` · `HELIPONTOS` |

> `posicao_txt` e `patio_txt` são redundância proposital: deixam a lista legível sem o app e permitem filtrar
> por pátio sem nenhum cruzamento. O app grava os três (`id_posicao`, `posicao_txt`, `patio_txt`) no mesmo `Patch`.

## 2. O voo

| # | Nome interno | Nome de exibição | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|---|
| 6 | `cia_sigla` | Companhia | Texto (uma linha) | Não | `GLO` `AZU` `TAM` `ONE` `FAB` `GER` — vazio em interdição |
| 7 | `voo_chegada` | Voo de Chegada | Texto (uma linha) | Não | `1214` |
| 8 | `voo_saida` | Voo de Saída | Texto (uma linha) | Não | `1217` |
| 9 | `prefixo` | Prefixo | Texto (uma linha) | Não | `PSESP` — aviação geral e helicópteros |
| 10 | `envergadura_m` | Envergadura (m) | Número | Não | 2 casas decimais |
| 19 | `equipamento` | Equipamento | Texto (uma linha) | Não | código de `tb_equipamentos.equip` — ver `ESTRUTURA_LISTAS_REGRAS.md` |
| 20 | `internacional` | Internacional | Número | Sim | 0 casas · `1` internacional · `0` doméstico · **Default `0`** |

> ⚠️ **O `ativo` da lista em produção tem `Default 0`, não `1`.** O `schemaXml` deste repositório diz
> `1`, e a lista real foi criada antes dele — as duas divergem. Descoberto em 02/09/2026 colando
> registros de importação: entraram com `ativo = 0` e **sumiram do app sem erro nenhum**, porque o
> filtro do dia exige `ativo = 1`.
>
> **Carga em massa nunca deve depender de default de coluna.** Escreva o valor explicitamente, mesmo
> quando o esquema promete um default: o que vale é a coluna que existe, não a que está documentada.

> **O `Default 0` é o que faz o acervo antigo já nascer correto.** Diferente do `equipamento` e do
> `data_fim`, aqui não há migração a fazer: o padrão é doméstico, e registro sem a coluna preenchida
> **é** doméstico. Criar a coluna com `Default 0` e obrigatória resolve os dois casos de uma vez — os
> existentes recebem 0 e os novos não podem ficar em branco.

> **`envergadura_m` deixou de ser digitada e passou a ser derivada.** A partir da checagem de
> compatibilidade, o valor que vale é `Coalesce(o que foi digitado, catálogo[equipamento].envergadura_m)`:
> o campo continua editável para cauda fora do padrão ou modelo fora do catálogo, mas em branco ele herda
> do equipamento. As duas colunas convivem de propósito — `equipamento` é a regra, `envergadura_m` é a
> exceção, e registro antigo só tem a segunda.

## 3. A ocupação no tempo

| # | Nome interno | Nome de exibição | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|---|
| 11 | `hora_inicio` | Início (min) | Número | Sim | 0 casas · **minutos desde 00:00**, `0`–`1439` |
| 12 | `hora_fim` | Fim (min) | Número | Sim | 0 casas · `1`–`1440` |
| 13 | `portao` | Portão | Texto (uma linha) | Não | `1`…`5` |
| 18 | `data_fim` | Data Final | Data e Hora → **Somente data** | Sim | **Indexada** · dia em que a ocupação **termina** · `>= data_operacao` |

> **Por que minutos e não coluna Hora.** A grade é aritmética pura: a largura do bloco é
> `(hora_fim - hora_inicio) / 1440`. Minutos eliminam fuso horário, eliminam conversão a cada render, delegam
> com `>=` / `<=`, e a detecção de sobreposição vira comparação de inteiros. O app converte para `HH:mm` só na
> exibição e na digitação.

> **Um registro, um intervalo — mesmo que ele dure dias.** O par é
> (`data_operacao`, `hora_inicio`) → (`data_fim`, `hora_fim`). Pernoite, aviação geral parada por dias,
> interdição de obra: tudo é **um** registro. `hora_inicio` continua sendo minuto do dia de entrada e
> `hora_fim`, minuto do dia de saída — as duas colunas nunca mudam de significado, muda só a data a que
> cada uma se refere. Quando entra e sai no mesmo dia, `data_fim = data_operacao` e nada muda em relação
> ao modelo antigo.
>
> **Numeração fora de ordem de propósito.** `data_fim` é a #18 porque foi acrescentada depois; renumerar
> as 17 primeiras só criaria divergência com quem já criou a lista. A ordem de criação não importa.
>
> ⚠️ **`data_fim` é obrigatória e não pode ficar nula em nenhum registro.** O filtro do dia é
> `data_operacao <= dia And data_fim >= dia`: registro com `data_fim` em branco **não casa com a
> comparação e some da grade** — sem erro, sem aviso. Ver *Migração* no fim deste documento.

## 4. Classificação e estado

| # | Nome interno | Nome de exibição | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|---|
| 14 | `tipo_registro` | Tipo | Texto (uma linha) | Sim | `VOO` · `INTERDICAO` · `RESERVA` · **Padrão: `VOO`** |
| 15 | `pesquisado` | Voo Pesquisado | Número | Sim | 0 casas · **Padrão: `0`** · `1` = voo da pesquisa |
| 16 | `observacao` | Observação | Texto (várias linhas) | Não | Texto sem formatação · "missão presidencial" |
| 17 | `ativo` | Ativo | Número | Sim | 0 casas · **Padrão: `1`** · **Indexada** · exclusão lógica |

> `pesquisado` e `ativo` são **Número**, não Sim/Não — ver o aviso no topo. O app testa `pesquisado = 1` e
> `ativo = 1`, e o negativo é `<> 1`.

## 5. Colunas nativas — o que já vem pronto e **não** deve ser recriado

| Coluna | Interno | Uso no sistema |
|---|---|---|
| ID | `ID` | Chave do registro · base do verificador de alteração (maior `ID` do dia) |
| Título | `Title` | **Não usada** — desobrigada e oculta, fora de todas as views |
| Criado | `Created` | Quando a programação foi lançada |
| Criado por | `Author` | Quem lançou |
| Modificado | `Modified` | **Exibido no painel lateral** |
| Modificado por | `Editor` | **Exibido no painel lateral** — é o "um mexe, o outro vê" |
| Anexos | `Attachments` | **Desabilitar** — não há anexo neste app |

## 6. Configuração da lista

| Item | Onde | Valor |
|---|---|---|
| **Versionamento** | Configurações da lista → Configurações de versão | **Ligado, 50 versões** — ligar **antes** da primeira carga |
| Anexos | Configurações avançadas | **Desabilitados** |
| Aprovação de conteúdo | Configurações de versão | Não |
| **Índices** | Configurações → Colunas indexadas | `aeroporto`, `data_operacao`, `data_fim`, `id_posicao`, `ativo` |
| Experiência de formulário | Configurações avançadas | Indiferente — a edição é toda pelo app |

> Criar os índices **antes** de a lista passar de 5.000 itens. Com o expurgo ligado ela se estabiliza em
> ~1.500, mas o índice em `data_operacao` é o que mantém o filtro do dia delegável desde o primeiro item.

## 7. Validação de coluna

Configurações da lista → coluna → **Validação de coluna**. Rede de segurança para edição feita fora do app.

| Coluna | Fórmula (site em pt-BR usa `;`) | Mensagem |
|---|---|---|
| `tipo_registro` | `=OU([tipo_registro]="VOO";[tipo_registro]="INTERDICAO";[tipo_registro]="RESERVA")` | `Use o app Mapa de Alocação para editar este campo.` |
| `hora_inicio` | `=E([hora_inicio]>=0;[hora_inicio]<=1439)` | `Início fora do dia (0 a 1439 minutos).` |
| `hora_fim` | `=E([hora_fim]>=1;[hora_fim]<=1440)` | `Fim fora do dia (1 a 1440 minutos).` |
| `data_fim` | `=[data_fim]>=[data_operacao]` | `A data final não pode ser anterior à inicial.` |
| `pesquisado` | `=OU([pesquisado]=0;[pesquisado]=1)` | `Use 0 ou 1.` |
| `ativo` | `=OU([ativo]=0;[ativo]=1)` | `Use 0 ou 1.` |

Validação **da lista** (Configurações → Configurações de validação), que enxerga duas colunas ao mesmo tempo:

```
=OU([data_fim]>[data_operacao];[hora_fim]>[hora_inicio])
```
Mensagem: `Quando entra e sai no mesmo dia, o fim tem que ser maior que o início.`

> ⚠️ **Era `=[hora_fim]>[hora_inicio]` e essa forma rejeita todo pernoite.** Um voo que chega 22:00 e sai
> 06:10 do dia seguinte grava `hora_inicio` 1320 e `hora_fim` 370 — o fim é *menor* que o início, e a
> validação antiga barra a gravação no próprio SharePoint, com um erro que o app só consegue reportar como
> "não foi possível gravar". Trocar esta fórmula é **obrigatório** antes de usar registros multi-dia.

> ⚠️ Site em **en-US** usa `OR` / `AND` e vírgula: `=OR([tipo_registro]="VOO", ...)`.

## 8. Views

| Nome da view | Filtro | Ordenação | Colunas |
|---|---|---|---|
| **Programação** *(padrão)* | `ativo` = `1` **E** `data_fim` >= `[Hoje]` | `data_operacao` ↑, `hora_inicio` ↑ | data_operacao, data_fim, posicao_txt, cia_sigla, voo_chegada, voo_saida, hora_inicio, hora_fim, portao, tipo_registro, Modificado por |
| **⚠ Passado** | `data_fim` < `[Hoje]` | `data_fim` ↓ | as mesmas + `ativo` |
| **⚠ Inativos** | `ativo` = `0` | `Modificado` ↓ | ID, data_operacao, posicao_txt, Modificado, Modificado por |

`Título` fora de todas elas.

---

## Segurança e permissões

Não existe lista de acesso. Quem pode editar é definido **na permissão do próprio SharePoint**, e o app
descobre isso sozinho:

```powerfx
Set(varPodeEditar; DataSourceInfo('tb_alocacoesMapa'; DataSourceInfo.EditPermission))
```

| Grupo do site | Permissão na lista | O que vê no app |
|---|---|---|
| APOC — operação | **Editar** | Grade + painel lateral + salvar/excluir |
| Demais áreas | **Ler** | Grade e legenda, sem botões de edição |

Quebrar a herança de permissão da lista e conceder **Editar** só ao grupo da operação. É o mesmo controle que
protege a lista contra edição direta pela interface do SharePoint.

---

## Ordem de execução

> Fazendo pelo caminho **A**, os passos 1 a 7 já vêm prontos — vá direto para o 8.

1. Criar a lista `tb_alocacoesMapa`.
2. **Ligar o versionamento** — antes de qualquer carga.
3. Desabilitar anexos.
4. Criar as 18 colunas na ordem da tabela, sempre com o procedimento de 3 passos do topo.
5. Neutralizar a coluna `Título`.
6. Criar os 5 índices.
7. Aplicar as validações de coluna e a validação de lista.
8. Criar as 3 views e remover `Título` de todas.
9. Quebrar a herança de permissão e conceder **Editar** só à operação.
10. Criar o fluxo de expurgo — [FLUXO_EXPURGO_MAPA.md](FLUXO_EXPURGO_MAPA.md).

---

## Checklist de conferência

- [ ] Nenhum nome interno contém `_x00` (conferir os 18 pela URL `FldEdit.aspx?...&Field=`)
- [ ] `Título` **oculto e não obrigatório**, e fora das 3 views
- [ ] **Nenhuma** coluna Sim/Não, Escolha ou Pesquisa na lista
- [ ] `pesquisado` e `ativo` como **Número**, 0 casas, padrão `0` e `1` respectivamente
- [ ] `tipo_registro` com padrão `VOO`
- [ ] Versionamento ligado **antes** do primeiro item
- [ ] Anexos desabilitados
- [ ] 5 índices criados: `aeroporto`, `data_operacao`, `data_fim`, `id_posicao`, `ativo`
- [ ] Validação de lista `=OU([data_fim]>[data_operacao];[hora_fim]>[hora_inicio])` ativa
- [ ] **Nenhum registro com `data_fim` em branco** — filtrar a view por `data_fim` vazio e conferir zero
- [ ] Herança de permissão quebrada; leitura para o resto do site
- [ ] Um item de teste criado pelo app aparece na view **Programação** com `Modificado por` preenchido

---

## Migração — lista que já existe e já tem dados

`data_fim` entrou depois da lista estar em produção. A ordem abaixo não pode ser trocada: a tela nova
filtra o dia por `data_operacao <= dia And data_fim >= dia`, então **enquanto houver registro com
`data_fim` em branco, esse registro não aparece na grade** — e não há erro nenhum na tela para denunciar.

1. Criar a coluna `data_fim` **como opcional** (`Required=FALSE`), pelo procedimento de 3 passos do topo.
2. Abrir a view **Programação** em modo de edição rápida, incluir a coluna `data_fim` e preenchê-la com o
   mesmo valor de `data_operacao` em **todos** os itens. Em lista pequena, copiar/colar a coluna resolve;
   acima de algumas centenas de itens, vale um fluxo de nuvem `Obter itens` → `Atualizar item` gravando
   **só** `data_fim` (qualquer outro campo preenchido reescreve o registro e muda o `Modificado`, o que faz
   a faixa "a programação foi alterada" aparecer para todo mundo).
3. Conferir **zero** itens com `data_fim` vazio, inclusive os inativos (`ativo = 0`) — o expurgo lê essa
   coluna, e item com `data_fim` nula nunca casa com `lt` e fica na lista para sempre.
4. Só então marcar `data_fim` como **obrigatória** e criar o índice.
5. Trocar a validação de lista para `=OU([data_fim]>[data_operacao];[hora_fim]>[hora_inicio])`.
6. Ajustar as views (`data_fim` no lugar de `data_operacao` nos filtros).
7. Só depois de tudo isso, colar as telas novas e o `App.Formulas` novo.

### Pernoites que já foram lançados como dois registros

O modelo antigo mandava partir o voo que vira o dia em dois registros, um até `24:00` e outro a partir de
`00:00`. Eles continuam **funcionando e desenhando certo** depois da migração — viram dois registros de um
dia cada, exatamente como estão hoje. Juntar cada par num registro só é opcional e pode ser feito aos poucos:
abrir o registro da véspera no app, mudar a **DATA FINAL** para o dia seguinte, corrigir a hora de saída e
excluir o registro do dia seguinte. Não há pressa e não há risco em deixar como está.
