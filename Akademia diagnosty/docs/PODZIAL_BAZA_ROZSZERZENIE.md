# Podział treści: BAZA i ROZSZERZENIE — propozycja do decyzji

*Szkic AI z 2026-10-05.* **✅ Przyjęte bez zmian 2026-10-05 i zbudowane (Etap 6).**

> **Jak to działa teraz:** kategorie są w kodzie gry (mapa `TIERS` w bloku „ETAP 6 · WERSJE”). Wersję publiczną buduje `python3 narzedzia/zbuduj_publiczna.py`.
> Zmiana kategorii zagadnienia = zmiana jednej litery w `TIERS` i ponowne zbudowanie. Do 32 zagadnień 🌍 z tabel doszło 21 nowych (każda katedra ma co najmniej 5) i 14 z Katedry Psychologii Religii i Płci — razem 67.
> W wersji publicznej zajęcia z pytaniami otwartymi zastępuje ✅ Sprawdzian (pytania zamknięte). Szczegóły i otwarte sprawy: `DO_PRZEJRZENIA.md`, punkty 66–74.

## Czego dotyczy
Podział dotyczy **pytań katedr** (176 zagadnień w `QUESTIONS_DB`). Korzystają z nich: zajęcia (pytania otwarte), szybki quiz u mistrza, kompendium i mini gry katedr, egzamin u Brygadzisty, Automat Powtórek oraz tabliczki i nagrobki ze wskazówkami.

Resztę gry (miasto, domy-przedmioty, Archipelag, Etapy 1–4, profil) trzeba przejrzeć osobno. Na pierwszy rzut oka to BAZA.

## Trzy kategorie
- 🌍 **B — dla każdego**: prawa pacjenta, sceptycyzm wobec pseudonauki, komunikacja, rozumienie wyników badań. Zostaje w BAZIE (kompendium, mini gry), w razie potrzeby prostszymi słowami.
- 🎓 **A — akademickie, bez tajemnicy zawodowej**: modele procesu diagnostycznego, metodologia, technika wywiadu. Trafia do ROZSZERZENIA.
- 🔒 **R — konkretne narzędzia**: budowa, skale, normy, procedura i interpretacja testów. Tylko w ROZSZERZENIU. To wiedza chroniona zawodowo — jej ujawnienie może osłabić moc diagnostyczną testu.

**Razem: 🌍 32 · 🎓 96 · 🔒 48** (na 176 zagadnień).

## Co to oznacza dla gry (propozycja)
1. **Jeden plik źródłowy, dwa pliki do grania.** Pierwszy to `akademia_diagnosty_miasteczko.html` — wersja akademicka, taka jak teraz. Drugi to `akademia_diagnosty_publiczna.html`, czyli BAZA. Robi go skrypt, który usuwa zagadnienia 🎓 i 🔒 oraz moduły tylko dla studentów.
2. **Katedry w BAZIE** zostają jako budynki. Kompendium, mini gry, szybki quiz i egzamin u Brygadzisty biorą wtedy tylko zagadnienia 🌍. Zajęcia z pytaniami otwartymi są zamknięte i oznaczone „dla studentów Akademii”.
3. **Katedry z małą liczbą 🌍** to Modele (0), Testy (0), Dziecko (1), Rodzina (2) i Neuro (3). W BAZIE potrzebują nowej treści dla laika, na przykład:
   - Poligon Psychometryczny: „Jak rozpoznać dobry test — i quiz z gazety”,
   - Obserwatorium: „Jak psycholog dochodzi do wniosków”.

   W roadmapie te treści mają status 💭 „do zaprojektowania”.
4. **Wersja akademicka** zostaje bez zmian.

## Pytania do Ciebie
1. Czy podział na trzy kategorie ma sens? Popraw w tabelach poniżej (🌍 / 🎓 / 🔒).
2. Czy zagadnienia 🎓 mogą być w BAZIE przynajmniej w kompendium (bez zajęć)?
3. Jak udostępniać wersję akademicką? W roadmapie jest „zamknięty obieg z weryfikacją”: kod dostępu od uczelni albo promotora, osobny link?

## Tabele (propozycja AI, do poprawienia)

### ⚖️ Ratusz — Komisja Etyki — 🌍 10 · 🎓 9 · 🔒 0

| Zagadnienie | Propozycja |
|---|---|
| Cztery Filary Metakodeksu Etycznego (EFPPA / PTP) | 🎓 A |
| Świadoma Zgoda na Badanie (13 Standardów) | 🌍 B |
| Model Decyzyjny Gottlieba (Relacje Podwójne) | 🎓 A |
| Zasady Opinii dla Odbiorcy Nieprofesjonalnego | 🎓 A |
| Zasada poszanowania praw i godności | 🌍 B |
| Zasady odpowiedzialności i kompetencji | 🎓 A |
| Prawo do wycofania zgody | 🌍 B |
| Ograniczenia poufności | 🌍 B |
| Zasada minimalizacji zbieranych danych | 🌍 B |
| Relacje podwójne i wykorzystujące | 🌍 B |
| Uczucia nieprofesjonalne diagnosty | 🎓 A |
| Udział trzeciej strony | 🌍 B |
| Zakaz opiniowania osób niebadanych | 🌍 B |
| Ograniczenia wniosków diagnostycznych | 🎓 A |
| Wykorzystanie przypadków w dydaktyce | 🌍 B |
| Granice przestrzenne, czasowe i cielesne | 🌍 B |
| Czego nie robić w informacji zwrotnej | 🎓 A |
| Rodzaje raportu psychologicznego | 🎓 A |
| Opinia dla odbiorcy nieprofesjonalnego | 🎓 A |

### 🕯️ Archiwum Szarlatanerii — 🌍 8 · 🎓 11 · 🔒 0

| Zagadnienie | Propozycja |
|---|---|
| Narzędzia Zdyskredytowane (Sondaż Norcrossa) | 🌍 B |
| Efekt Rumpelstilzchena | 🌍 B |
| Zjawisko Reifikacji Pacjenta | 🎓 A |
| Błąd Koniunkcji (Conjunction Fallacy) | 🌍 B |
| Efekt Barnuma / Forera (Meehl) | 🌍 B |
| Katalog narzędzi zdyskredytowanych | 🌍 B |
| Zdyskredytowane zastosowania, nie narzędzia | 🌍 B |
| Trzy podejścia do interpretacji rysunku | 🎓 A |
| Krytyka technik projekcyjnych | 🌍 B |
| Test Rorschacha — status i zarzuty | 🌍 B |
| Błąd przedwczesnej konkluzji | 🎓 A |
| Pośpiech i mechanicyzm a stagnacja | 🎓 A |
| Kierowanie się autodiagnozą klienta | 🎓 A |
| Brak czujności diagnostycznej | 🎓 A |
| Notatki jako źródło błędu | 🎓 A |
| Model biomedyczny jako źródło błędu | 🎓 A |
| Rekomendacje dla profesjonalnego diagnosty | 🎓 A |
| Intuicja diagnosty w paradygmacie EBA | 🎓 A |
| Ekstremalność myślenia o pacjencie | 🎓 A |

### 🏛️ Instytut Metodologii & EBA — 🌍 4 · 🎓 16 · 🔒 0

| Zagadnienie | Propozycja |
|---|---|
| 3 Filary EBA (APA 2005/2006) | 🎓 A |
| Kryteria Dauberta w Sądzie | 🎓 A |
| Twierdzenie Bayesa: Czułość a Swoistość | 🌍 B |
| Proporcja Podstawowa (Base Rate) a Ryzyko Samobójstwa | 🎓 A |
| Diagnoza Aktuarialna a Kliniczna (Meehl 1954) | 🎓 A |
| Przypadek Złamanej Nogi Meehla | 🎓 A |
| Diagnoza a testowanie psychologiczne | 🌍 B |
| Rygor naukowy postępowania diagnostycznego | 🎓 A |
| Diagnoza a ocena | 🎓 A |
| Trzy desygnaty terminu diagnoza psychologiczna | 🎓 A |
| Podejście idiotetyczne | 🎓 A |
| Podejście mieszane (ilościowo-jakościowe) | 🎓 A |
| Standaryzacja i obiektywność | 🎓 A |
| Trafność a rzetelność | 🌍 B |
| Normalizacja testu | 🎓 A |
| Adaptacja narzędzia do warunków krajowych | 🎓 A |
| Kompetencja diagnostyczna — definicja | 🎓 A |
| Architektoniczny model kompetencji diagnosty | 🎓 A |
| Holistyczny model człowieka — cztery sfery | 🌍 B |
| Diagnoza jako interwencja | 🎓 A |

### 💬 Gabinet Wywiadu i Obserwacji — 🌍 4 · 🎓 20 · 🔒 0

| Zagadnienie | Propozycja |
|---|---|
| Kontakt Pozorny (Geller i Król) | 🎓 A |
| Technika Przyczółka przy Oporze | 🎓 A |
| Parafraza a Interpretacja | 🌍 B |
| Wywiad Poznawczy (Fisher & Geiselman) | 🎓 A |
| Konstrukcja Lejkowa a Odwróconego Lejka | 🎓 A |
| Model Kontaktu Tickle-Degnen i Rosenthala | 🎓 A |
| Przymierze w Działaniu (Bordin / Horvath WAI) | 🎓 A |
| Recypatia i Błąd Minimalizacji Kontekstu | 🎓 A |
| Pytania otwarte a zamknięte | 🌍 B |
| Pytania projekcyjne w wywiadzie | 🎓 A |
| Pytania uwikłane (normalizujące) | 🎓 A |
| Czym pytania w wywiadzie być NIE powinny | 🌍 B |
| Wypowiedzi osobiste a bezosobowe | 🌍 B |
| Kontakt pozorny i przejawy oporu | 🎓 A |
| Źródła oporu badanego | 🎓 A |
| Sposoby przełamywania oporu | 🎓 A |
| Klaryfikacja a konfrontacja | 🎓 A |
| Nieświadoma akomodacja | 🎓 A |
| Behawioralne potwierdzenie w badaniu | 🎓 A |
| Kolejność tematów i notatki w wywiadzie | 🎓 A |
| Podziały obserwacji psychologicznej | 🎓 A |
| Trafność ekologiczna a teoretyczna w obserwacji | 🎓 A |
| Podejście analityczne a doświadczeniowe | 🎓 A |
| Wywiad jako społeczne konstruowanie znaczeń | 🎓 A |

### 🔭 Obserwatorium Modeli Procesu — 🌍 0 · 🎓 20 · 🔒 0

| Zagadnienie | Propozycja |
|---|---|
| Procedura 5 Kroków Teresy Szustrowej | 🎓 A |
| Model Maloneya i Warda (Faza 5 i 6) | 🎓 A |
| Model Paluchowskiego (Etap 1 i 4) | 🎓 A |
| Model GAP (Guidelines for Assessment Process) | 🎓 A |
| Trzy Piętra Osobowości McAdamsa | 🎓 A |
| Zasada wielokrotności w procedurze Szustrowej | 🎓 A |
| Krok 1 i 2 procedury pięciu kroków | 🎓 A |
| Krok 4 i 5 procedury pięciu kroków | 🎓 A |
| Modele użyteczności decyzji (Cronbach i Gleser) | 🎓 A |
| Model regresyjny (matematyczny) Meehla | 🎓 A |
| Model aktuarialny | 🎓 A |
| Modele formalne a modele procesu | 🎓 A |
| Zarzucanie sieci u Maloneya i Warda | 🎓 A |
| Końcowe etapy modelu Maloneya i Warda | 🎓 A |
| Etap prediagnostyczny u Paluchowskiego | 🎓 A |
| Iteracyjność modelu Paluchowskiego | 🎓 A |
| Follow-up w modelu GAP | 🎓 A |
| Trzy główne rodzaje diagnozy psychologicznej | 🎓 A |
| Protodiagnoza | 🎓 A |
| Siatka pytań o diagnozę psychologiczną | 🎓 A |

### 🎯 Poligon Psychometryczny — 🌍 0 · 🎓 6 · 🔒 19

| Zagadnienie | Propozycja |
|---|---|
| MMPI-2: Strategia Konstrukcji | 🔒 R |
| Test Matryc Ravena (TMS) | 🔒 R |
| TRE a INTE: Inteligencja Emocjonalna | 🔒 R |
| Skala Wartości Rokeacha (RVS) | 🔒 R |
| Inwentarz FCZ-KT(R) Jana Strelaua | 🔒 R |
| Test Zdań Niedokończonych Rottera (RISB) | 🔒 R |
| Metodologia Q-Sort (Stephenson) | 🔒 R |
| Skala a inwentarz (homogeniczność) | 🎓 A |
| Kwestionariusz a test zadaniowy | 🎓 A |
| MMPI-2 — skala konstrukcji | 🔒 R |
| NEO-FFI a NEO-PI-R | 🔒 R |
| EPQ-R i Gigantyczna Trójka | 🔒 R |
| Lista Przymiotników ACL | 🔒 R |
| STAI — stan a cecha lęku | 🔒 R |
| Podskale stylu unikowego w CISS | 🔒 R |
| SES a MSEI | 🔒 R |
| LOT-R, SWLS i GSES | 🔒 R |
| WKP — Wielowymiarowy Kwestionariusz Preferencji | 🔒 R |
| TRE a INTE — wykonawczy kontra samoopisowy | 🔒 R |
| Formy pozycji testowych i sposoby odpowiadania | 🎓 A |
| Kiedy stosować techniki projekcyjne | 🎓 A |
| Stopnie strukturalizacji technik projekcyjnych | 🎓 A |
| Pięć rodzajów zadań w technikach projekcyjnych | 🎓 A |
| RISB — Wskaźnik Ogólnego Przystosowania | 🔒 R |
| Metoda Konfrontacji z Sobą Hermansa | 🔒 R |

### 🧸 Pracownia Diagnozy Dziecka — 🌍 1 · 🎓 4 · 🔒 12

| Zagadnienie | Propozycja |
|---|---|
| Skala Stanford-Binet 5 (SB5) | 🔒 R |
| Bateria Leiter-3 | 🔒 R |
| Dziecięca Skala Rozwojowa (DSR) | 🔒 R |
| Rysunkowy Test Twórczego Myślenia (TCT-DP) | 🔒 R |
| SB5 — unikalna właściwość | 🔒 R |
| Skale Wechslera — zakresy wiekowe | 🔒 R |
| APIS-P(R) — forma i wiek | 🔒 R |
| DSR — dwie skale | 🔒 R |
| TAT a CAT | 🔒 R |
| Leiter-3 w diagnozie rozwojowej | 🔒 R |
| Poufność wobec nastolatka i rodziców | 🌍 B |
| TCT-DP — kryteria oceny | 🔒 R |
| Dobór testu do wieku i warunków | 🎓 A |
| STAIC i wersje dziecięce narzędzi | 🔒 R |
| Techniki projekcyjne u dzieci | 🎓 A |
| Obserwacja dzieci — uczestnicząca czy nie | 🎓 A |
| Diagnoza dziecka a protodiagnoza otoczenia | 🎓 A |

### 🧠 Pawilon Neuropsychologii — 🌍 3 · 🎓 6 · 🔒 7

| Zagadnienie | Propozycja |
|---|---|
| Test Sortowania Kart z Wisconsin (WCST) | 🔒 R |
| Krótka Skala Oceny Stanu Umysłowego (MMSE) | 🔒 R |
| Skala SOAS-R w Obserwacji Agresji | 🔒 R |
| Diagnoza Ambulatoryjna (Ambulatory Assessment) | 🎓 A |
| Inteligencja płynna a skrystalizowana | 🌍 B |
| TMS — postać zadania i ograniczenie | 🔒 R |
| WCST — procedura badania | 🔒 R |
| MMSE — zastosowanie i normy | 🔒 R |
| Test Bendera — dopuszczalne zastosowanie | 🔒 R |
| Testy słowne a bezsłowne | 🎓 A |
| Granice metod neuropsychologicznych | 🎓 A |
| Aparatura i narzędzia elektroniczne w obserwacji | 🎓 A |
| Wymóg świadomej zgody przy aparaturze | 🌍 B |
| Centrum rozwoju (Development Center) | 🎓 A |
| Zmęczenie a wyniki testów wykonawczych | 🎓 A |
| Diagnoza nozologiczna a rola psychiatry | 🌍 B |

### 🤝 Klinika Relacji i Rodziny — 🌍 2 · 🎓 4 · 🔒 10

| Zagadnienie | Propozycja |
|---|---|
| Test Stosunków Rodzinnych (TSR) | 🔒 R |
| Kwestionariusz Komunikacji Małżeńskiej (KKM) | 🔒 R |
| Kwestionariusz CISS (Endler & Parker) | 🔒 R |
| Kwestionariusz Relacji Rodzinnych (KRR) | 🔒 R |
| Trzy wymiary KKM | 🔒 R |
| Zestaw metod do relacji rodzinnych | 🔒 R |
| Techniki socjometryczne | 🎓 A |
| Diagnoza rodziny jako diagnoza interakcji | 🎓 A |
| RVS w porównywaniu partnerów | 🔒 R |
| Bezstronność przy diagnozie par i rodzin | 🌍 B |
| PROKOS — Profil Kompetencji Społecznych | 🔒 R |
| TSR jako metoda hybrydowa | 🔒 R |
| Test Rysunku Rodziny — status metodologiczny | 🌍 B |
| Metoda 360 stopni | 🎓 A |
| Diagnoza interakcyjna a rola klienta | 🎓 A |
| INTE a kompetencje społeczne | 🔒 R |
