---
title: Cum se gestionează stornarea unei comenzi online
description: Stornarea în iConta.eu anulează întotdeauna 100% din factură; pentru un retur parțial dintr-o comandă online trebuie emisă manual o factură de corecție cu liniile corecte, nu prin butonul de storno.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se gestionează stornarea unei comenzi online

O comandă online se poate întoarce integral sau parțial — clientul returnează tot coletul sau doar un produs din trei. Diferența contează, pentru că mecanismul de storno din iConta.eu tratează un singur caz: anularea completă a facturii.

## Temeiul legal

::: ghid-temei
„Articolul 330 Corectarea facturilor
(1) Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel: […] b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus […], în care se înscriu numărul și data facturii corectate."

„(3) În cazul în care este obligatorie ajustarea bazei impozabile conform art. 287 lit. a)-c) și e), dacă furnizorul de bunuri/prestatorul de servicii nu emite factura de corecție prevăzută la art. 330 alin. (2), beneficiarul trebuie să emită o autofactură în vederea ajustării taxei deductibile, cel târziu până în cea de-a 15-a zi a lunii următoare celei în care au intervenit evenimentele […]" — Cod fiscal 227/2015, art. 319 alin. (3)
:::

## Storno total vs. corecție parțială

Legea permite explicit ambele variante: fie o factură de corecție care conține „valorile corecte" (nu neapărat o anulare integrală), fie stornarea completă urmată de o factură nouă cu valorile corecte. Practic, pentru un retur parțial dintr-o comandă cu mai multe produse, varianta firească e o singură factură de corecție, cu liniile care reflectă exact ce s-a returnat.

Butonul/funcția de storno din iConta.eu nu oferă această variantă. Ea negă întotdeauna **toate liniile** facturii originale, integral — nu există un parametru pentru a selecta o singură linie sau o sumă parțială.

::: ghid-exemplu
Un client comandă 3 produse pe o singură factură și returnează doar 1. Apăsarea „storno" pe acea factură anulează toate cele 3 produse, nu doar produsul returnat. Pentru situația reală (retur parțial), trebuie construită manual o factură de corecție separată, cu o singură linie — cea a produsului returnat — nu prin funcția de storno.
:::

Dacă vânzătorul nu emite la timp factura de corecție pentru un retur pe care l-a acceptat, obligația de ajustare a taxei deductibile poate trece la cumpărător, sub forma unei autofacturi, cu termen până în a 15-a zi a lunii următoare (art. 319 alin. 3).

## Ce se greșește în practică

- Se apasă „storno" pentru un retur parțial, crezând că sistemul va anula doar produsul returnat — de fapt anulează întreaga factură.
- După un storno total greșit aplicat unui retur parțial, se uită să se reemită o factură nouă, corectă, pentru produsele nereturnate.
- Se confundă „retur de marfă" (problemă de stoc/logistică) cu „corecție de factură" (problemă fiscală) — cele două trebuie sincronizate manual.
- Nu se respectă termenul de 15 zile pentru autofactură atunci când furnizorul întârzie emiterea corecției.

## Ce face iConta.eu

Funcția de storno (`storneaza`) neagă integral toate liniile facturii originale (`-abs(cantitate)` pe fiecare linie), fără niciun parametru de selecție a liniilor sau de sumă parțială — stornarea e mereu 100%. Pentru o corecție parțială, singura variantă disponibilă azi e construirea manuală a unei facturi de corecție prin fluxul normal de creare a facturii, cu liniile exacte ale returului, fără să se treacă prin funcția de storno. Sistemul nu are un tip de document „autofactură" implementat — situațiile în care obligația de ajustare trece la cumpărător, conform art. 319 alin. (3), nu pot fi emise cu motorul curent.

[iConta.eu](/)
