---
title: Ce fac dacă găsesc o factură din anul trecut neînregistrată
description: O factură veche, găsită abia acum, nu se înregistrează cu data ei originală dacă luna respectivă e închisă — se contează la data descoperirii, cu mențiunea explicită a legăturii cu factura și a motivului.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă găsesc o factură din anul trecut neînregistrată

O factură din anul trecut, descoperită abia acum, ridică o întrebare simplă: cu ce dată intră în evidență, dacă luna emiterii ei e deja închisă? Răspunsul nu e „se forțează pe luna veche" și nici „se ignoră" — e un al treilea drum, cablat explicit în aplicație.

## Temeiul legal

::: ghid-temei
„Erorile constatate după depunerea situațiilor financiare anuale se corectează la data constatării lor, potrivit reglementărilor contabile emise de instituțiile prevăzute la art. 4 alin. (1) și (3), după caz." — Legea contabilității nr. 82/1991, art. 36^2

„Corectarea erorilor se efectuează la data constatării lor." — OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 65 alin. (2)
:::

Ambele texte spun același lucru din unghiuri diferite: o eroare (aici, o omisiune — o factură nefolosită) nu se „repară" retroactiv, ca și cum ar fi fost mereu acolo. Se înregistrează la data la care a fost găsită.

## Cum funcționează în iConta.eu

Contarea unei facturi primește, implicit, data emiterii facturii — faptul și evidența lui au aceeași dată, cazul normal.

Pentru o factură veche, descoperită acum, aplicația acceptă explicit o dată diferită pentru notă:

- dacă luna **emiterii** facturii e blocată (Registru jurnal > Blocheaza luna), nota nu se poate scrie pe acea dată — poarta de perioadă o refuză;
- nota se scrie atunci la **data descoperirii** (în luna curentă, deschisă), cu motivul consemnat explicit în descrierea ei — de exemplu „Contare factura ... din 2025-11-14 — inregistrata la 2026-09-23: factură de furnizor găsită la reconcilierea soldurilor";
- legătura cu factura originală nu se pierde — nota rămâne legată de factura reală (`factura_id`), cu data ei corectă de emitere, doar înregistrarea contabilă e datată la momentul găsirii.

Dacă nu se dă explicit o dată de înregistrare și data facturii cade într-o lună blocată, aplicația refuză contarea — nu există o cale silențioasă prin care o factură veche „intră" fără să fie datată corect.

## Ce se greșește în practică

- Se încearcă forțarea datei facturii originale pe nota de contare, ca și cum eroarea „nu ar fi existat" — și aplicația refuză, pentru că luna respectivă e închisă.
- Se lasă câmpul de motiv gol la înregistrarea întârziată, deși descrierea notei ar trebui să spună clar de ce data notei diferă de data facturii — fără el, peste câteva luni nimeni nu mai știe de ce apare acolo.
- Se presupune că o factură de anul trecut, odată găsită, afectează automat rezultatul fiscal al anului trecut — de fapt, dacă situațiile financiare ale acelui an au fost deja depuse, corectarea urmează un tratament separat, în funcție de cât de semnificativă e suma.

## Ce face iConta.eu

Nota de contare poartă implicit data emiterii facturii. Pentru o factură veche descoperită ulterior, aplicația acceptă o dată explicită de înregistrare: dacă luna emiterii e închisă, poarta de perioadă se mută pe data notei, nu pe data facturii, iar descrierea notei consemnează atât data reală a facturii, cât și motivul pentru care înregistrarea e ulterioară. Factura originală rămâne legată de notă prin identificatorul ei, cu data ei corectă — nu se rescrie nimic din trecut, se adaugă doar mențiunea corectă la momentul prezent.

[iConta.eu](/)
