---
title: Cum calculez suma care poate fi scăzută pentru sponsorizare?
description: Suma deductibilă este minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit datorat — calculați ambele valori separat și rețineți-o pe cea mai mică; la microîntreprinderi, facilitatea a fost abrogată de la 01.01.2024 și nu mai există în 2026.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum calculez suma care poate fi scăzută pentru sponsorizare?

Calculul plafonului de sponsorizare deductibil se face în doi pași simpli — dar greșeala tipică este să vă opriți la primul rezultat obținut, în loc să îl comparați cu al doilea. Mai jos, formula completă și câteva scenarii numerice, pentru firme plătitoare de impozit pe profit.

## Temeiul legal

::: ghid-temei
„i) ... contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea..., scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele:
1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor;
2. valoarea reprezentând 20% din impozitul pe profit datorat. În cazul sponsorizărilor efectuate către entități persoane juridice fără scop lucrativ, inclusiv unități de cult, sumele aferente acestora se scad din impozitul pe profit datorat, în limitele prevăzute de prezenta literă, doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală.*
:::

## Formula, pas cu pas

1. **Calculați prima valoare:** `0,75% × cifra de afaceri` a firmei.
2. **Calculați a doua valoare:** `20% × impozitul pe profit datorat` (pentru trimestrul/anul respectiv, în funcție de momentul la care faceți calculul).
3. **Rețineți valoarea mai mică** dintre cele două — acesta este plafonul deductibil.
4. **Comparați plafonul cu suma efectiv sponsorizată.** Creditul fiscal propriu-zis este minimul dintre plafon și suma efectiv acordată — dacă sponsorizați mai puțin decât plafonul, creditul e egal cu suma acordată; dacă sponsorizați mai mult, creditul se oprește la plafon.

::: ghid-exemplu
**Scenariul 1 — limitează cifra de afaceri.** Firmă mică, cu profit mare: cifra de afaceri 1.000.000 lei, impozit pe profit datorat 100.000 lei. Prima valoare: 0,75% × 1.000.000 = 7.500 lei. A doua valoare: 20% × 100.000 = 20.000 lei. Plafonul este minimul: **7.500 lei** — aici cifra de afaceri e cea care limitează, nu impozitul.

**Scenariul 2 — limitează impozitul pe profit.** Firmă mare, cu profit mic: cifra de afaceri 20.000.000 lei, impozit pe profit datorat 5.000 lei. Prima valoare: 0,75% × 20.000.000 = 150.000 lei. A doua valoare: 20% × 5.000 = 1.000 lei. Plafonul este minimul: **1.000 lei** — de data asta impozitul pe profit mic e cel care limitează, indiferent cât de mare e cifra de afaceri.

**Scenariul 3 — sponsorizarea consumă doar parțial plafonul.** O firmă cu plafon calculat de 12.000 lei sponsorizează efectiv doar 4.000 lei. Creditul din D101 este 4.000 lei (întreaga sumă acordată, pentru că e sub plafon), iar cei 8.000 lei rămași neconsumați din plafon pot fi redirecționați separat, prin D177, direct din impozitul pe profit datorat, până la termenul de depunere a D101.
:::

## Ce se greșește în practică

- Se calculează o singură valoare (de obicei cea din cifra de afaceri) și se ignoră cealaltă — rezultatul corect e mereu minimul dintre cele două.
- Se calculează 20% dintr-un impozit pe profit greșit — de exemplu, dintr-o bază de impozitare intermediară, nu din impozitul pe profit efectiv datorat.
- Se aplică formula de mai sus unei microîntreprinderi — facilitatea de la impozitul micro a fost abrogată de la 01.01.2024 și nu mai există în 2026; formula 0,75%/20% este specifică exclusiv impozitului pe profit.
- Se confundă „suma efectiv sponsorizată” cu „plafonul deductibil” — creditul e minimul dintre ele, nu automat suma acordată.
- Se aplică procentul de 0,75% unei sponsorizări acordate înainte de 03.02.2022, când procentul legal era 0,5%.

## Ce face iConta.eu

Funcția `plafon_credit(cifra_afaceri, impozit_profit, la_data=None)` din `core/sponsorizari.py` calculează exact acest lucru: `p1 = 0,75% × cifra_afaceri`, `p2 = 20% × impozit_profit`, iar rezultatul e `min(p1, p2)`. Funcția `credit_sponsorizare(...)` merge un pas mai departe și aplică pasul 4 de mai sus: `credit = min(sponsorizari_efectuate, plafon)`, plus `redirectionabil_d177 = plafon - credit` pentru spațiul rămas.

Un detaliu de reținut dacă folosiți motorul și pentru calculul de la microîntreprinderi: parametrul `impozit_profit` este redenumit implicit în ramura `tip_impozit="micro"` a funcției — acolo el reprezintă impozitul micro datorat **pe trimestru**, nu un impozit anual, iar plafonul nu mai are componentă legată de cifra de afaceri. Introduceți valoarea corectă pentru fiecare ramură, ca să nu obțineți un plafon calculat greșit.

[iConta.eu](/)
