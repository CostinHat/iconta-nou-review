---
title: "Care este diferența dintre plafonul micro și plafonul TVA în 2026?"
description: "Cele două praguri distincte — 100.000 euro pentru încadrarea ca microîntreprindere și 395.000 lei pentru scutirea de TVA — și de ce nu trebuie confundate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este diferența dintre plafonul micro și plafonul TVA în 2026?

Firmele mici din România se lovesc adesea de doi „plafoane" diferite, care nu au nicio legătură directă unul cu celălalt, deși ambele se raportează la veniturile firmei: plafonul de încadrare ca **microîntreprindere** (impozit pe veniturile microîntreprinderilor) și plafonul de **scutire de TVA** pentru întreprinderile mici. Depășirea unuia nu înseamnă automat depășirea celuilalt.

## Temeiul legal

::: ghid-temei
„a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile;"
— Codul fiscal (Legea nr. 227/2015), art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Persoana impozabilă stabilită în România [...], a cărei cifră de afaceri anuală, declarată sau realizată, nu depășește plafonul de 395.000 lei, poate aplica scutirea de taxă, denumită în continuare regim special de scutire, pentru operațiunile prevăzute la art. 268 alin. (1) [...]"
— Codul fiscal (Legea nr. 227/2015), art. 310 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **Plafonul micro** (art. 47 alin. (1) lit. c)) este de **100.000 euro**, exprimat în echivalent lei la cursul de la închiderea exercițiului financiar, și privește **veniturile** firmei, verificate la 31 decembrie a anului precedent, pentru a stabili dacă firma poate aplica impozitul pe veniturile microîntreprinderilor.
- **Plafonul de TVA** (art. 310 alin. (1)) este de **395.000 lei** și privește **cifra de afaceri** relevantă pentru TVA (definită la art. 310 alin. (2), cu excluderi precum livrările de active fixe corporale), determinând dacă firma poate rămâne neplătitoare de TVA sau trebuie să se înregistreze în scopuri de TVA.
- Cele două plafoane se calculează pe **baze diferite** (venituri totale vs. cifră de afaceri relevantă pentru TVA) și **momente diferite** de verificare (anual, la 31 decembrie, pentru micro; continuu, pe parcursul anului, pentru TVA).
- O firmă poate fi, în același timp, plătitoare de impozit micro **și** plătitoare de TVA (dacă a depășit plafonul de 395.000 lei), sau neplătitoare de TVA dar la impozit pe profit (dacă a depășit plafonul micro de 100.000 euro, dar are cifra de afaceri sub plafonul de TVA).

## Ce se greșește în practică

- Se crede că cele două plafoane sunt sinonime sau că depășirea unuia declanșează automat depășirea celuilalt.
- Se calculează plafonul de TVA folosind veniturile totale ale firmei, în loc de cifra de afaceri relevantă pentru TVA definită la art. 310 alin. (2), care exclude anumite operațiuni (de exemplu livrările de active fixe).
- Se ignoră faptul că plafonul micro se verifică o singură dată pe an (la închiderea exercițiului precedent), în timp ce plafonul de TVA trebuie monitorizat continuu, pe măsură ce se acumulează cifra de afaceri în cursul anului curent.
- Se presupune că o firmă micro este automat scutită de TVA, deși cele două regimuri sunt complet independente unul de celălalt.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu urmărește separat, prin constante și module dedicate fiecărei declarații fiscale (de exemplu logica de TVA la încasare din `core/tva_incasare.py`), diverse praguri legale relevante pentru declarațiile aplicabile firmei. Nu am găsit însă, în cod, un ecran sau modul unic care să compare explicit, pentru contabil, plafonul micro (100.000 euro) cu plafonul de TVA (395.000 lei) într-o singură vedere — cele două rămân, la acest moment, verificări separate în aplicație.

[iConta.eu](/)
