---
title: "Cum încep facturarea electronică pentru un SRL nou?"
description: Trei pași reali, în ordine: autorizarea certificatului cabinetului în SPV, fereastra de 24 de ore de așteptare, apoi prima factură prin fluxul obișnuit de validare și trimitere — obligatoriu din prima zi de activitate B2B.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum încep facturarea electronică pentru un SRL nou?

Pentru un SRL nou-înființat, obligația de RO e-Factura există din prima factură emisă către un alt operator economic din România — nu există o perioadă de grație pentru firmele noi. Ce trebuie pregătit înainte de prima factură, mai jos.

## Temeiul legal

::: ghid-temei
**OMFP nr. 660/2017** stabilește calitățile care dau acces la Spațiul Privat Virtual: „a) reprezentant legal ...; b) reprezentant desemnat ...", plus calitatea de împuternicit. Autorizarea acestor calități „se face prin intermediul aplicaţiilor informatice" puse la dispoziție de ANAF.

„În relaţia comercială B2B, între persoane impozabile stabilite în România ... emitentul facturii electronice are obligaţia de transmitere a acesteia către destinatar utilizând sistemul naţional privind factura electronică RO e-Factura." — OUG nr. 120/2021, art. 10 alin. (1), forma modificată prin Legea nr. 296/2023, art. LXV pct. 4.
:::

## Pasul 1: autorizarea accesului la SPV

Accesul la e-Factura nu e o setare din iConta — e o autorizare care se face în Spațiul Privat Virtual, cu certificatul digital calificat al cabinetului, o singură dată per certificat. Autorizarea o poate face reprezentantul legal al firmei, un reprezentant desemnat sau un împuternicit.

iConta e o aplicație înrolată la ANAF cu un Client ID/Secret propriu, dar nu deține niciun certificat — fiecare cabinet autorizează cu al lui, iar nomenclatorul de servicii activat la înrolare acoperă doar e-Factura și e-Transport (mesajele SPV, rapoartele și alte declarații rămân pe un canal separat, nedisponibil momentan).

Accesul se dă **per cabinet**, nu per firmă: dacă administrezi mai multe firme prin același cabinet, nu repeți autorizarea pentru fiecare — dar dreptul concret pe fiecare CIF se verifică separat, la prima trimitere reală pentru firma respectivă.

## Pasul 2: cele 24 de ore de așteptare

După înrolarea certificatului cabinetului în SPV, accesul nu devine funcțional instantaneu — trebuie așteptate circa 24 de ore până când e recunoscut de serverele ANAF. Nu e o regulă scrisă într-un act normativ, ci un comportament observat constant al sistemului. Dacă imediat după înrolare o primă încercare de trimitere eșuează cu eroare de acces, nu înseamnă neapărat că autorizarea a picat — poate fi doar fereastra de propagare.

## Pasul 3: prima factură

De aici înainte, fluxul e identic pentru orice factură: generare cu datele complete ale clientului, validare la validatorul public ANAF, verificare că nu există deja o trimitere activă, upload. Firma trebuie să transmită fiecare factură emisă către o altă persoană impozabilă din România în termen de 5 zile lucrătoare de la emitere (din 1 ianuarie 2026) — nu există prag de valoare sau de vechime a firmei care să scutească de această obligație.

## Ce se greșește în practică

- Se emite și se trimit facturi imediat după înființarea firmei, fără autorizarea prealabilă a certificatului în SPV — trimiterea eșuează la primul pas (token lipsă).
- Se confundă înrolarea aplicației (făcută de iConta, o singură dată, la nivel de platformă) cu autorizarea cabinetului (făcută de fiecare firmă, cu propriul certificat) — a doua lipsește cel mai des la firmele noi.
- Se renunță la prima încercare, la primul eșec, fără să se ia în calcul fereastra de 24 de ore de după înrolare.

## Ce face iConta.eu

Un singur ecran de conectare la ANAF, per cabinet — configurat o singură dată, verificat apoi automat pe fiecare CIF nou adăugat. De la prima factură, aceleași verificări rulează indiferent de vechimea firmei: validare de structură înainte de orice upload, protecție împotriva trimiterii duble, semafor de stare vizibil pentru fiecare document.

[iConta.eu](/)
