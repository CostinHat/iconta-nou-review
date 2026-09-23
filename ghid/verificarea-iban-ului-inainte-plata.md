---
title: "Verificarea IBAN-ului înainte de plată 2026"
description: iConta.eu validează IBAN-ul angajaților (mod-97) înainte de generarea fișierului de plată a salariilor — dar nu are o funcție generică de verificare IBAN valabilă pentru orice altă plată (facturi, furnizori, taxe).
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Verificarea IBAN-ului înainte de plată 2026

Dacă te interesează verificarea IBAN-ului salariaților înainte de plata salariilor, răspunsul e da — iConta.eu face această verificare automat. Dacă te interesează o verificare IBAN valabilă pentru orice altă plată din aplicație (facturi, furnizori, taxe), răspunsul e nu — o asemenea funcție generică nu există la acest moment.

## Temeiul legal

::: ghid-temei
„Plata salariului se poate efectua prin virament într-un cont bancar, în cazul în care aceasta modalitate este prevăzută în contractul colectiv de muncă aplicabil." — Legea nr. 53/2003 (Codul muncii), art. 161 alin. (2)
:::

Legea nu impune explicit o „verificare a IBAN-ului" înainte de plată — condiția pe care o pune e alta (existența unei prevederi în contractul colectiv de muncă aplicabil pentru plata prin virament). Verificarea tehnică a corectitudinii unui IBAN (formatul, cifra de control mod-97) ține de standardul internațional ISO 13616, nu de o normă fiscală sau de dreptul muncii — dar rămâne, în practică, singura măsură eficientă de prevenire a unei plăți greșite din cauza unui IBAN incorect introdus.

## Ce face, concret, verificarea din iConta.eu

Funcția de validare IBAN din iConta.eu verifică formatul și cifra de control (mod-97, conform ISO 13616), pentru IBAN-uri românești. Ea este folosită în două puncte:

- la introducerea/actualizarea IBAN-ului unui angajat, în fișa salariatului;
- la introducerea IBAN-ului firmei (ordonator), folosit ca sursă a plății în fișierul SEPA.

Un angajat cu IBAN invalid nu e inclus în fișierul de plată generat pentru salarii — e exclus automat și raportat separat, tocmai pentru a preveni transmiterea NET-ului către un cont greșit.

## Ce se greșește în practică

Se presupune, din formularea generică a întrebării „verificarea IBAN-ului înainte de plată", că funcția e disponibilă pentru orice tip de plată din aplicație — facturi către furnizori, plăți către ANAF etc. Nu e cazul: validarea IBAN din iConta.eu e legată explicit de fluxul de plată a salariilor, nu de un modul general reutilizabil pentru alte tipuri de plăți.

## Ce face iConta.eu

Validarea IBAN (mod-97, ISO 13616, doar pentru IBAN-uri românești) există în iConta.eu exclusiv în contextul plății salariilor — pentru IBAN-ul fiecărui angajat și pentru IBAN-ul firmei folosit ca ordonator în fișierul SEPA. Nu există, la acest moment, o funcție de verificare IBAN generică, disponibilă pentru alte tipuri de plăți (facturi, furnizori, taxe) din afara acestui flux.

[iConta.eu](/)
