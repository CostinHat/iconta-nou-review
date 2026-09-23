---
title: "Cum verific dacă un furnizor din UE are cod valid de TVA?"
description: Codul de TVA al unui furnizor din alt stat membru se verifică în VIES, sistemul oficial al Comisiei Europene — nu prin simpla existență a firmei într-un registru comercial — pentru că valabilitatea contează la data operațiunii, nu o singură dată, la începutul relației comerciale.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific dacă un furnizor din UE are cod valid de TVA?

Un cod de TVA poate fi valid pentru operațiuni interne în statul de origine al furnizorului și, în același timp, invalid pentru operațiuni intracomunitare — cele două înregistrări sunt distincte. Singura sursă oficială care confirmă valabilitatea pentru operațiuni intracomunitare este VIES (sistemul de schimb de informații privind TVA al Comisiei Europene).

## Temeiul legal

::: ghid-temei
Scutirea LIC cu drept de deducere are condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt stat membru (CF art. 294 alin. 2 lit. a); simetric, la serviciile B2B intracomunitare, prezența unui client non-RO cu cod valid VIES face operațiunea neimpozabilă în România, declarată în D390 (S), iar lipsa unui cod valid o tratează ca B2C, facturată cu TVA românesc (CF art. 278 alin. 2-3) — verificat în dosarul F050, sursă `cod_fiscal_227_2015_consolidat.txt` L18397+ și L17303+.
:::

Deși citatul de mai sus descrie condițiile scutirii la vânzare (LIC), principiul e simetric și la achiziție: codul de TVA valid al partenerului e o condiție de fond a tratamentului corect al operațiunii, iar VIES e mecanismul oficial de confirmare a acelei valabilități — pentru orice direcție a operațiunii, cumpărare sau vânzare.

## Cum funcționează verificarea

Un cod de TVA intracomunitar e format dintr-un prefix de țară și un număr — de exemplu „DE123456789". Prefixul trebuie să corespundă uneia dintre țările UE recunoscute pentru VIES (cele 27 state membre, plus „XI" pentru Irlanda de Nord, regim post-Brexit); Grecia e un caz special, prefixul oficial e „EL", nu „GR", deși „GR" apare frecvent informal. Interogarea propriu-zisă se face prin serviciul REST oficial VIES al Comisiei Europene, pe codul de țară și numărul separate de prefix, și întoarce dacă acel cod e valid, plus numele și adresa firmei asociate, când statul membru le publică.

## Ce se greșește în practică

- Se verifică doar existența firmei furnizoare (de exemplu printr-un registru comercial local), nu și validitatea specifică VIES a codului ei de TVA.
- Se face o singură verificare, la începutul relației comerciale, fără reluare periodică — un cod valid azi poate fi anulat peste câteva luni, iar validitatea contează la data operațiunii, nu la data primei verificări.

## Ce face iConta.eu

La emiterea unei facturi către un client cu cod de TVA de prefix non-românesc, sistemul verifică automat starea codului direct în VIES și afișează rezultatul (valid/invalid) sau avertismentul „VIES indisponibil" dacă serviciul european nu răspunde la timp — acest comportament automat e confirmat explicit pentru ecranul de emitere a facturilor.

Pentru verificarea unui furnizor, la introducerea unei achiziții intracomunitare, motorul de validare a codului (separarea prefixului de țară + interogarea directă VIES, cu aceeași normalizare pentru Grecia „GR"→"EL") e același mecanism — dar cercetarea acestui dosar nu a găsit o confirmare explicită a unui apel automat similar pe ecranul de achiziție. Recomandarea practică: verificați manual codul furnizorului în VIES înainte de a înregistra achiziția, mai ales dacă e o relație comercială nouă sau dacă a trecut mult timp de la ultima verificare.

[iConta.eu](/)
