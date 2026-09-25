---
title: "Care este plafonul pentru încasările cash and carry în 2026?"
description: "Plafonul special de sold de casă pentru magazinele de tip cash and carry, super și hipermarket, conform Legii 70/2015 modificate prin OUG 115/2023."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este plafonul pentru încasările cash and carry în 2026?

Magazinele de tip cash and carry, supermagazinele și hipermagazinele au un plafon de sold de casă de zece ori mai mare decât regula generală — dar plafonul „standard" de 50.000 lei rămâne aplicabil oricărei alte entități.

## Temeiul legal

::: ghid-temei
„Sumele în numerar aflate în casieria persoanelor prevăzute la art. 1 alin. (1) nu pot depăși, la sfârșitul fiecărei zile, plafonul de 50.000 lei. În cazul magazinelor de tipul cash and carry, supermagazinelor și hipermagazinelor care sunt organizate și funcționează în baza legislației în vigoare, sumele în numerar aflate în casierie nu pot depăși, la sfârșitul fiecărei zile, plafonul de 500.000 lei. Sumele în numerar care depășesc plafonul se depun în conturile bancare ale acestor persoane în termen de două zile lucrătoare."
— Legea 70/2015, art. 4^2 alin. (1), astfel cum a fost modificat prin OUG 115/2023 (sursă: anaf_surse/oug_115_2023_consolidat.txt)
:::

Din text rezultă două plafoane distincte de **sold de casă la sfârșitul zilei** (nu de încasare pe tranzacție):

- **50.000 lei** — plafonul general, pentru toate entitățile vizate de Legea 70/2015 (persoane juridice, PFA, întreprinderi individuale/familiale etc.).
- **500.000 lei** — plafonul special pentru magazinele de tip cash and carry, supermagazine și hipermagazine, organizate potrivit legislației specifice comerțului.
- Suma care depășește plafonul aplicabil trebuie depusă în cont bancar **în termen de două zile lucrătoare** de la data constatării.

Acest plafon de sold e diferit de plafonul de **încasare zilnică de la o singură persoană** din magazinele cash and carry, care este de 10.000 lei potrivit art. 3 alin. (1) lit. b) din aceeași lege — cele două praguri nu trebuie confundate: unul limitează cât numerar poate rămâne în casierie la finalul zilei, celălalt cât se poate încasa de la un singur client într-o zi.

## Ce se greșește în practică

- Se confundă plafonul de sold de casă (500.000 lei, la sfârșitul zilei) cu plafonul de încasare de la o persoană (10.000 lei, per tranzacție/zi) — sunt reguli diferite, din articole diferite ale aceleiași legi.
- Se aplică plafonul de 500.000 lei unor magazine care nu se încadrează legal în categoria cash and carry/supermagazin/hipermagazin, fără verificarea organizării și funcționării lor potrivit legislației comerțului.
- Se depășește termenul de două zile lucrătoare pentru depunerea la bancă a sumei care trece de plafon, considerând eronat că simpla constatare a depășirii, fără depunere, e suficientă.

## Ce face iConta.eu

Modulul de casierie al iConta.eu (`core/casa.py`) aplică efectiv acest plafon dublu: funcția `verifica_plafon` calculează soldul de casă la sfârșitul fiecărei zile și semnalează un avertisment (`PLAFON_SOLD_CASA`) când soldul depășește pragul aplicabil — 500.000 lei dacă operațiunile sunt marcate drept `cash_and_carry=True`, respectiv 50.000 lei în regimul standard. Avertismentele generate sunt de nivel informativ (risc la control), nu blocante — aplicația nu împiedică introducerea operațiunii, ci atrage atenția contabilului asupra depășirii.

[iConta.eu](/)
