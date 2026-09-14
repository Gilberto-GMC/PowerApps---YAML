// ⚠️ Imprime UMA escala viavel (38 APAC). Nao e o minimo: o minimo exato e 36
// (valida_minimo_app.js, 14/09/2026).
// Cobertura minima: cada pessoa = janela de 8h consecutivas menos 1 hora de intervalo (interior).
// Pergunta: quantas pessoas sao necessarias para cobrir o envelope horario?
// Greedy pelo maior ganho + 400 reinicios aleatorios deterministicos (LCG), depois poda.
const maxA=[5,8,8,8,11,11,11,11,11,11,14,14,8,11,11,14,11,11,14,14,14,8,5,5];
const maxS=[0,1,1,1,1,1,1,1,1,1,2,2,1,1,1,2,1,1,2,2,2,1,0,0];
const padroes=[];
for(let s=0;s<24;s++) for(let b=1;b<=6;b++){
  const cob=Array(24).fill(0);
  for(let k=0;k<8;k++) if(k!==b) cob[(s+k)%24]=1;
  padroes.push({s,b,cob});
}
function resolve(dem,seed){
  let rng=seed; const rnd=()=>((rng=(rng*1103515245+12345)&0x7fffffff)/0x7fffffff);
  const falta=dem.slice(); const esc=[];
  while(falta.some(x=>x>0)){
    let best=null,bv=-1;
    for(const p of padroes){ let g=0; for(let h=0;h<24;h++) if(falta[h]>0&&p.cob[h]) g++;
      const v=g+rnd()*0.9; if(v>bv){bv=v;best=p;} }
    if(bv<=0.9) break;
    esc.push(best); for(let h=0;h<24;h++) if(best.cob[h]) falta[h]--;
  }
  // poda: remove quem nao e necessario
  let mudou=true;
  while(mudou){ mudou=false;
    for(let i=0;i<esc.length;i++){
      const cob=Array(24).fill(0); esc.forEach((p,j)=>{if(j!==i) for(let h=0;h<24;h++) cob[h]+=p.cob[h];});
      if(dem.every((d,h)=>cob[h]>=d)){ esc.splice(i,1); mudou=true; break; }
    }
  }
  return esc;
}
function melhor(dem,nome,contratado){
  let best=null;
  for(let s=1;s<=400;s++){ const e=resolve(dem,s*7919); if(!best||e.length<best.length) best=e; }
  const cob=Array(24).fill(0); best.forEach(p=>{for(let h=0;h<24;h++) cob[h]+=p.cob[h];});
  console.log(`\n=== ${nome}: envelope ${dem.reduce((a,b)=>a+b,0)} homem-hora | MINIMO ENCONTRADO = ${best.length} pessoas | contratado hoje = ${contratado}`);
  const cont={}; best.forEach(p=>{const k=String(p.s).padStart(2,"0")+"h (intervalo +"+p.b+")"; cont[k]=(cont[k]||0)+1;});
  for(const [k,v] of Object.entries(cont).sort()) console.log(`   ${v} pessoa(s) inicio ${k}`);
  console.log("   cobertura:",cob.join(","));
  console.log("   demanda  :",dem.join(","));
  console.log("   folga    :",cob.map((c,h)=>c-dem[h]).join(","));
  return best.length;
}
melhor(maxA,"APAC",38);
melhor(maxS,"SUPERVISOR",4);
