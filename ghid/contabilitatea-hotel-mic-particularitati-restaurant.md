---
title: "Contabilitatea unui hotel mic: particularități față de un restaurant"
description: "De ce cazarea hotelieră și serviciile de restaurant au aceeași cotă redusă de TVA, dar un hotel mic gestionează contabil mai multe linii de venit cu cote diferite decât un restaurant simplu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unui hotel mic: particularități față de un restaurant

Diferența contabilă dintre un hotel mic și un restaurant nu vine din cota de TVA — cazarea și serviciile de restaurant/catering au aceeași cotă redusă. Vine din numărul de linii de venit cu regim de TVA diferit pe care le gestionează simultan un hotel: cazare, mic dejun/restaurant, băuturi alcoolice, minibar și alte servicii conexe, fiecare cu tratament fiscal propriu.

## Temeiul legal

::: ghid-temei
„Cota redusă de 11% se aplică asupra bazei de impozitare pentru următoarele prestări de servicii și/sau livrări de bunuri: [...] m) cazarea în cadrul sectorului hotelier sau al sectoarelor cu funcție similară, inclusiv închirierea terenurilor amenajate pentru camping; [...] n) serviciile de restaurant și de catering, cu excepția băuturilor alcoolice, precum și a băuturilor nealcoolice care se încadrează la codul NC 2202."
— Legea nr. 227/2015 privind Codul fiscal, art. 291 alin. (2) lit. m) și n) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă concret pentru cele două tipuri de afaceri:

- **Cota de 11%** se aplică deopotrivă cazării hoteliere (lit. m) și serviciilor de restaurant/catering (lit. n) — un restaurant simplu, ca și un hotel, aplică aceeași cotă redusă pentru vânzarea de mâncare și pentru serviciile de masă.
- **Excepția comună**: băuturile alcoolice, precum și băuturile nealcoolice încadrate la codul NC 2202 (în principal băuturi carbogazoase/răcoritoare cu zahăr adăugat), rămân în afara cotei reduse de la lit. n) — atât într-un restaurant, cât și în restaurantul/barul unui hotel, aceste produse se taxează la cota standard.
- **Particularitatea unui hotel** e că, spre deosebire de un restaurant care are de regulă o singură linie de venit dominantă (masa/serviciile de restaurant), un hotel cumulează mai multe linii cu regim de TVA diferit în cadrul aceleiași facturi sau al aceleiași șederi a clientului: cazare (11%), mic dejun/restaurant (11%, cu excepția alcoolului), minibar/băuturi alcoolice (21%), și eventual alte servicii (spa, parcare, transport) care pot avea reguli proprii, distincte de cazare și restaurant.

## Ce se greșește în practică

- Se aplică o singură cotă de TVA pentru întreaga factură a unui sejur hotelier (de exemplu, doar 11%), fără separarea corectă a liniilor de venit — băuturile alcoolice consumate la restaurantul hotelului sau din minibar rămân la cota standard, indiferent că fac parte din același sejur facturat clientului.
- Se presupune că restaurantul unui hotel are un regim de TVA diferit de un restaurant independent — art. 291 alin. (2) lit. n) se aplică identic, indiferent de tipul de operator care prestează serviciul de restaurant.
- Se ignoră separarea pe conturi analitice a veniturilor din cazare față de cele din restaurant/alte servicii, deși cele două au regimuri de TVA diferite parțial (cazare complet la 11%, restaurant la 11% cu excepția alcoolului) — o evidență nesegregată complică reconcilierea TVA colectată pe fiecare cotă.

## Ce face iConta.eu

iConta.eu are o funcționalitate reală de clasificare a operațiunilor pe cote de TVA, în `core/cote_tva.py`, cu chei distincte de nomenclator pentru „cazare" (cazare hotelieră sau în sectoare cu funcție similară), „restaurant_catering" (servicii de restaurant și catering) și băuturile alcoolice (taxate separat, chiar și în restaurant/catering) — exact distincția din art. 291 alin. (2) lit. m) și n). Aplicația oferă evidența contabilă generală pe aceste categorii; separarea liniilor de venit ale unui hotel (cazare, restaurant, minibar, alte servicii) pe facturile emise rămâne, la această dată, o decizie de structurare pe care contabilul o face la configurarea articolelor/serviciilor firmei.

[iConta.eu](/)
