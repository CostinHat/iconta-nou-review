---
title: Ce fac dacă statul de salarii nu corespunde cu D112?
description: O divergență roșie între contabilitate și D112 nu se rezolvă cu o ajustare "ca să dea verde" — remediul depinde de cauză (stat necontabilizat, notă în ciornă sau diferență neclară), și fiecare are un pas concret diferit.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă statul de salarii nu corespunde cu D112?

Când controlul încrucișat D112 vs. contabilitate arată roșu pe unul dintre cele patru conturi (444, 4315, 4316, 436), pasul următor depinde de motivul divergenței — nu există un singur remediu universal. iConta.eu distinge automat între trei situații și recomandă acțiuni diferite pentru fiecare.

## Temeiul legal

::: ghid-temei
"Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Divergența dintre suma declarată în D112 și rulajul contabil (creditul conturilor 444/4315/4316/436) poate avea trei explicații distincte, iar remediul corect se stabilește după cauză:

- **Contul e 0, D112 declară o sumă, și nu există nicio notă (nici măcar în ciornă)** → statul de salarii pur și simplu nu a fost contabilizat. Remediul e executabil: contabilizează statul de plată aferent lunii verificate.
- **Contul e 0, D112 declară o sumă, dar există o notă de salarii în ciornă (nevalidată)** → nota există, dar nu a intrat încă în evidență. Remediul e "validează nota" — contabilitatea recunoaște doar liniile validate, nu ciornele.
- **Diferența nu se încadrează în niciunul din cazurile de mai sus** (de exemplu contul are deja o sumă, dar nu egală cu declaratul) → cauza nu poate fi dedusă automat. Posibile explicații: salariați adăugați sau șterși după contabilizare, note manuale directe pe cont, corecții de lună anterioară sau concedii medicale înregistrate diferit față de D112. În acest caz remediul e investigație manuală, nu o ajustare automată a contului.

## Ce se greșește în practică

Cea mai frecventă greșeală e "ajustarea" contului contabil (o notă manuală care aduce soldul la valoarea din D112) doar ca verificarea să dea verde, fără să se identifice cauza reală a diferenței. Asta poate ascunde o eroare reală de calcul sau o depunere greșită la ANAF. A doua greșeală e ignorarea distincției dintre "notă lipsă" și "notă în ciornă" — cele două au remedii diferite (contabilizare de la zero, respectiv validarea unei note deja existente).

## Ce face iConta.eu

Funcția `compara_d112` din `core/control_incrucisat.py` separă exact aceste cazuri: stat necontabilizat → remediu executabil ("Contabilizează statul de plată"), notă cunoscută în ciornă → remediu sugerat ("Validează nota"), orice altă divergență → remediu de tip investigație, cu cauzele posibile enumerate explicit în răspuns. Aplicația nu propune niciodată o ajustare a contului doar pentru a elimina o culoare roșie.

[iConta.eu](/)
