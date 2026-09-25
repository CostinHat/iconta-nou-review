---
title: Cum se închide soldul contului 581?
description: Contul 581 „Viramente interne” este un cont tranzitoriu de activ care evidențiază transferurile de disponibilități între conturile de trezorerie proprii; corect utilizat, el nu prezintă sold la închiderea perioadei — un sold rămas semnalează o eroare de înregistrare, nu o operațiune de închidere propriu-zisă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se închide soldul contului 581?

Întrebarea „cum se închide contul 581" pornește, de cele mai multe ori, de la o premisă greșită: contul 581 nu ar trebui să aibă sold de închis. Dacă are, problema e de identificat și corectat, nu de „închis" printr-o notă contabilă artificială.

### Ce este contul 581

Potrivit planului de conturi general din reglementările contabile aprobate prin OMFP nr. 1.802/2014: „Contul 581 «Viramente interne» [...] ține evidența viramentelor de disponibilități între conturile de trezorerie." Este un cont de activ (A).

- În **debitul** contului se înregistrează sumele virate dintr-un cont de trezorerie în alt cont de trezorerie (în corespondență cu conturile 512 „Conturi curente la bănci", 531 „Casa", 541 „Acreditive").
- În **creditul** contului se înregistrează sumele intrate într-un cont de trezorerie din alt cont de trezorerie (aceleași conturi 512, 531, 541).

Textul reglementării este explicit: „**De regulă, contul nu prezintă sold.**"

### De ce contul 581 este doar tranzitoriu

Contul 581 servește exclusiv ca punte contabilă pentru viramentele între propriile conturi de trezorerie ale entității — de exemplu, o depunere de numerar din casierie (531) în contul bancar (512), sau un transfer între două conturi bancare ale aceleiași firme. Fiecare astfel de operațiune presupune două înregistrări simetrice:

```
581 "Viramente interne" = 531 "Casa"          (ridicare numerar din casă)
512 "Conturi curente la bănci" = 581 "Viramente interne"   (depunere în bancă)
```

Dacă ambele înregistrări sunt făcute corect și complet, la finalul perioadei debitul și creditul contului 581 se compensează exact, iar soldul rămâne zero.

### Când apare totuși un sold

Un sold rezidual în contul 581 la închiderea lunii/anului indică, de regulă:

- o operațiune de virament înregistrată doar pe una dintre cele două laturi (de exemplu s-a înregistrat ridicarea din casă, dar nu s-a mai înregistrat încă intrarea în bancă — tipic pentru un virament „în tranzit" la data de închidere, generat de decalajul dintre data ridicării și data creditării în extrasul bancar);
- o eroare de înregistrare (sumă greșită, cont de contrapartidă greșit).

### Cum se rezolvă practic

1. **Verificați dacă e vorba de un virament „în tranzit"** — de exemplu numerar ridicat de la bancă pe 31 decembrie, dar înregistrat în casierie abia pe 2 ianuarie. În acest caz, soldul temporar în 581 la data bilanțului este normal și se lămurește odată cu înregistrarea completării operațiunii, nu se „forțează" la zero printr-o notă artificială.
2. **Dacă nu există o explicație de tranzit**, identificați operațiunea incompletă (comparați rulajele debitoare și creditoare ale contului pe perioada analizată) și completați înregistrarea lipsă sau corectați eroarea.
3. **Nu treceți soldul rezidual pe cheltuieli/venituri** doar pentru a „închide" contul — un sold nejustificat în 581 este un semnal de eroare de reconciliere bancă-casă, nu o diferență de regularizat pe rezultat.

### De reținut

- Contul 581 este un cont de tranzit, nu un cont de rezultat — scopul lui e să existe temporar pentru fiecare operațiune, nu să acumuleze sold.
- La închiderea exercițiului financiar, orice sold în 581 trebuie explicat expres (tranzit legitim sau eroare corectată), nu ignorat sau forțat la zero.
