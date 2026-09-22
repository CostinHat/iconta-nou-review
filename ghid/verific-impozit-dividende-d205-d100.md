---
title: Cum verific impozitul pe dividende din D205 cu D100?
description: Verificarea D205 cu D100 nu are sens fiscal — D100 nu conține deloc impozitul pe dividende; verificarea reală a corectitudinii impozitului se face prin recalcul independent din contabilitate, nu prin comparație între declarații.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum verific impozitul pe dividende din D205 cu D100?

Este firesc să vrei o a doua confirmare pentru o sumă declarată la ANAF, iar D100 e prima declarație la care te gândești, pentru că e cea mai frecventă și cuprinde majoritatea obligațiilor curente ale firmei. Pentru impozitul pe dividende, însă, această verificare nu are corespondent — explicăm mai jos de ce, și cum se verifică de fapt corectitudinea impozitului din D205.

## Temeiul legal

::: ghid-temei
„Declaraţia se completează şi se depune de către plătitorii de venituri care au obligaţia calculării, reţinerii şi virării impozitului pe veniturile cu regim de reţinere la sursă a impozitului... pentru următoarele tipuri de venituri: a) venituri din dividende..." (OPANAF 179/2022, I.1, l.217-231)

„Cap. V «Date informative privind impozitul pe veniturile din dividende» se completează de către plătitorii de venituri din dividende, pentru fiecare persoană fizică beneficiară." (OPANAF 179/2022, Secțiunea V dividende, l.381-397)
:::

## De ce D100 nu ajută la verificare

D100 raportează obligațiile fiscale curente ale firmei — de exemplu impozitul pe veniturile microîntreprinderilor sau impozitul pe profit trimestrial. Impozitul reținut la sursă din dividende **nu are un cod de obligație propriu în D100** — pur și simplu nu apare acolo ca linie distinctă. O comparație „suma din D205 trebuie să se regăsească undeva în D100" nu are deci la ce sumă din D100 să se raporteze: acea sumă nu există în structura declarației.

Verificarea corectă a impozitului pe dividende din D205 se face altfel: prin recalcularea independentă a bazei și a impozitului per beneficiar, direct din mișcările contabile ale distribuirii și plății dividendelor, și confruntarea acestui recalcul cu ce a produs generarea automată.

## Ce se greșește în practică

- Se caută în D100 o sumă egală cu totalul impozitului din D205 — sumă care nu are unde să apară în D100.
- Se amână depunerea D205 „până se lămurește" diferența față de D100, deși nu există nicio diferență de verificat între cele două.
- Se ignoră faptul că impozitul pe dividende se verifică prin recalcul din contabilitate (contul care ține evidența distribuirii/plății), nu prin comparație cu altă declarație.
- Se presupune că o eventuală eroare în D205 s-ar vedea și în D100 — de fapt D100 nu ar semnala nimic, indiferent de eroarea din D205.

## Ce face iConta.eu

Pentru a verifica intern corectitudinea D205, aplicația folosește o a doua cale de calcul, complet independentă de motorul principal de generare: recalculează separat, din mișcările contabile ale distribuirii/plății de dividende, baza și impozitul pentru fiecare beneficiar, folosind aceeași formulă de potrivire cronologică a plăților cu distribuirile. Dacă acest recalcul independent diverge de rezultatul generat automat, generarea declarației este blocată. Această verificare **nu** implică D100, în mod explicit: pentru că D100 nu conține deloc impozitul pe dividende, o comparație D205↔D100 ar citi practic aceeași sursă de date de două ori, fără să valideze nimic suplimentar față de verificarea internă deja existentă.

[iConta.eu](/)
