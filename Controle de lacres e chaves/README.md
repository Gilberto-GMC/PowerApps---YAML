# Controle de Lacres e Chaves

Um app Canvas só, com **dois módulos** que compartilham `ScreenHome`, o `App.OnStart` e a base de
usuários. O de Chaves já existia; o de Lacres foi construído dentro dele.

Trabalhado em 08/09/2026 (Douglas + Claude). Veio do repositório local
`Documents/Projetos/Controle-de-Lacres`, commit `c59c3d0`.

## As telas

| Arquivo | Módulo | O que é |
|---|---|---|
| `ScreenHome.pa.yaml` | ambos | menu; três cartões de Chaves, três de Lacres |
| `ScreenChaves.pa.yaml` | Chaves | cadastro de chaves |
| `ScreenOperação.pa.yaml` | Chaves | retirada e devolução, **em lote desde 08/09** |
| `ScreenHistoricoOperacao.pa.yaml` | Chaves | histórico de movimentações |
| `scrPontoLacravelForm.pa.yaml` | Lacres | cadastro de pontos lacráveis |
| `ScreenOperaçãoLacres_new.pa.yaml` | Lacres | painel, KPIs, aplicação e rompimento |
| `ScreenHistoricoLacres.pa.yaml` | Lacres | histórico de lacres |

Não estão aqui e existem no app: `ScreenSucesso` e `ScreenHistoricoExtravio`.

## Modelo de dados

**Chaves** — `tbl_chave` (a chave; `ativo` é flag de extravio, não de empréstimo) e
`tbl_movimentacoes` (uma linha por chave por empréstimo). Não há estado de "disponível/emprestada" na
chave: ele é **derivado** de existir movimentação com `operacao = "Retirada"`. A devolução **atualiza
a própria linha** da retirada — não cria registro novo. `tbl_chave_extravio` liga-se à chave por
`id_chave` e à movimentação por `id_entrega`.

**Lacres** — `tbl_Pontos_Lacraveis` (o ponto físico) e `tbl_Lacres_Aplicacao`. O rompimento **não
tem lista própria**: é gravado no mesmo registro da aplicação. Um lacre em vigor é uma aplicação com
`Data_Rompimento` em branco.

## Duas coisas que não são óbvias no código

**O campo `Status` do ponto lacrável é opinião, não fato.** Ele é mantido por `Patch` do app. A tela
de operações **deriva** o estado da aplicação mais recente e não depende dele. O campo continua sendo
gravado porque o Power BI lê a coluna direto da lista.

**Ponto lacrável excluído é inativado, não apagado** (`Excluido = true`), quando já teve lacre.
Apagar de vez orfanaria as aplicações e deixaria a localização em branco no histórico e no Power BI.
Ponto que nunca teve lacre sai de verdade. Filtros usam `Excluido <> true`, que tolera branco — o
padrão da coluna **não** preenche itens que já existiam.

## Antes de mexer

Leia o `LICOES_APRENDIDAS_POWERAPPS_YAML.md` da raiz e o `AGENTS.md`. Três armadilhas que custaram
colagens nesta pasta especificamente:

1. **`OnSelect: =UpdateContext({var: false})` em escalar simples é YAML inválido.** O `: ` dentro do
   valor vira mapeamento e o Studio recusa a tela inteira. Tem que ser bloco `|-`.
2. **Coluna referenciada pelo nome lógico num lugar e pelo de exibição noutro não é inconsistência** —
   `'Criado por'` *é* o `Author`. "Corrigir" isso quebra o que funcionava.
3. **Container AutoLayout com filho de altura fixa precisa de `Height` próprio**, senão corta o
   último filho.

## Os documentos

- `EXCLUSAO_PONTO_LACRAVEL.md` — a exclusão de ponto lacrável e a regra em três estados.
- `ANALISE_LACRES.md` — auditoria do módulo de Lacres: delegação, inconsistências, o que fica lento
  quando a base crescer, e o que continua em aberto.
- `LOTE_CHAVES.md` — empréstimo e devolução de várias chaves de uma vez.

## Em aberto

- O fluxo do Power Automate que desliga `Alerta_Enviado` existe? O app só liga.
- A exclusão de ponto lacrável deve ter trava por perfil? Hoje qualquer um exclui, igual ao Editar.
- Alguma tela fora desta pasta lê `varUltimaAplicacao`? Se não, dá para remover duas consultas
  remotas por clique.
- Trava de número de lacre duplicado — lembrando que a numeração real admite faixa (`0032-0033`) e
  texto livre.
