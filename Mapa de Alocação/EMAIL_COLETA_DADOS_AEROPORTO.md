# Modelo de e-mail — coleta de dados para implantar um aeroporto no Mapa

Pedido que o responsável pela implantação manda aos supervisores do aeroporto novo. Troque
`FOZ DO IGUAÇU` pelo nome do aeroporto e ajuste os exemplos; o resto serve para qualquer um.

Quem recebe não precisa saber nada do app — o e-mail pede o que a operação já sabe de cor, na
linguagem dela. A tradução para pátio/posição/tipo é feita por quem cadastra.

> **Antes de enviar:** confirme com quem vai cadastrar se o aeroporto vai **importar programação**.
> Se for, acrescente o bloco 4 (pré-posição), que está no fim deste arquivo. Para quem não importa —
> caso de FOZ DO IGUAÇU em 27/10/2026 — o bloco 4 fica de fora.

---

## Assunto

`Mapa de Alocação de Pátio — dados das posições de FOZ DO IGUAÇU`

## Corpo

Bom dia,

Estamos implantando em FOZ DO IGUAÇU o **Mapa de Alocação de Pátio**, o módulo do AirportNow onde a
operação monta a alocação do dia e enxerga conflito de posição antes que ele aconteça. Já está em uso
em Navegantes.

Para deixar o aeroporto pronto, preciso que vocês me confirmem como o pátio é hoje. Não precisa de
formulário: pode responder este e-mail em texto mesmo, ou mandar a planilha/croqui que vocês já usam.

**1. Pátios**

Como o pátio é dividido na prática (ex. Pátio Principal, Pátio Sul, Hangares). Para cada um, o nome
pelo qual a equipe chama.

**2. Posições**

A lista das posições de cada pátio, na ordem em que vocês leem o pátio, com:

- o nome exato usado no dia a dia (ex. 1, 2A, T4) — é o nome que vai aparecer na tela e ficar gravado
  em cada alocação;
- se a posição é **ponte** (com portão) ou **remota**;
- a **maior aeronave** que entra nela (ex. A320, B738, ATR72);
- se tem limite de **comprimento ou envergadura** em metros que a equipe respeite;
- se existe posição que, ao ser usada, **inutiliza outra** (ex. ao usar a 6C não dá para usar 5 e 6);
- se alguma posição é **reservada para emergência/contingência**.

**3. Portões e hangares**

- Os números dos portões de embarque em uso.
- Os hangares existentes e o nome de cada um (ex. hangar da Poly). Hangar entra como estacionamento de
  aeronave, fora da grade do pátio.

Qualquer campo que não se aplique, é só dizer que não tem. Se houver um croqui ou tabela de posições
já pronta, ela resolve a maior parte do que está acima.

Fico à disposição para explicar o módulo e, depois que estiver cadastrado, faço uma apresentação rápida
com a equipe.

Obrigado,

---

## Bloco 4 — só para aeroporto que vai importar programação

**4. Preferência de posição por companhia**

Para a importação automática da programação, preciso saber, para cada companhia que opera aí, as
posições que ela usa **em ordem de preferência** (ex. GOL: 3, 4, 2) e os portões na mesma lógica. Se
alguma operação tem prioridade sobre as outras na hora de escolher a posição — cargueiro, por exemplo
— me diga qual.

Preciso também de uma **ordem geral de queda**: a sequência de posições a usar quando a preferência da
companhia já estiver ocupada.

---

## Depois que a resposta chegar

A ordem de cadastro e as armadilhas estão em `CADASTRO_AEROPORTO.md`. Resumo:

1. pátios (um deles só para hangares, se houver);
2. posições — **o Tipo vem REMOTA por padrão**, e hangar tem que ser HANGAR;
3. portões;
4. restrições (o que a pergunta "inutiliza outra" revelou vira OCUPA ou regra em RESTRIÇÕES);
5. conferir no Mapa do Dia.
