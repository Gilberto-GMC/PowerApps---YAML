#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera pacotes individuais de importação do Power Automate no formato "pacote
herdado" (Importar > Importar Pacote (Legado)), a partir das definições
corrigidas em REA/MigracaoAIRPORTNOW_src/Workflows (conteúdo do 1.0.0.5).

Estrutura produzida — igual à de um export real do portal:

    manifest.json                                   <- manifesto do pacote
    Microsoft.Flow/flows/manifest.json              <- manifesto dos assets
    Microsoft.Flow/flows/<res>/definition.json
    Microsoft.Flow/flows/<res>/apisMap.json
    Microsoft.Flow/flows/<res>/connectionsMap.json

A versão anterior deste script escrevia só manifest.json + definition.json;
faltando Microsoft.Flow/flows/manifest.json a importação falha com
MissingPackageManifest ("a pasta 'Microsoft.Flow' não contém manifest.json").

Como os fluxos vêm de uma solução, as connection references do Dataverse
(iem_sharedteams_5a6f9 etc.) são convertidas para conexões "Embedded", que é o
que o pacote herdado entende. Na importação o Power Automate pede uma conexão
para cada conector.

Saída: REA/fluxos_individuais/<NomeDoFluxo>.zip
"""
import json, os, re, uuid, zipfile
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'MigracaoAIRPORTNOW_src')
WF = os.path.join(SRC, 'Workflows')
OUT = os.path.join(BASE, 'fluxos_individuais')

API_DISPLAY = {
    'shared_sharepointonline': 'SharePoint',
    'shared_office365': 'Office 365 Outlook',
    'shared_teams': 'Microsoft Teams',
    'shared_office365users': 'Office 365 Users',
    'shared_excelonlinebusiness': 'Excel Online (Business)',
}

FLOWS = [
    dict(json_file='CriarchatdeacionamentosPLEMPRAI-205429A0-97CC-F011-8543-00224835DFFB.json',
         guid='205429a0-97cc-f011-8543-00224835dffb',
         display='Criar chat de acionamentos PLEM/PRAI',
         zip_name='CriarChatAcionamentosPLEMPRAI.zip'),
    dict(json_file='EnviarAcionamentocomOpcao-9FC77DAD-97CC-F011-8543-00224835DFFB.json',
         guid='9fc77dad-97cc-f011-8543-00224835dffb',
         display='Enviar Acionamento com Opcao',
         zip_name='EnviarAcionamentoComOpcao.zip'),
    dict(json_file='Airportnow-notificaodeacionamento-BE8E23BF-34D5-F011-8543-6045BD39D3BC.json',
         guid='be8e23bf-34d5-f011-8543-6045bd39d3bc',
         display='Airport now - notificação de acionamento',
         zip_name='AirportNowNotificacaoDeAcionamento.zip'),
    dict(json_file='EnviarAtividadeparachatteams-5554D88E-97CC-F011-8543-00224835DFFB.json',
         guid='5554d88e-97cc-f011-8543-00224835dffb',
         display='Enviar Atividade para chat teams',
         zip_name='EnviarAtividadeParaChatTeams.zip'),
]

NS = uuid.UUID('7a5c9a10-4b3e-4b6f-9a2d-00ac00000000')


def det_guid(*parts):
    """GUID determinístico (reproduzível entre execuções)."""
    return str(uuid.uuid5(NS, '/'.join(parts)))


def connref_display_names():
    """nome de exibição de cada connection reference, vindo do customizations.xml."""
    with open(os.path.join(SRC, 'customizations.xml'), encoding='utf-8-sig') as f:
        root = ET.fromstring(f.read())
    out = {}
    crs = root.find('connectionreferences')
    for cr in (crs if crs is not None else []):
        out[cr.get('connectionreferencelogicalname')] = cr.findtext('connectionreferencedisplayname')
    return out


CR_NAMES = connref_display_names()


def build_package(flow):
    with open(os.path.join(WF, flow['json_file']), encoding='utf-8') as f:
        src = json.load(f)
    props = src['properties']
    definition = props['definition']
    conn_refs_sol = props.get('connectionReferences', {})

    flow_res = det_guid(flow['guid'], 'flow')

    # ---- conexões: uma por chave usada na definição ("shared_teams-1" conta) ----
    conn_refs, apis_map, conns_map = {}, {}, {}
    resources, depends_on = {}, []
    api_res = {}   # api_name -> resource id (deduplicado)

    for key, ref in conn_refs_sol.items():
        api_name = ref['api']['name']
        api_display = API_DISPLAY.get(api_name, api_name)

        if api_name not in api_res:
            rid = det_guid(flow['guid'], 'api', api_name)
            api_res[api_name] = rid
            resources[rid] = {
                'id': f'/providers/Microsoft.PowerApps/apis/{api_name}',
                'name': api_name,
                'type': 'Microsoft.PowerApps/apis',
                'suggestedCreationType': 'Existing',
                'details': {'displayName': api_display},
                'configurableBy': 'System',
                'hierarchy': 'Child',
                'dependsOn': [],
            }
            depends_on.append(rid)

        # conexão que o usuário vai escolher no wizard de importação
        cid = det_guid(flow['guid'], 'connection', key)
        logical = ref.get('connection', {}).get('connectionReferenceLogicalName', key)
        resources[cid] = {
            'type': 'Microsoft.PowerApps/apis/connections',
            'suggestedCreationType': 'Existing',
            'creationType': 'Existing',
            'details': {'displayName': CR_NAMES.get(logical) or api_display},
            'configurableBy': 'User',
            'hierarchy': 'Child',
            'dependsOn': [api_res[api_name]],
        }
        depends_on.append(cid)

        conn_refs[key] = {
            'connectionName': det_guid(flow['guid'], 'connname', key).replace('-', ''),
            'source': 'Embedded',
            'id': f'/providers/Microsoft.PowerApps/apis/{api_name}',
            'tier': 'NotSpecified',
        }
        apis_map[key] = api_res[api_name]
        conns_map[key] = cid

    # ---- recurso do fluxo: sem "id"/"name", senão o import tenta casar com um
    # fluxo existente no ambiente de destino ----
    # suggestedCreationType 'Update': o wizard já abre em "Atualizar" e deixa
    # escolher o fluxo que existe no ambiente. Isso SUBSTITUI a definição do
    # fluxo mantendo o mesmo ID, então o app continua apontando para ele e nada
    # precisa ser removido/re-adicionado no Studio. Com 'New' (como estava) a
    # importação cria uma CÓPIA com ID novo, e aí o app teria que ser
    # reapontado — que é justamente onde o Studio renomeia para "..._1".
    resources[flow_res] = {
        'type': 'Microsoft.Flow/flows',
        'suggestedCreationType': 'Update',
        'creationType': 'Existing, New, Update',
        'details': {'displayName': flow['display']},
        'configurableBy': 'User',
        'hierarchy': 'Root',
        'dependsOn': depends_on,
    }

    manifest = {
        'schema': '1.0',
        'details': {
            'displayName': flow['display'],
            'description': 'Fluxo do acionamento PLEM/PRAI (versão corrigida — equivalente ao pacote MigracaoAIRPORTNOW 1.0.0.5)',
            'createdTime': '2026-08-13T00:00:00Z',
            'packageTelemetryId': det_guid(flow['guid'], 'telemetry'),
            'creator': 'N/A',
            'sourceEnvironment': '',
        },
        'resources': resources,
    }

    definition_json = {
        'name': flow['guid'],
        'id': f"/providers/Microsoft.Flow/flows/{flow['guid']}",
        'type': 'Microsoft.Flow/flows',
        'properties': {
            'apiId': '/providers/Microsoft.PowerApps/apis/shared_logicflows',
            'displayName': flow['display'],
            'definition': definition,
            'connectionReferences': conn_refs,
            'flowFailureAlertSubscribed': False,
        },
    }

    assets_manifest = {'packageSchemaVersion': '1.0',
                       'flowAssets': {'assetPaths': [flow_res]}}

    os.makedirs(OUT, exist_ok=True)
    zpath = os.path.join(OUT, flow['zip_name'])
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        def write(name, obj):
            info = zipfile.ZipInfo(name, date_time=(2026, 8, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, json.dumps(obj, ensure_ascii=False, indent=2))
        base = f'Microsoft.Flow/flows/{flow_res}'
        write('manifest.json', manifest)
        write('Microsoft.Flow/flows/manifest.json', assets_manifest)
        write(f'{base}/definition.json', definition_json)
        write(f'{base}/apisMap.json', apis_map)
        write(f'{base}/connectionsMap.json', conns_map)
    return zpath, sorted(set(api_res)), len(conns_map)


def main():
    for flow in FLOWS:
        p, apis, nconn = build_package(flow)
        print(f"{flow['display']}\n  {os.path.relpath(p, BASE)} ({os.path.getsize(p)} bytes) "
              f"| {len(apis)} conector(es), {nconn} conexão(ões): {', '.join(apis)}")


if __name__ == '__main__':
    main()
