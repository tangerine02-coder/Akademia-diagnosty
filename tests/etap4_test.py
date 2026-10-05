"""Test Etapu 4 (2026-10-05): ogródek i straganik, Poletko Doświadczalne, rozbudowa domu, osobowość z wyborów.

Uruchomienie (w folderze repo):
    python3 -m http.server 8765 --directory "Akademia diagnosty" &
    python3 tests/etap4_test.py            # zrzuty ekranu trafiają do tests/out/

Test działa w czystym profilu przeglądarki, więc nie dotyka prawdziwego zapisu.
Upływ dni symuluje zwiększanie state.day i game.e4Tick().
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

SPOT = """(kind) => {
  game.closeModal(true); game.closeDialog(true);
  const it = game.zone.interacts.find(x => x.kind === kind);
  if (!it) return { err: 'brak ' + kind + ' w ' + game.zone.id };
  game.useSpot(it);
  const m = document.getElementById('modal');
  return { prompt: game.spotPrompt(it), modal: game.modalOpen ? m.querySelector('.panel-head h2').textContent : null };
}"""
DAY = "() => { game.state.day += 1; game.e4Tick(); }"
FITS = "() => { const p = document.querySelector('#modal .panel'); return p ? p.scrollWidth > p.clientWidth + 2 || p.getBoundingClientRect().right > innerWidth + 1 : 'brak'; }"

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
        ctx = await b.new_context(viewport={'width': 1100, 'height': 760})
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type in ('error', 'warning') and 'ETAP4' in m.text and errs.append(m.text))
        await start_game(pg)
        check(await pg.evaluate('() => !!window.ETAP4'), 'moduł ETAP4 załadowany')

        # ---------- 1. ogródek i straganik ----------
        print('\n[1] Ogródek i straganik')
        await pg.evaluate("() => { game.closeModal(true); game.closeDialog(true); game.state.money = 300; game.setZone('osiedle'); game.player.x = 11*16+8; game.player.y = 10*16; game.state.time = 12*60; }")
        r = await pg.evaluate(SPOT, 'e4_ogrod')
        check(r.get('modal') == '🌱 Ogródek przy domu', f'grządki otwierają ogródek ({r})')
        check(r.get('prompt') == 'Ogródek: grządki', 'podpowiedź przy grządkach')
        r = await pg.evaluate("""() => { document.querySelector('.e4-seed[data-c="salata"]').click(); document.getElementById('e4-plant-all').click();
          document.getElementById('e4-water').click();
          return { planted: game.e4Data().beds.filter(Boolean).length, wet: game.zone.objects.filter(o => o.type === 'e4_crop' && o.wet).length, money: game.state.money }; }""")
        check(r['planted'] == 12 and r['wet'] == 12 and r['money'] == 300 - 36, f'12 grządek sałaty posadzonych i podlanych za 36 🟡 ({r})')
        await pg.screenshot(path=f'{OUT}/e4_ogrodek.png')
        # bez podlewania roślina nie rośnie
        await pg.evaluate(DAY)
        g1 = await pg.evaluate("() => game.e4Data().beds[0].g")
        await pg.evaluate(DAY)
        g2 = await pg.evaluate("() => game.e4Data().beds[0].g")
        check(g1 == 1 and g2 == 1, f'rośnie tylko w podlane dni ({g1}, {g2})')
        for _ in range(2):
            await pg.evaluate("() => { const d = game.e4Data(); d.beds.forEach(b => { if (b && !b.ripe) b.w = game.state.day; }); game.state.day += 1; game.e4Tick(); }")
        r = await pg.evaluate("() => { game.e4PlaceGarden(); return game.e4Data().beds.filter(b => b && b.ripe).length; }")
        check(r == 12, f'po 3 podlanych dniach sałata dojrzała ({r})')
        await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'{OUT}/e4_ogrodek_dojrzaly.png')
        r = await pg.evaluate("""(SPOT) => { const f = eval(SPOT); f('e4_ogrod'); document.getElementById('e4-harvest').click();
          return { kosz: game.e4Data().kosz, beds: game.e4Data().beds.filter(Boolean).length }; }""", SPOT)
        check(r['kosz'].get('salata') == 12 and r['beds'] == 0, f'zbiory trafiają do koszyka ({r})')
        r = await pg.evaluate(SPOT, 'e4_stragan')
        check(r.get('modal') == '🧺 Straganik pod płotem', f'straganik się otwiera ({r})')
        m0 = await pg.evaluate("() => game.state.money")
        await pg.click('#e4-sell-all')
        r = await pg.evaluate("() => ({ money: game.state.money, kosz: game.e4Data().kosz.salata, st: game.e4Data().stats })")
        check(r['money'] > m0 and not r['kosz'] and r['st'].get('sold') == 12, f'sprzedaż wszystkiego ({m0} → {r["money"]})')
        await pg.screenshot(path=f'{OUT}/e4_straganik.png')
        r = await pg.evaluate("() => { const d = game.e4Data(); d.beds[0] = { c: 'pomidor', g: 0, p: game.state.day, w: game.state.day }; game.e2Data().seasonOverride = 'zima'; game.state.day += 1; game.e4Tick(); const g = d.beds[0].g; game.e2Data().seasonOverride = null; d.beds[0] = null; return g; }")
        check(r == 0, f'poza swoją porą roku roślina nie rośnie ({r})')

        # ---------- 2. Poletko Doświadczalne ----------
        print('\n[2] Poletko Doświadczalne')
        await pg.evaluate("() => { game.closeModal(true); game.setZone('wzgorze'); game.player.x = 22*16+8; game.player.y = 22*16+8; game.state.money = 300; }")
        r = await pg.evaluate("() => ({ npc: game.npcs.some(n => n.id === 'losowska'), solidPlot: game.zone.solid[20*game.zone.w+25], gate: game.zone.solid[22*game.zone.w+24] })")
        check(r['npc'] and r['solidPlot'] == 0 and r['gate'] == 0, f'poletko: Pani Losowska, wejście i ścieżka ({r})')
        r = await pg.evaluate(SPOT, 'e4_pole')
        check(r.get('modal') == '🧪 Poletko Doświadczalne', f'poletko się otwiera ({r})')
        crop = await pg.evaluate("() => document.querySelector('.e4-seed[data-c]:not(.off)').dataset.c")
        await pg.click(f'.e4-seed[data-c="{crop}"]')
        for i in (1, 3, 5, 7):
            await pg.click(f'.e4-plot[data-p="{i}"]')
        r = await pg.evaluate("() => [...document.querySelectorAll('.e4-plot')].map(b => b.classList.contains('z') ? 1 : 0).join('')")
        check(r == '11110000', f'ręczny przydział: cały górny rząd z zabiegiem ({r})')
        await pg.screenshot(path=f'{OUT}/e4_poletko_plan.png')
        await pg.click('#e4-pl-go')
        r = await pg.evaluate("() => ({ pole: game.e4Data().pole, obj: game.zone.objects.filter(o => o.type === 'e4_crop' && o.pole).length, flags: game.zone.objects.filter(o => o.flag).length })")
        check(r['pole'] and r['pole']['mode'] == 'reczny' and r['obj'] == 32 and r['flags'] == 8, f'eksperyment ruszył: 32 rośliny, 8 chorągiewek ({r["obj"]}, {r["flags"]})')
        await pg.evaluate("() => game.closeModal(true)")
        for _ in range(8):
            await pg.evaluate(DAY)
        await pg.evaluate("() => game.e4PlaceField()")
        await pg.evaluate("() => { game.player.x = 28*16+8; game.player.y = 22*16+8; }")
        await pg.wait_for_timeout(400)
        await pg.screenshot(path=f'{OUT}/e4_poletko_swiat.png')
        r = await pg.evaluate("() => !!(game.e4Data().pole && game.e4Data().pole.ripe)")
        check(r, 'plony na poletku dojrzały same (deszcz podlewa)')
        await pg.evaluate(SPOT, 'e4_pole')
        await pg.click('#e4-pl-har')
        txt = await pg.evaluate("() => document.getElementById('modal').innerText")
        check('zakłócenie' in txt and 'Prawda gry' in txt and 'z 70' in txt, 'wyniki: zakłócenie, test permutacyjny i „prawda gry”')
        r = await pg.evaluate("() => ({ log: game.e4Data().poleLog.length, pole: game.e4Data().pole, kosz: game.e4Data().kosz, bars: document.querySelectorAll('.e4-barv').length })")
        check(r['log'] == 1 and r['pole'] is None and r['bars'] == 8 and sum(r['kosz'].values()) >= 3, f'dziennik, 8 słupków, skrzynki w koszyku ({r})')
        await pg.screenshot(path=f'{OUT}/e4_poletko_wyniki.png')
        # losowanie w rzędach: po 2 poletka z zabiegiem w każdym rzędzie
        await pg.evaluate(SPOT, 'e4_pole')
        await pg.click(f'.e4-seed[data-c="{crop}"]')
        await pg.click('.e4-seed[data-t="muzyka"]')
        ok = True
        for _ in range(5):
            await pg.click('#e4-blok')
            a = await pg.evaluate("() => [...document.querySelectorAll('.e4-plot')].map(b => b.classList.contains('z') ? 1 : 0)")
            ok = ok and sum(a[:4]) == 2 and sum(a[4:]) == 2
        check(ok, 'losowanie w rzędach zawsze daje 2 + 2')
        await pg.click('#e4-pl-go')
        for _ in range(8):
            await pg.evaluate(DAY)
        await pg.evaluate(SPOT, 'e4_pole')
        await pg.click('#e4-pl-har')
        txt = await pg.evaluate("() => document.getElementById('modal').innerText")
        check('bloki' in txt and 'nie ma tu żadnego wpływu' in txt, 'bloki i „muzyka nie działa” w wynikach')
        r = await pg.evaluate("() => game.e4Data().stats")
        check(r.get('experiments') == 2 and r.get('randomized') == 1, f'statystyki eksperymentów ({r.get("experiments")}, {r.get("randomized")})')
        r = await pg.evaluate("() => { const P = ETAP4.permP; return [P([1,1,1,1,9,9,9,9],[1,1,1,1,0,0,0,0]), P([5,5,5,5,5,5,5,5],[1,0,1,0,1,0,1,0])]; }")
        check(abs(r[0] - 2/70) < 1e-9 and r[1] == 1, f'test permutacyjny: skrajny podział p = 2/70, brak różnic p = 1 ({r})')

        # ---------- 3. Rozbudowa domu ----------
        print('\n[3] Rozbudowa domu')
        await pg.evaluate("() => { game.closeModal(true); game.state.stats.xp = 250; game.state.stats.level = 3; game.setZone('port'); }")
        r = await pg.evaluate("""async () => { const n = game.npcs.find(x => x.id === 'brygadzista');
          const rr = Math.random; Math.random = () => 0.99; try { game.talkTo(n); } finally { Math.random = rr; }   // bez losowych dylematów z PROFILU
          await new Promise(r => setTimeout(r, 60));
          return game.dialog ? { pages: game.dialog.pages, opts: game.dialog.options.map(o => o.label) } : null; }""")
        check(r and len(r['pages']) == 2 and 'poziom' in r['pages'][1] and r['opts'][0].startswith('🏗️'), f'Brygadzista mówi o rozbudowie od 4. poziomu ({r})')
        r = await pg.evaluate("() => { game.closeDialog(true); game.e4Budowa(); return [!!document.getElementById('e4-b-take'), document.getElementById('e4-bud').innerText.includes('od 4. poziomu')]; }")
        check(r == [False, True], f'na 3. poziomie zlecenie zablokowane ({r})')
        r = await pg.evaluate("""() => { game.closeModal(true); game.state.stats.xp = 300; game.state.stats.level = 4; game.state.money = 400;
          game.e4Data().kosz = { salata: 6, dynia: 3, marchewka: 4 };
          game.e4Budowa(); document.getElementById('e4-b-take').click(); document.getElementById('e4-b-pay').click(); document.getElementById('e4-b-veg').click();
          return { job: game.e4Dom().job, kosz: game.e4Data().kosz, money: game.state.money }; }""")
        check(r['job'] and r['job']['paid'] and r['job']['veg'] == 10 and r['money'] == 150, f'zlecenie: zapłata i prowiant ({r["job"]}, {r["money"]})')
        check(r['kosz'] == {'dynia': 3}, f'najpierw oddaje najtańsze warzywa ({r["kosz"]})')
        await pg.screenshot(path=f'{OUT}/e4_budowa_zlecenie.png')
        # egzamin niezdany → jutro kolejne podejście
        await pg.evaluate("() => document.getElementById('e4-b-exam').click()")
        await pg.screenshot(path=f'{OUT}/e4_egzamin.png')
        for k in range(8):
            await pg.evaluate("""(k) => { const X = ETAP4.exam, q = X.items[X.i]; const bs = [...document.querySelectorAll('#modal .quiz-opt')];
              (k < 2 ? bs.find(b => b.dataset.id !== q.id) : bs.find(b => b.dataset.id === q.id)).click(); document.getElementById('e4-ex-next').click(); }""", k)
        r = await pg.evaluate("() => ({ txt: document.getElementById('modal').innerText, job: game.e4Dom().job })")
        check('6/8' in r['txt'] and not r['job']['exam'], 'egzamin 6/8 niezdany')
        r = await pg.evaluate("() => { document.getElementById('e4-ex-back').click(); return [!!document.getElementById('e4-b-exam'), document.getElementById('e4-bud').innerText.includes('kolejne jutro')]; }")
        check(r == [False, True], f'jedno podejście dziennie ({r})')
        await pg.evaluate("() => { game.closeModal(true); game.state.day += 1; game.e4Budowa(); document.getElementById('e4-b-exam').click(); }")
        for k in range(8):
            await pg.evaluate("""(k) => { const X = ETAP4.exam, q = X.items[X.i]; const bs = [...document.querySelectorAll('#modal .quiz-opt')];
              (k === 5 ? bs.find(b => b.dataset.id !== q.id) : bs.find(b => b.dataset.id === q.id)).click(); document.getElementById('e4-ex-next').click(); }""", k)
        r = await pg.evaluate("() => ({ txt: document.getElementById('modal').innerText, job: game.e4Dom().job, st: game.e4Data().stats })")
        check('7/8' in r['txt'] and r['job']['exam'] and r['st'].get('examFails') == 1, 'drugie podejście 7/8 zdane')
        r = await pg.evaluate("() => { document.getElementById('e4-ex-back').click(); return !!document.getElementById('e4-b-go'); }")
        check(r is False, 'bez opanowanych zagadnień nie da się zlecić budowy')
        r = await pg.evaluate("""() => { game.closeModal(true); const st = game.state.stats; QUESTIONS_DB.slice(0, 25).forEach(q => st.answeredQuestions[q.id] = true);
          game.e4Budowa(); document.getElementById('e4-b-go').click(); return game.e4Dom().job; }""")
        check(r['done'] and r['readyDay'] == r['examDay'] + 1, f'budowa zlecona, gotowa jutro ({r})')
        await pg.screenshot(path=f'{OUT}/e4_budowa_trwa.png')
        r = await pg.evaluate("() => { game.closeModal(true); game.setZone('dom'); return [HOME.w, game.zone.w, game.e4Dom().lvl]; }")
        check(r == [14, 14, 0], f'przed dniem gotowości dom bez zmian ({r})')
        r = await pg.evaluate("""() => { game.state.day += 1; game.setZone('osiedle'); game.setZone('dom'); game.player.x = 15*16+8; game.player.y = 5*16+8;
          const Z = game.zone, spec = Object.assign({ id: 'fotel' }, ITEMS.fotel), obraz = Object.keys(ITEMS).find(k => ITEMS[k].layer === 'wall');
          return { W: HOME.w, zw: Z.w, lvl: game.e4Dom().lvl, job: game.e4Dom().job, wallTop: Z.solid[2*Z.w+14], door: [4,5,6].map(y => Z.solid[y*Z.w+14]), wallBot: Z.solid[8*Z.w+14],
            fitsWall: game.nocFits(spec, 14, 8, 0), fitsNew: game.nocFits(spec, 16, 8, 0), fitsWin: obraz ? game.nocFits(Object.assign({ id: obraz }, ITEMS[obraz]), 16, 0, 0) : 'brak',
            light: Z.lights.some(l => l.col === '#ffe8b0') }; }""")
        check(r['W'] == 20 and r['zw'] == 20 and r['lvl'] == 1 and r['job'] is None, f'nowy pokój: izba 20 kratek ({r["W"]}, {r["zw"]}, {r["lvl"]})')
        check(r['wallTop'] == 1 and r['door'] == [0, 0, 0] and r['wallBot'] == 1 and r['light'], f'ścianka z przejściem i kinkiet ({r["wallTop"]}, {r["door"]}, {r["wallBot"]})')
        check(r['fitsWall'] is False and r['fitsNew'] is True and r['fitsWin'] is False, f'meble: nie na ściance ani oknie, tak w nowym pokoju ({r["fitsWall"]}, {r["fitsNew"]}, {r["fitsWin"]})')
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'{OUT}/e4_dom_nowy_pokoj.png')
        r = await pg.evaluate("() => { game.setZone('halina'); const a = [HOME.w, game.zone.w]; game.setZone('osiedle'); const b = HOME.w; game.setZone('dom'); game.save(); return [a, b, HOME.w]; }")
        check(r == [[14, 14], 14, 20], f'dom Pani Haliny i Osiedle bez zmian, u siebie 20 ({r})')
        await pg.reload(); await pg.wait_for_timeout(2000)
        r = await pg.evaluate("() => [HOME.w, game.zone.id, game.zone.w, game.e4Dom().lvl, JSON.parse(localStorage.getItem('akademia_freudowice_v1')).e4.dom.lvl]")
        check(r == [20, 'dom', 20, 1, 1], f'po wczytaniu gry pokój zostaje ({r})')
        r = await pg.evaluate("() => { game.closeModal(true); game.state.stats.level = 8; game.e4Budowa(); return document.getElementById('e4-bud').innerText; }")
        check('600' in r and '25 warzyw' in r and '📐 do zlecenia' in r, 'druga rozbudowa od 8. poziomu: 600 🟡, 25 warzyw')
        await pg.evaluate("() => { game.closeModal(true); const D = game.e4Dom(); D.lvl = 2; game.setZone('osiedle'); game.setZone('dom'); }")
        r = await pg.evaluate("() => [HOME.w, game.zone.solid[2*game.zone.w+20], game.zone.solid[5*game.zone.w+20]]")
        check(r == [26, 1, 0], f'dwa nowe pokoje: izba 26 kratek, druga ścianka z przejściem ({r})')
        await pg.wait_for_timeout(400)
        await pg.screenshot(path=f'{OUT}/e4_dom_dwa_pokoje.png')
        r = await pg.evaluate("() => { game.e4Budowa(); return document.getElementById('e4-bud').innerText.includes('wszystkie pokoje'); }")
        check(r, 'po dwóch rozbudowach: plan domu ukończony')
        await pg.evaluate("() => { game.closeModal(true); game.e4Dom().lvl = 1; game.setZone('osiedle'); game.setZone('dom'); }")

        # ---------- 4. Osobowość z wyborów ----------
        print('\n[4] Osobowość z wyborów')
        r = await pg.evaluate("""() => { const st = game.e4Data().stats; Object.assign(st, { waterDays: 9, plantedLong: 8, plantedShort: 2, soldHigh: 6, soldLow: 1 });
          const e3 = game.e3Data(); e3.leit = Object.assign({ cards: {} }, e3.leit, { sessions: 7 }); e3.ogrod = { oddech: 3, skan: 1 };
          const all = game.prObservations(), e4 = all.filter(x => x.k.startsWith('e4_'));
          const firstUnknown = all.findIndex(x => !x.text), lastKnown = all.map(x => !!x.text).lastIndexOf(true);
          return { hooked: !!Game.prototype.prObservations.e4, keys: e4.map(x => x.k), known: e4.filter(x => x.text).map(x => x.k), sorted: firstUnknown === -1 || lastKnown < firstUnknown, txt: e4.map(x => x.text).join(' | ') }; }""")
        check(r['hooked'] and len(r['keys']) == 6, f'6 nowych obserwacji w profilu ({r["keys"]})')
        check(set(['e4_systematycznosc', 'e4_troska', 'e4_cierpliwosc', 'e4_badawcze', 'e4_cele']) <= set(r['known']), f'obserwacje z wyborów i osiągnięć ({r["known"]})')
        check(r['sorted'], 'najpierw to, co gra zauważyła, potem „???”')
        check('Ukończył' not in r['txt'] and 'ukończyła' not in r['txt'], 'teksty bez form zależnych od płci')
        await pg.evaluate("() => game.openProfile('osobowosc')")
        await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'{OUT}/e4_profil_osobowosc.png')
        r = await pg.evaluate("() => { const b = document.querySelector('[data-obsno^=\"e4_\"]'); if (!b) return null; const k = b.dataset.obsno; b.click(); return [k, !!game.profData().obsNo[k]]; }")
        check(r and r[1], f'„To nie o mnie” działa dla nowych obserwacji ({r})')
        await pg.evaluate("() => game.closeModal(true)")
        r = await pg.evaluate("() => { game.save(); const s = JSON.parse(localStorage.getItem('akademia_freudowice_v1')); return !!(s.e4 && s.e4.stats && s.e4.dom && Array.isArray(s.e4.poleLog)); }")
        check(r, 'stan ETAP4 jest w pliku zapisu')

        # ---------- 5. telefon ----------
        print('\n[5] Telefon')
        mob = await b.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        merrs = []
        mob.on('pageerror', lambda e: merrs.append(str(e)))
        await start_game(mob)
        await mob.evaluate("() => { game.closeModal(true); game.closeDialog(true); game.state.money = 300; game.state.stats.level = 4; game.e4Data().kosz = { salata: 2 }; }")
        for name, js in [('ogrodek', "game.setZone('osiedle'); game.e4Ogrodek()"), ('straganik', "game.e4Stragan()"),
                         ('poletko', "game.setZone('wzgorze'); game.e4Poletko()"), ('budowa', "game.e4Budowa()")]:
            await mob.evaluate(f"() => {{ game.closeModal(true); {js}; }}")
            await mob.wait_for_timeout(300)
            over = await mob.evaluate(FITS)
            check(over is False, f'telefon: okno „{name}” mieści się na szerokość')
            await mob.screenshot(path=f'{OUT}/e4_tel_{name}.png')
        await mob.evaluate("() => { game.closeModal(true); game.e4Dom().lvl = 1; game.setZone('dom'); }")
        await mob.wait_for_timeout(400)
        await mob.screenshot(path=f'{OUT}/e4_tel_dom.png')
        check(not merrs, f'telefon: brak błędów ({merrs[:3]})')

        check(not errs, f'brak błędów JS ({errs[:5]})')
        await b.close()
    print('\nWYNIK:', 'OK' if not fails else f'{len(fails)} błędów')
    for f in fails:
        print('  -', f)
    sys.exit(1 if fails else 0)

asyncio.run(main())
