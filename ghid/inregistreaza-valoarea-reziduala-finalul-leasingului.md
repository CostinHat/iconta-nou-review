---
title: "Cum se înregistrează valoarea reziduală la finalul leasingului financiar?"
description: "Valoarea reziduală închide contul de datorie 167 față de societatea de leasing (167=404, cu TVA pe 4426) — bunul rămâne deja recunoscut de la primire."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează valoarea reziduală la finalul leasingului financiar?

Valoarea reziduală e, practic, ultima plată pe care locatarul o face pentru a „cumpăra" definitiv bunul preluat prin leasing financiar — o sumă stabilită încă de la începutul contractului, nu o operațiune surpriză de la final.

## Temeiul legal

::: ghid-temei
„213. ‐ (1) [...] a) contract de leasing este un acord prin care locatorul cedează locatarului, în schimbul unei plăți sau serii de plăți, dreptul de a utiliza un bun pentru o perioadă stabilită; [...] (2) Un contract de leasing este recunoscut ca leasing financiar dacă îndeplinește cel puțin una dintre următoarele condiții: [...] b) locatarul are opțiunea de a cumpăra bunul la un preț estimat a fi suficient de mic [...]."
— OMFP 1802/2014, pct. 213 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

- Valoarea reziduală face parte, alături de avans și de ratele de capital, din valoarea totală a bunului recunoscută **de la primire** — nu se adaugă separat la finalul contractului.
- La final, plata ei stinge datoria față de societatea de leasing: contul 167 se închide prin 167=404, cu TVA calculată pe valoarea reziduală, la fel ca pe orice altă rată.
- Bunul propriu-zis (2133) nu se mai modifică la acest pas — a fost deja recunoscut integral, la intrare, conform OMFP pct. 214-215.

## Ce se greșește în practică

- Se omite includerea valorii reziduale în valoarea totală recunoscută la intrarea bunului (2133=167) — ea trebuie inclusă încă de la primire, nu adăugată ulterior.
- Se tratează plata valorii reziduale ca o nouă achiziție (o altă intrare pe 2133), deși bunul e deja înregistrat integral, de la începutul contractului.
- Se omite TVA-ul pe valoarea reziduală, considerând-o greșit o simplă „ultimă rată" fără regim fiscal propriu.

## Ce face iConta.eu

Funcția `nota_reziduala` din F056 (Leasing financiar și operațional) închide exact contul 167, la valoarea reziduală plătită, cu TVA pe 4426 (167=404 + 4426=404) — testată unitar în aplicație (de exemplu, valoare reziduală 278,15 lei → TVA 58,41 lei la cota de 21%). Notă: la data acestui ghid, ecranul „Leasing" nu colectează câmpul de cotă TVA pentru acest tip de operațiune („Valoare reziduală"), deci trimiterea ei din interfață eșuează azi cu eroare de validare, deși motorul de calcul o produce corect.

[iConta.eu](/)
