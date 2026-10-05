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
 4. zmienia klucz zapisu (wersje mają osobne zapisy w przeglądarce) i tytuł strony,
 5. sprawdza, że w wyniku nie został ani jeden wzorzec odpowiedzi z usuniętych zagadnień.
Gdy coś się nie zgadza, kończy się błędem i niczego nie zapisuje.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'Akademia diagnosty', 'akademia_diagnosty_miasteczko.html')
DST = os.path.join(ROOT, 'Akademia diagnosty', 'akademia_diagnosty_publiczna.html')


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
                ca = re.search(r'canonicalAnswer:\s*"((?:[^"\\]|\\.)*)"', body)
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

    # 4) zapis i tytuł
    old_key = "const SAVE_KEY = 'akademia_freudowice_v1';"
    if html.count(old_key) != 1:
        fail('nie znaleziono klucza zapisu')
    html = html.replace(old_key, "const SAVE_KEY = 'akademia_freudowice_publiczna_v1';")
    html = html.replace('<title>Akademia Diagnosty — Freudowice Zdrój</title>', '<title>Akademia Diagnosty — Freudowice Zdrój (wersja publiczna)</title>', 1)
    html = html.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n<!-- WERSJA PUBLICZNA — plik zbudowany przez narzedzia/zbuduj_publiczna.py z akademia_diagnosty_miasteczko.html. Nie edytuj go ręcznie. -->', 1)

    # 5) kontrola: żaden wzorzec odpowiedzi z usuniętych zagadnień nie może zostać w pliku
    left = [qid for qid, t in texts if t[:60] in html]
    if left:
        fail('w wersji publicznej zostały treści zagadnień: ' + ', '.join(left))
    for qid in removed:
        if re.search(r'\bid:\s*["\']%s["\']' % re.escape(qid), html):
            fail('zostało zagadnienie ' + qid)
    if 'TYLKO-AKADEMIA:START' in html or "Prof. Konstanty Przypis" in html and 'NPCS.przypis' in html:
        fail('został blok tylko dla studentów')

    open(DST, 'w', encoding='utf-8').write(html)
    by = {}
    for v in tiers.values():
        by[v] = by.get(v, 0) + 1
    print(f'OK: {os.path.relpath(DST, ROOT)}')
    print(f'   usunięte zagadnienia: {len(removed)} (🎓 {sum(1 for q in removed if tiers[q] == "A")}, 🔒 {sum(1 for q in removed if tiers[q] == "R")}), zostało: {kept}')
    print(f'   usunięte bloki tylko dla studentów: {nblk}')


if __name__ == '__main__':
    main()
