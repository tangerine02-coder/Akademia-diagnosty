"""Test Etapu 3 (2026-10-05): Archiwum 2.0, Dom Żyrafy, Dom Muzyki, Ogród Uważności, Dzielnica Pamięci.

Uruchomienie (w folderze repo):
    python3 -m http.server 8765 --directory "Akademia diagnosty" &
    python3 tests/etap3_test.py            # zrzuty ekranu trafiają do tests/out/

Test działa w czystym profilu przeglądarki, więc nie dotyka prawdziwego zapisu.
Ćwiczenia na czas są przyspieszane przez ETAP3.cfg.speed.
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

TALK = """async (id) => {
  game.closeModal(true); game.closeDialog(true);
  const n = game.npcs.find(x => x.id === id);
  if (!n) return { err: 'brak NPC ' + id + ' w ' + game.zone.id };
  const r = Math.random; Math.random = () => 0.99;
  try { game.talkTo(n); } finally { Math.random = r; }
  await new Promise(res => setTimeout(res, 60));
  const d = game.dialog;
  return d ? { name: d.name, pages: d.pages, options: (d.options || []).map(o => o.label) } : null;
}"""
SPOT = """(kind) => {
  game.closeModal(true); game.closeDialog(true);
  const it = game.zone.interacts.find(x => x.kind === kind);
  if (!it) return { err: 'brak ' + kind + ' w ' + game.zone.id };
  game.useSpot(it);
  const m = document.getElementById('modal');
  return { prompt: game.spotPrompt(it), modal: game.modalOpen ? m.querySelector('.panel-head h2').textContent : null,
    dialog: game.dialog ? { name: game.dialog.name, pages: game.dialog.pages, options: (game.dialog.options || []).map(o => o.label) } : null };
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
        pg.on('console', lambda m: m.type in ('error', 'warning') and 'ETAP3' in m.text and errs.append(m.text))
        await start_game(pg)
        check(await pg.evaluate('() => !!window.ETAP3'), 'moduł ETAP3 załadowany')
        await pg.evaluate("() => { ETAP3.cfg.speed = 1; game.state.energy = 100; game.e2Data().seasonOverride = 'lato'; }")

        async def wait_until(js, secs):
            for _ in range(int(secs * 10)):
                if await pg.evaluate(js):
                    return True
                await pg.wait_for_timeout(100)
            return False

        async def goto(zone, x, y, t=12 * 60):
            await pg.evaluate(f"""() => {{ game.closeModal(true); game.closeDialog(true);
                game.setZone('{zone}'); game.player.x = {x}; game.player.y = {y}; game.state.time = {t}; }}""")
            await pg.wait_for_timeout(350)

        async def modal_text():
            return await pg.evaluate("() => game.modalOpen ? document.getElementById('modal').innerText : ''")

        # ================= 0) MIASTO: siatka, most, płot =================
        grid = await pg.evaluate('() => ZONE_GRID')
        check(grid[2] == ['osiedle', 'plaza', 'port', 'dzielnica_pamieci'], f'Dzielnica Pamięci w siatce miasta, na wschód od Portu ({grid[2]})')
        nb = await pg.evaluate("() => [buildZone('port').neighbors.E, buildZone('dzielnica_pamieci').neighbors.W, buildZone('dzielnica_pamieci').exits]")
        check(nb[0] == 'dzielnica_pamieci' and nb[1] == 'port' and nb[2] == {'N': False, 'S': False, 'W': True, 'E': False}, f'sąsiedztwo Port ↔ Dzielnica Pamięci: {nb}')
        port = await pg.evaluate("""() => { const Z = buildZone('port'), w = Z.w;
          const col = y => Z.solid[y * w + 39]; return { fence: [1,2,3,4,5,6,7,8,9].every(col), bridge: [12,13,14,15].every(y => !col(y) && Z.terrain[y*w+39] === 'planks'),
            bollard: !Z.flats.some(f => f.type === 'bollard' && f.x === 33 && f.y === 12), sign: Z.interacts.some(i => i.kind === 'sign' && /MOST PAMIĘCI/.test(i.text)) }; }""")
        check(all(port.values()), f'Port: płotek na brzegu, most z desek, pachołek usunięty, drogowskaz ({port})')
        await goto('port', 39 * 16 + 15, 13 * 16 + 8)
        await pg.evaluate('() => game.checkEdges()')
        ok = await wait_until("() => !game.transition && game.zone.id === 'dzielnica_pamieci'", 6)
        pos = await pg.evaluate('() => [game.player.x, game.player.y, game.state.visited.dzielnica_pamieci]')
        check(ok and pos[0] < 40 and pos[2], f'przejście mostem do Dzielnicy Pamięci (gracz na {pos[:2]}, odwiedzona: {pos[2]})')
        toast = await pg.evaluate("() => new Promise(r => setTimeout(() => r(document.getElementById('toast').textContent), 1900))")
        check('Dzielnica Pamięci' in toast or 'Nowa dzielnica' in toast, f'powitanie nowej dzielnicy: {toast[:60]!r}')
        await pg.screenshot(path=f'{OUT}/e3_most_dzielnica.png')
        await pg.evaluate('() => { game.player.x = 2; game.checkEdges(); }')
        back = await wait_until("() => !game.transition && game.zone.id === 'port'", 6)
        check(back, 'powrót mostem do Portu')
        kart = await pg.evaluate("() => ALL_BADGES.find(b => b.id === 'kartograf').desc")
        check('10' in kart, f'odznaka Kartografa: {kart!r}')
        await goto('port', 27 * 16 + 8, 7 * 16 + 4)
        mag = await pg.evaluate("""() => { const b = game.zone.buildings.find(x => x.id === 'magazyn'); game.closeDialog(true); game.enterDoor(b); return game.dialog ? game.dialog.pages.join(' ') : ''; }""")
        check('Przeprowadzka' in mag, 'stary Magazyn w Porcie odsyła do Dzielnicy Pamięci')
        bud = await pg.evaluate(SPOT, 'budowa')
        check(bud['dialog'] and any('Dzielnicę Pamięci' in p_ for p_ in bud['dialog']['pages']), 'plac budowy w Porcie wspomina nową dzielnicę')

        # ================= 1) ARCHIWUM 2.0 =================
        await goto('wyparte', 19 * 16 + 8, 8 * 16 + 10)
        d = await pg.evaluate(TALK, 'sceptyk')
        check(d and any('Wystawa' in o for o in d['options']), f'Kustosz proponuje wystawę: {d and d["options"]}')
        w = await pg.evaluate("""() => { game.closeDialog(true); const b = game.zone.buildings.find(x => x.loc === 'archiwum'); game.enterDoor(b);
          return game.dialog ? game.dialog.options.map(o => o.label) : null; }""")
        check(w and len(w) == 3 and 'Wystawa' in w[0] and 'Zajęcia' in w[1], f'drzwi Archiwum: wybór Wystawa / Zajęcia ({w})')
        await pg.evaluate('() => game.chooseOption(0)')
        await pg.wait_for_timeout(250)
        halls = await pg.evaluate("() => document.querySelectorAll('#modal .e3-hall').length")
        check(halls == 6, f'wystawa: 6 sal ({halls})')
        await pg.screenshot(path=f'{OUT}/e3_wystawa.png')
        await pg.click('#modal .e3-hall >> nth=0'); await pg.wait_for_timeout(200)
        exn = await pg.evaluate("() => document.querySelectorAll('#modal .e3-ex').length")
        check(exn >= 3, f'sala z eksponatami ({exn})')
        xp0 = await pg.evaluate('() => game.state.stats.xp')
        await pg.click('#modal .e3-ex >> nth=0'); await pg.wait_for_timeout(200)
        secs = await pg.evaluate("() => document.querySelectorAll('#modal .e3-ex-sec').length")
        seen = await pg.evaluate('() => Object.keys(game.e3Wyst().seen).length')
        xp1 = await pg.evaluate('() => game.state.stats.xp')
        check(secs == 4 and seen == 1 and xp1 > xp0, f'eksponat: 4 części (obietnica/badania/dlaczego/lekcja), zapisany, +XP ({secs}, {seen}, {xp1 - xp0})')
        await pg.screenshot(path=f'{OUT}/e3_eksponat.png')
        # cała sala → premia
        allhall = await pg.evaluate("""async () => { const h = ETAP3.WYSTAWA[0]; for (const it of h.items) { game.e3OpenEksponat(it.id); await new Promise(r => setTimeout(r, 30)); }
          return { hall: !!game.e3Wyst().halls[h.id], txt: document.getElementById('modal').innerText.includes('Sala zwiedzona') }; }""")
        check(allhall['hall'], f'zwiedzona cała sala zapisana ({allhall})')
        await goto('wyparte', 9 * 16 + 8, 22 * 16 + 10)
        g = await pg.evaluate(SPOT, 'e3_gablota')
        check(g['modal'] and 'Sala' in g['modal'] and g['prompt'].startswith('Gablota:'), f'gablota otwiera swoją salę: {g["prompt"]} → {g["modal"]}')
        a = await pg.evaluate(SPOT, 'e3_aleja')
        check(a['dialog'] and a['dialog']['name'] == 'Aleja Gablot', 'tabliczka alei gablot')
        await pg.screenshot(path=f'{OUT}/e3_aleja_gablot.png')

        # ================= 2) DOM ŻYRAFY =================
        await goto('bulwar', 36 * 16 + 8, 8 * 16 + 4)
        zy = await pg.evaluate("() => { const b = game.zone.buildings.find(x => x.subject === 'e3_zyrafa'); return b && [b.doorCol, b.doorRow, game.subjectDoorPrompt(b)]; }")
        check(zy and zy[0] == 36 and zy[1] == 6, f'Dom Żyrafy na Bulwarze, drzwi (36,6): {zy}')
        await pg.evaluate("() => { const b = game.zone.buildings.find(x => x.subject === 'e3_zyrafa'); game.enterSubjectHouse(b); }")
        inside = await wait_until("() => !game.transition && game.zone.id === 'in:e3_zyrafa'", 6)
        check(inside, 'wejście do Domu Żyrafy')
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'{OUT}/e3_zyrafa_wnetrze.png')
        info = await pg.evaluate("() => { game.closeModal(true); game.showSubjectInfo('e3_zyrafa'); return [...document.querySelectorAll('#modal .panel-foot button')].map(b => b.textContent); }")
        check(any('Księga' in x for x in info), f'pulpit w holu: przycisk Księgi Rozmów ({info})')
        ks = await pg.evaluate("() => { game.closeModal(true); game.e3KsiegaRozmow(); return { title: document.querySelector('#modal .panel-head h2').textContent, n: document.querySelectorAll('#modal details').length, talks: document.querySelectorAll('#modal .e3-talk').length }; }")
        check('Księga' in ks['title'] and ks['n'] > 0 and ks['talks'] >= ks['n'] * 3, f'Księga Rozmów: rozmowy z miasta w 4 stylach ({ks})')
        await pg.screenshot(path=f'{OUT}/e3_ksiega.png')
        await pg.evaluate("() => { game.closeModal(true); game.exitSubjectHouse(); }")
        outside = await wait_until("() => !game.transition && game.zone.id === 'bulwar'", 6)
        check(outside, 'wyjście z Domu Żyrafy na Bulwar')
        await goto('bulwar', 25 * 16, 19 * 16)
        pi = await pg.evaluate(SPOT, 'pianino')
        keys = await pg.evaluate("() => document.querySelectorAll('#modal .e3-key').length")
        check(pi['modal'] and 'Pianino' in pi['modal'] and keys == 13, f'pianino uliczne: grywalne, 13 klawiszy ({pi["modal"]}, {keys})')
        await pg.keyboard.press('KeyA'); await pg.keyboard.press('KeyG')
        await pg.click('#e3-p-sim'); await pg.wait_for_timeout(300)
        st = await pg.evaluate("() => document.getElementById('e3-p-st').textContent")
        check('Słuchaj' in st, f'„Zagraj z pamięci”: melodia startuje ({st!r})')
        await pg.screenshot(path=f'{OUT}/e3_pianino.png')
        await pg.evaluate('() => game.closeModal(true)')

        # ================= 3) DOM MUZYKI =================
        await goto('plaza', 31 * 16 + 8, 8 * 16 + 4)
        mu = await pg.evaluate("() => { const b = game.zone.buildings.find(x => x.subject === 'e3_muzyka'); return b && [b.doorCol, b.doorRow]; }")
        check(mu == [31, 6], f'Dom Muzyki na Plaży, drzwi (31,6): {mu}')
        sh = await pg.evaluate(SPOT, 'e3_shepard')
        check(sh['dialog'] and sh['dialog']['name'] == 'Schody Sheparda', 'Schody Sheparda grają iluzję')
        d = await pg.evaluate(TALK, 'fuga')
        check(d and d.get('name') == 'Kapelmistrzyni Fuga', f'Kapelmistrzyni Fuga rozmawia ({d and d.get("name")})')

        # ================= 4) OGRÓD UWAŻNOŚCI =================
        await goto('wzgorze', 7 * 16 + 8, 7 * 16 + 4)
        og = await pg.evaluate("""() => { const Z = game.zone, w = Z.w; return { b: Z.buildings.find(x => x.subject === 'e3_uwaznosc'), spots: ['e3_oddech','e3_skan','e3_staw','e3_dzwon'].filter(k => Z.interacts.some(i => i.kind === k)),
          gap: [6,7,8].every(x => !Z.solid[11*w+x]), hedge: [2,3,4,5,9,10,11,12].every(x => Z.solid[11*w+x]), npc: Z.npcs.some(n => n.id === 'oddechowska') }; }""")
        check(og['b'] and og['b']['doorCol'] == 7 and len(og['spots']) == 4 and og['gap'] and og['hedge'] and og['npc'], f'Ogród: pawilon, 4 stanowiska, żywopłot z wejściem, Pani Oddechowska ({og["spots"]})')
        await pg.evaluate("() => { ETAP3.cfg.speed = 30; }")
        o = await pg.evaluate(SPOT, 'e3_oddech')
        check(o['modal'] and 'Kamień Oddechu' in o['modal'], 'Kamień Oddechu: okno ćwiczenia')
        await pg.click('#e3-br-go')
        await pg.wait_for_timeout(250)
        mid = await pg.evaluate("() => document.getElementById('e3-br-txt').textContent")
        check(mid.startswith('Wdech') or mid.startswith('Wydech'), f'oddech: kółko prowadzi wdech/wydech ({mid!r})')
        await pg.screenshot(path=f'{OUT}/e3_oddech.png')
        okb = await wait_until("() => !!document.querySelector('#e3-br-end [data-f]')", 6)
        en0 = await pg.evaluate('() => game.state.energy')
        txt = await modal_text()
        check(okb and '+6 ⚡' in txt, f'oddech: koniec, pytanie „jak teraz jest?”, +6 ⚡ raz dziennie')
        await pg.click('#e3-br-end [data-f="2"]'); await pg.wait_for_timeout(150)
        fb = await pg.evaluate("() => document.getElementById('e3-br-fb').textContent")
        check('specjalistą' in fb, 'oddech: odpowiedź „gorzej” dostaje troskliwą wskazówkę')
        await pg.screenshot(path=f'{OUT}/e3_oddech_koniec.png')
        sk = await pg.evaluate(SPOT, 'e3_skan')
        await pg.click('#e3-sk-go'); await pg.wait_for_timeout(150)
        h1 = await pg.evaluate("() => document.getElementById('e3-sk-h').textContent")
        on1 = await pg.evaluate("() => [...document.querySelectorAll('.e3-bp.on')].map(e => e.dataset.part)")
        check(h1 == 'Stopy' and on1 and all(x == 'stopy' for x in on1), f'skanowanie: zaczyna od stóp ({h1}, {on1})')
        await pg.screenshot(path=f'{OUT}/e3_skan.png')
        sk_end = await wait_until("() => document.getElementById('e3-sk-h') && document.getElementById('e3-sk-h').textContent.includes('Koniec')", 8)
        check(sk_end and 'MBSR' in await modal_text(), 'skanowanie: 9 części ciała, zakończenie z wyjaśnieniem')
        # staw myśli: każdy liść nazwany poprawnie
        await pg.evaluate("() => { ETAP3.cfg.speed = 4; }")
        st = await pg.evaluate(SPOT, 'e3_staw')
        await pg.click('#e3-st-go')
        labeled = 0
        for _ in range(300):
            r = await pg.evaluate("""() => {
              if (!document.getElementById('e3-pond')) return 'closed';
              if (document.querySelector('#e3-st-end .fb')) return 'end';
              const leaves = [...document.querySelectorAll('.e3-leaf')].filter(l => !l.classList.contains('ok') && !l.classList.contains('bad'));
              if (!leaves.length) return 'wait';
              const L = leaves[0], txt = L.textContent.replace('🍂', '').trim();
              const def = ETAP3.LISCIE.find(x => ETAP3.g(game, x[0]) === txt);
              if (!def) return 'unknown:' + txt;
              L.click(); document.querySelector('.e3-lbl[data-l="' + def[1] + '"]').click(); return 'labeled';
            }""")
            if r == 'labeled': labeled += 1
            if r == 'end' or r == 'closed' or r.startswith('unknown'): break
            await pg.wait_for_timeout(60)
        end = await modal_text()
        check('trafnie: 9' in end.replace('\n', ' ') and labeled == 9, f'Staw Myśli: 9 liści, wszystkie nazwane trafnie ({labeled}, {r})')
        check('defuzja' in end, 'Staw Myśli: wyjaśnienie (ACT, defuzja)')
        await pg.screenshot(path=f'{OUT}/e3_staw.png')
        # dzwon
        await pg.evaluate("() => { ETAP3.cfg.speed = 20; }")
        dz = await pg.evaluate(SPOT, 'e3_dzwon')
        await pg.click('#e3-bell-go'); await pg.wait_for_timeout(400)
        await pg.click('#e3-bell-stop'); await pg.wait_for_timeout(150)
        bell = await modal_text()
        check('Słuchał' in bell and 'Thich Nhat Hanha' in bell, 'Dzwon Uważności: czas słuchania i wyjaśnienie')
        allg = await pg.evaluate("() => [game.e3Ogrod(), !!game.e3Data().once.ogrod_all]")
        check(allg[1], f'wszystkie 4 ćwiczenia ogrodu → premia ({allg[0]})')
        await pg.evaluate('() => { game.closeModal(true); ETAP3.cfg.speed = 1; }')
        e_before = await pg.evaluate('() => game.state.energy')
        rep = await pg.evaluate("() => game.e3OgrodReward('oddech', 6, ['spokoj', 6])")
        e_after = await pg.evaluate('() => game.state.energy')
        check(e_after == e_before and 'raz dziennie' in rep, 'energia z ćwiczenia tylko raz dziennie')
        await goto('wzgorze', 7 * 16 + 8, 12 * 16)
        await pg.screenshot(path=f'{OUT}/e3_ogrod.png')

        # ================= 5) DZIELNICA PAMIĘCI =================
        await goto('dzielnica_pamieci', 16 * 16 + 8, 16 * 16 + 8)
        dz = await pg.evaluate("""() => { const Z = game.zone; return { b: Z.buildings.map(b => [b.id, b.subject, b.doorCol, b.doorRow]), npcs: Z.npcs.map(n => n.id),
          spots: ['e3_fiszkomat','e3_krzywa','e3_lete','e3_kapsula'].filter(k => Z.interacts.some(i => i.kind === k)), bus: !!Z.busStop, song: Z.def.song }; }""")
        check(len(dz['b']) == 3 and all(x[1] for x in dz['b']), f'trzy domy-przedmioty: {dz["b"]}')
        check(set(dz['npcs']) >= {'mnemozyna', 'ebbinghaus', 'pewny', 'rybka'} and len(dz['spots']) == 4 and dz['bus'] and dz['song'] == 'pamiec', f'mieszkańcy, park, przystanek, muzyka ({dz["npcs"]}, {dz["spots"]})')
        fish = await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'rybka'); const s = animalSprite(n.def, 0); return { water: game.zone.terrain[Math.floor(n.y/16)*40 + Math.floor(n.x/16)], w: s.c.width }; }")
        check(fish['water'] == 'water' and fish['w'] > 5, f'złota rybka pływa w Kanale Lety ({fish})')
        # Automat Powtórek (pudełka Leitnera)
        empty = await pg.evaluate(SPOT, 'e3_fiszkomat')
        check('pusty' in await modal_text(), 'Automat Powtórek bez zaliczonych pytań: podpowiada, skąd wziąć karty')
        await pg.evaluate("() => { QUESTIONS_DB.slice(0, 6).forEach(q => game.state.stats.answeredQuestions[q.id] = true); game.closeModal(true); }")
        f1 = await pg.evaluate(SPOT, 'e3_fiszkomat')
        go = await pg.evaluate("() => { const b = document.getElementById('e3-lt-go'); return b && b.textContent; }")
        check(go and '5 kart' in go, f'Automat Powtórek: 6 kart do powtórki, sesja po 5 ({go})')
        await pg.screenshot(path=f'{OUT}/e3_fiszkomat.png')
        await pg.click('#e3-lt-go'); await pg.wait_for_timeout(150)
        await pg.screenshot(path=f'{OUT}/e3_fiszka.png')
        for k in range(5):
            await pg.keyboard.press('Space'); await pg.wait_for_timeout(80)
            await pg.keyboard.press('3' if k < 4 else '1'); await pg.wait_for_timeout(80)
        summ = await modal_text()
        leit = await pg.evaluate("() => { const L = game.e3Leit(), d = game.state.day; return { n: Object.keys(L.cards).length, boxes: Object.values(L.cards).map(c => c.box), next: Object.values(L.cards).map(c => c.next - d) }; }")
        check('Powtórka gotowa' in summ and leit['n'] == 5 and sorted(leit['boxes']) == [1, 2, 2, 2, 2] and sorted(leit['next']) == [1, 2, 2, 2, 2], f'Leitner: „pamiętam” → pudełko 2 (za 2 dni), „nie” → jutro ({leit})')
        check('+6 XP' in summ, 'pierwsza powtórka dnia nagrodzona')
        due = await pg.evaluate("() => { const a = game.e3LeitDue().due.length; game.state.day += 2; const b = game.e3LeitDue().due.length; game.state.day -= 2; return [a, b]; }")
        check(due == [1, 6], f'kolejka: dziś 1 nowa karta, za 2 dni wszystkie 6 ({due})')
        await pg.evaluate("() => { game.closeModal(true); }")
        # Krzywa Ebbinghausa, Fontanna Lety
        kr = await pg.evaluate(SPOT, 'e3_krzywa')
        path_ok = await pg.evaluate("() => (document.querySelector('#modal .e3-chart path') || {}).getAttribute && document.querySelector('#modal .e3-chart path').getAttribute('d').split('L').length")
        check(kr['modal'] and 'Ebbinghausa' in kr['modal'] and path_ok == 8, f'Krzywa Ebbinghausa: wykres z 8 punktami ({path_ok})')
        await pg.screenshot(path=f'{OUT}/e3_krzywa.png')
        le = await pg.evaluate(SPOT, 'e3_lete')
        check(le['dialog'] and len(le['dialog']['options']) == 3, 'Fontanna Lety: wybór źródła')
        await pg.evaluate('() => game.chooseOption(1)'); await pg.wait_for_timeout(150)
        tip = await pg.evaluate('() => game.dialog && game.dialog.name')
        check(tip == 'Źródło Mnemozyny', f'źródło Mnemozyny daje radę o pamięci ({tip})')
        # Kapsuła Czasu
        await pg.evaluate("() => game.closeDialog(true)")
        kp = await pg.evaluate(SPOT, 'e3_kapsula')
        await pg.fill('#e3-kp-txt', 'Drogie Przyszłe Ja: czy pamiętasz, czego uczyłaś się o pamięci?')
        await pg.click('#e3-kp-go'); await pg.wait_for_timeout(150)
        k1 = await pg.evaluate("() => game.e3Data().kapsula")
        check(k1 and k1['open'] == k1['day'] + 7, f'Kapsuła Czasu zakopana na 7 dni ({k1 and k1["open"]})')
        k2 = await pg.evaluate(SPOT, 'e3_kapsula')
        check(k2['dialog'] and 'zakopana' in ' '.join(k2['dialog']['pages']), 'przed terminem kapsuła się nie otwiera')
        await pg.evaluate("() => { game.closeDialog(true); game.state.day += 7; }")
        xp0 = await pg.evaluate('() => game.state.stats.xp')
        k3 = await pg.evaluate(SPOT, 'e3_kapsula')
        xp1 = await pg.evaluate('() => game.state.stats.xp')
        check(k3['modal'] and 'otwarta' in k3['modal'] and 'Przyszłe Ja' in await modal_text() and xp1 - xp0 >= 10, 'po 7 dniach: list wraca, +10 XP')
        await pg.screenshot(path=f'{OUT}/e3_kapsula.png')
        await pg.evaluate("() => { game.closeModal(true); game.state.day -= 7; }")
        # rozmowy
        for npc, name in [('mnemozyna', 'Mnemozyna'), ('ebbinghaus', 'Hermann Ebbinghaus'), ('pewny', 'Pan Pewny, świadek'), ('rybka', 'Złota rybka')]:
            d = await pg.evaluate(TALK, npc)
            check(d and d.get('name') == name, f'rozmowa: {name}')
        nb_ = await pg.evaluate("() => { game.closeDialog(true); const it = game.zone.interacts.find(i => i.kind === 'np_info'); if (!it) return null; game.useSpot(it); return game.dialog && game.dialog.pages.join(' '); }")
        check(nb_ and 'hipokamp' in nb_, 'tablica dzielnicy: „gdzie to jest w mózgu?”')
        await pg.evaluate("() => game.closeDialog(true)")
        await goto('dzielnica_pamieci', 20 * 16, 13 * 16)
        await pg.screenshot(path=f'{OUT}/e3_dzielnica.png')
        await goto('dzielnica_pamieci', 20 * 16, 13 * 16, 22 * 60 + 30)
        await pg.screenshot(path=f'{OUT}/e3_dzielnica_noc.png')

        # ================= 6) DOMY-PRZEDMIOTY: wnętrza i wszystkie pokoje =================
        houses = ['e3_zyrafa', 'e3_muzyka', 'e3_uwaznosc', 'e3_magazyn', 'e3_falszywe', 'e3_techniki']
        for sid in houses:
            res = await pg.evaluate(f"""async () => {{
              const S = SUBJECTS['{sid}']; game.closeModal(true); game.closeDialog(true); game.setZone(S.zone);
              const b = game.zone.buildings.find(x => x.subject === '{sid}'); game.player.x = b.doorCol * 16 + 8; game.player.y = (b.doorRow + 1) * 16 + 6;
              game.enterSubjectHouse(b);
              for (let i = 0; i < 80 && (game.transition || game.zone.id !== 'in:{sid}'); i++) await new Promise(r => setTimeout(r, 50));
              const inside = game.zone.id === 'in:{sid}', song = game.zone.def.song;
              const rooms = [];
              for (let i = 0; i < S.rooms.length; i++) {{
                game.state.energy = 100; game.closeModal(true);
                let ok = true, err = '';
                try {{ game.startMinigame('{sid}', i); }} catch (e) {{ ok = false; err = String(e); }}
                const has = !!document.querySelector('#modal .mg');
                rooms.push(S.rooms[i].kind + (ok && has ? '' : ' BŁĄD ' + err));
                game.closeModal(true);
              }}
              return {{ inside, song, rooms }};
            }}""")
            bad = [r_ for r_ in res['rooms'] if 'BŁĄD' in r_]
            check(res['inside'] and not bad, f'{sid}: wnętrze ({res["song"]}), pokoje startują: {res["rooms"]}')
        lect = await pg.evaluate("() => ['e3_techniki', 'e3_uwaznosc'].map(s => { game.closeModal(true); game.showSubjectInfo(s); return [...document.querySelectorAll('#modal .panel-foot button')].map(b => b.textContent).join('|'); })")
        check('Automat' in lect[0] and 'oddechu' in lect[1], f'pulpity: Automat Powtórek w Pracowni, oddech w Pawilonie ({lect})')
        await pg.evaluate('() => game.closeModal(true)')
        await pg.screenshot(path=f'{OUT}/e3_wnetrze_techniki.png')

        # --- eksperymenty z prawdziwą rozgrywką ---
        async def play_drm():
            await pg.evaluate("() => { ETAP3.cfg.speed = 40; game.state.energy = 100; game.closeModal(true); game.startMinigame('e3_falszywe', 0); }")
            for rnd in range(2):
                await pg.keyboard.press('Enter')
                ok = await wait_until("() => !!document.querySelector('#e3-drm [data-a]')", 5)
                if not ok: return 'brak testu'
                if rnd == 0: await pg.screenshot(path=f'{OUT}/e3_drm.png')
                for _ in range(7):
                    word = await pg.evaluate("() => document.querySelector('#e3-drm .e3-word').textContent")
                    await pg.keyboard.press('1'); await pg.wait_for_timeout(40)
                await pg.wait_for_timeout(100)
            return await modal_text()
        drm = await play_drm()
        check('wynik' in (await pg.evaluate("() => document.querySelector('#modal .panel-head h2').textContent")) and 'fałszywe wspomnienie' in drm, 'DRM: dwie listy, słowa-wabiki rozpoznane jako „były” → wyjaśnienie')
        await pg.screenshot(path=f'{OUT}/e3_drm_wynik.png')

        await pg.evaluate("() => { ETAP3.cfg.speed = 10; game.state.energy = 100; game.closeModal(true); game.startMinigame('e3_falszywe', 1); }")
        await pg.screenshot(path=f'{OUT}/e3_swiadek_start.png')
        await pg.click('#e3-play')
        sp_ok = await wait_until("() => !!document.getElementById('e3-v')", 6)
        await pg.screenshot(path=f'{OUT}/e3_swiadek_pytanie.png')
        await pg.evaluate("() => { const v = document.getElementById('e3-v'); v.value = 70; v.dispatchEvent(new Event('input')); }")
        await pg.click('#e3-vok'); await pg.wait_for_timeout(100)
        await pg.click('#modal [data-g="0"]'); await pg.wait_for_timeout(200)
        sw = await modal_text()
        check(sp_ok and 'Loftus i Palmer' in sw and '70 km/h' in sw and 'nie było' in sw, 'Świadek stłuczki: nagranie → prędkość → szkło → wyniki Loftus i Palmer')
        await pg.screenshot(path=f'{OUT}/e3_swiadek_wynik.png')

        await pg.evaluate("() => { ETAP3.cfg.speed = 30; game.state.energy = 100; game.closeModal(true); game.startMinigame('e3_techniki', 0); }")
        pairs = {}
        for k in range(8):
            await wait_until("() => { const b = document.getElementById('e3-lc-next'); return b && !b.disabled; }", 4)
            pl, it = await pg.evaluate("() => [document.querySelector('.e3-locus-place').textContent, document.querySelector('.e3-locus-item').textContent.replace(/^\\S+\\s*/, '').trim()]")
            pairs[pl] = it.lower()
            if k == 0: await pg.screenshot(path=f'{OUT}/e3_loci.png')
            await pg.click('#e3-lc-next')
        okr = await wait_until("() => !!document.querySelector('.e3-lc-opts')", 6)
        for k in range(8):
            pl = await pg.evaluate("() => document.querySelector('.e3-locus-place').textContent")
            target = pairs.get(pl, '')
            await pg.evaluate(f"() => {{ const b = [...document.querySelectorAll('.e3-lc-opts button')].find(x => x.textContent.toLowerCase().includes({json.dumps(target)})); (b || document.querySelector('.e3-lc-opts button')).click(); }}")
            await pg.wait_for_timeout(60)
        lo = await modal_text()
        check(okr and '8/8' in lo, f'Pałac pamięci: 8 przedmiotów na 8 miejscach trasy ({lo[lo.find("Przedmioty"):lo.find("Przedmioty") + 50]!r})')
        await pg.screenshot(path=f'{OUT}/e3_loci_wynik.png')
        await pg.evaluate('() => { game.closeModal(true); ETAP3.cfg.speed = 1; }')

        # ================= 7) Etap 2: przedmiot zadania w nowym domu zostaje przeniesiony =================
        fx = await pg.evaluate("""() => {
          game.closeModal(true); game.closeDialog(true);
          const q = game.e2Quests(); q.listy = { state: 'active', day: game.state.day, items: [{ zone: 'bulwar', x: 35, y: 4, found: false }] };
          game.setZone('bulwar'); game.e2PlaceItems();
          const it = game.e2Quests().listy.items[0], Z = game.zone;
          return { x: it.x, y: it.y, solid: Z.solid[it.y * Z.w + it.x], obj: Z.objects.some(o => o.type === 'e2_item' && o.x === it.x && o.y === it.y) };
        }""")
        check(not fx['solid'] and fx['obj'] and (fx['x'], fx['y']) != (35, 4), f'zgubiony list w ścianie Domu Żyrafy przeniesiony na wolne pole ({fx})')
        await pg.evaluate("() => { game.e2Quests().listy = { state: null }; game.e2PlaceItems(); }")

        # ================= 8) dziennik, zapis =================
        jr = await pg.evaluate("() => { game.closeModal(true); game.showJournal('stats'); const c = [...document.querySelectorAll('#modal .card')].find(x => x.textContent.includes('Odkryte dzielnice')); return c && c.textContent; }")
        check(jr and '/10' in jr, f'dziennik: odkryte dzielnice liczone z 10 ({jr})')
        await pg.evaluate('() => { game.closeModal(true); game.save(); }')
        saved = await pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('akademia_freudowice_v1')); return s && s.e3 ? Object.keys(s.e3) : null; }")
        check(saved and all(k in saved for k in ['wyst', 'ogrod', 'leit', 'once', 'daily']), f'stan Etapu 3 w zapisie: {saved}')
        await pg.reload(); await pg.wait_for_timeout(2500)
        for _ in range(8):
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
        after = await pg.evaluate("() => game && game.state && game.state.e3 ? [Object.keys(game.state.e3.wyst.seen).length, Object.keys(game.state.e3.leit.cards).length] : null")
        check(after and after[0] >= 1 and after[1] == 5, f'po wczytaniu: wystawa i pudełka Leitnera zachowane ({after})')

        # ================= 9) TELEFON =================
        mob = await b.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
        merrs = []
        mob.on('pageerror', lambda e: merrs.append(str(e)))
        await start_game(mob)
        await mob.evaluate("() => { game.closeModal(true); game.closeDialog(true); game.setZone('wzgorze'); game.player.x = 5*16; game.player.y = 10*16; ETAP3.cfg.speed = 1; }")
        await mob.wait_for_timeout(500)
        await mob.screenshot(path=f'{OUT}/e3_tel_ogrod.png')
        for name, js in [('oddech', "game.e3Oddech()"), ('staw', "game.e3Staw()"), ('skan', "game.e3Skan()"), ('dzwon', "game.e3Dzwon()"),
                         ('fiszkomat', "(QUESTIONS_DB.slice(0,3).forEach(q => game.state.stats.answeredQuestions[q.id] = true), game.e3Fiszkomat())"),
                         ('krzywa', "game.e3Krzywa()"), ('kapsula', "game.e3Kapsula()"), ('wystawa', "game.e3OpenWystawa()"), ('pianino', "game.e3Pianino()")]:
            await mob.evaluate(f"() => {{ game.closeModal(true); {js}; }}")
            await mob.wait_for_timeout(250)
            over = await mob.evaluate("() => { const p = document.querySelector('#modal .panel'); return p ? p.scrollWidth > p.clientWidth + 2 || p.getBoundingClientRect().right > innerWidth + 1 : 'brak'; }")
            check(over is False, f'telefon: okno „{name}” mieści się na szerokość')
            await mob.screenshot(path=f'{OUT}/e3_tel_{name}.png')
        await mob.evaluate("() => { game.closeModal(true); game.state.energy = 100; game.startMinigame('e3_techniki', 0); }")
        await mob.wait_for_timeout(300)
        await mob.screenshot(path=f'{OUT}/e3_tel_loci.png')
        await mob.evaluate("() => { game.closeModal(true); game.state.energy = 100; game.startMinigame('e3_falszywe', 1); }")
        await mob.wait_for_timeout(300)
        await mob.screenshot(path=f'{OUT}/e3_tel_swiadek.png')
        check(not merrs, f'telefon: brak błędów ({merrs[:3]})')

        check(not errs, f'brak błędów JS ({errs[:5]})')
        await b.close()
    print('\nWYNIK:', 'OK' if not fails else f'{len(fails)} błędów')
    for f in fails:
        print('  -', f)
    sys.exit(1 if fails else 0)

asyncio.run(main())
