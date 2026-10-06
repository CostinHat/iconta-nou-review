---
title: "Desființarea voluntară a grupului fiscal înainte de 5 ani: recalculare și accesorii"
description: "Dacă toți membrii cer desființarea grupului fiscal înainte de 5 ani, grupul încetează din anul următor. Fiecare membru își recalculează individual impozitul pe toată perioada, cu dobânzi și penalități."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Desființarea voluntară a grupului fiscal înainte de 5 ani: recalculare și accesorii

Dacă toți membrii grupului fiscal cer desființarea în cursul unui an, înainte să treacă cei 5 ani fiscali, grupul **se desființează începând cu anul fiscal următor**. Avantajul consolidării se anulează retroactiv. Fiecare membru își recalculează impozitul pe profit individual, pentru toată perioada în care s-a aplicat consolidarea, **cu dobânzi și penalități de întârziere**, potrivit Codului de procedură fiscală (Legea 207/2015).

Desființarea voluntară e deci scumpă. Pierderile unui membru, care au redus profitul altuia în consolidare, nu mai pot fi folosite așa. Diferențele de impozit devin datorate cu accesorii de la data aplicării sistemului.

## Temeiul legal

::: ghid-temei
„În cazul în care în mod voluntar toți membrii grupului fiscal solicită desființarea grupului în cursul unui an fiscal, înainte de expirarea perioadei de 5 ani fiscali, grupul fiscal se desființează începând cu anul fiscal următor. Fiecare membru al grupului calculează impozitul pe profit, în mod individual, pentru perioada în care s-a aplicat sistemul de consolidare prin recalcularea impozitului pe profit pe baza rezultatelor fiscale individuale, cu perceperea de creanțe fiscale accesorii stabilite potrivit Codului de procedură fiscală, după caz, de la data aplicării sistemului și până la începutul anului fiscal în care grupul se desființează."
— Codul fiscal (Legea 227/2015), art. 42^8 alin. (5) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„În mod corespunzător, și persoana juridică responsabilă recalculează impozitul pe profit datorat de grup cu perceperea de creanțe fiscale accesorii stabilite potrivit Codului de procedură fiscală, după caz, de la data aplicării sistemului și până la începutul anului fiscal în care grupul se desființează și are obligația depunerii declarației fiscale rectificative."
— Codul fiscal (Legea 227/2015), art. 42^8 alin. (5) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„Nivelul dobânzii este de 0,02% pentru fiecare zi de întârziere."
— Codul de procedură fiscală (Legea 207/2015), art. 174 alin. (5) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))

„Nivelul penalității de întârziere este de 0,01% pentru fiecare zi de întârziere."
— Codul de procedură fiscală (Legea 207/2015), art. 176 alin. (2) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))
:::

Pașii și efectele:

- **Cererea trebuie făcută de toți membrii.** Desființarea voluntară presupune solicitarea tuturor membrilor, nu a unuia singur.
- **Data desființării: anul fiscal următor.** Anul în care se depune cererea rămâne an de consolidare.
- **Recalcularea acoperă toată perioada.** De la primul an de consolidare până la începutul anului în care grupul se desființează, fiecare membru își calculează impozitul pe propriul rezultat fiscal.
- **Persoana juridică responsabilă recalculează impozitul grupului** și depune declarația fiscală rectificativă.
- **Accesoriile se calculează potrivit Codului de procedură fiscală.** Dobânda e de 0,02% pe zi, iar penalitatea de întârziere de 0,01% pe zi. Pentru diferențele rezultate din corectarea declarațiilor, dobânzile curg de la scadența creanței pentru care s-a stabilit diferența (art. 174 alin. (2)); pentru impozitele cu perioadă fiscală anuală, art. 175 conține reguli speciale privind momentul de la care se calculează, aplicabile și penalităților (art. 176 alin. (1)).
- **După desființare**, membrii declară și plătesc impozitul pe profit individual, potrivit art. 41 și 42.
- **Excepțiile de la art. 42^8 alin. (3)** (vânzarea participației sub 25%, dizolvarea unui membru, reorganizarea) privesc ieșirea unui membru, nu desființarea voluntară a întregului grup.

::: ghid-exemplu
SC Exemplu SRL (persoana juridică responsabilă) și o filială formează un grup fiscal din 2024. În 2026, ambele cer desființarea, deci grupul se desființează din 2027. Rezultate fiscale anuale, aceleași în 2024, 2025 și 2026:
- SC Exemplu SRL: profit 500.000 lei;
- filiala: pierdere 200.000 lei.

În consolidare: (500.000 − 200.000) × 16% = 48.000 lei pe an.
Individual: SC Exemplu SRL datorează 500.000 × 16% = 80.000 lei pe an. Filiala are pierdere și nu datorează impozit.
Diferență: 80.000 − 48.000 = 32.000 lei pe an, deci 96.000 lei pentru cei trei ani, plus accesorii.

Ca ordin de mărime, pentru diferența de 32.000 lei aferentă unui an, o întârziere de 365 de zile înseamnă dobânzi de 32.000 × 0,02% × 365 = 2.336 lei și penalități de 32.000 × 0,01% × 365 = 1.168 lei.
:::

## Ce se greșește în practică

- Se crede că desființarea produce efecte din anul cererii. Legea spune „începând cu anul fiscal următor".
- Se recalculează doar ultimul an, nu întreaga perioadă de la data aplicării sistemului.
- Persoana juridică responsabilă nu depune declarația rectificativă pentru grup.
- Accesoriile se omit în bugetul deciziei de desființare, deși pot fi semnificative după câțiva ani de consolidare.
- Excepțiile de la alin. (3), gândite pentru ieșirea unui membru, se aplică desființării voluntare.

## Ce face iConta.eu

iConta.eu calculează declarația individuală de impozit pe profit (D101) din balanța fiecărei firme din portofoliu și generează XML validat. Declarația consolidată a grupului fiscal (D101G) nu se poate genera încă din interfața aplicației. Aplicația nu recalculează retroactiv impozitul la desființarea grupului și nu calculează dobânzile și penalitățile aferente. Recalcularea pe fiecare membru, accesoriile și declarațiile rectificative le face contabilul.

[iConta.eu](/)
