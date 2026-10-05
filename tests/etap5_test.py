"""Test Etapu 5 (część, 2026-10-05): hol katedry, Kompendium wiedzy, mini gry w każdej katedrze, mentorka, Wyspa Snu.

Uruchomienie (w folderze repo):
    python3 -m http.server 8765 --directory "Akademia diagnosty" &
    python3 tests/etap5_test.py            # zrzuty ekranu trafiają do tests/out/

Test działa w czystym profilu przeglądarki, więc nie dotyka prawdziwego zapisu.
Mini gry są rozgrywane klikaniem (Memory, Błyskawica, „Który opis pasuje?”).
"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright

URL = os.environ.get('GAME_URL', 'http://localhost:8765/akademia_diagnosty_miasteczko.html')
OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)
fails = []

def check(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)

HALL = """async (loc) => {
  game.closeModal(true); game.closeDialog(true);
  const zone = LOCATIONS[loc].zone; if (game.zone.id !== zone) game.setZone(zone);
  const b = game.zone.buildings.find(x => x.loc === loc);
  game.player.x = b.doorCol * 16 + 8; game.player.y = b.doorRow * 16 + 8; game.player.dir = 'up';
  game.enterDoor(b);
  await new Promise(r => setTimeout(r, 80));
  return game.dialog ? { name: game.dialog.name, pages: game.dialog.pages, opts: game.dialog.options.map(o => o.label), py: game.player.y, below: (b.doorRow + 1) * 16 + 8 } : null;
}"""
PICK = """(prefix) => { const o = game.dialog.options.find(x => x.label.startsWith(prefix)); game.closeDialog(true); if (o && o.fn) o.fn(); return !!o; }"""
PLAY_PAIRS = """async () => {
  const R = SUBJECTS[game._mg.sid].rooms[0], cards = [...document.querySelectorAll('#modal .mg-card')];
  for (const [a, b] of R.pairs) {
    const ca = cards.find(c => c.querySelector('b') && c.textContent.trim() === a), cb = cards.find(c => !c.querySelector('b') && c.textContent.trim() === b);
    ca.click(); cb.click(); await new Promise(r => setTimeout(r, 30));
  }
  await new Promise(r => setTimeout(r, 900));
}"""
PLAY_TF = """async () => {
  const R = SUBJECTS[game._mg.sid].rooms[1];
  for (let k = 0; k < 12; k++) {
    const q = document.querySelector('#modal #mg-q'); if (!q) break;
    const it = R.items.find(x => x[0] === q.textContent); if (!it) break;
    document.getElementById(it[1] ? 'mg-t' : 'mg-f').click();
    await new Promise(r => setTimeout(r, 20));
  }
}"""
PLAY_QUIZ = """async () => {
  for (let k = 0; k < 8; k++) {
    const good = document.querySelector('#modal .mg-opt[data-k="0"]'); if (!good) break;
    good.click(); const nx = document.getElementById('mg-next'); if (nx) nx.click();
    await new Promise(r => setTimeout(r, 20));
  }
}"""

async def start_game(pg):
    await pg.goto(URL)
    await pg.wait_for_timeout(1500)
    await pg.fill("input[placeholder*='Sylwia']", 'Testerka')
    await pg.click('text=Zamieszkaj w Freudowice Zdrój')
    await pg.wait_for_timeout(1500)
    for _ in range(8):
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1100, 'height': 760})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type in ('error', 'warning') and 'ETAP5' in m.text and errs.append(m.text))
        await start_game(pg)
        check(await pg.evaluate('() => !!window.ETAP5 && Object.keys(LOCATIONS).every(l => SUBJECTS["e5_" + l] && SUBJECTS["e5_" + l].rooms.length >= 3)'), 'moduł ETAP5: co najmniej 3 mini gry w każdej z katedr (Etap 6: Katedra Religii i Płci ma 4)')

        # ---------- 1. hol katedry ----------
        print('\n[1] Hol katedry')
        r = await pg.evaluate(HALL, 'eba')
        check(r and r['opts'][0].startswith('📖 Kompendium') and r['opts'][1].startswith('🎲 Mini gry') and r['opts'][2].startswith('📝 Zajęcia') and r['opts'][-1] == '🚪 Wyjdź', f'drzwi katedry otwierają hol z wyborem ({r and r["opts"]})')
        check(r and r['py'] == r['below'], 'postać odsuwa się spod drzwi (nie wchodzi drugi raz)')
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path=f'{OUT}/e5_hol.png')
        r = await pg.evaluate(HALL, 'eba')
        check(r and 'Dokąd idziemy' in r['pages'][0], 'przy kolejnej wizycie krótsze powitanie')

        # ---------- 2. kompendium ----------
        print('\n[2] Kompendium')
        await pg.evaluate(PICK, '📖')
        r = await pg.evaluate("() => ({ title: document.querySelector('#modal .panel-head h2').textContent, n: document.querySelectorAll('#modal details.e5-k').length, total: QUESTIONS_DB.filter(q => q.locId === 'eba').length })")
        check(r['title'].startswith('📖 Kompendium') and r['n'] == r['total'] and r['n'] >= 10, f'kompendium: wszystkie zagadnienia katedry ({r["n"]}/{r["total"]})')
        await pg.screenshot(path=f'{OUT}/e5_kompendium.png')
        r = await pg.evaluate("""() => { const inp = document.getElementById('e5-k-q'); inp.value = 'DAUBERT'; inp.dispatchEvent(new Event('input'));
          const vis = [...document.querySelectorAll('#modal details.e5-k')].filter(x => !x.hidden); inp.value = 'zzzqqq'; inp.dispatchEvent(new Event('input'));
          const none = !document.getElementById('e5-k-none').hidden; inp.value = ''; inp.dispatchEvent(new Event('input'));
          return { n: vis.length, topic: vis[0] && vis[0].querySelector('summary b').textContent, none }; }""")
        check(r['n'] == 1 and 'Dauberta' in r['topic'] and r['none'], f'wyszukiwarka (bez wielkości liter) i komunikat „nic nie pasuje” ({r})')
        r = await pg.evaluate("""async () => { const c0 = (game.profData().obs || {}).ciekawosc || 0, xp0 = game.state.stats.xp;
          const ds = [...document.querySelectorAll('#modal details.e5-k')];
          for (const d of ds) { d.open = true; await new Promise(r => setTimeout(r, 5)); }
          await new Promise(r => setTimeout(r, 100));
          return { read: Object.keys(game.e5Data().read).length, n: ds.length, cur: ((game.profData().obs || {}).ciekawosc || 0) - c0, dxp: game.state.stats.xp - xp0, once: !!game.e5Data().once.kompendium_eba }; }""")
        check(r['read'] == r['n'] and r['cur'] == r['n'], f'czytanie liczy się do „ciekawości” w profilu ({r["cur"]})')
        check(r['once'] and r['dxp'] >= 10, f'całe kompendium przeczytane: +10 XP raz ({r["dxp"]})')
        await pg.screenshot(path=f'{OUT}/e5_kompendium_otwarte.png')

        # ---------- 3. mini gry ----------
        print('\n[3] Mini gry')
        await pg.evaluate("() => { document.getElementById('e5-k-mg').click(); }")
        r = await pg.evaluate("() => [...document.querySelectorAll('#modal .e5-mg b')].map(x => x.textContent)")
        check(len(r) == 3, f'lista mini gier ({r})')
        await pg.screenshot(path=f'{OUT}/e5_minigry.png')
        res = {}
        for i, js in [(0, PLAY_PAIRS), (1, PLAY_TF), (2, PLAY_QUIZ)]:
            st0 = await pg.evaluate("() => ({ xp: game.state.stats.xp, money: game.state.money, energy: game.state.energy })")
            await pg.evaluate(f"() => document.querySelector('[data-play=\"{i}\"]').click()")
            await pg.wait_for_timeout(300)
            if i == 1:
                await pg.screenshot(path=f'{OUT}/e5_blyskawica.png')
            await pg.evaluate(js)
            await pg.wait_for_timeout(400)
            r = await pg.evaluate("""() => ({ title: document.querySelector('#modal .panel-head h2').textContent, txt: document.getElementById('modal').innerText, xp: game.state.stats.xp, money: game.state.money, energy: game.state.energy })""")
            res[i] = r
            check('wynik' in r['title'] and 'Wynik: 100%' in r['txt'], f'mini gra {i + 1} rozegrana bezbłędnie ({r["title"]})')
            check(st0['energy'] - r['energy'] == 4, f'mini gra {i + 1} kosztuje 4 ⚡')
            check(0 < r['xp'] - st0['xp'] <= 50, f'mini gra {i + 1}: nagroda zmniejszona ({r["xp"] - st0["xp"]} XP, {r["money"] - st0["money"]} 🟡)')
            if i == 0:
                await pg.screenshot(path=f'{OUT}/e5_wynik.png')
            await pg.evaluate("() => [...document.querySelectorAll('#modal .panel-foot .btn')].find(x => x.textContent.includes('Wróć do mini gier')).click()")
        check('Wszystkie mini gry zaliczone' in res[2]['txt'], 'komplet trzech gier: premia katedry')
        r = await pg.evaluate("() => [0, 1, 2].map(i => game.roomStars('e5_eba', i))")
        check(r == [3, 3, 3], f'gwiazdki zapisane ({r})')
        r = await pg.evaluate("""() => { const a = JSON.stringify(SUBJECTS.e5_eba.rooms[2].items); game.closeModal(true); game.state.energy = 100; game.startMinigame('e5_eba', 2);
          const b2 = JSON.stringify(SUBJECTS.e5_eba.rooms[2].items); game.closeModal(true); game._mg && game.mgStop(game._mg); return [a.length > 10, a !== b2]; }""")
        check(r[0] and r[1], 'każda gra losuje nowe pytania')
        r = await pg.evaluate("() => { const S = SUBJECTS.e5_eba; return S.rooms[2].items.every(it => it.a.length === 4 && new Set(it.a).size === 4) && S.rooms[1].items.length === 10 && S.rooms[0].pairs.length === 6; }")
        check(r, 'quiz: 4 różne opisy; błyskawica: 10 zdań; memory: 6 par')

        # ---------- 4. mistrz, Archiwum, zajęcia ----------
        print('\n[4] Mistrz, Archiwum, zajęcia')
        r = await pg.evaluate("""async () => { game.closeModal(true); game.closeDialog(true); const n = game.npcs.find(x => x.def && x.def.master === 'eba');
          const rr = Math.random; Math.random = () => 0.99; try { game.talkTo(n); } finally { Math.random = rr; }
          await new Promise(r => setTimeout(r, 300)); return game.dialog ? game.dialog.options.map(o => o.label) : null; }""")
        check(r and '📖 Kompendium wiedzy' in r and '🎲 Mini gry' in r and '📖 Czego tu się uczy?' not in r and r[-1].startswith('👋'), f'mistrz katedry: kompendium i mini gry ({r})')
        r = await pg.evaluate("() => { const o = game.dialog.options.find(x => x.label === '📖 Kompendium wiedzy'); game.closeDialog(true); o.fn(); return document.querySelector('#modal .panel-head h2').textContent; }")
        check(r.startswith('📖 Kompendium'), '„Czego tu się uczy?” prowadzi do kompendium')
        r = await pg.evaluate(HALL, 'archiwum')
        check(r and any(o.startswith('🕯️ Wystawa') for o in r['opts']), f'Archiwum: w holu także Wystawa ({r and r["opts"]})')
        await pg.evaluate("() => { game.state.energy = 100; }")
        await pg.evaluate(PICK, '📝')
        await pg.wait_for_timeout(1300)
        r = await pg.evaluate("() => ({ scene: game.scene, modal: game.modalOpen && document.querySelector('#modal .panel-head h2').textContent })")
        check(r['scene'] == 'interior' and r['modal'] and 'poziom' in r['modal'], f'„Zajęcia” wchodzą na pytania otwarte jak dawniej ({r})')
        await pg.evaluate("() => game.leaveInterior()")
        await pg.wait_for_timeout(600)
        r = await pg.evaluate("() => { game.save(); const s = JSON.parse(localStorage.getItem('akademia_freudowice_v1')); return !!(s.e5 && s.e5.read && s.subj && s.subj.e5_eba); }")
        check(r, 'stan ETAP5 i gwiazdki są w pliku zapisu')

        # ---------- 5. mentorka ----------
        print('\n[5] Mentorka')
        TALKM = """async () => { game.closeModal(true); game.closeDialog(true); if (game.zone.id !== 'rynek') game.setZone('rynek');
          const n = game.npcs.find(x => x.id === 'busola'); if (!n) return null; game.player.x = n.x + 16; game.player.y = n.y;
          const rr = Math.random; Math.random = () => 0.99; try { game.talkTo(n); } finally { Math.random = rr; }
          await new Promise(r => setTimeout(r, 60)); return game.dialog ? { pages: game.dialog.pages, opts: game.dialog.options.map(o => o.label) } : null; }"""
        await pg.evaluate("() => { game.state.time = 11 * 60; }")
        r = await pg.evaluate(TALKM)
        check(r and 'mentorka' in r['pages'][0] and r['opts'][0] == '🧭 Spotkanie mentorskie', f'Dr Busola na Rynku zaprasza na spotkanie ({r and r["opts"]})')
        await pg.evaluate("() => { const o = game.dialog.options[0]; game.closeDialog(true); o.fn(); document.getElementById('e5-ms-next').click(); }")
        r = await pg.evaluate("() => [...document.querySelectorAll('#e5-ms [data-g]')].map(b => b.dataset.g)")
        check(len(r) == 3, f'trzy propozycje celu ({r})')
        await pg.evaluate("() => { const g = document.querySelector('#e5-ms [data-g=\"talks\"]') || document.querySelector('#e5-ms [data-g]'); g.click(); document.querySelector('#e5-ms [data-c=\"rynek\"]').click(); }")
        r = await pg.evaluate("() => document.querySelector('#e5-ms .fb.ok').innerText")
        check(r.startswith('📌 Plan: Jeśli zobaczę ławkę na Rynku, to '), f'plan „jeśli–to” ({r[:80]})')
        await pg.screenshot(path=f'{OUT}/e5_mentorka_cel.png')
        r = await pg.evaluate("() => { document.getElementById('e5-ms-save').click(); const M = game.e5Mentor(); return { goal: M.goal, last: M.last, n: M.n }; }")
        check(r['goal'] and r['goal']['cue'] == 'rynek' and r['n'] == 1, f'cel zapisany ({r["goal"]})')
        r = await pg.evaluate(TALKM)
        check(r and '🧭 Spotkanie mentorskie' not in r['opts'] and 'Następne spotkanie' in r['pages'][0], 'spotkanie raz w tygodniu; między spotkaniami postęp celu')
        r = await pg.evaluate("() => { game.closeDialog(true); game.showJournal('quests'); const c = document.querySelector('#modal .e5-jgoal'); const t = c && c.innerText; game.closeModal(true); return t; }")
        check(r and 'Cel tygodnia' in r and 'Jeśli zobaczę ławkę na Rynku' in r, 'cel tygodnia widać też w „Zadaniach dnia”')
        r = await pg.evaluate("""async () => { game.closeDialog(true); game.setZone('bulwar'); game.setZone('rynek'); await new Promise(r => setTimeout(r, 1200));
          const t1 = document.getElementById('toast').textContent; const M = game.e5Mentor(); return [t1, M.remind === game.state.day]; }""")
        check(r[0].startswith('📌 Twój plan: Jeśli zobaczę ławkę na Rynku') and r[1], f'przypomnienie dokładnie w chwili z planu ({r[0][:60]})')
        r = await pg.evaluate("""async () => { const G = game.e5Mentor().goal, k = ETAP5.GOALS[G.t].k, c = ETAP5.counters(game);
          if (k === 'talks') game.state.talked.test_m = 50; else if (k === 'stars' || k === 'topics' || k === 'read') { G.base = -99; }
          game.setZone('bulwar'); await new Promise(r => setTimeout(r, 1000)); return [document.getElementById('toast').textContent, game.e5Mentor().goal.ok]; }""")
        check('Cel tygodnia osiągnięty' in r[0] and r[1], f'osiągnięty cel: komunikat ({r[0][:50]})')
        r = await pg.evaluate("""async () => { game.state.day += 7; const xp0 = game.state.stats.xp, m0 = game.state.money; game.e5MentorSession();
          const rev = document.getElementById('e5-ms').innerText; document.getElementById('e5-ms-next').click(); const prev = document.getElementById('e5-ms').innerText;
          document.getElementById('e5-ms-next').click(); const big = [...document.querySelectorAll('#e5-ms [data-g]')].map(b => b.innerText);
          return { rev, prev, dxp: game.state.stats.xp - xp0, dm: game.state.money - m0, big }; }""")
        check('Od ostatniego spotkania minęło 7 dni' in r['rev'] and 'Udało się' in r['prev'] and r['dxp'] >= 20 and r['dm'] >= 10, f'tydzień później: podsumowanie i nagroda za cel (+{r["dxp"]} XP, +{r["dm"]} 🟡)')
        await pg.evaluate("() => { document.querySelector('#e5-ms [data-g]').click(); document.querySelector('#e5-ms [data-c=\"kawa\"]').click(); document.getElementById('e5-ms-save').click(); }")
        r = await pg.evaluate("""() => { game.closeModal(true); game.state.day += 7; game.e5MentorSession(); document.getElementById('e5-ms-next').click();
          const a = document.getElementById('e5-ms').innerText; document.querySelector('#e5-ms [data-r=\"czas\"]').click();
          const fb = document.querySelector('#e5-ms .fb.ai').innerText; document.getElementById('e5-ms-next').click();
          const small = document.getElementById('e5-ms').innerText.includes('mniejszy krok');
          return { a, fb, small, hist: game.e5Mentor().hist.map(h => h.ok + ':' + (h.why || '')) }; }""")
        check('Co przeszkodziło' in r['a'] and 'mniejszy' in r['fb'] and r['small'] and r['hist'] == ['1:', '0:czas'], f'nieudany tydzień: rozmowa o przeszkodach, potem mniejszy krok ({r["hist"]})')
        await pg.screenshot(path=f'{OUT}/e5_mentorka_przeszkody.png')
        r = await pg.evaluate("() => { game.closeModal(true); const t = [game.e5MentorTip(), game.e5MentorTip()]; const o = game.prObservations().find(x => x.k === 'e5_plany'); return [t, o && o.text]; }")
        check(all(r[0]) and r[1], f'szybka rada i obserwacja „Planowanie” w profilu ({r[1] and r[1][:50]})')

        # ---------- 6. Wyspa Snu ----------
        print('\n[6] Wyspa Snu')
        r = await pg.evaluate("""() => { game.closeModal(true); game.closeDialog(true); game.setZone('wyspa_snu');
          const it = game.zone.interacts.find(i => i.kind === 'e5_higiena'); return { it: !!it, prompt: it && game.spotPrompt(it), npcs: game.npcs.map(n => n.id) }; }""")
        check(r['it'] and r['prompt'] == 'Tablica Higieny Snu' and 'sennik' in r['npcs'] and 'kot_drzemka' in r['npcs'], f'Wyspa Snu: tablica, Pan Sennik i Kot Drzemka ({r["npcs"]})')
        r = await pg.evaluate("""() => { const np = game.npData(); const d = game.state.day; np.log = [{ d: d - 3, bed: 23 * 60 }, { d: d - 2, bed: 23 * 60 + 40 }, { d: d - 1, bed: 22 * 60 + 50 }];
          game.e5Higiena(); return { n: document.querySelectorAll('#modal .e5-rada').length, streak: game.e5Rytm().streak, btn: !!document.getElementById('e5-rytm') }; }""")
        check(r['n'] == 8 and r['streak'] == 3 and r['btn'], f'tablica: 8 rad i wyzwanie „regularny rytm” zaliczone ({r})')
        await pg.screenshot(path=f'{OUT}/e5_tablica_snu.png')
        r = await pg.evaluate("""() => { const xp0 = game.state.stats.xp, lp0 = game.dreamData().lp; document.getElementById('e5-rytm').click();
          return { dxp: game.state.stats.xp - xp0, dlp: game.dreamData().lp - lp0, again: !!document.getElementById('e5-rytm') }; }""")
        check(r['dxp'] >= 10 and r['dlp'] == 5 and not r['again'], f'nagroda za rytm raz w tygodniu (+{r["dxp"]} XP, +{r["dlp"]} LP)')
        r = await pg.evaluate("() => { const np = game.npData(); np.log = [{ d: 1, bed: 22 * 60 }, { d: 2, bed: 25 * 60 }, { d: 3, bed: 23 * 60 }]; const a = game.e5Rytm().streak; np.log = [{ d: 1, bed: 23 * 60 }, { d: 3, bed: 23 * 60 }]; return [a, game.e5Rytm().streak]; }")
        check(r == [1, 1], f'rytm: rozrzut ponad godzinę albo przerwa w nocach przerywa serię ({r})')
        await pg.evaluate("() => { game.closeModal(true); game.state.energy = 100; game.e5Higiena(); document.getElementById('e5-mity').click(); }")
        await pg.wait_for_timeout(250)
        await pg.evaluate("""async () => { const R = SUBJECTS.e5_sen.rooms[0]; for (let k = 0; k < 10; k++) { const q = document.querySelector('#modal #mg-q'); if (!q) break;
          const it = R.items.find(x => x[0] === q.textContent); if (!it) break; document.getElementById(it[1] ? 'mg-t' : 'mg-f').click(); await new Promise(r => setTimeout(r, 20)); } }""")
        await pg.wait_for_timeout(400)
        r = await pg.evaluate("() => ({ txt: document.getElementById('modal').innerText, back: [...document.querySelectorAll('#modal .panel-foot .btn')].map(b => b.textContent) })")
        check('Wynik: 100%' in r['txt'] and '🌙 Wróć do tablicy' in r['back'], 'quiz „Sen: mit czy fakt?” i powrót do tablicy')
        r = await pg.evaluate("""async () => { game.closeModal(true); const n = game.npcs.find(x => x.id === 'sennik'); const rr = Math.random; Math.random = () => 0.99;
          try { game.talkTo(n); } finally { Math.random = rr; } await new Promise(r => setTimeout(r, 60)); const opts = game.dialog.options.map(o => o.label);
          const m0 = game.state.money; const o = game.dialog.options[1]; game.closeDialog(true); o.fn();
          return { opts, dm: game.state.money - m0, txt: document.getElementById('modal').innerText }; }""")
        check(len(r['opts']) == 5 and r['dm'] == -2 and 'efekt Barnuma' in r['txt'] and 'Co mówią badania' in r['txt'], 'Pan Sennik: „wróżba” za 2 🟡, potem badania i efekt Barnuma')
        await pg.screenshot(path=f'{OUT}/e5_sennik.png')

        # ---------- 6b. list z nowościami ----------
        r = await pg.evaluate("""() => { game.closeModal(true); game.closeDialog(true); delete game.e5Data().once['nowosci-2026-10-05'];
          if (game.e6Data) game.e6Data().once['nowosci-2026-10-05-e6'] = 1;   // list Etapu 6 sprawdza tests/etap6_test.py
          game.openMail(); const a = document.querySelector('#modal .panel-head h2').textContent; game.closeModal(true);
          game.state.mailDay = 0; game.openMail(); const b2 = document.querySelector('#modal .panel-head h2').textContent; game.closeModal(true); return [a, b2]; }""")
        check('nowości' in r[0] and 'nowości' not in r[1], f'list z nowościami raz, potem zwykłe listy ({r})')

        # ---------- 7. telefon ----------
        print('\n[7] Telefon')
        mob = await b.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        merrs = []
        mob.on('pageerror', lambda e: merrs.append(str(e)))
        await start_game(mob)
        for name, js in [('kompendium', "game.e5Kompendium('neuro')"), ('minigry', "game.e5MiniGry('neuro')"), ('mentorka', "game.e5MentorSession()"), ('tablica_snu', "game.e5Higiena()"), ('quiz', "(game.state.energy = 100, game.startMinigame('e5_neuro', 2))"), ('memory', "(game.state.energy = 100, game.startMinigame('e5_neuro', 0))")]:
            await mob.evaluate(f"() => {{ game.closeModal(true); if (game._mg) game.mgStop(game._mg); {js}; }}")
            await mob.wait_for_timeout(350)
            over = await mob.evaluate("() => { const p = document.querySelector('#modal .panel'); return p ? p.scrollWidth > p.clientWidth + 2 || p.getBoundingClientRect().right > innerWidth + 1 : 'brak'; }")
            check(over is False, f'telefon: okno „{name}” mieści się na szerokość')
            await mob.screenshot(path=f'{OUT}/e5_tel_{name}.png')
        check(not merrs, f'telefon: brak błędów ({merrs[:3]})')
        check(not errs, f'brak błędów JS ({errs[:5]})')
        await b.close()
    print('\nWYNIK:', 'OK' if not fails else f'{len(fails)} błędów')
    for f in fails:
        print('  -', f)
    sys.exit(1 if fails else 0)

asyncio.run(main())
