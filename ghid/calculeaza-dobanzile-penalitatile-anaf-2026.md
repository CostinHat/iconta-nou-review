---
title: "Cum se calculează dobânzile și penalitățile ANAF 2026"
description: "Nivelurile dobânzii de întârziere, ale penalității de întârziere și ale penalității de nedeclarare, potrivit Codului de procedură fiscală, și diferența dintre ele."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează dobânzile și penalitățile ANAF 2026

„Dobânzi și penalități" nu sunt, fiscal, același lucru — Codul de procedură fiscală definește trei obligații fiscale accesorii distincte, cu cote diferite și condiții diferite de aplicare, care se pot cumula pentru aceeași obligație principală neplătită la termen.

## Temeiul legal

::: ghid-temei
„Nivelul dobânzii este de 0,02% pentru fiecare zi de întârziere."
— Legea 207/2015, art. 174 alin. (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Nivelul penalității de întârziere este de 0,01% pentru fiecare zi de întârziere."
— Legea 207/2015, art. 176 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„Pentru obligațiile fiscale principale nedeclarate sau declarate incorect de contribuabil/plătitor și stabilite de organul fiscal prin decizii de impunere, contribuabilul/plătitorul datorează o penalitate de nedeclarare de 0,08% pe fiecare zi, începând cu ziua imediat următoare scadenței și până la data stingerii sumei datorate, inclusiv [...]"
— Legea 207/2015, art. 181 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Cele trei accesorii, cu rolurile lor distincte:

- **Dobânda** — 0,02%/zi de întârziere — se aplică oricărei sume neplătite la scadență, indiferent dacă a fost corect declarată sau nu; e „prețul" banilor datorați bugetului cu întârziere.
- **Penalitatea de întârziere** — 0,01%/zi — se cumulează, în anumite situații, cu dobânda, pentru sume declarate corect dar neplătite la scadență.
- **Penalitatea de nedeclarare** — 0,08%/zi, semnificativ mai mare — se aplică nu pentru simpla întârziere la plată, ci pentru obligații **nedeclarate sau declarate incorect**, constatate ulterior de organul fiscal printr-o decizie de impunere. Legea prevede și o reducere de 75% dacă suma se stinge prin plată/compensare până la un anumit termen, sau dacă se eșalonează la plată.
- Penalitatea de nedeclarare nu înlătură obligația de plată a dobânzii — cele două se pot cumula pentru aceeași sumă, spre deosebire de penalitatea de întârziere, care are alt regim.

## Ce se greșește în practică

- Se calculează o singură „penalitate", fără să se distingă între penalitatea de întârziere (0,01%/zi, pentru sume declarate corect dar plătite târziu) și penalitatea de nedeclarare (0,08%/zi, pentru sume nedeclarate sau declarate greșit, constatate de organul fiscal) — diferența de cotă e de opt ori.
- Se ignoră reducerea de 75% a penalității de nedeclarare, disponibilă dacă suma stabilită prin decizie se stinge prin plată sau compensare până la termenul legal, sau dacă se eșalonează la plată.
- Se presupune că plata dobânzii acoperă și penalitatea — sunt obligații accesorii distincte, care se cumulează, nu se substituie una pe cealaltă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează automat** dobânzile și penalitățile de întârziere aferente obligațiilor fiscale neplătite la termen, potrivit art. 174, 176 și 181 din Codul de procedură fiscală — aplicația generează declarațiile fiscale (D100, D112, D300 etc.) cu sumele datorate, dar accesoriile pentru eventuale întârzieri la plată sau la declarare rămân calculate de ANAF, comunicate ulterior prin decizii sau prin contul unic al contribuabilului, în afara aplicației.

[iConta.eu](/)
