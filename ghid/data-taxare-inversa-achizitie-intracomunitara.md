---
title: La ce dată se aplică taxarea inversă la o achiziție intracomunitară
description: Taxa la o achiziție intracomunitară se înregistrează în luna în care devine exigibilă, prin 4426 = 4427, conform pct. 109 alin. (1) din normele HG 1/2016 — nu la data plății și nu cu o cotă „înghețată" dintr-o perioadă anterioară.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# La ce dată se aplică taxarea inversă pentru o achiziție intracomunitară?

Data contează dublu la o achiziție intracomunitară: stabilește în ce lună (perioadă fiscală) apare operațiunea în decont și în D390, și stabilește ce cotă de TVA se aplică — pentru că o cotă în vigoare azi poate să nu mai fie cea corectă peste câteva luni, dacă legea o schimbă. Greșeala tipică e legarea taxării inverse de data plății către furnizor, când de fapt ea e legată de exigibilitatea taxei.

## Temeiul legal

::: ghid-temei
**Norme metodologice, HG 1/2016, pct. 109 alin. (1)** — momentul înregistrării: *„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."*
:::

## Ce înseamnă „perioada în care taxa e exigibilă"

Norma leagă explicit înregistrarea contabilă de **perioada fiscală de exigibilitate**, nu de data facturii ca atare și nu de data plății. Practic, asta înseamnă:

- Taxarea inversă (`4426 = 4427`) se înregistrează în luna în care taxa devine exigibilă pentru operațiunea respectivă, indiferent când se face efectiv plata către furnizor — o achiziție facturată într-o lună și plătită în alta nu „mută" data taxării.
- Cota de TVA aplicată e cea în vigoare pentru perioada de exigibilitate a operațiunii, nu cota curentă la momentul în care cineva înregistrează manual nota contabilă cu întârziere. De aceea o cotă „scrisă o dată" într-un șablon sau o constantă e riscantă: rămâne validă doar până la prima schimbare legislativă a cotei, moment în care produce sume greșite pentru orice operațiune înregistrată cu întârziere sau retroactiv.
- Formula `4426 = 4427` se aplică identic, indiferent de tipul concret de operațiune cu taxare inversă (achiziție de bunuri, servicii primite sau altă situație reglementată) — clauza de generalizare din norme o confirmă explicit.

Stabilirea exactă a datei de exigibilitate pentru fiecare tip de operațiune (bunuri versus servicii, avansuri, facturare anticipată) ține de reguli separate ale Codului fiscal privind faptul generator și exigibilitatea, care nu fac obiectul acestui ghid.

## Ce se greșește în practică

- **Se leagă taxarea inversă de data plății către furnizor.** Data care contează e exigibilitatea taxei, nu momentul în care banii ies efectiv din cont.
- **Se aplică retroactiv cota curentă** unei operațiuni din urmă cu câteva luni, în loc de cota în vigoare pentru perioada de exigibilitate a operațiunii respective.
- **Se amână înregistrarea** până la reconcilierea facturii cu extrasul de cont, „ca să fie totul pe aceeași dată" — operațiunea trebuie evidențiată în perioada ei fiscală, nu în perioada în care se face contabilitatea efectiv.

## Ce face iConta.eu

Calculul taxei aplică formula `TVA = bază × cotă / 100`, cu rotunjire aritmetică (`ROUND_HALF_UP`) la 2 zecimale. Cota nu are valoare implicită — trebuie transmisă explicit la fiecare calcul, tocmai pentru ca o schimbare de cotă prin lege să nu rămână „înghețată" într-o valoare veche folosită din neatenție pentru o perioadă la care nu se mai aplică.

[iConta.eu](/)
