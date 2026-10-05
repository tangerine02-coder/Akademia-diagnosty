# Akademia Diagnosty

Pikselowa gra o psychologii w miasteczku Freudowice. Gra ma dwie wersje, każda to jeden plik:

- `Akademia diagnosty/akademia_diagnosty_miasteczko.html` — **wersja akademicka** (dla studentów psychologii: zajęcia z pytaniami otwartymi, wiedza o testach, promotor). To źródło — tu wprowadzamy zmiany.
- `Akademia diagnosty/akademia_diagnosty_publiczna.html` — **wersja publiczna** (dla każdego). Powstaje z wersji akademickiej skryptem — nie edytuj jej ręcznie:

```
python3 narzedzia/zbuduj_publiczna.py
```

## Jak uruchomić
Otwórz plik przez lokalny serwer, np. w folderze `Akademia diagnosty`:

```
python3 -m http.server 8765
```

i wejdź na `http://localhost:8765/akademia_diagnosty_miasteczko.html` (wersja akademicka) albo `http://localhost:8765/akademia_diagnosty_publiczna.html` (wersja publiczna).
Postęp zapisuje się w przeglądarce, osobno dla każdego adresu (host + port) i osobno dla każdej wersji.
Żeby przenieść postęp: 💾 Zapis → ⬇️ Pobierz plik zapisu, a w innym miejscu 📂 Wczytaj z pliku.

## Testy
Przy działającym serwerze (z folderu repo: `python3 -m http.server 8765 --directory "Akademia diagnosty"`):

- `python3 tests/etap1_test.py` … `python3 tests/etap6_test.py` — każdy etap osobno (Etap 6 sprawdza obie wersje — najpierw zbuduj publiczną),
- `python3 tests/czcionki_test.py` — wybór czcionek,
- `python3 tests/przeglad_test.py` — przegląd całej gry (każda dzielnica, miejsce, mieszkaniec i drzwi); z argumentem `tel` na ekranie telefonu.

Wszystkie naraz: `sh tests/wszystkie.sh` (zbuduje wersję publiczną, sam włączy serwer, jeśli trzeba, i przejrzy obie wersje). Testy używają Playwright i czystego profilu przeglądarki; zrzuty ekranu i logi trafiają do `tests/out/`.

## Dokumenty
- `docs/WIZJA_I_ROADMAP.md` — wizja gry i roadmapa etapów
- `docs/DO_PRZEJRZENIA.md` — decyzje AI czekające na akceptację autorki
- `docs/PODZIAL_BAZA_ROZSZERZENIE.md` — podział pytań katedr na wersję publiczną i akademicką (przyjęty 5.10)
- `docs/ARCHITEKTURA.md` — jak zbudowany jest plik gry (bloki, owijki, stan zapisu) — ściąga do kolejnych zmian
- zadania: tablica POPRAWKI w Notion („Gra Akademia Diagnosty”)

## Stare wersje
Kopie `przed_*.html` są w historii Gita (np. `git log --stat`), a nie w folderze.
