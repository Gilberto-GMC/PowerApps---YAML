import fs from 'fs';
const rec = l => l.length - l.replace(/^ +/, '').length;

// uma tela por entrada: os nomes dos filtros mudam entre as duas
const TELAS = [
  {
    arq: 'ScreenInventarioSeparar.pa.yaml', sufixo: 'Eleg', tipo: 'ELEGIVEIS',
    rodape: 'Container11', antesDe: 'Text5_2', timerVizinho: 'Timer2_9',
    cat: 'ComboboxCanvasCat_7', sub: 'ComboboxCanvasSubCat_7',
    aero: 'ComboboxCanvasAeroporto_6', de: 'dtpFilterInicio_6',
    ate: 'dtpFilterTermino_6', busca: 'SearchInput2_6',
  },
  {
    arq: 'ScreenInventarioDoacao.pa.yaml', sufixo: 'Sep', tipo: 'SEPARADOS',
    rodape: 'Container6', antesDe: 'Text5_3', timerVizinho: 'Timer2_11',
    cat: 'ComboboxCanvasCat_8', sub: 'ComboboxCanvasSubCat_8',
    aero: 'ComboboxCanvasAeroporto_7', de: 'dtpFilterInicio_7',
    ate: 'dtpFilterTermino_7', busca: 'SearchInput2_7',
  },
];

for (const t of TELAS) {
  const RAW = fs.readFileSync(t.arq, 'utf8');
  const CRLF = RAW.includes('\r\n');
  const a = RAW.replace(/\r\n/g, '\n').split('\n');

  const V = 'varPedidoExp' + t.sufixo;   // o pedido corrente, relido pelo timer
  const BTN = 'btnExportar' + t.sufixo;
  const LBL = 'lblExportar' + t.sufixo;
  const BAI = 'btnBaixar' + t.sufixo;
  const TMR = 'tmrExportar' + t.sufixo;

  // ---------- 1. os tres controles no rodape, antes do contador ----------
  const i = a.findIndex(l => new RegExp('^ *- ' + t.antesDe + ':$').test(l));
  if (i < 0) throw new Error(t.antesDe + ' nao encontrado em ' + t.arq);
  const ind = rec(a[i]);
  const I = ' '.repeat(ind), I2 = ' '.repeat(ind + 4), I3 = ' '.repeat(ind + 6);

  const bloco = [
    I + '- ' + BTN + ':',
    I2 + 'Control: Button@0.0.45',
    I2 + 'Properties:',
    I3 + 'AlignInContainer: =AlignInContainer.Center',
    I3 + "Appearance: ='ButtonCanvas.Appearance'.Secondary",
    I3 + 'BasePaletteColor: =thmPrimaria',
    I3 + 'DisplayMode: |-',
    I3 + '  =If(',
    I3 + "      " + V + ".status = \"PRONTO\" Or " + V + '.status = "PROCESSANDO",',
    I3 + '      DisplayMode.Disabled,',
    I3 + '      DisplayMode.Edit',
    I3 + '  )',
    I3 + 'FillPortions: =0',
    I3 + 'Height: =34',
    I3 + 'Icon: ="DocumentPdf"',
    I3 + "IconStyle: ='ButtonCanvas.IconStyle'.Filled",
    I3 + 'OnSelect: |-',
    I3 + '  =Set(varUltimaAtividade, Now());',
    // o pedido nasce PRONTO: e isso que o gatilho do fluxo espera
    I3 + '  Set(',
    I3 + '      ' + V + ',',
    I3 + '      Patch(',
    I3 + '          tb_exportacaoPA,',
    I3 + '          Defaults(tb_exportacaoPA),',
    I3 + '          {',
    I3 + '              aeroporto: Coalesce(' + t.aero + '.Selected.Value, varAeroUser),',
    I3 + '              tipo: "' + t.tipo + '",',
    I3 + '              categoria: ' + t.cat + '.Selected.Value,',
    I3 + '              subcategoria: ' + t.sub + '.Selected.Value,',
    I3 + '              data_de: ' + t.de + '.SelectedDate,',
    I3 + '              data_ate: ' + t.ate + '.SelectedDate,',
    I3 + '              busca: ' + t.busca + '.Text,',
    I3 + '              solicitante: varNomeUser,',
    I3 + '              status: "PRONTO",',
    I3 + '              ativo: 1',
    I3 + '          }',
    I3 + '      )',
    I3 + '  );',
    I3 + '  Notify(',
    I3 + '      "Pedido enviado. O arquivo leva cerca de um minuto.",',
    I3 + '      NotificationType.Information',
    I3 + '  )',
    I3 + 'Text: ="Exportar Excel"',
    I3 + 'Width: =160',

    I + '- ' + LBL + ':',
    I2 + 'Control: Label@2.5.1',
    I2 + 'Properties:',
    I3 + 'AlignInContainer: =AlignInContainer.Center',
    I3 + 'BorderColor: =RGBA(0, 0, 0, 0)',
    I3 + 'BorderStyle: =BorderStyle.None',
    I3 + 'Color: |-',
    I3 + '  =If(',
    I3 + '      ' + V + '.status = "ERRO",',
    I3 + '      thmVermelho,',
    I3 + '      thmTextoFraco',
    I3 + '  )',
    I3 + 'FillPortions: =0',
    I3 + 'Height: =34',
    I3 + 'Size: =11',
    I3 + 'Text: |-',
    I3 + '  =Switch(',
    I3 + '      ' + V + '.status,',
    I3 + '      "PRONTO", "Na fila...",',
    I3 + '      "PROCESSANDO", "Gerando o arquivo...",',
    I3 + '      "CONCLUIDO", ' + V + '.total & " item(ns) no arquivo",',
    I3 + '      "ERRO", ' + V + '.mensagem,',
    I3 + '      ""',
    I3 + '  )',
    I3 + 'Width: =240',

    I + '- ' + BAI + ':',
    I2 + 'Control: Button@0.0.45',
    I2 + 'Properties:',
    I3 + 'AlignInContainer: =AlignInContainer.Center',
    I3 + "Appearance: ='ButtonCanvas.Appearance'.Primary",
    I3 + 'BasePaletteColor: =thmAcao',
    I3 + 'FillPortions: =0',
    I3 + 'Height: =34',
    I3 + 'Icon: ="Save"',
    I3 + "IconStyle: ='ButtonCanvas.IconStyle'.Filled",
    I3 + 'OnSelect: |-',
    I3 + '  =Set(varUltimaAtividade, Now());',
    I3 + '  Launch(' + V + '.arquivo_url)',
    I3 + 'Text: ="Baixar"',
    I3 + 'Visible: =' + V + '.status = "CONCLUIDO"',
    I3 + 'Width: =120',
  ];
  a.splice(i, 0, ...bloco);

  // ---------- 2. o timer que acompanha o pedido ----------
  const k = a.findIndex(l => new RegExp('^ *- ' + t.timerVizinho + ':$').test(l));
  if (k < 0) throw new Error(t.timerVizinho + ' nao encontrado em ' + t.arq);
  const j = rec(a[k]);
  const J = ' '.repeat(j), J2 = ' '.repeat(j + 4), J3 = ' '.repeat(j + 6);
  a.splice(k, 0,
    J + '- ' + TMR + ':',
    J2 + 'Control: Timer@2.1.0',
    J2 + 'Properties:',
    J3 + 'AutoStart: =true',
    J3 + 'Duration: =5000',
    // so corre enquanto ha pedido em andamento: parado, nao consulta nada
    J3 + 'OnTimerEnd: |-',
    J3 + '  =If(',
    J3 + '      ' + V + '.status = "PRONTO" Or ' + V + '.status = "PROCESSANDO",',
    J3 + '      Set(',
    J3 + '          ' + V + ',',
    J3 + '          LookUp(tb_exportacaoPA, ID = ' + V + '.ID)',
    J3 + '      )',
    J3 + '  )',
    J3 + 'Repeat: =true',
    J3 + 'Visible: =false',
  );

  fs.writeFileSync(t.arq, CRLF ? a.join('\n').replace(/\n/g, '\r\n') : a.join('\n'), 'utf8');
  console.log(t.arq + ': ' + BTN + ', ' + LBL + ', ' + BAI + ' no ' + t.rodape + '; ' + TMR + ' na raiz');
}
