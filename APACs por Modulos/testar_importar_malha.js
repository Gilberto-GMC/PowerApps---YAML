// testar_importar_malha.js — roda o Office Script importar_malha.ts FORA do Excel, contra o export
// real do Power BI, e compara o retorno com os CSVs de dados/ (a malha já conferida).
//
// Uso:  node testar_importar_malha.js "C:/Users/.../Downloads/DECOLAGENS (6).xlsx"
//
// Node 24 tira os tipos do .ts sozinho; o workbook do Excel é substituído por um objeto que só sabe
// devolver getValues().
//
// ⚠️ O export do Power BI grava as células SEM referência de coluna (<x:c> sem r="A1") e com texto
// embutido (inlineStr), sem sharedStrings.xml. Leitor genérico de xlsx não acha linha nenhuma nele —
// este lê por posição, que é como o Excel entrega ao script.

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const ARQ = process.argv[2];
if (!ARQ) { console.error('uso: node testar_importar_malha.js "DECOLAGENS.xlsx"'); process.exit(2); }
const AQUI = __dirname;

// ---------------------------------------------------------------- xlsx cru
function lerZip(caminho) {
  const buf = fs.readFileSync(caminho);
  const arquivos = {};
  let i = 0;
  while ((i = buf.indexOf(Buffer.from("PK\x03\x04"), i)) !== -1) {
    const metodo = buf.readUInt16LE(i + 8), tamComp = buf.readUInt32LE(i + 18);
    const tamNome = buf.readUInt16LE(i + 26), tamExtra = buf.readUInt16LE(i + 28);
    const nome = buf.slice(i + 30, i + 30 + tamNome).toString("utf8");
    const ini = i + 30 + tamNome + tamExtra;
    if (tamComp > 0) {
      const d = buf.slice(ini, ini + tamComp);
      try { arquivos[nome] = metodo === 0 ? d.toString("utf8") : zlib.inflateRawSync(d).toString("utf8"); } catch { }
    }
    i = ini + tamComp;
  }
  return arquivos;
}
const des = (s) => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"')
  .replace(/&apos;/g, "'").replace(/&#(\d+);/g, (m, d) => String.fromCharCode(+d)).replace(/&amp;/g, "&");

const z = lerZip(ARQ);
const nomeAba = Object.keys(z).filter((k) => /^xl\/worksheets\/sheet\d+\.xml$/.test(k)).sort()[0];
const xml = z[nomeAba];
const dados = [];
for (const r of xml.matchAll(/<(?:x:)?row\b[^>]*?(?:\/>|>([\s\S]*?)<\/(?:x:)?row>)/g)) {
  const linha = [];
  for (const c of (r[1] || "").matchAll(/<(?:x:)?c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/(?:x:)?c>)/g)) {
    const attrs = c[1] || "", corpo = c[2] || "";
    if (/\br="/.test(attrs)) { console.error("este arquivo tem referência de coluna — use outro leitor"); process.exit(1); }
    const t = corpo.match(/<(?:x:)?t\b[^>]*>([\s\S]*?)<\/(?:x:)?t>/);
    const v = corpo.match(/<(?:x:)?v>([\s\S]*?)<\/(?:x:)?v>/);
    if (/t="inlineStr"/.test(attrs)) linha.push(t ? des(t[1]) : "");
    else if (v) linha.push(isNaN(Number(v[1])) ? des(v[1]) : Number(v[1]));
    else linha.push("");
  }
  dados.push(linha);
}
const largura = Math.max(...dados.map((l) => l.length));
dados.forEach((l) => { while (l.length < largura) l.push(""); });
console.log(`planilha: ${dados.length} linhas × ${largura} colunas (${nomeAba})`);

// ---------------------------------------------------------------- script
const tmp = path.join(require("os").tmpdir(), "importar_malha_sob_teste.ts");
fs.writeFileSync(tmp, fs.readFileSync(path.join(AQUI, "importar_malha.ts"), "utf8") + "\nmodule.exports = { main };\n");
const { main } = require(tmp);
const workbook = { getWorksheets: () => [{ getUsedRange: () => ({ getValues: () => dados }) }] };

let falhas = 0;
const confere = (rot, cond, det) => { console.log(`${cond ? "  ✓" : "  ✗"} ${rot}${det ? " — " + det : ""}`); if (!cond) falhas++; };

// ---------------------------------------------------------------- CSVs conferidos
const doCsv = [];
for (const f of fs.readdirSync(path.join(AQUI, "dados")).filter((x) => /^malha_.*\.csv$/.test(x))) {
  const ls = fs.readFileSync(path.join(AQUI, "dados", f), "utf8").replace(/^\uFEFF/, "").trim().split(/\r?\n/);
  const cab = ls[0].split(";");
  for (const l of ls.slice(1)) { const v = l.split(";"); const o = {}; cab.forEach((c, i) => (o[c] = v[i])); doCsv.push(o); }
}
const chave = (o) => [o.aeroporto, o.competencia, o.data, o.hora_min, o.empresa, o.voo, o.rota, o.aeronave,
  o.assentos, o.tipo_voo, o.dia_semana, o.ativo].map(String).join("|");
const isoParaBr = (iso) => iso.substring(8, 10) + "/" + iso.substring(5, 7) + "/" + iso.substring(0, 4);

// 1) descoberta
console.log("\n[1] mesRef vazio — descoberta");
let r = main(workbook, "");
confere("ok e sem registros", r.ok && r.registros.length === 0, r.mensagem);
confere("5 competências", r.competencias.length === 5, r.competencias.map((c) => c.competencia + "=" + c.voos).join(" "));
confere("filtro vazio (descoberta não apaga nada)", r.filtro === "");

// 2) TODAS
console.log("\n[2] mesRef TODAS");
r = main(workbook, "TODAS");
confere("ok", r.ok, r.mensagem);
confere("3.841 registros", r.registros.length === 3841, String(r.registros.length));
confere("total = registros", r.total === r.registros.length);
confere("2 linhas descartadas (rodapé do Power BI)", r.descartados === 2, String(r.descartados));
confere("filtro com as 5 competências", r.filtro ===
  "competencia eq '2026-10' or competencia eq '2026-11' or competencia eq '2026-12' or competencia eq '2027-01' or competencia eq '2027-02'", r.filtro);
const bolsa = new Map();
for (const o of doCsv) bolsa.set(chave(o), (bolsa.get(chave(o)) || 0) + 1);
let semPar = 0; const exemplos = [];
for (const x of r.registros) {
  const k = chave(Object.assign({}, x, { data: isoParaBr(x.data) }));
  const n = bolsa.get(k) || 0;
  if (n > 0) bolsa.set(k, n - 1); else { semPar++; if (exemplos.length < 3) exemplos.push(k); }
}
const sobra = [...bolsa.values()].reduce((a, b) => a + b, 0);
confere("todo registro do script existe no CSV conferido, campo a campo", semPar === 0, semPar ? exemplos.join(" || ") : "");
confere("nenhuma linha do CSV ficou sem registro do script", sobra === 0, sobra ? sobra + " sobrando" : "");

// 3) um mês
console.log("\n[3] mesRef 2026-12");
r = main(workbook, "2026-12");
confere("814 registros", r.ok && r.registros.length === 814, r.mensagem);
confere("todos de 2026-12", r.registros.every((x) => x.competencia === "2026-12"));
confere("filtro só de dezembro — importar dezembro não apaga outubro", r.filtro === "competencia eq '2026-12'", r.filtro);

// 4) mês sem voos
console.log("\n[4] mesRef 2099-01");
r = main(workbook, "2099-01");
confere("recusa com mensagem, sem filtro", !r.ok && r.registros.length === 0 && r.filtro === "", r.mensagem);

// 5) competência mal escrita
console.log('\n[5] mesRef "12/2026"');
r = main(workbook, "12/2026");
confere("recusa antes de ler, sem filtro", !r.ok && r.filtro === "", r.mensagem);

// 6) aeroporto
console.log("\n[6] aeroporto informado pelo fluxo");
r = main(workbook, "2027-02", " navegantes ");
confere("normaliza para NAVEGANTES", r.aeroporto === "NAVEGANTES" && r.registros.every((x) => x.aeroporto === "NAVEGANTES"));

// 7) tamanho do retorno
console.log("\n[7] tamanho do retorno TODAS");
const kb = Buffer.byteLength(JSON.stringify(main(workbook, "TODAS"))) / 1024;
confere("abaixo de 5 MB", kb < 5 * 1024, kb.toFixed(0) + " KB");

console.log(falhas ? `\n✗ ${falhas} verificação(ões) falharam` : "\n✓ todas as verificações passaram");
process.exit(falhas ? 1 : 0);
