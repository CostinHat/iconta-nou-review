---
title: "Amortizarea din perioada în care firma a fost micro se recuperează fiscal după trecerea la profit?"
description: "Ce spune Codul fiscal despre continuitatea amortizării mijloacelor fixe la trecerea de la impozitul pe veniturile microîntreprinderilor la impozitul pe profit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea din perioada în care firma a fost micro se recuperează fiscal după trecerea la profit?

Codul fiscal reglementează amortizarea fiscală ca mecanism de recuperare a valorii mijloacelor fixe prin deduceri — dar deducerea are sens doar la impozitul pe profit, unde există noțiunea de rezultat fiscal. Nu am găsit în sursele consultate o normă explicită care să trateze separat „amortizarea nededusă în perioada de micro" la trecerea la profit — explicăm mai jos ce rezultă din regulile generale ale amortizării.

## Temeiul legal

::: ghid-temei
„Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei [...]; c) are o durată normală de utilizare mai mare de un an."
— Legea nr. 227/2015, art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1), (2), (4) și (7) se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv."
— Legea nr. 227/2015, art. 52 alin. (6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă, cu limita clar marcată:

- Amortizarea fiscală (art. 28) e un mecanism care recuperează, prin **deduceri** la calculul rezultatului fiscal al impozitului pe profit, valoarea unui mijloc fix pe durata lui normală de utilizare — deducerea fiscală există numai atât timp cât firma e plătitoare de impozit pe profit, pentru că doar acolo există noțiunea de „cheltuială deductibilă din rezultatul fiscal".
- Cât timp firma a fost microîntreprindere, ea a plătit impozit pe veniturile realizate, fără a deduce fiscal cheltuiala cu amortizarea — regimul micro nu are un mecanism de deducere a cheltuielilor.
- Art. 52 alin. (6) spune că, la trecerea la profit, calculul se face „luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv" — adică amortizarea **continuă** de la valoarea fiscală rămasă neamortizată, pe durata normală de utilizare rămasă, ca pentru orice mijloc fix aflat deja în funcțiune.
- Nu am identificat însă în sursele consultate o prevedere explicită care să permită „recuperarea" retroactivă, prin deducere suplimentară, a amortizării calculate dar nededuse fiscal în anii de micro — interpretarea noastră, prudentă: amortizarea acelei perioade nu se recuperează separat, ci firma continuă pur și simplu amortizarea de la valoarea rămasă, fără compensație pentru anii în care deducerea nu a fost posibilă.

## Ce se greșește în practică

- Se presupune că, la trecerea la profit, firma poate deduce dintr-o dată toată amortizarea „acumulată" și nededusă din anii de micro — nu există un asemenea mecanism explicit în Codul fiscal.
- Se repornește greșit durata normală de utilizare de la zero la trecerea la profit, în loc să se continue de la valoarea fiscală rămasă și durata rămasă, stabilite o singură dată, la punerea în funcțiune.
- Se confundă amortizarea contabilă (care continuă neîntrerupt, indiferent de regimul fiscal) cu amortizarea fiscală deductibilă (relevantă doar la impozitul pe profit) — cele două nu coincid automat.

## Ce face iConta.eu

Modulul de amortizare a mijloacelor fixe din iConta.eu (`core/d406_active.py`) calculează amortizarea pe baza valorii de intrare, a duratei normale de utilizare și a datei de punere în funcțiune, continuu, indiferent de schimbarea regimului de impozitare (micro/profit) al firmei pe parcurs — aplicația nu introduce o „recuperare" suplimentară a amortizării din perioada de micro, pentru că nu am identificat temei legal explicit pentru un asemenea mecanism.

[iConta.eu](/)
