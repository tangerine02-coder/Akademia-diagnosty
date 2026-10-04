# 🎯 Akademia Diagnosty — Wizja i Roadmapa

*Dokument żywy. Ostatnia aktualizacja: 2026-10-04.*
*Sesja brainstorm z AI — decyzje autorki gry.*

> **Jak czytać ten dokument:**
> - ✅ = zdecydowane, gotowe do implementacji
> - 🔨 = do zbudowania (decyzja podjęta, kod jeszcze nie)
> - 💭 = do przegadania w sesji brainstorm
> - ⚡ = już istnieje w kodzie

---

## 🗺️ Roadmapa realizacji (zaakceptowana 2026-10-04)

Źródło zadań: tablica POPRAWKI w Notion („Gra Akademia Diagnosty”).
Kolejność: od najmniejszego ryzyka do największych systemów. Każdy etap kończy się
wersją do przetestowania. Szczegóły zrobionych rzeczy odhaczamy w Notion.

### Etap 0 · Porządki
- 🔨 Stare kopie `przed_*.html` i `backup` zostają tylko w historii Gita; w repo jeden plik gry.
- ⚡ Zapis do pliku i wczytanie z pliku już istnieją (💾 Zapis → ⬇️ Pobierz / 📂 Wczytaj). Cały postęp siedzi w jednym kluczu, więc plik zapisu zawiera wszystko.
- 🔨 Przegląd decyzji oznaczonych **[do przejrzenia]** z nocy 1.10 (lista w `docs/DO_PRZEJRZENIA.md`).
- 🔨 Jedno źródło prawdy: wgrać do repo najnowszy plik gry z komputera oraz ukryte foldery `.profil-work/` i `.noc-work/` (źródła modułów i testy). Blok `PROFIL` w HTML jest generowany z `.profil-work/src/` — bez tych źródeł zmiany w nim zrobione w repo nadpisze następny `build.js`.

### Etap 1 · Szybkie wygrane — ⚡ zrobione 2026-10-04
Kod: osobny `<script>` „ETAP 1 · 2026-10-04” (przed blokiem PROFIL). Test: `tests/etap1_test.py`.
- ⚡ Easter eggi: kod Konami, zawrót głowy (3 obroty w miejscu), marzenie na jawie (długi bezruch), gumowa kaczka na kanale Bulwaru, butelka z listem od przyszłego „ja” na Plaży, Fontanna Barnuma na Rynku.
- ⚡ Błonia: Deska Galtona, Budka „Lody i oparzenia” (korelacja ≠ przyczyna), Ławka Średniej Płacy (średnia vs mediana), Automat z Monetą (złudzenie gracza), Pomnik Regresji do Średniej; +15 XP za wszystkie.
- ⚡ Domy z zewnątrz: dachówka-łuska, łupek, strzecha, mech, szachulec, bluszcz, podmurówka, okiennice, lukarny, daszki, latarenki, donice.
- ⚡ Wnętrza domów-przedmiotów: 27 motywów (podłoga, ściana, okno, hol, meble, obrazy, dywany) i różny układ (drzwi pokoi, stanowiska, kolumny, ławki, rośliny).
- ⚡ Muzyka: pogłos, akordy w tle, delikatna perkusja, druga linia melodii, nokturn nocą, własny motyw wnętrz na każdej wyspie.

### Etap 2 · Systemy świata — ⚡ zrobione 2026-10-04
Kod: osobny `<script>` „ETAP 2 · 2026-10-04” (przed blokiem PROFIL). Test: `tests/etap2_test.py`. Panel testerki (F9, a na telefonie 💾 Zapis → 🧪 Otwórz) ma przełącznik pór roku.
- ⚡ 4 pory roku wg daty gry: 28 dni na porę, rok = 112 dni, dzień 1 = jesień. Zmienia się teren (paleta, śnieg, opadłe liście, stokrotki, zimą bez kwiatów), drzewa i krzewy, śnieg na dachach, cząsteczki (liście, płatki, płatki śniegu). Ikona pory przy dacie w HUD, komunikat i jedno zdanie o świetle dnia, gdy pora się zmienia.
- ⚡ Silnik „znajdź”: zadania poboczne od mieszkańców — ✉️ Listonosz (4 listy w 4 dzielnicach), 🎣 Rybak (3 spławiki przy wodzie), 🙈 Mała Ida (chowany, codziennie), 🦋 Morfeusza (3 senne motyle, nagroda w LP). Każde kończy się ciekawostką z psychologii. Pasek postępu w rogu ekranu.
- ⚡ Trening snu „co się zmieniło względem jawy”: 2–5 zmian (napis, kolor budynku lub przedmiotu, wygląd mieszkańca, przedmiot, którego na jawie nie ma). Mgła i poprzestawiane drzewa na niskim poziomie (nie liczą się). Limit czasu od 1:30, rośnie z treningiem do 5:30; +20 s i +5 LP za trafienie; komplet = dzień treningowy. Po czasie postać się budzi. We śnie są teraz mieszkańcy dzielnicy.

### Etap 3 · Nowe miejsca
- 🔨 Ogród Uważności (mindfulness i medytacja).
- 🔨 Dom Żyrafy w mieście (✅ NVC) — dom dla istniejących rozmów w stylach.
- 🔨 Dom Muzyki — poznawcza nauka muzyki; fundator pianina na Bulwarze Empatii.
- 🔨 Dzielnica Pamięci (✅ nowa dzielnica na mapie; pamięć długotrwała przenosi się z Portu).
- 🔨 Archiwum Szarlatanerii 2.0 — dla laika przegląd zdyskredytowanych testów i technik, nie testowanie.
- 💭 Katedra Teologii i Płci — treść do ustalenia z autorką.

### Etap 4 · Długa gra
- 🔨 Ogródek i poletko; sprzedaż warzyw daje Dopaminki.
- 🔨 Powiększanie domku: trudna misja odblokowuje nowe pomieszczenie (rzadko), balans razem z zarobkami z poletka.
- 🔨 Osobowość z wyborów: zakładka 🧠 Osobowość już istnieje — domykamy brakujące źródła danych.

### Etap 5 · Wersja akademicka
- 🔨 Podział na BAZĘ i ROZSZERZENIE; testy tylko w wersji dla studentów. Warunek przed publikacją gry.
- 🔨 Promotor (magisterka, praca roczna) i mentor postaci.
- 🔨 Mini gry i kompendium wiedzy w każdym budynku.

### Później
- 💭 Rodzina postaci.

### Otwarte pytania
- 💭 Mentor i promotor: jedna postać czy dwie?
- 💭 Katedra Teologii i Płci: co ma w niej być?

---

## ✅ Architektura: BAZA + ROZSZERZENIE

### 📁 Wersja publiczna (BAZA) — kompletna gra
- **Dla kogo:** Każdy — laicy, osoby ciekawe psychologii
- **Treść:** Pełna, samodzielna gra z własnym łukiem — autorefleksja, emocje, relacje, mity psychologiczne, prawa pacjenta, rozpoznawanie szarlatanerii
- **Dystrybucja:** Otwarta, do pobrania
- **Wymóg:** Musi być PEŁNYM doświadczeniem, nie demo ani okrojoną wersją
- **Status:** 💭 treści do zaprojektowania

### 📁 Wersja akademicka (BAZA + MODUŁY STUDENCKIE)
- **Dla kogo:** Studenci psychologii (po min. roku studiów)
- **Treść:** Wszystko co w bazie PLUS: wiedza o testach, modele procesu, psychometria, ścieżka akademicka (stażysta → diagnosta)
- **Dystrybucja:** Zamknięty obieg z weryfikacją (uczelnia, promotor, kod dostępu)
- **Status:** ⚡ pytania i silnik prawie gotowe (~80+ pytań akademickich)
- **Fabularnie:** Student = mieszkaniec Freudowic, który zapisał się do Akademii

### Dlaczego dwa pliki, a nie wybór w grze?
- Gra to HTML — każdy może otworzyć źródło
- Nie da się zweryfikować gracza w kliencie
- Wiedza o testach (co badają, jak działają skale) jest **chroniona zawodowo** — ujawnienie niszczy moc psychometryczną
- „Zamknięte drzwi" w grze to tylko scenografia, nie ochrona

### Dlaczego baza + rozszerzenie, a nie dwa osobne światy?
- Student też jest człowiekiem — treści o autorefleksji czynią go lepszym diagnostą
- Spójność — jedna wizja, jeden świat, dwa poziomy wtajemniczenia
- Technicznie czystsze — jeden build bazowy + drugi z dodatkowym blokiem
- Fabularnie eleganckie — laik = mieszkaniec, student = mieszkaniec + student Akademii

---

## ✅ Zasady treściowe

### Laik NIE powinien wiedzieć:
- Co bada konkretny test (MMPI-2, WCST, Raven, TRE, INTE...)
- Jak działają skale kontrolne
- Szczegóły modeli procesu diagnostycznego
- Psychometria (czułość, swoistość, alfa Cronbacha)

### Laik POWINIEN wiedzieć:
- Czym jest dobra pomoc psychologiczna (i jak rozpoznać złą)
- Swoje prawa jako pacjent
- Że test Lüschera/Szondiego/grafologia to bzdura
- Że intuicja zawodzi (zasady myślenia, nie nazwiska)
- Jak działają emocje, pamięć, sen (życiowo)
- Że diagnoza ≠ etykieta

---

## ✅ Tożsamość gry

- Autorka: przyszła psycholog, kończąca studia
- Gra ma **podmiotowo traktować gracza** (modeluje to, czego uczy)
- **Trochę terapeutyczna** — autorefleksja, bezpieczne przestrzenie, ciepło
- Postać gracza kształtowana przez wybory i osiągnięcia
- **Gra NIGDY nie mówi graczowi, kim jest. Mówi, co zaobserwowała.**

### ✅ FUNDAMENTALNE ZASADY PROJEKTOWE

**0. WOLNOŚĆ — w każdym aspekcie.**
Nadrzędna zasada. Gracz jest wolny: w wyborze tożsamości (zmienialnej
w każdej chwili), specjalizacji, stylu rozmowy, jedzenia, tempa, drogi.
Wolny, żeby pominąć, zignorować, wrócić później. Wolny, żeby nie
odpowiedzieć. Wolny, żeby odejść. Żadnych wymuszonych tutoriali,
obowiązkowych ścieżek, karania za „złe" wybory. Gra daje przestrzeń —
gracz ją wypełnia po swojemu.

**1. Gra nie zabrania, nie zmusza, nie moralizuje.**
Gra prezentuje opcje. Pokazuje naturalne konsekwencje. Zadaje pytania.
Zaprasza do refleksji. Ale NIGDY nie robi za gracza, nie blokuje
„złych" wyborów i nie karze. Jak dobry terapeuta — rogersowska zasada.

**2. Gra jest prawdziwa.**
Świat gry odzwierciedla rzeczywistość taką, jaka jest — nie taką, jaką
chcemy ją widzieć. Bez toksycznego optymizmu, bez przesadnego negatywizmu.
Ludzie (NPC) są różni: ciepli i zimni, mądrzy i błądzący, spójni i
niespójni. Jak w życiu.

**3. Gra jest zabawna.**
Prawdziwość nie oznacza ponurości. Gra ma dawać śmiech i DUŻO zabawy.
Humor wynika z prawdy, nie z lukrowania (Freudowice Zdrój! Dopaminki!
Archiwum Szarlatanerii!). Lekki ton, poważna treść.

### ✅ Język i zachowania — promowanie bez narzucania

**NVC (język żyraf):**
- Część NPC mówi NVC, część nie, część miesza — jak w życiu
- Gra NIE mówi „NVC jest dobre, reszta zła"
- Gra POKAZUJE różnicę w efektach: NVC → otwarcie, oceny → zamknięcie
- Gracz ma dostęp do WSZYSTKICH stylów w dialogach (też tych „złych")
- Po interakcji: pytanie refleksyjne → dziennik → nauka

**Zdrowe odżywianie, sen, ruch, relacje:**
- Wszystkie opcje dostępne zawsze (kawa+baton, pizza, sałatka, nic)
- Postać żyje naturalne konsekwencje (nie kary/nagrody)
- Gracz widzi wzory sam po kilku dniach gry
- Gra nie mówi „jedz zdrowo" — postać po prostu lepiej/gorzej funkcjonuje

**Zadania od NPC:**
- NPC dają zaproszenia i eksperymenty, nie wykłady
- Przykład: „Przez resztę dnia, zanim coś powiesz, nazwij w myślach co czujesz"
- Gracz może zrobić albo nie — obie opcje są OK
- „Zapomniałam" → NPC: „To normalne. Spróbuj kiedy będziesz gotowa."

---

## 🔨 Profil postaci — odkrywa się jak prawdziwe poznawanie siebie

### Zasada: profil zaczyna pusty i wypełnia się w trakcie gry

Dzień 1 — prawie pusta karta ("jeszcze nie wiem" / "???")
Dzień 30 — żywy portret, wyłoniony z wyborów, zachowań i refleksji gracza

### Panel profilu — dostępny z dolnego paska

Układ: popiersie postaci w centrum + zakładki:

### Zakładka 👤 Ja — tożsamość (edytowalna w dowolnym momencie!)
- Imię, wiek
- Płeć / zaimki (dowolne, w tym niebinarne)
- Orientacja seksualna (opcjonalne — można zostawić puste)
- Pochodzenie / kultura (tekst wolny lub wybór)
- Rodzina (opcjonalne, może wpływać na dialogi)
- Wartości (wybór z listy lub wolny tekst)
- Wierzenia / duchowość (opcjonalne — sfera noetyczna!)
- Neurodywergencja (opcjonalne, bez oceniania)
- Mocne strony (gracz sam wpisuje)
- To, z czym się zmagam (samo-refleksja, nie diagnoza)

**Zasada: gra NIGDY nie ocenia tych wyborów. Nie ma „lepszej" orientacji, „poprawnej" rodziny.**

### Zakładka 🧠 Osobowość — wyłania się z gry (gracz NIE ustawia)

| Wymiar | Skąd się bierze |
|---|---|
| Styl poznawczy (analityczny ↔ intuicyjny) | Jak odpowiada na pytania |
| Styl relacyjny (ciepły ↔ rzeczowy) | Jak rozmawia z NPC-ami |
| Styl radzenia sobie (zadaniowy / emocjonalny / unikowy) | Jak reaguje na porażki |
| Otwartość na doświadczenie | Ile dzielnic odwiedza, czy eksploruje |
| Wytrwałość | Czy wraca do trudnych pytań |
| Ciekawość | Ile razy czyta wyjaśnienia / klika „dlaczego?" |
| Odwaga | Czy podejmuje trudne dylematy etyczne |

Gra nie etykietuje. Zamiast "jesteś introwertykiem" mówi:
*"Spędzasz więcej czasu sam w domu niż na rynku. Może lubisz ciszę?"*

### Zakładka 📊 Profil diagnosty (TYLKO wersja akademicka)
- Radar kompetencji (EBA, Wywiad, Psychometria, Etyka, Neuro, Dziecko, Rodzina, Modele)
- Styl diagnostyczny: generowany label (np. „Empatyczna empirystka")
- Podejście: bardziej aktuarialne czy kliniczne?
- Najsilniejszy i najsłabszy obszar
- Historia superwizji (feedback od NPC-superwizora)
- Powiązany z osiągnięciami i podejściami do budynków/testów

### Zakładka 📖 Dziennik — żywy dokument
- Myśli postaci po ważnych momentach
- Odpowiedzi gracza na pytania refleksyjne (wolne pole)
- Sny z Katedry Snu
- Cytaty z NPC-ów, które „zapamiętałeś"
- Historia wyborów etycznych z uzasadnieniami gracza

### Zakładka 🏆 Osiągnięcia
- Odznaki z poszczególnych dzielnic/budynków

---

## 🔨 System wyborów — pięć rodzajów

### 🪞 Wybory tożsamości — „kim jestem"
Kreator postaci, ale NIE jednorazowy. Gracz ustawia na starcie, ale może zmieniać
w trakcie gry — bo ludzie się zmieniają.

### 📚 Wybory uwagi — „czego się uczę"
Gra śledzi, gdzie gracz spędza czas. Płynna specjalizacja, nie klasa postaci.
Można się zanurzyć w jednym obszarze, ale też zmienić w dowolnym momencie.

### ⚖️ Wybory etyczne — „jak myślę"
NPC-e stawiają przed dylematami bez jednej poprawnej odpowiedzi.
Przykład: „Pani Kowalska prosi, żebyś nie wpisywała do opinii, że syn moczy
łóżko. Boi się, że ojciec użyje tego w sądzie. Co robisz?"
Gra zapamiętuje, nie ocenia.

### 💬 Wybory relacyjne — „jak się odnoszę do ludzi"
Jak gracz rozmawia z NPC-ami? Ciepło czy rzeczowo? Pyta o emocje czy fakty?
Opcje dialogowe + wolne pole tekstowe (gracz może napisać własną odpowiedź).

### 🌙 Wybory refleksyjne — „co czuję"
Pytania otwarte z wolnym polem tekstowym. Odpowiedzi trafiają do dziennika
i pomagają kształtować profil osobowości.

---

## 🔨 Pytania refleksyjne — mechanika odkrywania siebie

Gra zadaje pytania, na które gracz PISZE RĘCZNIE. Nie quiz. Wolny tekst.
Odpowiedzi trafiają do dziennika i pomagają kształtować profil.

### Kiedy się pojawiają:

| Moment | Przykład pytania |
|---|---|
| Po rozmowie z NPC | „Halina powiedziała, że ludzie boją się tego, czego nie rozumieją. Zgadzasz się? Dlaczego?" |
| Po porażce w quizie | „Nie poszło Ci dobrze. Co teraz czujesz — złość, ciekawość, zniechęcenie?" |
| Po sukcesie | „Poszło świetnie. Co Ci pomogło?" |
| Wieczór w domu | „Kończy się dzień. Co Cię dziś zaskoczyło?" |
| Po dylematie etycznym | „Wybrałaś X. Napisz dlaczego — dla siebie, nie dla mnie." |
| Po śnie | „Co myślisz o tym śnie? Co Ci przypomina?" |
| Losowo, rzadko | „Gdybyś mogła zmienić jedną rzecz w swoim życiu, to co?" |

### Co się dzieje z odpowiedzią:
1. Zapis do dziennika (zawsze)
2. Analiza słów kluczowych (prosty parser jak istniejący verifyAnswer)
3. Aktualizacja profilu osobowości (subtelna, narastająca)

---

## 🔨 Samoopieka przez opiekę nad postacią

### Filozofia: gracz uczy się dbać o siebie, ćwicząc dbanie o postać
Mechanizmy: projekcja, przeniesienie, nauka nie-wprost.
Jak terapia zabawą, ale medium to gra.

### Potrzeby postaci — lustro prawdziwego człowieka:

| Potrzeba | Jak gracz o nią dba | Czego się uczy (nie wprost) |
|---|---|---|
| 🔋 Energia | Sen, odpoczynek, kawa | Zarządzanie zasobami, sen ma wartość |
| 💛 Nastrój | Rozmowy z NPC, ładne miejsca, sukcesy | Emocje reagują na otoczenie i relacje |
| 🫂 Więzi | Odwiedzanie ludzi, pomaganie NPC-om | Izolacja kosztuje, kontakt daje siłę |
| 🧘 Spokój | Dom, cisza, dziennik, sen | Potrzeba przestrzeni od bodźców |
| 🎯 Sens | Nauka, osiągnięcia, postęp | Cel daje energię, bezczynność zabiera |
| 🍽️ Ciało | Jedzenie, spacer, ruch | Podstawowe potrzeby fizyczne wpływają na psychikę |

### Subtelne sygnały, NIE stresujące paski:
Gra nie karze za zaniedbanie. Pokazuje konsekwencje łagodnie:
- Dawno nie rozmawiała → 💭 „Cisza jest przyjemna... ale chyba trochę za długo."
- Nie spała → porusza się wolniej, więcej błędów w quizach
- Tylko się uczy → 💭 „Głowa pęka. Może spacer nad morze?"
- Zjadła z NPC → krótki moment ciepła, bonus do nastroju
- Napisała w dzienniku → micro-animacja oddychania (ulga)

### Rytuały wbudowane w rozgrywkę:

**🛏️ Wieczorny rytuał (przed snem):**
- „Jak minął Ci ten dzień?" (wolne pole → dziennik)
- Wybór: dziennik / herbata / zadzwonić do NPC / po prostu spać

**🌅 Poranny check-in:**
- „Jak się dziś czujesz?" → Dobrze / Średnio / Ciężko
- Wybór wpływa na tempo dnia, ale żaden nie jest „zły"

**⚡ Sygnały przeciążenia:**
- Gra NIE blokuje. Sugeruje. 💭 „Trzeci test pod rząd. Może przerwa?"

**🏠 Dom jako bezpieczna baza:**
- Tu nikt nie zadaje pytań, tu gracz odpoczywa najszybciej
- 💭 „Jest dobrze. Jestem u siebie."
- Uczy: wycofanie się to nie porażka, to zasób

### Ukryte spięcie z fundamentami gry:
NPC mówi: „Nie możesz dobrze diagnozować kogoś innego, jeśli nie znasz
i nie dbasz o siebie. Narzędzie diagnosty to nie test. To on sam."
→ System samoopieki = ukryty wykład o architektonicznym modelu kompetencji.

---

## 🔨 Ścieżki progresji

### 🌿 Warstwa bazowa (każdy gracz): Dojrzewanie osobiste
Nie tytuły, nie levele. Głębokość obecności w świecie:

🌱 Nowa/y w mieście → 🌿 Mieszkaniec/ka → 🌳 Zakorzeniona/y → 🌾 Mentor/ka

Przejścia NIE są bramkami. Gra obserwuje (ile NPC zna, ile refleksji napisał,
ile dzielnic odwiedził) i w pewnym momencie NPC mówi ciepło:
„Wiesz co? Chyba już nie jesteś tu nowa."

### 🎓 Warstwa akademicka: Droga diagnosty
📋 Stażysta/ka → specjalizacja wyłania się z zachowań (płynna!) → 🔬 Diagnosta/ka → 🎓 Superwizor/ka

| Gdzie spędzasz czas | Kim się stajesz |
|---|---|
| Gabinet Wywiadu | 💬 Klinicystka |
| Poligon Psychometryczny | 📊 Psychometryczka |
| Pawilon Neuro | 🧠 Neuropsycholożka |
| Pracownia Dziecka | 🧒 Rozwojowiec |
| Klinika Rodziny | 👨‍👩‍👧 Systemowiec |
| Komisja Etyki | ⚖️ Strażniczka etyki |
| Archiwum Błędów | 🔍 Demaskatorka |
| Instytut EBA | 🏛️ Metodolożka |

Specjalizacja NIE jest trwała! Zmienisz fokus → profil się przebarwia.

**Stażysta → Diagnosta:** Przez integrację — studium przypadku (wolne pole,
konceptualizacja, feedback od NPC-superwizora jak prawdziwa superwizja).

**Superwizor (endgame):** Odwrócenie ról — gracz sprawdza pracę NPC-stażysty
i daje feedback. Gra sprawdza czy potrafi: znaleźć błędy merytoryczne,
ale też dać feedback ciepło i konstruktywnie.

---

## 💭 Hobby i kreatywność

Hobby to nie quest. To przestrzeń bez punktów, bez „poprawnie". Robisz, bo chcesz.
Gra uczy: hobby to samoopieka i profilaktyka wypalenia.

Pomysły do rozważenia:
- 🎨 Edytor pixel artu (prace wieszasz w domu, dajesz NPC)
- 🌱 Ogródek (sadzisz, podlewasz, czekasz — metafora rozwoju)
- 🍳 Kuchnia (łączenie składników, jedzenie z NPC buduje relację)
- 📝 Pisanie (listy do NPC, wiersze, opowiadania — wolne pole)
- 🎵 Muzyka (prosty sekwencer, słuchanie w miejscach w grze)
- 📸 Momenty (screenshot + podpis gracza → album)
- 🧶 Kolekcjonowanie (muszle, kamienie, książki → półka w domu)

---

## 💭 Otwarte tematy do dalszych burz mózgów
- [ ] System zapisu postępu
- [ ] Treści dla wersji bazowej (publicznej) — jakie pytania, mini-gry
- [ ] Weryfikacja w wersji akademickiej — jak technicznie
- [ ] Arc fabularny — początek, środek, koniec? Czy sandbox?
- [ ] NPC-e — kto mieszka w Freudowicach, jakie mają osobowości
- [ ] System reputacji / relacji z NPC-ami
- [ ] Jak wyglądają treści dla laika — konkretne przykłady pytań/mini-gier
- [ ] Hobby — które mechaniki budujemy, priorytet

---

## ⚡ Co już istnieje w kodzie
- Świat: 9+ dzielnic z własną muzyką, pixel art, cykl dnia/nocy
- HUD: portret, ranga, zegar, dopaminki, energia, XP, streak
- System dialogowy (portret + tekst + opcje)
- Kreator postaci
- 80+ pytań akademickich z parserem odpowiedzi (NLP, Levenshtein)
- Mini-gry (memory, sortowanie, sekwencjonowanie, prawda/fałsz)
- Katedra Snu (świadome śnienie)
- Dom Pani Haliny (shaky text)
- Mapa miasta (kolorowe kratki, mgła, latarnia)
- System dekoracji domu
- Silnik dźwiękowy (Web Audio API, melodie per dzielnica)
- Sterowanie dotykowe (mobile)
- Odznaki, dziennik zadań
- Superwizor AI (z fallbackiem na parser lokalny)
- Przycisk 💾 Zapis (do rozbudowania)
- **(2026-10-01, noc)** 👤 Profil [P]: zakładki Ja / Osobowość / Jak się mam / Dziennik / Droga / Osiągnięcia / Profil diagnosty
- **(2026-10-01)** Dziennik + pytania refleksyjne (karteczki „💭”), wieczorny rytuał, poranny check-in, 📌 zapamiętywanie słów NPC
- **(2026-10-01)** Samoopieka: 6 potrzeb bez pasków, myśli, łagodne konsekwencje, jedzenie (kawiarnia, kanapka i herbata w domu)
- **(2026-10-01)** Progresja: 🌱→🌾 dojrzewanie, 📋 Stażystka → płynna specjalizacja → 🔬 Diagnostka (studium przypadku) → 🎓 Superwizorka (raport Kazia)
- **(2026-10-01)** Wybory: 10 dylematów, 6 rozmów w stylach (NVC/ocena/rada/zmiana tematu/po swojemu), 6 eksperymentów od mieszkańców
- **(2026-10-01)** Treści dla każdej osoby: 7 domów w mieście (mity, placebo, szarlataneria, prawa pacjenta, emocje, relacje, przywiązanie) — szkic do przejrzenia
- **(2026-10-01)** Trzecia forma gramatyczna: neutralna (dukaizmy)
  → szczegóły: `docs/superpowers/specs/2026-10-01-profil-dziennik-samoopieka-design.md`
