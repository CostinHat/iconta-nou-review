# RAPORT — REMEDIEREA FINALĂ P2, după auditul revizuirii | 09.09.2026

*Structura e cea cerută de comanda de remediere finală, punct cu punct. Acceptarea nu se cere pe
narațiune: fiecare afirmație de mai jos are un artefact brut în `masuratori/p2/` și o probă în
suită.*

---

## 1. COMMIT FINAL

| | |
|---|---|
| **codul remedierii** | `63c62218f5f4f14687bd83c9690a242291f2710d` — cele trei blockere |
| **ultima probă cerută + artefacte în git** | `2514337d997c21881b1f79dd7135e6c76b50e72f` |
| **acest raport + artefactele brute** | commitul care poartă fișierul de față; hash-ul complet e în `COMMIT_P2_REMEDIERE_FINALA.txt` din pachet |
| punct de plecare al turei | `7f40ee0c` |

**TOATE artefactele au fost produse pe `2514337d`**, adică **după** ultimul patch — cum cere
cerința 4.1. Fiecare artefact își poartă în antet comanda, timestampul, commitul, `git status
--short` și exit code-ul.

*De ce raportul stă într-un commit ulterior artefactelor: un raport care s-ar comite odată cu ele
și-ar cita propriul hash, ceea ce nu se poate. Hash-ul final e în pachetul de livrare, generat după.*

---

## 2. CE S-A REPARAT

### Finding 1 — infrastructura P2 putea eșua fail-open la startup

**Cauza.** `lifespan()` rula DDL-ul, migrarea triggerelor și verificarea într-un `try/except: pass`,
cu motivul scris în cod: *„nu blocăm pornirea dacă DB e temporar indisponibil"*. **Motivul era fals
de la naștere:** `verifica_fus_orar()`, două linii mai sus, deschide deja o conexiune și ridică —
deci o bază căzută oprea pornirea și înainte. Ce prindea `except`-ul nu era indisponibilitatea
bazei, ci **eșecul instalării infrastructurii**.

Iar fără ea nimic nu se vede: fără registrul `firma_aspect_sursa`, versiunea oricărui aspect e `0`,
deci **orice** rezumat pare curent, pe veci · fără triggere, nimic nu mai invalidează · fără coloana
`epoca`, dependența de timp dispare. **Niciuna nu produce o eroare la citire.**

**Modificarea.** Blocul e fail-closed: se loghează cu `.exception()` și se re-ridică. Eșecul
migrării pe fie și o singură firmă oprește pornirea, cu `tenant_id` / `schema` / excepție /
traceback per firmă. După migrare rulează `verifica_infrastructura()` — nouă, și mai mult decât
`verifica_triggerele`: tabele centrale · coloanele adăugate la remediere · cele trei funcții
PostgreSQL · registrul `firma_aspect_sursa` **comparat cu `ASPECTE`** · triggerele pe fiecare firmă
activă · triggerele pe sursele din `public` · proiecțiile `tip_firma`. Problemele se întorc cu
**cod dintr-un nomenclator închis** (`CODURI_INFRASTRUCTURA`, șapte), nu ca proză.

**Fișierele.** `main.py` (lifespan) · `core/firma_rezumat.py` (`verifica_infrastructura`,
`CODURI_INFRASTRUCTURA`, `migreaza_triggerele` cu eșecuri bogate).

**Testele.** `core/test_p2_infrastructura.py`: `test_p2_startup_fails_if_ddl_fails` ·
`test_p2_startup_fails_if_trigger_migration_incomplete` · `test_p2_startup_detects_missing_trigger` ·
`test_p2_verificarea_prinde_registrul_desincronizat` · `test_p2_verificarea_prinde_o_functie_lipsa` ·
`test_p2_trigger_migration_is_idempotent` · `test_p2_startup_happy_path`.

### Finding 2 — advisory lock luat și eliberat pe sesiuni diferite

**Cauza.** `pg_try_advisory_lock` e ținut de **conexiune**, nu de tranzacție. Era luat într-un
`with get_conn()` și eliberat în **alt** `with get_conn()` — două împrumuturi din pool, fără nicio
garanție că e aceeași sesiune PostgreSQL. Când nu e, `pg_advisory_unlock` întoarce `false` pe o
sesiune care nu ține nimic, iar blocajul rămâne agățat de prima conexiune până când pool-ul o
reciclează. *Un blocaj scurs nu se vede ca eroare: se vede ca o firmă care nu se mai recalculează
niciodată.*

**Modificarea.** `lock_conn` rămâne împrumutată pe toată durata recalculării firmei. `ia_blocajul()`
întoarce și `pg_backend_pid()`, citit **în aceeași instrucțiune** cu luarea blocajului;
`lasa_blocajul()` îl compară la eliberare. Unlock în `finally`. Rezultatul boolean e **verificat**:
`false` sau backend diferit → ERROR în log, cu firma și ambele PID-uri, plus contorul
`blocaje_neeliberate` în raportul turei.

**Fișierele.** `core/firma_rezumat.py` (`ia_blocajul`, `lasa_blocajul`, `recalculeaza_lot`).

**Testele.** `test_p2_pool_chiar_da_sesiuni_diferite` (anti-tautologie) ·
`test_p2_worker_same_session_advisory_lock` · `test_p2_worker_second_worker_skips_locked_tenant` ·
`test_p2_worker_unlocks_after_success` · `test_p2_worker_unlocks_after_exception` ·
`test_p2_worker_unlock_false_observable` · `test_p2_worker_semnaleaza_sesiuni_diferite` ·
`test_p2_worker_no_lock_leak_in_pool` · `test_p2_worker_nu_epuizeaza_poolul`.

### Finding 3 — matricea de dependențe se sprijinea pe ramurile exercitate de portofoliul de azi

**Cauza.** Instrumentarea dinamică vede numai drumurile pe care le exercită datele firmelor
existente. Registrul și scanul puteau fi **egale și amândouă incomplete**.

**Modificarea.** Ramurile se derivă prin **măsurare**: ce declară registrul, minus ce atinge o firmă
**goală** construită din `tenant_template.sql` cu vector fiscal complet. Rezultat: din cele 27 de
surse ale lui `control_fiscal`, **24 se citesc necondiționat**; ramuri sunt exact trei.
`core/test_dependente_ramuri.py` construiește o firmă reală din template și aplică setup-uri
**cumulativ**, măsurând delta după fiecare.

**Fișierele.** `core/test_dependente_ramuri.py` (nou) · `scripts/scan_dependente.py`
(`RAMURI_ACOPERIRE` + blocul generat) · `DEPENDENTE_P2.md` (secțiunea ACOPERIRE RAMURI).

**Testele.** `test_ramura_deschide_sursele_ei` (parametrizat) ·
`test_ramurile_acopera_tot_ce_declara_registrul` ·
`test_nicio_sursa_observata_nu_lipseste_din_registru` ·
`test_3ABC_sursa_ceruta_de_audit_e_exercitata` · `test_3D_sursa_publica_e_exercitata` ·
`test_3F_garda_pica_daca_o_sursa_iese_din_registru` (mutație) ·
`test_registrul_de_ramuri_e_acelasi_in_proba_si_in_document`.

---

## 3. STARTUP / MIGRARE

| lanțul cerut | ce se întâmplă | proba |
|---|---|---|
| DDL P2 eșuează → **startup failure** | `aplica_ddl` ridică → `lifespan` loghează cu `.exception()` și re-ridică; aplicația nu intră în `ready` | `test_p2_startup_fails_if_ddl_fails` |
| migrarea triggerelor incompletă → **startup failure** | o singură firmă nelegată → `RuntimeError`, după ce **toate** firmele au fost încercate (raportul spune CÂTE sunt rupte, nu doar care e prima) | `test_p2_startup_fails_if_trigger_migration_incomplete` |
| trigger lipsă **după** migrare → **startup failure** | `verifica_infrastructura` îl prinde; „`CREATE TRIGGER` n-a ridicat excepție" nu e destul | `test_p2_startup_detects_missing_trigger` |
| registru desincronizat → **startup failure** | `firma_aspect_sursa` comparat cu `ASPECTE`; cod `REGISTRU_DESINCRONIZAT` | `test_p2_verificarea_prinde_registrul_desincronizat` |
| happy path → **startup OK, idempotent** | pornire reușită, și a doua oară; migrarea repetată nu schimbă setul de triggere și nu lasă duplicate | `test_p2_startup_happy_path`, `test_p2_trigger_migration_is_idempotent` |

**Varianta aleasă e FAIL-FAST**, cea preferată de comandă. Nu s-a construit calea „tenant
degradat": n-a existat un motiv operațional real, iar ea ar fi cerut o stare `P2_UNHEALTHY`
persistentă, propagată în `citeste()`, în worker, în UI și în healthcheck — adică un al doilea
mecanism de prospețime, exact clasa pe care P2 o repară.

**Starea măsurată acum, pe producție:**

```
ok: True · tabele_lipsa: [] · coloane_lipsa: [] · functii_lipsa: []
registru_in_baza: 37 = registru_in_cod: 37 · firme_active: 20 · triggere_lipsa: []
surse_publice_fara_trigger: [] · domeniu_gol: False
```

**Consecință operațională, declarată:** dacă baza e indisponibilă la pornire, aplicația **nu
pornește**. Asta nu e o schimbare de purtare — `verifica_fus_orar()` o făcea deja. Ce s-a schimbat e
că acum **și** o infrastructură incompletă oprește pornirea.

---

## 4. WORKER LOCKING

| întrebare | răspuns |
|---|---|
| tipul blocajului | **advisory de SESIUNE**, `pg_try_advisory_lock(CHEIE_BLOCAJ, tenant_id)`, `CHEIE_BLOCAJ = 0x1C0A7A` |
| cine îl ține | conexiunea `lock_conn`, împrumutată din pool **pe toată durata recalculării firmei** |
| când se obține | înainte de orice calcul, **neblocant**: dacă altcineva ține firma, tura o sare (`sarite_blocate`), nu o așteaptă |
| când se eliberează | în `finally`, deci și la excepție, și la abandon |
| verificarea | `pg_backend_pid()` citit **odată cu** luarea și comparat la eliberare; `pg_advisory_unlock` verificat ca boolean |
| la excepție | blocajul se eliberează; probat cu `recalculeaza_firma` monkeypatch-uit să ridice |
| ce se vede la eșec | ERROR în `iconta.firma_rezumat` cu firma și ambele PID-uri; `blocaje_neeliberate` în raportul turei |

**De ce nu `pg_try_advisory_xact_lock`.** Recalcularea deschide **alte** conexiuni și alte
tranzacții (`recalculeaza_greu` ia două deodată). Un blocaj tranzacțional ar fi ținut doar cât
tranzacția conexiunii de blocaj — adică nu ar acoperi secțiunea critică. S-a păstrat blocajul de
sesiune, cu sesiunea ținută deschisă.

**Regresia pe care o introduce reparația, MĂSURATĂ.** Ținând o conexiune în plus, vârful de
conexiuni simultane într-o tură e **3, la un plafon de pool de 10**. Măsurat pe o firmă reală cu
aspecte grele, nu presupus — și gardat de `test_p2_worker_nu_epuizeaza_poolul`, care măsoară vârful
la fiecare rulare și cade dacă atinge plafonul.

**Anti-tautologia.** `test_p2_pool_chiar_da_sesiuni_diferite` verifică întâi că pool-ul chiar
întoarce backenduri PostgreSQL distincte. Fără ea, „lock pe A, unlock pe B" ar putea trece din
întâmplare. Iar `test_p2_worker_semnaleaza_sesiuni_diferite` **simulează chiar defectul de dinainte**
și cere ca blocajul să rămână agățat și eroarea să apară — deci garda e probată pe defectul real,
nu doar pe reparație.

---

## 5. DEPENDENCY COVERAGE

**Cum s-au derivat ramurile:** măsurat ce atinge o firmă goală din `tenant_template.sql` (vector
fiscal complet), scăzut din registru. Diferența E lista ramurilor.

| aspect | ramură | fixture | surse observate (delta) | surse declarate | status |
|---|---|---|---|---|---|
| `termene`, `control_fiscal` | `baza_vector_complet` | firmă din template, vector complet | 5 (termene) + 24 (control_fiscal) | idem | **ACOPERIT** |
| `control_fiscal` | `salarii` | salariat activ **cu tichete** + lună confirmată pe `pontaj` | `pontaj`, `salariu_istoric` | declarate | **ACOPERIT** |
| `control_fiscal` | `stoc` | articol + mișcare de stoc | `miscari_stoc` | declarată | **ACOPERIT** |
| `termene`, `control_fiscal` | `facturi_emise` | o factură emisă | — (nicio sursă nouă) | — | **ACOPERIT** |
| `termene`, `control_fiscal` | `vector_pfa_profit_neplatitor` | PFA · partidă simplă · profit · neplătitor TVA | — | — | **ACOPERIT** |
| `termene`, `control_fiscal` | `vector_trimestrial_art317_tva_incasare` | SRL · profit · TVA trimestrial · IC · art. 317 · TVA la încasare | — | — | **ACOPERIT** |

**Reuniunea peste ramuri = registrul, exact.** `MASURAT − DECLARAT = ∅` pe fiecare ramură și
fiecare aspect (`test_nicio_sursa_observata_nu_lipseste_din_registru`), iar
`DECLARAT − MASURAT = ∅` peste reuniune (`test_ramurile_acopera_tot_ce_declara_registrul`).

### Ce a costat asta, și de ce merită scris

Fixtura pentru `pontaj` a fost **respinsă de gardă de două ori**:

1. salariat activ → `pontaj` **neatins**;
2. salariat **cu tichete** → `pontaj` **tot neatins**;
3. plus **luna confirmată pe domeniul `pontaj`** → atins.

`d112` ridică `PerioadaNeconfirmata` **înainte** de citire dacă luna nu e confirmată
(HG 1045/2018 art.10(3): tichetele cer pontaj confirmat). Deci ramura cere **două condiții
deodată**. *O gardă care s-ar fi mulțumit cu prima formă ar fi declarat o acoperire inexistentă —
și exact asta e clasa pe care auditul a cerut-o închisă.*

### Mutația

`test_3F_garda_pica_daca_o_sursa_iese_din_registru`: cu ramura de stoc **activă**, se scoate
`miscari_stoc` din registru și verificarea **trebuie** să-l raporteze ca nedeclarat. Fără ea, un
`⊆` între două mulțimi calculate din aceeași sursă ar trece oricând.

### Ce NU acoperă, declarat

Ramurile sunt derivate din **registrul de azi**. O sursă pe care codul o citește și pe care nici
firma goală, nici cele șase fixturi n-o ating **și** care nu e în registru ar rămâne invizibilă
tuturor celor trei instrumente. Ce s-a închis e clasa „declarat, dar exercitat doar accidental";
clasa „citit pe o ramură pe care nimeni n-a construit-o" se micșorează, nu dispare — și de-aia
`scan_dependente` rămâne, iar `DEPENDENTE_P2.md` spune cum se reface.

---

## 6. QUERY COUNT FINAL

`scripts/masoara_rute_portofoliu.py`, prin `TestClient` — **cererea HTTP întreagă**: `cere_context`,
`cere_cabinet`, `tenantii_userului`, citirea modelului, serializarea. Nimic din calea de cerere nu e
înlocuit. Hamul e calibrat **prin stratul HTTP**, în ambele direcții, înainte de orice cifră.

Artefact: `masuratori/p2/benchmark_FINAL.log`.

| scenariu | N=5 | N=50 | N=100 | N=250 | N=500 | N=1000 |
|---|---|---|---|---|---|---|
| 0% invalidat | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c |
| 10% invalidat | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c |
| 100% invalidat | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c |
| **model rece** | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c | 5 q / 3 c |

**Identic pe toate cele cinci rute** (`/migrare/solduri`, `/migrare/plan-conturi`,
`/migrare/vector`, `/termene`, `/control-fiscal`), **toate răspunsurile 200**. Numărul de interogări
**nu depinde de N**.

Gardat și în suită, nu doar în artefact: `test_p2_endpoint_query_count` compară 5 vs 50 de firme pe
toate cele cinci rute, prin același ham.

`auth_api.tenantii_userului` pe portofoliul REAL (14 firme): **2 interogări / 1 conexiune**.

---

## 7. PARITATE

Artefact: `masuratori/p2/paritate_FINAL.log` · `core/test_paritate_p2.py` — **6 probe, 6 trecute,
0 picate**.

Pe **firme reale**, răspunsul rutei se compară **întreg**, cu `==`, cu ce ar fi dat bucla per firmă
de dinainte de P2, cu aceleași funcții. **Nicio normalizare** — nici a verdictelor
(`verde`/`galben`/`rosu`/`gri`), nici a sumelor, nici a ordinii. Singurul câmp scos e `prospetime`,
**cu motivul scris**: nu exista înainte de P2, deci n-are pereche.

A șasea probă e mutația: se strică deliberat o valoare și comparația **trebuie** să pice.

**Payloadul funcțional al celor 5 rute nu s-a schimbat** în această tură — de aceea paritatea trece
neatinsă, fără nicio ajustare a testului.

---

## 8. SUITA COMPLETĂ

Artefact: `masuratori/p2/suita_completa_FINALA.iesire.txt` (cu comandă, timestamp, commit,
`git status --short`, stdout+stderr, exit code).

| | |
|---|---|
| comandă | `./venv/bin/python -m pytest -q` |
| commit | `2514337d997c21881b1f79dd7135e6c76b50e72f` |
| **passed** | **4254** |
| **failed** | **0** |
| skipped | 11 |
| xfailed | 14 |
| **exit code** | **0** |
| durată | 1576,85 s (26 min 16 s) |

Verificator: `masuratori/p2/verificator_FINAL.log` → **TOTAL: 0 candidate**, exit code 0.
`ruff` (F821/F822/F823): `All checks passed!`

*Artefactul roșu de dinainte (`suita_completa.iesire.txt`, 9 failed) NU a fost suprascris — a rămas
în pachet, lângă cel verde. O dovadă care înlocuiește istoricul e o dovadă mai slabă.*

---

## 9. RISCURI RĂMASE

**Nu există „niciun risc".** Separate pe felul lor:

### BLOCKER
**Niciunul cunoscut.** Cele patru criterii de acceptare sunt demonstrate, fiecare cu artefact și
probă.

### DEBT

1. **Ramurile acoperite sunt cele derivate din registrul de azi.** Vezi §5, „ce nu acoperă". Un
   tabel citit pe o ramură neconstruită **și** absent din registru rămâne invizibil. Se micșorează
   clasa, nu dispare.
2. **Fixturile de ramură rulează pe o firmă atașată unui cabinet REAL** (`_ctx_admin` are nevoie de
   un administrator cu acces). Firma e ștearsă la final, dar pe durata probei apare în portofoliul
   acelui cabinet. Nu afectează date reale; se declară.
3. **R177 rămâne DESCHISĂ** — clasa „model de citire cu dependențe scrise din memorie" e reparată
   pentru `firma_rezumat`, dar **nu e măsurată pe tot repo-ul**. Nimic nu spune azi câți alți
   purtători ai aceleiași clase mai are aplicația.
4. **Cifrele măsurătorii de dimineață (08.09) se pot citi, nu se pot recalcula** — hamul care le-a
   produs n-a fost păstrat. Logurile sunt în `masuratori/p2/dimineata_*.txt`.
5. **`verifica_infrastructura` rulează la pornire, nu continuu.** Un trigger șters în timpul
   funcționării n-ar fi prins până la următoarea repornire. Nu e blocker (nimic din aplicație nu
   șterge triggere), dar e o fereastră reală.

### SLA / CAPACITY

6. **Vârful de conexiuni în tură: 3 din 10.** Măsurat, gardat. Dacă pool-ul se micșorează sub 4 sau
   lucrătorul devine paralel, garda cade — ceea ce e purtarea dorită.
7. **Lotul rămâne 200 de perechi la 5 minute** (confirmat de Costin). La 1000 de firme × 5 aspecte,
   un backlog complet se golește în ~50 de ture, adică peste 4 ore. E o alegere declarată, nu o
   scăpare: raportul turei spune `ramase`, deci un backlog care nu scade e vizibil.
8. **O trecere grea costă ~2,4 s per firmă.** La 1000 de firme atinse simultan, recalcularea
   completă e de ordinul a 40 de minute de lucru de fundal. Costul nu a dispărut, s-a mutat — cum
   scrie și în antetul modulului.

---

## VERDICT

Cele patru criterii cerute pentru „P2 = ÎNCHIS":

| | criteriu | stare |
|---|---|---|
| 1 | INFRASTRUCTURĂ FAIL-CLOSED | **PASS** — §3 |
| 2 | WORKER LOCKING CORECT | **PASS** — §4 |
| 3 | DEPENDENCY BRANCH COVERAGE | **PASS** — §5 |
| 4 | SUITĂ FINALĂ + BENCHMARK + PARITATE | **PASS** — §6, §7, §8 |

**Niciun blocker nou descoperit în timpul remedierii.** Ce s-a descoperit — condiția dublă a ramurii
`pontaj`, vocabularul `mesaj` vs `diagnostic`, cele nouă ancore pe text — a fost reparat în aceeași
tură și e scris mai sus.

**Nu declar eu P2 închis.** Comanda cere ca acceptarea să se facă pe cod, teste, artefacte brute și
commit final; toate patru sunt livrate. Declarația rămâne a ta.
