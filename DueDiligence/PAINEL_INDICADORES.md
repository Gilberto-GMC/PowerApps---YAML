# Painel de indicadores — Due Diligence

Tela nova: `ScreenDueDiligencePainel.yaml`. Entradas: botão **Painel de
indicadores** na tela inicial e aba **Painel** na barra do módulo. O painel é
somente leitura e restrito ao perfil Compliance (lista
`tb_dueDiligenceCompliance`): os botões só aparecem para esse perfil, e a própria
tela confere o acesso a cada carga. Quem não está cadastrado vê um aviso com o
login a informar.

## Largura da tela (2026-09-17)

O painel saía mais largo que a janela: o card da direita e os filtros do topo
ficavam cortados, enquanto a tela de Registros cabia. A diferença estrutural é o
`LayoutMinWidth`: Registros o declara nos contêineres e controles esticados (14
vezes); o painel só tinha 4. Sem ele, o Power Apps aplica um mínimo padrão e um
controle esticado pode empurrar o contêiner além da tela. Agora a barra, o corpo,
a linha do período e todos os visualizadores HTML têm `LayoutMinWidth: =16`, e o
validador confere (grupo "Painel cabe na largura da tela"). A causa é a mais
provável pela comparação das duas telas; confirmar no app depois da colagem.

## Filtros

| Filtro | Onde fica | O que recorta |
|---|---|---|
| Bloco (`cmbDdPainelBloco`) | Barra superior | O painel inteiro, inclusive a situação atual |
| Aeroporto (`cmbDdPainelAeroporto`) | Barra superior | O painel inteiro; a lista mostra só os aeroportos do bloco escolhido |
| Período (`cmbDdPainelPeriodo`) | Título "Solicitações no período" | Só essa seção |

- Trocar o bloco volta o aeroporto para "Todos os aeroportos". SEDE não tem
  bloco e aparece só como aeroporto.
- Bloco e aeroporto recortam **em memória** o que a carga já trouxe: mudar
  esses filtros não consulta o SharePoint de novo e não altera as 3 consultas
  delegáveis. Mudar o período recarrega, como antes.
- Registros antigos não têm `bloco` gravado. A carga completa o campo pela
  tabela aeroporto → bloco (`colDdPainelAeroportos`), que precisa continuar
  igual ao `bloco_DataCard` da `ScreenDueDiligence`. O validador compara as duas.
- O recorte escolhido aparece no título das seções ("SITUAÇÃO ATUAL · BLOCO SUL").

## Hover e animação

Os blocos HTML ganharam CSS progressivo (`varDdPainelCss`): cartões sobem 2 px
com sombra no hover, linhas de tabela ficam destacadas, barras crescem da
esquerda e os números sobem suavemente quando o painel carrega ou o filtro
muda. `prefers-reduced-motion` desliga tudo.

O suporte a `<style>` no `HtmlViewer` do Power Apps **não estava comprovado**
neste projeto quando isso foi feito (o único `<style>` existente era de um
relatório oculto). Por isso:

- o CSS fica dentro de `<div style='display:none'>`: se o sanitizador remover a
  tag e deixar o texto, nada aparece na tela;
- todo o visual continua em estilo inline; o CSS só acrescenta efeito. Sem ele,
  o painel fica idêntico ao anterior;
- o efeito só aparece com o app em execução (visualização ou publicado), não no
  modo de edição do Studio.

Teste depois de colar: passe o mouse sobre um cartão. Se ele subir, o CSS está
ativo; registre o resultado em `LICOES_APRENDIDAS_POWERAPPS_YAML.md`.

## O que aparece

A página tem duas seções. Os filtros ficam acima do que eles recortam.

### Situação atual (não depende do período)

| Cartão | Regra |
|---|---|
| Vigências | Contagem de vencidas nos últimos 12 meses (`Vencido` ou `data_vencimento` já passada) e das que vencem em até 30, de 31 a 60 e de 61 a 90 dias, com a lista dos 8 próximos vencimentos. Considera `Aprovado`, `Aprovado com Ressalvas`, `Reprovado Parcialmente` e `Vencido`. |
| Pendências fora do prazo | `Aguardando Terceiro` há mais dias que o prazo do terceiro (contados de `data_envio_terceiro`) e `Pendente Compliance` há mais dias que o prazo do Compliance (contados de `data_resposta_terceiro`), com as 6 solicitações abertas há mais tempo. |

### Solicitações no período (seletor à direita do título)

Períodos: últimos 30 dias, últimos 90 dias, últimos 12 meses (padrão), ano atual
e todo o período. O recorte é pela data de criação (`Created`).

| Cartão | Regra |
|---|---|
| Solicitações no período | Total criado; quantas foram para o Fluxo III. |
| Em andamento | `Aguardando Terceiro` + `Pendente Compliance`. |
| Aprovadas | `Aprovado` + `Aprovado com Ressalvas`; automáticas = `Aprovado` sem `decisao_compliance`. |
| Reprovadas | `Reprovado` + `Reprovado Parcialmente`. |
| Canceladas | `Cancelado`; informa também as que já venceram. |
| Por aeroporto / por área solicitante | Barras com quantidade e participação; campo vazio vira "Não informado", em cinza e por último. |
| Classificação de risco | Barra 100% com Baixo, Médio e Alto e a vigência de cada faixa; registros sem risco aparecem à parte. |
| Categoria da contraparte | Barras. |
| Tipo de contrato | Os 8 mais frequentes; os demais somados em "Outros". |
| Tempo de resposta e SLA | Média e mediana, em dias corridos: envio do questionário (em horas), resposta do terceiro, análise do Compliance e ciclo completo do Fluxo III (criação até o parecer). Para terceiro e Compliance, mostra a porcentagem dentro do prazo. |

## Prazos (SLA)

Os prazos são lidos da `tb_dueDiligenceParametros`, pela coluna `pontuacao`:

| `codigo_opcao` | Padrão |
|---|---|
| `config_sla_terceiro_dias` | 10 dias corridos após o envio |
| `config_sla_compliance_dias` | 5 dias corridos após a resposta |

Sem as linhas, ou com valor zero, o painel usa os padrões. Para mudar, inclua ou
edite as duas linhas (`codigo_pergunta = config`, `versao_questionario = 2`,
`ativo = 1`). Os valores padrão precisam ser confirmados pelo Compliance.

## Dados e desempenho

- A carga fica no `OnVisible` e é repetida no botão **Atualizar** (espelho
  obrigatório: navegar para a própria tela não reexecuta o `OnVisible`).
- São três consultas delegáveis: solicitações do período, vigências e abertas.
  As do período são lidas em janelas de 30 dias, para que um período longo não
  passe do limite de linhas do app.
- Se alguma consulta trouxer 500 linhas ou mais, o rodapé avisa que pode haver
  corte.
- Durante a atualização, os cartões mantêm o desenho anterior esmaecido.
- Índices recomendados na `tb_dueDiligence`: `Created`, `ativo`, `status` e
  `data_vencimento`.

## Cores

Os tons foram validados com o verificador de paleta, contra fundo branco.

- **Séries únicas:** verde-azulado da marca `#00879A`, contraste 4,26:1; "Não informado" em `#94A3B8`, sempre com rótulo.
- **Risco:** `#118D5C`, `#C47F00` e `#D93025`, as mesmas cores do app. Passa com legenda e espaço de 2px entre os segmentos.
- **Vigência:** escala de um só tom, `#8A1C12`, `#B9281B`, `#DE5346` e `#EC8177`, validada como escala ordenada.
- **Texto secundário:** `#64748B` (4,76:1).

## Checklist pós-colagem

1. Colar `ScreenDueDiligencePainel.yaml` **antes** das versões novas de
   `ScreenDueDiligence` e `ScreenDueDiligenceInicio`: as duas navegam para o
   painel e, sem ele, o Studio acusa nome desconhecido.
2. Confirmar que `tb_dueDiligence`, `tb_dueDiligenceParametros` e
   `tb_dueDiligenceCompliance` estão adicionadas ao app.
3. Testar a delegação com o limite de linhas do app temporariamente em `1`:
   nenhum aviso de delegação deve aparecer nas consultas.
4. Conferir os números contra a listagem com o filtro de status.
5. Conferir a coluna `bloco` na `tb_dueDiligence` (a carga lê `_r.bloco`).
6. Escolher um bloco e depois um aeroporto: os totais têm de bater com a
   listagem filtrada pelo mesmo aeroporto. Trocar o bloco deve voltar o
   aeroporto para "Todos os aeroportos".
7. Em execução, passar o mouse sobre um cartão para verificar o CSS (ver
   "Hover e animação").

## Limitações conhecidas

- O `HtmlViewer` não tem clique nem dica por item. Todos os valores aparecem
  escritos ao lado das barras ou nas tabelas.
- Os tempos usam as datas gravadas hoje. Depois de um reenvio,
  `data_envio_terceiro` passa a ser a data do último envio.
- A mediana usa a média dos dois valores centrais quando a quantidade é par.
