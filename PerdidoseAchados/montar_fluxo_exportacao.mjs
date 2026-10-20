// Monta o fluxo "Exportar Perdidos e Achados" a partir do molde do Mapa.
// O molde e o fluxo de exportacao da programacao, que ja esta em producao:
// mesmo gatilho (pedido com status PRONTO), mesmo Marcar_processando /
// Criar_arquivo / Concluir / Marcar_erro.
import fs from 'fs';

const SITE = 'https://grupoccr.sharepoint.com/sites/AIRPORTNOW';
const LISTA_PEDIDOS = 'tb_exportacaoPA';
const LISTA_ITENS = 'tbl_perdidosAchadosItens';
const PASTA = '/Documentos Partilhados/exportacoes';

// Mesma lista do colCatDoaveis no App.Formulas. Repetida aqui de proposito:
// o fluxo nao enxerga o App.Formulas, e a regra dos itens 5.13 e 5.16 do PRO
// tem que valer nos dois lados. Mexeu em um, mexa no outro.
const DOAVEIS = [
  'Artigos religiosos', 'Artigos sexuais', 'Bagagem', 'Bebidas/Alimentos',
  'Bijuterias/Joias', 'Cama, mesa e banho', 'Cortantes', 'Ferramenta',
  'Fumígeno', 'Infantil', 'Itens esportivos', 'Itens médico',
  'Objetos de arte', 'Óculos', 'Papelaria', 'Pessoais', 'Pet',
  'Produtos de uso pessoal', 'Produtos químicos', 'Regionais', 'Souvenir',
  'Veículo', 'Vestuário',
];

const host = op => ({
  apiId: '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
  connectionName: 'shared_sharepointonline',
  operationId: op,
});

const patchPedido = (campos) => ({
  runAfter: {},
  type: 'OpenApiConnection',
  inputs: {
    parameters: {
      dataset: SITE,
      table: LISTA_PEDIDOS,
      id: "@triggerBody()?['ID']",
      'item/aeroporto': "@triggerBody()?['aeroporto']",
      'item/tipo': "@triggerBody()?['tipo']",
      'item/ativo': "@triggerBody()?['ativo']",
      ...campos,
    },
    host: host('PatchItem'),
    authentication: "@parameters('$authentication')",
  },
});

const arr = xs => 'createArray(' + xs.map(x => "'" + x.replace(/'/g, "''") + "'").join(',') + ')';

// dias em custodia: igual ao DateDiff(recebido, Today(), Days) da tela
const DIAS = "div(sub(ticks(utcNow()),ticks(item()?['recebido'])),864000000000)";

const definition = {
  $schema: 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#',
  contentVersion: '1.0.0.0',
  parameters: {
    $connections: { defaultValue: {}, type: 'Object' },
    $authentication: { defaultValue: {}, type: 'SecureObject' },
  },
  triggers: {
    Quando_um_pedido_entra: {
      recurrence: { frequency: 'Minute', interval: 1 },
      evaluatedRecurrence: { frequency: 'Minute', interval: 1 },
      splitOn: "@triggerOutputs()?['body/value']",
      type: 'OpenApiConnection',
      inputs: {
        parameters: { dataset: SITE, table: LISTA_PEDIDOS },
        host: host('GetOnUpdatedItems'),
        authentication: "@parameters('$authentication')",
      },
      conditions: [{ expression: "@equals(triggerBody()?['status'], 'PRONTO')" }],
    },
  },
  actions: {
    Marcar_processando: patchPedido({ 'item/status': 'PROCESSANDO' }),

    // Delegacao: o $filter vai no servidor; so o que o SharePoint nao sabe
    // filtrar (os 90 dias e a lista de categorias) fica no Filtrar_opcionais.
    Obter_itens: {
      runAfter: { Marcar_processando: ['Succeeded'] },
      type: 'OpenApiConnection',
      inputs: {
        parameters: {
          dataset: SITE,
          table: LISTA_ITENS,
          $filter: "arquivar eq 0 and Aeroporto eq '@{triggerBody()?['aeroporto']}' and status eq '@{if(equals(triggerBody()?['tipo'],'SEPARADOS'),'Separado','Recebido')}'",
          $orderby: 'recebido desc',
          $top: 5000,
        },
        host: host('GetItems'),
        authentication: "@parameters('$authentication')",
      },
    },

    Filtrar_opcionais: {
      runAfter: { Obter_itens: ['Succeeded'] },
      type: 'Query',
      inputs: {
        from: "@body('Obter_itens')?['value']",
        where: '@and(and(and(and(and(and(' +
          // so categoria doavel — itens 5.13 e 5.16 do PRO
          'contains(' + arr(DOAVEIS) + ",coalesce(item()?['categoria'],'')),"
          // ELEGIVEIS exige os 90 dias de guarda; SEPARADOS ja passou por isso
          + "if(equals(triggerBody()?['tipo'],'SEPARADOS'),true,greaterOrEquals(" + DIAS + ',90))),'
          + "or(empty(coalesce(triggerBody()?['categoria'],'')),equals(item()?['categoria'],triggerBody()?['categoria']))),"
          + "or(empty(coalesce(triggerBody()?['subcategoria'],'')),equals(item()?['subCategoria'],triggerBody()?['subcategoria']))),"
          + "or(empty(coalesce(triggerBody()?['data_de'],'')),greaterOrEquals(item()?['recebido'],formatDateTime(triggerBody()?['data_de'],'yyyy-MM-dd')))),"
          + "or(empty(coalesce(triggerBody()?['data_ate'],'')),lessOrEquals(formatDateTime(item()?['recebido'],'yyyy-MM-dd'),formatDateTime(triggerBody()?['data_ate'],'yyyy-MM-dd')))),"
          // a busca das duas telas e StartsWith na marca; aqui vale o mesmo
          + "or(empty(coalesce(triggerBody()?['busca'],'')),startsWith(toLower(coalesce(item()?['marca'],'')),toLower(triggerBody()?['busca']))))",
      },
    },

    Montar_linhas: {
      runAfter: { Filtrar_opcionais: ['Succeeded'] },
      type: 'Select',
      inputs: {
        from: "@body('Filtrar_opcionais')",
        select: "@concat('\"',item()?['ID'],'\";\"',formatDateTime(item()?['recebido'],'dd/MM/yyyy'),'\";\"'," +
          "coalesce(item()?['categoria'],''),'\";\"',coalesce(item()?['subCategoria'],''),'\";\"'," +
          "coalesce(item()?['marca'],''),'\";\"'," +
          "replace(coalesce(item()?['descricao'],''),'\"',''''),'\";\"'," +
          DIAS + ",'\";\"',coalesce(item()?['Aeroporto'],''),'\"')",
      },
    },

    Criar_arquivo: {
      runAfter: { Montar_linhas: ['Succeeded'] },
      type: 'OpenApiConnection',
      inputs: {
        parameters: {
          dataset: SITE,
          folderPath: PASTA,
          name: "perdidosachados_@{toLower(triggerBody()?['tipo'])}_@{triggerBody()?['aeroporto']}_@{formatDateTime(utcNow(),'yyyyMMdd_HHmm')}.csv",
          // BOM na frente: sem ele o Excel abre os acentos errados
          body: "@{concat(decodeUriComponent('%EF%BB%BF'),'\"Item\";\"Data\";\"Categoria\";\"Subcategoria\";\"Marca\";\"Descricao\";\"Dias em custodia\";\"Aeroporto\"',decodeUriComponent('%0D%0A'),join(body('Montar_linhas'),decodeUriComponent('%0D%0A')))}",
        },
        host: host('CreateFile'),
        authentication: "@parameters('$authentication')",
      },
    },

    Concluir: {
      runAfter: { Criar_arquivo: ['Succeeded'] },
      type: 'OpenApiConnection',
      inputs: {
        parameters: {
          dataset: SITE,
          table: LISTA_PEDIDOS,
          id: "@triggerBody()?['ID']",
          'item/aeroporto': "@triggerBody()?['aeroporto']",
          'item/tipo': "@triggerBody()?['tipo']",
          'item/ativo': "@triggerBody()?['ativo']",
          'item/status': 'CONCLUIDO',
          'item/total': "@length(body('Filtrar_opcionais'))",
          'item/arquivo_nome': "@body('Criar_arquivo')?['Name']",
          'item/arquivo_url': "@{concat('" + SITE + "',body('Criar_arquivo')?['Path'])}",
        },
        host: host('PatchItem'),
        authentication: "@parameters('$authentication')",
      },
    },

    Marcar_erro: {
      runAfter: {
        Obter_itens: ['Failed', 'TimedOut'],
        Filtrar_opcionais: ['Failed', 'TimedOut'],
        Montar_linhas: ['Failed', 'TimedOut'],
        Criar_arquivo: ['Failed', 'TimedOut'],
        Concluir: ['Failed', 'TimedOut'],
      },
      type: 'OpenApiConnection',
      inputs: {
        parameters: {
          dataset: SITE,
          table: LISTA_PEDIDOS,
          id: "@triggerBody()?['ID']",
          'item/aeroporto': "@triggerBody()?['aeroporto']",
          'item/tipo': "@triggerBody()?['tipo']",
          'item/ativo': "@triggerBody()?['ativo']",
          'item/status': 'ERRO',
          'item/mensagem': 'Falha ao gerar o arquivo. Veja o historico da execucao no fluxo Exportar Perdidos e Achados.',
        },
        host: host('PatchItem'),
        authentication: "@parameters('$authentication')",
      },
    },
  },
};

const saida = {
  name: 'Exportar Perdidos e Achados',
  id: '/providers/Microsoft.Flow/flows/00000000-0000-0000-0000-000000000000',
  type: 'Microsoft.Flow/flows',
  properties: { displayName: 'Exportar Perdidos e Achados', definition },
};

fs.writeFileSync(process.argv[2], JSON.stringify(saida, null, 2) + '\n', 'utf8');
console.log('fluxo gravado: ' + Object.keys(definition.actions).length + ' acoes, ' + DOAVEIS.length + ' categorias doaveis');
