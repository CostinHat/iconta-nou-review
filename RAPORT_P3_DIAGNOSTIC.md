# RAPORT P3 — DIAGNOSTIC | 09.09.2026 | pe commitul `6b59c19f`

## TRASABILITATE

```
POST_P2_FULL_SUITE_COMMIT = 6e4dd53c6f6f6d7aa0d8aa4fb0d4d0634ad1eb0d
P3_MEASUREMENT_COMMIT     = 6b59c19f   (starea pe care s-au făcut măsurătorile P3)
P3_FINAL_COMMIT           = 54a91390   (diagnosticul, comis)
P3_EVIDENCE_COMMIT        = commitul care poartă corecțiile de precizie de față
```

**P3 final changes diagnostic/reporting artifacts only; no request-path runtime change after the
green POST-P2 suite.** Suita completă verde (4270 passed, exit 0) s-a rulat pe `6e4dd53c`; tot ce
a urmat — diagnosticul, măsurătorile, corecțiile de precizie — atinge **numai** instrumente de
măsură, artefacte și documente. Diff-ul o confirmă mecanic: niciun fișier din `main.py` sau
`core/` (în afara testelor) nu apare în commiturile de după.

---

**Diagnostic, fără implementare.** Nu s-a schimbat nicio linie din calea de cerere. Nu s-a mutat
nimic în cache, nu s-a atins fail-closed-ul, advisory lockul, `citeste()` set-based sau vreo gardă
P2. Ce urmează sunt măsurători și cauze demonstrate; propunerile din §6 sunt **scrise, nu făcute**.

---

## 1. CUM S-A DERIVAT LISTA RUTELOR — nu din memorie

`scripts/scan_cale_cerere.py`. O rută poate crește cu numărul de firme dacă ajunge, direct sau prin
apeluri, la funcția prin care o cerere află *care sunt firmele utilizatorului* —
`auth_api.tenantii_userului`. Se parsează `main.py` + `core/*.py` cu `ast`, se construiește graful
de apeluri pe nume simple, se ia închiderea tranzitivă a apelanților, apoi se încrucișează cu
decoratorii de rută.

**Calibrat în trei direcții** (apelant direct · apelant indirect la două niveluri · nu inventează o
rută străină) — altfel un graf care ar întoarce „toate rutele" ar părea că funcționează.

**37 de rute ating portofoliul. Doar 12 cresc cu N** — restul sunt de portal, unde poarta e
`cere_client`: un client vede **o** firmă, deci costul lui nu depinde de mărimea cabinetului.
Deosebirea se face pe poarta de autorizare, citită din `Depends(...)`, nu pe ghicite din cale.

**Ce nu vede instrumentul, declarat:** apeluri prin variabilă sau `getattr`; omonimii (două funcții
cu același nume simplu se contopesc → posibile fals-pozitive, care se văd la măsurare). Lista e un
**plafon inferior**.

---

## 2. INSTRUMENTUL — ce despică, și cum s-a dovedit că despică

`scripts/masoara_p3.py`, peste hamul HTTP din P2. Măsoară **cererea întreagă** prin `TestClient` și
o desface în:

| coloană | ce e |
|---|---|
| `db_sec` | timpul petrecut ÎN bază: durata fiecărui `execute` / `fetch*` **plus** deschiderea conexiunii, cronometrate în jurul apelului real |
| `cpu_sec` | `total_sec − db_sec` — Python: dependențele FastAPI, construirea răspunsului, serializarea JSON |
| `octeti` | mărimea răspunsului — proxy pentru serializare și rețea |

**De ce despicarea contează:** o rută poate avea **număr constant de interogări și tot să crească
liniar**, dacă lista de răspuns are N elemente. Fără despicare, „N+1 în bază" și „am de serializat N
obiecte" arată identic.

**Calibrare, ambele direcții** — și e chiar proba că separarea înseamnă ceva:

```
(a) rută care doar AȘTEAPTĂ baza (pg_sleep 0,2 s) -> db_sec 0,2021 · cpu_sec 0,0102 · db 95,2%
(b) rută care doar ARDE CPU (buclă 0,2 s)         -> db_sec 0,0000 · cpu_sec 0,2033 · db  0,0%
```

*Un instrument care ar pune tot timpul într-o singură coloană ar trece nedetectat pe orice rută
reală; numai o rută sigur de celălalt fel îl demască.*

---

## 3. DOMENIUL MĂSURĂTORII — și o afirmație a mea care era prea largă

**Curba sintetică**, N = 5/50/100/250/500/1000: firme în `public.tenants`, fiecare cu schema ei
(`tenants.schema_name` e unic, deci schemele reale nu se pot cicla).

### Ce am afirmat greșit, și corecția

Prima formă a raportului spunea că domeniul sintetic *„redă corect FORMA creșterii (câte interogări
și conexiuni per firmă), dar subestimează munca per firmă"*.

**Afirmația era prea largă.** Pe o schemă fără tabelele firmei, `rezumat()` **iese devreme** —
`SELECT to_regclass('<tabela>')` întoarce `NULL` — deci **și coeficientul de interogări per firmă e
mai mic**, nu doar timpul. Nu era o subestimare de latență; era o pantă diferită.

**Nu mai afirm nimic despre coeficientul real pe baza celui sintetic.** Calea de succes se măsoară
direct, pe scheme REALE construite din `tenant_template.sql` — §4.5 — iar cele două pante se
reconciliază explicit, cu instrucțiunile capturate, în §4.6.

### O a doua corecție, și e mai gravă: sonda a SCRIS în producție

Schemele sintetice erau, la a doua formă a hamului, **inexistente** — azi sunt **reale, dar goale**
(v. mai jos). `SET search_path TO "inexistenta",
public` e **acceptat** de PostgreSQL, care ignoră tăcut schemele care lipsesc — iar o rută care
apoi execută un `CREATE TABLE IF NOT EXISTS` **necalificat** nimerește prima schemă existentă din
cale, adică `public`.

Măsurând `/migrare/parteneri`, sonda a creat **`public.solduri_parteneri`** în producție: tabelă
goală, fără `tenant_id`, cu coloane identice cu cele din `tenant_template.sql`, **zero referințe în
tot codul**. E chiar clasa *„sonda de audit nu e read-only"*: am presupus că măsurătoarea nu poate
scrie, în loc s-o dovedesc.

**Reparat în instrument:** schemele sintetice sunt acum **reale, dar goale**. `to_regclass`
întoarce tot `NULL` — deci ramura măsurată nu se schimbă —, dar orice scriere necalificată
aterizează în schema de probă, care se șterge la curățenie.

*Tabela rămasă în `public` nu a fost ștearsă: e o operațiune ireversibilă pe producție și se cere
separat.* Vezi §11.

**A treia corecție, tot a instrumentului:** curățenia făcea `DROP SCHEMA ... CASCADE` pentru toate
schemele într-o singură tranzacție și cădea la N=1000 cu `out of shared memory /
max_locks_per_transaction` — adică pica exact când era cel mai mult de curățat, lăsând în urmă
1.000 de scheme. Curățate manual, în loturi; instrumentul șterge acum în loturi de 50, cu `commit`
după fiecare, și s-a probat pe 120 de scheme.

---

## 4. CURBELE BRUTE

Artefact: `masuratori/post_p2/curba_p3.json` · rulare: `masuratori/post_p2/curba_p3.iesire.txt`

### 4.1 Interogări / conexiuni

| rută | N=5 | N=50 | N=100 | N=250 | N=500 | N=1000 |
|---|---|---|---|---|---|---|
| `/control-fiscal` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/migrare/plan-conturi` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/migrare/solduri` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/migrare/vector` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/termene` | 5q/3c | 5q/3c | 5q/3c | 5q/3c | 5q/3c | **5q/3c** |
| `/tenants` | 4q/3c | 4q/3c | 4q/3c | 4q/3c | 4q/3c | **4q/3c** |
| `/migrare/istoric-declaratii` | 9q/8c | 54q/53c | 104q/103c | 254q/253c | 504q/503c | **1004q/1003c** |
| `/supervizor` | 15q/9c | 105q/54c | 205q/104c | 505q/254c | 1005q/504c | **2005q/1004c** |
| `/migrare/asociati` | 19q/13c | 154q/103c | 304q/203c | 754q/503c | 1504q/1003c | **3004q/2003c** |
| `/migrare/mijloace-fixe` | 19q/13c | 154q/103c | 304q/203c | 754q/503c | 1504q/1003c | **3004q/2003c** |
| `/migrare/salariati` | 19q/13c | 154q/103c | 304q/203c | 754q/503c | 1504q/1003c | **3004q/2003c** |
| `/migrare/parteneri` | 24q/13c | 204q/103c | 404q/203c | 1004q/503c | 2004q/1003c | **4004q/2003c** |

### 4.2 Latență totală, cu procentul petrecut în bază

| rută | N=5 | N=100 | N=1000 | db% la N=1000 |
|---|---|---|---|---|
| `/tenants` | 0,004 s | 0,006 s | **0,025 s** | 25,7% |
| `/migrare/plan-conturi` | 0,005 | 0,045 | **0,040 s** | 54,3% |
| `/migrare/solduri` | 0,005 | 0,009 | **0,042 s** | 52,0% |
| `/control-fiscal` | 0,005 | 0,010 | **0,050 s** | 50,9% |
| `/termene` | 0,005 | 0,009 | **0,053 s** | 51,2% |
| `/migrare/vector` | 0,005 | 0,009 | **0,097 s** | 22,1% |
| `/migrare/istoric-declaratii` | 0,006 | 0,037 | **0,324 s** | 66,2% |
| `/supervizor` | 0,007 | 0,053 | **0,496 s** | 71,4% |
| `/migrare/salariati` | 0,009 | 0,104 | **0,983 s** | 59,8% |
| `/migrare/mijloace-fixe` | 0,010 | 0,105 | **0,993 s** | 59,7% |
| `/migrare/asociati` | 0,010 | 0,104 | **0,995 s** | 59,8% |
| `/migrare/parteneri` | 0,016 | 0,135 | **1,317 s** | 62,1% |

*Latențele de mai sus sunt un PLAFON INFERIOR pentru rutele cu N+1: la momentul rulării, schemele
sintetice erau goale, deci munca reală per firmă lipsea din ele. Coeficienții demonstrați ai căii de
succes sunt în §4.5; reconcilierea, în §4.6.*

### 4.3 Octeți de răspuns (N=1000) — costul care NU vine din interogări

| rută | octeți | per firmă |
|---|---|---|
| `/supervizor` | 592.255 | 592 B |
| `/termene` | 359.347 | 359 B |
| `/migrare/vector` | 261.311 | 261 B |
| `/control-fiscal` | 202.163 | 202 B |
| `/tenants` | 199.013 | 199 B |
| `/migrare/solduri` | 170.311 | 170 B |
| `/migrare/plan-conturi` | 154.311 | 154 B |
| cele 5 rute de status | ~90.000 | ~90 B |

### 4.4 Portofoliul REAL — 14 firme, scheme adevărate

| rută | interog | conex | total_s | db_s | cpu_s | octeți |
|---|---|---|---|---|---|---|
| `/tenants` | 4 | 3 | 0,0050 | 0,0012 | 0,0039 | 2.935 |
| `/control-fiscal` | 5 | 3 | 0,0060 | 0,0020 | 0,0041 | 9.479 |
| `/migrare/plan-conturi` | 5 | 3 | 0,0059 | 0,0019 | 0,0040 | 2.371 |
| `/migrare/solduri` | 5 | 3 | 0,0059 | 0,0018 | 0,0040 | 2.580 |
| `/migrare/vector` | 5 | 3 | 0,0059 | 0,0018 | 0,0041 | 3.982 |
| `/termene` | 5 | 3 | 0,0066 | 0,0019 | 0,0046 | 9.633 |
| `/migrare/istoric-declaratii` | 18 | 17 | 0,0098 | 0,0044 | 0,0054 | 1.446 |
| `/supervizor` | 33 | 18 | 0,0132 | 0,0066 | 0,0065 | 8.623 |
| `/migrare/mijloace-fixe` | 60 | 31 | 0,0232 | 0,0135 | 0,0096 | 1.460 |
| `/migrare/asociati` | 60 | 31 | 0,0238 | 0,0140 | 0,0098 | 1.460 |
| `/migrare/salariati` | 60 | 31 | 0,0236 | 0,0140 | 0,0097 | 1.472 |
| `/migrare/parteneri` | 60 | 31 | 0,0252 | 0,0143 | 0,0109 | 1.474 |

**Costul real per firmă — MODELUL DEMONSTRAT, nu o medie.** Prima formă a raportului împărțea
totalul la N (`60/14 ≈ 4,3` interogări, `31/14 ≈ 2,2` conexiuni) și numea rezultatul „cost per
firmă". **Greșit:** `total/N` amestecă overheadul FIX cu costul MARGINAL, deci nu e o pantă — și
scade artificial pe măsură ce N crește. Panta se obține din două puncte, nu dintr-o împărțire.

Măsurat la N = 5 / 10 / 14 pe scheme reale (§4.5), pentru **toate cele patru rute**:

```
queries(N)     = 4 + 4*N
connections(N) = 3 + 2*N
```

Verificat: N=14 → 4 + 56 = **60 interogări**, 3 + 28 = **31 conexiuni**. Coincide exact cu
măsurătoarea independentă de pe cabinetul real din tabelul de mai sus.

**Extrapolarea la N=1000, din formula demonstrată** (nu din medii):

| rută | `queries(1000)` | `connections(1000)` |
|---|---|---|
| `/migrare/asociati` | 4 + 4×1000 = **4.004** | 3 + 2×1000 = **2.003** |
| `/migrare/mijloace-fixe` | **4.004** | **2.003** |
| `/migrare/salariati` | **4.004** | **2.003** |
| `/migrare/parteneri` | **4.004** | **2.003** |

Timpul de bază măsurat la N=14 e ~14 ms, adică ~1 ms per firmă; la 1000 de firme, **~1 s doar
timp petrecut în bază** — și e o extrapolare a unei pante măsurate, nu a unei medii.

### 4.5 CALEA DE SUCCES, pe scheme REALE — overhead fix vs cost marginal

Artefacte: `masuratori/post_p2/p3_success_path_curve.json` · `.iesire.txt`

Firme construite din `tenant_template.sql`, cu `firma_profil` completat, la **N = 5 / 10 / 14**.
Toate răspunsurile **200** — e chiar calea de succes, nu una care cade pe `except`.

| rută | N=5 | N=10 | N=14 | `BASE_QUERIES` | `QUERIES_PER_FIRM` | `BASE_CONNECTIONS` | `CONNECTIONS_PER_FIRM` |
|---|---|---|---|---|---|---|---|
| `/migrare/asociati` | 24q/13c | 44q/23c | 60q/31c | **4** | **4** | **3** | **2** |
| `/migrare/mijloace-fixe` | 24q/13c | 44q/23c | 60q/31c | **4** | **4** | **3** | **2** |
| `/migrare/salariati` | 24q/13c | 44q/23c | 60q/31c | **4** | **4** | **3** | **2** |
| `/migrare/parteneri` | 24q/13c | 44q/23c | 60q/31c | **4** | **4** | **3** | **2** |

**Liniaritatea e verificată, nu presupusă:** cu trei puncte, `BASE + PANTĂ × N` reproduce **exact**
toate trei, pentru interogări și pentru conexiuni, la toate patru rutele. De-aia s-a măsurat la
trei valori ale lui N, nu la două.

*Cifrele coincid cu măsurătoarea independentă pe cabinetul real de 14 firme din §4.4 (60q/31c).*

**Ce NU intră în aceste cifre, declarat:** `db.get_conn(schema)` execută `SET search_path` la
intrare și `RESET search_path` la ieșire, pe conexiunea brută — **înaintea** învelișului care
numără. Deci la nivelul bazei sunt **încă două instrucțiuni per conexiune de schemă**, adică ~2 în
plus per firmă. Contorul măsoară interogările **aplicației**; cifra de la nivelul bazei e mai mare.

### 4.6 RECONCILIERE sintetic vs real

| rută | `SYNTHETIC_QUERY_SLOPE` | `REAL_SUCCESS_QUERY_SLOPE` | `SYNTHETIC_CONNECTION_SLOPE` | `REAL_SUCCESS_CONNECTION_SLOPE` |
|---|---|---|---|---|
| `/migrare/asociati` | 3,0 | **4,0** | 2,0 | 2,0 |
| `/migrare/mijloace-fixe` | 3,0 | **4,0** | 2,0 | 2,0 |
| `/migrare/salariati` | 3,0 | **4,0** | 2,0 | 2,0 |
| `/migrare/parteneri` | 4,0 | 4,0 | 2,0 | 2,0 |

**Diferența nu se ascunde într-o medie: e de exact o interogare per firmă, la trei rute din patru.**

**Ce branch nu se execută**, citit din instrucțiunile capturate (`p3_success_path_curve.iesire.txt`,
secțiunea 3 — nu din citirea codului):

- pe schemă reală, `/migrare/asociati` execută, per firmă:
  `SELECT to_regclass('asociati')` **apoi** `SELECT count(*), COALESCE(sum(cota),0) FROM asociati`;
- pe schemă goală execută **doar prima**. `rezumat()` (`core/asociati_import_api.py:119–121`)
  întoarce devreme când `to_regclass` dă `NULL`. Identic la `mijloace_fixe_import_api.py:172–174`
  și `salariati_import_api.py:173–175`.
- `/migrare/parteneri` **nu are gardă `to_regclass`**: `rezumat()`
  (`core/solduri_parteneri_api.py:261`) cheamă `asigura_tabel()`, care execută
  `CREATE TABLE IF NOT EXISTS solduri_parteneri`, apoi numără. Ambele căi fac același număr de
  instrucțiuni — de-aia panta lui sintetică era deja egală cu cea reală, **și tot din cauza asta
  sonda a scris în `public`** (§3).

**Conexiunile per firmă coincid pe ambele domenii (2,0)** — acolo forma sintetică era fidelă.

**Latența sintetică a lui `/migrare/parteneri` nu se mai citează.** După ce schemele de probă au
devenit reale-dar-goale, `CREATE TABLE IF NOT EXISTS` chiar creează câte o tabelă per firmă, iar
latența sintetică urcă la 5,57 s la N=1000 — artefact al sondei, nu purtare de producție (unde
tabela există și instrucțiunea e o verificare ieftină). Pentru latență valorează §4.5 și §4.4.

---

## 5. TOPUL COSTURILOR CARE CRESC CU N, cu cauza demonstrată

### Clasa 1 — N+1 pe conexiuni și interogări (6 rute)

Ordonate după costul măsurat la N=1000:

| # | rută | la N=1000 | per firmă | cauza, la linie |
|---|---|---|---|---|
| 1 | `/migrare/parteneri` | 4004q / 2003c / 1,32 s | 4q + 2c | `main.py:2310` `for f in firme:` → `schema_tenant` (conexiune proprie) + `get_conn(schema)` + `solduri_parteneri_api.rezumat(c)` |
| 2 | `/migrare/asociati` | 3004q / 2003c / 0,99 s | 3q + 2c | `main.py:2441` → `schema_tenant` + `get_conn(schema)` + `asociati_import_api.rezumat(c)` |
| 3 | `/migrare/mijloace-fixe` | 3004q / 2003c / 0,99 s | 3q + 2c | `main.py:2540` → idem, `mijloace_fixe_import_api.rezumat(c)` |
| 4 | `/migrare/salariati` | 3004q / 2003c / 0,98 s | 3q + 2c | `main.py:2380` → idem, `salariati_import_api.rezumat(c)` |
| 5 | `/supervizor` | 2005q / 1004c / 0,50 s | 2q + 1c | `main.py:2880` `for f in ale_mele:` → `with db.get_conn() as c: schema_tenant(...)`, **o conexiune per firmă doar ca să rezolve schema și accesul** |
| 6 | `/migrare/istoric-declaratii` | 1004q / 1003c / 0,32 s | 1q + 1c | `main.py:2592` → `istoric_declaratii_import_api.rezumat(c, tid)`, o conexiune per firmă (citește din `public`, **nu deschide schema**) |

**Coeficienții din tabel sunt cei SINTETICI.** Pentru cele patru rute de import, coeficientul real
al căii de succes e **4 interogări + 2 conexiuni per firmă** (§4.5) — la trei dintre ele, cu o
interogare mai mult decât arată coloana. Proiecția corectă la N=1000 e deci
**~4.004 interogări / ~2.003 conexiuni**, nu 3.004, pentru `asociati`, `mijloace-fixe` și
`salariati`.

**Cauza e aceeași pentru primele patru, și e chiar tiparul pe care P2 l-a scos din celelalte trei
rute surori:** o buclă per firmă care deschide **două** conexiuni — una ca să afle schema, alta ca
să citească din ea. Cele trei rute vecine (`/migrare/solduri`, `/migrare/plan-conturi`,
`/migrare/vector`) au fost convertite la modelul de citire în P2; **aceste patru au rămas**.

**`/supervizor` e un caz aparte, și merită numit exact:** P1 a rezolvat partea scumpă — rezultatele
se citesc **set-based**, într-o singură interogare (`supervizor_cache.citeste`, `main.py:2899`). Ce
a rămas e o buclă **înaintea** ei, care rezolvă schema și accesul firmă cu firmă. Deci nu e o
regresie a lui P1; e o bucată pe care P1 n-a atins-o fiindcă nu era în domeniul lui.

**Cifra care doare nu e numărul de interogări, ci de CONEXIUNI.** Pool-ul are `maxconn = 10`
(implicit, `ICONTA_POOL_MAX` nesetat). O cerere cere și dă înapoi ~2.003 conexiuni, **secvențial** —
deci nu se blochează pe sine.

```
POOL_CONTENTION_RISK = UNMEASURED_BUT_PLAUSIBLE
```

Prima formă a raportului scria *„utilizatorii concurenți se serializează pe el"*. **N-am măsurat
asta.** E o consecință plauzibilă a numărului de împrumuturi din pool, dar concurența n-a făcut
parte din domeniul P3 și nu s-a executat niciun test cu cereri simultane. Rămâne o ipoteză numită,
nu un rezultat — și **nu condiționează închiderea diagnosticului**.

### Clasa 2 — payload și serializare (toate cele 12, inclusiv cele „constante")

Rutele convertite în P2 au **număr constant de interogări** și tot cresc liniar în latență:
`/control-fiscal` 0,005 → 0,050 s, `/termene` 0,005 → 0,053 s. Cauza e demonstrată de despicare:
la N=1000, **~50% din timp e în bază** (aducerea a N rânduri) și **~50% în Python** (construirea
listei + serializarea JSON).

`/tenants` e cazul curat: **4 interogări la orice N**, dar **74% din timp e CPU** — nu are ce citi
în plus, are ce serializa în plus.

`/supervizor` are cel mai mare răspuns: **592 KB la 1000 de firme**, fiindcă întoarce constatările
întregi, nu un rezumat.

*Asta e o clasă de cost pe care niciun read-model n-o rezolvă: dacă răspunsul are N elemente,
cineva tot trebuie să-l construiască, să-l serializeze și să-l trimită.*

### Ce NU crește

Cele cinci rute convertite în P2 plus `/tenants`: **numărul de interogări și de conexiuni e constant
la orice N**, confirmat din nou aici, independent de gărzile P2.

---

## 6. PROPUNEREA MINIMĂ DE REMEDIERE — **scrisă, NU implementată**

Ordonată după raport cost/beneficiu măsurat. Fiecare punct e minim prin construcție: nu cere
mecanism nou, ci folosește unul care există și e deja gardat.

### 6.1 `/supervizor` — cea mai ieftină reparație din listă

**Ce:** rezolvarea schemei și a accesului, **într-o singură interogare** pentru tot portofoliul, în
loc de o conexiune per firmă. `tenantii_userului` întoarce deja `schema_name`; bucla o recere prin
`schema_tenant` doar ca să verifice accesul — verificare pe care apartenența la cabinet o dă deja.

**Câștig măsurat (proiecție din cifrele de mai sus):** 2005q/1004c → ~5q/3c. **Efect zero asupra
prospețimii** — nu atinge modelul de citire, doar rezolvarea de schemă.

**Risc:** trebuie păstrată exact semantica de acces (o firmă la care userul n-are acces se sare, nu
se afișează). Se probează cu un test de izolare, care există deja ca tipar.

### 6.2 Cele patru rute de status — aspecte noi în modelul de citire existent

**Ce:** `asociati`, `mijloace_fixe`, `parteneri`, `salariati` devin patru aspecte în
`firma_rezumat.ASPECTE`, calculate de lucrător, citite set-based — **exact drumul deja parcurs**
pentru `solduri`, `plan_conturi` și `vector`.

**Câștig:** 4×(3004q/2003c) → 4×(5q/3c).

**Costul mutat, declarat:** patru aspecte în plus înseamnă mai multă muncă pentru lucrător și mai
multe surse de invalidare. Payloadul lor e mic (~90 B/firmă), deci clasa 2 nu se agravează.

**Obligatoriu, prin regula deja scrisă în `GARZI.md`:** fiecare aspect nou vine în același commit cu
(1) sursele în registru, (2) fixtura care activează ramura, (3) testul că sursa e observată, (4)
testul de invalidare.

### 6.3 `/migrare/istoric-declaratii` — o singură interogare, fără model nou

**Ce:** `istoric_declaratii_import_api.rezumat(c, tid)` citește din `public`, pe `tenant_id`. Se
poate cere **pentru toate firmele deodată**, cu `WHERE tenant_id = ANY(...)` și un `GROUP BY`.

**Câștig:** 1004q/1003c → ~5q/3c, fără niciun aspect nou și fără nicio dependență de prospețime.
*E cea mai mică schimbare din listă și n-are legătură cu modelul de citire.*

### 6.4 Clasa 2 (payload) — cere o decizie, nu o optimizare

Nu propun nimic tehnic aici, fiindcă întrebarea e de produs: **are un contabil nevoie de toate cele
1000 de firme într-un singur răspuns?** Variantele obișnuite — paginare, câmpuri reduse, filtrare pe
server — schimbă contractul ecranelor. La 592 KB (`/supervizor`) și 359 KB (`/termene`) merită pusă
întrebarea; la 0,05 s pentru celelalte, nu urgent.

### Ce NU propun

Cache nou, event bus, denormalizare suplimentară, atingerea advisory lockului, a fail-closed-ului
sau a semanticilor `CURENT`/`INVALIDAT`/`EROARE`. Nimic din ce e demonstrat nu cere așa ceva.

---

## 7. RISCURI DE PROSPEȚIME ȘI CONCURENȚĂ

**Prospețime.** §6.2 e singurul punct care introduce prospețime unde azi nu există: cele patru rute
citesc **acum** date proaspete direct din schema firmei. Trecerea la modelul de citire înseamnă că
vor putea arăta `invalidat`/`lipseste` — corect, dar **e o schimbare de contract al ecranului**, nu
doar de performanță. Ecranul trebuie să știe să arate starea, cum o fac deja cele cinci convertite.

**§6.1 și §6.3 nu ating prospețimea deloc** — de aceea le pun primele.

**Concurență.** `POOL_CONTENTION_RISK = UNMEASURED_BUT_PLAUSIBLE`.

Rutele din clasa 1 cer și dau înapoi ~2.003 conexiuni per cerere, la un pool cu `maxconn = 10`.
E **plauzibil** ca doi utilizatori simultani să se influențeze pe pool — dar **n-am măsurat-o**, și
nu afirm nici serializare, nici starvation, nici saturare. Concurența n-a făcut parte din domeniul
P3; ar cere un test cu cereri simultane, care nu s-a scris.

Ce se poate spune fără măsurătoare: reparațiile din §6 scad numărul de împrumuturi din pool de la
~2.003 la ~3 per cerere. Dacă riscul e real, dispare odată cu cauza; dacă nu e, reparațiile nu
strică nimic. *În ambele cazuri, decizia nu atârnă de o cifră pe care n-o am.*

**Lucrătorul.** Patru aspecte în plus cresc lotul: la 1000 de firme, backlogul complet trece de la 5
la 9 perechi per firmă. Metricile există deja (`p2_worker_remaining`,
`p2_oldest_pending_age_seconds`) — deci efectul ar fi **vizibil**, nu presupus.

---

## 8. R177 — STATUS NESCHIMBAT DE P3

Comanda cere să nu fie deschisă decât dacă măsurătoarea demonstrează **aceeași cauză**. Nu o
demonstrează, și se poate spune precis de ce:

**R177** e despre un model de citire ale cărui **dependențe au fost scrise din memorie** — o valoare
veche arătată drept `curent`. Cele șase rute din clasa 1 **n-au niciun model de citire**: citesc
direct din schema firmei, la fiecare cerere. Sunt proaspete prin construcție; defectul lor e de
**cost**, nu de adevăr.

Legătura ar apărea abia dacă se implementează §6.2 — atunci cele patru aspecte noi *ar deveni*
purtători ai clasei R177, și **de-aia regula din `GARZI.md` le cere fixtura și testul de invalidare
în același commit**.

```
R177_OPENED_BY_P3 = NO
R177_STATUS       = UNCHANGED
```

*Precizare de formulare.* Prima formă spunea, în aceeași frază, și „R177 nu se deschide în P3", și
„R177 rămâne deschisă" — două lucruri diferite scrise ca și cum ar fi unul. Corect: **R177 a fost
deschisă la 08.09.2026, ca restanță în `CONFORMITATE.md`, printr-o decizie anterioară și
independentă de P3.** P3 nu a atins-o: n-a deschis-o, n-a închis-o, n-a măsurat-o. Statusul ei
rămâne cel de dinainte, iar el se citește din registru, nu din raportul ăsta.

---

## 9. TESTE DE ACCEPTARE PROPUSE — pentru o eventuală remediere

Scrise acum, ca să nu fie inventate după implementare.

| # | test | criteriu |
|---|---|---|
| 1 | `test_p3_endpoint_query_count_toate_cele_12` | pe **toate** cele 12 rute derivate: 5 firme vs 50 → același număr de interogări **și** de conexiuni |
| 2 | `test_p3_cost_pe_cerere_nu_creste_cu_N` | numărul de interogări **și** de conexiuni per cerere **nu crește cu N** (criteriul corect: un total de împrumuturi mai mare decât `maxconn` nu e în sine un defect — pool-ul le servește secvențial) |
| 2b | `test_p3_conexiuni_simultane_sub_capacitate` — **numai dacă se scrie un test de concurență** | maximul de conexiuni ținute SIMULTAN ≤ capacitatea pool-ului, fără starvation și fără deadlock |
| 3 | `test_p3_paritate_status_import` | pentru fiecare din cele 4 rute de status: răspunsul de dinainte și de după, **întreg**, fără normalizare |
| 4 | `test_p3_supervizor_acces_neschimbat` | o firmă la care userul n-are acces **rămâne** absentă din răspuns după batching |
| 5 | `test_p3_aspect_nou_invalideaza` | pentru fiecare aspect nou: scriere în sursă → `invalidat`; scriere în sursă străină → **rămâne** `curent` |
| 6 | `test_p3_ramura_noua_e_acoperita` | regula din `GARZI.md`, aplicată: fiecare sursă nouă are fixtură și e observată |
| 7 | `test_p3_payload_declarat` | mărimea răspunsului per firmă rămâne sub un plafon scris, ca o creștere de payload să fie o decizie, nu o surpriză |

**Instrumentul există deja** — `scripts/masoara_p3.py` produce toate cifrele de care au nevoie
testele 1, 2 și 7; nu trebuie construit nimic nou ca să se poată verifica.

---

## 10. AUDITABILITATEA AFIRMAȚIILOR DE ROOT-CAUSE

`masuratori/post_p2/p3_route_callchains.txt`, generat cu
`python3 -m scripts.scan_cale_cerere --lanturi`. Pentru **fiecare** dintre cele 37 de rute care
ating portofoliul (cele 12 care cresc cu N sunt marcate `CREȘTE CU N`):

```
GET /migrare/asociati
    handler   : migrare_asociati_status()  la main.py:2437
    poarta    : cere_cabinet   -> CREȘTE CU N
    lant      : migrare_asociati_status -> tenantii_userului
        migrare_asociati_status -> tenantii_userului   apelat la main.py:2440
                                                       ·  definit la core/auth_api.py:395
```

*Rostul lui:* afirmațiile de root-cause din §5 nu mai trebuie luate pe încredere. Fiecare pas al
lanțului poartă fișierul și linia, iar artefactul e **generat**, nu scris de mână — deci se
regenerează și se compară oricând.

---

## 11. ARTEFACTUL ACCIDENTAL DIN PRODUCȚIE — eliminat, cu dovadă

`public.solduri_parteneri`, creată **de sonda mea** (§3). Dovada pre/post:
`masuratori/post_p2/p3_accidental_table_cleanup.txt`.

**Cele patru condiții cerute înainte de orice `DROP`, fiecare demonstrată:**

| condiția | dovada |
|---|---|
| nu exista înaintea probei | `OID = 307.840.147`, **mai mare** decât al tabelelor create la remedierea P2 pe 08.09 (`firma_tip` = 302.504.031), și imediat înaintea unei scheme efemere de test |
| nu conține date legitime | `ROW_COUNT = 0`; `pg_stat`: `n_tup_ins = 0`, `n_tup_upd = 0`, `n_tup_del = 0`, `n_live_tup = 0` — **n-a primit niciodată un rând** |
| nimic nu depinde de ea | zero view-uri/reguli, zero chei străine către ea, zero triggere; singurul index e propria cheie primară |
| fără cod / job care s-o folosească | zero referințe în `*.py`, `*.sql`, `*.js` — în afara a două **comentarii** din chiar sonda care a creat-o, care descriu incidentul. Joburile de fundal sunt module Python din același corpus, deci acoperite de aceeași căutare |

**Executat:** `DROP TABLE public.solduri_parteneri;`

**Post-ștergere, verificat:** `to_regclass('public.solduri_parteneri') = None`, zero obiecte rămase
cu acest nume în `public`, iar **cele 20 de tabele `solduri_parteneri` din schemele de tenant sunt
neatinse** — acelea sunt cele legitime.

```
ACCIDENTAL_TABLE_FOUND            = YES
ACCIDENTAL_TABLE_PROVEN_TEST_ONLY = YES
ACCIDENTAL_TABLE_CLEANUP          = REMOVED
```

Cauza e reparată în instrument (schemele sintetice sunt reale-dar-goale), deci nu se mai poate
repeta.

---

## 12. CE NU ACOPERĂ ACEST DIAGNOSTIC

- **Doar `GET`-uri de cabinet, fără parametru de cale.** Un `POST` de portofoliu ar schimba date, iar
  o măsurătoare care scrie nu se poate repeta identic.
- **O singură cerere pe rând, fără concurență.** `POOL_CONTENTION_RISK = UNMEASURED_BUT_PLAUSIBLE`
  — argumentat din numărul de împrumuturi din pool, **nemăsurat**. N-a făcut parte din domeniul P3
  și nu condiționează închiderea diagnosticului.
- **Latențele sintetice ale rutelor cu N+1 sunt plafoane inferioare** — schemele sintetice sunt
  **reale, dar goale**, deci munca per firmă e mai mică decât în producție. Coeficienții căii de
  succes vin din §4.5 (scheme reale din `tenant_template.sql`), iar costul real per firmă din §4.4.
- **Cele 25 de rute de portal** n-au fost măsurate: poarta lor e `cere_client`, deci văd o firmă.
- **Nu s-a măsurat frontendul** — câte cereri face un ecran la deschidere. Instrumentul are deja
  `--ecrane` pentru asta; n-a intrat în domeniul cerut.
