# Conferência do catálogo de equipamentos — aviação comercial

Lista para você comparar com a tela **EQUIPAMENTOS** e corrigir o que estiver diferente.
Origem das medidas: planta PRANCHA 2519 lida do `.dwg` (metros, 1:1) — detalhe em
[MEDIDAS_PATIO_NVT.md](MEDIDAS_PATIO_NVT.md). As quatro últimas não estão na planta e vêm do
fabricante.

O **código** é o código OACI do tipo, que é como o catálogo já trabalha (o BE40 do Hawker 400XP, por
exemplo). Confira o código antes de mexer: se o seu cadastro usa outro, vale manter o seu.

| código | aeronave | envergadura (m) | comprimento (m) | na planta |
|---|---|---|---|---|
| B738 | B737-800 (winglets) | 35,80 | 39,48 | sim |
| E195 | E195 | 28,72 | 38,67 | sim |
| A320 | A320-200 Sharklet | 35,80 | 37,57 | sim |
| E190 | E190 | 28,72 | 36,24 | sim |
| F100 | Fokker 100 (MK 28) | 28,08 | 35,53 | sim |
| A319 | A319 | 34,10 | 33,84 | sim |
| B737 | B737-700 (winglets) | 35,79 | 33,63 | sim |
| B733 | B737-300 (winglets) | 31,22 | 33,40 | sim |
| E175 | E175 | 26,00 | 31,68 | sim |
| A318 | A318 | 34,10 | 31,44 | sim |
| E170 | E170 | 26,00 | 29,90 | sim |
| AT72 | ATR 72 | 27,05 | 27,17 | sim |
| AT42 | ATR 42 | 24,57 | 22,67 | sim |
| E295 | E195-E2 | 35,12 | 41,50 | não |
| E290 | E190-E2 | 33,72 | 36,24 | não |
| A20N | A320neo | 35,80 | 37,57 | não |
| A21N | A321neo | 35,80 | 44,51 | não |

## Ordem sugerida para mexer

1. **Comprimentos primeiro.** É o campo que hoje mais deve estar zerado ou estimado, e é dele que
   depende a trava nova das posições.
2. **Envergaduras depois**, só onde estiver diferente — a trava de envergadura já roda hoje, então
   mudar um valor muda o que o app aceita. Se alguma diferença for grande, me avise antes.
3. **Só então os `comp_max` das posições** (T1 33,70 · T2 41,60 · T3 41,60 · T4 39,50 · T5 41,60 ·
   T6 41,60). Se os comprimentos ainda estiverem errados no catálogo, a trava barra o que não deve.

## Dois pontos de atenção

- **A321neo (44,51 m) não cabe em nenhuma posição** com esses limites. Cadastrar não é problema; o
  app vai barrar sozinho, e é justamente o aviso que se quer.
- **E190 e E190-E2 têm o mesmo comprimento (36,24 m)** e envergaduras bem diferentes (28,72 e 33,72).
  Se estiverem no catálogo como um só código, a trava de envergadura vai errar em um dos dois.
