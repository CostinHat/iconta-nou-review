---
title: Sunt deductibile ajustările pentru deprecierea creanțelor?
description: Ajustările pentru deprecierea creanțelor sunt deductibile la 30% (peste 270 de zile de la scadență) sau la 100% (faliment/insolvență a debitorului), doar dacă creanța nu e garantată și nu e la o persoană afiliată.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Sunt deductibile ajustările pentru deprecierea creanțelor?

Ajustările pentru deprecierea creanțelor (cont 491) sunt printre puținele provizioane/ajustări pe care Codul fiscal le acceptă la deducere, dar nu integral și nu necondiționat. Există două praguri de deducere — 30% și 100% — fiecare cu propriile condiții cumulative, iar o creanță garantată sau la o persoană afiliată nu e deductibilă deloc, indiferent de vechime sau de starea debitorului.

## Temeiul legal

::: ghid-temei
"ajustările pentru deprecierea creanțelor, înregistrate potrivit reglementărilor contabile aplicabile,
reprezentând sume datorate de clienții interni și externi pentru produse, semifabricate, materiale,
mărfuri vândute, lucrări executate și servicii prestate, în limita unui procent de 30% din valoarea
acestor ajustări, altele decât cele prevăzute la lit. d)-f), h) și i), dacă creanțele îndeplinesc
cumulativ următoarele condiții:
1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței;
2. nu sunt garantate de altă persoană;
3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului;"

"ajustările pentru deprecierea creanțelor înregistrate potrivit reglementărilor contabile aplicabile,
în limita unui procent de 100% din valoarea creanțelor, altele decât cele prevăzute la lit. d), e),
f), h) și i), dacă creanțele îndeplinesc cumulativ următoarele condiții:
1. sunt deținute la o persoană juridică asupra căreia este declarată procedura de deschidere a
falimentului, pe baza hotărârii judecătorești prin care se atestă această situație, sau la o persoană
fizică asupra căreia este deschisă procedura de insolvență pe bază de: – plan de rambursare a
datoriilor; – lichidare de active; – procedură simplificată;
2. nu sunt garantate de altă persoană;
3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului;"
:::

## Cele două praguri, pas cu pas

Condițiile de la fiecare literă sunt **cumulative** — trebuie îndeplinite toate, nu doar una:

1. **30% (art. 26 alin. (1) lit. c))** — creanța e neîncasată de peste 270 de zile de la scadență, nu e garantată, nu e la o persoană afiliată.
2. **100% (art. 26 alin. (1) lit. j))** — debitorul (persoană juridică) are declarată procedura de faliment prin hotărâre judecătorească, sau (persoană fizică) e în procedură de insolvență; în plus, creanța nu e garantată și nu e la o persoană afiliată.

Condiția de negarantare și de neafiliere se verifică **înaintea** oricărui calcul de vechime sau de stadiu de insolvență: o creanță garantată sau la un afiliat rămâne nedeductibilă chiar dacă debitorul a intrat în faliment.

::: ghid-exemplu
O creanță de 10.000 lei, neîncasată de 300 de zile, negarantată, la un client neafiliat: ajustarea contabilă constituită integral (10.000 lei) e deductibilă fiscal în limita a 30% din valoarea ei, adică 3.000 lei; restul de 7.000 lei rămâne cheltuială nedeductibilă. Dacă în schimb debitorul intră în faliment declarat prin hotărâre judecătorească, ajustarea devine deductibilă 100%, adică 10.000 lei.
:::

## Ce se greșește în practică

- Se aplică procentul de 30% (sau 100%) direct la soldul creanței, nu la valoarea ajustării contabile constituite.
- Se ignoră condiția de negarantare — o creanță garantată (ex. printr-o scrisoare de garanție bancară) rămâne nedeductibilă indiferent de vechime.
- Se aplică deducerea pentru creanțe la persoane afiliate, deși legea o exclude explicit.
- Se calculează greșit pragul de 270 de zile ca "270 de zile de la data facturii" în loc de "de la data scadenței".
- Se confundă pragul de 270 de zile (impozit pe profit) cu pragurile complet diferite prevăzute pentru ajustarea TVA (vezi ghidul dedicat).

## Ce face iConta.eu

Funcția `deductibilitate_creanta(zile_depasire_scadenta, garantata, afiliata, faliment_declarat)` din `core/provizioane.py` aplică exact această ordine de verificare: o creanță garantată sau afiliată primește 0% necondiționat, indiferent de celelalte argumente; abia apoi se verifică falimentul declarat (100%) și, în lipsa lui, depășirea celor 270 de zile (30%, strict peste prag). Notă: aplicația nu calculează automat pierderea propriu-zisă la scoaterea din evidență a creanței (vezi ghidul „Când pot deduce pierderea dintr-o creanță neîncasată?") și nu preia automat rezultatul în D101 — valoarea nedeductibilă trebuie introdusă manual la rândurile corespunzătoare.

[iConta.eu](/)
