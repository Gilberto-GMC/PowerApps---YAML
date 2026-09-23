# Due Diligence — Fase 3: Laudo final (DD04)

## O que é

O laudo é a entrega final do módulo: um documento único, com identidade
visual própria, que consolida a solicitação inteira. Fica disponível para
**download por qualquer usuário do app** (não só Compliance) assim que a
solicitação recebe o parecer final — `Aprovado`, `Aprovado com Ressalvas`,
`Reprovado Parcialmente` ou `Reprovado`.

### Conteúdo (2026-09-17)

O laudo é lido pelo solicitante e pelo Compliance, então só traz o que faz
sentido para os dois:

| Seção | Conteúdo |
|---|---|
| Cabeçalho | Número, emissão, subtítulo conforme a base da decisão e selo com o resultado e a vigência. |
| Identificação da contraparte | Razão social, CNPJ/CPF, categoria, tipo de contrato, área, aeroporto, solicitante, abertura e objeto. |
| Resultado da avaliação | Classificação de risco; análise (`Automática` ou `Compliance`); gatilho crítico; questionário do terceiro (`Não se aplica`, `Sem resposta`, `Sem risco alto` ou `Com risco alto`). Não mostra o nome técnico do fluxo nem a pontuação. |
| Aprovação automática | Só em `Aprovado` sem decisão do Compliance. Traz a data e o critério que dispensou a análise: obrigação legal, contraparte sem risco (com o tipo), resposta limpa do terceiro em risco baixo ou médio, ou a regra do Fluxo II anterior a 15/09/2026. Não tem campos de parecer. |
| Parecer do Compliance | Decisão e data; justificativa; condicionantes (um bloco só quando o texto é o mesmo da justificativa); responsável; prazo de reavaliação só quando existe. |
| Vigência | Só quando há data de vencimento. |
| Questionário do terceiro | Omitido quando não houve questionário. Com questionário, tabela de pergunta, resposta e classificação, ou o aviso de que o terceiro não respondeu até a decisão. |
| Histórico da solicitação | Marcos com `visivel_solicitante = 1`, em texto de negócio: registro, atualização que mudou o status, envio e resposta do questionário, esclarecimentos visíveis, parecer, cancelamento e vencimento. Ficam de fora a falha de envio, o pedido de reenvio e os identificadores técnicos. |

Textos digitados (razão social, objeto, justificativa, condicionantes,
respostas e esclarecimentos) são escapados para HTML antes de entrar no
arquivo.

## Por que HTML, e não PDF gerado pelo fluxo

A primeira versão deste laudo populava um modelo Word e convertia para PDF
via Power Automate. O ambiente deste projeto não tem o conector **Word
Online (Business)** liberado (é premium por inteiro, não só uma ação dele) —
sem ele, não dá para preencher nem converter um `.docx` pelo fluxo.

A solução: o **Power Apps monta o HTML do laudo** (a mesma técnica de
concatenar texto que a tela já usa em vários lugares — o resumo da
avaliação, o painel de indicadores, o corpo do e-mail do DD01) e manda
pronto para o fluxo. O fluxo só grava esse HTML como arquivo numa biblioteca
do SharePoint e devolve o link — **nenhum conector além do SharePoint que
DD01–DD03 já usam**. O usuário abre o link no navegador e, se quiser um PDF
de verdade, usa **Ctrl+P → Salvar como PDF** (funciona em qualquer
navegador, sem nenhum passo extra no app).

## Sobre o pacote pronto

Diferente da primeira versão, o `GerarLaudoDueDiligence_PRONTO.zip` **é um
pacote importável de verdade**, no mesmo nível de confiança que DD01–DD03.
Isso só foi possível depois de um fluxo esqueleto real, exportado do Studio
deste ambiente, revelar o formato exato de duas peças que eu não tinha como
verificar sozinho: o gatilho **Power Apps (V2)** e a ação **Responder a um
aplicativo do Power Apps ou fluxo**. Um detalhe não-óbvio que só esse
esqueleto revelou: o Power Automate nomeia os campos do gatilho pelo
**tipo** da entrada, não pelo nome escolhido — a entrada chamada `id` vira
internamente a chave `number`, e `html` vira `text` (o nome escolhido fica
só como rótulo/`title`). O fluxo já está gerado com esses nomes reais.

## Peças

| Arquivo | O que é |
|---|---|
| `GerarLaudoDueDiligence_PRONTO.zip` | Pacote pronto para importar no Power Automate, gerado por `build_power_automate_flows.py` (`configure_laudo`). |
| `PowerAutomate/DD04_GerarLaudo.definition.json` | A definição expandida do mesmo fluxo, para leitura/diff — não é para importar direto. |

## Passo a passo

### 1. Pré-requisito no SharePoint

Criar a biblioteca **Laudos Due Diligence** no site
`https://grupoccr.sharepoint.com/sites/ComplianceAeroportos`. Permissão de
**leitura** para todos os usuários do app (o link do laudo precisa abrir
para quem clicar em "Baixar Laudo"); edição restrita ao Compliance/
administradores do site.

A coluna `laudo_url` já está em `listgen_tb_dueDiligence_completo.json` para
instalações novas; em listas existentes, criar aditivamente (Texto, 400
caracteres) como nas migrações anteriores (ver `FASE2_POWER_AUTOMATE.md`).

### 2. Importar o DD04

1. Importar `GerarLaudoDueDiligence_PRONTO.zip` como **Criar como novo**
   (não existe rascunho para atualizar — mesma lógica do DD03).
2. Mapear a conexão SharePoint pedida na importação.
3. Abrir o fluxo, salvar e ativar.

### 3. Ligar o fluxo ao app

1. No Power Apps Studio, adicione **DD04 Gerar Laudo** como fonte de dados
   (Power Automate). O app referencia o fluxo pelo nome sem espaços que o
   Studio gera automaticamente — `DD04GerarLaudo` — não pelo nome de
   exibição; se o seu ambiente gerar um identificador diferente, ajuste a
   fórmula do botão (`tbDdAcoes.OnSelect`, ramo `"laudo"`).
2. O botão **Baixar Laudo** já está na tela `ScreenDueDiligence` (toolbar de
   cada linha da lista, item `laudo`) — não precisa de mais nenhuma mudança
   no app. Ele já:
   - monta o HTML completo do laudo em Power Fx (identificação, risco,
     parecer, respostas do terceiro, linha do tempo);
   - chama `DD04GerarLaudo.Run(ThisItem.ID, _html)`;
   - se `laudo_url` já estiver preenchido, baixa o arquivo existente direto
     (`Download`), sem rechamar o fluxo;
   - fica desabilitado fora das quatro decisões finais, com a dica
     explicando o motivo.
3. Teste com uma solicitação de cada fluxo (I, II e III) já com parecer
   registrado, e confira o HTML gerado (abra o link, confira no navegador,
   teste o Ctrl+P → Salvar como PDF) antes de liberar para os usuários.

O `DD04GerarLaudo_20260914134244.zip` que você exportou já cumpriu o papel
dele (serviu de referência para o gatilho/resposta) — pode excluir, não é
mais necessário.

## Regenerar o pacote

Qualquer mudança no contrato (novos campos, nova biblioteca) é feita em
`laudo_actions()` / `configure_laudo()`, em `build_power_automate_flows.py`.
Depois de editar:

```bash
python build_power_automate_flows.py
python validar_due_diligence.py
```

O validador confere a integridade do zip, o formato do gatilho, e que o
botão do app (`ScreenDueDiligence.yaml`) continua consistente com o que o
fluxo devolve (`saida_laudo_url`, `saida_erro`).

## Limitações conhecidas

- O laudo é gerado uma vez e fica fixo: se o parecer for corrigido depois
  (caso raro, já que a tela volta a ser somente leitura após a conclusão), é
  preciso apagar `laudo_url` do item para que o botão gere um arquivo novo.
- Laudos já gerados não mudam de layout: para gerar de novo no modelo atual,
  apague `laudo_url` do item e use Baixar Laudo outra vez.
- O histórico só mostra desdobramentos com `visivel_solicitante = 1` —
  a mesma regra de confidencialidade que já separa o histórico interno do
  Compliance do que aparece para os demais usuários no app. Notas internas
  não aparecem no laudo, mesmo para quem tem acesso a elas na tela.
- As respostas do terceiro mostradas são as do envio ativo (`forms_envio_id`
  atual); um reenvio de questionário substitui esse conjunto.
- O arquivo é `.html`, não `.pdf`. Quem precisar de um PDF de verdade gera
  pelo próprio navegador (Ctrl+P → Salvar como PDF) — o layout já é
  desenhado para impressão em A4. Se no futuro o ambiente ganhar uma licença
  premium com conversor HTML→PDF sem custo extra, dá para acrescentar uma
  etapa de conversão automática no DD04 sem mudar nada no app (o HTML que
  ele já recebe seria só a entrada dessa nova etapa).
