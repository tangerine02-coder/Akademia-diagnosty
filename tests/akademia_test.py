"""Test Etapu 7 (2026-10-19): wejście do Akademii — konto, mail z linkiem, kod, paczka, panel admina.

Uruchomienie (w folderze repo):
    python3 tests/akademia_test.py

Test sam buduje folder strona/ (narzedzia/zbuduj_strone.py) i sam włącza serwer na porcie 8766.
Firebase jest udawany (tests/fake_firebase/ zamiast modułów z gstatic.com), z uproszczoną kopią
reguł bazy — prawdziwe reguły sprawdza emulator: firebase/testy/reguly.test.mjs.
Zrzuty ekranu trafiają do tests/out/.
"""
import asyncio, base64, gzip, hashlib, json, os, re, subprocess, sys, time, urllib.request
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, 'tests')
FAKE = os.path.join(TESTS, 'fake_firebase')
OUT = os.path.join(TESTS, 'out')
os.makedirs(OUT, exist_ok=True)
PORT = 8766
BASE = f'http://localhost:{PORT}/strona/'
AKAD = os.path.join(ROOT, 'Akademia diagnosty', 'akademia_diagnosty_miasteczko.html')
PUBL = os.path.join(ROOT, 'Akademia diagnosty', 'akademia_diagnosty_publiczna.html')
KONFIG = "export default { apiKey: 'test', authDomain: 'demo-akademia.firebaseapp.com', projectId: 'demo-akademia', appId: 'test' };"
DZIEN = 86400 * 1000
fails = []


def check(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)


def stan_poczatkowy():
    """Baza na start: admin, lista uczelni, paczka Akademii (jak po wgraniu w panelu) i kilka kodów."""
    teraz = int(time.time() * 1000)
    html = open(AKAD, 'rb').read()
    gz = gzip.compress(html, 9)
    sha = hashlib.sha256(html).hexdigest()
    pref, N = 'p' + sha[:12], 700000
    docs = {
        'admini/uidADMIN': {'imie': 'Sylwia'},
        'config/uczelnie': {'domeny': ['umk.pl', 'uni.lodz.pl']},
        'akademia/info': {'wersja': 'test-1', 'prefiks': pref, 'czesci': (len(gz) + N - 1) // N, 'sha256': sha,
                          'rozmiar': len(html), 'spakowana': len(gz), 'plik': 'akademia_diagnosty_miasteczko.html', 'wgrano': {'__t': teraz}},
    }
    for i in range(0, len(gz), N):
        docs[f'akademia/{pref}-{i // N}'] = {'dane': {'__b': base64.b64encode(gz[i:i + N]).decode()}}

    def kod(typ, etykieta, za=30 * DZIEN, uzyty=False, przez=None):
        return {'typ': typ, 'etykieta': etykieta, 'waznyDo': {'__t': teraz + za}, 'uzyty': uzyty, 'uzytyPrzez': przez,
                'uzytyKiedy': {'__t': teraz} if uzyty else None, 'utworzono': {'__t': teraz - DZIEN}}
    docs['kody/AAAABBBBCCCC'] = kod('student', 'UMK, psychologia, II rok')
    docs['kody/DDDDEEEEFFFF'] = kod('absolwent', 'Absolwenci psychologii')
    docs['kody/UUUUVVVVWWWW'] = kod('student', 'Zużyty', uzyty=True, przez='uidSTARY')
    docs['kody/EEEEFFFFGGGG'] = kod('student', 'Po terminie', za=-DZIEN)
    docs['studenci/uidSTARY'] = {'email': 'stary@stud.umk.pl', 'kod': 'UUUUVVVVWWWW', 'typ': 'student', 'etykieta': 'Zużyty', 'domena': 'umk.pl', 'kiedy': {'__t': teraz - DZIEN}}
    users = {
        'uidADMIN': {'email': 'sylwia@umk.pl', 'haslo': 'haslo-admina-1', 'emailVerified': True, 'tokenEV': True, 'lastSignIn': teraz},
        'uidSTARY': {'email': 'stary@stud.umk.pl', 'haslo': 'stare-haslo-1', 'emailVerified': True, 'tokenEV': True, 'lastSignIn': teraz},
    }
    return json.dumps({'users': users, 'current': None, 'docs': docs, 'mails': [], 'seq': 1})


STAN = None
IDB_ILE = """() => new Promise(ok => { const r = indexedDB.open('akademia-diagnosty', 1);
  r.onupgradeneeded = () => r.result.createObjectStore('paczka');
  r.onsuccess = () => { const q = r.result.transaction('paczka').objectStore('paczka').count(); q.onsuccess = () => ok(q.result); q.onerror = () => ok(-1); };
  r.onerror = () => ok(-1); })"""


async def kontekst(b, konfig=True, viewport=None):
    ctx = await b.new_context(viewport=viewport or {'width': 1100, 'height': 760})

    async def gstatic(route):
        name = route.request.url.split('?')[0].rsplit('/', 1)[-1]
        path = os.path.join(FAKE, name)
        if os.path.exists(path):
            await route.fulfill(path=path, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/javascript'})
        else:
            await route.fulfill(status=404, body='', headers={'Access-Control-Allow-Origin': '*'})
    await ctx.route(re.compile(r'https://www\.gstatic\.com/firebasejs/.*'), gstatic)
    await ctx.route(re.compile(r'https://fonts\.(googleapis|gstatic)\.com/.*'), lambda r: r.fulfill(status=200, body='', headers={'Access-Control-Allow-Origin': '*'}))
    if konfig:
        await ctx.route(re.compile(r'.*/strona/firebase-config\.js$'), lambda r: r.fulfill(body=KONFIG, headers={'Content-Type': 'application/javascript'}))
    return ctx


async def nowa_strona(ctx, errs):
    pg = await ctx.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)))
    return pg


async def zasiej(pg):
    await pg.goto(BASE + 'uczelnie-start.json')
    await pg.evaluate("s => { localStorage.clear(); localStorage.setItem('__fakefb', s); }", STAN)


async def czekaj(pg, tekst, timeout=10000):
    try:
        await pg.wait_for_function("t => document.body && document.body.innerText.includes(t)", arg=tekst, timeout=timeout)
        return True
    except Exception:
        return False


async def stan(pg):
    return await pg.evaluate("() => JSON.parse(localStorage.getItem('__fakefb'))")


async def ramka(pg, timeout=30000):
    await pg.wait_for_function("() => { const f = document.getElementById('gra'); return f && !f.hidden && f.contentWindow && f.contentWindow.game; }", timeout=timeout)
    return await (await pg.query_selector('#gra')).content_frame()


async def start_game(pg, url):
    await pg.goto(url)
    await pg.wait_for_timeout(1500)
    await pg.fill("input[placeholder*='Sylwia']", 'Testerka')
    await pg.click('text=Zamieszkaj w Freudowice Zdrój')
    await pg.wait_for_timeout(1500)
    for _ in range(8):
        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(80)


async def student(b):
    errs = []
    ctx = await kontekst(b)
    pg = await nowa_strona(ctx, errs)
    await zasiej(pg)

    print('\n[S1] Wersja publiczna: przycisk 🎓 Akademia')
    await start_game(pg, BASE + 'index.html')
    r = await pg.evaluate("() => { const b = document.getElementById('t-akademia'); if (!b) return null; game.closeModal(true); game.closeDialog(true); b.click(); return document.getElementById('modal').innerText; }")
    check(bool(r) and 'Zaloguj się do Akademii' in r and 'kod od prowadzącego' in r, 'w wersji publicznej 🎓 opisuje Akademię i prowadzi do logowania')
    await pg.screenshot(path=f'{OUT}/e7_pub_panel.png')
    await pg.click('#e7-wejdz')
    await pg.wait_for_url(re.compile(r'.*/akademia\.html$'))
    check(await czekaj(pg, 'Mam konto'), 'akademia.html: ekran logowania')
    r = await pg.evaluate("() => !!localStorage.getItem('akademia_freudowice_publiczna_v1')")
    check(r, 'gra zapisała postęp przed przejściem do Akademii')
    await pg.screenshot(path=f'{OUT}/e7_logowanie.png')

    print('\n[S2] Nowe konto i potwierdzenie adresu')
    await pg.click('[data-z=nowe]')
    await pg.fill('#n-email', '123456@stud.umk.pl')
    check('Adres uczelni' in await pg.inner_text('#n-domena'), 'podpowiedź: adres uczelni')
    await pg.fill('#n-haslo', 'krotkie')
    await pg.fill('#n-haslo2', 'krotkie')
    await pg.click('#f-nowe [type=submit]')
    check(await czekaj(pg, 'Hasło jest za krótkie'), 'za krótkie hasło: komunikat po polsku')
    await pg.fill('#n-haslo', 'tajne-haslo-1')
    await pg.fill('#n-haslo2', 'tajne-haslo-2')
    await pg.click('#f-nowe [type=submit]')
    check(await czekaj(pg, 'Hasła się różnią'), 'różne hasła: komunikat')
    await pg.fill('#n-haslo2', 'tajne-haslo-1')
    await pg.click('#f-nowe [type=submit]')
    check(await czekaj(pg, 'Potwierdź adres e-mail'), 'po założeniu konta: prośba o kliknięcie linku')
    s = await stan(pg)
    uid = s['current']
    check(any(m['email'] == '123456@stud.umk.pl' and m['typ'] == 'potwierdzenie' and str(m['url']).endswith('/strona/akademia.html') for m in s['mails']),
          'mail z linkiem wysłany, link wraca do akademia.html')
    await pg.click('#p-spr')
    check(await czekaj(pg, 'Jeszcze nie widać potwierdzenia'), 'przed kliknięciem linku: jeszcze nie')
    await pg.evaluate("() => __fakefb.potwierdz('123456@stud.umk.pl')")
    await pg.click('#p-spr')
    check(await czekaj(pg, 'Ostatni krok'), 'po kliknięciu linku: ekran kodu')
    s = await stan(pg)
    check(s['users'][uid]['tokenEV'] is True, 'token odświeżony — baza widzi potwierdzony adres')
    check('adres uczelni' in await pg.inner_text('#k-dom'), 'ekran kodu: adres uczelni ✓')
    await pg.screenshot(path=f'{OUT}/e7_kod.png')

    print('\n[S3] Kod od prowadzącego')
    for kod, oczek, opis in [('abc', 'Kod ma 12 znaków', 'zły format'), ('UUUU-VVVV-WWWW', 'został już użyty', 'kod użyty'),
                             ('EEEE FFFF GGGG', 'stracił ważność', 'kod po terminie'), ('ZZZZ-YYYY-XXXX', 'Nie ma takiego kodu', 'nieistniejący kod')]:
        await pg.fill('#k-kod', kod)
        await pg.click('#f-kod [type=submit]')
        check(await czekaj(pg, oczek), f'{opis}: „{oczek}”')
    await pg.fill('#k-kod', 'aaaa-bbbb-cccc')
    await pg.click('#f-kod [type=submit]')
    check(await czekaj(pg, 'Przenieść postęp?', 30000), 'dobry kod (małe litery też): wejście i pytanie o postęp')
    s = await stan(pg)
    st, kd = s['docs'].get(f'studenci/{uid}'), s['docs']['kody/AAAABBBBCCCC']
    check(bool(st) and st['typ'] == 'student' and st['domena'] == 'umk.pl' and st['etykieta'] == 'UMK, psychologia, II rok' and st['email'] == '123456@stud.umk.pl',
          f'dokument w studenci: typ, opis i domena z kodu ({st})')
    check(kd['uzyty'] is True and kd['uzytyPrzez'] == uid, 'kod zużyty i przypisany do konta')
    await pg.screenshot(path=f'{OUT}/e7_postep.png')

    print('\n[S4] Przeniesienie postępu i gra w ramce')
    await pg.click('#z-tak')
    fr = await ramka(pg)
    r = await fr.evaluate("() => ({ w: WERSJA, created: game.state.created, name: game.state.player.name, n: QUESTIONS_DB.length })")
    check(r['w'] == 'akademicka' and r['created'] and r['name'] == 'Testerka' and r['n'] == 215, f'w ramce wersja akademicka z przeniesionym postępem ({r})')
    r = await pg.evaluate("() => [!!localStorage.getItem('akademia_freudowice_v1'), localStorage.getItem('ad_akademia_postep_zapytano'), document.getElementById('ekran').hidden]")
    check(r == [True, '1', True], f'zapis Akademii założony, pytanie zapamiętane, ekran logowania schowany ({r})')
    await pg.wait_for_timeout(600)
    await pg.screenshot(path=f'{OUT}/e7_akademia_gra.png')

    print('\n[S5] 🎓 w Akademii: konto i wylogowanie')
    r = await fr.evaluate("() => { game.closeModal(true); game.closeDialog(true); document.getElementById('t-akademia').click(); return document.getElementById('modal').innerText; }")
    check('123456@stud.umk.pl' in r and 'UMK, psychologia, II rok' in r and 'Wyloguj' in r and 'Konto i dane' in r, 'panel 🎓 w Akademii: konto, opis kodu, wylogowanie')
    await pg.screenshot(path=f'{OUT}/e7_akademia_panel.png')
    await fr.click('#e7-out')
    check(await czekaj(pg, 'Mam konto'), 'po wylogowaniu: ekran logowania')
    r = await pg.evaluate(IDB_ILE)
    s = await stan(pg)
    check(r == 0 and s['current'] is None, f'wylogowanie czyści kopię Akademii w przeglądarce ({r})')

    print('\n[S6] Ponowne logowanie: od razu do Akademii')
    await pg.fill('#l-email', '123456@stud.umk.pl')
    await pg.fill('#l-haslo', 'zle-haslo')
    await pg.click('#f-login [type=submit]')
    check(await czekaj(pg, 'Zły e-mail albo hasło'), 'złe hasło: komunikat')
    await pg.fill('#l-haslo', 'tajne-haslo-1')
    await pg.click('#f-login [type=submit]')
    fr = await ramka(pg)
    r = await fr.evaluate("() => [WERSJA, game.state.player.name]")
    check(r == ['akademicka', 'Testerka'], f'bez pytania o postęp, ten sam zapis Akademii ({r})')
    check(await pg.evaluate(IDB_ILE) == 1, 'kopia Akademii w przeglądarce (kolejne wejścia bez pobierania)')

    print('\n[S7] Konto i dane: usunięcie konta')
    await pg.goto(BASE + 'akademia.html?konto')
    check(await czekaj(pg, 'Twoje konto'), 'akademia.html?konto: ekran konta')
    check('UMK, psychologia, II rok' in await pg.inner_text('#tresc'), 'ekran konta: opis kodu')
    await pg.screenshot(path=f'{OUT}/e7_konto.png')
    await pg.click('#a-usun')
    check(await czekaj(pg, 'Na pewno?'), 'usunięcie wymaga drugiego kliknięcia')
    await pg.click('#a-usun')
    check(await czekaj(pg, 'zostały usunięte'), 'konto usunięte: komunikat')
    s = await stan(pg)
    check(uid not in s['users'] and f'studenci/{uid}' not in s['docs'] and await pg.evaluate(IDB_ILE) == 0, 'w bazie nie ma konta ani dostępu, kopia usunięta')
    check(not errs, f'bez błędów JavaScript ({errs[:3]})')
    await ctx.close()


async def absolwent(b):
    errs = []
    ctx = await kontekst(b)
    pg = await nowa_strona(ctx, errs)
    await zasiej(pg)

    print('\n[A1] Adres spoza uczelni')
    await pg.goto(BASE + 'akademia.html')
    await czekaj(pg, 'Mam konto')
    await pg.click('[data-z=nowe]')
    await pg.fill('#n-email', 'ktos@gmail.com')
    check('nie wygląda na adres uczelni' in await pg.inner_text('#n-domena'), 'podpowiedź: adres spoza uczelni, tylko kod absolwenta')
    await pg.fill('#n-haslo', 'haslo-absolwenta')
    await pg.fill('#n-haslo2', 'haslo-absolwenta')
    await pg.click('#f-nowe [type=submit]')
    await czekaj(pg, 'Potwierdź adres e-mail')
    await pg.evaluate("() => __fakefb.potwierdz('ktos@gmail.com')")
    await pg.click('#p-spr')
    check(await czekaj(pg, 'Ostatni krok'), 'po potwierdzeniu: ekran kodu')
    check('spoza uczelni' in await pg.inner_text('#k-dom'), 'ekran kodu: adres spoza uczelni')
    await pg.fill('#k-kod', 'AAAA-BBBB-CCCC')
    await pg.click('#f-kod [type=submit]')
    check(await czekaj(pg, 'wymaga adresu e-mail uczelni'), 'kod studenta z adresem spoza uczelni: odmowa z wyjaśnieniem')
    r = await pg.evaluate("""async () => { const K = await import('./konto.js'); const k = await K.sprawdzKod('AAAABBBBCCCC');
      const F = await import('https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js'); const db = F.getFirestore(); const u = K.uzytkownik();
      const b = F.writeBatch(db);
      b.set(F.doc(db, 'studenci', u.uid), { email: u.email, kod: k.kod, typ: k.typ, etykieta: k.etykieta, domena: 'umk.pl', kiedy: F.serverTimestamp() });
      b.update(F.doc(db, 'kody', k.kod), { uzyty: true, uzytyPrzez: u.uid, uzytyKiedy: F.serverTimestamp() });
      try { await b.commit(); return 'przeszło'; } catch (e) { return e.code; } }""")
    check(r == 'permission-denied', f'obejście sprawdzania w przeglądarce: baza i tak odmawia ({r})')

    print('\n[A2] Kod absolwenta')
    await pg.fill('#k-kod', 'DDDD-EEEE-FFFF')
    await pg.click('#f-kod [type=submit]')
    fr = await ramka(pg)
    r = await fr.evaluate("() => [WERSJA, game.state.created]")
    check(r == ['akademicka', False], f'absolwent z dowolnym adresem wchodzi; bez postępu z wersji publicznej — nowa postać ({r})')
    s = await stan(pg)
    st = s['docs'].get('studenci/' + s['current'])
    check(bool(st) and st['typ'] == 'absolwent' and st['domena'] == '', f'dokument w studenci: absolwent ({st})')
    check(not errs, f'bez błędów JavaScript ({errs[:3]})')
    await ctx.close()


async def admin(b):
    errs = []
    ctx = await kontekst(b)
    pg = await nowa_strona(ctx, errs)
    await zasiej(pg)

    print('\n[P1] Panel admina: logowanie i kody')
    await pg.goto(BASE + 'admin.html')
    await czekaj(pg, 'Panel dla autorki')
    await pg.fill('#email', 'sylwia@umk.pl')
    await pg.fill('#haslo', 'haslo-admina-1')
    await pg.click('#f [type=submit]')
    check(await czekaj(pg, 'Nowe kody'), 'admin widzi panel')
    check(await czekaj(pg, 'stary@stud.umk.pl'), 'lista kodów: użyty kod z adresem osoby')
    await pg.fill('#n', '3')
    await pg.select_option('#typ', 'pracownik')
    await pg.fill('#opis', 'Kadra testowa')
    await pg.click('#gen')
    check(await czekaj(pg, 'Gotowe: 3 nowych kodów'), 'wygenerowane 3 kody')
    kody = (await pg.input_value('#lista-nowych')).split('\n')
    check(len(kody) == 3 and all(re.fullmatch(r'[A-HJKMNP-Z2-9]{4}-[A-HJKMNP-Z2-9]{4}-[A-HJKMNP-Z2-9]{4}', k) for k in kody), f'kody w zapisie XXXX-XXXX-XXXX ({kody})')
    s = await stan(pg)
    nowe = {p: d for p, d in s['docs'].items() if p.startswith('kody/') and d.get('etykieta') == 'Kadra testowa'}
    check(len(nowe) == 3 and all(d['typ'] == 'pracownik' and d['uzyty'] is False for d in nowe.values()), 'w bazie 3 wolne kody dla pracowników')
    await pg.screenshot(path=f'{OUT}/e7_admin_kody.png', full_page=True)
    pierwszy = kody[0].replace('-', '')
    await pg.wait_for_selector(f'[data-uniewaznij="{pierwszy}"]')
    await pg.click(f'[data-uniewaznij="{pierwszy}"]')
    await pg.wait_for_function("k => !document.querySelector(`[data-uniewaznij=\"${k}\"]`)", arg=pierwszy)
    s = await stan(pg)
    check(s['docs'][f'kody/{pierwszy}']['waznyDo']['__t'] <= time.time() * 1000 + 1000, 'unieważniony kod traci ważność')

    print('\n[P2] Uczelnie')
    await pg.click('[data-z=uczelnie]')
    await pg.wait_for_function("() => document.getElementById('domeny') && document.getElementById('domeny').value.includes('umk.pl')")
    await pg.click('#start')
    check(await czekaj(pg, 'Dołączone'), 'lista startowa dołączona')
    await pg.click('#zapisz')
    check(await czekaj(pg, 'Zapisane:'), 'lista zapisana')
    s = await stan(pg)
    d = s['docs']['config/uczelnie']['domeny']
    check(len(d) >= 30 and 'kul.pl' in d and 'umk.pl' in d and d == sorted(d), f'w bazie lista domen ({len(d)})')

    print('\n[P3] Paczka Akademii')
    await pg.click('[data-z=paczka]')
    check(await czekaj(pg, 'test-1'), 'paczka: obecna wersja')
    await pg.set_input_files('#plik', PUBL)
    await pg.click('#wgraj')
    check(await czekaj(pg, 'To nie jest plik wersji akademickiej'), 'wersji publicznej nie da się wgrać jako paczki')
    zmieniony = os.path.join(OUT, 'akademia_e7_test.html')
    open(zmieniony, 'w', encoding='utf-8').write(open(AKAD, encoding='utf-8').read() + '\n<!-- e7-test-paczki -->\n')
    stary = (await stan(pg))['docs']['akademia/info']['prefiks']
    await pg.set_input_files('#plik', zmieniony)
    await pg.click('#wgraj')
    check(await czekaj(pg, 'Wgrane:', 60000), 'nowa paczka wgrana')
    s = await stan(pg)
    I = s['docs']['akademia/info']
    sha = hashlib.sha256(open(zmieniony, 'rb').read()).hexdigest()
    check(I['sha256'] == sha and I['prefiks'] != stary and I['czesci'] >= 1, 'info: nowa wersja i nowe części')
    check(not any(p.startswith(f'akademia/{stary}-') for p in s['docs']) and all(f'akademia/{I["prefiks"]}-{i}' in s['docs'] for i in range(I['czesci'])), 'stare części usunięte, nowe są w bazie')

    print('\n[P4] Osoby z dostępem')
    await pg.click('[data-z=osoby]')
    check(await czekaj(pg, 'stary@stud.umk.pl'), 'lista osób z dostępem')
    await pg.click('[data-odbierz="uidSTARY"]')
    await pg.click('[data-odbierz="uidSTARY"]')
    check(await czekaj(pg, 'Nikt jeszcze nie wszedł'), 'odebranie dostępu (dwa kliknięcia)')
    s = await stan(pg)
    check('studenci/uidSTARY' not in s['docs'], 'w bazie nie ma już dostępu tej osoby')

    print('\n[P5] Admin wchodzi do Akademii — z paczki wgranej w panelu')
    await pg.goto(BASE + 'akademia.html')
    fr = await ramka(pg)
    # komentarz dopisany po </html> trafia do węzłów dokumentu, nie do <html>
    r = await fr.evaluate("() => [WERSJA, [...document.childNodes].some(n => n.nodeType === 8 && n.data.includes('e7-test-paczki')) || document.documentElement.outerHTML.includes('e7-test-paczki')]")
    check(r == ['akademicka', True], f'paczka z panelu rozpakowana i uruchomiona ({r})')

    print('\n[P6] Konto bez uprawnień admina')
    await pg.goto(BASE + 'admin.html')
    await czekaj(pg, 'Nowe kody')
    await pg.click('#out')
    await czekaj(pg, 'Panel dla autorki')
    await pg.fill('#email', 'jan@uw.edu.pl')
    await pg.fill('#haslo', 'haslo-jana-123')
    await pg.click('#nowe')
    await czekaj(pg, 'Wysłaliśmy link')
    await pg.evaluate("() => __fakefb.potwierdz('jan@uw.edu.pl')")
    await pg.click('#spr')
    check(await czekaj(pg, 'nie jest kontem admina'), 'konto bez wpisu w „admini”: instrukcja zamiast panelu')
    uid = (await stan(pg))['current']
    check(uid in await pg.inner_text('#uid'), 'panel pokazuje UID do wpisania w konsoli')
    check(not errs, f'bez błędów JavaScript ({errs[:3]})')
    await ctx.close()


async def inne(b):
    errs = []
    print('\n[I1] Bez konfiguracji Firebase')
    ctx = await kontekst(b, konfig=False)
    pg = await nowa_strona(ctx, errs)
    await pg.goto(BASE + 'akademia.html')
    check(await czekaj(pg, 'nie jest jeszcze włączone'), 'akademia.html: logowanie wyłączone, link do wersji dla każdego')
    await pg.goto(BASE + 'admin.html')
    check(await czekaj(pg, 'uzupełnij'), 'admin.html: prośba o konfigurację')
    await ctx.close()

    print('\n[I2] Telefon')
    ctx = await kontekst(b, viewport={'width': 390, 'height': 844})
    pg = await nowa_strona(ctx, errs)
    await zasiej(pg)
    await pg.goto(BASE + 'akademia.html')
    await czekaj(pg, 'Mam konto')
    r = await pg.evaluate("() => document.documentElement.scrollWidth <= innerWidth + 1")
    check(r, 'akademia.html mieści się na ekranie telefonu')
    await pg.click('[data-z=nowe]')
    await pg.screenshot(path=f'{OUT}/e7_tel_konto.png', full_page=True)
    await ctx.close()

    print('\n[I3] Wersja akademicka z pliku (bez strony Akademii)')
    ctx = await kontekst(b)
    pg = await nowa_strona(ctx, errs)
    await start_game(pg, f'http://localhost:{PORT}/Akademia%20diagnosty/akademia_diagnosty_miasteczko.html')
    r = await pg.evaluate("() => { game.closeModal(true); game.closeDialog(true); document.getElementById('t-akademia').click(); return document.getElementById('modal').innerText; }")
    check('z pliku na tym komputerze' in r and 'Wyloguj' not in r, 'plik akademicki otwarty wprost: 🎓 bez wylogowania')
    check(not errs, f'bez błędów JavaScript ({errs[:3]})')
    await ctx.close()


async def main():
    global STAN
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'narzedzia', 'zbuduj_strone.py')], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout, r.stderr)
        sys.exit(1)
    STAN = stan_poczatkowy()
    serwer = None
    try:
        urllib.request.urlopen(f'http://localhost:{PORT}/strona/akademia.html', timeout=2)
    except Exception:
        serwer = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--directory', ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            await student(b)
            await absolwent(b)
            await admin(b)
            await inne(b)
            await b.close()
    finally:
        if serwer:
            serwer.terminate()
    print('\nWYNIK:', 'OK' if not fails else f'{len(fails)} błędów')
    for f in fails:
        print(' -', f)
    sys.exit(1 if fails else 0)


asyncio.run(main())
