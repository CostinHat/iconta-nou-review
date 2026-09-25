---
title: Ce cont se folosește pentru transferul banilor între casă și bancă
description: Viramentele între casă și cont bancar (sau între conturi bancare) trec prin contul 581 "Viramente interne" (OMFP 1802/2014), cont de activ folosit tocmai pentru intervalul în care banii sunt "pe drum" între cele două evidențe.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce cont se folosește pentru transferul banilor între casă și bancă?

Ridicarea de numerar din bancă pentru casierie, sau depunerea încasărilor din casierie la bancă, nu se înregistrează direct 531 = 512 (sau invers) — pentru că, în realitate, între momentul ridicării/depunerii și momentul confirmării în extrasul de cont trece timp, uneori câteva zile. Pentru exact acest interval există un cont dedicat.

### Contul 581 "Viramente interne"

OMFP 1802/2014: "Cu ajutorul acestui cont se ține evidența viramentelor de disponibilități între conturile de trezorerie." Contul 581 este **cont de activ**.

- În **debitul** contului 581 se înregistrează sumele virate dintr-un cont de trezorerie în alt cont de trezorerie (contrapartidă: 512 bancă, 531 casă, 541 acreditive).
- În **creditul** contului 581 se înregistrează sumele intrate într-un cont de trezorerie din alt cont de trezorerie (aceleași contrapartide: 512, 531, 541).

Norma precizează explicit: "**De regulă, contul nu prezintă sold**" — pentru că e un cont de tranzit, folosit doar cât timp mișcarea de bani e în curs, nu ca o poziție permanentă în bilanț.

### Exemplu de flux — ridicare numerar de la bancă pentru casierie

1. Firma ridică 2.000 lei numerar de la bancă pentru casierie.
2. La momentul ridicării (dispoziția de plată către bancă emisă, dar suma încă neconfirmată în casierie): 581 = 512 (2.000 lei) — banii ies din contul bancar.
3. La momentul intrării efective a numerarului în casierie (pe bază de foaie de vărsământ/chitanță): 531 = 581 (2.000 lei) — banii intră în casă.

Dacă cele două momente se produc practic simultan (aceeași zi, aceeași operațiune), unele firme simplifică înregistrarea direct 531 = 512, dar folosirea contului 581 rămâne corectă și recomandată ori de câte ori există un decalaj real între cele două evidențe, mai ales la transferuri între bănci diferite sau la depuneri de numerar care se confirmă cu întârziere în extras.

### Exemplu de flux — transfer între două conturi bancare ale firmei

Când firma transferă bani din contul de la Banca A în contul de la Banca B:

1. Ieșirea din contul de la Banca A: 581 = 512.01 (analitica Banca A)
2. Intrarea în contul de la Banca B, la confirmarea în extras: 512.02 (analitica Banca B) = 581

Motivul pentru care nu se face direct 512.02 = 512.01: transferul între bănci diferite nu e instantaneu — poate dura de la câteva ore la 1-2 zile lucrătoare, iar contul 581 reflectă corect faptul că banii au ieșit dintr-o evidență și nu au intrat încă în cealaltă.

### Checklist

1. Orice mișcare de bani între casă și bancă, sau între două conturi bancare, trece prin 581, nu direct între cele două conturi de trezorerie.
2. La sfârșitul fiecărei luni, verifică soldul contului 581 — dacă nu e zero, înseamnă că există un virament neconfirmat, care trebuie urmărit și lămurit (bani ieșiți dintr-un cont, dar neintrați încă în celălalt, la data raportării).
3. Documentele justificative pentru fiecare parte a operațiunii: dispoziția de plată/ordinul de virament pentru ieșire, extrasul de cont sau foaia de vărsământ/chitanța pentru intrare.
