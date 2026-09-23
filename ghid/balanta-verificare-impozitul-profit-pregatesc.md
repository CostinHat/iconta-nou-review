---
title: "Balanta de verificare și impozitul pe profit: cum îl pregătesc"
description: Ce date preia D101 din balanța de verificare — clase de conturi, rezerva legală, cheltuiala cu impozitul — și cum se pregătesc corect înainte de generarea declarației.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Balanta de verificare și impozitul pe profit: cum îl pregătesc

Impozitul pe profit se calculează pornind de la balanța de verificare, dar nu prin preluarea brută a rulajelor — anumite clase de conturi și solduri au un rol specific în determinarea profitului impozabil.

## Temeiul legal

::: ghid-temei
Rezerva legală (P13) e „calculată automat când nu e dată manual (liniile 264–275), din profitul contabil brut + cheltuiala cu impozitul (cont 691), plafonată la min(5% × bază; 20% × capital social − rezervă existentă), temei CF art.26 alin.(1) lit.a)"
— sursă: `core/d101.py`, liniile 264–275, dosar de cercetare F027.

D101 „citește profilul firmei + balanța, cu split exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare) și datele pentru rezerva legală (capital 1012, rezervă existentă 1061, cheltuială impozit 691)"
— sursă: `core/d101.py`, funcția `pull()`, liniile 448–467, dosar de cercetare F027.
:::

Practic, balanța trebuie să conțină corect cel puțin patru repere înainte de generarea D101: soldul contului 1012 (capital social), soldul contului 1061 (rezervă legală deja constituită), soldul contului 691 (cheltuiala cu impozitul pe profit) și separarea clară între conturile de clasa 76/66 (venituri/cheltuieli financiare) și restul conturilor de clasa 7x/6x (exploatare). Rezerva legală se calculează automat din profitul contabil brut plus cheltuiala cu impozitul, plafonată la minimul dintre 5% din bază și 20% din capitalul social minus rezerva deja constituită (art.26 alin.(1) lit.a) din Codul fiscal) — dacă aceste conturi nu sunt corect încheiate, plafonul rezultă greșit.

## Ce se greșește în practică

Cea mai frecventă greșeală este nedecontarea corectă a contului 691 înainte de închiderea lunii/anului, ceea ce denaturează atât calculul rezervei legale, cât și verificarea automată privind cheltuielile nedeductibile. A doua greșeală este amestecarea veniturilor/cheltuielilor financiare (clasele 76/66) cu cele de exploatare, care poate distorsiona subtotalurile folosite mai departe în declarație.

## Ce face iConta.eu

La generarea D101, iConta.eu preia automat din balanță profilul firmei și datele necesare: capitalul social (1012), rezerva legală existentă (1061) și cheltuiala cu impozitul pe profit (691), cu separarea automată exploatare/financiar pe baza claselor de conturi. Rezerva legală se calculează automat, cu opțiunea de a fi introdusă manual dacă valoarea calculată nu corespunde situației reale. Declarația nu se poate genera fără date minime de identificare corecte (CUI valid, denumire, adresă, cod CAEN pe 4 cifre).

[iConta.eu](/)
