---
title: "Cum se plătesc dividendele prin bancă?"
description: "Ordinea corectă a înregistrărilor pentru plata prin bancă a dividendelor: repartizare, impozit reținut și viramentul net către asociat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se plătesc dividendele prin bancă?

Plata dividendelor nu este o simplă ieșire de bani din contul firmei: contabil, ea presupune trei pași distincți — repartizarea dividendului, reținerea impozitului și abia apoi viramentul net către asociat.

## Temeiul legal

::: ghid-temei
„Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social vărsat, opțional trimestrial pe baza situațiilor financiare interimare și anual, după regularizarea efectuată prin situațiile financiare anuale [...]" — Legea 31/1990, art. 67 alin. (2)

„Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. [...] Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata." — Codul fiscal, art. 97 alin. (7), în forma dată de Legea 141/2025, art. II pct. 5 (cotă de 16% pentru dividende plătite începând cu 01.01.2026; 10% pentru dividendele plătite în 2025, potrivit OUG 156/2024)
:::

Ordinea corectă a operațiunilor este: (1) se repartizează dividendul brut, (2) se calculează și se reține impozitul pe dividende la cota în vigoare la data plății, (3) se virează prin bancă doar diferența netă către asociat. Pentru dividendul anual (aprobat prin situațiile financiare anuale), notele folosesc contul 457 „Dividende de plată". Pentru dividendul interimar (distribuit trimestrial, înainte de aprobarea situațiilor anuale), OMFP 1802/2014 pct. 423^1 impune folosirea contului 463: „Entitățile care au optat [...] să repartizeze dividende în cursul exercițiului financiar evidențiază acea repartizare în contul 463 «Creanțe reprezentând dividende repartizate în cursul exercițiului financiar» (articol contabil 463 = 456 «Decontări cu acționarii/asociații privind capitalul»)."

## Ce se greșește în practică

Greșeala cea mai frecventă este virarea către asociat a dividendului brut, fără reținerea impozitului — ceea ce obligă ulterior la o corecție și la calculul unor eventuale accesorii. A doua greșeală este folosirea acelorași conturi pentru dividendul interimar ca pentru cel anual: dividendul trimestrial trece prin 463/456, nu prin 1171/457, iar confuzia celor două monografii duce la solduri greu de reconciliat la regularizarea de la finalul anului. În fine, cota de impozit se schimbă în timp (16% de la 1 ianuarie 2026, 10% pentru plățile din 2025) — aplicarea cotei curente unei plăți efectuate anterior este o eroare de dată, nu de monografie.

## Ce face iConta.eu

Modulul de decontări asociați din iConta (ecranul Operațiuni speciale > Finanțare, secțiunea „Decontări asociați") generează nota de dividend pe baza sumei brute și a datei plății. Pentru dividendul anual, linia generată este 1171=457 (brut), apoi 457=446 (impozit); pentru cel interimar, 463=456 (brut), apoi 456=446 (impozit). Cota de impozit nu este fixă în cod: aplicația o citește dintr-un registru intern actualizat pentru fiecare interval de aplicare (16% din 2026, 10% în 2025 etc.), astfel încât nota generată la o dată din trecut folosește automat cota corectă pentru acea dată. Dacă se bifează plata efectivă, aplicația adaugă automat și linia de virament net către contul bancar (457=5121, respectiv 456=5121).

[iConta.eu](/)
