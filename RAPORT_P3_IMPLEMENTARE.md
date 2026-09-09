# RAPORT P3 — IMPLEMENTARE

*09.09.2026. Baza: `7d921282` (închiderea diagnosticului P3). Valul A: `e7ce0c2e`. Valul B:
`0f0a135a`. Fiecare val a trecut poarta separat, cum s-a cerut.*

Diagnosticul P3 a numit șase rute interactive al căror cost creștea cu numărul de firme din
portofoliu. Raportul ăsta spune ce s-a făcut cu ele, cu ce s-a măsurat, ce a picat pe drum și ce
NU acoperă.

---

## 1. VERDICTELE, întâi

```
QUERY_COUNT_WITH_N                = CONSTANT   (12 rute din 12)
CONNECTION_COUNT_WITH_N           = CONSTANT   (12 rute din 12)
DYNAMIC_SQL_COMPLEXITY_WITH_N     = CONSTANT
PER_TENANT_REQUEST_DB_WORK        = 0

DYNAMIC_UNION_ALL_BYPASS_USED     = NO
SQL_COMPLEXITY_SLOPE_WITH_N       = 0

STALE_AS_CURRENT_COUNT            = 0          (măsurat, 7 ecrane din 7)
UNKNOWN_AS_EMPTY_COUNT            = 0          (măsurat, 7 ecrane din 7)
UNKNOWN_AS_NO_COUNT               = 0          (măsurat, 7 ecrane din 7)

DATA_PARITY                       = PASS       (14 firme reale, toate CURENT, zero diferențe)
INTENTIONAL_PRESENTATION_CORRECTION = YES

P2_REOPENED                       = NO
P2_PRESENTATION_CORRECTNESS_FIX   = YES
P2_CONTRACT_DEFECT_FOUND          = NO
```

---

## 2. CE S-A SCHIMBAT, cu cifrele de dinainte și de după

Toate măsurate prin **cererea HTTP întreagă**, nu prin funcția izolată — O(N)-ul stătea de fiecare
dată în dependențele rutei, nu în corpul ei. Curba: `N = 5 · 50 · 100 · 250 · 500 · 1000`, liniară
pe toate șase punctele.

### Valul A — două rute set-based (`e7ce0c2e`)

| ruta | înainte (N=1000) | după | panta interogări | panta conexiuni |
|---|---|---|---|---|
| `/migrare/istoric-declaratii` | 1.004 q · 1.003 c · 349,1 ms | **5 q · 3 c · 19,5 ms** | 1,0 → **0** | 1,0 → **0** |
| `/supervizor` | 2.005 q · 1.004 c · 545,8 ms | **5 q · 4 c · 38,9 ms** | 2,0 → **0** | 1,0 → **0** |

`/migrare/istoric-declaratii` chema `rezumat()` per firmă, fiecare cu conexiunea ei din pool.
`rezumat_lot()` întreabă **aceeași** sursă (`public.declaratii_depuse`, `sursa='migrare'`) o singură
dată, cu `= ANY(...)` și `GROUP BY`, pe aceeași conexiune pe care s-a citit deja portofoliul. Nu e
cache și nu schimbă prospețimea: e aceeași citire, făcută o dată.

`/supervizor` cerea schema **per firmă** prin `schema_tenant` — o conexiune și două interogări
fiecare — deși `tenantii_userului` filtrează pe exact aceleași reguli și o are deja în rând.

### Valul B — patru rute pe modelul de citire (`0f0a135a`)

| ruta | înainte (N=1000) | după | panta interogări | panta conexiuni |
|---|---|---|---|---|
| `/migrare/parteneri` | 4.004 q · 2.003 c · 2.005,9 ms | **5 q · 3 c · 48,0 ms** | 4,0 → **0** | 2,0 → **0** |
| `/migrare/asociati` | 3.004 q · 2.003 c · 1.010,3 ms | **5 q · 3 c · 79,8 ms** | 3,0 → **0** | 2,0 → **0** |
| `/migrare/mijloace-fixe` | 3.004 q · 2.003 c · 1.008,5 ms | **5 q · 3 c · 46,0 ms** | 3,0 → **0** | 2,0 → **0** |
| `/migrare/salariati` | 3.004 q · 2.003 c · 1.010,5 ms | **5 q · 3 c · 42,0 ms** | 3,0 → **0** | 2,0 → **0** |

**De ce modelul de citire, și nu altceva.** Datele celor patru straturi stau în schema FIECĂREI
firme, nu în `public` cu `tenant_id` — deci nu există, ca la valul A, un `GROUP BY` care să le
adune. Singurul mecanism care face munca per-firmă să dispară din calea cererii e modelul de citire
P2, construit anume pentru ecranele astea și folosit deja de rutele surori `/migrare/solduri` și
`/migrare/plan-conturi`. **Niciun al doilea mecanism de cache n-a fost inventat.**

**Ce s-a refuzat, și de ce.** Un `UNION ALL` construit dinamic peste cele N scheme ar fi dat *o
singură* interogare pe *o singură* conexiune — deci `AFTER_QUERY_SLOPE = 0` și
`AFTER_CONNECTION_SLOPE = 0`, literă cu literă. Dar textul SQL, numărul de ramuri și munca de
planificare cresc cu N, deci latența ar fi crescut mai departe: criteriul trecut fără ca problema
să fie rezolvată. `DYNAMIC_SQL_BRANCHES_PER_FIRM = FORBIDDEN`.

### Valul C — verificarea încrucișată

Nu o listă de rute scrisă de mână: `scripts/masoara_p3.py` **derivă** din cod (AST) rutele care
sunt `GET`, cer autentificare de cabinet și ating portofoliul. A găsit **12**. Toate sunt acum
constante de la N=5 la N=1000:

```
/control-fiscal · /migrare/asociati · /migrare/istoric-declaratii · /migrare/mijloace-fixe
/migrare/parteneri · /migrare/plan-conturi · /migrare/salariati · /migrare/solduri
/migrare/vector · /supervizor · /tenants · /termene
        toate 5q/3c   (supervizor 5q/4c · tenants 4q/3c)
```

Pe portofoliul real (14 firme, scheme adevărate): fiecare rută sub 12 ms, între 1,4 și 9,6 KB.

Ce **crește** legitim cu N e doar corpul răspunsului (de la ~0,9 KB la N=5 până la ~592 KB la
N=1000 pe `/supervizor`) și timpul de serializare al lui. Munca de bază de date per firmă în calea
cererii e zero.

---

## 3. CONCURENȚA — și cifra care nu convine

`scripts/masoara_concurenta.py`, N=1000 firme, server propriu (`uvicorn` pe port liber, **nu**
procesul de producție), 20 de cereri per nivel.

| rută | k | p50 | p95 | p99 | conex. simultane | erori |
|---|---|---|---|---|---|---|
| `/supervizor` | 1 | 55,8 ms | 82,8 | 96,2 | 1 | 0 |
| | 2 | 124,8 | 182,0 | 223,5 | 2 | 0 |
| | 5 | 358,9 | 417,5 | 417,7 | 5 | 0 |
| | 10 | 754,6 | 783,1 | 786,3 | **10** | 0 |
| `/migrare/parteneri` | 1 | 60,5 | 98,4 | 101,3 | 1 | 0 |
| | 10 | 787,7 | 802,3 | 804,1 | **10** | 0 |
| `/control-fiscal` | 1 | 70,4 | 114,3 | 127,7 | 1 | 0 |
| | 10 | 832,6 | 925,5 | 932,4 | 9 | 0 |

**Zero erori, zero expirări, zero blocaje, toate 200**, pe toate nivelele și toate rutele.

**Dar:** la 10 cereri simultane, conexiunile simultane ating **exact 10**, adică
`ICONTA_POOL_MAX = 10`. Pool-ul e fix saturat — rezervă zero. O a unsprezecea cerere de portofoliu
ar aștepta o conexiune liberă. Iar latența crește aproape liniar cu `k` (55,8 → 754,6 ms, adică
13,5× pentru de 10 ori mai multe cereri), deci **debitul e practic plat**: cererile se servesc
aproape secvențial.

*Asta nu e o regresie a lui P3 — dimpotrivă, înainte fiecare cerere lua 1.003–2.003 conexiuni pe
rând și ținea pool-ul mult mai mult. E o proprietate a configurației de azi, măsurată acum fiindcă
înainte n-a fost.* Nu se propune nimic aici: mărirea pool-ului ar fi tocmai „ascunderea prin
mărirea poolului" pe care ai interzis-o, iar cauza serializării (un singur proces, GIL pe
serializarea a sute de KB) e altă discuție decât P3.

**Instrumentul își probează afirmația.** Calibrare în ambele direcții, cu mutație pe propriul mod
de eșec: (a) 6 conexiuni ținute deodată → trebuie văzute ≥6 (văzute 6); (b) aceleași 6 una după
alta → trebuie văzute <6 (văzute 1). Fără (b), un contor *cumulat* ar fi trecut (a) fără să
clipească, iar „pool-ul n-a fost atins" ar fi fost o minciună liniștitoare.

---

## 4. UN NECUNOSCUT NU SE ROTUNJEȘTE LA „ȘTIU CĂ NU"

Modelul de citire întoarce, de la P2 încoace, o `prospetime.stare` pentru fiecare firmă. **Stratul
de ecran o ignora.** Deci o firmă al cărei rezumat încă nu fusese calculat arăta identic cu una
măsurată și găsită goală: *„fără parteneri încă", „de încărcat"*. Un necunoscut prezentat ca un nu
hotărât — interdicția 32 / R39 —, pe **șapte** ecrane.

Cele patru stări își au acum randarea lor, pe toate șapte:

| stare | rând | insignă |
|---|---|---|
| `curent` + are date | valoarea (ex. „34 parteneri importați") | ✓ gata |
| `curent` + gol | „fără parteneri încă" — **aici e un fapt măsurat** | de încărcat |
| `invalidat` | „se recalculează" | se recalculează |
| `lipseste` / niciodată calculat | „încă necunoscut" | de calculat |
| `eroare` | „temporar indisponibil" | indisponibil |

Sumarul nu mai topește necunoscutul în numitor: *„1 firme au parteneri · 1 fără · 4 încă
necunoscute"* în loc de *„1 din 6"*.

Corectat pe toate cele șapte ecrane care citesc modelul, **inclusiv** `/migrare/solduri`,
`/migrare/plan-conturi` și `/migrare/vector` — autorizat explicit ca
`P2_PRESENTATION_CORRECTNESS_FIX`. Zero linii de logică P2 atinse: nici algoritmul, nici contractul
de prospețime, nici invalidarea, nici blocajul, nici recalcularea.

### Garda a prins două defecte în chiar implementarea asta

Amândouă erau tocmai clasa pe care venise s-o închidă:

1. **`starePros` cădea implicit pe „curent"** când câmpul lipsea. O firmă pe care modelul n-a
   calculat-o NICIODATĂ apărea ca măsurată și goală — defectul reintrodus prin valoarea implicită.
   Acum lipsa câmpului se citește ca „nu se știe".
2. **Contorul de sus număra firmele `invalidat`** printre cele „cu parteneri", fiindcă ele păstrează
   în răspuns ultima valoare cunoscută. Rândul o arăta corect ca „se recalculează"; **agregatul o
   mințea.** Contoarele filtrează acum pe `seStie(f) && f.are_X`.

### Cum sunt probate

`core/test_p3_val_b.py` — **48 de probe**: șase aserțiuni × șapte ecrane, plus sumarul pe cele șase
care au unul. Rulează modulele JS **reale**, în chromium, prin cererea reală a fiecărui ecran, și
asertează pe **arborele de randare**.

Proprietatea apărată nu e „scrie «încă necunoscut»" — aia e o alegere de cuvinte. E **DISTINCȚIA**:
stările trebuie să producă randări diferite între ele, iar niciuna dintre cele de neștiut n-are voie
să coincidă cu «măsurat și gol». *Se compară randări între ele, nu randări cu șiruri* — deci garda
supraviețuiește oricărei reformulări și cade exact când semantica se pierde.

```
MISSING_IS_NOT_RENDERED_AS_EMPTY          PASS   7/7 ecrane
NEVER_COMPUTED_IS_NOT_RENDERED_AS_EMPTY   PASS   7/7
INVALIDATED_IS_NOT_RENDERED_AS_CURRENT    PASS   7/7
ERROR_IS_NOT_RENDERED_AS_EMPTY            PASS   7/7
CURRENT_EMPTY_REMAINS_EMPTY               PASS   7/7
```

Prima formă proba **un singur** ecran și lăsa restul „prin implementare comună" — adică pe cuvânt.
Ecranele nu sunt identice: `plan-conturi` n-are `are_*`, are o cifră; `vector` își compune
subtitlul din alte câmpuri. *„Aceleași funcții ajutătoare" e o ipoteză despre cod, nu o proprietate
a ecranului.*

---

## 5. PARITATE

Pe definiția cerută: **pentru firmele CURENT, valoarea funcțională dinainte și cea de după trebuie
să fie identice.** 14 firme reale, toate `curent`, **zero diferențe**, pe toate cele șase rute.

Egalitatea de octeți pică pe drept și nu e criteriul: câmpul `prospetime` e nou, iar pentru
`MISSING`/`INVALIDATED`/`ERROR` reprezentarea nouă diferă **intenționat** de cea veche, fiindcă cea
veche era semantic greșită. *A numi asta „paritate picată" ar însemna să aperi tocmai defectul.*

Instantaneele de dinainte au fost capturate **înainte** de fiecare patch: paritatea nu se poate
măsura după faptă.

---

## 6. DEPENDENȚELE SUNT MĂSURATE, NU SCRISE

Cele patru aspecte noi și-au primit tabelele-sursă din măsurătoare, nu din memorie —
`scripts/scan_dependente.py`, calibrat în trei direcții (vede o citire reală · nu inventează pe o
citire absentă · PLAN ratează ce e într-o funcție plpgsql, iar STAT prinde). Pe toate cele 20 de
firme reale, **zero dezacorduri** între cele două instrumente:

```
parteneri      declarat: solduri_parteneri   măsurat: solduri_parteneri   (20/20 firme)
salariati      declarat: salariati           măsurat: salariati           (20/20)
asociati       declarat: asociati            măsurat: asociati            (20/20)
mijloace_fixe  declarat: mijloace_fixe       măsurat: mijloace_fixe       (20/20)
```

600 de triggere pe 20 de firme, `verifica_infrastructura` → `ok`, 0 probleme.

**Acoperirea invalidării e probată, nu declarată.** `core/test_dependente_ramuri.py` cere ca fiecare
sursă din registru să fie atinsă de o ramură măsurată. A **respins** prima formă: `solduri_parteneri`
era declarată și neatinsă. Cauza: `ASPECTE_MASURATE` era o listă scrisă de mână lângă registru, care
rămăsese în urmă. E acum **derivată** din registru (`tuple(FR.ASPECTE)`) — un aspect nou intră
automat sub gardă, iar dacă citește o tabelă nedeclarată, direcția a doua a gărzii îl prinde.

---

## 7. POARTA A RESPINS DE PATRU ORI, ȘI DE FIECARE DATĂ A AVUT DREPTATE

Se scriu fiindcă un raport din care lipsesc respingerile descrie o muncă pe care n-am făcut-o.

1. **`test_supervizor`** — ciotul din test întorcea o firmă fără `schema_name`, deci ruta nouă o
   sărea. Prima mea probă de echivalență comparase cele două căi „pe portofoliul real" — dar
   portofoliul ăla e al unui `admin_firma`, iar `tenantii_userului` are **trei** ramuri de SQL, una
   per rol. *Am ales un rol și i-am spus „real".* Reparat în ambele direcții: ciotul poartă forma pe
   care funcția reală chiar o întoarce, iar o gardă nouă execută toate trei ramurile
   (superadmin / admin_firma / legat prin `user_tenants`) pe date construite anume, într-o
   tranzacție care se dă înapoi.
2. **`test_tenant_stergere`** — clichetul de orfani a urcat 69 → 74. Cauza, măsurată nu ghicită:
   secvența `tenants` era la 83.918, deci firma `83615` din rândurile orfane era una din firmele
   mele sintetice; lucrătorul P2 **viu** luase un lot înainte de curățenie și și-a scris rezultatele
   înapoi după ea. *Un ham de măsurat care lasă baza mai murdară decât a găsit-o nu e un instrument,
   e o scurgere.* `curata` are acum o a doua trecere, după comitere, care se reia cât timp mai apar
   rânduri și **ridică** dacă fereastra nu se închide.
3. **`test_garzi_pe_text`** (METODA §23) — aserțiunea care cerea `schema_name` stătea într-o buclă:
   pe listă goală n-ar fi asertat nimic. Rescrisă pe mulțimi calculate, cu premisa anti-vacuu lipită
   de ea.
4. **`test_dependente_ramuri`** — §6 de mai sus.

Plus o greșeală de execuție a mea, fără legătură cu codul: am lansat din neatenție **două porți în
paralel**, iar amândouă scriau în același `/tmp/precommit_pytest.log`. Logul portii care a trecut a
afișat linia de sumar a celeilalte („2 failed"), deși propriul ei pytest ieșise 0. *Un log contaminat
nu e o dovadă* — de aceea am rulat suita din nou, curat, pe commitul valului A:
`masuratori/p3/wave_a_suita.txt`, **4278 passed, 0 failed, EXIT_CODE=0**.

---

## 8. CE NU ACOPERĂ RAPORTUL ĂSTA

*Se scrie ca să fie o alegere, nu o omisiune.*

- **Concurența e măsurată pe un singur proces de aplicație**, pe `127.0.0.1`, fără rețea reală și
  fără mai mulți lucrători `uvicorn`. Producția poate arăta altfel; ce e măsurat aici e pool-ul unui
  proces.
- **Lucrătorul de fundal rulează** în timpul măsurătorii de concurență, iar conexiunile lui intră în
  numărătoare — fiindcă și în producție intră. N-a fost oprit: o măsurătoare cu el oprit ar fi fost
  mai curată și mai puțin adevărată.
- **Costul s-a mutat, nu a dispărut.** Modelul de citire plătește la scriere: o firmă care se
  schimbă des se recalculează des. Ce s-a câștigat e că **cererea interactivă nu mai plătește pentru
  portofoliu**. Backlogul lucrătorului e observabil (`p2_worker_*`, `p2_oldest_pending_age_seconds`),
  dar SLA-ul lui nu e obiectul lui P3.
- **Cele 20 de firme reale sunt un portofoliu mic.** Curbele până la N=1000 sunt pe firme sintetice
  cu schemă reală dar goală; calea de succes (cu date) e măsurată separat, pe scheme construite din
  `tenant_template.sql`. Domeniul fiecărei cifre e scris lângă ea în artefacte.
- **`plan-conturi` n-are sumar agregat**, deci proba de sumar nu-l acoperă — n-are ce acoperi.

---

## 9. ARTEFACTE

Fiecare poartă `COMMIT=`, `COMMAND=`, `EXIT_CODE=`.

```
masuratori/p3/wave_a_inainte.json      curba + corpurile reale, ÎNAINTE de valul A
masuratori/p3/wave_a_dupa.json         aceleași, după
masuratori/p3/wave_a_suita.txt         suita întreagă pe commitul valului A (4278 passed)
masuratori/p3/wave_b_inainte.json      curba + corpurile reale, ÎNAINTE de valul B
masuratori/p3/wave_b_dupa.json         aceleași, după
masuratori/p3/wave_b_paritate.txt      paritatea pe stări, cele patru rute
masuratori/p3/wave_c_curba.txt         măturarea peste toate cele 12 rute derivate din cod
masuratori/p3/concurenta.txt           2/5/10 simultane + calibrarea instrumentului
masuratori/p3/concurenta.json          aceleași, structurat
masuratori/p3/concurenta_uvicorn.log   jurnalul serverului de probă
masuratori/p2/dependente_masurate.json matricea de dependențe, remăsurată cu cele patru aspecte noi
```

Instrumente: `scripts/masoara_val.py` (înainte/după/paritate pe stări) · `scripts/masoara_p3.py`
(rute derivate din cod, DB/CPU separate) · `scripts/masoara_concurenta.py` (nou, calibrat) ·
`scripts/scan_dependente.py`.

Gărzi noi: `core/test_p3_wave_a.py` (8) · `core/test_p3_val_b.py` (48).
