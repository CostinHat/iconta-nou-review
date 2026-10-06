---
title: "Cum se aplică limita de 50% la diferențele de curs din leasingul unui autoturism folosit mixt?"
description: "Limita de 50% se aplică doar pe diferența nefavorabilă netă dintre cheltuielile și veniturile din diferențe de curs ale contractului de leasing, nu pe cheltuiala brută."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Cum se aplică limita de 50% la diferențele de curs din leasingul unui autoturism folosit mixt?

La un autoturism în leasing în euro, folosit și în scop personal, diferențele de curs apar lunar: la reevaluarea datoriei și la plata ratelor. Codul fiscal nu cere să aplici 50% pe fiecare cheltuială cu diferențe de curs luată separat. Compensezi întâi **cheltuielile** cu **veniturile** din diferențe de curs aferente contractului de leasing, iar limita de 50% se aplică doar pe **diferența nefavorabilă** rezultată. Dacă veniturile depășesc cheltuielile, nu ai nimic de limitat.

Pentru alte contracte decât leasingul (de exemplu un credit bancar pentru mașină), diferențele de curs direct atribuibile vehiculului intră la limitare după regula generală a cheltuielilor auto, nu după compensarea specială de la leasing.

## Temeiul legal

::: ghid-temei
„În cazul cheltuielilor aferente vehiculelor rutiere motorizate reprezentând diferențe de curs valutar înregistrate ca urmare a derulării unui contract de leasing, limita de 50% se aplică asupra diferenței nefavorabile dintre veniturile din diferențe de curs valutar/veniturile financiare aferente creanțelor și datoriilor cu decontare în funcție de cursul unei valute, rezultate din evaluarea sau decontarea acestora și cheltuielile din diferențe de curs valutar/cheltuielile financiare aferente;"
— Codul fiscal (Legea 227/2015), art. 25 alin. (3) lit. l) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

::: ghid-temei
„În cadrul cheltuielilor aferente vehiculelor rutiere motorizate supuse limitării fiscale se cuprind cheltuielile direct atribuibile unui vehicul, cum sunt: impozitele locale, asigurarea obligatorie de răspundere civilă auto, inspecțiile tehnice periodice, rovinieta, chiriile, partea nedeductibilă din taxa pe valoarea adăugată, dobânzile, comisioanele, diferențele de curs valutar înregistrate ca urmare a derulării altor contracte decât cele de leasing. În cazul cheltuielilor reprezentând diferențe de curs valutar înregistrate ca urmare a derulării unui contract de leasing, limita de 50% se aplică asupra diferenței nefavorabile dintre veniturile din diferențe de curs valutar/veniturile financiare aferente datoriilor cu decontare în funcție de cursul unei valute, rezultate din evaluarea sau decontarea acestora, și cheltuielile din diferențe de curs valutar/cheltuielile financiare aferente."
— HG 1/2016, Normele metodologice, titlul II, pct. 16 alin. (3) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

Cum aplici regula:

- **separi** diferențele de curs aferente contractului de leasing al vehiculului supus limitării de celelalte diferențe de curs ale firmei;
- **compensezi**: cheltuieli din diferențe de curs (665) minus venituri din diferențe de curs (765), ambele aferente contractului;
- dacă rezultatul e **nefavorabil**, adică cheltuielile sunt mai mari, **50% din el e nedeductibil**;
- dacă rezultatul e **favorabil**, nu există cheltuială netă de limitat;
- amortizarea nu intră în această limitare. Codul spune expres că cheltuielile vizate de lit. l) nu includ amortizarea.

Codul fiscal actual vorbește de venituri aferente „creanțelor și datoriilor", normele doar de „datoriilor". La un contract de leasing financiar, locatarul are de regulă doar datoria față de finanțator, așa că în practică rezultatul e același.

Limitarea privește vehiculele până la 3.500 kg și cel mult 9 scaune, care nu sunt folosite exclusiv în scopul activității economice. Pentru vehiculele din categoriile exceptate (curierat, agenți de vânzări, taxi etc.) cheltuielile rămân integral deductibile.

::: ghid-exemplu
SC Exemplu SRL are un autoturism în leasing financiar în euro, folosit mixt. În anul fiscal, diferențele de curs aferente contractului sunt: cheltuieli 665 = 5.000 lei, venituri 765 = 1.800 lei. Diferența nefavorabilă: 5.000 - 1.800 = 3.200 lei. Nedeductibil: 3.200 x 50% = 1.600 lei. Greșit ar fi fost 5.000 x 50% = 2.500 lei nedeductibil, cu veniturile de 1.800 lei lăsate integral impozabile. Dacă veniturile ar fi fost de 6.000 lei, rezultatul ar fi fost favorabil și nu ar fi existat nicio sumă nedeductibilă din diferențe de curs.
:::

## Ce se greșește în practică

- Se aplică 50% pe totalul contului 665 aferent leasingului, fără compensarea cu 765.
- Diferențele de curs ale leasingului se amestecă cu cele ale furnizorilor sau clienților în valută, iar limita se aplică pe totalul firmei.
- Se aplică limita și la amortizarea autoturismului, deși codul o exclude din lit. l). Amortizarea are limita ei separată, de 1.500 lei pe lună pentru autoturismele de cel mult 9 scaune (art. 28 alin. (14)).
- Diferențele de curs la un credit bancar pentru mașină se tratează cu regula compensării de la leasing, deși normele o rezervă contractelor de leasing.

## Ce face iConta.eu

iConta.eu generează notele pentru leasingul financiar (primirea bunului, ratele, valoarea reziduală) și înregistrează diferențele de curs valutar în 665/765. Compensarea specială pentru leasingul auto și limita de 50% nu sunt calculate automat: suma nedeductibilă o determini tu, pe baza analiticului contractului, și o treci pe rândul de cheltuieli nedeductibile din D101, pe care aplicația o generează din balanță.

[iConta.eu](/)
