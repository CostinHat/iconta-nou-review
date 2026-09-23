---
title: De ce diferă TVA din D300 de jurnalul de cumpărări?
description: TVA deductibilă din D300 (rândul TOTAL TAXĂ DEDUCTIBILĂ) trebuie comparată cu rulajul debitor al contului 4426, nu cu un alt rând al declarației — o confuzie frecventă de rând poate produce diferențe false.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# De ce diferă TVA din D300 de jurnalul de cumpărări?

Când TVA deductibilă din D300 nu se potrivește cu jurnalul de cumpărări, primul lucru de verificat e chiar rândul din declarație folosit în comparație: rândul corect este **TOTAL TAXĂ DEDUCTIBILĂ (R27_2)**, comparat cu rulajul debitor al contului **4426**. Un alt rând al declarației (cel de „ajustări/pro-rata") înseamnă altceva și nu trebuie confundat cu TVA-ul dedus efectiv.

## Temeiul legal

::: ghid-temei
Art. 281 din Codul fiscal (Legea 227/2015) — "Faptul generator pentru livrări de bunuri și prestări de servicii" — stabilește momentul nașterii obligației/dreptului de TVA. D300 se întocmește pe baza facturilor lunii (fapt generator); jurnalul de cumpărări și rulajul contului 4426 reflectă înregistrările contabile efectiv făcute — o diferență de calendar între cele două nu e automat o eroare. Titlul și numărul articolului sunt confirmate în sursele legale folosite de aplicație; textul integral nu e citat literal aici.
:::

## Cauze frecvente ale diferenței

- **Notă în ciornă, nu validată** — o achiziție înregistrată dar cu nota încă nevalidată nu contează ca evidență în comparație, deși există deja în jurnal.
- **Facturi cu data în altă lună decât înregistrarea** — factura are data lunii X, dar a fost înregistrată contabil în luna Y; D300 și rulajul contului „văd" diferit momentul.
- **Storno neînregistrat** — o corecție deja făcută la furnizor, dar neoglindită încă în evidența proprie.
- **TVA la încasare** — pentru firmele la care exigibilitatea e decalată la plată, momentul deducerii nu coincide automat cu data facturii.
- **Regularizări** — ajustări ulterioare care modifică baza sau TVA-ul unei achiziții deja înregistrate.

Aceste cauze nu sunt corectate automat de aplicație — sunt semnalate ca „investigație", pentru că nu pot fi dovedite mecanic doar din date.

## Ce se greșește în practică

- Se compară D300 cu rândul greșit al declarației (ajustări/pro-rata în loc de TOTAL TAXĂ DEDUCTIBILĂ) — rezultă o diferență care nu există de fapt.
- Se validează în grabă o notă de corecție fără să se verifice mai întâi dacă diferența are o cauză clară (executabilă) sau dacă e nevoie de investigație (storno, TVA la încasare).
- Se ignoră posibilitatea ca o achiziție să fie înregistrată corect valoric, dar în luna greșită — caz în care „corecția" reală e mutarea în perioada corectă, nu ajustarea sumei.

## Ce face iConta.eu

Aplicația compară automat rulajul debitor al contului 4426 cu rândul TOTAL TAXĂ DEDUCTIBILĂ din D300, ținând cont doar de notele validate, cu o toleranță de 1 leu. Când diferența e explicată mecanic de o achiziție fără notă validată, propune corecția pentru validare; când cauza ține de storno neînregistrat, TVA la încasare sau regularizări, semnalează situația pentru investigație manuală, fără să ajusteze automat contul.

[iConta.eu](/)
