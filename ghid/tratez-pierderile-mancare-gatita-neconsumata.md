---
title: "Cum tratez pierderile din mâncare gătită neconsumată"
description: "Explică distincția fiscală dintre pierderea tehnologică din bucătărie și perisabilitatea mărfurilor de comercializare, plus regula de TVA la bunuri distruse."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez pierderile din mâncare gătită neconsumată

Mâncarea preparată și neconsumată, rezultată dintr-un proces de preparare culinară, se încadrează legal altfel decât marfa cumpărată și revândută ca atare — distincția contează pentru alegerea temeiului corect.

## Temeiul legal

::: ghid-temei
"Următoarele cheltuieli au deductibilitate limitată: [...] d) scăzămintele, perisabilitățile, pierderile rezultate din manipulare/depozitare, potrivit legii; e) pierderile tehnologice care sunt cuprinse în norma de consum proprie necesară pentru fabricarea unui produs sau prestarea unui serviciu;"
— Codul fiscal (Legea 227/2015), art. 25 alin. (3) lit. d)-e), `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F066.

"(2) Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă. [...]"
— Codul fiscal (Legea 227/2015), art. 304 alin. (2) lit. a), `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F066.
:::

Mâncarea gătită și neconsumată e, de regulă, rezultatul unui proces de preparare (fabricare/prestare) — încadrarea legală mai potrivită e pierderea tehnologică (lit. e), justificată printr-o normă de consum proprie a firmei, nu perisabilitatea de comercializare (lit. d), al cărei temei (HG 831/2004) vizează explicit mărfurile vândute ca atare, nu ingredientele transformate în bucătărie. Indiferent de încadrare însă, dacă pierderea (bunul distrus) e dovedită corespunzător, art. 304 alin. (2) lit. a) scutește de obligația de a ajusta TVA-ul deja dedus la achiziția ingredientelor — regula se aplică la nivel de lege, nu doar sub umbrela HG 831/2004.

## Ce se greșește în practică

Greșeala frecventă e aplicarea automată a unui procent de perisabilitate HG 831/2004 pe mâncarea gătită, ca și cum ar fi marfă comercializată nemodificat — temeiul corect e mai degrabă norma de consum proprie, nu tabelul HG 831/2004. A doua greșeală e ajustarea automată a TVA-ului dedus la achiziția ingredientelor, chiar și atunci când pierderea/distrugerea e dovedită corespunzător — deși legea scutește exact acest caz de la ajustare.

## Ce face iConta.eu

iConta.eu nu are un modul dedicat calculului sau limitării unei norme de consum proprii pentru pierderi tehnologice din bucătărie — căutat explicit în codul de producție (`core/productie.py`) și de rețete (`core/retete.py`), fără nicio logică de acest tip. Modulul de rețete al aplicației (F076) tratează doar consumul normal de ingrediente la vânzarea unei porții, nu risipa sau pierderea. Pentru marfa cumpărată și revândută ca atare (de exemplu băuturi îmbuteliate), motorul de perisabilități (`core/perisabilitati.py`, HG 831/2004) rămâne aplicabil — dar pentru mâncarea gătită și neconsumată, justificarea corectă rămâne documentarea internă a normei de consum, în afara automatizărilor aplicației.

[iConta.eu](/)
