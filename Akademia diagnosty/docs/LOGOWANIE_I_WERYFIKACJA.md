# 🎓 Logowanie i weryfikacja — wejście do Akademii (Etap 7)

*2026-10-19. Plan i stan budowy. Decyzje autorki są oznaczone ✅, propozycje AI — **[do przejrzenia]** (też w `DO_PRZEJRZENIA.md`, punkty 85–91).*

## Decyzje autorki (19.10)
- ✅ Jedna gra pod jednym adresem. Repozytorium zostaje prywatne, bez osobnego publicznego repo.
- ✅ Do Akademii wpuszczają **oba warunki naraz**: potwierdzony e-mail uczelni i osobisty kod od prowadzącego.
- ✅ Dla kogo: studenci, pracownicy i absolwenci **wszystkich polskich uczelni** (publicznych i prywatnych).
- ✅ Kody: **jednorazowe, dla każdej osoby**.

## Propozycje AI [do przejrzenia]
- **Absolwenci**: kod typu „absolwent” wpuszcza z dowolnym potwierdzonym e-mailem, bo uczelnie zwykle zamykają skrzynkę po studiach. Kody „student” i „pracownik” wymagają e-maila uczelni.
- **E-mail uczelni** = każdy adres w domenie `.edu.pl` oraz adresy z listy domen uczelni spoza `.edu.pl` (np. `umk.pl`, `kul.pl`, `uni.lodz.pl`) razem z subdomenami (np. `stud.umk.pl`, `edu.uni.lodz.pl`). Listę zmieniasz w panelu admina, bez zmian w kodzie. Lista startowa: `strona/uczelnie-start.json`.
- **Konto**: e-mail i hasło (min. 8 znaków) plus mail z linkiem potwierdzającym adres. Logowanie samym linkiem z maila odpada, bo na darmowym planie to tylko 5 maili dziennie.
- **Firebase, darmowy plan Spark**: Hosting (strona), Authentication (konta), Firestore (baza) w regionie `europe-central2` (Warszawa).
- **Kod**: 12 znaków — wielkie litery bez I, L, O i cyfry 2–9 — w zapisie `K7QM-3XPA-9RTD`. Ma typ (student / pracownik / absolwent), opis (np. „UMK, psychologia, II rok, 2026/27”) i datę ważności. Po użyciu jest przypisany do konta i nie działa drugi raz.

## Jak to działa
1. **`index.html`** — wersja publiczna gry (dla każdego). Na dolnym pasku jest przycisk **🎓 Akademia**: krótko mówi, czym jest Akademia, i prowadzi do `akademia.html`.
2. **`akademia.html`** — wejście do Akademii: logowanie albo zakładanie konta → mail z linkiem → kod od prowadzącego → wejście.
3. Po weryfikacji `akademia.html` pobiera z bazy **paczkę Akademii** (spakowaną wersję akademicką) i uruchamia ją na całym ekranie. Paczkę mogą czytać tylko zweryfikowane konta i admini — pilnują tego reguły bazy. Przeglądarka trzyma kopię, więc kolejne wejścia są szybkie; nowa paczka pobiera się sama.
4. Przy pierwszym wejściu do Akademii gra proponuje **przeniesienie postępu** z wersji publicznej (ta sama przeglądarka). Zapisy obu wersji dalej są osobne.
5. W Akademii przycisk 🎓 pokazuje konto, **wylogowanie** i powrót do wersji publicznej.
6. **`admin.html`** — panel autorki: kody (generowanie, lista, CSV, unieważnianie), paczka Akademii (wgranie nowego pliku), uczelnie (lista domen), osoby z dostępem (odbieranie dostępu).

## Dane w bazie (Firestore)
| Kolekcja | Dokument | Pola | Kto czyta / pisze |
|---|---|---|---|
| `kody` | kod (12 znaków) | `typ`, `etykieta`, `waznyDo`, `uzyty`, `uzytyPrzez`, `uzytyKiedy`, `utworzono` | tylko admini; osoba z kontem może jedynie „zużyć” wolny kod dla siebie |
| `studenci` | UID konta | `email`, `kod`, `typ`, `etykieta`, `kiedy` | właściciel konta i admini; tworzy się tylko razem ze zużyciem pasującego kodu |
| `akademia` | `info`, `czesc-0`, `czesc-1`… | wersja, liczba części, rozmiar, SHA-256; części spakowanego pliku | zweryfikowani i admini; piszą tylko admini |
| `config` | `uczelnie` | `domeny` (lista) | czyta każdy; piszą admini |
| `admini` | UID konta | dowolne, np. `imie` | tylko z konsoli Firebase |

## Bezpieczeństwo — co chroni, a czego nie
- Weryfikacja dzieje się w **regułach bazy** (`firebase/firestore.rules`), a nie w przeglądarce, więc nie da się jej obejść, grzebiąc w kodzie gry.
- Wersji akademickiej **nie ma na hostingu** (hosting jest publiczny) — jest tylko w bazie. Skrypt `narzedzia/zbuduj_strone.py` sprawdza przed każdą publikacją, że do folderu `strona/` nie trafiła.
- Osoba z dostępem może zapisać pobraną grę i komuś ją przekazać. Logowanie chroni przed dostępem z przypadku, a nie przed kimś, kto ma dostęp — tak działa każdy zamknięty obieg.
- Plik `strona/firebase-config.js` nie jest tajny: identyfikuje projekt, a dostęp pilnują reguły.

## Dane osobowe (RODO) — minimum
- Zapisujemy tylko: e-mail, datę weryfikacji, kod i jego opis.
- Informacja przy zakładaniu konta i przycisk „Usuń konto” w `akademia.html`.
- Baza w UE (Warszawa).
- **[do decyzji autorki]** Kto jest administratorem danych (Ty jako osoba prywatna, fundacja, uczelnia?). Przed szerszym udostępnieniem warto dodać krótką politykę prywatności.

## Co musisz zrobić — projekt Firebase (ok. 15 min)
1. [console.firebase.google.com](https://console.firebase.google.com) → **Utwórz projekt**, np. `akademia-diagnosty` (Google Analytics można wyłączyć).
2. **Authentication** → Rozpocznij → Metoda logowania → **E-mail/hasło** → włącz (bez „Link w e-mailu”). Szablony → język **polski**.
3. **Firestore Database** → Utwórz bazę → lokalizacja **europe-central2 (Warszawa)** → tryb produkcyjny.
4. Ustawienia projektu → Twoje aplikacje → **Web (</>)** → zarejestruj (np. „gra”) → skopiuj `firebaseConfig` i wklej mi albo do `strona/firebase-config.js`.
5. Na komputerze, w folderze repo: `npm install -g firebase-tools`, `firebase login`, `firebase use --add` (wybierz projekt).
6. `python3 narzedzia/zbuduj_strone.py`, potem `firebase deploy --only hosting,firestore:rules`.
7. Otwórz `https://<projekt>.web.app/admin.html` → załóż konto → potwierdź mail → skopiuj UID z panelu → w konsoli: Firestore → kolekcja **`admini`** → dokument o ID = UID (pole np. `imie: "Sylwia"`) → odśwież panel.
8. W panelu: **Uczelnie** → „Wczytaj listę startową” → Zapisz; **Paczka Akademii** → wybierz `akademia_diagnosty_miasteczko.html` → Wgraj; **Kody** → wygeneruj.

## Testy
- `tests/akademia_test.py` — cały przepływ w przeglądarce z udawanym Firebase (`tests/fake_firebase/`): konto, mail, kod (dobry, zużyty, nie pasujący do e-maila, absolwenta), paczka, przeniesienie postępu, wylogowanie z gry, panel admina.
- `firebase/testy/reguly.test.mjs` — 13 testów prawdziwych reguł w emulatorze Firebase. Uruchamia je **GitHub Actions** (`.github/workflows/reguly.yml`) po każdej zmianie w `firebase/` albo ręcznie (Actions → „Reguły bazy (emulator)” → Run workflow); 19.10: 13/13 ✅. Lokalnie: `cd firebase && npm install && npm test` (Java 21).

## Limity darmowego planu (Spark)
- 1000 maili z linkiem potwierdzającym dziennie, 150 resetów hasła dziennie.
- 100 nowych kont na godzinę z jednego adresu IP — cała sala w jednej sieci Wi-Fi może to przekroczyć; wtedy część osób zakłada konto później albo z telefonu.
- Hosting: 360 MB transferu dziennie; jedno wejście do wersji publicznej to ok. 0,6 MB, więc ok. 600 wejść dziennie.
- Firestore: 50 000 odczytów i 20 000 zapisów dziennie (paczka Akademii pobiera się raz na wersję).

## Stan
- ⚡ Zbudowane 19.10: reguły bazy z testami, `strona/akademia.html`, `strona/admin.html`, `strona/konto.js`, przycisk 🎓 w grze (blok „ETAP 7 · AKADEMIA — WEJŚCIE”), `narzedzia/zbuduj_strone.py`. `tests/akademia_test.py` przechodzi (67 sprawdzeń z udawanym Firebase).
- ✅ Reguły bazy sprawdzone w emulatorze (GitHub Actions, 13/13, 19.10).
- ⏳ Czeka na autorkę: projekt Firebase (kroki 1–8).
- 💭 Później: konto także dla graczy wersji publicznej (zapis w chmurze na wielu urządzeniach); automatyczna publikacja po każdej zmianie (GitHub Actions).

## Pliki
| Plik | Co robi |
|---|---|
| `strona/index.html` | wersja publiczna; buduje ją `narzedzia/zbuduj_strone.py` (nie ma jej w repo) |
| `strona/akademia.html` | logowanie, mail, kod, konto i dane, uruchomienie Akademii w ramce |
| `strona/admin.html` | panel autorki |
| `strona/konto.js` | wspólny moduł: Firebase, kody, paczka, kopia w przeglądarce, komunikaty po polsku |
| `strona/firebase-config.js` | konfiguracja projektu (na razie pusta) |
| `strona/uczelnie-start.json` | startowa lista domen uczelni spoza `.edu.pl` |
| `firebase/firestore.rules` | reguły bazy — tu naprawdę dzieje się weryfikacja |
| `firebase/testy/reguly.test.mjs` | testy reguł (emulator) |
| `firebase.json` | hosting = folder `strona/`, reguły z `firebase/` |
