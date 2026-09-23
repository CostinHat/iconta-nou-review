---
title: "Cum corectez o livrare intracomunitară declarată greșit în D390?"
description: "Cum funcționează reclasificarea unei livrări intracomunitare în panoul D390 și în ce caz corecția nu are, de fapt, niciun efect vizibil."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez o livrare intracomunitară declarată greșit în D390?

O livrare intracomunitară e implicit clasificată automat cu tipul „L" în D390. Dacă operațiunea era de fapt altceva — o prestare de serviciu (P), o livrare în cadrul unei operațiuni triunghiulare (T) sau în regim special agricultori (R) — panoul de clasificare din pasul 2 al declarației permite reclasificarea. Dar există un caz în care această corecție nu produce niciun efect, și trebuie știut din timp.

## Temeiul legal

::: ghid-temei
„L - pentru livrări intracomunitare de bunuri către alte state membre; T - pentru livrări în cadrul unei operaţiuni triunghiulare; [...] P - pentru prestările intracomunitare de servicii; [...] R - livrări intracomunitare de bunuri efectuate în cadrul regimului special pentru agricultori." — OPANAF nr. 705/2020, Anexa 2, Instrucțiuni, coloana „Tipul operațiunii"
:::

## Ce se greșește în practică

- Se presupune că orice operațiune clasificată automat ca „L" poate fi mereu redirecționată către alt tip din panoul de reclasificare — nu întotdeauna, vezi mai jos.
- Se ignoră faptul că o tranziție ilegală (de exemplu, transformarea unei operațiuni de tip „emisă" într-un tip specific direcției „primită") e respinsă explicit de aplicație, nu convertită tacit la implicit — deci o eroare de acest fel se vede imediat, nu rămâne ascunsă.
- Se încearcă „editarea" valorii unei operațiuni direct din panoul de clasificare — pentru o linie manuală, nu există buton de editare, doar ștergere și re-adăugare; pentru o operațiune provenită dintr-o factură, valoarea se corectează la sursă (pe factură), nu în panoul D390.

## Ce face iConta.eu

Pentru facturile emise, panoul de clasificare din pasul 2 al declarației D390 afișează tipul curent (implicit „L") și permite reclasificarea către T, P sau R prin selectarea altui tip. Dacă alegi din nou tipul implicit (L), reclasificarea salvată anterior e ștearsă și operațiunea revine pe calculul automat. Sistemul validează direcția și tipul ales: o combinație nepermisă e respinsă cu eroare explicită, nu ajunge tacit la o clasificare greșită.

**Onest — există un caz în care reclasificarea nu are niciun efect vizibil**: dacă factura a fost creată prin ecranul dedicat „Livrare intracomunitară" (nu prin emiterea obișnuită de factură), aplicația reține pe factură, o singură dată, la creare, dacă operațiunea e „bunuri" sau „servicii" — și acest marcaj decide direct tipul din D390, indiferent ce alegi ulterior în panoul de reclasificare. Practic, pentru acest tip de factură, selectorul din panou tot afișează opțiuni și salvarea reușește, dar la regenerarea declarației XML-ul iese neschimbat — corecția pare acceptată, dar nu se produce. Pentru facturile emise prin ecranul obișnuit de facturare (care nu setează acest marcaj), reclasificarea funcționează normal.

Dacă te afli în acest caz și ai nevoie de o schimbare reală de tip pentru o factură emisă prin ecranul dedicat de livrare intracomunitară, corectarea presupune stornarea și reemiterea facturii — nu am identificat o rută de modificare a acestui marcaj pe o factură deja creată.

[iConta.eu](/)
