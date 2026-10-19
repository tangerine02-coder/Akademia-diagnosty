// Akademia Diagnosty — wspólny moduł kont dla akademia.html i admin.html (Etap 7, 2026-10-19).
// Firebase: Authentication (e-mail i hasło + mail z linkiem), Firestore (kody, dostęp, paczka Akademii).
// Weryfikację i tak robią reguły bazy (firebase/firestore.rules) — sprawdzanie tutaj służy tylko
// czytelnym komunikatom. Opis: Akademia diagnosty/docs/LOGOWANIE_I_WERYFIKACJA.md.
import KONFIG from './firebase-config.js';
import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js';
import {
  getAuth, onAuthStateChanged, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut,
  sendEmailVerification, sendPasswordResetEmail, reload, deleteUser,
} from 'https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js';
import {
  getFirestore, doc, getDoc, getDocs, setDoc, updateDoc, deleteDoc, collection, writeBatch,
  serverTimestamp, Timestamp, Bytes,
} from 'https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js';

export const SKONFIGUROWANE = !!(KONFIG && KONFIG.apiKey && KONFIG.projectId);
const app = SKONFIGUROWANE ? initializeApp(KONFIG) : null;
const auth = app ? getAuth(app) : null;
const db = app ? getFirestore(app) : null;
if (auth) auth.languageCode = 'pl';

export const ALFABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';   // bez I, L, O, 0 i 1 — nie da się ich pomylić
export const TYPY = { student: 'student', pracownik: 'pracownik uczelni', absolwent: 'absolwent' };
export const KLUCZ_PUBLICZNA = 'akademia_freudowice_publiczna_v1';   // zapis wersji publicznej (SAVE_KEY)
export const KLUCZ_AKADEMIA = 'akademia_freudowice_v1';              // zapis wersji akademickiej
const CZESC = 700000;            // bajtów spakowanej gry w jednym dokumencie (limit Firestore to 1 MiB)
const OFFLINE_DNI = 14;          // bez internetu Akademia działa z kopii, jeśli dostęp sprawdzono niedawno

/* ---------- błędy po polsku ---------- */
const KOMUNIKATY = {
  'zly-format': 'Kod ma 12 znaków: wielkie litery i cyfry 2–9 (bez I, L, O, 0 i 1), np. K7QM-3XPA-9RTD.',
  'brak-kodu': 'Nie ma takiego kodu. Sprawdź, czy dobrze go przepisujesz.',
  'kod-uzyty': 'Ten kod został już użyty. Każdy kod działa tylko raz — poproś prowadzącego o nowy.',
  'kod-po-terminie': 'Ten kod stracił ważność. Poproś prowadzącego o nowy.',
  'email-spoza-uczelni': 'Ten kod wymaga adresu e-mail uczelni, a konto ma inny adres. Załóż konto na adres uczelni albo poproś o kod dla absolwentów.',
  'kod-odrzucony': 'Baza nie przyjęła kodu: mógł zostać przed chwilą użyty albo nie pasuje do adresu e-mail. Spróbuj jeszcze raz albo poproś o nowy kod.',
  'email-niepotwierdzony': 'Najpierw potwierdź adres e-mail (link w mailu).',
  'brak-paczki': 'Akademia nie jest jeszcze wgrana. Zajrzyj później.',
  'paczka-uszkodzona': 'Nie udało się pobrać Akademii w całości. Odśwież stronę.',
  'to-nie-akademicka': 'To nie jest plik wersji akademickiej (akademia_diagnosty_miasteczko.html).',
  'brak-uprawnien': 'Brak uprawnień do tej operacji.',
  'offline': 'Brak połączenia z internetem.',
  'hasla-rozne': 'Hasła się różnią.',
  'auth/invalid-email': 'To nie wygląda na adres e-mail.',
  'auth/missing-email': 'Wpisz adres e-mail.',
  'auth/missing-password': 'Wpisz hasło.',
  'auth/email-already-in-use': 'Na ten adres jest już konto — zaloguj się albo zresetuj hasło.',
  'auth/weak-password': 'Hasło jest za krótkie — użyj co najmniej 8 znaków.',
  'auth/invalid-credential': 'Zły e-mail albo hasło.',
  'auth/wrong-password': 'Zły e-mail albo hasło.',
  'auth/user-not-found': 'Zły e-mail albo hasło.',
  'auth/too-many-requests': 'Za dużo prób. Odczekaj chwilę i spróbuj znowu.',
  'auth/network-request-failed': 'Brak połączenia z internetem.',
  'auth/requires-recent-login': 'Ze względów bezpieczeństwa wyloguj się, zaloguj jeszcze raz i powtórz.',
  'auth/quota-exceeded': 'Dzisiejszy limit maili się wyczerpał. Spróbuj jutro.',
  'inny': 'Coś poszło nie tak. Spróbuj jeszcze raz.',
};
export class BladAkademii extends Error {
  constructor(kod, oryginal) {
    super(KOMUNIKATY[kod] || KOMUNIKATY.inny + (kod ? ` (${kod})` : ''));
    this.kod = kod; this.oryginal = oryginal;
  }
}
export function przetlumacz(e, domyslny) {
  if (e instanceof BladAkademii) return e;
  const c = (e && e.code) || '';
  if (c === 'permission-denied' || c === 'firestore/permission-denied') return new BladAkademii(domyslny || 'brak-uprawnien', e);
  if (c === 'unavailable' || c === 'firestore/unavailable') return new BladAkademii('offline', e);
  if (KOMUNIKATY[c]) return new BladAkademii(c, e);
  return new BladAkademii(domyslny || c || 'inny', e);
}
const proba = (p, domyslny) => p.catch(e => { throw przetlumacz(e, domyslny); });

/* ---------- e-mail uczelni (tak samo liczą reguły bazy) ---------- */
let _domeny = null;
export async function domenyUczelni(odswiez = false) {
  if (_domeny && !odswiez) return _domeny;
  try {
    const s = await getDoc(doc(db, 'config', 'uczelnie'));
    _domeny = s.exists() ? (s.data().domeny || []) : [];
  } catch (e) { _domeny = _domeny || []; }
  return _domeny;
}
// '' = adres w domenie .edu.pl, 'umk.pl' = pozycja z listy, null = adres spoza uczelni
export function domenaUczelni(email, domeny) {
  const host = String(email || '').trim().toLowerCase().split('@')[1] || '';
  if (/.+\.edu\.pl$/.test(host)) return '';
  for (const d of domeny || []) if (host === d || host.endsWith('.' + d)) return d;
  return null;
}
export function normujDomene(t) {
  const d = String(t || '').trim().toLowerCase().replace(/^[@.]+/, '');
  return /^[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(d) ? d : null;
}

/* ---------- konto ---------- */
export const naZmiane = (cb) => onAuthStateChanged(auth, cb);
export const uzytkownik = () => auth && auth.currentUser;
const powrot = () => location.origin + location.pathname;   // link z maila wraca na tę samą stronę

export async function zalozKonto(email, haslo, haslo2) {
  if (haslo2 !== undefined && haslo !== haslo2) throw new BladAkademii('hasla-rozne');
  if (String(haslo || '').length < 8) throw new BladAkademii('auth/weak-password');
  const c = await proba(createUserWithEmailAndPassword(auth, String(email || '').trim(), haslo));
  await proba(sendEmailVerification(c.user, { url: powrot() }));
  return c.user;
}
export const zaloguj = (email, haslo) => proba(signInWithEmailAndPassword(auth, String(email || '').trim(), haslo)).then(c => c.user);
export async function wyloguj() { await wyczyscKopie(); await signOut(auth); }
export const resetHasla = (email) => proba(sendPasswordResetEmail(auth, String(email || '').trim(), { url: powrot() }));
export const wyslijLinkPonownie = () => proba(sendEmailVerification(auth.currentUser, { url: powrot() }));
// po kliknięciu linku: odśwież konto i token, żeby reguły bazy zobaczyły potwierdzony adres
export async function sprawdzPotwierdzenie() {
  const u = auth.currentUser;
  if (!u) return false;
  await proba(reload(u));
  if (u.emailVerified) await proba(u.getIdToken(true));
  return !!u.emailVerified;
}
export async function usunKonto() {
  const u = auth.currentUser;
  const ostatnio = Date.parse((u.metadata && u.metadata.lastSignInTime) || 0) || 0;
  if (Date.now() - ostatnio > 5 * 60 * 1000) throw new BladAkademii('auth/requires-recent-login');
  await deleteDoc(doc(db, 'studenci', u.uid)).catch(() => {});
  await wyczyscKopie();
  await proba(deleteUser(u));
}

/* ---------- dostęp do Akademii ---------- */
export async function dostep() {
  const u = auth.currentUser;
  const [student, admin] = await Promise.all([
    proba(getDoc(doc(db, 'studenci', u.uid))).then(s => (s.exists() ? s.data() : null)),
    getDoc(doc(db, 'admini', u.uid)).then(s => s.exists()).catch(() => false),
  ]);
  return { student, admin };
}

/* ---------- kody ---------- */
export const normujKod = (t) => String(t || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
export const kodPoprawny = (k) => k.length === 12 && [...k].every(c => ALFABET.includes(c));
export const pokazKod = (k) => String(k).replace(/(.{4})(?=.)/g, '$1-');
// odczyt znanego kodu: typ, opis, ważność (listy kodów nie widzi nikt poza adminem)
export async function sprawdzKod(tekst) {
  const kod = normujKod(tekst);
  if (!kodPoprawny(kod)) throw new BladAkademii('zly-format');
  if (!auth.currentUser.emailVerified) throw new BladAkademii('email-niepotwierdzony');
  await proba(auth.currentUser.getIdToken(true));   // świeży token: reguły bazy muszą widzieć potwierdzony adres
  const s = await proba(getDoc(doc(db, 'kody', kod)), 'kod-odrzucony');
  if (!s.exists()) throw new BladAkademii('brak-kodu');
  const k = s.data();
  if (k.uzyty) throw new BladAkademii('kod-uzyty');
  if (k.waznyDo && k.waznyDo.toMillis() < Date.now()) throw new BladAkademii('kod-po-terminie');
  return { kod, typ: k.typ, etykieta: k.etykieta, waznyDo: k.waznyDo };
}
// jeden zapis zbiorczy: dokument w studenci + zużycie kodu (reguły bazy przepuszczą tylko oba naraz)
export async function aktywujKod(k) {
  const u = auth.currentUser;
  const domena = domenaUczelni(u.email, await domenyUczelni(true));
  if (k.typ !== 'absolwent' && domena === null) throw new BladAkademii('email-spoza-uczelni');
  const b = writeBatch(db);
  b.set(doc(db, 'studenci', u.uid), { email: u.email, kod: k.kod, typ: k.typ, etykieta: k.etykieta, domena: domena || '', kiedy: serverTimestamp() });
  b.update(doc(db, 'kody', k.kod), { uzyty: true, uzytyPrzez: u.uid, uzytyKiedy: serverTimestamp() });
  await proba(b.commit(), 'kod-odrzucony');
}

/* ---------- paczka Akademii: spakowana wersja akademicka w bazie ---------- */
async function spakuj(tekst) {
  const s = new Blob([tekst]).stream().pipeThrough(new CompressionStream('gzip'));
  return new Uint8Array(await new Response(s).arrayBuffer());
}
async function rozpakuj(czesci) {
  const s = new Blob(czesci).stream().pipeThrough(new DecompressionStream('gzip'));
  return new Response(s).text();
}
export async function sha256(tekst) {
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(tekst));
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
}
// kopia w przeglądarce (IndexedDB), żeby kolejne wejścia nie pobierały całej gry
const IDB = 'akademia-diagnosty', SKLEP = 'paczka';
function idb() {
  return new Promise((ok, nie) => {
    const r = indexedDB.open(IDB, 1);
    r.onupgradeneeded = () => r.result.createObjectStore(SKLEP);
    r.onsuccess = () => ok(r.result);
    r.onerror = () => nie(r.error);
  });
}
async function idbGet(k) {
  try { const d = await idb(); return await new Promise(ok => { const r = d.transaction(SKLEP).objectStore(SKLEP).get(k); r.onsuccess = () => ok(r.result || null); r.onerror = () => ok(null); }); }
  catch (e) { return null; }
}
async function idbSet(k, v) {
  try { const d = await idb(); await new Promise(ok => { const t = d.transaction(SKLEP, 'readwrite'); t.objectStore(SKLEP).put(v, k); t.oncomplete = ok; t.onerror = ok; }); }
  catch (e) { /* bez kopii też zadziała, tylko wolniej */ }
}
export async function wyczyscKopie() {
  try { const d = await idb(); await new Promise(ok => { const t = d.transaction(SKLEP, 'readwrite'); t.objectStore(SKLEP).clear(); t.oncomplete = ok; t.onerror = ok; }); }
  catch (e) {}
}
// bez internetu: kopia, jeśli dostęp tego konta sprawdzono w ostatnich dniach
export async function kopiaOffline() {
  const k = await idbGet('akademia');
  const u = auth && auth.currentUser;
  if (!k || !u || k.uid !== u.uid || Date.now() - (k.sprawdzono || 0) > OFFLINE_DNI * 864e5) return null;
  return k;
}
export async function pobierzPaczke(postep = () => {}) {
  const s = await proba(getDoc(doc(db, 'akademia', 'info')));
  if (!s.exists()) throw new BladAkademii('brak-paczki');
  const I = s.data(), uid = auth.currentUser.uid;
  const kopia = await idbGet('akademia');
  if (kopia && kopia.wersja === I.wersja && kopia.html) {
    await idbSet('akademia', Object.assign(kopia, { uid, sprawdzono: Date.now() }));
    return { html: kopia.html, info: I, zKopii: true };
  }
  const czesci = [];
  for (let i = 0; i < I.czesci; i++) {
    postep(i / I.czesci);
    const c = await proba(getDoc(doc(db, 'akademia', `${I.prefiks}-${i}`)));
    if (!c.exists()) throw new BladAkademii('paczka-uszkodzona');
    czesci.push(c.data().dane.toUint8Array());
  }
  postep(1);
  let html;
  try { html = await rozpakuj(czesci); } catch (e) { throw new BladAkademii('paczka-uszkodzona', e); }
  if (I.sha256 && (await sha256(html)) !== I.sha256) throw new BladAkademii('paczka-uszkodzona');
  await idbSet('akademia', { wersja: I.wersja, html, uid, sprawdzono: Date.now() });
  return { html, info: I, zKopii: false };
}

/* ---------- panel admina ---------- */
export async function czyAdmin() {
  const u = auth.currentUser;
  return getDoc(doc(db, 'admini', u.uid)).then(s => s.exists()).catch(() => false);
}
export function nowyKod() {
  const a = new Uint32Array(12);
  crypto.getRandomValues(a);
  return [...a].map(x => ALFABET[x % ALFABET.length]).join('');
}
export async function generujKody(n, typ, etykieta, waznyDo) {
  if (!TYPY[typ]) throw new BladAkademii('inny');
  const kody = [];
  for (let i = 0; i < n; i += 400) {
    const b = writeBatch(db);
    for (let j = i; j < Math.min(n, i + 400); j++) {
      const k = nowyKod();
      kody.push(k);
      b.set(doc(db, 'kody', k), { typ, etykieta, waznyDo: Timestamp.fromDate(waznyDo), uzyty: false, uzytyPrzez: null, uzytyKiedy: null, utworzono: serverTimestamp() });
    }
    await proba(b.commit());
  }
  return kody;
}
export async function listaKodow() {
  const s = await proba(getDocs(collection(db, 'kody')));
  return s.docs.map(d => Object.assign({ kod: d.id }, d.data()));
}
export const uniewaznijKod = (kod) => proba(updateDoc(doc(db, 'kody', kod), { waznyDo: Timestamp.now() }));
export const usunKod = (kod) => proba(deleteDoc(doc(db, 'kody', kod)));
export async function listaOsob() {
  const s = await proba(getDocs(collection(db, 'studenci')));
  return s.docs.map(d => Object.assign({ uid: d.id }, d.data()));
}
export const odbierzDostep = (uid) => proba(deleteDoc(doc(db, 'studenci', uid)));
export const zapiszDomeny = (lista) => proba(setDoc(doc(db, 'config', 'uczelnie'), { domeny: lista, zmieniono: serverTimestamp() })).then(() => { _domeny = lista; });
export async function infoPaczki() {
  const s = await proba(getDoc(doc(db, 'akademia', 'info')));
  return s.exists() ? s.data() : null;
}
// nowe części pod nowymi nazwami → potem info → na końcu usunięcie starych (grający nie trafi na pół paczki)
export async function wgrajPaczke(tekst, nazwa, postep = () => {}) {
  const w = String(tekst).match(/const WERSJA = '([a-z]+)';/);
  if (!w || w[1] !== 'akademicka') throw new BladAkademii('to-nie-akademicka');
  const dane = await spakuj(tekst);
  const sha = await sha256(tekst);
  const prefiks = 'p' + sha.slice(0, 12);
  const czesci = Math.ceil(dane.length / CZESC);
  const stare = await infoPaczki().catch(() => null);
  for (let i = 0; i < czesci; i++) {
    postep(i / (czesci + 1));
    await proba(setDoc(doc(db, 'akademia', `${prefiks}-${i}`), { dane: Bytes.fromUint8Array(dane.slice(i * CZESC, (i + 1) * CZESC)) }));
  }
  const wersja = new Date().toISOString().slice(0, 16).replace('T', ' ') + ' · ' + sha.slice(0, 8);
  await proba(setDoc(doc(db, 'akademia', 'info'), { wersja, prefiks, czesci, rozmiar: new Blob([tekst]).size, spakowana: dane.length, sha256: sha, plik: nazwa || '', wgrano: serverTimestamp() }));
  if (stare && stare.prefiks && stare.prefiks !== prefiks) {
    for (let i = 0; i < (stare.czesci || 0); i++) await deleteDoc(doc(db, 'akademia', `${stare.prefiks}-${i}`)).catch(() => {});
  }
  postep(1);
  return { wersja, czesci, spakowana: dane.length };
}
