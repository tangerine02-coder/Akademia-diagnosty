// Udawany Firebase do testów (tests/akademia_test.py): wspólny stan w localStorage, żeby przetrwał przejścia między stronami.
// Test podmienia nim prawdziwe moduły z https://www.gstatic.com/firebasejs/11.6.1/…
const KLUCZ = '__fakefb';
export const pusty = () => ({ users: {}, current: null, docs: {}, mails: [], seq: 1 });
export function wczytaj() {
  try { return JSON.parse(localStorage.getItem(KLUCZ)) || pusty(); } catch (e) { return pusty(); }
}
export function zapisz(s) { localStorage.setItem(KLUCZ, JSON.stringify(s)); }
export const tick = () => new Promise(r => setTimeout(r, 5));
export const blad = (code, msg) => Object.assign(new Error(msg || code), { code });
