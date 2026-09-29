---
title: "Bunuri livrate în consignație sau stoc la dispoziția clientului: când intervine faptul generator de TVA?"
description: "La consignație, când consignatarul vinde bunurile clienților săi; la stocul la dispoziția clientului, când clientul retrage bunurile din stoc. Transferul fizic nu contează."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Bunuri livrate în consignație sau stoc la dispoziția clientului: când intervine faptul generator de TVA?

În ambele situații, faptul generator nu intervine la ieșirea fizică a bunurilor din depozitul furnizorului:

- la **consignație**, livrarea de la consignant la consignatar se consideră făcută la data la care **consignatarul vinde bunurile clienților săi**;
- la **stocul la dispoziția clientului**, livrarea are loc la data la care **clientul retrage bunurile din stoc** pentru utilizare, în principal în producție.

Până atunci, bunurile rămân în stocul furnizorului, chiar dacă fizic se află la consignatar sau la client. Factura cu TVA pentru întreaga cantitate trimisă se emite prea devreme: TVA devine exigibilă la data facturii și se plătește la buget înainte de vânzarea efectivă.

## Temeiul legal

::: ghid-temei
„Pentru bunurile livrate în baza unui contract de consignație se consideră că livrarea bunurilor de la consignant la consignatar are loc la data la care bunurile sunt livrate de consignatar clienților săi."
— Codul fiscal (Legea 227/2015), art. 281 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Pentru stocurile la dispoziția clientului se consideră că livrarea bunurilor are loc la data la care clientul retrage bunurile din stoc în vederea utilizării, în principal pentru activitatea de producție."
— Codul fiscal (Legea 227/2015), art. 281 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„În sensul titlului VII din Codul fiscal, contractul de consignație reprezintă un contract prin care consignantul se angajează să livreze bunuri consignatarului, pentru ca acesta din urmă să găsească un cumpărător pentru aceste bunuri. Consignatarul acționează în nume propriu, dar în contul consignantului, când livrează bunurile către cumpărători."
— Normele metodologice de aplicare a Codului fiscal (HG 1/2016), Titlul VII, pct. 24 alin. (1) (norme art. 281 CF) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)

„Stocurile la dispoziția clientului reprezintă o operațiune potrivit căreia furnizorul transferă regulat bunuri într-un depozit propriu sau într-un depozit al clientului, iar transferul proprietății bunurilor intervine, potrivit contractului, la data la care clientul scoate bunurile din depozit, în principal pentru a le utiliza în procesul de producție, dar și pentru alte activități economice."
— HG 1/2016, Titlul VII, pct. 24 alin. (3) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Ce înseamnă concret:

- **Consignație**: în același moment au loc două livrări, de la consignant la consignatar și de la consignatar la cumpărătorul final. Consignatarul acționează în nume propriu, deci facturează el cumpărătorului.
- **Stoc la dispoziția clientului**: contractul trebuie să prevadă că proprietatea trece la retragerea din depozit. Evidența retragerilor, de regulă lunară, este documentul-cheie.
- **Exigibilitatea poate apărea mai devreme**: dacă furnizorul emite factura sau încasează un avans înainte de vânzare sau retragere, TVA devine exigibilă la data facturii sau a avansului (art. 282 alin. (2) CF).
- **Excepție**: normele (pct. 24 alin. (4)) exclud aceste reguli pentru bunurile din import pentru care beneficiarul a optat să fie persoana obligată la plata TVA pentru import.

::: ghid-exemplu
SC Exemplu SRL trimite pe 20 septembrie 100 de bucăți, la 100 lei/buc, unui magazin consignatar. În septembrie nu intervine niciun fapt generator. Consignatarul raportează că în octombrie a vândut 40 de bucăți. Faptul generator pentru livrarea SC Exemplu SRL către consignatar intervine în octombrie, pentru 40 × 100 = **4.000 lei**, cu TVA 21% de **840 lei**. Restul de 60 de bucăți rămân în stocul SC Exemplu SRL (în gestiunea „mărfuri aflate la terți").
:::

## Ce se greșește în practică

- Se emite factură pentru întreaga cantitate la expediere, iar TVA devine exigibilă înainte de vânzare. La mărfurile nevândute urmează storno.
- Bunurile trimise în consignație sunt scoase din stoc la plecare, în loc să fie urmărite ca stoc aflat la terți.
- La stocul la dispoziția clientului lipsește din contract clauza privind momentul transferului proprietății, așa că operațiunea nu poate fi susținută la control.
- Nu se primește lunar raportul de vânzări al consignatarului sau lista retragerilor clientului, deci faptul generator nu se poate stabili.

## Ce face iConta.eu

iConta.eu contează facturile emise cu TVA pe cote (4111 = 70x + 4427). Recepția și evidența stocurilor se fac prin modulele de stocuri și NIR. Momentul în care factura se emite, adică data vânzării raportate de consignatar sau data retragerii din stoc, îl stabilește contabilul pe baza documentelor primite. Aplicația nu urmărește automat stocurile aflate la consignatari sau la clienți.

[iConta.eu](/)
