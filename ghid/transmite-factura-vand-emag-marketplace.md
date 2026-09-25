---
title: "Cine transmite e-Factura când vând prin eMAG Marketplace"
description: "Dacă obligația de transmitere a facturii în RO e-Factura, la o vânzare printr-un marketplace, revine vânzătorului sau platformei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cine transmite e-Factura când vând prin eMAG Marketplace

Legea leagă obligația de transmitere în RO e-Factura de calitatea de "operator economic – persoană impozabilă stabilită în România" care efectuează livrarea de bunuri sau prestarea de servicii, nu de platforma prin care se derulează tranzacția. Sursele disponibile nu conțin o prevedere specifică marketplace-urilor tip eMAG, iar acolo unde legea nu transează explicit un caz particular, principiul general e cel care se aplică: obligația rămâne a furnizorului efectiv al bunurilor, nu a intermediarului tehnic.

## Temeiul legal

::: ghid-temei
„În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Ordonanța de urgență nr. 120/2021, art. 10 alin. (1), astfel cum a fost modificat prin Legea nr. 296/2023 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

- **Obligația legală vizează persoana impozabilă care efectuează livrarea de bunuri sau prestarea de servicii** — la o vânzare prin marketplace, aceasta e, de regulă, vânzătorul înscris pe platformă (SRL-ul care listează produsul), nu operatorul platformei, cu excepția situațiilor în care platforma însăși vinde bunuri în nume propriu.
- **Textul de lege nu conține o excepție sau o regulă specială pentru vânzările prin marketplace** — deci se aplică regula generală: cine emite factura (vânzătorul, identificat ca atare în relația contractuală cu cumpărătorul) e cel obligat să o transmită și în RO e-Factura.
- **Relația comercială efectivă contează**, nu doar canalul tehnic prin care circulă comanda — dacă vânzătorul emite factura direct către clientul final, chiar dacă tranzacția e intermediată tehnic de platformă, obligația RO e-Factura rămâne a vânzătorului, pentru relațiile B2B.

## Ce se greșește în practică

- Se presupune că platforma de marketplace preia automat obligația de raportare fiscală a vânzătorului, doar pentru că intermediază plata și livrarea — legea nu transferă obligația de emitere/transmitere a facturii către operatorul platformei.
- Se ignoră obligația RO e-Factura pentru vânzările B2B derulate prin marketplace, considerând regimul identic cu vânzările B2C către persoane fizice, care au alte reguli de facturare.
- Se confundă facturarea comisionului reținut de platformă (unde platforma e furnizorul serviciului de intermediere către vânzător) cu facturarea bunului vândut către clientul final (unde vânzătorul rămâne furnizorul) — sunt două relații de facturare distincte, fiecare cu propriul obligat la transmitere.

## Ce face iConta.eu

Modulele de facturare și e-Factura din iConta.eu (`core/efactura_send.py`, `core/efactura_trimitere.py`) transmit facturile emise de utilizatorul aplicației (vânzătorul) în sistemul RO e-Factura, indiferent de canalul de vânzare — aplicația nu are o integrare directă cu platformele de marketplace pentru preluarea automată a comenzilor, generarea facturilor pentru vânzările prin eMAG Marketplace sau altele similare rămânând un proces manual al utilizatorului, pe baza rapoartelor de vânzări primite de la platformă.

[iConta.eu](/)
