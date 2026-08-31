Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — E1: **umbra închisă definitiv** (decizie), **clichetele devin bloc generat**, **Supervizorul intră în plan** (31.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-31**. **Rescriere PARȚIALĂ**, a șasea la rând.
- **de ce PARȚIALĂ, și de ce asta nu e o scuză**: structura a fost rescrisă complet pe 30.08, când
  documentul se contrăzicea în trei locuri. Nu se mai contrazice. Ce s-a schimbat în cele **șapte
  commituri de azi** e **starea**, plus **trei instrumente noi** care fac cifrele derivabile. *O
  rescriere completă a unui document care nu mai e stricat ar fi ceremonie, nu întreținere* — și ar
  rupe urma pe care antetul o cere, fiindcă „ce s-a schimbat" s-ar dizolva într-un text nou.
- **ATENȚIE, s-a schimbat CINE scrie cifrele**: trei blocuri care erau proză sunt acum **derivate** —
  titlul listei 3 (`scripts/scan_lista3.py`), tabelul de probă a datelor, și lista a ce a rămas
  (`scripts/scan_ramas.py`). *Regula, dată de Costin pe 30-31.08 și extinsă de două ori: **orice
  proză care reafirmă un număr — sau un calificativ — derivat ori se generează, ori se șterge.**
  A treia instanță a fost a mea: „niciuna n-are două exerciții consecutive", adevărat doar cu
  „**cu rulaje**", calificativ care lipsea.*
- **ce s-a atins ACUM (tura a cincea)**: titlul · antetul · tabelul clichetelor, care a devenit
  **BLOC GENERAT** · rândul interdicției 77 din tabelul de restanțe · două intrări noi în „cifre
  invalidate" · „dacă continui de aici" · „starea la predare". Restul e neatins **și verificat că
  mai e adevărat**, nu presupus.
- **ATENȚIE, al doilea bloc a trecut de la om la instrument**: tabelul clichetelor vii nu se mai
  scrie. Erau patru cifre sub propoziția «se recalculează, nu se citesc de aici»; trei erau corecte
  — **exact cele trei plafonate**. Regula, generalizată din instanța asta: *o populație declarată
  nedeplafonată nu are voie să-și poarte cifra în proză.*
- **pe commit**: `13acfe0` — ultimul commit intrat. *Predarea se scrie ÎNAINTE de commitul care
  poartă munca de mai jos, fiindcă blocul de cifre trebuie să intre ODATĂ cu ea. Ce descrie e
  arborele care devine commitul următor.*
- **cum se citește „pe commit", ca să nu pară stale**: numele de acolo e al commitului **precedent**,
  prin construcție, nu din uitare. Cifra care spune adevărul despre vechime e cea de mai jos.
- **vechime măsurată, nu estimată**: **0 commituri** de la ultima atingere a fișierului.
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut;
  `core/test_predare_cifre.py` nu lasă cifrele despre date să îmbătrânească.

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
| **13** | tabele din `public` cu `tenant_id`, numărate |

<!-- CIFRE-DATE:STOP -->

**Ce NU e în bloc, și rămâne afirmație datată, cu ora citirii** (`METODA §10.16b`): cifrele de
**proces** („a câta tură", „câte commituri în urmă"), **judecățile**, și cifrele despre **cod**
(rute, gărzi, teste) — alea au instrumentele lor.

---

## AL DOILEA: UNDE SUNTEM ÎN PLAN — citește asta înainte de orice

- `PLAN_LUCRU.md` are **5 etape** (E1–E5) și **3 puncte de decizie**. `PLAN_INVESTIGATII.md` are
  **8 faze**, mapate pe ele: E1 = faza 1 · E2 = faza 2 · E3 = fazele 3–6 · E4 = faza 7 · E5 =
  reparațiile.
- Suntem la **E1 — SETUL COMPLET**. Faza 1 avea patru pași — **1a, 1b, 1c, 1d** — și **toți patru
  sunt făcuți**, toți pe 29.08.
- **DAR criteriul de terminare al etapei NU e îndeplinit**, și aici e diferența care contează:
  *„gata cu pașii" nu e „gata cu etapa".* Listele 3, 4 și 5 ale verdictului trebuie să fie goale pe
  fiecare regim.
- **VERDICTUL 1d, starea de acum:** lista 1 — **1 artefact** (registrul de casă) · lista 3 —
  **1 deschis din 7**, cifră **DERIVATĂ**, nu scrisă (`./venv/bin/python scripts/scan_lista3.py`) ·
  lista 4 — **GOALĂ** · lista 5 — **COMPLETĂ**.
- **CIFRA „8 ARTEFACTE" ERA STĂTUTĂ, și de-aia titlul e acum generat.** Venea din premisa care a
  căzut. Recalculată pe 31.08: 6 reparate, 1 deschis. **Nu o mai scrie de mână** —
  `core/test_lista3.py` o compară caracter cu caracter.
- **ORDINEA REPARAȚIILOR** (`DECIZII.md` 12): **lista 4 → lista 5 → lista 3**, iar **faza 2 după
  ele**. **Toate trei sunt închise.**
- **LISTA 3 E ÎNCHISĂ CA SURSĂ DE CONSTRUCȚIE** (confirmat de Costin, 31.08). Rândul rămas — notele
  explicative — e deschis **pe producător**, nu pe date: R3 s-a închis în aceeași zi. *Nu mai lua
  următorul artefact de aici; n-a mai rămas ce.*
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

---

## AL TREILEA: DE UNDE SE PORNEȘTE, DACĂ EȘTI O SESIUNE NOUĂ

**FAZA 2 A ÎNCEPUT (31.08).** Listele 3/4/5 sunt închise, iar `DECIZII.md` 12 spune *„faza 2 după
ele"*. Grupul ei de interdicții (49–62), măsurat: **8 MĂSURATE · 2 PARȚIAL · 4 NEÎNCEPUTE**.
Criteriul lui **E2** numește exact două lucruri care lipsesc:

1. **categoria de reverificare** (interdicția **55**) — câmpul nu există; proiectul e decis din
   23.08 (două axe mecanice × tabelul 3×3 de praguri). **Axa A e acum calculabilă**, cu
   `core/articol_in_act.py`, dar **pe 15 din 26** de perechi: restul cad pe **R106** sau pe un
   document-ciot. Ce urmează: axa B (consecința, din `core/dependenti_act.py`) și tabelul, cu
   `NECUNOSCUT` declarat pe perechile care nu se confruntă.
2. **51, 56, 57, 62 sunt NEÎNCEPUTE în registru, deși planul le declară *nemăsurabile retroactiv*.**
   Registrul are starea `NEMĂSURABILĂ` exact pentru asta, iar regula lui e *„un câmp gol nu e
   permis; dacă nu se poate măsura, se scrie NEMĂSURABILĂ CU MOTIVUL"*. **E o divergență
   plan↔registru, nu o măsurătoare lipsă** — se închide scriind motivul, nu măsurând.

**R106, deschisă azi:** șase temeiuri numesc actul care a **modificat** articolul, nu actul care îl
**conține**. `COTE.impozit_dividend` are patru temeiuri și niciunul nu se confruntă cu documentul
lui. *Nereparată deliberat: fiecare cere o verificare la sursă a actului care poartă azi valoarea.*

**Restul, neschimbat:**
`core.agenda.urmator_cluster()` întoarce `(None, 0, 0)` din 04.08; lista 3 e **închisă ca sursă de
construcție**; nu e nicio restanță de prag 1 deschisă; din lanțul facturii nu mai e nimic deschis.
**Ce a rămas se citește din `scripts/scan_ramas.py`**, nu dintr-o listă purtată.

*Rândul care stătea aici — „pasul următor e restul listei 3, cele 5 rânduri care cer construcție" —
**contrazicea alte două secțiuni ale acestui document** (`AL DOILEA` și `DACĂ CONTINUI DE AICI`,
amândouă scriind că lista 3 e închisă). Era rămas din revizuirea de dimineață, nesincronizat cu
decizia de după-amiază. **A treia oară în două zile când documentul ăsta se contrazice pe el
însuși**, și de fiecare dată în același fel: o secțiune atinsă, alta nu.*

**ÎNAINTE DE A ESTIMA COSTUL ORICĂREI CONSTRUCȚII, citește ce-au pățit ultimele două
estimări.** La lista 5, „scump"
fusese *dedus* din „nici ruta nu trimite" — fals: componentele existau pe obiectele de rezultat. La
lista 3, un rând întreg („Bilanț — zero rute") era *fals de la naștere*. **Cele trei întrebări se pun
separat, cu răspunsuri mecanice**: producătorul se cheamă pe date reale, ruta se citește din AST,
ecranul se caută în `static/js`.

**Ce s-a închis în ultimele trei ture, ca să nu se recitească registrul:**
- **lista 5, 11 din 12** — registrul-jurnal își arată cele trei coloane 14-1-1 · netul de pe fluturaș
  cele 12 componente, dintr-o **sursă unică** pe care o citesc și hârtia, și ecranul · balanța are
  **rută de date** și verdict de închidere cu **trei** stări · 8 din cele 9 declarații își desfac
  cifra, dintr-o **singură hartă**, nu nouă serializatoare. Rămâne **D112** — `R105`, cu motivul
  scris și **verificat de gardă**, nu crezut pe cuvânt.
- **R93** — aceeași lipsă (`adresa`) era poartă în D100/D101/D205 și **avertisment** în D394, iar
  DUKIntegrator respingea XML-ul. Acum blochează, cu propoziția pe care aplicația o avea deja scrisă.
- **R102** — D394 declara livrări și **zero facturi emise** în același document; poartă pre-DUK, cu
  cauza numită (numărul facturii n-avea cifre).
- **R101** — declarantul e **blocant pe toate cele opt**, după ce **sursa ANAF a decis pe fiecare**.
  A cerut 30 de fișiere de fixturi și un asterisc nou pe ecran.
- **R103, partea statică** — legătura DS↔verificator are gardă cu **trei clichete** (24 / 5 / 18) și
  RED-proof.

**Cea mai importantă cifră de context, dacă ești sesiune nouă:** „verificator **TOTAL 0**", rândul
care apare în fiecare poartă verde, înseamnă **zero din ce știe EL să întrebe** — din 62 de reguli
ale Design System, **5** sunt acoperite. Nu invalidează porțile; le încadrează.

---

## AL PATRULEA: CE E ADEVĂRAT DESPRE STAREA CODULUI

- **restanțe deschise: 44** (din care ale etapei E1: **24**), derivat cu `scripts/raport_b.py`.
  **Nu se scrie de mână** — rândul ăsta a fost invalidat o dată.
- **deschise în ultimele două zile**: R92 (etichete de stare) · R94–R96 (din 1b) · R97 (clasa „ruta
  livrează, ecranul tace", **remăsurată azi: 41 de câmpuri pe 15 rute**, de la 54 pe 16) · R98
  (interdicția care își poartă inventarul) · R99 (previzualizarea scoaterii) · R100 (calibrarea care
  confirmă presupunerea) · R104. **Închise**: R93, R101, R102, partea statică a lui R103, **lista 5
  întreagă**, și **R105** — deschisă și închisă în aceeași zi.
- **decizii care blochează: niciuna.**
- **locuri de verificare**: **221 scrise / 0 goale din 221 (100%)**.
- **interdicții, din 76**: MĂSURATE **21** · PARȚIAL **16** · NEMĂSURABILE **1** · NEÎNCEPUTE **38**.
- **clusterele topologice**: `core.agenda.urmator_cluster()` → **`(None, 0, 0)`**; secvența e epuizată
  din 04.08.2026 — **nu există „următorul programat"**.
- **cele mai vechi restanțe deschise**: R1, R3, R4, R5, R6, R7 — familia „încrederea în corpus".

---

## STAREA LA PREDARE

Poartă verde, citită din ieșirea rulării complete de pe arborele care devine commitul următor:
**3864 teste trec** · 11 skip · 14 xfail · **COLLECTED 3889** · ruff OK · verificator **TOTAL 0** ·
rute **423 = ACCEPTAT 382 + GRI 7 + ROSU 0 + EXCLUS 34** · site **200** · four-way se închide la
`post-commit`, care publică pe `origin/main` și pe `backup/lant-2026-08-31` și **restartează
necondiționat** procesul viu.

**AL PATRULEA BRAȚ AL FOUR-WAY-ULUI SE CITEȘTE ACUM DIRECT** (Costin, 31.08, `DECIZII.md` 16.3): nu
se mai deduce din `ExecMainStartTimestamp`. Se mintează un token de superadmin cu
`auth_api.emite_token` — tiparul propriu al sondelor, `frontend_test/w_auth.py` — și se citește
`GET /admin/versiune`, care întoarce `running`, `head`, `divergent` și `necunoscut`. *Ora de pornire
rămâne a doua lectură, nu singura.*

**VERIFICATORUL DE NECONFORMITĂȚI ARE TREI REZULTATE**, din 31.08: `PASS` · `FAIL` ·
**`NEVERIF [cod]`**. Codul de ieșire nu mai contrazice rezumatul — **2** înseamnă „nu s-a putut
verifica tot", confirmat de Costin (`DECIZII.md` 17.2). *Nu-l consumă nimic programatic azi; se
rulează cu mâna.* Stare: `PASS 18 · FAIL 0 · NEVERIF 2`, cele două fiind liniile NC-07.

**ANCORA NC-02 E RETRASĂ** (`DECIZII.md` 17.1), cu motivul în script. *Regula de purtat mai
departe: o verificare ancorată pe PREZENȚA unei reparații moare la prima rescriere legitimă a
codului reparat; una ancorată pe EFECT nu.*

**CLICHETELE VII — blocul de mai jos e GENERAT, nu scris.** Tabelul ăsta spunea, până pe 31.08,
chiar propoziția «se recalculează, nu se citesc de aici», și avea patru cifre scrise cu mâna. Trei
erau corecte — **exact cele trei plafonate**. A patra, umbra, singura declarată nedeplafonată,
circula în aceeași zi în **trei** valori diferite, prin trei documente. *Propoziția care spune că o
cifră se recalculează nu o recalculează.* Reconstituirea, cu commiturile ei, e în `ISTORIC.md` și în
antetul gărzii — **nu aici**, fiindcă predarea e fișier de stare curentă și orice cifră din ea
pretinde că e de acum. Gardat de `core/test_clichete_generate.py`; regenerare:
`./venv/bin/python scripts/scan_ramas.py --clichete-md`.

<!-- CLICHETE-VII:START (generat de scripts/scan_ramas.py --clichete-md) -->

*Generat din COD. **Nu se scrie cu mâna** — `core/test_clichete_generate.py` recalculează și compară caracter cu caracter. Regenerare: `./venv/bin/python scripts/scan_ramas.py --clichete-md`.*

| cod | acum | ce se numără | instrument |
|---|---|---|---|
| **77** | **61** | refuzuri fără temei în module care citează legea | `scripts/scan_refuzuri.datorie()` |
| **77u** | **781** | UMBRA: refuzuri în module care nu citează legea (nedeplafonat) | `scripts/scan_refuzuri.umbra()` |
| **50** | **1222** | aserțiuni ancorate pe text, nu pe structură | `core/scan_garzi_pe_text.pe_fel()` |
| **R80** | **7** | rute despre care detectorul de apelanți nu poate afirma nimic | `scripts/scan_ancore_rute.verdicte()` |

<!-- CLICHETE-VII:STOP -->

*Al cincilea rând de dinainte — rata clasificatorului de alerte — a plecat de aici în blocul de
**date**, unde îi e locul: se derivă din confruntarea predicțiilor cu faptele, nu din cod.*

**CE A RĂMAS DE FĂCUT se citește rulând `./venv/bin/python scripts/scan_ramas.py`** — șase surse,
defalcat pe fel. *Cifrele NU se scriu aici: sunt derivate și au îmbătrânit deja o dată (111→112,
43→44, la deschiderea lui R106), în chiar ziua în care s-a gardat clasa asta pe tabelul de clichete.
Doar clichetele au dimensiune sigură; restul poartă cifra din fișier, sau `?`.*

**CLICHETUL DE GRI A FĂCUT 45 → 49 → 7 ÎN ACEEAȘI ZI**, iar a doua mutare e **reparația**, nu o
replafonare. Prima creștere venea din vocabular: ancora era un CUVÂNT, iar un ecran nou al cărui
titlu conține „jurnal" orbea cele patru rute `/tenants/{id}/jurnal` — care **au apelanți**. După a
treia creștere din aceeași zi (`salariati`, de la caseta categoriei de mărime), ancora a devenit
**segment de cale**: orbirea **55 → 6**, ACCEPTAT **327 → 375**, **ROSU rămâne 0** — deci nicio rută
n-a pierdut dovada că e chemată. **Instanța fondatoare a lui R80, `PUT /tenants/{id}`, rămâne
oarbă**: reparația n-a acoperit-o, a curățat în jurul ei.

**Cifrele de aici se copiază din IEȘIREA PORȚII, nu din predarea de dinainte.**
**Cifrele secțiunii „Unde suntem" nu se scriu de mână** — `scripts/raport_b.py`.
**Poarta durează ~15-18 minute** (măsurat pe rulările de azi: 869s … 1069s; **ultimele două,
1061s și 1069s, sunt cele mai lungi de până acum** — suita a crescut cu 37 de teste într-o zi). *E cifra pe
care o folosește cine estimează o tură.* Azi poarta a respins de **șase** ori. **Niciuna dintre
respingeri n-a fost regresie de comportament** — toate au fost gărzi scrise înainte, care au prins
forme reale: aserțiuni pe text, afirmații netipate, tabele goale neclasificate, o constantă fiscală
nesursată, două blocuri generate neregenerate, și — de două ori — **cifre scrise de mână de mine, în
chiar tura care construia gardul împotriva lor**.

**O ORDINE CARE M-A COSTAT O RULARE, și se scrie ca să nu se repete:** la o schimbare de JS,
`versioneaza_assets.py --scrie` vine **ÎNAINTEA** lui `interactiune_scan.py`, nu după. Versionarea
rescrie fișierele care REFERĂ modulul schimbat, deci le schimbă conținutul — iar `ui_hash` se
recalculează pe ele. Rulate invers, scanul vizual e deja învechit când versionarea termină, și
poarta cade pe `test_versionare_assets`, nu pe scan — adică semnalul arată spre alt fișier decât
cauza.

---

## CE E ADEVĂRAT ACUM DESPRE RESTANȚE

| | |
|---|---|
| **prag 1** | **niciuna deschisă.** |
| **lista 4** | **GOALĂ**, prin reparație: **R93** (câmp obligatoriu tratat ca avertisment) și **R102** (livrări peste zero facturi). Golul e **re-măsurat pe 19 firme** cu instrumentul care le găsise. *Diferența față de „goală" din 22.08 e chiar criteriul care a pus lista 4 prima: atunci era goală fiindcă măsurătoarea acoperea trei firme.* |
| **R101 · R103-static** | **REZOLVATE.** Declarantul e blocant pe toate opt — **sursa ANAF a decis pe fiecare**, iar o decizie de-a noastră din 17.08 s-a **anulat** (`DECIZII.md` 14). Legătura DS↔verificator are gardă. |
| **lista 5** | **11 din 12 REPARATE (30.08).** Registrul-jurnal · netul de pe fluturaș · balanța · 8 din 9 declarații. Rămâne **D112** = **R105**. *Estimarea de preț de la 1c a ținut pe jumătate: declarațiile n-au fost scumpe — componentele existau, lipsea transportul.* |
| **R97** | clasa *„ruta livrează, ecranul tace"*, **remăsurată 30.08**: **41 de câmpuri pe 15 rute** (era 54 pe 16). Scăderea de **13** e exact felia listei 5 — 2 (jurnal) + 12 (stat) − 1 (`retinut_tichete`, declarat cu motiv). **Clasa propriu-zisă n-a mișcat: 32 pe 13 rute, toate pe ecrane interne**, plus cele 8 ale lui R99. Calibrarea instrumentului s-a mutat pe **caz sintetic** (METODA §29) după ce a picat la prima reparație. |
| **R94 · R95 · R96** | deschise, prag 2, din 1b: două mecanisme care răspund diferit la „ce datorează firma" · o obligație (D100 pe profit) pe care semaforul n-o poate cere · trei registre care citesc trei populații. |
| **R98 · R99 · R100 · R104 · R105** | deschise, cu condiția scrisă. R100 și R104 au fost cerute **explicit** ca gărzi de construit mai târziu, nu acum. **R105** (D112) cere o schimbare de MOTOR, nu de rută — se face ca temă proprie, cu poarta ei. |
| **interdicția 77** | **NOUĂ, 31.08** — *„un blocaj fără temei"*. Perimetru: **61** refuzuri în module care citează legea. **UMBRA rămâne deliberat în afara plafonului**, cu motivul scris în normă, iar din 31.08 **nemăsurată definitiv** (`DECIZII.md` 15) — cifra ei trăiește numai în blocul generat de mai sus, fiindcă aici a îmbătrânit deja. **Migrarea între populații e gardată în ambele direcții**: un modul care începe să citeze legea își aduce în datorie și refuzurile vechi; unul care încetează **nu-și stinge datoria**, o mută în umbră. |
| **clasificatorul de alerte** | **REPARAT 31.08 pe FORMA întrebării.** Nu mai cere `relevanta`, cere **două fapte** (încotro merge documentul · ce declarații atinge), iar relevanța se derivă. Clichet: **2 măsurate, 2 greșite** — și proba nu poate fi ștearsă ca să scadă rata. |
| **poziția 116 D100** | **ABSENȚĂ DECLARATĂ**, nu construcție. D100 **spune** că nu poate declara contribuția de solidaritate, cu temeiul. Zero din 19 firme o datorează. Garda de așteptare pică dacă apare un purtător. |
| **calea jurnalului** | **REPARATĂ 31.08**, trei găuri găsite prin exercițiu: contul din afara planului intra în evidență · o dată care nu e dată ieșea 500 · cele 12 refuzuri n-aveau temei. Acum **0 din 14 fără temei**. |
| **restul (43)** | Vezi `CONFORMITATE.md`, sau `scripts/scan_ramas.py`. Numărul e derivat, nu scris. |

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează. Tabelul se
POARTĂ, nu se deleagă în istoric.*

**Clasa asta are acum un mecanism, nu doar un tabel:** cifrele despre **date** nu mai pot îmbătrâni,
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

### despre măsurători și instrumente

- **Blocul de cifre e derivat din date VII, nu din cod.** Dacă portofoliul se schimbă între generarea
  blocului și sfârșitul porții (~12,5 min), garda **pică** — și pe drept: documentul chiar nu mai
  descrie baza. Remediul e regenerarea. Operațional: **blocul se regenerează ULTIMUL**.
- **Predarea nu se mai poate scrie fără acces la bază.** Scenariul care doare: un incident cu baza
  jos — atunci nu se poate rula nici poarta, deci nu se comite nimic, dar **handover-ul e blocat exact
  când e mai necesar**.
- **Gardul de cifre nu interzice o cifră de date în PROZA predării.** Ce nu mai are voie e ca
  **tabelul** să fie scris din memorie.
- **Verificarea reală a denumirii a rămas pe O SINGURĂ poziție.** Un „0 divergențe" pe o mulțime de un
  element spune mult mai puțin decât pare.
- **Harta ZZ2 e pe AST, deci vede ce SCRIE în `inregistrari`** — nu vede un fapt economic pe care
  aplicația nu-l modelează deloc. Un fapt fără obiect și fără rută nu apare nici ca automat, nici ca
  gol: **nu apare.**
- **Cifra R34 (24 pe 7) nu e cea din 24.08 (29 pe 10).** Măsurătoarea de atunci n-a lăsat instrument,
  deci fereastra ei de luni nu se poate reconstitui. Ce **se** reproduce exact e cazul cel mai mare:
  `tenant_001` 2026-06. Ancora ține; contorul nu.
- **Cele 45 de rute GRI rămân GRI.** S-a reparat raportarea, nu orbirea.
- **Confirmările nu sunt citite de nimeni în afară de mine.** Că textul e bun pentru un contabil e o
  judecată de om, nu o măsurătoare. Ce s-a probat e că **apare** și **ce scrie**.
- **`_bannerFirma` dispare după 8 secunde.** Nu s-a măsurat dacă 8 secunde ajung.
- **Câmpul `fel` e aditiv: ecranul nu-l citește.** Azi nu ascunde nimic — cele patru nu pot diverge —
  dar în ziua în care ar apărea un roșu de regresie, omul l-ar vedea la fel cu unul real.
- **`ALFA MICRO SRL` a fost dezactivată și reactivată de două ori pe 28.08**, deliberat, ca probă. De
  fiecare dată restaurarea a stat în `finally`, iar starea finală s-a **citit** din bază.

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

1. **NU LUA URMĂTORUL ARTEFACT DIN LISTA 3.** E **închisă ca sursă de construcție** (Costin,
   31.08): 1 deschis din 7, iar acela — notele explicative, forma redusă — e deschis **pe
   producător**. Ce a rămas de făcut se citește din `scripts/scan_ramas.py`, nu din listă.
   *Restanțele și interdicțiile nemăsurate sunt populațiile mari; instrumentele din roadmap sunt
   singurele cu contur. Cifrele se iau din instrument, nu de aici.*
2. **UMBRA INTERDICȚIEI 77 E ÎNCHISĂ DEFINITIV** (Costin, 31.08, `DECIZII.md` 15): populația nu
   se auditează, nu devine restanță, **nu se mai deschide ca temă**. Ce continuă e derivarea cifrei,
   nu munca pe ea. *Nu propune o campanie pe ea; nu e „nu acum", e niciodată.*
3. **SUPERVIZORUL e temă de arhitectură pentru FINAL**, scrisă în `PLAN_LUCRU.md` la „Direcții de
   produs, nedatate": *verificarea încrucișată devine funcționalitate distinctă a aplicației, care
   rulează pe cont propriu, nu la depunere.* **Nu e restanță** — n-are contor, n-are condiție de
   deblocare. Trei alegeri rămân ale lui Costin și sunt scrise acolo ca nedecise: ce declanșează o
   rulare · ce vede contabilul din ea · dacă o constatare poate deveni blocantă.
4. **CIFRELE DE CLICHET NU SE MAI SCRIU ÎN PREDARE.** Blocul `CLICHETE-VII` e generat; regenerare
   `./venv/bin/python scripts/scan_ramas.py --clichete-md`. Dacă vrei să pui o cifră de clichet în
   proză, întreabă întâi dacă populația are plafon — dacă n-are, îmbătrânește, și
   `core/test_clichete_generate.py` te oprește pentru umbră.
5. **CONSTATĂRI DESCHISE în `GARZI.md`**, fiecare cu condiția scrisă: ce anume varia la ecranul
   `banca` (rămasă GRI) · **clasificatorul de alerte**, 2 din 2 greșite, acum confruntabil ·
   `verificator_neconformitati.sh` — **ÎNCHIS 31.08**, reparat la cerere: al treilea rezultat
   (`NEVERIF`, cu cod stabil pe fiecare motiv), setul de `sudo` neatins. Generalizarea a scos
   încă trei forme latente în același script, plus un `EXIT=0` peste propriul `FAIL: 3`.
   **Nicio constatare nu mai așteaptă o decizie de la Costin** — rămâne doar `banca`, GRI,
   care așteaptă o măsurătoare, nu o hotărâre.
6. **POLKIT: ÎNCHIS, nu restanță.** *Se scrie explicit fiindcă l-am purtat o tură ca „lucru care îl
   blochează pe Costin", după ce îi scrisesem închiderea eu însumi, în aceeași zi.* Sonda a rulat pe
   31.08 la 01:02, iar temeiul e în `GARZI.md`: **restartul prin polkit se autorizează ONE-SHOT ca
   `unix-user:costin`, exclusiv interactiv, prin `pkttyagent`**. Restartul care eșuase rula **fără
   agent de autentificare** — nu era identitate greșită, era **absența oricărei identități**.
   **Nu se mai rulează nicio sondă polkit.** Rămâne o singură regulă, permanentă: linia
   `Identity unix-group:admin is not valid` e **observație**, iar **nu se atinge nimic din polkit**
   — nu se creează grupul, nu se rescrie spre `unix-group:sudo`, nu se adaugă regulă permisivă —
   **până nu se citește fișierul care declară identitatea** și se stabilește dacă e al nostru sau
   implicit de distribuție. *Nu e o sarcină; e o interdicție.*
7. **ÎNAINTE DE A EXECUTA O COMANDĂ, citește restanța pe care o numește** — și **măsoară cifra pe
   care o afirmă**. Pe 30.08, o comandă a afirmat că predarea e „cu 12 commituri în urmă"; era **0**.
   E a cincea oară pentru aceeași cifră. Verificarea costă o comandă. **A ținut din nou pe 31.08**:
   comanda numea o cifră pentru populația din umbră; măsurată, era alta, iar cele trei valori aflate
   în circulație au fost reconstituite mecanic, pe worktree-uri detașate (`ISTORIC.md`, partea a
   doua). *Regula asta a produs întreaga tură — dacă cifra se lua de bună, derapajul rămânea în trei
   documente.*
8. **Nu porni nicio construcție fără măsurătoare.**
9. **`scripts/raport_b.py` derivă „Unde suntem".** Nu se scrie de mână.
10. **Raportul se scrie din `SABLON_RAPORT.md`**, în ordinea:
   0 CERINȚE · 1 CE AM PRESUPUS · 2 ÎN PLUS/MAI PUȚIN · 3 CE AM ACTUALIZAT · 4 ÎNȚELEGEREA ·
   5 RĂSPUNS LA COMANDĂ · 6 UNDE SUNTEM · 7 POARTA.
