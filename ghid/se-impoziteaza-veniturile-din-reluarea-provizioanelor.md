---
title: Se impozitează veniturile din reluarea provizioanelor?
description: Depinde dacă provizionul a fost dedus la constituire — reluarea unui provizion dedus e venit impozabil (CF art. 26 alin. (5)), iar reluarea unui provizion nededus e venit neimpozabil (CF art. 23 lit. d)); nu există o regulă unică valabilă pentru toate provizioanele.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Se impozitează veniturile din reluarea provizioanelor?

Când un provizion se reduce sau se anulează, contabil apare un venit (781x). Fiscal, acest venit nu e impozabil sau neimpozabil "automat" — tratamentul oglindește exact ce s-a întâmplat la constituire: dacă provizionul a fost dedus atunci, venitul din reluare e impozabil acum; dacă a fost nedeductibil la constituire, venitul din reluare e neimpozabil.

## Temeiul legal

::: ghid-temei
"Reducerea sau anularea oricărui provizion ori a rezervei care a fost anterior dedusă, inclusiv
rezerva legală, se include în rezultatul fiscal, ca venituri impozabile sau elemente similare
veniturilor, indiferent dacă reducerea sau anularea este datorată modificării destinației
provizionului sau a rezervei, distribuirii provizionului sau rezervei către participanți sub orice
formă, lichidării, divizării sub orice formă, fuziunii contribuabilului sau oricărui altui motiv."

"d) veniturile din anularea, recuperarea, inclusiv refacturarea cheltuielilor pentru care nu s-a
acordat deducere, veniturile din reducerea sau anularea provizioanelor pentru care nu s-a acordat
deducere, veniturile din restituirea ori anularea unor dobânzi și/sau penalități pentru care nu
s-a acordat deducere, precum și veniturile reprezentând anularea rezervei înregistrate ca urmare a
participării în natură la capitalul altor persoane juridice sau ca urmare a majorării capitalului
social la persoana juridică la care se dețin titlurile de participare;"
:::

## Regula, în oglindă

Ține minte simetria: **reluarea urmează constituirea**.

- Un provizion pentru garanții (1512), dedus la constituire în limita cotei contractuale, generează la reluare venit **impozabil**, în limita aceleiași sume care a fost dedusă.
- O ajustare pentru deprecierea creanțelor dedusă 30% sau 100% la constituire (art. 26 lit. c)/j)) generează la reluare venit **impozabil**, pentru partea care fusese dedusă.
- Un provizion pentru litigii (1511), restructurare (1514) sau alte provizioane (1518), nedeductibile la constituire, generează la reluare venit **neimpozabil** — pentru că nu s-a acordat deducere inițial, nu poate exista impozitare "de a doua oară" la reluare.
- Ajustarea pentru deprecierea stocurilor (cont 39x), nedeductibilă necondiționat la constituire, generează la reluare venit **neimpozabil**, pentru același motiv.

::: ghid-exemplu
O firmă a constituit un provizion pentru garanții de 5.000 lei, integral dedus fiscal (în limita cotei contractuale). Un an mai târziu, garanția expiră fără pretenții și provizionul se reia integral la venituri (1512 = 7812). Cei 5.000 lei sunt venit impozabil. Dacă în schimb firma reia un provizion pentru litigii de 8.000 lei, care fusese nedeductibil la constituire, cei 8.000 lei sunt venit neimpozabil — se scad din rezultatul fiscal.
:::

## Ce se greșește în practică

- Se impozitează automat orice venit din reluare de provizion (781x), fără verificarea dacă provizionul fusese dedus la constituire.
- Se declară neimpozabil venitul din reluarea unui provizion parțial dedus (ex. ajustare de creanță dedusă 30%), în loc să se impoziteze doar partea corespunzătoare celei deduse.
- Se pierde urma tratamentului fiscal de la constituire, mai ales când constituirea și reluarea au loc în exerciții financiare diferite sau sub o altă persoană responsabilă cu evidența.

## Ce face iConta.eu

`core/provizioane.py` generează nota contabilă de reluare pentru fiecare tip de provizion (`15xx = 7812` prin `nota_provizion`, respectiv `491 = 7814` / `39x = 7814` prin `nota_ajustare_creanta` și `nota_ajustare_stoc`), dar **nu recalculează și nu propagă automat caracterul impozabil sau neimpozabil al venitului din reluare** — flagul `deductibil` calculat la constituire nu e reutilizat la reluare. Verificarea dacă provizionul reluat fusese dedus inițial și, deci, dacă venitul din reluare e impozabil sau nu, rămâne o decizie manuală, pe baza regulii de simetrie explicate mai sus.

[iConta.eu](/)
