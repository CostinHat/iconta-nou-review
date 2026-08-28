Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — direcția exista în cod de mult; ce lipsea era regula, iar fără ea golurile nu se puteau numi (29.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-29**, prima oară în ziua asta. *Rescriere COMPLETĂ, nu petic.*
- **pe commit**: `872526c` — ultimul commit intrat. *Predarea se scrie ÎNAINTE de commitul care poartă
  munca de mai jos, fiindcă blocul de cifre trebuie să intre ODATĂ cu ea. Ce descrie e arborele care
  devine commitul următor.*
- **rescrierea de dinainte**: `872526c`, ieri. Între ele au încăput **2 commituri**.
- **de ce acum**: **R36 s-a închis** — decizia care ține de ea restul lanțului de contabilizare.
  Și a produs o hartă, iar harta a produs **două restanțe noi**. *Conținutul, nu contorul* —
  măsurat cu formula din `pre-commit`: **2** commituri în urmă, pragul e **10**.
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

## AL DOILEA: DIRECȚIA EXISTA ÎN COD DE MULT — CE LIPSEA ERA REGULA (R36)

**Decizia lui Costin, varianta (a):** *aplicația contabilizează automat orice fapt economic nou
construit; ruta manuală există doar acolo unde e declarată explicit, cu motivul scris.*

**Ce a scos măsurătoarea, și schimbă felul în care se citește restanța:** **nu era „ce direcție",
era „direcția nescrisă"**. Din faptele pe care aplicația le gestionează, cele mai multe
contabilizează automat **de mult** — NIR, descărcare de gestiune, casă, chitanță, bon, raport Z,
ieșiri din stoc, rețete, și toate cele ~30 de operațiuni speciale. Fără regulă însă, fiecare modul
nou putea alege altfel, la fel de legitim. *Numele restanței a fost corect de la început.*

**De ce nu (c) „hibrid, cu granița scrisă"** — deși (c) descrie exact ce se întâmplă azi: o graniță
trasată **acum** ar fi înghețat starea de fapt, **inclusiv golurile**. Cele două găsite azi ar fi
devenit „graniță", nu restanță. *O regulă care descrie ce e nu mai poate arăta ce lipsește.*

---

## AL TREILEA: HARTA — 48 de scriitori de note, 6 acte separate, 2 goluri

Criteriul nu e „există o rută", ci: **actul care construiește faptul scrie și nota, sau nota cere un
act separat, ulterior?**

**AUTOMAT (9 clase):** NIR · descărcare de gestiune · ieșire/inventar/reclasificare stoc · rețete ·
casă · chitanță și stingere bon · bon aprobat · raport Z și AMEF · cele ~30 de operațiuni speciale
*(acolo faptul și nota sunt același act — omul descrie o operațiune care n-are alt obiect)*.

**MANUAL (6):** factura emisă · factura primită · linia de extras bancar · statul de plată ·
amortizarea · nota liberă.

**Din cele 6: patru sunt excepții legitime, două sunt goluri.**

| excepție declarată | de ce rămâne manuală |
|---|---|
| nota liberă (`/jurnal`) | **supapa** pentru fapte pe care aplicația nu le modelează — n-are fapt declanșator |
| reconcilierea bancară | cere o **alegere care nu se poate deriva**: ce factură stinge o încasare |
| salariile | decizie explicită din 25.08 (propunere + patru-ochi) |
| amortizarea | **rulare de perioadă**, fără act al omului; are deja idempotență |

**GOLURI → R87 (factura emisă) și R88 (factura primită).** Efectul lor se vedea de mult, doar că nu
se numea așa: **R35 a măsurat 28 din 43 de facturi declarabile necontate — 65%, 102.260 lei TVA, pe
10 firme din 17.**

**Marginea pe care am refuzat s-o transform în restanță:** liniile de extras pe care potrivirea
automată le rezolvă **fără ambiguitate** ar putea urma automat. N-am măsurat câte sunt — *o restanță
pe o intuiție e o datorie fără cifră.*

---

## AL PATRULEA: CE A DEBLOCAT DECIZIA (ZZ5)

- **R39** — blocajul ei era literal *„se răspunde la R36"*. **S-a răspuns.** Cine scrie
  `document_ref` nu mai e o întrebare: îl scrie actul care produce nota. Restanța **nu se închide**
  (nu s-a construit nimic), dar **își schimbă natura: din DECIZIE în INTERN**, iar condiția se
  rescrie pe muncă, nu pe răspuns.
- **R37** — i se schimbă **domeniul, nu condiția**: sub (a), notele automate devin regula, iar **o
  notă automată n-are autor-persoană prin construcție**. „Autor" se citește ca *actul care a
  produs-o*, deci `sursa` **e** autorul — ceea ce face prima jumătate a condiției (nomenclator
  închis, într-un loc unic) **mai grea și mai importantă**, nu mai ușoară.
- **R34 și R35**, re-citite fiindcă chiar condiția lui R36 o cerea: **niciuna nu se redeschide.**
  R34 e despre ce cifră intră în notă, nu despre cine o produce. R35 își păstrează gardul **cu atât
  mai mult** — sub (a), o factură necontabilizată devine o **anomalie**, nu starea normală.

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
| **R36** (închisă; registrul o numește în commitul următor) | Varianta (a). Harta ZZ2-ZZ3 e în registru. |
| **R87** (DESCHISĂ, INTERN, prag 2) | **Nouă.** Factura EMISĂ nu produce nota; ruta de contabilizare există, dar n-o declanșează nimic. |
| **R88** (DESCHISĂ, INTERN, prag 2) | **Nouă.** Factura PRIMITĂ validată creează cheltuiala, nu și nota. |
| **R39** | DECIZIE → **INTERN**. Deblocată de R36; rămâne muncă, nu răspuns. |
| **R37** | Domeniul re-citit: pentru actele automate, `sursa` **e** autorul. |
| **prag 1** | **niciuna deschisă.** |
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
   **Nu e propus niciun pas următor** — ordinea o dă Costin. Ce a produs tura asta și așteaptă:
   **R87** și **R88**, amândouă INTERNE (muncă, nu decizie).
2. **Nu porni nicio construcție fără măsurătoare.**
3. **`scripts/raport_b.py` derivă „Unde suntem".** Nu se scrie de mână.
4. **Raportul se scrie din `SABLON_RAPORT.md`.**
