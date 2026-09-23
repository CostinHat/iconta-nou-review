---
title: "Cum se contabilizează restituirea împrumutului asociatului prin bancă?"
description: "Monografia pentru restituirea prin bancă a unui împrumut primit de la asociat, inclusiv dobânda și impozitul reținut la sursă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează restituirea împrumutului asociatului prin bancă?

Restituirea către asociat a unei sume pe care acesta a depus-o anterior cu titlu de împrumut presupune, dacă a fost stabilită și o dobândă, și reținerea unui impozit la sursă asupra dobânzii plătite.

## Temeiul legal

::: ghid-temei
„Sumele depuse sau lăsate temporar de către acționari/asociați la dispoziția entității, precum și dobânzile aferente, calculate în condițiile legii, se înregistrează în contabilitate în conturi distincte (contul 4551 «Acționari/asociați - conturi curente», respectiv contul 4558 «Acționari/asociați - dobânzi la conturi curente»)." — OMFP 1802/2014, pct. 349

„Cota de impozit este de 10% și se aplică asupra venitului impozabil corespunzător fiecărei surse din fiecare categorie pentru determinarea impozitului pe veniturile din: [...] d) investiții." — Codul fiscal, art. 64 alin. (1) lit. d), coroborat cu art. 91 lit. b) („Veniturile din investiții cuprind: [...] b) venituri din dobânzi")
:::

Restituirea sumei propriu-zise (capitalul împrumutat) stinge datoria firmei față de asociat pe contul 4551, fără impozit. Dacă părțile au stabilit și o dobândă, aceasta este o cheltuială financiară a firmei, iar suma plătită asociatului — persoană fizică — este un venit din investiții impozabil cu 10%, reținut la sursă de firmă.

## Ce se greșește în practică

Greșeala cea mai gravă este omiterea reținerii impozitului de 10% pe dobânda plătită asociatului, motivând că „e tot banii lui, pe care ni i-a împrumutat" — dobânda este totuși un venit distinct, impozabil separat de capitalul restituit. A doua greșeală este citarea unui temei legal greșit: art. 97^1 din Codul fiscal, care prevede tot o cotă de 10%, se aplică exclusiv dobânzilor la obligațiuni emise de societăți pe piețe de capital din afara României, nu dobânzii plătite unui asociat pentru un împrumut acordat firmei — pentru acest caz, temeiul corect este art. 64 alin. (1) lit. d) coroborat cu art. 91 lit. b).

## Ce face iConta.eu

Pentru operațiunea de restituire, motorul de decontări asociați generează mai multe linii, în funcție de datele introduse: restituirea capitalului (4551=5121), iar dacă a fost introdusă o dobândă, cheltuiala cu dobânda (666=4551), impozitul reținut la sursă — calculat implicit cu cota de 10%, dar configurabilă (4551=446) — și, în final, plata netă a dobânzii către asociat (4551=5121, diminuată cu impozitul reținut). Suma principalului restituit nu este supusă niciunui impozit în notă; doar componenta de dobândă este.

[iConta.eu](/)
