#!/usr/bin/env bash
# Pipeline de entrega — app mobile "Inspeção de Pista". Usa o ferramental de ../Inspeções/build
# com cwd nesta pasta (msapp/Src, build/propdict.json e build/allow_*.json deste app).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="C:/Users/60-00378/AppData/Local/Python/pythoncore-3.14-64/python.exe"
T="../Inspeções/build"
export PYTHONIOENCODING=utf-8
export LOTE="Q"
export PROJETO_NOME="Inspeção de Pista"

gerar() {
  rm -f out/*.pa.yaml out/*.txt out/_excecoes_layout.json
  "$PY" $T/gerar_leve.py --lote Q --lotes build/lotes.py
  "$PY" build/gerar_sondas.py
  "$PY" $T/gerar_ptbr.py
}

echo "── dicionário de propriedades do próprio export"
"$PY" $T/dict.py | head -1

echo "── gerando (correções rápidas + tela de sondas)"
gerar

echo "── YAML e propriedades (PA2108)"
"$PY" $T/valida.py out/*.pa.yaml > /dev/null && echo "   ✓ YAML válido, propriedades no dicionário, nomes únicos"

echo "── trava de layout"
"$PY" $T/trava_layout.py

echo "── valores por propriedade (nada muda só em espaço; mudanças = lista revisada)"
"$PY" $T/checar_valores.py | grep -v "^   ·"

echo "── sintaxe"
"$PY" $T/checar_sintaxe.py | tail -1

echo "── referências entre telas"
"$PY" $T/checar_cross_screen.py | tail -1

echo "── consultas por linha / delegação"
"$PY" $T/checar_por_linha.py | tail -1
"$PY" $T/checar_delegacao.py | tail -1

echo "── erro"
"$PY" $T/checar_erro.py | tail -1

echo "── variáveis mortas"
"$PY" $T/checar_vars_mortas.py | tail -1

echo "── referências de tela / navegação / locale"
"$PY" $T/checar_refs.py | tail -1
"$PY" $T/auditar_nav.py
"$PY" $T/checar_locale.py | tail -1

echo "── idempotência"
md5sum out/*.pa.yaml out/*.txt > build/_h1
gerar > /dev/null
md5sum -c build/_h1 --quiet && echo "   ✓ mesmo hash em duas execuções"
rm -f build/_h1

echo "── quebra de linha"
if grep -l $'\r' out/*.pa.yaml out/*.txt 2>/dev/null; then echo "   ✗ CR encontrado"; exit 1; fi
echo "   ✓ 0 CR"

echo
echo "✓ entrega pronta em out/ (Inspeção de Pista)"
