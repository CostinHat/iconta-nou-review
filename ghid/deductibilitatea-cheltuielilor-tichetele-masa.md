---
title: "Deductibilitatea cheltuielilor cu tichetele de masă"
description: Cheltuiala cu tichetele de masă are deductibilitate limitată la impozitul pe profit, nu deductibilitate integrală — limita fiind valoarea nominală acordată potrivit legii, adică plafonul legal al tichetului, nu un procent din fondul de salarii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Deductibilitatea cheltuielilor cu tichetele de masă

Cheltuiala cu tichetele de masă e adesea descrisă simplificat ca „deductibilă integral" — formulare care poate induce în eroare, pentru că textul de lege o încadrează explicit la categoria cheltuielilor cu **deductibilitate limitată**, nu la cele nelimitate.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 25 alin. (3) lit. c) — sub titlul „Următoarele cheltuieli au deductibilitate limitată": „cheltuielile reprezentând tichetele de masă și vouchere de vacanță acordate de angajatori, potrivit legii;"
:::

Limita reală nu e un procent propriu (spre deosebire de cheltuielile sociale de la art. 25 alin. (3) lit. b), plafonate explicit la 5% din fondul de salarii, categorie în care intră cadourile, tichetele culturale sau tichetele de creșă) — limita e „acordate potrivit legii", adică valoarea nominală acordată **în limita plafonului legal al tichetului**: 45 lei/tichet pentru 2026 (Legea 201/2025). Tichetele de masă și voucherele de vacanță au poziție proprie, separată de plafonul de 5%, la art. 25 alin. (3) lit. c) — nu se cumulează cu acesta și nu intră în calculul lui.

## Ce se greșește în practică

- Se afirmă că tichetele de masă sunt „deductibile integral", fără nicio referire la art. 25 din Codul fiscal — o simplificare care ascunde faptul că deductibilitatea e condiționată de acordarea „potrivit legii", nu necondiționată.
- Se include cheltuiala cu tichetele de masă în plafonul de 5% al cheltuielilor sociale (art. 25 alin. (3) lit. b) — greșit, pentru că tichetele de masă/vacanță au poziție proprie, distinctă, la lit. c).
- Se ignoră faptul că, dacă un tichet ar fi emis peste plafonul legal (45 lei pentru 2026), acel excedent nu ar mai fi „acordat potrivit legii" și ar risca nedeductibilitatea — limita nu e doar formală, are consecință fiscală directă.

## Ce face iConta.eu

Motorul de salarizare aplică plafonul legal de 45 lei/tichet pentru 2026 (`common.COTE["tichet_masa_plafon"]`), astfel încât valoarea acordată prin tichete de masă rămâne, structural, în limita legală care condiționează deductibilitatea la impozitul pe profit. Contarea automată (`core/salarii_contare.py`) înregistrează biletele de valoare acordate pe contul 642 = 5328, distinct de cheltuielile sociale plafonate la 5%, care urmează un flux separat — dar încadrarea finală a cheltuielii ca deductibilă limitat conform art. 25 alin. (3) lit. c), la calculul impozitului pe profit, rămâne o verificare pe care contabilul o face pe baza acestor date, nu un calcul automatizat de impozit pe profit în F133.

[iConta.eu](/)
