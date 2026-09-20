# Așteptări F1 — ETAPA 4 (salarizare) — scris ÎNAINTE de a rula

**Context:** F1 = 3 salariați (etapa 1), salariu în `salariu_istoric` (2026-01-01). `salariati.salariu_brut = 0`
pe rând — **baza contractuală trebuie citită din istoric, NU din coloana 0** (DS v2.33; `stat_plata_api.py:47-54`
folosește `salariu_istoric.salariu_la`, nu `salariati.salariu_brut` — [tranzitie 29.07.2026]). VERIFICAT: baza
citită corect din istoric, baza_lipsa=False.

**CAPCANĂ (regula bazei nule):** dacă statul de plată ar citi `salariati.salariu_brut` = 0, baza ar fi
0 → stat gol/greșit. Invariantul etapei: fiecare salariat cu bază = salariul din istoric, NU 0.

**CORECȚIE DE DATE DE TEST (20.09):** salariile inițiale (4.000/4.500/4.000) aveau 2 sub **salariul minim
2026 = 4.325 lei (HG 146/2026)** — ilegal pentru full-time. Gardul `ReconciliereD112` (a doua cale) a
REFUZAT corect contarea ("brut 4000 SUB salariul minim 4325 ... date probabil corupte"). Test-data, nu bug.
Corectate la **4.500 / 5.000 / 4.400** (toate ≥ 4.325).

## Valori așteptate (sursă de adevăr: `core.salarizare.calcul_salariu`, la_data 2026-09-01)

| salariat | brut (istoric) | CAS 25% | CASS 10% | impozit | NET | CAM 2.25% |
|---|---|---|---|---|---|---|
| Ionescu Ion | 4.500 | 1.125 | 450 | 214,65→**215** | **2.710,35** | 101,25 |
| Popescu Maria | 5.000 | 1.250 | 500 | 268,78→**269** | **2.981,23** | 112,50 |
| Georgescu Ilie | 4.400 | 1.100 | 440 | 203,83→**204** | **2.656,18** | 99,00 |

**Notă contabilă stat (verificat DB, sursa='salarii'):**
- **641 = 421: 13.900** (cheltuială salarii = brut total 4.500+5.000+4.400)
- **421 = 4315: 3.475** (CAS reținut) · **421 = 4316: 1.390** (CASS reținut) · **421 = 444: 688** (impozit reținut, rotunjit per salariat 215+269+204)
- **646 = 436: 313** (CAM angajator 2,25%, rotunjit)

Impozit = 10% × (brut − CAS − CASS − deducere personală), rotunjit aritmetic per salariat (ROUND_HALF_UP).

## Invarianți verificabili în DB după etapa 4 (tenant_049)
| ce | valoare așteptată |
|---|---|
| nr. linii stat de plată | **3** (câte un salariat) |
| bază fiecare linie | **4.500 / 5.000 / 4.400** (din istoric, NU 0) |
| NET fiecare linie | 2.710,35 / 2.981,23 / 2.656,18 |
| nota 641=421 (brut total) | **13.900** |
| impozit reținut total (421=444) | **688** |
| CAM (646=436) | **313** |

**Temei fiscal:** cotele (CAS 25% CF art.138, CASS 10% CF art.156, impozit 10% CF art.64, CAM 2.25% CF art.220^3)
+ salariul minim 2026 + deducerea personală (CF art.77 alin.(2)) — TOATE din `core.contributii`/`salarizare`, NU
din memorie. Valorile din tabel sunt PRODUSE de `salarizare.calcul_salariu`, nu presupuse.

**OBS (pentru D112, etapă ulterioară):** `salariati.cor` = gol pe toți 3 — COR e obligatoriu la D112.
De completat înainte de testarea D112. Nu blochează statul de plată.
