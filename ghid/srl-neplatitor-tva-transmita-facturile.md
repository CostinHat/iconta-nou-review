---
title: "Un SRL neplătitor de TVA trebuie să transmită facturile în e-Factura"
description: "Dacă obligația RO e-Factura pentru facturile B2B depinde de înregistrarea în scopuri de TVA a firmei emitente."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Un SRL neplătitor de TVA trebuie să transmită facturile în e-Factura

Obligația de a transmite facturile prin sistemul național RO e-Factura pentru relațiile B2B nu e condiționată de înregistrarea în scopuri de TVA. Legea vizează persoanele impozabile stabilite în România, indiferent dacă sunt sau nu plătitoare de TVA — deci și un SRL neplătitor de TVA, care emite facturi către alți operatori economici stabiliți în România, are aceeași obligație.

## Temeiul legal

::: ghid-temei
„Operatorii economici - persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015 privind Codul fiscal, cu modificările și completările ulterioare, indiferent dacă sunt sau nu înregistrați în scopuri de TVA conform art. 316 din Legea nr. 227/2015, cu modificările și completările ulterioare, pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România [...] efectuate în relația B2B [...] au obligația în perioada 1 ianuarie 2024-30 iunie 2024 să transmită facturile emise în sistemul național privind factura electronică RO e-Factura [...], indiferent dacă destinatarii sunt sau nu înregistrați în Registrul RO e-Factura."
— Legea nr. 296/2023, art. LIX alin. (1) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)

„În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Ordonanța de urgență nr. 120/2021, art. 10 alin. (1), astfel cum a fost modificat prin Legea nr. 296/2023 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

**Notă de precizie:** citatul din art. LIX alin. (1) a fost o regulă tranzitorie, valabilă strict pentru perioada 1 ianuarie–30 iunie 2024. Începând cu 1 iulie 2024, obligația generală de transmitere B2B a fost preluată de forma permanentă a art. 10 alin. (1) din OUG 120/2021 (reprodusă mai sus) — care nu mai repetă expres formularea „indiferent dacă sunt sau nu înregistrați în scopuri de TVA", dar se aplică oricărei „persoane impozabile stabilite în România conform art. 266 alin. (2) din Codul fiscal", categorie care, prin definiția din Codul fiscal, nu presupune înregistrarea în scopuri de TVA.

- **Criteriul legal e "persoană impozabilă stabilită în România"**, nu "plătitor de TVA" — cele două nu se suprapun; un SRL poate fi persoană impozabilă (desfășoară activitate economică) fără să fie înregistrat în scopuri de TVA (de exemplu, sub plafonul de scutire).
- **Formularea explicită "indiferent dacă sunt sau nu înregistrați în scopuri de TVA"** din regula tranzitorie (art. LIX alin. (1)) confirmă, pentru perioada ei de aplicare, că interpretarea corectă exclude scutirea neplătitorilor de TVA de la obligația RO e-Factura — iar forma permanentă a art. 10 alin. (1) păstrează același criteriu, prin trimiterea la definiția persoanei impozabile din art. 266 alin. (2) Cod fiscal.
- **Excepțiile de la obligație** sunt altele decât statutul de TVA — de exemplu livrările scutite specifice de la art. 294 alin. (1) lit. a) și b), facturile simplificate sau relațiile cu persoane nestabilite și neînregistrate în scopuri de TVA în România.

## Ce se greșește în practică

- Se presupune că regimul de TVA (neplătitor sau sub plafonul de scutire) exclude automat firma de la RO e-Factura — legea nu face această legătură.
- Se transmite factura doar către clienți persoane fizice sau instituții publice (unde regulile B2C/B2G diferă), omițând obligația pentru facturile emise către alți operatori economici (B2B).
- Se ignoră termenul de transmitere (5 zile lucrătoare de la emitere) pentru că firma "oricum nu colectează TVA", deși sancțiunea pentru nerespectarea termenului nu depinde de statutul de plătitor.

## Ce face iConta.eu

Modulele de e-Factura din iConta.eu (`core/efactura_send.py`, `core/efactura_trimitere.py`, `core/spv_conector.py`) transmit facturile emise în sistemul RO e-Factura indiferent de statutul de plătitor de TVA al firmei, pe baza obligației generale B2B de la art. 10 alin. (1) din OUG 120/2021 (forma actuală, modificată prin Legea nr. 296/2023) — aplicația nu condiționează trimiterea de existența unui cod de TVA activ al emitentului.

[iConta.eu](/)
