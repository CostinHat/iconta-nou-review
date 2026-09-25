---
title: "Ce înseamnă eroarea de identificare a cumpărătorului în e-Factura?"
description: "Ce date de identificare a beneficiarului sunt obligatorii pe o factură, potrivit Codului fiscal, și de ce lipsa sau incorectitudinea lor generează erori la validarea în sistemul RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce înseamnă eroarea de identificare a cumpărătorului în e-Factura?

Atunci când sistemul RO e-Factura respinge o factură pentru „eroare de identificare a cumpărătorului", motivul de fond nu e o particularitate tehnică a SPV, ci o cerință veche și clară a Codului fiscal: datele de identificare ale beneficiarului sunt un element obligatoriu al oricărei facturi, iar sistemul electronic doar aplică automat această regulă.

## Temeiul legal

::: ghid-temei
„Factura cuprinde în mod obligatoriu următoarele informații: [...] denumirea/numele și adresa beneficiarului bunurilor sau serviciilor, precum și codul de înregistrare în scopuri de TVA sau codul de identificare fiscală al beneficiarului, dacă acesta este o persoană impozabilă ori o persoană juridică neimpozabilă [...]"
— Legea 227/2015, art. 319 alin. (20) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Onest, despre limitele acestei surse pentru întrebarea concretă:

- Codul fiscal stabilește **obligația de fond**: factura trebuie să conțină denumirea, adresa și codul de identificare fiscală (CIF sau cod de TVA) al cumpărătorului, atunci când acesta e persoană impozabilă sau juridică neimpozabilă.
- Sursele disponibile pentru acest ghid **nu conțin textul tehnic** al codurilor de eroare afișate concret de sistemul RO e-Factura la validare (de tipul unor coduri de eroare BR-RO specifice) — acele reguli de validare sunt stabilite prin specificațiile tehnice RO_CIUS și prin regulile operaționale ale sistemului, menționate în OUG 120/2021 doar ca principiu (structura facturii respectă „specificațiile tehnice și de utilizare a elementelor de bază ale facturii electronice – RO_CIUS"), nu detaliate cu conținutul exact al fiecărei erori de validare.
- Ce se poate confirma cu certitudine: o „eroare de identificare a cumpărătorului" înseamnă, la bază, că una dintre informațiile obligatorii de la art. 319 alin. (20) — denumire, adresă sau cod de identificare fiscală — lipsește, e incompletă sau nu corespunde formatului așteptat (de exemplu CIF inexistent sau nevalid la data facturii).

## Ce se greșește în practică

- Se tratează eroarea de identificare ca fiind exclusiv tehnică, specifică SPV, fără să se verifice mai întâi datele de bază ale cumpărătorului din contractul sau comanda originală — cauza reală e, de cele mai multe ori, o simplă neconcordanță cu datele obligatorii de la art. 319.
- Se introduce CIF-ul cumpărătorului fără prefixul „RO" acolo unde e cerut (pentru plătitorii de TVA), sau invers, generând erori de format la validare.
- Se presupune că adresa cumpărătorului e opțională pe factură, deși legea o cere explicit alături de denumire și codul de identificare fiscală, ca element obligatoriu.

## Ce face iConta.eu

La emiterea unei facturi, iConta.eu citește datele emitentului și ale cumpărătorului (din profilul terțului asociat facturii) și construiește XML-ul UBL 2.1/CIUS-RO pentru transmiterea prin RO e-Factura (`core/efactura_send.py`, `core/efactura_trimitere.py`). Dacă transmiterea eșuează, aplicația distinge explicit între o eroare de structură a facturii și o eroare de drept de acces asupra CIF-ului/serviciului (cod 403), și afișează mesajul de eroare integral primit de la SPV. iConta.eu **nu validează independent**, înainte de trimitere, corectitudinea codului de identificare fiscală al cumpărătorului față de Registrul contribuabililor — corectarea datelor de identificare ale cumpărătorului, în urma unei erori semnalate de SPV, rămâne o intervenție manuală a contabilului pe profilul terțului.

[iConta.eu](/)
