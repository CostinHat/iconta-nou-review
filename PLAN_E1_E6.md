# PLAN E1…E6 — etapa de după închiderea P0…P7

**Baza:** `RAPORT_AUDIT_GLOBAL_POST_HARDENING_2026-09-14.md`, acceptat ca punct de plecare.
**Măsurat pe:** `b8bcead0` (arbore curat, poartă verde). **Scris:** 14.09.2026.

**P0…P7 rămân `CLOSED_ACCEPTED` și nu se redeschid.** Regula are o consecință mecanică pe care planul
ăsta o duce până la capăt: **nicio etapă de mai jos nu are voie să schimbe o cifră pe care o
acceptare închisă o poartă în ea.** Unde o măsurătoare nouă se suprapune peste una veche, primește
**nume nou**; cifra veche rămâne cu domeniul ei.

---

## CUM E SCRIS FIECARE PAS

Ca la P0…P7: **baseline** (măsurat azi, cu instrumentul care îl recalculează), **criteriu de ieșire**
(o cifră, nu o impresie), **dependențe** (ce trebuie să fie adevărat înainte) și **ce NU face**.

---

# E1 — Ritmul se numără o singură dată · **ÎNCHIS 14.09.2026**

**Constatările:** D1, D2, D3 din audit. **Rezultat: `RATE_LIMIT_IN_PROCES` 6 → 0.**

```
E1_STATUS=CLOSED_ACCEPTED            E1_BAZA=6b9ba2da  (commitul de dinainte de E1)
#  commitul care POARTA E1 e chiar cel care contine randul asta — ca la predare, un document
#  nu-si poate scrie propriul commit fara sa-l fi facut deja
RATE_LIMIT_IN_PROCES_INAINTE=6       RATE_LIMIT_IN_PROCES_ACUM=0
PRAGURI_SCHIMBATE=0                  CONTRACT_HTTP_SCHIMBAT=0
LOGROTATE_SCRIS=1                    LOGROTATE_INSTALAT=0   (cere root — v. mai jos)
```

**Ce s-a făcut:** cele trei dicționare au plecat în `public.cereri_ritm`, cu tiparul de la
`login_esecuri` — un rând per cerere admisă, fereastra în `WHERE`, ștergerea celor expirate la
fiecare scriere, **ridică** la bază căzută. Peste tipar s-a adăugat un **blocaj consultativ pe
`(cheie, ip)`**: la login cursa dintre două inserări e inofensivă, aici ar fi fost o scăpare de
prag. Probat: opt fire simultane trec exact cinci.

**Ce a rămas, explicit:** `config/iconta-logrotate.conf` e scris și verificat
(`logrotate --debug`, zero note), dar **instalarea în `/etc/logrotate.d/` cere root** — ca
`Environment=WEB_CONCURRENCY=2` la P6 val 3. Comanda e în antetul fișierului. Până atunci,
**D3 din audit rămâne deschis**, iar `uvicorn.log` crește în continuare.

### Baseline (măsurat, `b8bcead0`)
```
LIMITATOARE_IN_MEMORIA_PROCESULUI = 3
  main.py:1545        _reset_rate    /public/reset-parola/cere
  main.py:1557        _cui_rate      /public/verifica-cui/{cui}   (rută publică → cheia ANAF)
  core/uc_comun.py:507 _magic_rate   /public/magic-link
PROCESE_IN_PRODUCTIE      = 2   (Environment=WEB_CONCURRENCY=2, de la P6 val 3)
PRAG_EFECTIV              = 2 × pragul scris
CONTOARE_LA_REPORNIRE     = se golesc
IP_URI_UITATE             = 0   (main.py:1563-1566 curăță doar IP-ul care cere acum)
LOGROTATE_PENTRU_ICONTA   = 0   · uvicorn.log = 63,7 MB
```

### Criteriu de ieșire
- `LIMITATOARE_IN_MEMORIA_PROCESULUI = 0`, gardat pe AST (un dicționar de modul folosit ca stare de
  ritm pică proba).
- Probat pe **procese reale**, ca la P6: cinci cereri pe lucrătorul A, **a șasea refuzată pe B**.
- Curățare periodică a rândurilor expirate, cu probă că tabela nu crește nemărginit.
- `logrotate` instalat pentru `uvicorn.log`, `alerta_acces.log`, `firma_rezumat.log`.

### Dependențe
**Niciuna.** Șablonul există deja în depozit: `core/stare_partajata.py:72-81,110` ține DDL-ul și
citirea pentru `login_esecuri` — blocarea la autentificare a fost mutată în bază exact din motivul
ăsta (`main.py:1274`). E1 aplică tiparul, nu inventează unul.

### Ce NU face
Nu atinge pragurile (5/15 min, 10/15 min rămân), nu schimbă mesajul de refuz, nu mută `_ip_client`.

*De notat:* codul nou aterizează în `core/stare_partajata.py` — unul dintre cele **6** module
declarate `REPOSITORY` care își deschid singure conexiunea (v. E2a). Nu blochează E1; se consemnează
ca să nu pară, la E2a, o regresie a acestui pas.

---

# E2 — Universul, nu eșantionul

**Constatarea:** L1 din audit. **Etapa asta se face în DOI pași, și mai jos e demonstrat de ce.**

### Baseline (măsurat, `b8bcead0`)
```
MODULE_PRODUCTIE_CORE            = 405
MODULE_CU_STRAT_DECLARAT         = 195
MODULE_NEDECLARATE_CU_SQL        = 138  = 87 vii + 51 migrări unice
INSTRUCTIUNI_SQL_IN_ELE          = 685  = 544 (vii) + 141 (migrări)
  din cele 87 vii: 16 își deschid SINGURE conexiunea → nu pot fi REPOSITORY prin contract
REPOSITORY_DECLARATE             = 65
REPOSITORY_CARE_ISI_DESCHID_CONEXIUNE_SAU_COMIT = 6
  core/firma_rezumat.py (get_conn 9, commit 2, 1357 linii, importă `main`)
  core/curs_bnr.py (2/1) · core/stare_partajata.py (1/0) · core/facturi_api.py (0/3)
  core/asociati_import_api.py (0/1) · core/salariati_import_api.py (0/1)
STRATURI_MIXTE_DECLARATE (`straturi.mixte()`) = 0
```

### De ce doi pași — și de ce nu se poate altfel

`scripts/scan_p7_straturi.py:379-383`:

```python
def d4_strat_mixt():
    return [Item(...) for d in straturi.mixte()]
```

**`D4` numără intrările din registru care au `mixt_cu` pus.** Nu observă nimic în cod. Deci:

- dacă cele 87 de module primesc o declarație **fără** `mixt_cu`, `D4` rămâne **0** — iar lărgirea e
  cosmetică: am declarat mai mult și n-am măsurat nimic în plus;
- dacă vreunul primește `mixt_cu`, **`D4` devine > 0**, iar
  `core/test_p7_criterii.py::test_cele_trei_detectoare_sunt_ZERO_si_raman` cade. Poarta pică, iar P7
  — `CLOSED_ACCEPTED` — s-ar redeschide printr-o cifră, fără ca nimeni s-o fi cerut.

*A treia ieșire, cea corectă:* măsurătoarea nouă primește **nume nou**. `D4` rămâne ce era când s-a
acceptat P7 — *„câte module sunt declarate mixte"*, pe universul de atunci. Alături apare
`D4b_MIXT_OBSERVAT`, care nu citește declarația, ci **codul**.

## E2a — universul se declară, amestecul se OBSERVĂ

### Criteriu de ieșire
- `MODULE_CU_SQL_FARA_STRAT = 0` pentru cele **87 vii**; cele **51 de migrări unice** intră într-o
  clasă de excludere **numită** (`MIGRARE_UNICA`), nu tăcută — cu regula scrisă lângă ea.
- Detector nou, pe observație, nu pe declarație:
  `D4b_MIXT_OBSERVAT` = module care conțin SQL **și** își deschid singure conexiunea sau comit.
  **Baseline așteptat: 16 + 6 = 22** (16 nedeclarate + 6 declarate `REPOSITORY` care încalcă
  contractul). Cifra se publică la prima rulare; nu se pune clichet pe ea înainte să fie văzută.
- `REPOSITORY_CARE_ISI_DESCHID_CONEXIUNE_SAU_COMIT = 0` **sau** fiecare din cele 6 are stratul
  corectat în registru — contradicția dintre declarație și cod nu rămâne nenumită.
- `D1`, `D2`, `D4` **rămân exact cifrele de azi** (0/0/0). Probat: rularea lui
  `core/test_p7_criterii.py` după E2a e verde, fără ca fișierul să fie atins.

### Dependențe
**E6** — `core/firma_rezumat.py` nu poate primi un strat onest cât timp importă `main`: un modul de
sub HTTP care depinde de HTTP n-are strat, are contradicție. E6 scoate una din cele trei
contradicții ale lui (import de `main`, 9 `get_conn`, declarat `REPOSITORY`).

### Ce NU face
Nu mută nicio linie de cod. E2a **numește**; separarea e E2b.

## E2b — valul care separă

### Criteriu de ieșire
`D4b_MIXT_OBSERVAT → 0`, cu aceleași reguli ca la valurile P7: mutare verbatim, contract HTTP
neschimbat, confruntare cu commitul dinainte.

### Dependențe
**E2a** (nu știi ce separi până nu e numit) și **E3** (nu muți 22 de module fără plasă).

### Ce NU face
Nu se planifică acum. **Mărimea lui se citește din E2a**, nu se estimează înainte — regula care a
ținut la D4 (37 de module, 215 instrucțiuni, aflate abia după ce s-au numărat).

---

# E3 — Ce scrie, se probează

**Constatarea:** R1 din audit.

### Baseline (măsurat)
```
RUTE_TOTAL                        = 421
RUTE_FARA_PROBA_CARE_LE_NUMESTE   = 59
  din care SCRIU (POST/PUT/PATCH/DELETE) = 21
```
Cele mai grele patru, cu corpul lor: `POST/DELETE /cabinet/api-chei` (`core/uc_cabinet.py`) —
suprafață de autentificare; `POST /admin/cabinete/{id}/suspenda|reactiveaza` (`core/uc_admin.py`);
`POST /portal/bon*` (`core/uc_portal.py`) — singurul flux în care **un client**, nu contabilul,
scrie date care ajung în contabilitate.

### Criteriu de ieșire
- `RUTE_CARE_SCRIU_FARA_PROBA = 0`, cu clichet (o rută nouă care scrie și n-are probă pică).
- Probele se scriu **la nivel de RUTĂ** (prin `main.<rută>` sau `TestClient`), nu pe funcția din
  use-case. Motivul e mecanic, nu estetic: corpurile celor 21 stau în `core/uc_*.py`, iar E2b le
  poate muta. O probă pe rută supraviețuiește mutării; una pe funcție se rescrie — iar regula
  proiectului spune că **o mutare care cere rescrierea probelor a schimbat comportamentul**.

### Dependențe
**Niciuna.** Nu așteaptă E2: dimpotrivă, e precondiția lui E2b.

### Ce NU face
Nu acoperă cele 38 de rute de citire fără probă (rămân în `L4`, declarate).

---

# E4 — Reparația se vede rulând

**Constatările:** R2, R3 din audit.

### Baseline (măsurat)
```
DATORII_FISCALE_CA_XFAIL_STRICT = 4 relevante
  core/test_datorie.py:126  d205 — trunchiere reparată, NEEXERCITATĂ
  core/test_datorie.py:132  d390 — idem
  core/test_datorie.py:138  d710 — reparată, dar niciun test nu-i verifică trunchierea
  core/test_datorie.py:159  8 coduri DUK/eFactura canonizate FĂRĂ verificare la sursă
                            (A91b, R28, R17, R11b, R15, F10_68, BR-RO-100, BR-RO-110)
  (înrudite: :167 R17/R28/R32 tratate ca RÂNDURI de declarație, nedovedit)
```

### Criteriu de ieșire
Cele patru `xfail(strict=True)` devin **xpass** — deci **roșii**, fiindcă `strict=True` — și se scot
odată cu datoria. Asta e criteriul: registrul de datorii semnalează singur când datoria s-a stins.

### Dependențe
**Date, nu cod:** o firmă de probă cu profilul care declanșează d205 (dividende), d390 (achiziții
intracomunitare) și d710. Fără ea, generatoarele sar cu *„nu se datorează"* și reparația rămâne
nevăzută.

### Ce NU face
Nu atinge cele 139 de constante fără temei (T1) — altă clasă, alt pas.

---

# E5 — Motoarele fiscale se pot citi

**Constatarea:** T2 din audit. **Nu e campanie.**

### Baseline (măsurat)
```
FUNCTII_PESTE_120_LINII = 25
  core/d300.py:147   calcul_d300          546
  core/d112.py:229   _d112_genereaza      465
  core/d394.py:416   calcul_d394          379
  core/control_fiscal_api.py:172 obligatii_datorate 358
```

### Criteriu de ieșire
Clichet **descrescător** pe „funcții peste 200 de linii în motoare fiscale". Se atinge **numai când
modulul se deschide oricum** pentru altceva. *Un val de refactorizare pe motoarele fiscale, fără o
schimbare cerută, e risc fără beneficiu: ele produc cifre care se depun.*

### Dependențe
Niciuna — și nicio urgență.

---

# E6 — Modelul de citire nu mai depinde de HTTP · **ÎNCHIS 14.09.2026**

**Constatarea:** D4 din audit. **Rezultat: `CORE_IMPORTA_MAIN` 2 → 0.**

```
E6_STATUS=CLOSED_ACCEPTED            E6_BAZA=d76cf9d2  (commitul de dinainte de E6)
CORE_IMPORTA_MAIN_INAINTE=2          CORE_IMPORTA_MAIN_ACUM=0
FUNCTII_MUTATE=1                     LINII_MUTATE=81   (verbatim)
CONTRACT_SCHIMBAT=0                  COMPORTAMENT_SCHIMBAT=0
```

**Cum:** `pastila_firma` se cere de la `core/common.py` (în `main` era re-export),
`_construieste_contabil` de la `core/uc_comun.py` (în `main` rămăsese doar învelișul HTTP), iar
`_termene_una_firma` **s-a mutat** în `core/firma_rezumat.py`, lângă singurul ei apelant.
*Mutată, nu redirecționată:* `core/uc_termene.py` importă `firma_rezumat`, deci mutarea acolo ar
fi închis un ciclu — iar ruta `/termene` n-o mai cheamă din P2. Așa dependența **dispare**, nu
se schimbă în alta.

### Baseline (măsurat)
```
CORE_IMPORTA_MAIN = 2 locuri, 1 fișier
  core/firma_rezumat.py:1009  import main as _main   → _construieste_contabil, pastila_firma
  core/firma_rezumat.py:1024  import main as _main2  → _termene_una_firma
```
Incidentul care dovedește costul: în valul use-case, o curățenie automată de importuri a scos din
`main.py` re-exportul `pastila_firma` — nefolosit *acolo* — și **șase firme** au ajuns cu
`control_fiscal` în stare de eroare.

### Criteriu de ieșire
`CORE_IMPORTA_MAIN = 0`, gardat. Cele trei funcții ajung fie în stratul use-case, fie injectate.

### Dependențe
**Niciuna.** Cost estimat: o zi.

---

# ORDINEA — verificată, nu presupusă

## Întrebarea pusă: trebuie E2 primul, fiindcă schimbă universul detectoarelor?

**Răspuns: NU — și, mai important, E2 nu poate fi executat ca pas unic.**

Trei fapte mecanice, fiecare verificabil în două minute:

1. **E2 nu schimbă universul lui `D1` și `D2`.** `D1` (SQL în corpul unei rute) și `D2`
   (`d2_motor_fiscal_cu_db`, `scan_p7_straturi.py:386-395`) se derivă **din cod**, nu din registru.
   Adăugarea a 138 de declarații nu le atinge.
2. **E2 schimbă doar `D4`, și îl schimbă în direcția greșită.** `D4` = `straturi.mixte()`, adică
   numărul de intrări cu `mixt_cu` pus. Azi: **0**. Dacă E2 declară amestecurile reale, `D4 > 0` și
   `core/test_p7_criterii.py` cade — o fază `CLOSED_ACCEPTED` ar fi redeschisă de un pas care
   trebuia doar să lărgească vederea.
3. **Deci nu ordinea e problema, ci forma lui E2.** Se desparte în E2a (declară + observă, cu
   `D4b_MIXT_OBSERVAT` ca nume nou) și E2b (separă). `D4` rămâne cu domeniul cu care a fost acceptat.

## Ordinea recomandată

```
E1  →  E6  →  E3  →  E2a  →  E2b        (E4 în paralel, când există firma de probă)
                                         (E5 continuu, niciodată ca val)
```

| loc | pas | de ce acolo — argument mecanic |
|---|---|---|
| 1 | **E1** | singurul **defect viu** cu efect de securitate, pe trei rute publice. Zero dependențe, iar tiparul e deja în depozit (`core/stare_partajata.py`, `login_esecuri`). Nu așteaptă pe nimeni |
| 2 | **E6** | **precondiție pentru E2a**: `core/firma_rezumat.py` nu poate primi un strat onest cât timp importă `main`. O zi, o gardă, un incident deja plătit |
| 3 | **E3** | **plasa de siguranță a lui E2b**. Corpurile celor 21 de rute stau în `core/uc_*.py`, exact modulele pe care E2b le mută. Probele pe rută supraviețuiesc mutării; fără ele, singurul verificator al valului ar fi iar poarta — iar valul use-case a pierdut tăcut două gărzi anti-spam și 27 de comentarii-declarație tocmai acolo unde probele de comportament lipseau |
| 4 | **E2a** | numește universul și **observă** amestecul. Nu mută nimic, deci nu poate strica nimic |
| 5 | **E2b** | mărimea lui se citește din E2a, nu se estimează acum |
| — | **E4** | independent de cod; blocat de **date**. Intră când firma de probă e gata, oriunde în șir |
| — | **E5** | nu se programează; se face când modulul se deschide oricum |

## De ce NU E2 primul, spus scurt

Pus primul, E2 ar cere ori să **declarăm totul nemixat** — și atunci n-am măsurat nimic, doar am
scris —, ori să **spargem poarta** unei faze închise. Iar E2b, partea care chiar repară, ar muta 22
de module peste 21 de rute care **n-au nicio probă de comportament**. Ordinea de mai sus pune întâi
plasa, apoi saltul.

---

## CE NU CONȚINE PLANUL ĂSTA

- Nicio redeschidere a lui P0…P7. Unde o cifră veche și una nouă se ating, cea nouă are nume nou.
- Nicio implementare. Aici e planul; codul se scrie la comandă, pas cu pas.
- Nicio estimare pentru E2b: se calculează după E2a, din cifra lui.
