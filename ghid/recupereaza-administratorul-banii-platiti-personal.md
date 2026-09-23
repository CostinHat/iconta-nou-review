---
title: Cum recuperează administratorul banii plătiți personal pentru firmă?
description: Când administratorul (și asociat) plătește din buzunarul propriu o cheltuială a firmei, suma devine datorie a societății către el, prin contul de asociați 4551, și se poate restitui oricând, cu sau fără dobândă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum recuperează administratorul banii plătiți personal pentru firmă?

Se întâmplă des la firmele mici: administratorul plătește din cont personal o factură, o taxă sau un abonament al firmei, pentru că nu are la îndemână cardul companiei. Contabil, acest lucru nu e o cheltuială „pierdută" a administratorului, ci un **împrumut acordat firmei** de către acesta — cu condiția ca administratorul să fie și asociat. Suma i se poate restitui oricând, integral sau în tranșe.

## Temeiul legal

::: ghid-temei
„Sumele depuse sau lăsate temporar de către acționari/asociați la dispoziția entității, precum și dobânzile aferente [...] se înregistrează în contabilitate în conturi distincte (contul 4551 «Acționari/asociați - conturi curente», respectiv contul 4558 «Acționari/asociați - dobânzi la conturi curente»)."
— OMFP 1802/2014, pct. 349
:::

Banii avansați de asociat pentru firmă intră exact în această categorie: sunt „sume lăsate temporar la dispoziția entității" de către un asociat, deci se contabilizează pe contul 4551, nu ca o cheltuială personală nedeductibilă și nu ca aport de capital.

Dacă firma plătește și o dobândă pentru aceste sume, dobânda e un venit impozabil pentru administratorul-persoană fizică: „Veniturile din investiții cuprind: [...] b) venituri din dobânzi" (Cod fiscal, art. 91 lit. b), impozitate cu „o cotă [...] de 10% [...] din: [...] d) investiții" (Cod fiscal, art. 64 alin. (1) lit. d)).

## Ce se greșește în practică

- Se trece suma direct pe cheltuieli ale firmei „în numele administratorului", fără să existe o contrapartidă clară în contul 4551 — ceea ce lasă suma nedocumentată și greu de justificat la control.
- Se confundă banii avansați cu un aport la capitalul social, deși administratorul nu a intenționat o majorare de capital, ci doar o avansare temporară recuperabilă.
- Se uită înregistrarea impozitului de 10% atunci când firma decide totuși să plătească dobândă pentru sumele avansate.

## Ce face iConta.eu

Funcționalitatea **Decontări asociați** (Operațiuni speciale > Finanțare) generează automat nota contabilă pentru împrumutul de la asociat: la primirea banilor, `5121 = 4551`; la restituire, `4551 = 5121`, plus, dacă se acordă dobândă, `666 = 4551` pentru cheltuiala cu dobânda și reținerea de 10% impozit pe `4551 = 446`. E suficient să alegi operațiunea „împrumut asociat" și data, iar iConta calculează și înregistrează restul.

[iConta.eu](/)
