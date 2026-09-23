---
title: "TVA la brunch-ul cu băuturi incluse: cum se aplică cotele"
description: Un brunch la preț fix, cu băuturi incluse, servit la restaurant, se defalcă pe TVA — mâncarea și băuturile nealcoolice care nu se încadrează la NC 2202 intră la 11%, băuturile alcoolice și cele NC 2202 rămân la 21%, indiferent de prețul unic afișat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# TVA la brunch-ul cu băuturi incluse: cum se aplică cotele

Un meniu de brunch la preț fix, cu mâncare și băuturi incluse, e un serviciu de restaurant — și beneficiază de cota redusă de 11%. Excepția de la această cotă vizează însă strict băuturile: alcoolul și băuturile nealcoolice de la codul NC 2202 rămân la 21%, chiar dacă sunt „incluse" într-un preț unic afișat pentru tot pachetul.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „serviciile de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202" — Codul fiscal, art. 291 alin. (2) lit. n).
:::

## Regula pentru un brunch la restaurant

Mâncarea servită ca parte a brunch-ului (inclusiv un desert dulce, indiferent de conținutul de zahăr — excepția de zahăr ține de livrarea de bunuri, nu de serviciul de restaurant) și băuturile nealcoolice care nu se încadrează la NC 2202 (de exemplu, cafea, ceai, sucuri proaspete presate care nu intră la acest cod) intră integral la cota de 11%. Băuturile alcoolice (mimoze, prosecco, cocktailuri) și băuturile de la NC 2202 rămân la cota standard de 21%, chiar dacă apar în meniul brunch-ului la un preț unic, „all inclusive" pe partea de băutură.

Legea nu prevede, pentru serviciul de restaurant, excepția valabilă la cazarea cu masă inclusă — unde prețul total al pachetului acoperă și alcoolul la cotă redusă. Acea excepție e specifică pachetelor de cazare (demipensiune, pensiune completă, all-inclusive hotelier), nu se extinde la un brunch de restaurant vândut separat de cazare.

## Cum se defalcă pe factură/bon

Dacă brunch-ul se vinde la un preț fix care include și băuturi alcoolice/NC 2202, prețul trebuie defalcat pe cote: partea de mâncare și băuturi nealcoolice (altele decât NC 2202) la 11%, partea de alcool/NC 2202 la 21%. Defalcarea se face pe baza costului sau a valorii de piață estimate a fiecărei componente, nu prin aplicarea unei cote unice pe tot prețul.

## Ce se greșește în practică

- Se aplică 11% pe tot prețul brunch-ului, inclusiv pe partea de alcool inclus, pornind de la asemănarea cu pachetul de cazare all-inclusive — regula de la cazare nu se aplică la restaurant.
- Se aplică 21% pe toată consumația, inclusiv pe mâncare, din prudență excesivă — mâncarea servită la masă rămâne la 11%, doar băuturile din excepție ies la cotă standard.
- Se ignoră codul NC 2202 pentru băuturile nealcoolice îndulcite/aromatizate incluse în brunch, tratându-le automat ca „nealcoolice, deci 11%" — cota depinde de încadrarea NC, nu doar de absența alcoolului.

## Ce face iConta.eu

`core/cote_tva.py` tratează categoria `restaurant_catering` la 11%, cu excepțiile din `EXCEPTII_21` pentru băuturi alcoolice și băuturi NC 2202, potrivite pe fiecare linie a facturii sau a bonului. Pentru un pachet cu preț unic care combină componente la cote diferite (mâncare + alcool inclus), defalcarea pe linii separate, cu cota corectă pentru fiecare, rămâne o decizie a emitentului la structurarea facturii — aplicația nu presupune automat o singură cotă pentru tot pachetul.

[iConta.eu](/)
