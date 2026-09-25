---
title: "Cum se contabilizează comisioanele Stripe?"
description: "Regula contabilă generală pentru comisioanele reținute de un procesator de plăți precum Stripe, în lipsa unei reglementări fiscale dedicate acestui tip de serviciu."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează comisioanele Stripe?

Stripe, ca și alți procesatori de plăți online, nu are un regim fiscal dedicat în legislația românească — nu există un act normativ care să-l menționeze explicit. Din punct de vedere contabil, comisionul reținut de Stripe la fiecare tranzacție e o cheltuială cu serviciile bancare și asimilate, iar suma încasată de la client trebuie evidențiată integral (brut), nu doar suma netă rămasă după comision.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea 82/1991 (legea contabilității), art. 6 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Nu există temei ANAF care să numească Stripe — regula generală se aplică oricărui procesator de plăți:

- **Venitul din vânzare** se recunoaște la valoarea brută facturată clientului (integral), conform regulilor generale de recunoaștere a veniturilor (OMFP 1802/2014, pct. 440-441) — indiferent cât reține Stripe ca și comision înainte de a vira suma netă în contul bancar al firmei.
- **Comisionul Stripe** se înregistrează separat, ca o cheltuială cu serviciile prestate de terți (analitic al contului 627 „Cheltuieli cu serviciile bancare și asimilate" sau un cont similar, în funcție de politica contabilă), pe baza raportului de tranzacții/facturii emise de Stripe.
- **Contul Stripe** (soldul neîncasat încă în contul bancar) se asimilă unei sume în curs de decontare, similar unui cont curent la o instituție de plată, nu casieriei — se reconciliază periodic cu extrasul bancar la momentul transferului efectiv al banilor.

## Ce se greșește în practică

- Se înregistrează doar suma netă primită în bancă (după reținerea comisionului Stripe), fără să se evidențieze separat venitul brut și cheltuiala cu comisionul — asta subraportează atât veniturile, cât și cheltuielile, denaturând contul de profit și pierdere.
- Se omite factura sau raportul de comisioane emis de Stripe ca document justificativ, deducând cheltuiala doar pe baza diferenței din extrasul bancar, fără document care s-o susțină.
- Se tratează TVA-ul (dacă e cazul) aferent comisionului Stripe fără să se verifice regimul aplicabil serviciilor electronice prestate de un furnizor stabilit în afara României (taxare inversă, dacă firma e înregistrată în scopuri de TVA).

## Ce face iConta.eu

iConta.eu oferă contabilitate generală — nu are, la data acestui ghid, o integrare dedicată cu Stripe (import automat de tranzacții sau reconciliere automată a comisioanelor). Operațiunile derulate prin Stripe se introduc manual în aplicație, pe baza rapoartelor descărcate din contul Stripe, la fel ca orice altă operațiune bancară introdusă de contabil.

[iConta.eu](/)
