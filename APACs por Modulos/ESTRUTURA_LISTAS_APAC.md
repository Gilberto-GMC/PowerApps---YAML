# Estrutura das listas — APACs por Módulos

> ⚠️ **14/09/2026:** os JSON **não levam mais `<Default>` nem `<Validation>`** — era a causa do
> BadGateway no `List_Generator` (`ARQUITETURA_APAC.md` §15). Onde as tabelas abaixo citam valor
> padrão ou regra de validação, leia como **regra do app**, conferida pela tela antes de gravar.

Documentos irmãos:
[CONTEXTO_APAC.md](CONTEXTO_APAC.md) (regra e medições) ·
[ARQUITETURA_APAC.md](ARQUITETURA_APAC.md) (decisões)

São **cinco listas**. Os cinco JSON deste diretório já passaram no `valida_lista.js`.

---

## Caminho recomendado — o `List_Generator` (~2 min por lista)

Importe `../List_Generator/List_Generator_v2.zip`, execute o fluxo, informe o `siteUrl` e cole o
JSON. Ele cria a lista com versionamento ligado, desobriga e esconde o `Título`, tira o `Título` da
view padrão e aplica índices e validações.

**Ordem de execução:**

1. `lista_tb_apacParametros.json` — já vem com a vigência de NAVEGANTES preenchida
2. `lista_tb_apacPostosFixos.json` — já vem com Acesso C (3), Portão Principal (1) e Apoio (1)
3. `lista_tb_apacMalha.json`
4. `lista_tb_apacEscala.json`
5. `lista_tb_apacImportacao.json` — **habilitar anexos nesta**, o fluxo lê o arquivo do anexo

> **Nome interno = nome de exibição, em `snake_case`.** É proposital: elimina o risco do nome
> codificado. Se preferir rótulos amigáveis, renomeie **a exibição** depois de criada; o nome
> interno não muda junto e o app continua funcionando.

### ⚠️ Se for criar à mão

O SharePoint codifica o nome interno quando você digita o nome de exibição na criação:

```
"Hora em minutos"  →  Hora_x0020_em_x0020_minutos
```

O app referencia **nome interno**. Nascendo codificado, toda fórmula quebra, e **não tem conserto**
— a coluna precisa ser excluída e recriada. Procedimento por coluna: criar com o nome interno em
`snake_case` → **salvar** → só então renomear a exibição.

Conferir depois: `.../_layouts/15/FldEdit.aspx?List={GUID}&Field=hora_min`. Se aparecer qualquer
`_x00`, recrie.

---

## `tb_apacMalha`

A malha planejada de decolagens. Uma linha por voo.

| Coluna | Tipo | Obrig. | Índice | Observação |
|---|---|---|---|---|
| `aeroporto` | Texto (60) | sim | sim | `NAVEGANTES` |
| `competencia` | Texto (7) | sim | sim | `AAAA-MM` — é por ela que a tela do mês filtra |
| `data` | Data | sim | sim | |
| `hora_min` | Número | sim | | **minutos desde 00:00**, 0 a 1439 |
| `empresa` | Texto (30) | não | sim | |
| `voo` | Texto (20) | sim | | |
| `rota` | Texto (30) | não | | `NVT - GRU` |
| `aeronave` | Texto (10) | não | | `73H`, `320`, `295` |
| `assentos` | Número | sim | | 0 no cargueiro, de propósito |
| `tipo_voo` | Texto (30) | não | | `PASSAGEIRO_REGULAR`, `PASSAGEIRO_EXTRA`, `CARGO-REGULAR` |
| `dia_semana` | Texto (5) | não | | vem pronto do Power BI |
| `ativo` | Número | sim | sim | 1 ou 0 |

**Por que a hora é número e não Data/Hora:** minuto inteiro não tem fuso, não tem formato regional
e não some na virada do horário de verão. É a mesma escolha da `tb_alocacoesMapa`, e ela evitou a
classe de defeito que o `LICOES_APRENDIDAS` chama de "os dois formatos que não se misturam".

### Carga inicial sem fluxo

`dados/malha_AAAA-MM.csv` traz a temporada inteira já convertida, um arquivo por competência, com
as colunas na ordem da lista e a data em `dd/mm/aaaa`:

| Arquivo | Voos |
|---|---|
| `malha_2026-10.csv` | 727 |
| `malha_2026-11.csv` | 727 |
| `malha_2026-12.csv` | 814 |
| `malha_2027-01.csv` | 832 |
| `malha_2027-02.csv` | 741 |

Abra a lista → **Editar em modo de grade** → cole. Separador `;`, UTF-8 com BOM (o Excel abre com
acento certo). Um mês por vez.

---

## `tb_apacParametros`

As premissas do cálculo, por aeroporto e vigência. **A vigência mais recente é a que vale.**

| Coluna | Tipo | Padrão | O que é |
|---|---|---|---|
| `aeroporto` | Texto | | indexada |
| `vigencia_inicio` | Data | | indexada; o `SALVAR PREMISSAS` grava `Today()` |
| `pax_por_modulo_hora` | Número | 185 | capacidade do módulo — **muda de aeroporto** |
| `ocupacao_pct` | Número | 85 | % dos assentos ofertados |
| `antecedencia_min` | Número | 90 | quando o módulo abre antes da decolagem |
| `assentos_min` | Número | 150 | corte para contar decolagem |
| `apac_por_modulo` | Número | 3 | |
| `modulos_por_supervisor` | Número | 2 | máximo |
| `raiosx_disponiveis` | Número | 3 | teto físico de NVT |
| `alternativa` | Texto | `VIII` | rótulo da configuração |
| `observacao` | Texto longo | | por que essa vigência existe |
| `ativo` | Número | 1 | |

**Não editar direto na lista para simular cenário** — é para isso que serve o painel de premissas
da tela, que calcula sem gravar.

---

## `tb_apacPostosFixos`

Os postos que não dependem da malha. Somados à demanda calculada em toda hora que a faixa cobre.

| Coluna | Tipo | Observação |
|---|---|---|
| `aeroporto` | Texto | indexada |
| `posto` | Texto (60) | `ACESSO C`, `PORTAO PRINCIPAL`, `PORTAO PRINCIPAL APOIO` |
| `papel` | Texto (20) | `APAC` ou `SUPERVISOR` — validado na coluna |
| `hora_inicio` | Número | minutos; 0 nos três de hoje |
| `hora_fim` | Número | minutos; 1440 nos três de hoje |
| `quantidade` | Número | 3, 1 e 1 |
| `ordem` | Número | ordem de exibição |
| `ativo` | Número | |

Validação de lista: `hora_fim > hora_inicio`.

---

## `tb_apacEscala`

Os turnos posicionados — a metade de baixo da planilha da Simone. **A tela que consome esta lista
ainda não existe**; a estrutura vai criada para não virar migração depois.

| Coluna | Tipo | Observação |
|---|---|---|
| `aeroporto` · `competencia` | Texto | indexadas |
| `papel` | Texto | `APAC` ou `SUPERVISOR` — vigilância fica fora do app; a tela ignora outro valor |
| `rotulo` | Texto (80) | ex.: `APAC 03h–11h (intervalo 07h)` |
| `hora_inicio` | Número | minutos |
| `duracao_min` | Número | 480 = as 8 horas da jornada |
| `intervalo_inicio` | Número | minutos; opcional |
| `intervalo_min` | Número | 60 |
| `quantidade` | Número | quantas pessoas nesse turno |
| `ordem` · `ativo` | Número | |

**Por que `quantidade` é coluna e não se deduz da linha:** na planilha, o efetivo de cada turno é
lido por `MEDIAN` da linha de horas. Funciona enquanto a linha for toda igual e **quebra calado** no
dia em que um turno tiver reforço em parte das horas.

---

## `tb_apacImportacao`

O canal entre o fluxo e a barra de progresso da tela. **Habilitar anexos.**

| Coluna | Tipo | Observação |
|---|---|---|
| `aeroporto` · `competencia` | Texto | indexadas |
| `arquivo` | Texto (255) | nome do anexo |
| `status` | Texto (20) | `INICIADA`, `LENDO`, `GRAVANDO`, `CONCLUIDA`, `ERRO` |
| `total_lidos` · `total_gravados` · `total_descartados` | Número | |
| `mensagem` | Texto longo | onde o fluxo escreve o motivo quando dá errado |
| `ativo` | Número | |

⚠️ **O fluxo tem que apagar os registros da competência antes de gravar**, senão reimportar
duplica. O `importar_malha.ts` devolve a `competencia` justamente para isso.

---

## Depois de criar

1. **Limite de linhas de dados do app: 2000.** Configurações → Geral. Com 500, dezembro (814) e
   janeiro (832) chegam truncados, sem erro nenhum na tela. Ver `ARQUITETURA_APAC.md` §4.
2. Permissão: `EditPermission` da `tb_apacParametros` decide quem pode gravar vigência nova.
3. Conferir o nome das fontes no app: `tb_apacMalha`, `tb_apacParametros`, `tb_apacPostosFixos`,
   `tb_apacEscala`, `tb_apacImportacao`.
