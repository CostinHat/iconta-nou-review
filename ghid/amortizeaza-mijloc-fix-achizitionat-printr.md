---
title: "Cum se amortizează un mijloc fix achiziționat printr-o subvenție?"
description: Amortizarea se calculează la valoarea integrală a mijlocului fix, ca la orice activ — subvenția care l-a finanțat se reia separat la venituri, în același ritm cu amortizarea.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se amortizează un mijloc fix achiziționat printr-o subvenție?

Un mijloc fix cumpărat cu ajutorul unei subvenții se amortizează la fel ca oricare altul — pe baza valorii lui integrale de intrare, cu metoda și durata normală de amortizare. Subvenția nu modifică amortizarea în sine; ea generează, în paralel, un venit recunoscut treptat, pe măsură ce amortizarea avansează.

## Temeiul legal

::: ghid-temei
„Subvențiile legate de activele amortizabile sunt recunoscute, de regulă, în contul de profit și pierdere pe parcursul perioadelor și în proporția în care amortizarea acelor active este recunoscută."
— OMFP 1802/2014, pct. 399 alin. (1)
:::

Practic, sunt două calcule paralele, nu unul singur:

- **Amortizarea activului**: normală, la valoarea integrală de intrare, indiferent de sursa finanțării.
- **Reluarea subvenției**: `4751 = 7584`, calculată ca amortizarea lunară a activului înmulțită cu procentul din valoarea lui finanțat prin subvenție. Dacă activul e amortizat integral sau cedat înainte de termen, soldul rămas din 4751 se reia integral la venituri.

Fiscal, la microîntreprindere, venitul din reluare (7584) se scade din baza impozabilă a impozitului pe veniturile microîntreprinderilor (art. 53 alin. (1) lit. d) din Codul fiscal). La impozitul pe profit, acest venit rămâne impozabil — nu există o scutire similară pentru veniturile din subvenții.

## Ce se greșește în practică

- Se calculează amortizarea doar la partea din valoare neacoperită de subvenție, reducând nejustificat baza de amortizare.
- Se omite complet reluarea subvenției la venituri, lăsând suma „înghețată" în contul 4751 pe toată durata de viață a activului.
- Se recunoaște reluarea într-o sumă fixă lunară, fără legătură cu amortizarea reală și cu procentul subvenționat din valoarea activului.

## Ce face iConta.eu

Amortizarea mijlocului fix se calculează normal, prin operațiunile obișnuite de mijloace fixe, la valoarea lui integrală de intrare. Reluarea proporțională a subvenției (`4751=7584`) e calculată corect de motor (`reluare_lunara_investitii`, formula `amortizare_lunară × subvenție / valoare_activ`), dar, la data acestei verificări, **ecranul „Subvenții (445/741)" nu are câmpuri pentru valoarea activului, subvenție și amortizarea lunară** — opțiunea „Reluare la venituri" apare în listă, dar operația nu poate fi finalizată din formularul standard; reluarea trebuie introdusă pe altă cale (API direct sau notă manuală), până la o corectare a ecranului.

[iConta.eu](/)
