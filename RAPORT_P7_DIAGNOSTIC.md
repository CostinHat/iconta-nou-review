# P7 — DIAGNOSTIC. Nicio reparație.

**Instantaneu datat, nu registru viu.** Măsurat prima oară pe `f260df2e` (12.09.2026), **rescris
după valul V3** pe `b67d2bfb` (13.09.2026). Se reproduce cu:

```
./venv/bin/python core/straturi.py                     # registrul straturilor
./venv/bin/python scripts/scan_p7_straturi.py          # universurile și itemii
./venv/bin/python scripts/p7_clasificare.py --itemi    # clasificarea, item cu item
./venv/bin/python -m pytest -q core/test_p7_clasificare.py core/test_p7_straturi.py
```

*Cifrele de mai jos NU se citesc ca stare curentă: se recalculează. Un raport de diagnostic e
fotografia zilei, iar instrumentul e cel care rămâne adevărat.*

---

## 1. DEFINIȚIA CANONICĂ, cu file:line

**`PLAN_HARDENING.md:733-755`** — singura sursă normativă a fazei P7.

- **`733`** — titlul: *„P7 — APPLICATION LAYER"*.
- **`735-736`** — ce trebuie făcut: *„Separarea **HTTP → use-case → motor fiscal → repository**. Azi
  ruta face adesea toate patru: citește cererea, decide, calculează și scrie."*
- **`738-740`** — criteriul: *„separarea responsabilităților, NU numărul de linii din `main.py`"*.
- **`742-746`** — cele patru straturi și ce are voie fiecare.
- **`748-751`** — **cum se verifică, mecanic**: *„un motor fiscal nu importă `db`; un use-case nu
  construiește `HTTPException`; ruta nu conține SQL."*
- **`752-755`** — testele rutelor rămân verzi **fără să fie rescrise**; se măsoară ce s-a mutat.

### Omonimia lui „P7"

`grep -n "P7"` peste registre întoarce **patru** lucruri diferite: faza (`PLAN_HARDENING.md:733`) ·
principiul „verificarea e independentă" (`PLAN_ARHITECTURA.md:279`) · rândul P7 din D101
(`DECIZII.md:6434`, `TESTE.md:495`) · clasa P7 din catalogul C-5 (`TESTE.md:167`). Nu e contradicție
— cele două planuri vorbesc despre lucruri disjuncte. **`P7_NORMATIVE_CONFLICT=NO`.**

---

## 2. CE NU E P7

- **`R69_IN_P7_SCOPE=NO`** — e o verificare business care lipsește; nu atinge niciunul dintre cele
  trei criterii mecanice.
- **`OPERATIONAL_CONSTANT_TAXONOMY_IN_P7_SCOPE=NO`** — e despre citarea temeiului unei valori, nu
  despre stratul în care trăiește.

---

## 3. VALUL V3 — REGISTRUL STRATURILOR *(13.09.2026)*

**Ce era de reparat.** Prima formă a diagnosticului a măsurat *„un motor fiscal nu importă `db`"* și
a găsit **zero** — dar pe un univers derivat din DOUĂ instrumente care nu cădeau de acord
(generatoarele celor nouă declarații: 25 de module; modulele care poartă valori fiscale: 104). Șapte
module cădeau între ele, iar pentru ele întrebarea nu se putea decide: `EVIDENCE_LIMITATION`.
*Un criteriu al cărui univers nu e definit nu e o măsurătoare, e o aproximare.*

**Ce s-a construit.** `core/straturi.py` — **o singură sursă autoritativă**, scrisă, nu regenerată:
`MODULE → STRAT`, cu `motiv` (faptul mecanic măsurat la declarare) și `regula` (linia canonică) pe
fiecare rând. Detectorul D2 **o consumă**; nu mai are nicio definiție proprie.

| | |
|---|---|
| **`LAYER_REGISTRY_UNIVERSE`** | reuniunea celor două definiții candidate de „fiscal" cu modulele care poartă rute, fără instrumentele de măsură și fără probe — **114 module**, derivată din repo la fiecare rulare |
| **`LAYER_REGISTRY_ENTRY_DEFINITION`** | `D(cale, strat, mixt_cu, motiv, regula)`; `strat` ∈ {HTTP, USE_CASE, FISCAL_ENGINE, REPOSITORY} |
| **`LAYER_REGISTRY_EXCLUSIONS`** | `core/scan_*` (instrumente de măsură), `core/test_*` (probe), `scripts/*`, `_arhiva_*`, `frontend_test/*` |

```
MODULE_DECLARATE=114     HTTP=2   USE_CASE=2   FISCAL_ENGINE=96   REPOSITORY=14
UNDECLARED_RELEVANT_MODULES=0     MULTI_LAYER_MODULES=0     UNKNOWN_LAYER_MODULES=0
MIXED_LAYER_MODULES=38
```

**Cele 29 de module unde faptele mecanice nu ajungeau** poartă `regula = „citit la sursa"`: le-am
citit docstringul și ce fac, și am decis. Restul de 85 urmează o regulă declarată, cu evidența
mecanică scrisă lângă fiecare (câte rute, câte instrucțiuni SQL, dacă e generator de declarație).

**`mixt_cu` nu e un al cincilea strat.** 38 de module fac azi două lucruri deodată — un motor fiscal
care își citește singur datele, o rută care scrie SQL. Comanda V3 cere să nu inventez o clasificare:
`strat` rămâne responsabilitatea principală (una singură), iar `mixt_cu` numește al doilea strat
atins. Fiecare e `ACTION_REQUIRED` pentru valul care separă.

### Cele șapte, rezolvate

| MODULE | DECLARED_LAYER | IMPORTS_CORE_DB | D2_CLASSIFICATION |
|---|---|---|---|
| `core/curs_bnr.py` | REPOSITORY | YES | **FALSE_POSITIVE** — aduce și păstrează cursuri; nu aplică o regulă fiscală |
| `core/efactura_send.py` | **FISCAL_ENGINE** | **YES** | **ACTION_REQUIRED** — generator de document normat care își deschide singur conexiunea |
| `core/firma_rezumat.py` | REPOSITORY | YES | **FALSE_POSITIVE** — model de citire (P2) |
| `core/monitor_fiscal.py` | USE_CASE | YES | **FALSE_POSITIVE** — cron care orchestrează, nu calculează obligații |
| `core/notificari_scadenta.py` | USE_CASE | YES | **FALSE_POSITIVE** — orchestrează un efect extern |
| `core/stare_partajata.py` | REPOSITORY | YES | **FALSE_POSITIVE** — starea scoasă din memoria procesului (P6 valul 1) |
| `core/stat_plata_emis.py` | REPOSITORY | YES | **FALSE_POSITIVE** — păstrează documentul emis |

**Registrul NU a fost folosit ca să le facă pe toate să dispară**: șase ies din D2 fiindcă nu sunt
motoare fiscale, dar al șaptelea **rămâne** motor fiscal și importă `db` — deci e o încălcare
adevărată, și a devenit **singurul item D2 al repo-ului**. `D2_EVIDENCE_LIMITATIONS=0`.

*Și o observație care nu se repară aici:* `core/efactura_send.py` își spune în docstring „generator
PUR de XML", dar are `db.get_conn()` în trei locuri (l. 469, 485, 523); la fel, `core/scadentar.py`
spune „Calcul PUR, fara DB" și are cinci instrucțiuni SQL. Proza descrie miezul, nu modulul — clasa
**R16**. Consemnat în registru, lăsat pentru valul potrivit.

---

## 4. CE A GĂSIT DIAGNOSTICUL, după V3

| detector | univers | itemi | clasă |
|---|---|---|---|
| **D1 — SQL în rută** | 424 rute | **257** | `ACTION_REQUIRED` (toate) — 139 din 424 de rute execută SQL în corpul lor: 91 SELECT · 100 INSERT · 28 UPDATE · 5 DELETE · 33 pe mai multe linii |
| **D2 — motor fiscal cu `db`** | **96 module declarate** | **1** | `ACTION_REQUIRED` — `core/efactura_send.py:368` |
| **D3 — HTTP sub stratul HTTP** | 324 module `core/` | **1** | `ACCEPTABLE_BY_DESIGN` — `core/spv_rute.py:42`, într-un modul care conține rute |
| **D4 — strat mixt** | 114 module declarate | **38** | `ACTION_REQUIRED` — poziții pentru valul care separă |

---

## 5. FELUL DOVEZII

| clasă | ce acoperă |
|---|---|
| **STATIC_EVIDENCE** | toate cele 297 de poziții — cele trei criterii canonice sunt proprietăți structurale |
| **SYNTHETIC_EVIDENCE** | calibrările detectoarelor și ale registrului (fragmente scrise de mână) |
| **REAL_PATH_EVIDENCE** | universurile derivate din repo; itemii cunoscuți pinați în probe |
| **PRODUCTION_EVIDENCE** | **niciuna, și nu e nevoie de niciuna** — nimic din P7 nu depinde de numărul de procese, de concurență sau de o cădere |

---

## 6. CONTRACTE CARE NU SE REDESCHID

Măsurat: **139 din 139** de rute cu SQL își deschid singure conexiunea. Azi **ruta deține
tranzacția**. `P4_TRANSACTION_OWNERSHIP_CHANGED=NO` — V3 n-a atins asta.

| contract | atins de reparația viitoare? | constrângerea de păstrat |
|---|---|---|
| **P4 — tranzacția** | **DA** | tranzacția urcă de la rută la **USE_CASE**; repository-ul NU-și creează tranzacție proprie dacă asta ar rupe atomicitatea |
| **P5 — I/O extern** | NU | nicio poziție P7 nu mută un apel extern |
| **P6 — starea procesului** | NU | nicio poziție P7 nu introduce stare în memoria procesului |

---

## 7. VALURI

**V3 — registrul de straturi: FĂCUT** (13.09.2026). Univers 114, zero nedeclarate, zero ambiguități,
`EVIDENCE_LIMITATION` 7 → 0.

**V1 — repository pentru citiri** · 91 de poziții SELECT · risc mic · gardă cu clichet descrescător ·
testele rutelor rămân verzi **nerescrise** · fără exercițiu de producție.

**V2 — repository pentru scrieri** · 133 de poziții (100 INSERT · 28 UPDATE · 5 DELETE) · risc mare
(atomicitate) · în plus: probă că fiecare scriere rămâne în aceeași tranzacție · fără exercițiu de
producție.

**V4 — separarea modulelor mixte** · 38 de module + `core/efactura_send.py` (singura încălcare D2) ·
risc mediu · se face după V1/V2, fiindcă multe amestecuri dispar odată cu mutarea SQL-ului.

---

## 8. PLANUL DE ACCEPTANȚĂ

| criteriu | baseline | țintă | măsurare | gardă |
|---|---|---|---|---|
| `751` — ruta nu conține SQL | **257** / 139 rute | **0** | `d1_sql_in_ruta()` | clichet descrescător |
| `749` — motorul fiscal nu importă `db` | **1** | **0** | `d2_motor_fiscal_cu_db()` | gardă + registru |
| `750` — use-case fără `HTTPException` | **0** | rămâne 0 | `d3_http_sub_http()` | gardă anti-regresie |
| straturi declarate | **114 / 114** | rămâne exhaustiv | `univers_registru()` vs registru | `core/test_p7_straturi.py` |
| module mixte | **38** | **0** | `straturi.mixte()` | clichet descrescător |
| `752-753` — testele rutelor verzi **nerescrise** | 5652 verzi | idem, fără rescrieri | diff-ul probelor | poarta completă |

---

## 9. CONTABILITATEA

```
P7_SCANNED_ITEMS           325      (main.py + 324 module core/)
P7_EXCLUDED_ITEMS          604      (fiecare sub o regulă scrisă)
P7_RAW_ITEMS               297
P7_CLASSIFIED_ITEMS        297
P7_ACTION_REQUIRED         296      (D1 257 + D4 38 + D2 1)
P7_ACCEPTABLE_BY_DESIGN      1
P7_FALSE_POSITIVES           0
P7_EVIDENCE_LIMITATIONS      0
P7_UNCLASSIFIED_ITEMS        0
P7_UNEXPLAINED_EXCLUSIONS    0

pe detector:  D1 = 257  ·  D2 = 1  ·  D3 = 1  ·  D4 = 38
universuri :  424 rute  ·  324 module core/  ·  96 module FISCAL_ENGINE  ·  114 în registru
```

Egalitatea se verifică mecanic: `core/test_p7_clasificare.py::test_contabilitatea_se_inchide` și
`core/test_p7_straturi.py::test_contabilitatea_P7_se_inchide_dupa_V3`.

**Cele 257 `D1_SQL_IN_RUTA`** împart același contract, aceeași dovadă și același motiv (temei
`PLAN_HARDENING.md:751`) — câmpurile comune sunt scrise o dată, la clasă; fiecare poziție își are
rândul ei mai jos.

---

## 10. ITEMII, generați

*Blocul de mai jos e produs de `./venv/bin/python scripts/p7_clasificare.py --itemi`. Nu se
editează de mână.*

```
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:820  cur.execute  <- admin_sanatate_istoric (app.get:814)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:879  cur.execute  <- admin_sanatate (app.get:830)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:881  cur.execute  <- admin_sanatate (app.get:830)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:892  cur.execute  <- admin_sanatate (app.get:830)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:941  cur.execute  <- admin_anunt_creeaza (app.post:932)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:944  cur.execute  <- admin_anunt_creeaza (app.post:932)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:947  cur.execute  <- admin_anunt_creeaza (app.post:932)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:949  cur.execute  <- admin_anunt_creeaza (app.post:932)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:957  cur.execute  <- admin_alerte_fiscale (app.get:955)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:966  cur.execute  <- admin_alerta_tratata (app.post:964)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:976  cur.execute  <- eu_anunturi (app.get:973)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:986  cur.execute  <- eu_anunt_confirma (app.post:984)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1000  cur.execute  <- admin_activitate_cabinete (app.get:995)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1030  cur.execute  <- admin_cabinet_suspenda (app.post:1025)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1039  cur.execute  <- admin_cabinet_reactiveaza (app.post:1034)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1055  cur.execute  <- admin_activitate_cabinet (app.get:1043)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1060  cur.execute  <- admin_activitate_cabinet (app.get:1043)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1124  _cur.execute  <- gdpr_export_cabinet (app.get:1102)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1501  cur.execute  <- login (app.post:1487)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1539  cur.execute  <- register (app.post:1510)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1660  cur.execute  <- firme_scoase (app.get:1652)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1828  cur.execute  <- client_acces_lista (app.get:1823)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1847  cur.execute  <- client_acces_creeaza (app.post:1834)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1857  cur.execute  <- client_acces_creeaza (app.post:1834)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1859  cur.execute  <- client_acces_creeaza (app.post:1834)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1862  cur.execute  <- client_acces_creeaza (app.post:1834)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:1866  cur.execute  <- client_acces_creeaza (app.post:1834)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2023  cur.execute  <- reset_parola_cere (app.post:1999)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2042  cur.execute  <- reset_parola_seteaza (app.post:2030)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2056  cur.execute  <- magic_link_cere (app.post:2049)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2089  cur.execute  <- magic_login (app.post:2084)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2094  cur.execute  <- magic_login (app.post:2084)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2108  cur.execute  <- activare_cont (app.post:2103)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2113  cur.execute  <- activare_cont (app.post:2103)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2115  cur.execute  <- activare_cont (app.post:2103)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2124  cur.execute  <- client_acces_revoca (app.delete:2119)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2141  cur.execute  <- acces_portal_preview (app.post:2133)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2148  cur.execute  <- acces_portal_preview (app.post:2133)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2252  cur.execute  <- migrare_importa (app.post:2243)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2385  cur.execute  <- tenant_plan_conturi_lista (app.get:2380)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2390  cur.execute  <- tenant_plan_conturi_lista (app.get:2380)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2430  cur.execute  <- tenant_plan_conturi_adauga (app.post:2408)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:2436  cur.execute  <- tenant_plan_conturi_adauga (app.post:2408)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:3175  cur.execute  <- control_fiscal_audit_preluare (app.post:3164)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:3562  cur.execute  <- firma_profil_regim_tva (app.post:3557)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:3572  cur.execute  <- firma_profil_regim_tva (app.post:3557)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:3824  cur.execute  <- vector_salveaza (app.post:3819)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:3912  cur.execute  <- proforma_transforma (app.post:3903)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:3932  cur.execute  <- proforma_transforma (app.post:3903)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4007  cur.execute  <- client_actualizeaza (app.put:3999)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4071  cur.execute  <- salariat_actualizeaza (app.put:4058)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4130  cur.execute  <- cm_lista (app.get:4121)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4143  cur.execute  <- cm_salveaza (app.post:4137)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4303  cur.execute  <- coada_continut (app.get:4295)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4437  _cur.execute  <- coada_depune (app.post:4382)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4444  _cur.execute  <- coada_depune (app.post:4382)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4447  _cur.execute  <- coada_depune (app.post:4382)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4644  cur.execute  <- declaratii_tipuri (app.get:4636)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4803  cur.execute  <- portal_acces_cont (app.get:4798)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4820  cur.execute  <- portal_acces_cont (app.get:4798)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4888  cur.execute  <- portal_confirma_email (app.post:4877)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4896  cur.execute  <- portal_confirma_email (app.post:4877)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4898  cur.execute  <- portal_confirma_email (app.post:4877)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4913  cur.execute  <- cabinet_urme_portal (app.get:4907)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4934  cur.execute  <- portal_schimba_email (app.put:4920)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4940  cur.execute  <- portal_schimba_email (app.put:4920)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4942  cur.execute  <- portal_schimba_email (app.put:4920)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4975  cur.execute  <- portal_adauga_acces (app.post:4965)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4977  cur.execute  <- portal_adauga_acces (app.post:4965)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4986  cur.execute  <- portal_adauga_acces (app.post:4965)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4987  cur.execute  <- portal_adauga_acces (app.post:4965)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4989  cur.execute  <- portal_adauga_acces (app.post:4965)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:4993  cur.execute  <- portal_adauga_acces (app.post:4965)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5016  cur.execute  <- portal_revoca_acces (app.delete:5007)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5017  cur.execute  <- portal_revoca_acces (app.delete:5007)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5019  cur.execute  <- portal_revoca_acces (app.delete:5007)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5051  cur.execute  <- bonuri_de_verificat (app.get:5045)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5088  cur.execute  <- bon_aproba (app.post:5081)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5101  cur.execute  <- bon_aproba (app.post:5081)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5112  cur.execute  <- bon_aproba (app.post:5081)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5107  cur.execute  <- bon_aproba (app.post:5081)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5110  cur.execute  <- bon_aproba (app.post:5081)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5142  cur.execute  <- salarii_contare_propunere (app.post:5129)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5169  cur.execute  <- salarii_contare_scrie (app.post:5153)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5176  cur.execute  <- salarii_contare_scrie (app.post:5153)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5182  cur.execute  <- salarii_contare_scrie (app.post:5153)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5209  cur.execute  <- tenant_amortizare (app.post:5195)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5215  cur.execute  <- tenant_amortizare (app.post:5195)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5238  cur.execute  <- tenant_amortizare (app.post:5195)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5244  cur.execute  <- tenant_amortizare (app.post:5195)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5371  cur.execute  <- perioade_blocate_lista (app.get:5365)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5456  cur.execute  <- perioada_blocheaza (app.post:5418)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5482  cur.execute  <- perioada_deblocheaza (app.delete:5468)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5521  cur.execute  <- tenant_jurnal (app.get:5502)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5627  cur.execute  <- horeca_import_amef (app.post:5596)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5628  cur.execute  <- horeca_import_amef (app.post:5596)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5634  cur.execute  <- horeca_import_amef (app.post:5596)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5646  cur.execute  <- horeca_import_amef (app.post:5596)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5636  cur.execute  <- horeca_import_amef (app.post:5596)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5686  cur.execute  <- horeca_raport_z (app.post:5661)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5698  cur.execute  <- horeca_raport_z (app.post:5661)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5757  _rc.execute  <- tenant_stat_plata (app.get:5736)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5771  cur.execute  <- tenant_fluturas (app.get:5762)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5876  cur.execute  <- tenant_plata_salarii_preview (app.get:5869)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:5902  cur.execute  <- tenant_plata_salarii_fisier (app.post:5889)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6049  _cur_per.execute  <- d300_manual_sterge (app.delete:6042)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6378  cur.execute  <- portal_bon (app.post:6317)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6389  cur.execute  <- portal_bon (app.post:6317)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6416  cur.execute  <- portal_bon_confirma (app.post:6412)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6427  cur.execute  <- portal_bon_sterge (app.delete:6422)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6466  cur.execute  <- bon_facturi_candidate (app.get:6458)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6472  cur.execute  <- bon_facturi_candidate (app.get:6458)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6507  cur.execute  <- chitanta_stinge (app.post:6496)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6521  cur.execute  <- chitanta_stinge (app.post:6496)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6527  cur.execute  <- chitanta_stinge (app.post:6496)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6564  cur.execute  <- chitanta_emite (app.post:6539)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6567  cur.execute  <- chitanta_emite (app.post:6539)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6575  cur.execute  <- chitanta_emite (app.post:6539)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6552  cur.execute  <- chitanta_emite (app.post:6539)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6583  cur.execute  <- chitanta_emite (app.post:6539)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6592  cur.execute  <- chitante_lista (app.get:6588)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6594  cur.execute  <- chitante_lista (app.get:6588)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6606  cur.execute  <- chitanta_pdf (app.get:6601)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6610  cur.execute  <- chitanta_pdf (app.get:6601)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:6915  cur.execute  <- apiv1_firme (app.get:6913)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7080  cur.execute  <- wc_config_get (app.get:7075)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7114  cur.execute  <- wc_config (app.put:7089)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7131  cur.execute  <- cabinet_consolidare (app.get:7122)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7177  cur.execute  <- portal_cashflow (app.get:7166)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7294  cur.execute  <- portal_solicitari_contor (app.get:7290)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7305  cur.execute  <- portal_solicitari_lista (app.get:7301)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7316  cur.execute  <- portal_solicitari_trimite (app.post:7312)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7320  cur.execute  <- portal_solicitari_trimite (app.post:7312)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7324  cur.execute  <- portal_solicitari_trimite (app.post:7312)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7337  cur.execute  <- cabinet_solicitari_lista (app.get:7333)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7351  cur.execute  <- cabinet_solicitari_raspunde (app.post:7345)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7445  cur.execute  <- asistent_creeaza (app.post:7437)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7448  cur.execute  <- asistent_creeaza (app.post:7437)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7703  cur.execute  <- eu_schimba_parola (app.post:7698)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:7970  cur.execute  <- eu_permisiuni (app.get:7962)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:8546  cur.execute  <- banca_rec_ignora (app.post:8540)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:8799  _cur.execute  <- cv_locatii (app.get:8790)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9106  cur.execute  <- verificare_stocuri (app.get:9095)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9110  cur.execute  <- verificare_stocuri (app.get:9095)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9119  cur.execute  <- verificare_stocuri (app.get:9095)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9122  cur.execute  <- verificare_stocuri (app.get:9095)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9148  cur.execute  <- etransport_xml (app.post:9139)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9180  cur.execute  <- etransport_trimite (app.post:9168)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9212  cur.execute  <- etransport_trimiteri_lista (app.get:9204)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9237  cur.execute  <- banca_rec_reactiveaza (app.post:9231)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9273  cur.execute  <- factura_recunoaste (app.post:9252)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9295  cur.execute  <- factura_recunoaste (app.post:9252)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9360  cur.execute  <- vanzare_marja (app.post:9345)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9371  cur.execute  <- vanzare_marja (app.post:9345)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9429  cur.execute  <- vanzare_marja_turism (app.post:9385)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9435  cur.execute  <- vanzare_marja_turism (app.post:9385)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9474  cur.execute  <- vanzare_aur_investitii (app.post:9444)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9478  cur.execute  <- vanzare_aur_investitii (app.post:9444)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9507  cur.execute  <- achizitie_agricultor (app.post:9486)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9512  cur.execute  <- achizitie_agricultor (app.post:9486)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9549  cur.execute  <- vanzare_agricultor (app.post:9521)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9554  cur.execute  <- vanzare_agricultor (app.post:9521)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9623  cur.execute  <- jurnal_marja (app.get:9609)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9663  cur.execute  <- d406_active_xml (app.get:9654)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9706  cur.execute  <- d406_stocuri_xml (app.get:9681)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9859  cur.execute  <- facturi_trimiteri_spv (app.get:9852)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9912  cur.execute  <- import_efactura (app.post:9901)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9947  cur.execute  <- facturi_primite_lista (app.get:9937)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9952  cur.execute  <- facturi_primite_lista (app.get:9937)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:9981  cur.execute  <- factura_primita_xml (app.get:9974)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10002  cur.execute  <- factura_primita_valideaza (app.post:9989)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10035  cur.execute  <- factura_primita_valideaza (app.post:9989)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10052  cur.execute  <- factura_primita_valideaza (app.post:9989)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10093  cur.execute  <- factura_primita_respinge (app.post:10082)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10099  cur.execute  <- factura_primita_respinge (app.post:10082)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10126  cur.execute  <- reges_config (app.post:10110)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10150  cur.execute  <- reges_trimite_salariat (app.post:10138)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10155  cur.execute  <- reges_trimite_salariat (app.post:10138)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10175  cur.execute  <- reges_trimite_salariat (app.post:10138)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10199  cur.execute  <- reges_poll (app.post:10189)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10218  cur.execute  <- reges_poll (app.post:10189)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10252  cur.execute  <- achizitie_taxare_inversa (app.post:10230)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10276  cur.execute  <- achizitie_taxare_inversa (app.post:10230)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10288  cur.execute  <- achizitie_taxare_inversa (app.post:10230)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10293  cur.execute  <- achizitie_taxare_inversa (app.post:10230)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10360  cur.execute  <- achizitie_ic (app.post:10317)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10370  cur.execute  <- achizitie_ic (app.post:10317)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10375  cur.execute  <- achizitie_ic (app.post:10317)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10415  cur.execute  <- achizitie_neinregistrat (app.post:10383)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10426  cur.execute  <- achizitie_neinregistrat (app.post:10383)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10430  cur.execute  <- achizitie_neinregistrat (app.post:10383)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10493  cur.execute  <- vanzare_ic (app.post:10438)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10497  cur.execute  <- vanzare_ic (app.post:10438)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10519  cur.execute  <- import_extracomunitar (app.post:10506)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10553  cur.execute  <- import_extracomunitar (app.post:10506)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10558  cur.execute  <- import_extracomunitar (app.post:10506)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10594  cur.execute  <- export_extracomunitar (app.post:10567)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10598  cur.execute  <- export_extracomunitar (app.post:10567)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10618  cur.execute  <- intrastat_praguri (app.get:10606)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10692  cur.execute  <- nota_tva_incasare (app.post:10643)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10695  cur.execute  <- nota_tva_incasare (app.post:10643)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10732  cur.execute  <- decontare_valuta (app.post:10702)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10737  cur.execute  <- decontare_valuta (app.post:10702)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10793  cur.execute  <- reevaluare_valuta (app.post:10748)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10799  cur.execute  <- reevaluare_valuta (app.post:10748)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10842  cur.execute  <- nota_leasing (app.post:10807)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10847  cur.execute  <- nota_leasing (app.post:10807)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10893  cur.execute  <- nota_credit (app.post:10855)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10898  cur.execute  <- nota_credit (app.post:10855)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10960  cur.execute  <- nota_avans (app.post:10906)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:10965  cur.execute  <- nota_avans (app.post:10906)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11025  cur.execute  <- achizitie_necorporala (app.post:10973)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11033  cur.execute  <- achizitie_necorporala (app.post:10973)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11043  cur.execute  <- achizitie_necorporala (app.post:10973)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11049  cur.execute  <- achizitie_necorporala (app.post:10973)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11112  cur.execute  <- reevaluare_imobilizare (app.post:11058)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11117  cur.execute  <- reevaluare_imobilizare (app.post:11058)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11079  cur.execute  <- reevaluare_imobilizare (app.post:11058)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11162  cur.execute  <- nota_provizion_ep (app.post:11126)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11167  cur.execute  <- nota_provizion_ep (app.post:11126)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11204  cur.execute  <- nota_productie (app.post:11176)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11209  cur.execute  <- nota_productie (app.post:11176)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11251  cur.execute  <- nota_obiect_inventar (app.post:11217)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11256  cur.execute  <- nota_obiect_inventar (app.post:11217)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11301  cur.execute  <- nota_asociati (app.post:11264)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11306  cur.execute  <- nota_asociati (app.post:11264)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11341  cur.execute  <- nota_sponsorizare_ep (app.post:11315)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11346  cur.execute  <- nota_sponsorizare_ep (app.post:11315)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11386  cur.execute  <- nota_subventie (app.post:11355)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11391  cur.execute  <- nota_subventie (app.post:11355)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11446  cur.execute  <- nota_chirie (app.post:11400)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11452  cur.execute  <- nota_chirie (app.post:11400)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11497  cur.execute  <- nota_decont_deplasare (app.post:11460)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11502  cur.execute  <- nota_decont_deplasare (app.post:11460)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11537  cur.execute  <- nota_bacsis (app.post:11511)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11542  cur.execute  <- nota_bacsis (app.post:11511)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11590  cur.execute  <- nota_sgr (app.post:11551)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11595  cur.execute  <- nota_sgr (app.post:11551)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11625  cur.execute  <- nota_perisabilitati (app.post:11603)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11630  cur.execute  <- nota_perisabilitati (app.post:11603)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11660  cur.execute  <- nota_contract_special (app.post:11641)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11665  cur.execute  <- nota_contract_special (app.post:11641)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11690  cur.execute  <- tenant_mijloace_fixe (app.get:11675)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11785  cur.execute  <- nota_inventariere (app.post:11716)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11790  cur.execute  <- nota_inventariere (app.post:11716)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11794  cur.execute  <- nota_inventariere (app.post:11716)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11798  cur.execute  <- nota_inventariere (app.post:11716)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11756  cur.execute  <- nota_inventariere (app.post:11716)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11849  cur.execute  <- nota_lichidare (app.post:11814)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11854  cur.execute  <- nota_lichidare (app.post:11814)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11889  cur.execute  <- nota_ong (app.post:11863)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:11894  cur.execute  <- nota_ong (app.post:11863)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:12192  cur.execute  <- eveniment_public (app.post:12180)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:12204  cur.execute  <- admin_analytics (app.get:12199)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:12207  cur.execute  <- admin_analytics (app.get:12199)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:12211  cur.execute  <- admin_analytics (app.get:12199)
  ACTION_REQUIRED D1_SQL_IN_RUTA         main.py:12215  cur.execute  <- admin_analytics (app.get:12199)
  ACTION_REQUIRED D2_MOTOR_FISCAL_CU_DB  core/efactura_send.py:368  from core import db  <- core/efactura_send.py
  ACCEPTABLE_BY_DESIGN D3_HTTP_SUB_HTTP       core/spv_rute.py:42  HTTPException(...)  <- core/spv_rute.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/beneficii_api.py:1  FISCAL_ENGINE + REPOSITORY  <- core/beneficii_api.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/categorie_marime.py:1  FISCAL_ENGINE + REPOSITORY  <- core/categorie_marime.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/control_fiscal_api.py:1  FISCAL_ENGINE + REPOSITORY  <- core/control_fiscal_api.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/control_incrucisat.py:1  FISCAL_ENGINE + REPOSITORY  <- core/control_incrucisat.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d100.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d100.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d100_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d100_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d101.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d101.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d101_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d101_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d101g.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d101g.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d104.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d104.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d112.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d112.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d112_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d112_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d205.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d205.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d205_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d205_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d207.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d207.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d220.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d220.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d221.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d221.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d223.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d223.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d300.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d300.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d300_manual_api.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d300_manual_api.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d300_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d300_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d301.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d301.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d301_operatiuni_api.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d301_operatiuni_api.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d301_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d301_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d390.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d390.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d390_clasificare_api.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d390_clasificare_api.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d390_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d390_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d394.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d394.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d394_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d394_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d406.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d406.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/d406_reconciliere.py:1  FISCAL_ENGINE + REPOSITORY  <- core/d406_reconciliere.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/efactura_send.py:1  FISCAL_ENGINE + REPOSITORY  <- core/efactura_send.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/monitor_fiscal.py:1  USE_CASE + REPOSITORY  <- core/monitor_fiscal.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/notificari_scadenta.py:1  USE_CASE + REPOSITORY  <- core/notificari_scadenta.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/registru_evidenta_fiscala.py:1  FISCAL_ENGINE + REPOSITORY  <- core/registru_evidenta_fiscala.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/registru_inventar.py:1  FISCAL_ENGINE + REPOSITORY  <- core/registru_inventar.py
  ACTION_REQUIRED D4_STRAT_MIXT          core/scadentar.py:1  FISCAL_ENGINE + REPOSITORY  <- core/scadentar.py
  ACTION_REQUIRED D4_STRAT_MIXT          main.py:1  HTTP + REPOSITORY  <- main.py
```
