Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — **planul de întărire P0–P7: trei pași închiși** (08.09.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-09-08**, cerută expres, înainte de `/clear`.
- **pe commit**: `f3567121`. *Predarea se scrie ÎNAINTE de commitul care o poartă; numele de aici e
  al celui precedent, prin construcție.*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **CE E RESCRIS ȘI CE E PĂSTRAT**: antetul, „unde suntem", starea și restanțele sunt **rescrise**.
  Tabelul cifrelor invalidate, capcanele, operaționalul, „ce cere poarta" și lecțiile sunt
  **păstrate** — documentul își interzice singur să le șteargă.
- **CE E REMĂSURAT**: cele patru clichete generate · blocul cifrelor despre date · inventarul
  gărzilor · numărul restanțelor deschise (`scripts/scan_ramas.py`).

---
## PRIMUL LUCRU DE ȘTIUT: **campania rămâne închisă; se lucrează la ÎNTĂRIRE, după un plan scris**

Etapele 1 și 2 ale campaniei sunt **neatinse**. Din 07.09 se lucrează la `PLAN_HARDENING.md` — opt
pași, P0…P7, fiecare cu *ce trebuie făcut* și *cum se verifică*, la nivelul de detaliu al comenzilor.

| pas | stare | ce a livrat, pe scurt |
|---|---|---|
| **P0** — feedback pe niveluri | **ÎNCHIS** (`8996f486`) | N1/N2/N3/N4 derivate din graful de import; N1 pe `control_fiscal_api` = **27 s** față de ~1.500 s poarta completă |
| **P1** — supervizor | **ÎNCHIS** (`ced26440`) | rezultat persistat, versionat; citire **p95 45 ms** pe 1000 de firme (era ~5 s) |
| **P2** — portofoliu / N+1 | **ÎNCHIS** (`f3567121`) | `control-fiscal` la 1000 de firme: **278.882 interogări · 70,8 s → 1 · 17 ms** |
| **P3** — SQL + index | **URMĂTORUL** | nedeschis |
| P4…P7 | nedeschise | v. `PLAN_HARDENING.md` |

**Tiparul comun al lui P1 și P2, și e de reținut înainte de P3:** ce era calculat în cerere se
persistă ca **model de citire** în `public`, invalidat de **triggere** pe tabelele-sursă, cu
prospețimea **derivată** din compararea a două versiuni — niciodată stocată. Interdicția, la
amândouă: *o valoare veche nu se arată ca fiind curentă; „în recalculare" declarat e acceptabil.*

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

- **restanțe deschise: 51**, derivat cu `scripts/scan_ramas.py` — **nu se scrie de mână**.
- **interdicții, din 77**: MĂSURATE **23** · PARȚIAL **16** · NEMĂSURABILE **5** · NEÎNCEPUTE **33**.
- **locuri de verificare**: **221 scrise / 0 goale din 221 (100%)**.
- **decizii care blochează: niciuna.**

---
## STAREA LA PREDARE

**4190 teste trec** *(ieșirea porții care a produs `f3567121`)* · 11 skip · 14 xfail · ruff OK ·
verificator **TOTAL 0** · four-way se închide la `post-commit`, care publică pe `origin/main`,
**pe `public/main`**, pe `backup/lant-<zi>`, publică statica din HEAD, restartează necondiționat, și
**verifică singur cele patru brațe** la capăt (pasul 4, P0).

**Cifrele de aici se copiază din IEȘIREA PORȚII, nu din predarea de dinainte.**

**CLICHETELE VII — blocul de mai jos e GENERAT.**

<!-- CLICHETE-VII:START (generat de scripts/scan_ramas.py --clichete-md) -->

*Generat din COD. **Nu se scrie cu mâna** — `core/test_clichete_generate.py` recalculează și compară caracter cu caracter. Regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.*

| cod | acum | ce se numără | instrument |
|---|---|---|---|
| **77** | **62** | refuzuri fără temei în module care citează legea | `scripts/scan_refuzuri.datorie()` |
| **77u** | **876** | UMBRA: refuzuri în module care nu citează legea (nedeplafonat) | `scripts/scan_refuzuri.umbra()` |
| **50** | **1222** | aserțiuni ancorate pe text, nu pe structură | `core/scan_garzi_pe_text.pe_fel()` |
| **R80** | **7** | rute despre care detectorul de apelanți nu poate afirma nimic | `scripts/scan_ancore_rute.verdicte()` |

<!-- CLICHETE-VII:STOP -->

**POARTA DUREAZĂ ~26 DE MINUTE** — măsurat pe 06–08.09: **1.474–1.595 s**, pe 14 rulări.

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

**Și una despre registre:** o restanță din `CONFORMITATE.md` e sursa a ce s-a măsurat **atunci**, nu
a ce e adevărat **acum**.

---
## DACĂ CONTINUI DE AICI

1. **NU DESCHIDE NIMIC.** Comanda de capăt de etapă, verbatim (06.09.2026): *„Etapa 2 e închisă.
   Nu deschide nimic altceva — nici restanțele, nici backlogul A3, nici cele opt căi rămase din
   clasa R164."* Cele **50** de restanțe deschise **nu sunt o coadă de sarcini**; `PLAN_LUCRU.md`
   → „⬛ STAREA, DUPĂ R118".

   **CE E ÎNCHIS, ca să nu se redeschidă din reflex:**

   | | |
   |---|---|
   | **etapa 1** — date invalide | 364/364, închisă 05.09.2026 |
   | **etapa 2** — date valide, până în declarație | **toate cele nouă**, închisă 06.09.2026, 0 nepotriviri pe cele cinci loturi |
   | **R151** — ultima restanță deblocată de decizie | răspuns primit 05.09, construită 06.09 |
   | **restanțe deschise** | **50** *(se derivă cu `scripts/raport_b.py`, nu se crede din proza asta)* |

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
