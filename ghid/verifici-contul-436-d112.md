---
title: Cum verifici contul 436 cu D112?
description: Contul 436 (CAM) trebuie să corespundă, pe rulaj creditor, cu codul 480 din D112 — singura obligație salarială care nu se împarte pe două coduri, fiind integral în sarcina angajatorului.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici contul 436 cu D112?

Contribuția asiguratorie pentru muncă (CAM) e cea mai simplă din punct de vedere al comparației cu D112 — un singur cod, un singur cont, fără componentă de suprataxă separată de reținut.

## Temeiul legal

::: ghid-temei
"Cota contribuției asiguratorii pentru muncă este de 2,25%." — Codul fiscal (Legea 227/2015), art. 220^3 alin. (1)
:::

Rulajul creditor al contului **436** trebuie să corespundă cu codul **480** din D112 — CAM, calculat pe cota de 2,25% conform art. 220^3 alin. (1) din Codul fiscal, în întregime în sarcina angajatorului (spre deosebire de CAS și CASS, care sunt rețineri din venitul angajatului).

Spre deosebire de CAS (4315) și CASS (4316), CAM nu are un cod suplimentar pentru suprataxa part-time — comparația e directă, un singur cod față de un singur cont.

Toleranța de comparație e aceeași regulă generală folosită pentru toate cele patru conturi: maximul dintre 1 leu și 0,5 lei înmulțit cu numărul de salariați ai lunii, nu o valoare fixă, pentru a absorbi rotunjirile legitime care cresc cu efectivul.

Când diferența depășește toleranța, cauzele posibile sunt aceleași ca la celelalte trei conturi: stat de plată necontabilizat, notă în ciornă nevalidată, sau modificări ulterioare ale statului de plată (salariați adăugați/șterși, corecții de lună anterioară).

## Ce se greșește în practică

Greșeala tipică e confuzia dintre CAM și CAS/CASS ca natură — CAM e cheltuială a angajatorului, nu reținere din salariul angajatului, deci nu apare nicăieri în calculul salariului net. Absența ei din fluturașul de salariu al angajatului e normală, nu o eroare.

## Ce face iConta.eu

Maparea `COD_CONT_D112` din `core/control_incrucisat.py` compară direct codul 480 cu rulajul creditor al contului 436, cu toleranța standard calculată pe numărul de salariați ai lunii. Verdictul (verde/roșu/gri) și cauza divergenței sunt afișate exact ca la celelalte trei conturi verificate.

[iConta.eu](/)
