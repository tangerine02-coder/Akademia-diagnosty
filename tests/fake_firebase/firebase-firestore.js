// Udawany Firebase (testy): firebase-firestore z uproszczoną kopią reguł z firebase/firestore.rules.
// Prawdziwe reguły sprawdza emulator (firebase/testy/reguly.test.mjs); ta kopia pilnuje, żeby strony
// w teście szły tą samą drogą co w prawdziwej bazie (np. zapis zbiorczy studenci + kody).
import { wczytaj, zapisz, tick, blad } from './stan.js';

export class Timestamp {
  constructor(ms) { this._ms = ms; }
  static fromDate(d) { return new Timestamp(d.getTime()); }
  static fromMillis(ms) { return new Timestamp(ms); }
  static now() { return new Timestamp(Date.now()); }
  toMillis() { return this._ms; }
  toDate() { return new Date(this._ms); }
  get seconds() { return Math.floor(this._ms / 1000); }
}
export class Bytes {
  constructor(u) { this._u = u; }
  static fromUint8Array(u) { return new Bytes(new Uint8Array(u)); }
  toUint8Array() { return this._u; }
}
const SERWER = { __serverTimestamp: true };
export const serverTimestamp = () => SERWER;
export const getFirestore = () => ({ fake: true });
export const doc = (db, ...seg) => { const path = seg.join('/'); return { path, id: path.split('/').pop() }; };
export const collection = (db, ...seg) => ({ path: seg.join('/') });

/* ---------- zapis w localStorage ---------- */
function b64(u) { let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); }
function zB64(t) { const s = atob(t); const u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u; }
function enc(v, teraz) {
  if (v === SERWER) return { __t: teraz };
  if (v instanceof Timestamp) return { __t: v._ms };
  if (v instanceof Bytes) return { __b: b64(v._u) };
  if (Array.isArray(v)) return v.map(x => enc(x, teraz));
  if (v && typeof v === 'object') return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, enc(x, teraz)]));
  return v;
}
function dec(v) {
  if (Array.isArray(v)) return v.map(dec);
  if (v && typeof v === 'object') {
    if ('__t' in v) return new Timestamp(v.__t);
    if ('__b' in v) return new Bytes(zB64(v.__b));
    return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, dec(x)]));
  }
  return v;
}
const snap = (path, d) => ({ id: path.split('/').pop(), exists: () => d != null, data: () => (d == null ? undefined : dec(d)) });

/* ---------- uproszczone reguły ---------- */
function kto() {
  const s = wczytaj(), uid = s.current, u = uid ? s.users[uid] : null;
  return { uid: u ? uid : null, email: u ? u.email : null, ev: !!(u && u.tokenEV) };
}
const odmowa = () => { throw blad('permission-denied', 'Missing or insufficient permissions.'); };
function emailUczelni(docs, email, domena) {
  const host = email.toLowerCase().split('@')[1];
  if (/.+\.edu\.pl$/.test(host)) return true;
  const lista = (docs['config/uczelnie'] || {}).domeny || [];
  return /^[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(domena) && lista.includes(domena) && (host === domena || host.endsWith('.' + domena));
}
function sprawdz(op, path, przed, po, dane, c) {
  const [kol, id] = path.split('/');
  const admin = !!c.uid && !!przed['admini/' + c.uid];
  const dostep = !!c.uid && !!przed['studenci/' + c.uid];
  if (kol === 'admini') return op === 'get' && c.uid === id ? null : odmowa();
  if (kol === 'config') return op === 'get' || op === 'list' || admin ? null : odmowa();
  if (kol === 'akademia') return (op === 'get' || op === 'list') ? (dostep || admin ? null : odmowa()) : (admin ? null : odmowa());
  if (kol === 'studenci') {
    if (op === 'get' || op === 'delete') return c.uid === id || admin ? null : odmowa();
    if (op === 'list') return admin ? null : odmowa();
    if (op !== 'create') return odmowa();
    const d = dane, pola = ['domena', 'email', 'etykieta', 'kiedy', 'kod', 'typ'];
    if (!c.uid || c.uid !== id || !c.ev) return odmowa();
    if (Object.keys(d).sort().join() !== pola.join()) return odmowa();
    if (d.email !== c.email || d.kiedy !== SERWER || typeof d.kod !== 'string' || !/^[A-HJKMNP-Z2-9]{12}$/.test(d.kod) || typeof d.domena !== 'string') return odmowa();
    const k = przed['kody/' + d.kod], kp = po['kody/' + d.kod];
    if (!k || k.uzyty !== false || !(k.waznyDo && k.waznyDo.__t > Date.now()) || d.typ !== k.typ || d.etykieta !== k.etykieta) return odmowa();
    if (!kp || kp.uzytyPrzez !== c.uid) return odmowa();
    if (k.typ !== 'absolwent' && !emailUczelni(przed, c.email, d.domena)) return odmowa();
    return null;
  }
  if (kol === 'kody') {
    if (op === 'get') return admin || (c.uid && c.ev) ? null : odmowa();
    if (op === 'list' || op === 'create' || op === 'delete') return admin ? null : odmowa();
    if (admin) return null;
    const k = przed[path];
    if (!c.uid || !k || k.uzyty !== false) return odmowa();
    if (!Object.keys(dane).every(x => ['uzyty', 'uzytyPrzez', 'uzytyKiedy'].includes(x))) return odmowa();
    if (dane.uzyty !== true || dane.uzytyPrzez !== c.uid || dane.uzytyKiedy !== SERWER) return odmowa();
    const st = po['studenci/' + c.uid];
    return st && st.kod === id ? null : odmowa();
  }
  return odmowa();
}

/* ---------- odczyt i zapis ---------- */
export async function getDoc(ref) {
  await tick();
  const s = wczytaj();
  sprawdz('get', ref.path, s.docs, s.docs, null, kto());
  return snap(ref.path, s.docs[ref.path]);
}
export async function getDocs(col) {
  await tick();
  const s = wczytaj();
  sprawdz('list', col.path + '/*', s.docs, s.docs, null, kto());
  const pre = col.path + '/';
  const docs = Object.keys(s.docs).filter(p => p.startsWith(pre) && !p.slice(pre.length).includes('/')).map(p => snap(p, s.docs[p]));
  return { docs, size: docs.length, empty: !docs.length };
}
async function zapiszOps(ops) {
  await tick();
  const s = wczytaj(), przed = s.docs, po = Object.assign({}, przed), teraz = Date.now(), c = kto();
  for (const o of ops) {
    if (o.op === 'set') po[o.path] = enc(o.dane, teraz);
    else if (o.op === 'update') { if (!po[o.path]) throw blad('not-found', 'No document to update: ' + o.path); po[o.path] = Object.assign({}, po[o.path], enc(o.dane, teraz)); }
    else delete po[o.path];
  }
  for (const o of ops) sprawdz(o.op === 'set' ? (przed[o.path] ? 'update' : 'create') : o.op, o.path, przed, po, o.dane, c);
  s.docs = po; zapisz(s);
}
export const setDoc = (ref, dane) => zapiszOps([{ op: 'set', path: ref.path, dane }]);
export const updateDoc = (ref, dane) => zapiszOps([{ op: 'update', path: ref.path, dane }]);
export const deleteDoc = (ref) => zapiszOps([{ op: 'delete', path: ref.path }]);
export function writeBatch() {
  const ops = [];
  return {
    set(r, d) { ops.push({ op: 'set', path: r.path, dane: d }); return this; },
    update(r, d) { ops.push({ op: 'update', path: r.path, dane: d }); return this; },
    delete(r) { ops.push({ op: 'delete', path: r.path }); return this; },
    commit: () => zapiszOps(ops),
  };
}
