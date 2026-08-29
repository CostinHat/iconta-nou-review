Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — proiectarea R87/R88 e DECISĂ, gaura de idempotență e MĂSURATĂ, iar stocul istoric are listă (29.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-29**, a patra oară în ziua asta. *Rescriere PE SECȚIUNI, nu completă
  — se spune, ca să nu pară ce nu e. S-au atins: antetul, „de unde se pornește", tabelul de restanțe,
  cifrele invalidate și lista „ce nu e adevărat". Restul e neatins fiindcă nu s-a mișcat.*
- **pe commit**: `427e254` — ultimul commit intrat. *Predarea se scrie ÎNAINTE de commitul care poartă
  munca de mai jos, fiindcă blocul de cifre trebuie să intre ODATĂ cu ea. Ce descrie e arborele care
  devine commitul următor.*
- **rescrierea de dinainte**: `a0cc6a5`, aceeași zi. Între ea și acum au intrat **două** commituri: `2c43571` și `427e254`.
- **de ce acum**: se rescrie înaintea opririi, ca de fiecare dată. *Conținutul, nu contorul* — măsurat
  cu formula din `pre-commit`: **1** commit în urmă, pragul e **10**, deci nu era stale. Se rescrie
  fiindcă s-a schimbat ce spune, nu fiindcă a îmbătrânit.
- **cum se citește „pe commit" din antet, ca să nu mai pară stale**: predarea se scrie **înainte**
  de commitul care o poartă, deci numele de acolo e al commitului **precedent**. După ce commitul
  intră, antetul arată cu unul în urmă **prin construcție**, nu din uitare. Cifra care spune
  adevărul despre vechime e cea de mai sus, măsurată cu formula din `pre-commit`.
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut; **de azi**,
  `core/test_predare_cifre.py` nu lasă cifrele despre date să îmbătrânească.

---

## PRIMUL LUCRU DE ȘTIUT: CIFRELE DE MAI JOS SUNT INTEROGATE, NU SCRISE

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

## AL DOILEA: DE UNDE SE PORNEȘTE, DACĂ EȘTI O SESIUNE NOUĂ

**Nu e nicio cerință comandată neîncepută.** Cele două întrebări de ieri **au primit răspuns** și sunt
scrise în `DECIZII.md` (intrarea „29.08.2026 (2)"). Ce așteaptă acum e altceva, și e mai puțin:

1. **TVA la încasare pe factura primită** — singurul punct al proiectării rămas fără răspuns, la
   **R88**. Nu e o rafinare de aliniat pe parcurs: `factura_contabilizeaza` citește regimul **propriu**
   al firmei și nu citește niciodată `facturi.furnizor_tva_incasare`, deși D300 o folosește. **2
   facturi** pe date curente ar primi TVA pe 4426 în timp ce decontul îl amână. Trei ieșiri scrise,
   **niciuna aleasă**.
2. **stocul istoric** — **R89**, restanță nouă. Lista e măsurată și scrisă, firmă cu firmă. Decizia pe
   ea, nu. Patru variante scrise, **niciuna propusă** — asta era chiar decizia din 29.08.

**Construcția R87/R88 nu e începută, și nu se poate începe de oriunde.** Ordinea pe care o impune
măsurătoarea: verificarea de idempotență trebuie întâi corectată să întrebe *„există o notă de
CONTARE?"*, nu *„există o notă?"* — altfel automatul refuză 3 facturi cu un mesaj fals. Vezi R87,
blocul BBB.

**Nu e propus niciun pas următor în afara astora** — ordinea o dă Costin.

---

## AL TREILEA: CE E ADEVĂRAT DESPRE STAREA CODULUI

- **nicio restanță de PRAG 1 deschisă.** R35 era ultima, închisă pe 28.08.
- **45 de restanțe deschise**, numărate mecanic pe registru azi: prag 2 — **17**, prag 3 — **12**,
  fără prag declarat — **16** (cele vechi, R1–R27). *Cifrele de dinainte (44 · 15) nu se reconstituie
  din registru cu aceeași numărătoare, deci nu se poartă mai departe — se refac. `scripts/raport_b.py`
  derivă totalul; defalcarea pe praguri se numără din câmpul `unde intră`.*
- **clusterele topologice**: `core.agenda.urmator_cluster()` → **`(None, 0, 0)`**. Inventarul are
  **79 de rânduri, 79 bifate, 0 blocate**. Secvența e epuizată din 04.08.2026 — **nu există
  „următorul programat"**.
- **progres E1**: **203 locuri de verificare scrise / 0 goale, din 203 (100%)**.
- **familia salariilor**: nimic deschis (R33, R34, R85, R86 — toate închise).

---

## AL PATRULEA: TREI CAPCANE DE PROCEDURĂ, ÎNVĂȚATE PE PIELEA MEA ÎN ULTIMELE DOUĂ ZILE

1. **Un `str.replace` fără aserțiune nu e o modificare, e o speranță.** A lovit de **trei ori** pe
   tabelul de restanțe din predarea asta. Unealta: `scripts/inlocuieste.py`. Regula:
   `METODA_VERIFICARE.md` **§28**.
2. **Poarta testează ARBORELE DE LUCRU, nu indexul.** Un `@COMMIT@` lăsat în `CONFORMITATE.md`
   pică poarta chiar dacă fișierul nu e în commitul curent. Ordinea celor două commituri — lucrul
   întâi, registrul după, cu hash-ul real — **nu e stil, e o constrângere**.
3. **Raționamentul care ține o restanță DESCHISĂ cere aceeași verificare ca cel care o închide.**
   Pe 28.08 am ținut R34 deschisă pe o condiție îndeplinită de trei zile. *E mai ușor de ratat
   fiindcă rezultatul lui pare prudent.*

---

## STAREA LA PREDARE

Poartă verde pe arborele care devine commitul următor: **3490 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator **TOTAL 0** ·
rute **411 = ACCEPTAT 334 + GRI 45 + ROSU 0 + EXCLUS 32** · acte de nivel firmă **0 tăcute din 7** ·
site **200** · four-way `HEAD = origin/main = origin/backup/lant-2026-08-28`.

**Cifrele nu se scriu aici** — `scripts/raport_b.py`. **Poarta durează ~12,5 minute.**

---

## CE E ADEVĂRAT ACUM DESPRE RESTANȚE

| | |
|---|---|
| **R87 · R88** (DESCHISE, INTERN, prag 2) | **PROIECTAREA E DECISĂ** (5 puncte, `DECIZII.md`). Niciun cod de producție scris. R87 poartă acum și **blocul BBB** — gaura de idempotență, măsurată. R88 rămâne blocată pe **un singur punct**: TVA la încasare. |
| **R89** (DESCHISĂ, DECIZIE, prag 2) | **NOUĂ azi.** Stocul istoric: 28 pe cheie / 31 fără notă de contare, 102.260,00 lei TVA, 10 firme. Lista e scrisă; decizia, nu. |
| **R36** (REZOLVATĂ pe `1bd9455`) | Închisă în ziua asta. |
| **R37, R39** | Re-citite la ZZ5: R39 a trecut DECIZIE → INTERN, R37 și-a schimbat domeniul. |
| **prag 1** | **niciuna deschisă.** |
| **restul (44)** | Vezi `CONFORMITATE.md`. Harta pe praguri e mai sus. |
| **R81, R79, R80** | Neatinse azi după închiderea lor / decizia (c). R80 rămâne deschisă pe **muncă**, nu pe răspuns. |
| **restul** | Vezi `CONFORMITATE.md` — nu s-a atins nimic altceva. |

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează. Tabelul se
POARTĂ, nu se deleagă în istoric.*

**De azi, clasa asta are un mecanism, nu doar un tabel:** cifrele despre **date** nu mai pot
îmbătrâni, fiindcă sunt generate. Tabelul rămâne pentru cele despre cod și proces — și ca istorie.

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
| **„PREDARE_LANT.md e cu 12 commituri în urmă"** | comenzile din 27.08 seara și târziu | **2**, măsurat cu formula din `pre-commit`. Pragul e 10, avertismentul n-a apărut. **A treia apariție a aceleiași cifre.** |
| **„4 din 6 acte de nivel firmă"** | R82, 27.08 | **4 din 7**, măsurat pe calea rutei, nu pe fișier. Cele patru tăcute sunt aceleași |
| **„4 divergențe de denumire"** (clichet pe date) | `test_nume_firma_unic.py`, 27.08 | **0** pe populația declarată. Vechea valoare era clichet pe **fixturi** — instrumentul citea toate firmele, fără filtru de cabinet |
| **„0 din 18 firme au `nume_anaf`"** | prima formă a predării de la 04:2x | **1 din 18** — `Antibiotice Iasi`, cu divergență reală față de ANAF, cu alegerea deja consemnată. Cifra fusese invalidată o dată pe 27.08 și a reapărut din memorie |
| **„divergența nu se poate naște la creare"** | R81, 28.08 dimineața | adevărat despre `POST /tenants`, **fals** despre `POST /auth/register`, unde `precompleteaza_din_anaf(seteaza_nume=True)` scria un singur loc. Găsit de garda de simetrie, la prima rulare |
| **„51 de rute oarbe" citit ca „51 GRI"** | R80, 27.08 | **45**. Din cele 51, șase erau deja `EXCLUS`. Orbirea instrumentului (51) și clasa GRI (45) sunt două întrebări, nu două măsurători ale aceleiași |
| **„caseta de divergență din LISTA de firme"** | R81, 27–28.08 | caseta e pe ecranul **firmei** (`meniuFirma`), nu în listă. Scris din memoria structurii; a produs o măsurătoare falsă în proba W înainte de a fi prinsă |
| **43** (facturi declarabile — numitorul lui „28 din 43, 65%") | R35, 24.08; purtată de-atunci în R87, R88 și în predare | **41** azi, cu instrument (`scripts/sonda_facturi_necontate.py`). Termenii lui „43" nu se reconstituie: în bază sunt 41 de facturi **în total**, iar în **aceeași zi** cealaltă măsurătoare — R36 — scria „41 de facturi, 34 de note". Două cifre despre același obiect, în aceeași zi. *Numărătorul (28) și TVA-ul (102.260,00) se refac exact.* |
| **44 de restanțe deschise · prag 2 = 15** | predarea din 29.08, dimineață | **45** și **17**, numărate mecanic pe câmpul `unde intră`. Vechea defalcare (15+12+16=43) nu se închidea cu totalul ei |

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Blocul de cifre e derivat din date VII, nu din cod.** Dacă portofoliul se schimbă între
  generarea blocului și sfârșitul porții (~12,5 min), garda **pică** — și pe drept: documentul chiar
  nu mai descrie baza. Remediul e regenerarea. Operațional: blocul se regenerează **ultimul**.
- **Predarea nu se mai poate scrie fără acces la bază.** În fluxul de azi e întotdeauna adevărat.
  Scenariul în care nu e: un incident cu baza jos — atunci nu se poate rula nici poarta, deci nu se
  comite nimic, dar **handover-ul e blocat exact când e mai necesar**.
- **Gardul de cifre nu interzice o cifră de date în PROZA predării.** Ce nu mai are voie e ca
  **tabelul** să fie scris din memorie.
- **Confirmările nu sunt citite de nimeni în afară de mine.** Că textul e bun pentru un contabil e o
  judecată de om, nu o măsurătoare. Ce s-a probat e că **apare** și **ce scrie**.
- **`ALFA MICRO SRL` a fost dezactivată și reactivată de două ori azi**, deliberat, ca probă. De
  fiecare dată restaurarea a stat în `finally`, iar starea finală s-a **citit** din bază.
- **Verificarea reală a rămas pe O SINGURĂ poziție.** Un „0 divergențe" pe o mulțime de un element
  spune mult mai puțin decât pare — iar cele 25 de perechi fără tichete nu pot arăta nimic nici
  despre aia.
- **Brutul din notă nu mai e confruntat cu nimic**, și e o pierdere asumată, nu un câștig.
- **Nimeni nu consumă încă `s["cam"]`.** Reparația scoate **capcana**, nu adaugă o capabilitate.
- **Harta ZZ2 e pe AST, deci vede ce SCRIE în `inregistrari`** — nu vede un fapt economic pe care
  aplicația nu-l modelează deloc. Un fapt fără obiect și fără rută nu apare nici ca automat, nici ca
  gol: **nu apare.**
- **R87 și R88 n-au fost reparate**, cerut explicit. Ruta de contabilizare există și funcționează —
  lipsește **legătura**, nu capabilitatea.
- **Cifra e re-măsurată azi, cu instrument: 28 din 41, 102.260,00 lei, 10 firme.** Numitorul „43"
  e **INVALIDAT** — vezi tabelul. Iar pe a doua citire, „fără notă de **contare**", sunt **31 din 41**
  și **103.163,00 lei**: trei facturi au cheia ocupată de o notă de **plată**.
- **Gaura de idempotență e măsurată: 14 note pe citirea largă, 2 pe cea strictă, ZERO coliziuni reale.**
  **Dar zeroul nu absolvă nimic**, și e partea care contează: pe toate cele 19 scheme, `sursa='manual'`
  apare de **zero** ori. Calea liberă (`POST /jurnal`) — chiar calea pe care AAA7 o numea periculoasă —
  **n-a fost folosită niciodată**. Nu s-a măsurat că gaura e inofensivă, ci că **nimeni n-a intrat încă
  pe ușa prin care se cade**. *Punctul orb e FIRMA, nu ecranul.*
- **Mecanismul `factura_id` greșește în AMÂNDOUĂ direcțiile, iar reversul nu era numit nicăieri.**
  O notă care poartă cheia și **nu** e o contare **blochează** contarea: `factura_contabilizeaza` refuză
  pe `COUNT(*)`, fără să se uite la ce e nota. **3 facturi** sunt exact așa azi.
- **Nicio factură din lista istorică n-ar fi refuzată azi pentru lună închisă** (0 pe criteriul mecanic,
  1 pe „sub ultima blocată"). *E o stare a datelor de test, nu o proprietate a stocului — pe date reale
  proporția s-ar inversa.* Riscul 1 din AAA5 rămâne scris.
- **Clasa „verde peste gri" e azi LATENTĂ** — n-a fost prinsă nicio instanță vie, fiindcă semnalul
  pe 4428 nu se aprinde pe datele curente. S-a reparat pe **clasă**, nu pe instanță.
- **Sonda R35 nu întreabă dacă facturile alea CHIAR trebuiau contabilizate în luna aia.**
- **Cele 16 restanțe „fără prag declarat" sunt cele vechi (R1–R27)** — nu înseamnă că sunt ușoare,
  înseamnă că n-au fost încadrate când s-a introdus scara de praguri.
- **Câmpul `fel` e aditiv: ecranul nu-l citește.** Azi nu ascunde nimic — cele patru nu pot diverge —
  dar în ziua în care ar apărea un roșu de regresie, omul l-ar vedea la fel cu unul real.
- **Cifra R34 de azi (24 pe 7) nu e cea din 24.08 (29 pe 10).** Măsurătoarea de atunci n-a lăsat
  instrument, deci fereastra ei de luni nu se poate reconstitui. Ce **se** reproduce exact, cifră cu
  cifră, e cazul cel mai mare: `tenant_001` 2026-06. Ancora ține; contorul nu.
- **Cele 10 perechi nemăsurabile** (`tenant_003` pontaj neconfirmat, `tenant_016` date invalide) sunt
  cele deja documentate la R34. Nu s-au ascuns ca să iasă un total rotund.
- **Cele 45 de rute GRI rămân GRI.** S-a reparat raportarea, nu orbirea.
- **`_bannerFirma` dispare după 8 secunde.** Cine se uită în altă parte pierde confirmarea — la fel
  ca înainte, dar acum are ce pierde. Nu s-a măsurat dacă 8 secunde ajung.

---

## OPERAȚIONAL — ce se rupe repetat

- Serverul e `ssh iconta`; `psql` direct e blocat — script prin stdin, cu `db.init_pool()`.
- **Env obligatoriu**: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a`.
- **Un escape de tip BACKSPACE într-un literal ne-raw devine octet de control.** Prins în cod de
  `test_octeti_invizibili`, iar de azi **și în mesajul de commit**.
- **Ghilimelele românești rup șirul Python** — literal triplu.
- **O probă care ține o tranzacție deschisă nu poate deschide o a doua conexiune pe același rând.**
- **O probă pe ecran care dezactivează o firmă nu mai găsește lista de firme** — se așteaptă
  `button.firme-rand, .firme-gol`, nu doar primul.
- **Un patch rulează PE SERVER** (CRLF tăcut pe Windows).
- **O schimbare de JS cere**: `versioneaza_assets.py --scrie` **și**
  `frontend_test/vizual/interactiune_scan.py` (~7 min, artefactul se comite).
- **Trei blocuri generate cer regenerare**: `TRASEE.md` (la refuzuri noi), `GARZI.md` (la gărzi noi),
  **`PREDARE_LANT.md`** (la orice schimbare de date).

---

## DACĂ CONTINUI DE AICI

1. **Nu e nicio cerință comandată neîncepută. Nicio restanță de prag 1 deschisă.**
   Ce așteaptă: **TVA la încasare** (R88, un singur punct) și **decizia pe stocul istoric** (R89, cu
   lista deja scrisă). Proiectarea R87/R88 **nu mai e o întrebare deschisă** — e în `DECIZII.md`.
2. **Nu porni nicio construcție fără măsurătoare.**
3. **`scripts/raport_b.py` derivă „Unde suntem".** Nu se scrie de mână.
4. **Raportul se scrie din `SABLON_RAPORT.md`.**
