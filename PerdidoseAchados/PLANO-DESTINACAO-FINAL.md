# Destinação final de itens não doáveis — plano

**Origem:** e-mail do Douglas à Mercia em 23/09/2026 com 7 pontos para definição;
resposta da **Carmen Mamani Orosco** em 09/10/2026 (14:47), com cópia para Angelica,
Mercia e GESTAO AIRPORTNOW.

**Problema que fecha:** o Airport Now tem caminho completo para doação — separação
após 90 dias, doação com instituição e data, encerramento do atendimento. Para o que
**não pode** ser doado, não há caminho. Os itens 5.13 e 5.16 do PRO proíbem doar
eletrônicos e documentos, e a tela de separação respeita a regra; mas Destruição e
Encaminhamento à Justiça nunca foram implementados. Na prática **um celular fica com
status "Recebido" para sempre**, e o item 5.17 diz que "a ausência de registro invalida
o processo de destinação".

---

## O que a Carmen decidiu, e o que ficou com ela

| # | Ponto | Resposta |
|---|---|---|
| 1 | Situação atual | ⏳ vai validar com os aeroportos como a destinação é conduzida hoje e se existe controle paralelo |
| 2 | Momento do registro | ✅ **registrar já na identificação da necessidade**, com status intermediário ("aguardando aprovação" ou "aguardando destinação"), rastreável até a destinação final efetivamente realizada |
| 3 | Perfil de acesso | ✅ restrito — ⏳ qual perfil, ela define internamente |
| 4 | Motivos do descarte | ✅ lista fechada: alíneas "a" a "j" do item 5.11 **mais** o 5.14 ("Não apresenta condições de doação") |
| 5 | Destruição | ✅ **Certificado de Destinação Final anexado** ao sistema; ela reconhece que acrescenta prazo |
| 6 | Justiça | ✅ lista pré-definida dos destinatários recorrentes **+ campo livre** |
| 7 | Categorias | ⏳ "precisará ser avaliado em conjunto" com as categorias e subcategorias do Airport Now |

O ponto 2 era o que mudava a estrutura da tela, e veio decidido. Os pontos 1, 3 e 7
continuam abertos, mas **nenhum deles bloqueia o desenvolvimento** — ver "O que fica
parametrizado" no fim.

---

## O que já existe no sistema

Levantado na `ScreenInventario` em 15/10/2026:

- **O `TabListDestinar` já tem as cinco abas**: `DESTINAR`, `DOAÇÃO`,
  `ENCAMINHAMENTO À JUSTIÇA`, `DESCARTE`, `DESTRUIÇÃO`.
- A coleção `col_itensDestinados` **já lê** `status = "Destruído"` e
  `status = "Encaminhado à Justiça"` (ScreenInventario.pa.yaml:505).
- **Ninguém nunca grava esses dois status.** As abas existem e sempre vêm vazias.

Ou seja: a metade de exibição está pronta. Falta a ação.

**Colunas que já existem em `tbl_perdidosAchadosItens`:** `status`, `recebido`,
`arquivar`, `perecivel`, `pessimas_condUso`, `sujeito_descarte`, `descarte`,
`descarte_usuario`, `doado_em`, `doado_usuario`, `doado_para`.

> **Não confundir `descarte` com destinação final.** O `descarte` de hoje é o
> **descarte imediato no cadastro** — perecível ou péssimas condições de uso, item
> 5.1.3 do PRO. Acontece na `ScreenCadastrar`, antes dos 90 dias. A destinação final
> é outro momento e outro fluxo. Reaproveitar aquelas colunas misturaria os dois.

**Perfil:** `varPerfilUser` vale `Sede` ou `Base` e controla troca de aeroporto.
Quem serve para restringir ação é o `varAutUser` (coluna `Autorizacao` da lista `User`),
que já tem o valor `Admin` em uso na `ScreenCadastrar:2391`.

---

## Ciclo de vida proposto

Hoje o item morre em `Recebido`. A proposta, seguindo a resposta 2 da Carmen e as
etapas do PRO (aprovação da Gerência do Aeroporto, condução pelo SGI Meio Ambiente):

```
Recebido
   |  agente identifica que o item nao e doavel
   v
Aguardando aprovacao      <- registro nasce aqui, com modalidade e motivo
   |  Gerencia do Aeroporto aprova
   v
Aguardando destinacao     <- aprovado, esperando execucao
   |  SGI Meio Ambiente executa e registra
   v
Destruido  |  Encaminhado a Justica
```

**Decisão em aberto:** dois status intermediários ou um só. A Carmen escreveu
"(por exemplo, aguardando aprovação ou aguardando destinação)" — o "ou" pode ser
alternativa ou enumeração. Dois status refletem as etapas do PRO e deixam explícito
de quem é a vez; um só é metade do trabalho de tela. **Precisa da decisão do Douglas.**

---

## Colunas novas em `tbl_perdidosAchadosItens`

Prefixo `dest_` para não colidir com o descarte imediato.

| Nome interno | Tipo | Preenchido em | Observação |
|---|---|---|---|
| `dest_modalidade` | Linha única de texto | identificação | `Destruição` ou `Encaminhamento à Justiça` — ComboBox, lista fechada |
| `dest_motivo` | Linha única de texto | identificação | lista fechada: 5.11 "a" a "j" + 5.14 |
| `dest_solicitado_em` | Data e Hora | identificação | |
| `dest_solicitado_por` | Linha única de texto | identificação | `varNomeUser` |
| `dest_aprovado_em` | Data e Hora | aprovação | |
| `dest_aprovado_por` | Linha única de texto | aprovação | |
| `dest_em` | Data e Hora | execução | a **data** do item 5.17 |
| `dest_usuario` | Linha única de texto | execução | o **responsável** do item 5.17 |
| `dest_destinatario` | Linha única de texto | execução | o **destinatário final** do 5.17; ComboBox com lista + digitação livre, conforme resposta 6 |
| `dest_certificado_num` | Linha única de texto | execução | número do Certificado de Destinação Final |
| `dest_obs` | Várias linhas de texto | qualquer etapa | |

**Não criar como coluna Escolha.** Este app não usa nenhuma coluna Choice do
SharePoint — toda lista fechada é texto alimentado por ComboBox. Uma Choice seria o
único campo tipo *record* do sistema e exigiria `.Value` em toda leitura.

**O anexo do certificado** (resposta 5) usa a coluna **Anexos** nativa do SharePoint,
via controle `AddMedia`, como a `foto` do item já faz. Não é coluna nova.

Os cinco dados que o item 5.17 exige ficam cobertos: identificação do objeto
(o próprio registro), modalidade (`dest_modalidade`), data (`dest_em`), responsável
(`dest_usuario`) e destinatário final (`dest_destinatario`).

---

## Alterações de tela

### `ScreenInventario` — onde a ação nasce

A aba `DESTINAR` hoje lista itens com `status = "Recebido"` e mais de 90 dias
(ScreenInventario.pa.yaml:428), e oferece o botão **Doar**. Acrescentar, ao lado dele,
**Destinação final**, visível só quando o item não for doável e o usuário tiver
autorização.

O botão abre um formulário no padrão do `FormItensDoar` já existente, pedindo
modalidade, motivo e observação, e grava o status intermediário.

As abas `DESTRUIÇÃO` e `ENCAMINHAMENTO À JUSTIÇA` passam a mostrar conteúdo pela
primeira vez. Acrescentar abas para os status intermediários, ou um filtro — depende
da decisão de um ou dois status.

### Aprovação e execução

Mesma tela, nas abas novas: o item aprovado muda de aba, e na execução abre o
formulário final com data, responsável, destinatário, número e anexo do certificado.

### `ScreenConsultListar`

O bloco de rastreabilidade (`HtmlTextRastreio`) ganha a linha da destinação quando
houver `dest_modalidade`. Mesma condição de hoje: se não há dado, não aparece.

---

## O que fica parametrizado, à espera dos pontos 1, 3 e 7

Nenhum dos três abertos impede começar, desde que fiquem **em um lugar só**:

- **Ponto 3 (perfil)** — a condição de visibilidade do botão sai de uma única
  fórmula. Enquanto a Carmen não define, vale `varAutUser = "Admin"`, que já é o
  precedente do app. Trocar depois é uma linha.
- **Ponto 7 (categorias não doáveis)** — hoje a regra de doação está espalhada nas
  telas. Levar a lista para o `App.Formulas`, como `catNaoDoaveis`, e consumir dali.
  Quando a Carmen fechar a lista, muda-se uma linha.
- **Ponto 1 (situação atual)** — pode revelar um controle paralelo em planilha que a
  tela precise refletir. Risco de retrabalho **baixo e localizado**: afetaria campos
  do formulário, não a estrutura.

---

## O que falta para começar

1. **O texto das alíneas "a" a "j" do item 5.11 do PRO.** A Carmen aprovou a lista
   fechada, mas o PRO não está neste repositório e eu não tenho o texto das alíneas.
   Sem isso não dá para montar o ComboBox de `dest_motivo`.
2. **Um ou dois status intermediários** (ver "Ciclo de vida proposto").
3. **Os destinatários recorrentes** da resposta 6 — Correios, Polícia Federal, quais
   mais? O campo livre cobre o resto, mas a lista precisa de um começo.

---

## Estimativa

O Douglas estimou à área **4 dias úteis, podendo chegar a 6**. As respostas da Carmen
empurram para o teto: o anexo do certificado (resposta 5) e o status intermediário
(resposta 2) eram justamente as duas condições que ele marcou como "conforme as
respostas abaixo".

| Etapa | Horas |
|---|---:|
| Colunas no SharePoint + conferência dos nomes internos | 0,5 |
| `App.Formulas`: `catNaoDoaveis`, motivos, destinatários | 1,0 |
| `ScreenInventario`: botão, formulário de identificação, abas novas | 6,0 |
| Aprovação e execução, com anexo do certificado | 5,0 |
| `ScreenConsultListar`: linha da destinação no rastreio | 1,0 |
| Validação do YAML e colagem no Studio | 2,0 |
| Testes do roteiro | 3,0 |
| Documentação (`AUDITORIA-TELAS.md`, `CONTEXTO-CODEX.md`) | 0,5 |
| **Total** | **19 h** ≈ 2,5 dias úteis |

Cabe nos 4 a 6 dias comunicados, com folga para uma rodada de ajuste com a área.
