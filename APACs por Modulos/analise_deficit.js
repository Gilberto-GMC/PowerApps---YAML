// analise_deficit.js — cruza a DEMANDA calculada da malha com a OFERTA da escala contratada,
// e diz em quais horas falta gente.
//
// Uso:
//   node analise_deficit.js "DECOLAGENS.xlsx" "Escopo NVT Verao 2027.xlsx"
//
// Responde a pergunta que originou o projeto: "precisamos contratar mais APACs, e em quais horários?"
//
// ⚠️ Lê o .xlsx direto do ZIP, sem biblioteca — esta máquina não tem Python nem pacote de planilha.
//
// ⚠️ ARMADILHA que custou uma leitura errada em 11/09/2026: célula vazia no meio da linha é
// gravada como `<c r="D20" s="5"/>` AUTO-FECHADA. Um regex que só casa `<c ...>...</c>` atravessa
// a célula vazia e atribui o valor da célula SEGUINTE à coluna errada — todo o resto da linha sai
// deslocado, sem erro nenhum. O parser aqui trata as duas formas, e o script CONFERE o próprio
// resultado contra as linhas de TOTAL da planilha antes de usar. Se a conferência falhar, ele para.

const fs = require("fs");
const zlib = require("zlib");

// ---------------------------------------------------------------- leitura de .xlsx (ZIP cru)
function lerZip(caminho) {
  const buf = fs.readFileSync(caminho);
  const arquivos = {};
  let i = 0;
  while ((i = buf.indexOf(Buffer.from("PK\x03\x04"), i)) !== -1) {
    const metodo = buf.readUInt16LE(i + 8);
    const tamComp = buf.readUInt32LE(i + 18);
    const tamNome = buf.readUInt16LE(i + 26);
    const tamExtra = buf.readUInt16LE(i + 28);
    const nome = buf.slice(i + 30, i + 30 + tamNome).toString("utf8");
    const ini = i + 30 + tamNome + tamExtra;
    if (tamComp > 0) {
      const dados = buf.slice(ini, ini + tamComp);
      try {
        arquivos[nome] = metodo === 0 ? dados.toString("utf8") : zlib.inflateRawSync(dados).toString("utf8");
      } catch { /* entrada ilegível: ignora */ }
    }
    i = ini + tamComp;
  }
  return arquivos;
}

function lerPlanilha(caminho) {
  const z = lerZip(caminho);
  const nomeAba = Object.keys(z).find((n) => /xl\/worksheets\/sheet1\.xml$/.test(n));
  if (!nomeAba) throw new Error(`${caminho}: não achei xl/worksheets/sheet1.xml`);
  const sh = z[nomeAba];
  const ssXml = z["xl/sharedStrings.xml"] || "";
  const strs = [...ssXml.matchAll(/<si>([\s\S]*?)<\/si>/g)]
    .map((m) => [...m[1].matchAll(/<t[^>]*>([\s\S]*?)<\/t>/g)].map((t) => t[1]).join(""));
  const px = /<x:row/.test(sh) ? "x:" : ""; // export do Power BI usa prefixo de namespace
  const linhas = {};
  const reLinha = new RegExp(`<${px}row([^>]*)>([\\s\\S]*?)</${px}row>`, "g");
  const reCel = new RegExp(`<${px}c ([^>]*?)/>|<${px}c ([^>]*?)>([\\s\\S]*?)</${px}c>`, "g");
  let n = 0;
  for (const r of sh.matchAll(reLinha)) {
    const rn = (r[1].match(/r="(\d+)"/) || [])[1];
    const num = rn ? +rn : ++n;
    const cel = {};
    let ordem = 0;
    for (const c of r[2].matchAll(reCel)) {
      const attrs = c[1] || c[2] || "";
      const inner = c[3];
      ordem++;
      if (inner === undefined) continue; // célula vazia auto-fechada: pula, mas já contou a posição
      const ref = (attrs.match(/r="([A-Z]+)\d+"/) || [])[1] || colDe(ordem);
      const t = (attrs.match(/\bt="([^"]+)"/) || [])[1];
      let v = (inner.match(new RegExp(`<${px}v>([\\s\\S]*?)</${px}v>`)) || [])[1];
      if (v === undefined) v = (inner.match(new RegExp(`<${px}t[^>]*>([\\s\\S]*?)</${px}t>`)) || [])[1];
      if (v === undefined) continue;
      cel[ref] = t === "s" ? strs[+v] : t === "inlineStr" ? v : Number(v);
    }
    linhas[num] = cel;
  }
  return linhas;
}

const colDe = (i) => {
  let s = "", n = i;
  while (n > 0) { const r = (n - 1) % 26; s = String.fromCharCode(65 + r) + s; n = Math.floor((n - 1) / 26); }
  return s;
};

// ---------------------------------------------------------------- premissas
const P = {
  capacidade: 185,      // pax por hora por módulo (TR)
  ocupacao: 0.85,       // dos assentos ofertados
  antecedencia: 90,     // minutos antes da decolagem em que o módulo abre
  assentosMin: 150,     // corte para contar decolagem
  apacPorModulo: 3,
  modulosPorSupervisor: 2,
  raiosX: 3,
  postosFixos: 5,       // Acesso C (3) + Portão Principal (1) + Apoio (1)
};
const teto = (x) => Math.floor(x) + (x > Math.floor(x) ? 1 : 0);
const COLS = "CDEFGHIJKLMNOPQRSTUVWXYZ".split("");

// ---------------------------------------------------------------- demanda, da malha
function demandaPorDia(linhas) {
  // Colunas do export do Power BI, por posição: A=horário (fração do dia), B=data (serial),
  // C=empresa, D=voo, E=rota, F=aeronave, G=assentos, H=tipo, I=dia da semana.
  // Endereça por LETRA e não por Object.values(): célula vazia no meio da linha não entra no
  // objeto, e a ordem dos valores deixaria de corresponder à ordem das colunas.
  const voos = [];
  for (const [n, cel] of Object.entries(linhas)) {
    if (+n === 1) continue;
    const hora = cel.A, data = cel.B, assentos = cel.G;
    if (typeof data !== "number" || typeof hora !== "number") continue;
    voos.push({ dia: data, min: Math.round(hora * 1440), assentos: Number(assentos) || 0 });
  }
  const dias = [...new Set(voos.map((v) => v.dia))].sort((a, b) => a - b);
  return { dias, porDia: dias.map((d) => umDia(voos, d)), voos };
}

function umDia(voos, d) {
  const fl = voos.filter((v) => v.dia === d || v.dia === d + 1)
    .map((v) => ({ off: v.min + (v.dia === d ? 0 : 1440), assentos: v.assentos }));
  return Array.from({ length: 24 }, (_, h) => {
    const ini = h * 60, fim = ini + 60;
    let pax = 0;
    for (const f of fl) {
      const a = Math.max(ini, f.off - P.antecedencia), b = Math.min(fim, f.off);
      if (b > a) pax += ((b - a) / P.antecedencia) * f.assentos * P.ocupacao;
    }
    const dec = fl.filter((f) => f.assentos > P.assentosMin && f.off >= ini && f.off < fim).length;
    const mod = Math.min(Math.max(teto(pax / P.capacidade), dec), P.raiosX);
    return { pax, mod, apac: mod * P.apacPorModulo + P.postosFixos, sup: teto(mod / P.modulosPorSupervisor) };
  });
}

// ---------------------------------------------------------------- oferta, da escala
// Estrutura do Escopo: pares de linhas (turno, "Efetivo em intervalo") em três blocos.
const BLOCOS = { apac8: [20, 39], superv: [40, 47], vigilancia: [48, 55] };
const TOTAIS = { apac8: 56, superv: 58, geral: 59 }; // linhas de conferência da própria planilha

function ofertaPorHora(linhas) {
  const soma = (a, b) => COLS.map((c) => {
    let s = 0;
    for (let r = a; r <= b; r++) { const v = linhas[r] && linhas[r][c]; if (typeof v === "number") s += v; }
    return s;
  });
  const lida = (r) => COLS.map((c) => { const v = linhas[r] && linhas[r][c]; return typeof v === "number" ? v : 0; });
  const apac8 = soma(...BLOCOS.apac8), superv = soma(...BLOCOS.superv), vigil = soma(...BLOCOS.vigilancia);

  // conferência obrigatória: meu somatório TEM que bater com as linhas de TOTAL da planilha
  const conferir = [["APAC 8h", apac8, lida(TOTAIS.apac8)], ["supervisores", superv, lida(TOTAIS.superv)],
                    ["total geral", COLS.map((_, h) => apac8[h] + superv[h] + vigil[h]), lida(TOTAIS.geral)]];
  const falhas = conferir.filter(([, meu, dela]) => !meu.every((v, i) => Math.abs(v - dela[i]) < 1e-9));
  if (falhas.length) {
    console.error("A leitura da escala NÃO bate com as linhas de TOTAL da planilha:");
    for (const [rot, meu, dela] of falhas) {
      console.error(`  ${rot}\n    lido    : ${meu.join(",")}\n    planilha: ${dela.join(",")}`);
    }
    console.error("Provável causa: o layout do Escopo mudou de linha. Ajuste BLOCOS/TOTAIS.");
    process.exit(1);
  }
  return { apac: COLS.map((_, h) => apac8[h] + vigil[h]), sup: superv };
}

// ---------------------------------------------------------------- relatório
function main() {
  const [malhaPath, escopoPath] = process.argv.slice(2);
  if (!malhaPath || !escopoPath) {
    console.error('uso: node analise_deficit.js "DECOLAGENS.xlsx" "Escopo NVT Verao 2027.xlsx"');
    process.exit(2);
  }
  const { dias, porDia } = demandaPorDia(lerPlanilha(malhaPath));
  const oferta = ofertaPorHora(lerPlanilha(escopoPath));
  console.log(`leitura da escala conferida contra os totais da própria planilha — ok`);
  console.log(`${dias.length} dias de malha · premissas: ${P.capacidade} pax/h · ${P.ocupacao * 100}% · ${P.antecedencia} min · corte ${P.assentosMin} assentos\n`);

  const maxA = Array.from({ length: 24 }, (_, h) => Math.max(...porDia.map((x) => x[h].apac)));
  const maxS = Array.from({ length: 24 }, (_, h) => Math.max(...porDia.map((x) => x[h].sup)));

  console.log("hora | oferta APAC | demanda máx | falta | dias com falta | superv (of/dem)");
  const criticas = [];
  for (let h = 0; h < 24; h++) {
    const falta = Math.max(0, maxA[h] - oferta.apac[h]);
    const nd = porDia.filter((x) => x[h].apac > oferta.apac[h]).length;
    const fs2 = Math.max(0, maxS[h] - oferta.sup[h]);
    if (falta || fs2) criticas.push({ h, falta, nd, fs2 });
    console.log(
      `${String(h).padStart(2, "0")}:00 |${String(oferta.apac[h]).padStart(12)} |${String(maxA[h]).padStart(12)} |` +
      `${String(falta).padStart(6)} |${String(`${nd}/${dias.length}`).padStart(15)} |` +
      `${String(`${oferta.sup[h]}/${maxS[h]}`).padStart(17)}${falta && nd > dias.length / 2 ? "  <<<" : ""}`
    );
  }

  const totOf = oferta.apac.reduce((a, b) => a + b, 0);
  const totDem = Math.max(...porDia.map((x) => x.reduce((a, y) => a + y.apac, 0)));
  console.log(`\nhomem-hora no dia — oferta ${totOf}, demanda no pior dia ${totDem} ` +
    `(${totOf >= totDem ? `sobram ${totOf - totDem}, então parte é distribuição` : `faltam ${totDem - totOf}`})`);

  const cronicas = criticas.filter((c) => c.nd > dias.length / 2);
  console.log("\nRESPOSTA");
  if (!cronicas.length) {
    console.log("  Nenhuma hora fica descoberta na maioria dos dias — não há contratação a fazer por este critério.");
  } else {
    const maxFaltaA = Math.max(...cronicas.map((c) => c.falta));
    const maxFaltaS = Math.max(...cronicas.map((c) => c.fs2));
    console.log(`  Falta gente em ${cronicas.map((c) => `${String(c.h).padStart(2, "0")}h`).join(" e ")} — ` +
      `na maioria dos dias da temporada.`);
    console.log(`  Contratar +${maxFaltaA} APAC e +${maxFaltaS} supervisor num turno que cubra essas horas.`);
    console.log(`  Com folguistas (1 para cada 3): +${maxFaltaA + teto(maxFaltaA / 3) + maxFaltaS + teto(maxFaltaS / 3)} pessoas no contrato.`);
  }
  const esporadicas = criticas.filter((c) => c.nd > 0 && c.nd <= dias.length / 2);
  if (esporadicas.length) {
    console.log(`\n  Horas com falta esporádica (não justificam contratação): ` +
      esporadicas.map((c) => `${String(c.h).padStart(2, "0")}h em ${c.nd} dia(s)`).join(", "));
  }
}

main();
