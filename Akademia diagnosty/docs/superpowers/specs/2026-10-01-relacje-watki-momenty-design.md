# Relacje z mieszkańcami, małe wątki, Momenty i „Mój tydzień” — projekt

*2026-10-01 (popołudnie). Ciąg dalszy `docs/WIZJA_I_ROADMAP.md` po module PROFIL.*
*Decyzje autorki: hobby = 📸 Momenty; relacje = etapy słowami; fabuła = sandbox + małe wątki; budowa od razu.*
*Decyzje podjęte bez niej: **[do przejrzenia]**.*

## 1. Relacje z mieszkańcami — etapy słowami
- Każdy człowiek w mieście ma z graczem relację: · jeszcze się nie znacie → 🙂 znajoma twarz → 🤝 dobra znajomość → 💛 przyjaźń. Bez liczb na ekranie.
- Bliskość rośnie z: rozmów w różne dni, rozmów w stylu NVC (ocena trochę oddala), wspólnych posiłków, eksperymentów, dylematów, rozdziałów wątków. **[do przejrzenia: progi]**
- Etap nie spada (relacje mogą ostygnąć w życiu, ale gra nie karze za nieobecność).
- Efekty: przy nowym etapie NPC mówi coś ciepłego; od „dobrej znajomości” wita gracza po imieniu; przyjaciele pojawiają się w wieczornym „📞 Zadzwoń do…”.
- Profil → nowa zakładka **🫂 Ludzie**: kogo znasz, jak blisko, gdzie mieszka, co już o tej osobie wiesz.

## 2. Małe wątki (sandbox)
- 6 kilkudniowych historii po 3 rozdziały (rozdział najwyżej raz dziennie, przy rozmowie z daną osobą): Rybak (wędka ojca — żałoba), Heniek (lęk przed psami — stopniowe oswajanie), Zenon (niewidzialny barista — potrzeba uznania), Ida (berek dla jednej osoby — przyjaźń dzieci), Burmistrz (zebranie mieszkańców — poczucie wpływu), Ratownik (każda głowa w wodzie — przeciążenie i odpoczynek).
- Każdy wątek ma wybór bez złej odpowiedzi, domknięcie z krótką psychologiczną puentą, wpis w dzienniku i propozycję zdjęcia.
- NPC pamiętają wcześniejsze wybory (np. styl rozmowy NVC).

## 3. 📸 Momenty (hobby)
- Klawisz F albo przycisk 📸 na dolnej belce: zdjęcie aktualnego kadru + podpis gracza (opcjonalny).
- Album w Profilu (zakładka **📸 Album**), do 30 zdjęć; do 3 zdjęć można powiesić w ramkach na ścianie domu.
- Zdjęcia (obrazki) trzymane w osobnym kluczu przeglądarki (`akademia_album_v1`), bo zapis w chmurze ma limit rozmiaru; w pliku zapisu (⬇️ Pobierz) są dołączone. Na innym urządzeniu przez chmurę przechodzą tylko podpisy. **[do przejrzenia]**

## 4. 📈 Mój tydzień (samoopieka — „gracz widzi wzory sam”)
- W zakładce 💛 Jak się mam: ostatnie 7 dni — sen przed dniem, poranny nastrój, posiłki, rozmowy, spacer, nauka. Bez wniosków ze strony gry; tylko zaproszenie: „Widzisz jakiś wzór?”.
- Mistrz katedry, gdy postać jest wyraźnie zaniedbana, mówi raz na kilka dni: „Nie możesz dobrze diagnozować kogoś innego, jeśli nie znasz i nie dbasz o siebie…”.

## Kod i testy
Pliki `.profil-work/src/08-tydzien.js`, `09-relacje.js`, `10-watki.js`, `11-momenty.js` (ten sam blok PROFIL, `node .profil-work/build.js`).
Testy `.profil-work/relacje.test.js` — tylko pod `http://test.localhost:8765`.
