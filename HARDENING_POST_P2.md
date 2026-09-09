# HARDENING POST-P2 — reducerea datoriei operaționale rămase

**P2 e ÎNCHIS.** Documentul ăsta nu redeschide nimic și nu rescrie istoria: P2 a fost acceptat pe
`b393b19c`, cu artefactele din `masuratori/p2/`. Ce urmează e o intervenție **separată**, de tip
*hardening / debt controlat*, care nu schimbă nicio proprietate demonstrată — face doar mai greu ca
o modificare viitoare sau un incident operațional să le strice.

*Ce NU s-a atins, deliberat:* read-modelul · schema de versiuni per sursă · epoca temporală ·
`citeste()` set-based · semanticile `CURENT`/`INVALIDAT`/`EROARE` · mecanismul de advisory lock ·
`firma_tip` · structura endpointurilor · payloadul fiscal.

---

## 1. COMMIT

| | |
|---|---|
| punct de plecare | `b393b19c` (P2 închis, acceptat) |
| **hardening** | commitul care poartă fișierul de față — hash-ul complet e în `COMMIT_POST_P2_HARDENING.txt` din pachet |

---

## 2. AJUSTĂRILE, punct cu punct

### A · Taskurile de fundal pornesc DUPĂ infrastructura critică — `LOW`

`create_task(_bucla_alerte_sanatate())` rula **înaintea** blocului critic. Nu era un defect de
corectitudine — startup-ul e fail-closed —, dar era o ordine care nu se poate apăra: un task de
fundal se lega de o bază despre care încă nu se știa dacă poartă infrastructura P2.

Acum: *deschizi resursele → DDL → migrare → verificare → **dacă toate au trecut** → taskuri de
fundal → `yield`.* Contorul `_TASKURI_FUNDAL_PORNITE` există anume ca ordinea să fie **probabilă**:
`asyncio` nu ține o evidență la care să ajungă un test.

`main.py` · probe: `test_taskurile_de_fundal_nu_pornesc_daca_infrastructura_pica`,
`test_taskurile_de_fundal_pornesc_o_data_la_pornire_reusita`.

### B · Izolarea migrării per tenant — `MEDIUM`

O eroare SQL pe o firmă lăsa tranzacția în `current transaction is aborted`, iar **toate** firmele
următoare picau din cauza ei. Raportul spunea „N firme rupte" despre una singură, iar diagnosticul
trimitea omul să caute în locul greșit.

Acum fiecare firmă rulează într-un `SAVEPOINT` propriu: `RELEASE` la reușită, `ROLLBACK TO` la eșec,
iar eroarea **originală** se păstrează per firmă. **Fail-closed rămâne neatins** — orice eșec tot
oprește pornirea. S-a schimbat numai *precizia raportului*, nu purtarea.

`core/firma_rezumat.migreaza_triggerele` · probă:
`test_o_firma_rupta_nu_contamineaza_diagnosticul_celorlalte` — și folosește o eroare **SQL
adevărată**, nu un `raise` din Python: numai aia abortează tranzacția, deci numai aia probează
mecanismul reparat.

### C · Verificare periodică a driftului — `MEDIUM`

`verifica_infrastructura` apăra doar momentul pornirii. Un `DROP TRIGGER` executat după — migrare
externă, mână pe `psql` — ar fi rămas nevăzut până la următoarea repornire, iar între timp
rezumatele acelei firme ar fi rămas `curent` fără ca nimic să le mai invalideze.

Acum: `firma_rezumat.verifica_drift()`, **strict read-only**, rulează în bucla de sănătate care
exista deja (la 5 minute), **niciodată în calea de cerere**. La drift: `CRITICAL` în log, cu cod,
firmă, schemă, tabelă, trigger și moment; plus alertă prin mecanismul existent.

**Detectează și alertează; NU repară.** O buclă care ar recrea singură triggerele ar șterge chiar
semnalul: driftul ar dispărea din log, iar cauza n-ar mai fi căutată de nimeni. Repararea rămâne un
act deliberat — o repornire, care trece oricum prin migrare.

`/admin/sanatate` expune `p2_infrastructure_ok` și `p2_infrastructure_last_checked_at`, din
**instantaneu**, nu recalculate la cerere. `ok = null` înseamnă *încă neverificat* și **nu** se
rotunjește la `true`.

`main.py`, `core/firma_rezumat.py` · probe:
`test_driftul_unui_trigger_sters_e_detectat_si_reparabil` (PASS → FAIL → PASS, plus proba că
verificarea **n-a** repus triggerul), `test_verificarea_de_drift_nu_intra_in_calea_de_cerere`.

### D · Observabilitatea backlogului — `MEDIUM`

Lotul mărginit e corect arhitectural, dar „1000 în așteptare" nu spune dacă ecranele sunt în urmă cu
zece secunde sau cu patru ore.

`masura_backlog()` — o singură interogare, set-based — și raportul turei emite acum linia:

```
p2_worker_selected · p2_worker_processed · p2_worker_remaining · p2_worker_errors
p2_worker_locked_skips · p2_worker_unlock_failures · p2_worker_duration_seconds
p2_oldest_pending_age_seconds
p2_worker_firms · p2_pending_never_computed · p2_pending_in_error · p2_worker_stopped
```

**`p2_oldest_pending_age_seconds` e un PLAFON SUPERIOR, și se scrie ca atare.** Nu ținem istoricul
schimbărilor de sursă, deci nu știm clipa exactă în care o pereche a devenit învechită; știm
`calculat_la` — când a fost ultima dată bună. Eroarea merge în direcția „pare mai vechi decât e",
adică o alarmă mai devreme, niciodată una mai târzie. Perechile necalculate **niciodată** n-au
vârstă: se numără separat (`p2_pending_never_computed`), nu se topesc într-o medie.

**Nu s-au hardcodat praguri de alertă** — comanda cere metrica disponibilă, pragurile se stabilesc
pe ritmul operațional real.

`core/firma_rezumat.py` · probe: `test_masura_backlogului_numara_ce_asteapta_si_de_cand`,
`test_tura_raporteaza_metricile_cerute`.

### E · Monotonicitatea versiunilor — `LOW-MEDIUM`

Invarianta pe care stă tot modelul de prospețime: `firma_sursa_versiune.versiune` e **monoton
crescătoare** pentru fiecare `(tenant_id, tabela)`. Dacă un contor ar putea scădea, o sumă veche ar
putea redeveni egală cu cea curentă — iar un rezumat învechit ar reapărea ca `curent`, tăcut.

Scrisă în DDL, lângă tabelă. Și **impusă**: `versiune_doar_creste`, trigger `BEFORE UPDATE`, respinge
orice scădere cu `check_violation`, indiferent cine scrie — calea aplicației, o migrare externă sau
o mână pe `psql`. Costă un apel de funcție per actualizare de contor, pe un rând care se
actualizează oricum la fiecare scriere în sursă; prețul e marginal, iar ce cumpără e că invarianta
nu mai depinde de disciplina apelanților.

*S-a verificat că nicio cale a aplicației nu decrementează:* singurele scrieri sunt `+ 1` din cele
două funcții de trigger și din `marcheaza_schimbat`. Fixturile de test care fixează versiuni
lucrează pe rânduri **nou inserate** (curăță întâi), deci nu scad nimic.

`core/firma_rezumat.py` · probe: `test_versiunea_sursei_doar_creste`,
`test_o_scadere_de_versiune_e_REFUZATA_de_baza`.

### F · Regula pentru ramuri fiscale noi — `MEDIUM`

Scrisă în `GARZI.md`: orice ramură nouă în `termene` / `control_fiscal` care citește o sursă nouă
vine, **în același commit**, cu (1) sursa în registru, (2) fixtura care activează ramura, (3) testul
că sursa e observată, (4) testul de invalidare.

Cu motivul fiecăreia și cu instanța care a produs regula: `pontaj` cere **două** condiții deodată
(tichete **și** lună confirmată), iar fixtura a fost respinsă de gardă de două ori înainte să
activeze cu adevărat ramura.

**Nu** s-a construit un parser SQL — decizie explicită, nu omisiune.

---

## 3. INVARIANTELE SCRISE ÎN COD

Două blocuri de comentariu, puse anume ca o „optimizare" viitoare să nu le desfacă din neatenție:

- **lângă advisory lock** — `pg_advisory_lock` e la nivel de SESIUNE; `lock_conn` trebuie ținută
  până DUPĂ `unlock`. Forma tentantă și greșită (lock → întorci conexiunea → calculezi → altă
  conexiune → unlock) e scrisă explicit ca fiind cea reparată la audit.
- **lângă blocul de startup** — infrastructura P2 decide dacă un rezumat poate fi `curent`; eșecul e
  fatal pentru pornire. Nu se revine la `except: pass` sub pretextul „baza poate fi temporar
  indisponibilă".

Ambele numesc garda care le apără, ca legătura să nu se piardă.

---

## 4. TESTE ADĂUGATE

| fișier | probe | ce apără |
|---|---|---|
| `core/test_p2_infrastructura.py` | 25 (10 noi) | startup fail-closed · blocaj same-session · **A, B, C, D, E** |
| `core/test_p2_contract.py` | **7, în ~1,7 s** | contractul arhitectural, ca listă scurtă |

**`p2_contract`** e un grup **prin fișier**, nu prin marcaj: suita n-are registru de marcaje, iar un
marcaj neînregistrat ar produce avertismente la fiecare rulare — zgomot permanent pentru o
comoditate de selecție. Se rulează cu `pytest core/test_p2_contract.py`.

Cele șapte contracte: infrastructură incompletă → nu pornește · scriere în sursă → `invalidat` (și
**numai** ce o citește) · trecerea zilei → `invalidat` · lucrătorul → `curent` · doi lucrători → cel
mult unul · 5 vs 50 de firme → același număr de interogări · `tip_firma` fără buclă per firmă.

**Toate probele P2 rămân permanente.** Niciuna n-a fost marcată temporară sau ștearsă.

---

## 5. REZULTATE

| | |
|---|---|
| suită completă | **4270 passed · 0 failed** · 11 skipped · 14 xfailed · exit 0 |
| durată | 1570,83 s (26 min 10 s) |
| verificator | **TOTAL: 0 candidate** |
| `ruff` | `All checks passed!` |
| grupul `p2_contract` | **7/7, 1,68 s** |
| four-way | închis, verificat cu `git ls-remote` |

**Benchmarkul nu s-a reexecutat integral**, și e o decizie, nu o omisiune: modificările —
reordonarea taskurilor de pornire, `SAVEPOINT` în migrare, verificarea periodică în bucla de
sănătate, metricile lucrătorului, triggerul de monotonie — **nu ating calea de cerere**. Ce s-a
păstrat și rulează în suită e chiar proba cerută: `5 firme vs 50` pe toate cele cinci endpointuri
(`test_p2_endpoint_query_count` și `test_contract_6_...`), plus proba că verificarea de drift **nu**
intră în cereri.

---

## 6. DEBT RĂMAS

Ce **s-a închis** din lista de după audit: fereastra dintre două porniri în care un trigger șters
n-ar fi fost văzut (C) · diagnosticul contaminat la migrare (B) · lipsa observabilității SLA (D) ·
invarianta de monotonie nescrisă și neimpusă (E) · ordinea taskurilor (A).

Ce **rămâne**:

1. **R177 — DESCHISĂ.** Clasa „model de citire cu dependențe scrise din memorie" e reparată pentru
   `firma_rezumat`, dar **nu e măsurată pe tot repo-ul**. Nimic nu spune azi câți alți purtători ai
   aceleiași clase mai are aplicația. *(Rămâne deschisă prin decizie, nu din uitare.)*
2. **Ramurile acoperite sunt cele derivate din registrul de azi.** Un tabel citit pe o ramură
   neconstruită **și** absent din registru rămâne invizibil tuturor instrumentelor. Regula din §2·F
   e apărarea împotriva creșterii clasei; nu o desființează.
3. **Fixturile de ramură rulează pe o firmă atașată unui cabinet REAL** (`_ctx_admin` are nevoie de
   un administrator cu acces). Firma e ștearsă la final, dar pe durata probei apare în portofoliul
   acelui cabinet.
4. **Pragurile de alertă pe backlog nu sunt stabilite.** Metricile există; pragurile cer ritmul
   operațional real, nu o cifră inventată acum.
5. **Cifrele măsurătorii din dimineața de 08.09 se pot citi, nu se pot recalcula** — hamul care
   le-a produs n-a fost păstrat. Logurile sunt în `masuratori/p2/dimineata_*.txt`.
6. **Vârf de 3 conexiuni din 10** în tura lucrătorului. Măsurat și gardat; dacă pool-ul scade sub 4
   sau lucrătorul devine paralel, garda cade — ceea ce e purtarea dorită.
7. **Lotul rămâne 200 de perechi la 5 minute** (confirmat). La 1000 de firme × 5 aspecte, un backlog
   complet se golește în ~50 de ture. Acum e și **vizibil**, prin `p2_worker_remaining` și
   `p2_oldest_pending_age_seconds`.

---

## 7. CE NU S-A FĂCUT, DELIBERAT

Condiția de stop din comandă a fost respectată. Nu s-au introdus: event bus · scheduler nou ·
schimbări în read-model · Kafka/Redis · straturi noi de cache · modificări ale advisory lockului ·
refactor de autentificare · redesign al modelului de tenanți · parser SQL static.

**P2 rămâne ÎNCHIS.** Intervenția asta se înregistrează separat, ca
**POST-P2 HARDENING — COMPLET**.
