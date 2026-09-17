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
| Usuários e aeroporto de cada um | lista **`User`** do AirportNow (a mesma do SAFETY e da Gestão de Chamados) | administrador do AirportNow |
| Lista de aeroportos com mapa | **derivada** dos pátios ativos em `tb_patios` + aeroporto padrão do usuário | automático |
| Portões e cores | lista `tb_portoes` (**por aeroporto**) — tela POSIÇÕES E CORES › PORTÕES | operador |
| Companhias e cores | lista `tb_companhias` (**vale para todos os aeroportos**) — tela POSIÇÕES E CORES › COMPANHIAS | operador |

> Desde 17/09/2026 portões e companhias são listas. Portão é físico, então cada aeroporto cadastra os seus;
> companhia é a mesma em qualquer aeroporto, então a lista é única — cadastrar uma companhia vale para todos.

---

## Ordem

1. **Usuários** — na lista **`User`** do AirportNow, que o Mapa só lê. **O aeroporto não é escolhido: vem do
   usuário conectado.** Não há tabela de aeroportos do Mapa no código.
   - o usuário é achado por `?USUARIO=<ID>` na URL (como o hub AirportNow abre os módulos) ou, sem parâmetro,
     pela coluna **`Email`** igual ao login (a tela Início mostra o e-mail de quem não é achado);
   - **`Aeroporto`**: o nome, em maiúsculas, **igual ao gravado nas listas do Mapa** (ex. NAVEGANTES) — é onde o app abre;
   - **`Perfil`**: **Base** (só o próprio aeroporto), **Bloco** (os aeroportos do mesmo `Bloco`) ou **Sede** (todos);
   - o bloco de cada aeroporto vem de `colAerosRede` no App.Formulas — a mesma tabela `nfAeros` do SAFETY;
   - quem **não está na lista** entra **somente leitura**.
2. **Entre no app com um usuário daquele aeroporto** (ou um SEDE/BLOCO escolhendo-o em TROCAR CONTEXTO). O
   aeroporto padrão aparece mesmo sem pátio cadastrado; tudo o que se cadastra depois vale para ele. Quando o
   primeiro pátio ativo existir, o aeroporto passa a aparecer para quem tem acesso.

> **Quando o módulo entrar no AirportNow:** o app já aceita `?USUARIO=<ID>`, a mesma convenção do SAFETY.
>
> ⚠️ **E o mesmo limite do SAFETY:** quem trocar o ID na URL é tratado como outro usuário (outro aeroporto e
> perfil). Aeroporto e perfil no app são **organização da tela, não segurança**. O que impede gravar de verdade é a
> **permissão do SharePoint** nas listas — é ela que precisa estar certa para quem não pode editar.
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
