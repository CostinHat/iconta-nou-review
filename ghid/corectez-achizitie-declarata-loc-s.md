---
title: "Cum corectez o achiziție declarată cu A în loc de S?"
description: "Cum reclasifici o achiziție intracomunitară din bunuri (A) în servicii (S) în D390, și cazul concret în care corecția nu are efect."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez o achiziție declarată cu A în loc de S?

O achiziție primită e implicit clasificată automat ca „A" (achiziție intracomunitară de bunuri) în D390. Dacă operațiunea era de fapt o achiziție de servicii, tipul corect e „S" — iar aici intervine exact distincția bunuri/servicii care, pentru anumite facturi, e „înghețată" chiar din momentul înregistrării lor.

## Temeiul legal

::: ghid-temei
„A - pentru achiziţii intracomunitare de bunuri, achiziţii care urmează transferurilor scutite, achiziţii efectuate de beneficiarul livrării ulterioare în cadrul unei operaţiuni triunghiulare din alte state membre; [...] S - pentru achiziţii intracomunitare de servicii." — OPANAF nr. 705/2020, Anexa 2, Instrucțiuni, coloana „Tipul operațiunii"
:::

## Ce se greșește în practică

- Se presupune că reclasificarea A→S funcționează întotdeauna la fel, indiferent cum a fost introdusă achiziția — nu e cazul: pentru achizițiile înregistrate prin ecranul dedicat „Achiziție intracomunitară", distincția bunuri/servicii e reținută pe factură chiar la creare și decide singură tipul din D390.
- Se salvează reclasificarea în panoul D390, se vede confirmarea de succes, și se presupune că declarația a fost efectiv corectată — fără să se verifice la regenerare dacă tipul chiar s-a schimbat în XML.
- Se încearcă „editarea" bazei unei achiziții direct din panoul de clasificare, pentru o linie introdusă manual — nu există editare, doar ștergere și re-adăugare a liniei.

## Ce face iConta.eu

Pentru achizițiile primite, panoul de clasificare permite reclasificarea între „A" și „S" — dacă alegi din nou tipul implicit (A), reclasificarea salvată e ștearsă și achiziția revine pe calculul automat; dacă alegi S, se salvează un override. Sistemul validează că tipul ales e permis pentru direcția „primită" (doar A sau S); o transformare nepermisă e respinsă explicit, nu convertită tacit.

**Onest — exact acest caz (A vs. S) e cel mai probabil să nu producă niciun efect vizibil dacă achiziția a fost introdusă prin ecranul dedicat „Achiziție intracomunitară".** Aplicația reține pe factură, o singură dată la creare, dacă achiziția e „bunuri" sau „servicii", iar acest marcaj decide direct tipul din D390, indiferent de ce se selectează ulterior în panoul de reclasificare. Practic, selectorul afișează opțiuni și salvarea reușește vizual, dar la regenerarea declarației tipul rămâne neschimbat — corecția pare acceptată, dar XML-ul iese la fel ca înainte. Pentru achizițiile introduse prin fluxul obișnuit de facturare (care nu setează acest marcaj), reclasificarea A↔S funcționează normal.

Dacă achiziția a fost introdusă prin ecranul dedicat și marcajul e greșit, corectarea reală presupune stornarea și reemiterea documentului sursă — nu am identificat o rută de modificare a acestui marcaj pe un document deja creat. Suplimentar, verificarea codului de TVA al furnizorului la introducere e făcută offline doar pentru câțiva parteneri (Germania, Croația, Franța) — pentru restul țărilor UE, un cod greșit nu e semnalat de aplicație la introducere, ci abia la validarea oficială, la depunere.

[iConta.eu](/)
