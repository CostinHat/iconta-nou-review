---
title: "Suma restituită dintr-o subvenție primită este cheltuială deductibilă la impozitul pe profit?"
description: "Da, partea înregistrată ca cheltuială la restituire e deductibilă. Partea care doar reduce venitul amânat (475) nu e cheltuială, deci nu se deduce nimic pentru ea."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Suma restituită dintr-o subvenție primită este cheltuială deductibilă la impozitul pe profit?

Da, dar numai pentru partea din restituire care ajunge efectiv pe cheltuieli. Normele Codului fiscal spun expres că sunt deductibile „cheltuielile înregistrate ca urmare a restituirii subvențiilor primite”. Logica e simetrică: subvenția a fost impozitată când a trecut pe venituri, iar restituirea anulează acel venit prin cheltuială deductibilă.

Întrebarea practică e alta: cât din suma restituită se înregistrează ca cheltuială. Răspunsul vine din reglementările contabile. La subvențiile pentru investiții, o parte din restituire doar micșorează venitul amânat din contul 475 și nu trece deloc prin contul de profit și pierdere.

## Temeiul legal

::: ghid-temei
„(2) În aplicarea prevederilor art. 25 alin. (1) din Codul fiscal, sunt cheltuieli deductibile la calculul rezultatului fiscal și cheltuielile reglementate prin acte normative în vigoare. De exemplu: [...] c) cheltuielile înregistrate ca urmare a restituirii subvențiilor primite, potrivit legii, de la Guvern, agenții guvernamentale și alte instituții naționale și internaționale.”
— HG 1/2016 (Normele Codului fiscal), titlul II, pct. 13 alin. (2) lit. c) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„(1) Restituirea unei subvenții referitoare la un activ se înregistrează prin reducerea soldului venitului amânat cu suma rambursabilă. (2) Restituirea unei subvenții aferente veniturilor se efectuează prin reducerea veniturilor amânate, dacă există, sau, în lipsa acestora, pe seama cheltuielilor. (3) În măsura în care suma rambursată depășește venitul amânat sau dacă nu există un asemenea venit, surplusul, respectiv valoarea integrală restituită, se recunoaște imediat ca o cheltuială.”
— OMFP 1802/2014 (Reglementările contabile), pct. 404 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Cum se aplică:

- **Subvenție pentru investiții, restituită înainte să fie reluată integral la venituri:** partea încă nereluată se stinge din contul 475 (venit amânat) și nu e cheltuială. Doar surplusul, adică partea deja trecută la venituri prin 7584, se înregistrează pe cheltuieli și se deduce.
- **Subvenție de exploatare** deja recunoscută la venituri (741): restituirea trece integral pe cheltuieli și e deductibilă.
- **Dobânzi și penalități aferente restituirii:** au regim propriu. Codul fiscal consideră nedeductibile dobânzile, majorările, amenzile și penalitățile datorate autorităților, cu excepția celor aferente contractelor încheiate cu aceste autorități (art. 25 alin. (4) lit. b)). Trebuie analizat dacă suma decurge din contractul de finanțare sau e un accesoriu fiscal.

::: ghid-exemplu
SC Exemplu SRL a primit o subvenție de 100.000 lei pentru un utilaj de 100.000 lei, amortizat pe 5 ani. După 2 ani, 40.000 lei au fost reluați la venituri (4751 = 7584), iar soldul contului 475 este 60.000 lei. Firma trebuie să restituie integral subvenția de 100.000 lei.

- 60.000 lei reduc soldul contului 475. Nu sunt cheltuială și nu influențează profitul.
- 40.000 lei se recunosc imediat ca cheltuială. Sunt deductibili și anulează efectul veniturilor de 40.000 lei impozitate în anii anteriori.
:::

## Ce se greșește în practică

- Întreaga sumă restituită se trece pe cheltuieli, inclusiv partea încă aflată în 475. Rezultă o cheltuială deductibilă umflată, pentru un venit care nu a fost impozitat niciodată.
- Restituirea se tratează ca nedeductibilă „pentru că e o sancțiune”. Normele o declară deductibilă.
- Dobânzile sau penalitățile pentru restituire se deduc fără analiză, deși sunt supuse regulii de la art. 25 alin. (4) lit. b).
- La o microîntreprindere se caută deductibilitatea. Impozitul pe venit al microîntreprinderilor nu funcționează pe cheltuieli deductibile.

## Ce face iConta.eu

iConta.eu are o operațiune dedicată pentru subvenții. Înregistrează dreptul de a primi și încasarea subvenției de exploatare (445 = 741) sau pentru investiții (445 = 4751), iar la subvențiile pentru investiții calculează reluarea lunară la venituri proporțional cu amortizarea (4751 = 7584). Restituirea subvenției nu are o operațiune dedicată. Se înregistrează prin editorul de note contabile, cu împărțirea între 475 și cheltuieli stabilită de contabil. Aplicația generează D101, dar deductibilitatea dobânzilor sau a penalităților rămâne decizia contabilului.

[iConta.eu](/)
