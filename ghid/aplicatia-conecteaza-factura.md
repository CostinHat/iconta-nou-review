---
title: "Ce fac dacă aplicația nu se mai conectează la e-Factura?"
description: Nu orice eroare de conectare la SPV e din aceeași cauză. Explicăm cele trei situații distincte — conexiune nefinalizată, conexiune expirată/revocată și lipsă drept SPV pe un CIF — și de ce lipsa dreptului nu apare mereu ca eroare „clasică".
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă aplicația nu se mai conectează la e-Factura?

„Nu se mai conectează" poate însemna trei lucruri diferite, cu soluții diferite. Confuzia cea mai costisitoare e să tratezi toate cele trei ca fiind aceeași problemă — mai ales pentru că una dintre ele nu se anunță deloc ca o „eroare" în sensul obișnuit.

## Temeiul legal

::: ghid-temei
„SPV este accesibil persoanei juridice sau entității fără personalitate juridică prin reprezentat legal, prin reprezentant desemnat sau prin împuternicit." — OMFP nr. 660/2017 privind aprobarea Procedurii de comunicare prin mijloace electronice de transmitere la distanță, art. 23 alin. (2)
:::

Multe blocaje de conectare nu sunt, de fapt, probleme tehnice ale aplicației de facturare, ci lipsa dreptului efectiv de acces la SPV pe CIF-ul respectiv — drept care se acordă și se verifică la ANAF, conform procedurii din OMFP 660/2017, nu în aplicația de facturare.

## Cele trei cauze reale

**1. Conexiunea nu a fost niciodată finalizată.** Dacă autorizarea SPV nu s-a dus până la capăt (de exemplu contabilul a abandonat fluxul înainte de a alege certificatul, sau sesiunea de autorizare a expirat pentru că a durat prea mult), aplicația nu are niciun acces activ — orice încercare de a transmite ceva eșuează cu un mesaj clar de „neconectat". Soluția: reia fluxul de autorizare de la zero.

**2. Conexiunea a expirat sau a fost revocată.** Accesul acordat unei aplicații are o durată limitată și se reînnoiește automat, în fundal, cât timp e activ. Dacă reînnoirea eșuează (de exemplu certificatul a expirat între timp, sau dreptul a fost revocat la ANAF), conexiunea devine inactivă și trebuie refăcută manual — la fel ca la o primă conectare.

**3. Lipsă drept SPV pe un CIF anume — capcana de interpretare.** Aici e diferența cea mai importantă: dacă certificatul contabilului este conectat corect la SPV, dar **nu are drept** pe CIF-ul unei firme anume (de exemplu firma nu a fost încă înregistrată cu împuternicire la ANAF pe acel certificat), acest lucru nu vine, în mod obișnuit, ca un cod de eroare „clasic" de tip acces refuzat. Vine ca un răspuns aparent normal, cu un mesaj explicit în conținut care spune că nu există drept pentru CIF-ul respectiv. Cine caută doar un cod de „acces interzis" ca semn că firma nu e împuternicită riscă să treacă pe lângă exact acest mesaj, crezând că cererea „a mers".

## Ce se greșește în practică

- Se presupune că orice blocaj de conectare înseamnă „certificat expirat" și se reface autorizarea, fără să se verifice mai întâi dacă, de fapt, conexiunea e activă, dar lipsește dreptul pe CIF-ul respectiv — problemă care nu se rezolvă prin reautorizare, ci prin obținerea dreptului la ANAF.
- Se caută strict un cod de eroare „de tip acces interzis" ca semn al lipsei dreptului pe CIF — mesajul relevant poate apărea altfel, în conținutul răspunsului, nu neapărat ca un cod distinct de refuz de acces.
- Se ignoră mesajul explicit al aplicației despre lipsa dreptului, presupunând că e o eroare temporară de sistem care „se rezolvă singură" — lipsa dreptului pe CIF nu se rezolvă prin reîncercare, ci printr-o procedură la ANAF (împuternicire, conform OMFP 660/2017 art. 15-17).

## Ce face iConta.eu

Toate cererile către ANAF trec printr-un singur mecanism intern, care distinge explicit cele trei situații: lipsă conexiune activă, expirare/eșec de reînnoire și lipsă drept pe un CIF anume (citită din conținutul răspunsului ANAF, nu presupusă). Pentru primele două, soluția arătată contabilului e reluarea autorizării SPV. Pentru a treia, aplicația nu poate „rezolva" ea însăși problema — dreptul pe CIF se obține la ANAF, conform procedurii de împuternicire/desemnare. Rezervă onestă: mecanismul e verificat cap-coadă în producție, dar cu certificatul administratorului platformei, care nu are drept SPV pe firme reale — comportamentul exact pe un cabinet real, cu un CIF cu drept efectiv, rămâne de confirmat cazuistic.

[iConta.eu](/)
