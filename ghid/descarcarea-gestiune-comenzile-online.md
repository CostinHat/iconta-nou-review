---
title: "Cum se face descărcarea de gestiune pentru comenzile online?"
description: Comenzile emise ca facturi prin API (magazin online, integrare externă) trec prin aceeași poartă obligatorie "pleacă marfa acum?" ca facturile din ecran — dar cu un câmp dedicat, fără valoare implicită.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se face descărcarea de gestiune pentru comenzile online?

Pentru o firmă cu gestiune cantitativ-valorică (articole cu cost pe unitate), fiecare comandă online facturată automat printr-o integrare (API) trece prin aceeași regulă ca o factură emisă manual din ecran: dacă factura are cel puțin o linie legată de un articol de stoc, trebuie spus explicit dacă marfa pleacă acum sau nu. Nu există o descărcare "automată, din oficiu" a gestiunii doar pentru că factura a fost emisă prin integrare.

## Temeiul legal

::: ghid-temei
"441. - (1) Veniturile din vânzarea bunurilor se recunosc în momentul în care sunt îndeplinite următoarele condiții: a) entitatea a transferat cumpărătorului riscurile şi avantajele semnificative care decurg din proprietatea asupra bunurilor; ... (2) Evaluarea momentului în care o entitate a transferat cumpărătorului riscurile şi avantajele semnificative aferente dreptului de proprietate asupra bunurilor impune o examinare a circumstanţelor în care s-a desfăşurat tranzacţia. În cele mai multe cazuri, transferul riscurilor şi avantajelor aferente dreptului de proprietate coincide cu transferul titlului legal de proprietate sau cu trecerea bunurilor în posesia cumpărătorului."
— OMFP 1802/2014, pct. 441 alin. (1)-(2)
:::

Legea leagă recunoașterea vânzării de momentul transferului riscurilor și avantajelor asupra bunului, care de regulă coincide cu predarea lui — moment care, pentru o comandă online, poate să difere de momentul emiterii facturii (de exemplu, marfă rezervată, livrată ulterior). De aceea integrarea trebuie să declare explicit acest moment, nu să-l presupună.

## Ce se greșește în practică

- Integratorul (platforma de magazin online) presupune că, dacă nu trimite nimic, gestiunea rămâne intactă (sau, dimpotrivă, că se descarcă automat) — API-ul nu are valoare implicită: o factură cu linii de stoc, fără acest câmp completat, e respinsă cu eroare, nu emisă cu o presupunere.
- Se confundă numele câmpului din ecran (`pleaca_marfa`) cu cel din API — API-ul de integrare folosește un câmp separat, `marfa_pleaca_cu_factura`; un request construit după numele din ecran nu funcționează.
- Se emit facturi doar pentru servicii (fără linie de articol) și se așteaptă poarta — poarta apare doar când există cel puțin o linie legată de un articol de stoc.

## Ce face iConta.eu

Pe ruta de API pentru integratori (emitere de facturi pentru tenant, ex. dintr-un magazin online), dacă factura conține cel puțin o linie legată de un articol de stoc, aplicația cere explicit câmpul `marfa_pleaca_cu_factura` (adevărat/fals). Dacă acest câmp lipsește, cererea este respinsă cu eroarea `POARTA_GESTIUNE_FARA_RASPUNS`, cu mesaj explicit — nu se presupune niciun răspuns. Dacă valoarea trimisă e "adevărat", gestiunea se descarcă automat, în aceeași operațiune cu emiterea facturii, folosind exact același motor ca și emiterea din ecran (mișcarea de stoc e legată de factură, nota contabilă rezultată rămâne ciornă, iar un eventual stoc insuficient nu blochează emiterea — apare raportat separat, în răspunsul cererii). Data la care se înregistrează descărcarea este data facturii (cea trimisă de integrator, sau data curentă dacă lipsește).

Menționăm onest o limitare: dacă valoarea trimisă e "fals" (marfa nu pleacă odată cu factura), gestiunea nu se descarcă deloc la acel moment — livrarea ulterioară, decuplată de factură, se descarcă separat, manual, din ecranul de stocuri, nu automat prin factura inițială.

[iConta.eu](/)
