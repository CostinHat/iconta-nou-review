---
title: "Cum completez D101 pentru un SRL pe profit în 2026"
description: "Ghid de completare a D101 pentru un SRL plătitor de impozit pe profit în anul fiscal 2026, cu atenționările specifice acestui an."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum completez D101 pentru un SRL pe profit în 2026

## Temeiul legal

::: ghid-temei
Art.17 CF: "Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

Un SRL plătitor de impozit pe profit completează D101 pe structura standard P1–P53 (reconstruită după OPANAF 206/2025): profitul impozabil (P40) e impozitat cu cota de 16% (art.17), rezultând P411. Deducerile (amortizarea fiscală P11, rezerva legală P13) și cheltuielile nedeductibile (P23, cu rollup-ul P34 pentru cele legate de amortizarea contabilă) se completează manual sau, pentru rezerva legală, se calculează automat dacă nu introduceți o valoare.

## Ce se greșește în practică

Pentru anul fiscal 2026, cea mai frecventă capcană nu ține de completarea propriu-zisă, ci de termenul de depunere și de tratamentul IMCA pentru firmele mari — vezi atenționările din secțiunea următoare.

## Ce face iConta.eu

iConta.eu nu generează D101 fără CUI valid (verificat prin checksum, `core.identitate.valideaza_cui`), denumire, adresă și cod CAEN pe 4 cifre, plus datele de declarant complete (`erori_generare`, `core/d101.py`). Dacă nu introduceți manual o valoare, iConta.eu calculează automat rezerva legală (P13) din profitul contabil brut plus cheltuiala cu impozitul (cont 691), plafonată la minimul dintre 5% din bază și 20% din capitalul social minus rezerva deja constituită (CF art.26 alin.(1) lit.a)). Pentru sponsorizare (P43), iConta.eu aplică dubla limită legală: 20% din impozitul pe profit datorat (verificată de motorul oficial DUK) și, suplimentar, 0,75% din cifra de afaceri — a doua verificare a fost adăugată manual în cod, pentru că motorul DUK verifică singur doar limita de 20% (CF art.25 alin.(4) lit.i)). D101 tratează amortizarea ca intrare, nu o calculează: P11 este amortizarea fiscală (deducere — intră în P16, total deduceri, și reduce profitul impozabil), iar rândurile de tip P2x/P28 reprezintă cheltuiala cu amortizarea contabilă, care intră în rollup-ul P34 „cheltuieli nedeductibile” și se adaugă înapoi la baza impozabilă. Contabilul introduce manual ambele valori în iConta.eu. Dacă cifra de afaceri a anului precedent (în EUR) transmisă depășește pragul IMCA de 50.000.000 EUR și rândul P47 nu a fost completat manual, iConta.eu cere explicit această valoare înainte de generare — nu subevaluează tacit impozitul unei firme mari. Atenție: motorul D101 din iConta.eu calculează astăzi IMCA cu formula `impozit_minim_cifra_afaceri`, cablată pe cota fixă de 1% (`core/d101.py`, confirmat de testul `test_imca_formula_1pct_din_vt_vs_i_a`), deși legea prevede explicit 0,5% pentru anul fiscal 2026 (art.18^1 alin.(16) CF, introdus prin OUG 89/2025). Dacă firma dvs. se încadrează la IMCA pentru 2026, impozitul minim generat de aplicație poate fi dublu față de cel legal — verificați manual suma până la corectarea acestui bug. Atenție: pentru anul fiscal 2026 (declarat în 2027), motorul D101 din iConta.eu (funcția `_scadenta_2026`) afișează încă 25 martie, aliniat validatorului oficial DUKIntegrator instalat local, care nu a fost reactualizat de ANAF. Legea (OUG 8/2026, aplicabilă începând cu anul fiscal 2026) mută însă termenul de bază definitiv la 25 iunie. **Termenul legal real de reținut este 25 iunie 2027**, indiferent de data afișată azi de aplicație. În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`).

[iConta.eu](/)
