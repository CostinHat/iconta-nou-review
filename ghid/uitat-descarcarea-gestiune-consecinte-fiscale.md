---
title: "Am uitat descărcarea de gestiune: consecințe fiscale"
description: Ce se întâmplă contabil și fiscal dacă o lună rămâne fără descărcare de gestiune global-valorică și cum se recuperează în iConta.eu.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am uitat descărcarea de gestiune: consecințe fiscale

La metoda global-valorică, vânzările (contul 707) se înregistrează pe măsură ce au loc, dar costul mărfii vândute (607), adaosul aferent (378) și TVA neexigibilă aferentă (4428) nu se descarcă automat imediat — ele se calculează și se notează o singură dată, la finalul lunii, prin nota de descărcare de gestiune. Dacă acest pas e omis, vânzarea rămâne „pe jumătate" înregistrată.

## Temeiul legal

::: ghid-temei
„Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (4)
:::

Pentru că formula e cumulată pe exercițiu, o lună omisă nu „dispare" din calcul — la prima descărcare rulată ulterior, coeficientul K va folosi în continuare soldurile și rulajele reale, cumulate corect de la 1 ianuarie. Ce nu se recuperează automat este partea de vânzări: rulajul contului 707 folosit de calculul de descărcare este citit strict pe luna pentru care se rulează descărcarea, nu cumulat. O lună omisă rămâne, deci, fără nota ei de descărcare până când cineva o rulează explicit pentru luna respectivă.

## Ce se greșește în practică

- Se presupune că, dacă se rulează descărcarea pentru luna curentă, aceasta „prinde" automat și vânzările lunii anterioare, omise. Nu e cazul: vânzările descărcate la o rulare sunt cele ale lunii pentru care rularea a fost cerută, nu un cumul al tuturor vânzărilor nedescărcate.
- Se lasă mai multe luni consecutive nedescărcate, ceea ce înseamnă că pentru toate acele luni contul 607 (cheltuiala cu marfa vândută) rămâne subevaluat, iar contul 371 (mărfuri) rămâne supraevaluat față de stocul faptic — rezultatul contabil lunar afișat între timp nu reflectă costul real al vânzărilor.
- Se ignoră efectul asupra TVA neexigibile: contul 4428 aferent vânzărilor din lunile omise nu e descărcat, deci taxa nu e transferată acolo unde ar trebui, la momentul potrivit.

## Ce face iConta.eu

Funcția de descărcare lunară primește explicit anul și luna pentru care se calculează, ceea ce înseamnă că o lună omisă poate fi descărcată ulterior, separat, cerând acea lună anume — recuperarea nu e automată la următoarea rulare, ci trebuie inițiată punctual pentru luna rămasă în urmă. Coeficientul K rămâne corect din punct de vedere al soldurilor cumulate, pentru că se calculează mereu din rulajele reale, validate, ale conturilor 371/378/4428 de la începutul anului — dar contabilul trebuie să identifice și să ruleze manual fiecare lună pentru care lipsește nota de descărcare, pentru ca vânzările acelei luni să-și primească efectiv costul, adaosul și TVA neexigibilă aferente.

[iConta.eu](/)
