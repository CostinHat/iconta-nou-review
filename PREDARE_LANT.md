Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — ziua s-a terminat cu o măsurătoare care a desființat premisa unei restanțe, și cu treisprezece cerințe comandate și NEÎNCEPUTE (27.08.2026, târziu)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-27**, târziu. *Rescriere COMPLETĂ, nu petic.*
- **pe commit**: `d5e0ad5` — starea pe care o descrie.
- **rescrierea de dinainte**: `f07f8e6`, aceeași zi, seara. Între ele au încăput **2 commituri**.
- **de ce acum, deși pragul NU sunase — și cu o cifră care nu se confirmă a treia oară**: comanda
  spune *„e cu 12 commituri în urmă, peste prag, semnalat de două ture."* **Măsurat, cu chiar
  formula din `pre-commit`:** `git rev-list --count $(git log -1 --format=%H -- PREDARE_LANT.md)..HEAD`
  → **2**. Pragul e **10**. Avertismentul **nu a apărut** azi, la niciun commit. `PREDARE_LANT.md`
  a fost atins în `f07f8e6`, `04e6f38`, `0963d7f`, `ed7d16a`, `c9bf964` — niciodată mai vechi de
  3 commituri azi. **Cifra „12" a fost deja invalidată o dată azi (D4, raportul de la 21:0x) și a
  reapărut în comanda următoare.** Se scrie aici a treia oară ca să nu se mai repete.
  **Motivul REAL al rescrierii ține**: conținutul a îmbătrânit — o tură întreagă de măsurători
  peste el, plus treisprezece cerințe noi neîncepute. *Conținutul, nu contorul.*
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.**
- **gardat**: `scripts/githooks/pre-commit` avertizează peste 10 commituri;
  `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut. Avertizează, nu blochează.

---

## PRIMUL LUCRU DE ȘTIUT: TREISPREZECE CERINȚE COMANDATE, ZERO ÎNCEPUTE

Ultima comandă a lui Costin a dat patru blocuri de construit (E, F, G, H). **Tura a fost întreruptă
în timpul investigației, înainte de orice scriere.** Nimic din ele nu e făcut, nimic nu e pe jumătate
— arborele e curat. **Astea sunt primul lucru de făcut, nu o listă de idei.**

### BLOC E — cele trei reguli, scrise *(textele sunt deja formulate, în raportul de la D3/D5/D6; „nu le rescrie")*

- **E1.** Tiparul R63 intră în `DESIGN_SYSTEM.md`. Partea gardabilă mecanic intră în
  `verificator_conformitate.py`, **ancorată structural (noduri de randare), nu pe text**, conform
  clichetului 50. Instanțele R63 și R81 se scriu lângă regulă.
  *Textul regulii, ca formulat:* **Două lucruri diferite primesc două nume distincte.** Când aceeași
  entitate are un atribut în două locuri, ecranul nu alege tăcut între ele: le arată pe amândouă, cu
  etichete care spun **de unde vine fiecare**, iar când **diferă**, spune **care dintre ele produce
  efectul** (pleacă pe hârtie, ajunge la client, intră în calcul). Când coincid, se spune și asta.
- **E2.** Regula confirmării vizibile, aceleași două locuri. Instanța măsurată (**4 din 6** acte în
  `firme.js`, cu liniile) se scrie lângă ea.
  *Textul regulii, ca formulat:* **Un act cu efect asupra unei entități se încheie cu o confirmare
  vizibilă care numește entitatea și consecința.** Nu „Salvat": *„«BORG DESIGN SRL» a fost scoasă din
  portofoliu — datele ei nu mai există."* Demontarea ecranului **nu e** confirmare: „a dispărut"
  arată identic cu „a reușit" și cu „s-a rupt ceva". Cu cât actul e mai puțin reversibil, cu atât
  confirmarea e mai obligatorie.
- **E3.** Regula recitirii stării intră în `METODA_VERIFICARE.md` **§10**, cu instanța: *27.08, 19:27,
  `nume_ales` raportat NULL la 11 minute după ce fusese scris.*
  *Textul regulii, ca formulat:* **Orice stare afirmată ca ACTUALĂ se recitește imediat înainte de a
  fi scrisă în raport, nu la începutul turei.** O stare citită la minutul 3 al unei ture de 30 și
  raportată la minutul 30 e o **amintire**, nu o măsurătoare — și se scrie cu ora citirii. Corolarul:
  nicio propoziție de forma „e exact cum ai lăsat-o" fără o recitire între ea și trimiterea
  raportului. Sunt doi actori pe baza asta, nu unul.

### BLOC F — afirmația falsă de pe ecran *(reclasificată de Costin: **NU** e prag 1 — e o afirmație falsă despre ce pleacă pe declarația fiscală, afișată chiar în momentul în care omul alege, pe un ecran unde alegerea s-a și făcut o dată, pe o firmă reală)*

- **F1.** Caseta din lista de firme (`static/js/ecrane/firme.js`, în jur de l. 297) scrie
  *„Denumirea din aplicație e cea folosită în documente."* Probele A5/A6 arată că documentele iau
  `firma_profil.nume`. **Scrie ce e adevărat azi**: pe declarații și pe bilanț pleacă denumirea
  **fiscală**, iar caseta asta **nu o schimbă**.
- **F2.** Butonul *„Ia denumirea de la ANAF"* schimbă **doar eticheta din portofoliu**. Numele și
  descrierea butonului spun ce face în realitate. La fel pentru *„Păstrez denumirea mea"*.
- **F3.** Ambele intră sub regula **E1** — sunt exact cazul ei.
- **F4.** **Test care ține F1/F2**: dacă ramura `anaf` ajunge vreodată să scrie în `firma_profil`,
  textul devine fals **invers**, iar testul trebuie să **pice**. Ancorat pe **comportament**, nu pe
  șirul de text.
- **INTERDICȚIE EXPLICITĂ**: *nu schimba ce scrie ramura `anaf`* — aia e R81 și **nu e decisă**.

### BLOC G — trei lucruri rămase deschise din măsurătorile pe R79

- **G1.** Aserțiunea orfanilor din `core/test_tenant_stergere.py::test_niciun_orfan_NOU_dupa_ultima_stergere`
  e `n <= 69`, **într-o singură direcție**. O scădere nu e prinsă. *Un contor care poate doar să
  crească nu e contor.* **Fă-o bidirecțională, cu motivul scris**: o scădere neexplicată e la fel de
  suspectă ca o creștere.
- **G2.** `core/test_nume_anaf.py::test_o_citire_ANAF_mai_noua_REDESCHIDE_intrebarea` păzește o ramură
  **corectă și nedeclanșabilă** — nicio rută nu re-citește ANAF pentru o firmă existentă. Verde pe
  vecie fără să demonstreze nimic; aceeași familie cu semafoarele permanent verzi din E1.
  **Marcheaz-o ca gardă pe cale moartă, acolo unde se citește, cu condiția care ar învia-o. NU o
  șterge.**
- **G3.** `public.firme_scoase.schema_name` e **singura** coloană din `public` care referă un tenant
  prin nume de schemă, fără cheie străină, iar numele **se reciclează** (`tenant_019` pentru două
  firme; `tenant_018` acum la o firmă vie). Rândul rămâne dezambiguizat de `tenant_id`, deci urma nu
  e pierdută. **Scrie lângă coloană că nicio citire nu se cheiază pe ea**, și pune o **gardă care
  prinde o citire cheiată pe `schema_name`** dacă apare.

### BLOC H — populația nedeclarată

- **H1.** Rezolvă cel mai ieftin: **listă explicită de cabinete excluse, scrisă lângă clichet**, cu
  motivul și cu decizia din `DECIZII.md` (09.08) care creează cabinetul 4163. **Fără coloană nouă în
  `accounting_firms`.**
- **H2.** Recalculează `_DIVERGENTE_CUNOSCUTE` (`core/test_nume_firma_unic.py`) pe populația
  declarată. **Dacă iese 0, scrie 0** și spune că vechea valoare **4** era clichet pe fixturi.
- **H3.** Problema e mai largă decât R81: orice măsurătoare viitoare *„pe firme reale"* lovește
  aceeași lipsă. **Consemnează în `METODA_VERIFICARE.md`** că o cifră despre „firme reale" declară
  populația pe care s-a calculat, sau nu se scrie.

### REGISTRELE cerute odată cu ele

- `DESIGN_SYSTEM.md` + `verificator_conformitate.py`: **E1, E2**.
- `METODA_VERIFICARE.md`: **E3, H3**.
- `CONFORMITATE.md`: **R81** primește constatarea că divergența **nu se poate naște la creare** — se
  naște doar prin **redenumire ulterioară**, fiindcă `PUT` și ramura `anaf` scriu într-un **singur**
  loc din două. *Întrebarea lui R81 nu mai e „care denumire e adevărul", ci **„de ce redenumirea
  atinge unul singur"**.* **Titlul restanței se rescrie în forma asta.** **R82** primește F1–F4 ca
  instanță **cu efect fiscal**, nu de prag 1.
- `DECIZII.md`: **NIMIC.** R81 **nu e decisă**.

---

## A DOUA: O CONVENȚIE NOUĂ DESPRE CUM SE CITESC COMENZILE — se aplică de acum înainte

Dată de Costin în ultima comandă, după ce am ridicat o contradicție între un bloc cu literă și
secțiunea `REGISTRE` a aceleiași comenzi:

> **`REGISTRE` listează MINIMUL OBLIGATORIU.** O scriere **comandată explicit într-un bloc cu literă**
> e autorizată **prin faptul că e comandată**. Dacă o scriere dintr-un bloc **nu** e dorită,
> `REGISTRE` o interzice **pe nume**.

Și partea a doua, care e la fel de importantă: *„Ai ridicat-o corect — **continuă să ridici**, dar
cazul general e rezolvat."* Deci ridicarea contradicției rămâne obligatorie; ce se schimbă e
**rezoluția implicită**: blocul cu literă câștigă, nu `REGISTRE`.

**Nu e scrisă încă în `CLAUDE.md`** — și acolo îi e locul, fiindcă `CLAUDE.md` e canonic pentru
PROCES. **E o cerință deschisă către Costin**, nu ceva de scris tăcut.

---

## STAREA LA PREDARE

Poartă verde la `d5e0ad5`: **3395 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator
`TOTAL scanat 180 = ACCEPTAT 179 + GRI 0 + ROSU 0 + EXCLUS 1` → **TOTAL 0** · site **200** ·
four-way `HEAD = origin/main = origin/backup/lant-2026-08-27 = d5e0ad5`, commit la **21:35:50**,
proces pornit **21:47:55**. *(Se reverifică rulând poarta, nu se crede pe cuvânt.)*

**Zero modificări necomise.** Neurmărite: **234** de fișiere — cele șapte `LOT_*_VERIFICARI.md`,
`corectii_lot_1.md`, și artefacte vizuale în `frontend_test/` (capturi `.png`, `.csv` de probă).

**Cifrele nu se scriu aici** — `scripts/raport_b.py`. Fotografia de la `d5e0ad5`: locuri de
verificare **203 scrise / 0 goale (100%)**; restanțe deschise **49** (E1: **27**); interdicții din
76: MĂSURATE 21 · PARȚIAL 16 · NEMĂSURABILE 1 · NEÎNCEPUTE 38.

**Poarta durează ~12 minute** (3395 de teste). Comite prin `nohup … &` și așteaptă separat — o
sesiune `ssh` întreruptă la mijloc lasă fișierele *staged* și niciun commit.

---

## CE S-A ÎNTÂMPLAT ÎN ULTIMELE DOUĂ COMMITURI, ȘI DE CE CONTEAZĂ

Amândouă sunt **numai registre**. **Zero cod de aplicație atins. Zero schimbare pentru un contabil.**

### `555d606` — premisa lui R81 s-a desființat

Comanda cerea măsurătoare *înainte* de orice decizie, iar măsurătoarea a schimbat temeiul:

- **Cele 4 divergențe de denumire sunt TOATE pe cabinetul de test 4163.** Excluzând cabinetele de
  test: **0 divergențe din 14 firme reale.**
- **Divergența e artefact de fixtură, nu comportament de utilizator.** Firmele au fost adăugate
  manual prin ecran (deci `tenants.nume` = ce a tastat omul, fără formă juridică), iar profilul
  fiscal a fost scris de semănătorul din afara repo-ului, `~/date_test_cabinet/genereaza.py` l. 239,
  cu `"ALFA MICRO SRL"`. Semănătorul din repo (`transa2_coerenta_tva`) trece **același** șir prin
  amândouă locurile — de aceea cabinetul real are 0.
- **Clichetul pe date la 4 e clichet pe fixturi**, fiindcă instrumentul citește toate firmele fără
  filtru de cabinet. **De aici blocul H.**
- **PROBĂ, nu citire**: D100 T3/2026, D205 2026 și bilanț S1005 generate pe `tenant_013` în
  tranzacție întoarsă la savepoint → în toate trei pleacă **`den="ALFA MICRO SRL"`**, denumirea
  **fiscală**. Bara de sus a ferestrei ia cealaltă. **De aici blocul F.**
- **R79 REDESCHISĂ** (`stare: DESCHISĂ`, `reluări: 1`), la cererea lui Costin: fusese închisă pe un
  criteriu mai îngust decât eticheta ei.
- **R82 deschisă**: 4 din 6 acte de nivel firmă se termină fără confirmare vizibilă.

### `d5e0ad5` — două cifre de-ale mele, corectate la a doua citire

Amândouă scrise de mine cu câteva minute înainte, amândouă trecute prin poarta verde (sunt afirmații
despre cod, nu despre teste):

1. *„`GET /tenants` face o singură interogare pe `public`, deci o listă pe denumire fiscală ar cere o
   citire în fiecare schemă"* — **FALS**. `auth_api.tenantii_userului` face **deja** o citire per
   schemă, cu savepoint, pentru `tip_firma` (l. 385-395). **Corectura mută costul variantei (a) din
   „scump" în „nimic"** — adică exact argumentul care se va cântări.
2. *„patru locuri scriu în `public.tenants.nume`"* — erau **trei**. Al patrulea numărat scrie în
   `firma_profil`, nu în `tenants`, **și o spuneam chiar în propriul rând**.

---

## CE E ADEVĂRAT ACUM DESPRE CELE PATRU RESTANȚE DE DENUMIRE

| | |
|---|---|
| **R81** (DESCHISĂ, DECIZIE) | Divergența nu se naște la creare — `provision_tenant` scrie **același** șir în `tenants` **și** în `firma_profil` (l. 172 și l. 190). Se naște doar prin **redenumire ulterioară**, fiindcă `PUT` și ramura `anaf` ating **un singur** loc din două. **Decizia NU e luată. Nu construi nimic pe ea.** |
| **R82** (DESCHISĂ, INTERN) | 4 din 6 acte de nivel firmă din `firme.js` se termină în tăcere — alegerea de denumire (l. 312), scoaterea definitivă (l. 2465), cele două dezactivări (l. 2450, l. 2493). Confirmă doar crearea și reactivarea. **Pe calea de eroare, toate patru vorbesc.** |
| **R79** (REDESCHISĂ) | Ce s-a probat rămâne probat: rândul `1272066` are `tenant_id NULL`. Ce rămâne deschis e **G3**. Schema **chiar** se face `DROP SCHEMA … CASCADE`; `tenant_019` **nu mai există**. |
| **R77** (REZOLVATĂ pe scriere) | Trei lucruri pe care închiderea nu le acoperea sunt scrise lângă ea: apăsarea nu confirmă (→ R82), redeschiderea întrebării **n-are declanșator** (→ G2), alegerea e a **firmei**, nu a omului. |

---

## TREI SCHIMBĂRI PE MAȘINĂ ȘI ÎN DATE, ÎN AFARA REPO-ULUI — încă valabile

1. **O linie nouă în `crontab`**, la 15 minute: `core.sonda_web`. Pusă de **mine**, confirmată de
   Costin. Backup: `/home/costin/crontab_inainte_sonda.bak`. Rămâne scrisă ca fiind a mea.
2. **O alertă pe email trimisă din greșeală la 12:42**, subiect *„nu pot spune dacă a fost deploy"*.
   E de ignorat.
3. **Portofoliul s-a schimbat de trei ori azi, prin ecran, de către Costin.** `public.firme_scoase`
   are 3 rânduri (13:42:13, 13:44:40, 19:25:04). **Portofoliul are 18 firme**, dintre care **1** cu
   instantaneu ANAF (`Antibiotice Iasi`, 33394) și **1** cu alegere consemnată.

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează.*

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

---

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Nu s-a construit nimic din ultima comandă.** Blocurile E, F, G, H sunt **zero începute**. Dacă
  citești predarea asta și vrei să continui, **acolo începi**.
- **Verde nu înseamnă exercitat.** 3395 de teste trec, iar cele două cifre corectate în `d5e0ad5` au
  trecut poarta verde fără să clipească: erau afirmații despre cod, nu despre teste.
- **Un gard verde poate păzi o cale moartă.** `test_o_citire_ANAF_mai_noua_REDESCHIDE_intrebarea` e
  corect și **nedeclanșabil** — nicio rută nu re-citește ANAF pentru o firmă existentă. **G2.**
- **Un clichet pe date poate fi un clichet pe fixturi.** `_DIVERGENTE_CUNOSCUTE = 4` măsoară
  semănătorul, nu aplicația. **H1/H2.**
- **Un contor într-o singură direcție nu e contor.** Orfanii sunt `n <= 69`; o scădere n-ar fi
  prinsă. **G1.**
- **Un ecran spune azi ceva fals** despre ce pleacă pe declarație, și **nu e reparat**. **F1/F2.**
- **Sonda web prinde REPORNIREA, nu DURATA.** R75 rămâne deschisă tocmai de-aia.
- **Baseline-urile nu sunt curate.** Sunt fotografii. Gărzile spun că **nu cresc**, nu că listele
  sunt adevărate.
- **Butonul „Scoate" nu e gardat de nimic mecanic.** Proba Playwright e o **probă, nu o gardă**.
- **Cei 67 de orfani dinainte rămân.** Decizia lui Costin. **Cifra 69 nu e o măsură a sănătății, e o
  constantă istorică** — informația e **creșterea**, nu totalul. Și atenție: **67 și 69 sunt două
  mulțimi diferite**, iar 67 apare în **două** înțelesuri (orfanii de dinainte de azi *și* orfanii din
  `audit_log` de azi). Dezambiguizarea e scrisă în R79.
- **Mesajul commitului `110f346` e TRUNCHIAT la jumătate** (1090 din ~2200 de octeți), fiindcă un
  ghilimel a închis argumentul `ssh`. E împins; `--force` pe main e interzis: **rămâne așa.**
  *De atunci mesajul se trimite prin **fișier**, iar după fiecare commit se face `diff` caracter cu
  caracter între fișierul trimis și `git log -1 --format=%B`. Ambele commituri de azi: identice.*
- **Nu există gard pe trunchierea mesajului de commit.** Verificarea de mai sus e **o comandă rulată
  de mână**, nu o poartă. *(Forma gardului e de trei rânduri în `post-commit`; n-a fost construită.)*
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
  în tăcere și face fiecare diff viitor zgomotos. După orice patch: verifică `b.count(b"\r\n") == 0`.
- **Mesajul de commit se trimite prin FIȘIER**, niciodată prin heredoc în argumentul `ssh`: un `"` îl
  trunchiază tăcut. S-a întâmplat de două ori pe 27.08.
- **Sondele care „doar citesc" pot scrie.** Orice probă pe date reale se rulează în tranzacție
  întoarsă la `SAVEPOINT`, iar la final se verifică ce s-a schimbat.

---

## DACĂ CONTINUI DE AICI

1. **Blocurile E, F, G, H.** Sunt comandate, sunt scrise mai sus cu tot ce le trebuie, și **niciunul
   n-a fost început.** Textele regulilor sunt fixate — *„nu le rescrie"*.
2. **Nu porni nicio construcție fără măsurătoare.** Azi, de patru ori din patru, măsurătoarea a
   schimbat ce trebuia construit — ultima oară desființând premisa unei restanțe întregi.
3. **R81 NU e decisă.** Nu construi nimic pe ea, și nu schimba ce scrie ramura `anaf`.
4. **`scripts/raport_b.py` derivă secțiunea „Unde suntem".** Nu se scrie de mână.
5. **Raportul se scrie din `SABLON_RAPORT.md`**, nu din memorie. Ordinea: 0 CERINTE · 1 CE AM
   PRESUPUS · 2 ÎN PLUS/MAI PUȚIN · 3 CE AM ACTUALIZAT · 4 ÎNȚELEGEREA · 5 RĂSPUNS LA COMANDĂ ·
   6 UNDE SUNTEM · 7 POARTA.
6. **Convenția nouă despre `REGISTRE` vs blocurile cu literă** (mai sus) se aplică de acum — și
   așteaptă să intre în `CLAUDE.md`.
