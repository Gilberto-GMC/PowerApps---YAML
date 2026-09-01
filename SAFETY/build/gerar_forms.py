# -*- coding: utf-8 -*-
"""Escopo de segurança nas telas que já eram únicas (FOD, CSO, Vistoria, Fauna)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
SRC, OUT = "msapp/Src", "out"

# (tela, arquivo de saída, [(coluna, controle, variável de escopo)])
TELAS = [
    ("ScreenFOD", "05_ScreenFOD.pa.yaml",
     [("aeroporto", "ComboboxCanvasAeroporto", "varEscopoAero")]),
    ("ScreenCSO", "06_ScreenCSO.pa.yaml",
     [("Aeroporto", "ComboboxCanvasAeroporto_1", "varEscopoAero")]),
    ("ScreenVistoriaSafetyFauna", "07_ScreenVistoriaSafetyFauna.pa.yaml",
     [("Aeroporto", "ComboboxCanvasAeroporto_5", "varEscopoAero")]),
    ("ScreenFauna", "08_ScreenFauna.pa.yaml",
     [("Aeroporto", "cmbOcoFaunaAeroporto", "varEscopoIATA"),
      ("aceIndFauna_aeroporto", "cmbOcoFaunaAeroporto", "varEscopoAero")]),
]


AVISOS = {
"ScreenVistoriaSafetyFauna": """#
# ⚠️ DEFEITO GRAVE NÃO CORRIGIDO AQUI — PRECISA DA SUA CONFIRMAÇÃO
#
#   A galeria Table1_2 desta tela consulta a lista  '1 - CSO' :
#
#       Items: =Search(Sort(Filter('1 - CSO', StartsWith(Aeroporto, ...), ...
#
#   mas o formulário (Form1_2) grava em  tbl_vistoriaSafetyFauna .
#   Ou seja: a tela lista reuniões de CSO e salva vistorias — o que é gravado
#   nunca aparece na listagem.
#
#   O esquema exportado confirma que as colunas certas existem em
#   tbl_vistoriaSafetyFauna:  Bloco, Aeroporto, Protocolo, Data, TipoVistoria,
#   Quadrante, Local, LocalEspecifico, Area, Descricao, AcalicaoRisco, Acoes,
#   SetorResponsavel, Prioridade, Observacao, foto1, foto2.
#
#   Não troquei a fonte de dados porque isso obriga a reescrever também todos os
#   ThisItem.<coluna> dos filhos da galeria (hoje apontam para colunas de CSO),
#   e o rótulo da linha usa ThisItem.aeroporto em minúsculo, que não existe em
#   nenhuma das duas listas. É uma correção que precisa ser feita olhando a tela
#   montada. Me confirme que quer e eu entrego a galeria reescrita.
#
""",
"ScreenCSO": """#
# ⚠️ DIVERGÊNCIA DE ESQUEMA — VERIFICAR NO SHAREPOINT
#
#   As fórmulas desta tela usam  Aeroporto  e  'Data/Hora'  na lista '1 - CSO',
#   mas o esquema gravado neste export não tem nenhuma das duas: a coluna de
#   data se chama  Data  e não há coluna de aeroporto.
#
#   Duas leituras possíveis: (a) o esquema em cache do .msapp está velho e as
#   colunas foram criadas depois; (b) as fórmulas estão realmente erradas e o
#   filtro de aeroporto/período desta tela nunca funcionou.
#
#   Abra a lista '1 - CSO' no SharePoint e confirme. Se o esquema do export
#   estiver certo, o filtro precisa passar a usar Data — e o escopo de
#   segurança por aeroporto só é possível depois de criar a coluna.
#
""",
}

CAB = '''# ************************************************************************************************
# AirportNow — Safety & Fauna  ·  {tela}
#
# ⚠️ LOCALE — ARQUIVO NO FORMATO INVARIANTE ("," para argumentos, ";" para encadear,
#    "." decimal). É assim que a EXIBIÇÃO DE CÓDIGO do Studio lê e grava, mesmo com o
#    Studio em pt-BR. NÃO converta para ";" / ";;": o arquivo para de compilar.
#    A conversão para pt-BR (";" / ";;" / vírgula decimal) só vale para o que é colado
#    na BARRA DE FÓRMULAS — aqui, nada é.
#
#
# COLAR EM: Studio > tela {tela} > exibição de código > substituir tudo.
#
# ESCOPO DE SEGURANÇA
#   As galerias desta tela filtravam o aeroporto de forma OPCIONAL:
#       IsBlank(combo.Selected.X) || Aeroporto = combo.Selected.X
#   Com o combo em branco a condição é sempre verdadeira e a galeria devolvia
#   TODOS os aeroportos — inclusive para o perfil "Base", que só pode enxergar
#   o próprio. Foi acrescentada uma condição anterior, que não depende de
#   nenhum controle da tela:
#       IsBlank({escopo}) || <coluna> = {escopo}
#   {escopo} é definida no App.OnStart e só tem valor para o perfil Base.
#   O filtro escolhido pelo usuário continua funcionando como antes, agora
#   dentro do que o perfil dele permite ver.
#
#   DELEGAÇÃO: estas condições usam IsBlank(), que o conector do SharePoint não
#   delega — a consulta continua limitada às primeiras 500/2000 linhas, como já
#   era antes desta mudança. As sete telas ScreenMod* receberam a versão
#   delegável (With + Switch); aqui a prioridade foi fechar o acesso sem
#   reescrever a consulta.
# ************************************************************************************************
'''


def aplicar(tela, saida, regras):
    txt = open(f"{SRC}/{tela}.pa.yaml", encoding='utf-8').read()
    corpo = txt[txt.index('Screens:'):]
    total = 0
    escopos = []
    for col, ctrl, esc in regras:
        escopos.append(esc)
        for suf in ('IATA', 'Aeroporto', 'Value'):
            ref = f'{ctrl}.Selected.{suf}'
            pat = re.compile(r'(\n(\s*))IsBlank\(' + re.escape(ref) + r'\) \|\|\n\s*' +
                             re.escape(col) + r' = ' + re.escape(ref) + r',')

            def sub(mt):
                nonlocal total
                total += 1
                pad = mt.group(2)
                return (f"{mt.group(1)}// escopo de segurança — independe do filtro da tela\n{pad}"
                        f"IsBlank({esc}) ||\n{pad}{col} = {esc},\n{pad}"
                        f"IsBlank({ref}) ||\n{pad}{col} = {ref},")

            corpo, n1 = pat.subn(sub, corpo)

        # variante StartsWith(...) usada em CSO e Vistoria: com o combo vazio
        # StartsWith(x, "") é verdadeiro para toda linha — mesmo vazamento.
        for pad_col in (f'Text({col})', col):
            pat = re.compile(r'(\n(\s*))StartsWith\(\s*\n\s*' + re.escape(pad_col) +
                             r',\s*\n\s*Text\(' + re.escape(f'{ctrl}.Selected.Value') + r'\)\s*\n\s*\),')
            def sub(mt):
                nonlocal total
                total += 1
                pad = mt.group(2)
                return (f"{mt.group(1)}// escopo de segurança — independe do filtro da tela\n{pad}"
                        f"IsBlank({esc}) ||\n{pad}{col} = {esc},\n{pad}"
                        f"StartsWith(\n{pad}    {pad_col},\n{pad}    Text({ctrl}.Selected.Value)\n{pad}),")
            corpo, n2 = pat.subn(sub, corpo)
            if n2:
                break

    cab = CAB.format(tela=tela, escopo=' / '.join(dict.fromkeys(escopos)))
    if tela in AVISOS:
        marca = '# ' + '*' * 96 + '\n'
        i = cab.rindex(marca)
        cab = cab[:i] + AVISOS[tela] + cab[i:]
    open(f"{OUT}/{saida}", 'w', encoding='utf-8').write(cab + corpo)
    print(f"{tela:28s} -> out/{saida}  ({total} galerias protegidas)")
    return total


if __name__ == '__main__':
    n = sum(aplicar(*t) for t in TELAS)
    if n == 0:
        sys.exit("nenhuma galeria alterada — padrão não encontrado")
