# -*- coding: utf-8 -*-
"""Gera out/90_scrSondaOffline.pa.yaml: uma tela para colar numa CÓPIA do app
mobile de Pista e provar, no tablet, o que o motor offline precisa antes de ser
gerado (sondas S2, S3, S4, S6, S13, S16 e S17 de build/sondas_offline.md do
projeto principal e da auditoria do mobile).

Só usa tipos de controle e propriedades que existem no export deste app
(build/propdict.json). Acrescenta as exceções "surgem" em out/_excecoes_layout.json
para a trava de layout (tela nova)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Inspeções', 'build'))
from pautil import HDR

TELA = 'scrSondaOffline'
CINZA = 'RGBA(51, 51, 51, 1)'
ROXO = 'RGBA(96, 70, 237, 1)'
BRANCO = 'RGBA(255, 255, 255, 1)'


def prop(nome, valor, ind):
    """propriedade YAML: linha única se couber, senão bloco literal |-"""
    pad = ' ' * ind
    if '\n' in valor or ': ' in valor or ' #' in valor:
        linhas = [f"{pad}{nome}: |-"] + [(pad + '  ' + l) if l.strip() else '' for l in valor.split('\n')]
        return '\n'.join(linhas)
    return f"{pad}{nome}: {valor}"


def controle(nome, tipo, props):
    out = [f"      - {nome}:", f"          Control: {tipo}", "          Properties:"]
    for k in sorted(props, key=str.lower):
        out.append(prop(k, props[k], 12))
    return '\n'.join(out)


def rotulo(nome, texto, x, y, w, h, size=11, bold=False):
    p = {'Color': f'={CINZA}', 'Height': f'={h}', 'Size': f'={size}', 'Text': texto, 'Width': f'={w}',
         'Wrap': '=true', 'X': f'={x}', 'Y': f'={y}', 'VerticalAlign': '=VerticalAlign.Top'}
    if bold:
        p['FontWeight'] = '=FontWeight.Bold'
    return controle(nome, 'Label@2.5.1', p)


def botao(nome, texto, onselect, x, y, w=250, h=50, visivel='=true', modo='=DisplayMode.Edit'):
    return controle(nome, 'Classic/Button@2.2.0', {
        'Color': f'={BRANCO}', 'DisplayMode': modo, 'Fill': f'={ROXO}', 'Height': f'={h}',
        'OnSelect': onselect, 'Size': '=11', 'Text': f'="{texto}"', 'Visible': visivel,
        'Width': f'={w}', 'X': f'={x}', 'Y': f'={y}'})


def imagem(nome, formula, x, y, w=200, h=150):
    return controle(nome, 'Image@2.2.3', {'Height': f'={h}', 'Image': formula,
                                          'ImagePosition': '=ImagePosition.Fit', 'Width': f'={w}', 'X': f'={x}', 'Y': f'={y}'})


S2_GRAVAR = '''=UpdateContext({locSondaS2: ""});
ClearCollect(
    colSondaS2,
    {texto: "sonda", numero: 1.5, quando: Now(), marcado: true}
);
IfError(
    SaveData(colSondaS2, "an_sonda_s2"),
    UpdateContext({locSondaS2: "ERRO SaveData: " & FirstError.Message & " | "})
);
UpdateContext({locSondaS2: locSondaS2 & "gravado às " & Text(Now(), "hh:mm:ss") & ". Feche o app (deslize para fechar), abra de novo e toque em S2 Ler."})'''

S2_LER = '''=UpdateContext({locSondaS2: ""});
Clear(colSondaS2);
IfError(
    LoadData(colSondaS2, "an_sonda_s2", true),
    UpdateContext({locSondaS2: "ERRO LoadData: " & FirstError.Message & " | "})
);
UpdateContext(
    {
        locSondaS2: locSondaS2 & "lidos " & CountRows(colSondaS2) & ": " &
            First(colSondaS2).texto & " / " & First(colSondaS2).numero & " / " &
            Text(First(colSondaS2).quando, "dd/mm/yyyy hh:mm:ss") & " / " & First(colSondaS2).marcado
    }
)'''

S6_CONVERTER = '''=UpdateContext({locSondaFotoUri: Substitute(JSON(sondaImgCapturada.Image, JSONFormat.IncludeBinaryData), Char(34), "")});
UpdateContext({locSondaS6: "base64: " & Len(locSondaFotoUri) & " caracteres (" & Round(Len(locSondaFotoUri) / 1048576, 2) & " MB) | "});
ClearCollect(
    colSondaFotos,
    {chave: "foto1", dataUri: locSondaFotoUri}
);
IfError(
    SaveData(colSondaFotos, "an_sonda_fotos"),
    UpdateContext({locSondaS6: locSondaS6 & "ERRO SaveData: " & FirstError.Message & " | "})
);
UpdateContext({locSondaS6: locSondaS6 & "guardado às " & Text(Now(), "hh:mm:ss")})'''

S4_LER = '''=UpdateContext({locSondaS4: ""});
Clear(colSondaFotos);
IfError(
    LoadData(colSondaFotos, "an_sonda_fotos", true),
    UpdateContext({locSondaS4: "ERRO LoadData: " & FirstError.Message & " | "})
);
UpdateContext({locSondaS4: locSondaS4 & "fotos lidas: " & CountRows(colSondaFotos) & " | tamanho: " & Len(First(colSondaFotos).dataUri) & " (a foto tem de aparecer no quadro 2)"})'''

S4B_GRAVAR = '''=UpdateContext({locSondaS4b: ""});
ClearCollect(
    colSondaFotoBruta,
    {chave: "foto1", img: sondaImgCapturada.Image}
);
IfError(
    SaveData(colSondaFotoBruta, "an_sonda_foto_bruta"),
    UpdateContext({locSondaS4b: "ERRO SaveData: " & FirstError.Message & " | "})
);
UpdateContext({locSondaS4b: locSondaS4b & "guardado às " & Text(Now(), "hh:mm:ss") & ". Feche e reabra o app antes de ler."})'''

S4B_LER = '''=UpdateContext({locSondaS4b: ""});
Clear(colSondaFotoBruta);
IfError(
    LoadData(colSondaFotoBruta, "an_sonda_foto_bruta", true),
    UpdateContext({locSondaS4b: "ERRO LoadData: " & FirstError.Message & " | "})
);
UpdateContext({locSondaS4b: locSondaS4b & "lidas: " & CountRows(colSondaFotoBruta) & " (a foto tem de aparecer no quadro 3)"})'''

S3_GRAVAR = '''=UpdateContext({locSondaS3: "", locSondaS3Inicio: Now()});
IfError(
    Patch(
        '7.4.1-tbl_InspPistaItens',
        Defaults('7.4.1-tbl_InspPistaItens'),
        {
            Hash: "SONDA-S3",
            IdInsp: 0,
            Status: "SONDA",
            UsuarioCriador: "SONDA OFFLINE (apagar)",
            Foto: sondaImgLida.Image
        }
    ),
    UpdateContext({locSondaS3: "ERRO Patch: " & FirstError.Message & " | "})
);
UpdateContext(
    {
        locSondaS3: locSondaS3 & "no servidor: " &
            If(IsBlank(LookUp('7.4.1-tbl_InspPistaItens', Hash = "SONDA-S3").ID), "NÃO", "sim") &
            " | " & DateDiff(locSondaS3Inicio, Now(), TimeUnit.Milliseconds) & " ms (a foto tem de aparecer no quadro 4)"
    }
)'''

S3_APAGAR = '''=IfError(
    RemoveIf('7.4.1-tbl_InspPistaItens', Hash = "SONDA-S3"),
    UpdateContext({locSondaS3: "ERRO ao apagar: " & FirstError.Message})
);
UpdateContext({locSondaS3: "registro da sonda apagado da lista de itens às " & Text(Now(), "hh:mm:ss")})'''

S13 = '''=ClearCollect(
    colSondaRand,
    ForAll(Sequence(3), {r: Rand()})
);
UpdateContext({locSondaS13: "3 sorteios dentro de ForAll: " & Concat(colSondaRand, Text(r, "0.000000"), "  |  ")})'''

S16 = '''=UpdateContext({locSondaS16a: "não rodou", locSondaS16b: "não rodou"});
Select(sondaBtnOcultoDesabilitado);
Select(sondaBtnOcultoHabilitado)'''

S17 = '''=UpdateContext(
    {
        locSondaS17: "maior ID na lista de itens: " & First(Sort('7.4.1-tbl_InspPistaItens', ID, SortOrder.Descending)).ID &
            "  |  maior ID em tbl_inspMenu: " & First(Sort(tbl_inspMenu, ID, SortOrder.Descending)).ID &
            "  |  itens de menu PISTA carregados: " & CountRows(col_inspPistaMenu) & " (0 enquanto a tela principal não abriu)"
    }
)'''

LIMPAR = '''=IfError(ClearData("an_sonda_s2"), false);
IfError(ClearData("an_sonda_fotos"), false);
IfError(ClearData("an_sonda_foto_bruta"), false);
UpdateContext({locSondaS2: "arquivos da sonda apagados do aparelho", locSondaS4: "", locSondaS4b: "", locSondaS6: ""})'''


def main():
    A, LA, B, LB = 20, 280, 690, 950
    filhos = [
        rotulo('sondaTitulo', '="Sondas offline · piloto Inspeção de Pista"', 20, 8, 900, 36, size=18, bold=True),
        rotulo('sondaInstrucao',
               '="Use numa CÓPIA do app, no tablet. Anote cada resultado em Inspeções/build/sondas_offline.md. '
               'Depois de S3, toque em Apagar sonda."', 20, 44, 1320, 30, size=11),
        rotulo('sondaStatus',
               '="Conexão: " & If(Connection.Connected, "on-line", "OFF-LINE") & "   |   Host: " & Host.OSType',
               950, 8, 400, 36, size=12, bold=True),
        # coluna A: SaveData / LoadData / fotos
        botao('sondaBtnS2Gravar', 'S2 · Gravar dados', S2_GRAVAR, A, 90),
        botao('sondaBtnS2Ler', 'S2 · Ler dados', S2_LER, A, 150),
        rotulo('sondaResS2', '=locSondaS2', LA, 90, 400, 110),
        botao('sondaBtnS6', 'S6 · Converter foto e guardar', S6_CONVERTER, A, 220),
        rotulo('sondaResS6', '=locSondaS6', LA, 220, 400, 50),
        botao('sondaBtnS4', 'S4 · Ler foto convertida', S4_LER, A, 280),
        rotulo('sondaResS4', '=locSondaS4', LA, 280, 400, 50),
        botao('sondaBtnS4bGravar', 'S4b · Guardar foto sem converter', S4B_GRAVAR, A, 340),
        botao('sondaBtnS4bLer', 'S4b · Ler foto sem converter', S4B_LER, A, 400),
        rotulo('sondaResS4b', '=locSondaS4b', LA, 340, 400, 110),
        botao('sondaBtnLimpar', 'Apagar arquivos da sonda', LIMPAR, A, 460),
        # coluna B: SharePoint, Rand, Select, contagens
        botao('sondaBtnS3Gravar', 'S3 · Gravar foto lida na lista', S3_GRAVAR, B, 90),
        botao('sondaBtnS3Apagar', 'S3 · Apagar sonda', S3_APAGAR, B, 150),
        rotulo('sondaResS3', '=locSondaS3', LB, 90, 400, 110),
        botao('sondaBtnS13', 'S13 · Rand em ForAll', S13, B, 220),
        rotulo('sondaResS13', '=locSondaS13', LB, 220, 400, 50),
        botao('sondaBtnS16', 'S16 · Select em botão oculto', S16, B, 280),
        rotulo('sondaResS16', '="oculto e desabilitado: " & locSondaS16a & "  |  oculto e habilitado: " & locSondaS16b',
               LB, 280, 400, 50),
        botao('sondaBtnS17', 'S17 · Tamanho das listas', S17, B, 340),
        rotulo('sondaResS17', '=locSondaS17', LB, 340, 400, 110),
        # quadros de foto (1 capturada, 2 base64 relida, 3 sem conversão relida, 4 gravada no SharePoint)
        rotulo('sondaLegendaFotos', '="1 capturada   ·   2 base64 relida   ·   3 sem conversão relida   ·   4 gravada no SharePoint"',
               20, 520, 900, 24, size=10),
        imagem('sondaImgCapturada', '=sondaAddMedia.Media', 20, 548),
        imagem('sondaImgLida', '=First(colSondaFotos).dataUri', 240, 548),
        imagem('sondaImgBruta', '=First(colSondaFotoBruta).img', 460, 548),
        imagem('sondaImgServidor', "=LookUp('7.4.1-tbl_InspPistaItens', Hash = \"SONDA-S3\").Foto.Full", 680, 548),
        controle('sondaAddMedia', 'AddMedia@2.2.1', {'Height': '=150', 'Width': '=200', 'X': '=20', 'Y': '=548'}),
        # S16: dois botões ocultos, um desabilitado (como o envio do app sem conexão) e um habilitado
        botao('sondaBtnOcultoDesabilitado', 'oculto desabilitado', '=UpdateContext({locSondaS16a: "RODOU"})',
              B, 460, visivel='=false', modo='=DisplayMode.Disabled'),
        botao('sondaBtnOcultoHabilitado', 'oculto habilitado', '=UpdateContext({locSondaS16b: "RODOU"})',
              B, 460, visivel='=false'),
    ]
    cab = '\n'.join([
        HDR.rstrip('\n'), '#',
        f'# SONDAS — Inspeção de Pista: NÃO colar no app de produção. Arquivo > Salvar como (cópia),',
        f'# criar tela em branco, renomear para {TELA}, Exibição de código > substituir tudo, arrastar a',
        '# tela para o topo da árvore (vira a tela inicial da cópia), publicar a cópia e abrir no tablet.',
        '# LOCALE: formato INVARIANTE ("," separa argumentos, ";" encadeia, "." decimal). NÃO converter.',
        '#', ''])
    corpo = f"Screens:\n  {TELA}:\n    Children:\n" + '\n'.join(filhos) + '\n'
    os.makedirs('out', exist_ok=True)
    open(f'out/90_{TELA}.pa.yaml', 'w', encoding='utf-8', newline='\n').write(cab + corpo)
    exc_path = 'out/_excecoes_layout.json'
    exc = json.load(open(exc_path, encoding='utf-8')) if os.path.exists(exc_path) else {'somem': [], 'surgem': [], 'mudam': []}
    nomes = [f.split(':')[0].strip()[2:] for f in filhos]
    exc['surgem'] = [e for e in exc.get('surgem', []) if e[0] != TELA] + [[TELA, n] for n in nomes]
    json.dump(exc, open(exc_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"   out/90_{TELA}.pa.yaml: {len(filhos)} controles (tela nova, declarada na trava de layout)")


if __name__ == '__main__':
    main()
