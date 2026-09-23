---
title: Ce conturi contabile trebuie să corespundă cu D112?
description: Doar patru conturi contabile intră în controlul încrucișat cu D112 — 444, 4315, 4316 și 436. Contul 421 (brutul) e explicit exclus din verificare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce conturi contabile trebuie să corespundă cu D112?

Nu toată contabilitatea salarială se compară cu D112 — doar patru conturi, cele care corespund direct obligațiilor fiscale declarate. Restul (inclusiv brutul angajaților) rămâne în afara acestei verificări, din motive legate de cum e construită declarația.

## Temeiul legal

::: ghid-temei
"Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Cele patru conturi verificate, fiecare cu codul D112 aferent și cota legală:

| Cont | Obligație | Cod D112 | Cotă | Temei |
|---|---|---|---|---|
| 444 | Impozit pe venit din salarii | 602 | 10% | CF art. 64 alin. (1) |
| 4315 | CAS | 412 + 458 | 25% | CF art. 138 lit. a) |
| 4316 | CASS | 432 + 459 | 10% | CF art. 156 |
| 436 | CAM | 480 | 2,25% | CF art. 220^3 alin. (1) |

Codurile 458 și 459 sunt suprataxa datorată de angajator pentru anumite contracte part-time și se contabilizează tot în 4315, respectiv 4316 — nu formează conturi separate.

**Ce nu se verifică:** contul 421 (salariile datorate angajaților — brutul). D112 raportează baza de contribuții, nu brutul contabil, iar cele două diverg legitim pe lunile cu concedii medicale (baza de calcul a indemnizațiilor urmează reguli proprii, din OUG 158/2005). De aceea includerea contului 421 în verificare ar produce diferențe false pe orice lună cu concediu medical.

## Ce se greșește în practică

Greșeala tipică e așteptarea ca soldul contului 421 (sau salariile nete plătite) să corespundă cu vreo sumă din D112 — nu există o astfel de corespondență directă, pentru că D112 nu raportează brutul, ci baza de contribuții pe fiecare tip de obligație.

## Ce face iConta.eu

Maparea `COD_CONT_D112` din `core/control_incrucisat.py` definește exact aceste patru perechi cod-cont, fără contul 421. Controlul încrucișat compară doar aceste patru conturi cu sumele declarate în D112, iar limitarea privind brutul e documentată explicit în rezultatul verificării, nu ascunsă.

[iConta.eu](/)
