# Estrutura das listas SharePoint — Gestão de Chamados (Onda 1 a 3)

Complementa [ARQUITETURA_CHAMADOS.md](ARQUITETURA_CHAMADOS.md). Aqui está o que
criar, com nome interno, tipo e configuração.

---

## ⚠️ Leia antes de criar a primeira coluna à mão

> Vale para `tbl_ServiceDesk` e `User`, que já existem. As listas novas saem do
> `List_Generator` e não passam por este procedimento.

O **nome interno** da coluna é congelado na criação e **nunca mais muda**. Criar
já com o nome bonito faz o SharePoint codificar acento e espaço, e o resultado
entra em todo `Patch` e `DataField` do app para sempre:

```
"Data de Conclusão"  →  Data_x0020_de_x0020_Conclus_x00e3_o
```

### Procedimento obrigatório para CADA coluna

1. **+ Adicionar coluna** → escolher o tipo → digitar **exatamente o nome interno**
   (minúsculo, `snake_case`, sem acento, sem espaço): `desk_data_conclusao`
2. **Salvar.**
3. Cabeçalho da coluna → **Editar** → trocar para o nome de exibição:
   `Data de Conclusão` → Salvar.

Conferir depois em Configurações da lista → clicar na coluna → olhar a URL:
`...FldEdit.aspx?List={...}&Field=desk_data_conclusao`. Qualquer `_x00` significa
coluna para **excluir e recriar**. Não tem conserto.

### Neutralizar a coluna `Título` — nas listas criadas à mão

A coluna nativa `Título` (interno `Title`) **não é usada neste sistema**. Antes de
gravar o primeiro item:

1. Configurações da lista → Configurações avançadas → *Permitir gerenciamento de
   tipos de conteúdo?* → **Sim** → OK.
2. Bloco **Tipos de conteúdo** → **Item** → **Título** → marcar **Oculto** → OK.
3. Devolver *Permitir gerenciamento de tipos de conteúdo?* para **Não**.
4. Remover `Título` de **todas as views**.

> Se **Oculto** for recusado, marque **Opcional** e tire das views. Para o app o
> efeito é o mesmo: `Patch` sem `Title` grava sem erro.

### Nenhuma coluna Sim/Não

Lição registrada em `LICOES_APRENDIDAS_POWERAPPS_YAML.md`: Sim/Não do SharePoint
chega ao app como `true`/`false`/**branco**, e `!Coluna` não é o mesmo que
`Coluna <> true`. Toda flag deste módulo é **Texto** com literal explícito
(`"SIM"` / `"NAO"`).

---

# Lista 1 — `tbl_ServiceDesk` (MESTRE, já existe)

## 1.1 Colunas que já existem

| Nome interno | Tipo atual | Ação |
|---|---|---|
| `desk_id` | Número | manter — **indexar** se ainda não estiver |
| `desk_categoria` | Escolha | **converter para Texto (uma linha)** — ver ARQUITETURA §6 |
| `desk_usuario` | Pessoa | manter (exibição e e-mail do formulário) |
| `desk_descricao` | Texto (várias linhas) | manter |
| `desk_status` | Texto | manter — **indexar** |
| `Anexos` | Anexos nativo | manter |

## 1.2 Colunas novas — Onda 1 (recorte por usuário)

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 1 | `desk_solicitante_email` | E-mail do Solicitante | Texto (uma linha) | Não ⚠️ | **Indexada.** Espelho de `desk_usuario.Email`. É a coluna do recorte delegável |
| 2 | `desk_ciclo` | Ciclo | Texto (uma linha) | Não | `SUPORTE` ou `DEMANDA`. Resolvido pela categoria em `App.Formulas` |
| 3 | `desk_categoria_chave` | Chave da Categoria | Texto (uma linha) | Não | `RESET_SENHA`, `NOVO_MODULO`… Literal estável, imune a mudança de rótulo |
| 4 | `desk_prioridade` | Prioridade | Texto (uma linha) | Não | `CRITICA`, `ALTA`, `MEDIA`, `BAIXA`. Padrão `MEDIA` |
| 5 | `desk_data_conclusao` | Data de Conclusão | Data e Hora | Não | Preenchida ao entrar em `Resolvido`/`Entregue`. **Não** existe nativa: `Modificado` é a última edição de qualquer coisa |

### O que NÃO se cria porque já existe nativo

| Nativa | Substitui | Onde é usada |
|---|---|---|
| `Created` (*Criado*) | uma coluna `desk_data_abertura` | data de abertura na lista e no detalhe |
| `Author` (*Criado por*) | — | auditoria de quem gravou pelo Studio/SharePoint |
| `Modified` (*Modificado*) | — | auditoria |

Criar coluna para o que o SharePoint já entrega é campo a mais para o app lembrar
de preencher, e mais uma chance de ficar nulo. `Created` é gravado sozinho, é
`Data e Hora`, e é **delegável** para filtro e ordenação.

> ⚠️ **Nenhuma coluna nova é obrigatória.** A tela de abertura atual não as grava
> ainda; torná-las obrigatórias agora quebra o formulário em produção. Elas passam
> a ser preenchidas no passo 6 da migração.

### Por que `Criado por` não substitui `desk_solicitante_email`

Dois motivos, e o primeiro sozinho já decide:

1. **`Author` é campo Pessoa e Pessoa não delega.** `Filter(tbl_ServiceDesk;
   'Criado por'.Email = X)` é avaliado só sobre as primeiras 500 linhas. A lista
   já passou de 1.100 itens — o usuário veria um recorte truncado **sem nenhum
   aviso**. É exatamente o motivo de não usar `desk_usuario.Email` também.
2. **`Author` é a conta AAD da sessão, não o usuário do AirPort Now.** A
   identidade deste app é o registro da lista `User` (`Usuarios`/`Senha`), e
   `desk_usuario` é escolhido no formulário — pode ser outra pessoa que não quem
   está com o app aberto. Recortar por `Author` mostraria "os chamados que esta
   conta digitou", não "os meus chamados".

> ⚠️ **`ScreenMeusChamados` também lê três colunas das ondas seguintes:**
> `desk_atendente_nome`, `desk_solucao` e `desk_motivo_recusa`. Crie as três **junto com a Onda 1**, mesmo que só passem a ser
> preenchidas depois. Coluna existente e vazia não quebra nada; coluna
> **inexistente derruba a tela inteira** ao colar no Studio.

## 1.3 Colunas novas — Onda 2 (atendimento)

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 8 | `desk_atendente_email` | E-mail do Atendente | Texto (uma linha) | Não | **Indexada.** Quem assumiu. Branco = na fila |
| 9 | `desk_atendente_nome` | Atendente | Texto (uma linha) | Não | Espelho |
| 10 | `desk_data_primeira_resposta` | Primeira Resposta | Data e Hora | Não | Carimbo do 1º movimento do atendente — mede o SLA de resposta |
| 11 | `desk_solucao` | Solução Aplicada | Texto (várias linhas) | Não | O que foi feito. Vai no e-mail de resolução |
| 12 | `desk_data_limite` | Prazo SLA | Data e Hora | Não | Calculado na abertura a partir da prioridade |

## 1.4 Colunas novas — Onda 3 (ciclo de demanda)

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 13 | `desk_etapa` | Etapa | Número | Não | 1 a 7 do roteiro de acompanhamento. Alimenta a barra de progresso |
| 14 | `desk_aprovador_email` | E-mail do Aprovador | Texto (uma linha) | Não | Quem aprovou/reprovou a demanda |
| 15 | `desk_data_aprovacao` | Data da Aprovação | Data e Hora | Não | |
| 16 | `desk_previsao_entrega` | Previsão de Entrega | Data | Não | Definida na aprovação, não na abertura |
| 17 | `desk_motivo_recusa` | Motivo da Recusa | Texto (várias linhas) | Não | Obrigatório na tela quando o status vira `Reprovado` |

## 1.5 Configuração da lista mestre

- **Versionamento:** ativar, 50 versões. Fazer **antes** de qualquer carga.
- **Anexos:** já habilitados, manter.
- **Índices:** `desk_id`, `desk_solicitante_email`, `desk_status`,
  `desk_atendente_email`. Criar **antes** de a lista passar de 5.000 itens —
  depois disso o SharePoint recusa criar índice.
- **Views:** `Fila` (status abertos, ordenado por `desk_data_limite`),
  `Demandas` (ciclo = DEMANDA), `Todos`. Nenhuma com `Título`.

---

# Lista `User` — uma única coluna nova (Onda 2)

O módulo de chamados **não altera nenhuma coluna existente de `User`** e não
reaproveita `Autorizacao` nem `Perfil`. Acrescenta uma só:

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 1 | `usr_papel_chamados` | Papel nos Chamados | Texto (uma linha) | Não | `GESTOR` ou `ATENDENTE`. **Em branco = solicitante** |

Deixe em branco para todo mundo e preencha só para quem opera o service desk.
Nenhum outro módulo lê essa coluna, e nenhuma outra tela do app precisa mudar —
a tela de detalhe lê de `userRecord`, que o Login já preenche.

---

# Listas 2 e 3 — geradas pelo `List_Generator` (Onda 2)

As duas listas de apoio **não são criadas à mão**: saem do gerador de listas do
projeto, pelos JSONs em [tb_chamadoHistorico.json](tb_chamadoHistorico.json) e
[tb_chamadoInteracao.json](tb_chamadoInteracao.json). O fluxo cria a lista com
versionamento (50 versões), neutraliza o `Title`, cria as colunas com o nome
interno garantido e acrescenta cada uma à view padrão.

Isso muda três convenções em relação ao rascunho anterior deste documento:

| Convenção do gerador | Efeito aqui |
|---|---|
| nome da lista `tb_` + camelCase | `tb_chamadoHistorico`, `tb_chamadoInteracao` — **não** `tb_chamadoHistorico` |
| chave estrangeira `id_fk_<entidade>` | `id_fk_chamado`, não `desk_id` |
| um só campo por pessoa, guardando o e-mail | `autor_email` — as colunas `*_autor_nome` deixaram de existir; a tela mostra o prefixo do e-mail |
| flag é `Number` com 1/0, nunca Sim/Não nem texto | `interna` é `1`/`0` |
| não duplicar coluna nativa | `Created` é a data do evento — não existe `hist_data` nem `int_data` |

## `tb_chamadoHistorico` — 5 colunas

| # | Nome interno | Tipo | Obrig. | Configuração |
|---|---|---|---|---|
| 1 | `id_fk_chamado` | Number (0 decimais, min 1) | **Sim** | **Indexada** |
| 2 | `status_de` | Text (40) | Não | Branco na abertura |
| 3 | `status_para` | Text (40) | **Sim** | **Indexada** |
| 4 | `autor_email` | Text (120) | **Sim** | **Indexada** |
| 5 | `observacao` | Note (sem rich text) | Não | Motivo da transição |

A data e a hora do evento são a coluna nativa `Created`.

## `tb_chamadoInteracao` — 5 colunas

| # | Nome interno | Tipo | Obrig. | Configuração |
|---|---|---|---|---|
| 1 | `id_fk_chamado` | Number (0 decimais, min 1) | **Sim** | **Indexada** |
| 2 | `autor_email` | Text (120) | **Sim** | **Indexada** |
| 3 | `autor_papel` | Text (20) | Não | `solicitante` ou `atendente` |
| 4 | `mensagem` | Note (sem rich text) | Não | |
| 5 | `interna` | Number (0 decimais) | Não | `1` = nota entre atendentes; branco e `0` valem o mesmo |

O gerador cria a lista com anexos **desabilitados**. Se a conversa precisar de
anexo, habilite manualmente depois — é a única coisa fora do JSON.

### Por que sem `<Default>` e sem `<Validation>`

A primeira versão deste JSON trazia valor padrão e regra de validação em
`autor_papel` e `interna`, e `mensagem` obrigatória. **O fluxo falhou.** O
`tb_chamadoHistorico`, que só usa `Text`, `Number` e `Note` sem elemento filho,
passou na mesma rodada — e essas eram as três únicas diferenças entre os dois
arquivos.

A regra que fica: **construção não comprovada num JSON que já rodou neste tenant
não entra**. É a mesma disciplina do dicionário de propriedades das telas.

Suspeita principal, ainda não confirmada: a fórmula de validação usa `;` como
separador (`=OU(...)`), que só vale em site **pt-BR**. Em site en-US é preciso
`=OR([interna]=0,[interna]=1)`. Confirmando o idioma do site, dá para devolver as
duas validações.

Nada disso muda o comportamento do app: `ScreenChamadoDetalhe` sempre grava
`autor_papel` e `interna` explicitamente, e nunca envia mensagem em branco. E o
filtro de nota interna usa `interna = 0`, que em Power Fx também casa com branco.

---

# Lista 4 — `tbl_ChamadoDemanda` (Onda 3)

Extensão **1-para-1** da mestre, só para o ciclo de demanda. Guarda as respostas
do roteiro de [ROTEIRO_NOVO_MODULO.md](ROTEIRO_NOVO_MODULO.md).

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Passo do roteiro |
|---|---|---|---|---|---|
| 1 | `desk_id` | Nº do Chamado | Número | **Sim** | **Indexada**, um registro por chamado |
| 2 | `dem_nome_modulo` | Nome do Módulo | Texto (uma linha) | **Sim** | 1 |
| 3 | `dem_area` | Área Solicitante | Texto (uma linha) | **Sim** | 1 |
| 4 | `dem_aeroportos` | Aeroportos Impactados | Texto (várias linhas) | **Sim** | 1 — siglas IATA separadas por `;`, ou `TODOS` |
| 5 | `dem_como_e_hoje` | Como é Feito Hoje | Texto (várias linhas) | **Sim** | 2 |
| 6 | `dem_ferramenta_atual` | Ferramenta Atual | Texto (uma linha) | **Sim** | 2 — Excel, papel, e-mail, outro sistema, nada |
| 7 | `dem_volume_mensal` | Volume Mensal | Número | Não | 2 — quantos registros por mês |
| 8 | `dem_tempo_gasto` | Tempo Gasto por Registro | Texto (uma linha) | Não | 2 |
| 9 | `dem_quem_executa` | Quem Executa Hoje | Texto (uma linha) | Não | 2 |
| 10 | `dem_o_que_registrar` | O Que Precisa Registrar | Texto (várias linhas) | **Sim** | 3 |
| 11 | `dem_quem_consulta` | Quem Consulta | Texto (várias linhas) | **Sim** | 3 |
| 12 | `dem_decisoes` | Decisões que Dependem | Texto (várias linhas) | Não | 3 |
| 13 | `dem_indicadores` | Indicadores Esperados | Texto (várias linhas) | Não | 3 |
| 14 | `dem_regulatorio` | Exigência Regulatória | Texto (uma linha) | **Sim** | 4 — `SIM`/`NAO` |
| 15 | `dem_norma` | Norma / Referência | Texto (uma linha) | Não | 4 — obrigatório na tela se item 14 = `SIM` |
| 16 | `dem_exige_evidencia` | Exige Evidência/Anexo | Texto (uma linha) | Não | 4 — `SIM`/`NAO` |
| 17 | `dem_exige_aprovacao` | Exige Aprovação no Fluxo | Texto (uma linha) | Não | 4 — `SIM`/`NAO` |
| 18 | `dem_patrocinador_email` | Patrocinador | Texto (uma linha) | **Sim** | 5 |
| 19 | `dem_prazo_desejado` | Prazo Desejado | Data | Não | 5 |
| 20 | `dem_impacto_sem` | Impacto se Não For Feito | Texto (várias linhas) | **Sim** | 5 |

- Anexos: **habilitados** (fluxograma, planilha modelo, print da tela atual).
- Versionamento: ativar, 20 versões.
- Índice em `desk_id`.

### Por que lista separada e não colunas na mestre

Vinte colunas que só valem para 4 das 10 categorias. Na mestre elas apareceriam
em todo formulário, em toda view e em toda consulta de suporte — e a lista mestre
é a que mais cresce. Separada, o custo é um `LookUp` por chamado de demanda, feito
só na tela de detalhe.

---

## Ordem de execução recomendada

1. Neutralizar `Título` em `tbl_ServiceDesk`.
2. Ligar versionamento em `tbl_ServiceDesk`.
3. Criar os índices que faltam na mestre.
4. Criar as 5 colunas da Onda 1 **mais** `desk_atendente_nome`, `desk_solucao` e
   `desk_motivo_recusa` — lidas pela tela de Meus Chamados. Oito no total.
5. Carga única do espelho `desk_solicitante_email` e do `desk_status` em branco → `Fechado`.
6. Converter `desk_categoria` de Escolha para Texto e preencher
   `desk_categoria_chave` nos registros existentes.
7. Publicar `App.Formulas` e ajustar `ScreenServiceDeskForm` (ARQUITETURA §6).
8. Publicar `ScreenMeusChamados`.
9. Onda 2: rodar o `List_Generator` com os dois JSONs, mais
   `desk_atendente_email` e `desk_data_primeira_resposta` na mestre — são as duas
   únicas colunas da Onda 2 que `ScreenChamadoDetalhe` grava. `desk_data_limite`
   só entra na onda 4, com os fluxos de SLA. Mais `usr_papel_chamados` em `User`.
10. Onda 3: lista 4, colunas 13–17 da mestre.

---

## Checklist de conferência

- [ ] Nenhum nome interno com `_x00` (conferir na URL de cada coluna).
- [ ] `Título` oculto e fora das views nas quatro listas.
- [ ] Nenhuma coluna Sim/Não em nenhuma das quatro listas.
- [ ] `desk_id` indexado nas quatro listas.
- [ ] `desk_solicitante_email` e `desk_status` indexados na mestre.
- [ ] Nenhuma coluna nova marcada como obrigatória na mestre antes do passo 7.
- [ ] Versionamento ligado na mestre e em `tbl_ChamadoDemanda`, desligado no histórico.
- [ ] Nenhuma coluna Pesquisa (Lookup) apontando para a mestre.
- [ ] Carga dos espelhos concluída **antes** de publicar `ScreenMeusChamados` —
      senão o usuário abre a tela e não vê o próprio histórico.
