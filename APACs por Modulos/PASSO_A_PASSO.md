# Passo a passo — colocar o APACs por Módulos de pé

Ordem de execução do zero. Cada passo diz **o que fazer**, **onde**, e **como saber que deu certo**.

Documentos irmãos: [CONTEXTO_APAC.md](CONTEXTO_APAC.md) · [ARQUITETURA_APAC.md](ARQUITETURA_APAC.md) ·
[ESTRUTURA_LISTAS_APAC.md](ESTRUTURA_LISTAS_APAC.md)

---

## Passo 0 — limpar o terreno

**A causa do BadGateway foi encontrada em 14/09/2026.** Todo JSON que passou pelo `List_Generator`
tinha colunas **sem** `<Default>` e **sem** `<Validation>`; todo JSON que falhou tinha pelo menos um
dos dois. Os cinco `lista_tb_apac*.json` foram limpos e agora têm exatamente a forma dos que passaram.

> Em 10/09 eu li o teste de três colunas como "o problema está fora do JSON". Estava errado: aquele
> arquivo tinha **uma hipótese por coluna** (`col_b` com `<Default>`, `col_c` com `<Validation>`),
> e basta uma coluna falhar para a execução inteira falhar. O teste nunca apontou para o ambiente.

Nada se perde com a limpeza. As faixas válidas (ocupação 1–100, antecedência 0–600, `ativo` 0 ou 1)
são conferidas pela tela de cadastro antes de gravar, e toda gravação do app e todo CSV mandam o
valor de todas as colunas — nenhuma depende de valor padrão.

1. Apague as listas que ficaram pela metade: **`tb_apacParametros`** (a de hoje), `tb_apacMalha`,
   `tb_apacTeste`, `tb_apacTeste2`, `tb_apacTeste3`.
2. Siga para o passo 1 com os JSON novos.

> ⚠️ **Sempre apague a lista meio criada antes de repetir.** Se ela ficar, o fluxo cai no ramo
> "lista já existe" e você termina com uma lista faltando coluna — que **não dá erro no app**, dá
> fórmula quebrada depois.

**Se ainda falhar:** no histórico da execução, abra `Para cada Coluna`, use as setas até a iteração
com o ícone vermelho e anote o `internalName`. Com o nome da coluna dá para fechar em uma rodada.

---

## Passo 1 — criar as cinco listas

Power Automate → fluxo **`Gerador de lista`** → informar o `siteUrl` → colar o JSON.
**Uma lista por execução**, nesta ordem:

| # | Arquivo | O que cria |
|---|---|---|
| 1 | `lista_tb_apacParametros.json` | premissas do cálculo — **já vem com a vigência de NAVEGANTES preenchida** |
| 2 | `lista_tb_apacPostosFixos.json` | **já vem com** Acesso C (3), Portão Principal (1) e Apoio (1) |
| 3 | `lista_tb_apacMalha.json` | a malha de decolagens |
| 4 | `lista_tb_apacEscala.json` | turnos da escala (a tela que a consome ainda não existe) |
| 5 | `lista_tb_apacImportacao.json` | progresso da importação |

**Como saber que deu certo:** a lista existe e tem **todas** as colunas do
[ESTRUTURA_LISTAS_APAC.md](ESTRUTURA_LISTAS_APAC.md). Coluna faltando é o defeito silencioso deste
passo — confira a contagem, não só a existência da lista.

Depois: na `tb_apacImportacao`, **habilite anexos** (Configurações da lista → Configurações
avançadas). É por ali que o arquivo chega ao fluxo, quando o fluxo existir.

---

## Passo 2 — a importação da malha

Agora a malha entra pelo app: tela **IMPORTAR MALHA**, com o export de DECOLAGENS do Power BI anexado.
Para isso existir, três peças — o passo a passo inteiro, com o porquê de cada ação, está em
[FLUXO_IMPORTACAO_APAC.md](FLUXO_IMPORTACAO_APAC.md):

1. **Anexos habilitados** em `tb_apacImportacao` (Configurações da lista → Configurações avançadas).
2. **Office Script** `importar_malha.ts` salvo como `Importar malha APAC` e movido para
   `Documentos › Roteiros`.
3. **Fluxo**: importar `fluxo/ImportarMalhaAPAC.zip` como pacote, reescolher as listas se vierem em
   branco e **ligar a costura** do Office Script — é a única ação montada à mão.

**Como saber que deu certo:** importar **2026-12** primeiro. A tela mostra **814 gravados de 814
lidos**, e importar dezembro de novo mantém a lista em 814 — não 1.628.

> Enquanto o fluxo não estiver ligado, o caminho antigo continua valendo: abrir
> `dados/malha_2026-12.csv` no Excel, copiar sem o cabeçalho e colar na `tb_apacMalha` em
> **Editar no modo de grade**. Confira a contagem: 814.

---

## Passo 3 — o app

1. **Limite de linhas de dados = 2000.** Configurações → Geral. **Antes de abrir as telas.**
   Com 500, dezembro chega truncado e a grade fica *certa* escondendo o fim do mês — foi o defeito
   do Mapa em 04/09/2026, e aqui ele custaria subdimensionar uma véspera de Natal sem aviso nenhum.
2. Adicione as cinco listas como fontes de dados.
3. Cole `App_Formulas_APAC.txt` em **App → propriedade `Formulas`** — **não** é o `OnStart`.
   Este arquivo é o único em **pt-BR** (`;` separa argumento, `;;` termina definição), porque é
   digitado no Studio e segue o locale.
   ⚠️ **Se já tinha colado antes de 14/09/2026, cole de novo:** a versão nova tem
   `apacJornadaPresenca`, `apacHorasTrabalhadas` e `apacTurnosPorFolguista`, e a tela do mês não
   compila sem elas.
4. Cole `scrApacMes.pa.yaml`, `scrApacDia.pa.yaml`, `scrApacCadastro.pa.yaml`, `scrApacImport.pa.yaml`
   e `scrApacEscala.pa.yaml`, cada um numa tela nova. Estes estão em
   **en-US** (vírgula separa argumento), que é o formato do código-fonte.
   ⚠️ **Se já tinha colado a `scrApacMes` antes, cole de novo:** a versão de 15/09/2026 tem o botão
   ESCALA e grava `varCompCalc`, sem o qual a tela da escala diz que o mês não está calculado.
5. **A escala da planilha do escopo** já está convertida em `dados/escala_escopo_AAAA-MM.csv`, um por
   mês, 25 turnos cada. Abra a `tb_apacEscala` em **Editar no modo de grade** e cole os cinco (ou só o
   do mês que for testar). Os turnos também se cadastram um a um na aba TURNOS da tela da escala.
   Os CSVs saem de `node escala_do_escopo.js "…/Escopo NVT Verão 2027.xlsx"`, que só grava se a
   cobertura dos turnos bater, hora a hora, com as linhas de total da planilha.

> As telas navegam umas para as outras. Se o Studio reclamar de tela inexistente ao colar uma,
> cole as outras e o erro some sozinho.

---

## Passo 4 — as provas

Na ordem, porque cada uma cobre uma classe de defeito diferente:

| Prova | Como fazer | O que tem que acontecer |
|---|---|---|
| **Aritmética** | abrir **24/12/2026** na tela do dia | às **20:00**: 3 módulos, **14 APACs**, 2 supervisores — e a linha "quem mandou" dizendo **voos** |
| **Postos fixos no mês** | tela do mês em **2026-12**, botão do olho em **APAC** | coluna PICO chega a **14** (9 dos módulos + 5 fixos), igual à tela do dia — antes desta versão mostrava 9 |
| **Efetivo mínimo** | tela do mês em **2026-12** | painel no topo: **36 APACs** e **5 supervisores** em escala; com folguistas, **48** e **7** |
| **Mínimo acompanha o mês** | trocar para **2026-11** | **33 APACs** e **4 supervisores** — novembro não exige o 5º supervisor |
| **Mínimo acompanha a premissa** | em **2027-02**, trocar a ocupação de 85 para **95** e RECALCULAR | **34 APACs** (era 33) e supervisores continuam **4**; no rodapé do painel, o homem-hora (34) passa a mandar sobre os turnos contíguos (33) |
| **Cadastro de premissa** | CADASTROS → PREMISSAS → NOVA VIGÊNCIA com ocupação **95** e data de hoje → SALVAR → VOLTAR AO MÊS em **2027-02** | o painel mostra **34 APACs**; a lista de vigências marca a nova como **EM VIGOR** |
| **Vigência desligada** | selecionar essa vigência, desligar **Ativa**, SALVAR e voltar ao mês | volta a **33 APACs**, e a vigência de 01/10/2026 volta a ser **EM VIGOR** |
| **Vigência duplicada** | NOVA VIGÊNCIA com a mesma data de uma que já existe → SALVAR | recusa, com aviso vermelho; nada é gravado |
| **Posto fixo** | CADASTROS → POSTOS FIXOS → ACESSO C, quantidade **4** → SALVAR → voltar ao mês | o pico da grade sobe de **14** para **15** e o mínimo de APACs aumenta |
| **Importação de um mês** | IMPORTAR MALHA → **2026-12** → anexar o export → IMPORTAR | barra até 100%, **814 gravados de 814 lidos**, e a lista com 814 itens de 2026-12 |
| **Reimportação não duplica** | importar **2026-12** de novo com o mesmo arquivo | a lista continua com **814** — não 1.628 |
| **Importação não apaga outro mês** | com dezembro na lista, importar **2027-01** | dezembro continua com **814**; janeiro entra com **832** |
| **Costura desligada** | rodar o fluxo antes de acrescentar a ação do Excel | a importação termina em **ERRO** dizendo "COSTURA NAO LIGADA", e **nenhum voo** é apagado ou gravado |
| **Antecedência** | qualquer voo às 05:00 | módulo aceso desde **03:30**, não às 05:00 |
| **Virada** | um voo entre 00:00 e 01:30 | módulo aceso no **dia anterior** |
| **Delegação** | abrir **28/12 a 31/12** | os voos aparecem (é o teste do limite de 500) |
| **Mês vazio** | apontar para uma competência não importada | aviso âmbar dizendo que falta importar — **nunca zeros** |
| **Premissas** | trocar 185 por 150 e RECALCULAR | os módulos sobem e o rodapé passa a dizer 150 |
| **Corte de 150** | olhar o rodapé | quantos voos ficaram fora do critério de contagem |
| **Escala sem turno** | ESCALA num mês sem os CSVs colados | aviso âmbar dizendo que não há turno ativo — **nunca "cobre o mês"** |
| **Escala de outubro** | colar `escala_escopo_2026-10.csv`, mês em **2026-10**, ESCALA | APAC **amarelo, REPOSICIONAR TURNOS**: 38 em escala, mínimo 36, **24 dias** com falta. SUP **vermelho, CONTRATAR 1**: 4 em escala, mínimo 5, 24 dias |
| **Onde falta em outubro** | tabela hora a hora | APAC: saldo **−2 às 11h** (7 dias), **−3 às 19h** (20 dias) e **−3 às 20h** (7 dias); todas as outras horas verdes. SUP: −1 nas mesmas três horas |
| **Célula exigido/escalado** | grade dia a dia, hora 19, um dia com falta | **14/11** em amarelo; em SUPERVISORES (olho), **2/1** em vermelho |
| **Régua bate com a planilha** | linha ESCALADOS da régua | **5 5 5 12 11 14 14 11 11 14 14 12 14 12 15 14 11 14 15 11 11 11 5 5** — a linha 56 + 48–55 do escopo |
| **Vigilância desligada** | em 2026-10, botão VIGILÂNCIA CONTA COMO APAC | vira VIGILÂNCIA NÃO CONTA; APAC passa a **32** em escala e **CONTRATAR 4**, em vermelho; a hora 00 fica **5/3** |
| **Escala de dezembro** | colar `escala_escopo_2026-12.csv`, mês **2026-12**, ESCALA | APAC amarelo com **30 dias** com falta, inclusive **01h e 02h** (2 dias, voos de madrugada); SUP **CONTRATAR 1** |
| **Novembro não pede supervisor** | mês **2026-11**, ESCALA | APAC e SUP **amarelos**, 11 dias com falta, só às 19h e 20h |
| **Turno novo muda a análise** | em 2026-10, TURNOS → NOVO TURNO: APAC, começa 17:00, 08h, intervalo 22:00, 3 pessoas → SALVAR → ANÁLISE | APAC passa a **41** em escala e **7 dias** com falta, só às **11h**; 19h e 20h ficam verdes. Desligar **Ativo** desse turno e SALVAR volta a **24 dias** (`node testar_escala.js --extra=APAC:1020:480:1320:60:3`) |
| **Intervalo fora do turno** | TURNOS → NOVO TURNO, começa 06:00, 08h, intervalo 20:00 → SALVAR | recusa com aviso vermelho; nada é gravado |

A prova da aritmética é a que vale por todas: **20:00 de 24/12 tem 171 passageiros**, que pela
volumetria dariam **1 módulo**, mas são **3 decolagens acima de 150 assentos** na mesma hora. Se a
célula disser 3 e 14, a fórmula inteira está funcionando — inclusive a parte que a volumetria
sozinha erraria por seis pessoas.

---

## O que ainda não existe

- **Copiar a escala de um mês para outro** — cada competência tem a sua escala e, na tela, só se
  cadastra turno a turno. Copiar exigiria `ForAll` com `Patch` numa lista, que não tem precedente
  validado neste repositório. Até lá, a carga em massa é pelos CSVs no modo de grade.
- **Técnico de segurança, ADM e preposto** — não entram em nenhuma conta.
