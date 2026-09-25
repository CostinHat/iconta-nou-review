---
title: "Ce fac dacă plata apare în extrasul bancar, dar nu apare stinsă în fișa pe plătitor?"
description: "De ce o plată deja debitată din bancă poate să nu apară stinsă în fișa pe plătitor de la ANAF: mecanismul contului unic și momentul legal al plății."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă plata apare în extrasul bancar, dar nu apare stinsă în fișa pe plătitor?

Banii au ieșit din contul firmei, extrasul bancar o arată clar — dar în fișa pe plătitor de la ANAF, obligația respectivă apare încă neachitată. Diferența nu e neapărat o eroare: are, de multe ori, o explicație în mecanismul contului unic prin care ANAF distribuie sumele plătite.

## Temeiul legal

::: ghid-temei
„(2) În cazul creanțelor fiscale administrate de organul fiscal central și organul fiscal local, debitorii efectuează plata acestora într-un cont unic ... (4) în cazul în care suma plătită nu acoperă obligațiile fiscale datorate unui buget sau fond, distribuirea în cadrul fiecărui buget sau fond se face în următoarea ordine: a) pentru toate impozitele și contribuțiile sociale cu reținere la sursă; b) pentru toate celelalte obligații fiscale principale; c) pentru obligațiile fiscale accesorii aferente obligațiilor prevăzute la lit. a) și b)."
— Legea 207/2015 (Codul de procedură fiscală), art. 163 alin. (2) și (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„(11) În cazul stingerii prin plată a obligațiilor fiscale ... momentul plății este: ... d) în cazul plăților efectuate prin decontare bancară, inclusiv internet banking, home banking, mobile banking ..., data la care băncile debitează contul persoanei care efectuează plata pe baza instrumentelor de decontare specifice, astfel cum această informație este transmisă prin mesajul electronic de plată de către instituția bancară inițiatoare."
— Legea 207/2015 (Codul de procedură fiscală), art. 163 alin. (11) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din text rezultă două lucruri utile pentru diagnostic:

- Legal, **momentul plății** e data la care banca a debitat contul, nu data la care ANAF procesează sau afișează suma în fișa pe plătitor. Dacă extrasul arată debitarea, plata e efectuată din punct de vedere legal, chiar dacă afișarea la ANAF întârzie.
- Plățile către bugetul de stat merg într-un **cont unic**, iar ANAF le **distribuie automat** pe obligații, într-o ordine fixă: mai întâi impozite/contribuții cu reținere la sursă, apoi celelalte obligații principale, apoi accesoriile. Dacă suma plătită nu acoperă tot ce e scadent, o parte din plată se duce pe altă obligație decât cea vizată de contabil — ceea ce poate lăsa exact obligația urmărită „neachitată" în fișă.

Dovada plății, dacă apare o divergență, se face conform art. 163 alin. (11^1): extrasul de cont original sau copia certificată e document valabil pentru a dovedi atât efectuarea, cât și data plății.

## Ce se greșește în practică

- Se presupune direct că fișa pe plătitor e greșită sau că ANAF „nu a primit banii", fără a verifica întâi dacă suma plătită a fost suficientă să acopere toate obligațiile scadente în ordinea legală de distribuire (reținere la sursă → alte obligații principale → accesorii).
- Se ignoră decalajul tehnic de procesare dintre data debitării bancare (momentul legal al plății) și data la care fișa pe plătitor reflectă efectiv stingerea — o discrepanță de câteva zile nu înseamnă automat o eroare.
- Se contestă divergența fără extrasul de cont ca probă, deși legea indică explicit acest document ca dovadă a plății și a datei ei.

## Ce face iConta.eu

La data acestui ghid, iConta.eu importă și interpretează extrasele bancare (identificarea automată a plăților și încasărilor din extras), dar aplicația **nu reconciliază automat** aceste plăți cu fișa pe plătitor de la ANAF — o comparație directă între ce a plătit firma și ce apare stins la ANAF rămâne, la acest moment, o verificare manuală, prin Spațiul Privat Virtual.

[iConta.eu](/)
