---
title: "TVA pentru restaurante 2026: cota aplicabilă"
description: Fișă rapidă — servicii de restaurant/catering 11%, băuturi alcoolice și NC 2202 21%, mâncare la pachet fără servicii conexe = livrare de bunuri la cota alimentului. Reguli valabile neschimbat tot 2026.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# TVA pentru restaurante 2026: cota aplicabilă

Pe scurt, pentru un restaurant sau un serviciu de catering, în 2026 se aplică practic trei cote diferite, în funcție de ce se vinde și cum:

| Ce se vinde | Cotă TVA | Temei |
|---|---|---|
| Meniu servit la masă (mâncare, ca serviciu de restaurant) | 11% | Art. 291 alin. (2) lit. n) |
| Băuturi nealcoolice servite la masă (altele decât NC 2202) | 11% | Art. 291 alin. (2) lit. n) |
| Băuturi alcoolice (servite la masă sau la pachet) | 21% | Art. 291 alin. (2) lit. n) — excepție |
| Băuturi nealcoolice NC 2202 (sucuri, cola, energizante) | 21% | Art. 291 alin. (2) lit. n) — excepție |
| Mâncare la pachet, fără servicii conexe (livrare de bunuri) | cota alimentului (de regulă 11%) | Art. 291 alin. (2) lit. b) |

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică „serviciilor de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202” — Codul fiscal, art. 291 alin. (2) lit. n), în vigoare de la 1 august 2025 (Legea 141/2025).
:::

## Regula pe scurt

Un serviciu de restaurant/catering (mâncare + servicii conexe pentru consum imediat, în local sau la eveniment) intră la 11%, cu excepția explicită a băuturilor alcoolice și a celor NC 2202, care rămân la 21% chiar servite la masă. Dacă alimentele/băuturile se vând la pachet, fără servicii conexe, operațiunea devine livrare de bunuri, nu serviciu de restaurant, iar cota o dă produsul livrat (de regulă 11% pentru alimente, cu excepțiile lor proprii — zahăr, alcool, NC 2202).

Aceste reguli sunt valabile neschimbat pe tot cursul lui 2026 — nicio modificare legislativă din acest an nu a atins cotele de TVA (OUG 8/2026 a schimbat doar alte praguri fiscale, nu art. 291).

## Ce se greșește în practică

Cea mai des întâlnită greșeală e aplicarea unei singure cote pe tot bonul unui restaurant, fără separare pe linii — de obicei se pierde din vedere excepția băuturilor alcoolice/NC 2202, care rămân la 21% chiar dacă tot restul consumației e la 11%.

## Ce face iConta.eu

Categoriile `restaurant_catering` (11%) și excepțiile `bauturi_alcoolice`/`bauturi_nc2202` (21%) din `core/cote_tva.py` sunt aplicate automat, pe fiecare linie de bon sau factură, prin motorul de potrivire cotă — astfel încât un meniu de restaurant și o băutură alcoolică vândute pe același document primesc fiecare cota lui corectă, fără intervenție manuală.

[iConta.eu](/)
