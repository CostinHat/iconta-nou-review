---
title: "Integrarea e-Factura cu programul de gestiune"
description: iConta nu sincronizează cu un program de gestiune extern — facturarea și legătura cu SPV trăiesc în aceeași aplicație, conectată direct la ANAF prin conexiunea OAuth a cabinetului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Integrarea e-Factura cu programul de gestiune

Întrebarea presupune adesea un model cu două aplicații separate — una de gestiune, una de contabilitate, sincronizate între ele. În iConta, arhitectura e alta, și merită spusă direct, ca să nu se caute o funcționalitate care nu există sub forma așteptată.

## Temeiul legal

::: ghid-temei
„Factura electronică se transmite de către emitent în sistemul naţional privind factura electronică RO e-Factura." — OUG nr. 120/2021, art. 4 alin. (3).
:::

## Cum funcționează, de fapt

iConta e ea însăși aplicația în care emiți facturile — nu există, la acest moment, un conector care să preia facturi dintr-un program de gestiune extern și să le sincronizeze automat cu e-Factura. Legătura cu SPV e directă: fiecare firmă (prin cabinetul care o administrează) autorizează accesul cu propriul certificat digital calificat, iar iConta se conectează la serviciile ANAF (upload, urmărire stare, descărcare) prin acest canal.

Modelul e **per cabinet, nu per firmă**: un singur token acoperă toate CIF-urile pe care certificatul cabinetului are drept declarat în SPV, dar dreptul concret pe fiecare CIF se verifică separat, la fiecare trimitere.

## Ce e automatizat în această conexiune

- **Reîmprospătarea tokenului** — zilnic, fără intervenție.
- **Urmărirea stării facturilor trimise** — la fiecare 30 de minute, recipisă sau eroare.
- **Descărcarea facturilor primite de la furnizori** — tot la 30 de minute, cu verificare de firmă și deduplicare.

Trimiterea inițială a unei facturi emise **nu** face parte din automatizări — se declanșează manual, per factură, prin butonul „Trimite în SPV".

## Ce nu există

Nu există, documentat sau construit, un modul de import/export care să sincronizeze facturile cu un program de gestiune terț (stoc, comenzi, alt soft de facturare). Dacă lucrezi cu un program de gestiune separat pentru stocuri sau vânzări, facturile emise trebuie introduse (sau reintroduse) direct în iConta pentru a putea fi transmise prin e-Factura — nu se preiau automat de acolo.

## Ce se greșește în practică

- Se caută un ecran de „integrare cu programul de gestiune" așteptând o sincronizare automată de date — arhitectura actuală nu are acest tip de conector.
- Se presupune că, pentru că iConta se conectează la SPV, se conectează implicit și la orice alt software folosit în firmă — legătura e strict cu ANAF, nu cu terți.
- Se dublează efortul introducând aceleași facturi în două sisteme fără un flux clar despre care e sursa de adevăr pentru transmiterea prin e-Factura.

## Ce face iConta.eu

Funcționează ca aplicație unică de facturare și contabilitate, conectată direct la SPV prin OAuth per cabinet — fără un strat separat de sincronizare cu un program de gestiune extern. Dacă ai nevoie de o astfel de integrare pentru fluxul tău actual, spunem clar: nu e o funcționalitate disponibilă azi, nu o funcționalitate ascunsă undeva în meniu.

[iConta.eu](/)
