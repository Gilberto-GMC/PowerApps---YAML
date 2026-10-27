# Implantação de FOZ DO IGUAÇU (SBFI) — pátios e posições

Fonte: quadros **CRO-LO-IGU-OPER-016 — MIX DE AERONAVES**, pátios 01, 02 e 03 (foto do mural da
operação, 27/10/2026). Revisão 04 de 01/06/2024 no pátio 01.

Este arquivo é a folha de cadastro: cada linha vira uma gravação na tela **POSIÇÕES E CORES**, com
FOZ DO IGUAÇU em contexto. O mesmo conteúdo em `implantacao_sbfi_posicoes.tsv`, para abrir no Excel.

⚠️ **Confirmar com a supervisão antes de salvar** — ver *Pontos em aberto* no fim.

---

## 1. Pátios

| Código do pátio | Nome exibido | Ordem | Sigla |
|---|---|---|---|
| `PATIO1` | Pátio 01 | 1 | P1 |
| `PATIO2` | Pátio 02 | 2 | P2 |
| `PATIO3` | Pátio 03 | 3 | P3 |

Cores: escolha na paleta da tela. Sugestão para não confundir com Navegantes: P1 no azul-petróleo,
P2 no azul, P3 no verde — texto branco nos três.

Hangar não aparece nos quadros. Se existir em IGU, crie um quarto pátio `HANGARES` (ordem 4) e
cadastre cada hangar como posição com **Tipo = HANGAR**.

## 2. Posições

`Classe/Aeronave máxima` é o texto que aparece na linha da posição. `Equip. máx.` é o código do
maior equipamento aceito — use a sigla como está na tela **EQUIPAMENTOS**.

### Pátio 01 — `PATIO1`

Aeronave crítica idêntica nas seis: A319 / A320 / A320NEO / A321 / A321NEO / B737-700 / B737-800 /
B737 MAX8 / E195 / E295.

| Posição | Ordem | Tipo | Classe / Aeronave máxima | Equip. máx. |
|---|---|---|---|---|
| `1` | 1 | ? | A321NEO / B737 MAX8 | A21N |
| `2` | 2 | ? | A321NEO / B737 MAX8 | A21N |
| `3` | 3 | ? | A321NEO / B737 MAX8 | A21N |
| `4` | 4 | ? | A321NEO / B737 MAX8 | A21N |
| `5` | 5 | ? | A321NEO / B737 MAX8 | A21N |
| `6` | 6 | ? | A321NEO / B737 MAX8 | A21N |

### Pátio 02 — `PATIO2`

| Posição | Ordem | Tipo | Classe / Aeronave máxima | Equip. máx. | Envergadura | OCUPA |
|---|---|---|---|---|---|---|
| `7` | 1 | REMOTA | B737 MAX8 | B38M | | `7L` ? |
| `7L` | 2 | REMOTA | Legacy 500 | | | |
| `8` | 3 | REMOTA | B737 MAX8 | B38M | | `8L` ? |
| `8L` | 4 | REMOTA | Legacy 500 | | | |
| `9` | 5 | REMOTA | B737 MAX8 | B38M | | `9L` ? |
| `9L` | 6 | REMOTA | Legacy 500 | | | |
| `10` | 7 | REMOTA | envergadura até 15 m | | 15 | |
| `11` | 8 | REMOTA | envergadura até 15 m | | 15 | |

### Pátio 03 — `PATIO3`

| Posição | Ordem | Tipo | Classe / Aeronave máxima | Equip. máx. | OCUPA |
|---|---|---|---|---|---|
| `12` | 1 | REMOTA | A321NEO | A21N | `12L` ? |
| `12L` | 2 | REMOTA | Legacy 500 | | |
| `13` | 3 | REMOTA | B737 MAX8 | B38M | `13R` ? |
| `13R` | 4 | REMOTA | Legacy 500 | | |
| `14` | 5 | REMOTA | B737 MAX8 | B38M | `14R` ? |
| `14R` | 6 | REMOTA | Legacy 500 | | |
| `15` | 7 | REMOTA | B737 MAX8 | B38M | `15L` ? |
| `15L` | 8 | REMOTA | Legacy 500 | | |

Total: 3 pátios, 22 posições.

---

## Pontos em aberto

1. **Ponte ou remota no pátio 01.** O quadro não diz. As seis posições em frente ao terminal
   provavelmente são PONTE — e aí cada uma precisa do **portão** correspondente cadastrado, senão o
   voo aparece tracejado na grade. **Tipo vem REMOTA por padrão: confira antes de salvar.**
2. **Portões.** Nenhum quadro traz. Faltam os números em uso e a correspondência posição → portão.
3. **O `L` e o `R` são meia-posição?** A leitura natural é que `7L` é parte da área de `7`: entra um
   Legacy quando não há um 737. Se for isso, `7` precisa de **OCUPA = `7L`** (e assim por diante),
   senão o app deixa alocar as duas ao mesmo tempo. **Confirme antes** — se forem posições
   independentes, o campo OCUPA fica vazio.
4. **Posições 10 e 11.** O texto estava rasurado na foto; li *15 m*, que seria limite de envergadura.
   Confirmar o valor e se é envergadura mesmo.
5. **`13R`/`14R` ou `13L`/`14L`.** A foto não deixa certo. O nome fica gravado em cada alocação —
   errar aqui dá trabalho depois (não se renomeia posição com lançamento).
6. **Equipamento máximo.** Os códigos sugeridos (`A21N`, `B38M`) precisam existir na tela
   EQUIPAMENTOS. Se a lista usar outra sigla, vale a da lista.
7. **Hangares**, se houver.

A primeira versão pode ir com os campos certos e os duvidosos em branco: trava de envergadura e
OCUPA se acrescentam depois sem mexer em lançamento nenhum. O que **não** se corrige fácil é nome de
posição e código de pátio.
