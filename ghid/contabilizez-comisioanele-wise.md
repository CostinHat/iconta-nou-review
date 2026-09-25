---
title: "Cum contabilizez comisioanele Wise?"
description: "Înregistrarea contabilă a comisioanelor reținute de Wise (fostă TransferWise) pentru operațiuni de transfer valutar și plăți din contul firmei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum contabilizez comisioanele Wise?

Firmele care folosesc Wise pentru încasări/plăți în valută primesc extrase de cont în care comisionul e reținut automat, separat de suma transferată. Din punct de vedere contabil, comisionul Wise nu e altceva decât o cheltuială cu serviciile bancare — tratamentul e identic cu cel al comisioanelor reținute de o bancă tradițională.

## Temeiul legal

::: ghid-temei
„Contul 627 «Cheltuieli cu serviciile bancare și asimilate» Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 «Cheltuieli cu serviciile bancare și asimilate» se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512) [...]"
— OMFP 1802/2014, reglementările contabile, planul de conturi general (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

În practică, pentru o operațiune Wise cu comision reținut:

- **Suma netă** care intră sau iese din contul Wise se înregistrează în contul de disponibilități corespunzător (5121 pentru lei, 5124 pentru valută, convertită la cursul BNR din ziua operațiunii).
- **Comisionul reținut de Wise** se înregistrează separat, ca și cheltuială, în contul **627** „Cheltuieli cu serviciile bancare și asimilate", pe baza extrasului de cont (documentul justificativ), fără a fi nevoie de o factură separată din partea Wise — extrasul de cont e suficient ca document justificativ pentru operațiunile bancare.
- Dacă Wise e folosit ca intermediar pentru o plată către un furnizor, comisionul rămâne tot cheltuială bancară (627), distinctă de valoarea facturii furnizorului, chiar dacă apar pe același extras.

## Ce se greșește în practică

- Comisionul Wise se contabilizează în 622 „Cheltuieli privind comisioanele și onorariile" — cont folosit de fapt pentru comisioane de intermediere, consultanță sau tranzacționare de titluri, nu pentru servicii bancare curente.
- Se înregistrează suma brută a transferului ca ieșire din bancă, iar comisionul reținut automat rămâne nereflectat separat în contabilitate, ceea ce denaturează soldul de disponibilități față de extras.
- Nu se convertește corect suma în valută la cursul BNR din ziua operațiunii, ci se preia cursul afișat de Wise în aplicație, care poate diferi de cursul oficial folosit pentru înregistrarea contabilă.

## Ce face iConta.eu

Modulul de bancă din iConta.eu (`core/banca.py`) analizează descrierea fiecărei linii din extrasul de cont și încearcă să detecteze automat tipul operațiunii (client, furnizor, salarii, TVA, transfer intern etc.), aplicând nota contabilă corespunzătoare pe contul de disponibilități potrivit (5121 sau 5124 pentru valută). La data acestui ghid, aplicația **nu are o regulă dedicată de recunoaștere automată a comisioanelor Wise** ca linie separată de cheltuială pe contul 627 — dacă extrasul importat conține comisionul ca rând distinct, acesta trebuie alocat manual pe 627 în cadrul procesului de contare a extrasului bancar.

[iConta.eu](/)
