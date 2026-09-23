---
title: Ce faci cu o încasare în cont de la un client necunoscut?
description: Când extrasul bancar nu conține un CUI identificabil în descrierea liniei, potrivirea automată eșuează și încasarea rămâne fără alocare — corelarea cu factura potrivită sau înregistrarea corectă se face manual.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci cu o încasare în cont de la un client necunoscut?

O sumă încasată în bancă, a cărei descriere nu conține un CUI identificabil (sau nu se poate lega de un partener cu facturi deschise), nu se stinge automat — aplicația o marchează ca neidentificată, iar corelarea corectă trebuie făcută manual, de contabil.

## Temeiul legal

::: ghid-temei
"Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." — Legea contabilității 82/1991, art. 6 alin. (1)

Extrasul de cont bancar rămâne document justificativ chiar și când partenerul nu poate fi identificat automat din descriere: "documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: aviz de însoțire a mărfii, chitanță, dispoziție de plată/încasare, **extras de cont bancar**, notă de contabilitate etc." — OMFP 2634/2015, Anexa 1, pct. 25
:::

Obligația legală rămâne aceeași — orice sumă intrată în cont trebuie înregistrată în contabilitate pe baza extrasului de cont, indiferent dacă partenerul e imediat identificabil sau nu. Lipsa identificării automate a partenerului nu e un motiv de a lăsa suma neînregistrată la nesfârșit — e un semnal că investigarea (contactarea băncii, a clientului, verificarea altor documente) trebuie făcută manual, înainte de contabilizare.

## Ce se greșește în practică

Cea mai frecventă greșeală: ignorarea liniilor de extras fără partener identificat, lăsându-le nealocat un timp îndelungat — ceea ce, la firmele cu TVA la încasare, amână și exigibilitatea TVA fără să se observe. A doua greșeală: alocarea „la întâmplare" a sumei pe prima factură deschisă găsită, doar ca linia să dispară din listă, fără verificare reală a identității plătitorului.

## Ce face iConta.eu

Motorul de potrivire caută mai întâi un CUI în descrierea liniei de extras. Dacă nu găsește niciun CUI, sau găsește unul dar acesta nu are nicio factură deschisă pe direcția de încasare, linia primește direct statusul „roșu" — neidentificată, fără alocare automată. Ambele module implicate (contabilizarea extrasului și reconcilierea cu facturile) documentează explicit acest caz ca fiind unul de corelare manuală, nu de eroare a sistemului.

Pentru rezolvare, contabilul are la dispoziție alocarea manuală — un selector de facturi deschise ale unui partener ales manual, cu posibilitatea de alocare pe una sau mai multe facturi și calculul restului. Dacă suma nu corespunde niciunei facturi existente (de exemplu, un avans sau o eroare de plată a clientului), înregistrarea se face printr-o notă de jurnal manuală, în afara fluxului automat de reconciliere.

[iConta.eu](/)
