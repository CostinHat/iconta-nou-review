---
title: "Ce fac dacă un cod de TVA nu apare valid în VIES?"
description: "Invalid" și "indisponibil" nu înseamnă același lucru în VIES — un cod invalid schimbă tratamentul fiscal al operațiunii, în timp ce o eroare temporară a serviciului nu spune nimic despre valabilitatea reală a codului.
published: 2026-09-25
modified: 2026-10-13
poarta: v1
---

# Ce fac dacă un cod de TVA nu apare valid în VIES?

Prima distincție de făcut: sistemul poate răspunde „cod invalid" sau poate pur și simplu să nu răspundă la timp („serviciu indisponibil"). Cele două situații cer reacții diferite, iar confundarea lor duce fie la tratamente fiscale greșite, fie la blocaje inutile.

## Temeiul legal

::: ghid-temei
„Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru [...]”
— Codul fiscal (Legea 227/2015), art. 294 alin. (2) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice.”
— Codul fiscal (Legea 227/2015), art. 278 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Locul de prestare a serviciilor către o persoană neimpozabilă este locul unde prestatorul își are stabilit sediul activității sale economice.”
— Codul fiscal (Legea 227/2015), art. 278 alin. (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Dacă e vorba despre codul unui **client**, la o livrare/prestare intracomunitară: fără un cod valid VIES, condiția de fond a scutirii (art. 294 alin. 2 lit. a) sau a neimpozabilității în România (art. 278 alin. 2-3, pentru servicii) nu e îndeplinită — operațiunea se tratează, după caz, ca vânzare cu TVA românesc (B2C, la servicii) sau nu poate beneficia de scutirea LIC, până la obținerea unui cod valid.

## Ce se greșește în practică

- Se tratează un mesaj „VIES indisponibil" (eroare temporară de sistem) la fel ca „cod invalid" — anulând greșit o scutire care, de fapt, ar fi justificată, doar că verificarea nu a putut fi confirmată în acel moment.
- Se ignoră un cod marcat invalid și se facturează oricum fără TVA, fără nicio altă dovadă care să justifice scutirea.
- Se renunță definitiv la operațiune la primul „invalid", fără să se ia legătura cu partenerul — un cod poate fi introdus greșit (eroare de tastare) sau poate fi în curs de reînregistrare.

## Ce face iConta.eu

La emiterea unei facturi, sistemul afișează distinct starea codului verificat în VIES — „valid", „invalid" sau avertismentul specific „VIES indisponibil" atunci când serviciul european nu răspunde în timp util — astfel încât utilizatorul știe exact dacă trebuie să reia verificarea mai târziu (indisponibil) sau să reconsidere tratamentul fiscal al operațiunii (invalid). Prefixul de țară e validat separat de interogarea propriu-zisă, cu erori distincte pentru cod absent, prefix nevalid sau prefix fără număr asociat — deci mesajul primit indică exact ce anume nu e în regulă cu codul introdus, înainte chiar de a ajunge la interogarea VIES.

[iConta.eu](/)
