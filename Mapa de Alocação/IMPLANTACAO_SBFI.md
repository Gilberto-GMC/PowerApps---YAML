# Implantação de FOZ DO IGUAÇU (SBFI) — pátios e posições

Fonte: quadros **CRO-LO-IGU-OPER-016 — MIX DE AERONAVES**, pátios 01, 02 e 03 (foto do mural da
operação, 27/10/2026). Revisão 04 de 01/06/2024 no pátio 01.

Este arquivo é a folha de cadastro: cada linha vira uma gravação na tela **POSIÇÕES E CORES**, com
FOZ DO IGUAÇU em contexto. O mesmo conteúdo em `implantacao_sbfi_posicoes.tsv`, para abrir no Excel.

⚠️ **Confirmar com a supervisão antes de salvar** — ver *Pontos em aberto* no fim.

> **Decisão de 27/10/2026: em IGU não se usa OCUPA.** A dupla `7`/`7L` é a mesma área, mas as duas
> precisam **aparecer na grade** — o supervisor aloca pelo nome que usa. OCUPA tira a posição da grade
> (quem tem OCUPA preenchido vira alternativa, mostrada entre parênteses na linha que consome), então
> o campo fica **vazio nas 22 posições** e a exclusão mútua vai para **RESTRIÇÕES**, que bloqueia sem
> esconder. Em Navegantes o OCUPA continua certo: lá a T6C é combinada e não precisa de linha própria.

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

**A ordem tem que ser única dentro do pátio.** Tanto faz 1, 2, 3… ou o próprio número da posição —
mas duas posições com a mesma ordem embaralham a sequência da grade e repetem a letra da sigla do
pátio. Usando o número da posição, a variante leva **meio ponto**: `13` fica com 13 e `13R` com
**13,5**.

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
| `7` | 1 | REMOTA | B737 MAX8 | B38M | | *(vazio)* |
| `7L` | 2 | REMOTA | Legacy 500 | | | *(vazio)* |
| `8` | 3 | REMOTA | B737 MAX8 | B38M | | *(vazio)* |
| `8L` | 4 | REMOTA | Legacy 500 | | | *(vazio)* |
| `9` | 5 | REMOTA | B737 MAX8 | B38M | | *(vazio)* |
| `9L` | 6 | REMOTA | Legacy 500 | | | *(vazio)* |
| `10` | 7 | REMOTA | envergadura até 15 m | | 15 | |
| `11` | 8 | REMOTA | envergadura até 15 m | | 15 | |

### Pátio 03 — `PATIO3`

| Posição | Ordem | Tipo | Classe / Aeronave máxima | Equip. máx. | OCUPA |
|---|---|---|---|---|---|
| `12` | 1 | REMOTA | A321NEO | A21N | *(vazio)* |
| `12L` | 2 | REMOTA | Legacy 500 | | *(vazio)* |
| `13` | 3 | REMOTA | B737 MAX8 | B38M | *(vazio)* |
| `13R` | 4 | REMOTA | Legacy 500 | | *(vazio)* |
| `14` | 5 | REMOTA | B737 MAX8 | B38M | *(vazio)* |
| `14R` | 6 | REMOTA | Legacy 500 | | *(vazio)* |
| `15` | 7 | REMOTA | B737 MAX8 | B38M | *(vazio)* |
| `15L` | 8 | REMOTA | Legacy 500 | | *(vazio)* |

Total: 3 pátios, 22 posições.

## 3. Restrições

Tela **RESTRIÇÕES**, uma regra por par. Tipo **Bloqueio**, **nenhum equipamento dos dois lados** — é
assim que a regra vale para qualquer aeronave — e a mensagem que o operador vai ler. A regra pega nos
dois sentidos: uma linha só por par.

| Posição | Posições afetadas | Tipo | Equipamentos | Mensagem |
|---|---|---|---|---|
| `7` | `7L` | Bloqueio | nenhum | A 7 e a 7L são o mesmo espaço físico: só uma aeronave por vez. |
| `8` | `8L` | Bloqueio | nenhum | A 8 e a 8L são o mesmo espaço físico: só uma aeronave por vez. |
| `9` | `9L` | Bloqueio | nenhum | A 9 e a 9L são o mesmo espaço físico: só uma aeronave por vez. |
| `12` | `12L` | Bloqueio | nenhum | A 12 e a 12L são o mesmo espaço físico: só uma aeronave por vez. |
| `13` | `13R` | Bloqueio | nenhum | A 13 e a 13R são o mesmo espaço físico: só uma aeronave por vez. |
| `14` | `14R` | Bloqueio | nenhum | A 14 e a 14R são o mesmo espaço físico: só uma aeronave por vez. |
| `15` | `15L` | Bloqueio | nenhum | A 15 e a 15L são o mesmo espaço físico: só uma aeronave por vez. |

> O botão **TESTAR** vai dizer que a regra não pegaria nada — é esperado num aeroporto sem histórico
> de lançamento. Ele olha os últimos dias de operação, que em IGU ainda não existem.

### OCUPA ou restrição?

| | OCUPA | Restrição de par |
|---|---|---|
| a posição aparece na grade | **não** | sim |
| bloqueia o uso simultâneo | sim | sim |
| quando usar | a posição é **combinação** de outras e não precisa de linha (T6C em Navegantes) | as duas posições são reais e o operador aloca por qualquer uma das duas (7 e 7L em IGU) |

---

## Pontos em aberto

1. **Ponte ou remota no pátio 01.** O quadro não diz. As seis posições em frente ao terminal
   provavelmente são PONTE — e aí cada uma precisa do **portão** correspondente cadastrado, senão o
   voo aparece tracejado na grade. **Tipo vem REMOTA por padrão: confira antes de salvar.**
2. **Portões.** Nenhum quadro traz. Faltam os números em uso e a correspondência posição → portão.
3. **O `L` e o `R` são meia-posição?** A leitura natural é que `7L` é a mesma área de `7` usada por um
   Legacy quando não há um 737. Sendo isso, o **OCUPA vai na variante**: `7L` ocupa `7`. Nunca o
   contrário — posição com OCUPA preenchido **sai da grade** (foi o que sumiu com 7, 8 e 9 em
   27/10/2026). Se forem posições independentes, que podem receber duas aeronaves ao mesmo tempo, o
   OCUPA fica vazio nas duas.
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
