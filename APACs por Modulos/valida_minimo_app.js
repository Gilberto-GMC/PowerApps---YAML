// Valida a formula candidata do app contra dois calculos independentes, em cada MES e cenario:
//   APP   = max( niveis_W8_rotacoes , ceil(soma/7) )           <- o que o Power Fx vai calcular
//   EXATO = minimo circular exato com janela de 8h (Bellman-Ford sobre restricoes de diferenca)
//   BUSCA = melhor escala real com intervalo INTERIOR achada por busca local + fluxo
const fs=require("fs"),path=require("path");
const dir="C:/Users/61-00095/Documents/Projetos/PowerApps---YAML/APACs por Modulos/dados";
let voos=[];
for(const f of fs.readdirSync(dir).filter(x=>/^malha_.*\.csv$/.test(x))){
  const ls=fs.readFileSync(path.join(dir,f),"utf8").replace(/^\uFEFF/,"").trim().split(/\r?\n/);
  const hd=ls[0].split(";"),iC=hd.indexOf("competencia"),iD=hd.indexOf("data"),iH=hd.indexOf("hora_min"),iA=hd.indexOf("assentos");
  for(const l of ls.slice(1)){const p=l.split(";");if(p.length<3)continue;const [dd,mm,yy]=p[iD].split("/").map(Number);
   voos.push({comp:p[iC],dia:Date.UTC(yy,mm-1,dd)/86400000,min:+p[iH],ass:+p[iA]});}
}
const dias=[...new Set(voos.map(v=>v.dia))].sort((a,b)=>a-b),dia0=dias[0];
const H=(dias[dias.length-1]-dia0+2)*24,teto=x=>Math.ceil(x-1e-9);
const compDia={};voos.forEach(v=>compDia[v.dia]=v.comp);
function envelopes({ocup=.85,antec=90,cap=185,assmin=150,literal=false}){
  const pax=Array(H).fill(0),dec=Array(H).fill(0);
  for(const v of voos){const off=(v.dia-dia0)*1440+v.min,ini=off-antec;
    for(let h=Math.floor(ini/60);h<=Math.floor((off-1)/60);h++){if(h<0||h>=H)continue;const a=Math.max(h*60,ini),b=Math.min(h*60+60,off);if(b>a)pax[h]+=(b-a)/antec*v.ass*ocup;}
    const hd=Math.floor(off/60);if(v.ass>assmin&&hd>=0&&hd<H)dec[hd]++;}
  const porComp={};
  for(let h=0;h<H;h++){const d=dia0+Math.floor(h/24);const c=compDia[d];if(!c)continue;
    const pd=literal?(dec[h]>=3?3:0):dec[h];const m=Math.min(3,Math.max(teto(pax[h]/cap),pd));
    porComp[c]=porComp[c]||{A:Array(24).fill(0),S:Array(24).fill(0)};
    const hr=h%24;porComp[c].A[hr]=Math.max(porComp[c].A[hr],m*3+5);porComp[c].S[hr]=Math.max(porComp[c].S[hr],teto(m/2));}
  const tem={A:Array(24).fill(0),S:Array(24).fill(0)};
  Object.values(porComp).forEach(e=>{for(let h=0;h<24;h++){tem.A[h]=Math.max(tem.A[h],e.A[h]);tem.S[h]=Math.max(tem.S[h],e.S[h]);}});
  porComp["TEMPORADA"]=tem;return porComp;
}
function niveis(env,W){let best=Infinity;
  for(let r=0;r<24;r++){const d=[...Array(24)].map((_,k)=>env[(r+k)%24]);let prev=null;
    for(let lv=1;lv<=4;lv++){const g=d.map((x,k)=>x+(lv>1&&k>=W?prev[k-W]:0));prev=g.map((_,h)=>Math.max(...g.slice(0,h+1)));}
    best=Math.min(best,prev[23]);}return best;}
function exatoW8(env){ // viabilidade de n por restricoes de diferenca; menor n viavel
  const soma=env.reduce((a,b)=>a+b,0);
  for(let n=0;n<=soma;n++){
    // S[-1]=0 ... S[23]=n ; nos 0..24 representam S[-1..23]
    const E=[];const N=25;
    for(let h=0;h<24;h++){E.push([h+1,h,0]); /* S[h]>=S[h-1] : S[h-1]-S[h]<=0 */}
    E.push([0,24,n]);E.push([24,0,-n]); // S[23]-S[-1]=n
    for(let h=0;h<24;h++){ // S[h]-S[h-8] (+n se cruza) >= d  -> S[h-8]-S[h] <= -d (+n)
      let j=h-8, add=0; if(j<-1){j+=24;add=n;} // S[j] com j em -1..23
      // cobertura em h = S[h]-S[j] + add  (add = n quando a janela atravessa o inicio)
      E.push([h+1,j+1,-env[h]+add]);
    }
    const dist=Array(N).fill(0);let ok=true;
    for(let it=0;it<N;it++){let mud=false;for(const [u,v,w] of E){if(dist[u]+w<dist[v]){dist[v]=dist[u]+w;mud=true;}}if(!mud)break;if(it===N-1&&mud)ok=false;}
    if(ok){let mud=false;for(const [u,v,w] of E)if(dist[u]+w<dist[v])mud=true;if(!mud)return n;}
  }return NaN;}
function viavel(s,d){const c=Array(24).fill(0);s.forEach((n,p)=>{for(let k=0;k<8;k++)c[(p+k)%24]+=n;});
  if(c.some((x,h)=>x<d[h]))return false;const n=s.reduce((a,b)=>a+b,0);
  const N=50,S=0,T=1,G=p=>2+p,Hh=h=>26+h;const cap=[...Array(N)].map(()=>Array(N).fill(0));
  s.forEach((x,p)=>{cap[S][G(p)]=x;for(let b=1;b<=6;b++)cap[G(p)][Hh((p+b)%24)]=1e9;});
  for(let h=0;h<24;h++)cap[Hh(h)][T]=c[h]-d[h];let fl=0;
  while(true){const pai=Array(N).fill(-1);pai[S]=S;const q=[S];while(q.length&&pai[T]<0){const u=q.shift();for(let v=0;v<N;v++)if(pai[v]<0&&cap[u][v]>0){pai[v]=u;q.push(v);}}
    if(pai[T]<0)break;let f=1e9;for(let v=T;v!==S;v=pai[v])f=Math.min(f,cap[pai[v]][v]);for(let v=T;v!==S;v=pai[v]){cap[pai[v]][v]-=f;cap[v][pai[v]]+=f;}fl+=f;}
  return fl===n;}
function busca(d,alvo){ // tenta achar escala com intervalo interior de tamanho 'alvo'
  for(let sd=1;sd<=40;sd++){let rng=sd*2654435761>>>0;const rnd=()=>((rng=(rng*1664525+1013904223)>>>0)/4294967296);
    let s=Array(24).fill(Math.ceil(Math.max(...d,1)/3)+1);while(!viavel(s,d))s[Math.floor(rnd()*24)]++;
    for(let it=0;it<20000;it++){const t=s.slice(),a=Math.floor(rnd()*24),mv=rnd();
      if(mv<.4){if(!t[a])continue;t[a]--;}else{const b=mv<.8?(a+(rnd()<.5?1:23))%24:Math.floor(rnd()*24);if(!t[a])continue;t[a]--;t[b]++;}
      if(viavel(t,d)){s=t;if(s.reduce((x,y)=>x+y,0)<=alvo)return true;}}}
  return false;}
const cen=[["base",{}],["literal",{literal:true}],["ocup80",{ocup:.8}],["ocup95",{ocup:.95}],["antec60",{antec:60}],["antec120",{antec:120}],["sem corte",{assmin:0}],["cap150",{cap:150}],["lit+95+120",{literal:true,ocup:.95,antec:120}]];
let divergencias=0;
console.log("cenario     comp        | APP_A EXATO_W8 busca<=APP? | APP_S EXATO_W8 busca<=APP?");
for(const [nome,o] of cen){const e=envelopes(o);
  for(const c of Object.keys(e).sort()){
    const res=[];
    for(const k of ["A","S"]){const d=e[c][k];const soma=d.reduce((a,b)=>a+b,0);
      const app=Math.max(niveis(d,8),Math.ceil(soma/7)), ex=exatoW8(d);
      const lb=Math.max(ex,Math.ceil(soma/7)); // limite inferior PROVADO
      const ating=busca(d,app);
      if(app!==lb||!ating)divergencias++;
      res.push(`${String(app).padStart(4)} ${String(ex).padStart(6)}${app!==lb?"(LB "+lb+")":""} ${ating?"sim":"NAO"}`);
    }
    console.log(nome.padEnd(11),c.padEnd(11),"|",res[0].padEnd(26),"|",res[1]);
  }
}
console.log("\nDIVERGENCIAS:",divergencias);
