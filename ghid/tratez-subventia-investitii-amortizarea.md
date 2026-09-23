---
title: Cum tratez subvenția pentru investiții și amortizarea
description: Subvenția pentru investiții se înregistrează separat de activul cumpărat și se reia la venituri treptat, pe măsura amortizării — nu integral, la primire.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez subvenția pentru investiții și amortizarea

O subvenție pentru investiții nu e venit din prima zi. Ea se înregistrează inițial ca datorie/venit amânat și se reia la venituri treptat, în același ritm cu amortizarea activului pe care l-a finanțat — nu integral, la momentul încasării.

## Temeiul legal

::: ghid-temei
„Subvențiile aferente activelor reprezintă subvenții pentru acordarea cărora principala condiție este ca entitatea beneficiară să cumpere, să construiască sau să achiziționeze active imobilizate."
— OMFP 1802/2014, pct. 394 alin. (1)
:::

::: ghid-temei
„Subvențiile legate de activele amortizabile sunt recunoscute, de regulă, în contul de profit și pierdere pe parcursul perioadelor și în proporția în care amortizarea acelor active este recunoscută."
— OMFP 1802/2014, pct. 399 alin. (1)
:::

::: ghid-temei
„Subvențiile nu trebuie înregistrate direct în conturile de capital și rezerve deoarece acestea reprezintă sume acordate sub rezerva îndeplinirii anumitor condiții de către societate."
— OMFP 1802/2014, pct. 402 alin. (1)
:::

Mecanismul contabil, în trei pași:

1. **Dreptul de a primi subvenția**: `445 = 4751` (Subvenții / Subvenții guvernamentale pentru investiții).
2. **Încasarea**: `5121 = 445`.
3. **Reluarea lunară la venituri**, pe măsura amortizării activului finanțat: `4751 = 7584` (Venituri din subvenții pentru investiții), cu cota calculată proporțional cu partea subvenționată din valoarea activului — adică amortizarea lunară a activului înmulțită cu procentul finanțat din subvenție. Dacă activul e cedat înainte de amortizarea integrală, soldul rămas din 4751 se reia integral la venituri, nu se pierde.

Fiscal, distincția e importantă:
- La **impozitul pe veniturile microîntreprinderilor**, veniturile din subvenții (deci și reluarea din 7584) se scad din baza impozabilă (art. 53 alin. (1) lit. d) din Codul fiscal).
- La **impozitul pe profit**, legea nu prevede nicio scutire pentru veniturile din subvenții — ele intră normal în calculul rezultatului fiscal.

## Ce se greșește în practică

- Se recunoaște toată subvenția ca venit la încasare, în loc să fie reluată treptat pe durata amortizării.
- Se înregistrează subvenția direct într-un cont de capital/rezerve, deși OMFP 1802 pct. 402 interzice explicit acest lucru.
- Se scade venitul din subvenție (7584) din baza impozabilă și la impozitul pe profit, unde legea nu prevede o asemenea scutire.

## Ce face iConta.eu

Ecranul „Subvenții (445/741)" din iConta.eu generează notele pentru dreptul de a primi și încasarea subvenției pentru investiții (`445=4751`, `5121=445`). Pentru reluarea lunară (`4751=7584`), motorul `reluare_lunara_investitii(valoare_activ, subventie, amortizare_lunara)` calculează exact cota proporțională descrisă mai sus — **dar, la data acestei verificări, formularul „Subvenții" din ecran nu expune câmpurile `valoare_activ`, `subventie` și `amortizare_lunara`** cerute de această operație (are doar dată, fel, sumă, moment și descriere); opțiunea „Reluare la venituri" apare în lista de tip de operațiune, dar nu poate fi dusă la capăt din formularul standard. Până la o corectare a ecranului, reluarea lunară trebuie introdusă prin altă cale (API direct sau o notă manuală calculată după formula de mai sus). La declarația unificată, dacă ai reluat subvenții pentru investiții în perioada raportată, verifică manual, conform art. 53 alin. (1) lit. d), că suma respectivă a fost scăzută din baza impozabilă a microîntreprinderii înainte de depunere.

[iConta.eu](/)
