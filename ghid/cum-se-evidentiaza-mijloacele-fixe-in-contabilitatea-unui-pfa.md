---
title: Cum se evidențiază mijloacele fixe în contabilitatea unui PFA?
description: Mijloacele fixe ale unui PFA se evidențiază prin Fișa mijlocului fix (cod 14-2-2) individual, pentru fiecare activ, și se regăsesc, la valoare rămasă, în Registrul-inventar (cod 14-1-2/b), alături de toate celelalte bunuri, drepturi și obligații ale afacerii.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se evidențiază mijloacele fixe în contabilitatea unui PFA?

Un PFA care deține echipamente, utilaje, mobilier sau un autoturism amortizabil are două obligații distincte de evidență, care se completează reciproc: o fișă individuală per activ și o poziție a acelui activ în inventarul general al afacerii.

## Temeiul legal

::: ghid-temei
OMFP 170/2015, Cap. III, pct. 17: "Evidența imobilizărilor corporale (mijloace fixe) se ține cu ajutorul Fişei mijlocului fix (cod 14-2-2)."

OMFP 170/2015, Cap. V: "Registrul-inventar serveşte ca document contabil de înregistrare a elementelor de natura activelor şi datoriilor inventariate ... se completează la începutul activității, la sfârşitul exercițiului financiar, precum şi cu ocazia încetării activității."

HG 1/2016 (Norme metodologice), pct. 7 alin. (8): "În aplicarea prevederilor art. 68 din Codul fiscal, toate bunurile, drepturile și obligațiile aferente desfășurării activității se înscriu în Registrul-inventar și constituie patrimoniul afacerii."

Codul fiscal, art. 28 alin. (2): "Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului; c) are o durată normală de utilizare mai mare de un an."
:::

## Fișa mijlocului fix + Registrul-inventar, nu unul în locul celuilalt

Fișa mijlocului fix (cod 14-2-2) este documentul individual, per activ: urmărește istoricul unui singur mijloc fix — data intrării, valoarea, amortizarea acumulată. Registrul-inventar (cod 14-1-2/b) este imaginea de ansamblu a patrimoniului afacerii la un moment dat: cuprinde toate bunurile, drepturile și obligațiile, inclusiv mijloacele fixe (la valoarea lor rămasă, nu la valoarea de achiziție) și disponibilitățile bănești. Cele două documente nu se substituie unul altuia — un PFA cu mai multe mijloace fixe are câte o fișă pentru fiecare, plus un singur Registru-inventar care le însumează.

## Ce se greșește în practică

- Se ține doar o listă generală de bunuri, fără fișă individuală pentru fiecare mijloc fix, deși legea cere document separat per activ.
- Se trece în Registrul-inventar valoarea de achiziție a mijlocului fix, nu valoarea rămasă (neamortizată) — Registrul-inventar reflectă starea patrimoniului la data completării, nu istoricul achiziției.
- Nu se completează Registrul-inventar la finalul fiecărui exercițiu financiar, ci doar o dată, la începutul activității.
- Se omit din Registrul-inventar bunurile complet amortizate, deși ele rămân în patrimoniul afacerii (chiar și la valoare reziduală zero) până la casare sau vânzare.
- Se evidențiază mijlocul fix doar în contabilitate, fără să fie corelat cu disponibilitățile bănești din Registrul-jurnal, deși Registrul-inventar trebuie să cuprindă ambele elemente pentru a reflecta totalul activului.

## Ce face iConta.eu

Funcția `registru_inventar(conn, schema, an)` din `core/rip_api.py` construiește automat Registrul-inventar (cod 14-1-2/b): calculează mijloacele fixe la valoare rămasă (aplicând amortizarea liniară pe lunile scurse din durata normală de funcționare, `dnf_luni`) și le însumează cu disponibilitățile bănești — soldul Registrului-jurnal de încasări și plăți, validat și cumulat până la 31 decembrie — obținând totalul activului. Evidența individuală a fiecărui mijloc fix (echivalentul Fișei mijlocului fix) se ține în tabela `mijloace_fixe`, populată prin `core/mijloace_fixe_import_api.py`; `registru_inventar()` citește aceste date ca atare, fără să reverifice încadrarea inițială a bunului ca mijloc fix.

[iConta.eu](/)
