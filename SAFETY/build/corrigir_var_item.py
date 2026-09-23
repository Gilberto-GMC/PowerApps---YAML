# -*- coding: utf-8 -*-
"""Correção pontual (roda 1x) dos 30 erros do ScreenExcluir achados no
Verificador de aplicativo em 2026-09-22.

Causa: o botão "Excluir" de cada um dos 7 módulos navega pra ScreenExcluir
passando {var_item: ThisItem, ...} — ThisItem é um registro de uma tabela do
SharePoint DIFERENTE em cada módulo (Colisão de Veículos, Derramamento, etc).
Como os 7 apontam pro MESMO destino (ScreenExcluir), a variável de contexto
"var_item" dessa tela acumula 7 formatos de registro incompatíveis entre si.
O Studio unifica o tipo e reprova toda leitura de campo específico de módulo
(var_item.colVei_id, var_item.derFlu_id, etc. — só var_item.ID, comum às 7
tabelas do SharePoint, não dá erro).

var_item só é lido de duas formas em ScreenExcluir: var_item.ID e
var_item.<modulo>_id (confirmado por grep — nenhum outro campo, nenhum uso do
registro inteiro). Fix: trocar o registro inteiro por dois números (tipo
homogêneo nos 7, sem ambiguidade) —
  var_item_id:    ThisItem.ID           (substitui var_item.ID)
  var_item_chave: ThisItem.<modulo>_id  (substitui var_item.<modulo>_id)
e não passar mais var_item.
"""
import re
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODULOS_EXCLUIR = [
    ("ScreenColisaoVeiculos", "colVei_id"),
    ("ScreenDerramamentoFluido", "derFlu_id"),
    ("ScreenExcursaoPista", "excPista_id"),
    ("ScreenIncursaoPista", "incPista_id"),
    ("ScreenInterferenciaExterna", "intExt_id"),
    ("ScreenJetBlast", "jetBlast_id"),
    ("ScreenOcorrenciaSolo", "ocoSolo_id"),
]


def corrigir_botao_excluir(nome_arquivo, campo_id):
    path = os.path.join(RAIZ, 'msapp', 'Src', f'{nome_arquivo}.pa.yaml')
    texto = open(path, encoding='utf-8').read()
    padrao = re.compile(r'\n( *)var_item: ThisItem,\n')
    m = padrao.search(texto)
    if not m:
        if 'var_item_chave: ThisItem.' in texto:
            print(f"  [{nome_arquivo}] ja corrigido, pulando")
            return
        raise SystemExit(f"[{nome_arquivo}] 'var_item: ThisItem,' nao encontrado")
    pad = m.group(1)
    novo = f"\n{pad}var_item_id: ThisItem.ID,\n{pad}var_item_chave: ThisItem.{campo_id},\n"
    texto = texto[:m.start()] + novo + texto[m.end():]
    open(path, 'w', encoding='utf-8', newline='\r\n').write(texto)
    print(f"  [{nome_arquivo}] var_item: ThisItem -> var_item_id + var_item_chave (ThisItem.{campo_id})")


def corrigir_screen_excluir():
    path = os.path.join(RAIZ, 'msapp', 'Src', 'ScreenExcluir.pa.yaml')
    texto = open(path, encoding='utf-8').read()
    antes = texto
    texto = texto.replace('var_item.ID', 'var_item_id')
    for _nome, campo in MODULOS_EXCLUIR:
        texto = texto.replace(f'var_item.{campo}', 'var_item_chave')
    sobrou = re.findall(r'var_item\.\w+', texto)
    if sobrou:
        raise SystemExit(f"[ScreenExcluir] sobrou referencia nao mapeada: {set(sobrou)}")
    if texto == antes:
        print("  [ScreenExcluir] ja corrigido, pulando")
        return
    open(path, 'w', encoding='utf-8', newline='\r\n').write(texto)
    print("  [ScreenExcluir] var_item.ID -> var_item_id ; var_item.<modulo>_id -> var_item_chave")


def main():
    for nome, campo in MODULOS_EXCLUIR:
        corrigir_botao_excluir(nome, campo)
    corrigir_screen_excluir()


if __name__ == '__main__':
    main()
