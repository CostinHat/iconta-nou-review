---
title: "Poate fi retras capitalul social după înființarea firmei?"
description: "Condițiile și procedura prin care capitalul social al unei societăți poate fi redus, cu protejarea creditorilor, după Legea societăților 31/1990."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate fi retras capitalul social după înființarea firmei?

Capitalul social nu poate fi „retras" liber, oricând, de către asociați — legea îl protejează ca garanție pentru creditorii societății. El poate fi însă **redus**, printr-o procedură formală, care include publicarea hotărârii și un termen de așteptare în care creditorii se pot opune.

## Temeiul legal

::: ghid-temei
„(1) Capitalul social poate fi redus prin: a) micșorarea numărului de acțiuni sau părți sociale; b) reducerea valorii nominale a acțiunilor sau a părților sociale; c) dobândirea propriilor acțiuni, urmată de anularea lor. (2) Capitalul social mai poate fi redus, atunci când reducerea nu este motivată de pierderi, prin: a) scutirea totală sau parțială a asociaților de vărsămintele datorate; b) restituirea către acționari a unei cote-părți din aporturi, proporțională cu reducerea capitalului social și calculată egal pentru fiecare acțiune sau parte socială; c) alte procedee prevăzute de lege."
— Legea nr. 31/1990 a societăților, art. 207 (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Reducerea capitalului social **nu se poate face imediat**: potrivit art. 208 alin. (1), ea poate fi efectuată numai după trecerea a **două luni** de la publicarea hotărârii în Monitorul Oficial, Partea a IV-a.
- Hotărârea de reducere trebuie să respecte minimul de capital social impus de lege (unde există), să arate motivele reducerii și procedeul folosit.
- Creditorii societății, ale căror creanțe sunt anterioare publicării hotărârii, au dreptul să obțină garanții pentru creanțele nescadente și pot face opoziție la hotărâre.
- Reducerea **nu produce efecte și nu se pot face plăți** către asociați până când creditorii nu și-au realizat creanțele sau nu au primit garanții adecvate, ori până când instanța respinge opoziția lor.

## Ce se greșește în practică

- Se crede că asociații pot retrage oricând, prin simplă decizie internă, o sumă din capitalul social — fără hotărâre publicată și fără respectarea termenului de două luni.
- Se fac plăți către asociați imediat după hotărârea de reducere, ignorând că legea interzice orice plată până la stingerea sau garantarea creanțelor creditorilor anteriori.
- Se confundă reducerea capitalului social cu distribuirea de dividende sau cu retragerea unui asociat — sunt operațiuni distincte, cu regimuri juridice și fiscale diferite.
- Nu se verifică dacă, după reducere, capitalul social rămâne cel puțin la minimul legal impus pentru forma de societate respectivă.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu are un motor pentru **lichidarea/radierea societății** (`core/lichidare.py`), care tratează restituirea capitalului social către asociați ca etapă a partajului de lichidare (înregistrarea contabilă 1012 = 456, neimpozabilă la asociat, distinctă de impozitarea câștigului din lichidare). Acest modul acoperă însă restituirea capitalului **la închiderea societății**, nu o reducere de capital social pe o firmă activă, în funcțiune — pentru acest din urmă caz, iConta.eu nu are, la acest moment, un flux dedicat, iar procedura de la art. 207-208 rămâne una gestionată direct de contabil/asociați, în afara aplicației.

[iConta.eu](/)
