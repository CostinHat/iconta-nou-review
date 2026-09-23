---
title: "Cum se declară în D205 impozitul pentru dividende neachitate până la sfârșitul anului?"
description: "Pașii practici pentru a nu pierde din D205 impozitul aferent unui dividend aprobat dar neplătit la 31 decembrie."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară în D205 impozitul pentru dividende neachitate până la sfârșitul anului?

Impozitul pe un dividend aprobat spre distribuire, dar neplătit asociaților până la 31 decembrie, se declară în D205 aferentă anului aprobării — chiar dacă suma nu a ajuns încă la asociat.

## Temeiul legal

::: ghid-temei
"Impozitul aferent dividendelor distribuite, dar care nu au fost plătite acționarilor sau asociaților până la sfârșitul anului în care s-a aprobat distribuirea acestora se cuprinde în declarația aferentă perioadei în care s-a aprobat distribuirea dividendelor."
— OPANAF 179/2022, instrucțiuni de completare D205 (`anaf_surse/opanaf_179_2022_d205_d207_baza.txt:381-400`), coroborat cu Codul fiscal art. 97 alin. (7) (`anaf_surse/cod_fiscal_227_2015_consolidat.txt:9470-9474`), care fixează scadența impozitului la 25 ianuarie a anului următor distribuirii.
:::

Practic, declarația trebuie să conțină, pentru anul aprobării: valoarea distribuită (coloana dedicată dividendului distribuit) și, separat, baza de impozitare și impozitul calculat pe partea neplătită, cu scadență de virare 25 ianuarie anul următor.

## Ce se greșește în practică

Se declară doar sumele deja plătite până la 31 decembrie, iar partea distribuită dar neîncasată de asociat rămâne complet în afara declarației — nu doar amânată, ci omisă.

## Ce face iConta.eu

Trebuie spus clar: generatorul automat D205 din iConta (`core/d205.py`) ia baza de calcul din dividendul efectiv plătit (citit din contul 457); pentru un beneficiar cu suma plătită zero, nu se generează automat nicio linie, deci impozitul aferent părții neachitate nu apare singur în XML. Acesta este un gol de conformitate cunoscut, nu o funcție care acoperă automat acest caz. iConta nu are momentan, în interfață, o opțiune de adăugare manuală a unui beneficiar la generarea D205, deci partea neachitată nu poate fi inclusă direct din aplicație — impozitul aferent trebuie calculat și declarat de contabil separat, cu baza și cota corespunzătoare anului distribuirii.

[iConta.eu](/)
