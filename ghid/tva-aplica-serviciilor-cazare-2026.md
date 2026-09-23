---
title: Ce TVA se aplică serviciilor de cazare în 2026?
description: Cazarea în sectorul hotelier și camping intră la cota redusă de 11%, iar la pachetele cu demipensiune, pensiune completă sau all-inclusive, cota redusă se aplică la prețul total — inclusiv băuturile alcoolice incluse.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce TVA se aplică serviciilor de cazare în 2026?

Cazarea este una dintre categoriile explicite de pe lista redusă a art. 291 alin. (2) din Codul fiscal, la cota de 11%. Are însă o particularitate importantă față de restul serviciilor HoReCa: la pachetele de tip demipensiune, pensiune completă sau all-inclusive, cota redusă se aplică inclusiv băuturilor alcoolice incluse în preț — spre deosebire de regula generală de la restaurant, unde alcoolul e mereu la cotă standard.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „cazarea în cadrul sectorului hotelier sau al sectoarelor cu funcție similară, inclusiv închirierea terenurilor amenajate pentru camping” — Codul fiscal, art. 291 alin. (2) lit. m).
:::

## Ce intră la cota de 11%

- Cazarea în structuri de primire turistice cu funcțiune de cazare (hoteluri, pensiuni, moteluri și sectoare cu funcție similară).
- Închirierea terenurilor amenajate pentru camping.

## Excepția demipensiunii/pensiunii complete/all-inclusive

La pachetele de cazare care includ masă (demipensiune, pensiune completă) sau „all inclusive", cota redusă de 11% se aplică **la prețul total al pachetului**, care poate include și băuturi alcoolice servite în cadrul acestuia — o excepție explicită de la regula generală conform căreia băuturile alcoolice sunt mereu la cota standard. Practic, un pachet all-inclusive nu se defalcă separat pe „cazare 11% + băuturi alcoolice 21%"; întregul preț al pachetului urmează cota cazării.

Această excepție e specifică pachetului de cazare — nu se extinde la restaurantul independent din cadrul aceleiași unități hoteliere, unde consumația servită separat (nu ca parte a pachetului de cazare) urmează regulile obișnuite de restaurant, cu alcoolul la cotă standard.

## Ce se greșește în practică

- Se aplică cota standard pe toată valoarea unui pachet all-inclusive, din obișnuința „alcoolul e mereu la 21%" — regula generală nu se aplică aici, tocmai pentru că prețul cazării e unul global.
- Se defalcă manual băuturile alcoolice din pachetul de cazare la o cotă separată de 21%, deși pentru pachetele cu demipensiune/pensiune completă/all-inclusive legea prevede explicit aplicarea cotei reduse la prețul total.
- Se confundă cazarea simplă (fără masă inclusă) cu pachetele tip demipensiune/all-inclusive — pentru cazarea simplă, orice consumație facturată separat urmează regulile ei proprii, nu cota cazării.

## Ce face iConta.eu

`core/cote_tva.py` include categoria `cazare` la cota de 11% (art. 291 alin. (2) lit. m), separat de categoria `restaurant_catering`. Tratamentul special al pachetelor demipensiune/pensiune completă/all-inclusive (cota redusă aplicată prețului total, inclusiv alcool inclus) ține de modul în care e facturat pachetul, nu de un câmp automat distinct — la emiterea facturii, pachetul se declară ca o singură linie de cazare, la cota de 11%, nu defalcat pe componente cu cote diferite.

[iConta.eu](/)
