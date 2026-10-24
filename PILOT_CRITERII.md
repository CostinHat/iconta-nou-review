# PILOT — criteriile de pornire (comanda Costin 11.2 pct.5, verbatim în DECIZII „Comanda 11.2”)

> „până la pilot nu intră funcții noi, doar reparații. Pilotul pornește când o lună completă de contabil merge cap-coadă pe o firmă fără
> deficiențe grave: facturi, bancă, casă, stoc, salarii, închidere, D300, D394, D112, D100, balanță.”

CLAUDE.md §2 (23.10.2026): „Pilotul are un scenariu automat al lunii complete a firmei-pilot, parcurs pe ecran ca un contabil, cu cifrele
exacte așteptate la fiecare pas, până la declarații. Scenariul crește cu fiecare poziție pilot rezolvată și rulează permanent în poartă.
Pilotul e atins când scenariul e verde de la cap la coadă.” Scenariul: `frontend_test/e2e/e2e_pilot_luna.py` — firma-pilot (SRL de comerț
nou, micro, plătitor de TVA lunar, cu salariați, stoc cantitativ-valoric, preluat din 09/2026, ca F1), luna 09/2026, pașii
`test_pilot_<nn>_<pas>` în ordine, cifrele calculate din lege în antetul fișierului.

## Domeniile (comanda 11.2)

Un domeniu e „probat” când luna completă a trecut prin el pe aceeași firmă, cap-coadă, fără deficiență gravă deschisă; rândul numește
atunci firma, luna și dovada (capturile din `dovezi/`, ca la DEFICIENTE, comanda 11.2 pct.3). Stările: `neprobat` / `în probă` / `probat`.
„În probă” = pașii domeniului sunt în scenariu; „probat” = pașii lui sunt verzi la o rulare a porții. Pilotul pornește numai când toate cele
11 sunt „probat” pe aceeași firmă și aceeași lună — decizia de pornire e a lui Costin. Până atunci, garda `core/test_fara_functii_noi.py`
oprește orice funcție nouă (rută, funcționalitate, trecere în LIVE) care nu repară o deficiență numită. Forma tabelului e păzită de aceeași
gardă (`test_criteriile_pilotului_sunt_cele_11_domenii_cu_stare`).

| # | domeniu | stare | probă (firma: … · luna: … · dovadă: …) |
|---|---|---|---|
| 1 | facturi | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pașii 07 (primite din e-Factura), 10, 14, 16, 17 (emise), 36 (valută, 10/2026), 38 (primită introdusă de mână, 10/2026); firma-pilot sintetică, luna 09/2026 |
| 2 | bancă | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pasul 18 (extrasul, potrivirea, contarea); firma-pilot sintetică, luna 09/2026 |
| 3 | casă | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pașii 11, 15 (dispozițiile, chitanța), 25 (registrul lunii); firma-pilot sintetică, luna 09/2026 |
| 4 | stoc | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pașii 06 (NIR cu transport), 10, 16 (descărcarea la factură), 12, 13 (descărcarea Z-urilor, scris de mână și importat din AMEF); firma-pilot sintetică, luna 09/2026 |
| 5 | salarii | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pașii 19–23 (salariații, statul cu CM, fluturașul, nota, plata pe card), 37 (CM cod 10, 10/2026); firma-pilot sintetică, luna 09/2026 |
| 6 | închidere | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pașii 24 (validarea notelor), 28 (regularizarea TVA, controalele, blocarea); firma-pilot sintetică, luna 09/2026 |
| 7 | D300 | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pasul 30; firma-pilot sintetică, luna 09/2026 |
| 8 | D394 | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pasul 31; firma-pilot sintetică, luna 09/2026 |
| 9 | D112 | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pasul 32; firma-pilot sintetică, luna 09/2026 |
| 10 | D100 | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pasul 34 (cu depunerea); firma-pilot sintetică, luna 09/2026 |
| 11 | balanță | în probă | scenariul `frontend_test/e2e/e2e_pilot_luna.py`, pasul 29; firma-pilot sintetică, luna 09/2026 |

## Pozițiile pilotului în scenariu (comanda 12.1, CLAUDE.md §2)

Cele 43 de poziții „pilot” din `FUNCTIONALITATI.csv` și fereastra de bun venit „Primii pași”: pașii scenariului care le acoperă și starea
fiecărui pas, în ordinea pașilor — „verde” (pasul e în scenariu, fără xfail) sau „xfail (deficiența <nr>)” (pasul e scris, cu cifrele lui,
dar o deficiență deschisă îl oprește azi; `xfail(strict=True)`: când se repară, pică și intră în scenariu). Păzit de
`core/test_lot12_pilot_criterii.py`: pozițiile sunt exact cele din comanda 12.1, numele e cel din registru, pașii scriși = pașii marcați
`@pozitii(...)` în scenariu, starea scrisă = starea declarată a pașilor, iar numărul din xfail e o deficiență deschisă din `DEFICIENTE.md`.

| poziție | funcționalitate | pașii scenariului | stare |
|---|---|---|---|
| F018 | Parteneri (clienți/furnizori) | `test_pilot_08_partenerii_au_localitatea`, `test_pilot_09_lista_partenerilor_cu_soldurile` | verde; verde |
| F023 | Regula cotelor de TVA | `test_pilot_05_nomenclatorul_cu_cota_propusa` | verde |
| F025 | Curs valutar BNR | `test_pilot_36_factura_in_valuta_pe_luna_urmatoare` | verde |
| F045 | PDF factură | `test_pilot_10_factura_cu_descarcarea_stocului` | verde |
| F046 | Contarea facturilor, cu TVA și stornare | `test_pilot_10_factura_cu_descarcarea_stocului`, `test_pilot_16_a_doua_factura_cu_marfa`, `test_pilot_17_factura_de_servicii_neincasata` | verde; verde; verde |
| F070 | Nomenclator produse, cu cota de TVA propusă de AI | `test_pilot_05_nomenclatorul_cu_cota_propusa` | verde |
| F126 | e-Factura SPV complet | `test_pilot_10_factura_cu_descarcarea_stocului` | verde |
| F131 | Notificări de plată și alerte neplătnici | `test_pilot_17_factura_de_servicii_neincasata`, `test_pilot_26_scadentarul`, `test_pilot_27_scadentarul_stie_incasarea_prin_banca` | verde; verde; verde |
| F172 | Descărcarea stocului la emiterea facturii | `test_pilot_10_factura_cu_descarcarea_stocului`, `test_pilot_16_a_doua_factura_cu_marfa` | verde; verde |
| F017 | Chitanțe emise | `test_pilot_11_incasarea_in_casa_cu_chitanta` | verde |
| F003 | Import Raport Z din AMEF | `test_pilot_12_raportul_z_si_descarcarea_lui`, `test_pilot_13_raportul_z_din_fisierul_amef` | verde; verde |
| F252 | Clasificare TVA pe factură | `test_pilot_10_factura_cu_descarcarea_stocului`, `test_pilot_30_d300` | verde; verde |
| F254 | Factură emisă pe baza bonului fiscal | `test_pilot_14_factura_pe_baza_bonului_fiscal`, `test_pilot_31_d394` | verde; verde |
| F043 | Import e-Factura (UBL) | `test_pilot_07_facturile_primite_din_e_factura`, `test_pilot_38_factura_primita_introdusa_manual` | verde; verde |
| F176 | Conectarea la SPV (ANAF) | `test_pilot_07_facturile_primite_din_e_factura` | verde |
| F179 | Cron receive e-Factura (facturi furnizori din SPV) | `test_pilot_07_facturile_primite_din_e_factura` | verde |
| F089 | Stocuri cantitativ-valorice (CMP) | `test_pilot_06_nir_cu_transport`, `test_pilot_12_raportul_z_si_descarcarea_lui` | verde; verde |
| F139 | Costul complet de achiziție pe NIR (transport, vamă) | `test_pilot_06_nir_cu_transport` | verde |
| F011 | Contabilizare extras de cont | `test_pilot_18_extrasul_de_banca_si_potrivirea` | verde |
| F012 | Citirea extrasului bancar | `test_pilot_18_extrasul_de_banca_si_potrivirea` | verde |
| F073 | Reconciliere bancară (potrivirea plăților cu facturile) | `test_pilot_18_extrasul_de_banca_si_potrivirea`, `test_pilot_27_scadentarul_stie_incasarea_prin_banca` | verde; verde |
| F015 | Registrul de casă și plafoanele de numerar | `test_pilot_11_incasarea_in_casa_cu_chitanta`, `test_pilot_15_depunerea_numerarului`, `test_pilot_25_registrul_de_casa` | verde; verde; verde |
| F078 | Salariați (adăugare, modificare, ștergere) | `test_pilot_19_salariatii` | verde |
| F080 | Calcul salarizare (de la brut la net) | `test_pilot_20_statul_de_plata_cu_concediul_medical`, `test_pilot_21_concediul_medical_arata_cas_ul` | verde; verde |
| F087 | Statul de plată și fluturașii | `test_pilot_20_statul_de_plata_cu_concediul_medical`, `test_pilot_22_contabilizarea_statului_si_fluturasul` | verde; verde |
| F122 | Cod 10 CM în flux | `test_pilot_37_concediul_cod_10_pe_luna_urmatoare` | verde |
| F134 | Plata salariilor pe card (fișier bancar) | `test_pilot_23_plata_salariilor_pe_card` | verde |
| F019 | Coada de validare patru-ochi | `test_pilot_24_notele_lunii_validate`, `test_pilot_30_d300` | verde; verde |
| F054 | Editor note contabile | `test_pilot_24_notele_lunii_validate`, `test_pilot_28_inchiderea_lunii` | verde; verde |
| F061 | Cartea mare și închiderea perioadei | `test_pilot_28_inchiderea_lunii`, `test_pilot_29_balanta` | verde; verde |
| F118 | Blocare perioade | `test_pilot_28_inchiderea_lunii`, `test_pilot_39_deblocarea_lunii_cu_motiv` | verde; verde |
| F022 | Semafor conformare fiscală | `test_pilot_35_controlul_fiscal_si_incrucisat` | verde |
| F081 | Calculul scadențelor | `test_pilot_35_controlul_fiscal_si_incrucisat` | verde |
| F162 | Control încrucișat: D112 (salarii) față de contabilitate | `test_pilot_32_d112`, `test_pilot_35_controlul_fiscal_si_incrucisat` | verde; verde |
| F169 | Control încrucișat: declarația de TVA față de contabilitate | `test_pilot_30_d300`, `test_pilot_35_controlul_fiscal_si_incrucisat` | verde; verde |
| F026 | Declarația D100 | `test_pilot_34_d100` | verde |
| F028 | Declarația D112 | `test_pilot_32_d112` | verde |
| F031 | Declarația D300 | `test_pilot_30_d300` | verde |
| F034 | Declarația D394 | `test_pilot_31_d394` | verde |
| F035 | Declarația D406 (SAF-T) | `test_pilot_33_d406` | verde |
| F084 | Import solduri inițiale (migrare) | `test_pilot_01_preluarea_luna_si_balanta_de_deschidere` | verde |
| F085 | Import solduri parteneri (migrare) | `test_pilot_02_soldurile_pe_parteneri`, `test_pilot_04_soldul_preluat_e_document_deschis` | verde; verde |
| F183 | Audit de preluare a firmei | `test_pilot_03_auditul_de_preluare` | verde |
| PRIMII_PASI | Fereastra de bun venit „Primii pași” | `test_pilot_00_primii_pasi` | verde |
