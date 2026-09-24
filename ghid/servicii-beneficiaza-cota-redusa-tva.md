---
title: Ce servicii beneficiază de cotă redusă de TVA în 2026?
description: Cota de 11% se aplică unei liste limitative de servicii — apă/canalizare, servicii agricole, acces cultural, servicii sociale, cazare, restaurant și catering — fiecare cu condițiile ei exacte din Codul fiscal.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce servicii beneficiază de cotă redusă de TVA în 2026?

Ca și la produse, cota redusă de 11% se aplică serviciilor doar dacă acestea se regăsesc explicit în lista limitativă de la art. 291 alin. (2) din Codul fiscal. Un serviciu care nu apare pe listă rămâne la cota standard de 21%, chiar dacă e considerat „de interes general".

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „cazarea în cadrul sectorului hotelier sau al sectoarelor cu funcție similară, inclusiv închirierea terenurilor amenajate pentru camping” și pentru „serviciile de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202” — Codul fiscal, art. 291 alin. (2) lit. m) și n).
:::

## Serviciile de pe lista redusă (11%)

- **Alimentarea cu apă și canalizarea** (lit. c).
- **Servicii agricole** de tipul celor utilizate în mod normal în producția agricolă, prevăzute prin ordin comun al ministrului finanțelor și al ministrului agriculturii (lit. e).
- **Accesul la castele, muzee, case memoriale, monumente istorice, monumente de arhitectură și arheologice, grădini zoologice și botanice** (lit. h).
- **Serviciile sociale** prestate de furnizori acreditați, prevăzute în Nomenclatorul serviciilor sociale — HG 867/2015 (lit. k pct. 4).
- **Cazarea** în sectorul hotelier sau sectoare similare, inclusiv camping (lit. m).
- **Serviciile de restaurant și de catering** — cu excepția băuturilor alcoolice și a băuturilor nealcoolice NC 2202 (lit. n).

## Ce înseamnă exact „serviciu de restaurant/catering"

Furnizarea de alimente și/sau băutură devine „serviciu" — deci eligibilă pentru 11% — doar dacă e însoțită de servicii conexe suficiente pentru consumul imediat (masă servită, personal, spațiu de consum), în spațiile prestatorului (restaurant) sau în afara lor (catering). Livrarea de alimente/băutură fără niciun serviciu conex atașat nu e „serviciu de restaurant", ci **livrare de bunuri**, cu regulile de cotă ale bunului respectiv.

## Ce se greșește în practică

Se confundă lista de servicii cu lista de produse — de exemplu, se aplică regula „cazare = 11%" și transportului sau altor servicii turistice conexe care nu sunt cazare propriu-zisă. A doua greșeală frecventă: se ignoră faptul că lista e limitativă, iar servicii care „par" de interes general (ex. consultanță educațională, servicii medicale private neincluse expres) nu intră automat la cotă redusă doar din analogie.

## Ce face iConta.eu

`core/cote_tva.py` include în `CATEGORII_11` fiecare serviciu eligibil, cu referință explicită la litera din art. 291 alin. (2) și exemple concrete (ex. „cazare hotel", „meniu restaurant", „catering eveniment"). Motorul de potrivire cotă (`potriveste_cota`) folosește AI pentru a încadra descrierea serviciului în categoria corectă și, dacă nu poate stabili clar cota, blochează linia ca **nedeterminată** — nu completează implicit cu 21%.

[iConta.eu](/)
