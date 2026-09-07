# Compatibilidade de equipamento com a posição — estrutura das listas

Duas listas novas e uma coluna nova na lista existente. Elas respondem a uma pergunta só:
**esta aeronave pode ocupar esta posição, agora, com o que já está ocupado em volta?**

Arquivos de criação: `lista_tb_equipamentos.json`, `lista_tb_regrasPosicao.json`, e a coluna
`equipamento` já acrescentada em `lista_tb_alocacoesMapa.json`.

---

## Por que três coisas e não uma

A verificação tem três naturezas diferentes, e misturá-las numa tabela só é o que faz esse tipo de
regra virar impossível de manter:

| verificação | natureza | onde mora |
|---|---|---|
| envergadura cabe na posição | **numérica**, contínua | `env_max` em `colPosicoes` (App.Formulas) |
| este modelo não entra nesta posição | **enumerada**, específica | `tb_regrasPosicao`, `vizinha` vazia |
| estes dois modelos não ficam lado a lado | **enumerada**, relacional | `tb_regrasPosicao`, `vizinha` preenchida |

> **O caso do T4 é o que dita a arquitetura.** T4 tem `aeronave_max` = `B-738`, que é **maior** que um
> E195-E2, e mesmo assim o E195-E2 não pode. Não existe ordenação por tamanho que produza essa regra:
> ela é um fato específico daquela posição e precisa ser **declarada**, não deduzida. É por isso que a
> checagem por equipamento vem **antes** da de envergadura, e não como um refinamento dela.

---

## 1. `tb_equipamentos` — catálogo de aeronaves

Fonte única de envergadura. Global: **não** tem coluna de aeroporto, o mesmo catálogo serve a todos.

| # | Nome interno | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|
| 1 | `equip` | Texto (uma linha) | Sim | **Indexada** — código do tipo, `B38M`, `E295`, `AT72` |
| 2 | `nome_equip` | Texto (uma linha) | Sim | `Boeing 737-8 MAX` — é o que aparece no seletor |
| 3 | `envergadura_m` | Número | Sim | 2 casas decimais |
| 4 | `ordem` | Número | Sim | 0 casas — ordem no seletor |
| 5 | `ativo` | Número | Sim | `1` ativo · `0` fora de uso, some do seletor sem quebrar registro antigo |

> **`equip` é chave, mas o SharePoint não a protege.** O contrato do `List_Generator` não carrega
> `EnforceUniqueValues`, então duplicata entra sem reclamar — e aí o `LookUp` devolve a primeira, e a
> checagem passa a depender da ordem de inserção. Quem tem que impedir duplicata é a tela de cadastro.
> Se um dia aparecer envergadura errada sem explicação, procure código repetido aqui primeiro.

---

## 2. `tb_regrasPosicao` — proibições enumeradas

Uma forma só para os dois casos: **é proibido ter `equip_a` em `posicao` junto de `equip_b` em
`vizinha`**. Com `vizinha` vazia, a proibição é da própria posição.

| # | Nome interno | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|
| 1 | `aeroporto` | Texto (uma linha, 60) | Sim | **Indexada** — `NAVEGANTES`, o **nome**, nunca o ICAO |
| 2 | `posicao` | Texto (uma linha) | Sim | **Indexada** — código da posição, `T4` |
| 3 | `equip_a` | Texto (uma linha, 255) | Sim | códigos separados por vírgula: `E295` ou `B738,B38M` |
| 4 | `vizinha` | Texto (uma linha) | Não | **vazio = regra da própria posição** · preenchido = regra de par |
| 5 | `equip_b` | Texto (uma linha, 255) | Não | só para regra de par |
| 6 | `mensagem` | Várias linhas (texto simples) | Sim | o texto que o operador lê quando o salvar é recusado |
| 7 | `ativo` | Número | Sim | `1` / `0` — desligar regra sem apagar histórico |

### Exemplos

```
| aeroporto | posicao | equip_a     | vizinha | equip_b     | mensagem                                          |
| NAVEGANTES | T4      | E295        |         |             | T4 não recebe E195-E2.                            |
| NAVEGANTES | T3      | B738,B38M   | T4      | B738,B38M   | T3 e T4 não comportam dois 737 ao mesmo tempo.    |
| NAVEGANTES | T4      | B738,B38M   | T5      | B738,B38M   | T4 e T5 não comportam dois 737 ao mesmo tempo.    |
```

> **`equip_a` e `equip_b` são Texto e não Nota de propósito.** Validação de lista do SharePoint **não
> enxerga coluna de várias linhas**. Como Texto, a lista consegue recusar sozinha uma regra de par pela
> metade — `vizinha` preenchida com `equip_b` vazio, que é uma regra que nunca dispara e se parece com
> *nenhuma regra*. A validação está em `validacaoLista` no JSON.

> **A regra de par é testada nos dois sentidos.** Uma linha `T3 → T4` também pega o caso de gravar em
> T4 com T3 já ocupada. Não cadastre a recíproca: a mensagem sairia duplicada.

> **Por que enumerar par a par em vez de deduzir vizinhança.** A coluna `ordem` de `colPosicoes` é
> **ordem visual da planilha**, não posição física — no pátio 3 a sequência é `A6, 7, A10, A7, A8, …`,
> e `A6` não faz fronteira com `7`. Deduzir vizinhança dali produziria regra errada em silêncio. Quem
> escreve a regra declara o par, e o pátio principal inteiro sai em 6 linhas.

> **A regra só vale quando as duas ocupações se cruzam no tempo.** Isso sai de graça: o `SALVAR` já
> monta `colValida` com tudo que cruza o período, em minutos absolutos.

---

## 3. `equipamento` em `tb_alocacoesMapa`

| # | Nome interno | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|
| 19 | `equipamento` | Texto (uma linha) | **Não** | código de `tb_equipamentos.equip` |

> **Opcional no SharePoint, obrigatório no app, e essa diferença é proposital.** Marcar como
> obrigatória na lista quebraria todo registro já existente, que não tem equipamento nenhum. Quem
> exige é o app, e só para `tipo_registro = "VOO"` — interdição e reserva não têm aeronave. O acervo
> antigo vai sendo preenchido conforme cada registro é editado.

---

## Ordem de implantação — não pode ser trocada

A tela nova exige o equipamento para gravar voo, e o seletor de equipamento vem de `tb_equipamentos`.
**Com o catálogo vazio, ninguém consegue salvar voo nenhum.** Então:

1. Criar `tb_equipamentos` e **preencher** com todos os modelos que operam no aeroporto.
2. Criar a coluna `equipamento` em `tb_alocacoesMapa` — como opcional.
3. Criar `tb_regrasPosicao`. Pode começar **vazia**: sem regra cadastrada, nada é proibido, e a
   checagem por envergadura continua valendo sozinha.
4. Preencher `env_max` em `colPosicoes`, no `App.Formulas`. **Hoje está `0` em todas as 25 posições**,
   e `0` significa *sem limite* — a checagem de envergadura que já existe na tela nunca disparou.
5. **Acrescentar `tb_equipamentos` e `tb_regrasPosicao` como fontes de dados do app** (Dados →
   Adicionar dados → SharePoint). Sem isso o Studio recusa a tela inteira: os dois nomes não existem
   para ele, e o erro aparece como nome não reconhecido, não como fonte faltando.
6. Só então colar `App.Formulas` e a tela.
7. Cadastrar as regras de `tb_regrasPosicao` com o app já rodando, uma a uma, testando cada uma.

> **O passo 4 é o que quase passou batido.** A validação de envergadura está no `SALVAR` desde a
> primeira versão e é inofensiva por falta de dado. Preencher `env_max` **liga** uma regra que nunca
> rodou em produção: revise os valores antes, porque a partir dali ela recusa gravação.
