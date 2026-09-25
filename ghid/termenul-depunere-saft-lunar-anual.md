---
title: "Termenul de depunere a SAF-T: lunar sau anual"
description: "SAF-T (D406) nu are un singur termen: secțiunile obișnuite sunt lunare/trimestriale, Active e anuală, Stocuri e la cererea ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Termenul de depunere a SAF-T: lunar sau anual

SAF-T (declarația D406) nu are un termen unic — are **trei regimuri diferite**, în funcție de secțiunea raportată. Întrebarea „lunar sau anual" primește răspunsuri diferite pentru jurnalul contabil, pentru secțiunea Active și pentru secțiunea Stocuri.

## Temeiul legal

::: ghid-temei
„Declaraţia informativă D406 se transmite în format electronic, data-limită de transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare, respectiv luna/trimestrul calendaristic, după caz, pentru alte informaţii decât cele privind secţiunile «Stocuri» şi «Active»; - la termenul de depunere a situaţiilor financiare aferente exerciţiului financiar, în cazul secţiunii «Active»; - la termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării, în cazul secţiunii «Stocuri»."
— OPANAF 1783/2021 (SAF-T D406), Anexa 4, pct. 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Cele trei regimuri, punctual:

- **Secțiunile obișnuite** (jurnalul contabil, facturile, mișcările de trezorerie etc.) — **lunar sau trimestrial**, în funcție de perioada fiscală de TVA a firmei, până la **ultima zi a lunii următoare** perioadei raportate. Acesta e regimul „standard" al D406, pe care majoritatea firmelor îl întâlnesc recurent.
- **Secțiunea Active** — **anual**, o singură depunere pe an financiar, la **termenul de depunere a situațiilor financiare** — un termen complet diferit, care poate cădea cu luni distanță de termenul lunar de TVA. Poate fi transmisă și ca declarație independentă, fără restul secțiunilor D406.
- **Secțiunea Stocuri** — **la cererea ANAF**, cu un termen stabilit de organul fiscal, care nu poate fi mai mic de **30 de zile calendaristice** de la data solicitării. Nu e nici lunar, nici anual în sens calendaristic fix — declanșarea vine de la fisc, nu dintr-un calendar propriu al contribuabilului.

Confuzia „lunar sau anual" apare de obicei pentru că D406 e tratat ca o singură declarație cu un singur termen, când de fapt structura ei internă separă explicit cele trei regimuri, fiecare cu logica lui.

## Ce se greșește în practică

- Se aplică termenul lunar (ultima zi a lunii următoare) tuturor secțiunilor D406, inclusiv Active și Stocuri, care au regimuri complet diferite.
- Se așteaptă ca secțiunea Stocuri să aibă un termen fix, calendaristic — de fapt termenul apare doar la solicitarea explicită a ANAF, cu un minimum de 30 de zile.
- Se depune secțiunea Active repetat, o dată cu fiecare D406 lunar/trimestrial, deși legea cere o singură raportare anuală, la termenul situațiilor financiare.

## Ce face iConta.eu

Generarea secțiunilor obișnuite ale D406 (jurnal contabil, facturi) urmează motorul principal de declarație lunară/trimestrială al aplicației, pe perioada fiscală de TVA a firmei. Secțiunea Active are un motor separat (`core/d406_active.py`), care calculează amortizarea pe cele patru metode fiscale (liniară/degresivă/accelerată/superaccelerată) și produce fragmentul XML `<Assets>` pentru anul cerut — coerent cu regimul anual descris mai sus. La data acestui ghid, ruta care întoarce acest calcul funcționează, dar produce doar fragmentul `<Assets>`, nu un fișier `<AuditFile>` complet, depunibil ca atare la ANAF, și nu are încă un ecran dedicat în interfață. Secțiunea Stocuri, cu termenul ei declanșat de cerere ANAF, are propriul modul de calcul, separat de cel al secțiunii Active.

[iConta.eu](/)
