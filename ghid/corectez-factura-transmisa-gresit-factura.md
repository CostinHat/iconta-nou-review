---
title: Cum corectez o factură transmisă greșit în e-Factura
description: O factură transmisă greșit în SPV nu se retrage și nu se editează — se corectează exclusiv prin stornare, un document nou cu valori negative, care la rândul lui trebuie transmis separat către ANAF.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez o factură transmisă greșit în e-Factura

Odată transmisă în RO e-Factura, o factură greșită nu mai poate fi „retrasă" din SPV sau editată pe loc — corecția se face exclusiv printr-un document nou, factura de stornare.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69
:::

Notă de precizie legală: o regulă tehnică des invocată — că o factură transmisă în SPV poate fi „anulată" în primele 5 zile calendaristice, dacă nu a fost descărcată de destinatar — nu are, la acest moment, un temei identificat direct în legislația de bază a e-Facturii verificată aici. Dacă ai auzit de această fereastră de 5 zile, tratează-o ca o eventuală procedură tehnică a portalului SPV, de verificat direct la sursa ANAF, nu ca o regulă contabilă generală — anularea (document netransmis, neînregistrat în contabilitate) și stornarea (document deja înregistrat, corectat printr-un document nou) sunt oricum situații diferite.

Pentru o factură deja transmisă și înregistrată în contabilitate, singura cale de corecție confirmată e stornarea: un document nou, cu cantitățile negate față de original, care păstrează cota de TVA, cursul valutar și clasificarea fiscală ale facturii inițiale.

## Ce se greșește în practică

- Se caută o opțiune de „retragere" sau „anulare" a facturii transmise în SPV — pentru o factură deja înregistrată în contabilitate, calea corectă e stornarea, nu anularea.
- Se emite factura de stornare, dar se consideră corectarea încheiată fără să se transmită și acest document nou către ANAF.
- Se editează direct linia greșită pe factura originală, deja transmisă — nu e o opțiune odată ce factura a generat notă contabilă.

## Ce face iConta.eu

Corecția unei facturi contabilizate e blocată la ștergere sau editare directă — sistemul refuză explicit, cu mesajul că se corectează prin stornare. La stornare, iConta.eu generează automat documentul de corecție: liniile originalului cu cantități negate, număr nou din aceeași serie, curs valutar și clasificare fiscală identice cu ale originalului.

De reținut: butonul de trimitere în SPV nu apare pe documentul de stornare — transmiterea efectivă a corecției către ANAF nu are, în acest moment, o cale automată în interfață; e un pas pe care contabilul trebuie să-l rezolve separat.

[iConta.eu](/)
