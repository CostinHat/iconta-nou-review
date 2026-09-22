---
title: Trebuie depusă D390 în fiecare lună dacă TVA este trimestrială?
description: Da, dacă în luna respectivă a existat cel puțin o operațiune intracomunitară — D390 se raportează lunar, complet independent de periodicitatea (lunară sau trimestrială) a decontului de TVA propriu-zis.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Trebuie depusă D390 în fiecare lună dacă TVA este trimestrială?

O confuzie frecventă: firma are perioadă fiscală trimestrială pentru TVA (depune D300 o dată la trei luni), și contabilul presupune că și D390 urmează același ritm. Nu e așa — cele două obligații sunt complet independente una de cealaltă.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, anexa 2, pct. 1.1**: „Declarația recapitulativă se depune lunar, în condițiile prevăzute la art. 325 din Legea nr. 227/2015 privind Codul fiscal, cu modificările și completările ulterioare (Codul fiscal), până la data de 25 inclusiv a lunii următoare unei luni calendaristice, de către persoanele impozabile înregistrate în scopuri de TVA conform art. 316 sau 317 din Codul fiscal."

**Art. 325 alin. (4)**: „Declarațiile recapitulative se depun numai pentru perioadele în care ia naștere exigibilitatea taxei pentru operațiunile menționate la alin. (1)."
:::

## D390 și decontul de TVA — două obligații separate

Perioada fiscală de TVA (lunară sau trimestrială, stabilită conform art. 322 din Codul fiscal) guvernează depunerea decontului D300, respectiv D301. D390 nu e legată de această periodicitate: obligația de depunere apare pe **lună calendaristică**, în funcție de exigibilitatea taxei pentru operațiunile intracomunitare din acea lună — indiferent dacă firma depune decontul de TVA lunar sau trimestrial.

Practic, dacă firma ta are TVA trimestrial, dar în luna mai a avut o singură achiziție intracomunitară de bunuri, D390 pentru luna mai se depune separat, până pe 25 iunie — nu odată cu decontul trimestrial de TVA (care s-ar depune abia în iulie, pentru trimestrul II).

::: ghid-exemplu
Firmă cu TVA trimestrial (trimestrul II = aprilie-iunie). În mai are o achiziție intracomunitară de servicii software de la un furnizor din Germania. Rezultat: D390 pentru luna mai se depune până pe 25 iunie, separat de decontul de TVA pe trimestrul II, care se depune abia până pe 25 iulie.
:::

## Ce se greșește în practică

- Se așteaptă finalul trimestrului fiscal pentru a depune și D390, considerând-o parte a aceleiași periodicități ca decontul de TVA.
- Se omite depunerea D390 pentru o lună din mijlocul trimestrului, pentru că nu coincide cu termenul decontului trimestrial.
- Se presupune greșit că, dacă nu există operațiuni intracomunitare într-o lună din trimestru, întregul trimestru e „scutit" de D390 — de fapt fiecare lună se evaluează separat.
- Se confundă exigibilitatea taxei (baza pentru obligația D390) cu data facturii sau cu data plății.

## Ce face iConta.eu

Poarta de generare a D390 este strict lunară: aplicația verifică existența unei operațiuni intracomunitare (L/T/A/P/S/R) pentru luna calendaristică selectată, complet independent de perioada fiscală de TVA configurată pentru firmă. Dacă nu există nicio operațiune intracomunitară în luna respectivă, generarea declarației este refuzată explicit de aplicație — cu temei citat direct în mesaj: OPANAF 705/2020 pct. 1.2 și art. 325 din Codul fiscal — D390 nu se depune pe zero, indiferent de periodicitatea TVA a firmei.

[iConta.eu](/)
