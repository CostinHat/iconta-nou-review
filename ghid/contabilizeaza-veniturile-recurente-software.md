---
title: "Cum se contabilizează veniturile recurente din software?"
description: "Abonamentele software (SaaS) încasate în avans se recunosc pe măsura prestării, nu integral la facturare — principiul contabil al angajamentelor aplicat facturării recurente."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează veniturile recurente din software?

O firmă care vinde acces la un produs software prin abonament (SaaS) facturează adesea pe perioade fixe — lunar, anual — uneori încasate integral în avans. Contabil, momentul facturării/încasării nu coincide cu momentul în care venitul poate fi recunoscut: venitul se recunoaște pe măsură ce serviciul e efectiv prestat, nu dintr-odată la emiterea facturii.

## Temeiul legal

::: ghid-temei
„Se consideră prestare de servicii orice operațiune care nu constituie livrare de bunuri, așa cum este definită la art. 270."
— Legea 227/2015, art. 271 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul de recunoaștere pentru abonamentele software:

- Accesul la un produs software pe bază de abonament e o prestare de servicii continuă, conform art. 271 — nu o livrare de bun cu transfer de proprietate la un moment unic, așa cum ar fi vânzarea unei licențe perpetue.
- Din perspectivă contabilă (OMFP 1802/2014, principiul contabilității de angajamente), o facturare anuală încasată integral la începutul perioadei nu înseamnă venit integral recunoscut în luna facturării — suma se înregistrează inițial ca venit în avans (cont 472) și se transferă lunar pe venit (cont 704/708) pe măsură ce serviciul e prestat.
- Din perspectiva TVA, exigibilitatea taxei urmează, de regulă, momentul facturării/încasării avansului, conform regulilor generale de exigibilitate — deci TVA-ul poate deveni exigibil integral la facturare, chiar dacă venitul contabil se eșalonează pe lunile următoare; cele două (exigibilitate TVA și recunoaștere venit) nu se mișcă neapărat sincron.
- Pentru abonamentele reînnoite automat (facturare recurentă lunară fără intervenție manuală de fiecare dată), fiecare factură emisă urmează regulile generale de conținut și, dacă relația e B2B în România, obligația de transmitere prin RO e-Factura.

## Ce se greșește în practică

- Se recunoaște integral ca venit o factură anuală de abonament în luna emiterii, umflând artificial rezultatul lunii respective și subraportând veniturile lunilor următoare din perioada acoperită de abonament.
- Se confundă exigibilitatea TVA (care poate surveni integral la facturarea avansului) cu recunoașterea venitului contabil (care se eșalonează) — sunt două mecanisme distincte, cu reguli proprii.
- Se omite reflectarea sumelor încasate în avans în contul de venituri înregistrate în avans (472), ținându-le direct pe venit, ceea ce denaturează bilanțul la finalul fiecărei perioade intermediare.

## Ce face iConta.eu

iConta.eu are un modul dedicat de facturi recurente, care generează automat facturile periodice pentru abonamente, cu liniile și sumele configurate de utilizator. Ce aplicația **nu face automat** este eșalonarea contabilă a venitului pe perioada de prestare (recunoașterea prin cont de venituri în avans) — fiecare factură emisă se înregistrează ca venit conform notei introduse de contabil; dacă firma vrea eșalonarea corectă pentru facturile anuale plătite în avans, contabilul trebuie să introducă separat notele de reluare lunară a venitului din avans, aplicația nu le generează singură pe baza perioadei de abonament.

[iConta.eu](/)
