# Destinação final de itens não doáveis — plano

**Origem:** e-mail do Douglas à Mercia em 23/09/2026 com 7 pontos para definição;
resposta da **Carmen Mamani Orosco** em 09/10/2026 (14:47), com cópia para Angelica,
Mercia e GESTAO AIRPORTNOW.

**Norma:** *Procedimento Perdidos e Achados 2026 VF – ASUR*, **Rev. 03**, lido na
íntegra em 15/10/2026.

> ## ✅ ENTREGUE EM 21/10/2026
>
> As tres etapas funcionando em tela, testadas pelo Douglas:
> `Recebido` → `Aguardando aprovação` → `Aguardando destinação` →
> `Destruído` / `Encaminhado à Justiça` / `Descartado`.
>
> Tres coisas que so apareceram na execucao e estao registradas em
> `LICOES_APRENDIDAS_POWERAPPS_YAML.md`: `{chave: valor}` em linha unica quebra a
> colagem (PA1001), `Multiline` nao e `MultiLine`, e **o List_Generator cria toda
> lista com anexos desligados** — foi preciso habilitar na mao para o Certificado
> de Destinacao Final funcionar.
>
> Continuam abertos com a area os pontos 1, 3 e 7 da tabela abaixo. Nenhum bloqueia:
> o perfil esta em `varPodeDestinar` e as categorias em `colCatDoaveis`, cada um numa
> linha so do `App.Formulas`.

**Problema que fecha:** o Airport Now tem caminho completo para doação — separação
após 90 dias, doação com instituição e data, encerramento do atendimento. Para o que
**não pode** ser doado, não há caminho. O item 5.13 proíbe doar eletrônicos e
documentos e a tela de separação respeita a regra; mas Destruição e Encaminhamento a
órgão público nunca foram implementados. Na prática **um celular fica com status
"Recebido" para sempre**, e o item 5.17 diz que "a ausência de registro invalida o
processo de destinação".

---

## O que a Carmen decidiu, e o que ficou com ela

| # | Ponto | Resposta |
|---|---|---|
| 1 | Situação atual | ⏳ vai validar com os aeroportos como a destinação é conduzida hoje e se existe controle paralelo |
| 2 | Momento do registro | ✅ **registrar já na identificação da necessidade**, com status intermediário, rastreável até a destinação final efetivamente realizada |
| 3 | Perfil de acesso | ✅ restrito — ⏳ qual perfil, ela define internamente |
| 4 | Motivos do descarte | ✅ lista fechada: alíneas "a" a "j" do item 5.11 **mais** o 5.14 ("Não apresenta condições de doação") |
| 5 | Destruição | ✅ **Certificado de Destinação Final anexado** ao sistema; ela reconhece que acrescenta prazo |
| 6 | Justiça | ✅ lista pré-definida **+ campo livre** → **decisão do Douglas em 15/10: só campo livre**, sem lista |
| 7 | Categorias | ⏳ "precisará ser avaliado em conjunto" com as categorias e subcategorias do Airport Now |

O ponto 2 era o único que mudava a estrutura da tela, e veio decidido. Os pontos 1, 3
e 7 continuam abertos e **nenhum bloqueia** — ver "O que fica parametrizado".

---

## Três coisas que a leitura do PRO corrigiu

**1. O item 5.11 é a lista do descarte IMEDIATO, não dos motivos de destinação final.**
O título é "OBJETOS PASSÍVEIS DE DESCARTE" e o texto diz "Está autorizado o descarte
imediato, após o devido registro de entrada no sistema". Como a pergunta 4 foi feita
citando o 5.11 e a Carmen aprovou, a lista vale — mas é bom saber que ela nasceu para
outro momento do processo. Na prática as dez alíneas descrevem *por que um objeto não
serve*, o que se aplica aos dois momentos.

**2. "Encaminhamento à Justiça" não é uma modalidade do PRO.** O item 5.12 lista
quatro: **Devolução ao Usuário, Doação, Descarte e Destruição**. O encaminhamento
aparece no 5.15, na lista de documentação comprobatória, como *"Encaminhamento a órgão
público: comprovante ou protocolo oficial de recebimento"*, e no 5.1.3:
*"Documentos pessoais serão encaminhados aos Correios, Polícia Federal ou órgão
competente"*.

> O app já tem a aba `ENCAMINHAMENTO À JUSTIÇA`. **Mantida**, porque é o termo que a
> operação usa e trocar agora quebraria o que já existe. Fica registrado que o termo
> do PRO é "encaminhamento a órgão público".

**3. Falta um campo que o PRO exige e ninguém pediu: o método.** O item 5.15 manda
registrar *"item, data, responsável e método aplicado"*, com exemplos "danificação
física, rompimento estrutural". Os cinco campos do 5.17 não incluem o método — são
duas exigências diferentes no mesmo procedimento. Entra como `metodo` na lista de destinação,
obrigatório só na modalidade Destruição.

*(Observação sobre o documento: o fluxo do 5.15 vai do passo 4 direto ao 6 — não existe
passo 5. Como a seção "Definições" que o §2.1 promete e o documento não traz.)*

---

## O que já existe no sistema

Levantado na `ScreenInventario` em 15/10/2026:

- **O `TabListDestinar` já tem as cinco abas**: `DESTINAR`, `DOAÇÃO`,
  `ENCAMINHAMENTO À JUSTIÇA`, `DESCARTE`, `DESTRUIÇÃO`.
- A coleção `col_itensDestinados` **já lê** `status = "Destruído"` e
  `status = "Encaminhado à Justiça"` (ScreenInventario.pa.yaml:505).
- **Ninguém nunca grava esses dois status.** As abas existem e sempre vêm vazias.

A metade de exibição está pronta. Falta a ação.

**Colunas que já existem em `tbl_perdidosAchadosItens`:** `status`, `recebido`,
`arquivar`, `perecivel`, `pessimas_condUso`, `sujeito_descarte`, `descarte`,
`descarte_usuario`, `doado_em`, `doado_usuario`, `doado_para`.

> **Não confundir `descarte` com destinação final.** O `descarte` de hoje é o
> **descarte imediato no cadastro** — perecível ou péssimas condições, item 5.11.
> Acontece na `ScreenCadastrar`, antes dos 90 dias. A destinação final é outro momento
> e outro fluxo. Reaproveitar aquelas colunas misturaria os dois.

**Perfil:** `varPerfilUser` vale `Sede` ou `Base` e controla troca de aeroporto. Quem
serve para restringir ação é o `varAutUser` (coluna `Autorizacao` da lista `User`), que
já tem o valor `Admin` em uso na `ScreenCadastrar:2391`.

---

## Ciclo de vida — dois status intermediários

**Decidido em 15/10/2026:** dois, e não um. A Carmen escreveu "(por exemplo, aguardando
aprovação ou aguardando destinação)"; o fluxo do item 5.15 do PRO resolve a ambiguidade,
porque são **duas mãos diferentes** entre a identificação e a execução:

| Passo do 5.15 | Quem | Vira qual status |
|---|---|---|
| 1. Identificação e relatório técnico | Operações | `Aguardando aprovação` |
| 2. Aprovação formal da destinação | **Gerência do Aeroporto** | `Aguardando destinação` |
| 3-4. Análise, planejamento, coleta e execução | **SGI Meio Ambiente** + fornecedor licenciado | — |
| 6-7. Consolidação, CDF e registro | SGI Meio Ambiente | `Destruído` / `Encaminhado à Justiça` / `Descartado` |

```
Recebido
   |  agente identifica que o item nao e doavel
   v
Aguardando aprovacao      <- nasce aqui, com modalidade e motivo
   |  Gerencia do Aeroporto aprova
   v
Aguardando destinacao     <- aprovado, com o SGI Meio Ambiente
   |  fornecedor executa; SGI valida e registra
   v
Destruido | Encaminhado a Justica | Descartado
```

Um status só juntaria a Gerência e o SGI na mesma caixa, e aí o sistema não saberia
dizer de quem é a vez — que é justamente o que o 5.17 quer rastreável.

---

## Onde os dados moram — lista separada, nao colunas no item

**Decidido em 20/10/2026, por proposta do Douglas.** A primeira versao deste plano
punha treze colunas `dest_` em `tbl_perdidosAchadosItens`. Medicao que derrubou a
ideia: **sete telas coletam de 1200 a 1500 linhas da lista de itens, e nenhuma usa
`ShowColumns`.**

| Tela | Coleção | Linhas |
|---|---|---|
| `ScreenCadastrar` | `col_itensCadastradosBase` | 1200 |
| `ScreenConsultListar` | `col_itensPAconsultaBase` | 1200 |
| `ScreenEntregaListar` | `col_itensPAconsultaBase` | 1200 |
| `ScreenEntregaRecibo` | `colItensEntregaReciboBase` | 1500 |
| `ScreenInventario` | `colInventarioItensBase` | 1500 |
| `ScreenInventarioDoacao` | `colItensComDataDevBase` | 1500 |
| `ScreenInventarioSeparar` | `colItensComDataBase` | 1500 |

Sem projecao de colunas, **toda coluna nova viaja 1500 vezes em cada abertura de cada
uma dessas telas** — inclusive nas seis que nunca vao ler nada de destinacao. Treze
colunas seriam cerca de 19.500 valores a mais por abertura, num app que ja e dos
maiores da casa.

Pior: as colunas seriam quase todas vazias. So o item que chega ao fim da guarda sem
ser doado tem destinacao.

### A lista

`tbl_perdidosAchadosDestinacao` — **uma linha por tentativa de destinacao**, definida
em [lista_tbl_perdidosAchadosDestinacao.json](lista_tbl_perdidosAchadosDestinacao.json).

| Coluna | Tipo | Etapa |
|---|---|---|
| `ID_item` | Número, **indexada**, obrigatória | chave para `tbl_perdidosAchadosItens.ID` |
| `aeroporto` | Texto, **indexada** | denormalizado, para filtrar sem join |
| `modalidade` | Texto | identificação |
| `motivo` | Texto | identificação |
| `solicitado_em` / `solicitado_por` | Data e Hora / Texto | identificação |
| `aprovado_em` / `aprovado_por` | Data e Hora / Texto | aprovação |
| `destinado_em` / `destinado_por` | Data e Hora / Texto | execução |
| `destinatario` | Texto | execução — campo livre |
| `metodo` | Texto | execução — o "método aplicado" do 5.15 |
| `certificado_num` / `mtr` | Texto | execução |
| `obs` | Várias linhas | qualquer |
| `arquivar` | Número, padrão 0 | idiom do app |

**O `status` continua no item**, porque e ele que alimenta as abas e os filtros que ja
existem. A lista de itens ganha **zero colunas**.

**O Certificado de Destinacao Final** vai no anexo nativo desta lista, nao na de itens.

### O que se ganha de quebra

Uma tentativa de destinacao que nao vinga — aprovacao negada, item que volta para a
guarda — vira **outra linha**, com historico. Treze colunas no item nao conseguiriam
expressar isso: a segunda tentativa sobrescreveria a primeira, e o 5.17 pede
rastreabilidade do processo, nao so do desfecho.

E converge com a ferramenta: o fluxo `List_Generator` **so cria lista nova** e se
recusa a mexer em lista existente (ver "Cuidado com o List_Generator"). Lista nova e
exatamente o caminho que ele sabe fazer.

### O que custa

**Duas gravacoes por transicao** em vez de uma: o registro na lista de destinacao e o
`status` no item. Ordem obrigatoria — **primeiro o registro, depois o status**. Se a
segunda falhar, sobra um registro sem mudanca de status: detectavel e repetivel. Na
ordem inversa, o item ficaria com status de destinacao e nenhum registro, que e
exatamente o que o 5.17 chama de processo invalido.

Mais uma fonte de dados e mais uma colecao — mas pequena, entao cabe inteira num
`ClearCollect` sem preocupacao de delegacao.

---

## Cuidado com o List_Generator

O fluxo foi lido em 20/10/2026 (`List_Generator_v2.zip`). A primeira acao depois do
`Parse_Definicao` e `HTTP_Verificar_Lista`, seguida de `Condicao_Lista_Ja_Existe`:

> Se a lista ja existe, o fluxo **termina com falha** e a mensagem
> *"Ja existe uma lista chamada X. O fluxo nao altera lista existente: exclua a lista
> e rode de novo."*

**Nao ha risco de perda de dado em rodar o fluxo** — ele para antes de tocar em
qualquer coisa. **O risco esta em obedecer a mensagem de erro:** excluir a lista e
rodar de novo apagaria todo o historico de Perdidos e Achados.


## Alterações de tela

### `ScreenInventario` — onde a ação nasce

A aba `DESTINAR` hoje lista itens com `status = "Recebido"` e mais de 90 dias
(ScreenInventario.pa.yaml:428) e oferece o botão **Doar**. Acrescentar ao lado
**Destinação final**, visível quando o item não for doável e o usuário tiver
autorização.

O botão abre um formulário no padrão do `FormItensDoar`, pedindo modalidade, motivo e
observação, e grava `Aguardando aprovação`.

Duas abas novas, `AGUARDANDO APROVAÇÃO` e `AGUARDANDO DESTINAÇÃO`, com o botão da
etapa seguinte. As abas `DESTRUIÇÃO` e `ENCAMINHAMENTO À JUSTIÇA`, hoje mortas, passam
a mostrar conteúdo.

### `ScreenConsultListar`

O bloco de rastreabilidade (`HtmlTextRastreio`) ganha a linha da destinação quando
houver registro de destinação para o item. Mesma condição de hoje: sem dado, não aparece.

---

## O que fica parametrizado, à espera dos pontos 1, 3 e 7

- **Ponto 3 (perfil)** — a visibilidade do botão sai de uma fórmula só. Até a Carmen
  definir, vale `varAutUser = "Admin"`, que já é o precedente do app.
- **Ponto 7 (categorias não doáveis)** — levar a lista para o `App.Formulas`, como
  `catNaoDoaveis`, e consumir dali. O 5.13 e o 5.16 já dão a base: eletrônicos
  (celulares, tablets, notebooks, smartwatches, HDs) e documentos.
- **Ponto 1 (situação atual)** — pode revelar um controle paralelo em planilha que a
  tela precise refletir. Risco **baixo e localizado**: afetaria campos do formulário,
  não a estrutura.

---

## Fora de escopo, registrado

O 5.1.3 fixa **prazos de guarda diferenciados** — medicamentos até 3 dias, perecíveis
descarte imediato — e a tela de separação aplica 90 dias para tudo. Já estava anotado
como lacuna e continua fora desta entrega.

---

## Estimativa

O Douglas estimou à área **4 dias úteis, podendo chegar a 6**. As respostas da Carmen
empurram para o teto: o anexo do CDF e o status intermediário eram as duas condições
que ele marcou como "conforme as respostas abaixo".

| Etapa | Horas |
|---|---:|
| Lista nova pelo List_Generator + conferência dos nomes internos | 0,5 |
| `App.Formulas`: `catNaoDoaveis`, motivos, modalidades | 1,0 |
| `ScreenInventario`: botão, formulário de identificação, duas abas novas | 7,0 |
| Aprovação e execução, com anexo do CDF | 5,0 |
| `ScreenConsultListar`: linha da destinação no rastreio | 1,0 |
| Validação do YAML e colagem no Studio | 2,0 |
| Testes do roteiro | 3,0 |
| Documentação (`AUDITORIA-TELAS.md`, `CONTEXTO-CODEX.md`) | 0,5 |
| **Total** | **20 h** ≈ 2,5 dias úteis |

Cabe nos 4 a 6 dias comunicados, com folga para uma rodada de ajuste com a área.
