#!/usr/bin/env sh
# Gera e confere a ScreenAPH. Rodar a partir de REA/:  sh build/verificar_aph.sh
# Usa os verificadores do projeto Inspeções (../Inspeções/build), que leem msapp/Src e out/.
set -e
PY="${PY:-/c/Users/60-00378/AppData/Local/Python/pythoncore-3.14-64/python.exe}"
B="../Inspeções/build"
export PYTHONIOENCODING=utf-8

echo "── gerar (2x, o hash tem de ser igual)"
"$PY" build/gerar_aph.py
h1=$(sha256sum out/ScreenAPH.pa.yaml | cut -d' ' -f1)
"$PY" build/gerar_aph.py > /dev/null
h2=$(sha256sum out/ScreenAPH.pa.yaml | cut -d' ' -f1)
[ "$h1" = "$h2" ] || { echo "   ✗ gerador não é determinístico"; exit 1; }
echo "   ✓ determinístico ($h1)"

echo "── dicionário de propriedades do app (msapp/Src)"
"$PY" "$B/dict.py" > /dev/null
echo "── propriedades conhecidas, nomes únicos, raiz"
"$PY" "$B/valida.py" out/ScreenAPH.pa.yaml
echo "── sintaxe"
"$PY" "$B/checar_sintaxe.py" --dir out
echo "── trava de layout"
"$PY" "$B/trava_layout.py"
echo "── valores (conjunto de mudanças = build/propriedades_esperadas.json)"
"$PY" "$B/checar_valores.py"
echo "── tratamento de erro"
"$PY" "$B/checar_erro.py"
echo "── Excel Online: uma condição por consulta (lição 2026-09-18)"
"$PY" build/checar_excel.py
echo "── hora/minuto: branco não pode virar 00:00 (lição 2026-09-18)"
n=$(grep -cE "(Hour|Minute)\(Parent\.Default\)|Value\((Hour|Minute)Value[0-9_]+\.Selected\.Value\), Second\(" out/ScreenAPH.pa.yaml || true)
[ "$n" = "0" ] || { echo "   ✗ $n ocorrências do padrão que grava 00:00 quando a hora está em branco"; exit 1; }
echo "   ✓ nenhum default de hora sem guarda e nenhum Update sem guarda"
echo "── variáveis de estado da ScreenAPH"
if "$PY" "$B/checar_vars_mortas.py" 2>&1 | grep "ScreenAPH"; then
    echo "   ✗ variável morta ou nunca ligada na ScreenAPH"; exit 1
fi
echo "   ✓ nenhuma variável morta ou presa na ScreenAPH"
echo "✓ ScreenAPH pronta para colar"
