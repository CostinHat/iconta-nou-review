---
title: TVA pentru serviciile de cazare în 2026
description: Cazarea în sectorul hotelier și camping intră la cota redusă de 11%, iar la pachetele cu demipensiune, pensiune completă sau all-inclusive, cota redusă se aplică la prețul total — inclusiv băuturile alcoolice incluse în preț.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# TVA pentru serviciile de cazare în 2026

Serviciile de cazare — hoteluri, pensiuni, moteluri, camping — sunt una dintre categoriile explicite de pe lista redusă a art. 291 din Codul fiscal, la cota de 11%. Particularitatea față de restul serviciilor HoReCa apare la pachetele cu masă inclusă: acolo cota redusă acoperă și băuturile alcoolice servite în cadrul pachetului, o excepție explicită de la regula generală.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „cazarea în cadrul sectorului hotelier sau al sectoarelor cu funcție similară, inclusiv închirierea terenurilor amenajate pentru camping" — Codul fiscal, art. 291 alin. (2) lit. m).
:::

## Ce intră la cota de 11%

- Cazarea propriu-zisă în structuri de primire turistice cu funcțiune de cazare (hoteluri, pensiuni, moteluri și sectoare cu funcție similară).
- Închirierea terenurilor amenajate pentru camping.

## Pachetele cu masă inclusă

La pachetele de tip demipensiune, pensiune completă sau „all inclusive", cota redusă de 11% se aplică **la prețul total al pachetului** — normele metodologice la Codul fiscal precizează explicit că acest preț total „poate include și băuturi alcoolice". Practic, un pachet all-inclusive nu se defalcă pe „cazare 11% + băuturi alcoolice 21%"; întreg prețul urmează cota cazării.

Excepția e specifică pachetului de cazare — nu se extinde la restaurantul independent din aceeași unitate hotelieră, unde o consumație facturată separat (nu ca parte a pachetului de cazare) urmează regulile obișnuite de restaurant, cu alcoolul mereu la cota standard.

## Ce se greșește în practică

- Se aplică cota standard pe toată valoarea unui pachet all-inclusive, din obișnuința „alcoolul e mereu la 21%" — regula generală nu se aplică aici, tocmai pentru că prețul cazării e unul global.
- Se defalcă manual băuturile alcoolice dintr-un pachet demipensiune/pensiune completă/all-inclusive la o cotă separată de 21%, deși legea prevede explicit aplicarea cotei reduse la prețul total al pachetului.
- Se confundă cazarea simplă, fără masă inclusă, cu pachetele de tip demipensiune/all-inclusive — pentru cazarea simplă, orice consumație facturată separat urmează cota ei proprie, nu pe cea a cazării.

## Ce face iConta.eu

`core/cote_tva.py` include categoria `cazare` la cota de 11% (art. 291 alin. (2) lit. m), separat de categoria `restaurant_catering`. Tratamentul special al pachetelor demipensiune/pensiune completă/all-inclusive ține de modul în care e facturat pachetul, nu de un câmp automat distinct — pachetul se declară pe factură ca o singură linie de cazare, la cota de 11%, nu defalcat pe componente cu cote diferite.

[iConta.eu](/)
