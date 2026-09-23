---
title: 'Cheltuieli cu sponsorizarea: cum se deduce din impozitul pe profit'
description: Sponsorizarea nu se deduce din baza impozabilă, ca o cheltuială obișnuită — se scade direct din impozitul pe profit datorat, ca și credit fiscal, în limita minimului dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cheltuieli cu sponsorizarea: cum se deduce din impozitul pe profit

Sponsorizarea are un regim fiscal diferit de restul cheltuielilor firmei: nu reduce profitul impozabil (nu se scade din baza de calcul), ci se scade **direct din impozitul pe profit datorat**, sub formă de credit fiscal, până la un plafon legal. Diferența e importantă — o cheltuială dedusă din bază reduce impozitul cu doar 16% din valoarea ei (cota de impozit pe profit), în timp ce un credit fiscal reduce impozitul aproape „leu la leu”, în limita plafonului.

## Temeiul legal

::: ghid-temei
„i) cheltuielile de sponsorizare și/sau mecenat, acordate potrivit legii; contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea, cu modificările și completările ulterioare, și ale Legii bibliotecilor nr. 334/2002, republicată, cu modificările și completările ulterioare, scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele:
1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor;
2. valoarea reprezentând 20% din impozitul pe profit datorat. În cazul sponsorizărilor efectuate către entități persoane juridice fără scop lucrativ, inclusiv unități de cult, sumele aferente acestora se scad din impozitul pe profit datorat, în limitele prevăzute de prezenta literă, doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală (de la 03.02.2022).*
:::

## Mecanismul, pe scurt

1. Cheltuiala de sponsorizare (contul 6582 „Donații acordate”, folosit uzual și pentru sponsorizare) rămâne, în contabilitate, cheltuială nedeductibilă la calculul profitului impozabil — nu se scade din bază.
2. În schimb, suma sponsorizată (sau, dacă e mai mică, plafonul legal) se scade **direct din impozitul pe profit deja calculat**, ca un credit fiscal.
3. Plafonul e minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit datorat — se calculează ambele valori și se reține cea mai mică.
4. Dacă beneficiarul e o entitate fără scop lucrativ sau o unitate de cult, ea trebuie să fie înscrisă, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale (ANAF) — altfel creditul nu se acordă deloc pentru acea sponsorizare.

## Ce se greșește în practică

- Se tratează sponsorizarea ca pe o cheltuială deductibilă obișnuită, scăzând-o din baza impozabilă în loc să se calculeze creditul fiscal separat.
- Se scade din impozit întreaga sumă sponsorizată, fără a o compara mai întâi cu plafonul `min(0,75% CA; 20% impozit)`.
- Se omite verificarea Registrului ANAF pentru beneficiar la data încheierii contractului — fără această înscriere, creditul nu se acordă, indiferent de plafon.
- Se aplică procentul actual de 0,75% unei sponsorizări acordate înainte de 03.02.2022, când procentul legal era 0,5% din cifra de afaceri.

## Ce face iConta.eu

Funcția `credit_sponsorizare(cifra_afaceri, impozit_profit, sponsorizari_efectuate, tip_impozit="profit", beneficiar_in_registru=True, la_data=None)` din `core/sponsorizari.py` implementează exact acest mecanism: dacă `beneficiar_in_registru=False`, returnează credit 0, cu notă explicită de respingere; altfel, calculează plafonul prin `plafon_credit()` = `min(0,75% × cifra_afaceri, 20% × impozit_profit)`, apoi `credit = min(sponsorizari_efectuate, plafon)`. Diferența rămasă neconsumată din plafon (`redirectionabil_d177 = plafon - credit`) poate fi redirecționată separat, prin formularul D177, până la termenul de depunere a D101.

Nota contabilă a sponsorizării în sine se generează cu `nota_sponsorizare(suma, mod="contract"|"plata")`, pe contul 6582 „Donații acordate” (denumirea oficială din planul de conturi OMFP 1802/2014 — nu există un cont dedicat „sponsorizare”).

[iConta.eu](/)
