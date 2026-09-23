# -*- coding: utf-8 -*-
"""Telas de apoio: ScreenExcluir e ScreenAnaliseSafety."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from pautil import HDR, limpar_redirect
from modulos import MODULOS

SRC, OUT = "msapp/Src", "out"
NOVA = {m['lista']: m['nova'] for m in MODULOS}
BRANCH = {
    "Colisão de veículos":     "colVei",
    "Derramamento de fluídos": "derFlu",
    "Excursão de pista":       "excPista",
    "Incursão em pista":       "incPista",
    "Interferência externa":   "intExt",
    "Jet blast":               "jetBlast",
    "Ocorrência de solo":      "ocoSolo",
}

CAB_EXCLUIR = '''# ************************************************************************************************
# AirportNow — Safety & Fauna  ·  ScreenExcluir  (corrigida)
#
# ⚠️ LOCALE — ARQUIVO NO FORMATO INVARIANTE ("," para argumentos, ";" para encadear,
#    "." decimal). É assim que a EXIBIÇÃO DE CÓDIGO do Studio lê e grava, mesmo com o
#    Studio em pt-BR. NÃO converta para ";" / ";;": o arquivo para de compilar.
#    A conversão para pt-BR (";" / ";;" / vírgula decimal) só vale para o que é colado
#    na BARRA DE FÓRMULAS — aqui, nada é.
#
#
# COLAR EM: Studio > tela ScreenExcluir > exibição de código > substituir tudo.
#
# CORREÇÕES APLICADAS
#
# 1. BUG DE CÓPIA — ramo "Colisão de veículos"
#    Os filhos eram apagados por  colVeiEnv_idOcorrencia = var_item.derFlu_id
#    e  colVeiImg_idOcorrencia = var_item.derFlu_id.  A coluna "derFlu_id" não
#    existe na lista de Colisão de Veículos, então a comparação era sempre com
#    branco: envolvidos, imagens e desdobramentos NUNCA eram apagados. Toda
#    exclusão de colisão deixava lixo nas listas filhas.
#
# 2. CHAVE ERRADA NOS FILHOS — todos os ramos
#    Os filhos eram apagados comparando com  var_item.ID  (o ID interno do
#    SharePoint), mas os formulários sempre gravaram os filhos com a coluna
#    <modulo>_id (que era calculada como "maior + 1" no app). Os dois números
#    só coincidem enquanto nada é excluído da lista pai — depois da primeira
#    exclusão eles divergem e a exclusão passa a apagar os filhos da ocorrência
#    ERRADA, ou nenhum. Agora a comparação usa a mesma coluna que a gravação usa.
#
# 3. NAVEGAÇÃO
#    Volta para as telas consolidadas (ScreenMod*).
#
# OBSERVAÇÃO SOBRE DADOS ANTIGOS
#    Depois desta correção, <modulo>_id passa a ser igual ao ID do SharePoint
#    nos registros NOVOS. Os registros antigos mantêm o valor sequencial antigo
#    — e é justamente por isso que a exclusão tem de comparar por <modulo>_id:
#    é a única chave que vale para os dois conjuntos.
#
# 4. TIPO AMBÍGUO DE "var_item" (achado no Verificador de aplicativo, 2026-09-22)
#    var_item vinha de {var_item: ThisItem} — só que cada um dos módulos que
#    navega pra cá manda o ThisItem de uma tabela do SharePoint diferente, e os
#    dois botões extras (Fauna, Desdobramentos) mandam mais duas. O Studio via
#    ISSO como uma variável só, de tipo "união" das ~9 tabelas — e reprovava
#    Clear/leitura de campo específico de módulo em cascata (30 erros).
#    var_item só era lido de duas formas (var_item.ID e var_item.<modulo>_id,
#    nunca o registro inteiro), então em vez do registro passou-se a mandar só
#    os dois números já prontos, mesmo tipo (numérico) nos 9 pontos de origem:
#        var_item_id:    ThisItem.ID            (era var_item.ID)
#        var_item_chave: ThisItem.<modulo>_id   (era var_item.<modulo>_id, só
#                                                 nos 7 módulos com filhos)
#    Esta função (corrigir_excluir) já escreve esses dois nomes; quem manda os
#    valores são os próprios botões "Excluir" (7 módulos + Fauna + Desdobra-
#    mentos, em msapp/Src) — corrigidos junto, fora deste script.
# ************************************************************************************************
'''


def corrigir_excluir():
    txt = open(f"{SRC}/ScreenExcluir.pa.yaml", encoding='utf-8').read()
    corpo = txt.split('# ' + '*' * 96 + '\n', 1)[-1]
    if corpo.startswith('#'):
        corpo = txt[txt.index('Screens:'):]
    else:
        corpo = txt[txt.index('Screens:'):]

    # 1. bug de cópia — já sai direto no nome final (var_item_chave), não em
    #    "var_item.colVei_id": o botão Excluir de cada módulo agora manda
    #    var_item_chave pronto (ThisItem.<modulo>_id), então não tem mais
    #    sentido reescrever pra um campo de registro que não existe mais.
    n1 = corpo.count('var_item.derFlu_id')
    corpo = corpo.replace('var_item.derFlu_id', 'var_item_chave')

    # 2. chave dos filhos, ramo a ramo
    # "Fauna" entra como marca-limite: aquele ramo usa as listas do site de
    # Inteligência Safety, cuja chave é o próprio ID do SharePoint — não deve
    # ser reescrito. Sem esta marca, o ramo de Ocorrência de Solo se estenderia
    # até o fim do arquivo e engoliria o ramo de Fauna.
    marcas = [(corpo.index(f'"{nome}",'), nome) for nome in list(BRANCH) + ['Fauna']
              if f'"{nome}",' in corpo]
    marcas.sort()
    n2 = 0
    saida, fim_ant = [], 0
    for idx, (pos, nome) in enumerate(marcas):
        prox = marcas[idx + 1][0] if idx + 1 < len(marcas) else len(corpo)
        saida.append(corpo[fim_ant:pos])
        trecho = corpo[pos:prox]
        pfx = BRANCH.get(nome)
        if pfx is None:
            saida.append(trecho)
            fim_ant = prox
            continue
        # só nas RemoveIf de filhos; a verificação final por ID vira var_item_id
        # embaixo (passo 2.5), igual nos ramos que não entram aqui.
        def troca(m):
            nonlocal n2
            n2 += 1
            return m.group(1) + 'var_item_chave'
        trecho = re.sub(r'(RemoveIf\((?:[^()]|\([^()]*\))*?=\s*)var_item\.ID', troca, trecho)
        saida.append(trecho)
        fim_ant = prox
    saida.append(corpo[fim_ant:])
    corpo = ''.join(saida)

    # 2.5 tipo homogêneo (item 4 do cabeçalho) — o resto de "var_item.ID" (a
    #     verificação final por ID em todo ramo, e os ramos Fauna/Desdobramentos
    #     inteiros, cuja chave já É o ID do SharePoint) vira var_item_id. Depois
    #     desta troca não pode sobrar nenhum "var_item." no arquivo — os únicos
    #     dois nomes usados são var_item_id e var_item_chave.
    n_id = corpo.count('var_item.ID')
    corpo = corpo.replace('var_item.ID', 'var_item_id')
    sobrou = re.findall(r'var_item\.\w+', corpo)
    if sobrou:
        raise SystemExit(f"ScreenExcluir: sobrou referencia var_item.* nao mapeada: {set(sobrou)}")

    # 3. navegação para as telas consolidadas
    n3 = 0
    for antiga, nova in NOVA.items():
        for chave in ('var_navigateSucess', 'var_navigateErro'):
            alvo = f'{chave}: {antiga}'
            n3 += corpo.count(alvo)
            corpo = corpo.replace(alvo, f'{chave}: {nova}')

    open(f"{OUT}/03_ScreenExcluir.pa.yaml", 'w', encoding='utf-8', newline='\n').write(CAB_EXCLUIR + corpo)
    print(f"ScreenExcluir  -> out/03_ScreenExcluir.pa.yaml")
    print(f"   {n1} refs 'derFlu_id' corrigidas no ramo de Colisão (-> var_item_chave)")
    print(f"   {n2} RemoveIf de filhos passaram a usar var_item_chave")
    print(f"   {n_id} demais 'var_item.ID' viraram var_item_id (tipo homogêneo, ver item 4 do cabeçalho)")
    print(f"   {n3} navegações apontadas para as telas consolidadas")


def corrigir_analise():
    txt = open(f"{SRC}/ScreenAnaliseSafety.pa.yaml", encoding='utf-8').read()
    corpo = txt[txt.index('Screens:'):]
    n = 0
    for antiga, nova in NOVA.items():
        for m in re.finditer(r'(?<![A-Za-z])' + antiga + r'(?![A-Za-z_])', corpo):
            n += 1
        corpo = re.sub(r'(?<![A-Za-z])' + antiga + r'(?![A-Za-z_])', nova, corpo)
    corpo, nred = limpar_redirect(corpo)
    cab = ('# ' + '*' * 96 + '\n'
           '# AirportNow — Safety & Fauna  ·  ScreenAnaliseSafety (navegação atualizada)\n'
           '#\n' 
           '# ⚠️ LOCALE — ARQUIVO NO FORMATO INVARIANTE ("," para argumentos, ";" para encadear,\n' 
           '#    "." decimal). É assim que a EXIBIÇÃO DE CÓDIGO do Studio lê e grava, mesmo com o\n' 
           '#    Studio em pt-BR. NÃO converta para ";" / ";;": o arquivo para de compilar.\n' 
           '#    A conversão para pt-BR (";" / ";;" / vírgula decimal) só vale para o que é colado\n' 
           '#    na BARRA DE FÓRMULAS — aqui, nada é.\n' 
           '#\n'
           '#\n'
           '# COLAR EM: Studio > tela ScreenAnaliseSafety > exibição de código.\n'
           '# Duas mudanças, nenhuma de layout ou de regra:\n'
           '#   1. Os destinos de Navigate passam a ser as telas consolidadas (ScreenMod*).\n'
           '#   2. Sair para frmHome limpa var_redirectAN. frmHome.OnVisible redireciona\n'
           '#      de volta enquanto essa variável tiver valor, e Param() a mantém pela\n'
           '#      sessão inteira: sem limpar, quem abriu o app por deep link não\n'
           '#      conseguia voltar para a home.\n'
           '# ' + '*' * 96 + '\n')
    open(f"{OUT}/04_ScreenAnaliseSafety.pa.yaml", 'w', encoding='utf-8', newline='\n').write(cab + corpo)
    print(f"ScreenAnaliseSafety -> out/04_ScreenAnaliseSafety.pa.yaml  ({n} referências atualizadas, "
          f"{nred} saídas limpando var_redirectAN)")


if __name__ == '__main__':
    corrigir_excluir()
    corrigir_analise()
