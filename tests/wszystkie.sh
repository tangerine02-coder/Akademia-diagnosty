#!/bin/sh
# Uruchamia wszystkie testy gry. Użycie (z folderu repo): sh tests/wszystkie.sh
# Jeśli na porcie 8765 nic nie działa, skrypt sam włącza serwer i wyłącza go na końcu.
cd "$(dirname "$0")/.." || exit 1
STARTED=""
if ! python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/akademia_diagnosty_miasteczko.html', timeout=2)" 2>/dev/null; then
  python3 -m http.server 8765 --directory "Akademia diagnosty" >/dev/null 2>&1 &
  STARTED=$!
  sleep 1
fi
mkdir -p tests/out
FAIL=0
for t in etap1_test etap2_test etap3_test etap4_test etap5_test czcionki_test przeglad_test; do
  printf '%-16s ' "$t"
  if python3 "tests/$t.py" > "tests/out/$t.log" 2>&1; then echo "OK"; else echo "BŁĄD (szczegóły: tests/out/$t.log)"; FAIL=1; fi
done
[ -n "$STARTED" ] && kill "$STARTED"
exit $FAIL
