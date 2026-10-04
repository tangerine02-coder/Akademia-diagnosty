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
`python3 tests/etap1_test.py` i `python3 tests/etap2_test.py` (Playwright, czysty profil przeglądarki; zrzuty w `tests/out/`).

## Dokumenty
- `docs/WIZJA_I_ROADMAP.md` — wizja gry i roadmapa etapów
- `docs/DO_PRZEJRZENIA.md` — decyzje AI czekające na akceptację autorki
- zadania: tablica POPRAWKI w Notion („Gra Akademia Diagnosty”)

## Stare wersje
Kopie `przed_*.html` są w historii Gita (np. `git log --stat`), a nie w folderze.
