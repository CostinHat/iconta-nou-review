---
title: Cum se deduce sponsorizarea din impozitul pe profit pe D101?
description: Sponsorizarea se scade direct din impozitul pe profit datorat, în limita minimului dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit, se declară în D101 a anului în care a fost acordată, iar spațiul neconsumat din plafon poate fi redirecționat separat prin D177, până la termenul de depunere a D101.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se deduce sponsorizarea din impozitul pe profit pe D101?

Sponsorizarea nu e o cheltuială care se deduce din baza impozabilă, ca protocolul sau alte cheltuieli — este un **credit fiscal**, scăzut direct din impozitul pe profit datorat, în limitele legii. Practic, asta înseamnă că suma sponsorizată reduce impozitul de plată aproape „leu la leu”, dar numai până la un plafon, iar rezultatul se reflectă în declarația 101.

## Temeiul legal

::: ghid-temei
„i) cheltuielile de sponsorizare și/sau mecenat, acordate potrivit legii; contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea, cu modificările și completările ulterioare, și ale Legii bibliotecilor nr. 334/2002, republicată, cu modificările și completările ulterioare, scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele:
1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor;
2. valoarea reprezentând 20% din impozitul pe profit datorat. În cazul sponsorizărilor efectuate către entități persoane juridice fără scop lucrativ, inclusiv unități de cult, sumele aferente acestora se scad din impozitul pe profit datorat, în limitele prevăzute de prezenta literă, doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală (de la 03.02.2022).*

„2. (1) Valoarea impozitului pe profit sau a diferenţei de impozit pe profit care poate fi redirecţionată se calculează prin scăderea din valoarea minimă stabilită, potrivit art. 25 alin. (4) lit. i) din Legea nr. 227/2015 privind Codul fiscal..., a sumelor reprezentând sponsorizare şi/sau mecenat, acordate entităţilor beneficiare în anul pentru care s-a depus declaraţia anuală de impozit pe profit, ..., şi a sumelor reportate, astfel cum au fost înscrise în formularul 101 «Declaraţie privind impozitul pe profit» a anului respectiv.”

„1. Plătitorii de impozit pe profit pot dispune redirecţionarea unor sume din impozitul datorat, potrivit legii, până la termenele legale de depunere a declaraţiei anuale de impozit pe profit [D101].”

— *OPANAF nr. 3562/2024, procedura D177.*
:::

## Pașii pentru deducerea corectă în D101

1. **Verificați eligibilitatea beneficiarului.** Dacă sponsorizarea merge către o entitate fără scop lucrativ (inclusiv unitate de cult), aceasta trebuie să fie înscrisă în Registrul entităților/unităților de cult **la data încheierii contractului** — nu la data plății și nu la data depunerii D101. Fără această înscriere, întregul credit e nedatorat, nu doar partea peste plafon.
2. **Calculați plafonul deductibil** ca `min(0,75% × cifra de afaceri; 20% × impozitul pe profit datorat)` pentru anul fiscal respectiv.
3. **Comparați plafonul cu suma efectiv sponsorizată** — creditul propriu-zis este cea mai mică dintre cele două valori.
4. **Reportați creditul în D101** a anului în care a fost acordată sponsorizarea, ca sumă care diminuează impozitul pe profit datorat.
5. **Dacă a rămas spațiu neconsumat** din plafon (sponsorizarea efectivă a fost sub plafon), puteți redirecționa separat, prin formularul **D177**, o sumă suplimentară din impozitul pe profit datorat, direct către un beneficiar eligibil — până la termenul legal de depunere a D101 a anului respectiv.

::: ghid-exemplu
O firmă cu cifra de afaceri 6.000.000 lei și impozit pe profit datorat 50.000 lei sponsorizează efectiv 15.000 lei o entitate înscrisă în Registru. Plafonul este `min(0,75% × 6.000.000; 20% × 50.000) = min(45.000; 10.000) = 10.000 lei`. În D101, firma scade din impozitul pe profit datorat 10.000 lei (nu cei 15.000 lei acordați efectiv — restul de 5.000 lei rămâne cheltuială nedeductibilă pe acest calcul, fără reportare în regimul actual). Nu mai are spațiu neconsumat pentru D177, pentru că a atins deja plafonul.
:::

## Ce se greșește în practică

- Se scade din impozitul pe profit direct suma sponsorizată, fără a o compara mai întâi cu plafonul `min(0,75% CA; 20% impozit)`.
- Se omite verificarea Registrului entităților/unităților de cult la data încheierii contractului, nu la altă dată.
- Se crede că D177 e o etapă obligatorie pentru orice sponsorizare — D177 servește doar pentru redirecționarea spațiului **neconsumat** din plafon, nu pentru declararea creditului propriu-zis, care se face în D101.
- Se depune D177 după termenul legal de depunere a D101 a anului respectiv, pierzând posibilitatea de redirecționare.
- Se aplică regula actuală (0,75%) unei sponsorizări acordate înainte de 03.02.2022, când plafonul era 0,5% din cifra de afaceri, cu reportare pe 7 ani, nu redirecționare D177.

## Ce face iConta.eu

Funcția `credit_sponsorizare(cifra_afaceri, impozit_profit, sponsorizari_efectuate, tip_impozit="profit", beneficiar_in_registru=True, la_data=None)` din `core/sponsorizari.py` calculează exact acest flux: dacă `beneficiar_in_registru=False`, returnează credit 0, cu o notă explicită de respingere; altfel, calculează `credit = min(sponsorizari_efectuate, plafon)` — unde `plafon` vine din `plafon_credit()`, ca `min(0,75% × cifra_afaceri, 20% × impozit_profit)` — și `redirectionabil_d177 = plafon - credit`, adică exact spațiul neconsumat pe care îl puteți redirecționa separat prin D177.

Acest calcul reflectă corect regula actuală (de la 03.02.2022), valabilă pentru anii fiscali curenți precum 2025–2026. Motorul aplică însă aceeași regulă de 0,75%/D177 indiferent de parametrul `la_data` transmis — pentru o D101 aferentă unui an fiscal anterior lui 2022, rezultatul automat nu este corect și trebuie recalculat manual cu regula valabilă atunci.

[iConta.eu](/)
