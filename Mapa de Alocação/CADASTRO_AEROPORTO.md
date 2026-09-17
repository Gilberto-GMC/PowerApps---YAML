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
| **Lista de aeroportos** | `colAerosMapa` no `App_Formulas_Mapa.txt` | **código** |
| Portões e cores | lista `tb_portoes` (**por aeroporto**) — tela POSIÇÕES E CORES › PORTÕES | operador |
| Companhias e cores | lista `tb_companhias` (**vale para todos os aeroportos**) — tela POSIÇÕES E CORES › COMPANHIAS | operador |

> Desde 17/09/2026 portões e companhias são listas. Portão é físico, então cada aeroporto cadastra os seus;
> companhia é a mesma em qualquer aeroporto, então a lista é única — cadastrar uma companhia vale para todos.

---

## Ordem

1. **Aeroporto no app** — acrescente uma linha em `colAerosMapa` (`App_Formulas_Mapa.txt`) e cole o
   App.Formulas no Studio. O nome escrito aqui é o que todas as listas gravam em `aeroporto`: escreva igual
   em todo lugar, em maiúsculas.
2. **Troque o contexto** no app (TROCAR CONTEXTO) para o aeroporto novo. Tudo o que se cadastra depois vale
   para ele.
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
