# Precisamos contratar mais APACs? — resposta medida

**Pergunta do Douglas (11/09/2026):** "precisamos contratar mais APACs e, se sim, em quais horários?"

**Resposta:** **+1 supervisor. Zero APACs.** Contrato de **59 → 60**, não 65.

⚠️ **Revisão de 14/09/2026:** o mínimo de APACs é **36**, não 38 — medido exato (§4). A resposta não
muda; a folga aumenta. E mês a mês, o 5º supervisor só é exigido em **outubro e dezembro** (§3).
O app passou a calcular esses mínimos sozinho, na tela do mês (`ARQUITETURA_APAC.md` §13).

⚠️ **Esta conclusão substitui a de 11/09 de manhã (+3 APAC, +1 supervisor, 59→65), que estava
errada.** O que mudou está na seção "O erro que a revisão pegou".

---

## 1. O que a malha exige e o que a escala entrega

Régua de horas da planilha: **coluna C = 00h … coluna Z = 23h** (linha 3, fração do dia).
Toda leitura de oferta abaixo é feita **pela letra da coluna**, nunca por posição.

| | fonte | confere contra |
|---|---|---|
| Oferta APAC/hora | linha 56 + linhas 48-55 (vigilância) | soma das linhas 20-39 = linha 56 OK |
| Oferta supervisor/hora | linha 58 | soma das linhas 40-47 = linha 58 OK |

```
OFERTA APAC   00->23: 5,5,5,12,11,14,14,11,11,14,14,12,14,12,15,14,11,14,15,11,11,11,5,5   (266 h-h)
OFERTA SUPERV 00->23: 0,0,0,1,1,2,2,1,1,2,2,1,2,1,2,2,1,2,2,1,1,1,0,0                      (28 h-h)
```

Demanda calculada sobre os 3.841 voos da temporada (85%, 90 min, 185 pax/h, corte >150 assentos),
envelope = maior exigência de cada hora nos 151 dias:

| hora | APAC exigido | ofertado | falta | supervisor exigido | ofertado | falta |
|---|---|---|---|---|---|---|
| 01h e 02h | 8 | 5 | **3**, em 2 dias | 1 | 0 | **1**, em 2 dias |
| 11h | 14 | 12 | **2**, em 7 dias | 2 | 1 | **1**, em 7 dias |
| **19h** | 14 | 11 | **3**, em 116 dias | 2 | 1 | **1**, em 116 dias |
| **20h** | 14 | 11 | **3**, em 95 dias | 2 | 1 | **1**, em 95 dias |
| demais 20 horas | — | — | cobre | — | — | cobre |

**Envelope APAC = 249 homem-hora contra 266 ofertados. Envelope supervisor = 27 contra 28.**

---

## 2. Por que "falta 3 às 19h" **não** significa contratar 3

Os turnos de hoje foram desenhados contra a coluna `VOLUMETRIA` digitada na planilha, que
**não sai desta malha** (medido em 10/09: 151 dias x 4 regras de distribuição x 2 ocupações, nenhuma
reproduz aquela linha). Subtrair a demanda da malha de uma escala desenhada contra outra curva mede
**desencontro de posicionamento**, não falta de gente.

O teste certo é: reposicionando os horários de início, os 38 efetivos cobrem o envelope?

**Cobrem, com folga.** O menor quadro que cobre todas as 24 horas em todos os 151 dias, com jornada
de 8h de presença e 1h de intervalo dentro do turno, é de **36 pessoas** (§4). `minimo_efetivo.js`
imprime uma escala possível com 38.

Um movimento de custo zero, visível a olho nu na planilha: a linha **L34 (2 pessoas, 12h->19h)**
passa a **13h->20h** e coloca 2 APACs na hora que mais falta.

---

## 3. Por que o supervisor **é** contratação, e não remanejo

`exaustivo_supervisores.js` enumerou **todas as 34.389.810 combinações** de 4 supervisores
(168 padrões distintos de janela de 8h com 1h de intervalo, em qualquer posição, com virada de dia).

> **Nenhuma cobre o envelope.** Com 5, cobre.

Não é heurística e não é amostra: é enumeração completa. 4 supervisores x 7 horas trabalhadas = 28
homem-hora contra 27 exigidos — a folga de 1 hora não sobrevive à exigência de que as horas sejam
contíguas e de que 10h, 11h, 15h, 18h, 19h e 20h peçam **2 simultâneos**.

**Mês a mês a exigência não é a mesma:**

| Competência | APACs mínimo | Supervisores mínimo |
|---|---|---|
| 2026-10 | 36 | **5** |
| 2026-11 | 33 | 4 |
| 2026-12 | 36 | **5** |
| 2027-01 | 33 | 4 |
| 2027-02 | 33 | 4 |

O 5º supervisor é exigido em **outubro e dezembro**. Se ele entra no contrato permanente ou como
reforço de temporada é decisão de contrato, não de cálculo.

---

## 4. Robustez — o que muda se a premissa mudar

Nove cenários, incluindo a leitura **literal** da regra da Simone (só 3 voos ou mais dispara 3
módulos, em vez de N voos -> N módulos). Mínimo da temporada:

| cenário | exigido (h-h) | mínimo APAC | mínimo supervisor |
|---|---|---|---|
| base (85%, 90 min, >150) | 249 | **36** | **5** |
| contagem literal (só >=3 dispara) | 246 | **36** | **5** |
| ocupação 80% | 246 | **36** | **5** |
| ocupação 95% | 255 | **37** | **5** |
| antecedência 60 min | 246 | **36** | **5** |
| antecedência 120 min | 246 | **36** | **5** |
| sem corte de assentos | 252 | **36** | **5** |
| capacidade 150 pax/h | 255 | **37** | **5** |
| literal + 95% + 120 min | 252 | **36** | **5** |

**Nenhum cenário passa de 37 APACs — os 38 contratados cobrem todos. O 5º supervisor é invariante.**

**Estes números são exatos, não estimativa.** Cada um foi fechado pelos dois lados
(`valida_minimo_app.js`): é o limite inferior provado — o maior entre a cobertura circular exata por
janelas de 8h e o homem-hora ÷ 7 —, e existe escala real, com o intervalo dentro do turno, desse
tamanho. 108 casos (meses e temporada × cenários × papéis), 0 divergências.

---

## 5. O erro que a revisão pegou

A resposta da manhã dizia **+3 APAC e +1 supervisor, 59 -> 65**. Dois defeitos:

1. **Array de supervisores deslocado uma hora.** Eu havia lido a linha 58 **por posição de célula**;
   lida **pela letra da coluna** contra a régua da linha 3, a série é
   `0,0,0,1,1,2,2,1,1,2,2,1,2,1,2,2,1,2,2,1,1,1,0,0`. É a mesma armadilha de 11/09 de manhã — célula
   vazia auto-fechada no XML — só que uma linha adiante. O déficit de supervisor às 19h/20h
   sobrevive à correção; o que **não** sobrevive é o "buraco das 03h", que era artefato do
   deslocamento.
3. **(14/09) Tratar o melhor achado como mínimo.** O 38 e os três 39 da versão de 11/09 vieram de
   busca gulosa com reinícios: ela acha escalas boas, não prova que não existe menor. Medido com
   limite inferior exato, o mínimo é 36 (37 nos dois cenários mais apertados). A conclusão não mudou
   por sorte, não por método.
2. **Confundir déficit com necessidade de contratação.** Déficit mede a escala atual; contratação
   se mede contra a **melhor escala possível**. Nunca rodei a otimização antes de recomendar +6
   pessoas.

---

## 6. O que ainda não está medido — e não deve virar aditivo sem resposta

1. **Fator de cobertura.** Férias, absenteísmo e treinamento estão fora de tudo acima. Os folguistas
   (1 para 3) cobrem folga de escala, não ausência.
2. **Malha planejada, não realizada.** Atraso operacional desloca demanda e nunca foi testado.
3. **151 dias de verão contra contrato permanente.** Dezembro e janeiro concentram a pressão
   (97% e 100% dos dias com déficit na escala atual); sábado é o dia mais folgado (36%).
4. **Restrição trabalhista.** A escala de 38 pessoas respeita jornada de 8h com 1h de intervalo e
   nada mais — interjornada de 11h e acordo do SNA não foram impostos ao otimizador.
5. **Perguntas para a Simone**, que mudam número: o posto de vigilância é 3 turnos de 8h (como a
   grade está preenchida) ou 4 de 6h (como o rótulo diz — o de 18h-00h hoje está vazio)? Os 2
   agentes de vigilância podem fechar um raio-X, ou contá-los como oferta de módulo usa a mesma
   pessoa duas vezes? E de onde veio a linha `VOLUMETRIA`, que não sai desta malha?

---

## Como reproduzir

```
node oferta_e_deficit.js          # oferta lida por letra de coluna + deficit hora a hora
node minimo_efetivo.js            # escala minima construtiva (38 APAC / 5 supervisores)
node exaustivo_supervisores.js    # prova exaustiva de que 4 supervisores nao cobrem
node robustez_efetivo.js          # os nove cenarios (versao 11/09, gulosa - superada)
node valida_minimo_app.js         # minimo EXATO por mes e cenario, e prova da formula do app
```
