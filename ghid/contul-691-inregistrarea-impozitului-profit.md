---
title: "Contul 691 și înregistrarea impozitului pe profit: monografia"
description: Impozitul pe profit se înregistrează ca o cheltuială distinctă, în contul 691 — dar, spre deosebire de majoritatea cheltuielilor, ea nu este deductibilă fiscal.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Contul 691 și înregistrarea impozitului pe profit: monografia

Impozitul pe profit datorat de firmă nu se scade direct din rezultat printr-o notă „invizibilă" — el se înregistrează explicit ca o cheltuială, în contul 691, exact ca orice altă cheltuială a perioadei. Particularitatea lui este că, deși e o cheltuială contabilă, legea îl exclude expres de la deducerea fiscală.

## Temeiul legal

::: ghid-temei
„Cu ajutorul acestui cont se ține evidența cheltuielilor cu impozitul pe profit. În debitul contului 691 «Cheltuieli cu impozitul pe profit» se înregistrează: valoarea impozitului pe profit (441)."
— OMFP 1802/2014, funcțiunea contului 691
:::

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: a) cheltuielile proprii ale contribuabilului cu impozitul pe profit datorat, inclusiv cele reprezentând diferențe din anii precedenți sau din anul curent [...]."
— Codul fiscal (Legea 227/2015), art. 25 alin. (4) lit. a)
:::

Nota contabilă e simplă: **691 = 441**, cu suma impozitului pe profit calculat pentru perioadă (trimestru sau an, după sistemul de declarare ales). Contul 691 face parte din grupa 69 „Cheltuieli cu impozitul pe profit și alte impozite" și este distinct de contul 698 (folosit pentru impozitul pe venitul microîntreprinderilor) — cele două nu se confundă, pentru că se raportează diferit fiscal. La finalul lunii/anului, soldul debitor al contului 691 se închide, ca orice cont din clasa 6, în contul 121 (**121 = 691**), diminuând rezultatul contabil brut al perioadei.

Particularitatea reală a contului 691 este dublă. Contabil, e o cheltuială ca oricare alta, care scade profitul contabil. Fiscal însă, ea este expres nedeductibilă — ceea ce înseamnă că suma ei se adună înapoi la calculul impozitului pe profit (rândul corespunzător din D101), pentru a nu ajunge ca impozitul pe profit să-și reducă propria bază de calcul.

## Ce se greșește în practică

Cea mai frecventă greșeală este să se lase suma din 691 „să curgă" în calculul impozitului pe profit fără ajustarea fiscală prevăzută de art. 25 alin. (4) lit. a) — practic, se omite readăugarea acestei cheltuieli la rezultatul fiscal, iar impozitul declarat iese mai mic decât cel real datorat. O a doua greșeală este confuzia dintre 691 (impozit pe profit) și 698 (impozit pe venitul microîntreprinderilor): la o firmă care trece de la regimul de microîntreprindere la impozit pe profit (sau invers) în cursul anului, folosirea contului greșit pentru perioada corespunzătoare denaturează atât evidența, cât și declarația aferentă.

## Ce face iConta.eu

Aplicația verifică, la generarea declarației anuale de impozit pe profit (D101), dacă există rulaj debitor pe contul 691 fără ca suma corespunzătoare să fi fost adăugată înapoi la rezultatul fiscal (rândul din declarație prevăzut pentru cheltuieli nedeductibile cu impozitul pe profit). Dacă găsește o astfel de situație, afișează un avertisment explicit — nu completează automat rândul, pentru că decizia asupra cărei părți din soldul contului 691 aparține exact anului declarat rămâne o decizie fiscală a contabilului, nu una pe care motorul o poate lua singur.

[iConta.eu](/)
