# Contexto do Projeto AVSEC

Fonte lida: `Power Apps - YAML - AVSEC.pdf`

## Objetivo
Construir/ajustar um módulo Power Apps Canvas para ocorrências AVSEC, inicialmente focado em `acesso_indevido_pessoas`, com integração SharePoint e fluxo de análise AVSEC.

O módulo deve registrar a ocorrência, notificar o responsável AVSEC, permitir análise, desdobramentos/timeline, classificação DSAC/CSA, envio à ANAC quando aplicável e encerramento do ciclo.

## Decisões consolidadas
- Usar nomenclatura física em minúsculo, sem acentos e com `_`.
- Listas com prefixo `tb_`.
- Colunas SharePoint com nomes internos iguais aos usados no Power Apps.
- Campos de seleção devem ser gravados como `Text`, não `Choice`.
- Flags devem seguir o padrão do projeto. No histórico do PDF, `tratar_csa` e `ativo` aparecem como `Number` em uma versão da lista já criada.
- Adotar `Responsável AVSEC`, não `SEC`, na interface/processo.
- Adotar `DSAC` como nome regulatório; `DSAQ` fica apenas como possível termo interno se a equipe confirmar.
- Não criar lista auxiliar para área/local na primeira versão.
- `area` fica na lista principal como seleção única.
- `local` fica como texto obrigatório na lista principal.
- Usar anexos nativos do SharePoint na ocorrência e nos desdobramentos.
- Usar colunas nativas do SharePoint para autoria e datas quando possível: `Created`, `Created By`, `Modified`, `Modified By`.
- Não permitir exclusão pela interface comum.

## Listas SharePoint

### `tb_avsec_ocorrencias`
Lista principal das ocorrências.

Campos citados como base:
- `modulo`
- `aeroporto`
- `inicio`
- `termino`
- `tipo_acesso`
- `area`
- `local`
- `envolvidos_identificacao`
- `descricao_ocorrencia`
- `acao_imediata`
- `varredura_ars_realizada`
- `status`
- `gera_dsac`
- `tratar_csa`
- `data_limite_dsac`
- `ativo`

Observações:
- `Title`: oculto/não obrigatório.
- Anexos: habilitados.
- Histórico de versões: habilitado.
- `data_limite_dsac`: calculada a partir de `inicio + 30 dias`.
- O prazo de 20 dias é SLA interno, não prazo regulatório identificado no RBAC citado no PDF.

### `tb_avsec_desdobramentos`
Lista da timeline/desdobramentos.

Campos citados:
- `ocorrencia_id`
- `categoria`
- `conteudo`
- `data_acao`
- `autor_nome`
- `autor_email`
- `perfil_autor`
- `incluir_dsac`
- `revisao_de_id`
- `numero_revisao`
- `ativo`

Observações:
- `Title`: oculto/não obrigatório.
- Anexos: habilitados.
- Histórico de versões: habilitado.
- Índice recomendado em `ocorrencia_id`.
- A ação imediata fica na ocorrência principal e aparece como primeiro marco da timeline, sem duplicar em desdobramentos.

### `tb_avsec_config_aeroportos`
Lista de configuração por aeroporto.

Campos citados:
- `aeroporto`
- `iata`
- `grupo_responsavel_sec` ou equivalente definido no projeto
- `grupo_bloco`
- `ativo`

Observações:
- `Title`: oculto/não obrigatório.
- Anexos: desabilitados.
- Índice recomendado em `iata`.
- `iata` com valores exclusivos, se possível.

## Valores persistidos citados no PDF

### `modulo`
- `acesso_indevido_pessoas`

### `tipo_acesso`
- `acesso_indevido`
- `tentativa_acesso_indevido`

### `area`
- `ac_area_controlada`
- `ap_area_publica`
- `ars_area_restrita_seguranca`
- `nao_aplicavel`

### `varredura_ars_realizada`
- `sim`
- `nao`
- `nao_aplicavel`

### `status`
- `aguardando_analise_avsec`
- `em_analise_avsec`
- `arquivada_sem_dsac`
- `encaminhada_ao_bloco`
- `escalonada_ao_bloco`
- `em_elaboracao_dsac`
- `enviada_a_anac`
- `encerrada`

### `gera_dsac`
- `pendente`
- `sim`
- `nao`

### `tratar_csa`
- `0`
- `1`

### `ativo`
- `1`

## Regras funcionais principais
- Ao salvar novo registro, definir status inicial como `aguardando_analise_avsec`.
- Calcular `data_limite_dsac` como 30 dias após `inicio`.
- A varredura ARS deve ser exigida no aplicativo quando `area = ars_area_restrita_seguranca` e `tipo_acesso = acesso_indevido`.
- A ocorrência encerrada não deve ser excluída; permanece disponível para anexos e desdobramentos.
- O controle de permissão deve existir no SharePoint, não apenas no Power Apps.

## Problema de YAML já identificado no histórico
O PDF registra erro PA2108:

`Unknown property 'LayoutAlignInContainer' for control type 'GroupContainer@1.5.0' and variant 'AutoLayout'`

Correção consolidada:
- Remover `LayoutAlignInContainer` de `GroupContainer@1.5.0`.
- A versão corrigida mencionada no PDF removeu 22 ocorrências.

## Pendências de confirmação
- Confirmar se `grupo_responsavel_sec` será mantido com esse nome interno ou renomeado para padrão AVSEC, por exemplo `grupo_responsavel_avsec`.
- Confirmar os tipos reais já criados no SharePoint, especialmente `tratar_csa` e `ativo`.
- Confirmar se existe YAML atual do módulo AVSEC para editar ou se será necessário gerar uma nova tela a partir de modelo.
- Confirmar os nomes exatos das fontes de dados adicionadas no app.

## Artefato atual
Arquivo adicionado ao projeto: `AcessoIndevidoPessoas.yaml`

Referência visual adicionada:
- `PrincipioIncendio.txt`: usado como base de layout, largura útil, bordas e paleta para refatorar `AcessoIndevidoPessoas.yaml`.

Decisões aplicadas na refatoração visual:
- Manter a lógica, fontes de dados, `SubmitForm`, `Patch`, filtros e nomes de controles existentes.
- Centralizar as visões principais com largura útil `Min(980, Parent.Width - If(App.Width < 900, 24, 100))`.
- Aproximar a paleta da tela de princípio de incêndio: fundo branco, bordas `RGBA(229, 229, 229, 1)`, títulos em `RGBA(2, 16, 59, 1)` e acentos preto/cinza.
- Manter o `SideMenu` com o roxo institucional já usado no projeto.
- Não copiar fórmulas vazias do arquivo de princípio de incêndio.

Nomes de fontes usados pelo YAML atual:
- `tb_avsecOcorrencias`
- `tb_avsecDesdobramentos`
- `tb_avsecConfigAeroportos`

Estrutura real informada para `tb_avsecOcorrencias`:
- `modulo`: Texto com uma linha
- `aeroporto`: Texto com uma linha
- `inicio`: Data e Hora
- `termino`: Data e Hora
- `tipo_acesso`: Texto com uma linha
- `area`: Texto com uma linha
- `local`: Texto com uma linha
- `envolvidos_identificacao`: Texto com várias linhas
- `descricao_ocorrencia`: Texto com várias linhas
- `acao_imediata`: Texto com várias linhas
- `varredura_ars_realizada`: Texto com uma linha
- `status`: Texto com uma linha
- `gera_dsac`: Texto com uma linha
- `tratar_csa`: Número
- `data_limite_dsac`: Data e Hora
- `ativo`: Número

Estrutura real informada para `tb_avsecConfigAeroportos`:
- `aeroporto`: Texto com uma linha
- `iata`: Texto com uma linha
- `grupo_responsavel_avsec`: Texto com uma linha
- `grupo_bloco`: Texto com uma linha
- `ativo`: Sim/Não

Estrutura real informada para `tb_avsecDesdobramentos`:
- `id_fk_ocorrencia`: Número
- `aeroporto`: Texto com uma linha
- `categoria`: Texto com uma linha
- `conteudo`: Texto com várias linhas
- `ativo`: Sim/Não

Campos/nomes que precisam bater com as listas reais antes da colagem:
- Desdobramentos usam `id_fk_ocorrencia`, conforme lista real informada.
- Configuração usa `grupo_responsavel_avsec`, conforme lista real informada.
- Status de envio à ANAC está persistido no YAML como `enviada_anac`.
