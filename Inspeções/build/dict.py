import re, json, os, glob, collections
SRC="msapp/Src"
d=collections.defaultdict(set)
pat_ctrl=re.compile(r'^(\s+)Control:\s*(\S+)\s*$')
files=glob.glob(f"{SRC}/*.pa.yaml")+glob.glob(f"{SRC}/Components/*.pa.yaml")
for f in files:
    lines=open(f,encoding='utf-8').read().split('\n')
    i=0
    while i<len(lines):
        m=pat_ctrl.match(lines[i])
        if m:
            ind=len(m.group(1)); ctrl=m.group(2)
            # find Properties: at same indent
            j=i+1
            while j<len(lines):
                s=lines[j]
                if not s.strip(): j+=1; continue
                cur=len(s)-len(s.lstrip())
                if cur<ind: break
                if cur==ind and s.strip()=='Properties:':
                    k=j+1
                    while k<len(lines):
                        s2=lines[k]
                        if not s2.strip(): k+=1; continue
                        cur2=len(s2)-len(s2.lstrip())
                        if cur2<=ind: break
                        if cur2==ind+2:
                            mm=re.match(r'^\s+([A-Za-z_][\w.\']*):',s2)
                            if mm: d[ctrl].add(mm.group(1))
                        k+=1
                    break
                if cur==ind and s.strip() not in ('Properties:',): 
                    j+=1; continue
                j+=1
        i+=1
out={k:sorted(v) for k,v in sorted(d.items())}
json.dump(out,open("build/propdict.json","w"),indent=1,ensure_ascii=False)
print(f"{len(out)} tipos de controle")
for k in out: print(f"  {k}: {len(out[k])} props")
