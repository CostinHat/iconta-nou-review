---
title: Cum se calculează plafonul de sponsorizare 2026 pentru profit
description: Plafonul deductibil în 2026 este minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit datorat — se calculează ambele valori separat și se reține cea mai mică; regula e neschimbată din 03.02.2022, nu diferă pentru anul fiscal 2026.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează plafonul de sponsorizare 2026 pentru profit

Pentru anul fiscal 2026, plafonul de sponsorizare deductibil din impozitul pe profit se calculează exact ca în anii anteriori, de la 3 februarie 2022 încoace — nu a intervenit nicio modificare de procent între 2022 și 2026. Formula are doi termeni, iar plafonul e mereu cel mai mic dintre ei.

## Temeiul legal

::: ghid-temei
„i) ... contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea..., scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele:
1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor;
2. valoarea reprezentând 20% din impozitul pe profit datorat. În cazul sponsorizărilor efectuate către entități persoane juridice fără scop lucrativ, inclusiv unități de cult, sumele aferente acestora se scad din impozitul pe profit datorat, în limitele prevăzute de prezenta literă, doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală (de la 03.02.2022, aplicabilă și în 2026).*
:::

## Formula, pas cu pas

1. **Calculați prima valoare:** `0,75% × cifra de afaceri` a firmei, pentru anul fiscal (sau trimestrul) pentru care se face calculul.
2. **Calculați a doua valoare:** `20% × impozitul pe profit datorat` pentru aceeași perioadă.
3. **Rețineți valoarea mai mică** dintre cele două — acesta e plafonul deductibil pentru 2026.
4. **Comparați plafonul cu suma efectiv sponsorizată** — creditul fiscal propriu-zis este minimul dintre plafon și suma acordată efectiv.

::: ghid-exemplu
O firmă are, în 2026, cifra de afaceri 4.000.000 lei și impozit pe profit datorat 60.000 lei. Prima valoare: 0,75% × 4.000.000 = 30.000 lei. A doua valoare: 20% × 60.000 = 12.000 lei. Plafonul deductibil e minimul: **12.000 lei** — aici impozitul pe profit e cel care limitează, nu cifra de afaceri. Dacă firma sponsorizează efectiv 20.000 lei, creditul din D101 este tot 12.000 lei — restul de 8.000 lei nu se poate scădea, în regimul actual, sub nicio formă suplimentară.
:::

## Ce se greșește în practică

- Se calculează o singură valoare (de obicei cea din cifra de afaceri) și se ignoră cealaltă — plafonul e mereu minimul dintre ele, nu un „ori-ori”.
- Se aplică procentul de 0,75% ca fiind valabil retroactiv — el se aplică doar din 3 februarie 2022; pentru sponsorizări din anii anteriori, procentul legal era 0,5%.
- Se calculează 20% dintr-o bază intermediară (de exemplu, profitul impozabil), nu din impozitul pe profit efectiv datorat.
- Se ignoră condiția de înscriere a beneficiarului nonprofit/cult în Registrul ANAF la data încheierii contractului — fără ea, plafonul calculat corect devine irelevant, pentru că întregul credit e nedatorat.

## Ce face iConta.eu

Funcția `plafon_credit(cifra_afaceri, impozit_profit, la_data=None)` din `core/sponsorizari.py` calculează exact formula de mai sus: `p1 = 0,75% × cifra_afaceri`, `p2 = 20% × impozit_profit`, iar rezultatul e `min(p1, p2)`. Pentru orice `la_data` din 2026, motorul folosește varianta curentă a regulii (singura înregistrată în `_VARIANTE_PLAFON_CREDIT`, activă din 01.01.2018 în sus, cu procentul de 0,75% aplicat pentru toate datele — atenție dacă recalculați retroactiv o perioadă anterioară lui 03.02.2022, unde procentul legal era, de fapt, 0,5%, nu 0,75%).

Funcția `credit_sponsorizare(...)` merge un pas mai departe: `credit = min(sponsorizari_efectuate, plafon)`, plus `redirectionabil_d177 = plafon - credit`, adică spațiul rămas care poate fi redirecționat separat, prin D177, din impozitul pe profit datorat.

[iConta.eu](/)
