---
title: "Ce sistem de impozit pe profit aplică o firmă agricolă fără venituri majoritare din cereale și viticultură?"
description: "Firma agricolă care nu mai are venituri majoritare din cereale, plante tehnice, cartof, pomicultură sau viticultură trece, din anul următor, la regimul general: declarare și plată trimestrială."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Ce sistem de impozit pe profit aplică o firmă agricolă fără venituri majoritare din cereale și viticultură?

Regimul special de declarare anuală a impozitului pe profit e rezervat firmelor care obțin **venituri majoritare** din cultura cerealelor, a plantelor tehnice și a cartofului, din pomicultură și din viticultură. Ponderea se verifică la sfârșitul fiecărui an fiscal. Dacă veniturile majoritare vin din alte activități, cum ar fi zootehnia, legumicultura sau comerțul, firma aplică **din anul fiscal următor** sistemul general: calcul, declarare și plată trimestrială (art. 41 alin. (1) din Codul fiscal).

Faptul că firma rămâne „agricolă” după codul CAEN nu contează. Contează proveniența veniturilor.

## Temeiul legal

::: ghid-temei
„b) contribuabilii care obțin venituri majoritare din cultura cerealelor, a plantelor tehnice și a cartofului, pomicultură și viticultură au obligația de a declara și de a plăti impozitul pe profit anual, până la termenele prevăzute la art. 42”
— Codul fiscal (Legea 227/2015), art. 41 alin. (5) lit. b), în forma aplicabilă din anul fiscal 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III.”
— Codul fiscal (Legea 227/2015), art. 41 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„Verificarea ponderii veniturilor obținute de contribuabili din cultura cerealelor, a plantelor tehnice și a cartofului, pomicultură și viticultură se face la sfârșitul fiecărui an fiscal, iar în situația în care veniturile majoritare se obțin din alte activități decât cele menționate, aceștia vor aplica pentru anul fiscal următor sistemul trimestrial de declarare și plată a impozitului pe profit prevăzut la art. 41 alin. (1) din Codul fiscal.”
— HG 1/2016, Normele metodologice ale Codului fiscal, titlul II pct. 41 alin. (2) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5) [...] pot opta pentru calculul, declararea și plata impozitului pe profit anual, cu plăți anticipate, efectuate trimestrial.”
— Codul fiscal (Legea 227/2015), art. 41 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret:

- **Testul se face anual, la închiderea exercițiului.** Veniturile din activitățile enumerate se compară cu totalul veniturilor. Sub jumătate înseamnă că nu mai sunt „majoritare”.
- **Schimbarea produce efecte din anul următor.** Anul verificat se definitivează tot în regim anual. Din anul următor, firma declară și plătește trimestrial, până pe 25 a lunii de după trimestrele I-III, iar definitivarea se face prin D101.
- **Opțiunea pentru sistemul anual cu plăți anticipate.** Normele nu o menționează, dar o firmă care nu mai intră la art. 41 alin. (5) este unul dintre „contribuabilii, alții decât cei prevăzuți la alin. (4) și (5)” din art. 41 alin. (2). Poate opta deci pentru sistemul anual cu plăți anticipate trimestriale, cu condițiile de la alin. (3): opțiune la începutul anului, obligatorie pentru cel puțin 2 ani, comunicată până la 31 ianuarie. Dacă normele și Codul fiscal nu spun același lucru, se aplică textul Codului fiscal.
- **Excepții de la opțiune.** Art. 41 alin. (6) obligă la sistemul trimestrial anumite firme, de exemplu pe cele care în anul precedent au avut pierdere fiscală sau nu au datorat impozit pe profit.

::: ghid-exemplu
SC Exemplu SRL are în 2026 venituri totale de 2.000.000 lei: 800.000 lei din cultura cerealelor și 1.200.000 lei din creșterea animalelor. Veniturile din cereale reprezintă 40%, deci nu sunt majoritare.

- Pentru 2026, dacă a aplicat regimul anual de la art. 41 alin. (5) lit. b) pe baza verificării pentru anul precedent, firma definitivează impozitul prin D101 anual.
- Pentru 2027, trece la sistemul trimestrial și declară și plătește în D100 până la 25 aprilie, 25 iulie și 25 octombrie 2027. Alternativ, dacă îndeplinește condițiile, poate comunica până la 31 ianuarie 2027 opțiunea pentru sistemul anual cu plăți anticipate.
:::

## Ce se greșește în practică

- Firma rămâne în regimul anual doar pentru că are cod CAEN agricol, deși veniturile majoritare vin din zootehnie sau din comerț.
- Ponderea se verifică pe venituri din anul curent, în cursul anului, și sistemul se schimbă imediat. Normele cer verificarea la sfârșitul anului și schimbarea din anul următor.
- Se consideră că singura alternativă e sistemul trimestrial și se ignoră opțiunea de la art. 41 alin. (2).
- Opțiunea pentru sistemul anual cu plăți anticipate se comunică după 31 ianuarie.

## Ce face iConta.eu

iConta.eu generează D100 pentru impozitul pe profit în sistemul trimestrial, pe baza profitului cumulat de la începutul anului, și D101 anual, ambele validate pe validatorul oficial ANAF. Aplicația nu verifică automat ponderea veniturilor din activitățile de la art. 41 alin. (5) lit. b) și nu comută singură sistemul de declarare. Încadrarea firmei rămâne decizia contabilului, pe baza veniturilor anului încheiat.

[iConta.eu](/)
