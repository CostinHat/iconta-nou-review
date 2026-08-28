Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — R81 e decisă și aplicată, iar garda ei a găsit o cale pe care măsurătoarea n-o văzuse (28.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-28**, a doua oară în aceeași zi. *Rescriere COMPLETĂ, nu petic.*
- **pe commit**: `08743aa` — starea pe care o descrie.
- **rescrierea de dinainte**: `be25471`, aceeași zi. Între ele a încăput **1 commit**.
- **de ce acum**: predarea de dimineață spunea *„ce rămâne deschis e o singură decizie"*. Decizia a
  venit în tura următoare, s-a aplicat, iar R81 e închisă. Un registru care descrie o restanță
  deschisă după ce ea s-a închis nu e vechi, e fals. *Conținutul, nu contorul* — măsurat cu formula
  din `pre-commit`: **1** commit în urmă, pragul e **10**, avertismentul n-a apărut.
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut.

---

## PRIMUL LUCRU DE ȘTIUT: R81 E DECISĂ, APLICATĂ ȘI ÎNCHISĂ

**Decizia lui Costin, textual:** *„simetrie de scriere. Orice act care redenumește o firmă scrie
denumirea în AMBELE locuri (`public.tenants.nume` și `{schema}.firma_profil.nume`), în aceeași
tranzacție, cu aceeași valoare. **Nu se construiește alias.**"*

Blocurile **O** (implementare), **P** (migrare) și **Q** (texte) sunt făcute, toate în `08743aa`.
`DECIZII.md` poartă decizia cu temeiul ei; `CONFORMITATE.md` o închide.

| bloc | ce s-a făcut |
|---|---|
| **O1–O3** | cele trei căi de redenumire trec prin **un singur scriitor**, `tenant_provisioning.scrie_denumirea` |
| **O3, răspunsul explicit** | **DA**, „Date firmă" avea o cale de editare directă a denumirii fiscale (`CAMPURI[0]`); trece și ea prin scriitor |
| **O4** | `core/scan_simetrie_denumire.py` + `core/test_simetrie_denumire.py` — **13 teste, 5 de calibrare** |
| **O5** | probă pe viu, savepoint, toate trei căile: amândouă coloanele, aceeași valoare; după rollback nimic atins |
| **P1–P3** | cele patru fixturi migrate, cu valoarea veche în `audit_log`; **0 divergențe pe toată populația** |
| **Q1–Q2** | textul revine la forma simplă, marcajul `data-e1` rămâne ca gardă de regresie |

---

## CE A GĂSIT GARDA, ȘI DE CE CONTEAZĂ MAI MULT DECÂT CE A REPARAT

**A patra cale asimetrică**: `precompleteaza_din_anaf(seteaza_nume=True)`, pe `POST /auth/register`,
scria `firma_profil.nume` **singur** — la câteva milisecunde după ce `provision_tenant` pusese
aceeași valoare în amândouă locurile.

**Deci propoziția scrisă de mine ieri în R81 — *„divergența nu se poate naște la creare"* — era
adevărată despre `POST /tenants` și falsă despre `POST /auth/register`.** N-a prins-o nicio citire,
nicio recitire și niciun raport: a prins-o un scan construit pentru altceva, la prima rulare.

**Lecția, și e a treia instanță în două zile:** o măsurătoare făcută **cu mâna** pe o clasă declarată
(„cele trei căi care redenumesc") găsește exact membrii la care te-ai uitat. Celelalte două instanțe
din 28.08: *„4 din 6 acte tăcute"* a devenit **4 din 7** când s-a măsurat pe rută în loc de fișier;
clichetul de **4** divergențe a devenit **0** când populația a fost declarată.

---

## O REGRESIE PE CARE SIMETRIA AR FI INTRODUS-O, dacă ecranul rămânea neatins

Ecranul „Date firmă" are **două** casete de denumire — `df-nume-portofoliu` (trimite
`PUT /tenants/{id}`) și `df-nume` din `CAMPURI` (trimite `POST …/firma-profil/date`). Salvarea
trimite **ambele cereri, în ordine**. Sub simetrie amândouă scriu amândouă coloanele, deci cine ar fi
editat numai caseta de sus **și-ar fi văzut modificarea revenită în tăcere** de a doua cerere, care
duce mai departe valoarea veche.

Reparat prin **legarea** celor două casete, în amândouă direcțiile, cu etichetele care spun că e
aceeași denumire. **Nicio casetă scoasă, nimic mutat** — comasarea lor într-una singură e o schimbare
de așezare și **se cere**.

---

## STAREA LA PREDARE

Poartă verde la `08743aa`: **3437 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator **TOTAL 0** ·
site **200** · four-way `HEAD = origin/main = origin/backup/lant-2026-08-28`.
*(Se reverifică rulând poarta, nu se crede pe cuvânt.)*

**Cifrele nu se scriu aici** — `scripts/raport_b.py`. **Poarta durează ~12 minute.** Comite prin
`nohup … &` și așteaptă separat.

---

## CE E ADEVĂRAT ACUM DESPRE CELE PATRU RESTANȚE DE DENUMIRE

| | |
|---|---|
| **R81** (REZOLVATĂ) | Simetrie de scriere, aplicată pe toate cele **patru** căi, cu gardă pe AST și probă pe viu. Cele patru divergențe de fixtură — migrate. **Nu s-a construit niciun alias.** |
| **R82** (DESCHISĂ, INTERN) | Cele **patru** acte de nivel firmă tot se termină în tăcere. Regula e scrisă (DS cap.27), clasa e măsurată (**4 din 7**) și clichetată. **Repararea lor e altă tură.** |
| **R79** (REDESCHISĂ) | Neatinsă azi. Ce rămâne e decizia despre `firme_scoase.schema_name`: informativ, sau nume de schemă care nu se mai reciclează. |
| **R77** (REZOLVATĂ) | Simetria **nu-i schimbă starea**, și motivul e scris acolo: axa e alta — portofoliu ↔ **ANAF**, nu portofoliu ↔ fiscal. Două afirmații ale unor actori diferiți **au voie** să difere; de-aia acolo răspunsul e o *alegere*, nu o sincronizare. |

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează.*
*Tabelul se POARTĂ, nu se deleagă în istoric — `core/test_predare_proaspata.py` o cere, și are dreptate.*

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

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Simetria e o afirmație despre codul APLICAȚIEI.** Un semănător, un import sau un `UPDATE` de mână
  nu trec prin scriitorul unic — și **chiar așa s-au născut cele patru divergențe migrate azi**.
  De-aia clichetul pe **date** rămâne, deși invariantul îl face structural imposibil.
- **Textul nou de pe ecran n-a fost văzut de un om pe o firmă cu divergență reală** — dar motivul
  nu e cel pe care îl scrisesem. *(Prima formă a rândului ăstuia spunea „**0 din 18** firme au
  `nume_anaf`". **Fals**, și e o cifră pe care propriul meu tabel de cifre invalidate o corectase deja
  o dată: „0 din 17" fusese invalidată pe 27.08 în favoarea lui „1 din 18". Am purtat-o mai departe
  din memorie, la douăzeci de minute după ce scrisesem §10.16 despre exact asta.)*
  **Recitit la 04:40:45, pe date:** **1 din 18** firme are `nume_anaf` — `Antibiotice Iasi` (33394),
  iar denumirea **chiar diferă** de cea de la ANAF (`ANTIBIOTICE SA`). Caseta tot nu apare, dar
  fiindcă **alegerea a fost deja făcută** (`nume_ales='aplicatie'`), nu fiindcă n-ar exista
  divergență. Deci calea **există** și e la o resetare de alegere distanță. S-a probat ce
  **randează** ecranul (scan de interacțiune + axe pe 14 ecrane, **0 violări**), nu ce vede cineva
  care are divergența în față.
- **Cele patru acte tăcute tot tac.** R82 e deschisă.
- **Gardul de simetrie nu urmărește apeluri în adâncime.** O funcție-intermediar care ar chema doar
  jumătate din scriitor n-ar fi văzută — dar nici n-are ce, cât timp scriitorul e o singură funcție
  care le face pe amândouă.
- **E1 nu cere «când coincid, se spune și asta».** Ramura e condiționată la rulare; un scan static
  nu poate deosebi ce se randează de ce nu. Regulă scrisă, nepăzită.
- **`GARZI.md` e cu șase zile în urmă** (ultima intrare: 22.08). Nici gărzile de azi nu sunt în el.
- **Convenția `REGISTRE` vs. blocurile cu literă tot nu e în `CLAUDE.md`.**
- **Ce n-a fost măsurat, și se știe:** dacă vreo declarație **deja depusă** poartă o denumire diferită
  de cea de azi. E o măsurătoare separată, pe `declaratii_depuse` — iar migrarea de azi a schimbat
  denumirea a patru firme, deci întrebarea e acum mai concretă decât era ieri.

---

## OPERAȚIONAL — ce se rupe repetat

- Serverul e `ssh iconta`. `psql` direct e **blocat**: pentru DB se trimite un script prin stdin —
  `cat script.py | ssh iconta '… ./venv/bin/python -'` — cu `sys.path.insert(0, …)`, `from core
  import db`, **`db.init_pool()`**.
- **Env obligatoriu**: `set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a`.
- **O probă care ține o tranzacție deschisă nu poate deschide o A DOUA conexiune pe același rând** —
  se blochează pe lock, tăcut, până la timeout. Instanța de azi: proba O5, rescrisă pe o singură
  conexiune cu `SET LOCAL search_path`.
- **Un script de patch rulează PE SERVER**, nu pe stație (CRLF tăcut). După orice patch:
  `b.count(b"\r\n") == 0`.
- **Mesajul de commit se trimite prin FIȘIER.**
- **Ghilimelele românești rup șirul Python** — `„text"` într-un literal cu ghilimele duble e eroare
  de sintaxă la linia următoare. Remediul: literal triplu.
- **O schimbare de JS cere, înainte de poartă**: `versioneaza_assets.py --scrie` **și**
  `frontend_test/vizual/interactiune_scan.py` (~8 minute, artefactul se comite).
- **O schimbare de cod care adaugă refuzuri explicite cere regenerarea blocului din `TRASEE.md`**
  (`scripts/scan_trasee.py --md`, rescris între marcaje). Azi: 162 → 164.

---

## DACĂ CONTINUI DE AICI

1. **Nu e nicio cerință comandată neîncepută.** Ce așteaptă e răspunsul lui Costin la §0.
2. **Nu porni nicio construcție fără măsurătoare** — azi, de trei ori din trei, măsurătoarea a
   schimbat cifra sau clasa.
3. **`scripts/raport_b.py` derivă secțiunea „Unde suntem".** Nu se scrie de mână.
4. **Raportul se scrie din `SABLON_RAPORT.md`.** Ordinea: 0 CERINTE · 1 CE AM PRESUPUS · 2 ÎN
   PLUS/MAI PUȚIN · 3 CE AM ACTUALIZAT · 4 ÎNȚELEGEREA · 5 RĂSPUNS LA COMANDĂ · 6 UNDE SUNTEM ·
   7 POARTA.
