const fs = require('node:fs');
const path = require('node:path');

const yamlPath = path.join(__dirname, 'PresencaFauna.pa.yaml');
const yaml = fs.readFileSync(yamlPath, 'utf8');
const errors = [];

function requireText(description, text) {
  if (!yaml.includes(text)) errors.push(`Ausente: ${description}`);
}

function rejectText(description, text) {
  if (yaml.includes(text)) errors.push(`Encontrado: ${description}`);
}

function controlBlocks(source) {
  const lines = source.split('\n');
  const blocks = [];

  for (let index = 0; index < lines.length; index += 1) {
    const match = lines[index].match(/^(\s+)- ([A-Za-z_][A-Za-z0-9_]*):\s*$/);
    if (!match) continue;

    const indentation = match[1].length;
    let end = index + 1;
    while (end < lines.length) {
      const next = lines[end].match(/^(\s+)- ([A-Za-z_][A-Za-z0-9_]*):\s*$/);
      if (next && next[1].length <= indentation) break;
      end += 1;
    }

    const blockLines = lines.slice(index, end);
    const controlTypePattern = new RegExp(`^\\s{${indentation + 4}}Control: (.+)$`);
    const controlTypeLine = blockLines.find(line => controlTypePattern.test(line));
    const controlType = controlTypeLine ? controlTypeLine.match(controlTypePattern)[1] : '';

    blocks.push({name: match[2], controlType, text: blockLines.join('\n')});
  }

  return blocks;
}

if (!yaml.startsWith('Screens:\n  PresencaFauna:')) {
  errors.push('O arquivo não inicia no esquema Source Code esperado para a tela PresencaFauna.');
}

rejectText('placeholder de DataCard do template', '%DATACARD_');
rejectText('propriedade Overflow incompatível com GroupContainer AutoLayout', 'Overflow:');
rejectText('carga local do histórico da lista', 'ClearCollect(tb_presencaFauna');
rejectText('contagem não delegável da lista SharePoint', 'CountRows(tb_presencaFauna');
rejectText('contagem filtrada não delegável da lista SharePoint', 'CountIf(tb_presencaFauna');
rejectText('validação residual do campo quantidade inexistente', 'txtPresencaFaunaQuantidade');
rejectText('contagem apresentada como total encontrado', 'REGISTROS ENCONTRADOS');
rejectText('Refresh executado ao abrir a aba Registros', '=Refresh(tb_presencaFauna);\n                                                        UpdateContext({var_visible: "Registros"');
rejectText('numeração no título de campo', 'Text: ="4.');
rejectText('numeração no título de campo', 'Text: ="5.');
rejectText('numeração no título de campo', 'Text: ="6.');
rejectText('numeração no título de campo', 'Text: ="7.');
rejectText('numeração no título de campo', 'Text: ="8.');
rejectText('numeração no título de campo', 'Text: ="9.');
rejectText('numeração no título de campo', 'Text: ="10.');

requireText('fonte de dados tb_presencaFauna', 'DataSource: =tb_presencaFauna');
requireText('filtro delegável por ativo', 'ativo = 1');
requireText('filtro delegável por aeroporto', 'aeroporto = _aeroporto');
requireText('limite inferior por data do evento', 'data_evento >= _inicioUtc');
requireText('limite superior por data do evento', 'data_evento < _fimUtc');
requireText('período inicial de 90 dias', 'SelectedDate: =DateAdd(Today(), -90, TimeUnit.Days)');
requireText('data final padrão de hoje', 'SelectedDate: =Today()');
requireText('carregamento adiado dos itens da galeria', 'DelayItemLoading: =true');
requireText('indicador de carregamento da galeria', 'LoadingSpinner: =LoadingSpinner.Controls');
requireText('contagem identificada como carregada', 'REGISTROS CARREGADOS');

for (const field of [
  'aeroporto',
  'data_evento',
  'clima',
  'local_geral',
  'tipo_ocorrencia',
  'evidencia',
  'comportamento',
  'descricao_evento',
  'status',
  'ativo'
]) {
  requireText(`DataField interno ${field}`, `DataField: ="${field}"`);
}

const refreshCount = (yaml.match(/Refresh\(tb_presencaFauna\)/g) || []).length;
if (refreshCount !== 2) {
  errors.push(`Esperadas somente 2 atualizações após gravação/exclusão; encontradas: ${refreshCount}`);
}

const blocks = controlBlocks(yaml);
const controlNames = new Set();
for (const block of blocks) {
  if (controlNames.has(block.name)) errors.push(`Controle duplicado: ${block.name}`);
  controlNames.add(block.name);

  if (block.controlType === 'TextInput@0.0.54' && /\n\s+Default:/.test(block.text)) {
    errors.push(`Propriedade Default incompatível no TextInput moderno: ${block.name}`);
  }
}

if (errors.length > 0) {
  console.error(`Validação falhou com ${errors.length} erro(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Validação concluída: ${blocks.length} controles, sem erros estruturais ou regressões de performance.`);
