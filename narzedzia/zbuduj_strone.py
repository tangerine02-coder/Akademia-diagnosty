#!/usr/bin/env python3
"""Buduje folder strona/ do publikacji w Firebase Hosting (Etap 7, 2026-10-19).

Użycie (w folderze repo):
    python3 narzedzia/zbuduj_strone.py
    firebase deploy --only hosting,firestore:rules

Co robi:
 1. buduje wersję publiczną (narzedzia/zbuduj_publiczna.py),
 2. kopiuje ją jako strona/index.html (obok są akademia.html, admin.html, konto.js…),
 3. sprawdza, że w strona/ nie ma wersji akademickiej ani bloków tylko dla studentów —
    hosting jest publiczny, a wersja akademicka trafia tylko do bazy (panel admina → Paczka Akademii).
Gdy coś się nie zgadza, kończy się błędem.
"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'Akademia diagnosty', 'akademia_diagnosty_publiczna.html')
STRONA = os.path.join(ROOT, 'strona')
WYMAGANE = ['akademia.html', 'admin.html', 'konto.js', 'firebase-config.js', 'styl.css', 'uczelnie-start.json']
# znaki rozpoznawcze wersji akademickiej: żaden plik na hostingu nie może ich mieć
ZAKAZANE = ["const WERSJA = 'akademicka'", 'TYLKO-AKADEMIA:START', 'NPCS.przypis']


def fail(msg):
    print('BŁĄD:', msg)
    sys.exit(1)


def main():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'narzedzia', 'zbuduj_publiczna.py')])
    if r.returncode:
        fail('nie udało się zbudować wersji publicznej')
    for name in WYMAGANE:
        if not os.path.exists(os.path.join(STRONA, name)):
            fail('brak pliku strona/' + name)
    shutil.copyfile(PUB, os.path.join(STRONA, 'index.html'))

    for dirpath, _, files in os.walk(STRONA):
        for name in files:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, ROOT)
            if name.endswith('.html') and 'miasteczko' in name:
                fail(rel + ' wygląda na wersję akademicką — nie może trafić na hosting')
            text = open(path, encoding='utf-8', errors='ignore').read()
            for z in ZAKAZANE:
                if z in text:
                    fail(f'{rel} zawiera „{z}” — wersja akademicka nie może trafić na hosting')
    index = open(os.path.join(STRONA, 'index.html'), encoding='utf-8').read()
    if "const WERSJA = 'publiczna';" not in index:
        fail('strona/index.html nie jest wersją publiczną')

    cfg = open(os.path.join(STRONA, 'firebase-config.js'), encoding='utf-8').read()
    print('OK: strona/ gotowa do publikacji (index.html = wersja publiczna).')
    if 'export default null' in cfg:
        print('   Uwaga: strona/firebase-config.js jest pusty — logowanie do Akademii będzie wyłączone.')
    print('   Dalej: firebase deploy --only hosting,firestore:rules')


if __name__ == '__main__':
    main()
