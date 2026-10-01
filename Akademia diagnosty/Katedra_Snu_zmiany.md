# Katedra Snu — dokładne zmiany

Zmiany są już zastosowane w pliku gry. Poniższe fragmenty pozwalają odtworzyć je ręcznie w kopii `akademia_diagnosty_miasteczko.przed_snem_v2.html`; stosuj je kolejno.

## 1. Sen zatrzymuje zegar świata; koszt Lustra jest naliczany raz przy wejściu.

**ZNAJDŹ**

```javascript
    const prevHour = Math.floor(s.time / 60);
    s.time += dt * MIN_PER_SEC;
    if (Math.floor(s.time / 60) !== prevHour) this.onHour(Math.floor(s.time / 60));
    if (s.time >= PASS_OUT) { this.passOut(); return; }
```

**ZAMIEŃ NA**

```javascript
    if (!this.dreamSession()) {
      const prevHour = Math.floor(s.time / 60);
      s.time += dt * MIN_PER_SEC;
      if (Math.floor(s.time / 60) !== prevHour) this.onHour(Math.floor(s.time / 60));
      if (s.time >= PASS_OUT) { this.passOut(); return; }
    }
```

## 2. Filtry dotyczą wyłącznie świata, bez rozjaśniania ekranu i interfejsu.

**ZNAJDŹ**

```javascript
    ctx.setTransform(s, 0, 0, s, -cam.x * s, -cam.y * s);
    const vx0 = Math.max(0, Math.floor(cam.x)), vy0 = Math.max(0, Math.floor(cam.y));
```

**ZAMIEŃ NA**

```javascript
    ctx.setTransform(s, 0, 0, s, -cam.x * s, -cam.y * s);
    ctx.filter = this.dreamWorldFilter(t);
    const vx0 = Math.max(0, Math.floor(cam.x)), vy0 = Math.max(0, Math.floor(cam.y));
```

## 3. Budynki snu otrzymują stopniową wyrazistość i detale materiałów.

**ZNAJDŹ**

```javascript
        if (inView(b.X, b.Y, b.spr.c.width, b.spr.c.height)) list.push({ y: (b.y + b.h) * 16, d: () => { ctx.drawImage(b.spr.c, b.X, b.Y); if (b.subject) this.drawSubjectBuilding(b, t); } });
        return;
```

**ZAMIEŃ NA**

```javascript
        if (inView(b.X, b.Y, b.spr.c.width, b.spr.c.height)) list.push({ y: (b.y + b.h) * 16, d: () => { this.drawDreamSprite(b.spr, b.X, b.Y, o); if (b.subject) this.drawSubjectBuilding(b, t); } });
        return;
```

## 4. Roślinność i obiekty korzystają z wyglądu właściwego dla snu.

**ZNAJDŹ**

```javascript
      list.push({ y: (o.y + o.fh) * 16 - (o.type === 'tree' ? 0 : 1), d: () => { ctx.drawImage(spr.c, X, Y); this.drawObjAnim(o, X, Y, t); } });
    });
```

**ZAMIEŃ NA**

```javascript
      list.push({ y: (o.y + o.fh) * 16 - (o.type === 'tree' ? 0 : 1), d: () => { this.drawDreamSprite(spr, X, Y, o); this.drawObjAnim(o, X, Y, t); } });
    });
```

## 5. Podczas lotu postać jest widoczna ponad dachami.

**ZNAJDŹ**

```javascript
    list.push({ y: this.player.y + 0.5, d: () => this.drawPlayer(t) });
    list.sort((a, b) => a.y - b.y).forEach(e => e.d());
```

**ZAMIEŃ NA**

```javascript
    list.push({ y: this.dreamSession() && this.dreamSession().flying ? Infinity : this.player.y + 0.5, d: () => this.drawPlayer(t) });
    list.sort((a, b) => a.y - b.y).forEach(e => e.d());
```

## 6. Elementy koszmaru są w świecie, a efekty pogodowe będą rysowane w skali ekranu.

**ZNAJDŹ**

```javascript
    this.drawDreamEffects(ctx, W, H, t);

    // nakładki na ekranie
    ctx.setTransform(1, 0, 0, 1, 0, 0);
```

**ZAMIEŃ NA**

```javascript
    this.drawDreamWorld(t);

    // nakładki na ekranie
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.filter = 'none';
```

## 7. Sen nie dostaje pełnoekranowej rozjaśniającej warstwy światła dziennego.

**ZNAJDŹ**

```javascript
    if (!Z.interior && tm >= 6 * 60 && tm < 17 * 60) {
      const dawn = tm < 8.5 * 60 ? Math.sin(clamp((tm - 6 * 60) / 150, 0, 1) * Math.PI) : 0;
```

**ZAMIEŃ NA**

```javascript
    if (!this.dreamSession() && !Z.interior && tm >= 6 * 60 && tm < 17 * 60) {
      const dawn = tm < 8.5 * 60 ? Math.sin(clamp((tm - 6 * 60) / 150, 0, 1) * Math.PI) : 0;
```

## 8. Pogoda i informacja o śnie są rysowane po przywróceniu transformacji ekranu.

**ZNAJDŹ**

```javascript
    this.drawLabels(s, cam, t);
    this.drawFade();
```

**ZAMIEŃ NA**

```javascript
    this.drawLabels(s, cam, t);
    this.drawDreamEffects(ctx, W, H, t);
    this.drawFade();
```

## 9. Liczba okien odpowiada liczbie pokoi: katedra_snu.

**ZNAJDŹ**

```javascript
      B.building({ id: 'katedra_snu', subject: 'sny_trening', style: 'cathedral', x: 5, y: 4, w: 9, h: 6, nWin: 5, wall: '#3d1f6d', roof: '#1a0a2e', trim: '#c9a0ff', sign: 'KATEDRA SNU' });
      B.building({ id: 'lustro_rem', kind: 'lustro', style: 'dome', x: 17, y: 2, w: 7, h: 5, nWin: 3, wall: '#e0d0f0', roof: '#7b4fcf', trim: '#f0e6ff', sign: 'LUSTRO REM' });
```

**ZAMIEŃ NA**

```javascript
      B.building({ id: 'katedra_snu', subject: 'sny_trening', style: 'cathedral', x: 5, y: 4, w: 9, h: 6, nWin: 4, wall: '#3d1f6d', roof: '#1a0a2e', trim: '#c9a0ff', sign: 'KATEDRA SNU' });
      B.building({ id: 'lustro_rem', kind: 'lustro', style: 'dome', x: 17, y: 2, w: 7, h: 5, nWin: 3, wall: '#e0d0f0', roof: '#7b4fcf', trim: '#f0e6ff', sign: 'LUSTRO REM' });
```

## 10. Liczba okien odpowiada liczbie pokoi: ogrod_hipnosa.

**ZNAJDŹ**

```javascript
      B.building({ id: 'ogrod_hipnosa', subject: 'sny_dziennik', style: 'greenhouse', x: 7, y: 15, w: 8, h: 4, nWin: 3, wall: '#2dd4bf', roof: '#1a0a2e', trim: '#c9a0ff', sign: 'OGRÓD HIPNOSA' });
      B.building({ id: 'wieza_eschera', subject: 'sny_edytor', style: 'babel', x: 25, y: 15, w: 7, h: 5, nWin: 4, wall: '#c9a0ff', roof: '#7b4fcf', trim: '#f0e6ff', sign: 'WIEŻA ESCHERA' });
```

**ZAMIEŃ NA**

```javascript
      B.building({ id: 'ogrod_hipnosa', subject: 'sny_dziennik', style: 'greenhouse', x: 7, y: 15, w: 8, h: 4, nWin: 2, wall: '#2dd4bf', roof: '#1a0a2e', trim: '#c9a0ff', sign: 'OGRÓD HIPNOSA' });
      B.building({ id: 'wieza_eschera', subject: 'sny_edytor', style: 'babel', x: 25, y: 15, w: 7, h: 5, nWin: 4, wall: '#c9a0ff', roof: '#7b4fcf', trim: '#f0e6ff', sign: 'WIEŻA ESCHERA' });
```

## 11. Liczba okien odpowiada liczbie pokoi: wieza_eschera.

**ZNAJDŹ**

```javascript
      B.building({ id: 'wieza_eschera', subject: 'sny_edytor', style: 'babel', x: 25, y: 15, w: 7, h: 5, nWin: 4, wall: '#c9a0ff', roof: '#7b4fcf', trim: '#f0e6ff', sign: 'WIEŻA ESCHERA' });
      B.obj('fountain', 18, 12, { fw: 4, fh: 3 });
```

**ZAMIEŃ NA**

```javascript
      B.building({ id: 'wieza_eschera', subject: 'sny_edytor', style: 'babel', x: 25, y: 15, w: 7, h: 5, nWin: 1, wall: '#c9a0ff', roof: '#7b4fcf', trim: '#f0e6ff', sign: 'WIEŻA ESCHERA' });
      B.obj('fountain', 18, 12, { fw: 4, fh: 3 });
```

## 12. Opis łóżka odpowiada nowemu przebiegowi snu.

**ZNAJDŹ**

```javascript
      name: 'Łóżko', emoji: '🛏️', pages: [`Jest ${this.timeText()}. Co chcesz zrobić? Możesz zakończyć dzień snem lub wejść w świadomy sen w Katedrze Snu.`],
      options: [
```

**ZAMIEŃ NA**

```javascript
      name: 'Łóżko', emoji: '🛏️', pages: [`Jest ${this.timeText()}. Co chcesz zrobić? Możesz zakończyć dzień zwykłym snem albo zwiedzić senną wersję wybranej dzielnicy. Po przebudzeniu zacznie się nowy dzień.`],
      options: [
```

## 13. Łóżko zapowiada wybór dzielnicy zamiast teleportacji na wyspę.

**ZNAJDŹ**

```javascript
        { label: '✨ Śnij świadomie (Wyspa Snu)', fn: () => this.enterDreamFromBed() },
        { label: 'Jeszcze nie', fn: null }
```

**ZAMIEŃ NA**

```javascript
        { label: '✨ Śnij świadomie · wybierz dzielnicę', fn: () => this.enterDreamFromBed() },
        { label: 'Jeszcze nie', fn: null }
```

## 14. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          { q: 'Dlaczego technikę WBTB wykonuje się po ok. 5–6 godzinach snu, a nie po 2 godzinach?', a: ['W drugiej połowie nocy epizody fazy REM są najdłuższe i najgęstsze', 'Wtedy temperatura ciała osiąga absolutne maksimum', 'Po 2 godzinach w mózgu nie ma jeszcze neuroprzekaźników', 'Wtedy całkowicie wyłącza się hipokamp'], why: 'Faza REM wydłuża się w kolejnych cyklach ultradialnych — w ostatnich cyklach epizod REM może trwać nawet 40–60 minut.' },
          { q: 'Co dzieje się z poziomem acetylocholiny w fazie REM w porównaniu z fazą NREM?', a: ['Poziom acetylocholiny gwałtownie wzrasta, zbliżając się do poziomu czuwania', 'Spada do zera', 'Zostaje całkowicie zastąpiony serotoniną', 'Nie ulega żadnym zmianom'], why: 'W fazie REM poziom acetylocholiny w korze jest wysoki (sprzyja plastyczności i marzeniom sennym), podczas gdy noradrenalina i serotonina są wyciszone.' },
```

**ZAMIEŃ NA**

```javascript
          { q: 'Dlaczego technikę WBTB wykonuje się po ok. 5–6 godzinach snu, a nie po 2 godzinach?', a: ['W drugiej połowie nocy epizody fazy REM są najdłuższe i najgęstsze', 'Wtedy temperatura ciała osiąga absolutne maksimum', 'Po 2 godzinach w mózgu nie ma jeszcze neuroprzekaźników', 'Wtedy całkowicie wyłącza się hipokamp'], why: 'Faza REM wydłuża się w kolejnych cyklach ultradiańskich — w ostatnich cyklach epizod REM może trwać nawet 40–60 minut.' },
          { q: 'Co dzieje się z poziomem acetylocholiny w fazie REM w porównaniu z fazą NREM?', a: ['Poziom acetylocholiny gwałtownie wzrasta, zbliżając się do poziomu czuwania', 'Spada do zera', 'Zostaje całkowicie zastąpiony serotoniną', 'Nie ulega żadnym zmianom'], why: 'W fazie REM poziom acetylocholiny w korze jest wysoki (sprzyja plastyczności i marzeniom sennym), podczas gdy noradrenalina i serotonina są wyciszone.' },
```

## 15. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          'Początek kolejnego cyklu ultradialnego (ok. 90-110 minut)'
        ],
```

**ZAMIEŃ NA**

```javascript
          'Początek kolejnego cyklu ultradiańskiego (ok. 90-110 minut)'
        ],
```

## 16. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
    intro: 'W gotyckiej nawie Katedry zgłębisz pięć filarów świadomego śnienia: reality checks, intencję prospektywną MILD, chronobiologię WBTB, techniki stabilizacji projekcji oraz kontrolę woli we śnie.',
    rooms: [
```

**ZAMIEŃ NA**

```javascript
    intro: 'W gotyckiej nawie Katedry poznasz cztery obszary: testy rzeczywistości, intencję MILD, metodę WBTB oraz różnicę między relacjami śniących a dowodami naukowymi.',
    rooms: [
```

## 17. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Próba przeczytania tekstu dwa razy we śnie niemal zawsze daje inny tekst lub zamazany napis.', true, 'Tekst i cyfry są niestabilne przez obniżoną aktywność grzbietowo-bocznej kory przedczołowej (DLPFC).'],
          ['We śnie nie da się spojrzeć na własne dłonie.', false, 'Można, ale dłonie często mają zniekształconą liczbę palców lub falują — to klasyczny test LaBerge’a.'],
```

**ZAMIEŃ NA**

```javascript
          ['Zmiana napisu przy ponownym spojrzeniu może być wskazówką, że śnimy, ale nie jest niezawodnym testem.', true, 'Treść snu bywa niestabilna, lecz napis może też pozostać taki sam. Nie ma tu prostej reguły dotyczącej jednego obszaru mózgu.'],
          ['We śnie nie da się spojrzeć na własne dłonie.', false, 'Można, ale dłonie często mają zniekształconą liczbę palców lub falują — to klasyczny test LaBerge’a.'],
```

## 18. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Test zatykania nosa i próby oddychania działa we śnie, ponieważ ciało fizyczne nadal oddycha.', true, 'Mózg odbiera sygnał z pnia mózgu o drożności dróg oddechowych, więc we śnie możesz oddychać przez zaciśnięty nos.'],
          ['Włączniki światła we śnie działają tak samo niezawodnie jak na jawie.', false, 'Próba włączenia światła we śnie często nie zmienia jasności otoczenia — to częsty wskaźnik snu (dream sign).'],
```

**ZAMIEŃ NA**

```javascript
          ['W relacjach o snach pojawia się możliwość oddychania mimo zatkania nosa we śnie.', true, 'Nos w scenie sennej nie musi odpowiadać rzeczywistemu ułożeniu ciała. To opisywany test rzeczywistości, ale jego niezawodność i dokładny mechanizm nie są ustalone.'],
          ['Włączniki światła we śnie działają tak samo niezawodnie jak na jawie.', false, 'Próba włączenia światła we śnie często nie zmienia jasności otoczenia — to częsty wskaźnik snu (dream sign).'],
```

## 19. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['We śnie nie da się spojrzeć na własne dłonie.', false, 'Można, ale dłonie często mają zniekształconą liczbę palców lub falują — to klasyczny test LaBerge’a.'],
          ['W relacjach o snach pojawia się możliwość oddychania mimo zatkania nosa we śnie.', true, 'Nos w scenie sennej nie musi odpowiadać rzeczywistemu ułożeniu ciała. To opisywany test rzeczywistości, ale jego niezawodność i dokładny mechanizm nie są ustalone.'],
```

**ZAMIEŃ NA**

```javascript
          ['We śnie nie da się spojrzeć na własne dłonie.', false, 'Można widzieć dłonie we śnie. Mogą wyglądać zwyczajnie albo nietypowo; liczenie palców nie daje pewności.'],
          ['W relacjach o snach pojawia się możliwość oddychania mimo zatkania nosa we śnie.', true, 'Nos w scenie sennej nie musi odpowiadać rzeczywistemu ułożeniu ciała. To opisywany test rzeczywistości, ale jego niezawodność i dokładny mechanizm nie są ustalone.'],
```

## 20. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Włączniki światła we śnie działają tak samo niezawodnie jak na jawie.', false, 'Próba włączenia światła we śnie często nie zmienia jasności otoczenia — to częsty wskaźnik snu (dream sign).'],
          ['Zegary cyfrowe we śnie zawsze pokazują poprawny czas lokalny.', false, 'Zegary cyfrowe we śnie zmieniają cyfry w chaotyczny sposób przy ponownym spojrzeniu.']
```

**ZAMIEŃ NA**

```javascript
          ['Włączniki światła we śnie działają tak samo niezawodnie jak na jawie.', false, 'Światło we śnie może zachowywać się różnie. Nietypowe działanie włącznika bywa wskazówką, a nie pewnym rozstrzygnięciem.'],
          ['Zegary cyfrowe we śnie zawsze pokazują poprawny czas lokalny.', false, 'Zegary cyfrowe we śnie zmieniają cyfry w chaotyczny sposób przy ponownym spojrzeniu.']
```

## 21. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Zegary cyfrowe we śnie zawsze pokazują poprawny czas lokalny.', false, 'Zegary cyfrowe we śnie zmieniają cyfry w chaotyczny sposób przy ponownym spojrzeniu.']
        ] },
```

**ZAMIEŃ NA**

```javascript
          ['Zegary cyfrowe we śnie zawsze pokazują poprawny czas lokalny.', false, 'Nie istnieje zasada, że zegar we śnie zawsze pokazuje poprawny albo zawsze niepoprawny czas.']
        ] },
```

## 22. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          'Rozbudzenie po 4-5 godzinach snu (najlepiej pod koniec fazy NREM)',
          'Przypomnienie sobie i ponowne przeżycie w pamięci ostatniego snu',
```

**ZAMIEŃ NA**

```javascript
          'Przebudzenie ze snu, często z fazy REM, i skierowanie uwagi na zapamiętaną treść',
          'Przypomnienie sobie i ponowne przeżycie w pamięci ostatniego snu',
```

## 23. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
        outro: 'Stephen LaBerge udowodnił obiektywnie świadome śnienie w 1981 r. w Stanfordzie za pomocą umówionych ruchów gałek ocznych (EOG) w fazie REM.' },
      { id: 'wbtb', name: 'Kaplica WBTB & Architektury Snu', icon: '⏰', kind: 'quiz', light: '#2dd4bf',
```

**ZAMIEŃ NA**

```javascript
        outro: 'Keith Hearne zarejestrował umówione sygnały oczne podczas świadomego snu Alana Worsleya w 1975 r. Stephen LaBerge niezależnie zastosował tę metodę; jego zespół opublikował wyniki w 1981 r.' },
      { id: 'wbtb', name: 'Kaplica WBTB & Architektury Snu', icon: '⏰', kind: 'quiz', light: '#2dd4bf',
```

## 24. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          { q: 'Jakie pasmo fal EEG wiąże się w badaniach Voss (2009, 2014) ze świadomością we śnie w fazie REM?', a: ['Fale gamma (~40 Hz) w okolicach czołowo-skroniowych', 'Wolne fale delta (0.5–2 Hz) w potylicy', 'Wrzeciona senne (12–14 Hz)', 'Fale theta w pniu mózgu'], why: 'Stymulacja tACS prądem o częstotliwości 40 Hz (gamma) nad okolicami czołowymi indukuje u śniących wgląd i lucidity.' }
        ] },
```

**ZAMIEŃ NA**

```javascript
          { q: 'Jak ostrożnie odczytać wynik badania Voss i współpracowników z 2014 r.?', a: ['Odnotowano wzrost niektórych ocen samoświadomości po stymulacji; nie dowodzi to niezawodnego wywoływania świadomych snów', 'Ustalono metodę działającą u każdej osoby', 'Każdy wzrost gamma dowodzi świadomego snu', 'Badanie dowodzi, że sny nie występują w REM'], why: 'Wynik oparto m.in. na ocenach kwestionariuszowych. Wzrost części skal nie jest tym samym co niezależnie potwierdzony świadomy sen.' }
        ] },
```

## 25. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          { q: 'Dlaczego technikę WBTB wykonuje się po ok. 5–6 godzinach snu, a nie po 2 godzinach?', a: ['W drugiej połowie nocy epizody fazy REM są najdłuższe i najgęstsze', 'Wtedy temperatura ciała osiąga absolutne maksimum', 'Po 2 godzinach w mózgu nie ma jeszcze neuroprzekaźników', 'Wtedy całkowicie wyłącza się hipokamp'], why: 'Faza REM wydłuża się w kolejnych cyklach ultradiańskich — w ostatnich cyklach epizod REM może trwać nawet 40–60 minut.' },
          { q: 'Co dzieje się z poziomem acetylocholiny w fazie REM w porównaniu z fazą NREM?', a: ['Poziom acetylocholiny gwałtownie wzrasta, zbliżając się do poziomu czuwania', 'Spada do zera', 'Zostaje całkowicie zastąpiony serotoniną', 'Nie ulega żadnym zmianom'], why: 'W fazie REM poziom acetylocholiny w korze jest wysoki (sprzyja plastyczności i marzeniom sennym), podczas gdy noradrenalina i serotonina są wyciszone.' },
```

**ZAMIEŃ NA**

```javascript
          { q: 'Dlaczego technikę WBTB wykonuje się po ok. 5–6 godzinach snu, a nie po 2 godzinach?', a: ['W drugiej połowie nocy epizody REM są zwykle dłuższe', 'Wtedy temperatura ciała osiąga absolutne maksimum', 'Po 2 godzinach w mózgu nie ma jeszcze neuroprzekaźników', 'Wtedy całkowicie wyłącza się hipokamp'], why: 'Faza REM wydłuża się w kolejnych cyklach ultradiańskich — w ostatnich cyklach epizod REM może trwać nawet 40–60 minut.' },
          { q: 'Co dzieje się z poziomem acetylocholiny w fazie REM w porównaniu z fazą NREM?', a: ['Poziom acetylocholiny gwałtownie wzrasta, zbliżając się do poziomu czuwania', 'Spada do zera', 'Zostaje całkowicie zastąpiony serotoniną', 'Nie ulega żadnym zmianom'], why: 'W fazie REM poziom acetylocholiny w korze jest wysoki (sprzyja plastyczności i marzeniom sennym), podczas gdy noradrenalina i serotonina są wyciszone.' },
```

## 26. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          { q: 'Dlaczego technikę WBTB wykonuje się po ok. 5–6 godzinach snu, a nie po 2 godzinach?', a: ['W drugiej połowie nocy epizody REM są zwykle dłuższe', 'Wtedy temperatura ciała osiąga absolutne maksimum', 'Po 2 godzinach w mózgu nie ma jeszcze neuroprzekaźników', 'Wtedy całkowicie wyłącza się hipokamp'], why: 'Faza REM wydłuża się w kolejnych cyklach ultradiańskich — w ostatnich cyklach epizod REM może trwać nawet 40–60 minut.' },
          { q: 'Co dzieje się z poziomem acetylocholiny w fazie REM w porównaniu z fazą NREM?', a: ['Poziom acetylocholiny gwałtownie wzrasta, zbliżając się do poziomu czuwania', 'Spada do zera', 'Zostaje całkowicie zastąpiony serotoniną', 'Nie ulega żadnym zmianom'], why: 'W fazie REM poziom acetylocholiny w korze jest wysoki (sprzyja plastyczności i marzeniom sennym), podczas gdy noradrenalina i serotonina są wyciszone.' },
```

**ZAMIEŃ NA**

```javascript
          { q: 'Dlaczego technikę WBTB wykonuje się po ok. 5–6 godzinach snu, a nie po 2 godzinach?', a: ['W drugiej połowie nocy epizody REM są zwykle dłuższe', 'Wtedy temperatura ciała osiąga absolutne maksimum', 'Po 2 godzinach w mózgu nie ma jeszcze neuroprzekaźników', 'Wtedy całkowicie wyłącza się hipokamp'], why: 'Epizody REM zwykle wydłużają się w kolejnych cyklach ultradiańskich. Długość cykli jest zmienna; to nie zegar odliczający zawsze dokładnie 90 minut.' },
          { q: 'Co dzieje się z poziomem acetylocholiny w fazie REM w porównaniu z fazą NREM?', a: ['Poziom acetylocholiny gwałtownie wzrasta, zbliżając się do poziomu czuwania', 'Spada do zera', 'Zostaje całkowicie zastąpiony serotoniną', 'Nie ulega żadnym zmianom'], why: 'W fazie REM poziom acetylocholiny w korze jest wysoki (sprzyja plastyczności i marzeniom sennym), podczas gdy noradrenalina i serotonina są wyciszone.' },
```

## 27. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
        intro: 'Gdy zorientujesz się, że śnisz, emocje mogą Cię wybudzić. Posortuj techniki stabilizacji snu i czynniki destabilizujące.',
        bins: ['Techniki stabilizujące sen', 'Czynniki grożące wybudzeniem'],
```

**ZAMIEŃ NA**

```javascript
        intro: 'Oddzielmy relacje o technikach stabilizacji od obietnic bez pokrycia. Przyporządkuj stwierdzenia do kategorii.',
        bins: ['Techniki stabilizujące sen', 'Czynniki grożące wybudzeniem'],
```

## 28. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
        bins: ['Techniki stabilizujące sen', 'Czynniki grożące wybudzeniem'],
        items: [
```

**ZAMIEŃ NA**

```javascript
        bins: ['Opisywana praktyka — bez gwarancji', 'Nieuprawniona pewność'],
        items: [
```

## 29. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Pocieranie dłoni o siebie (stymulacja proprioceptywna)', 0],
          ['Gwałtowny skok emocji i euforia („O rety, śnię!”)', 1],
```

**ZAMIEŃ NA**

```javascript
          ['Niektóre osoby opisują pocieranie dłoni we śnie jako pomoc w skupieniu uwagi.', 0],
          ['Gwałtowny skok emocji i euforia („O rety, śnię!”)', 1],
```

## 30. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Gwałtowny skok emocji i euforia („O rety, śnię!”)', 1],
          ['Obracanie się wokół własnej osi (spinning)', 0],
```

**ZAMIEŃ NA**

```javascript
          ['Silna emocja zawsze natychmiast kończy każdy świadomy sen.', 1],
          ['Obracanie się wokół własnej osi (spinning)', 0],
```

## 31. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Obracanie się wokół własnej osi (spinning)', 0],
          ['Skupienie uwagi na detalach dotykowych podłoża', 0],
```

**ZAMIEŃ NA**

```javascript
          ['Obracanie się we śnie pojawia się w relacjach o próbach jego podtrzymania.', 0],
          ['Skupienie uwagi na detalach dotykowych podłoża', 0],
```

## 32. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Skupienie uwagi na detalach dotykowych podłoża', 0],
          ['Próba poruszenia fizycznymi powiekami', 1],
```

**ZAMIEŃ NA**

```javascript
          ['Kierowanie uwagi na szczegóły otoczenia jest opisywaną praktyką śniących.', 0],
          ['Próba poruszenia fizycznymi powiekami', 1],
```

## 33. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Próba poruszenia fizycznymi powiekami', 1],
          ['Komenda głosowa: „Zwiększ jasność i stabilność!”', 0],
```

**ZAMIEŃ NA**

```javascript
          ['Wystarczy jedna technika, żeby każda osoba sterowała każdym snem.', 1],
          ['Komenda głosowa: „Zwiększ jasność i stabilność!”', 0],
```

## 34. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Komenda głosowa: „Zwiększ jasność i stabilność!”', 0],
          ['Zbyt długie wpatrywanie się w jeden nieruchomy punkt', 1],
```

**ZAMIEŃ NA**

```javascript
          ['Niektóre osoby próbują zmieniać sen przez wypowiadanie intencji.', 0],
          ['Zbyt długie wpatrywanie się w jeden nieruchomy punkt', 1],
```

## 35. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Zbyt długie wpatrywanie się w jeden nieruchomy punkt', 1],
          ['Świadome pogłębienie oddechu wewnątrz snu', 0]
```

**ZAMIEŃ NA**

```javascript
          ['Wpatrywanie się w punkt zawsze powoduje przebudzenie.', 1],
          ['Świadome pogłębienie oddechu wewnątrz snu', 0]
```

## 36. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Świadome pogłębienie oddechu wewnątrz snu', 0]
        ] }
```

**ZAMIEŃ NA**

```javascript
          ['Doświadczenia i skuteczność opisywanych praktyk różnią się między osobami.', 0]
        ] }
```

## 37. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
        intro: 'Stickgold i Walker wykazali, że różne fazy snu konsolidują różne rodzaje pamięci. Przyporządkuj rodzaje wiedzy do fazy snu:',
        bins: ['Głównie sen wolnofalowy (N3 / SWS)', 'Głównie faza REM'],
```

**ZAMIEŃ NA**

```javascript
        intro: 'Sen wspiera pamięć, ale proste przypisanie każdej umiejętności jednej fazie jest mylące. Oddziel ostrożne wnioski od nadmiernych uproszczeń:',
        bins: ['Głównie sen wolnofalowy (N3 / SWS)', 'Głównie faza REM'],
```

## 38. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
        bins: ['Głównie sen wolnofalowy (N3 / SWS)', 'Głównie faza REM'],
        items: [
```

**ZAMIEŃ NA**

```javascript
        bins: ['Ostrożny wniosek', 'Nadmierne uproszczenie'],
        items: [
```

## 39. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Fakty deklaratywne (daty, definicje, pojęcia)', 0],
          ['Pamięć emocjonalna i modulacja afektu', 1],
```

**ZAMIEŃ NA**

```javascript
          ['NREM jest powiązany z konsolidacją pamięci deklaratywnej.', 0],
          ['Pamięć emocjonalna i modulacja afektu', 1],
```

## 40. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Pamięć emocjonalna i modulacja afektu', 1],
          ['Pamięć semantyczna (sieci pojęciowe i integracja)', 0],
```

**ZAMIEŃ NA**

```javascript
          ['Każde wspomnienie emocjonalne jest przetwarzane wyłącznie w REM.', 1],
          ['Pamięć semantyczna (sieci pojęciowe i integracja)', 0],
```

## 41. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Pamięć semantyczna (sieci pojęciowe i integracja)', 0],
          ['Twórcze łączenie odległych skojarzeń (insight)', 1],
```

**ZAMIEŃ NA**

```javascript
          ['Różne procesy snu mogą współdziałać w utrwalaniu i reorganizacji wspomnień.', 0],
          ['Twórcze łączenie odległych skojarzeń (insight)', 1],
```

## 42. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Twórcze łączenie odległych skojarzeń (insight)', 1],
          ['Pamięć przestrzenna (mapy poznawcze hipokampa)', 0],
```

**ZAMIEŃ NA**

```javascript
          ['Każdy twórczy pomysł powstaje wyłącznie podczas REM.', 1],
          ['Pamięć przestrzenna (mapy poznawcze hipokampa)', 0],
```

## 43. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Pamięć przestrzenna (mapy poznawcze hipokampa)', 0],
          ['Integracja reguł gramatycznych i schematów złożonych', 1]
```

**ZAMIEŃ NA**

```javascript
          ['Wyniki zależą m.in. od rodzaju zadania i sposobu pomiaru pamięci.', 0],
          ['Integracja reguł gramatycznych i schematów złożonych', 1]
```

## 44. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Integracja reguł gramatycznych i schematów złożonych', 1]
        ] }
```

**ZAMIEŃ NA**

```javascript
          ['Reguły gramatyczne należą wyłącznie do REM, a znaczenia słów wyłącznie do N3.', 1]
        ] }
```

## 45. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Fałszywe przebudzenie to sytuacja, w której śnisz, że się obudziłeś i zaczynasz poranną rutynę.', true, 'Klasyczne zjawisko, często powtarzające się wielokrotnie pod rząd (fałszywe przebudzenie warstwowe).']
        ] },
```

**ZAMIEŃ NA**

```javascript
          ['Fałszywe przebudzenie to sytuacja, w której śnisz, że właśnie nastąpiło przebudzenie i zaczyna się poranna rutyna.', true, 'Klasyczne zjawisko, często powtarzające się wielokrotnie pod rząd (fałszywe przebudzenie warstwowe).']
        ] },
```

## 46. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Prowadzenie dziennika snów natychmiast poprawia wskaźnik przypominania marzeń sennych (dream recall).', true, 'Zapisywanie snów tuż po przebudzeniu wzmacnia ich ślad przed zanikiem w pamięci roboczej.'],
          ['Fałszywe przebudzenie to sytuacja, w której śnisz, że właśnie nastąpiło przebudzenie i zaczyna się poranna rutyna.', true, 'Klasyczne zjawisko, często powtarzające się wielokrotnie pod rząd (fałszywe przebudzenie warstwowe).']
```

**ZAMIEŃ NA**

```javascript
          ['Dziennik snów gwarantuje natychmiastową poprawę pamięci snów u każdej osoby.', false, 'Zapisywanie pomaga zachować dostępną relację. Nie gwarantuje jednak jednakowej ani natychmiastowej poprawy przypominania.'],
          ['Fałszywe przebudzenie to sytuacja, w której śnisz, że właśnie nastąpiło przebudzenie i zaczyna się poranna rutyna.', true, 'Klasyczne zjawisko, często powtarzające się wielokrotnie pod rząd (fałszywe przebudzenie warstwowe).']
```

## 47. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Allan Hobson', 'Model aktywacji-syntezy (AIM): kora próbuje nadać sens losowym wyładowaniom pnia'],
          ['Antti Revonsuo', 'Teoria symulacji zagrożeń: sen jako ewolucyjny trening radzenia sobie z niebezpieczeństwem'],
```

**ZAMIEŃ NA**

```javascript
          ['Hobson i McCarley — aktywacja-synteza', 'Hipoteza z 1977 r.: mózg syntetyzuje doświadczenie senne na podstawie aktywności neuronalnej'],
          ['Hobson i współpracownicy — AIM', 'Późniejszy model stanów świadomości: aktywacja, źródło informacji i modulacja neurochemiczna'],
          ['Antti Revonsuo', 'Teoria symulacji zagrożeń: sen jako ewolucyjny trening radzenia sobie z niebezpieczeństwem'],
```

## 48. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
        intro: 'Połącz teorie marzeń sennych z ich autorami i główną tezą:',
        pairs: [
```

**ZAMIEŃ NA**

```javascript
        intro: 'Połącz autorów i modele z ich tezami. To różne propozycje teoretyczne, nie jednakowo potwierdzone fakty:',
        pairs: [
```

## 49. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Francis Crick', 'Oduczanie (unlearning): usuwanie pasożytniczych połączeń neuronalnych'],
          ['Matthew Walker', 'Nocna terapia emocjonalna: sen zdejmuje ładunek afektywny ze wspomnień']
```

**ZAMIEŃ NA**

```javascript
          ['Francis Crick i Graeme Mitchison', 'Hipoteza uczenia odwróconego: osłabianie niepożądanych wzorców w sieciach neuronalnych'],
          ['Matthew Walker', 'Nocna terapia emocjonalna: sen zdejmuje ładunek afektywny ze wspomnień']
```

## 50. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Matthew Walker', 'Nocna terapia emocjonalna: sen zdejmuje ładunek afektywny ze wspomnień']
        ] }
```

**ZAMIEŃ NA**

```javascript
          ['Walker i van der Helm', 'Hipoteza roli REM w przetwarzaniu emocjonalnych aspektów wspomnień']
        ] }
```

## 51. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
        intro: 'Świat snu nie musi podlegać fizyce newtonowskiej. Przyporządkuj zjawiska do kategorii:',
        bins: ['Zjawiska możliwe do modulacji w LD', 'Biologiczne ograniczenia percepcji'],
```

**ZAMIEŃ NA**

```javascript
        intro: 'Rozróżnij świadomość śnienia i kontrolę treści snu. To dwie różne rzeczy:',
        bins: ['Zjawiska możliwe do modulacji w LD', 'Biologiczne ograniczenia percepcji'],
```

## 52. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
        bins: ['Zjawiska możliwe do modulacji w LD', 'Biologiczne ograniczenia percepcji'],
        items: [
```

**ZAMIEŃ NA**

```javascript
        bins: ['Świadomość śnienia', 'Kontrola treści snu'],
        items: [
```

## 53. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Zmiana grawitacji i lewitacja', 0],
          ['Natychmiastowa transformacja pory roku z lata na zimę', 0],
```

**ZAMIEŃ NA**

```javascript
          ['Rozpoznanie podczas snu: „Teraz śnię”.', 0],
          ['Natychmiastowa transformacja pory roku z lata na zimę', 0],
```

## 54. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Natychmiastowa transformacja pory roku z lata na zimę', 0],
          ['Brak możliwości jednoczesnego widzenia w 360 stopniach bez treningu', 1],
```

**ZAMIEŃ NA**

```javascript
          ['Celowa zmiana pogody w treści snu.', 1],
          ['Brak możliwości jednoczesnego widzenia w 360 stopniach bez treningu', 1],
```

## 55. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Brak możliwości jednoczesnego widzenia w 360 stopniach bez treningu', 1],
          ['Zamiana materiałów (budynki ze szkła lub cukierków)', 0],
```

**ZAMIEŃ NA**

```javascript
          ['Uświadomienie sobie, że otoczenie jest snem, bez możliwości jego zmiany.', 0],
          ['Zamiana materiałów (budynki ze szkła lub cukierków)', 0],
```

## 56. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Zamiana materiałów (budynki ze szkła lub cukierków)', 0],
          ['Konieczność utrzymania stałego oddechu ciała biologicznego', 1],
```

**ZAMIEŃ NA**

```javascript
          ['Celowe przekształcenie sennego budynku w cukierkowy dom.', 1],
          ['Konieczność utrzymania stałego oddechu ciała biologicznego', 1],
```

## 57. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Konieczność utrzymania stałego oddechu ciała biologicznego', 1],
          ['Zatrzymanie upływu czasu subiektywnego', 0]
```

**ZAMIEŃ NA**

```javascript
          ['Zorientowanie się, że pozorne przebudzenie nadal jest snem.', 0],
          ['Zatrzymanie upływu czasu subiektywnego', 0]
```

## 58. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Zatrzymanie upływu czasu subiektywnego', 0]
        ] }
```

**ZAMIEŃ NA**

```javascript
          ['Celowe wywołanie latania w treści snu.', 1]
        ] }
```

## 59. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          <p class="small mt">Wybierz przestrzeń snu i nałóż prawa, którymi ma się rządzić. Jako Oneironauta możesz dowolnie modulować otoczenie!</p>
        </div>
```

**ZAMIEŃ NA**

```javascript
          <p class="small mt">Wybierz przestrzeń snu i nałóż prawa, którymi ma się rządzić. We śnie możesz ćwiczyć zmianę otoczenia!</p>
        </div>
```

## 60. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
    greet: 'Witaj w Katedrze Snu. Jestem Morfeusza — Oneironautka. Nauczę cię, jak przejąć kontrolę nad swoimi snami.',
    lines: ['Sen to nie ucieczka od rzeczywistości — to drugie laboratorium umysłu.', 'Hipokamp nie śpi, gdy ty śpisz. Konsoliduje, reorganizuje, łączy.', 'Faza REM: oczy się ruszają, ciało jest sparaliżowane, a umysł tworzy światy. Fascynujące, prawda?', 'Lucidity to świadomość we śnie. Im więcej trenujesz, tym częściej ją osiągniesz.', 'Paracelsus mówił: „Sen jest mikrokosmos śmierci." Ja wolę: sen jest mikrokosmos twórczości.', 'Śniło ci się kiedyś, że zdajesz egzamin nago przed komisją? Spokojnie — komisji też się to śni.', 'Faza wolnofalowa NREM: fale delta płyną przez korę, a mózg dosłownie spłukuje metabolity. Taki biologiczny zmywak po całym dniu kognitywnego potu.', 'Zjawisko paraliżu sennego: budzisz się, ciało jak z ołowiu, a w kącie majaczy cień. Spokojnie! To tylko pień mózgu zapomniał zwolnić hamulec motoryczny.', 'Dziennik snów kładź przy łóżku. Zapisuj natychmiast po przebudzeniu, zanim hipokamp oznaczy te wspomnienia jako spam i skasuje.'] },
```

**ZAMIEŃ NA**

```javascript
    greet: 'Witaj w Katedrze Snu. Jestem Morfeusza. Poznamy naukę o snach, a w sennej wersji miasta poćwiczymy wyobraźnię.',
    lines: ['Sen to nie ucieczka od rzeczywistości — to drugie laboratorium umysłu.', 'Hipokamp nie śpi, gdy ty śpisz. Konsoliduje, reorganizuje, łączy.', 'Faza REM: oczy się ruszają, ciało jest sparaliżowane, a umysł tworzy światy. Fascynujące, prawda?', 'Lucidity to świadomość we śnie. Im więcej trenujesz, tym częściej ją osiągniesz.', 'Paracelsus mówił: „Sen jest mikrokosmos śmierci." Ja wolę: sen jest mikrokosmos twórczości.', 'Śniło ci się kiedyś, że zdajesz egzamin nago przed komisją? Spokojnie — komisji też się to śni.', 'Faza wolnofalowa NREM: fale delta płyną przez korę, a mózg dosłownie spłukuje metabolity. Taki biologiczny zmywak po całym dniu kognitywnego potu.', 'Zjawisko paraliżu sennego: budzisz się, ciało jak z ołowiu, a w kącie majaczy cień. Spokojnie! To tylko pień mózgu zapomniał zwolnić hamulec motoryczny.', 'Dziennik snów kładź przy łóżku. Zapisuj natychmiast po przebudzeniu, zanim hipokamp oznaczy te wspomnienia jako spam i skasuje.'] },
```

## 61. Morfeusza przekazuje ostrożne, poprawione informacje bez fałszywego cytatu.

**ZNAJDŹ**

```javascript
    lines: ['Sen to nie ucieczka od rzeczywistości — to drugie laboratorium umysłu.', 'Hipokamp nie śpi, gdy ty śpisz. Konsoliduje, reorganizuje, łączy.', 'Faza REM: oczy się ruszają, ciało jest sparaliżowane, a umysł tworzy światy. Fascynujące, prawda?', 'Lucidity to świadomość we śnie. Im więcej trenujesz, tym częściej ją osiągniesz.', 'Paracelsus mówił: „Sen jest mikrokosmos śmierci." Ja wolę: sen jest mikrokosmos twórczości.', 'Śniło ci się kiedyś, że zdajesz egzamin nago przed komisją? Spokojnie — komisji też się to śni.', 'Faza wolnofalowa NREM: fale delta płyną przez korę, a mózg dosłownie spłukuje metabolity. Taki biologiczny zmywak po całym dniu kognitywnego potu.', 'Zjawisko paraliżu sennego: budzisz się, ciało jak z ołowiu, a w kącie majaczy cień. Spokojnie! To tylko pień mózgu zapomniał zwolnić hamulec motoryczny.', 'Dziennik snów kładź przy łóżku. Zapisuj natychmiast po przebudzeniu, zanim hipokamp oznaczy te wspomnienia jako spam i skasuje.'] },

  // --- Bulwar Empatii ---
```

**ZAMIEŃ NA**

```javascript
    lines: ['Sen też jest ciekawym tematem badań. Tylko trudniej zaprosić go na wywiad.', 'Podczas snu mózg nadal jest aktywny; różne procesy wspierają utrwalanie i reorganizację wspomnień.', 'W REM występują szybkie ruchy oczu i znaczne obniżenie napięcia wielu mięśni. Oddychanie nadal trwa.', 'Świadomy sen oznacza rozpoznanie, że się śni. Nie musi oznaczać kontroli nad fabułą.', 'W naszej grze praktyka odblokowuje możliwości. W prawdziwym życiu nie ma drabinki gwarantującej latanie po ośmiu nocach.', 'Egzamin we śnie? Oby komisja pamiętała, że nie wolno oceniać bez jasnych kryteriów.', 'N3 to sen wolnofalowy. Nie jest jedyną fazą ważną dla pamięci ani prostym trybem sprzątania mózgu.', 'Paraliż senny to przejściowe nakładanie się świadomości otoczenia i atonii związanej z REM. Może być nieprzyjemny; nawracające, uciążliwe epizody warto omówić ze specjalistą.', 'Dziennik zachowuje to, co pamiętasz po przebudzeniu. Nie trzeba dopowiadać brakujących scen.'] },

  // --- Bulwar Empatii ---
```

## 62. Poprawa treści edukacyjnej o śnie.

**ZNAJDŹ**

```javascript
          ['Paraliż senny jest groźną chorobą uszkadzającą mięśnie.', false, 'To naturalna atonia fazy REM, która wyjątkowo nakłada się na stan czuwania. Jest nieszkodliwa, choć subiektywnie przerażająca.'],
          ['Dziennik snów gwarantuje natychmiastową poprawę pamięci snów u każdej osoby.', false, 'Zapisywanie pomaga zachować dostępną relację. Nie gwarantuje jednak jednakowej ani natychmiastowej poprawy przypominania.'],
```

**ZAMIEŃ NA**

```javascript
          ['Paraliż senny sam w sobie oznacza uszkodzenie mięśni.', false, 'To przejściowa niemożność ruchu przy zasypianiu lub budzeniu, związana z atonią REM. Bywa silnie nieprzyjemny; nawracające, uciążliwe epizody warto skonsultować.'],
          ['Dziennik snów gwarantuje natychmiastową poprawę pamięci snów u każdej osoby.', false, 'Zapisywanie pomaga zachować dostępną relację. Nie gwarantuje jednak jednakowej ani natychmiastowej poprawy przypominania.'],
```

## 63. System sesji snu, treningu, koszmarów i latania

Nowy blok zastępuje metody dawnego prototypu snu oraz rozszerza istniejące metody gry.

**WSTAW PO**

```javascript
   START
   ===================================================================== */
let game = null;
```

```javascript
/* Katedra Snu v2 — postęp jest trwały, świat snu jest osobną instancją. */
const DREAM_LOCATIONS = ["rynek", "plaza", "las", "wzgorze", "bulwar", "osiedle", "port", "blonia", "wyparte"];
const DREAM_MODS = {
  season: { name: "Pory roku", lp: 0, days: 0, options: [["normal", "Lato"], ["jesien", "Jesień"], ["zima", "Zima"], ["wiosna", "Wiosna"]] },
  weather: { name: "Pogoda", lp: 40, days: 2, options: [["clear", "Czyste niebo"], ["rain", "Fioletowy deszcz"], ["snow", "Śnieg"], ["fog", "Mgła REM"]] },
  material: { name: "Materiały", lp: 100, days: 4, options: [["default", "Zwykłe materiały"], ["cukierki", "Wszystko z cukierków"], ["czekolada", "Czekolada"], ["krysztal", "Kryształ"]] },
  style: { name: "Barwy wyobraźni", lp: 100, days: 4, options: [["none", "Naturalne"], ["sepia", "Sepia"], ["negatyw", "Negatyw"], ["psychedelic", "Tęczowy świat"]] },
  gravity: { name: "Grawitacja", lp: 160, days: 6, options: [["normal", "Zwykła"], ["low", "Lekkość"], ["inverted", "Odwrócona grawitacja"], ["flying", "Latanie"]] }
};
const DREAM_FLIGHT = [
  { id: "stable", name: "Utrzymaj stabilny sen", days: 1, lp: 0 },
  { id: "reshape", name: "Zmień otoczenie świadomie", days: 2, lp: 0 },
  { id: "hover", name: "Przećwicz unoszenie i powrót", days: 6, lp: 160 },
  { id: "land", name: "Wystartuj, przeleć i bezpiecznie wyląduj", days: 8, lp: 220 }
];
const DREAM_TASKS = [["count", "Liczenie wstecz"], ["logic", "Zagadka logiczna"], ["memory", "Sekwencja symboli"], ["anomaly", "Co tu nie pasuje?"], ["stroop", "Kolor kontra słowo · Stroop"], ["nback", "Pamięć robocza · n-back"]];
const DREAM_NIGHTMARES = [
  { name: "Egzamin z niczego", story: "Komisja żąda indeksu od twojego cienia. Cień twierdzi, że studiuje zaocznie.", color: "#785079" },
  { name: "Ulice donikąd", story: "Schody kończą się w powietrzu. Drogowskazy wskazują wczoraj. Znajdź punkt oparcia.", color: "#455875" },
  { name: "Cień za plecami", story: "Za tobą sunie cień. Możesz spróbować zmienić ten sen albo obudzić się w każdej chwili.", color: "#352b50" }
];
const dreamBase = {};
["setZone", "startWorld", "save", "bindInput", "updateHUD", "update", "updatePlayer", "blockedAt", "checkEdges", "checkFiszki", "enterDoor", "trigger", "updatePrompt", "drawPlayer", "darkness", "warmth", "sleep", "finishMinigame", "openModal"].forEach(k => { dreamBase[k] = Game.prototype[k]; });

Object.assign(Game.prototype, {
  dreamData() {
    const d = this.state.dream || (this.state.dream = {});
    if (d.version !== 2) {
      d.version = 2; d.lp = Math.max(0, Number(d.lp) || 0);
      d.claimed = {}; d.trainingDays = []; d.flightSteps = {}; d.daily = {};
      d.journal = Array.isArray(d.journal) ? d.journal : [];
      d.fragments = []; d.visited = []; d.challenges = {}; d.techniques = {};
      d.activeMods = {}; d.session = null;
      // Ukończone wcześniej pokoje dostają jednorazowe zaliczenie w nowym systemie.
      Object.keys(SUBJECTS).filter(k => k.startsWith("sny_")).forEach(sid => {
        SUBJECTS[sid].rooms.forEach(r => {
          if (this.state.subj[sid] && this.state.subj[sid][r.id] && this.state.subj[sid][r.id].stars) {
            d.claimed["room:" + sid + ":" + r.id] = true; d.lp += 10;
          }
        });
      });
    }
    if (!Number.isInteger(d.daily.trainingDay)) {
      const completedDay = d.trainingDays.reduce((last, day) => Math.max(last, day), 0);
      d.daily.trainingDay = Math.max(completedDay, d.lastDream ? d.lastDream.day : 0, d.session ? (d.session.startedDay || this.state.day) : 0);
    }
    return d;
  },
  dreamSession() { return this.state && this.state.dream && this.state.dream.version === 2 ? this.state.dream.session : null; },
  dreamDays() { return this.dreamData().trainingDays.length; },
  dreamClarity() { return Math.min(1, 0.25 + this.dreamDays() * 0.075); },
  dreamRequirement(group, value) {
    const d = this.dreamData(), cfg = DREAM_MODS[group];
    if (!cfg || !cfg.options.some(o => o[0] === value)) return "Nieznana opcja";
    if (value === cfg.options[0][0]) return "";
    const flight = value === "flying", lp = flight ? 220 : cfg.lp, days = flight ? 8 : cfg.days;
    const reasons = [];
    if (d.lp < lp) reasons.push(`${lp - d.lp} LP`);
    if (this.dreamDays() < days) reasons.push(`${days - this.dreamDays()} dni treningowych`);
    if (flight && !d.flightSteps.land) reasons.push("ukończenie czterech prób lotu");
    return reasons.length ? "Brakuje: " + reasons.join(" · ") : "";
  },
  dreamCleanMods(mods = {}) {
    const clean = {};
    Object.entries(DREAM_MODS).forEach(([k, cfg]) => {
      clean[k] = this.dreamRequirement(k, mods[k]) ? cfg.options[0][0] : mods[k];
    });
    return clean;
  },
  dreamReward(key, points, reason) {
    const d = this.dreamData();
    if (d.claimed[key]) return false;
    d.claimed[key] = true; d.lp += points;
    d.unlockedMods = Object.keys(DREAM_MODS).filter(k => !this.dreamRequirement(k, DREAM_MODS[k].options[1][0]));
    this.toast(`+${points} LP · ${reason} · Razem ${d.lp} LP`); audio.coin();
    this.save(); this.updateHUD(); return true;
  },
  // Dawne punkty za samo wejście są celowo wyłączone.
  addLucidity() { return false; },
  dreamTrain(key) {
    const d = this.dreamData(), s = this.dreamSession();
    if (!s) return;
    const changed = !d.trainingDays.includes(this.state.day);
    if (changed) d.trainingDays.push(this.state.day);
    d.challenges[key] = (d.challenges[key] || 0) + 1;
    d.techniques.control = Object.keys(d.challenges).length;
    s.trained = true;
    this.dreamReward("task:" + key, 10, "pierwsze ukończenie zadania");
    if (changed) { this.rebuildDream(); this.toast(`Dzień treningowy ${this.dreamDays()}/8 · sen nabiera wyrazistości.`); }
    this.save(); this.updateHUD();
  },
  bindInput() {
    dreamBase.bindInput.call(this);
    const anchor = document.getElementById("t-dream");
    [["t-dream-task", "🧠 Zadanie", () => this.openDreamTasks()], ["t-flight", "🪶 Lot [F]", () => this.toggleDreamFlight()], ["t-wake", "☀ Obudź się", () => this.wakeDream()]].forEach(([id, label, fn]) => {
      const b = document.createElement("button"); b.id = id; b.className = "tool"; b.textContent = label; b.hidden = true;
      b.addEventListener("click", fn); anchor.parentNode.insertBefore(b, anchor.nextSibling);
    });
    window.addEventListener("keydown", e => {
      if (e.code === "KeyF" && !e.repeat && !this.modalOpen && !this.dialog && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) && this.dreamSession()) this.toggleDreamFlight();
    });
  },
  updateHUD() {
    dreamBase.updateHUD.call(this);
    if (!this.state) return;
    const s = this.dreamSession();
    const wake = document.getElementById("t-wake"), tasks = document.getElementById("t-dream-task"), flight = document.getElementById("t-flight");
    if (wake) { wake.hidden = !s; wake.style.display = s ? "" : "none"; }
    if (tasks) { tasks.hidden = !s; tasks.style.display = s ? "" : "none"; tasks.textContent = s && s.nightmare ? "🧠 Opanuj koszmar" : "🧠 Zadanie"; }
    if (flight) { flight.hidden = !s || !!s.nightmare || !(s.lesson || s.mods.gravity === "flying"); flight.style.display = flight.hidden ? "none" : ""; flight.textContent = s && (s.flying || s.hovering) ? "🪶 Ląduj [F]" : "🪶 Start [F]"; }
    document.getElementById("t-dream").title = s ? "Ustawienia i postęp snu [K]" : "Trening, dziennik snów i postęp [K]";
  },
  startWorld() {
    const d = this.dreamData(), s = d.session;
    this.transition = null; this.scene = "world";
    if (s && DREAM_LOCATIONS.includes(s.loc) && s.origin && ["bed", "mirror"].includes(s.source)) {
      s.mods = this.dreamCleanMods(s.mods); s.flying = false; s.hovering = false; s.lesson = null;
      this.setZone("dream:" + s.loc);
      Object.assign(this.player, s.pos || { x: 320, y: 224 }); this.unstick();
      this.transition = { phase: "in", t: 0 }; this.updateHUD(); return;
    }
    d.session = null; d.activeMods = {};
    dreamBase.startWorld.call(this);
  },
  save(cloud = false) {
    const s = this.dreamSession();
    if (s) s.pos = { x: this.player.x, y: this.player.y, dir: this.player.dir };
    // Sesja, zadania i miejsce powrotu są zwykłymi danymi, bez canvasów i sprite’ów.
    return dreamBase.save.call(this, cloud);
  },
  setZone(id) {
    if (id.startsWith("dream:")) {
      const s = this.dreamSession();
      if (!s || id !== "dream:" + s.loc) return;
      this.zones[id] = this.buildDreamZone(s);
    } else if (this.dreamSession()) return;
    dreamBase.setZone.call(this, id);
    if (id.startsWith("dream:")) { this.fiszki = []; this.particles = []; this.prepareBuildings(this.zone); }
  },
  buildDreamZone(s) {
    const Z = buildZone(s.loc), d = this.dreamData(), mods = s.mods;
    Z.id = "dream:" + s.loc; Z.def = Object.assign({}, Z.def, { name: "Sen · " + Z.def.name, particles: "none" });
    Z.neighbors = {}; Z.exits = {}; Z.pal = Object.assign({}, DEFAULT_PAL, Z.pal);
    Z.npcs = []; Z.interacts = [];
    const seasons = {
      jesien: { grass: "#b78b48", grass2: "#946436", path: "#b48660", water: "#577788" },
      zima: { grass: "#dae4ee", grass2: "#b8cbdd", path: "#b4c5d3", water: "#647f9f" },
      wiosna: { grass: "#8ab967", grass2: "#72a856", path: "#d5be91", water: "#65a9b7" }
    };
    Object.assign(Z.pal, seasons[mods.season] || {});
    const mats = {
      cukierki: ["#eba5c9", "#a8d7c0", "#e8c689", "#fce0bd", "#c96693"],
      czekolada: ["#8a5b42", "#6a4335", "#b0845b", "#ac7652", "#513328"],
      krysztal: ["#9ecfd5", "#91aacf", "#bec8e5", "#d0e8e3", "#7286b5"]
    };
    const mat = mats[mods.material], nightmare = s.nightmare, restored = nightmare ? nightmare.step : 3;
    if (mat && restored === 3) Object.assign(Z.pal, { grass: mat[0], grass2: mat[1], cobble: mat[2], path: mat[2], plaza: mat[3], water: mat[4], sand: mat[3], planks: mat[2], dead: mat[1], moss: mat[0] });
    const peacefulPal = Object.assign({}, Z.pal);
    if (nightmare) Object.keys(Z.pal).forEach(k => { Z.pal[k] = mix(Z.pal[k], DREAM_NIGHTMARES[nightmare.kind].color, 0.63); });
    const nearest = [...Z.buildings].sort((a, b) => Math.hypot(a.doorCol * 16 - this.player.x, a.doorRow * 16 - this.player.y) - Math.hypot(b.doorCol * 16 - this.player.x, b.doorRow * 16 - this.player.y)).slice(0, 2);
    Z.buildings.forEach((b, i) => {
      // Prywatna kopia obiektów z buildZone; prawdziwe budynki nigdy nie zmieniają barw.
      if (b.kind === "home") b.kind = "dream-home";
      b.dreamRestored = restored === 3 || (restored >= 2 && nearest.includes(b));
      if (mat && b.dreamRestored) { b.wall = mat[(i % 2) + 2]; b.roof = mat[i % 2]; b.trim = mat[3]; }
      if (nightmare && !b.dreamRestored) { b.wall = mix(b.wall, "#302b43", 0.6); b.roof = mix(b.roof, "#28243a", 0.7); }
    });
    const treePal = { jesien: ["#76422e", "#a65c32", "#c5883c", "#dbb55d"], zima: ["#7c95ac", "#afc4d5", "#d3dfe7", "#edf0e8"], wiosna: ["#6e9250", "#97b56e", "#d3a7bc", "#f0c3d0"] };
    Z.objects.forEach(o => { if (o.type === "tree" || o.type === "bush") o.dreamPal = mat && restored === 3 ? [mat[4], mat[0], mat[1], mat[3]] : treePal[mods.season]; });
    Z.ground = bakeGround(Z);
    const g = Z.ground.getContext("2d");
    if (nightmare && restored >= 2) {
      const peaceful = bakeGround(Object.assign({}, Z, { pal: peacefulPal }));
      g.save(); g.beginPath(); g.rect(this.player.x - 64, this.player.y - 48, 128, 96); g.clip(); g.drawImage(peaceful, 0, 0); g.restore();
    }
    if (mat && restored === 3) {
      for (let y = 1; y < Z.h - 1; y += 2) for (let x = 1; x < Z.w - 1; x += 2) {
        const px = x * 16 + 5, py = y * 16 + 5;
        g.fillStyle = mat[4];
        if (mods.material === "czekolada") { g.strokeStyle = mat[4]; g.strokeRect(px, py, 11, 8); g.fillStyle = mat[3]; g.fillRect(px + 1, py + 1, 8, 1); }
        else if (mods.material === "cukierki") { g.fillStyle = mat[(x + y) % 4]; g.fillRect(px, py, 6, 4); g.fillRect(px - 2, py + 1, 2, 2); g.fillRect(px + 6, py + 1, 2, 2); }
        else { g.strokeStyle = mat[4]; g.beginPath(); g.moveTo(px + 4, py); g.lineTo(px + 8, py + 6); g.lineTo(px + 3, py + 10); g.closePath(); g.stroke(); }
      }
    }
    const detail = this.dreamDays() < 3 ? 3 : this.dreamDays() < 6 ? 2 : 1;
    if (detail > 1) {
      const [small, sg] = mkCanvas(Math.ceil(Z.ground.width / detail), Math.ceil(Z.ground.height / detail));
      sg.imageSmoothingEnabled = false; sg.drawImage(Z.ground, 0, 0, small.width, small.height);
      g.imageSmoothingEnabled = false; g.clearRect(0, 0, Z.ground.width, Z.ground.height); g.drawImage(small, 0, 0, Z.ground.width, Z.ground.height);
    }
    d.activeMods = Object.assign({}, mods); return Z;
  },
  rebuildDream() {
    const s = this.dreamSession(); if (!s) return;
    const p = { x: this.player.x, y: this.player.y, dir: this.player.dir };
    this.setZone("dream:" + s.loc); Object.assign(this.player, p);
    if (!s.flying) this.unstick();
  },
  enterDreamFromBed() { this.openDreamModulation("bed"); },
  dreamTrainingUsed() { return this.dreamData().daily.trainingDay === this.state.day; },
  dreamCanEnter(source) {
    if (this.dreamSession() || this.transition || this.scene !== "world" || this.dreamTrainingUsed()) return false;
    if (source === "bed") return this.zone.id === "dom";
    if (source !== "mirror" || this.zone.id !== "wyspa_snu") return false;
    return this.zone.buildings.some(b => b.kind === "lustro" && Math.hypot(this.player.x - (b.doorCol * 16 + 8), this.player.y - ((b.doorRow + 1) * 16 + 8)) < 48);
  },
  enterModulatedDream(loc, mods, source) {
    if (!this.dreamSession() && this.dreamTrainingUsed()) { this.toast("Dzisiejszy trening snu jest już wykorzystany. Kolejny będzie dostępny następnego dnia gry."); return; }
    if (!this.dreamCanEnter(source) || !DREAM_LOCATIONS.includes(loc)) return;
    if (source === "mirror" && this.state.time + 60 >= PASS_OUT) { this.toast("Na godzinny trening jest już za późno. Dziś wybierz łóżko."); return; }
    const d = this.dreamData();
    const origin = { zone: this.zone.id, x: this.player.x, y: this.player.y, dir: this.player.dir };
    this.closeModal(true); this.closeDialog(true); this.keys = {}; this.clickTarget = null; this.pendingInteract = null;
    if (source === "mirror") this.state.time += 60;
    d.daily.trainingDay = this.state.day;
    d.session = { source, origin, startedDay: this.state.day, loc, mods: this.dreamCleanMods(mods), pos: null, flying: false, nightmare: null, elapsed: 0, nightmareAt: Math.random() < 0.45 ? 35 + Math.random() * 30 : null, warned: false, trained: false };
    this.transition = { phase: "out", t: 0, speed: 1.2, then: () => {
      this.setZone("dream:" + loc);
      this.player.x = 20 * 16; this.player.y = 14 * 16; this.player.dir = "down"; this.unstick();
      if (!d.visited.includes(loc)) d.visited.push(loc);
      this.showBanner("🌙 Sen · " + ZONES[loc].name, "Zadanie: przycisk 🧠 · Ustawienia: K · Przebudzenie: ☀");
      this.save();
    } }; audio.sleep(); this.save(); this.updateHUD();
  },
  wakeDream() {
    const d = this.dreamData(), s = d.session;
    if (!s || this.transition) return;
    this.closeModal(true); this.closeDialog(true); this._dreamTrial = null;
    this.keys = {}; this.clickTarget = null; this.pendingInteract = null;
    d.lastDream = { day: this.state.day, loc: s.loc, nightmare: !!s.hadNightmare, trained: s.trained };
    d.session = null; d.activeMods = {}; delete this.zones["dream:" + s.loc];
    if (s.source === "bed") { dreamBase.sleep.call(this); return; }
    this.transition = { phase: "out", t: 0, speed: 2, then: () => {
      this.setZone(s.origin.zone); Object.assign(this.player, { x: s.origin.x, y: s.origin.y, dir: s.origin.dir }); this.unstick();
      this.showBanner("☀ Z powrotem na jawie", "Godzina treningu za tobą. Zajrzyj do dziennika snów."); this.save(); this.updateHUD();
    } };
  },
  sleep(passedOut = false) { if (this.dreamSession()) return this.wakeDream(); return dreamBase.sleep.call(this, passedOut); },
  openDreamModulation(source = null) {
    if (this.transition || this.dialog || this._mg && !this._mg.dead) return;
    const d = this.dreamData(), s = d.session, entry = source && this.dreamCanEnter(source);
    if (s && s.nightmare) { this.openDreamTasks(); return; }
    const canMod = !!s || entry, mods = this.dreamCleanMods(s ? s.mods : d.preferences || {});
    let loc = s ? s.loc : DREAM_LOCATIONS.includes(d.preferredLoc) ? d.preferredLoc : "rynek";
    const progression = Object.entries(DREAM_MODS).map(([k, cfg]) => `<div class="card"><b>${cfg.name}</b><div class="small">${cfg.lp} LP · ${cfg.days} dni ${this.dreamRequirement(k, cfg.options[1][0]) ? "🔒" : "✓"}</div></div>`).join("");
    const flight = DREAM_FLIGHT.map(f => `<li>${d.flightSteps[f.id] ? "✓" : "○"} ${f.name} <span class="small muted">(${f.days} dni, ${f.lp} LP)</span></li>`).join("");
    const options = canMod ? `<label>Dzielnica snu <select id="dream-location" class="mg-input" ${s ? "disabled" : ""}>${DREAM_LOCATIONS.map(k => `<option value="${k}" ${k === loc ? "selected" : ""}>${esc(ZONES[k].name)}</option>`).join("")}</select></label>${Object.entries(DREAM_MODS).map(([k, cfg]) => `<fieldset class="card mt"><legend>${cfg.name}</legend><div class="row" style="flex-wrap:wrap">${cfg.options.map(([v, label]) => { const why = this.dreamRequirement(k, v); return `<button class="btn ${mods[k] === v ? "btn-purple" : ""}" data-dgroup="${k}" data-dvalue="${v}" ${why ? "disabled" : ""}>${label}${why ? `<br><span class="small">🔒 ${why}</span>` : ""}</button>`; }).join("")}</div></fieldset>`).join("")}` : `<p>Wejdź w sen przez <b>łóżko w domu</b> albo <b>Lustro REM na Wyspie Snu</b>. Tutaj możesz zapisać sen, wykonać dzienny test i sprawdzić postępy.</p>`;
    const body = `<div class="row"><span class="tag purple">${d.lp} LP</span><span class="tag">${this.dreamDays()} dni treningowych</span><span class="tag">Wyrazistość ${Math.round(this.dreamClarity() * 100)}%</span></div><p class="small mt">Pierwsze ukończenie pokoju lub unikalnego zadania: 10 LP. Test rzeczywistości i wpis do dziennika: po 5 LP dziennie. Powtórki ćwiczą umiejętności; wejścia nie dają LP.</p>${options}<details class="mt" ${canMod ? "" : "open"}><summary>Drabinka możliwości i próby lotu</summary><div class="grid2 mt">${progression}</div><p>Latanie: 220 LP, 8 dni treningowych i wszystkie próby.</p><ol>${flight}</ol><p class="small">Odwiedzone senne dzielnice: ${d.visited.length}/9 · Odzyskane fragmenty koszmarów: ${d.fragments.length}/9.</p></details><p class="small muted mt">To zasady gry. W prawdziwym śnie świadomość, wyrazistość i kontrola nie muszą występować razem.</p>`;
    const foot = `<button class="btn" data-close>Zamknij</button>${!s ? `<button class="btn" id="dream-rc" ${d.daily.rc === this.state.day ? "disabled" : ""}>Test rzeczywistości</button><button class="btn" id="dream-journal">Dziennik snów</button>` : `<button class="btn" id="dream-practice">Zadania</button><button class="btn" id="dream-wake">Obudź się</button>`}${canMod ? `<button class="btn btn-purple" id="btn-enter-dream">${s ? "Zastosuj zmiany" : source === "bed" ? "Zaśnij · zakończy dzień" : "Wejdź · 60 minut"} [Enter]</button>` : ""}`;
    const dailyNote = !s ? `<p class="fb" id="dream-daily-limit">${this.dreamTrainingUsed() ? "Dzisiejszy trening snu jest już wykorzystany. Kolejny będzie dostępny następnego dnia gry. Możesz zakończyć dzień zwykłym snem w łóżku." : "Dostępny trening snu: 1/1. Łóżko i Lustro REM korzystają ze wspólnego limitu. Wejście zużywa trening także przy wcześniejszym przebudzeniu."}</p>` : "";
    const m = this.openModal(this.panel("🌙 Akademia świadomego snu", dailyNote + body, foot, "wide"));
    m.querySelectorAll("[data-dgroup]").forEach(b => b.onclick = () => {
      mods[b.dataset.dgroup] = b.dataset.dvalue;
      m.querySelectorAll(`[data-dgroup="${b.dataset.dgroup}"]`).forEach(el => el.classList.toggle("btn-purple", el === b));
    });
    const select = m.querySelector("#dream-location"); if (select) select.onchange = () => { loc = select.value; };
    const enter = m.querySelector("#btn-enter-dream");
    if (enter) {
      enter.onclick = () => {
        if (s && s.flying && mods.gravity !== "flying") { this.toast("Najpierw bezpiecznie wyląduj przyciskiem F."); return; }
        d.preferences = Object.assign({}, mods); d.preferredLoc = loc;
        if (s) { s.mods = this.dreamCleanMods(mods); this.closeModal(true); this.rebuildDream(); this.save(); }
        else this.enterModulatedDream(loc, mods, source);
      };
      enter.focus();
    }
    const wire = (id, fn) => { const b = m.querySelector(id); if (b) b.onclick = fn; };
    wire("#dream-rc", () => this.openRealityCheck()); wire("#dream-journal", () => this.openDreamJournal());
    wire("#dream-practice", () => this.openDreamTasks()); wire("#dream-wake", () => this.wakeDream());
  },
  openRealityCheck() {
    const d = this.dreamData(); if (d.session || d.daily.rc === this.state.day) return;
    this.runDreamQuiz("rc", [{ q: "Rozglądasz się i przypominasz sobie drogę tutaj. Co można wnioskować z pojedynczego testu rzeczywistości?", a: ["To wskazówka do refleksji, a nie niezawodny dowód snu lub jawy", "Nieprawidłowy zegar zawsze dowodzi snu", "Pięć palców wyklucza sen"], why: "Testy rzeczywistości bywają zawodne. W grze ćwiczymy uważne sprawdzanie, a nie diagnozujemy stanu świadomości." }], () => {
      d.daily.rc = this.state.day; d.techniques.realityCheck = (d.techniques.realityCheck || 0) + 1;
      this.dreamReward("rc:" + this.state.day, 5, "dzienny test rzeczywistości"); this.openDreamModulation();
    });
  },
  openDreamJournal() {
    const d = this.dreamData(); if (d.session) return;
    const canWrite = !!d.lastDream && d.daily.journal !== this.state.day;
    const m = this.openModal(this.panel("📖 Dziennik snów", `<p>Zapisz obraz, emocję lub niezgodność z ostatniego snu postaci. Można też zanotować brak wspomnień. Krótkie zdanie wystarczy.</p>${canWrite ? `<label>Twój wpis<textarea id="dream-note" class="mg-input" rows="3" maxlength="700" placeholder="Pamiętam…"></textarea></label>` : `<p class="fb">${d.lastDream ? "Dzisiejszy wpis jest już zapisany." : "Najpierw przeżyj sen i obudź postać."}</p>`}<div class="col mt">${d.journal.slice(-12).reverse().map(e => `<div class="card"><b>Dzień ${e.day}</b><p>${esc(e.text || "")}</p></div>`).join("") || "Dziennik czeka na pierwszy sen."}</div>`, `<button class="btn" data-close>Zamknij</button>${canWrite ? `<button class="btn btn-purple" id="dream-note-save">Zapisz · 5 LP</button>` : ""}`, "narrow"));
    const b = m.querySelector("#dream-note-save"); if (b) b.onclick = () => {
      const value = m.querySelector("#dream-note").value.trim();
      if (value.length < 5) { this.toast("Zapisz choć krótką myśl — minimum 5 znaków."); return; }
      if (d.daily.journal === this.state.day) return;
      d.daily.journal = this.state.day; d.journal.push({ day: this.state.day, text: value.slice(0, 700), loc: d.lastDream.loc });
      this.dreamReward("journal:" + this.state.day, 5, "dziennik snów"); this.save(); this.openDreamJournal();
    };
    if (canWrite) m.querySelector("#dream-note").focus();
  },
  openDreamTasks() {
    const s = this.dreamSession(); if (!s || this.transition) return;
    const d = this.dreamData(), n = s.nightmare;
    const stage = this.dreamDays() < 2 ? 0 : this.dreamDays() < 4 ? 1 : this.dreamDays() < 8 ? 2 : 3;
    const next = DREAM_FLIGHT.find(f => !d.flightSteps[f.id]);
    const locked = next && (this.dreamDays() < next.days || d.lp < next.lp);
    const body = `${n ? `<div class="fb"><b>${DREAM_NIGHTMARES[n.kind].name}</b><p>${DREAM_NIGHTMARES[n.kind].story}</p><p>Przemiana: ${n.step}/3. ${stage === 0 ? "Na tym etapie ukończenie zadania obudzi postać." : `Możesz osiągnąć etap ${stage}/3: ${["", "uspokojenie jednego elementu", "przemiana fragmentu przestrzeni", "przemiana całego koszmaru"][stage]}.`}</p></div>` : `<p>Wybierz zadanie. Każde ma instrukcję, wskazówki i dowolny czas na odpowiedź. To ćwiczenia inspirowane psychologią — wynik nie jest diagnozą.</p>`}<div class="grid2 mt">${DREAM_TASKS.map(([id, name]) => `<button class="btn" data-dtask="${id}">${name}</button>`).join("")}</div><p class="small muted mt">Po 4 dniach: trudniejszy wariant. N-back przechodzi z 1-back do 2-back. LP przysługują raz za każdy wariant zadania.</p>${next && !n ? `<div class="card mt"><b>Próba lotu ${DREAM_FLIGHT.indexOf(next) + 1}/4: ${next.name}</b><p>${locked ? `Wymagane: ${next.days} dni i ${next.lp} LP. Brakuje ${Math.max(0, next.days - this.dreamDays())} dni i ${Math.max(0, next.lp - d.lp)} LP.` : "Próba gotowa. Wykonaj poprzedzające ją ćwiczenie, a potem postępuj zgodnie z instrukcją."}</p><button class="btn btn-purple" id="dream-flight-trial" ${locked ? "disabled" : ""}>Rozpocznij próbę</button></div>` : ""}`;
    const m = this.openModal(this.panel(n ? "🌘 Oswajanie koszmaru" : "🧠 Trening we śnie", body, `<button class="btn" data-close>Wróć do snu</button><button class="btn" id="dream-task-wake">Obudź się</button>`, "wide"));
    m.querySelectorAll("[data-dtask]").forEach(b => b.onclick = () => this.startDreamTask(b.dataset.dtask));
    m.querySelector("#dream-task-wake").onclick = () => this.wakeDream();
    const trial = m.querySelector("#dream-flight-trial"); if (trial) trial.onclick = () => this.startFlightTrial();
    m.querySelector("[data-dtask]").focus();
  },
  startDreamTask(kind, after = null) {
    const s = this.dreamSession(); if (!s) return;
    const level = this.dreamDays() >= 4 ? 2 : 1, key = kind + ":" + level;
    const finish = () => { this.dreamTrain(key); if (after) after(); else if (s.nightmare) this.advanceNightmare(); else this.openDreamTasks(); };
    const questions = [], q = (text, answers, why, extra = {}) => ({ q: text, a: answers, why, ...extra });
    if (kind === "count") {
      const start = (level === 1 ? 40 : 100) + Math.floor(Math.random() * 10), step = level === 1 ? 3 : 7;
      for (let i = 0; i < 4; i++) { const from = start - i * step; questions.push(q(`Liczymy wstecz co ${step}. Po ${from} będzie…`, [String(from - step), String(from - step + 1), String(from + step)], `${from} − ${step} = ${from - step}.`)); }
    } else if (kind === "logic") {
      questions.push(level === 1 ? q("Każdy lampion w tej zagadce świeci. To jest lampion. Co wynika z tych założeń?", ["Świeci", "Nie świeci", "Jest latarnią morską"], "Wniosek wynika z podanych przesłanek, nawet w absurdalnym świecie snu.") : q("Jeżeli pada, dach jest mokry. Dach jest mokry. Czy na pewno pada?", ["Nie — dach mógł zmoknąć inaczej", "Tak, to pewny dowód deszczu", "Tak, o ile to dach z cukierków"], "Potwierdzenie następstwa nie dowodzi poprzednika. Ktoś mógł polać dach wodą."));
      questions.push(q("Który element uzupełnia ciąg: 2, 4, 8, 16, …?", ["32", "18", "24"], "Każda kolejna liczba jest dwa razy większa."));
    } else if (kind === "anomaly") {
      questions.push(q("Drogowskaz obiecuje: „Droga na północ prowadzi wyłącznie na południe”. Co tu nie pasuje?", ["Sprzeczne kierunki w tej samej obietnicy", "Drogowskaz ma za dużo samogłosek", "Północ zawsze musi być na dole"], "Szukamy niezgodności informacji. Dziwny drogowskaz jest wskazówką fabularną, nie dowodem prawdziwego snu."));
      questions.push(q("Na zegarze cyfrowym pojawia się godzina 27:83. Co budzi wątpliwość?", ["Minuty przekraczają 59, a godziny zwykły zakres dobowy", "Zegar jest cyfrowy", "Każdy zegar we śnie musi kłamać"], "Nietypowy zapis zwraca uwagę, lecz sam nie rozstrzyga, czy ktoś śni."));
      if (level === 2) questions.push(q("Plan mówi: biblioteka jest na wschód od fontanny, a fontanna na wschód od biblioteki. Zakładamy zwykłą płaską mapę. Co z tego wynika?", ["Te opisy wzajemnego położenia są sprzeczne", "Oba opisy są zgodne", "Biblioteka musi być pod fontanną"], "Na takiej mapie relacja „na wschód od” nie może działać w obie strony naraz. Zauważenie sprzeczności wymaga połączenia dwóch informacji."));
    } else if (kind === "stroop") {
      const colors = [["czerwony", "#a32e37"], ["niebieski", "#285fa0"], ["zielony", "#316e42"], ["fioletowy", "#784197"]];
      for (let i = 0; i < 4; i++) {
        const ink = Math.floor(Math.random() * 4), word = (ink + (i % 2 ? 1 : 0) + (level === 2 ? 1 : 0)) % 4;
        questions.push(q("Wybierz kolor tuszu, ignorując znaczenie napisu.", [colors[ink][0], ...colors.filter((_, j) => j !== ink).map(c => c[0])], "Zadanie Stroopa pokazuje konflikt między czytaniem słowa a nazywaniem koloru. Tutaj nie mierzymy czasu ani nie porównujemy wyniku z normami.", { stimulus: `<span style="color:${colors[ink][1]};font-family:var(--font-pixel);font-size:32px;font-weight:400;background:#fff7e6;padding:16px;display:inline-block">${colors[word][0].toUpperCase()}</span>` }));
      }
    } else if (kind === "nback") {
      const n = level, pool = shuffle(Math.random, ["K", "M", "R", "T"]), indexes = [0, 1, 0, 2, 2, 2, 3, 2], seq = indexes.map(i => pool[i]);
      for (let i = 0; i < seq.length; i++) {
        const yes = i >= n && seq[i] === seq[i - n];
        questions.push(i < n ? q(`Rozgrzewka ${n}-back: zapamiętaj znak. Potem będziesz porównywać bieżący znak ze znakiem sprzed ${n} kroków.`, ["Zapamiętaj · dalej"], "Każdy znak zastępuje poprzedni. Przesuwaj uwagę wraz z sekwencją.", { stimulus: seq[i] }) : q(`${n}-back: czy ten znak jest taki sam jak ${n} ${n === 1 ? "krok" : "kroki"} wcześniej?`, yes ? ["Tak", "Nie"] : ["Nie", "Tak"], `Porównanie: ${seq[i]} i ${seq[i - n]}. ${yes ? "To ten sam znak." : "To różne znaki."} N-back wymaga aktualizowania informacji w pamięci roboczej.`, { stimulus: seq[i] }));
      }
    } else if (kind === "memory") {
      const symbols = shuffle(Math.random, ["★", "●", "▲", "■", "◆"]).slice(0, level === 1 ? 3 : 5);
      questions.push(q("Zapamiętaj kolejność symboli. Przejdź dalej, kiedy zechcesz.", ["Zapamiętaj · dalej"], "W następnym kroku sekwencja zniknie.", { stimulus: symbols.join("   ") }));
      const index = level === 1 ? 1 : 3;
      questions.push(q(`Który symbol był na pozycji ${index + 1}?`, [symbols[index], ...symbols.filter((_, i) => i !== index)], `Sekwencja: ${symbols.join(" → ")}. Wskazana pozycja to ${symbols[index]}.`));
    } else return;
    this.runDreamQuiz(key, questions, finish);
  },
  runDreamQuiz(key, questions, onFinish) {
    const trial = { key, i: 0, questions, onFinish }; this._dreamTrial = trial;
    const show = () => {
      if (this._dreamTrial !== trial) return;
      const item = questions[trial.i];
      const answers = shuffle(Math.random, item.a.map((label, i) => ({ label, correct: i === 0 })));
      const m = this.openModal(this.panel("🧠 Ćwiczenie · " + (trial.i + 1) + "/" + questions.length, `<p>${esc(item.q)}</p>${item.stimulus ? `<div class="center" id="dream-stimulus" style="font-family:var(--font-pixel);font-size:32px;font-weight:400;padding:16px">${item.stimulus}</div>` : ""}<div class="col mt">${answers.map((a, i) => `<button class="btn" data-danswer="${i}">${esc(a.label)}</button>`).join("")}</div><p id="dream-feedback" class="fb mt" aria-live="polite">Bez pośpiechu. Błąd daje wskazówkę; możesz spróbować ponownie.</p>`, `<button class="btn" id="dream-quit">Przerwij zadanie</button>${this.dreamSession() ? `<button class="btn" id="dream-quiz-wake">Obudź się</button>` : ""}<button class="btn btn-purple" id="dream-next" disabled>Dalej</button>`, "narrow", false), { locked: true, dreamTrial: trial });
      let answered = false;
      m.querySelectorAll("[data-danswer]").forEach(b => b.onclick = () => {
        if (answered) return;
        const a = answers[Number(b.dataset.danswer)], feedback = m.querySelector("#dream-feedback");
        feedback.textContent = (a.correct ? "Dobrze. " : "Spróbuj jeszcze raz. ") + item.why;
        if (!a.correct) { audio.error(); return; }
        answered = true; audio.success();
        m.querySelectorAll("[data-danswer]").forEach(el => { el.disabled = true; });
        m.querySelector("#dream-next").disabled = false; m.querySelector("#dream-next").focus();
      });
      m.querySelector("#dream-next").onclick = () => {
        if (!answered || this._dreamTrial !== trial) return;
        trial.i++;
        if (trial.i === questions.length) { this._dreamTrial = null; this.closeModal(true); onFinish(); }
        else show();
      };
      m.querySelector("#dream-quit").onclick = () => { this._dreamTrial = null; this.closeModal(true); if (this.dreamSession()) this.openDreamTasks(); else this.openDreamModulation(); };
      const wake = m.querySelector("#dream-quiz-wake"); if (wake) wake.onclick = () => this.wakeDream();
      m.querySelector("[data-danswer]").focus();
    };
    show();
  },
  openModal(html, opts = {}) {
    if (this._dreamTrial && opts.dreamTrial !== this._dreamTrial) this._dreamTrial = null;
    return dreamBase.openModal.call(this, html, opts);
  },
  startFlightTrial() {
    const s = this.dreamSession(), d = this.dreamData(), f = DREAM_FLIGHT.find(x => !d.flightSteps[x.id]);
    if (!s || s.nightmare || !f || this.dreamDays() < f.days || d.lp < f.lp) return;
    this.startDreamTask(f.id === "stable" ? "memory" : "logic", () => {
      if (f.id === "stable" || f.id === "reshape") {
        d.flightSteps[f.id] = this.state.day;
        if (f.id === "reshape") { s.mods.season = "wiosna"; this.rebuildDream(); }
        this.dreamTrain("flight:" + f.id); this.toast("Zaliczono: " + f.name); this.openDreamTasks();
      } else {
        s.lesson = f.id; s.lessonStart = { x: this.player.x, y: this.player.y };
        s.lessonDistance = 0; s.flying = f.id === "land"; s.hovering = f.id === "hover";
        this.closeModal(true); this.updateHUD(); this.save();
        this.showBanner(f.id === "land" ? "🪶 Próba lotu" : "🪶 Próba unoszenia", "Przemieść się o co najmniej 3 kafelki. F lub przycisk „Ląduj” kończy próbę na wolnym podłożu.");
      }
    });
  },
  toggleDreamFlight() {
    const s = this.dreamSession(); if (!s || this.transition || this.modalOpen || this.dialog) return;
    if (s.flying || s.hovering) {
      if (dreamBase.blockedAt.call(this, this.player.x, this.player.y)) { this.toast("Tu nie można lądować. Poszukaj wolnej ścieżki lub trawy."); return; }
      if (s.lesson && (s.lessonDistance || 0) < 48) { this.toast("Próba trwa: przemieszczaj się jeszcze trochę, łącznie co najmniej 3 kafelki."); return; }
      const lesson = s.lesson;
      s.flying = false; s.hovering = false; s.lesson = null;
      if (lesson) { this.dreamData().flightSteps[lesson] = this.state.day; this.dreamTrain("flight:" + lesson); if (lesson === "land") s.mods.gravity = "flying"; this.toast(lesson === "land" ? "Latanie odblokowane! F: start i lądowanie." : "Unoszenie opanowane. Przed tobą ostatnia próba lotu."); }
    } else {
      if (s.nightmare) { this.toast("Najpierw opanuj koszmar."); return; }
      const reason = this.dreamRequirement("gravity", "flying");
      if (reason) { this.toast(reason); return; }
      if (s.mods.gravity !== "flying") { this.toast("Wybierz latanie w ustawieniach snu (K)."); return; }
      s.flying = true;
    }
    this.save(); this.updateHUD();
  },
  beginNightmare(kind = Math.floor(Math.random() * DREAM_NIGHTMARES.length)) {
    const s = this.dreamSession(); if (!s || s.nightmare || s.lesson || s.flying || s.hovering) return;
    s.hadNightmare = true; s.nightmare = { kind, step: 0 }; s.nightmareAt = null;
    s.flying = false; s.hovering = false; this.rebuildDream();
    this.showBanner("🌘 " + DREAM_NIGHTMARES[kind].name, "Przycisk 🧠: oswajaj koszmar. Przycisk ☀: obudź się.");
    this.save(); this.updateHUD();
  },
  advanceNightmare() {
    const s = this.dreamSession(); if (!s || !s.nightmare) return;
    const d = this.dreamDays(), limit = d < 2 ? 0 : d < 4 ? 1 : d < 8 ? 2 : 3;
    if (!limit) { this.toast("Zadanie pomogło odzyskać orientację. Postać się budzi."); this.wakeDream(); return; }
    if (s.nightmare.step >= limit) { this.toast(`Ten etap jest opanowany. Kolejna przemiana wymaga ${limit === 1 ? 4 : 8} dni treningowych. Możesz dalej ćwiczyć albo się obudzić.`); this.openDreamTasks(); return; }
    s.nightmare.step++;
    const fragments = this.dreamData().fragments, fragment = s.nightmare.kind + ":" + s.nightmare.step;
    if (!fragments.includes(fragment)) fragments.push(fragment);
    if (s.nightmare.step === 3) {
      const kind = s.nightmare.kind; s.nightmare = null;
      this.dreamReward("nightmare:" + kind, 10, "pierwsze opanowanie tego koszmaru");
      this.rebuildDream(); this.save(); this.showBanner("🌤 Koszmar przemieniony", "Teraz wybierz, jaki ma być twój sen."); this.openDreamModulation();
    } else {
      this.rebuildDream(); this.save(); this.toast(s.nightmare.step === 1 ? "Jeden element odzyskuje spokój. Zrób kolejny krok, jeśli masz dość treningu." : "Fragment dzielnicy wraca pod twoją kontrolę. Przemiana całego snu to kolejny etap.");
      this.closeModal(true);
    }
  },
  update(dt) {
    dreamBase.update.call(this, dt);
    const s = this.dreamSession(); if (!s || this.paused()) return;
    s.elapsed += dt;
    if (s.nightmareAt != null && !s.lesson && !s.flying && !s.hovering) {
      if (!s.warned && s.elapsed >= s.nightmareAt - 10) { s.warned = true; this.toast("Coś się zmienia… Drogowskazy tracą sens, a kolory ciemnieją."); }
      if (s.elapsed >= s.nightmareAt) this.beginNightmare();
    }
  },
  updatePlayer(dt) {
    const s = this.dreamSession(), p = this.player, x = p.x, y = p.y;
    dreamBase.updatePlayer.call(this, dt);
    if (s) {
      p.x = clamp(p.x, 6, this.zone.w * 16 - 6); p.y = clamp(p.y, 5, this.zone.h * 16 - 5);
      if (s.lesson) s.lessonDistance = (s.lessonDistance || 0) + Math.hypot(p.x - x, p.y - y);
    }
  },
  blockedAt(x, y) {
    const s = this.dreamSession();
    if (s && s.flying) return x < 6 || y < 5 || x > this.zone.w * 16 - 6 || y > this.zone.h * 16 - 5;
    return dreamBase.blockedAt.call(this, x, y);
  },
  checkEdges() { if (!this.dreamSession()) dreamBase.checkEdges.call(this); },
  checkFiszki() { if (!this.dreamSession()) dreamBase.checkFiszki.call(this); },
  enterDoor(b) {
    if (this.dreamSession()) return;
    if (b.kind === "lustro" && !this.transition && !this.modalOpen && !this.dialog) {
      this.player.y = (b.doorRow + 1) * 16 + 8; this.keys = {}; this.clickTarget = null;
      return this.openDreamModulation("mirror");
    }
    return dreamBase.enterDoor.call(this, b);
  },
  trigger(it) { if (this.dreamSession()) return this.openDreamTasks(); return dreamBase.trigger.call(this, it); },
  updatePrompt() {
    if (!this.dreamSession()) return dreamBase.updatePrompt.call(this);
    document.getElementById("prompt").style.display = "none";
  },
  darkness() { return this.dreamSession() ? 0 : dreamBase.darkness.call(this); },
  warmth() { return this.dreamSession() ? 0 : dreamBase.warmth.call(this); },
  finishMinigame(ctx, ratio, summary = "") {
    const eligible = !ctx.dead && ctx.sid.startsWith("sny_");
    dreamBase.finishMinigame.call(this, ctx, ratio, summary);
    if (eligible && this.roomStars(ctx.sid, ctx.idx)) this.dreamReward("room:" + ctx.sid + ":" + ctx.R.id, 10, "ukończenie pokoju");
  },
  dreamWorldFilter(t) {
    const s = this.dreamSession(); if (!s) return "none";
    const base = `saturate(${0.45 + this.dreamClarity() * 0.55})`;
    return base + (s.nightmare ? "" : ({ sepia: " sepia(0.85)", negatyw: " invert(1)", psychedelic: ` hue-rotate(${Math.floor(t * 8) % 360}deg)` }[s.mods.style] || ""));
  },
  drawDreamSprite(sprite, x, y, object) {
    const s = this.dreamSession(), ctx = this.ctx;
    if (!s) { ctx.drawImage(sprite.c, x, y); return; }
    if (object.dreamPal) {
      if (!object.dreamSprite) {
        const [c, g] = mkCanvas(sprite.c.width, sprite.c.height); g.drawImage(sprite.c, 0, 0);
        const pixels = g.getImageData(0, 0, c.width, c.height), pal = object.dreamPal.map(hexToRgb);
        for (let i = 0; i < pixels.data.length; i += 4) {
          const r = pixels.data[i], green = pixels.data[i + 1], b = pixels.data[i + 2];
          if (pixels.data[i + 3] && green > r * 1.1 && green > b * 0.95) {
            const color = pal[Math.min(pal.length - 1, Math.floor(green / 70))];
            pixels.data[i] = color[0]; pixels.data[i + 1] = color[1]; pixels.data[i + 2] = color[2];
          }
        }
        g.putImageData(pixels, 0, 0); object.dreamSprite = { c };
      }
      sprite = object.dreamSprite;
    }
    const dist = Math.hypot(x + sprite.c.width / 2 - this.player.x, y + sprite.c.height - this.player.y);
    const vague = dist > 96 && this.dreamDays() < 6;
    ctx.save();
    if (vague) ctx.globalAlpha = 0.45 + this.dreamClarity() * 0.5;
    if (vague && this.dreamDays() < 3) {
      ctx.beginPath();
      for (let yy = 0; yy < sprite.c.height; yy += 8) ctx.rect(x, y + yy, sprite.c.width, 6);
      ctx.clip();
    }
    ctx.drawImage(sprite.c, x, y); ctx.restore();
    if (object.type === "building" && s.mods.material !== "default" && object.b.dreamRestored) {
      const b = object.b;
      ctx.fillStyle = s.mods.material === "czekolada" ? "#dfb487" : s.mods.material === "krysztal" ? "#b8e6f0" : "#fff0cb";
      for (let k = 8; k < b.w * 16 - 8; k += 14) {
        const px = b.x * 16 + k, py = (b.y + b.h) * 16 - 18;
        ctx.fillRect(px, py, 4, 3); ctx.fillRect(px + 1, py - 2, 2, 7);
      }
    }
  },
  drawPlayer(t) {
    const s = this.dreamSession(); if (!s) return dreamBase.drawPlayer.call(this, t);
    const p = this.player, ctx = this.ctx;
    const floatY = s.flying ? 28 + Math.sin(t * 2) * 2 : s.hovering || s.mods.gravity === "low" ? 7 + Math.sin(t * 2) * 3 : s.mods.gravity === "inverted" ? 20 : 0;
    const spr = characterSprite(this.playerLook(), p.dir, p.moving ? p.frame : 0, t % 3.7 < 0.12);
    ctx.save(); ctx.filter = "none";
    ctx.fillStyle = "rgba(30,24,42,0.35)"; ctx.fillRect(p.x - 5, p.y - 1, 10, 3);
    if (s.mods.gravity === "inverted" && !s.flying) { ctx.translate(p.x, p.y - floatY - 10); ctx.scale(1, -1); ctx.drawImage(spr.c, -spr.ax, -spr.ay + 10); }
    else ctx.drawImage(spr.c, Math.round(p.x - spr.ax), Math.round(p.y - spr.ay - floatY));
    ctx.restore();
  },
  drawDreamWorld(t) {
    const s = this.dreamSession(); if (!s) return;
    const ctx = this.ctx, Z = this.zone, n = s.nightmare;
    if (n) {
      for (let i = 0; i < 6; i++) {
        const x = i === 0 ? this.player.x + 30 : 90 + i * 76, y = i === 0 ? this.player.y - 12 : 130 + (i % 2) * 84;
        const calm = n.step >= 1 && i === 0;
        ctx.fillStyle = calm ? "#8fb697" : DREAM_NIGHTMARES[n.kind].color;
        if (n.kind === 0) {
          ctx.fillRect(x, y - 28, 31, 21); ctx.fillStyle = calm ? "#e6ecd5" : "#dcbaca";
          ctx.font = `8px ${WORLD_FONT}`; ctx.fillText(calm ? "PRZERWA" : "EGZAMIN ∞", x + 2, y - 15);
        } else if (n.kind === 1) {
          for (let k = 0; k < (calm ? 2 : 6); k++) ctx.fillRect(x + k * 4, y - k * 5 - Math.sin(t + i) * 3, 12, 3);
        } else {
          const sx = calm ? x : this.player.x + Math.sin(t * 0.4 + i) * (28 + i * 9), sy = calm ? y : this.player.y + 28 + i * 6;
          ctx.globalAlpha = calm ? 0.8 : 0.35; ctx.fillRect(sx - 5, sy - 18, 10, 18); ctx.fillRect(sx - 3, sy - 23, 6, 5); ctx.globalAlpha = 1;
        }
      }
    }
    if (s.mods.gravity === "inverted" && !n) {
      ctx.fillStyle = "#b3a1d1";
      for (let i = 0; i < 16; i++) ctx.fillRect(24 + (i * 83) % (Z.w * 16 - 48), (Z.h * 16 - (t * 20 + i * 47) % (Z.h * 16)), 4, 5);
    }
  },
  drawDreamEffects(ctx, W, H, t) {
    const s = this.dreamSession(); if (!s) return;
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.filter = "none";
    const m = s.mods, size = Math.max(2, Math.round(this.scale)), snow = m.weather === "snow" || m.season === "zima";
    const petals = m.season === "wiosna", leaves = m.season === "jesien";
    if (snow || petals || leaves || m.weather === "rain") for (let i = 0; i < 42; i++) {
      const rain = m.weather === "rain", x = (i * 83 + t * (rain ? 33 : 9) + Math.sin(t + i) * 12) % (W + 20) - 10;
      const y = (i * 137 + t * (rain ? 175 : 28)) % (H + 20) - 10;
      ctx.fillStyle = rain ? "#948bc8" : snow ? "#e5edf1" : petals ? "#e4a4bb" : ["#c9853c", "#a94f38", "#ddba65"][i % 3];
      ctx.fillRect(Math.round(x), Math.round(y), rain ? 2 : size, rain ? 10 : Math.max(2, size / 2));
    }
    if (m.weather === "fog") {
      // Kilka lokalnych, ciemnych smug; bez mlecznej zasłony na całym ekranie.
      ctx.fillStyle = "rgba(86,91,123,0.22)";
      for (let i = 0; i < 7; i++) {
        const x = (i * 193 + t * 11) % (W + 200) - 160, y = H * 0.35 + (i * 67) % Math.max(1, H * 0.55);
        ctx.fillRect(x, y, 150, 10); ctx.fillRect(x + 22, y - 8, 104, 8);
      }
    }
    const fs = Math.max(16, Math.round(W / 700) * 8);
    ctx.font = `${fs}px ${WORLD_FONT}`; ctx.textBaseline = "top"; ctx.textAlign = "left";
    const label = `${s.nightmare ? "KOSZMAR " + s.nightmare.step + "/3" : "SEN"} · ${this.dreamData().lp} LP · wyrazistość ${Math.round(this.dreamClarity() * 100)}%`;
    ctx.fillStyle = "#252334"; ctx.fillRect(8, 8, Math.min(W - 16, ctx.measureText(label).width + 20), fs + 14);
    ctx.fillStyle = "#e8dfc9"; ctx.fillText(label, 18, 14, W - 36); ctx.restore();
  }
});

```
