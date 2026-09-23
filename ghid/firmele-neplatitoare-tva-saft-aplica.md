---
title: "Firmele neplătitoare de TVA și SAF-T: se aplică"
description: Un SRL neplătitor de TVA nu scapă de D406 — rămâne obligat structural, doar periodicitatea se schimbă la trimestrial.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Firmele neplătitoare de TVA și SAF-T: se aplică

Statutul de neplătitor de TVA nu scutește o firmă de obligația SAF-T (D406) — obligația de a depune D406 e legată de forma juridică a firmei, nu de statutul ei de plătitor de TVA. Ce se schimbă, în funcție de acest statut, e doar periodicitatea de depunere.

## Temeiul legal

::: ghid-temei
„Contribuabilii care nu sunt înregistraţi în scopuri de TVA transmit Declaraţia informativă D406 trimestrial."

*(OPANAF nr. 1783/2021, Anexa 4, pct. 3)*
:::

## Cine e obligat, indiferent de TVA

Categoriile de contribuabili obligate să depună D406 sunt stabilite structural, prin OPANAF 407/2025, Anexa 5, pct. 3 — printre ele, explicit, societățile cu răspundere limitată (S.R.L.). Statutul de TVA nu apare printre criteriile de excludere (Anexa 5, pct. 4) — acolo sunt exceptate, de exemplu, persoanele fizice autorizate (PFA), întreprinderile individuale (II), întreprinderile familiale (IF) și alte categorii care țin contabilitatea în partidă simplă, nu firmele neplătitoare de TVA cu contabilitate în partidă dublă.

Concluzia practică: **un SRL neplătitor de TVA e obligat să depună D406, trimestrial** — obligat prin forma juridică (Anexa 5, pct. 3), cu periodicitatea dată de statutul de TVA (Anexa 4, pct. 3, citat mai sus).

## Ce se greșește în practică

- **Se presupune că neplătitorii de TVA sunt scutiți integral de D406** — confuzie între „nu depun decont de TVA" și „nu depun deloc SAF-T"; cele două obligații sunt independente.
- **Se aplică periodicitate lunară din prudență**, deși legea fixează trimestrial pentru neplătitorii de TVA — o periodicitate greșită poate genera confuzie la depunere, chiar dacă nu e o eroare de fond.
- **Se confundă excluderea de la D406 a PFA/II/IF (partidă simplă) cu o excludere generală a „firmelor mici"** — un SRL rămâne obligat indiferent de mărime, din 2025 pentru toate categoriile (mari, mijlocii, mici).

## Ce face iConta.eu

Motorul F022 (`core/control_fiscal_api.py`) derivă automat periodicitatea D406 din regimul de TVA al firmei: dacă firma nu e plătitoare de TVA, generează verdictul pe fereastră trimestrială; dacă e plătitoare, urmărește exact perioada ei fiscală de TVA (lunar sau trimestrial), trecând automat la trimestrial dacă perioada declarată e semestrială sau anuală. Regula de fond e aceeași cu cea folosită de generatorul propriu-zis al declarației D406: deși semaforul F022 nu apelează direct funcția comună `core/common.py::fereastra_d406` (are propria implementare, prin `emite_tva`/`per_trim`/`per_luni`), ambele căi se bazează pe aceeași sursă de adevăr pentru perioada TVA din `core/common.py`, ceea ce asigură consecvența între cele două.

[iConta.eu](/)
