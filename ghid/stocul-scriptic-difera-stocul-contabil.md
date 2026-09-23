---
title: "Ce faci dacă stocul scriptic diferă de stocul contabil?"
description: "De ce, în arhitectura iConta.eu, stocul din modulul de gestiune și stocul rezultat din conturile contabile sunt două evidențe separate — și de ce nota de inventariere nu le sincronizează automat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce faci dacă stocul scriptic diferă de stocul contabil?

Aparent, "stocul scriptic" ar trebui să fie un singur număr — dar în practică, poate exista un decalaj între ce arată modulul de gestiune a stocurilor și ce arată soldurile conturilor de stoc din contabilitate. Aici e o distincție importantă, onest semnalată, pentru utilizatorii iConta.eu.

## Temeiul legal

::: ghid-temei
"Rezultatul inventarierii se înregistrează în contabilitate potrivit reglementărilor contabile
aplicabile." — Legea 82/1991, art. 7 alin. (3)
:::

Legea cere ca rezultatul inventarierii — diferența dintre stocul faptic (numărat) și cel scriptic — să fie înregistrat în contabilitate. Norma nu presupune însă că "stocul scriptic" e obligatoriu un singur sistem: dacă gestiunea de stoc se ține într-un modul separat de contabilitate (cum e cazul în iConta.eu), pot apărea, teoretic, două valori "scriptic" diferite — una din modulul de gestiune, alta din soldurile conturilor 3xx — dacă cele două evidențe nu sunt actualizate în paralel.

## Ce se greșește în practică

- Se presupune că înregistrarea unei note de inventariere actualizează automat și stocul afișat în modulul de gestiune a stocurilor.
- Se compară stocul faptic doar cu una dintre cele două evidențe (fie doar contabilitatea, fie doar modulul de gestiune), fără să se verifice dacă ele coincid între ele înainte de comparație.

## Ce face iConta.eu

Aici e important de spus deschis o limitare confirmată în cod: ecranul "Inventariere anuală" din iConta.eu (`nota-inventariere`) scrie **doar** în jurnalul contabil și, pentru plusuri de mijloace fixe sau casări, în registrul de mijloace fixe. **Nu apelează modulul de gestiune a stocurilor și nu actualizează mișcările de stoc din acel modul.** Cu alte cuvinte, nota de inventariere rezolvă partea contabilă (soldurile conturilor 3xx), dar **stocul scriptic afișat în modulul de gestiune a stocurilor trebuie actualizat separat, manual**, de contabil sau de gestionar — cele două evidențe nu sunt legate automat printr-un singur document.

Această situație era, la ultima verificare internă disponibilă, deschisă și documentată ca atare; nu putem confirma dacă a fost deja rezolvată la data citirii acestui ghid — dacă lucrați cu stocuri gestionate atât în modulul de gestiune, cât și contabil, verificați ambele evidențe separat după orice notă de inventariere.

[iConta.eu](/)
