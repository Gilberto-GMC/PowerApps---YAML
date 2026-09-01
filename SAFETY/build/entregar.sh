#!/usr/bin/env bash
# Pipeline de entrega. Falha se qualquer verificação falhar.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "── gerando"
python3 build/gerar.py
python3 build/gerar_apoio.py
python3 build/gerar_forms.py
python3 build/gerar_ptbr.py

echo "── validando YAML e propriedades"
python3 build/valida.py out/*.pa.yaml > /dev/null

echo "── verificações semânticas"
python3 build/checar.py | tail -1

echo "── referências de tela"
python3 build/checar_refs.py

echo "── navegação e botões de voltar"
python3 build/auditar_nav.py

echo "── locale"
python3 build/checar_locale.py

echo "── idempotência"
md5sum out/*.pa.yaml out/*.txt > /tmp/_h1
python3 build/gerar.py > /dev/null
python3 build/gerar_apoio.py > /dev/null
python3 build/gerar_forms.py > /dev/null
python3 build/gerar_ptbr.py > /dev/null
md5sum -c /tmp/_h1 --quiet
echo "   ✓ mesmo hash em duas execuções"

echo
echo "✓ entrega pronta em out/"
