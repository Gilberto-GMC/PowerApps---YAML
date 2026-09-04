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

## 3. Cores para a aviação geral

**Como está hoje:** o preenchimento do bloco é a cor da companhia (`colCias`), e a legenda declara
isso. Aeronave de aviação geral não tem companhia na tabela, então cai na cor de borda padrão — todas
iguais e sem significado.

**⚠️ Precisa ser esclarecido antes de fazer.** "Alternativa e diferentes cores" comporta pelo menos
duas leituras:

- cores por **categoria de aeronave** (executivo, militar, táxi aéreo, helicóptero) para os voos sem
  companhia; **ou**
- um **esquema alternativo inteiro**, que o operador liga e desliga, pintando por outro critério.

A segunda quebraria a regra da legenda de que preenchimento = companhia — regra que já foi defendida
duas vezes neste projeto. Se for essa, a legenda tem que mudar junto.

---

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
