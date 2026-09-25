---
title: "TVA la stocurile distruse sau degradate: ajustare"
description: "De ce TVA dedusă la achiziția stocurilor distruse sau degradate calitativ nu se ajustează, dacă situația e demonstrată corespunzător, conform Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA la stocurile distruse sau degradate: ajustare

Reflexul multor contabili, la scoaterea din gestiune a unor stocuri distruse sau degradate calitativ, e să ajusteze (să restituie) TVA dedusă inițial la achiziție. Legea prevede exact opusul, cu condiția ca situația să fie dovedită corespunzător.

## Temeiul legal

::: ghid-temei
„(2) Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă. În cazul bunurilor furate, persoana impozabilă demonstrează furtul bunurilor pe baza actelor doveditoare emise de organele judiciare."
— Codul fiscal (Legea 227/2015), art. 304 alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta în practică:

- **Regula e neajustarea**: dacă un stoc a fost distrus (accidental, prin degradare calitativă, expirare) sau pierdut, TVA dedusă la achiziția lui **rămâne dedusă** — nu se colectează înapoi la bugetul de stat.
- **Condiția e demonstrarea situației**, nu formalitatea în sine — proces-verbal de constatare, decizie a comisiei de inventariere, documente tehnice de expertiză, după caz. Fără dovadă corespunzătoare, organul fiscal poate contesta neajustarea.
- Pentru bunurile **furate**, standardul de probă e mai strict: legea cere explicit acte doveditoare emise de organele judiciare, nu doar o constatare internă a firmei.
- Excepția nu se confundă cu casarea voluntară fără motiv obiectiv (ex. lichidare de stoc nevândut, fără nicio degradare reală) — acolo se aplică alte reguli, cele generale de la art. 304 alin. (1), care pot cere ajustare dacă bunul iese din circuitul economic fără o cauză de forță majoră sau degradare demonstrată.

## Ce se greșește în practică

- Se colectează automat TVA la casarea unui stoc degradat, "din prudență", deși legea prevede expres neajustarea pentru bunurile distruse — o colectare nejustificată e o eroare la fel de reală ca o neajustare nejustificată.
- Se casează stocuri fără proces-verbal sau altă documentație a cauzei degradării — fără dovadă, poziția „nu se ajustează" nu poate fi susținută la un control.
- Se tratează furtul la fel ca degradarea calitativă din punct de vedere probatoriu — furtul cere specific acte de la organele judiciare, nu doar o notă internă de constatare a lipsei.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul dedicat casării/degradării stocurilor cu aplicarea automată a art. 304 alin. (2). Aplicația oferă evidența generală de stocuri (`core/stocuri_cv.py`, `core/stocuri_api.py`), în care ieșirea unui stoc distrus se poate înregistra ca orice altă ieșire de gestiune, dar decizia de neajustare a TVA — și documentarea ei corespunzătoare — rămân, azi, integral în sarcina contabilului.

[iConta.eu](/)
