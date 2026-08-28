Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — cele patru restanțe de denumire sunt închise, iar o orbire care se citea VERDE de două zile s-a făcut vizibilă (28.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-28**, a treia oară în aceeași zi. *Rescriere COMPLETĂ, nu petic.*
- **pe commit**: `184add3` — starea pe care o descrie.
- **rescrierea de dinainte**: `3362fbb`, aceeași zi. Între ele a încăput **1 commit**.
- **de ce acum**: șase blocuri de decizii aplicate într-o tură (R, S, T, U, V, X + proba W). Predarea
  de dimineață descria trei restanțe deschise care s-au închis între timp. *Conținutul, nu contorul*
  — măsurat cu formula din `pre-commit`: **1** commit în urmă, pragul e **10**.
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut.

---

## PRIMUL LUCRU DE ȘTIUT: NU E NICIO CERINȚĂ COMANDATĂ NEÎNCEPUTĂ

Toate cele șase blocuri sunt aplicate, plus proba W. **R79, R80 și R81 nu mai blochează.**

| bloc | ce s-a făcut |
|---|---|
| **R** | cele două casete de denumire s-au **comasat** — duplicatul iese, legarea de acum câteva ore se scoate |
| **S** | **GRI nu se mai falsifică în verde**: patru verdicte pe rute, GRI numărat separat în raportul porții |
| **T** | numele de schemă **nu se mai reciclează** — secvență Postgres pornită de la maximul istoric |
| **U** | `GARZI.md` rămâne **viu**: backfill 23–28.08 + inventar **generat** și păzit |
| **V** | convenția `REGISTRE` vs. blocurile cu literă, scrisă verbatim în `CLAUDE.md` §2.2.1b |
| **X** | excluderea cabinetelor de test trece de la **listă de id-uri** la **tipar de nume**, cu clichet |
| **W** | divergență **vie**, văzută pe ecran real, apoi ștearsă |

---

## CE A GĂSIT FIECARE, DINCOLO DE CE A REPARAT

**S — o orbire care se citea VERDE de două zile.** Detectorul de apelanți avea **două** răspunsuri;
rutele pe care ancora literală nu le identifică cădeau **prin construcție** în primul, fiindcă ancora
lor apare peste tot. Deci „nicio rută fără apelant" era adevărat despre 334 de rute și **mut** despre
45, iar mutul se citea ca verde. Acum: **411 = ACCEPTAT 334 + GRI 45 + ROSU 0 + EXCLUS 32**, tipărit
în raportul porții la fiecare commit.

**W — două lucruri pe care niciun scan nu le prinsese.** (1) Caseta de divergență **nu e în lista de
firme**, cum scrisesem în R81, ci pe ecranul **firmei**; prima formă a probei a căutat-o în listă și
a raportat *„nu apare"* — **măsurătoarea greșea, nu ecranul**. (2) Textul spunea *„(citită acum
azi)"*. Un `axe` n-are ce să reclame la asta; **se vede numai cu ochii**, care e chiar motivul pentru
care W a fost cerut.

**U — un registru care s-ar fi stricat prin propria actualizare.** Prima formă a inventarului generat
grupa gărzile pe ziua primului commit — dar fișierele din commitul **curent** n-au încă una. Blocul
ar fi intrat cu `—` și s-ar fi schimbat singur imediat după commit, făcând garda doc↔cod roșie la
următoarea rulare. Inventarul e acum **fără date**; datele trăiesc în intrările narative.

**Poarta, de două ori.** Un octet `BACKSPACE` strecurat într-un comentariu (scrisesem un `\b` într-un
literal ne-raw, în scriptul de patch) — și apoi **din nou în mesajul de commit care descria
greșeala**. Iar `test_g9_oblig_backend` a picat pe scoaterea câmpului `nume` din `CAMPURI`:
reparația **nu** a fost să scot obligația din backend, ci să învăț **garda** să vadă caseta de
deasupra grilei. Obligația nu dispăruse, se mutase.

---

## STAREA LA PREDARE

Poartă verde la `184add3`: **3450 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator **TOTAL 0** ·
rute **411 = ACCEPTAT 334 + GRI 45 + ROSU 0 + EXCLUS 32** · site **200** · four-way
`HEAD = origin/main = origin/backup/lant-2026-08-28`. *(Se reverifică rulând poarta.)*

**Cifrele nu se scriu aici** — `scripts/raport_b.py`. **Poarta durează ~12,5 minute.**

---

## CE E ADEVĂRAT ACUM DESPRE RESTANȚELE DE DENUMIRE ȘI DE RUTE

| | |
|---|---|
| **R81** (REZOLVATĂ) | Simetrie de scriere pe toate cele **patru** căi + cele două casete comasate. Nu s-a construit niciun alias. |
| **R82** (DESCHISĂ, INTERN) | Cele **patru** acte de nivel firmă tot se termină în tăcere (**4 din 7**). Regula e scrisă, clasa e clichetată. **Repararea lor e altă tură** — și e singura restanță de ecran rămasă. |
| **R79** (REZOLVATĂ) | Amândouă jumătățile probate: auditul nu mai lasă orfani (27.08) **și** numele de schemă nu se mai reciclează (azi, probat A→`tenant_020`, ștearsă, B→`tenant_021`). |
| **R80** (DESCHISĂ, **INTERN**) | Decizia (c) e luată, deci nu mai așteaptă răspuns: `cine deblochează` a trecut din DECIZIE în INTERN. Ce o ține deschisă e **munca** — clasa GRI se golește când se construiește (a) sau (b). |

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează. Tabelul se
POARTĂ, nu se deleagă în istoric.*

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

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **GRI nu e „aproape verde".** Cele 45 de rute rămân rute despre care **nu se poate afirma nimic**.
  Ce s-a reparat e că nu mai *arată* ca verzi; orbirea e aceeași.
- **Contorul de scheme oprește reciclarea DE-ACUM ÎNAINTE.** Cele două rânduri `tenant_019` din
  `firme_scoase` **rămân** — sunt istorie, dezambiguizată de `tenant_id`. R79 se închide fiindcă *nu
  se mai poate produce*, nu fiindcă trecutul s-ar fi curățat.
- **Backfill-ul din `GARZI.md` NU spune de ce a fost construită fiecare gardă.** Spune **ce** a intrat
  și **ce afirmă fiecare despre sine** — amândouă verificabile. *De ce*-ul zilelor 23–26.08 ar fi fost
  reconstruit din numele fișierelor, adică exact ce METODA interzice.
- **Inventarul generat nu judecă dacă o gardă e bună.** Nu numără aserțiuni, nu spune dacă păzește
  ceva viu. Pentru aia sunt instrumentele de FAZA 4.
- **Tiparul de cabinet de test nu prinde „TESTARE SRL"** — `\b` cere cuvântul întreg. **Deliberat**:
  un cabinet de test nedeclarat intră în cifră și o strică **vizibil**; unul real exclus tăcut ar face
  cifra să arate mai curată. Prima greșeală se vede, a doua nu.
- **Textul nou de pe ecran a fost văzut o dată, pe o firmă fabricată de mine.** Nu de un contabil, pe
  firma lui.
- **`Antibiotice Iasi` (33394) rămâne cu alegerea consemnată** — nu s-a atins, cum s-a cerut.
- **Propunerea din `METODA §10.16b` e NECONSTRUITĂ:** cifrele „X din Y" din predare se scriu tot de
  mână. Ce s-a scris e unde ar intra controlul, nu controlul.

---

## OPERAȚIONAL — ce se rupe repetat

- Serverul e `ssh iconta`. `psql` direct e **blocat**: script prin stdin,
  `cat x.py | ssh iconta '… ./venv/bin/python -'`, cu `db.init_pool()`.
- **Env obligatoriu**: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a`.
- **`\b` într-un literal Python ne-raw devine un octet BACKSPACE.** S-a întâmplat de **două** ori
  azi, a doua oară chiar în mesajul care descria prima. `core/test_octeti_invizibili.py` îl prinde în
  cod; în **mesajul de commit** nu-l prinde nimic — se verifică de mână.
- **Ghilimelele românești rup șirul Python** — remediul e literalul triplu.
- **O probă care ține o tranzacție deschisă nu poate deschide o a doua conexiune pe același rând.**
- **Un patch rulează PE SERVER** (CRLF tăcut pe Windows). După: `b.count(b"\r\n") == 0`.
- **O schimbare de JS cere**: `versioneaza_assets.py --scrie` **și**
  `frontend_test/vizual/interactiune_scan.py` (~8 min, artefactul se comite).
- **O schimbare de cod care adaugă refuzuri explicite cere regenerarea blocului din `TRASEE.md`**;
  **o gardă nouă cere regenerarea inventarului din `GARZI.md`**
  (`scripts/scan_garzi_inventar.py --md`).
- **Mesajul de commit se trimite prin FIȘIER**, și se verifică după commit.

---

## DACĂ CONTINUI DE AICI

1. **Nu e nicio cerință comandată neîncepută.** Ce așteaptă e răspunsul lui Costin la §0.
2. **R82 e singura restanță de ecran deschisă**: cele patru acte tăcute.
3. **Nu porni nicio construcție fără măsurătoare.**
4. **`scripts/raport_b.py` derivă „Unde suntem".** Nu se scrie de mână.
5. **Raportul se scrie din `SABLON_RAPORT.md`.**
