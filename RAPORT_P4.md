RAPORT — P4, TRANSACTION OWNERSHIP | 09–10.09.2026 | `a05618ce` → `0742e177` (lucrul) → commitul de registru

## 0. CERINTE

1. **Confirmarea celor două alegeri de contract pe care le-am luat singur** *(scrise și în
   `DECIZII.md`)*. Amândouă schimbă comportament observabil, amândouă decurg din reparații, și
   niciuna n-a fost cerută de comandă:
   - **(a)** la `409 CONSTATARI_NECONFIRMATE`, confirmările trimise în chiar cererea aia **nu mai
     rămân scrise** — se retrimit toate odată, cum cere deja mesajul rutei. *Ce blochează dacă
     rămâne nedată:* nimic azi; codul e deja așa, fiindcă alternativa e chiar forma care a produs
     R179. Dacă răspunsul e „nu", reparația lui R179 trebuie refăcută altfel — cu confirmările
     comise separat și un mecanism care le curăță când depunerea nu urmează.
   - **(b)** notificările de scadență trec de la **cel puțin o dată** la **cel mult o dată**: un
     eșec după e-mail lasă pragul `in_curs` și nu se mai încearcă. *Ce blochează:* nimic azi.
     *Detaliul care ajută decizia:* alternativa e riscul opus — un al doilea e-mail către clientul
     firmei, în numele cabinetului, care nu se mai poate lua înapoi.
   - *a câta tură:* prima.
2. **Ce se face cu R183** — `apel_anaf` ține o tranzacție de bază deschisă peste apelul la ANAF și
   peste backoff-ul de `429`. Proprietatea tranzacțională e reparată (R180); ce rămâne e **durata**.
   *Ce blochează:* nimic azi; e neblocantă, ca R178. *Detaliul care ajută decizia:* scoaterea
   apelului din tranzacție e ieftină ca schimbare și scumpă ca risc — atinge **singura** funcție
   prin care trec toate apelurile ANAF. Propunerea mea e s-o închid împreună cu R178, după ce se
   măsoară traficul real. *a câta tură:* prima.

## 1. CE AM PRESUPUS

Patru lucruri, niciunul în comandă:

1. **Criteriile de acceptare sunt despre ce rămâne DUPĂ clasificare, nu despre inventarul brut.**
   Comanda cere `TRANSACTION_OWNERSHIP_GAPS = 0` și `PARTIAL_COMMIT_PATHS = 0`, dar tot ea spune
   *„nu modifica arhitectura doar fiindcă există multe apeluri `commit()`"*. Cele două nu se pot
   împăca la literă: aplicația **are** 24 de căi cu scrieri în mai multe tranzacții, iar unele sunt
   despărțite **deliberat** (cache-ul de curs, rotația tokenului, bătaia de heartbeat). Am citit
   criteriile ca fiind despre **golurile nejustificate**: zero căi critice rămase cu proprietate
   ruptă, zero excluderi fără motiv scris. Cifrele brute sunt și ele în raport, ca să se poată
   verifica citirea asta, nu ca să o înlocuiască.
2. **Pragul de la care o cale cere clasificare** — scrieri în mai multe domenii tranzacționale, SAU
   un commit care taie o operație în două, SAU un efect ireversibil cât timp există scrieri
   necomise. Comanda dă șase semne de **candidatură**; nu spune de la care încolo se cere judecată
   scrisă. Am ales pragul ăsta fiindcă restul semnelor (C1 pe 316 căi) sunt adevărate despre
   aproape orice rută din casă: poarta de acces își deschide propria conexiune de citire.
3. **Criteriul de „critic"** — l-am scris **înainte** de a-l aplica, în antetul lui
   `core/p4_clasificare.py`: evidență greșită sau lipsă · fundătură pentru om · efect ireversibil
   rămas fără perechea din bază — **și** eșecul să nu fie anunțat.
4. **Reparațiile intră în tura asta.** Comanda cere `PARTIAL_STATE_AFTER_FAULT = 0`, ceea ce nu se
   poate obține doar raportând. Am reparat cele șase căi critice care aveau ce repara și am probat
   a șaptea fără s-o schimb.

## 2. CE AM FĂCUT ÎN PLUS / MAI PUȚIN

**ÎN PLUS**

- **Un gard care ține clasificarea vie** (`core/test_tranzactii_clasificate.py`). Comanda cerea
  clasificarea; gardul face ca o cale compusă **nouă**, neclasificată, să cadă poarta. Fără el,
  clasificarea ar fi fost adevărată azi și mută peste trei săptămâni.
- **Șase reparații de cod** (R179–R182), nu doar inventar. V. presupunerea 4.
- **`scripts/p4_artefacte.py`** — artefactele se regenerează dintr-o comandă numită, nu se scriu.

**MAI PUȚIN**

- **Nu am probat cu injecție de defect cele 24 de căi NON_CRITICAL.** Fiecare are motivul scris, dar
  un motiv scris nu e o probă. Ce le apără e clasificarea + gardul care o ține la zi, nu o măsurătoare.
- **Nu am măsurat durata tranzacțiilor** deschise peste apeluri externe (R183). Am derivat **forma**
  din cod; cifra ar cere trafic real, și aparține lui R178.
- **Injecția e în Python, nu în proces.** N-am oprit PostgreSQL între `INSERT` și `COMMIT`; efectul e
  același (tranzacția nu se comite), dar nu l-am probat pe calea aia. Scris și în antetul probelor.

## 3. CE AM ACTUALIZAT

| registru | ce s-a scris |
|---|---|
| `CONFORMITATE.md` | **cinci restanțe noi**: R179 (confirmare ↔ depunere), R180 (rotația tokenului SPV), R181 (e-mail ↔ rândul care-l oprește), R182 (cont ↔ dovada acordului / cheia clientului), R183 (tranzacție deschisă peste apelul ANAF — DESCHISĂ, neblocantă). Primele patru sunt reparate; rămân `DESCHISĂ` până la commitul de registru, fiindcă `REZOLVATĂ` cere `rezolvată pe commit` și hash-ul lucrului nu există înaintea lucrului |
| `DECIZII.md` | cele două alegeri de contract din secțiunea 0, cu varianta respinsă numită |
| `PLAN_HARDENING.md` | starea → **P4 ÎNCHIS · P5 URMĂTORUL**; sub P4, ce a livrat, cu cifrele |
| `TESTE.md` | cele trei straturi ale lui P4, cu calibrarea și cu cele patru greșeli ale instrumentului prinse măsurând |
| `GARZI.md` | blocul generat, regenerat (`scan_garzi_inventar.py --md`) |
| `PREDARE_LANT.md` | antetul, tabelul P0–P7, „unde suntem"; blocurile generate regenerate ULTIMELE |
| `ISTORIC.md` | **nimic de actualizat, fiindcă** ziua nu s-a încheiat cu o lecție de proces nouă — ce s-a învățat despre instrument e în `TESTE.md`, iar ce s-a învățat despre cod e în restanțe |
| `PLAN_LUCRU.md` | **nimic de actualizat, fiindcă** regulile de conducere a lucrului n-au fost atinse: P4 s-a executat în cadrul lor |
| `PLAN_INVESTIGATII.md` | **nimic de actualizat, fiindcă** e registrul fazelor campaniei, iar campania rămâne închisă |
| `PLAN_ARHITECTURA.md` | **nimic de actualizat, fiindcă** P4 nu a schimbat niciun principiu — a făcut o proprietate deja cerută (P4 din plan: *„Documentul emis e fapt"*, și *„Două scrieri simultane nu se pierd tăcut"*) verificabilă mecanic |
| `METODA_VERIFICARE.md` | **nimic de actualizat, fiindcă** metoda folosită e cea scrisă: calibrare în ambele direcții (§22), aserțiuni pe structură (§23), instrument înainte de cifră. N-am descoperit o formă nouă de verificare, am aplicat-o pe o axă nouă |
| `DESIGN_SYSTEM.md` | **nimic de actualizat, fiindcă** nu s-a atins niciun ecran |
| `INSTRUMENTE_ROADMAP.md` | **nimic de actualizat, fiindcă** cele 11 instrumente sunt registrul campaniei de gărzi, nu al planului de întărire; P4 nu e unul dintre ele |
| `MODEL_AUDIT_TENANT.md` | **nimic de actualizat, fiindcă** fațetele F1–F9 privesc auditul unui tenant, iar P4 e despre proprietatea tranzacției pe toate căile |
| `ISTORIC_TENANTI.md` | **nimic de actualizat, fiindcă** niciun tenant real n-a fost atins; probele își fac și își șterg firma lor (`ztest_p4`) |
| `anaf_surse/INDEX.json`, `PROVENIENTA.json` | **nimic de actualizat, fiindcă** n-a intrat niciun act normativ în corpus |

## 4. ÎNȚELEGEREA

Am înțeles că nu se cere o refactorizare, ci o **măsurătoare urmată de judecată**: să derive din cod
— nu din memorie — care căi de execuție fac o singură operație logică sprijinindu-se pe mai multe
tranzacții sau amestecând scrieri cu efecte pe care `rollback` nu le desface; să clasific fiecare
candidat, cu justificare scrisă pentru **fiecare** excludere; și să dovedesc, prin defecte injectate
la frontiere, că ce am numit critic nu lasă stare parțială. Explicit: *nu* am voie să mut arhitectura
doar fiindcă există multe `commit()`, *nu* redeschid P2 sau P3, *nu* ating advisory lock-ul sau
modelul de citire.

**Ce a ieșit altfel decât credeam la început, și se scrie fiindcă diferă:** credeam că întrebarea e
„câte `commit()` sunt" (171 în producție). Nu e. Întrebarea care se poate pune mecanic e **peste câte
tranzacții sunt împrăștiate scrierile unei operații** — și abia formularea asta a scos defectele.
Primele două forme ale instrumentului, care numărau frontiere, dădeau 334 și 348 de „candidați" din
care nu se putea alege nimic.

## 5. RĂSPUNS LA COMANDĂ

**1. „Limitele tranzacționale trebuie definite de use-case. Nu modifica arhitectura doar fiindcă
există multe apeluri `commit()`."**

Respectat, și verificabil. Apelurile `.commit()` din producție (`main.py` + `core/*.py`, fără teste),
numărate cu `ast` — deci **apeluri**, nu potriviri de text: **170 înainte, 170 acum**. Reparațiile au
scos două și au adăugat două, iar asta e chiar forma lor:

| fișier | înainte | acum | de ce |
|---|---|---|---|
| `main.py` | 68 | 67 | unificarea rutei de depunere |
| `core/alerta_acces.py` | 1 | 0 | rezervarea de dedup și-a luat tranzacția ei |
| `core/notificari_scadenta.py` | 0 | 0 | cele trei scrieri noi folosesc `with db.get_conn(...)`, care comite singur |
| `core/spv_conector.py` | 0 | **2** | `_roteste_si_comite` — commitul e chiar reparația |

**Restul de 168 sunt neatinse.** Reparațiile sunt de **proprietate**, nu de formă: în fiecare caz
limita a trecut la actul care o deține. *Numărul total neschimbat e cel mai bun rezumat al regulii
din comandă: nu s-a atins arhitectura fiindcă existau multe `commit()`; s-au mutat patru, acolo unde
proprietatea o cerea.*

*Cifra e numărată cu `ast` fiindcă `grep '\.commit()'` dă **171** — cu unu mai mult, iar diferența e
text: `.commit()` apare și în proza unui docstring. Aceeași clasă ca „un scan pe forma BRUTĂ a datelor
supra-numără" din capcanele casei, prinsă aici pe propria mea cifră.*

**2. „Identificarea operațiilor compuse critice NU se construiește din memorie. Se derivă mecanic din
cod, apoi se revizuiește."**

`scripts/scan_tranzactii.py` — parsează `main.py` + `core/*.py` cu `ast` și construiește, pentru
fiecare punct de intrare, **arborele de domenii tranzacționale** al căii: fiecare
`with db.get_conn(...)` deschide un domeniu; un eveniment aparține domeniului care îl cuprinde; un
eveniment necuprins urcă la apelant — exact cum o funcție care primește `conn` scrie în tranzacția
apelantului. Apelurile se expandează pe lanț, cu rezolvare în trei trepte (modul de import → fișier
gazdă → toate omonimele, marcate).

**Ce n-am scris în nicio listă, deliberat:** efectele „de proiect". `trimite_email`, `spv_*`,
`alerteaza` nu apar nicăieri în instrument — ies din expandare, fiindcă ajung, pe lanț, la primitive
reale (`requests`, `smtplib`, `subprocess`, `open(...,"w")`). Lista scrisă de mână conține **numai
primitive**.

**Revizuirea** e pasul B, în `core/p4_clasificare.py`, și e cea care a schimbat cifrele: din 32 de
căi peste prag, 7 sunt critice, 24 nu, 1 e fals pozitiv — iar cu cele două ieșite din inventar
după reparație și calea internă, clasificarea are 35 de intrări.

**3. „Detectorul inventariază căi de execuție cu oricare din: [C1…C6]"**

Toate șase sunt implementate și numite în cod cu chiar formularea comenzii. La rularea de referință:

| semn | ce numără | căi |
|---|---|---|
| **C1** | mai multe frontiere de tranzacție în aceeași operație | 316 |
| **C2** | scrieri către două sau mai multe surse/tabele/scheme | 62 |
| **C3** | scriere + efect extern | 47 |
| **C4** | scriere în sursă + model de citire | 0 |
| **C5** | mai multe domenii tranzacționale **care scriu** | 24 |
| **C6** | scriere A → frontieră sau efect → scriere B | 31 |

**C4 = 0, și e un rezultat, nu o lipsă:** invalidarea modelului de citire se face prin **triggere pe
tabelele-sursă** (P2), deci nicio cale de aplicație nu scrie în sursă și în model în aceeași
operație. Comanda spune să nu ating read-modelul; nu l-am atins, și cifra arată de ce nici nu era
nevoie.

**4. „A. Scanare mecanică, inventar brut: callchain, `file:line`, frontierele de tranzacție,
scrierile/efectele identificate, motivul candidaturii."**

`masuratori/p4/inventar_brut.txt` (250 KB) și `.json` (543 KB). Fiecare candidat poartă: punctul de
intrare (metodă + cale, sau modulul de fundal), handlerul și fișierul lui, poarta de autorizare,
semnele aprinse cu motivul fiecăruia, apoi **fiecare domeniu tranzacțional** cu locul deschiderii și
lanțul de apel până acolo, iar în el fiecare scriere (verb, sursă, tabel), fiecare efect extern și
fiecare frontieră, cu `fisier:linie`, ramura (`normal` / `eroare` / `finally` / `bucla:<loc>`) și
lanțul `a -> b -> c`.

**510** puncte de intrare parcurse · **332** candidați · **0** căi trunchiate de limita de adâncime.

**5. „B. Clasifică fiecare candidat: CRITICAL_COMPOSITE / NON_CRITICAL_COMPOSITE / FALSE_POSITIVE."**

`core/p4_clasificare.py`, **35** de intrări: cele **32** de căi peste prag, plus **două** ieșite din
inventar după reparație (depunerea și accesul de client — rândul lor rămâne ca urmă), plus **una
internă** (`spv_conector.reimprospateaza_token`), care nu e punct de intrare dar e cauza a șase căi.

- **CRITICAL_COMPOSITE — 7**: depunerea declarației · înregistrarea cabinetului · accesul de client ·
  rotația tokenului SPV · notificarea de scadență · alerta de acces anormal · emiterea de factură;
- **NON_CRITICAL_COMPOSITE — 27**;
- **FALSE_POSITIVE — 1**: `POST /tenants/{id}/firma-profil/date` — două ramuri exclusive ale unui
  `if` aplatizate de scaner în „commit, apoi scriere". Falsul pozitiv **numește oarbirea** din
  antetul instrumentului care l-a produs; un gard cere asta pentru fiecare.

Tabelul complet, cu efectele compuse ale fiecărei căi și motivul fiecărei clasificări, e în
`masuratori/p4/clasificare.txt` (generat) și în chiar fișierul de clasificare (sursa).

**6. „C. Orice excludere din CRITICAL_COMPOSITE cere justificare explicită scrisă în artefact."**

Toate cele 28 de excluderi au justificare, iar cerința nu stă pe cuvântul meu:
`core/test_tranzactii_clasificate.py::test_fiecare_excludere_are_motiv_scris` verifică **conținutul**
(prag de lungime), nu prezența câmpului, iar `test_falsii_pozitivi_numesc_oarbirea_care_i_a_produs`
cere ca un fals pozitiv să spună **prin ce** s-a înșelat instrumentul.

Deosebirea care taie jumătate din listă, scrisă o dată și aplicată per loc: **interogare ≠ efect.**
`requests.post` la validatorul de CUI al ANAF și `requests.post` care încarcă o factură în SPV arată
identic pentru un scaner; primul nu lasă nimic la celălalt capăt, al doilea da. Instrumentul nu poate
face deosebirea — de-aia clasificarea nu se poate genera.

**7. „D. Pentru fiecare CRITICAL_COMPOSITE: fault injection la fiecare frontieră relevantă între
efecte … verifică starea persistentă după fiecare eșec."**

`core/test_p4_fault_injection.py` — 7 probe, una per cale critică, pe **firmă și cabinet reale, cu
commituri reale** (altfel n-ar exista ce observa), curățate la final.

| cale critică | frontiera la care s-a injectat defectul | ce s-ar fi întâmplat fără reparație |
|---|---|---|
| `POST /coada/{id}/depune` | între confirmare și marcarea depunerii; **și** la refuzul marcării | confirmare scrisă peste o depunere care nu s-a făcut; element rămas `aprobata`, din care nu se mai poate respinge |
| `POST /auth/register` | între cont și dovada acordului | cont fără dovada consimțământului, tăcut |
| `POST /tenants/{id}/client-acces` | între cont și tokenul de activare | utilizator care nu poate intra niciodată |
| `spv_conector.reimprospateaza_token` | după rotația la ANAF, înainte de commit | perechea rotită pierdută; principal deconectat |
| `notificari_scadenta` | după e-mail, înainte de scrierea rezultatului | al doilea e-mail la clientul firmei, a doua zi |
| `alerta_acces` | între rezervarea de dedup și alerta plecată | alerta repetată la fiecare 15 minute |
| `POST /tenants/{id}/facturi/emite` | înainte de commitul final | număr consumat fără factura lui |

**Starea se compară pe AMPRENTĂ, nu pe numărătoare** — `md5` per rând, `sha256` peste rândurile
ordonate. Motivul e măsurat, nu teoretic: sonda care număra rânduri a fost oarbă la modificări o dată
(**R137**), a redenumit o firmă în două tabele și a raportat „nicio schimbare de stare".

**Fiecare probă are două direcții.** Fără calea fără defect, o probă care asertează „nu s-a scris
nimic" ar trece și pe un cod care nu scrie niciodată nimic.

**O a doua frontieră a ieșit reparând-o pe prima**, și se scrie fiindcă e chiar felul în care
lucrează metoda: pe ruta de depunere, `if not r["ok"]: raise` stătea **după** `with`, deci tranzacția
se închidea normal și **comitea aprobarea** scrisă cu o linie mai sus. Un refuz al marcării lăsa
elementul `aprobata` fără să fie depus — forma pe care R128 o reparase venind din client. *Ordinea
celor două scrieri era corectă; ce lipsea era ca refuzul să fie înăuntrul limitei lor.*

**ȘI PROBA PROBELOR:** le-am rulat pe codul de **dinaintea** reparațiilor, restaurat cu `git stash`
pentru rute și conector, și cu o mutație scrisă pentru cele două lucrătoare de fundal.
**Șase din șapte au fost roșii.** A șaptea — emiterea de factură — trece în amândouă, fiindcă
probează o proprietate care **exista deja**; scrie asta în chiar clasificarea ei, la câmpul
`reparatie`: *„NIMIC DE REPARAT — și tocmai de-asta are probă."*

**8. „Analizează separat efectele care nu pot fi anulate prin rollback PostgreSQL … ordinea corectă e
ca efectul ireversibil să vină ultimul, după ce tranzacția DB a reușit sigur."**

Analiză separată, cu artefact propriu: `masuratori/p4/efecte_ireversibile.txt`, derivat mecanic —
**8** locuri în care un apel extern se face cât timp există scrieri necomise. Fiecare are verdict
scris în `EFECTE_EXTERNE`, iar un loc nou, nejudecat, **cade poarta**.

- **4 sunt INTEROGĂRI** (validarea CUI la ANAF, XML-ul BNR, pagina de noutăți ANAF, comenzile
  WooCommerce): nu lasă nimic la celălalt capăt, deci `rollback` n-are ce desface acolo. Ce rămâne e
  **durata**, care e R183.
- **4 sunt EFECTE**, și aici e reparația:
  - **rotația tokenului la ANAF** — cazul în care regula comenzii nu se poate aplica literal: efectul
    ireversibil **nu poate veni ultimul**, fiindcă e chiar sursa valorii de scris. Forma corectă e
    oglinda ei: **scrierea lui se comite prima** (`_roteste_si_comite`). R180.

    **Prima formă a reparației a fost greșită, și e a doua lecție a turei.** Deschidea o *a doua
    conexiune* pentru scriere. Se **blochează**: tranzacția apelantului poate ține rândul, iar a doua
    așteaptă la infinit un commit care nu vine. Poarta a prins-o — suita a atârnat la 80% și a rămas
    acolo până am oprit-o —, iar regula era deja scrisă în casă, la operațional: *o probă care ține o
    tranzacție deschisă nu poate deschide o a doua conexiune pe același rând*. Forma bună e chiar
    cea cerută de P4: **limita aparține use-case-ului**. `apel_anaf` deschide conexiunea, deci
    `apel_anaf` hotărăște când se comite — imediat după rotație;
  - **e-mailul către un om** — ordinea corectă e cea din tiparul care exista deja în casă
    (`efactura_send.trimite`, `etransport_send.trimite`): rândul care face mesajul inutil de retrimis
    se scrie **și se comite înaintea lui**. Aplicat la notificarea de scadență și la alerta de acces
    (R181);
  - **alerta internă de eroare** — rămâne unde e, și se scrie de ce: o alertă amânată până după commit
    s-ar pierde exact când actul cade.

**Un fals pozitiv al primei forme a instrumentului, păstrat fiindcă e instructiv:**
`gdpr_sterge.executa` comite **întâi** și abia apoi șterge fișierele de pe disc, cu motivul scris
lângă cod. Metrica mea, oarbă la commitul explicit, a raportat **ordinea corectă ca defect**. Am
reparat metrica, nu codul.

**9. „Nu redeschide P2 sau P3. Nu atinge advisory lock-ul sau read-modelul."**

Respectat, și verificabil în diff: `core/firma_rezumat.py` nu e atins; `pg_advisory_lock` nu apare în
nicio linie modificată; niciun trigger nu s-a schimbat. `core/firma_rezumat.py::main` **apare** în
inventar cu 3 domenii care scriu și e clasificat NON_CRITICAL — cu motivul că modelul e derivat prin
construcție și că o firmă recalculată parțial rămâne `invalidat` și se reia.

**10. Criteriile de acceptare**

| criteriu | valoare | cum se verifică |
|---|---|---|
| `CRITICAL_COMPOSITES_WITH_FAULT_TESTS = CRITICAL_COMPOSITES` | **7 = 7** | `test_fiecare_cale_critica_are_proba_de_injectie` — numele probei se caută cu `ast` în fișierul de injecție, nu ca text |
| `UNTESTED_CRITICAL_COMPOSITES = 0` | **0** | aceeași probă: mulțimea diferență |
| `UNEXPLAINED_EXCLUSIONS = 0` | **0** din 28 | `test_fiecare_excludere_are_motiv_scris`, pe conținut |
| `TRANSACTION_OWNERSHIP_GAPS = 0` | **0 nejustificate** (24 în inventarul brut, toate clasificate) | `test_nicio_cale_ramane_neclasificata` + clasificarea |
| `PARTIAL_COMMIT_PATHS = 0` | **0 nejustificate** (6 în inventarul brut) | idem; cele 6 sunt DDL idempotent (2), ramuri exclusive aplatizate (3) și două acte independente (1) |
| `PARTIAL_STATE_AFTER_FAULT = 0` | **0** | cele 7 probe de injecție, pe amprentă |
| `P4_CRITICAL_OPERATION_INVENTORY = MECHANICALLY_DERIVED` | **da** | `scripts/scan_tranzactii.py`, cu 22 de probe de calibrare în ambele direcții |
| `P4_FAULT_INJECTION_COVERAGE = COMPLETE` | **da**, pe mulțimea CRITICAL | v. rândul întâi; ce **nu** acoperă e scris în antetul probelor |

**Două dintre ele sunt citite, nu bifate**, și o spun aici ca să se poată contrazice:
`TRANSACTION_OWNERSHIP_GAPS` și `PARTIAL_COMMIT_PATHS` **nu sunt zero pe inventarul brut**, și n-ar
putea fi fără să contrazică prima frază a comenzii. Zero e numărul celor **nejustificate**. Cifrele
brute sunt mai sus, în tabelul semnelor, ca să se vadă exact ce am exclus și de ce.

**11. „Raport final: `RAPORT_P4.md`, cu inventarul complet și clasificarea fiecărui candidat."**

Fișierul ăsta, plus artefactele pe care le numește. Inventarul complet e prea mare pentru un raport
(250 KB de text), deci e în `masuratori/p4/inventar_brut.txt`, iar clasificarea fiecărui candidat în
`masuratori/p4/clasificare.txt` — amândouă **generate** cu `./venv/bin/python -m scripts.p4_artefacte`,
amândouă în ZIP.

**12. „Reguli de raportare ca de obicei: structura `SABLON_RAPORT.md`, lista operațiunilor peste 1
minut cu durată exactă, ZIP de livrare la final cu calea exactă, verificată de tine cu `unzip -l`."**

Structura: cele opt secțiuni, în ordinea 0→7.

**O cifră pe care am corectat-o înainte să intre în istorie, și se scrie fiindcă e chiar clasa pe
care casa o urmărește:** prima formă a mesajului de commit și a lui `PLAN_HARDENING.md` scria
*„24 NON_CRITICAL"*. Real: **27**. Cauza — am purtat cifra **24** de la o altă măsurătoare din
aceeași tură (căile cu scrieri în mai multe domenii), fără s-o recitesc din generator. Prinsă
confruntând raportul cu ieșirea lui `scripts/p4_artefacte.py`, cu poarta deja pornită; am oprit
rularea și am corectat-o, fiindcă o cifră greșită într-un mesaj de commit rămâne acolo.

**A doua cifră corectată, și tot înainte de a ajunge la tine.** O formă mai veche a paragrafului de
mai sus scria **«170 înainte, 168 acum»** și *«n-au adăugat niciunul»*. Era adevărat când l-am scris
— și a devenit fals patru ore mai târziu, când prima formă a reparației lui R180 s-a dovedit greșită
și a fost rescrisă: forma bună **adaugă două** `commit()` în `spv_conector`, fiindcă acolo commitul
**este** reparația. Prinsă confruntând raportul cu ieșirea instrumentului la împachetare. *O cifră
scrisă înaintea ultimei schimbări de cod nu e greșită din neatenție: e greșită fiindcă a fost scrisă
prea devreme, iar singurul remediu e s-o reciteşti din instrument la capăt.*

**Operațiuni peste 1 minut, cu durata exactă:**

| operațiune | durată |
|---|---|
| gărzile de registru (`test_conformitate` + 4), prima rulare | **131,57 s** |
| poarta completă, rularea care a trecut (`0742e177`) | **1.590,76 s** (26 min 31 s) |
| poarta completă, rulările RESPINSE de dinaintea ei | **1.600,59 s** · **1.601,39 s** · plus două opriri făcute de mine (v. mai jos) |

Tot ce a durat sub un minut nu e în tabel: scanerul rulează în **1,8 s** pe tot repo-ul, probele de
injecție în **14,2 s**, gardul de clasificare în **1,9 s**.

ZIP-ul: calea exactă și ieșirea `unzip -l` sunt la secțiunea 7.

## 6. UNDE SUNTEM

*Derivat din `CONFORMITATE.md` cu `scripts/raport_b.py` — nu scris de mână.*

- **etapa**: E1 — SETUL COMPLET (faza 1 din `PLAN_INVESTIGATII.md`)
- **pasul curent**: **lista 5 COMPLETĂ**. Pe lista 3, premisa ei a căzut: «datele există, lipsește documentul» s-a dovedit falsă. Rândurile rămase nu sunt transport până nu se dovedesc. *(Cifrele se derivă — vezi `scripts/raport_b.py`.)*
- **locuri de verificare**: **221 scrise / 0 goale** din 221 (100%)
- **criteriul de terminare**: există lista artefactelor cerute de lege — din lege, cu temei — pe **regimurile reale** (nu pe trei alese arbitrar), iar fiecare artefact e clasificat în una din cele cinci liste ale verdictului 1d. Aplicația e gata pe acest criteriu când listele 3, 4 și 5 sunt goale pe fiecare regim; lista 2 poate avea conținut, fiindcă măsoară ce n-a completat contabilul, nu ce n-a făcut aplicația.
- **ce mai lipsește**: faza 1 nu mai are **pași** — 1a, 1b, 1c și 1d sunt făcute —, dar **criteriul ei de terminare nu e îndeplinit**: lista 3 nu e goală. *(Câte, și care, se derivă din corpul registrului — nu se scriu aici. Câmpul ăsta a purtat cifre scrise de mână și au îmbătrânit: spunea că lista 5 mai are o poziție după ce se golise, și numea lista 3 cu un număr de acum o săptămână.)* Ce blochează cel mai mult rămâne **încrederea în corpusul pe care stă tot 1a** — vezi restanțele de sursă din corpul registrului.
- **interdicții, din 77**: MĂSURATE 23 · PARȚIAL 16 · NEMĂSURABILE 5 · NEÎNCEPUTE 33
  - ⚠ **Transferul retrospectiv 3a e FĂCUT (23.08.2026)**, deci avertismentul de dinainte nu se mai aplică în bloc: din cele douăsprezece, nouă au trecut (una MĂSURATĂ, opt PARȚIAL). Rămân **trei** care scriu NEÎNCEPUTĂ deși §3a le dădea ca măsurate — **7, 8, 12** — și rămân **prin regulă, nu din uitare**: pentru ele nu există cifră pe domeniu, ci proză despre instanțe, iar *ce nu se reconstituie onest rămâne NEÎNCEPUTĂ*.
- **cel mai vechi commit din registru**: `ffbcb745` (2026-08-22), de la secțiunea #2
- **decizii care blochează**: **niciuna.** *(Stocul istoric nu mai blochează: s-a executat pe 29.08, după ce Costin a spus că nu există clienți reali — starea restanței se citește din registru, nu de aici.)* *(Ultima — ce face aplicația cu o factură EMISĂ care intră prin import — a primit răspuns pe 29.08.2026, varianta (iii), și e construită; starea restanței se citește din registru, nu de aici.)* *(A doua decizie care bloca — TVA la încasare pe factura primită — a primit răspuns pe 29.08.2026, varianta (ii), și e construită; restanța ei e închisă, iar starea se citește din registru, nu de aici.)*
- **restanțe DESCHISE: 54** (din care ale etapei E1: **25**)
  - **SURSĂ**: R1 — Câte alte acte din corpus sunt PARȚIALE (contor 271) · R104 — Optsprezece reguli din Design System nu numesc nimic: sunt preferințe, nu norme (contor 90) · R107 — Două temeiuri citează un document adus PARȚIAL, deci nu se poate confrunta nimic (contor 71) · R112 — Ianuarie 2026 stă pe un act care nu era în vigoare (contor 62) · R4 — Câte alte forme VECHI din corpus sunt citite ca fiind la zi (contor 271) · R5 — Marcajele din corpus nu se citesc la FOLOSIRE (contor 270) · R6 — Ceva a scris într-un fișier de corpus, și nu se știe ce (contor 270)
  - **VERIFICARE**: R100 — O calibrare care testează doar ce știe instrumentul să caute confirmă presupunerea, nu o verifică (contor 92) · R113 — Opt acte din corpus sunt nevăzute de instrumentele de articol, fiindcă poartă așezarea Monitorului Oficial (contor 60) · R116 — Cronul de alerte numără firmele DUPĂ succes, deci una care ridică nu apare nicăieri (contor 56) · R117 — Un gard al cărui subiect e o mulțime de lucruri NEREZOLVATE se golește când ultimul se rezolvă (contor 55) · R121 — Decontul precompletat (RO e-TVA / P300) nu e accesibil programatic (contor 52) · R122 — O absență la nivel de FUNCȚIE e invizibilă gărzii care lucrează la nivel de MODUL (contor 48) · R15 — Perechile verificator/verificat copiază CONDIȚII, nu doar constante (contor 260) · R16 — Proza care descrie codul poate fi FALSĂ DE LA NAȘTERE (contor 259) · R173 — Douăzeci și trei de temeiuri n-au prag fiindcă nu li se poate citi FRECVENȚA (contor 10) · R175 — Desktopul asistentului e văzut de o probă proprie, nu de uneltele de listă (contor 4) · R176 — „Publicat" a însemnat un singur repo, iar raportul n-a spus care (contor 3) · R177 — Un model de citire poate avea dependențele scrise din memorie, iar sub-invalidarea nu produce niciun semnal (contor 2) · R178 — Pool-ul de conexiuni se saturează exact la 10 cereri de portofoliu simultane (contor 1) · R18 — Două porți verzi care nu pot deveni roșii (contor 253) · R183 — `apel_anaf` ține o tranzacție deschisă peste apelul la ANAF și peste backoff (contor 0) · R23 — Urme de intenție: nume declarate pe care nu le citește nimeni (contor 227) · R24 — Trei cicluri în graful de clustere: reciproce în fapt, sau doar în graf? (contor 226) · R26 — Cota de TVA scrisă ca valoare implicită în 25 de funcții, iar 23 de apeluri o folosesc (contor 221) · R27 — Pragul de reverificare din cod e încă cel global, deși tabelul lui 55 l-a înlocuit azi (contor 218) · R32 — Date de test al căror antet își contrazice propriile linii (contor 211) · R37 — Nota contabilă n-are autor, iar `sursa` ei e un nomenclator de fapt, scris în 48 de locuri (contor 200) · R48 — Patru trasee nu se pot exercita pe nicio firmă, și nimic din afară nu le blochează (contor 184) · R53 — Inventarul de trasee atribuie unei rute tot ce scrie modulul, nu ce scrie ruta (contor 170) · R59 — Reevaluarea schimbă valoarea contabilă, dar registrul care conduce amortizarea rămâne pe cea veche (contor 162) · R67 — Suita de teste rulează pe baza de PRODUCȚIE, iar izolarea e o convenție, nu o barieră (contor 151) · R68 — Suita n-are bază proprie; separarea rămâne de făcut după ce testele se decuplează (contor 149) · R7 — Câte câmpuri obligatorii sunt gardate ca PREZENȚĂ, dar necontrolate ca ADEVĂR (contor 268) · R75 — Joburile de fundal au deadman; procesul care servește ecranele, nu (contor 134) · R76 — „Googlebot" într-un log nu mai e o informație: 70% din cererile care se declară așa sunt scanere (contor 132) · R98 — O interdicție care citează un inventar îmbătrânește singură la fiecare măsurătoare (contor 95) · R99 — Previzualizarea scoaterii unei firme arată ce s-a GĂSIT, dar nu ce s-a VERIFICAT (contor 93)
  - **ARTEFACT**: R114 — Ecranul Intrastat compară fluxurile unui an ales cu pragul de AZI (contor 58) · R174 — O factură încasată prin bancă nu se marchează încasată nicăieri (contor 6) · R3 — Categoria de mărime nu există în aplicație (contor 271) · R64 — Contabilitatea și stocul sunt două evidențe disjuncte, iar niciun document nu le leagă (contor 158) · R69 — O declarație depusă pe un regim care s-a schimbat între timp nu contrazice pe nimeni (contor 147) · R71 — Ce a scos prima exercitare pe date: șapte lucruri pe care nicio gardă nu le vede (contor 146) · R92 — Ecranul nu poate numi cinci din cele opt stări ale unei facturi, iar 10 din 41 afișează azi șirul brut (contor 97) · R95 — Semaforul nu are nicio cale prin care să ceară D100 unei firme pe regim de profit (contor 96) · R97 — „Ruta livrează, ecranul tace": serverul trimite compoziția unei cifre, iar randarea o pierde (contor 95)
  - **ORDINE**: R11 — Datoria veche consemnată doar în proză, în GARZI.md (contor 264) · R14 — Două funcții de creare a facturii, cu stări implicite diferite (contor 260) · R38 — Lista de cote din ecranul de NIR e scrisă de mână, fiindcă serverul n-o poate da (contor 196) · R39 — Coloana pe care se sprijină verificarea D112 nu se scrie de nicăieri (contor 192) · R47 — NIR-ul creează nota contabilă direct validată, sărind peste ciornă (contor 184) · R8 — Cele trei egalități stricte, redeschise și nereverificate (contor 264) · R9 — Ecranul statului de plată: STOP nemișcat (contor 264)
  - ⚠ **a supraviețuit unei ture**: R1 — 271 commituri pe registru · R100 — 92 commituri pe registru · R104 — 90 commituri pe registru · R107 — 71 commituri pe registru · R11 — 264 commituri pe registru · R112 — 62 commituri pe registru · R113 — 60 commituri pe registru · R114 — 58 commituri pe registru · R116 — 56 commituri pe registru · R117 — 55 commituri pe registru · R121 — 52 commituri pe registru · R122 — 48 commituri pe registru · R14 — 260 commituri pe registru · R15 — 260 commituri pe registru · R16 — 259 commituri pe registru · R173 — 10 commituri pe registru · R174 — 6 commituri pe registru · R175 — 4 commituri pe registru · R176 — 3 commituri pe registru · R177 — 2 commituri pe registru · R18 — 253 commituri pe registru · R23 — 227 commituri pe registru · R24 — 226 commituri pe registru · R26 — 221 commituri pe registru · R27 — 218 commituri pe registru · R3 — 271 commituri pe registru · R32 — 211 commituri pe registru · R37 — 200 commituri pe registru · R38 — 196 commituri pe registru · R39 — 192 commituri pe registru · R4 — 271 commituri pe registru · R47 — 184 commituri pe registru · R48 — 184 commituri pe registru · R5 — 270 commituri pe registru · R53 — 170 commituri pe registru · R59 — 162 commituri pe registru · R6 — 270 commituri pe registru · R64 — 158 commituri pe registru · R67 — 151 commituri pe registru · R68 — 149 commituri pe registru · R69 — 147 commituri pe registru · R7 — 268 commituri pe registru · R71 — 146 commituri pe registru · R75 — 134 commituri pe registru · R76 — 132 commituri pe registru · R8 — 264 commituri pe registru · R9 — 264 commituri pe registru · R92 — 97 commituri pe registru · R95 — 96 commituri pe registru · R97 — 95 commituri pe registru · R98 — 95 commituri pe registru · R99 — 93 commituri pe registru
- **restanțe REZOLVATE**: R10 — Cerințe din „Restanțele" (PLAN_LUCRU) fără gardă · R101 — Declarantul e obligatoriu în hartă și nu oprește nicio declarație, iar XML-ul pleacă în numele lui „ADMINISTRATOR" · R102 — D394 declara livrări și zero facturi emise, în același document, iar contradicția o prindea ANAF · R103 — Regula „orice regulă din DS intră simultan în verificator" n-are nicio gardă · R105 — D112 nu-și poate desface cifra: generatorul ei nu întoarce pozițiile, doar XML-ul · R106 — Un temei numește actul care a MODIFICAT articolul, nu actul care îl CONȚINE · R108 — Un prag fiscal are TREI copii, iar cea canonică era greșită și nefolosită · R109 — Pragul de reverificare se calculează, dar raportul lunar folosește tot pragul global · R110 — Pragul Intrastat e în registru, dar actul care îl poartă e un ciot · R111 — Frecvența citește marcaje într-un document care nu le poate purta, și răspunde STABIL · R115 — Tăria constatărilor supervizorului nu e atribuită, deci nimic nu cere confirmare · R118 — Fișierele statice se servesc DE PE DISC: nicio poartă între scriere și producție · R119 — D394 nu-și expune facturile, deci perechea cu e-Factura nu se poate face fără schimbare de generator · R12 — Divergență între D300 și D100 pe aceeași firmă, același fapt · R120 — Identitatea D300 ↔ D394 lit. C nu e verificată rând cu rând · R123 — Trei din cele cinci comparații orizontale n-au gardul „citește ce scrie generatorul" · R124 — Cheltuiala cu impozitul pe profit rămânea nededusă, iar D101 nu spunea nimic · R125 — „Suma de plată" a obligației D100 trăia doar în XML, nu în rândurile persistate · R126 — Poarta confirmării cere o confirmare pe care ECRANUL nu are prin ce s-o dea · R127 — Depunerea se încheia VIZIBIL pe un drum și TĂCUT pe celălalt, cu același buton · R128 — Poarta confirmării cădea DUPĂ aprobare, iar refuzul ei îngusta opțiunile omului · R129 — O filă deschisă de mult rulează modulele de atunci, oricâte publicări trec · R13 — Partener fără cod fiscal pe factură · R130 — Fluxul public de cursuri al BNR nu mai răspunde, iar cursul vechi se folosește tăcut · R131 — Cele 13 descărcări de fișier înlocuiau motivul serverului cu propriul lor număr · R132 — Infrastructura de testare vizuală rula de nouă zile pe bytecode fără sursă · R133 — Două instrumente de măsură citeau JS-ul printr-un cititor care orbea la o linie cu trei ghilimele · R134 — Toate porțile lui `PUT /tenants/{id}` refuzau cu `500`, deci mesajele lor n-au ajuns niciodată la un om · R135 — O denumire de firmă fără nicio literă trecea, și pleca pe `den` în D394 · R136 — Ecranul «Date firmă» trimitea redenumirea ÎNAINTEA a ceea ce putea fi refuzat · R137 — Sonda de ecran număra rânduri, deci era oarbă exact la felul de scriere pe care îl face un ecran de date · R138 — Un `@` nu e o adresă de email: patru rute creau un cont sau trimiteau un email pe orice șir care conținea unul · R139 — Refuzul de pe linia facturii spunea CARE câmp, nu CE e greșit — iar cuvântul pe care îl folosea era fals · R140 — Registrul de încasări și plăți refuza în limba programatorului, și nimeni nu-l putea deschide ca să vadă · R141 — Unsprezece restanțe erau scrise în AFARA blocului pe care îl citește garda, deci nu le-a verificat nimeni · R142 — Pe ecranul de emitere, o cotă de TVA NECUNOSCUTĂ se afișa ca zero, iar «Total» ieșea egal cu «Bază» · R143 — Ecranul de emitere avea două violări de accesibilitate, dintre care una critică, și nimic nu le vedea · R144 — «Aur de investiții» cădea cu `500` pe o puritate care nu e număr, deci refuzul lui n-a existat niciodată · R145 — «Chirii / comodat / refacturări» nu putea reuși NICIODATĂ din ecran: formularul trimitea alt câmp decât cere ruta · R146 — Fix acolo unde verificarea devenea imposibilă, se renunța la ea: o operațiune fără dată trecea · R147 — Șase refuzuri care vorbeau limba programatorului, dintre care unul în patru locuri · R148 — Aceeași achiziție intracomunitară era așezată în declarație pe exigibilitate și i se valida cota pe data facturii · R149 — Două rute validau cota pe o dată pe care legea nu o numește niciodată · R150 — Un cabinet inexistent răspundea „n-a făcut nimic", iar trei rute înlocuiau tăcut o valoare imposibilă cu una convenabilă · R151 — Excepția din art. 291 alin. (5) nu e modelată: aplicația nu poate ști dacă factura sau avansul au precedat livrarea · R152 — Magazinul online se declara „conectat" la o adresă cu care nu vorbise nimeni · R153 — Registratura scria un document într-un an pe care tot ea îl refuză la citire · R154 — „N-am putut trimite" despre un șir care nu era o adresă de email · R155 — „Încearcă o poză mai clară" despre un fișier care nu era o poză · R156 — Ecranul pachetelor acoperea refuzul precis al serverului · R157 — Răspunsul gol la o sesizare: ecranul nu făcea nimic și nu spunea nimic · R158 — Ecranul de recomandare spunea una, bara de sus alta · R159 — „Ciornă salvată." după o salvare care fusese refuzată · R160 — Gardul acoperirii vizuale cerea 16 ecrane din 18, și nimic n-o spunea · R161 — Butonul de casă rămânea stins, iar motivul trăia într-un `title` pe care atingerea nu-l vede · R162 — «Nota a fost creată ca ciornă» se scria și se ștergea în aceeași clipă · R163 — Nota contabilă cădea cu `500` pe un cont PLAUZIBIL, și numai pe unul plauzibil · R164 — Un CNP valid, deja folosit, întorcea `500` în loc de refuz · R165 — SAF-T-ul unei firme TRIMESTRIALE raporta o singură lună din trei · R166 — Validarea D406 din aplicație era INACCESIBILĂ: orice apel ieșea `gri` · R167 — Refuzul spunea că firma depune TRIMESTRIAL și nu spunea pe ce se sprijină · R168 — Gardul de diacritice era verde, la clichet 0, peste un defect pe care lotul 13 îl scrisese · R169 — Scannerul de citări măsura o lume care se micșora cu fiecare temei pus unde trebuie · R17 — Graful de dependențe e cheiat pe NUME SIMPLU, plat peste tot `core/` · R170 — „32 de formulare probate" era spus despre un registru de 34 · R171 — Cele 24 de citări scoase la iveală de R169 n-au nici articol localizabil, nici prag de reverificare · R172 — «Date firmă» cerea periodicitatea TVA fără să spună după ce se alege · R179 — Confirmarea supervizorului putea rămâne scrisă peste o depunere care nu s-a făcut · R180 — Rotația tokenului SPV se pierdea la orice eșec de după ea · R181 — Un e-mail deja plecat putea rămâne fără rândul care îl oprea să plece din nou · R182 — Contul se putea crea fără dovada acordului, iar clientul fără cheia lui de intrare · R19 — `graf_clustere` tratează utilitarele partajate ca proprietate · R2 — Vigoarea PE PUNCT, nu doar pe articol · R20 — Opt artefacte de UN OCTET în corpus, cu nume de declarație · R21 — Forma de înregistrare în contabilitate nu există nicăieri, iar de ea atârnă Cartea mare · R22 — Jurnalul de origine al unei înregistrări e o constantă, și pleacă așa la ANAF · R25 — Module fiscale care NU citează legea, deci rămân în afara domeniului scanului · R28 — Ce trebuie să arate ecranul de angajare, dacă arată ceva · R29 — Cota de TVA ca valoare implicită în ECRAN, care anulează refuzul învățat de server · R30 — Avertismentul de prăpastie al salariului minim, plecat odată cu estimarea · R31 — Anul e scris în cerere, deci ecranul nu poate ajunge la anul curent · R33 — Module de verificare care n-au fost NICIODATĂ legate · R34 — Nota contabilă de salarii contrazice D112-ul depus, pe 10 din 40 de perechi · R35 — Verdict VERDE pe o lună cu factură necontabilizată, cunoscută în chiar payload-ul verdictului · R36 — Cum ajung faptele economice în contabilitate nu e o alegere DECLARATĂ nicăieri · R40 — Nicio declarație depusă prin aplicație, deci lanțul de apărare nu e exercitat niciodată · R41 — Verdictul oficial de validare se produce, se afișează și se aruncă · R42 — 144 de rute care schimbă date nu verifică niciun rol, iar 24 din 24 dintre ele fac contabilitate · R43 — Confirmarea de plată marchează o factură încasată fără să fi intrat un leu, și caută prin toate firmele · R44 — Un element din coadă e legat de o firmă care nu există · R45 — Patru artefacte se produc, se descarcă, și nu rămân nicăieri · R46 — Trecerea de regim fiscal are cea mai mare consecință și cele mai puține verificări · R49 — Avertismentul de prăpastie al salariului minim, desprins din R30 · R50 — Ștergerea unui cabinet nu curăță tabelele partajate, iar datele lui rămân în ele · R51 — Data încetării contractului nu ajungea în bază, iar ruta răspundea 200 · R52 — Un document care ajunge la un om poate pleca pe un GET, iar acolo nu se verifică niciun rol · R54 — Contul contabil venit din corpul cererii nu e confruntat cu planul de conturi · R55 — Aceeași clasă de operațiune contabilă, roluri diferite, fără motiv scris · R56 — Trei rute manipulează credențiale ale unor sisteme externe, fără rol · R57 — Calea de API emite facturi fără poarta de gestiune pe care o are ecranul · R58 — Închiderea perioadei nu verifică nimic, iar redeschiderea nu lasă urmă · R60 — Instrumentul care hrănește verificările atribuia rutei modulul importat de altcineva · R61 — Raportul Z tastat de om nu are verificare de duplicat, iar nota lui intră direct ca evidență · R62 — Clientul își schimbă adresa de autentificare fără confirmare, iar cabinetul nu află nici asta, nici cine a primit acces · R63 — Aceeași persoană are două adrese în aplicație, iar nimic nu le confruntă · R65 — `patron_email` are precedență la trimiterea pachetului și nicio cale de scriere · R66 — `patron_nume` intră în adeverințe și contracte, și nu-l scrie nimic · R70 — O rută poate fi scrisă, gardată și verde, fără ca nimic s-o cheme · R72 — O firmă adăugată din greșeală nu se poate scoate · R73 — Patru trimiteri de email sunt înghițite tăcut, iar trei dintre ele sunt singura cale de intrare · R74 — Trei joburi de fundal sunt oprite de o lună, iar deadman-ul nu se uită la ele · R77 — Divergența de denumire se ARATĂ, dar alegerea nu se CERE · R78 — Actul cel mai distructiv al aplicației stă sub 26 de carduri, iar cine îl caută nu-l găsește · R79 — Ștergerea unei firme își produce propriul orfan, la 78 de milisecunde după ce a terminat · R80 — Pentru 51 din 411 rute, gardul „rută fără apelant" nu poate afirma nimic · R81 — Denumirea unei firme stă în două locuri, iar redenumirea atinge unul singur · R82 — Cele patru acte cu cel mai mare efect asupra unei firme se termină în tăcere · R83 — O firmă dezactivată nu se poate reactiva: poarta de acces o consideră inexistentă · R84 — Trecutul unei firme scoase din portofoliu nu se mai poate citi: 13 rute de raport răspund 404 · R85 — `d112.pull` întoarce un salariat cu CAS, CASS și impozit, dar fără CAM · R86 — Nota de salarii nu înregistrează deloc biletele de valoare, iar salariile brute intră cu altă cifră decât cea declarată · R87 — O factură EMISĂ nu produce nota contabilă; contabilizarea e un act separat, care se poate uita · R88 — O factură PRIMITĂ validată creează cheltuiala, dar nu și nota contabilă · R89 — Stocul de facturi rămase în afara evidenței n-are nici listă revizuită, nici decizie: reconcilierea istorică · R90 — O notă legată de o factură nu se poate dezlega, iar refuzul ștergerii numește o ieșire care nu există · R91 — O factură EMISĂ care intră prin import nu produce nota, iar absența e DECLARATĂ, nu decisă · R93 — Aceeași lipsă e poartă în trei module de declarație și simplu avertisment în al patrulea, iar ANAF respinge XML-ul · R94 — Două mecanisme răspund diferit la „ce datorează firma asta", iar generatorul nu ascultă de niciunul · R96 — Cele trei registre obligatorii citesc trei populații diferite de note, în aceeași lună și pe aceeași firmă
- **antetul, actualizat la**: 2026-09-10

## 7. POARTA

**Teste.** `4347 passed, 11 skipped, 14 xfailed` în **1.590,76 s** — rularea completă care a produs
`0742e177`. Zero roșii, zero xpass. Cele **21** de teste noi ale lui P4 sunt înăuntru.

**Verificator.** `TOTAL: 0 candidate` · `TOTAL scanat 189 = ACCEPTAT 188 + GRI 0 + ROSU 0 + EXCLUS 1`
· `TOTAL rute 421 = ACCEPTAT 382 + GRI 7 + ROSU 0 + EXCLUS 32` (clichet GRI 7, neatins).

**Four-way, închis de `post-commit`:** `HEAD = origin/main = backup/lant-2026-09-10 = procesul viu`.
Verificat și direct: `git rev-parse HEAD origin/main public/main` dă de trei ori
`0742e177d36a3bfb49cacd299f59f4c4d8fb9964`. **Publicat înseamnă amândouă remote-urile** (R176):
`origin/main` **și** `public/main`, amândouă pe `0742e177`.

**Site.** `https://iconta.eu/` → **200**. Serviciul `iconta-nou`: `active`.

**Commitul de registru** care poartă raportul ăsta rulează **tot poarta completă**. Regula 5 din
`PLAN_LUCRU.md` — o tură care nu atinge niciun `.py`/`.js` rulează doar gărzile de registru — e o
regulă pentru rulările DE MÂNĂ; `pre-commit` rulează suita întreagă la **fiecare** commit,
deliberat: «o poartă care depinde de ce comandă tastezi nu e poartă». Deci și registrele intră
pe verde complet. Ieșirea e în pachetul de livrare, la `loguri/`.

---

## POARTA A RESPINS DE PATRU ORI, ȘI DE FIECARE DATĂ A AVUT DREPTATE

Se scrie fiindcă e chiar felul în care a lucrat tura asta — și fiindcă două dintre respingeri au
găsit defecte în **reparațiile mele**, nu în cod străin.

1. **A treia rulare a atârnat la 80% și n-a mai avansat.** Prima formă a reparației lui R180
   deschidea o **a doua conexiune** ca să scrie tokenul rotit — pe un rând pe care tranzacția
   apelantului îl putea ține. Nu eșuează: **se blochează**. Regula era deja scrisă în casă, la
   operațional: *o probă care ține o tranzacție deschisă nu poate deschide o a doua conexiune pe
   același rând.* Reparația s-a rescris pe forma cerută chiar de P4 — limita aparține
   **use-case-ului**, deci `apel_anaf` comite, imediat după rotație.
2. **Trei gărzi de igienă**, la a patra rulare: două importuri nefolosite · `core/p4_clasificare.py`
   ca *modul de producție nelegat* (a intrat în PIN, cu motivul scris: e un **registru de judecăți**,
   nu o cale de producție) · `test_schema_coloane`, care a citit **proza mea** ca referințe de
   coloane, fiindcă un verdict conținea numele unui tabel urmat de cuvinte. Toate trei aveau
   dreptate; textul s-a rescris.
3. **Doi orfani lăsați de propriile mele probe**, la a cincea rulare: fixtura de curățenie avea o
   listă de tabele **scrisă de mână**, iar ei doi lipseau din ea. Acum folosește chiar lista pe care
   o folosește ștergerea unei firme (`tenant_stergere.TABELE_TENANT`, 20 de tabele). *O probă care
   lasă baza mai murdară decât a găsit-o nu e o probă.* Ce a picat n-a fost proba mea, ci
   `test_tenant_stergere` și blocul de cifre din predare — adică exact gărzile puse pentru asta.
4. **Ziua s-a schimbat sub tură** (capcana 6): antetul lui `CONFORMITATE.md` purta 09.09, iar
   `test_antetul_nu_e_stale` a cerut 10.09.

*Și două opriri care nu sunt respingeri ale porții, ci ale mele:* am oprit rularea de două ori —
o dată ca să adaug o frontieră găsită între timp, o dată ca să corectez o cifră greșită din mesajul
de commit înainte să intre în istorie. Jurnalul porții le-a consemnat ca `exit 143`; se spune aici
ca să nu se citească drept suită roșie.
