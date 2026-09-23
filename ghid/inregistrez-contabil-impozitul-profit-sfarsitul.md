---
title: Cum înregistrez contabil impozitul pe profit la sfârșitul trimestrului?
description: Impozitul pe profit trimestrial se înregistrează ca o cheltuială obișnuită, în contul 691, care se închide apoi în 121 — dar fiscal, aceeași sumă e expres nedeductibilă și trebuie adăugată înapoi la calculul impozitului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum înregistrez contabil impozitul pe profit la sfârșitul trimestrului?

Impozitul pe profit calculat pentru un trimestru nu se scade direct din rezultat printr-o ajustare invizibilă — se înregistrează explicit ca o cheltuială a perioadei, în contul 691, exact ca orice altă cheltuială, cu o singură particularitate fiscală importantă.

## Temeiul legal

::: ghid-temei
„Cu ajutorul acestui cont se ține evidența cheltuielilor cu impozitul pe profit. În debitul contului 691 «Cheltuieli cu impozitul pe profit» se înregistrează: valoarea impozitului pe profit (441)."
— OMFP 1802/2014, funcțiunea contului 691
:::

::: ghid-temei
„Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— Codul fiscal (Legea 227/2015), art. 41 alin. (1)
:::

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: a) cheltuielile proprii ale contribuabilului cu impozitul pe profit datorat, inclusiv cele reprezentând diferențe din anii precedenți sau din anul curent [...]."
— Codul fiscal (Legea 227/2015), art. 25 alin. (4) lit. a)
:::

Nota contabilă la sfârșitul fiecărui trimestru (pentru firmele care aplică sistemul trimestrial, conform art. 41 alin. (1)) e simplă: **691 = 441**, cu suma impozitului calculat pentru trimestrul respectiv. La finalul lunii, soldul debitor al contului 691 se închide, ca orice cont din clasa 6, în 121 (**121 = 691**), diminuând rezultatul contabil brut al perioadei.

Particularitatea reală e fiscală: deși e o cheltuială contabilă obișnuită, legea o exclude expres de la deducere (art. 25 alin. (4) lit. a)) — suma din 691 trebuie adăugată înapoi la calculul impozitului pe profit, ca să nu ajungă ca impozitul să-și reducă propria bază de calcul. Suma plătită trimestrial rămâne, în plus, o estimare: definitivarea impozitului pentru întregul an se face abia la termenul declarației anuale (D101, până la 25 iunie anul următor, art. 42 alin. (1)) — dacă regularizarea aduce o diferență, ea se înregistrează separat, în perioada corespunzătoare, nu retroactiv peste trimestrele deja închise.

## Ce se greșește în practică

- Se lasă suma din 691 „să curgă" în calculul impozitului pe profit fără ajustarea fiscală de la art. 25 alin. (4) lit. a) — se omite readăugarea cheltuielii la rezultatul fiscal, iar impozitul declarat iese mai mic decât cel real datorat.
- Se confundă termenul de plată trimestrială (art. 41) cu termenul de depunere a declarației anuale (art. 42) — depunerea declarației anuale nu amână obligația de plată trimestrială din cursul anului.
- Se folosește contul 691 și pentru firmele plătitoare de impozit pe veniturile microîntreprinderilor — acelea folosesc contul 698, distinct, pentru că se raportează diferit fiscal.

## Ce face iConta.eu

Motorul de închidere lunară al aplicației include soldul debitor al contului 691, alături de toate celelalte conturi de cheltuieli, în transferul către contul 121 — calculul e disponibil ca funcție pe care contabilul o aplică la momentul potrivit, nu se postează de la sine. La generarea declarației anuale de impozit pe profit (D101), aplicația verifică dacă există rulaj debitor pe contul 691 fără ca suma corespunzătoare să fi fost adăugată înapoi la rezultatul fiscal, și afișează un avertisment explicit dacă găsește o astfel de situație — nu completează automat rândul, pentru că decizia asupra cărei părți din soldul contului 691 aparține exact anului declarat rămâne o decizie fiscală a contabilului.

[iConta.eu](/)
