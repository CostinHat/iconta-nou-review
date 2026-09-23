---
title: Cum verifici contul 444 cu D112?
description: Contul 444 (impozit pe venit din salarii) trebuie să corespundă, pe rulaj creditor, cu codul 602 din D112, cu o toleranță de rotunjire proporțională cu numărul de salariați.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici contul 444 cu D112?

Impozitul pe venitul din salarii e, alături de CAM, cea mai directă comparație din controlul D112 vs. contabilitate — un singur cod din declarație, un singur cont contabil, fără componentă de suprataxă.

## Temeiul legal

::: ghid-temei
"Cota de impozit este de 10% și se aplică asupra venitului impozabil..." — Codul fiscal (Legea 227/2015), art. 64 alin. (1)
:::

Rulajul creditor al contului **444** trebuie să corespundă cu codul **602** din D112 — impozitul pe venitul din salarii, calculat cu cota de 10% conform art. 64 alin. (1) din Codul fiscal, aplicată pe baza impozabilă a fiecărui angajat (după scăderea CAS, CASS și, dacă e cazul, a deducerii personale).

Toleranța nu e o valoare fixă de 1 leu, ci maximul dintre 1 leu și 0,5 lei înmulțit cu numărul de salariați ai lunii — D112 rotunjește totalul la leu, iar contabilitatea reflectă suma exactă calculată pentru fiecare salariat, deci diferența legitimă de rotunjire crește cu efectivul.

Când diferența depășește toleranța, verifică în ordine:
1. Statul de plată al lunii a fost contabilizat? Dacă nu, și nu există nici notă în ciornă, remediul e contabilizarea lui.
2. Există o notă de salarii, dar nevalidată (în ciornă)? Remediul e validarea ei.
3. Dacă niciuna din cele de mai sus nu explică diferența, verifică salariați adăugați/șterși după contabilizare, corecții de lună anterioară sau concedii medicale calculate diferit față de D112.

## Ce se greșește în practică

Greșeala tipică e compararea contului 444 cu impozitul teoretic calculat manual pe brutul total al lunii, fără să se țină cont de facilități fiscale sau deduceri personale aplicate individual pe fiecare angajat — suma corectă de comparat e cea efectiv declarată în D112 pentru codul 602, nu o recalculare paralelă.

## Ce face iConta.eu

Maparea `COD_CONT_D112` din `core/control_incrucisat.py` compară direct codul 602 cu rulajul creditor al contului 444, folosind suma parsată din XML-ul D112 (depus sau regenerat), nu o reagregare separată a salariaților — pentru a evita exact acest risc de "a treia cifră" divergentă.

[iConta.eu](/)
