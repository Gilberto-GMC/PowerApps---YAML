const fs = require('node:fs');
const path = require('node:path');

const yamlPath = path.join(__dirname, 'FocoAtracaoFauna.pa.yaml');
const yaml = fs.readFileSync(yamlPath, 'utf8');
const errors = [];

function requireText(description, value) {
  if (!yaml.includes(value)) errors.push(`Ausente: ${description}`);
}

function rejectText(description, value) {
  if (yaml.includes(value)) errors.push(`Encontrado: ${description}`);
}

function getControlBlock(name) {
  const lines = yaml.split('\n');
  const start = lines.findIndex(line => new RegExp(`^\\s+- ${name}:\\s*$`).test(line));
  if (start < 0) return '';

  const indentation = lines[start].match(/^\s*/)[0].length;
  let end = start + 1;
  while (end < lines.length) {
    const match = lines[end].match(/^(\s+)- [A-Za-z_][A-Za-z0-9_]*:\s*$/);
    if (match && match[1].length <= indentation) break;
    end += 1;
  }
  return lines.slice(start, end).join('\n');
}

function allControls() {
  const controls = [];
  const lines = yaml.split('\n');
  for (let index = 0; index < lines.length; index += 1) {
    const match = lines[index].match(/^(\s+)- ([A-Za-z_][A-Za-z0-9_]*):\s*$/);
    if (!match) continue;

    const indentation = match[1].length;
    const typePattern = new RegExp(`^\\s{${indentation + 4}}Control: (.+)$`);
    let controlType = '';
    for (let cursor = index + 1; cursor < lines.length; cursor += 1) {
      if (typePattern.test(lines[cursor])) {
        controlType = lines[cursor].match(typePattern)[1];
        break;
      }
      const next = lines[cursor].match(/^(\s+)- [A-Za-z_][A-Za-z0-9_]*:\s*$/);
      if (next && next[1].length <= indentation) break;
    }
    controls.push({name: match[2], controlType});
  }
  return controls;
}

if (!yaml.startsWith('Screens:\n  FocoAtracaoFauna:')) {
  errors.push('O arquivo não inicia no esquema Source Code da tela FocoAtracaoFauna.');
}
if (!/^Screens:\n {2}FocoAtracaoFauna:\n {4}Properties:/u.test(yaml)) {
  errors.push('Indentação raiz inválida: Screens deve estar na coluna 1 e a tela deve ter dois espaços.');
}

rejectText('placeholder de DataCard do template', '%DATACARD_');
rejectText('propriedade Overflow incompatível', 'Overflow:');
rejectText('carga do histórico em coleção', 'ClearCollect(tb_focoAtracaoFauna');
rejectText('contagem SharePoint não delegável', 'CountRows(tb_focoAtracaoFauna');
rejectText('contagem SharePoint não delegável', 'CountIf(tb_focoAtracaoFauna');
rejectText('referência residual à tela anterior', 'PresencaFauna');
rejectText('referência residual à tela anterior', 'presenca_fauna');
rejectText('campo residual tipo_ocorrencia', 'tipo_ocorrencia');
rejectText('campo residual evidencia', 'ThisItem.evidencia');
rejectText('campo residual comportamento', 'ThisItem.comportamento');
rejectText('campo residual descricao_evento', 'descricao_evento');
rejectText('numeração nos títulos dos campos', 'Text: ="1.');
rejectText('numeração nos títulos dos campos', 'Text: ="2.');
rejectText('numeração nos títulos dos campos', 'Text: ="3.');
rejectText('numeração nos títulos dos campos', 'Text: ="4.');
rejectText('numeração nos títulos dos campos', 'Text: ="5.');
rejectText('numeração nos títulos dos campos', 'Text: ="6.');
rejectText('numeração nos títulos dos campos', 'Text: ="7.');
rejectText('numeração nos títulos dos campos', 'Text: ="8.');
rejectText('numeração nos títulos dos campos', 'Text: ="9.');
rejectText('numeração nos títulos dos campos', 'Text: ="10.');

requireText('fonte de dados do formulário', 'DataSource: =tb_focoAtracaoFauna');
requireText('filtro delegável por ativo', 'ativo = 1');
requireText('filtro delegável por aeroporto', 'aeroporto = _aeroporto');
requireText('limite inicial por data', 'data_evento >= _inicioUtc');
requireText('limite final por data', 'data_evento < _fimUtc');
requireText('carregamento adiado da galeria', 'DelayItemLoading: =true');
requireText('indicador de carregamento', 'LoadingSpinner: =LoadingSpinner.Controls');
requireText('formato persistido do quadrante', 'cmbFocoAtracaoFaunaMapaLetra.Selected.Value & " - " & cmbFocoAtracaoFaunaMapaNumero.Selected.Value');
requireText('restauração da letra durante edição', 'First(Split(Parent.Default, " - ")).Value');
requireText('restauração do número durante edição', 'Last(Split(Parent.Default, " - ")).Value');

for (const field of [
  'aeroporto',
  'data_evento',
  'clima',
  'local_geral',
  'mapa_grade',
  'foco_atrativo',
  'protocolo_manutencao',
  'vulnerabilidade',
  'mitigacao_realizada',
  'observacoes',
  'status',
  'ativo'
]) {
  requireText(`DataField interno ${field}`, `DataField: ="${field}"`);
}

const letterBlock = getControlBlock('cmbFocoAtracaoFaunaMapaLetra');
const numberBlock = getControlBlock('cmbFocoAtracaoFaunaMapaNumero');
const letterItems = letterBlock.match(/Items: =(\[[^\n]+\])/);
const numberItems = numberBlock.match(/Items: =(\[[^\n]+\])/);

if (!letterItems) {
  errors.push('Não foi possível validar as letras do mapa de grade.');
} else {
  const values = JSON.parse(letterItems[1]);
  if (values.length !== 78 || values[0] !== 'A' || values.at(-1) !== 'BZ') {
    errors.push(`Lista de letras incorreta: ${values.length} itens, ${values[0]} até ${values.at(-1)}.`);
  }
}

if (!numberItems) {
  errors.push('Não foi possível validar os números do mapa de grade.');
} else {
  const values = JSON.parse(numberItems[1]);
  if (values.length !== 70 || values[0] !== '1' || values.at(-1) !== '70') {
    errors.push(`Lista de números incorreta: ${values.length} itens, ${values[0]} até ${values.at(-1)}.`);
  }
}

const controls = allControls();
const names = new Set();
for (const control of controls) {
  if (names.has(control.name)) errors.push(`Controle duplicado: ${control.name}`);
  names.add(control.name);

  if (control.controlType === 'TypedDataCard@1.0.7') {
    const block = getControlBlock(control.name);
    const fieldValueCount = (block.match(/MetadataKey: FieldValue/g) || []).length;
    if (fieldValueCount > 1) {
      errors.push(`MetadataKey FieldValue repetida no DataCard ${control.name}: ${fieldValueCount} ocorrências`);
    }
  }

  if (control.controlType === 'TextInput@0.0.54') {
    const block = getControlBlock(control.name);
    if (/\n\s+Default:/.test(block)) {
      errors.push(`Propriedade Default incompatível no TextInput moderno: ${control.name}`);
    }
  }
}

// Um DataCard pode ter somente um filho identificado como FieldValue. O mapa
// de grade possui dois ComboBox visuais, mas apenas o primeiro representa o
// FieldValue canônico do DataCard no esquema do Studio.
const mapaGradeCard = getControlBlock('mapa_grade_DataCardFocoAtracaoFauna');
const mapaFieldValueCount = (mapaGradeCard.match(/MetadataKey: FieldValue/g) || []).length;
if (mapaFieldValueCount !== 1) {
  errors.push(`O DataCard mapa_grade deve ter exatamente um MetadataKey FieldValue; encontrados: ${mapaFieldValueCount}`);
}

const refreshCount = (yaml.match(/Refresh\(tb_focoAtracaoFauna\)/g) || []).length;
if (refreshCount !== 2) {
  errors.push(`Esperados 2 Refresh após gravação/exclusão; encontrados: ${refreshCount}`);
}

if (errors.length > 0) {
  console.error(`Validação falhou com ${errors.length} erro(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Validação concluída: ${controls.length} controles, 78 letras, 70 números e nenhum erro estrutural.`);
