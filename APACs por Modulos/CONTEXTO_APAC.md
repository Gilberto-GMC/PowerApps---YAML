# Contexto — APACs por Módulos (dimensionamento de efetivo AVSEC)

Documentos irmãos:
[ARQUITETURA_APAC.md](ARQUITETURA_APAC.md) (decisões) ·
[ESTRUTURA_LISTAS_APAC.md](ESTRUTURA_LISTAS_APAC.md) (colunas e ordem de execução)

## O problema

APAC é o **Agente de Proteção da Aviação Civil**. A Simone Soares de Castro dimensiona o efetivo
AVSEC de Navegantes **à mão, em dois arquivos**: abre a malha planejada no Power BI, olha voo por
voo, e preenche o `Escopo NVT Verão 2027.xlsx` — quantos módulos de inspeção ficam abertos em cada
hora, quantos APACs e quantos supervisores isso exige, e se a escala 6x2 cobre.

A pergunta que ela responde, nas palavras do Douglas na reunião de 10/09/2026: *"a demanda que está
lá vai ser suportada pelos módulos de inspeção que vão estar refletidos aqui"*.

O trabalho é recorrente (muda a cada temporada e a cada revisão de malha), a conta é mecânica, e o
resultado vira número de contrato.

## A regra de dimensionamento

Fonte: transcrição da reunião de 10/09/2026 com a Simone, mais as medições registradas adiante.

1. **Antecedência de 1h30.** *"Um voo que sai às 5 horas da manhã, eu tenho que estar com o módulo
   preparado para atender esse voo no mínimo 3:30 da manhã."* O módulo abre em
   `decolagem − antecedencia_min`.
2. **Volumetria** = `assentos × ocupacao_pct`, distribuída ao longo dessa janela — não jogada na
   hora da decolagem, porque o processamento começa antes. Os **85%** foram definidos pelo Douglas
   em 10/09/2026.
3. **Capacidade de `pax_por_modulo_hora`** por módulo (185 em NVT, número do TR registrado na
   própria planilha da Simone). **É entrada de tela, não constante — muda de aeroporto.**
4. **Módulos por decolagem:** *"se eu tenho três voos ou mais dentro de uma hora e cada aeronave
   possui mais de 150 assentos, então eu sei que eu preciso ter três módulos em operação."*
5. **`apac_por_modulo` = 3.** *"Cada módulo é composto por 3 APACs."* — confirmado pelo Douglas na
   reunião. Vem da configuração alternativa vigente, que a Simone chamou de "alternativa 8".
6. **`modulos_por_supervisor` = 2.** *"Cada supervisor pode controlar dois módulos"* — *"no máximo
   dois módulos"*. Três módulos → 9 APACs → 2 supervisores.
7. **Postos fixos 24h**, como já estão na planilha: Acesso C = 3, Portão Principal = 1,
   Portão Principal Apoio = 1.

### A fórmula

```
pax(h)        = soma, sobre os voos, de (assentos × ocupacao_pct) repartida pelos minutos
                da janela [decolagem − antecedencia_min, decolagem] que caem na hora h
modulos(h)    = Max( ARREDONDAR.PARA.CIMA(pax(h) / pax_por_modulo_hora) ,
                     decolagens na hora h com assentos > assentos_min )
apacs(h)      = modulos(h) × apac_por_modulo + postos fixos
supervisores(h) = ARREDONDAR.PARA.CIMA(modulos(h) / modulos_por_supervisor)
```

Os dois termos de `modulos(h)` são **piso, não alternativa**. A volumetria pega a hora cheia de
gente; a contagem de decolagens pega o caso de três aeronaves grandes na mesma hora, que exigem
três canais abertos ainda que a soma de passageiros coubesse em dois.

## ⚠️ O que foi medido antes de codar

### A leitura literal de "um módulo por voo" está errada

"Um módulo por voo simultâneo" admite duas leituras. Testadas as duas contra a temporada inteira
(`DECOLAGENS (6).xlsx`, 3.841 voos, 3.624 horas):

| Critério | Horas que pedem mais que os 3 raios-X de NVT |
|---|---|
| Volumetria `pax / 185` | **0** |
| Decolagens acima de 150 assentos na hora cheia | **0** |
| Janelas de 1h30 sobrepostas | **570 — 15,7%** |

A planilha da Simone **nunca passa de 3 módulos** em nenhuma hora. Se o critério fosse janela
sobreposta, ela teria estourado em todo dia da temporada.

**Logo: conta-se decolagem na hora cheia, e o 1h30 diz apenas quando o módulo abre.** Um módulo
atende voos em sequência — é exatamente o que "185 passageiros por hora" significa. Se algum dia
alguém propuser trocar isso por contagem de janelas, este é o número que decide.

### A volumetria da planilha não sai desta malha

Os 151 dias da temporada foram testados contra quatro regras de distribuição (sem janela, 60, 90 e
120 minutos) e duas ocupações (85% e 100%). **Nenhuma combinação reproduz a linha `VOLUMETRIA
EMBARQUE DOMÉSTICO`** do escopo: o melhor caso erra por larga margem, e a planilha tem movimento às
21h e 22h que esta malha não tem.

Aquela coluna veio de outra base ou de outro período. **Não prometer que os números do app vão
coincidir com o que ela digitou** — a comparação é conversa, não teste de aceitação.

### O corte de 150 assentos exclui 20% da temporada

`assentos_min = 150` elimina o E195 (136 assentos), o A319 (140) e o 73G (138): **764 dos 3.841
voos**. Um E195 sozinho numa hora não abre módulo nenhum — só a volumetria o sustenta.

Por isso `assentos_min` é campo de tela, e a tela mostra quantos voos ficaram de fora. A Simone
troca para 130, vê a grade mudar e decide olhando o resultado.

## O que a malha da temporada já diz

Calculado com a regra acima, antes da primeira tela:

- Pico de **14 APACs e 2 supervisores** por hora, e ele se repete nos cinco meses.
- Dia mais pesado de cada mês: 28/10, 03/11, **24/12**, 04/01 e 02/02.
- Em 24/12/2026 há **3 módulos abertos em 4 horas** (10:00, 18:00, 19:00 e 20:00).
- **Nenhuma hora da temporada estoura os 3 raios-X.**

### O caso que justifica os dois critérios

Em **24/12 às 20:00**: 171 passageiros na hora — pela volumetria, `171/185` arredonda para **1
módulo**. Mas são **3 decolagens acima de 150 assentos** na mesma hora, e três aeronaves grandes
embarcando juntas não cabem num canal só. O critério de contagem manda, e a hora vai a **3
módulos, 14 APACs**.

Com volumetria sozinha, essa hora sairia com 8 APACs em vez de 14 — **seis pessoas a menos no
pico de véspera de Natal**. É a diferença que a planilha manual pega porque quem preenche está
olhando os voos, e que um app só de volumetria perderia calado.

## A entrada

`DECOLAGENS (6).xlsx` — export do Power BI, aba única. Filtros gravados no rodapé do arquivo:
`ArrDep é D`, `Airport é NVT`, `Date é igual a ou está depois de 01/10/2026 e está antes de
01/03/2027`.

| Posição | Coluna | Formato |
|---|---|---|
| 1 | `Horário Hierarquia - Horário` | fração do dia (0,21527… = 05:10) |
| 2 | `Data` | serial do Excel (46296 = 01/10/2026) |
| 3 | `Empresa` | texto |
| 4 | `Voo` | texto |
| 5 | `Rota` | texto (`NVT - GRU`) |
| 6 | `Aeronave` | texto (`73H`, `320`, `295`) |
| 7 | `Assentos` | número |
| 8 | `Tipo Voo` | `PASSAGEIRO_REGULAR`, `PASSAGEIRO_EXTRA`, `CARGO-REGULAR` |
| 9 | `Dia` | dia da semana abreviado |

Temporada: GOL 1.935 voos, LATAM 1.291, AZUL 594, ABSA 21.
Frota: 73H e 7M8 (186 assentos), 320 (176), 32N (174), 319 (140), 73G (138), 295 (136),
76V (0 — cargueiro da ABSA).

⚠️ **O Office Script lê o cabeçalho por NOME, não por posição** — o Power BI pode reordenar o
relatório entre exports. É o mesmo padrão do `importar_programacao.ts` do Mapa. (As células do
arquivo bruto não trazem referência de coluna, mas isso só atrapalha quem lê o XML na mão; o
`getValues()` do Office Script devolve a matriz já montada.)

⚠️ **`CARGO-REGULAR` tem 0 assentos.** Não gera volumetria nem conta decolagem — mas é importado,
porque sumir com voo da malha é pior que mostrá-lo valendo zero.

## Decisões de nomenclatura

Mesma convenção dos outros projetos do workspace:

- Listas com prefixo `tb_`, minúsculo sem acento com `_`.
- Nome interno do SharePoint **igual** ao nome de exibição.
- Seleção gravada como `Text`, nunca `Choice`.
- Sem exclusão pela interface — desativa-se com `ativo`.
- Aeroporto identificado pelo **nome** (`NAVEGANTES`), como no Mapa de Alocação, não pelo ICAO.

## Pendências

- **Confirmar com a Simone o corte de 150 assentos** — a tela dá o número dos excluídos.
- **Confirmar a "alternativa 8".** Na planilha, o campo *Alternativa de módulo de Inspeção Embarque
  Doméstico* diz **V**, e **VIII** aparece na linha do Acesso C. Ela disse "alternativa 8" na
  reunião. Como o que muda é `apac_por_modulo`, e ela confirmou 3 por módulo, o cálculo não depende
  dessa etiqueta — mas o rótulo exibido, sim.
- **Escala e déficit** (`scrApacEscala`) entregam a metade de baixo da planilha; a v1 fecha o
  previsto, não o realizado.
