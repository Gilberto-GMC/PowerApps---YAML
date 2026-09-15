// testar_escala.js — os números que a scrApacEscala tem de mostrar, calculados fora do Power Apps.
//
// Uso:  node testar_escala.js
// Lê:   dados/malha_AAAA-MM.csv (a malha importada) e dados/escala_escopo_AAAA-MM.csv (a escala da planilha)
//
// Reproduz a conta do app, não a conta "ideal":
//   - colMesCel do btnCalcMes: só voos da MESMA competência (é o que colVoosMes traz), o dia seguinte
//     derrama passageiros nas últimas horas do dia, módulos = max(ceil(pax/cap), decolagens > corte) travado
//     nos raios-X, APAC = módulos × 3 + postos fixos (5 nas 24h), supervisor = ceil(módulos/2);
//   - cobre() da escala — a mesma função do escala_do_escopo.js, que bateu com a planilha hora a hora;
//   - falta = max(0, exigido − escalado) em cada dia × hora.
// Premissas: as da vigência de NVT (185 pax/h, 85%, 90 min, corte 150, 3 APAC/módulo, 2 módulos/sup, 3 raios-X).
//
// Conferências antes de imprimir (sai com erro se alguma falhar):
//   1. a cobertura lida dos CSVs é a da planilha (linhas 56+48–55 e 58);
//   2. o total de voos por competência é o que a tela do mês mostrou (727 em 2026-10).

const fs = require("fs");
const path = require("path");
const DIR = path.join(__dirname, "dados");
const P = { cap: 185, ocup: 85, antec: 90, assmin: 150, apacMod: 3, modSup: 2, raiosx: 3, fixoA: 5, fixoS: 0 };
// --fixos=N troca os APACs de posto fixo por hora (padrão 5: Acesso C 3 + Portão 1 + Apoio 1, como cadastrado)
const FIXOS = process.argv.find((a) => a.startsWith("--fixos="));
if (FIXOS) { P.fixoA = +FIXOS.slice(8); console.log(`postos fixos de APAC por hora: ${P.fixoA}`); }
// linha 56 do escopo (TOTAL APAC 8HRS) — sem as linhas 48–55: vigilância fora do app
const PLAN_A = [3, 3, 3, 10, 11, 12, 12, 9, 9, 12, 12, 10, 12, 11, 14, 12, 9, 12, 14, 10, 9, 9, 3, 3];
const PLAN_S = [0, 0, 0, 1, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2, 2, 1, 1, 1, 0, 0];
const VOOS_ESPERADOS = { "2026-10": 727 };

const csv = (f) => {
  const ls = fs.readFileSync(f, "utf8").replace(/^﻿/, "").trim().split(/\r?\n/);
  const cab = ls[0].split(";");
  return ls.slice(1).filter((l) => l.trim()).map((l) => { const p = l.split(";"); const o = {}; cab.forEach((c, i) => (o[c] = p[i])); return o; });
};
const teto = (x) => Math.ceil(x - 1e-9);

function cobre(t, h) {
  const s = h * 60, fim = t.ini + t.dur;
  const presente = (s >= t.ini && s + 60 <= fim) || (s + 1440 >= t.ini && s + 1500 <= fim);
  const emIntervalo = t.im > 0 &&
    ((s < t.ii + t.im && s + 60 > t.ii) || (s + 1440 < t.ii + t.im && s + 1500 > t.ii));
  return presente && !emIntervalo;
}

// mínimo da tela do mês (mesma fórmula do btnCalcMes, validada em valida_minimo_app.js)
function niveis(env, W) {
  let best = Infinity;
  for (let r = 0; r < 24; r++) {
    const d = [...Array(24)].map((_, k) => env[(r + k) % 24]); let prev = null;
    for (let lv = 1; lv <= 4; lv++) { const g = d.map((x, k) => x + (lv > 1 && k >= W ? prev[k - W] : 0)); prev = g.map((_, h) => Math.max(...g.slice(0, h + 1))); }
    best = Math.min(best, prev[23]);
  }
  return best;
}
const minimo = (env) => Math.max(niveis(env, 8), teto(env.reduce((a, b) => a + b, 0) / 7));

// --extra=PAPEL:inicio_min:duracao_min:intervalo_inicio_min:intervalo_min:qtd  soma um turno à escala de cada mês,
// para prever o que a tela mostra depois de cadastrar esse turno (a conferência 1 não se aplica).
const EXTRA = (process.argv.find((a) => a.startsWith("--extra=")) || "").slice(8);
const turnoExtra = EXTRA ? (([papel, ini, dur, ii, im, qtd]) => ({ papel, ini: +ini, dur: +dur, ii: +ii, im: +im, qtd: +qtd }))(EXTRA.split(":")) : null;
if (turnoExtra) console.log("com turno extra:", JSON.stringify(turnoExtra));

let falhas = 0;
const comps = fs.readdirSync(DIR).map((f) => (f.match(/^escala_escopo_(\d{4}-\d{2})\.csv$/) || [])[1]).filter(Boolean).sort();
const hh = (h) => String(h).padStart(2, "0");
const linha = (rot, arr) => rot.padEnd(18) + arr.map((v) => String(v === "" ? "" : v).padStart(4)).join("");

for (const comp of comps) {
  const turnos = csv(path.join(DIR, `escala_escopo_${comp}.csv`)).filter((r) => r.ativo === "1").map((r) => ({
    papel: r.papel, ini: +r.hora_inicio, dur: +r.duracao_min,
    ii: r.intervalo_inicio === "" ? 0 : +r.intervalo_inicio, im: r.intervalo_inicio === "" ? 0 : +r.intervalo_min, qtd: +r.quantidade,
  }));
  const cob = (papeis) => Array.from({ length: 24 }, (_, h) => turnos.filter((t) => papeis.includes(t.papel) && cobre(t, h)).reduce((a, t) => a + t.qtd, 0));
  const escA = cob(["APAC"]), escS = cob(["SUPERVISOR"]);
  if (turnoExtra) {
    turnos.push(turnoExtra);
    const extraCob = (papeis) => Array.from({ length: 24 }, (_, h) => (papeis.includes(turnoExtra.papel) && cobre(turnoExtra, h) ? turnoExtra.qtd : 0));
    const eA = extraCob(["APAC"]), eS = extraCob(["SUPERVISOR"]);
    for (let h = 0; h < 24; h++) { escA[h] += eA[h]; escS[h] += eS[h]; }
  } else if (escA.join() !== PLAN_A.join() || escS.join() !== PLAN_S.join()) { console.log(`✗ ${comp}: cobertura do CSV não é a da planilha`); falhas++; continue; }

  const arqMalha = path.join(DIR, `malha_${comp}.csv`);
  if (!fs.existsSync(arqMalha)) { console.log(`✗ ${comp}: falta dados/malha_${comp}.csv`); falhas++; continue; }
  const voos = csv(arqMalha).map((r) => ({ dia: +r.data.split("/")[0], min: +r.hora_min, ass: +r.assentos }));
  if (VOOS_ESPERADOS[comp] !== undefined && voos.length !== VOOS_ESPERADOS[comp]) {
    console.log(`✗ ${comp}: ${voos.length} voos, a tela mostrou ${VOOS_ESPERADOS[comp]}`); falhas++;
  }
  const [ano, mes] = comp.split("-").map(Number);
  const diasNoMes = new Date(Date.UTC(ano, mes, 0)).getUTCDate();

  // colMesCel, célula a célula, como o Power Fx
  const cel = [];
  for (let d = 1; d <= diasNoMes; d++) for (let h = 0; h < 24; h++) {
    const jI = h * 60, jF = jI + 60;
    let pax = 0, dec = 0;
    for (const v of voos) {
      if (v.dia === d || v.dia === d + 1) {
        const pos = v.min + (v.dia === d ? 0 : 1440);
        const a = Math.max(jI, pos - P.antec), b = Math.min(jF, pos);
        if (b > a) pax += (b - a) / Math.max(1, P.antec) * v.ass * P.ocup / 100;
      }
      if (v.dia === d && v.ass > P.assmin && v.min >= jI && v.min < jF) dec++;
    }
    const pedido = Math.max(teto(pax / P.cap), dec), mod = Math.min(pedido, P.raiosx);
    const apac = mod * P.apacMod + P.fixoA, sup = teto(mod / P.modSup) + P.fixoS;
    cel.push({ d, h, apac, sup, fA: Math.max(0, apac - escA[h]), fS: Math.max(0, sup - escS[h]) });
  }

  const envA = Array.from({ length: 24 }, (_, h) => Math.max(...cel.filter((c) => c.h === h).map((c) => c.apac)));
  const envS = Array.from({ length: 24 }, (_, h) => Math.max(...cel.filter((c) => c.h === h).map((c) => c.sup)));
  const porHora = (k) => Array.from({ length: 24 }, (_, h) => Math.max(...cel.filter((c) => c.h === h).map((c) => c[k])));
  const diasHora = (k) => Array.from({ length: 24 }, (_, h) => cel.filter((c) => c.h === h && c[k] > 0).length);
  const diasComFalta = (k) => new Set(cel.filter((c) => c[k] > 0).map((c) => c.d)).size;
  const pessoasA = turnos.filter((t) => t.papel === "APAC").reduce((a, t) => a + t.qtd, 0);
  const pessoasS = turnos.filter((t) => t.papel === "SUPERVISOR").reduce((a, t) => a + t.qtd, 0);
  const minA = minimo(envA), minS = minimo(envS);
  const veredito = (dias, pessoas, min) =>
    dias === 0 ? "COBRE O MÊS" : pessoas < min ? `CONTRATAR ${min - pessoas}` : "REPOSICIONAR TURNOS";

  console.log(`\n══ ${comp} · ${voos.length} voos · ${diasNoMes} dias`);
  console.log(`APAC: ${pessoasA} em escala · mínimo ${minA} · ${diasComFalta("fA")} dia(s) com falta → ${veredito(diasComFalta("fA"), pessoasA, minA)}`);
  console.log(`SUP : ${pessoasS} em escala · mínimo ${minS} · ${diasComFalta("fS")} dia(s) com falta → ${veredito(diasComFalta("fS"), pessoasS, minS)}`);
  console.log(linha("hora", [...Array(24)].map((_, h) => hh(h))));
  console.log(linha("APAC exigido", envA));
  console.log(linha("APAC escalado", escA));
  console.log(linha("APAC maior falta", porHora("fA").map((v) => (v ? v : ""))));
  console.log(linha("APAC dias c/ falta", diasHora("fA").map((v) => (v ? v : ""))));
  console.log(linha("SUP exigido", envS));
  console.log(linha("SUP escalado", escS));
  console.log(linha("SUP maior falta", porHora("fS").map((v) => (v ? v : ""))));
  console.log(linha("SUP dias c/ falta", diasHora("fS").map((v) => (v ? v : ""))));
}
console.log(falhas ? `\n✗ ${falhas} conferência(s) falharam` : "\n✓ conferências passaram");
process.exit(falhas ? 1 : 0);
