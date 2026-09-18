# Medidas do pátio de NAVEGANTES — aeronaves e limite por posição

Fonte das aeronaves: planta **PRANCHA 2519, rev. 1 de 27/05/2016**, lida direto do `.dwg` (desenho em
metros, 1:1; conferido contra o catálogo dos fabricantes, bate na casa dos centímetros).
Fonte dos limites de posição: **Douglas, 17/09/2026** — a planta é anterior ao adiantamento do ponto
de parada e por isso não vale como limite atual.

## Limite de comprimento por posição (pátio comercial)

Cadastrado em 18/09/2026, conforme o Douglas:

| posição | maior aeronave aceita | comprimento | `comp_max` |
|---|---|---|---|
| T1 | B737-800 | 39,48 m | **39,50** |
| T2 | E195-E2 | 41,50 m | **41,60** |
| T3 | E195-E2 | 41,50 m | **41,60** |
| T4 | B737-800 | 39,48 m | **39,50** |
| T5 | E195-E2 | 41,50 m | **41,60** |
| T6 | E195-E2 | 41,50 m | **41,60** |
| T7 | E195-E2 | 41,50 m | **41,60** |
| T6C | B767-300F | 54,94 m | **54,94** |
| H1 a H4 | — | — | **sem trava, por decisão dele** |

O `comp_max` vai um pouco acima do comprimento da aeronave de propósito: assim um arredondamento no
catálogo não barra justamente a aeronave que é aceita.

**O B737-800 entra em todas as posições do pátio principal.** O que separa as posições é o E2:
**T1 e T4 não o recebem** — na T4 por causa da via de serviço, que impede a aeronave de vir mais à
frente. Por isso a **aeronave máxima de todas as pontes é o B-738**: ela é a de maior envergadura
aceita (35,80 m), e é dela que sai a trava de envergadura. Deixar o E-2 como aeronave máxima barraria
o B738 na posição, que foi o que aconteceu em T2 e T3 até 18/09/2026.

A restrição de **B737 MAX lado a lado** é envergadura entre posições vizinhas e vive em
`tb_regrasPosicao`, não no limite da posição.

Aviação geral e helicópteros seguem por **categoria**, não por medida de posição. A planta registra a
aeronave crítica do pátio de helicópteros: **Sikorsky S76-C, comprimento máximo 16,00 m** — fica de
referência, sem virar trava.

## Comprimento e envergadura das aeronaves comerciais

Medidos na planta:

| aeronave | comprimento (m) | envergadura (m) |
|---|---|---|
| B737-800W | 39,48 | 35,80 |
| E195 | 38,67 | 28,72 |
| A320-200 Sharklet | 37,57 | 35,80 |
| E190 | 36,24 | 28,72 |
| F100 (MK 28) | 35,53 | 28,08 |
| A319 | 33,84 | 34,10 |
| B737-700W | 33,63 | 35,79 |
| B737-300W | 33,40 | 31,22 |
| E175 | 31,68 | 26,00 |
| A318 | 31,44 | 34,10 |
| E170 | 29,90 | 26,00 |
| ATR 72 | 27,17 | 27,05 |
| ATR 42 | 22,67 | 24,57 |

Entraram depois da planta — números do fabricante:

| aeronave | comprimento (m) | envergadura (m) |
|---|---|---|
| E195-E2 | 41,50 | 35,12 |
| E190-E2 | 36,24 | 33,72 |
| A320neo | 37,57 | 35,80 |
| A321neo | 44,51 | 35,80 |

⚠️ O **A321neo tem 44,51 m** — não cabe em nenhuma posição pelo limite acima. Se um dia for operar
aqui, o limite das posições precisa ser revisto antes, não depois.

## Regras que a planta traz (2016) e ainda não estão no app

Valem conferência antes de virar restrição em `tb_regrasPosicao`:

- **Posição 6 ocupada** impede a saída por meios próprios da **6A e 6B**, e restringe a saída da
  **A2 e A4**.
- O **envelope "padrão ACI" da posição 6** precisa estar livre quando houver movimento em
  **6B, A3, A4 e A5**.
- **Helicóptero acionado nas posições 1 a 4** fecha a TWY de acesso aos hangares.
- Acionamento simultâneo de asas rotativas só entre **1 e 2, 3 e 4, 1 e 4, 2 e 3**, e só parado na posição.

## Como a leitura do DWG foi feita

O DWG TrueView instalado abre o arquivo mas **recusa script e recusa exportar DXF**. A leitura saiu
com a biblioteca livre LibreDWG (`@mlightcad/libredwg-web`), em Node, rodando local — o arquivo não
sai da máquina. Os desenhos de aeronave são blocos; a medida é a caixa do bloco, com os arcos
amostrados. Conferência de escala: A320-200 Sharklet 35,80 × 37,57 e E190 28,72 × 36,24, iguais ao
catálogo.
