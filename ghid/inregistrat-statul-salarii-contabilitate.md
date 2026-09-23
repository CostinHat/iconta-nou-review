---
title: Ce fac dacă nu am înregistrat statul de salarii în contabilitate?
description: Dacă D112 declară sume pe impozit, CAS, CASS sau CAM iar conturile 444/4315/4316/436 sunt la zero și nu există nicio notă (nici în ciornă), statul de salarii lipsește pur și simplu din evidență — remediul e contabilizarea lui, nu o ajustare a contului.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă nu am înregistrat statul de salarii în contabilitate?

Statul de salarii al unei luni poate fi calculat și depus corect în D112 fără să fi ajuns și în evidența contabilă. iConta.eu distinge exact acest caz de o simplă divergență de sumă, pentru că soluția e diferită: nu se ajustează un cont, se contabilizează statul de plată.

## Temeiul legal

::: ghid-temei
"Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

D112 se depune indiferent dacă statul de salarii a fost sau nu contabilizat — obligația de declarare (art. 147) și evidența contabilă sunt două fluxuri separate. Când o firmă declară corect la ANAF, dar uită să înregistreze nota contabilă aferentă, apar diferențe: contul de credit (444 pentru impozit, 4315 pentru CAS, 4316 pentru CASS, 436 pentru CAM) rămâne la zero, în timp ce D112 arată o sumă datorată.

iConta.eu recunoaște acest tipar specific — cont contabil zero, sumă declarată pozitivă, și nicio notă de salarii (nici măcar nevalidată) — și îl marchează cu un remediu executabil direct: "Contabilizează statul de plată", nu doar un avertisment generic.

Important: dacă există deja o notă de salarii, dar e în ciornă (nevalidată), cazul e altul — remediul e "validează nota", nu o contabilizare de la zero. Evidența contabilă ia în calcul, prin regula generală de înregistrare cronologică (validarea notelor), doar liniile validate, nu ciornele nevalidate.

## Ce se greșește în practică

Greșeala tipică e depunerea la timp a D112 (pentru a evita penalitățile de declarare) urmată de amânarea notei contabile aferente — mai ales la firme cu mulți angajați, unde nota de salarii e complexă și cere timp pentru verificare. Diferența rămâne nedetectată până la o verificare de tip control încrucișat, sau, mai grav, până la un control ANAF.

## Ce face iConta.eu

Funcția `compara_d112` (`core/control_incrucisat.py`) tratează explicit cazul "cont 0, D112 pozitiv, fără notă" ca roșu cu remediu executabil ("Contabilizează statul de plată"), separat de cazul cu notă în ciornă (remediu "Validează nota") și de orice altă divergență (remediu investigație). Comparația citește rulajele contabile doar din notele cu statut validat — o notă în ciornă nu contează ca evidență, exact ca să nu se raporteze fals că statul a fost înregistrat.

[iConta.eu](/)
