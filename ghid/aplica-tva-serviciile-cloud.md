---
title: "Cum se aplică TVA la serviciile cloud"
description: "Regulile de loc al prestării pentru serviciile cloud, diferite pentru clienți persoane impozabile (B2B, taxare inversă) și persoane neimpozabile (B2C, locul beneficiarului peste prag)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se aplică TVA la serviciile cloud

Serviciile cloud (hosting, stocare, SaaS, procesare de date) sunt „servicii furnizate pe cale electronică" din perspectiva TVA, iar locul lor de prestare — deci statul care are dreptul la TVA — depinde în primul rând de cine e clientul: o firmă (B2B) sau o persoană fizică (B2C).

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...] Prin excepție de la prevederile [...] (3), locul următoarelor servicii este considerat a fi: [...] h) locul unde beneficiarul este stabilit, își are domiciliul stabil sau reședința obișnuită, în cazul următoarelor servicii prestate către o persoană neimpozabilă: [...] 3. serviciile furnizate pe cale electronică."
— Legea 227/2015, art. 278 alin. (2) și alin. (5) lit. h) pct. 3 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele două situații, tratate diferit:

- **Client persoană impozabilă (B2B)**: locul prestării e la sediul beneficiarului (art. 278 alin. (2)) — dacă firma din România vinde servicii cloud unei firme din alt stat UE, factura se emite fără TVA românesc, cu mențiunea „taxare inversă", clientul fiind cel care datorează TVA în statul lui. Simetric, când firma din România **cumpără** servicii cloud de la un furnizor stabilit în alt stat, ea datorează TVA prin taxare inversă (art. 307 alin. (2)).
- **Client persoană neimpozabilă (B2C), din UE**: regula implicită mută locul prestării la statul clientului (art. 278 alin. (5) lit. h) pct. 3), dar excepția de la art. 278^1 „împinge" locul înapoi la România atât timp cât vânzările B2C intracomunitare cumulate (servicii electronice + vânzări la distanță de bunuri) rămân sub pragul de 10.000 euro pe an.
- **Client persoană neimpozabilă, din afara UE**: nu se aplică TVA românesc — locul prestării iese de sub incidența TVA românesc, de regulă impozitarea revenind statului de reședință al clientului, conform legislației locale a acestuia.
- Pentru clientul B2B, obligația de a verifica statutul de persoană impozabilă (de regulă prin codul de TVA valid, verificabil VIES) revine prestatorului, care altfel riscă să aplice greșit taxarea inversă unui client care nu era, de fapt, persoană impozabilă înregistrată.

## Ce se greșește în practică

- Se aplică taxare inversă automat pe orice factură emisă către un client din UE, fără verificarea prealabilă a codului de TVA al clientului (VIES) — dacă acesta nu e persoană impozabilă valid înregistrată, operațiunea trebuie tratată ca B2C, nu B2B.
- Se omite colectarea TVA pentru achizițiile de servicii cloud de la furnizori din afara UE (nu doar din UE), presupunând că taxarea inversă se aplică doar între state membre — regula de la art. 278 alin. (2) și art. 307 alin. (2) nu face distincție geografică, ci de statut al furnizorului (stabilit sau nu în România).
- Se ignoră pragul de 10.000 euro pentru vânzările B2C de servicii cloud/SaaS către persoane fizice din UE, aplicând TVA românesc peste prag, deși locul prestării ar fi trecut la statul clientului.

## Ce face iConta.eu

Pentru achizițiile de servicii cloud de la furnizori nestabiliți în România, iConta.eu aplică taxarea inversă (4426=4427, sau TVA nedeductibilă dar datorată pentru firmele înregistrate doar conform art. 317). Aplicația poate verifica, la cerere, validitatea codului de TVA al unui partener direct în VIES (serviciul oficial al Comisiei Europene), ceea ce ajută la confirmarea statutului de persoană impozabilă înainte de a factura B2B. Ce nu face automat este urmărirea cumulată a pragului de 10.000 euro pentru vânzările proprii de servicii cloud/SaaS către persoane fizice din UE — verificarea VIES e o acțiune punctuală, per partener, nu o regulă aplicată automat la fiecare factură, iar plafonul B2C rămâne o evidență ținută de contabil.

[iConta.eu](/)
