"""Test Etapu 6 (2026-10-05): wersja akademicka i publiczna, Katedra Psychologii Religii i Płci, promotor.

Uruchomienie (w folderze repo):
    python3 narzedzia/zbuduj_publiczna.py          # najpierw wersja publiczna
    python3 -m http.server 8765 --directory "Akademia diagnosty" &
    python3 tests/etap6_test.py                    # zrzuty ekranu trafiają do tests/out/

Test działa w czystym profilu przeglądarki, więc nie dotyka prawdziwego zapisu.
"""
import asyncio, json, os, re, sys
from playwright.async_api import async_playwright

URL = os.environ.get('GAME_URL', 'http://localhost:8765/akademia_diagnosty_miasteczko.html')
PUB_URL = re.sub(r'akademia_diagnosty_miasteczko\.html', 'akademia_diagnosty_publiczna.html', URL)
OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)
fails = []

def check(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)

CLEAN = """() => { try { if (game._mg) game.mgStop(game._mg); } catch (e) {} game.closeModal(true); game.closeDialog(true); game.transition = null; game.currentBlock = null; game.state.energy = 100; }"""
HALL = """async (loc) => {
  game.closeModal(true); game.closeDialog(true);
  const zone = LOCATIONS[loc].zone; if (game.zone.id !== zone) game.setZone(zone);
  const b = game.zone.buildings.find(x => x.loc === loc);
  game.player.x = b.doorCol * 16 + 8; game.player.y = b.doorRow * 16 + 8; game.player.dir = 'up';
  game.enterDoor(b);
  await new Promise(r => setTimeout(r, 80));
  return game.dialog ? { name: game.dialog.name, pages: game.dialog.pages, opts: game.dialog.options.map(o => o.label + (o.disabled ? ' [x]' : '')) } : null;
}"""
PICK = """(prefix) => { const o = game.dialog.options.find(x => x.label.startsWith(prefix)); game.closeDialog(true); if (o && o.fn) o.fn(); return !!o; }"""
TALK = """async (id) => { game.closeModal(true); game.closeDialog(true); const n = game.npcs.find(x => x.id === id); if (!n) return null;
  game.talkTo(n); await new Promise(r => setTimeout(r, 60)); return game.dialog ? { name: game.dialog.name, pages: game.dialog.pages, opts: game.dialog.options ? game.dialog.options.map(o => o.label + (o.disabled ? ' [x]' : '')) : [] } : null; }"""

async def start_game(pg, url):
    await pg.goto(url)
    await pg.wait_for_timeout(1500)
    await pg.fill("input[placeholder*='Sylwia']", 'Testerka')
    await pg.click('text=Zamieszkaj w Freudowice Zdrój')
    await pg.wait_for_timeout(1500)
    for _ in range(8):
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(80)

async def academic(b):
    pg = await b.new_page(viewport={'width': 1100, 'height': 760})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: m.type in ('error', 'warning') and 'ETAP' in m.text and errs.append(m.text))
    await start_game(pg, URL)

    print('\n[A1] Wersja akademicka: kategorie zagadnień')
    r = await pg.evaluate("""() => { const T = ETAP6.TIERS, ids = QUESTIONS_DB.map(q => q.id), c = { A: 0, B: 0, R: 0 };
      ids.forEach(id => c[T[id] || '?'] = (c[T[id] || '?'] || 0) + 1);
      return { w: WERSJA, n: ids.length, uniq: new Set(ids).size, c, missing: ids.filter(id => !T[id]), extra: Object.keys(T).filter(id => !ids.includes(id)) }; }""")
    check(r['w'] == 'akademicka', f'WERSJA = {r["w"]}')
    check(r['n'] == 215 and r['uniq'] == 215, f'215 zagadnień (176 + 21 nowych 🌍 + 18 w nowej katedrze), bez powtórek ({r["n"]}, {r["uniq"]})')
    check(not r['missing'] and not r['extra'], f'mapa TIERS opisuje każde zagadnienie ({r["missing"][:5]}, {r["extra"][:5]})')
    check(r['c'] == {'A': 100, 'B': 67, 'R': 48}, f'podział: 🌍 67 · 🎓 100 · 🔒 48 ({r["c"]})')
    r = await pg.evaluate("() => Object.keys(LOCATIONS).map(l => [l, QUESTIONS_DB.filter(q => q.locId === l && ETAP6.TIERS[q.id] === 'B').length])")
    check(all(n >= 5 for _, n in r), f'każda katedra ma co najmniej 5 zagadnień 🌍 ({r})')
    r = await pg.evaluate("() => QUESTIONS_DB.filter(q => /_b\\d|^rel_/.test(q.id)).every(q => q.topic && q.question && q.canonicalAnswer && q.explanation && q.hint && q.points > 0 && q.expectedGroups.length >= 2 && LOCATIONS[q.locId] && q.location === LOCATIONS[q.locId].name)")
    check(r, 'nowe zagadnienia mają komplet pól (pytanie, grupy słów, wzorzec, wyjaśnienie, podpowiedź)')
    # parser lokalny zalicza wzorcową odpowiedź i nie zalicza „nie wiem”
    r = await pg.evaluate("""() => QUESTIONS_DB.filter(q => /_b\\d|^rel_/.test(q.id)).map(q => [q.id, verifyAnswer(q.canonicalAnswer, q.expectedGroups, q.question).isCorrect, verifyAnswer('nie wiem', q.expectedGroups, q.question).isCorrect]).filter(x => !x[1] || x[2])""")
    check(not r, f'pytania otwarte: wzorzec zaliczony, „nie wiem” nie ({r})')

    print('\n[A2] Kompendium ze znaczkami')
    r = await pg.evaluate(HALL, 'testy')
    await pg.evaluate(PICK, '📖')
    r = await pg.evaluate("() => ({ tags: [...document.querySelectorAll('#modal .e6-tier')].map(x => x.textContent.trim().slice(0, 2)), legend: document.getElementById('modal').innerText.includes('konkretne narzędzia') })")
    check(r['tags'].count('🔒') == 19 and r['tags'].count('🌍') == 5 and r['legend'], f'Poligon: 19 × 🔒, 5 × 🌍 i legenda ({len(r["tags"])})')
    await pg.screenshot(path=f'{OUT}/e6_kompendium_znaczki.png')

    print('\n[A3] Katedra Psychologii Religii i Płci')
    await pg.evaluate(CLEAN)
    await pg.evaluate("() => { game.setZone('port'); }")
    await pg.wait_for_timeout(300)
    r = await pg.evaluate("""() => { const b = game.zone.buildings.find(x => x.id === 'magazyn'); return { loc: b.loc, style: b.style, locked: !!b.locked, sign: b.sign, npcs: game.npcs.map(n => n.id), topics: ZONES.port.topics, solid: game.npcs.filter(n => ['rolska', 'zaslyszany'].includes(n.id)).map(n => game.zone.solid[Math.floor(n.y / 16) * game.zone.w + Math.floor(n.x / 16)]) }; }""")
    check(r['loc'] == 'religia' and r['style'] == 'e6_katedra' and not r['locked'], f'dawny Magazyn Pamięci to teraz katedra ({r["loc"]}, {r["style"]})')
    check('rolska' in r['npcs'] and 'zaslyszany' in r['npcs'] and r['solid'] == [0, 0], f'Prof. Rolska i Pan Zasłyszany stoją na wolnych kratkach ({r["solid"]})')
    check('religia' in r['topics'], 'Port ma temat katedry (fiszki, mapa)')
    await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'rolska'); game.player.x = n.x + 16; game.player.y = n.y; game.state.time = 12 * 60; }")
    await pg.wait_for_timeout(500)
    await pg.screenshot(path=f'{OUT}/e6_katedra_port.png')
    r = await pg.evaluate(HALL, 'religia')
    check(r and r['opts'][0].startswith('📖 Kompendium wiedzy (0/18)') and r['opts'][1].startswith('🎲 Mini gry (⭐ 0/12)') and r['opts'][2].startswith('📝 Zajęcia'), f'hol katedry: kompendium (18), 4 mini gry, zajęcia ({r and r["opts"]})')
    await pg.evaluate(PICK, '🎲')
    r = await pg.evaluate("() => [...document.querySelectorAll('#modal .e5-mg b')].map(x => x.textContent)")
    check(len(r) == 4 and r[3] == 'Mit czy fakt?', f'cztery mini gry, czwarta: „Mit czy fakt?” ({r})')
    await pg.evaluate("() => document.querySelector('[data-play=\"3\"]').click()")
    await pg.wait_for_timeout(300)
    await pg.screenshot(path=f'{OUT}/e6_mit_czy_fakt.png')
    await pg.evaluate("""async () => { const R = SUBJECTS.e5_religia.rooms[3];
      for (let k = 0; k < 12; k++) { const q = document.querySelector('#modal #mg-q'); if (!q) break; const it = R.items.find(x => x[0] === q.textContent); if (!it) break;
        document.getElementById(it[1] ? 'mg-t' : 'mg-f').click(); await new Promise(r => setTimeout(r, 20)); } }""")
    await pg.wait_for_timeout(400)
    r = await pg.evaluate("() => ({ t: document.getElementById('modal').innerText, s: game.roomStars('e5_religia', 3) })")
    check('Wynik: 100%' in r['t'] and r['s'] == 3, f'„Mit czy fakt?” rozegrane bezbłędnie, 3 gwiazdki ({r["s"]})')
    for i in range(3):
        r = await pg.evaluate(f"() => {{ game.closeModal(true); game.state.energy = 100; game.startMinigame('e5_religia', {i}); const ok = !!document.querySelector('#modal .panel'); if (game._mg) game.mgStop(game._mg); game.closeModal(true); return ok; }}")
        check(r, f'mini gra {i + 1} katedry startuje z pytaniami katedry')
    r = await pg.evaluate(TALK, 'rolska')
    check(r and r['name'] == 'Prof. Teodora Rolska' and any(o.startswith('⚡ Szybki quiz') for o in r['opts']) and any(o.startswith('🎲 Mini gry') for o in r['opts']), f'mistrzyni katedry: quiz, kompendium, mini gry ({r and r["opts"]})')
    r = await pg.evaluate(TALK, 'zaslyszany')
    check(r and 'Z okna' in r['pages'][0], 'Pan Zasłyszany powtarza mit, a z okna katedry pada źródło')
    # piętro po 10 zaliczonych zagadnieniach
    r = await pg.evaluate("""() => { game.closeDialog(true); const b = game.zone.buildings.find(x => x.loc === 'religia'), h0 = b.spr.SH;
      game.questionsFor('religia').slice(0, 10).forEach(q => game.markCorrect(q, 1)); game.refreshBuilding('religia');
      const b2 = game.zone.buildings.find(x => x.loc === 'religia'); return { h0, h1: b2.spr.SH, lvl: game.unlockedLevel('religia'), win: b2.win.length }; }""")
    check(r['lvl'] == 2 and r['h1'] == r['h0'] + 18, f'po 10 zaliczonych: poziom 2 i nowe piętro budynku ({r})')
    await pg.wait_for_timeout(300)
    await pg.screenshot(path=f'{OUT}/e6_katedra_pietro.png')
    r = await pg.evaluate("() => { game.closeDialog(true); const it = game.zone.interacts.find(x => x.kind === 'budowa'); game.useSpot(it); return game.dialog.pages.join(' '); }")
    check('AKTUALIZACJA 3' in r, 'plac budowy w Porcie ogłasza nową katedrę')
    r = await pg.evaluate("() => { game.closeDialog(true); const it = game.zone.interacts.find(x => x.kind === 'np_info'); game.useSpot(it); return game.dialog.pages.join(' '); }")
    check('punktu Boga' in r and 'mozaiki' in r, 'tablica Portu: „gdzie w mózgu?” o religii i płci')

    print('\n[A4] Promotor')
    await pg.evaluate(CLEAN)
    await pg.evaluate("() => game.setZone('rynek')")
    await pg.wait_for_timeout(300)
    r = await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'przypis'); return n ? { solid: game.zone.solid[Math.floor(n.y / 16) * game.zone.w + Math.floor(n.x / 16)], x: n.x, y: n.y } : null; }")
    check(r and r['solid'] == 0, f'Prof. Przypis stoi przy Bibliotece na wolnej kratce ({r})')
    await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'przypis'); game.player.x = n.x - 16; game.player.y = n.y; game.state.time = 12 * 60; }")
    await pg.wait_for_timeout(400)
    await pg.screenshot(path=f'{OUT}/e6_promotor_rynek.png')
    r = await pg.evaluate(TALK, 'przypis')
    check(r and 'Konstanty Przypis' in r['pages'][0] and len(r['opts']) == 5, f'pierwsza rozmowa: przedstawia się, 5 opcji ({r and r["opts"]})')
    r = await pg.evaluate("""() => { game.closeDialog(true); const b = game.zone.buildings.find(x => x.id === 'biblioteka'); game.player.x = b.doorCol * 16 + 8; game.player.y = b.doorRow * 16 + 8; game.enterDoor(b);
      return new Promise(res => setTimeout(() => res(game.dialog ? game.dialog.name : null), 60)); }""")
    check(r and 'Przypis' in r, f'drzwi Biblioteki prowadzą do promotora ({r})')
    # etapy
    await pg.evaluate("() => { game.closeDialog(true); game.e6Promotor('etapy'); }")
    r = await pg.evaluate("() => ({ st: document.querySelectorAll('#modal details.e6-st').length, cb: document.querySelectorAll('#modal [data-it]').length })")
    check(r['st'] == 9 and r['cb'] >= 35, f'magisterka: 9 etapów z listą punktów ({r})')
    r = await pg.evaluate("""async () => { const xp0 = game.state.stats.xp;
      for (let k = 0; k < 4; k++) { const cb = [...document.querySelectorAll('#modal [data-it^="temat:"]')].find(x => !x.checked); if (!cb) break; cb.checked = true; cb.dispatchEvent(new Event('change')); await new Promise(r => setTimeout(r, 20)); }
      const W = game.e6Pr().works.mgr; return { closed: !!W.closed.temat, dxp: game.state.stats.xp - xp0, tag: document.querySelector('#modal details[data-st="temat"] summary .tag.green') ? 1 : 0 }; }""")
    check(r['closed'] and r['dxp'] >= 4 * 2 + 15 and r['tag'], f'etap „Temat” zamknięty: 4 × 2 XP + 15 XP (z mnożnikiem serii) ({r})')
    await pg.screenshot(path=f'{OUT}/e6_promotor_etapy.png')
    r = await pg.evaluate("""async () => { const inp = document.querySelector('#modal [data-add="lit"]'); inp.value = 'Przeczytać metaanalizę X'; inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
      await new Promise(r => setTimeout(r, 30)); const W = game.e6Pr().works.mgr; const open = !!document.querySelector('#modal details[data-st="lit"][open]');
      document.querySelector('#modal [data-skip="obr"]').click(); await new Promise(r => setTimeout(r, 30));
      return { custom: (W.custom.lit || []).length, open, skip: !!game.e6Pr().works.mgr.skip.obr, label: document.querySelector('#modal details[data-st="obr"] summary').textContent }; }""")
    check(r['custom'] == 1 and r['open'] and r['skip'] and 'nie dotyczy' in r['label'], f'własny punkt i „nie dotyczy” ({r})')
    # konsultacja
    await pg.evaluate("() => game.e6Promotor('kons')")
    sample = 'Wyniki pokazały, że grupa z treningiem uważności miała istotnie wyższe zaangażowanie estetyczne niż grupa kontrolna (p < 0,05). Oznacza to, że trening uważności zwiększa przeżycie estetyczne i dowodzi tego bardzo jasno.'
    r = await pg.evaluate("""async (t) => { document.querySelector('#modal [data-typ="wyn"]').click(); document.getElementById('e6-text').value = t; document.getElementById('e6-go').click();
      await new Promise(r => setTimeout(r, 120)); return { qs: [...document.querySelectorAll('#e6-out ol.e6-q li')].map(x => x.textContent), hist: game.e6Pr().cons.length, saved: JSON.stringify(game.e6Pr().cons).includes('dowodzi tego bardzo jasno') }; }""", sample)
    qs = ' | '.join(r['qs'])
    check(len(r['qs']) >= 3 and 'efekt' in qs and 'przedział' in qs.lower(), f'konsultacja wyników: pytania o wielkość efektu i przedziały ufności ({len(r["qs"])})')
    check('statystyką' in qs and 'dyskusji' in qs, 'pytanie o statystykę testu i o interpretację w wynikach')
    check(r['hist'] == 1 and not r['saved'], 'historia zapisuje pytania i początek fragmentu, ale nie cały tekst')
    await pg.screenshot(path=f'{OUT}/e6_promotor_konsultacja.png')
    r = await pg.evaluate("""() => { const g = game; const a = ETAP6.analiza;
      const w = a('Liczne badania pokazują, że uważność wpływa na dobrostan. Kowalski (2008) wykazał związek. Nowak (2009) to potwierdził. Zieliński (2010) również.', 'wstep', g);
      const h = a('Hipoteza 1: osoby po treningu uważności będą miały wyższe zaangażowanie estetyczne, mierzone kwestionariuszem AEQ.', 'hip', g);
      const m = a('W badaniu wzięło udział 60 studentów. Uzyskano zgodę komisji etycznej. Rzetelność skali wyniosła alfa = 0,87. Badanych losowo przydzielono do grup. Kryteria wyłączenia: wcześniejsza praktyka medytacji. Procedura: najpierw…', 'met', g);
      const d = a('Hipoteza 1 się potwierdziła, co jest zgodne z badaniami (Smith, 2020). Ograniczeniem jest mała próba. Możliwe, że wynik wynika z oczekiwań. Dalsze badania powinny… W praktyce warto…', 'dys', g);
      return { w: w.qs, h: h.qs, hp: h.plus, m: m.qs, mp: m.plus, d: d.qs, dp: d.plus }; }""")
    check(any('lista streszczeń' in q for q in r['w']) and any('luka' in q for q in r['w']), f'wstęp: lista streszczeń i luka w badaniach ({r["w"]})')
    check('Hipoteza ma kierunek.' in r['hp'] and 'Wiadomo, czym zmierzysz zmienne.' in r['hp'], f'hipoteza kierunkowa z operacjonalizacją ({r["hp"]})')
    check(len(r['mp']) >= 4 and not any('komisji' in q for q in r['m']), f'metoda: dobre elementy rozpoznane ({r["mp"]}, {r["m"]})')
    check(len(r['dp']) >= 2 and not any('ograniczenia' in q.lower() and 'Jakie są' in q for q in r['d']), f'dyskusja: ograniczenia i literatura rozpoznane ({r["dp"]}, {r["d"]})')
    # harmonogram
    await pg.evaluate("() => game.e6Promotor('plan')")
    r = await pg.evaluate("""async () => { const d = new Date(); d.setDate(d.getDate() + 200); const s = ETAP6.dates.ymd(d);
      const inp = document.getElementById('e6-due'); inp.value = s; inp.dispatchEvent(new Event('change')); document.getElementById('e6-auto').click();
      await new Promise(r => setTimeout(r, 60)); const W = game.e6Pr().works.mgr, st = ETAP6.WORKS.mgr.stages.filter(x => !W.skip[x.id]).map(x => W.dates[x.id]);
      return { due: s, dates: st, sorted: st.every((x, i) => i === 0 || x >= st[i - 1]), last: st[st.length - 1], rows: document.querySelectorAll('#modal .e6-pl').length }; }""")
    check(len(r['dates']) == 8 and all(r['dates']) and r['sorted'] and r['last'] <= r['due'], f'rozplanowanie wstecz: 8 terminów rosnąco, ostatni ≤ termin ({r["dates"]})')
    await pg.screenshot(path=f'{OUT}/e6_promotor_harmonogram.png')
    r = await pg.evaluate("""() => { document.getElementById('e6-ics').click(); const t = ETAP6.lastIcs || ''; return { ev: (t.match(/BEGIN:VEVENT/g) || []).length, ok: t.startsWith('BEGIN:VCALENDAR') && t.includes('DTSTART;VALUE=DATE:') && t.includes('\\r\\n') }; }""")
    check(r['ev'] == 8 and r['ok'], f'plik .ics: 8 wydarzeń całodniowych ({r})')
    r = await pg.evaluate("""() => { const P = game.e6Pr(), W = P.works.mgr; const d = new Date(); d.setDate(d.getDate() + 3); W.dates.lit = ETAP6.dates.ymd(d); P.remindDate = ''; const m = game.e6PromotorRemind(); const again = game.e6PromotorRemind(); return { m, again }; }""")
    check(r['m'] and 'za 3 dni' in r['m'] and r['again'] is None, f'przypomnienie: tydzień przed terminem, raz dziennie ({r["m"]})')
    r = await pg.evaluate("() => game.e6PromotorTalk(null) || new Promise(res => setTimeout(() => res(game.dialog.pages[0]), 60))")
    check(r and 'Najbliższy termin' in r and '%' in r, f'w rozmowie: postęp i najbliższy termin ({r[:90] if r else r})')
    r = await pg.evaluate("() => { game.closeDialog(true); const o = (ETAP4.extraObs || []).map(f => f(game)).flat().find(x => x.k === 'e6_praca'); return o && o.text; }")
    check(bool(r) and 'krok po kroku' in r, 'obserwacja w profilu: praca dyplomowa krok po kroku')

    print('\n[A5] List z nowościami')
    r = await pg.evaluate("() => { game.closeModal(true); game.closeDialog(true); game.e6Data().once = {}; game.openMail(); return document.getElementById('modal').innerText; }")
    check('Katedrę Psychologii Religii i Płci' in r and 'Przypis' in r, 'list od Burmistrza: katedra i promotor')
    check(not errs, f'bez błędów JavaScript ({errs[:3]})')
    await pg.close()

async def public(b):
    pg = await b.new_page(viewport={'width': 1100, 'height': 760})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: m.type in ('error', 'warning') and 'ETAP' in m.text and errs.append(m.text))
    await start_game(pg, PUB_URL)

    print('\n[P1] Wersja publiczna: tylko zagadnienia 🌍')
    r = await pg.evaluate("""() => ({ w: WERSJA, n: QUESTIONS_DB.length, bad: QUESTIONS_DB.filter(q => ETAP6.TIERS[q.id] !== 'B').map(q => q.id), key: SAVE_KEY, title: document.title,
      promotor: typeof NPCS.przypis, html: document.documentElement.outerHTML.includes('MMPI-2: Strategia Konstrukcji') })""")
    check(r['w'] == 'publiczna' and r['n'] == 67 and not r['bad'], f'WERSJA publiczna: 67 zagadnień, wszystkie 🌍 ({r["n"]}, {r["bad"][:5]})')
    check(r['key'] != 'akademia_freudowice_v1' and 'publiczna' in r['title'], f'osobny zapis i tytuł ({r["key"]}, {r["title"]})')
    check(r['promotor'] == 'undefined' and not r['html'], 'bez promotora i bez treści zagadnień 🔒 w pliku')

    print('\n[P2] Hol: sprawdzian zamiast zajęć')
    r = await pg.evaluate(HALL, 'testy')
    check(r and any(o.startswith('✅ Sprawdzian: zalicz zagadnienia (do zaliczenia: 5)') for o in r['opts']) and any('dla studentów Akademii [x]' in o for o in r['opts']) and not any(o.startswith('📝 Zajęcia') for o in r['opts']),
          f'hol Poligonu: sprawdzian (5), zajęcia zamknięte ({r and r["opts"]})')
    await pg.wait_for_timeout(900)
    await pg.screenshot(path=f'{OUT}/e6_pub_hol.png')
    await pg.evaluate(PICK, '✅')
    await pg.wait_for_timeout(200)
    await pg.screenshot(path=f'{OUT}/e6_pub_sprawdzian.png')
    r = await pg.evaluate("""async () => { const xp0 = game.state.stats.xp; let n = 0;
      for (let k = 0; k < 6; k++) { const B = game.currentBlock; if (!B) break; const q = B.questions[B.index];
        const btn = document.querySelector(`#modal .quiz-opt[data-id="${q.id}"]`); if (!btn) break; btn.click(); n++;
        await new Promise(r => setTimeout(r, 20)); document.getElementById('e6-next').click(); await new Promise(r => setTimeout(r, 20)); }
      return { n, ans: QUESTIONS_DB.filter(q => q.locId === 'testy' && game.state.stats.answeredQuestions[q.id]).length, dxp: game.state.stats.xp - xp0, sum: document.getElementById('modal').innerText, left: ETAP6.pendingFor(game, 'testy').length }; }""")
    check(r['n'] == 5 and r['ans'] == 5 and r['left'] == 0, f'sprawdzian: 5 dobrych odpowiedzi zalicza 5 zagadnień ({r["n"]}, {r["ans"]})')
    check(r['dxp'] > 0 and '5 / 5' in r['sum'], f'podsumowanie i XP ({r["dxp"]})')
    await pg.screenshot(path=f'{OUT}/e6_pub_sprawdzian_wynik.png')
    r = await pg.evaluate("() => ({ b: !!game.state.stats.badges.psychometra, d: ALL_BADGES.find(x => x.id === 'psychometra').desc })")
    check(not r['b'] and 'Poligonie' in r['d'], f'odznaka Psychometry: opis dla wersji publicznej ({r["d"]})')
    r = await pg.evaluate("""() => { game.closeModal(true); QUESTIONS_DB.filter(q => q.locId === 'dziecko').slice(0, 2).forEach(q => game.markCorrect(q, 1)); game.checkBadges(); return !!game.state.stats.badges.psychometra; }""")
    check(r, 'odznaka Psychometry za zagadnienia 🌍 Poligonu i Pracowni Dziecka')
    r = await pg.evaluate(HALL, 'religia')
    check(r and any(o.startswith('✅ Sprawdzian') for o in r['opts']) and r['opts'][0].startswith('📖 Kompendium wiedzy (0/14)'), f'Katedra Religii i Płci w wersji publicznej: 14 zagadnień 🌍 ({r and r["opts"][0]})')
    await pg.evaluate(CLEAN)
    r = await pg.evaluate("""async () => { game.setZone('blonia'); await new Promise(r => setTimeout(r, 100)); const n = game.npcs.find(x => x.id === 'psychometrzyk'); game.talkTo(n); await new Promise(r => setTimeout(r, 60));
      return game.dialog.options.map(o => o.label + (o.disabled ? ' [x]' : '')); }""")
    check(any(o.startswith('🏅 Wszystkie zagadnienia zaliczone') for o in r) and not any('zajęcia' in o for o in r), f'mistrz: bez wejścia na zajęcia ({r})')
    r = await pg.evaluate("() => { game.closeDialog(true); const b = game.zone.buildings.find(x => x.loc === 'testy'); game.enterBuilding(b); return { scene: game.scene, t: game.dialog ? game.dialog.pages[0] : (document.querySelector('#modal .panel-head h2') || {}).textContent }; }")
    check(r['scene'] == 'world', f'enterBuilding nie otwiera sali z pytaniami otwartymi ({r})')

    print('\n[P3] Profil, Brygadzista, mentorka')
    r = await pg.evaluate("""() => { game.closeDialog(true); game.closeModal(true); game.openProfile('diagnosta'); const tabs = [...document.querySelectorAll('#modal [data-prtab]')].map(x => x.dataset.prtab);
      const acad = game.prAcadVisible(), cas = game.prCaseUnlocked(); game.closeModal(true); return { tabs, acad, cas, know: ETAP4.EXP.map(e => e.know), goal: ETAP5.GOALS.topics.text(3) }; }""")
    check('diagnosta' not in r['tabs'] and not r['acad'] and not r['cas'], f'profil bez 📊 Profilu diagnosty i bez drogi diagnosty ({r["tabs"]})')
    check(r['know'] == [20, 40] and 'sprawdzianach' in r['goal'], f'progi Brygadzisty 20/40 i cel mentorki ({r["know"]}, {r["goal"]})')
    r = await pg.evaluate("() => { game.closeModal(true); game.closeDialog(true); game.e6Data().once = {}; game.openMail(); return document.getElementById('modal').innerText; }")
    check('Sprawdzian' in r and 'Przypis' not in r, 'list od Burmistrza w wersji publicznej')
    await pg.evaluate("() => { game.closeModal(true); game.save(true); }")
    r = await pg.evaluate("() => [!!localStorage.getItem('akademia_freudowice_publiczna_v1'), !!localStorage.getItem('akademia_freudowice_v1')]")
    check(r == [True, False], f'zapis wersji publicznej pod osobnym kluczem ({r})')
    check(not errs, f'bez błędów JavaScript ({errs[:3]})')
    await pg.close()

    print('\n[P4] Telefon')
    pg = await b.new_page(viewport={'width': 390, 'height': 844})
    await start_game(pg, URL)
    await pg.evaluate("() => { game.e6Promotor('kons'); }")
    r = await pg.evaluate("() => { const m = document.querySelector('#modal .panel'); return m.scrollWidth <= m.clientWidth + 2; }")
    check(r, 'panel promotora mieści się na ekranie telefonu')
    await pg.screenshot(path=f'{OUT}/e6_tel_promotor.png')
    await pg.evaluate("() => { game.e6Promotor('plan'); }")
    r = await pg.evaluate("() => { const m = document.querySelector('#modal .panel'); return m.scrollWidth <= m.clientWidth + 2; }")
    check(r, 'harmonogram mieści się na ekranie telefonu')
    await pg.screenshot(path=f'{OUT}/e6_tel_harmonogram.png')
    await pg.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await academic(b)
        await public(b)
        await b.close()
    print('\nWYNIK:', 'OK' if not fails else f'{len(fails)} błędów')
    for f in fails:
        print(' -', f)
    sys.exit(1 if fails else 0)

asyncio.run(main())
