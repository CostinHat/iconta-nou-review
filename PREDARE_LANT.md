Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — **nicio comandă deschisă; 6 confirmări cerute lui Costin (drepturi pe rol)** (04.10.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-10-04**, rescriere COMPLETĂ la cererea lui Costin (commitul care poartă această predare; hash-ul lui e
  în raport și în `git log`). Versiunea de dinainte (1007 rânduri, cu istoria D212/F1–F3) e în istoria git — `git show a3210e08:PREDARE_LANT.md`.
- **pe commit**: `63c04a95` — four-way închis (HEAD = origin/main = public/main = backup/lant-2026-10-04 = procesul viu), prima
  parte a execuției „Testarea ca asistent”; a doua parte (butoanele de intrare în formular) e commitul care poartă predarea. Secțiunile atinse acum: ANTET, STAREA, FRONTURI, DECIZII ÎN VIGOARE, ATENȚIONĂRI,
  CE CERE POARTA.
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire** (CLAUDE.md §2.3 pct.10, pasul 5). E fișier de STARE CURENTĂ, nu
  jurnal — jurnalul e `ISTORIC.md`, deciziile în `DECIZII.md`, gărzile în `GARZI.md`, firele în `TESTE.md`.

## ÎN CE STARE E PROIECTUL

**Nu există nicio comandă deschisă.** Comanda Costin din 03.10 (patru puncte) și deciziile din 04.10 sunt livrate, fiecare cu poartă
completă, four-way și ZIP în `/home/costin/ghid_incoming/`:

| ce | commit | ZIP |
|---|---|---|
| lotul 19 — 433 de ghiduri + defectele 6–13 | `2798f8ce` | `iconta_lot19_publicat.zip` |
| D394 Î2 — încasările din activități exceptate de la AMEF | `5de03649` | `iconta_d394_i2.zip` |
| factura din bon marcată în SAGA/WinMentor, D406 (310327), e-Factura (751), încasată la emitere | `4bc13607` | `iconta_export_din_bon.zip` |
| schemele de test șterse din producție + jurnalul bifei C&D | `57724df6` | — |
| coloana `salariati.salariu_brut` retrasă (producția migrată DUPĂ deploy, 04.10 05:02) | `7c7a71ff` | `iconta_2b_coloana.zip` |
| salariul în timp (dată validată, înlocuire explicită, poarta pe lunile atinse) + etichete accesibile în toată aplicația + condiția D112 A1 | `a3210e08` | `iconta_salariu_in_timp.zip` |
| **testarea ca asistent**: drepturile pe rol și bifă (`cere_drept`, decizia „varianta 2”), interfața care urmează serverul (`data-actiune`), refuzul lângă buton, emailul clientului verificat înainte de creare, X + Esc pe ferestrele informative, ghidul pe rol, contorul Asistenți, fără „48 de ore” | `63c04a95` + commitul următor (butoanele de intrare în formular, proba pe producție) | `iconta_testare_asistent.zip` |

**Starea de lucru, decisă de Costin (17.09.2026, verbatim): „După asta nu urmează nicio temă.”** Proiectul e **în așteptarea folosirii
aplicației**, nu „în așteptarea unei teme”:

| | |
|---|---|
| **ce NU se face** | nu se alege o temă din backlog; nu se ia la rând nicio restanță; nu se deschide o investigație fiindcă „pare următorul lucru rezonabil”. `core.agenda.urmatorul_pas()` arată ce e scris în TESTE, nu dă o comandă |
| **ce declanșează lucru** | o comandă a lui Costin, sau ce iese din folosirea aplicației (un refuz care nu se înțelege, o cifră care nu se potrivește) |
| **ce se întâmplă cu restanțele** | rămân scrise (`CONFORMITATE.md`, `core/test_datorie.py`) și se închid **doar când le atinge altă lucrare** |
| **ce e permis fără să întrebi** | un **prag 1** găsit apăsând |

## FRONTURI DESCHISE, cu blocajul fiecăruia

- **D112 contract uniform A1** (pasul D1 din firul „Contract uniform A1”, TESTE.md): „nu acum”. **Se execută la prima modificare reală a
  `core/d112.py`, în același commit** — condiția e scrisă în fir și în docstring-ul modulului (decizia Costin 04.10; fără gard).
- **F1 etapele 9–11** (depunere reală prin SPV, ieșiri externe): **[EXTERN]** — certificat/token ANAF, depunere efectivă.
- **D212**: validatorul ANAF pentru OPANAF 2736/2025 (agricol pe normă, opțiunea CAS lit.B, CASS pe pensiile din străinătate) —
  **[EXTERN]**, datorii stricte în `core/test_datorie.py`.
- **R40**: nicio declarație depusă efectiv la ANAF prin aplicație — se închide prin folosire, nu prin cod. **R121**: P300/RO e-TVA fără
  acces programatic — **[EXTERN]**.
- **Drepturile pe rol — 6 confirmări cerute lui Costin** (raportul 04.10, §6; DECIZII 04.10.2026, consecințele 4–7). Implementat varianta
  scrisă, revenirea e o linie în `main.py` + pinul din `core/test_drepturi_rol.py`: (1) R52 — fluturașul/PDF-ul chitanței/fotografia
  bonului rămân la administrator, deși asistentul emite chitanța și certifică bonul; (2) pivotul R42(c) — regimul de TVA la „Poate
  pregăti” (vectorul îl scrie oricum); (3) pivotul R55 — planul de conturi la „Poate pregăti” (pasul 9 din Import date); (4) aprobarea
  bonului din portal și raportul Z manual la „Poate valida” (scriu notă validată direct); (5) REGES (configurare, trimitere, răspunsuri)
  la administrator (R56, credențiale); (6) contul Ana din producție are toate bifele pe „nu” — „Poate pregăti” i-l bifează
  administratorul (nu s-a modificat nimic în datele ei).
- **Restul restanțelor**: numărul se DERIVĂ (`scripts/raport_b.py`, `scripts/scan_ramas.py`), nu se scrie aici.

## DECIZII ÎN VIGOARE care schimbă cum se lucrează (detaliul în DECIZII.md)

- **Ghidurile**: metoda arhitectului — Claude în chat redactează și verifică, Costin aprobă titlurile, Code publică.
- **Bifa C&D**: fără rol separat (garda fișei, `cere_cabinet`); fiecare schimbare se jurnalizează în `mijloace_fixe_jurnal`.
- **Factura din bon**: marcată în toate ieșirile (nu omisă, nu vânzare nouă); se naște încasată.
- **Chitanța fără factură**: la firma exceptată de la AMEF = vânzare cu cotă (Î2); la cea neexceptată = încasare de creanță (5311=4111).
- **Drepturile pe rol (04.10, „varianta 2”)**: „Poate pregăti” = munca curentă; „Poate valida” = validări, înregistrarea amortizării,
  închiderea lunii; „Poate depune” = depunerea; administratorul = firme, asistenți, chei API, GDPR, abonament, datele cabinetului,
  deblocarea perioadei; mereu pe firmele alocate. Lista administratorului e exhaustivă; restul scrierilor pe firmă = „Poate pregăti”.
- **Ferestrele**: cele informative se închid din X și cu Esc (`inchidereDialog`); cele cu câmpuri doar din X (DS cap.9 v2.64).

## DACĂ CONTINUI DE AICI

1. **Ritualul de început** (CLAUDE.md §5): `pwd; hostname; git log --oneline -1; git rev-parse --is-inside-work-tree;
   ./venv/bin/python -m core.agenda` — trebuie `/home/costin/iconta_nou`, `iconta-prod`, arbore git valid.
2. **Fără o comandă a lui Costin nu se pornește nimic** (secțiunea de mai sus). Cu o comandă: firul se scrie întâi în TESTE.md
   („În lucru acum”, cu pașii), decizia în DECIZII.md (verbatim), apoi codul.
3. **Fiecare temă se încheie la fel**: gard + mutație (backup cu `cp`, niciodată `git checkout`; `__pycache__` curățat) + probă pe
   portofoliu vechi→nou (output brut) + cele trei unelte vizuale dacă s-a atins un ecran + verificatorul ÎNAINTE de commit + registrele
   (GARZI, DECIZII, TESTE, ISTORIC, PREDARE; FUNCTIONALITATI/TRASEE după caz) + commit pe nume (`git commit -F`) + four-way + ZIP + raportul
   cu cele 11 secțiuni (CLAUDE.md §2.2).
4. **Când poarta respinge, prima ipoteză e că are dreptate.** Pe 03–04.10 a respins fiecare temă cel puțin o dată și de fiecare dată a prins ceva
   real (o coloană NULL nedeclarată, un registru nesincronizat, o tabelă neclasificată, un import nefolosit, un `bool(corp…)`).

## ATENȚIONĂRI — efecte recente care schimbă ce se întâmplă în probe și teste

- **Salariul contractual trăiește NUMAI în `salariu_istoric`** (coloana `salariati.salariu_brut` nu mai există — gard `core/test_2b_coloana.py`).
  Un test/seed care inserează un salariat pune salariul în istoric (`valabil_din` = data angajării).
- **Schimbarea salariului la o dată deja în istoric e REFUZATĂ** (`SALARIU_DATA_OCUPATA`); înlocuirea cere `inlocuieste: true`.
  O schimbare care atinge o lună închisă e refuzată, chiar datată înaintea ei.
- **O societate fără formă juridică / capital în Date firmă nu emite facturi** (lotul 19, decizia 12). Probele care emit pe F1–F5 își
  completează profilul ÎN TRANZACȚIA anulată; testele pe schemă efemeră pun `forma_juridica='SRL'`, `capital_subscris=200`.
- **La o firmă marcată exceptată de la AMEF, chitanța fără factură cere cota**; la una neexceptată, chitanța cu cotă e refuzată.
- **Orice câmp nou de formular are nume accesibil** (`for` pe etichetă sau `aria-label`) — gard `core/test_etichete_campuri.py`.
- **Baza de producție are 5 scheme = cei 5 tenanți** (tenant_049–053); reziduurile de test au fost șterse 04.10 (backup
  `~/backup_scheme_test_prod_20261004_0048.sql.gz`). Baza de test (`iconta_test`) are 35 de scheme cu salariați, inclusiv `ztest_*`.
- **Orice rută de SCRIERE pe o firmă (`{tenant_id}`) stă pe `cere_drept(_drepturi.NIVEL)`** — nu `cere_cabinet`/`cere_context`/`cere_rol`
  (gard `core/test_drepturi_rol.py`). Testele HTTP care cheamă rute de firmă ca `angajat` au nevoie de bifa potrivită și de firma în
  `user_tenants`; ca `client`, rutele de cabinet răspund 403.
- **Orice buton care cheamă o rută restrânsă poartă `data-actiune="METODĂ /cale"`** (șablonul din `main.py`), pe ELEMENTUL al cărui
  handler face apelul (gard `core/test_drepturi_ui.py`, instrument `scripts/scan_drepturi_ui.py`). Un câmp care arată și o valoare
  poartă `data-actiune-camp` (se dezactivează). Declarațiile „METODĂ /cale” NU se numără ca apelanți (R70/R80, `_static()`).
- **Un refuz din `catch` trece prin `arataMesaj(…, "eroare")` / `eroareCamp`**, nu prin `.textContent` / `.innerHTML` direct.
- **„adresa are deja cont”** are o singură formulare: `uc_comun._refuza_email_ocupat` (alt rol / client activ / asistent existent).
- **Staging necomis, deliberat:** `import_fiscalos/` (urcat de Costin 21.09) — nu se comite, nu se șterge.

## STAREA LA PREDARE

**Cifrele de aici se copiază din IEȘIREA PORȚII**, nu din predarea de dinainte. Ultima, pe `a3210e08` (04.10.2026):

```
7101 passed, 9 skipped, 13 xfailed in 2921.58s (0:48:41)      -> COLLECTED 7123
verificator: TOTAL: 0 candidate
```

**Poarta durează ~48 de minute** (pytest complet ~7120 de teste; măsurat pe ultimele 8 rulări din 03–04.10: 2877–2922 s). O tură cu o
respingere costă deci ~1,5 ore numai în porți — de-aia gărzile care pică repetat se rulează ÎNAINTE de commit (lista de la „CE CERE
POARTA”). `commit-msg` rulează DUPĂ pytest: `# diff-citit:` (fișiere normative) și `# multe-fisiere-ok:` (peste 8 fișiere noi) se pun
în mesaj ÎNAINTE de primul `git commit`.

**Four-way-ul se închide la `post-commit`**: publică pe `origin/main`, `public/main`, `backup/lant-<zi>`, publică statica din HEAD,
restartează necondiționat și verifică brațele. Confirmarea independentă: `scripts/toate_poarta_head.py <SHA COMPLET>` (cu SHA scurt
raportează fals), `systemctl show iconta-nou -p ExecMainStartTimestamp` după data commitului, sentinelele `.git/PUSH_*_ESUAT` absente.

**CLICHETELE VII — blocul de mai jos e GENERAT** (`scripts/scan_ramas.py --clichete-md`; nu se editează cu mâna).

<!-- CLICHETE-VII:START (generat de scripts/scan_ramas.py --clichete-md) -->

*Generat din COD. **Nu se scrie cu mâna** — `core/test_clichete_generate.py` recalculează și compară caracter cu caracter. Regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.*

| cod | acum | ce se numără | instrument |
|---|---|---|---|
| **77** | **109** | refuzuri fără temei în module care citează legea | `scripts/scan_refuzuri.datorie()` |
| **77u** | **899** | UMBRA: refuzuri în module care nu citează legea (nedeplafonat) | `scripts/scan_refuzuri.umbra()` |
| **50** | **1220** | aserțiuni ancorate pe text, nu pe structură | `core/scan_garzi_pe_text.pe_fel()` |
| **R80** | **7** | rute despre care detectorul de apelanți nu poate afirma nimic | `scripts/scan_ancore_rute.verdicte()` |

<!-- CLICHETE-VII:STOP -->

## CIFRELE DESPRE DATE SUNT INTEROGATE, NU SCRISE

Blocul următor e **generat** de `scripts/scan_predare_cifre.py`, iar `core/test_predare_cifre.py` îl compară cu interogarea de la
rulare. **Descrie baza în care rulează poarta — `iconta_test` (din R68), nu producția.**

<!-- CIFRE-DATE:START (generat de scripts/scan_predare_cifre.py --md) -->

*Generat din bază. **Nu se scrie cu mâna** — `core/test_predare_cifre.py` compară blocul cu interogarea curentă și pică dacă diferă. Regenerare: `./venv/bin/python scripts/scan_predare_cifre.py --md`.*

**Portofoliu**

| cifra | ce e |
|---|---|
| **20** | firme în portofoliu |
| **20** | din care active |
| **15** | la cabinete reale |
| **5** | la cabinete de test |
| **0** | perechi de firme cu același nume în același cabinet |

**Cabinete**

| cifra | ce e |
|---|---|
| **7** | cabinete |
| **4** | din care declarate de test (tipar pe nume: TEST / PROBA) |

**Denumirea firmei (R81)**

| cifra | ce e |
|---|---|
| **0** | divergențe portofoliu ↔ fiscal, pe populația declarată |
| **0** | divergențe pe TOATĂ populația, fără nicio excludere |
| **2** | firme cu instantaneu ANAF (`nume_anaf`) |
| **2** | din care cu denumirea DIFERITĂ de cea de la ANAF |
| **1** | din care cu alegerea deja consemnată (deci caseta nu apare) |

**Scoatere și scheme (R79)**

| cifra | ce e |
|---|---|
| **4** | rânduri în `public.firme_scoase` |
| **3** | nume de schemă distincte în ele |
| **20** | scheme `tenant_NNN` în bază |
| **49** | contorul `tenant_schema_seq` |
| **48** | maximul istoric de nume de schemă |

**Clasificatorul de alerte**

| cifra | ce e |
|---|---|
| **2** | predicții de alertă confruntate cu faptul |
| **2** | din care greșite |

**Referințe moarte**

| cifra | ce e |
|---|---|
| **0** | rânduri care trimit la o firmă inexistentă |
| **20** | tabele din `public` cu `tenant_id`, numărate |

<!-- CIFRE-DATE:STOP -->

## BUCLA DE LUCRU — citește înainte de prima probă

- **Se lucrează pe server**, `~/iconta_nou`, branch `main` (ritualul de început din CLAUDE.md §5). Python: `./venv/bin/python`.
- **Mediul**: baza de producție `set -a; . ~/.iconta/db.env; set +a`; baza de test `~/.iconta/test.env`; pentru probe cu browser și
  `api_keys.env` (fără `BREVO_API_KEY`). Pytest sursează singur `test.env` (`conftest.py`, R68) — suita nu poate atinge producția.
- **Probele pe producție**: numai în tranzacție anulată (proxy cu `commit` neutralizat peste `db.get_conn`, `ROLLBACK` în `finally`),
  `observare.alerteaza` neutralizat. Codul vechi se probează dintr-un `git worktree` temporar la HEAD, scos după.
- **R118 — ce se servește NU e ce e în lucru.** `/static` vine din `../iconta_publicat/static`, scris din HEAD la `post-commit`. O
  editare de JS nu e live: înainte de orice probă pe ecran, `scripts/publica_static.py --din-arbore`, iar la final republicarea HEAD.
- **O schimbare de JS cere, în ordine**: `versioneaza_assets.py --scrie` (în rădăcina repo-ului) după ULTIMA editare · rescanarea vizuală
  (artefactele `proba_r175_arbore_asistent.json`, `proba_decl50.json`, `acoperire_vizuala.json` se comit cu lucrul).
- **Scanul vizual — rețeta, ca script cu `trap`** (exemplu: `scan_sal.sh` din scratchpad-ul turei, în ZIP-ul `iconta_salariu_in_timp.zip`):
  `publica_static.py --din-arbore` → `uvicorn main:app --port 8011` pe `iconta_test` (așteaptă 200) → `proba_r175_arbore_asistent.py`,
  proba UI a temei, `vizual/interactiune_scan.py`, `proba_decl50.py`, `vizual/axe_scan.py`, `vizual/mobil_scan.py` →
  `vizual/curata_proba_ecrane.py` → oprește 8011 **pe PID** → `publica_static.py` (republică HEAD). Durată ~9 minute. **Nu se editează
  arborele cât rulează** poarta sau scanarea.
- **`pkill -f "<tipar>"` își omoară propriul shell** dacă tiparul apare în comandă — se oprește după PID.
- **Pachetul de livrare** (cerut la capătul fiecărei teme): ZIP în `/home/costin/ghid_incoming/<nume cerut>.zip`, cu fișierele atinse la
  căile lor (`git archive <commit> <fișiere>`), registrele, output-ul brut al probelor (vechi/nou), mutațiile, logurile porții și ale
  scanului — făcut DUPĂ ce poarta a trecut și four-way-ul e închis.

## RESTANȚELE — unde se citesc

**Numărul se derivă** (`scripts/raport_b.py`, `scripts/scan_ramas.py`), nu se scrie aici. Registre: `CONFORMITATE.md` (restanțele cu
stare), `core/test_datorie.py` (datoria verificabilă, `xfail(strict=True)` — 13 la 04.10), `GARZI.md` (limitele declarate ale gărzilor).
O restanță se închide **doar când o atinge altă lucrare**.

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează. Tabelul se
POARTĂ, nu se deleagă în istoric.*

**Clasa asta are un mecanism, nu doar un tabel:** cifrele despre **date** nu mai pot îmbătrâni,
fiindcă sunt generate. Tabelul rămâne pentru cele despre **cod** și **proces** — și ca istorie.

| cifra | unde apărea | de ce e INVALIDATĂ |
|---|---|---|
| **131** (valori fiscale în afara registrului) | predarea din 22.08 | termeni recalculați pe domeniu lărgit de trei ori. Clichetul viu: `core/test_constante_nesursate.py` |
| **„25 de trasee"** | comenzile din 24 și 25.08 | nu exista instrument. Cifra care se poate reface e **36** |
| **„129 de rute schimbă date fără rol"** | predarea din 26.08 dimineață | raza nu se mai poate reconstitui |
| **17** (coloane citite și scrise de nimic) | instrument din 26.08 seara | INVALIDATĂ înainte de publicare |
| **13 / 6** (rute de citire fără apelant) | raportul din 26.08 seara | ancoră greșită; real, prin citire: **5** |
| **„4 din 5 rute nedeclarate"** | R70, 26.08 | **2**, nu 4 |
| **12** (tabele cu `tenant_id`) | R50, 25.08 | **13** din 26.08 |
| **25** (scrieri care refuză fără motiv) | prima măsurătoare, 27.08 | **16** după calibrare |
| **623** (404-uri primite de Googlebot) | raportul din 27.08 | **11**; restul sunt scanere — 70,3%, prin rDNS cu confirmare |
| **„2" (aritmetică pe nume neutre)** | clichet din 24.08 | cifra e tot 2, dar **termenii** erau greșiți |
| **8** (coloane `tenant_id NOT NULL`) | 27.08, R79, în mesajul commitului `0963d7f` | **10**. Numărată pe drum, fără instrument |
| **„1 din 411" (rute oarbe la detector)** | prima măsurătoare a orbirii, 27.08 | **51**. `_static()` întoarce un **șir** |
| **„toate cele 13 firme au evidență"** | prima sondă de scoatere, 27.08 | clasificator pe text, care citea ecranele rămase în DOM |
| **„0 din 17 firme au `nume_anaf`"** | predarea din 27.08 dimineața | **1 din 18** din 19:12 |
| **„4 din 17 divergențe de denumire"** | R81, 27.08 seara | **4 din 18**, și **0 din 14** firme reale — restul e cabinetul de test 4163 |
| **„patru locuri scriu `tenants.nume`"** | `555d606`, 27.08 | **trei**. Al patrulea scria în `firma_profil` |
| **„lista pe denumire fiscală ar cere o citire în fiecare schemă"** | `555d606`, 27.08 | bucla per-schemă **există deja** (`tip_firma_v1`) |
| **„4 din 6 acte de nivel firmă"** | R82, 27.08 | **4 din 7**, măsurat pe calea rutei, nu pe fișier. Cele patru tăcute sunt aceleași |
| **„4 divergențe de denumire"** (clichet pe date) | `test_nume_firma_unic.py`, 27.08 | **0** pe populația declarată. Vechea valoare era clichet pe **fixturi** — instrumentul citea toate firmele, fără filtru de cabinet |
| **„0 din 18 firme au `nume_anaf`"** | prima formă a predării din 28.08, 04:2x | **1 din 18** — `Antibiotice Iasi`. Cifra fusese invalidată o dată pe 27.08 și a reapărut din memorie |
| **„divergența nu se poate naște la creare"** | R81, 28.08 dimineața | adevărat despre `POST /tenants`, **fals** despre `POST /auth/register`, unde `precompleteaza_din_anaf(seteaza_nume=True)` scria un singur loc. Găsit de garda de simetrie, la prima rulare |
| **„51 de rute oarbe" citit ca „51 GRI"** | R80, 27.08 | **45**. Din cele 51, șase erau deja `EXCLUS`. Orbirea instrumentului (51) și clasa GRI (45) sunt două întrebări, nu două măsurători ale aceleiași |
| **„caseta de divergență din LISTA de firme"** | R81, 27–28.08 | caseta e pe ecranul **firmei** (`meniuFirma`), nu în listă. Scris din memoria structurii; a produs o măsurătoare falsă în proba W înainte de a fi prinsă |
| **43** (facturi declarabile — numitorul lui „28 din 43, 65%") | R35, 24.08; purtată de-atunci în R87, R88 și în predare | **41**, cu instrument (`scripts/sonda_facturi_necontate.py`). Termenii lui „43" nu se reconstituie: în bază sunt 41 de facturi **în total**, iar în **aceeași zi** cealaltă măsurătoare — R36 — scria „41 de facturi, 34 de note". Două cifre despre același obiect, în aceeași zi. *Numărătorul (28) și TVA-ul (102.260,00) se refac exact.* |
| **44 de restanțe deschise · prag 2 = 15** | predarea din 29.08 dimineață | **45** și **17** atunci, numărate mecanic pe câmpul `unde intră`. Vechea defalcare (15+12+16=43) nu se închidea cu totalul ei |
| **13** (regimuri fiscale reale) | prima formă a lui `scan_regimuri.py`, 29.08 | **12**. Scanul număra `tip_decont` **brut**, iar în date există patru scrieri pentru două lucruri — `L`, `lunar`, `T`, `trimestrial`. **Verificat la sursă: nu e un defect** — `core.common.perioada_tva_tip` le parsează pe toate fără default tăcut. Era naivitatea instrumentului: două firme cu aceeași periodicitate apăreau ca două regimuri |
| **„PREDARE_LANT.md e cu 12 commituri în urmă"** | comenzile din 27.08 seara, 27.08 târziu, **și 29.08** | **2**, apoi **0**, măsurat cu formula din `pre-commit`. Pragul e 10; avertismentul n-a apărut niciodată. **A patra apariție a aceleiași cifre**, de fiecare dată fără măsurătoare în spate |
| **66 de câmpuri tăcute, pe 17 rute** (clasa R97) | raportul și registrele din 30.08 dimineața | **54 pe 16**. Instrumentul căuta „randat" pe NUME și nu vedea parcurgerea **generică** (`Object.keys`, `Object.entries`), care afișează cheile fără să le numească — deci dădea drept tăcute câmpuri care **se afișează** (`randuri_de_sters.*`, cele 9 `marcaje.*`). **Greșeala era în direcția OPUSĂ celei declarate de instrument** („randat e supra-numărat, deci clasa e plafon inferior"), ceea ce o face mai rea decât o imprecizie: cine o citea o corecta mental în partea greșită. Reparat în aceeași zi, `randat_generic()` |
| **„nu arată ce anume s-ar șterge"** (previzualizarea scoaterii) | raportul din 30.08 dimineața | **fals** — `randuri_de_sters` **se afișează**, „N × tabel", generic; la fel motivele, inclusiv *„nu pot decide"*. Afirmația era făcută pe ieșirea instrumentului, **fără citirea codului**. Ce tace, cu adevărat, e altceva și mai mic: **ce s-a verificat și a ieșit gol** (R99) |
| **„rute 411 = … + EXCLUS 32"** | predările din 28 și 29.08, inclusiv **prima formă a rescrierii complete de azi** | **413** și **34**, citit din ieșirea porții care a produs `471368c`. *Cifra a fost **copiată din documentul de dinainte** în timpul unei rescrieri al cărei scop era să scoată exact afirmațiile purtate din memorie. A treia clasă de cifră care se strecoară prin copiere, după `nume_anaf` și `43`. De-asta rândul „starea la predare" spune acum, în text, de unde se ia.* |
| **„Bilanț (S1005) · CPP — zero rute"** | lista 3 din verdictul 1d, scrisă 22.08 și purtată prin două revizuiri, inclusiv cea din 30.08 dimineața | **FALSĂ DE LA NAȘTERE.** Măsurat: **patru rute** (`s1005-xml`, `s1005-valideaza`, plus perechea `s1003`) **și un ecran** (`ecranBilant`). Datat cu `git log -S`: rutele au intrat pe **04.07.2026** (`671a09f`), ecranul în aceeași zi (`8e450fa`) — **cu aproape două luni înainte** ca rândul să fie scris. *Contradicția era vizibilă în chiar același document: o secțiune din 26.08 discută pe larg cele două rute pe care tabelul le declara inexistente.* Rândul s-a **scos**: ce rămâne nerezolvat la bilanț e categoria de mărime, care e deja alt rând al aceleiași liste (`R3`) |
| **„cele 9 declarații sunt scumpe, fiindcă nici ruta nu trimite"** | verdictul 1c (29.08), purtat în verdictul 1d, în decizia de ordine din 30.08 și în predare | **falsă ca estimare de cost, adevărată ca observație.** Ruta chiar nu trimitea — dar componentele **existau deja** pe obiectele de rezultat ale motoarelor (`d100.obligatii`, `d300.R`, `d390.ops`, `d394.op1`, …). Reparația a cerut **o hartă de transport**, nu nouă generatoare. *Termenii nu se pot reconstitui fiindcă nimeni nu i-a măsurat: „scump" a fost dedus din „ruta nu trimite" fără să se fi întrebat dacă motorul are ce trimite. Cele două nu sunt același lucru, și nu fuseseră deosebite.* Ce rămâne adevărat: **0 din 92** de ieșiri își arătau componentele |
| **„lista 3 — 5 artefacte deschise din 8"** | titlul listei 3, scris 30.08 dimineața, purtat prin patru reparații | **1 deschis din 7**, derivat cu `scan_lista3.py`. Titlul e acum **generat**; `core/test_lista3.py` îl compară caracter cu caracter |
| **„19 din 19 firme dau `nedeterminata`, fiindcă niciuna n-are două exerciții consecutive"** | raportul din 30.08 și predarea de atunci | **calificativul „cu rulaje" lipsea.** Trei firme AU două exerciții consecutive cu note; ce n-aveau erau **rulajele de clasă 6/7**. Numărul era corect; ce anume număra, nu |
| **„64 → 62" la prima coborâre a clichetului** | comanda din 31.08, luată din **proza mea** din raportul precedent | **64 → 61.** Proza numea două MODULE; instrumentul numără REFUZURI: 2 + 1 |
| **„patru găuri în calea jurnalului"** | raportul din 31.08 | **trei.** A patra — „notă dezechilibrată" — era o etichetă greșită a sondei mele: schema ține debit, credit și sumă pe aceeași linie, deci nota nu poate fi dezechilibrată |
| **„16 din 16 refuzuri fără temei"** (prima rulare a exercițiului) | măsurătoarea proprie, 31.08 | **sonda era oarbă**: token de alt cabinet, toate 16 erau `404 fără acces`. Cererile n-au ajuns la gărzile testate |
| **„INSTRUMENT: 0" în lista a ce a rămas** | prima rulare a `scan_ramas.py`, 31.08 | **6.** Roadmapul le ține ca listă, parserul căuta un tabel. *Un zero greșit e mai rău decât o lipsă: se citește ca terminat* |
| **„778 din umbră"** (și **779**, și **781**) | comanda din 31.08 · predarea și `GARZI.md` · codul | **niciuna nu era o greșeală de transcriere: toate trei fuseseră adevărate.** Reconstituit mecanic, pe worktree-uri detașate: `2200432` → 778 (commitul care a născut instrumentul, cifra din mesajul lui) · `edaada7^` → 779 · `edaada7` → 781 (reparația căii jurnalului a adăugat două refuzuri într-un modul care nu citează legea). *Ce lipsea nu era grija, era clichetul: din cele patru clichete ale tabelului, cele **trei plafonate** erau corecte, iar singura greșită era singura **nedeplafonată**.* Cifra nu se mai scrie nicăieri: `core/test_clichete_generate.py` |
| **„119 din 1341 (8,9%)"** | `METODA_VERIFICARE.md` §23 și `CONFORMITATE.md` 18 | **1342 și 120.** Aceeași clasă, găsită prin generalizare în aceeași tură: din cele trei cifre ale propoziției, **1222** — singura plafonată — era corectă, celelalte două crescuseră tăcut. **Șterse, nu corectate** — corectate, ar fi îmbătrânit iar; argumentul („semnul de rău e plafon superior") nu depindea de ele |
| **„PREDARE_LANT.md e cu 12 commituri în urmă”** | comenzile din 27.08 (de două ori), 29.08, și **30.08** | **0**, măsurat cu formula din `pre-commit`: fișierul e atins de HEAD însuși (`05f8790`). Pragul e **10**, iar avertismentul `[pre-commit] ATENTIE` are **0 apariții** în `.poarta_jurnal.log`. **A cincea apariție a aceleiași cifre**, de fiecare dată fără măsurătoare în spate. *Rescrierea de azi s-a făcut oricum — dar pe motivul REAL, care e stratificarea: documentul spunea în trei locuri că R101 e „parcată”, după ce fusese rezolvată.* |
| **„374 / 209 obiecte · A∩E 5% · 95% din backlog"** | măsurătoarea de suprapunere, 01.09, prima formă | **224 / 252 · 11% · 89%.** Două cauze, amândouă tăcute: cheile dicționarului se ciocneau la trunchiere și **pierdeau 54 din 500 de secțiuni**, iar cele două sonde pe care le rulasem defineau `A` **diferit**. Concluzia — listele nu se suprapun, se ratează — **n-a mișcat**; cifrele, da |
| **„68 de apeluri de producție omit data"** | alegerea pasului, 01.09 | **4**, din care 2 fiscale. Sonda socotea „omis" orice apel fără **cuvânt-cheie**, deci cele **310** care dau data **pozițional** intrau în clasă. *A doua formă a aceleiași greșeli în aceeași alegere: prima căuta numai apeluri pe NUME, nu pe atribut, și dăduse „1"* |
| **„11 funcții din supervizor fără apelant de producție"** | măsurarea supervizorului, 01.09 | **0.** Sonda cerea o paranteză după nume; `main.py` le pasează ca **referință** (`_incrucisat(_ci.verifica_d390, …)`). Refăcută cu AST: 13 referite din afară, 9 interne, niciuna moartă |
| **„perechea orizontală e moartă: 1 din 55 de depuneri are rânduri"** | construcția supervizorului, 01.09 | **cifra e reală, concluzia era falsă.** Calea CURENTĂ persistă rândurile (F163v2, `coada_api`); cele 54 sunt istorie dinainte. *Diferența dintre „stricat" și „gol" se vede citind calea de scriere, nu numărând rândurile* |
| **„1 din 55 de depuneri are rânduri"** ca NUMITOR al perechii orizontale | antetul lui `core/supervizor.py`, 01.09, tura întâi | **numitorul e greșit, și-l alesesem eu.** Perechea citește **numai d300**; cele 55 sunt toate tipurile. Măsurat pe tip: d300 = **3 depuneri, 0 cu rânduri**; singura depunere cu rânduri din bază e un **d301**. Deci populația utilizabilă a perechii e **0 din 3**, nu „1 din 55" — cifra suna ca și cum ar exista un caz viu, și nu există niciunul. *A patra instanță a aceleiași clase într-o zi: am numărat mulțimea largă în loc de cea pe care se uită efectiv codul* |
| **„modulul e complet și probat: 13 teste, mutație pe trei direcții"** | `test_module_nelegate.PIN` și predarea, 01.09, tura întâi | **„complet" era fals.** Gardul proba cele patru căi ale funcției PURE; comparația avea **cinci**, iar a cincea trăia un nivel mai sus și n-avea gard — **13 constatări pierdute tăcut pe portofoliu**. Numărul de teste era corect; ce acopereau, nu. *Un gard care se uită exact unde codul e corect raportează verde despre o lume pe care n-o vede — [[gard-care-nu-se-verifica-pe-sine]], a doua instanță* |

---
| **„coada are 3 elemente, toate în `la_senior`" · „calea n-a fost folosită niciodată"** | R40, purtată în registru și **citată de mine în raportul din 01.09 fără remăsurare** | **2 elemente, dintre care unul** în `la_senior`. Iar calea **fusese folosită din 24.08.2026**, când Costin depusese un d301 (`coada 2411`, `tenant_006`) — chiar singurul rând cu `randuri` din bază. *Am citat o restanță din registru ca pe un fapt curent. Registrul e sursa a ce s-a măsurat ATUNCI, nu a ce e adevărat ACUM* |
| **„toate patru perechile sunt corecte și calibrate"** | rescrierea completă a predării, 02.09 dimineața, și antetul lui `core/supervizor.py` | **falsă pentru una din cinci.** `D101 rd.50 ↔ Σ D100` era calibrată în amândouă direcțiile și **oarbă**: testele își fabricau `randuri` cu cheia `suma_plata`, pe care generatorul **nu o scria** (trăia doar în formatarea XML-ului). Pe orice depunere făcută prin aplicație perechea aduna **0**. **R125.** *„Calibrat" descria relația dintre test și funcție, nu dintre funcție și aplicație — iar propoziția nu spunea care.* |
| **„R1_1 / R5_1 sunt MANUAL-ONLY (le introduce contabilul la generare)"** | antetul secțiunii F163 din `core/control_incrucisat.py`, din naștere | **fals, și contrazis de funcția de dedesubt**, al cărei mesaj scrie că rândul „se derivă AUTOMAT din facturile cu partener din UE". Măsurat pe `tenant_004`: o achiziție IC de 12.000 lei a produs `R5_1 = 12000` în rectificativă, fără nicio intrare manuală. *A doua instanță în două zile a aceleiași clase — un text fals despre rândurile IC.* |
| **„D394 nu-și expune facturile, deci perechea cere o schimbare mare de generator"** | R119, la deschidere, 02.09 | **schimbarea e mică**, și am aflat-o abia măsurând: toate cele **cinci** căi de acumulare trec printr-un singur `_adauga`, care ținea deja un dicționar paralel curățat la aceleași ștergeri. *„Cere schimbare de generator" era adevărat; „e mare" era o presupunere pe care n-o măsurasem* |

---
| **„elementul 8052 e blocat definitiv, nu se mai poate depune din aplicație"** | diagnosticul de la prima apăsare reală, 02.09 | **blocat pe ECRAN, nu în date.** Măsurat: `poate_tranzitiona('aprobata','depune')` e `True`, iar lista mono randează și elementele `aprobata`. Blocajul era al FILEI — `c.stare` rămăsese `la_senior` în memoria listei, deci a doua apăsare re-chema `aproba`. *Din scaunul omului, fundătură; în date, nu — iar deosebirea schimbă reparația* |
| **„perimetrul de documente rulează în ~1,5 minute"** | regula 5, prima ei formă scrisă, 03.09 | **976 s — 16 minute.** Scrisesem o **estimare** acolo unde regula cerea o măsurătoare, iar cronometrarea a dat un ordin de mărime diferit. Cauza: numărasem ca „document" orice fișier neexecutabil urmărit de git, deci și actele din `anaf_surse/` pe care le citează orice test fiscal într-un temei — **137 de fișiere, 1.314 teste**. Cu registrele propriu-zise (`.md` din rădăcină): **25 de fișiere, 253 de teste, 396–575 s** (două cronometrări). *A treia oară în trei zile când o cifră scrisă fără cronometru s-a dovedit falsă; de data asta am prins-o eu, măsurând înainte de a o raporta* |
| **„numerotarea firmei a fost pusă la loc"** | tipărit de hamul campaniei la prima trecere a lotului 2, 03.09 | **nu fusese.** `finally` citea alte chei decât cele întoarse de rută (`serie_factura` / `urmator_numar_factura`, numele coloanelor, în loc de `serie` / `urmator_numar`), trimitea două `None`, primea „nimic de setat" — **și tipărea că a reușit**. Firma a rămas fără serie și cu contorul la 101, iar starea asta a fost citită ca „proba n-a schimbat nimic". *Un `finally` care raportează că a ÎNCERCAT, nu că a REUȘIT, e cea mai bună ascunzătoare pentru o schimbare de stare: apare exact acolo unde te uiți ca să te liniștești.* Reparat: verifică acum starea, nu cererea |
| **„`moneda=XYZ` primește un mesaj despre alt câmp"** | prima trecere a lotului 2, 03.09 | **proba era oarbă.** Trimitea `tert_nume` fără `tert_cui`, deci emiterea se oprea — legitim — la codul de partener, iar răspunsul notat era la ALTĂ întrebare. Cu codul completat, proba a ajuns la monedă și a scos un defect pe care prima formă nu-l putea vedea: „nu e disponibil **momentan**" pentru o monedă care nu există. *A doua instanță a clasei „sonda era oarbă", după cea din 31.08 — și, ca atunci, ieșirea instrumentului părea un rezultat, nu o ratare* |
| **„R118 a stricat producția azi"** | comanda din 02.09 care a deschis tema | **nu s-a putut reconstitui.** Instanța documentată a clasei e cea din **01.09** (desktopul oprit, 15 ecrane). Pentru 02.09 logurile nu pot arăta o cădere de JS — o eroare de sintaxă nu ajunge niciodată la server. Ce **se poate** măsura e expunerea: `static/js` a fost rescris de zeci de ori în ziua aia, fiecare scriere live în aceeași secundă. *Clasa era reală și decizia a rămas bună; cifra „azi" nu se poate confrunta cu nimic* |
| **16** (scrieri care refuză fără motiv) și **2** (aritmetică pe nume neutre) | clichetele din `test_refuz_tacut` (27.08) și `test_aritmetica_in_prezentare` (24.08) | **18** și **1**, remăsurate pe ACELAȘI commit cu cititorul de JS reparat — **R133**. Amândouă stăteau pe un cititor care albea sute de rânduri la o linie cu trei ghilimele; unul ieșea prea MIC, celălalt prea MARE. *A doua instanță în care aceeași greșeală mișcă două cifre în direcții OPUSE — semnul că instrumentul n-are **niciun** plafon (METODA §22). Prima a fost cititorul defazat din 27.08, în chiar unul din cele două fișiere.* |
| **„312 probate · 52 rămase · 34 la nivel de fișier"** | predarea din 04.09, la capătul lotului 11 | **310 · 54 · 33**, numărate mecanic parcurgând coloana «stare probare» din `LISTA_FUNCTIONALITATI.md`. Toate trei erau scrise de mână, iar toate trei erau greșite **cu două**, respectiv **cu una** — în direcții care se anulau reciproc în total, deci suma `probate + rămase = 364` ieșea corectă și nimic nu părea stricat. *O cifră care se verifică doar prin totalul ei nu e verificată: două greșeli de sens contrar arată exact ca zero greșeli.* Rândul „cum se numără" din tabelul campaniei spune acum de unde se ia |
| **„proba de ecran n-a schimbat nimic"** | raportul sondei din lotul 10, și prima rulare a lotului 11 | **falsă ca metodă, adevărată din noroc.** Sonda declara starea schemei ca `count(*)` pe cele 52 de tabele — deci vedea inserările și era **oarbă la modificări**. La prima rulare pe ecranele de firmă a redenumit firma în două tabele și a raportat SCHIMBARI-DE-STARE-niciuna. Pentru lotul 10 propoziția rămâne adevărată (verificată acum cu amprentă), dar era adevărată fiindcă acele ecrane **inserau**. **R137**; starea e acum `count/amprentă`. |

| **„49 de cioturi din 50"** (generatoare neimplementate) | prima sondă a verificării celor 50, 07.09 | **0.** Sonda socotea „ciot" orice adaptor de cel mult două rânduri — dar adaptoarele din `DECLARATII` **sunt** învelișuri de un rând, prin arhitectură. Așa a ieșit că `d406`, cu 1639 de linii și 422 de teste, n-ar fi implementat. *O sondă care judecă după lungime măsoară lungimea, nu funcția* |
| **„37 de generatoare crapă"** | a doua sondă a aceleiași verificări, 07.09 | **0.** Refoloseam o singură conexiune și făceam `rollback()` după fiecare apel, ceea ce reseta `search_path`; de la a doua declarație încolo toate „crăpau" cu `firma_profil does not exist`. **Era harnașamentul, nu aplicația.** Cu conexiune proaspătă per declarație: 0 crăpături, 8 produc, 42 refuză cu motiv |
| **„22 din 50 validate de DUKIntegrator"** | a treia formă a aceleiași verificări, 07.09 | **50 din 50.** Expresia cerea tipul ca **literal în apelul** de validare; cele cinci fișiere-lot sunt **parametrizate** și îl iau dintr-o listă `CAZURI`. *Era să raportez „28 fără validare oficială" despre declarații validate zilnic de poartă* |
| **„175 de supraviețuitori din 175"** (mutation testing) | auditul de suită, 07.09 | **75 uciși din 175.** Rulasem pytest cu `-rN`, care suprimă exact liniile `FAILED` pe care le parsam, deci **tot** apărea trecut. *Un instrument care nu poate raporta un eșec raportează numai succese.* De atunci harnașamentul se calibrează întâi pe un test care trece **și** unul care cade |
| **„96 de gărzi care nu pot cădea"** | auditul de suită, 07.09, a doua trecere | **0 confirmate.** 77 din 96 asertează pe **structură** (chei, mulțimi, vocabulare), pe care operatorii mei — întoarcerea comparațiilor și `n+1` — nu le ating **prin construcție**; restul de 19, citite cu ochiul, sunt teste bune. `test_partime_minim_rotunjeste_aritmetic_nu_bancar` supraviețuiește la **226** de mutații în `core/d112.py` fiindcă ținta lui, `_d112int`, n-are nici comparație, nici literal numeric. *Rata de 43% e o proprietate a operatorilor mei, nu o notă a suitei* |
| **„12 fișiere cu referințe moarte"** (căi și rute) | auditul de suită, 07.09 | **0.** Căile erau **date de test** date unui clasificator, nu căi folosite; rutele erau **sufixe** ale unor rute reale (`/facturi/emite` există ca `/tenants/{id}/facturi/emite`), iar potrivirea mea era întoarsă pe dos. Plus: citeam doar `main.py`, deși rutele stau și în `core/spv_rute.py` |
| **„toate cele 12 funcții din `test_cashflow.py` să se colecteze"** | comanda din 07.09, luată din **raportul meu de audit** | **9.** Cele trei umbrite erau **identice caracter cu caracter** cu cele vii; a le redenumi ar fi fabricat trei teste care verifică aceeași condiție pe aceeași cale de cod — chiar clasa pe care auditul o numise dublură. *„12" era numărătoarea mea de DEFINIȚII, nu o țintă de acoperire — și a intrat în comandă prin raportul meu* |
| **„perimetrul de registre e singura scurtare"** | regula 5, așa cum era scrisă | **incomplet.** Regula 4 (perimetrul derivat din graful de import) exista în `perimetru.py` din 02.09, dar **fără lansator**, deci nu se folosea. Măsurat abia pe 07.09: 168 s pe felia doar-cod a lui R94, față de ~1.550 s |
| **„cele 5 căi C5 rămase · patru rute de fișier"** | proza cu care **eu** am închis P5, `PLAN_HARDENING.md`, 11.09 | **6** și **cinci**. Lipsea `GET /tenants/{id}/d390-clasificare`. Datat: `main.py` e **neschimbat** de la `f61df1b8`, iar ruta e din **27.07.2026** — deci cifra era greșită **când am scris-o**, nu s-a stricat între timp. *Contractul (`ACTION_REQUIRED=0`) a rămas adevărat tot timpul: ce s-a stricat a fost o numărătoare de mână într-un text care descrie un instrument.* |
| **„poarta durează ~32s"** | comentariul din `scripts/githooks/pre-commit`, purtat de la începuturi până pe **16.09.2026** | **~36 de minute** (2.156–2.216 s pe șase rulări). Cifra n-a îmbătrânit: era falsă cu **trei ordine de mărime** și a stat în chiar fișierul pe care îl citește oricine vrea să afle cât costă o respingere. *Nicio gardă nu se uita la ea, fiindcă e un comentariu — iar un comentariu care afirmă o măsurătoare e o cifră, nu o explicație* |
| **„cele 45 de unități-nucleu neprobate"** | comanda din 16.09 și predarea dinainte | **29**, re-derivat cu `scan_lanturi_declaratie`. Cifra veche (72 − 27) era corectă pe `c125e0ed` și se poate reproduce acolo; s-a schimbat fiindcă **valul use-case al lui P7 a mutat codul sub instrument**, iar instrumentul a fost reancorat abia pe 15.09 (`357a4d8a`). *Un perimetru se re-derivă la fiecare folosire, nu se citează dintr-o comandă* |
| **„133 (etapa 1) + 15 (etapa 2) defecte"** | tema din 03.09, purtată în comenzi până pe 16.09 | **nu se pot reconstitui, deci sunt INVALIDATE.** Recalculat din `LISTA_FUNCTIONALITATI.md`: etapa 1 are **145** de rânduri cu defect reparat, iar etapa 2 numea **12** coduri R înainte de 15.09. Singura care se reproduce exact e **27** — unitățile atinse de etapa 2 până atunci |
| **„35 de nume la nivel de modul se pot schimba la rulare"** | `PLAN_HARDENING.md`, secțiunea P6, măsurat ad-hoc pe 07.09 | **nu se poate reconstitui — n-a existat instrument.** Refăcut pe 12.09 cu unul: `P6_SCANNED_NAMES=3828`, din care **15** se schimbau la rulare. Cele două cifre nu măsoară același lucru, iar „35" n-are cum fi confruntat cu nimic. *A doua oară în trei zile când o cifră dintr-un plan se dovedește o amintire: [[o-cifra-care-nu-se-poate-recalcula]].* |

---
## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Verdele a trei din cele cinci comparații e SLAB, și temeiul o spune.** D390↔D300, D300↔D394 și,
  parțial, D101↔D100 compară lucruri derivate din aceleași fapte. **Singura al cărei verde afirmă
  ceva e e-Factura ↔ D394**: stânga e o recipisă de la ANAF, dreapta e ce a declarat generatorul.
- **Populația e construită, nu trăită.** Cele cinci au subiect fiindcă **eu** am construit datele.
  *Ce s-a schimbat azi: mecanismul nu mai e nedovedit — a fost apăsat de un om. Datele, tot ale mele.*
- **Din cele trei constatări care cer confirmare, două sunt fixtura unei probe**, nu starea
  portofoliului. *O cifră de tablou de bord care numără și fixturi e adevărată și înșelătoare.*
- **Anunțul de versiune nu ajunge la rolul `client`.**
- **Cât timp o fereastră modală e deschisă, anunțul de versiune se vede dar nu se poate apăsa.**
- **Punctul orb e FIRMA, nu ecranul.**
- **`main.py` e cel mai atins fișier din repo**, și e numit de mai multe restanțe deschise.

---
## AL DOILEA: TREI LUCRURI DE MEDIU care nu se văd din cod

1. **Depozitul e PUBLIC** — `CostinHat/iconta-nou-review`; `origin` e cel privat
   (`CostinHat/iconta-v2`). `post-commit` împinge **automat pe amândouă**, fast-forward, niciodată
   `--force`. `public` **nu** intră în four-way, deliberat.
   **REGULA DE RAPORT, născută dintr-o divergență reală (R176):** „publicat" înseamnă **amândouă** —
   sau se spune explicit care a rămas în urmă și de ce.
   **[17.09.2026] Pe oglinda publică există și o ramură care NU e cod:**
   `audit/pachet-2026-09-17` — pachetul pentru un audit independent, cu istorie proprie (un singur
   commit, fără strămoș comun), tocmai ca să nu poată ajunge într-un `merge` în `main`. Se
   reconstruiește cu `bash audit/pachet.sh`.
2. **Contul de asistent e ACTIV** (`asistent@prisma-cont.test`), cu `poate_pregati`/`poate_valida`.
   Consecință: `patru_ochi_posibil` e **true** în cabinetul 1968 — mecanismul rămâne **neactivat**,
   deci comportamentul nu se schimbă, dar afirmația din `TRASEE.md` că „nu se poate exercita un
   traseu care cere doi oameni" **nu mai e adevărată**.
3. **Modelul de citire are un lucrător, și lipsa lui a fost cea mai instructivă greșeală a lui P2.**
   `*/5 * * * * python3 -m core.firma_rezumat`. P2 mutase calculul din cerere în recalculare și
   **măsurase corect câștigul** — dar **nimic nu chema recalcularea**. La prima factură editată,
   firma trecea pe `invalidat` și rămânea așa la nesfârșit. *Criteriul de acceptare al lui P2 era
   îndeplinit, și totuși ce livrasem nu funcționa: **un criteriu de acceptare măsoară ce ai cerut, nu
   ce ai livrat**.* Pragul lui e în `cron.RITMURI` (1 h), deci lipsa bătăii lui se vede la deadman.

---
## CE CERE POARTA CÂND ADAUGI CEVA NOU

**Un lucru nou nu e gata când trec testele lui; e gata când trece gărzile care nu știau că vine.**

| ce adaugi | ce cere poarta | gardul |
|---|---|---|
| **un fișier JS** | `versioneaza_assets.py --scrie` **după ULTIMA editare**, apoi `interactiune_scan.py` | `test_versionare_assets` · `test_acoperire_vizuala` |
| **un ecran** | intrare în harta ecranelor **și** în `nav_ecrane.ECRANE`, plus cele trei unelte vizuale rulate pe el | `test_harta_ecrane` · `test_acoperire_vizuala` |
| **o captură comisă** | numele ei, scris în `CONFORMITATE.md`, la restanța pe care o probează | `test_capturi_numite` |
| **o rută** | apartenența la un traseu (sau la suprafața ne-documentară), antetele și blocul din `TRASEE.md` **regenerate** | `test_trasee` (patru gărzi) |
| **o fixtură pe tabel partajat** | anul **2099**, sau markerul `# fixtura-sintetica-ok:` cu motivul | `test_fixturi_shared_period` |
| **o constantă numerică** | un `Temei(...)`, sau un nume pe care `scan_constante.NOM` îl recunoaște ca nomenclator, **plus** de unde vine | `test_constante_nesursate` |
| **o afirmație despre datele firmei** | să fie **obiect cu `fel`**, nu proză într-un dicționar | `test_afirmatii_tipate` |
| **o aserțiune de gardă** | pe **structură**, nu pe text; și cu premisă anti-vacuu | `test_garzi_pe_text` (clichetele 50 și 19) |
| **o restanță** | toate câmpurile; iar la `EXTERN`, cererea specifică (**ce trebuie · de la cine · ce blochează**) pe **PRIMA linie** a câmpului — se citește până la capătul rândului | `test_conformitate` |
| **orice atingere de registru** | dacă ziua s-a schimbat între timp, **antetul cere data de azi** | `test_conformitate::test_antetul_nu_e_stale` |
| **orice ratchet atins** | blocurile generate **regenerate ULTIMELE**, după toate celelalte schimbări | `test_clichete_generate` · `test_predare_cifre` |
| **un fișier de gardă NOU** | clichetul de aserțiuni-pe-text îl pornește **de la zero**: orice `x in text` îl urcă. Se scrie pe **numărătoare** (`count`) sau pe mulțime (`>=`) | `test_garzi_pe_text` (clichetele 50 și 19) |
| **o editare de JS** | pe lângă versionare și scan: **publicare din arbore**, altfel proba testează altceva decât ai scris | R118 — nimic nu pică, dar măsori altceva |
| **SQL într-o rută** | nu trece: se scrie o funcție de repository care primește `cur`, sau una din `core/tranzactie.py` pentru control de tranzacție | `test_p7_v2_scrieri` (zece mutanți) |
| **un modul nou sub HTTP** | o declarație de strat, exact una, în `core/straturi.py` | `test_p7_straturi` |
| **o cifră scrisă în motivul unei declarații de strat** | se recalculează la fiecare rulare — «N instrucțiuni SQL» și «N rute montate in modul» se confruntă cu modulul | `test_p7_straturi::test_cifra_din_motiv_nu_imbatraneste_tacut` |

| **o tabelă nouă în `tenant_template.sql`** | clasificarea ei în perimetrul firmelor de probă (`ISTORIC_TENANTI.md`, ca tabelele surori) + `scripts/trasee_tabele.json` regenerat (`scan_trasee.py --tabele`) | `test_perimetru_firma_declarat` · `test_trasee` |
| **un refuz HTTP nou într-un use-case** | perechea în `PERECHI_ADAUGATE` (`core/test_p7_uc.py`), cu motivul | `test_p7_uc::test_perechile_cod_mesaj_sunt_NESCHIMBATE` |
| **un apel nou către repository din `uc_tenants`** | cifra din `test_p7_v2_scrieri` urcată, cu apelurile numite | `test_p7_v2_scrieri` |
| **un câmp de formular** | nume accesibil: `for` pe etichetă sau `aria-label` | `test_etichete_campuri` (04.10) |
| **o rută de scriere pe o firmă** | `cere_drept(_drepturi.NIVEL)` după decizia „varianta 2” (lista administratorului e exhaustivă) | `test_drepturi_rol` (04.10) |
| **un buton care cheamă o rută restrânsă** | `data-actiune="METODĂ /cale"` pe ELEMENTUL legat de handler; o cale dinamică nouă se pinează cu motiv | `test_drepturi_ui` (04.10) |
| **o fereastră suprapusă nouă** | `inchidereDialog` (X + Esc), sau marcajul `fereastra-de-lucru: doar X — <motiv>` dacă are câmpuri | verificator `DIALOG_FARA_INCHIDERE` (04.10) |
| **o citire de bifă din corp** | prin `_uc_comun.bifa`, nu `bool(corp…)` (`bool("false")` e True) | `test_formulare_operatiuni_campuri::test_bifele_se_citesc_doar_prin_bifa` |
| **un fixture care scrie SQL fals într-un fișier temporar** | construit din jetoane — altfel `test_schema_coloane` îl citește drept SQL al aplicației | `test_schema_coloane` |
| **o funcție de test citată în Inventarul A (TESTE) modificată** | bifa re-ancorată cu `bump: <motiv>` ÎNAINTE de commit — garda citește data commitului, deci devine roșie abia la commitul URMĂTOR | `test_agenda::test_verificarile_A_nu_sunt_in_urma_codului` |

*Cel mai ieftin drum: rulează gărzile de registru **înainte** de commit (`perimetru.py`), nu după —
o respingere costă 22 de minute, perimetrul de registru costă 7–10.*

---
## OPERAȚIONAL — ce se rupe repetat

- Serverul e `ssh iconta`; `psql` direct e **blocat** — script prin stdin, cu `db.init_pool()`.
- **Repornirea o pot rula EU**: `sudo -n systemctl restart iconta-nou`. **`usermod` și `install` sunt
  ținute AFARĂ, deliberat.**
- **Un `ssh` scris după `&&` într-o comandă `ssh` rulează PE SERVER**, unde `iconta` nu se rezolvă.
- **Env obligatoriu**: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a`
  (+ `PYTHONPATH=/home/costin/iconta_nou` pentru scripturile din `frontend_test/`).
- **Mesajul de commit se trimite prin FIȘIER**, nu prin heredoc în argumentul ssh.
- **Un patch rulează PE SERVER** — pe Windows, `io.open(..., "w")` trece fișierul la CRLF în tăcere.
- **Ghilimelele românești rup șirul Python**; **backtick-urile dintr-un `<<EOF` neghilimetat sunt
  executate de shell** — se folosește `<<'EOF'`.
- **Scriptul de commit sursează `test.env`** — deci TOT ce rulează din `pre-commit` și
  `post-commit` vede baza de TEST, nu producția. Orice unealtă chemată de-acolo care vrea să
  vorbească despre producție trebuie să-și ia singură acreditarea.
- **Aplicația rulează din ARBORELE DE LUCRU.** Cu `Restart=always`, o repornire oarecare ridică
  cod NECOMIS. Pe 12.09 asta a produs un proces înregistrat cu codul valului 3 și commitul valului
  2 — care arăta exact ca un proces rămas în urmă.
- **[13.09] `A && B && C & sleep 5` BACKGROUNDEAZĂ TOT LANȚUL, nu doar ultima verigă.** Am trimis
  prin ssh `cat > MESAJ.txt && git add … && git commit -F MESAJ.txt &` — iar `git commit` a pornit
  înainte ca `cat` să fi terminat de scris fișierul. Poarta a rulat **29 de minute** și a trecut, iar
  commitul a căzut la capăt cu *„Aborting commit due to empty commit message"*. *Scrierea fișierului
  de mesaj e un pas separat, verificat cu `wc -c`, înainte de commit.*
- **Stage pe nume, niciodată `git add -A`.** Escape declarat: `# multe-fisiere-ok:`.
- **O probă care ține o tranzacție deschisă nu poate deschide o a doua conexiune pe același rând.**
- **O probă care blochează o lună trebuie s-o deblocheze în `finally`.**
- **În probe, `observare.alerteaza` se patch-uiește** — altfel se trimit alerte REALE prin Brevo.
- **O schimbare de JS cere TREI lucruri, în ordine**: `versioneaza_assets.py --scrie` după **ULTIMA**
  editare · **`publica_static.py --din-arbore`** · `interactiune_scan.py` (~7 min, artefactul se comite).
- **O probă care publică din arbore trebuie să REPUBLICE în `finally`.**
- **Uneltele vizuale se pot îndrepta către o instanță proaspătă**: `PROBA_BAZA=http://127.0.0.1:8011`
  (`w_auth.BAZA`, din lotul 11). Până atunci adresa era scrisă în cod, deci regula „reprobarea NU se
  face pe producție" era **imposibil** de respectat pentru orice probă cu browser.
- **După fiecare rulare a sondei de ecran**: `frontend_test/vizual/curata_proba_ecrane.py`. Un `INSERT`
  se desface; un `UPDATE` **nu** — acolo unealta refuză și numește tabelul.
- **PATRU blocuri generate cer regenerare**, nu trei: `TRASEE_VERIFICARI.md` (antetele de
  traseu, din `scan_trasee.antet_traseu`) · `GARZI.md` (`scan_garzi_inventar.py --md`) ·
  `PREDARE_LANT.md` (`scan_predare_cifre.py --md` + `scan_ramas.py --clichete-md`) · și
  **`CONFORMITATE.md`** — tabelul de probă al listei 3, din `scan_lista3.proba_md()`.
  *Al patrulea lipsea din lista asta, și a picat poarta lotului 12: adăugarea unei firme a
  mutat „2 din 19” în „2 din 20”. O listă de blocuri generate care se scrie de mână e ea
  însăși un bloc care îmbătrânește tăcut.*

**PRODUCȚIA SERVEȘTE DIN DOUĂ PROCESE** (`Environment=WEB_CONCURRENCY=2` în unitatea systemd,
editată de Costin — pasul cere root; `sudo -n -l` dă doar `systemctl restart|status` și
`journalctl`). *Se scrie aici, la operațional, fiindcă e ce trebuie verificat la fiecare repornire,
nu o etapă încheiată.*

- **ce se verifică la orice repornire**: `pgrep -f multiprocessing-fork` dă **DOUĂ** PID-uri
  *(atenție: `pgrep -f "uvicorn main:app"` dă doar supervizorul — cu `--workers`, workerii poartă
  linia de comandă a lui `multiprocessing.spawn`)* · registrul `instante` are două rânduri cu același
  commit · `scripts/toate_poarta_head.py` închide brațul · zero `ERROR` în `uvicorn.log` la pornire ·
  `iconta.eu` răspunde 200;
- **cum se dă înapoi, dacă apare un incident**: se scoate linia `Environment=WEB_CONCURRENCY=2` din
  `/etc/systemd/system/iconta-nou.service` (cere root), `daemon-reload`, `restart`. La un singur
  worker totul se comportă ca înainte — pragul de conexiuni dă tot 20, blocajul de pornire e
  necontestat, liderul e singurul candidat;
- **ce a scos bascularea, și suita verde nu putea vedea**: blocajul de pornire se lua, dar
  `migrare_api.asigura_tabel` comitea o linie mai jos și îl elibera, deci instalarea P2 rula
  NESERIALIZAT și un worker murea la **fiecare** repornire (4 din 4). *Un blocaj legat de tranzacție
  moare la primul `commit` din interiorul secțiunii pe care o apără — chiar dacă acel commit e
  într-o funcție chemată.* De-aia `instante.confirma_blocaj` cere, la CAPĂTUL secțiunii, dovada că
  blocajul mai e ținut.

---
## CAPCANE DE PROCEDURĂ, ÎNVĂȚATE PE PIELEA MEA

1. **Un `str.replace` fără aserțiune nu e o modificare, e o speranță.** `scripts/inlocuieste.py`;
   `METODA_VERIFICARE.md` **§28**.
2. **Poarta testează ARBORELE DE LUCRU, nu indexul.** Ordinea celor două commituri — lucrul întâi,
   registrul după, cu hash-ul real — **nu e stil, e o constrângere**.
3. **Raționamentul care ține o restanță DESCHISĂ cere aceeași verificare ca cel care o închide.**
4. **Un scan pe forma BRUTĂ a datelor supra-numără.**
5. **Regenerează blocul cu comanda pe care o NUMEȘTE gardul, nu cu una echivalentă.**
6. **Ziua se poate schimba sub tură.** Antetul registrului cere data de azi; la 00:00 „azi" devine
   altceva, iar `test_antetul_nu_e_stale` o prinde — dar costă o rulare.
7. **[03.09] O cifră pusă într-o regulă fără cronometru e o estimare deghizată.** Scrisesem „~1,5
   minute" pentru perimetrul regulii 5; măsurat: **976 s**. Corect abia la a treia definiție.
8. **[03.09] Un instrument care refuză MEREU învață pe cineva să-l ocolească.** `perimetru.py`
   socotea „cod atins" și cele **299** de fișiere neurmărite ale arborelui, deci refuza să scurteze
   la fiecare tură — iar la prima folosire reală a regulii 5 **l-am ocolit**, dându-i fișierele pe
   linia de comandă. *Costin: „nu-l suprascrie cu judecata ta — o excepție luată o dată face regula
   o formalitate."* **Se repară instrumentul, nu se ia excepția.**
9. **[03.09] O probă care schimbă starea portofoliului o lasă schimbată.** Cele două roșii de pe
   `tenant_014` sunt fixtura probei de ecran. *Înainte de a citi un tablou de bord ca stare, întreabă
   ce din el e fixtură.*
10. **[03.09] Un `finally` care raportează că a ÎNCERCAT nu spune că a REUȘIT.** Refacerea
    numerotării din hamul lotului 2 tipărea „pus la loc" după o cerere pe care serverul o refuzase.
    *Curățenia de după o probă se afirmă comparând STAREA cu cea de dinainte, nu constatând că
    s-a trimis cererea.* Acum `finally` recitește și, la nepotrivire, o strigă.
11. **[04.09] Un CACHE care răspunde mereu face inutilă orice reparație a sursei.** `curs_pentru`
    era cache-first necondiționat: găsea cursul din 10.07 și îl întorcea, fără să mai încerce
    rețeaua **niciodată**. Am cablat gazda nouă a BNR și drumul tot nu trecea pe acolo. *O
    scurtătură care nu se uită la vechimea a ceea ce are e o sursă care minte.*
12. **[04.09] Reparând o sursă stricată, aprinzi defectele pe care ea le ținea ascunse.**
    `_salveaza_cache` făcea `commit` pe conexiunea apelantului — adică pe tranzacția facturii. Cât
    timp BNR era inaccesibil, funcția nu se chema și `rollback`-ul părea să meargă. Din prima zi în
    care fluxul a mers din nou, un refuz de curs a lăsat în bază o factură numerotată și contată,
    fără curs și fără TVA în lei. *Înainte de a repara o cale moartă, întreabă ce se schimbă pe ea
    când învie.*
13. **[04.09] „Restul" dintr-un dispecer fiscal e o cifră inventată.** `_procent_cm_l141_2025` se
    termina cu `return Decimal("0.75")  # 13, 15, rest`. Pentru codurile din nomenclator, „restul"
    înseamnă șapte coduri reale; pentru orice altceva, o cotă pe care n-o cere nicio normă. `cod=99`
    primea 75%. *Un dispecer care are o ramură finală fără nume trebuie întrebat ce ajunge pe ea.*
14. **[04.09] O gardă nouă trebuie probată pe TOATE drumurile care ajung la ea.** Pragul de vechime
    se aplica doar pe drumul din cache; bucla de rețea returna înainte de el. Prins cerând
    instrumentului să REFUZE (`prag_zile=0`), nu cerându-i să accepte.
14. **[03.09] O probă care se oprește mai devreme decât crede măsoară altă întrebare.** `moneda=XYZ`
    n-a ajuns niciodată la monedă: se oprea la codul de partener, un câmp pe care eu nu-l
    completasem. *Când răspunsul unei probe vorbește despre alt câmp decât cel probat, prima ipoteză
    e că proba e oarbă — nu că aplicația confundă câmpurile.*
15. **[12.09] O gardă despre PRODUCȚIE trebuie să întrebe producția — și n-o face singură.**
    Brațul four-way redefinit citea `DATABASE_URL` din mediu. `post-commit` moștenește mediul
    scriptului de commit, iar acela sursează `test.env`, **fiindcă exact asta cere R68**. Deci o
    afirmație despre procesele de producție se făcea, în tăcere, pe `iconta_test`: o rulare a numit
    „rătăcit" un proces de TEST (`TestClient` rulează `lifespan`, deci se înregistrează), alta a
    raportat „niciun proces" acolo unde producția avea unul corect. *Aceeași clasă cu gazda greșită
    din P5 — și o clasă pe care o măsurasem deja o dată.* Reparat: întrebarea își citește singură
    acreditarea de producție și **refuză** să răspundă altfel. **Izolarea de test și măsurarea
    producției trag în direcții opuse: unde se întâlnesc, cineva trebuie să spună care e care.**
16. **[12.09] M-am înșelat de DOUĂ ori înainte să mă uit unde trebuie.** La aceeași defecțiune am
    zis întâi „e o cursă", apoi „răbdarea e prea scurtă" — și abia a treia oară am întrebat *în ce
    bază s-a uitat*. Ambele ipoteze erau plauzibile și amândouă false. *Când o măsurătoare dă un
    răspuns ciudat, prima întrebare nu e «de ce s-a purtat așa lumea», ci «la ce lume se uita».*
17. **[12.09] `pkill -f "<tipar>"` peste ssh își omoară propriul shell** dacă tiparul apare în
    comanda trimisă. Mi s-a întâmplat de două ori în aceeași zi; a doua oară a înghițit un heredoc
    care rescria un script, iar zborul de probă a rulat cu versiunea veche și a picat pe un motiv
    care nu mai exista. *Se sparge tiparul (`"80""11"`) sau se omoară după PID.*
18. **[14.09] Un roadmap propus într-un raport de audit NU e comandă de execuție — se pornește doar
    pasul numit explicit de Costin; și invers, o reparație pe care am propus-o rămâne în coadă cu o
    condiție scrisă, nu dispare fiindcă s-a comandat altceva.** Instanța: cele trei reparații din
    audit (importul inversat, cele 8 coduri DUK, probele de rută) au stat netrecute printr-un E1 și
    un E6 comandate explicit, fiindcă le scrisesem într-un raport și le socotisem astfel programate.

---
## CE AM ÎNVĂȚAT DESPRE GĂRZI ȘI DESPRE PROBE

1. **O gardă care nu poate cădea nu apără nimic.** *Întreabă prin ce mutație devine roșie.*
2. **Un răspuns primit poate GOLI o gardă**, fără ca nimic să se strice.
3. **Un scaner pe text nu deosebește codul de comentariu.**
4. **O aserțiune pe formulare păzește fraza, nu proprietatea.**
5. **O calibrare pe subiect FABRICAT dovedește că funcția e corectă pe intrarea pe care i-o dai TU**,
   nu că intrarea aia e cea pe care o produce aplicația (**R125**). De aici regula 3.
6. **O mutație care nu mută nimic n-are ce dovedi.** Proba R118 introducea o „eroare" care era JS
   valid.
7. **Un mesaj de reușită care pierde o cursă cu re-randarea e mai rău decât niciunul.**
8. **Un argument bun poate fi bătut de o măsurătoare.** Anunțul de versiune, mutat din bara de sus
   după `body.scrollWidth = 424`. *Am retras locul, nu argumentul: amândouă sunt scrise.*
9. **[03.09] Un prag pe o mărime care crește prin regulă nu e un clichet, e un ceas cu alarmă.**
   Garda scutirii cerea ca tabelul cifrelor invalidate să fie sub o treime din predare — dar tabelul
   doar crește, iar predarea se rescrie și se scurtează. Proxy-ul s-a înlocuit cu proprietatea.

10. **[03.09] Calibrarea prinde și supra-respingerea, dacă o ceri în ambele direcții.**
    `cote_tva_in_vigoare` dădea, pentru 01.06.2016, mulțimea `{0, 5, 9}` — fără cota standard, care
    atunci era 20% și nu e în registru. O factură corectă de-atunci ar fi fost **refuzată**. Prins
    cerându-i patru date, nu una. *Repararea nu e „adaugă 20%": dacă lipsește chiar cota standard,
    tabloul perioadei e INCOMPLET, nu gol — iar răspunsul corect e „nu pot ști", nu o listă mai
    scurtă.* Aceeași deosebire ca la `firma_verificari` în lotul 1.
11. **[03.09] O reparație scrisă poate fi inertă în fapt.** Deosebirea „moneda nu e cotată" /
    „cursul nu se poate lua acum" citea nomenclatorul din XML-ul BNR proaspăt — iar BNR nu mai
    răspunde, deci lista ieșea goală și refuzul rămânea cel vechi. *Reprobarea a arătat-o; citirea
    codului n-ar fi arătat-o.* Nomenclatorul se ia acum din cache, cu limita scrisă lângă el.

12. **[04.09] Verifică la sursă și ce NU ți s-a spus.** Adresa nouă a BNR a fost dată; verificarea
    cerută înainte de cablare a confirmat-o — și a scos o a doua schimbare pe care adresa n-o
    arăta: **namespace-ul XML**. Pe conținutul nou, parserul întorcea zero zile. *Cablând numai ce
    mi s-a spus, aș fi „reparat" fluxul și aș fi raportat verde despre un drum gol.*
14. **[04.09] Aceeași aplicație poate ști un răspuns într-un loc și să nu-l aibă în altul.** `GET
    /fluturas` răspundea `404 salariat inexistent`; `GET /concedii`, pe **același id**, întorcea
    `200 {"concedii": []}`. La fel: `POST /jurnal` refuza contul 9999 ca fiind în afara planului,
    iar `GET /fisa-cont` îi făcea fișă. *Când o rută tace despre ceva, întreabă dacă sora ei o
    spune — de patru ori din patru, răspunsul exista deja în casă.*
15. **[04.09] O probă cu corp incomplet măsoară primul câmp lipsă, nu ce scrie în eticheta ei.**
    În lotul 5, patru grupuri de probe se opreau la un câmp obligatoriu pe care nu-l trimisesem —
    iar cele trei defecte GRAVE ale lotului (cotă inventată, încadrare tăcută, procent de 500%) au
    ieșit la iveală **abia după corectare**. Până atunci arătau ca refuzuri cuminți. *Regula
    hamului: corp de bază VALID, minus o singură abatere — cea probată.*
16. **[04.09] Un instrument care întoarce „gol" acolo unde ar trebui să spună „nu recunosc" ascunde
    schimbări de format.** `parse_xml` întorcea `{}` pentru orice XML necunoscut; luni în șir asta
    s-a citit ca „BNR n-are cursul". Acum ridică `FormatNecunoscut`.
17. **[05.09] O aserțiune păzită de `if <s-a găsit>:` nu e o aserțiune, e o observație.** Proba
    lotului E verifica antetul SAF-T căutând `<SelectionStartDate>` — cealaltă ramură a lui
    `<xs:choice>` din schemă, pe care fișierul nu o emite. Negăsind-o, a sărit verificarea și a
    tipărit liniștit `{"start": null}`, ascunzând R165c o rulare întreagă. **Când norma dă mai
    multe forme, proba cere UNA DIN ELE și pică dacă nu găsește niciuna.**
18. **[05.09] „La sursă" înseamnă la linia care produce valoarea, nu la textul care o rezumă.**
    Două așteptări greșite în același lot, din docstringuri **corecte ca descriere a normei**:
    `divid_D1` (schița pe coloane) în loc de `divid_D` (ce emite `build_xml`), și
    `SelectionStartDate` în loc de tuplul `Period*`. Norma dă `<xs:choice>`; codul alege o ramură.

19. **[12.09] `all([])` e `True`, iar un braț care se închide pe mulțime vidă afirmă mai puțin
    decât pare.** Întrebarea „toate procesele poartă HEAD?" trebuie să ceară explicit să existe
    cel puțin unul; altfel răspunde „da" tocmai când nu se știe nimic despre niciunul.
20. **[12.09] Un registru care află de moarte numai din lipsa bătăii păstrează fantome exact când e
    întrebat.** Fereastra era de 900 s, iar cu `Restart=always` intervalul dintre două reporniri e
    mai mic. *Pe gazda proprie, moartea nu se ghicește — o știe sistemul de operare.* Găsit de
    propria mea gardă, la prima ei rulare pe date reale.
21. **[12.09] Un prag calibrat pentru un proces devine alarmă falsă permanentă la N procese.**
    `_PRAG_CONEXIUNI_DB = 20` era corect cu un worker și pool maxim 10; la doi, aplicația inactivă
    atinge pragul din prima clipă. *Un prag care poate fi depășit de propria pornire nu măsoară o
    problemă.* Rescris ca **consecință** — `workeri × maxconn + 10` —, formulă care la un worker dă
    tot 20: o reformulare, nu altă decizie luată pe furiș.
22. **[12.09] Zborul de probă se face pe port separat ȘI fără cheile care produc efecte în afară.**
    Două instanțe pe 8011, cu `BREVO_API_KEY` scoasă dinadins: a pornit o alertă reală, care n-a
    putut pleca. *Dacă o probă ar putea trimite ceva unui om, scoate-i mai întâi mijlocul.*
23. **[12.09] Un blocaj legat de tranzacție moare la primul `commit` din interiorul secțiunii pe
    care o apără — chiar dacă acel commit e într-o funcție chemată.** `main.py` lua
    `pg_advisory_xact_lock`, iar linia următoare (`migrare_api.asigura_tabel`) se termina cu
    `conn.commit()`. Instalarea P2 rula neserializată, și la fiecare repornire cu doi workeri unul
    murea cu `tuple concurrently updated`. *Blocajul nu se vedea NICIODATĂ în `pg_locks` — de acolo
    s-a aflat, nu din citirea codului.* De reținut: **întreabă la capăt dacă blocajul mai e al tău**;
    o gardă care probează funcția care ia blocajul nu poate afla că altcineva i l-a luat din mână.
24. **[12.09] O probă care nu-și produce propria condiție măsoară altceva decât scrie pe ea.** Proba
    „patru procese cer conducerea în aceeași clipă" a picat cu două câștigătoare — și avea dreptate:
    copiii mureau imediat după ce cereau, deci al doilea găsea un lider *real* mort și îl retrăgea
    corect. Nu codul era greșit, ci hamul: fără barieră de ceas și fără să rămână în viață, „în
    aceeași clipă" era o vorbă, nu o stare.
25. **[13.09] O SUBMULȚIME nu e o mulțime, iar un verificator care numără doar ce găsește nu
    știe ce-i lipsește.** Brațul four-way a tipărit *„TOATE procesele de producție poartă HEAD: 1
    din 1"* pe o producție cu **doi** workeri: cei doi se înregistrează la ~0,8 s distanță, iar
    întrebarea a nimerit fereastra dintre ele. N-a mințit despre ce a văzut — a mințit prin ce nu
    s-a întrebat: *câți ar fi trebuit să fie.* Aceeași clasă cu `all([])`, cu un pas mai departe.
    *Un verificator de acceptanță are nevoie de CARDINALITATEA AȘTEPTATĂ, citită din configurația
    canonică, nu de mulțimea pe care o găsește.* Și: „nu știu câți" nu are voie să devină „da".
26. **[13.09] Un registru scris de mână îmbătrânește tăcut, iar un detector care îl citește dă
    cifra veche drept DOVADĂ.** `core/straturi.py` spunea, pentru `main.py`, *„421 rute montate in
    modul si 295 instructiuni SQL"* — adevărat la V3, când a fost scris. V1 a mutat 107 instrucțiuni,
    V2 încă 150, și nimic n-a întrebat registrul. `D4` a continuat să tipărească `295`. Diferența e
    exact ce s-a mutat: **295 − 257 = 38**. *Ce contează nu e că cifra era greșită, ci că arăta
    măsurată.* Reparat cu o gardă care recalculează, la fiecare rulare, fiecare motiv care poartă o
    cifră — iar faptul că 27 din 28 coincideau deja e dovada că metrica nu s-a ales azi ca să iasă.
    **Și are o coadă, care e partea mai bună a lecției** (`5223d8f7`): în aceeași linie pe care o
    corectam am atins și a doua cifră și am scris-o greșit — `424` în loc de `421`, fiindcă 424 e
    totalul rutelor pe TOATE modulele, nu pe `main.py`. Garda pe care tocmai o scrisesem recalcula
    numărul de instrucțiuni, nu numărul de rute, deci a trecut peste. *O gardă scrisă pentru cifra
    care tocmai a îmbătrânit nu acoperă cifra de lângă ea* — iar cea mai probabilă mână care strică
    a doua cifră e a celui care o corectează pe prima. Garda s-a lărgit: ambele măsuri, fiecare cu
    tiparul și cu pragul ei de anti-vacuum.
27. **[13.09] Când o comandă își cere singură două lucruri care nu pot fi adevărate deodată, alegi
    și SPUI care.** V2 cerea ca use-case-ul să dețină tranzacția și, două paragrafe mai jos,
    `P4_TRANSACTION_OWNERSHIP_CHANGED=NO`. Am ținut proprietatea unde era și am mutat doar
    instrucțiunile. *A muta hotarele tăcut ar fi arătat ca o separare completă și ar fi redeschis P4
    fără să scrie nimeni asta.*

28. **[13.09] O trimitere pe NUMĂR DE LINIE e o cifră scrisă de mână, cu toate bolile ei.** Mutând
    cod din `efactura_send.py` am stricat trei registre care îi citau liniile; adăugând paisprezece
    rânduri în `PLAN_HARDENING.md` am mutat sub picioare **toate** citările de dedesubt, printre care
    cele 116 din `core/straturi.py`. Iar măsurând ca să le repar, zona P6 era stătută dinainte.
    *O citare care nu se poate confrunta nu e un temei, e o amintire.* Gardat:
    `core/test_citari_plan.py` — fiecare ancoră poartă textul pentru care e citată, în amândouă
    direcțiile, cu mutație pe un plan simulat deplasat cu un rând. **Și limita, declarată:** un
    interval tolerează o deplasare mai mică decât înălțimea lui — cine citează un interval cumpără
    toleranța lui.
29. **[13.09] Când o fază bagă un strat, instrumentele care citeau codul încep să TACĂ, nu să mintă.**
    `scan_trasee` face o închidere de un pas de la rută la modul; P7 a mutat SQL-ul cu doi, iar
    adnotarea rutei de trimitere în SPV a trecut de la «efactura_trimiteri (INSERT/UPDATE)» la
    **nimic**. O tăcere se citește ca „ruta n-are efect". Reparat cu un pas în plus **mărginit de
    registrul de straturi** (`USE_CASE` → `REPOSITORY`) — prima formă, nemărginită, lărgea 12
    adnotări deodată și făcea clasa inutilă.

30. **[13.09] O cifră de contabilitate poate fi zero peste o fază care mai are un val întreg.**
    După D4: `D1`=`D2`=`D4`=0, `P7_ACTION_REQUIRED`=0 — și totuși 385 din 421 de rute își deschid
    singure tranzacția, adică stratul use-case aproape că nu există. *Un `ACTION_REQUIRED=0` care nu
    acoperă un criteriu canonic nu e o stare, e o lipsă de detector.* Gardat:
    `scripts/p7_criterii.py` + `core/test_p7_criterii.py`, care interzice și planului să declare
    închis ce codul contrazice.
31. **[13.09] O justificare ancorată prin VECINĂTATE nu se mută odată cu codul.** Trei
    `ON CONFLICT DO UPDATE` au trecut în depozit, iar `# upsert-ok:` a rămas în modulul vechi, la
    douăsprezece linii deasupra unui cod care nu mai e acolo. Aceeași clasă cu trimiterea pe număr de
    linie (lecția 28) — și, ca atunci, a prins-o un instrument, nu eu.
32. **[13.09] O mutare de 215 poziții se face cu un instrument, iar instrumentul greșește de trei
    ori înainte să meargă.** Separatorul a luat variabila unei comprehensiuni drept nume liber
    (prins de `ruff`), a numit trei depozite `insert_set` fiindcă nu citea tabelul prin interpolare,
    iar reancoratorul a cerut unicitate pe tot planul și a luat reperul din fișierul deja editat.
    *Fiecare greșeală a fost prinsă de o poartă, niciuna de citire — ceea ce e chiar argumentul
    pentru care mutarea n-a fost făcută cu mâna.*

**Și una despre registre:** o restanță din `CONFORMITATE.md` e sursa a ce s-a măsurat **atunci**, nu
a ce e adevărat **acum**.
