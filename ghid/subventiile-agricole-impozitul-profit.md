---
title: "Subvențiile agricole și impozitul pe profit"
description: "De ce subvențiile agricole sunt, la impozitul pe profit, venituri impozabile (spre deosebire de regimul micro), cu excepția celor care reduc valoarea fiscală a unui mijloc fix."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Subvențiile agricole și impozitul pe profit

Spre deosebire de impozitul micro, unde subvențiile sunt explicit excluse din baza de calcul, la impozitul pe profit subvențiile agricole sunt, ca regulă, venituri impozabile — lista veniturilor neimpozabile de la art. 23 din Codul fiscal nu le menționează.

## Temeiul legal

::: ghid-temei
„La calculul rezultatului fiscal, următoarele venituri sunt neimpozabile: a) dividendele primite [...]; b) dividende primite de la o persoană juridică străină [...]; c) valoarea titlurilor de participare noi [...]; d) veniturile din anularea, recuperarea [...]; [...]." — lista, limitativă, nu conține subvențiile.
— Legea 227/2015, art. 23, Titlul II (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Prin excepție de la prevederile art. 7 pct. 44 și 45, în situația în care, potrivit reglementărilor contabile aplicabile, contribuabilul deduce subvenția guvernamentală la calculul valorii contabile a mijloacelor fixe, valoarea rezultată este și valoare fiscală."
— Legea 227/2015, art. 28 alin. (13), Titlul II (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

Pentru comparație, la microîntreprinderi: „Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: [...] d) veniturile din subvenții; [...]."
— Legea 227/2015, art. 53 alin. (1) lit. d), Titlul III (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Concluzia din combinarea textelor:

- **La impozitul pe profit** (Titlul II) — subvenția agricolă primită (de exemplu, plăți APIA pentru suprafață cultivată) e, ca regulă, venit impozabil, pentru că nu apare în lista limitativă de venituri neimpozabile de la art. 23. Se impozitează cu 16%, la fel ca orice alt venit din exploatare.
- **Excepția** — dacă subvenția finanțează achiziția unui mijloc fix (de exemplu, subvenție pentru un utilaj agricol) și, potrivit reglementărilor contabile, firma o deduce din valoarea contabilă a activului, atunci valoarea fiscală a mijlocului fix e cea rezultată după scăderea subvenției (art. 28 alin. 13) — practic, subvenția nu se impozitează separat ca venit, ci reduce baza de amortizare viitoare a activului.
- **La impozitul micro** (Titlul III) — regimul e mai favorabil: veniturile din subvenții se scad explicit din baza impozabilă (art. 53 alin. 1 lit. d), indiferent de destinația subvenției.

## Ce se greșește în practică

- Se aplică, greșit, prin analogie cu regimul micro, o scutire generală a subvențiilor agricole la impozitul pe profit — art. 23 (lista de venituri neimpozabile la profit) nu include subvențiile.
- Se impozitează subvenția și separat ca venit, și indirect prin amortizarea integrală (nereduse) a activului achiziționat din ea — dublă neconcordanță față de art. 28 alin. (13), care cere reducerea valorii fiscale a activului cu subvenția dedusă contabil.
- Se confundă subvențiile de exploatare (contul 741, de regulă venit impozabil integral) cu subvențiile pentru investiții (contul 7584, cu regimul particular de la art. 28 alin. 13, legat de valoarea fiscală a mijlocului fix).

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit pe baza rezultatului fiscal real (venituri minus cheltuieli), care include, ca regulă, veniturile din subvenții înregistrate în conturile de venituri — conform tratamentului general de la art. 23, care nu le scutește. Pentru microîntreprinderi, motorul de calcul al bazei impozabile (art. 53) exclude veniturile din subvenții din baza de 1%. La data acestui ghid, aplicația nu are o funcție automată dedicată care să identifice subvențiile pentru investiții și să ajusteze corespunzător valoarea fiscală a mijlocului fix conform art. 28 alin. (13) — această ajustare, atunci când se aplică, rămâne o operațiune manuală a contabilului la înregistrarea activului.

[iConta.eu](/)
