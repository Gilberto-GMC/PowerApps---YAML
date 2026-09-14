// ⚠️ SUPERADO em 14/09/2026 por valida_minimo_app.js. O minimo de APAC aqui vem de busca gulosa
// e sai MAIOR que o verdadeiro (39 onde o exato e 37). Mantido para rastrear a versao de 11/09.
// O minimo de efetivo sobrevive as premissas em disputa?
// Varia: (a) leitura da contagem N->N  x  literal (so >=3 dispara 3), (b) ocupacao, (c) antecedencia,
// (d) corte de assentos. Para cada cenario: envelope, minimo de APAC (greedy+poda) e
// viabilidade EXAUSTIVA de 4 supervisores.
const fs=require("fs"),path=require("path");
const dir="C:/Users/61-00095/Documents/Projetos/PowerApps---YAML/APACs por Modulos/dados";
let voos=[];
for(const f of fs.readdirSync(dir).filter(x=>/^malha_.*\.csv$/.test(x))){
  const ls=fs.readFileSync(path.join(dir,f),"utf8").replace(/^\uFEFF/,"").trim().split(/\r?\n/);
  const hd=ls[0].split(";"),iD=hd.indexOf("data"),iH=hd.indexOf("hora_min"),iA=hd.indexOf("assentos");
  for(const l of ls.slice(1)){const p=l.split(";");if(p.length<3)continue;const [dd,mm,yy]=p[iD].split("/").map(Number);
   voos.push({dia:Date.UTC(yy,mm-1,dd)/86400000,min:+p[iH],ass:+p[iA]});}
}
const dias=[...new Set(voos.map(v=>v.dia))].sort((a,b)=>a-b),dia0=dias[0],setD=new Set(dias);
const H=(dias[dias.length-1]-dia0+2)*24, teto=x=>Math.ceil(x-1e-9);
function envelope({ocup=0.85,antec=90,cap=185,assmin=150,literal=false}){
  const pax=Array(H).fill(0),dec=Array(H).fill(0);
  for(const v of voos){const off=(v.dia-dia0)*1440+v.min,ini=off-antec;
   for(let h=Math.floor(ini/60);h<=Math.floor((off-1)/60);h++){if(h<0||h>=H)continue;
     const a=Math.max(h*60,ini),b=Math.min(h*60+60,off); if(b>a) pax[h]+=(b-a)/antec*v.ass*ocup;}
   const hd=Math.floor(off/60); if(v.ass>assmin&&hd>=0&&hd<H) dec[hd]++;}
  const mA=Array(24).fill(0),mS=Array(24).fill(0);
  for(let h=0;h<H;h++){const d=dia0+Math.floor(h/24);if(!setD.has(d))continue;
   const porDec = literal ? (dec[h]>=3?3:0) : dec[h];
   const m=Math.min(3,Math.max(teto(pax[h]/cap),porDec));
   const hd=h%24; mA[hd]=Math.max(mA[hd],m*3+5); mS[hd]=Math.max(mS[hd],teto(m/2));}
  return {mA,mS};
}
const P=[];{const vis=new Set();
 for(let s=0;s<24;s++)for(let b=0;b<8;b++){const c=Array(24).fill(0);for(let k=0;k<8;k++)if(k!==b)c[(s+k)%24]=1;
  const key=c.join("");if(!vis.has(key)){vis.add(key);P.push(c);}}}
function minPessoas(dem,limite){ // greedy multi-restart + poda
  let best=Infinity;
  for(let seed=1;seed<=250;seed++){let rng=seed*7919;const rnd=()=>((rng=(rng*1103515245+12345)&0x7fffffff)/0x7fffffff);
   const falta=dem.slice(),esc=[];
   while(falta.some(x=>x>0)){let bp=null,bv=-1;
     for(const p of P){let g=0;for(let h=0;h<24;h++)if(falta[h]>0&&p[h])g++;const v=g+rnd()*0.9;if(v>bv){bv=v;bp=p;}}
     if(bv<=0.9)break; esc.push(bp);for(let h=0;h<24;h++)if(bp[h])falta[h]--;}
   let mud=true;while(mud){mud=false;for(let i=0;i<esc.length;i++){const c=Array(24).fill(0);
     esc.forEach((p,j)=>{if(j!==i)for(let h=0;h<24;h++)c[h]+=p[h];});
     if(dem.every((d,h)=>c[h]>=d)){esc.splice(i,1);mud=true;break;}}}
   if(esc.length<best)best=esc.length;}
  return best;
}
function viavelN(dem,n){ // exaustivo para n pequeno
  const m=P.length;
  const rec=(i,ini,cob)=>{ if(i===n) return dem.every((d,h)=>cob[h]>=d);
    // poda: potencial maximo restante
    for(let j=ini;j<m;j++){const c2=cob.map((x,h)=>x+P[j][h]); if(rec(i+1,j,c2))return true;}
    return false;};
  return rec(0,0,Array(24).fill(0));
}
const cenarios=[
 {nome:"base (N->N, 85%, 90min, >150)",o:{}},
 {nome:"contagem LITERAL (so >=3 dispara 3)",o:{literal:true}},
 {nome:"ocupacao 80%",o:{ocup:0.80}},
 {nome:"ocupacao 95%",o:{ocup:0.95}},
 {nome:"antecedencia 60min",o:{antec:60}},
 {nome:"antecedencia 120min",o:{antec:120}},
 {nome:"sem corte de assentos",o:{assmin:0}},
 {nome:"capacidade 150 pax/h",o:{cap:150}},
 {nome:"LITERAL + 95% + 120min",o:{literal:true,ocup:0.95,antec:120}},
];
console.log("cenario".padEnd(38),"envAPAC","minAPAC(38?)","envSUP","4sup?","minSUP");
for(const c of cenarios){
  const {mA,mS}=envelope(c.o);
  const eA=mA.reduce((a,b)=>a+b,0), eS=mS.reduce((a,b)=>a+b,0);
  const nA=minPessoas(mA), quatro=viavelN(mS,4), nS=quatro?4:(viavelN(mS,5)?5:6);
  console.log(c.nome.padEnd(38), String(eA).padStart(6), String(nA).padStart(8)+(nA<=38?" ok":" ESTOURA"),
    String(eS).padStart(6), (quatro?"viavel":"INVIAVEL").padStart(9), String(nS).padStart(5));
}
