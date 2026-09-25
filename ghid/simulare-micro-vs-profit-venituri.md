---
title: "Simulare micro vs profit pentru venituri de 300.000 lei"
description: "Cum se calculează, cu temei legal, impozitul datorat de o firmă cu 300.000 lei venituri sub cele două regimuri — micro (1%) și profit (16%) — în funcție de marja de profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Simulare micro vs profit pentru venituri de 300.000 lei

Pentru o firmă cu 300.000 lei venituri anuale, răspunsul „ce regim e mai avantajos" depinde exclusiv de marja de profit — nu există un răspuns universal, pentru că bazele de calcul ale celor două impozite sunt diferite.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Legea 227/2015, art. 51 alin. (1), Titlul III (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Legea 227/2015, art. 17, Titlul II (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cu 300.000 lei venituri:

- **La micro**: impozitul e fix, indiferent de cheltuieli — 300.000 × 1% = **3.000 lei**, plătit chiar dacă firma are pierdere contabilă în acel an (baza impozabilă, art. 53, e „veniturile din orice sursă", nu profitul).
- **La profit**: impozitul depinde de cheltuielile deductibile. Formula e (venituri − cheltuieli deductibile) × 16%. Pragul la care cele două rezultate coincid e atunci când profitul impozabil e de 300.000 × (1%/16%) = **18.750 lei**, adică o marjă de profit de 6,25% din venituri:
  - dacă profitul impozabil e sub 18.750 lei (marjă sub 6,25%), micro e mai ieftin;
  - dacă profitul impozabil e peste 18.750 lei (marjă peste 6,25%), profitul (16%) e mai ieftin.

Exemplu concret: cu 300.000 lei venituri și cheltuieli deductibile de 250.000 lei, profitul impozabil e 50.000 lei — impozit pe profit 50.000 × 16% = 8.000 lei, mai mare decât impozitul micro de 3.000 lei; la marja asta, micro rămâne mai avantajos. Dacă însă cheltuielile deductibile sunt doar 100.000 lei, profitul impozabil e 200.000 lei — impozit pe profit 200.000 × 16% = 32.000 lei, mult peste cei 3.000 lei de la micro; totuși aici concluzia se inversează doar dacă marja reală trece de 6,25% — cu marje mari, profitul devine mai scump decât micro doar în aparență, calculul corect fiind întotdeauna comparația directă a celor două sume, nu a cotelor.

## Ce se greșește în practică

- Se compară direct cotele (1% vs. 16%) fără a calcula efectiv impozitul pe fiecare bază, ajungându-se la concluzia greșită că micro e mereu mai ieftin.
- Se ignoră că eligibilitatea pentru micro nu e opțională oricând — depinde de condițiile din art. 47 (printre altele, plafonul de 100.000 euro, redus prin OUG 8/2026) și de momentul opțiunii (art. 48).
- Se face simularea doar pe venituri anuale, fără a ține cont că, la profit, impozitul se calculează cumulat de la începutul anului (art. 41), iar la micro, trimestrial pe fiecare perioadă separat.

## Ce face iConta.eu

iConta.eu calculează efectiv, pentru fiecare firmă, atât baza impozitului pe profit (motorul D100, rezultat fiscal real — venituri minus cheltuieli, cumulat de la începutul anului, conform art. 41), cât și baza impozitului micro (venituri din orice sursă, conform art. 53). La data acestui ghid, aplicația nu are un modul dedicat de simulare comparativă „micro vs. profit" care să afișeze, pentru o cifră de venituri și o marjă estimată, impozitul datorat sub fiecare regim — o astfel de comparație se poate obține azi doar rulând cele două calcule separat, pe baza datelor reale din evidența contabilă.

[iConta.eu](/)
