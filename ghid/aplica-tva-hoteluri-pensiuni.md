---
title: Cum se aplică TVA în hoteluri și pensiuni
description: Cazarea și serviciile de restaurant/catering sunt amândouă la cota redusă de 11%, dar cu reguli diferite pentru alcool — la cazare cu masă inclusă, cota redusă acoperă și băuturile alcoolice, la restaurant, alcoolul rămâne mereu la cota standard.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se aplică TVA în hoteluri și pensiuni

Un hotel sau o pensiune facturează, de regulă, mai multe tipuri de servicii sub același acoperiș: cazarea propriu-zisă, micul dejun sau masa inclusă în pachet, și eventual consumația de la restaurantul propriu, facturată separat. Codul fiscal tratează cazarea și restaurantul/cateringul ca două categorii distincte, ambele la cota redusă de 11%, dar cu o diferență importantă la tratamentul băuturilor alcoolice.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „cazarea în cadrul sectorului hotelier sau al sectoarelor cu funcție similară, inclusiv închirierea terenurilor amenajate pentru camping" (art. 291 alin. (2) lit. m) și pentru „serviciile de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202" (art. 291 alin. (2) lit. n) — Codul fiscal.
:::

## Cazarea, inclusiv masa inclusă în pachet

Cazarea simplă, cazarea cu mic dejun, demipensiune, pensiune completă sau all-inclusive intră la cota de 11%. La pachetele care includ masă, cota redusă se aplică **la prețul total al pachetului**, inclusiv băuturile alcoolice servite în cadrul lui — o excepție explicită de la regula generală a alcoolului, valabilă doar pentru pachetul de cazare cu masă inclusă.

## Restaurantul unității, facturat separat

Dacă hotelul are un restaurant propriu și oaspetele consumă acolo în afara pachetului de cazare (de exemplu, cină facturată separat, la liber, nu inclusă în tariful camerei), operațiunea e „serviciu de restaurant" de sine stătător — tot la 11%, dar **cu excepția strictă a băuturilor alcoolice și a celor NC 2202**, care rămân la cota standard de 21%. Aici nu mai funcționează excepția de la pachetul de cazare: alcoolul servit la restaurant, în afara pachetului, e mereu la 21%.

## Distincția-cheie

Regula depinde de ce anume e facturat, nu de locație: dacă suma apare ca parte a tarifului de cazare (pachet cu masă inclusă), cota de 11% acoperă tot, inclusiv alcoolul; dacă suma e o consumație facturată separat de cazare (restaurant la liber), alcoolul iese din cota redusă.

## Ce se greșește în practică

- Se aplică automat regula „alcoolul e mereu la 21%" și la pachetele de cazare cu masă inclusă, deși acolo legea prevede explicit aplicarea cotei reduse la prețul total.
- Invers, se aplică regula pachetului de cazare (alcool la 11%) și la restaurantul facturat separat din afara pachetului — corect este 21% pentru alcool în acest caz.
- Se facturează cazarea și restaurantul pe aceeași linie, fără să se distingă dacă suma e parte din tariful de cazare sau o consumație separată — ceea ce face imposibilă aplicarea corectă a excepției de alcool.

## Ce face iConta.eu

`core/cote_tva.py` ține separat categoria `cazare` (art. 291 alin. (2) lit. m) de categoria `restaurant_catering` (lit. n), fiecare cu regulile ei proprii de excepție. Motorul de potrivire cotă lucrează linie cu linie: o linie de cazare (inclusiv pachet cu masă) primește 11% integral, iar o linie de restaurant/catering primește 11% cu excepția explicită pentru băuturile alcoolice și NC 2202, care rămân la 21%. Distincția rămâne, în ultimă instanță, de felul în care emitentul structurează factura — pe linie de cazare sau pe linie de consumație separată.

[iConta.eu](/)
