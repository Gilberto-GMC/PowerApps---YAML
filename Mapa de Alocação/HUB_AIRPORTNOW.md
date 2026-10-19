# Colocar o Mapa de Alocação no hub do AirportNow

O hub abre cada módulo por `Launch(...)` com `LaunchTarget.Replace`. O Mapa entra na tela
**`frmPatiosPistas`** (menu *Pátios e Pistas*), na seção **Diversos**.

| o quê | valor |
|---|---|
| ID do aplicativo | `daaf8c38-3170-4f50-9e14-2e1f61ac24b1` |
| Identificador no catálogo | `ALO-PAT` (reaproveitado, ver abaixo) |
| Menu | `Pátios e Pistas` |
| SubMenu | `Diversos` |
| Parâmetros recebidos | `USUARIO` (único que o Mapa lê), mais `LOGADO` e `HUB` por convenção |

## 1. O item `ALO-PAT` é reaproveitado (19/10/2026)

Decisão do Douglas: em vez de desativar o módulo antigo e cadastrar outro, **o mesmo item passa a
apontar para o Mapa**. O `ALO-PAT` era o **App B**, "Reserva e Alocação de Pátios"
(`bbf03a1d-0a54-4732-bbaa-1c5f8be757d0`), que gravava em `tbl_aloca_aeronave` e disputava as mesmas
posições de pátio sem enxergar o Mapa.

Vantagem de reaproveitar: quem já conhecia o cartão continua achando no mesmo lugar, e não sobra
item morto no catálogo.

No formulário **Admin › Módulos**, no item `ALO-PAT`:

| campo | valor |
|---|---|
| Titulo | `Mapa de Alocação` |
| Menu | `Pátios e Pistas` |
| SubMenu | `Diversos` |
| Status | `Ativo` |
| Identificador | **`ALO-PAT`, sem mexer** |
| Logo | trocar pela imagem do Mapa (a galeria usa `Logo.Small`) |
| Descricao | texto do ⓘ do cartão |
| Palavras Chave | aproveitar as que já estão; valem para o Mapa também |

> O `Identificador` é o que a tela usa para decidir qual app abrir, e a tela foi escrita para
> `ALO-PAT`. Mudá-lo aqui faz o cartão cair no ramo genérico, tentar `Navigate` por `col_NavTelas` —
> que não tem tela para o Mapa — e o clique não faz nada.

## 2. Tela `frmPatiosPistas.pa.yaml`

Colar a tela inteira. O que mudou em relação à versão que estava no app:

- `Label6_328` — rótulo **"Diversos:"**, em Y 527;
- `Gallery30_3` — galeria da seção, em Y 547, filtrando `SubMenu.Value = "Diversos"`;
- dentro dela, o cartão (`Container84_27` e filhos), igual aos das outras seções, com o `OnSelect`
  abrindo o Mapa quando `Identificador = "ALO-PAT"`;
- **o ramo que abria o App B foi removido** do `OnSelect` da galeria de *Ocorrências envolvendo*.
  Não sobrou nenhuma referência ao `bbf03a1d-…` em `frmPatiosPistas`.

As três seções existentes não foram tocadas no resto. A nova entra em 527/547 porque as anteriores
ocupam 77/97, 227/247 e 377/397, e `cntHome` tem 718 de altura — a seção nova termina em 667, ainda
dentro.

⚠️ **A ordem importa.** Enquanto a tela antiga estiver publicada e o item já estiver em
`SubMenu = Diversos`, o cartão some do hub: nenhuma galeria filtra *Diversos* ainda. Ele volta
quando a tela nova for colada e publicada. Se isso incomodar, mude o SubMenu só na hora de publicar.

## 3. O que o Mapa faz com os parâmetros

Só `USUARIO` importa: é o ID na lista `User` do AirportNow, e dele saem perfil, aeroporto e
permissão de edição (`usrMapa` em `App_Formulas_Mapa.txt`). Aberto fora do hub, o Mapa cai no
e-mail do login — ou seja, abrir direto continua funcionando.

`LOGADO` e `HUB` são ignorados pelo Mapa; vão junto para manter o padrão dos outros módulos.

## O App B continua publicado

Tirar o atalho do hub não desliga o app antigo: quem tiver o link direto ainda consegue gravar em
`tbl_aloca_aeronave`, e nada disso aparece no Mapa. Despublicá-lo ou deixá-lo somente leitura é a
Etapa 1 do plano de unificação e continua em aberto.
