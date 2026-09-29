---
title: "Cum se rotunjește baza de calcul a impozitului pe venit datorat de persoanele fizice?"
description: "Baza de calcul a impozitului pe venit se rotunjește la leu: fracțiunile de până la 50 de bani inclusiv se neglijează, iar cele de peste 50 de bani se rotunjesc la leul următor."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Cum se rotunjește baza de calcul a impozitului pe venit datorat de persoanele fizice?

Baza de calcul a impozitului pe venit se rotunjește **la un leu**, după o regulă care diferă de rotunjirea matematică obișnuită. Fracțiunile de până la 50 de bani **inclusiv** se neglijează. Numai fracțiunile care **depășesc** 50 de bani se rotunjesc la leul următor. O bază de 1.234,50 lei devine deci 1.234 lei, nu 1.235 lei.

Regula se aplică la determinarea impozitului anual sau lunar pe veniturile persoanelor fizice din titlul IV al Codului fiscal: salarii, activități independente, cedarea folosinței bunurilor și celelalte categorii impozitate cu cota de 10%.

## Temeiul legal

::: ghid-temei
„În aplicarea prevederilor art. 64 din Codul fiscal, la determinarea impozitului anual/lunar, bazele de calcul al impozitului vor fi stabilite prin rotunjire la un leu, prin neglijarea fracțiunilor de până la 50 de bani inclusiv sau prin majorarea la leu a fracțiunilor ce depășesc 50 de bani.”
— HG 1/2016, Normele metodologice ale Codului fiscal, titlul IV pct. 4 (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„Cota de impozit este de 10% și se aplică asupra venitului impozabil corespunzător fiecărei surse din fiecare categorie pentru determinarea impozitului pe veniturile din:”
— Codul fiscal (Legea 227/2015), art. 64 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Sumele sunt calculate prin rotunjire la un leu, prin neglijarea fracțiunilor de până la 50 de bani inclusiv și majorarea la leu a fracțiunilor ce depășesc 50 de bani.”
— Codul fiscal (Legea 227/2015), art. 66 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret:

- **Se rotunjește baza, nu doar impozitul.** Venitul impozabil pe care se aplică cota de 10% se aduce mai întâi la leu întreg, apoi se calculează impozitul.
- **Pragul de 50 de bani e în favoarea contribuabilului.** Exact 50 de bani se neglijează. Numai 51 de bani sau mai mult duc la majorarea cu un leu.
- **Rotunjirea se face pe fiecare sursă și categorie.** Cota de 10% se aplică venitului impozabil din fiecare sursă, deci și rotunjirea bazei se face pe fiecare sursă, nu pe totalul veniturilor.
- **Aceeași metodă pentru sumele fixe.** Art. 66 din Codul fiscal folosește aceeași metodă pentru sumele fixe din titlul IV.
- **Atenție la alte titluri.** Alte capitole ale Codului fiscal au propriile reguli de rotunjire, uneori cu pragul de 50 de bani tratat invers. Regula de mai sus e cea din titlul IV, impozitul pe venit.

::: ghid-exemplu
Un salariat al SC Exemplu SRL are, într-o lună, după scăderea contribuțiilor și a deducerii personale, un venit impozabil de 3.456,50 lei.

- Baza rotunjită: 3.456 lei, pentru că fracțiunea de 50 de bani se neglijează.
- Impozit: 3.456 × 10% = 345,60 lei.

Dacă venitul impozabil ar fi fost de 3.456,51 lei, baza rotunjită ar fi fost 3.457 lei, iar impozitul 345,70 lei.
:::

## Ce se greșește în practică

- Se aplică rotunjirea matematică standard, în care 50 de bani urcă la leul următor, deși normele neglijează fracțiunea de exact 50 de bani.
- Se rotunjește doar impozitul final, iar baza de calcul rămâne cu bani.
- Se rotunjește totalul veniturilor din mai multe surse în loc de baza fiecărei surse.
- Se preia regula de rotunjire din alt titlu al Codului fiscal. De exemplu, art. 315^4 din titlul VII (TVA) majorează la leu și fracțiunea de exact 50 de bani.

## Ce face iConta.eu

iConta.eu calculează în modulul de salarizare contribuțiile și impozitul pe venit pentru fiecare salariat și pregătește declarația unică D212 pentru persoanele fizice. Motorul de salarizare nu aplică însă regula de la pct. 4 din norme: impozitul se calculează pe baza impozabilă cu bani, iar sumele din D112 se rotunjesc apoi aritmetic la leu. Pot apărea diferențe de un leu la impozitul declarat, așa că pe cazurile-limită rezultatul trebuie verificat de contabil.

[iConta.eu](/)
