---
title: Cum verific codul de TVA al clientului UE pentru scutire
description: Codul se desparte în prefix de țară și număr, prefixul se validează contra statelor membre, iar restul se interoghează live în VIES; rezultatul — valid sau invalid — decide dacă livrarea se poate factura scutită de TVA.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific codul de TVA al clientului UE pentru scutire

Scutirea de TVA la livrarea intracomunitară depinde de un singur lucru verificabil obiectiv: dacă, la data operațiunii, clientul avea cod de TVA valid pentru operațiuni intracomunitare. Verificarea are doi pași distincți — validarea formei codului, apoi confirmarea lui reală în VIES.

## Temeiul legal

::: ghid-temei
„Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” — CF art. 294 alin. (2) lit. a) (sursă: `cod_fiscal_227_2015_consolidat.txt`, L18397+, verificat în dosarul F050).
:::

## Pasul 1 — forma codului

Codul de TVA intracomunitar are un prefix de țară urmat de un număr — „DE123456789”, „FR40303265045”. Prefixul trebuie să corespundă unui stat membru UE recunoscut pentru VIES: cele 27 de state, plus „XI” pentru Irlanda de Nord (regim post-Brexit). Grecia e cazul special: codul VIES real folosește prefixul „EL”, nu „GR”, deși „GR” circulă frecvent ca prescurtare informală a țării.

Un cod fără prefix recognoscibil, fără număr după prefix, sau complet absent, nu ajunge nici măcar la interogarea VIES — eroarea se vede din formă, înainte de orice verificare live.

## Pasul 2 — verificarea live în VIES

Codul cu formă corectă se interoghează în sistemul VIES al Comisiei Europene, care întoarce dacă e valid la momentul verificării și, când statul membru publică aceste date, numele și adresa firmei asociate. Un rezultat „invalid” sau o eroare de tip „serviciu indisponibil” înseamnă că scutirea nu poate fi susținută pe baza acelei verificări — și, dacă serviciul e indisponibil, verificarea trebuie reluată, nu presupusă favorabilă.

## Ce se greșește în practică

Verificarea codului o singură dată, la începutul relației comerciale, și nu la fiecare operațiune sau periodic — un cod valid azi poate fi anulat peste câteva luni, iar ce contează pentru scutire e validitatea **la data livrării**, nu la prima verificare făcută vreodată. A doua greșeală: tratarea unui răspuns „VIES indisponibil” ca „probabil valid” — un serviciu indisponibil nu confirmă nimic, iar dovada verificării nu există dacă rezultatul n-a putut fi obținut.

## Ce face iConta.eu

La emiterea facturii cu cod de TVA de prefix non-românesc, sistemul desparte automat prefixul de restul codului, îl validează contra listei statelor membre (cu normalizarea Grecia „GR”→„EL”), apoi interoghează live sistemul VIES oficial și afișează rezultatul — valid, invalid, sau avertismentul „VIES indisponibil” dacă serviciul european nu răspunde în timp util. Erorile de formă (cod absent, prefix nevalid, prefix fără număr) sunt distincte de eroarea de validitate — mesajul primit arată exact ce anume nu e în regulă.

[iConta.eu](/)
