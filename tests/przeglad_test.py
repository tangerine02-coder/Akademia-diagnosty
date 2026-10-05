"""Przegląd całej gry (2026-10-05): każda dzielnica, każde miejsce interaktywne, każdy mieszkaniec, każde drzwi.

Uruchomienie (w folderze repo):
    python3 -m http.server 8765 --directory "Akademia diagnosty" &
    python3 tests/przeglad_test.py          # komputer
    python3 tests/przeglad_test.py tel      # telefon (390×844)

Nie sprawdza treści — szuka błędów JavaScript i ostrzeżeń modułów ETAP przy każdej interakcji.
"""
import asyncio, json, sys
from playwright.async_api import async_playwright
import os
URL = os.environ.get('GAME_URL', 'http://localhost:8765/akademia_diagnosty_miasteczko.html')
CLEAN = """() => { try { if (game._mg) game.mgStop(game._mg); } catch (e) {} game.closeModal(true); game.closeDialog(true); game.transition = null; if (game.scene === 'interior') game.leaveInterior(); game.transition = null; game.state.energy = 100; }"""
async def main():
    vw, vh = (390, 844) if 'tel' in sys.argv else (1100, 760)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': vw, 'height': vh})
        errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)[:300]))
        pg.on('console', lambda m: m.type == 'error' and 'ERR_TUNNEL' not in m.text and 'Failed to load resource' not in m.text and errs.append('CONSOLE ' + m.text[:300]))
        pg.on('console', lambda m: m.type == 'warning' and 'ETAP' in m.text and errs.append('WARN ' + m.text[:300]))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.fill("input[placeholder*='Sylwia']", 'Testerka')
        await pg.click('text=Zamieszkaj w Freudowice Zdrój')
        await pg.wait_for_timeout(1500)
        for _ in range(8):
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(80)
        zones = await pg.evaluate("() => ['dom'].concat(Object.keys(ZONES))")
        print('zones', len(zones))
        stats = {}
        for z in zones:
            n0 = len(errs)
            await pg.evaluate(CLEAN)
            ok = await pg.evaluate("(z) => { try { game.setZone(z); return true; } catch (e) { return String(e); } }", z)
            if ok is not True:
                errs.append(f'setZone {z}: {ok}'); continue
            await pg.wait_for_timeout(250)
            info = await pg.evaluate("() => ({ it: (game.zone.interacts || []).length, npc: (game.npcs || []).length, doors: (game.zone.buildings || []).length })")
            # interakcje
            for i in range(info['it']):
                await pg.evaluate(CLEAN)
                r = await pg.evaluate("""(i) => { const it = game.zone.interacts[i]; if (!it) return null; try { game.player.x = (it.x + 0.5) * 16; game.player.y = (it.y + (it.h || 1)) * 16 + 6; const pr = game.spotPrompt(it); game.useSpot(it); return it.kind + ':' + (pr || ''); } catch (e) { return 'ERR ' + it.kind + ' ' + e; } }""", i)
                if r and r.startswith('ERR'): errs.append(f'{z} useSpot {r}')
                await pg.wait_for_timeout(60)
            # mieszkańcy
            for i in range(info['npc']):
                await pg.evaluate(CLEAN)
                r = await pg.evaluate("""async (i) => { const n = game.npcs[i]; if (!n) return null; const rr = Math.random; Math.random = () => 0.99;
                  try { game.talkTo(n); } catch (e) { return 'ERR ' + n.id + ' ' + e; } finally { Math.random = rr; }
                  await new Promise(r => setTimeout(r, 30)); return n.id; }""", i)
                if r and r.startswith('ERR'): errs.append(f'{z} talk {r}')
            # drzwi
            for i in range(info['doors']):
                await pg.evaluate(CLEAN)
                r = await pg.evaluate("""(i) => { const b = game.zone.buildings[i]; if (!b) return null; try { game.player.x = b.doorCol * 16 + 8; game.player.y = b.doorRow * 16 + 8; game.player.dir = 'up'; game.enterDoor(b); return b.id; } catch (e) { return 'ERR ' + b.id + ' ' + e; } }""", i)
                if r and r.startswith('ERR'): errs.append(f'{z} door {r}')
                await pg.wait_for_timeout(700)
                await pg.evaluate(CLEAN)
                back = await pg.evaluate("(z) => { if (game.zone.id !== z) { try { game.setZone(z); } catch (e) { return String(e); } } return game.zone.id; }", z)
            stats[z] = (info, len(errs) - n0)
            print(z, info, 'nowe błędy:', len(errs) - n0)
        # rysowanie kilku klatek w każdej dzielnicy (render)
        for z in zones:
            await pg.evaluate(CLEAN)
            await pg.evaluate("(z) => game.setZone(z)", z)
            await pg.wait_for_timeout(120)
        await b.close()
    print('\nWYNIK:', 'OK' if not errs else f'{len(errs)} błędów')
    for e in errs[:40]:
        print(' -', e)
    sys.exit(1 if errs else 0)
asyncio.run(main())
