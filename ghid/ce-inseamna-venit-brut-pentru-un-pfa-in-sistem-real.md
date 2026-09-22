---
title: Ce înseamnă venit brut pentru un PFA în sistem real?
description: Venitul brut al unui PFA în sistem real cuprinde sumele efectiv încasate din activitate (inclusiv echivalentul veniturilor în natură), dobânzile din creanțe comerciale și câștigurile din transferul activelor din patrimoniul afacerii — nu facturile emise, ci încasările reale.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce înseamnă venit brut pentru un PFA în sistem real?

Venitul brut, în sistem real, nu e valoarea facturilor emise, ci suma efectiv încasată în anul fiscal, legată de activitatea independentă. E un punct important de neînțeles greșit: chiar dacă o factură a fost emisă în decembrie, dacă a fost încasată abia în ianuarie anul următor, ea intră în venitul brut al anului în care a fost încasată.

## Temeiul legal

::: ghid-temei
**Art. 68 alin.(2):** "Venitul brut cuprinde: a) sumele încasate și echivalentul în lei al veniturilor în natură din desfășurarea activității; b) veniturile sub formă de dobânzi din creanțe comerciale...; c) câștigurile din transferul activelor din patrimoniul afacerii...".

**Art. 68 alin.(1):** "Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri, cu excepția situațiilor în care sunt aplicabile prevederile art. 68^1, 68^3 și 69."
:::

## Ce intră și ce nu intră în venitul brut

Conform art. 68 alin. (2), venitul brut include:

- **sumele efectiv încasate** din desfășurarea activității, plus echivalentul în lei al veniturilor în natură (de exemplu bunuri sau servicii primite în loc de bani);
- **dobânzile din creanțe comerciale** legate de activitate;
- **câștigurile din transferul activelor din patrimoniul afacerii** (de exemplu vânzarea unui echipament folosit în activitate).

Ce nu intră: facturi emise dar neîncasate, avansuri primite pentru servicii viitoare care nu au fost încă prestate (tratamentul lor depinde de natura sumei), sau sume care nu au legătură cu activitatea independentă.

## Ce se greșește în practică

- Se raportează venitul brut pe baza facturilor emise, nu a încasărilor efective — greșeală tipică pentru cineva obișnuit cu contabilitatea în partidă dublă.
- Se omit veniturile în natură (bunuri sau servicii primite drept plată), deși legea le include explicit, la echivalentul lor în lei.
- Se confundă o încasare care ține de activitate cu o mișcare de bani personală, needucă în venitul brut al PFA.
- Se include eronat în venitul brut o sumă care de fapt e o restituire de TVA sau un transfer între conturi proprii, fără legătură cu activitatea.

## Ce face iConta.eu

Sursa venitului brut pentru D212 (`core/rip_api.py: fisa_d212`) e suma tuturor operațiunilor de tip "încasare", cu categoria "activitate", care sunt **validate** (au status "validata", adică au document justificativ complet). Operațiunile nevalidate (ciorne) nu intră în venitul brut — sunt doar numărate separat, cu avertisment, ca să știi că mai ai operațiuni de confirmat înainte de a genera declarația. Această abordare pe bază de încasări efective, validate, corespunde exact definiției din art. 68 alin. (2) — sistemul real e construit pe cash, nu pe facturare.

[iConta.eu](/)
