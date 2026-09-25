---
title: "Amortizarea imobilizărilor achiziționate prin leasing financiar"
description: "Regula legală pentru cine amortizează un bun preluat prin leasing financiar, și granița dintre nota de leasing (recunoașterea bunului) și calculul propriu-zis al amortizării."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Amortizarea imobilizărilor achiziționate prin leasing financiar

La leasingul financiar, bunul intră în contabilitatea locatarului (firma care îl folosește) chiar de la primire, tratat ca o investiție în imobilizări. De aici decurge și regula amortizării: se ține la locatar, nu la societatea de leasing. Dar recunoașterea bunului și calculul amortizării sunt două operațiuni distincte, care nu se fac în același loc.

## Temeiul legal

::: ghid-temei
„214. ‐ (1) Înregistrarea în contabilitate a amortizării bunului ce face obiectul contractului se efectuează în cazul leasingului financiar de către locatar/utilizator, iar în cazul leasingului operațional, de către locator/finanțator. (2) În cazul leasingului financiar, achizițiile de către locatar de bunuri imobile şi mobile sunt tratate ca investiții în imobilizări, fiind supuse amortizării pe o bază consecventă cu politica normală de amortizare pentru bunuri similare ale locatarului."
— OMFP 1802/2014, pct. 214 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

- Amortizarea unui bun preluat prin leasing financiar se face **la locatar**, nu la finanțator — indiferent la cine rămâne, prin contract, titlul juridic de proprietate.
- Bunul e „tratat ca investiție în imobilizări" — adică intră în contabilitate exact ca un mijloc fix cumpărat direct, nu ca o categorie separată cu reguli proprii.
- Politica de amortizare trebuie să fie **consecventă** cu cea aplicată altor bunuri similare ale firmei — nu se inventează o regulă specială doar pentru că bunul a venit prin leasing.

## Ce se greșește în practică

- Se tratează „amortizarea în leasing financiar" ca pe o operațiune separată, de calculat manual în afara registrului de mijloace fixe al firmei.
- Se omite recunoașterea bunului la valoarea corectă de intrare (capitalul din contract, fără TVA și fără dobânda totală) înainte de a începe amortizarea — dobânda rămâne extracontabilă, nu intră în baza de amortizare.
- Se amestecă notele de leasing (167, 404, 8051) cu notele de amortizare (681=281x), care sunt operațiuni contabile diferite, ținute în locuri diferite ale aplicației.

## Ce face iConta.eu

Funcționalitatea „Leasing financiar și operațional" (`core/leasing.py`) înregistrează recunoașterea bunului la primire (2133=167, la valoarea capitalului, cu dobânda totală ținută extracontabil pe 8051) și, separat, fiecare rată și valoarea reziduală — dar **nu calculează amortizarea propriu-zisă**. Nicio funcție din acest modul nu produce o notă de amortizare. Odată intrat 2133=167 prin nota de leasing, bunul trece în registrul general de Mijloace fixe, unde e amortizat exact ca orice alt mijloc fix al firmei, fără nicio diferențiere pentru că a venit prin leasing.

[iConta.eu](/)
