---
title: Ce fac dacă vectorul fiscal al firmei noi este greșit?
description: La înființare, doar statutul de plătitor de TVA se preia automat din ANAF — regimul fiscal, periodicitatea și operațiunile intracomunitare rămân, întotdeauna, o alegere manuală a contabilului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă vectorul fiscal al firmei noi este greșit?

Dacă vectorul fiscal al unei firme nou create arată greșit, primul lucru de verificat e ce s-a completat automat la înființare și ce a rămas, de fapt, needitat.

## Temeiul legal

::: ghid-temei
Nu există un temei legal unic pentru precompletarea vectorului fiscal la înființarea firmei — regula tehnică de mai jos e o **regulă de produs a iConta**, documentată direct în cod: „NU scrie tip_decont (periodicitatea TVA): ANAF v9 nu o întoarce -> rămâne alegerea contabilului (necunoscut declarat explicit, nu fabricat)." Sursă: `core/tenant_provisioning.py`, funcția `precompleteaza_din_anaf`.
:::

La crearea unei firme (indiferent de cale — cabinet propriu, adăugare manuală, import în masă), aplicația interoghează live ANAF și precompletează automat doar `platitor_tva` (dacă firma e înregistrată TVA), `tva_la_incasare`, un snapshot pentru comparația ulterioară cu ANAF, plus date generale (CAEN, adresă, reg. com.).

`regim_fiscal` (micro/profit), `tip_decont` (periodicitatea TVA) și `operatiuni_ic` **nu se precompletează niciodată** — coloanele corespunzătoare nu au valoare implicită în baza de date, deci o firmă nou creată pornește cu aceste trei câmpuri complet goale, indiferent ce arată ANAF. Dacă vectorul „pare greșit" la o firmă nouă, cel mai probabil aceste trei câmpuri pur și simplu n-au fost completate încă de contabil, nu că ar fi fost completate greșit automat.

Corectarea, în acest caz, e de obicei simplă: fiind o firmă nouă, în majoritatea cazurilor nu există încă perioade fiscale închise, deci completarea/corectarea vectorului e o resalvare directă, fără nevoia de redeschidere de perioade.

## Ce se greșește în practică

- Se presupune că regimul fiscal sau periodicitatea TVA au fost precompletate greșit din ANAF — de fapt, aceste câmpuri nu se precompletează niciodată, indiferent de sursă.
- Se lasă firma cu vectorul necompletat (`completat=False`), fără să se observe că declarațiile dependente ies gri în semafor din acest motiv.
- Se editează doar `platitor_tva` (singurul câmp precompletat automat), fără să se completeze și celelalte trei atribute obligatorii ale vectorului.

## Ce face iConta.eu

Funcția `precompleteaza_din_anaf` (`core/tenant_provisioning.py`) e sursa unică pentru toate căile de creare a unei firme; docstring-ul ei afirmă explicit alegerea de produs de a nu „ghici" periodicitatea TVA, regimul fiscal sau operațiunile intracomunitare — acestea rămân „necunoscut declarat explicit, nu fabricat". Vectorul a fost adus pe ecranul individual „Date firmă" tocmai pentru a evita situația anterioară, în care o firmă adăugată direct rămânea pe valorile implicite din șablon (micro, neplătitor TVA, fără intracom) — adică pe presupuneri, nu pe date reale.

[iConta.eu](/)
