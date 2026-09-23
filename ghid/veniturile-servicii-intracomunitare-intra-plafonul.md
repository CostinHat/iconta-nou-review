---
title: Veniturile din servicii intracomunitare intră în plafonul micro?
description: Da — veniturile din serviciile facturate către un client din alt stat membru sunt venituri din activitatea economică a firmei și intră în calculul veniturilor totale pentru încadrarea ca microîntreprindere; e o regulă de impozit pe venit, distinctă de tratamentul de TVA al operațiunii.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Veniturile din servicii intracomunitare intră în plafonul micro?

Da. Locul prestării unui serviciu B2B intracomunitar (la sediul beneficiarului, conform art. 278 alin. (2) din Codul fiscal) decide **regimul de TVA** al operațiunii — dacă e neimpozabilă în România, dacă se declară în D390. Nu decide dacă venitul respectiv se cuprinde sau nu în **veniturile totale** pentru impozitul pe veniturile microîntreprinderilor. Sunt două impozite diferite, cu baze de calcul diferite.

## Temeiul legal

::: ghid-temei
„Nicio ramură de cod specifică regimului micro pentru operațiuni intracomunitare, în afara câmpurilor generice `operatiuni_ic`/`inreg_art317` din vectorul fiscal (…), care se aplică indiferent de regimul de impozitare (micro/profit).” — dosar F050, secțiunea „Microîntreprindere + IC” (cod sursă: `date_firma.js`, `core/control_fiscal_api.py`, confirmat și de `core/test_perimetru_firma_declarat.py`, care descrie un tenant de test „neplătitor micro cu achiziții intracomunitare”).
:::

Ce confirmă acest citat e faptul că, la nivel de aplicație, obligațiile legate de operațiunile intracomunitare (D390, verificarea VIES) nu depind de regimul de impozitare al firmei — se aplică la fel unei microîntreprinderi ca unei firme plătitoare de impozit pe profit. Regimul micro și existența operațiunilor intracomunitare sunt două perimetre independente.

**Notă de onestitate:** dosarul de cercetare F050 a fost construit pe latura de TVA a operațiunilor intracomunitare (art. 268, 278, 294, 308-309, 322, 325 din Codul fiscal) și nu conține un citat verificat din Titlul III al Codului fiscal (impozitul pe veniturile microîntreprinderilor). Răspunsul de mai sus e principiul general, cunoscut independent de regulile de TVA din acest dosar: veniturile din exploatare, indiferent dacă provin dintr-o operațiune internă sau intracomunitară, se cuprind în veniturile totale relevante pentru încadrare — sub rezerva excepțiilor limitativ enumerate în lege, care se verifică punctual la data la care se face încadrarea, separat de acest dosar.

## Ce se greșește în practică

Confuzia cea mai frecventă e să se creadă că o operațiune „specială” fiscal — pentru că trece prin VIES, D390 sau are un regim de TVA diferit — e automat exclusă și din calculul veniturilor pentru plafonul micro. Cele două nu sunt legate. La fel, nu se confundă acest plafon cu plafonul de 10.000 euro de la art. 268 din Codul fiscal, care e un prag de TVA pentru înregistrarea specială art. 317 a neplătitorilor la achizițiile intracomunitare de bunuri — un subiect complet diferit, tratat într-un alt ghid.

## Ce face iConta.eu

Câmpurile `operatiuni_ic` și `inreg_art317` din vectorul fiscal al firmei se aplică identic, indiferent dacă firma e la impozit pe veniturile microîntreprinderilor sau la impozit pe profit — nu există o ramură de cod care ar exclude sau ar trata diferit veniturile din operațiuni intracomunitare la calculul plafonului micro. Calculul propriu-zis al veniturilor totale pentru încadrarea sau menținerea ca microîntreprindere nu face parte din funcționalitatea F050 (operațiuni intracomunitare) cercetată aici — e o funcționalitate distinctă, de impozit pe venit, pe care acest dosar nu a verificat-o.

[iConta.eu](/)
