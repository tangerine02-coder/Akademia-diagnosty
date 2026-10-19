// Udawany Firebase (testy): firebase-auth. Konto e-mail + hasło, mail z linkiem (zapisany w stanie),
// token z email_verified, który odświeża się dopiero po getIdToken(true) albo zalogowaniu — jak w prawdziwym.
import { wczytaj, zapisz, tick, blad } from './stan.js';

const sluchacze = new Set();
let cur = null, auth = null;

class User {
  constructor(uid, u) {
    this.uid = uid; this.email = u.email; this.emailVerified = !!u.emailVerified;
    this.metadata = { lastSignInTime: new Date(u.lastSignIn || Date.now()).toUTCString() };
  }
  async getIdToken(force) {
    await tick();
    if (force) { const s = wczytaj(); const u = s.users[this.uid]; if (u) { u.tokenEV = !!u.emailVerified; zapisz(s); } }
    return 'fake-token-' + this.uid;
  }
}
const biezacy = () => { const s = wczytaj(); return s.current && s.users[s.current] ? new User(s.current, s.users[s.current]) : null; };
function powiadom() { cur = biezacy(); sluchacze.forEach(cb => setTimeout(() => cb(cur), 0)); }

export function getAuth() {
  if (!auth) { cur = biezacy(); auth = { languageCode: null, get currentUser() { return cur; } }; }
  return auth;
}
export function onAuthStateChanged(a, cb) { sluchacze.add(cb); setTimeout(() => cb(cur), 0); return () => sluchacze.delete(cb); }

export async function createUserWithEmailAndPassword(a, email, haslo) {
  await tick();
  email = String(email).trim().toLowerCase();
  if (!email) throw blad('auth/missing-email');
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw blad('auth/invalid-email');
  if (String(haslo).length < 6) throw blad('auth/weak-password');
  const s = wczytaj();
  if (Object.values(s.users).some(u => u.email === email)) throw blad('auth/email-already-in-use');
  const uid = 'uid' + (s.seq++);
  s.users[uid] = { email, haslo, emailVerified: false, tokenEV: false, lastSignIn: Date.now() };
  s.current = uid; zapisz(s); powiadom();
  return { user: biezacy() };
}
export async function signInWithEmailAndPassword(a, email, haslo) {
  await tick();
  email = String(email).trim().toLowerCase();
  const s = wczytaj();
  const uid = Object.keys(s.users).find(k => s.users[k].email === email);
  if (!uid || s.users[uid].haslo !== haslo) throw blad('auth/invalid-credential');
  Object.assign(s.users[uid], { tokenEV: !!s.users[uid].emailVerified, lastSignIn: Date.now() });
  s.current = uid; zapisz(s); powiadom();
  return { user: biezacy() };
}
export async function signOut() { await tick(); const s = wczytaj(); s.current = null; zapisz(s); powiadom(); }
export async function sendEmailVerification(user, ustawienia) {
  await tick(); const s = wczytaj(); s.mails.push({ typ: 'potwierdzenie', email: user.email, url: ustawienia && ustawienia.url }); zapisz(s);
}
export async function sendPasswordResetEmail(a, email, ustawienia) {
  await tick(); const s = wczytaj(); s.mails.push({ typ: 'reset', email, url: ustawienia && ustawienia.url }); zapisz(s);
}
export async function reload(user) {
  await tick();
  const u = wczytaj().users[user.uid];
  if (!u) throw blad('auth/user-not-found');
  user.emailVerified = !!u.emailVerified; user.email = u.email;
}
export async function deleteUser(user) {
  await tick(); const s = wczytaj(); delete s.users[user.uid]; if (s.current === user.uid) s.current = null; zapisz(s); powiadom();
}

// uchwyty dla testu: „kliknięcie linku z maila” i podgląd stanu
globalThis.__fakefb = Object.assign(globalThis.__fakefb || {}, {
  potwierdz(email) { const s = wczytaj(); Object.values(s.users).forEach(u => { if (u.email === email) u.emailVerified = true; }); zapisz(s); },
  stan: () => wczytaj(),
});
