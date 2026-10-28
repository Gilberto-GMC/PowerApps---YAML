// Gera o Mapa_de_Alocacao_gerentes.pptx (10 slides, apresentação aos gerentes).
//
// Para rodar, fora do repositório, numa pasta com pptxgenjs instalado:
//   npm install pptxgenjs
//   NODE_PATH=<pasta>/node_modules node gerar_deck.js saida.pptx <caminho do apply_theme.js>
//
// O apply_theme.js vem da skill pptx do Claude Code e grava as cores do tema no arquivo;
// sem ele o deck sai com a paleta padrão do Office. O texto de fala de cada slide está
// nas anotações (slide.addNotes), e o roteiro impresso está no ROTEIRO_APRESENTACAO_GERENTES.md.

const pptxgen = require("pptxgenjs");

const THEME = {
  name: "ASUR Mapa de Alocação",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1E293B", lt1: "FFFFFF",
    dk2: "0A5A66", lt2: "F1F5F9",
    accent1: "0E7C8C", accent2: "0891B2", accent3: "B9D9DE",
    accent4: "DD511A", accent5: "16A34A", accent6: "64748B",
    hlink: "0E7C8C", folHlink: "64748B",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Douglas";
pres.company = "ASUR BRASIL";
pres.title = "Mapa de Alocação - AirportNow";
const C = pres.SchemeColor;

const W = 13.33, H = 7.5, M = 0.75, CW = W - 2 * M;
const TEAL = "0E7C8C", INK = "1E293B", GREY = "64748B", DEEP = "0F3F46";

/* ---------------- layouts ---------------- */
pres.defineSlideMaster({ title: "ESCURO", background: { color: C.text2 }, objects: [] });
pres.defineSlideMaster({
  title: "CONTEUDO",
  background: { color: C.background1 },
  objects: [
    { text: { text: "", options: { name: "title", placeholder: "title",
        x: M, y: 0.42, w: CW, h: 0.85, fontSize: 34, bold: true, color: C.text1, valign: "middle", margin: 0 } } },
    { text: { text: "Mapa de Alocação  ·  AirportNow", options: {
        x: M, y: H - 0.5, w: 7.5, h: 0.3, fontSize: 10, color: "94A3B8", valign: "middle", margin: 0 } } },
  ],
  slideNumber: { x: W - M - 0.8, y: H - 0.5, w: 0.8, h: 0.3, fontSize: 10, color: "94A3B8", align: "right" },
});

/* ---------------- helpers ---------------- */
function tx(slide, text, o) { slide.addText(text, Object.assign({ margin: 0, isTextBox: true }, o)); }
function ttl(slide, text) {
  slide.addText(text, { placeholder: "title", x: M, y: 0.42, w: CW, h: 0.85, fontSize: 34, bold: true, color: INK, valign: "middle", margin: 0 });
}
function card(slide, o) {
  slide.addShape(pres.ShapeType.roundRect, {
    x: o.x, y: o.y, w: o.w, h: o.h, rectRadius: 0.1,
    fill: { color: o.fill || "F1F5F9" }, line: { color: o.line || "E2E8F0", width: 1 }, objectName: o.name,
  });
}
function bola(slide, x, y, d, txt, bg, fg) {
  slide.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: bg || TEAL }, line: { color: bg || TEAL, width: 0 } });
  tx(slide, txt, { x, y, w: d, h: d, fontSize: d >= 0.6 ? 20 : 15, bold: true, color: fg || "FFFFFF", align: "center", valign: "middle" });
}
function pilula(slide, x, y, w, h, txt, cor) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: h / 2, fill: { color: cor }, line: { color: cor, width: 0 } });
  tx(slide, txt, { x, y, w, h, fontSize: 11, bold: true, color: "FFFFFF", align: "center", valign: "middle", charSpacing: 1 });
}
function demo(slide) { pilula(slide, W - M - 2.4, 0.62, 2.4, 0.44, "MOSTRAR NO APP", "DD511A"); }
function notas(slide, linhas) { slide.addNotes(linhas.join("\n")); }

let s;

/* 1 - CAPA */
pres.addSection({ title: "Abertura" });
s = pres.addSlide({ masterName: "ESCURO", sectionTitle: "Abertura" });
tx(s, "ASUR BRASIL  ·  AIRPORTNOW", { x: 1.1, y: 1.45, w: 8, h: 0.4, fontSize: 14, bold: true, color: "7FB3BC", charSpacing: 4 });
tx(s, "Mapa de Alocação", { x: 1.1, y: 2.3, w: 11.2, h: 1.6, fontSize: 60, bold: true, color: "FFFFFF", valign: "bottom" });
tx(s, "Reserva e controle do pátio da aviação geral, com voos internacionais", { x: 1.1, y: 4.1, w: 11.2, h: 0.9, fontSize: 24, color: "B9D9DE", valign: "top" });
tx(s, "Apresentação aos gerentes dos aeroportos", { x: 1.1, y: 6.2, w: 11.2, h: 0.45, fontSize: 14, color: "7FB3BC", valign: "middle" });
notas(s, [
  "Abertura, 1 min.",
  "",
  "Agradecer o tempo de todos.",
  "Dizer o objetivo: mostrar como a reserva de pátio da aviação geral passa a ser feita dentro do AirportNow, incluindo o agendamento dos voos internacionais com os órgãos.",
  "Já está rodando em Navegantes e em Foz do Iguaçu.",
]);

/* 2 - Como era e como fica */
pres.addSection({ title: "Aviação geral" });
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Aviação geral" });
ttl(s, "Reserva de aviação geral: como era e como fica");
const colW = (CW - 0.5) / 2;
const antes = [
  "Reserva anotada fora do mapa do pátio",
  "O turno seguinte depende do repasse",
  "Conflito de posição aparece quando a aeronave chega",
  "Aviso aos órgãos escrito do zero a cada voo",
  "Difícil saber quem reservou e quando",
];
const agora = [
  "Reserva lançada direto no mapa, pela matrícula",
  "Qualquer turno abre a tela e vê o que está reservado",
  "O app não aceita reserva em posição ocupada",
  "Aviso aos órgãos sai pronto a partir da reserva",
  "Fica registrado quem lançou e quando",
];
card(s, { x: M, y: 1.45, w: colW, h: 4.95, name: "antes" });
card(s, { x: M + colW + 0.5, y: 1.45, w: colW, h: 4.95, fill: "EAF5F6", line: "9FC9D0", name: "agora" });
tx(s, "ANTES", { x: M + 0.42, y: 1.72, w: colW - 0.8, h: 0.35, fontSize: 13, bold: true, color: GREY, charSpacing: 2 });
tx(s, "COM O MAPA DE ALOCAÇÃO", { x: M + colW + 0.92, y: 1.72, w: colW - 0.8, h: 0.35, fontSize: 13, bold: true, color: TEAL, charSpacing: 2 });
antes.forEach((t, i) => {
  const y = 2.35 + i * 0.78;
  s.addShape(pres.ShapeType.ellipse, { x: M + 0.44, y: y + 0.19, w: 0.16, h: 0.16, fill: { color: "CBD5E1" }, line: { color: "CBD5E1", width: 0 } });
  tx(s, t, { x: M + 0.78, y, w: colW - 1.15, h: 0.55, fontSize: 15.5, color: GREY, valign: "middle" });
});
agora.forEach((t, i) => {
  const y = 2.35 + i * 0.78, x0 = M + colW + 0.5;
  s.addShape(pres.ShapeType.ellipse, { x: x0 + 0.44, y: y + 0.19, w: 0.16, h: 0.16, fill: { color: TEAL }, line: { color: TEAL, width: 0 } });
  tx(s, t, { x: x0 + 0.78, y, w: colW - 1.15, h: 0.55, fontSize: 15.5, bold: true, color: INK, valign: "middle" });
});
notas(s, [
  "Como era e como fica, 2 a 3 min.",
  "",
  "Perguntar para a sala como cada aeroporto controla hoje a reserva de AG. Deixar um ou dois responderem.",
  "Depois ler a coluna da direita, sem pressa.",
  "Pontos para reforçar: todo mundo vê a mesma reserva, o app barra a posição ocupada, e o aviso aos órgãos sai pronto.",
]);

/* 3 - Fazendo a reserva */
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Aviação geral" });
ttl(s, "Fazendo uma reserva");
demo(s);
const passos = [
  { t: "Matrícula", d: "O app já sugere o equipamento da aeronave" },
  { t: "Posição e horários", d: "Data e hora de entrada e de saída" },
  { t: "Internacional ou alternativa", d: "Só marcar, quando for o caso" },
  { t: "Salvar", d: "A reserva já aparece na grade e no painel de reservas" },
];
const pw = (CW - 3 * 0.4) / 4;
passos.forEach((p, i) => {
  const x = M + i * (pw + 0.4);
  card(s, { x, y: 1.55, w: pw, h: 2.75, name: "passo" + i });
  bola(s, x + 0.32, 1.85, 0.58, String(i + 1));
  tx(s, p.t, { x: x + 0.32, y: 2.62, w: pw - 0.6, h: 0.7, fontSize: 17, bold: true, color: INK, valign: "top" });
  tx(s, p.d, { x: x + 0.32, y: 3.3, w: pw - 0.6, h: 0.85, fontSize: 13.5, color: GREY, valign: "top" });
  if (i < 3) s.addShape(pres.ShapeType.rightArrow, { x: x + pw + 0.07, y: 2.8, w: 0.26, h: 0.26, fill: { color: "B9D9DE" }, line: { color: "B9D9DE", width: 0 } });
});
card(s, { x: M, y: 4.65, w: CW, h: 1.7, fill: "EAF5F6", line: "9FC9D0", name: "conflito" });
tx(s, "E se a posição já estiver ocupada?", { x: M + 0.45, y: 4.85, w: CW - 0.9, h: 0.45, fontSize: 19, bold: true, color: TEAL });
tx(s, "O app não grava. Ele mostra qual reserva ou voo está ocupando a posição naquele horário, para o operador escolher outra.",
  { x: M + 0.45, y: 5.35, w: CW - 0.9, h: 0.8, fontSize: 15.5, color: DEEP });
notas(s, [
  "Fazendo uma reserva, 4 min. Mostrar no app.",
  "",
  "Abrir Navegantes, Mapa do Dia.",
  "Criar uma reserva com a matrícula de teste. Mostrar o equipamento sugerido.",
  "Escolher posição, entrada e saída. Salvar.",
  "Mostrar o bloco aparecendo na grade.",
  "",
  "Depois tentar outra reserva na mesma posição e horário. O app recusa e mostra quem está lá. Esse é o ponto principal da demo.",
  "",
  "Lembrar de apagar as reservas de teste no fim.",
]);

/* 4 - Controle das reservas */
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Aviação geral" });
ttl(s, "Acompanhando o pátio");
demo(s);
const ctrl = [
  { t: "Painel de reservas", d: "Todas as reservas futuras em uma lista, separadas por mês, com o dia de hoje destacado." },
  { t: "Filtro por situação", d: "Para ver só o que está previsto, no pátio ou finalizado." },
  { t: "Ir ao dia", d: "Da lista para a grade daquele dia com um clique." },
  { t: "NO PÁTIO", d: "Quando a aeronave chega, o bloco muda e todo mundo fica sabendo." },
  { t: "Matrícula fora do padrão", d: "O app avisa quando o prefixo parece digitado errado, sem impedir de salvar." },
  { t: "Hangar", d: "Aeronave no hangar com painel próprio, entrada e saída registradas." },
];
const cw2 = (CW - 0.35) / 2;
ctrl.forEach((c, i) => {
  const x = M + (i % 2) * (cw2 + 0.35), y = 1.5 + Math.floor(i / 2) * 1.62;
  card(s, { x, y, w: cw2, h: 1.42, name: "ctrl" + i });
  s.addShape(pres.ShapeType.ellipse, { x: x + 0.38, y: y + 0.32, w: 0.2, h: 0.2, fill: { color: TEAL }, line: { color: TEAL, width: 0 } });
  tx(s, c.t, { x: x + 0.78, y: y + 0.2, w: cw2 - 1.1, h: 0.44, fontSize: 17, bold: true, color: INK, valign: "middle" });
  tx(s, c.d, { x: x + 0.78, y: y + 0.66, w: cw2 - 1.1, h: 0.62, fontSize: 13.5, color: GREY, valign: "top" });
});
notas(s, [
  "Acompanhando o pátio, 3 min. Mostrar no app.",
  "",
  "Abrir o painel RESERVAS DE PÁTIO.",
  "Mostrar a separação por mês e o HOJE em destaque.",
  "Usar o filtro de situação.",
  "Clicar em IR AO DIA numa reserva.",
  "Se tiver alguma aeronave no pátio, mostrar o NO PÁTIO no bloco.",
  "Mostrar rápido o painel do hangar.",
]);

/* 5 - Voo internacional */
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Aviação geral" });
ttl(s, "Voo internacional");
demo(s);
const lw = 5.9;
const intl = [
  { t: "Chegada ou saída", d: "Escolhe o sentido e o texto se ajusta." },
  { t: "Dados que já estão na reserva", d: "Aeronave, matrícula, operador, data e horário entram sozinhos." },
  { t: "O que falta, preenche ali mesmo", d: "Horário da imigração, procedência ou destino, tripulantes e passageiros." },
  { t: "Pronto para enviar", d: "Cartão para print ou texto para copiar. Depois de enviado, a reserva fica marcada." },
];
intl.forEach((it, i) => {
  const y = 1.5 + i * 1.22;
  bola(s, M, y + 0.05, 0.5, String(i + 1));
  tx(s, it.t, { x: M + 0.75, y, w: lw - 0.8, h: 0.42, fontSize: 17, bold: true, color: INK, valign: "middle" });
  tx(s, it.d, { x: M + 0.75, y: y + 0.44, w: lw - 0.8, h: 0.66, fontSize: 13.5, color: GREY, valign: "top" });
});
// cartao ilustrativo
const cx = M + lw + 0.5, cwid = W - M - cx;
card(s, { x: cx, y: 1.45, w: cwid, h: 5.0, fill: "FFFFFF", line: "CBD5E1", name: "cartao" });
s.addShape(pres.ShapeType.rect, { x: cx + 0.02, y: 1.47, w: cwid - 0.04, h: 0.95, fill: { color: TEAL }, line: { color: TEAL, width: 0 } });
tx(s, "SOLICITAÇÃO DE AGENDAMENTO COM OS ÓRGÃOS FEDERAIS", { x: cx + 0.35, y: 1.55, w: cwid - 0.7, h: 0.4, fontSize: 11.5, bold: true, color: "FFFFFF", valign: "middle" });
tx(s, "CHEGADA INTERNACIONAL  ·  Navegantes (SBNF)", { x: cx + 0.35, y: 1.95, w: cwid - 0.7, h: 0.38, fontSize: 13, color: "D7ECEF", valign: "middle" });
const linhas = [
  ["AERONAVE", "Cessna Citation, matrícula PR-ABC"],
  ["CHEGADA", "Sexta, 13/11  ·  imigração às 14:30"],
  ["PROCEDÊNCIA", "Punta del Este"],
  ["DESEMBARQUE", "2 tripulantes e 4 passageiros"],
];
linhas.forEach(([r, v], i) => {
  const y = 2.7 + i * 0.82;
  tx(s, r, { x: cx + 0.35, y, w: cwid - 0.7, h: 0.3, fontSize: 10.5, bold: true, color: GREY, charSpacing: 1.5 });
  tx(s, v, { x: cx + 0.35, y: y + 0.3, w: cwid - 0.7, h: 0.38, fontSize: 15, bold: true, color: INK });
});
tx(s, "exemplo ilustrativo", { x: cx + 0.35, y: 6.0, w: cwid - 0.7, h: 0.3, fontSize: 10, italic: true, color: "94A3B8", align: "right" });
notas(s, [
  "Voo internacional, 5 min. Mostrar no app. É a parte que mais interessa a eles.",
  "",
  "Abrir uma reserva marcada como internacional e clicar em AVISO.",
  "Trocar entre chegada e saída e mostrar o texto mudando.",
  "Preencher imigração, procedência, tripulantes e passageiros.",
  "Mostrar o cartão e o TIRAR PRINT.",
  "Comentar que o mesmo vale para aeronave saindo do hangar.",
  "",
  "Se perguntarem: o cabeçalho da grade mostra quantos internacionais tem no dia.",
]);

/* 6 - Regras do patio */
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Aviação geral" });
ttl(s, "Regras que o app aplica nas reservas");
const RED = ["B91C1C", "FEF2F2", "FCA5A5", "NÃO DEIXA"];
const BLK = ["0A5A66", "EAF5F6", "9FC9D0", "BLOQUEIA AS VIZINHAS"];
const AMB = ["B45309", "FFFBEB", "FCD34D", "PEDE CONFIRMAÇÃO"];
const regras = [
  ["Reservar posição já ocupada no mesmo horário", RED],
  ["Aeronave mais comprida do que a posição aceita", RED],
  ["Reservar posição interditada", RED],
  ["Aeronave grande que ocupa mais do que o próprio box", BLK],
  ["Envergadura acima do limite da posição", AMB],
  ["Reserva de alternativa no mesmo box de outra", AMB],
];
regras.forEach(([t, k], i) => {
  const y = 1.45 + i * 0.78;
  card(s, { x: M, y, w: CW, h: 0.64, fill: k[1], line: k[2], name: "regra" + i });
  tx(s, t, { x: M + 0.42, y, w: 8.4, h: 0.64, fontSize: 16, color: INK, valign: "middle" });
  pilula(s, W - M - 2.75, y + 0.13, 2.4, 0.38, k[3], k[0]);
});
tx(s, "As medidas e os bloqueios vêm do cadastro de cada aeroporto.",
  { x: M, y: 6.25, w: CW, h: 0.45, fontSize: 14.5, italic: true, color: GREY });
notas(s, [
  "Regras, 3 min.",
  "",
  "Passar linha a linha.",
  "Bloqueia as vizinhas: quando entra uma aeronave grande, as posições ao lado aparecem como INDISPONÍVEL na grade. Ninguém precisa lembrar.",
  "Alternativa: a aeronave que só vem se precisar desviar. O app não trava o box por causa dela, só avisa e o supervisor decide. Voo confirmado tem prioridade.",
  "Fechar dizendo que cada aeroporto cadastra as próprias medidas e restrições.",
]);

/* 7 - Voo regular */
pres.addSection({ title: "Voo regular" });
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Voo regular" });
ttl(s, "O voo regular fica no mesmo mapa");
const hw = (CW - 0.4) / 2;
card(s, { x: M, y: 1.5, w: hw, h: 4.1, name: "grade" });
card(s, { x: M + hw + 0.4, y: 1.5, w: hw, h: 4.1, name: "prog" });
tx(s, "GRADE DO DIA", { x: M + 0.42, y: 1.8, w: hw - 0.8, h: 0.35, fontSize: 13, bold: true, color: TEAL, charSpacing: 2 });
tx(s, "PROGRAMAÇÃO DAS COMPANHIAS", { x: M + hw + 0.82, y: 1.8, w: hw - 0.8, h: 0.35, fontSize: 13, bold: true, color: TEAL, charSpacing: 2 });
const gItens = [
  "Uma linha por posição e uma coluna por horário",
  "Voos e reservas da aviação geral juntos",
  "Trocar posição ou portão com dois cliques",
  "Cor da companhia e contorno do portão no bloco",
];
const pItens = [
  "A programação do mês entra por planilha",
  "Pode reimportar quando a companhia mudar algo",
  "Ninguém precisa lançar voo a voo",
];
const lista = (arr, x0) => arr.forEach((t, i) => {
  const y = 2.4 + i * 0.85;
  s.addShape(pres.ShapeType.ellipse, { x: x0 + 0.44, y: y + 0.17, w: 0.16, h: 0.16, fill: { color: TEAL }, line: { color: TEAL, width: 0 } });
  tx(s, t, { x: x0 + 0.78, y, w: hw - 1.15, h: 0.5, fontSize: 15.5, color: INK, valign: "middle" });
});
lista(gItens, M);
lista(pItens, M + hw + 0.4);
notas(s, [
  "Voo regular, 2 min. Rápido.",
  "",
  "Mostrar a grade de Navegantes com voos e reservas juntos.",
  "A importação é só citar: a planilha do mês entra pela tela de importação e vira grade.",
  "Não entrar em detalhe de pareamento.",
]);

/* 8 - O que levantar */
pres.addSection({ title: "Próximos passos" });
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Próximos passos" });
ttl(s, "O que cada aeroporto precisa levantar");
const itens = [
  { t: "Pátios e posições", d: "Os boxes de cada pátio e a maior aeronave que cada um recebe. Normalmente já está no quadro de mix de aeronaves." },
  { t: "Restrições", d: "Qual posição atrapalha a vizinha e qual aeronave não entra onde." },
  { t: "Portões e pontes", d: "Quais existem e quais posições atendem." },
  { t: "Operadores", d: "As companhias e os operadores de aviação geral que usam o aeroporto." },
];
itens.forEach((it, i) => {
  const y = 1.45 + i * 1.18;
  card(s, { x: M, y, w: CW, h: 1.02, name: "item" + i });
  bola(s, M + 0.35, y + 0.24, 0.54, String(i + 1));
  tx(s, it.t, { x: M + 1.15, y, w: 3.0, h: 1.02, fontSize: 18, bold: true, color: TEAL, valign: "middle" });
  tx(s, it.d, { x: M + 4.25, y, w: CW - 4.6, h: 1.02, fontSize: 14.5, color: INK, valign: "middle" });
});
tx(s, "Vou entrar em contato com cada aeroporto para fazer esse levantamento junto com a supervisão.",
  { x: M, y: 6.25, w: CW, h: 0.45, fontSize: 15, bold: true, color: TEAL });
notas(s, [
  "O que levantar, 2 min.",
  "",
  "Deixar claro que quase tudo já existe no aeroporto, principalmente no quadro de mix de aeronaves.",
  "Avisar que eu vou procurar cada um para fazer o levantamento junto.",
]);

/* 9 - O que eu preciso */
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Próximos passos" });
ttl(s, "O que eu preciso de vocês");
const pedidos = [
  { t: "Um contato na supervisão", d: "Para eu combinar o levantamento e tirar as dúvidas do dia a dia." },
  { t: "A ordem de entrada", d: "Qual aeroporto começa primeiro. Vamos um de cada vez." },
  { t: "Como funciona hoje", d: "Como cada aeroporto faz a reserva de aviação geral hoje, para a implantação respeitar isso." },
];
const pw3 = (CW - 2 * 0.3) / 3;
pedidos.forEach((p, i) => {
  const x = M + i * (pw3 + 0.3);
  card(s, { x, y: 1.5, w: pw3, h: 3.15, fill: "EAF5F6", line: "9FC9D0", name: "pedido" + i });
  bola(s, x + 0.4, 1.85, 0.64, String(i + 1));
  tx(s, p.t, { x: x + 0.4, y: 2.72, w: pw3 - 0.8, h: 0.85, fontSize: 19, bold: true, color: DEEP, valign: "top" });
  tx(s, p.d, { x: x + 0.4, y: 3.6, w: pw3 - 0.8, h: 0.95, fontSize: 14, color: "15565F", valign: "top" });
});
card(s, { x: M, y: 5.0, w: CW, h: 1.3, name: "compromisso" });
tx(s, [
  { text: "Da minha parte: ", options: { bold: true, color: TEAL } },
  { text: "faço o cadastro junto com a supervisão e acompanho de perto o primeiro mês de uso.", options: { color: INK } },
], { x: M + 0.45, y: 5.0, w: CW - 0.9, h: 1.3, fontSize: 16, valign: "middle" });
notas(s, [
  "O que eu preciso, 2 min.",
  "",
  "Pedir os três itens.",
  "Tentar sair da reunião com pelo menos o nome do contato de cada aeroporto.",
  "Se a Andreza quiser falar de prazo, passar a palavra para ela aqui.",
]);

/* 10 - Perguntas */
pres.addSection({ title: "Fecho" });
s = pres.addSlide({ masterName: "ESCURO", sectionTitle: "Fecho" });
tx(s, "OBRIGADO", { x: 1.1, y: 2.55, w: 11.2, h: 0.45, fontSize: 15, bold: true, color: "7FB3BC", charSpacing: 3, valign: "bottom" });
tx(s, "Dúvidas?", { x: 1.1, y: 3.1, w: 11.2, h: 1.3, fontSize: 50, bold: true, color: "FFFFFF", valign: "top" });
tx(s, "Mapa de Alocação  ·  AirportNow  ·  ASUR BRASIL", { x: 1.1, y: 4.55, w: 11.2, h: 0.4, fontSize: 15, color: "B9D9DE" });
notas(s, [
  "Dúvidas, o tempo que sobrar.",
  "",
  "Substitui o Ares? Não. O registro oficial continua no Ares.",
  "Quem pode mexer? Quem tem acesso pelo AirportNow. Cada um vê o próprio aeroporto.",
  "Dá para tirar relatório? Sim, a programação exporta em planilha com quem lançou e quando.",
  "Quanto tempo para implantar? Depende do levantamento do pátio. O cadastro em si é rápido.",
  "",
  "O que não souber, anotar e responder depois.",
]);

/* ---------------- gravar ---------------- */
const out = process.argv[2];
pres.writeFile({ fileName: out }).then(async () => {
  const { applyTheme } = require(process.argv[3]);
  await applyTheme(out, THEME);
  console.log("ok ->", out);
}).catch((e) => { console.error("ERRO:", e); process.exit(1); });
