# Colocar um aeroporto novo no Mapa de Alocação

Guia para quem mantém o app. O operador cadastra pátios, posições e hangares pela tela
**POSIÇÕES E CORES** — o guia dele está no botão **COMO CADASTRAR** daquela tela. Este documento cobre
o que **não** se faz pela tela e a ordem de tudo.

Estado em 16/09/2026. Aeroporto é identificado pelo **nome** (`NAVEGANTES`), não pelo ICAO — só neste app.

---

## O que é cadastro e o que ainda é código

| o quê | onde | quem |
|---|---|---|
| Pátios | lista `tb_patios` — tela POSIÇÕES E CORES › PÁTIOS | operador |
| Posições | lista `tb_posicoes` — tela POSIÇÕES E CORES › POSIÇÕES | operador |
| Hangares | posição com **Tipo = HANGAR** num pátio próprio | operador |
| Restrições entre posições | lista `tb_regrasPosicao` — tela RESTRIÇÕES | operador |
| Equipamentos | lista `tb_equipamentos` — tela EQUIPAMENTOS (vale para todos os aeroportos) | operador |
| Pré-posição da importação | lista `tb_prePosicao` (SharePoint, sem tela) | responsável |
| Usuários e aeroporto de cada um | lista `tb_usuariosMapa` (SharePoint, sem tela) | responsável |
| Lista de aeroportos com mapa | **derivada** dos pátios ativos em `tb_patios` + aeroporto padrão do usuário | automático |
| Portões e cores | lista `tb_portoes` (**por aeroporto**) — tela POSIÇÕES E CORES › PORTÕES | operador |
| Companhias e cores | lista `tb_companhias` (**vale para todos os aeroportos**) — tela POSIÇÕES E CORES › COMPANHIAS | operador |

> Desde 17/09/2026 portões e companhias são listas. Portão é físico, então cada aeroporto cadastra os seus;
> companhia é a mesma em qualquer aeroporto, então a lista é única — cadastrar uma companhia vale para todos.

---

## Ordem

1. **Usuários** — na lista `tb_usuariosMapa`, uma linha por pessoa. **O aeroporto não é escolhido: vem do
   usuário conectado** (e-mail do Windows/Power Apps). Não há mais tabela de aeroportos no código.
   - `email_usuario` exatamente como o do login (a tela Início mostra o e-mail de quem não tem cadastro);
   - `perfil`: **BASE** (só o próprio aeroporto), **BLOCO** ou **SEDE** (também os de `aeroportos`);
   - `aeroporto_padrao`: o nome, em maiúsculas, **igual ao gravado nas listas** (ex. NAVEGANTES) — é onde o app abre;
   - `aeroportos` (BLOCO/SEDE): nomes separados por `;`, ou `TODOS`;
   - quem **não está na lista** entra **somente leitura**.
2. **Entre no app com um usuário daquele aeroporto** (ou um SEDE/BLOCO escolhendo-o em TROCAR CONTEXTO). O
   aeroporto padrão aparece mesmo sem pátio cadastrado; tudo o que se cadastra depois vale para ele. Quando o
   primeiro pátio ativo existir, o aeroporto passa a aparecer para quem tem acesso.

> **Quando o módulo entrar no AirportNow:** o app já aceita `?aeroporto=NOME` na URL. Esse valor tem prioridade,
> mas só se for um aeroporto permitido para o usuário — trocar a URL não dá acesso a outro aeroporto.
3. **Pátios** — tela POSIÇÕES E CORES › PÁTIOS. Um por pátio físico; mais um para hangares, se houver.
4. **Posições** — tela POSIÇÕES E CORES › POSIÇÕES. Confira o **Tipo** de cada uma: vem REMOTA por padrão.
   - `OCUPA` para posição que consome outras (ex. T6C ocupa `T5,T6`).
   - Hangar: Tipo = **HANGAR**, no pátio dos hangares, sem classe, travas ou OCUPA.
5. **Restrições** — tela RESTRIÇÕES: bloqueios entre posições vizinhas e vetos de equipamento. Use o botão
   TESTAR para conferir que a regra pega algum lançamento.
6. **Pré-posição** (só se o aeroporto for **importar programação**) — na lista `tb_prePosicao`, direto no
   SharePoint:
   - uma linha por companhia: `aeroporto`, `cia` (sigla), `nome_planilha` (como a empresa aparece na
     planilha, ex. GOL), `posicoes` e `portoes` em ordem de preferência, separados por vírgula;
   - `prioridade = 1` para quem aloca antes dos demais (ex. cargueiro);
   - **uma linha `cia = *`** com a ordem de queda. **Sem ela a importação recusa** — de propósito.
   - Toda posição citada precisa existir em `tb_posicoes` com o mesmo nome; senão a importação recusa e diz qual.
7. **Confira no Mapa do Dia**: ATUALIZAR; se a grade não mudar, feche e abra o app (as posições vêm de fórmula
   nomeada e o app pode estar com a leitura antiga).

---

## Armadilhas já vistas

- **Tipo que ficou REMOTA.** Em 16/09/2026 HAVAN e POLY foram salvas sem trocar o tipo e apareceram como
  linhas na grade, sem o botão HANGARES. Sintoma = hangar na grade.
- **Renomear posição com lançamento.** O nome fica gravado em cada lançamento (`posicao_txt`); renomear
  deixa o histórico apontando para um nome que não existe mais. Crie outra e desative a antiga.
- **Trocar o código de um pátio.** Mesmo problema: cada posição guarda o código.
- **Renumerar `id_posicao`.** Nunca. Mais de 700 lançamentos apontam para esses números e nada na tela denuncia.
- **Validação com fórmula em lista nova.** O gerador de listas deste tenant recusou `=OU(...;...)` com 502 e
  deixou a lista criada pela metade (`tb_prePosicao`, 16/09/2026). O `valida_lista.js` avisa.
