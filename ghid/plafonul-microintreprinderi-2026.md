---
title: "Care este plafonul pentru microîntreprinderi în 2026?"
description: "Plafonul de venituri de 100.000 euro pentru încadrarea ca microîntreprindere în 2026, potrivit ultimei modificări a Codului fiscal, și celelalte condiții cumulative."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este plafonul pentru microîntreprinderi în 2026?

Plafonul de venituri pentru microîntreprindere nu e singura condiție de încadrare, dar e cea mai des verificată — și cea care s-a schimbat cel mai recent, prin ordonanța de urgență adoptată la finalul lunii februarie 2026.

## Temeiul legal

::: ghid-temei
„(1) În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...]
c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile;
[...]
d) capitalul social al acesteia este deținut de persoane, altele decât statul și unitățile administrativ-teritoriale;
[...]
g) are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3);
[...]
h) are asociați/acționari care dețin, în mod direct sau indirect, peste 25% din valoarea/numărul titlurilor de participare sau al drepturilor de vot și este singura persoană juridică stabilită de către asociați/acționari să aplice prevederile prezentului titlu;
[...]
i) a depus în termen situațiile financiare anuale, dacă are această obligație potrivit legii."
— Legea 227/2015 (Codul fiscal), art. 47 alin. (1) lit. c), d), g), h), i), lit. c) modificată prin OUG 8/2026, art. 6 pct. 15 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie verificat concret pentru 2026:

- **Plafonul de venituri e 100.000 euro**, calculat la cursul de schimb valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile — nu la cursul de la 31 decembrie sau de la data depunerii declarației.
- **Condiția se verifică la 31 decembrie a anului fiscal precedent**, pentru toate condițiile alineatului (1), inclusiv plafonul de venituri — nu e o verificare continuă în timpul anului, ci un test la un moment fix.
- **Veniturile se cumulează cu ale întreprinderilor legate** (potrivit alin. (1^1)) — o firmă poate părea sub plafon izolat, dar depăși plafonul odată cumulate veniturile persoanelor juridice afiliate, conform testelor de legătură (participații de peste 25%, drept de numire a administratorului etc.).
- **Plafonul e doar una dintre condițiile cumulative** — capitalul social deținut de persoane altele decât stat/UAT, existența a cel puțin un salariat (cu excepțiile de la art. 48 alin. (3)), unicitatea firmei desemnate să aplice regimul micro între societăți afiliate cu asociați comuni peste 25%, și depunerea la termen a situațiilor financiare. Depășirea oricăreia dintre ele scoate firma din regimul micro, indiferent de venituri.

## Ce se greșește în practică

- Se verifică plafonul de 100.000 euro izolat, fără cumularea veniturilor întreprinderilor legate — o structură cu mai multe firme mici, deținute de aceleași persoane peste 25%, poate depăși plafonul cumulat fără ca fiecare firmă, privită separat, să pară că îl depășește.
- Se folosește cursul de schimb de la data depunerii declarației sau cursul mediu anual, în loc de cursul valabil la închiderea exercițiului financiar, așa cum cere explicit legea.
- Se presupune că plafonul de venituri e singura condiție relevantă, ignorând condițiile cumulative (salariat, unicitatea firmei desemnate, depunerea la termen a situațiilor financiare) care pot scoate firma din regim chiar dacă veniturile sunt sub plafon.
- Se ignoră faptul că textul lit. c) a fost modificat prin OUG 8/2026 (aplicabil, potrivit actului, inclusiv pentru încadrarea ca microîntreprindere în anul fiscal 2026) — se folosește o valoare veche a plafonului, dintr-o formă anterioară a legii.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează și nu verifică automat plafonul de venituri pentru încadrarea în regimul de microîntreprindere**. Modulul `core/control_fiscal_api.py` tratează regimul fiscal (micro/profit) ca pe un câmp declarat manual de utilizator (`regim_fiscal`, la Date firmă) și confirmă explicit, în comentariile de cod, că nu există nicio constantă a plafonului micro în aplicație — deci nu poate contrazice sau semnala singură o eventuală depășire a plafonului. Dacă firma depășește plafonul de 100.000 euro sau altă condiție cumulativă, actualizarea regimului fiscal declarat rămâne responsabilitatea contabilului, verificată în afara aplicației.

[iConta.eu](/)
