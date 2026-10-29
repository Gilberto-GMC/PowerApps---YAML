# Perdidos e Achados — o que mudou e como usar

Roteiro para apresentar à área. Cobre as entregas de setembro e outubro de 2026:
rastreabilidade do achado, destinação final de itens não doáveis e exportação
para Excel.

> **Estado em 29/10/2026:** tudo colado no Studio, nada testado com dado real
> ainda. Não prometer data de liberação.

---

## 1. Rastreabilidade — quem encontrou o objeto

**Onde:** tela de Cadastro, no formulário do atendimento.

Atende à sugestão do gerente Silvio e ao item 5.18 do PRO, que manda perguntar ao
declarante o local, a data e o horário do achado.

**Quatro campos novos:**

| Campo | Obrigatório? |
|---|---|
| Declarante (quem encontrou) | não |
| Empresa/organização do declarante | não |
| Tipo de origem | não — lista de 10 opções, sem digitação livre |
| **Data/hora da localização** | **sim** |

As dez opções de origem, aprovadas pela Carmen em 09/10: Agente de
Atendimento/Aeroporto, Supervisão SPO, Supervisão SPE, APAC, Limpeza /
Conservação / Facilities, Segurança patrimonial, Companhia aérea, Cessionário /
Permissionário, Passageiro / Público em geral, Outros.

**Três rótulos mudaram de nome**, para separar o achado da entrega:

| Antes | Agora |
|---|---|
| Data do Registro | Data/hora da **entrega à ASUR** |
| Entregue por | **Entregue à ASUR por** |
| Operador do sistema | **Agente ASUR que recebeu** |

> **Avisar a operação:** a *Data/hora da localização* é obrigatória. Ao **editar**
> um atendimento antigo, que não tem esse campo preenchido, o sistema vai exigir
> preenchê-lo antes de salvar. É o comportamento correto pelo item 5.1.1 do PRO,
> mas pega de surpresa quem abre um registro só para corrigir outra coisa.

---

## 2. Consulta — a cadeia completa do objeto

**Onde:** tela de Consulta, clicando em cima de um atendimento.

Abre um bloco mostrando as três etapas:

```
Achado:            declarante | empresa | origem | local | data e hora
Entrega à ASUR:    data e hora | entregue por | recebido por
Destinação final:  item 42 — Destruição | 21/10 | Fulano → empresa X | CDF 12345
```

A terceira linha só aparece quando o item passou pela destinação final.

**Atendimento antigo não mostra o bloco.** Se nenhum dos campos de rastreabilidade
estiver preenchido, ele nem abre — em vez de exibir uma fileira de traços.

---

## 3. Destinação final — o caminho do que não pode ser doado

**Onde:** tela de Inventário.

Resolve um buraco do sistema: os itens 5.13 e 5.16 do PRO proíbem doar
eletrônicos e documentos, e a tela de separação respeitava a regra — mas não
havia caminho nenhum para esses itens. Na prática um celular ficava com status
"Recebido" para sempre, e o item 5.17 diz que *a ausência de registro invalida o
processo de destinação*.

O Inventário agora tem **três abas, e cada uma é uma etapa com responsável
diferente**, seguindo o fluxo do item 5.15:

### Aba DESTINAR — o agente identifica

Lista os itens com mais de 90 dias que **não podem ser doados**. Para os doáveis
aparece o botão de doação normal; para os não doáveis, o botão **Destinar**.

Ao clicar, preenche:
- **Modalidade** — Destruição, Encaminhamento à Justiça ou Descarte
- **Motivo** — lista fechada de 11 opções: as alíneas "a" a "j" do item 5.11 mais
  "Não apresenta condições de doação" do 5.14
- **Observação** — livre

O item sai do inventário e entra na fila da Gerência.

### Aba AGUARDANDO APROVAÇÃO — a Gerência do Aeroporto decide

Dois botões: **Aprovar**, que manda o item para o SGI Meio Ambiente, e
**Cancelar**, que devolve o item para a guarda e arquiva o pedido.

O Cancelar existe para o caso de marcação por engano. Depois da aprovação ele
some — a partir daí o processo já está com o SGI e desfazer pelo app seria mentir
sobre o que aconteceu.

### Aba AGUARDANDO DESTINAÇÃO — o SGI Meio Ambiente registra

Botão **Registrar**, que abre o formulário final:

- Data da destinação e responsável pela execução *(obrigatórios)*
- Destinatário final — campo livre: Correios, Polícia Federal, empresa contratada
- **Método aplicado** — só aparece na Destruição, porque é o que o item 5.15 exige
- Número do Certificado de Destinação Final e MTR
- **Anexo do Certificado**

Gravado, o item recebe o desfecho — Destruído, Encaminhado à Justiça ou
Descartado — e passa a aparecer na Consulta, com a linha de destinação.

> **Acesso restrito.** Hoje só quem tem perfil de administrador vê esses botões.
> É o ponto 3 que ficou com a área: assim que definirem o perfil correto, a troca
> é imediata.

> **Nada é gravado pela metade.** O registro da destinação é sempre gravado antes
> do status do item mudar. Se a gravação falhar, o item não muda de estado e a
> ação pode ser repetida — nunca fica um item marcado como destruído sem registro,
> que é exatamente o que o item 5.17 chama de processo inválido.

---

## 4. Exportação para Excel

**Onde:** nas duas telas da doação — *Separar itens para doação* e *Itens
separados para doação*.

Atende ao pedido da Carmen de 20/10: uma planilha dos itens elegíveis e outra dos
já separados.

**Como usa:**

1. Filtre a tela como quiser — categoria, subcategoria, período, busca.
2. **Marque os itens** que devem entrar na planilha.
3. Clique em **Exportar Excel**. O botão fica cinza enquanto nada estiver marcado.
4. O status aparece ao lado: *Na fila* → *Gerando o arquivo* → *N item(ns) no
   arquivo*.
5. Clique em **Baixar**.

A planilha traz item, data, categoria, subcategoria, marca, descrição, dias em
custódia e aeroporto. Abre direto no Excel, com os acentos corretos.

> **Só vai o que estiver marcado.** Foi decisão de projeto: dá controle ao
> supervisor sobre o que entra na relação que ele envia.

---

## 5. O que ainda depende da área

Três pontos da resposta da Carmen de 09/10 continuam em aberto. **Nenhum impede o
uso** — cada um é um ajuste de uma linha quando a definição chegar.

1. **Situação atual nos aeroportos** — como a destinação de eletrônicos e
   documentos é conduzida hoje, e se existe controle paralelo em planilha. Se
   existir, a tela deve refletir o processo real.
2. **Perfil de acesso** — qual perfil pode executar e registrar a destinação.
   Hoje está no perfil de administrador.
3. **Categorias não doáveis** — avaliar em conjunto, olhando a parametrização do
   Airport Now. Hoje o sistema trata como não doável tudo que não está na lista de
   categorias liberadas, o que na prática exclui Documentos, Eletrônicos e
   Financeiro.

---

## 6. O que dizer sobre prazo

Tudo acima está construído e colado no ambiente, **mas nada foi testado com
movimento real** até 29/10/2026. Faltam:

- o ciclo completo Destinar → Aprovar → Registrar com um item de verdade;
- a exportação com itens marcados;
- a conferência de que a correção de desempenho resolveu os aeroportos que vinham
  sem dados na Consulta.

Enquanto isso não for feito, **não prometer data de liberação**. O caminho mais
curto é criar dois ou três itens de teste e rodar o ciclo inteiro.
