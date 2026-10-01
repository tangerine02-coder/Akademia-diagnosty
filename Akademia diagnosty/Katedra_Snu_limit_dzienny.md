# Jeden trening snu na dzień

Zmiana jest już zastosowana w grze. Limit dotyczy jednej sesji snu na dzień gry, wspólnie dla łóżka i Lustra REM. Wcześniejsze przebudzenie nie odnawia limitu; odświeżenie wznawia tę samą sesję. Zwykły sen kończący dzień pozostaje dostępny. W ramach jednej sesji można wykonywać kolejne zadania i etapy koszmaru.

Poniższe podmiany stosuj kolejno do wersji sprzed tego uzupełnienia.

## 1. Aktualizacja obsługi dziennego limitu

**ZNAJDŹ**

```javascript
      });
    }
    return d;
```

**ZAMIEŃ NA**

```javascript
      });
    }
    if (!Number.isInteger(d.daily.trainingDay)) {
      const completedDay = d.trainingDays.reduce((last, day) => Math.max(last, day), 0);
      d.daily.trainingDay = Math.max(completedDay, d.lastDream ? d.lastDream.day : 0, d.session ? (d.session.startedDay || this.state.day) : 0);
    }
    return d;
```

## 2. Aktualizacja obsługi dziennego limitu

**ZNAJDŹ**

```javascript
  enterDreamFromBed() { this.openDreamModulation("bed"); },
  dreamCanEnter(source) {
    if (this.dreamSession() || this.transition || this.scene !== "world") return false;
    if (source === "bed") return this.zone.id === "dom";
```

**ZAMIEŃ NA**

```javascript
  enterDreamFromBed() { this.openDreamModulation("bed"); },
  dreamTrainingUsed() { return this.dreamData().daily.trainingDay === this.state.day; },
  dreamCanEnter(source) {
    if (this.dreamSession() || this.transition || this.scene !== "world" || this.dreamTrainingUsed()) return false;
    if (source === "bed") return this.zone.id === "dom";
```

## 3. Aktualizacja obsługi dziennego limitu

**ZNAJDŹ**

```javascript
  enterModulatedDream(loc, mods, source) {
    if (!this.dreamCanEnter(source) || !DREAM_LOCATIONS.includes(loc)) return;
```

**ZAMIEŃ NA**

```javascript
  enterModulatedDream(loc, mods, source) {
    if (!this.dreamSession() && this.dreamTrainingUsed()) { this.toast("Dzisiejszy trening snu jest już wykorzystany. Kolejny będzie dostępny następnego dnia gry."); return; }
    if (!this.dreamCanEnter(source) || !DREAM_LOCATIONS.includes(loc)) return;
```

## 4. Aktualizacja obsługi dziennego limitu

**ZNAJDŹ**

```javascript
    if (source === "mirror") this.state.time += 60;
    d.session = { source, origin, loc, mods: this.dreamCleanMods(mods), pos: null, flying: false, nightmare: null, elapsed: 0, nightmareAt: Math.random() < 0.45 ? 35 + Math.random() * 30 : null, warned: false, trained: false };
    this.transition = { phase: "out", t: 0, speed: 1.2, then: () => {
```

**ZAMIEŃ NA**

```javascript
    if (source === "mirror") this.state.time += 60;
    d.daily.trainingDay = this.state.day;
    d.session = { source, origin, startedDay: this.state.day, loc, mods: this.dreamCleanMods(mods), pos: null, flying: false, nightmare: null, elapsed: 0, nightmareAt: Math.random() < 0.45 ? 35 + Math.random() * 30 : null, warned: false, trained: false };
    this.transition = { phase: "out", t: 0, speed: 1.2, then: () => {
```

## 5. Aktualizacja obsługi dziennego limitu

**ZNAJDŹ**

```javascript
      this.save();
    } }; audio.sleep(); this.updateHUD();
  },
```

**ZAMIEŃ NA**

```javascript
      this.save();
    } }; audio.sleep(); this.save(); this.updateHUD();
  },
```

## 6. Aktualizacja obsługi dziennego limitu

**ZNAJDŹ**

```javascript
    const foot = `<button class="btn" data-close>Zamknij</button>${!s ? `<button class="btn" id="dream-rc" ${d.daily.rc === this.state.day ? "disabled" : ""}>Test rzeczywistości</button><button class="btn" id="dream-journal">Dziennik snów</button>` : `<button class="btn" id="dream-practice">Zadania</button><button class="btn" id="dream-wake">Obudź się</button>`}${canMod ? `<button class="btn btn-purple" id="btn-enter-dream">${s ? "Zastosuj zmiany" : source === "bed" ? "Zaśnij · zakończy dzień" : "Wejdź · 60 minut"} [Enter]</button>` : ""}`;
    const m = this.openModal(this.panel("🌙 Akademia świadomego snu", body, foot, "wide"));
    m.querySelectorAll("[data-dgroup]").forEach(b => b.onclick = () => {
```

**ZAMIEŃ NA**

```javascript
    const foot = `<button class="btn" data-close>Zamknij</button>${!s ? `<button class="btn" id="dream-rc" ${d.daily.rc === this.state.day ? "disabled" : ""}>Test rzeczywistości</button><button class="btn" id="dream-journal">Dziennik snów</button>` : `<button class="btn" id="dream-practice">Zadania</button><button class="btn" id="dream-wake">Obudź się</button>`}${canMod ? `<button class="btn btn-purple" id="btn-enter-dream">${s ? "Zastosuj zmiany" : source === "bed" ? "Zaśnij · zakończy dzień" : "Wejdź · 60 minut"} [Enter]</button>` : ""}`;
    const dailyNote = !s ? `<p class="fb" id="dream-daily-limit">${this.dreamTrainingUsed() ? "Dzisiejszy trening snu jest już wykorzystany. Kolejny będzie dostępny następnego dnia gry. Możesz zakończyć dzień zwykłym snem w łóżku." : "Dostępny trening snu: 1/1. Łóżko i Lustro REM korzystają ze wspólnego limitu. Wejście zużywa trening także przy wcześniejszym przebudzeniu."}</p>` : "";
    const m = this.openModal(this.panel("🌙 Akademia świadomego snu", dailyNote + body, foot, "wide"));
    m.querySelectorAll("[data-dgroup]").forEach(b => b.onclick = () => {
```
