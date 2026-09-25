---
title: "Cum corectez o chitanță înregistrată de două ori?"
description: "Ce prevede legea pentru corectarea unei duble înregistrări de numerar — stornare, nu ștergere — și ce oferă azi iConta.eu pentru chitanțele deja emise."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez o chitanță înregistrată de două ori?

Aceeași încasare ajunge, din greșeală, înregistrată de două ori — o dată la emiterea propriu-zisă și încă o dată la reintroducerea manuală, sau pur și simplu prin dublă apăsare. Rezultatul e o sumă în plus în Registrul de casă și în contabilitate, care trebuie anulată corect, nu doar „ștearsă".

## Temeiul legal

::: ghid-temei
„În cazul operațiunilor contabile pentru care nu se întocmesc documente justificative, înregistrările în contabilitate se fac pe bază de note de contabilitate care au la bază note justificative sau note de calcul, după caz. În cazul stornărilor, pe documentul inițial se menționează numărul și data notei de contabilitate prin care s-a efectuat stornarea operațiunii, iar în nota de contabilitate de stornare se menționează documentul, data și numărul de ordine ale operațiunii care face obiectul stornării."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 20 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

- Corecția unei duble înregistrări nu se face prin ștergerea pur și simplu a rândului din contabilitate, ci prin **stornare** — o notă de contabilitate separată, care anulează efectul înregistrării greșite.
- Nota de stornare trebuie să facă trimitere explicită la documentul inițial (numărul și data operațiunii stornate), iar pe documentul inițial se menționează, la rândul lui, numărul și data notei de stornare — o legătură bidirecțională, verificabilă ulterior.
- Chitanța însăși — documentul de hârtie sau PDF — nu se modifică retroactiv; ceea ce se corectează e înregistrarea contabilă/de casă dublă generată de ea, prin operațiunea de stornare descrisă mai sus.

## Ce se greșește în practică

- Se șterge direct a doua înregistrare din Registrul de casă, fără nicio notă de stornare care să documenteze corecția — la control, dispariția unei operațiuni fără urmă e mai greu de justificat decât o stornare vizibilă.
- Se anulează greșit prima înregistrare (cea corectă) în loc de duplicat, pentru că nu s-a verificat cu atenție care dintre cele două corespunde exact documentului real.
- Se presupune că simpla corectare a soldului de casă e suficientă, fără să se actualizeze și eventuala factură legată de chitanța dublată, care poate rămâne greșit marcată ca plătită de două ori.

## Ce face iConta.eu

Verificat în cod: `chitanta_emite` alocă, la fiecare apel, strict numărul următor din serie (`urmatorul_numar_chitanta`), fără nicio verificare de duplicat față de chitanțe existente, și nu există în modulul de chitanțe nicio funcție de corectare, ștergere sau stornare a unui rând deja creat în tabela de chitanțe. Dacă aceeași încasare a fost emisă de două ori din greșeală, iConta.eu nu oferă azi un buton dedicat de corecție — cele două chitanțe rămân, ambele, active în listă și în Registrul de casă, iar remedierea (inclusiv nota de stornare descrisă mai sus) trebuie făcută manual, în afara aplicației.

[iConta.eu](/)
