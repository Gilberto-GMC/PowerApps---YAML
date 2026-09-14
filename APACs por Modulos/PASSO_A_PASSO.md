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

## Passo 2 — carregar a malha

Sem o fluxo de importação, a malha entra direto:

1. Abra a `tb_apacMalha` → **Editar em modo de grade**.
2. Abra `dados/malha_2026-12.csv` e cole. Separador `;`, UTF-8 com BOM, data em `dd/mm/aaaa`.

Dezembro tem **814 voos** e é o mês de pico da temporada — é o que serve de prova. Os outros quatro
meses estão na mesma pasta.

**Como saber que deu certo:** 814 itens na lista, e o primeiro dia com voos a partir de 01/12.

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
4. Cole `scrApacMes.pa.yaml`, `scrApacDia.pa.yaml` e `scrApacCadastro.pa.yaml`, cada um numa tela nova. Estes estão em
   **en-US** (vírgula separa argumento), que é o formato do código-fonte.

> As telas navegam umas para as outras. Se o Studio reclamar de tela inexistente ao colar uma,
> cole as outras e o erro some sozinho.

---

## Passo 4 — as provas

Na ordem, porque cada uma cobre uma classe de defeito diferente:

| Prova | Como fazer | O que tem que acontecer |
|---|---|---|
| **Aritmética** | abrir **24/12/2026** na tela do dia | às **20:00**: 3 módulos, **14 APACs**, 2 supervisores — e a linha "quem mandou" dizendo **voos** |
| **Postos fixos no mês** | tela do mês em **2026-12**, botão VENDO APACs | coluna PICO chega a **14** (9 dos módulos + 5 fixos), igual à tela do dia — antes desta versão mostrava 9 |
| **Efetivo mínimo** | tela do mês em **2026-12** | painel no topo: **36 APACs** e **5 supervisores** em escala; com folguistas, **48** e **7** |
| **Mínimo acompanha o mês** | trocar para **2026-11** | **33 APACs** e **4 supervisores** — novembro não exige o 5º supervisor |
| **Mínimo acompanha a premissa** | em **2027-02**, trocar a ocupação de 85 para **95** e RECALCULAR | **34 APACs** (era 33) e supervisores continuam **4**; no rodapé do painel, o homem-hora (34) passa a mandar sobre os turnos contíguos (33) |
| **Cadastro de premissa** | CADASTROS → PREMISSAS → NOVA VIGÊNCIA com ocupação **95** e data de hoje → SALVAR → VOLTAR AO MÊS em **2027-02** | o painel mostra **34 APACs**; a lista de vigências marca a nova como **EM VIGOR** |
| **Vigência desligada** | selecionar essa vigência, desligar **Ativa**, SALVAR e voltar ao mês | volta a **33 APACs**, e a vigência de 01/10/2026 volta a ser **EM VIGOR** |
| **Vigência duplicada** | NOVA VIGÊNCIA com a mesma data de uma que já existe → SALVAR | recusa, com aviso vermelho; nada é gravado |
| **Posto fixo** | CADASTROS → POSTOS FIXOS → ACESSO C, quantidade **4** → SALVAR → voltar ao mês | o pico da grade sobe de **14** para **15** e o mínimo de APACs aumenta |
| **Antecedência** | qualquer voo às 05:00 | módulo aceso desde **03:30**, não às 05:00 |
| **Virada** | um voo entre 00:00 e 01:30 | módulo aceso no **dia anterior** |
| **Delegação** | abrir **28/12 a 31/12** | os voos aparecem (é o teste do limite de 500) |
| **Mês vazio** | apontar para uma competência não importada | aviso âmbar dizendo que falta importar — **nunca zeros** |
| **Premissas** | trocar 185 por 150 e RECALCULAR | os módulos sobem e o rodapé passa a dizer 150 |
| **Corte de 150** | olhar o rodapé | quantos voos ficaram fora do critério de contagem |

A prova da aritmética é a que vale por todas: **20:00 de 24/12 tem 171 passageiros**, que pela
volumetria dariam **1 módulo**, mas são **3 decolagens acima de 150 assentos** na mesma hora. Se a
célula disser 3 e 14, a fórmula inteira está funcionando — inclusive a parte que a volumetria
sozinha erraria por seis pessoas.

---

## O que ainda não existe

- **`scrApacEscala`** — os turnos cadastrados e o déficit contra eles. O **mínimo necessário** e os
  folguistas já saem na tela do mês; falta comparar com a escala que existe de fato.
- **`scrApacImport`** e o fluxo do Power Automate — por isso o passo 2 é manual.
- **Cadastro da escala** (`tb_apacEscala`) — a lista existe, mas nenhuma tela ainda lê nem grava
  os turnos. Entra junto com a `scrApacEscala`.
