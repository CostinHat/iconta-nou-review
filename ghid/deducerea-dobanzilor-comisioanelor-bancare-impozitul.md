---
title: "Deducerea dobânzilor și a comisioanelor bancare la impozitul pe profit"
description: "Regula de limitare a deductibilității costurilor excedentare ale îndatorării din Codul fiscal (regula ATAD): plafonul de 1.000.000 euro, limita de 30% din baza fiscală de calcul și excepția pentru entitățile independente."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Deducerea dobânzilor și a comisioanelor bancare la impozitul pe profit

Cheltuielile cu dobânzile și costurile echivalente lor din punct de vedere economic — inclusiv comisioanele de garantare, comisioanele de intermediere și alte costuri similare aferente împrumuturilor — nu sunt automat deductibile integral la impozitul pe profit. Codul fiscal le supune unei reguli de plafonare, cunoscută drept regula de limitare a deductibilității dobânzii (transpunerea directivei ATAD).

## Temeiul legal

::: ghid-temei
„(1) [...] diferența dintre costurile excedentare ale îndatorării [...] și plafonul deductibil prevăzut la alin. (4) este dedusă limitat în perioada fiscală în care este suportată, până la nivelul a 30% din baza de calcul stabilită conform algoritmului prevăzut la alin. (2).
(4) Contribuabilul are dreptul de a deduce, într-o perioadă fiscală, costurile excedentare ale îndatorării până la plafonul deductibil reprezentat de echivalentul în lei al sumei de 1.000.000 euro. [...]
(5) Prin excepție de la alin. (1) și (4), în cazul în care contribuabilul este o entitate independentă, în sensul că nu face parte dintr-un grup consolidat în scopuri de contabilitate financiară, și nu are nicio întreprindere asociată și niciun sediu permanent, acesta deduce integral costurile excedentare ale îndatorării, în perioada fiscală în care acestea sunt suportate."
— Legea 227/2015 (Codul fiscal), art. 40^2 alin. (1), (4) și (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„costurile îndatorării - cheltuiala reprezentând dobânda aferentă tuturor formelor de datorii, alte costuri echivalente din punct de vedere economic cu dobânzile [...] comisioane de garantare pentru mecanisme de finanțare, comisioane de intermediere și costuri similare aferente împrumuturilor de fonduri."
— Legea 227/2015, art. 40^1 pct. 1 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul de plafonare, pas cu pas:

1. **Se calculează costurile excedentare ale îndatorării** — diferența dintre costurile îndatorării (dobânzi și costuri echivalente, inclusiv comisioane) și veniturile din dobânzi ale firmei.
2. **Până la echivalentul a 1.000.000 euro**, aceste costuri excedentare sunt deductibile integral, indiferent de baza de calcul.
3. **Peste acest plafon**, diferența e deductibilă doar în limita a **30% din baza de calcul** stabilită la alin. (2) — practic un fel de EBITDA fiscal (rezultatul contabil ajustat cu impozitul pe profit, costurile excedentare ale îndatorării și amortizarea fiscală).
4. **Pentru tranzacțiile cu persoane afiliate** care nu finanțează achiziția/producția de imobilizări, plafonul deductibil coboară la **500.000 euro** — cu excepția instituțiilor de credit și financiare nebancare, care rămân la plafonul de 1.000.000 euro.
5. **Excepția de la alin. (5)**: o firmă independentă — fără grup consolidat, fără întreprinderi asociate, fără sediu permanent — deduce integral costurile excedentare ale îndatorării, fără plafonare.

## Ce se greșește în practică

- Se aplică plafonul de 1.000.000 euro fără să se verifice mai întâi dacă firma se încadrează la excepția de la alin. (5) — o firmă independentă, fără grup sau întreprinderi asociate, deduce integral, fără nicio limitare.
- Se confundă costurile îndatorării cu simpla dobândă bancară — definiția de la art. 40^1 pct. 1 include explicit comisioanele de garantare, de intermediere și costurile similare aferente împrumuturilor, nu doar dobânda propriu-zisă.
- Se aplică plafonul general de 1.000.000 euro pentru finanțări de la persoane afiliate care nu finanțează active imobilizate, ignorând plafonul specific, mai mic, de 500.000 euro.

## Ce face iConta.eu

La data acestui ghid, nu am putut confirma din codul aplicației un modul care să aplice automat regula de limitare a deductibilității dobânzii din art. 40^2 (calculul bazei de 30%, plafonul de 1.000.000/500.000 euro sau testul de entitate independentă) la determinarea impozitului pe profit. Aplicația oferă evidența contabilă generală a cheltuielilor financiare; verificarea plafonului de deductibilitate rămâne, la acest stadiu, un calcul pe care contabilul trebuie să-l facă separat.

[iConta.eu](/)
