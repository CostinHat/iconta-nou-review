---
title: "Regularizarea anuală a impozitului pe profit: cum se face"
description: "Detaliază mecanismul legal al definitivării anuale a impozitului pe profit și rolul D101 în acest proces."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Regularizarea anuală a impozitului pe profit: cum se face

## Temeiul legal

::: ghid-temei
Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.

Art.41 alin.(1) CF: calculul, declararea și plata impozitului pe profit se fac trimestrial, „până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III", cu definitivare la termenul de la art.42.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Definitivarea (regularizarea) anuală a impozitului pe profit se face exclusiv prin D101, depusă până la 25 iunie inclusiv a anului următor (art.42 alin.(1)). D101 consolidează întregul exercițiu fiscal, aplicând cota de 16% (art.17) pe profitul impozabil rezultat din veniturile și cheltuielile anuale, ajustate cu deducerile (P11, P13) și cheltuielile nedeductibile (P23/P34). Plățile din timpul anului (trimestriale sau anticipate) sunt raportate separat, prin D100.

## Ce se greșește în practică

Se greșește prin amestecarea celor două declarații — corectarea unei plăți trimestriale greșite se face prin D710 (dedicat D100), nu prin D101, care rămâne strict declarația de definitivare anuală.

## Ce face iConta.eu

Plățile trimestriale/anticipate de impozit pe profit (cod_oblig 103) se depun prin D100 (F026), nu prin D101 — D101 este exclusiv declarația ANUALĂ de definitivare, generată la finalul exercițiului fiscal. Dacă nu introduceți manual o valoare, iConta.eu calculează automat rezerva legală (P13) din profitul contabil brut plus cheltuiala cu impozitul (cont 691), plafonată la minimul dintre 5% din bază și 20% din capitalul social minus rezerva deja constituită (CF art.26 alin.(1) lit.a)). Pentru sponsorizare (P43), iConta.eu aplică dubla limită legală: 20% din impozitul pe profit datorat (verificată de motorul oficial DUK) și, suplimentar, 0,75% din cifra de afaceri — a doua verificare a fost adăugată manual în cod, pentru că motorul DUK verifică singur doar limita de 20% (CF art.25 alin.(4) lit.i)). D101 tratează amortizarea ca intrare, nu o calculează: P11 este amortizarea fiscală (deducere — intră în P16, total deduceri, și reduce profitul impozabil), iar rândurile de tip P2x/P28 reprezintă cheltuiala cu amortizarea contabilă, care intră în rollup-ul P34 „cheltuieli nedeductibile” și se adaugă înapoi la baza impozabilă. Contabilul introduce manual ambele valori în iConta.eu. În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`).

[iConta.eu](/)
