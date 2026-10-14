---
title: Cum se declară facturile cu TVA la încasare în D394?
description: Bifa prin care contabilul marchează, pe factura de achiziție, că furnizorul aplică TVA la încasare alimentează rândul B1 din D300 — tratamentul acelorași facturi în D394 nu e confirmat de acest ghid.
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum se declară facturile cu TVA la încasare în D394?

Pentru o factură de la un furnizor înscris la TVA la încasare, contabilul are de bifat ceva concret în aplicație — dar destinația exactă a acelei informații, în raportarea D394, nu e confirmată de acest ghid.

## Temeiul legal

::: ghid-temei
**Art. 297 alin. (2) CF**: *„Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă de la o persoană impozabilă care aplică sistemul TVA la încasare... este amânat până la data la care taxa aferentă... a fost plătită furnizorului."*
:::

## Ce e sigur

Pe factura de achiziție, contabilul bifează manual dacă furnizorul aplică TVA la încasare — informație necesară pentru amânarea dreptului de deducere prevăzută de art. 297 alin. (2). În iConta.eu, câmpul „furnizor cu TVA la încasare” din ecranul facturii alimentează **rândul B1 din D300**. Verificarea față de Registrul public al persoanelor care aplică sistemul TVA la încasare, organizat de ANAF (art. 324 alin. (16)), depinde de drumul pe care intră factura:

- **La validarea unei facturi primite prin SPV**, alegerea „Furnizor cu TVA la încasare” (Da/Nu) e obligatorie și se reține exact cum a făcut-o contabilul — aplicația **nu** o confruntă cu registrul ANAF. Aici bifa e declarativă, pe răspunderea contabilului.
- **La înregistrarea directă a unei facturi primite cu CUI** (fără validarea unei facturi din SPV), aplicația citește statutul furnizorului din registrul ANAF, așa cum era la data emiterii facturii, și îl reține pe factură în locul bifei. Dacă ANAF nu răspunde sau CUI-ul nu e găsit, rămâne ce a declarat contabilul.

## Ce nu am putut confirma

Efectul confirmat al acestei bife este în D300, nu în D394. Acest ghid nu a verificat cum este întocmită D394 în aplicație — nu putem confirma dacă facturile marcate cu „furnizor TVA la încasare" primesc vreun tratament sau indicator distinct în D394, sau dacă informația respectivă e relevantă deloc pentru acea declarație.

## Ce se greșește în practică

- **Se presupune că bifa „furnizor TVA la încasare" de pe factură are efect și în D394**, pentru că are efect confirmat în D300 — cele două nu sunt automat aceleași, iar acest ghid nu confirmă legătura.
- **Se verifică regimul furnizorului doar din memorie sau din discuții cu acesta**, în loc de Registrul public ANAF (art. 324 alin. (16)), singura sursă oficială.
- **Se lasă nebifată situația furnizorului**, ceea ce lasă neînregistrată amânarea dreptului de deducere de la art. 297 alin. (2).

## Ce face iConta.eu

Aplicația reține alegerea contabilului („furnizor TVA la încasare", da/nu) pe fiecare factură de achiziție, cu efect confirmat asupra rândului B1 din D300. Efectul acestei alegeri asupra raportării D394, dacă există, nu a fost verificat pentru acest ghid — recomandăm confirmarea directă a comportamentului, la nevoie, înainte de a-l considera stabilit.

[iConta.eu](/)
