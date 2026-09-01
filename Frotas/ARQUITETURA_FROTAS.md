# Arquitetura — Sistema de Gestão de Frotas | Motiva Aeroportos

Documento de referência da arquitetura de dados e de aplicação. Vale para os **23 módulos** mapeados em
`Gestao_Frotas_Mapa_Modulos.xlsx` (604 H/H, 16 aeroportos), não só para o Módulo 1.

Documentos irmãos:
[ESTRUTURA_LISTAS_FROTAS.md](ESTRUTURA_LISTAS_FROTAS.md) (criação das listas) ·
[AppFormulas_Frotas.fx.md](AppFormulas_Frotas.fx.md) (dados estáticos e tema)

---

## 1. Decisões estruturais

| Decisão | Escolha | Por quê |
|---|---|---|
| Chave do ativo | Código patrimonial `FRT-#####` em `codigo_ativo` | GSE, dolly e máquina **não têm placa**. A planilha alerta no módulo 20: *"a chave não pode ser 'placa'"* |
| Coluna `Title` | **Não usada** — desobrigada e oculta nas duas listas | Campo genérico do SharePoint. Todo dado fica em coluna própria de nome interno legível |
| Lista mestre | Uma (`tb_ativosFrota`) + extensões 1-para-1 | Multa, manutenção e abastecimento não precisam saber se é carro ou GSE |
| Relacionamento | Chave `ID` numérica resolvida no app | Coluna Lookup limita a 12 por view, quebra delegação e trava a exclusão do pai |
| Rastreabilidade | Versionamento nativo + colunas de autoria | Decisão do gestor. Zero código, zero lista de log |
| Topologia | Um site, uma base, coluna `aeroporto` indexada | Um app, um Power BI, uma manutenção para os 16 aeroportos |
| Dados estáticos | `App.Formulas`, não lista | Menos conexão, menos consulta no start, menos permissão para governar |
| Exclusão | Lógica (`ativo = 0`), nunca física | Apagar ativo apagaria o histórico de custo e a rastreabilidade |

### Limite conhecido da rastreabilidade escolhida

O versionamento nativo do SharePoint **não é legível de dentro do app nem pelo Power BI**, e não guarda
justificativa da mudança. Onde isso pesa: módulos **16** (credenciamento, RBAC 107) e **22** (ESO, RBAC 153),
em que auditoria da ANAC costuma pedir o histórico apresentável.

Mitigação atual: a coluna `motivo_situacao` guarda o "porquê" da última mudança de situação, e é obrigatória na
tela de baixa/bloqueio.

Se a exigência aparecer, uma `tb_logAuditoria` central entra depois **sem alterar nada do que já existe** — os
módulos passam a gravar nela por Power Automate. A decisão de hoje não fecha essa porta.

---

## 2. Critério: dado local ou lista SharePoint?

O sistema evita lista sempre que possível. Cada lista a menos é uma conexão a menos no app, uma consulta a menos
na abertura e uma permissão a menos para governar entre 16 aeroportos.

### Vai para `App.Formulas` (named formula)

Quando **as três** forem verdadeiras:

- O conteúdo é **estável** (muda uma ou duas vezes por ano, no máximo)
- Só **quem desenvolve** altera — não o usuário final
- Cabe confortavelmente em memória (dezenas de linhas, não milhares)

Exemplos: os 16 aeroportos, tipos de ativo, status, combustíveis, roteiro de checklist de vistoria (módulo 3),
itens de sinalização NBR 8919 (módulo 18), categorias de infração (módulo 6).

### Vira lista SharePoint

Quando **qualquer uma** for verdadeira:

- Cresce sem parar (todo lançamento é uma linha nova)
- É alimentada pelo **usuário final** pelo app
- Precisa mudar **sem republicar** o app
- O Power BI precisa consumir o histórico

Exemplos: ativos, usuários, BDV, abastecimentos, ordens de serviço, multas, vistorias.

### Named formula, não `ClearCollect` no `OnStart`

Para o dado estático, `colX = Table(...)` em `App.Formulas` custa **zero** na abertura do app (calcula sob
demanda) e a leitura é idêntica a uma coleção. A única restrição — não pode `Collect`/`Patch` dentro — não afeta
dado estático.

---

## 3. Modelo de dados

### 3.1 A mestre e seus satélites

```
                        tb_ativosFrota          ← 1 registro por ativo, seja carro, GSE ou CCI
                  (codigo_ativo = FRT-00042)
                              │  ID
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
  EXTENSÕES 1-p-1        TRANSAÇÕES N            ESPELHOS
  (Onda 4)               (Ondas 1 a 6)           (colunas na própria mestre)
        │                     │                     │
  tb_ativoGSE            tb_bdv                medidor_km / medidor_horas
  tb_ativoCCI            tb_abastecimentos     doc_proximo_vencimento
                         tb_ordensServico      credencial_validade
                         tb_multas             conforme_lado_ar
                         tb_vistorias          manut_proxima_data
                         tb_credenciais
```

### 3.2 Padrão obrigatório de toda lista-filha

Toda lista criada daqui em diante repete estas quatro colunas:

| Coluna | Tipo | Papel |
|---|---|---|
| `id_ativo` | Número (0 casas), **indexada** | Chave estrangeira para `tb_ativosFrota.ID` |
| `cod_ativo_txt` | Texto (uma linha) | `FRT-00042` redundante — leitura humana e Power BI sem `LookUp` |
| `aeroporto` | Texto (uma linha), **indexada** | Recorte de acesso e de delegação |
| `ativo` | Número (0 casas), **indexada** | Exclusão lógica |

Listas com volume alto ganham ainda uma coluna de data **indexada** (`data_evento`, `data_lancamento`), porque é
por ela que a consulta inicial é limitada.

> **Por que `cod_ativo_txt` redundante?** Sem ele, cada linha de galeria faria um `LookUp` na mestre só para
> exibir o código do veículo. Numa galeria de 50 linhas isso são 50 consultas. O custo de gravar um texto a mais
> é irrelevante perto disso.

### 3.3 Chave do ativo — `FRT-#####`

Sequencial **global**, sem sigla de aeroporto. O módulo 12 prevê frota compartilhada entre os 16 aeroportos:
um código com sigla ficaria mentiroso na primeira transferência. **Aeroporto é atributo mutável, nunca chave.**

O código deriva do `ID` do SharePoint, o que dispensa contador paralelo e elimina a corrida entre 16 aeroportos
cadastrando ao mesmo tempo:

```powerfx
Set(
    varNovoAtivo;
    Patch('tb_ativosFrota'; Defaults('tb_ativosFrota'); { /* campos do formulário */ ativo: 1 })
);;
If(
    !IsBlank(varNovoAtivo.ID);
    Patch('tb_ativosFrota'; varNovoAtivo; { codigo_ativo: "FRT-" & Text(varNovoAtivo.ID; "00000") });
    Notify("Falha ao criar o ativo. Nenhum registro foi gravado."; NotificationType.Error)
)
```

Duas escritas, zero colisão. A guarda `IsBlank` evita o padrão de gravação sem verificação já registrado em
`LICOES_APRENDIDAS_POWERAPPS_YAML.md`. A view **`⚠ Sem código`** cobre a falha da segunda escrita.

### 3.4 Como carro, GSE e CCI convivem na mesma lista

O que normalmente força duas listas mestres é o medidor: carro tem hodômetro, GSE tem horímetro. Aqui isso vira
**dado**, não estrutura:

| Ativo | `tipo_ativo` | `placa` | `n_serie` | `tipo_medidor` | Medidor usado |
|---|---|---|---|---|---|
| Gol da administração | `Veículo Leve` | `ABC1D23` | — | `Hodômetro (km)` | `medidor_km` |
| GPU do pátio | `GSE` | — | `GPU-88213` | `Horímetro (h)` | `medidor_horas` |
| CCI do SESCINC | `CCI/SESCINC` | `XYZ4E56` | `CCI-02` | `Ambos` | os dois |

A tabela `colTipoAtivo` (em `App.Formulas`) carrega `ExigePlaca` e `MedidorPadrao`, então o formulário sabe o que
exigir sem `If` encadeado, e o plano de manutenção do módulo 7 lê `tipo_medidor` para saber se compara km ou horas.

**Consequência prática:** os módulos de multa, manutenção, abastecimento e custo funcionam para GSE sem uma linha
de código específica.

### 3.5 Campos-espelho

A mestre guarda o **resumo**; o módulo guarda o **detalhe**.

| Espelho na mestre | Detalhe no módulo | Quem grava |
|---|---|---|
| `medidor_km` / `medidor_horas` / `medidor_data` | `tb_bdv`, `tb_abastecimentos` | Power Automate no item criado |
| `doc_proximo_vencimento` / `doc_situacao` | `tb_documentosAtivo` | Fluxo diário |
| `credencial_validade` | `tb_credenciais` | Fluxo na emissão/renovação |
| `conforme_lado_ar` | `tb_checklistLadoAr` | Fluxo no fechamento do checklist |
| `manut_proxima_data` / `manut_proximo_medidor` | `tb_ordensServico` | Fluxo no fechamento da OS |

É o que permite a galeria de frota exibir semáforo de pendências **sem um `LookUp` por linha**. Todas essas
colunas já existem vazias na mestre desde o Módulo 1, para não alterar a lista com o app publicado.

---

## 4. Regras de performance

Herdadas de `LICOES_APRENDIDAS_POWERAPPS_YAML.md` e obrigatórias em toda tela deste sistema.

- **Nunca** `ClearCollect` de lista histórica. Galeria consulta a lista direto com `Filter` delegável.
- Consulta inicial **sempre limitada**: `ativo = 1` + `aeroporto` + (nas transacionais) intervalo de data.
- Toda galeria com `DelayItemLoading: =true` e `LoadingSpinner: =LoadingSpinner.Data`.
- Todo campo de busca com `DelayOutput: =true` — sem isso cada tecla dispara consulta.
- Busca por `StartsWith(...)`, nunca `Search()` sobre lista SharePoint (`Search` não delega).
- **Nunca** `CountRows`/`CountIf` sobre lista SharePoint. Contador da galeria = `Gallery.AllItemsCount`, com o
  rótulo **"REGISTROS CARREGADOS"** (é o que o número significa — nunca "ENCONTRADOS").
- `LookUp` repetido na mesma fórmula = uma consulta por repetição **por linha de galeria**. Envolver em
  `With({ _x: LookUp(...) }; ...)`.
- `Refresh` só depois de gravação/exclusão ou em ação explícita do usuário. Nunca ao trocar de aba.
- Timer de monitoramento: comparar o maior `ID`, nunca `CountRows`; intervalo ≥ 30s; e **sempre** condicionado à
  visibilidade da seção (timer com `AutoStart` + `Repeat` continua rodando com a seção invisível).

### Escopo em produção: só o Módulo 1

Enquanto apenas o Módulo 1 está no ar, o app **não lê nem escreve** campo de módulo que não existe. Não é só
questão de não mostrar: cálculo sobre coluna vazia produz número que parece diagnóstico e não é.

| Fora do app hoje | Volta quando entrar |
|---|---|
| `doc_situacao`, `doc_proximo_vencimento` | Módulo 4 — Documentação |
| `conforme_lado_ar` | Módulo 18 — Sinalização lado ar |
| `credencial_validade` | Módulo 16 — Credenciamento |
| `manut_proxima_data` | Módulo 7 — Manutenção |
| `id_fornecedor` | Módulo 14 — Fornecedores (Onda 3) |

As colunas continuam criadas e vazias na lista mestre — essa foi sempre a decisão, para não alterar estrutura
com o app publicado. O que mudou é que a **projeção do cache** e a **interface** param no Módulo 1.

O painel passou a medir integridade do próprio cadastro: ativo sem código FRT, sem leitura de medidor, sem placa
onde o tipo exige, sem gestor responsável, e registros fora do status Ativo. Tudo isso é dado que o Módulo 1
preenche — logo, é pendência real, acionável hoje.

### Campo-espelho antes do módulo dono existir

`conforme_lado_ar` é `0` para toda a frota hoje, porque o módulo 18 ainda não existe para preenchê-lo. Isso não
significa "não conforme" — significa **não verificado**. O painel diz exatamente isso ("Lado ar sem verificação
· aguardam o módulo 18") e não conta essa contagem como pendência crítica na leitura do dia.

Vale para todo campo-espelho: enquanto o módulo dono não entra, o valor default é ausência de dado, e a
interface tem que dizer ausência de dado. Chamar `0` de "não conforme" seria inventar um diagnóstico
regulatório que ninguém fez.

### Cache da mestre em coleção — e por que isso não contradiz a regra acima

As regras acima valem para lista **transacional** (BDV, abastecimento, OS): crescem sem teto, então a galeria
consulta a lista direto, com `Filter` delegável e recorte por data.

A mestre é outro caso: **um registro por ativo**, limitada pelo tamanho físico da frota. Ela é carregada uma vez
por sessão em `colFrota`, com uma consulta **delegável por aeroporto do perfil** (`ativo = 1` e
`aeroporto = ...`, ambos indexados), projetando só as colunas que as telas leem (`ForAll` + record).

O que isso compra: KPI, contagem por aeroporto, busca e filtro **sem uma consulta sequer** depois do login — e
sem `CountRows` sobre SharePoint, que não delega e devolveria número errado.

O que isso cobra: limite de linhas do app em **2000** e um aviso quando o cache trunca (`varCacheTruncado`).
Recarga só em ação explícita (botão ATUALIZAR, com trava de reentrância) ou depois de gravação.

### O limite que realmente importa

A frota dos 16 aeroportos fica bem abaixo dos 5.000 itens por view. **O risco está nas listas transacionais**:
`tb_bdv` com 16 aeroportos lançando diariamente passa de 5.000 no primeiro ano.

Por isso toda lista-filha nasce com `id_ativo`, `aeroporto` e a coluna de data **indexados**, e a tela sempre
aplica um recorte de período. Índice tem que ser criado **antes** de a lista crescer — indexar lista que já
passou de 5.000 itens falha.

Atenção também ao **limite de linhas do app** (Configurações → Geral): o padrão é 500. Qualquer coleção que
carregue mais que isso trunca **em silêncio**.

---

## 5. Camada de aplicação

### 5.1 Convenções

| Item | Padrão |
|---|---|
| Lista | `tb_camelCase` — `tb_ativosFrota` |
| Coluna | `snake_case` minúsculo sem acento — `data_aquisicao` |
| Named formula (dado) | `colX` — `colAeros`, `colTipoAtivo` |
| Named formula (tema) | `thmX` — `thmPrimaria`, `thmEsp` |
| Variável global | `varX` — `varAeroUser` |
| Tela | `scrX` — `scrFrotaLista` |
| Controle | `txt`/`drp`/`btn`/`lbl`/`gal`/`cnt` + descritivo |

**Locale:** `.pa.yaml` sempre **invariante** (`,` argumentos, `.` decimal). Snippet de barra de fórmulas
(`App.Formulas`, `App.OnStart`) sempre **pt-BR** (`;`, `;;`, vírgula decimal). Não misturar.

### 5.2 Contexto do usuário

`App.OnStart` faz **uma única consulta**: `LookUp('tb_usuariosFrota'; email_usuario = User().Email And ativo = 1)`.
Dali saem `varAeroUser`, `varPerfilNivel` e `varAerosPermitidos`. Nenhuma consulta de aeroporto — `colAeros`
já está em memória.

Usuário sem cadastro não abre o app com contexto vazio: `varAcessoLiberado = false` leva à tela de bloqueio.

### 5.3 Telas do Módulo 1

| Tela | Papel | Estado |
|---|---|---|
| `scrLoginContexto` | Resolve perfil e aeroporto, carrega o cache, trata usuário não cadastrado | **entregue** |
| `scrFrotaPainel` | Painel: KPIs, distribuição por aeroporto, pendências dos campos-espelho | **entregue** |
| `scrFrotaLista` | Busca e filtros sobre o cache, detalhe do ativo em painel lateral | **entregue** |
| `scrFrotaFicha` | Ficha em abas; as abas dos módulos futuros já aparecem desabilitadas | a fazer |
| `scrFrotaForm` | Cadastro e edição; campos dirigidos por `colTipoAtivo` e `colTipoMedidor` | **entregue** |
| `scrFrotaBaixa` | Baixa/inativação; exige `motivo_situacao` e respeita `pode_baixar_ativo` | a fazer |

### 5.5 Navegação — trilho lateral

Com 23 módulos no horizonte, navegação por botão solto na barra não escala. Todas as telas internas abrem dentro
de um **shell horizontal**: trilho fixo à esquerda + conteúdo à direita.

```
cntShell{Tela}  (horizontal)
├── cntMenu{Tela}   largura 236 aberto / 76 recolhido
│   ├── marca (wordmark completo aberto, "MF" recolhido)
│   ├── navegação: PAINEL · CONSULTAR FROTA · NOVO ATIVO
│   ├── próximos módulos (só com o menu aberto)
│   └── rodapé: usuário, perfil, base · RECOLHER · TROCAR CONTEXTO
└── cnt{Tela}Raiz   (a tela como era: barra de título + corpo)
```

Três decisões:

- **Não é componente.** Componente de canvas vive fora do `.pa.yaml` de tela e não sobrevive a colar/recolar.
  O trilho é replicado em cada tela por gerador (`aplicar_menu.py`), com sufixo por tela (`Pnl`, `Lst`, `Frm`)
  porque **nome de controle é único no app inteiro**.
- **Estado global, não de tela.** `varMenuAberto` é `Set`, não `UpdateContext` — recolher em uma tela mantém
  recolhido nas outras. Nasce `true` na `scrLoginContexto`.
- **O item ativo é literal, não calculado.** Cada tela nasce sabendo quem ela é; nada de `If` comparando
  `App.ActiveScreen` em três botões por tela.

A barra roxa de cada tela ficou só com **título + ação daquela tela** (ATUALIZAR no painel, NOVO ATIVO na lista,
CANCELAR/SALVAR no formulário). Navegar é papel do trilho.

O bloco "próximos módulos" não é enfeite: é o que mostra ao usuário que Ficha, Baixa, BDV, Documentação e
Vistorias estão previstos — e é onde cada um vira item real quando a onda entrar.

Identidade visual: **Design System Motiva** — roxo `#391694`, canto reto, bloco de 26 px, título em caixa alta.
Todo cartão, chip e barra é HTML dentro de `HtmlViewer` (menos controle na tela = menos render), e toda cor sai
de token `hx*`/`thm*`. Ver `AppFormulas_Frotas.fx.md`, seção 3.

### 5.4 Perfis

| Perfil | Nível | Pode |
|---|---|---|
| Administrador | 5 | Tudo, em todos os aeroportos |
| Gestor de Frota | 4 | Tudo nos aeroportos do seu acesso |
| Operador | 3 | Cadastrar e editar; não dá baixa |
| Condutor | 2 | Consultar; lançar BDV e vistoria (ondas seguintes) |
| Consulta | 1 | Somente leitura |

Baixa de ativo é ação sensível e fica em coluna própria (`pode_baixar_ativo`), separada do perfil — um Operador
específico pode receber a permissão sem virar Gestor.

---

## 6. Roteiro das ondas

Segue a sequência da aba "Sequencia sugerida" da planilha. Nenhuma onda exige alterar a lista mestre.

| Onda | Módulos | Listas novas | Observação |
|---|---|---|---|
| **1 — Fundação** | 1, 2, 3, 4 | `tb_ativosFrota`, `tb_usuariosFrota`, `tb_documentosAtivo`, `tb_bdv`, `tb_vistorias`, `tb_vistoriaItens` | O **roteiro do checklist** de vistoria é dado estático → `App.Formulas` |
| **2 — Conformidade aeroportuária** | 16, 17, 18 | `tb_credenciais`, `tb_habilitacaoArea`, `tb_checklistLadoAr` | Bloco regulatório (RBAC 107/153). Envolve Segurança Aeroportuária, não só Frotas. Itens NBR 8919 também estáticos |
| **3 — Operação e custo** | 5, 6, 7, 8, 12, 14 | `tb_condutores`, `tb_multas`, `tb_ordensServico`, `tb_abastecimentos`, `tb_reservas`, `tb_fornecedores` | Aqui `id_fornecedor` da mestre deixa de ser vazia |
| **4 — Ativos especiais** | 19, 20, 21 | `tb_peso`, `tb_ativoGSE`, `tb_ativoCCI` | Extensões 1-para-1. `colAeros.Cat`/`.Classe` já atendem o SESCINC |
| **5 — Risco e inteligência** | 10, 22, 13 | `tb_sinistros`, `tb_esoVeiculo` | Módulo 13 (TCO) é predominantemente Power BI. **Módulo 22 deve reusar Ocorrências do Airport Now**, não duplicar |
| **6 — Complementos** | 9, 11, 15, 23 | `tb_telemetria`, `tb_pneus`, `tb_baixaAtivo`, `tb_frotaTerceiros` | Módulo 9 depende de contrato/API externa. Módulo 23 espelha 16/17/18 para `tipo_propriedade = Terceiro/Contratada` |

### Pendências a validar com as áreas antes de especificar

Levantadas pela própria planilha e ainda em aberto:

- **Módulo 2 (BDV):** o registro é por turno, por viagem ou por dia?
- **Módulo 5 (Condutores):** integrar com a base de RH para evitar cadastro duplicado?
- **Módulo 18:** confirmar a lista de itens de sinalização com Segurança Operacional
- **Módulo 19 (PESO):** como o PESO é controlado hoje?
- **Módulo 21:** o SESCINC já possui sistema próprio?
- **Módulo 22:** confirmar o reuso do módulo de Ocorrências do Airport Now
- **Módulo 15:** alinhar com Patrimônio/Contabilidade antes de modelar a baixa
- **Geral:** os H/H da planilha são preliminares e não foram validados com o setor de Frotas

### Extensões 1-para-1 previstas (Onda 4)

| Lista | Campos exclusivos | Liga por |
|---|---|---|
| `tb_ativoGSE` | Tipo de equipamento (rebocador, GPU, escada, belt loader, ambulift, varredeira, trator de bagagem, plataforma), itens NBR 8919, PESO vinculado, plano de manutenção por horímetro | `id_ativo` único |
| `tb_ativoCCI` | Reserva técnica de água, agentes extintores e estoque, teste de desempenho, status "CCI em Linha" | `id_ativo` único |

O ativo continua **um só registro** na mestre. Multa, manutenção e abastecimento não sabem — nem precisam saber —
que o ativo é um GSE.
