# Pacotes herdados — importar sem solução

Um zip por fluxo, para **Power Automate > Meus fluxos > Importar > Importar
Pacote (Legado)**. Gerados por `../gerar_pacotes_fluxos_individuais.py` a partir
das definições corrigidas em `../MigracaoAIRPORTNOW_src/Workflows` (mesmo
conteúdo do pacote 1.0.0.5).

| Zip | Fluxo | Conectores |
|---|---|---|
| `CriarChatAcionamentosPLEMPRAI.zip` | Criar chat de acionamentos PLEM/PRAI | Teams, SharePoint, Outlook |
| `EnviarAcionamentoComOpcao.zip` | Enviar Acionamento com Opcao | Teams, SharePoint, Outlook |
| `AirportNowNotificacaoDeAcionamento.zip` | Airport now - notificação de acionamento | Teams, SharePoint, Outlook |
| `EnviarAtividadeParaChatTeams.zip` | Enviar Atividade para chat teams | Teams |

## Escolha *Atualizar*, não *Criar como novo* (2026-08-24)

Os fluxos foram refatorados (mensagens padronizadas, e-mail redesenhado,
resposta imediata ao app, validações, retry). **Nenhuma assinatura de gatilho
mudou** — então a importação não exige mexer no app, desde que você faça uma
coisa na caixa *Configuração de Importação*:

> escolha **Atualizar** e selecione o fluxo que já existe no ambiente.

Com *Atualizar* a definição é substituída e o **ID do fluxo é preservado**: o
app continua apontando para ele e nada precisa ser removido nem re-adicionado
em *Dados > Power Automate*. Com *Criar como novo* entra uma cópia com ID novo,
o app continua chamando a antiga, e reapontá-lo exige remover/re-adicionar — que
é onde o Studio renomeia para `EnviarAtividadeparachatteams_1` e o YAML colado
deixa de encontrar a referência.

Os pacotes já vêm com `Atualizar` como opção sugerida, então é o que o wizard
abre por padrão.

O `CriarChatAcionamentosPLEMPRAI.zip` agora pede **2 conexões** em vez de 3: o
conector do Outlook saiu junto com o e-mail duplicado que esse fluxo mandava.

Detalhes do que mudou em `../PADRAO_MENSAGENS_TEAMS.md`; para ver as mensagens
prontas, `../previa/mensagens_acionamento.html`.

## O que estava errado antes (MissingPackageManifest)

A primeira versão do gerador escrevia só 2 arquivos: `manifest.json` na raiz e
`Microsoft.Flow/flows/<res>/definition.json`. Faltava o
**`Microsoft.Flow/flows/manifest.json`** — o manifesto de assets
(`{"packageSchemaVersion":"1.0","flowAssets":{"assetPaths":["<res>"]}}`), que é
o que o importador procura ao entrar na pasta `Microsoft.Flow`. Daí a mensagem
"a pasta 'Microsoft.Flow' não contém o arquivo de manifesto do pacote".
Faltavam também `apisMap.json` e `connectionsMap.json`, e o recurso do fluxo no
manifesto trazia `id`/`name` (o importador tentaria casar com um fluxo já
existente em vez de criar um novo).

Estrutura agora, idêntica à de um export real do portal:

```
manifest.json
Microsoft.Flow/flows/manifest.json
Microsoft.Flow/flows/<res>/definition.json
Microsoft.Flow/flows/<res>/apisMap.json
Microsoft.Flow/flows/<res>/connectionsMap.json
```

As connection references do Dataverse (`iem_sharedteams_5a6f9`,
`iem_sharedsharepointonline_27185`, `iem_sharedoffice365_d341f`) viraram
conexões `Embedded` — pacote herdado não suporta connection reference. No
wizard de importação o Power Automate vai pedir uma conexão para cada conector
(o nome da connection reference original aparece como rótulo, para você saber
qual escolher).

## Ao importar, atenção

- **Envie o zip exatamente como está.** Não descompacte e recompacte: o
  `manifest.json` tem que ficar na raiz do zip, sem pasta envolvendo.
- Escolha **Atualizar** no primeiro item (ver acima) e mapeie as conexões em
  *Recursos Relacionados*. O botão Importar só habilita depois disso.
- Os fluxos entram em **Meus fluxos** como fluxos novos, com **IDs novos** —
  não substituem os que já estão na solução gerenciada MigracaoAIRPORTNOW.
  O app chama `'CriarchatdeacionamentosPLEM/PRAI'.Run`,
  `EnviarAcionamentocomOpcao.Run` e `EnviarAtividadeparachatteams.Run`; para o
  app passar a usar as cópias importadas é preciso **remover e re-adicionar o
  fluxo no Power Apps Studio** (Dados > Power Automate), senão ele continua
  chamando os da solução.
- Os 4 fluxos são disparados pelo app (gatilho PowerApps V2), então as cópias
  não rodam sozinhas — não há risco de disparo duplicado enquanto o app não for
  reapontado.
- Referências de site/lista do SharePoint viajam dentro da definição e continuam
  apontando para o mesmo ambiente.

Se preferir manter tudo na solução, use `../MigracaoAIRPORTNOW_1_0_0_5_managed.zip`
(Soluções > Importar) ou os zips de `../solucoes_fluxos/`.
