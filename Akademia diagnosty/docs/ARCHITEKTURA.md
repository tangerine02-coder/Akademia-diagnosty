# Architektura pliku gry — ściąga dla kolejnych zmian

*2026-10-05. Gra to jeden plik `akademia_diagnosty_miasteczko.html` (ok. 24 tys. wierszy).*

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
| 15 | `<!-- PROFIL:START -->` … `<!-- PROFIL:END -->` | moduł PROFIL — **generowany** z `.profil-work/src` (nie edytować w HTML) |
| 16 | `<script type="module">` | chmura (Firebase) |

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

## Stan gry (`localStorage['akademia_freudowice_v1']`, też w pliku zapisu)
- Baza: `stats`, `totals`, `home`, `subj` (gwiazdki pokoi), `talked`, `day`, `time`…
- Etapy: `state.e2` (pory, zadania), `state.e3` (wystawa, Leitner, ogród uważności…), `state.e4` (grządki, koszyk, poletko, `dom` — rozbudowa, `stats`), `state.e5` (`read` — kompendium, `halls`, `mentor`, `sen`, `once`).
- Każdy etap ma akcesor tworzący brakujące pola (`e4Data()`, `e5Data()`…), więc stare zapisy działają bez migracji.
- Ustawienia urządzenia (nie w zapisie): `ad_font`, `ad_zoom2`.

## Testy
`tests/etap1_test.py` … `etap5_test.py`, `czcionki_test.py` i `przeglad_test.py` (przegląd całej gry; `tel` = telefon). Wszystkie razem uruchamia `tests/wszystkie.sh` — sam włącza i wyłącza serwer.
