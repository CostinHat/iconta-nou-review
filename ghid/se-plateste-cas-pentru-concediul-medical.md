---
title: Se plătește CAS pentru concediul medical?
description: Indemnizația de concediu medical este supusă contribuției de asigurări sociale (CAS) de 25%, aplicată uniform pe majoritatea codurilor de boală, inclusiv maternitate și îngrijire copil - dar acesta este un punct bazat pe practica administrativă, nu pe un text explicit al legii.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Se plătește CAS pentru concediul medical?

Da, în regulă generală, din indemnizația brută de concediu medical se reține CAS de 25%, la fel ca din salariu. Este însă un punct care merită nuanțat: reținerea CAS pe indemnizația de concediu medical nu are, la nivelul verificării surselor, un text de lege dedicat descoperit explicit pentru acest caz — se bazează pe practica administrativă (interpretare oficială), nu pe o formulare directă și separată în actul normativ pentru indemnizații.

## Temeiul legal

::: ghid-temei
**Codul fiscal, Articolul 138 lit.a)** — cota de 25% pentru contribuția de asigurări sociale, aplicabilă persoanelor cu calitate de angajați (articolul confirmat la sursă, fără citat extins disponibil pentru formularea integrală).

**Codul fiscal, Articolul 156:** *"Cota de contribuție de asigurări sociale de sănătate este de 10%."*

**Codul fiscal, Articolul 62 lit.c):** *"indemnizațiile pentru: risc maternal, maternitate, creșterea copilului și îngrijirea copilului bolnav, îngrijirea pacientului cu afecțiuni oncologice, potrivit legii;"* — aceste indemnizații sunt neimpozabile (fără impozit pe venit), dar textul nu le scutește de CAS.
:::

## De ce e o zonă bazată pe interpretare, nu pe text explicit

Pentru salariu, CAS de 25% e clar reglementat de Codul fiscal (art.138). Pentru indemnizațiile de asigurări sociale de sănătate (concediu medical), Codul fiscal nu conține însă o formulare separată, la fel de directă, care să spună explicit "din indemnizația de concediu medical se reține CAS de 25%". Aplicarea CAS pe aceste indemnizații — inclusiv pe maternitate și îngrijire copil bolnav — este o practică administrativă consacrată, tratată ca atare: regula se aplică, dar cu precizarea onestă că baza ei este practica/ghidul administrativ, nu un articol de lege citat explicit pentru acest caz particular.

Important de reținut: CAS 25% se reține pe majoritatea codurilor de indemnizație (inclusiv codul 01 - boală obișnuită, codul 08 - maternitate, codul 10 - reducere program de muncă). CASS de 10% se reține însă doar pentru anumite coduri, iar impozitul de 10% nu se aplică deloc pe indemnizațiile enumerate expres ca neimpozabile (maternitate, risc maternal, îngrijire copil, îngrijire oncologică).

::: ghid-exemplu
O indemnizație brută de concediu medical (cod 01) de 1.300 lei suportă CAS de 25% = 325 lei, indiferent dacă se aplică și CASS sau impozit, care depind de codul de boală.
:::

## Ce se greșește în practică

- Se presupune că indemnizația de concediu medical e complet scutită de contribuții, pentru că e o "compensație", nu un salariu.
- Se aplică CAS doar pe concediul medical obișnuit (cod 01), omițând că se aplică uniform și pe maternitate, îngrijire copil bolnav sau alte coduri.
- Se confundă neimpozabilitatea (scutirea de impozit pe venit, pentru anumite coduri) cu scutirea de CAS — sunt lucruri diferite.
- Se prezintă regula CAS 25% pe indemnizații ca fiind un articol de lege explicit, când în realitate e o practică administrativă consacrată.

## Ce face iConta.eu

Funcția de calcul al reținerilor pe indemnizație (`taxe_cm`) aplică CAS de 25% UNIFORM pe toate codurile de concediu medical. Codul sursă marchează explicit acest punct drept „interpretare oficială" (nivel de sursă distinct de un text de lege citat direct), recunoscând că regula reflectă practica administrativă. CASS de 10% se reține doar pentru codurile 01, 07 și 10, iar impozitul de 10% se aplică pe (brut − CASS), cu excepția codurilor neimpozabile prevăzute expres de Codul fiscal (08, 09, 15, 17, 91, 92).

[iConta.eu](/)
