# Estrutura proposta — Presença de Fauna

Esta estrutura adapta o padrão da tela `ReporteFauna` para o módulo **Presença de Fauna**. Ela não reutiliza `tb_reporteFauna`, porque aquela lista representa reporte mandatório de colisão/quase colisão/avistamento e possui campos de aeronave que não pertencem à Presença de Fauna.

## Nome da lista

`tb_presencaFauna`

## Colunas do módulo

| Nome interno de trabalho | Nome exibido | Tipo SharePoint | Obrigatório | Opções / padrão |
|---|---|---|---|---|
| `aeroporto` | Aeroporto | Texto com uma linha | Conforme lista | Os 16 aeroportos já usados no modelo. |
| `data_evento` | Data e Hora do Evento (UTC) | Data e Hora | Conforme lista | Uma única coluna, seguindo o padrão do YAML `ReporteFauna`. |
| `clima` | Clima | Texto com uma linha | Conforme lista | `Claro`; `Poucas Nuvens`; `Encoberto`; `Chuva`; `Nevoeiro`; `Tempestade`. |
| `local_geral` | Local | Texto com uma linha | Conforme lista | `Área Operacional`; `Área Patrimonial`; `Área de Segurança Aeroportuária - ASA`. |
| `tipo_ocorrencia` | Foi registrada alguma ocorrência com fauna? | Texto com uma linha | Conforme lista | `Afugentamento`; `Captura`; `Manejo de Brando`; `Coleta de Carcaça`; `Nenhum`; `Presença`; `Vestígio`. |
| `evidencia` | Há evidências? | Texto com uma linha | Conforme lista | `Escuta`; `Ninho`; `Fezes`; `Ovos`; `Presença`; `Penas`; `Pegadas`. |
| `comportamento` | Comportamento do animal ou bando | Texto com uma linha | Conforme lista | `Buscando alimento`; `Se alimentando`; `Empoleirado`; `Parado no chão`; `Dentro do ninho`; `Outros`. |
| `descricao_evento` | Descrição do evento/observação | Texto com várias linhas | Conforme lista | Texto livre. |
| `{Attachments}` | Anexos | Anexos nativos da lista | Não | Habilitar anexos na lista. |
| `status` | Status | Texto (uma linha) | Não | Valor inicial usado pelo padrão: `em_analise`. |
| `ativo` | Ativo | Número | Não | Valor inicial usado pelo padrão de registros: `1`. |

## Colunas padrão do SharePoint

Manter as colunas nativas `ID`, `Criado`, `Criado por`, `Modificado` e `Modificado por`. A tela usa `ID` no histórico e na confirmação de exclusão. A coluna padrão `Título` não aparece no modelo; pode permanecer opcional/oculta, sem ser usada pela tela.

## Observações de compatibilidade

- Os nomes internos e tipos foram informados para a lista `tb_presencaFauna` e foram usados no YAML.
- Mantive os campos de seleção como texto de uma linha porque o modelo existente grava valores com `.Selected.Value` em DataCards `TextualEdit`.
- `data_evento` foi mantida como uma coluna única de data/hora em UTC para seguir o padrão do YAML enviado, apesar de o protótipo React exibir data e hora em controles separados.
- `status` e `ativo` são campos técnicos ocultos do padrão atual; não devem ser apresentados como campos de preenchimento.
- A opção `Manejo de Brando` foi preservada exatamente como aparece no código-base. Confirmar se esse texto é intencional antes de publicar a lista.
- Não criar campos de espécie, matrícula, modelo, operador, fase de voo ou danos: eles pertencem ao `ReporteFauna`, não à tela de Presença de Fauna.
