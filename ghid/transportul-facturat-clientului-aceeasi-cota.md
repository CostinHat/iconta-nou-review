---
title: Transportul facturat clientului are aceeași cotă TVA ca produsul?
description: Depinde dacă transportul e prestat de sine stătător sau e accesoriu unei livrări proprii de bunuri — doar în al doilea caz urmează cota produsului transportat; ca serviciu independent, are propria cotă, de regulă 21%.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Transportul facturat clientului are aceeași cotă TVA ca produsul?

Răspunsul nu e „da" în toate cazurile, nici „nu" în toate cazurile — depinde de relația dintre transport și livrarea de bunuri pe care o însoțește. Există două situații distincte, cu tratament de TVA diferit.

## Temeiul legal

::: ghid-temei
„Baza de impozitare cuprinde [...] cheltuielile accesorii, cum sunt: comisioanele, cheltuielile de ambalare, transport și asigurare, solicitate de către furnizor/prestator cumpărătorului sau beneficiarului. Cheltuielile facturate de furnizorul de bunuri sau de prestatorul de servicii cumpărătorului, care fac obiectul unui contract separat și care sunt legate de livrările de bunuri sau de prestările de servicii în cauză, se consideră cheltuieli accesorii.” — Codul fiscal, art. 286 alin. (3) lit. b).
:::

## Cele două situații

**1. Transportul e accesoriu unei livrări de bunuri proprii.** Dacă tu, ca furnizor, vinzi un produs și recuperezi de la client costul transportului aceluiași produs (livrat de tine sau în numele tău), transportul intră în baza de impozitare a livrării, ca cheltuială accesorie — deci **urmează cota produsului transportat**. Nu se facturează separat, la cotă proprie, ci se include (sau se evidențiază la aceeași cotă) în valoarea livrării.

**2. Transportul e un serviciu de sine stătător.** Dacă transportul e prestat independent — de exemplu, de o firmă de transport care nu are legătură cu o livrare de bunuri proprie a emitentului — este o prestare de servicii separată, cu **cotă proprie**. Transportul de mărfuri sau persoane nu apare pe lista limitativă a cotei reduse (art. 291 alin. (2)), deci, ca regulă, se facturează la **cota standard de 21%**.

## Cum distingi practic

Întrebarea-cheie: transportul cade contractual în sarcina furnizorului bunurilor și se recuperează de la același client, ca parte a aceleiași tranzacții comerciale? Dacă da — accesoriu, urmează cota bunului. Dacă transportul e prestat de un terț independent sau facturat ca serviciu autonom, fără legătură cu o livrare proprie — cotă proprie de transport, de regulă 21%.

## Ce se greșește în practică

- Se facturează transportul mereu la 21%, chiar și când e strict accesoriu unei livrări de bunuri la cotă redusă (11%) — caz în care ar trebui să urmeze cota bunului.
- Se aplică automat cota bunului transportat și pentru un serviciu de transport prestat independent, fără legătură contractuală cu o livrare proprie a emitentului — greșit, acesta e un serviciu de sine stătător.
- Se ignoră condiția „facturat către același client, ca parte a aceleiași tranzacții" — regula accesoriului nu se aplică oricărui transport, ci doar celui legat direct de livrarea proprie.

## Ce face iConta.eu

Motorul de potrivire cotă (`core/cote_tva.py`) clasifică transportul, implicit, alături de consultanță, IT și chirii comerciale, ca „serviciu obișnuit" — la cota standard de 21%. Distincția dintre transportul accesoriu unei livrări proprii (care ar trebui să urmeze cota bunului) și transportul ca serviciu independent nu e modelată automat în motor — la facturarea unui transport legat direct de o livrare proprie de bunuri, cota corectă (cea a bunului) se declară manual, aplicând regula de la art. 286 alin. (3) lit. b).

[iConta.eu](/)
