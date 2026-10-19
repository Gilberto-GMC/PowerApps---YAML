# Reinserir o `MenuLateral` na Home — à mão, no Studio

O Studio **descarta instância de componente na colagem de YAML**. O bloco
`Control: CanvasComponent` existe em [Home.pa.yaml:210](Home.pa.yaml) e some
toda vez que a tela é colada. Não adianta recolar.

Então: colar a tela, e depois reinserir a instância uma vez, à mão.

## Passos

1. Na árvore, selecionar **`SidebarContainerInterno`** (dentro de
   `SidebarContainer1_1` → `Container44` → `BottomContainer1_1`).
2. **Inserir** → **Personalizado** (ou "Custom") → **MenuLateral**.
3. Arrastar na árvore para ficar **entre `Icon11` e `TextCanvas8`** — o container
   é AutoLayout vertical, a ordem define a posição na tela.
4. Renomear para **`MenuLateral_1`** (o `TextCanvas8` não depende disso, mas
   mantém o YAML e a tela falando a mesma língua).
5. Colar as propriedades abaixo, uma por uma, na barra de fórmulas.

## Propriedades do container

| Propriedade | Fórmula |
| --- | --- |
| AlignInContainer | `AlignInContainer.Stretch` |
| Fill | `thmSuperficie` |
| FillPortions | `1` |
| Height | `Max(App.Height, App.MinScreenHeight)` |
| LayoutMinHeight | `0` |
| LayoutMinWidth | `0` |
| Width | `0` |

`LayoutMaxHeight` e `LayoutMaxWidth` ficam vazias.

## Propriedades personalizadas do componente

| Propriedade | Fórmula |
| --- | --- |
| Home | `Home` |
| Sair | `Login` |
| Navegacao | **não mexer** — o default `If(false, Home)` já cobre |
| funcaoUsuario | `varFuncaoUser` |
| idUsuario | `varIdUser` |
| nomeMenu | `"Home"` |
| nomeUsuario | `varNomeUser` |
| varAeroUser | `varAeroUser` |
| varPerfilUser | `varPerfilUser` |
| var_sideBarWidth | `var_sideBarWidth` |
| menuLoad | `col_menu` |

`TITULO`:

```powerfx
If(
    varPerfilUser = "Base",
    "AIRPORT NOW - AEROPORTO DE " & Upper(varAeroUser),
    varPerfilUser = "Bloco",
    "AIRPORT NOW - BLOCO " & Upper(varBlocoUser),
    varPerfilUser = "Sede",
    "AIRPORT NOW - SEDE",
    "AIRPORT NOW"
)
```

## Consequência para o fluxo de trabalho

Toda tela que instancia componente tem esse custo: a colagem traz o layout e a
lógica, a instância entra à mão. Vale colar a tela **uma vez**, reinserir a
instância, e a partir daí preferir ajuste pontual na propriedade a recolar a
tela inteira — ou aceitar refazer este passo a cada colagem.
