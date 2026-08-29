Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — faza 1 terminată, **clasa R97 măsurată**: 66 de câmpuri tăcute, dar lista 5 nu crește (30.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-30** — **actualizare de secțiuni**, nu rescriere completă. S-au
  schimbat
  **antetul**, **unde suntem în plan**, **de unde se pornește**, **starea codului**, **starea la
  predare**, **tabelul de restanțe** și **dacă continui**. Restul rămâne cum era, fiindcă nu s-a
  schimbat. *Rescrierea completă de acum câteva ore a fost necesară fiindcă documentul se
  stratificase; o a doua rescriere completă la trei ore după prima ar fi fost ritual, nu nevoie.*
- **ce s-a schimbat de fapt, azi**: **clasa R97 e MĂSURATĂ** — 66 de câmpuri livrate și tăcute, pe 17
  rute (plafon inferior), din care **doar 2 poartă artefacte cerute de lege**. **Lista 5 rămâne la 10
  poziții**: marginea despre care se spunea „nu se poate ști" era **zero**.
- **ce s-a schimbat ieri (29.08), și rămâne adevărat**: faza 1 s-a terminat — 1b pe regimurile reale
  (12 din 12, 19 firme, 285 de generări prin DUKIntegrator) · 1c pe artefactele care ies (168 de
  ieșiri) · **verdictul 1d rescris**, cu șase poziții mutate · s-au deschis **R93–R98** · `scripts/`
  nu mai contează ca apelant de producție (`DECIZII.md` 29.08 (10)).
- **ultima rescriere COMPLETĂ**: tot azi, a douăsprezecea atingere —
  primele unsprezece au fost **pe secțiuni**, iar documentul se stratificase: un paragraf „de unde se
  pornește" apărea de două ori, tabelul de restanțe avea două rânduri „restul" (unul spunea **44**,
  proza spunea **35**), „fals-negativul cheii" era scris de două ori, iar „dacă continui" era
  numerotat 1-2-3-2-3-4. *Un document care se contrazice în două rânduri vecine nu se citește: cine
  îl citește nu poate ști care rând mai e adevărat.*
- **corectată imediat după**: rescrierea completă a intrat pe `471368c`, iar rularea porții care a
  produs-o a arătat că **rândul „starea la predare" purta o cifră falsă, copiată din documentul
  vechi** (`411`/`32` în loc de `413`/`34`). Corectată în commitul următor, și **invalidată în
  tabel**. *Se scrie aici, nu doar în tabel: o rescriere al cărei scop era să scoată afirmațiile
  purtate din memorie a purtat ea însăși una, la douăzeci de minute după ce a explicat de ce nu se
  face asta.*
- **pe commit**: `d54d58a` — ultimul commit intrat. *Predarea se scrie ÎNAINTE de commitul care
  poartă munca de mai jos, fiindcă blocul de cifre trebuie să intre ODATĂ cu ea. Ce descrie e
  arborele care devine commitul următor.*
- **cum se citește „pe commit", ca să nu mai pară stale**: numele de acolo e al commitului
  **precedent**, prin construcție, nu din uitare. Cifra care spune adevărul despre vechime e cea de
  mai jos, măsurată cu formula din `pre-commit`.
- **vechime măsurată, nu estimată**: **1 commit** de la ultima atingere a fișierului, citit acum cu
  formula din hook (`git rev-list --count $(git log -1 --format=%H -- PREDARE_LANT.md)..HEAD`) —
  commitul instrumentului lui R97, `d54d58a`. **Devine 0 odată cu commitul care poartă rândurile
  astea.**
  Pragul din hook e **10**; avertismentul `[pre-commit] ATENTIE` **nu a apărut** în niciuna din
  porțile de azi. *Se scrie cifra de la momentul scrierii, nu cea de după — altfel documentul ar
  afirma despre un commit care încă nu există.*
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
- Suntem la **E1 — SETUL COMPLET**, adică **etapa 1 din 5**. Faza 1 avea patru pași — **1a, 1b, 1c,
  1d** — și **toți patru sunt făcuți**, toți azi. **Faza 1 nu mai are pași.**
- **DAR criteriul ei de terminare NU e îndeplinit**, și aici e diferența care contează: „gata cu
  pașii" nu e „gata cu etapa". Listele 3, 4 și 5 ale verdictului trebuie să fie goale pe fiecare
  regim, și nu sunt.
- **Criteriul care termină E1**: lista artefactelor cerute de lege — din lege, cu temei — pe
  **regimurile REALE**, fiecare artefact clasificat în una din cele cinci liste ale verdictului 1d.
  Etapa e gata când listele **3, 4 și 5** sunt goale pe fiecare regim. Lista 2 poate avea conținut:
  măsoară ce n-a completat contabilul, nu ce n-a făcut aplicația.
- **1a — MĂSURAT AZI, prima oară: 12 regimuri reale pe 19 firme**, cu
  `scripts/scan_regimuri.py`. *Planul cerea cifra asta ca **primă operațiune a etapei**, iar lucrul a
  mers opt luni fără ea — 91 de restanțe deschise și închise pe un criteriu de terminare care se
  sprijinea pe o cifră pe care n-o avea nimeni.* Detaliul, cu tabelul pe semnături, e în
  `CONFORMITATE.md`, secțiunea „1a".
- **Ce a scos măsurătoarea, pe scurt:** **3 profile incomplete** (rânduri vechi de seed, nu o gaură
  în cod — `vector_fiscal_api` refuză deja să salveze fără ele; intră în lista 2 a verdictului 1d) ·
  **marjă turism (art. 311) = 0 firme** și **marjă second-hand (art. 312) = 0 firme**, adică module
  fără nicio firmă care să le exercite, chiar semnalul cerut de plan · **agricultor forfetar** și
  **construcții** NU SE POT NUMĂRA — n-au nici câmp pe profil, nici marcaj în note, iar un „0" acolo
  n-ar deosebi „nicio firmă" de „nu știu să caut".
- **1b — MĂSURAT AZI, pe tot portofoliul**, cu `scripts/scan_1b_regimuri.py`: **12 din 12 regimuri ·
  19 din 19 firme · 15 tipuri de declarație · 285 de generări**, fiecare trecută prin
  **DUKIntegrator**. Detaliul e în `CONFORMITATE.md`, „Pasul 1b, RELUAT PE REGIMURILE REALE".
  *Măsurătoarea 1b de pe 22.08 acoperea trei firme, adică **două** din cele 12 semnături.*
- **Ce a scos 1b, pe scurt, în ordinea gravității:** **lista 4 a verdictului 1d nu mai e goală** (D394
  iese și e respins de arbitru pe `tenant_001` și `tenant_017` — **R93**) · **cele trei registre
  obligatorii citesc trei populații diferite**, 21 din 41 de note sunt ciorne și intră în balanță și
  în registrul-jurnal, dar nu în fișa de cont (**R96**) · **semaforul n-are nicio cale să ceară D100
  pe regim de profit**, deși CF art. 41 alin. (1) cere declarare trimestrială (**R95**) · **selectorul
  și semaforul răspund diferit la „ce datorează firma"**, iar generatorul nu ascultă de niciunul — 8
  divergențe pe 4 firme (**R94**).
- **Și două verdicte din 22.08 care NU mai sunt adevărate, în bine:** **Cartea mare** are producător
  (`core/fisa_cont.py`, Fișa de cont 14-6-22, probată pe date reale) — cauza se schimbă din „nu există
  producător" în „producătorul există, nu ajunge la om"; **registrul-jurnal** are cele trei coloane
  cerute de pct. 45, derivate la citire din 24.08 — ce rămâne e că **14 din 41 de note** n-au document
  derivabil.
- **1c — MĂSURAT AZI, pe artefactele care ies**, cu `scripts/scan_1c_verificabil.py`: **168 de
  ieșiri**, 19 firme, cele patru întrebări ale planului puse pe **structura răspunsului**, nu pe
  șiruri. Rezultatul e o **despărțire**, nu un număr: **0 din 92** de ieșiri de declarație își arată
  componentele (ruta întoarce un **contor**, nu operațiunile), în timp ce **registrele desfac** —
  jurnalul întoarce liniile, casa operațiunile cu soldul curent, statul rândul per salariat. Iar cele
  **92 de „are temei" sunt false**: e temeiul **validatorului**, nu al cifrei.
- **VERDICTUL 1d, RESCRIS — șase poziții mutate:** lista 1 rămâne la **1 artefact** (registrul de
  casă) · lista 3 scade la **8** (a ieșit registrul-jurnal; Cartea mare a rămas, cu altă cauză) ·
  **lista 4 are 2 poziții** (era goală) · lista 5 are **10 poziții + clasa R97**, nemăsurată.
- **Un rezultat despre FORMA muncii rămase:** listele 3 și 5 sunt **identice pe toate cele 12
  regimuri** — ecranele și producătorii nu depind de regim. Deci munca rămasă **nu se împarte pe
  regimuri, ci pe artefacte**: un ecran reparat o dată curăță aceeași poziție pe toate douăsprezece.
- **Pasul următor NU e ales.** Faza 1 nu mai are pași; ce urmează — faza 2 (temeiurile), sau
  reparațiile din listele 3/4/5 — **e ordinea lui Costin**.

---

## AL TREILEA: DE UNDE SE PORNEȘTE, DACĂ EȘTI O SESIUNE NOUĂ

**Nu e nicio cerință comandată neîncepută.** Ultima — 1c — e terminată, iar cele două decizii date
peste raport (clasa R97 și garda R98) sunt scrise și deschise. **Nu e nicio restanță de prag 1
deschisă**
(R35, ultima, s-a închis pe 28.08). **Din lanțul facturii nu mai e nimic deschis** — nici muncă, nici
decizie, nici verificare.

**Cele trei intrări ale unei facturi în evidență, toate acoperite:**
1. **emiterea prin aplicație** → nota se scrie în `creeaza_factura`, punctul unic al **tuturor** celor
   patru drumuri de emitere (R87);
2. **factura primită, din SPV** → nota la `/facturi-primite/{id}/valideaza`, unde omul alege contul de
   cheltuială (obligatoriu) și clasifică regimul (R88);
3. **factura emisă întoarsă prin import** → **ciornă de recunoaștere** (stare `de_recunoscut`,
   **declarabilă**), apoi `POST /facturi/{id}/recunoaste` (R91, varianta (iii)).

*Iar istoricul a intrat prin **aceleași acte**, nu printr-o migrare: **31 de facturi, 103.163,00 lei
TVA, 11 firme** (R89).*

**Ce s-a construit, ca să nu se recitească registrul:** contarea are un singur loc
(`core/contare_facturi.py`); nota se scrie **în același act cu faptul**; cheia `factura_id` distinge
contarea de plată, iar trezoreria (51/53) **taie** semnătura de contare; plasa caută note fără cheie
înainte de fiecare notă automată; nota din jurnalul liber primește cheia **la scriere**; o notă de
plată se poate **dezlega**, cu motiv obligatoriu, rol declarat și urmă proprie (R90).

**Cele 18 rânduri de verificare ale celor două acte noi sunt executate și bifate pe RULARE**, nu pe
citirea codului: `scripts/proba_verificari_trasee.py` cheamă funcțiile de rută din `main.py` pe o
schemă efemeră — **18 din 18** cu dovadă tipărită.

**Nu e propus niciun pas următor.** Faza 1 nu mai are pași, iar ce urmează — faza 2, sau reparațiile
din listele verdictului — e o decizie de ordine, deci a lui Costin.

---

## AL PATRULEA: CE E ADEVĂRAT DESPRE STAREA CODULUI

- **restanțe deschise: 42**, derivat cu `scripts/raport_b.py`. *Ziua a închis douăsprezece și a
  deschis șapte — **R92**, găsită la scrierea ISTORICULUI · **R93–R96**, scoase de măsurătoarea 1b ·
  **R97–R98**, din 1c și din decizia care a urmat. **Niciuna n-a fost găsită de o gardă.*** Restul
  defalcării (praguri, cine deblochează) se derivă; **nu se scrie aici**, fiindcă exact rândul ăsta a
  fost invalidat o dată azi.
- **toate șapte sunt de PRAG 2**, și niciuna nu produce azi o cifră greșită pe un ecran: două trăiesc
  pe calea de API (R94), una e o absență prin construcție pe care datele de azi n-o pot aprinde
  (R95), una cere întâi răspunsul la R36 (R96). *R93 e singura cu instanță vie: contabilul de pe
  `tenant_001` primește eroarea brută a validatorului ANAF în loc de propoziția pe care aplicația o
  avea deja scrisă.*
- **R97 — MĂSURATĂ pe 30.08, și rezultatul are două jumătăți care trag în direcții opuse.** Clasa
  *„ruta livrează, ecranul tace"* e **mare și reală**: **66 de câmpuri tăcute sigur, pe 17 rute**
  (plafon inferior, fiindcă „randat" e supra-numărat prin construcție), plus 268 de candidați pe 41 de
  rute. **89 din cele 106 rute măsurate n-au niciun câmp tăcut** — deci e concentrată, nu difuză.
  **DAR:** din cele 17 rute, doar **două** poartă artefacte din lista lui 1a, și amândouă erau deja în
  lista 5. **Lista 5 rămâne la 10 poziții — marginea era zero.** Restul de 14 sunt **ecrane interne**.
  *Cifra asta e chiar cea care lipsea ca să se poată alege ordinea listelor.*
- **Ce a crescut totuși: adâncimea.** Statul de plată avea 7 câmpuri tăcute cunoscute; are **12** —
  printre cele noi, `cm_brut`/`cm_net`/`cm_zile`, adică **concediul medical**, și tichetele. Iar
  `/tenants/{id}/scoatere` tace pe **11 din 31** de câmpuri: previzualizarea celui mai distructiv act
  al aplicației nu arată nici ce s-a decis, nici ce anume s-ar șterge.
- **cele 16 „fără prag declarat" sunt cele vechi (R1–R27)** — nu înseamnă că sunt ușoare, înseamnă că
  n-au fost încadrate când s-a introdus scara de praguri.
- **decizii care blochează: niciuna.** Toate trei care blocau punctul de decizie 1 au primit răspuns
  pe 29.08.
- **locuri de verificare**: **221 scrise / 0 goale din 221 (100%)**, derivat cu `scripts/raport_b.py`.
  *Contorul a fost lărgit odată cu ultimele 18: o căsuță nebifată e un loc nefăcut și cu text, și
  fără. Înainte, un rând `- [ ] <propoziție>` nu intra nici la scrise, nici la goale — dispărea din
  numitor, iar procentul sărea înapoi la „100%".*
- **interdicții, din 76**: MĂSURATE **21** · PARȚIAL **16** · NEMĂSURABILE **1** · NEÎNCEPUTE **38**.
- **clusterele topologice**: `core.agenda.urmator_cluster()` → **`(None, 0, 0)`**. Inventarul are
  **79 de rânduri, 79 bifate, 0 blocate**. Secvența e epuizată din 04.08.2026 — **nu există
  „următorul programat"**.
- **familia salariilor**: nimic deschis (R33, R34, R85, R86 — toate închise).
- **cele mai vechi restanțe deschise, ca vechime pe registru**: R1, R3, R4 (**174** commituri fiecare),
  R5, R6 (**173**), R7 (**171**). *Toate patru din familia „încrederea în corpus" — exact temelia pe
  care stă 1a.*

---

## STAREA LA PREDARE

Poartă verde, citită din rularea care a produs `d54d58a`: **3564 teste trec** · 10 skip · 14 xfail ·
ruff OK · verificator **TOTAL 0** (182 scanate = 181 acceptate + 1 exclus) · rute
**413 = ACCEPTAT 334 + GRI 45 + ROSU 0 + EXCLUS 34** (clichet GRI 45) · site **200** · four-way
`HEAD = origin/main = origin/backup/lant-2026-08-30 = d54d58a`, procesul viu restartat de post-commit.
*Ramura de backup e a zilei noi — `lant-2026-08-30`, creată de hook la primul commit de după miezul
nopții.*

**Poarta a respins de TREI ORI în ziua asta, și toate trei respingerile au fost ale mele, nu
regresii.** A treia a fost `commit-msg`: în commit erau fișiere **normative** (`CONFORMITATE.md`),
iar mesajul n-avea rândul `# diff-citit:`. *Garda cere ca un fișier normativ să nu intre până nu e
citit — inclusiv când diff-ul e scris de mine, fiindcă ce contează e ce CERINȚE conține, nu cine l-a
scris.* Primele două: Prima: instrumentul nou importa `core/fisa_cont.py`, iar clichetul modulelor nelegate a
cerut, corect după propria lui regulă, ca modulul să iasă din pin — adică exact stingerea semnalului
pe care pinul îl păzea. A doua: cele două gărzi noi de calibrare erau **ancorate pe text**
(`"core/modul_probat.py" in ceva`), iar clichetul 50 le-a prins la **1223 > 1222**. Rescrise pe
structură — aserțiunea compară acum ce a creat fixtura cu ce a raportat sonda, fără niciun șir scris
de mână. *Amândouă gărzile au avut dreptate; niciuna n-a fost ocolită.*

**Cifrele de aici se copiază din IEȘIREA PORȚII, nu din predarea de dinainte.** *Prima formă a
rescrierii de azi scria „411 … EXCLUS 32" — purtată din documentul vechi, fără măsurătoare. Poarta a
măsurat 413 și 34, la douăzeci de minute după ce documentul din jur explica de ce nu se face asta.
Vezi tabelul de cifre invalidate.*

**Cifrele secțiunii „Unde suntem" nu se scriu de mână** — `scripts/raport_b.py`.
**Poarta durează ~12,5 minute.**

---

## CE E ADEVĂRAT ACUM DESPRE RESTANȚE

| | |
|---|---|
| **prag 1** | **niciuna deschisă.** R35, ultima, închisă pe 28.08. |
| **lanțul facturii** | **R87 · R88** (`55a57f6`), **R89** (`d582563`), **R90** (`95f5d0e`), **R91** (`6ca0aba`) — toate REZOLVATE, fiecare cu proba ei pe date reale. Condiția lui R87/R88 s-a **DESPĂRȚIT**, nu s-a considerat satisfăcută: jumătatea „proporția de necontate = 0" s-a mutat, cu numele ei, la R89. |
| **cele șapte de azi** | **R45, R54, R58, R63, R66, R70, R73** — REZOLVATE. **Șase erau deja construite**; ce lipsea era decizia scrisă, sau proba. Două s-au închis pe **alt motiv** decât cel din comandă, și se spune în registru: R54 (validarea EXISTĂ din 26.08 — „nu se adaugă" ar fi însemnat *a scoate* o poartă care merge) și R63 (comanda cerea fuziunea, decizia din 26.08 spune invers; fuziunea a rulat și a găsit **0 cazuri**). |
| **retrase de autorul lor** | Costin a retras el însuși, în tura următoare, amândouă comenzile: **R54 rămâne cum e, poarta nu se atinge** · **R63 varianta (c) rămâne, adresele nu se fuzionează**. Scris în `DECIZII.md` (9). |
| **scos definitiv din discuție** | **reîncercarea automată la eșec de email**. Nu acum, nu ca restanță viitoare. Consecința, scrisă o dată ca să nu fie redescoperită ca lipsă: **un email pierdut rămâne pierdut** — aplicația spune că s-a întâmplat și alertează, dar nu încearcă din nou. |
| **R92, DESCHISĂ azi** | Ecranul nu poate numi **5 din cele 8** stări ale unei facturi, iar **10 din 41** afișează azi șirul brut `importata`. Prag 2 — nu e latentă. *Nu se închide prin adăugarea a cinci șiruri: etichetele se derivă din nomenclator, cu gardă în amândouă direcțiile.* |
| **R93–R96, DESCHISE azi de 1b** | **R93** — aceeași lipsă (`adresa`) e poartă în D100/D101/D205 și simplu **avertisment** în D394 (`core/d394.py:1086`), iar DUKIntegrator respinge XML-ul: **lista 4 a verdictului 1d nu mai e goală**. · **R94** — selectorul știe forma și vectorul TVA, semaforul știe regimul, generatorul nu ascultă de niciunul: D101 iese valid pe cele 10 firme micro, iar D300/D394 se produc pe 4 neplătitoare, cu nota falsă „un plătitor depune nul". · **R95** — semaforul n-are nicio cale să ceară D100 pe profit, deși CF art. 41 alin. (1) cere declarare trimestrială; `d100.py` are ramura de profit, lipsește cine s-o ceară. · **R96** — balanța și registrul-jurnal citesc ciornele, fișa de cont nu: **21 din 41 de note**. Toate patru sunt **prag 2**. |
| **R97–R98, DESCHISE de 1c și de deciziile de după** | **R97** — clasa *„ruta livrează, ecranul tace"*: registrul-jurnal (ruta derivă `nr_curent`, `document`, `total_debit`/`total_credit`; ecranul afișează **zero** din ele) și netul de pe fluturaș (toate cele 7 componente sosesc, **niciuna** nu se afișează). **Se tratează ca CLASĂ, nu ca două poziții de listă** — decizia lui Costin —, iar condiția cere **întâi măsurarea clasei**, cu instrumentul care confruntă câmpurile trimise cu cele randate. · **R98** — o interdicție care își poartă inventarul îmbătrânește singură: la 66, `Temei(` a trecut 57 → **64**, mențiunile din JS 43 → **68**, sub un verdict care a rămas corect. Regula: interdicția citează **regula și pragul**, inventarul stă ca **anexă datată**. **Doar gardă, nu rescriere acum.** |
| **restul (42)** | Vezi `CONFORMITATE.md`. Numărul e derivat, nu scris; nu s-a atins nimic altceva. |

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
| **„rute 411 = … + EXCLUS 32"** | predările din 28 și 29.08, inclusiv **prima formă a rescrierii complete de azi** | **413** și **34**, citit din ieșirea porții care a produs `471368c`. *Cifra a fost **copiată din documentul de dinainte** în timpul unei rescrieri al cărei scop era să scoată exact afirmațiile purtate din memorie. A treia clasă de cifră care se strecoară prin copiere, după `nume_anaf` și `43`. De-asta rândul „starea la predare" spune acum, în text, de unde se ia.* |

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
  Repornirea serviciului o rulează Costin: `! ssh iconta "sudo systemctl restart iconta-nou"`.
- **Env obligatoriu**: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a`
  (+ `PYTHONPATH=/home/costin/iconta_nou` pentru scripturile din `frontend_test/`).
- **Mesajul de commit se trimite prin FIȘIER, nu prin heredoc în argumentul ssh.** Un `"` îl
  trunchiază în tăcere; s-a întâmplat de două ori pe 27.08, a doua oară jumătate de mesaj.
- **Un patch rulează PE SERVER** — pe Windows, `io.open(..., "w")` trece fișierul la CRLF în tăcere și
  face fiecare diff viitor zgomotos.
- **Ghilimelele românești rup șirul Python** — literal triplu.
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

1. **Nicio cerință comandată neîncepută. Nicio restanță de prag 1 deschisă.** Din lanțul facturii nu
   mai e nimic deschis, iar `TRASEE_VERIFICARI.md` e la **221 / 221**.
2. **ÎNAINTE DE A EXECUTA O COMANDĂ, citește restanța pe care o numește.** De două ori pe 29.08 o
   comandă a cerut ceva deja construit, iar o dată ar fi însemnat să **scot** o poartă care merge.
   **Costin a retras el însuși amândouă comenzile**, în tura următoare. Verificarea premisei a costat
   o oră și a scos două lucruri reale.
3. **Nu propune un pas următor — cere-l.** Faza 1 nu mai are pași; ce urmează e ordine, adică
   decizie. **Materialul pentru ea e acum complet**, fiindcă R97 a fost măsurată exact ca să nu se
   aleagă pe presupuneri: **lista 4** — 2 poziții, cea mai mică și cea mai ascuțită (R93) · **lista
   3** — 8 artefacte, muncă de construit · **lista 5** — 10 poziții, **și cifra e finală**, nu plafon
   · **clasa R97** — 66 de câmpuri pe 17 rute, din care 14 rute sunt ecrane interne, **în afara**
   setului măsurat de faza 1 · **faza 2 — temeiurile**, pasul următor din plan.
4. **Nu porni nicio construcție fără măsurătoare.**
5. **`scripts/raport_b.py` derivă „Unde suntem".** Nu se scrie de mână.
6. **Raportul se scrie din `SABLON_RAPORT.md`**, în ordinea:
   0 CERINȚE · 1 CE AM PRESUPUS · 2 ÎN PLUS/MAI PUȚIN · 3 CE AM ACTUALIZAT · 4 ÎNȚELEGEREA ·
   5 RĂSPUNS LA COMANDĂ · 6 UNDE SUNTEM · 7 POARTA.
