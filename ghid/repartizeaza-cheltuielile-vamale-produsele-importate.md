---
title: "Cum se repartizează cheltuielile vamale pe produsele importate?"
description: Cheltuielile vamale se calculează separat, la import, apoi se repartizează pe produsele NIR-ului proporțional cu costul lor de bază, cu restul de rotunjire pe ultima linie, exact ca transportul.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se repartizează cheltuielile vamale pe produsele importate?

Repartizarea cheltuielilor vamale (taxă vamală, eventual comision vamal) pe mai multe produse dintr-un import are loc după ce aceste sume au fost deja calculate la vamă — repartizarea propriu-zisă pe articole e un pas contabil separat, ulterior.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Secțiunea 1.2, pct. 6: „costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe (cu excepția acelora pe care persoana juridică le poate recupera de la autoritățile fiscale), cheltuielile de transport, manipulare și alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective."
:::

Ca și în cazul transportului, legea nu impune o cheie de repartizare specifică pentru cheltuielile vamale pe mai multe articole cumpărate simultan — cere doar atribuirea lor directă achiziției bunurilor. Repartizarea proporțională cu costul de bază al fiecărui articol e practica uzuală, dar rămâne o alegere metodologică, nu un text de lege citat literal.

## Ce se greșește în practică

- Se repartizează cheltuiala vamală doar pe câteva articole „principale" din NIR, în loc de toate articolele afectate, proporțional cu valoarea lor.
- Se amestecă baza de calcul a TVA la import (art. 289 din Codul fiscal, cu scop fiscal-declarativ) cu repartizarea contabilă a cheltuielilor vamale pe articole (scop de determinare a costului de achiziție) — sunt calcule paralele, nu identice.
- Se încearcă repartizarea automată a cheltuielilor vamale și pentru firmele care țin gestiunea cantitativ-valorică (CMP), unde acest mecanism nu există în aplicație.

## Ce face iConta.eu

Cheltuiala vamală, odată calculată la import, se introduce ca parametru separat („taxe") în ecranul NIR, unde e repartizată automat proporțional cu costul de bază al fiecărei linii, cu restul de rotunjire alocat ultimei linii — mecanism verificat prin teste (inclusiv cazul în care costul de bază al liniilor e zero, situație în care aplicația respinge explicit repartizarea, cerând un cost de bază pozitiv). Contul de credit al cheltuielii vamale (implicit 446, contul de taxe vamale) e vizibil și configurabil în formular, pentru confirmare de către contabil. Mecanismul funcționează doar pentru firmele cu gestiune global-valorică — pentru gestiune cantitativ-valorică, repartizarea rămâne manuală.

[iConta.eu](/)
