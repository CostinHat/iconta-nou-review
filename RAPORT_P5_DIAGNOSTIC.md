# RAPORT — P5, DIAGNOSTIC (async / I/O blocant) | 10.09.2026 | `8ce4cd84` → `20a10bc6` → final

*Trei commituri, ținute separat fiindcă așa cere comanda: **`8ce4cd84`** = baseline (P4 închis) · **`20a10bc6`** = codul de diagnostic și artefactele lui, publicat pe ambele remote-uri cu four-way închis · **finalul** = commitul care poartă raportul ăsta, iar hash-ul lui e în `masuratori/p5/TRASABILITATE_P5.txt` — un raport nu-și poate conține propriul hash.*

*Diagnostic, nu implementare. Nicio linie de cod de producție n-a fost atinsă — și asta nu e o
promisiune, e un câmp derivat din `git diff` față de commitul de bază (§7).*

---

## 0. CERINTE

**1. Aprobarea valurilor de remediere P5, sau altă ordine.** Diagnosticul a găsit **46 de căi care
cer acțiune**, împărțite în **două** valuri după felul dovezii. Nu le-am executat — comanda
interzice explicit. Ce cer: **care valuri intră, în ce ordine, și dacă intră amândouă**.

* **ce blochează dacă rămâne nedată** — P5 nu poate trece din diagnostic în implementare. Faza
  rămâne deschisă la nesfârșit, iar cele 46 de căi rămân măsurate și nereparate.
* **detaliile care ajută decizia:**
  * **Valul 1 — 17 căi, dovadă MĂSURATĂ.** Handler `async def` cu I/O blocant pe buclă. Efectul e
    pe cifre: la N=5000, o cerere fără nicio legătură a așteptat **158,7 ms**, față de **3,4 ms**
    linia de bază. Intervenția e cea din plan (`run_in_threadpool`), și casa o are deja scrisă în
    propriul middleware de audit. **Cea mai gravă din val: `POST /migrare/fisier`**, care ajunge la
    `core/anaf_api.py:138` — `time.sleep(1.1)` **pe buclă**, o dată la fiecare 100 de CUI-uri. Un
    fișier cu 500 de CUI-uri îngheață întreaga aplicație ~4,4 s, garantat, fără ca ANAF să fie
    măcar lent.
  * **Valul 3 — 29 de căi, dovadă STRUCTURALĂ de CAPACITATE.** Apel extern executat cât timp e
    ținută o conexiune din pool. Pool-ul are **10**; termenele externe merg până la 60 s.
    Aritmetica, nu măsurătoarea: 10 cereri simultane pe astfel de căi golesc pool-ul pentru toată
    aplicația. **N-am măsurat-o fiindcă ar fi însemnat să chem ANAF/SPV pe bune**, iar regula fazei
    interzice efectul extern real.
  * **Valul 2 a existat și a dispărut în tura asta, și merită spus de ce.** Era „apel de rețea fără
    `timeout`", 2 căi. Verificând la sursă, s-a dovedit **fals-pozitiv al detectorului meu**:
    termenul vine prin despachetare (`**kw`), iar toți cei 7 apelanți reali îl trimit — v. §5.14.
    *Cifra n-a scăzut fiindcă am relaxat criteriul, ci fiindcă criteriul greșea; iar cele două căi
    n-au ieșit din `ACTION_REQUIRED`, s-au mutat în valul 3 pe altă dovadă.* **Ce rămâne, ca risc
    numit și nestins:** `spv_conector.apel_anaf` n-are termen **implicit**, deci un apelant viitor
    care uită `timeout=` produce chiar defectul, și nimic nu l-ar opri.
  * **Ordinea pe care o propun, și de ce nu e cea evidentă:** 1 → 3, dar **nu** fiindcă 3 e
    opțional. **Avertizarea iese chiar din măsurătoare** (v. §5.5): blocarea buclei ASCUNDE azi
    presiunea pe pool. La k=10 s-au folosit simultan doar **8 conexiuni din 10**, fiindcă bucla
    serializează cererile. *Reparând valul 1, cererile chiar devin simultane — și abia atunci
    pool-ul se va lovi de plafon.* Deci valul 3 e **consecința** valului 1, nu o temă separată:
    făcut singur valul 1, aplicația schimbă un blocaj vizibil pe unul mai greu de citit.
* **a câta tură** — prima.

**2. Confirmarea că P5 se publică pe cele două remote-uri, ca P4.** Regula de livrare a pașilor
(`PLAN_HARDENING.md`, „REGULI DE LIVRARE") cere publicare per pas. P5 însă **nu schimbă runtime-ul**
— sunt instrumente de diagnostic și artefacte. Am publicat, ca la P4, fiindcă asta cere regula
scrisă; dacă vrei ca fazele pur-diagnostice să NU repornească procesul, spune-o și o scriu în plan
ca excepție.

* **ce blochează dacă rămâne nedată** — nimic acum; e o regulă pentru fazele următoare.
* **detalii** — publicarea repornește procesul (pasul 5). Repornirea costă, fiindcă `lifespan`
  blochează bucla la pornire cu un timp care crește cu numărul de firme (v. §5.3, rândul
  `main.py::lifespan()`). Pentru o fază care nu schimbă nimic în runtime, e cost fără câștig.
* **a câta tură** — prima.

**3. Deschid sau nu o secțiune măsurată în `CONFORMITATE.md` pentru clasa găsită la §5.13?**
Defectul propriei mele sonde pare **sistematic**, nu izolat: în `scripts/masoara_*.py` sunt **5**
funcții de agregare care primesc statusul de la ajutorul lor și nu-l duc mai departe
(`masoara_p3.curba`, `masoara_p3.masoara_pe_real`, `masoara_p3.de_ce_difera`,
`masoara_rute_portofoliu.curba`, `masoara_val.curba`).

* **ce blochează dacă rămâne nedată** — nimic în P5. Dar dacă e o clasă reală, alte măsurători din
  istoric ar putea fi la fel de fals-verzi ca a mea, iar asta nu se va afla singur.
* **detalii** — **n-am deschis-o din proprie inițiativă, și motivul e regula secțiunii**: cifra „5"
  e obținută prin detecție **pe text**, nu pe structură, și n-a trecut prin eșantionul de 30 pe care
  `METODA_VERIFICARE.md` îl cere înainte de un total. *O secțiune de conformitate cu o cifră
  nemăsurată ca lumea ar fi chiar defectul pe care secțiunea îl păzește.* Am scris-o deocamdată ca
  **instanță** sub interdicția 76, care o acoperă. Costul măsurării ca lumea: o tură scurtă,
  instrument pe AST + calibrare, în jur de o oră.
* **a câta tură** — prima.

---

## 1. CE AM PRESUPUS

1. **Că „rută" din contractul P5 înseamnă „punct de intrare care servește cereri", deci include
   middleware-ul.** Planul zice „per rută". Am inclus `@app.middleware("http")` fiindcă rulează pe
   buclă la FIECARE cerere — e cea mai fierbinte cale din aplicație. *Prima formă a scanerului nu-l
   vedea; era un fals-negativ exact pe calea care contează cel mai mult.* Dacă „rută" trebuia citit
   strict, inventarul are 3 intrări în plus, toate declarate.

2. **Că nivelul de concurență cerut (k=2/5/10) se măsoară pe UNA din căile diagnosticate, nu pe
   toate.** Am ales `POST /tenants/{id}/banca/parse-extras`: e `async def`, e **read-only**, și
   costul ei crește cu un parametru pe care îl controlez (numărul de tranzacții din extras). O rută
   care scrie ar fi cerut curățenie după fiecare din cele ~100 de cereri ale bancului.

3. **Că „interogare lungă" din pasul 2 al planului nu primește detector static.** Nu e decidabilă
   din cod: aceeași interogare e scurtă sau lungă după datele firmei. Am declarat-o ca limită a
   instrumentului, iar înlocuitorul empiric e chiar timpul măsurat al rutei. Presupunerea e că asta
   satisface pasul 2 — dacă nu, îmi spui și construiesc altceva (`pg_stat_statements`).

4. **Că pot re-rula bancul de măsură de câte ori e nevoie**, fiindcă e read-only pe date reale și
   își face curățenia. Verificat, nu presupus: amprentă pe 10 tabele înainte/după, identică.

Altceva n-am presupus. Contractul P5 nu l-am dedus: l-am citit, și e citat cu `file:line` în §5.0.

---

## 2. CE AM FĂCUT ÎN PLUS / MAI PUȚIN

### În plus

* **Un martor sincron**, care nu era cerut. Fără el, „ruta async încetinește alte cereri" ar fi fost
  o afirmație despre încărcare în general, nu despre buclă. Martorul e o rută **sincronă de cost
  comparabil** (21,8 ms vs 22,5 ms): aceeași muncă, efect opus asupra vecinilor — 3,8 ms vs 117,9 ms.
  *Asta transformă măsurătoarea din „e lent" în „e lent DIN CAUZA buclei".*
* **Citirea jurnalului serverului**, adăugată ca să numere deadlock-uri. A prins altceva — v. §5.13.
* **O a treia stare în detectorul de termene** (`PRIN_KW`), peste cele două cerute de o citire
  simplă a criteriului. Nu ca rafinament: fără ea, două căi de cerere rămâneau clasificate greșit,
  iar raportul ar fi cerut o reparație inexistentă (§5.14).
* **Clichet bidirecțional pe ce vede detectorul în casă**, în loc de cerința „fiecare detector se
  aprinde pe cod real". Cerința aia ar fi picat pe un adevăr, nu pe un defect.
* **N=2500 și N=5000**, peste seria cerută. Nu ca să umflu cifra: seria cerută se oprește unde curba
  abia se desface, iar panta se citește greu pe capătul plat.
* **`MAX_SIMULTANEOUS_RESOURCE_USE` măsurat prin eșantionare de proces**, nu numărat din cod.
* **Blocul de acceptare e generat**, nu scris — inclusiv `PRODUCTION_CODE_CHANGED`, care e derivat
  din `git diff` față de baseline. Un câmp care spune „n-am schimbat nimic" și pe care îl scriu tot
  eu nu e o măsurătoare.

### Mai puțin

* **N-am măsurat căile din valul 3 pe serviciile externe reale.** Regula fazei interzice efectul
  extern. Deci pentru cele 27 de căi dovada e aritmetică de capacitate, nu o cifră — și e scrisă ca
  atare în fiecare rând, nu ascunsă sub același cuvânt cu cele măsurate.
* **N-am măsurat ocuparea threadpool-ului (cele 40 de fire) direct.** Nu se poate observa din
  afara procesului fără instrumentare în cod, iar comanda cere STOP înainte de așa ceva.
  Înlocuitorul e martorul sincron: dacă firele s-ar fi terminat, canarul ar fi arătat-o. N-a arătat.
* **N-am reparat nimic.** 46 de căi cer acțiune și rămân neatinse.
* **N-am pornit P6.**

---

## 3. CE AM ACTUALIZAT

| registru | ce s-a scris |
|---|---|
| `CONFORMITATE.md` | intrarea P5-DIAGNOSTIC: contractul citit la sursă, cei 7 detectori, 94 de candidați, 46/48/0, defectul propriei sonde (§5.13) |
| `GARZI.md` | garda nouă `core/test_blocante_clasificate.py` — 30 de probe, trei straturi |
| `TESTE.md` | fișierul de test nou, cu ce păzește |
| `PLAN_HARDENING.md` | linia de stare a lui P5: **diagnostic închis, implementare neîncepută**. Fișier normativ — citit înainte de modificare (`:325-342`), v. §5.0 |
| `PLAN_LUCRU.md` | nimic de actualizat: P5 nu schimbă ordinea de lucru, iar valurile sunt cerință deschisă (§0.1), nu plan adoptat |
| `DECIZII.md` | decizia de a NU garda „interogare lungă" printr-un detector static, cu motivul |
| `INSTRUMENTE_ROADMAP.md` | nimic de actualizat: cele 11 instrumente sunt ale campaniei de gărzi; `scan_blocante` nu e pe listă, e instrument de fază |
| `ISTORIC.md` | nimic de actualizat, fiindcă nu s-a schimbat nimic în comportamentul aplicației — istoricul urmărește ce vede utilizatorul |
| `METODA_VERIFICARE.md` | nimic de actualizat: §22 (ambele direcții) și §23 (structură, nu text) au fost **aplicate**, nu extinse |
| `DESIGN_SYSTEM.md` | nimic de actualizat: nu s-a atins niciun ecran |
| `PLAN_INVESTIGATII.md` | nimic de actualizat: P5 n-a deschis investigații, a închis o măsurătoare |
| `PLAN_ARHITECTURA.md` | nimic de actualizat: diagnosticul nu propune schimbare de arhitectură; valurile sunt intervenții locale |
| `MODEL_AUDIT_TENANT.md` | nimic de actualizat: nu s-a atins nicio fațetă de audit de tenant |
| `ISTORIC_TENANTI.md` | nimic de actualizat: firmele de probă s-au șters, amprenta o dovedește |
| `anaf_surse/INDEX.json` | nimic de actualizat: nu s-a adus niciun act |
| `anaf_surse/PROVENIENTA.json` | nimic de actualizat: idem |

---

## 4. ÎNȚELEGEREA

*Scrisă înainte de muncă. Ce a ieșit diferit e notat în §5.13, nu rescris aici.*

Am înțeles că **P5 e o măsurătoare, nu o reparație**, și că partea grea nu e să găsesc I/O blocant
— e să nu confund trei lucruri diferite:

1. **cod blocant** (o proprietate a formei — se citește din AST),
2. **cod care blochează pe cineva** (o proprietate a execuției — se vede doar măsurând),
3. **cod care merită reparat** (o judecată, care trebuie scrisă, nu presupusă).

Un inventar care le amestecă ar produce fie 400 de „probleme" fără greutate, fie o listă scurtă
aleasă după ce-mi amintesc eu. De-aia comanda cere trei lucruri separate: inventar **fără prag**,
clasificare cu **verdict pentru fiecare**, și măsurători pe **calea reală**.

Am înțeles și că **instrumentul e primul suspect**, nu codul: un scaner necalibrat produce cifre pe
care nimeni nu le poate contrazice, fiindcă nimeni nu știe ce văd. De-aia calibrarea e cerută
înaintea inventarului, cu fixtură per detector și controale negative.

Și am înțeles că sonda **n-are voie să lase urme**: schemă/tenant dedicat, curățenie, curățenie
**verificată**.

---

## 5. RĂSPUNS LA COMANDĂ

### 5.0 „Înainte de orice măsurătoare, citește documentele canonice … Nu inventa din memorie ce înseamnă P5."

**Contractul P5, la sursă: `PLAN_HARDENING.md:325-342`.** Citat, nu rezumat:

> `:325` **# P5 — ASYNC / BLOCKING I/O**
> `:327` **Analiză per rută, nu migrare masivă.** Nu se convertește aplicația la `async` pe
> orizontală; se caută rutele în care un I/O blocant ține bucla de evenimente ocupată.
> `:328-331` Concret, în trei pași, per rută: **1.** benchmark concurent — N cereri simultane, se
> măsoară latența p50/p95 și debitul; **2.** identificarea blocajului — apel de rețea sincron (SPV,
> BNR, Brevo), citire de fișier mare, `subprocess` (DUKIntegrator), interogare lungă; **3.**
> intervenție minimă — mutare pe `run_in_threadpool`, sau scoatere din cerere pe o coadă.
> `:334-340` **Cum se verifică:** benchmark concurent din nou, aceeași sarcină, același N; se
> raportează p50/p95 și debitul înainte/după. *O intervenție care îmbunătățește p50 și înrăutățește
> p95 nu e o îmbunătățire.* … Nicio rută nu se convertește „fiindcă e la modă": fiecare intră cu
> măsurătoarea care a arătat blocajul.

**Ce am dedus din el, și e important pentru forma raportului:** pasul 3 (intervenția) și verificarea
„din nou, după" sunt **în afara** fazei de diagnostic. Deci P5-DIAGNOSTIC produce **jumătatea
„înainte"** a fiecărei perechi de măsurători. Cifrele din §5.4-5.5 sunt exact linia de bază față de
care se va măsura orice intervenție viitoare. *De-aia am păstrat eșantioanele brute: fără ele,
comparația „înainte/după" ar compara o măsurătoare cu o amintire.*

**Alte documente citite:** `SABLON_RAPORT.md` (forma raportului ăstuia), `METODA_VERIFICARE.md`
§22-§23 (calibrare în ambele direcții; aserțiuni pe structură), `CLAUDE.md` (procesul, poarta),
`PLAN_HARDENING.md` „REGULI DE LIVRARE" (ZIP per pas, publicare pe două remote-uri).

---

### 5.1 „Inventar mecanic complet … ID-uri stabile, definiții exacte, limitări cunoscute … fără prag înainte de clasificare"

**Instrument: `scripts/scan_blocante.py`.** Separat de `scan_tranzactii` **deliberat**: P4 e o fază
închisă, ale cărei 332 de cifre nu au voie să se miște fiindcă am atins un fișier comun.

**Cei 7 detectori, cu definiția exactă** (`scripts/scan_blocante.py`, `DETECTORI`):

| id | definiție |
|---|---|
| **C1** | `async def` cu primitivă blocantă atinsă **fără** trecere prin threadpool — ține bucla ocupată |
| **C2** | rută **sincronă** care ajunge la un apel de rețea extern — ocupă un fir din cele 40 |
| **C3** | cale care ajunge la un **subproces** |
| **C4** | cale care ajunge la `time.sleep` |
| **C5** | primitivă blocantă **ne-DB** executată cât timp e ținută o conexiune din pool |
| **C6** | apel de rețea **fără `timeout`** |
| **C7** | I/O de fișier pe calea unei cereri |

**Ce s-a scanat:** `main.py`, `core/`, `scripts/` — **514 puncte de intrare**: 407 rute sincrone, 20
rute `async`, **3 middleware**, restul lucrători de fundal (`__main__` + `cron.ruleaza`) și
`lifespan`. Expandare pe graful de apeluri până la adâncimea 8; **`TRUNCATED_EXPANSIONS=0`**, deci
niciun lanț n-a fost tăiat.

**Fără prag: `RAW_CANDIDATES=94`** — orice punct de intrare care aprinde **≥1** detector e candidat.
Fiecare are ID stabil (`P5-001`…`P5-094`), fișier, funcție, detectorii aprinși, primitivele cu
`file:line`, și lanțul de apel până la fiecare. Artefacte: `P5_INVENTAR_BRUT.{txt,json}`,
`P5_CALLCHAINS.{txt,json}`.

**Limitările instrumentului, declarate în antetul lui — nu descoperite de cititor:**

* **Omonimia.** Rezolvarea numelor are trei trepte: alias de import → fișierul gazdă → **toate
  definițiile cu acel nume**. Treapta a treia **supra-aproximează**, și fiecare primitivă venită de
  acolo poartă steagul `O` în `P5_CALLCHAINS.txt`.
* **Apel indirect.** Un apel prin variabilă, `getattr`, sau tabelă de dispecerizare **nu se vede**.
  Deci fals-negativele sunt posibile, iar `RAW_CANDIDATES=94` e un **minim**, nu un total.
* **„Interogare lungă" n-are detector.** Nu e decidabilă static — v. §1.3. Înlocuitorul e timpul
  măsurat al rutei.
* **Adâncimea 8.** La 0 trunchieri nu limitează azi; ar putea limita după ce lanțurile cresc.

---

### 5.2 „Calibrarea detectorilor … «numai Cx» unde e matematic posibil … `DETECTOR_CALIBRATION_GAPS=0`"

**`DETECTOR_CALIBRATION_PROBES=24` · `DETECTOR_CALIBRATION_GAPS=0` · `NEGATIVE_CONTROLS=5`.**
Artefact: `P5_DETECTOR_CALIBRATION.{txt,json}`. Calibrarea rulează **în suită**
(`core/test_blocante_clasificate.py`), nu doar la linia de comandă.

**Fixturi pozitive.** Corpus sintetic (`scan_blocante.CORPUS`) cu o rută per detector, iar
**mulțimea aprinsă e pinată**, nu doar prezența: `C1`, `C2`, `C3`, `C4`, `C7` aprind **numai** pe
detectorul lor.

**Unde „numai Cx" e matematic imposibil, implicația e scrisă și testată:**

* **C5 implică C2.** C5 = primitivă ne-DB ținută sub o conexiune. Ca s-o ai, îți trebuie un apel
  extern pe o cale sincronă — care e definiția lui C2. Fixtura `POST /minim_c5` pinează `{C2, C5}`.
* **C6 implică C2.** Un apel de rețea fără termen e, întâi de toate, un apel de rețea.
  `POST /minim_c6` pinează `{C2, C6}`.

**Controale negative** (nu se aprind deloc): `GET /control_curat`, `GET /control_pur`,
`POST /control_threadpool` (blocantă, dar **prin** `run_in_threadpool` — proba că ieșirea din buclă
e recunoscută), plus două middleware curate.

**Calibrarea de middleware, adăugată după un fals-negativ real:** `mw_blocant()` **trebuie** văzut ca
punct de intrare și trebuie să aprindă `{C1}`. Prima formă a scanerului nu vedea middleware-ul
deloc.

**Calibrarea stării nedecise, adăugată după al doilea fals-pozitiv (§5.14):** o rută sintetică ce
apelează `requests.get(url, **kw)` **nu** trebuie să aprindă C6, trebuie să aprindă exact `{C2}`, și
starea `PRIN_KW` trebuie **numărată**, nu uitată. Trei probe.

**Anti-vacuu, în ambele direcții — dar ca CLICHET, nu ca cerință.** Prima formă cerea ca fiecare
detector să se aprindă și pe **codul real**. Cerința aia s-a dovedit prea tare: după reparația lui
C6, el are **zero** instanțe reale, fiindcă așa e casa. Deci mulțimea detectorilor aprinși pe cod
real e **pinată** (`{C1,C2,C3,C4,C5,C7}`), fiecare absență își scrie motivul, iar un test separat
cere ca detectorul cu zero instanțe să fie **totuși viu** — se aprinde pe cazul lui sintetic, cu
mulțimea pinată. *Un detector care se strică și unul care n-are ce găsi arată identic din cifră;
numai clichetul în două direcții îi deosebește.*

---

### 5.3 „Clasificare completă … ACTION_REQUIRED / ACCEPTABLE_BY_DESIGN / FALSE_POSITIVE … `UNCLASSIFIED=0`, `UNEXPLAINED_EXCLUSIONS=0`"

**Registru: `core/p5_clasificare.py`. Gardă: `core/test_blocante_clasificate.py` (30 de probe).**

```
RAW_CANDIDATES=94   CLASSIFIED_CANDIDATES=94   UNCLASSIFIED_RAW_CANDIDATES=0
ACTION_REQUIRED=46   ACCEPTABLE_BY_DESIGN=48   FALSE_POSITIVES=0
RAW_CLASS_SUM=94     RAW_CLASS_ACCOUNTING=PASS      (46+48+0 = 94 = 94)
EXCLUSIONS_TOTAL=48  UNEXPLAINED_EXCLUSIONS=0
```

`EXCLUSIONS_TOTAL` e derivat peste **toți** candidații care nu cer acțiune (48), nu peste rândurile
scrise de mână — lecția din runda de acceptare a lui P4. Fiecare are motiv scris; garda cere
minimum 80 de caractere de motiv, deci un motiv gol nu poate trece.

**Regulile, în ordine — și ordinea e o afirmație:**

| # | regulă | clasă | n |
|---|---|---|---|
| 1 | `OMONIM` — toată dovada vine din treapta a treia | FALSE_POSITIVE | 0 |
| 2 | `FUNDAL` — lucrător cron, fără buclă, fără om care așteaptă | ACCEPTABLE | 13 |
| 3 | `C1-CERERE` — blocant pe buclă, pe cale care servește cereri | **ACTION** | 16 |
| 4 | `C6-FARA-TIMEOUT` — rețea fără termen pe calea unei cereri | **ACTION** | **0** |
| 5 | `C5-EXTERN-CU-CONEXIUNE` — apel extern sub conexiune ținută | **ACTION** | 29 |
| 6 | `SINCRON-MARGINIT` — threadpool, I/O mărginit | ACCEPTABLE | 34 |
| — | rânduri individuale (`parse-extras`, `lifespan`) | 1 ACTION + 1 ACCEPT | 2 |

*Regula 4 are **zero** aplicări reale după reparația din §5.14, și rămâne în registru cu cazul ei
sintetic. O regulă cu zero aplicări nu se șterge: ștergerea ar face ca reapariția clasei să treacă
neobservată.*

**`OMONIM` stă PRIMA, iar la P4 aceeași regulă stătea ULTIMA.** Nu e o inconsecvență, e simetria:
rezolvarea pe omonimie **adaugă** evenimente. La P4 verdictul sigur era „non-critic", deci
supra-aproximarea era inofensivă. Aici verdictul sigur e „acceptabil", deci aceleași evenimente în
plus ar produce o **acțiune falsă**. *Aceeași proprietate a instrumentului cere ordini opuse,
fiindcă direcția prudenței e opusă.* Ordinea e pinată de un test.

**`FALSE_POSITIVES=0` — și e o cifră care trebuie apărată, nu doar raportată.** Zero fals-pozitivi
ar putea însemna „regula nu se aplică niciodată", adică o regulă decorativă. De-aia există un
candidat sintetic care o aprinde, plus proba că un candidat sprijinit **numai** pe omonimie
primește `FALSE_POSITIVE` chiar dacă aprinde C1.

**Felurile de dovadă, ținute separat** (`MASURAT` 17 · `STRUCTURAL_MARGINIT_DAR_RAR` 29 ·
`THREADPOOL` 34 · `FARA_BUCLA` 13 · `PORNIRE` 1). Un raport care le-ar pune sub „am găsit 46 de
probleme" ar ascunde exact partea care decide ordinea reparațiilor.

**Mecanismul REFUZĂ — și asta e proba care contează.** Pentru fiecare regulă există un candidat
sintetic care o aprinde **și** dovada că, fără ea, același candidat rămâne neclasificat, iar
contabilitatea trece pe `FAIL`. Există și un test pentru cazul viclean: dacă scot **doar**
`C1-CERERE`, candidatul cade în regula-coadă și primește tăcut verdictul **greșit**. Testul pinează
purtarea asta ca fiind cunoscută — de-aia proba de refuz se face cu lista **goală**, nu ciuntită.

---

### 5.4 „Măsurători pe calea reală … N=5/50/100/250/500/1000 … nu extrapola un slope din total/N"

**Instrument: `scripts/masoara_p5.py`.** Pornește **propriul** uvicorn, pe un port liber — niciodată
procesul de producție. Metoda: un **canar** care bate continuu o rută ieftină (`/public/config`) cu
client persistent, cât timp ruta grea lucrează. Canarul nu măsoară ruta grea; măsoară **ce pățesc
ceilalți** cât timp ea lucrează. Fiecare N se repetă de 8 ori, ca fereastra să conțină ~50 de probe
de canar — *o percentilă pe două valori nu e o percentilă*.

**Calibrarea canarului, în gol:** p50 **2,4 ms**, p95 **3,4 ms**, 212 probe. Bancul **refuză** să
măsoare dacă linia de bază nu e strânsă.

| N | rută p50 | rută p95 | canar p50 | **canar p95** | canar max |
|---|---|---|---|---|---|
| — (gol) | — | — | 2,4 | **3,4** | 6,7 |
| 5 | 22,5 | 38,9 | 1,7 | **4,5** | 5,6 |
| 50 | 24,1 | 40,3 | 1,6 | **3,3** | 5,1 |
| 100 | 24,6 | 42,7 | 2,4 | **4,8** | 4,9 |
| 250 | 28,6 | 44,8 | 2,2 | **6,5** | 7,8 |
| 500 | 34,4 | 48,8 | 1,8 | **13,7** | 14,0 |
| 1000 | 46,6 | 63,7 | 1,5 | **25,4** | 27,6 |
| 2500 | 82,4 | 117,0 | 2,8 | **58,9** | 96,5 |
| 5000 | 143,0 | 196,1 | 1,9 | **117,9** | 158,7 |

**Ce spune tabelul, citit corect:** canarul p50 rămâne ~2 ms peste tot — cele mai multe cereri
nimeresc între blocaje. Dar **coada crește cu munca rutei**: p95 al canarului urmărește p50 al
rutei aproape unu-la-unu (117,9 vs 143,0). *Adică o cerere care n-are nicio legătură cu importul
așteaptă cât durează importul altcuiva.* Asta e definiția blocării buclei.

**MARTORUL SINCRON, controlul care transformă asta din corelație în cauză.** Aceeași măsurătoare pe
`GET /tenants/{id}/facturi` — rută **sincronă**, deci în threadpool, cu cost comparabil (p50 **21,8
ms** față de 22,5 ms al rutei async la N=5):

```
canar în timpul rutei sincrone:   p50 1,5 ms · p95 3,8 ms · max 16,8 ms   (219 probe, toate 200)
canar în gol:                     p50 2,4 ms · p95 3,4 ms
```

**Plat.** Aceeași cantitate de muncă, aceeași bază de date, efect asupra vecinilor: **nul**.
Diferența dintre 3,8 ms și 117,9 ms nu e cantitatea de muncă — e **unde** se execută.

**Nu am extrapolat nicio pantă.** Fiecare rând e o măsurătoare proprie, cu propriul eșantion.
Eșantioanele brute — **27 de serii, 1030 de valori** — sunt în `P5_RAW_EVIDENCE/esantioane.json`,
deci orice percentilă din raportul ăsta se poate recalcula. *O cifră care nu se poate recalcula nu e
o măsurătoare, e o amintire.*

**Căi de succes, gol și eroare:** toate cererile au ieșit **200** (`UNEXPECTED_STATUSES=0`), inclusiv
martorul. Cazul „gol" e chiar N=5. Cazul de eroare l-am măsurat fără să vreau — v. §5.13.

---

### 5.5 „Concurență k=2/5/10 … `MAX_SIMULTANEOUS_RESOURCE_USE` … nu confunda total acquisitions cu simultaneous usage … nu «repara» prin mărirea poolului"

| k | total | **debit** | p50 | p95 | p99 | **MAX_SIM** / CAP | ERRORS | TIMEOUTS | DEADLOCKS | canar p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 43,4 ms | **23,05/s** | 43,0 | 43,0 | 43,0 | **1** / 10 | 0 | 0 | 0 | 8,8 |
| 2 | 88,6 ms | **22,59/s** | 84,1 | 87,2 | 87,2 | **2** / 10 | 0 | 0 | 0 | 8,5 |
| 5 | 206,7 ms | **24,19/s** | 201,4 | 204,1 | 204,1 | **4** / 10 | 0 | 0 | 0 | 17,5 |
| 10 | 451,5 ms | **22,15/s** | 435,6 | 444,5 | 444,5 | **8** / 10 | 0 | 0 | 0 | 44,3 |

**Rândul care spune tot e coloana debitului: 23,05 → 22,59 → 24,19 → 22,15.** Plat. Zece cereri
simultane produc exact același debit ca una singură, iar timpul total crește **liniar** cu k
(43 → 88 → 207 → 451 ms). Asta e serializare curată: **concurența nu cumpără nimic**, fiindcă toate
cererile stau la coadă pentru același fir de execuție — bucla.

`MAX_SIMULTANEOUS_RESOURCE_USE` e măsurat prin **eșantionarea conexiunilor active ale procesului**
în timpul rafalei, nu prin numărarea achizițiilor din cod. Diferența contează: la k=10 s-au făcut 10
achiziții, dar niciodată mai mult de **8 simultane**.

**Și aici e cea mai importantă concluzie a fazei, care nu se vede în niciun rând luat separat:**
pool-ul are 10 conexiuni și **nu s-a atins niciodată**. Nu fiindcă e generos — ci fiindcă **bucla
blocată serializează cererile înainte să ajungă la pool**. *Defectul valului 1 ASCUNDE presiunea
măsurată de valul 3.* Când bucla se eliberează, cererile chiar devin simultane, și abia atunci
pool-ul se lovește de plafon. De-aia valul 3 nu e opțional (§0.1).

**N-am mărit nimic.** `ICONTA_POOL_MAX` a rămas 10, threadpool-ul 40, un singur proces uvicorn.
Mărirea poolului ar fi mutat cifra fără să atingă cauza — și ar fi făcut diagnosticul să pară mai
bun exact în felul pe care comanda îl interzice.

---

### 5.6 „Siguranța efectelor secundare … `PRODUCTION_DATA_AFFECTED=NO`"

```
PRODUCTION_DATA_AFFECTED=NO   FINGERPRINTED_TABLES=10   FINGERPRINT_DIFFS=0
AUDIT_ROWS_CLEANED=122        SERVER_LOG_TRACEBACKS=0
```

* **Fără DDL accidental în `public`.** Firmele de probă primesc **scheme dedicate** (prefix
  `proba_p3s_`), create din `tenant_template.sql`. *Motivul e o pățanie a casei, scrisă în
  `masoara_rute_portofoliu.py`: `SET search_path` către o schemă inexistentă e acceptat tăcut de
  PostgreSQL, iar un `CREATE TABLE` necalificat aterizează atunci în `public`.*
* **Fără scrieri persistente neintenționate.** Verificat prin **amprentă**, nu prin `count(*)`:
  `(count, md5(agregat ordonat al md5-urilor pe rând))` pe 10 tabele din `public`, înainte și după.
  **Zero diferențe.**
* **Fără email/webhook/job extern real.** Ruta măsurată e read-only și nu iese din proces. Cele 27
  de căi cu apeluri externe **nu s-au chemat** — de-aia dovada lor e structurală (§0.1).
* **Fără contaminarea tenantului.** Firmele de probă sunt sintetice, iar schemele lor se șterg cu
  `DROP SCHEMA CASCADE`.
* **Curățenie verificată, nu doar făcută.** Și a prins ceva: middleware-ul de audit scrie în
  `public.audit_log` la **fiecare** cerere, deci bancul lăsa în urmă rânduri pentru un utilizator
  sintetic. Amprenta le-a văzut; s-a adăugat `curata_audit()`; **122 de rânduri** șterse la rularea
  finală, amprentă identică după. *Curățenia care „n-are ce lăsa" e o presupunere; amprenta e o
  măsurătoare.*
* **Curățenie și ÎNAINTE**, ca o rulare oprită la mijloc să nu se târască în următoarea.

---

### 5.7 „Baseline de regresie: P2/P3/P4 nu se redeschid"

```
P2_REOPENED=NO   core/test_p2_contract.py + core/test_p2_infrastructura.py   verzi
P3_REOPENED=NO   core/test_p3_wave_a.py + core/test_p3_val_b.py             verzi
                 → cele patru, împreună: 88 passed
P4_REOPENED=NO   core/test_tranzactii_clasificate.py + core/test_p4_fault_injection.py
                 → 48 passed
```

**Cifrele lui P4 sunt neatinse:** 332 candidați bruți, 6+325+1, 7 operații critice, acoperire 7/7.
`scan_blocante.py` e un fișier **separat** de `scan_tranzactii.py` tocmai ca să nu existe drum prin
care P5 să miște un număr al lui P4.

**N-am găsit niciun defect de contract într-o fază anterioară.** Defectul găsit în tura asta e al
**instrumentului meu de măsură din P5**, nu al unei faze închise — v. §5.13, unde e scris ca atare
și nu ascuns sub P5.

---

### 5.8 „Fără remediere în diagnostic … dacă e nevoie de instrumentare în production code: STOP și cere aprobare"

```
BASELINE_COMMIT=8ce4cd84b07f411f458a35cc9b9ff9e9990fbcd1
PRODUCTION_CODE_CHANGED=NO   REQUEST_PATH_CHANGED=NO   RUNTIME_BEHAVIOR_CHANGED=NO
P5_IMPLEMENTATION_STARTED=NO
fișiere de producție atinse față de baseline: niciunul
```

**Derivat, nu declarat:** câmpurile ies din `git diff --name-status <baseline>..HEAD` plus
`git status`, filtrate pe ce ajunge în procesul care servește cereri. Un câmp care spune „n-am
schimbat nimic" și pe care îl scriu tot eu ar fi o promisiune.

**A doua verificare, independentă:** un test cere ca `main.py` să **nu importe** niciunul din
`scan_blocante`, `masoara_p5`, `p5_clasificare`. Diagnosticul nu poate deveni cod viu pe furiș.

**N-a fost nevoie de instrumentare în codul de producție**, deci n-am cerut aprobare. Am ocolit-o
prin construcție: canarul măsoară din **afară**, prin HTTP, iar conexiunile se numără prin
eșantionarea procesului. Singurul lucru pe care nu-l pot vedea așa e ocuparea threadpool-ului — și
l-am declarat nemăsurat (§2), n-am pus instrumentare pentru el.

---

### 5.9 „Trasabilitate: `BASELINE_COMMIT` / `DIAGNOSTIC_CODE_COMMIT` / `P5_FINAL_DIAGNOSTIC_COMMIT` … nu atribui unei suite un commit pe care n-a rulat"

**Cele trei sunt ținute separat**, iar valorile sunt în `masuratori/p5/TRASABILITATE_P5.txt`,
produs **după** ultimul commit — *un raport nu-și poate conține propriul hash.* Fișierul e în ZIP.

```
BASELINE_COMMIT=            8ce4cd84b07f411f458a35cc9b9ff9e9990fbcd1   (pinat de comandă)
DIAGNOSTIC_CODE_COMMIT=     20a10bc6
P5_FINAL_DIAGNOSTIC_COMMIT= v. TRASABILITATE_P5.txt
FULL_SUITE_COMMIT=          v. TRASABILITATE_P5.txt   (== P5_FINAL_DIAGNOSTIC_COMMIT)
```

**Ce s-a schimbat după fiecare rulare de suită, spus exact:** suita **a rulat pe HEAD-ul final**,
adică `scripts/p5_trasabilitate.py` face commitul-raport **întâi** și rulează suita **după**. Deci
`FULL_SUITE_COMMIT == P5_FINAL_DIAGNOSTIC_COMMIT`, iar dacă generatorul găsește că cele două diferă,
**o scrie el, nu eu**.

**Per rezultat important, COMANDA · COMMIT · EXIT_CODE · ARTEFACT BRUT:**

| rezultat | comandă | commit | exit | artefact brut |
|---|---|---|---|---|
| inventar + clasificare + calibrare | `./venv/bin/python scripts/artefacte_p5.py` | `20a10bc6` | **0** | `P5_INVENTAR_BRUT.*` · `P5_CLASIFICARE.*` · `P5_CALLCHAINS.*` · `P5_DETECTOR_CALIBRATION.*` · `acceptare.txt` |
| măsurători + concurență | `./venv/bin/python scripts/masoara_p5.py` | `8ce4cd84` (baseline) | **0** | `P5_MASURATORI.json` · `P5_RAW_EVIDENCE/esantioane.json` · `P5_RAW_EVIDENCE/P5_uvicorn.log` |
| verificator | `./venv/bin/python verificator_conformitate.py` | `20a10bc6` | **0** (`TOTAL: 0 candidate`) | ieșirea, în §7 |
| suita, la poarta de commit | hook `pre-commit` → `pytest` | arborele lui `20a10bc6` | **0** | `4405 passed, 11 skipped, 14 xfailed` în 25:49 |
| suita, finală | `./venv/bin/python -m pytest -q` | `P5_FINAL_DIAGNOSTIC_COMMIT` | v. artefact | `TRASABILITATE_P5.txt` |

**Măsurătorile au rulat pe `8ce4cd84`, adică pe BASELINE, nu pe commitul de diagnostic — și asta e
deliberat, nu o scăpare.** Codul de producție e identic între cele două (`PRODUCTION_CODE_CHANGED=NO`),
deci ruta măsurată e aceeași; iar `P5_MASURATORI.json` poartă câmpul `commit` cu hash-ul exact pe
care a rulat, scris de banc, nu de mine. *O măsurătoare care nu-și poartă commitul nu se poate
atribui.*

---

### 5.10 „Artefacte obligatorii"

Toate în `masuratori/p5/`, toate în ZIP:

| cerut | livrat | cum |
|---|---|---|
| `RAPORT_P5_DIAGNOSTIC.md` | ✔ | fișierul ăsta, în rădăcină, **comis** |
| `P5_INVENTAR_BRUT.*` | ✔ | `.txt` (244 KB) + `.json` (792 KB), comise |
| `P5_CLASIFICARE.*` | ✔ | `.txt` (87 KB) + `.json` (87 KB), comise |
| `P5_CALLCHAINS.*` | ✔ | `.txt` (408 KB) + `.json` (750 KB), comise |
| `P5_MASURATORI.*` | ✔ | `.json`, comis |
| `P5_DETECTOR_CALIBRATION.*` | ✔ | `.txt` + `.json`, comise |
| `P5_RAW_EVIDENCE/` | ✔ | `esantioane.json` (27 serii, **1030 valori**) + `P5_uvicorn.log`, comise |
| `FISIERE_ATINSE.txt` | ✔ | **generat după ultimul commit** de `scripts/p5_trasabilitate`, în ZIP |
| `COMMIT_P5.txt` | ✔ | idem — cele trei commituri, cu subiectul fiecăruia, în ZIP |
| stdout/stderr brut | ✔ | `P5_RAW_EVIDENCE/P5_uvicorn.log` — jurnalul serverului de probă, întreg |
| datele brute ale benchmark-ului | ✔ | `P5_RAW_EVIDENCE/esantioane.json` — fiecare latență, în ms |

*Plus unul necerut: `acceptare.txt`, blocul de cifre al fazei, **generat** de
`scripts/artefacte_p5.py`. Există ca să nu fie nevoie să copiez cifre în raport de mână — și ca
`scripts/p5_trasabilitate` să-și poată verifica singur condițiile de `COMPLETE` citindu-l.*

**De ce trei artefacte se generează abia după ultimul commit:** ele descriu commitul care le
conține, deci înainte de el n-au ce descrie. Merg în ZIP, necomise. Aceeași soluție ca la P4.

---

### 5.11 „Poarta completă: verificator, ruff, teste P5, contracte P2/P3/P4, suită completă, cu cifre exacte"

Toate în **§7**, cu cifrele lor, ca să nu fie scrise de două ori. Pe scurt: verificator **TOTAL: 0
candidate** · `ruff` **All checks passed** · gărzile P5 **31 passed** · contractele P2+P3 **88
passed** · contractele P4 **48 passed** · suita completă, rulată de hook-ul de pre-commit pe
arborele fazei: **4405 passed, 11 skipped, 14 xfailed** în 25:49, apoi **din nou pe HEAD-ul final**
prin `scripts/p5_trasabilitate` (cifrele acolo).

**„Dacă după full suite mai faci un commit doar de artefacte/raport: NU pretinde că suita a rulat pe
noul commit."** Nu pretind, și mai mult — am aranjat să nu fie nevoie: `p5_trasabilitate` rulează
suita **DUPĂ** ultimul commit, deci `FULL_SUITE_COMMIT == P5_FINAL_DIAGNOSTIC_COMMIT` prin
construcție. Iar dacă cele două ar diferi, **generatorul o scrie el**, nu eu. Ce se schimbă după
suita finală: **numai trei fișiere de dovadă** — `TRASABILITATE_P5.txt`, `FISIERE_ATINSE.txt`,
`COMMIT_P5.txt` — care nu pot exista înainte de commitul pe care îl descriu, și care merg în ZIP,
**necomise**. Aceeași soluție ca la P4: *un raport nu-și poate conține propriul hash.*

---

### 5.12 „Raportul final, cu lista de câmpuri obligatorii, `P5_DIAGNOSTIC_COMPLETENESS`, `P5_DIAGNOSTIC_STATUS`, și recomandarea separată"

Fișierul ăsta e raportul. Câmpurile obligatorii sunt derivate, nu scrise: blocul complet e în
`masuratori/p5/acceptare.txt`, generat de `scripts/artefacte_p5.py`, și e reprodus pe secțiuni la
**§5.1** (inventar), **§5.2** (calibrare), **§5.3** (clasificare), **§5.4-5.5** (măsurători și
concurență), **§5.6** (siguranța sondei), **§5.8** (contractul fazei). Cele trei verdicte —
`P5_DIAGNOSTIC_COMPLETENESS`, `P5_DIAGNOSTIC_STATUS`, `P5_IMPLEMENTATION_REQUIRED` — sunt în blocul
**VERDICTUL FAZEI**, la sfârșit, împreună cu valurile.

**Recomandarea e ținută SEPARAT de starea diagnosticului**, cum cere comanda:
`P5_DIAGNOSTIC_STATUS=COMPLETE` descrie ce am măsurat; `P5_IMPLEMENTATION_REQUIRED=YES` e o
recomandare despre ce urmează. A doua nu decurge din prima — un diagnostic complet putea la fel de
bine să iasă `NO`. Motivul pentru care iese `YES` e scris acolo, și e o măsurătoare, nu o impresie.

**Valurile sunt PROPUSE, NEEXECUTATE.** Nicio linie din ele n-a fost scrisă.

---

*Cele **douăsprezece** puncte ale comenzii se termină aici (5.0 e preambulul „citește documentele
canonice"). Ce urmează — 5.13 și 5.14 — **nu sunt puncte primite**: sunt două defecte ale
propriilor mele instrumente, găsite în tura asta. Le pun în §5 și nu în §2 fiindcă schimbă cum se
citesc cifrele de mai sus, iar cine citește §5.4 trebuie să dea peste ele fără să caute.*

---

### 5.13 DEFECTUL PROPRIULUI INSTRUMENT — găsit în tura asta, scris fiindcă schimbă cum se citesc cifrele

Contorul de deadlock-uri adăugat la §5.5 citește jurnalul serverului. La prima rulare cu el:
**`URME_EXCEPTIE=240`**, la un număr de cereri unde așteptam zero.

**Cauza:** martorul sincron cădea cu `psycopg2.errors.UndefinedTable: relation "facturi" does not
exist`. Firma sintetică se construia cu **schemă reală, dar goală** — forma corectă pentru
măsurătoarea P2, unde ramura fără tabele **e** subiectul. Pentru P5 e greșită: ruta de control n-are
ce citi. **Deci cele 40 de cereri ale martorului măsurau cât durează să arunci o excepție.**

**De ce n-am văzut mai devreme:** `curba_sync` înregistra duratele, **nu și statusurile**. *O durată
există și pe 500.* Sonda nu-și asertase premisa, deci raporta liniștit despre o lume pe care n-o
vedea — chiar tiparul pe care casa îl are scris ca interdicție.

**Ce s-a schimbat:** firma de probă se construiește acum cu schemă adevărată; `curba_sync`
înregistrează statusurile; iar măsurătoarea **se refuză** dacă vreo cerere nu e 200, în **ambele**
curbe. Un test cere ca artefactul să arate `UNEXPECTED_STATUSES=0` și `SERVER_LOG_TRACEBACKS=0`.

**Cât de mult schimbă concluzia:** cifra veche a martorului era **7,1 ms**; cea nouă, pe o rută care
chiar reușește și costă cât ruta async, e **3,8 ms**. Adică martorul e acum **mai bun**, nu mai
slab — contrastul cu 117,9 ms e mai net decât înainte. *Dar asta e noroc, nu metodă: putea la fel de
bine să iasă invers, și atunci un raport livrat mai devreme ar fi fost livrat greșit.*

**Nu e un defect al lui P2, P3 sau P4.** E al bancului meu de măsură din P5, apărut în tura asta, și
n-am ascuns nimic sub el.

---

### 5.14 AL DOILEA DEFECT AL INSTRUMENTULUI — direcția opusă, aceeași zi

Cele două căi din valul 2 (`etransport/trimite`, `facturi/{id}/trimite-spv`) erau
`ACTION_REQUIRED` pe C6: „apel de rețea fără `timeout`". **Am verificat la sursă înainte să scriu
despre ele**, cum cere regula de aur. N-a ținut.

**Ce am găsit.** Toate cele **5** aprinderi C6 din întreaga casă erau **același loc**, numărat de
cinci ori prin cinci lanțuri de apel: `core/spv_conector.py:455`,

```python
r = requests.request(metoda, url, headers={...}, **kw)      # în `apel_anaf`
```

La locul apelului nu scrie `timeout`. Dar **toți cei 7 apelanți reali îl trimit prin `**kw`** —
`efactura_send.py:393,400,407,442` și `etransport_send.py:82,89,97`, cu `timeout=30`, `60`, `120`.
Verificat rând cu rând, nu eșantionat.

**Reparația, și ce NU e.** N-am șters detectorul și n-am mutat cele două căi într-o clasă mai blândă
ca să iasă cifra. Am adăugat o **a treia stare**: `PRIN_KW` — *nu se poate decide la locul
apelului*. C6 se aprinde acum numai pe absența **certă**; starea nedecisă se numără separat și intră
în motivul scris al fiecărei căi.

**Riscul rămâne, și e numit în loc să fie stins:** `apel_anaf` **n-are termen implicit**. Un apelant
viitor care uită `timeout=` produce exact defectul pe care C6 îl căuta, iar acum nimic nu-l mai
raportează. *Asta e prețul corectării unui fals-pozitiv, și se scrie ca preț, nu ca victorie.*

**Cele două defecte ale zilei greșesc în direcții OPUSE.** Bancul de măsură **rata** (măsura o cale
de eroare și o raporta ca succes); scanerul **inventa** (raporta un defect care nu există). *Un
instrument care greșește în ambele direcții n-are niciun plafon* — `METODA_VERIFICARE.md` §22. De-aia
niciuna din cele două reparații n-a fost o relaxare de criteriu: prima a adăugat o poartă pe
statusuri, a doua o a treia stare.

**Ce nu s-a schimbat:** `ACTION_REQUIRED` a rămas **46**. Cele două căi n-au ieșit din clasă, s-au
mutat din valul 2 în valul 3, pe altă dovadă.

---

## 6. UNDE SUNTEM

*Derivat cu `scripts/raport_b.py`, rulat după commitul codului de diagnostic. Blocul e mai jos, așa
cum l-a produs instrumentul — nu l-am rescris.*

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
  - **SURSĂ**: R1 — Câte alte acte din corpus sunt PARȚIALE (contor 273) · R104 — Optsprezece reguli din Design System nu numesc nimic: sunt preferințe, nu norme (contor 92) · R107 — Două temeiuri citează un document adus PARȚIAL, deci nu se poate confrunta nimic (contor 73) · R112 — Ianuarie 2026 stă pe un act care nu era în vigoare (contor 64) · R4 — Câte alte forme VECHI din corpus sunt citite ca fiind la zi (contor 273) · R5 — Marcajele din corpus nu se citesc la FOLOSIRE (contor 272) · R6 — Ceva a scris într-un fișier de corpus, și nu se știe ce (contor 272)
  - **VERIFICARE**: R100 — O calibrare care testează doar ce știe instrumentul să caute confirmă presupunerea, nu o verifică (contor 94) · R113 — Opt acte din corpus sunt nevăzute de instrumentele de articol, fiindcă poartă așezarea Monitorului Oficial (contor 62) · R116 — Cronul de alerte numără firmele DUPĂ succes, deci una care ridică nu apare nicăieri (contor 58) · R117 — Un gard al cărui subiect e o mulțime de lucruri NEREZOLVATE se golește când ultimul se rezolvă (contor 57) · R121 — Decontul precompletat (RO e-TVA / P300) nu e accesibil programatic (contor 54) · R122 — O absență la nivel de FUNCȚIE e invizibilă gărzii care lucrează la nivel de MODUL (contor 50) · R15 — Perechile verificator/verificat copiază CONDIȚII, nu doar constante (contor 262) · R16 — Proza care descrie codul poate fi FALSĂ DE LA NAȘTERE (contor 261) · R173 — Douăzeci și trei de temeiuri n-au prag fiindcă nu li se poate citi FRECVENȚA (contor 12) · R175 — Desktopul asistentului e văzut de o probă proprie, nu de uneltele de listă (contor 6) · R176 — „Publicat" a însemnat un singur repo, iar raportul n-a spus care (contor 5) · R177 — Un model de citire poate avea dependențele scrise din memorie, iar sub-invalidarea nu produce niciun semnal (contor 4) · R178 — Pool-ul de conexiuni se saturează exact la 10 cereri de portofoliu simultane (contor 3) · R18 — Două porți verzi care nu pot deveni roșii (contor 255) · R183 — `apel_anaf` ține o tranzacție deschisă peste apelul la ANAF și peste backoff (contor 2) · R23 — Urme de intenție: nume declarate pe care nu le citește nimeni (contor 229) · R24 — Trei cicluri în graful de clustere: reciproce în fapt, sau doar în graf? (contor 228) · R26 — Cota de TVA scrisă ca valoare implicită în 25 de funcții, iar 23 de apeluri o folosesc (contor 223) · R27 — Pragul de reverificare din cod e încă cel global, deși tabelul lui 55 l-a înlocuit azi (contor 220) · R32 — Date de test al căror antet își contrazice propriile linii (contor 213) · R37 — Nota contabilă n-are autor, iar `sursa` ei e un nomenclator de fapt, scris în 48 de locuri (contor 202) · R48 — Patru trasee nu se pot exercita pe nicio firmă, și nimic din afară nu le blochează (contor 186) · R53 — Inventarul de trasee atribuie unei rute tot ce scrie modulul, nu ce scrie ruta (contor 172) · R59 — Reevaluarea schimbă valoarea contabilă, dar registrul care conduce amortizarea rămâne pe cea veche (contor 164) · R67 — Suita de teste rulează pe baza de PRODUCȚIE, iar izolarea e o convenție, nu o barieră (contor 153) · R68 — Suita n-are bază proprie; separarea rămâne de făcut după ce testele se decuplează (contor 151) · R7 — Câte câmpuri obligatorii sunt gardate ca PREZENȚĂ, dar necontrolate ca ADEVĂR (contor 270) · R75 — Joburile de fundal au deadman; procesul care servește ecranele, nu (contor 136) · R76 — „Googlebot" într-un log nu mai e o informație: 70% din cererile care se declară așa sunt scanere (contor 134) · R98 — O interdicție care citează un inventar îmbătrânește singură la fiecare măsurătoare (contor 97) · R99 — Previzualizarea scoaterii unei firme arată ce s-a GĂSIT, dar nu ce s-a VERIFICAT (contor 95)
  - **ARTEFACT**: R114 — Ecranul Intrastat compară fluxurile unui an ales cu pragul de AZI (contor 60) · R174 — O factură încasată prin bancă nu se marchează încasată nicăieri (contor 8) · R3 — Categoria de mărime nu există în aplicație (contor 273) · R64 — Contabilitatea și stocul sunt două evidențe disjuncte, iar niciun document nu le leagă (contor 160) · R69 — O declarație depusă pe un regim care s-a schimbat între timp nu contrazice pe nimeni (contor 149) · R71 — Ce a scos prima exercitare pe date: șapte lucruri pe care nicio gardă nu le vede (contor 148) · R92 — Ecranul nu poate numi cinci din cele opt stări ale unei facturi, iar 10 din 41 afișează azi șirul brut (contor 99) · R95 — Semaforul nu are nicio cale prin care să ceară D100 unei firme pe regim de profit (contor 98) · R97 — „Ruta livrează, ecranul tace": serverul trimite compoziția unei cifre, iar randarea o pierde (contor 97)
  - **ORDINE**: R11 — Datoria veche consemnată doar în proză, în GARZI.md (contor 266) · R14 — Două funcții de creare a facturii, cu stări implicite diferite (contor 262) · R38 — Lista de cote din ecranul de NIR e scrisă de mână, fiindcă serverul n-o poate da (contor 198) · R39 — Coloana pe care se sprijină verificarea D112 nu se scrie de nicăieri (contor 194) · R47 — NIR-ul creează nota contabilă direct validată, sărind peste ciornă (contor 186) · R8 — Cele trei egalități stricte, redeschise și nereverificate (contor 266) · R9 — Ecranul statului de plată: STOP nemișcat (contor 266)
  - ⚠ **a supraviețuit unei ture**: R1 — 273 commituri pe registru · R100 — 94 commituri pe registru · R104 — 92 commituri pe registru · R107 — 73 commituri pe registru · R11 — 266 commituri pe registru · R112 — 64 commituri pe registru · R113 — 62 commituri pe registru · R114 — 60 commituri pe registru · R116 — 58 commituri pe registru · R117 — 57 commituri pe registru · R121 — 54 commituri pe registru · R122 — 50 commituri pe registru · R14 — 262 commituri pe registru · R15 — 262 commituri pe registru · R16 — 261 commituri pe registru · R173 — 12 commituri pe registru · R174 — 8 commituri pe registru · R175 — 6 commituri pe registru · R176 — 5 commituri pe registru · R177 — 4 commituri pe registru · R178 — 3 commituri pe registru · R18 — 255 commituri pe registru · R183 — 2 commituri pe registru · R23 — 229 commituri pe registru · R24 — 228 commituri pe registru · R26 — 223 commituri pe registru · R27 — 220 commituri pe registru · R3 — 273 commituri pe registru · R32 — 213 commituri pe registru · R37 — 202 commituri pe registru · R38 — 198 commituri pe registru · R39 — 194 commituri pe registru · R4 — 273 commituri pe registru · R47 — 186 commituri pe registru · R48 — 186 commituri pe registru · R5 — 272 commituri pe registru · R53 — 172 commituri pe registru · R59 — 164 commituri pe registru · R6 — 272 commituri pe registru · R64 — 160 commituri pe registru · R67 — 153 commituri pe registru · R68 — 151 commituri pe registru · R69 — 149 commituri pe registru · R7 — 270 commituri pe registru · R71 — 148 commituri pe registru · R75 — 136 commituri pe registru · R76 — 134 commituri pe registru · R8 — 266 commituri pe registru · R9 — 266 commituri pe registru · R92 — 99 commituri pe registru · R95 — 98 commituri pe registru · R97 — 97 commituri pe registru · R98 — 97 commituri pe registru · R99 — 95 commituri pe registru
- **restanțe REZOLVATE**: R10 — Cerințe din „Restanțele" (PLAN_LUCRU) fără gardă · R101 — Declarantul e obligatoriu în hartă și nu oprește nicio declarație, iar XML-ul pleacă în numele lui „ADMINISTRATOR" · R102 — D394 declara livrări și zero facturi emise, în același document, iar contradicția o prindea ANAF · R103 — Regula „orice regulă din DS intră simultan în verificator" n-are nicio gardă · R105 — D112 nu-și poate desface cifra: generatorul ei nu întoarce pozițiile, doar XML-ul · R106 — Un temei numește actul care a MODIFICAT articolul, nu actul care îl CONȚINE · R108 — Un prag fiscal are TREI copii, iar cea canonică era greșită și nefolosită · R109 — Pragul de reverificare se calculează, dar raportul lunar folosește tot pragul global · R110 — Pragul Intrastat e în registru, dar actul care îl poartă e un ciot · R111 — Frecvența citește marcaje într-un document care nu le poate purta, și răspunde STABIL · R115 — Tăria constatărilor supervizorului nu e atribuită, deci nimic nu cere confirmare · R118 — Fișierele statice se servesc DE PE DISC: nicio poartă între scriere și producție · R119 — D394 nu-și expune facturile, deci perechea cu e-Factura nu se poate face fără schimbare de generator · R12 — Divergență între D300 și D100 pe aceeași firmă, același fapt · R120 — Identitatea D300 ↔ D394 lit. C nu e verificată rând cu rând · R123 — Trei din cele cinci comparații orizontale n-au gardul „citește ce scrie generatorul" · R124 — Cheltuiala cu impozitul pe profit rămânea nededusă, iar D101 nu spunea nimic · R125 — „Suma de plată" a obligației D100 trăia doar în XML, nu în rândurile persistate · R126 — Poarta confirmării cere o confirmare pe care ECRANUL nu are prin ce s-o dea · R127 — Depunerea se încheia VIZIBIL pe un drum și TĂCUT pe celălalt, cu același buton · R128 — Poarta confirmării cădea DUPĂ aprobare, iar refuzul ei îngusta opțiunile omului · R129 — O filă deschisă de mult rulează modulele de atunci, oricâte publicări trec · R13 — Partener fără cod fiscal pe factură · R130 — Fluxul public de cursuri al BNR nu mai răspunde, iar cursul vechi se folosește tăcut · R131 — Cele 13 descărcări de fișier înlocuiau motivul serverului cu propriul lor număr · R132 — Infrastructura de testare vizuală rula de nouă zile pe bytecode fără sursă · R133 — Două instrumente de măsură citeau JS-ul printr-un cititor care orbea la o linie cu trei ghilimele · R134 — Toate porțile lui `PUT /tenants/{id}` refuzau cu `500`, deci mesajele lor n-au ajuns niciodată la un om · R135 — O denumire de firmă fără nicio literă trecea, și pleca pe `den` în D394 · R136 — Ecranul «Date firmă» trimitea redenumirea ÎNAINTEA a ceea ce putea fi refuzat · R137 — Sonda de ecran număra rânduri, deci era oarbă exact la felul de scriere pe care îl face un ecran de date · R138 — Un `@` nu e o adresă de email: patru rute creau un cont sau trimiteau un email pe orice șir care conținea unul · R139 — Refuzul de pe linia facturii spunea CARE câmp, nu CE e greșit — iar cuvântul pe care îl folosea era fals · R140 — Registrul de încasări și plăți refuza în limba programatorului, și nimeni nu-l putea deschide ca să vadă · R141 — Unsprezece restanțe erau scrise în AFARA blocului pe care îl citește garda, deci nu le-a verificat nimeni · R142 — Pe ecranul de emitere, o cotă de TVA NECUNOSCUTĂ se afișa ca zero, iar «Total» ieșea egal cu «Bază» · R143 — Ecranul de emitere avea două violări de accesibilitate, dintre care una critică, și nimic nu le vedea · R144 — «Aur de investiții» cădea cu `500` pe o puritate care nu e număr, deci refuzul lui n-a existat niciodată · R145 — «Chirii / comodat / refacturări» nu putea reuși NICIODATĂ din ecran: formularul trimitea alt câmp decât cere ruta · R146 — Fix acolo unde verificarea devenea imposibilă, se renunța la ea: o operațiune fără dată trecea · R147 — Șase refuzuri care vorbeau limba programatorului, dintre care unul în patru locuri · R148 — Aceeași achiziție intracomunitară era așezată în declarație pe exigibilitate și i se valida cota pe data facturii · R149 — Două rute validau cota pe o dată pe care legea nu o numește niciodată · R150 — Un cabinet inexistent răspundea „n-a făcut nimic", iar trei rute înlocuiau tăcut o valoare imposibilă cu una convenabilă · R151 — Excepția din art. 291 alin. (5) nu e modelată: aplicația nu poate ști dacă factura sau avansul au precedat livrarea · R152 — Magazinul online se declara „conectat" la o adresă cu care nu vorbise nimeni · R153 — Registratura scria un document într-un an pe care tot ea îl refuză la citire · R154 — „N-am putut trimite" despre un șir care nu era o adresă de email · R155 — „Încearcă o poză mai clară" despre un fișier care nu era o poză · R156 — Ecranul pachetelor acoperea refuzul precis al serverului · R157 — Răspunsul gol la o sesizare: ecranul nu făcea nimic și nu spunea nimic · R158 — Ecranul de recomandare spunea una, bara de sus alta · R159 — „Ciornă salvată." după o salvare care fusese refuzată · R160 — Gardul acoperirii vizuale cerea 16 ecrane din 18, și nimic n-o spunea · R161 — Butonul de casă rămânea stins, iar motivul trăia într-un `title` pe care atingerea nu-l vede · R162 — «Nota a fost creată ca ciornă» se scria și se ștergea în aceeași clipă · R163 — Nota contabilă cădea cu `500` pe un cont PLAUZIBIL, și numai pe unul plauzibil · R164 — Un CNP valid, deja folosit, întorcea `500` în loc de refuz · R165 — SAF-T-ul unei firme TRIMESTRIALE raporta o singură lună din trei · R166 — Validarea D406 din aplicație era INACCESIBILĂ: orice apel ieșea `gri` · R167 — Refuzul spunea că firma depune TRIMESTRIAL și nu spunea pe ce se sprijină · R168 — Gardul de diacritice era verde, la clichet 0, peste un defect pe care lotul 13 îl scrisese · R169 — Scannerul de citări măsura o lume care se micșora cu fiecare temei pus unde trebuie · R17 — Graful de dependențe e cheiat pe NUME SIMPLU, plat peste tot `core/` · R170 — „32 de formulare probate" era spus despre un registru de 34 · R171 — Cele 24 de citări scoase la iveală de R169 n-au nici articol localizabil, nici prag de reverificare · R172 — «Date firmă» cerea periodicitatea TVA fără să spună după ce se alege · R179 — Confirmarea supervizorului putea rămâne scrisă peste o depunere care nu s-a făcut · R180 — Rotația tokenului SPV se pierdea la orice eșec de după ea · R181 — Un e-mail deja plecat putea rămâne fără rândul care îl oprea să plece din nou · R182 — Contul se putea crea fără dovada acordului, iar clientul fără cheia lui de intrare · R19 — `graf_clustere` tratează utilitarele partajate ca proprietate · R2 — Vigoarea PE PUNCT, nu doar pe articol · R20 — Opt artefacte de UN OCTET în corpus, cu nume de declarație · R21 — Forma de înregistrare în contabilitate nu există nicăieri, iar de ea atârnă Cartea mare · R22 — Jurnalul de origine al unei înregistrări e o constantă, și pleacă așa la ANAF · R25 — Module fiscale care NU citează legea, deci rămân în afara domeniului scanului · R28 — Ce trebuie să arate ecranul de angajare, dacă arată ceva · R29 — Cota de TVA ca valoare implicită în ECRAN, care anulează refuzul învățat de server · R30 — Avertismentul de prăpastie al salariului minim, plecat odată cu estimarea · R31 — Anul e scris în cerere, deci ecranul nu poate ajunge la anul curent · R33 — Module de verificare care n-au fost NICIODATĂ legate · R34 — Nota contabilă de salarii contrazice D112-ul depus, pe 10 din 40 de perechi · R35 — Verdict VERDE pe o lună cu factură necontabilizată, cunoscută în chiar payload-ul verdictului · R36 — Cum ajung faptele economice în contabilitate nu e o alegere DECLARATĂ nicăieri · R40 — Nicio declarație depusă prin aplicație, deci lanțul de apărare nu e exercitat niciodată · R41 — Verdictul oficial de validare se produce, se afișează și se aruncă · R42 — 144 de rute care schimbă date nu verifică niciun rol, iar 24 din 24 dintre ele fac contabilitate · R43 — Confirmarea de plată marchează o factură încasată fără să fi intrat un leu, și caută prin toate firmele · R44 — Un element din coadă e legat de o firmă care nu există · R45 — Patru artefacte se produc, se descarcă, și nu rămân nicăieri · R46 — Trecerea de regim fiscal are cea mai mare consecință și cele mai puține verificări · R49 — Avertismentul de prăpastie al salariului minim, desprins din R30 · R50 — Ștergerea unui cabinet nu curăță tabelele partajate, iar datele lui rămân în ele · R51 — Data încetării contractului nu ajungea în bază, iar ruta răspundea 200 · R52 — Un document care ajunge la un om poate pleca pe un GET, iar acolo nu se verifică niciun rol · R54 — Contul contabil venit din corpul cererii nu e confruntat cu planul de conturi · R55 — Aceeași clasă de operațiune contabilă, roluri diferite, fără motiv scris · R56 — Trei rute manipulează credențiale ale unor sisteme externe, fără rol · R57 — Calea de API emite facturi fără poarta de gestiune pe care o are ecranul · R58 — Închiderea perioadei nu verifică nimic, iar redeschiderea nu lasă urmă · R60 — Instrumentul care hrănește verificările atribuia rutei modulul importat de altcineva · R61 — Raportul Z tastat de om nu are verificare de duplicat, iar nota lui intră direct ca evidență · R62 — Clientul își schimbă adresa de autentificare fără confirmare, iar cabinetul nu află nici asta, nici cine a primit acces · R63 — Aceeași persoană are două adrese în aplicație, iar nimic nu le confruntă · R65 — `patron_email` are precedență la trimiterea pachetului și nicio cale de scriere · R66 — `patron_nume` intră în adeverințe și contracte, și nu-l scrie nimic · R70 — O rută poate fi scrisă, gardată și verde, fără ca nimic s-o cheme · R72 — O firmă adăugată din greșeală nu se poate scoate · R73 — Patru trimiteri de email sunt înghițite tăcut, iar trei dintre ele sunt singura cale de intrare · R74 — Trei joburi de fundal sunt oprite de o lună, iar deadman-ul nu se uită la ele · R77 — Divergența de denumire se ARATĂ, dar alegerea nu se CERE · R78 — Actul cel mai distructiv al aplicației stă sub 26 de carduri, iar cine îl caută nu-l găsește · R79 — Ștergerea unei firme își produce propriul orfan, la 78 de milisecunde după ce a terminat · R80 — Pentru 51 din 411 rute, gardul „rută fără apelant" nu poate afirma nimic · R81 — Denumirea unei firme stă în două locuri, iar redenumirea atinge unul singur · R82 — Cele patru acte cu cel mai mare efect asupra unei firme se termină în tăcere · R83 — O firmă dezactivată nu se poate reactiva: poarta de acces o consideră inexistentă · R84 — Trecutul unei firme scoase din portofoliu nu se mai poate citi: 13 rute de raport răspund 404 · R85 — `d112.pull` întoarce un salariat cu CAS, CASS și impozit, dar fără CAM · R86 — Nota de salarii nu înregistrează deloc biletele de valoare, iar salariile brute intră cu altă cifră decât cea declarată · R87 — O factură EMISĂ nu produce nota contabilă; contabilizarea e un act separat, care se poate uita · R88 — O factură PRIMITĂ validată creează cheltuiala, dar nu și nota contabilă · R89 — Stocul de facturi rămase în afara evidenței n-are nici listă revizuită, nici decizie: reconcilierea istorică · R90 — O notă legată de o factură nu se poate dezlega, iar refuzul ștergerii numește o ieșire care nu există · R91 — O factură EMISĂ care intră prin import nu produce nota, iar absența e DECLARATĂ, nu decisă · R93 — Aceeași lipsă e poartă în trei module de declarație și simplu avertisment în al patrulea, iar ANAF respinge XML-ul · R94 — Două mecanisme răspund diferit la „ce datorează firma asta", iar generatorul nu ascultă de niciunul · R96 — Cele trei registre obligatorii citesc trei populații diferite de note, în aceeași lună și pe aceeași firmă
- **antetul, actualizat la**: 2026-09-10

---

## 7. POARTA

| poartă | rezultat |
|---|---|
| `verificator_conformitate.py` | **TOTAL: 0 candidate** |
| `ruff check` (fișierele fazei) | **All checks passed** |
| gărzile P5 | **31 passed** |
| contractele P2 + P3 | **88 passed** |
| contractele P4 | **48 passed** |
| suita completă | v. `TRASABILITATE_P5.txt` — rulată **pe HEAD-ul final** |
| five-way | v. `TRASABILITATE_P5.txt` (HEAD · `origin/main` · `public/main` · backup · proces viu) |
| site | v. `TRASABILITATE_P5.txt` (procesul viu răspunde la `GET /admin/versiune`) |

**O rulare intermediară a suitei, raportată fiindcă a picat.** Înainte de actualizarea registrelor,
suita a dat **2 failed, 4402 passed, 11 skipped, 14 xfailed** în 26:20. Amândouă căderile erau gărzi
de registru care își făceau treaba, nu defecte: `test_garzi_inventar` (blocul generat din `GARZI.md`
spunea 545, instrumentul 547 — două fișiere noi) și `test_module_nelegate` (`core/p5_clasificare.py`
e modul de producție nelegat, deci cere intrare în `PIN` cu motiv scris — exact ce a cerut și
`p4_clasificare.py` la faza precedentă). Amândouă tratate; cifrele finale sunt în
`TRASABILITATE_P5.txt`.

---

## VERDICTUL FAZEI

```
P5_DIAGNOSTIC_COMPLETENESS=COMPLETE
  514 puncte de intrare scanate · 94 candidați bruți · 94 clasificați · 0 neclasificați
  0 goluri de calibrare · 0 excluderi nemotivate · 0 trunchieri de expandare

P5_DIAGNOSTIC_STATUS=  v. TRASABILITATE_P5.txt   (condiționat de suita completă + five-way)

P5_IMPLEMENTATION_REQUIRED=YES
P5_IMPLEMENTATION=NOT_STARTED
```

**`P5_DIAGNOSTIC_STATUS=COMPLETE` NU înseamnă `P5_IMPLEMENTATION=CLOSED`.** Diagnosticul e închis;
remedierea nu e nici măcar începută.

### De ce `P5_IMPLEMENTATION_REQUIRED=YES`

Nu fiindcă există cod blocant — există în orice aplicație. Ci fiindcă **s-a măsurat că doare pe
altcineva**: la k=10, debitul e identic cu cel de la k=1 (22,15 vs 23,05 cereri/s), iar o cerere
străină așteaptă până la 158,7 ms în loc de 3,4 ms. Iar martorul sincron arată că aceeași muncă,
mutată de pe buclă, **nu costă pe nimeni**.

### Valurile de remediere — PROPUSE, NEEXECUTATE

Ordonate după risc și dependențe, nu după mărime.

| val | ce | căi | dovadă | risc | de ce în ordinea asta |
|---|---|---|---|---|---|
| **1** | scoaterea I/O blocant de pe buclă (`run_in_threadpool` sau coadă) | 17 | **MĂSURAT** | **mediu** | dovada cea mai tare; tiparul e deja scris în casă (`_audit_middleware`). Cazul cel mai grav: `time.sleep(1.1)` pe buclă în `core/anaf_api.py:138` |
| **3** | scoaterea apelurilor externe de sub conexiunea ținută | 29 | STRUCTURAL_MĂRGINIT_DAR_RAR | **mare** | atinge tranzacții — deci **redeschide teritoriul lui P4**. Și e **consecința valului 1**: abia după ce bucla se eliberează, pool-ul chiar se lovește de plafon |
| ~~2~~ | ~~termen pe apelurile fără `timeout`~~ | **0** | — | — | **a dispărut în tura asta**: fals-pozitiv al detectorului meu, v. §5.14. Numerotarea o păstrez ca să se vadă că a existat, nu ca s-o ascund |

**Un lucru rămas nerezolvat de valuri, și nu-l trec sub tăcere:** `spv_conector.apel_anaf` n-are
termen **implicit**. Azi toți cei 7 apelanți îl trimit; mâine unul poate să nu-l trimită, și nimic
nu-l va raporta. Nu e o cale din inventar, deci n-are val — dar e o interdicție care s-ar putea
scrie, iar dacă vrei o scriu ca gardă separată în faza de implementare.

**Fiecare val intră cu perechea de măsurători cerută de plan (`:334`):** aceeași sarcină, același N,
p50/p95 **și debitul**, înainte/după. Jumătatea „înainte" e deja produsă și păstrată brut. *O
intervenție care îmbunătățește p50 și înrăutățește p95 nu e o îmbunătățire.*

**Ce NU intră în niciun val**, ca să nu fie citit mai larg decât e: cele **48** de căi
`ACCEPTABLE_BY_DESIGN` — 13 lucrători de fundal, 34 de rute sincrone mărginite, și `lifespan`.
Fiecare are motivul scris în `P5_CLASIFICARE.txt`.

**STOP.** Nu am pornit implementarea P5. Nu am pornit P6.
