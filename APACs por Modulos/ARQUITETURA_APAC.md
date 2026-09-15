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

O **efetivo mínimo** (§13) soma outro custo ao mesmo recálculo: 2 papéis × 24 rotações × 4 níveis,
cada nível varrendo tabelas de 24 linhas — da ordem de 250 mil operações, **fixas**, porque não
dependem de quantos voos o mês tem. Também não medido no app.

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
| `scrApacCadastro.pa.yaml` | cadastro de premissas (vigências) e postos fixos |
| `scrApacImport.pa.yaml` | importação da malha: anexo, progresso e histórico |
| `scrApacEscala.pa.yaml` | a escala cadastrada contra o exigido do mês: veredito, hora a hora, régua dos turnos, dia a dia (§17) |
| `escala_do_escopo.js` | converte a escala do `Escopo NVT Verão 2027.xlsx` em `dados/escala_escopo_AAAA-MM.csv`, conferindo a cobertura contra a planilha |
| `testar_escala.js` | os números que a tela da escala tem de mostrar, mês a mês, com a conta do app |
| `montar_fluxo_importacao.js` | gera `fluxo/ImportarMalhaAPAC.zip` e confere a definição antes |
| `testar_importar_malha.js` | roda o Office Script fora do Excel contra o export real |
| `FLUXO_IMPORTACAO_APAC.md` | passo a passo do fluxo, com a costura do Office Script |
| `testar_montar_fluxo.js` | prova que as conferências do gerador recusam defeito (controle + 8 casos) |
| `importar_malha.ts` | Office Script — lê o export do Power BI, devolve os voos e o filtro de exclusão; não grava |
| `lista_tb_*.json` | insumos do `List_Generator` |
| `dados/malha_AAAA-MM.csv` | a temporada já convertida, para colar no modo de grade |
| `valida_minimo_app.js` | prova de que a fórmula do mínimo da tela do mês bate com o mínimo exato |
| `CONTRATACAO_APAC.md` | a resposta "precisamos contratar?", medida |

## 12. O que ainda não existe

- **Copiar a escala entre meses** — sem precedente validado de `ForAll` com `Patch` em lista; a carga
  em massa é pelos CSVs no modo de grade (§17).
- **Técnico de segurança, ADM e preposto** — fora de todas as contas.

## 13. Efetivo mínimo — calculado na tela do mês, sem laço

Pedido do Douglas em 14/09/2026: **conforme os dados entram, o sistema já calcula o mínimo
necessário.** A cada leitura do mês ou RECALCULAR, o `btnCalcMes` monta três coleções novas:

| Coleção | O que é |
|---|---|
| `colFixoHoraMes` | postos fixos por hora, da `colPostosApac` — a tela do mês não os lia até aqui |
| `colEnvMes` | **envelope**: a maior exigência de cada hora entre os dias do mês, já com os fixos |
| `colMinMes` | uma linha por papel (APAC, SUPERVISOR): mínimo, folguistas, total no quadro |

⚠️ **Mudança de número visível:** a célula da grade em modo APAC, a coluna PICO e o rodapé passam
a **somar os postos fixos**. Dezembro mostrava 9 no pico; agora mostra **14**, igual à tela do dia.

### A fórmula

```
mínimo = Max( porCobertura , porHomemHora )

porCobertura = menor número de turnos de 8h contíguas que cobre todas as horas do envelope
porHomemHora = teto( soma do envelope ÷ 7 )     -- 7 = horas trabalhadas, o intervalo fica de fora
folguistas   = teto( mínimo ÷ 3 )               -- escala 6x2
```

**Por que dois termos.** O primeiro trata cada turno como 8 horas cheias — enxerga a *forma* do dia,
mas esquece o intervalo. O segundo desconta o intervalo — enxerga o *volume*, mas esquece a forma.
Cada um sozinho erra para menos; o maior dos dois foi, em todos os casos medidos, exatamente o
mínimo verdadeiro.

**Como o primeiro termo é calculado sem laço.** Power Fx não tem laço com estado. Cobrir horas com
turnos contíguos, porém, tem forma fechada: o número de turnos que um guloso da esquerda para a
direita abre é igual à **maior soma de exigências em horas espaçadas de pelo menos uma jornada**.
Com 24 horas e jornada de 8h cabem no máximo 3 dessas horas (4 para jornada de 6h ou 7h), e cada
"nível" `t1..t4` é um `ForAll` de 24 linhas sobre o nível anterior. Como o dia é circular — turno
das 22h cruza a meia-noite —, o cálculo roda nas **24 rotações** e fica com a menor.

### Por que confiar — e onde não confiar

`valida_minimo_app.js` compara a fórmula, em cada mês e na temporada, nos 9 cenários de premissa,
para os 2 papéis, contra:

1. o **limite inferior provado**: o maior entre o mínimo exato de cobertura circular por janelas de
   8h (restrições de diferença, Bellman-Ford) e o homem-hora ÷ 7;
2. uma **escala real** com o intervalo dentro do turno (2ª a 7ª hora), achada por busca local com
   verificação de encaixe dos intervalos por fluxo máximo.

**108 casos, 0 divergências**: a fórmula deu o limite inferior provado, e existe escala desse tamanho.

Números que a tela tem de mostrar com as premissas padrão (emulação do cálculo da própria tela):

| Competência | APACs em escala | + folguistas | Supervisores em escala | + folguistas |
|---|---|---|---|---|
| 2026-10 | **36** | 48 | **5** | 7 |
| 2026-11 | **33** | 44 | **4** | 6 |
| 2026-12 | **36** | 48 | **5** | 7 |
| 2027-01 | **33** | 44 | **4** | 6 |
| 2027-02 | **33** | 44 | **4** | 6 |

⚠️ **Isso é medição sobre a malha de NVT, não teorema.** As rotações do guloso podem, em tese,
superar o mínimo exato em outro perfil de demanda. Antes de usar o número de outro aeroporto como
número de contrato, exporte a malha e rode `valida_minimo_app.js`.

⚠️ **O mínimo não é o quadro contratado.** Ele não cobre férias, absenteísmo nem treinamento, e não
impõe interjornada de 11h. É o piso de desenho de escala — abaixo dele nenhuma escala cobre.

## 14. Cadastro de premissas e postos fixos

`scrApacCadastro`, aberta pelo botão **CADASTROS** da tela do mês. Duas abas, cada uma com lista à
esquerda e formulário à direita — o mesmo desenho do `scrMapaReferencia`, validado no Studio.

**Premissas são vigências, não uma linha que se sobrescreve.** NOVA VIGÊNCIA abre o formulário já
preenchido com a vigência em vigor; muda-se o que mudou e a data a partir da qual vale. Selecionar uma
vigência na lista serve para corrigir digitação. O cálculo usa a **ativa mais recente**, e a lista
marca qual é com EM VIGOR. Duas vigências na mesma data são recusadas: deixariam "a mais recente"
indefinida, e o número mudaria sem ninguém mexer.

⚠️ **A tela do mês guarda as premissas em variáveis e só relê a lista quando elas estão vazias** —
é o que permite mexer no painel sem gravar. Por isso gravar uma vigência esvazia `varCap`,
`varOcup`, `varAntec`, `varAssentosMin`, `varApacMod`, `varModSup` e `varRaiosX`. Se um dia
entrar variável nova no painel, ela tem de entrar nessa lista também, senão a vigência gravada não
chega ao cálculo e nada acusa.

**Postos fixos** usam hora cheia (DAS/ATÉ de 00:00 a 24:00), porque o cálculo soma o posto em cada
hora inteiramente coberta. Posto que atravessa a meia-noite vira dois cadastros — a tela recusa ATÉ
antes de DAS e explica.

**Nada se apaga:** vigência e posto se desligam em Ativa/Ativo, como em todo o workspace.

**As faixas válidas moram na tela, não na lista.** Ver §15.

## 15. As listas não levam `<Default>` nem `<Validation>`

Em 14/09/2026 ficou claro que o `List_Generator` deste tenant falha com `HTTP_Criar_Coluna:
BadGateway` em coluna que traz `<Default>` ou `<Validation>` no `schemaXml`. A separação entre os
arquivos que passaram e os que falharam é total. Os `lista_tb_apac*.json` saem sem os dois.

Consequência de desenho: **toda faixa válida é conferida pelo app antes do `Patch`** — ocupação de 1
a 100, antecedência de 0 a 600, quantidade inteira maior que zero, ATÉ depois de DAS. Quem grava
direto no SharePoint (modo de grade) não tem essa rede; por isso a carga em grade fica restrita aos
CSVs de `dados/`, que já saem conferidos.

A skill `list-generator` ainda documenta `<Validation>` como padrão. Não está provado se o que falha
é o elemento em si ou a fórmula em sintaxe pt-BR (`OU(...;...)`) — o `schemaXml` é XML de
SharePoint, e fórmula de coluna nesse formato costuma ser em inglês. Enquanto isso não for isolado
com uma coluna só, a regra aqui é não usar.

## 16. Importação da malha

O triângulo do Mapa, com três mudanças. Passo a passo em `FLUXO_IMPORTACAO_APAC.md`.

| Peça | Faz |
|---|---|
| `importar_malha.ts` | lê o export pelo **nome** das colunas, converte data e hora, devolve os voos e o **filtro de exclusão** |
| fluxo `Importar malha APAC` | só transporta: apaga o que o filtro diz, grava em lotes, atualiza o progresso |
| `scrApacImport` | anexa, escolhe TODAS ou um mês, acompanha a barra e mostra o histórico |

**1. Um anexo importa a temporada.** O padrão é TODAS. Escolher um mês grava só aquele mês e o filtro
de exclusão só inclui aquele mês — importar dezembro não apaga outubro. O teste
`testar_importar_malha.js` prova isso contra o export real, junto com os 3.841 voos campo a campo.

**2. O que apagar é decidido pelo script, não pelo fluxo.** É a parte perigosa, e é a única das
três peças que dá para rodar sozinha e conferir. O fluxo só apaga se o script disser `ok`, tiver
lido algum voo e devolvido filtro; senão cai em `Recusar`, com a mensagem do script na tela.

**3. Lotes de 50, com 10 em paralelo.** O fluxo do Mapa grava um registro por vez e gasta cerca de
quatro ações por registro; com 3.841 voos seriam uns 15 mil pedidos, acima do limite diário da
licença M365. Em lotes são cerca de 4 mil — 8 mil ao reimportar a temporada, porque também apaga.
**Se TODAS falhar por limite, importe mês a mês.**

**Formulário com sete cards invisíveis.** `Attachments` só existe dentro de `Form`, e o
`SubmitForm` só cria o item se todas as obrigatórias tiverem valor. Como as listas saem sem
`<Default>` (§15), cada obrigatória precisa de card — o Mapa tinha dois, aqui são seis mais a
competência. O item nasce `RASCUNHO` e o `OnSuccess` o marca `PRONTO`: o fluxo dispara em
`PRONTO`, quando o anexo já está gravado.

**O gerador confere antes de gerar, e a conferência foi testada.** testar_montar_fluxo.js roda uma cópia sem defeito (tem de passar) e oito cópias com defeito plantado — obrigatória faltando em PostItem e em PatchItem, referência a ação inexistente, coluna que não existe, runAfter para outro nível, variável não inicializada, items() fora do laço e InitializeVariable dentro de escopo. Os oito são recusados, e cada um pela própria conferência: erro de sintaxe não conta como recusa.

## 17. A escala contra o exigido

A tela do mês diz **quanto** a malha pede; a `scrApacEscala` diz se **os turnos cadastrados** entregam
isso em cada hora de cada dia. Abre só pelo botão ESCALA do mês.

**Não recalcula o exigido.** Usa `colMesCel` e `colMinMes` que o `btnCalcMes` deixou prontos, e
`varCompCalc` diz de qual mês eles são. Se não bater com `varComp`, a tela avisa em vez de comparar
turnos de um mês com a malha de outro.

**A regra de cobertura é uma só nos três lugares** — `btnCalcEsc`, a régua da tela e o `cobre()` de
`escala_do_escopo.js`: o turno conta na hora h se a hora inteira está dentro da presença (atravessando
a meia-noite) e não encosta no intervalo. Essa regra foi conferida contra a planilha antes de virar
Power Fx: os 20 turnos gerados reproduzem, nas 24 horas, a linha 56 (APAC) e a linha 58
(supervisor). Mudar a regra num lugar exige mudar nos outros e rodar o script de novo.

**Um turno por hora de intervalo.** A planilha tem, por turno, uma linha "efetivo em intervalo" com
quantas pessoas param em cada hora. Cada hora negativa vira um registro; quem não para vira um
registro "sem intervalo". Por isso a escala do escopo tem 20 turnos para 36 pessoas.

**Vigilância fica fora de tudo** (Douglas, 15/09/2026: não é o foco do app). As linhas 48–55 do escopo
não viram turno, e a tela só lê da `tb_apacEscala` os papéis APAC e SUPERVISOR — vigilância colada na
lista não aparece nem conta. Os **postos fixos de APAC** cadastrados continuam no exigido, e são eles
que decidem o veredito: com os 5 por hora, os 32 APACs da planilha não cobrem nenhum mês; sem eles,
cobrem todos com folga (`node testar_escala.js --fixos=0`).

**Verde, amarelo, vermelho.** Em cada célula, `exigido/escalado`:

| Cor | Quando |
|---|---|
| verde | escalado ≥ exigido |
| amarelo | falta nesta hora, **e** o total em escala ≥ mínimo do mês (§13) — remanejar turnos cobre |
| vermelho | falta nesta hora, **e** o total em escala < mínimo do mês — só contratando |

Amarelo ou vermelho se decide **pelo mês**, não pela hora: a escala é uma só para todos os dias, e o
mínimo do mês é o menor quadro que cobre o pior dia de cada hora com turnos de 8h e 1h de intervalo —
provado atingível em `valida_minimo_app.js`. Quem tem o mínimo tem uma escala que cobre tudo; quem
não tem, não tem nenhuma.

**Sem intervalo** grava `intervalo_inicio = hora_inicio` e `intervalo_min = 0`, que a regra ignora — em
vez de gravar `Blank()` num número, que não tem precedente de `Patch` neste repositório.

**Números esperados:** `node testar_escala.js`. Com os postos fixos cadastrados: APAC 32 em escala
contra mínimo 36 em outubro e dezembro (contratar 4) e 33 nos outros meses (contratar 1);
supervisores 4 contra 5 em outubro e dezembro (contratar 1), amarelo nos outros. Sem postos fixos,
o mínimo de APAC cai para 21 (out, dez) e 18 (nov, jan, fev), e a escala cobre todos os meses.

⚠️ O `CONTRATACAO_APAC.md` e a página da Simone ainda contam a vigilância como oferta de APAC (linha 56 +
48–55) — é de lá que vinha o "zero APAC". Sem vigilância, aquela resposta não vale.
