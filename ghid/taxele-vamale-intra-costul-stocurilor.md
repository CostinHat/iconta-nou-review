---
title: "Taxele vamale intră în costul stocurilor importate?"
description: Taxele vamale nerecuperabile fac parte din costul de achiziție al mărfurilor importate — calculul taxei se face separat, la vamă, dar capitalizarea ei pe articolele stocului e un pas contabil distinct.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Taxele vamale intră în costul stocurilor importate?

Da, taxele vamale intră în costul de achiziție al mărfurilor importate — dar procesul are, practic, doi pași separați: calcularea taxei vamale (la vamă, pe baza valorii în vamă) și, apoi, capitalizarea acelei taxe, deja calculate, pe articolele din nota de intrare-recepție.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Secțiunea 1.2, pct. 6: „costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe (cu excepția acelora pe care persoana juridică le poate recupera de la autoritățile fiscale), cheltuielile de transport, manipulare și alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective."
:::

Textul include explicit „taxele de import" printre elementele costului de achiziție, alături de prețul de cumpărare și transport. Important: acest text privește costul de achiziție **contabil**, nu baza de calcul a TVA la import, care e reglementată separat de Codul fiscal, art. 289, cu scopuri diferite — cele două calcule se suprapun parțial (ambele includ transport, taxe), dar servesc scopuri distincte (cost de achiziție vs. bază TVA la import).

## Ce se greșește în practică

- Se lasă taxa vamală ca o cheltuială separată, nedescărcată în costul mărfii, în loc să fie capitalizată în cont 371, ceea ce denaturează costul de achiziție și, implicit, adaosul comercial la vânzare.
- Se confundă baza de calcul a TVA la import (art. 289 din Codul fiscal, care cuprinde valoarea în vamă + taxe + accize + cheltuieli accesorii) cu costul de achiziție contabil — cele două nu au întotdeauna aceeași valoare finală, chiar dacă elementele se suprapun parțial.
- Se presupune că taxa vamală se repartizează automat pe articolele NIR doar pentru că a fost calculată corect la vamă — capitalizarea pe articole e un pas separat, care trebuie introdus explicit în ecranul de recepție a mărfii.

## Ce face iConta.eu

Calculul taxei vamale și al bazei de TVA la import se face în ecranul de import extracomunitar, pe baza valorii în vamă, procentului de taxă vamală și eventualelor accize. Suma taxei vamale rezultate se introduce apoi, ca parametru separat, în ecranul NIR, unde e capitalizată automat proporțional cu costul de bază al fiecărei linii din NIR, cu restul de rotunjire pe ultima linie. Cele două ecrane nu sunt integrate automat — fluxul complet presupune parcurgerea ambilor pași, în ordine: întâi calculul taxei la import, apoi introducerea ei ca accesoriu la NIR.

[iConta.eu](/)
