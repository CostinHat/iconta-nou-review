# INVENTAR A — structura GENERATA din common.COTE + overlay judecati umane

GENERAT de `genereaza_inventar_a.py` (nu edita direct partea de tabel). Structura
(cluster/valoare/temei/data_in/data_out) se regenereaza din cod; judecatile umane
(Risc/Verificat/nota) traiesc in `INVENTAR_A_OVERLAY.tsv` si NU se pierd la regenerare.

| Cluster | Valoare | Temei (structurat) | data_in | data_out | Risc | Verificat la sursă | Notă |
|---|---|---|---|---|---|---|---|
| tva_standard | 0.21 | Legea 141/2025 | 2025-08-01 | — | FISCAL | √ 31.07 | Legea 141/2025 21% standard / 11% redusa de la 01.08.2025; golden test_d394 |
| plafon_mijloc_fix | 5000 | OUG 8/2026 | 2026-01-01 | 2028-01-01 (ESTIMAT) | STRUCTURA | — | OUG 8/2026 prag 5000 |
| plafon_sold_casa | 50000 | Legea 70/2015 | 2015-05-09 | — | STRUCTURA | — | Legea 70/2015 plafon sold casierie |
| plafon_avans_decontare | 5000 | OUG 115/2023 | 2023-12-15 | — | STRUCTURA | — | OUG 115/2023 plafon avans decontare |
| cas | 0.25 | CF art.138 | 2018-01-01 | — | FISCAL | √ 31.07 | CF art.138 25%; cluster concedii medicale (taxe_cm canonic, DUK cod01 valid) |
| cass | 0.10 | CF art.156 | 2018-01-01 | — | FISCAL | √ 31.07 | CF art.156 10% |
| impozit_venit | 0.10 | CF art.78 | 2018-01-01 | — | FISCAL | √ 31.07 | CF art.78 10% |
| cam | 0.0225 | CF art.220^1 | 2018-01-01 | — | FISCAL | √ 31.07 | CF art.220^1 2.25% (angajator) |
| salariu_minim | 4325 | HG 146/2026 | 2026-07-01 | 2026-12-31 (ESTIMAT) | FISCAL | √ 31.07 | HG 146/2026 (4325 S2 2026); HG 1506/2024 corectat 4050 (era 3700, act gresit) |
| facilitate_salariu_minim | 200 | OUG 89/2025 art.III | 2026-07-01 | 2026-12-31 (ESTIMAT) | FISCAL | √ 31.07 | OUG 89/2025 art.III + HG 146/2026; conditii cumulative norma/functie/contractual/plafon |
| plafon_facilitate_salariu_minim | 4600 | OUG 89/2025 art.III lit.b | 2026-07-01 | 2026-12-31 (ESTIMAT) | FISCAL | √ 31.07 | venit brut total: S1 4300 / S2 4600 |
| tichet_masa_plafon | 45 | Legea 201/2025 | 2026-01-01 | 2026-09-30 (ESTIMAT) | FISCAL | PARTIAL 31.07 | fond fiscal verificat (45, imp/CASS, plafon); deschis: D2 nr tichete, D3 exces vacanta |
