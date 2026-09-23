---
title: "Checklist lunar pentru respectarea termenelor fiscale"
description: "Cum folosești ecranul Termene din iConta.eu ca checklist lunar de scadențe pe portofoliu și ce limitări trebuie cunoscute."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Checklist lunar pentru respectarea termenelor fiscale

Pentru un cabinet cu portofoliu de firme, ecranul „Termene” din iConta.eu agregă, pentru toate firmele, declarațiile scadente în următoarele 60 de zile, grupate pe dată. E gândit ca instrument de verificare periodică, dar are câteva limite pe care merită să le cunoști înainte să-l folosești drept checklist unic.

## Temeiul legal

::: ghid-temei
Descrierea funcționalității (din documentația internă a aplicației): „Pentru fiecare firmă derivă din vectorul fiscal declarațiile datorate cu termenele următoarelor 60 de zile; agregare pe portofoliu, grupare pe dată.”
:::

Ecranul de agregare în sine nu are un temei legal propriu — fiecare declarație afișată își are propriul temei (de exemplu, art. 323 alin. (1) Cod fiscal pentru D300, OPANAF 705/2020 pentru D390 ș.a.m.d.), în funcție de tipul de obligație.

## Ce se greșește în practică

- Se tratează lista din „Termene” ca fiind completă pentru toate obligațiile firmei — ecranul arată strict viitorul apropiat (60 de zile), nu și restanțele. O declarație deja scadentă în trecut nu apare aici deloc, ci pe ecranul separat „Semafor conformare fiscală”.
- Se presupune că lista se actualizează instant după fiecare depunere — ecranul citește un model precalculat periodic de un proces de fundal, nu recalculează live la fiecare afișare.
- Se așteaptă ca ecranul să acopere absolut toate tipurile de declarații — anumite obligații (de exemplu D205, legată de dividende distribuite) nu apar pe acest ecran, ci doar în Semafor.
- Pentru firme la regim de impozit pe profit (nu micro), se presupune că ecranul urmărește și avansurile trimestriale de impozit pe profit (D100, cod obligație 103) — la momentul cercetării, motorul comun generează pentru aceste firme doar D101 (declarația anuală), nu și avansul trimestrial; aceasta e o lipsă cunoscută, semnalată explicit chiar în codul aplicației ca datorie deschisă.
- Pentru un SAF-T (D406) aflat la prima raportare a firmei, se ia data afișată drept termenul real — legea prevede o perioadă de grație la prima raportare (până la 6 luni pentru contribuabilii lunari, 3 luni pentru cei trimestriali), pe care aplicația nu o calculează; data afișată e termenul nominal, fără grație.

## Ce face iConta.eu

Pentru fiecare firmă din portofoliu, aplicația citește vectorul fiscal (regim de impozitare, calitate de plătitor de TVA, prezența operațiunilor intracomunitare) și derivă declarațiile datorate în fereastra fixă de 60 de zile calendaristice (nu configurabilă din interfață), afișate grupate pe dată, cu etichete relative („azi”, „mâine”, „în N zile”). Un click pe o dată deschide firmele cu acea scadență; un click pe firmă deschide fișa ei.

Firmele pentru care nu se poate calcula nimic — de exemplu pentru că nu au vectorul fiscal completat — nu dispar tăcut din listă, ci apar explicit într-o secțiune separată, cu motivul afișat (de exemplu „Vector fiscal necompletat — nu pot evalua obligațiile firmei.”).

Calendarul din acest ecran acoperă, în funcție de regim: D300/D390 (TVA), D406 (SAF-T), D101 (impozit pe profit, anual), D100 (impozit micro, trimestrial) și D112 (contribuții, doar în lunile cu salariat activ). Nu acoperă D205, avansurile trimestriale de profit (D100 cod 103) și nici formalitățile de înființare a firmei (D700 și formularele vechi D010/D020/D070, care oricum nu sunt implementate ca modul separat în iConta.eu — se depun direct la ANAF/ONRC).

Accesul la acest ecran e limitat conturilor de cabinet cu portofoliu de firme; nu e disponibil pe cont individual.

[iConta.eu](/)
