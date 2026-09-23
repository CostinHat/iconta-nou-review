---
title: Cum reconciliezi taxele salariale din balanță cu D112?
description: Reconcilierea taxelor salariale cu D112 se face pe patru perechi cont-cod, cu sursa declarației (depusă sau regenerată), toleranță proporțională cu efectivul și trei stări de verdict — verde, roșu, gri.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum reconciliezi taxele salariale din balanță cu D112?

Reconcilierea completă a taxelor salariale înseamnă compararea, lună de lună, a patru obligații fiscale declarate în D112 cu conturile contabile corespunzătoare — nu o singură verificare globală, ci patru comparații independente, fiecare cu propriul remediu în caz de divergență.

## Temeiul legal

::: ghid-temei
"Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Pașii unei reconcilieri complete:

1. **Alege sursa declarației.** Dacă D112 a fost efectiv depusă și XML-ul a fost persistat, folosește-l pe acela — reflectă ce a văzut ANAF. Dacă nu, se folosește o regenerare a D112 pentru luna respectivă, pornind de la datele curente din statele de plată.
2. **Extrage sumele pe cele patru coduri relevante** direct din XML (elementul cu totalurile angajatorului), nu printr-o recalculare paralelă din salariați individuali — o a doua cifră calculată separat ar putea diverge de D112 chiar și când ambele sunt corecte (de exemplu din cauza recalculărilor pe concedii medicale).
3. **Extrage rulajul creditor** al conturilor 444, 4315, 4316 și 436, dar numai din notele contabile validate — o notă în ciornă nu e evidență.
4. **Compară fiecare pereche** cu toleranța de 0,5 lei per salariat (minim 1 leu).
5. **Pentru fiecare divergență peste toleranță**, identifică dacă e stat necontabilizat, notă în ciornă sau altă cauză (salariați adăugați/șterși, corecții, concedii medicale) — și aplică remediul specific, nu o ajustare a contului.
6. **Reține ce nu intră în reconciliere**: contul 421 (brutul) — D112 raportează baza de contribuții, nu brutul, iar cele două diverg legitim pe lunile cu concedii medicale.

## Ce se greșește în practică

Greșeala tipică e tratarea reconcilierii ca pe o singură cifră totală ("taxele salariale" ca sumă globală), în loc de patru comparații separate pe conturi distincte — o compensare între un cont în plus și altul în minus poate masca o eroare reală pe fiecare din ele individual.

## Ce face iConta.eu

`verifica_d112` (`core/control_incrucisat.py`) automatizează cei șase pași de mai sus pentru fiecare lună: alege sursa corectă a declarației, parsează sumele din XML, citește rulajele validate, aplică toleranța dinamică și afișează verdictul pe fiecare cont în parte, cu cauza divergenței și remediul recomandat — niciodată o cifră agregată care ar putea ascunde erori individuale.

[iConta.eu](/)
