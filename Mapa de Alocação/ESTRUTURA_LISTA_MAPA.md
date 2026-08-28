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
| 2 | `data_operacao` | Data da Operação | Data e Hora → **Somente data** | Sim | **Indexada** — é a chave do filtro do dia |
| 3 | `id_posicao` | ID da Posição | Número | Sim | 0 casas · **Indexada** · aponta para `colPosicoes.id` |
| 4 | `posicao_txt` | Posição | Texto (uma linha) | Sim | `T4` — redundante, para leitura humana e Power BI |
| 5 | `patio_txt` | Pátio | Texto (uma linha) | Sim | `PRINCIPAL` · `PATIO23` · `HELIPONTOS` |

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

## 3. A ocupação no tempo

| # | Nome interno | Nome de exibição | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|---|
| 11 | `hora_inicio` | Início (min) | Número | Sim | 0 casas · **minutos desde 00:00**, `0`–`1439` |
| 12 | `hora_fim` | Fim (min) | Número | Sim | 0 casas · `1`–`1440` |
| 13 | `portao` | Portão | Texto (uma linha) | Não | `1`…`5` |

> **Por que minutos e não coluna Hora.** A grade é aritmética pura: a largura do bloco é
> `(hora_fim - hora_inicio) / 1440`. Minutos eliminam fuso horário, eliminam conversão a cada render, delegam
> com `>=` / `<=`, e a detecção de sobreposição vira comparação de inteiros. O app converte para `HH:mm` só na
> exibição e na digitação.

> **Bloco que cruza a meia-noite** é cortado em `1440` e continua como um segundo registro no dia seguinte —
> é exatamente o que a planilha já faz (`GLO 1857` aparece das 00:00 às 06:10 no dia).

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
| **Índices** | Configurações → Colunas indexadas | `aeroporto`, `data_operacao`, `id_posicao`, `ativo` |
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
| `pesquisado` | `=OU([pesquisado]=0;[pesquisado]=1)` | `Use 0 ou 1.` |
| `ativo` | `=OU([ativo]=0;[ativo]=1)` | `Use 0 ou 1.` |

Validação **da lista** (Configurações → Configurações de validação), que enxerga duas colunas ao mesmo tempo:

```
=[hora_fim]>[hora_inicio]
```
Mensagem: `O fim tem que ser maior que o início.`

> ⚠️ Site em **en-US** usa `OR` / `AND` e vírgula: `=OR([tipo_registro]="VOO", ...)`.

## 8. Views

| Nome da view | Filtro | Ordenação | Colunas |
|---|---|---|---|
| **Programação** *(padrão)* | `ativo` = `1` **E** `data_operacao` >= `[Hoje]` | `data_operacao` ↑, `hora_inicio` ↑ | data_operacao, posicao_txt, cia_sigla, voo_chegada, voo_saida, hora_inicio, hora_fim, portao, tipo_registro, Modificado por |
| **⚠ Passado** | `data_operacao` < `[Hoje]` | `data_operacao` ↓ | as mesmas + `ativo` |
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

1. Criar a lista `tb_alocacoesMapa`.
2. **Ligar o versionamento** — antes de qualquer carga.
3. Desabilitar anexos.
4. Criar as 17 colunas na ordem da tabela, sempre com o procedimento de 3 passos do topo.
5. Neutralizar a coluna `Título`.
6. Criar os 4 índices.
7. Aplicar as validações de coluna e a validação de lista.
8. Criar as 3 views e remover `Título` de todas.
9. Quebrar a herança de permissão e conceder **Editar** só à operação.
10. Criar o fluxo de expurgo — [FLUXO_EXPURGO_MAPA.md](FLUXO_EXPURGO_MAPA.md).

---

## Checklist de conferência

- [ ] Nenhum nome interno contém `_x00` (conferir os 17 pela URL `FldEdit.aspx?...&Field=`)
- [ ] `Título` **oculto e não obrigatório**, e fora das 3 views
- [ ] **Nenhuma** coluna Sim/Não, Escolha ou Pesquisa na lista
- [ ] `pesquisado` e `ativo` como **Número**, 0 casas, padrão `0` e `1` respectivamente
- [ ] `tipo_registro` com padrão `VOO`
- [ ] Versionamento ligado **antes** do primeiro item
- [ ] Anexos desabilitados
- [ ] 4 índices criados: `aeroporto`, `data_operacao`, `id_posicao`, `ativo`
- [ ] Validação de lista `=[hora_fim]>[hora_inicio]` ativa
- [ ] Herança de permissão quebrada; leitura para o resto do site
- [ ] Um item de teste criado pelo app aparece na view **Programação** com `Modificado por` preenchido
