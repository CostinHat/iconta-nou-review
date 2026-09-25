---
title: "Greșeala de a nu corela e-Factura cu D300 și D394"
description: "De ce corelarea dintre e-Factura, D300 și D394 nu e automată în aplicație, ci depinde de faptul că toate trei pornesc din același registru de facturi."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeala de a nu corela e-Factura cu D300 și D394

E ușor să presupui că, odată ce facturile intră prin e-Factura, D300 și D394 „se potrivesc automat" cu ce a trecut prin sistemul național de facturare electronică. Legătura reală e mai indirectă — și tocmai de aceea merită verificată, nu presupusă.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii şi achiziţiile de bunuri şi servicii realizate pe teritoriul României către/de la orice persoană, aşa cum este definită la art. 266 alin. (1) pct. 24 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare."
— OPANAF 3769/2015, art.1 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt:20-24)
:::

Obligația de declarare în D394 (și, similar, cea de raportare în D300) privește **operațiunile efectiv realizate**, nu doar pe cele care au trecut prin fluxul e-Factura. Facturile primite prin e-Factura sunt o sursă de date, nu singura — orice factură emisă în afara sistemului sau corectată manual după import rămâne, la fel, supusă obligației de declarare.

## Ce se greșește în practică

- Se presupune că, dacă o factură a fost validată și transmisă prin e-Factura, ea „e automat" reflectată corect în D300 și D394 — corectitudinea depinde de cum a fost preluată și prelucrată, nu doar de faptul că a trecut prin sistemul național.
- Se ignoră facturile care nu au trecut deloc prin e-Factura (de exemplu, corectate sau introduse manual) la momentul verificării declarațiilor — acestea nu au un corespondent de confruntat automat.
- Se tratează lipsa unei erori la depunere ca dovadă că e-Factura, D300 și D394 sunt reciproc corelate — o declarație poate fi validă structural (trece de validatorul ANAF) fără ca sursele ei de date să fi fost verificate una față de alta.

## Ce face iConta.eu

D394 se generează din aceleași tabele de facturi (`facturi` + `factura_linii`) populate de importul e-Factura din aplicație (parser UBL 2.1/CIUS-RO, `core/efactura_import.py`) — corelarea dintre e-Factura și D394 e, deci, **structurală**: sursa de date e comună, nu rezultatul unei funcții dedicate de comparare.

Nu există în cod un modul separat care compară explicit ce a generat D394 cu ce a primit sau trimis efectiv sistemul e-Factura. Pentru D300 față de D394 există, doar la nivel de dezvoltare (nu în fluxul de generare folosit de contabil), un gard intern (`core/test_d300_d394_paritate.py`) care confruntă cele două calcule pe cotă — dar chiar acest gard e documentat în cod ca tautologic, fiindcă ambele generatoare citesc aceleași linii de factură și deduc cota identic, deci prinde doar o divergență între generatoare, nu o eroare reală de conținut; la generarea efectivă a declarațiilor nu rulează nicio comparație automată D300↔D394. Practic, asta înseamnă că D300 și D394 „se potrivesc" de obicei cu ce arată e-Factura tocmai pentru că pornesc din aceeași bază de facturi — dar limita reală e la facturile care nu au trecut prin importul e-Factura sau care au fost corectate manual după import: acestea nu sunt reconfirmate automat împotriva e-Factura de nicio funcție din aplicație, deci verificarea lor rămâne o responsabilitate manuală a contabilului.

[iConta.eu](/)
