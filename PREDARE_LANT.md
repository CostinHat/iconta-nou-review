Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — cele treisprezece cerinţe sunt făcute, iar ce rămâne deschis e o singură decizie (28.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-28**. *Rescriere COMPLETĂ, nu petic.*
- **pe commit**: `864edb8` — starea pe care o descrie.
- **rescrierea de dinainte**: `4ffbcd1`, 27.08 târziu. Între ele a încăput **1 commit**.
- **de ce acum, deși pragul nu sunase**: `git rev-list --count $(git log -1 --format=%H -- PREDARE_LANT.md)..HEAD` → **1**; pragul e **10**, avertismentul **nu** a apărut. Motivul e **conținutul**: predarea de ieri își începea primul capitol cu *„TREISPREZECE CERINȚE COMANDATE, ZERO ÎNCEPUTE."* Toate treisprezece sunt făcute. Lăsată așa, ar fi fost un registru care minte, nu unul vechi.
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri; `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut. Avertizează, nu blochează.

---

## PRIMUL LUCRU DE ȘTIUT: BLOCURILE E, F, G, H SUNT FĂCUTE — TOATE

Ultima comandă a lui Costin a dat patru blocuri, treisprezece cerințe. **Toate sunt în `864edb8`.**
Ce **nu** s-a făcut, și e scris explicit acolo unde trebuia: **nimic din R81**. Decizia nu e luată,
ramura `anaf` scrie azi exact ce scria ieri.

| bloc | ce s-a făcut | unde trăiește |
|---|---|---|
| **E1** | regula *„două lucruri diferite primesc două nume distincte"*, cu instanțele R63 și R81 | `DESIGN_SYSTEM.md` cap.26 · `core/scan_ecran_reguli.py` · `verificator_conformitate.py` |
| **E2** | regula *„un act se încheie cu o confirmare vizibilă"*, cu instanța măsurată | `DESIGN_SYSTEM.md` cap.27 · aceleași două instrumente |
| **E3** | regula recitirii stării, cu instanța de la 19:27 | `METODA_VERIFICARE.md` §10.16 |
| **F1–F4** | afirmația falsă de pe ecran, reparată; butoanele își spun fapta; testul ancorat pe comportament | `static/js/ecrane/firme.js` · `core/test_nume_anaf.py` · R82 |
| **G1** | clichetul orfanilor, bidirecțional, cu motivul scris | `core/test_tenant_stergere.py` |
| **G2** | gardă pe cale moartă, **marcată**, nu ștearsă, plus clichetul care ține marcajul onest | `core/test_nume_anaf.py` |
| **G3** | nota de lângă coloană în amândouă locurile de DDL + garda pe citirea cheiată | `core/migrare_firme_scoase.py` · `infra/bootstrap_public.sql` · `core/test_tenant_stergere.py` |
| **H1–H2** | populația declarată, cu excludere verificată; clichetul recalculat **4 → 0** | `core/test_nume_firma_unic.py` |
| **H3** | *o cifră despre „firme reale" declară populația, sau nu se scrie* | `METODA_VERIFICARE.md` §26 |

---

## INSTRUMENTUL NOU, ȘI DE CE E ALTFEL DECÂT UN REGEX

`core/scan_ecran_reguli.py` — **sparge sursa în NODURI înainte de a aserta pe ea**, fiindcă amândouă
regulile sunt despre *ce conține un nod*:

- **nodul de randare** (E1): literalii de șablon se parsează ca HTML, cu interpolările `${…}`
  înlocuite **înainte** de parsare — altfel un `${a > b ? …}` ar rupe arborele, și l-ar rupe tăcut.
  Aserțiunea e pe **descendență**.
- **blocul de execuție** (E2): sursa se tokenizează (fără comentarii, fără **conținutul** șirurilor)
  și se sparge în blocuri `{ }`. Aserțiunea e pe **conținutul blocului `try`**.

**Calibrarea care contează e negativă, și e chiar defectul:** un `arataMesaj` din `catch` **nu**
confirmă nimic. Un gard care s-ar fi uitat în handler, nu în blocul `try`, ar fi declarat toate patru
actele confirmate — fiindcă toate patru vorbesc pe calea de eroare. Ar fi fost verde exact pe clasa
pentru care a fost construit.

**Limita, scrisă lângă instrument: nu e un parser de JavaScript.** Știe unde încep și unde se termină
blocurile și ce identificatori se cheamă; nu știe ce e expresie și ce e instrucțiune. Regula de
distincție `/` regex-vs-împărțire e cea standard, calibrată pe amândouă formele.

**A doua limită a instrumentelor de azi**, prinsă tot de calibrare: prima formă a lui `_pozitia_lui`
(G3) mergea înapoi **un singur jeton** și se oprea pe operand, deci nu vedea `ON a.s = f.schema_name`.
Reparată: merge înapoi până la primul **cuvânt-cheie SQL**.

---

## O CIFRĂ DE-A MEA, CORECTATĂ LA MĂSURAREA CU INSTRUMENT

R82 scria **„4 din 6"** acte de nivel firmă care se termină în tăcere. Măsurat acum pe **calea pe
care o lovesc**, nu pe fișierul în care stau: **4 din 7**. Cele patru tăcute sunt **aceleași**; al
șaptelea act e `PUT /tenants/{id}` din `date_firma.js`, care **confirmă**, și pe care numărătoarea de
mână nu-l văzuse fiindcă se uita numai în `firme.js`. **Numitorul se corectează, numărătorul nu** —
iar limita declarată atunci (*„s-a numărat un singur fișier"*) s-a dovedit exact acolo unde spunea că e.

---

## STAREA LA PREDARE

Poartă verde la `864edb8`: **3424 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator
**TOTAL 0** · site **200** · four-way `HEAD = origin/main = origin/backup/lant-2026-08-28 =
864edb8`. *(Se reverifică rulând poarta, nu se crede pe cuvânt.)*

**Cifrele nu se scriu aici** — `scripts/raport_b.py`.

**Poarta durează ~12 minute** (peste 3400 de teste). Comite prin `nohup … &` și așteaptă separat — o
sesiune `ssh` întreruptă la mijloc lasă fișierele *staged* și niciun commit.

---

## CE E ADEVĂRAT ACUM DESPRE CELE PATRU RESTANȚE DE DENUMIRE

| | |
|---|---|
| **R81** (DESCHISĂ, DECIZIE) | **Titlul s-a rescris**: *„Denumirea unei firme stă în două locuri, iar redenumirea atinge unul singur."* Divergența **nu se poate naște la creare** — `provision_tenant` scrie același șir în amândouă locurile. Se naște numai prin **redenumire ulterioară**, fiindcă `PUT` și ramura `anaf` ating **un singur loc din două**. Întrebarea nu mai e *„care denumire e adevărul"*, ci **„de ce redenumirea atinge unul singur"**. **Decizia NU e luată. Nu construi nimic pe ea.** |
| **R82** (DESCHISĂ, INTERN) | Cele **patru** acte tot nu confirmă nimic. S-a scris regula (DS cap.27), s-a măsurat clasa (**4 din 7**) și s-a pus clichetul, în ambele direcții, plus mulțimea exactă a rutelor. **Repararea lor e altă tură.** A primit F1–F4 ca instanță **cu efect fiscal** — reclasificare a lui Costin: *nu e prag 1*. |
| **R79** (REDESCHISĂ) | **G3 e făcut**: nota de lângă coloană, în amândouă locurile de DDL, plus garda care prinde o citire cheiată pe `schema_name`. Ce rămâne e chiar **condiția de deblocare**: se decide dacă `schema_name` rămâne informativ sau numele de schemă nu se mai reciclează. |
| **R77** (REZOLVATĂ pe scriere) | **G2 e făcut**: `test_o_citire_ANAF_mai_noua_REDESCHIDE_intrebarea` e marcată **gardă pe cale moartă**, cu condiția care ar învia-o, iar marcajul e ținut de un clichet pe cele **3** căi de captare ANAF. |

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează.*

*Tabelul se POARTĂ, nu se deleagă în istoricul git.* Prima formă a predării de azi trimitea la
`git show 4ffbcd1:PREDARE_LANT.md` — și a fost respinsă de `core/test_predare_proaspata.py`, care
cere ca cifra **131** să fie **în** predare. Gardul are dreptate: o cifră invalidată pe care trebuie
s-o cauți în istoric e o cifră pe care n-o mai citește nimeni. Ultimele două rânduri sunt de azi.

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

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Cele patru acte tot tac.** S-a scris regula și s-a pus clichetul; **nu s-a reparat niciunul**.
- **E1 nu cere «când coincid, se spune și asta».** Partea aia e condiționată la rulare, iar un scan
  static nu poate deosebi ramura care se randează de cea care nu. **Regulă scrisă, nepăzită.**
- **E1 nu prinde R63.** Cele două adrese trăiesc pe **două ecrane diferite**, prin chiar decizia (c) a
  restanței. Se scrie în cap.26, ca să nu pară omisiune.
- **Niciun gard nu judecă TEXTUL confirmării.** „Salvat" trece pe mecanică și pică la citire.
- **Cele trei cabinete „Proba …" nu sunt excluse din populație.** Au **0 firme** azi, deci nu ating
  cifra, și pentru ele n-am o decizie de citat. În ziua în care primesc firme, cifra crește.
- **Verde nu înseamnă exercitat.** Textul reparat pe ecran n-a fost văzut de un om pe o firmă cu
  divergență reală: **0 din 18** firme au `nume_anaf`, deci caseta nu se poate declanșa azi. Ce s-a
  probat e ce **randează** ecranul (scan de interacțiune + axe, 14 ecrane, 0 violări), nu ce vede
  cineva care chiar are divergența.
- **Cei 67 de orfani dinainte rămân.** Decizia lui Costin. Acum contorul e bidirecțional: și o
  **scădere** îl aprinde.
- **Baseline-urile nu sunt curate.** Sunt fotografii. Gărzile spun că **nu cresc**, nu că listele
  sunt adevărate.
- **Convenția `REGISTRE` vs. blocurile cu literă tot nu e în `CLAUDE.md`.** Costin a dat-o pe 27.08:
  *„`REGISTRE` listează minimul obligatoriu; o scriere comandată explicit într-un bloc cu literă e
  autorizată prin faptul că e comandată."* Rămâne **cerință deschisă către el**, nu ceva de scris tăcut.
- **Ce n-a fost măsurat, și se știe:** dacă vreo declarație **deja depusă** poartă o denumire diferită
  de cea din portofoliu de azi. E o măsurătoare separată, pe `declaratii_depuse`.

---

## OPERAȚIONAL — ce se rupe repetat

- Serverul e `ssh iconta`. `psql` direct și `systemctl restart` sunt **blocate** de stație: pentru DB
  se trimite un script prin stdin — `cat script.py | ssh iconta '… ./venv/bin/python -'` — cu
  `sys.path.insert(0, "/home/costin/iconta_nou")`, `from core import db`, **`db.init_pool()`**.
- **Env obligatoriu** pentru orice rulează cod de aplicație:
  `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a`.
- **Un script de patch rulează PE SERVER, nu pe stație** — pe Windows scrierea trece fișierul la CRLF
  în tăcere. După orice patch: verifică `b.count(b"\r\n") == 0`. *(Verificat pe fiecare fișier atins azi.)*
- **Mesajul de commit se trimite prin FIȘIER**, niciodată prin heredoc în argumentul `ssh`.
- **Ghilimelele românești rup șirul Python**: `„text"` într-un literal cu ghilimele duble e eroare de
  sintaxă la linia următoare. S-a întâmplat de **două** ori azi, în scripturile de patch. Remediul e
  literalul triplu.
- **O schimbare de JS cere două lucruri înainte de poartă**: `./venv/bin/python versioneaza_assets.py
  --scrie` și `frontend_test/vizual/interactiune_scan.py` (are nevoie de env + `PYTHONPATH`, durează
  ~8 minute, scrie `acoperire_vizuala.json`, care se **comite**).
- **Sondele care „doar citesc" pot scrie.** Orice probă pe date reale se rulează în tranzacție
  întoarsă la `SAVEPOINT`.

---

## DACĂ CONTINUI DE AICI

1. **Nu e nicio cerință comandată neîncepută.** Ce așteaptă e **răspunsul lui Costin** la cele din
   §0 al raportului de azi.
2. **R81 NU e decisă.** Nu construi nimic pe ea, și nu schimba ce scrie ramura `anaf`.
3. **Nu porni nicio construcție fără măsurătoare.** Azi, iarăși: măsurătoarea a schimbat numitorul
   lui R82 și a golit clichetul divergențelor.
4. **`scripts/raport_b.py` derivă secțiunea „Unde suntem".** Nu se scrie de mână.
5. **Raportul se scrie din `SABLON_RAPORT.md`**, nu din memorie. Ordinea: 0 CERINTE · 1 CE AM
   PRESUPUS · 2 ÎN PLUS/MAI PUȚIN · 3 CE AM ACTUALIZAT · 4 ÎNȚELEGEREA · 5 RĂSPUNS LA COMANDĂ ·
   6 UNDE SUNTEM · 7 POARTA.
