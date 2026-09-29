---
title: "Cum se calculează IMCA datorat pe un trimestru când calculul se face cumulat de la începutul anului?"
description: "Se compară IMCA și impozitul pe profit calculate cumulat de la 1 ianuarie, se reține cel mai mare, apoi se scade impozitul datorat pentru trimestrele anterioare; diferența e impozitul trimestrului."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Cum se calculează IMCA datorat pe un trimestru când calculul se face cumulat de la începutul anului?

La IMCA, comparația dintre impozitul pe profit și impozitul minim nu se face pe fiecare trimestru izolat. Se face cumulat, de la începutul anului fiscal până la sfârșitul trimestrului de calcul. Suma de plată pentru trimestru se obține prin diferență: din impozitul datorat cumulat, adică profitul sau minimul, după caz, se scade impozitul datorat deja pentru trimestrele anterioare.

În consecință, o firmă poate plăti IMCA într-un trimestru și impozit pe profit în următorul, iar suma trimestrială nu e niciodată „IMCA-ul trimestrului" calculat separat.

## Temeiul legal

::: ghid-temei
„c) pentru stabilirea impozitului pe profit/minim datorat trimestrial, din impozitul pe profit/minim calculat cumulat de la începutul anului fiscal se scade impozitul minim sau impozitul pe profit datorat pentru perioada anterioară celei de calcul, după caz;"
— HG 1/2016 (Normele Codului fiscal), Titlul II, pct. 4^1 alin. (1) lit. c) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)

„care în anul de calcul determină un impozit pe profit, cumulat de la începutul anului fiscal/anului fiscal modificat până la sfârșitul trimestrului/anului de calcul, mai mic decât impozitul minim pe cifra de afaceri stabilit potrivit prevederilor alin. (3)"
— Codul fiscal (Legea 227/2015), art. 18^1 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin. (3) este 0,5%."
— Codul fiscal (Legea 227/2015), art. 18^1 alin. (16) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pașii pentru fiecare trimestru, la sistemul trimestrial:

1. Se calculează **IMCA cumulat**: 0,5% × (VT − Vs − I − A), cu toți indicatorii cumulați de la începutul anului.
2. Se calculează **impozitul pe profit cumulat pentru comparație**. Acesta e impozitul înainte de scăderile legale, din care se scad sponsorizarea/mecenatul și alte sume din legi speciale, dar nu creditul fiscal extern, scutirea pentru profitul reinvestit și creditul pentru cercetare-dezvoltare (art. 18^1 alin. (5), forma aplicabilă din 2026).
3. Se reține **impozitul datorat cumulat**: profitul, dacă e cel puțin egal cu IMCA; altfel IMCA.
4. Se scade **impozitul datorat pentru trimestrele anterioare**, indiferent dacă atunci s-a plătit profit sau minim. Diferența e suma trimestrului.

Dacă rezultatul fiscal cumulat e pierdere, se determină tot IMCA (art. 18^1 alin. (2)). Dacă formula dă o valoare negativă, impozitul minim este zero (alin. (4)). Pentru firmele cu sistem anual și plăți anticipate, comparația se face altfel, cu plățile anticipate (alin. (6)).

::: ghid-exemplu
SC Exemplu SA (peste pragul de 50.000.000 euro, sistem trimestrial), anul 2026, sume cumulate de la 1 ianuarie:

| Trimestru | IMCA cumulat | Impozit profit cumulat (comparație) | Datorat cumulat | Datorat anterior | De plată în trimestru |
|---|---|---|---|---|---|
| I | 1.000.000 | 800.000 | 1.000.000 (IMCA) | 0 | 1.000.000 |
| II | 2.100.000 | 2.500.000 | 2.500.000 (profit) | 1.000.000 | 1.500.000 |
| III | 3.300.000 | 3.000.000 | 3.300.000 (IMCA) | 2.500.000 | 800.000 |

În trimestrul III, IMCA-ul „trimestrului" luat separat (3.300.000 − 2.100.000 = 1.200.000) ar fi o sumă greșită. Se scade ce s-a datorat efectiv înainte, 2.500.000 lei.
:::

## Ce se greșește în practică

- IMCA se calculează doar pe veniturile trimestrului curent și se compară cu profitul trimestrului curent.
- Din valoarea cumulată se scade IMCA-ul trimestrelor anterioare, deși în acele trimestre s-a datorat impozit pe profit (sau invers).
- În 2026 se aplică cota de 1%, deși alin. (16) o stabilește la 0,5%.
- În comparație se scade scutirea pentru profitul reinvestit sau creditul fiscal extern, pe care alin. (5) le exclude.

## Ce face iConta.eu

iConta.eu calculează IMCA și comparația cu impozitul pe profit în declarația anuală D101, validată pe validatorul oficial ANAF, cu cota aleasă după anul fiscal. Indicatorii VT, Vs, I și A se introduc de contabil. Calculul trimestrial cumulat și scăderea impozitului datorat în trimestrele anterioare nu sunt automatizate în D100. Suma de declarat pe trimestru o stabilește contabilul.

[iConta.eu](/)
