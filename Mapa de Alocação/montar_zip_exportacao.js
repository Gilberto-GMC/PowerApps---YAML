// Monta o pacote .zip do fluxo "Exportar programacao".
// Molde: o Importarprogramacao_COMPLETO.zip, que funcionou neste ambiente.
// Cuidados que vieram de erro real:
//   - entradas com "/" e na mesma ordem do pacote original (o .NET escreve "\" e o
//     Power Automate recusa)
//   - manifest com suggestedCreationType "New" (senao pede "salve como novo fluxo primeiro")
//   - operationId conferido contra o fluxo que roda, nao contra o rotulo da UI
const fs = require("fs"), zlib = require("zlib");

const SITE = "https://grupoccr.sharepoint.com/sites/AIRPORTNOW";
const FLOW_ID = "3f1c9a04-7b62-4e58-9c31-8ad5e0b41726";
const API_ID = "1821735d-649e-4ffe-933f-35a1c1e32c2a";
const CONN_ID = "822f4c97-d670-4aa7-baf5-c0129e3ecf71";
const CONN_NAME = "shared-sharepointonl-0cd12861-383f-4b6e-9359-db983fb70160";
const ICON = "https://static.powerapps.com/resource/ppcr/releases/v1.0.1827/1.0.1827.4913/sharepointonline/icon.png";
const HOST = {
  apiId: "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
  connectionName: "shared_sharepointonline",
};

const sp = (op, params) => ({
  type: "OpenApiConnection",
  inputs: {
    parameters: params,
    host: Object.assign({}, HOST, { operationId: op }),
    authentication: "@parameters('$authentication')",
  },
});

// Obrigatorias da tb_exportacaoMapa: so aeroporto, status e ativo. Foi de proposito —
// na tb_importacaoMapa as oito obrigatorias tornaram cada PatchItem um exercicio de
// repreencher campo que nao mudou.
const patchBase = {
  dataset: SITE,
  table: "tb_exportacaoMapa",
  id: "@triggerBody()?['ID']",
  "item/aeroporto": "@triggerBody()?['aeroporto']",
  "item/ativo": "@triggerBody()?['ativo']",
};

const q = "'";
const asp = '"'; // aspas literais: dentro de literal de expressao do Logic Apps nao se escapam

const LINHA =
  "@concat(" + q + asp + q + ",formatDateTime(item()?['data_operacao'],'dd/MM/yyyy')," + q + asp + ";" + asp + q + "," +
  "formatDateTime(item()?['data_fim'],'dd/MM/yyyy')," + q + asp + ";" + asp + q + "," +
  "item()?['posicao_txt']," + q + asp + ";" + asp + q + ",item()?['patio_txt']," + q + asp + ";" + asp + q + "," +
  "formatNumber(div(item()?['hora_inicio'],60),'00'),':',formatNumber(mod(item()?['hora_inicio'],60),'00')," + q + asp + ";" + asp + q + "," +
  "formatNumber(div(item()?['hora_fim'],60),'00'),':',formatNumber(mod(item()?['hora_fim'],60),'00')," + q + asp + ";" + asp + q + "," +
  "item()?['tipo_registro']," + q + asp + ";" + asp + q + ",coalesce(item()?['cia_sigla'],'')," + q + asp + ";" + asp + q + "," +
  "coalesce(item()?['voo_chegada'],'')," + q + asp + ";" + asp + q + ",coalesce(item()?['voo_saida'],'')," + q + asp + ";" + asp + q + "," +
  "coalesce(item()?['prefixo'],'')," + q + asp + ";" + asp + q + ",coalesce(item()?['equipamento'],'')," + q + asp + ";" + asp + q + "," +
  "coalesce(item()?['portao'],'')," + q + asp + ";" + asp + q + ",coalesce(item()?['condicao'],'PREVISTO')," + q + asp + ";" + asp + q + "," +
  "if(equals(item()?['internacional'],1),'SIM','NAO')," + q + asp + ";" + asp + q + "," +
  "if(equals(item()?['pesquisado'],1),'SIM','NAO')," + q + asp + ";" + asp + q + "," +
  "if(equals(item()?['alternativa'],1),'SIM','NAO')," + q + asp + ";" + asp + q + "," +
  "coalesce(item()?['responsavel'],'')," + q + asp + ";" + asp + q + ",coalesce(item()?['contato'],'')," + q + asp + ";" + asp + q + "," +
  "replace(coalesce(item()?['observacao'],''),'" + asp + "','''')," + q + asp + q + ")";

// ---- 16/09/2026: autoria e historico de versoes ---------------------------------------------------
// O Douglas pediu para ver "as acoes que foram feitas" num movimento: quem reservou, quem alterou,
// com data e hora. Menor impacto: nada novo gravando log — le o que o SharePoint ja guarda (Author,
// Editor, Created, Modified e o historico de versoes da lista).
const SEP = q + asp + ";" + asp + q;                         // '";"' dentro do concat
const FUSO = "'E. South America Standard Time'";
// convertTimeZone e nao convertFromUtc: a API de versoes devolve Created SEM o Z ("2026-09-04T18:12:50.0000000")
// e o convertFromUtc recusa — foi o erro da primeira execucao, 16/09/2026. O valor e UTC (o Modified da mesma
// versao vem com Z e bate), e convertTimeZone recebe a origem explicita, com ou sem Z.
const quando = (campo) => "convertTimeZone(" + campo + ",'UTC'," + FUSO + ",'dd/MM/yyyy HH:mm')";

// CSV normal: as mesmas 20 colunas de antes + 4 de autoria no fim (quem abre o arquivo antigo nao
// perde coluna de lugar).
const LINHA_AUTORIA = LINHA.slice(0, -("," + q + asp + q + ")").length) + "," + SEP + "," +
  "coalesce(item()?['Author']?['DisplayName'],'')," + SEP + "," + quando("item()?['Created']") + "," + SEP + "," +
  "coalesce(item()?['Editor']?['DisplayName'],'')," + SEP + "," + quando("item()?['Modified']") + "," + q + asp + q + ")";

// Historico: a API de versoes do SharePoint costuma devolver nome interno com sublinhado codificado
// (data_operacao -> data_x005f_operacao). Nao deu para confirmar daqui, entao aceita as duas formas.
const v = (nome) => nome.includes("_")
  ? "coalesce(item()?['" + nome + "'],item()?['" + nome.replace(/_/g, "_x005f_") + "'])"
  : "item()?['" + nome + "']";
// Confirmado na execucao de 16/09/2026: a API de versoes devolve numero como TEXTO no formato do site
// (envergadura "16,2"; milhar viria "1.080"). float("1.080") quebra. Tira o ponto de milhar, troca a
// virgula por ponto e fica com a parte inteira. coalesce antes de string: string(null) nao entra.
const inteiro = (x) => "int(first(split(replace(replace(string(coalesce(" + x + ",'0')),'.',''),',','.'),'.')))";
const hhmm = (x) => "formatNumber(div(" + inteiro(x) + ",60),'00'),':',formatNumber(mod(" + inteiro(x) + ",60),'00')";
// Versao antiga pode nao ter a coluna (data_fim entrou depois): formatDateTime de vazio derruba o pedido.
// if() do Power Automate avalia os dois lados: if(empty(x),'',formatDateTime(x)) ainda quebra com x vazio.
// Data substituta impossivel, formatada e depois apagada — formatDateTime nunca recebe vazio.
const data = (x) => "replace(formatDateTime(coalesce(" + x + ",'1900-01-01T12:00:00Z'),'dd/MM/yyyy'),'01/01/1900','')";
const txt = (x) => "coalesce(string(" + x + "),'')";

const LINHA_VERSAO =
  "@concat(" + q + asp + q + "," +
  "string(items('Para_cada_registro')?['ID'])," + SEP + "," +
  "coalesce(item()?['VersionLabel'],'')," + SEP + "," +
  quando("item()?['Created']") + "," + SEP + "," +
  "coalesce(item()?['Editor']?['LookupValue'],'')," + SEP + "," +
  data(v("data_operacao")) + "," + SEP + "," +
  data(v("data_fim")) + "," + SEP + "," +
  txt(v("posicao_txt")) + "," + SEP + "," +
  hhmm(v("hora_inicio")) + "," + SEP + "," + hhmm(v("hora_fim")) + "," + SEP + "," +
  txt(v("tipo_registro")) + "," + SEP + "," + txt(v("cia_sigla")) + "," + SEP + "," +
  txt(v("voo_chegada")) + "," + SEP + "," + txt(v("voo_saida")) + "," + SEP + "," +
  txt(v("prefixo")) + "," + SEP + "," + txt(v("equipamento")) + "," + SEP + "," +
  txt(v("portao")) + "," + SEP + "," + txt(v("condicao")) + "," + SEP + "," +
  "if(equals(" + inteiro(v("ativo")) + ",0),'EXCLUIDO','ATIVO')," + SEP + "," +
  "replace(" + txt(v("observacao")) + ",'" + asp + "','''')," + q + asp + q + ")";

const COLS = ["Data", "Data fim", "Posicao", "Patio", "Inicio", "Fim", "Tipo", "Companhia", "Voo chegada",
  "Voo saida", "Prefixo", "Equipamento", "Portao", "Condicao", "Internacional", "Pesquisado",
  "Alternativa", "Responsavel", "Contato", "Observacao", "Criado por", "Criado em", "Alterado por", "Alterado em"];
const CABECALHO = COLS.map((c) => '"' + c + '"').join(";");
const COLS_HIST = ["Registro", "Versao", "Data e hora da acao", "Usuario", "Data", "Data fim", "Posicao", "Inicio", "Fim",
  "Tipo", "Companhia", "Voo chegada", "Voo saida", "Prefixo", "Equipamento", "Portao", "Condicao", "Situacao", "Observacao"];
const CABECALHO_HIST = COLS_HIST.map((c) => '"' + c + '"').join(";");
const LIMITE_HISTORICO = 50;
const EH_HISTORICO = "equals(coalesce(triggerBody()?['historico'],0),1)";
const CRLF = "decodeUriComponent('%0D%0A')";

const definition = {
  name: FLOW_ID,
  id: "/providers/Microsoft.Flow/flows/" + FLOW_ID,
  type: "Microsoft.Flow/flows",
  properties: {
    apiId: "/providers/Microsoft.PowerApps/apis/shared_logicflows",
    displayName: "Exportar programacao",
    definition: {
      $schema: "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
      metadata: {
        workflowEntityId: null,
        processAdvisorMetadata: null,
        flowChargedByPaygo: null,
        flowclientsuspensionreason: "None",
        flowclientsuspensiontime: null,
        flowclientsuspensionreasondetails: null,
        creator: null,
        provisioningMethod: "FromDefinition",
        failureAlertSubscription: true,
        creationSource: "Portal",
        modifiedSources: "Portal",
      },
      contentVersion: "1.0.0.0",
      parameters: {
        $authentication: { defaultValue: {}, type: "SecureObject" },
        $connections: { defaultValue: {}, type: "Object" },
      },
      triggers: {
        Quando_um_pedido_entra: {
          recurrence: { frequency: "Minute", interval: 1 },
          evaluatedRecurrence: { frequency: "Minute", interval: 1 },
          splitOn: "@triggerOutputs()?['body/value']",
          type: "OpenApiConnection",
          inputs: {
            parameters: { dataset: SITE, table: "tb_exportacaoMapa" },
            host: Object.assign({}, HOST, { operationId: "GetOnUpdatedItems" }),
            authentication: "@parameters('$authentication')",
          },
          conditions: [{ expression: "@equals(triggerBody()?['status'], 'PRONTO')" }],
        },
      },
      actions: {
        Marcar_processando: Object.assign(
          sp("PatchItem", Object.assign({}, patchBase, { "item/status": "PROCESSANDO" })),
          { runAfter: {} }
        ),

        // Variavel so se inicializa no nivel de cima; o ramo do historico acumula o CSV aqui.
        Inicializar_historico: {
          type: "InitializeVariable",
          inputs: { variables: [{ name: "csv_historico", type: "string", value: "" }] },
          runAfter: { Marcar_processando: ["Succeeded"] },
        },

        Obter_movimentacao: Object.assign(
          sp("GetItems", {
            dataset: SITE,
            table: "tb_alocacoesMapa",
            // Sem "ativo eq 1" desde 16/09/2026: o historico precisa do registro excluido (ativo = 0) para
            // mostrar quem excluiu. O corte de ativo foi para o Filtrar_opcionais, que ja e condicional.
            $filter:
              "aeroporto eq '@{triggerBody()?['aeroporto']}' and " +
              "data_operacao ge '@{formatDateTime(triggerBody()?['data_de'],'yyyy-MM-dd')}' and " +
              "data_operacao le '@{formatDateTime(triggerBody()?['data_ate'],'yyyy-MM-dd')}'",
            // Sem isto o arquivo sai na ordem em que o SharePoint devolve, que e por ID:
            // os voos semanais de setembro apareciam antes do dia 1.
            $orderby: "data_operacao asc,hora_inicio asc",
            $top: 5000,
          }),
          {
            runAfter: { Inicializar_historico: ["Succeeded"] },
            runtimeConfiguration: { paginationPolicy: { minimumItemCount: 5000 } },
          }
        ),

        // Os filtros opcionais ficam aqui e nao no $filter: montar OData condicional
        // a mao e onde este fluxo quebraria.
        Filtrar_opcionais: {
          type: "Query",
          inputs: {
            from: "@outputs('Obter_movimentacao')?['body/value']",
            where:
              "@and(or(equals(coalesce(triggerBody()?['so_internacional'],0),0),equals(item()?['internacional'],1))," +
              "or(equals(coalesce(triggerBody()?['so_pesquisado'],0),0),equals(item()?['pesquisado'],1))," +
              // historico ligado inclui finalizados e excluidos: e justamente o que se quer investigar
              "or(" + EH_HISTORICO + ",equals(coalesce(triggerBody()?['incluir_finalizados'],0),1),not(equals(item()?['condicao'],'FINALIZADO')))," +
              "or(" + EH_HISTORICO + ",equals(item()?['ativo'],1))," +
              "or(empty(coalesce(triggerBody()?['patio'],'')),equals(item()?['patio_txt'],triggerBody()?['patio']))," +
              // busca: voo de chegada, voo de saida, prefixo ou companhia, sem diferenciar maiuscula
              "or(empty(trim(coalesce(triggerBody()?['busca'],''))),contains(toUpper(concat(" +
              "string(coalesce(item()?['voo_chegada'],'')),'|',string(coalesce(item()?['voo_saida'],'')),'|'," +
              "coalesce(item()?['prefixo'],''),'|',coalesce(item()?['cia_sigla'],''))),toUpper(trim(triggerBody()?['busca'])))))",
          },
          runAfter: { Obter_movimentacao: ["Succeeded"] },
        },

        // Select em MODO TEXTO: a saida e lista de strings, nao de objetos, para o
        // join do passo seguinte funcionar. E monta a linha com ponto e virgula, porque
        // a acao "Criar tabela CSV" separa por virgula e o Excel em portugues abriria
        // tudo numa coluna so.
        Montar_linhas: {
          type: "Select",
          inputs: { from: "@body('Filtrar_opcionais')", select: LINHA_AUTORIA },
          runAfter: { Filtrar_opcionais: ["Succeeded"] },
        },

        // Historico de versoes. So com poucos registros: e uma chamada ao SharePoint por registro.
        Modo_historico: {
          type: "If",
          expression: { equals: ["@coalesce(triggerBody()?['historico'],0)", 1] },
          actions: {
            Limite_historico: {
              type: "If",
              expression: { greater: ["@length(body('Filtrar_opcionais'))", LIMITE_HISTORICO] },
              actions: {
                Recusar_historico: Object.assign(
                  sp("PatchItem", Object.assign({}, patchBase, {
                    "item/status": "ERRO",
                    "item/total": "@length(body('Filtrar_opcionais'))",
                    "item/mensagem":
                      "@{concat('O historico foi pedido para ', string(length(body('Filtrar_opcionais'))), " +
                      "' registros; o limite e " + LIMITE_HISTORICO + ". Use a busca por voo, prefixo ou companhia, ou um periodo menor.')}",
                  })),
                  { runAfter: {} }
                ),
                Encerrar_historico: {
                  type: "Terminate",
                  inputs: { runStatus: "Cancelled" },
                  runAfter: { Recusar_historico: ["Succeeded"] },
                },
              },
              else: { actions: {} },
              runAfter: {},
            },
            Para_cada_registro: {
              type: "Foreach",
              foreach: "@body('Filtrar_opcionais')",
              // 1 por vez: o texto e acumulado numa variavel, e em paralelo as linhas se misturariam
              runtimeConfiguration: { concurrency: { repetitions: 1 } },
              actions: {
                // Mesma acao "Enviar solicitacao HTTP ao SharePoint" do List_Generator, que roda neste ambiente.
                Obter_versoes: Object.assign(
                  sp("HttpRequest", {
                    dataset: SITE,
                    "parameters/method": "GET",
                    "parameters/uri":
                      "_api/web/lists/getbytitle('tb_alocacoesMapa')/items(@{items('Para_cada_registro')?['ID']})/versions",
                    "parameters/headers": { Accept: "application/json;odata=nometadata" },
                  }),
                  { runAfter: {} }
                ),
                // A API devolve da versao mais nova para a mais antiga; reverse() poe em ordem de acontecimento.
                Montar_versoes: {
                  type: "Select",
                  inputs: { from: "@reverse(body('Obter_versoes')?['value'])", select: LINHA_VERSAO },
                  runAfter: { Obter_versoes: ["Succeeded"] },
                },
                Acumular_versoes: {
                  type: "AppendToStringVariable",
                  inputs: {
                    name: "csv_historico",
                    value: "@{concat(join(body('Montar_versoes')," + CRLF + ")," + CRLF + ")}",
                  },
                  runAfter: { Montar_versoes: ["Succeeded"] },
                },
              },
              runAfter: { Limite_historico: ["Succeeded"] },
            },
          },
          else: { actions: {} },
          runAfter: { Montar_linhas: ["Succeeded"] },
        },

        Criar_arquivo: Object.assign(
          sp("CreateFile", {
            dataset: SITE,
            // "Partilhados", nao "Compartilhados": confirmado pela URL do arquivo gerado em 09/09/2026.
            folderPath: "/Documentos Partilhados/exportacoes",
            name:
              "programacao@{if(" + EH_HISTORICO + ",'_historico','')}_@{triggerBody()?['aeroporto']}_@{formatDateTime(triggerBody()?['data_de'],'yyyyMMdd')}" +
              "_a_@{formatDateTime(triggerBody()?['data_ate'],'yyyyMMdd')}.csv",
            // decodeUriComponent('%EF%BB%BF') e a marca UTF-8. Sem ela o Excel abre
            // "Navegantes" corrompido e o operador conclui que o arquivo quebrou.
            body:
              "@{concat(decodeUriComponent('%EF%BB%BF'),if(" + EH_HISTORICO + ",'" + CABECALHO_HIST + "','" + CABECALHO + "')," +
              CRLF + ",if(" + EH_HISTORICO + ",variables('csv_historico'),join(body('Montar_linhas')," + CRLF + ")))}",
          }),
          { runAfter: { Modo_historico: ["Succeeded"] } }
        ),

        Concluir: Object.assign(
          sp("PatchItem", Object.assign({}, patchBase, {
            "item/status": "CONCLUIDO",
            "item/total": "@length(body('Filtrar_opcionais'))",
            "item/arquivo_nome": "@body('Criar_arquivo')?['Name']",
            // O Path devolvido e relativo ao SITE, nao ao host: sem o /sites/AIRPORTNOW o link da 404.
            "item/arquivo_url": "@{concat('" + SITE + "',body('Criar_arquivo')?['Path'])}",
          })),
          { runAfter: { Criar_arquivo: ["Succeeded"] } }
        ),

        // Sem este ramo, uma falha deixa o pedido preso em PROCESSANDO e o operador
        // nao sabe se espera ou refaz.
        Marcar_erro: Object.assign(
          sp("PatchItem", Object.assign({}, patchBase, {
            "item/status": "ERRO",
            "item/mensagem": "Falha ao gerar o arquivo. Veja o historico da execucao no fluxo Exportar programacao.",
          })),
          { runAfter: { Criar_arquivo: ["Failed", "Skipped", "TimedOut"] } }
        ),
      },
      outputs: {},
    },
    connectionReferences: {
      shared_sharepointonline: {
        connectionName: CONN_NAME,
        source: "Embedded",
        id: "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
        tier: "NotSpecified",
        apiName: "sharepointonline",
        isProcessSimpleApiReferenceConversionAlreadyDone: false,
      },
    },
    flowFailureAlertSubscribed: false,
    isManaged: false,
  },
};

const resources = {};
resources[FLOW_ID] = {
  type: "Microsoft.Flow/flows",
  suggestedCreationType: "New",
  creationType: "Existing, New, Update",
  details: { displayName: "Exportar programacao" },
  configurableBy: "User",
  hierarchy: "Root",
  dependsOn: [API_ID, CONN_ID],
};
resources[API_ID] = {
  id: "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
  name: "shared_sharepointonline",
  type: "Microsoft.PowerApps/apis",
  suggestedCreationType: "Existing",
  details: { displayName: "SharePoint", iconUri: ICON },
  configurableBy: "System",
  hierarchy: "Child",
  dependsOn: [],
};
resources[CONN_ID] = {
  type: "Microsoft.PowerApps/apis/connections",
  suggestedCreationType: "Existing",
  creationType: "Existing",
  details: { displayName: "SharePoint (conexao existente)", iconUri: ICON },
  configurableBy: "User",
  hierarchy: "Child",
  dependsOn: [API_ID],
};

const manifest = {
  schema: "1.0",
  details: {
    displayName: "Exportar programacao",
    description: "",
    createdTime: new Date().toISOString(),
    packageTelemetryId: "b4e1c7d2-0a55-4f18-9e63-2c7a1d8f4b90",
    creator: "N/A",
    sourceEnvironment: "",
  },
  resources: resources,
};

const entradas = [
  ["Microsoft.Flow/flows/" + FLOW_ID + "/apisMap.json", JSON.stringify({ shared_sharepointonline: API_ID })],
  ["Microsoft.Flow/flows/" + FLOW_ID + "/connectionsMap.json", JSON.stringify({ shared_sharepointonline: CONN_ID })],
  ["Microsoft.Flow/flows/" + FLOW_ID + "/definition.json", JSON.stringify(definition)],
  ["Microsoft.Flow/flows/manifest.json", JSON.stringify({ packageSchemaVersion: "1.0", flowAssets: { assetPaths: [FLOW_ID] } })],
  ["manifest.json", JSON.stringify(manifest)],
];

function crc32(buf) {
  if (!crc32.t) {
    crc32.t = [];
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      crc32.t[n] = c >>> 0;
    }
  }
  let c = 0xffffffff;
  for (const b of buf) c = crc32.t[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

const locais = [], centrais = [];
let off = 0;
for (const par of entradas) {
  const dados = Buffer.from(par[1], "utf8");
  const comp = zlib.deflateRawSync(dados, { level: 9 });
  const nb = Buffer.from(par[0], "utf8");
  const crc = crc32(dados);
  const lh = Buffer.alloc(30);
  lh.writeUInt32LE(0x04034b50, 0); lh.writeUInt16LE(20, 4); lh.writeUInt16LE(0, 6);
  lh.writeUInt16LE(8, 8); lh.writeUInt16LE(0, 10); lh.writeUInt16LE(0, 12);
  lh.writeUInt32LE(crc, 14); lh.writeUInt32LE(comp.length, 18); lh.writeUInt32LE(dados.length, 22);
  lh.writeUInt16LE(nb.length, 26); lh.writeUInt16LE(0, 28);
  locais.push(lh, nb, comp);
  const ch = Buffer.alloc(46);
  ch.writeUInt32LE(0x02014b50, 0); ch.writeUInt16LE(20, 4); ch.writeUInt16LE(20, 6);
  ch.writeUInt16LE(0, 8); ch.writeUInt16LE(8, 10); ch.writeUInt16LE(0, 12); ch.writeUInt16LE(0, 14);
  ch.writeUInt32LE(crc, 16); ch.writeUInt32LE(comp.length, 20); ch.writeUInt32LE(dados.length, 24);
  ch.writeUInt16LE(nb.length, 28); ch.writeUInt16LE(0, 30); ch.writeUInt16LE(0, 32);
  ch.writeUInt16LE(0, 34); ch.writeUInt16LE(0, 36); ch.writeUInt32LE(0, 38);
  ch.writeUInt32LE(off, 42);
  centrais.push(ch, nb);
  off += 30 + nb.length + comp.length;
}
const corpo = Buffer.concat(locais);
const central = Buffer.concat(centrais);
const fim = Buffer.alloc(22);
fim.writeUInt32LE(0x06054b50, 0); fim.writeUInt16LE(0, 4); fim.writeUInt16LE(0, 6);
fim.writeUInt16LE(entradas.length, 8); fim.writeUInt16LE(entradas.length, 10);
fim.writeUInt32LE(central.length, 12); fim.writeUInt32LE(corpo.length, 16); fim.writeUInt16LE(0, 20);

fs.writeFileSync(process.argv[2], Buffer.concat([corpo, central, fim]));
fs.writeFileSync(process.argv[3], JSON.stringify(definition, null, 2) + "\n");
console.log("zip gerado:", fs.statSync(process.argv[2]).size, "bytes,", entradas.length, "entradas");
