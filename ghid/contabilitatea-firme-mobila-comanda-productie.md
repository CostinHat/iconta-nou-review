---
title: "Contabilitatea unei firme de mobilă la comandă: producție în curs"
description: "Mobila la comandă e un produs fizic supus regulilor generale de producție în curs și produse finite — nu unui tratament contabil special de sector."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unei firme de mobilă la comandă: producție în curs

O firmă care execută mobilă la comandă are, în mod tipic, comenzi aflate în lucru la sfârșitul lunii — panouri croite, piese asamblate parțial, comenzi nefinalizate. Deși activitatea e „la comandă", din punct de vedere contabil produsul rămas este un bun fizic, nu un serviciu, ceea ce fixează exact ce conturi se folosesc.

## Temeiul legal

::: ghid-temei
„Contul 331 „Produse în curs de execuție" Cu ajutorul acestui cont se ține evidența stocurilor de produse în curs de execuție (care nu au trecut prin toate fazele de prelucrare prevăzute de procesul tehnologic, respectiv producția neterminată) existente la sfârșitul perioadei. [...] valoarea la cost de producție a stocului de produse în curs de execuție la sfârșitul perioadei, stabilită pe bază de inventar (711)."
— OMFP 1802/2014, Reglementările contabile, Cap. 16, funcțiunea contului 331 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o comandă de mobilă nefinalizată la sfârșitul lunii:

- Fiind un **bun fizic** (nu un serviciu), o comandă de mobilă în lucru intră sub definiția producției neterminate din contul 331, evaluată la cost de producție (materiale, manoperă, cheltuieli indirecte alocate) stabilit pe bază de inventar la stadiul de execuție al comenzii.
- La finalizarea comenzii, piesa de mobilă trece în contul 345 „Produse finite" — „valoarea la preț de înregistrare a produselor finite intrate în gestiune [...] (711)" — de regulă la cost standard, dacă firma folosește această metodă, cu eventuala diferență de preț urmărită prin contul 348.
- La livrarea către client, se înregistrează concomitent vânzarea (venit + TVA) și descărcarea de gestiune a produsului finit din 345.

## Ce se greșește în practică

- Se tratează comanda de mobilă drept „serviciu în curs" și se caută un cont de tip 332, deși reglementarea contabilă românească nu prevede un astfel de tratament pentru un bun fizic ca mobila — corect este 331/345, ca la orice produs.
- Se omite constatarea producției în curs pentru comenzile nefinalizate la sfârșitul lunii, mai ales când firma facturează doar la livrare, considerând eronat că „nu s-a întâmplat nimic contabil" până atunci.
- Se evaluează comanda în lucru la prețul de vânzare convenit cu clientul, în loc de costul de producție efectiv acumulat până la acea dată.

## Ce face iConta.eu

Din ecranul **Operațiuni speciale → Imobilizări**, operațiunea „Producție (711/345)" acoperă exact acest flux, generic pentru orice tip de produs: constatarea/reluarea producției în curs pentru comenzile nefinalizate și obținerea produsului finit la finalizare (cu diferența de cost, dacă se folosește cost standard). Notă onestă: nu există în aplicație niciun câmp sau flux specific „mobilă la comandă" — mecanismul este cel general de producție, aplicabil oricărui sector care obține bunuri fizice din proces propriu; particularitățile comenzii (schița, materialele, manopera alocată) rămân calcule făcute de contabil în afara aplicației, al căror rezultat (costul de producție) se introduce manual în nota de producție.

[iConta.eu](/)
