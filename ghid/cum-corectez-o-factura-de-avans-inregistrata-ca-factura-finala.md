---
title: Cum corectez o factură de avans înregistrată ca factură finală?
description: Corecția se face prin stornarea liniilor de avans (409/419), pe temeiul ajustării bazei de impozitare pentru facturi de avans emise pentru operațiuni desființate total sau parțial; cursul valutar rămâne cel al avansului inițial, nu cel din ziua corecției.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez o factură de avans înregistrată ca factură finală?

Se întâmplă frecvent ca o factură care era de fapt un avans (plată parțială, înainte de livrare) să fi fost înregistrată din greșeală ca factură finală, cu toate liniile de venit/cheltuială deja recunoscute. Corecția nu e o simplă ștergere — are un temei legal specific.

## Temeiul legal

::: ghid-temei
"Baza de impozitare se reduce în următoarele situații: a) în cazul desființării totale sau parțiale a contractului pentru livrarea de bunuri sau prestarea de servicii, înainte de efectuarea acestora, dar pentru care au fost emise facturi în avans;"

"(9) În cazul evenimentelor menționate la art. 287, taxa este exigibilă la data la care intervine oricare dintre evenimente, iar regimul de impozitare, cotele aplicabile și cursul de schimb valutar sunt aceleași ca și ale operațiunii de bază care a generat aceste evenimente."

"(10) ... a) pentru situația prevăzută la art. 287 lit. a): 1. în cazul în care operațiunea este anulată total înainte de livrare/prestare, exigibilitatea taxei intervine la data anulării operațiunii, pentru contravaloarea pentru care a intervenit exigibilitatea taxei. Pentru contravaloarea pentru care nu a intervenit exigibilitatea taxei se operează anularea taxei neexigibile aferente; 2. în cazul în care operațiunea este anulată parțial înainte de livrare/prestare, se operează reducerea taxei neexigibile aferente contravalorii pentru care nu a intervenit exigibilitatea taxei, iar în situația în care cuantumul taxei aferente anulării depășește taxa neexigibilă, pentru diferență exigibilitatea taxei intervine la data anulării operațiunii;"
:::

## Care e diferența față de o simplă corecție

Dacă documentul a fost, în realitate, o plată parțială înainte de livrare/prestare — deci un avans — și nu factura finală a operațiunii, temeiul corecției nu e "am greșit tehnic o linie contabilă", ci art. 287 lit. a) din Codul fiscal: ajustarea bazei de impozitare pentru facturi de avans emise pentru un contract care s-a desființat total sau parțial (sau, în cazul de față, care nu s-a mai derulat conform documentului emis inițial).

Un aspect legal important, ușor de ratat: la stornarea/anularea avansului, **regimul de impozitare, cota și cursul de schimb valutar rămân cele de la data operațiunii de bază** — adică cele valabile la data avansului inițial, nu cele din ziua în care se face corecția (art. 282 alin. 9). Practic, nu "reinventați" cursul sau cota la data corecției; le preluați identice din nota inițială.

## Ce se greșește în practică

- Se șterge pur și simplu factura greșit înregistrată, fără o notă de stornare documentată, ceea ce lasă o gaură în cronologia documentelor și complică un eventual control.
- Se recalculează cota de TVA sau cursul valutar la data corecției, în loc să se păstreze regimul, cota și cursul de la data operațiunii de bază (avansul inițial), conform art. 282 alin. (9).
- Se tratează corecția ca pe o simplă modificare de sumă, fără să se separe explicit stornarea liniei de avans (409/419) de eventuala reînregistrare corectă ca avans propriu-zis.
- Se ignoră distincția dintre anulare totală și anulare parțială (art. 282 alin. 10 lit. a) pct. 1 și 2) — la o anulare parțială, doar taxa neexigibilă aferentă părții anulate se reduce, restul rămâne neschimbat.

## Ce face iConta.eu

Pentru un avans plătit greșit înregistrat ca factură finală, corecția tehnică se face prin `nota_regularizare_avans_platit(...)`, care inversează linia de avans: `401 = 409x` pentru capital și `401 = 4426` pentru TVA. Pentru un avans încasat, echivalentul e `nota_regularizare_avans_incasat(...)`, cu `419 = 4111` și `4427 = 4111`. Ambele funcții stornează strict avansul — docstring-ul modulului precizează explicit că "factura finală se înregistrează separat, întreagă": motorul nu generează singur factura finală corectă, doar reversul avansului.

În `core/uc_tenants.py`, orchestrarea cere explicit data livrării (`data_livrare`) pentru orice operație de tip `"regularizare"`, iar cota se calculează pe baza acestei date — nu pe data la care se face efectiv corecția, conform art. 291 alin. (6). Totuși, câmpul `tip_operatiune='regularizare_avans'` e informativ: nu ramifică generatoarele de declarații (D300/D390), regularizarea se reflectă corect prin liniile facturii (livrare minus storno avans), dar eticheta în sine nu declanșează o verificare separată în sistem — util de reținut la audit intern, chiar dacă rezultatul fiscal final e corect.

[iConta.eu](/)
