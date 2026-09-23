---
title: "Ce fac dacă un cod de TVA nu apare valid în VIES?"
description: "Invalid" și "indisponibil" nu înseamnă același lucru în VIES — un cod invalid schimbă tratamentul fiscal al operațiunii, în timp ce o eroare temporară a serviciului nu spune nimic despre valabilitatea reală a codului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă un cod de TVA nu apare valid în VIES?

Prima distincție de făcut: sistemul poate răspunde „cod invalid" sau poate pur și simplu să nu răspundă la timp („serviciu indisponibil"). Cele două situații cer reacții diferite, iar confundarea lor duce fie la tratamente fiscale greșite, fie la blocaje inutile.

## Temeiul legal

::: ghid-temei
Scutirea LIC cu drept de deducere are condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt stat membru (CF art. 294 alin. 2 lit. a); simetric, la serviciile B2B intracomunitare, prezența unui client non-RO cu cod valid VIES face operațiunea neimpozabilă în România, declarată în D390 (S), iar lipsa unui cod valid o tratează ca B2C, facturată cu TVA românesc (CF art. 278 alin. 2-3) — verificat în dosarul F050, sursă `cod_fiscal_227_2015_consolidat.txt` L18397+ și L17303+.
:::

Dacă e vorba despre codul unui **client**, la o livrare/prestare intracomunitară: fără un cod valid VIES, condiția de fond a scutirii (art. 294 alin. 2 lit. a) sau a neimpozabilității în România (art. 278 alin. 2-3, pentru servicii) nu e îndeplinită — operațiunea se tratează, după caz, ca vânzare cu TVA românesc (B2C, la servicii) sau nu poate beneficia de scutirea LIC, până la obținerea unui cod valid.

## Ce se greșește în practică

- Se tratează un mesaj „VIES indisponibil" (eroare temporară de sistem) la fel ca „cod invalid" — anulând greșit o scutire care, de fapt, ar fi justificată, doar că verificarea nu a putut fi confirmată în acel moment.
- Se ignoră un cod marcat invalid și se facturează oricum fără TVA, fără nicio altă dovadă care să justifice scutirea.
- Se renunță definitiv la operațiune la primul „invalid", fără să se ia legătura cu partenerul — un cod poate fi introdus greșit (eroare de tastare) sau poate fi în curs de reînregistrare.

## Ce face iConta.eu

La emiterea unei facturi, sistemul afișează distinct starea codului verificat în VIES — „valid", „invalid" sau avertismentul specific „VIES indisponibil" atunci când serviciul european nu răspunde în timp util — astfel încât utilizatorul știe exact dacă trebuie să reia verificarea mai târziu (indisponibil) sau să reconsidere tratamentul fiscal al operațiunii (invalid). Prefixul de țară e validat separat de interogarea propriu-zisă, cu erori distincte pentru cod absent, prefix nevalid sau prefix fără număr asociat — deci mesajul primit indică exact ce anume nu e în regulă cu codul introdus, înainte chiar de a ajunge la interogarea VIES.

[iConta.eu](/)
