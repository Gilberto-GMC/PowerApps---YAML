# Contexto Codex - AirportNow Perdidos e Achados

Data do pacote trabalhado: 03/08/2026.

## Escopo combinado

- Trabalhar somente nas telas YAML do Power Apps Canvas.
- Preservar o layout visual existente, corrigindo logica, formulas e desempenho.
- Nao alterar `App.OnStart`, fluxos Power Automate, conectores ou pacote `.msapp` sem instrucao explicita.
- Quando alguma alteracao fora das telas for necessaria, orientar ajuste manual no app em execucao.

## Problema principal encontrado

O app estava exibindo erro de rede do SharePoint:

`A operacao tentada foi proibida porque excede o limite do modo de exibicao de lista.`

Isso indica que consultas diretas em listas grandes, principalmente usando colunas como `status`, `data`, `aeroporto`, `ID_fk`, `categoria` e `subCategoria`, estavam ultrapassando o limite de exibicao de lista do SharePoint.

## Abordagem atual

As telas corrigidas usam uma abordagem mais segura para performance:

- carregar janelas recentes em colecoes locais;
- filtrar galerias/tabelas em colecoes, nao diretamente nas listas grandes;
- manter busca exata por ID do atendimento, pois igualdade em `ID` e a consulta mais segura;
- evitar `Filter`, `UpdateIf`, `RemoveIf` e `LookUp` por `ID_fk` diretamente em `tbl_perdidosAchadosItens` nos pontos principais;
- preservar visual e estrutura das telas originais.

Janelas usadas:

- pais: ultimos 300 registros por `ID`;
- filhos em cadastro/consulta/entrega: ultimos 1200 itens por `ID`;
- filhos em inventario: ultimos 1500 itens por `ID`.

## Telas principais corrigidas

- `telas-corrigidas/ScreenCadastrar.pa.yaml`
- `telas-corrigidas/ScreenEntregaListar.pa.yaml`
- `telas-corrigidas/ScreenConsultListar.pa.yaml`
- `telas-corrigidas/ScreenEntregaRecibo.pa.yaml`
- `telas-corrigidas/ScreenInventario.pa.yaml`
- `telas-corrigidas/ScreenInventarioSeparar.pa.yaml`
- `telas-corrigidas/ScreenInventarioDoacao.pa.yaml`

## Arquivos de apoio

- `AUDITORIA-TELAS.md`: auditoria tecnica, ajustes feitos, limites e checklist.
- `manifest.json`: metadados do pacote extraido.

## Limite conhecido

A abordagem de cache local evita o erro de limite e melhora a abertura das telas, mas nao substitui indices do SharePoint para busca historica completa.

Para garantir busca completa em listas grandes, criar indices nas colunas:

- Pai `tbl_perdidosAchados`: `ID`, `aeroporto`, `bloco`, `status`, `arquivado`, `data`.
- Filho `tbl_perdidosAchadosItens`: `ID`, `ID_fk`, `Aeroporto`, `status`, `arquivar`, `recebido`, `categoria`, `subCategoria`.

Se for necessario pesquisar todo o historico por texto livre ou cruzar pai/filho sem limite, a melhor evolucao e criar uma lista indice achatada/search, com uma linha por item contendo os campos relevantes do pai e do filho.

## Rastreabilidade da cadeia de recebimento (23/09/2026)

Alteracao em `ScreenCadastrar` e `ScreenConsultListar` para registrar quem encontrou o objeto antes de ele chegar a ASUR. Detalhes completos em `AUDITORIA-TELAS.md`, secao "Rastreabilidade da cadeia de recebimento".

Resumo: quatro colunas novas no pai (`declarante`, `empresa_declarante`, `tipo_origem`, `encontrado_em`), sendo `encontrado_em` obrigatorio por exigencia do item 5.1.1 do PRO Rev. 03. `tipo_origem` e coluna de **texto** com ComboBox de 10 opcoes fixas -- este app nao usa colunas Choice do SharePoint.

## Descarte imediato — correcoes (23/09/2026)

Parte A (bugs, sem mudanca visivel): removido o modal de descarte duplicado do `ScreenCadastrar` e eliminados os dois `Filter(tbl_perdidosAchadosItens, ID_fk = ...)` que restavam no `OnSuccess`.

Parte B: coluna nova `sujeito_descarte` (Sim/Nao) em `tbl_perdidosAchadosItens`, um marcador unico que abrange as dez hipoteses do item 5.11 do PRO. Amplia a regra do botao "Descartar", que antes so aceitava `perecivel` ou `pessimas_condUso`.

Detalhes em `AUDITORIA-TELAS.md`.

## Migracao do App.OnStart para App.Formulas

Proposta pronta em `AppFormulas_PerdidosAchados.fx.md`: tudo migra, menos as tres variaveis de sessao (`varSessaoAtiva`, `varUltimaAtividade`, `varForcarExpiracao`), que sao reatribuidas em tempo de execucao. Nenhuma tela precisa ser alterada — os nomes foram mantidos.

**Inclui a correcao do `varIdUser`.** O OnStart fixava `Coalesce(584; ...)`, valor de teste que ficou no codigo — como `584` nunca e vazio, o `LookUp` jamais executava e todo usuario era identificado como o mesmo. Restaurado para `Coalesce(IfError(Value(Param("USUARIO")); Blank()); LookUp(User; usrNome = User().FullName).ID)`.

Isso muda `varAeroUser`, `varBlocoUser`, `varPerfilUser` e `varAutUser` para os valores reais de cada usuario, alterando filtros de aeroporto, permissao de troca de bloco e liberacao de exclusao de itens. **Testar com um usuario `Sede` e um `Base` antes de publicar.**

## Checklist rapido apos colagem no Power Apps Studio

1. Recolar somente as telas corrigidas necessarias.
2. Atualizar as fontes de dados: `tbl_perdidosAchados`, `tbl_perdidosAchadosItens`, `DadosGerais` e `Documentos`.
3. Salvar o app.
4. Testar cadastro novo com varios itens.
5. Testar busca por ID nas telas de cadastro, entrega e consulta.
6. Testar entrega/recibo.
7. Testar inventario: separar, cancelar separacao e doar.
8. Rodar App Checker e Monitor para confirmar ausencia do erro de limite.
