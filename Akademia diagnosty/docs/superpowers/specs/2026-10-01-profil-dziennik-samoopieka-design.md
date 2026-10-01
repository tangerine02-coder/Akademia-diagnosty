# Profil, dziennik, samoopieka, progresja, wybory i treści dla laika — projekt

*2026-10-01, noc. Budowa pierwszych 🔨 z `docs/WIZJA_I_ROADMAP.md`.*
*Decyzje autorki — z pytań przed snem. Decyzje podjęte bez niej: **[do przejrzenia]**.*

## Cel

Gra ma podmiotowo traktować gracza: **obserwuje, nie etykietuje**, nie zmusza, nie karze, nie moralizuje.
Ta noc buduje fundament, do którego będą pisać kolejne systemy: **dziennik** (serce), **profil**,
**samoopieka**, **progresja** (dojrzewanie + droga diagnosty), **wybory** (etyczne, relacyjne), potem **treści dla laika**.

## Decyzje autorki (2026-10-01)

| Temat | Decyzja |
|---|---|
| Kolejność | dziennik + refleksja + rytuały → profil → samoopieka → progresja → dylematy/NVC → treści laika |
| Poziomy XP | XP i „Lv” zostają w HUD jako licznik nauki; pod imieniem nowy podpis: „🌿 Mieszkanka · 📋 Stażystka (skłania się ku: 💬 Klinicystka)” |
| Potrzeby | żadnych nowych pasków; myśli nad głową + karta „Jak się mam” w profilu (słowa i emotki, bez liczb) |
| Prywatność | dziennik i „Ja” zapisują się **do chmury jak reszta** |
| Dwa pliki | **nie ruszać podziału** — bez znaczników i flag |
| Formy | trzecia forma: **neutralna (dukaizmy)** — „zrobiłoś”, „byłom”, „gotowe”; zaimki = osobne wolne pole |
| Konsekwencje | **łagodne, bez wpływu na naukę** — wolniejszy chód, myśli, wolniejszy powrót energii; punkty i Dopaminki bez kar |
| Treści laika | **jak najwięcej**, po fundamencie, **rozsiane po mieście** (pojedyncze domy w dzielnicach), forma scenek / „mit czy fakt” / historii |

## Architektura

- Jeden nowy `<script>` „PROFIL, DZIENNIK I SAMOOPIEKA” tuż przed `<!-- Zapis w chmurze`, jak pozostałe moduły:
  IIFE owijające `Game.prototype` (zapamiętane bazy w `prBase`). Źródło w `.profil-work/src/*.js`,
  sklejane i wstrzykiwane skryptem `.profil-work/build.js` między `<!-- PROFIL:START -->` i `<!-- PROFIL:END -->`.
- Punktowe zmiany w głównym skrypcie tylko tam, gdzie owijanie byłoby kruche: `gf()` (trzecia forma) i przycisk formy w kreatorze.
- Stan: `state.prof` (tworzony leniwie przez `profData()`, stare zapisy działają bez migracji):
  - `ja` — pola tożsamości (wszystkie opcjonalne),
  - `journal` — wpisy `{ id, d, t, typ, q, a, tags }` (typ: `wieczor`, `rano`, `refleksja`, `wybor`, `cytat`, `mysl`, `wlasny`, `rozmowa`),
  - `pending` — pytania, które czekają (zaproszenie odłożone „na później”),
  - `obs` — liczniki obserwacji (styl poznawczy, relacyjny, radzenie sobie, ciekawość, odwaga…),
  - `needs` — 5 potrzeb 0–100 (energia to istniejące `state.energy`),
  - `spec` — aktywność akademicka per katedra (z wygaszaniem → płynna specjalizacja),
  - `path` — etapy dojrzewania i drogi diagnosty + kolejka ciepłych komunikatów NPC,
  - `choices`, `talks`, `exp` — wybory etyczne, rozmowy NVC, eksperymenty od NPC,
  - `opt` — ustawienia rytuałów (pytaj / nie pytaj).

## 1. Dziennik i pytania refleksyjne

- **Zaproszenie, nie przerwanie.** Pytanie pojawia się jako mała karteczka w rogu („💭 Myśl do zapisania…”):
  `Odpowiem` / `Później` / ✕. „Później” odkłada je do dziennika (zakładka „Czekają”). Po 40 s karteczka sama znika (też do „Czekają”). **[do przejrzenia]**
- Wyzwalacze (limit: 3 zaproszenia dziennie + rytuały, min. 3 min przerwy):
  po rozmowie z NPC (rzadko, cytuje jego słowa), po nieudanym bloku (<50%), po bezbłędnym bloku, po śnie,
  po dylemacie etycznym, rzadko losowo w domu.
- Odpowiedź: wolne pole, zawsze do dziennika; po zapisie mikro-animacja oddechu (ulga).
- **Analiza słów kluczowych** (prosty słownik rdzeni jak w `verifyAnswer`): emocje, „bo/dlatego” (analitycznie) vs „czuję/wydaje mi się” (intuicyjnie),
  radzenie sobie (zadaniowo / emocjonalnie / unikowo). Wynik tylko podbija liczniki w `obs` — nic nie jest pokazywane jako ocena.
- Dotychczasowe notatki z ławek (`state.np.notes`) i dziennik snów pokazują się w tym samym dzienniku.

## 2. Rytuały

- **Wieczorny rytuał** przy zwykłym śnie (łóżko, „Tak, idę spać”): „Jak minął Ci ten dzień?” + „Co Cię dziś zaskoczyło?” (wolne pola) i wybór:
  📓 tylko zapisz · 🍵 herbata (spokój, lepszy poranek) · 📞 zadzwoń do bliskiej osoby (więzi; imiona z pola „Rodzina”, jeśli są) · 😴 po prostu spać.
  Nigdy przy omdleniu o 2:00 i przy wybudzeniu ze snu świadomego.
- **Poranny check-in**: „Jak się dziś czujesz?” 🌞 Dobrze / 🌤️ Średnio / 🌧️ Ciężko / ✍️ opowiem więcej / pomiń.
  „Ciężko” = łagodniejszy dzień: jedno zadanie dnia zamienia się na „Zrób coś dobrego dla siebie”, dom regeneruje szybciej,
  myśli postaci są łagodniejsze. **Żaden wybór nie jest „zły”.** **[do przejrzenia]**
- Oba rytuały można wyłączyć w profilu (zasada wolności).

## 3. Profil (przycisk 👤 Profil na dolnej belce, klawisz P)

Lewa kolumna: popiersie postaci, imię, zaimki, podpis drogi, mini „Jak się mam”. Zakładki:
- **👤 Ja** — imię, wiek, forma (ż/m/neutralna), zaimki, orientacja, pochodzenie, rodzina, wartości (chipy + wolny tekst),
  wierzenia/duchowość, neuroróżnorodność (chipy + tekst), mocne strony, z czym się zmagam. Wszystko opcjonalne, edycja w każdej chwili, „gra nigdy tego nie ocenia”.
- **🧠 Osobowość** — obserwacje w formie „Zauważam…/Może…?” dla 8 wymiarów; na starcie „jeszcze nie wiem”.
- **💛 Jak się mam** — 6 potrzeb słowami (bez liczb), z łagodną sugestią.
- **📖 Dziennik** — oś czasu po dniach, filtry, „✍️ Nowy wpis”, pytania czekające.
- **🌱 Droga** — dojrzewanie osobiste i droga diagnosty (etapy, co je przybliża — opisowo), studium przypadku, superwizja.
- **🏆 Osiągnięcia** — odznaki (istniejące) + etapy + ukończone domy.
- **📊 Profil diagnosty** — radar kompetencji z 9 katedr, styl diagnostyczny (etykieta opisowa, np. „Empatyczna empirystka”), najsilniejszy/najsłabszy obszar, historia superwizji.

Stary „📜 Dziennik” (zadania, postępy, powtórki, statystyki) zostaje pod J i dostaje etykietę **„📜 Zadania”** **[do przejrzenia]**. Biurko w domu pyta: zadania czy mój dziennik.

## 4. Samoopieka

Potrzeby (0–100, wewnętrznie): 🔋 energia (istniejąca), 💛 nastrój, 🫂 więzi, 🧘 spokój, 🎯 sens, 🍽️ ciało.
- Źródła: rozmowy, jedzenie (samemu / z kimś), dom, ławki, dziennik, herbata, sen, nauka i sukcesy, spacer (kroki).
- Upływ z czasem gry; nocą reset do sensownych wartości zależnych od długości snu.
- **Sygnały**: myśli nad głową przy niskich wartościach (z przerwą, nigdy w trakcie nauki), ciepłe momenty (💛 przy jedzeniu z kimś).
- **Konsekwencje (łagodne)**: niski sen/ciało/energia → chód wolniejszy (×0,85, przy bardzo niskich ×0,75); niski spokój → energia z kawy/kominka wraca wolniej (×0,8).
  Wyniki nauki, XP i Dopaminki — bez zmian.
- **Przeciążenie**: trzecia sesja nauki z rzędu bez przerwy → myśl „Trzeci test pod rząd. Może przerwa?”. Gra nie blokuje.
- **Dom jako baza**: pierwsze wejście danego dnia → „Jest dobrze. Jestem u siebie.”; w domu spokój i energia wracają najszybciej.
- **Jedzenie**: w kawiarni nowa sekcja (kawa + baton, pizza, sałatka z kaszą, zupa dnia, „zjedz z Zenonem”), w domu przy biurku kanapka i herbata (za darmo, żeby bieda nie głodziła postaci). **[do przejrzenia: ceny i wartości]**

## 5. Progresja

- **Dojrzewanie osobiste**: 🌱 Nowa w mieście → 🌿 Mieszkanka → 🌳 Zakorzeniona → 🌾 Mentorka
  (neutralnie: Nowe w mieście → Tutejsza osoba → Zakorzenione → Osoba mentorska **[do przejrzenia]**).
  Liczone z: różnych dni gry, poznanych NPC, odwiedzonych dzielnic, wpisów w dzienniku, wyborów/rozmów. Nie bramki — przy przejściu następny napotkany człowiek mówi ciepło „Wiesz co? Chyba już nie jesteś tu nowa.”
- **Droga diagnosty**: 📋 Stażystka → (płynna specjalizacja z 9 katedr, aktywność wygasa ×0,9 dziennie) → 🔬 Diagnostka → 🎓 Superwizorka.
  Specjalizacje z roadmapy + **🔭 Modelarka procesu** dla Obserwatorium Modeli **[do przejrzenia]**.
  - Stażystka → Diagnostka: **studium przypadku** u Dr Szuster (Obserwatorium Modeli) po zaliczeniu ≥ 40 zagadnień w ≥ 4 katedrach **[do przejrzenia: progi]**:
    winieta + 5 pól (pytanie diagnostyczne, hipotezy, źródła informacji, etyka, informacja zwrotna dla klienta), superwizja jak prawdziwa: mocne strony + do rozważenia; bez kar, można poprawiać.
  - Diagnostka → Superwizorka: po ≥ 100 zaliczonych — **odwrócenie ról**: raport stażysty Kazia z ukrytymi błędami; zaznacz błędy i napisz feedback. Gra sprawdza trafność i ton (ciepło + konkret); Kazio reaguje na ton.
- Istniejąca klasa z kreatora (premia XP) zostaje bez zmian, znika tylko z HUD **[do przejrzenia]**.

## 6. Wybory

- **Dylematy etyczne** (bez jednej dobrej odpowiedzi): akademickie u Przewodniczącego Etyka (nowa opcja „⚖️ Mam dylemat…”), codzienne od ludzi w mieście (rzadko, max 1 na 2 dni).
  Po wyborze: naturalna reakcja NPC + „Napisz dlaczego — dla siebie, nie dla mnie” → dziennik. Gra pamięta, nie ocenia. „Nie chcę teraz o tym myśleć” też jest w porządku.
- **Rozmowy (NVC)**: NPC dzieli się czymś; gracz ma wszystkie style (NVC / ocena / rada / zmiana tematu / ✍️ po swojemu). Efekt pokazuje różnicę (otwarcie vs zamknięcie), bez komentarza „dobrze/źle”; potem pytanie refleksyjne.
- **Eksperymenty od NPC**: zaproszenie („Przez resztę dnia, zanim coś powiesz, nazwij w myślach, co czujesz”), następnego dnia pytanie „Jak poszło?” — „Zapomniałam” → „To normalne. Spróbuj, kiedy będziesz gotowa.”

## 7. Treści dla laika — rozsiane po mieście

Zamknięte dotąd budynki stają się domami-przedmiotami (system `SUBJECTS`, pokój = mini-gra, zapalanie świateł).
Formy: nowe pokoje **„scenka”** (sytuacja → wybór → naturalny skutek + wyjaśnienie; wszystkie wybory dozwolone)
i **„mit czy fakt?”** (bez zegara, z historią mitu), plus istniejące: sortowanie, memory, kolejność.
Kandydaci **[do przejrzenia: przydział]**: Biblioteka (mity psychologiczne), Apteka Placebo (placebo, oczekiwania, ciało–umysł),
Instytut Magnetyzmu (jak rozpoznać szarlatana: Lüscher, Szondi, grafologia, obietnice cudów), Poczta (komunikat „ja”, NVC),
domy na Osiedlu (emocje na co dzień, relacje i konflikt, przywiązanie), Magazyn Pamięci (pamięć życiowo, sen i nauka),
oraz prawa pacjenta i „jak rozpoznać dobrą pomoc”. Bez treści chronionych (co bada konkretny test, skale, klucze, normy).

## Testy

`.profil-work/*.test.js` — wyłącznie pod `http://test.localhost:8765` (zapis autorki na `localhost:8765` nietknięty),
z kopią i przywróceniem localStorage. `node --check` na sklejonym skrypcie przed każdym wstrzyknięciem.

## Plan wdrożenia

1. Rdzeń: `profData`, formy (dukaizmy), dziennik, zaproszenia refleksyjne, rytuały, słowniki → test.
2. Panel profilu (7 zakładek), przycisk P, biurko → test.
3. Samoopieka: potrzeby, myśli, konsekwencje, jedzenie, przeciążenie, dom → test.
4. Progresja: etapy, specjalizacja, podpis HUD, studium przypadku, superwizja → test.
5. Dylematy, rozmowy NVC, eksperymenty → test.
6. Treści laika: nowe rodzaje pokoi + domy w mieście → test.
7. Raport, pamięć, zrzuty.

## Stan wdrożenia (2026-10-01, rano)

Zbudowane wszystkie punkty 1–7. Kod: `.profil-work/src/00-styl.js … 07-laik.js`, wstrzykiwany do gry przez `node .profil-work/build.js`
(blok `<!-- PROFIL:START -->…<!-- PROFIL:END -->` przed „Zapis w chmurze” — nie edytować w HTML, tylko w źródle).
Punktowo w głównym skrypcie: `gf(f, m, n)`, przycisk formy neutralnej w kreatorze, przyciski „📜 Zadania” i „👤 Profil” na dolnej belce.
Testy (tylko pod `http://test.localhost:8765`): `.profil-work/profil.test.js` (89/89), `.profil-work/laik.test.js` (110/110);
stare zestawy bez regresji: halina 39/39, zapis 29/29, tabliczki 22/22 (mapa 45/51 — te same 6 błędów także w kopii sprzed nocy: test klika w kanwę mapy, a przy ukrytym panelu przeglądarki ma ona złe wymiary; to środowisko testowe, nie kod).
Kopia gry sprzed zmian: `akademia_diagnosty_miasteczko.przed_profilem.html`.

Domy dla każdej osoby (zamienione zamknięte budynki): Biblioteka → 📚 Biblioteka Mitów (Rynek), Apteka → 💊 Apteka Placebo (Rynek),
Magnetyzm → 🔮 Instytut Magnetyzmu (Wyparte), Poczta → ✉️ Okienko Praw Pacjenta (Bulwar), dom_a → 💞 Dom Emocji, dom_c → 🪟 Dom Otwartego Okna,
dom_b → 🧸 Dom Bezpiecznej Bazy (Osiedle). 20 pokoi, nowe rodzaje: „🧚 Mit czy fakt?” i „🎭 Scenki”.

**[do przejrzenia]** — przede wszystkim: treści merytoryczne domów laika i studium przypadku; numery pomocowe
(116 123, 800 70 2222, 116 111, 112, Niebieska Linia 800 120 002, Rzecznik Praw Pacjenta 800 190 590); neutralne nazwy etapów
(„Tutejsza osoba”, „Osoba mentorska”, „Osoba na stażu”); nazwy specjalizacji („Rozwojowczyni”, „Systemowczyni”, „Modelarka procesu”);
ceny jedzenia; progi etapów (np. studium przypadku od ~40 zagadnień w 4 katedrach, superwizja od ~100); etykieta „📜 Zadania”.
