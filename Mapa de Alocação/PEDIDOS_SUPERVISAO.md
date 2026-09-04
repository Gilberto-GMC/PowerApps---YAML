# Pedidos da supervisão — 04/09/2026

Levantados pelo supervisor durante a apresentação do sistema pelo Douglas. **Nada aqui foi feito
ainda.** A ordem abaixo é a que ele indicou; a exportação fica por último por decisão dele.

Cada item traz o que já existe no app e o que ainda precisa ser decidido — porque metade deles tem
mais de uma leitura possível, e escolher errado custa mais que perguntar.

---

## 1. Grade de 10 em 10 minutos

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

## 1b. Bloco pequeno demais: rolagem horizontal em vez do dia inteiro na página

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

## 3b. Reserva com o aeroporto como ALTERNATIVA — a fazer

Esclarecido pelo Douglas em 04/09/2026, e **não era o que eu tinha entendido**. Não é opção de cor: é
o **aeroporto de alternativa do plano de voo**. A aeronave da aviação geral reserva a posição, mas
declara que só virá se precisar desviar — provavelmente não vem.

**Por que importa:** hoje toda reserva ocupa a posição igual. Uma reserva de alternativa segurando um
box que provavelmente não será usado tira capacidade real do pátio.

**A desenhar, e a decisão não é de quem programa:**

- coluna nova em `tb_alocacoesMapa` (`alternativa`, 0/1), do mesmo feitio de `pesquisado` e
  `internacional`, com marca visual própria no bloco;
- **conflito: bloqueia ou avisa?** Se uma reserva de alternativa impedisse um voo confirmado de
  entrar, o pátio perderia posição por um voo que provavelmente não vem. O padrão de aviso com
  confirmação no segundo toque, já usado no portão e na envergadura, parece o caminho — mas é decisão
  da operação.

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

## 5. Botões de "aeronave no pátio" e "concluído"

**O que existe hoje:** a coluna `condicao` (`PREVISTO` / `NO PATIO` / `FINALIZADO`) e um seletor no
painel. O pedido é transformar isso em **ação de um toque**, como no app de reserva que o Mapa
absorveu — lá um ícone de avião alternava o estado direto na lista.

**Onde faria sentido:** no próprio bloco da grade, ou na lista de voos do painel lateral. Um toque
que já grava, sem abrir o formulário.

**⚠️ "Trocar de cor de categoria" precisa ser esclarecido.** Pode ser: o bloco muda de cor conforme a
condição — o que colide de novo com preenchimento = companhia. Ou pode ser outra coisa, ligada ao
item 3. Perguntar antes de desenhar.

---

## 6. Exportação e importação dos voos

O supervisor pediu explicitamente por último.

**Importação já existe** (mensal, da planilha, com o fluxo). **Exportação não existe.**

**A esclarecer:** exportar o quê — um dia, um mês, o pátio inteiro? E para quê: reimportar em outro
ambiente, mandar para quem não tem acesso ao app, ou guardar histórico? A resposta muda o formato.

**Se for para reimportar**, o formato de saída deveria ser o mesmo que a importação lê, para o ciclo
fechar. E aí vale reusar o `importacao_set26.csv`, que já tem a ordem de colunas correta da lista.

---

## Duas decisões anteriores ainda em aberto

Não vieram do supervisor, mas estão paradas esperando o Douglas:

1. **Tirar ou não o fallback do `colPosicoesAero`**, que devolve todas as posições quando o filtro por
   aeroporto não casa nada. Escondeu um defeito real em 04/09/2026.
2. **Conferir as relações de `bloqueia`** da aviação geral. Ele descreveu duas posições classe A por
   classe B; o croqui do outro app declarava quatro.
