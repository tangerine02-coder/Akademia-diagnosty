#!/usr/bin/env python3
"""Buduje wersję publiczną gry (BAZA) z wersji akademickiej (ROZSZERZENIE).

Użycie (w folderze repo):
    python3 narzedzia/zbuduj_publiczna.py

Wejście:  Akademia diagnosty/akademia_diagnosty_miasteczko.html  — wersja akademicka, tu wprowadzamy zmiany
Wyjście:  Akademia diagnosty/akademia_diagnosty_publiczna.html   — wersja publiczna, NIE edytować ręcznie

Co robi skrypt:
 1. przełącza  const WERSJA = 'akademicka'  na  'publiczna',
 2. wycina z pliku wszystkie zagadnienia 🎓 (A) i 🔒 (R) według mapy TIERS
    (z bazy QUESTIONS_DB i z list oznaczonych /* PYTANIA */),
 3. wycina bloki między <!-- TYLKO-AKADEMIA:START … --> a <!-- TYLKO-AKADEMIA:END -->,
 4. podmienia fragmenty z osobną wersją dla publicznej (w jednym wierszu):
        /*W-AKADEMICKIEJ*/ 'tekst akademicki' /*W-PUBLICZNEJ: 'tekst publiczny' */
    W pliku akademickim drugi tekst jest tylko komentarzem, więc gra go nie widzi.
    W publicznym zostaje sam tekst publiczny,
 5. zmienia klucz zapisu (wersje mają osobne zapisy w przeglądarce) i tytuł strony,
 6. sprawdza, że w wyniku nie został ani jeden wzorzec odpowiedzi z usuniętych zagadnień,
    żadna nazwa konkretnego testu z listy ZAKAZANE_W_PUBLICZNEJ ani źródło z zajęć (ZAJECIA_W_PUBLICZNEJ).
Gdy coś się nie zgadza, kończy się błędem i niczego nie zapisuje.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'Akademia diagnosty', 'akademia_diagnosty_miasteczko.html')
DST = os.path.join(ROOT, 'Akademia diagnosty', 'akademia_diagnosty_publiczna.html')


# Nazwy konkretnych testów, których nie może być w wersji publicznej (DO_PRZEJRZENIA, punkt 73).
# Celowo zostają (decyzja 19.10): Archiwum Szarlatanerii (Lüscher, Szondi, Rorschach, Bender, Wechsler do diagnozy
# osobowości), efekt Stroopa, Wechsler jako przykład skali IQ na Błoniach oraz skale z badań i ocena klinicysty:
# GAF, SDO, RWA, MBEA.
ZAKAZANE_W_PUBLICZNEJ = [
    r'MMPI', r'WCST', r'Wisconsin', r'MMSE', r'\bEPQ', r'Leiter', r'\bTMS\b', r'Test Matryc', r'Raven',
    r'Stanford-Binet', r'\bAPIS\b', r'\bDSR\b', r'Łączenia Punktów', r'\bKRR\b', r'\bKKM\b', r'\bTSR\b',
    r'\bWAIS', r'\bWISC', r'\bNEO-(?:FFI|PI)', r'\bSTAI\b', r'\bBDI\b',
]
# Źródła z zajęć (rok, semestr, notatki, egzaminy) — w wersji publicznej przy domach jest sam temat (decyzja 19.10):
#   src: /*W-AKADEMICKIEJ*/ '4 ROK › 7 semestr › …' /*W-PUBLICZNEJ: 'Sam temat' */
ZAJECIA_W_PUBLICZNEJ = [
    r'\d ROK ›', r'\bSEM ›', r'semestr ›', r'Notatki dysk', r'Notatki ›', r'kolokwium (?:z )?20\d\d',
    r'pytania do egzaminu', r'zagadnień na egzamin', r'przygotowań do egzaminu', r'Z Twoich materiałów',
    r'Twoich notatek z \d', r'z Twoich studiów', r'Według slajdów',
]
ALT = re.compile(r'/\*W-AKADEMICKIEJ\*/\s*(.+?)\s*/\*W-PUBLICZNEJ:\s*(.+?)\s*\*/')


def fail(msg):
    print('BŁĄD:', msg)
    sys.exit(1)


def scan_array(text, start):
    """text[start] == '['. Zwraca (koniec_tablicy, [(początek, koniec) obiektów na najwyższym poziomie])."""
    i, depth, objs, obj_start = start, 0, [], None
    n = len(text)
    while i < n:
        c = text[i]
        if c in '"\'`':                                   # napisy (z obsługą \")
            q = c; i += 1
            while i < n and text[i] != q:
                i += 2 if text[i] == '\\' else 1
        elif c == '/' and text[i + 1] == '/':              # komentarz do końca wiersza
            i = text.index('\n', i)
            continue
        elif c == '/' and text[i + 1] == '*':
            i = text.index('*/', i) + 2
            continue
        elif c in '[{(':
            depth += 1
            if c == '{' and depth == 2:
                obj_start = i
        elif c in ']})':
            if c == '}' and depth == 2 and obj_start is not None:
                objs.append((obj_start, i + 1))
                obj_start = None
            depth -= 1
            if depth == 0:
                return i, objs
        i += 1
    fail('nie znaleziono końca tablicy pytań')


def main():
    if not os.path.exists(SRC):
        fail('brak pliku ' + SRC)
    html = open(SRC, encoding='utf-8').read()

    m = re.search(r'/\* TIERS:START \*/(.*?)/\* TIERS:END \*/', html, re.S)
    if not m:
        fail('brak mapy TIERS w pliku gry')
    tiers = json.loads(m.group(1))
    drop = {k for k, v in tiers.items() if v in ('A', 'R')}

    # 1) wersja
    if html.count("const WERSJA = 'akademicka';") != 1:
        fail("nie znaleziono dokładnie jednego  const WERSJA = 'akademicka';")
    html = html.replace("const WERSJA = 'akademicka';", "const WERSJA = 'publiczna';")

    # 2) zagadnienia 🎓 i 🔒
    starts = [mm.end() - 1 for mm in re.finditer(r'const QUESTIONS_DB = \[', html)] + [mm.end() - 1 for mm in re.finditer(r'/\* PYTANIA \*/ \[', html)]
    if len(starts) < 2:
        fail('nie znaleziono list pytań (QUESTIONS_DB i /* PYTANIA */)')
    cuts, removed, kept, texts = [], [], 0, []
    for st in starts:
        _, objs = scan_array(html, st)
        for a, b in objs:
            body = html[a:b]
            idm = re.search(r'\bid:\s*["\']([^"\']+)["\']', body)
            if not idm:
                continue
            qid = idm.group(1)
            if qid in drop:
                end = b
                tail = re.match(r'\s*,', html[end:])
                if tail:
                    end += tail.end()
                beg = a
                while beg > 0 and html[beg - 1] in ' \t':
                    beg -= 1
                if html[end:end + 1] == '\n':
                    end += 1
                cuts.append((beg, end))
                removed.append(qid)
                ca = re.search(r'canonicalAnswer:\s*(?:/\*W-AKADEMICKIEJ\*/\s*)?"((?:[^"\\]|\\.)*)"', body)
                if ca:
                    texts.append((qid, ca.group(1)))
            else:
                kept += 1
    for a, b in sorted(cuts, reverse=True):
        html = html[:a] + html[b:]
    missing = drop - set(removed)
    if missing:
        fail('w pliku nie ma zagadnień z mapy TIERS: ' + ', '.join(sorted(missing)))

    # 3) bloki tylko dla studentów
    html, nblk = re.subn(r'<!-- TYLKO-AKADEMIA:START.*?<!-- TYLKO-AKADEMIA:END -->\n?', '', html, flags=re.S)
    if nblk < 1:
        fail('nie znaleziono bloków TYLKO-AKADEMIA')

    # 4) fragmenty z osobną wersją dla publicznej
    nstart = html.count('/*W-AKADEMICKIEJ*/')
    html, nalt = ALT.subn(lambda mm: mm.group(2), html)
    if nalt != nstart or '/*W-AKADEMICKIEJ*/' in html or '/*W-PUBLICZNEJ:' in html:
        fail('znaczniki /*W-AKADEMICKIEJ*/ i /*W-PUBLICZNEJ: … */ muszą być w parach, w jednym wierszu')

    # 5) zapis i tytuł
    old_key = "const SAVE_KEY = 'akademia_freudowice_v1';"
    if html.count(old_key) != 1:
        fail('nie znaleziono klucza zapisu')
    html = html.replace(old_key, "const SAVE_KEY = 'akademia_freudowice_publiczna_v1';")
    html = html.replace('<title>Akademia Diagnosty — Freudowice Zdrój</title>', '<title>Akademia Diagnosty — Freudowice Zdrój (wersja publiczna)</title>', 1)
    html = html.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n<!-- WERSJA PUBLICZNA — plik zbudowany przez narzedzia/zbuduj_publiczna.py z akademia_diagnosty_miasteczko.html. Nie edytuj go ręcznie. -->', 1)

    # 6) kontrola: żaden wzorzec odpowiedzi z usuniętych zagadnień nie może zostać w pliku
    left = [qid for qid, t in texts if t[:60] in html]
    if left:
        fail('w wersji publicznej zostały treści zagadnień: ' + ', '.join(left))
    for qid in removed:
        if re.search(r'\bid:\s*["\']%s["\']' % re.escape(qid), html):
            fail('zostało zagadnienie ' + qid)
    if 'TYLKO-AKADEMIA:START' in html or "Prof. Konstanty Przypis" in html and 'NPCS.przypis' in html:
        fail('został blok tylko dla studentów')
    names = [p for p in ZAKAZANE_W_PUBLICZNEJ if re.search(p, html)]
    if names:
        fail('w wersji publicznej są nazwy testów (' + ', '.join(names) + ') — oznacz te miejsca '
             '/*W-AKADEMICKIEJ*/ … /*W-PUBLICZNEJ: … */ albo zmień kategorię zagadnienia w TIERS')
    course = [p for p in ZAJECIA_W_PUBLICZNEJ if re.search(p, html)]
    if course:
        fail('w wersji publicznej są źródła z zajęć (' + ', '.join(course) + ') — przy src: dopisz '
             "/*W-AKADEMICKIEJ*/ '…' /*W-PUBLICZNEJ: 'sam temat' */")

    open(DST, 'w', encoding='utf-8').write(html)
    by = {}
    for v in tiers.values():
        by[v] = by.get(v, 0) + 1
    print(f'OK: {os.path.relpath(DST, ROOT)}')
    print(f'   usunięte zagadnienia: {len(removed)} (🎓 {sum(1 for q in removed if tiers[q] == "A")}, 🔒 {sum(1 for q in removed if tiers[q] == "R")}), zostało: {kept}')
    print(f'   usunięte bloki tylko dla studentów: {nblk}')
    print(f'   fragmenty podmienione na wersję publiczną: {nalt}')


if __name__ == '__main__':
    main()
