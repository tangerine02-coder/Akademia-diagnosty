"""Test Etapu 2 (2026-10-04): pory roku, zadania „znajdź”, trening snu.

Uruchomienie (w folderze repo):
    python3 -m http.server 8765 --directory "Akademia diagnosty" &
    python3 tests/etap2_test.py            # zrzuty ekranu trafiają do tests/out/

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

# rozmowa bez losowych wtrąceń modułu PROFIL (Math.random = 0.99), okno dialogowe otwiera się chwilę później
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

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1100, 'height': 760})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type in ('error', 'warning') and 'ETAP2' in m.text and errs.append(m.text))
        await pg.goto(URL)
        await pg.wait_for_timeout(1500)
        await pg.fill("input[placeholder*='Sylwia']", 'Testerka')
        await pg.click('text=Zamieszkaj w Freudowice Zdrój')
        await pg.wait_for_timeout(1500)
        for _ in range(8):
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(120)
        check(await pg.evaluate('() => !!window.ETAP2'), 'moduł ETAP2 załadowany')

        async def wait_until(js, secs):
            # sen rysuje z filtrem saturate(); bez karty graficznej (headless) to ~3 klatki/s
            for _ in range(int(secs * 10)):
                if await pg.evaluate(js):
                    return True
                await pg.wait_for_timeout(100)
            return False

        async def goto(zone, x, y, t=12 * 60):
            await pg.evaluate(f"""() => {{ game.closeModal(true); game.closeDialog(true);
                game.setZone('{zone}'); game.player.x = {x}; game.player.y = {y}; game.state.time = {t}; }}""")
            await pg.wait_for_timeout(450)

        # ================= 1) PORY ROKU =================
        cal = await pg.evaluate("() => [1, 28, 29, 56, 57, 84, 85, 112, 113].map(d => ETAP2.seasonOfDay(d).id)")
        check(cal == ['jesien', 'jesien', 'zima', 'zima', 'wiosna', 'wiosna', 'lato', 'lato', 'jesien'], f'kalendarz: 28 dni na porę, rok 112 dni ({cal})')
        hud = await pg.evaluate("() => document.getElementById('hud-day').textContent")
        check(hud.startswith('🍂'), f'HUD pokazuje porę roku: {hud!r}')

        # jasność terenu Rynku w każdej porze (zima najjaśniejsza, lato bez zmian)
        lum = {}
        for se in ['lato', 'jesien', 'zima', 'wiosna']:
            await pg.evaluate(f"() => {{ game.e2Data().seasonOverride = '{se}'; game._e2season = '{se}'; game.e2ApplySeason(false); }}")
            await goto('rynek', 20 * 16, 17 * 16)
            lum[se] = await pg.evaluate("""() => { const c = game.zone.ground, d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
              let s = 0, g = 0, n = 0; for (let i = 0; i < d.length; i += 4 * 7) { s += d[i] + d[i+1] + d[i+2]; g += d[i+1] - (d[i] + d[i+2]) / 2; n++; } return [Math.round(s / n), Math.round(g / n)]; }""")
            await pg.screenshot(path=f'{OUT}/e2_rynek_{se}.png')
        print('     jasność / zieleń terenu:', lum)
        check(lum['zima'][0] > lum['lato'][0] + 60, 'zima: teren wyraźnie jaśniejszy (śnieg)')
        check(lum['jesien'][1] < lum['lato'][1], 'jesień: mniej zieleni w trawie')
        check(lum['wiosna'][1] > lum['jesien'][1], 'wiosna: trawa znowu zielona')
        # drzewa zimą przemalowane, budynki z czapą śniegu
        snow = await pg.evaluate("""() => {
          game.e2Data().seasonOverride = 'zima'; game._e2season = 'zima'; game.e2ApplySeason(false);
          const tree = game.zone.objects.find(o => o.type === 'tree' && (o.kind || 'oak') === 'oak'), b = game.zone.buildings[0];
          const t0 = objSprite(tree), t1 = ETAP2.seasonalSprite(t0, tree, 'zima'), b1 = ETAP2.seasonalSprite(b.spr, { type: 'building', b }, 'zima');
          return { tree: t1 !== t0, building: b1 !== b.spr && b1.c.width === b.spr.c.width, same: ETAP2.seasonalSprite(t0, tree, 'zima') === t1 };
        }""")
        check(snow['tree'] and snow['building'] and snow['same'], f'zima: drzewa w szronie, dachy w śniegu, wynik w pamięci podręcznej ({snow})')
        for zone, x, y, se in [('las', 28 * 16, 14 * 16, 'jesien'), ('plaza', 20 * 16, 14 * 16, 'zima'), ('osiedle', 12 * 16, 20 * 16, 'zima'), ('blonia', 20 * 16, 14 * 16, 'wiosna')]:
            await pg.evaluate(f"() => {{ game.e2Data().seasonOverride = '{se}'; game._e2season = '{se}'; game.e2ApplySeason(false); }}")
            await goto(zone, x, y)
            await pg.screenshot(path=f'{OUT}/e2_{zone}_{se}.png')
        parts = await pg.evaluate("""() => { const r = {};
          for (const se of ['jesien', 'zima', 'wiosna', 'lato']) { game.e2Data().seasonOverride = se; game.initParticles(game.zones.rynek); r[se] = game.particles.length ? game.particles[0].kind : 'brak'; }
          return r; }""")
        check(parts['jesien'] == 'leaves' and parts['wiosna'] == 'petals' and parts['zima'] == 'brak', f'cząsteczki pór roku: {parts}')
        inter = await pg.evaluate("() => { game.e2Data().seasonOverride = 'zima'; const c = bakeGround(Object.assign({}, buildZone('rynek'), { id: 'dream:rynek' })); return !!c; }")
        check(inter, 'teren snu i wnętrz nie dostaje pory roku z jawy')
        # automatyczna zmiana pory przy nowym dniu
        auto = await pg.evaluate("""async () => {
          delete game.e2Data().seasonOverride; game._e2season = game.e2Season().id;
          game.state.day = 28; game.closeModal(true); game.closeDialog(true); game.newDay(false);
          for (let i = 0; i < 12 && (game.modalOpen || game.dialog); i++) { game.closeModal(true); game.closeDialog(true); await new Promise(r => setTimeout(r, 80)); }
          await new Promise(r => setTimeout(r, 400));
          return { day: game.state.day, season: game.e2Season().id, applied: game._e2season, toast: document.getElementById('toast').textContent };
        }""")
        check(auto['day'] == 29 and auto['season'] == 'zima' and auto['applied'] == 'zima', f'dzień 29 → zima zastosowana sama ({auto["day"]}, {auto["applied"]})')
        check('Zima' in auto['toast'], f'komunikat o nowej porze: {auto["toast"]!r}')
        await pg.evaluate("() => { game.state.day = 3; game.state.time = 12 * 60; game._e2season = null; }")
        await pg.wait_for_timeout(300)

        # ================= 2) ZADANIA „ZNAJDŹ” =================
        # listonosz: na Osiedlu, zadanie po pierwszej zwykłej rozmowie albo od dnia 2
        await goto('osiedle', 20 * 16, 16 * 16)
        d = await pg.evaluate(TALK, 'listonosz')
        check(bool(d) and any('Pomogę' in o for o in d['options']), f'Listonosz proponuje zadanie: {d and d["options"]}')
        await pg.evaluate("() => game.chooseOption(0)")
        await pg.wait_for_timeout(200)
        st = await pg.evaluate("() => game.e2Quests().listy")
        check(st['state'] == 'active' and [i['zone'] for i in st['items']] == ['rynek', 'bulwar', 'plaza', 'wzgorze'], 'Zgubione listy: 4 listy w 4 dzielnicach')
        chip = await pg.evaluate("() => { const e = document.getElementById('e2-chip'); return e && !e.hidden ? e.textContent : null; }")
        check(chip and '0/4' in chip, f'pasek zadań pokazuje postęp: {chip!r}')
        # każdy przedmiot: osiągalny, nie w ścianie, i da się go podnieść, stojąc obok
        async def collect(qid):
            items = await pg.evaluate(f"() => game.e2Quests().{qid}.items")
            res = []
            for i, it in enumerate(items):
                await goto(it['zone'], it['x'] * 16 + 8, (it['y'] + 1) * 16 + 6)
                r = await pg.evaluate(f"""() => {{
                  const Z = game.zone, it = Z.interacts.find(x => x.kind === 'e2_item' && x.q === '{qid}' && x.i === {i});
                  const obj = Z.objects.find(o => o.type === 'e2_item' && o.x === {it['x']} && o.y === {it['y']});
                  game.player.dir = 'up';
                  const f = game.findInteraction(), prompt = f && f.type === 'spot' && f.it.kind === 'e2_item' ? game.spotPrompt(f.it) : null;
                  const w = Z.w, h = Z.h, seen = new Uint8Array(w * h), q = [];
                  const push = (x, y) => {{ if (x < 0 || y < 0 || x >= w || y >= h || seen[y*w+x] || Z.solid[y*w+x]) return; seen[y*w+x] = 1; q.push([x, y]); }};
                  for (let x = 0; x < w; x++) {{ push(x, 0); push(x, h - 1); }} for (let y = 0; y < h; y++) {{ push(0, y); push(w - 1, y); }}
                  while (q.length) {{ const [x, y] = q.pop(); push(x+1,y); push(x-1,y); push(x,y+1); push(x,y-1); }}
                  const nearWater = [[1,0],[-1,0],[0,1],[0,-1]].some(([dx,dy]) => Z.terrain[({it['y']}+dy)*w + {it['x']}+dx] === 'water');
                  if (f) game.trigger(f);
                  return {{ has: !!it && !!obj, reach: !!seen[{it['y']}*w+{it['x']}], prompt, nearWater, found: game.e2Quests().{qid}.items[{i}].found }};
                }}""")
                await pg.wait_for_timeout(120)
                res.append(r)
            return res
        await goto('rynek', 20 * 16, 17 * 16)
        await pg.screenshot(path=f'{OUT}/e2_list_rynek.png')
        res = await collect('listy')
        check(all(r['has'] for r in res), 'listy leżą w swoich dzielnicach')
        check(all(r['reach'] for r in res), 'do każdego listu da się dojść')
        check(all(r['prompt'] == 'Podnieś list' for r in res), f'podpowiedź przy liście: {[r["prompt"] for r in res]}')
        check(all(r['found'] for r in res), 'wszystkie 4 listy podniesione Spacją')
        money0 = await pg.evaluate("() => game.state.money")
        await goto('osiedle', 20 * 16, 16 * 16)
        await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'listonosz'); game.player.x = n.x; game.player.y = n.y + 14; }")
        d = await pg.evaluate(TALK, 'listonosz')
        st = await pg.evaluate("() => game.e2Quests().listy")
        money1 = await pg.evaluate("() => game.state.money")
        check(st['state'] == 'done' and money1 - money0 == 25, f'oddanie listów: +25 🟡 ({money1 - money0})')
        check(bool(d) and any('Zeigarnik' in pg_ for pg_ in d['pages']), 'Listonosz opowiada o efekcie Zeigarnik')
        d = await pg.evaluate(TALK, 'listonosz')
        check(not d or not any('Pomogę' in o for o in d['options']), 'zadanie z listami nie wraca drugi raz')

        # rybak: spławiki przy wodzie
        await goto('port', 27 * 16, 21 * 16)
        await pg.evaluate("() => game.chooseOption && game.closeDialog(true)")
        d = await pg.evaluate(TALK, 'rybak')
        check(bool(d) and any('spławik' in o.lower() for o in d['options']), 'Rybak proponuje szukanie spławików')
        await pg.evaluate("() => game.chooseOption(0)")
        res = await collect('splawiki')
        check(all(r['nearWater'] for r in res), 'każdy spławik leży przy wodzie')
        check(all(r['found'] and r['reach'] for r in res), 'spławiki osiągalne i podniesione')
        await goto('port', 27 * 16, 21 * 16)
        d = await pg.evaluate(TALK, 'rybak')
        check(bool(d) and any('Langer' in x for x in d['pages']), 'Rybak: złudzenie kontroli (Langer, 1975)')

        # Ida: chowany (codziennie)
        await goto('plaza', 13 * 16, 16 * 16)
        d = await pg.evaluate(TALK, 'ida')
        check(bool(d) and any('Szukam' in o for o in d['options']), 'Ida proponuje chowanego')
        await pg.evaluate("() => game.chooseOption(0)")
        await pg.wait_for_timeout(150)
        hidden = await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'ida'); return n ? !game.npcVisible(n) : null; }")
        check(hidden is True, 'Ida znika z plaży')
        ch = await pg.evaluate("() => game.e2Quests().chowany.items[0]")
        check(ch['zone'] in ['rynek', 'osiedle', 'bulwar', 'blonia', 'wzgorze', 'port'], f'Ida chowa się w mieście: {ch["zone"]}')
        await goto(ch['zone'], ch['x'] * 16 + 8, (ch['y'] + 2) * 16)
        await pg.screenshot(path=f'{OUT}/e2_ida_schowana.png')
        money0 = await pg.evaluate("() => game.state.money")
        res = await collect('chowany')
        await pg.wait_for_timeout(200)
        st = await pg.evaluate("() => game.e2Quests().chowany")
        money1 = await pg.evaluate("() => game.state.money")
        dl = await pg.evaluate("() => game.dialog && game.dialog.pages")
        check(st['state'] == 'done' and st['n'] == 1 and money1 - money0 == 10, f'Ida znaleziona: +10 🟡 ({money1 - money0})')
        check(bool(dl) and any('Piaget' in x for x in dl), 'Ida: stałość przedmiotu (Piaget)')
        await goto('plaza', 13 * 16, 16 * 16)
        vis = await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'ida'); return game.npcVisible(n); }")
        d = await pg.evaluate(TALK, 'ida')
        check(vis and (not d or not any('Szukam' in o for o in d['options'])), 'Ida wraca na plażę; drugi raz tego samego dnia nie proponuje')
        await pg.evaluate("() => { game.state.day += 1; }")
        d = await pg.evaluate(TALK, 'ida')
        check(bool(d) and any('Szukam' in o for o in d['options']), 'następnego dnia znowu chowany')
        await pg.evaluate("() => game.chooseOption(0)")
        money0 = await pg.evaluate("() => game.state.money")
        await collect('chowany')
        money1 = await pg.evaluate("() => game.state.money")
        check(money1 - money0 == 3, f'kolejne chowane: mniejsza nagroda (+{money1 - money0} 🟡)')
        # nieznaleziona Ida następnego dnia wraca na plażę
        await pg.evaluate("() => { game.state.day += 1; }")
        await goto('plaza', 13 * 16, 16 * 16)
        await pg.evaluate(TALK, 'ida')
        await pg.evaluate("() => game.chooseOption(0)")
        await pg.evaluate("() => { game.closeDialog(true); game.state.day += 1; }")
        await goto('plaza', 13 * 16, 16 * 16)
        back = await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'ida'); return { vis: game.npcVisible(n), st: game.e2Quests().chowany.state }; }")
        check(back['vis'] and back['st'] is None, f'nieznaleziona Ida rano wraca na plażę ({back})')

        # Morfeusza: senne motyle, nagroda w LP
        await goto('wyspa_snu', 18 * 16, 12 * 16)
        lp0 = await pg.evaluate("() => game.dreamData().lp")
        d = await pg.evaluate(TALK, 'morfeusza')
        check(bool(d) and any('Złapię' in o for o in d['options']), 'Morfeusza proponuje szukanie sennych motyli')
        await pg.evaluate("() => game.chooseOption(0)")
        st = await pg.evaluate("() => game.e2Quests().sny.items")
        a, b2 = st[0], st[2]
        check(abs(a['x'] - b2['x']) + abs(a['y'] - b2['y']) >= 8, 'dwa motyle na Wyspie Snu nie leżą obok siebie')
        glow = await pg.evaluate("() => game.zone.lights.filter(l => l.e2).length")
        check(glow == 2, f'senne motyle świecą nocą ({glow} światła)')
        await goto('wyspa_snu', a['x'] * 16 + 8, (a['y'] + 2) * 16, 22 * 60)
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'{OUT}/e2_motyl_noc.png')
        res = await collect('sny')
        await goto('wyspa_snu', 18 * 16, 12 * 16)
        await pg.evaluate("() => { const n = game.npcs.find(x => x.id === 'morfeusza'); game.player.x = n.x; game.player.y = n.y + 14; }")
        await pg.evaluate(TALK, 'morfeusza')
        lp1 = await pg.evaluate("() => game.dreamData().lp")
        check(lp1 - lp0 == 10, f'senne motyle: +10 LP ({lp1 - lp0})')
        save = await pg.evaluate("() => { game.save(); return JSON.parse(localStorage.getItem('akademia_freudowice_v1')).e2; }")
        check(bool(save) and save['q']['listy']['state'] == 'done' and save['q']['chowany']['n'] == 2, 'stan zadań jest w zapisie gry')

        # ================= 3) TRENING SNU =================
        await pg.evaluate("() => { game.closeModal(true); game.closeDialog(true); game.dreamData().daily.trainingDay = 0; game.state.time = 22 * 60; }")
        await goto('dom', 7 * 16, 6 * 16, 22 * 60)
        await pg.evaluate("() => game.enterModulatedDream('rynek', {}, 'bed')")
        await wait_until("() => game.zone && game.zone.id === 'dream:rynek' && !game.transition", 40)
        info = await pg.evaluate("""() => { const s = game.dreamSession(), P = s && s.e2;
          return P ? { zone: game.zone.id, n: P.changes.length, kinds: P.changes.map(c => c.kind), limit: P.limit, npcs: game.npcs.length,
            still: game.npcs.every(n => !n.def.wander), wskaz: game.zone.interacts.filter(i => i.kind === 'e2_wskaz').length } : null; }""")
        print('     sen:', info)
        check(bool(info) and info['zone'] == 'dream:rynek', 'wejście w sen z łóżka')
        check(bool(info) and info['n'] == 2 and info['limit'] == 90, 'dzień 0 treningu: 2 zmiany, 1:30 snu')
        check(bool(info) and info['npcs'] > 0 and info['still'], 'we śnie są mieszkańcy dzielnicy i stoją w miejscu')
        check(bool(info) and info['wskaz'] > 5, 'przedmioty we śnie da się wskazać')
        await wait_until("() => game.dreamSession().e2.briefed && game.dreamSession().e2.left < 89.5", 15)
        await pg.screenshot(path=f'{OUT}/e2_sen_mgla.png')
        brief = await pg.evaluate("() => document.getElementById('toast').textContent")
        check('W tym śnie' in brief, f'instrukcja na początku snu: {brief[:60]!r}')
        left = await pg.evaluate("() => game.dreamSession().e2.left")
        check(left < 90, f'czas snu płynie ({left:.1f} s)')
        # każdy rodzaj zmiany da się wylosować; do zrzutów składamy po jednej z każdego rodzaju
        kinds = await pg.evaluate("""() => { const s = game.dreamSession(), seen = {};
          for (let i = 0; i < 60; i++) { const P = game.e2DreamPlan(game.zone, s); P.changes.forEach(c => { if (!seen[c.kind]) seen[c.kind] = c; }); }
          return seen; }""")
        check(set(kinds) == {'napis', 'kolor', 'postac', 'obiekt', 'przedmiot'}, f'rodzaje zmian: {sorted(kinds)}')
        # wskazanie niezmienionej rzeczy
        nope = await pg.evaluate("""() => { const s = game.dreamSession(), P = s.e2;
          const used = new Set(P.changes.filter(c => c.kind === 'obiekt').map(c => c.otype + c.x + ',' + c.y));
          const it = game.zone.interacts.find(i => i.kind === 'e2_wskaz' && i.obj.type !== 'e2_dreamitem' && !used.has(i.obj.type + i.obj.x + ',' + i.obj.y));
          game._e2nope = 0; game.trigger({ type: 'spot', it }); return { toast: document.getElementById('toast').textContent, modal: game.modalOpen, found: P.changes.filter(c => c.found).length }; }""")
        check('tak samo' in nope['toast'] and not nope['modal'] and nope['found'] == 0, f'niezmieniona rzecz: {nope["toast"]!r}')
        # trafienia: +20 s i +5 LP za każdą zmianę
        hits = await pg.evaluate("""async () => { const s = game.dreamSession(), P = s.e2, out = [];
          for (let idx = 0; idx < P.changes.length; idx++) {
            const c = P.changes[idx], left0 = P.left, lp0 = game.dreamData().lp; let it = null;
            if (c.kind === 'napis' || c.kind === 'kolor') it = { type: 'door', b: game.zone.buildings.find(b => b.id === c.bid) };
            else if (c.kind === 'postac') it = { type: 'npc', n: game.npcs.find(n => n.id === c.npc) };
            else if (c.kind === 'obiekt') it = { type: 'spot', it: game.zone.interacts.find(i => i.kind === 'e2_wskaz' && i.obj.type === c.otype && i.obj.x === c.x && i.obj.y === c.y) };
            else it = { type: 'spot', it: game.zone.interacts.find(i => i.kind === 'e2_wskaz' && i.obj.type === 'e2_dreamitem') };
            game.trigger(it);
            out.push({ kind: c.kind, found: !!c.found, dt: Math.round(P.left - left0), dlp: game.dreamData().lp - lp0 });
          }
          return out; }""")
        print('     trafienia:', hits)
        check(all(h['found'] for h in hits), 'wszystkie zmiany rozpoznane')
        check(all(h['dt'] >= 19 for h in hits), 'każde trafienie wydłuża sen o 20 s (ostatnie o 60 s)')
        check(all(h['dlp'] == 5 for h in hits), 'każde trafienie: +5 LP')
        await pg.wait_for_timeout(4800)
        tr = await pg.evaluate("() => ({ days: game.dreamDays(), session: !!game.dreamSession(), allDone: game.dreamSession() && game.dreamSession().e2.allDone })")
        check(tr['days'] == 1 and tr['session'] and tr['allDone'], f'wszystkie zmiany = dzień treningowy ({tr})')
        await pg.evaluate("() => game.openDreamTasks()")
        card = await pg.evaluate("() => { const c = document.getElementById('e2-dream-card'); return c ? c.textContent : ''; }")
        check('Co się zmieniło' in card and '✓' in card, 'okno zadań snu: karta „co się zmieniło” z listą znalezionych')
        await pg.screenshot(path=f'{OUT}/e2_sen_zadania.png')
        await pg.evaluate("() => game.closeModal(true)")
        # zrzuty: po jednej zmianie każdego rodzaju naraz
        await pg.evaluate("""(kinds) => { const s = game.dreamSession();
          s.e2.changes = Object.values(kinds).map(c => Object.assign({}, c, { found: false })); s.e2.allDone = false;
          game.rebuildDream(); }""", kinds)
        shots = await pg.evaluate("""() => game.dreamSession().e2.changes.map(c => {
          if (c.bid) { const b = game.zone.buildings.find(x => x.id === c.bid); return [c.kind, b.doorCol, b.doorRow + 2]; }
          if (c.npc) { const n = game.npcs.find(x => x.id === c.npc); return [c.kind, Math.floor(n.x / 16), Math.floor(n.y / 16) + 2]; }
          return [c.kind, c.x, c.y + 2]; })""")
        for kind, x, y in shots:
            await pg.evaluate(f"() => {{ game.player.x = {x} * 16 + 8; game.player.y = {y} * 16 + 8; game.unstick(); }}")
            await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'{OUT}/e2_sen_{kind}.png')
        npcLook = await pg.evaluate("""() => { const c = game.dreamSession().e2.changes.find(c => c.kind === 'postac'); const n = game.npcs.find(x => x.id === c.npc);
          return n.def.look.hairC === c.look.hairC && NPCS[c.npc].look.hairC !== c.look.hairC; }""")
        check(npcLook, 'zmieniony wygląd postaci tylko we śnie (oryginał nietknięty)')
        # wysoki poziom: mniej mgły, dłuższy sen, więcej zmian
        lvl = await pg.evaluate("""() => { const d = game.dreamData(), keep = d.trainingDays.slice();
          d.trainingDays = [1, 2, 3, 4, 5, 6, 7]; const P = game.e2DreamPlan(game.zone, game.dreamSession()), r = { n: P.changes.length, limit: P.limit, clarity: game.dreamClarity() };
          d.trainingDays = keep; return r; }""")
        check(lvl['n'] == 5 and lvl['limit'] == 300, f'7 dni treningu: 5 zmian, 5:00 snu ({lvl})')
        # koniec czasu: postać się budzi (z łóżka = nowy dzień)
        day0 = await pg.evaluate("() => game.state.day")
        await pg.evaluate("() => { game.closeModal(true); game.closeDialog(true); game.dreamSession().e2.left = 0.3; }")
        await pg.wait_for_timeout(2500)
        for _ in range(10):
            await pg.evaluate("() => { game.closeModal(true); game.closeDialog(true); }")
            await pg.wait_for_timeout(120)
        woke = await pg.evaluate("() => ({ session: !!game.dreamSession(), day: game.state.day, zone: game.zone.id })")
        check(not woke['session'] and woke['day'] == day0 + 1, f'po czasie sen się kończy, a po nocy jest nowy dzień ({woke})')
        await pg.screenshot(path=f'{OUT}/e2_po_snie.png')

        # ================= 4) PANEL TESTERKI, ZAPIS =================
        await pg.evaluate("() => game.openTesterPanel()")
        has = await pg.evaluate("() => document.querySelectorAll('#modal [data-e2season]').length")
        check(has == 5, 'panel testerki: przełącznik pór roku')
        await pg.evaluate("() => document.querySelector('#modal [data-e2season=\"zima\"]').click()")
        await pg.wait_for_timeout(200)
        ov = await pg.evaluate("() => game.e2Data().seasonOverride")
        check(ov == 'zima', 'panel testerki ustawia porę roku ręcznie')
        await pg.evaluate("() => { document.querySelector('#modal [data-e2season=\"auto\"]').click(); game.closeModal(true); }")
        check(not errs, 'brak błędów JS: ' + '; '.join(errs[:3]))
        await b.close()
    print('\nWYNIK:', 'wszystko OK' if not fails else f'{len(fails)} błędów')
    sys.exit(1 if fails else 0)

asyncio.run(main())
