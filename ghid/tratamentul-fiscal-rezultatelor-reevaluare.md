---
title: Tratamentul fiscal al rezultatelor din reevaluare
description: Rezultatul unei reevaluări (creștere sau scădere) nu se impozitează la fel ca un venit sau o cheltuială obișnuită — creșterea e neimpozabilă imediat, scăderea e nedeductibilă, iar rezerva constituită devine oricum impozabilă mai târziu.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Tratamentul fiscal al rezultatelor din reevaluare

Rezultatul unei reevaluări nu urmează regulile fiscale obișnuite ale unui venit sau ale unei cheltuieli — regimul e special, gândit să nu impoziteze o simplă schimbare de valoare contabilă, dar nici să n-o scutească definitiv de impozit.

## Temeiul legal

::: ghid-temei
"veniturile reprezentând creșteri de valoare rezultate din reevaluarea mijloacelor fixe, terenurilor, imobilizărilor necorporale, după caz, care compensează cheltuielile cu descreșterile anterioare aferente aceleiași imobilizări" [venituri neimpozabile] — Legea 227/2015, art. 23 lit. g)

"cheltuielile din reevaluarea imobilizărilor necorporale/mijloacelor fixe, în cazul în care, ca urmare a efectuării unei reevaluări efectuate potrivit reglementărilor contabile aplicabile, se înregistrează o descreștere a valorii acestora" [cheltuieli nedeductibile] — Legea 227/2015, art. 25 alin. (4) lit. l)

"rezervele din reevaluarea mijloacelor fixe, inclusiv a terenurilor, efectuată după data de 1 ianuarie 2004, care sunt deduse la calculul profitului impozabil prin intermediul amortizării fiscale sau al cheltuielilor privind activele cedate și/sau casate, se impozitează concomitent cu deducerea amortizării fiscale, respectiv la momentul scăderii din gestiune a acestor mijloace fixe, după caz" — Legea 227/2015, art. 26 alin. (6)
:::

Patru reguli formează tabloul complet:

1. **Creșterea "simplă"**, care intră în rezerva din reevaluare (cont 105, OMFP 1802/2014 pct. 111 alin. (1)), nu trece prin contul de profit și pierdere — nu generează impozit pe profit imediat.
2. **Creșterea care compensează** o descreștere anterioară recunoscută ca cheltuială la același activ (cont 755) e explicit **neimpozabilă** (art. 23 lit. g) — regula elimină dubla impunere a aceleiași diferențe de valoare, în timp.
3. **Scăderea** (cont 655) e, ca regulă, **cheltuială nedeductibilă** fiscal (art. 25 alin. (4) lit. l).
4. **Rezerva constituită** din creșteri (cont 105) nu rămâne definitiv neimpozitată: se impozitează treptat, pe măsură ce e „consumată" prin amortizarea fiscală, sau integral, dintr-odată, la scăderea din gestiune (cedare/casare) a activului — art. 26 alin. (6).

Cu alte cuvinte: momentul reevaluării în sine e, de regulă, neutru fiscal pentru o creștere simplă și nedeductibil pentru o scădere — dar impozitul pe rezerva constituită dintr-o creștere nu dispare, doar se amână.

## Ce se greșește în practică

- Se tratează orice cheltuială din reevaluare (cont 655) ca deductibilă, la fel ca o cheltuială curentă — art. 25 alin. (4) lit. l) o exclude expres de la deducere.
- Se impozitează integral un venit din reevaluare (cont 755) fără să se verifice dacă el compensează o descreștere anterioară a aceluiași activ, caz în care ar fi neimpozabil (art. 23 lit. g).
- Se consideră rezerva din reevaluare (105) definitiv scutită de impozit, ignorând că devine impozabilă la deducerea prin amortizare fiscală sau la scoaterea din evidență a activului (art. 26 alin. (6)).

## Ce face iConta.eu

Motorul de reevaluare generează corect notele contabile aferente celor două ramuri (creștere/scădere), respectând ordinea din OMFP 1802/2014 pct. 111 alin. (1)-(2) — inclusiv compensarea unei creșteri cu o pierdere anterioară pe 655, sau consumarea unei rezerve existente la o scădere. Aplicația nu calculează însă și nu semnalează automat consecințele fiscale de mai sus — deductibilitatea cheltuielii 655, neimpozabilitatea condiționată a venitului 755 sau impozitarea amânată a rezervei 105 conform art. 26 alin. (6). Aceste verificări rămân, deocamdată, în sarcina contabilului, în evidența fiscală extracontabilă.

[iConta.eu](/)
