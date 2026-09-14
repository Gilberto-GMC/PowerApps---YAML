# Fluxo `Importar malha APAC` — passo a passo

A tela `scrApacImport` cria um item em `tb_apacImportacao` com o export anexado e status `PRONTO`.
Esse item dispara o fluxo, que roda o Office Script `importar_malha.ts`, apaga a malha anterior das
mesmas competências e grava a nova em `tb_apacMalha`, atualizando o progresso que a tela lê.

Molde: a importação do Mapa de Alocação (`Mapa de Alocação/FLUXO_IMPORTACAO.md`), que roda neste
tenant. Onde este fluxo difere daquele, está dito por quê.

---

## 0. Antes de começar

| O quê | Como conferir |
|---|---|
| `tb_apacImportacao` e `tb_apacMalha` criadas | existem no site, com todas as colunas |
| **Anexos habilitados** em `tb_apacImportacao` | Configurações da lista → Configurações avançadas → Anexos: **Habilitado**. O `List_Generator` cria com anexos desligados, e sem eles a tela não consegue enviar o arquivo |
| Pasta **Documentos › Importar** | é a mesma que a importação do Mapa usa; se não existir, crie |
| Office Script salvo | ver passo 1 |

---

## 1. O Office Script

1. Abra o `DECOLAGENS (6).xlsx` no **Excel Online** → **Automatizar** → **Novo Script**.
2. Cole todo o `importar_malha.ts` e salve como **`Importar malha APAC`**.
3. **Executar** sem parâmetro. O retorno tem que dizer **5 competências**, com 727, 727, 814, 832 e
   741 voos.
4. No painel Scripts do Office, **⋯ do cartão → Mover script** para o SharePoint do site.

> ⚠️ O "Mover script" ignora a pasta que você escolhe e grava na pasta padrão **localizada** —
> `Documentos › Roteiros`. Criar uma pasta `Scripts` antes não adianta. Foi o que custou duas rodadas
> no Mapa. O seletor do fluxo também chama o campo de **Roteiro**.

O script já foi testado fora do Excel contra esse mesmo arquivo — `testar_importar_malha.js` confere
campo a campo contra os CSVs de `dados/`. Rodá-lo no Excel é para ver que ele compila lá.

---

## 2. Importar o pacote

**Power Automate → Meus fluxos → Importar → Pacote (herdado)** → `fluxo/ImportarMalhaAPAC.zip` →
em *Recursos relacionados*, clique na conexão do SharePoint e selecione a sua → **Importar**.

O pacote entra como **fluxo novo** (`suggestedCreationType: New`), com o nome
**`Importar malha APAC`**.

---

## 3. Três ajustes depois de importar

### 3a. Reescolher as listas

As listas estão no pacote **pelo nome**, porque o GUID de uma lista só existe depois que ela é
criada. Abra o fluxo e, em cada ação abaixo, confira se o campo **Nome da Lista** está preenchido; se
estiver em branco ou com erro, reescolha no dropdown:

| Ação | Lista |
|---|---|
| gatilho *Quando um item é criado ou modificado* | `tb_apacImportacao` |
| `Marcar_processando`, `Obter_anexos`, `Obter_conteudo_do_anexo`, `Guardar_total`, `Atualizar_barra`, `Fechar`, `Recusar`, `Marcar_erro` | `tb_apacImportacao` |
| `Obter_malha_anterior`, `Excluir_voo_anterior`, `Criar_voo` | `tb_apacMalha` |

Na `Salvar_planilha`, confira a **pasta** pelo ícone de pasta, sem digitar — caminho interno de
biblioteca em site português nem sempre é o que aparece na tela.

### 3b. Ligar a costura do Office Script

O pacote só declara a conexão do SharePoint: acrescentar o conector do Excel exigiria inventar
entradas no manifesto, e erro ali derruba a importação inteira. Então a chamada do script entra à mão.

Dentro do escopo **`Processar`**, entre **`Salvar_planilha`** e **`Resultado_script`**, adicione
**Excel Online (Business) → Executar script de uma biblioteca do SharePoint**:

| Campo | Valor |
|---|---|
| Localização da pasta de trabalho | o site do AirportNow |
| Biblioteca da pasta de trabalho | `Documentos` |
| Pasta de trabalho | **`Id`** da `Salvar_planilha` (é `corpo/ID`, não `ItemId`) |
| Localização do script | o site do AirportNow |
| Biblioteca do script | `Documentos` |
| Roteiro | `Roteiros › Importar malha APAC.osts` |
| mesRef | `competencia` do gatilho |
| aeroporto | `aeroporto` do gatilho |

Depois abra **`Resultado_script`**, apague o JSON que está dentro e ponha:

```
@outputs('Executar_script_de_uma_biblioteca_do_SharePoint')?['body/result']
```

Use o nome interno real da ação que você acabou de criar — espaço vira sublinhado. Se preferir, selecione
**result** pelo conteúdo dinâmico.

> Se rodar **sem** ligar a costura, o fluxo não apaga nem grava nada: o `Resultado_script` vem com
> `ok: false`, o fluxo cai no ramo `Recusar` e a tela mostra "COSTURA NAO LIGADA". Foi de propósito.

### 3c. Conferir a trava do gatilho

Gatilho → **⋯ → Configurações → Condições de gatilho**:

```
@equals(triggerBody()?['status'], 'PRONTO')
```

**Sem ela o fluxo entra em laço infinito**: ele altera o item que o dispara. O Verificador de fluxo
vai acusar "loop circular" nas ações que escrevem em `tb_apacImportacao` — é falso positivo enquanto a
condição estiver lá.

---

## 4. Como o fluxo é, e por que

```
Inicializar_gravados
Marcar_processando                    status PROCESSANDO — tira o item da condição de gatilho
Processar (escopo)
  Obter_anexos → Obter_conteudo_do_anexo → Salvar_planilha
  [Executar script]                   ← a costura
  Resultado_script
  Guardar_total                       total_lidos, total_descartados, arquivo, mensagem
  Conferir_resultado
    SIM  (ok, total > 0, filtro não vazio)
      Obter_malha_anterior            aeroporto + competências do arquivo
      Apagar_anteriores               10 em paralelo
      Gravar_lotes                    lotes de 50, um lote por vez
        Gravar_lote                   10 voos em paralelo
        Somar_lote → Atualizar_barra
      Fechar                          CONCLUIDO
    NÃO
      Recusar                         ERRO, com a mensagem do script — nada apagado
Marcar_erro                           se o escopo falhar
```

**Nada é apagado sem o script ter dito ok.** O filtro de exclusão (`competencia eq '2026-10' or ...`)
é montado pelo script, só com as competências que ele vai gravar, e testado fora do fluxo. Importar
dezembro não apaga outubro.

**Lotes, e não um voo por vez como no Mapa.** O fluxo do Mapa gasta cerca de quatro ações por
registro. Com 3.841 voos seriam uns 15 mil pedidos numa execução, e o limite diário de pedidos do
Power Automate para licença M365 fica abaixo disso. Em lotes de 50 com 10 em paralelo são cerca de
4 mil na primeira importação e 8 mil ao reimportar a temporada inteira (que também apaga). **Se uma
importação de TODAS falhar por limite, importe mês a mês.**

**Escopo com tratamento de falha.** No fluxo do Mapa, o `Marcar_erro` dependia de seis ações ao mesmo
tempo; como uma falha faz as ações seguintes serem *puladas*, e não *falhadas*, a condição quase nunca
fechava e o item ficava em `PROCESSANDO`. Aqui o `Marcar_erro` depende de um escopo só.

**Falhou no meio?** Importe de novo o mesmo arquivo: a reimportação apaga o que ficou pela metade antes
de gravar.

---

## 5. Como testar sem risco

1. Na tela, escolha **2026-12** (não TODAS) e anexe o export.
2. O item vai a `CONCLUIDO`, a barra chega a 100% e o resumo diz **814 gravados de 814 lidos**.
3. A `tb_apacMalha` tem 814 itens de `2026-12`.
4. Abra a tela do mês em **2026-12**: **36 APACs e 5 supervisores**.
5. **Importe de novo dezembro.** A lista continua com **814**, não 1.628 — é a prova da exclusão.
6. Só então importe **TODAS**: a lista termina com **3.841**.

---

## 6. O que não consegui verificar daqui

- **O pacote não foi importado por mim** — a validação é estrutural (`montar_fluxo_importacao.js`
  confere referências, colunas obrigatórias, colunas existentes, escopos e variáveis antes de gerar).
- **O site.** O pacote usa `https://grupoccr.sharepoint.com/sites/AIRPORTNOW`, o mesmo do Mapa. Se as
  listas APAC foram criadas em outro site, troque o *Endereço do Site* em todas as ações.
- **`chunk()`** é função padrão das expressões do Power Automate, mas não tem precedente nos fluxos
  deste repositório. Se o `Gravar_lotes` acusar expressão inválida, é aqui.
