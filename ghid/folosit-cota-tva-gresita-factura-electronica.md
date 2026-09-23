---
title: "Ce fac dacă am folosit o cotă TVA greșită pe factura electronică?"
description: "Mecanismul legal de corecție (art. 330 Cod fiscal) e identic pentru facturi electronice. Dar în iConta.eu, o stornare trimisă prin e-Factura ajunge la SPV ca factură obișnuită (tip 380) cu valori negative, nu ca notă de credit (tip 381) — o limitare tehnică declarată a versiunii curente, nu una legală."
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă am folosit o cotă TVA greșită pe factura electronică?

Legea nu tratează diferit o factură electronică transmisă prin SPV față de una pe hârtie — corecția urmează același mecanism, art. 330 din Codul fiscal. Ce diferă e partea tehnică a transmiterii, unde iConta.eu are în acest moment o limitare declarată, pe care merită s-o cunoști înainte să retrimiți documentele.

## Temeiul legal

::: ghid-temei
**Art. 330 alin. (1):** „Corectarea informațiilor înscrise în facturi [...] se efectuează astfel: a) în cazul în care factura nu a fost transmisă către beneficiar, aceasta se anulează și se emite o nouă factură; b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus [...], iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus [...], în care se înscriu numărul și data facturii corectate."
:::

Nimic din acest text nu depinde de canalul de transmitere — mecanismul de corecție (stornare + factură nouă, sau anulare + reemitere) e valabil identic indiferent dacă factura merge pe e-mail, pe hârtie sau prin SPV.

## Ce faci fiscal

Exact ce ai face pentru orice factură cu cotă greșită: dacă n-a ajuns la client, o anulezi și reemiti la cota corectă; dacă a ajuns deja, o stornezi și emiți o factură nouă, separată, la cota corectă — conform art. 330 alin. (1).

## Limitarea tehnică a transmiterii prin e-Factura

Aici intervine diferența față de o corecție pe hârtie. Când factura de stornare e trimisă mai departe prin e-Factura, versiunea curentă a aplicației o trimite la SPV cu tipul de document marcat **întotdeauna ca factură obișnuită** (codul XML `InvoiceTypeCode 380`), inclusiv atunci când conține valori negative — **nu** ca notă de credit (`InvoiceTypeCode 381`), tipul standard prevăzut de formatul CIUS-RO pentru corecții/stornări.

Practic: o factură de stornare emisă pentru a corecta o cotă TVA greșită, dacă e trimisă prin e-Factura, ajunge la SPV ca factură normală cu valori negative, nu ca notă de credit propriu-zisă. Această limitare e declarată explicit ca atare în aplicație, pentru versiunea curentă, urmând să fie completată după confirmarea comportamentului corect pe mediul de test al SPV.

Important de distins: **mecanismul legal de corecție (art. 330) rămâne valabil** — documentul de stornare există, referă corect factura inițială și produce efectele fiscale corecte. Limitarea e strict de reprezentare tehnică în format XML la transmiterea către SPV, nu o imposibilitate legală de a corecta o factură electronică.

## Ce se greșește în practică

- Se presupune că o stornare trimisă prin e-Factura ajunge automat recunoscută de partener ca „notă de credit" — în acest moment, ajunge ca factură obișnuită cu valori negative (tip 380).
- Nu se anunță partenerul că documentul primit prin SPV e o factură normală cu minus, nu un tip 381 standard — ceea ce poate crea confuzie la reconcilierea automată de partea lui.
- Se confundă limitarea tehnică de transmitere cu o imposibilitate legală de a corecta factura — corecția prin art. 330 e valabilă și completă, independent de acest aspect.

## Ce face iConta.eu

Mecanismul de corecție (stornare + factură nouă, conform art. 330 alin. 1 lit. b) funcționează identic pentru facturi trimise și prin e-Factura. La transmiterea către SPV, însă, aplicația generează în acest moment `InvoiceTypeCode 380` pentru orice factură trimisă, inclusiv pentru stornări — nu există momentan nicio ramură care să genereze `InvoiceTypeCode 381`. Aceasta e o limitare declarată explicit a versiunii curente, cunoscută și asumată, nu o eroare ascunsă — dar merită comunicată partenerului atunci când o corecție de cotă TVA se transmite prin canal electronic.

[iConta.eu](/)
