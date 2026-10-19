# Colocar o Mapa de Alocação no hub do AirportNow

O hub abre cada módulo por `Launch(...)` com `LaunchTarget.Replace`. O Mapa entra na tela
**`frmPatiosPistas`** (menu *Pátios e Pistas*), numa seção nova chamada **Outros**.

| o quê | valor |
|---|---|
| ID do aplicativo | `daaf8c38-3170-4f50-9e14-2e1f61ac24b1` |
| Identificador no catálogo | `MAPA-ALO` |
| Menu | `Pátios e Pistas` |
| SubMenu | `Outros` |
| Parâmetros recebidos | `USUARIO` (único que o Mapa lê), mais `LOGADO` e `HUB` por convenção |

## 1. Lista dos módulos (origem de `col_menuModulos`)

A seção só aparece quando houver item ativo nela — galeria vazia some sozinha, mas o rótulo "Outros:"
fica. Então o cadastro vem **antes** de colar a tela.

1. Na coluna de escolha **SubMenu**, acrescentar o valor **`Outros`**. Sem isso o item não pode ser
   gravado.
2. Criar o item do módulo:

| campo | valor |
|---|---|
| Titulo | `Mapa de Alocação` |
| Menu | `Pátios e Pistas` |
| SubMenu | `Outros` |
| Status | `Ativo` |
| Identificador | `MAPA-ALO` |
| Logo | imagem do módulo (a galeria usa `Logo.Small`) |
| Descricao | texto do botão de informação (ⓘ) do cartão |

> O `Identificador` é o que a tela usa para decidir qual app abrir. Se ele vier diferente de
> `MAPA-ALO`, o cartão cai no ramo genérico e tenta `Navigate` por `col_NavTelas` — que não tem tela
> para o Mapa, e o clique não faz nada.

## 2. Tela `frmPatiosPistas.pa.yaml`

Colar a tela inteira. O que foi acrescentado, em relação à versão que estava no app:

- `Label6_328` — rótulo **"Outros:"**, em Y 527;
- `Gallery30_3` — galeria da seção, em Y 547, filtrando `SubMenu.Value = "Outros"`;
- dentro dela, o cartão (`Container84_27` e filhos), igual aos das outras seções, com o `OnSelect`
  do botão abrindo o Mapa quando `Identificador = "MAPA-ALO"`.

As três seções existentes não foram tocadas. A nova entra em 527/547 porque as anteriores ocupam
77/97, 227/247 e 377/397, e `cntHome` tem 718 de altura — a seção nova termina em 667, ainda dentro.

## 3. O que o Mapa faz com os parâmetros

Só `USUARIO` importa: é o ID na lista `User` do AirportNow, e dele saem perfil, aeroporto e
permissão de edição (`usrMapa` em `App_Formulas_Mapa.txt`). Aberto fora do hub, o Mapa cai no
e-mail do login — ou seja, abrir direto continua funcionando.

`LOGADO` e `HUB` são ignorados pelo Mapa; vão junto para manter o padrão dos outros módulos.

## O `ALO-PAT` foi aposentado (19/10/2026)

Decisão do Douglas: *"não vamos mais usar o app antigo"*. O identificador `ALO-PAT` abria o
`bbf03a1d-0a54-4732-bbaa-1c5f8be757d0` — o **App B**, "Reserva e Alocação de Pátios", que gravava em
`tbl_aloca_aeronave` e disputava as mesmas posições de pátio sem enxergar o Mapa.

Duas coisas, e as duas precisam ser feitas:

1. **Na lista dos módulos**, pôr o item do `ALO-PAT` em `Status = Desativado`. É isso que tira o
   cartão do hub: as galerias filtram `Status.Value = "Ativo"`.
2. **Na tela** (já feito neste arquivo), o ramo do `Switch` que abria aquele app foi removido do
   `OnSelect` da galeria de *Ocorrências envolvendo*. Não sobrou nenhuma referência ao app antigo
   em `frmPatiosPistas`.

O App B em si continua publicado no ambiente. Despublicá-lo ou deixá-lo somente leitura é a Etapa 1
do plano de unificação e continua em aberto — enquanto ele existir, quem tiver o link direto ainda
consegue gravar por lá.
