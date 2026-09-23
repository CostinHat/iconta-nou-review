---
title: De ce diferă TVA din D300 de jurnalul de vânzări?
description: TVA colectată din D300 (rândul TOTAL TAXĂ COLECTATĂ) se compară cu rulajul creditor al contului 4427 — diferențele apar mai ales din facturi de vânzare fără notă validată sau înregistrate în altă lună decât cea a facturii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# De ce diferă TVA din D300 de jurnalul de vânzări?

Când TVA colectată din D300 nu se potrivește cu jurnalul de vânzări, comparația de referință este între rândul **TOTAL TAXĂ COLECTATĂ (R17_2)** al declarației și rulajul creditor al contului **4427**. Diferența nu înseamnă automat o eroare de contabilizare — poate fi și un decalaj legitim între momentul facturării și cel al înregistrării.

## Temeiul legal

::: ghid-temei
Art. 281 din Codul fiscal (Legea 227/2015) — "Faptul generator pentru livrări de bunuri și prestări de servicii" — stabilește momentul de la care se naște obligația de colectare a TVA. D300 se calculează pe facturile lunii (fapt generator); jurnalul de vânzări și rulajul contului 4427 reflectă înregistrările contabile efectiv făcute. Titlul și numărul articolului sunt confirmate în sursele legale folosite de aplicație; textul integral nu e citat literal aici.

Art. 282 din Codul fiscal — "Exigibilitatea pentru livrări de bunuri și prestări de servicii" — explică de ce, pentru firmele cu TVA la încasare, exigibilitatea colectării poate fi decalată față de data facturii, fără ca asta să fie o eroare. Menționat ca temei conceptual, nu ca prag de calcul folosit direct în verificare.
:::

## Cauze frecvente ale diferenței

- **Notă în ciornă, nu validată** — o factură de vânzare există în jurnal, dar nota contabilă aferentă nu a fost încă validată, deci nu intră în comparație.
- **Facturi cu data în altă lună decât înregistrarea** — factura e emisă în luna X, dar înregistrată contabil în luna Y.
- **Storno neînregistrat** — o factură stornată la client, dar corecția nu a ajuns încă în evidența proprie.
- **TVA la încasare** — colectarea devine exigibilă la încasare, nu la facturare, pentru firmele înscrise în acest regim.
- **Regularizări** — ajustări ulterioare ale bazei sau TVA-ului unei vânzări deja înregistrate.

Ca și la TVA deductibilă, aceste cauze nu sunt ajustate automat — sunt marcate pentru investigație, pentru că nu pot fi confirmate mecanic doar din datele existente.

## Ce se greșește în practică

- Se presupune că orice diferență la colectată înseamnă o factură „lipsă" din contabilitate — de multe ori e doar o notă nevalidată sau o factură înregistrată în altă lună.
- Se ignoră regimul de TVA la încasare ca posibilă cauză legitimă a decalajului, mai ales la firme care au trecut recent la acest regim.
- Se validează o corecție fără verificarea contului corect (4427, nu 4428 — TVA neexigibilă e informativ, nu parte din comparația de bază).

## Ce face iConta.eu

Aplicația compară automat rulajul creditor al contului 4427 cu rândul TOTAL TAXĂ COLECTATĂ din D300, folosind doar notele validate, cu o toleranță de 1 leu. Când diferența e explicată mecanic de o factură fără notă validată, propune corecția pentru validare; când cauza ține de storno neînregistrat, TVA la încasare sau regularizări, semnalează situația pentru investigație manuală, fără ajustare automată.

[iConta.eu](/)
