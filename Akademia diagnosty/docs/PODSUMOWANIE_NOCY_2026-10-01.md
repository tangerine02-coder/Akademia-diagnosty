# Co zrobiłam w nocy 1.10.2026 (i rano, po wznowieniu)

Gra: `http://localhost:8765/akademia_diagnosty_miasteczko.html?v=noc` (dopisek `?v=noc` omija starą kopię w pamięci przeglądarki, a Twój zapis zostaje).
Kopia pliku sprzed nocy: `akademia_diagnosty_miasteczko.przed_noca.html`.
Testowałam tylko pod `test.localhost`, więc Twój zapis jest nietknięty.
Zrobione punkty odhaczyłam w Notion z dopiskiem „ZROBIONE 1.10”.
Decyzje podjęte bez Ciebie mają oznaczenie **[do przejrzenia]**.
Sesja przerwała się w nocy około 2:20 (limit) i wznowiłam ją o 10:05.

## Paczka 1: poprawki
- **Postacie się trzęsły**: to był błąd rysowania, a nie zmęczenie ani monstera. Kamera jechała płynnie za graczem, a postacie przeskakiwały co cały piksel świata, czyli co 2–3 px ekranu, więc drgały o ±1,5 px. Teraz rysują się z dokładnością do piksela ekranu (`snapPx`).
- **Numery domów**: tabliczki są w 70% rozmiaru i lekko przygaszone.
- **Cienie-kółka**: to były losowe łaty ciemniejszej trawy w kształcie kół. Wyglądały jak cienie drzew, których tam nie ma, i ucinały się łukiem przy budynkach. Teraz to nieregularne, delikatne kępki. Doszły prawdziwe cienie pod drzewami i wąski cień przy ścianach domów, w prawo w dół, bo światło w grze pada z lewej.
- **Obserwatorium Modeli**: nowy wygląd z gzymsem, balustradą, kamiennym bębnem z okienkami i balkonem, cieniowaną kopułą z żebrami, szczeliną z gwiazdami i mosiężnym teleskopem. Nocą świecą okienka i niebieska szczelina. Ten sam styl ma Wieża Kontroli na Wyspie Lewina.
- **Teleskop na Wzgórzu Hipotez**: panorama Freudowic i wysp. Rozglądasz się strzałkami albo WASD w ograniczonym polu, a na telefonie przyciskami ◀▲▼▶. Niebo zmienia się z godziną gry (słońce, księżyc z fazą, gwiazdy), a nocą palą się światła w oknach i obraca się światło latarni. Miejsca, których jeszcze nie odwiedzono, są zamglone. Pod okularem pojawia się podpis z ciekawostką o miejscu, na które patrzysz. Easter eggi: spadająca gwiazda, rzadkie UFO (6% szans) z cytatem Sagana i monstera w oknie Pani Haliny, która przy dużej grozie „patrzy”.
- **Pomnik Mózgu w Lesie Synaps**: kolorowy model na cokole, na polanie przy przystanku, a obok często siada kruk Munin. W oknie klikasz płat i czytasz, czym się zajmuje. Są też trzy mity: „10% mózgu”, „lewo- i prawopółkulowi” oraz „dorosły mózg się nie zmienia”. Za poznanie wszystkich części jest +10 XP.
- Kod: teleskop i pomnik są w osobnym `<script>` „NOC 2026-10-01 · TELESKOP I POMNIK MÓZGU”, a reszta to punktowe poprawki w głównym skrypcie.

## Paczka 2: sklep i kawiarnia
Kod: `<script>` „NOC 2026-10-01 · SKLEP…”. Testy `.noc-work/sklep.test.js`: 30/30.
- **Strefa Komfortu** [do przejrzenia]: tak nazywa się teraz sklep z meblami („Nie wychodź ze strefy komfortu. Urządź ją.”). Nazwa zmieniona też w opisie dzielnicy, kwestii sąsiadki, liście cioci, na mapie i w panelu urządzania.
- **Ceny ×3**: Kozetka kosztuje 360 🟡, fiołki 36 🟡.
- **18 nowych mebli i dekoracji** z własnymi rysunkami: fikus „Superego”, bonsai cierpliwości, pufa „Regresja”, fotel bujany Eriksona, lampa „Oświecenie” (świeci), globus kulturowy (WEIRD), skrzynka Skinnera z gołębiem, teleskop, pianino, akwarium z meduzami (świeci), Złota Kozetka (1500 🟡), zegar Dalego, portret Jamesa, koło emocji Plutchika, tablica korkowa z nitkami, neon „Cogito” (świeci na różowo), dywan owalny i dywan „Neuron”. Sklep ma filtry kategorii i oznaczenie 🏆 „na zbieranie”.
- **Półka z przekąskami**: każda rzecz ma plus od razu i minus później, z krótką ciekawostką.
  - Energetyk: +30 ⚡ i przez 2 h szybszy chód („Czuję się ŚWIETNIE!”), potem z godziny na godzinę coraz wolniej. Ratuje tylko zwykły sen we własnym łóżku, a świadome śnienie jest wtedy niedostępne.
  - Baton: −10 ⚡ po godzinie.
  - Chipsy: −5 ⚡ po godzinie.
  - Cola: po 16:00 skraca sen, −8 ⚡ po godzinie.
  - Pączek: −15 ⚡ po 2 h.
- **Eliksir Podpowiedzi** (45 🟡): jedna podpowiedź. W quizie ABCD skreśla jedną złą odpowiedź, a przy pytaniu w katedrze pokazuje wskazówkę bez utraty XP.
- **Kawiarnia**: 8 napojów z pikselowym podglądem, różnymi cenami i plusem/minusem.
  - Kofeina po 16:00 skraca sen (Drake i in., 2013).
  - Po 3 dniach kawy z rzędu pojawia się tolerancja: kawa daje 70% energii.
  - Kawa nie jest już darmowa raz dziennie. Zamiast tego Zenon stawia jeden napój bez kofeiny dziennie [do przejrzenia], żeby nie nagradzać nawyku kawy.

## Paczka 3: sen, chronotyp, myśli i wiek
Kod: `<script>` „NOC 2026-10-01 · SEN…”. Testy `.noc-work/sen.test.js`: 27/27. Stare zestawy też przechodzą: Halina 39/39, zapis 29/29, tabliczki 22/22.
- **Dług snu** liczę jak w badaniu Van Dongena i in. (2003): co noc 8 h minus przespane godziny. W tamtym badaniu 14 dni snu po 6 h dawało deficyty jak 1–2 noce bez snu.
- **Progi halucynacji** wg przeglądu Waters i in. (2018): zniekształcenia percepcji po 24–48 h bez snu, złożone halucynacje po 48–90 h, a normalny sen zwykle je usuwa. W grze wygląda to tak:
  - **14 h długu**, czyli jak noc bez snu: świat lekko „oddycha” na skraju ekranu, kątem oka miga cień, pojawiają się myśli „czy ten krzak się ruszył?”.
  - **26 h długu**, czyli jak 2 noce bez snu: na ulicy stoi przechodzień, który znika, gdy podejdziesz; ktoś szepcze imię postaci drżącymi literami; zegar w HUD na sekundę pokazuje „25:61”.
  - Najszybsza droga do tego to spanie od 2:00 przez 5 nocy (zniekształcenia) albo 9 nocy (halucynacje). Jedna porządna noc zdejmuje halucynacje, a dług spada stopniowo.
  - Konsekwencje są łagodne, tak jak ustaliłaś z sesją „Wizja”: tylko obraz i myśli, bez kar w nauce. Wolniejszy chód przy długu robi moduł PROFIL.
- **Paraliż przysenny**: rzadko, przy przebudzeniu po niewyspanych albo nieregularnych nocach. Przez 7 s nie da się ruszyć, a w ciemności stoi cień. Potem jest wyjaśnienie: atonia REM, 7,6% ludzi i 28% studentów (Sharpless i Barber, 2011), niegroźny.
- **Budzik** przy łóżku: 6:00–10:00. Dzięki niemu da się w ogóle mieć chronotyp sowy.
- **Dziennik → zakładka 🌙 Sen**:
  - dług snu z opisem,
  - chronotyp liczony ze środka snu, jak w kwestionariuszu MCTQ (skowronek, typ pośredni, sowa),
  - dziennik ostatnich nocy (paski 20:00–12:00),
  - godziny efektywności: po 15 odpowiedziach z Twojej trafności w poszczególnych godzinach, wcześniej z krzywej chronotypu („efekt synchronii”, May i in., 1993).
- **Odstawienie kofeiny**: pierwszy dzień bez kawy po 3 dniach picia przynosi ból głowy rano i −15 ⚡.
- **Myśli w tle** co 1,5–2,5 min (nigdy w trakcie nauki): niewyspanie, mało Dopaminek, nowe miejsce, późna pora, monstera, losowe śmieszne, chęci, troski, „co myślą inni” (efekt reflektora) i podpowiedzi do gry. Moduł PROFIL dokłada przez `NOC_MYSLI.dodaj` myśli o potrzebach, więc wszystko idzie jednym harmonogramem i nie spamuje.
- **Starzenie (paczka 3)**: rok gry to 112 dni. Po każdym roku przychodzi poranna myśl („strzyknęło w kolanie”, „pierwszy siwy włos?!”), a po 2, 4 i 7 latach na postaci jest coraz więcej siwych pasemek.

## Paczka 4: dom — obracanie i przestawianie
Kod: `<script>` „NOC 2026-10-01 · DOM…”. Testy `.noc-work/dom.test.js`: 26/26.
- **🔄 Obróć [R]** w trybie urządzania działa na mebel podniesiony albo wybrany z ekwipunku:
  - Dywany obracają się o 90° (4 ustawienia).
  - Kanapy, kozetki, stoliki, biurko i łóżko mają ustawienia: poziomo, pionowo, odbite i pionowo z drugiej strony. Nie stają „do góry nogami”.
  - Pozostałe meble i obrazy dają się odbić lewo–prawo [do przejrzenia: obrót wysokiego regału o 90° wyglądałby jak przewrócony].
  - Neon „Cogito” się nie odbija, bo napis byłby w lustrze.
- **Stałe meble są ruchome**: łóżko, szafę, biurko cioci Jadzi, półkę z trofeami i kominek klikasz w trybie urządzania („✋ Przenosisz…”) i stawiasz w nowym miejscu.
  - Półka i kominek przesuwają się tylko wzdłuż ściany i nie wejdą na okno. Okno i drzwi stoją w miejscu.
  - Prawy przycisk albo wyjście z trybu odkłada mebel tam, gdzie stał.
  - Kolizje, akcje (spanie, szafa, biurko), światło kominka i miejsce pobudki rano idą za meblem.
