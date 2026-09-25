---
title: "Locul prestării serviciilor către persoane fizice din UE"
description: "Pentru servicii prestate unor persoane neimpozabile (B2C) din alt stat membru, regula generală e locul unde e stabilit prestatorul — cu o listă lungă de excepții pentru servicii specifice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Locul prestării serviciilor către persoane fizice din UE

Regula B2C e inversul celei B2B: la servicii prestate către o persoană impozabilă, locul e la beneficiar; la servicii prestate către o persoană fizică (neimpozabilă), regula generală rămâne la prestator — dar excepțiile de la această regulă sunt numeroase și afectează exact tipurile de servicii cel mai des vândute online sau la distanță.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană neimpozabilă este locul unde prestatorul își are stabilit sediul activității sale economice. Dacă serviciile sunt prestate de la un sediu fix al prestatorului, aflat în alt loc decât locul în care persoana impozabilă și-a stabilit sediul activității economice, locul de prestare a serviciilor este locul unde se află respectivul sediu fix. În absența unui astfel de loc sau sediu fix, locul de prestare a serviciilor este locul unde prestatorul își are domiciliul stabil sau reședința obișnuită."
— Codul fiscal (Legea 227/2015), art. 278 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie verificat înainte de a aplica regula generală:

- Regula de bază: pentru un prestator stabilit în România care vinde servicii unei persoane fizice din alt stat membru, locul prestării rămâne România — se aplică TVA românesc, ca pentru orice client intern.
- Excepția cea mai importantă în practică: serviciile electronice, de telecomunicații și de radiodifuziune/televiziune prestate către persoane neimpozabile au locul la beneficiar (art. 278 alin. (5) lit. h)), nu la prestator — aici intervine regimul special OSS (One Stop Shop).
- Alte excepții relevante: serviciile legate de bunuri imobile (locul unde e situat imobilul), transportul de călători (proporțional cu distanțele), serviciile culturale/artistice/sportive (locul desfășurării efective) și închirierea mijloacelor de transport (reguli proprii, în funcție de durata închirierii).
- Pentru intermediarii care acționează în numele și contul altei persoane, când beneficiarul e o persoană neimpozabilă, locul e cel al operațiunii principale intermediate (art. 278 alin. (5) lit. a)), nu locul prestatorului intermediar.

## Ce se greșește în practică

- Se aplică automat regula generală (TVA la locul prestatorului) pentru toate serviciile B2C, ignorând excepțiile numeroase de la art. 278 alin. (4) și (5) — cele mai frecvente greșeli apar la servicii electronice și la închirierea de bunuri mobile sau mijloace de transport.
- Se tratează un client B2C ca B2B doar pentru că a comunicat un cod de TVA — dacă acel cod nu e valid sau persoana nu acționează ca persoană impozabilă, aplicarea regulii B2B e greșită.
- Se ignoră regimul special OSS pentru serviciile electronice prestate către persoane neimpozabile din UE, declarând TVA românesc peste tot, deși obligația reală e de declarare la locul beneficiarului.

## Ce face iConta.eu

`core/intracomunitar.py`, modulul de operațiuni intracomunitare al iConta.eu, implementează explicit regula B2B pentru prestări de servicii (`valideaza_prestare_ic`, conform art. 278 alin. (2)) — locul la beneficiarul persoană impozabilă din alt stat membru, cu verificare VIES a codului de TVA. Funcția respinge explicit cazul unui cod de TVA invalid, semnalând că operațiunea trece în regim B2C, cu TVA românesc conform art. 278 alin. (3).

Aplicația nu are însă un modul dedicat regulilor speciale B2C (servicii electronice și regimul OSS, servicii legate de imobile, transport de călători, închiriere mijloace de transport) — pentru aceste excepții de la regula generală, încadrarea corectă a operațiunii rămâne o evaluare manuală a contabilului.

[iConta.eu](/)
