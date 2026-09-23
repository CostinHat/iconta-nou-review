---
title: "Cum ies din sistemul TVA la încasare?"
description: "Regulile legale pentru ieșirea din sistemul TVA la încasare — termenul minim de rămânere, depășirea plafonului și notificarea la ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum ies din sistemul TVA la încasare?

Ieșirea din sistemul TVA la încasare nu e o simplă bifă pe care o schimbați când vreți — legea impune un termen minim de rămânere în sistem și un calendar strict de notificare.

## Temeiul legal

::: ghid-temei
Art. 324 alin. (16) Cod fiscal: „A.N.A.F. organizează Registrul persoanelor impozabile care aplică sistemul TVA la încasare... Registrul este public și se afișează pe site-ul A.N.A.F." — verificat în `cod_fiscal_227_2015_consolidat.txt`.
:::

Conform art. 282 alin. (5) Cod fiscal, o firmă care a optat pentru TVA la încasare are obligația de a rămâne în sistem cel puțin până la sfârșitul anului calendaristic în care a optat, cu o singură excepție: depășirea plafonului în cursul anului. Ieșirea voluntară (opțională) se face prin notificare depusă între 1 și 20 ale lunii, dar nu în primul an de aplicare a sistemului.

Dacă ieșirea e forțată de depășirea plafonului, se aplică art. 324 alin. (14): notificarea trebuie depusă până la data de 20 a lunii următoare celei în care s-a depășit plafonul. Nedepunerea notificării în acest termen duce la **radiere din oficiu** de către organul fiscal.

Indiferent de motiv, ieșirea și intrarea în sistem se reflectă în Registrul public al persoanelor care aplică TVA la încasare, organizat de ANAF conform art. 324 alin. (16) — registru pe care orice partener comercial îl poate consulta.

## Ce se greșește în practică

Cea mai frecventă greșeală e depunerea notificării de ieșire prea devreme, în primul an de aplicare a sistemului, când legea nu o permite (art. 282 alin. 5). A doua greșeală e ignorarea termenului de 20 ale lunii următoare depășirii plafonului (art. 324 alin. 14) — nedepunerea la timp nu înseamnă că firma rămâne liniștit în sistem, ci că e radiată din oficiu, cu efecte asupra dreptului de deducere al partenerilor (art. 297).

## Ce face iConta.eu

Motorul de decont (`core/d300.py`) citește un flag `tva_la_incasare` de pe profilul firmei pentru a decide dacă aplică mecanismul de exigibilitate la încasare (accesibil, conform înregistrării funcționalității, din „Operatiuni speciale > TVA regimuri"). Aplicația nu depune și nu transmite automat notificarea de intrare/ieșire către ANAF — aceasta rămâne o procedură administrativă separată (art. 324), iar aplicația nu verifică live Registrul public ANAF al persoanelor înscrise. Calculul de exigibilitate din decont urmează pur și simplu starea flagului setat de contabil pe profilul firmei.

[iConta.eu](/)
