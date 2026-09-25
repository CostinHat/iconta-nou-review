---
title: "Cum se înregistrează un mijloc fix cumpărat prin leasing operațional?"
description: "La leasingul operațional, locatarul nu cumpără și nu înregistrează niciun mijloc fix — bunul rămâne la locator; firma utilizatoare înregistrează doar chiria."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează un mijloc fix cumpărat prin leasing operațional?

Întrebarea pornește de la o premisă greșită: la leasingul operațional, firma utilizatoare (locatarul) nu cumpără niciun bun și nu înregistrează niciun mijloc fix — oricât de lungă ar fi durata contractului. Bunul rămâne, contabil și fiscal, al societății de leasing.

## Temeiul legal

::: ghid-temei
„218. ‐ (1) În contabilitatea locatarului, bunurile luate în leasing operațional sunt evidențiate în conturi de evidență din afara bilanțului. (2) Sumele plătite sau de plătit se înregistrează în contabilitatea locatarului ca o cheltuială în contul de profit şi pierdere, conform contabilității de angajamente."
— OMFP 1802/2014, pct. 218 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014.txt)

„(1) În cazul leasingului financiar utilizatorul este tratat din punct de vedere fiscal ca proprietar, în timp ce, în cazul leasingului operațional, locatorul are această calitate."
— Legea 227/2015, art. 29 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- La leasingul operațional nu există niciun transfer al bunului către patrimoniul contabil al locatarului — nici de fapt, nici pe hârtie.
- Bunul rămâne al locatorului, care e și proprietarul lui fiscal, conform Codului fiscal.
- Singura înregistrare pe care o face firma utilizatoare e cheltuiala cu chiria (rata de leasing) — niciodată o intrare de imobilizare.

## Ce se greșește în practică

- Se pornește de la premisa că leasingul operațional „cumpără" un mijloc fix pentru utilizator — de fapt e o formă de închiriere, oricât de lung ar fi contractul.
- Se caută, fără succes, un cont de imobilizare de debitat — singura înregistrare corectă e pe un cont de cheltuială (612).
- Se încearcă introducerea bunului în registrul de Mijloace fixe al firmei utilizatoare, deși bunul nu-i aparține contabil.

## Ce face iConta.eu

Pentru leasing operațional, funcția `nota_rata_operational` din F056 (Leasing financiar și operațional) înregistrează doar chiria: contul de cheltuială (implicit 612) = 401, plus TVA pe 4426 — niciodată un cont de imobilizare. Dacă întrebarea reală e „cum înregistrez rata de leasing operațional", răspunsul e chiar acest ecran; dacă e chiar despre cumpărarea unui mijloc fix, subiectul aparține de fapt leasingului financiar (F056, tipul „Primire bun") sau unei achiziții directe, nu leasingului operațional. Notă: la data acestui ghid, ecranul „Leasing" nu colectează câmpul de cotă TVA pentru tipul „Chirie leasing operațional", deci trimiterea acestei note eșuează azi din interfață cu eroare de validare.

[iConta.eu](/)
