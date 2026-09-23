---
title: "Greșeala de a nu valida fișierul SAF-T înainte de depunere"
description: "De ce validarea D406 înainte de depunere nu e un pas opțional, ce riscă cine sare peste el și cum face iConta.eu această verificare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu valida fișierul SAF-T înainte de depunere

Depunerea unui fișier SAF-T (D406) nevalidat este cea mai frecventă cauză de respingere sau de amendă evitabilă. Validarea nu e un formalism — e singurul mod de a ști, înainte de a trimite declarația, dacă structura ei e corectă.

## Temeiul legal

::: ghid-temei
„(1) Constituie contravenţii următoarele fapte: a) nedepunerea la termenele prevăzute de lege a fişierului standard de control fiscal; b) depunerea incorectă ori incompletă a fişierului standard de control fiscal. (2) Contravenţiile [...] se sancţionează astfel: a) cu amendă de la 1.000 lei la 5.000 lei în cazul săvârşirii faptei prevăzute la lit. a); b) cu amendă de la 500 lei la 1.500 lei în cazul săvârşirii faptei prevăzute la lit. b)." — Legea nr. 207/2015 (Codul de procedură fiscală), art. 337^1
:::

Legea face diferența clară între „nedepunere" (amendă mai mare, 1.000-5.000 lei) și „depunere incorectă ori incompletă" (500-1.500 lei) — iar o depunere nevalidată în prealabil riscă exact a doua categorie: fișierul ajunge la ANAF cu erori de structură pe care validarea le-ar fi prins înainte de trimitere. Legea prevede și o excepție de la sancțiune atunci când corectarea se face până la termenul următoarei depuneri, sau ca urmare a unui fapt neimputabil contribuabilului — dar aceasta nu înlocuiește validarea, ci doar atenuează consecința unei greșeli deja depuse.

## Ce se greșește în practică

- Se trimite fișierul direct spre depunere, fără să treacă prin pasul de validare, pe premisa că „a generat, deci e bun".
- Se ignoră starea afișată de validator (istoric, în aplicație a existat chiar un bug prin care butonul de validare D406 nu trimitea corect anul și luna către validator și întorcea mereu o stare neconcludentă — problemă reparată și reconfirmată ulterior pe date reale).
- Se confundă generarea fișierului (care produce un XML structural corect din punct de vedere al codului) cu validarea lui (care confirmă conformitatea cu schema oficială ANAF).

## Ce face iConta.eu

Validarea D406 se face cu instrumentul oficial ANAF, `DUKIntegrator_AnLunaUI.jar`, integrat în aplicație (`core/duk.py`, funcția `valideaza`), nu cu un validator generic construit intern. Fluxul e testat pe date reale — validare confirmată „valid" pentru declarații reale generate în aplicație — și bug-ul istoric de trimitere greșită a anului/lunii către validator (care ducea la o stare neclară, nu la un răspuns fals-pozitiv) a fost identificat și reparat.

Recomandarea practică din acest mecanism: nu trimite niciodată declarația în coadă direct de la generare — folosește pasul de validare din aplicație și abia după ce fișierul iese „valid" continuă spre depunere. E singurul mod verificat de a evita categoria de amendă pentru „depunere incorectă ori incompletă" din art. 337^1.

[iConta.eu](/)
