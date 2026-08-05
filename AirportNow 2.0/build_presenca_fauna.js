const fs = require('node:fs');

const sourcePath = '/home/codespace/.codex/attachments/4aa03bd7-66ee-4220-b6b2-43b6ecd96153/pasted-text.txt';
const targetPath = '/workspaces/codespaces-blank/AirportNow 2.0/PresencaFauna.pa.yaml';

let yaml = fs.readFileSync(sourcePath, 'utf8').replace(/\r\n/g, '\n');

function extractCard(name) {
  const marker = `                                                      - ${name}:`;
  const start = yaml.indexOf(marker);
  if (start < 0) throw new Error(`Card não encontrado: ${name}`);
  const nextCard = yaml.indexOf('\n                                                      - ', start + marker.length);
  const formButtons = yaml.indexOf('\n                                                - ContainerFaunaBotoes:', start + marker.length);
  const endCandidates = [nextCard, formButtons].filter(value => value >= 0);
  return yaml.slice(start, Math.min(...endCandidates));
}

function setCardPosition(card, x, y, widthExpression) {
  const childrenIndex = card.indexOf('\n                                                          Children:');
  let head = card.slice(0, childrenIndex);
  const tail = card.slice(childrenIndex);

  head = head.replace(/\n                                                            X: =[^\n]+/, `\n                                                            X: =${x}`);
  head = head.replace(/\n                                                            Y: =[^\n]+/, `\n                                                            Y: =${y}`);
  head = head.replace(/\n                                                            Width: =[^\n]+/, `\n                                                            Width: =${widthExpression}`);

  if (!/\n                                                            X: =/.test(head)) {
    head += `\n                                                            X: =${x}`;
  }
  if (!/\n                                                            Y: =/.test(head)) {
    head += `\n                                                            Y: =${y}`;
  }

  return head + tail;
}

function renameCard(card, replacements) {
  for (const [from, to] of replacements) {
    card = card.split(from).join(to);
  }
  return card;
}

const aeroporto = setCardPosition(extractCard('aeroporto_DataCardFauna'), 0, 0, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');
const dataEvento = setCardPosition(extractCard('data_evento_DataCardFauna'), 1, 0, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');

let clima = renameCard(extractCard('parte_dia_DataCardFauna'), [
  ['parte_dia', 'clima'],
  ['ParteDia', 'Clima'],
  ['Parte do dia *', '4. Clima *'],
  ['colFaunaPartesDia', 'colFaunaClimas'],
  ['Selecione...', 'Selecione o clima']
]);
clima = setCardPosition(clima, 0, 1, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');

let local = renameCard(extractCard('condicao_ceu_DataCardFauna'), [
  ['condicao_ceu', 'local_geral'],
  ['CondicaoCeu', 'LocalGeral'],
  ['Condições do Céu *', '5. Local *'],
  ['colFaunaCondicoesCeu', 'colFaunaLocaisPresenca'],
  ['Selecione...', 'Selecione o local']
]);
local = setCardPosition(local, 1, 1, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');

let tipoOcorrencia = renameCard(extractCard('precipitacao_DataCardFauna'), [
  ['precipitacao', 'tipo_ocorrencia'],
  ['Precipitacao', 'TipoOcorrencia'],
  ['Precipitação *', '6. Foi registrada alguma ocorrência com fauna? *'],
  ['colFaunaPrecipitacoes', 'colFaunaTiposOcorrencia'],
  ['Selecione...', 'Localizar itens']
]);
tipoOcorrencia = setCardPosition(tipoOcorrencia, 0, 2, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');

let evidencia = renameCard(extractCard('local_geral_DataCardFauna'), [
  ['local_geral', 'evidencia'],
  ['LocalGeral', 'Evidencia'],
  ['Local Geral *', '7. Há evidências? *'],
  ['colFaunaLocais', 'colFaunaEvidencias'],
  ['Selecione o local', 'Localizar itens']
]);
evidencia = setCardPosition(evidencia, 1, 2, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');

let comportamento = renameCard(extractCard('comportamento_fauna_DataCardFauna'), [
  ['comportamento_fauna', 'comportamento'],
  ['ComportamentoFauna', 'Comportamento'],
  ['Comportamento Observado *', '8. Comportamento do animal ou bando *'],
  ['colFaunaComportamentos', 'colFaunaComportamentosPresenca']
]);
comportamento = setCardPosition(comportamento, 0, 3, 'Parent.Width - 24');

let descricao = renameCard(extractCard('descricao_evento_DataCardFauna'), [
  ['Descrição do Evento *', '9. Descrição do evento/observação *'],
  ['Descreva detalhadamente o evento...', 'Descreva detalhadamente a presença de fauna, as ações tomadas e observações adicionais...']
]);
descricao = setCardPosition(descricao, 0, 4, 'Parent.Width - 24');

let anexos = extractCard('Anexos_DataCardFauna');
anexos = renameCard(anexos, [['Registro Fotográfico e Evidências', '10. Registro Fotográfico e Evidências']]);
anexos = setCardPosition(anexos, 0, 5, 'Parent.Width');

const status = setCardPosition(extractCard('status_DataCardFauna'), 0, 6, 'Parent.Width');
const ativo = setCardPosition(extractCard('ativo_DataCardFauna'), 0, 7, 'Parent.Width');

const firstCardMarker = '                                                      - tipo_evento_DataCardFauna:';
const cardsStart = yaml.indexOf(firstCardMarker);
const cardsEnd = yaml.indexOf('\n                                                - ContainerFaunaBotoes:', cardsStart);
if (cardsStart < 0 || cardsEnd < 0) throw new Error('Bloco de DataCards não encontrado');

const targetCards = [
  aeroporto,
  dataEvento,
  clima,
  local,
  tipoOcorrencia,
  evidencia,
  comportamento,
  descricao,
  anexos,
  status,
  ativo
].join('\n');

yaml = yaml.slice(0, cardsStart) + targetCards + yaml.slice(cardsEnd);

const onVisibleStart = yaml.indexOf('      OnVisible: |-');
const screenChildren = yaml.indexOf('    Children:', onVisibleStart);
if (onVisibleStart < 0 || screenChildren < 0) throw new Error('OnVisible não encontrado');

const onVisible = `      OnVisible: |-
        =If(
            !varFaunaEstruturaCarregada || IsEmpty(colFaunaAeroportos),
            ClearCollect(
                colFaunaAeroportos,
                [
                    "BACACHERI", "BAGÉ", "CURITIBA", "FOZ DO IGUAÇU",
                    "GOIÂNIA", "IMPERATRIZ", "JOINVILLE", "LONDRINA",
                    "NAVEGANTES", "PALMAS", "PAMPULHA", "PELOTAS",
                    "PETROLINA", "SÃO LUIS", "TERESINA", "URUGUAIANA"
                ]
            );
            ClearCollect(colFaunaAeroportosFiltro, ["TODOS OS AEROPORTOS"]);
            Collect(colFaunaAeroportosFiltro, colFaunaAeroportos);
            ClearCollect(colFaunaClimas, ["Claro", "Poucas Nuvens", "Encoberto", "Chuva", "Nevoeiro", "Tempestade"]);
            ClearCollect(colFaunaLocaisPresenca, ["Área Operacional", "Área Patrimonial", "Área de Segurança Aeroportuária - ASA"]);
            ClearCollect(colFaunaTiposOcorrencia, ["Afugentamento", "Captura", "Manejo de Brando", "Coleta de Carcaça", "Nenhum", "Presença", "Vestígio"]);
            ClearCollect(colFaunaEvidencias, ["Escuta", "Ninho", "Fezes", "Ovos", "Presença", "Penas", "Pegadas"]);
            ClearCollect(colFaunaComportamentosPresenca, ["Buscando alimento", "Se alimentando", "Empoleirado", "Parado no chão", "Dentro do ninho", "Outros"]);
            Set(varFaunaEstruturaCarregada, true)
        );
        UpdateContext(
            {
                var_filterButtonAction: "TODOS",
                var_visible: "Novo Registro",
                var_acao: "new",
                var_visibleExcluir: false,
                var_visibleProcessando: false,
                var_dados_reporteFauna: Defaults(tb_reporteFauna)
            }
        );
        Reset(filtro_fauna_aeroporto);
        Reset(filtro_fauna_data_inicio);
        Reset(filtro_fauna_data_fim);
        ResetForm(FormReporteFauna);
        NewForm(FormReporteFauna)
`;

yaml = yaml.slice(0, onVisibleStart) + onVisible + yaml.slice(screenChildren);

yaml = yaml.replace(
  /                                                      Height: \|-\n                                                        =1990 \+\n                                                        If\(varDanosPrejuizoFauna in \["Sim", "Indeterminado"\], 150, 0\)/,
  '                                                      Height: =1030'
);

yaml = yaml
  .replace('                                                Text: ="REPORTE MANDATÓRIO DE FAUNA"', '                                                Text: ="PRESENÇA DE FAUNA"')
  .replace('                                                              "<p style=\'margin:0;\'>Este módulo é destinado ao <b>Reporte Mandatório de Fauna</b>. Registre colisões, quase colisões e avistamentos, incluindo condições operacionais, aeronave envolvida, espécie, evidências e ações executadas.</p>" &', '                                                              "<p style=\'margin:0;\'>Registre a presença de fauna, as evidências observadas, o comportamento do animal ou bando e as ações realizadas no local.</p>" &')
  .replace('                                                      Text: =If(var_acao = "edit", "Editar Reporte", "Novo Registro")', '                                                      Text: =If(var_acao = "edit", "Editar Registro", "Novo Registro")')
  .replace('                                                                  Text: =If(var_acao = "edit", "Salvar Alterações", "Finalizar Reporte")', '                                                                  Text: =If(var_acao = "edit", "Salvar Alterações", "Finalizar Registro")')
  .replace('                        Text: ="O reporte mandatório de fauna está sendo atualizado no sistema."', '                        Text: ="O registro de presença de fauna está sendo atualizado no sistema."')
  .replace('                                                            Notify("Reporte de fauna salvo com sucesso.", NotificationType.Success, 3000)', '                                                            Notify("Registro de presença de fauna salvo com sucesso.", NotificationType.Success, 3000)')
  .replace('                                                            "Não foi possível salvar o reporte. Verifique os campos obrigatórios e tente novamente.",', '                                                            "Não foi possível salvar o registro. Verifique os campos obrigatórios e tente novamente.",')
  .replace('                                                                  Placeholder: ="Descreva detalhadamente a interação, reportes da tripulação e danos observados..."', '                                                                  Placeholder: ="Descreva detalhadamente a presença de fauna, as ações tomadas e observações adicionais..."');

yaml = yaml
  .replace('                                                                  Text: ="AERONAVE"', '                                                                  Text: ="AEROPORTO / LOCAL"')
  .replace('                                                                  Text: ="FAUNA / ESPÉCIE"', '                                                                  Text: ="EVIDÊNCIA / COMPORTAMENTO"')
  .replace('                                                                  Text: ="TIPO DE EVENTO"', '                                                                  Text: ="OCORRÊNCIA"');

function replaceControlPropertyBlock(controlName, propertyName, nextPropertyName, replacement) {
  const controlStart = yaml.indexOf(`                                                                  - ${controlName}:`);
  if (controlStart < 0) throw new Error(`Controle não encontrado: ${controlName}`);
  const propertyStart = yaml.indexOf(`                                                                        ${propertyName}: |-`, controlStart);
  const propertyEnd = yaml.indexOf(`\n                                                                        ${nextPropertyName}:`, propertyStart);
  if (propertyStart < 0 || propertyEnd < 0) throw new Error(`Propriedade ${propertyName} não encontrada em ${controlName}`);
  yaml = yaml.slice(0, propertyStart) + replacement + yaml.slice(propertyEnd);
}

replaceControlPropertyBlock(
  'htmlFaunaAeronave',
  'HtmlText',
  'LayoutMinWidth',
  `                                                                        HtmlText: |-
                                                                          ="<div style='text-align:center;line-height:1.2;'>" &
                                                                          "<div style='color:#000000;font-size:12px;font-weight:700;'>" & Coalesce(ThisItem.aeroporto, "-") & "</div>" &
                                                                          "<div style='color:#777777;font-size:10px;font-weight:600;margin-top:2px;'>" & Coalesce(ThisItem.local_geral, "-") & "</div>" &
                                                                          "</div>"`
);

replaceControlPropertyBlock(
  'htmlFaunaEspecie',
  'HtmlText',
  'LayoutMinWidth',
  `                                                                        HtmlText: |-
                                                                          ="<div style='text-align:center;line-height:1.2;'>" &
                                                                          "<div style='color:#000000;font-size:12px;font-weight:600;'>" & Coalesce(ThisItem.evidencia, "-") & "</div>" &
                                                                          "<div style='color:#777777;font-size:10px;font-weight:600;margin-top:2px;'>" & Coalesce(ThisItem.comportamento, "-") & "</div>" &
                                                                          "</div>"`
);

replaceControlPropertyBlock(
  'htmlFaunaTipo',
  'HtmlText',
  'LayoutMinWidth',
  `                                                                        HtmlText: |-
                                                                          ="<div style='display:table;width:100%;height:55px;'>" &
                                                                          "<div style='display:table-cell;vertical-align:middle;text-align:center;'>" &
                                                                          "<span style='display:inline-block;border:1px solid #bfdbfe;background:#eff6ff;color:#2563eb;font-size:10px;font-weight:800;padding:4px 8px;'>" &
                                                                          Upper(Coalesce(ThisItem.tipo_ocorrencia, "-")) &
                                                                          "</span></div></div>"`
);

const toolbarStart = yaml.indexOf('                                                                  - ToolbarFaunaAcoes:');
const toolbarOnSelect = yaml.indexOf('                                                                        OnSelect: |-', toolbarStart);
const toolbarPadding = yaml.indexOf('\n                                                                        Padding:', toolbarOnSelect);
if (toolbarStart < 0 || toolbarOnSelect < 0 || toolbarPadding < 0) throw new Error('Toolbar de ações não encontrada');

const toolbarFormula = `                                                                        OnSelect: |-
                                                                          =Switch(
                                                                              Self.Selected.ItemKey,
                                                                              "ver",
                                                                              UpdateContext(
                                                                                  {
                                                                                      var_dados_reporteFauna: ThisItem,
                                                                                      var_visible: "Novo Registro",
                                                                                      var_acao: "ver"
                                                                                  }
                                                                              );
                                                                              ViewForm(FormReporteFauna);
                                                                              SetFocus(cmbFaunaAeroporto),
                                                                              "edit",
                                                                              UpdateContext(
                                                                                  {
                                                                                      var_dados_reporteFauna: ThisItem,
                                                                                      var_visible: "Novo Registro",
                                                                                      var_acao: "edit"
                                                                                  }
                                                                              );
                                                                              EditForm(FormReporteFauna);
                                                                              SetFocus(cmbFaunaAeroporto),
                                                                              "exc",
                                                                              UpdateContext(
                                                                                  {
                                                                                      var_dados_reporteFauna: ThisItem,
                                                                                      var_visibleExcluir: true,
                                                                                      var_acao: "exc"
                                                                                  }
                                                                              )
                                                                          )`;

yaml = yaml.slice(0, toolbarOnSelect) + toolbarFormula + yaml.slice(toolbarPadding);

yaml = yaml.replace(/\b([A-Za-z_][A-Za-z0-9_]*)Fauna([A-Za-z0-9_]*)\b/g, '$1PresencaFauna$2');
yaml = yaml.replace(/\bFauna(?=[A-Z_])/g, 'PresencaFauna');

yaml = yaml
  .replace('  ReportePresencaFauna:', '  PresencaFauna:')
  .replaceAll('tb_reportePresencaFauna', 'tb_presencaFauna')
  .replaceAll('var_dados_reportePresencaFauna', 'var_dados_presencaFauna')
  .replaceAll('FormReportePresencaFauna', 'FormPresencaFauna')
  .replaceAll('filtro_fauna_', 'filtro_presenca_fauna_')
  .replaceAll('Tooltip: =Coalesce(ThisItem.operador_aeronave, "")', 'Tooltip: =Coalesce(ThisItem.aeroporto, "")')
  .replaceAll('Tooltip: =Coalesce(ThisItem.especie_fauna, "")', 'Tooltip: =Coalesce(ThisItem.evidencia, "")')
  .replaceAll('                                                                varTipoEventoPresencaFauna: "Colisão",\n', '')
  .replaceAll('                                                                varDanosPrejuizoPresencaFauna: "Não",\n', '')
  .replaceAll('Reporte de fauna salvo com sucesso.', 'Registro de presença de fauna salvo com sucesso.')
  .replaceAll('Preencha todos os campos obrigatórios antes de finalizar o reporte.', 'Preencha todos os campos obrigatórios antes de finalizar o registro.')
  .replaceAll('Deseja excluir permanentemente o reporte:', 'Deseja excluir permanentemente o registro:')
  .replaceAll('Não foi possível excluir o reporte.', 'Não foi possível excluir o registro.')
  .replaceAll('Reporte excluído com sucesso.', 'Registro excluído com sucesso.')
  .replaceAll('ContainerPresencaFaunaNovoReporte', 'ContainerPresencaFaunaNovoRegistro')
  .replaceAll('lblPresencaFaunaCabAeronave', 'lblPresencaFaunaCabAeroportoLocal')
  .replaceAll('htmlPresencaFaunaAeronave', 'htmlPresencaFaunaAeroportoLocal')
  .replaceAll('htmlPresencaFaunaEspecie', 'htmlPresencaFaunaEvidenciaComportamento')
  .replaceAll('4. Clima *', 'Clima *')
  .replaceAll('5. Local *', 'Local *')
  .replaceAll('6. Foi registrada alguma ocorrência com fauna? *', 'Foi registrada alguma ocorrência com fauna? *')
  .replaceAll('7. Há evidências? *', 'Há evidências? *')
  .replaceAll('8. Comportamento do animal ou bando *', 'Comportamento do animal ou bando *')
  .replaceAll('9. Descrição do evento/observação *', 'Descrição do evento/observação *')
  .replaceAll('10. Registro Fotográfico e Evidências', 'Registro Fotográfico e Evidências');

// Mantém a consulta inicial limitada ao período operacional mais recente.
// O padrão de 90 dias já é usado nas telas históricas do aplicativo de referência.
yaml = yaml.replace(
  `                                                            Height: =40
                                                            Placeholder: ="dd/mm/aaaa"
                                                            Width: =130
                                                      - filtro_presenca_fauna_data_fim:`,
  `                                                            Height: =40
                                                            Placeholder: ="dd/mm/aaaa"
                                                            SelectedDate: =DateAdd(Today(), -90, TimeUnit.Days)
                                                            Width: =130
                                                      - filtro_presenca_fauna_data_fim:`
);

const filtroDataFimStart = yaml.indexOf('                                                      - filtro_presenca_fauna_data_fim:');
const filtroLimparStart = yaml.indexOf('                                                      - btnPresencaFaunaLimparFiltros:', filtroDataFimStart);
if (filtroDataFimStart < 0 || filtroLimparStart < 0) throw new Error('Filtro de data final não encontrado');
const filtroDataFimBlock = yaml.slice(filtroDataFimStart, filtroLimparStart);
yaml = yaml.slice(0, filtroDataFimStart) + filtroDataFimBlock.replace(
  '                                                            Placeholder: ="dd/mm/aaaa"',
  '                                                            Placeholder: ="dd/mm/aaaa"\n                                                            SelectedDate: =Today()'
) + yaml.slice(filtroLimparStart);

// Trocar de aba não deve fazer uma nova chamada de rede. As operações de
// gravação continuam atualizando a fonte no OnSuccess/remoção.
yaml = yaml.replace(
  `                                                      OnSelect: |-
                                                        =Refresh(tb_presencaFauna);
                                                        UpdateContext({var_visible: "Registros", var_acao: Blank()})`,
  `                                                      OnSelect: |-
                                                        =UpdateContext({var_visible: "Registros", var_acao: Blank()})`
);

const galleryStart = yaml.indexOf('                                                      - GalleryPresencaFauna:');
const galleryItemsStart = yaml.indexOf('                                                            Items: |-', galleryStart);
const galleryItemsEnd = yaml.indexOf('\n                                                            LayoutMinHeight:', galleryItemsStart);
if (galleryStart < 0 || galleryItemsStart < 0 || galleryItemsEnd < 0) throw new Error('Items da galeria não encontrado');

const galleryItems = `                                                            Items: |-
                                                              =With(
                                                                  {
                                                                      _aeroporto: filtro_presenca_fauna_aeroporto.Selected.Value,
                                                                      _inicioLocal: Coalesce(
                                                                          filtro_presenca_fauna_data_inicio.SelectedDate,
                                                                          DateAdd(Today(), -90, TimeUnit.Days)
                                                                      ),
                                                                      _fimLocal: Coalesce(
                                                                          filtro_presenca_fauna_data_fim.SelectedDate,
                                                                          Today()
                                                                      )
                                                                  },
                                                                  With(
                                                                      {
                                                                          _inicioUtc: DateAdd(
                                                                              _inicioLocal,
                                                                              -TimeZoneOffset(_inicioLocal),
                                                                              TimeUnit.Minutes
                                                                          ),
                                                                          _fimUtc: DateAdd(
                                                                              DateAdd(_fimLocal, 1, TimeUnit.Days),
                                                                              -TimeZoneOffset(DateAdd(_fimLocal, 1, TimeUnit.Days)),
                                                                              TimeUnit.Minutes
                                                                          )
                                                                      },
                                                                      SortByColumns(
                                                                          Filter(
                                                                              tb_presencaFauna,
                                                                              ativo = 1,
                                                                              _aeroporto = "TODOS OS AEROPORTOS" || aeroporto = _aeroporto,
                                                                              data_evento >= _inicioUtc,
                                                                              data_evento < _fimUtc
                                                                          ),
                                                                          "ID",
                                                                          SortOrder.Descending
                                                                      )
                                                                  )
                                                              )`;

yaml = yaml.slice(0, galleryItemsStart) + galleryItems + yaml.slice(galleryItemsEnd);
yaml = yaml.replace(
  '                                                            Text: =GalleryPresencaFauna.AllItemsCount & " REGISTROS ENCONTRADOS"',
  '                                                            Text: =GalleryPresencaFauna.AllItemsCount & " REGISTROS CARREGADOS"'
);

// A lista de presença de fauna não possui o campo quantidade. Remove a
// validação residual herdada do formulário de reporte mandatorório.
yaml = yaml.replace(
  `                                                                        !IsBlank(txtPresencaFaunaQuantidade.Value) &&
                                                                        (!IsNumeric(txtPresencaFaunaQuantidade.Value) || Value(txtPresencaFaunaQuantidade.Value) < 0),
                                                                        Notify(
                                                                            "A quantidade estimada deve ser um número maior ou igual a zero.",
                                                                            NotificationType.Error,
                                                                            5000
                                                                        ),
`,
  ''
);

// Os placeholders abaixo pertencem ao template interno do Studio e não são
// fórmulas válidas no Source Code YAML. Os controles usam Parent.Default e
// não dependem da propriedade MaxLength do DataCard.
yaml = yaml.replace(
  /\n\s+MaxLength: =DataSourceInfo\(%DATACARD_DATASOURCE_NAME\.ID%, %DataSourceInfo\.RESERVED%\.MaxLength, '%DATACARD_FIELD_NAME\.ID%'\)/g,
  ''
);

function addPropertyBeforeChildren(controlName, property) {
  const controlStart = yaml.indexOf(`- ${controlName}:`);
  if (controlStart < 0) throw new Error(`Controle não encontrado para inclusão de propriedade: ${controlName}`);

  const childrenStart = yaml.indexOf('\n', yaml.indexOf('Children:', controlStart));
  const childrenLineStart = yaml.lastIndexOf('\n', childrenStart - 1) + 1;
  const childrenLine = yaml.slice(childrenLineStart, childrenStart);
  const indentation = childrenLine.match(/^\s*/)[0] + '  ';

  yaml = yaml.slice(0, childrenLineStart) + `${indentation}${property}\n` + yaml.slice(childrenLineStart);
}

// Estado vazio: cabeçalho e galeria só aparecem quando a consulta possui itens.
addPropertyBeforeChildren('ContainerPresencaFaunaCabecalhoTabela', 'Visible: =GalleryPresencaFauna.AllItemsCount > 0');
addPropertyBeforeChildren('GalleryPresencaFauna', 'Visible: =GalleryPresencaFauna.AllItemsCount > 0');
addPropertyBeforeChildren('GalleryPresencaFauna', 'LoadingSpinner: =LoadingSpinner.Controls');
addPropertyBeforeChildren('GalleryPresencaFauna', 'DelayItemLoading: =true');

fs.writeFileSync(targetPath, yaml);
