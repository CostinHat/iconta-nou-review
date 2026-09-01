Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — **supervizorul construit**, **axa corpus-instrument închisă**, **două reguli noi de conducere a lucrului** (01.09.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-09-01**. Ultima **completă** a fost tot azi, cerută de Costin;
  deasupra ei, **o parțială** (tura supervizorului, a doua). Precedenta completă: 30.08.
- **pe commit**: `1a0c112` — ultimul commit intrat. *Predarea se scrie ÎNAINTE de commitul care o
  poartă, fiindcă blocul de cifre trebuie să intre ODATĂ cu ea. Ce descrie e arborele care devine
  commitul următor; numele de aici e al celui **precedent**, prin construcție, nu din uitare.*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **DE CE COMPLETĂ, acum**: nu fiindcă documentul se contrazicea — nu se contrazicea —, ci fiindcă
  **direcția s-a schimbat**. Axa pe care mergeau ultimele zile (corpus, instrumente, igienă) a fost
  **oprită de Costin, pe cifra ei**, iar tema care era „de arhitectură, pentru final" a devenit
  lucrul curent. Un document care descrie drumul vechi în structura veche ar fi trimis următoarea
  sesiune înapoi pe el.
- **CE S-A PĂSTRAT VERBATIM, și de ce**: cele două blocuri **generate** · **tabelul cifrelor
  invalidate** (se poartă, nu se deleagă) · **capcanele de procedură** · **operaționalul**. Astea
  sunt registru câștigat: o rescriere care le-ar fi „împrospătat" ar fi șters exact ce nu se poate
  reconstrui. *Restul e narațiune și s-a rescris.*
- **vechime măsurată, nu estimată**: **0 commituri** de la ultima atingere a fișierului.
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut;
  `core/test_predare_cifre.py` și `core/test_clichete_generate.py` nu lasă cele două blocuri
  generate să îmbătrânească.

---
## PRIMUL LUCRU DE ȘTIUT: CIFRELE DESPRE DATE SUNT INTEROGATE, NU SCRISE

Blocul următor e **generat** din bază de `scripts/scan_predare_cifre.py`, iar
`core/test_predare_cifre.py` îl compară cu interogarea **de la rulare**, caracter cu caracter. Dacă
nu se potrivesc, **poarta cade**. Nu se editează cu mâna. Regenerare:
`./venv/bin/python scripts/scan_predare_cifre.py --md`.

**De ce există:** pe 28.08 am scris aici *„0 din 18 firme au `nume_anaf`"*. Real: **1 din 18**. Cifra
fusese **deja invalidată o dată**, iar corectura era în tabelul „cifre invalidate" **din aceeași
predare**. Am purtat-o din memorie, peste propriul meu tabel, la douăzeci de minute după ce
scrisesem regula care o interzice (`METODA §10.16`). *O regulă scrisă nu ține fără control mecanic.*

<!-- CIFRE-DATE:START (generat de scripts/scan_predare_cifre.py --md) -->

*Generat din bază. **Nu se scrie cu mâna** — `core/test_predare_cifre.py` compară blocul cu interogarea curentă și pică dacă diferă. Regenerare: `./venv/bin/python scripts/scan_predare_cifre.py --md`.*

**Portofoliu**

| cifra | ce e |
|---|---|
| **19** | firme în portofoliu |
| **19** | din care active |
| **15** | la cabinete reale |
| **4** | la cabinete de test |
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
| **19** | scheme `tenant_NNN` în bază |
| **47** | contorul `tenant_schema_seq` |
| **46** | maximul istoric de nume de schemă |

**Clasificatorul de alerte**

| cifra | ce e |
|---|---|
| **2** | predicții de alertă confruntate cu faptul |
| **2** | din care greșite |

**Referințe moarte**

| cifra | ce e |
|---|---|
| **69** | rânduri care trimit la o firmă inexistentă |
| **14** | tabele din `public` cu `tenant_id`, numărate |

<!-- CIFRE-DATE:STOP -->

---

## AL DOILEA: UNDE SUNTEM ÎN PLAN

- `PLAN_LUCRU.md` are **5 etape** (E1–E5) și **3 puncte de decizie**. `PLAN_INVESTIGATII.md` are
  **8 faze**, mapate pe ele: E1 = faza 1 · E2 = faza 2 · E3 = fazele 3–6 · E4 = faza 7 · E5 =
  reparațiile.
- Suntem la **E1 — SETUL COMPLET**. Cei patru pași ai fazei 1 (1a–1d) sunt **făcuți**, din 29.08.
  **Criteriul de terminare al etapei NU e îndeplinit** — *„gata cu pașii" nu e „gata cu etapa".*
- **Listele verdictului 1d:** lista 1 — 1 artefact (registrul de casă) · lista 3 — **1 deschis din
  7**, cifră **DERIVATĂ** (`scripts/scan_lista3.py`) · lista 4 — **GOALĂ** · lista 5 — **COMPLETĂ**.
- **Lista 3 e ÎNCHISĂ ca sursă de construcție** (Costin, 31.08). Rândul rămas e deschis **pe
  producător**. *Premisa ei — „datele există, lipsește documentul" — a căzut.*
- **PREMISA LISTEI 3 A CĂZUT, și e mai mare decât oricare rând al ei.** Se construise pe
  *„datele există, lipsește documentul"*. **Fals de două ori într-o zi**: un nontransfer nu se
  derivă din nimic, iar valoarea de inventar vine din numărare faptică. *Rândurile rămase nu sunt
  transport până nu se dovedește.*
- **CE A SCOS REMĂSURAREA LISTEI 3, și e lecția de purtat mai departe:** „nu iese din vina
  aplicației" acoperea **trei** lucruri care nu seamănă între ele — *nu există producător* · *există
  și n-are ieșire* · *rândul minte*. De-aia tabelul are acum coloanele **A producător / B rută /
  C ecran**, nu o „cauză". **Patru dintre cele cinci s-au construit pe 30-31.08**: cele două
  registre din normele art. 321, registrul-inventar (14-1-2), registrul de evidență fiscală (care e
  **tot două**: art. 19 profit + art. 68 persoane fizice), și categoria de mărime. *Fiecare a pornit
  de la temeiul legal, nu de la ecran.*
- **Ce NU intră în lista 5, prin decizie:** cele **15** reguli DS acoperite doar la suprafață **nu
  sunt datorie** — sunt limita unui scaner static, corect diagnosticată, și cer un instrument care
  cheamă rute: **faza 2**. Iar cele **18 fără ancoră** sunt **R104**: defect al regulii, nu al
  instrumentului.
- **CE A SCOS REPARAȚIA LISTEI 5, și e partea de reținut**: despărțirea de preț măsurată la 1c —
  *„declarațiile sunt scumpe, registrele sunt ieftine"* — **a ținut doar pe jumătate**. Registrele
  chiar au fost ieftine. Cele 9 declarații **n-au fost scumpe**: componentele existau deja pe
  obiectele de rezultat ale motoarelor, deci lipsea **transportul**, nu calculul. *Afirmația „nici
  ruta nu trimite" era adevărată despre RĂSPUNS și falsă despre ce are motorul în mână, iar cele
  două nu fuseseră deosebite.* Singura poziție care chiar e scumpă e **D112**, și din alt motiv
  decât se credea: nu că n-ar avea componente, ci că generatorul ei nu le întoarce.

- **DAR ORDINEA DE LUCRU NU MAI VINE DIN PLANUL DE FAZE.** Din 01.09, Costin conduce pe **temă**, nu
  pe fază: axa corpus-instrument s-a închis, iar supervizorul a intrat în lucru. *Planul rămâne
  valabil ca hartă a etapei; nu mai e coada din care se ia următorul lucru.*

---

## AL TREILEA: DE UNDE SE PORNEȘTE, DACĂ EȘTI O SESIUNE NOUĂ

### 0. Citește cele două reguli noi de conducere a lucrului (`PLAN_LUCRU.md`, 01.09)

1. **Deciziile care nu mută direcția sunt ale tale, nu urcă la arhitect.** Testul: *dacă răspunsul
   lui Costin ar putea fi înlocuit cu un default rezonabil fără ca nimic din plan să se mute,
   întrebarea n-avea ce căuta la el.* Ce urcă: ce schimbă direcția, un contract pe care se sprijină
   altcineva, ritmul de muncă al contabilului, sau ce n-are răspuns care să nu fie o presupunere.
2. **O tură care nu schimbă nimic pentru un contabil cere justificare SCRISĂ**, în `§2` al
   raportului. Nu e interzisă — nu mai e **implicit acceptabilă**.

### 1. AXA CORPUS-INSTRUMENT ȘI IGIENĂ E ÎNCHISĂ (Costin, 01.09)

*Motivul, al lui, scris:* „criteriul aplicat cinstit a scos populația 4 și o reparație. Axa nu mai
are randament, iar restanțele cresc mai repede decât se închid."

**R112, R113, R114 rămân DESCHISE și NEREPARATE. #33, #67, #70 rămân NEMĂSURATE. Restanțele noi din
familia asta se CONSEMNEAZĂ, nu se lucrează.** *Nu e o judecată despre corectitudinea muncii — e una
despre randament. Nu redeschide axa fiindcă „mai era puțin".*

### 2. SUPERVIZORUL — CONSTRUIT 01.09, NELEGAT INTENȚIONAT

`core/supervizor.py`. Umple gaura măsurată: din tot ce confruntă aplicația, **o singură** pereche era
**orizontală** (declarație contra declarație); restul e vertical — fiecare declarație față de propria
sursă. *Nouă declarații verificate fiecare pe verticala ei nu produc nicio afirmație despre coerența
dintre ele.*

- **Două tării** *(Costin)*: **euristice** — semnalează, nu opresc niciodată · **certe** —
  nepotrivire aritmetică; **nu blochează**, dar cer **confirmare explicită** înainte de depunere, iar
  confirmarea **rămâne scrisă**.
- **Împărțirea pe tării e A LUI COSTIN, pe tipuri. Supervizorul n-o deduce.** Tabelul `TIPURI` o
  așteaptă ca **date**: tip necunoscut → **ridică**; tip cunoscut dar neatribuit → **se vede și nu
  produce niciun efect**. **R115**, singura cerință deschisă către el.
- **Confirmarea se dă pe CIFRE**, nu pe tip: amprenta e în cheia primară a jurnalului
  `public.supervizor_confirmari` (aplicat, gol). O reformulare nu invalidează o confirmare; o cifră
  schimbată o invalidează. *Fără asta, „confirmare explicită" devenea o bifă permanentă.*
- **DOMENIUL E CONSTRUIT** *(tura a doua, 01.09)* — `ruleaza_portofoliu`. Din cele **trei** fațete pe
  care `PLAN_LUCRU` le dă supervizorului (*„declanșator propriu, domeniu propriu și ieșire proprie"*),
  domeniul era **singura deja decisă**: *„rulează pe portofoliu, nu pe un act"*. Funcția e
  **chemabilă**, nu programată și nu rutată — deci nu atinge niciuna din cele două întrebări ale lui
  Costin. Trei rezultate EXCLUSIVE per firmă (`CONSTATARI` / `FARA_SUBIECT` / `NEVERIFICAT`), iar
  rezumatul e **derivat** din listă, nu acumulat pe drum.
- **PE PORTOFOLIUL VIU, AZI:** `CONSTATARI 16 · FARA_SUBIECT 0 · NEVERIFICAT 3`, suma **19** =
  domeniul. Toate cele 16 sunt **gri** („n-am ce compara"), **zero roșii**. Cele 3 neverificate sunt
  **numite**, cu cauza (D390 nu se poate calcula — profil incomplet). *Asta face răspunsul la R115
  mai ieftin de dat: atribuirea tăriei nu schimbă nimic azi.*
- **A CINCEA CALE, care era tăcută — și e lecția turei.** Comparația orizontală avea **cinci** ieșiri,
  nu patru. Gardul de ieri proba cele patru ale funcției PURE; a cincea — *nicio depunere D300* —
  trăia un nivel mai sus, în `verifica_d390`, și chema `_absenta_libera` **fără ștampilă**.
  **Măsurat: supervizorul vedea 3 constatări orizontale și pierdea tăcut 13.** Reparat structural
  (`orizontal_d390_vs_d300` — o singură ieșire): **3 → 16**, **13 → 0**. *„Modulul e complet și
  probat" era fals ieri, și n-avea cum să se vadă: gardul se uita exact unde era codul corect.*
- **De ce rămâne NELEGAT:** cele două lucruri care l-ar cabla — **ce declanșează o rulare** și **ce
  vede contabilul din ea** — sunt scrise în `PLAN_LUCRU` ca fiind ale lui Costin, nedecise. A-l cabla
  ar însemna să le decizi tu. E în `PIN` cu motivul, nu e cod mort: **21 de teste**, mutație pe
  **cinci** direcții.
- **Ce rulează deja pe cont propriu, și exista dinainte:** cronul de la 08:00
  (`notificari_scadenta` → `alerte_control_fiscal.ruleaza()`) trece portofoliul prin **patru**
  verificări și împinge în clopoțel **doar roșul**, agregat pe firmă.

### 3. CE SE ȘTIE DESPRE LISTELE PE CARE LE URMEZI (măsurat 01.09)

**Trei dintre cele cinci sunt una singură:** restanțele deschise și interdicțiile neîncepute sunt
**100% conținute** în cele 114 rânduri ale lui `scan_ramas.py`. Rămân trei distincte, și **abia se
ating**: 90% din ce atinge checklistul de browser nu apare în backlog; 89% din backlog n-are nicio
verificare de browser. *Nu se dublează munca — se ratează.* Recalculabil:
`./venv/bin/python scripts/masoara_suprapunerea.py` (fără gardă și fără clichet, deliberat).

---

## AL PATRULEA: CE E ADEVĂRAT DESPRE STAREA CODULUI

- **restanțe deschise: 48** (din care ale etapei E1: **23**), derivat cu `scripts/raport_b.py`.
  **Nu se scrie de mână** — rândul ăsta a fost invalidat o dată.
- **interdicții, din 77**: MĂSURATE **23** · PARȚIAL **16** · NEMĂSURABILE **5** · NEÎNCEPUTE **33**.
- **locuri de verificare**: **221 scrise / 0 goale din 221 (100%)**.
- **decizii care blochează: niciuna.** Singura cerință deschisă e **R115** (tăria constatărilor).
- **clusterele topologice**: `core.agenda.urmator_cluster()` → **`(None, 0, 0)`**; secvența e
  epuizată din 04.08.2026 — **nu există „următorul programat"**.
- **cele mai vechi restanțe deschise**: R1, R3, R4, R5, R6, R7 — familia „încrederea în corpus",
  acum **în afara axei de lucru**.
- **deschise pe 01.09**: R110 *(închisă în aceeași zi)* · **R111** *(închisă)* · **R112** · **R113** ·
  **R114** · **R115**. *Patru rămân deschise, trei dintre ele pe axa oprită.*

---

## STAREA LA PREDARE

Poartă verde, citită din ieșirea rulării complete de pe arborele care devine commitul următor:
**3928 teste trec** · 11 skip · 14 xfail · ruff OK · verificator **TOTAL 0** ·
rute **423 = ACCEPTAT 382 + GRI 7 + ROSU 0 + EXCLUS 34** · site **200** · four-way se închide la
`post-commit`, care publică pe `origin/main` și pe `backup/lant-<ziua curentă>` și **restartează
necondiționat** procesul viu.

**AL PATRULEA BRAȚ AL FOUR-WAY-ULUI.** Ștampila de RUNNING trăiește **numai în memoria procesului**,
iar endpointul care o citește (`GET /admin/versiune`) cere **superadmin**. Cele două lecturi:
(a) mintezi un token de superadmin — tiparul din `frontend_test/w_auth.py` — și citești `running`,
`head`, `divergent`, `necunoscut`; (b) **proba gardată**, fără token: *ora de pornire a procesului >
ora commitului*. **Pe 01.09 s-a folosit (b) de patru ori** — o verificare de rutină nu justifică
emiterea unui token de superadmin.

**VERIFICATORUL DE NECONFORMITĂȚI ARE TREI REZULTATE**: `PASS` · `FAIL` · **`NEVERIF [cod]`**. Codul
de ieșire **2** înseamnă „nu s-a putut verifica tot". *Nu-l consumă nimic programatic; se rulează cu
mâna.* Stare: `PASS 18 · FAIL 0 · NEVERIF 2`. **Ancora NC-02 e retrasă**, cu motivul în script —
*o verificare ancorată pe PREZENȚA unei reparații moare la prima rescriere legitimă a codului
reparat; una ancorată pe EFECT nu.*

**CLICHETELE VII — blocul de mai jos e GENERAT, nu scris.** Gardat de
`core/test_clichete_generate.py`; regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.

<!-- CLICHETE-VII:START (generat de scripts/scan_ramas.py --clichete-md) -->

*Generat din COD. **Nu se scrie cu mâna** — `core/test_clichete_generate.py` recalculează și compară caracter cu caracter. Regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.*

| cod | acum | ce se numără | instrument |
|---|---|---|---|
| **77** | **61** | refuzuri fără temei în module care citează legea | `scripts/scan_refuzuri.datorie()` |
| **77u** | **784** | UMBRA: refuzuri în module care nu citează legea (nedeplafonat) | `scripts/scan_refuzuri.umbra()` |
| **50** | **1222** | aserțiuni ancorate pe text, nu pe structură | `core/scan_garzi_pe_text.pe_fel()` |
| **R80** | **7** | rute despre care detectorul de apelanți nu poate afirma nimic | `scripts/scan_ancore_rute.verdicte()` |

<!-- CLICHETE-VII:STOP -->

**CE A RĂMAS DE FĂCUT se citește rulând `./venv/bin/python scripts/scan_ramas.py`** — 114 rânduri,
șase surse, defalcat pe fel. *Cifrele NU se scriu aici.*

**POARTA DUREAZĂ ~21 DE MINUTE** — măsurat pe cele nouă rulări de pe 01.09: 1134s … 1281s. Suita a
crescut de la 3862 la 3928 de teste într-o zi. *E cifra pe care o folosește cine estimează o tură:
o tură cu două commituri costă ~45 de minute doar în porți.*

**TURA SUPERVIZORULUI (a doua) A FOST RESPINSĂ DE PATRU GĂRZI CARE NU ȘTIAU CĂ VINE, ȘI TOATE
PATRU AVEAU DREPTATE — toate patru pe greșeli ale mele, în același commit:** `ruff` **F821**
(importul local `_d390` s-a pierdut la extragerea blocului — efectul era o degradare **tăcută** în
gri, adică exact clasa pe care o reparam) · `test_afirmatii_tipate` („firma n-a fost verificată" era
proză într-o cheie, nu afirmație tipată; felul potrivit — `verificare_rupta` — exista deja în
nomenclatorul închis) · `test_garzi_pe_text` (**trei** aserțiuni ale mele erau pe text, rescrise pe
structură) · `test_clichete_generate` (umbra 77u crescuse cu 1). *Confirmă, a doua zi la rând, că un
modul nou e gata abia când trece gărzile care nu-l așteptau.*

**PE 01.09 POARTA A RESPINS DE ȘAPTE ORI, ȘI NICIO RESPINGERE N-A FOST FALS POZITIV.** Toate au fost
gărzi scrise înainte, care au prins forme reale: clichetul **50** (aserțiuni pe text — **de două
ori**, amândouă ale mele) · clichetul CIOT · afirmații netipate · registrul de excepții · module
nelegate · o tabelă cu `tenant_id` neclasificată · și **de patru ori blocuri generate
neregenerate**. *Un modul nou nu e „gata" când trece testele lui — e gata când trece gărzile care nu
știau că vine.*

**Cifrele de aici se copiază din IEȘIREA PORȚII, nu din predarea de dinainte.**
**Cifrele secțiunii „Unde suntem" nu se scriu de mână** — `scripts/raport_b.py`.

**O ORDINE CARE COSTĂ O RULARE:** la o schimbare de JS, `versioneaza_assets.py --scrie` vine
**ÎNAINTEA** lui `interactiune_scan.py`, nu după. Rulate invers, scanul vizual e deja învechit când
versionarea termină, iar poarta cade pe alt fișier decât cauza.

---

## CE E ADEVĂRAT ACUM DESPRE RESTANȚE

| | |
|---|---|
| **prag 1** | **niciuna deschisă.** |
| **R115** | **singura cerință către Costin.** Tăria constatărilor supervizorului, pe tipuri. Fără ea, motorul rulează și arată, dar nimic nu cere confirmare. *Nu e o restanță de muncă — e una de decizie, cu câmpul `planul` completat: planul NU răspunde.* |
| **R112 · R113 · R114** | deschise pe 01.09, **și rămân nereparate prin decizie** (axa oprită). R112 — ianuarie 2026 stă pe un act care nu era în vigoare · R113 — 8 acte de corpus nevăzute fiindcă poartă așezarea Monitorului Oficial · R114 — ecranul Intrastat compară fluxurile anului cerut cu pragul de **azi**. |
| **lista 4 · lista 5** | **GOALE / COMPLETE**, prin reparație. Rămâne **R105** (D112, schimbare de MOTOR). |
| **R94 · R95 · R96 · R97 · R98 · R99 · R100 · R104** | deschise, prag 2, cu condiția scrisă. R100 și R104 au fost cerute **explicit** ca gărzi de construit mai târziu. |
| **familia „încrederea în corpus"** | R1, R3, R4, R5, R6, R7, R107 — cele mai vechi, acum **în afara axei**. |
| **restul** | `CONFORMITATE.md`, sau `scripts/scan_ramas.py`. Numărul e derivat, nu scris. |

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează. Tabelul se
POARTĂ, nu se deleagă în istoric.*

**Clasa asta are un mecanism, nu doar un tabel:** cifrele despre **date** nu mai pot îmbătrâni,
fiindcă sunt generate. Tabelul rămâne pentru cele despre **cod** și **proces** — și ca istorie.

**CE ARATĂ TABELUL, CITIT CA ÎNTREG (01.09):** din cele **patru** intrări noi de azi, **toate patru**
sunt greșeli ale **sondelor mele**, nu ale aplicației — și trei din patru sunt **aceeași greșeală**:
*am numărat FORMA în loc de EFECT*. O paranteză cerută după un nume de funcție. Un argument socotit
absent fiindcă n-avea cuvânt-cheie. O cheie de dicționar trunchiată care înghite rânduri. *Clasa are
acum un nume și patru instanțe într-o zi.*

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

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

### despre lanțul facturii — ce s-a construit azi și ce a rămas în afară

- **Fals-negativul cheii e MICȘORAT, nu închis.** Rămân notele scrise înainte de azi (nu se leagă
  retroactiv), cazul cu două potriviri (unde legarea refuză deliberat), și o contare făcută pe
  `461`/`462`, pe care semnătura n-o vede.
- **Mecanismul `factura_id` greșea în AMÂNDOUĂ direcțiile, iar reversul nu era numit nicăieri.** O
  notă care poartă cheia și **nu** e o contare **blochează** contarea. **3 facturi** erau exact așa
  azi-dimineață; de-asta există actul de dezlegare.
- **Cele două acte noi n-au ecran** — nici dezlegarea, nici recunoașterea. Nici calea care aduce
  documentul (`POST /import-efactura`) n-are. Motivul e măsurat: **nicio cale din `static/` nu șterge
  o factură**, deci și `DELETE /facturi/{id}` e act de API. Clasa e **R70**, deschisă; orbirea
  detectorului pe căi compuse e **R80**, deschisă. Niciuna nu s-a redeschis — amândouă erau deschise.
- **Perimetrul lui R91 e mai îngust decât scria la deschidere**: `spv_receive` scrie doar în
  `efactura_primite`, și doar primite. Singura cale prin care o factură **emisă** intră prin import e
  încărcarea manuală de XML. *Comentariul din `main.py` care spunea altceva era fals; e corectat.*
- **Starea `de_recunoscut` e DECLARABILĂ, și e deliberat.** „Ciornă" se referă la **nota contabilă**,
  nu la caracterul fiscal: TVA-ul e datorat la emitere (art. 281 CF). O stare nedeclarabilă ar fi scos
  factura tăcut din D300 — defectul 1.1 din 22.08. *Cuvântul din comandă putea fi citit și altfel.*
- **Starea nouă `de_recunoscut` NU ARE ETICHETĂ PE ECRAN**, găsit pe 29.08 seara, la scrierea
  ISTORICULUI. `static/js/ecrane/facturi_ecran.js:476` are `STATUS_ETICHETA` cu patru intrări, iar
  linia următoare cade pe `|| f.status` — deci contabilul vede șirul brut `de_recunoscut`. **E o
  clasă, și greșește în amândouă direcțiile** (`METODA §22`): nomenclatorul are **8** stări, eticheta
  acoperă **4**; cinci n-au etichetă (`importata`, `de_recunoscut`, `ciorna`, `descarcata`,
  `stornata`), iar una — `platita` — numește o stare care nu există în nomenclator. **Măsurat pe
  cele 19 scheme: 10 facturi din 41 cad azi pe ramura brută** — nu e latentă. **Deschisă ca R92**, cu
  condiția de deblocare scrisă acolo: etichetele se **derivă** din nomenclator, cu gardă care
  confruntă cele două liste în amândouă direcțiile. *Nu s-a reparat în tura în care a fost găsită
  fiindcă era o tură de registre; orice atingere de JS cere și lanțul vizual (~7 min).*
- **Cele 31 de note ale istoricului au intrat `ciorna`**, ca oricare alta. Patru-ochi rămâne unde e
  (**R47**, deschisă): evidența are notele, dar nu le-a validat nimeni.
- **11 dintre ele poartă data descoperirii, nu data faptului** — cu mențiunea care le leagă de
  factură. Nu e o dată arbitrară, dar nici data faptului nu e.
- **Regula de datare are un caz pe care NU-l acoperă**: dacă și luna emiterii, și luna descoperirii
  sunt închise, nu există nicio dată validă și actul **refuză**. `tenant_001` e instanța. Ieșirea e
  redeschiderea unei luni — act cu urmă.
- **Cele 3 facturi din fosta clasă R90 se pot acum șterge**, dar numai după o dezlegare explicită, cu
  motiv. *Niciuna n-a fost ștearsă: proba rulează în tranzacție întoarsă.*
- **Două clase reparate sunt LATENTE, nu probate pe instanță vie**: nota de plată a unei firme cu TVA
  la încasare (nicio firmă din portofoliu nu e în regimul ăla) și referința moartă pe care ștergerea
  ar lăsa-o în `extras_linii.alocari` (14 linii au `alocari`, **zero** numesc o factură). *„Reparat pe
  clasă" și „probat pe instanță" nu sunt același lucru.*
- **Clasa „verde peste gri" e LATENTĂ** — nicio instanță vie prinsă, fiindcă semnalul pe 4428 nu se
  aprinde pe datele curente.
- **Nicio factură din lista istorică n-ar fi fost refuzată azi pentru lună închisă** (0 pe criteriul
  mecanic, 1 pe „sub ultima blocată"). *E o stare a datelor de test, nu o proprietate a stocului — pe
  date reale proporția s-ar inversa.*
- **Gaura de idempotență e măsurată: 14 note pe citirea largă, 2 pe cea strictă, ZERO coliziuni
  reale.** **Dar zeroul nu absolvă nimic**, și e partea care contează: pe toate cele 19 scheme,
  `sursa='manual'` apare de **zero** ori. Calea liberă (`POST /jurnal`) — chiar calea numită
  periculoasă — **n-a fost folosită niciodată**. Nu s-a măsurat că gaura e inofensivă, ci că **nimeni
  n-a intrat încă pe ușa prin care se cade**. *Punctul orb e FIRMA, nu ecranul.*
- **Sonda R35 nu întreabă dacă facturile alea CHIAR trebuiau contabilizate în luna aia.**

### despre supervizor

- **Nu confruntă nimic în plus față de ieri.** Are **o singură** pereche orizontală — cea care exista
  deja. Ce s-a construit e **locul** unde stau perechile, **contractul** lor și **domeniul**, nu
  perechi noi. *Tura a doua a reparat cine VEDE constatările, nu a adus constatări noi.*
- **Perechea lui răspunde azi, întotdeauna, „n-am ce compara" — și populația ei e ZERO, nu 1.**
  Din 55 de depuneri, 1 are rânduri persistate, dar aceea e un **d301**; dintre cele **3** depuneri
  **d300**, **niciuna** n-are rânduri. Calea curentă le persistă (verificat la sursă:
  `coada_api.randuri_din_res` + `marcheaza_depusa`), deci populația crește de acum înainte.
- **NU S-A CONSTRUIT NICIO PERECHE NOUĂ, și motivul e neschimbat:** identitatea fiscală n-are temei
  scris. *Domeniul se putea construi fără temei nou; o pereche, nu.*
- **N-am adus perechi noi (D394↔D300, D101↔D100) fiindcă n-am putut scrie identitatea fără s-o
  inventez.** Nu e un „mai târziu" vag: e refuzul de a pune o identitate fiscală nedovedită într-un
  motor care produce afirmații despre datele unei firme.
- **Nimic din el nu are ecran.** Ce vede contabilul e nedecis.

### despre măsurători și instrumente

- **Blocul de cifre e derivat din date VII, nu din cod.** Dacă portofoliul se schimbă între generarea
  blocului și sfârșitul porții (~21 min), garda **pică** — și pe drept. **Blocul se regenerează
  ULTIMUL.**
- **Predarea nu se mai poate scrie fără acces la bază.** Scenariul care doare: baza jos — atunci nici
  poarta nu rulează, dar handover-ul e blocat exact când e mai necesar.
- **Gardul de cifre nu interzice o cifră de date în PROZA predării.** Ce nu mai are voie e ca
  **tabelul** să fie scris din memorie.
- **`main.py` are 131 de commituri în 30 de zile** și e numit de **6** restanțe deschise. E cel mai
  atins fișier din repo. *Nicio restanță nu e despre asta.*
- **Din 131 de fișiere numite de liste, 10 n-au fost atinse deloc în 30 de zile.**
- **Punctul orb e FIRMA, nu ecranul.** Un scan vede doar stările pe care le produc datele firmei pe
  care rulează.

### despre ce s-a oprit

- **Cele trei restanțe ale axei oprite nu sunt „aproape gata".** R114 cere o schimbare de verdict
  afișat, cu poartă vizuală. R113 cere extinderea a **două** tipare (numărătorul și localizatorul),
  cu direcția periculoasă măsurată: 2 fișiere ar câștiga titluri **false**. R112 cere un act adus.
- **Nu redeschide axa fiindcă „mai era puțin".** Decizia e pe randament, iar cifrele care au produs-o
  sunt în `DECIZII.md` (33).

---

## PATRU CAPCANE DE PROCEDURĂ, ÎNVĂȚATE PE PIELEA MEA ÎN ULTIMELE TREI ZILE

1. **Un `str.replace` fără aserțiune nu e o modificare, e o speranță.** A lovit de **trei ori** pe
   tabelul de restanțe din predarea asta. Unealta: `scripts/inlocuieste.py`. Regula:
   `METODA_VERIFICARE.md` **§28**.
2. **Poarta testează ARBORELE DE LUCRU, nu indexul.** Un `@COMMIT@` lăsat în `CONFORMITATE.md` pică
   poarta chiar dacă fișierul nu e în commitul curent. Ordinea celor două commituri — lucrul întâi,
   registrul după, cu hash-ul real — **nu e stil, e o constrângere**.
3. **Raționamentul care ține o restanță DESCHISĂ cere aceeași verificare ca cel care o închide.** Pe
   28.08 am ținut R34 deschisă pe o condiție îndeplinită de trei zile. *E mai ușor de ratat fiindcă
   rezultatul lui pare prudent.*
4. **Un scan pe forma BRUTĂ a datelor supra-numără.** De trei ori în două zile: rute, denumiri,
   regimuri. De fiecare dată citirea la sursă a corectat cifra, și de fiecare dată defectul era al
   instrumentului, nu al aplicației. *Înainte de a raporta o cifră dintr-un scan nou, întreabă dacă
   aplicația normalizează ce numeri tu brut.*

---

## OPERAȚIONAL — ce se rupe repetat

- Serverul e `ssh iconta`; `psql` direct e **blocat** — script prin stdin, cu `db.init_pool()`.
- **Repornirea o pot rula EU**, din 30.08: `sudo -n systemctl restart iconta-nou` e în setul îngust
  de sudoers. **`usermod` și `install` sunt ținute AFARĂ, deliberat** — apartenența la grupuri e
  schimbare de identitate, iar `install` scrie oriunde ca root, deci setul și-ar putea rescrie
  propriile reguli. *Refuzurile lor sunt dovada că îngustarea e reală.*
- **Un `ssh` scris după `&&` într-o comandă `ssh` rulează PE SERVER**, unde `iconta` nu se rezolvă.
  S-a întâmplat azi: al doilea pas al unui lanț a eșuat tăcut, cu „Could not resolve hostname".
- **Env obligatoriu**: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a`
  (+ `PYTHONPATH=/home/costin/iconta_nou` pentru scripturile din `frontend_test/`).
- **Mesajul de commit se trimite prin FIȘIER, nu prin heredoc în argumentul ssh.** Un `"` îl
  trunchiază în tăcere; s-a întâmplat de două ori pe 27.08, a doua oară jumătate de mesaj.
- **Un patch rulează PE SERVER** — pe Windows, `io.open(..., "w")` trece fișierul la CRLF în tăcere și
  face fiecare diff viitor zgomotos.
- **Ghilimelele românești rup șirul Python** — `„...”` cu închidere `"` ASCII termină literalul.
  **De șapte ori într-o zi, pe 30.08.** Se scrie cu `«»` în literale, sau cu apostrof la delimitare.
- **Backtick-urile dintr-un heredoc `<<EOF` neghilimetat sunt executate de shell.** Se folosește
  `<<'EOF'`, sau se trimite fișierul prin `cat ... | ssh`.
- **Un escape de tip BACKSPACE într-un literal ne-raw devine octet de control.** Prins de
  `test_octeti_invizibili`, și în mesajul de commit.
- **Stage pe nume, niciodată `git add -A`.** Escape declarat: `# multe-fisiere-ok:`.
- **O probă care ține o tranzacție deschisă nu poate deschide o a doua conexiune pe același rând.**
  Iar `SET search_path` e tranzacțional: după `rollback`, numărătorile se citesc pe o conexiune nouă.
- **O probă care blochează o lună trebuie s-o deblocheze în `finally`** — altfel otrăvește toți pașii
  de după.
- **În probe, `observare.alerteaza` se patch-uiește** — altfel `esec_secundar(alerta=True)` trimite
  alerte REALE prin Brevo.
- **O probă pe ecran care dezactivează o firmă nu mai găsește lista de firme** — se așteaptă
  `button.firme-rand, .firme-gol`, nu doar primul.
- **O schimbare de JS cere**: `versioneaza_assets.py --scrie` **și**
  `frontend_test/vizual/interactiune_scan.py` (~7 min, artefactul se comite).
- **Trei blocuri generate cer regenerare**: `TRASEE.md` (la refuzuri noi), `GARZI.md` (la gărzi noi),
  **`PREDARE_LANT.md`** (la orice schimbare de date).

---

## DACĂ CONTINUI DE AICI

1. **NU REDESCHIDE AXA CORPUS-INSTRUMENT.** R112/R113/R114 se consemnează, nu se lucrează
   (`DECIZII.md` 33). #33, #67, #70 rămân nemăsurate.
2. **UMBRA INTERDICȚIEI 77 E ÎNCHISĂ DEFINITIV** (`DECIZII.md` 15): nu se auditează, nu devine
   restanță, **nu se mai deschide ca temă**. *Nu e „nu acum", e niciodată.* Cifra ei trăiește numai
   în blocul generat.
3. **Singurul lucru care blochează ceva e o DECIZIE a lui Costin, nu muncă** — tăria constatărilor
   supervizorului, pe tipuri *(restanța e numită în tabelul de mai sus)*.
4. **Cifrele de clichet nu se scriu în predare.** Blocul e generat. Dacă vrei o cifră de clichet în
   proză, întreabă întâi dacă populația are plafon — dacă n-are, îmbătrânește, iar
   `core/test_clichete_generate.py` te oprește.
5. **Înainte de a alege ce faci: rulează `scripts/scan_ramas.py` și MĂSOARĂ candidații.** Pe 01.09,
   candidatul ales pe criteriu s-a dovedit de 4 instanțe, nu de 68 — iar prima cifră venea din
   propria mea sondă. *Un candidat din vecinătate nu e un candidat.*
6. **Criteriul de prioritate, dat de Costin:** *ce poate produce o cifră validă și falsă.* **A
   funcționat, și merită spus cum:** aplicat pe supervizor, a scos în două ore un defect care ascundea
   **13 din 16** constatări, și a dat forma parcurgătorului de portofoliu (trei rezultate exclusive,
   rezumat derivat). *Criteriul nu spune „caută bug-uri" — spune „caută unde o cifră poate arăta
   corect și minți".*
7. **CLASA ARE ÎNCĂ O INSTANȚĂ, CONSEMNATĂ NEREPARATĂ — R116.** `alerte_control_fiscal.ruleaza()`
   numără firmele DUPĂ succes; una care ridică nu apare în niciun contor. Nereparată **cu condiția
   scrisă**: valoarea n-are consumator azi, iar bucla e chiar calea care trimite alertele reale.
8. **Justifică în scris orice tură care nu schimbă nimic pentru un contabil.**
