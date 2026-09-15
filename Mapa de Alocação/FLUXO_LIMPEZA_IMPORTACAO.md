# Fluxo `Mapa - Limpeza das planilhas de importação`

Agendado, **mensal**. Apaga os `.xlsx` da pasta de importação com mais de **30 dias**.

## Por que existe

A cada importação o fluxo `Importar programacao` grava uma cópia da planilha (`programacao-<ID>.xlsx`)
numa pasta da biblioteca, só porque o conector do Excel não roda script sobre conteúdo binário — precisa
de arquivo com caminho. Depois da importação ninguém usa essa cópia, e nada a apaga.

**O que ele NÃO toca** (decisão do Douglas, 15/09/2026):

- o anexo original no item da `tb_importacaoMapa`, nem o próprio item;
- os CSVs da exportação;
- qualquer registro da `tb_alocacoesMapa` — isso é do `Mapa - Expurgo Diário`.

## Montagem no designer

Montado à mão, não por pacote `.zip`: "Obter arquivos (somente propriedades)" e "Excluir arquivo" não têm
precedente no repositório, e **caminho de pasta se escolhe no seletor, não se digita** — a importação grava
em `Documentos Compartilhados/importacoes`, a exportação só funcionou com `Documentos Partilhados`.

### 1. Gatilho — Recorrência

| campo | valor |
|---|---|
| Intervalo / Frequência | `1` / **Mês** |
| Fuso horário | `(UTC-03:00) Brasília` |
| Hora de início | `2026-10-01T03:00:00` |

### 2. SharePoint — Obter arquivos (somente propriedades)

Nome da ação: `Obter_planilhas_antigas`

| campo | valor |
|---|---|
| Endereço do Site | o site do AirportNow |
| Nome da Biblioteca | escolher no seletor |
| Consulta de Filtro | `Created lt '@{formatDateTime(addDays(utcNow(), -30), 'yyyy-MM-dd')}'` |
| Limitar Entradas à Pasta | **escolher no seletor** a pasta onde a importação grava as planilhas |
| Incluir Itens Aninhados | `Não` |
| Configurações → Paginação | ligada, limite `5000` |

> **`Created`, não `Modified`.** Abrir a planilha ou o script rodar sobre ela pode mexer na data de
> modificação; a de criação é a da importação e não muda.

### 3. Aplicar a cada — saída `value` do passo 2

Simultaneidade: **1**.

Dentro, uma **Condição** — trava contra apagar o que não é planilha (pasta, ou outro arquivo que alguém
largou ali):

```
@and(
    equals(items('Aplicar_a_cada')?['{IsFolder}'], false),
    endsWith(toLower(items('Aplicar_a_cada')?['{FilenameWithExtension}']), '.xlsx')
)
```

No modo básico: `IsFolder` *é igual a* `false` **E** `Nome do arquivo com extensão` *termina com* `.xlsx`.

**Se sim → SharePoint — Excluir arquivo**

| campo | valor |
|---|---|
| Endereço do Site | o site do AirportNow |
| Identificador do Arquivo | `Identificador` (do passo 2) → `@items('Aplicar_a_cada')?['{Identifier}']` |

## ⚠️ Primeira execução: a seco

Antes de ligar a exclusão, rode uma vez com o **Excluir arquivo desativado** (três pontos → *Desativar
ação*, ou troque por um `Compor` com `{FilenameWithExtension}`) e confira no histórico da execução:

1. quantos arquivos o passo 2 devolveu;
2. que **todos** são `programacao-*.xlsx` e têm mais de 30 dias.

Zero arquivos com a pasta cheia de planilhas antigas quase sempre é a pasta errada no seletor, ou o filtro
digitado com aspas trocadas. Só depois reative o Excluir.

## Recuperação

Arquivo excluído vai para a **Lixeira do site** e fica recuperável por 93 dias. E o original continua anexado
no item da `tb_importacaoMapa` — a cópia apagada nunca é a única.
