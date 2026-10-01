# Mapa świata i Latarnia Wglądu — projekt

Data: 2026-09-30 · Kawałek A z „średnich” punktów listy Notion („Gra Akademia Diagnosty”):
- „Daj opcje wejścia na latarnię. Tam będzie mapa całego świata zbudowanego w tej grze. I piękny widok na niebo i słońce oraz księżyc.”
- „Stwórz prawdziwą mapę miasta z lokalizacjami.”

## Ustalenia z rozmowy

| Pytanie | Decyzja użytkowniczki |
|---|---|
| Do czego służy mapa? | **Orientacja** — prawdziwa miniatura świata, budynki z nazwami i numerami, „tu jesteś”; klik w budynek = co w nim jest i ile zrobiono; stare kafelki z postępem zostają jako druga zakładka |
| Co daje latarnia? | **Odkrywa mapę** — pierwsze wejście zdejmuje mgłę z całej mapy (odznaka Kartograf nadal wymaga osobistych odwiedzin) |
| Jak rysować mapę? | **Opcja 1: kolorowe kratki** — 1 kafelek terenu = 1 kolorowy kwadrat; budynki = prostokąty w kolorze dachu z numerem; drzewa = kropki |
| Sekcja 1 (mapa pod M) | zaakceptowana |

Sekcje 2 i 3 dopisałam sama, kiedy użytkowniczka wyszła („pracuj tak, żeby się nie zatrzymywać”). Decyzje podjęte bez niej są oznaczone **[do przejrzenia]**.

## Sekcja 1 — Mapa pod klawiszem M (zaakceptowana)

- Okno „🗺️ Mapa świata” z zakładkami **🗺️ Mapa** (domyślna) i **📈 Postępy** (dotychczasowe kafelki bez zmian).
- **Widok świata:** miasto 3×3, pod nim morze, przerywana trasa promu z Portu do pierwszej wyspy, rząd wysp Archipelagu połączonych mostami, dzielnice „tylko autobusem” (Kampus) obok miasta z przerywaną linią Ψ. Układ liczony z danych (`ZONE_GRID`, `ISLE_GRID`, `ZONES[*].busOnly`) — nowa wyspa czy przystanek pojawi się sam.
- Każda dzielnica: kolory terenu z jej palety, budynki w kolorze dachu, drzewa/krzaki jako kropki, podpis z ikoną i nazwą.
- **„TU JESTEŚ”** — pulsujący znacznik gracza; we wnętrzu (przedmiot, dom, u Pani Haliny) znacznik stoi przy drzwiach tego budynku.
- **Mgła** na dzielnicach nieodwiedzonych i nieodkrytych z latarni, ze znakiem „?”.
- **Klik w dzielnicę → duży widok:** budynki z numerami (te same co tabliczki na domach — ta sama kolejność: po x, potem po y) i nazwami, ikonki tablic informacyjnych, przystanku, teleskopu, latarni. **Klik w budynek → kartka:** nazwa, nr domu, co jest w środku, postęp (pokoje x/y albo poziom katedry). „← Świat” wraca.
- **We śnie** mapa jest rozmyta, z komunikatem, że mapy we śnie nie działają — test rzeczywistości (nawiązanie do Katedry Snu).
- Na telefonie mapa skaluje się do szerokości; klikanie działa tak samo.
- **Poza zakresem:** szybka podróż z mapy, wnętrza na mapie, własne pinezki.

## Sekcja 2 — Latarnia Wglądu

- Latarnia w Porcie Przyszłego Ja (obiekt `lighthouse` na cyplu, x35 y3) dostaje interakcję „Wejdź na latarnię”. Nazwa: **Latarnia Wglądu** (opis Portu już o niej wspomina). **[do przejrzenia]** Latarnia na Wyspie Poznania zostaje ozdobą.
- Wejście nic nie kosztuje; zegar gry płynie jak w innych oknach. **[do przejrzenia]**
- Okno „🗼 Latarnia Wglądu” = animowany widok z galerii:
  - **niebo zależne od godziny gry**: noc (granat, gwiazdy migoczą), przedświt, różowy świt, błękit dnia, złota godzina, fioletowy zmierzch;
  - **słońce** wędruje łukiem 6:00→20:00 (najwyżej ok. 13:00);
  - **księżyc** nocą, z **fazą zależną od dnia gry** (cykl 28 dni, 8 nazwanych faz — pasuje do przyszłych pór roku po 28 dni) **[do przejrzenia]**;
  - na dole: sylwetki dachów Freudowic (nocą zapalone okna), morze, wyspy Archipelagu na horyzoncie; nocą snop światła latarni omiata widok; w dzień płyną chmury.
- Pod widokiem jedna linijka ciekawostki zależnej od pory: iluzja Księżyca (Kaufman i Rock, 1962), widzenie zerkaniem (pręciki na obrzeżu siatkówki), efekt autokinetyczny (Sherif), efekt Purkiniego o zmierzchu, światło poranne a zegar biologiczny (melanopsyna → jądro nadskrzyżowaniowe → melatonina). **[do przejrzenia — dodatek; łatwo usunąć]**
- **Pierwsze wejście:** mgła znika z całej mapy (`state.mapa.odkryta = true`), komunikat „Z latarni widać cały świat — mgła na mapie zniknęła!” i myśl w chmurce.
- Przycisk „🗺️ Mapa świata” otwiera mapę z sekcji 1.

## Sekcja 3 — Technika

- **Osobny `<script>`** „MAPA ŚWIATA I LATARNIA” wstawiony po skrypcie „POPRAWKI Z NOTION”, przed „Zapis w chmurze” — jak moduł z paczki 1: IIFE, zapamiętane oryginały (`mapBase`) i `Object.assign(Game.prototype, …)`. Główny skrypt bez zmian (mniej konfliktów z innymi sesjami, Gemini i GPT).
- Interakcja latarni: dopięcie do `ZoneBuilder.prototype.finalize` (tak jak `npDecorate`) — w Porcie obiekt `lighthouse` dostaje `interact: 'latarnia'`.
- Nadpisane metody: `showMap` (nowe okno z zakładkami; stara treść → zakładka Postępy), `useSpot`, `spotPrompt`.
- **Stan:** `state.mapa = { odkryta: false }` — tworzony leniwie, stare zapisy działają bez migracji.
- **Dane dzielnic:** `this.zones[id] || (this.zones[id] = buildZone(id))` — ta sama ścieżka co przy wejściu do dzielnicy (teren i tak piecze się dopiero w `setZone`), więc na mapie są też dodatki z modułów (Dom Pani Haliny, stacja w Lesie, tablice).
- **Rysowanie:** kanwa na dzielnicę w danej skali, trzymana na obiekcie strefy (`Z._mapImg[px]`) — znika razem ze strefą. Kolor kafelka: `pal[t] || DEFAULT_PAL[t]`. Klikalne obszary liczone z tych samych prostokątów co rysunek.
- **Niebo:** osobna kanwa w oknie, `requestAnimationFrame` tylko gdy okno jest otwarte; stałe losowanie (gwiazdy, dachy) z `mulberry(hashStr(...))`.
- **Testy:** `.mapa-work/mapa.test.js`, uruchamiane w konsoli **tylko pod `http://test.localhost:<port>`** (osobny localStorage; zapis użytkowniczki pod `localhost` nietknięty), z kopią i przywróceniem localStorage. Sprawdzają: układ świata z danych, zgodność numerów z tabliczkami, mgłę przed/po latarni, „tu jesteś” we wnętrzu, dojście do latarni (BFS po `solid`), otwarcie/zamknięcie okien bez błędów, zatrzymanie animacji po zamknięciu, sen → komunikat.
- Kopia pliku przed zmianą: `akademia_diagnosty_miasteczko.przed_mapa.html`.

## Wykonanie (2026-09-30)

- Zrobione zgodnie z sekcjami 1–3; testy `.mapa-work/mapa.test.js`: **51/51** pod `test.localhost`.
- Dodatki wyszłe przy oglądaniu zrzutów: w dużym widoku dzielnicy latarnie, ławki, kontenery itp. są ciemnymi obrysami (bez nich dzielnice wyglądały pusto); trasa promu kończy się na brzegu wyspy (przystań Wyspy Poznania jest po drugiej stronie — linia przecinała ląd); na widoku z latarni ukośne nabrzeże z latarniami nocą; mapa rysuje się od razu po kliknięciu (w tle przeglądarka wstrzymuje animację).
- Zrzuty: `.mapa-work/mapa-swiat.png`, `mapa-osiedle.png`, `latarnia-poludnie.png`, `latarnia-zmierzch.png`, `latarnia-noc.png`.
