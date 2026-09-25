---
title: "Cum corectez un extras bancar înregistrat de două ori?"
description: "Cum se corectează o operațiune bancară dublată în contabilitate, prin stornarea notei de contabilitate, conform normelor OMFP 2.634/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez un extras bancar înregistrat de două ori?

Când același extras — sau aceeași linie dintr-un extras — ajunge înregistrată de două ori, soldul contului de bancă din contabilitate nu mai corespunde cu soldul real. Corectarea nu se face ștergând pur și simplu înregistrarea, ci prin stornare, cu urmă vizibilă în evidență.

## Temeiul legal

::: ghid-temei
„În cazul operațiunilor contabile pentru care nu se întocmesc documente justificative, înregistrările în contabilitate se fac pe bază de note de contabilitate care au la bază note justificative sau note de calcul, după caz. În cazul stornărilor, pe documentul inițial se menționează numărul și data notei de contabilitate prin care s-a efectuat stornarea operațiunii, iar în nota de contabilitate de stornare se menționează documentul, data și numărul de ordine ale operațiunii care face obiectul stornării."
— OMFP nr. 2.634/2015, Norme generale, pct. 20 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Practic, corectarea unei înregistrări duble cere:

- O **notă de contabilitate de stornare**, care anulează exact suma și conturile din înregistrarea dublată — nu o simplă ștergere a operațiunii din sistem, fără urmă.
- Pe **documentul inițial** (extrasul dublat) se menționează numărul și data notei de stornare.
- Pe **nota de stornare** se menționează, la rândul ei, documentul, data și numărul de ordine ale operațiunii pe care o corectează — trasabilitate în ambele sensuri.
- După stornare, soldul contului bancar (5121/5124) revine la valoarea reală, corespunzătoare extrasului efectiv primit de la bancă.

## Ce se greșește în practică

- Se șterge pur și simplu una dintre cele două înregistrări, fără notă de stornare și fără urmă a corecției — ceea ce contravine cerinței de trasabilitate din normă.
- Se corectează doar suma din a doua înregistrare, fără să se verifice dacă soldul contului bancar mai coincide efectiv cu soldul din extrasul original al băncii.
- Se descoperă dublarea abia la reconcilierea de la finalul lunii, deși un extras importat de două ori într-o perioadă scurtă putea fi observat la momentul importului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu detectează automat un extras bancar importat de două ori — fiecare linie e procesată și contabilizată în funcție de conținutul ei, fără o verificare încrucișată cu importurile anterioare pentru duplicate. Corectarea unei înregistrări dublate rămâne, în prezent, o intervenție manuală a contabilului, prin ștergerea notei greșite (posibilă doar cât timp nota e încă ciornă, nu definitivă) sau prin înregistrarea unei note de stornare.

[iConta.eu](/)
