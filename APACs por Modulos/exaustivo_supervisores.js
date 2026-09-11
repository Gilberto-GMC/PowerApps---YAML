// Enumeracao EXAUSTIVA: existe alguma combinacao de 4 supervisores (janela 8h, 1h de intervalo
// em qualquer das 8 horas) que cubra o envelope? Sem heuristica, sem amostragem.
const dem=[0,1,1,1,1,1,1,1,1,1,2,2,1,1,1,2,1,1,2,2,2,1,0,0];
const pad=[];
for(let s=0;s<24;s++) for(let b=0;b<8;b++){
  const c=Array(24).fill(0);
  for(let k=0;k<8;k++) if(k!==b) c[(s+k)%24]=1;
  pad.push(c);
}
// dedup de padroes identicos
const vistos=new Set(), P=[];
for(const c of pad){const k=c.join("");if(!vistos.has(k)){vistos.add(k);P.push(c);}}
console.log("padroes distintos:",P.length);
let achou=null, testados=0;
const n=P.length;
outer:
for(let a=0;a<n;a++) for(let b=a;b<n;b++) for(let c=b;c<n;c++) for(let d=c;d<n;d++){
  testados++;
  let ok=true;
  for(let h=0;h<24;h++){ if(P[a][h]+P[b][h]+P[c][h]+P[d][h] < dem[h]){ok=false;break;} }
  if(ok){ achou=[a,b,c,d]; break outer; }
}
console.log("combinacoes testadas:",testados);
console.log(achou? "EXISTE solucao com 4 supervisores: "+JSON.stringify(achou.map(i=>P[i].join("")))
                 : "NAO EXISTE nenhuma combinacao de 4 supervisores que cubra o envelope.");
