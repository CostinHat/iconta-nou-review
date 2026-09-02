Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — **supervizorul e LEGAT**, **patru perechi orizontale**, **și regula care spune ce descrie o tărie** (02.09.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-09-02**. **Rescriere COMPLETĂ**, cerută de Costin. Precedenta completă
  a fost pe 01.09; între ele, **cinci parțiale**.
- **pe commit**: `e82fbf72` — ultimul commit intrat. *Predarea se scrie ÎNAINTE de commitul care o
  poartă, fiindcă blocul de cifre trebuie să intre ODATĂ cu ea. Ce descrie e arborele care devine
  commitul următor; numele de aici e al celui **precedent**, prin construcție, nu din uitare.*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **DE CE COMPLETĂ, acum**: documentul precedent descria o aplicație în care **supervizorul era
  NELEGAT** și avea **o singură** pereche orizontală, iar cele două lucruri care l-ar fi cablat erau
  întrebări deschise. Toate trei s-au schimbat într-o zi: e legat (cron + rută + ecran), are **patru**
  perechi, iar întrebările au primit răspuns. *O sesiune nouă care ar citi vechea structură ar căuta
  un blocaj care nu mai există.*
- **CE S-A PĂSTRAT VERBATIM, și de ce**: cele două blocuri **generate** · **tabelul cifrelor
  invalidate** (se poartă, nu se deleagă) · **capcanele de procedură** · **operaționalul**. Astea sunt
  registru câștigat: o rescriere care le-ar fi „împrospătat" ar fi șters exact ce nu se poate
  reconstrui. *Restul e narațiune și s-a rescris.*
- **CE S-A SCHIMBAT DE LA RESCRIEREA COMPLETĂ DE AZI-DIMINEAȚĂ** *(tura a doua, 02.09)*: cele
  **cinci** comparații orizontale au fost **probate pe portofoliul viu**, fiecare pe date construite
  prin lanțul aplicației, și **fiecare a dat roșu cel puțin o dată**. Documentul de dimineață spunea
  că toate patru perechile sunt „corecte și calibrate" și că niciuna n-a avut subiect. **Prima
  jumătate era falsă** — v. tabelul cifrelor invalidate —, iar a doua nu mai e adevărată.
  `de_confirmat` nu mai e 0.
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
predare**. *O regulă scrisă nu ține fără control mecanic.*

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

## AL DOILEA: CE E SUPERVIZORUL AZI — și ce NU e

**E LEGAT.** A stat trei ture în `test_module_nelegate.PIN`, cu condiția de deblocare scrisă ca
RĂSPUNS, nu ca muncă. Răspunsul a venit pe 01.09, iar modulul a ieșit din PIN.

- **declanșator**: blocul izolat de pe **slotul de 08:00 care exista** (`core/notificari_scadenta`),
  **plus** `GET /supervizor` la cerere. Amândouă cheamă **aceeași** funcție —
  `supervizor.ruleaza_portofoliu`. *„Nu construi al doilea mecanism" (Costin).*
- **domeniu**: portofoliul. Ruta rulează pe firmele cabinetului apelantului, iar **un domeniu injectat
  RIDICĂ dacă nu e numit** — altfel răspunsul ar purta criteriul întregului portofoliu despre o
  mulțime filtrată.
- **ieșire**: cardul **„Supervizor"** de pe desktopul cabinetului, cu **temeiul** pe fiecare
  constatare și cu firmele **NEVERIFICATE numite separat**. Renderer-ul e împrumutat din
  `control_verdict.js`, nu rescris.
- **clopoțelul n-a cerut cod**: era deja cablat — o constatare orizontală roșie face `verifica_d390`
  roșu, iar `alerte_control_fiscal` o duce **agregat pe firmă**.

**TREI REZULTATE EXCLUSIVE PE FIRMĂ**, cu suma egală cu domeniul: `CONSTATARI` · `FARA_SUBIECT` ·
`NEVERIFICAT`. Rezumatul e **derivat** din listă, nu acumulat pe drum — o firmă nu poate dispărea
dintr-un contor pe care nimeni nu-l incrementează. *Tiparul opus e măsurat în
`alerte_control_fiscal.ruleaza()`, care numără DUPĂ succes: **R116**.*

### Cele PATRU perechi orizontale, și cât valorează fiecare

| pereche | tărie | ce confruntă | cât valorează VERDELE |
|---|---|---|---|
| **D390 ↔ D300 depus** | EURISTICA | baza IC recalculată vs rândurile D300 depuse | **slab** — ambele din aceleași facturi |
| **D101 rd.50 ↔ Σ D100** | CERTA | ce a scris contabilul vs ce s-a declarat trimestrial | real, dar pe **două declarații** |
| **D101 rd.48 ↔ cont 691** | CERTA | impozitul declarat vs cel înregistrat contabil | **real** — fiscal vs evidență |
| **D300 rd.12 ↔ D394 lit. C** | EURISTICA | două depuneri, pe taxare inversă | **slab**, și o spune singur (`verde_slab`) |
| **e-Factura ↔ D394** | EURISTICA | recipisa ANAF vs ce declară generatorul că a inclus | **cel mai tare** — singurele surse cu adevărat independente |

**Identitatea fiecăreia e verificată VERBATIM în corpus înainte de a fi scrisă în cod.** Unde nu s-a
putut, nu s-a construit: **R121** (P300 n-are acces programatic) e singura respinsă rămasă.

### DOUĂ REGULI ALE LUI COSTIN care guvernează tot ce urmează

1. **Criteriul tăriei** *(01.09)*: *„Tăria se dă după dacă diferența admite o explicație legitimă, nu
   după cine sunt cele două părți. Certă = orice nepotrivire e eroare."*
2. **Ce descrie o tărie** *(02.09)*: *„Tăria descrie IDENTITATEA, nu calitatea datelor noastre. Unde
   nu poți stabili că vezi tot, spui gri — ca la ciorna pe 691."*

**A doua a fost aplicată de patru ori**, și e cea mai productivă regulă din tot șirul: un trimestru
D100 nevăzut → gri care numește trimestrul · o notă în ciornă pe 691 → gri care numește nota · o
cheie `op1` necitibilă → gri · operațiuni **manuale** în D394 → gri, fiindcă o factură transmisă ar
putea fi acoperită de una fără să pot ști. *Fără regula asta, fiecare dintre cele patru ar fi produs
un roșu al orbirii mele.*

### CE SPUN PEREChILE AZI, PE PORTOFOLIUL VIU — măsurat, nu estimat

```
CONSTATARI 16 · FARA_SUBIECT 0 · NEVERIFICAT 3   (suma = 19 = domeniul)
constatari_total 92 · de_confirmat 1

D101_VS_CONT_691                 19   gri 18 · VERDE 1
D101_VS_D100_PLATI_ANTICIPATE    19   gri 18 · ROSU 1
D300_VS_D394_TAXARE_INVERSA      19   gri 18 · VERDE 1
EFACTURA_VS_D394                 19   gri 18 · VERDE 1
D390_VS_D300_IC                  16   gri 14 · VERDE 2
```

**Șase constatări cu conținut, pe trei firme** — `tenant_004` (trei verzi), `tenant_005` (un roșu +
un verde), `tenant_017` (un verde). *Restul e gri onest: „n-am ce compara".* Cele **trei
NEVERIFICATE** sunt firme pe care D390 nu se poate calcula (profil incomplet), numite pe ecran cu
cauza.

**Cifra care contează pentru cine continuă: `de_confirmat = 1`.** Constatarea CERTĂ roșie e pe
`tenant_005`, anul 2025: **D101 rd.50 = 12.000 lei, iar cele trei D100 depuse însumează 15.200**.
Amprenta ei: `09441a61b26c5ce555929ad4a890518f`. Poarta confirmării o cere la **orice** depunere pe
firma aia — elementul **8052** (D300 trim 3/2026, `la_senior`, verdict valid) e pus în coadă exact
ca s-o întâlnească.

**NU E O DEPUNERE REALĂ CARE A IEȘIT ROȘU — E UN SCENARIU CONSTRUIT, DECLARAT.** Datele sunt scrise
de mine pe firme de test, pe calea aplicației, ca să se poată apăsa poarta. Regula care cere asta:
`PLAN_LUCRU.md`, regula 3 de conducere a lucrului.

### Suprafața lui, concret — ce chemi și ce primești

```
supervizor.ruleaza_portofoliu(an, luna, firme=None, deschide=None, domeniu=None)
    -> {an, luna, domeniu, firme:[...], rezumat, tipuri_neatribuite}
       firme[i] = {tenant_id, nume, rezultat, constatari, de_confirmat, neverificat}
       rezumat  = {CONSTATARI, FARA_SUBIECT, NEVERIFICAT, firme_in_domeniu,
                   constatari_total, de_confirmat}
supervizor.firme_portofoliu(conn)      -> domeniul, CITIT din bază
supervizor.neconfirmate(...)           -> ce citește poarta de depunere
supervizor.scrie_confirmare(...)       -> jurnalul, cu motiv NOT NULL
```

**`firme`/`deschide` se injectează** — fără ele, căile de eșec n-ar putea fi probate: o probă care
ține o firmă sintetică într-o tranzacție întoarsă **nu o poate vedea** de pe a doua conexiune.
**`domeniu` injectat fără nume RIDICĂ**, deliberat.

Producătorii de constatări orizontale, toți în `core/control_incrucisat.py`, fiecare cu **o singură
ieșire ștampilată**: `orizontal_d390_vs_d300` · `orizontal_d101` · `orizontal_d300_vs_d394` ·
`orizontal_efactura_vs_d394`. *Culegerea se face după **eticheta de tip**, nu după modul — o
constatare fără `tip_constatare` e socotită verticală și sărită.*

### CE LE-AR FACE VII: o depunere prin aplicație. Pașii, măsurați

Toate patru perechile sunt înfometate fiindcă aproape nimic n-a trecut prin coadă. **Nu e o restanță
de cod — e folosire.** Pașii, verificați la sursă pe 01.09:

- **URL**: `https://iconta.eu` (nginx: `server_name 178.105.201.56 iconta.eu www.iconta.eu` →
  `proxy_pass 127.0.0.1:8010`).
- **cont**: `patron@prisma-cont.test`, uid **1968**, rol `admin_firma`, `poate_valida` și
  `poate_depune` adevărate. *`asistent@prisma-cont.test` e **inactiv** și n-are drepturi.*
- **patru-ochi e OPRIT** pe cabinetul 1968 (`{'activ': False, 'posibil': False, 'efectiv': False}`),
  deci **nu există pas separat de aprobare**: cardul „De validat" își schimbă titlul în „De depus",
  iar butonul **„Confirmă depunerea"** înlănțuie `aproba` + `depune`. Dialogul cere indexul SPV,
  **opțional**.
- **proba că a mers** e în bază, nu pe ecran: `public.declaratii_depuse` trebuie să primească un rând
  cu **`randuri` NENUL**. Dacă `randuri` e NULL, depunerea s-a înregistrat dar **nu s-a persistat
  nimic de comparat**.
- **luna din jurnal**: pentru trimestriale e **luna finală a trimestrului** (`_trim * 3`), nu numărul
  trimestrului — `coada_api.marcheaza_depusa`.

### PRIMUL ROȘU AL FIECĂREIA — DAT, ȘI MĂSURAT *(02.09.2026, tura a doua)*

**Lista de mai jos nu mai e o listă de așteptări: fiecare rând s-a întâmplat.** Datele au fost
construite de mine, pe firme de test, **prin lanțul aplicației** (generator → DUK → coadă →
depunere), invalide întâi și valide după — regula 3 din `PLAN_LUCRU.md`.

| comparația | firma · perioada | ROȘU (invalid) | VERDE (valid) |
|---|---|---|---|
| **D101 rd.50 ↔ Σ D100** | `tenant_005` · 2025 | rd.50 = 12.000 vs Σ 15.200 | rectificativă cu rd.50 = 15.200 |
| **D101 rd.48 ↔ cont 691** | `tenant_005` · 2025 | 15.200 declarat vs 0 în 691 | notă validată pe 691 = 15.200 |
| **D390 ↔ D300 depus** | `tenant_004` · 08/2026 | D390 A = 12.000 vs D300 depus 0 | rectificativă D300, R5_1 = 12.000 |
| **D300 rd.12 ↔ D394 lit. C** | `tenant_004` · 08/2026 | D300 0 vs D394 8.000 | rectificativă D300, rd.12 = 8.000 |
| **e-Factura ↔ D394** | `tenant_004` · 08/2026 | 1 din 1 transmisă, nedeclarată | rectificativă D394 o include |

**STAREA LĂSATĂ, deliberat:** patru din cinci sunt **verzi**; singura lăsată **roșie** e
D101 rd.50, fiindcă poarta confirmării are nevoie de un subiect viu ca să poată fi apăsată.

*Ce urmează e textul de dimineață, păstrat fiindcă descrie ce ar face perechile vii din FOLOSIRE,
nu din construcție — și aia încă n-a venit.*

- **D390 ↔ D300 depus** — un D300 depus prin coadă, pe o firmă cu operațiuni intracomunitare, în
  care rândul `R1_1` **nu** se potrivește cu baza recalculată a D390. Azi rândul se derivă automat
  din aceleași facturi, deci roșul vine doar din **derivă**: facturile se schimbă după depunere.
- **D101 rd.50 ↔ Σ D100** — un D101 depus, plus **toate** cele trei trimestre (lunile 3, 6, 9)
  depuse prin aplicație. Dacă lipsește unul, perechea spune gri și numește trimestrul; **nu** acuză.
- **D101 rd.48 ↔ cont 691** — un D101 depus pe o firmă pe regim de profit, cu nota de impozit
  **validată** în contabilitate. Dacă nota e încă în ciornă, perechea tace motivat.
- **D300 ↔ D394 (taxare inversă)** — ambele depuse pe aceeași perioadă, cu rânduri, pe o firmă cu
  achiziții în taxare inversă. Roșul apare când se schimbă ceva **între** cele două depuneri.
- **e-Factura ↔ D394** — o factură cu **recipisă acceptată** (`stare='ok'`, `mediu='prod'`) care nu
  apare printre cele incluse în D394-ul depus al perioadei. **Asta e cea care merită urmărită**:
  laturile sunt independente, deci și verdele ei spune ceva, nu doar roșul.

**Ordinea în care ar deveni vii, dacă cineva depune:** ultima e cea mai ieftină — cere doar o
factură trimisă prin e-Factura și un D394 depus pe aceeași lună. Prima cere o firmă cu IC. Cele două
D101 cer un an încheiat.

### Contractul expunerii D394 (R119) — de citit înainte de a-l atinge

`d394.Rezultat` poartă acum **`facturi_incluse`** (cheia operațiunii → id-uri de facturi) și
**`manuale_fara_factura`**. Amândouă se umplu **din aceleași apeluri** care compun declarația
(`_adauga`, punct unic de trecere) și se curăță la **aceleași** `del op1[k]`.

**Regula, scrisă ca să nu se piardă:** *cine decide ce intră în D394 rămâne generatorul; cine
confruntă doar citește.* O a doua implementare a eligibilității, oriunde, ar produce două motoare
care se despart în tăcere — chiar clasa care dă cifra validă și falsă.

**Cheile lui `op1` sunt tupluri serializate ca JSON** (`coada_api._chei_serializabile`), deci se
citesc înapoi cu `json.loads`, **nu** prin despicare pe separator: a cincea componentă e denumirea
partenerului și poate conține orice caracter ai alege ca separator.

---

## AL TREILEA: UNDE SUNTEM ÎN PLAN, ȘI CE NU SE REDESCHIDE

- `PLAN_LUCRU.md` are **5 etape** (E1–E5). Suntem la **E1 — SETUL COMPLET**. Cei patru pași ai fazei 1
  sunt făcuți din 29.08; **criteriul de terminare al etapei NU e îndeplinit** — lista 3 nu e goală.
- **ORDINEA NU MAI VINE DIN PLANUL DE FAZE.** Din 01.09, Costin conduce pe **temă**. Planul rămâne
  hartă a etapei; nu mai e coada din care se ia următorul lucru.
- **AXA CORPUS-INSTRUMENT ȘI IGIENĂ E ÎNCHISĂ** *(Costin, 01.09)*: *„criteriul aplicat cinstit a scos
  populația 4 și o reparație. Axa nu mai are randament."* **R112, R113, R114 rămân DESCHISE și
  NEREPARATE; #33, #67, #70 rămân NEMĂSURATE.** Restanțele noi din familia asta **se consemnează, nu
  se lucrează**. *Nu redeschide axa fiindcă „mai era puțin".*
- **UMBRA INTERDICȚIEI 77 E ÎNCHISĂ DEFINITIV** (`DECIZII.md`, intrarea a cincisprezecea): nu se
  auditează, nu devine restanță, **nu se mai deschide ca temă**. Cifra ei trăiește numai în blocul
  generat, unde se recalculează la fiecare rulare.
- **Restanțele consemnate-și-nelucrate ale axei oprite** sunt numite în tabelul de restanțe de mai
  jos, cu condiția fiecăreia.
- **Cele PATRU reguli de conducere a lucrului** (`PLAN_LUCRU`, 01–02.09): deciziile care nu mută
  direcția sunt ale mele, nu urcă la arhitect · **o tură care nu schimbă nimic pentru un contabil
  cere justificare SCRISĂ** în `§2` al raportului · **3.** o pereche sau o gardă nouă **se probează
  pe portofoliu**, nu doar în teste, pe date construite de mine — invalide întâi, apoi valide, ca
  scenariu declarat; omului i se cere doar apăsarea pe care numai el o poate face · **4.** poarta
  **scurtă** rulează construcția atinsă și tot ce depinde de ea, **derivat** din import-uri
  (`scripts/perimetru.py`), nu ales de la caz la caz; poarta completă rămâne obligatorie **înainte
  de publicare și înainte de `/clear`**, iar când derivarea nu poate închide perimetrul se rulează
  **tot** și se spune de ce.

---

## AL PATRULEA: CE E ADEVĂRAT DESPRE STAREA CODULUI

- **restanțe deschise: 50** (din care ale etapei E1: **22**), derivat cu `scripts/raport_b.py`.
  **Nu se scrie de mână** — rândul ăsta a fost invalidat o dată.
- **interdicții, din 77**: MĂSURATE **23** · PARȚIAL **16** · NEMĂSURABILE **5** · NEÎNCEPUTE **33**.
- **locuri de verificare**: **221 scrise / 0 goale din 221 (100%)**.
- **decizii care blochează: niciuna.** *Toate cele cinci întrebări deschise către Costin au primit
  răspuns pe 01–02.09.*
- **clusterele topologice**: `core.agenda.urmator_cluster()` → **`(None, 0, 0)`**; secvența e epuizată
  din 04.08.2026 — **nu există „următorul programat"**.
- **cele mai vechi restanțe deschise**: R1, R3, R4, R5, R6, R7 — familia „încrederea în corpus", acum
  **în afara axei de lucru**.

---

## STAREA LA PREDARE

Poartă verde, citită din ieșirea rulării complete de pe arborele care devine commitul următor:
**3959 teste trec** · 11 skip · 14 xfail · ruff OK · verificator **TOTAL 0** ·
rute **424 = ACCEPTAT 383 + GRI 7 + ROSU 0 + EXCLUS 34** · site **200** · four-way se închide la
`post-commit`, care publică pe `origin/main` și pe `backup/lant-<ziua curentă>` și **restartează
necondiționat** procesul viu.

**AL PATRULEA BRAȚ AL FOUR-WAY-ULUI.** Ștampila de RUNNING trăiește **numai în memoria procesului**,
iar endpointul care o citește (`GET /admin/versiune`) cere **superadmin**. Cele două lecturi:
(a) mintezi un token de superadmin — tiparul din `frontend_test/w_auth.py`; (b) **proba gardată**,
fără token: *ora de pornire a procesului > ora commitului*. **Pe 01–02.09 s-a folosit (b) de nouă
ori** — o verificare de rutină nu justifică emiterea unui token de superadmin.

**VERIFICATORUL DE NECONFORMITĂȚI ARE TREI REZULTATE**: `PASS` · `FAIL` · **`NEVERIF [cod]`**. Codul
de ieșire **2** înseamnă „nu s-a putut verifica tot". Stare: `PASS 18 · FAIL 0 · NEVERIF 2`.

**CLICHETELE VII — blocul de mai jos e GENERAT, nu scris.** Gardat de
`core/test_clichete_generate.py`; regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.

<!-- CLICHETE-VII:START (generat de scripts/scan_ramas.py --clichete-md) -->

*Generat din COD. **Nu se scrie cu mâna** — `core/test_clichete_generate.py` recalculează și compară caracter cu caracter. Regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.*

| cod | acum | ce se numără | instrument |
|---|---|---|---|
| **77** | **61** | refuzuri fără temei în module care citează legea | `scripts/scan_refuzuri.datorie()` |
| **77u** | **786** | UMBRA: refuzuri în module care nu citează legea (nedeplafonat) | `scripts/scan_refuzuri.umbra()` |
| **50** | **1221** | aserțiuni ancorate pe text, nu pe structură | `core/scan_garzi_pe_text.pe_fel()` |
| **R80** | **7** | rute despre care detectorul de apelanți nu poate afirma nimic | `scripts/scan_ancore_rute.verdicte()` |

<!-- CLICHETE-VII:STOP -->

**CE A RĂMAS DE FĂCUT se citește rulând `./venv/bin/python scripts/scan_ramas.py`.** *Cifrele NU se
scriu aici.*

**POARTA DUREAZĂ ~21 DE MINUTE** — măsurat pe cele zece rulări de pe 01–02.09: 1223s … 1256s. Suita a
crescut de la 3928 la 3959 de teste în două zile. *E cifra pe care o folosește cine estimează o tură:
o tură cu două commituri costă ~42 de minute doar în porți.*

**PE 01–02.09 POARTA A RESPINS DE ZECE ORI, ȘI NICIO RESPINGERE N-A FOST FALS POZITIV.** Cele mai
multe au cerut **înregistrare**, nu reparație: un asset neversionat, o captură nenumită, o rută în
afara inventarului, o fixtură pe tabel partajat cu an real, un plafon intrat ca valoare fiscală, un
antet de registru rămas pe ziua de ieri după miezul nopții. **Toate au fost gărzi scrise de mine, mai
demult, care nu știau ce vine.**

**Cifrele de aici se copiază din IEȘIREA PORȚII, nu din predarea de dinainte.**
**Cifrele secțiunii „Unde suntem" nu se scriu de mână** — `scripts/raport_b.py`.

**O ORDINE CARE COSTĂ O RULARE, acum mai strictă decât era scrisă:** `versioneaza_assets.py --scrie`
vine după **ULTIMA** editare de JS, nu doar înaintea scanului vizual. *Am rulat-o o dată înainte de a
repara o ghilimea, iar amprenta a rămas a fișierului vechi — poarta a picat pe alt fișier decât cauza.*

---

## CE E ADEVĂRAT ACUM DESPRE RESTANȚE

| | |
|---|---|
| **prag 1** | **niciuna deschisă.** *Două s-au reparat pe 02.09, amândouă găsite construind altceva: textul fals „rândurile IC sunt manual-only", și D394 care nu putea intra în coadă.* |
| **decizii** | **niciuna deschisă.** R115 închisă (tăria), R120 închisă (decizia de a construi). |
| **R121** | singura pereche respinsă rămasă: P300 / RO e-TVA n-are acces programatic. **EXTERNĂ** — cere o cale publicată de ANAF, nu muncă. |
| **R116 · R117 · R118** | deschise, **consemnate și nelucrate** (axa oprită). R116 — cronul numără firmele după succes · R117 — un gard al cărui subiect e o mulțime de nerezolvate se golește când ultimul se rezolvă · R118 — `static/` se servește de pe disc, deci JS-ul e live fără nicio poartă. |
| **R112 · R113 · R114** | deschise, **nereparate prin decizie** (axa oprită). |
| **familia „încrederea în corpus"** | R1, R3, R4, R5, R6, R7, R107 — cele mai vechi, **în afara axei**. |
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
| **„coada are 3 elemente, toate în `la_senior`" · „calea n-a fost folosită niciodată"** | R40, purtată în registru și **citată de mine în raportul din 01.09 fără remăsurare** | **2 elemente, dintre care unul** în `la_senior`. Iar calea **fusese folosită din 24.08.2026**, când Costin depusese un d301 (`coada 2411`, `tenant_006`) — chiar singurul rând cu `randuri` din bază. *Am citat o restanță din registru ca pe un fapt curent. Registrul e sursa a ce s-a măsurat ATUNCI, nu a ce e adevărat ACUM* |
| **„toate patru perechile sunt corecte și calibrate"** | rescrierea completă a predării, 02.09 dimineața, și antetul lui `core/supervizor.py` | **falsă pentru una din cinci.** `D101 rd.50 ↔ Σ D100` era calibrată în amândouă direcțiile și **oarbă**: testele își fabricau `randuri` cu cheia `suma_plata`, pe care generatorul **nu o scria** (trăia doar în formatarea XML-ului). Pe orice depunere făcută prin aplicație perechea aduna **0**. **R125.** *„Calibrat" descria relația dintre test și funcție, nu dintre funcție și aplicație — iar propoziția nu spunea care.* |
| **„R1_1 / R5_1 sunt MANUAL-ONLY (le introduce contabilul la generare)"** | antetul secțiunii F163 din `core/control_incrucisat.py`, din naștere | **fals, și contrazis de funcția de dedesubt**, al cărei mesaj scrie că rândul „se derivă AUTOMAT din facturile cu partener din UE". Măsurat pe `tenant_004`: o achiziție IC de 12.000 lei a produs `R5_1 = 12000` în rectificativă, fără nicio intrare manuală. *A doua instanță în două zile a aceleiași clase — un text fals despre rândurile IC.* |
| **„D394 nu-și expune facturile, deci perechea cere o schimbare mare de generator"** | R119, la deschidere, 02.09 | **schimbarea e mică**, și am aflat-o abia măsurând: toate cele **cinci** căi de acumulare trec printr-un singur `_adauga`, care ținea deja un dicționar paralel curățat la aceleași ștergeri. *„Cere schimbare de generator" era adevărat; „e mare" era o presupunere pe care n-o măsurasem* |

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

### despre supervizor și perechile lui

- **Patru perechi, dar populația e aproape goală.** Din 19 firme, perechile răspund azi covârșitor
  *„n-am ce compara"*. Motivul e măsurat: aproape nimic n-a fost depus **prin aplicație** cu rânduri
  persistate. Cele două excepții sunt depunerile făcute de Costin (d301 pe 24.08, d300 pe 01.09).
- **VERDELE A TREI DIN CELE PATRU E SLAB, și temeiul o spune.** D390↔D300, D300↔D394 și, parțial,
  D101↔D100 compară lucruri derivate din aceleași fapte. **Singura al cărei verde afirmă ceva e
  e-Factura ↔ D394**: stânga e o recipisă de la ANAF, dreapta e ce a declarat generatorul.
- **`verde_slab` e un CÂMP, nu o frază.** Constatarea care are un verde slab o declară ca fapt, iar o
  gardă asertează pe câmp — o gardă pe formulare ar fi păzit textul, nu proprietatea.
- **Nicio constatare nu cere azi confirmare.** Euristicele nu cer niciodată; certele cer doar pe roșu,
  iar roșu nu există încă. `public.supervizor_confirmari` e gol.
- **STRATUL DE EFECT E CABLAT** *(02.09, ultima tură a zilei)*. `supervizor.poarta_confirmarii()` e
  chemată din `POST /coada/{id}/depune`, ÎNAINTE de `marcheaza_depusa`: o constatare **CERTĂ** pe
  firma și perioada care se depune cere o **confirmare scrisă** (cine · când · **peste ce
  constatare**, prin amprentă), iar euristicele nu cer nimic. *Gaura de dinainte — `neconfirmate()`
  fără niciun apelant — a stat trei ture nevăzută, fiindcă `test_module_nelegate` lucrează la nivel
  de MODUL, iar modulul era chemat prin altă funcție.*
- **„Nu blochează niciodată" e citit până la capăt: nici prin AVARIE.** Apelul stă într-un `try` al
  cărui `except` **nu re-ridică** — dacă supervizorul crapă, depunerea trece, cu eșecul logat. Iar
  când chiar sunt constatări neconfirmate, răspunsul **numește calea de trecere în corpul lui**.
  Gardat pe AST, cu mutație probată.
- **Perechea D101 E calibrată acum pe portofoliu** *(02.09, tura a doua)* — patru depuneri D101 și
  trei D100 pe `tenant_005`, toate prin lanțul aplicației. Propoziția de dimineață — *„nu se poate
  calibra pe date reale"* — era adevărată atunci și e falsă acum. **Ce a scos calibrarea aia:
  R125.** *„Reparat pe clasă" și „probat pe instanță" chiar nu sunt același lucru — iar de data asta
  a doua l-a contrazis pe primul.*

### despre ce s-a oprit

- **Cele trei restanțe ale axei oprite nu sunt „aproape gata".** R114 cere o schimbare de verdict
  afișat, cu poartă vizuală. R113 cere extinderea a **două** tipare, cu direcția periculoasă măsurată:
  2 fișiere ar câștiga titluri **false**. R112 cere un act adus.
- **R117 și R118 sunt deschise fiindcă axa e oprită, nu fiindcă sunt mici.** R118 în special: între o
  greșeală de sintaxă într-un `.js` și producție **nu există nicio poartă**.

### despre măsurători

- **Blocul de cifre e derivat din date VII.** Dacă portofoliul se schimbă între generarea blocului și
  sfârșitul porții (~21 min), garda **pică** — și pe drept. **Blocul se regenerează ULTIMUL.**
- **Predarea nu se mai poate scrie fără acces la bază.**
- **`main.py` e cel mai atins fișier din repo**, și e numit de mai multe restanțe deschise.
- **Punctul orb e FIRMA, nu ecranul.** Un scan vede doar stările pe care le produc datele firmei pe
  care rulează.

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

---

## CE CERE POARTA CÂND ADAUGI CEVA NOU — lista pe care am plătit-o de zece ori

**Un lucru nou nu e gata când trec testele lui; e gata când trece gărzile care nu știau că vine.**
Din cele zece respingeri ale porții de pe 01–02.09, **niciuna n-a fost o regresie** — toate au cerut
**înregistrare**. Lista, ca următoarea sesiune să nu le mai plătească pe rând:

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

*Cel mai ieftin drum: rulează gărzile de clichet **înainte** de commit, nu după — o respingere costă
21 de minute, o rulare țintită costă două.*

---

## CE AM ÎNVĂȚAT DESPRE GĂRZI ÎN ULTIMELE DOUĂ ZILE — patru lecții, fiecare cu instanța ei

1. **O gardă care nu poate cădea nu apără nimic.** Prima formă a gărzii care apără „eligibilitatea
   rămâne a generatorului" proba o excludere oprită de un filtru **dinainte** de acumulare — deci
   trecea oricum, chiar dacă cineva scotea curățarea dicționarului paralel. Mutată pe o excludere
   care trece prin `del op1[k]`, abia atunci mutația o face roșie. *Înainte de a te bucura că o
   gardă e verde, întreabă prin ce mutație devine roșie.*

2. **Un răspuns primit poate GOLI o gardă, fără ca nimic să se strice.** Testul care apăra „un tip
   fără tărie nu cere confirmare" parcurgea mulțimea tipurilor neatribuite. În ziua în care Costin a
   atribuit ultima tărie, mulțimea a devenit vidă — iar un `for` pe gol trece. Gardul fusese corect
   toată viața lui. **Măsurat în amândouă direcțiile**: cu mutația care strecoară implicitul, forma
   veche trece, forma nouă cade. *Clasa e consemnată; orice gardă al cărei subiect e o mulțime de
   lucruri nerezolvate se golește când ultimul se rezolvă.*

3. **Un scaner pe text nu deosebește codul de comentariu.** Am reparat o randare greșită, apoi am
   **explicat reparația într-un comentariu care conținea chiar tokenul căutat** — și verificatorul
   s-a aprins din nou, pe explicație. E limita declarată a clasei de gărzi ancorate pe text, de data
   asta întoarsă împotriva mea.

4. **O aserțiune pe formulare păzește fraza, nu proprietatea.** De trei ori în două zile am scris
   gărzi care cereau un cuvânt în mesaj; de fiecare dată clichetul le-a prins, iar rescrierea pe
   **câmp** a fost și o îmbunătățire a datelor: așa au apărut `verde_slab`, `felul_neverificarii`,
   `an`/`luna` pe constatare. *Gardul pe structură cere date mai bune — de-aia merită.*

**Și una despre registre:** o restanță din `CONFORMITATE.md` e sursa a ce s-a măsurat **atunci**, nu
a ce e adevărat **acum**. Am citat R40 într-un raport fără s-o remăsor, iar două dintre cifrele ei
erau stătute de opt zile.

---

## DACĂ CONTINUI DE AICI

1. **NU REDESCHIDE AXA CORPUS-INSTRUMENT** (`DECIZII.md` 33). Restanțele ei se consemnează, nu se
   lucrează — care anume, în tabelul de restanțe. #33, #67, #70 rămân nemăsurate.
2. **UMBRA INTERDICȚIEI 77 E ÎNCHISĂ DEFINITIV** (`DECIZII.md`, intrarea a cincisprezecea). *Nu e
   „nu acum", e niciodată.*
3. **Nicio decizie nu blochează nimic.** Singura restanță care așteaptă din afară e **R121**.
4. **Cifrele de clichet nu se scriu în predare.** Blocul e generat.
5. **Înainte de a alege ce faci: rulează `scripts/scan_ramas.py` și MĂSOARĂ candidații.**
6. **Criteriul de prioritate, dat de Costin:** *ce poate produce o cifră validă și falsă.* A
   funcționat de patru ori în două zile — a scos un defect care ascundea 13 din 16 constatări, un
   text fals afișat contabilului, un D394 care nu putea intra în coadă, și forma parcurgătorului de
   portofoliu.
7. **Cele două reguli ale tăriei sunt în antetul `core/supervizor.py`**, nu doar în restanțele care
   le-au produs. Un tip nou de constatare le aplică sau nu trece de gardă.
8. **Justifică în scris orice tură care nu schimbă nimic pentru un contabil.**
9. **Ce ar face perechile să însemne ceva: DEPUNERI PRIN APLICAȚIE.** Toate patru sunt înfometate.
   *Nu e o restanță de cod — e folosire.*
