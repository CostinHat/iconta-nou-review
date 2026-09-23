---
title: Cum corectez o factură după depunerea D101
description: iConta.eu nu leagă în niciun fel depunerea D101 de corectarea facturilor. Corectarea facturii se face prin storno, independent de D101; dacă factura corectată schimbă rezultatul fiscal deja declarat, ajustarea acelui rezultat se face separat, prin D101 rectificativă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o factură după depunerea D101

D101 e declarația anuală de impozit pe profit — un rezumat al unui exercițiu financiar întreg, depus o dată pe an. Spre deosebire de D112 (care blochează editarea pontajului lunii), depunerea D101 nu declanșează niciun blocaj automat în iConta.eu, nici pentru facturi, nici pentru altceva. Sunt, de fapt, două întrebări diferite, ușor de confundat: cum corectez factura, și cum corectez ce am declarat deja la ANAF pe baza ei.

## Corectarea facturii, în sine

Aici răspunsul nu depinde deloc de D101: o factură emisă se corectează prin storno — o factură nouă, cu cantitățile negate, datată la momentul corecției, în luna curentă (deschisă). Dacă luna facturii originale e blocată prin „Blocare perioade" (F118), stornoul funcționează exact la fel, pentru că e datat oricum azi, nu în luna veche.

## Corectarea rezultatului fiscal deja declarat

Dacă factura corectată schimbă baza de calcul a impozitului pe profit pentru un an deja declarat prin D101, cele două lucruri nu se rezolvă automat unul din celălalt — stornarea facturii nu retrimite singură o D101 nouă. Ajustarea rezultatului fiscal al anului respectiv se face separat, prin declarație rectificativă.

## Temeiul legal

::: ghid-temei
„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale." — Legea nr. 207/2015 privind Codul de procedură fiscală, art. 105 alin. (1)

„Dreptul organului fiscal de a stabili creanțe fiscale se prescrie în termen de 5 ani, cu excepția cazului în care legea dispune altfel." — Legea nr. 207/2015, art. 110 alin. (1)
:::

Termenul de 5 ani curge, potrivit aceluiași articol, de la 1 iulie a anului următor celui pentru care se datorează obligația fiscală — deci o D101 rectificativă pentru anul X se poate depune, în regula generală, până la 1 iulie din X+6.

## Ce se greșește în practică

- Se amână corectarea facturii, crezând că „nu se mai poate face nimic" odată ce D101 a fost depusă — factura, ca atare, se corectează oricând, prin storno; problema separată e dacă rezultatul fiscal declarat trebuie și el ajustat.
- Se rectifică D101 fără să se evalueze mai întâi dacă suma e semnificativă — pentru sume mici, costul administrativ al unei rectificative poate depăși beneficiul, o decizie profesională, nu una tehnică.
- Se caută în aplicație un mesaj de blocare legat de D101 — nu există, pentru că nicio verificare din cod nu leagă starea D101 de corectarea facturilor.

## Ce face iConta.eu

Corectarea unei facturi funcționează identic, indiferent dacă D101 a fost sau nu depusă pe anul respectiv: se stornează, cu factura nouă datată la momentul corecției. Aplicația nu urmărește automat legătura dintre o corecție de factură și necesitatea unei D101 rectificative — decizia de a rectifica declarația anuală, atunci când suma o justifică, rămâne un pas separat, luat de contabil, în termenul legal de prescripție.

[iConta.eu](/)
