---
title: "Simulare micro vs profit pentru venituri de 500.000 lei"
description: "Din 2026, pragul de la care o firmă nu mai poate fi microîntreprindere a scăzut la 100.000 euro — un SRL cu venituri de 500.000 lei rămâne, de regulă, sub acest prag și poate alege încă regimul micro."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Simulare micro vs profit pentru venituri de 500.000 lei

Un SRL cu venituri anuale de 500.000 lei se întreabă firesc dacă mai poate rămâne la impozitul pe veniturile microîntreprinderilor sau trebuie să treacă la impozit pe profit. Răspunsul depinde, în primul rând, de pragul valoric — iar acesta s-a schimbat de la 2026.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile[.]"
— Codul fiscal (Legea 227/2015), art. 47 alin. (1) lit. c), astfel cum a fost modificată de OUG nr. 8/2026, aplicabilă inclusiv pentru încadrarea ca microîntreprindere în anul fiscal 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta pentru un SRL cu venituri de 500.000 lei:

- Pragul valoric de la care o firmă iese din regimul micro este acum **100.000 euro** (redus succesiv în ultimii ani de la 500.000, apoi 250.000 euro) — echivalentul în lei se stabilește la cursul de la închiderea exercițiului financiar în care s-au realizat veniturile.
- La un curs orientativ de circa 5 lei/euro, 500.000 lei reprezintă aproximativ 100.000 euro — deci un SRL cu exact acest nivel de venituri se află **la limita** pragului, iar rezultatul simulării (rămâne micro sau trece la profit) depinde de cursul valutar exact de la închiderea exercițiului și de veniturile efective realizate.
- Pe lângă pragul valoric, microîntreprinderea trebuie să îndeplinească și celelalte condiții cumulative de la art. 47 (capitalul deținut de alte persoane decât statul, existența a cel puțin un salariat, absența dizolvării/lichidării) — depășirea unui singur prag valoric nu e singurul criteriu relevant.

## Ce se greșește în practică

- Se folosește pragul vechi (500.000 euro sau 250.000 euro, aplicabile în anii anteriori) pentru a decide încadrarea în 2026, ignorând reducerea la 100.000 euro.
- Se face conversia lei-euro la un curs aproximativ „de cap", fără să se folosească explicit cursul de la închiderea exercițiului financiar, singurul relevant legal pentru încadrare.
- Se analizează doar criteriul valoric al veniturilor, fără verificarea celorlalte condiții cumulative (existența unui salariat, structura capitalului social) care pot scoate firma din regimul micro chiar dacă veniturile sunt sub prag.

## Ce face iConta.eu

iConta.eu **nu are un simulator dedicat** care să compare, pe cifre ipotetice, impozitul micro cu impozitul pe profit pentru o firmă. Vectorul fiscal al firmei (regim micro/profit) este însă o dată stocată și folosită de aplicație pentru a determina automat ce declarații sunt datorate (D100 pentru micro, D101 pentru profit) și pentru a calcula corect impozitul aferent regimului activ. Verificarea pragului valoric de încadrare (100.000 euro în 2026) și decizia de a rămâne sau nu la regimul micro rămân, la data acestui ghid, o evaluare făcută de contabil înainte de a seta regimul firmei în aplicație.

[iConta.eu](/)
