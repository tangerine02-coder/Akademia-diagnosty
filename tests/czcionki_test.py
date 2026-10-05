"""Test wyboru czcionek (2026-10-05): przycisk „Aa”, pary czcionek, zapamiętywanie wyboru.

Uruchomienie (w folderze repo):
    python3 -m http.server 8765 --directory "Akademia diagnosty" &
    python3 tests/czcionki_test.py

Sprawdza zmienne CSS, stałe dla canvasa (PIXEL_FONT, WORLD_FONT) i localStorage.
Same pliki czcionek przychodzą z Google Fonts — bez internetu przeglądarka pokaże zastępcze.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

URL = os.environ.get('GAME_URL', 'http://localhost:8765/akademia_diagnosty_miasteczko.html')
OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)
fails = []

def check(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)

STATE = """() => { const cs = getComputedStyle(document.documentElement);
  return { id: document.documentElement.dataset.font, pix: cs.getPropertyValue('--font-pixel'), body: cs.getPropertyValue('--font-body'),
    bodyFF: getComputedStyle(document.body).fontFamily, P: PIXEL_FONT, W: WORLD_FONT, ls: localStorage.getItem('ad_font') }; }"""

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
        await start_game(pg)
        r = await pg.evaluate(STATE)
        check(r['id'] == 'nowa' and 'Pixelify Sans' in r['pix'] and 'Fraunces' in r['body'] and 'Fraunces' in r['bodyFF'], f'domyślnie nowa para: Pixelify Sans + Fraunces ({r["id"]})')
        check('Pixelify Sans' in r['P'] and 'Fraunces' in r['W'], 'canvas: PIXEL_FONT i WORLD_FONT z nowej pary')
        check('Vollkorn' in r['body'] and 'Tiny5' in r['pix'], 'dawne czcionki zostają jako zapas w stosie')
        btn = await pg.query_selector('#bar #t-font')
        check(btn is not None, 'przycisk „Aa” na dolnym pasku')
        await pg.evaluate("() => game.closeModal(true)")
        await pg.click('#t-font')
        await pg.wait_for_timeout(300)
        r = await pg.evaluate("() => ({ title: document.querySelector('#modal .panel-head h2').textContent, opts: [...document.querySelectorAll('[data-font-id]')].map(b => b.dataset.fontId), sel: document.querySelector('.cz-opt.sel').dataset.fontId })")
        check(r['title'] == '🔤 Czcionka' and r['opts'] == ['nowa', 'ksiazkowa', 'wyrazna', 'klasyczna'] and r['sel'] == 'nowa', f'okno wyboru: 4 pary, zaznaczona nowa ({r})')
        await pg.screenshot(path=f'{OUT}/czcionki_okno.png')
        await pg.click('[data-font-id="klasyczna"]')
        r = await pg.evaluate(STATE)
        check(r['id'] == 'klasyczna' and r['pix'].strip().startswith("'Tiny5'") and r['body'].strip().startswith("'Vollkorn'") and r['ls'] == 'klasyczna', 'klasyczna: Tiny5 + Vollkorn, zapisane w przeglądarce')
        check('Vollkorn' in r['W'] and 'Tiny5' in r['P'] and 'Fraunces' not in r['W'], 'klasyczna: napisy na canvasie też wracają do Vollkorn')
        sel = await pg.evaluate("() => document.querySelector('.cz-opt.sel').dataset.fontId")
        check(sel == 'klasyczna', 'zaznaczenie przechodzi na wybraną parę')
        await pg.click('[data-font-id="wyrazna"]')
        r = await pg.evaluate(STATE)
        check('Atkinson Hyperlegible' in r['pix'] and 'Atkinson Hyperlegible' in r['body'] and 'Atkinson' in r['W'], 'wyraźna: Atkinson Hyperlegible wszędzie')
        await pg.click('[data-font-id="ksiazkowa"]')
        r = await pg.evaluate(STATE)
        check('Literata' in r['body'] and 'Pixelify Sans' in r['pix'] and 'Literata' in r['W'], 'książkowa: Pixelify Sans + Literata')
        await pg.reload(); await pg.wait_for_timeout(1800)
        r = await pg.evaluate(STATE)
        check(r['id'] == 'ksiazkowa' and 'Literata' in r['W'], f'wybór zostaje po odświeżeniu ({r["id"]})')
        await pg.evaluate("() => { game.closeModal(true); localStorage.setItem('ad_font', 'zepsuta'); }")
        await pg.reload(); await pg.wait_for_timeout(1800)
        r = await pg.evaluate(STATE)
        check('Fraunces' in r['W'] and 'Fraunces' in r['body'], f'nieznana wartość → nowa para ({r["id"]})')
        await pg.evaluate("() => { game.closeModal(true); CZCIONKI.apply('nowa'); }")
        # telefon: pasek mieści się na szerokość
        mob = await b.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        merrs = []
        mob.on('pageerror', lambda e: merrs.append(str(e)))
        await start_game(mob)
        r = await mob.evaluate("() => { const bar = document.getElementById('bar'), f = document.getElementById('t-font').getBoundingClientRect(); return { over: bar.scrollWidth > bar.clientWidth + 2, inside: f.right <= innerWidth && f.left >= 0 }; }")
        check(not r['over'] and r['inside'], f'telefon: pasek z „Aa” mieści się ({r})')
        await mob.evaluate("() => { game.closeModal(true); game.openFontPicker(); }")
        await mob.wait_for_timeout(300)
        over = await mob.evaluate("() => { const p = document.querySelector('#modal .panel'); return p.scrollWidth > p.clientWidth + 2 || p.getBoundingClientRect().right > innerWidth + 1; }")
        check(over is False, 'telefon: okno czcionek mieści się na szerokość')
        await mob.screenshot(path=f'{OUT}/czcionki_tel.png')
        check(not merrs, f'telefon: brak błędów ({merrs[:3]})')
        check(not errs, f'brak błędów JS ({errs[:5]})')
        await b.close()
    print('\nWYNIK:', 'OK' if not fails else f'{len(fails)} błędów')
    for f in fails:
        print('  -', f)
    sys.exit(1 if fails else 0)

asyncio.run(main())
