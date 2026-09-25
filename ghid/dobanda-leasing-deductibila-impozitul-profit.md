---
title: "Dobânda din leasing este deductibilă la impozitul pe profit?"
description: "Cum se încadrează costul de finanțare al ratelor de leasing financiar în regula de limitare a deductibilității costurilor îndatorării, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Dobânda din leasing este deductibilă la impozitul pe profit?

Da, dobânda (mai exact, componenta de finanțare din rata de leasing financiar) este deductibilă — dar legea o tratează exact ca pe orice altă dobândă bancară, supusă aceleiași reguli de plafonare, nu ca pe o categorie separată de cheltuială.

## Temeiul legal

::: ghid-temei
„costurile îndatorării - cheltuiala reprezentând dobânda aferentă tuturor formelor de datorii, alte costuri echivalente din punct de vedere economic cu dobânzile, inclusiv alte cheltuieli suportate în legătură cu obținerea de finanțare potrivit reglementărilor legale în vigoare, cum ar fi, dar fără a se limita la acestea: [...] costul de finanțare al plăților de leasing financiar, dobânda capitalizată inclusă în valoarea contabilă a unui activ aferent sau amortizarea dobânzii capitalizate [...]."
— Legea nr. 227/2015 (Codul fiscal), art. 40^1 pct. 1 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecința directă a acestei definiții:

- Componenta de dobândă/finanțare din ratele de leasing financiar intră în categoria **„costurilor îndatorării"**, alături de dobânzile bancare clasice — nu are un regim fiscal separat.
- Fiind cost al îndatorării, se supune aceleiași reguli de limitare de la art. 40^2: deductibilă integral până la plafonul de 1.000.000 euro anual (sau integral, dacă firma e „entitate independentă", fără grup consolidat sau afiliați), iar peste plafon, limitată la 30% dintr-o bază de calcul specifică.
- Componenta de **capital** din rata de leasing (nu dobânda) nu este o cheltuială, ci o rambursare a principalului — ea majorează, respectiv diminuează, valoarea datoriei de leasing din bilanț, fără impact direct asupra rezultatului fiscal ca „dobândă".

## Ce se greșește în practică

- Se tratează întreaga rată de leasing ca fiind deductibilă necondiționat, fără să se separe componenta de dobândă (supusă plafonării de la art. 40^2) de componenta de capital.
- Se presupune că leasingul financiar are un regim de deductibilitate mai favorabil decât un credit bancar clasic — de fapt, costul de finanțare al leasingului e explicit inclus în aceeași definiție a „costurilor îndatorării", cu același tratament.
- Se ignoră, la firme mici cu un singur contract de leasing, faptul că majoritatea se încadrează în excepția de „entitate independentă" de la art. 40^2 alin. (5), ceea ce le-ar scuti de orice limitare — verificarea acestei încadrări se omite frecvent.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă evidența contabilă a contractelor de leasing financiar și operațional și a ratelor aferente (`core/leasing.py`), care înregistrează separat, la fiecare rată, componenta de capital (contul 167) de componenta de dobândă (contul 666) — deci separarea contabilă a dobânzii există. Aplicația **nu însumează însă automat**, la nivelul întregului an fiscal și al tuturor surselor de finanțare (leasing plus alte împrumuturi), costurile excedentare ale îndatorării și **nu verifică** plafonul de 1.000.000 euro de la art. 40^2 sau încadrarea firmei ca entitate independentă. Ajustarea fiscală rezultată din regula de limitare, dacă e cazul, rămâne o evaluare a contabilului, introdusă manual în calculul impozitului pe profit.

[iConta.eu](/)
