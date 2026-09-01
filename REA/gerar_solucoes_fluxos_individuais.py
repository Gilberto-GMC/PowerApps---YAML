#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera uma SOLUÇÃO NÃO GERENCIADA por fluxo, a partir de MigracaoAIRPORTNOW_src.

Por que solução e não "pacote herdado" (manifest.json + Microsoft.Flow/):
os 4 fluxos do acionamento PLEM/PRAI são solution-aware — as ações apontam para
connection references do Dataverse (ex.: iem_sharedteams_5a6f9). Pacotes herdados
não suportam connection references (a doc da Microsoft diz explicitamente que
flow packages e solution packages são incompatíveis), por isso o importador
rejeita o zip com MissingPackageManifest.

Saída: REA/solucoes_fluxos/SOLUCAO_<Nome>_1_0_0_0.zip
(só para 'Soluções > Importar' — NÃO serve para 'Importar Pacote (Legado)')
Importar em: make.powerapps.com > Soluções > Importar solução.
"""
import json, os, re, shutil, zipfile
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'MigracaoAIRPORTNOW_src')
OUT = os.path.join(BASE, 'solucoes_fluxos')
VERSION = '1.0.0.0'

# fluxos corrigidos do acionamento PLEM/PRAI
FLOWS = [
    ('205429a0-97cc-f011-8543-00224835dffb', 'CriarChatAcionamentosPLEMPRAI',
     'Fluxo - Criar chat de acionamentos PLEM/PRAI'),
    ('9fc77dad-97cc-f011-8543-00224835dffb', 'EnviarAcionamentoComOpcao',
     'Fluxo - Enviar Acionamento com Opcao'),
    ('be8e23bf-34d5-f011-8543-6045bd39d3bc', 'AirportNowNotificacaoAcionamento',
     'Fluxo - Airport now notificação de acionamento'),
    ('5554d88e-97cc-f011-8543-00224835dffb', 'EnviarAtividadeParaChatTeams',
     'Fluxo - Enviar Atividade para chat teams'),
]


def read(p):
    with open(p, encoding='utf-8-sig') as f:
        return f.read()


def build(flow_id, unique_suffix, display):
    cust = ET.fromstring(read(os.path.join(SRC, 'customizations.xml')))

    # 1) manter só o Workflow do fluxo
    wfs = cust.find('Workflows')
    keep = None
    for wf in list(wfs):
        if wf.get('WorkflowId', '').strip('{}').lower() == flow_id:
            keep = wf
        else:
            wfs.remove(wf)
    if keep is None:
        raise SystemExit(f'Workflow {flow_id} não encontrado em customizations.xml')
    json_rel = keep.findtext('JsonFileName').lstrip('/')

    # 2) manter só as connection references usadas por esse fluxo
    wf_json = json.loads(read(os.path.join(SRC, json_rel)))
    used = {
        ref['connection']['connectionReferenceLogicalName']
        for ref in wf_json['properties'].get('connectionReferences', {}).values()
        if ref.get('connection', {}).get('connectionReferenceLogicalName')
    }
    crs = cust.find('connectionreferences')
    for cr in list(crs):
        if cr.get('connectionreferencelogicalname') not in used:
            crs.remove(cr)

    # 3) solution.xml: nome único, versão, não gerenciada, 1 root component
    sol = ET.fromstring(read(os.path.join(SRC, 'solution.xml')))
    man = sol.find('SolutionManifest')
    unique = f'MigracaoAIRPORTNOWFx{unique_suffix}'
    man.find('UniqueName').text = unique
    for ln in man.find('LocalizedNames'):
        ln.set('description', display)
    man.find('Version').text = VERSION
    man.find('Managed').text = '0'
    roots = man.find('RootComponents')
    for rc in list(roots):
        roots.remove(rc)
    ET.SubElement(roots, 'RootComponent',
                  {'type': '29', 'id': '{%s}' % flow_id, 'behavior': '0'})

    os.makedirs(OUT, exist_ok=True)
    # prefixo SOLUCAO_ no nome do arquivo: estes zips são de SOLUÇÃO e só
    # funcionam em "Soluções > Importar". Subir um deles na tela de "Importar
    # Pacote (Legado)" dá "Something went wrong. Please try again later.",
    # porque o importador herdado procura manifest.json na raiz e aqui há
    # solution.xml. Os nomes eram quase idênticos aos de fluxos_individuais/,
    # o que já causou o engano uma vez.
    zpath = os.path.join(OUT, f"SOLUCAO_{unique_suffix}_{VERSION.replace('.', '_')}.zip")
    head = '<?xml version="1.0" encoding="utf-8"?>\n'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', read(os.path.join(SRC, '[Content_Types].xml')))
        z.writestr('solution.xml', head + ET.tostring(sol, encoding='unicode'))
        z.writestr('customizations.xml', head + ET.tostring(cust, encoding='unicode'))
        z.writestr(json_rel, read(os.path.join(SRC, json_rel)))
    return zpath, unique, sorted(used), json_rel


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    for flow_id, suffix, display in FLOWS:
        zpath, unique, used, json_rel = build(flow_id, suffix, display)
        print(f'{display}\n  zip     : {os.path.relpath(zpath, BASE)} '
              f'({os.path.getsize(zpath)} bytes)\n  solução : {unique} v{VERSION} (não gerenciada)'
              f'\n  connrefs: {", ".join(used)}\n')


if __name__ == '__main__':
    main()
