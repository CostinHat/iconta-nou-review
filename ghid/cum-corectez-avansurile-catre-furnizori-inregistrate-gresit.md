---
title: Cum corectez avansurile către furnizori înregistrate greșit?
description: Corecția unui avans plătit greșit (sumă, cont analitic sau furnizor eronat) se face prin stornarea liniei de avans pe temeiul ajustării bazei de impozitare, păstrând regimul, cota și cursul valutar de la data avansului inițial, nu de la data corecției.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez avansurile către furnizori înregistrate greșit?

Un avans plătit unui furnizor poate fi înregistrat greșit dintr-un motiv sau altul: sumă incorectă, cont analitic greșit (409 folosit pentru altă destinație decât cea reală), sau chiar furnizor greșit. Corecția are un temei legal precis, nu e doar o operațiune tehnică.

## Temeiul legal

::: ghid-temei
"Baza de impozitare se reduce în următoarele situații: a) în cazul desființării totale sau parțiale a contractului pentru livrarea de bunuri sau prestarea de servicii, înainte de efectuarea acestora, dar pentru care au fost emise facturi în avans;"

"(9) În cazul evenimentelor menționate la art. 287, taxa este exigibilă la data la care intervine oricare dintre evenimente, iar regimul de impozitare, cotele aplicabile și cursul de schimb valutar sunt aceleași ca și ale operațiunii de bază care a generat aceste evenimente."

"(10) ... a) pentru situația prevăzută la art. 287 lit. a): 1. în cazul în care operațiunea este anulată total înainte de livrare/prestare, exigibilitatea taxei intervine la data anulării operațiunii, pentru contravaloarea pentru care a intervenit exigibilitatea taxei. Pentru contravaloarea pentru care nu a intervenit exigibilitatea taxei se operează anularea taxei neexigibile aferente; 2. în cazul în care operațiunea este anulată parțial înainte de livrare/prestare, se operează reducerea taxei neexigibile aferente contravalorii pentru care nu a intervenit exigibilitatea taxei..."
:::

## Cum se face corect stornarea

Corecția unui avans plătit greșit înregistrat nu e o simplă ștergere de notă, ci o stornare care urmează regula ajustării bazei de impozitare pentru facturi de avans (art. 287 lit. a) — chiar dacă motivul stornării e o greșeală de operare, nu o desființare de contract propriu-zisă, mecanica contabilă e aceeași: se inversează linia de avans.

Regula esențială la stornare: **regimul de impozitare, cota și cursul de schimb valutar rămân cele de la data operațiunii inițiale** (avansul greșit înregistrat), nu cele din ziua în care se face corecția (art. 282 alin. 9). Practic, stornați exact ce ați înregistrat, la aceleași valori, apoi reînregistrați corect avansul (dacă acesta a existat efectiv, doar cu date greșite) sau înregistrați corect operațiunea reală, dacă suma nu era deloc un avans.

## Ce se greșește în practică

- Se șterge nota greșit înregistrată direct din jurnal, fără o notă de stornare vizibilă, ceea ce complică reconstituirea traseului documentelor la un control.
- Se recalculează cota TVA sau cursul valutar la data corecției, în loc să se preia identic cota și cursul de la data avansului inițial (art. 282 alin. 9).
- Se corectează doar suma, fără să se verifice și contul analitic 409 folosit (`destinatie` greșită la stocuri/servicii/imobilizări) — o destinație greșită are efect asupra clasificării activului, nu doar asupra sumei.
- Se face corecția fără să se distingă între o eroare totală (tot avansul e greșit → stornare integrală) și o eroare parțială (doar o parte din sumă e greșită → reducerea taxei neexigibile aferente doar pentru diferența greșită), conform distincției din art. 282 alin. (10) lit. a) pct. 1 și 2.

## Ce face iConta.eu

Corecția tehnică se face prin `nota_regularizare_avans_platit(...)`, care inversează avansul: `401 = 409x` pentru capital și `401 = 4426` pentru TVA, folosind același cont analitic 409x (4091-4094) ca la avansul inițial. Cota de TVA trebuie transmisă explicit la fiecare apel — motorul nu are o valoare implicită, exact ca să evite aplicarea din greșeală a unei cote curente în locul celei corecte de la data avansului.

Un aspect util pentru audit: câmpul `tip_operatiune='regularizare_avans'` e informativ, nu declanșează o ramificație separată în generatoarele de declarații — regularizarea se reflectă corect prin liniile contabile (rezultatul fiscal net iese corect), dar eticheta nu produce automat o verificare sau un raport dedicat de "avansuri corectate". Dacă aveți nevoie de trasabilitate suplimentară pentru corecțiile de avansuri greșit înregistrate, recomandăm documentarea separată (notă internă/referință) a motivului corecției, în afara mecanicii pur contabile oferite de motor.

[iConta.eu](/)
