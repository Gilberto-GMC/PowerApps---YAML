// validar_json.js — gêmeo em Node do validar_json.py desta skill.
//
// Uso:  node validar_json.js arquivo.json [arquivo2.json ...]
//
// Existe porque a máquina do Douglas não tem Python, e o validador .py da skill
// nunca chegou a rodar sobre os JSON que eu gerei. As regras aqui são as MESMAS
// do .py — quando uma mudar lá, mude aqui.
//
// Não substitui o valida_lista.js da raiz: aquele confere a forma que o FLUXO aceita,
// este confere o contrato da skill. Rode os dois.

const fs = require("fs");

const NOME_LISTA = /^tb_[a-z][a-zA-Z0-9]*$/;
const INTERNAL = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const CHAVES = ["nomeLista", "descricao", "ocultarTitle", "colunas", "registrosIniciais", "validacaoLista"];
const TIPOS_OK = new Set(["Text", "Note", "Number", "DateTime"]);
const TIPOS_PROIBIDOS = new Set(["Choice", "MultiChoice", "User", "UserMulti", "Boolean", "Lookup",
  "LookupMulti", "Currency", "TaxonomyFieldType", "Calculated"]);
const MAX_INDICES = 20;
const NATIVAS = new Set(["id", "created", "modified", "author", "editor", "title"]);

const verdadeiro = (v) => ["TRUE", "1"].includes(String(v == null ? "" : v).trim().toUpperCase());

// Leitor de <Field ...> suficiente para o que a regra precisa: atributos da tag raiz
// e o elemento <Validation>. Não é um parser de XML completo — e confere se fecha.
function leField(xml) {
  const raiz = xml.match(/^<Field\b([^>]*?)(\/?)>/);
  if (!raiz) return { erro: "não começa com <Field ...>" };
  const autoFechado = raiz[2] === "/";
  const attrs = {};
  for (const m of raiz[1].matchAll(/([A-Za-z]+)\s*=\s*'([^']*)'|([A-Za-z]+)\s*=\s*"([^"]*)"/g)) {
    attrs[m[1] || m[3]] = m[2] !== undefined ? m[2] : m[4];
  }
  if (autoFechado) {
    if (xml.trim() !== raiz[0]) return { erro: "conteúdo depois de um <Field/> auto-fechado" };
    return { attrs, validacao: null };
  }
  if (!/<\/Field>$/.test(xml.trim())) return { erro: "não fecha com </Field>" };
  const interno = xml.slice(raiz[0].length, xml.lastIndexOf("</Field>"));
  // equilíbrio das tags filhas
  const pilha = [];
  for (const t of interno.matchAll(/<(\/?)([A-Za-z]+)([^>]*?)(\/?)>/g)) {
    if (t[4] === "/") continue;
    if (t[1] === "/") { if (pilha.pop() !== t[2]) return { erro: `tag </${t[2]}> sem abertura correspondente` }; }
    else pilha.push(t[2]);
  }
  if (pilha.length) return { erro: `tag <${pilha[pilha.length - 1]}> não fechada` };
  const v = interno.match(/<Validation\b([^>]*)>([\s\S]*?)<\/Validation>/);
  let validacao = null;
  if (v) {
    const va = {};
    for (const m of v[1].matchAll(/([A-Za-z]+)\s*=\s*'([^']*)'|([A-Za-z]+)\s*=\s*"([^"]*)"/g)) {
      va[m[1] || m[3]] = m[2] !== undefined ? m[2] : m[4];
    }
    validacao = { attrs: va, texto: v[2] };
  }
  return { attrs, validacao };
}

function validar(doc) {
  const erros = [];
  const e = (x) => erros.push(x);

  const faltando = CHAVES.filter((k) => !(k in doc));
  if (faltando.length) e(`propriedades ausentes: ${faltando.join(", ")}`);
  const extras = Object.keys(doc).filter((k) => !CHAVES.includes(k));
  if (extras.length) e(`propriedades não previstas: ${extras.join(", ")}`);
  const ordem = Object.keys(doc).filter((k) => CHAVES.includes(k));
  const esperada = CHAVES.filter((k) => k in doc);
  if (ordem.join(",") !== esperada.join(",")) e(`propriedades fora da ordem do contrato: ${ordem.join(", ")}`);

  if (!NOME_LISTA.test(String(doc.nomeLista || ""))) {
    e(`nomeLista '${doc.nomeLista}' deve começar com tb_ e seguir camelCase sem acento/espaço/hífen`);
  }
  if (doc.ocultarTitle !== true) e("ocultarTitle deve ser exatamente true");
  if (typeof doc.descricao !== "string" || !doc.descricao.trim()) e("descricao deve ser um texto não vazio");

  const colunas = doc.colunas;
  if (!Array.isArray(colunas) || !colunas.length) { e("colunas deve ser uma lista não vazia"); return erros; }

  const nomes = [];
  let indices = 0;

  colunas.forEach((col, i) => {
    let rot = `colunas[${i}]`;
    if (typeof col !== "object" || col === null) { e(`${rot}: deve ser um objeto`); return; }
    const sobra = Object.keys(col).filter((k) => !["internalName", "schemaXml"].includes(k));
    if (sobra.length) e(`${rot}: propriedades não previstas: ${sobra.join(", ")}`);

    const interno = col.internalName || "";
    rot = `coluna '${interno || i}'`;
    if (!INTERNAL.test(String(interno))) e(`${rot}: internalName fora do padrão minúsculo snake_case`);
    if (NATIVAS.has(String(interno).toLowerCase())) e(`${rot}: duplica coluna nativa do SharePoint`);
    if (nomes.includes(interno)) e(`${rot}: internalName duplicado`);
    nomes.push(interno);

    const xml = col.schemaXml || "";
    if (xml.includes("Title")) e(`${rot}: schemaXml não pode mencionar Title`);

    const f = leField(xml);
    if (f.erro) { e(`${rot}: schemaXml inválido (${f.erro})`); return; }

    for (const attr of ["DisplayName", "Name", "StaticName"]) {
      if (f.attrs[attr] !== interno) {
        e(`${rot}: ${attr}='${f.attrs[attr]}' deveria ser idêntico ao internalName '${interno}'`);
      }
    }

    const tipo = f.attrs.Type;
    if (TIPOS_PROIBIDOS.has(tipo)) e(`${rot}: tipo ${tipo} é proibido`);
    else if (!TIPOS_OK.has(tipo)) e(`${rot}: tipo '${tipo}' não permitido (use Text, Note, Number ou DateTime)`);

    if (f.attrs.Group !== "AirportNow") e(`${rot}: Group deve ser 'AirportNow'`);
    if (f.attrs.Required === undefined) e(`${rot}: Required não declarado`);

    const indexado = verdadeiro(f.attrs.Indexed || "FALSE");
    if (indexado) indices++;

    if (tipo === "Text" && !f.attrs.MaxLength) e(`${rot}: campo Text sem MaxLength`);
    if (tipo === "Note") {
      if (verdadeiro(f.attrs.RichText || "FALSE")) e(`${rot}: Note deve usar RichText='FALSE'`);
      if (verdadeiro(f.attrs.AppendOnly || "FALSE")) e(`${rot}: Note deve usar AppendOnly='FALSE'`);
      if (indexado) e(`${rot}: campo Note nunca pode ser indexado`);
    }
    if (tipo === "Number" && f.attrs.Decimals === undefined) e(`${rot}: campo Number sem Decimals`);
    if (tipo === "DateTime" && !["DateTime", "DateOnly"].includes(f.attrs.Format)) {
      e(`${rot}: DateTime precisa de Format='DateTime' ou 'DateOnly'`);
    }

    if (f.validacao) {
      const texto = (f.validacao.texto || "").trim();
      if (!texto.startsWith("=")) e(`${rot}: <Validation> precisa de uma fórmula começando com '='`);
      if (!String(f.validacao.attrs.Message || "").trim()) e(`${rot}: <Validation> sem atributo Message`);
      const fora = [...new Set([...texto.matchAll(/\[([^\]]+)\]/g)].map((m) => m[1]))].filter((r) => r !== interno);
      if (fora.length) {
        e(`${rot}: <Validation> referencia outra coluna (${fora.sort().join(", ")}) — regra entre colunas vai em validacaoLista`);
      }
    }
  });

  const val = doc.validacaoLista;
  if (typeof val !== "object" || val === null || Array.isArray(val)) {
    e("validacaoLista deve ser um objeto (use {} quando não houver regra)");
  } else if (Object.keys(val).length) {
    const sobra = Object.keys(val).filter((k) => !["formula", "mensagem"].includes(k));
    if (sobra.length) e(`validacaoLista: propriedades não previstas: ${sobra.join(", ")}`);
    const formula = String(val.formula || "");
    if (!formula.startsWith("=")) e("validacaoLista.formula deve começar com '='");
    if (!String(val.mensagem || "").trim()) e("validacaoLista: fórmula sem mensagem");
    const refs = [...formula.matchAll(/\[([^\]]+)\]/g)].map((m) => m[1]);
    for (const r of refs) if (!nomes.includes(r)) e(`validacaoLista.formula referencia a coluna '${r}', que não está em colunas`);
    if (new Set(refs).size < 2) {
      e("validacaoLista deve cruzar duas colunas — regra de uma coluna só vai no <Validation> do próprio schemaXml");
    }
  }

  if (indices > MAX_INDICES) e(`${indices} colunas indexadas — o SharePoint permite no máximo ${MAX_INDICES}`);

  const registros = doc.registrosIniciais;
  if (!Array.isArray(registros)) e("registrosIniciais deve ser uma lista (use [] quando não houver)");
  else {
    registros.forEach((reg, i) => {
      if (typeof reg !== "object" || reg === null) { e(`registrosIniciais[${i}]: deve ser um objeto`); return; }
      for (const [chave, valor] of Object.entries(reg)) {
        if (!nomes.includes(chave)) e(`registrosIniciais[${i}]: coluna '${chave}' não declarada em colunas`);
        if (typeof valor === "boolean") e(`registrosIniciais[${i}].${chave}: use 1 ou 0, nunca true/false`);
      }
    });
  }
  return erros;
}

const arquivos = process.argv.slice(2);
if (!arquivos.length) {
  console.error("uso: node validar_json.js arquivo.json [...]");
  process.exit(2);
}
let falhou = false;
for (const a of arquivos) {
  let doc;
  try {
    doc = JSON.parse(fs.readFileSync(a, "utf8"));
  } catch (exc) {
    console.log(`✗ ${a} — JSON inválido: ${exc.message}`);
    falhou = true;
    continue;
  }
  const erros = validar(doc);
  if (erros.length) {
    falhou = true;
    console.log(`✗ ${a} — ${erros.length} problema(s):`);
    for (const x of erros) console.log(`   ${x}`);
  } else {
    console.log(`✓ ${a}`);
  }
}
process.exit(falhou ? 1 : 0);
