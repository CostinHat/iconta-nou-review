---
title: "Se facturează cu TVA serviciile software către firme din UE?"
description: "Când o factură de servicii software către o firmă din UE se emite fără TVA și când, dimpotrivă, trebuie facturată cu TVA românesc."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se facturează cu TVA serviciile software către firme din UE?

Răspunsul scurt: depinde exclusiv de statutul clientului, nu de tipul exact de serviciu software. Regula e cea generală pentru serviciile B2B intracomunitare.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

Dacă firma-client are un cod de TVA valid, verificat în VIES, într-un alt stat membru UE, serviciul software (dezvoltare, licențiere de soft custom, mentenanță, suport) se facturează **fără TVA românesc** — locul prestării e considerat, legal, la beneficiar, iar impozitarea revine statului lui.

Dacă firma-client NU are un cod de TVA valid în VIES — fie pentru că e persoană fizică, fie pentru că nu e (încă) înregistrată în scopuri de TVA — operațiunea nu mai poate fi tratată ca B2B intracomunitară: devine, practic, o vânzare care se facturează **cu TVA românesc**, la fel ca la un client din România.

## Ce se greșește în practică

- Se emite fără TVA orice factură către o firmă „din UE”, fără să se verifice dacă acel client are efectiv cod de TVA valid în VIES.
- Se confundă acest regim (servicii B2B, art. 278 alin. 2) cu regulile specifice serviciilor electronice către consumatori persoane fizice (B2C, altă temă, neacoperită aici).
- Se aplică scutirea o singură dată, la prima factură, și apoi „din inerție” la toate facturile ulterioare, fără reverificare VIES.

## Ce face iConta.eu

La emiterea unei facturi cu un cod de TVA de prefix non-RO, iConta verifică automat, live, în VIES starea codului (valid/invalid) și afișează rezultatul în ecranul de emitere; dacă VIES e temporar indisponibil, afișează un avertisment explicit.

Formularul de vânzare intracomunitară (`vanzare_ic`) validează neimpozabilitatea pe baza a două condiții: client non-RO + cod valid VIES. Dacă oricare lipsește, tratamentul corect e facturarea cu TVA — nu scutirea „din oficiu”. Operațiunea validă se clasifică automat pentru D390, cod P (servicii prestate).

[iConta.eu](/)
