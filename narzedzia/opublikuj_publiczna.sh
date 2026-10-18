#!/bin/sh
# Publikuje wersję publiczną gry w osobnym, publicznym repo (GitHub Pages).
#
# Użycie (z folderu repo):  sh narzedzia/opublikuj_publiczna.sh ../akademia-diagnosty-gra
# Argument: folder z klonem publicznego repo
#           (git clone https://github.com/tangerine02-coder/akademia-diagnosty-gra ../akademia-diagnosty-gra).
#
# Do repo publicznego trafia TYLKO zbudowana wersja publiczna (jako index.html) i pusty plik .nojekyll.
# Wersja akademicka i reszta tego repo zostają prywatne.
# Opcjonalnie: STOPKA="…" dopisuje akapit na końcu opisu commita.
set -e
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
DEST="$1"
if [ -z "$DEST" ] || [ ! -d "$DEST/.git" ]; then
  echo "Podaj folder z klonem publicznego repo, np.: sh narzedzia/opublikuj_publiczna.sh ../akademia-diagnosty-gra"
  exit 1
fi
DEST="$(cd "$DEST" && pwd)"
if [ "$DEST" = "$ROOT" ] || [ -e "$DEST/Akademia diagnosty" ]; then
  echo "To jest repo z wersją akademicką. Wersję publiczną publikujemy w osobnym repo."
  exit 1
fi

python3 narzedzia/zbuduj_publiczna.py
REV="$(git rev-parse --short HEAD)"
cp "Akademia diagnosty/akademia_diagnosty_publiczna.html" "$DEST/index.html"
: > "$DEST/.nojekyll"

cd "$DEST"
git add index.html .nojekyll
if git diff --cached --quiet; then
  echo "Bez zmian: ta wersja publiczna jest już opublikowana."
  exit 0
fi
if [ -n "$STOPKA" ]; then
  git commit -q -m "Wersja publiczna (z $REV)" -m "$STOPKA"
else
  git commit -q -m "Wersja publiczna (z $REV)"
fi
git push -q origin HEAD:main
echo "Opublikowane ($(git rev-parse --short HEAD)). Strona odświeży się w ciągu 1–2 minut."
