---
title: "Cum trec un SRL de la micro la impozit pe profit?"
description: "Pașii și termenele pentru trecerea unui SRL din regimul de microîntreprindere la impozit pe profit, atunci când plafonul de venituri de 100.000 euro e depășit în cursul anului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum trec un SRL de la micro la impozit pe profit?

Trecerea de la microîntreprindere la impozit pe profit nu e opțională odată ce una dintre condițiile de la art. 47 nu mai e îndeplinită — cel mai frecvent, depășirea plafonului de venituri. Legea stabilește exact din ce moment se aplică noul regim și ce declarații se depun pentru perioada de tranziție.

## Temeiul legal

::: ghid-temei
„a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile."
— Legea 227/2015, art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul trecerii la profit:

- Depășirea plafonului se verifică în cursul anului, nu doar la 31 decembrie: dacă veniturile cumulate de la începutul anului trec de 100.000 euro, firma devine plătitoare de impozit pe profit **începând cu trimestrul** în care a avut loc depășirea, pentru întreaga perioadă rămasă din an (nu retroactiv pentru trimestrele deja închise ca micro).
- Pentru perioada anterioară depășirii, firma rămâne micro și depune D100 pentru acele trimestre; pentru perioada de la depășire încolo, calculul se face în sistemul impozitului pe profit, cu declarația privind impozitul pe profit aferentă perioadei respective, depusă până la 25 martie a anului fiscal următor.
- Cursul de schimb pentru verificarea plafonului nu e cel de la data fiecărei facturi, ci cel valabil la închiderea exercițiului financiar — pentru verificarea depășirii în cursul anului se folosește cursul BNR din ziua în care se constată depășirea, conform normelor metodologice.
- Modificarea regimului fiscal trebuie reflectată și în vectorul fiscal al firmei la ANAF (declarația de mențiuni 700), nu doar în evidența internă — vezi ghidul dedicat modificării vectorului fiscal.

## Ce se greșește în practică

- Se așteaptă finalul anului fiscal pentru a schimba regimul, deși legea impune trecerea la profit din trimestrul depășirii, nu de la 1 ianuarie anul următor.
- Se recalculează integral anul ca fiind pe profit, inclusiv trimestrele anterioare depășirii, în loc să se păstreze micro pentru acea perioadă și profit doar pentru rest.
- Se omite depunerea declarației de mențiuni la ANAF pentru actualizarea vectorului fiscal, deși schimbarea regimului de impozitare trebuie comunicată organului fiscal, nu doar aplicată intern în contabilitate.

## Ce face iConta.eu

Regimul fiscal e un câmp pe care utilizatorul îl schimbă manual din ecranul de configurare a firmei. iConta.eu **nu calculează automat momentul depășirii plafonului de 100.000 euro** și nu declanșează singură trecerea la profit — aplicația nu urmărește cumulat, în timp real, veniturile firmei față de plafonul legal. Odată ce utilizatorul schimbă regimul în aplicație, D100 continuă să se genereze lunar/trimestrial, dar calculul obligației trece de pe cota micro (cod 121, pe venituri) pe cea de profit (cod 103, pe profitul perioadei) — D101 (declarația anuală de impozit pe profit) devine în plus relevantă pentru perioadele din regimul de profit. Verificarea momentului exact al depășirii și depunerea declarației de mențiuni la ANAF rămân în sarcina contabilului.

[iConta.eu](/)
