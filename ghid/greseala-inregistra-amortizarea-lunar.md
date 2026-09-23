---
title: "Greșeala de a nu înregistra amortizarea lunar"
description: "De ce omiterea notelor lunare de amortizare nu produce o eroare permanentă, datorită calculului cumulat la zi."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu înregistra amortizarea lunar

O practică defectuoasă frecventă e amânarea înregistrării amortizării lunare — dar registrul de mijloace fixe nu depinde de disciplina acestor înregistrări pentru a arăta suma corectă.

## Temeiul legal

::: ghid-temei
"Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);"
— Codul fiscal, art.28 alin.(12) lit.a
:::

Amortizarea "la zi" e definită ca sumă cumulată de la PIF până la data cerută, pe metoda reală a activului. Practic, nu contează dacă notele lunare au fost postate consecvent — la orice moment ulterior, valoarea cumulată corectă poate fi obținută direct din calculul motorului de amortizare.

## Ce se greșește în practică

Amânarea lunară a înregistrărilor duce la un decalaj tot mai mare între ce arată contabilitatea și ce ar trebui să arate — deși recuperabil, decalajul complică urmărirea și crește riscul de eroare la reconciliere.

## Ce face iConta.eu

Funcțiile de calcul (`amortizat_la_data` pentru cumulat, `amortizare_luna` pentru o singură lună) sunt independente de istoricul înregistrărilor contabile efective — recalculează mereu corect pe baza PIF, valorii și metodei activului. Aceasta e valoarea folosită uniform de registru, de nota lunară, de casare și de reevaluare.

[iConta.eu](/)
