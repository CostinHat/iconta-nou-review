---
title: "Greșeli la contractele de mandat: contribuții omise"
description: Cea mai gravă greșeală la contractele de mandat nu e taxarea în plus, ci omiterea completă a CAS/CASS, tratând administratorul sau cenzorul ca pe un colaborator fără contribuții.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeli la contractele de mandat: contribuții omise

Pentru că mandatul de administrator sau de cenzor nu e un raport de muncă, apare des o confuzie inversă față de cea obișnuită: dacă nu e „salariu", unii presupun că nu se datorează nicio contribuție socială. E o greșeală — CAS și CASS rămân datorate. Iar CAM (contribuția asiguratorie pentru muncă) NU lipsește automat: pentru administratori și pentru directorii cu contract de mandat, remunerația intră în baza CAM (art. 220^4 alin. (1) lit. d) și e) din Codul fiscal); doar pentru cenzori CAM nu se datorează.

## Temeiul legal

::: ghid-temei
„sumele primite de membrii comisiei de cenzori sau comitetului de audit, după caz, precum și sumele primite pentru participarea în consilii, comisii, comitete și altele asemenea"

*(Codul fiscal — Legea nr. 227/2015, art. 76 alin. (2) lit. i), pentru cenzori)*
:::

Pentru administratorul cu contract de mandat, temeiul corespunzător e **art. 76 alin. (2) lit. o)** din același cod — remunerația administratorilor de societăți.

## Ce se omite frecvent

- **CAS (25%) și CASS (10%)**, sub premisa greșită că, neexistând raport de muncă, nu există nici obligație de contribuții sociale — de fapt, veniturile din mandat sunt asimilate salariilor tocmai la acest capitol, prin art. 76 alin. (2), și rămân în sfera contribuțiilor.
- **CASS**, în special, e uneori omisă separat de CAS — poate rezultă din presupunerea că regulile de plafon minim de la activitățile independente (venituri din alte surse, PFA) s-ar aplica și mandatului, deși acesta e asimilat salariilor, nu independent.
- **Reținerea corectă a impozitului pe baza netă** (după CAS și CASS), nu pe brutul integral.

## Ce nu se datorează, corect

CAM (contribuția asiguratorie pentru muncă) se datorează diferit, după tipul mandatului: pentru **administratori** (tip asigurat 6) și pentru **directorii cu contract de mandat** (tip 3.4), remunerația e inclusă expres în baza CAM — art. 220^4 alin. (1) lit. d) și e) din Codul fiscal, confirmat de Nomenclatorul „Tip asigurat” din OPANAF 605/2026 (D112), unde aceste tipuri au CAM = Da. Doar pentru **cenzori** (tip asigurat 4) CAM nu se datorează. Așadar, la mandatul de administrator omiterea CAM este greșită; e corectă doar la cenzor. CAS și CASS rămân datorate în toate cazurile.

## Ce se greșește în practică

- Se tratează integral remunerația de mandat/cenzor ca „fără contribuții”, omițând CAS/CASS (întotdeauna greșit) și CAM — omiterea CAM fiind greșită la administrator și la directorul cu contract de mandat, corectă doar la cenzor.
- Se citează greșit temeiul pentru administrator — lit. g) în loc de lit. o) — ceea ce poate duce la aplicarea, din confuzie, a regulilor de la altă categorie de venit.

## Ce face iConta.eu

Funcția `calcul_mandat(brut)` din modulul F021 (`core/contracte_speciale.py`) calculează întotdeauna CAS 25% și CASS 10% pentru mandat și cenzor, alături de impozitul de 10% pe rest — nu există în cod o variantă „fără contribuții" pentru aceste categorii. Nota contabilă generată (`nota(fel="mandat"/"cenzor")`) include automat pasul `421 = 4315` (CAS) și, dacă suma rezultă pozitivă, `421 = 4316` (CASS) — omiterea lor ar necesita o abatere manuală de la fluxul standard al aplicației, nu un comportament implicit.

[iConta.eu](/)
