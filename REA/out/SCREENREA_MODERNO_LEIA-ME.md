# ScreenREA — painel moderno

Arquivo para colagem: `ScreenREA_Moderno.pa.yaml`.

## O que mudou

- Cabeçalho com o componente nativo `HeaderTitle_14`; busca visível no conteúdo.
- Cards maiores, organizados em grade, mantendo os destinos e links do menu exportado em 19/10/2026.
- Ícones originais dos módulos, lidos de `ThisItem.Logo.Small`; as rotinas usam a imagem `Periodo` já presente no app.
- Rotinas diárias, semanais e mensais abertas em uma janela sobreposta, sem deslocar as seções do painel. Abas permitem trocar de período ali mesmo; a busca e a rolagem ficam dentro da janela.
- Calendário em abas por período, preservando o seletor de aeroporto por perfil.
- Estados vazios ao pesquisar. O corpo rola verticalmente em telas menores.

O visual usa HTML nos títulos das seções. Contêineres nativos controlam a altura, as bordas e o fundo dos cards para evitar cortes e barras internas no Studio. Os ícones auxiliares usam controles `Classic/Icon` do próprio app; os logos de módulos continuam vindo da lista.

## O que eu ajustei

- `ScreenREA.OnVisible` — a aba do calendário e o painel de rotinas agora iniciam em estado definido.
- `lblCalStatus*` — a rotina semanal compara semana **e ano**; a mensal compara mês **e ano**. A consulta filtra `ID_modulo` e aeroporto antes da ordenação por `Data`.
- `Gallery30_6`, `Gallery30_7`, `Gallery30_8` — layout em grade; suas fórmulas `Items` e as ações de cada módulo foram preservadas.
- `TextInputCanvasBuscarREA` — saiu de um contêiner oculto e passou a filtrar as galerias à vista.
- `cntReaRotinas`, `cntReaGestao`, `cntReaOcorrencias`, `cntReaInspecoes` e cards — o fundo e a borda agora são propriedades dos contêineres, evitando o corte vertical observado na primeira colagem.
- `cntReaCalendar` — título e seletor de aeroporto em linhas separadas, evitando a sobreposição observada na primeira colagem.
- `Image1_82`, `Image1_100`, `Image1_101`, `Image1_110` e `Image1_104` a `Image1_106` — ícones originais reinseridos nos cards com dimensões e padding adaptados.
- `cntReaStats`/`htmlReaStats` — bloco de indicadores removido; o AutoLayout posiciona as rotinas logo abaixo da introdução.
- Cabeçalho customizado — substituído pela instância `HeaderTitle_14` do componente `HeaderTitle`; sua seta usa a ação de voltar definida no componente.
- Introdução, títulos de seções, busca, setas de navegação e indicadores do calendário — símbolos de texto trocados por ícones nativos, usando a paleta do painel.
- `cntReaRotinasModal` — a seleção de período agora abre uma janela central com botão de fechar visível, clique fora para fechar, abas, busca própria e estado vazio. Os cards exibem o ícone e a descrição da lista; a galeria mantém o filtro por período e a navegação originais.

## Checklist pós-colagem

1. Substituir a `ScreenREA` existente no mesmo aplicativo. Não manter duas telas com esse nome.
2. Confirmar que o componente `HeaderTitle`, `col_menuModulos`, `col_NavTelas`, `colAeros`, `tbl_Checklist_REA_base`, `varIdUser`, `varAeroUser`, `varPerfilUser` e `varBlocoUser` continuam disponíveis no app; a tela parte dessas dependências já usadas na base atual.
3. Testar as três rotinas, pelo menos um card de cada grupo, a busca e as três abas do calendário no Power Apps Studio.
4. Conferir o App Checker e a apresentação em 1366×768 e 1920×900. A validade final de fórmulas e a renderização do HTML dependem do Studio.

Para gerar novamente a partir do export de referência, executar `python REA/build/gerar_screenrea_moderno.py` na raiz do repositório.
