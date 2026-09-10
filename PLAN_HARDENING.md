# PLAN_HARDENING — P0…P7

**Registrul planului de întărire.** Cerut de Costin pe 08.09.2026: *„Scrie planul complet P0-P7 …
la nivelul de detaliu cu care au fost date comenzile de P0 și P1 — nu doar titlul, ci ce trebuie
făcut concret și cum se verifică."*

- **ultima actualizare**: 2026-09-10 (valul 1b)
- **stare**: **P0 ÎNCHIS** · **P1 ÎNCHIS** · **P2 ÎNCHIS** · **P3 ÎNCHIS** · **P4 ÎNCHIS** · **P5 VALURILE 1 și 1b EXECUTATE ȘI MĂSURATE** (toate cele 17 căi mutate de pe buclă; C1 pe cereri = **0**; valul 3 NEÎNCEPUT, prin decizia arhitectului) · P6–P7 nedeschise
- **unde stau dovezile**: fiecare pas are commitul lui, raportul lui și ZIP-ul lui
  (`iconta_P<n>_<data>.zip`). Cifrele din planul ăsta se copiază din **ieșirea măsurătorii**, nu din
  raportul precedent — regula care a prins deja trei cifre purtate prin copiere.

---

## ȚINTA GENERALĂ

Aplicația trebuie să reziste la **1000 de firme** fără ca vreo cerere interactivă să depindă de
cantitatea portofoliului. Nu e un obiectiv de viteză, e unul de **formă**: azi mai multe căi fac
muncă proporțională cu portofoliul *în interiorul unei cereri*, iar asta nu se repară prin mașini
mai mari.

**Ce înseamnă „gata" pentru un pas:** nu că trec testele lui, ci că trec **gărzile care nu știau că
vine** — plus măsurătoarea cerută, cu scenariul declarat.

---

## PRINCIPIUL DE LUCRU

Fiecare pas trece prin cinci faze, în ordine, și **niciuna nu se sare**:

1. **Implementare** — se extinde ce există; nu se pornește de la zero dacă există un instrument care
   face deja o parte. Auditul a ce există e primul act, nu o formalitate.
2. **Teste** — gardă proprie, cu calibrare pe propriul mod de eșec (mutație în ambele direcții) și
   aserțiune anti-vacuu. *O gardă care nu poate cădea nu apără nimic.*
3. **Măsurători** — cu **scenariu declarat**: ce s-a construit, pe ce populație, ce NU măsoară.
   Reperul de dinainte se măsoară **înainte de a schimba ceva**, altfel nu există cu ce compara.
4. **Audit independent** — se caută ce a ratat implementarea: instrumentul minte în ambele direcții?
   perimetrul e derivat sau ales? cifra se poate reface?
5. **Acceptare** — poarta completă verde, four-way închis, publicat pe **amândouă** remote-urile,
   ZIP-ul pasului livrat, raport cu măsurătorile.

**Ritmul:** se rulează integral, fără oprire pentru confirmare la fiecare sub-parte. Se oprește doar
în **trei** cazuri: (a) apare o cerință nouă de la Costin; (b) ceva contrazice o decizie deja luată —
atunci se **numește** contradicția, nu se trece tăcut peste ea; (c) contextul e aproape epuizat și
trebuie pregătit `/clear`.

---

## REGULA DE EXCEPȚIE

**Un defect de CORECTITUDINE, de IZOLARE între firme, sau de CONCURENȚĂ urcă imediat în prioritate**,
înaintea oricărui pas de performanță, indiferent unde suntem în P0…P7.

Motivul e asimetria consecinței: un pas de performanță amânat costă minute de așteptare; un rezultat
greșit, o scurgere între firme, sau o stare parțială scrisă în bază costă **încrederea în cifră** —
iar într-o aplicație de contabilitate cifra e produsul.

Ce se face concret: se oprește pasul curent, se deschide restanța, se repară, se gardează, apoi se
reia pasul din locul în care a rămas. *Se consemnează întreruperea, ca să nu pară că pasul a durat
mai mult decât a durat.*

---

## CE NU SE FACE

- **Nu se rescrie ce merge**, ca să arate mai bine. Fiecare schimbare pleacă de la o măsurătoare care
  arată că forma actuală nu încape în țintă.
- **Nu se optimizează speculativ.** Dacă reperul nu s-a măsurat înainte, pasul nu e început.
- **Nu se schimbă comportamentul fiscal** în pașii de întărire. Un P nu are voie să miște o cifră
  care se depune la ANAF; dacă o mișcă, e un defect al pasului, nu un efect.
- **Nu se scoate o gardă ca să treacă un pas.** Dacă o gardă pică, prima ipoteză e că are dreptate.
- **Nu se ridică un clichet** ca să încapă cod nou. Se scrie codul astfel încât să nu-l miște.
- **Nu se atinge poarta completă.** Rămâne obligatorie înainte de publicare și înainte de `/clear`,
  neschimbată, la fiecare pas.

---

# P0 — TEST FEEDBACK ARCHITECTURE · **ÎNCHIS** (`8996f486`, 07.09.2026)

**Ce trebuia făcut.** Modelul pe niveluri: *modificare → teste direct afectate → regresie subsistem →
integrare relevantă → regresie completă (poarta finală, neschimbată)*. **Nu de la zero**: se
auditează și se extind `scripts/perimetru.py` și `scripts/poarta_scurta.py`, deja construite și
probate pe R43, R94 și `d112.py`. **Fail-closed obligatoriu la fiecare nivel**: dacă derivarea nu
poate stabili cu certitudine perimetrul, se rulează tot și se spune de ce.

**Cum se verifică.** Pentru fiecare nivel nou: *ce derivă · pe ce se bazează · ce se întâmplă când
perimetrul nu se poate închide*. Plus măsurarea timpului de feedback pe fiecare nivel, comparat cu
regresia completă.

**Ce s-a livrat.** `nivel_direct` / `nivel_subsistem` / `nivel_integrare` / `complet`, toate derivate
din același graf de import; `perimetru()` **neatinsă**. Frontieră la rădăcina de compunere (`main`) —
descoperită măsurând: `main.py` nu importă `core.d112`, dar închiderea ajungea la el și aducea toate
cele 22 de teste care importă `main`, pentru orice modul. Refuzul se **moștenește**: `_seminte()` e
comună, deci un `.md`, un `.js` sau `main.py` atins face **fiecare** nivel să refuze.

**Măsurat** (poarta completă de referință: 4.161 teste, ~1.500 s):

| atins | N1 | N2 | N3 |
|---|---|---|---|
| `core/facturi_api.py` | 7 fiș · 112 teste · 99 s | 8 · 114 · 89 s | 29 · 298 · 140 s |
| `core/control_fiscal_api.py` | 14 · 211 · **27 s** (55×) | 25 · 313 · 129 s | 47 · 550 · 170 s |
| `core/d112.py` | 28 · 331 · 103 s | 189 · 1.657 · 338 s | 204 · 1.803 · 349 s |

*Cifra care contrazice intuiția, păstrată fiindcă e utilă:* pe `facturi_api`, N1 (7 fișiere) a durat
**mai mult** decât N2 (8 fișiere). Costul e dat de câteva fișiere lente, nu de numărul lor —
**„nivel mai mic" înseamnă „mai puțin acoperit", nu „mai rapid"**.

**Gard:** `core/test_niveluri_feedback.py` (monotonie pe mulțimi, moștenirea refuzului, N4 care nu
se derivă, frontiera care chiar taie, anti-vacuu).

**DEFECT GĂSIT DUPĂ ÎNCHIDERE, 08.09.2026 — și se scrie aici, la P0, nu într-o notă de raport.**
Nivelurile N1 și N2 ocoleau ramura **regulii 5**: chemau `_seminte()` direct, deci o tură care atinge
**numai documente** era refuzată, în loc să primească perimetrul de registre pe care `perimetru()`
îl închide corect. Cum `subsistem` e nivelul IMPLICIT al lansatorului, **regula 5 era desființată în
practică** din 07.09 până azi. Reparat: ramura e acum în dispecerul `nivel()`, comună tuturor.

*De ce n-a prins-o garda mea:* `test_refuzul_se_mosteneste_la_toate_nivelurile` proba refuzul pe
atingeri **mixte** (`.md` + `.py`), unde refuzul e corect. Cazul **doar-documente** n-a fost probat
niciodată. **O calibrare care verifică doar direcția în care instrumentul trebuie să REFUZE nu spune
nimic despre cazurile în care trebuie să ACCEPTE** — a doua instanță a lecției „ambele direcții"
(METODA §22), de data asta pe un instrument de proces, nu pe unul fiscal. Proba lipsă e acum în gardă.

*Cum a fost găsit:* folosind instrumentul pe chiar tura care scria planul ăsta.

---

# P1 — SUPERVIZOR · **ÎNCHIS** (`ced26440`, 08.09.2026)

**Ce trebuia făcut.** De la recalcularea completă la fiecare `GET`, la **stare persistată,
versionată, cu prospețime explicită**. Rezultatul per firmă se calculează o dată, se persistă, se
citește ieftin. Fiecare rezultat poartă: **versiunea datelor-sursă** din care a fost calculat,
**momentul calculului**, și **dacă e curent sau urmează să fie recalculat**. Recalcularea se
declanșează la schimbarea unei date-sursă **a firmei respective** — nu la fiecare cerere, nu pentru
tot portofoliul deodată.

**Interzis explicit:** a arăta o valoare veche ca fiind curentă, fără să spună asta. *O stare „în
recalculare" declarată e acceptabilă; una veche și tăcută nu e.*

**Cum se verifică.** `GET` pe ecranul supervizorului cu **1000 de firme populate cu date realiste**
(scenariu construit și **declarat**), **p95 sub 1 s la citire**; recalcularea per firmă poate fi
asincronă. **Fault-check:** dacă datele-sursă ale unei firme se schimbă în timp ce rezultatul ei e
citit, cititorul nu primește o stare parțial actualizată.

**Ce s-a livrat.** `core/supervizor_cache.py`: contor de versiune ridicat de **triggere** pe cele
șase tabele-sursă ale firmei plus sursa din `public` (derivate mecanic din ce citește culegerea);
prospețimea **derivată**, nu stocată; `stare ∈ {curent, invalidat, lipseste}`; al treilea fel de
neverificare, `NECALCULAT`, fiindcă înainte nu putea exista. `ruleaza_portofoliu` **neatinsă** —
persistarea e un strat, nu a doua implementare. **DECIZII 76** înlocuiește explicit decizia din
01.09 („fără tabel nou, fără ciclu de viață"), a cărei condiție de expirare era chiar apariția
consumatorului.

**Măsurat:** reper 9 ms/firmă → **~5 s la 1000**. După: citire **p95 45 ms** (rece 57, median 42),
adică **~110×**. Recalcularea rămâne 9 ms/firmă, dar se plătește o dată per schimbare.

**Gard:** `core/test_supervizor_cache.py` (7 probe, inclusiv fault-check-ul pe scriere concurentă).

---

# P2 — PORTOFOLIU / N+1 · **ÎNCHIS** (08.09.2026)

**Ce trebuie făcut.** Eliminarea **pipeline-urilor fiscale seriale per firmă** din cererile
interactive. Rutele numite: `migrare/solduri`, `migrare/plan-conturi`, `migrare/vector`,
`control-fiscal`, `termene`.

**Criteriul de acceptabilitate, verbatim:** *„O complexitate O(N) ieftină pe read-model e
acceptabilă; un pipeline costisitor rulat serial de 1000 de ori nu e."* Deci ținta **nu** e
eliminarea buclei peste firme — e eliminarea **muncii scumpe din interiorul ei**: deschiderea unei
conexiuni per firmă, rularea unui motor fiscal per firmă, recitirea acelorași nomenclatoare la
fiecare iterație.

**Concret, pentru fiecare din cele cinci:**
1. **Se măsoară întâi**, per rută: **numărul de interogări** și **latența**, pe curba
   **100 / 250 / 500 / 1000** de firme. Fără reperul ăsta pe toate patru punctele, pasul nu e început
   — o singură măsurătoare nu arată dacă creșterea e liniară sau mai rea.
2. Se stabilește **ce e read-model** (poate fi citit dintr-o interogare peste `public`) și **ce e
   pipeline** (cere motorul fiscal per firmă). Distincția se derivă din cod, nu se alege.
3. Pipeline-ul iese din cererea interactivă — fie precalculat și persistat, ca la P1, fie mutat pe o
   cale asincronă, **cu aceeași disciplină de prospețime ca P1**: versiune, moment, stare explicită.
   *Interdicția lui P1 se aplică și aici: o valoare veche nu se arată ca fiind curentă.*
4. Ce rămâne în cerere trebuie să fie **O(N) ieftin**: o interogare peste read-model, nu N interogări.

**Cum se verifică.**
- **Query count și latență, înainte/după, pe curba 100/250/500/1000**, per rută, cu scenariul
  declarat (cum s-au construit firmele, ce date au, ce NU măsoară scenariul).
- Numărul de interogări per cerere **nu crește cu N** după intervenție — se măsoară, nu se afirmă.
- Nicio schimbare de **conținut**: aceleași rute întorc aceleași verdicte pe aceleași date. Se
  probează prin comparație înainte/după pe portofoliul real, nu doar prin teste noi.
- Gărzile existente ale rutelor rămân verzi, iar cele care numără interogări (dacă apar) se
  calibrează în ambele direcții.

**Reper cunoscut, de comparat:** P1 a scos 5 s → 45 ms pe supervizor, cu read-model persistat. Dacă o
rută din P2 iese cu un raport mult mai slab, **se spune de ce** — nu se raportează ca succes.


## P2 — CE S-A LIVRAT ȘI CE S-A MĂSURAT

**Instrumentul întâi, calibrat în ambele direcții** (`scripts/masoara_interogari.py`): numără
interogări, **conexiuni** și dus-întorsuri, împachetând `db.get_conn` la rulare. Calibrarea e
obligatorie înainte de folosire — i se dă un caz N+1 (trebuie să raporteze problemă) și unul
set-based (trebuie să raporteze corect). *Cifrele de mai jos n-ar fi valorat nimic fără ea.*

**Ce a găsit instrumentul și citirea codului n-ar fi arătat:** `auth_api.tenantii_userului` — chemată
din 13 locuri — făcea **3 interogări per firmă** (`SAVEPOINT` + `SELECT tip_firma` + `RELEASE`) doar
ca să LISTEZE portofoliul. La 1000 de firme: 3.000 de interogări înaintea oricărei munci utile.

**Soluția:** model de citire în `public` (`core/firma_rezumat.py`), un rând per (firmă, aspect), cu
**aceeași disciplină de prospețime ca P1** — versiune, moment, stare derivată, niciodată stocată.
Șase aspecte: `tip_firma`, `solduri`, `plan_conturi`, `vector`, `termene`, `control_fiscal`.
Invalidarea vine de la aceleași **triggere**, cu contorul extins la 8 tabele-sursă.
Calculul **nu s-a rescris**: blocul per-firmă din `/termene` a fost **extras** cuvânt cu cuvânt, iar
`control_fiscal` cheamă exact `evalueaza_firma` + `_construieste_contabil`.

**MĂSURAT, curba 100 / 250 / 500 / 1000** (scenariu declarat: domeniu sintetic peste cele 14 scheme
reale, ciclate; model populat cu rezumate reale, 10% invalidate; `tenantii_userului` e înlocuit de
ham, deci interogarea lui de listare **nu intră în cifră, nici înainte, nici după**):

| ruta | ÎNAINTE la 1000 | DUPĂ la 1000 |
|---|---|---|
| `migrare/solduri` | 4.000 interog. · 2.001 conex. · **1,24 s** | **1 · 1 · 0,012 s** |
| `migrare/plan-conturi` | 3.000 · 2.001 · **0,98 s** | **1 · 1 · 0,009 s** |
| `migrare/vector` | 3.000 · 2.001 · **1,01 s** | **1 · 1 · 0,010 s** |
| `termene` | 8.000 · 3.001 · **12,88 s** | **1 · 1 · 0,022 s** |
| **`control-fiscal`** | **278.882 · 12.001 · 70,81 s** | **1 · 1 · 0,017 s** |

Creșterea era **liniară** înainte (~2,0× la fiecare dublare, măsurat pe toate patru punctele).
După: **numărul de interogări e constant**, iar latența crește de la o bază de milisecunde — exact
„O(N) ieftin pe read-model", care e acceptabil.

**Costul mutat, nu desființat:** recalcularea grea costă **~120 ms/firmă** (măsurat pe portofoliul
real), plătită o dată per firmă per schimbare, în afara cererii interactive.

**TREI DEFECTE ALE MELE, prinse de gărzi în timpul pasului** — scrise fiindcă două erau serioase:
1. **SECURITATE.** Extrăgând blocul din `/termene`, am inserat funcția nouă **între decorator și
   `def`** — deci `@app.get("/termene")` a ajuns pe ajutorul extras, **fără `Depends(cere_cabinet)`**.
   `ruff` n-a văzut nimic (cod valid), `compile()` la fel. A prins-o `test_rute_autentificate`.
   *O mutare de cod care trece pe lângă un decorator nu e o mutare de cod, e o schimbare de contract.*
2. **CORECTITUDINE.** Recalcularea rula cu `ctx`-ul unui singur cabinet, iar două sub-verificări
   (stocuri, praguri Intrastat) cad pe „gri" fără acces la firmă — deci verdictul ar fi depins de
   cine întreabă. Reparat: se alege, per firmă, administratorul cabinetului ei.
3. **MĂSURĂTOARE FLATANTĂ.** Prima curbă „după" arăta 1 interogare / 4 ms — dar modelul era **gol**
   pentru id-urile sintetice, deci rutele întorceau „necalculat" pentru toate. Am populat modelul și
   am măsurat din nou. *O cifră adevărată despre un răspuns fără conținut e tot o cifră falsă.*

*Și două lecții de unealtă:* `ast.parse` **nu** prinde `continue` în afara buclei — aia e o
verificare de compilare, deci validarea corectă e `compile()`; iar contorul de interogări numără doar
ce se deschide **înăuntrul** blocului măsurat — a raportat 0, cinstit, când testul lua conexiunea
înainte.


---

# P3 — SQL + INDEX

**Ce trebuie făcut.** **Exclusiv pe măsurătoare**, în patru pași, în ordine, pentru fiecare
interogare atinsă:
1. **query real** — luat din trafic sau din calea măsurată la P2, nu inventat;
2. **`EXPLAIN (ANALYZE, BUFFERS)`** — ieșirea se păstrează, integral, ca dovadă;
3. **identificarea** cauzei: scanare secvențială pe tabel mare, sortare pe disc, buffere citite
   inutil, join în ordine proastă;
4. **index sau rescriere**, apoi **`EXPLAIN` din nou**, cu ieșirea păstrată.

**Cum se verifică.**
- Ambele ieșiri `EXPLAIN` (înainte/după) intră în raport și în ZIP-ul pasului. *Un index adăugat
  fără plan de dinainte și de după e o presupunere, nu o reparație.*
- **Costul migrării pe 1000 de scheme** se măsoară separat și se raportează: un index pe un tabel de
  firmă înseamnă 1000 de `CREATE INDEX`. Se măsoară durata totală, dacă se poate face concurent, și
  ce se întâmplă dacă migrarea cade la jumătate.
- Se verifică și **costul de scriere**: un index accelerează citirea și încetinește `INSERT`.
  Rutele de import (care scriu mult) se re-măsoară după.
- Niciun index „preventiv": fiecare intră cu interogarea care l-a cerut, numită în comentariu.

---

# P4 — TRANSACTION OWNERSHIP

**Ce trebuie făcut.** Limitele tranzacției se definesc de **use-case**, nu de funcția de bază de
date. Azi `get_conn()` deschide o tranzacție per apel, iar un use-case care cheamă trei funcții poate
ajunge cu trei tranzacții — deci cu stare parțială posibilă între ele.

**Concret:** se identifică use-case-urile care scriu în mai multe locuri (emitere factură + contare +
numerotare; import cu mai multe straturi; aprobare + depunere), și li se dă **o singură** limită de
tranzacție, deținută de use-case.

**Cum se verifică — prin fault injection, nu prin citire:**
- `BEGIN → pas A → pas B → eșec intenționat` → se confirmă că **nu rămâne stare parțială**: se
  compară amprenta bazei înainte și după, nu doar numărul de rânduri. *O sondă care numără rânduri e
  oarbă la modificări — clasă deja măsurată (R137).*
- **Separat**, se verifică **efectele ireversibile prin rollback**: fișiere scrise pe disc, e-mailuri
  trimise, apeluri externe (SPV/ANAF, Brevo). Un `rollback` nu desface un e-mail. Pentru fiecare
  astfel de efect: ori se mută după commit, ori se face idempotent, ori se declară explicit ca
  ireversibil, cu motivul.
- Cazul deja cunoscut, de folosit ca reper: `_salveaza_cache` făcea `commit` pe conexiunea
  apelantului — adică pe tranzacția facturii —, iar un refuz de curs lăsa în bază o factură
  numerotată și contată, fără curs. *Înainte de a repara o cale moartă, întreabă ce se schimbă pe ea
  când învie.*

**ÎNCHIS 09.09.2026.** Ce a livrat, pe scurt — detaliile în `RAPORT_P4.md`:

- **inventarul e DERIVAT, nu scris**: `scripts/scan_tranzactii.py` construiește, pentru fiecare din
  cele **510** puncte de intrare (rute + lucrători de fundal), **arborele de domenii tranzacționale**
  al căii, și marchează cele șase semne cerute de comandă. **332** de candidați — **toți** primesc
  verdict, fără prag *(prima formă clasifica 32; pragul era al meu, nu al comenzii, iar runda de
  acceptare din 10.09 l-a scos)*;
- **clasificarea e COMPLETĂ și PĂZITĂ**: `core/p4_clasificare.py` — 34 de rânduri individuale plus un
  motor de **reguli pe clase structurale** care acoperă restul de 298. Rezultat: `RAW_CANDIDATES =
  CLASSIFIED_CANDIDATES = 332`, `UNCLASSIFIED_RAW_CANDIDATES = 0`, iar contabilitatea inventarului
  se închide: **6 RAW_CRITICAL + 325 RAW_NON_CRITICAL + 1 RAW_FALSE_POSITIVE = 332**. Separat, pe
  universul operațiilor critice: **1 cale internă**, deci `TOTAL_CRITICAL_OPERATIONS = 7`, toate
  şapte cu probă de injecție. *Cele două nu se adună între ele — prima formă a blocului le punea sub
  acelaşi nume şi dădea 333 pe o populaţie de 332.* `core/test_tranzactii_clasificate.py` —
  o cale compusă nouă, neclasificată, **cade poarta**, iar refuzul e probat prin **calibrare
  negativă pe fiecare din C1…C6** și prin două mutații;
- **fiecare cale critică are injecție de defect**: `core/test_p4_fault_injection.py`, cu starea
  comparată pe **amprentă**, nu pe numărătoare (R137). **Șase din șapte au fost roșii pe codul de
  dinainte** — a șaptea, emiterea de factură, probează o proprietate care exista deja;
- **șase reparații**: R179 (confirmare ↔ depunere), R180 (rotația tokenului SPV), R181 (e-mail ↔
  rândul care-l oprește, în două locuri), R182 (cont ↔ dovada acordului; client ↔ cheia lui);
- **efectele pe care `rollback` nu le desface** au analiză separată: **8** locuri, toate judecate
  (`INTEROGARE` sau `EFECT`), în `EFECTE_EXTERNE`, păzite la fel;
- **rămas deschis, declarat**: R183 — `apel_anaf` ține o tranzacție peste apelul la ANAF. E durată,
  nu proprietate; se închide cu R178.

---

# P5 — ASYNC / BLOCKING I/O

**Ce trebuie făcut.** **Analiză per rută, nu migrare masivă.** Nu se convertește aplicația la
`async` pe orizontală; se caută rutele în care un I/O blocant ține bucla de evenimente ocupată.

**Concret, în trei pași, per rută:**
1. **Benchmark concurent** — N cereri simultane, se măsoară latența p50/p95 și debitul;
2. **identificarea blocajului** — apel de rețea sincron (SPV, BNR, Brevo), citire de fișier mare,
   `subprocess` (DUKIntegrator), interogare lungă;
3. **intervenție minimă** — mutare pe `run_in_threadpool`, sau scoatere din cerere pe o coadă.

**Cum se verifică.**
- **Benchmark concurent din nou**, aceeași sarcină, aceleași N. Se raportează p50/p95 și debitul
  înainte/după. *O intervenție care îmbunătățește p50 și înrăutățește p95 nu e o îmbunătățire.*
- Se verifică explicit că **nu s-a schimbat semantica**: aceleași răspunsuri, aceeași ordine a
  efectelor, aceleași erori.
- Nicio rută nu se convertește „fiindcă e la modă": fiecare intră cu măsurătoarea care a arătat
  blocajul.

## Rezultatul DIAGNOSTICULUI (10.09.2026) — pasul 3 NEEXECUTAT

*Runda de diagnostic a produs **jumătatea „înainte"** a fiecărei perechi de măsurători cerute mai
sus. Pasul 3 (intervenția) și verificarea „din nou, după" rămân neîncepute, prin regula rundei.*

- **inventar mecanic**, `scripts/scan_blocante.py`: **514** puncte de intrare (407 rute sincrone,
  20 `async`, **3 middleware**, restul lucrători și `lifespan`), **7 detectori**, **0 trunchieri**
  de expandare. Fără prag: **94** candidați bruți. Artefacte în `masuratori/p5/`;
- **calibrare**: 24 de probe, **0 goluri**, 5 controale negative. Unde „numai Cx" e imposibil,
  implicația e scrisă și pinată: **C5 ⟹ C2**, **C6 ⟹ C2**;
- **C6 („rețea fără termen") are ZERO instanțe reale**, și e o măsurătoare, nu o scăpare. Toate
  cele 5 aprinderi din prima formă erau **același loc**, numărat de cinci ori:
  `core/spv_conector.py:455`, `requests.request(metoda, url, ..., **kw)` din `apel_anaf`. Termenul
  vine prin **despachetare**, iar toți cei 7 apelanți reali îl trimit (`timeout=30/60/120`,
  verificat rând cu rând). Detectorul are acum trei stări și se aprinde numai pe absența **certă**.
  *Rămâne adevărat, și se scrie: `apel_anaf` n-are termen **implicit**, deci un apelant viitor care
  uită `timeout=` produce chiar defectul, și nimic nu l-ar opri;*
- **clasificare**, `core/p5_clasificare.py`, păzită de `core/test_blocante_clasificate.py`:
  **46 ACTION_REQUIRED + 48 ACCEPTABLE_BY_DESIGN + 0 FALSE_POSITIVE = 94**, `UNCLASSIFIED=0`,
  `UNEXPLAINED_EXCLUSIONS=0` peste toți cei 48 excluși;
- **măsurat, pe calea reală**: canar în gol p95 **3,4 ms**; în timpul rutei `async def` la N=5000,
  p95 **117,9 ms**, vârf **158,7 ms**. Martorul sincron, cost comparabil (21,8 vs 22,5 ms), în
  threadpool: canar p95 **3,8 ms** — **plat**. *Aceeași muncă, efect opus asupra vecinilor;*
- **concurență** k=1/2/5/10 pe ruta `async def`: debit **23,05 · 22,59 · 24,19 · 22,15** cereri/s.
  **Plat** — concurența nu cumpără nimic, iar timpul total crește liniar cu k. `ERRORS`,
  `TIMEOUTS`, `DEADLOCKS` = 0 peste tot;
- **descoperirea care schimbă ordinea reparațiilor**: pool-ul (10) **nu s-a atins niciodată** —
  maxim **8** simultane la k=10. Nu fiindcă e generos, ci fiindcă **bucla blocată serializează
  cererile înainte să ajungă la pool**. *Defectul de pe buclă ASCUNDE presiunea pe pool; reparând
  bucla, cererile chiar devin simultane, și abia atunci pool-ul se lovește de plafon.* Deci valul
  care scoate apelurile externe de sub conexiune nu e opțional: e **consecința** celui de pe buclă;
- **efect asupra producției**: niciunul. `PRODUCTION_CODE_CHANGED=NO`, derivat din `git diff` față
  de `8ce4cd84`, nu declarat; `PRODUCTION_DATA_AFFECTED=NO`, prin amprentă pe 10 tabele;
- **valurile propuse, NEEXECUTATE**: **1** (17 căi mutate de pe buclă — dovada MĂSURATĂ) → **3**
  (29 de căi scoase de sub conexiunea ținută — dovadă de capacitate; atinge tranzacții, deci
  teritoriul lui P4). *Al doilea val, cel al termenelor, a dispărut la reparația detectorului: n-a
  rămas niciun apel fără termen cert. Cifra n-a scăzut fiindcă am relaxat criteriul, ci fiindcă
  criteriul greșea — iar cele două căi n-au ieșit din `ACTION_REQUIRED`, s-au mutat în valul 3 pe
  altă dovadă.*


---

### Excepția de publicare pentru fazele PUR DIAGNOSTICE (10.09.2026, cerută de arhitect)

**Regula.** *„Nu publica fazele pur-diagnostice pe cele două remote-uri — publicarea repornește
procesul degeaba dacă runtime-ul nu s-a schimbat."* O fază care nu atinge niciun fișier care ajunge
în procesul care servește cereri **nu se publică**: nu se împinge pe `origin/main` și `public/main`,
nu se republică statica, nu se repornește serviciul.

**Criteriul e MECANIC, nu o etichetă din mesaj:** `git diff --name-status <baza>..HEAD`, filtrat pe
ce ajunge în proces. `scripts/artefacte_p5.py:_e_productie` e definiția, deja folosită ca să derive
`PRODUCTION_CODE_CHANGED`. *La fel ca la curățenie: decide indexul, nu eticheta.*

**NEIMPLEMENTATĂ ÎN HOOK, și motivul e o ciocnire, nu o uitare.** `post-commit` nu poate primi
criteriul ăsta fără să cadă `core/test_publicare_restart_neconditionat.py`, care interzice explicit
*„orice inspecție a CONȚINUTULUI commitului în hook (`git diff` / `--name-only` / extensii de
fișier)"*. Gardul are instanța lui scrisă: pe **11.08.2026**, publicarea condiționată pe tipul
commitului a lăsat procesul viu pe commitul anterior — `RUNNING b0ccc40` vs `HEAD f504f00`. Iar
four-way-ul cere `pornire > commit`, deci un commit nepublicat l-ar lăsa deschis prin construcție.

**CUM SE APLICĂ: varianta (b), confirmată de arhitect pe 10.09.2026.** *„O fază pur diagnostică
nu se comite separat — artefactele ei călătoresc cu următorul commit de runtime."*

Deci **hook-ul nu se atinge**, iar `core/test_publicare_restart_neconditionat.py` rămâne exact cum e:
publicarea și restartul continuă să fie NECONDIȚIONATE de conținut, iar four-way-ul își păstrează
invarianta `pornire > commit`. *Varianta (a) — un four-way care are voie să lase `RUNNING` în urmă —
a fost respinsă: ar fi slăbit cea mai tare garanție a casei ca să scutească o repornire.*

**Ce se schimbă în practică:** măsurătorile și artefactele unei runde de diagnostic se produc pe
arborele de lucru, ÎNAINTE de commit, și intră în același commit cu schimbarea de runtime pe care o
verifică. Asta e și forma corectă a perechii cerute la `:334`: jumătatea «înainte» și cea «după» ale
aceleiași intervenții ajung împreună în lanț, nu la două zile distanță.

**Limita, scrisă ca să nu fie citită mai larg:** o rundă care chiar NU produce nicio schimbare de
runtime — un diagnostic care se închide cu «nu e nimic de reparat» — n-are cu ce să călătorească.
Atunci artefactele ei intră în ZIP-ul de livrare și rămân necomise, iar raportul spune asta.


## VALUL 1 (10.09.2026) — executat, măsurat, și NEÎNCHIS

*Aprobat de arhitect: „valul 1, apoi valul 3 (obligatoriu, nu opțional)". Valul 3 NU s-a pornit.*

**Ce s-a făcut.** 16 din cele 17 căi au trecut din `async def` în `def`, deci Starlette le mută pe
un fir din cele 40. Citirea fișierului a trecut de la `await X.read()` la `_octetii(X)` —
echivalent verificat în sursa Starlette (`datastructures.py:462`, `formparsers.py:266`). Diff-ul e
de două linii pe rută. Clichet în ambele direcții în `core/test_blocante_clasificate.py`: niciuna
din cele 16 nu mai poate aprinde C1, **și** mulțimea celor rămase pe buclă e pinată.

**Ce NU s-a făcut, și de ce.** `POST /tenants/{id}/horeca/import-amef` rămâne `async def`. Azi,
după citirea fișierului, handler-ul rulează până la capăt fără să cedeze bucla, deci două cereri
simultane sunt SERIALIZATE — iar pe serializarea asta se sprijină, fără s-o fi declarat nimeni,
poarta R61 din `_cere_z_unic` (un raport Z duplicat se REFUZĂ). `inregistrari` **nu are index unic
pe `(sursa, numar)`**. Mutarea pe fir ar fi cumpărat latență cu o regresie de contabilitate.

**Măsurat din nou, aceeași sarcină, aceiași N** (`masuratori/p5_val1/`, cu așteptarea scrisă
ÎNAINTE în `ASTEPTAREA.md` și confruntarea în `REZULTATUL.md`):

| | înainte | după | predicția |
|---|---|---|---|
| canar p95 la N=5000 | 117,9 ms | **93,7 ms** | „sub 10 ms" — **GREȘIT** |
| ruta p50 la N=5000 | 143,0 ms | 149,7 ms | „± 25%" — corect |
| debit la k=10 | 22,15 req/s | **19,4 req/s** | „peste 40" — **GREȘIT, și invers** |
| conexiuni simultane la k=10 | 8 din 10 | **10 din 10** | „10 din 10" — corect |

**De ce n-a fost destul, măsurat și nu dedus.** Prima explicație — GIL-ul — a căzut la măsurătoare:
munca de procesor a rutei e 38,5 ms din 149,7. Cauza adevărată e că FastAPI serializează răspunsul
**în afara handler-ului, pe buclă**: `jsonable_encoder` **67,6 ms** + `json.dumps` 7,2 ms pentru
cele 5000 de tranzacții (998 KB de JSON). *Handler-ul s-a mutat; răspunsul nu.* Comparația care
închide argumentul: martorul sincron, tot `def`, tot cu bază, dar cu răspuns mic — canar p95
**4,3 ms, plat**. O singură variabilă diferă.

**Consecința pentru inventarul P5:** cei 7 detectori au căutat I/O blocant **în codul nostru**.
Serializarea răspunsului e în framework, deci n-a fost văzută de niciun detector și nu figurează
între cei 94 de candidați. **Oarbire prin construcție, descoperită abia măsurând reparația.**

**Ce e închis:** cele **4** căi care ajung la rețea, `sleep` sau disc — `/migrare/fisier`,
`/migrare/incarca`, `/portal/bon`, `/raportari/mesaj/{mid}/imagine`. Acolo câștigul e întreg,
fiindcă acele primitive eliberează GIL-ul. `/migrare/fisier` era cazul cel mai grav din tot P5:
`time.sleep(1.1)` la fiecare 100 de CUI-uri, pe buclă — un fișier cu 500 de CUI-uri îngheța
aplicația 4,4 secunde.

**Ce NU e închis:** cele **12** căi care întorc liste mari. Pentru ele valul 1 era necesar, dar nu
suficient.


## VALUL 1b (10.09.2026) — serializarea răspunsului, și un defect al propriului banc

**Ce s-a făcut.** Cele 12 rute care întorc liste mari își construiesc singure răspunsul
(`JSONResponse(jsonable_encoder(x))`), deci codificarea se execută pe firul handler-ului. FastAPI o
făcea în învelișul `async` de după — adică **pe buclă**, oricât de sincron ar fi fost handler-ul.
Octeții sunt aceiași, verificat la sursă și pinat de o probă care compară cu chiar calea
framework-ului.

**`horeca/import-amef`, ultima din cele 17, a trecut și ea pe fir** — după ce garanția pe care se
sprijinea a devenit una a DATELOR: index unic parțial pe `(sursa, numar)`, în template pentru
firmele noi și prin `core/raport_z.py` la pornire pentru cele existente. **Măsurat înainte: 0
rânduri de raport Z pe toate cele 20 de scheme, deci 0 duplicate** — indexul a intrat pe teren gol.
Migrarea **nu șterge niciodată nimic**: dacă o firmă ar avea duplicate, `CREATE UNIQUE INDEX` pică
pe ea, mesajul le numește, iar pornirea se oprește.

**Rezultatul, cu așteptarea scrisă înainte** (`masuratori/p5_val1b/`):

| | început P5 | val 1 | val 1b |
|---|---|---|---|
| canar p95 @N=5000 | 117,9 ms | 93,7 ms | **33,2 ms** |
| canar vârf @N=5000 | 158,7 ms | 107,2 ms | **66,2 ms** |
| canar în gol (martor) | 3,4 ms | 3,0 ms | 3,0 ms |
| **C1 pe căi de cerere** | 17 | 1 | **0** |

**Ce cere planul la `:328` — „rutele în care un I/O blocant ține bucla ocupată" — e ÎNCHIS.**

**Ce NU e închis: debitul.** La k=10, 23,7 cereri/s față de 27,5 la k=1 — plat. Și aici e a treia
descoperire a rundei: **cifra veche, 19,4, nu era o măsurătoare a aplicației**. Bancul trimitea cele
k cereri din k FIRE ale unui singur proces Python; la k=2 consuma **0,98** din timpul de perete în
procesor, adică era el însuși strangularea. S-a mutat pe **procese**, cu bazinul încălzit înainte de
ceas, și — mai important — **își raportează acum propria saturare** (`saturare_client`,
`DEBIT_DEMN_DE_INCREDERE` în fiecare rând). Excluse prin măsurătoare: clientul (0,32), pool-ul
(10 vs 40 pe serverul de probă: 381 → 379 ms), saturarea de procesor a serverului (0,47).

**Rămâne DESCHIS de ce nu crește debitul**, și nu se inventează o explicație: în campania asta am
ghicit cauza de două ori înainte s-o măsor și am greșit de fiecare dată. Următoarea măsurătoare care
ar închide întrebarea cere cronometrare pe segmente în codul de producție — deci se cere întâi.


---

# P6 — STATELESS / SCALARE ORIZONTALĂ

**Ce trebuie făcut.** **Nicio stare business autoritativă doar în memoria unui proces.** Măsurat deja
(07.09): 35 de nume la nivel de modul se pot schimba la rulare; dintre ele, **`main._login_fail`**
(blocarea după eșecuri de autentificare) și **`main._alerte_ultima_trimitere`** (cooldown-ul
alertelor) sunt stare business — se pierd la fiecare repornire, iar `post-commit` repornește la
fiecare publicare.

**Cache local admis, dar numai DECLARAT**, cu cinci lucruri scrise lângă el:
**rol** (ce accelerează) · **sursa autoritativă** (de unde se poate reface) · **motiv** (de ce e în
memorie) · **invalidare** (când și cum) · **dovadă de reconstrucție identică** (o probă care golește
cache-ul și arată că răspunsul e același).

**Include infrastructura, nu doar codul:** trecerea de la **un singur proces** (azi: `ExecStart`
fără `--workers`, confirmat un singur PID) la **mai multe instanțe** — `--workers` sau echilibrator.

**Cum se verifică.**
- Se pornesc **cel puțin două instanțe** și se probează că un flux care trece prin amândouă se
  comportă identic: blocarea la autentificare ține pe ambele, cooldown-ul alertelor nu trimite
  dublu, sesiunile funcționează indiferent de instanță.
- Pentru fiecare cache rămas: proba de **reconstrucție identică** (golire → același răspuns).
- **Fault-check:** o instanță e oprită în timpul unei cereri; cererea eșuează curat, nu lasă stare
  parțială (se leagă de P4).
- Se re-măsoară four-way-ul: cu mai multe procese, „procesul viu poartă HEAD" devine „**toate**
  procesele poartă HEAD" — brațul se redefinește, altfel afirmă mai puțin decât pare.

---

# P7 — APPLICATION LAYER

**Ce trebuie făcut.** Separarea **HTTP → use-case → motor fiscal → repository**. Azi ruta face
adesea toate patru: citește cererea, decide, calculează și scrie.

**Criteriul e separarea responsabilităților, NU numărul de linii din `main.py`.** O rută mutată în
alt fișier, care face tot ce făcea, n-a schimbat nimic — a mutat problema și a produs o cifră
flatantă.

**Concret:**
- **HTTP** — validare de formă, autentificare, traducerea erorilor în coduri. Nu decide nimic fiscal.
- **use-case** — deține tranzacția (P4), orchestrează, nu conține reguli fiscale.
- **motor fiscal** — pur pe cât se poate: primește date, întoarce rezultat, nu deschide conexiuni.
- **repository** — singurul care știe SQL și scheme.

**Cum se verifică.**
- **Mecanic, nu prin impresie:** un motor fiscal nu importă `db`; un use-case nu construiește
  `HTTPException`; ruta nu conține SQL. Fiecare din cele trei se poate deriva cu `ast` și se poate
  garda cu clichet.
- Testele existente ale rutelor rămân verzi **fără să fie rescrise** — dacă trebuie rescrise, mutarea
  a schimbat comportamentul.
- Se măsoară ce s-a mutat: câte rute, câte reguli fiscale scoase din stratul HTTP. *Nu se raportează
  „main.py a scăzut cu N linii" ca rezultat — e un efect, nu un criteriu.*

---

## REGULI DE LIVRARE, valabile la toți pașii

- **ZIP per pas**: `iconta_P<n>_<data>.zip`, conținând **doar** fișierele modificate/create în pasul
  respectiv, plus raportul complet al pasului, plus măsurătorile brute.
- **„Publicat" înseamnă AMÂNDOUĂ remote-urile** (`origin` privat și `public`), sau se spune explicit
  care a rămas în urmă și de ce. Regula s-a născut dintr-o divergență reală (**R176**).
- **Poarta completă** înainte de publicare și înainte de `/clear`, neschimbată.
- **Pentru fiecare operațiune care a durat peste o secundă**, raportul spune **ce a rulat concret** și
  **durata exactă**, nu eticheta pasului. Dacă există un reper dintr-o tură similară, se compară
  explicit.
