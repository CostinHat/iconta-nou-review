---
title: "Cum se contabilizează costurile de remediere după predarea unui apartament nou?"
description: "Regula fiscală a provizioanelor pentru garanții de bună execuție, aplicabilă dezvoltatorilor imobiliari care rămân obligați la remedieri după predarea unei locuințe noi."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează costurile de remediere după predarea unui apartament nou?

Un dezvoltator imobiliar rămâne, de regulă, obligat contractual să remedieze defectele constatate la un apartament nou vândut, o perioadă de timp după predare (garanția de bună execuție). Costurile viitoare de remediere nu sunt cheltuieli certe la data vânzării, dar sunt previzibile — de aceea legea permite constituirea unui provizion deductibil fiscal, în anumite condiții.

## Temeiul legal

::: ghid-temei
„b) provizioanele pentru garanții de bună execuție acordate clienților. Provizioanele pentru garanții de bună execuție acordate clienților se deduc trimestrial/anual numai pentru bunurile livrate, lucrările executate și serviciile prestate în cursul trimestrului/anului respectiv pentru care se acordă garanție în perioadele următoare, la nivelul cotelor prevăzute în convențiile încheiate sau la nivelul procentelor de garantare prevăzut în tariful lucrărilor executate ori serviciilor prestate;"
— Legea nr. 227/2015 (Codul fiscal), art. 26 alin. (1) lit. b) „Provizioane/ajustări pentru depreciere și rezerve" (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă pentru un dezvoltator care vinde apartamente noi cu obligație de garanție:

- Provizionul se constituie **pentru bunul livrat** (apartamentul predat) în trimestrul/anul respectiv, nu retroactiv pentru toate vânzările vechi — legătura dintre livrare și constituirea provizionului trebuie să fie directă.
- Nivelul deductibil al provizionului este limitat la **cota prevăzută în convenția încheiată cu clientul** sau la procentul de garantare din tariful lucrărilor/serviciilor — nu la o estimare discreționară a costurilor viitoare.
- Costurile efective de remediere, atunci când apar, se suportă din provizionul constituit (reluare la venituri, în măsura utilizării), nu se înregistrează din nou ca o cheltuială deductibilă separată, dacă provizionul le acoperă.

## Ce se greșește în practică

- Se înregistrează costurile de remediere direct pe cheltuială, în momentul în care apar, fără să fi fost constituit anterior provizionul pentru garanție la momentul livrării — pierzând astfel corelarea cheltuielii cu veniturile perioadei de vânzare.
- Se constituie provizionul la un nivel arbitrar, fără legătură cu cota din convenția de vânzare sau din tariful aplicat, ceea ce poate atrage respingerea deductibilității diferenței la un control fiscal.
- Se omite reluarea la venituri a provizionului rămas neutilizat după expirarea perioadei de garanție — provizionul nu poate rămâne constituit la nesfârșit, fără actualizare periodică a estimării.

## Ce face iConta.eu

Da — iConta.eu are un modul dedicat provizioanelor (`core/provizioane.py`), care implementează explicit regula de la art. 26 alin. (1) lit. b): provizioanele pentru garanții de bună execuție (cont 1512) sunt marcate ca fiind singurele deductibile integral din categoria provizioanelor de risc (spre deosebire de cele pentru litigii, dezafectare sau restructurare, care sunt nedeductibile), cu notele contabile de constituire (6812 = 1512) și de reluare (1512 = 7812) deja construite.

[iConta.eu](/)
