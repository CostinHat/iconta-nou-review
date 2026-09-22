---
title: Care este monografia contabilă pentru cumpărarea mărfurilor?
description: Achiziția de mărfuri se înregistrează 371 = 401 pentru bază și 4426 = 401 pentru TVA deductibilă, conform planului de conturi OMFP 1802/2014; dacă doar furnizorul e la TVA la încasare (nu și firma proprie), contarea automată e refuzată și cere intervenție manuală, nu trece automat pe 4428.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Care este monografia contabilă pentru cumpărarea mărfurilor?

Cumpărarea de mărfuri e una dintre cele mai frecvente operațiuni contabile, dar are un detaliu ușor de scăpat din vedere: contul de TVA folosit nu e mereu 4426 — depinde de regimul de TVA la încasare al furnizorului sau al firmei proprii.

## Temeiul legal

::: ghid-temei
„371. Mărfuri (A)" — OMFP 1802/2014

„401. Furnizori (P)" — OMFP 1802/2014

„4426. TVA deductibilă (A)
4427. TVA colectată (P)
4428. TVA neexigibilă (A/P)" — OMFP 1802/2014

Contul 4428 „Taxa pe valoarea adăugată neexigibilă": „este un cont bifuncțional. […] taxa pe valoarea adăugată neexigibilă devenită exigibilă (4428)." — OMFP 1802/2014

„(2) Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă de la o persoană impozabilă care aplică sistemul TVA la încasare conform prevederilor art. 282 alin. (3)-(8) este amânat până la data la care taxa aferentă bunurilor și serviciilor care i-au fost livrate/prestate a fost plătită furnizorului/prestatorului său." — Cod fiscal 227/2015, art. 297 alin. (2)
:::

## Nota de bază, și excepția de TVA la încasare

Pentru o factură primită de marfă, în regim normal, nota e simplă: **371 = 401** pentru valoarea mărfii (baza), și **4426 = 401** pentru TVA-ul deductibil.

Excepția apare când e implicat regimul de TVA la încasare — al firmei proprii sau al furnizorului:

- Dacă **firma proprie** e la TVA la încasare, toate achizițiile ei (indiferent de regimul furnizorului) intră pe **4428** în loc de 4426 — deducerea e amânată, conform art. 297 alin. (3), până la plata efectivă către furnizor.
- Dacă firma e în regim normal, dar **furnizorul** e la TVA la încasare, deducerea e amânată pentru contabilul care operează factura (art. 297 alin. 2) — trebuie tratată manual, nu automat, tocmai pentru că regula depinde de un fapt (regimul furnizorului) care cere confirmare explicită înainte de a alege între 4426 și 4428.

::: ghid-exemplu
O factură de achiziție marfă, 1.000 lei bază + TVA la cota standard aplicabilă (de exemplu 21%): în regim normal se înregistrează 371 = 401 cu 1.000 lei și 4426 = 401 cu suma de TVA aferentă. Dacă firma proprie e la TVA la încasare, a doua notă devine 4428 = 401, nu 4426 = 401 — taxa rămâne neexigibilă până la plata facturii.
:::

Pentru alte tipuri de achiziții, planul de conturi diferă: materii prime pe 301, materiale consumabile pe 302, obiecte de inventar pe 303, iar anumite mijloace fixe (instalații tehnice și mijloace de transport) pe 213 — mapări distincte de 371, folosite doar pentru marfă cumpărată în scop de revânzare.

## Ce se greșește în practică

- Se înregistrează TVA-ul de pe factura de achiziție pe 4427 (TVA colectată) în loc de 4426 (TVA deductibilă) — 4427 e contul pentru facturile emise, nu pentru cele primite.
- Se ignoră regimul de TVA la încasare al furnizorului și se postează direct pe 4426, deși deducerea ar trebui amânată.
- Se presupune că o factură de marfă primită apare deja contată în sistem imediat ce e vizibilă — de fapt, contarea facturilor primite se face la validare, nu la simpla înregistrare a documentului.
- Se așteaptă ca o factură de marfă importată automat din SPV să fie deja contată — importul aduce documentul, dar nu declanșează automat generarea notei.
- Se folosește contul 371 și pentru achiziții care ar trebui să meargă pe 301/302/303 (materii prime, materiale, obiecte de inventar) doar pentru că e „contul implicit cunoscut".

## Ce face iConta.eu

Pentru facturile primite de marfă, motorul de calcul mapează tipul „marfa" pe contul 371 pentru bază, cu TVA-ul pe 4426 — sau pe 4428, dacă se aplică TVA la încasare (fie al firmei proprii, fie al furnizorului, conform art. 297). Dacă firma proprie e la TVA la încasare, toate facturile primite intră pe 4428, indiferent de regimul furnizorului. Dacă firma e în regim normal, dar furnizorul e la TVA la încasare, automatul **refuză** contarea și cere intervenție manuală, citând explicit temeiul legal — un comportament așteptat, nu o eroare a aplicației. Contarea propriu-zisă a unei facturi primite se face la validarea ei, nu la crearea/importul documentului; facturile intrate prin import SPV/XML rămân necontate până la o acțiune explicită. Alte tipuri de achiziție (materii prime, materiale, obiecte de inventar, anumite imobilizări) au propriile conturi în maparea implicită, distincte de 371.

[iConta.eu](/)
