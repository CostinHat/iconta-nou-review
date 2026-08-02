# GARZI.md — registrul gardurilor

**Ce e:** indexul mecanismelor care prind defecte automat, pe categorii de eșec.
**De ce:** gardurile au apărut reactiv, după fiecare bug, în patru locuri diferite. Fără un
index, nimeni nu poate răspunde la *„câte mai lipsesc"* — iar un gard lipsă e invizibil
exact ca defectul pe care ar fi trebuit să-l prindă.

**Se actualizează** în același commit cu gardul livrat. Registru stale = fals sentiment de
acoperire.

---

## Ce înseamnă „gard"

Un mecanism e gard doar dacă îndeplinește toate:

1. **Rulează automat** — în suită, în verificator, sau la runtime. Un document nu e gard.
2. **Pică pe defect** — dovedit prin mutație: strici lucrul, gardul devine roșu.
3. **Trece pe cod corect** — un gard cu fals-pozitiv se dezactivează și moare.
4. **Spune cauza** — „a picat ceva" nu ajută; mesajul poartă fișierul, valoarea, motivul.

Punctul 2 nu e formal. Pe 27.07 o gardă a „picat pe mutant" în timp ce crăpa cu `NameError`
— pica pe orice, deci nu testa nimic. **Mutația verifică MOTIVUL eșecului, nu doar eșecul.**

---

## Unde trăiesc gardurile

| Loc | Ce acoperă | Când rulează |
|---|---|---|
| suita pytest (1277 teste, 133 fișiere) | logică, schemă, semnături, contracte | la dev, înainte de commit |
| `verificator_conformitate.py` | Design System, frontend (28 gardieni) | la dev, TOTAL 0 obligatoriu |
| `core/verificatoare.py` | echilibru notă/balanță, TVA pe cotă, trezorerie | în aplicație, pe date reale |
| `core/control_incrucisat.py` | D112/D300/D390 vs evidență, cotă TVA | în aplicație, semafor |
| `core/cron.py` | eșecul joburilor de fundal | în producție, la fiecare rulare |

---

## Categoriile de eșec

Legenda stării: **ACOPERIT** / **PARȚIAL** / **LIPSĂ**

### 0. Mascarea erorii (transversal — cauza rădăcină)
**Eșec:** `except` care întoarce default gol; eroarea nu ajunge nicăieri; un query rupt
produce zero rânduri, iar declarația iese validă structural și goală.
**Stare: ACOPERIT.**
- `core/d406.py` — 6 măști scoase (27.07), zero rămase. Fiecare cauză cu mesajul ei.
- `d112/d300/d390` — `except: return 0` scoase (27.07), regula în `numere.numar_fiscal`.
- Rămân 2 în `core/jurnal_api.py:84,141` — pe scrierea în `ai_corectii`. Clasă mai blândă
  (nu strică nota contabilă, pierde tăcut date de învățare), dar tot tăcere.
- ACOPERIT: `core/test_masti.py` (27.07) — scan AST pe tot repo-ul; orice `except` cu corp
  mut peste un query pică. Regula: **înghițirea e permisă, tăcerea nu** — handlerul trebuie
  să spună ce a eșuat (`observare.esec_secundar`) sau să poarte marcajul `# MASCA MOTIVATA:`
  cu explicația. Dovedit prin mutație pe cod real.
- Cele 15 măști peste query din `main.py` și `jurnal_api.py` (audit_log, metrici, precompletare
  ANAF, învățare AI) sunt acum zgomotoase. Nu li s-a schimbat comportamentul: efectul secundar
  tot nu oprește operația principală — dar lasă urmă.
- LIMITĂ DECLARATĂ: acoperă doar măștile peste query. Cele peste conversii numerice sunt
  tratate separat (`numere.numar_fiscal`). Nu verifică dacă eticheta e corectă.

### 1. Intrare date
**Eșec:** câmp lipsă → NULL → 0; import duplicat; valoare cu virgulă zecimală devenită 0;
cotă TVA inexistentă la data documentului; semn inversat.
**Stare: PARȚIAL.**
- ACOPERIT: `core/numere.numar()` — sursă unică de parsare (extrasă din 9 copii pe 15.07;
  6 transformau `(200)` în 0.0 tăcut). `numar_fiscal()` pentru valori care intră în
  declarații: absența e legitimă, invalidul e eroare.
- ACOPERIT: F184 conformitate cotă TVA la dată; F185 coliziune CUI; audit de preluare firmă.
- LIPSĂ: gard care cere NOT NULL pe fiecare coloană de bani și cheie naturală unică pe
  fiecare tabel de import. Idempotența importurilor nu e verificată mecanic.

### 2. Graniță cod–bază
**Eșec:** query pe coloană/tabel inexistent; drift între schema unui tenant și template.
**Stare: PARȚIAL.**
- ACOPERIT: F165 `core/audit_schema.py` + `test_audit_schema.py` — poartă reală pe DB, cu
  test de mutație negativă. Direcția template→tenant = drift HARD.
- LIMITĂ DECLARATĂ: direcția tenant→template e informativă. Decizie din 22.07 (un whitelist
  ever-growing produce roșu fals). Consecință acceptată: un tabel creat ad-hoc într-un
  tenant rămâne „extra informativ" — cazul `d205_beneficiari`, care s-a dovedit legitim
  (cod mort, zero consumatori).
- ACOPERIT parțial: `core/test_pull_declaratii.py` (27.07) — teste pe `pull()`, granița
  cod↔bază, pe schemă temporară din template cu ROLLBACK. Două clase: `pull` **vede** datele
  care există, și `pull` **crapă zgomotos** când schema nu se potrivește. Cele ~175 de teste
  pe generatoare erau toate pure (`calcul_dXXX` + `build_xml` cu fixturi) — `pull()` nu era
  atins de niciunul, deși acolo au trăit toate defectele din iulie.
- ACOPERIT: `common.cere_coloane` — `SELECT *` nu crapă la coloană lipsă; rândul iese fără
  cheie, `get()` dă `None`, iar absența e tratată legitim ca 0. Dovedit pe D112: cu
  `salariu_brut` redenumită, declarația ieșea cu salarii ZERO (1333 car. în loc de 1890).
  Garda verifică PREZENȚA cheii; valoarea 0 rămâne legitimă.
- LIMITĂ DECLARATĂ: `cere_coloane` verifică rândurile CITITE, deci **o tabelă goală trece**.
  O coloană dispărută pe o firmă fără salariați nu se semnalează.
- LIPSĂ: verificare statică a query-urilor din cod contra schemei reale (`audit_cod_schema.py`
  a fost prototipat local pe 27.07, **nu e pe server**). Ar prinde defectul înainte de rulare.
- LIPSĂ: aceeași gardă la celelalte `SELECT *` pe date fiscale (d394, bilant_api, rip_api,
  stocuri_cv_api, reconciliere_api). Vezi DE_FACUT.

### 3. Calcul fiscal
**Eșec:** cotă/prag greșit, rotunjire greșită, graniță de perioadă — **și bază zero pentru
că intrarea a fost înghițită**.
**Stare: PARȚIAL.**
- ACOPERIT: cotele parametrizate cu data în `common.cota()` (period-aware).
- ACOPERIT: `control_incrucisat.py` — D112 vs rulaj, D300 vs jurnal, D390 vs evidență +
  D300 depus. Trei stări (verde/roșu/**gri**), temei + limită pe fiecare constatare.
- ACOPERIT parțial: regula bazei nule. `d205.genereaza` refuză explicit să emită fără
  beneficiar. La celelalte, `declaratii_api.numar_operatiuni` numără operațiunile, iar ecranul
  pune o **poartă** (DS cap.5 `.caseta-poarta`) înainte de trimiterea în coadă: omul confirmă
  că firma chiar n-a avut activitate. Nu blochează depunerea pe zero (obligație reală), dar
  golul nu mai trece tăcut. `None` = nu se poate număra (d101/d112) → fără poartă.
- LIMITĂ DECLARATĂ: poarta e doar în ecran. `POST /coada` regenerează declarația și n-are
  poartă — un apel direct de API trimite pe zero fără întrebare.
- LIPSĂ: gard care interzice cote literale în cod (azi nimic nu împiedică un `* 0.19`).
- LIPSĂ: teste golden pe cifre calculate de mână din exemplul oficial.
- LIPSĂ: gard de **derivă legislativă** (deschis 31.07.2026). Garda anti-stale a agendei
  (`core/test_agenda.py`) e UNIDIRECȚIONALĂ: prinde codul schimbat sub o bifă (ancoră =
  commit), NU legea schimbată sub un cod care stă — un act care modifică art.77 fără ca
  nimeni să atingă fișierul lasă bifa verde la infinit. Cere: temeiuri structurate
  (act+nr+articol+dată) citibile mecanic, o sursă de adevăr externă pentru „actul X s-a
  modificat după data D", reset al bifei la orice atingere a unui act citat. Fundație
  parțială: `core/temeiuri.py` găsește deja locurile care citează un act; lipsește partea
  care întreabă dacă actul s-a schimbat. Nu se începe acum — clusterele nebifate sunt risc
  prezent. (Poziția cerută pt. DE_FACUT.md, care nu mai există; trăiește aici, în registrul
  gardurilor.)
- ACOPERIT (31.07.2026): temei STRUCTURAT (`common.Temei`: act/nr/an/art/alin/lit/data_in/
  data_out/url) pe toate cotele din `common.COTE` + garda de EXPIRARE pe `data_out`. `cota()`
  RIDICĂ după `data_out` (nu întoarce tăcut valoarea veche) — mecanismul PRINCIPAL de derivă, nu
  un proxy: nu există API legislativ RO fiabil (dovedit repetat). Gard ratchet în verificator:
  orice cotă nouă cu temei string (nestructurat) blochează. Inventar A generat parțial din COTE,
  cu overlay persistent pentru judecățile umane (`genereaza_inventar_a.py` + `INVENTAR_A_OVERLAY.tsv`).
- LIMITĂ REALĂ (rămâne descoperit, 31.07.2026): o schimbare de lege **între `data_in` și
  `data_out`** NU e detectabilă. `data_out` semnalează doar când TRECE valabilitatea DECLARATĂ,
  nu când actul se modifică dedesubt mai devreme decât s-a estimat. Sistemul nu detectează
  schimbarea legii — refuză doar să răspundă cu o valoare expirată; eroarea apare la CALCUL, nu la
  depunere. `estimat=True` marchează `data_out`-urile ghicite (sfârșit de perioadă rezonabilă:
  an fiscal/semestru), unde fereastra nedetectabilă e mai largă. Închiderea ar cere un feed
  legislativ mecanic care nu există — degradează la revizuire manuală periodică ghidată de registru.
- ACOPERIT (01.08.2026): BLOCAJ MOTIVAT pe cote de regula late-start. O cota citita de o functie de
  regula cu `data_in` mai tarziu decat `common.DATA_START_SISTEM` (2025-01-01, podeaua datelor salariale)
  ridica `common.PerioadaIndisponibila` (subclasa ValueError, tag `PERIOADA_BLOCATA`) cand e ceruta pentru o
  perioada din [podea, data_in) - handler-ul global (`main.py`) o arata utilizatorului ca 423 cu mesaj (cele
  4 elemente: ce s-a oprit / de ce / ce se poate face / cine decide), NU ca traceback 500. Gard in verificator
  (`GARD BLOCAJ MOTIVAT`, PRAG 0): probeaza runtime ca fiecare cota de regula late-start produce blocaj motivat,
  nu exceptie bruta. Test: `core/test_perioada_indisponibila.py`. Commit-uri 1d37d3a (mecanism) + 1de6ac9 (gard).
- LIMITA DECLARATA (01.08.2026): calculul salarial NU e disponibil pentru perioade anterioare lui 2026-01-01,
  fiindca plafonul facilitatii (`plafon_facilitate_salariu_minim`) si plafonul tichetelor (`tichet_masa_plafon`)
  nu sunt verificate la sursa pentru 2025 - desi salariu_minim/facilitate exista din 2025-01-01. O adeverinta/
  rectificativa pentru o luna 2025 da mesajul motivat, nu crapa. Se DESCHIDE prin backfill la sursa (candidat:
  OUG 115/2023 pentru plafon), NU prin estimare - nu se inventeaza o valoare. Ramificatie: `tva_redusa`
  (start 2025-08-01) rupe similar `calcul_tva` (cititor subtire, NU functie de regula) pentru facturi pre-
  2025-08 - acoperit de acelasi mecanism central (cota()), dar out-of-scope pentru gardul de reguli.
- ACOPERIT (02.08.2026): **CM4 plafon 12 salarii minime** pe baza de calcul CM (OUG 158/2005 art.10 alin.(1);
  OMS 15/2018 ART.61 + Exemplul nr.5). `_calcul_cm_core` capeaza fiecare venit **LUNAR** la
  `12 * cota("salariu_minim", luna)` INAINTE de mediere (param `venituri_lunare`). GARD MECANIC =
  `test_cm_plafon_traverseaza_schimbarea_sm`: fereastra Apr-Sep 2026 are sm 4050 (Apr-Iun) si 4325 (Iul-Sep) ->
  plafoane 48600/51900 diferite pe luni; **MUTATIE**: cine muta plafonarea pe MEDIA (un singur sm) pica testul
  (media zilnica difera). + `test_cm_plafon_{toate_sub_nu_se_activeaza, o_luna_peste, toate_peste, luni_asimilate_stagiului}`.
- ACOPERIT (02.08.2026): **ziua 15 CM = 75%**. `test_cm_ziua15_este_75pct` fixeaza ziua 15 la 75% (gol de
  redactare art.17(1): lit.b "8-14", lit.c "peste 15"; decizie arhitect favorabila asiguratului); **MUTATIE**:
  mutarea tacita la 65% pica testul.
- **BLOCAJ MOTIVAT (02.08.2026) — plafon CM "salariul minim IN LUNA".** CE S-A OPRIT: nimic la runtime; regula
  "plafon lunar = 12 x sm-in-luna" e APLICATA in cod, dar NEconfirmata verbatim la sursa. DE CE: OMS 15/2018
  Exemplul 5 exemplifica plafonul cu sm **ANUAL** ("pentru anul X = 12 x sm"), din era cu un singur sm/an (claim
  5 GRI); pentru era cu doua sm/an (din 2024) textul nu confirma explicit "in luna". CE SE POATE FACE:
  reconfirmare la sursa (ordin/circulara MS/CNAS pe era cu doua sm/an, sau forma la zi a art.61); pana atunci se
  aplica interpretarea coerenta cu "12 sm lunar" din art.10(1). CINE DECIDE: Costin (arhitect). Consemnat
  DECIZII.md 02.08.
- DATORIE DESCHISA (02.08.2026, art.XI L141/2025): forma pre-01.08.2025 a procentelor CM (art.17(1)) NU e
  implementata (`_VARIANTE_PROCENT_CM` are o singura varianta = forma L141/2025, aplicata inclusiv episoadelor
  cu certificat initial anterior lunii august 2025). Procentele vechi nu-s verificate la sursa -> blocaj motivat,
  `xfail test_datorie_cm_art_xi_regim_initial`.
- ACOPERIT (02.08.2026): **tichete culturale** (Legea 165/2018 cap.V). GARD `test_bilete_valoare_declara_
  toate_tratamentele` (BILETE_VALOARE_TRATAMENT): fiecare bilet de valoare declara EXPLICIT cele 4 tratamente
  (impozit/CAS/CASS/CAM) + sursa plafonului; **MUTATIE**: adaugi un tip nou fara declaratie -> pica. + GARD
  plafon semestrial `plafon_cultural()`: fereastra GRI (oct.2025-mar.2026) BLOCATA motivat in beneficii_api.seteaza
  (test_cultural_seteaza_gri_blocat), NU se calculeaza tacit cu 240/470. Divergenta esentiala vs etalon:
  culturalul NU are CASS (art.157(2)) - test_cultural_diferit_de_masa_pe_cass.
- ACOPERIT (02.08.2026): **tichete de cresa** (Legea 165/2018 art.19). Tratament = ca CULTURAL (impozit
  10%, FARA CAS/CASS/CAM), in registru BILETE_VALOARE_TRATAMENT (gardul 4 tratamente il acopera). GARD plafon
  `plafon_cresa()` = 450/copil (baza art.19(1) confirmata); grant peste baza (indexare 740 GRI verdict 17, mmuncii
  503) BLOCAT motivat in beneficii_api.seteaza (test_cresa_seteaza_peste_plafon_*), NU se aplica 740 tacit.
  Divergenta CASS vs etalon (cresa fara CASS, art.157(2)) prinsa de registru + test_cresa_in_registru_fara_cass.
- DESCHIS: rotunjirea din D390 e bancară (`round()`), în timp ce D112 documentează că ANAF
  cere aritmetică. Schimbare fiscală — se verifică la sursă. Vezi DE_FACUT.

### 4. Ieșire către autorități
**Eșec:** XML structural valid, semantic gol sau fals.
**Stare: PARȚIAL.**
- ACOPERIT: `core/duk.py` + `test_duk.py`. Trei stări; **eșecul rulării = gri, nu valid**.
  Un XML nevalidat nu se declară valid. Test: niciun validator nu acceptă gunoi.
- ACOPERIT: `test_ruta_valideaza_trimite_an_si_luna` — leagă ruta de semnătura cerută de
  validatorul SAF-T. Fără el, validarea D406 a fost gri permanent luni de zile.
- ACOPERIT: reconcilierea linii-antet la D406 (divergență între două surse ale aceleiași
  facturi = eroare).
- LIPSĂ: totalurile din XML reconciliate pe **a doua cale de calcul**, independentă.
- LIPSĂ: snapshot de regresie pe fixturi înghețate.
- **DUK validează STRUCTURA, nu conținutul.** Nu e gard de conținut și nu se tratează ca atare.

### 5. Izolare tenanți
**Eșec:** `search_path` nesetat; constrângere nescopată la `current_schema()`; job de
fundal pe tenantul greșit; **IDOR** (id tenant din URL neverificat contra userului).
**Stare: ACOPERIT (mecanism + probă dinamică + gard structural).**
- Mecanismul: `db.get_conn(schema)` cu `SET LOCAL`; `auth_api.schema_tenant(uid, tenant_id)` →
  `None` fără acces → 404. Model API-key: `_api_schema` scopat pe `accounting_firm_id`.
- ACOPERIT (probă DINAMICĂ, 31.07): `core/test_izolare_incrucisata.py` — doi tenanți sub cabinete
  diferite, acces încrucișat real prin HTTP (5 rute) → 404, zero date; mutație `schema_tenant`
  bypass → leak → testul pică. + măsurat: `from core.db import` = 0 module (proba e completă).
- ACOPERIT (gard STRUCTURAL, 31.07): `verificator_conformitate.py` — orice rută cu `{tenant_id}`
  în path care deschide `get_conn` TREBUIE să rezolve accesul (schema_tenant SAU resolver pe
  accounting_firm_id/user_tenants). CODEBASE-WIDE (`@<var>.<verb>` în tot `.py`, nu doar main.py
  @app) + META-GARD pentru APIRouter nemontat. Baseline 0. RED dovedit (gol în alt fișier; router
  nemontat).
- LIMITĂ DECLARATĂ a criteriului: gardul acoperă `{tenant_id}` în **PATH**. Rute care iau
  `tenant_id` din **BODY/query** (POST `/coada`, POST `/declaratii/{tip}`) NU sunt acoperite de
  criteriul structural — azi rezolvă accesul (`/coada`→`_schema_sau_404`, declaratii→schema_tenant,
  verificat manual 31.07), dar gardul nu le impune. Resolveri pe 2 niveluri de indirectare:
  neacoperiți (măsurat: 0 azi).
- LIMITĂ (conexiuni brute): 1 conexiune brută în afara helperului (`sinteza_zilnica.py`, citește
  doar `public.*`) — nepăzită mecanic.

### 6. Acces
**Eșec:** rută fără dependență de rol; IDOR (id din URL neverificat contra tenantului).
**Stare: PARȚIAL.**
- ACOPERIT: `core/test_rute_autentificate.py` (27.07) — AST pe `main.py` **și**
  `core/spv_rute.py`; orice rută fără `Depends` trebuie să fie în lista `PUBLICE`, declarată
  explicit cu motivul. Lista e verificată și invers: o intrare care nu mai corespunde unei
  rute fără auth pică (nu se acumulează acoperire moartă). Dovedit prin mutație pe cod real.
- Cele 3 rute din `core/spv_rute.py` (declarate cu `@app.get` *în interiorul* funcției
  `monteaza`) fuseseră ratate de auditul manual — garda le acoperă.
- LIMITĂ DECLARATĂ: verifică PREZENȚA dependenței, nu corectitudinea ei. O rută de cabinet
  care cere din greșeală `cere_client` trece.
- LIPSĂ: test de acces încrucișat (obiect din alt tenant → 404).
- DESCHIS: gating admin inconsecvent (`cere_rol("superadmin")` vs `cere_cabinet` + gardă
  inline) — DE_FACUT poz. 7.

### 7. Integritate în timp
**Eșec:** modificare retroactivă în lună închisă; declarație depusă regenerată altfel;
balanță ≠ sumă înregistrări; backup nerestaurabil.
**Stare: PARȚIAL.**
- ACOPERIT: `perioade_blocate`; declarația depusă persistată cu rânduri (F163v2);
  `verificatoare.echilibru_nota` / `balanta`.
- ACOPERIT: backup local + off-site cu alertare la N eșecuri consecutive.
- ACOPERIT: restaurarea din off-site **a fost testată cap-coadă pe 18.07** (`pg_restore` exit 0,
  scheme identice cu producția, `tenant_002.facturi=5`, apoi `dropdb`). Am scris inițial aici
  „LIPSĂ" fără să verific — vezi ISTORIC 18.07. Ce lipsește e **repetarea automată**: proba a
  fost făcută o dată, manual; nimic n-o reia periodic.
- LIPSĂ: verificare nocturnă Σdebit=Σcredit per perioadă/tenant + orfani.

### 8. Integritate cod — arbori paraleli
**Eșec:** două implementări ale aceluiași generator; repari copia moartă.
**Stare: ACOPERIT DE FAPT, gard absent.**
- Verificat 27.07: pe server există **un singur arbore** (`core/`). `declaratii.*` și
  `motor.*` nu există aici. Zero module neimportate (toate `migrare_*` sunt scripturi CLI;
  `alerta_acces`, `audit_retentie`, `sinteza_zilnica` rulează din cron).
- LIPSĂ: gard care să prindă apariția unei a doua copii.

### 9. Onestitatea testelor
**Eșec:** teste verzi care nu testează nimic (fake-uri pe codul auditat, teste stale,
fișiere necolectate).
**Stare: PARȚIAL.**
- ACOPERIT de fapt: 1277 teste colectate; fake-uri (`monkeypatch`/`MagicMock`) doar pe
  integrări externe (SPV, e-Factura, e-Transport, JWT). **Zero fake pe generatoarele de
  declarații.**
- LIPSĂ: **mutantul zero sistematic** — forțezi fiecare generator să întoarcă `[]` și suita
  trebuie să devină roșie. Se aplică azi ad-hoc, la reparații.
- ACOPERIT (31.07): gard că fiecare `test_*.py` (exclus venv) are ≥1 funcție `def test_` — `core/test_agenda.py::test_fiecare_fisier_test_are_cel_putin_un_test`, cu mutație. Un `test_*.py` cu 0 teste e script deghizat în suită (pytest nu-l colectează, dar numele sugerează acoperire). Prins pe `test_gdpr_functional` → redenumit `gdpr_functional.py`.

### 10. Joburi de fundal
**Eșec:** job care crapă nesupravegheat; job mort care arată identic cu unul care n-a avut
nimic de făcut.
**Stare: PARȚIAL.**
- ACOPERIT: `core/cron.py` — traceback în log + alertă (canal unic, cu throttling) + exit 1.
  `test_cron.py` verifică mecanic că fiecare din cele 7 module din crontab cheamă
  `cron.ruleaza`. Alerta care crapă nu maschează eșecul.
- ACOPERIT: **heartbeat** (27.07) — fiecare rulare reușită scrie în `public.cron_batai`;
  `core/cron.verifica_batai` compară cu pragul per job (ritm ×2 + marjă) și alertează.
  Rulează pe **systemd timer** la 6 ore, nu pe cron — singurul mecanism care supraviețuiește
  unui crontab pierdut. `bootstrap()` evită falsul-pozitiv la instalare.
- LIMITĂ DECLARATĂ: verificatorul rulează pe **același server**. Server jos = nici el nu
  rulează, nimeni nu află. Un deadman extern (ping către un serviciu terț) ar acoperi și asta.

### 11. Interfață (Design System)
**Eșec:** dialecte de formatare, culori hardcodate, stări goale ad-hoc.
**Stare: ACOPERIT mecanic, PARȚIAL vizual.**
- `verificator_conformitate.py`, 28 gardieni, TOTAL 0 obligatoriu înainte de commit.
- LIMITĂ DECLARATĂ: prinde SEMNĂTURA TEXTUALĂ, nu randarea. ~20/30 ecrane nevăzute cu ochii.

---

## Cum se strică un gard (lecții trăite, 27.07.2026)

Toate patru la aceeași gardă, în aceeași zi.

1. **Regex naiv pe cod.** `[^)]*` se oprește la prima paranteză închisă, deci ratează
   `body.get("an")`. Garda pica pe cod **corect**. Extragerea din cod se face pe paranteze
   echilibrate sau cu AST, niciodată cu regex naiv.
2. **Gardă care crapă.** `NameError` (import lipsă) → pică pe orice, inclusiv pe mutant.
   Testul de mutație a trecut **fals**. Mutația verifică motivul, nu doar eșecul.
3. **Verificare trunchiată.** `pytest -q | tail -3` taie mesajul la `AssertionEr...`.
   Verificarea unei gărzi citește output complet (`--tb=long` în fișier).
4. **Comparație pe `hash()`.** Randomizat per proces în Python — a raportat 6 diferențe
   false. Artefactele se compară pe SHA256 sau diff, niciodată pe `hash()`.

A cincea, din aceeași zi, la altă gardă:
5. **Poartă decorativă.** Verificarea rulează dar nu blochează (commit legat de `py_compile`,
   nu de probă). Dacă proba nu e poartă, e comentariu.

---

## Reguli de scris în acest registru

- Starea se schimbă **doar cu dovadă în același commit**.
- „ACOPERIT DE FAPT, gard absent" e o stare distinctă și onestă: azi e curat, mâine nu se știe.
- Limita declarată a fiecărui gard se scrie explicit. Un gard fără limită scrisă e citit ca
  acoperire totală.
