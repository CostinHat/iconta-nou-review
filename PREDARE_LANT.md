Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — **planul E (de după audit) e ÎNCHIS; E5 a devenit regulă permanentă** (15.09.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-09-15**, la **închiderea planului E** — cele șase etape derivate din
  auditul de ansamblu (E1, E2a, E2b, E3 lot fiscal, E4, E6) sunt închise cu cifră, iar **E5 a ieșit
  din plan și a devenit regula 9 din `PLAN_LUCRU.md`**: *un motor fiscal deschis pentru altceva se
  lasă citibil la închidere.* Motivul e mecanic, nu estetic: o etapă are criteriu de ieșire și se
  închide, iar lizibilitatea nu se termină — motoarele se schimbă odată cu legea. *Un pas care nu se
  poate închide, ținut în plan ca pas, e o datorie care crește tăcut în dreptul unui plan altfel
  terminat.*
- **pe commit**: `0976154e`. *Predarea se scrie ÎNAINTE de commitul care o poartă; numele de aici e
  al celui precedent, prin construcție.*
- **[15.09.2026] ZIUA ASTA A SCHIMBAT ȘI CE VEDE CONTABILUL**, spre deosebire de cele dinainte: o
  **proformă nu mai intră în D300** (și operațiunea ieșită din ea nu se mai declară de două ori), iar
  **partenerul din D394 se citește de pe factură**, nu din fișa clientului. Amândouă pe decizia lui
  Costin, amândouă **măsurate pe portofoliu înainte de a schimba codul**: 47 de documente, toate de
  tip `factura` → **zero cifre schimbate azi**. Defectul era real în cod și neexercitat în producție.
  *Dacă portofoliul ar fi avut proforme, reparația ar fi rescris declarații deja depuse — și ar fi
  cerut alt plan. De-aia cifra se măsoară, nu se presupune.*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **[13.09.2026] CE A IEȘIT LA IVEALĂ CHIAR RESCRIIND, și se scrie fiindcă e clasa pe care documentul
  o păzește:** titlul spunea *„șase pași închiși"* — sunt **șapte** (P0…P6) · „interdicții, din **77**:
  **23** măsurate" — sunt **78** și **24** · iar „restanțe deschise" scria **50** într-un tabel și
  **54** în altă secțiune, în același document. *Toate trei erau cifre scrise de mână în secțiuni pe
  care regula de mai sus le declară RESCRISE — deci nu îmbătrâniseră în tăcere, ci fiindcă rescrierea
  le sărise. A treia oară în trei zile când cifra greșită e una copiată, nu una măsurată.*
- **[13.09.2026] ANTETUL A FOST STĂTUT TREI ZILE** — a rămas pe `0742e177` / 10.09 prin două
  rescrieri care au atins alte secțiuni. *Se păstrează notat: o regulă pe care documentul și-o dă
  singur nu se respectă singură.*
- **CE E RESCRIS ȘI CE E PĂSTRAT**: antetul, „unde suntem", starea și restanțele sunt **rescrise**.
  Tabelul cifrelor invalidate, capcanele, operaționalul, „ce cere poarta" și lecțiile sunt
  **păstrate** — documentul își interzice singur să le șteargă.
- **CE E REMĂSURAT**: cele patru clichete generate · blocul cifrelor despre date · inventarul
  gărzilor · numărul restanțelor deschise (`scripts/scan_ramas.py`).
- **[13.09.2026] ȘI CIFRA ASTA A FOST GREȘITĂ, TOT PRIN DERIVARE.** Am scris «5743 teste trec»
  socotind 5735 + cele 8 probe noi, în loc s-o copiez din ieșirea porții. Real: **5744** —
  rularea pe care mă bazam avea o gardă roșie (blocul din `GARZI.md`, neregenerat încă), iar ea
  a trecut la verde odată cu regenerarea. *Aritmetica pe o bază măsurată arată sigură exact cât
  o cifră copiată: rândul de mai jos spune, în text, DE UNDE se ia.*
- **[13.09.2026, valul D2] CE A IEȘIT LA IVEALĂ MUTÂND COD:** o trimitere pe **număr de linie**
  se strică la orice mutare, și nimic n-o prindea. Adăugând paisprezece rânduri în
  `PLAN_HARDENING.md`, toate citările de sub ele au început să arate spre alt text — printre
  care cele **116** din `core/straturi.py` —, iar zona P6 era stătută **dinainte** (patru ancore,
  ~nouă rânduri). Gardat de `core/test_citari_plan.py`. *A treia oară în două zile când clasa e
  «ce scrie de mână un registru despre altceva».*

- **[13.09.2026, valul use-case] CE A IEȘIT LA IVEALĂ MUTÂND LOGICA APLICAȚIEI, și e clasa zilei:**
  **întreaga mașinărie de gărzi doc↔cod era ancorată pe o presupunere nescrisă — că logica aplicației
  stă în `main.py`.** Mutând-o în `core/uc_*.py`, ~40 de gărzi au devenit deodată oarbe sau roșii, nu
  fiindcă s-a stricat codul, ci fiindcă se uitau unde nu mai e nimic. *Nicio gardă n-a fost slăbită ca
  să treacă: fiecare s-a re-ancorat prin accesorul comun, cu semantica ei.* Iar **două scanere aveau
  `main.py` ca punct orb DECLARAT** (`scan_data_curenta`, `scan_constante`): valul le-a închis gaura,
  iar clichetele lor au **urcat** — cu lista exactă a cazurilor nou-expuse, fiecare regăsibil în
  `git show HEAD:main.py`. *Un clichet care urcă fiindcă instrumentul vede mai mult nu e o datorie
  nouă; e datoria veche, numărată prima dată.*

---
## PRIMUL LUCRU DE ȘTIUT: **P0…P7 și planul E sunt închise; ce urmează se alege, nu se moștenește**

Etapele 1 și 2 ale campaniei sunt **neatinse**. Din 07.09 s-a lucrat la `PLAN_HARDENING.md` (P0…P7,
închis formal pe 14.09), iar din 14.09 la `PLAN_E1_E6.md` — cele șase etape derivate din auditul de
ansamblu, **închise pe 15.09**:

| pas | cifra care-l închide | commit |
|---|---|---|
| **E1** — ritmul se numără o singură dată | `RATE_LIMIT_IN_PROCES` 3 → **0** | `d76cf9d2` |
| **E6** — modelul de citire nu depinde de HTTP | `CORE_IMPORTA_MAIN` 2 → **0** | `6aa687fb` |
| **E3** — ce scrie, se probează *(lotul fiscal)* | subsetul declarațiilor 49 → **8**; rute care scriu fără probă: **88**, cu **43** mai puține | `c28000ec`, `32919d88` |
| **E4** — reparația se vede rulând | cele **4** `xfail(strict)` din registrul de datorii, scoase | `622dec8e` |
| **E2a** — universul se declară | `MODULE_CU_SQL_FARA_STRAT` 78 → **0** | `df361e9c` |
| **E2b** — valul care separă | `REPOSITORY care își deschid conexiunea` 32 → **0** | `1ca3b7ee` |
| **E5** — motoarele fiscale se pot citi | **nu e pas, e regula 9** din `PLAN_LUCRU.md` | `0976154e` |

**Ce NU s-a închis odată cu ele, și e scris ca datorie cu clichet, nu ca pas:** 88 de rute care scriu
fără probă în suită (din care **8** ating cifre de declarație și cer fixturi grele: stoc, extras
bancar, bon pozat, mijloc fix, rețetă, fișier de migrare) · **18** module cu amestec OBSERVAT, toate
ACTE, care au voie să-și dețină tranzacția · **8** citări `DUK regula` nerezolvate în `core/d402.py`
și `core/d301_operatiuni_api.py` · **logrotate** neinstalat (cere root) · `d301` rămâne singura
sărire din garda de limite, fiindcă cere o firmă NEplătitoare, iar fixtura e plătitoare.

*Vechiul tabel P0…P7 rămâne mai jos, fiindcă lanțul întreg e întrebat des.*

| pas | stare | ce a livrat, pe scurt |
|---|---|---|
| **P0** — feedback pe niveluri | **ÎNCHIS** (`8996f486`) | N1/N2/N3/N4 derivate din graful de import; N1 pe `control_fiscal_api` = **27 s** față de ~1.500 s poarta completă |
| **P1** — supervizor | **ÎNCHIS** (`ced26440`) | rezultat persistat, versionat; citire **p95 45 ms** pe 1000 de firme (era ~5 s) |
| **P2** — portofoliu / N+1 | **ÎNCHIS** (`f3567121`) | `control-fiscal` la 1000 de firme: **278.882 interogări · 70,8 s → 1 · 17 ms** |
| **P3** — rutele care cresc cu portofoliul | **ÎNCHIS** (`3cd7aebe`) | șase rute N-dependente eliminate în trei valuri; **toate cele 12 rute de portofoliu derivate din cod sunt acum 5q/3c constant de la N=5 la N=1000** |
| **P4** — proprietatea tranzacției | **ÎNCHIS** (`0742e177`) | inventar DERIVAT pe 510 puncte de intrare; 32 de căi peste prag, clasificate și **păzite**; 7 critice, fiecare cu injecție de defect; **6 reparații** (R179–R182); 8 efecte ireversibile judecate |
| **P5** — async / I/O blocant | **ÎNCHIS** (`f61df1b8`) | valurile 1, 1b și 3; `ACTION_REQUIRED` **19 → 0**, C1 pe cereri **0** |
| **P6** — stateless / scalare orizontală | **ÎNCHIS** `CLOSED_ACCEPTED` (`f260df2e`) | starea business în PostgreSQL · cele șapte cache-uri declarate · două procese reale în producție, four-way 2 din 2 |
| **P7** — stratul de aplicație | **ÎNCHIS** `CLOSED_ACCEPTED` (`f5e6cffc`) | diagnostic (`b67d2bfb`) · V3 (`364fbc63`) · V1 (`8d182afa`) · V2 (`cd5538ae`) · D2 (`e1cf6ee1`) · D4: cele 37 de module mixte · **valul use-case: cele 385 de corpuri de rută**. **Toate patru criteriile canonice satisfăcute**: `D1`=`D2`=`D4`=**0** și rutele care își dețin tranzacția **385 → 0** |

**P3, pe scurt** (detaliile în `RAPORT_P3_IMPLEMENTARE.md`): valul A a strâns două bucle
set-based (`1.004 q` → `5 q`; `2.005 q` → `5 q`); valul B a mutat patru rute de status pe modelul de
citire, fiindcă datele lor stau în schema fiecărei firme și n-aveau cum fi adunate cu un `GROUP BY`;
valul C a măturat toate rutele derivate din cod. **Un `UNION ALL` peste cele N scheme a fost refuzat
explicit**: ar fi dat panta 0 la litera criteriului, dar textul și planul SQL cresc cu N — criteriul
trecut fără ca problema să fie rezolvată.

**P4, pe scurt** (detaliile în `RAPORT_P4.md`): întrebarea „câte `commit()` sunt" (171 în
producție) nu se poate răspunde. Cea care se poate, și care a scos defectele, e **peste câte
tranzacții sunt împrăștiate scrierile unei operații**. Din 32 de căi peste prag, **7 sunt critice**;
șase aveau ce repara, iar **șase din șapte probe de injecție au fost roșii pe codul de dinainte**.

**Și o lecție despre propriul instrument, a patra oară în trei zile.** Prima formă a metricii de
efecte ireversibile raporta **ordinea CORECTĂ ca defect**: `gdpr_sterge.executa` comite întâi și
abia apoi șterge fișierele de pe disc — cu motivul scris lângă cod —, iar metrica mea era oarbă la
commitul explicit. *Când instrumentul acuză un cod care își explică singur ordinea, prima ipoteză e
că instrumentul n-a citit explicația.* Alte trei greșeli au ieșit la fel, măsurând: aliasurile de
import citite pe fișier în loc de domeniu de vizibilitate (**unsprezece** aliasuri sunt refolosite în
`main.py`, iar `_cc` înseamnă trei module diferite), bucla pierdută la trecerea printr-un apel, și
două bucle diferite împletite fiindcă n-aveau identitate.

**Și o lecție care nu e despre viteză.** Modelul de citire întorcea de la P2 o `prospetime.stare`
pe care **stratul de ecran o ignora** — deci o firmă necalculată încă arăta identic cu una măsurată
și găsită goală („fără parteneri încă"). Un necunoscut arătat ca un nu hotărât, pe șapte ecrane.
Corectat pe toate șapte, probat pe arborele de randare în chromium (`core/test_p3_val_b.py`, 48 de
probe). *Când adaugi un model de citire, întreabă imediat ce arată ecranul cât timp modelul e rece.*

**P7, pe scurt — și e cea mai mare schimbare de formă a codului din toată campania.** Stratul HTTP
nu mai conține SQL. **257 de instrucțiuni** au ieșit din corpul rutelor în două valuri: **107 citiri**
(V1) și **140 de scrieri + 10 instrucțiuni de control de tranzacție** (V2). Unde au ajuns: **15 module
de sub HTTP** — 14 `core/repo_*.py` plus `core/tranzactie.py`.

**Contractul lor, și e ce trebuie știut înainte de a scrie o rută nouă:**

- **fiecare funcție primește CURSORUL apelantului** (`def f(cur, …)`) — aceeași tranzacție, aceeași
  conexiune, același `search_path`, același `cursor_factory`;
- **niciun `get_conn`, niciun `commit`, niciun `rollback`, nicio `HTTPException`** sub stratul HTTP —
  cerut pe AST de `core/test_p7_v2_scrieri.py`, nu prin convenție;
- cele 15 module au, măsurat, **zero importuri** și exact patru nume de apel: `execute` (192),
  `fetchone` (92), `fetchall` (41), `join` (1). *Nicio rețea, niciun fișier, niciun `await` — de-asta
  contractul P5 nu s-a putut atinge nici din greșeală.*

**Proprietatea tranzacției NU s-a mutat.** Rutele orchestrează în continuare; `core/tranzactie.py` e
declarat USE_CASE dar își scrie în docstring că nu deține tranzacția — execută pe cursorul primit, la
același loc în șir. *Comanda V2 cerea și ca use-case-ul să dețină tranzacția, și ca proprietatea să
NU se schimbe; am ținut-o unde era și am scris alegerea — lecția 27.*

**Ce a rămas în `main.py`: 38 de instrucțiuni**, toate în helperi de modul, **niciuna în corpul unei
rute**. N-au fost niciodată în universul D1 (care e „corpul unei rute"), dar sunt motivul pentru care
`main.py` e în continuare `D4_STRAT_MIXT`.

**VALUL D2 — a doua verificare canonică închisă, și cea mai mică.** `core/efactura_send.py` era
declarat `FISCAL_ENGINE` și importa `db`: **8 instrucțiuni SQL**, **trei conexiuni** proprii,
singura încălcare `D2` din repo. Orchestrarea a trecut în `core/efactura_trimitere.py`
(`USE_CASE`, nou), SQL-ul în `core/repo_efactura.py` (7) și `core/repo_tenants.py` (1), iar
`principal_pentru_schema` în `core/spv_conector.py`. **Modulul a rămas `FISCAL_ENGINE`** —
reclasificarea ar fi dat `D2`=0 fără să atingă o linie de cod, iar o probă interzice acum exact
asta. **Proprietatea tranzacției n-a fost mutată**: `trimite` deschide tot trei `db.get_conn()`,
gardat pe AST. **Detectorul rămas fără instanță** și-a primit calibrarea *sintetică* — un univers
în care `main.py` e declarat motor fiscal —, plus cele patru forme de import și două negative.
*Un detector care raportează zero fiindcă s-a stricat arată identic cu unul care n-are ce găsi.*

**Și o probă pe care structura n-o putea da.** AST-ul, confruntarea SQL-ului și suita verde sunt
afirmații despre FORMA codului; niciuna nu vede o **eroare de apel** — `trimitere_vie(cur,
schema, factura_id, mediu)` cu ultimele două inversate trece tot și desface idempotența porții 3,
pe un upload care nu e idempotent. `core/test_efactura_trimitere.py` cheamă `trimite` cap-coadă
pe schemă efemeră, cu rețeaua pe mock: **8 probe**, 7 din cele 8 instrucțiuni mutate, RED-proof
cu trei mutații. *Un val care mută cod are nevoie de amândouă felurile de probă.*

**VALUL D4 — a treia verificare canonică închisă, și cea mai mare mutare de cod din campanie.**
Cele **37 de module mixte** purtau **215 instrucțiuni SQL**; toate au trecut în **37 de
`core/repo_*.py`**, fiecare funcție primind cursorul apelantului. Mutarea a fost făcută de
`scripts/p7_d4_separa.py` — **rest 0 din 215** —, iar dovada că s-a mutat și nu s-a rescris e
amprenta SQL a întregului cod de producție: **1050 distincte / 1307 total, identică înainte și
după**. Niciun `get_conn`, `commit` sau `rollback` n-a intrat în vreun depozit: contractul P4 e
gardat pe AST.

**ȘI DE CE P7 TOT NU E ÎNCHISĂ, deși contabilitatea arată 0 peste tot.** După D4:
`D1`=`D2`=`D4`=0 și `P7_ACTION_REQUIRED`=0. Citită singură, cifra spune că faza s-a terminat.
Măsurat: **385 din 421 de rute își deschid singure tranzacția**, doar 7 deleagă către un
`USE_CASE`, iar use-case-uri declarate sunt 4 — deci stratul pe care textul canonic îl definește
prin *«deține tranzacția (P4), orchestrează»* aproape că nu există. *Un `ACTION_REQUIRED=0` care
nu acoperă un criteriu canonic nu e o stare, e o lipsă de detector.* Golul e închis cu
`scripts/p7_criterii.py` + `core/test_p7_criterii.py`, care ține clichetul celor 385 și
**interzice planului să declare P7 închisă peste el**.

**Unde se citește adevărul, nu proza asta:** `core/straturi.py` (registrul de straturi, 167 de
declarații), `scripts/scan_p7_straturi.py` (detectoarele), `scripts/p7_clasificare.py`
(contabilitatea celor trei), `scripts/p7_criterii.py` (**toate** criteriile canonice).

**Tiparul comun al lui P1 și P2, și confirmat de P3:** ce era calculat în cerere se
persistă ca **model de citire** în `public`, invalidat de **triggere** pe tabelele-sursă, cu
prospețimea **derivată** din compararea a două versiuni — niciodată stocată. Interdicția, la
amândouă: *o valoare veche nu se arată ca fiind curentă; „în recalculare" declarat e acceptabil.*

### LANȚUL ÎNTREG, cu commitul de închidere al fiecărei etape

*Se scrie ca tabel fiindcă întrebarea „unde s-a oprit ce" a fost pusă de trei ori, iar răspunsul era
împrăștiat prin patru rapoarte.*

| etapă | închisă pe | ce a livrat |
|---|---|---|
| **P2** — portofoliu / N+1 | `f3567121` | `control-fiscal` la 1000 de firme: 278.882 interogări · 70,8 s → 1 · 17 ms |
| **P2, redeschis** — modelul își cunoaște dependențele | `224cfc40` | 27 de surse **măsurate** (erau 8 scrise din memorie), triggere pe toate, epocă temporală, `DEPENDENTE_P2.md` generat și păzit |
| **P2, remedierea auditului** | `b393b19c` | fail-closed la pornire · blocaj de sesiune pe aceeași conexiune · ramuri acoperite deliberat · artefactele produse DUPĂ ultimul patch |
| **hardening post-P2** | `6b59c19f` | ordinea taskurilor de fundal · `SAVEPOINT` per tenant la migrare · verificare periodică de drift · backlog observabil (`p2_worker_*`) · monotonie impusă prin trigger |
| **P3, diagnostic** | `7d921282` | 12 rute care cresc cu N, 6 cu N+1; pante măsurate, nu medii; cauze demonstrate; **nicio implementare** |
| **P3, implementare** | `3cd7aebe` | valul A (`e7ce0c2e`) · valul B (`0f0a135a`) · valul C + concurență (`3cd7aebe`) |

**Toate închise.** Ce rămâne deschis e la „restanțe", mai jos: **R177** (clasa, nu instanța) și
**R178** (capacitatea pool-ului, neblocantă).

---
## DOUĂ LUCRURI DE MEDIU care nu se văd din cod

1. **Repo-ul e PUBLIC pe GitHub** — `CostinHat/iconta-nou-review`. `origin` e cel **privat**
   (`CostinHat/iconta-v2`). **Din 08.09, `post-commit` împinge AUTOMAT pe amândouă** (pasul 1b),
   contract identic: fast-forward, niciodată `--force`, sentinelă la eșec, nu blochează publicarea
   locală. `public` **nu** intră în four-way, deliberat.
   **REGULA DE RAPORT, născută dintr-o divergență reală (R176):** „publicat" înseamnă **amândouă**
   remote-urile — sau se spune explicit care a rămas în urmă și de ce. *Patru commituri au stat în
   urmă pe public fiindcă rapoartele mele spuneau „publicat" fără să zică pe care.*
2. **Contul de asistent e ACTIV** (`asistent@prisma-cont.test`), cu `poate_pregati`/`poate_valida`.
   Consecință: `patru_ochi_posibil` e **true** în cabinetul 1968 — mecanismul rămâne **neactivat**,
   deci comportamentul nu se schimbă, dar afirmația din `TRASEE.md` că „nu se poate exercita un
   traseu care cere doi oameni" **nu mai e adevărată**.

---
## AL TREILEA LUCRU: **LUCRĂTORUL modelului de citire, și de ce e o lecție, nu un detaliu**

`*/5 * * * * python3 -m core.firma_rezumat` — recalculează firmele invalidate. **A fost adăugat abia
la sfârșit, pregătind predarea asta**, și lipsa lui e cea mai instructivă greșeală a zilei:

P2 mutase calculul din cerere în recalculare și **măsurase corect câștigul** — dar **nimic nu chema
recalcularea**. Modelul era populat fiindcă îl rulasem eu de mână în timpul măsurătorilor. La prima
factură editată, firma trecea pe `invalidat` și **rămânea așa la nesfârșit**: ecranul Control fiscal
ar fi arătat gri, permanent, pentru orice firmă atinsă.

*Criteriul de acceptare al lui P2 — interogări și latență — era îndeplinit, și totuși ce livrasem nu
funcționa.* **Un criteriu de acceptare măsoară ce ai cerut, nu ce ai livrat.**

Probat cap-coadă înainte de predare, pe o editare reală: `curent` → editare → `invalidat` → lucrător
→ `curent`. Pragul lui e în `cron.RITMURI` (1 h), deci lipsa bătăii lui se vede la deadman.

---
## AL DOILEA: CIFRELE DESPRE DATE SUNT INTEROGATE, NU SCRISE

Blocul următor e **generat** din bază de `scripts/scan_predare_cifre.py`, iar
`core/test_predare_cifre.py` îl compară cu interogarea **de la rulare**, caracter cu caracter. Dacă
nu se potrivesc, **poarta cade**. Nu se editează cu mâna.

**De ce există:** pe 28.08 am scris aici *„0 din 18 firme au `nume_anaf`"*. Real: **1 din 18**. Cifra
fusese **deja invalidată o dată**, iar corectura era în tabelul „cifre invalidate" **din aceeași
predare**. *O regulă scrisă nu ține fără control mecanic.*

**DESPRE CE BAZĂ VORBEȘTE BLOCUL — s-a schimbat sub mecanism, și nimic n-a spus-o.**
Garda compară blocul cu interogarea **din mediul în care rulează poarta**. Din R68 (11.09) poarta
rulează în `iconta_test`, deci blocul descrie **restaurarea de test**, nu producția. Măsurat pe
12.09: `iconta_test` are **20** de firme, `iconta_v2` are **49**. Mecanismul e intact — cifrele tot
nu pot îmbătrâni —, dar **subiectul lor s-a mutat în tăcere**, iar cine le citește ca stare a
producției greșește. *Aceeași clasă cu brațul four-way care întreba baza de test: izolarea și
măsurarea producției trag în direcții opuse, iar unde se întâlnesc trebuie spus care e care.*

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
| **48** | contorul `tenant_schema_seq` |
| **48** | maximul istoric de nume de schemă |

**Clasificatorul de alerte**

| cifra | ce e |
|---|---|
| **2** | predicții de alertă confruntate cu faptul |
| **2** | din care greșite |

**Referințe moarte**

| cifra | ce e |
|---|---|
| **69** | rânduri care trimit la o firmă inexistentă |
| **20** | tabele din `public` cu `tenant_id`, numărate |

<!-- CIFRE-DATE:STOP -->

## AL TREILEA: SUPERVIZORUL. **A fost apăsat de un om, prin ecran.**

### S-A TRECUT CAP-COADĂ *(03.09.2026, 07:43)*

Costin a trecut poarta confirmării **prin interfață**, pe elementul `8052` (`tenant_005`, D300 trim
3/2026): pasul s-a deschis cu constatarea și temeiul, **motivul gol a fost refuzat**, iar cu motiv
scris depunerea a trecut. **Verificat în date, nu luat pe cuvânt:**

```
declaratii_coada 8052   -> stare 'depusa', depus_de_id 1968, depus_la 07:43:27
supervizor_confirmari   -> 1 rând: tenant 4840 · 09/2026 · D101_VS_D100_PLATI_ANTICIPATE
                           amprenta 09441a61b26c5ce555929ad4a890518f · de 1968
                           motiv: „probă supervizor — se corectează prin rectificativă"
declaratii_depuse       -> d300 2026/9, cu `randuri` NENUL
```

**`depus_la` și `confirmat_la` sunt aceeași secundă** — confirmarea și depunerea sunt un singur act,
nu două care se pot despărți.

### Cele cinci comparații orizontale, pe portofoliul viu — **remăsurat acum**

```
CONSTATARI 16 · FARA_SUBIECT 0 · NEVERIFICAT 3   (suma = 19 = domeniul)
constatari_total 92 · de_confirmat 3

D101_VS_D100_PLATI_ANTICIPATE   gri 17 · ROSU 2      <- CERTE, cer confirmare
D101_VS_CONT_691                gri 17 · ROSU 1 · VERDE 1
D390_VS_D300_IC                 gri 13 · VERDE 3
D300_VS_D394_TAXARE_INVERSA     gri 18 · VERDE 1
EFACTURA_VS_D394                gri 18 · VERDE 1
```

Pe **cinci** firme, nu pe trei: `tenant_004` (trei verzi) · `tenant_005` (un roșu + un verde) ·
`tenant_013` și `tenant_017` (câte un verde) · `tenant_014` (două roșii).

**`de_confirmat = 3`, și cele trei nu sunt la fel:**
- **una** e scenariul declarat de pe `tenant_005`, pe care Costin a hotărât să-l lase (*„un portofoliu
  în care nimic nu e vreodată roșu e starea din care tocmai am ieșit"*). Confirmarea lui e scrisă, dar
  **amprenta e pe perioada depunerii** (09/2026); constatarea rămâne roșie pentru orice altă perioadă.
- **două** sunt **subiectul probei de ecran** de pe `tenant_014` (cabinetul de test 4163).
  `frontend_test/proba_r126_confirmare.py` **își șterge propriile confirmări la fiecare rulare**, ca
  să fie repetabilă — deci le lasă în urmă, deliberat. *Nu sunt un scenariu al portofoliului; sunt o
  fixtură care trăiește între rulări.*

**Fiecare din cele cinci comparații a dat ROȘU cel puțin o dată**, pe date construite prin lanțul
aplicației, invalide întâi și valide după — regula 3. Tabelul cu firma, perioada și cifrele fiecărui
roșu e în `CONFORMITATE.md`, la R123/R125.

### Ce a schimbat ordinea, reparat apăsând (R128)

Poarta cade **ÎNAINTE** de aprobare. Înlănțuirea „aprobă + depune" trăia în client, deci un refuz
lăsa elementul `aprobata` — stare din care nu se mai poate **respinge**. Acum se trimite **un act**,
iar serverul aprobă după poartă.

---
## AL PATRULEA: BUCLA DE LUCRU — citește înainte de prima probă

### R118 — ce se servește NU e ce e în lucru

`/static` se montează din **`../iconta_publicat/static`**, scris de `scripts/publica_static.py` din
**HEAD**, în `post-commit`, **înainte** de restart. Publicarea are poarta ei: **`node --check` pe
fiecare `.js`**, și **refuză** dacă vreunul nu se parsează.

> **CONSECINȚA, pe care o plătești la fiecare tură:** o editare de JS **NU e live**. Înainte de orice
> probă pe ecran: `./venv/bin/python scripts/publica_static.py --din-arbore`.
> Amprenta a ce se servește: `curl -s https://iconta.eu/static/.publicat.json`.

### R129 — o filă deschisă de mult AFLĂ că s-a publicat

`static/js/versiune.js` compară amprenta la 5 minute și la revenirea în filă; la diferență **anunță**
— o pastilă în bara de stare. **Nu reîncarcă singură.** Limita: la rolul `client` bara de stare nu
există, deci anunțul nu se vede acolo.

### Regula 5 — ce rulează o tură

O tură care **nu atinge niciun `.py`/`.js`** rulează doar **gărzile de registru**: `perimetru.py` le
derivă — **25 de fișiere / 253 de teste / 396–575 s** (două cronometrări; mașina e partajată), față
de ~22 de minute ale porții complete. Se stabilește din `git diff`, pe extensie, **nu prin judecată**. Dacă s-a atins măcar un
executabil, poarta rămâne cea completă. **Înainte de publicare și înainte de `/clear`: poarta
completă, fără excepție.**

```
./venv/bin/python scripts/perimetru.py            # ce s-a atins si ce perimetru iese
./venv/bin/python scripts/perimetru.py --pytest   # doar argumentele, pentru pytest
```

---
## AL CINCILEA: CE E ADEVĂRAT DESPRE STAREA CODULUI

*Toate cifrele de mai jos sunt DERIVATE (`scripts/raport_b.py`, `scripts/scan_ramas.py`) și
remăsurate pe `6d73eec1`. **Nu se scriu de mână** — de trei ori s-a dovedit că o cifră copiată dintr-o
predare în alta e greșită exact acolo unde pare cea mai sigură.*

- **restanțe deschise: 54** (din care ale etapei E1: **25**) — SURSĂ 7 · VERIFICARE 31 · ARTEFACT 9 ·
  ORDINE 7. *P7 n-a deschis niciuna și n-a închis niciuna: e o mutare de cod, nu o reparație de
  produs.*
- **interdicții, din 78**: MĂSURATE **24** · PARȚIAL **16** · NEMĂSURABILE **5** · NEÎNCEPUTE **33**.
- **locuri de verificare**: **221 scrise / 0 goale din 221 (100%)**.
- **gărzi și instrumente**: **574** (547 în `core/`), din **520** fișiere de test.
- **decizii care blochează: niciuna.**

---
## STAREA LA PREDARE

**6172 teste trec** *(ieșirea porții de la `1ca3b7ee`, E2b)* · 7 skip · 11 xfail · ruff OK ·
verificator **TOTAL 0** · four-way se închide la `post-commit`, care publică pe `origin/main`,
**pe `public/main`**, pe `backup/lant-<zi>`, publică statica din HEAD, restartează necondiționat, și
**verifică singur cele patru brațe** la capăt (pasul 4, P0).

**Brațul four-way cere acum și CARDINALITATEA** (din 12.09): numărul așteptat de procese se citește
din `Environment=` al unității systemd, iar „2 din 2" e o afirmație despre TOATE, nu despre cele
găsite. *Un rând rămas de la un proces mort face brațul `PREA_MULTE`, deci „instanțe stătute = 0" nu
e o vorbă, e o consecință.*

**Cifrele de aici se copiază din IEȘIREA PORȚII, nu din predarea de dinainte.**

**CLICHETELE VII — blocul de mai jos e GENERAT.**

<!-- CLICHETE-VII:START (generat de scripts/scan_ramas.py --clichete-md) -->

*Generat din COD. **Nu se scrie cu mâna** — `core/test_clichete_generate.py` recalculează și compară caracter cu caracter. Regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.*

| cod | acum | ce se numără | instrument |
|---|---|---|---|
| **77** | **62** | refuzuri fără temei în module care citează legea | `scripts/scan_refuzuri.datorie()` |
| **77u** | **866** | UMBRA: refuzuri în module care nu citează legea (nedeplafonat) | `scripts/scan_refuzuri.umbra()` |
| **50** | **1222** | aserțiuni ancorate pe text, nu pe structură | `core/scan_garzi_pe_text.pe_fel()` |
| **R80** | **7** | rute despre care detectorul de apelanți nu poate afirma nimic | `scripts/scan_ancore_rute.verdicte()` |

<!-- CLICHETE-VII:STOP -->

**POARTA DUREAZĂ ~33 DE MINUTE** — măsurat pe 14–15.09: **1.898–1.991 s**, pe nouă rulări.
*Cifra veche (~26 de minute, 1.474–1.595 s pe 14 rulări, 06–08.09) se păstrează alături: suita a
crescut cu ~430 de probe între timp, deci diferența e conținut, nu încetinire.* **Consecința
practică, de planificat:** o tură cu trei respingeri la poartă costă aproape două ore numai în
porți — de-aia regulile 6–8 (fără rulare preventivă) contează mai mult acum decât când au fost
scrise.

**POARTA SCURTĂ EXISTĂ, și are patru trepte** (`scripts/poarta_scurta.py --nivel=`). Măsurat: N1 pe
`control_fiscal_api` = **27 s**; N2 pe `d112` = 338 s; N3 = 349 s. **Refuză** — corect — când se
atinge un `.md`, un `.js` sau `main.py` **alături de cod**; când se ating **numai** registre,
închide perimetrul (28 de fișiere).

---
## CE E ADEVĂRAT ACUM DESPRE RESTANȚE

| | |
|---|---|
| **prag 1** | **niciuna deschisă** |
| **decizii** | **niciuna deschisă** |
| **rute fără probă** | *(15.09)* **88** de rute care SCRIU n-au nicio probă în suită; dintre ele **8** ating tabele din care se ridică declarații și cer fiecare o lume pregătită (articol de stoc ×3, linie de extras bancar, bon pozat, mijloc fix, rețetă, fișier de migrare). Clichet dublu în `core/test_rute_probate.py` + `PLAFON_SUBSET_FISCAL` — scad **numai** cu probe scrise, niciodată prin lărgirea definiției lui „numită" |
| **D4b = 18** | *(15.09)* module cu SQL care își deschid singure conexiunea sau comit. **Toate sunt ACTE** (cron-uri, lucrători, sonde, conectori), iar un act are voie — `PLAN_HARDENING.md:840`. Cifra e clichetată ca să nu crească pe tăcute, nu fiindcă ar fi o datorie |
| **8 citări DUK** | *(15.09)* `R14/R34/R39/R43/R50` în `core/d402.py` și `R24.1` în `core/d301_operatiuni_api.py` nu se regăsesc în validatoarele lor. Jarul D402 instalat are în tot cuprinsul lui patru coduri — niciunul dintre cele citate. **Se lămurește prin RULARE** (XML mutat deliberat), nu prin citirea constantelor: la D100, adiacența din bytecode m-a mințit, iar validatorul m-a corectat |
| **d301, sărit** | *(15.09)* garda de limite per-câmp exercită opt declarații pe date semănate, dar `d301` rămâne sărit: decontul special e doar pentru NEplătitori, iar fixtura e plătitoare fiindcă așa cer D300/D394. **O firmă nu poate fi și una și alta** — cere a doua fixtură |
| **R183** | *(nou, 09.09, P4)* `spv_conector.apel_anaf` ține o conexiune din pool și tranzacția ei **deschise** peste apelul către ANAF (timeout până la 60 s la upload), peste retry-ul de `401` și peste backoff-ul de `429`. **Proprietatea e reparată** (R180: scrierea de token nu mai depinde de tranzacția aia); ce rămâne e **durata**, aceeași clasă ca R178, și se închide împreună cu ea. *Nu e o cifră, e o formă a codului — cifra ar cere trafic real* |
| **R178** | *(nou, 09.09, măsurat nu presupus)* la **10 cereri de portofoliu simultane**, conexiunile simultane ating exact `ICONTA_POOL_MAX = 10` — rezervă zero —, iar latența crește ~liniar cu concurența (p50 56 → 755 ms), deci debitul e practic plat. **Nu e o regresie P3** (înainte o singură cerere lua 1.003–2.003 conexiuni pe rând); e o proprietate a configurației, măsurată acum fiindcă înainte n-a fost. Mărirea pool-ului ar ascunde-o, nu ar rezolva-o |
| **R177** | clasa „model de citire cu dependențe scrise din memorie". **Instanța e reparată** (`224cfc40`); ce rămâne deschis e că **nimic nu spune câți alți purtători ai clasei are aplicația**. P3 a mai găsit unul, fără să-l caute — v. mai jos |
| **R176** | *(nou, 08.09)* divergența `public` ↔ `origin`. Push-ul automat e **făcut**; ce rămâne deschis e că **nicio gardă nu prinde divergența** — azi a prins-o un om uitându-se pe GitHub |
| **R174** | o factură încasată prin BANCĂ nu se marchează încasată nicăieri |
| **R175** | desktopul asistentului e acoperit de o probă proprie, nu de uneltele de listă |
| **R69** | declarațiile deja depuse să apară **contrazise** când se schimbă vectorul — **rămâne netratată**, amânată de trei ori de comenzi noi |
| **R121** | P300 / RO e-TVA n-are acces programatic. **EXTERNĂ** |
| **restul** | `CONFORMITATE.md`, sau `scripts/scan_ramas.py`. Numărul e derivat, nu scris |

---
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

*Cel mai ieftin drum: rulează gărzile de registru **înainte** de commit (`perimetru.py`), nu după —
o respingere costă 22 de minute, perimetrul de registru costă 7–10.*

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

---
## DACĂ CONTINUI DE AICI

0Z. **[15.09.2026] PLANUL E E ÎNCHIS. Următoarea temă e ALEASĂ de Costin, nu moștenită.**

   Nu există pas următor „la rând". `PLAN_E1_E6.md` are tabelul de închidere în cap; `PLAN_LUCRU.md`
   are acum **regula 9** (motorul fiscal deschis pentru altceva se lasă citibil) — o regulă, nu o
   etapă, deci nu se „pornește".

   **Tema care ASTEAPTĂ COMANDĂ, cu cifrele ei din tabel** (`LISTA_FUNCTIONALITATI.md`,
   `VERIFICARE_FUNCTIONALITATI.md`): *probarea suprafeței de introducere a datelor*. Etapa 1 (date
   invalide) e terminată — **333** de unități probate din cele **364** ale perimetrului, **133** cu
   defect găsit și reparat. Etapa 2 (date valide, până în rândul declarației) s-a oprit pe
   **05.09.2026, lotul E**, cu **27** de unități atinse și toate cele nouă declarații acoperite ca
   generare. Ce a cerut Costin și n-a început: **cele 45 de unități-nucleu neprobate individual**, în
   ordinea d300 → d394 → d112 → d406 → restul, fiecare cu lanțul complet — *valoarea intră, se
   înregistrează, ajunge în rândul corect cu suma corectă, declarația se generează și validează* —,
   iar „suprapunere" **nu** contează ca probă.

   **[15.09.2026] Pasul de verificare S-A FĂCUT, iar cifrele de mai sus sunt INVALIDATE.** Starea
   e confirmată: **zero defecte deschise**, **zero în `xfail`** din temă — detectorul care caută un
   defect fără cuvântul „reparat" în aceeași propoziție dă **0** pe tot registrul, iar din cele 54 de
   restanțe DESCHISE (`scripts/raport_b.py`) **niciuna** nu e din intervalul temei; toate codurile ei
   apar la *restanțe REZOLVATE*. Cele 12 `xfail(strict=True)` din suită sunt toate din afara temei.

   **Dar cifrele „133" și „15" nu se pot reconstitui, deci se INVALIDEAZĂ** — aceeași regulă ca la
   cifra 131 (`core/test_predare_proaspata.py`): *o cifră ai cărei termeni nu se mai pot reconstitui
   se invalidează, nu se corectează.* Recalculat din `LISTA_FUNCTIONALITATI.md`: etapa 1 are **145**
   de rânduri cu defect reparat (122 cu fraza canonică `**defect găsit și reparat**` + 23 cu alte
   formulări), iar etapa 2 numea **12** coduri R înainte de 15.09 (R161–R170 + R165c, R166b). Singura
   cifră care se reproduce exact e **27** — unitățile atinse de etapa 2 până atunci.

   **Și „cele 45" sunt INVALIDATE.** Perimetrul se re-derivă, nu se citează: `scan_lanturi_declaratie`
   dă **44** de unități-nucleu, din care 15 erau deja atinse — deci **29** rămase, nu 45. Cifra veche
   (72 − 27) era corectă pe `c125e0ed` și se poate reproduce acolo; s-a schimbat fiindcă valul
   use-case al lui P7 a mutat codul sub instrument, iar instrumentul a fost reancorat pe 15.09
   (`357a4d8a`). Din cele 29, **20 sunt probate** în loturile F (D300, 10), G (D394, 3) și H (D112, 7);
   rămân **9**: D406 (8) și D205 (1).

0Y. **[15.09.2026] CE E DE ȘTIUT DESPRE CELE DOUĂ REPARAȚII FISCALE, dacă apare o mirare.**

   `nomenclator_status_factura.clauza_tip_document()` e acum **singurul loc** unde scrie că un
   document fiscal e `tip = 'factura'`; D300 o cere pe toate cele patru drumuri ale lui prin
   `facturi`, iar D394 și-a înlocuit cei trei literali cu ea. Dacă mâine o proformă „dispare" dintr-un
   raport, ăsta e motivul, și e deliberat.

   `core/d394.py` citește partenerul de pe **factură** (`tert_cui`/`tert_nume`), cu fișa clientului ca
   **rezervă** — nu invers, ca până acum. Motivarea lui Costin, scrisă în DECIZII 47: *factura e
   autoritatea; istoria se corectează prin storno și reemitere, nu prin editarea fișei.*


0. **P6 E ÎNCHIS (12.09.2026). Producția servește din DOUĂ procese.**

   Unitatea poartă `Environment=WEB_CONCURRENCY=2` (editată de Costin — pasul cere root; `sudo -n -l`
   dă doar `systemctl restart|status` și `journalctl`). Criteriile canonice au fost exercitate pe
   procese REALE, nu pe copii de test: login blocat pe un worker și văzut de celălalt · cooldown cu
   un singur câștigător · sesiune acceptată de amândoi · `SIGKILL` în timpul unei cereri, fără stare
   parțială · four-way 2 din 2.

   **BASCULAREA A SCOS UN DEFECT PE CARE SUITA VERDE NU-L PUTEA VEDEA**, și merită citit înainte de
   orice: blocajul de pornire se lua, dar `migrare_api.asigura_tabel` comitea o linie mai jos și îl
   elibera. Instalarea P2 rula neserializată, iar un worker murea la **fiecare** repornire (4 din 4).
   Reparat în aceeași zi: blocajul se ia primul · `asigura_tabel(comite=False)` pe calea de pornire ·
   iar la CAPĂTUL secțiunii `instante.confirma_blocaj` cere dovada că blocajul mai e ținut — ca un
   viitor apel care comite să nu mai poată desface serializarea în tăcere.

   **Ce se verifică la orice repornire de acum înainte:** `pgrep -f multiprocessing-fork` dă DOUĂ
   PID-uri *(atenție: `pgrep -f "uvicorn main:app"` dă doar supervizorul — cu `--workers`, workerii
   poartă linia de comandă a lui `multiprocessing.spawn`)* · registrul `instante` are două rânduri cu
   același commit · `scripts/toate_poarta_head.py` închide brațul · zero `ERROR` în `uvicorn.log` la
   pornire · `iconta.eu` 200.

   **De întors, dacă apare un incident:** se scoate linia `Environment=WEB_CONCURRENCY=2` din
   `/etc/systemd/system/iconta-nou.service` (cere root), `daemon-reload`, `restart`. La un singur
   worker totul se comportă ca înainte — pragul de conexiuni dă tot 20, blocajul e necontestat,
   liderul e singurul candidat.

0b. **P7 E ÎNCHIS (13.09.2026), și cu el TOT PLANUL DE ÎNTĂRIRE. `main.py` nu mai conține nici SQL,
   nici logică de aplicație.**

   **Ce se schimbă pentru cine scrie cod de acum:** o rută nouă care atinge baza **nu scrie SQL**.
   Scrie o funcție într-un `core/repo_*.py`, care primește `cur` și nu comite nimic. Dacă ai nevoie
   de `SAVEPOINT` sau de `SET LOCAL search_path`, sunt în `core/tranzactie.py` — o funcție per
   instrucțiune, cu SQL-ul literal, dinadins (un nume de savepoint interpolat ar fi o suprafață de
   injecție care azi nu există). **Garda cade dacă pui `.execute` într-o rută**, pe oricare din cele
   patru clase: `core/test_p7_v2_scrieri.py`, cu cei zece mutanți.

   **`D4` E ÎNCHIS (13.09.2026), și cu el TOATE cele trei detectoare.** Cele 37 de module mixte
   și-au dat cele 215 instrucțiuni la 37 de `core/repo_*.py`. `D1`=`D2`=`D4`=0,
   `P7_ACTION_REQUIRED`=0.

   **VALUL USE-CASE A ÎNCHIS CRITERIUL CARE ȚINEA FAZA DESCHISĂ.** Cele **385 de corpuri de rută**
   au plecat în **27 de module `core/uc_*.py`**, cu **58 de helperi** și **12 nume de modul** după
   ele; `main.py` a scăzut de la **11714** la **6546** de linii. Clichetul celor 385 a coborât la
   **0** și s-a rescris în **gardă de zero** — un clichet la zero n-ar mai păzi nimic, fiindcă orice
   rută nouă care își deschide singură tranzacția ar încăpea sub el.

   **CE TREBUIE ȘTIUT ÎNAINTE DE A SCRIE O RUTĂ NOUĂ, și e scurt:**

   - ruta ține **decoratorul, semnătura și docstringul**; corpul stă în `core/uc_<segment>.py`, unde
     `<segment>` e primul segment al căii. FastAPI validează pe semnătură, deci contractul de intrare
     e al rutei, nu al use-case-ului;
   - use-case-ul **nu construiește `HTTPException`**. Refuzurile se spun în vocabularul din
     `core/erori.py` — clase care numesc CONDIȚIA —, iar traducerea în cod HTTP e **o singură hartă**,
     `main._COD_EROARE`. Învelișul o aplică: `except _erori.EroareDeDomeniu as e: raise _http_din(e)`;
   - **obiectele de protocol nu trec granița.** `Response`/`FileResponse` se construiesc în înveliș,
     din valorile întoarse; `UploadFile` se citește în înveliș (`_octetii`) și se pasează ca `bytes` +
     nume; gărzile de ritm care se uită la IP rămân pe primul rând, deasupra lui `try`;
   - ce se află **la pornire** (`_TENANT_TEMPLATE`, `_STATIC_DIR`) stă în `core/uc_comun.py`, iar
     stratul HTTP îl **pune** acolo când îl află. *HTTP-ul configurează, use-case-ul consumă.*

   **Contractul HTTP e PĂZIT, nu promis:** `core/test_p7_uc.py` confruntă, funcție cu funcție,
   perechile `(cod, mesaj)` cu `main.py` de la commitul dinainte de val. O singură abatere e
   acceptată, cu numele și motivul ei în fișier.

   **`D2` E ÎNCHIS (13.09.2026).** Motorul fiscal `core/efactura_send.py` nu mai importă `db` și
   n-are nicio instrucțiune SQL; orchestrarea trăiește în `core/efactura_trimitere.py` (`USE_CASE`),
   SQL-ul în `repo_efactura` / `repo_tenants`, principalul la `spv_conector`. **Ce trebuie știut
   înainte de a-l atinge:** modulul a rămas declarat `FISCAL_ENGINE` **dinadins**, iar o probă cere
   asta explicit — dacă un val viitor îl reclasifică, `D2` ar cădea la zero pentru motivul greșit.

   **CE A RĂMAS DESCHIS DUPĂ ÎNCHIDERE, și se scrie ca să nu treacă drept curat:**
   `core/uc_comun._raspuns` construiește un `JSONResponse` — e serializarea mutată de pe bucla de
   evenimente la P5, ajunsă aici fiindcă o cereau corpurile a șapte rute. E **singurul** loc din
   stratul use-case care mai atinge un obiect de protocol, nu e cerut de niciun criteriu canonic, și
   nu s-a atins în valul ăsta fiindcă mutarea lui ar redeschide o măsurătoare de la P5.

   **Lecția valului, pentru orice mutare viitoare de cod:** *când muți codul, instrumentele care îl
   citeau se mută și ele, sau raportează despre o lume de dinainte.* ~40 de gărzi au trebuit
   re-ancorate, iar două scanere și-au pierdut un punct orb pe care și-l declaraseră singure.

1. **RESTUL: NU DESCHIDE NIMIC.** Comanda de capăt de etapă, verbatim (06.09.2026): *„Etapa 2 e
   închisă. Nu deschide nimic altceva — nici restanțele, nici backlogul A3, nici cele opt căi
   rămase din clasa R164."* Cele **54** de restanțe deschise **nu sunt o coadă de sarcini**;
   `PLAN_LUCRU.md` → „⬛ STAREA, DUPĂ R118". *Rămâne în vigoare: din 07.09 se lucrează la
   `PLAN_HARDENING.md`, iar temele vin de la Costin, una câte una.*

   **CE E ÎNCHIS, ca să nu se redeschidă din reflex:**

   | | |
   |---|---|
   | **etapa 1** — date invalide | 364/364, închisă 05.09.2026 |
   | **etapa 2** — date valide, până în declarație | **toate cele nouă**, închisă 06.09.2026, 0 nepotriviri pe cele cinci loturi |
   | **R151** — ultima restanță deblocată de decizie | răspuns primit 05.09, construită 06.09 |
   | **restanțe deschise** | **54** *(se derivă cu `scripts/raport_b.py`, nu se crede din proza asta — iar „50" a stat aici o săptămână, contrazicând „54" din altă secțiune a aceluiași document)* |

   **CE A RĂMAS EXPRES NEATINS, și de cine s-a decis:**
   - **backlogul A3** (Playwright/infra: reconciliator #5, matrice de stări #4, baseline determinist
     #8, keyboard-only #9, linter de consistență #10, global-first CSS, model-audit F2/F7) —
     `INSTRUMENTE_ROADMAP.md`. §5-calculat le raportează **computat** cât rămân neacoperite.
   - **cele opt căi rămase din clasa R164** — schema unui tenant are 12 constrângeri UNIQUE, trei nu
     pot ajunge la `500` (și se spune de ce), una e reparată. Restul de opt **n-au fost probate**, și
     asta e scris în `CONFORMITATE.md` la R164, nu ascuns.
   - *(închis 06.09.2026)* Principiul deciziei 72 **e acum în `PLAN_ARHITECTURA.md`**, la
     Verificarea 5, cerut de Costin în aceeași tură: *o alegere fiscală care nu se poate deriva
     mecanic din datele existente se cere de la om, la operațiune — niciodată preselectată,
     niciodată dedusă pe ghicite; și nu se cere ce aplicația poate stabili singură.* Golul pe care
     îl numea R151 — planul spunea *că* alegerea se cere, nu *de la cine* — e închis. **Nu mai e o
     cerință pentru tura următoare.**

   **CE SE ȘTIE ACUM ȘI NU SE ȘTIA LA ÎNCEPUTUL CAMPANIEI** — trei lucruri, fiecare cu instanța:
   1. *Datele plauzibile ating defecte pe care santinela nu le atinge.* `«»@#$%` cade la prima
      validare de formă; `7015` în loc de `701`, sau un CNP valid deja folosit, ajung la stratul
      care crapă (R163, R164 — în aceeași zi).
   2. *Confruntarea între generatoare găsește ce nicio probă pe un singur generator nu poate.* R165 a
      ieșit comparând aceeași perioadă între D300, D394 și D406.
   3. *Un arbitru la care nu ajungi nu te judecă.* Validarea D406 ieșea `gri` cu validatorul
      instalat, fiindcă niciun corp de cerere nu trecea și generarea, și validarea. Reparând drumul,
      arbitrul a numit din primul apel un defect vechi de când există generatorul (R166b).

   **ȘI TREI DESPRE PROPRIILE MELE INSTRUMENTE**, fiindcă toate trei s-au întâmplat în ultimele două
   ture și niciuna n-a fost prinsă de mine:
   4. *O aserțiune păzită de `if <s-a găsit>:` nu e o aserțiune, e o observație.* Proba lotului E
      căuta `<SelectionStartDate>` — ramura pe care fișierul n-o emite — și, negăsind-o, sărea
      verificarea și tipărea `null`. A ascuns R165c o rulare întreagă.
   5. *Un test care acceptă orice refuz nu apără motivul refuzului.* Mutația mea a scos verificarea
      ramurii la R151 și garda a rămas **verde**: refuzul venea oricum, din alt motiv. De-aia
      refuzurile poartă acum `cod`.
   6. *„La sursă" înseamnă la linia care produce valoarea, nu la textul care o rezumă.* Două
      așteptări greșite în același lot, din docstringuri corecte ca descriere a normei și greșite ca
      descriere a codului (`divid_D1` vs `divid_D`; `SelectionStartDate` vs tuplul `Period*`).

   **ULTIMUL LUCRU, și e o regulă de conduită, nu o observație:** în ultimele două ture **poarta a
   condus designul de patru ori**, și de fiecare dată a avut dreptate — a respins împrumutul
   ferestrei din generator (`test_non_tautologie`), a refuzat să emită un SAF-T contradictoriu, m-a
   prins asertând pe text în chiar gardul cu docstring despre §23, și a arătat `main.py 0 → 389`
   când am pus o constantă unde nu-i era locul. **Când poarta respinge, prima ipoteză e că are
   dreptate.**
   **ETAPA 2 E COMPLETĂ PE TOATE CELE NOUĂ** (05.09.2026, lotul E a închis-o): probarea cu date **VALIDE**, pe lanțul până în
   declarație. Perimetrul, tăiat de el de două ori în aceeași zi: numai unitățile care
   alimentează **cele nouă declarații pe care aplicația le GENEREAZĂ** — D100, D101, D112,
   D205, D300, D301, D390, D394, D406/SAF-T. Derivat mecanic cu
   `scripts/scan_lanturi_declaratie.py`: **197** de unități ating o declarație, **162** intră în
   cele nouă, **72** sunt NUCLEU pentru cel puțin una. Nucleul pe declarație: d406 **34** ·
   d300 **33** · d112 **24** · d394 **23** · d390 **13** · d205 **3** · d301 **3** · d100 **0** ·
   d101 **0**. *(Cifrele poartă corectura din `DECIZII.md` 68 — un comparator de declarații nu e
   un hrănitor. Se derivă din instrument, nu se cred din predare.)*
   **Trecute: lotul A** (D300 + D394) — 16 rânduri confruntate, toate potrivite; TVA colectată
   D394 = `R17_2` din D300 — **și lotul B** (D390 + D301) — reclasificarea mișcă numai tipul,
   linia manuală ajunge cu suma ei, iar desfacerea readuce declarația EXACT la starea de bază.
   **și lotul C** (D100 + D101, hrănite de nota contabilă) — ciorna nu mișcă nimic, validarea
   mișcă exact cu suma notei, iar impozitul din D100 e 16% din rezultatul calculat de D101.
   **și lotul D** (D112) — declarant → salariat → stat de plată → rând; contribuțiile din
   declarație sunt leu cu leu cele din statul de plată. **și lotul E** (D406/SAF-T + D205) —
   **etapa 2 e închisă, toate cele nouă sunt probate**.
   *Lotul E a scos un defect desfăcut în patru — **R165** (SAF-T-ul unei firme trimestriale
   raporta o lună din trei), **R165b** (oglinda de reconciliere, prinsă de propria noastră
   gardă), **R165c** (antetul rămas pe luna-ancoră: reparația transformase o lipsă într-o
   minciună), **R166** (validarea D406 era INACCESIBILĂ — niciun corp nu trecea și generarea și
   validarea), **R166b** (numit de validatorul oficial la prima lui rulare reală). **Fiecare pas
   a făcut vizibil pasul următor.***
   *Și o lecție despre instrument: **proba mea a ascuns R165c o rulare întreagă**, fiindcă
   verifica antetul căutând ramura pe care fișierul n-o emite — v. lecția 17.*
   *Lotul D a scos **R164** (al doilea `500` al zilei pe o intrare PLAUZIBILĂ) și a ascuțit
   instrumentul de perimetru: un comparator de declarații nu e un hrănitor, deci se scoate
   din închidere — nucleu total 103 → 72, `DECIZII.md` 68.*
   *Lotul C a scos **R163**: un `500` pe un cont PLAUZIBIL — pe care etapa 1 nu-l putea vedea,
   fiindcă santinela ei nu semăna cu niciun cont și ramura care crapă nici nu se executa.*
   *Firma se alege după CUI I SE APLICĂ declarația, nu după firma campaniei — `DECIZII.md` 66.*
   *Regula formei: așteptarea se scrie ÎNAINTE, ca formulă, și poartă semantica intrării —
   `DECIZII.md` 64. De trei ori în lotul A un „defect" era de fapt așteptarea mea.*
2. **Ce e permis fără să întrebi:** un **prag 1** găsit apăsând.
3. **Următoarea temă vine de la Costin, după pilot.**
4. **Înainte de orice probă pe ecran:** `publica_static.py --din-arbore`.
5. **Ce rulezi:** `scripts/perimetru.py` decide. Poarta completă **înainte de publicare și înainte de
   `/clear`**.
6. **Cifrele nu se scriu în predare.** Blocurile sunt generate; „unde suntem" se derivă cu
   `scripts/raport_b.py`.
7. **Cele CINCI reguli de conducere a lucrului** sunt în `PLAN_LUCRU.md`.


## PACHETUL DE LIVRARE — se face la CAPĂTUL fiecărei teme, și n-a fost scris nicăieri

**De ce e aici, din 08.09.2026.** P0, P1 și P2 au produs fiecare câte un pachet
(`~/iconta_P0_2026-09-07.zip`, `~/iconta_P1_2026-09-08.zip`, `~/iconta_P2_2026-09-08.zip`).
Remedierea P2 **nu a produs unul**, iar Costin a trebuit să întrebe. Cauza nu e neglijență: convenția
exista doar în firul conversației, iar firul fusese golit (`/clear`) înainte de remediere. *O regulă
care trăiește numai într-o sesiune se pierde exact la prima sesiune nouă* — și de-aia se scrie aici,
în documentul care supraviețuiește golirii.

**Ce conține, după tiparul celor trei:**

- `iconta_<TEMA>/` ca director rădăcină, iar arhiva `~/iconta_<TEMA>_<AAAA-LL-ZZ>.zip`;
- `COMMIT_<TEMA>.txt` — hash, subiect, dată, `--stat`-ul commitului;
- `MASURATORI_<TEMA>.txt` — cifrele brute, cu instrumentul și calibrarea lui numite;
- `RAPORT_<TEMA>.md` — raportul, în forma din `SABLON_RAPORT.md`;
- **fișierele atinse, la căile lor din repo** (`core/…`, `scripts/…`, `main.py`) — nu o listă de
  fragmente: auditorul trebuie să poată pune arhiva peste o clonă și să vadă exact ce s-a schimbat;
- **registrele atinse**, întregi;
- **logurile brute**, dacă tema a produs măsurători.

**Ce NU se face:** nu se împachetează `venv/`, `.git/` sau `efactura_zip/`. Și nu se împachetează o
stare necomisă — pachetul se face **după** ce poarta a trecut și four-way-ul e închis, altfel
descrie o lume care nu există pe niciun server.
