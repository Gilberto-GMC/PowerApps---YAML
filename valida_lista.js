// valida_lista.js — confere um JSON de definição de lista contra a forma que o fluxo
// "Gerador de lista" aceita, ANTES de submetê-lo.
// Uso: node valida_lista.js "Mapa de Alocação"/lista_*.json
//
// Existe porque o gerador rejeita com "ValidationFailed. The schema validation failed."
// e não diz qual campo — o que transforma um erro de uma linha numa caça ao tesouro.
// Cada regra aqui saiu de um JSON que funcionou, não de suposição sobre o schema.

const fs = require("fs");

// Chaves da raiz e seus tipos. `validacaoLista` é objeto SEMPRE — `{}` quando não há
// validação. `null` reprova (09/09/2026: foi exatamente isso que derrubou a tb_exportacaoMapa).
const RAIZ = {
  nomeLista: "string",
  descricao: "string",
  ocultarTitle: "boolean",
  colunas: "array",
  registrosIniciais: "array",
  validacaoLista: "object",
};

const tipoDe = (v) => (Array.isArray(v) ? "array" : v === null ? "null" : typeof v);

function analisa(arquivo) {
  const erros = [];
  const avisos = [];
  let j;
  try {
    j = JSON.parse(fs.readFileSync(arquivo, "utf8"));
  } catch (e) {
    return { erros: ["JSON inválido: " + e.message], avisos: [] };
  }

  for (const [k, t] of Object.entries(RAIZ)) {
    if (!(k in j)) erros.push(`falta a chave '${k}'`);
    else if (tipoDe(j[k]) !== t) erros.push(`'${k}' é ${tipoDe(j[k])}, deveria ser ${t}` + (j[k] === null ? " (use {} em vez de null)" : ""));
  }
  for (const k of Object.keys(j)) if (!(k in RAIZ)) avisos.push(`chave '${k}' não é conhecida pelo gerador`);

  if (Array.isArray(j.colunas)) {
    const vistos = new Set();
    j.colunas.forEach((c, i) => {
      const onde = `coluna[${i}]${c && c.internalName ? " '" + c.internalName + "'" : ""}`;
      if (!c || typeof c !== "object") return erros.push(`${onde}: não é objeto`);
      if (typeof c.internalName !== "string" || !c.internalName) return erros.push(`${onde}: internalName ausente`);
      if (typeof c.schemaXml !== "string" || !c.schemaXml) return erros.push(`${onde}: schemaXml ausente`);
      for (const k of Object.keys(c)) if (k !== "internalName" && k !== "schemaXml") avisos.push(`${onde}: chave extra '${k}'`);

      if (vistos.has(c.internalName)) erros.push(`${onde}: internalName repetido`);
      vistos.add(c.internalName);

      const x = c.schemaXml;
      if (!/^<Field\b/.test(x)) erros.push(`${onde}: schemaXml não começa com <Field`);
      if (!(x.endsWith("/>") || x.endsWith("</Field>"))) erros.push(`${onde}: schemaXml não fecha`);
      // Só como delimitador de atributo. Dentro de <Validation> as aspas duplas são
      // legítimas: é assim que a fórmula do SharePoint escreve literal de texto.
      const semValidacao = x.replace(new RegExp("<Validation[^]*?</Validation>", "g"), "");
      const attrsAspas = semValidacao.match(new RegExp('[A-Za-z]+="', "g")) || [];
      if (attrsAspas.length) erros.push(`${onde}: ${attrsAspas.length} atributo(s) com aspas duplas (${attrsAspas.join(" ")}) — o padrão do projeto é apóstrofo`);

      for (const attr of ["Type", "DisplayName", "Name", "StaticName", "Required"]) {
        if (!new RegExp(`\\b${attr}='`).test(x)) erros.push(`${onde}: falta o atributo ${attr}`);
      }
      for (const attr of ["Name", "StaticName"]) {
        const m = x.match(new RegExp(`\\b${attr}='([^']*)'`));
        if (m && m[1] !== c.internalName) erros.push(`${onde}: ${attr}='${m[1]}' não bate com o internalName`);
      }
      const tipo = (x.match(/\bType='([^']*)'/) || [])[1];
      if (tipo === "Number" && /<Default>([^<]*)<\/Default>/.test(x)) {
        const d = x.match(/<Default>([^<]*)<\/Default>/)[1];
        if (d.trim() === "" || isNaN(Number(d))) erros.push(`${onde}: <Default>${d}</Default> não é número`);
      }
      // Coluna obrigatória sem Default é armadilha para o fluxo, que precisa reenviar
      // todo campo obrigatório em cada Atualizar item.
      if (/Required='TRUE'/.test(x) && !/<Default>/.test(x) && tipo !== "Text" && tipo !== "DateTime") {
        avisos.push(`${onde}: obrigatória e sem <Default>`);
      }
    });

    const obrig = j.colunas.filter((c) => /Required='TRUE'/.test(c.schemaXml || "")).map((c) => c.internalName);
    if (obrig.length > 5) {
      avisos.push(`${obrig.length} colunas obrigatórias (${obrig.join(", ")}) — cada Atualizar item do fluxo terá que reenviar todas`);
    }
  }

  return { erros, avisos };
}

let falhou = false;
for (const a of process.argv.slice(2)) {
  const r = analisa(a);
  if (r.erros.length) {
    falhou = true;
    console.log(`\n✗ ${a} — ${r.erros.length} problema(s)`);
    r.erros.forEach((e) => console.log("   " + e));
  } else {
    console.log(`✓ ${a}`);
  }
  if (r.avisos.length) {
    console.log(`  ⚠ ${r.avisos.length} aviso(s)`);
    r.avisos.forEach((e) => console.log("     " + e));
  }
}
process.exit(falhou ? 1 : 0);
