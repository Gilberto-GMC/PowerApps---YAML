// escala_do_escopo.js — converte a escala 6x2 do "Escopo NVT Verão 2027.xlsx" em turnos da tb_apacEscala
// e confere a regra de cobertura que a tela scrApacEscala usa.
//
// Uso:  node escala_do_escopo.js "C:/Users/.../Downloads/Escopo NVT Verão 2027.xlsx"
// Saída: dados/escala_escopo_AAAA-MM.csv, um por competência da temporada (colar em tb_apacEscala no modo
//        de grade, ou cadastrar pela tela)
//
// A PROVA. A cobertura hora a hora é calculada com a MESMA regra da tela (função cobre(), abaixo — gêmea
// da fórmula do btnCalcEsc) e comparada com as linhas de total da própria planilha:
//   APAC  = linha 56 (TOTAL APAC 8HRS) + linhas 48–55 (posto de vigilância)
//   SUPER = linha 58 (TOTAL SUPERVISORES)
// Se não bater hora a hora, nada é gravado. Assim a regra da tela é testada contra a planilha antes de
// virar Power Fx, e os turnos gerados são provadamente a escala da planilha.
//
// A REGRA DE COBERTURA (hora cheia, como a planilha):
//   o turno conta na hora h se a hora INTEIRA está dentro da presença (início até início + duração,
//   atravessando a meia-noite) e NÃO encosta no intervalo.
//
// Leitura da planilha pela LETRA da coluna contra a régua da linha 3 (C = 00h … Z = 23h). Ler por posição
// deslocou uma série inteira em 11/09/2026 — ver CONTRATACAO_APAC.md §5.

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const ARQ = process.argv[2];
if (!ARQ) { console.error('uso: node escala_do_escopo.js "Escopo NVT Verão 2027.xlsx"'); process.exit(2); }
const COMPETENCIAS = ["2026-10", "2026-11", "2026-12", "2027-01", "2027-02"];
const AEROPORTO = "NAVEGANTES";

// ---------------------------------------------------------------- xlsx
function lerZip(c) {
  const b = fs.readFileSync(c); const a = {}; let i = 0;
  while ((i = b.indexOf(Buffer.from("PK\x03\x04"), i)) !== -1) {
    const m = b.readUInt16LE(i + 8), tc = b.readUInt32LE(i + 18), tn = b.readUInt16LE(i + 26), te = b.readUInt16LE(i + 28);
    const n = b.slice(i + 30, i + 30 + tn).toString("utf8"); const ini = i + 30 + tn + te;
    if (tc > 0) { const d = b.slice(ini, ini + tc); try { a[n] = m === 0 ? d.toString("utf8") : zlib.inflateRawSync(d).toString("utf8"); } catch { } }
    i = ini + tc;
  }
  return a;
}
const z = lerZip(ARQ);
const shared = [...(z["xl/sharedStrings.xml"] || "").matchAll(/<si>([\s\S]*?)<\/si>/g)]
  .map((m) => [...m[1].matchAll(/<t[^>]*>([\s\S]*?)<\/t>/g)].map((x) => x[1]).join(""));
const linhas = {};
for (const lm of z["xl/worksheets/sheet1.xml"].matchAll(/<row[^>]*r="(\d+)"[^>]*>([\s\S]*?)<\/row>/g)) {
  const cel = {};
  for (const cm of lm[2].matchAll(/<c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/c>)/g)) {
    if (cm[2] === undefined) continue;   // célula vazia auto-fechada
    const ref = (cm[1].match(/r="([A-Z]+)\d+"/) || [])[1];
    const v = (cm[2].match(/<v>([\s\S]*?)<\/v>/) || [])[1];
    if (!ref || v === undefined) continue;
    cel[ref] = /t="s"/.test(cm[1]) ? shared[+v] : parseFloat(v);
  }
  linhas[+lm[1]] = cel;
}
const regua = {};
for (const [ref, v] of Object.entries(linhas[3])) { const h = Math.round(v * 24); if (typeof v === "number" && h >= 0 && h <= 23) regua[ref] = h; }
const COLS = Object.keys(regua);
if (COLS.length !== 24) { console.error("régua da linha 3 não tem 24 horas"); process.exit(1); }
const serie = (n) => { const s = Array(24).fill(0); for (const c of COLS) if (linhas[n] && typeof linhas[n][c] === "number") s[regua[c]] = linhas[n][c]; return s; };
const somaLinhas = (de, ate) => { const s = Array(24).fill(0); for (let n = de; n <= ate; n++) serie(n).forEach((v, h) => (s[h] += v)); return s; };

// ---------------------------------------------------------------- turnos
function papelDe(rotulo) {
  const r = String(rotulo || "").toLowerCase();
  if (r.startsWith("apac 8")) return "APAC";
  if (r.startsWith("supervisor")) return "SUPERVISOR";
  if (r.includes("vigil")) return "VIGILANCIA";
  return null;
}
const hh = (h) => String(h).padStart(2, "0") + "h";
const turnos = [];
const problemas = [];
for (let n = 19; n <= 55; n++) {
  const papel = papelDe(linhas[n] && linhas[n].B);
  if (!papel) continue;
  const pres = serie(n);
  const horas = pres.map((v, h) => (v > 0 ? h : -1)).filter((h) => h >= 0);
  if (!horas.length) continue;                                   // turno vazio (ex.: vigilância 18h–00h)
  const qtd = Math.max(...pres);
  if (horas.some((h) => pres[h] !== qtd)) problemas.push(`linha ${n}: quantidade varia ao longo do turno`);
  const inicio = horas.find((h) => !horas.includes((h + 23) % 24));
  const dur = horas.length;
  for (let k = 0; k < dur; k++) if (!horas.includes((inicio + k) % 24)) problemas.push(`linha ${n}: presença não é contígua`);

  const rotuloBase = (papel === "APAC" ? "APAC" : papel === "SUPERVISOR" ? "Supervisor" : "Vigilância") +
    " " + hh(inicio) + "–" + hh((inicio + dur) % 24);
  const intervalo = linhas[n + 1] && String(linhas[n + 1].B || "").toLowerCase().includes("intervalo") ? serie(n + 1) : Array(24).fill(0);
  let resto = qtd;
  intervalo.forEach((v, h) => {
    if (v < 0) {
      if (!horas.includes(h)) problemas.push(`linha ${n + 1}: intervalo às ${hh(h)} fora da presença`);
      turnos.push({ papel, rotulo: rotuloBase + " (intervalo " + hh(h) + ")", ini: inicio * 60, dur: dur * 60, ii: h * 60, im: 60, qtd: -v, linha: n });
      resto += v;
    }
  });
  if (resto < 0) problemas.push(`linha ${n}: mais gente em intervalo do que no turno`);
  if (resto > 0) turnos.push({ papel, rotulo: rotuloBase + " (sem intervalo)", ini: inicio * 60, dur: dur * 60, ii: null, im: 0, qtd: resto, linha: n });
}

// ---------------------------------------------------------------- a regra da tela
function cobre(t, h) {
  const s = h * 60, fim = t.ini + t.dur;
  const presente = (s >= t.ini && s + 60 <= fim) || (s + 1440 >= t.ini && s + 1500 <= fim);
  const emIntervalo = t.ii !== null && t.im > 0 &&
    ((s < t.ii + t.im && s + 60 > t.ii) || (s + 1440 < t.ii + t.im && s + 1500 > t.ii));
  return presente && !emIntervalo;
}
const cobertura = (papeis) => Array.from({ length: 24 }, (_, h) =>
  turnos.filter((t) => papeis.includes(t.papel) && cobre(t, h)).reduce((a, t) => a + t.qtd, 0));

const planApac = serie(56).map((v, h) => v + somaLinhas(48, 55)[h]);
const planSup = serie(58);
const minhaApac = cobertura(["APAC", "VIGILANCIA"]);
const minhaSup = cobertura(["SUPERVISOR"]);

console.log(`turnos gerados: ${turnos.length} (${turnos.filter((t) => t.papel === "APAC").length} APAC, ` +
  `${turnos.filter((t) => t.papel === "SUPERVISOR").length} supervisor, ${turnos.filter((t) => t.papel === "VIGILANCIA").length} vigilância)`);
console.log(`pessoas em escala por dia: APAC ${turnos.filter((t) => t.papel === "APAC").reduce((a, t) => a + t.qtd, 0)}` +
  ` + vigilância ${turnos.filter((t) => t.papel === "VIGILANCIA").reduce((a, t) => a + t.qtd, 0)}` +
  ` · supervisores ${turnos.filter((t) => t.papel === "SUPERVISOR").reduce((a, t) => a + t.qtd, 0)}`);
console.log("\nhora            " + Array.from({ length: 24 }, (_, h) => String(h).padStart(3)).join(""));
console.log("APAC planilha   " + planApac.map((v) => String(v).padStart(3)).join(""));
console.log("APAC regra      " + minhaApac.map((v) => String(v).padStart(3)).join(""));
console.log("SUP  planilha   " + planSup.map((v) => String(v).padStart(3)).join(""));
console.log("SUP  regra      " + minhaSup.map((v) => String(v).padStart(3)).join(""));

const bateApac = planApac.every((v, h) => v === minhaApac[h]);
const bateSup = planSup.every((v, h) => v === minhaSup[h]);
console.log(`\n${bateApac ? "✓" : "✗"} cobertura de APAC igual à planilha nas 24 horas`);
console.log(`${bateSup ? "✓" : "✗"} cobertura de supervisores igual à planilha nas 24 horas`);
problemas.forEach((p) => console.log("✗ " + p));
if (!bateApac || !bateSup || problemas.length) { console.log("\nnada foi gravado"); process.exit(1); }

// ---------------------------------------------------------------- CSV
const dir = path.join(__dirname, "dados");
fs.mkdirSync(dir, { recursive: true });
const cab = "aeroporto;competencia;papel;rotulo;hora_inicio;duracao_min;intervalo_inicio;intervalo_min;quantidade;ordem;ativo";
for (const comp of COMPETENCIAS) {
  const corpo = turnos.map((t, i) => [AEROPORTO, comp, t.papel, t.rotulo, t.ini, t.dur, t.ii === null ? "" : t.ii, t.im, t.qtd, i + 1, 1].join(";"));
  fs.writeFileSync(path.join(dir, `escala_escopo_${comp}.csv`), "\uFEFF" + [cab].concat(corpo).join("\r\n") + "\r\n");
}
console.log(`\n✓ ${COMPETENCIAS.length} CSVs em dados/escala_escopo_AAAA-MM.csv, ${turnos.length} turnos cada`);
