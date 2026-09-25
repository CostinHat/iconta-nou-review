---
title: "Corectarea facturilor emise cu TVA eronat 2026"
description: "Cum se corectează legal o factură emisă cu cotă de TVA greșită și cum semnalează iConta.eu facturile emise la o cotă neconformă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Corectarea facturilor emise cu TVA eronat 2026

O factură emisă cu TVA calculat greșit — cel mai frecvent, cu cota veche după o schimbare legislativă — nu se editează pur și simplu. Legea prevede un mecanism explicit de corecție prin documente noi, iar cota corectă e cea valabilă la data facturii, nu la data la care observi greșeala.

## Temeiul legal

::: ghid-temei
„Corectarea informațiilor înscrise în facturi [...] se efectuează astfel: a) în cazul în care factura nu a fost transmisă către beneficiar, aceasta se anulează și se emite o nouă factură; b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus [...], iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus [...], în care se înscriu numărul și data facturii corectate."
— Codul fiscal (Legea 227/2015), art. 330 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Cota corectă e cea standard (21%) sau redusă valabilă **la data la care a intervenit faptul generator**, cu excepția facturii/avansului emis înainte de livrare, caz în care contează data facturii sau a încasării avansului (art. 291 alin. 4-5 Cod fiscal).
- Corectarea unei facturi deja transmise beneficiarului se face prin una din cele două variante de la art. 330 alin. (1) lit. b): fie o singură factură nouă (minus + corect), fie două facturi separate (una doar cu minus, una doar cu valorile corecte) — ambele fac referire explicită la factura corectată.
- Dacă neconformitatea a fost constatată printr-un control fiscal, cu obligare la plata sumelor, factura de corecție trebuie să poarte mențiunea „emisă după control" și se înscrie separat în decontul de taxă (art. 330 alin. 3).
- Corecția nu recalculează cota la data corecției — stornarea preia exact clasificarea și cota facturii inițiale; doar factura nouă, separată, poartă cota corectă.

## Ce se greșește în practică

- Se editează factura originală în loc să se emită documentele de corecție prevăzute de art. 330 — o factură transmisă nu se poate modifica retroactiv „pe loc".
- Se aplică la stornare o cotă recalculată la data corecției, în loc să se păstreze cota facturii inițiale — stornarea trebuie să anuleze exact ce s-a facturat greșit, nu o variantă „actualizată".
- Se presupune că orice diferență de cotă e o eroare de perioadă (cotă veche după schimbarea legii), când de fapt poate fi o eroare de încadrare a produsului/serviciului (11% aplicat unui serviciu care cerea 21%) — cele două cauze cer verificări diferite.
- Se uită mențiunea „emisă după control" pe facturile de corecție rezultate dintr-un control fiscal, deși legea o cere explicit.

## Ce face iConta.eu

iConta verifică automat, pentru fiecare firmă, dacă facturile emise la **cota standard** au cota corectă pentru data lor de emitere — motorul compară TVA de pe fiecare linie cu baza × cota standard valabilă la acea dată (de exemplu 21% de la 1 august 2025, 19% înainte). Verificarea acoperă doar liniile la cota standard: liniile la cotă redusă (11%) sau scutite nu sunt verificate de acest mecanism, pentru că schimbarea cotei standard nu le afectează. La fel, aplicația **nu verifică dacă un produs sau serviciu ar fi trebuit încadrat la altă cotă** (de exemplu 11% în loc de 21%) — asta e o eroare de clasificare de produs, nu de perioadă, și rămâne responsabilitatea contabilului.

Când găsește o factură cu cota veche aplicată după schimbarea legală, aplicația marchează roșu constatarea și **sugerează** remediul (stornare + reemitere sau factură de corecție) — nu corectează nimic automat; cota corectă o confirmă întotdeauna contabilul. Butonul „Stornează" din ecranul facturii creează documentul de corecție cu valori negative, păstrând clasificarea fiscală și cota facturii originale, exact cum cere mecanismul legal. O limitare curentă: dacă factura corectată a fost deja trimisă prin RO e-Factura, documentul de stornare generat de aplicație nu are încă buton de trimitere în SPV — trimiterea corecției către ANAF rămâne, la acest moment, în afara fluxului automatizat.

[iConta.eu](/)
