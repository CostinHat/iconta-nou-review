RAPORT — P4, TRANSACTION OWNERSHIP | runda de acceptare, 10.09.2026 | `d4127159` → HEAD final

*Prima livrare a fost respinsă cu patru puncte. Raportul ăsta le răspunde punct cu punct și
înlocuiește versiunea de dinainte; contradicțiile din ea sunt numite, nu șterse.*

## 0. CERINTE

**nimic.**

Cele două alegeri de contract — A și B — au primit răspuns: **APROBATE de arhitect în runda de
confirmare din 10.09.2026**, și nu se mai cer. R183 (`apel_anaf` ține o tranzacție deschisă peste
apelul la ANAF) rămâne o **restanță deschisă cu condiție de închidere scrisă** — se închide împreună
cu R178, după ce se măsoară traficul real —, deci nu e o cerință: nu aștept nimic ca s-o pot duce
mai departe.

## 1. CE AM PRESUPUS

1. **`CRITICAL_COMPOSITES` numără OPERAȚIILE critice, nu doar punctele de intrare.** Sunt **7**:
   șase apar ca puncte de intrare în inventarul brut, iar a șaptea —
   `spv_conector.reimprospateaza_token` — e o **cale internă**, cauza a șase dintre ele. Blocul de
   acceptare arată amândouă cifrele, ca să nu fie nevoie să se ghicească pe care o citesc.
   *Contabilitatea inventarului se închide oricum: 6 + 325 + 1 = 332.*
2. **Un raport nu-și poate conține propriul hash.** `FINAL_HEAD` e hash-ul commitului care poartă
   fișierul ăsta, deci nu poate fi scris în el înainte să existe. Am rezolvat-o cu un artefact
   produs **după** commit — `TRASABILITATE_P4.txt`, în pachetul de livrare — care poartă toate
   valorile, plus rularea suitei complete **pe HEAD-ul final**. Blocul din raport le numește și
   trimite acolo. Dacă preferi altă formă, spune-mi și o schimb.

## 2. CE AM FĂCUT ÎN PLUS / MAI PUȚIN

**ÎN PLUS**

- **Am scos pragul cu totul**, nu l-am lărgit. Clasificarea nu mai are „peste prag / sub prag":
  fiecare din cei **332** de candidați bruți primește verdict, regulă și motiv.
- **Motor de reguli pe clase structurale** (`REGULI`), care se aplică pe **faptele derivate** ale
  căii — câte tranzacții, câte scriu, câte scrieri, ce efecte —, nu pe numele ei. Fiecare regulă
  spune ce clasă dă și de ce ține argumentul.
- **Calibrare negativă pe fiecare din C1…C6**, cu **două mutații** care arată că refuzul chiar
  cade (v. §5.1).
- **Artefact nou** — `masuratori/p4/acceptare.txt`, blocul de cifre derivat.

**MAI PUȚIN**

- **Nu am probat prin injecție de defect cele 325 de căi NON_CRITICAL.** Ele au verdict cu motiv și
  regulă, nu probă. Ce le apără e argumentul structural (o tranzacție care nu scrie nu poate lăsa
  stare parțială; interiorul unei tranzacții e tot-sau-nimic) plus gardul care recalculează
  inventarul la fiecare rulare.
- **Nu am măsurat durata** tranzacțiilor deschise peste apeluri externe (R183). Am derivat forma din
  cod; cifra cere trafic real.
- **Injecția de defect e în Python**, nu la nivel de proces: n-am oprit PostgreSQL între `INSERT` și
  `COMMIT`.

## 3. CE AM ACTUALIZAT

| registru | ce s-a scris |
|---|---|
| `CONFORMITATE.md` | antetul la 10.09; R179–R183 rămân cum au fost scrise (R179–R182 REZOLVATE pe `0742e177`, R183 DESCHISĂ) |
| `DECIZII.md` | **A și B: APROBATE de arhitect, 10.09.2026** — starea se schimbă din „luată de mine, cere confirmare" în „confirmată", cu data și cu cine a decis |
| `PLAN_HARDENING.md` | cifrele lui P4, refăcute pe inventarul complet (332 clasificați, nu 32) |
| `TESTE.md` | motorul de reguli, completitudinea și calibrarea negativă pe C1…C6, cu cele două mutații |
| `RAPORT_P4.md` | rescris — fișierul ăsta |
| `GARZI.md`, `PREDARE_LANT.md` | blocurile generate, regenerate ULTIMELE |
| `ISTORIC.md` | **nimic de actualizat, fiindcă** lecția turei e despre instrument și despre prag, iar ea stă în `TESTE.md` și în raport |
| `PLAN_LUCRU.md`, `PLAN_INVESTIGATII.md`, `PLAN_ARHITECTURA.md` | **nimic de actualizat, fiindcă** niciun principiu și nicio regulă de conducere nu s-a schimbat |
| `METODA_VERIFICARE.md` | **nimic de actualizat, fiindcă** metoda folosită e cea scrisă (§22 ambele direcții, §23 structură); ce s-a schimbat e că am aplicat-o pe completitudine, nu doar pe detector |
| `DESIGN_SYSTEM.md`, `MODEL_AUDIT_TENANT.md`, `ISTORIC_TENANTI.md` | **nimic de actualizat, fiindcă** nu s-a atins niciun ecran, nicio fațetă de audit, niciun tenant real |
| `INSTRUMENTE_ROADMAP.md` | **nimic de actualizat, fiindcă** cele 11 instrumente sunt registrul campaniei de gărzi, nu al planului de întărire |
| `anaf_surse/INDEX.json`, `PROVENIENTA.json` | **nimic de actualizat, fiindcă** n-a intrat niciun act normativ în corpus |

## 4. ÎNȚELEGEREA

Patru puncte de închis: **(1)** completitudinea inventarului — fiecare candidat brut are verdict,
fără prag, cu calibrare negativă pe fiecare criteriu care demonstrează **refuzul**, nu doar
observarea; **(2)** A și B sunt aprobate, nu mai sunt cerințe; **(3)** trasabilitate finală, cu
suita rulată pe HEAD-ul final și four-way verificat pe cinci brațe; **(4)** raport fără contradicții,
cu blocul de cifre. Și: **nu porni P5.**

**Ce am înțeles greșit prima dată, și se scrie fiindcă ăsta e chiar punctul 1:** am citit „inventar
brut" ca pe o listă din care aleg ce merită judecat. Nu e. Comanda spune *oricare din C1…C6* —
pragul l-am adăugat eu, iar el a scos din discuție **300 de căi** înainte ca vreo regulă să le fi
atins. Un prag pus înaintea clasificării nu e o economie de efort, e o clasificare nescrisă.

## 5. RĂSPUNS LA COMANDĂ

### 5.1 „COMPLETITUDINEA INVENTARULUI"

**Pragul a dispărut.** Verdictul se dă pe două căi, amândouă trasabile:

- **INDIVIDUAL** — calea are un rând scris în `CLASIFICARE`, cu motivul ei: **34** de căi;
- **PE CLASĂ STRUCTURALĂ** — o regulă din `REGULI`, aplicată pe faptele derivate: **298**.

| regulă | verdict | câte | argumentul |
|---|---|---|---|
| `INDIVIDUAL` | (al rândului scris) | 34 | judecată scrisă, per cale |
| *(niciuna)* | **cere judecată** | 0 rămase | scrieri în >1 tranzacție, commit parțial sau efect ireversibil în tranzacție **nu au regulă de clasă** — pentru ele `None` e răspunsul corect, iar gardul îl face refuz |
| `FARA-SCRIERI` | NON_CRITICAL | 218 | C1 aprinde pe numărul de **frontiere**, nu pe scrieri. O operație care nu scrie nimic nu poate lăsa stare parțială: nu există jumătate de nimic |
| `UN-SINGUR-SCRIITOR` | NON_CRITICAL | 47 | mai multe tranzacții, dar **una singură scrie** (tipic: poarta de acces își deschide propria conexiune de citire). O tranzacție care nu scrie nu poate lăsa stare parțială, deci toate scrierile căii sunt atomice împreună |
| `O-SINGURA-TRANZACTIE` | NON_CRITICAL | 33 | tot actul într-un singur domeniu: C2 și C6 descriu ordinea din **interiorul** unei tranzacții, care se comite întreagă sau deloc |
| `OMONIM` | FALSE_POSITIVE | 0 | ultima plasă, pentru căi despre care nu se poate spune nimic altfel |

**De ce regulile structurale stau ÎNAINTEA celei de omonimie**, și de ce `OMONIM` a rămas la zero:
rezolvarea pe omonimie **adaugă** evenimente, niciodată nu scoate. Deci o concluzie de forma „nicio
scriere" sau „cel mult un domeniu scrie", trasă pe faptele supra-aproximate, rămâne adevărată
**a fortiori** despre calea reală. Un verdict structural e mai tare decât unul de proveniență. *În
prima formă a motorului, cele trei căi purtate de omonimie primeau `FALSE_POSITIVE`; era verdictul
mai slab, și l-am schimbat.*

**CALIBRAREA NEGATIVĂ.** Șase căi sintetice, câte una per criteriu, într-un corpus propriu
(`inventar_din`, ca să nu se scrie nimic în repo). Pentru fiecare se probează **trei** lucruri:

1. criteriul **se aprinde** pe calea lui;
2. calea **intră în inventarul brut** — adică în domeniul care cere clasificare;
3. **mecanismul REFUZĂ**: cu registrul și regulile goale, `clasifica()` o raportează
   `neclasificată`, iar `numaratori()` dă `UNCLASSIFIED_RAW_CANDIDATES = 1`. *Adică poarta ar cădea.*

Și o a patra probă, pinată: cu regulile **reale**, fiecare cale sintetică fie primește o clasă, fie
e **trimisă la judecată scrisă** (`None`). Trei din șase merg pe a doua ramură — și aia nu e o
scăpare, e refuzul de a absorbi pe clasă exact căile pentru care clasificarea individuală există.

**Implicațiile dintre criterii, măsurate — nu presupuse.** „NUMAI C4" și „NUMAI C5" nu există prin
construcție, și mulțimile sunt **pinate în probă**, ca o schimbare de definiție să pice:

| criteriu | mulțimea aprinsă de calea minimă | de ce |
|---|---|---|
| C1 | `{C1}` | se izolează |
| C2 | `{C2}` | se izolează |
| C3 | `{C3}` | se izolează |
| C4 | `{C2, C4}` | C4 cere o scriere în sursă **și** una în modelul de citire = ≥2 tabele, care e chiar C2 |
| C5 | `{C1, C5, C6}` | două domenii care scriu sunt două frontiere (C1), iar între cele două scrieri stă închiderea unui domeniu (C6) |
| C6 | `{C3, C6}` | ce poate sta între două scrieri e o frontieră (C1) sau un efect (C3) |

**Că refuzul chiar cade, probat prin mutație — de două ori:**

- **mutația 1** — `verdict()` întoarce o clasă implicită în loc de `None`: **3 din 6** probe de refuz
  devin roșii (C1, C2, C4). Celelalte trei supraviețuiesc fiindcă le oprește mai devreme
  `_cere_individual`;
- **mutația 2** — și `_cere_individual()` întoarce mereu `False`: **toate 6** devin roșii, plus 3
  probe de rutare. *Fără a doua mutație, aș fi crezut că prima acoperă tot.*

**Cifrele:** `RAW_CANDIDATES = CLASSIFIED_CANDIDATES = 332` · `UNCLASSIFIED_RAW_CANDIDATES = 0` ·
`UNEXPLAINED_EXCLUSIONS = 0`. Artefactul cu **toate** cele 332 de rânduri, fiecare cu verdict,
regulă și motiv, e `masuratori/p4/clasificare.txt`.

**Semnele, pe inventarul final:** C1 **316** · C2 **57** · C3 **47** · C4 **0** · C5 **22** ·
C6 **30**. *(C4 = 0 e un rezultat: invalidarea modelului de citire se face prin triggere pe
tabelele-sursă, deci nicio cale de aplicație nu scrie în sursă și în model în aceeași operație.)*

### 5.2 „DECIZIILE DE CONTRACT A ȘI B"

**`P4_CONTRACT_DECISION_A = APPROVED`** — la `409 CONSTATARI_NECONFIRMATE`, confirmările din cerere
NU persistă.

**`P4_CONTRACT_DECISION_B = APPROVED`** — notificarea de scadență are semantică **AT-MOST-ONCE**;
riscul acceptat explicit e notificarea **pierdută**, nu duplicată.

**Aprobarea aparține arhitectului (Costin) și a fost dată în runda de confirmare din 10.09.2026.**
Scris ca atare în `DECIZII.md`, unde starea trece din „luată de mine" în „confirmată" — deosebirea
contează, fiindcă a doua cere să i se ceară din nou ca să se răstoarne, prima nu.

### 5.3 „TRASABILITATE FINALĂ"

Suita completă rulează pe **HEAD-ul final**, după ultimul commit, iar rezultatul plus cele cinci
brațe se scriu în `masuratori/p4/TRASABILITATE_P4.txt`, produs de `scripts/p4_trasabilitate.py` —
care e în repo, deci măsurătoarea se poate reface, chiar dacă artefactul ei nu poate exista înainte
de commitul pe care îl descrie. Valorile sunt în
blocul de la §5.5 și în artefact. `LIVE_PROCESS_COMMIT` se citește din procesul viu, nu se presupune.

Regula pe care o respect: dacă oricare braț nu se poate verifica sau diferă,
`FOUR_WAY_STATUS = FAIL` și `P4_STATUS = NOT_ACCEPTED`. Nu declar „închis" pe un braț necitit.

### 5.4 „RAPORT FINAL — corectează toate contradicțiile"

| contradicție | ce era | ce e |
|---|---|---|
| **24 vs 27 NON_CRITICAL** | prima livrare a scris 24 (cifră purtată de la altă măsurătoare), apoi 27 | **325** — și cifra veche n-a fost doar greșită, ci **măsura altceva**: NON_CRITICAL peste un prag pe care l-am inventat. Fără prag, clasa are 325 de membri |
| **32 de căi clasificate** | „32 peste prag" | **332**, adică toți candidații bruți |
| **referințe la un HEAD vechi** | raportul vechi purta `a05618ce → 0742e177` | raportul ăsta pleacă de la `d4127159` și se închide pe HEAD-ul final, scris în blocul de la §5.5 |
| **suita atribuită altui commit** | „4347 passed … rularea care a produs `0742e177`" — adevărat, dar era rularea de **dinaintea** commitului | acum: o rulare completă **pe HEAD-ul final**, cu `FULL_SUITE_COMMIT == FINAL_HEAD` |
| **cifre de inventar vs artefacte** | blocul de semne era dinaintea ultimei reparații | toate cifrele din raportul ăsta sunt cele din `masuratori/p4/acceptare.txt`, generat la ultima rulare |
| **`.commit()` 170 → 168** | corectat deja în tura precedentă | rămâne **170 → 170**: `main.py` 68→67, `alerta_acces` 1→0, `spv_conector` 0→**2** (acolo commitul **este** reparația) |

### 5.5 BLOCUL DE ACCEPTARE

*Cifrele de inventar și de clasificare sunt derivate cu `./venv/bin/python -m scripts.p4_artefacte`
și scrise în `masuratori/p4/acceptare.txt`. Cele de trasabilitate se măsoară după ultimul commit și
se scriu în `TRASABILITATE_P4.txt`, în pachetul de livrare — un raport nu-și poate conține propriul
hash.*

```
RAW_CANDIDATES=332
CLASSIFIED_CANDIDATES=332

CRITICAL_COMPOSITES=7            (6 puncte de intrare + 1 cale internă)
NON_CRITICAL_COMPOSITES=325
FALSE_POSITIVES=1

UNCLASSIFIED_RAW_CANDIDATES=0
UNTESTED_CRITICAL_COMPOSITES=0
UNEXPLAINED_EXCLUSIONS=0

TRANSACTION_OWNERSHIP_GAPS=0
PARTIAL_COMMIT_PATHS=0
PARTIAL_STATE_AFTER_FAULT=0

P4_CONTRACT_DECISION_A=APPROVED
P4_CONTRACT_DECISION_B=APPROVED

P4_CRITICAL_OPERATION_INVENTORY=MECHANICALLY_DERIVED · COMPLETE
P4_FAULT_INJECTION_COVERAGE=COMPLETE

FINAL_HEAD=            v. TRASABILITATE_P4.txt
FULL_SUITE_COMMIT=     v. TRASABILITATE_P4.txt
FULL_SUITE_PASSED=     v. TRASABILITATE_P4.txt
FULL_SUITE_FAILED=     v. TRASABILITATE_P4.txt
FULL_SUITE_EXIT_CODE=  v. TRASABILITATE_P4.txt

HEAD=                  v. TRASABILITATE_P4.txt
ORIGIN_MAIN=           v. TRASABILITATE_P4.txt
PUBLIC_MAIN=           v. TRASABILITATE_P4.txt
BACKUP=                v. TRASABILITATE_P4.txt
LIVE_PROCESS_COMMIT=   v. TRASABILITATE_P4.txt

FOUR_WAY_STATUS=       v. TRASABILITATE_P4.txt
P4_STATUS=             v. TRASABILITATE_P4.txt
```

**Ce înseamnă cele trei zerouri de mijloc, ca să nu fie citite mai larg decât sunt:**
`TRANSACTION_OWNERSHIP_GAPS = 0` și `PARTIAL_COMMIT_PATHS = 0` numără **căile rămase fără verdict
scris** — nu spun că aplicația n-are nicio cale cu scrieri în mai multe tranzacții. Are **22**, și
fiecare are un rând care spune de ce e așa. `PARTIAL_STATE_AFTER_FAULT = 0` e măsurat prin cele
**șapte** probe de injecție, pe stare comparată prin **amprentă**.

### 5.6 „Nu porni P5"

Nepornit. `PLAN_HARDENING.md` marchează P5 ca **URMĂTORUL**, nedeschis; nicio linie din el n-a fost
atinsă.

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
  - **SURSĂ**: R1 — Câte alte acte din corpus sunt PARȚIALE (contor 272) · R104 — Optsprezece reguli din Design System nu numesc nimic: sunt preferințe, nu norme (contor 91) · R107 — Două temeiuri citează un document adus PARȚIAL, deci nu se poate confrunta nimic (contor 72) · R112 — Ianuarie 2026 stă pe un act care nu era în vigoare (contor 63) · R4 — Câte alte forme VECHI din corpus sunt citite ca fiind la zi (contor 272) · R5 — Marcajele din corpus nu se citesc la FOLOSIRE (contor 271) · R6 — Ceva a scris într-un fișier de corpus, și nu se știe ce (contor 271)
  - **VERIFICARE**: R100 — O calibrare care testează doar ce știe instrumentul să caute confirmă presupunerea, nu o verifică (contor 93) · R113 — Opt acte din corpus sunt nevăzute de instrumentele de articol, fiindcă poartă așezarea Monitorului Oficial (contor 61) · R116 — Cronul de alerte numără firmele DUPĂ succes, deci una care ridică nu apare nicăieri (contor 57) · R117 — Un gard al cărui subiect e o mulțime de lucruri NEREZOLVATE se golește când ultimul se rezolvă (contor 56) · R121 — Decontul precompletat (RO e-TVA / P300) nu e accesibil programatic (contor 53) · R122 — O absență la nivel de FUNCȚIE e invizibilă gărzii care lucrează la nivel de MODUL (contor 49) · R15 — Perechile verificator/verificat copiază CONDIȚII, nu doar constante (contor 261) · R16 — Proza care descrie codul poate fi FALSĂ DE LA NAȘTERE (contor 260) · R173 — Douăzeci și trei de temeiuri n-au prag fiindcă nu li se poate citi FRECVENȚA (contor 11) · R175 — Desktopul asistentului e văzut de o probă proprie, nu de uneltele de listă (contor 5) · R176 — „Publicat" a însemnat un singur repo, iar raportul n-a spus care (contor 4) · R177 — Un model de citire poate avea dependențele scrise din memorie, iar sub-invalidarea nu produce niciun semnal (contor 3) · R178 — Pool-ul de conexiuni se saturează exact la 10 cereri de portofoliu simultane (contor 2) · R18 — Două porți verzi care nu pot deveni roșii (contor 254) · R183 — `apel_anaf` ține o tranzacție deschisă peste apelul la ANAF și peste backoff (contor 1) · R23 — Urme de intenție: nume declarate pe care nu le citește nimeni (contor 228) · R24 — Trei cicluri în graful de clustere: reciproce în fapt, sau doar în graf? (contor 227) · R26 — Cota de TVA scrisă ca valoare implicită în 25 de funcții, iar 23 de apeluri o folosesc (contor 222) · R27 — Pragul de reverificare din cod e încă cel global, deși tabelul lui 55 l-a înlocuit azi (contor 219) · R32 — Date de test al căror antet își contrazice propriile linii (contor 212) · R37 — Nota contabilă n-are autor, iar `sursa` ei e un nomenclator de fapt, scris în 48 de locuri (contor 201) · R48 — Patru trasee nu se pot exercita pe nicio firmă, și nimic din afară nu le blochează (contor 185) · R53 — Inventarul de trasee atribuie unei rute tot ce scrie modulul, nu ce scrie ruta (contor 171) · R59 — Reevaluarea schimbă valoarea contabilă, dar registrul care conduce amortizarea rămâne pe cea veche (contor 163) · R67 — Suita de teste rulează pe baza de PRODUCȚIE, iar izolarea e o convenție, nu o barieră (contor 152) · R68 — Suita n-are bază proprie; separarea rămâne de făcut după ce testele se decuplează (contor 150) · R7 — Câte câmpuri obligatorii sunt gardate ca PREZENȚĂ, dar necontrolate ca ADEVĂR (contor 269) · R75 — Joburile de fundal au deadman; procesul care servește ecranele, nu (contor 135) · R76 — „Googlebot" într-un log nu mai e o informație: 70% din cererile care se declară așa sunt scanere (contor 133) · R98 — O interdicție care citează un inventar îmbătrânește singură la fiecare măsurătoare (contor 96) · R99 — Previzualizarea scoaterii unei firme arată ce s-a GĂSIT, dar nu ce s-a VERIFICAT (contor 94)
  - **ARTEFACT**: R114 — Ecranul Intrastat compară fluxurile unui an ales cu pragul de AZI (contor 59) · R174 — O factură încasată prin bancă nu se marchează încasată nicăieri (contor 7) · R3 — Categoria de mărime nu există în aplicație (contor 272) · R64 — Contabilitatea și stocul sunt două evidențe disjuncte, iar niciun document nu le leagă (contor 159) · R69 — O declarație depusă pe un regim care s-a schimbat între timp nu contrazice pe nimeni (contor 148) · R71 — Ce a scos prima exercitare pe date: șapte lucruri pe care nicio gardă nu le vede (contor 147) · R92 — Ecranul nu poate numi cinci din cele opt stări ale unei facturi, iar 10 din 41 afișează azi șirul brut (contor 98) · R95 — Semaforul nu are nicio cale prin care să ceară D100 unei firme pe regim de profit (contor 97) · R97 — „Ruta livrează, ecranul tace": serverul trimite compoziția unei cifre, iar randarea o pierde (contor 96)
  - **ORDINE**: R11 — Datoria veche consemnată doar în proză, în GARZI.md (contor 265) · R14 — Două funcții de creare a facturii, cu stări implicite diferite (contor 261) · R38 — Lista de cote din ecranul de NIR e scrisă de mână, fiindcă serverul n-o poate da (contor 197) · R39 — Coloana pe care se sprijină verificarea D112 nu se scrie de nicăieri (contor 193) · R47 — NIR-ul creează nota contabilă direct validată, sărind peste ciornă (contor 185) · R8 — Cele trei egalități stricte, redeschise și nereverificate (contor 265) · R9 — Ecranul statului de plată: STOP nemișcat (contor 265)
  - ⚠ **a supraviețuit unei ture**: R1 — 272 commituri pe registru · R100 — 93 commituri pe registru · R104 — 91 commituri pe registru · R107 — 72 commituri pe registru · R11 — 265 commituri pe registru · R112 — 63 commituri pe registru · R113 — 61 commituri pe registru · R114 — 59 commituri pe registru · R116 — 57 commituri pe registru · R117 — 56 commituri pe registru · R121 — 53 commituri pe registru · R122 — 49 commituri pe registru · R14 — 261 commituri pe registru · R15 — 261 commituri pe registru · R16 — 260 commituri pe registru · R173 — 11 commituri pe registru · R174 — 7 commituri pe registru · R175 — 5 commituri pe registru · R176 — 4 commituri pe registru · R177 — 3 commituri pe registru · R178 — 2 commituri pe registru · R18 — 254 commituri pe registru · R23 — 228 commituri pe registru · R24 — 227 commituri pe registru · R26 — 222 commituri pe registru · R27 — 219 commituri pe registru · R3 — 272 commituri pe registru · R32 — 212 commituri pe registru · R37 — 201 commituri pe registru · R38 — 197 commituri pe registru · R39 — 193 commituri pe registru · R4 — 272 commituri pe registru · R47 — 185 commituri pe registru · R48 — 185 commituri pe registru · R5 — 271 commituri pe registru · R53 — 171 commituri pe registru · R59 — 163 commituri pe registru · R6 — 271 commituri pe registru · R64 — 159 commituri pe registru · R67 — 152 commituri pe registru · R68 — 150 commituri pe registru · R69 — 148 commituri pe registru · R7 — 269 commituri pe registru · R71 — 147 commituri pe registru · R75 — 135 commituri pe registru · R76 — 133 commituri pe registru · R8 — 265 commituri pe registru · R9 — 265 commituri pe registru · R92 — 98 commituri pe registru · R95 — 97 commituri pe registru · R97 — 96 commituri pe registru · R98 — 96 commituri pe registru · R99 — 94 commituri pe registru
- **restanțe REZOLVATE**: R10 — Cerințe din „Restanțele" (PLAN_LUCRU) fără gardă · R101 — Declarantul e obligatoriu în hartă și nu oprește nicio declarație, iar XML-ul pleacă în numele lui „ADMINISTRATOR" · R102 — D394 declara livrări și zero facturi emise, în același document, iar contradicția o prindea ANAF · R103 — Regula „orice regulă din DS intră simultan în verificator" n-are nicio gardă · R105 — D112 nu-și poate desface cifra: generatorul ei nu întoarce pozițiile, doar XML-ul · R106 — Un temei numește actul care a MODIFICAT articolul, nu actul care îl CONȚINE · R108 — Un prag fiscal are TREI copii, iar cea canonică era greșită și nefolosită · R109 — Pragul de reverificare se calculează, dar raportul lunar folosește tot pragul global · R110 — Pragul Intrastat e în registru, dar actul care îl poartă e un ciot · R111 — Frecvența citește marcaje într-un document care nu le poate purta, și răspunde STABIL · R115 — Tăria constatărilor supervizorului nu e atribuită, deci nimic nu cere confirmare · R118 — Fișierele statice se servesc DE PE DISC: nicio poartă între scriere și producție · R119 — D394 nu-și expune facturile, deci perechea cu e-Factura nu se poate face fără schimbare de generator · R12 — Divergență între D300 și D100 pe aceeași firmă, același fapt · R120 — Identitatea D300 ↔ D394 lit. C nu e verificată rând cu rând · R123 — Trei din cele cinci comparații orizontale n-au gardul „citește ce scrie generatorul" · R124 — Cheltuiala cu impozitul pe profit rămânea nededusă, iar D101 nu spunea nimic · R125 — „Suma de plată" a obligației D100 trăia doar în XML, nu în rândurile persistate · R126 — Poarta confirmării cere o confirmare pe care ECRANUL nu are prin ce s-o dea · R127 — Depunerea se încheia VIZIBIL pe un drum și TĂCUT pe celălalt, cu același buton · R128 — Poarta confirmării cădea DUPĂ aprobare, iar refuzul ei îngusta opțiunile omului · R129 — O filă deschisă de mult rulează modulele de atunci, oricâte publicări trec · R13 — Partener fără cod fiscal pe factură · R130 — Fluxul public de cursuri al BNR nu mai răspunde, iar cursul vechi se folosește tăcut · R131 — Cele 13 descărcări de fișier înlocuiau motivul serverului cu propriul lor număr · R132 — Infrastructura de testare vizuală rula de nouă zile pe bytecode fără sursă · R133 — Două instrumente de măsură citeau JS-ul printr-un cititor care orbea la o linie cu trei ghilimele · R134 — Toate porțile lui `PUT /tenants/{id}` refuzau cu `500`, deci mesajele lor n-au ajuns niciodată la un om · R135 — O denumire de firmă fără nicio literă trecea, și pleca pe `den` în D394 · R136 — Ecranul «Date firmă» trimitea redenumirea ÎNAINTEA a ceea ce putea fi refuzat · R137 — Sonda de ecran număra rânduri, deci era oarbă exact la felul de scriere pe care îl face un ecran de date · R138 — Un `@` nu e o adresă de email: patru rute creau un cont sau trimiteau un email pe orice șir care conținea unul · R139 — Refuzul de pe linia facturii spunea CARE câmp, nu CE e greșit — iar cuvântul pe care îl folosea era fals · R140 — Registrul de încasări și plăți refuza în limba programatorului, și nimeni nu-l putea deschide ca să vadă · R141 — Unsprezece restanțe erau scrise în AFARA blocului pe care îl citește garda, deci nu le-a verificat nimeni · R142 — Pe ecranul de emitere, o cotă de TVA NECUNOSCUTĂ se afișa ca zero, iar «Total» ieșea egal cu «Bază» · R143 — Ecranul de emitere avea două violări de accesibilitate, dintre care una critică, și nimic nu le vedea · R144 — «Aur de investiții» cădea cu `500` pe o puritate care nu e număr, deci refuzul lui n-a existat niciodată · R145 — «Chirii / comodat / refacturări» nu putea reuși NICIODATĂ din ecran: formularul trimitea alt câmp decât cere ruta · R146 — Fix acolo unde verificarea devenea imposibilă, se renunța la ea: o operațiune fără dată trecea · R147 — Șase refuzuri care vorbeau limba programatorului, dintre care unul în patru locuri · R148 — Aceeași achiziție intracomunitară era așezată în declarație pe exigibilitate și i se valida cota pe data facturii · R149 — Două rute validau cota pe o dată pe care legea nu o numește niciodată · R150 — Un cabinet inexistent răspundea „n-a făcut nimic", iar trei rute înlocuiau tăcut o valoare imposibilă cu una convenabilă · R151 — Excepția din art. 291 alin. (5) nu e modelată: aplicația nu poate ști dacă factura sau avansul au precedat livrarea · R152 — Magazinul online se declara „conectat" la o adresă cu care nu vorbise nimeni · R153 — Registratura scria un document într-un an pe care tot ea îl refuză la citire · R154 — „N-am putut trimite" despre un șir care nu era o adresă de email · R155 — „Încearcă o poză mai clară" despre un fișier care nu era o poză · R156 — Ecranul pachetelor acoperea refuzul precis al serverului · R157 — Răspunsul gol la o sesizare: ecranul nu făcea nimic și nu spunea nimic · R158 — Ecranul de recomandare spunea una, bara de sus alta · R159 — „Ciornă salvată." după o salvare care fusese refuzată · R160 — Gardul acoperirii vizuale cerea 16 ecrane din 18, și nimic n-o spunea · R161 — Butonul de casă rămânea stins, iar motivul trăia într-un `title` pe care atingerea nu-l vede · R162 — «Nota a fost creată ca ciornă» se scria și se ștergea în aceeași clipă · R163 — Nota contabilă cădea cu `500` pe un cont PLAUZIBIL, și numai pe unul plauzibil · R164 — Un CNP valid, deja folosit, întorcea `500` în loc de refuz · R165 — SAF-T-ul unei firme TRIMESTRIALE raporta o singură lună din trei · R166 — Validarea D406 din aplicație era INACCESIBILĂ: orice apel ieșea `gri` · R167 — Refuzul spunea că firma depune TRIMESTRIAL și nu spunea pe ce se sprijină · R168 — Gardul de diacritice era verde, la clichet 0, peste un defect pe care lotul 13 îl scrisese · R169 — Scannerul de citări măsura o lume care se micșora cu fiecare temei pus unde trebuie · R17 — Graful de dependențe e cheiat pe NUME SIMPLU, plat peste tot `core/` · R170 — „32 de formulare probate" era spus despre un registru de 34 · R171 — Cele 24 de citări scoase la iveală de R169 n-au nici articol localizabil, nici prag de reverificare · R172 — «Date firmă» cerea periodicitatea TVA fără să spună după ce se alege · R179 — Confirmarea supervizorului putea rămâne scrisă peste o depunere care nu s-a făcut · R180 — Rotația tokenului SPV se pierdea la orice eșec de după ea · R181 — Un e-mail deja plecat putea rămâne fără rândul care îl oprea să plece din nou · R182 — Contul se putea crea fără dovada acordului, iar clientul fără cheia lui de intrare · R19 — `graf_clustere` tratează utilitarele partajate ca proprietate · R2 — Vigoarea PE PUNCT, nu doar pe articol · R20 — Opt artefacte de UN OCTET în corpus, cu nume de declarație · R21 — Forma de înregistrare în contabilitate nu există nicăieri, iar de ea atârnă Cartea mare · R22 — Jurnalul de origine al unei înregistrări e o constantă, și pleacă așa la ANAF · R25 — Module fiscale care NU citează legea, deci rămân în afara domeniului scanului · R28 — Ce trebuie să arate ecranul de angajare, dacă arată ceva · R29 — Cota de TVA ca valoare implicită în ECRAN, care anulează refuzul învățat de server · R30 — Avertismentul de prăpastie al salariului minim, plecat odată cu estimarea · R31 — Anul e scris în cerere, deci ecranul nu poate ajunge la anul curent · R33 — Module de verificare care n-au fost NICIODATĂ legate · R34 — Nota contabilă de salarii contrazice D112-ul depus, pe 10 din 40 de perechi · R35 — Verdict VERDE pe o lună cu factură necontabilizată, cunoscută în chiar payload-ul verdictului · R36 — Cum ajung faptele economice în contabilitate nu e o alegere DECLARATĂ nicăieri · R40 — Nicio declarație depusă prin aplicație, deci lanțul de apărare nu e exercitat niciodată · R41 — Verdictul oficial de validare se produce, se afișează și se aruncă · R42 — 144 de rute care schimbă date nu verifică niciun rol, iar 24 din 24 dintre ele fac contabilitate · R43 — Confirmarea de plată marchează o factură încasată fără să fi intrat un leu, și caută prin toate firmele · R44 — Un element din coadă e legat de o firmă care nu există · R45 — Patru artefacte se produc, se descarcă, și nu rămân nicăieri · R46 — Trecerea de regim fiscal are cea mai mare consecință și cele mai puține verificări · R49 — Avertismentul de prăpastie al salariului minim, desprins din R30 · R50 — Ștergerea unui cabinet nu curăță tabelele partajate, iar datele lui rămân în ele · R51 — Data încetării contractului nu ajungea în bază, iar ruta răspundea 200 · R52 — Un document care ajunge la un om poate pleca pe un GET, iar acolo nu se verifică niciun rol · R54 — Contul contabil venit din corpul cererii nu e confruntat cu planul de conturi · R55 — Aceeași clasă de operațiune contabilă, roluri diferite, fără motiv scris · R56 — Trei rute manipulează credențiale ale unor sisteme externe, fără rol · R57 — Calea de API emite facturi fără poarta de gestiune pe care o are ecranul · R58 — Închiderea perioadei nu verifică nimic, iar redeschiderea nu lasă urmă · R60 — Instrumentul care hrănește verificările atribuia rutei modulul importat de altcineva · R61 — Raportul Z tastat de om nu are verificare de duplicat, iar nota lui intră direct ca evidență · R62 — Clientul își schimbă adresa de autentificare fără confirmare, iar cabinetul nu află nici asta, nici cine a primit acces · R63 — Aceeași persoană are două adrese în aplicație, iar nimic nu le confruntă · R65 — `patron_email` are precedență la trimiterea pachetului și nicio cale de scriere · R66 — `patron_nume` intră în adeverințe și contracte, și nu-l scrie nimic · R70 — O rută poate fi scrisă, gardată și verde, fără ca nimic s-o cheme · R72 — O firmă adăugată din greșeală nu se poate scoate · R73 — Patru trimiteri de email sunt înghițite tăcut, iar trei dintre ele sunt singura cale de intrare · R74 — Trei joburi de fundal sunt oprite de o lună, iar deadman-ul nu se uită la ele · R77 — Divergența de denumire se ARATĂ, dar alegerea nu se CERE · R78 — Actul cel mai distructiv al aplicației stă sub 26 de carduri, iar cine îl caută nu-l găsește · R79 — Ștergerea unei firme își produce propriul orfan, la 78 de milisecunde după ce a terminat · R80 — Pentru 51 din 411 rute, gardul „rută fără apelant" nu poate afirma nimic · R81 — Denumirea unei firme stă în două locuri, iar redenumirea atinge unul singur · R82 — Cele patru acte cu cel mai mare efect asupra unei firme se termină în tăcere · R83 — O firmă dezactivată nu se poate reactiva: poarta de acces o consideră inexistentă · R84 — Trecutul unei firme scoase din portofoliu nu se mai poate citi: 13 rute de raport răspund 404 · R85 — `d112.pull` întoarce un salariat cu CAS, CASS și impozit, dar fără CAM · R86 — Nota de salarii nu înregistrează deloc biletele de valoare, iar salariile brute intră cu altă cifră decât cea declarată · R87 — O factură EMISĂ nu produce nota contabilă; contabilizarea e un act separat, care se poate uita · R88 — O factură PRIMITĂ validată creează cheltuiala, dar nu și nota contabilă · R89 — Stocul de facturi rămase în afara evidenței n-are nici listă revizuită, nici decizie: reconcilierea istorică · R90 — O notă legată de o factură nu se poate dezlega, iar refuzul ștergerii numește o ieșire care nu există · R91 — O factură EMISĂ care intră prin import nu produce nota, iar absența e DECLARATĂ, nu decisă · R93 — Aceeași lipsă e poartă în trei module de declarație și simplu avertisment în al patrulea, iar ANAF respinge XML-ul · R94 — Două mecanisme răspund diferit la „ce datorează firma asta", iar generatorul nu ascultă de niciunul · R96 — Cele trei registre obligatorii citesc trei populații diferite de note, în aceeași lună și pe aceeași firmă
- **antetul, actualizat la**: 2026-09-10

## 7. POARTA

**Poarta commitului care poartă raportul ăsta** e mai jos; **rularea pe HEAD-ul final**, cerută la
punctul 3, e în `TRASABILITATE_P4.txt` din pachetul de livrare, fiindcă se face după commit.

`pre-commit` rulează **suita întreagă** la fiecare commit — inclusiv la unul numai de registre.
Regula 5 din `PLAN_LUCRU.md` (perimetru scurt când nu se atinge cod) e pentru rulările **de mână**;
hookul nu o folosește, deliberat: *o poartă care depinde de ce comandă tastezi nu e poartă*.

**Ce se verifică, și unde sunt cifrele.** Poarta acestui commit rulează suita întreagă plus
verificatorul, iar `post-commit` închide four-way-ul și publică pe amândouă remote-urile. Cifrele
măsurate — ale rulării **pe HEAD-ul final**, cerută la punctul 3 — sunt în `TRASABILITATE_P4.txt`
din pachetul de livrare, împreună cu cele cinci brațe citite unul câte unul, inclusiv commitul
**procesului viu**, citit din proces, nu presupus.

Nu scriu aici cifre pe care nu le pot avea la scriere: o rulare nu poate fi atribuită unui commit
care încă nu există. *Prima livrare a făcut exact asta — a numit rularea de dinaintea commitului
drept «rularea care a produs commitul» —, iar punctul 3 al respingerii e chiar despre asta.*

**Istoria porții în tura asta, ca să nu se citească nimic mai bine decât a fost.** Poarta a respins
de patru ori în prima rundă, și de fiecare dată a avut dreptate: o reparație a mea care **bloca**
(a doua conexiune pe același rând), trei gărzi de igienă, doi orfani lăsați de propriile mele probe,
și ziua schimbată sub tură. Amănuntele au rămas scrise în restanțe și în `TESTE.md`; se numesc aici
fiindcă un raport care arată numai rularea verde de la capăt ascunde exact partea care a produs
calitatea.
