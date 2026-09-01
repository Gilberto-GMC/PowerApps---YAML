#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reempacota a solução MigracaoAIRPORTNOW a partir de MigracaoAIRPORTNOW_src,
subindo a versão. Saída: REA/MigracaoAIRPORTNOW_1_0_0_6_managed.zip

Por que este caminho e não os pacotes individuais:

  Os zips de `fluxos_individuais/` importam os fluxos como fluxos NOVOS, com
  IDs novos. O app continua chamando os antigos, então seria preciso remover e
  re-adicionar os 3 fluxos no Power Apps Studio — e é exatamente aí que o
  Studio renomeia para "EnviarAtividadeparachatteams_1" e o YAML colado deixa
  de encontrar a referência.

  Aqui os WorkflowId do customizations.xml são os MESMOS do 1.0.0.5, e a
  versão sobe 1.0.0.5 -> 1.0.0.6. O Power Platform trata como ATUALIZAÇÃO da
  solução gerenciada já instalada: as definições dos fluxos são substituídas
  no lugar, os IDs não mudam, as connection references continuam ligadas e o
  app não precisa de nenhum ajuste.

Estrutura idêntica à do export original (14 arquivos):

    [Content_Types].xml
    solution.xml
    customizations.xml
    Workflows/<NomeDoFluxo>-<GUID>.json      x 11
"""
import os
import re
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'MigracaoAIRPORTNOW_src')
WF = os.path.join(SRC, 'Workflows')

VERSAO_ANTERIOR = '1.0.0.5'
VERSAO = '1.0.0.6'
OUT = os.path.join(HERE, 'MigracaoAIRPORTNOW_%s_managed.zip' % VERSAO.replace('.', '_'))
REFERENCIA = os.path.join(HERE, 'MigracaoAIRPORTNOW_%s_managed.zip'
                          % VERSAO_ANTERIOR.replace('.', '_'))

# fluxos tocados por refatorar_fluxos_teams.py
REFATORADOS = ('EnviarAtividadeparachatteams', 'EnviarAcionamentocomOpcao',
               'CriarchatdeacionamentosPLEMPRAI')


def die(msg):
    raise SystemExit('ERRO: %s' % msg)


def ler(nome):
    """Binário de propósito: o export original vem com CRLF e BOM, e o pacote
    tem que sair byte a byte igual nos arquivos que não foram alterados."""
    with open(os.path.join(SRC, nome), 'rb') as f:
        return f.read()


def main():
    solution = ler('solution.xml')
    tag_antes = ('<Version>%s</Version>' % VERSAO_ANTERIOR).encode('utf-8')
    tag_nova = ('<Version>%s</Version>' % VERSAO).encode('utf-8')
    if solution.count(tag_antes) != 1:
        die('solution.xml não está em %s — confira antes de subir a versão'
            % VERSAO_ANTERIOR)
    if b'<Managed>1</Managed>' not in solution:
        die('solution.xml não está marcado como gerenciado')
    solution = solution.replace(tag_antes, tag_nova)

    customizations = ler('customizations.xml')

    # os arquivos de fluxo têm que ser exatamente os que o customizations cita
    citados = re.findall(r'<JsonFileName>/Workflows/([^<]+)</JsonFileName>',
                         customizations.decode('utf-8-sig'))
    presentes = sorted(f for f in os.listdir(WF) if f.endswith('.json'))
    faltando = [c for c in citados if c not in presentes]
    sobrando = [p for p in presentes if p not in citados]
    if faltando:
        die('customizations.xml cita fluxo que não existe: %s' % faltando)
    if sobrando:
        die('Workflows/ tem arquivo não citado no customizations.xml: %s' % sobrando)

    # os GUIDs precisam bater com os do pacote anterior, senão vira fluxo novo
    if os.path.exists(REFERENCIA):
        with zipfile.ZipFile(REFERENCIA) as z:
            antes = sorted(n.split('/', 1)[1] for n in z.namelist()
                           if n.startswith('Workflows/'))
        if antes != sorted(citados):
            die('a lista de fluxos mudou em relação a %s — a atualização '
                'no lugar depende dos mesmos GUIDs.\n  antes: %s\n  agora: %s'
                % (os.path.basename(REFERENCIA), antes, sorted(citados)))

    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        def escreve(nome, conteudo):
            info = zipfile.ZipInfo(nome, date_time=(2026, 8, 24, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, conteudo)

        escreve('[Content_Types].xml', ler('[Content_Types].xml'))
        escreve('solution.xml', solution)
        escreve('customizations.xml', customizations)
        for nome in citados:
            with open(os.path.join(WF, nome), 'rb') as f:
                escreve('Workflows/' + nome, f.read())

    print('%s (%d bytes)' % (os.path.relpath(OUT, HERE), os.path.getsize(OUT)))
    print('  versão   : %s -> %s (gerenciada, atualização no lugar)'
          % (VERSAO_ANTERIOR, VERSAO))
    print('  fluxos   : %d, mesmos WorkflowId do pacote anterior' % len(citados))
    print('  alterados: %s' % ', '.join(REFATORADOS))


if __name__ == '__main__':
    main()
