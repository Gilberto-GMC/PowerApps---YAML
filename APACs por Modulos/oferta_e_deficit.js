// Reverificacao do deficit, com a OFERTA lida por LETRA de coluna (regua da linha 3),
// nao por posicao. Foi a posicao que produziu o array de supervisores deslocado.
const fs=require("fs"), zlib=require("zlib"), path=require("path");
function lerZip(c){const b=fs.readFileSync(c);const a={};let i=0;
 while((i=b.indexOf(Buffer.from("PK\x03\x04"),i))!==-1){const m=b.readUInt16LE(i+8),tc=b.readUInt32LE(i+18),tn=b.readUInt16LE(i+26),te=b.readUInt16LE(i+28);
 const n=b.slice(i+30,i+30+tn).toString("utf8");const ini=i+30+tn+te;
 if(tc>0){const d=b.slice(ini,ini+tc);try{a[n]=m===0?d.toString("utf8"):zlib.inflateRawSync(d).toString("utf8")}catch{}}
 i=ini+tc;}return a;}
const z=lerZip("C:/Users/61-00095/Downloads/Escopo NVT Verão 2027.xlsx");
const xml=z["xl/worksheets/sheet1.xml"];
const linhas={};
for(const lm of xml.matchAll(/<row[^>]*r="(\d+)"[^>]*>([\s\S]*?)<\/row>/g)){
  const n=+lm[1]; const cel={};
  for(const cm of lm[2].matchAll(/<c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/c>)/g)){
    if(cm[2]===undefined) continue;
    const ref=(cm[1].match(/r="([A-Z]+)\d+"/)||[])[1];
    const v=(cm[2].match(/<v>([\s\S]*?)<\/v>/)||[])[1];
    if(ref&&v!==undefined&&!/t="s"/.test(cm[1])) cel[ref]=parseFloat(v);
  }
  linhas[n]=cel;
}
// regua: linha 3, fracao do dia -> hora
const regua={};
for(const [ref,v] of Object.entries(linhas[3]||{})) { const h=Math.round(v*24); if(h>=0&&h<=23) regua[ref]=h; }
const cols=Object.keys(regua).sort((a,b)=>regua[a]-regua[b]);
console.log("REGUA:", cols.map(c=>c+"->"+regua[c]).join(" "));
const serie=(n)=>{const s=Array(24).fill(0);for(const c of cols) s[regua[c]]=linhas[n]&&linhas[n][c]!==undefined?linhas[n][c]:0;return s;};
const soma=(de,ate)=>{const s=Array(24).fill(0);for(let n=de;n<=ate;n++) for(const c of cols) if(linhas[n]&&linhas[n][c]!==undefined) s[regua[c]]+=linhas[n][c];return s;};

const apac8=serie(56), vigil=soma(48,55), supOf=serie(58);
const apacOf=apac8.map((v,i)=>v+vigil[i]);
// autoconferencia: soma detalhada das linhas 20..39 tem de bater com a linha 56
const det=soma(20,39);
const bate=det.every((v,i)=>v===apac8[i]);
console.log("CONFERE linhas 20-39 == linha 56 ?", bate?"SIM":"NAO -> "+JSON.stringify(det));
if(!bate){console.log("PARANDO: leitura da oferta nao se confere.");process.exit(1);}
const detSup=soma(40,47);
console.log("CONFERE linhas 40-47 == linha 58 ?", detSup.every((v,i)=>v===supOf[i])?"SIM":"NAO -> "+JSON.stringify(detSup));
console.log("OFERTA APAC :",apacOf.join(","));
console.log("OFERTA SUPER:",supOf.join(","));
console.log("homem-hora APAC ofertado:",apacOf.reduce((a,b)=>a+b,0));

// ------------------------------------------------ DEMANDA da malha
const OCUP=0.85, ANTEC=90, CAP=185, ASSMIN=150, RX=3, FIXOS=5, APACMOD=3;
const dir="C:/Users/61-00095/Documents/Projetos/PowerApps---YAML/APACs por Modulos/dados";
let voos=[];
for(const f of fs.readdirSync(dir).filter(x=>/^malha_.*\.csv$/.test(x))){
  const txt=fs.readFileSync(path.join(dir,f),"utf8").replace(/^\uFEFF/,"");
  const ls=txt.trim().split(/\r?\n/); const hd=ls[0].split(";");
  const iD=hd.indexOf("data"),iH=hd.indexOf("hora_min"),iA=hd.indexOf("assentos");
  for(const l of ls.slice(1)){const p=l.split(";"); if(p.length<3)continue;
    const [dd,mm,yy]=p[iD].split("/").map(Number);
    voos.push({dia:Date.UTC(yy,mm-1,dd)/86400000, min:+p[iH], ass:+p[iA]});}
}
console.log("voos lidos:",voos.length);
const dias=[...new Set(voos.map(v=>v.dia))].sort((a,b)=>a-b);
console.log("dias:",dias.length);
const teto=(x)=>Math.ceil(x-1e-9);
// linha do tempo absoluta em horas -> trata virada da meia-noite naturalmente
const dia0=dias[0];
const H=(dias[dias.length-1]-dia0+2)*24;
const pax=Array(H).fill(0), dec=Array(H).fill(0);
for(const v of voos){
  const off=(v.dia-dia0)*24*60 + v.min;          // minuto absoluto da decolagem
  const ini=off-ANTEC;
  for(let h=Math.floor(ini/60); h<=Math.floor((off-1)/60); h++){
    if(h<0||h>=H) continue;
    const a=Math.max(h*60,ini), b=Math.min(h*60+60,off);
    if(b>a) pax[h]+=(b-a)/ANTEC*v.ass*OCUP;
  }
  const hd=Math.floor(off/60);
  if(v.ass>ASSMIN && hd>=0 && hd<H) dec[hd]++;
}
const mod=Array(H),apacD=Array(H),supD=Array(H);
for(let h=0;h<H;h++){ const m=Math.min(RX, Math.max(teto(pax[h]/CAP), dec[h]));
  mod[h]=m; apacD[h]=m*APACMOD+FIXOS; supD[h]=teto(m/2); }
// deficit por hora-do-dia, contando dias (so as horas dentro dos 151 dias com voos)
const setDias=new Set(dias);
const defA={},defS={},maxA=Array(24).fill(0),maxS=Array(24).fill(0);
for(let h=0;h<H;h++){
  const d=dia0+Math.floor(h/24), hd=h%24;
  if(!setDias.has(d)) continue;
  maxA[hd]=Math.max(maxA[hd],apacD[h]); maxS[hd]=Math.max(maxS[hd],supD[h]);
  const fa=apacD[h]-apacOf[hd], fs_=supD[h]-supOf[hd];
  if(fa>0){ defA[hd]=defA[hd]||{dias:0,max:0}; defA[hd].dias++; defA[hd].max=Math.max(defA[hd].max,fa); }
  if(fs_>0){ defS[hd]=defS[hd]||{dias:0,max:0}; defS[hd].dias++; defS[hd].max=Math.max(defS[hd].max,fs_); }
}
console.log("\nhora | demMaxAPAC ofer falta(dias,max) | demMaxSUP ofer falta(dias,max)");
for(let h=0;h<24;h++){
  const a=defA[h],s=defS[h];
  console.log(String(h).padStart(2,"0")+"h  | "+String(maxA[h]).padStart(3)+" "+String(apacOf[h]).padStart(3)+"  "+(a?`FALTA ${a.max} em ${a.dias}d`:"ok").padEnd(18)+"| "+String(maxS[h]).padStart(2)+" "+String(supOf[h]).padStart(2)+"  "+(s?`FALTA ${s.max} em ${s.dias}d`:"ok"));
}
// envelope: demanda maxima por hora somada (dimensionamento de pior caso por hora)
console.log("\nenvelope APAC (soma dos maximos por hora):",maxA.reduce((a,b)=>a+b,0),"| oferta:",apacOf.reduce((a,b)=>a+b,0));
console.log("envelope SUP:",maxS.reduce((a,b)=>a+b,0),"| oferta:",supOf.reduce((a,b)=>a+b,0));
