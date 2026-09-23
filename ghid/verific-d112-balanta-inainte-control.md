---
title: Cum verific D112 cu balanța înainte de control?
description: Înaintea unui control, iConta.eu compară D112 cu rulajul contabil pe patru conturi (444, 4315, 4316, 436), cu toleranță de rotunjire și trei stări posibile — util ca verificare preventivă, nu doar ca reacție la o inspecție.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific D112 cu balanța înainte de control?

Cel mai bun moment să descoperi o divergență între D112 și contabilitate nu este în timpul unui control ANAF, ci înainte de el — când mai poți investiga cauza și, dacă e nevoie, corecta declarația sau nota contabilă. iConta.eu face acest control încrucișat oricând, nu doar la cerere.

## Temeiul legal

::: ghid-temei
„Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Verificarea compară, pentru fiecare lună, sumele declarate în D112 cu rulajul creditor al patru conturi contabile: 444 (impozit, cod 602, 10% conform art. 64 alin. 1), 4315 (CAS, coduri 412+458, 25% conform art. 138 lit. a), 4316 (CASS, coduri 432+459, 10% conform art. 156) și 436 (CAM, cod 480, 2,25% conform art. 220^3 alin. 1).

## Ce se greșește în practică

Greșeala frecventă este să se aștepte până aproape de un control pentru a face această verificare, deși ea poate fi rulată oricând, pentru orice lună închisă. A doua greșeală este să se trateze orice diferență ca fiind normală („e doar rotunjire") fără să se verifice dacă se încadrează efectiv în toleranța calculată — 0,5 lei per salariat, minim 1 leu; peste acest prag, diferența are o cauză reală care merită clarificată înainte, nu în timpul controlului.

## Ce face iConta.eu

Funcția `verifica_d112` (`core/control_incrucisat.py`) rulează controlul pentru orice lună, indiferent de context — poate fi folosită oricând, ca verificare preventivă. Compară sumele declarate (din XML-ul D112 efectiv depus și persistat, dacă există, altfel dintr-o regenerare — cu sursa comunicată explicit) cu rulajul conturilor 444/4315/4316/436, citit doar din notele validate. Rezultatul are trei stări: verde (în toleranță), roșu (diferență reală, cu cauza cea mai probabilă și remediul asociat — contabilizare, validare de notă sau investigație) și gri (D112 nu s-a putut genera, cu cauza explicată, nu un mesaj generic). Dacă luna nu a avut salariați, D112 nu se datorează, iar aplicația nu produce niciun verdict pe acea lună — nici verde, nici roșu, nici gri — ca să nu sugereze o verificare pe un subiect inexistent. Rularea acestei verificări lună de lună, înainte de orice control, e modul de a intra pregătit — cu diferențele deja explicate sau corectate, nu descoperite pe loc.

[iConta.eu](/)
