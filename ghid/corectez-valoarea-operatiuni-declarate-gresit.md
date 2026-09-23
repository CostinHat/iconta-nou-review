---
title: "Cum corectez valoarea unei operațiuni declarate greșit în D390?"
description: Nu există „editare" a unei valori direct în D390 — corecția se face la sursă (factură) sau prin ștergere și re-adăugare (linie manuală).
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez valoarea unei operațiuni declarate greșit în D390?

Ca și la codul de TVA al partenerului, corecția depinde de sursa operațiunii — și, la fel, nu există o funcție de „editare" directă a unei valori în panoul D390.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Secțiunea I**:
> „[...] ATENŢIE: Informaţiile completate eronat în perioade de raportare anterioare nu se corectează prin înscrierea cifrei «0» la rubrica «Bază impozabilă» [...]"
:::

Norma vizează în mod direct declarațiile deja depuse, pentru perioade anterioare — pentru o declarație aflată încă la pasul 2, nedepusă, discuția e strict despre cum funcționează panoul de clasificare din aplicație.

## Ce se greșește în practică

Greșeala tipică este căutarea unui buton de „editare" a bazei impozabile a unei operațiuni direct din panoul D390 — nu există; funcția acoperă doar adăugarea și ștergerea liniilor manuale, nu modificarea lor in-place.

## Ce face iConta.eu

- dacă operațiunea provine dintr-o **factură** (clasificare automată), valoarea greșită se corectează la sursă — pe factură (prin stornare și reemitere, sau editarea facturii, după fluxul standard al aplicației), nu din panoul D390; după corectarea facturii, regenerezi declarația;
- dacă e o **linie manuală**, nu există o operațiune de „actualizare" a bazei — motorul de clasificare expune doar adăugare și ștergere. Corectarea unei linii manuale greșite înseamnă: ștergi linia greșită, apoi adaugi una nouă cu valoarea corectă.

O atenție suplimentară: dacă declarația D390 a fost deja generată pentru perioadă, ștergerea unei linii manuale cere confirmare din partea unui utilizator cu rol de administrator al firmei — aplicația tratează asta ca pe o modificare a ceva deja emis. Adăugarea unei linii noi sau reclasificarea unei operațiuni auto, în schimb, nu au acest control suplimentar în acest moment, chiar dacă declarația a fost deja generată sau depusă — așa că, dacă corecția are loc după depunere, ține cont că trebuie tratată, legal, ca o rectificare a declarației (vezi limitarea privind rectificativa, semnalată în ghidurile despre facturi/achiziții omise).

[iConta.eu](/)
