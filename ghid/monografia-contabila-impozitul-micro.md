---
title: "Care este monografia contabilă pentru impozitul micro?"
description: "Cum se înregistrează în contabilitate impozitul pe veniturile microîntreprinderilor, de la calcul până la plata către bugetul de stat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este monografia contabilă pentru impozitul micro?

Impozitul pe veniturile microîntreprinderilor nu se înregistrează prin contul de impozit pe profit (691), pentru că nu e un impozit pe profit — planul de conturi îi dedică un cont distinct de cheltuială, tocmai pentru că baza de calcul e cifra de afaceri, nu rezultatul contabil.

## Temeiul legal

::: ghid-temei
„Contul 698 «Cheltuieli cu impozitul pe venit și cu alte impozite care nu apar în elementele de mai sus» [...] Cu ajutorul acestui cont se ține evidența cheltuielilor cu impozitul pe venit plătit de microîntreprinderi și a altor impozite, conform reglementărilor emise în acest scop. În debitul contului 698 [...] se înregistrează: – valoarea impozitului pe venitul microîntreprinderilor (441)."
— OMFP 1802/2014 (reglementări contabile), funcțiunea contului 698 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)

„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Codul fiscal (Legea 227/2015), art. 51 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Monografia standard, în doi pași:

1. **Calculul și înregistrarea obligației**, la finalul trimestrului: `698 = 441` — cu suma reprezentând 1% din cifra de afaceri (veniturile impozabile ale trimestrului), conform art. 51 din Codul fiscal.
2. **Plata efectivă către buget**: `441 = 512` — la data virării sumei, pe baza declarației depuse (obligație de plată la bugetul de stat).

Contul **441 „Impozitul pe profit și alte impozite"** e cel folosit atât pentru impozitul pe profit, cât și pentru impozitul micro — analiticul distinct (de exemplu 4411 pentru profit, un alt analitic pentru micro) ajută la separarea evidenței, dar structura de bază a monografiei e identică: cheltuiala se recunoaște prin contul de cheltuieli specific (691 la profit, 698 la micro), iar decontarea cu bugetul trece prin 441.

## Ce se greșește în practică

- Se înregistrează impozitul micro prin contul 691 „Cheltuieli cu impozitul pe profit", ca la firmele plătitoare de impozit pe profit — planul de conturi prevede explicit contul 698 pentru acest caz.
- Se calculează impozitul micro pe profitul contabil, în loc de pe cifra de afaceri (veniturile impozabile ale trimestrului), confundând cele două baze de impozitare complet diferite.
- Se omite constituirea provizionului/cheltuielii la finalul fiecărui trimestru și se înregistrează impozitul o singură dată, la sfârșitul anului, ceea ce denaturează rezultatul intermediar al fiecărui trimestru.

## Ce face iConta.eu

iConta.eu calculează impozitul pe veniturile microîntreprinderilor folosind cota legală curentă (1%, conform art. 51 din Codul fiscal), cu rata configurabilă manual de contabil dacă e cazul, și generează declarația aferentă (D100) pentru fiecare trimestru. Motorul intern al aplicației menține separate cele două tipuri de impozit ale firmei (micro, pe cont/poziție distinctă în nomenclatorul de obligații, versus impozit pe profit), evitând amestecul lor în aceeași poziție de declarație.

[iConta.eu](/)
