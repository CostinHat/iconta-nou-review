# R68 — IZOLAREA BAZEI SUITEI DE TESTE FAȚĂ DE PRODUCȚIE

*11.09.2026. Decizia arhitectului din aceeași zi, varianta (c): bază proprie, izolată.*

---

## 1. DE CE

Până azi, `conftest.py` sursa `~/.iconta/db.env` în `os.environ` **înaintea colectării**, deci
suita primea DSN-ul de PRODUCȚIE și scria în baza reală. Izolarea era o **convenție**: fiecare test
trebuia să-și facă `rollback`.

Pe 10.09 convenția s-a rupt. Un rând a rămas în `tenant_001.salariu_istoric` (salariat 53,
`2026-06-01`, `7000.0`, scris la `23:54:38`) și a făcut poarta roșie la rularea următoare:
`rand_fluturas` întoarce exemplarul înghețat când luna e emisă, iar mutația testului scria de a
doua oară valoarea care era deja acolo — deci aserțiunea lui anti-vacuum s-a aprins, pe drept.

**Producătorul exact nu e cunoscut, și tocmai ăsta e argumentul:** o frontieră care depinde de
disciplina fiecărui test nu e o frontieră.

## 2. CE S-A CONSTRUIT

### 2.1 Bariera, la PostgreSQL

Nu în Python. Rolul cu care rulează suita **nu are `CONNECT`** pe baza de producție:

```
iconta_v2 ACL, înainte:  =Tc/postgres | postgres=CTc/postgres | iconta_user=C/postgres
iconta_v2 ACL, după:     =T/postgres  | postgres=CTc/postgres | iconta_user=Cc/postgres
```

PUBLIC a rămas doar cu `TEMP`. `iconta_user` a primit `CONNECT` **explicit**, iar ordinea a contat:
ACL-ul măsurat înainte arăta că aplicația se conecta *prin* `CONNECT`-ul lui PUBLIC, deci revocarea
fără grantul prealabil ar fi tăiat aplicația de la baza ei.

Dovada, în cuvintele serverului:

```
iconta_test_user -> iconta_test : SE CONECTEAZĂ
iconta_test_user -> iconta_v2   : FATAL: permission denied for database "iconta_v2"
```

Ambele direcții contează. Fără prima, refuzul n-ar dovedi frontiera — ar dovedi o parolă greșită.

### 2.2 A doua încuietoare, în Python

`core/mediu_test.py` oprește suita **înainte de colectare** dacă nu se poate dovedi că mediul e de
test. Fail-closed în înțelesul tare: **lipsa unei informații nu e permisiune.**

Un motiv de refuz e un **obiect cu câmpuri** (`Motiv(cod, detaliu)`), iar excepția poartă `coduri`
și `cale_remediu` — ca gărzile să asertere pe structură, nu pe proza mesajului. Namedtuple, nu
dicționar: un dict cu cheia `motiv` ar fi fost citit de garda afirmațiilor tipate drept afirmație
despre datele unei firme.

Măsurat, pe patru configurații — toate ies cu **cod 4 și ZERO teste colectate**:

| configurație | rezultat |
|---|---|
| DSN de producție | refuz, numește baza și rolul |
| fără `test.env`, mediu nedeclarat | refuz: *„nu se cade pe baza de producție"* |
| fără `test.env`, DSN de producție în mediu | refuz |
| ambiguă (`DATABASE_URL`≠`DB_NAME`) | refuz: *nu se știe care ajunge la conexiune* |

**Nu există cădere pe producție.** Varianta „baza de test indisponibilă → folosim producția" nu e
implementată nicăieri și nu trebuie să fie: exact acolo s-ar pierde tot.

### 2.3 Ce a trebuit reparat ca suita să poată rula izolat

- **`tenant_template.sql` numea un proprietar.** 35 de linii `ALTER ... OWNER TO iconta_user`; sub
  orice alt rol, fiecare cere apartenență la rolul ăla. Leacul evident — să i-o dau — ar fi
  desființat least-privilege. `parametrizeaza_template` pune `OWNER TO CURRENT_USER`: în producție
  aplicația rulează **ca** `iconta_user`, deci e literă cu literă același lucru.
- **Două teste își făceau singure `replace("TENANT_PLACEHOLDER", ...)`** — logică paralelă cu
  `parametrizeaza_template`, de-aia reparația din sursa unică n-avea cum să ajungă la ele.
- **Două teste își citeau singure `~/.iconta/db.env`.** Bariera de rol nu le acoperea: acreditările
  de acolo sunt ale lui `iconta_user`, care *are* `CONNECT`. Ținea doar prin `setdefault`, adică
  iar prin convenție. Acum nu mai citesc fișierul deloc. Al doilea face `DROP SCHEMA ... CASCADE`.

### 2.4 Gazda de producție, declarată

`sonda_web.GAZDA_PRODUCTIE = "https://iconta.eu"`, păzită de `core/test_gazda_productie.py`.
Garda compară pe **host**, nu pe subșir. Sonda deadman rămâne pe procesul **local** — un `200` prin
nginx poate veni dintr-un cache sau de la alt upstream, deci ar putea fi verde peste un proces mort.

## 3. ACCEPTANȚA

```
TEST_DB_IS_DISTINCT_FROM_PRODUCTION=PASS
TEST_CREDENTIALS_DISTINCT=PASS
TEST_PRODUCTION_DSN_GUARD=PASS
TEST_PRODUCTION_WRITE_ATTEMPT_FAILS_CLOSED=PASS
TEST_EXPLICIT_COMMIT_CANNOT_PERSIST_TO_PRODUCTION=PASS
TEST_SECOND_CONNECTION_CANNOT_PERSIST_TO_PRODUCTION=PASS
TEST_MISSING_ROLLBACK_CANNOT_PERSIST_TO_PRODUCTION=PASS
```

Plus patru probe de **calibrare**, fiindcă o gardă care refuză orice trece la fel de ușor ca una
care acceptă orice.

**Non-contaminare, măsurată pe 1087 de tabele:** în cele 26 de minute ale suitei izolate s-au mișcat
**două** — `public.cron_batai` și `public.metrici_sanatate`, bătăile aplicației vii. Niciun tabel de
firmă, nicio schemă `tenant_*`.

```
PRODUCTION_DB_CHANGED_BY_ISOLATED_SUITE=NO
FULL_SUITE=5427 trecute · 0 roșii · 11 sărite · 14 xfailed · exit 0
```

Drumul până aici, fiindcă numărul final nu spune nimic singur: **145 roșii + 345 erori** la prima
rulare → **16 + 43** după reparația proprietarului și un reset făcut corect → **2** (una trecătoare,
una adevărată — sonda web prinsese căderea reală a producției) → **0**.

## 4. CE NU ACOPERĂ R68

**Procesul.** Suita rulează ca `costin`, la fel ca serviciul (`User=costin`), iar sudoers are
`NOPASSWD` pe `systemctl restart iconta-nou` — de care depinde publicarea. Deci capabilitatea de a
controla procesul viu **există**, chiar dacă inventarul mecanic nu găsește niciun apelant din suită.
E **R69**, hardening, temă separată.

**Nu R69 a produs incidentul din 11.09.** Atribuirea mea inițială a fost greșită și e corectată în
`masuratori/r68/PROCESS_RESTART_ATTRIBUTION.txt`: `unattended-upgrades` a actualizat `libc6`, iar
`needrestart` a repornit 20 de servicii, printre care `iconta-nou`. Lanțul real:

1. suita a scris 12 firme-fantomă în producție (00:46–00:58, **înainte** de R68);
2. `libc6` actualizat la 06:04, `needrestart` a repornit tot;
3. `iconta-nou` a refuzat să pornească — P2 fail-closed, `37 proiecții pentru 49 firme active`;
4. indisponibilitate până la 07:52, când dezactivarea celor 12 le-a scos din numărătoare.

**Defectul latent era al suitei. Declanșatorul, nu.** P2 a funcționat exact cum trebuie: a refuzat
să servească peste o infrastructură inconsistentă.

## 5. CE RĂMÂNE DESCHIS, DECLARAT

- `EXACT_LEAK_PRODUCER_IDENTIFIED=NO` — producătorul rândului 53 nu e numit. `core/sonda_scrieri.py`
  e montat (declanșator PostgreSQL, se aprinde cu `ICONTA_SONDA_SCRIERI=1`) și așteaptă reproducerea
  în mediul izolat. Discriminatorul vine pe gratis: rândul de jurnal trăiește în aceeași tranzacție
  cu scrierea observată — dacă a supraviețuit, scrierea a fost comisă.
- `PREVIOUS_CLEANUP_DOCUMENTED=PARTIAL` — **limitare permanentă**. Cele 16 exemplare șterse pe 11.09
  n-au instantaneu per rând: dumpul de 03:00 e de **după** ștergere. Predicatul și numărătoarea pe
  schemă sunt tot ce există.
- Neatinse, prin decizie: rândul 53, rândul 63, cele două corecții orfane, cele 12 firme
  (`DISABLED`, nici șterse, nici reactivate).

## 6. INSTANȚE DE METODĂ, ADUNATE AICI

- **Poarta care se uită în altă parte.** Am verificat `iconta.ro` după fiecare pas al frontierei.
  Aplicația e pe `iconta.eu`. Patru verzi la rând despre o lume pe care n-o vedeam, două ore în care
  aplicația era 502. Garda din §2.4 e scrisă din instanța asta.
- **Proba care demonstrează o barieră nu se poate rula unde bariera lipsește** — acolo *ea e*
  încălcarea. Am rulat probele de scriere înainte de frontieră și am lăsat `public.sonda_izolare` cu
  două rânduri comise în producție. Reparat: cele patru probe refuză înainte de orice conexiune.
- **Cheia `motiv` a aprins un gard a treia oară** (P4 → `de_ce`, `gdpr_cerere` → tuplu, acum
  `amprenta_productie` → steagul `md5_omis`).
- **`to_regclass` rezolvă un TABEL, nu o schemă.** Prima formă a interogării de incident răspundea
  că nici `tenant_001` n-are schemă. Un răspuns greșit cu încredere.
- **Reparația în sursa unică nu ajunge la cine are logică paralelă** — de-aia 43 de erori au rămas
  concentrate într-un singur fișier după ce „reparasem" proprietarul.
- **Un reset care pică tăcut** — `DROP OWNED BY` pe 1086 de tabele depășește `max_locks_per_transaction`;
  restaurarea de după a lovit 7655 de obiecte existente. Baza nu fusese golită, iar un baseline luat
  pe ea ar fi măsurat reziduul rulării dinainte.
