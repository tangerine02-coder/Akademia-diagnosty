// Testy reguł bazy Akademii (../firestore.rules) w emulatorze Firebase.
// Uruchomienie (w folderze firebase/):  npm install  &&  npm test
// Emulator pobiera się sam przy pierwszym uruchomieniu (potrzebna Java 11+).
import { test, before, after, beforeEach } from 'node:test';
import { readFileSync } from 'node:fs';
import { initializeTestEnvironment, assertFails, assertSucceeds } from '@firebase/rules-unit-testing';
import { doc, getDoc, getDocs, collection, setDoc, deleteDoc, updateDoc, writeBatch, serverTimestamp, Timestamp } from 'firebase/firestore';

const DZIEN = 24 * 3600 * 1000;
const za = (ms) => Timestamp.fromMillis(Date.now() + ms);
let env;

before(async () => {
  env = await initializeTestEnvironment({
    projectId: 'demo-akademia',
    firestore: { rules: readFileSync(new URL('../firestore.rules', import.meta.url), 'utf8') },
  });
});
after(async () => { if (env) await env.cleanup(); });
beforeEach(async () => {
  await env.clearFirestore();
  await env.withSecurityRulesDisabled(async (ctx) => {
    const db = ctx.firestore();
    const kod = (typ, etykieta, ms = 30 * DZIEN) => ({ typ, etykieta, waznyDo: za(ms), uzyty: false, uzytyPrzez: null, uzytyKiedy: null });
    await setDoc(doc(db, 'config/uczelnie'), { domeny: ['umk.pl', 'uni.lodz.pl', 'kul.pl'] });
    await setDoc(doc(db, 'admini/ADMIN'), { imie: 'Sylwia' });
    await setDoc(doc(db, 'kody/AAAABBBBCCCC'), kod('student', 'UMK, psychologia, II rok'));
    await setDoc(doc(db, 'kody/DDDDEEEEFFFF'), kod('absolwent', 'Absolwenci'));
    await setDoc(doc(db, 'kody/GGGGHHHHJJJJ'), kod('pracownik', 'Kadra'));
    await setDoc(doc(db, 'kody/KKKKMMMMNNNN'), kod('student', 'Po terminie', -DZIEN));
    await setDoc(doc(db, 'akademia/info'), { wersja: 'v1', czesci: 1 });
  });
});

// konto z potwierdzonym (albo nie) adresem e-mail
const konto = (uid, email, potwierdzony = true) => env.authenticatedContext(uid, { email, email_verified: potwierdzony }).firestore();
const gosc = () => env.unauthenticatedContext().firestore();
const admin = () => konto('ADMIN', 'sylwia@example.com');

// zapis zbiorczy jak w akademia.html: dokument w studenci + zużycie kodu
function aktywuj(db, uid, email, k, { typ, etykieta, domena = '' }) {
  const b = writeBatch(db);
  b.set(doc(db, 'studenci', uid), { email, kod: k, typ, etykieta, domena, kiedy: serverTimestamp() });
  b.update(doc(db, 'kody', k), { uzyty: true, uzytyPrzez: uid, uzytyKiedy: serverTimestamp() });
  return b.commit();
}
const STUDENT = { typ: 'student', etykieta: 'UMK, psychologia, II rok' };

test('student UMK z kodem wchodzi i czyta paczkę', async () => {
  const db = konto('u1', '123456@stud.umk.pl');
  await assertFails(getDoc(doc(db, 'akademia/info')));
  await assertSucceeds(aktywuj(db, 'u1', '123456@stud.umk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
  await assertSucceeds(getDoc(doc(db, 'akademia/info')));
  await assertSucceeds(getDoc(doc(db, 'studenci/u1')));
});

test('ten sam kod nie działa drugi raz', async () => {
  await assertSucceeds(aktywuj(konto('u1', 'a@stud.umk.pl'), 'u1', 'a@stud.umk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
  const db2 = konto('u2', 'b@stud.umk.pl');
  await assertFails(aktywuj(db2, 'u2', 'b@stud.umk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
  await assertFails(getDoc(doc(db2, 'akademia/info')));
});

test('niepotwierdzony e-mail nie wchodzi', async () => {
  const db = konto('u1', 'a@stud.umk.pl', false);
  await assertFails(aktywuj(db, 'u1', 'a@stud.umk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
});

test('adres spoza uczelni z kodem studenta nie wchodzi', async () => {
  const db = konto('u1', 'ktos@gmail.com');
  await assertFails(aktywuj(db, 'u1', 'ktos@gmail.com', 'AAAABBBBCCCC', { ...STUDENT, domena: '' }));
  await assertFails(aktywuj(db, 'u1', 'ktos@gmail.com', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
  const db2 = konto('u2', 'ktos@notumk.pl');
  await assertFails(aktywuj(db2, 'u2', 'ktos@notumk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
});

test('domena spoza listy nie pomaga', async () => {
  const db = konto('u1', 'ktos@gmail.com');
  await assertFails(aktywuj(db, 'u1', 'ktos@gmail.com', 'AAAABBBBCCCC', { ...STUDENT, domena: 'gmail.com' }));
});

test('absolwent wchodzi z dowolnym potwierdzonym e-mailem', async () => {
  const db = konto('u1', 'ktos@gmail.com');
  await assertSucceeds(aktywuj(db, 'u1', 'ktos@gmail.com', 'DDDDEEEEFFFF', { typ: 'absolwent', etykieta: 'Absolwenci' }));
  await assertSucceeds(getDoc(doc(db, 'akademia/info')));
});

test('każda domena .edu.pl i subdomeny z listy', async () => {
  await assertSucceeds(aktywuj(konto('u1', 'jan@uw.edu.pl'), 'u1', 'jan@uw.edu.pl', 'GGGGHHHHJJJJ', { typ: 'pracownik', etykieta: 'Kadra' }));
  await assertSucceeds(aktywuj(konto('u2', 'ola@edu.uni.lodz.pl'), 'u2', 'ola@edu.uni.lodz.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'uni.lodz.pl' }));
});

test('kod po terminie i kod nie z tym typem albo opisem', async () => {
  const db = konto('u1', 'a@stud.umk.pl');
  await assertFails(aktywuj(db, 'u1', 'a@stud.umk.pl', 'KKKKMMMMNNNN', { typ: 'student', etykieta: 'Po terminie', domena: 'umk.pl' }));
  await assertFails(aktywuj(db, 'u1', 'a@stud.umk.pl', 'AAAABBBBCCCC', { typ: 'pracownik', etykieta: STUDENT.etykieta, domena: 'umk.pl' }));
  await assertFails(aktywuj(db, 'u1', 'a@stud.umk.pl', 'AAAABBBBCCCC', { typ: 'student', etykieta: 'Inny opis', domena: 'umk.pl' }));
  await assertFails(aktywuj(db, 'u1', 'a@stud.umk.pl', 'ZZZZYYYYXXXX', { ...STUDENT, domena: 'umk.pl' }));
});

test('samo zużycie kodu albo sam dokument w studenci nie wystarczą', async () => {
  const db = konto('u1', 'a@stud.umk.pl');
  await assertFails(updateDoc(doc(db, 'kody/AAAABBBBCCCC'), { uzyty: true, uzytyPrzez: 'u1', uzytyKiedy: serverTimestamp() }));
  await assertFails(setDoc(doc(db, 'studenci/u1'), { email: 'a@stud.umk.pl', kod: 'AAAABBBBCCCC', ...STUDENT, domena: 'umk.pl', kiedy: serverTimestamp() }));
});

test('nie da się wejść za kogoś ani z cudzym e-mailem', async () => {
  const db = konto('u1', 'a@stud.umk.pl');
  await assertFails(aktywuj(db, 'u2', 'a@stud.umk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
  await assertFails(aktywuj(db, 'u1', 'inna@stud.umk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
});

test('kody, lista osób, paczka i lista uczelni — zapis tylko dla admina', async () => {
  await assertSucceeds(aktywuj(konto('u1', 'a@stud.umk.pl'), 'u1', 'a@stud.umk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
  const st = konto('u1', 'a@stud.umk.pl');
  await assertSucceeds(getDoc(doc(st, 'kody/GGGGHHHHJJJJ')));   // znany kod: typ i opis przed aktywacją
  await assertFails(getDoc(doc(konto('u3', 'c@stud.umk.pl', false), 'kody/GGGGHHHHJJJJ')));
  await assertFails(getDocs(collection(st, 'kody')));
  await assertFails(getDocs(collection(st, 'studenci')));
  await assertFails(setDoc(doc(st, 'akademia/info'), { wersja: 'podrobka' }));
  await assertFails(setDoc(doc(st, 'config/uczelnie'), { domeny: ['gmail.com'] }));
  await assertFails(setDoc(doc(st, 'kody/ZZZZZZZZZZZZ'), { typ: 'student', etykieta: 'x', waznyDo: za(DZIEN), uzyty: false }));
  const ad = admin();
  await assertSucceeds(getDocs(collection(ad, 'kody')));
  await assertSucceeds(getDocs(collection(ad, 'studenci')));
  await assertSucceeds(setDoc(doc(ad, 'kody/ZZZZZZZZZZZZ'), { typ: 'student', etykieta: 'x', waznyDo: za(DZIEN), uzyty: false, uzytyPrzez: null, uzytyKiedy: null }));
  await assertSucceeds(setDoc(doc(ad, 'akademia/info'), { wersja: 'v2', czesci: 1 }));
  await assertSucceeds(setDoc(doc(ad, 'config/uczelnie'), { domeny: ['umk.pl'] }));
  await assertFails(setDoc(doc(ad, 'admini/u1'), { imie: 'x' }));
});

test('rezygnacja i odebranie dostępu; dokumentu nie da się zmienić', async () => {
  await assertSucceeds(aktywuj(konto('u1', 'a@stud.umk.pl'), 'u1', 'a@stud.umk.pl', 'AAAABBBBCCCC', { ...STUDENT, domena: 'umk.pl' }));
  await assertSucceeds(aktywuj(konto('u2', 'jan@uw.edu.pl'), 'u2', 'jan@uw.edu.pl', 'GGGGHHHHJJJJ', { typ: 'pracownik', etykieta: 'Kadra' }));
  const st = konto('u1', 'a@stud.umk.pl');
  await assertFails(updateDoc(doc(st, 'studenci/u1'), { typ: 'pracownik' }));
  await assertFails(deleteDoc(doc(st, 'studenci/u2')));
  await assertSucceeds(deleteDoc(doc(st, 'studenci/u1')));
  await assertFails(getDoc(doc(st, 'akademia/info')));
  await assertSucceeds(deleteDoc(doc(admin(), 'studenci/u2')));
});

test('bez logowania: tylko lista uczelni', async () => {
  const g = gosc();
  await assertSucceeds(getDoc(doc(g, 'config/uczelnie')));
  await assertFails(getDoc(doc(g, 'akademia/info')));
  await assertFails(getDoc(doc(g, 'kody/AAAABBBBCCCC')));
  await assertFails(getDocs(collection(g, 'studenci')));
  await assertFails(getDoc(doc(g, 'admini/ADMIN')));
});
