---
title: "Cum se raportează vânzarea unui mijloc fix în D406?"
description: "Fereastra de raportare anuală a secțiunii Active din SAF-T (D406) și legătura ei cu ieșirea unui mijloc fix din evidență prin vânzare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează vânzarea unui mijloc fix în D406?

Secțiunea „Active" din SAF-T se raportează o singură dată pe an, la nivelul întregului exercițiu financiar — vânzarea unui mijloc fix în cursul anului se reflectă în acea raportare anuală, nu într-o depunere separată, la momentul vânzării.

## Temeiul legal

::: ghid-temei
„Informațiile privind «Activele» din cadrul Declarației informative D406 sunt întocmite la nivelul anului financiar aplicat de către contribuabili și transmise printr-o singură depunere, respectiv o singură raportare a Declarației informative D406, până la data depunerii situațiilor financiare aferente exercițiului financiar la care se referă. Declarația informativă D406 pentru «Active» se poate transmite ca o declarație independentă, nefiind necesară introducerea tuturor secțiunilor/subsecțiunilor dintr-o Declarație informativă D406, ci doar a zonelor indicate ca fiind obligatorii pentru transmiterea acestui tip de informație."
— OPANAF nr. 1.783/2021, Anexa 5, pct. 7-8 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce rezultă pentru situația unei vânzări de mijloc fix:

- Raportarea „Active" în SAF-T e **anuală**, nu lunară/trimestrială ca restul D406 — se depune o singură dată pentru tot exercițiul financiar, cel târziu până la data depunerii situațiilor financiare anuale.
- Un mijloc fix vândut în cursul anului apare în raportarea anuală de Active cu istoricul lui din acel an: valoarea fiscală, amortizarea calculată până la data ieșirii din patrimoniu și, după caz, data ieșirii — nu se generează o depunere D406 separată doar pentru operațiunea de vânzare.
- Declarația de Active se poate transmite **independent** de celelalte secțiuni ale D406 — firma nu trebuie să completeze toate secțiunile SAF-T doar pentru a raporta partea de Active.
- Operațiunea de vânzare în sine (factura emisă, TVA colectată, rezultatul din cesiune) se raportează, separat, prin secțiunile obișnuite ale D406 (jurnalul de vânzări, facturile) la depunerea lunară/trimestrială curentă — secțiunea de Active nu înlocuiește raportarea tranzacției comerciale.

## Ce se greșește în practică

- Se așteaptă o obligație de raportare imediată în SAF-T la momentul vânzării unui mijloc fix — secțiunea de Active urmează calendarul anual, nu pe cel al tranzacției.
- Se omite includerea mijlocului fix vândut din raportarea anuală de Active, considerând că „a ieșit din evidență" și deci nu mai trebuie raportat — dar el a existat și a fost amortizat o parte din exercițiul financiar respectiv, deci intră în raportarea acelui an.
- Se amestecă cele două fluxuri — raportarea anuală a Activelor și raportarea curentă a tranzacției de vânzare (factură, TVA) — tratându-le ca și cum ar fi aceeași depunere D406.

## Ce face iConta.eu

Generatorul de secțiune Active din SAF-T (`core/d406_active.py`, funcțiile `xml_asset`/`xml_d406_anual_active`) construiește raportarea anuală pentru fiecare mijloc fix, inclusiv amortizarea calculată până la data de referință, pe baza datelor introduse în modulul de mijloace fixe. Vânzarea propriu-zisă a activului (emiterea facturii, calculul rezultatului din cesiune) se înregistrează separat, în modulul de facturare al aplicației, și se reflectă în secțiunile curente ale D406, nu în raportarea anuală de Active.

[iConta.eu](/)
