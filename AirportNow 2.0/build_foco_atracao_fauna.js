const fs = require('node:fs');
const path = require('node:path');

const sourcePath = path.join(__dirname, 'PresencaFauna.pa.yaml');
const targetPath = path.join(__dirname, 'FocoAtracaoFauna.pa.yaml');

let yaml = fs.readFileSync(sourcePath, 'utf8').replace(/\r\n/g, '\n');

function extractCard(name) {
  const marker = `                                                      - ${name}:`;
  const start = yaml.indexOf(marker);
  if (start < 0) throw new Error(`DataCard não encontrado: ${name}`);

  const nextCard = yaml.indexOf('\n                                                      - ', start + marker.length);
  const buttons = yaml.indexOf('\n                                                - ContainerPresencaFaunaBotoes:', start + marker.length);
  const candidates = [nextCard, buttons].filter(value => value >= 0);
  return yaml.slice(start, Math.min(...candidates));
}

function setCardPosition(card, x, y, widthExpression) {
  const childrenIndex = card.indexOf('\n                                                          Children:');
  let head = card.slice(0, childrenIndex);
  const tail = card.slice(childrenIndex);

  head = head.replace(/\n                                                            X: =[^\n]+/, `\n                                                            X: =${x}`);
  head = head.replace(/\n                                                            Y: =[^\n]+/, `\n                                                            Y: =${y}`);
  head = head.replace(/\n                                                            Width: =[^\n]+/, `\n                                                            Width: =${widthExpression}`);
  return head + tail;
}

function makeComboCard({field, controlSuffix, label, items, placeholder, y, searchable = false}) {
  return `                                                      - ${field}_DataCardPresencaFauna:
                                                          Control: TypedDataCard@1.0.7
                                                          Variant: TextualEdit
                                                          Properties:
                                                            BorderColor: =RGBA(0, 18, 107, 1)
                                                            DataField: ="${field}"
                                                            Default: =ThisItem.${field}
                                                            DisplayName: =DataSourceInfo([@tb_presencaFauna], DataSourceInfo.DisplayName, ${field})
                                                            Fill: =RGBA(251, 252, 253, 1)
                                                            Height: =100
                                                            Required: =true
                                                            Update: =cmbPresencaFauna${controlSuffix}.Selected.Value
                                                            Width: =Parent.Width - 24
                                                            X: =0
                                                            Y: =${y}
                                                          Children:
                                                            - lbl_cmbPresencaFauna${controlSuffix}:
                                                                Control: Text@0.0.51
                                                                MetadataKey: FieldName
                                                                Properties:
                                                                  Height: =22
                                                                  Text: ="${label} *"
                                                                  Weight: ='TextCanvas.Weight'.Semibold
                                                                  Width: =Parent.Width - 48
                                                                  Wrap: =false
                                                                  X: =24
                                                                  Y: =10
                                                            - cmbPresencaFauna${controlSuffix}:
                                                                Control: ComboBox@0.0.51
                                                                MetadataKey: FieldValue
                                                                Properties:
                                                                  AccessibleLabel: =Parent.DisplayName
                                                                  Appearance: ='ComboboxCanvas.Appearance'.FilledLighter
                                                                  BorderColor: =RGBA(229, 229, 229, 1)
                                                                  BorderRadius: =0
                                                                  BorderStyle: =BorderStyle.Solid
                                                                  BorderThickness: =1
                                                                  DefaultSelectedItems: =If(IsBlank(Parent.Default), [], [Parent.Default])
                                                                  DisplayMode: =Parent.DisplayMode
                                                                  Height: =40
                                                                  InputTextPlaceholder: ="${placeholder}"
                                                                  IsSearchable: =${searchable}
                                                                  Items: =${items}
                                                                  ValidationState: =If(IsBlank(Parent.Error), "None", "Error")
                                                                  Width: =Parent.Width - 46
                                                                  X: =24
                                                                  Y: =lbl_cmbPresencaFauna${controlSuffix}.Y + lbl_cmbPresencaFauna${controlSuffix}.Height + 4
                                                            - err_cmbPresencaFauna${controlSuffix}:
                                                                Control: Text@0.0.51
                                                                MetadataKey: ErrorMessage
                                                                Properties:
                                                                  Height: =30
                                                                  Text: =Parent.Error
                                                                  Visible: =And(!IsBlank(Parent.Error), Parent.DisplayMode = DisplayMode.Edit)
                                                                  Width: =Parent.Width - 48
                                                                  X: =24
                                                                  Y: =cmbPresencaFauna${controlSuffix}.Y + cmbPresencaFauna${controlSuffix}.Height`;
}

function makeTextCard({field, controlSuffix, label, placeholder, y}) {
  return `                                                      - ${field}_DataCardPresencaFauna:
                                                          Control: TypedDataCard@1.0.7
                                                          Variant: TextualEdit
                                                          Properties:
                                                            BorderColor: =RGBA(0, 18, 107, 1)
                                                            DataField: ="${field}"
                                                            Default: =ThisItem.${field}
                                                            DisplayName: =DataSourceInfo([@tb_presencaFauna], DataSourceInfo.DisplayName, ${field})
                                                            Fill: =RGBA(251, 252, 253, 1)
                                                            Height: =100
                                                            Required: =true
                                                            Update: =txtPresencaFauna${controlSuffix}.Value
                                                            Width: =Parent.Width - 24
                                                            X: =0
                                                            Y: =${y}
                                                          Children:
                                                            - lbl_txtPresencaFauna${controlSuffix}:
                                                                Control: Text@0.0.51
                                                                MetadataKey: FieldName
                                                                Properties:
                                                                  Height: =22
                                                                  Text: ="${label} *"
                                                                  Weight: ='TextCanvas.Weight'.Semibold
                                                                  Width: =Parent.Width - 48
                                                                  Wrap: =false
                                                                  X: =24
                                                                  Y: =10
                                                            - txtPresencaFauna${controlSuffix}:
                                                                Control: TextInput@0.0.54
                                                                MetadataKey: FieldValue
                                                                Properties:
                                                                  AccessibleLabel: =Parent.DisplayName
                                                                  Appearance: ='TextInputCanvas.Appearance'.FilledLighter
                                                                  BorderColor: =RGBA(229, 229, 229, 1)
                                                                  BorderRadius: =0
                                                                  BorderStyle: =BorderStyle.Solid
                                                                  BorderThickness: =1
                                                                  DisplayMode: =Parent.DisplayMode
                                                                  Height: =40
                                                                  Placeholder: ="${placeholder}"
                                                                  Required: =Parent.Required
                                                                  ValidationState: =If(IsBlank(Parent.Error), "None", "Error")
                                                                  Value: =Parent.Default
                                                                  Width: =Parent.Width - 46
                                                                  X: =24
                                                                  Y: =lbl_txtPresencaFauna${controlSuffix}.Y + lbl_txtPresencaFauna${controlSuffix}.Height + 4
                                                            - err_txtPresencaFauna${controlSuffix}:
                                                                Control: Text@0.0.51
                                                                MetadataKey: ErrorMessage
                                                                Properties:
                                                                  Height: =30
                                                                  Text: =Parent.Error
                                                                  Visible: =And(!IsBlank(Parent.Error), Parent.DisplayMode = DisplayMode.Edit)
                                                                  Width: =Parent.Width - 48
                                                                  X: =24
                                                                  Y: =txtPresencaFauna${controlSuffix}.Y + txtPresencaFauna${controlSuffix}.Height`;
}

function makeMultilineCard({field, controlSuffix, label, placeholder, y, required, sectionTitle = ''}) {
  const hasSection = sectionTitle !== '';
  const cardHeight = hasSection ? 210 : 170;
  const labelY = hasSection ? 60 : 10;
  const section = hasSection ? `
                                                            - lblSecao_txtPresencaFauna${controlSuffix}:
                                                                Control: Text@0.0.51
                                                                Properties:
                                                                  FontColor: =RGBA(0, 0, 0, 0.7)
                                                                  Height: =30
                                                                  PaddingLeft: =38
                                                                  Text: ="${sectionTitle}"
                                                                  VerticalAlign: =VerticalAlign.Middle
                                                                  Weight: ='TextCanvas.Weight'.Semibold
                                                                  Width: =Parent.Width - 22
                                                                  Wrap: =false
                                                                  X: =12
                                                                  Y: =15
                                                            - icoSecao_txtPresencaFauna${controlSuffix}:
                                                                Control: Icon@0.0.7
                                                                Properties:
                                                                  Height: =18
                                                                  Icon: ="DocumentBulletList"
                                                                  IconColor: =RGBA(0, 0, 0, 1)
                                                                  IconStyle: ='Icon.IconStyle'.Outline
                                                                  Width: =18
                                                                  X: =24
                                                                  Y: =21` : '';

  return `                                                      - ${field}_DataCardPresencaFauna:
                                                          Control: TypedDataCard@1.0.7
                                                          Variant: TextualEdit
                                                          Properties:
                                                            BorderColor: =RGBA(0, 18, 107, 1)
                                                            DataField: ="${field}"
                                                            Default: =ThisItem.${field}
                                                            DisplayName: =DataSourceInfo([@tb_presencaFauna], DataSourceInfo.DisplayName, ${field})
                                                            Fill: =RGBA(251, 252, 253, 1)
                                                            Height: =${cardHeight}
                                                            Required: =${required}
                                                            Update: =txtPresencaFauna${controlSuffix}.Value
                                                            Width: =Parent.Width - 24
                                                            X: =0
                                                            Y: =${y}
                                                          Children:${section}
                                                            - lbl_txtPresencaFauna${controlSuffix}:
                                                                Control: Text@0.0.51
                                                                MetadataKey: FieldName
                                                                Properties:
                                                                  Height: =22
                                                                  Text: ="${label}${required ? ' *' : ''}"
                                                                  Weight: ='TextCanvas.Weight'.Semibold
                                                                  Width: =Parent.Width - 48
                                                                  Wrap: =false
                                                                  X: =24
                                                                  Y: =${labelY}
                                                            - txtPresencaFauna${controlSuffix}:
                                                                Control: TextInput@0.0.54
                                                                MetadataKey: FieldValue
                                                                Properties:
                                                                  AccessibleLabel: =Parent.DisplayName
                                                                  Appearance: ='TextInputCanvas.Appearance'.FilledLighter
                                                                  BorderColor: =RGBA(229, 229, 229, 1)
                                                                  BorderRadius: =0
                                                                  BorderStyle: =BorderStyle.Solid
                                                                  BorderThickness: =1
                                                                  DisplayMode: =Parent.DisplayMode
                                                                  Height: =100
                                                                  Mode: ='TextInputCanvas.Mode'.Multiline
                                                                  Placeholder: ="${placeholder}"
                                                                  Required: =Parent.Required
                                                                  ValidationState: =If(IsBlank(Parent.Error), "None", "Error")
                                                                  Value: =Parent.Default
                                                                  Width: =Parent.Width - 46
                                                                  X: =24
                                                                  Y: =lbl_txtPresencaFauna${controlSuffix}.Y + lbl_txtPresencaFauna${controlSuffix}.Height + 4
                                                            - err_txtPresencaFauna${controlSuffix}:
                                                                Control: Text@0.0.51
                                                                MetadataKey: ErrorMessage
                                                                Properties:
                                                                  Height: =30
                                                                  Text: =Parent.Error
                                                                  Visible: =And(!IsBlank(Parent.Error), Parent.DisplayMode = DisplayMode.Edit)
                                                                  Width: =Parent.Width - 48
                                                                  X: =24
                                                                  Y: =txtPresencaFauna${controlSuffix}.Y + txtPresencaFauna${controlSuffix}.Height`;
}

const letras = [];
for (let code = 65; code <= 90; code += 1) letras.push(String.fromCharCode(code));
for (const prefix of ['A', 'B']) {
  for (let code = 65; code <= 90; code += 1) letras.push(prefix + String.fromCharCode(code));
}
const numeros = Array.from({length: 70}, (_, index) => String(index + 1));

const mapaGradeCard = `                                                      - mapa_grade_DataCardPresencaFauna:
                                                          Control: TypedDataCard@1.0.7
                                                          Variant: TextualEdit
                                                          Properties:
                                                            BorderColor: =RGBA(0, 18, 107, 1)
                                                            DataField: ="mapa_grade"
                                                            Default: =ThisItem.mapa_grade
                                                            DisplayName: =DataSourceInfo([@tb_presencaFauna], DataSourceInfo.DisplayName, mapa_grade)
                                                            Fill: =RGBA(251, 252, 253, 1)
                                                            Height: =110
                                                            Required: =true
                                                            Update: |-
                                                              =If(
                                                                  IsBlank(cmbPresencaFaunaMapaLetra.Selected.Value) ||
                                                                  IsBlank(cmbPresencaFaunaMapaNumero.Selected.Value),
                                                                  Blank(),
                                                                  cmbPresencaFaunaMapaLetra.Selected.Value & " - " & cmbPresencaFaunaMapaNumero.Selected.Value
                                                              )
                                                            Width: =Parent.Width - 24
                                                            X: =0
                                                            Y: =2
                                                          Children:
                                                            - lblPresencaFaunaMapaGrade:
                                                                Control: Text@0.0.51
                                                                MetadataKey: FieldName
                                                                Properties:
                                                                  Height: =22
                                                                  Text: ="Quadrante do mapa de grade *"
                                                                  Weight: ='TextCanvas.Weight'.Bold
                                                                  Width: =Parent.Width - 48
                                                                  Wrap: =false
                                                                  X: =24
                                                                  Y: =10
                                                            - cmbPresencaFaunaMapaLetra:
                                                                Control: ComboBox@0.0.51
                                                                MetadataKey: FieldValue
                                                                Properties:
                                                                  AccessibleLabel: ="Letra do quadrante"
                                                                  Appearance: ='ComboboxCanvas.Appearance'.FilledLighter
                                                                  BorderColor: =RGBA(229, 229, 229, 1)
                                                                  BorderRadius: =0
                                                                  BorderStyle: =BorderStyle.Solid
                                                                  BorderThickness: =1
                                                                  DefaultSelectedItems: |-
                                                                    =If(
                                                                        IsBlank(Parent.Default),
                                                                        [],
                                                                        [Trim(First(Split(Parent.Default, " - ")).Value)]
                                                                    )
                                                                  DisplayMode: =Parent.DisplayMode
                                                                  Height: =40
                                                                  InputTextPlaceholder: ="Selecione a letra"
                                                                  IsSearchable: =false
                                                                  Items: =${JSON.stringify(letras)}
                                                                  ValidationState: =If(IsBlank(Parent.Error), "None", "Error")
                                                                  Width: =(Parent.Width - 72) / 2
                                                                  X: =24
                                                                  Y: =lblPresencaFaunaMapaGrade.Y + lblPresencaFaunaMapaGrade.Height + 4
                                                            - sepPresencaFaunaMapaGrade:
                                                                Control: Text@0.0.51
                                                                Properties:
                                                                  Align: ='TextCanvas.Align'.Center
                                                                  Height: =cmbPresencaFaunaMapaLetra.Height
                                                                  Text: ="-"
                                                                  VerticalAlign: =VerticalAlign.Middle
                                                                  Width: =24
                                                                  X: =cmbPresencaFaunaMapaLetra.X + cmbPresencaFaunaMapaLetra.Width
                                                                  Y: =cmbPresencaFaunaMapaLetra.Y
                                                            - cmbPresencaFaunaMapaNumero:
                                                                Control: ComboBox@0.0.51
                                                                Properties:
                                                                  AccessibleLabel: ="Número do quadrante"
                                                                  Appearance: ='ComboboxCanvas.Appearance'.FilledLighter
                                                                  BorderColor: =RGBA(229, 229, 229, 1)
                                                                  BorderRadius: =0
                                                                  BorderStyle: =BorderStyle.Solid
                                                                  BorderThickness: =1
                                                                  DefaultSelectedItems: |-
                                                                    =If(
                                                                        IsBlank(Parent.Default),
                                                                        [],
                                                                        [Trim(Last(Split(Parent.Default, " - ")).Value)]
                                                                    )
                                                                  DisplayMode: =Parent.DisplayMode
                                                                  Height: =40
                                                                  InputTextPlaceholder: ="Selecione o número"
                                                                  IsSearchable: =false
                                                                  Items: =${JSON.stringify(numeros)}
                                                                  ValidationState: =If(IsBlank(Parent.Error), "None", "Error")
                                                                  Width: =cmbPresencaFaunaMapaLetra.Width
                                                                  X: =sepPresencaFaunaMapaGrade.X + sepPresencaFaunaMapaGrade.Width
                                                                  Y: =cmbPresencaFaunaMapaLetra.Y
                                                            - errPresencaFaunaMapaGrade:
                                                                Control: Text@0.0.51
                                                                MetadataKey: ErrorMessage
                                                                Properties:
                                                                  Height: =30
                                                                  Text: =Parent.Error
                                                                  Visible: =And(!IsBlank(Parent.Error), Parent.DisplayMode = DisplayMode.Edit)
                                                                  Width: =Parent.Width - 48
                                                                  X: =24
                                                                  Y: =cmbPresencaFaunaMapaLetra.Y + cmbPresencaFaunaMapaLetra.Height`;

const aeroporto = setCardPosition(extractCard('aeroporto_DataCardPresencaFauna'), 0, 0, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');
const dataEvento = setCardPosition(extractCard('data_evento_DataCardPresencaFauna'), 1, 0, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');
const clima = setCardPosition(extractCard('clima_DataCardPresencaFauna'), 0, 1, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');
const local = setCardPosition(extractCard('local_geral_DataCardPresencaFauna'), 1, 1, 'If(Parent.Width < 700, Parent.Width, Parent.Width / 2) - 12');
const focoAtrativo = makeComboCard({
  field: 'foco_atrativo',
  controlSuffix: 'FocoAtrativo',
  label: 'Foi identificado foco atrativo de fauna?',
  items: 'colPresencaFaunaFocosAtrativos',
  placeholder: 'Localizar itens',
  y: 3,
  searchable: true
});
const protocolo = makeTextCard({
  field: 'protocolo_manutencao',
  controlSuffix: 'ProtocoloManutencao',
  label: 'Protocolo do chamado da manutenção',
  placeholder: 'MNT-2026-0891',
  y: 4
});
const vulnerabilidade = makeComboCard({
  field: 'vulnerabilidade',
  controlSuffix: 'Vulnerabilidade',
  label: 'Foi identificada vulnerabilidade?',
  items: 'colPresencaFaunaVulnerabilidades',
  placeholder: 'Localizar itens',
  y: 5
});
const mitigacao = makeMultilineCard({
  field: 'mitigacao_realizada',
  controlSuffix: 'MitigacaoRealizada',
  label: 'Qual foi a mitigação realizada no local?',
  placeholder: 'Descreva as ações imediatas ou corretivas tomadas para sanar ou mitigar o foco atrativo...',
  y: 6,
  required: true,
  sectionTitle: 'MITIGAÇÃO E OBSERVAÇÕES'
});
const observacoes = makeMultilineCard({
  field: 'observacoes',
  controlSuffix: 'Observacoes',
  label: 'Observações',
  placeholder: 'Informações adicionais, observações de acompanhamento ou pendências (opcional)...',
  y: 7,
  required: false
});
const anexos = setCardPosition(extractCard('Anexos_DataCardPresencaFauna'), 0, 8, 'Parent.Width');
const status = setCardPosition(extractCard('status_DataCardPresencaFauna'), 0, 9, 'Parent.Width');
const ativo = setCardPosition(extractCard('ativo_DataCardPresencaFauna'), 0, 10, 'Parent.Width');

const firstCard = yaml.indexOf('                                                      - aeroporto_DataCardPresencaFauna:');
const buttons = yaml.indexOf('\n                                                - ContainerPresencaFaunaBotoes:', firstCard);
if (firstCard < 0 || buttons < 0) throw new Error('Bloco de DataCards não encontrado');

const cards = [
  aeroporto,
  dataEvento,
  clima,
  local,
  mapaGradeCard,
  focoAtrativo,
  protocolo,
  vulnerabilidade,
  mitigacao,
  observacoes,
  anexos,
  status,
  ativo
].join('\n');
yaml = yaml.slice(0, firstCard) + cards + yaml.slice(buttons);

const onVisibleStart = yaml.indexOf('      OnVisible: |-');
const screenChildren = yaml.indexOf('    Children:', onVisibleStart);
if (onVisibleStart < 0 || screenChildren < 0) throw new Error('OnVisible não encontrado');

const onVisible = `      OnVisible: |-
        =If(
            !varPresencaFaunaEstruturaCarregada || IsEmpty(colPresencaFaunaAeroportos),
            ClearCollect(
                colPresencaFaunaAeroportos,
                [
                    "BACACHERI", "BAGÉ", "CURITIBA", "FOZ DO IGUAÇU",
                    "GOIÂNIA", "IMPERATRIZ", "JOINVILLE", "LONDRINA",
                    "NAVEGANTES", "PALMAS", "PAMPULHA", "PELOTAS",
                    "PETROLINA", "SÃO LUIS", "TERESINA", "URUGUAIANA"
                ]
            );
            ClearCollect(colPresencaFaunaAeroportosFiltro, ["TODOS OS AEROPORTOS"]);
            Collect(colPresencaFaunaAeroportosFiltro, colPresencaFaunaAeroportos);
            ClearCollect(colPresencaFaunaClimas, ["Claro", "Poucas Nuvens", "Encoberto", "Chuva", "Nevoeiro", "Tempestade"]);
            ClearCollect(colPresencaFaunaLocaisPresenca, ["Área Operacional", "Área Patrimonial", "Área de Segurança Aeroportuária - ASA"]);
            ClearCollect(
                colPresencaFaunaFocosAtrativos,
                [
                    "Acúmulo de água nas valas de drenagem",
                    "Acúmulo de materiais e entulhos",
                    "Atividade humana (pesqueiro,parques, etc.)",
                    "Disposição inadequada de resíduos",
                    "Edificações abandonadas",
                    "Gramado com apara de vegetação acumulada",
                    "Grama com o corte recente",
                    "Gramado lateral da pista produzindo sementes",
                    "Ponto de acúmulo temporário de água",
                    "Ponto de referência para empoleiramento de aves",
                    "Presença de carcaças",
                    "Presença de colônia de insetos",
                    "Vegetação com frutos e sementes",
                    "Vegetação servindo de poleiro",
                    "Nenhum",
                    "Ponto de acumulo permanente de agua",
                    "Outros"
                ]
            );
            ClearCollect(
                colPresencaFaunaVulnerabilidades,
                [
                    "Vulnerabilidade na cerca operacional",
                    "Vulnerabilidade na cerca/muro patrimonial",
                    "Vulnerabilidade nas entradas/saídas dos sistemas de drenagem",
                    "Nenhum"
                ]
            );
            Set(varPresencaFaunaEstruturaCarregada, true)
        );
        UpdateContext(
            {
                var_filterButtonAction: "TODOS",
                var_visible: "Novo Registro",
                var_acao: "new",
                var_visibleExcluir: false,
                var_visibleProcessando: false,
                var_dados_presencaFauna: Defaults(tb_presencaFauna)
            }
        );
        Reset(filtro_presenca_fauna_aeroporto);
        Reset(filtro_presenca_fauna_data_inicio);
        Reset(filtro_presenca_fauna_data_fim);
        ResetForm(FormPresencaFauna);
        NewForm(FormPresencaFauna)
`;
yaml = yaml.slice(0, onVisibleStart) + onVisible + yaml.slice(screenChildren);

const formStart = yaml.indexOf('                                                - FormPresencaFauna:');
const formChildren = yaml.indexOf('\n                                                    Children:', formStart);
if (formStart < 0 || formChildren < 0) throw new Error('Formulário não encontrado');
const formHead = yaml.slice(formStart, formChildren).replace('                                                      Height: =1030', '                                                      Height: =1450');
yaml = yaml.slice(0, formStart) + formHead + yaml.slice(formChildren);

yaml = yaml
  .replaceAll('PresencaFauna', 'FocoAtracaoFauna')
  .replaceAll('presenca_fauna', 'foco_atracao_fauna')
  .replaceAll('tb_presencaFauna', 'tb_focoAtracaoFauna')
  .replaceAll('var_dados_presencaFauna', 'var_dados_focoAtracaoFauna')
  .replaceAll('colFocoAtracaoFaunaLocaisPresenca', 'colFocoAtracaoFaunaLocais')
  .replaceAll('attFocoAtracaoFaunaEvidencias', 'attFocoAtracaoFaunaAnexos')
  .replace('  FocoAtracaoFauna:', '  FocoAtracaoFauna:')
  .replace('Text: ="PRESENÇA DE FAUNA"', 'Text: ="FOCO DE ATRAÇÃO DE FAUNA"')
  .replace(
    "<p style='margin:0;'>Registre a presença de fauna, as evidências observadas, o comportamento do animal ou bando e as ações realizadas no local.</p>",
    "<p style='margin:0;'>Registre os focos atrativos de fauna, o quadrante do mapa de grade, as vulnerabilidades identificadas e as medidas de mitigação realizadas.</p>"
  )
  .replaceAll('Registro de presença de fauna salvo com sucesso.', 'Registro de foco de atração de fauna salvo com sucesso.')
  .replaceAll('O registro de presença de fauna está sendo atualizado no sistema.', 'O registro de foco de atração de fauna está sendo atualizado no sistema.')
  .replaceAll('/Lists/tb_focoAtracaoFauna/', '/Lists/tb_focoAtracaoFauna/');

yaml = yaml
  .replace('Text: ="EVIDÊNCIA / COMPORTAMENTO"', 'Text: ="FOCO / QUADRANTE"')
  .replace('Text: ="OCORRÊNCIA"', 'Text: ="PROTOCOLO MNT"')
  .replaceAll('lblFocoAtracaoFaunaCabEspecie', 'lblFocoAtracaoFaunaCabFocoQuadrante')
  .replaceAll('lblFocoAtracaoFaunaCabTipo', 'lblFocoAtracaoFaunaCabProtocolo')
  .replaceAll('htmlFocoAtracaoFaunaEvidenciaComportamento', 'htmlFocoAtracaoFaunaFocoQuadrante')
  .replaceAll('htmlFocoAtracaoFaunaTipo', 'htmlFocoAtracaoFaunaProtocolo')
  .replaceAll('Coalesce(ThisItem.evidencia, "-")', 'Coalesce(ThisItem.foco_atrativo, "-")')
  .replaceAll('Coalesce(ThisItem.comportamento, "-")', 'Coalesce(ThisItem.mapa_grade, "-")')
  .replaceAll('Tooltip: =Coalesce(ThisItem.evidencia, "")', 'Tooltip: =Coalesce(ThisItem.foco_atrativo, "")')
  .replaceAll('Upper(Coalesce(ThisItem.tipo_ocorrencia, "-"))', 'Upper(Coalesce(ThisItem.protocolo_manutencao, "-"))');

// O Schema V3 exige `Screens:` na coluna 1 e a tela exatamente dois espaços
// abaixo. Qualquer recuo na raiz faz o Studio interpretar a tela como uma
// propriedade de PaModule e gera PA1001.
yaml = yaml.replace(
  /^\s*Screens:\s*\n\s*FocoAtracaoFauna:/,
  'Screens:\n  FocoAtracaoFauna:'
);

if (!yaml.startsWith('Screens:\n  FocoAtracaoFauna:\n    Properties:')) {
  throw new Error('Estrutura raiz Source Code inválida para FocoAtracaoFauna');
}

fs.writeFileSync(targetPath, yaml);
