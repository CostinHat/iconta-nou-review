---
title: Cum închid un SRL cu bani în contul bancar?
description: Cum se calculează și se plătește netul către asociați din soldul bancar rămas la lichidare — și de ce cota de impozit aplicată de iConta.eu trebuie verificată manual.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL cu bani în contul bancar?

Soldul rămas în contul bancar (5121) la finalul lichidării este, de regulă, ultima etapă a procesului: după ce s-au valorificat activele și s-au stins datoriile, ce rămâne în bancă se împarte între asociați prin operațiunea de partaj.

## Temeiul legal

::: ghid-temei
„Venitul impozabil obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice sau din reducerea capitalului social, potrivit legii, care nu reprezintă distribuții în bani sau în natură ca urmare a restituirii cotei-părți din aporturi se impun cu o cotă de 10%, impozitul fiind final. Obligația calculării, reținerii și plății impozitului revine persoanei juridice. Impozitul calculat și reținut la sursă în cazul lichidării persoanei juridice se plătește până la data depunerii situației financiare finale la oficiul registrului comerțului, întocmită de lichidatori [...]."
— Codul fiscal (Legea 227/2015), art. 97 alin. (5)
:::

## Ce se greșește în practică

Cea mai gravă greșeală posibilă la acest pas este aplicarea unei cote greșite de impozit asupra câștigului distribuit asociaților persoane fizice (partea din rezerve și profituri, capitalul social propriu-zis rămânând neimpozabil). Din citirea directă a Codului fiscal, art. 97 alin. (5) — articolul dedicat explicit „venitul impozabil obținut din lichidarea unei persoane juridice" — prevede o **cotă fixă de 10%**, neschimbată din 2018. Acest articol este distinct de art. 97 alin. (7), care privește dividendele obișnuite și a cărui cotă a crescut la 16% de la 1 ianuarie 2026 (Legea 141/2025). Confirmarea vine și din nomenclatorul oficial ANAF pentru declarația D205, unde cele două categorii de venit apar separat, cu tratament diferit:

> „08 1.a) venituri din dividende - 8%/2024, 10%/2025, 16%/2026"
> „11 1.e) venituri din lichidarea persoanei juridice – 10%"
> — `anaf_surse/d205_struct_anaf.txt`

**Atenție — bug cunoscut al aplicației:** iConta.eu calculează în prezent impozitul pe câștigul din partaj (rezerve + profituri distribuite la lichidare) folosind **exact același registru de cote ca la dividendele obișnuite** — adică 16% începând cu 2026, în loc de 10% conform art. 97 alin. (5). Această echivalare a fost o decizie de simplificare la nivel de cod (un singur registru de cote pentru ambele situații), nu o verificare punctuală a articolului corect pentru lichidare. Până la clarificarea sau corectarea acestui aspect, **verificați manual impozitul reținut din netul plătit către asociați** și recalculați la 10% dacă este cazul, mai ales dacă lichidarea are loc după 1 ianuarie 2026.

## Ce face iConta.eu

Operația „Partaj către asociați" din ecranul de lichidare (categoria „Diverse" → „Lichidare / radiere firmă") generează automat notele contabile: capitalul social ca neimpozabil (1012=456), rezervele și profiturile ca bază impozabilă (1061/1171=456), impozitul reținut (456=446) și netul plătit către asociat, virat din contul bancar (456=5121). Aplicația afișează și cota de impozit folosită la calcul — verificați această valoare față de 10% (art. 97 alin. 5), nu doar față de cota de dividend curentă.

[iConta.eu](/)
