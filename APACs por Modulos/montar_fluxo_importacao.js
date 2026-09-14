// montar_fluxo_importacao.js — gera o pacote do fluxo "Importar malha APAC" para o Power Automate.
//
// Uso:  node montar_fluxo_importacao.js
// Saída: fluxo/ImportarMalhaAPAC.zip  (Meus fluxos → Importar → Pacote (herdado))
//        fluxo/importar_malha_apac.definition.json  (a mesma definição, legível, para revisar)
//
// Molde: o pacote do Mapa de Alocação (Importarprogramacao_COMPLETO.zip), que importou neste tenant.
// O que foi herdado de erro real, e está explicado em FLUXO_IMPORTACAO_APAC.md:
//   - entradas do zip com "/" e na ordem do pacote original (o .NET grava "\" e o Power Automate recusa)
//   - suggestedCreationType "New" no manifesto
//   - operationId conferido contra o conector (GetItemAttachments, não GetAttachments)
//   - só a conexão do SharePoint no pacote; o Office Script entra por uma COSTURA ligada à mão
//   - PatchItem manda TODAS as colunas obrigatórias, mesmo as que não mudam
//
// O que muda em relação ao Mapa, e por quê:
//   1. GRAVA EM LOTES DE 50, em paralelo dentro do lote. O Mapa gasta ~4 ações por registro
//      (criar, incrementar, condição, às vezes atualizar). Com 3.841 voos seriam ~15 mil pedidos numa
//      execução, e o limite diário de pedidos da licença M365 é da ordem de 10 mil. Em lotes são ~4 mil.
//   2. O TRABALHO FICA NUM ESCOPO, e o Marcar_erro roda se o escopo falhar. No Mapa ele dependia de seis
//      ações ao mesmo tempo — e como uma falha faz as seguintes serem PULADAS, não falhadas, a condição
//      quase nunca fechava e a importação ficava presa em PROCESSANDO.
//   3. NADA É APAGADO SEM O SCRIPT TER DITO OK. O filtro de exclusão vem do script; se a costura não
//      estiver ligada, ou o arquivo estiver errado, o fluxo recusa antes de apagar qualquer coisa.

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const SITE = "https://grupoccr.sharepoint.com/sites/AIRPORTNOW";
const LISTA_IMP = "tb_apacImportacao";   // pelo título: o GUID só existe depois de criar a lista
const LISTA_MALHA = "tb_apacMalha";
const PASTA = "/Documentos Compartilhados/Importar";   // a mesma pasta que a importação do Mapa usa
const LOTE = 50;
const PARALELO = 10;

const FLOW_ID = "5b7d2e91-4c3a-4f0e-9a61-7e2c8d4f1a3b";
const API_ID = "1821735d-649e-4ffe-933f-35a1c1e32c2a";
const CONN_ID = "822f4c97-d670-4aa7-baf5-c0129e3ecf71";
const CONN_NAME = "shared-sharepointonl-0cd12861-383f-4b6e-9359-db983fb70160";
const ICON = "https://static.powerapps.com/resource/ppcr/releases/v1.0.1827/1.0.1827.4913/sharepointonline/icon.png";
const NOME = "Importar malha APAC";

const sp = (operationId, parameters, extra) => Object.assign({
  type: "OpenApiConnection",
  inputs: {
    parameters,
    host: {
      apiId: "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      connectionName: "shared_sharepointonline",
      operationId,
    },
    authentication: "@parameters('$authentication')",
  },
}, extra || {});

const T = (c) => "@triggerBody()?['" + c + "']";
const R = (c) => "@outputs('Resultado_script')?['" + c + "']";
const RN = (c) => "@coalesce(outputs('Resultado_script')?['" + c + "'], 0)";
const ID = T("ID");

// tb_apacImportacao: obrigatórias = aeroporto, status, total_lidos, total_gravados, total_descartados, ativo.
// Cada PatchItem parte do valor do gatilho e sobrescreve só o que muda naquela etapa.
const patchImp = (over, extra) => sp("PatchItem", Object.assign({
  dataset: SITE, table: LISTA_IMP, id: ID,
  "item/aeroporto": T("aeroporto"),
  "item/competencia": T("competencia"),
  "item/status": T("status"),
  "item/total_lidos": T("total_lidos"),
  "item/total_gravados": T("total_gravados"),
  "item/total_descartados": T("total_descartados"),
  "item/ativo": T("ativo"),
}, over), extra);

// ------------------------------------------------------------------ dentro do escopo
const processar = {};

processar.Obter_anexos = sp("GetItemAttachments", {
  dataset: SITE, table: LISTA_IMP, itemId: ID,
}, { runAfter: {} });

// a tela limita a um anexo: first() em vez de laço
processar.Obter_conteudo_do_anexo = sp("GetAttachmentContent", {
  dataset: SITE, table: LISTA_IMP, itemId: ID,
  attachmentId: "@{first(body('Obter_anexos'))?['Id']}",
}, { runAfter: { Obter_anexos: ["Succeeded"] } });

// o conector do Excel não lê binário solto: precisa de arquivo com caminho. Nome pelo ID para duas
// importações não sobrescreverem uma à outra.
processar.Salvar_planilha = sp("CreateFile", {
  dataset: SITE,
  folderPath: PASTA,
  name: "malha-apac-@{triggerBody()?['ID']}.xlsx",
  body: "@body('Obter_conteudo_do_anexo')",
}, { runAfter: { Obter_conteudo_do_anexo: ["Succeeded"] } });

// >>>>>>>>>>>>>>>>>>>>>>>> A COSTURA <<<<<<<<<<<<<<<<<<<<<<<<
// Forma exata do retorno do script, com ok=false. Rodar sem religar não apaga nem grava nada: cai no
// ramo Recusar e escreve o motivo na tela.
processar.Resultado_script = {
  runAfter: { Salvar_planilha: ["Succeeded"] },
  type: "Compose",
  inputs: {
    ok: false,
    mensagem: "COSTURA NAO LIGADA: acrescente a acao do Excel 'Executar script de uma biblioteca do SharePoint' e troque o valor desta acao pelo resultado dela. Ver FLUXO_IMPORTACAO_APAC.md.",
    aeroporto: "",
    mes_ref: "",
    total: 0,
    descartados: 0,
    competencias: [],
    filtro: "",
    registros: [],
  },
};

processar.Guardar_total = patchImp({
  "item/status": "PROCESSANDO",
  "item/total_lidos": RN("total"),
  "item/total_gravados": 0,
  "item/total_descartados": RN("descartados"),
  "item/arquivo": "@{first(body('Obter_anexos'))?['DisplayName']}",
  "item/mensagem": R("mensagem"),
}, { runAfter: { Resultado_script: ["Succeeded"] } });

// ---- ramo SIM: o script disse ok, leu voo e devolveu filtro
const gravar = {};

// Apaga só as competências que este arquivo traz, só deste aeroporto. Sem este passo, reimportar
// duplica a malha — e duplicar a malha dobra o efetivo calculado sem erro nenhum.
gravar.Obter_malha_anterior = sp("GetItems", {
  dataset: SITE, table: LISTA_MALHA,
  $filter: "aeroporto eq '@{triggerBody()?['aeroporto']}' and (@{outputs('Resultado_script')?['filtro']})",
  $top: 5000,
}, {
  runAfter: {},
  runtimeConfiguration: { paginationPolicy: { minimumItemCount: 5000 } },
});

gravar.Apagar_anteriores = {
  runAfter: { Obter_malha_anterior: ["Succeeded"] },
  type: "Foreach",
  foreach: "@outputs('Obter_malha_anterior')?['body/value']",
  runtimeConfiguration: { concurrency: { repetitions: PARALELO } },
  actions: {
    Excluir_voo_anterior: sp("DeleteItem", {
      dataset: SITE, table: LISTA_MALHA,
      id: "@items('Apagar_anteriores')?['ID']",
    }, { runAfter: {} }),
  },
};

// Lotes em sequência (o contador da barra só é somado entre lotes, nunca em paralelo); voos dentro
// do lote em paralelo.
gravar.Gravar_lotes = {
  runAfter: { Apagar_anteriores: ["Succeeded"] },
  type: "Foreach",
  foreach: "@chunk(outputs('Resultado_script')?['registros'], " + LOTE + ")",
  runtimeConfiguration: { concurrency: { repetitions: 1 } },
  actions: {
    Gravar_lote: {
      runAfter: {},
      type: "Foreach",
      foreach: "@items('Gravar_lotes')",
      runtimeConfiguration: { concurrency: { repetitions: PARALELO } },
      actions: {
        // as 12 colunas; ativo explícito — voo com ativo vazio some da tela sem erro
        Criar_voo: sp("PostItem", {
          dataset: SITE, table: LISTA_MALHA,
          "item/aeroporto": "@items('Gravar_lote')?['aeroporto']",
          "item/competencia": "@items('Gravar_lote')?['competencia']",
          "item/data": "@items('Gravar_lote')?['data']",
          "item/hora_min": "@items('Gravar_lote')?['hora_min']",
          "item/empresa": "@items('Gravar_lote')?['empresa']",
          "item/voo": "@items('Gravar_lote')?['voo']",
          "item/rota": "@items('Gravar_lote')?['rota']",
          "item/aeronave": "@items('Gravar_lote')?['aeronave']",
          "item/assentos": "@items('Gravar_lote')?['assentos']",
          "item/tipo_voo": "@items('Gravar_lote')?['tipo_voo']",
          "item/dia_semana": "@items('Gravar_lote')?['dia_semana']",
          "item/ativo": "@items('Gravar_lote')?['ativo']",
        }, { runAfter: {} }),
      },
    },
    Somar_lote: {
      runAfter: { Gravar_lote: ["Succeeded"] },
      type: "IncrementVariable",
      inputs: { name: "gravados", value: "@length(items('Gravar_lotes'))" },
    },
    Atualizar_barra: patchImp({
      "item/status": "PROCESSANDO",
      "item/total_lidos": RN("total"),
      "item/total_gravados": "@variables('gravados')",
      "item/total_descartados": RN("descartados"),
    }, { runAfter: { Somar_lote: ["Succeeded"] } }),
  },
};

gravar.Fechar = patchImp({
  "item/status": "CONCLUIDO",
  "item/total_lidos": RN("total"),
  "item/total_gravados": "@variables('gravados')",
  "item/total_descartados": RN("descartados"),
  "item/mensagem": "@{outputs('Resultado_script')?['mensagem']} Gravados: @{variables('gravados')}.",
}, { runAfter: { Gravar_lotes: ["Succeeded"] } });

// ---- ramo NÃO: nada é apagado nem gravado
const recusar = {
  Recusar: patchImp({
    "item/status": "ERRO",
    "item/total_lidos": RN("total"),
    "item/total_gravados": 0,
    "item/total_descartados": RN("descartados"),
    "item/mensagem": "@{coalesce(outputs('Resultado_script')?['mensagem'], 'O script nao devolveu resultado.')} Nada foi apagado nem gravado.",
  }, { runAfter: {} }),
};

processar.Conferir_resultado = {
  runAfter: { Guardar_total: ["Succeeded"] },
  type: "If",
  expression: {
    and: [
      { equals: ["@outputs('Resultado_script')?['ok']", true] },
      { greater: ["@coalesce(outputs('Resultado_script')?['total'], 0)", 0] },
      { not: { equals: ["@coalesce(outputs('Resultado_script')?['filtro'], '')", ""] } },
    ],
  },
  actions: gravar,
  else: { actions: recusar },
};

// ------------------------------------------------------------------ nível de cima
const actions = {};

// variável tem de ser inicializada no nível de cima — e antes de tudo, para o Marcar_erro poder lê-la
actions.Inicializar_gravados = {
  runAfter: {},
  type: "InitializeVariable",
  inputs: { variables: [{ name: "gravados", type: "integer", value: 0 }] },
};

// também é o que tira o item da condição de gatilho: a próxima modificação não redispara
actions.Marcar_processando = patchImp(
  { "item/status": "PROCESSANDO" },
  { runAfter: { Inicializar_gravados: ["Succeeded"] } });

actions.Processar = {
  runAfter: { Marcar_processando: ["Succeeded"] },
  type: "Scope",
  actions: processar,
};

// sem isto, falha no meio deixa o item em PROCESSANDO para sempre e a barra parada sem explicação
actions.Marcar_erro = patchImp({
  "item/status": "ERRO",
  "item/total_gravados": "@variables('gravados')",
  "item/mensagem": "A importacao falhou no meio. Gravados ate a falha: @{variables('gravados')}. Veja o historico do fluxo Importar malha APAC e importe de novo: a reimportacao apaga o que ficou pela metade.",
}, { runAfter: { Processar: ["Failed", "TimedOut"] } });

// ------------------------------------------------------------------ definição
const definition = {
  name: FLOW_ID,
  id: "/providers/Microsoft.Flow/flows/" + FLOW_ID,
  type: "Microsoft.Flow/flows",
  properties: {
    apiId: "/providers/Microsoft.PowerApps/apis/shared_logicflows",
    displayName: NOME,
    definition: {
      $schema: "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
      contentVersion: "1.0.0.0",
      parameters: {
        $authentication: { defaultValue: {}, type: "SecureObject" },
        $connections: { defaultValue: {}, type: "Object" },
      },
      triggers: {
        When_an_item_is_created_or_modified: {
          recurrence: { frequency: "Minute", interval: 1 },
          evaluatedRecurrence: { frequency: "Minute", interval: 1 },
          splitOn: "@triggerOutputs()?['body/value']",
          type: "OpenApiConnection",
          inputs: {
            parameters: { dataset: SITE, table: LISTA_IMP },
            host: {
              apiId: "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
              connectionName: "shared_sharepointonline",
              operationId: "GetOnUpdatedItems",
            },
            authentication: "@parameters('$authentication')",
          },
          // A TRAVA: o fluxo altera o item que o dispara. Sem isto, laço infinito.
          conditions: [{ expression: "@equals(triggerBody()?['status'], 'PRONTO')" }],
        },
      },
      actions,
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

// ------------------------------------------------------------------ conferências
const erros = [];
const OBR = {
  [LISTA_IMP]: ["aeroporto", "status", "total_lidos", "total_gravados", "total_descartados", "ativo"],
  [LISTA_MALHA]: ["aeroporto", "competencia", "data", "hora_min", "voo", "assentos", "ativo"],
};
const COLUNAS = {
  [LISTA_IMP]: JSON.parse(fs.readFileSync(path.join(__dirname, "lista_tb_apacImportacao.json"), "utf8")).colunas.map((c) => c.internalName),
  [LISTA_MALHA]: JSON.parse(fs.readFileSync(path.join(__dirname, "lista_tb_apacMalha.json"), "utf8")).colunas.map((c) => c.internalName),
};
const nomes = new Map();   // nome da ação -> caminho do escopo

(function anda(as, escopo, nivel) {
  const irmas = new Set(Object.keys(as));
  for (const [n, a] of Object.entries(as)) {
    if (nomes.has(n)) erros.push(`nome de ação repetido: ${n}`);
    nomes.set(n, escopo);
    for (const dep of Object.keys(a.runAfter || {})) {
      if (!irmas.has(dep)) erros.push(`${n}: runAfter aponta para '${dep}', que não está no mesmo nível`);
    }
    if (a.type === "InitializeVariable" && nivel > 0) erros.push(`${n}: InitializeVariable fora do nível de cima`);
    const op = a.inputs && a.inputs.host && a.inputs.host.operationId;
    if (op === "PatchItem" || op === "PostItem") {
      const p = a.inputs.parameters;
      for (const c of OBR[p.table] || []) if (!(("item/" + c) in p)) erros.push(`${n}: falta a obrigatória ${c}`);
      for (const k of Object.keys(p).filter((k) => k.startsWith("item/"))) {
        if (!(COLUNAS[p.table] || []).includes(k.slice(5))) erros.push(`${n}: coluna '${k.slice(5)}' não existe em ${p.table}`);
      }
    }
    if (a.actions) anda(a.actions, escopo + "/" + n, nivel + 1);
    if (a.else) anda(a.else.actions, escopo + "/" + n + "(senão)", nivel + 1);
  }
})(actions, "", 0);

const texto = JSON.stringify(actions);
for (const m of texto.matchAll(/(?:outputs|body|items|result)\('([^']+)'\)/g)) {
  if (!nomes.has(m[1])) erros.push(`referência a ação inexistente: ${m[1]}`);
}
for (const m of texto.matchAll(/variables\('([^']+)'\)/g)) {
  if (m[1] !== "gravados") erros.push(`variável não inicializada: ${m[1]}`);
}
// items('X') só vale dentro do laço X
(function itens(as, lacos) {
  for (const [n, a] of Object.entries(as)) {
    const proprio = JSON.stringify(Object.assign({}, a, { actions: undefined, else: undefined }));
    for (const m of proprio.matchAll(/items\('([^']+)'\)/g)) {
      const dentro = a.type === "Foreach" && m[1] === n ? false : !lacos.includes(m[1]);
      if (dentro && !(a.type === "Foreach" && lacos.includes(m[1]))) erros.push(`${n}: usa items('${m[1]}') fora desse laço`);
    }
    const novos = a.type === "Foreach" ? lacos.concat(n) : lacos;
    if (a.actions) itens(a.actions, novos);
    if (a.else) itens(a.else.actions, novos);
  }
})(actions, []);

if (erros.length) {
  console.error("✗ definição com problema — nada foi gravado:");
  erros.forEach((e) => console.error("   " + e));
  process.exit(1);
}

// ------------------------------------------------------------------ pacote
const resources = {};
resources[FLOW_ID] = {
  type: "Microsoft.Flow/flows", suggestedCreationType: "New", creationType: "Existing, New, Update",
  details: { displayName: NOME }, configurableBy: "User", hierarchy: "Root", dependsOn: [API_ID, CONN_ID],
};
resources[API_ID] = {
  id: "/providers/Microsoft.PowerApps/apis/shared_sharepointonline", name: "shared_sharepointonline",
  type: "Microsoft.PowerApps/apis", suggestedCreationType: "Existing",
  details: { displayName: "SharePoint", iconUri: ICON }, configurableBy: "System", hierarchy: "Child", dependsOn: [],
};
resources[CONN_ID] = {
  type: "Microsoft.PowerApps/apis/connections", suggestedCreationType: "Existing", creationType: "Existing",
  details: { displayName: "SharePoint (conexao existente)", iconUri: ICON }, configurableBy: "User",
  hierarchy: "Child", dependsOn: [API_ID],
};
const manifest = {
  schema: "1.0",
  details: {
    displayName: NOME, description: "Importa a malha de decolagens do Power BI para tb_apacMalha",
    createdTime: "2026-09-14T18:00:00.0000000Z", packageTelemetryId: "c2a7e5d1-8b43-4f6a-9d20-3e1b7c5a9f84",
    creator: "N/A", sourceEnvironment: "",
  },
  resources,
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
    for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; crc32.t[n] = c >>> 0; }
  }
  let c = 0xffffffff;
  for (const b of buf) c = crc32.t[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
const locais = [], centrais = [];
let off = 0;
for (const [nome, conteudo] of entradas) {
  if (nome.includes("\\")) throw new Error("entrada com barra invertida: " + nome);
  const dados = Buffer.from(conteudo, "utf8");
  const comp = zlib.deflateRawSync(dados, { level: 9 });
  const nb = Buffer.from(nome, "utf8");
  const crc = crc32(dados);
  const lh = Buffer.alloc(30);
  lh.writeUInt32LE(0x04034b50, 0); lh.writeUInt16LE(20, 4); lh.writeUInt16LE(0, 6); lh.writeUInt16LE(8, 8);
  lh.writeUInt16LE(0, 10); lh.writeUInt16LE(0, 12); lh.writeUInt32LE(crc, 14); lh.writeUInt32LE(comp.length, 18);
  lh.writeUInt32LE(dados.length, 22); lh.writeUInt16LE(nb.length, 26); lh.writeUInt16LE(0, 28);
  locais.push(lh, nb, comp);
  const ch = Buffer.alloc(46);
  ch.writeUInt32LE(0x02014b50, 0); ch.writeUInt16LE(20, 4); ch.writeUInt16LE(20, 6); ch.writeUInt16LE(0, 8);
  ch.writeUInt16LE(8, 10); ch.writeUInt16LE(0, 12); ch.writeUInt16LE(0, 14); ch.writeUInt32LE(crc, 16);
  ch.writeUInt32LE(comp.length, 20); ch.writeUInt32LE(dados.length, 24); ch.writeUInt16LE(nb.length, 28);
  ch.writeUInt16LE(0, 30); ch.writeUInt16LE(0, 32); ch.writeUInt16LE(0, 34); ch.writeUInt16LE(0, 36);
  ch.writeUInt32LE(0, 38); ch.writeUInt32LE(off, 42);
  centrais.push(ch, nb);
  off += 30 + nb.length + comp.length;
}
const corpo = Buffer.concat(locais), central = Buffer.concat(centrais), fim = Buffer.alloc(22);
fim.writeUInt32LE(0x06054b50, 0); fim.writeUInt16LE(0, 4); fim.writeUInt16LE(0, 6);
fim.writeUInt16LE(entradas.length, 8); fim.writeUInt16LE(entradas.length, 10);
fim.writeUInt32LE(central.length, 12); fim.writeUInt32LE(corpo.length, 16); fim.writeUInt16LE(0, 20);

const SAIDA = path.join(__dirname, "fluxo");
fs.mkdirSync(SAIDA, { recursive: true });
fs.writeFileSync(path.join(SAIDA, "ImportarMalhaAPAC.zip"), Buffer.concat([corpo, central, fim]));
fs.writeFileSync(path.join(SAIDA, "importar_malha_apac.definition.json"), JSON.stringify(definition, null, 2) + "\n");

let n = 0; (function conta(as) { for (const a of Object.values(as)) { n++; if (a.actions) conta(a.actions); if (a.else) conta(a.else.actions); } })(actions);
console.log(`✓ ${n} ações, 0 problemas nas conferências`);
console.log(`✓ fluxo/ImportarMalhaAPAC.zip (${fs.statSync(path.join(SAIDA, "ImportarMalhaAPAC.zip")).size} bytes, ${entradas.length} entradas)`);
