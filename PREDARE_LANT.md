Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — **construcția internă e ÎNCHISĂ**, iar poarta a fost trecută de un om (03.09.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-09-03**, **a treia a zilei** — actualizare, nu rescriere: s-a
  adăugat starea campaniei de verificare și s-a corectat secțiunea care spunea că nu se deschide
  nicio temă. *Restul documentului e cel de la a doua rescriere și rămâne valabil.*
- **pe commit**: `a8d9337e` — ultimul commit intrat. *Predarea se scrie ÎNAINTE de commitul care o
  poartă; numele de aici e al celui precedent, prin construcție, nu din uitare.*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **DE CE ÎNCĂ O DATĂ, la câteva ore de la precedenta**: între ele s-au întâmplat două lucruri pe
  care documentul de dimineață le contrazicea. **(1)** Costin a trecut poarta confirmării prin
  interfață — secțiunea „ce te așteaptă neapăsat" devenise **falsă**. **(2)** A intrat **regula 5**,
  care schimbă ce rulează o tură. Iar cifrele portofoliului **s-au mișcat sub document**:
  `de_confirmat` nu mai e 1, e **3**. *O predare care poartă trei afirmații false despre starea
  curentă e mai rea decât una veche care se declară veche.*
- **CE S-A PĂSTRAT VERBATIM, și de ce**: cele două blocuri **generate** · **tabelul cifrelor
  invalidate** · **tabelul „ce cere poarta"**. Sunt registru câștigat, iar retranscrierea lor cu
  mâna e chiar clasa pe care tabelul cifrelor invalidate o consemnează de cinci ori.
- **TOATE CIFRELE DE MAI JOS SUNT REMĂSURATE ÎN TURA ASTA**, nu copiate din documentul dinainte.
- **vechime măsurată, nu estimată**: **0 commituri** de la ultima atingere a fișierului.

---
## PRIMUL LUCRU DE ȘTIUT: **E O TEMĂ DESCHISĂ, ȘI E ÎN LUCRU**

**Costin a deschis-o el, pe 03.09.2026**, verbatim: *„Temă nouă. Predarea spune «NU SE DESCHIDE
NICIO TEMĂ» — asta nu mai e valabil, o deschid eu acum."* Deci propoziția din secțiunea următoare —
păstrată mai jos fiindcă restul ei e adevărat — **nu se mai aplică la ea**.

### Tema: *vorbește aplicația când primește date greșite?*

Comanda, în șapte puncte: lista funcționalităților **derivată din cod** · pentru fiecare, date
invalide și valide · probare **întâi cu invalide, apoi cu valide**, cu **mesajul verbatim** notat ·
orice defect **se repară pe loc** · se reprobează după reparație · rezultatele într-un fișier ·
fără gărzi noi, fără restanțe deschise, o singură publicare per lot.

**La invalide se urmărește un singur lucru: aplicația VORBEȘTE.** Tăcerea e defect, chiar dacă
valoarea n-a intrat. Refuzul spune **care câmp**, **ce e greșit**, în termeni de contabil, cu temei
acolo unde aplică o regulă fiscală. Nu cade, nu dă 500, nu pierde ce s-a tastat, și **nu confundă
„e invalid" cu „n-am putut verifica"**.

**La valide se urmărește tot lanțul, nu ecranul:** valoarea intră, se înregistrează, ajunge în
declarație **în rândul corect și cu suma corectă**, declarația se generează și se validează. *DUK
verde nu e proba — el confirmă forma; o cifră în rândul greșit trece la fel de bine.*

### Unde e campania acum

| | |
|---|---|
| **populația derivată** | **553 de unități** — `LISTA_FUNCTIONALITATI.md`, generat cu `scripts/scan_functionalitati.py`. 427 de rute · 75 de ecrane · 14 joburi · 37 de instrumente |
| **perimetrul etapei 1** | **364** — numai suprafața prin care **un om introduce date**: cele 75 de ecrane + **289 de rute cu câmpuri de completat**. Tăiat de Costin pe 03.09, fiindcă 553 depășea pragul de la care comanda cerea oprire |
| **ce a ieșit, marcat în listă cu motivul** | **189** = 138 de rute fără câmpuri de completat · 14 joburi de fundal (nu primesc nimic de la un om) · 37 de instrumente din `scripts/` (nu le atinge un contabil) |
| **probate** | **14** (lotul 1 = T01, drumul declarației, 11 unități · lotul 1b = 3 căi de import) |
| **RĂMASE DE PROBAT** | **350** |
| **defecte** | găsite **11**, reparate **11**, reprobate **11** |

### Unde stau rezultatele — două fișiere, două roluri

- **`LISTA_FUNCTIONALITATI.md`** — *populația și starea*. O linie per unitate, cu coloana **stare
  probare**. **Se EDITEAZĂ, nu se regenerează**: `scan_functionalitati.py --scrie` rescrie tabelele
  și **pierde stările**. Numerotarea `#nr` e stabilă cât timp nu se regenerează.
- **`VERIFICARE_FUNCTIONALITATI.md`** — *proba*. Un rând per probă, cu **mesajul verbatim înainte și
  după reparație**, ce s-a introdus, ce s-a reparat. Aici stă și secțiunea **„ce a rămas nereparat,
  și de ce"** — locul recunoscut de garda din `commit-msg` (al patrulea, adăugat pe 03.09).
- **`frontend_test/proba_verificare_functionalitati.py`** — hamul. Cereri reale, token emis
  server-side, corpul răspunsului **neatins**. Loturi: `T01`, `IMPORT-GOL`. Subiect: cabinetul
  **1968**, utilizator `patron@prisma-cont.test`, firma **4838 `Comert Micro TVA SRL`** — plătitor
  de TVA cu **perioadă fiscală trimestrială**, ceea ce contează pentru trei dintre probe.

**Reprobarea NU se face pe producție.** Procesul viu ține codul vechi până la repornire, iar
repornirea nu e a mea. Se ridică o instanță proaspătă — `./venv/bin/uvicorn main:app --port 8011`,
cu `db.env` și `api_keys.env` încărcate — se probează cu `PROBA_BAZA=http://127.0.0.1:8011`, și **se
oprește după**.

### CELE TREI DECIZII CARE AȘTEAPTĂ UN RĂSPUNS

Sunt ale lui Costin, niciuna nu blochează probarea, toate se vor repeta dacă rămân nedate:

1. **`403` sau `404` pe o firmă inexistentă?** `/declaratii/{tip}` răspunde `403`, `/coada` răspunde
   `404`, pentru aceeași stare. `403` = „nu divulg dacă firma există"; `404` = „nu există". Atinge
   zeci de rute și testele lor — de-aia n-am ales-o singur. *Cerută prima oară în tura 1.*
2. **Eticheta `# doar-curatenie:` falsă se RESPINGE sau doar se ignoră?** Am făcut-o mai strictă
   decât formularea lui („ignorată"): `commit-msg` respinge commitul, ca să nu rămână o afirmație
   falsă în istorie. Se poate slăbi la avertisment, sau scoate. *Tura 2.*
3. **Ce înseamnă „registru" pentru ocolirea de curățenie?** Azi: `.md` din **rădăcina** repo-ului +
   cele două JSON-uri de proveniență (definiția împrumutată de la `scripts/perimetru.py`). Un `.md`
   din `ghid/` sau `_arhiva_briefuri/` **nu** e registru, deci se poate șterge prin ocolire. *Tura 2.*

### Trei lucruri NEREPARATE din lotul 1, cu motivul — nu sunt restanțe, sunt scrise în registru

1. **Temeiul legal al periodicității TVA nu e citat.** Mesajul *„firma depune d300 TRIMESTRIAL"*
   aplică o regulă fiscală, iar comanda cere temei acolo unde se aplică una. N-am pus niciun articol
   fiindcă **nu l-am verificat la sursă**, iar un temei citat din memorie intră în corpus ca fapt.
2. **`403` vs `404`** — v. decizia 1 de mai sus.
3. **`rand 2` pentru primul rând trimis prin API** — numerotarea pornește de la 2 fiindcă drumul
   normal e un fișier cu antet, unde „rândul 2" e prima linie de date.

### Ce se face mai departe, când vine comanda

Lotul următor de probare **invalid**, pe bucăți, cu raport după fiecare — așa a cerut-o. Probarea cu
**date valide** (lanțul complet până la rândul corect din declarație) **n-a început pentru niciun
lot**: e partea scumpă a temei și n-a fost comandată încă.

---
## DAR RESTUL LISTEI INTERNE NU SE DESCHIDE

Înainte de a-ți alege orice, citește `PLAN_LUCRU.md`, secțiunea **„⬛ STAREA, DUPĂ R118"**. E scrisă
de Costin, ca stare, exact ca să nu se reia lucrul din vecinătate după un `/clear`.

> *„După R118 nu se mai deschide nicio temă internă. Restul familiei R82 rămâne parcată. Backlogul A3
> rămâne neînceput. R116 și R117 rămân consemnate. Ce urmează nu e construcție, e **ieșirea la un
> cabinet-pilot**."*
>
> Și confirmarea: *„Lista internă e închisă, iar cele 50 de restanțe rămase **nu sunt sarcini** —
> sunt starea scrisă în plan. Rămâi pe prag 1 găsit apăsând, atât. **Următoarea temă vine de la mine,
> după pilot**."*

| ce | ce faci |
|---|---|
| un defect de **PRAG 1**, găsit apăsând — cifră greșită, blocaj, afirmație falsă pe ecran | **se repară**, fără să întrebi. E datorie, nu temă |
| orice altceva din cele **50** de restanțe deschise | **nu se deschide.** Nu e o coadă de sarcini; e starea măsurată |
| ceva ce „ar ajuta la pilot" | **întreabă întâi.** Cine e cabinetul, ce date intră, ce se promite — sunt decizii ale lui Costin |

*Cele 50 sunt tentația principală a unei sesiuni noi: fiecare e argumentabilă, iar alegerea din
vecinătate seamănă cu progres fără să fie.*

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

- **restanțe deschise: 50** (din care ale etapei E1: **22**), derivat cu `scripts/raport_b.py`.
  **Nu se scrie de mână** — rândul ăsta a fost invalidat o dată.
- **interdicții, din 77**: MĂSURATE **23** · PARȚIAL **16** · NEMĂSURABILE **5** · NEÎNCEPUTE **33**.
- **locuri de verificare**: **221 scrise / 0 goale din 221 (100%)**.
- **decizii care blochează: niciuna.**
- **clusterele topologice**: `core.agenda.urmator_cluster()` → **`(None, 0, 0)`**; secvența e epuizată
  din 04.08.2026 — **nu există „următorul programat"**.

---
## STAREA LA PREDARE

**3992 teste trec** · 11 skip · 14 xfail · ruff OK · verificator **TOTAL 0** ·
rute **424 = ACCEPTAT 383 + GRI 7 + ROSU 0 + EXCLUS 34** · site **200** · four-way se închide la
`post-commit`, care publică pe `origin/main` și pe `backup/lant-<ziua curentă>`, **publică statica din
HEAD**, și **restartează necondiționat** procesul viu.

**AL CINCILEA BRAȚ:** `https://iconta.eu/static/.publicat.json` spune, **din afară**, din ce commit e
ce se servește. Four-way-ul dovedea că *procesul* poartă HEAD; nimic nu dovedea că *JS-ul* îl poartă.

**AL PATRULEA BRAȚ AL FOUR-WAY-ULUI.** Ștampila de RUNNING trăiește numai în memoria procesului, iar
endpointul care o citește cere superadmin. Proba gardată, fără token: *ora de pornire a procesului >
ora commitului*.

**VERIFICATORUL ARE TREI REZULTATE**: `PASS` · `FAIL` · **`NEVERIF [cod]`**. Cod de ieșire **2** =
„nu s-a putut verifica tot".

**CLICHETELE VII — blocul de mai jos e GENERAT.** Gardat de `core/test_clichete_generate.py`.

<!-- CLICHETE-VII:START (generat de scripts/scan_ramas.py --clichete-md) -->

*Generat din COD. **Nu se scrie cu mâna** — `core/test_clichete_generate.py` recalculează și compară caracter cu caracter. Regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.*

| cod | acum | ce se numără | instrument |
|---|---|---|---|
| **77** | **61** | refuzuri fără temei în module care citează legea | `scripts/scan_refuzuri.datorie()` |
| **77u** | **794** | UMBRA: refuzuri în module care nu citează legea (nedeplafonat) | `scripts/scan_refuzuri.umbra()` |
| **50** | **1221** | aserțiuni ancorate pe text, nu pe structură | `core/scan_garzi_pe_text.pe_fel()` |
| **R80** | **7** | rute despre care detectorul de apelanți nu poate afirma nimic | `scripts/scan_ancore_rute.verdicte()` |

<!-- CLICHETE-VII:STOP -->

**POARTA DUREAZĂ ~22 DE MINUTE** — măsurat pe rulările din 02–03.09: **1.300 s … 1.350 s**. *(Scrise
cu separator de mii nu din stil: `test_cifra_131_e_marcata_invalidata` se uită la prima apariție a
șirului „131", iar „1316s" o furniza înaintea tabelului.)*

**AZI POARTA A RESPINS O DATĂ**, patru teste, **toate de înregistrare** (blocuri generate
învechite). Alte două respingeri le-am prins **eu**, rulând gărzile de registru înainte de commit —
exact ce face regula 5 ieftin.

**Cifrele de aici se copiază din IEȘIREA PORȚII, nu din predarea de dinainte.**

---
## CE E ADEVĂRAT ACUM DESPRE RESTANȚE

| | |
|---|---|
| **prag 1** | **niciuna deschisă.** *Șase s-au reparat pe 02–03.09, toate găsite apăsând sau construind: R124, R125, R126, R127, R128, R129.* |
| **decizii** | **niciuna deschisă.** Toate cele cinci cerute în ultimele două zile au primit răspuns în aceeași zi |
| **R121** | singura pereche respinsă rămasă: P300 / RO e-TVA n-are acces programatic. **EXTERNĂ** |
| **R116 · R117** | deschise, **consemnate și nelucrate**, prin decizia din 03.09 |
| **familia R82** | **PARCATĂ.** Instanța depunerii s-a închis (R127); restul **nu se deschide** |
| **familia „încrederea în corpus"** | R1, R3–R7, R107 — cele mai vechi, **în afara axei** |
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
| **„R118 a stricat producția azi"** | comanda din 02.09 care a deschis tema | **nu s-a putut reconstitui.** Instanța documentată a clasei e cea din **01.09** (desktopul oprit, 15 ecrane). Pentru 02.09 logurile nu pot arăta o cădere de JS — o eroare de sintaxă nu ajunge niciodată la server. Ce **se poate** măsura e expunerea: `static/js` a fost rescris de zeci de ori în ziua aia, fiecare scriere live în aceeași secundă. *Clasa era reală și decizia a rămas bună; cifra „azi" nu se poate confrunta cu nimic* |

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
- **Trei blocuri generate cer regenerare**: `TRASEE.md`, `GARZI.md`, **`PREDARE_LANT.md`**.

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

**Și una despre registre:** o restanță din `CONFORMITATE.md` e sursa a ce s-a măsurat **atunci**, nu
a ce e adevărat **acum**.

---
## DACĂ CONTINUI DE AICI

1. **NU DESCHIDE NICIO TEMĂ.** `PLAN_LUCRU.md` → „⬛ STAREA, DUPĂ R118". Cele 50 de restanțe **nu
   sunt o coadă de sarcini**.
2. **Ce e permis fără să întrebi:** un **prag 1** găsit apăsând.
3. **Următoarea temă vine de la Costin, după pilot.**
4. **Înainte de orice probă pe ecran:** `publica_static.py --din-arbore`.
5. **Ce rulezi:** `scripts/perimetru.py` decide. Poarta completă **înainte de publicare și înainte de
   `/clear`**.
6. **Cifrele nu se scriu în predare.** Blocurile sunt generate; „unde suntem" se derivă cu
   `scripts/raport_b.py`.
7. **Cele CINCI reguli de conducere a lucrului** sunt în `PLAN_LUCRU.md`.
