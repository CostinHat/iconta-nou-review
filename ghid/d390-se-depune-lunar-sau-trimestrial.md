---
title: D390 se depune lunar sau trimestrial?
description: D390 se depune întotdeauna lunar, pe lună calendaristică, indiferent de periodicitatea fiscală (lunară sau trimestrială) a firmei pentru TVA — nu există o variantă trimestrială a declarației recapitulative.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# D390 se depune lunar sau trimestrial?

Răspuns direct: **lunar**, întotdeauna, indiferent de perioada fiscală a firmei pentru TVA. Nu există „D390 trimestrială" — declarația recapitulativă are o singură periodicitate, stabilită de lege, complet separată de decontul de TVA propriu-zis.

## Temeiul legal

::: ghid-temei
**Art. 325 alin. (2)**: „Termenul de depunere al declarației recapitulative și modelul acesteia se stabilesc prin ordin al președintelui Agenției Naționale de Administrare Fiscală. Declarația se întocmește pentru fiecare lună calendaristică în care ia naștere exigibilitatea taxei pentru operațiunile prevăzute la alin. (1) [...]."

**Art. 325 alin. (4)**: „Declarațiile recapitulative se depun numai pentru perioadele în care ia naștere exigibilitatea taxei pentru operațiunile menționate la alin. (1)."

**OPANAF 705/2020, anexa 2, pct. 1.1**: „Declarația recapitulativă se depune lunar, în condițiile prevăzute la art. 325 din Legea nr. 227/2015 privind Codul fiscal, cu modificările și completările ulterioare (Codul fiscal), până la data de 25 inclusiv a lunii următoare unei luni calendaristice, de către persoanele impozabile înregistrate în scopuri de TVA conform art. 316 sau 317 din Codul fiscal."
:::

## De ce nu există variantă trimestrială

Legea leagă obligația de depunere strict de „lună calendaristică" (art. 325 alin. (2)) și de exigibilitatea taxei apărută în acea lună (alin. (4)) — nu de perioada fiscală de TVA din art. 322, care poate fi lunară sau trimestrială în funcție de cifra de afaceri a firmei. Cele două noțiuni sunt guvernate de articole diferite din Codul fiscal și nu se intersectează: o firmă cu TVA trimestrial raportează D390 tot lunar, dacă are operațiuni intracomunitare.

Singura variație reală a periodicității e alta: declarația se depune **doar pentru lunile în care există efectiv o operațiune intracomunitară** (L/T/A/P/S/R) — nu se depune „pe zero". Asta poate crea impresia unei periodicități neregulate, dar mecanismul de bază rămâne strict lunar, niciodată trimestrial.

## Ce se greșește în practică

- Se presupune că, dacă firma are TVA trimestrial, și D390 urmează aceeași cadență.
- Se depune D390 o dată la trei luni, cumulând operațiunile din tot trimestrul într-o singură declarație — greșit, fiecare lună se declară separat.
- Se confundă absența unei declarații într-o lună fără operațiuni cu o presupusă „periodicitate trimestrială" a obligației.
- Se ignoră o lună din mijlocul trimestrului cu o singură operațiune intracomunitară izolată, considerând-o nesemnificativă.

## Ce face iConta.eu

Generarea D390 este structurată strict pe lună calendaristică, independent de configurarea perioadei fiscale de TVA a firmei (lunară sau trimestrială). Poarta de validare a generării verifică existența a cel puțin unei operațiuni intracomunitare (L/T/A/P/S/R) în luna respectivă — dacă nu există nicio operațiune, generarea e refuzată explicit, cu temeiul citat direct: OPANAF 705/2020 pct. 1.2 și art. 325 Cod fiscal.

[iConta.eu](/)
