# Pedidos da supervisão — 04/09/2026

Levantados pelo supervisor durante a apresentação do sistema pelo Douglas. A ordem abaixo é a que ele indicou; a exportação fica por último por decisão dele.

Cada item traz o que já existe no app e o que ainda precisa ser decidido — porque metade deles tem
mais de uma leitura possível, e escolher errado custa mais que perguntar.

---

## 1. Grade de 10 em 10 minutos — ✅ feito em 05/09/2026

Colunas a cada 10 minutos, com o número (`10`, `20`, `30`, `40`, `50`) **bem menor** que o da hora, e
a **linha do intervalo menos evidente** que a da hora cheia.

**O que existe hoje:** a grade tem 24 colunas de hora. `mapPctHora = "4.1666"` (100/24 truncado, para
as colunas nunca estourarem os 100%), e `mapFundoHoras` desenha as linhas de fundo.

**O que muda:** de 24 para 144 colunas. Isso toca o cabeçalho, o fundo e — o ponto que exige atenção —
a **camada de clique**, que hoje tem 24 células em container AutoLayout, uma por hora.

**Ganho de brinde, que vale confirmar se ele quer:** com a camada em 10 minutos, clicar numa célula
vazia passaria a abrir o registro novo com o horário arredondado a 10 minutos em vez de à hora cheia.
Hoje clicar às 09h40 propõe 09:00.

**Cuidado:** 144 células de clique por linha, vezes as linhas visíveis. A camada atual é AutoLayout com
`FillPortions`; multiplicar por seis pode pesar. Medir antes de espalhar.

---

## 1b. Bloco pequeno demais — ✅ feito em 05/09/2026, junto com o 1

Acrescentado depois, e **é o mesmo problema do item 1 visto pelo outro lado.** Hoje as 24 horas cabem
numa página só, e o retângulo do voo fica pequeno. Passar para colunas de 10 minutos na mesma largura
deixaria menor ainda. **Os dois têm que ser feitos juntos** — separados, o primeiro piora o segundo.

O pedido: bloco maior, **rolagem horizontal embaixo** para andar nos horários, e a rolagem
**acompanhando a passagem da hora** sozinha.

**O que a plataforma permite, e o que não permite:**

`LayoutOverflowX: =LayoutOverflow.Scroll` **tem 19 precedentes** no repositório, então rolar
horizontalmente é seguro. O problema é a segunda metade do pedido: **o Power Apps não expõe a posição
de rolagem de um container.** Não dá para dizer "role até as 14h" — quem rola é o usuário, e o app não
lê nem escreve essa posição.

**Alternativa que entrega o pedido inteiro sem depender disso:** em vez de rolar, a grade desenha uma
**janela de horas** — 6 ou 8 em vez de 24 — e a janela anda. Setas para mover, e um `Timer` que avança
a janela quando o relógio vira a hora. Como a largura de tudo já é calculada sobre `mapMinutosDia`,
passar a calcular sobre `mapJanelaMin` é mudar o denominador, não a arquitetura.

Vantagens sobre a rolagem: o bloco fica maior **e** o app controla onde a janela está, que é
justamente o que a rolagem não permite. Desvantagem: perde-se a visão do dia inteiro de relance — vale
perguntar ao supervisor se ele quer poder voltar a ver 24 horas com um toque.

---

## 2. Explicar o formato da planilha de importação

**O que existe hoje:** a regra está no `importar_programacao.ts` e descrita em
`IMPORTACAO_PROGRAMACAO.md`, mas voltada para quem mantém o sistema, não para quem vai montar a
planilha.

O script lê **a primeira aba**, com **cabeçalho na linha 1**, e acha as colunas **pelo nome**, não pela
posição: `Data`, `Empresa`, `Voo`, `Rota`, `Aeronave`, uma com `Horário` e uma com `Pouso`. Pousos e
decolagens ficam na mesma aba, distinguidos pela coluna de movimento.

**O que fazer:** texto de ajuda na própria tela de importação, onde o operador está quando precisa da
informação. O `HtmlViewer` de instruções já existe lá.

---

## 3. Cores para a aviação geral — ✅ feito em 04/09/2026

**A raiz do pedido:** existia uma única entrada `GER` — "AV. GERAL" — num cinza-claro lavado
(`#E2E8F0`). Toda a aviação geral era da mesma cor, e por isso não se distinguia nada.

**O que foi feito:** bloco sem companhia de verdade (`GER` ou em branco) toma a cor da **classe da
posição** — nova tabela `colClasses`. Na aviação geral quem distingue é o porte, e o porte está na
classe: A é aeronave pequena, B é grande, mais os helipontos.

| classe | cor |
|---|---|
| A | `#0E7490` |
| B | `#C2410C` |
| HELICÓPTERO | `#7E22CE` |

**A regra da legenda continua valendo para quem tem companhia.** Só a aviação geral muda, e a legenda
diz isso nas duas telas. A classe vem da posição **do bloco**, não da linha — bloco que aparece noutra
linha por `ocupa` ou `bloqueia` mantém a cor da posição dele.

---

## 3b. Reserva com o aeroporto como ALTERNATIVA — ✅ feito em 05/09/2026

Esclarecido pelo Douglas em 04/09/2026, e **não era o que eu tinha entendido**. Não é opção de cor: é
o **aeroporto de alternativa do plano de voo**. A aeronave da aviação geral reserva a posição, mas
declara que só virá se precisar desviar — provavelmente não vem.

**Por que importa:** hoje toda reserva ocupa a posição igual. Uma reserva de alternativa segurando um
box que provavelmente não será usado tira capacidade real do pátio.

**O que foi feito**, com a decisão tomada pelo Douglas em 05/09/2026 ("faça conforme a sua
recomendação"):

- coluna `alternativa` (Number 0/1, **não obrigatória**, padrão 0) na `tb_alocacoesMapa`. Registro
  antigo fica em branco e é lido como 0 — ou seja, reserva já existente continua bloqueando como hoje;
- **selo `A` ardósia** no bloco, na frente do texto junto de `P` e `I`, porque o bloco trunca no fim.
  O bloco de reserva passa a dizer `ALTERNATIVA` em vez de `RESERVADO`, e a dica de mouse explica;
- **conflito avisa e pede confirmação no segundo toque**, no mesmo padrão do portão e da envergadura.
  A trava é por id do registro em conflito, então muda o conflito, volta a perguntar;
- o KPI **BLOQUEIOS deixou de contar alternativas**, e elas ganharam um KPI próprio.

⚠️ **A relaxação é assimétrica, de propósito.** O aviso só vale quando o que seria dobrado é uma
reserva de alternativa. Conflito com registro firme continua **bloqueando**, inclusive quando quem
chega é uma alternativa: segurar um voo confirmado por causa de uma reserva que provavelmente não vem
seria o inverso do que o pedido quer. A ordem dos ramos no SALVAR é o que garante isso — o ramo do
aviso só é alcançado quando a busca por conflito firme voltou vazia.

## 4. Matrícula quando não há número de voo

**Provavelmente já está feito.** O bloco da grade já cai para o prefixo:

```
If(
    IsBlank(_b.voo_ida) And IsBlank(_b.voo_volta),
    Coalesce(_b.prefixo, ""),
    ...
)
```

**A conferir com o supervisor:** onde ele viu faltando. Candidatos que **não** têm essa queda hoje: o
cabeçalho do painel lateral, a lista de voos do painel, e o balão de dica. Pode ser que o registro que
ele viu simplesmente estivesse sem prefixo preenchido — o que seria outro problema, de dado.

---

## 5. Botões de "aeronave no pátio" e "concluído" — ✅ concluído em 09/09/2026

**O que existe hoje:** a coluna `condicao` (`PREVISTO` / `NO PATIO` / `FINALIZADO`) e um seletor no
painel. O pedido é transformar isso em **ação de um toque**, como no app de reserva que o Mapa
absorveu — lá um ícone de avião alternava o estado direto na lista.

**Onde faria sentido:** no próprio bloco da grade, ou na lista de voos do painel lateral. Um toque
que já grava, sem abrir o formulário.

**"Trocar de cor de categoria" foi dado por atendido pelo Douglas em 09/09/2026**, sem código novo.
A condição é comunicada por **selo** (`✈` e `✓`) e, desde o item 7, finalizado também **desbota** — o
que entrega a distinção pedida sem quebrar a regra de que preenchimento = companhia. Cor de fundo por
condição foi considerada e recusada: custaria a cor da companhia ou a da classe da aviação geral.

---

## 6. Exportação e importação dos voos — 🔧 tela pronta em 09/09/2026, falta o fluxo

O supervisor pediu explicitamente por último.

**Importação já existe** (mensal, da planilha, com o fluxo). **Exportação não existe.**

**Esclarecido pelo Douglas em 09/09/2026:** *"serve para enviar a movimentação ou verificar situações
que já passaram, como se fosse o histórico. Ela pode ser feita do passado mas também do futuro para
planejar algo que irá acontecer. Praticamente uma lista em excel onde podemos usar alguns filtros,
principalmente de data, internacional, pesquisa e etc."*

**Não é ciclo de reimportação**, e isso cortou a maior parte do trabalho: o importador existente lê
programação de companhia e *calcula* posição e portão. Exportar naquele formato jogaria fora
exatamente o que o app faz. Um ciclo de verdade pediria um segundo importador, que aceitasse posições
prontas — não foi pedido e não foi feito.

**Estado:** lista `tb_exportacaoMapa` e a tela estão prontas; o fluxo está especificado passo a passo
em `EXPORTACAO_PROGRAMACAO.md` e ainda **não foi montado**. Até ele existir, os pedidos ficam parados
em `PRONTO` — a tela não quebra.

**Onde a exportação mora, e por quê:** no fim da `scrMapaImport`, não em tela própria. O menu é
duplicado nas seis telas, então tela nova custa sete colagens antes de qualquer teste; ali custa uma.
**O que se perde é descoberta** — quem procura "exportar" não rola até o fim de "Importar
programação". A promoção para tela própria é mecânica e deve pegar carona na passada do `ASUR BRASIL`,
que já precisa tocar as seis telas.

---

## Marca ASUR BRASIL — ✅ concluída em 09/09/2026

As seis telas dizem `ASUR BRASIL`. Levou de 04 a 09/09, tela a tela, cada uma na passada de outra
mudança — que era exatamente o combinado, para nenhuma colagem existir só por causa de um rótulo.

As quatro últimas (`scrMapaInicio`, `scrMapaReferencia`, `scrMapaEquip`, `scrMapaRegra`) saíram juntas
na passada em que o menu virou **IMPORTAÇÃO / EXPORTAÇÃO** — esse rótulo vive duplicado nas cinco
telas que têm menu, então a varredura já era obrigatória e a marca pegou carona.

O receio de que `ASUR BRASIL` não coubesse na `scrMapaInicio` **não se confirmou**: são ~107px num
painel que ocupa a tela menos 430px. Eu tinha superestimado o risco a partir do `letter-spacing`.

---

## 7. Filtro "mostrar finalizados" — ✅ feito em 09/09/2026

Consequência direta do item 5. Marcar um movimento como finalizado tira o registro da grade e da
lista do painel, e **não há como alcançá-lo de volta pelo app** — um toque errado no visto só se
desfaz pelo SharePoint.

O conserto natural é uma opção **mostrar finalizados** junto do botão FILTRAR que já existe na barra
da grade. Ligada, o `colDia` para de excluir `FINALIZADO`, e os registros voltam a aparecer — cinzas
pelo selo que já têm — para poderem ser desfeitos.

**A decisão que estava em aberto foi resolvida contra o bloqueio, e a razão é operacional:** movimento
finalizado significa que a aeronave saiu e a posição está **livre**. Deixar que ela volte a bloquear
faria o operador perder um box vazio só por ter ligado uma visão de histórico. O interruptor é de
visualização e nada mais — o `RemoveIf` do `colValida` é **incondicional** de propósito, e está
comentado no código para não ser "consertado" por engano.

**Como ficou:** botão `FINALIZADOS` na barra da janela, desligado por padrão. Ligado, os registros
voltam à grade e à lista do painel, **desbotados** (`opacity:.45`) além do visto que já tinham, e o
cabeçalho passa a dizer `COM FINALIZADOS` — porque com eles a contagem de registros sobe e o número
precisa se explicar. Voltar atrás é abrir o registro e trocar a condição no próprio painel.

⚠️ **Efeito visual conhecido:** o desenho de uma linha é sequencial, e blocos que se sobrepõem no
tempo são recortados. Se uma posição foi reusada por cima do horário de um movimento já finalizado, o
segundo bloco aparece truncado enquanto o filtro estiver ligado. É consequência do filtro, não
defeito de dado, e some ao desligar. Consertar exigiria dar precedência ao bloco vivo numa segunda
passada — não vale o custo enquanto for visão de exceção.

---

## Duas decisões anteriores ainda em aberto

Não vieram do supervisor, mas estão paradas esperando o Douglas:

1. **Tirar ou não o fallback do `colPosicoesAero`**, que devolve todas as posições quando o filtro por
   aeroporto não casa nada. Escondeu um defeito real em 04/09/2026.
2. **Conferir as relações de `bloqueia`** da aviação geral. Ele descreveu duas posições classe A por
   classe B; o croqui do outro app declarava quatro.

---

## O que a janela entregou do 1 e do 1b, e o que ela trocou

Feito em 05/09/2026. **A rolagem horizontal pedida não foi entregue** — foi trocada por uma janela
de horas que anda, porque o Power Apps não deixa o app posicionar nem ler a rolagem, e a segunda
metade do pedido (*acompanhar a passagem da hora*) morria aí. Detalhe do desenho e das trocas em
`ARQUITETURA_MAPA.md`, seção "A grade virou uma janela de horas".

O que o supervisor vai ver: setas para andar, o rótulo da faixa, **AGORA**, e três botões de zoom —
**6 HORAS**, **12 HORAS**, **DIA INTEIRO**. O último reproduz a grade anterior, então nada foi perdido.
A janela abre em 12 horas, começando na hora atual quando a data é hoje.

**Vale confirmar com ele:** se 12 horas é a abertura certa, ou se o dia a dia pede 6.
