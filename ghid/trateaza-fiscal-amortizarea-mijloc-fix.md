---
title: "Cum se tratează fiscal amortizarea unui mijloc fix finanțat din fonduri europene?"
description: Amortizarea mijlocului fix e integral deductibilă, la valoarea lui de intrare; separat, venitul din reluarea fondurilor europene se scade din baza microîntreprinderii, dar rămâne impozabil la impozitul pe profit.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se tratează fiscal amortizarea unui mijloc fix finanțat din fonduri europene?

Sursa fondurilor — europeană sau națională — nu schimbă modul de amortizare a activului: se amortizează integral, la valoarea lui de intrare. Ce diferă fiscal e tratamentul venitului generat de reluarea fondurilor la venituri, în paralel cu amortizarea.

## Temeiul legal

::: ghid-temei
„Subvențiile legate de activele amortizabile sunt recunoscute, de regulă, în contul de profit și pierdere pe parcursul perioadelor și în proporția în care amortizarea acelor active este recunoscută."
— OMFP 1802/2014, pct. 399 alin. (1)
:::

::: ghid-temei
„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: [...] d) veniturile din subvenții; [...]"
— Legea 227/2015, art. 53 alin. (1) lit. d)
:::

Doi pași distincți:

- **Amortizarea**: contabil, activul se amortizează la valoarea lui integrală de intrare, indiferent de sursa finanțării; cheltuiala cu amortizarea e deductibilă în condițiile obișnuite.
- **Venitul din reluarea fondurilor** (`4751 = 7584`, proporțional cu amortizarea): la impozitul pe veniturile microîntreprinderilor, acest venit se scade din baza impozabilă, conform art. 53 alin. (1) lit. d) din Codul fiscal. La impozitul pe profit, în sursele verificate pentru acest ghid nu există o prevedere echivalentă în lista veniturilor neimpozabile (art. 23 din Legea 227/2015) — deci venitul din subvenții rămâne impozabil integral la firmele plătitoare de impozit pe profit.

Practic, o firmă micro nu plătește impozit pe venitul din reluarea fondurilor europene, dar o firmă plătitoare de impozit pe profit îl include în rezultatul fiscal, exact ca orice alt venit.

## Ce se greșește în practică

- Se presupune că orice venit din fonduri europene e neimpozabil, indiferent de regimul fiscal al firmei — scutirea de la art. 53 alin. (1) lit. d) există doar pentru microîntreprinderi.
- Se reduce baza de amortizare a activului cu suma fondurilor primite, deși amortizarea trebuie calculată la valoarea integrală de intrare.
- Se scade venitul din reluare (7584) din baza impozitului pe profit, unde nu există temei legal pentru o asemenea excludere.

## Ce face iConta.eu

Amortizarea se calculează normal, la valoarea integrală a activului, prin operațiunile de mijloace fixe. Motorul de reluare a fondurilor europene la venituri (`4751=7584`) calculează corect cota proporțională, dar, la data acestei verificări, **ecranul „Subvenții (445/741)" nu are câmpurile necesare** (valoarea activului, subvenția, amortizarea lunară) pentru operația „Reluare la venituri" — aceasta apare ca opțiune în listă, dar nu poate fi finalizată din formularul standard; reluarea trebuie introdusă pe altă cale (API direct sau notă manuală). Dacă firma ta e plătitoare de impozit pe veniturile microîntreprinderilor, verifică manual, la declarația unificată, că venitul din reluare a fost scăzut din baza impozabilă, conform art. 53 alin. (1) lit. d) — dacă firma e plătitoare de impozit pe profit, acest venit se include normal, fără nicio scădere.

[iConta.eu](/)
