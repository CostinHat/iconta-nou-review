---
title: Instrumente pentru alerte de termene fiscale
description: iConta.eu afișează automat termenele fiscale ale firmei (scadențe, semafor de conformare), dar singurele mecanisme cu adevărat proactive din aplicație acoperă legislația nouă și findingurile roșii de control fiscal, nu termenele proprii, configurabile.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Instrumente pentru alerte de termene fiscale

Dacă se caută un „instrument" în sensul strict — un ecran unde se aleg termenele de urmărit și pragul de alertă —, răspunsul onest e că un asemenea instrument de configurare nu există, în acest moment, în iConta.eu. Există însă câteva mecanisme reale, automate, care se apropie de ideea de alertă, fiecare cu un scop diferit de „termenele fiscale" proprii firmei.

## Ce e afișare automată, nu alertă configurabilă

Trei ecrane calculează și arată automat, fără intervenția utilizatorului, situația termenelor fiscale ale firmei: scadențele declarative derivate din vectorul fiscal, o listă a termenelor viitoare pe un orizont fix de 60 de zile (grupată pe dată, pentru toate firmele din portofoliu) și un indicator de tip semafor pentru starea generală de conformare. Toate trei sunt utile ca punct de plecare, dar rămân afișări la cerere — nu se poate alege un prag propriu de zile, un canal de notificare (e-mail, push) sau declarațiile urmărite selectiv.

## Ce e, într-adevăr, o alertă proactivă în aplicație

Două mecanisme din iConta.eu funcționează efectiv ca alerte trimise, nu doar afișate la cerere — dar niciunul dintre ele nu e „instrument de configurat" de către utilizator, ci un job automat cu reguli fixe:

- **Alertele legislative** — un job zilnic (dimineața) care semnalează modificările de legislație fiscală relevante, cu praguri fixe de afișare, indiferent de firmă.
- **Notificările în-app pentru findinguri roșii de control fiscal** — un job zilnic, separat, care pushează în aplicație doar constatările „roșii" din câteva verificări specifice (TVA, D112, D390, cota de TVA), agregate per firmă, către persoanele din cabinet responsabile de validarea acelei firme.

Niciunul dintre cele două nu urmărește termene de depunere — primul urmărește noutățile legislative, al doilea urmărește erori deja constatate în declarațiile depuse, nu scadențe viitoare.

## Ce se greșește în practică

- Se caută un instrument unic de „alerte termene fiscale" care să acopere tot — de fapt, funcțiile relevante sunt împărțite pe mai multe ecrane, cu scopuri diferite, fără un punct central de configurare.
- Se confundă notificările roșii de control fiscal (care privesc erori deja existente în declarații) cu o alertă de scadență viitoare — sunt lucruri diferite, declanșate de cauze diferite.
- Se presupune că, dacă nu apare nicio alertă, totul e în regulă — absența unei notificări roșii nu înseamnă că nu există un termen apropiat de depunere, doar că verificările automate specifice nu au găsit o eroare deja constatată.

## Ce face iConta.eu

Afișarea termenelor fiscale (scadențe pe portofoliu, semafor de conformare) e automată, dar necofigurabilă — fără opt-in, fără prag ales de utilizator. Separat, două joburi automate funcționează efectiv ca alerte proactive: unul zilnic pentru noutăți legislative și unul zilnic pentru findinguri roșii de control fiscal (limitate la TVA, D112, D390 și cota de TVA), trimise către validatorii cabinetului responsabili de firma respectivă. Niciunul dintre aceste mecanisme nu e, astăzi, un instrument configurabil de utilizator pentru termene fiscale proprii — sunt joburi cu reguli fixe, construite pentru alte scopuri, dar cele mai apropiate de ideea de „alertă reală" existentă în aplicație.

[iConta.eu](/)
