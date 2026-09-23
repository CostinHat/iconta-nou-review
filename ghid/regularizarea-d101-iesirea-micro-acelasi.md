---
title: Regularizarea D101 după ieșirea din micro în același an
description: Cum se leagă D100-urile trimestriale depuse pe impozit micro de D101 anuală, când firma a trecut la impozit pe profit în cursul aceluiași an fiscal.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Regularizarea D101 după ieșirea din micro în același an

Firma a fost la impozit micro o parte din an, apoi a depășit plafonul și a intrat la impozit pe profit — ce se „regularizează" de fapt prin D101 de la finalul anului?

## Temeiul legal

::: ghid-temei
Art.52 alin.(6) CF: „Calculul și plata impozitului pe profit de către microîntreprinderile care se încadrează în prevederile alin. (1), (2), (4) și (7) se efectuează luând în considerare veniturile și cheltuielile realizate începând cu trimestrul respectiv."
— sursă: dosar de cercetare F027, secțiunea „Ieșirea din regimul micro în cursul anului".
:::

Răspunsul scurt: D101 nu „regularizează" retroactiv perioada de micro — ea definitivează doar impozitul pe profit datorat de la trimestrul depășirii plafonului până la finalul anului fiscal, cumulând plățile anticipate trimestriale deja declarate prin D100 pe cod de obligație 103. Perioada anterioară, cât firma a fost corect la impozit micro, rămâne declarată separat prin D100 pe cod 121 și nu intră în baza de calcul a D101.

Conform dosarului de cercetare, cadrul legal citat în secțiunea privind opțiunea de declarare trimestrial/anual menționează și că firmele foste plătitoare de impozit micro au obligația (nu opțiunea) sistemului trimestrial de declarare/plată în anul imediat următor schimbării de regim — un detaliu relevant pentru anul următor celui în care s-a produs trecerea, nu pentru regularizarea propriu-zisă din anul curent.

## Ce se greșește în practică

Greșeala frecventă este tratarea D101 ca pe o „regularizare totală" a anului, incluzând eronat în baza de calcul veniturile/cheltuielile din perioada de micro. O a doua greșeală este dublarea impozitării: recalcularea unor sume deja acoperite prin D100-urile pe cod 121, ceea ce umflă artificial profitul impozabil declarat prin D101.

## Ce face iConta.eu

D101 din iConta.eu este generată ca declarație anuală de definitivare, cu date preluate automat din balanță (profil firmă, split exploatare/financiar, rezervă legală, cont 691) pentru întreaga perioadă în care firma a fost la impozit pe profit în anul respectiv. Motorul nu recalculează și nu amestecă automat perioada de micro anterioară trecerii — aceasta rămâne acoperită de D100-urile deja depuse. Trebuie menționat, de asemenea, că D101 rectificativă nu este încă disponibilă din interfața aplicației (flag-urile de stare din formularul XML sunt hardcodate la „0"); orice corecție ulterioară a definitivării de profit se face în prezent tot manual, direct la ANAF.

[iConta.eu](/)
