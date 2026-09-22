---
title: Ce situații financiare trebuie întocmite la lichidarea unui SRL?
description: Legea cere două momente distincte de raportare la lichidare — bilanțul de deschidere, întocmit de lichidatori la preluarea funcției, și situația financiară finală, care propune repartizarea activului și stă la baza cererii de radiere.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce situații financiare trebuie întocmite la lichidarea unui SRL?

Lichidarea unui SRL nu se încheie cu un singur bilanț, ci presupune cel puțin două momente de raportare financiară separate: unul la începutul procedurii, când lichidatorii preiau patrimoniul, și unul la final, când se propune repartizarea a ceea ce a rămas către asociați.

## Temeiul legal

::: ghid-temei
**Legea 31/1990, art.253 alin.(3):**
"Lichidatorii sunt datori, îndată după preluarea funcției, ca împreună cu directorii și administratorii... să facă un inventar și să încheie un bilanț, care să constate situația exactă a activului și pasivului societății, și să le semneze."

**Legea 31/1990, art.263 alin.(1):**
"După terminarea lichidării societății în nume colectiv, în comandită simplă sau cu răspundere limitată, lichidatorii trebuie să întocmească situația financiară și să propună repartizarea activului între asociați."

**Legea 31/1990, art.260 alin.(6):**
"În termen de 15 zile de la terminarea lichidării, lichidatorii vor depune la registrul comerțului cererea de radiere a societății din registrul comerțului, pe baza raportului final de lichidare și a situațiilor financiare de lichidare prin care se prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase, după caz, inclusiv, dacă este cazul, dovada îndeplinirii obligației de calculare, reținere și plată a impozitului pe venit din lichidarea societății, prevăzută la art. 97 alin. (5) din Legea nr. 227/2015..."
:::

## Cele două momente de raportare

**Bilanțul de deschidere al lichidării** — se întocmește imediat după ce lichidatorii preiau funcția, împreună cu administratorii/directorii în funcție până atunci. Este un inventar și un bilanț care constată situația exactă a activului și pasivului la acel moment — practic, punctul de plecare al lichidatorilor.

**Situația financiară finală** — se întocmește după terminarea lichidării (vânzarea activelor, încasarea creanțelor, plata datoriilor) și trebuie să propună explicit repartizarea activului rămas între asociați. Ea stă la baza cererii de radiere, care se depune în 15 zile de la terminarea lichidării și trebuie să arate situația patrimoniului, a creanțelor și repartizarea activelor rămase — inclusiv, dacă e cazul, dovada plății impozitului pe venitul din lichidare prevăzut la art.97 alin.(5).

## Ce se greșește în practică

- Se confundă bilanțul de deschidere al lichidării cu bilanțul contabil anual obișnuit — sunt documente diferite, cu scop și moment diferite.
- Se depune cererea de radiere fără să se anexeze dovada calculării, reținerii și plății impozitului pe venitul din lichidare, deși legea o cere explicit.
- Se întocmește situația financiară finală doar ca o listă de solduri, fără propunerea explicită de repartizare a activului, deși legea cere expres această propunere.
- Se verifică dovada de plată a impozitului anexată la cererea de radiere fără să se confirme mai întâi că suma reținută corespunde cotei legale — un punct sensibil dacă nota contabilă de partaj a fost generată cu o cotă greșită (vezi ghidul dedicat calculului câștigului din lichidare).

## Ce face iConta.eu

Modulul general de bilanț al aplicației (`core/bilant.py` / `core/bilant_api.py`) nu conține nicio adaptare pentru lichidare, radiere sau dizolvare — nu există un generator dedicat, nici pentru bilanțul de deschidere, nici pentru situația financiară finală de lichidare. iConta.eu oferă doar notele contabile punctuale ale operațiunilor din lichidare — vânzarea unui activ și partajul final către asociați — care alimentează soldurile din care contabilul trebuie să întocmească manual, în afara aplicației, cele două situații financiare cerute de lege.

[iConta.eu](/)
