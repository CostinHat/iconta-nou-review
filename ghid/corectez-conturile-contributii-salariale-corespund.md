---
title: Cum corectez conturile de contribuții salariale dacă nu corespund cu D112?
description: CAS (4315), CASS (4316) și CAM (436) se corectează diferit față de simplul „ajustezi soldul" — iConta.eu identifică, pentru fiecare cont în parte, dacă lipsește contabilizarea, dacă nota e doar în ciornă sau dacă e nevoie de investigație.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez conturile de contribuții salariale dacă nu corespund cu D112?

Spre deosebire de impozit (contul 444), contribuțiile salariale sunt urmărite pe trei conturi distincte — CAS, CASS și CAM — fiecare cu propria pereche de coduri D112 și propria cotă legală. Corectarea lor înseamnă identificarea cauzei pe fiecare cont în parte, nu o singură ajustare globală.

## Temeiul legal

::: ghid-temei
„Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Cele trei conturi de contribuții și cotele lor: CAS (coduri D112 412 + 458, cont 4315) — 25%, conform art. 138 lit. a) din Codul fiscal; CASS (coduri 432 + 459, cont 4316) — 10%, conform art. 156; CAM (cod 480, cont 436) — 2,25%, conform art. 220^3 alin. (1).

## Ce se greșește în practică

O greșeală frecventă este ignorarea codurilor 458 și 459 — suprataxa datorată de angajator la anumite contracte part-time — care se contabilizează tot în 4315, respectiv 4316, nu separat; o corecție care nu ține cont de ele va părea greșit calculată. A doua greșeală este corectarea unui singur cont (de exemplu doar CAS) fără a verifica și celelalte două — cele trei conturi sunt verificate independent, iar cauza divergenței poate fi diferită de la unul la altul.

## Ce face iConta.eu

Pentru fiecare din cele trei conturi, funcția `compara_d112` (`core/control_incrucisat.py`) compară suma declarată (coduri D112 relevante, incluzând suprataxa 458/459 unde e cazul) cu rulajul creditor al contului, citit doar din notele validate, și aplică toleranța de rotunjire (0,5 lei per salariat, minim 1 leu). În funcție de rezultat:

- Cont la zero, fără nicio notă → remediu executabil, „contabilizează statul de plată" pentru contribuția respectivă.
- Cont la zero, dar cu notă de salarii în ciornă → remediu sugerat, „validează nota".
- Orice altă divergență → remediu de investigație, cu cauzele posibile enumerate (salariați modificați ulterior, note manuale pe cont, corecții de lună anterioară, concedii medicale cu bază de calcul diferită conform OUG 158/2005).

Aplicația nu propune niciodată o ajustare directă a soldului doar pentru a elimina o culoare roșie — remediul indicat depinde de cauza reală identificată pentru fiecare cont în parte.

[iConta.eu](/)
