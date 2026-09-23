#!/usr/bin/env bash
# Pipeline de entrega — Inspeções. Falha se qualquer verificação falhar.
#   build/entregar.sh [A|AB|ABC|ABCD]   (lote da frente "leve"; padrão ABCD)
set -euo pipefail
cd "$(dirname "$0")/.."
PY="C:/Users/60-00378/AppData/Local/Python/pythoncore-3.14-64/python.exe"
export PYTHONIOENCODING=utf-8
LOTE="${1:-ABCD}"
export LOTE

echo "── dicionário de propriedades do próprio export"
"$PY" build/dict.py | head -1

echo "── gerando (lote $LOTE)"
"$PY" build/gerar_leve.py --lote "$LOTE"
"$PY" build/gerar_ptbr.py

echo "── YAML e propriedades (PA2108)"
"$PY" build/valida.py out/*.pa.yaml > /dev/null && echo "   ✓ YAML válido, propriedades no dicionário, nomes únicos"

echo "── trava de layout"
"$PY" build/trava_layout.py

echo "── valores por propriedade (nada muda só em espaço; mudanças = lista revisada do lote)"
"$PY" build/checar_valores.py | grep -v "^   ·"

echo "── sintaxe"
"$PY" build/checar_sintaxe.py | tail -1

echo "── referências entre telas (meta 0)"
"$PY" build/checar_cross_screen.py | tail -2

echo "── consultas por linha / delegação"
"$PY" build/checar_por_linha.py | tail -1
"$PY" build/checar_delegacao.py | tail -1

echo "── erro (OnFailure, retorno de fluxo, named formulas)"
"$PY" build/checar_erro.py | tail -1

echo "── variáveis mortas"
"$PY" build/checar_vars_mortas.py | tail -1

echo "── referências de tela / navegação / locale"
"$PY" build/checar_refs.py | tail -1
"$PY" build/auditar_nav.py
"$PY" build/checar_locale.py | tail -1

echo "── idempotência"
ARQS=$(ls out/*.pa.yaml out/*.txt out/Components/*.pa.yaml 2>/dev/null || true)
md5sum $ARQS > build/_h1
"$PY" build/gerar_leve.py --lote "$LOTE" > /dev/null
"$PY" build/gerar_ptbr.py > /dev/null
md5sum -c build/_h1 --quiet && echo "   ✓ mesmo hash em duas execuções"
rm -f build/_h1

echo "── quebra de linha"
if grep -l $'\r' $ARQS 2>/dev/null; then echo "   ✗ CR encontrado"; exit 1; fi
echo "   ✓ 0 CR"

echo
echo "✓ entrega pronta em out/ (lote $LOTE)"
