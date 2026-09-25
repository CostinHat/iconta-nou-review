---
title: "Cheltuielile de protocol reduc impozitul micro?"
description: "De ce cheltuielile de protocol nu au niciun efect asupra impozitului pe veniturile microîntreprinderilor, spre deosebire de regula de la impozitul pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cheltuielile de protocol reduc impozitul micro?

Răspunsul scurt este nu, iar motivul ține de însăși structura impozitului pe veniturile microîntreprinderilor: spre deosebire de impozitul pe profit, unde cheltuielile deductibile (inclusiv cele de protocol, în limita legală) se scad din baza impozabilă, la regimul micro baza de calcul este formată din venituri, nu din profit. Cheltuielile firmei, indiferent de natura lor, nu intră în formulă.

## Temeiul legal

::: ghid-temei
„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie **veniturile din orice sursă**, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile aferente costurilor serviciilor în curs de execuție; c) veniturile din producția de imobilizări corporale și necorporale; d) veniturile din subvenții; [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 53 alin. (1), Titlul III „Impozitul pe veniturile microîntreprinderilor" (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Observația esențială: lista de scăderi din art. 53 alin. (1) conține exclusiv **venituri** (venituri aferente costurilor stocurilor, venituri din subvenții, venituri din diferențe de curs valutar etc.) — nicio literă a acestui articol nu permite scăderea vreunei **cheltuieli**, indiferent de tipul ei. Cheltuielile de protocol nu apar și nu ar putea apărea în această listă, pentru că nu sunt venituri.

Consecințe practice:

- Impozitul pe veniturile microîntreprinderilor se calculează prin aplicarea cotei de 1% (potrivit art. 51 alin. (1), în forma în vigoare de la 1 ianuarie 2026) direct asupra veniturilor totale, ajustate doar cu elementele enumerate la art. 53 — niciodată cu cheltuielile.
- O firmă la regim micro nu are, așadar, niciun stimulent fiscal să limiteze sau să optimizeze cheltuielile de protocol din perspectiva impozitului pe venit — acestea influențează doar profitul contabil și disponibilul de numerar, nu baza de impozitare.
- Situația e diferită la impozitul pe profit, unde cheltuielile de protocol sunt deductibile în limita a 2% aplicată asupra unei baze de calcul specifice (diferența dintre veniturile și cheltuielile înregistrate, ajustată) — acolo, da, cheltuiala de protocol reduce, în limita legală, baza impozabilă.

## Ce se greșește în practică

- Se aplică, din obișnuință, raționamentul de la impozitul pe profit („protocolul e deductibil în limita a 2%") și la firme la regim micro, unde acest concept nu are corespondent.
- Se urmărește plafonul de 2% pentru cheltuielile de protocol la o firmă micro, deși acest plafon nu are relevanță fiscală pentru ea — poate fi relevant doar dacă firma trece ulterior la impozit pe profit.
- Se presupune că orice cheltuială „excesivă" (inclusiv protocolul) afectează automat impozitul datorat, ignorând că la micro impozitul depinde exclusiv de venituri.

## Ce face iConta.eu

Pentru acest subiect nu am identificat în cod un modul specific care să trateze diferit cheltuielile de protocol în funcție de regimul de impozitare (micro vs. profit) — nu am găsit, în fișierele verificate, o funcție dedicată calculului plafonului de 2% pentru protocol sau unei distincții explicite legate de acest subiect între cele două regimuri de impozitare a firmelor.

[iConta.eu](/)
