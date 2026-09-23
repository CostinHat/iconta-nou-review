---
title: Cum se calculează impozitul pe profit la firmele cu pierdere
description: Ce înseamnă „pierdere fiscală" la impozitul pe profit, de ce conceptul nu există la impozitul micro, și ce trebuie să știe contabilul la trecerea dintr-un regim în altul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează impozitul pe profit la firmele cu pierdere

„Pierdere fiscală" nu e sinonim cu „pierdere contabilă" și nu există în orice regim de impozitare — o confuzie frecventă mai ales la firmele care au trecut prin regimul micro.

## Temeiul legal

::: ghid-temei
Art.31 alin.(5) CF: „Contribuabilii care au fost plătitori de impozit pe veniturile microîntreprinderilor și care ANTERIOR au realizat pierdere fiscală intră sub incidența alin.(1) de la data la care au revenit la sistemul [profit]"
— sursă: dosar de cercetare F027, secțiunea „Poate microîntreprinderea înregistra pierdere fiscală?".
:::

Conceptul de „pierdere fiscală" (reglementat la art.31, în Titlul II — impozit pe profit) nu există ca atare în Titlul III (impozit pe veniturile microîntreprinderilor, art.47–56): baza impozabilă la micro este venitul, nu profitul, astfel încât noțiunea de pierdere fiscală generată în perioada de micro nu are corespondent legal. Singura mențiune a pierderii la impozitul micro (art.53 alin.(2) lit.c)-d)) se referă la rezerve constituite anterior, când firma era plătitoare de impozit pe profit — nu la o pierdere generată în timp ce firma era la micro. Art.31 alin.(5), citat mai sus, confirmă indirect aceeași logică: pierderea fiscală reportabilă e legată de perioadele în care firma a fost efectiv plătitoare de impozit pe profit.

Concluzie practică: o firmă nu poate raporta „pierdere fiscală" cât timp e la impozit micro — poate avea pierdere contabilă, dar nu pierdere fiscală în sensul art.31. Pierderea fiscală reportabilă din perioade anterioare de profit rămâne, însă, valabilă și se poate folosi la revenirea la sistemul de impozit pe profit.

## Ce se greșește în practică

Greșeala des întâlnită este raportarea unei „pierderi fiscale" pentru perioada de micro, de obicei prin confuzie cu pierderea contabilă din bilanț. O altă greșeală este ignorarea pierderilor fiscale reportate din perioade anterioare (dinainte de trecerea la micro), care rămân valabile și trebuie reluate corect la revenirea la impozit pe profit.

## Ce face iConta.eu

Dosarul de cercetare al funcționalității D101 confirmă mecanismul de citire automată a balanței (profil firmă, split exploatare/financiar, rezervă legală, cont 691) la generarea declarației, dar nu documentează un modul dedicat de gestiune a reportului pierderii fiscale între ani în interfața D101 — profitul impozabil (P40) se asamblează din datele preluate din balanță plus intrările manuale ale contabilului (inclusiv, dacă e cazul, pierderea fiscală reportată). Recomandăm verificarea manuală atentă a reportului de pierdere fiscală înainte de generarea declarației, întrucât acest calcul nu este descris ca fiind automatizat integral în motorul aplicației.

[iConta.eu](/)
