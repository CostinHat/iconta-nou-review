---
title: "Ce se întâmplă dacă depui D101 după termen?"
description: "Precizează termenul legal de depunere a D101 și atenționează asupra unei neconcordanțe curente în aplicație pentru anul fiscal 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce se întâmplă dacă depui D101 după termen?

## Temeiul legal

::: ghid-temei
Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.

OUG 153/2020 art.I alin.(13) lit.a) + art.VI: pentru anii fiscali 2021–2025, termenul de depunere D101 este 25 iunie (derogare temporară de la art.41/42 CF, aplicabilă 2021–2025).
— `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

Termenul legal de depunere a D101 este 25 iunie inclusiv a anului următor celui pentru care se face definitivarea — atât pentru anii fiscali 2021–2025 (OUG 153/2020), cât și pentru anul fiscal 2026 și următorii, conform art.42 alin.(1), modificat prin OUG 8/2026. Sursele locale verificate în acest dosar nu conțin detalii despre regimul sancționator (cuantumul amenzilor, dobânzi/penalități de întârziere) pentru nedepunerea la termen — acestea sunt reglementate de Codul de procedură fiscală și trebuie verificate separat, direct la sursă (Legea 207/2015) sau cu un consultant fiscal.

## Ce se greșește în practică

Confuzia principală privește exact termenul aplicabil anului fiscal 2026: vezi atenționarea din secțiunea următoare.

## Ce face iConta.eu

Atenție: pentru anul fiscal 2026 (declarat în 2027), motorul D101 din iConta.eu (funcția `_scadenta_2026`) afișează încă 25 martie, aliniat validatorului oficial DUKIntegrator instalat local, care nu a fost reactualizat de ANAF. Legea (OUG 8/2026, aplicabilă începând cu anul fiscal 2026) mută însă termenul de bază definitiv la 25 iunie. **Termenul legal real de reținut este 25 iunie 2027**, indiferent de data afișată azi de aplicație. În aplicație: Declarații → D101 → anul → Generează (ecranul mapează codul `d101` la fișa de ajutor F027, `static/js/ecrane/declaratii.js`). Pentru consecințele nedepunerii la termen (amenzi, penalități), acest ghid nu poate cita un temei verificat local — recomandăm verificarea directă a Codului de procedură fiscală.

[iConta.eu](/)
