# Arquitetura — APACs por Módulos (ASUR Brasil)

Documentos irmãos:
[CONTEXTO_APAC.md](CONTEXTO_APAC.md) (regra e medições) ·
[ESTRUTURA_LISTAS_APAC.md](ESTRUTURA_LISTAS_APAC.md) (colunas e ordem de execução)

## 1. O que é lista e o que é dado local

| Coisa | Onde vive | Por quê |
|---|---|---|
| Malha de decolagens | lista `tb_apacMalha` | milhares de linhas, trocada a cada temporada |
| Premissas de cálculo | lista `tb_apacParametros` | muda por aeroporto e precisa de histórico |
| Postos fixos | lista `tb_apacPostosFixos` | muda sem desenvolvedor |
| Turnos da escala | lista `tb_apacEscala` | alimentada pelo usuário |
| Progresso da importação | lista `tb_apacImportacao` | é o canal entre o fluxo e a barra da tela |
| Aeroportos | `App.Formulas` (`colAerosApac`) | uma linha, não cresce sozinha, sem tela de cadastro |
| Paleta, tipografia, medidas | `App.Formulas` | é tema, não dado |

O critério é o mesmo do Mapa de Alocação: **vira lista o que o usuário final alimenta ou o que
cresce**; vira dado local o que é tema ou tabela de uma linha.

## 2. Por que não reusar a `tb_alocacoesMapa`

O Mapa de Alocação já importa programação mensal de NVT, e a tentação de ler dali é óbvia. **Não
serve**, por decisão do Douglas em 10/09/2026: a carga do Mapa abrange vários meses e é a
programação *operacional* do pátio, não a **malha planejada de temporada** que a Simone usa para
dimensionar contrato. São documentos diferentes, com horizontes diferentes, revisados em ritmos
diferentes.

Amarrar os dois faria o dimensionamento de contrato depender de uma importação feita para outro
fim — e mudar a operação do pátio mexeria, calado, no número de gente do contrato.

## 3. Ler uma vez, desenhar muitas

Cada tela tem **dois botões escondidos**:

- `btnLerMes` / `btnLerDia` — vão ao SharePoint e enchem `colVoosMes` / `colVoosDia`.
- `btnCalcMes` / `btnCalcDia` — só fazem conta sobre a coleção que já está na memória.

Mexer numa premissa chama **só o de calcular**. Sem isso, cada dígito digitado no painel de
premissas dispararia uma consulta ao SharePoint — foi a lição da janela de horas do Mapa, onde cada
seta relia a lista inteira.

## 4. Delegação — a trava que mais custou neste workspace

⚠️ **Nenhuma consulta deste app usa `<>` nem termo não delegável.** Os filtros são só igualdade e
comparação de data sobre colunas indexadas:

```
Filter(tb_apacMalha; aeroporto = varAero; ativo = 1; competencia = varComp)
```

Em 04/09/2026, no Mapa, um `condicao <> "FINALIZADO"` derrubou a consulta para o modo local: o app
passou a ver só as **500 primeiras linhas por ID**, a grade parecia certa, e todo registro criado
depois da importação ficou invisível. Ninguém viu por um dia inteiro.

Aqui o risco é maior e está medido: **um mês da temporada tem entre 727 e 832 voos**. Por isso:

> **O app tem que estar com o "Limite de linhas de dados" em 2000** (Configurações → Geral). Com
> 500, dezembro e janeiro chegam truncados — e truncado, aqui, significa subdimensionar o efetivo
> de uma véspera de Natal sem nenhum aviso na tela.

**Sintoma que identifica o problema, se voltar:** a idade do registro decidindo visibilidade.

## 5. Aritmética sem função sem precedente

O cálculo evita `RoundUp`, `GroupBy` e `Ungroup` — as três têm **zero ocorrências** em todos os
`.pa.yaml` deste repositório. Arredondar para cima virou:

```
With({ q: pax / Max(1; varCap) }; Int(q) + If(q > Int(q); 1; 0))
```

Não é preciosismo. Em 09/09/2026 a propriedade `Default` em `TextInput@0.0.54` tinha **12
precedentes** no repositório e ainda assim foi recusada pelo Studio. Precedente é pista; ausência
total de precedente é sinal vermelho. Ver `LICOES_APRENDIDAS_POWERAPPS_YAML.md`.

**Todo divisor está dentro de `Max(1; …)`.** O Studio avalia as fórmulas **na colagem**, antes de
qualquer `OnVisible` rodar — variável ainda em branco vira divisão por zero e a colagem é recusada.
Foi o quarto erro da série de 05/09/2026, e o `fx_check.js` pegou os três casos deste app antes de
qualquer colagem.

## 6. A virada da meia-noite

Um voo que decola 00:30 abre módulo às 23:00 **do dia anterior**. O cálculo trata isso assim:

- **Na tela do dia:** lê os voos de `D` e `D+1` e posiciona cada um em minutos relativos a `D`
  (`off = hora_min + 1440` quando o voo é de `D+1`). O que sobra abaixo de zero pertence a `D−1` e
  simplesmente não aparece — corretamente.
- **Na tela do mês:** a mesma conta, com `dia_num = diaCel Or dia_num = diaCel + 1`.

Na importação do Mapa, o buraco equivalente valia **~70 voos por ano** nas bordas de mês, e nenhuma
importação os recuperava.

## 7. O painel de premissas

Os sete coeficientes são campos editáveis no alto das duas telas de cálculo, e alterar qualquer um
redesenha na hora. **Nada é gravado sem `SALVAR PREMISSAS`**, que cria uma **vigência nova** em vez
de sobrescrever a anterior.

A razão é que este número vira contrato: daqui a seis meses alguém vai perguntar com que premissa
aquele efetivo foi calculado, e a resposta tem que estar gravada. O rodapé da grade sempre mostra a
premissa em vigor no que está desenhado — grade impressa sem isso não se explica sozinha.

## 8. Grade vazia nunca é zero

Competência sem malha importada **não desenha zeros**: desenha um aviso âmbar dizendo que falta
importar. Zero e "não importei" são estados diferentes, e confundi-los aqui significa dizer que uma
hora não precisa de ninguém.

## 9. Custo do cálculo — a medir no Studio

A grade do mês monta **744 células** (31 × 24) e cada uma varre a coleção do mês (~830 voos no pior
caso). São da ordem de 600 mil visitas de linha por recálculo, em coleção local.

**Isso não foi medido no app** — não tenho como. Se a grade demorar a redesenhar quando você mexe
numa premissa, o caminho já pensado é trocar o pré-cálculo das 744 células por uma **galeria de
dias**, em que cada linha desenha as próprias 24 horas: a galeria só renderiza o que está visível,
e o custo cai para os ~10 dias na tela.

Está escrito aqui para não virar redescoberta.

## 10. Convenções

- Listas `tb_`, minúsculo sem acento com `_`, nome interno igual ao de exibição.
- Aeroporto pelo **nome** (`NAVEGANTES`), como no Mapa — não pelo ICAO.
- Sem exclusão pela interface: desativa-se com `ativo`.
- Locale pt-BR no `App.Formulas`: `;` separa argumentos, `;;` termina definição.

## 11. Arquivos

| Arquivo | O que é |
|---|---|
| `App_Formulas_APAC.txt` | colar em App → Formulas (não é o OnStart) |
| `scrApacMes.pa.yaml` | grade do mês: dias × horas |
| `scrApacDia.pa.yaml` | o dia hora a hora, reproduzindo a planilha da Simone |
| `importar_malha.ts` | Office Script — lê o export do Power BI, não grava |
| `lista_tb_*.json` | insumos do `List_Generator` |
| `dados/malha_AAAA-MM.csv` | a temporada já convertida, para colar no modo de grade |

## 12. O que ainda não existe

- **`scrApacEscala`** — turnos 6x2 sobre a régua de horas, déficit ao vivo e o fechamento com
  folguistas. É a metade de baixo da planilha da Simone.
- **`scrApacImport`** e o fluxo do Power Automate. Enquanto não existem, a malha entra pelos CSVs
  de `dados/` no modo de grade do SharePoint — o que já permite validar todo o cálculo.
- **`scrApacParametros`** — hoje as premissas se editam no painel das telas de cálculo, que grava
  vigência; falta a tela que lista o histórico e cadastra postos fixos.
