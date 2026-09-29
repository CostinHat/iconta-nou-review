---
title: "Limitele cheltuielilor deductibile se aplică trimestrial sau anual la impozitul pe profit?"
description: "Depinde de sistemul de plată: la plătitorii trimestriali, limitele se aplică trimestrial, cumulat, și se regularizează la finalul anului; la sistemul anual, limitele se aplică anual."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Limitele cheltuielilor deductibile se aplică trimestrial sau anual la impozitul pe profit?

Depinde de sistemul de declarare și plată al firmei. Dacă firma plătește impozitul pe profit trimestrial, limitele (protocol, sponsorizare și celelalte cheltuieli cu deductibilitate limitată) se aplică la fiecare trimestru, pe rezultatul cumulat de la începutul anului, astfel încât la finalul anului totalul să se încadreze în limitele legii. Dacă firma a optat pentru sistemul anual, cu plăți anticipate, limitele se aplică o singură dată, la nivelul anului.

Contează în practică pentru că, la plătitorul trimestrial, o cheltuială de protocol făcută în primul trimestru poate depăși limita în T1 și poate încăpea la sfârșitul anului, când baza cumulată e mai mare. Suma nedeductibilă calculată pe parcursul anului se recalculează la fiecare trimestru.

## Temeiul legal

::: ghid-temei
„La calculul rezultatului fiscal al contribuabililor care plătesc trimestrial impozit pe profit, limitele cheltuielilor deductibile se aplică trimestrial, astfel încât, la finele anului acestea să se încadreze în prevederile titlului II din Codul fiscal. Pentru contribuabilii care plătesc impozitul pe profit anual, limitele cheltuielilor deductibile prevăzute de titlul II din Codul fiscal se aplică anual."
— Normele metodologice (HG 1/2016), Titlul II, pct. 5 alin. (5) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„Rezultatul fiscal se calculează trimestrial/anual, cumulat de la începutul anului fiscal."
— Codul fiscal (Legea 227/2015), art. 19 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
„Contribuabilii, alții decât cei prevăzuți la alin. (4) [...] pot opta pentru calculul, declararea și plata impozitului pe profit anual, cu plăți anticipate, efectuate trimestrial."
— Codul fiscal (Legea 227/2015), art. 41 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret:

- **Sistemul trimestrial** (regula, art. 41 alin. (1)): la fiecare trimestru, limitele se calculează pe baza cumulată de la 1 ianuarie. Rezultatul de la T2 include T1 și așa mai departe. Nedeductibilul se recalculează de fiecare dată.
- **Sistemul anual cu plăți anticipate** (opțiune, art. 41 alin. (2)): plățile anticipate trimestriale nu presupun calculul limitelor pe trimestru. Limitele se aplică anual, la definitivarea impozitului.
- **Opțiunea pentru sistemul anual** se face la începutul anului, este obligatorie cel puțin 2 ani consecutivi și se comunică organului fiscal până la 31 ianuarie (art. 41 alin. (3)).
- **Pentru fiecare limită,** baza de calcul este cea din articolul care o stabilește. De exemplu, protocolul se raportează la profitul contabil la care se adaugă cheltuielile cu impozitul pe profit și cheltuielile de protocol (art. 25 alin. (3) lit. a)).

::: ghid-exemplu
SC Exemplu SRL plătește impozitul pe profit trimestrial. Limita pentru protocol este de 2% din profitul contabil, la care se adaugă cheltuielile cu impozitul pe profit și cheltuielile de protocol.

- **T1 (cumulat):** profit contabil de 34.000 lei, impozit pe profit de 10.000 lei, protocol de 6.000 lei. Baza este de 50.000 lei, iar limita este 1.000 lei. Sunt nedeductibili 5.000 lei.
- **31 decembrie (cumulat):** profit contabil de 284.000 lei, impozit pe profit de 60.000 lei, protocol de 6.000 lei (niciun protocol nou după T1). Baza este de 350.000 lei, iar limita este 7.000 lei. Tot protocolul este deductibil, iar calculul anual regularizează nedeductibilul din T1.

Dacă firma ar fi fost în sistemul anual, calculul s-ar fi făcut o singură dată, la 31 decembrie.
:::

## Ce se greșește în practică

- Limitele se calculează pe trimestrul izolat, nu cumulat de la începutul anului. Codul fiscal cere calcul cumulat.
- La sistemul anual, firmele aplică limitele trimestrial la plățile anticipate, deși norma spune că limitele se aplică anual.
- Nedeductibilul din trimestrele anterioare nu se recalculează la sfârșitul anului, iar suma rămâne dublată sau greșit reportată.
- Se trece de la un sistem la altul în cursul anului. Opțiunea se exercită la începutul anului și este obligatorie cel puțin 2 ani.

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit trimestrial pe baza profitului contabil cumulat de la începutul anului (declarația D100, cod 103), fără ajustări fiscale, și generează declarația anuală D101, validată pe validatorul oficial ANAF. Ajustările fiscale, inclusiv partea nedeductibilă a cheltuielilor cu limită, le introduce contabilul în D101; calculul trimestrial din D100 nu le aplică. Aplicația nu calculează automat limitele pentru fiecare categorie de cheltuială.

[iConta.eu](/)
