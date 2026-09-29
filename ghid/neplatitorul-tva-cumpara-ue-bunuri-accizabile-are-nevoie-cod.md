---
title: "Neplătitorul de TVA care cumpără din UE bunuri accizabile are nevoie de cod special de TVA?"
description: "Nu. Firma neînregistrată care face achiziții intracomunitare de produse accizabile nu se înregistrează conform art. 317, dar datorează TVA în România și o declară prin decontul special D301."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Neplătitorul de TVA care cumpără din UE bunuri accizabile are nevoie de cod special de TVA?

Nu. Normele Codului fiscal spun expres că firma neînregistrată conform art. 316 nu are obligația să ceară cod special de TVA (art. 317) pentru achizițiile intracomunitare de bunuri accizabile. Regula e aceeași pentru o persoană juridică neimpozabilă. Asta nu înseamnă că achiziția e scutită. TVA se datorează în România și se plătește prin **decontul special de taxă (D301)**.

Diferența față de alte bunuri e importantă. La bunurile obișnuite, un neplătitor sub plafonul de 10.000 euro pentru achiziții intracomunitare nu datorează TVA în România. La produsele accizabile plafonul nu contează. Achiziția e impozabilă în România de la primul leu.

## Temeiul legal

::: ghid-temei
„Persoana impozabilă sau persoana juridică neimpozabilă care nu este înregistrată conform art. 316 din Codul fiscal și care efectuează achiziții intracomunitare de bunuri accizabile nu are obligația să se înregistreze conform art. 317 din Codul fiscal pentru plata taxei aferente respectivei achiziții intracomunitare.”
— Normele metodologice ale Codului fiscal (HG 1/2016), titlul VII, pct. 90 alin. (8) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„o achiziție intracomunitară de produse accizabile, efectuată de o persoană impozabilă, care acționează ca atare, sau de o persoană juridică neimpozabilă.”
— Codul fiscal (Legea 227/2015), art. 268 alin. (3) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„Decontul special de taxă se depune la organele fiscale competente de către persoanele care nu sunt înregistrate și care nu trebuie să se înregistreze conform art. 316 , astfel: […] c) pentru achiziții intracomunitare de produse accizabile, de către persoanele impozabile și persoanele juridice neimpozabile, indiferent dacă sunt sau nu înregistrate conform art. 317;”
— Codul fiscal (Legea 227/2015), art. 324 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce reiese din cele trei texte:

- **Operațiunea e impozabilă în România.** Art. 268 alin. (3) lit. c) o include separat în operațiunile impozabile. Nu i se aplică excepția de la alin. (4) pentru neplătitorii sub plafon. Plafonul de 10.000 euro nici nu cuprinde bunurile accizabile (art. 268 alin. (5)).
- **Nu se cere cod special.** Pct. 90 alin. (8) din norme scutește firma de înregistrarea conform art. 317 pentru această achiziție.
- **TVA se declară în D301.** Decontul special se depune până pe 25 inclusiv ale lunii următoare celei în care ia naștere exigibilitatea (art. 324 alin. (2)). Obligația există indiferent dacă firma are sau nu cod special.
- **Neplătitorul nu deduce.** Firma în regimul de scutire nu are drept de deducere, deci TVA plătită din D301 devine cost al achiziției.

Obligațiile legate de accize, cum ar fi statutul de destinatar, documentele de circulație și plata accizei, țin de regimul accizelor. Se analizează separat de TVA.

::: ghid-exemplu
SC Exemplu SRL, neplătitoare de TVA, administrează o pensiune. În aprilie cumpără din Italia vin în valoare de 5.000 lei, fără TVA, cu exigibilitatea în aprilie. Nu are alte achiziții intracomunitare în an.

- Nu cere cod special de TVA pentru această achiziție.
- Achiziția e impozabilă în România, deși e mult sub plafonul de 10.000 euro.
- TVA datorată e de 5.000 × 21% = 1.050 lei. Se declară în D301 până pe 25 mai și se plătește în același termen.
- Costul vinului în contabilitate e de 6.050 lei, pentru că TVA nu se deduce.
:::

## Ce se greșește în practică

- Se aplică și la produsele accizabile regula plafonului de 10.000 euro, iar achiziția se tratează ca netaxabilă în România.
- Se cere cod special de TVA doar pentru această achiziție, deși norma nu îl cere.
- Se uită D301 pentru că firma „nu are cod de TVA”. Art. 324 alin. (1) lit. c) îl cere indiferent de cod.
- TVA plătită se trece ca deductibilă, deși firma e neplătitoare.

## Ce face iConta.eu

iConta.eu generează D301, decontul special de TVA, cu ecran de introducere a operațiunilor pe tipurile oficiale, inclusiv „Achiziții intracomunitare de produse accizabile”. Cota se aplică după data operațiunii, iar XML-ul se validează înainte de depunere. Depunerea o faci din SPV, cu XML-ul verificat de iConta.eu. Obligațiile de accize nu sunt tratate de aplicație.

[iConta.eu](/)
