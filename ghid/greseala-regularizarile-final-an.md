---
title: "Greșeala de a nu face regularizările de final de an"
description: Închiderea unui an contabil nu se termină odată cu ultima factură — rezerva legală, reportarea rezultatului și repartizarea profitului sunt operațiuni separate, cu temei legal propriu, care se uită frecvent.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Greșeala de a nu face regularizările de final de an

O greșeală răspândită este să se considere anul „închis" odată ce ultima factură e înregistrată și rezultatul e calculat — venituri minus cheltuieli. De fapt, închiderea reală a anului contabil presupune câteva note suplimentare, obligatorii prin reglementările contabile, care rămân adesea nefăcute pentru că nu au o factură sau un document extern care să le declanșeze.

## Temeiul legal

::: ghid-temei
„În contabilitate, profitul sau pierderea se stabilește cumulat de la începutul exercițiului financiar."
— OMFP 1802/2014, pct. 420 alin. (1)
:::

::: ghid-temei
„Repartizarea profitului se înregistrează în contabilitate pe destinații, după aprobarea situațiilor financiare anuale. Repartizarea profitului se efectuează în conformitate cu prevederile legale în vigoare."
— OMFP 1802/2014, pct. 421 alin. (1)
:::

::: ghid-temei
„Din profitul societății se va prelua, în fiecare an, cel puțin 5% pentru formarea fondului de rezervă, până ce acesta va atinge minimum a cincea parte din capitalul social."
— Legea 31/1990, art. 183 alin. (1)
:::

Regularizările tipice de final de an, în ordinea firească în care se aplică:
1. **Închiderea conturilor de venituri și cheltuieli în 121** — pentru fiecare cont din clasa 7 cu sold creditor și fiecare cont din clasa 6 cu sold debitor, se transferă soldul în contul 121, obținând rezultatul exercițiului.
2. **Rezerva legală** — dacă exercițiul e pe profit, cel puțin 5% din profit se alocă la rezerva legală (129=1061), până când rezerva cumulată atinge 20% din capitalul social; peste acest plafon, alocarea nu mai e obligatorie.
3. **Reportarea rezultatului** — la începutul anului următor, rezultatul rămas (profit sau pierdere) se transferă din 121 în 1171/117, iar dacă a existat repartizare spre rezerve, se închide și 129 contra lui 121.

Fiecare din aceste trei pași are temei legal distinct — nu sunt variații ale aceleiași operațiuni, ci obligații separate care se aplică, de regulă, în aceeași fereastră de timp, ceea ce le face ușor de confundat sau de omis pe rând.

## Ce se greșește în practică

Cea mai comună omisiune este rezerva legală: pentru că nu are o factură sau un document care s-o declanșeze, rămâne adesea neînregistrată ani la rând, mai ales la firmele mici, până când o eventuală distribuire de dividende sau o operațiune de capital scoate la iveală lipsa ei. A doua omisiune frecventă este reportarea propriu-zisă a rezultatului: contul 121 rămâne cu sold de la un an la altul, în loc să fie golit în 117/1171 la începutul anului următor, ceea ce face ca balanța anului nou să pornească deja „murdară". A treia este ordinea greșită: se face reportarea rezultatului înainte de a aloca rezerva legală, deși alocarea rezervei trebuie calculată din profitul exercițiului încheiat, nu din ce mai rămâne după alte mutări.

## Ce face iConta.eu

Motorul de închidere al aplicației calculează, pe baza notelor validate ale perioadei, cele trei operațiuni descrise mai sus: transferul veniturilor/cheltuielilor în 121, rezerva legală (5% din profit, plafonată la 20% din capitalul social, cu regula versionată pe dată dacă legea se schimbă) și reportarea rezultatului în 1171/117. Calculul e disponibil ca funcție de închidere pe care contabilul o aplică la momentul potrivit din calendarul fiscal — verificați, înainte de a considera anul închis, că toate cele trei note au fost efectiv generate și validate, nu doar calculate.

[iConta.eu](/)
