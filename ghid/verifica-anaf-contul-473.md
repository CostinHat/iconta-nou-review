---
title: "Ce verifică ANAF la contul 473?"
description: "De ce contul 473 Decontări din operațiuni în curs de clarificare este un indicator urmărit la controale și cum trebuie clarificat conform termenului legal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce verifică ANAF la contul 473?

Contul 473 „Decontări din operațiuni în curs de clarificare" există pentru situații excepționale, tranzitorii: o sumă intrată sau ieșită din trezorerie pentru care, la momentul înregistrării, nu se poate stabili încă natura exactă (cui aparține, ce reprezintă). Tocmai pentru că e menit să fie temporar, un sold semnificativ sau vechi pe acest cont atrage atenția organelor de control — pentru că semnalează operațiuni nedocumentate corespunzător.

## Temeiul legal

::: ghid-temei
„352. — (1) Operațiunile care nu pot fi înregistrate direct în conturile corespunzătoare, pentru care sunt necesare clarificări ulterioare, se înregistrează, provizoriu, în contul 473 «Decontări din operațiuni în curs de clarificare». Sumele înregistrate în acest cont trebuie clarificate de către entitate într‐un termen de cel mult trei luni de la data constatării.
(2) Entitățile care înregistrează sold la contul 473 «Decontări din operațiuni în curs de clarificare» la sfârșitul exercițiului financiar prezintă în notele explicative informații privind natura operațiunilor în curs de clarificare."
— OMFP 1802/2014, pct. 352 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

- Legea fixează explicit un termen maxim de trei luni de la data constatării pentru clarificarea sumelor înregistrate provizoriu în contul 473 — un sold care „îmbătrânește" peste acest termen este, prin definiție, o neconformitate contabilă.
- Dacă la finalul exercițiului financiar există sold pe 473, entitatea are obligația să explice în notele la situațiile financiare natura exactă a operațiunilor rămase neclarificate — nu poate fi doar o sumă „lăsată acolo" fără justificare.
- Un sold semnificativ sau recurent pe 473 este un indicator tipic urmărit la controale, pentru că poate ascunde venituri neînregistrate, cheltuieli nedocumentate sau sume care ar fi trebuit reclasificate demult către conturile de clienți, furnizori, debitori/creditori diverși sau venituri/cheltuieli.

## Ce se greșește în practică

- Se lasă sume pe contul 473 mult peste termenul legal de trei luni, fără nicio acțiune de clarificare sau reclasificare.
- Se folosește contul 473 ca „sertar" general pentru orice sumă greu de justificat, în loc să se identifice contul corect încă de la înregistrarea inițială (client, furnizor, debitor divers etc.).
- Se ignoră obligația de a detalia în notele explicative natura sumelor rămase în sold la 473 la finalul exercițiului financiar, ceea ce ridică suspiciuni suplimentare la analiza situațiilor financiare.

## Ce face iConta.eu

Contul 473 este prezent în planul de conturi implementat de iConta.eu (`plan_omfp.py`), alături de descrierea sa oficială, dar la verificarea codului nu există în prezent o funcție dedicată care să alerteze automat asupra unui sold vechi (peste termenul legal de trei luni) rămas pe acest cont. Monitorizarea soldului contului 473 și clarificarea la timp a operațiunilor înregistrate provizoriu rămân, deocamdată, o sarcină manuală a contabilului.

[iConta.eu](/)
