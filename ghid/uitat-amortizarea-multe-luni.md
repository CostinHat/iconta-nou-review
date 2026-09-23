---
title: "Ce fac dacă am uitat amortizarea mai multe luni?"
description: "Cum recuperează registrul de mijloace fixe automat amortizarea omisă, prin calculul cumulat la zi."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am uitat amortizarea mai multe luni?

Dacă ai omis să înregistrezi nota lunară de amortizare pentru câteva luni, nu trebuie să reconstitui manual fiecare lună — registrul calculează mereu suma cumulată corectă până la orice dată.

## Temeiul legal

::: ghid-temei
"Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);"
— Codul fiscal, art.28 alin.(12) lit.a
:::

Amortizarea "la zi" e definită ca sumă cumulată de la PIF până la data cerută, pe metoda reală a activului — nu ca o acumulare a unor înregistrări lunare individuale postate în contabilitate. Așadar, la următoarea înregistrare, poți prelua direct din registru valoarea cumulată corectă la data respectivă și înregistra diferența față de ce era deja postat.

## Ce se greșește în practică

Greșeala tipică e recalcularea manuală, lună cu lună, a sumelor omise, cu risc de eroare de rotunjire sau de aplicare greșită a metodei — în loc să se folosească direct valoarea cumulată calculată de motorul de amortizare.

## Ce face iConta.eu

Funcția `amortizat_la_data` calculează amortizarea cumulată "la zi" plus valoarea rămasă, pentru orice dată cerută, pe metoda reală a activului — indiferent ce a fost sau nu postat anterior în contabilitate. Aceasta e valoarea folosită și de ecranul de registru, și de casare, și de reevaluare.

[iConta.eu](/)
