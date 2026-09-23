---
title: Cum se impozitează diferențele din reevaluare
description: O creștere din reevaluare intră, de regulă, în rezervă și nu se impozitează imediat; o scădere e, de regulă, cheltuială nedeductibilă. Excepțiile apar când reevaluările anterioare ale aceluiași activ au avut semn opus.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se impozitează diferențele din reevaluare

Tratamentul fiscal al unei diferențe din reevaluare depinde de semnul ei (creștere sau scădere) și de istoricul reevaluărilor anterioare ale aceluiași activ — dacă a existat deja o descreștere recunoscută drept cheltuială, o creștere ulterioară care o compensează are alt regim decât o creștere "simplă".

## Temeiul legal

::: ghid-temei
"veniturile reprezentând creșteri de valoare rezultate din reevaluarea mijloacelor fixe, terenurilor, imobilizărilor necorporale, după caz, care compensează cheltuielile cu descreșterile anterioare aferente aceleiași imobilizări" [venituri neimpozabile] — Legea 227/2015, art. 23 lit. g)

"cheltuielile din reevaluarea imobilizărilor necorporale/mijloacelor fixe, în cazul în care, ca urmare a efectuării unei reevaluări efectuate potrivit reglementărilor contabile aplicabile, se înregistrează o descreștere a valorii acestora" [cheltuieli nedeductibile] — Legea 227/2015, art. 25 alin. (4) lit. l)
:::

Patru situații, verificate direct în textul Codului fiscal:

1. **Creștere "simplă"** (nu a existat o descreștere anterioară recunoscută la acel activ): intră integral în rezerva din reevaluare (cont 105, OMFP 1802/2014 pct. 111 alin. (1)) — nu trece prin contul de profit și pierdere, deci nu generează impozit pe profit la momentul reevaluării.
2. **Creștere ce compensează o descreștere anterioară**: partea de venit care compensează exact descreșterea recunoscută anterior ca cheltuială (cont 755) e **neimpozabilă** (art. 23 lit. g) — logic, pentru că descreșterea anterioară fusese deja nedeductibilă, iar altfel s-ar impozita de două ori aceeași diferență netă de valoare.
3. **Scădere, fără rezervă anterioară pe acel activ**: întreaga depreciere e cheltuială (cont 655, OMFP 1802/2014 pct. 111 alin. (2)) și, fiscal, **nedeductibilă** (art. 25 alin. (4) lit. l).
4. **Scădere, cu rezervă anterioară pe acel activ**: se scade mai întâi din rezerva existentă (105), iar eventualul rest neacoperit merge tot pe cheltuială nedeductibilă (655).

Conturile 755/venituri, respectiv 655/cheltuieli din reevaluare, apar separat în contul de profit și pierdere doar în cazurile 2 și 3-4 de mai sus — creșterea "simplă" (cazul 1) rămâne integral în bilanț, la rezerve.

## Ce se greșește în practică

- Se deduce automat cheltuiala 655 din descreșterea unei reevaluări, la fel ca orice altă cheltuială — art. 25 alin. (4) lit. l) o exclude explicit de la deducere.
- Se impozitează venitul din cont 755 fără să se verifice dacă el compensează o descreștere anterioară a aceluiași activ (caz în care ar fi neimpozabil, art. 23 lit. g) — regula se aplică per activ, nu global pe categoria de imobilizări.
- Se ignoră complet regimul de mai sus și se tratează diferența din reevaluare exclusiv ca operațiune de bilanț, uitând că rezerva din reevaluare a mijloacelor fixe devine oricum impozabilă ulterior, prin amortizare sau la scoaterea din evidență (Legea 227/2015, art. 26 alin. (6)).

## Ce face iConta.eu

Motorul de reevaluare calculează corect diferența (creștere/scădere) și separă corect porțiunea care merge pe rezervă (105) de cea care trece prin 755/655, respectând ordinea din pct. 111 alin. (1)-(2). Nu marchează însă automat cheltuiala 655 drept "nedeductibilă fiscal" și nu verifică dacă un venit din 755 compensează o descreștere anterioară în sensul art. 23 lit. g) — spre deosebire de alte module ale aplicației (de exemplu provizioanele), unde acest tip de semnalare fiscală există explicit. Recalcularea fiscală a acestor sume rămâne, deocamdată, în sarcina contabilului.

[iConta.eu](/)
