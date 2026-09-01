# Estrutura das listas SharePoint — Gestão de Frotas (Fase 1)

Guia de **criação manual** das listas do Módulo 1 — Cadastro de Veículos, no site SharePoint já existente.

São **2 listas**. Aeroportos, tipos, status e demais enumerações **não viram lista** — ficam em `App.Formulas`
(ver [AppFormulas_Frotas.fx.md](AppFormulas_Frotas.fx.md)).

---

## ⚠️ Leia antes de criar a primeira coluna

O **nome interno** da coluna é congelado no momento da criação e **nunca mais muda**. Se você criar a coluna já
com o nome bonito, o SharePoint codifica acento e espaço, e o resultado entra em todo `Patch` e `DataField` do
app para sempre:

```
"Data de Aquisição"  →  Data_x0020_de_x0020_Aquisi_x00e7_x00e3_o
```

### Procedimento obrigatório para CADA coluna

1. **+ Adicionar coluna** → escolher o tipo → digitar **exatamente o nome interno** da tabela
   (minúsculo, `snake_case`, sem acento, sem espaço): `data_aquisicao`
2. **Salvar.**
3. Clicar no cabeçalho da coluna → **Editar** → trocar o nome para o de exibição: `Data de Aquisição` → Salvar.

O interno continua `data_aquisicao`; só o rótulo muda. **Não pule o passo 2** — renomear antes de salvar não
funciona.

### Como conferir depois

Configurações da lista → clicar na coluna → olhar a URL:

```
.../_layouts/15/FldEdit.aspx?List={...}&Field=data_aquisicao
                                              ^^^^^^^^^^^^^^  ← nome interno real
```

Se aparecer qualquer `_x00`, a coluna precisa ser **excluída e recriada**. Não tem conserto.

A coluna nativa **`Título`** (nome interno `Title`) **não é usada neste sistema**. Nada é gravado nela — nem o
código do ativo, nem o e-mail do usuário. Cada dado fica em coluna própria, com nome interno legível. Como o
SharePoint não deixa excluir `Título`, ela é **desobrigada e ocultada** nas duas listas.

### Neutralizar a coluna `Título` — fazer nas DUAS listas

Antes de gravar o primeiro item:

1. **Configurações da lista** → **Configurações avançadas** → *Permitir gerenciamento de tipos de conteúdo?* →
   **Sim** → OK.
2. Na página de configurações, bloco **Tipos de conteúdo** → clicar **Item** → clicar **Título**.
3. Marcar **Oculto (não aparece em formulários)** → OK.
4. Voltar em **Configurações avançadas** e devolver *Permitir gerenciamento de tipos de conteúdo?* para **Não** —
   o `Título` continua oculto.
5. Remover `Título` de **todas as views** da lista.

> Se a opção **Oculto** for recusada, marque **Opcional** e tire a coluna das views. Para o app o efeito é o
> mesmo: `Patch` sem `Title` grava sem erro.
>
> Consequência aceita: sem `Título` a view do SharePoint perde a coluna que abre o item no clique — o item abre
> pelo seletor da linha. A consulta do dia a dia é pelo app, não pela lista.

---

# Lista 1 — `tb_usuariosFrota`

**Criar como:** Lista em branco → nome `tb_usuariosFrota`.
Define quem acessa o quê. É lista (e não dado local) porque muda toda semana e não pode exigir republicação do app.

| # | Nome interno | Nome de exibição | Tipo SharePoint | Obrig. | Configuração |
|---|---|---|---|---|---|
| 1 | `email_usuario` | E-mail do Usuário | Texto (uma linha) | Sim | **Indexada + Valores exclusivos = Sim** |
| 2 | `nome_usuario` | Nome | Texto (uma linha) | Sim | |
| 3 | `perfil` | Perfil | Texto (uma linha) | Sim | Valores de `colPerfil` |
| 4 | `aeroportos` | Aeroportos de Acesso | Texto (várias linhas) | Sim | **Texto sem formatação** (não Rich Text) |
| 5 | `aeroporto_padrao` | Aeroporto Padrão | Texto (uma linha) | Sim | Sigla IATA |
| 6 | `bloco_acesso` | Bloco de Acesso | Texto (uma linha) | Não | `CENTRAL`, `SUL` ou vazio |
| 7 | `pode_baixar_ativo` | Pode Dar Baixa em Ativo | Número | Não | 0 casas · **Padrão: `0`** · `1` = pode |
| 8 | `ativo` | Ativo | Número | Sim | 0 casas decimais · **Padrão: `1`** · Indexada |

### Como preencher `aeroportos`

Siglas IATA separadas por ponto e vírgula, **sem espaço**:

| Caso | Valor |
|---|---|
| Usuário de um aeroporto | `SLZ` |
| Usuário de vários | `SLZ;THE;IMP` |
| Gestor do bloco SUL | `BFH;CWB;JOI;NVT;BGX;IGU;LDB;PET;URG` |
| Administrador da rede | `TODOS` |

> Texto delimitado em vez de Escolha múltipla é proposital: coluna multi-escolha do SharePoint **não é indexável
> nem delegável**. O app faz `Split(varUsuario.aeroportos; ";")` uma vez no start e cruza com `colAeros`.

### Configuração da lista

- Configurações de versão → **Criar versões: Sim**, manter **50**.
- Anexos: **desabilitados**.
- Índices: `email_usuario`, `ativo`.
- Coluna `Título`: **desobrigada e oculta** (procedimento acima).

### Primeiro registro (crie antes de abrir o app)

| Campo | Valor |
|---|---|
| `email_usuario` | *(seu e-mail corporativo)* |
| `nome_usuario` | *(seu nome)* |
| `perfil` | `Administrador` |
| `aeroportos` | `TODOS` |
| `aeroporto_padrao` | *(a sigla que você quer que abra)* |
| `pode_baixar_ativo` | Sim |
| `ativo` | `1` |

Sem esse registro o app abre bloqueado — é o `LookUp` do `OnStart` que resolve o contexto.

---

# Lista 2 — `tb_ativosFrota` (LISTA MESTRE)

**Criar como:** Lista em branco → nome `tb_ativosFrota`.
É a tabela-pai referenciada pelos outros 22 módulos. São **52 colunas, todas criadas por você** — a nativa
`Título` não é usada (desobrigar e ocultar pelo procedimento acima). Reserve uma hora e siga na ordem.

## 2.1 Identificação

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 1 | `codigo_ativo` | Código do Ativo | Texto (uma linha) | **Não** ⚠️ | **Indexada**, **sem** valores exclusivos. Ver abaixo |
| 2 | `identificacao_visual` | Identificação Visual | Texto (uma linha) | Não | Prefixo pintado no ativo (`GPU-03`) |
| 3 | `placa` | Placa | Texto (uma linha) | Não | **Indexada.** Sem máscara: `ABC1D23` |
| 4 | `renavam` | RENAVAM | Texto (uma linha) | Não | **Texto**, não número — preserva zero à esquerda |
| 5 | `chassi` | Chassi | Texto (uma linha) | Não | 17 caracteres |
| 6 | `n_serie` | Número de Série | Texto (uma linha) | Não | Identificação do GSE sem placa |
| 7 | `n_patrimonio` | Nº Patrimônio Contábil | Texto (uma linha) | Não | Amarra com Patrimônio/Contabilidade |

### ⚠️ Sobre o código do ativo (`codigo_ativo`) — por que não é obrigatório

O plano previa esse campo **obrigatório e exclusivo**. Ao detalhar, isso não funciona, e o motivo é concreto:

O código é `FRT-` + o `ID` do SharePoint, e o `ID` **só existe depois que o item é criado**. O app grava em duas
etapas: cria o registro e, com o `ID` em mãos, escreve o código. Se `codigo_ativo` fosse obrigatório, a **primeira**
gravação seria recusada por vir em branco.

**Configuração correta:** `codigo_ativo` **não obrigatório**, **indexada**, **sem "Valores exclusivos"**.

Isso não abre brecha de duplicidade: `FRT-00042` deriva do `ID`, que o SharePoint já garante único — a
unicidade é **por construção**, e "Valores exclusivos" não acrescentaria nada além de quebrar a criação.

**Rede de segurança:** se a segunda gravação falhar (queda de rede no meio), sobra um item sem código. Por isso a
view de controle **`⚠ Sem código`** (seção 2.9) — se ela tiver linhas, houve falha e o item precisa ser
corrigido ou excluído.

## 2.2 Classificação

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 8 | `tipo_ativo` | Tipo de Ativo | Texto (uma linha) | Sim | **Indexada + validação (§2.10).** Valores de `colTipoAtivo` |
| 9 | `categoria_uso` | Categoria de Uso | Texto (uma linha) | Sim | Valores de `colCategoriaUso` |
| 10 | `marca` | Marca | Texto (uma linha) | Sim | |
| 11 | `modelo` | Modelo | Texto (uma linha) | Sim | |
| 12 | `ano_fabricacao` | Ano de Fabricação | Número | Sim | 0 casas decimais |
| 13 | `ano_modelo` | Ano do Modelo | Número | Não | 0 casas decimais |
| 14 | `cor` | Cor | Texto (uma linha) | Não | |
| 15 | `combustivel` | Combustível | Texto (uma linha) | Sim | Valores de `colCombustivel` |
| 16 | `capacidade_tanque` | Capacidade do Tanque (L) | Número | Não | 0 casas. **Necessária no módulo 8** para flagrar abastecimento acima da capacidade |
| 17 | `qtd_passageiros` | Lotação (passageiros) | Número | Não | 0 casas |
| 18 | `capacidade_carga_kg` | Capacidade de Carga (kg) | Número | Não | 0 casas |

> **Cosmético:** a view do SharePoint pode exibir `ano_fabricacao` como `2.024` (separador de milhar do locale).
> Não afeta o dado nem o app, que formata com `Text(ano_fabricacao; "0000")`.

## 2.3 Medição — as colunas que resolvem o GSE

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 19 | `tipo_medidor` | Tipo de Medidor | Texto (uma linha) | Sim | **Validação (§2.10).** Valores de `colTipoMedidor` |
| 20 | `medidor_km` | Hodômetro Atual (km) | Número | Não | 0 casas |
| 21 | `medidor_horas` | Horímetro Atual (h) | Número | Não | **1 casa decimal** |
| 22 | `medidor_data` | Data da Última Leitura | Data e Hora | Não | Incluir hora: **Sim** |
| 23 | `medidor_origem` | Origem da Última Leitura | Texto (uma linha) | Não | Valores de `colMedidorOrigem` |

> Um único plano de manutenção (módulo 7) lê `tipo_medidor` e sabe se compara km ou horas. Sem essa coluna, o GSE
> exigiria uma segunda lista mestre — exatamente o que a planilha alerta no módulo 20.

## 2.4 Localização e responsabilidade

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 24 | `aeroporto` | Aeroporto de Lotação | Texto (uma linha) | Sim | **Indexada.** Sigla IATA vinda de `colAeros` |
| 25 | `bloco` | Bloco | Texto (uma linha) | Sim | **Indexada.** `CENTRAL`/`SUL`, gravado pelo app |
| 26 | `base_operacional` | Base / Local | Texto (uma linha) | Não | Garagem, TPS, SCI, Pátio |
| 27 | `centro_custo` | Centro de Custo | Texto (uma linha) | Sim | **Indexada.** Base do TCO (módulo 13) |
| 28 | `setor_responsavel` | Setor Responsável | Texto (uma linha) | Sim | |
| 29 | `gestor_email` | E-mail do Gestor | Texto (uma linha) | Não | **Indexada** |
| 30 | `gestor_nome` | Gestor Responsável | Texto (uma linha) | Não | |

> **Por que `bloco` se o app deriva de `colAeros`?** Porque o Power BI não enxerga coleção do app. Sem essa
> coluna, todo relatório regional teria que recriar o de-para dos 16 aeroportos.
>
> **Por que `gestor_email` em texto e não coluna Pessoa?** Para permitir
> `Filter('tb_ativosFrota'; gestor_email = User().Email)` **delegável** ("meus veículos") e exportar limpo para
> o Power BI. Coluna Pessoa não é delegável em filtro.

## 2.5 Situação e ciclo de vida

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 31 | `status` | Status do Ativo | Texto (uma linha) | Sim | **Indexada + validação (§2.10)** · Padrão: `Ativo` |
| 32 | `situacao_operacional` | Situação Operacional | Texto (uma linha) | Sim | Padrão: `Disponível` |
| 33 | `motivo_situacao` | Motivo da Situação | Texto (várias linhas) | Não | **Texto sem formatação** |
| 34 | `data_situacao` | Data da Situação | Data e Hora | Não | Incluir hora: Sim |
| 35 | `ativo` | Ativo (registro) | Número | Sim | 0 casas · **Padrão: `1`** · **Indexada** |

> `status` = ciclo de vida patrimonial (`Ativo`/`Inativo`/`Baixado`).
> `situacao_operacional` = disponibilidade do dia a dia. São coisas diferentes: um veículo `Ativo` pode estar
> `Em Manutenção`. Agora as duas são manuais; a segunda passa a ser automatizada nas ondas 3 e 4.
>
> `ativo` é **flag técnica de exclusão lógica**, não aparece no formulário. Nunca excluímos ativo fisicamente —
> isso apagaria o histórico de custo e a rastreabilidade.
>
> `motivo_situacao` é o **único lugar que guarda o "porquê"** dentro do app, já que optamos por não ter lista de
> log. Tratar como campo obrigatório na tela de baixa/bloqueio.

## 2.6 Aquisição e propriedade

| # | Nome interno | Nome de exibição | Tipo | Obrig. | Configuração |
|---|---|---|---|---|---|
| 36 | `tipo_propriedade` | Tipo de Propriedade | Texto (uma linha) | Sim | Valores de `colTipoPropriedade` · Padrão: `Próprio` |
| 37 | `fornecedor_txt` | Fornecedor / Locadora | Texto (uma linha) | Não | Texto livre nesta fase |
| 38 | `id_fornecedor` | ID Fornecedor | Número | Não | 0 casas. **Criar vazia** — reservada para a Onda 3 |
| 39 | `contrato_numero` | Nº do Contrato | Texto (uma linha) | Não | |
| 40 | `data_aquisicao` | Data de Aquisição | Data e Hora | Não | Incluir hora: **Não** |
| 41 | `valor_aquisicao` | Valor de Aquisição | Número | Não | 2 casas decimais |
| 42 | `data_fim_contrato` | Fim do Contrato / Locação | Data e Hora | Não | Incluir hora: **Não** |
| 43 | `data_baixa` | Data da Baixa | Data e Hora | Não | Incluir hora: **Não** |
| 44 | `motivo_baixa` | Motivo da Baixa | Texto (várias linhas) | Não | **Texto sem formatação** |

> **`tb_fornecedores` fica para a Onda 3** (módulos 7, 8 e 14), quando oficina, posto e seguradora entram de
> verdade. Nesta fase só a locadora é preenchida, em texto livre.
>
> **Risco assumido:** texto livre entre 16 aeroportos vira "Localiza" / "LOCALIZA" / "Localiza Rent a Car".
> Como `id_fornecedor` já nasce reservada, normalizar depois é preencher a coluna — não alterar estrutura.
> Mitigação barata agora: padronizar o nome da locadora no procedimento e conferir na carga inicial.

## 2.7 Campos-espelho das próximas ondas

Criar **agora e vazias**. Custa nada e evita alterar a lista mestre com o app já publicado. Serão preenchidas por
Power Automate quando o módulo dono entrar. São elas que permitem a galeria mostrar semáforo de pendências
**sem um `LookUp` por linha**.

| # | Nome interno | Nome de exibição | Tipo | Onda | Módulo dono |
|---|---|---|---|---|---|
| 45 | `circula_lado_ar` | Circula no Lado Ar | Número | 1 | 0 casas · **Padrão: `0`** · `1` = circula. Define se os módulos 16/17/18 se aplicam |
| 46 | `doc_proximo_vencimento` | Próximo Vencimento (Documentos) | Data e Hora (sem hora) | 4 | Módulo 4 — Documentação |
| 47 | `doc_situacao` | Situação Documental | Texto (uma linha) | 4 | `Regular`/`A vencer`/`Vencido` |
| 48 | `credencial_validade` | Validade da Credencial | Data e Hora (sem hora) | 16 | Módulo 16 — Credenciamento |
| 49 | `conforme_lado_ar` | Conforme NBR 8919 | Número | 18 | 0 casas · `1` = conforme, `0` = **não verificado ainda**. Módulo 18 — Sinalização lado ar |
| 50 | `manut_proxima_data` | Próxima Manutenção (data) | Data e Hora (sem hora) | 7 | Módulo 7 |
| 51 | `manut_proximo_medidor` | Próxima Manutenção (medidor) | Número (0 casas) | 7 | Comparado com km **ou** horas conforme `tipo_medidor` |
| 52 | `observacoes` | Observações | Texto (várias linhas) | 1 | **Texto sem formatação** |

> **Por que Número (`0`/`1`) e não Sim/Não.** Coluna Sim/Não do SharePoint nasce **NULA** quando o `Patch` de
> criação não a preenche, e `NULL` não casa com `eq false` na consulta delegada — o filtro volta vazio sem erro
> nenhum (lição já registrada em `LICOES_APRENDIDAS_POWERAPPS_YAML.md`). Com Número + valor padrão `0`, o campo
> nasce preenchido e o filtro é previsível.
>
> **Como o app testa:** positivo sempre `= 1`; negativo sempre `<> 1` — nunca `= 0`, que perderia o nulo de
> qualquer registro criado fora do app.

## 2.8 Colunas nativas — o que já vem pronto

Nada a criar. Só saber que existem e que o sistema depende delas.

| Coluna | Interno | Uso no sistema |
|---|---|---|
| ID | `ID` | **Chave de relacionamento** de todas as listas-filhas e origem do código `FRT-#####` |
| Título | `Title` | **Não usada** — desobrigada e oculta. O código do ativo é `codigo_ativo` |
| Criado | `Created` | Quando foi cadastrado |
| Criado por | `Author` | Quem cadastrou |
| Modificado | `Modified` | Última alteração |
| Modificado por | `Editor` | Quem alterou por último |
| Anexos | `Attachments` | Foto do ativo, CRLV digitalizado, nota fiscal |

## 2.9 Configuração da lista mestre

### Versionamento — **fazer primeiro**

Configurações da lista → **Configurações de versão** → **Criar versões: Sim**, manter **50**.

> Esta é a rastreabilidade escolhida para o sistema. **Sem isso não existe histórico nenhum** — nem quem mudou,
> nem o que mudou. Ligar antes de cadastrar o primeiro ativo; versões não são retroativas.

### Anexos

Configurações avançadas → Anexos: **Habilitados**.

### Índices — **criar antes de carregar a base**

Configurações da lista → **Colunas indexadas** → adicionar:

`codigo_ativo` · `placa` · `aeroporto` · `bloco` · `status` · `ativo` · `tipo_ativo` · `centro_custo` · `gestor_email`

> Indexar lista que já passou de 5.000 itens **falha**. Como a frota dos 16 aeroportos deve ficar bem abaixo
> disso, criar agora é barato e definitivo.

### Views

| Nome da view | Filtro | Colunas |
|---|---|---|
| **Todos os ativos** *(padrão)* | `ativo` = `1` | `codigo_ativo`, `placa`, `identificacao_visual`, `tipo_ativo`, `marca`, `modelo`, `aeroporto`, `status`, `situacao_operacional` |
| Ativos por Aeroporto | `ativo` = `1` | idem, **agrupado por** `aeroporto` |
| Lado Ar | `ativo` = `1` **E** `circula_lado_ar` = `Sim` | + `conforme_lado_ar`, `credencial_validade` |
| Baixados | `status` = `Baixado` | + `data_baixa`, `motivo_baixa` |
| **⚠ Sem código** | `codigo_ativo` **está vazio** | `ID`, `placa`, `Created`, `Author` |

> A view padrão **não deve trazer as 52 colunas** — view larga deixa a lista lenta no navegador e não muda nada
> para o app (o Power Apps consulta por coluna, não por view).
>
> A view **⚠ Sem código** é a rede de segurança da gravação em duas etapas: se aparecer linha ali, a segunda
> gravação falhou e o item precisa ser corrigido ou excluído.

## 2.10 Validação de coluna — integridade sem criar lista

Como trocamos Escolha por Texto, alguém editando a lista **direto pelo navegador** conseguiria digitar qualquer
coisa. O app nunca faz isso (grava só valores das tabelas de `App.Formulas`), mas a lista fica exposta.

Correção sem criar lista nenhuma: **Coluna → Editar → Mais opções → Validação de coluna**.

```
=OU([status]="Ativo";[status]="Inativo";[status]="Baixado")
```

```
=OU([tipo_medidor]="Hodômetro (km)";[tipo_medidor]="Horímetro (h)";[tipo_medidor]="Ambos";[tipo_medidor]="Não se aplica")
```

```
=OU([tipo_ativo]="Veículo Leve";[tipo_ativo]="Veículo Pesado";[tipo_ativo]="Utilitário";[tipo_ativo]="Motocicleta";[tipo_ativo]="Ônibus/Micro-ônibus";[tipo_ativo]="Reboque/Semirreboque";[tipo_ativo]="Máquina/Trator";[tipo_ativo]="GSE";[tipo_ativo]="CCI/SESCINC")
```

**Mensagem do usuário:** `Valor não permitido. Use o aplicativo Gestão de Frotas para editar este campo.`

> ⚠️ **Separador depende do idioma do site.** Em site **pt-BR** use `;` (como acima). Em site **en-US** troque
> `OU` por `OR` e `;` por `,`. Se a validação for recusada ao salvar, é isso. Teste digitando um valor inválido
> logo depois de configurar.
>
> Só as **três colunas críticas** têm validação. Colocar em todas encareceria a manutenção sem ganho — e cada
> valor novo na enumeração passaria a exigir editar a lista em produção, que é justamente o que queríamos evitar.

---

## Ordem de execução recomendada

1. Criar `tb_usuariosFrota` → ligar versionamento → **desobrigar e ocultar `Título`** → criar as 8 colunas →
   criar o **seu** registro de Administrador.
2. Criar `tb_ativosFrota` → **ligar versionamento antes de qualquer coluna**.
3. **Desobrigar e ocultar `Título`** — antes de gravar o primeiro item.
4. Criar as 52 colunas na ordem das tabelas (nome interno → salvar → renomear).
5. Habilitar anexos.
6. Criar os 9 índices.
7. Aplicar as 3 validações de coluna.
8. Criar as 5 views.
9. Conferir os nomes internos pela URL (`Field=`) — procurar qualquer `_x00`.
10. Cadastrar **um ativo de teste de cada extremo**: um carro com placa e um GSE sem placa com horímetro.

## Checklist de conferência

- [ ] Nenhum nome interno contém `_x00`
- [ ] `Título` nativo **oculto e não obrigatório** nas duas listas, e fora de todas as views
- [ ] `codigo_ativo` de `tb_ativosFrota`: **não obrigatório**, indexada, **sem** valores exclusivos
- [ ] `email_usuario` de `tb_usuariosFrota`: obrigatória, indexada, **com** valores exclusivos
- [ ] Versionamento ligado nas **duas** listas
- [ ] `ativo` com valor padrão `1` nas duas listas
- [ ] `circula_lado_ar`, `conforme_lado_ar` e `pode_baixar_ativo` como **Número**, 0 casas, padrão `0`
- [ ] 9 índices criados em `tb_ativosFrota`
- [ ] 3 validações de coluna aceitas e testadas com valor inválido
- [ ] View padrão enxuta e filtrada por `ativo = 1`
- [ ] View `⚠ Sem código` criada
- [ ] Seu registro em `tb_usuariosFrota` existe com perfil `Administrador` e `aeroportos = TODOS`
