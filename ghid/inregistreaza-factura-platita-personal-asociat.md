---
title: Cum se înregistrează o factură plătită personal de asociat?
description: O factură a firmei achitată de un asociat din bani proprii nu se pierde în evidența contabilă — devine automat o datorie a firmei către asociat, prin contul 4551, recuperabilă ulterior.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează o factură plătită personal de asociat?

Un asociat achită direct furnizorului o factură emisă pe firmă — pentru că firma nu are lichidități la momentul respectiv sau pur și simplu e mai rapid. Factura rămâne, desigur, cheltuială/achiziție a firmei (se înregistrează normal pe conturile de cheltuieli sau imobilizări și TVA, dacă e cazul), dar plata ei nu vine din contul firmei, ci din buzunarul asociatului. Diferența trebuie reflectată undeva: firma îi rămâne datoare asociatului cu suma respectivă.

## Temeiul legal

::: ghid-temei
„Sumele depuse sau lăsate temporar de către acționari/asociați la dispoziția entității, precum și dobânzile aferente [...] se înregistrează în contabilitate în conturi distincte (contul 4551 «Acționari/asociați - conturi curente», respectiv contul 4558 «Acționari/asociați - dobânzi la conturi curente»)."
— OMFP 1802/2014, pct. 349
:::

Practic, plata facturii din bani proprii de către asociat este tratată contabil identic cu un împrumut acordat firmei: suma achitată în numele firmei se înregistrează pe contul 4551 „Acționari/asociați — conturi curente", ca datorie a firmei față de asociat, distinctă de factura în sine (care rămâne înregistrată pe furnizor și se stinge la data plății).

## Ce se greșește în practică

- Se stinge direct contul de furnizor fără nicio contrapartidă în 4551, ca și cum firma ar fi plătit ea însăși factura — ceea ce face plata imposibil de trasat la un control și poate ridica suspiciunea unei plăți „din numerar nejustificat".
- Se tratează suma ca aport la capital sau ca venit al asociatului, deși e vorba doar de o sumă avansată, recuperabilă fără impozitare la restituirea capitalului avansat (impozitul de 10% apare doar dacă firma plătește și dobândă).
- Nu se păstrează dovada plății (extras de cont personal, chitanță) care să justifice suma înregistrată pe 4551, în cazul unui control.

## Ce face iConta.eu

Funcționalitatea **Decontări asociați** (Operațiuni speciale > Finanțare) tratează avansul asociatului ca împrumut acordat firmei: la recunoașterea sumei plătite de asociat, `5121 = 4551` (sau direct stingerea obligației către furnizor prin contrapartidă cu 4551, după configurarea aleasă), iar la restituirea ulterioară către asociat, `4551 = 5121`. Dacă firma decide să acorde și dobândă pentru perioada cât suma a stat „împrumutată", iConta calculează automat cheltuiala cu dobânda (`666 = 4551`) și impozitul de 10% reținut la sursă (`4551 = 446`).

[iConta.eu](/)
