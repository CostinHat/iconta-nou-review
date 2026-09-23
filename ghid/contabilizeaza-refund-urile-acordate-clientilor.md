---
title: Cum se contabilizează refund-urile acordate clienților unui SaaS?
description: Un refund acordat unui client de SaaS se contabilizează prin stornarea facturii de abonament — aceeași cotă de TVA, aceleași conturi, doar suma negată — nu ca o cheltuială nouă sau o notă separată de „refund".
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se contabilizează refund-urile acordate clienților unui SaaS?

Un refund pentru un abonament SaaS nu e o operațiune contabilă nouă, distinctă — e corectarea facturii de vânzare deja emise pentru acel abonament, prin stornare.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69
:::

Stornarea unei facturi de abonament SaaS urmează același principiu ca orice altă stornare: se emite un document nou, cu liniile facturii originale copiate și cantitățile (sau valoarea abonamentului) negate, păstrând exact cota de TVA a facturii inițiale și clasificarea ei fiscală — nu se recalculează nimic la data refund-ului, nici măcar dacă între timp cota legală de TVA s-ar fi schimbat.

Documentul de stornare, generat prin funcția dedicată, copiază cursul valutar al facturii originale (relevant pentru un SaaS facturat în valută) și clasificarea fiscală a acesteia, astfel încât refund-ul să „oglindească" exact vânzarea inițială, nu o operațiune nouă, neclasificată.

De reținut: mecanismul confirmat construiește un document care oglindește integral factura originală (aceleași linii, negate). Pentru un refund parțial — de exemplu doar o parte din valoarea unui abonament anual — cea mai sigură practică e emiterea stornării exact pentru porțiunea returnată, nu pentru toată factura, dacă aplicația permite ajustarea cantităților/valorii la generarea documentului de corecție.

## Ce se greșește în practică

- Se înregistrează refund-ul ca o cheltuială nouă a firmei (de exemplu pe un cont de cheltuieli comerciale), în loc de o corectare a venitului deja recunoscut prin stornarea facturii — abordarea corectă e stornarea, nu o cheltuială separată.
- Se aplică la refund o cotă de TVA recalculată la data restituirii, în loc de cota facturii originale.
- Se ține evidența refund-urilor doar în platforma de plăți (Stripe, PayPal etc.), fără emiterea facturii de stornare corespunzătoare în contabilitate.

## Ce face iConta.eu

Funcția de stornare din iConta.eu generează automat, pentru orice factură emisă — inclusiv una de abonament SaaS — documentul de corecție: liniile originalului cu cantități/valori negate, aceeași cotă de TVA, același curs valutar și aceeași clasificare fiscală ca ale facturii inițiale.

[iConta.eu](/)
