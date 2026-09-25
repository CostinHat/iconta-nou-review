---
title: "Prima declarație D112 a unei firme noi: cum o depun"
description: "Regula din Codul fiscal privind alegerea între depunerea lunară și cea trimestrială a D112 pentru o firmă nou-înființată, condiționată de o declarație estimativă la înregistrarea fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Prima declarație D112 a unei firme noi: cum o depun

O firmă nou-înființată nu e obligată automat la depunerea lunară a D112 — dacă se încadrează în anumite condiții și le declară din capul locului, poate opta pentru regimul trimestrial chiar din anul înființării, fără să aștepte un an fiscal complet de istoric.

## Temeiul legal

::: ghid-temei
„(4) Prin excepție de la prevederile alin. (1), plătitorii de venituri din salarii și asimilate salariilor prevăzuți la art. 80 alin. (2), în calitate de angajatori sau de persoane asimilate angajatorului, depun trimestrial Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate aferentă fiecărei luni a trimestrului, până la data de 25 inclusiv a lunii următoare trimestrului.
[...]
(10) Persoanele și entitățile prevăzute la art. 80 alin. (2) lit. b) și c) care se înființează în cursul anului aplică regimul trimestrial de declarare începând cu anul înființării dacă, odată cu declarația de înregistrare fiscală, declară că în cursul anului estimează un număr mediu de până la 3 salariați exclusiv și, după caz, urmează să realizeze un venit total de până la 100.000 euro."
— Legea 227/2015 (Codul fiscal), art. 147 alin. (4) și (10) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul pentru o firmă nouă, cu primul angajat:

- **Regula generală (alin. (1))**: D112 se depune lunar, până la data de 25 a lunii următoare celei pentru care se plătesc veniturile — acesta e regimul implicit, dacă nu se face nimic special.
- **Excepția trimestrială** se aplică, potrivit alin. (4), persoanelor juridice plătitoare de impozit pe profit cu venituri anuale sub 100.000 euro și maximum 3 salariați, respectiv persoanelor juridice la impozitul micro cu maximum 3 salariați (categoriile de la art. 80 alin. (2) lit. b) și c)).
- **Pentru o firmă nou-înființată, care nu are „anul anterior" cu care să se verifice pragurile**, alin. (10) oferă exact soluția: firma poate aplica regimul trimestrial **încă din anul înființării**, dar numai dacă, **odată cu declarația de înregistrare fiscală**, declară estimativ un număr mediu de până la 3 salariați și, dacă e cazul, un venit total estimat sub 100.000 euro.
- Fără această declarație estimativă la înregistrare, firma nouă rămâne, implicit, la regimul lunar, chiar dacă ulterior s-ar încadra în pragurile de la alin. (4).

## Ce se greșește în practică

- Se presupune că orice firmă nou-înființată depune automat lunar D112, fără verificarea opțiunii de la alin. (10), care poate simplifica declararea încă din primul an.
- Se încearcă trecerea la regimul trimestrial ulterior înființării, fără să se fi făcut declarația estimativă odată cu înregistrarea fiscală — condiția de la alin. (10) leagă opțiunea explicit de acel moment, nu de o cerere ulterioară.
- Se confundă condiția „maximum 3 salariați" cu numărul de salariați la un moment dat, deși testul, pentru firmele deja existente, se face ca medie aritmetică anuală (alin. (6)) — pentru firma nouă, testul e estimativ, declarat la înființare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează **D112** lunar, din datele salariale introduse de contabil (`core/d112.py`) — declarația se completează, ca formă, pentru fiecare lună, indiferent de periodicitatea de depunere aleasă. Nu am putut confirma din cod un mecanism care să verifice sau să semnaleze automat eligibilitatea unei firme nou-înființate pentru regimul trimestrial conform art. 147 alin. (10): alegerea periodicității, corelată cu declarația estimativă depusă la înregistrarea fiscală, rămâne o decizie pe care contabilul o ia și o urmărește separat.

[iConta.eu](/)
