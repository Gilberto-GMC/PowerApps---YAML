#!/usr/bin/env python3
"""Valida os artefatos de implantação DD01/DD02/DD02P sem acessar produção."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

from build_fluxos_resilientes import (
    BASE, CAPTURE_NEW_OUTPUT, CAPTURE_OUTPUT, FORM_ID, MANUAL_OUTPUT,
    MONITOR_OUTPUT, PROCESS_SOURCE, SEND_OUTPUT, SEND_SOURCE,
    WORKER_OUTPUT,
)


def fail(message: str) -> None:
    raise AssertionError(message)


def read_flow(path: Path) -> tuple[dict, dict]:
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, f"ZIP corrompido: {path.name}"
        names = [name for name in archive.namelist() if name.endswith('/definition.json')]
        assert len(names) == 1, f"definition.json ausente/duplicado: {path.name}"
        package = json.loads(archive.read(names[0]))
        manifest = json.loads(archive.read('manifest.json'))
    return package, manifest


def all_actions(actions: dict, errors: list[str], path: str = "") -> list[str]:
    names = []
    for name, action in actions.items():
        names.append(name)
        for dependency in action.get('runAfter', {}):
            if dependency not in actions:
                errors.append(f"{path}/{name}: runAfter aponta a irmão inexistente {dependency}")
        all_actions(action.get('actions', {}), errors, path + '/' + name)
        all_actions(action.get('else', {}).get('actions', {}), errors, path + '/' + name + '/else')
        for case_name, case in action.get('cases', {}).items():
            all_actions(case.get('actions', {}), errors, path + '/' + name + '/' + case_name)
    return names


def collect_names(actions: dict) -> list[str]:
    names = []
    def visit(items):
        for name, action in items.items():
            names.append(name)
            visit(action.get('actions', {}))
            visit(action.get('else', {}).get('actions', {}))
            for case in action.get('cases', {}).values():
                visit(case.get('actions', {}))
    visit(actions)
    return names


def check_workflow(name: str, workflow: dict, errors: list[str]) -> None:
    actions = workflow['actions']
    all_actions(actions, errors)
    names = collect_names(actions)
    duplicates = sorted(k for k, count in Counter(names).items() if count > 1)
    if duplicates:
        errors.append(f"{name}: nomes de ação duplicados: {duplicates}")
    raw = json.dumps(workflow, ensure_ascii=False)
    for ref in sorted(set(re.findall(r"(?:body|outputs|items)\('([^']+)'\)", raw))):
        if ref not in names:
            errors.append(f"{name}: referência a ação ausente: {ref}")
    if 'PREENCHER_' in raw:
        errors.append(f"{name}: placeholder não preenchido")
    def check_expressions(value, location=''):
        if isinstance(value, dict):
            for key, child in value.items():
                check_expressions(child, location + '/' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check_expressions(child, location + '/' + str(index))
        elif isinstance(value, str) and value.startswith('@') and not value.startswith('@{'):
            depth, quoted, index = 0, False, 1
            while index < len(value):
                char = value[index]
                if char == "'":
                    if quoted and index + 1 < len(value) and value[index + 1] == "'":
                        index += 2
                        continue
                    quoted = not quoted
                elif not quoted:
                    if char == '(':
                        depth += 1
                    elif char == ')':
                        depth -= 1
                    if depth < 0:
                        break
                index += 1
            if depth != 0 or quoted:
                errors.append(f'{name}{location}: expressão WDL com parênteses/aspas desequilibrados')
    check_expressions(workflow)


def action(actions: dict, target: str) -> dict:
    for name, value in actions.items():
        if name == target:
            return value
        for nested in (value.get('actions', {}), value.get('else', {}).get('actions', {})):
            try:
                return action(nested, target)
            except KeyError:
                pass
    raise KeyError(target)


def check_schema(path: Path, required: set[str], errors: list[str]) -> None:
    schema = json.loads(path.read_text(encoding='utf-8'))
    cols = {entry['internalName']: entry['schemaXml'] for entry in schema['colunas']}
    if not required <= set(cols):
        errors.append(f"{path.name}: campos ausentes {sorted(required - set(cols))}")
    if len(cols) != len(schema['colunas']):
        errors.append(f"{path.name}: nome interno repetido")
    for name, xml in cols.items():
        field = ElementTree.fromstring(xml)
        if field.attrib.get('Name') != name or field.attrib.get('StaticName') != name:
            errors.append(f"{path.name}: Name/StaticName divergente para {name}")
        legacy_names = {'gatilho_representacao_orgao_publico', 'gatilho_indicado_funcionario_publico'}
        if len(name) > 32 and not (path.name == 'listgen_tb_dueDiligence_completo.json' and name in legacy_names):
            errors.append(f"{path.name}: nome interno excede 32 caracteres: {name}")
    for key in ('envio_id', 'forms_chave'):
        if key in cols and "EnforceUniqueValues='TRUE'" not in cols[key]:
            errors.append(f"{path.name}: {key} precisa ser único")


def main() -> int:
    errors: list[str] = []
    flows = {}
    for label, path in (
        ('DD01', SEND_OUTPUT), ('DD02_CAPTURE', CAPTURE_OUTPUT),
        ('DD02N', CAPTURE_NEW_OUTPUT), ('DD02M', MANUAL_OUTPUT),
        ('DD02P', WORKER_OUTPUT), ('DD06', MONITOR_OUTPUT),
    ):
        package, manifest = read_flow(path)
        workflow = package['properties']['definition']
        check_workflow(label, workflow, errors)
        if package['properties'].get('flowFailureAlertSubscribed') is not True:
            errors.append(f'{label}: alerta de falha não solicitado no pacote')
        flows[label] = (package, workflow, manifest)
    send = flows['DD01'][1]
    capture = flows['DD02_CAPTURE'][1]
    manual = flows['DD02M'][1]
    worker = flows['DD02P'][1]
    monitor = flows['DD06'][1]
    original_send, _ = read_flow(SEND_SOURCE)
    original_process, _ = read_flow(PROCESS_SOURCE)
    if flows['DD01'][0]['name'] != original_send['name']:
        errors.append('DD01: Update perdeu o ID do fluxo ativo')
    if flows['DD02_CAPTURE'][0]['name'] != original_process['name']:
        errors.append('DD02 captura: Update perdeu o ID do fluxo ativo')
    if flows['DD02P'][0]['name'] == original_process['name']:
        errors.append('DD02P: novo processador reutiliza o ID do DD02')
    if flows['DD02M'][0]['name'] == original_process['name']:
        errors.append('DD02M: captura manual reutiliza o ID do DD02')
    if flows['DD02N'][0]['name'] == original_process['name']:
        errors.append('DD02N: captura alternativa reutiliza o ID do DD02')
    send_steps = send['actions']['ESCOPO_Processar_Envio']['actions']['Condicao_Item_Valido']['actions']
    if send_steps['Enviar_Email_V2']['runAfter'] != {'HTTP_Registrar_Envio_Preparado': ['Succeeded']}:
        errors.append('DD01: e-mail não depende do registro de convite')
    if send_steps['Montar_Atualizacao_Envio']['runAfter'] != {'HTTP_Marcar_Envio_Aceito': ['Succeeded']}:
        errors.append('DD01: item marcado enviado antes do convite Aceito')
    if send_steps['Envio_Concluido']['runAfter'] != {'HTTP_Registrar_Historico_Envio': ['Succeeded']}:
        errors.append('DD01: falha de histórico tratada como conclusão')
    if not all(k in send_steps['Montar_Historico_Envio']['inputs'] for k in ('forms_envio_id','email_envio','forms_evento_chave')):
        errors.append('DD01: histórico não traz campos estruturados')
    if 'destinatario_versao_id' not in send_steps['Montar_Registro_Envio']['inputs']:
        errors.append('DD01: convite sem versão do destinatário')
    if 'forms_destinatario_versao_id' not in action(send['actions'], 'HTTP_Obter_Item_Atual')['inputs']['parameters']['parameters/uri']:
        errors.append('DD01: $select não lê a versão do destinatário')
    form_capture = capture['triggers']['When_a_new_response_is_submitted']
    if form_capture['inputs']['parameters']['form_id'] != FORM_ID:
        errors.append('DD02 captura: Form ID incorreto')
    if 'concurrency' in form_capture.get('runtimeConfiguration', {}):
        errors.append('DD02 captura: concorrência do gatilho ainda ligada')
    if capture['actions']['Obter_detalhes_da_resposta']['inputs']['parameters']['form_id'] != FORM_ID:
        errors.append('DD02 captura: Get response details usa outro formulário')
    if 'conteudo_json' not in action(capture['actions'], 'Montar_Entrada')['inputs']:
        errors.append('DD02 captura: não salva snapshot da resposta')
    if manual['triggers']['manual'].get('kind') != 'Button' or manual['triggers']['manual']['inputs']['schema'].get('required') != ['number']:
        errors.append('DD02M: botão não exige Response ID numérico')
    if "triggerOutputs()?['body/resourceData/responseId']" in json.dumps(manual):
        errors.append('DD02M: captura manual ainda depende do webhook')
    if set(worker['triggers']) != {'Recorrencia_Processamento'}:
        errors.append('DD02P: gatilho não é a recorrência exclusiva')
    if set(monitor['triggers']) != {'Recorrencia_Monitoramento'}:
        errors.append('DD06: monitor não usa recorrência')
    if action(monitor['actions'], 'Falha_Pendencias')['inputs'].get('runStatus') != 'Failed':
        errors.append('DD06: pendência não produz falha visível')
    if 'HTTP_Buscar_Solicitacao_Sem_Envio' not in monitor['actions']:
        errors.append('DD06: não detecta intenção DD01 sem disparo')
    raw_worker = json.dumps(worker, ensure_ascii=False)
    if "triggerOutputs()?['body/resourceData/responseId']" in raw_worker:
        errors.append('DD02P: ainda depende do gatilho Forms antigo')
    if "items('Para_Cada_Validacao')" not in raw_worker:
        errors.append('DD02P: pré-validação não lê a pergunta corrente')
    if "destinatario_versao_id" not in json.dumps(action(worker['actions'], 'Condicao_Resposta_Valida'), ensure_ascii=False):
        errors.append('DD02P: não impede ressurgimento de link após troca de destinatário')
    if 'forms_destinatario_versao_id' not in action(worker['actions'], 'HTTP_Obter_Solicitacao')['inputs']['parameters']['parameters/uri']:
        errors.append('DD02P: $select do pai não lê versão do destinatário')
    if 'HTTP_Atualizar_Item_Resposta' in raw_worker:
        errors.append('DD02P: uma retomada não pode sobrescrever linha de resposta existente')
    if 'Condicao_Item_Existente_Identico' not in raw_worker:
        errors.append('DD02P: não compara linha já gravada ao snapshot')
    if "forms_resposta_envio_id" not in action(worker['actions'], 'Montar_Atualizacao_Solicitacao')['inputs']:
        errors.append('DD02P: não separa o envio usado do último convite')
    parent_update = action(worker['actions'], 'HTTP_Atualizar_Solicitacao')
    if parent_update['inputs']['parameters']['parameters/headers'].get('IF-MATCH') != "@body('HTTP_Reler_Solicitacao')?['d']?['__metadata']?['etag']":
        errors.append('DD02P: atualização do pai não usa ETag')
    if action(worker['actions'], 'Resposta_Processada')['runAfter'] != {'HTTP_Marcar_Inbox_Processado': ['Succeeded']}:
        errors.append('DD02P: confirmação independe da Inbox')
    if 'Montar_Tentativa' not in action(worker['actions'], 'Condicao_Tem_Pendente')['actions']:
        errors.append('DD02P: faltou limite de tentativas')
    for label in ('DD01', 'DD02_CAPTURE'):
        roots = [v for v in flows[label][2]['resources'].values() if v.get('type') == 'Microsoft.Flow/flows']
        if len(roots) != 1 or roots[0].get('suggestedCreationType') != 'Update':
            errors.append(f'{label}: pacote não indica Update')
    for label in ('DD02P', 'DD02M', 'DD02N', 'DD06'):
        roots = [v for v in flows[label][2]['resources'].values() if v.get('type') == 'Microsoft.Flow/flows']
        if len(roots) != 1 or roots[0].get('suggestedCreationType') != 'New':
            errors.append(f'{label}: pacote não indica Criar como novo')
    check_schema(BASE/'listgen_tb_dueDiligenceEnvios.json',
                 {'envio_id','solicitacao_id','forms_formulario_id','email_envio','destinatario_versao_id','estado_envio','criado_em','aceito_em'}, errors)
    check_schema(BASE/'listgen_tb_dueDiligenceRespostasInbox.json',
                 {'forms_chave','forms_formulario_id','forms_resposta_id','codigo_acompanhamento','conteudo_json','capturado_em','estado','tentativas'}, errors)
    check_schema(BASE/'listgen_tb_dueDiligenceDesdobramentos_completo.json',
                 {'forms_envio_id','email_envio','forms_evento_chave'}, errors)
    check_schema(BASE/'listgen_tb_dueDiligence_completo.json',
                 {'forms_envio_id','forms_ultima_resposta_id','forms_resposta_envio_id','forms_destinatario_versao_id'}, errors)
    screen = (BASE/'ScreenDueDiligence.yaml').read_text(encoding='utf-8')
    if screen.count('forms_resposta_id = varRegistroDueDiligence.forms_ultima_resposta_id') != 2:
        errors.append('App: filtros da resposta aceita não aparecem nas duas leituras')
    if screen.count('forms_resposta_id = ThisItem.forms_ultima_resposta_id') != 1:
        errors.append('App: resumo não seleciona a resposta aceita')
    if 'varDdDestinatarioVersaoForm: If(' not in screen or 'forms_destinatario_versao_id_DataCard:' not in screen:
        errors.append('App: troca de destinatário não gera versão nova')
    if errors:
        print('\n'.join(f'FALHA: {item}' for item in errors))
        return 1
    print('OK: 6 ZIPs, dependências de ações, contratos, esquemas e filtros do aplicativo.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
