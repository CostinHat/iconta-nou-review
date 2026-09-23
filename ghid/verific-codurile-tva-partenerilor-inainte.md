---
title: "Cum verific codurile TVA ale partenerilor înainte de depunerea D390?"
description: "De ce verificarea VIES (nu registrul ANAF de CUI-uri) este obligatorie pentru fiecare partener intracomunitar înainte de a depune D390."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific codurile TVA ale partenerilor înainte de depunerea D390?

Orice operațiune intracomunitară — achiziție sau livrare de bunuri, prestare sau achiziție de servicii B2B — depinde de un singur lucru verificabil obiectiv: codul de TVA al partenerului este valid, la data operațiunii, în sistemul **VIES**.

## Temeiul legal

::: ghid-temei
CF art. 294 alin. (2) lit. a): „Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” (sursă: `intracomunitar.py`, docstring)

CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420)
:::

VIES (registrul de schimb de informații privind TVA la nivel UE) e sursa oficială de verificare — nu un registru local de CUI-uri, nu o simplă declarație a partenerului. Practic, verificarea unui cod de TVA presupune două etape: (1) separarea prefixului de țară de restul codului (de exemplu „DE123456789” → țara DE, numărul 123456789), cu o atenție specială pentru Grecia, al cărei prefix real în VIES este „EL”, nu „GR”; și (2) interogarea efectivă a VIES pentru acel cod, la acea dată.

Rezultatul verificării — valid/invalid, plus numele și adresa asociate codului — condiționează direct tratamentul TVA al operațiunii: fără cod valid VIES, o livrare de bunuri sau o prestare de servicii nu poate fi tratată ca neimpozabilă/scutită, indiferent de alte documente.

## Ce se greșește în practică

- Se verifică codul de TVA o singură dată, la începutul relației comerciale, și nu se mai reverifică la fiecare factură — codul poate fi anulat între timp.
- Se confundă un CUI/CIF valid din registrul comerțului local al altui stat cu un cod de TVA valid în VIES — sunt lucruri diferite.
- Se aplică scutirea/neimpozitarea pe baza codului comunicat de client, fără o verificare independentă în VIES.

## Ce face iConta.eu

La emiterea unei facturi cu un cod de TVA de prefix non-RO, aplicația verifică automat, live, în VIES starea codului și afișează rezultatul (valid/invalid) direct în ecranul de emitere; dacă serviciul VIES e temporar indisponibil, afișează un avertisment explicit „VIES indisponibil”, în loc să presupună tacit că e valid.

Motorul intern separă mai întâi prefixul de țară de restul codului, validează prefixul contra listei celor 27 de state membre plus „XI” (Irlanda de Nord, post-Brexit) și normalizează cazuri speciale precum Grecia (GR→EL). Rezultatul verificării alimentează direct validările din formularele de achiziție (`achizitie_ic`) și vânzare (`vanzare_ic`) intracomunitară, precum și clasificarea pentru D390.

[iConta.eu](/)
