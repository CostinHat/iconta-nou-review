---
title: Cum se declară facturile cu TVA la încasare în D394?
description: Bifa prin care contabilul marchează, pe factura de achiziție, că furnizorul aplică TVA la încasare e confirmată în cod ca alimentând rândul B1 din D300 — tratamentul acelorași facturi în D394 nu a fost verificat în cercetarea de temei.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară facturile cu TVA la încasare în D394?

Pentru o factură de la un furnizor înscris la TVA la încasare, contabilul are de bifat ceva concret în aplicație — dar destinația exactă a acelei informații, în raportarea D394, nu e confirmată de cercetarea de temei a acestui ghid.

## Temeiul legal

::: ghid-temei
**Art. 297 alin. (2) CF**: *„Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă de la o persoană impozabilă care aplică sistemul TVA la încasare... este amânat până la data la care taxa aferentă... a fost plătită furnizorului."*

Verificat direct în codul sursă (`static/js/ecrane/facturi_ecran.js`, linia 142): `furnizor_tva_incasare: corp.querySelector("#pr-furnizor-incasare").checked, // [B1 D300]`.
:::

## Ce e sigur

Pe factura de achiziție, contabilul bifează manual dacă furnizorul aplică TVA la încasare — informație necesară pentru amânarea dreptului de deducere prevăzută de art. 297 alin. (2). Codul confirmă explicit, prin comentariul `[B1 D300]`, că această bifă alimentează **rândul B1 din D300**. Nu există, conform cercetării de față, o verificare automată a acestei bife împotriva Registrului public al persoanelor care aplică sistemul TVA la încasare, organizat de ANAF (art. 324 alin. (16)) — bifa e declarativă, pe răspunderea contabilului.

## Ce nu am putut confirma

Comentariul din cod leagă explicit această bifă de D300, nu de D394. Cercetarea de temei pentru acest ghid nu a inclus o citire a modulului de generare D394 (`core/d394.py`) — nu putem confirma dacă facturile marcate cu „furnizor TVA la încasare" primesc vreun tratament sau indicator distinct în D394, sau dacă informația respectivă e relevantă deloc pentru acea declarație.

## Ce se greșește în practică

- **Se presupune că bifa „furnizor TVA la încasare" de pe factură are efect și în D394**, pentru că are efect confirmat în D300 — cele două nu sunt automat aceleași, iar acest dosar nu confirmă legătura.
- **Se verifică regimul furnizorului doar din memorie sau din discuții cu acesta**, în loc de Registrul public ANAF (art. 324 alin. (16)), singura sursă oficială.
- **Se lasă nebifată situația furnizorului**, ceea ce lasă neînregistrată amânarea dreptului de deducere de la art. 297 alin. (2).

## Ce face iConta.eu

Aplicația reține alegerea contabilului („furnizor TVA la încasare", da/nu) pe fiecare factură de achiziție, cu efect confirmat asupra rândului B1 din D300. Efectul acestei alegeri asupra raportării D394, dacă există, nu a fost verificat în cercetarea de temei a acestui ghid — recomandăm confirmarea directă a comportamentului, la nevoie, înainte de a-l considera stabilit.

[iConta.eu](/)
