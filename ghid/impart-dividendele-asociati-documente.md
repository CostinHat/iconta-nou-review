---
title: "Cum se împart dividendele între asociați: documente"
description: "Regula legală de împărțire a dividendelor între asociați, proporțional cu capitalul social vărsat, și modul în care iConta.eu înregistrează contabil operațiunea."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se împart dividendele între asociați: documente

Dividendul nu se împarte „pe din două" între asociați sau după o înțelegere informală, ci după o regulă legală precisă: proporțional cu cota fiecăruia din capitalul social vărsat. Documentul de bază e hotărârea adunării generale de aprobare a situațiilor financiare anuale (sau, pentru dividendul interimar, situațiile financiare interimare), pe baza căreia se calculează suma cuvenită fiecărui asociat și se generează nota contabilă.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend.
[...] Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social vărsat, opțional trimestrial pe baza situațiilor financiare interimare și anual, după regularizarea efectuată prin situațiile financiare anuale [...]"
— Legea 31/1990, art. 67 alin. (1) și (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Criteriul de împărțire e **cota de participare la capitalul social vărsat**, nu numărul de asociați și nu o cotă negociată separat de actul constitutiv.
- Distribuirea se poate face **trimestrial**, pe bază de situații financiare interimare, cu regularizare obligatorie prin situațiile financiare anuale.
- Documentele care stau la baza sumei de repartizat sunt: situațiile financiare (anuale sau interimare) aprobate, hotărârea adunării generale/asociaților de aprobare a repartizării profitului și, dacă e cazul, actul constitutiv (dacă acesta prevede o altă cheie de repartizare decât cea legală implicită).

## Ce se greșește în practică

- Se împarte dividendul brut în părți egale între asociați, ignorând cotele reale de participare la capitalul social vărsat.
- Se distribuie dividend interimar fără documentul obligatoriu — situațiile financiare interimare — și fără a face ulterior regularizarea prin situațiile financiare anuale.
- Se calculează suma netă către fiecare asociat fără a reține impozitul pe dividende, sau se aplică o cotă de impozit greșită (cota se schimbă de la un an la altul).

## Ce face iConta.eu

Din ecranul **Operațiuni speciale > Finanțare**, intrarea „Decontări asociați (455/457)", iConta.eu generează nota contabilă a dividendului: pentru dividendul anual, `1171=457` (brut) și `457=446` (impozit reținut), iar pentru dividendul interimar, `463=456` și `456=446`, cu opțiunea de a înregistra și plata netă către asociat pe contul 5121. Cota de impozit e citită automat, în funcție de data operațiunii, din registrul intern de cote istorice al aplicației, nu e hardcodată.

De precizat onest: motorul contabil primește ca intrare o singură sumă („brut") pentru operațiunea de dividend — el **nu calculează el însuși partea fiecărui asociat** pornind de la cotele de participare. Împărțirea sumei totale aprobate pe fiecare asociat, conform art. 67 alin. (2), rămâne în sarcina contabilului, care introduce separat nota corespunzătoare fiecărei sume individuale.

[iConta.eu](/)
