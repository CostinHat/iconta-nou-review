---
title: Ce cotă de TVA se aplică băuturilor vândute într-un restaurant?
description: Băuturile alcoolice și băuturile nealcoolice NC 2202 (sucuri, cola, energizante) rămân la cota standard de 21% chiar servite în restaurant — orice amestec cu alcool e tratat tot ca băutură alcoolică.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce cotă de TVA se aplică băuturilor vândute într-un restaurant?

Spre deosebire de alimente, băuturile dintr-un restaurant nu urmează automat cota de 11% a serviciului de restaurant — legea exclude explicit din categoria redusă băuturile alcoolice și o categorie precisă de băuturi nealcoolice.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică serviciilor de restaurant și de catering „cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202” — Codul fiscal, art. 291 alin. (2) lit. n).
:::

## Care băuturi rămân la cota standard (21%)

- **Băuturile alcoolice** — bere, vin, băuturi spirtoase — indiferent dacă sunt servite la masă sau la pachet.
- **Orice amestec de băutură alcoolică cu băutură nealcoolică**, indiferent de concentrația alcoolică rezultată — se consideră, ca principiu, tot băutură alcoolică.
- **Băuturile nealcoolice încadrate la codul NC 2202** — ape minerale/gazoase îndulcite sau aromatizate, sucuri, băuturi răcoritoare, energizante.

## Care băuturi intră la cota redusă (11%)

Băuturile nealcoolice care **nu** se încadrează la codul NC 2202 — de exemplu apa plată/minerală neîndulcită, cafeaua, ceaiul, laptele — servite ca parte a serviciului de restaurant/catering, urmează cota de 11% a serviciului.

## Ce se greșește în practică

- Se aplică 11% și băuturilor alcoolice, pentru că „sunt servite în restaurant" — greșit, excepția e explicită și nu ține cont de contextul serviciului.
- Se tratează un cocktail cu conținut mic de alcool ca „nealcoolic" — orice amestec cu alcool intră la cota standard, indiferent de concentrație.
- Se aplică din reflex 11% oricărei băuturi nealcoolice, fără verificarea codului NC 2202 pentru sucuri, energizante sau ape aromatizate.

## Ce face iConta.eu

`core/cote_tva.py` listează separat, în `EXCEPTII_21`, categoriile `bauturi_alcoolice` și `bauturi_nc2202`, fiecare cu exemple concrete (bere, vin, vodcă, whisky pentru alcool; cola, suc acidulat, energizant, apă aromatizată pentru NC 2202) — astfel încât o băutură de acest tip primește automat cota standard de 21%, chiar dacă apare pe același bon cu produse de restaurant la 11%.

[iConta.eu](/)
