# Akademia Diagnosty

Pikselowa gra o psychologii w miasteczku Freudowice. Cała gra to jeden plik:
`Akademia diagnosty/akademia_diagnosty_miasteczko.html`.

## Jak uruchomić
Otwórz plik przez lokalny serwer, np. w folderze `Akademia diagnosty`:

```
python3 -m http.server 8765
```

i wejdź na `http://localhost:8765/akademia_diagnosty_miasteczko.html`.
Postęp zapisuje się w przeglądarce, osobno dla każdego adresu (host + port).
Żeby przenieść postęp: 💾 Zapis → ⬇️ Pobierz plik zapisu, a w innym miejscu 📂 Wczytaj z pliku.

## Testy
Przy działającym serwerze (z folderu repo: `python3 -m http.server 8765 --directory "Akademia diagnosty"`):

- `python3 tests/etap1_test.py` … `python3 tests/etap5_test.py` — każdy etap osobno,
- `python3 tests/czcionki_test.py` — wybór czcionek,
- `python3 tests/przeglad_test.py` — przegląd całej gry (każda dzielnica, miejsce, mieszkaniec i drzwi); z argumentem `tel` na ekranie telefonu.

Testy używają Playwright i czystego profilu przeglądarki; zrzuty ekranu trafiają do `tests/out/`.

## Dokumenty
- `docs/WIZJA_I_ROADMAP.md` — wizja gry i roadmapa etapów
- `docs/DO_PRZEJRZENIA.md` — decyzje AI czekające na akceptację autorki
- `docs/PODZIAL_BAZA_ROZSZERZENIE.md` — propozycja podziału pytań katedr na wersję publiczną i akademicką
- zadania: tablica POPRAWKI w Notion („Gra Akademia Diagnosty”)

## Stare wersje
Kopie `przed_*.html` są w historii Gita (np. `git log --stat`), a nie w folderze.
