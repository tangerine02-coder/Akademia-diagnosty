# Architektura pliku gry — ściąga dla kolejnych zmian

*2026-10-05, uzupełnione 2026-10-19. Gra to jeden plik `akademia_diagnosty_miasteczko.html` (ok. 25,7 tys. wierszy) — wersja akademicka.*
*Wersja publiczna `akademia_diagnosty_publiczna.html` powstaje z niej skryptem (patrz „Dwie wersje”). Zmiany wprowadzamy tylko w pliku akademickim.*

## Kolejność bloków `<script>`
Każda większa zmiana to **osobny blok**, który owija wcześniejsze funkcje. Nie przepisuje kodu bazowego. Kolejność ma znaczenie, bo późniejszy blok owija wcześniejszy.

| # | Blok (nagłówek w komentarzu) | Co zawiera |
|---|---|---|
| 0 | `<script>` w `<head>` | wybór czcionki z `localStorage['ad_font']` przed pierwszym rysowaniem |
| 1 | AKADEMIA DIAGNOSTY — FREUDOWICE ZDRÓJ | baza: dane (`QUESTIONS_DB`, `ZONES`, `NPCS`, `SUBJECTS`…), budowanie dzielnic, sprite'y, klasa `Game` |
| 2–4 | POPRAWKI Z NOTION, MAPA ŚWIATA, TABLICZKI | poprawki z 30.09 |
| 5–8 | NOC 2026-10-01 · … | teleskop, sklep i kawiarnia, sen i chronotyp, przestawianie mebli (`window.NOC_DOM`) |
| 9 | ETAP 1 · 2026-10-04 | easter eggi, Błonia, wygląd domów, wnętrza, muzyka (`window.ETAP1`) |
| 10 | ETAP 2 · 2026-10-04 | pory roku, zadania „znajdź”, trening snu (`window.ETAP2`) |
| 11 | ETAP 3 · 2026-10-05 | Archiwum 2.0, Dom Żyrafy, Dom Muzyki, Ogród Uważności, Dzielnica Pamięci (`window.ETAP3`) |
| 12 | ETAP 4 · 2026-10-05 | ogródek, poletko, rozbudowa domu, osobowość z wyborów (`window.ETAP4`) |
| 13 | CZCIONKI · 2026-10-05 | okno „Aa” (`window.CZCIONKI`); pary czcionek: `FONT_SETS` w bazie i `:root[data-font]` w CSS |
| 14 | ETAP 5 · 2026-10-05 | hol katedr, kompendium, mini gry katedr, mentorka, Wyspa Snu, list z nowościami (`window.ETAP5`) |
| 15 | ETAP 6 · WERSJE | `const WERSJA`, mapa kategorii `TIERS` (🌍 B / 🎓 A / 🔒 R), 21 nowych zagadnień 🌍, w wersji publicznej sprawdzian zamiast zajęć, znaczki w kompendium (`window.ETAP6`) |
| 16 | ETAP 6 · KATEDRA PSYCHOLOGII RELIGII I PŁCI | `LOCATIONS.religia`, 18 zagadnień, budynek `e6_katedra` w dawnym Magazynie w Porcie, Prof. Rolska, Pan Zasłyszany |
| 17 | ETAP 6 · PROMOTOR — między `<!-- TYLKO-AKADEMIA:START … -->` a `<!-- TYLKO-AKADEMIA:END -->` | Prof. Przypis: etapy, konsultacje, harmonogram (tylko wersja akademicka) |
| 18 | ETAP 7 · AKADEMIA — WEJŚCIE | przycisk 🎓 (`Game.prototype.openAkademia`): w publicznej — opis i przejście do `akademia.html`; w Akademii — konto i wylogowanie przez `window.parent.AD_AKADEMIA` |
| 19 | `<!-- PROFIL:START -->` … `<!-- PROFIL:END -->` | moduł PROFIL — **generowany** z `.profil-work/src` (nie edytować w HTML; wnętrze w zamknięciu `(() => {…})()`, więc np. `PR_TABS` i `PR_SPEC` nie są dostępne z zewnątrz) |
| 20 | `<script type="module">` | chmura (Firebase w Gemini Canvas; poza nim zapis tylko w przeglądarce) |

Gra startuje na zdarzenie `load`, czyli po wykonaniu wszystkich bloków. Dzięki temu owijki działają już przy pierwszym `setZone`.

## Wzorce
- **Owijanie metod**:

  ```js
  const base = {};
  ['setZone', 'useSpot'].forEach(k => base[k] = Game.prototype[k]);
  Object.assign(Game.prototype, {
    setZone(id) { const r = base.setZone.call(this, id); /* … */ return r; }
  });
  ```

- **Owijanie funkcji globalnych**: `bakeRoom`, `buildHomeZone`, `buildingSprite` i inne przypisuje się na nowo (`const b0 = bakeRoom; bakeRoom = function (…) { … b0(…) … }`).
- **Nowa treść w istniejącej dzielnicy**: `ETAP4.extendZone(id, B => { … })`, wcześniej `ETAP3.extendZone`. Najpierw wykonuje się dotychczasowa budowa, potem dodatki. API `B`: `rect`, `obj`, `building`, `interact`, `sign`, `npc`, `fenceRect`, `addHedge`…
- **Miejsca do klikania**: `B.interact(x, y, { kind, w, h })` albo `B.obj(type, x, y, { interact: kind })`. Obsługa trafia do owijki `useSpot` / `spotPrompt` z kluczem `kind`.
- **Mieszkańcy**: wpis w `NPCS[id]` (wygląd `look`, kwestie `lines`) i `B.npc(id, x, y)`. Własną rozmowę daje owijka `talkTo`. Okno dialogu otwieramy przez `Promise.resolve().then(…)`, bo moduł PROFIL zagląda w dialog zaraz po rozmowie.
- **Okna**: `this.openModal(this.panel(tytuł, treść, stopka, 'wide'|'narrow'))`. Element `#modal` jest jeden dla całej gry, więc trzymane okno sprawdzamy przez `root.isConnected`.
- **Mini gry**: silnik pokoi `MINIGAMES` (`quiz`, `pairs`, `sort`, `order`, `tf`…) czyta `SUBJECTS[sid].rooms[i]`. Etap 5 dokłada „wirtualne domy” `SUBJECTS['e5_…']` z flagą `e5` (mniejsze nagrody, własny powrót).
- **Teksty zależne od płci**: `this.prG('{forma żeńska|męska|neutralna}')` (moduł PROFIL).
- **Obserwacje do profilu (🧠 Osobowość)**: funkcja dopisana do `ETAP4.extraObs` zwraca listę `{ k, name, text }`. `text: null` znaczy „??? — jeszcze nie wiem”.

## Dwie wersje: akademicka i publiczna
- Plik akademicki to źródło. Wersję publiczną buduje `python3 narzedzia/zbuduj_publiczna.py` (uruchamia go też `tests/wszystkie.sh`).
- Skrypt: `const WERSJA = 'akademicka'` → `'publiczna'`; wycina z `QUESTIONS_DB` i z list oznaczonych `/* PYTANIA */ [` każde zagadnienie, które w `TIERS` ma `A` albo `R`; wycina bloki `TYLKO-AKADEMIA`; podmienia fragmenty `W-AKADEMICKIEJ` / `W-PUBLICZNEJ`; zmienia `SAVE_KEY` i tytuł; na koniec sprawdza, że w pliku nie został żaden wzorzec odpowiedzi z wyciętych zagadnień ani nazwa testu z listy `ZAKAZANE_W_PUBLICZNEJ`.
- **Inny tekst w każdej wersji** (np. kwestia mieszkańca z nazwą testu), w jednym wierszu: `/*W-AKADEMICKIEJ*/ 'tekst akademicki' /*W-PUBLICZNEJ: 'tekst publiczny' */`. Gra akademicka widzi tylko pierwszy tekst (drugi jest komentarzem), a skrypt zostawia w publicznej tylko drugi. Działa dla każdej wartości: napisu, tablicy, obiektu. Liczba elementów listy musi się zgadzać, więc zamiennik zawsze musi być.
- **Nazwy testów**: gdy nazwa z listy `ZAKAZANE_W_PUBLICZNEJ` (MMPI, WCST, MMSE, EPQ, Leiter, TMS, KRR/KKM/TSR…) trafi do wersji publicznej, skrypt kończy się błędem. Trzeba wtedy oznaczyć miejsce jak wyżej albo zmienić kategorię zagadnienia w `TIERS`. Celowo dozwolone: narzędzia zdyskredytowane z Archiwum Szarlatanerii, efekt Stroopa, Wechsler jako przykład skali IQ, skale z badań i ocena klinicysty (GAF, SDO, RWA, MBEA).
- **Źródła z zajęć** (rok, semestr, prowadzący, notatki, egzaminy) są tylko w wersji akademickiej. Nowy dom-przedmiot: `src: /*W-AKADEMICKIEJ*/ '4 ROK › 7 semestr › …' /*W-PUBLICZNEJ: 'Sam temat' */`. Gdy wzorzec z listy `ZAJECIA_W_PUBLICZNEJ` (np. `ROK ›`, „Notatki dysk”, „Z Twoich materiałów”) trafi do wersji publicznej, skrypt kończy się błędem.
- **Publikacja (Etap 7)**: repo z grą jest prywatne. Stronę gry trzyma Firebase Hosting z folderu `strona/`: `python3 narzedzia/zbuduj_strone.py` kopiuje wersję publiczną jako `strona/index.html` i sprawdza, że w `strona/` nie ma wersji akademickiej; potem `firebase deploy --only hosting,firestore:rules`. Wersja akademicka trafia tylko do bazy: panel `admin.html` → Paczka Akademii.

## Strona i wejście do Akademii (Etap 7)
- `strona/akademia.html` — konto, mail z linkiem, kod; po weryfikacji pobiera paczkę (`akademia/info` + części `akademia/<prefiks>-<n>`: gzip, Bytes, SHA-256), trzyma kopię w IndexedDB (`akademia-diagnosty` → `paczka`) i uruchamia grę w `<iframe id="gra">` z adresem `blob:` tej samej domeny — dzięki temu gra ma zwykły `localStorage` (klucz `akademia_freudowice_v1`) i widzi `window.parent.AD_AKADEMIA` (`email`, `etykieta`, `wyloguj()`, `publiczna()`, `konto()`).
- `strona/konto.js` — jedyne miejsce z Firebase (SDK 11.6.1 z gstatic): konta, kody, dostęp, paczka, panel admina, komunikaty błędów po polsku. `strona/firebase-config.js` — konfiguracja projektu.
- `firebase/firestore.rules` — weryfikacja naprawdę dzieje się tu: dokument `studenci/{uid}` powstaje tylko w jednym zapisie zbiorczym ze zużyciem pasującego kodu (`kody/{kod}`), przy potwierdzonym e-mailu uczelni (albo kodzie „absolwent”). Paczkę czytają tylko konta z dostępem i admini (`admini/{uid}`, dodawani w konsoli).
- Testy: `tests/akademia_test.py` (cały przepływ; Firebase podmieniony na `tests/fake_firebase/` z uproszczoną kopią reguł), `firebase/testy/reguly.test.mjs` (prawdziwe reguły w emulatorze — uruchamia je GitHub Actions, `.github/workflows/reguly.yml`; lokalnie `cd firebase && npm install && npm test`).
- Nowe zagadnienie: obiekt na liście `/* PYTANIA */ [ … ]` (albo w `QUESTIONS_DB`) i wpis w `TIERS`. Brak wpisu = 🌍 (zostaje w obu wersjach).
- Kod tylko dla studentów: osobny `<script>` między komentarzami `<!-- TYLKO-AKADEMIA:START … -->` i `<!-- TYLKO-AKADEMIA:END -->`. Kod wspólny sprawdza `ETAP6.PUB` (albo `WERSJA === 'publiczna'`).
- W wersji publicznej katedry nie mają zajęć z pytaniami otwartymi; `enterBuilding` prowadzi na ✅ Sprawdzian (`e6Sprawdzian`), który zalicza zagadnienia przez zwykłe `markCorrect`.

## Stan gry (`localStorage['akademia_freudowice_v1']`, w wersji publicznej `akademia_freudowice_publiczna_v1`; też w pliku zapisu)
- Baza: `stats`, `totals`, `home`, `subj` (gwiazdki pokoi), `talked`, `day`, `time`…
- Etapy: `state.e2` (pory, zadania), `state.e3` (wystawa, Leitner, ogród uważności…), `state.e4` (grządki, koszyk, poletko, `dom` — rozbudowa, `stats`), `state.e5` (`read` — kompendium, `halls`, `mentor`, `sen`, `once`), `state.e6` (`once`, `pr` — promotor: `works.mgr` / `works.roczna` z `done`, `dates`, `skip`, `custom`, `closed`; `cons` — ostatnie konsultacje bez tekstu fragmentu).
- Każdy etap ma akcesor tworzący brakujące pola (`e4Data()`, `e5Data()`…), więc stare zapisy działają bez migracji.
- Ustawienia urządzenia (nie w zapisie): `ad_font`, `ad_zoom2`.

## Testy
`tests/etap1_test.py` … `etap6_test.py` (Etap 6 testuje obie wersje), `czcionki_test.py`, `przeglad_test.py` (przegląd całej gry; `tel` = telefon; `GAME_URL=…publiczna.html` = wersja publiczna) i `akademia_test.py` (Etap 7: wejście do Akademii i panel admina, port 8766). Wszystkie razem uruchamia `tests/wszystkie.sh` — buduje wersję publiczną, sam włącza i wyłącza serwer i przegląda obie wersje.
