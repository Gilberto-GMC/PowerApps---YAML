import re,sys
SRC="msapp/Src"
def block(path, key, indent):
    """return text of property block starting at 'key:' with given indent"""
    lines=open(f"{SRC}/{path}.pa.yaml",encoding='utf-8').read().split('\n')
    out=[]
    for i,l in enumerate(lines):
        if l.strip().startswith(key):
            ind=len(l)-len(l.lstrip())
            out=[l]
            for s in lines[i+1:]:
                if not s.strip(): out.append(s); continue
                if (len(s)-len(s.lstrip()))<=ind: break
                out.append(s)
            return '\n'.join(out)
    return "<<não encontrado>>"
mods={
 "ColVei":("ScreenColisaoVeiculos","GalleryColVeiRegistros:"),
 "DerFlu":("ScreenDerramamentoFluido","GalleryDerFlu:"),
 "ExcPista":("ScreenExcursaoPista","GalleryExcPistaRegistros:"),
 "IncPista":("ScreenIncursaoPista","GalleryIncPistaRegistros:"),
 "IntExt":("ScreenInterferenciaExterna","GalleryIntExtRegistros:"),
 "JetBlast":("ScreenJetBlast","GalleryJetBlastRegistros:"),
 "OcoSolo":("ScreenOcorrenciaSolo","GalleryOcoSoloListar:"),
}
for k,(scr,gal) in mods.items():
    print("#"*20,k,scr)
    t=block(scr,gal,0)
    m=re.search(r'^(\s+)Items: \|-\n(.*?)(?=\n\s{0,%d}\w)'%0,t,re.S)
    # simpler: grab Items block
    lines=t.split('\n')
    for i,l in enumerate(lines):
        if re.match(r'^\s+Items:',l):
            ind=len(l)-len(l.lstrip()); out=[l]
            for s in lines[i+1:]:
                if not s.strip(): out.append(s); continue
                if (len(s)-len(s.lstrip()))<=ind: break
                out.append(s)
            print('\n'.join(out)); break
    print("-- OnVisible --")
    print(block(scr,"OnVisible:",0)[:1200])
