---
title: "Ce faci cu TVA la marjă când prețul de vânzare e mai mic decât prețul de cumpărare?"
description: "Nu colectezi TVA pentru acea livrare: marja negativă dă taxă zero. Pierderea nu se scade din marjele pozitive ale altor bunuri, pentru că taxa se calculează pe fiecare livrare."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Ce faci cu TVA la marjă când prețul de vânzare e mai mic decât prețul de cumpărare?

Pentru acea vânzare nu colectezi TVA. Normele Codului fiscal spun direct că, în regimul special al marjei, taxa nu se colectează când marja profitului e negativă. Livrarea se înscrie în jurnalul special de vânzări, dar cu TVA zero.

Contează și ce nu faci. Marja negativă nu devine TVA de recuperat și nu reduce taxa colectată pe alte vânzări. În regimul marjei, taxa se calculează separat pentru fiecare livrare. TVA a perioadei este suma taxelor pe livrările cu marjă pozitivă.

## Temeiul legal

::: ghid-temei
„Persoana impozabilă nu colectează TVA conform regimului special în situația în care marja profitului, determinată conform alin. (4) lit. b) , este negativă.”
— Normele metodologice ale Codului fiscal (HG 1/2016), titlul VII, pct. 86 alin. (5) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

::: ghid-temei
„a) baza de impozitare pentru fiecare livrare de bunuri supusă regimului special este diferența dintre marja de profit realizată de persoana impozabilă revânzătoare și valoarea taxei aferente marjei respective; […] Taxa colectată într-o perioadă fiscală pentru bunurile supuse regimului special reprezintă suma taxelor pe valoarea adăugată aferente fiecărei livrări de bunuri efectuate în perioada respectivă.”
— Normele metodologice ale Codului fiscal (HG 1/2016), titlul VII, pct. 86 alin. (4) (sursă: [HG nr. 1/2016 (Normele metodologice ale Codului fiscal)](https://legislatie.just.ro/Public/DetaliiDocument/174822))
:::

::: ghid-temei
„baza de impozitare este marja profitului, determinată conform alin. (1) lit. g) , exclusiv valoarea taxei aferente.”
— Codul fiscal (Legea 227/2015), art. 312 alin. (4) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Regula se aplică în trei pași:

- **Calculezi marja pe fiecare bun:** prețul de vânzare minus prețul de cumpărare, cu toate elementele din definiția de la art. 312 alin. (1) lit. g) (comision, transport, ambalare facturate clientului).
- **Dacă marja e pozitivă,** extragi TVA prin procedeul sutei mărite, cu 21/121 la cota standard.
- **Dacă marja e zero sau negativă,** TVA pentru livrarea respectivă e zero. Rezultatul nu se reportează și nu se compensează cu alte livrări.

Pe factură nu se înscrie TVA distinct, nici la marjă pozitivă, nici la marjă negativă. Art. 312 alin. (12) interzice mențiunea separată a taxei în regimul special. Vânzarea sub costul de achiziție rămâne în contabilitate o pierdere comercială obișnuită, fără efect în decontul de TVA.

::: ghid-exemplu
SC Exemplu SRL, revânzător de mobilier second-hand, vinde în aceeași lună două piese cumpărate de la persoane fizice:

- o canapea cumpărată cu 2.000 lei și vândută cu 1.500 lei: marja e −500 lei, deci TVA = 0;
- un dulap cumpărat cu 1.000 lei și vândut cu 2.210 lei: marja e 1.210 lei, deci TVA = 1.210 × 21 / 121 = 210 lei.

TVA colectată în regim special în lună: 0 + 210 = **210 lei**. Nu se calculează (1.210 − 500) × 21 / 121 = 123,22 lei, pentru că marja negativă a canapelei nu se scade din marja dulapului.
:::

## Ce se greșește în practică

- Se face o „marjă globală” pe lună, iar pierderile de pe unele bunuri se scad din câștigurile de pe altele. Normele cer calculul pe fiecare livrare.
- Marja negativă se înscrie ca TVA negativă sau se raportează ca taxă de recuperat. Regimul marjei nu dă drept de deducere (art. 312 alin. (6)).
- Vânzarea cu pierdere se scoate din jurnalul special de vânzări. Toate livrările în regim special se înscriu în jurnal, inclusiv cele cu TVA zero (pct. 86 alin. (6) lit. b)).
- Pe factura cu marjă negativă se trece „TVA 0”. Taxa nu se menționează distinct deloc, iar factura poartă mențiunea privind regimul marjei.

## Ce face iConta.eu

iConta.eu are operațiunea „Vânzare regim marjă (second-hand)”. Pe fiecare vânzare introduci prețul de vânzare și prețul de cumpărare, iar aplicația calculează TVA pe marjă prin suta mărită, la cota introdusă. La marjă zero sau negativă, TVA calculată este zero. Nota contabilă se generează ca ciornă și trebuie verificată de contabil înainte de validare, mai ales la vânzările cu pierdere.

[iConta.eu](/)
