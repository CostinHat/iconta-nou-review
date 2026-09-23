---
title: Cum verifici dacă taxele salariale au fost calculate corect?
description: Verificarea corectitudinii taxelor salariale se face prin comparație cu D112 pe patru conturi, cu trei stări posibile — verde, roșu, gri — și cu limite clar declarate: nu se verifică brutul, iar sursa declarației (depusă sau regenerată) contează.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici dacă taxele salariale au fost calculate corect?

"Corect calculate" înseamnă, în practică, coerente cu ce a fost (sau ar trebui) declarat la ANAF prin D112. Verificarea nu dă un simplu da/nu — poate răspunde și "nu se poate ști", când datele disponibile nu permit un verdict cert.

## Temeiul legal

::: ghid-temei
"Articolul 147 — Depunerea Declarației privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate. (1) Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal (Legea 227/2015), art. 147
:::

Verificarea compară patru taxe salariale (impozit, CAS, CASS, CAM) cu D112, folosind cotele legale — 10% impozit (art. 64 alin. 1), 25% CAS (art. 138 lit. a), 10% CASS (art. 156), 2,25% CAM (art. 220^3 alin. 1) — și produce unul din trei verdicte, nu doar corect/greșit:

- **Verde** — diferența dintre declarat și contabilizat se încadrează în toleranța de rotunjire (0,5 lei per salariat, minim 1 leu).
- **Roșu** — diferența depășește toleranța; aplicația indică și cauza cea mai probabilă (stat necontabilizat, notă în ciornă sau altă divergență de investigat).
- **Gri** — nu se poate da un verdict, fie pentru că D112 nu s-a putut genera (de exemplu perioadă neconfirmată), fie pentru că luna nu a avut salariați, caz în care nu există nimic de verificat.

Gri nu e o eroare a aplicației — e recunoașterea faptului că un verdict verde fals, dat peste date lipsă sau incerte, ar fi mai periculos decât absența unui verdict.

Un detaliu important pentru certitudinea verificării: dacă D112 a fost efectiv depusă la ANAF și XML-ul a fost persistat, verificarea folosește exact acel XML. Dacă nu (de exemplu la declarații importate istoric, fără XML persistat), se folosește o regenerare calculată acum din datele curente — comunicată explicit ca atare, pentru că cele două nu sunt garantat identice.

**Ce nu acoperă verificarea:** dacă brutul contabil (contul 421) e corect — D112 raportează baza de contribuții, nu brutul, iar cele două diverg legitim pe lunile cu concedii medicale (bază de calcul distinctă, conform OUG 158/2005).

## Ce se greșește în practică

Greșeala tipică e interpretarea unui verdict gri drept "totul e în regulă" (pentru că nu e roșu) — gri înseamnă strict că nu s-a putut verifica, nu că e corect. A doua greșeală e ignorarea diferenței dintre XML depus și XML regenerat — dacă declarația a fost depusă cu date diferite de cele calculate acum, verdictul verde de azi nu garantează că și declarația depusă a fost corectă.

## Ce face iConta.eu

`verifica_d112` (`core/control_incrucisat.py`) implementează exact cele trei stări, cu cauza precisă pentru gri (nu un mesaj generic) și cu sursa declarației (depusă/regenerată) comunicată explicit pe fiecare constatare. Comparația propriu-zisă (`compara_d112`) e o funcție pură care nu modifică nimic în baza de date — doar raportează, cu temei legal citat pentru fiecare din cele patru obligații verificate.

[iConta.eu](/)
