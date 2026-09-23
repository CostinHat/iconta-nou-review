---
title: Cum se amortizează bunurile achiziționate din fonduri nerambursabile?
description: Regula amortizării integrale a activelor cofinanțate din subvenții/fonduri nerambursabile, reluarea proporțională a subvenției la venituri, și limitele reale ale iConta.eu pe acest caz.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se amortizează bunurile achiziționate din fonduri nerambursabile?

Un mijloc fix cumpărat parțial sau integral dintr-o subvenție (fonduri nerambursabile, fonduri
UE) ridică o întrebare specifică: se amortizează doar partea suportată de firmă, sau toată
valoarea de intrare? Și ce se întâmplă cu subvenția în paralel?

## Temeiul legal

::: ghid-temei
402. - (2) Subvențiile pentru active, inclusiv subvențiile nemonetare la valoarea justă, se
înregistrează în contabilitate ca subvenții pentru investiții și se recunosc în bilanț ca
venit amânat (contul 475 "Subvenții pentru investiții"). Venitul amânat se înregistrează ca
venit curent în contul de profit și pierdere pe măsura înregistrării cheltuielilor cu
amortizarea sau la casarea ori cedarea activelor.

— OMFP 1802/2014, pct.402(2)
:::

::: ghid-temei
Prin excepție de la prevederile art. 7 pct. 44 și 45, în situația în care, potrivit
reglementărilor contabile aplicabile, contribuabilul deduce subvenția guvernamentală la
calculul valorii contabile a mijloacelor fixe, valoarea rezultată este și valoare fiscală.

— Codul fiscal (Legea 227/2015), art.28 alin.(13)
:::

Există, de fapt, **două metode contabile posibile** pentru subvențiile de investiții:

- **metoda brută** (OMFP 1802/2014, pct.402(2)): activul se înregistrează și se amortizează
  integral la valoarea brută de intrare, iar subvenția stă separat ca venit amânat (cont 475),
  reluat la venituri proporțional cu amortizarea lunară a activului finanțat;
- **metoda netă** (Codul fiscal, art.28 alin.13): subvenția se scade direct din valoarea
  contabilă a mijlocului fix, iar valoarea rezultată (mai mică) devine și valoare fiscală, deci
  și bază de amortizare — dar numai dacă firma alege această metodă și în contabilitate, nu doar
  fiscal.

## Ce se greșește în practică

- Se scade subvenția direct din valoarea mijlocului fix "ca să fie mai simplu", deși firma
  aplică de fapt metoda brută în contabilitate — ceea ce ar amortiza greșit o valoare care nu
  corespunde evidenței contabile reale.
- Se uită reluarea proporțională a subvenției la venituri (cont 475→7584), lăsând-o "înghețată"
  în bilanț ani la rând.
- Se raportează în D406/SAF-T un activ cofinanțat fără să se semnaleze partea de subvenție,
  pentru că informația respectivă nu e legată automat de rândul mijlocului fix.

## Ce face iConta.eu

Registrul `Firma > Mijloace fixe` amortizează activul integral pe valoarea brută de intrare —
aplicația **implementează doar metoda brută** (OMFP 1802/2014). Reluarea subvenției la venituri,
proporțional cu amortizarea, este o operațiune contabilă separată, ținută manual în paralel
(contabilul introduce valoarea activului, subvenția și amortizarea lunară pentru calculul
proporției) — **nu există un câmp de subvenție pe rândul mijlocului fix** în registru.

Limitare de raportare importantă, de spus deschis: în declarația D406/SAF-T, câmpul de suport
de investiție al activului (`InvestmentSupport`) este raportat mereu ca `0.00`, indiferent cât
de mult a fost activul cofinanțat efectiv din fonduri nerambursabile — deci D406 generat din
iConta.eu nu reflectă cofinanțarea unui activ, chiar dacă evidența contabilă a subvenției e
ținută corect separat. De asemenea, metoda netă din CF art.28 alin.(13) nu este implementată —
dacă firma dvs. aplică metoda netă în contabilitate, calculul amortizării fiscale pe valoarea
netă trebuie făcut manual, în afara registrului.

[iConta.eu](/)
