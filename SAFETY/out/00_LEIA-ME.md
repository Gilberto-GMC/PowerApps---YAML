# AirportNow Safety & Fauna — campo Aeroporto em todos os módulos (2026-09-24)

Origem: `SAFETY/AirportNow-Safety&Fauna-2025_20260831145316.zip`, extraído em
`extracted/` (pacote) e `msapp/` (app). As telas daqui partem de `msapp/Src` sem
nenhuma outra alteração: só o campo Aeroporto.

## Regra

- O campo nasce com o aeroporto do usuário (`varAeroUser`).
- Só quem tem **View_safety = 1** troca o aeroporto (`varPerfilSafety`, que já é
  definido no `App.OnStart` do app original: `usuario.View_safety = 1`).
- Quem não tem View_safety vê o próprio aeroporto travado e grava exatamente o que
  gravava antes (`varAeroUser` / `varBlocoUser`).
- Quando o View_safety troca o aeroporto, o bloco gravado acompanha o aeroporto
  escolhido (`colAeros`).

## Arquivos

| Arquivo | Tela | O que muda |
|---|---|---|
| `ScreenColisaoVeiculosForms.pa.yaml` | Colisão de veículos | campo novo logo abaixo da Data e hora |
| `ScreenDerramamentoForms.pa.yaml` | Derramamento de fluidos | caixa Aeroporto ao lado da Data; demais caixas na linha 2; e-mail de notificação usa o aeroporto escolhido |
| `ScreenExcursaoPistaForms.pa.yaml` | Excursão de pista | caixa Aeroporto ao lado da Data; demais caixas na linha 2 |
| `ScreenIncursaoPistaForms.pa.yaml` | Incursão de pista | caixa Aeroporto ao lado da Data; demais caixas na linha 2 |
| `ScreenInterferenciaExternaForms.pa.yaml` | Interferência externa | caixa Aeroporto ao lado da Data; demais caixas na linha 2 |
| `ScreenJetBlastForms.pa.yaml` | Jet Blast | **modelo** ajustado por você no Studio |
| `ScreenOcorrenciaSoloForms.pa.yaml` | Ocorrência de solo | caixa Aeroporto ao lado da Data; demais caixas na linha 2 |
| `ScreenAcessIndFaunaForms.pa.yaml` | Fauna — Acesso indevido | caixa Aeroporto ao lado da Data (caixa da Data volta para 350 de largura) |
| `ScreenFOD.pa.yaml` | FOD | cartão Aeroporto vira lista (era texto livre, editável por todos) |
| `ScreenCSO.pa.yaml` | CSO | cartão Aeroporto vira lista (era travado para todos) |
| `ScreenVistoriaSafetyFauna.pa.yaml` | Vistoria Safety/Fauna | cartão Aeroporto passa a aparecer, como lista e obrigatório (era oculto) |
| `ScreenFaunaForms.pa.yaml` | Fauna — Focos, Presença, Colisões | combos Bloco/Aeroporto: trava passa de perfil "Base" para View_safety |

Padrão definido no `ScreenJetBlastForms` ajustado no Studio (export guardado em
`studio/ScreenJetBlastForms.pa.yaml`, entregue como está):

- **Linha 1:** Data e hora + caixa **Aeroporto** logo à direita (16 px de folga).
- **Linha 2:** as demais caixas da linha de cima (Operador, Voo, Matrícula, Local,
  Condições…) descem 71 px, alinhadas à esquerda com a Data.
- **Corpo** do formulário desce 69 px e perde 60 de altura.

As outras 6 telas do mesmo formato recebem o mesmo padrão pelo gerador, com borda,
legenda e combo copiados das caixas da própria tela. Acesso Indevido (Fauna) só tem a
caixa da Data, que tinha 1030 de largura vazia: voltou para 350 e o Aeroporto fica ao
lado; não há linha 2. Em Colisão, que é uma coluna só, o Aeroporto vem logo abaixo
da Data e hora.

## Como colar

1. Cada arquivo substitui a tela **de mesmo nome** (exibição de código do Studio).
   Não há ordem entre eles, nenhuma tela nova e nada a colar no `App.OnStart`:
   `varPerfilSafety`, `varAeroUser`, `varBlocoUser`, `varIATAUser` e `colAeros` já
   existem no OnStart original.
2. As telas assumem que o app no Studio é o do zip. Se alguma delas foi alterada no
   Studio depois de 31/08, colar por cima desfaz essa alteração. Nesse caso, exporte
   o app de novo e rode o gerador sobre o export novo (ele falha se não achar o
   trecho que espera, em vez de adivinhar).
3. Os arquivos estão em formato invariante (vírgula nos argumentos). Não converter
   para pt-BR.

## Ordem de execução

Antes de colar:
1. Salvar o app no Studio como está (vira uma versão restaurável no histórico).
2. Confirmar que o app é o do zip: existe `ScreenJetBlastForms` e não existe nenhuma `ScreenMod*`.
3. Conferir se a lista `'1 - CSO'` tem a coluna `Aeroporto` (ver Pontos de atenção).

Para cada tela: apagar a tela antiga → colar o arquivo → conferir que voltou com o
**mesmo nome** (se vier `..._1`, a antiga ainda existe: apague as duas e cole de novo).
Enquanto a tela está apagada, as telas que navegam para ela mostram erro; some ao colar.

| # | Arquivo | Por quê nesta posição |
|---|---|---|
| 1 | `ScreenJetBlastForms` | piloto: testar com e sem View_safety antes de seguir |
| 2–8 | `ScreenColisaoVeiculosForms`, `ScreenDerramamentoForms`, `ScreenExcursaoPistaForms`, `ScreenIncursaoPistaForms`, `ScreenInterferenciaExternaForms`, `ScreenOcorrenciaSoloForms`, `ScreenAcessIndFaunaForms` | mesmo padrão do piloto |
| 9 | `ScreenFOD` | cartão do EditForm |
| 10 | `ScreenVistoriaSafetyFauna` | cartão do EditForm |
| 11 | `ScreenCSO` | só depois de confirmar a coluna `Aeroporto` |
| 12 | `ScreenFaunaForms` | a maior (5.452 linhas), por último |

Depois: Salvar → testes abaixo → Publicar.

Para testar sem View_safety no Studio: zerar temporariamente o `View_safety` do seu
usuário na lista `User` e executar o `OnStart` de novo (voltar para 1 no fim).

## Testes depois de colar

Com um usuário **com** View_safety = 1:
- [ ] Em cada um dos 8 formulários o combo abre com o aeroporto do usuário e aceita trocar.
- [ ] Trocar para outro aeroporto, salvar, e conferir no SharePoint `<módulo>_aeroporto`
      e `<módulo>_bloco` do aeroporto escolhido; o registro aparece na lista filtrada por ele.
- [ ] Deixar o combo vazio e salvar: bloqueia com "Atenção todas as informações devem ser preenchidas!".
- [ ] Derramamento: o e-mail mostra o aeroporto escolhido.
- [ ] FOD, CSO, Vistoria: em Novo e em Editar aparece a lista; em visualização aparece o texto gravado.
- [ ] Fauna (Focos, Presença, Colisões): combos Bloco/Aeroporto liberados em Cadastrar.

Com um usuário **sem** View_safety:
- [ ] O combo mostra o próprio aeroporto, travado; o registro grava o aeroporto e o bloco do usuário, como antes.
- [ ] FOD: cartão travado em Novo e em Editar.
- [ ] Fauna: combos travados no próprio bloco/aeroporto.

## Pontos de atenção

- **CSO:** no export, a lista `'1 - CSO'` **não tem** coluna `Aeroporto` (nem antes desta
  entrega; o cartão já existia). Conferir se a coluna existe na lista. Se não existir, o
  cartão acusa erro e o aeroporto não é gravado; criar a coluna (texto) resolve.
- **FOD, perfil Sede sem View_safety:** antes o formulário pegava o aeroporto do filtro da
  lista; agora grava o aeroporto do próprio usuário. Se o cadastro desse usuário não tiver
  aeroporto, o cartão (obrigatório) impede salvar.
- **Filtros das telas de lista** (Bloco/Aeroporto no topo de cada módulo) continuam com a
  regra de antes, por perfil Base/Bloco/Sede. Esta entrega mexe só no aeroporto do registro.
- Fauna em modo edição continua sem permitir trocar o aeroporto (como no original).

## Regerar e validar

```bash
PY="/c/Users/60-00378/AppData/Local/Python/pythoncore-3.14-64/python.exe"
export PYTHONIOENCODING=utf-8
"$PY" build/adicionar_aeroporto.py && "$PY" build/validar_aeroporto.py
```

O validador compara cada tela com o export **por valor** e reprova qualquer mudança fora
da lista declarada, além de nomes duplicados no app, propriedade não comprovada no
export, combo sem a trava de View_safety, Patch gravando `varAeroUser` direto, e Reset
ou validação faltando.
