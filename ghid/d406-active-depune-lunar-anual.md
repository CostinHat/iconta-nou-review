---
title: "D406 Active se depune lunar sau anual?"
description: "De ce secțiunea Active din SAF-T (D406) are un regim anual, diferit de restul declarației, care e lunară sau trimestrială."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D406 Active se depune lunar sau anual?

Răspunsul scurt: **anual**, nu lunar — spre deosebire de restul declarației D406 (jurnalul contabil, facturile), care urmează perioada fiscală a TVA. Secțiunea Active are un regim de raportare separat, explicit stabilit de act normativ.

## Temeiul legal

::: ghid-temei
„Declaraţia informativă D406 se transmite în format electronic, data-limită de transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare, respectiv luna/trimestrul calendaristic, după caz, pentru alte informaţii decât cele privind secţiunile «Stocuri» şi «Active»; - la termenul de depunere a situaţiilor financiare aferente exerciţiului financiar, în cazul secţiunii «Active»; - la termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării, în cazul secţiunii «Stocuri».
Informaţiile privind «Activele» din cadrul Declaraţiei informative D406 sunt întocmite la nivelul anului financiar aplicat de către contribuabili şi transmise printr-o singură depunere, respectiv o singură raportare a Declaraţiei informative D406, până la data depunerii situaţiilor financiare aferente exerciţiului financiar la care se referă."
— OPANAF 1783/2021 (SAF-T D406), Anexa 4, pct. 1 și pct. 7 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

D406 nu are un singur regim de depunere — are **trei**, pe secțiuni:

- Secțiunile obișnuite (jurnal contabil, facturi etc.) — **lunar sau trimestrial**, în funcție de perioada fiscală de TVA a firmei, până la ultima zi a lunii următoare.
- Secțiunea **Active** — **anual**, o singură dată, la termenul situațiilor financiare.
- Secțiunea **Stocuri** — „la cerere", la termenul stabilit de organul fiscal, minimum 30 de zile de la solicitare — nici lunar, nici anual în sensul strict, ci declanșat de ANAF.

Deci întrebarea „lunar sau anual" nu are un răspuns unic pentru tot D406 — depinde strict de secțiunea la care se referă. Pentru Active, răspunsul e ferm: anual, o singură raportare pe an financiar.

## Ce se greșește în practică

- Se presupune că D406 e „o singură declarație" cu un singur termen, ignorând că Active și Stocuri au regimuri complet diferite de restul declarației.
- Se depune secțiunea Active repetat, lunar sau trimestrial, ca și cum ar urma perioada fiscală TVA — legea cere o singură depunere pe an.
- Se confundă termenul secțiunii Active cu termenul de 25 al declarațiilor lunare de TVA — termenul real e cel al situațiilor financiare, care cade mult mai târziu în an.

## Ce face iConta.eu

Motorul secțiunii Active (`core/d406_active.py`) calculează amortizarea pe cele patru metode fiscale și generează fragmentul XML `<Assets>` din registrul de mijloace fixe, la cererea unui an anume — coerent cu regimul anual descris mai sus, nu cu un ciclu lunar. Ruta care întoarce acest calcul (`GET /tenants/{id}/d406-active`) e funcțională, dar la data acestui ghid întoarce doar fragmentul `<Assets>`, nu un fișier `<AuditFile>` complet, depunibil ca atare, și nu are încă un ecran dedicat în interfață — comentariul din cod marchează explicit acest lucru („fără UI încă, păstrat deliberat"). Generatorul fișierului complet există la nivel de motor, probat valid pe validatorul oficial DUK, dar nu e conectat azi la nicio rută accesibilă din aplicație.

[iConta.eu](/)
