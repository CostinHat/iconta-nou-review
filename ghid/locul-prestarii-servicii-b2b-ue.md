---
title: Locul prestării pentru servicii B2B în UE
description: Pentru un serviciu prestat unei firme dintr-un alt stat membru UE, locul prestării e la sediul beneficiarului (art. 278 alin. (2) Cod fiscal), condiție de bază pentru care legea cere un cod de TVA valabil, verificat de regulă prin VIES.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum stabilesc locul prestării pentru servicii B2B în UE?

Regula generală pentru serviciile prestate între firme (B2B) în UE nu e „unde stă prestatorul", ci „unde stă beneficiarul". Dacă vinzi consultanță, dezvoltare software sau alt serviciu unei firme dintr-un alt stat membru, locul prestării se mută la sediul clientului — ceea ce înseamnă că, de regulă, factura ta nu poartă TVA românesc, iar operațiunea se raportează ca prestare intracomunitară de servicii, nu ca vânzare internă.

## Temeiul legal

::: ghid-temei
**Art. 278 alin. (2) Cod fiscal** — regula generală pentru servicii B2B: *„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. Dacă serviciile sunt furnizate către un sediu fix al persoanei impozabile, aflat în alt loc decât cel în care persoana își are sediul activității sale economice, locul de prestare a serviciilor este locul unde se află respectivul sediu fix al persoanei care primește serviciile. În absența unui astfel de loc sau sediu fix, locul de prestare a serviciilor este locul unde persoana impozabilă care primește aceste servicii își are domiciliul stabil sau reședința obișnuită."*
:::

## Ce condiție trebuie îndeplinită

Ca operațiunea să fie tratată drept prestare intracomunitară neimpozabilă în România, trebuie îndeplinite două lucruri:

1. **Beneficiarul e stabilit în alt stat membru UE**, nu în România — verificat prin prefixul de țară al codului său de TVA.
2. **Beneficiarul are un cod de TVA valabil**, comunicat prestatorului.

Legea nu impune literal „verificare pe portalul VIES" ca obligație distinctă — cere ca beneficiarul să aibă „un cod valabil de înregistrare în scopuri de TVA". VIES (portalul UE de validare a codurilor de TVA, reglementat la nivel european prin cooperarea administrativă între statele membre) e mijlocul administrativ uzual și recomandat prin care se probează acest lucru, nu un termen distinct scris în Codul fiscal.

Dacă beneficiarul **nu** are un cod de TVA valabil comunicat, operațiunea nu se mai încadrează la regula B2B de mai sus, ci se tratează după regulile aplicabile persoanelor neimpozabile (locul prestării rămâne, în general, la sediul prestatorului) — o situație tratată separat, cu propriile condiții.

Spre deosebire de scutirea la livrarea de bunuri (LIC), prestarea de servicii **nu** cere dovadă de transport — firesc, pentru că un serviciu nu se transportă fizic dintr-un stat membru în altul.

## Ce se greșește în practică

- **Se aplică TVA românesc pe factura de servicii B2B intracomunitare**, din reflex, deși locul prestării e la sediul beneficiarului, nu la sediul prestatorului.
- **Se confundă „cod de TVA valabil" cu „verificare VIES" ca și cum ar fi aceeași obligație legală.** Legea cere codul valabil; VIES e modul uzual de a-l verifica, nu o cerință separată scrisă în Codul fiscal.
- **Se cere dovadă de transport pentru servicii**, împrumutată din regulile de la livrarea de bunuri — la servicii, condiția nu există, pentru că nu se transportă nimic fizic.

## Ce face iConta.eu

Codul de TVA al beneficiarului e analizat automat — prefixul de țară (cu mapare specială pentru Grecia, `GR → EL`) e verificat contra listei celor 27 de state membre UE plus `XI`; dacă prefixul lipsește sau nu e recunoscut, aplicația semnalează explicit eroarea, distingând „cod lipsă" de „prefix necunoscut". Operațiunea e tratată ca prestare intracomunitară doar dacă țara codului nu e România și codul e comunicat ca valabil; verificarea validității codului se face prin interogarea directă a serviciului oficial VIES.

[iConta.eu](/)
