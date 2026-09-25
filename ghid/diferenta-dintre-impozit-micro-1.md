---
title: "Diferența dintre impozit micro 1% și impozit pe profit 16% în 2026"
description: "Cum diferă bazele de calcul și cotele celor două regimuri de impozitare a firmelor românești în 2026: impozitul micro (1%, pe venituri) și impozitul pe profit (16%, pe profit)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferența dintre impozit micro 1% și impozit pe profit 16% în 2026

Diferența nu e doar de cotă, ci de bază de calcul: impozitul micro se aplică pe venituri, impozitul pe profit se aplică pe profit. O firmă cu marjă mică poate plăti mai mult la micro decât ar plăti la profit, chiar dacă 1% pare mult mai puțin decât 16%.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Legea 227/2015, art. 51 alin. (1), Titlul III (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: [...]."
— Legea 227/2015, art. 53 alin. (1), Titlul III (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Legea 227/2015, art. 17, Titlul II (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic:

- **Micro** — 1% aplicat la venituri (cu scăderile limitative de la art. 53: costuri stocuri/servicii în curs, producție de imobilizări, subvenții etc.), indiferent dacă firma a avut profit sau pierdere contabilă în perioada respectivă. Se plătește chiar și atunci când firma e pe pierdere.
- **Profit** — 16% aplicat la profitul impozabil (venituri minus cheltuieli deductibile, plus/minus ajustări fiscale). Dacă firma nu are profit impozabil într-un trimestru, nu datorează impozit pentru acel trimestru.

Pragul „de rentabilitate" la care cele două regimuri dau aceeași sumă de plată e, aproximativ, o marjă de profit de 6,25% din venituri (1% / 16% = 6,25%): sub acest procent, micro e mai scump; peste, profitul e mai avantajos — dar alegerea regimului nu e liberă în orice moment, ci condiționată de art. 47-48 (eligibilitate și momentul opțiunii).

## Ce se greșește în practică

- Se compară direct cotele (1% vs. 16%) fără a lua în calcul că bazele de impozitare sunt complet diferite (venituri vs. profit).
- Se presupune că o firmă pe pierdere plătește 0 la micro, la fel ca la profit — de fapt, la micro impozitul se calculează tot pe venituri, indiferent de rezultat.
- Se ignoră faptul că trecerea între regimuri nu e liberă în orice moment al anului (vezi art. 48 și art. 52), ci supusă unor condiții și termene distincte.

## Ce face iConta.eu

iConta.eu calculează separat cele două baze conform legii: pentru profit, motorul D100 determină rezultatul fiscal real (venituri minus cheltuieli, cumulat de la începutul anului, conform art. 41), nu doar venituri brute; pentru micro, baza pornește de la veniturile din orice sursă înregistrate în conturile de clasa 7, cu reducerile comerciale scăzute. La data acestui ghid, aplicația nu are un simulator dedicat care să compare automat, pentru o firmă dată, câte lei ar plăti sub fiecare regim — o astfel de comparație rămâne o analiză pe care contabilul o face separat, folosind cifrele reale din evidența contabilă a firmei.

[iConta.eu](/)
