# Contexto do projeto-base para Power Apps

## Finalidade desta pasta

Este projeto é um protótipo React/Vite da plataforma **Motiva Controle de Aeroportos**. Ele deve ser usado como referência funcional e visual para os módulos que serão implementados em Power Apps Canvas, não como fonte de dados nem como implementação de produção.

Arquivo recebido: `motiva-controle-de-aeroportos---nova-plataforma (3).zip`  
Pasta de extração: `motiva-controle-de-aeroportos---nova-plataforma/`  
Data da análise: 05/08/2026

## Estado técnico validado

- Projeto React 18 + TypeScript + Vite 6.
- `npm run lint` concluído sem erros de TypeScript.
- `npm run build` concluído com sucesso.
- Catálogo com 33 módulos distribuídos em 6 categorias.
- 22 módulos possuem telas funcionais no protótipo.
- 11 módulos aparecem no catálogo, mas ainda mostram a mensagem “em desenvolvimento”.
- Os registros são mantidos apenas em `useState`; recarregar a página descarta alterações.
- Não há conexão com SharePoint, Dataverse, API, Power Automate ou outra fonte persistente.
- Login demonstrativo fixo: `admin` / `admin`; não representa a autenticação final.
- Os atrasos de gravação são simulados com `setTimeout` e os IDs com `Math.random`.

## Arquitetura de navegação

Fluxo principal:

1. Login demonstrativo.
2. Página inicial com visão tática.
3. Menu lateral por grandes áreas.
4. Página “Operações Aeroportuárias” com busca, filtro por categoria e visualização em lista ou grade.
5. Seleção de um módulo.
6. Dentro do módulo, padrão predominante de abas “Novo Registro” e “Registros”.
7. Histórico com filtros, tabela, status e menu de ações.
8. Modais de confirmação, conclusão, devolução, recusa, exclusão ou detalhe, conforme o módulo.

Elementos globais que devem ser preservados na adaptação:

- Menu lateral fixo e recolhível.
- Cabeçalho com busca, RELPREV, notificações e usuário.
- Retorno ao painel no topo de cada módulo.
- Botão “Instruções em Vídeo”.
- Estados de carregamento/sucesso antes de retornar ao histórico.
- Filtros de aeroporto e período nos históricos.
- Ações contextuais por registro e por status.

## Identidade visual

- Fonte principal: **Sora**.
- Cor institucional primária: `#391694`.
- Variação escura: `#2A106E`.
- Fundo primário: `#FFFFFF`.
- Fundo auxiliar: escala Slate clara (`#F8FAFC`/equivalentes).
- Borda institucional clara: `#C9C5E6`.
- Ação de instrução: `#DD511A`.
- Operacional: `#0891B2` / `#C2F6FF`.
- Inspeções: `#FFAC8B`.
- Fauna: `#51FF62`.
- Eventos de segurança: `#D946EF` / `#F1C5FF`.
- Informações aeronáuticas: `#4F46E5`.
- Programa de orientação: `#FFFD8A`.
- Controles e cartões predominantemente sem raio (`rounded-none`).
- Espaçamento recorrente entre blocos: 26 px.
- Títulos dos módulos: 24–26 px, negrito e caixa alta.
- Labels: 13 px, negrito; obrigatoriedade indicada por `*`.
- Campos: fundo branco, borda Slate clara, preenchimento aproximado de 16–20 px.

No Canvas App, essas definições devem virar constantes/variáveis de tema no `App.OnStart` ou propriedades nomeadas de um componente de tema, evitando repetir valores em todas as telas.

## Catálogo de módulos

### Implementados no protótipo

| ID | Módulo | Comportamento central |
|---|---|---|
| `aero-1` | Informações Aeronáuticas – AISWEB | Auditoria por seções; Conforme/Não Conforme; observação e código SDIA obrigatórios nas divergências; resumo e histórico. |
| `aero-2` | NOTAMs / Suplementos AIP | Cadastro de vigência, texto e antecedência de alerta; filtro e ordenação de histórico. |
| `aero-3` | Descumprimento AIS | Reporte, edição, visualização e fluxo Aguardando envio → Enviado à ANAC / Devolvido / Recusado; número SEI e justificativas. |
| `aero-4` | Aviso Operacional (AVOP) | Período, detalhamento, impacto, destinatários, confirmação e geração de PDF. |
| `insp-6` | Inspeção do Ambulift | Checklist Conforme/Não Conforme; observação obrigatória para não conformidade; anexos e histórico. |
| `ops-2` | Teste de Motores | Agendamento, aeronave, local, tipo, horários; edição, exclusão e conclusão com horários reais. |
| `ops-6` | Ambulift | Companhia, voo, data e horários; término sugerido 20 minutos após o início; conclusão e histórico. |
| `ops-7` | Controle de Sobrecarga | Aeronave, peso de pouso e anexos; fluxo Em Análise / Aprovado / Devolvido / Recusado. |
| `ops-8` | Acesso de Terceiros | Visitante, documento, empresa, motivo, área, período, responsável pela escolta e veículo. |
| `safe-1` | Vazamentos em Área Operacional | Fluido, área/volume, origem, local, protocolos/relatos, fotos e orientação de resíduo perigoso. |
| `safe-2` | Detritos (F.O.Debris) | Material, local, posição, origem provável e descrição. |
| `safe-10` | Dano por Detritos (F.O.Damage) | Estrutura semelhante a FOD, aplicada ao dano provocado pelo detrito. |
| `safe-3` | Jet-blast / Propeller-Wash | Aeronave originadora, tipo/identificação do afetado, local e descrição. |
| `safe-4` | Ocorrência de Solo | Aeronave, dano/perda, local, descrição e pessoas feridas. |
| `safe-5` | Colisão de Veículos/Equipamentos | Originador, alvo, local, descrição, relato do condutor e feridos. |
| `safe-6` | Interferência Externa | Drone, balão, pipa ou laser; quadrante, quantidade, descrição e anexo. |
| `safe-7` | Eventos Envolvendo Obras | Empresa, área, tipo, descrição, ações, feridos e aeronaves danificadas. |
| `safe-8` | Outras Ocorrências | Título, envolvidos, local, descrição, ações, feridos e aeronaves danificadas. |
| `safe-9` | Princípio de Incêndio | Origem, combate/extintores, resposta SEISC, dano material, feridos e descrição. |
| `fauna-1` | Reporte Mandatório de Fauna | Colisão/quase colisão/avistamento, aeronave, espécie, fase/efeito do voo, dano, ambiente e local. |
| `fauna-5` | Presença de Fauna | Clima, local, tipo de ocorrência, evidência, comportamento, descrição e imagens. |
| `fauna-6` | Foco de Atração de Fauna | Clima, local/grade, foco atrativo, vulnerabilidade, protocolo, mitigação e imagens. |

### Ainda não implementados no protótipo

- `insp-1` — Inspeção de Pátios.
- `insp-2` — Inspeção da Pista de Pouso e Decolagem e Pistas de Táxi.
- `insp-3` — Inspeção da Faixa de Pista.
- `insp-4` — Inspeção do Sistema de Proteção.
- `insp-5` — Inspeção das Zonas de Proteção do Aeródromo.
- `insp-7` — Inspeção Especial (Extraordinária).
- `ops-1` — Aviso Meteorológico.
- `ops-3` — Vistoria de Veículos.
- `ops-4` — Follow-Me de Aeronaves.
- `ops-5` — Embarque e Desembarque Híbrido.
- `orient-1` — Registros do Programa de Orientação.

## Padrão recomendado para o Canvas App

O protótipo usa controles soltos e estado local, mas a escolha entre `EditForm`/DataCards ou controles soltos com `Patch()` deve seguir a tela-modelo Power Apps que for fornecida para o novo módulo.

Estrutura conceitual sugerida:

- `scr<Modulo>`: tela principal do módulo.
- `conCabecalhoModulo`: título, voltar e instruções.
- `conAbasModulo`: novo registro / registros.
- `conFormulario`: formulário responsivo.
- `conFiltros`: aeroporto, período e filtros específicos.
- `galRegistros`: histórico; preferível a uma tabela rígida para responsividade.
- `conModal*`: confirmações e tratativas.
- Componente global para cabeçalho, menu lateral, campo padrão, modal e estado vazio.

Estados a reproduzir com variáveis Power Fx:

- Aba ativa.
- Registro selecionado.
- Modo novo, edição ou somente leitura.
- Modal ativo.
- Operação em andamento.
- Filtros.
- Status do fluxo.

Os estados não devem ser a fonte definitiva dos dados: as operações precisam usar SharePoint e tratamento com `IfError`, `Notify`, `Refresh` e reset apenas após confirmação de sucesso.

## Modelo de dados e SharePoint

O protótipo não fornece nomes de listas nem nomes internos de colunas. Antes de gerar YAML, serão obrigatórios:

1. Nome exato da fonte SharePoint.
2. Estrutura da lista com nome de exibição, nome interno, tipo e obrigatoriedade.
3. Regras de permissão por perfil e aeroporto.
4. Status permitidos e responsáveis por cada transição.
5. Política de anexos, exclusão e retenção.
6. Definição da exportação (Excel/PDF) e eventual fluxo Power Automate.

Estruturas repetitivas, como pessoas feridas, aeronaves danificadas, itens de checklist e destinatários de e-mail, provavelmente exigirão listas filhas relacionadas por Lookup ao registro principal. Não devem ser achatadas em texto sem validação funcional.

## Regras de negócio que já aparecem no protótipo

- Aeroporto é uma dimensão comum a quase todos os módulos; há uma lista fixa de 16 aeroportos.
- Históricos normalmente filtram por aeroporto e intervalo de datas.
- Não conformidade de checklist exige observação.
- AISWEB exige também código SDIA para cada item não conforme antes da finalização.
- Ambulift sugere término 20 minutos após o horário inicial.
- Alguns fluxos impedem edição após estado terminal.
- Exclusões usam confirmação explícita.
- Registros com devolução ou recusa guardam motivo/justificativa.
- Vários módulos trabalham com anexos ou imagens.
- AVOP gera documento PDF e aceita múltiplos e-mails para notificação.

Essas regras precisam ser confirmadas com o responsável funcional; o protótipo evidencia intenção, mas não substitui requisito homologado.

## Riscos e lacunas antes da implementação

- Todos os dados atuais são mocks em memória.
- Não existe controle real de acesso por usuário, função ou aeroporto.
- A busca global procura apenas título/categoria de módulo.
- Alguns botões de exportação e navegação são apenas visuais.
- Datas usam padrões do navegador e precisam ser normalizadas no Power Fx, incluindo UTC quando indicado.
- Anexos usam objetos locais do navegador e não demonstram persistência.
- Exclusão física pode ser inadequada; avaliar cancelamento lógico e trilha de auditoria.
- As listas de aeroportos e opções estão duplicadas em componentes; no Power Apps devem vir de fonte central ou coleção única.
- Há duas versões de AISWEB; `App.tsx` usa `AISWebModule_v2.tsx`.
- O build alerta para bundle acima de 500 kB; isso não afeta o Canvas App, mas reforça que o React é apenas referência.
- O HTML referencia `/index.css`, arquivo ausente no pacote; o build mantém a referência para resolução em runtime.
- A auditoria de dependências encontrou vulnerabilidades no projeto web. Elas não migram para Power Apps, mas devem ser tratadas se este protótipo também vier a ser publicado como aplicação web.

## Fonte de verdade para o próximo módulo

Na implementação Power Apps, a prioridade de referência deve ser:

1. Regras funcionais homologadas e estrutura real do SharePoint.
2. Tela-modelo YAML existente e seu padrão (`EditForm` ou `Patch`).
3. Este protótipo para aparência, organização, textos, estados e fluxo esperado.
4. Dados mock apenas como exemplo visual, nunca como regra definitiva.

