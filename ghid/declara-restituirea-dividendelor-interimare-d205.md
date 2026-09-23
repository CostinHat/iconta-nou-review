---
title: Cum se declară restituirea dividendelor interimare în D205?
description: Când interimarele plătite depășesc dividendul anual aprobat, asociatul restituie diferența într-un cont diferit de cel pe care se calculează D205 automat — restituirea trebuie tratată manual în declarație.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară restituirea dividendelor interimare în D205?

Dacă dividendele interimare distribuite în cursul anului depășesc dividendul anual aprobat ulterior de adunarea asociaților, diferența trebuie restituită de asociat firmei — iar acest lucru are consecințe și pentru declarația D205.

## Temeiul legal

::: ghid-temei
**Legea 31/1990, art. 67 alin. (2^2)**: „În cazul în care asociații sau acționarii datorează restituiri de dividende, în urma regularizării [...] acestea se achită societății în termen de 60 de zile de la data aprobării situațiilor financiare anuale."
:::

Când interimarul plătit e mai mare decât dividendul anual aprobat, regularizarea generează, pe lângă compensarea normală (457=463), o notă suplimentară pentru excesul de restituit: firma primește banii înapoi de la asociat, iar suma respectivă se înregistrează direct între bancă și contul de decontări cu asociatul (nu prin contul 457, pe care se calculează automat D205).

Aceasta e diferența importantă: restituirea excesului nu trece prin contul 457, deci nu reduce automat, în calculul declarației, suma deja declarată ca dividend distribuit/plătit pentru acel asociat. Corectarea trebuie tratată separat de contabil, la nivelul declarației, pentru anul în care regularizarea s-a produs.

## Ce se greșește în practică

- Se presupune că restituirea excesului „se scade automat" din D205, pentru că a fost înregistrată contabil — nu se scade automat, pentru că nu afectează contul 457 pe care declarația îl citește.
- Se lasă declarația D205 cu suma inițială, integrală, fără să se corecteze pentru excesul restituit de asociat.
- Se depășește termenul de 60 de zile de la aprobarea situațiilor financiare anuale pentru restituirea efectivă, fără să se urmărească dobânda penalizatoare prevăzută de lege pentru întârziere.

## Ce face iConta.eu

Motorul de decontări asociați din iConta.eu generează automat nota de restituire a excesului de dividend interimar (banca firmei, în corespondență cu contul de decontări cu asociatul), inclusiv în cazul testat explicit al unei restituiri parțiale. Declarația D205 se calculează automat din mișcările contului 457 — pentru că restituirea excesului nu trece prin acest cont, corectarea sumei deja declarate pentru asociatul respectiv rămâne o intervenție pe care contabilul trebuie s-o facă manual, la nivelul declarației aferente anului regularizării.

[iConta.eu](/)
