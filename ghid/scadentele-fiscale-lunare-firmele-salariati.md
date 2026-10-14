---
title: "Scadențele fiscale lunare pentru firmele cu salariați în 2026"
description: "Ce declarație lunară apare pe ecranul Termene pentru o firmă cu salariați și de la ce moment intră ea în calendar."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Scadențele fiscale lunare pentru firmele cu salariați în 2026

O firmă cu cel puțin un salariat activ datorează lunar declarația D112 (declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate). Ecranul „Termene” din iConta.eu o include automat în calendarul de scadențe al firmei, din luna în care apare primul salariat.

## Temeiul legal

::: ghid-temei
„Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora, [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate.”
— Codul fiscal (Legea 227/2015), art. 147 alin. (1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Termenul legal al D112 este, deci, 25 a lunii următoare celei pentru care se plătesc veniturile — aceeași dată pe care o folosește și aplicația în calendarul de scadențe.

## Ce se greșește în practică

- Se așteaptă ca D112 să apară retroactiv pe lunile dinaintea angajării primului salariat — aplicația nu face asta; verifică pe fapt, lună cu lună, dacă firma a avut salariat activ în luna respectivă, nu doar starea curentă.
- Se presupune că D112 rămâne în calendar și după ce firma nu mai are niciun salariat — verificarea e lunară, pe fapt, nu o bifă permanentă.

## Ce face iConta.eu

Motorul de calcul verifică, pentru fiecare lună, dacă firma a avut salariat activ efectiv în acea lună (nu doar o bifă statică „are salariați”). D112 intră în lista de scadențe viitoare doar pentru lunile în care această condiție e îndeplinită — corectând o problemă mai veche în care o firmă care angaja primul salariat la mijlocul anului primea, eronat, D112 restant și pe lunile dinainte de angajare.

Ca și celelalte declarații de pe acest ecran, D112 e afișată doar dacă scade în următoarele 60 de zile, data e mutată automat pe prima zi lucrătoare dacă termenul cade în weekend sau sărbătoare legală, iar ecranul e disponibil doar conturilor de cabinet cu portofoliu de firme.

[iConta.eu](/)
