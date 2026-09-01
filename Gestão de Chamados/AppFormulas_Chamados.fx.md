# `App.Formulas` — Gestão de Chamados

Named formulas do módulo. Cola direto na propriedade **`Formulas`** do objeto
**App** no Power Apps Studio.

> **Locale:** este arquivo está na sintaxe da **barra de fórmulas em pt-BR** —
> separador de argumentos `;`, encadeamento `;;`, decimal com vírgula. O YAML
> `.pa.yaml` das telas continua em sintaxe **invariante** (`,`). Não misturar os
> dois: o que está aqui é para colar no Studio, não para colar em YAML.

Named formula é reavaliada sob demanda e **não** ocupa o `OnStart`. Catálogo em
named formula = zero consulta ao SharePoint e zero espera na abertura do app.
Named formula **não enxerga variáveis** — se precisar do usuário logado, é
variável, não named formula.

---

## 1. Catálogo de temas

```powerfx
nfCategorias =
Table(
    {Chave: "RESET_SENHA"; Nome: "Reset de senha";                  Ciclo: "SUPORTE"; Prioridade: "MEDIA";  Roteiro: "NAO"; Auto: "SIM"; SlaResposta: 0;  SlaSolucao: 0;  Ordem: 1};
    {Chave: "ACESSO";      Nome: "Acesso e permissão";              Ciclo: "SUPORTE"; Prioridade: "ALTA";   Roteiro: "NAO"; Auto: "NAO"; SlaResposta: 4;  SlaSolucao: 8;  Ordem: 2};
    {Chave: "ERRO";        Nome: "Erro no sistema";                 Ciclo: "SUPORTE"; Prioridade: "ALTA";   Roteiro: "NAO"; Auto: "NAO"; SlaResposta: 4;  SlaSolucao: 8;  Ordem: 3};
    {Chave: "DADO";        Nome: "Correção de dado ou registro";    Ciclo: "SUPORTE"; Prioridade: "MEDIA";  Roteiro: "NAO"; Auto: "NAO"; SlaResposta: 8;  SlaSolucao: 24; Ordem: 4};
    {Chave: "DESEMPENHO";  Nome: "Lentidão ou desempenho";          Ciclo: "SUPORTE"; Prioridade: "MEDIA";  Roteiro: "NAO"; Auto: "NAO"; SlaResposta: 8;  SlaSolucao: 24; Ordem: 5};
    {Chave: "DUVIDA";      Nome: "Dúvida de uso";                   Ciclo: "SUPORTE"; Prioridade: "BAIXA";  Roteiro: "NAO"; Auto: "NAO"; SlaResposta: 8;  SlaSolucao: 40; Ordem: 6};
    {Chave: "NOVO_MODULO"; Nome: "Solicitação de novo módulo";      Ciclo: "DEMANDA"; Prioridade: "MEDIA";  Roteiro: "COMPLETO"; Auto: "NAO"; SlaResposta: 16; SlaSolucao: 0; Ordem: 7};
    {Chave: "MELHORIA";    Nome: "Melhoria em módulo existente";    Ciclo: "DEMANDA"; Prioridade: "MEDIA";  Roteiro: "COMPLETO"; Auto: "NAO"; SlaResposta: 16; SlaSolucao: 0; Ordem: 8};
    {Chave: "INTEGRACAO";  Nome: "Integração com outro sistema";    Ciclo: "DEMANDA"; Prioridade: "MEDIA";  Roteiro: "COMPLETO"; Auto: "NAO"; SlaResposta: 24; SlaSolucao: 0; Ordem: 9};
    {Chave: "RELATORIO";   Nome: "Novo relatório ou indicador";     Ciclo: "DEMANDA"; Prioridade: "BAIXA";  Roteiro: "REDUZIDO"; Auto: "NAO"; SlaResposta: 24; SlaSolucao: 0; Ordem: 10}
);
```

`SlaResposta` e `SlaSolucao` são **horas úteis**. `0` em `SlaSolucao` significa
"sem SLA de solução" — ciclo de demanda trabalha com previsão, não com prazo.

Itens da ComboBox de categoria, já ordenados:

```powerfx
nfCategoriasOrdenadas = Sort(nfCategorias; Ordem);
```

---

## 2. Status e transições permitidas

`De` é o status atual; `Para` é o destino; `Rotulo` é o texto do botão; `Perfil`
diz quem pode executar. A tela de detalhe **gera os botões a partir desta tabela**
— nada de `If` encadeado que ninguém consegue manter.

```powerfx
nfTransicoes =
Table(
    // ---- Ciclo A: suporte ----
    {Ciclo: "SUPORTE"; De: "Aberto";               Para: "Em atendimento";      Rotulo: "Assumir";              Perfil: "ATENDENTE";   Etapa: 2};
    {Ciclo: "SUPORTE"; De: "Aberto";               Para: "Cancelado";           Rotulo: "Cancelar chamado";     Perfil: "SOLICITANTE"; Etapa: 0};
    {Ciclo: "SUPORTE"; De: "Em atendimento";       Para: "Aguardando usuário";  Rotulo: "Pedir informação";     Perfil: "ATENDENTE";   Etapa: 2};
    {Ciclo: "SUPORTE"; De: "Em atendimento";       Para: "Resolvido";           Rotulo: "Resolver";             Perfil: "ATENDENTE";   Etapa: 3};
    {Ciclo: "SUPORTE"; De: "Aguardando usuário";   Para: "Em atendimento";      Rotulo: "Responder";            Perfil: "SOLICITANTE"; Etapa: 2};
    {Ciclo: "SUPORTE"; De: "Resolvido";            Para: "Reaberto";            Rotulo: "Reabrir";              Perfil: "SOLICITANTE"; Etapa: 2};
    {Ciclo: "SUPORTE"; De: "Resolvido";            Para: "Fechado";             Rotulo: "Fechar";               Perfil: "SOLICITANTE"; Etapa: 4};
    {Ciclo: "SUPORTE"; De: "Reaberto";             Para: "Em atendimento";      Rotulo: "Assumir";              Perfil: "ATENDENTE";   Etapa: 2};

    // ---- Ciclo B: demanda ----
    {Ciclo: "DEMANDA"; De: "Aberto";                 Para: "Em análise";            Rotulo: "Iniciar análise";   Perfil: "ATENDENTE";   Etapa: 2};
    {Ciclo: "DEMANDA"; De: "Aberto";                 Para: "Cancelado";             Rotulo: "Cancelar demanda";  Perfil: "SOLICITANTE"; Etapa: 0};
    {Ciclo: "DEMANDA"; De: "Em análise";             Para: "Aguardando informações";Rotulo: "Pedir informação";  Perfil: "ATENDENTE";   Etapa: 2};
    {Ciclo: "DEMANDA"; De: "Em análise";             Para: "Aguardando aprovação";  Rotulo: "Enviar p/ aprovação";Perfil: "ATENDENTE";  Etapa: 3};
    {Ciclo: "DEMANDA"; De: "Em análise";             Para: "Cancelado";             Rotulo: "Cancelar demanda";  Perfil: "SOLICITANTE"; Etapa: 0};
    {Ciclo: "DEMANDA"; De: "Aguardando informações"; Para: "Em análise";            Rotulo: "Responder";         Perfil: "SOLICITANTE"; Etapa: 2};
    {Ciclo: "DEMANDA"; De: "Aguardando aprovação";   Para: "Em backlog";            Rotulo: "Aprovar";           Perfil: "GESTOR";      Etapa: 4};
    {Ciclo: "DEMANDA"; De: "Aguardando aprovação";   Para: "Reprovado";             Rotulo: "Reprovar";          Perfil: "GESTOR";      Etapa: 0};
    {Ciclo: "DEMANDA"; De: "Em backlog";             Para: "Em desenvolvimento";    Rotulo: "Iniciar";           Perfil: "ATENDENTE";   Etapa: 5};
    {Ciclo: "DEMANDA"; De: "Em desenvolvimento";     Para: "Em homologação";        Rotulo: "Enviar p/ teste";   Perfil: "ATENDENTE";   Etapa: 6};
    {Ciclo: "DEMANDA"; De: "Em homologação";         Para: "Ajustes solicitados";   Rotulo: "Solicitar ajuste";  Perfil: "SOLICITANTE"; Etapa: 6};
    {Ciclo: "DEMANDA"; De: "Em homologação";         Para: "Entregue";              Rotulo: "Dar aceite";        Perfil: "SOLICITANTE"; Etapa: 7};
    {Ciclo: "DEMANDA"; De: "Ajustes solicitados";    Para: "Em desenvolvimento";    Rotulo: "Retomar";           Perfil: "ATENDENTE";   Etapa: 5};
    {Ciclo: "DEMANDA"; De: "Entregue";               Para: "Fechado";               Rotulo: "Fechar";            Perfil: "ATENDENTE";   Etapa: 7}
);
```

`Etapa: 0` marca saída da trilha (cancelado/reprovado) — a tela pinta a trilha
inteira em cinza em vez de avançar.

---

## 3. Aparência de status e prioridade

Um só lugar define cor. Se um status novo aparecer sem cor cadastrada, o
`Coalesce` devolve o cinza neutro — status desconhecido nunca deixa o item sem
pintar.

```powerfx
nfStatusVisual =
Table(
    {Status: "Aberto";                 Cor: RGBA(96; 70; 237; 1);   Fundo: RGBA(238; 242; 255; 1); Aberto: "SIM"};
    {Status: "Em atendimento";         Cor: RGBA(2; 132; 199; 1);   Fundo: RGBA(224; 242; 254; 1); Aberto: "SIM"};
    {Status: "Aguardando usuário";     Cor: RGBA(180; 83; 9; 1);    Fundo: RGBA(255; 247; 237; 1); Aberto: "SIM"};
    {Status: "Resolvido";              Cor: RGBA(21; 128; 61; 1);   Fundo: RGBA(220; 252; 231; 1); Aberto: "NAO"};
    {Status: "Reaberto";               Cor: RGBA(190; 24; 93; 1);   Fundo: RGBA(253; 242; 248; 1); Aberto: "SIM"};
    {Status: "Em análise";             Cor: RGBA(2; 132; 199; 1);   Fundo: RGBA(224; 242; 254; 1); Aberto: "SIM"};
    {Status: "Aguardando informações"; Cor: RGBA(180; 83; 9; 1);    Fundo: RGBA(255; 247; 237; 1); Aberto: "SIM"};
    {Status: "Aguardando aprovação";   Cor: RGBA(109; 40; 217; 1);  Fundo: RGBA(245; 243; 255; 1); Aberto: "SIM"};
    {Status: "Em backlog";             Cor: RGBA(71; 85; 105; 1);   Fundo: RGBA(241; 245; 249; 1); Aberto: "SIM"};
    {Status: "Em desenvolvimento";     Cor: RGBA(2; 132; 199; 1);   Fundo: RGBA(224; 242; 254; 1); Aberto: "SIM"};
    {Status: "Em homologação";         Cor: RGBA(180; 83; 9; 1);    Fundo: RGBA(255; 247; 237; 1); Aberto: "SIM"};
    {Status: "Ajustes solicitados";    Cor: RGBA(190; 24; 93; 1);   Fundo: RGBA(253; 242; 248; 1); Aberto: "SIM"};
    {Status: "Entregue";               Cor: RGBA(21; 128; 61; 1);   Fundo: RGBA(220; 252; 231; 1); Aberto: "NAO"};
    {Status: "Reprovado";              Cor: RGBA(185; 28; 28; 1);   Fundo: RGBA(254; 242; 242; 1); Aberto: "NAO"};
    {Status: "Cancelado";              Cor: RGBA(100; 116; 139; 1); Fundo: RGBA(241; 245; 249; 1); Aberto: "NAO"};
    {Status: "Fechado";                Cor: RGBA(100; 116; 139; 1); Fundo: RGBA(241; 245; 249; 1); Aberto: "NAO"}
);

nfPrioridadeVisual =
Table(
    {Chave: "CRITICA"; Nome: "Crítica"; Cor: RGBA(185; 28; 28; 1);   Horas: 4};
    {Chave: "ALTA";    Nome: "Alta";    Cor: RGBA(194; 65; 12; 1);   Horas: 8};
    {Chave: "MEDIA";   Nome: "Média";   Cor: RGBA(180; 83; 9; 1);    Horas: 24};
    {Chave: "BAIXA";   Nome: "Baixa";   Cor: RGBA(100; 116; 139; 1); Horas: 40}
);
```

---

## 4. As 7 etapas da trilha

```powerfx
nfEtapas =
Table(
    {N: 1; Nome: "Recebida";              Descricao: "Sua solicitação chegou e está na fila de leitura."};
    {N: 2; Nome: "Em análise";            Descricao: "TI está avaliando viabilidade e esforço."};
    {N: 3; Nome: "Em aprovação";          Descricao: "Aguardando decisão do gestor."};
    {N: 4; Nome: "Aprovada e priorizada"; Descricao: "Aprovada. Já existe previsão de entrega."};
    {N: 5; Nome: "Em desenvolvimento";    Descricao: "Sendo construída."};
    {N: 6; Nome: "Em homologação";        Descricao: "Pronta para o seu teste e aceite."};
    {N: 7; Nome: "Entregue";              Descricao: "Publicada e disponível para uso."}
);
```

---

## 5. Consultas do dia a dia

**Nenhuma destas é named formula** — todas dependem do usuário logado, e named
formula não enxerga variável. Ficam no `OnVisible` da tela ou na propriedade
`Items` da galeria.

### Meus chamados (delegável)

```powerfx
Sort(
    Filter(
        tbl_ServiceDesk;
        desk_solicitante_email = varEmailUser
    );
    desk_id;
    SortOrder.Descending
)
```

Texto = Texto sobre coluna indexada. Delega. **Não** trocar por
`desk_usuario.Email = ...`: campo Pessoa expandido não delega e a lista para de
funcionar em silêncio ao passar de 500 itens.

### Meus chamados em aberto

```powerfx
Filter(
    tbl_ServiceDesk;
    desk_solicitante_email = varEmailUser And
    desk_status <> "Fechado" And
    desk_status <> "Cancelado"
)
```

### Fila do time de TI

```powerfx
Filter(
    tbl_ServiceDesk;
    desk_status = "Aberto" Or
    desk_status = "Em atendimento" Or
    desk_status = "Reaberto" Or
    desk_status = "Em análise"
)
```

Cadeia de `Or`, não `desk_status in [...]`. O operador `in` sobre coluna do
SharePoint **não delega**.

### Busca textual — sobre a coleção, nunca sobre a lista

```powerfx
// no OnVisible, uma vez:
ClearCollect(
    colMeusChamados;
    Sort(
        Filter(tbl_ServiceDesk; desk_solicitante_email = varEmailUser);
        desk_id;
        SortOrder.Descending
    )
);;

// na galeria:
Search(colMeusChamados; varDeskBusca; "desk_descricao"; "desk_categoria")
```

`Search()` não delega no SharePoint. Rodando sobre a coleção já recortada do
usuário, o limite deixa de ser um problema — e a busca fica instantânea.

### Ações disponíveis para o chamado aberto na tela

```powerfx
Filter(
    nfTransicoes;
    Ciclo = varChamadoAtual.desk_ciclo And
    De = varChamadoAtual.desk_status And
    (Perfil = varPerfilUser Or                  // CONFIRMAR DOMÍNIO DE Perfil
     (Perfil = "ATENDENTE" And varPerfilUser = "GESTOR"))
)
```

Esta é a `Items` da galeria de botões da tela de detalhe. Tabela local: zero
consulta, reavaliada de graça a cada mudança de status.

---

## 6. Regras que não podem ser esquecidas

1. **Nada de `LookUp`/`Filter` sobre fonte de dados dentro de galeria.** Toda
   propriedade de item que precisar de cor, rótulo ou etapa lê de `nfStatusVisual`,
   `nfCategorias` ou `nfEtapas` — tabelas locais.
2. **Espelho grava junto com a origem**, no mesmo `SubmitForm`/`Patch`. Espelho
   que depende de fluxo posterior passa metade do tempo desatualizado.
3. **Coluna numérica não gravada fica nula, e nulo ≠ 0.** `desk_etapa` é gravado
   explicitamente na abertura (`1`), nunca deixado em branco.
4. **`Coalesce`/`IsBlank` envolve a função que pode devolver branco**, nunca a
   expressão que já fez conta com ela — branco em aritmética vira zero e a guarda
   fica decorativa.
5. **Literais gravados × literais lidos** têm que bater em `desk_status`,
   `desk_ciclo`, `desk_prioridade` e `desk_categoria_chave`. Divergência é bug
   silencioso. É o motivo de tudo aqui vir de tabela, não de string digitada na tela.
