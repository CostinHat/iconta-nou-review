---
title: "SAF-T și registrul de mijloace fixe: cum se raportează"
description: Secțiunea Active din D406 SAF-T se depune anual, separat de raportarea lunară/trimestrială, la termenul situațiilor financiare — cu amortizarea calculată pe metoda reală a fiecărui activ.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# SAF-T și registrul de mijloace fixe: cum se raportează

Registrul de mijloace fixe ajunge în SAF-T printr-o secțiune distinctă de restul declarației D406 — nu se depune lunar sau trimestrial, ca operațiunile curente, ci o singură dată pe an, la termenul situațiilor financiare.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — cu subsecțiuni detaliate, printre care Assets (Active).
— OPANAF nr. 1783/2021, Anexa 1, pct. 4-5
:::

::: ghid-temei
„Active — întocmite la nivelul anului financiar ... printr-o singură depunere ... până la data depunerii situaţiilor financiare" — se poate depune „ca o declaraţie independentă".
— OPANAF nr. 1783/2021, Anexa 4, pct. 7-8
:::

Spre deosebire de restul declarației D406, care se transmite lunar sau trimestrial, urmând periodicitatea de TVA a firmei, secțiunea Active are un regim separat: o singură depunere anuală, la termenul situațiilor financiare, și poate fi transmisă independent de restul declarației. Codul „A" (anual) din structura tehnică a fișierului e rezervat exact pentru această fereastră de 12 luni — nu există o variantă „anuală" a raportării periodice obișnuite, doar lunar sau trimestrial pentru operațiuni curente, plus anual pentru Active.

## Ce se greșește în practică

- Se așteaptă ca secțiunea Active să fie inclusă automat în fiecare depunere lunară/trimestrială de D406 — ea se depune separat, o singură dată pe an.
- Se presupune că termenul secțiunii Active coincide cu termenul obișnuit de raportare periodică (ultima zi a lunii următoare) — termenul real e cel al situațiilor financiare anuale.
- Se ignoră faptul că metoda de amortizare declarată în SAF-T trebuie să corespundă exact metodei reale a fiecărui activ, nu unei aproximări liniare aplicate tuturor.

## Ce face iConta.eu

Secțiunea Active a D406 e generată din același motor unic de calcul al amortizării folosit și pentru registrul „Firmă > Mijloace fixe" — fiecare activ apare cu valoarea de intrare, amortizarea cumulată și valoarea rămasă calculate pe metoda lui reală (liniară, degresivă, accelerată sau superaccelerată), nu pe o metodă implicită. O limită confirmată: câmpul de suport de investiții din SAF-T e raportat mereu ca zero — registrul de mijloace fixe nu ține o legătură directă cu subvențiile de investiții primite pentru un activ anume, așa că o achiziție cofinanțată din fonduri europene sau alt tip de subvenție nu apare cu suportul de investiție corespunzător în declarație, indiferent cât de mult a fost ea cofinanțată efectiv.

[iConta.eu](/)
