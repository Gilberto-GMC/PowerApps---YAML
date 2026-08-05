# Configuração SharePoint — `tb_presencaFauna`

Para a tela continuar responsiva com o crescimento do histórico, criar índices
simples nas seguintes colunas internas da lista:

- `data_evento`
- `aeroporto`
- `ativo`

`data_evento` é o principal recorte da consulta e deve ser indexado antes de a
lista ultrapassar o limite operacional de 5.000 itens. `ID` já é uma coluna de
sistema do SharePoint.

## Comportamento implementado

- A galeria consulta `tb_presencaFauna` diretamente; o histórico não é copiado
  para uma coleção do aplicativo.
- O período inicial é dos últimos 90 dias até o dia atual, seguindo o padrão
  das telas históricas existentes no aplicativo de referência.
- A consulta usa filtros delegáveis por `ativo`, `aeroporto` e `data_evento`.
- A galeria carrega novas páginas conforme necessário durante a rolagem.
- A troca para a aba Registros não executa `Refresh` automaticamente.
- O contador informa registros carregados, e não um total incorreto da lista.

## Validação no Power Apps Studio

1. Adicionar ou atualizar a fonte `tb_presencaFauna`.
2. Em **Configurações > Geral**, definir temporariamente **Limite de linha de
   dados** como `1`.
3. Colar a tela e confirmar que `GalleryPresencaFauna.Items` não apresenta aviso
   azul de delegação.
4. Testar os filtros com registros anteriores e posteriores a 90 dias.
5. Restaurar o limite de linha adotado pelo aplicativo depois do teste.

O teste com limite `1` precisa ser executado no Studio conectado ao SharePoint;
ele não pode ser reproduzido apenas com o arquivo YAML local.
