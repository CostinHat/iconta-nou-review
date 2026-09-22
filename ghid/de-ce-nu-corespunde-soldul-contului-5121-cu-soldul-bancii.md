---
title: De ce nu corespunde soldul contului 5121 cu soldul băncii?
description: Legea cere confruntarea soldurilor din extrasul de cont cu contabilitatea la inventariere; o diferență între soldul 5121 și soldul bancar poate proveni din comisioane, dobânzi, viramente interne sau linii de extras neimportate/necontate, cauze pe care motorul de matching din F073 nu le acoperă complet.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# De ce nu corespunde soldul contului 5121 cu soldul băncii?

O diferență între soldul contului 5121 din contabilitate și soldul afișat de bancă e una dintre cele mai frecvente surse de neliniște la închiderea lunii. Vestea bună: aproape întotdeauna diferența are o cauză identificabilă, care nu ține de o eroare a motorului de matching, ci de operațiuni care pur și simplu nu au trecut încă (sau nu trec deloc) prin fluxul de reconciliere pe facturi.

## Temeiul legal

::: ghid-temei
**29. - (2)** Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității. În acest scop, extrasele de cont din ziua de 31 decembrie sau din ultima zi bancară, puse la dispoziție de instituțiile de credit și unitățile Trezoreriei Statului, vor purta ștampila oficială a acestora.

Contul 512 "Conturi curente la bănci" [...] este un cont bifuncțional. În debitul contului 512 [...] se înregistrează: [...] – sumele încasate de la clienți (411, 413); [...] În creditul contului 512 [...] se înregistrează: [...] – plățile efectuate către furnizori de bunuri și servicii, inclusiv prin intermediul efectelor comerciale (401, 403, 404, 405); [...] Soldul debitor reprezintă disponibilitățile în lei și în valută, iar soldul creditor creditele primite.
:::

## Ce poate cauza diferența

Motorul de matching din F073 (`core/reconciliere.py` + `core/reconciliere_api.py`) potrivește exclusiv linii de extras pe facturi deschise, pe baza CUI-ului partenerului. Nu calculează și nu compară un sold total de cont cu soldul bancar. O discrepanță reală de sold poate veni din cauze complet din afara acestui motor:

- comisioane bancare (cont 627), care apar în extras dar nu sunt legate de nicio factură;
- dobânzi încasate sau plătite (766/666/518);
- viramente interne între conturile proprii ale firmei (581);
- operațiuni fără factură asociată — avansuri, restituiri, cecuri neîncasate încă (cont 511);
- linii de extras pur și simplu neimportate sau necontate încă (status "nou" în evidența liniilor de extras).

Verificarea corectă nu se face comparând doar liniile alocate de motorul de matching, ci confruntând fișa completă de cont 5121 cu extrasul bancar complet al perioadei, așa cum cere textul citat mai sus.

## Ce se greșește în practică

- Se presupune că orice diferență de sold e o eroare a motorului de matching, deși motorul nu acoperă comisioane, dobânzi sau viramente interne.
- Se compară soldul 5121 din balanță cu soldul bancar fără să se verifice mai întâi dacă toate liniile din extras au fost importate și contate.
- Se ignoră liniile cu status "nou" — extras importat, dar linia încă neprocesată prin matching.
- Se omit operațiunile fără factură (avansuri, restituiri) din analiza diferenței, deși ele afectează direct soldul 512.

## Ce face iConta.eu

`core/reconciliere.py` și `core/reconciliere_api.py` potrivesc doar liniile de extras care au un CUI identificat și o factură deschisă corespunzătoare — rezultatul e clasificat verde (potrivire exactă), galben (alocare parțială, necesită confirmare) sau roșu (fără CUI sau fără factură deschisă a partenerului). Contarea (`conteaza`) generează înregistrarea contabilă doar pentru liniile alocate, folosind formula debit 5121/5124 – credit 4111 la încasare, respectiv debit 401 – credit 5121/5124 la plată.

Sistemul nu calculează și nu afișează automat o comparație agregată "sold 5121 vs. sold extras bancar" — pentru asta rămâne necesară verificarea fișei de cont 5121 complete, inclusiv operațiunile care nu trec prin acest motor de matching.

[iConta.eu](/)
