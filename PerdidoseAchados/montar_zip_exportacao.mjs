// Empacota o fluxo "Exportar Perdidos e Achados" num .zip importavel pelo
// Power Automate (Meus fluxos > Importar > Pacote legado).
//
// Molde: montar_zip_exportacao.js do Mapa de Alocacao, que funcionou neste
// ambiente. Os cuidados abaixo vieram de erro real la, nao invente diferente:
//   - entradas com "/" e nesta ordem (o .NET escreve "\" e o Power Automate recusa)
//   - manifest com suggestedCreationType "New", senao ele pede "salve como novo
//     fluxo primeiro" e nao importa
//   - a definicao vem do .json versionado, para nao existirem duas verdades
//
// Uso:
//   node montar_zip_exportacao.mjs fluxo_exportar_perdidosachados.definition.json Exportar_PerdidosAchados.zip
import fs from 'fs';
import zlib from 'zlib';

const ENTRADA = process.argv[2] || 'fluxo_exportar_perdidosachados.definition.json';
const SAIDA = process.argv[3] || 'Exportar_PerdidosAchados.zip';

const NOME = 'Exportar Perdidos e Achados';
const FLOW_ID = '7c2d5b91-48af-4e06-b3d7-1f90ac62e845';
const TELEMETRIA = 'd9a3f618-25c7-4b0e-8f42-6ab017c35d9e';

// Constantes do ambiente, iguais as do pacote do Mapa: mesmo tenant, mesmo
// conector. Na importacao o Power Automate pede para escolher a conexao de
// qualquer forma, entao o CONN_ID serve so de sugestao.
// ASSET_ID e a pasta dentro do pacote; FLOW_ID e o id do fluxo em si. No
// List_Generator_v2.zip os dois sao diferentes, e foi so copiando esse pacote
// inteiro que a importacao parou de pedir "salve como novo fluxo primeiro".
const ASSET_ID = '2a6f41c8-93be-4d57-8e10-5b7c2fa09d34';
const API_ID = '1821735d-649e-4ffe-933f-35a1c1e32c2a';
const CONN_ID = '822f4c97-d670-4aa7-baf5-c0129e3ecf71';
// nome da conexao do SharePoint neste tenant — vai em connectionReferences
const CONN_NAME = 'shared-sharepointonl-0cd12861-383f-4b6e-9359-db983fb70160';
const ICON = 'https://static.powerapps.com/resource/ppcr/releases/v1.0.1827/1.0.1827.4913/sharepointonline/icon.png';

const bruto = JSON.parse(fs.readFileSync(ENTRADA, 'utf8'));
const definition = bruto.properties ? bruto.properties.definition : (bruto.definition || bruto);
if (!definition || !definition.actions) throw new Error('definicao sem actions: ' + ENTRADA);

const resources = {};
resources[ASSET_ID] = {
  type: 'Microsoft.Flow/flows',
  suggestedCreationType: 'New',
  creationType: 'Existing, New, Update',
  details: { displayName: NOME },
  configurableBy: 'User',
  hierarchy: 'Root',
  dependsOn: [API_ID, CONN_ID],
};
resources[API_ID] = {
  id: '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
  name: 'shared_sharepointonline',
  type: 'Microsoft.PowerApps/apis',
  suggestedCreationType: 'Existing',
  details: { displayName: 'SharePoint', iconUri: ICON },
  configurableBy: 'System',
  hierarchy: 'Child',
  dependsOn: [],
};
resources[CONN_ID] = {
  type: 'Microsoft.PowerApps/apis/connections',
  suggestedCreationType: 'Existing',
  creationType: 'Existing',
  details: { displayName: 'SharePoint (conexao existente)', iconUri: ICON },
  configurableBy: 'User',
  hierarchy: 'Child',
  dependsOn: [API_ID],
};

const manifest = {
  schema: '1.0',
  details: {
    displayName: NOME,
    description: '',
    createdTime: new Date().toISOString(),
    packageTelemetryId: TELEMETRIA,
    creator: 'N/A',
    sourceEnvironment: '',
  },
  resources,
};

// Mesma forma do definition.json do List_Generator_v2.zip. Sem o apiId e sem o
// connectionReferences a importacao falha com "save it as a new flow first".
const flowAsset = () => ({
  name: FLOW_ID,
  id: '/providers/Microsoft.Flow/flows/' + FLOW_ID,
  type: 'Microsoft.Flow/flows',
  properties: {
    apiId: '/providers/Microsoft.PowerApps/apis/shared_logicflows',
    displayName: NOME,
    definition,
    connectionReferences: {
      shared_sharepointonline: {
        connectionName: CONN_NAME,
        source: 'Invoker',
        id: '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
        tier: 'NotSpecified',
        apiName: 'sharepointonline',
        isProcessSimpleApiReferenceConversionAlreadyDone: false,
      },
    },
    flowFailureAlertSubscribed: false,
    isManaged: false,
  },
});

const entradas = [
  ['Microsoft.Flow/flows/' + ASSET_ID + '/apisMap.json', JSON.stringify({ shared_sharepointonline: API_ID })],
  ['Microsoft.Flow/flows/' + ASSET_ID + '/connectionsMap.json', JSON.stringify({ shared_sharepointonline: CONN_ID })],
  ['Microsoft.Flow/flows/' + ASSET_ID + '/definition.json', JSON.stringify(flowAsset())],
  ['Microsoft.Flow/flows/manifest.json', JSON.stringify({ packageSchemaVersion: '1.0', flowAssets: { assetPaths: [ASSET_ID] } })],
  ['manifest.json', JSON.stringify(manifest)],
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
  const dados = Buffer.from(par[1], 'utf8');
  const comp = zlib.deflateRawSync(dados, { level: 9 });
  const nb = Buffer.from(par[0], 'utf8');
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

fs.writeFileSync(SAIDA, Buffer.concat([corpo, central, fim]));
console.log('zip gerado: ' + SAIDA + ', ' + fs.statSync(SAIDA).size + ' bytes, ' + entradas.length + ' entradas');
