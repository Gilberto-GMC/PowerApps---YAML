# Importação da programação de voos

Substitui o trabalho de recriar ~700 registros por mês copiando as caixas do mês anterior.

## As três peças, e por que a inteligência não está no fluxo

| peça | onde | faz |
|---|---|---|
| `importar_programacao.ts` | Office Script, no Excel Online | lê a planilha, pareia pouso com decolagem, aloca posição e portão, devolve JSON |
| fluxo `Importar programacao` | Power Automate | chama o script e grava o que voltou, atualizando o progresso |
| `scrMapaImport` | Power Apps | anexa o arquivo, escolhe o mês, dispara e mostra a barra |

**O fluxo é o pedaço mais burro de propósito.** Ele não pareia, não aloca e não decide nada — só
transporta. Toda a lógica está no script, que é a única das três peças que dá para **rodar sozinha e
conferir a saída** antes de existir o resto. Fluxo é a peça mais cara de depurar: erro nele aparece
como execução falhada num histórico, sem ponto de parada e sem como reproduzir com os mesmos dados.

---

## O script

### Como testar sem fluxo nenhum

1. Abra a planilha no **Excel Online** → **Automatizar** → **Novo Script**.
2. Cole o conteúdo de `importar_programacao.ts` e salve como `Importar programacao`.
3. **Executar**. O painel mostra o retorno: `ok`, `mensagem`, `total`, `registros` e `pendencias`.

Rodando contra `Programação set.26.xlsx` o esperado é **698 registros e 7 pendências**. Esse número é
o teste de regressão do script: se mudar sem a planilha ter mudado, alguma configuração foi mexida.

### O pareamento

A planilha traz pousos e decolagens em linhas separadas, sem nada que ligue um ao outro. A numeração
**não serve**: GOL `1212`→`1215` é +3, `1224`→`1225` é +1, `2165`→`1471` não tem relação, e a LATAM
mistura +1 com saltos grandes.

O que pareia é **mesma empresa + menor tempo em solo**, com rota e tipo de aeronave como desempate:

```
custo = minutos em solo + 90 se a rota difere + 30 se a aeronave difere
```

Contra setembro/26 isso pareia **699 de 702** pousos. Os 3 que sobram de cada lado são a borda do mês:
pousos do dia 30 cuja decolagem é em outubro, e decolagens do dia 1º cujo pouso foi em agosto. **Não é
falha do algoritmo — é o arquivo começando e terminando no meio de uma rotação de aeronave.**

O tempo em solo mediano é de 45 minutos. Por isso ele domina o custo: um voo que sai 40 minutos depois
por outra rota é quase sempre a mesma aeronave; um que sai 4 horas depois pela mesma rota quase nunca é.

### A alocação

Duas tentativas, nesta ordem: a preferência da companhia, depois a queda geral. Se as duas falharem,
**o voo vira pendência em vez de ir para um lugar qualquer** — posição inventada vira avião no lugar
errado, e ninguém teria como saber que foi chute.

Portão é diferente: cai para qualquer um livre, porque **portão fora do habitual incomoda menos que
portão vazio**. Cargueiro fica sem portão de propósito — não é falta de portão livre.

`T6C` consome `T5` e `T6`: ocupar uma bloqueia as outras, nos dois sentidos. É o mesmo fato que a
coluna `ocupa` de `colPosicoes` declara para a tela.

---

## ⚠️ A duplicação que não dá erro

As tabelas no topo do script — preferências, `id_posicao`, `ocupa`, equivalência IATA — são um
**espelho do `App.Formulas`**. O Office Script não consegue ler o app, então as duas convivem.

**Divergência entre elas não gera erro nenhum.** Produz alocação que a tela recusaria depois, ou pior,
que ela aceita mas que não é a que a operação combinou. Mexeu em `colPrefPosicao`, `colPosicoes` ou
`colCias`, abra o script e confira o bloco de configuração.

É o preço de ter escolhido guardar as preferências no `App.Formulas`. A alternativa seria uma lista do
SharePoint que as duas pontas leem — vale trocar se as preferências começarem a mudar com frequência.

---

## O fluxo, ação por ação

Gatilho: **SharePoint — quando um item é criado ou modificado** em `tb_importacaoMapa`,
com condição `status = PRONTO`.

1. **Atualizar item** → `status = PROCESSANDO`.
2. **Obter anexos** e **Obter conteúdo do anexo** do item.
3. Gravar o anexo numa biblioteca (o conector do Excel precisa de um arquivo com caminho).
4. **Excel Online — Executar script** → `Importar programacao`, passando `mesRef` no formato `aaaa-MM`.
5. **Atualizar item** → `total` = `total` do retorno.
6. **Aplicar a cada** sobre `registros` → **Criar item** em `tb_alocacoesMapa`.
   - A cada 25 itens, **Atualizar item** com `processados`. É isso que move a barra.
   - **Grave `ativo` explicitamente como 1.** O default da coluna em produção é `0`, e registro com
     `ativo = 0` some do app sem erro nenhum.
7. **Atualizar item** → `status = CONCLUIDO`, `criados`, `pendencias`, e `mensagem` com o resumo.
8. Em caso de erro: `status = ERRO` e a mensagem no campo `mensagem`.

> **Reimportação.** Todo registro nasce com `IMPORTACAO aaaa-MM` na observação. Antes do passo 6, o
> fluxo deve apagar o que já foi importado daquele mês, senão rodar duas vezes duplica tudo. Um campo
> próprio de origem seria melhor que a observação — fica para quando a importação sair do piloto.

---

## Antes da primeira importação

1. Criar `tb_importacaoMapa` (`lista_tb_importacaoMapa.json`) e **habilitar anexos** nela — o
   `List_Generator` cria listas com anexos desabilitados, e o anexo é o ponto central desta.
2. Cadastrar o **`B763`** em `tb_equipamentos` (Boeing 767-300F). Sem ele os voos da ABSA entram sem
   equipamento e o app recusa quando alguém for editar.
3. Conferir as envergaduras do catálogo — foram montadas de valores publicados de fabricante, não de
   fonte aeronáutica, e variante com winglet muda o número.
