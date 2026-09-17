# INVENTAR A — structura GENERATA din common.COTE + overlay judecati umane

GENERAT de `genereaza_inventar_a.py` (nu edita direct partea de tabel). Structura
(cluster/valoare/temei/data_in/data_out) se regenereaza din cod; judecatile umane
(Risc/Verificat/nota) traiesc in `INVENTAR_A_OVERLAY.tsv` si NU se pierd la regenerare.

| Cluster | Valoare | Temei (structurat) | data_in | data_out | Risc | Verificat la sursă | Notă |
|---|---|---|---|---|---|---|---|
| tva_standard | 0.21 | Legea 141/2025 art.291 alin.(1) | 2025-08-01 | — | FISCAL | √ 31.07 | Legea 141/2025 21% standard / 11% redusa de la 01.08.2025; golden test_d394 |
| tva_redusa | 0.11 | Legea 141/2025 art.291 alin.(2) | 2025-08-01 | — | — | — |  |
| tva_redusa_9 | 0.11 | Legea 141/2025 art.291 alin.(2) | 2025-08-01 | — | — | — |  |
| tva_redusa_5 | 0.11 | Legea 141/2025 art.291 alin.(3) | 2025-08-01 | — | — | — |  |
| impozit_dividend | 0.16 | Legea 141/2025 art.97 alin.(7) | 2026-01-01 | — | — | — |  |
| plafon_tva_incasare | 5500000 | OUG 8/2026 art.282 alin.(3) lit.b | 2027-01-01 | — | — | — |  |
| plafon_mijloc_fix | 5000 | OUG 8/2026 art.28 alin.(2) lit.b | 2026-02-25 | — | STRUCTURA | — | OUG 8/2026 prag 5000 |
| plafon_intrastat | 1000000 | Ordin 1604/2025 art.1 | 2026-01-01 | — | — | — |  |
| plafon_sold_casa | 50000 | Legea 70/2015 | 2015-05-09 | — | STRUCTURA | — | Legea 70/2015 plafon sold casierie |
| plafon_avans_decontare | 5000 | OUG 115/2023 | 2023-12-15 | — | STRUCTURA | — | OUG 115/2023 plafon avans decontare |
| impozit_micro | 0.01 | CF art.51 alin.(1) | 2023-01-01 | — | — | — |  |
| impozit_profit | 0.16 | CF art.17 | 2018-01-01 | — | — | — |  |
| cas | 0.25 | CF art.138 | 2018-01-01 | — | FISCAL | √ 31.07 | CF art.138 25%; cluster concedii medicale (taxe_cm canonic, DUK cod01 valid) |
| cass | 0.10 | CF art.156 | 2018-01-01 | — | FISCAL | √ 31.07 | CF art.156 10% |
| impozit_venit | 0.10 | CF art.78 | 2018-01-01 | — | FISCAL | √ 31.07 | CF art.78 10% |
| cam | 0.0225 | CF art.220^3 alin.(1) | 2018-01-01 | — | FISCAL | √ 31.07 | CF art.220^1 2.25% (angajator) |
| salariu_minim | 4325 | HG 146/2026 | 2026-07-01 | — | FISCAL | √ 31.07 | HG 146/2026 (4325 S2 2026); HG 1506/2024 corectat 4050 (era 3700, act gresit) |
| facilitate_salariu_minim | 200 | OUG 89/2025 art.III | 2026-07-01 | — | FISCAL | √ 31.07 | OUG 89/2025 art.III + HG 146/2026; conditii cumulative norma/functie/contractual/plafon |
| plafon_facilitate_salariu_minim | 4600 | OUG 89/2025 art.III alin.(1) lit.b | 2026-07-01 | — | FISCAL | √ 31.07 | venit brut total: S1 4300 / S2 4600 |
| tichet_masa_plafon | 45 | Legea 201/2025 art.I | 2025-11-01 | — | FISCAL | PARTIAL 31.07 | fond fiscal verificat (45, imp/CASS, plafon); deschis: D2 nr tichete, D3 exces vacanta |

## Reguli-algoritm cu temei la nivel de functie (NU cote - proposal point 2)

| Modul | Functie | Temei |
|---|---|---|
| contracte_speciale.py | calcul_zilier | Legea 52/2011 art.9^1 (zilieri: impozit 10% + CAS 25%, fara CASS/CAM); impozit pe (brut-CAS). |
| d100.py | _rata_impozit_default | CF art.51 (micro), art.17 (profit). nivel_sursa: REDARE. |
| d101.py | datoreaza_imca | CF art.18^1 alin.(1). |
| d101.py | impozit_minim_cifra_afaceri | CF art.18^1 alin.(3)-(4). VERDE (verbatim anaf_surse/). |
| d101.py | genereaza | CF art.18^1 alin.(1). |
| d112.py | pull | OUG 156/2024 art.LXVI alin.(5) = OUG 89/2025 art.III — derogarea „NIVELUL ... SE DIMINUEAZA |
| d402.py | calcul_d402 | `anaf_surse/structuraXML_D402_2022.pdf` — verbatim, *"totalPlata_A = Σ (beneficiar.venit.Suma_venit)"*, cu eroarea numita tot acolo: *"ERR – camp totalPlata_A calculat gresit"*. |
| deconturi.py | plafon_diurna | CF art.76(2) lit.k + alin.(4^1) (plafon = min 2.5x diurna bugetara; 3x salariu/zile lucratoare); |
| motor.py | rezerva_legala | Legea 31/1990 art.183 (rezerva legala 5% profit / plafon 20% capital social); OMFP 1802/2014 |
| salarizare.py | _deducere_personala_2018 | CF art.77 alin.(4) (scara degresiva 20/25/30/35/45%, prag salariu minim+2000) + alin.(10) lit.a (deducere 100 lei/copil scolarizat). nivel_sursa: REDARE (scara 45% pt 4+ din redare secundara noulcodfiscal, nu MO). |
| salarizare.py | deducere_personala | CF art.77 alin.(4) (scara degresiva 20/25/30/35/45%, prag salariu minim+2000) + alin.(10) lit.a |
| salarizare.py | _calcul_salariu_2018 | CF art.77 (deducere personala), art.146 alin.(5^6)/(5^7) (contributia minima / exceptari |
| salarizare.py | _pd | pragul (alin.5) se prorateaza prin INTERPRETARE; facilitatea (alin.4 lit.b) prin |
| salarizare.py | calcul_salariu | CF art.77 (deducere personala), art.146 alin.(5^6)/(5^7) (contributia minima / exceptari |
| salarizare.py | _procent_cm_l141_2025 | OUG 158/2005 art.17(1) (progresiv 55/65/75, forma Legea 141/2025); art.20(3) + Legea 136/2020 (carantina 07=100%); art.25(1) (maternitate 08=85%); art.30(1) (ingrijire copil 09=85%). nivel_sursa: REDARE (OUG 158/2005 citita, verbatim necapturat). |
| salarizare.py | procent_cm | OUG 158/2005 art.17(1) (progresiv 55/65/75, forma Legea 141/2025); art.20(3)+Legea 136/2020 |
| salarizare.py | _calcul_cm_cod10_2018 | OUG 158/2005 art.19 (reducere timp munca cod 10; plafon 25% din baza de calcul). nivel_sursa: REDARE. |
| salarizare.py | calcul_cm_cod10 | OUG 158/2005 art.19 (reducere timp munca cod 10; plafon 25% din baza de calcul). nivel_sursa: |
| salarizare.py | _calcul_cm_core | OUG 158/2005 (indemnizatie CM: Ci = Mzbci x procent x zile); Ordinul 506/1030/2026 |
| salarizare.py | calcul_cm | OUG 158/2005 (indemnizatie CM: Ci = Mzbci x procent x zile); Ordinul 506/1030/2026 (MOF |
| salarizare.py | _taxe_cm_2018 | CF art.139(1)(o)+140 (CAS 25% pe indemnizatie); art.155(1) lit.i (CASS 10% cod 01/07/10); art.78 (impozit 10%). nivel_sursa: INTERPRETARE_OFICIALA (CAS 25% pe maternitate/copil = ghid ANAF, nu litera actului). |
| salarizare.py | taxe_cm | CF art.139(1)(o)+140 (CAS 25% pe indemnizatie); art.155(1) lit.i (CASS 10% cod 01/07/10); |
| sponsorizari.py | plafon_credit | CF art.25 alin.(4) lit.i (credit = min 0,75% cifra afaceri; 20% impozit profit). nivel_sursa: |
| sponsorizari.py | credit_sponsorizare | CF art.25 alin.(4) lit.i (credit sponsorizare); OUG 115/2023 (micro: facilitate eliminata); |
| stat_plata_api.py | randuri_deducere | CF art.77 alin.(2) deducerea personala de baza; alin.(4^1) suplimentara pentru tineri sub |
| tva_marja.py | vanzare_marja | CF art.312 (regim special marja bunuri second-hand; norme pct.86). nivel_sursa: REDARE. |
| tva_marja_turism.py | marja_turism_special | CF art.311 (regim special agentii turism; alin.5 scutire non-UE; alin.2-4 |
