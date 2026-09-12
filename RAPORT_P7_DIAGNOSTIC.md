# P7 — DIAGNOSTIC. Nicio reparație.

**Instantaneu datat, nu registru viu.** Măsurat pe `f260df2e`, 13.09.2026. Se reproduce cu:

```
./venv/bin/python scripts/scan_p7_straturi.py          # universurile și itemii
./venv/bin/python scripts/p7_clasificare.py --itemi    # clasificarea, item cu item
./venv/bin/python -m pytest -q core/test_p7_clasificare.py   # calibrările celor trei detectoare
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
  construiește `HTTPException`; ruta nu conține SQL. Fiecare din cele trei se poate deriva cu `ast`
  și se poate garda cu clichet."*
- **`752-755`** — celelalte două criterii de acceptare: testele rutelor rămân verzi **fără să fie
  rescrise**; se măsoară ce s-a mutat, iar *„main.py a scăzut cu N linii" NU e criteriu*.

### Omonimia lui „P7", măsurată — și de ce contează pentru orice unealtă

`grep -n "P7"` peste registre întoarce **patru** lucruri diferite. Nu e o contradicție normativă;
e un omonim, și oricine construiește un instrument pe `grep P7` măsoară altceva:

| unde | ce înseamnă acolo |
|---|---|
| `PLAN_HARDENING.md:733` | **faza P7 — APPLICATION LAYER** *(subiectul de aici)* |
| `PLAN_ARHITECTURA.md:279` | **principiul P7** — „Verificarea e independentă prin construcție și prin disciplină" |
| `DECIZII.md:6434`, `TESTE.md:495` | **rândul P7** din declarația D101 („Rezultat brut") |
| `TESTE.md:167`, `GARZI.md:1727` | **clasa P7** din catalogul C-5 al mesajelor |

Cele două *planuri* nu se contrazic: PLAN_ARHITECTURA nu spune nimic despre stratificare, iar
PLAN_HARDENING nu spune nimic despre independența verificării. **`P7_NORMATIVE_CONFLICT=NO`.**

---

## 2. CE NU E P7 — datoriile care rămân unde sunt

- **`R69_IN_P7_SCOPE=NO`.** R69 e *„o declarație depusă pe un regim care s-a schimbat între timp nu
  contrazice pe nimeni"* (`CONFORMITATE.md`) — o verificare business care lipsește. Niciunul dintre
  cele trei criterii mecanice ale lui P7 nu o atinge: nu e SQL în rută, nu e motor fiscal care
  deschide conexiuni, nu e HTTP sub HTTP. Derivat din definiție, nu din faptul că e deschisă.
- **`OPERATIONAL_CONSTANT_TAXONOMY_IN_P7_SCOPE=NO`.** Taxonomia constantelor operaționale din
  `core/` e despre **citarea temeiului** unei valori, nu despre stratul în care trăiește. P7 nu
  vorbește despre constante.

---

## 3. UNIVERSUL, definit înainte de scanare

| | |
|---|---|
| **`P7_ENTRYPOINT_DEFINITION`** | funcție decorată cu `@<obiect>.<metodă>(...)`, metoda ∈ {get, post, put, delete, patch, head, options}. Derivat din AST peste `main.py` + `core/*.py`. **424** — *3 dintre ele nu sunt în `main.py`, ci în `core/spv_rute.py`* |
| **`P7_RAW_ITEM_DEFINITION`** | **D1**: un apel `.execute`/`.executemany` pe un nume legat de `.cursor()`, lexical în corpul unei rute · **D2**: un import/o folosire a lui `core.db` într-un modul-motor fiscal · **D3**: o construcție `HTTPException(...)` în `core/`, în afara oricărei rute |
| **`P7_PATH_DEFINITION`** | ruta în al cărei corp stă itemul (D1); modulul (D2, D3) |
| **`P7_EXCLUSION_DEFINITION`** | `core/test_*.py` (probe) · `core/scan_*.py` (instrumente de măsură) · `scripts/*` (unelte, nu sunt pe calea unei cereri) · `_arhiva_*` · `frontend_test/*`. **603 fișiere**, fiecare sub o regulă scrisă; `P7_UNEXPLAINED_EXCLUSIONS=0` |

**Universul nu e o listă scrisă:** se regenerează la fiecare rulare din repo.

---

## 4. CE A GĂSIT DIAGNOSTICUL

| detector | univers | itemi | rezultat |
|---|---|---|---|
| **D1 — SQL în rută** | 424 rute | **257** | **139 din 424 de rute execută SQL în corpul lor.** 91 SELECT · 100 INSERT · 28 UPDATE · 5 DELETE · 33 pe mai multe linii (felul nedeterminat din prima linie, declarat). Zero apeluri `.execute` pe altceva decât un cursor |
| **D2 — motor fiscal care atinge baza** | 25 module-motor | **0** | **Criteriul e deja îndeplinit.** Niciunul dintre cele 25 de module ale celor nouă declarații nu importă `db`: primesc `conn` ca parametru. *Zero e o măsurătoare, nu o orbire — detectorul găsește importul în `core/firma_rezumat.py` și în alte trei module, probat* |
| **D3 — HTTP sub stratul HTTP** | 323 module `core/` | **1** | `core/spv_rute.py:42` — și e ACCEPTABIL: modulul conține rute, deci **e** stratul HTTP, iar ce face acolo e autorizare tradusă în cod HTTP, exact sarcina stratului (`PLAN_HARDENING.md:743`) |

### Dezacordul dintre cele două instrumente — clasa `EVIDENCE_LIMITATION`

„Motor fiscal" nu e definit mecanic nicăieri. Am folosit **două** definiții independente și le-am
confruntat, în loc să aleg tăcut una:

- **F1** = modulele celor nouă declarații (`scripts/scan_lanturi_declaratie.py::generatoare()`) — **25**;
- **F2** = modulele care poartă valori fiscale (`core/scan_constante.py::inventar()`) — **104**;
- în comun: **16**; numai în F1: **9**; **7 module sunt fiscale după F2, nefiscale după F1, și ating
  baza**: `curs_bnr` · `efactura_send` · `firma_rezumat` · `monitor_fiscal` · `notificari_scadenta` ·
  `stare_partajata` · `stat_plata_emis`.

Pentru ele întrebarea „e o încălcare a lui «motorul fiscal nu importă `db`»?" **nu se poate decide
azi** — și nu se decide pe ghicite. *Asta e chiar prima cerință a implementării P7: un registru de
straturi, altfel criteriul rămâne nemăsurabil exact.*

---

## 5. FELUL DOVEZII, separat

| clasă de dovadă | ce acoperă aici |
|---|---|
| **STATIC_EVIDENCE** | toate cele 265 de poziții. Cele trei criterii canonice sunt proprietăți **structurale** ale codului („ruta conține SQL"), nu comportamente la rulare — AST-ul e forma potrivită, nu o scurtătură |
| **SYNTHETIC_EVIDENCE** | calibrările celor trei detectoare (fragmente scrise de mână, în `core/test_p7_clasificare.py`) |
| **REAL_PATH_EVIDENCE** | universul rutelor e chiar populația pe care o numără și verificatorul; itemii cunoscuți (`admin_sanatate`, `core/spv_rute.py:42`) sunt pinați în probe |
| **PRODUCTION_EVIDENCE** | **niciuna, și nu e nevoie de niciuna.** Nimic din P7 nu depinde de numărul de procese, de concurență sau de o cădere. *Nu prezint o probă statică drept probă de producție* |

---

## 6. CONTRACTE CARE NU SE REDESCHID

Măsurat: **139 din 139** de rute cu SQL își deschid singure conexiunea (`db.get_conn()` în corpul
rutei). Deci azi **ruta deține tranzacția**.

| contract | atins de reparația P7? | constrângerea pe care reparația TREBUIE s-o păstreze |
|---|---|---|
| **P4 — tranzacția** | **DA** | tranzacția trece de la rută la **use-case**, nu la repository. Un repository care își deschide propria conexiune ar sparge atomicitatea pe care P4 a închis-o |
| **P5 — I/O extern** | **NU** | nicio poziție P7 nu mută un apel extern |
| **P6 — starea procesului** | **NU** | nicio poziție P7 nu introduce stare în memoria procesului; `stare_partajata` apare doar în lista de dezacord, ca modul, nu ca stare nouă |
| altele | `[login_lockout_v1]`, `[upsert-ok]`, fail-closed-ul de pornire | mutarea SQL-ului nu are voie să schimbe nici pragurile, nici purtarea la eșec |

---

## 7. VALURI PROPUSE — nicio implementare

**V1 — repository pentru citiri** · 91 de poziții SELECT · cauză comună: ruta știe SQL ·
contract propus: *toate citirile trec printr-un modul-repository; ruta nu mai conține `cur.execute`
pe citire* · risc: **mic** (citirile n-au efect) · probe: gardă pe AST cu clichet descrescător +
testele existente ale rutelor rămân verzi **nerescrise** · exercițiu de producție: **NU**.

**V2 — repository pentru scrieri** · 133 de poziții (100 INSERT + 28 UPDATE + 5 DELETE) · contract
propus: la fel, **plus** tranzacția rămâne a apelantului (P4) · risc: **mare** (atomicitate) ·
probe: pe lângă cele de la V1, o probă că fiecare scriere mutată rămâne în aceeași tranzacție ·
exercițiu de producție: **NU** (probele P4 existente acoperă atomicitatea).

**V3 — registrul de straturi** · cele 7 dezacorduri + definiția lui „motor fiscal" · contract
propus: fiecare modul își declară stratul, iar `scan_p7_straturi` citește declarația în loc să
folosească două aproximări · risc: mic · exercițiu de producție: **NU**.

**Ordinea e dată de risc și dependență**, nu de comoditate: V1 înainte de V2 fiindcă citirile nu pot
strica date; V3 poate merge oricând, dar **înaintea** oricărei afirmații că „D2 = 0" e completă.

**Cele 33 de poziții cu felul nedeterminat** se împart între V1 și V2 după ce se citesc — nu le-am
repartizat din prima linie a instrucțiunii.

---

## 8. PLANUL DE ACCEPTANȚĂ

| criteriu (`PLAN_HARDENING.md`) | baseline azi | țintă | măsurare | gardă | probă de producție |
|---|---|---|---|---|---|
| `751` — ruta nu conține SQL | **257** poziții / 139 rute | **0** | `scan_p7_straturi.d1_sql_in_ruta()` | clichet descrescător, fișier cu fișier | NU |
| `749` — motorul fiscal nu importă `db` | **0** (deja îndeplinit) | **rămâne 0** | `d2_motor_fiscal_cu_db()` | gardă anti-regresie | NU |
| `750` — use-case fără `HTTPException` | **0** sub stratul HTTP | **rămâne 0** | `d3_http_sub_http()` | gardă anti-regresie | NU |
| `752-753` — testele rutelor rămân verzi **nerescrise** | 5634 verzi | 5634 verzi, **fără rescrieri** | diff-ul probelor la fiecare val | poarta completă | NU |
| `754-755` — se măsoară **ce s-a mutat** | — | raport per val | numărul de poziții mutate, pe rută | — | NU |

*Nicio țintă inventată: fiecare vine dintr-o linie a textului canonic. „main.py a scăzut cu N linii"
nu apare, fiindcă textul spune explicit că nu e criteriu.*

---

## 9. CONTABILITATEA

```
P7_SCANNED_ITEMS           324      (main.py + 323 module core/)
P7_EXCLUDED_ITEMS          603      (fiecare sub o regulă scrisă)
P7_RAW_ITEMS               265
P7_CLASSIFIED_ITEMS        265
P7_ACTION_REQUIRED         257
P7_ACCEPTABLE_BY_DESIGN      1
P7_FALSE_POSITIVES           0
P7_EVIDENCE_LIMITATIONS      7
P7_UNCLASSIFIED_ITEMS        0
P7_UNEXPLAINED_EXCLUSIONS    0

pe detector:  D1 = 257   ·   D2 = 0 + 7 dezacorduri   ·   D3 = 1
universuri :  424 rute   ·   323 module core/   ·   25 module fiscale
```

**Egalitatea se verifică mecanic**, nu se citește de aici:
`core/test_p7_clasificare.py::test_contabilitatea_se_inchide`.

**Cele 257 de poziții `ACTION_REQUIRED` împart același contract, aceeași dovadă și același motiv**
(regula `D1_SQL_IN_RUTA`, temei `PLAN_HARDENING.md:751`) — de aceea câmpurile comune sunt scrise o
dată, la clasă, iar fiecare poziție își are rândul ei mai jos, cu fișier, linie, simbol și ruta.

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
  ACCEPTABLE_BY_DESIGN D3_HTTP_SUB_HTTP       core/spv_rute.py:42  HTTPException(...)  <- core/spv_rute.py
  EVIDENCE_LIMITATION D2_DEZACORD            core/curs_bnr.py:225  from core import db  <- core/curs_bnr.py
  EVIDENCE_LIMITATION D2_DEZACORD            core/efactura_send.py:368  from core import db  <- core/efactura_send.py
  EVIDENCE_LIMITATION D2_DEZACORD            core/firma_rezumat.py:469  from core import db  <- core/firma_rezumat.py
  EVIDENCE_LIMITATION D2_DEZACORD            core/monitor_fiscal.py:125  from core import db  <- core/monitor_fiscal.py
  EVIDENCE_LIMITATION D2_DEZACORD            core/notificari_scadenta.py:20  from core import db  <- core/notificari_scadenta.py
  EVIDENCE_LIMITATION D2_DEZACORD            core/stare_partajata.py:171  from core import db  <- core/stare_partajata.py
  EVIDENCE_LIMITATION D2_DEZACORD            core/stat_plata_emis.py:31  from core import db  <- core/stat_plata_emis.py
```
