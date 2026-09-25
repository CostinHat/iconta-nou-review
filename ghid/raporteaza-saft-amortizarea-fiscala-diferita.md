---
title: Cum se raportează în SAF-T amortizarea fiscală diferită de cea contabilă?
description: În secțiunea Active din D406, fiecare activ are un bloc Valuations care poate conține mai multe evaluări (cardinalitate 1..*), fiecare identificată prin AssetValuationType. Evaluarea contabilă și cea fiscală se raportează separat, iar registrul-jurnal din SAF-T rămâne strict contabil (structura D406, OPANAF 1783/2021).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează în SAF-T amortizarea fiscală diferită de cea contabilă?

Diferența dintre cele două amortizări se raportează în secțiunea Active (Assets), nu în registrul-jurnal. Structura D406 publicată de ANAF pentru OPANAF 1783/2021 prevede, pentru fiecare activ, un bloc **Valuations** despre care spune: „Informațiile pot fi raportate în diferite scopuri. Mai multe tipuri de informații pot fi în acest SAF.” Elementul Valuation are cardinalitatea 1..*, deci un activ poate avea mai multe evaluări.

### Ce conține fiecare evaluare

Fiecare bloc Valuation are câmpurile lui, independente de celelalte evaluări:
- **AssetValuationType**: „Descrie scopul raportării: f.i. comercial, fiscal”;
- **ValuationClass**: clasificarea activului „în scopuri de raportare (fiscală)”. Schema conține foaia CatalogActive, adică Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe;
- **AssetLifeYear** sau **AssetLifeMonth**: durata de viață, cu unul singur dintre cele două câmpuri;
- **DepreciationMethod**, **DepreciationPercentage**, **DepreciationForPeriod**: metoda, rata și amortizarea din perioadă;
- **AccumulatedDepreciation**, **BookValueBegin**, **BookValueEnd**: amortizarea cumulată și valorile de la început și sfârșit.

Dacă amortizarea contabilă și cea fiscală diferă prin metodă, durată sau valoare, schema îți permite să raportezi două blocuri Valuation pentru același activ, unul contabil și unul fiscal. Nu trebuie să alegi doar una dintre ele.

La fel se procedează și pentru tranzacțiile cu active (AssetTransactions). Elementul **AssetTransactionValuations** are propriile evaluări (cardinalitate 1..*), cu explicația „Aceste valori ale tranzacției pot diferi în funcție de tipul de evaluare a activelor”.

### Ce nu se modifică

Secțiunea GeneralLedgerEntries conține înregistrările contabile „așa cum sunt înregistrate în sistemul contabil” (OPANAF 1783/2021). Amortizarea fiscală nu se înregistrează în contabilitate. În registrul-jurnal apare doar amortizarea contabilă (6811 = 281x). Diferența fiscală se reflectă în calculul impozitului pe profit din D101, unde se deduce amortizarea fiscală calculată potrivit Codului fiscal art. 28.

### Exemplu

O firmă cumpără în 2026 un utilaj de 120.000 lei. Contabil îl amortizează liniar pe 8 ani, adică 15.000 lei pe an. Fiscal aplică metoda degresivă sau altă metodă permisă de art. 28, cu o durată din catalog, iar amortizarea fiscală din primul an iese mai mare. În D406 Active, utilajul apare cu:
- Valuation 1, cu AssetValuationType contabil, metoda liniară și DepreciationForPeriod de 15.000;
- Valuation 2, cu AssetValuationType fiscal, metoda fiscală și amortizarea fiscală a perioadei.

Amortizarea cumulată din evaluarea contabilă trebuie să corespundă soldului contului 281x din balanță.

### Atenție

Schema nu impune valori fixe pentru AssetValuationType. Câmpul este text scurt (SAFshorttextType), iar descrierea dă doar exemple. Folosește aceleași etichete la toate activele și de la un an la altul, ca evaluările să poată fi comparate.

Secțiunea Active se raportează o dată pe an. Observațiile din schemă arată că raportarea ei „este obligatorie cel puțin o dată pe an pentru firmele care au active în evidență”.

### De reținut
- Amortizarea fiscală diferită se raportează ca evaluare separată în Assets/Valuations, nu în registrul-jurnal.
- Fiecare evaluare are propria metodă, durată, amortizare pe perioadă și amortizare cumulată.
- Evaluarea contabilă trebuie să corespundă balanței. Diferența fiscală se reflectă în D101.
