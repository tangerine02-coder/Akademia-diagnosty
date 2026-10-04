"""Test Etapu 1 (2026-10-04): wnętrza, domy, Błonia, easter eggi, muzyka.

Uruchomienie (w folderze repo):
    python3 -m http.server 8765 --directory "Akademia diagnosty" &
    python3 tests/etap1_test.py            # zrzuty ekranu trafiają do tests/out/

Test działa w czystym profilu przeglądarki, więc nie dotyka prawdziwego zapisu.
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

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1100, 'height': 760})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type in ('error', 'warning') and 'ETAP1' in m.text and errs.append(m.text))
        await pg.goto(URL)
        await pg.wait_for_timeout(1500)
        await pg.fill("input[placeholder*='Sylwia']", 'Testerka')
        await pg.click('text=Zamieszkaj w Freudowice Zdrój')
        await pg.wait_for_timeout(1500)
        for _ in range(8):
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(120)
        check(await pg.evaluate('() => !!window.ETAP1'), 'moduł ETAP1 załadowany')

        async def goto(zone, x, y):
            await pg.evaluate(f"""() => {{ game.closeModal && game.closeModal(true); game.closeDialog && game.closeDialog(true);
                game.setZone('{zone}'); game.player.x = {x}; game.player.y = {y}; game.state.time = 12*60; }}""")
            await pg.wait_for_timeout(500)

        # ---- 1) wnętrza: każdy dom ma motyw, stanowiska są osiągalne z wejścia ----
        res = await pg.evaluate("""() => {
          const out = [];
          for (const sid of Object.keys(SUBJECTS)) {
            const Z = buildSubjectZone(sid);
            const w = Z.w, h = Z.h, seen = new Uint8Array(w * h), q = [];
            const sx = Math.floor(w / 2), sy = h - 1;
            const push = (x, y) => { if (x < 0 || y < 0 || x >= w || y >= h || seen[y*w+x] || Z.solid[y*w+x]) return; seen[y*w+x] = 1; q.push([x, y]); };
            push(sx, sy); push(sx - 1, sy);
            while (q.length) { const [x, y] = q.shift(); push(x+1,y); push(x-1,y); push(x,y+1); push(x,y-1); }
            const bad = Z.interacts.filter(it => { const xs = [...Array(it.w).keys()].map(k => it.x + k);
              return !xs.some(x => [[x, it.y+1],[x, it.y-1],[x-1, it.y],[x+it.w, it.y]].some(([a,b]) => a>=0&&b>=0&&a<w&&b<h&&seen[b*w+a])); });
            let baked = true; try { bakeSubjectRoom(Z); } catch (e) { baked = false; }
            out.push({ sid, theme: Z.e1 ? Object.keys(ETAP1).length && SUBJECTS[sid] && Z.e1.floor[0] + '/' + Z.e1.wall[0] : null, bad: bad.length, baked, song: Z.def.song });
          }
          return out; }""")
        check(all(r['theme'] for r in res), f'wszystkie {len(res)} domy mają motyw wnętrza')
        check(all(r['bad'] == 0 for r in res), 'każde stanowisko i pulpit da się podejść od wejścia: ' + ', '.join(r['sid'] for r in res if r['bad']))
        check(all(r['baked'] for r in res), 'każde wnętrze się wypala (podłoga, ściana, okno)')
        check(len({r['theme'] for r in res}) >= 15, f"różnych kombinacji podłoga/ściana: {len({r['theme'] for r in res})}")
        for sid in ['psycholing', 'chronos', 'ewolucja_z', 'sny_trening', 'kl_autyzm', 'sp_kosmos', 'laik_szarlatani', 'laik_placebo']:
            await goto('in:' + sid, 8 * 16, 11 * 16)
            await pg.screenshot(path=f'{OUT}/wnetrze_{sid}.png')

        # ---- 2) domy z zewnątrz ----
        await goto('osiedle', 10 * 16, 22 * 16)
        await pg.screenshot(path=f'{OUT}/osiedle_domy.png')
        await goto('osiedle', 30 * 16, 10 * 16)
        await pg.screenshot(path=f'{OUT}/osiedle_halina.png')
        await goto('kampus', 20 * 16, 14 * 16)
        await pg.screenshot(path=f'{OUT}/kampus.png')
        await goto('wyspa_pinela', 20 * 16, 14 * 16)
        await pg.screenshot(path=f'{OUT}/wyspa_pinela.png')

        # ---- 3) Błonia ----
        await goto('blonia', 32 * 16, 20 * 16)
        kinds = await pg.evaluate("() => game.zone.interacts.map(i => i.kind).filter(k => k.startsWith('e1_'))")
        check(set(kinds) >= {'e1_galton', 'e1_lody', 'e1_srednia', 'e1_moneta', 'e1_regresja'}, 'Błonia: 5 stanowisk statystyki')
        await pg.screenshot(path=f'{OUT}/blonia.png')
        await pg.evaluate('() => game.e1Galton()')
        await pg.click('[data-n="100"]'); await pg.wait_for_timeout(2600)
        await pg.screenshot(path=f'{OUT}/galton.png')
        await pg.evaluate('() => game.closeModal(true)')
        await pg.evaluate('() => game.e1Lody()'); await pg.click('#e1-lody-btn'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=f'{OUT}/lody.png'); await pg.evaluate('() => game.closeModal(true)')
        await pg.evaluate('() => game.e1Srednia()'); await pg.click('#e1-sr-btn'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=f'{OUT}/srednia.png'); await pg.evaluate('() => game.closeModal(true)')
        await pg.evaluate('() => game.e1Moneta()')
        for _ in range(5):
            await pg.click('#e1-mon-btn'); await pg.wait_for_timeout(60)
        check(await pg.evaluate("() => !!document.querySelector('#e1-mon-q [data-a]')"), 'Automat z Monetą zadaje pytanie po serii')
        await pg.click('[data-a="even"]'); await pg.wait_for_timeout(150)
        await pg.screenshot(path=f'{OUT}/moneta.png'); await pg.evaluate('() => game.closeModal(true)')
        await pg.evaluate('() => game.e1Regresja()'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'{OUT}/regresja.png')
        await pg.evaluate('() => { game.closeDialog && game.closeDialog(true); }')
        st = await pg.evaluate('() => game.state.e1.blonia')
        check(st.get('_done') == 1, 'spacer statystyczny zaliczony po 5 stanowiskach')

        # ---- 4) easter eggi ----
        await goto('rynek', 20 * 16, 17 * 16)
        await pg.evaluate('() => { game.closeModal(true); game.closeDialog && game.closeDialog(true); }')
        await pg.keyboard.press('Escape')
        money0 = await pg.evaluate('() => game.state.money')
        for k in ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a']:
            await pg.keyboard.press(k); await pg.wait_for_timeout(40)
        await pg.wait_for_timeout(300)
        check(await pg.evaluate('() => (game.state.e1.konami || 0) >= 1'), 'kod Konami działa')
        check(await pg.evaluate(f'() => game.state.money') >= money0 + 7, 'Konami: +7 Dopaminek za pierwszym razem')
        await pg.screenshot(path=f'{OUT}/konami.png')
        await pg.evaluate('() => { game.closeDialog && game.closeDialog(true); game.closeModal(true); }')
        await pg.evaluate("""() => { const p = game.player, dirs = ['up','right','down','left'];
            for (let i = 0; i < 14; i++) { p.dir = dirs[i % 4]; game.e1EggsUpdate(0.05); } }""")
        check(await pg.evaluate('() => game.state.e1.zawrot === 1'), 'zawrót głowy po trzech obrotach')
        await pg.evaluate('() => game.e1Fontanna()'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=f'{OUT}/fontanna.png')
        await pg.evaluate('() => { game.closeDialog && game.closeDialog(true); }')
        await goto('bulwar', 35 * 16, 19 * 16)
        check(await pg.evaluate("() => game.zone.interacts.some(i => i.kind === 'e1_kaczka')"), 'gumowa kaczka na kanale')
        await pg.evaluate('() => game.e1Kaczka()'); await pg.fill('#e1-kaczka-txt', 'Nie wiem, od czego zacząć.'); await pg.click('#e1-kaczka-ok')
        await pg.screenshot(path=f'{OUT}/kaczka.png'); await pg.evaluate('() => game.closeModal(true)')
        await pg.evaluate('() => { game.state.day = 6; }')
        await goto('plaza', 30 * 16, 16 * 16)
        check(await pg.evaluate("() => game.zone.interacts.some(i => i.kind === 'e1_butelka')"), 'butelka z listem pojawia się w dniu 6')
        await pg.evaluate('() => game.e1Butelka()'); await pg.wait_for_timeout(200)
        check(await pg.evaluate("() => !game.zone.interacts.some(i => i.kind === 'e1_butelka')"), 'po przeczytaniu butelka odpływa')
        await pg.evaluate('() => { game.closeDialog && game.closeDialog(true); }')

        # ---- 5) muzyka: nowy sekwencer gra bez błędów we wszystkich utworach ----
        music = await pg.evaluate("""async () => {
            audio.init(); await new Promise(r => setTimeout(r, 300));
            if (audio.ctx.state !== 'running') { try { await audio.ctx.resume(); } catch (e) {} }
            const keys = Object.keys(SONGS); let errs = 0;
            for (const k of keys) { try { audio.setSong(k); audio.nextTime = audio.ctx.currentTime; for (let i = 0; i < 4; i++) audio.tick(); } catch (e) { errs++; } }
            audio.nightFactor = 0.6; try { audio.tick(); } catch (e) { errs++; }
            return { state: audio.ctx.state, songs: keys.length, errs, bus: !!audio._e1bus }; }""")
        print('  muzyka:', music)
        check(music['errs'] == 0, f"muzyka: {music['songs']} utworów bez błędów")

        # ---- 6) zapis: dane etapu przechodzą przez plik zapisu ----
        saved = await pg.evaluate('() => JSON.parse(game.exportSaveText()).e1')
        check(saved and saved.get('konami') and saved.get('blonia'), 'stan ETAP1 jest w pliku zapisu')

        check(not errs, 'brak błędów JS: ' + ' | '.join(errs[:5]))
        await b.close()
    print('\nWYNIK:', 'OK' if not fails else f'{len(fails)} błędów')
    sys.exit(1 if fails else 0)

asyncio.run(main())
