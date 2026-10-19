# Nomenclatorul obligațiilor de plată D100 / D710 / D112 — sursele (comanda Costin 9.1, A.3, 19.10.2026)

Generat în `core/nomenclator_obligatii.py` de `scripts/nomenclator_obligatii.py`; garda `core/test_nomenclator_obligatii.py`.

| rol | fișier | de unde | descărcat | sha256 |
|---|---|---|---|---|
| denumirea D100 / D710 (nivel 1, MO) | `opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.html` — anexa nr. 3 „Nomenclatorul obligațiilor de plată la bugetul de stat”, forma consolidată 15.05.2026 | legislatie.just.ro (adus anterior în corpus) | — | în `.sha256` |
| codul XML al poziției D100 / D710 (nivel 2, procedură ANAF) | `structura_D100-D710_0126_140926.pdf` (+ `.txt` = `pdftotext` simplu) | https://static.anaf.ro/static/10/Anaf/Declaratii_R/AplicatiiDec/structura_D100-D710_0126_140926.pdf (legat din https://static.anaf.ro/static/10/Anaf/Declaratii_R/100.html) | 19.10.2026 | `e374389299342b5fbbd88ce8105b12b21d58f1d12586d5b18e1ea177553045a8` |
| denumirea D112 (nivel 1, MO 463 bis / 2.06.2026) | `opanaf_605_2026_d112.pdf` — anexa nr. 2 Nomenclatorul „Creanţe fiscale”; cuvintele cu coordonate în `nomenclator_creante_d112_bbox.html` (`pdftotext -bbox -f 22 -l 25 opanaf_605_2026_d112.pdf`) | adus anterior în corpus | 19.10.2026 (extragerea) | în `.sha256` |
| codul XML al poziției D112 (nivel 2) | `structura_D112_0726_070926.pdf` (+ `.txt` = `pdftotext -layout`) — „Nomenclator 3 – Obligatii de plata la BS si BASFS (cf.anexa2 Ordin comun)” | https://static.anaf.ro/static/10/Anaf/Declaratii_R/AplicatiiDec/structura_D112_0726_070926.pdf (legat din https://static.anaf.ro/static/10/Anaf/Declaratii_R/112.html) | 19.10.2026 | `3c7c78aee3588357da0b801aa322107071abc010ed25727eb705ca3c5b6edfce` |

Ce NU intră (și de ce): pozițiile pe care ordinul le arată „Eliminat(ă)” / „Abrogat(ă)” (587: 21, 52–56, 64, 73, 78, 80); codurile din
structură fără poziție în ordin (D100: 107 / 127 — „poz.000”, sunt în anexa 3^1, obligațiile scutite; 130 / 161 / 708 / 763 pe poziții
abrogate; 704 / poz.117 — Legea 162/2026, mai nouă decât forma consolidată 15.05.2026 a ordinului; D112: 441 / poz.19, care lipsește din
ordinul 605; 483, 484, 486, 487, 488, 472, 624 — fără „Nr.cr. Mof.”). Niciunul nu e emis de aplicație.
