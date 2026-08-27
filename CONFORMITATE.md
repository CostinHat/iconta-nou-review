# CONFORMITATE — confruntarea codului cu PLAN_ARHITECTURA.md

**Registrul măsurătorilor.** Planul spune cum trebuie să fie; aici scrie **cât de departe e**, cu
cifră, listă și calibrare. Cerut de Costin pe 22.08.2026, cu motivul: *„Cifrele confruntării nu au
voie să existe doar în raport. Raportul se citește o dată; registrul rămâne."*

**O secțiune per interdicție, toate 75.** Majoritatea sunt NEÎNCEPUTE — așa se vede de la început cât
e de făcut, în loc să se descopere pe parcurs.

**Câmpurile sunt obligatorii.** Un câmp gol nu e permis: dacă nu se poate măsura, se scrie
**NEMĂSURABILĂ** cu motivul. *„Investigată" nu e o stare.*

| stare | ce înseamnă |
|---|---|
| **MĂSURATĂ** | există cifră, listă și o calibrare care a găsit un caz cunoscut |
| **PARȚIAL** | măsurabilă doar pe o formă declarată; cifra e un plafon inferior |
| **NEMĂSURABILĂ** | nu se poate număra, cu motivul scris — nu din slăbiciunea instrumentului |
| **NEÎNCEPUTĂ** | nu s-a măsurat încă |

Gardat de `core/test_conformitate.py`: o interdicție din plan fără secțiune nu trece poarta, iar un
câmp obligatoriu gol o oprește la fel.

---

## ANTET DE ETAPĂ

Cerut de `PLAN_LUCRU.md` („Unde suntem"): un singur loc care spune unde suntem, ca un om care se uită să
poată răspunde fără să citească rapoarte vechi. Gardat de `core/test_conformitate.py` — **un antet cu
date vechi e mai rău decât niciunul**, deci data se verifică mecanic: contra ultimului commit care a
atins fișierul, iar o modificare încă necomisă a registrului cere data de azi.

**Ce are voie să stea aici, și de ce e plafonat.** `pasul curent` e limitat **mecanic la 300 de
caractere**. Motivul e măsurat, nu estetic: în două zile, antetul a rămas în urma corpului de **două
ori**, și de fiecare dată pe partea **numărabilă** — o coloană de cifre depășită, un transfer scris la
viitor după ce fusese făcut, un avertisment despre un contor care se schimbase. Regula, scrisă:
**dacă o propoziție se poate confrunta cu o cifră, nu e a antetului** — e a derivatorului
(`scripts/raport_b.py`), care o recalculează la fiecare raport. Aici rămâne doar ce nu se derivă din
nimic: **de ce pasul curent e pasul curent**. Plafonul nu citește proza și nu judecă ce scrie în ea;
face doar imposibilă acumularea unei narațiuni care să îmbătrânească. *(Decizia lui Costin, 23.08.2026,
după a doua oară: „e gardul care nu citește proză și totuși o disciplinează".)*

- **etapa**: E1 — SETUL COMPLET (faza 1 din `PLAN_INVESTIGATII.md`)
- **pasul curent**: **`TRASEE_VERIFICARI.md`** — ce trebuie să fie adevărat după fiecare pas. Le scrie Costin, în loturi de câte 30 (`scan_trasee.py --loturi N`). Până se scriu toate, inventarul de trasee e o hartă a codului, nu o listă de verificare. *(Cifrele se derivă.)*
- **criteriul de terminare**: există lista artefactelor cerute de lege — din lege, cu temei — pe **regimurile reale** (nu pe trei alese arbitrar), iar fiecare artefact e clasificat în una din cele cinci liste ale verdictului 1d. Aplicația e gata pe acest criteriu când listele 3, 4 și 5 sunt goale pe fiecare regim; lista 2 poate avea conținut, fiindcă măsoară ce n-a completat contabilul, nu ce n-a făcut aplicația.
- **ce lipsește**: faza 1 nu mai are pași, iar cele două restanțe care blocau punctul de decizie 1 (R17, R2) sunt închise. Rămân restanțele de mai jos — **numărul lor e derivat, nu scris aici**. Cele care blochează cel mai mult sunt acum **R5** și **R6** (încrederea în corpusul pe care stă tot 1a).
- **decizii care blochează**: **niciuna.** Toate cele patru cerute pe 26.08.2026 au primit răspuns și sunt aplicate: **R54** (contul se REFUZĂ, nu se semnalează), **poarta de coadă** (mutată la intrare), **baseline-urile** (nu se urmăresc în git), **R43** (verificată, rămâne prag 2 — blocată EXTERN pe chei de procesator). Deschise fără să blocheze: **R53** și **R58** *(numai partea amânată de Costin — echilibrul și orfanii ca posibile condiții de închidere)*. Cele trei restanțe de rol și de poartă decise ieri sunt marcate REZOLVATE; **starea lor se citește din registru, nu din antet** — antetul nu poartă stări care se pot confrunta cu un câmp. *(Text de dinainte, păstrat fiindcă e istoricul întrebării: „una — R54, DESCHISĂ**: contul contabil venit din corpul cererii e normalizat (nu mai poate fi alb), dar **nu e confruntat cu planul de conturi** — se refuză cererea, sau se semnalează și se scrie? Atinge cele **12 câmpuri de cont în text liber** din ecranul de operațiuni. **R33 nu mai blochează: DECISĂ și APLICATĂ 26.08.2026, varianta b′′** (`echilibru_perioada` se leagă lângă cea existentă, `BALANTA_INEGALA` iese fiindcă e tautologică, ambele se arată ca un singur „Echilibru”). Istoricul întrebării — schimbată de două ori, fiindcă premisa „logică paralelă” era falsă — rămâne în R33, fiindcă e chiar lecția.
- **avertisment la cifre**: **Transferul retrospectiv 3a e FĂCUT (23.08.2026)**, deci avertismentul de dinainte nu se mai aplică în bloc: din cele douăsprezece, nouă au trecut (una MĂSURATĂ, opt PARȚIAL). Rămân **trei** care scriu NEÎNCEPUTĂ deși §3a le dădea ca măsurate — **7, 8, 12** — și rămân **prin regulă, nu din uitare**: pentru ele nu există cifră pe domeniu, ci proză despre instanțe, iar *ce nu se reconstituie onest rămâne NEÎNCEPUTĂ*.
- **ultima actualizare**: 2026-08-27
- **cel mai vechi commit din registru**: `ffbcb74` (22.08.2026) — cifrele mai vechi de-atât descriu un cod care s-a mișcat de sub ele. Se compară cu HEAD la fiecare citire; garda verifică doar că e chiar cel mai vechi dintre `pe commit`-urile de mai jos.

---
## TRIAJ PE PRAGURI (22.08.2026)

Cele trei praguri sunt definite în `PLAN_LUCRU.md`, E5. Aplicate pe **ce e deja măsurat** — lista, nu
reparațiile. **Testul lor:** dacă știi ce se repară primul fără să te uiți în tabel, n-ai nevoie de tabel.

### PRAGUL 1 — imediat (efect greșit la un om ACUM) — **AMBELE REPARATE 22.08.2026**

**1.1 — REPARAT.** `core/nomenclator_status_factura.py`: stările unei facturi într-un singur loc, cu
decizia de interpretare scrisă (varianta aleasă: `de_preluat` = stare finală, declarabilă; varianta
respinsă: staging — **de confirmat de Costin**). `d300.py` (două locuri) și `d300_reconciliere.py`
citesc acum registrul, nu liste proprii. **Proba, pe aceleași ferestre, înainte → după:**
t003 0 → **889,00 lei TVA** · t005 0 → **2.100,00** · t013 315,00 → **378,00**. Total recuperat
**3.052,00 lei**, exact cifra măsurată înainte. Gardat de `core/test_status_factura_un_loc.py`
(7 teste, RED-proof 5/5).

**1.2 — REPARAT.** `core/coduri_cm_api.py` + ruta `/tenants/{id}/concedii/coduri`; `CM_CODURI` a
dispărut din `flux_concediu.js`. **Proba:** ecranul oferă acum **20 de coduri** (era 18) — `11`, `91`,
`92` au intrat — iar procentul urmează **data certificatului**: cod 01 = `55/65/75%` azi și `75%` pe o
dată dinainte de Legea 141/2025. Gardat de `core/test_coduri_cm_din_registru.py` (5 teste). Garda a
prins o a doua instanță, mai mică, a aceleiași clase: textul de ajutor scria „la 75%" — scos.


| # | ce e | efectul, azi |
|---|---|---|
| **1.1** | **`de_preluat` înseamnă două lucruri opuse, iar D300 omite tăcut facturi emise** — GĂSIT AZI, prin experimentul de la R12 | **cifră greșită într-o declarație generată** (pe date de test; pe instalare nu există firme reale, deci nicio depunere reală — vezi corecția din 1d). `core/d300.py:50-52` tratează `de_preluat` ca **staging** și îl exclude din decont; `core/export_winmentor.py:17` scrie explicit *„'de_preluat' e starea NORMALĂ a facturii emise, nu una de exclus"*; iar `core/facturi_api.py:311` **creează facturile noi exact cu `status="de_preluat"`**. Măsurat: **4 facturi emise, la 3 plătitori de TVA, cu TVA colectată de 3.052,00 lei, nu intră în D300** (t003: 2 facturi / 889,00 · t005: 1 / 2.100,00 · t013: 1 / 63,00). Pe t013 decontul **nu e gol, e incomplet** — iese cu 18 operațiuni și o omite pe a 19-a, ceea ce e mai greu de văzut decât un zero |
| **1.2** | **`flux_concediu.js` blochează introducerea unui cod legal** (secțiunea 28, `DECIZII` D3) | **blocaj**: codurile `11`, `91`, `92` există în nomenclator cu temei, aplicația le acceptă, ecranul nu le oferă. Consemnat, nereparat, de trei ture |

### PRAGUL 2 — la închiderea etapei (cauză unică dovedită, fără concurență)

| # | ce e | de ce prag 2 |
|---|---|---|
| **2.1** | **Interdicția 2** — 3 apeluri fără dată, **o cauză unică**: defaultul `la_data=None` din `common.cota` | cauza e o linie; scos defaultul, interdicția devine imposibilă prin construcție. Nu concurează cu nimic |
| **2.2** | **Registrul-inventar** (14-1-2) — nu există producător pentru partidă dublă | absență: n-are instanțe de ordonat |
| **2.3** | **Cartea mare** (14-1-3) — motorul există (`core/motor.py:32`), zero consumatori | absență, cu motorul deja scris |
| **2.4** | **Registrul de evidență fiscală** (CF art. 19 / 68) — nu există | absență |
| **2.5** | **Evidența TVA ca artefact** (jurnale de vânzări/cumpărări, CF art. 321) | absență **simplă** — vezi Q2: datele există la nivelul cerut de articol, lipsește doar documentul |
| **2.6** | **Jurnalul regim marjă** — producător DA, ecran NU | absență de randare, cu producătorul scris; vezi Q1 pentru de ce nu e o absență *declarată* |

### PRAGUL 3 — după tabelul final

| # | ce e | de ce prag 3 |
|---|---|---|
| **3.1** | **Interdicția 1** — ~100 valori fiscale în afara registrului, în 16 fișiere | multe instanțe, ordinea contează, concurează între ele |
| **3.2** | **Interdicția 16** — 39 nomenclatoare ancorate pe sursă secundară, din 93 | idem |
| **3.3** | **Interdicția 17a** — 42 valori re-declarate | idem |
| **3.4** | **Interdicția 32** — 19 note din 33 fără legătură la document (P14) | clasă mare, cere decizie de model de date |
| **3.5** | **Registrul-jurnal**, ca artefact conform pct. 45 | depinde de 3.4: nu se poate randa ce nu e în date |

**Ce NU intră în praguri, și de ce:** restanțele deschise (R1–R12) nu sunt defecte, sunt **muncă de
măsurare sau de decizie**; pragurile ordonează reparațiile, nu investigația.

---

## AUDITUL CONSEMNĂRII (22.08.2026)

**De ce.** Un defect găsit și nereparat nu avea întotdeauna unde să fie consemnat: instanțele
interdicțiilor merg în secțiuni, restanțele blocate în secțiunea lor — dar ce nu e nici una, nici alta
rămânea doar în raport, adică se pierdea. Auditul inventariază **ce s-a găsit și unde stă**, **din ce
există pe disc**.

**Cum s-a căutat, ca să se poată discuta ce nu prinde:** sweep mecanic pe `PREDARE_LANT.md`,
`GARZI.md`, `DECIZII.md`, `CONFORMITATE.md`, `TESTE.md`, `ISTORIC.md`, `ISTORIC_TENANTI.md`, pe zece
tipare declarate („NU se repară acum", „NEREPARAT", „RĂMÂNE DESCHIS", „merită a doua privire",
„de privit", „defect LATENT", „divergență", „contrazice", „STOP", „neatins") — **154 de potriviri pe
tot corpusul de registre**, dintre care **88 în liniile ADĂUGATE de commiturile din 20–22.08**.
Zgomotul s-a numărat: „neatins" prinde masiv „datele firmei X neatinse" (deliberat), iar
„contrazicere"/„divergență" prind definițiile din planuri, nu constatări. Plus: **grep pe cod după
`TODO|FIXME|HACK|XXX` → zero**; cele trei „rămâne" din `d300.py`/`d301.py` sunt limite declarate, nu
defecte.

### Inventarul

| # | ce e | unde | ce efect are | reparat? | unde era consemnat | unde e ACUM |
|---|---|---|---|---|---|---|
| 1 | **70 de linii scrise de Costin în `PLAN_LUCRU.md`, intrate în commitul meu `45f15ab`** printr-un `git add` fără citirea diff-ului | `PLAN_LUCRU.md:111–170` | patru cerințe au stat **opt commituri** neimplementate; între timp am derivat în paralel o a doua taxonomie pentru același obiect | **azi, parțial** — taxonomiile împăcate, două gărzi construite | **nicăieri** — nici măcar ca observație | `PLAN_LUCRU` („De unde vin cele două") + **R10** pentru gărzile rămase |
| 2 | **Cele trei egalități stricte**: `d223.py:159`, `d406.py:1338`, `:1367` — verificate azi, toate există | cod | dacă vreuna e interpretare, nu lege, e interdicția 21; cifra „2 reale" rămâne plafon inferior | NU | proză în patru locuri, fără stare | **R8** (ORDINE) |
| 3 | **Ecranul statului de plată — STOP nemișcat** | — | semnalul de contradicție și butoanele emite/corectează nu sunt în interfață | NU | `PREDARE_LANT.md`, care **se rescrie la fiecare predare** | **R9** (ORDINE) |
| 4 | **preview↔salvare, trei instanțe** (checksum VIES D301 · indicatorul patru-ochi · front↔back) | `GARZI`/`ISTORIC`/`ISTORIC_TENANTI` | reguli diferite la previzualizare față de salvare | **DA, toate trei** | proză — iar **secțiunea 15 spunea „NEÎNCEPUTĂ, niciun caz"** | **secțiunea 15**, acum PARȚIAL cu 3 instanțe |
| 5 | **D300 valid cu 0 operațiuni vs D100 care refuză**, pe t003 | `CONFORMITATE` 1b | același fapt, două motoare, două comportamente | NU | consemnat azi, în narațiunea lui 1b | rămâne la 1b — e obiect de măsurat, nu restanță |
| 6 | **Factură cu `categorie_331` și `taxare_inversa = false`**, pe t013 | `CONFORMITATE` E1 | de lămurit la 1b | NU | consemnat azi, în narațiune | rămâne la 1b |
| 7 | **`CM_CODURI` din `flux_concediu.js`** | cod | **blochează un contabil să introducă un cod legal** | NU (decis CUM) | secțiunea 28 + `DECIZII` D3 | **avea deja loc** |
| 8 | **Nouă poziții vechi în `GARZI.md`** („defect LATENT", „NU se repară acum" ×2, „RĂMÂNE DESCHIS", D_8, GL neechilibrat, C3, „NEREPARAT", D300 furnizor taxare inversă, xfail deschis) | `GARZI.md`, în afara ferestrei de două zile | diverse | NU | proză, fără stare | **R11** (ORDINE), numărate — nu transcrise |
| — | `d300_reconciliere` | — | — | — | **`DECIZII.md:10649`, 21.08: fals pozitiv corectat.** Raportasem duplicarea ca datorie; duplicarea e **deliberată** și e apărată de `test_non_tautologie` | **nu e defect**; rămâne unde e |

### Cifrele

| | |
|---|---|
| defecte găsite, în inventarul reconstituibil de pe disc | **8** |
| dintre ele, **reparate** | **4** (trei preview↔salvare, înainte de azi; al patrulea — coliziunea de taxonomii — azi, parțial) |
| **consemnate azi pentru prima dată** într-un loc cu stare | **5** (#1 → R10 + plan, #2 → R8, #3 → R9, #4 → secțiunea 15, #8 → R11) |
| aveau deja loc | **1** (#7) |
| rămân în narațiune, deliberat, ca obiecte de măsurat la 1b | **2** (#5, #6) |
| **fals pozitive corectate** | **1** (`d300_reconciliere`) |
| **pierdute definitiv** | **nenumărabile din disc** — vezi mai jos |

**„Pierdute definitiv" nu e zero, și nu e o cifră.** Rapoartele au trăit în conversație, nu pe disc.
Ce n-a fost scris niciodată într-un fișier **nu se poate reconstitui de aici**, iar din memorie nu se
reconstruiește — ar fi exact greșeala pe care regula 1 a raportului o interzice. Singurul lucru care se
poate spune cu probă: **din cele opt găsite pe disc, cinci n-aveau niciun loc cu stare**, deci rata de
pierdere a fost mare, nu marginală.

**Ce nu vede auditul:** un defect descris fără niciunul dintre cele zece tipare · unul consemnat într-un
fișier din afara listei · unul care trăiește doar într-o captură sau într-un nume de test. Și nu spune
nimic despre defectele **necunoscute** — inventariază ce s-a găsit, nu ce există.

---

### TRIAJ — ce s-a măsurat pe 23.08.2026, așezat pe praguri

**PORNIT prin decizia lui Costin, 23.08.2026.** Era *PREGĂTIT, NU DECIS*; de acum e ordinea de lucru.
Pragurile s-au atribuit după regulile deja luate: **pragul 1 se citește ca ATINGIBILITATE**
(lămurirea din `PLAN_LUCRU.md`), iar în pragul 3 **lista 5 intră înaintea listei 3**, cu excepția
artefactelor obligatorii prin lege. Cele trei poziții care nu sunt acoperite de o regulă deja luată
rămân marcate **cere decizie** și **nu blochează restul** — se lucrează în jurul lor.

**Tabelul se recitește la fiecare tură.** La prima citire de după scriere, patru rânduri din cinci ale
pragului 2 și două din pragul 3 erau deja **stătute** — se închiseseră în ziua în care fuseseră scrise.
Un tabel de triaj care nu se recitește ordonează muncă făcută.

#### PRAGUL 1 — imediat

**O singură instanță nouă, și e REPARATĂ în aceeași tură.** Eticheta **„Deducere personala"** de pe
fluturaș tipărea `deducere['total']`, care include și deducerile suplimentare: pe un tânăr la salariul
minim, eticheta spunea *Deducere personala* peste cifra **1.513,75**, când deducerea personală e
**865,00**. **3 din 5** cazuri obișnuite, **2 din 24** de salariați existenți. Reparat cu rânduri
numite, gardat cu 13 teste, RED-proof de două ori. *(A treia instanță de prag 1 din campanie.)*

**A DOUA INTRARE DE PRAG 1 (23.08.2026): `JournalID` = `GENERAL` în D406.** Reclasificată de Costin
din restanță în prag 1, cu motivul: *un element care pleacă la ANAF purtând o valoare inventată nu e o
absență, e o afirmație falsă — iar destinatarul e autoritatea, treapta de deasupra unui om.* Măsurat,
reparat, probat la validatorul oficial și gardat în aceeași tură — vezi **R22**. *(A patra instanță de
prag 1 din campanie.)*

**Nimic altceva măsurat azi nu atinge pragul 1** — și o spun explicit, fiindcă s-au măsurat multe:
niciuna dintre cele opt interdicții din faza 2, niciuna din faza 4, și niciuna dintre restanțele noi
nu produce o cifră greșită, un blocaj sau o afirmație falsă la un contabil care ar folosi aplicația azi.

#### PRAGUL 2 — la închiderea etapei (cauză unică dovedită, fără concurență)

| ce | cauza unică | stare |
|---|---|---|
| **R17** — graful cheiat pe nume simplu | dicționar plat, cheie prea scurtă | **REZOLVAT** 23.08 (`c7bcddb`) |
| **R2** — vigoarea pe punct | instrumentul lipsea | **REZOLVAT** 23.08 (`c7bcddb`) |
| **datoria 31.07 — `verificator_conformitate` fără nicio gardă** | analizorul lui nu e testat pe fixturi known-good / known-bad | **REZOLVAT** 23.08 (`139bca5`), după **23 de zile** |
| **R20** — opt artefacte de un octet în corpus | o derivare care a produs gol și n-a spus-o | **REZOLVAT** 23.08 (`9510c94`), prin decizie: șterse |
| **R19** — `graf_clustere` tratează utilitarele partajate ca proprietate | filtrul exclude partajarea **cu sine**, nu **între alții** | **REZOLVAT** 23.08 — mecanic, nu prin decizie |
| **`scan_constante` — gardă fără calibrare NEGATIVĂ** | *(rândul spunea «ZERO calibrare pozitivă, 2 teste» — **stătut cu trei zile**: avea 14 teste și patru calibrări pozitive)* | **REZOLVAT** 23.08 — două găuri tăcute, măsurate și închise |

**Pragul 2 s-a golit pe trei sferturi într-o zi**, iar la reluarea triajului a mai căzut una: R19,
**mecanic** — o funcție partajată nu primește alt proprietar, ci niciunul. Apoi a căzut și
`scan_constante`, ultima. **PRAGUL 2 E GOL.**

**Ce a scos calibrarea lui `scan_constante`, și de ce contează mai mult decât închiderea lui.** Rândul
din tabel îl descria cu *„ZERO calibrare pozitivă, 2 teste"* — **stătut cu trei zile și patru
commituri**: gardul avea deja **14 teste** și **patru calibrări pozitive**, adăugate pe 20–21.08. E a
**patra** poziție de triaj descrisă fără să fie deschis modulul. Dar cererea lui Costin — *„calibrează
în ambele direcții, dar mai ales negativ: dacă instrumentul vede mai puțin decât crede, clichetul
păzește un prag fals, iar direcția aia e tăcută"* — a nimerit exact ce lipsea: **toate cele patru
calibrări erau pozitive sau contra-direcții ale clasei E. Niciuna nu întreba ce rămâne AFARĂ.**

**Două găuri tăcute, amândouă numite chiar de docstringul scanului, niciuna testată până azi:**

| gaura | măsurat | ce s-a făcut |
|---|---|---|
| **DOMENIUL** — `FIS` e o listă de NUME | **79 din 289** de module `core/` erau în domeniu; **50** dintre cele rămase aveau semnal fiscal, iar **4 construiesc `Temei`** — adică sunt fiscale prin propria mărturisire | domeniul e acum `FIS` **SAU** *modulul construiește un `Temei`* — criteriu **mecanic**, care se întreține singur: un modul intră în ziua în care citează legea |
| **BOTEZUL** — un nume care se potrivește cu `NOM` trimite valoarea în B, tăcut | probat sintetic: `TIP_COTA = 21` → **B**; `COD_COTA = 21` → **B**; `CATEG_PLAFON = 300000` → **B**. Pe date reale: **15 coliziuni, 7 nume, toate coduri de categorie** — gaura e reală, dar **azi goală** | **nu s-a schimbat regula** (NF peste NOM ar fi mutat exact acele 15 clasificări corecte în C, umflând clichetul cu false pozitive). S-a făcut **vizibilă**: `BOTEZ_BASELINE`, cu fiecare coliziune numită; a opta pică |

**CIFRA S-A MIȘCAT: clasa C urcă de la 93 la 104** — nu fiindcă datoria a crescut, ci fiindcă a
devenit vizibilă. Cele 11 sunt în `contracte_speciale.py` (5) · `sponsorizari.py` (3) · `motor.py` (2)
· `deconturi.py` (1). **Clichetul a fost lărgit cu ele, nu ridicat**: fiecare modul nou intră cu
datoria lui măsurată și nu mai poate crește. Consecința pe care Costin a anticipat-o: **se mișcă și
interdicția 1**, unde 93 era unul dintre termenii confruntării.

**Gardă**: `core/test_constante_nesursate.py`, **14 → 19 teste**. RED-probat: domeniul readus la lista
de nume → **2 teste roșii**, dintre care `test_baseline_nu_e_stat`, adică chiar clichetul.
`scan_constante` e cel mai expus dintre cele două: ține clichetul de 93 de constante nesursate în
producție, deci o gaură în el ar coborî o cifră fără ca nimic să se schimbe.

#### PRAGUL 3 — după tabelul final

**Ordinea în interiorul lui e decisă**: L5 înaintea L3, cu excepția celor obligatorii prin lege.

| ordine | ce | cifra | fel de muncă |
|---|---|---|---|
| **1** | **L3 obligatorii prin lege** — Cartea mare, Registrul-inventar, registrul de evidență fiscală | **nu 3 la fel**: unul lipsește complet (evidența fiscală), unul e de construit (Cartea mare), unul **are producător și ecran** (Registrul-inventar) — *corectat 23.08, vezi mai jos* | construcție pentru două; **îngustare** pentru al treilea |
| **2** | **L5 — predare** (temeiul pe ecran, balanța pe ecran, componentele fluturașului, desfacerea unei poziții) | **verificat 23.08: 2 din 4 intrări nu sunt predare** | **ore** pentru balanță și fluturaș · **zile** pentru temeiul pe ecran și desfacere |
| **3** | **L5 — interdicția 65** (explicația diferenței față de luna anterioară) | 0 mecanisme în Python, 0 în JS | **zile, nu ore** — nu e nepredat, e nescris |
| **4** | **restul L3** — bilanț/CPP fără rute, note explicative, registrul-jurnal, evidența TVA, jurnalul de marjă, categoria de mărime | 6 artefacte, din care **două au deja producător și rută** (`jurnal-marja`, `jurnal`) — *corectat 23.08* | construcție pentru patru; **predare** pentru jurnalul de marjă |
| **5** | **60 — legătura normă↔implementare** | **374 din 470** de elemente nu poartă nimic; structurile de declarație, termenele și validările au **zero** legături structurate | mare, dar se poate tăia pe categorii |
| **6** | **55 — categoria de reverificare** | câmpul nu există; un prag global unic pentru toate | **axa DECISĂ 23.08**; categoriile **propuse**, așteaptă confirmarea |
| **7** | **61 — lista dependenților** | 16 din 17, dar domeniul e registrul de cote, nu corpusul | îngustare, la prima folosire reală |

**Ieșite din tabel, fiindcă s-au închis:** **52** (era *„162 din 339 de acte fără amprentă, volum
mecanic"*) — închisă pe `7663e87`, și nu prin volum: cifra 162 era ea însăși greșită, iar amprentarea
mecanică ar fi umflat acoperirea fără s-o crească · **50** (era *„8 acte din 9 neverificate"*) —
închisă pe `d115f28`, 16 din 16, zero instanțe.

#### CORECTARE 23.08 — pozițiile s-au atribuit după NUME, nu după ce produce modulul

Poziția 1 spunea *„motorul Cărții mari există: `core/motor.py:32`, zero consumatori"*. **Fals.**
`carte_mare` e un înveliș de o linie peste `agrega_conturi`, care întoarce `{cont: {debit, credit,
sold}}` — **rulaje totale**. Norma (OMFP 2634/2015, cod 14-1-3) cere *„defalcarea rulajului debitor
pe conturi corespondente"*, iar perechea debit↔credit se pierde chiar la însumare. **Ce există e
balanța de rulaje, nu Cartea mare** — deci poziția e **construcție, nu predare**.

**Întrebarea care urmează n-a fost pusă de instrument, ci de Costin: câte alte poziții au fost
clasificate pe existența unui nume?** Verificat, cele 7 poziții ale pragului 3:

| poziția | pe ce stă clasificarea | verdict 23.08 |
|---|---|---|
| **1** — L3 obligatorii | prezența unui nume de funcție | **greșită de două ori, în direcții opuse** |
| **2** — L5 predare (*«totul e calculat»*) | afirmație de prezență, sprijinită pe o numărătoare de nume | **VERIFICATĂ 23.08 — greșită pe 2 din 4** |
| **3** — interdicția 65 | absență măsurată (0 în Python, 0 în JS) | ține |
| **4** — restul L3 | inventar de rute | **greșită pe două din șase** |
| **5** — 60 | numărătoare (374 din 470) | ține |
| **6** — 55 | absența unui câmp | ține |
| **7** — 61 | numărătoare (16 din 17) | ține |

**Cele patru erori, toate din același gest — poziția s-a scris fără să se deschidă modulul:**

- **Cartea mare** — creditată cu un motor pe care nu-l are (mai sus).
- **Registrul-inventar** — declarat *fără producător*, deși `registru_inventar(conn, schema, an)`
  există în `core/rip_api.py:169`, are rută (`main.py:6259`) și ecran
  (`static/js/ecrane/rip_ecran.js:52,133`). **Limita reală e alta, și e de scris**: acoperă doar
  mijloacele fixe la valoare rămasă plus disponibilitățile din RIP — deci **regimul de partidă
  simplă (14-1-2/b)**, nu inventarul complet de activ **și datorii**. Nu e absență; e îngustare.
- **Jurnalul de marjă** — trecut la *construcție*, deși `GET /tenants/{id}/jurnal-marja`
  (`main.py:7086`) produce per notă cost / marjă netă / TVA plus totalurile perioadei, cu un
  comentariu care spune singur *„fără UI încă, păstrat deliberat"*. Asta e **exact predare**.
- **Registrul-jurnal** — trecut la *construcție*, deși `GET /tenants/{id}/jurnal`
  (`main.py:3799`) întoarce înregistrările lunii cu dată, număr, descriere, cont debitor, cont
  creditor și sumă. De confruntat cu 14-1-1 înainte de a fi tratat ca absent.

  > **CONFRUNTAT 24.08.2026 (pragul 3, poziția 1), pe commit `56768af`.** Norma: OMFP 2634/2015,
  > anexa 2, cod 14-1-1 — opt coloane, enumerate în text. Măsurat pe **34 de note reale**, pe toate
  > cele 17 scheme.
  >
  > | col. | ce cere norma | ce produce ruta | verdict |
  > |---|---|---|---|
  > | **1** | numărul curent al operațiunilor, **de la 1 ianuarie** până la sfârșitul exercițiului | `numar` populat **1 din 34 (3%)**; `id` e cheie de bază de date, nu număr curent — iar ruta e **lunară**, deci nu poate produce o secvență cumulativă pe an | **ABSENT** |
  > | 2 | data (an, lună, zi) a înregistrării | `data` | prezent |
  > | **3** | **felul, numărul și data documentului justificativ** (factura, chitanța…) sau ale jurnalului auxiliar | `factura_id` la **15 din 34 (44%)**; coloana **`document_ref` EXISTĂ în schemă** și e populată **0 din 34 (0%)** | **ABSENT** |
  > | 4 | explicațiile | `descriere` | prezent |
  > | 5, 6 | simbolul conturilor debitoare / creditoare | `cont_debit`, `cont_credit` | prezent |
  > | 7, 8 | sumele totale, debitoare și creditoare, **din documentul justificativ** | `suma`, o singură coloană pe linie | parțial |
  > | — | *„sumele debitoare și creditoare se **totalizează lunar**"* | ruta întoarce `{"note": [...]}`, **fără niciun total** | **ABSENT** |
  >
  > **Verdictul se schimbă: Registrul-jurnal NU e un artefact absent.** Are producător, iar 4 din 8
  > coloane ies corect. Ce lipsește e precis: **coloana 1** (numerotare cronologică anuală),
  > **coloana 3** (identificarea documentului justificativ) și **totalizarea lunară**. Deci trece din
  > lista 3 a verdictului 1d (*„nu iese"*) în **lista 4** (*„iese, dar nu se validează"*) — altă
  > clasă, alt cost, altă reparație.
  >
  > **Și coloana 3 e chiar interdicția 32**, pe artefactul ei: `document_ref` nu e un câmp care
  > lipsește din model, e un câmp **care există și nu se scrie niciodată**. Reparația registrului
  > trece prin popularea lui, nu prin construirea unui artefact nou — ceea ce e mult mai ieftin decât
  > spunea încadrarea de dinainte.
  >
  > *Regula pe care o aplică asta e chiar cea din tabelul de triaj: o poziție se atribuie după CE
  > PRODUCE modulul, confruntat cu norma — nu după numele funcției și nu după existența rutei.*
  >
  > **REPARAT 24.08.2026, în aceeași tură.** Cele trei lipsuri se acoperă **prin derivare la citire**,
  > deci **nicio cale de scriere nu se atinge** — reparația nu depinde de **R36**:
  > **col. 1** — `nr_curent` calculat cu `ROW_NUMBER()` pe fereastră de **AN** (nu de lună: altfel
  > numerotarea ar reîncepe lunar, contra normei); **col. 3** — `document_justificativ()` în
  > `core/jurnal_api.py`, care compune *„Factură <serie><număr> din <dată>"* din factura legată, ia
  > `document_ref` ca atare când e scris, și **întoarce `None` când n-are din ce deriva**;
  > **totalizarea** — `total_debit` / `total_credit` pe lună, egale prin construcție în partidă dublă.
  >
  > **Ce NU s-a fabricat, și e partea care contează:** o notă fără factură și fără `document_ref`
  > primește coloana 3 **goală**, iar răspunsul poartă `note_fara_document` — absența se **numără**,
  > nu se ascunde. Un registru care ar completa un document inexistent ar face exact ce s-a scos din
  > ecranul de NIR prin R29: ar răspunde în locul omului.
  >
  > **Probat pe date reale** (`tenant_013`, 2026-08): 18 note, total D=C **28.055,00**, coloana 3
  > ieșită pe **8**, lipsă pe 10 — de la **0 din 34** înainte. Gardat de
  > `core/test_registru_jurnal_14_1_1.py`, RED-probat pe **6 mutații**, între care regresia tăcută a
  > ferestrei de numerotare de la an la lună.
  >
  > **Rămâne**: forma e conformă pe 7 din 8 coloane; **conținutul** coloanei 3 e incomplet fiindcă
  > `document_ref` nu se scrie niciodată — aia e **interdicția 32**, și ea atârnă de R36.

**Ce a rezistat verificării, și se spune la fel de explicit:** **registrul de evidență fiscală** are
într-adevăr **zero** potriviri în `.py`, `.js`, `.html` — apare doar în corpusul de acte. Și
**evidența TVA** n-are producător sub niciun nume de jurnal: `calcul_d300` agregă direct din
`facturi`, deci **datele există, artefactul nu**. Amândouă rămân unde erau.

**REGULA, scrisă în tabel:** *o poziție de triaj se atribuie după *ce produce* modulul, confruntat cu
norma — nu după numele funcției și nu după existența rutei.*

**A DOUA REGULĂ, adăugată 23.08 fiindcă prima nu era de ajuns: *o poziție se RECITEȘTE LA SURSĂ înainte
de a fi lucrată, indiferent cât de recentă pare.*** Motivul e o **rată, nu o observație**: din **patru**
poziții deschise și verificate, **patru** s-au dovedit descrise fără să fi fost deschis modulul —
poziția 1 (Cartea mare, Registrul-inventar), poziția 2 (*„totul e calculat"*), poziția 4 (jurnalul de
marjă, registrul-jurnal) și rândul lui `scan_constante` din pragul 2 (*„ZERO calibrare pozitivă, 2
teste"*, când avea 14 teste și patru calibrări). **4 din 4 nu mai e un accident, e o proprietate a
tabelului**: el a fost scris într-o singură trecere, iar o trecere unică peste 76 de poziții nu poate
deschide 76 de module. Recitirea nu e neîncredere în cine a scris tabelul — e recunoașterea că tabelul
a fost scris exact așa cum spune că a fost scris: *o trecere superficială* (`PLAN_INVESTIGATII.md`, 3b). Greșeala merge în **ambele** direcții:
un nume potrivit a creditat un motor inexistent, iar lipsa unui nume căutat a ascuns două artefacte
care există. Costul de a nu o respecta nu e simetric: prima direcție amână o construcție necesară, a
doua o pornește degeaba.

#### CORECTARE 23.08 (a doua) — poziția 2 verificată: «totul e calculat» e adevărat pe jumătate

Întrebarea lui Costin: *„Cele 11 artefacte din L5 au fost clasificate pe același criteriu care a greșit
de patru ori? Dacă da, «L5 costă ore» — argumentul pe care am ordonat L5 înaintea lui L3 — s-ar putea
să nu țină."* **Da, și pe una dintre cele patru intrări e chiar aceeași numărătoare de nume.**

| intrarea din L5 | ce spunea justificarea | măsurat 23.08 | verdict |
|---|---|---|---|
| **temeiul pe ecran** (9 declarații) | *«valorile există: 57 de obiecte `Temei`»* | **57 confirmat prin AST** (`common.py` 34 · `salarizare.py` 10 · alte opt module 13); în **cele nouă module de declarație sunt 2**, amândouă în `d101`, amândouă pe **termenul de depunere**, niciuna pe o casetă *(cifră corectată — vezi mai jos)* | **construcție** |
| **desfacerea unei poziții** | *(se subînțelegea din aceeași frază)* | **niciun producător**: nicio funcție care, dată o casetă, să întoarcă operațiunile care au compus-o; `valideaza` întoarce `stare` și **numărul** de operațiuni | **construcție** |
| **balanța pe ecran** | *«balanța se produce»* | adevărat: se produce și se descarcă PDF (`firme.js:2652`); lipsește doar drumul de la cifră la notele din spate | **predare** — ține |
| **componentele fluturașului** | *«`deducere`/`facilitate` sunt în răspunsul API»* | adevărat, verificat pe cod: `core/stat_plata_api.py:109–114` întoarce deja `deducere`, `deducere_baza`, `deducere_tineri`, `deducere_copii` | **predare** — ține |

**Numărătoarea de 57 măsura alt domeniu decât cel despre care afirma** — exact defectul de la poziția 1,
în aceeași formă: o cifră adevărată despre motor și salarizare, folosită ca dovadă despre declarații.

**CORECTAREA CORECTĂRII (23.08, aceeași zi) — și e a mea, nu a triajului.** Am scris *„cele nouă module
au ZERO"*. **Fals: sunt 2**, amândouă în `d101:211–212`, construite prin **aliasul `_Tm(`** — iar eu
măsurasem cu `grep 'Temei('`, care nu vede aliasul. Deci corectarea unei clasificări făcute pe nume a
fost ea însăși măsurată **pe nume**. Re-măsurat cu AST, rezolvând aliasurile de import: **57 în `core/`
fără teste** (cifra veche se confirmă), din care **2 în cele nouă module de declarație**. Ambele sunt
pe `_scadenta` (termenul de depunere, variante datate, `35b4732`), **niciuna pe o casetă**.

**Concluzia nu se schimbă, se întărește:** 2 obiecte din 57, într-un modul din nouă, niciunul legat de
o casetă — deci *temeiul pe ecran* rămâne **construcție**. Ce se schimbă e încrederea în instrument:
un `grep` pe numele clasei nu măsoară construcția obiectelor.
Iar registrul avea deja contra-măsurătoarea, la **60**: **374 din 470** de elemente nu poartă nicio
legătură normă↔implementare, și *structurile de declarație au **zero** legături structurate*. Cele două
propoziții — *«valorile există»* și *«zero legături»* — stăteau la 900 de rânduri una de alta.

**Ce se schimbă în ordine, și ce nu.** Decizia *L5 înaintea lui L3* **nu cade**, dar temeiul ei se
îngustează: argumentul de cost ține pentru **balanță și fluturaș**, unde valoarea chiar există și se
oprește înainte de ecran. Pentru **temeiul pe ecran** și **desfacerea unei poziții** nu e predare — nu
există ce preda — deci nu sunt «ore», și nu mai pot intra înaintea lui L3 pe argumentul de cost. **L5
intră primul cu cele două intrări care sunt cu adevărat predare**, nu ca bloc.

**Rata, fiindcă a devenit o rată și nu mai e o observație:** **6 artefacte greșit clasificate din 16
atinse** — 4 din 12 la pragul 3, plus 2 din 4 aici. Toate din același gest: poziția scrisă fără să se
deschidă modulul. De asta regula urcă în `METODA_VERIFICARE.md`.

#### CORECTARE 23.08 (a patra) — un NUME din normă poate acoperi DOUĂ obligații, pe regimuri diferite

Al treilea criteriu de recitire, **distinct** de *„ce produce, nu cum se numește"*: un nume luat din
normă poate ascunde **două artefacte**, cu **coduri de formular și regimuri diferite**. Verificat pe
toate numele din pozițiile 1 și 4, contra Anexei 1 pct. 44 și **pct. 48** (verbatim: *„Persoanele fizice
[…] care conduc evidența contabilă pe baza regulilor contabilității în partidă simplă întocmesc
Registrul-jurnal de încasări și plăți (**cod 14-1-1/b**) și Registrul-inventar (**cod 14-1-2/b**)"*):

| numele din triaj | partidă dublă | partidă simplă | verdict |
|---|---|---|---|
| **Registrul-inventar** | cod **14-1-2** | cod **14-1-2/b** | **DOUĂ** — iar cel simplu **există deja** (`rip_api.registru_inventar`) |
| **Registrul-jurnal** | cod **14-1-1** | cod **14-1-1/b** (*de încasări și plăți*) | **DOUĂ** — iar cel simplu **există deja** (`rip_api`, modulul e chiar el) |
| **registrul de evidență fiscală** | CF art. 19 alin. (7) | CF art. 68 alin. (8) | **DOUĂ** — verdicte opuse, vezi mai jos |
| **Cartea mare** | 14-1-3 / 14-1-3/a | *(nu se aplică)* | **UNU**, în două forme, ambele înlocuibile cu Fișa de cont |

**Deci trei din patru nume acopereau două obligații**, iar în două cazuri **artefactul de partidă simplă
era deja construit** și trecea drept absent. Asta explică de ce poziția 1 s-a corectat de trei ori:
criteriul *„ce produce"* prinde modulul greșit numit, dar nu prinde **obligația numărată o dată când
sunt două**.

#### CORECTARE 23.08 (a treia) — registrul de evidență fiscală: nu e un artefact, sunt DOUĂ

Cerută de Costin, cu criteriul de azi: *„Registrul de evidență fiscală e o listă de ajustări între
rezultatul contabil și cel fiscal. Aplicația calculează D101, deci undeva face diferențele. Întrebarea
nu e dacă există modulul, ci dacă există **calculul**."* Îl declarasem *rezistă la verificare* pe baza
lui *„zero potriviri în `.py`, `.js`, `.html`"* — adică **pe nume**. **A cincea instanță a aceleiași
greșeli, și e chiar singurul artefact pe care îl dădusem drept verificat.**

**Norma, citită verbatim: sunt două registre, pe două regimuri, cu temeiuri diferite.**

| regim | temei | ce cere să conțină |
|---|---|---|
| **impozit pe profit** | **CF art. 19 alin. (7)** | *„contribuabilii sunt obligați să evidențieze în registrul de evidență fiscală **veniturile impozabile** înregistrate într-un an fiscal […] precum și **cheltuielile efectuate în scopul desfășurării activității economice** […] potrivit art. 25"* |
| **activități independente, sistem real** | **CF art. 68 alin. (8)–(9)** | *„au obligația să completeze Registrul de evidență fiscală, **în vederea stabilirii venitului net anual**"*; modelul se aprobă prin ordin |

**Verdictul, per regim — și sunt opuse:**

- **Partidă simplă: CALCULUL EXISTĂ, artefactul nu.** `core/rip_api.py` clasifică **fiecare
  operațiune** (`CATEGORII_PLATA` = *cheltuiala_deductibila · cheltuiala_limitata ·
  cheltuiala_nedeductibila · aport_retragere · rambursare_credit*), iar `deductibilitate` e **câmp
  obligatoriu** la validare; `fisa_d212()` agregă pe an, iar `d212_engine.calculeaza_d212(venit_brut,
  cheltuieli_deductibile, …)` produce **venitul net**. Aia e **exact** ce cere art. 68 să stabilească
  registrul. Deci poziția nu e „artefact fără producător": e **PREDARE** — lipsește forma, nu calculul.
- **Partidă dublă (profit): CALCULUL NU EXISTĂ.** `d101.calcul_d101` primește `P1, P2, P4, P5` *„din
  contabilitate"* **plus ajustările fiscale „din manual"** — le tastează contabilul, nu se derivă. Iar
  `inregistrari` / `inregistrari_linii` **n-au nicio coloană de deductibilitate** (spre deosebire de
  RIP). Deci evidența **per operațiune** pe care o cere art. 19 alin. (7) nu există nicăieri.
  **CONSTRUCȚIE — și mai mare decât părea**: nu e o randare care lipsește, e o clasificare per
  operațiune care nu s-a scris.

**CONSTRUIT 23.08.2026, primul artefact din pragul 3: `core/fisa_cont.py` — Fișa de cont pentru
operațiuni diverse (cod 14-6-22).** Aleasă prima fiindcă **stinge obligația Cărții mari în AMÂNDOUĂ
formele de înregistrare** — norma o spune la fel la 14-1-3 și la 14-1-3/a — deci un artefact în loc de
doi, și fără să depindă de R21 (forma de înregistrare). Ce produce, și e exact ce pierdea
`motor.carte_mare`: **cronologia** și **contul corespondent pe fiecare rând**, plus soldul purtat din
rând în rând **cu sensul lui** (D/C). Nu inventează sold inițial: dacă nu i se dă unul, pornește de la
zero **și o declară** (`sold_initial_declarat=False`), fiindcă o fișă care pornește tăcut de la zero
afirmă că înainte n-a fost nimic. Gardă: `core/test_fisa_cont.py`, **15 teste**, RED-probat cu **2
mutații** — prima (fișa pierde contul corespondent, redevine balanță) a picat imediat; **a doua (soldul
își pierde sensul) a TRECUT**, iar gardul a fost completat cu cazul în care soldul trece prin zero D→C.
*Propria mutație a găsit gaura propriei gărzi.*

  **ȘI POARTA A RESPINS-O, de două ori, pe reguli existente — se scrie fiindcă e chiar dovada că
  gărzile vechi lucrează.** (1) `test_afirmatii_tipate` a picat: fișa întorcea un **dict de proză**,
  deși e o afirmație despre datele firmei (P3, 21.08). Tipată ca `fapt`, cu **`temei_completitudine`**
  — *toate liniile care ating contul, pe note validate, în interval, cronologic; ciornele nu sunt
  evidență*. La un control, exact câmpul ăla o face apărabilă: spune **de ce credem că am văzut tot**.
  (2) A picat din nou: **rândul** era tot un dict. Devenit `RandFisa`, dataclass — un rând care spune
  *„contul 5311 a primit 1000 de la 4111, sold 1000 D"* e o afirmație, iar conversia la dict se face la
  **margine** (`ca_dict`), pentru randare. **Artefactul a ieșit mai bun din respingere decât intrase.**

  **Ce NU s-a făcut**: randarea — fișa are producător, nu
  ecran; aia e lista 5.

**Ce se schimbă în poziția 1:** nu „3 artefacte fără producător", ci — după cele patru corectări —
**Cartea mare: construcție · Registrul-inventar: îngustare (există, regim simplu) · registrul de
evidență fiscală: DOUĂ, unul predare (simplă) și unul construcție mare (dublă)**. Din trei poziții
descrise, **niciuna nu era descrisă corect**.

#### CORECTARE 23.08 — ordinea: **3a înaintea lui 3b**, nu invers

Triajul s-a pornit peste **76** de interdicții, din care **50 scriu NEÎNCEPUTĂ** — iar avertismentul
din antet spune că cel puțin zece dintre ele **au cifre** în `GARZI.md` și `TESTE.md`. Verificat azi,
pe cele numite în `PLAN_INVESTIGATII.md` §3a: **6, 7, 8, 9, 10, 11, 12, 13, 14, 20, 26, 34 — toate
douăsprezece scriu încă NEÎNCEPUTĂ.** Zero transferate.

**Deci triajul a ordonat pe poziții necunoscute.** Un triaj pe ce n-a fost măsurat ordonează după
presupuneri, iar planul însuși pune **3a înaintea lui 3b** — ordinea era scrisă, nu s-a respectat.

**Ce se schimbă și ce nu.** Pragul 3 e ordonat pe **artefacte** (faza 1), nu pe interdicții
NEÎNCEPUTE, deci ordinea lui **nu cade**; ce cade e pretenția că triajul acoperă toate 76. **3a intră
înaintea următoarei ture de triaj**, e mărginit (douăsprezece interdicții, cifre deja existente în
registre) și are regula de transfer deja scrisă: *o măsurătoare veche fără calibrare devine PARȚIAL,
nu MĂSURATĂ; ce nu se reconstituie onest rămâne NEÎNCEPUTĂ.* (Al treilea punct din 3a — *interdicțiile
49–75 n-au secțiuni* — **e făcut**: registrul are azi 76 de secțiuni.)

#### Ce NU intră în praguri, fiindcă cere o decizie, nu o reparație

Cele trei rămân aici și **nu blochează restul** (Costin, 23.08).

- **R18 — cele două porți vide.** Nu se repară cu cod: ori există iar clustere de ordonat, ori se
  declară că mecanismul se verifică doar pe date sintetice. **Cere decizie.**
- **R14 — cele două populații de facturi.** Decizia de nomenclator, apoi migrarea; a doua nu e
  opțională odată ce prima s-a luat.
- **55 — categoriile de reverificare.** Axa e decisă (frecvența istorică a articolului, ponderată de
  consecință); **categoriile concrete sunt propuse la secțiunea 55** și așteaptă confirmarea.

*(A patra, „cum se citește pragul 1 pe o instalare fără clienți", a fost **LĂMURITĂ 23.08**:
atingibilitate.)*

## RESTANȚE

Ce a rămas neterminat, cu **felul blocajului** și **condiția de deblocare scrisă**. O restanță fără
condiție de deblocare e o notă; una cu condiție e o poartă.

**Cele PATRU feluri de blocaj**, definite în `PLAN_LUCRU.md` („Restanțele"): **SURSĂ** (temeiul nu se
poate cita complet sau corect) · **VERIFICARE** (instrumentul nu ajunge până acolo) · **ARTEFACT** (nu
se poate spune ce datorează o firmă) · **ORDINE** (nimic tehnic nu blochează — doar nu e momentul;
condiția de deblocare e un MOMENT din plan).

**Fiecare restanță poartă și `unde intră`** — etapa, și interdicția dacă are una — plus **`reluări`**,
de câte ori a fost reluată fără rezultat. Trei reluări fără rezultat înseamnă că **condiția de
deblocare e scrisă greșit**, nu că restanța e grea; atunci se rescrie condiția, prin decizie.

**UN SINGUR CONTOR, și motivul pentru care al doilea a fost RETRAS (23.08.2026).** Am adăugat un
câmp `încercări`, distinct de `reluări`, fiindcă *„câte au fost încercate"* nu se numără nicăieri.
**Retras în aceeași zi, la decizia lui Costin, și argumentul e mai bun decât al meu:** era un câmp
**întreținut manual** pe fiecare secțiune, purtând o informație **derivabilă din git** — exact clasa
care a stricat antetul de patru ori. Iar *„prima încercare"* nu se poate defini fără arbitrar: o
citire atentă e o încercare? o măsurătoare care n-a dus nicăieri? **Un contor care cere o convenție ca
să fie completat nu e o măsurătoare, e o opinie numerotată.**

**Contorul de commituri NU se scrie**: se derivă din git — câte commituri au atins `CONFORMITATE.md` de când s-a
deschis restanța. **Numără commituri, nu ture** — o tură poate produce mai multe, deci contorul urcă
mai repede decât ziua; e ce poate da git fără să inventez o noțiune de „tură". O restanță cu contorul
peste unu a supraviețuit cel puțin unei porți verzi și se arată ca atare în secțiunea B.

**Pragul, scris ca să nu rămână doar în cap (Costin, 22.08.2026).** Restanțele se deschid ca să fie
rezolvate, nu ca să fie colectate. **Punctul de control: închiderea lui 1b.** Dacă la acel moment
niciuna dintre restanțele deschise nu s-a mișcat — nici rezolvată, nici măcar măsurată — atunci
procedura colectează în loc să rezolve, iar asta se vede exact aici, în contoare. Nu e o regulă cu
gardă; e un prag de citit, la un moment numit.

**CITIT PE 23.08.2026, la cerere.** La `ccf6cb3` (închiderea lui 1b, 22.08) erau **15 restanțe
deschise**. Urmărite până azi: **1 rezolvată** (R2) · **2 mișcate fără rezolvare** (R14 — decizia
luată, devenită migrare; R16 — corp modificat) · **12 neatinse**.

**Pragul, citit literal, NU e atins:** trei s-au mișcat, deci nu „niciuna". **Citit pe fond, e la un
pas:** 12 din 15 stau neatinse la o zi după punctul de control, iar dintre ele **doar 3 au blocaj de
ORDINE** (R8, R9, R11) — adică doar trei își așteaptă legitim rândul. **Celelalte nouă** (R1, R3, R4,
R5, R6, R7, R10, R13, R15) n-au niciun moment de așteptat: patru SURSĂ, trei VERIFICARE, două ARTEFACT.

**Ce a scos citirea, și e mai grav decât pragul.** Contorul de **reluări e 0 pe TOATE cele 25 de
restanțe** — de la prima până la ultima. `PLAN_LUCRU.md` („Reaprinderea") cere ca la fiecare tură să se
verifice ce restanțe au blocajul dispărut; regula era **scrisă și nepăzită, deci se citea ca
respectată**. **Reaprinderea n-a funcționat niciodată.** Trei condiții s-au îndeplinit fără să fie
observate:

| restanța | condiția | când s-a îndeplinit |
|---|---|---|
| **R8** | *„la primul commit care atinge `d223.py` ori `d406.py`"* | **de două ori pe 23.08**, prin commituri proprii (`c3938af`, `25b07c0`) — declanșator **mecanic**, ratat |
| **R10** | prima jumătate cere `unde intră` pe fiecare restanță | textul restanței spune singur *„**există de azi**, deci nu mai e blocată de nimic tehnic"* |
| **R11** | *„la triajul din faza 3b"* | triajul a pornit pe 23.08 și a trecut prin pragurile 1 și 2 |

**Ce s-a construit din asta:** `core/test_reaprindere.py` face reaprinderea mecanică pentru clasa în
care declanșatorul E mecanic — o condiție care numește un fișier și verbul *„atinge"*. Gardul a fost
**roșu de la prima rulare, pe R8** — nu e RED-probat pe o mutație inventată, ci pe instanța reală care
l-a cerut. Ce nu acoperă, scris: declanșatoarele care nu sunt fișiere („la punctul de decizie 2")
rămân de citit de om.

**BILANȚUL ZILEI, pe restanțe** (de la `57c8189`, prima tură, la `2fe86ae`): deschise la început **16** ·
**închise 3** (R19, R21, R22) · **deschise noi 5** (R21, R22, R23, R24, R25 — dintre care R21 și R22
s-au și închis în aceeași zi) · **deschise acum 18**. **Intrări − ieșiri = +2.** Etapa nu se apropie de
închidere: se mișcă. Iar mișcarea e de un fel anume — restanțele noi vin din **măsurători care au
scos ce nu se știa**, nu din defecte noi.

### R1 — Câte alte acte din corpus sunt PARȚIALE

- **felul**: SURSĂ
- **cine deblochează**: INTERN
- **unde intră**: E2 · fără interdicție (corpusul, precondiția lui 49–59)
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `45f15ab`
- **ce blochează**: orice temei sprijinit pe un act adus parțial se citește ca „regula nu există", nu ca „pagina lipsește". Instanța cunoscută: OMFP 2634/2015, o anexă din trei — registrul de casă părea absent din lege.
- **condiția de deblocare**: un inventar al corpusului care spune, pentru fiecare act cu anexe, dacă anexele sunt aduse; plus regula de aducere scrisă în METODA, aplicată de acum înainte. Se închide când inventarul există și fiecare act parțial e ori completat, ori declarat parțial în `INDEX.json`.

### R2 — Vigoarea PE PUNCT, nu doar pe articol

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E2 · interdicțiile 49, 54
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `c7bcddb`
- **deschisă pe commit**: `45f15ab`
- **ce blochează**: Reglementările contabile (anexa OMFP 1802/2014) și Normele OMFP 2634/2015 sunt structurate pe **puncte**; `scripts/vigoare_articol.py` delimitează pe articole. Deci pentru familia B din 1a se cunoaște doar data consolidării actului, nu starea punctului folosit.
- **măsurat 23.08.2026**: **instrumentul e construit** — `scripts/vigoare_punct.py`, gardat de `core/test_vigoare_punct.py` (6 teste). Costul a fost **mai mic decât la articol**, dintr-un motiv care nu se vedea până nu s-a deschis actul: în forma consolidată, **marcajul își spune singur adresa în actul de bază** — *„(la 23-08-2024, Litera a), Alineatul (2), Punctul 9., Sectiunea 1.3, Capitolul 1 a fost modificată de..."*. Deci punctul nu se deduce din poziție, se citește. **Numitorul real e 8 puncte, nu 58**: verdictul 1d stă pe pct. 9, 20, 21 (Reglementări) și 44–48 (Norme).
- **rezultatul pe cele 8**: pct. **9** — modificat **23-08-2024** de ORDIN 4.164/2024 (exact ce știam, deci calibrarea trece); pct. **20** și **21** — găsite în act, **neatinse** de vreun marcaj; pct. **44–48** din Norme — găsite în act (64 de puncte detectate), **neatinse**.
- **cele două greșeli ale instrumentului, prinse la calibrare, nu după**: (1) expresia marcajului se oprea la primul `)`, care e chiar în „Litera a)", deci rata „Punctul 9." și raporta NEMODIFICAT punctul despre care **știam** că fusese modificat dimineața; (2) cunoștea un singur tipar de numerotare (`9. - (1)`), iar Normele scriu `45. Registrul-jurnal` — deci pe Anexa 1 vedea **zero puncte** și **răspundea totuși**, cu încredere. Amândouă sunt gardate acum, iar instrumentul **refuză** să răspundă pe un act în care nu vede niciun punct.
- **ce mai lipsește ca R2 să se închidă, și e puțin**: Anexa 1 are **doar 2 marcaje de consolidare în tot fișierul**, ceea ce e suspect de puțin pentru un act din 2015 consolidat la 01.08.2024. Ori chiar n-a fost modificată în zona punctelor 44–48, ori **extragerea a pierdut marcajele**. Se confruntă cu pagina de act de pe portal — o singură verificare, nu o campanie. Până atunci, „neatins" pe 44–48 se citește **împreună cu amprenta** `bf39029e…a87f`.

- **REZOLVATĂ 23.08.2026**, prin confruntarea cerută — **un caz pozitiv cunoscut din Anexa 1**: *„dacă nu-l găsește, instrumentul e rupt, nu anexa e goală."* **Era rupt.** Anexa 1 ARE modificări: ORDIN 1.447/2023 a **abrogat punctele 38 și 39**, în vigoare 24-05-2023. Instrumentul le rata din **două** cauze, amândouă prinse de cazul pozitiv și niciuna de recitire:
  1. cerea virgulă după „Punctul 38.", iar textul scrie „Punctul 38. **din** Litera C.";
  2. fereastra marcajului era **capturată** în expresie, nu feliată — cu `re.S` înghițea marcajele următoare, deci din 4 marcaje raporta 2. Aceeași greșeală ascundea **104 marcaje** și în Reglementări (220 → 324).
- **rezultatul final pe cele 8 puncte pe care stă verdictul 1d**: pct. **9** — modificat 23-08-2024 de ORDIN 4.164/2024 · pct. **20**, **21** — găsite, neatinse · pct. **44–48** — găsite (64 de puncte detectate în Anexa 1), **neatinse**. „Neatins" are acum greutate: instrumentul e dovedit pe câte un caz pozitiv **din fiecare dintre cele două acte**.
- **gardat**: `core/test_vigoare_punct.py`, 8 teste — cazul cunoscut din fiecare act, refuzul pe act fără puncte, distincția „negăsit" ≠ „neatins", și fereastra care nu înghite marcajul următor.
- **condiția de deblocare**: instrumentul citește și puncte, calibrat pe un punct despre care se ȘTIE că a fost modificat (pct. 9, ORDIN 4.164/2024) plus unul nemodificat plus un control negativ. **Cost măsurat, nu estimat din burtă: ~2 ore** — marcajele pe punct EXISTĂ și sunt mai bogate decât cele pe articol (numesc Litera, Alineatul, Punctul, Secțiunea, Capitolul: 58 de marcaje în act), dar titlul punctului e **în flux, nu la început de rând** (`9. - (1) În funcție de…`), deci delimitarea cere alt regex decât cel de articol. **E restanță de muncă, nu limită declarată.**

### R3 — Categoria de mărime nu există în aplicație

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · faza 1, familia B
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `45f15ab`
- **ce blochează**: componența situațiilor financiare depinde de categoria de mărime (micro / mică / mijlocie-mare). Nu e câmp în `firma_profil`, nu apare în vectorul fiscal.

  **ÎNGUSTATĂ 22.08.2026, după măsurătoare.** Formularea inițială — *„nu se poate spune, din date, ce set datorează, deci toată familia B nu poate intra în 1b"* — **era prea largă, și a costat o amânare**: familia B s-a măsurat totuși, iar R3 n-o bloca decât pe jumătate. **Datele există**: categoria s-a derivat de probă pe **toate cele 17 firme**, din `inregistrari_linii` și `salariati`, cu regula celor două criterii din trei. Ce lipsește nu e informația, ci **calculul** — nimeni nu-l face și nimic nu-l stochează. Deci restanța nu e „nu se poate ști", ci „nu se calculează".
- **CONSECINȚĂ MĂSURATĂ 26.08.2026, și e o cifră pentru LISTA 3 din verdictul 1d.** Scriind verificările lotului 1, Costin a cerut la `POST /tenants/{}/s1005-valideaza` și `s1003-valideaza`: *„situațiile financiare cerute depind de categoria de mărime. Dacă aceasta nu există ca dimensiune, ruta nu poate ști ce datorează firma — se declară, nu se presupune."* **Verificat la sursă: `grep -rn "categorie_marime|categoria_marime|micro_entitate|mijlocii|CATEGORII_MARIME"` pe tot codul, `.py` și `.js` — ZERO potriviri.** Nu e câmp, nu e derivare, nu e nici măcar un nume. Deci cele două rute **produc un artefact fără să poată ști dacă e cel datorat** — iar `bilant_api.genereaza_s1003` își spune singur în docstring *„S1003 (mici)"*, adică regimul e ales de **cine cheamă ruta**, nu derivat din firmă. **Lista 3** („nu ies / ies greșit fiindcă lipsesc date pe care aplicația nu le-a cerut"): situațiile financiare, pe criteriul mărimii. Cifra: **2 artefacte** (S1005, S1003), pe **17 firme**, niciuna cu categoria calculată.
- **condiția de deblocare**: categoria se derivă (active, cifră de afaceri netă, număr mediu de salariați, două criterii din trei, **la data bilanțului**) și **rezultatul devine interogabil** — nu recalculat ad-hoc de fiecare consumator, ci o singură dată, cu data la care s-a calculat, ca orice adevăr din registru. **Ce rămâne de lămurit la implementare, nu acum:** `active` trebuie luat din **bilanț**, nu din rulaje ca în proba de azi; iar „numărul mediu de salariați" e o medie pe exercițiu, nu numărul de azi. Se închide când fiecare firmă are categoria calculată pe date corecte, iar artefactele familiei B primesc verdictul care depinde de ea.

### R4 — Câte alte forme VECHI din corpus sunt citite ca fiind la zi

- **felul**: SURSĂ
- **cine deblochează**: INTERN
- **unde intră**: E2 · interdicția 52
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `45f15ab`
- **ce blochează**: o formă inițială dă valori reale, dar ale altui an, și nu se deosebește de o formă la zi decât dacă o întrebi. Instanța: criteriile de mărime, scrise în EUR din forma 2014, corectate în aceeași zi.
- **condiția de deblocare**: `TIP_FORMA` din `anaf_surse/gen_index.py` poartă deja răspunsul pentru fișierele legate de cote; se închide când orice fișier din care se citește un temei are forma declarată, iar citirea dintr-o formă marcată `forma_la_data` pentru o valoare CURENTĂ e imposibilă, nu doar nerecomandată.

### R5 — Marcajele din corpus nu se citesc la FOLOSIRE

- **felul**: SURSĂ
- **cine deblochează**: INTERN
- **unde intră**: E2 · interdicțiile 50, 52
- **reluări**: 1
- **stare**: DESCHISĂ
- **deschisă pe commit**: `07d5351`
- **ce blochează**: **măsurat înainte de a fi scris, nu presupus.** Din **529** de fișiere în `INDEX.json`, **47 poartă cel puțin un marcaj** (21 `forma_la_data` · 9 `consolidat_la_zi` · 11 detectate ca formă inițială · 2 abrogate · 2 cu text neextractibil), iar **18** dintre ele sunt legate de cote. **Patru poartă o notă explicită** — avertismente scrise de om: *„forma initiala 2014; NU include Ordinul 1239/2021…"* (`omfp_1802_2014.pdf` — chiar fișierul care a produs cifra falsă) · *„consolidare 2018, nu la zi"* · *„sursa legex.ro, neoficiala"* · *„abrogat de HG 773/2019 … HG 773/2019 nu e in corpus"*. **Cine citește marcajele: doar `gen_index.py` însuși și două gărzi.** Nimic la punctul de folosire — cine deschide fișierul ca să ia o valoare nu vede nimic. Asta nu e o instanță, e clasa din care instanța a ieșit.
- **condiția de deblocare**: marcajul ajunge la folosire, nu doar în manifest. Se închide când citirea unei valori CURENTE dintr-un fișier marcat `forma_la_data` sau cu notă e **imposibilă sau zgomotoasă prin construcție** — nu doar nerecomandată. Forma minimă acceptabilă: o gardă care leagă fiecare `Temei` de forma fișierului lui și pică pe combinația „valoare fără succesor + sursă marcată ca formă veche". Până atunci, cele 4 note se citesc manual înainte de orice valoare luată din acele fișiere.
- **ÎNCERCATĂ 23.08.2026 — a mers pe jumătate, iar eșecul e informativ.** Aleasă fiindcă antetul o numește, alături de R6, drept una dintre cele **două care blochează cel mai mult**. Prima citire a lui `INDEX.json` a dat **zero** fișiere marcate, deși restanța spune 47 — cauza: structura nu e o listă, ci `{"fisiere": {nume: {...}}}`. **Cu structura corectă, măsurătoarea legăturii cerute de condiție EXISTĂ acum: din 34 de obiecte `Temei` cu `url`, 23 arată spre un fișier care poartă un marcaj.** Deci gardul cerut de condiție **are pe ce lucra** — nu e vid, cum ar fi părut după prima citire.
- **UNDE S-A OPRIT, exact**: detectorul de marcaj e încă prea larg — a prins printre „marcate" și `gen_index.py`, care e un **script**, nu un act. Un gard construit pe el ar produce fals-pozitive din prima zi, iar un gard care se aprinde degeaba se dezactivează și moare. **Condiția de deblocare se ascute cu asta**: întâi se separă mecanic marcajele care spun ceva despre **forma actului** (`forma_la_data`, formă inițială, abrogat, sursă neoficială) de restul câmpurilor din `INDEX.json`; abia apoi se leagă de `Temei` fără `data_out`. *Motivul eșecului a devenit condiția, cum cere fluxul în cinci pași.*

### R6 — Ceva a scris într-un fișier de corpus, și nu se știe ce

- **felul**: SURSĂ
- **cine deblochează**: INTERN
- **unde intră**: E2 · interdicția 52
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `07d5351`
- **ce blochează**: `legea_82_1991_consolidat.html` a apărut modificat față de commit — 1629 de linii — **fără ca vreun script al turei să-l scrie**. Textul extras era identic; diferența e în chrome-ul paginii. Dacă ceva scrie în corpus fără să știm ce, interdicția 52 e păzită împotriva unui **simptom**, nu a cauzei: data viitoare diferența poate fi în text. **Ce s-a verificat deja, ca să nu se refacă:** niciun fișier `.py` din repo nu scrie în `anaf_surse/` (căutare pe `open(...,"w")`, `write(`, `urlretrieve`, `shutil.copy/move`) · singurul client HTTP din vecinătatea corpusului e `core/monitor_fiscal.py`, care **nu scrie fișiere** (trimite email și scrie în DB) · `gen_index.py` doar CITEȘTE fișierele, scrie numai `INDEX.json`.
- **condiția de deblocare**: scriitorul e **numit**. Garda nouă `core/test_corpus_amprenta.py` transformă tăcerea în poartă roșie: dacă se repetă, se aprinde la primul commit, iar comenzile turei sunt cunoscute, deci vinovatul e unul dintre ele. Se închide fie când garda se aprinde și scriitorul e identificat, fie când o reproducere deliberată îl numește. **Nu se închide** doar fiindcă nu s-a mai întâmplat — aia e tăcere, nu răspuns.

### R7 — Câte câmpuri obligatorii sunt gardate ca PREZENȚĂ, dar necontrolate ca ADEVĂR

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · faza 4 (instrumentele)
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `2375d54`
- **ce blochează**: **un câmp completat pe care nimic nu-l verifică arată identic cu unul verificat.** Instanța cunoscută nu e mică: corpusul avea **177 de amprente** și **niciun test care să le compare cu fișierele** — gardat ca prezență (fișierul `.sha256` există), necontrolat ca adevăr (nimeni nu recalcula hash-ul). Clasa e mai largă decât corpusul: `CONFORMITATE.md` gardează prezența câmpurilor `cifra`, `instanțe`, `calibrare`, `ce nu vede`, `pe commit`; `TESTE.md`, `GARZI.md`, `ISTORIC_TENANTI.md` au și ele câmpuri obligatorii. Pentru fiecare dintre ele se poate întreba dacă există un al doilea control, cel de adevăr — și **răspunsul nu e măsurat**.
- **condiția de deblocare**: măsurătoarea e făcută — pentru fiecare câmp obligatoriu din registre se spune dacă are control de adevăr, iar fiecare câmp fără control primește **ori un control**, ori o **declarație scrisă** că prezența e tot ce se poate verifica mecanic (ca la „temeiul determină comparația", unde declarația e răspunsul corect). Se închide când lista e completă, nu când primele câteva au fost reparate. **Nu se măsoară acum** — cerut explicit de Costin: *„Nu acum, dar nu-l lăsa nescris."*

### R8 — Cele trei egalități stricte, redeschise și nereverificate

- **felul**: ORDINE
- **cine deblochează**: INTERN
- **unde intră**: E3 · interdicția 21
- **reluări**: 1
- **stare**: DESCHISĂ
- **deschisă pe commit**: `1eaecbb`
- **ce blochează**: la prima citire, cele 15 potriviri ale interdicției 21 au fost triate **pe linie**; trei dintre cele numite zgomot merită a doua privire, **pe context**. Verificate azi, toate trei există în cod: `core/d223.py:159` — `len(asociati) == 1 and cota == Decimal(100)` (regula „100% doar cu un singur asociat"); `core/d406.py:1338` și `:1367` — `cota_l == 0` / `cota == 0` decid codul fiscal `300101` vs `300501`. Dacă vreuna e o **interpretare**, nu o regulă de lege, e o alegere făcută la scriere — adică exact interdicția 21, iar cifra „2 reale" rămâne plafon inferior. **Consemnate până azi doar în proză**, în patru locuri (`GARZI.md`, `ISTORIC.md`, `PREDARE_LANT.md`, câmpul „ce nu vede" al secțiunii 21) — nicăieri cu stare și condiție.
- **condiția de deblocare**: **la reluarea interdicției 21**, sau mai devreme, la primul commit care atinge `d223.py` ori `d406.py`. Se citește fiecare pe context, se spune dacă e lege sau interpretare, iar cifra secțiunii 21 se corectează în consecință.
- **RELUATĂ 23.08.2026 — declanșatorul se produsese, și nu fusese observat.** Condiția s-a îndeplinit **de două ori în aceeași zi**, prin commituri proprii care au atins `core/d406.py` (`c3938af` — reparația R22; `25b07c0` — felurile de jurnal). Reluarea s-a făcut abia după ce a fost căutată anume. **Două din trei sunt lămurite:**

  **`d406.py:1436` și `:1465` — INTERPRETARE, nu lege.** `tcod_l = "300101" if (r["ti"] or cota_l == 0) else "300501"`. Două dovezi, amândouă mecanice: (a) **modulul o declară singur** — antetul lui, la linia 21, scrie *„TaxCode achizitii pe deductibilitate reala (acum **grosier** 300501)"*; (b) `cota == 0` **contopește situații distincte în drept** — scutit **cu** drept de deducere, scutit **fără** drept, și operațiune neimpozabilă — care nu au același cod în nomenclatorul SAF-T. A alege un singur cod pentru toate trei e o decizie luată la scriere, nu o regulă citită din normă.

  **`d223.py:159` — RĂMÂNE DESCHISĂ, cu partea ei izolată.** `not (0 < cota < 100) and not (len(asociati) == 1 and cota == 100)`. Partea *„=100 doar cu un singur asociat"* **nu e interpretare**: e o consecință aritmetică a regulii de alături — suma cotelor trebuie să fie 100, deci cu un singur asociat singura valoare admisibilă e 100. Ce **nu** e derivabil e inegalitatea **strictă de jos**: `0 < cota` interzice un asociat cu cotă **zero**, iar asta nu decurge din suma = 100. E o alegere, până se citește norma D223 la sursă.
- **ce mai lipsește ca să se închidă**: verdictul pe `0 < cota` din `d223.py`, citit din actul care reglementează distribuirea la asociere. Restul e făcut.

### R9 — Ecranul statului de plată: STOP nemișcat

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E5 · fără interdicție (e o propunere vizuală, nu o clasă)
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `1eaecbb`
- **ce blochează**: semnalul de contradicție și butoanele emite/corectează **nu sunt în interfață**; capabilitatea e ajunsă prin API. Propunerea vizuală în cinci puncte așteaptă din 22.08. Reorganizarea unui ecran cere confirmare, deci nu se face în trecere — dar tocmai de aceea are nevoie de un loc cu stare, nu de un rând în `PREDARE_LANT.md`, care se rescrie la fiecare predare.
- **condiția de deblocare**: **când se atinge ecranul statului de plată** — fie pentru propunerea vizuală confirmată, fie pentru orice altă reparație pe el.

### R10 — Cerințe din „Restanțele" (PLAN_LUCRU) fără gardă

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E1 · fără interdicție (e disciplină de proces)
- **reluări**: 1
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `2bf9204`
- **deschisă pe commit**: `1eaecbb`
- **ce blochează**: cele **patru** cerințe din „Ce se gardează" (`PLAN_LUCRU.md`), cu starea fiecăreia la 22.08.2026 — **răspuns la întrebarea 5**: (1) *„un raport care nu enumeră restanțele deschise nu trece"* — **realizată în forma posibilă**: secțiunea B le enumeră, derivat din registru; **negardabilă mecanic**, fiindcă rapoartele nu trăiesc pe disc, iar asta se declară, nu se ascunde. (2) *„o restanță fără «ce o închide» nu poate fi scrisă"* — **implementată**, câmpul e obligatoriu. (3) *„o etapă nu se poate declara terminată dacă are restanțe deschise care îi aparțin"* — **implementată azi**, cu anti-vacuu. (4) *„o restanță cu blocaj EXTERN fără cerere specifică formulată nu trece"* — **NEIMPLEMENTATĂ, și singura rămasă**. **Răspuns la întrebarea 4: SE POATE GARDA, nu e o consecință acceptată.** Împăcarea a mutat EXTERN pe axa „cine deblochează", care azi e o notă în proză — dar nimic nu obligă să rămână așa: dacă devine **câmp** (`cine deblochează`: EXTERN / INTERN / DECIZIE), garda se scrie în trei rânduri, pe același tipar cu celelalte: valoarea EXTERN cere, în `condiția de deblocare`, cele trei elemente ale unei cereri specifice — **ce trebuie · de unde · pentru ce**. Deci rămâne restanță de muncă, cu condiția de deblocare acum concretă, nu limită declarată.
- **condiția de deblocare**: cele două gărzi există, RED-probate. Prima are nevoie de `unde intră` pe fiecare restanță — **există de azi**, deci nu mai e blocată de nimic tehnic; a doua are nevoie de o formă scrisă a cererii specifice.
- **ÎNCERCATĂ ȘI ÎNCHISĂ 23.08.2026 — costul încercării: două minute.** Aleasă anume ca **prima** dintre cele nouă neatinse fără blocaj de ORDINE, fiindcă textul ei spunea deja *„există de azi, deci nu mai e blocată de nimic tehnic"*. Verificate cele patru cerințe, una câte una, în `core/test_conformitate.py`: (1) *raportul enumeră restanțele* — realizată în forma posibilă, negardabilă mecanic, **declarat**; (2) *restanță fără „ce o închide"* — `CAMPURI_RESTANTA` include `condiția de deblocare`, obligatoriu; (3) *etapa nu se închide peste restanțele ei* — `test_o_etapa_nu_se_inchide_peste_restantele_ei`, cu anti-vacuu (`test_cititorul_de_etape_terminate_chiar_vede`); (4) *EXTERN fără cerere specifică* — `test_o_restanta_EXTERN_are_cerere_specifica`, cu anti-vacuu (`test_gardul_EXTERN_chiar_ar_prinde`). **Toate patru sunt acoperite, și erau de pe 22.08.** Restanța n-a fost grea: **n-a fost încercată**. Asta e chiar răspunsul pe care îl căuta încercarea.

### R11 — Datoria veche consemnată doar în proză, în GARZI.md

- **felul**: ORDINE
- **cine deblochează**: INTERN
- **unde intră**: E3 · faza 3b (triajul)
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `1eaecbb`
- **ce blochează**: zece poziții de forma „găsit, NU se repară acum", care trăiesc numai ca proză în `GARZI.md`, în afara ferestrei de două zile. **Enumerate aici, o linie fiecare — răspuns la întrebarea 4:** transcrierea *prozei* ar fi mutat proză în proză, dar **numirea** lor nu e transcriere, e indexare: diferența dintre „nouă lucruri necunoscute" și „nouă lucruri numite" e exact ce a produs auditul.
  1. `:1005` — defect declarat **LATENT**, nedeclanșat: „de reparat ÎNAINTE să existe date reale".
  2. `:1128` — depășire de plafon vs. responsabilitatea contabilului; „NU se repară acum", descoperit la confruntarea celor 4 corecții C-1.
  3. `:1163` — CF art. 139/140 la sursă; „NU se repară **unilateral**" (schimbă ieșirea la ANAF); **xfail-ancoră nescrisă încă**.
  4. `:1248` — „RĂMÂNE DESCHIS: Finding 2b — rotunjire Σ(round) vs round(total)"; datorie separată, coincid doar pe fixturi non-graniță.
  5. `:1370` — emisia `D_8`, neatinsă „în afara scopului impozit".
  6. `:1389` — **GL neechilibrat**: nu se verifică Σdebit = Σcredit; datorie separată, cablare d406 după curățarea fixturilor.
  7. `:1502` — risc pe date NULL curente + touch pe multe tabele; scopat separat pe buget (C3, job nocturn).
  8. `:1576` — „NEREPARAT în această tură": buget de context + decizie de design pe forma API-ului de perioadă.
  9. `:1603` — R13 (art. 331), „D300 furnizor taxare inversă", item separat; firmele fără taxare inversă emisă neafectate.
  10. `:1837` — xfail rămas deschis: amortizarea fiscală ca input P11, afectează afișarea D406 Assets.
- **condiția de deblocare**: **la triajul din faza 3b**, care trece o dată peste toate cele 75 de interdicții — acolo fiecare dintre ele primește ori o instanță într-o secțiune, ori o restanță proprie. Până atunci rămân numărate aici, nu transcrise.

### R12 — Divergență între D300 și D100 pe aceeași firmă, același fapt

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · faza 1, pasul 1b · interdicția 17
- **reluări**: 0
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `cbf7b67`
- **rezolvată pe commit**: `42c9e85`
- **ce blochează**: (istoric) pe t003, D300 ieșea `valid` cu 0 operațiuni, iar D100 refuza pe aceeași firmă și perioadă. Nu puteau avea amândoi dreptate.
- **condiția de deblocare**: **îndeplinită — experimentul s-a făcut.** Ipoteza inițială („facturi necontabilizate") s-a dovedit greșită la prima privire în date: facturile **erau** contate, dar notele erau `ciornă`. Experimentul s-a îngustat la **ciornă vs validat**: am validat cele două note prin ruta aplicației (`/tenants/{id}/jurnal/{nota}/valideaza`). **Rezultat: D100 refuz → `valid`, 1 operațiune. D300: `valid` cu 0 operațiuni, ÎNAINTE și DUPĂ.** Deci **D100 avea dreptate** — citea contabilitatea validată și refuza corect. **D300 nu vedea facturile în niciuna dintre stări**, iar cauza s-a găsit citind filtrul: `status='de_preluat'`, exclus prin construcție. Defectul real e mai mare decât divergența și a trecut în **pragul 1, poziția 1.1**.

### R13 — Partener fără cod fiscal pe factură

- **stare**: REZOLVATĂ
- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · faza 1, pasul 1b
- **reluări**: 1
- **rezolvată pe commit**: `c22a0c5`
- **stare**: DESCHISĂ
- **deschisă pe commit**: `44d30cf`
- **ce blochează**: măsurat la Q2 (evidența TVA): pe t003, **una din trei facturi are `tert_cui = NULL`** (CMT149, către „Agentie Turism Marja SRL"). Un jurnal de vânzări și D394 cer partenerul cu codul lui; fără el, operațiunea nu se poate raporta pe partener. Nu e o lipsă de structură — coloana există — ci de **completitudine a datelor**, deci se rezolvă altfel decât o absență de producător.
- **condiția de deblocare**: se măsoară **câte** facturi din matrice n-au cod de partener, pe direcție și pe plătitor de TVA, și se stabilește dacă lipsa e legitimă (persoană fizică) sau nu.
- **ÎNCERCATĂ 23.08.2026, prima jumătate a condiției e FĂCUTĂ.** Măsurat pe cele 23 de scheme: **42 de facturi în total, 2 fără cod de partener** — `tenant_003` / `CMT149`, direcție **emisă**, partener *„Agentie Turism Marja SRL"*; `tenant_013` / `PF-01`, direcție **primită**, partener *„IONESCU MARIA PFA"*. **Prima nu e legitimă**: un SRL e persoană impozabilă și are CUI, iar factura emisă către el trebuie să-l poarte. A doua e o PFA — tot persoană impozabilă, deci nici ea nu e evident legitimă, dar aici lipsa poate veni din felul în care a fost introdusă, nu din natura partenerului. **Ce a rămas**: nu s-a defalcat pe *plătitor de TVA*, fiindcă domeniul e prea mic ca defalcarea să spună ceva — 2 cazuri. Restanța nu se închide, dar nu mai e nemăsurată: **e o listă de două nume**, nu o clasă necunoscută.
- **A DOUA JUMĂTATE A CONDIȚIEI, numită la cerere:** *„se decide dacă aplicația trebuie să **ceară codul la introducere** (P23) sau doar **să-l semnaleze**."* Aia e ce a rămas — o decizie de produs, nu o măsurătoare.
- **DE UNDE AU VENIT CELE DOUĂ — și asta schimbă felul restanței.** `CMT149` (t003): `sursa_externa` **NULL**, `status = de_preluat` — starea produsă chiar de `emite_factura`, deci factura a intrat **prin aplicație**, nu prin import. `PF-01` (t013): `status = importata`, deci prin import. **Iar validare nu există**: `facturi_api.creeaza_factura` și `emite_factura` au amândouă `tert_cui=None` ca **default de parametru**, iar în tot `facturi_api.py` și `main.py` **nu există nicio verificare** pe `tert_cui` — nici prezență, nici checksum. **Deci un SRL fără CUI introdus prin aplicație e un defect de VALIDARE, nu o restanță de măsurat**, cum a observat Costin. Ce ține restanța deschisă e doar decizia (a cere vs a semnala); **defectul de validare e altceva și trece la reparații**, cu observația că `tert_cui` fiind default de parametru e și o instanță a interdicției **14**.
- **DECIS 23.08.2026 (Costin): se CERE la introducere, nu se semnalează.** Motivul, verbatim: *„o factură fără CUI de partener nu intră în D394 și nu se poate corela în VIES. Nu e o coloană goală, e o declarație incompletă la prima firmă reală"* — și *„un CUI lipsă nu se poate completa retroactiv de nimeni altcineva decât cel care a emis factura"*. **REPARAT în aceeași tură, ca prag 2**: `facturi_api.cere_cod_partener`, chemată din **amândouă** căile de creare; excepția e **declarată explicit** (`tert_pf=True`), nu dedusă din nume sau din lipsă. Singurul apelant legitim fără cod — importul WooCommerce — o declară, cu motivul scris. **Poarta a respins prima încercare, și a avut dreptate a treia oară azi**: garda a prins handlerul de *achiziție de la o persoană neînregistrată* (`main.py:7748`), unde lipsa codului e **legitimă** — dar era declarată **doar într-un comentariu**, pe care nicio gardă n-o poate citi. Acum o spune codul: `tert_pf=True`. *Exact clasa interdicției 16 — proza care descrie codul — prinsă de o gardă construită pentru altceva.* Gardă: `core/test_cod_partener.py`, 9 teste, RED-probat cu 2 mutații (garda scoasă din `emite_factura` → anti-vacuu roșu; excepția devenită tăcută → 7 roșii). **Restanța se închide**: măsurătoarea era făcută, decizia e luată, reparația e în poartă.
- **Ce NU e prag 1, și de ce o spun explicit**: toate cele 17 firme sunt de test (`Agentie Turism Marja SRL` e un nume de fixtură), deci **niciun contabil nu are azi o factură greșită**. Efectul e potențial, nu actual — dar calea de intrare e de producție. Abia apoi se decide dacă aplicația trebuie să ceară codul la introducere (P23) sau doar să-l semnaleze.

### R14 — Două funcții de creare a facturii, cu stări implicite diferite

- **felul**: ORDINE
- **cine deblochează**: INTERN
- **unde intră**: E3 · interdicția 17
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `4853dfb`
- **ce blochează**: `facturi_api.creeaza_factura` creează cu `status="emisa"` (7 apelanți), `facturi_api.emite_factura` cu `status="de_preluat"` (6 apelanți), iar modelul `FacturaIn` (`main.py:811`) are tot `"emisa"`. **Nu există nicio tranziție între ele** — starea unei facturi e decisă o dată, la creare, de care funcție a fost chemată, și nu se mai schimbă niciodată.

  **MĂSURAT (22.08.2026), și cifra reîncadrează restanța.** Pe cele 17 scheme, facturile emise:
  **27 `emisa` · 4 `de_preluat` · 10 `importata`**. Dar distribuția **nu e separată pe firme**:

  | firmă | stări pe aceeași firmă |
  |---|---|
  | t003 | `de_preluat` 2 · `emisa` 1 |
  | t005 | `de_preluat` 1 · `emisa` 2 |
  | t013 | `de_preluat` 1 · `importata` 5 |

  **Trei firme din douăsprezece au populații amestecate** — aceleași facturi emise, în aceeași firmă,
  poartă stări diferite după care funcție le-a creat. Deci deblocarea **nu mai e doar o decizie de
  nomenclator: e și o migrare de date.** O decizie care unifică stările lasă în urmă facturi vechi în
  starea cealaltă, iar orice regulă viitoare care se atașează de „starea unei facturi" le va vedea
  împărțite după un criteriu care nu înseamnă nimic.
- **DECIS 23.08.2026 (Costin) — restanța NU mai e de nomenclator, e o MIGRARE.** Motivul, scris: *„două populații cu aceeași etichetă înseamnă că orice regulă scrisă de acum înainte e adevărată pentru jumătate din date."* Deci pasul (1) de mai jos **e luat**: distincția nu e reală, stările se unifică. Ce rămâne e pasul (2), și **nu e opțional** — dar **nu se face acum**: intră **la reparații**, de unde și felul schimbat din SURSĂ în ORDINE. **NUMIT 23.08.2026 (Costin): supraviețuiește `emisa`.** Motivul, verbatim: *„E starea care
  descrie faptul: factura a fost emisă. «de_preluat» descrie o intenție de proces care nu s-a întâmplat
  niciodată — nimic n-o consumă."* **Migrarea e într-o direcție**: `de_preluat` → `emisa`, pe tot ce nu
  e ciornă, anulată sau descărcată. **Nu invers.**

  **Două lucruri de verificat la migrare, nu acum, dar scrise ca să nu se piardă.** (a) Filtrul numit
  (*ciornă / anulată / descărcată*) e pe **aceeași coloană** `status` ca `de_preluat`, deci un rând nu
  poate fi și una și alta; se verifică dacă vreun rând `de_preluat` poartă marcajul de ciornă/anulare
  **într-o altă coloană** — dacă nu, filtrul e o plasă de siguranță, nu o restricție. (b) **Decizia de
  interpretare din 22.08 devine fără obiect** și trebuie stinsă odată cu migrarea: `nomenclator_status_factura.py`
  poartă alegerea *„`de_preluat` e stare FINALĂ, deci DECLARABILĂ"*, confirmată de Costin pe 22.08 sub
  pragul 1. Odată ce starea dispare, interpretarea nu se șterge — se marchează **stinsă prin migrare**,
  cu varianta respinsă ținută vie, cum cere registrul.
- **condiția de deblocare**: **două lucruri, în ordinea asta.** (1) — **LUAT 23.08** — Se decide dacă cele două funcții trebuie să producă **aceeași** stare — și atunci una dintre valori dispare — sau dacă distincția e reală și trebuie **numită** în nomenclator, nu dedusă din care funcție a fost chemată. (2) **Migrarea populațiilor existente**, care nu e opțională odată ce (1) s-a luat: pe cele trei firme amestecate, facturile din starea care dispare trebuie mutate, altfel decizia e adevărată doar pentru facturile viitoare. Se închide când ambele s-au făcut, nu doar prima.

### R15 — Perechile verificator/verificat copiază CONDIȚII, nu doar constante

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · interdicțiile 11, 12
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `4853dfb`
- **ce blochează**: `test_cale_a_doua` verifică **importul** — calea a doua nu importă modulul verificat. Dar Partea V spune și *„nu-i copiază constantele"*, iar **o condiție SQL identică e o constantă compusă**. Măsurat pe cele 9 perechi `*_reconciliere.py`: **7 condiții identice, pe 3 perechi** — `d300` 4 (`COALESCE(f.taxare_inversa, false) = false`, `COALESCE(f.furnizor_tva_incasare, false) = true`, `NOT (f.directie = 'primita'…`), `d394` 2, `d101` 1. Exact clasa care a produs defectul de azi: filtrul pe status era a 5-a, iar reconcilierea n-a prins omisiunea fiindcă **vedea aceeași realitate trunchiată**. **Cifra e plafon inferior:** metoda compară fragmente textuale normalizate, deci nu vede o condiție rescrisă cu altă ordine sau alt alias; iar 2 din cele 7 sunt fragmente lungi de SELECT, tăiate imperfect de instrument — deci **~5 reale**.
- **condiția de deblocare**: fiecare condiție comună primește ori o **sursă unică** (ca `nomenclator_status_factura.clauza_sql`), ori o **declarație scrisă** că duplicarea e deliberată și de ce — tiparul există deja: `test_d300_reconciliere.test_non_tautologie_*` apără o duplicare **voită**. Se închide când `test_cale_a_doua` capătă și axa condițiilor, nu doar a importului.
- **ordinea la deblocare, scrisă ca să nu fie alfabetică**: observația care contează nu e că reconcilierea era slabă în general — era slabă **exact acolo unde a contat**. Filtrul pe status era a cincea condiție copiată din `d300`, iar el decidea **ce intră în declarație**. Deci: **întâi condițiile care decid ce intră în declarație** (`taxare_inversa`, `furnizor_tva_incasare`, `directie`, `tip`), **apoi restul**. O condiție care doar taie o coloană dintr-un SELECT nu are aceeași greutate cu una care hotărăște dacă o factură e declarată.

### R16 — Proza care descrie codul poate fi FALSĂ DE LA NAȘTERE

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · faza 4 (instrumentele) · interdicția 18
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `554ae17`
- **ce blochează**: docstringul din `core/export_saga.py:157` spunea că *„WinMentor cere `status='emisa'` — doar facturi emise corect, nu `de_preluat`/`anulata`"*. **Era invers, și era invers de la scriere:** F187-fix scosese tocmai acel filtru din WinMentor. **Nu e aceeași clasă cu doc-stătut** — acolo codul se schimbă sub un text care fusese adevărat; aici textul n-a fost adevărat niciodată. **Măsurat, cu proxy declarat:** docstringuri care afirmă `param='valoare'` pentru un parametru **al lor**, contrazis de semnătură — **1 instanță** (`core/observare.py:114`, `trimite_email_html()`: docstringul zice `expeditor_nume='<Firma> prin iConta'`, semnătura are `'iConta.eu'`). **Cifra e plafon inferior, și limita e chiar cazul care a produs restanța:** o afirmație despre **alt modul** — ce cere WinMentor — **n-are proxy mecanic**. Se poate verifica doar citind ambele module.
- **condiția de deblocare**: proxy-ul pe propriile valori implicite devine gardă (ieftin: e deja scris ca măsurătoare), **iar** pentru afirmațiile despre alte module se scrie regula că o frază care descrie comportamentul altui modul poartă referința la locul din care a fost citită — cum poartă `Temei` un citat. Se închide când amândouă există; prima singură ar lăsa exact clasa care a produs restanța.

### R17 — Graful de dependențe e cheiat pe NUME SIMPLU, plat peste tot `core/`

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · faza 4 (instrumentele) · interdicțiile 61–62 (lista dependenților)
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `c7bcddb`
- **deschisă pe commit**: `4033a14`
- **ce blochează**: `core/graf_temei.construieste_graf` construiește `functii[node.name] = (fisier, node)` — un dicționar **plat, cheiat pe numele simplu**, peste tot `core/*.py`, care include și definițiile **imbricate**. Când două fișiere definesc același nume, **ultimul alfabetic câștigă**, iar toți apelanții celuilalt sunt rerutați tăcut către el. Pe graful ăsta stă `agenda.cote_cluster`, adică baza resetării propagate V3 (`test_bifele_nu_stau_pe_o_baza_schimbata`).

  **MĂSURAT (22.08.2026)**: din **1.411** nume de funcții din `core/`, **118 sunt definite în mai multe fișiere**. Cele mai răspândite sunt chiar punctele de intrare ale declarațiilor: `genereaza` — **53 de fișiere**, `pull` — 52, `erori_generare` — 51, `build_xml` — 49, `_esc` — 49, `_cif` — 39. Unsprezece dintre cele 118 au cel puțin o definiție **imbricată**, deci invizibilă la o citire de sus.

  **Cum a ieșit la iveală, și de ce contează forma:** reparația de prag 1 de la fluturaș a adăugat un helper imbricat numit `_suma` — al șaselea din `core/`. `stat_plata_api.py` sortează după `d130`, `d213`, `d710`, `kpi_client`, `sgr`, deci **a preluat toți apelanții lor**, iar clusterele D300, D394 și regim marjă au apărut brusc ca depinzând de `salariu_minim`, `cam`, `cas`, `tichet_masa_plafon`. Ratchet-ul a sărit de la **14 la 35** și a blocat poarta.

  **Garda a prins-o — dar numai în direcția zgomotoasă.** Un nume preluat ADAUGĂ dependențe false, iar numărul crește și poarta cade. Direcția tăcută e cealaltă: o dependență **reală** dispare când numele funcției e preluat de alt fișier, iar atunci o cotă schimbată sub o bifă **nu se mai vede deloc**. Aceeași cauză, semn opus, și niciun gard nu se uită acolo.

  **Consecință asupra unei cifre deja scrise:** `STALE_BAZA_BASELINE = 14` a fost măsurat **pe graful conflat**. Nu e o cifră care se poate crede ca atare până nu se recalculează pe un graf corectat.
- **cât e de mare, măsurat 23.08.2026 pe commit `4a0c9b9`** (cerut ca să se știe dacă e restanță sau prag 2):
  - `core/` are **2.173 definiții** de funcții; graful păstrează **1.412 noduri** → **761 de definiții (35,0%) sunt pierdute prin cheia scurtă**.
  - harta pe care stau gărzile are **79 de clustere**, dintre care 30 cu cote derivate, și **88 de muchii (cluster, cotă)**.
  - **2 muchii** sunt pinuite de un test care afirmă PREZENȚA. **86 din 88 pot dispărea fără ca vreun test să se aprindă.**
  - **57 din cele 79 de clustere** au lanțul trecând printr-un nume conflat. *(Instrumentul meu a tipărit „57 din 30" — raport imposibil; numitorul corect e 79, toate clusterele, nu 30, care numără doar clusterele cu cote. Greșeala e a etichetei mele, nu a măsurătorii, și o scriu în loc s-o corectez tăcut.)*
  - câștigătorii sunt arbitrari și absurzi: `genereaza` (53 de fișiere) → graful păstrează doar `declaratii_api.py`; `build_xml` (49) și `erori_generare` (51) → doar `d710.py`; `pull` (52) → `scadentar.py`.
- **câte porți verzi sunt false** (întrebarea pusă direct): **10 funcții de test stau pe graf. 7 afirmă PREZENȚA** unei muchii — o muchie dispărută le face ROȘII, deci sunt zgomotoase și în regulă. **3 devin VERZI** când o muchie dispare: `test_bifele_nu_stau_pe_o_baza_schimbata` (prag `len(stale) <= 14` — mai puține muchii, mai puține stale), `test_secventa_persistata_e_topologica` (`assert not viol` — mai puține muchii, mai puține violări) și `test_secventa_persistata_e_actuala`, care compară **două derivări ale aceluiași graf greșit** și e verde prin construcție. Cele 7 zgomotoase pin **2 muchii din 88**; restul hărții e nepăzit în direcția tăcută.
- **prag**: **PRAGUL 2**, după definiția din `PLAN_LUCRU.md` — cauză unică dovedită (dicționarul cheiat pe nume) și nu concurează cu nimic (n-are instanțe de ordonat). Nereparat acum, cum s-a cerut.

- **REPARAT 23.08.2026**, pe commit `c7bcddb`, cu ce a ieșit la iveală:
  - **cheia**: `"fisier.py::nume"`. Verificat înainte de a alege, fiindcă definițiile imbricate stau în același fișier: `(fișier, nume)` lasă **o singură coliziune în tot `core/`** — `common.py::__init__`, două clase imbricate. Cheia e suficientă pentru 2.172 din 2.173, iar coliziunea rămasă e numărată, nu ascunsă.
  - **jumătatea care conta mai mult**: apelurile nu se mai potrivesc pe nume. `alias.N(...)` se rezolvă prin **importurile fișierului**; `N(...)` întâi în același fișier, apoi prin `from core.M import N`; iar ce rămâne nerezolvat se leagă de **toți** candidații — supra-aproximare **deliberată**, ca greșeala să cadă în direcția zgomotoasă. Reziduul se numără: **10 nume** (`_esc` 49 candidați, `_d` 36, restul sub 10).
  - **graful**: **1.412 → 2.180 de noduri**.
  - **a cerut memoizare**: `cote_cluster` cerea graful o dată per cluster per funcție de test, iar graful e cu 54% mai mare — suita trecuse de bugetul porții.
- **ce a ascuns conflatarea, măsurat după reparație** — și e direcția tăcută, cea prezisă:
  - **`depinde_de("salariu_minim")`: 12 → 83 de funcții**, pe 16 fișiere (10 directe, 73 tranzitive). **Doar 1 dintre ele vine printr-un nume ambiguu**, deci cifra nu e umflată de supra-aproximare. *Când s-a schimbat salariul minim, lista locurilor de actualizat arăta 12.* **Nuanță onestă:** 37 din cele 83 sunt în `declaratii_api.py`, adică rutare — închiderea tranzitivă printr-un dispecer e adevărată, dar nu e „loc de actualizat".
  - **clustere cu dependențe în graf: 30 → 41** din 79. **Muchii (cluster, cotă): 88 → 120.**
  **Observație lipită de instrument, ca următorul care primește 83 să știe ce sunt** (cerut 23.08):
  **37 din cele 83 sunt în `declaratii_api.py`**, adică **rutare** — dispecerul cheamă fiecare
  generator, deci închiderea tranzitivă îl leagă de tot ce ating ei. Muchia e **adevărată**, dar nu e
  „loc de actualizat": cine ia cele 83 ca listă de lucru va găsi o treime din ea inutilă. Se îngustează
  **la prima folosire reală**, nu preventiv — un filtru scris acum, pe un caz imaginat, ar fi la fel de
  necalibrat ca graful pe care tocmai l-am reparat.

  - **stale: 14 → 11.** Graful reparat e mai MARE și totuși stale-urile SCAD — deci cifra veche nu era doar necreditabilă, era **umflată**: conflatarea atribuia clusterelor cote de care nu depindeau. Clichetul coboară la 11.
- **cele trei porți false, verificate una câte una** (cerut explicit — „redevin verzi din motive reale, sau abia acum arată ce ascundeau?"):
  - `test_bifele_nu_stau_pe_o_baza_schimbata` — **verde din motiv real**: 11 stale reale, sub prag. Cifra s-a schimbat, deci poarta chiar măsura ceva.
  - `test_secventa_persistata_e_topologica` și `test_secventa_persistata_e_actuala` — **verzi din VACUITATE, nu din corectitudine**: `secvența calculată = 0`, `persistată = 0`. Campania s-a epuizat pe 04.08.2026, deci de **19 zile** cele două teste trec fără să compare nimic. Nu devin roșii după reparație; **nu pot deveni**, până nu mai există clustere de ordonat. Asta ascundeau. *Corect e să se spună și partea bună:* mecanismul e totuși gardat, de `test_secventa_prinde_inversiune`, care rulează checker-ul pe date sintetice — deci e vidă **verificarea pe date reale**, nu unealta.
- **cele 7 porți zgomotoase, întrebarea „au prins vreodată ceva?"**: în cele 22 de zile de la `e516a23` (01.08.2026), **git nu arată niciun commit în care să fi picat și să fi cauzat o reparație** — cele trei fișiere au fost atinse doar ca să urmeze schimbări de cod (01.08, 02.08, 17.08). **Azi au picat, toate patru** care afirmau nume — dar la o schimbare de FORMĂ a cheii, nu la o dependență pierdută. Deci **nu sunt decorative, sunt înguste**: pin spina `salarizare` / `d100` / `d212` și nimic altceva. După reparație afirmațiile lor sunt **calificate** (`salarizare.py::calcul_salariu`, nu `calcul_salariu`), deci strict mai stricte decât înainte.
- **condiția de deblocare**: graful se cheie pe **`(fișier, nume)`**, nu pe nume; funcțiile imbricate ori se exclud, ori primesc cheie `(fișier, funcție-părinte, nume)`. Se închide când **toate trei** există: (a) cheia e calificată; (b) o gardă numără coliziunile rămase, cu clichet, ca 118 să nu crească tăcut; (c) `STALE_BAZA_BASELINE` e **re-măsurat** pe graful corectat — altfel rămâne o cifră moștenită dintr-o lume conflată. Prima singură ar muta numărul fără să spună nimeni de ce.

### R18 — Două porți verzi care nu pot deveni roșii

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E3 · faza 4 (instrumentele) · interdicția 19 (gardă care raportează favorabil pe zero rânduri)
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `241acf4`
- **ce blochează**: `test_secventa_persistata_e_topologica` și `test_secventa_persistata_e_actuala` verifică **ordinea** celor 64 de clustere contra grafului. **Secvența calculată = 0, persistată = 0** de pe **04.08.2026**, când campania s-a epuizat. Deci de **19 zile** cele două trec fără să compare nimic, iar repararea grafului (R17) **nu le-a schimbat cu nimic** — nu sunt verzi din corectitudine, sunt verzi din **vacuitate**, și nu pot deveni roșii până nu mai există clustere de ordonat. **Ce e totuși gardat, și trebuie spus:** mecanismul în sine — `test_secventa_prinde_inversiune` rulează checker-ul topologic pe date sintetice (X depinde de Y) și chiar prinde inversiunea. E vidă **verificarea pe date reale**, nu unealta.
- **RĂMÂNE DESCHISĂ prin decizie, 23.08.2026 (Costin)** — și varianta (b) e refuzată explicit, cu motivul scris: *„declarația «se verifică doar pe date sintetice» ar fi onestă, dar ar închide o gardă pe care o vrem reală."* Deci se așteaptă (a). **Condiția de predare a deciziei**: primele date care generează clustere. Până atunci restanța nu se reia și nu se renumără — starea ei nu e neglijență, e așteptare declarată.
- **condiția de deblocare**: **una din două, prin decizie, nu prin reparație** — (a) există iar clustere de ordonat, și atunci cele două redevin verificări reale; sau (b) se **declară scris** că ordinea se verifică doar pe date sintetice, iar cele două teste își schimbă numele și docstringul ca să nu mai pretindă că verifică secvența persistată. Ce nu e acceptabil e starea de azi: două nume care promit o verificare pe date reale și trec pe zero rânduri.

### R19 — `graf_clustere` tratează utilitarele partajate ca proprietate

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · faza 4 (instrumentele) · interdicțiile 61–62 (lista dependenților)
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `f189b81`
- **deschisă pe commit**: `241acf4`
- **ce blochează**: al **doilea** defect al aceluiași instrument, distinct de R17 și nereparat de el. `graf_clustere` declară că o funcție e „deținută" de clusterul ale cărui teste o cheamă. Propriul docstring spune *„funcție partajată = CO-LOCAȚIE, nu dependență"*, dar filtrul aplicat e doar `if f in own: continue` — adică exclude partajarea **cu sine**, nu partajarea **între alții**. Un utilitar chemat de testele a cinci clustere e „deținut" de toate cinci, iar orice al șaselea cluster care îl atinge tranzitiv capătă **cinci muchii de dependență**.

  **MĂSURAT 23.08.2026 pe graful reparat:** din **154** de funcții deținute, **70 sunt deținute de 2+ clustere**. `duk.py::valideaza` — de **21 de clustere**; `rip_migrare_api.py::get` — de 19; `duk.py::poate_valida` — de 11.

  **Efectul asupra cifrelor:** cu regula de azi, harta are **960 de muchii** între clustere. Cerând ca dovada să fie o funcție cu **proprietar unic**, rămân **111**. Adică **aproape 9 din 10 muchii sunt co-locație, nu dependență** — de acolo vin absurdități ca *„facilitate salariu minim depinde de «edge canonic www/HEAD (crawler)»"*.
- **condiția de deblocare**: proprietatea se decide altfel decât „testul o cheamă" — fie funcția aparține modulului pe care clusterul îl verifică, fie proprietarul se declară explicit în inventar. Se închide când numărul de muchii sprijinite pe funcții multi-proprietar e **zero**, iar cifra de 111 se re-măsoară — nu se moștenește cea de 960.
- **MĂSURAT 23.08.2026, la reluarea triajului: PRIMA VARIANTĂ NU E CALCULABILĂ AZI.** *„Funcția aparține modulului pe care clusterul îl verifică"* presupune că inventarul știe **ce modul** verifică un cluster. Nu știe: coloana `fisiere` poartă **fișierul de TEST**, nu modulul-sursă. Cifrele: **79 de clustere · 35 de fișiere de test distincte · 95 de perechi (cluster, fișier)**; doar **19** fișiere aparțin unui singur cluster, iar `test_salarizare.py` e împărțit de **8** clustere, `test_d300.py` / `test_d394.py` / `test_d406.py` de câte **7**. Probat mecanic: construind proprietatea din modul, pe cheile grafului (`fisier.py::functie`), rezultă **0 funcții cu proprietar** — potrivirea nu se poate face, fiindcă numele din inventar e al testului.
- **Deci varianta (a) ar muta ambiguitatea, n-ar rezolva-o**: opt clustere care împart `test_salarizare.py` ar deveni opt proprietari ai lui `salarizare.py` — exact co-locația de azi, urcată un nivel.
- **REZOLVATĂ 23.08.2026 — și nu prin niciuna dintre cele două variante scrise.** Întrebarea lui Costin — *„dacă e o decizie per cluster, sunt 79 de decizii și e a mea; dacă se poate deriva din ce verifică testul, e mecanic"* — a fost pusă **înainte** de a începe, și răspunsul măsurat e **mecanic**. A treia variantă, pe care condiția de deblocare n-o numea: **o funcție partajată nu primește un ALT proprietar — nu primește NICIUNUL.** Faptul că testele a două clustere o cheamă nu e o dovadă că vreunul o deține; e chiar definiția co-locației din docstringul instrumentului.
- **Cifrele, măsurate pe graful reparat:** funcții deținute **154 → 84** (cele **70** partajate ies din proprietate) · muchii **960 → 111** · clustere cu cel puțin o dependență **54 → 46** · **muchii sprijinite pe funcții multi-proprietar: 0** — chiar criteriul scris de închidere. **Nu s-a moștenit cifra de 960**, s-a re-măsurat. Bonus nesolicitat, dar semnificativ: **ciclurile scad de la 321 la 3** — o sortare topologică peste 321 de cicluri nu ordona nimic.
- **Ce rămâne, și se scrie:** cele **3 cicluri** rămase sunt în familia salarizării (*facilitate salariu minim* ↔ *deducere personală* ↔ *concedii medicale*) și par dependențe reciproce reale, nu artefacte ale regulii. Nu s-au atins.
- **Gardă**: `core/test_graf_clustere_proprietar.py`, **6 teste** — calibrare în ambele direcții pe caz sintetic, anti-vacuu pe inventarul real (*dacă nu există funcții partajate, gardul ar trece pe zero rânduri*) și **clichet pe 111 muchii**, care nu poate crește tăcut și nici coborî la zero (un graf vid n-ar ordona nimic — vezi R18). RED-probat: proprietatea readusă la *„toți cei care cheamă"* → **5 teste din 6 roșii**.

---

### R20 — Opt artefacte de UN OCTET în corpus, cu nume de declarație

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E2 · interdicția 52 (corpusul)
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `9510c94`
- **deschisă pe commit**: `139bca5`
- **ce blochează**: `d104.txt`, `d110_20260330.txt`, `d112_06082026.txt`, `d220_20180108.txt`, `d221_20170303.txt`, `d223_20160113.txt`, `d307_20171205.txt`, `d311_20210129.txt` — toate de **un octet** (o linie goală), create pe **13–14.08.2026**, fiecare **lângă un `.xsd` real și amprentat**. Sunt ieșirea unei derivări care a produs gol și n-a spus-o. **Nimeni nu le citește**: zero citări literale în cod, teste sau registre — verificat. Dar un fișier gol cu nume de act e **mai rău decât unul lipsă**: pentru orice instrument arată ca *act PREZENT și TĂCUT*, deci produce o absență falsă, nu o lipsă vizibilă. E aceeași clasă cu corolarul interdicției **76** — cazul în care lucrul e absent dar semnul lui e prezent.
- **condiția de deblocare**: o decizie între **ștergere** (XSD-ul de alături e prezent și amprentat, deci nu se pierde nimic) și **regenerare** din XSD, pe tiparul lui `d402_20160226_xsd_linii.txt`. **Nu se face fără decizie**: conținutul intenționat nu se poate deduce din nimic de pe disc, iar a-l inventa ar fi mai rău decât gol. Până atunci sunt sub clichet declarat în `anaf_surse/PROVENIENTA.json` (`goale_cunoscute`), iar `core/test_provenienta.py::test_niciun_artefact_gol_nou` face imposibil să apară al nouălea. Se închide când cele opt sunt ori șterse, ori au conținut, iar clichetul coboară la 0.
- **cum s-a închis (23.08.2026)**: **ȘTERSE**, prin decizia lui Costin — *„a le regenera din XSD ar însemna să inventăm ce trebuiau să conțină; un gol declarat e mai bun decât un conținut plauzibil.”* Înainte de ștergere, fiecare a fost verificat încă o dată **pe disc**: cel mult 2 octeti, cu XSD-ul de alături **prezent și amprentat** — deci nu s-a pierdut nimic. Clichetul a coborât **8 → 0**: de acum nu doar un artefact gol *nou* pică poarta, ci **orice** artefact gol din corpus.
- **DE CE EXISTAU — măsurat 23.08.2026, după închidere, fiindcă un clichet coborât pe 0 fără cauză cunoscută cade la prima regenerare fără să știm dacă e regresie sau normal.** Create de **`e8ab015` (13.08.2026)**, pasul 2 al normalizării corpusului: *„Text extras pentru fisierele noi fara .txt (.pdf pdftotext -layout; .html strip cu structura articolelor)."* **Cauza e acum demonstrabilă, nu presupusă**: corpusul are **9 fișiere `.xsd`**, iar cele opt goale erau **exact opt dintre ele** — extractorul a trecut XSD-urile prin ramura de HTML, iar un strip de etichete peste un XSD nu lasă nimic în urmă. Al nouălea, `d402_20160226.xsd`, a scăpat fiindcă fusese derivat separat, sub alt nume (`d402_20160226_xsd_linii.txt`). Deci nu opt accidente, ci **o singură ramură greșită aplicată de opt ori**.
- **CE LE POATE REGENERA**: scriptul din `e8ab015` **nu e în depozit** — a fost de unică folosință, deci nu regenerează singur. Dar **`scripts/portal_legislativ.py adu` scria `<nume>.txt` necondiționat**: `t = text(brut)` și scrie, oricare ar fi `t`, chiar dacă e gol — și tocmai unealta asta e cea despre care propriul ei docstring spune că *„pasul 1 din Partea 0 («nu-l am -> il aduc») se va repeta"*. Același mod de eșec, viu. **Reparat la sursă în aceeași tură** (`_scrie_text`): unealta **se oprește** dacă extragerea n-a produs text, cu numele fișierului în mesaj, și nu lasă în urmă nici `.txt`, nici `.txt.sha256` — deci golul se raportează **la unealtă**, nu la poartă două commituri mai târziu. Gardă: `core/test_portal_nu_scrie_gol.py`.

### R21 — Forma de înregistrare în contabilitate nu există nicăieri, iar de ea atârnă Cartea mare

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · faza 1 (setul complet) · triaj pragul 3, poziția 1
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `936aeb3`
- **deschisă pe commit**: `57c8189`
- **ce blochează**: obligația legală **nu cere un artefact, ci unul din trei**, iar care anume depinde de forma de înregistrare a entității. Verbatim, din corpus (`anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt`, poz. 165 și 166): *„Registrul Cartea mare poate fi înlocuit cu Fișa de cont pentru operațiuni diverse."* — aceeași frază la **14-1-3** („pe jurnale") și la **14-1-3/a** („maestru-șah"). Iar Anexa 1, pct. 51: formele sunt *„pe jurnale", „maestru-șah"* și combinata *„maestru-șah cu jurnale"*. **În aplicație forma nu există**: zero potriviri în `.py`, `.js`, `.sql` pentru vreuna dintre ele sau pentru un câmp echivalent. Deci nu se poate spune **ce datorează o firmă** — de aici felul ARTEFACT, nu SURSĂ: temeiul se citează complet, ce lipsește e latura firmei.
- **CÂMP SAU CONSECINȚĂ — răspunsul, măsurat pe schemă, nu presupus.** Întrebarea lui Costin (*„E un câmp pe firmă, sau o consecință a felului în care se fac notele? Dacă e câmp, e o zi. Dacă e consecință, e altceva."*) are răspuns **CONSECINȚĂ**, și consecința e deja determinată:

  - **Ce cere fiecare formă.** Anexa 1 pct. 52 („pe jurnale") listează printre registrele obligatorii **jurnalele auxiliare**, iar Cartea mare (14-1-3) se completează *din* ele. Pct. 53 („maestru-șah") **nu listează jurnale auxiliare**, iar Cartea mare (șah) *„se completează pe baza documentelor justificative, documentelor centralizatoare și a **notelor de contabilitate**"*.
  - **Ce are aplicația.** Notele trăiesc în `inregistrari` + `inregistrari_linii`, iar **fiecare linie poartă `cont_debit` și `cont_credit`** (`main.py:3799`) — perechea corespondentă e deja acolo, pe operațiune, exact forma de care are nevoie 14-1-3/a. **Jurnale auxiliare nu există**: evidența TVA n-are producător sub niciun nume de jurnal, iar `calcul_d300` agregă direct din `facturi`.
  - **Deci forma nu e liberă.** Aplicația poate produce azi **maestru-șah** și **nu poate** produce „pe jurnale" fără să construiască întâi jurnalele. Un câmp pe firmă ar fi o zi de lucru și **o minciună de o zi**: i-ar da contabilului o alegere pe care aplicația n-o poate onora. Forma e, azi, o **proprietate a aplicației** — de declarat scris, cu temei, nu de bifat per firmă. Devine câmp real abia când există jurnale auxiliare; atunci alegerea e adevărată.
  - **Și o ieșire care scurtcircuitează întrebarea, găsită la citirea normei:** fiindcă **Fișa de cont pentru operațiuni diverse înlocuiește Cartea mare în AMÂNDOUĂ formele**, construirea ei satisface obligația indiferent de formă. Atunci forma încetează să blocheze artefactul și rămâne doar o etichetă de declarat.
- **condiția de deblocare**: **una din două, prin decizie.** (a) Se **declară scris** forma pe care o produce aplicația — *maestru-șah* — cu temeiul (Anexa 1 pct. 53), se scrie unde o vede contabilul, și se construiește **Cartea mare (șah), cod 14-1-3/a** din `inregistrari_linii`; sau (b) se construiește **Fișa de cont pentru operațiuni diverse**, care înlocuiește Cartea mare în ambele forme, iar forma rămâne doar declarată. **Ce nu e acceptabil** e un câmp pe firmă care oferă „pe jurnale" cât timp jurnalele auxiliare nu există. Se închide când firma are un artefact pe care organul de control îl poate cere, nu când câmpul există.
- **ÎNCHISĂ 23.08.2026, în ziua în care s-a deschis — și asta se scrie, nu se ascunde.** Întrebarea lui Costin: *„Fișa de cont satisface obligația indiferent de formă. Ce mai rămâne blocat de R21? Dacă nimic, R21 e o restanță care s-a închis în ziua în care s-a deschis."* **Verificat, punct cu punct, în Anexa 1:** singura diferență între cele două forme, pe registre, e Cartea mare (14-1-3 vs 14-1-3/a) plus jurnalele auxiliare la „pe jurnale" (pct. 52 vs 53). Registrul-jurnal, Registrul-inventar și Balanța de verificare sunt **identice în ambele**. Iar Cartea mare, în **ambele** forme, se poate înlocui cu Fișa de cont. **Deci forma nu mai blochează niciun artefact** — rămâne o etichetă de declarat, nu o precondiție. Restanța se închide **fără să fi fost lucrată**: a fost deschisă înainte de a fi citită partea din normă care o stingea.
- **Ce s-a învățat, și de asta merită să rămână scrisă în loc să fie ștearsă:** precondiția era reală în momentul în care am scris-o și falsă două paragrafe mai încolo, în același act. **O restanță deschisă înainte de a fi citit actul până la capăt e o restanță pe care o citește altcineva ca pe muncă rămasă.** Ce a rămas cu adevărat blocat e altceva, măsurat la aceeași citire, și are restanță proprie: **R22**.

### R22 — Jurnalul de origine al unei înregistrări e o constantă, și pleacă așa la ANAF

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · faza 1 · D406 (SAF-T) · criteriile minimale de program
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `46adff1`
- **deschisă pe commit**: `936aeb3`
- **ce blochează**: OMFP 2634/2015, Anexa 1, **pct. 58 lit. i)** cere ca programul să asigure, printre elementele constitutive ale **fiecărei** înregistrări contabile, *„jurnalul de origine în care se regăsesc înregistrările contabile"* — citit verbatim din corpus. Cerința e **independentă de forma de înregistrare**, deci nu dispare odată cu R21. Măsurat: `core/d406.py:832` scrie `<JournalID>GENERAL</JournalID>` **literal**, aceeași valoare pentru orice înregistrare, în declarația care pleacă la ANAF. Elementul **există** ca etichetă și **nu poartă nicio informație**: nu se poate răspunde la *„din ce jurnal provine rândul ăsta"*, care e chiar întrebarea pentru care norma cere câmpul. **Și datele pentru un răspuns real există deja**: coloana `inregistrari.sursa` poartă azi valori care sunt exact jurnale de origine — `casa` (`core/sgr.py:36`, `core/ong.py:27`, `core/contracte_speciale.py:90`), `salarii` (`core/control_incrucisat.py:485`), `migrare` și `iconta` (`core/istoric_declaratii_import_api.py`). Deci nu lipsește informația, lipsește legătura dintre ea și SAF-T.
- **condiția de deblocare**: o **decizie**, fiindcă nu e determinată de text — (a) `JournalID` se derivă din `inregistrari.sursa`, cu o mapare scrisă și un temei pentru fiecare valoare, și atunci elementul devine informativ; sau (b) se **declară scris** că firma ține un singur jurnal general, cu temeiul care permite asta, și atunci constanta e adevărată, nu o umplutură. **Ce nu e acceptabil e starea de azi**: un câmp cerut de normă, completat cu o constantă, fără ca undeva să scrie că firma chiar ține un singur jurnal. Se închide când `JournalID` ori poartă originea, ori are în spate o declarație scrisă că e unic.
- **RECLASIFICATĂ ȘI REPARATĂ 23.08.2026 — nu era restanță, era PRAG 1.** Costin: *„E un element din declarație care pleacă la ANAF purtând o valoare inventată — nu o absență, o afirmație falsă. […] Nu e «efect greșit la un om», e efect greșit la autoritate, ceea ce e treapta de deasupra."* Am deschis-o ca restanță fiindcă am citit-o ca lipsă de legătură; e o **afirmație falsă emisă**, deci intră în pragul 1 și trece înaintea a tot ce e în triaj. Aleasă **varianta (a)**.
- **CE ACCEPTĂ SCHEMA, verificat la sursă** (`anaf_surse/d406_schema_anaf.xlsx`, foaia *3. GeneralLedgerEntries*): **GL.4 `Journal` are cardinalitate `0..*`** — mai multe jurnale sunt permise · **GL.5 `JournalID` e `SAFshorttextType` = `xs:string`, `maxLength = 18`** — deci **NU e nomenclator închis**, e text liber · GL.7 `Type` e `SAFcodeType`, max 9. **Sursa se mapează totuși**, dar nu fiindcă ar cere-o schema: `inregistrari.sursa` poartă **nume interne** (un nume intern într-un document citit de autoritate = interdicția 13), iar `migrare` și `iconta`, care există în coloană, **nu sunt jurnale** — sunt proveniența unui import.
- **CÂTE D406 DEPUSE POARTĂ `GENERAL`: zero, și motivul contează.** `public.declaratii_depuse` are **17 rânduri D406**, toate cu `sursa='migrare'` și **`xml` gol** — sunt depuneri de istoric importate, nu declarații generate de aplicație. Deci constanta **nu a plecat încă la ANAF prin aplicație**; defectul era pe calea de generare, viu pentru orice D406 generat de azi înainte. *Se scrie explicit, fiindcă „zero depuse afectate" și „defectul nu exista" sunt două lucruri diferite.*
- **REPARAȚIA**: `core/d406.py` — nomenclator `_JURNALE` (casa · banca · facturi · salarii · amortizare), cu felurile de jurnal auxiliar **numite de normă** (Anexa 1 pct. 45); `pull` citește `i.sursa`; `_gl_entries` emite **un `<Journal>` per jurnal de origine**, cu sortare **stabilă** (ordinea notelor în interiorul unui jurnal rămâne cea din `ORDER BY i.id`). O notă fără sursă intră în **`DIVERSE`** — Nota de contabilitate, cod 14-6-2/A, Anexa 1 pct. 52 — iar o sursă **nemapată** nu devine `DIVERSE` în tăcere: se numește în avertisment, cu nota și valoarea (tiparul `[B17]` de la UM necunoscute).
- **PROBAT PE DATE REALE ȘI LA ARBITRU**: `tenant_013`, 2026-08, 13 note din 4 surse → **`AMORTIZARE`, `BANCA`, `CASA`, `DIVERSE`**, zero `GENERAL`. Trecut prin **validatorul oficial ANAF** (DUKIntegrator, D406, reguli 2026.1): **`stare = valid`, zero erori** — deci structura cu mai multe jurnale nu e o presupunere.
- **CORECTARE 23.08, la întrebarea lui Costin: denumirile NU erau decizie de produs pe de-a-ntregul.** Le pusesem pe toate cinci ca alegere a noastră. **Anexa 1 pct. 45 și 52 numesc felurile** de jurnal auxiliar — deci partea aceea e **nomenclator oficial**, iar scrierea lui ca literal e chiar **interdicția 28**. Refăcut: `_FELURI` poartă textele **verbatim** din pct. 52 (*„operațiuni de casă și bancă" · „operațiuni privind decontările cu furnizorii" · „situația încasării-achitării facturilor" · „operațiuni privind salariile și contribuția pentru asigurări sociale, protecția socială a șomerilor și asigurările de sănătate" · „alte operațiuni"*), cu `TEMEI_JURNALE` (`Temei` structurat, `nivel_sursa=MO`) lângă ele; `<Description>` ia felul din nomenclator, iar `JournalID` rămâne al nostru (text liber în schemă). **Gardat mecanic**: un test caută fiecare fel **literal în corpus** — o reformulare, oricât de nevinovată, îl face roșu.
- **Cele două abateri de la lista normei, declarate ca fiind ale noastre:** (1) `CASA` și `BANCA` sunt **două identificatoare pentru un singur fel** — norma le grupează („operațiuni de casă și bancă"), aplicația le ține în registre distincte, iar lista fiind *ilustrativă* („cum sunt"), un jurnal mai fin e mai informativ, nu mai puțin conform; (2) `AMORTIZARE` **nu e un fel numit de normă** — intră la „alte operațiuni". Iar `furnizori` stă în nomenclator **fără mapare**: niciun `inregistrari.sursa` nu-l produce azi. Nomenclatorul e complet, maparea e parțială, și diferența se vede.
- **GARDĂ**: `core/test_d406_jurnal_origine.py`, **18 teste**, RED-probat cu **2 mutații / 2 roșii** (constanta se întoarce → 3 teste roșii; `pull` nu mai trece sursa prin mapare → testul anti-vacuu roșu). Include limitele schemei (18/256/9) și anti-vacuu pe cablare, citit din sursa lui `pull`/`genereaza`.

### R23 — Urme de intenție: nume declarate pe care nu le citește nimeni

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · faza 4 (instrumentele) · vecin cu interdicția 16 (proza care descrie codul poate fi falsă)
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `f189b81`
- **ce blochează**: întrebarea lui Costin, 23.08.2026: *„un import mort nu e defect, dar e semnal — la fel ca `jurnal: str = «GENERAL»`, care a stat trei săptămâni ca urmă a unei intenții. Merită verificat ce mai era început acolo."* **Scanat, AST, pe cele nouă module de declarație** — nume declarate la nivel de modul sau de `dataclass` pe care nimic din modul nu le citește: `d205` — `Beneficiar.categ`, `Beneficiar.castig1`, `Beneficiar.pierdere1` · `d300` — `REGULI`, `_LIVRARE_RAND`, `_ACHIZ_RAND` · `d301`, `d390` — `REGULI` · `d406` — `REGULI`, `MISCARI_STOC`, `MOVEMENT_IMPLICIT`, `TAB_VALORI`, `Partener.adresa`, `Factura.partener_nume`. **Separat, importuri nefolosite (ruff F401) în `core/` + `main.py`: 90.**

  **Ce NU spune scanul, și de asta e restanță, nu constatare.** Scanul e **pe nume**, deci moștenește exact limitele clasei pe care o urmărim: (a) nu vede citirile prin `getattr(obj, "nume")` — chiar `Nota.jurnal` apare „mort" în el, deși e citit de la reparația R22 încoace; (b) nu vede citirile **din alt modul** (`REGULI` e o convenție de marcaj, citită în `facturi.py` prin `MODUL`/`REGULI`, deci probabil legitimă peste tot). **Deci lista de mai sus e o listă de CANDIDAȚI, nu de defecte** — iar a o trata ca listă de defecte ar fi a treia instanță a aceleiași greșeli într-o zi.
- **condiția de deblocare**: fiecare candidat verificat **individual**, la sursă, cu întrebarea *„a fost început ceva aici și s-a oprit, sau e o convenție citită din altă parte?"*, iar rezultatul scris pe două coloane — **convenție** (rămâne, cu motivul) sau **urmă de intenție** (se duce la capăt sau se scoate). Pentru cele 90 de importuri: fie clichet per fișier pe `F401` în poartă (tiparul deja folosit la mesajele cu nume interne), fie o decizie că nu merită. Se închide când niciun nume din cele nouă module nu e „declarat și necitit" fără o explicație scrisă lângă el. *Precedentul care justifică restanța: `jurnal: str = "GENERAL"` a stat de la prima zi a modulului ca urmă a unei intenții, iar reparația de prag 1 din R22 a aterizat exact acolo.*

### R24 — Trei cicluri în graful de clustere: reciproce în fapt, sau doar în graf?

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · faza 4 (instrumentele) · vecin cu R18 (secvența care nu poate deveni roșie)
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `25b07c0`
- **ce blochează**: după repararea proprietății (R19), ciclurile din graful de clustere au scăzut de la **321 la 3**, toate în familia salarizării: *facilitate salariu minim* ↔ *deducere personală* ↔ *concedii medicale*. Le-am numit *„par dependențe reciproce reale"* și nu le-am atins. **Observația lui Costin, care schimbă întrebarea:** o dependență reciprocă **reală** înseamnă că **nu există ordine de verificare între ele** — iar atunci **sortarea topologică nu le acoperă**, oricât de curat ar fi graful. Secvența ar trece peste ele într-o ordine arbitrară, fără să spună că e arbitrară.
- **condiția de deblocare**: se stabilește dacă cele trei sunt reciproce **în fapt** sau doar **în graf**. *În graf* ar însemna că muchia dintr-o direcție vine dintr-un utilitar comun rămas cu proprietar unic din întâmplare — atunci se repară proprietatea și ciclul dispare. *În fapt* ar însemna că valorile chiar se determină reciproc (deducerea depinde de baza pe care o schimbă facilitatea, și invers) — atunci **ciclul nu e un defect al grafului, ci o proprietate a legii**, și trebuie **declarat**: cele trei se verifică împreună, ca un singur nod, nu una după alta. Se închide când fiecare dintre cele trei cicluri poartă un verdict scris — *reparat* sau *declarat* — nu când numărul ajunge la zero.

### R25 — Module fiscale care NU citează legea, deci rămân în afara domeniului scanului

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E3 · faza 4 · interdicția 1 (valori fiscale în afara registrului)
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `2bf9204`
- **deschisă pe commit**: `25b07c0`
- **ce blochează**: criteriul nou de domeniu — *„nume fiscal SAU modulul construiește un `Temei`"* — prinde modulele care **știu** că sunt fiscale. Nu le prinde pe cele care **ar trebui să știe**. Măsurat 23.08.2026, pe cele 210 module din afara lui `FIS`: **50 au semnal fiscal** (construiesc `Temei` sau au ≥20 de potriviri cu vocabularul fiscal), din care 4 au intrat prin criteriul nou. Sondat pe **10** dintre cele rămase — `casa.py` (6 de clasă C), `notificari_scadenta.py` (2), `control_incrucisat.py` (1), `beneficii_api.py` (1), `stat_plata_emis.py` (1), `facturi_api.py` (1), iar `expirare_cote.py`, `salariu_istoric.py`, `plan_omfp.py`, `declaratii_api.py` cu **0** — **12 constante de clasă C nevăzute**. Cifra e un **plafon inferior**: s-au sondat 10 din 46.
- **condiția de deblocare**: o **decizie**, fiindcă lărgirea are un cost simetric — un domeniu prea larg aduce zgomot operațional în clasa C (măsurat deja o dată: cele 14 constante din `main.py`, toate de infrastructură), iar unul prea îngust lasă datorie invizibilă. Variantele: (a) se adaugă în `FIS` modulele sondate care au clasă C nenulă, cu clichetul lor măsurat; (b) se rulează sonda pe toate cele 46 și se decide pe cifra completă; (c) se declară scris că domeniul rămâne la *„module care citează legea"*, cu motivul. Se închide când domeniul e ales **pe o cifră completă**, nu pe un eșantion de 10.
- **SONDAJUL COMPLET, 23.08.2026 — și decizia luată pe compoziție, nu pe teamă.** Toate cele **46** de module rămase: **48 de constante de clasă C**, în **21** dintre ele. Extrapolarea de la eșantionul de 10 ar fi dat ~55 — aproape, dar **distribuția e ce contează**, și ea nu se extrapolează. Clasificate una câte una:

  | fel | câte | ce sunt |
  |---|---|---|
  | **FISCALE reale** | **17** | plafoanele de casă (6, Legea 70/2015 — într-un modul al cărui comentariu scrie *„cu temei"* și nu poartă niciunul) · **cota 21 ca DEFAULT DE PARAMETRU** în șase module (`import_export`, `lichidare`, `perisabilitati`, `stocuri`, `taxare_inversa`, `produse_api`) · plafonul de 10% și cota de 16% din `ong.py` · pragul de **270 de zile** de la art. 26(1)c · impozitul pe dobândă de 10% · norma de 8 ore/zi |
  | **ALGORITM** | **20** | vectorul de ponderi al checksum-ului CNP (`_CHEIE`, de două ori câte nouă) și decodarea secolului din CNP |
  | **OPERAȚIONALE** | **11** | praguri de zile pentru notificări, orizont de scadențar, paginare, lățimea unui logo în PDF |

  **Cele 20 de algoritm au ieșit corect, nu prin excepție**: `CHEIE` a fost adăugat în `NOM`, unde îi era locul — e aceeași clasă cu `_CNP_W`. Rămân **30**, din care **17 fiscale: peste jumătate**. Zgomotul operațional **nu se aruncă** — intră în clichet pe fișierul lui, deci e vizibil și nu poate crește.
- **DECIS: domeniul se lărgește.** A treia regulă în `scan_constante.in_domeniu`: *nume fiscal* **SAU** *citează legea* **SAU** *densitate de vocabular fiscal peste `PRAG_SEMNAL`*. **Clasa C: 104 → 135**; module văzute **60 → 85**. Datoria n-a crescut — a devenit vizibilă a doua oară în aceeași zi. Clichetul s-a lărgit cu fiecare fișier la valoarea lui măsurată.

### R26 — Cota de TVA scrisă ca valoare implicită în 25 de funcții, iar 23 de apeluri o folosesc

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E3 · interdicțiile 1 și 14 · **PRAG 3** *(ridicat greșit la prag 1 pe 23.08 și coborât în aceeași zi — vezi «CORECTARE» mai jos)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `c22a0c5`
- **ce blochează**: întrebarea lui Costin — *„zece module au aceeași cotă scrisă de zece ori ca valoare implicită. Când s-a schimbat de la 19 la 21, câte au fost actualizate, și de unde știm?"* — a scos o clasă mai mare decât cifra care a produs-o. **Măsurat, AST, pe tot `core/` + `main.py`: 25 de funcții au `cota = 21` ca default de parametru** (nu 10 — cifra de 10 era pe clasa C a scanului, deci pe modulele nesursate), iar **23 de apeluri de PRODUCȚIE lasă defaultul să lucreze** — **22 din ele în `main.py`**, adică în rute.

  **Răspunsul la întrebarea pusă e „niciunul, și asta nu e o veste bună":** niciunul dintre module n-a purtat vreodată `19` — toate au primit `21` pe **04.07.2026**, în commituri separate, iar depozitul începe pe 01.07.2026, **după** schimbarea cotei. Deci migrarea 19→21 **nu a avut loc aici**, iar mecanismul de propagare **n-a fost pus niciodată la încercare**. Nu știm că ar funcționa; știm doar că n-a fost nevoie.

  **Și nu e un risc de la următoarea schimbare — e o cifră greșită AZI.** Un default fix ignoră **data operațiunii**: o notă generată pentru o operațiune dinainte de **01.08.2025** prin oricare dintre cele 23 de căi primește **21%** în loc de **19%**. Registrul știe amândouă valorile, cu date și cu temei — `COTE["tva_standard"]` are `(2025-08-01, 0.21, Legea 141/2025)` și `(2017-01-01, 0.19, Legea 227/2015)`, iar `common.cota(nume, la_data)` întoarce valoarea validă la o dată. **Cele 23 de apeluri nu-l întreabă.**
- **condiția de deblocare**: o **decizie de formă**, fiindcă reparația mecanică are două variante cu costuri diferite. **(a)** Defaultul devine `None`, iar funcția rezolvă din registru pe **data operațiunii** — corect, dar cere ca data să ajungă până acolo pe toate cele 23 de căi, iar azi nu ajunge peste tot. **(b)** Defaultul rămâne, dar se ia din `common.cota("tva_standard")` **la momentul apelului** — ieftin, elimină literalul, **dar nu rezolvă retroactivitatea**: o notă pe 2024 tot ar primi cota de azi. Se închide când cele 25 nu mai poartă literalul **și** se scrie care dintre cele două s-a ales, cu ce rămâne neacoperit. *Nu se începe fără decizie: (b) făcut tăcut ar arăta ca o reparație completă și n-ar fi.*
- **RIDICATĂ LA PRAG 1, 23.08.2026, prin CONSECVENȚĂ — nu prin apariția unui caz nou.** Criteriul lui Costin, aplicat la o clasă vecină: *„dacă vreo cale ajunge la default, produc o cifră greșită, ceea ce le-ar pune la pragul 1."* Verificat: **23 de căi ajung**, iar rutele din `main.py` primesc **data operațiunii din corpul cererii** — deci o operațiune datată înainte de **01.08.2025** produce **21%** în loc de **19%**, la cerere, azi. **Nu e un risc viitor: e o cifră greșită disponibilă acum.** Ridicarea nu e o judecată nouă, e aceeași cu **R22**: acolo `JournalID = GENERAL` a fost declarat prag 1 deși **zero** depuneri erau afectate, fiindcă **calea de generare era vie**. Aici e identic — a lăsa R26 la prag 2 ar fi însemnat două praguri pentru același fel de defect.
- **CORECTARE 23.08.2026, în aceeași zi: ridicarea la prag 1 a fost A MEA și era GREȘITĂ. Măsurătoarea pe care stătea număra doar argumentele NUMITE.** Am întrebat, prin AST, dacă apelanții dau parametrul `cota` **ca `keyword`** — și am citit „nu" ca „lasă defaultul să lucreze". **Dar 22 din cele 23 de apeluri îl dau POZIȚIONAL**, din `_common.cota_ceruta(corp)`, care refuză deja o cerere fără cotă. Re-măsurat corect (legare pozițională **și** prin nume): **un singur apel** nu dă parametrul — `stocuri_api.py:60` → `nir_gv` — iar **și acela e mort**: apelantul refuză orice linie de NIR fără `cota_tva` explicită, iar `cota_tva_implicita` e doar o rezervă per linie.
- **Deci ZERO căi vii ajung la vreunul dintre cele 25 de defaults.** Nu e prag 1: nicio cifră greșită nu se poate produce azi pe niciun drum. Nu e nici prag 2, fiindcă nu există instanță. **E prag 3** — o clasă **latentă**: 25 de literali umbriți azi de valori explicite, care ar furniza tăcut o cotă greșită la primul apelant care omite valoarea.
- **REPARATĂ TOTUȘI, în aceeași tură, cu argumentul lui Costin:** *„un default cu valoare, oricare ar fi, e aceeași clasă peste șase luni."* Cele **25 de literale au fost scoase** — parametrul devine `None`, iar funcția **refuză** cu un mesaj care spune de ce nu se ghicește (*o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi*). Alegerea de a **refuza**, nu de a rezolva din registru pe dată, urmează o decizie **deja scrisă în același modul**: `common.cota_ceruta` spune, din iulie, că *„NU se ghiceste o cota implicita, nici macar cota standard (un default cu common.cota() ar fi tot o valoare inventata, doar actualizata)"*. Cele 25 de funcții contraziceau o regulă a casei, nu doar buna practică.
- **Ce a scos reparația, și e o măsurătoare, nu o impresie: 11 teste picau pe default** — adică **îl testau**. `test_stocuri` (9), `test_versionare_formule` (2), `test_operatiuni_speciale` (1). Toate au fost făcute să **declare** cota. Un test care se sprijină pe o valoare implicită nu verifică regula, verifică defaultul.
- **Clichetul s-a coborât singur**: `test_baseline_nu_e_stat` a picat imediat după reparație, fiindcă datoria devenise mai mică decât pragul. **C: 162 → 134.**
- **A DOUA RUNDĂ, 23.08 — și aici e singura instanță VIE din toată clasa.** Întrebarea lui Costin — *„reparația a fost verificată cum? Testele acoperă căile, sau doar confirmă că defaultul a dispărut din semnătură?"* — avea răspunsul **a doua**: cele 15 fișiere actualizate **dau** cota, deci verificau doar calculul **cu** ea. Am construit garda care lipsea (`core/test_cota_fara_default.py`, exercită **refuzul** pe fiecare funcție care îl poartă), **iar ea a găsit un al 26-lea caz în prima rulare**: `deconturi.nota_decont(cota_tva=0)`.
- **`0` e o cotă VALIDĂ (scutit), deci un default de 0 e aceeași clasă — și mai periculos decât 21.** Propria mea listă de excluderi îl ascundea: la măsurarea defaults-urilor am scos `0, 1, -1, 2, 100` ca „structurale". **Iar ăsta e VIU**: ruta punea `corp.get("cota", 0)` și **nu** chema `cota_ceruta`, deci un decont cu cazare pe factură, trimis fără cotă, primea tăcut **0%** → **zero TVA deductibilă**. Reparat: funcția refuză, ruta cere cota ca celelalte 14. *Un default de 0 nu adaugă o cifră greșită — o șterge pe cea corectă, ceea ce e mai greu de văzut.*

### R27 — Pragul de reverificare din cod e încă cel global, deși tabelul lui 55 l-a înlocuit azi

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E2 · interdicțiile 54, 55
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `bde0502`
- **ce blochează**: `common.cote_neconfirmate(luni=6)` aplică un **prag global unic de 6 luni** tuturor valorilor — exact ce interdicția 55 numea drept defect, și exact ce **decizia de azi a înlocuit** cu un tabel de nouă căsuțe (`VOLATIL/MIȘCĂTOR/STABIL` × `DEPUS/CALCULAT/INFORMATIV`, de la 1 la 18 luni). Găsit la triajul celor 35 de defaults cu valoare, cerut de Costin: *„valoarea de acum e cea în vigoare, sau e una veche care a supraviețuit?"* — aici nu e nici una, nici alta: e o valoare pe care **propria noastră decizie a depășit-o acum câteva ore**. Raportul intern de cote neconfirmate spune deci, azi, altceva decât regula scrisă în registru.
- **condiția de deblocare**: `cote_neconfirmate` citește pragul din **categoria valorii** (clasa A × clasa B din 55), nu dintr-un parametru global. Precondiție: categoriile trebuie **atribuite** valorilor — ceea ce interdicția 55 declară nemăsurat („câte articole cad în fiecare căsuță"). **Deci se închide după 55, nu înaintea ei** — dar se scrie acum, ca decizia de azi să nu rămână o regulă fără aplicare.

### R28 — Ce trebuie să arate ecranul de angajare, dacă arată ceva

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E5 · triaj · **PRAG 3** *(structură — nicio cifră greșită azi)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `fa3330c`
- **deschisă pe commit**: `e325f7c`
- **ce blochează**: Costin a cerut *scoaterea* unei cifre afișate sub eticheta „Impozit estimat", cu motivul că **nu e impozit și nu e nimic numibil**. **Cifra aceea nu există.** Verificat pe tot depozitul: `impozit estimat` are **zero** potriviri în `static/` — singura apariție e `core/ong.py:52`, în **Python**, unde cheia `impozit_estimat` întoarce impozitul pe profit al excedentului economic al unui ONG (art. 15 alin. 3 CF). **Nu se afișează nicăieri** — vezi mai jos de ce. Ce **există** pe ecranul de salariu (`firme.js:1042`) e altceva: **„Net estimat: … lei"**.
- **INTENȚIA, GĂSITĂ SCRISĂ — răspuns la întrebarea pusă.** Există comentariu, și e explicit, la trei rânduri deasupra (`firme.js:1026–1028`): *„consecința ÎNAINTE de buton (DS cap. 6): la un leu peste salariul minim se stinge facilitatea și netul SCADE. Calculul vine de la server (`salarizare.calcul_salariu`) — nicio regulă fiscală nu se rescrie aici."* Deci: **(a)** cifra e a serverului, nu a ecranului — nicio formulă în JS; **(b)** scopul nu e o estimare, e **o consecință arătată înainte de apăsarea butonului**, cu temei de design citat; **(c)** varianta implementată e, dintre cele trei propuse, exact **„netul salariatului"** — aleasă, nu nimerită.
- **condiția de deblocare**: **Decizie cerută [atunci].** Rămâne deschisă fiindcă întrebarea e **bună chiar dacă premisa n-a fost**: azi ecranul arată netul (varianta 2), iar **costul total lunar pentru angajator** — ce interesează efectiv la angajare — **nu apare nicăieri**. Variantele: **(a)** rămâne netul singur, cu motivul scris; **(b)** se adaugă costul total al angajatorului lângă net, ca a doua consecință; **(c)** se înlocuiește netul cu costul total. Se închide când e scris **care** și **de ce**. *Nu se începe fără decizie: oricare dintre ele ar alege singură ce înseamnă ecranul — exact ce a cerut Costin să nu fac.*
- **ȘI O CIFRĂ CARE CHIAR NU AJUNGE LA NIMENI, găsită pe drum.** `impozit_estimat` din `core/ong.py` **nu poate fi produsă din aplicație**: ecranul de operațiuni (`operatiuni_ecran.js:264`) oferă opțiunea *„Calcul scutire art. 15 CF"*, dar **formularul nu declară niciunul** dintre cele trei câmpuri de care are nevoie (`venituri_economice`, `venituri_neimpozabile`, `curs_eur`) — toate câmpurile condiționate sunt pe ramura *„Venit AFSP"*. Cererea pleacă fără ele, `main.py:9078` face `corp["venituri_economice"]`, iar `KeyError` e prins și întors ca **422 cu textul `venituri_economice`** — adică un **nume de câmp intern** afișat unui contabil, pe o opțiune care **nu poate reuși niciodată**. Prag 2, clasă de mesaj — consemnat aici fiindcă a ieșit din aceeași verificare, **nu reparat în tura asta**.
- **DECIS 24.08.2026 de Costin — VARIANTA 3: NIMIC.** *«La angajare, brutul e ce se negociază și ce se scrie în contract. Costul angajatorului și netul se calculează după salvare, cu toate elementele — persoane în întreținere, tip de contract, CAEN. O estimare care nu le are e o cifră care contrazice fluturașul de peste o lună. Iar ecranul de angajare nu e locul unei simulări: cine vrea să compare scenarii deschide simulatorul.»*
- **PREMISA DECIZIEI, VERIFICATĂ ÎNAINTE DE EXECUȚIE — și e adevărată mai tare decât a fost enunțată.** Ruta chema `calcul_salariu(brut, la_data=...)`. Funcția are **18 parametri**; ruta pasa **doi**. Restul luau valorile implicite: `persoane=0`, `sub_26=False`, `copii_scoala=0`, `norma_intreaga=True`, `data_angajare=None`. Deci cifra afișată **nu putea** coincide cu fluturașul pentru un salariat cu persoane în întreținere, sub 26 de ani, cu normă parțială sau angajat la mijloc de lună. Și mai exact: `salariat_id` **se trimitea**, dar era folosit **doar ca referent al afirmației** (`_Unde("salariat", id)`), nu în calcul — ecranul spunea *«despre salariatul ăsta»* calculând ca și cum salariatul n-ar avea pe nimeni în întreținere.
- **EXECUTAT:** blocul de estimare scos din `firme.js`, iar ruta `/salariu-efect` **ștearsă din `main.py`** (3.604 caractere) — nimeni altcineva n-o chema, deci ar fi rămas cod mort. Motivul măsurat e scris în locul ei, în comentariu, ca următorul care trece pe-acolo să nu o rescrie.
- **Ce NU s-a rezolvat cu asta:** *«costul total lunar pentru angajator»* — care a fost motivul pentru care restanța a rămas deschisă ieri — **tot nu apare nicăieri**. Varianta 3 spune că **nu pe ecranul de angajare** e locul lui, nu că nu e nevoie de el nicăieri. Iar simulatorul la care trimite decizia (*«cine vrea să compare scenarii deschide simulatorul»*) **nu există**: căutat, zero potriviri pentru *simulator* sau *simulare* în `static/js/` și în `main.py`. Nu e o obiecție la decizie — e ce lipsește ca ea să fie completă.
### R29 — Cota de TVA ca valoare implicită în ECRAN, care anulează refuzul învățat de server

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · interdicțiile 1 și 14 · **PRAG 1** *(o cifră implicită ajunge în date salvate)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `2636004`
- **deschisă pe commit**: `e325f7c`
- **cum s-a închis, 24.08.2026**: cele două valori implicite au fost scoase, iar refuzul serverului se poate declanșa. `firme.js` — linia nouă de NIR pornește **fără cotă** (`cota_tva: ""`), selectorul are o opțiune goală *„alege"* selectată când linia n-are cotă (ce se **vede** e ce se **trimite**), iar corpul cererii trimite `null` în loc de `21`. **Măsurătoarea a lărgit clasa:** aceeași formă trăia și în **Python**, pe o cale vie — `core/produse_api.py:25`, `else 21.0`, prin `main.py:2513`: orice produs cu cota NULL era **prezentat ca 21%**. Deci R26 nu greșise doar domeniul de limbaj, ci și **forma**: măsurase defaultul din SEMNĂTURĂ, nu pe cel de la CITIRE. Reparat și acolo, cu o cuplare obligatorie — `badgeCota` din `produse_ecran.js` făcea `Number(null) === 0` și ar fi afișat o cotă lipsă drept **„fără TVA"**, adică 0%; acum arată *„cotă lipsă"*, pe griul de stare din `DS` cap. 8, cu contrast AA.
- **gardul cerut de condiție, construit**: `core/test_cota_fara_default_fallback.py`, cu `static/js/` în domeniu. Acoperă **cele trei forme** ale clasei — fallback la citire (`or`/`||`/`else`) și literal în inițializare (`{cota_tva: 21}`) — complementar lui `test_cota_fara_default.py`, care acoperă doar defaultul din semnătură, doar în `core/*.py`. **Forma a treia a fost adăugată după ce RED-proof-ul a arătat că lipsea**: mutația care repunea `cota_tva: 21` pe linia nouă lăsa gardul verde. RED-probat pe 4 mutații, inclusiv una într-un fișier nescanat până atunci. Două calibrări negative, ambele cu instanță reală în cod: defaultul pe **zero** (18 instanțe legitime) și `cota` fără sufix — care e **flagul micro** cerut de validatorul DUK (`cota=1`), nu o cotă de TVA.
- **ce blochează**: **R26 a scos 25 de valori implicite de cotă din Python și a declarat clasa golită. Aceeași valoare implicită trăiește în JavaScript, și ea e cea care rulează.** Ecranul de NIR o scrie de **trei ori**: `firme.js:1649` — o linie nouă pornește cu `cota_tva: 21`; `firme.js:1660` — lista de opțiuni e `[21, 11]`, scrisă literal, iar selecția implicită e `(l.cota_tva || 21)`; `firme.js:1738` — **în corpul trimis la server**: `cota_tva: l.cota_tva || 21`.
- **de ce e prag 1, și nu latență.** `main.py:798` poartă comentariul deliberat *„None → potrivire automată / eroare la lipsă (**fără valoare implicită**)"*, iar R26 a încheiat cu constatarea că *„apelantul refuză orice linie de NIR fără `cota_tva` explicită"*. **Refuzul acela nu se poate declanșa niciodată din ecranul de NIR**, fiindcă ecranul completează valoarea **înainte** ca serverul s-o vadă. Serverul a fost învățat să întrebe; clientul răspunde în locul contabilului. Cifra ajunge în **date salvate** (cota pe linia de NIR → TVA neexigibilă, adaos, valoarea stocului), nu doar pe un ecran.
- **și de ce măsurătoarea lui R26 era corectă și totuși incompletă**: a fost făcută prin **AST pe Python**. Domeniul a fost `core/` + `main.py`. Nu era greșită înăuntrul lui — era prea îngustă, iar concluzia *„zero căi vii ajung la vreun default"* a fost **adevărată despre Python și falsă despre aplicație**. Aceeași formă cu gardul `DEFAULT_FISCAL_TACIT`, care are și el domeniu Python: **un gard cu domeniul pe un singur limbaj raportează verde despre limbajul pe care nu-l vede.**
- **condiția de deblocare**: cele trei literale scoase din ecran **și** un gard care are `static/js/` în domeniu — altfel a patra apariție intră mâine fără să se vadă. Lista `[21, 11]` cere o decizie separată de formă (cotele vin de la server, sau ecranul rămâne cu o listă care trebuie ținută la zi cu mâna), fiindcă azi **ambele valori sunt corecte** — 21% standard și 11% redusă, Legea 141/2025 — deci nu e o cifră greșită, e o listă care **va** îmbătrâni. Se închide când ecranul nu mai poartă niciun literal de cotă și gardul îl poate proba.

- **INVENTARUL COTELOR LITERALE DIN `static/js/`, măsurat 24.08.2026 pe commit `27ea876`** — cerut ca *„verifică-le valorile, nu doar prezența"*. Confruntarea e mecanică, în `core/test_valori_fiscale_js.py` (13 teste), nu o afirmație a mea: **10 situri, toate cu valoarea în vigoare azi. ZERO valori expirate.**
- **Patru dintre cele zece NU erau confruntate până azi**, iar unde erau găurile spune ceva despre forma gardului: `firme.js` *„Total 21% (alcool, sucuri)"* — **fratele de pe linia următoare** a unui rând care era deja în tabel (*„Total 11% (mâncare)"*); `produse_ecran.js:101-102` — `<option value="21">21%` și `<option value="11">11%`, **aceeași formă cu lista `[21, 11]`** din R29, într-un alt ecran; `facturi_ecran.js:883` — *„TVA 21%"* cu **315,00 pe o bază de 1.500,00** în previzualizarea de factură, deci o schimbare de cotă ar lăsa acolo o pereche aritmetică falsă. **Un tabel scris de om are găuri exact lângă rândurile pe care le conține** — de aceea limita declarată a gardului (*„nu descoperă singur valori fiscale noi în JS"*) e cea care contează, nu numărul de rânduri. Toate patru RED-probate prin mutație pe ecran.
- **DAR o valoare fiscală în AFARA registrului, cu cale vie — găsită în aceeași măsurătoare.** `migrare.js:455`, textul de ajutor de la periodicitatea decontului de TVA: *„Trimestrial doar dacă în anul precedent cifra de afaceri a fost sub **100.000 euro** (curs BNR 31.12) … art. 322 alin. 2."* Cheia **nu există în `COTE`** — sunt `plafon_tva_incasare`, `plafon_mijloc_fix`, `plafon_sold_casa`, `plafon_avans_decontare`, `impozit_micro`, `plafon_facilitate_salariu_minim`, `tichet_masa_plafon`, niciuna pentru art. 322. Deci **nimic nu o poate confrunta**, iar gardul de mai sus n-o vede prin construcție: n-are cheie de registru cu care s-o compare. **Interdicția 1**, într-un ecran de configurare a vectorului fiscal.
- **Vigoarea ei NU s-a putut verifica, și motivul se scrie lângă ea:** `scripts/vigoare_articol.py` cere identificatorul de portal al actului, iar **Codul fiscal n-are unul înregistrat în corpus** (cele patru identificatori din registre sunt OPANAF-uri). Fără el, *„100.000 e încă valoarea din art. 322 alin. 2"* rămâne **o citire, nu o măsurătoare**. De aceea **nu s-a urcat la prag 1**: autorizarea de a urca fără să mai întreb era condiționată de o valoare **dovedită** expirată, iar aici dovada lipsește. A o urca oricum ar fi fost exact ce interzice regula — o cifră fără termenii ei.
- **`rip_ecran.js:143` nu e o valoare expirată**, deși arată ca una: *„venituri 2025 (sm 4.050 lei)"* — 4.050 e corect pentru anul **numit în etichetă**, iar registrul dă azi 4.325 (HG 146/2026). Ecranul nu minte despre 2025; nu poate ajunge la 2026. Aia e **R31**.
- **ce rămâne din inventar:** cheia art. 322 alin. 2 intră în registru **sau** textul de ajutor pierde cifra (o regulă citată fără cifră nu îmbătrânește); și identificatorul de portal al Codului fiscal se aduce în corpus, ca vigoarea articolelor lui să devină mecanică — azi nu e.

### R30 — Avertismentul de prăpastie al salariului minim, plecat odată cu estimarea

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E5 · triaj · **PRAG 2** *(o protecție care exista nu mai există)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `9b3bf41`
- **criteriu de acceptare**: **MĂSURAT ȘI ACCEPTAT** *(decizia lui Costin, 25.08.2026)*
- **deschisă pe commit**: `fa3330c`
- **CUM S-A ÎNCHIS — decizia lui Costin, 25.08.2026**, pe partea care rămăsese vie: *„Cele patru semafoare derivate care aleg culoarea în randor: migrarea la structură se face, dar la reparații, cu celelalte etichete. E prag 3. Ce închide restanța acum: cele trei hardcodate sunt reparate, iar restul e datorie declarată. Marchează-o ca MĂSURATĂ ȘI ACCEPTATĂ, cu condiția de reluare la grupul 4."* Plus criteriul de proces: *„O restanță care așteaptă 29 de commituri fără să se poată închide n-are condiția scrisă bine."*
- **CONDIȚIA DE RELUARE**: **grupul 4 din ordinea reparațiilor** (`PLAN_ARHITECTURA` Partea VII — *Direcția dependenței*, P3·P13, interdicțiile 4, 5, 13, 15, 26, 27, **31**). Acolo se face migrarea la structură, împreună cu celelalte etichete cheiate pe altceva decât starea. Nu e o condiție cablabilă pe fișier — motivul e scris: momentul e un punct din plan, nu o atingere de cod (`PLAN_LUCRU`, „forma condiției de deblocare").
- **CIFRA CLASEI, măsurată acum ca să nu rămână „patru" din memorie: 14 instanțe, în 3 fișiere** — `control_verdict.js` **4** (la zi · de urmărit · restanță · nu se poate verifica), `asistenti.js` **4** (probleme · de urmărit · fără probleme · nu se poate verifica), `etransport_ecran.js` **6** (în valabilitate · expiră curând · EXPIRAT · trimisă · eroare · în lucru). Costin a numit **patru**; patru sunt cele din `control_verdict.js`, fișierul cel mai vizibil. Registrul numea **trei** — trei sunt **fișierele**. Amândouă erau adevărate despre altceva.
- **INSTRUMENTUL A GREȘIT DE DOUĂ ORI, în aceeași direcție, în aceeași măsurătoare** *(interdicția 76: se calibrează pe felul în care POATE greși)*: prima formă căuta doar harta cu obiect imbricat (`verde: { txt: "…" }`) și a dat **4 într-un fișier** — deși registrul numea trei fișiere; `asistenti.js` și `etransport_ecran.js` folosesc harta **plată** (`verde: "fără probleme"`). A doua formă respingea orice valoare de un singur cuvânt ca „nume de cheie" și pierdea **„probleme"** — o etichetă reală. Cifra 14 e de la a treia formă, calibrată pe **toate cele trei fișiere numite în registru**.
- **ce blochează**: **Decizie cerută [atunci].** R28 a scos blocul de estimare, iar în același bloc trăia și altceva: avertismentul că **la un leu peste salariul minim se stinge facilitatea și netul SCADE** (OUG 156/2024 art. LXVI / OUG 89/2025 art. III), cu brutul de la care netul redevine cel de la minim. Nu era o estimare de confort — era o **prăpastie** pe care un contabil o poate călca fără s-o vadă, iar ecranul o arăta **înainte de buton** (`DS` cap. 6). A plecat colateral, și e corect că a plecat **așa cum era**: textul lui conținea **două cifre de net**, calculate cu aceleași valori implicite care au invalidat estimarea.
- **CE S-A SEPARAT, ȘI DE CE.** Decizia de mai sus privește **jumătatea „verde scris, nu derivat"**. Cealaltă jumătate a lui R30 — **avertismentul de prăpastie al salariului minim** — n-a fost atinsă de ea: e ARTEFACT/DECIZIE, prag 2, iar întrebarea (a)/(b)/(c) e tot fără răspuns. A rămâne aici ar fi însemnat s-o închid tăcut odată cu restanța, adică să aleg singur varianta (a) — *«nu se întoarce»* — care e chiar alegerea pe care condiția o interzice. **Mutată ca `R49`.** *Și e instanța regulii lui Costin din aceeași comandă: R30 n-a putut fi închisă 29 de commituri fiindcă avea două subiecte cu două condiții de închidere.*
- **condiția de deblocare**: clasa e **acceptată măsurată** — se reia la **grupul 4** din ordinea reparațiilor, unde etichetele se migrează la structură împreună. Se închide definitiv când cele **14** instanțe din cele 3 fișiere nu mai cheiază un text pe o culoare. *Momentul e un punct din plan, nu o atingere de fișier, deci condiția NU e cablabilă — motivul e scris, cum cere `PLAN_LUCRU`.*
- **condiția veche, a jumătății mutate la R49** *(istoric)*: se alege una și se scrie de ce. **(a)** Nu se întoarce — prăpastia se semnalează la salvare, de server, unde toate elementele sunt cunoscute. **(b)** Se întoarce **fără nicio cifră**: *«brutul introdus e peste salariul minim — se pierde facilitatea de scutire»*. E o afirmație de **drept**, adevărată pentru oricine, independentă de persoane în întreținere sau de normă, deci nu poate contrazice fluturașul. **(c)** Se întoarce cu cifre, dar calculate cu **toate** elementele salariatului. Se închide când e scris **care** și **de ce**. *Nu se începe fără decizie: (b) pare evident ieftin, dar a alege singur ce spune un ecran e chiar ce s-a cerut să nu fac.*

- **LĂRGITĂ 24.08.2026 (Costin): R30 primește și clasa „verde SCRIS, nu derivat".** Cerută explicit — *„regula e consemnează întâi, apoi decide dacă repari"* — după ce triajul semafoarelor a produs măsurători care s-ar fi pierdut la închiderea sesiunii. **Cele două subiecte rămân distincte**: avertismentul de prăpastie e ARTEFACT/DECIZIE și e **neatins** de rândurile de mai jos, iar condiția lui de deblocare (a)/(b)/(c) rămâne deschisă; clasa de aici e VERIFICARE/INTERN. *Consecință mecanică, scrisă ca să nu surprindă:* `scripts/raport_b.py` numără **restanțe**, nu instanțe, și citește un singur `felul` pe secțiune — deci B va arăta același număr de restanțe deschise, iar cele trei instanțe vor fi raportate sub felul ARTEFACT. Ca cifra să le prindă, ele cer o **restanță proprie**; vezi „ce nu închide lărgirea".
- **CELE TREI INSTANȚE — măsurate 24.08.2026, pe commit `9e545f3`.** Criteriul, al lui Costin: *„Un semafor verde care nu compară nimic spune «am verificat și e în regulă» — exact P6, verdele care afirmă. Iar contabilul nu are cum să distingă un verde derivat de unul scris."*

  | # | loc | ce face | prag |
  |---|---|---|---|
  | 1 | `cabinet.js:431-432` | `randuri \|\| «● Echipă activă»` — verdele apare **și** când `/asistenti/echipa/semafor` aruncă (`catch {}`) sau întoarce `!ok`. Nimic n-a fost comparat | **1** — afirmație falsă pe ecran, acum |
  | 2 | `cabinet.js:102` și `:104` | `var(--verde)` pasat **necondiționat** pentru „validate" și „depuse"; `0 validate` se pictează verde. Frații de pe aceeași listă (`respinse`, `de validat`, `sesizări noi`) pasează culoarea doar pe număr nenul | 2 — verde pe zero, culoare pe numărătoare, nu verdict |
  | 3 | `capacitate.js:53` | idem, pe `depuse_luna`; iar `de_validat`, pe **linia de deasupra**, este condiționat | 2 |

- **DE CÂND — n-au fost NICIODATĂ derivate.** `git blame`: instanța 1 vine din `cbf24ce` (**commitul rădăcină**, 01.07.2026, „Snapshot initial"); instanțele 2 și 3 din `a6d9c2c0` (13.07.2026) — iar fratele lor condiționat, `cabinet.js:103` (`d65724c3`), e din **aceeași zi**: forma corectă exista la un rând distanță și n-a fost aplicată. **Limita măsurătorii, declarată:** `cbf24ce` e commitul rădăcină (1.766 de commituri), deci „niciodată" e demonstrabil **doar până la 01.07.2026** — înainte de snapshot nu există istorie în depozitul ăsta. *Al treilea semnal al clasei „n-a fost niciodată corect" în două zile.*
- **CE NU SUNT, verificat la sursă ÎNAINTE de reparație.** **(a)** Nu sunt cele trei din Grupa A a censului de 24.08 (`control_verdict.js`, `asistenti.js`, `etransport_ecran.js`): alea primesc o **stare reală** de la server, iar defectul lor e **eticheta cheiată pe culoare** — interdicția **31**, nu P6. **(b)** **Nu există niciun semafor verde lângă cota de impozit pe dividende.** Căutat în toate cele 37 de ecrane din `static/js/`, în `core/control_incrucisat.py`, `core/control_fiscal_api.py`, `main.py` și în toți consumatorii lui `impozit_dividend`. Singurul semafor pe dividende — `D205 (impozit dividende)`, `control_incrucisat.py:1494` — **e derivat**: `_thunk_d205` scoate rulajul contului **457**, citește cota period-aware din registru (`cota("impozit_dividend", date(an, 12, 31))`, l. 1212) și cheamă `d205_reconciliere.reconciliaza`; fără dividende plătite, linia e **sărită ca NEVERIFICAT**, nu verde.
- **DAR — și asta rămâne DESCHIS.** Cota din registru e **intrare în ambele părți** ale comparației, nu unul dintre termenii ei: dacă `COTE["impozit_dividend"]` e greșită sau expirată, generatorul și recalculul folosesc **aceeași** cotă greșită, diferența e zero, iar semaforul rămâne verde. Clasa nu e ipotetică — `GARZI.md:2759`: cota pe 2025 era 10%, codul aplica 8%, **sub-declarare de 20%**; reconcilierea D205 **nu ar fi prins-o**, exact din motivul ăsta. Un semafor care să compare *cota* cere un al doilea termen **extern** (validatorul, sau `scripts/vigoare_articol.py`), nu declarația. Consemnat aici, **nereparat** — ce păzește azi cota însăși e `core/expirare_cote.py` (`CONFIRMARE_COTE_PRAG_LUNI`, raport din cron), nu un semafor de ecran.
- **REPARAT 24.08.2026**, pe regula lui Costin: *„dacă starea se poate deriva, se derivă; dacă nu se poate deriva încă, se scoate semaforul, nu se lasă verde. Absența unui indicator e onestă; un verde care nu verifică nimic nu e."* Instanța **1** — starea are acum trei valori (`derivat`), iar când nu se poate deriva **semaforul lipsește**, nu devine verde. Instanțele **2** și **3** — culoarea devine condiționată, ca frații de lângă ele. Instanța 3 **nu** s-a derivat din `control_incrucisat`, cum cerea comanda: `cab.depuse_luna` vine din `core/capacitate_api.py:57`, un `COUNT(*) FILTER (WHERE depus_la >= început_de_lună)` — numărătoare de volum al cabinetului, fără legătură cu controlul fiscal, deci n-are ce deriva de acolo. Gardat de `core/test_verde_derivat.py`, RED-probat prin mutație.
- **CE NU ÎNCHIDE LĂRGIREA, și e condiția de deblocare a clasei:** cele trei sunt pinuite pe **fișier și formă**, nu pe **clasă**. Un scan care găsește *orice* verde emis fără condiție în `static/js/` **nu există** — până există, a patra apariție intră mâine fără să se vadă, exact tiparul lui R29 (clasă golită pe un limbaj, vie în altul). Se închide când gardul are domeniul `static/js/` pe clasă, nu pe cele trei situri, **sau** când clasa primește restanță proprie ca s-o prindă cifra din B.

### R41 — Verdictul oficial de validare se produce, se afișează și se aruncă

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · TRASEE I, pasul 3 · interdicția 32 · **PRAG 1** *(ecranul spune „De depus" despre lucruri care nu sunt de depus — afirmație falsă, nu listă incompletă)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `9b3bf41`
- **deschisă pe commit**: `6d3a414`
- **măsurat la**: 2026-08-24 · **pe commit**: `6d3a414`
- **cum s-a închis — PARTEA A II-A, ECRANUL (25.08.2026).** Condiția era: *„cele patru câmpuri se persistă, `aproba` și `depune` le consultă, iar ecranul separă cele două liste. Se închide când o declarație fără verdict proaspăt **nu poate** ajunge în «De depus», probat prin mutație."* Toate trei sunt făcute.
  - **Serverul spune ce știe.** `lista_coada` întoarce acum `verdict_stare` și `gata_de_depus` pentru fiecare element. Până azi starea exista în bază și **nu ajungea la ecran** — de asta ecranul nu avea cum să nu mintă, oricât de corect ar fi fost scris.
  - **O singură definiție a lui «gata de depus».** `_poarta_verdict` (care refuză depunerea) și `lista_coada` (care alimentează ecranul) cheamă **aceeași funcție**, `gata_de_depus`. Nu e o curățenie de stil: două condiții scrise separat sunt exact mecanismul prin care ecranul ajunge să numească „de depus" ce serverul refuză. Gardat **pe structură** (AST, nu text) în `core/test_coada_gata_de_depus.py`, cu RED-proof pe **două** mutații — condiția rescrisă inline în poartă, și `gata_de_depus` care întoarce mereu `True`.
  - **Ecranul: două liste, nu una.** „De depus" conține **doar** ce e gata. Restul stă în „Generate, nevalidate", care spune **ce lipsește** și **pe unde se iese**. Când nimic nu e gata, golul poartă cauza și ieșirea (DS cap. 6, fundătura interzisă).
  - **Eticheta e derivată, nu aleasă.** Purta `c.coerenta`, care e `NULL` pe toate elementele — deci scria *„neverificat"* despre orice, inclusiv despre o declarație pe care validatorul tocmai o dăduse validă. Acum are patru stări: validat · erori · **stătut** · nevalidat (interdicția 31).
  - **Trecerea peste refuz există, dar e explicită.** Butonul principal pe un element nevalidat e cel care **repară** („Deschide ca să fie validat" — ruta rulează DUKIntegrator și persistă verdictul). „Depune totuși…" cere un motiv **obligatoriu**, consemnat cu cine și când. Un blocaj fără cale de trecere pentru om ar fi interdicția **47**.
  - **Și cardul, nu doar ecranul.** Tabloul cabinetului spunea *„3 declarații de depus"* despre trei declarații pe care serverul le refuză. Acum numără ce e gata, și spune separat câte sunt nevalidate.
- **ce a prins proba comportamentală, și niciun test nu prindea:** prima formă a cardului număra **toate** rândurile din răspuns, deci includea și o declarație **deja depusă** — cifra de pe card (3) nu era despre aceeași populație ca cifra de pe ecran (2). Reparat înainte de commit; proba are acum o aserțiune care compară chiar cele două cifre între ele. *Un card și un ecran care numără altceva sub aceeași etichetă sunt aceeași clasă de defect ca R41 însuși, cu un nivel mai sus.*
- **cum s-a probat:** `frontend_test/proba_r41_coada.py` (Playwright, desktop + Pixel 5) — **14 afirmații, toate verzi**, pe o coadă cu stare **mixtă** (una gata, una nu), deci cele două liste chiar se separă. Așteptările sunt **derivate din starea reală a cozii**, nu fixate pe o cifră: proba însăși mută un element din „nevalidat" în „gata" când deschide o declarație, iar o aserțiune pe „(0)" ar fi devenit falsă după prima rulare și ar fi arătat ca o regresie. Zero erori de consolă, desktop și mobil.
- **și o capcană de metodă, fiindcă era gata să treacă drept probă:** prima rulare a dat *„16/16"* — dar pe **procesul vechi**. JS-ul se servește de pe disc, deci era cel nou; `core/coada_api.py` rulează în serviciu, care nu se repornise. Cu `gata_de_depus` **absent** din răspuns, `c.gata_de_depus` era `undefined`, totul cădea în „nevalidat", iar asta se potrivea exact cu așteptarea de atunci („De depus (0)"). *Un verde obținut fiindcă jumătate din reparație nu rula.* Proba adevărată e cea de după repornire, pe stare mixtă.
- **ce NU s-a închis, declarat:** ecranul cozii **nu e în `nav_ecrane.ECRANE`**, deci scanul vizual/a11y nu-l atinge — `test_acoperire_vizuala` a trecut pe el **vacuu**. Proba de mai sus acoperă comportamentul și consola, nu axe/contrast pe toată suprafața. *Rămâne o gaură numită, nu una descoperită mai târziu.*
- **numerotare**: Costin a numit-o **R44**; registrul avea ultima **R40**, iar R41–R43 nu există. Am folosit următorul număr liber ca să nu rămână trei goluri. Se redenumește la un cuvânt.
- **ce blochează**: validatorul oficial **este** legat — `GET /coada/{id}/continut` rulează DUKIntegrator (Java, `core/duk.py`, local, prin `subprocess`) **la fiecare deschidere** a unui element din coadă și întoarce `stare`, `erori`, `severitate`, `temei`, `limita`. Docstringul rutei spune `Read-only`, și asta e problema: **verdictul se produce și nu se scrie nicăieri**. Coloana care l-ar ține — `declaratii_coada.coerenta` — e parametru cu default `None` în `adauga_in_coada`, iar **singurul apelant (`POST /coada`) nu-l trimite niciodată**; e NULL pe 3 din 3. Nici `aproba`, nici `marcheaza_depusa` nu-l consultă — `marcheaza_depusa` **n-are nicio poartă**. Consecința măsurată: badge-ul afișează „neverificat" **pentru orice declarație, întotdeauna**, iar cele trei din „De depus" au ieșit din coadă fiindcă s-a apăsat un buton, nu fiindcă au trecut o verificare.
- **de ce e PRAG 1**: nu e o gardă care raportează greșit. Ecranul **numește** „De depus" o listă care conține declarații fără verdict. E o afirmație falsă despre starea lucrurilor, exact clasa celor trei semafoare din R30.
- **ce cere reparația — patru câmpuri, nu unul** *(Costin, 24.08.2026)*: **rezultatul** validării · **momentul** · **versiunea validatorului** · **amprenta fișierului validat**. Ultima e cea care contează: *un verdict pe un XML care s-a regenerat între timp nu mai e verdict.* Dacă amprenta diferă de a XML-ului curent, verdictul e **stătut**, nu valid — și nu poate ține locul unuia proaspăt.
- **ce mai cere, pe ecran** *(decis 24.08.2026, vezi `DECIZII.md`)*: coadă reală — verdict păstrat și afișat · blocare pe respins **sau lipsă** · trecere explicită și **consemnată** peste blocare · iar „De depus" arată **doar** ce e gata de depus, cu generatul-nevalidat într-o listă separată care spune **ce lipsește**.
- **condiția de deblocare**: cele patru câmpuri se persistă la generare/validare, `aproba` și `depune` le consultă, iar ecranul separă cele două liste. Se închide când o declarație fără verdict proaspăt **nu poate** ajunge în „De depus", probat prin mutație.

### R42 — 144 de rute care schimbă date nu verifică niciun rol, iar 24 din 24 dintre ele fac contabilitate

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE XI.2 · **PRAG 3** *(nimic fals pe ecran azi; lipsește o restricție, iar instalarea n-are al doilea actor care s-o exercite)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **planul**: NEACOPERIT. Căutat în PLAN_ARHITECTURA la P16 („Cine a autorizat, se știe" — cere ca actorul să fie identificabil, nu spune CARE actor are voie), la P11 („unde textul nu determină rezultatul, nu se alege — se cere decizia", care confirmă că se cere, dar nu răspunde) și în Partea 00 „Angajamentul față de cabinet". Planul nu repartizează operațiuni pe roluri. Criteriul l-a dat Costin pe 25.08; cele **patru întrebări** rămase sunt tot decizie, nu citire. (METODA §25)
- **deschisă pe commit**: `3cb6c44`
- **măsurat la**: 2026-08-25 · **pe commit**: `3cb6c44`
- **ce blochează**: din **229** de rute care schimbă ceva (POST/PUT/PATCH/DELETE), **144 cer doar să fii un utilizator autentificat al cabinetului** — nici gardă de rol, nici verificare în corp, nici ajutor, nici drept fin. `cere_cabinet` verifică exact două lucruri: că nu ești `client`, și că nu e cabinetul suspendat. **Un `angajat` și un `admin_firma` sunt același actor pe toate cele 144.** Concentrarea contează mai mult decât totalul: pe traseul **notei contabile (T05) sunt 24 din 24** — toate cele optsprezece rute `nota-*`, plus crearea, editarea, ștergerea și validarea din jurnal; pe **factură (T02) 11 din 13**; pe **regimurile speciale de TVA (T29) 10 din 10**. Singurele trasee păzite pe tot ce scriu sunt **închiderea lunii**, **pontajul** și **statul de plată**. *Perioada, prezența și statul sunt păzite; contabilitatea nu.*
- **de ce NU e prag 1**: efectul cere un al doilea actor, iar instalarea n-are unul — singurul cont `angajat` (`asistent@prisma-cont.test`) **n-are nicio firmă atribuită** în `public.user_tenants` și are toate cele trei drepturi fine pe `false`. Deci azi nimeni nu poate exercita lipsa. Pe primul cabinet cu doi oameni, poate.
- **ce s-a măsurat corect abia la a treia formă a instrumentului**: primele două au raportat „nu verifică nimic" despre rute care verifică — o dată fiindcă nu citeau garda din argument, a doua oară fiindcă nu vedeau nici comparația din corp, nici ajutorul `_cer_admin_cabinet`. Cifra 144 e de la forma care le vede pe toate patru. Instrument: `scripts/scan_trasee.py`.
- **CELE PATRU ÎNTREBĂRI, RĂSPUNSE (Costin, 25.08.2026) — și aplicate.**

  **(a) O notă contabilă e ceva emis?** *„Nu. E o înregistrare în evidență, nu un artefact predat. Se emit documentele care ies — factura, fluturașul, declarația. Nota rămâne înăuntru. Dar nu e nici liberă: o notă care a intrat în evidență nu se șterge, se stornează. Deci cele 24 de rute `nota-*` nu primesc `admin_firma` — primesc verificarea de la P15."*
  **Aplicat, și mai larg decât întrebarea.** `_cere_perioada_deschisa` păzea deja **editarea, ștergerea și validarea** unei note care există. **Crearea intra pe altă ușă și nu era păzită** — o notă nouă datată într-o lună închisă e tot o modificare a perioadei închise. Au primit verificarea **39 de rute**: cele 20 de creare din T05 (19 `nota-*` + `POST /jurnal`), plus **19 găsite de gardă**, pe care întrebarea nu le numea dar motivul deciziei le acoperă — operațiunile de regim special, amortizarea, contabilizarea unei facturi, raportul Z, aprobarea unui bon. *Toate scriu în `inregistrari`; a le lăsa afară ar fi însemnat un clichet cu 19 excepții, adică regulă scrisă pe jumătate de clasă.*
  `POST /tenants/{tenant_id}/plan-conturi` **nu** a primit-o, cu motivul: un cont din planul de conturi n-are dată, deci n-are perioadă.

  **(b) O completare manuală e parte din declarație?** *„Da, după generare. Nu, înainte. […] Deci ștergerea cere `admin_firma` dacă declarația e generată."*
  **Aplicat** pe `DELETE /d390-clasificare/manual/{mid}` și `DELETE /d300-manual/{rid}` — verificare **în corp**, nu dependență statică: condiția e pe starea datelor, iar o dependență ar cere administratorul și înainte de generare, unde decizia spune explicit că nu. „Generată" înseamnă **și în coadă, și depusă**: o declarație generată și nedepusă e tot generată, iar fereastra dintre ele e exact cea în care contează.
  La D300 perioada se citește **din rândul însuși**, nu din cerere — altfel s-ar putea șterge un rând dintr-o lună generată trimițând altă lună.

  **(c) Trecerea de regim e o ieșire?** *„Nu e o ieșire, dar cere `admin_firma`. […] Adaug criteriul: ce schimbă ce datorează firma cere `admin_firma`."*
  **Aplicat** pe `POST /firma-profil/regim-tva` (`platitor_tva`). **Nu** s-au atins, cu motivul scris: `firma-profil/model` (font, culoare, logo — nu schimbă nimic din ce se datorează) și `firma-profil/date` (nume, CUI, CAEN, adresă — **identifică** firma, nu decid ce datorează; vectorul o face, și el cere deja `admin_firma`).

  **(d) Cine pornește sau oprește un canal către client?** *„Pornirea și oprirea unui canal cer `admin_firma`. […] Nu e organizare internă — e o decizie despre cum comunică firma cu autoritatea și cu clienții."*
  **Aplicat** pe `PUT /woocommerce/config` — ruta scrie chiar cheile canalului: cu ele pline canalul e pornit, golite îl oprește. Nu există azi o rută de pornire/oprire pentru e-Factura/SPV; măsurat, nu presupus.

- **CE NU S-A SCHIMBAT, cu cifra.** Cele **7** operațiuni de regim special din T29 (vânzare în marjă, marjă-turism, aur de investiții, achiziție și vânzare de la agricultor, import și export extracomunitar) rămân la `cere_cabinet`: sunt **introducere**, iar criteriul spune explicit că introducerea o poate face un asistent. Cifra e gardată, ca să nu devină impresie.
- **GARDA**: `core/test_r42_criteriu.py` — 16 teste, **5 mutații** probate (verificarea care nu ridică niciodată · o rută care pierde apelul · `regim-tva` care pierde rolul · o notă strecurată pe `admin_firma` · ștergerea manuală care nu mai întreabă). Probele funcționale pe schemă efemeră verifică **și** refuzul, **și** că lunile deschise trec, **și** marginile lunii închise (1 și 31) — un `>` în loc de `>=` ar lăsa exact zilele de la capete.
- **condiția de deblocare**: **ÎNDEPLINITĂ.** Decizia e dată, aplicată pe toate patru ramurile, și păzită structural.
- **rezolvată pe commit**: `187a151`
- **DECIZIA, 25.08.2026 (Costin).** Criteriul, în cuvintele lui: *„tot ce iese din aplicație către o autoritate sau către un om, plus tot ce închide sau redeschide o perioadă. Concret: confirmarea depunerii · emiterea unui document · închiderea lunii · redeschiderea ei · ștergerea a ceva emis. Restul — introducere, generare, validare, pregătire — poate face un asistent. Motivul: alea se pot reface. Ce am numit mai sus, nu."*
- **APLICAT — 14 rute trecute pe `cere_rol("admin_firma")`**, fiecare în dreptul termenului din criteriu care o prinde:
  - *confirmarea depunerii*: `POST /coada/{id}/depune`;
  - *emiterea unui document, către un om*: `facturi/emite` · `POST /facturi` · `facturi/{id}/storno` · `facturi/{id}/email` · `stat-plata/emite` · `chitante` · `salariati/{id}/adeverinta` · `contracte/genereaza` · `pachete/{id}/trimite`;
  - *emiterea unui document, către o autoritate*: `facturi/{id}/trimite-spv` · `etransport/trimite` · `reges-trimite-salariat`;
  - *ștergerea a ceva emis*: `DELETE /facturi/{id}`;
  - *închiderea și redeschiderea perioadei* erau **deja** păzite cu `admin_firma` — singurul traseu din cele 35 care era.
- **CE S-A SCHIMBAT, măsurat**: rutele care schimbă date și nu verifică **niciun** rol scad de la **144 la 134** (din 229). Nu 14, fiindcă trei dintre ele erau deja pe `cere_rol` și doar s-au **îngustat** de la `admin_firma|angajat` la `admin_firma`, iar una (`stat-plata/emite`) verifica deja un drept fin în corp.
- **DOUĂ CONSECINȚE, scrise fiindcă nu decurg evident din criteriu:**
  1. **`poate_depune` pe un `angajat` nu mai poate fi exercitat.** Dreptul fin rămâne verificat în corpul rutei, dar poarta de rol e acum `admin_firma`, deci dreptul devine o **a doua** condiție peste rol, nu o cale paralelă. Patru-ochi nu e atins: *validarea* (`aproba`/`respinge`) rămâne la asistent — se poate reface.
  2. **Cele două rute de creare a facturii nu separă „introducerea" de „emiterea".** `POST /facturi` și `POST /facturi/emite` produc amândouă un document numerotat (R14: două funcții, stări implicite diferite), deci amândouă intră la *„emiterea unui document"*. Dacă separarea se face vreodată, partea de introducere se poate întoarce la asistent.
- **A DOUA APLICARE, 25.08.2026 — criteriul dus pe toate cele 134.** Rezultatul, pe categoriile criteriului:

  | categorie | rute | ce s-a făcut |
  |---|---|---|
  | închide/redeschide o perioadă | **0** | toate cinci erau deja păzite |
  | iese către o autoritate | **0** | `import-efactura` și `reges-poll` **aduc**, nu trimit |
  | iese către un om | **3** | trecute pe `admin_firma` |
  | șterge ceva **emis** | **0** | ștergerile ating note, registre și nomenclatoare — niciun document emis |
  | asistent (introducere, generare, validare, pregătire) | **118** | rămân |
  | **ambigue** | **13** | **nu s-au schimbat**, sunt numite mai jos |

- **Cele 3 care ies către un om**, verificate în corpul rutei, nu ghicite din nume: `POST /tenants/{}/solicitari` (trimite email clientului) · `POST /pachete/{}/poveste` (pe `status=aprobat` trimite raportul lunar) · `POST /tenants/{}/facturi/{}/link-plata` (produce linkul pe care îl primește clientul, și de care atârnă `platita_la` — R43).
- **Cele 13 AMBIGUE, pe fel, cu ce nu decide criteriul:**
  - **3 ștergeri care ating contabilitatea** (`casa/operatiuni/{}`, `jurnal/{}`, `rip/operatiuni/{}`) — o notă nu e „emisă", dar e evidență contabilă;
  - **3 ștergeri de completări manuale la o declarație care se depune** (`d300-manual/{}`, `d301-operatiuni/{}`, `d390-clasificare/manual/{}`) — nu sunt „ceva emis", dar schimbă cifra care pleacă la ANAF;
  - **3 de regim fiscal** (`firma-profil/{date,model,regim-tva}`) — nu emit nimic, dar schimbă ce se datorează (R46);
  - **2 de canal către client** (`scadentar/opt-in`, `facturi/{}/notificare`) — pornesc sau **opresc** ce pleacă la client; nu trimit ele însele;
  - **`PUT /facturi/numerotare`** — nu emite, dar controlează seria documentelor emise (interdicția 35: serie fără goluri);
  - **`POST /recomanda`** — trimite email unui terț, dar e marketing, nu artefact al firmei.
- **RECLASIFICARE PE FAPT, 25.08.2026 (Costin: *„criteriul l-am dat în abstract, tu l-ai aplicat pe nume de rută"*).** Critica e corectă și cifra o arată. A doua măsurătoare nu se uită la calea rutei, ci la **ce scrie și pe unde ajunge**:
  - **SE_DEPUNE** = scrie într-o tabelă pe care o **citește** cel puțin un modul `core/d*.py` — adică ce scrie ea ajunge într-o cifră care pleacă la ANAF. Cele zece tabele, derivate: `facturi`, `factura_linii`, `inregistrari`, `inregistrari_linii`, `clienti`, `furnizori`, `asociati`, `firma_profil`, `plan_conturi`, `d301_operatiuni`;
  - **SE_PREDĂ** = scrie într-o tabelă de artefact dat unui om (`facturi`, `state_plata`, `chitante`, `artefacte_produse`);
  - **IESE_AFARĂ** = ajunge la un modul-margine **sau** trimite un email — detectat din AST, nu din nume.

  | ce ating, măsurat | rute |
  |---|---|
  | **SE_DEPUNE** | **64** |
  | **SE_DEPUNE + SE_PREDĂ** | **10** |
  | IESE_AFARĂ | 2 |
  | IESE_AFARĂ + SE_DEPUNE + SE_PREDĂ | 1 |
  | INTERN (nu ating nicio ieșire) | 57 |

- **Deci 77 din 134 ating o ieșire care se depune sau se predă — nu 3.** Clasificarea pe nume găsise **trei**. *Diferența nu e o corectură de cifră, e diferența dintre a citi eticheta și a citi fapta.*
- **Cifra acum: 131** de rute care schimbă date și nu verifică niciun rol (144 la deschidere · 134 după prima aplicare · **a urcat înapoi la 134** când trei rute de artefact au trecut de la GET la POST pentru R45 și au devenit acte · 131 după ce au primit `admin_firma`).
- **Consecință proprie, consemnată**: o reparație (R45) a **înrăutățit** cifra alteia (R42) cu trei, fiindcă a transformat trei citiri în acte. S-a văzut doar la remăsurare. *O reparație care schimbă populația altei măsurători trebuie să remăsoare, nu să presupună.*
- **A TREIA APLICARE, 25.08.2026 (Costin)**: *„Doar cele care ating un artefact predat — 11, nu 77. Cele 64 care scriu într-o tabelă citită de o declarație nu produc nimic: declarația se generează separat, iar generarea are propriul rol. A cere `admin_firma` la fiecare introducere de date ar bloca munca zilnică a unui asistent."*
- **APLICAT: 11 rute** — cele patru `achizitie-*` (IC, necorporală, neînregistrat, taxare inversă) · `bonuri/{}/stinge` · `facturi-primite/{}/valideaza` · `facturi/{}/transforma` · `facturi/{}/notificare` · `scadentar/opt-in` · `woocommerce/sincronizeaza` · `PUT /facturi/numerotare`. Cifra scade de la **134 la 123**.
- **CELE PATRU ÎNTREBĂRI care rămân** *(cerute explicit — categoriile nu erau întrebări)*:
  1. **O notă contabilă e „ceva emis"?** Trei ștergeri o ating (`casa/operatiuni/{}`, `jurnal/{}`, `rip/operatiuni/{}`). Nu e un document predat cuiva, dar e evidență pe care stă o declarație depusă. *Dacă da → cele trei cer `admin_firma`; dacă nu → rămân la asistent, iar ștergerea unei note validate rămâne o operațiune de zi cu zi.*
  2. **O completare manuală la o declarație e parte din declarație?** Trei ștergeri o ating (`d300-manual/{}`, `d301-operatiuni/{}`, `d390-clasificare/manual/{}`). Nu e „ceva emis", dar **schimbă cifra care pleacă la ANAF**. *Dacă da → generarea nu mai e singurul loc cu rol.*
  3. **Trecerea de regim fiscal e o „ieșire"?** Trei rute (`firma-profil/{date,model,regim-tva}`). Nu emit nimic, dar schimbă **ce declarații se datorează** (R46). *Dacă da → e singura clasă care intră fără să producă un artefact.*
  4. **Cine pornește sau oprește un canal către client?** Patru rute (`scadentar/opt-in`, `facturi/{}/notificare` — deja mutate — plus `PUT /facturi/numerotare` și `POST /recomanda`). *Numerotarea nu emite, dar controlează seria documentelor emise (interdicția 35); recomandarea trimite email unui terț, dar e marketing, nu artefact al firmei.*
- **condiția de deblocare**: se răspunde la cele patru întrebări, apoi cifra devine clichet în `core/test_trasee.py`. Se închide când numărul nu mai poate crește tăcut. *Restanța rămâne DESCHISĂ: criteriul e aplicat pe tot ce decide singur; ce nu decide e numit, nu tăcut.*

### R43 — Confirmarea de plată marchează o factură încasată fără să fi intrat un leu, și caută prin toate firmele

- **felul**: ARTEFACT
- **cine deblochează**: EXTERN
- **unde intră**: E1 · TRASEE XI.3, T18 · **PRAG 2** *(cauză unică, dovedită, nu concurează cu nimic)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `3cb6c44`
- **măsurat la**: 2026-08-25 · **pe commit**: `3cb6c44`
- **ce blochează**: `GET /public/plata/{ref}` întoarce o pagină al cărei text spune, literal, *„Integrarea cu procesatorul de plăți urmează. Apăsați pentru a simula plata."* Butonul ei cheamă `POST /public/plata/{ref}/confirma`, care e **neautentificată**, **parcurge toate schemele de firme** din `public.tenants` și pune `platita_la = now()` pe prima factură cu `plata_ref` potrivit. Deci cine primește linkul poate marca factura încasată **fără să fi plătit**, iar `platita_la` devine o afirmație despre bani care nu e sprijinită de nimic.
- **ce NU e**: nu e o scurgere. `ref` e `"pl_" + secrets.token_urlsafe(16)` — 128 de biți, neghicibil. Iar căutarea prin toate schemele nu expune nimic în afara firmei care a emis linkul. **Problema e semantica, nu secretul**: aplicația nu deosebește „clientul a apăsat butonul de demo" de „banii au intrat".
- **de ce e prag 2 și nu 1**: nicio firmă din cele 17 n-a generat vreun link (`plata_ref` gol peste tot), deci efectul n-a fost produs; dar e o **cauză unică**, dovedită, care nu concurează cu nimic.
- **condiția de deblocare**: **trebuie cheile unui procesator de plăți real** (Stripe, Netopia sau echivalent), **de la Costin**, **pentru ca** `platita_la` să însemne bani intrați, nu un buton apăsat — `provider_activ()` ridică deja `NotImplementedError` pentru orice provider în afară de `mock`, deci calea e pregătită. Până atunci, se închide parțial dacă `platita_la` scris pe calea `mock` poartă o **marcă de simulare** care se vede în evidență. Se închide complet când confirmarea vine de la provider, semnată, și când ruta nu mai parcurge toate schemele, ci pleacă de la firma din `ref`.

### R44 — Un element din coadă e legat de o firmă care nu există

> **27.08.2026** — necunoscuta pe care sta si R44, si R50 (*ce anume depinde de un `tenant_id` in `public`*) e **masurata**: 13 tabele, din care 10 fara cheie straina, 67 de randuri orfane pe doi tenanti disparuti. Lista, in **R72**; ce inseamna pentru calea de stergere, in **R50**.

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · TRASEE XI.4 · interdicția 32 · **PRAG 3**
- **reluări**: 1
- **când s-a reluat**: 25.08.2026 — declanșatorul s-a produs (`core/coada_api.py` atins de R41 partea II), iar `core/test_reaprindere.py` a cerut reluarea **în aceeași tură**. Reaprinderea nu e opțională.
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `91b77ec`
- **notă la închidere**: acolo coboară clichetul de orfani la 0; ștergerea rândului 2020 e o operațiune pe **date**, făcută în aceeași tură, nu un commit.
- **cum s-a închis**: rândul 2020 **s-a șters**, la decizia lui Costin (25.08.2026). Clichetul de orfani din `core/test_coada_firma_exista.py` coboară la **0**, iar poarta de intrare îl ține acolo. Copia integrală a rândului, înainte de ștergere, e în `/tmp/coada_2020_inainte_de_stergere.json` — dovada supraviețuiește ștergerii.
- **CORECTURĂ LA PREMISA DECIZIEI, fiindcă măsurătoarea o contrazice.** Costin: *„E un rând de test dintr-o rulare a probei, cu id fabricat, pe o firmă care nu există."* **Nu era.** Rândul e din **15.08.2026, ora 15:44** — cu zece zile înaintea oricărei probe din sesiunea asta. Firma 13245 a **existat și a fost folosită**: `public.audit_log` are **21 de rânduri** pe ea, între 15:21 și 17:41 în aceeași zi, toate de la userul 1968, inclusiv un **`PUT /tenants/13245/facturi/numerotare`** — o scriere. Nu e reziduu de probă; e o firmă ștearsă care și-a lăsat declarația în urmă. *Rândurile care chiar veneau din proba mea (3847, 3848, `tenant_id` 999000777) fuseseră deja șterse, tot în tura aia, cu cauza scrisă în `GARZI.md`.*
- **VERIFICAREA LA INTRARE EXISTĂ — măsurat 25.08.2026, contra ipotezei că ar lipsi.** `POST /coada` cheamă `_schema_sau_404(ctx, date.tenant_id)`, care interoghează `public.tenants` și **ridică 404** dacă firma nu e a cabinetului sau nu e activă; iar generarea XML-ului rulează **pe schema firmei**, deci fără schemă n-ar fi produs nimic. Rândul 2020 are un XML de 708 de octeți cu datele reale ale firmei — **deci firma exista la momentul creării**. Ruta n-a acceptat un `tenant_id` fără firmă; firma a fost **ștearsă după**. Ce lipsește nu e o verificare la intrare, ci **curățarea la ștergere** — R50.
- **A DOUA CONSTATARE, care nu era căutată**: **ștergerea unui cabinet nu curăță tabelele partajate.** `core/gdpr_sterge.executa` face `DROP SCHEMA CASCADE` și șterge din `audit_log`, `user_tenants`, `tenants`, `users`, `accounting_firms` — dar **nu atinge** `public.declaratii_coada` și `public.declaratii_depuse`. Ăsta e mecanismul care produce orfani, și va produce alții. Deschis ca **R50**.
- **deschisă pe commit**: `3cb6c44`
- **măsurat la**: 2026-08-25 · **pe commit**: `3cb6c44`
- **CE S-A FĂCUT LA RELUARE**: **refuzul e construit.** `adauga_in_coada` interoghează `public.tenants` **înaintea** inserării și întoarce `FIRMA_INEXISTENTA`. Nu e cheie străină, și motivul e scris în cod: `declaratii_coada` e tabelă **partajată**, iar firmele trăiesc și ca **scheme** — o cheie străină ar lega două modele de date diferite. Poarta de intrare în coadă e una singură, deci acolo stă refuzul. Gardat de `core/test_coada_firma_exista.py` (3 teste, pe structură): interogarea există · codul de refuz există · refuzul e **înaintea** `INSERT`-ului, fiindcă unul scris după n-ar refuza, ar curăța.
- **CE NU S-A ÎNCHIS, și de ce**: rândul orfan care **există deja** (id 2020, `tenant_id` 13245). Ștergerea lui e o operațiune pe **datele** unei instalări, nu pe cod — nu se face fără cuvântul lui Costin. Până atunci e **clichet 1**: nu mai poate apărea al doilea. *Motivul eșecului devine condiția de deblocare, cum cere fluxul (pasul 4).*
- **condiția de deblocare, rescrisă**: se decide ce se face cu rândul 2020 — se șterge, sau se relegă de `tenant_017` (firma din payload). Se închide când clichetul de orfani din `core/test_coada_firma_exista.py` ajunge la **0**.
- **ce blochează**: `public.declaratii_coada.id = 2020` are `tenant_id = 13245`. În `public.tenants` **nu există** rândul, iar schema `tenant_13245` **nu există** în bază. Conținutul lui e un D300 pe august 2026 al firmei *„Firma Grea Audit SRL"*, care e `tenant_017`, id **14769**. Deci o declarație stă în coadă, în starea `la_senior`, legată de o firmă ștearsă sau niciodată creată — și **nimic n-o semnalează**: nici ecranul cozii, nici vreo verificare. Coada are 3 elemente; **unul din trei e orfan**.
- **ce NU se știe încă, și nu se scrie ca fapt**: dacă firma a existat și a fost ștearsă (caz în care ștergerea nu curăță coada), sau dacă `tenant_id` a fost scris greșit de la început. `public.audit_log` nu conține nicio urmă a lui 13245 — deci nu se poate reconstitui, doar constata.
- **condiția de deblocare**: la primul commit care atinge `core/coada_api.py`, `adauga_in_coada` refuză un `tenant_id` care nu există în `public.tenants`, iar o gardă numără elementele orfane și cere zero. Se închide când numărătoarea e zero **și** inserarea unui orfan e imposibilă, probat prin mutație.

### R45 — Patru artefacte se produc, se descarcă, și nu rămân nicăieri

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE XI.7 · interdicția 32 · **PRAG 2** *(sunt absențe: n-au instanțe de ordonat)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `3cb6c44`
- **măsurat la**: 2026-08-25 · **pe commit**: `3cb6c44`
- **ce blochează**: e **aceeași clasă cu R41**, în patru locuri diferite — artefactul se produce, se afișează sau se descarcă, și nu se păstrează:
  - **situațiile financiare anuale (S1003, S1005)** — 4 rute, `bilant_api` **nu scrie nimic**; nu intră nici în coadă (nu există `POST /coada` pentru ele), nici în `declaratii_depuse`. *Artefactul care încheie exercițiul financiar n-are memorie.*
  - **fișierul de plată a salariilor** — 2 rute, amândouă `GET`; nu se consemnează că s-a generat, pentru ce lună, de cine. „Salariile s-au plătit" nu e o stare a aplicației.
  - **exportul contabil (SAGA, WinMentor)** — 3 rute, toate `GET`, zero scrieri. La o preluare inversă, „ce s-a exportat și când" e exact întrebarea.
  - **auditul de preluare** — `audit_preluare` **nu scrie nimic**; verdictul lui se afișează și se pierde. *Măsurat acum, nu presupus — Partea X îl lăsase marcat ca nemăsurat, tocmai ca să nu fie scris ca fapt.*
- **de ce ca o singură restanță, nu patru**: au aceeași cauză (nu există un loc unde se ține un artefact produs) și aceeași reparație (un rând cu ce s-a produs, când, de cine, cu amprenta conținutului — exact cele patru câmpuri alese la R41). Patru restanțe ar ordona de patru ori aceeași decizie.
- **DECIZIA, 25.08.2026 (Costin).** *„Se păstrează, cu: artefactul însuși, momentul, autorul, amprenta conținutului, și numărul exemplarului. Iar dacă e o declarație, plus verdictul de validare cu amprenta fișierului validat. Un artefact produs și nepăstrat nu se poate apăra. E chiar P4."*
- **CELE CINCI CÂMPURI, plus al șaselea condiționat:**

  | câmp | de ce |
  |---|---|
  | **artefactul însuși** | fără el, restul e metadată despre nimic |
  | **momentul** | când a fost produs |
  | **autorul** | P16: orice act cu efect juridic extern are autor identificat |
  | **amprenta conținutului** | ce s-a produs, nu ce s-ar produce acum dacă s-ar regenera |
  | **numărul exemplarului** | P4: emiterea e idempotentă și repetabilă, iar al doilea exemplar e un fapt, nu o eroare |
  | **verdictul de validare + amprenta fișierului validat** | **doar la declarații** — aceleași patru câmpuri construite la R41 |
- **ce leagă ultimul rând, și e o observație despre numerotare**: Costin a numit legătura *„cea de la R44"*. R44 din registru e orfanul din coadă; verdictul cu amprentă e **R41** — aceeași abatere de numerotare ca la deschiderea lui R41, pe care el a numit-o R44 de trei ori. **Am legat-o de R41, fiindcă acolo e mecanismul.** Se redenumește la un cuvânt.
- **CONSTRUIT, 25.08.2026 — trei din patru.** `core/artefacte.py` + `core/migrare_artefacte.py` (tabela `artefacte_produse`, aplicată pe **17/17** scheme, cu mirror în `tenant_template.sql`). Un singur loc, nu patru: aceeași cauză, aceeași reparație — patru implementări ar fi însemnat patru vocabulare pentru același lucru.
  - **situațiile financiare (S1003, S1005)** — se păstrează la `-valideaza`, cu toate cele cinci câmpuri **plus verdictul** și amprenta XML-ului validat, luate de la `duk.versiune_validator` (aceeași sursă ca R41);
  - **fișierul de plată a salariilor** — se păstrează;
  - **exportul contabil (SAGA, WinMentor)** — arhiva se păstrează întreagă, base64 în coloană, cu amprenta pe **octeții** ei.
- **OBSTACOLUL, prins la wiring și nu ocolit**: trei din cele patru se produceau pe **GET**, iar `core/test_get_fara_scriere.py` interzice unui GET să scrie în starea de business (interdicția 6 — garda a ieșit din cele 24 de rânduri lăsate în `state_plata` de o simplă deschidere de ecran). Deci *„se păstrează"* a cerut ca **producerea lor să devină un act**: cele trei rute au trecut pe **POST**, împreună cu cele trei apeluri din ecran. Erau deja declanșate de un buton — doar metoda le contrazicea fapta.
- **AL PATRULEA — FĂCUT, iar motivul pentru care nu-l făcusem era GREȘIT.** Scrisesem că auditul de preluare *„se randează la deschiderea ecranului, deci un POST ar produce un exemplar la fiecare privire"*. **Fals.** L-am dedus din locul apelului (`api.get`), fără să citesc contextul: auditul e **deja în spatele unui buton** — *„Rulează auditul de preluare"* / *„Rerulează auditul"* (`control_verdict.js`, `ruleazaAudit`). Deci nu cerea nicio decizie de design. Ruta a trecut pe **POST**, verdictul se păstrează (serializat întreg), iar cheia e **anul**: două audituri în ani diferiți sunt două artefacte, două în aceeași zi sunt exemplarul 1 și 2 ale aceluiași. **R45 e completă: 4 din 4.**
- *A treia oară în două zile când am afirmat o absență citind un singur loc, nu contextul lui* — după „ruta fără gardă" și „modulul care nu scrie nimic". Toate trei în aceeași direcție: **lipsește**.
- **ce a prins gardul propriu, în chiar commitul lui**: `export-winmentor` trecuse pe POST și **nu păstra nimic**. *O rută care și-a schimbat metoda fără să capete fapta e mai rea decât una nemodificată — arată reparată.*
- **condiția de deblocare**: se decide cum se păstrează auditul de preluare (act propriu în ecran). Se închide când `scripts/scan_trasee.py` nu mai raportează niciun traseu **PARȚIAL** din cauza asta.

### R46 — Trecerea de regim fiscal are cea mai mare consecință și cele mai puține verificări

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · TRASEE X.8 și XI · **PRAG 3**
- **reluări**: 1
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `3cb6c44`
- **rezolvată pe commit**: `892b337`
- **măsurat la**: 2026-08-25 · **pe commit**: `3cb6c44`
- **ce blochează**: constatarea e din Partea X (24.08) și **n-a avut până azi loc cu stare** — trăia în narațiune, exact clasa măsurată pe 22.08 (din opt defecte, cinci fără loc cu stare). O trecere micro↔profit sau plătitor↔neplătitor schimbă **ce declarații se datorează, pe ce perioade, cu ce cote**. Traseul are **8 rute, 4 care scriu, dintre care 3 fără nicio verificare de rol**, și **nu s-a găsit nicio verificare de coerență la schimbare**: nici că perioada afectată e deschisă, nici că declarațiile deja depuse pe regimul vechi rămân explicabile. Pentru comparație, casa are 29 de refuzuri; asta are 9 pe tot traseul.
- **RELUATĂ 26.08.2026 — declanșatorul mecanic s-a produs, iar `core/test_reaprindere.py` a oprit commitul.** Am atins `core/firma_profil_api.py` pentru **altceva** (R66: `patron_nume` intră în `CAMPURI_FISCALE`, plus `cere_administrator`), nu pentru regimul fiscal. Declanșatorul e legat de **fișier**, deci s-a aprins corect chiar dacă munca era pe altă temă — și exact aia e valoarea lui: *reaprinderea n-a funcționat niciodată până n-a fost mecanică*.
- **ce a scos reluarea**: condiția e scrisă ca **execuție**, nu ca decizie, dar conține în ea **două** variante — *„refuză (sau cere trecere explicită, consemnată)”* — iar alegerea dintre ele e o hotărâre de produs, nu una tehnică. Un refuz pe o perioadă închisă e o poartă; o *trecere explicită consemnată* e un act cu urmă, ca redeschiderea de perioadă din R58. N-am ales-o eu: schimbarea atinge ce declarații se datorează, deci e decizia lui Costin. **Rămâne DESCHISĂ, cu contorul crescut**, cum cere regula: *dacă reluarea a avut loc și n-a mers, contorul crește oricum*.
- **APLICAT 26.08.2026 — REFUZ, decizia lui Costin.** *„O schimbare de date fiscale ale firmei într-o perioadă închisă nu e o corecție, e o rescriere a trecutului. Iar datele acelea decid ce declarații s-au datorat pentru perioada aceea — declarații care s-au depus deja.”* De ce **nu** trecere consemnată, deși R58 a ales invers pentru redeschidere: *„acolo omul ia o decizie despre perioadă. Aici ar lua o decizie despre trecut fără să redeschidă nimic, iar urma ar rămâne singura care știe.”* Calea corectă rămâne deschisă și e mai bună: **redeschide (cu motiv) → schimbă → închide la loc**, trei acte consemnate în loc de unul tăcut — iar refuzul o spune, ca P3.
- **unde s-a pus poarta**: `firma_profil_api.cere_perioade_deschise`, un loc unic, chemat din **cele trei** căi care ating câmpuri ce decid — `vector_fiscal_api.salveaza` (vectorul), ruta `POST /firma-profil/regim-tva` (regimul), și `salveaza_date` (CUI-ul). Gard: `core/test_regim_peste_perioada_inchisa.py`, 5 teste, cu calibrare pe o cale care scrie fără poartă.
- **MĂSURAT care câmpuri decid, cum a cerut Costin — și măsurătoarea e un PLAFON, nu răspunsul.** Din cele **16** din `CAMPURI_FISCALE`, **14** sunt citite de generatoarele de declarații (doar `patron_nume` și `reg_com` nu). Dar *citit de un generator* nu înseamnă *decide ce se datorează*: `telefon`, `adresa`, `judet` ajung în **antetul** formularului. Criteriul l-a dat el — *„vectorul, regimul, CUI-ul. Nu telefonul sau adresa de corespondență.”* — iar aplicarea lui scoate un lucru care nu se vedea: **vectorul și regimul nu sunt în `CAMPURI_FISCALE`**. Trăiesc pe rutele lor (`regim_fiscal`, `platitor_tva`, `tip_decont`, `operatiuni_ic`, `inreg_art317`), scrise de `vector_fiscal_api`. Din `CAMPURI_FISCALE` rămâne **unul singur**: `cui`. De aceea `CAMPURI_CARE_DECID = ("cui",)`, iar gardul verifică să nu se lărgească tăcut peste `CAMPURI_FISCALE` și nici să nu se golească.
- **limitarea, care e jumătate din valoare**: refuzul se aplică **doar** câmpurilor care decid. *„Altfel un contabil nu mai poate corecta un număr de telefon pe o firmă cu ianuarie închis.”*
- **ce NU acoperă poarta, declarat**: a doua jumătate a condiției — *declarații depuse pe regimul vechi în intervalul atins*. Poarta de azi e pe **perioada închisă**, care e proxy-ul mecanic; o declarație depusă pe o lună care **nu** e închisă rămâne neacoperită. Scris și în antetul gardului.
- **condiția de deblocare**: la primul commit care atinge `core/firma_profil_api.py`, schimbarea de regim refuză (sau cere trecere explicită, consemnată) când perioada afectată e închisă sau când există declarații depuse pe regimul vechi în intervalul atins. Se închide când refuzul există și e probat prin mutație.

### R47 — NIR-ul creează nota contabilă direct validată, sărind peste ciornă

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE X.3 · legată de **R36** · **PRAG 3**
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `3cb6c44`
- **măsurat la**: 2026-08-25 · **pe commit**: `3cb6c44`
- **ce blochează**: `stocuri_api` pune starea `validata` pe nota creată la recepție. **Toate celelalte căi de creare de notă pun `ciorna`.** Nu spun că e greșit — spun că e **o excepție netratată nicăieri**: dacă modelul ales la **R36** e „aplicația propune, omul validează", recepția îl încalcă deja, iar dacă modelul e altul, atunci celelalte căi sunt cele care trebuie schimbate. Ca și R46, constatarea e din 24.08 și n-a avut loc cu stare până azi.
- **condiția de deblocare**: se răspunde la **R36**, apoi NIR-ul se aliniază modelului ales (sau excepția se scrie ca excepție, cu motivul). Se închide când starea pusă de `stocuri_api` e aceeași cu cea a celorlalte căi **sau** când abaterea e declarată în `DECIZII.md`.

### R48 — Patru trasee nu se pot exercita pe nicio firmă, și nimic din afară nu le blochează

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E1 · TRASEE XI.4 · interdicția 19 · **PRAG 3**
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `3cb6c44`
- **măsurat la**: 2026-08-25 · **pe commit**: `3cb6c44`
- **ce blochează**: măsurat pe toate cele 17 firme, pe numele **reale** ale tabelelor. **Șase** trasee n-au nicio firmă care să le poată exercita azi; **două** au o cauză din afară (T06 e-Factura și T27 e-Transport — `public.spv_token` = 0, deci lipsește certificatul), iar **patru n-au niciun blocaj: pur și simplu nimeni n-a introdus date** — **T08 NIR** (`nir` = 0), **T16 pontajul** (`pontaj` = 0), **T19 scadențarul** (`notificari_scadenta` = 0), **T32 partida simplă** (`rip_operatiuni` = 0). Toate patru, zero pe toate cele 17.
- **de ce contează, cu instanța**: (a) Partea III scrie că *„pontajul trebuie să existe — fără el calculul stă pe zile presupuse"*; cele două state de plată emise, pe `tenant_003`, poartă `zile_lucrate = 21` — **o lună întreagă presupusă** — iar tabela `pontaj` a firmei e goală. (b) partida simplă are motor scris (`rip_api` + `d212_engine`) și **zero probe pe date**, deși e una dintre datoriile numite la pragul 3. (c) NIR-ul e traseul din care a ieșit **R47**, iar constatarea aia n-a putut fi confruntată cu date reale.
- **de ce e o restanță și nu o notă**: orice verificare care atinge cele patru trasee întoarce azi **zero dintr-un motiv care nu se poate deosebi mecanic de „totul e în regulă"** — interdicția 19, produsă de date, nu de instrument.
- **condiția de deblocare**: se introduc date pe cele patru trasee, pe firmele care le potrivesc, și se parcurge fiecare până la ieșirea lui. Se închide când `scripts/scan_trasee.py --db` raportează cel puțin o firmă pentru T08, T16, T19 și T32.

### R49 — Avertismentul de prăpastie al salariului minim, desprins din R30

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E5 · triaj · **PRAG 2** *(o protecție care exista nu mai există)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `61b1af3`
- **DECIZIA, 25.08.2026 (Costin): varianta (c) — cu cifre, calculate cu toate elementele.**
  *„Contabilul care mărește un salariu cu 100 de lei are nevoie să vadă CÂT pierde salariatul, nu că pierde. «Se pierde facilitatea» e adevărat și inutil: el știe regula, vrea suma."* Plus condiția: *dacă cifrele nu se pot calcula cu toate elementele în momentul acela, atunci (b), și spui de ce nu se poate.*
- **(c) A FOST POSIBILĂ, și verificarea contează**: R28 scosese varianta veche fiindcă pasa **doi** din cei optsprezece parametri ai lui `salarizare.calcul_salariu` — restul luau valorile implicite. Am citit formularul de angajare înainte de a alege: colectează **persoane în întreținere · data nașterii · copii școlarizați · declarația părintelui · tipul de normă · orele/zi · județul · data angajării · scutirea de contribuția minimă · tichetul de masă**. **Nu lipseau datele — lipsea pasarea lor.** Deci nu s-a căzut pe (b).
- **cum arată, măsurat pe 2026-08-01** (prag 4.325 lei, HG 146/2026): la **4.326** lei brut, netul e **2.617,21** față de **2.699,63** la prag — **82,42 lei** mai puțin — iar netul redevine cel de la minim abia de la **4.478** lei brut. *Exact cifra pe care o cerea decizia: cât, nu că.*
- **unde se calculează**: `core/prapastie_salariu.py`, funcție pură; ecranul trimite elementele și afișează ce întoarce serverul (P3 — nicio regulă fiscală în prezentare). Apare **înainte de buton** (DS cap. 6, ghidaj preventiv), și dispare când nu se aplică.
- **trei gărzi au căzut pe modulul nou, și toate trei aveau dreptate**: capătul de sus al căutării era un `1.6` **inventat de mine** — registrul are deja `plafon_facilitate_salariu_minim` = 4.600 (OUG 89/2025 art. III alin. (1) lit. b), adică chiar plafonul peste care facilitatea nu se mai aplică; iar motivele neaplicării erau **proză într-un dicționar** (afirmații netipate, decizia din 21.08) — au devenit **coduri dintr-un vocabular închis**, cu textul compus de ecran.
- **gardat**: `core/test_prapastie_salariu.py`, 10 teste, din care unul e chiar motivul lui R28 — *cifra trebuie să se schimbe cu elementele salariatului*; dacă două persoane în întreținere nu schimbă netul, funcția calculează pe un salariat implicit.
- **deschisă pe commit**: `9b3bf41`
- **de ce a fost o restanță proprie**: era **a doua jumătate a lui R30**, care avea două subiecte cu două condiții de închidere diferite — și de aia n-a putut fi închisă **29 de commituri**. Costin a decis pe 25.08.2026 jumătatea „verde scris, nu derivat" (MĂSURAT ȘI ACCEPTAT, reluare la grupul 4); jumătatea asta n-a fost atinsă de decizia aia. A o închide odată cu R30 ar fi însemnat să aleg singur varianta (a), *«nu se întoarce»* — exact alegerea pe care condiția o interzice. *Regula, în cuvintele lui: „o restanță care așteaptă 29 de commituri fără să se poată închide n-are condiția scrisă bine."*
- **ce blochează**: **Decizie cerută [atunci].** R28 a scos blocul de estimare de pe ecranul de angajare, iar în același bloc trăia și avertismentul că **la un leu peste salariul minim se stinge facilitatea și netul SCADE** (OUG 156/2024 art. LXVI / OUG 89/2025 art. III), cu brutul de la care netul redevine cel de la minim. Nu era o estimare de confort — era o **prăpastie** pe care un contabil o poate călca fără s-o vadă, iar ecranul o arăta **înainte de buton** (`DS` cap. 6). A plecat colateral, și e corect că a plecat **așa cum era**: textul lui conținea **două cifre de net**, calculate cu aceleași valori implicite care au invalidat estimarea.
- **condiția de deblocare**: se alege una și se scrie de ce. **(a)** Nu se întoarce — prăpastia se semnalează la salvare, de server, unde toate elementele sunt cunoscute. **(b)** Se întoarce **fără nicio cifră**: *«brutul introdus e peste salariul minim — se pierde facilitatea de scutire»*. E o afirmație de **drept**, adevărată pentru oricine, independentă de persoane în întreținere sau de normă, deci nu poate contrazice fluturașul. **(c)** Se întoarce cu cifre, dar calculate cu **toate** elementele salariatului. Se închide când e scris **care** și **de ce**. *Nu se începe fără decizie: (b) pare evident ieftin, dar a alege singur ce spune un ecran e chiar ce s-a cerut să nu fac.*

### R50 — Ștergerea unui cabinet nu curăță tabelele partajate, iar datele lui rămân în ele

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E4 · P17 · interdicția 39 · **PRAG 2** *(cauză unică, dovedită, nu concurează cu nimic)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `3391371`
- **deschisă pe commit**: `91b77ec`
- **măsurat la**: 2026-08-25 · **pe commit**: `dcf5c25`
- **ce blochează**: `core/gdpr_sterge.executa` se numește *„ștergere completă cabinet"* și face `DROP SCHEMA CASCADE` pe fiecare firmă, plus `DELETE` din `audit_log`, `user_tenants`, `tenants`, `users`, `accounting_firms`. **Nu atinge `public.declaratii_coada` și `public.declaratii_depuse`** — două tabele partajate, cheiate pe `tenant_id`. Ce rămâne în urmă nu e o referință goală: `payload`-ul unei declarații conține **CUI-ul, denumirea, adresa, contul bancar al firmei și numele și prenumele declarantului**. Verificat pe rândul 2020, șters azi: toate erau acolo, la zece zile după ce firma dispăruse.
- **de ce e mai mult decât un orfan**: e mecanismul care a produs R44 și îl va produce din nou. Iar pe latura de retenție, o ștergere care se declară completă și lasă date personale în urmă e chiar interdicția **39** citită invers — nu „s-a șters ce trebuia păstrat", ci „n-a fost șters ce trebuia șters".
- **ce NU se afirmă**: **nu se știe dacă firma 13245 a fost ștearsă prin calea asta.** Dacă ar fi fost, `audit_log` s-ar fi golit de rândurile ei — și cele 21 sunt încă acolo. Deci calea ei rămâne necunoscută; gaura din `gdpr_sterge` e dovedită **prin citirea codului**, independent de cazul ăla.
- **măsurat pe TOATE tabelele partajate (25.08.2026)**: din cele **12** tabele din `public` care poartă `tenant_id`, două au orfani — `audit_log` **65** de rânduri și `alerte_control_emise` **2**. `declaratii_coada` și `declaratii_depuse` sunt curate acum. **Firmele-fantomă sunt două: 13245 și 14963.**
- **CIFRELE, ca date, nu ca text** *(cerute explicit — „nu apar nicăieri ca restanță cu cifră")*, **măsurat la 2026-08-25, pe commit `c9b9c8f`**:

  | firmă | folosită | rânduri de audit rămase | din care scrieri | alte urme |
  |---|---|---|---|---|
  | **13245** | 15.08, 15:21–17:41 | **21** | 1 | `alerte_control_emise`: **2** |
  | **14963** | 16.08, 12:38–18:26 | **44** | **21** | — |
  | **total orfani** | — | **65** | — | **2** |

  Cele 44 de rânduri de pe 14963 sunt **tot ce a mai rămas din firma aia**. Nu e o urmă tehnică: e evidența că a fost lucrată, fără nimic din ce s-a lucrat.
- **REMĂSURAT 27.08.2026, și clasa A CRESCUT peste noapte** *(pe commit `3fb126e`, numai SELECT)*: nu **12** tabele din `public` cu `tenant_id`, ci **13**. Al treisprezecelea e `public.schimbari_email`, creat ieri la 13:34 (`70b20f9`, reparația punctului (1) din R62) — și **nu e nici el în `gdpr_sterge`**. Asta e partea care contează mai mult decât cifra: **lista se lungește la fiecare funcționalitate nouă, iar calea de ștergere nu se uită la ea.** `gdpr_sterge.executa` atinge **2 din 13** (`audit_log`, `user_tenants`) și apoi face `DELETE FROM public.tenants`; celelalte **11** rămân.
- **ȘI DOUĂ DINTRE ELE AR OPRI ȘTERGEREA LA MIJLOC**, ceea ce e mai rău decât să lase urme: din cele 13, doar **3** au cheie străină pe `tenant_id` — `user_tenants` cu **ON DELETE CASCADE**, iar `anunturi_cabinet` și `solicitari_client` cu **ON DELETE NO ACTION**. În ziua în care un cabinet are un anunț sau o solicitare de client, `DELETE FROM public.tenants` **eșuează cu violare de cheie străină**, după ce `DROP SCHEMA CASCADE` a rulat deja pe firmele lui. Azi nu lovește fiindcă amândouă au **0** rânduri — deci calea n-a fost niciodată exercitată pe un caz cu conținut, exact ca la instanța din jurnalul PostgreSQL de mai jos.
- **restul de 10 n-au nicio cheie străină**: `alerte_control_emise`, `audit_log`, `declaratii_coada`, `declaratii_depuse`, `pachet_povestea`, `reges_chei`, `reges_mesaje`, `schimbari_email`, `spv_token`, `urme_portal`. Nimic nu le leagă, deci nimic nu le-ar opri să rămână în urmă. **Lista completă, cu rânduri și indecși, e în R72** — acolo a fost cerută ca pas 1 al căii de ștergere a unei firme.
- **CORECTURĂ LA CE AM SCRIS IERI, din jurnalul PostgreSQL.** Scrisesem că *„niciuna n-a fost ștearsă prin aplicație"*, pe temeiul că `public.gdpr_stergeri` e gol. **Jurnalul serverului arată altceva**, iar el nu putea fi citit din bază:

  ```
  2026-08-16 14:01:32.857  ERROR:  cannot delete from view "declaratii_depuse_curente"
  2026-08-16 14:01:32.859  ERROR:  current transaction is aborted, commands ignored…
  2026-08-16 14:01:32.859  STATEMENT: DELETE FROM public.tenants WHERE accounting_firm_id=9977
  ```

  **O ștergere de cabinet a rulat ca `iconta_user`** — utilizatorul aplicației — pe 16.08 la 14:01, și a **eșuat**: a încercat `DELETE` pe **`declaratii_depuse_curente`, care e un VIEW**, PostgreSQL a refuzat, iar **toate** instrucțiunile de după au fost ignorate, inclusiv ștergerea firmei. De-aia jurnalul `gdpr_stergeri` e gol: `INSERT`-ul lui era în aceeași tranzacție.
- **Dar codul care a rulat atunci NU e `gdpr_sterge` de azi**: șterge din tabele pe care versiunea actuală nu le atinge (`notificari`, `pachet_povestea`, `reges_mesaje`, `reges_chei`, `anunturi_cabinet`, `tokene_activare`, `invitatii_cont`, `raportari`, **`declaratii_coada`**, **`declaratii_depuse`**), iar `gdpr_sterge.py` are doar **două** commituri în tot istoricul. Forma lui — o măturare peste toate tabelele cu `tenant_id` — arată a **script ad-hoc care enumeră `information_schema`**, și de aia a lovit view-ul.
- **Concluzia, mai îngustă și mai fermă decât ieri**: firme se șterg cu **SQL ad-hoc rulat ca utilizatorul aplicației**, cel puțin o dată eșuat la jumătate. Nu se poate spune care rulare a scos 13245 și 14963 — jurnalul de atunci privește cabinetul **9977** / tenantul **15133**, care **nu** mai are niciun rând orfan.
- **și o capcană pe care am călcat-o și eu**: propria mea căutare de orfani a enumerat `declaratii_depuse_curente` printre „tabelele cu `tenant_id`" — **același view**. Pe o citire n-a stricat nimic; pe o ștergere ar fi produs exact eroarea din jurnal. *Orice măturare care enumeră `information_schema` trebuie să ceară `table_type='BASE TABLE'`.*
- **ce înseamnă asta pentru restanță**: gaura din `gdpr_sterge` rămâne dovedită **prin citirea codului** și va produce aceiași orfani la prima ștergere reală; dar cauza celor două de azi e **în afara codului**, deci R50 nu le poate preveni retroactiv. *Se scrie așa ca să nu pară că reparația lui `gdpr_sterge` explică tot ce s-a găsit.*
- **REZOLVATĂ 27.08.2026, pe cele trei puncte ale condiției** *(prin `core/tenant_stergere.py`, construit pentru R72 — aceeași cale, nu una paralelă)*:
  - **(a)** `executa` șterge din **toate cele 13** tabele cu `tenant_id`, nu doar din `declaratii_coada` și `declaratii_depuse`. Nu mai are listă proprie: cheamă `tenant_stergere.sterge` pentru fiecare firmă.
  - **(b)** **nu mai enumeră deloc** `information_schema` la ștergere — lista e fixă și declarată; enumerarea trăiește doar în **gardă**, unde cere explicit `table_type='BASE TABLE'`. Deci view-ul din jurnalul PostgreSQL nu mai poate fi lovit, nici azi, nici de o măturare viitoare.
  - **(c)** `previzualizare` întoarce `randuri_de_sters` — câte rânduri dispar din fiecare tabelă, **înainte** de apăsare — și pe firmă, și pe cabinet. Măsurat pe cabinetul 1968: `audit_log 6.618 · user_tenants 18 · alerte_control_emise 6 · urme_portal 4 · declaratii_coada 2 · declaratii_depuse 2 · schimbari_email 1`.
- **PROBAT PE O SCHEMĂ EFEMERĂ**, cum cerea condiția: un cabinet sintetic cu două firme, dintre care una cu o `solicitare_client`. Calea **veche**, rulată într-un `SAVEPOINT`, **eșuează** cu `solicitari_client_tenant_id_fkey` — **după** `DROP SCHEMA`. Calea nouă curăță tot și lasă câte o urmă în `firme_scoase` per firmă. Curățat după probă.
- **ce rămâne dincolo de restanță, și se spune**: cei **67** de orfani vechi (13245, 14963) **nu** se repară de aici — n-au tenant, deci nu se pot scoate pe firmă. Cauza lor e în afara codului (SQL ad-hoc), cum scrie mai sus.
- **condiția de deblocare**: *(cea de atunci)* la primul commit care atinge `core/gdpr_sterge.py`, `executa` (a) șterge și din `declaratii_coada` și `declaratii_depuse`, (b) enumeră numai `BASE TABLE`, (c) previzualizarea numără rândurile. **Toate trei, îndeplinite.**

### R51 — Data încetării contractului nu ajungea în bază, iar ruta răspundea 200

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E5 · interdicția 32 · **PRAG 1** *(contabilul completează data plecării, primește confirmare, iar salariatul rămâne în serviciu — deci continuă să apară în D112)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `c9d1724`
- **deschisă pe commit**: `8a25308`
- **măsurat la**: 2026-08-25 · **pe commit**: `8a25308`
- **ce blochează**: *(istoric — rezolvat)* ecranul de salariați are un dialog dedicat pentru data încetării, cu textul lui explicit — *„Gol = contract activ. La plecare NU se șterge salariatul — se completează data încetării (istoricul susține declarațiile depuse)"* — și trimite `{ data_incetare }` pe `PUT /tenants/{}/salariati/{}`. **`SalariatEdit` n-avea câmpul.** Pydantic îl arunca **înainte** ca ruta să-l vadă, deci `actualizeaza_salariat` nu primea nimic și întorcea `{"ok": true, "neschimbat": true}`. Probat pe ruta reală: **200**, coloana rămâne `NULL`.
- **de ce e prag 1**: `salariati_api` susține câmpul pe **tot restul drumului** — e în `_CAMPURI_API`, e validat contra `data_angajare`, iar *„în serviciu"* e **definit** prin el. Ștergerea salariatului e refuzată tocmai ca să se folosească data încetării. Deci **singura cale corectă era cea care nu funcționa**, iar rezultatul e un salariat plecat care rămâne în D112 — fără niciun semn pe ecran.
- **a doua jumătate, care nu se rezolva doar adăugând câmpul**: ecranul trimite `null` pentru *„gol = contract activ"*, iar `actualizeaza_salariat` filtra `v is not None` — deci `null` însemna **„netrimis"**, nu **„golește"**. O dată pusă din greșeală n-ar mai fi putut fi scoasă. Ruta calculează acum ce chei au fost **efectiv trimise** (`exclude_unset`) și le trece mai departe ca golire cerută; apelanții vechi nu-și schimbă comportamentul. *E aceeași formă cu interdicția 32, în oglindă: acolo un necunoscut se rotunjea la „știu că nu"; aici două lucruri diferite împărțeau aceeași valoare.*
- **cum s-a probat**, pe procesul viu, după repornire (METODA §24): `{"data_incetare": "2026-08-31"}` → 200 și coloana devine `2026-08-31`; `{"data_incetare": null}` → 200 și coloana revine la `NULL`. Restaurat la starea inițială, verificat.
- **cum a ieșit**: `scripts/scan_contract_ecran.py`, instrument nou — compară cheile trimise de fiecare `api.post/put` din `static/js` cu câmpurile modelului rutei. **67 de perechi, 1 diferență, după reparație 0.** Gardat de `core/test_contract_ecran_ruta.py`, cu anti-vacuu pe domeniu.
- **condiția de deblocare**: *(îndeplinită)* câmpul ajunge în bază la trimitere și se poate goli la cerere, probat pe procesul viu; iar clasa întreagă e păzită — clichetul de contracte rupte din `core/test_contract_ecran_ruta.py` e **0** și nu poate crește tăcut.

### R52 — Un document care ajunge la un om poate pleca pe un GET, iar acolo nu se verifică niciun rol

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE XI.2 · P12 · **PRAG 3** *(nimic fals pe ecran; lipsește o restricție, iar instalarea n-are al doilea actor care s-o exercite)*
- **reluări**: 0
- **deschisă pe commit**: `c9d1724`
- **măsurat la**: 2026-08-25 · **pe commit**: `8a25308`
- **ce blochează**: **punctul orb al tuturor măsurătorilor mele de rol.** Am numărat de fiecare dată **rutele care schimbă date** — 229, apoi 131 fără rol. Dar *„iese către un om"* nu e totuna cu *„scrie ceva"*: un document poate pleca pe un **GET**. Măsurat pe corpul rutelor (Content-Disposition, `application/pdf`, `FileResponse`), nu pe nume: **25** de rute predau un document, **17** fără niciun rol, **toate GET**. Scăzând cele 8 pagini publice (`/`, ghid, robots, sitemap, termeni, pagina de plată), rămân **9 documente ale firmei**:
  `chitante/{}/pdf` · `facturi/{}/pdf` · `facturi/{}/export-saga` · `documente/balanta` · `d406-active` · `d406-stocuri` · `bonuri/{}/imagine/{n}` · `portal/bon/{}/imagine/{n}` · **`fluturas/{salariat_id}`**.
- **cel mai ascuțit e ultimul**: fluturașul unui salariat se ia cu un `GET`, de orice utilizator al cabinetului, fără nicio verificare de rol. E documentul cu cele mai personale date din aplicație.
- **de ce e o restanță separată de R42**: R42 e despre acte (POST/PUT/DELETE) și criteriul lui e „ce se poate reface". Aici nu se reface nimic — se **citește**. Criteriul lui Costin (*„tot ce iese către o autoritate sau către un om"*) le prinde, dar decizia de rol pe **citiri** n-a fost luată, iar a o lua singur ar bloca asistenții pe munca lor zilnică (un asistent trebuie să poată deschide un PDF de factură).
- **DECIZIA, 25.08.2026 (Costin)**: *„Tot ce poartă date ale unui terț — deci trei: fluturașul, chitanța, imaginile de bon. Criteriul nu e «e document predat», ci «conține date despre cineva care nu e firma». Un asistent trebuie să poată deschide un PDF de factură; un fluturaș poartă salariul unei persoane."*
- **APLICAT**: `GET /tenants/{}/fluturas/{salariat_id}` · `GET /tenants/{}/chitante/{}/pdf` · `GET /tenants/{}/bonuri/{}/imagine/{n}` — toate trei pe `cere_rol("admin_firma")`. Documentele predate fără rol scad de la **17 la 14**; dintre cele **9 ale firmei**, rămân **6**.
- **ce NU s-a atins, cu motivul**: `GET /portal/bon/{}/imagine/{n}` e ruta **clientului**, care își privește propriul bon prin portal — a-i cere `admin_firma` ar închide portalul. Restul de 5 (`facturi/{}/pdf`, `facturi/{}/export-saga`, `documente/balanta`, `d406-active`, `d406-stocuri`) sunt documente ale **firmei**, nu ale unui terț, deci rămân la asistent prin criteriul dat.
- **condiția de deblocare**: **ÎNDEPLINITĂ (25.08.2026).** clichetul există în `core/test_trasee.py` (`test_clichet_documente_predate_fara_rol`), plus un test care asertează pe nume că **exact cele trei** documente cu date de terț cer rol — clichetul singur ar trece și dacă ele l-ar pierde, atât timp cât totalul nu crește.
- **CONFRUNTAREA CELOR DOUĂ INSTRUMENTE, fiindcă cifrele NU coincid.** Măsurătoarea de mai sus a dat **25** de rute care predau un document, **17** fără rol. Gardul, cu **aceleași marcaje** dar citind doar **corpul rutei**, găsește **18** și **8**. Diferența nu e un progres — e **raza**: măsurătoarea a urmărit și ce livrează modulele chemate, gardul se oprește la rută. Clichetul e pus pe **8**, cifra pe care instrumentul o poate recalcula de fiecare dată; restul până la 17 **nu sunt păzite aici**, și asta se scrie. *Un clichet pe o cifră pe care instrumentul n-o poate reproduce ar fi o amintire, nu o măsurătoare.*
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `187a151`

### R53 — Inventarul de trasee atribuie unei rute tot ce scrie modulul, nu ce scrie ruta

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E1 · TRASEE · **PRAG 2** *(nu produce o cifră greșită la un om — produce o listă de verificat în care 108 rânduri din 192 promit mai mult decât s-a măsurat)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `d0bd859`
- **măsurat la**: 2026-08-26 · **pe commit**: `d0bd859`
- **ce blochează**: `scan_trasee.pasii_ordonati()` compune rândul *„ce face"* din **două** surse care arată la fel în text: SQL-ul găsit în **corpul rutei**, și **reuniunea tabelelor scrise oriunde în fiecare modul** pe care ruta îl atinge. A doua e un **plafon superior**, nu o măsurătoare: altă funcție din același modul poate scrie acolo fără ca ruta asta s-o cheme. **Măsurat pe toate cele 192 de locuri: 65 au scrieri proprii · 108 doar moștenite · 19 niciuna.** Deci **108 din 192** de rânduri păreau măsurate pe rută și erau despre modul.
- **cum a ieșit la iveală**: scriind verificările lotului 1, Costin a observat că *„patru rute de «încărcare» scriu în tabele de date, nu doar în `migrare_status`. Ori previzualizarea salvează, ori inventarul e inexact."* **Citite toate patru la sursă: previzualizarea NU salvează.** `solduri/incarca` și `articole-import/incarca` nu deschid nicio conexiune; `parteneri/incarca` deschide una doar pentru `coerenta(...)`, care citește; `salariati-import/incarca` doar pentru nomenclatorul COR. Docstringurile lor spun *„nu salvează"*, și e adevărat. **Inventarul era inexact.**
- **ce s-a făcut deja**: rândul din lot nu mai amestecă cele două. Ce e măsurat pe rută se scrie `scrie …`; ce e moștenit se scrie **`poate atinge, prin modul (PLAFON, nemăsurat pe rută)`**. **Nu s-a atins** blocul generat din `TRASEE.md` Partea XII — acela e păzit caracter cu caracter, iar schimbarea lui e o măsurătoare separată.
- **restul declarat, completat 26.08.2026 (vezi R60)**: cele două fișiere lăsate atunci neatinse — blocul din `TRASEE.md` Partea XII și adnotările din `TRASEE_VERIFICARI.md` — s-au regenerat, **121 din 192** de rânduri. Iar divergența nu se mai poate întâmpla tăcut: `test_adnotarea_din_TRASEE_VERIFICARI_e_IDENTICA_cu_ce_masoara_instrumentul`. **Cifra de mai sus nu se schimbă** — 65 · 108 · 19, remăsurate azi pe instrumentul reparat: toate cele 14 rute atinse de R60 aveau deja scrieri proprii, deci erau în cele 65. Condiția de deblocare a lui R53 rămâne neatinsă.
- **ce NU vede măsurătoarea**: nu spune care dintre cele 108 sunt **greșite** — spune că sunt **nedovedite**. O rută care deleagă lui `solduri_api.importa` chiar scrie `solduri_initiale`; una care cheamă `extrage_balanta` nu. Diferența cere rezolvarea apelului la nivel de **funcție**, nu de modul — exact modul de eșec **E4** din R33, a doua oară în două zile.
- **condiția de deblocare**: `scan_trasee` rezolvă, pentru fiecare rută, **ce funcții** ale modulului cheamă, și moștenește doar scrierile acelor funcții. Se închide când numărul de pași „doar moșteniți" pe care instrumentul nu-l poate reduce e **declarat**, nu întâmplător — iar `test_trasee` îl ține clichet.

### R54 — Contul contabil venit din corpul cererii nu e confruntat cu planul de conturi

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · P8 · **PRAG 2** *(azi nicio firmă n-are un cont rupt; dar ecranul de operațiuni are 12 câmpuri de cont în text liber, deci e atingibil de primul contabil)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `d0bd859`
- **planul**: PARȚIAL ACOPERIT. Căutat în `PLAN_ARHITECTURA`: **Partea III, „Categoriile de conținut"** listează explicit **planul de conturi** printre **Nomenclatoare**, iar „Reguli de acces" spune *„Nimeni nu scrie o valoare din aceste categorii în afara registrului"* — deci planul TRANȘEAZĂ că planul de conturi e un nomenclator de registru. Ce **nu** spune e ce se întâmplă când un om introduce un cont din afara lui: **interdicția 16** („nomenclator derivat dintr-o sursă secundară") și **28** („denumire de nomenclator scrisă ca literal în cod") privesc cum se CONSTRUIEȘTE nomenclatorul, nu cum se VALIDEAZĂ o intrare contra lui; **interdicția 45** (P20 — „o valoare intrată din afară, fără sursă și grad de certitudine") e cea mai apropiată și tot nu răspunde: cere proveniență, nu apartenență. Alegerea refuz-vs-semnal rămâne decizie (P11). (METODA §25)
- **măsurat la**: 2026-08-26 · **pe commit**: `d0bd859`
- **ce blochează**: măsurat pe AST, pe cele **52 de situri** de scriere în `inregistrari_linii` (41 în `main.py`, 11 în `core/`): **3** au conturile fixate în SQL, **49** le iau din expresii. Dintre cele care iau contul **din corpul cererii**, tiparul dominant era `str(corp.get("cont_x") or "<implicit>")` — care **pare o gardă și e o mască**: `or` transformă `None` și `""` în implicit, dar lasă `"   "` să treacă **verbatim**. **Șirul gol propriu-zis NU e atingibil** (fiecare cale ori îl refuză explicit, ori îl convertește în implicit) — deci un `CHECK (cont <> '')` ar fi fost exact *„o centură pe o gaură teoretică"*, cum a spus Costin. **Spațiul alb ERA atingibil, în 19 situri**, și e strict mai rău: `NOT NULL` nu-l oprește, un `CHECK` pe șirul gol nu-l oprește, iar până azi **nicio verificare de echilibru nu-l vedea** (probat pe schemă efemeră).
- **ce s-a reparat**: toate **19** situri normalizate cu tiparul deja corect din același cod — `(str(corp.get("x") or "").strip() or "<implicit>")`. Gardă structurală (pe AST, nu pe text): `core/test_cont_din_corp_normalizat.py`, cu clichet **gol** și calibrare pozitivă pe propriul mod de eșec. RED-probată printr-un sit repus în forma mascată.
- **ce RĂMÂNE, și e decizia**: normalizarea oprește contul **alb**, nu contul **greșit**. `"7O7"` cu litera O, sau `"9999"` care nu există în planul firmei, trec neatinse. Confruntarea cu `plan_conturi` e o **decizie de produs**: se **refuză** cererea (și atunci un cont nou trebuie întâi creat), sau se **semnalează** și se scrie? Ambele schimbă ce poate face contabilul pe ecranul de operațiuni, unde sunt **12 câmpuri de cont în text liber**.
- **DECIZIA (Costin, 26.08.2026): SE REFUZĂ.** *„O notă cu cont inexistent nu e evidență, e un rând care arată ca evidență. Nu se poate depune, nu se poate desface la control, iar contabilul află abia când generează ceva."* Argumentul contrar — că blochează un contabil care lucrează repede — *„se rezolvă altfel: dacă vrea un cont nou, îl creează în plan. Aia e o operațiune de câteva secunde și e chiar decizia pe care ar trebui s-o ia conștient."*
- **APLICAT.** `core/cont_valid.py` — un singur loc: `normalizeaza` (curăță) + `exista` (citește planul firmei) + `apropiate` (conturi vecine, ca refuzul să poată sugera) + `cere_cont` (refuză, cu mesajul cerut). Probat pe `tenant_013`: `707` → trece · `7O7` → *„Contul 7O7 nu există în planul firmei (cont_venit). Îl adaugi din Plan de conturi (Import date › Plan de conturi), apoi reia operațiunea."* · `9999` → la fel · `"   "` și `None` → *„cont_venit este obligatoriu"*. Pe `7O7` **nu apar conturi apropiate**, și asta e informație: nu e o greșeală de o cifră, e alt caracter.
- **CÂT S-A LEGAT: 19 din 27 de citiri de cont din corpul cererii.** Toate rutele care scriu în evidența contabilă cu un cont venit de la om: cele cinci regimuri speciale, achiziția de la neînregistrat, importul și exportul extracomunitar, leasingul, lichidarea, inventarierea, perisabilitățile, provizioanele, subvenția, decontarea în valută.
- **CE A CORECTAT MĂSURĂTOAREA ÎN PROPRIA MEA PROZĂ:** eram gata să scriu în clichet, pentru jumătate dintre ele, motivul *„modul pur, fără conn/schema"*. **E fals** — la `nota_leasing` și la surorile ei `conn` și `schema` sunt în domeniu, iar expresia e în `try` care prinde `ValueError`. Singurul lucru care le ținea nelegate era **forma patch-ului meu**, nu codul. Verificat la sursă înainte de a scrie motivul; s-au legat toate.
- **CE RĂMÂNE, cu motivul citit pentru fiecare (8):** `factura_primita_valideaza` (citirea e înainte de `with db.get_conn()`, deci n-are nici conn, nici `try`) · `firma_profil_api.salveaza_date` (e o **preferință** de profil, nu un cont dintr-o notă; se confruntă la folosire) · `inventariere.pregateste_mf_plus` ×2 (modul **pur**, verificat: nu primește conn/schema) · `stocuri_cv_api.intrare` ×2 (contul intră în `articole` ca implicit al articolului, nu într-o linie de înregistrare) · `stocuri_cv_api.reclasificare` ×2 (refuzurile modulului sunt **dict**, nu ridicate — legarea cere întâi un singur fel de refuz).
- **gardat**: `core/test_cont_din_corp_normalizat.py` — 8 teste. Clichetul e ancorat pe **fișier + FUNCȚIE + expresie**, nu pe linie (liniile se mută la orice editare, deci un clichet pe ele ar pica din alt motiv decât cel păzit) și e **bidirecțional**: pică și când apare o citire neconfruntată, și când una din clichet s-a legat între timp. Plus: refuzul e verificat că **numește contul, câmpul și unde se creează**.
- **regula intră și în plan**, cum ai cerut: `PLAN_ARHITECTURA.md` Partea III, „Reguli de acces" — *„o intrare din AFARA unui nomenclator de registru se REFUZĂ, nu se semnalează"*, cu motivul și cu cerința ca refuzul să numească intrarea și locul unde se creează.
- **condiția de deblocare**: cele **8** rămase se leagă, sau primesc o declarație scrisă de ce rămân. Se închide când `NELEGATE` din `core/test_cont_din_corp_normalizat.py` e gol sau conține doar intrări cu decizie scrisă.

### R55 — Aceeași clasă de operațiune contabilă, roluri diferite, fără motiv scris

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T29 · P12 · **PRAG 2** *(nu produce o cifră greșită; produce o restricție care se aplică inconsecvent)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `e47b60e`
- **rezolvată pe commit**: `19db8b0`
- **măsurat la**: 2026-08-26 *(remăsurat în aceeași zi, pe domeniul corect)* · **pe commit**: `d681e1e`
- **planul**: NEACOPERIT. `PLAN_ARHITECTURA` are **P12** (drepturile se verifică în interogare, nu doar în interfață) și **interdicția 25** (un drept verificat numai în interfață), dar amândouă spun *cum* se verifică un drept, nu **care operațiune cere care rol**. Planul nu repartizează operațiuni pe roluri — aceeași constatare ca la R42. (METODA §25)
- **ce blochează**: găsit de Costin scriind verificările lotului 2, apoi măsurat la sursă.

  **CIFRA DIN PRIMA VERSIUNE ERA GREȘITĂ, și corectura e instructivă.** Am scris *„șapte rute, șase fără rol, una cu"* — pentru că îmi luasem domeniul din **numele traseului** („regimuri speciale de TVA"), nu din cod. Lotul 3, care poartă acum și garda pe fiecare pas, a arătat imediat că familia e mai mare: `import-extracomunitar` și `export-extracomunitar` scriu tot în `inregistrari_linii` și sunt tot fără rol.

  **Măsurat pe criteriul mecanic — rute care scriu în `inregistrari_linii` ÎN CORPUL LOR, adică direct în evidența contabilă: 40. Dintre ele 36 fără niciun rol, 4 cu `admin_firma`.**

  **Și există un tipar, contrar a ce am scris prima dată.** Cele 4 cu rol sunt **toate** `achizitie-*`:
  `achizitie-ic` · `achizitie-necorporala` · `achizitie-neinregistrat` · `achizitie-taxare-inversa`.
  Deci regula de fapt e *„achizițiile cer `admin_firma`"* — iar **`achizitie-agricultor` e singura excepție de la ea**, a cincea rută `achizitie-*` și singura fără rol.

  | grup | câte | gardă |
  |---|---|---|
  | `achizitie-*` | **4 din 5** | `cere_rol("admin_firma")` |
  | `achizitie-agricultor` | **1** | `cere_cabinet` — **excepția** |
  | tot restul: `vanzare-*`, `nota-*` (18), `reevaluare-*`, `amortizare`, `salarii-contare`, `horeca/*`, `bonuri/{}/aproba`, `facturi/{}/contabilizeaza`, `decontare-valuta` | **35** | `cere_cabinet` — **fără rol** |

- **de ce contează, reformulat**: nu e „nicio regulă", cum am scris. E o **regulă nescrisă care acoperă o cincime din clasă și are deja o excepție**. Asta e mai rău decât absența, fiindcă arată ca intenție: cine adaugă a 41-a rută va copia vecinul, iar vecinul e ales la întâmplare. Și niciuna dintre cele 40 nu e o gaură de acces — toate cer cabinet; ce lipsește e criteriul.
- **DECIZIA (Costin, 26.08.2026): criteriul rămâne cel de la R42, extins — *„ce schimbă ce datorează firma cere `admin_firma`"*. Plus o cerere de măsurătoare înainte de aplicare: *„din cele 36, câte sunt operațiuni curente pe care le face un asistent zilnic? Dacă majoritatea sunt, criteriul e prea larg pentru operațiuni interne."*

- **MĂSURAT, ȘI RĂSPUNSUL E MAI BUN DECÂT ÎNTREBAREA.** Prima măsurătoare, pe proxy-ul „e pe suprafața de lucru": **30 din 36** sunt pe ecranul de operațiuni, deci majoritatea **sunt** muncă zilnică — iar pe testul lui Costin criteriul ar fi fost prea larg. Dar a doua măsurătoare taie altfel, și o face inutilă pe prima: **cu ce STARE intră nota?**

  | stare scrisă | câte | ce înseamnă |
  |---|---|---|
  | `ciorna` | **36 din 40** | **propun**, nu schimbă ce datorează firma. Poarta e la validare |
  | `validata` direct | **3** | **produc evidență**, sărind peste validare |
  | nedeterminat pe AST | 1 | `salarii-contare` — citit la sursă: e `ciorna` (statusul e parametru de la R33) |

  **Deci criteriul nu se aplică celor 36: o ciornă nu schimbă nimic.** Iar cele 4 rute `achizitie-*` care aveau deja rol scriu **tot ciornă** — adică rolul de pe ele e inconsecvent în cealaltă direcție: cer `admin_firma` pentru o propunere, în timp ce 32 de surori nu cer nimic pentru aceeași propunere.

- **APLICAT — lanțul, exact cum l-a numit Costin.** *„Prima instanță de rezolvat nu e una dintre cele 36 — e lanțul `plan-conturi` → `jurnal` → validare. Cine adaugă un cont poate anula orice refuz."*

  | rută | înainte | acum | de ce |
  |---|---|---|---|
  | `POST /plan-conturi` | `cere_context` | **`admin_firma`** | extinde nomenclatorul pe care stă refuzul din R54 |
  | `POST /jurnal/{id}/valideaza` | `cere_cabinet` | **`admin_firma`** | transformă ciorna în evidență |
  | `POST /amortizare` | `cere_cabinet` | **`admin_firma`** | scrie `validata` **direct** |
  | `POST /bonuri/{id}/aproba` | `cere_cabinet` | **`admin_firma`** | idem |
  | `POST /horeca/raport-z` | `cere_cabinet` | **`admin_firma`** | idem |

  **`POST/PUT/DELETE /jurnal` rămân fără rol**, cu motivul citit la sursă: `jurnal_api.editeaza` și `.sterge` refuză orice notă care nu e `ciorna`, iar `creeaza` scrie tot `ciorna`. E munca zilnică a asistentului, și nu atinge evidența.

  **După aplicare: fiecare rută care scrie `validata` direct cere `admin_firma`.** Măsurat, nu declarat.

- **NU E O CLASĂ NOUĂ.** Cele trei care scriau `validata` direct sunt exact bugul pe care **R33 l-a reparat pe 25.08** la nota de salarii — antetul lui `core/salarii_contare.py` îl scrie: *„status='validata' direct — ocolea patru-ochi"*. Trei instanțe rămăseseră nereparate. **Generalizarea pe clasă nu s-a făcut atunci**, iar asta e chiar pasul 2 din ciclul de neconformitate.

- **GARDUL EXISTĂ (26.08.2026): `core/test_rol_pe_efect.py`**, 8 teste, **3 mutații** probate. Rolul se cere după **ce face** ruta, nu după cum se numește: mulțimea rutelor care scriu `validata` direct se **derivă din AST**, nu se citește dintr-o listă (altfel a 41-a rută n-ar fi văzută), iar aserțiunea e pe **mulțime**, nu pe cardinal — un clichet pe număr ar trece la o inversare. Cele **șase moduri de eșec ale gardului** sunt scrise în antetul lui, înaintea primei măsurători, inclusiv cele două pe care nu le închide (rol calculat dinamic; stare scrisă din parametru, cazul `salarii-contare`, pinat cu motivul).
- **condiția de deblocare**: ÎNDEPLINITĂ. **Marcată REZOLVATĂ pe `19db8b0`.** Criteriul e al lui Costin — „ce schimbă ce datorează firma” — iar `core/test_trasee.py` nu mai are nevoie de testul cerut inițial: l-a înlocuit gardul de mai sus, care e pe **efect**, nu pe nume (un clichet pe număr ar trece și dacă s-ar inversa între ele). **Prima instanță de rezolvat, oricare ar fi criteriul: `achizitie-agricultor`**, care rupe singurul tipar existent.

### R56 — Trei rute manipulează credențiale ale unor sisteme externe, fără rol

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T15, T25 · P12 · **PRAG 2** *(niciun cabinet n-are azi al doilea actor care să exercite diferența — vezi R52)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `e47b60e`
- **rezolvată pe commit**: `19db8b0`
- **măsurat la**: 2026-08-26 · **pe commit**: `e47b60e`
- **planul**: NEACOPERIT, la fel ca R55 — planul nu repartizează operațiuni pe roluri. Cel mai aproape e **P12** (izolarea datelor firmei), dar cheile nu sunt *date ale firmei*, sunt **mijloace de acces** la sisteme terțe; distincția nu e scrisă nicăieri. (METODA §25)
- **ce blochează**: observația lui Costin, verbatim: *„Cheile de acces la sisteme externe nu sunt date de firmă — sunt credențiale."*

  **CIFRA MEA ERA GREȘITĂ: sunt DOUĂ rute, nu trei.** `PUT /woocommerce/config` **avea deja** `admin_firma`, aplicat pe 25.08 prin R42 (d) — *„pornirea și oprirea unui canal cer `admin_firma`"* — iar registrul o scrie corect acolo. Am măsurat garda cu un **grep pe CALE**, iar pe aceeași cale există și un `GET` (citirea configurației), care chiar e `cere_context`. **Am citit garda GET-ului și am scris-o în dreptul PUT-ului.**

  **De ce n-a ajuns răspunsul la restanță — verificat, cum a cerut Costin.** Nu registrul a tăcut și nu decizia s-a pierdut: **decizia a ajuns și e aplicată**. Ce n-a ajuns e măsurătoarea mea, iar nimic n-a contrazis-o fiindcă **lotul 2 nu purta garda**. De la lotul 3, o poartă — și tocmai de aceea a cerut-o. Dacă lotul 2 ar fi avut-o, eroarea s-ar fi văzut în aceeași propoziție în care am scris-o.

  Rămân, și au primit `admin_firma` azi: `POST /reges-config` (scrie `reges_chei`) și `POST /reges-poll` (consumă coada REGES).
- **ce NU e**: nu e o scurgere — niciuna nu întoarce cheile în răspuns (verificarea e scrisă la pașii lor în `TRASEE_VERIFICARI.md` și rămâne de exercitat).
- **DECIZIA (Costin, 26.08.2026): `admin_firma`, nu drept fin.** *„Un drept nou e un al doilea sistem de autorizare de întreținut, iar cele trei rute nu justifică unul."* **APLICAT** pe cele două rămase.
- **condiția de deblocare**: ÎNDEPLINITĂ. Decizia e aplicată, iar partea care lipsea — gardul — există: `core/test_rol_pe_efect.py::test_orice_ruta_care_atinge_credentiale_cere_rol` **derivă** mulțimea din cod (rute ne-GET care scriu într-o tabelă de credențiale), cu anti-vacuu propriu, și e RED-probat prin scoaterea rolului de pe `reges-config`. **Marcată REZOLVATĂ pe `19db8b0`.**

### R57 — Calea de API emite facturi fără poarta de gestiune pe care o are ecranul

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T02 · P4 · **PRAG 2** *(`public.api_chei` = 0 — nicio cheie n-a fost creată vreodată, deci efectul n-a fost produs)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `ba72b39`
- **rezolvată pe commit**: `19db8b0`
- **măsurat la**: 2026-08-26 · **pe commit**: `ba72b39`
- **planul**: NEACOPERIT. `PLAN_ARHITECTURA` cere la **P4** ca documentul emis să fie fapt înghețat, și la **Partea V** ca interfața cu exteriorul să aibă componente separate — dar nu spune ce se întâmplă când **aceeași operațiune** are două căi de intrare cu porți diferite. Cel mai aproape e **interdicția 15** („reguli diferite la previzualizare față de salvare"), care e despre același gest în două momente, nu despre același gest pe două căi. (METODA §25)
- **ce blochează**: `POST /api/v1/firme/{id}/facturi` și `POST /tenants/{id}/facturi/emite` cheamă **aceeași** `emite_factura`. Două diferențe erau **defecte și s-au reparat azi** (`platitor_tva` venea din corpul cererii peste faptul din `firma_profil`; numele beneficiarului nu era cerut). A treia **nu e defect, e decizie**: ruta din ecran are poarta *„pleacă marfa acum?"* — care decide dacă se descarcă gestiunea — iar pe o cale neinteractivă nu se poate pune fără să alegem în locul integratorului.
- **ce NU e**: nu e ocolire de rol. `cere_api_key` chiar n-are rol, dar cheia se creează doar prin `POST /cabinet/api-chei`, care cere `admin_firma`: e **delegare explicită**, nu escaladare — un `angajat` nu-și poate face singur cheie. Iar `_api_schema` verifică apartenența firmei la cabinetul cheii.
- **DECIZIA (Costin, 26.08.2026): SE REFUZĂ fără câmp explicit în corp.** *„Cele două căi produc documente diferite din același corp, iar asta e chiar interdicția 15. Un implicit, oricare ar fi, alege în locul integratorului: «descarcă» îl face să descarce gestiunea fără să știe; «nu descarcă» lasă stocul greșit fără să afle. Iar refuzul e ieftin acum: `api_chei` = 0, nimeni nu e afectat. Peste un an, un implicit ales azi ar fi imposibil de schimbat."* Plus cerința de formă: *„câmpul se numește explicit — nu `descarca: bool`, ci ceva care spune ce se întâmplă."*
- **APLICAT.** Câmpul e **`marfa_pleaca_cu_factura`**. Poarta e aceeași ca în ecran (`tip == "factura"` **și** există linie cu `articol_id`), refuzul e **422** cu cod `POARTA_GESTIUNE_FARA_RASPUNS`, numește câmpul și spune ce înseamnă fiecare valoare. La răspuns afirmativ, descărcarea se face în **aceeași tranzacție** cu emiterea, exact ca în ecran — nu într-un al doilea apel al integratorului.
- **condiția de deblocare**: ÎNDEPLINITĂ. **Marcată REZOLVATĂ pe `19db8b0`.** Ce **nu** e închis și se spune: nu există încă un gard care să oprească reapariția unui implicit pe vreo cale nouă de emitere.

### R58 — Închiderea perioadei nu verifică nimic, iar redeschiderea nu lasă urmă

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T11 · P15 · **interdicția 36** · **PRAG 2** *(o singură perioadă e blocată azi pe toate cele 17 firme, deci efectul n-a fost produs — dar e cauză unică, dovedită)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `3c774dc`
- **măsurat la**: 2026-08-26 · **pe commit**: `3c774dc`
- **planul**: **ACOPERIT, și explicit** — spre deosebire de R55/R56. **P15**: *„închiderea e act deliberat, cu autor · editarea devine imposibilă · redeschiderea e act consemnat, cu motiv"*. **Interdicția 36**: *„o redeschidere de perioadă fără motiv consemnat"*. Deci aici nu se cere o decizie despre CE trebuie — planul o spune. Decizia cerută e doar despre **ce anume blochează închiderea**.
- **ce blochează**: găsit de Costin scriind verificările lotului 4 — *„dacă închiderea nu verifică coerența perioadei înainte de a o închide, se închide o lună cu ciorne nevalidate și balanță neechilibrată."* **Verificat la sursă: nu verifică nimic.** `POST /perioade-blocate` face un singur `INSERT (an, luna, blocat_de)`. **Măsurat: dacă s-ar închide luna curentă pe `tenant_013`, ar rămâne 5 ciorne închise înăuntru** (`tenant_003`: 1).
- **ȘI SUNT DOUĂ ACTE DE ÎNCHIDERE, DINTRE CARE DOAR UNUL VERIFICĂ — iar cel care verifică nu e poarta.** `core/inchidere_luna.py` (21.08) verifică un blocaj real (e-Facturi primite și neînregistrate), **refuză motivat**, iar o modificare **de-confirmă automat**; dar scrie în `perioada`, pe domeniul `facturi` — e o **afirmație** despre completitudine. **Poarta care oprește scrierile e `perioade_blocate`**, citită de `_cere_luna_deschisa` la fiecare notă, și aceea nu verifică nimic. *Nu sunt duplicate — sunt obiecte diferite (afirmație vs poartă). Verificat, nu presupus: lecția R33.*
- **REDESCHIDEREA NU LASĂ URMĂ.** `DELETE /perioade-blocate` **șterge rândul**: dispar `blocat_de`, `blocat_la`, și însuși faptul că perioada a fost vreodată închisă. Tabela n-are coloană de motiv (`an, luna, blocat_de, blocat_la` — atât). Asta e **interdicția 36** direct.
- **ce NU vede măsurătoarea**: n-am verificat dacă ecranul cere un motiv înainte de a chema `DELETE` — dacă îl cere, motivul se pierde oricum la server, dar refuzul ar fi altundeva.
- **DECIZIA (Costin, 26.08.2026): se mută pe poartă verificarea care există deja, PLUS ciornele.** *„Perioada nu se închide dacă are ciorne nevalidate, sau dacă `inchidere_luna` ar refuza-o."* Motivul pentru ciorne: *„o ciornă închisă înăuntru nu se mai poate valida, nu se mai poate șterge, și nu apare nicăieri. E o cheltuială sau un venit care dispare fără urmă."* Motivul pentru mutare: *„o verificare care refuză motivat, dar nu oprește scrierile, e o afirmație despre perioadă, nu o poartă."* **Ce a amânat explicit:** echilibrul și orfanii — *„amândouă cer măsurătoare pe ce s-ar bloca azi."*

- **APLICAT, amândouă părțile.**
  **(1) Poarta.** `POST /perioade-blocate` refuză cu **422** (`PERIOADA_NU_SE_POATE_INCHIDE`) dacă perioada are note `ciorna` sau dacă `inchidere_luna.blocaj` întoarce ceva. Refuzul poartă **motivele numite** și unde se rezolvă fiecare. Verificarea de e-Facturi **nu se duplică**: se cheamă exact funcția existentă din 21.08.
  **(2) Urma.** Tabelă nouă `perioade_inchideri` (an, luna, `actiune`, `motiv`, `cine_id`, `cand`), append-only, cu **constrângerea de motiv în BAZĂ** — `CHECK (actiune <> 'redeschisa' OR btrim(coalesce(motiv,'')) <> '')`. `DELETE /perioade-blocate` cere `motiv` și consemnează; s-a adăugat și `GET /perioade-blocate/istoric`, fiindcă o urmă care nu se poate citi e scrisă degeaba.
  **Migrare: 17/17 scheme OK**, plus oglinda în `tenant_template.sql` pentru firmele noi.

- **DE CE O TABELĂ SEPARATĂ, nu coloane pe `perioade_blocate`.** `_cere_luna_deschisa` întreabă `SELECT 1 FROM perioade_blocate WHERE an=%s AND luna=%s` la **fiecare** scriere de notă. Un marcaj de „redeschis" pe același rând ar fi cerut ca poarta să înceapă să-l citească — o schimbare într-un drum cald, pentru o cerință de istoric. Așa: **poarta rămâne neatinsă**, iar urma stă lângă ea. Urma e o evidență, nu o stare.

- **PROBAT pe schemă efemeră** (nu doar pe AST): o ciornă în perioadă → `_ciorne_in_perioada` întoarce 1 · o redeschidere fără motiv → **refuzată de bază**, nu doar de rută · după ștergerea rândului din `perioade_blocate`, urma păstrează **două acte** (închisă de #7, redeschisă de #9 cu motivul). Schema ștearsă la final.

- **condiția de deblocare**: partea (1) — urma — e **ÎNDEPLINITĂ**. Rămâne deschisă pentru ce a amânat Costin: echilibrul și orfanii ca posibile condiții de blocare, după o măsurătoare pe ce s-ar bloca pe firme reale. **Ce NU e păzit încă, și se spune:** nu există un test care să asertea că poarta refuză — azi e o probă funcțională, nu un clichet. Ciorne rămase? Dezechilibru pe `echilibru_perioada`? Orfani? Sau blocajul deja existent din `inchidere_luna`, mutat pe poartă? Se închide când poarta refuză motivat cel puțin pe condiția aleasă, cu gard.

### R59 — Reevaluarea schimbă valoarea contabilă, dar registrul care conduce amortizarea rămâne pe cea veche

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T22 · P6 · **PRAG 2** *(măsurat, nu presupus: **0 note de reevaluare** pe toate cele 17 scheme, pe 3 mijloace fixe active în total — efectul nu e produs azi)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `abc0bc2`
- **măsurat la**: 2026-08-26 · **pe commit**: `abc0bc2`
- **planul**: NEACOPERIT. Am citit `PLAN_ARHITECTURA.md` după *reevaluare*, *amortizare* și *mijloace fixe*: **niciun cuvânt**. Cel mai aproape e **P6** — *verdele afirmă, necunoscutul domină favorabilul* — dar aici nu e un verdict care afirmă prea mult, ci **două înregistrări care spun lucruri diferite despre același activ, iar niciuna nu știe de cealaltă**. Planul nu spune ce se întâmplă când un registru operațional și evidența contabilă divergează prin construcție. (METODA §25)
- **ce blochează**: `POST /reevaluare-imobilizare` **nu atinge `mijloace_fixe`** — citește valoarea și amortizarea cumulată (`SELECT … WHERE id=%s AND activ=true`) și scrie **doar o notă ciornă**. Niciun `UPDATE` pe registru, verificat pe tot corpul rutei. Iar `POST /amortizare` calculează „per MF activ" din **exact acel registru**. Deci după o reevaluare: nota contabilă spune o valoare, registrul spune alta, iar amortizarea lunii următoare se calculează pe cea veche.

  **Nu e o scăpare tăcută** — docstringul o declară: *„actualizeaza valoarea/dnf ramane manual (raport evaluator)"*. Dar o limită declarată **în docstring** nu e o limită declarată **contabilului**: aplicația nu spune nicăieri, la niciun ecran, că baza de amortizare a rămas în urmă.
- **de unde a ieșit**: din măsurătoarea cerută de Costin la lotul 5 — *„reevaluare-imobilizare, care schimbă baza de amortizare (deci impozitul pe profit) dar nu scrie `validata`"*. **Premisa lui era mai bună decât realitatea**: ruta nici măcar nu schimbă baza. Întrebarea era despre rol; răspunsul e despre consistență.
- **ce NU e**: nu e o restanță de rol. Criteriul de la R55 (scrie `validata` direct) n-o prinde, și **corect** — scrie ciornă. Dacă registrul ar începe să fie actualizat aici, ar deveni o schimbare imediată de bază fiscală, iar atunci criteriul s-ar reaplica.
- **condiția de deblocare**: decizia lui Costin între **(a)** ruta actualizează `mijloace_fixe` la validarea notei — reevaluarea devine un act complet, cu riscul că un `UPDATE` pe registru se face dintr-o ciornă; **(b)** ruta rămâne cum e, dar aplicația **spune** divergența — un semnal pe mijlocul fix reevaluat și pe ecranul de amortizare, până la actualizarea manuală; **(c)** altceva. Se închide când divergența ori nu mai există, ori e vizibilă contabilului — cu gard.

### R60 — Instrumentul care hrănește verificările atribuia rutei modulul importat de altcineva

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE (toate cele 35) · METODA §22 · **PRAG 3** *(nimic fals pe ecranul unui om; ce s-a stricat e ce se putea AFIRMA despre cod — iar pe asta s-au scris verificări)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `b86be82`
- **rezolvată pe commit**: `70b20f9`
- **măsurat la**: 2026-08-26 · **pe commit**: `b86be82`
- **planul**: **ACOPERIT pe jumătate, și jumătatea acoperită numește exact cazul.** `PLAN_ARHITECTURA.md`, **interdicția 76** (*„un instrument de măsurare fără calibrare pe propriul mod de eșec”*, P24) și corolarul ei: *„un instrument se calibrează pe felul în care POATE greși — unul **cheiat pe nume** → pe o **coliziune de nume**.”* Instrumentul ăsta e cheiat pe un nume (aliasul `_cv`), iar defectul E o coliziune de nume. Planul spunea deja ce trebuia făcut, iar calibrarea lipsea; s-a construit azi, deci partea asta nu mai cere decizie. **NEACOPERIT** rămâne cealaltă jumătate, și n-am găsit-o nicăieri (citit după *instrument*, *inventar*, *măsurătoare*, *alias*): ce se întâmplă cu **afirmațiile deja scrise pe o măsurătoare care s-a schimbat**. Interdicția 76 apără instrumentul; nu spune nimic despre ce s-a construit peste el cât timp era greșit. (METODA §25)
- **ce blochează**: `scripts/scan_trasee.py` construia harta de aliasuri de nivel-modul cu `ast.walk(tree)`, care intră **și** în corpurile funcțiilor. `main.py` are `from core import cont_valid as _cv` la linia 30 și `from core import stocuri_cv_api as _cv` în corpul unei rute (linia 2841); al doilea îl suprascria pe primul. **Măsurat: 1 alias umbrit, 14 rute cu atribuire falsă** — cele șase `nota-*` (leasing, lichidare, perisabilități, provizion, subvenție, inventariere), plus `achizitie-agricultor`, `achizitie-taxare-inversa`, `achizitie-ic`, `achizitie-neinregistrat`, `vanzare-ic`, `import-extracomunitar`, `export-extracomunitar`, `decontare-valuta`. Fiecare primea `articole (INSERT/UPDATE)` și `miscari_stoc (INSERT)` pe care nu le atinge: `cont_valid` are **zero** `INSERT`/`UPDATE`/`DELETE`, doar confruntă contul cu planul firmei.
- **AMBELE DIRECȚII, și cea tăcută e cea gravă (METODA §22).** Pe cele 14 instrumentul **adaugă** tabele inexistente — direcția zgomotoasă, care se vede. Dar ruta care chiar cheamă `stocuri_cv_api` primea răspunsul corect **dintr-un accident**: aliasul o nimerea. Un instrument care nimerește nu măsoară, iar direcția care ar fi **scos** un modul real n-ar fi produs zgomot, ci **tăcere** — forma numită pe 25.08 în METODA (*„un filtru învechit nu produce zgomot, produce TĂCERE"*). De aceea nu are plafon: nu se poate spune „cel mult atâtea greșeli".
- **de unde a ieșit**: din comanda lui Costin la lotul 6 — *„două rute ating tabele neașteptate prin modul: `decontare-valuta` atinge `articole` și `miscari_stoc`, `client-acces` atinge `tenants`. Verifică-le — nu ca defecte, ci fiindcă efectul e mai larg decât numele rutei."* **Răspunsul a fost invers decât întrebarea**: efectul nu e mai larg, adnotarea e falsă. (`client-acces` e altceva: acolo plafonul e corect prin construcție, iar ruta doar **citește** `public.tenants` prin `tenant_provisioning.detalii_tenant`, ca să pună numele firmei în emailul de invitație.)
- **reparat în aceeași tură**: aliasurile de nivel-modul se citesc din nodurile din **afara** oricărui corp de funcție sau clasă (`_noduri_nivel_modul`). Clasele nu s-au mișcat — MECANIC 30 · PARȚIAL 0 · MANUAL 5, măsurat înainte și după. **Două gărzi noi** în `core/test_trasee.py`: a treia față a atribuirii false, pe fișier sintetic, cu ambele direcții (aliasul de sus nu se umbrește · importul din corpul propriu funcționează mai departe); și una **anti-vacuu pe `main.py` real** — un modul atribuit unei rute trebuie să fie importat de unde ruta îl poate vedea. A doua pica sub rezolvarea veche, pe `decontare-valuta`.
- **A DOUA MĂSURĂTOARE, mai mare decât prima, și n-a fost căutată.** Regenerând adnotările pe toate cele 192, **121 din 192 difereau** de ce măsoară instrumentul. **Doar 4 din reparația de azi; 117 veneau din altă parte** — și, **corectat după ce am citit R53**, nu erau o putrezire netiută: sunt **restul declarat** al reparației parțiale din R53 (`d0bd859`, aceeași zi), care spune negru pe alb *„nu s-a atins blocul generat din TRASEE.md Partea XII — acela e păzit caracter cu caracter, iar schimbarea lui e o măsurătoare separată”*. Ce n-a spus nimeni acolo e că `TRASEE_VERIFICARI.md` rămăsese la fel — iar el e fișierul în care se **scriu** verificările. Azi s-au regenerat amândouă. Adică verificările se scriau uitându-se la un rând care spunea *„ruta scrie în T"* acolo unde instrumentul măsurase *„un modul chemat de ea scrie în T"* — **o afirmație mai tare decât măsurătoarea**, exact inversul a ce apără cuvântul PLAFON. Cauza e aceeași clasă cu blocul din `TRASEE.md` Partea XII, dar acolo exista o gardă doc↔cod și aici nu: garda cerea doar ca rândul `ce face` să **existe**. Construită azi: `test_adnotarea_din_TRASEE_VERIFICARI_e_IDENTICA_cu_ce_masoara_instrumentul`.
- **relația cu R53, ca să nu se citească drept aceeași restanță**: **R53 e despre GROSIMEA plafonului** — o rută moștenește tot ce scrie modulul, nu doar funcțiile pe care le cheamă (65 scrieri proprii · 108 doar moștenite · 19 niciuna; **verificat azi: neschimbate de reparația asta**, fiindcă toate cele 14 rute aveau deja scrieri proprii). **R60 e despre DIRECȚIA în care arăta plafonul** — modulul însuși era altul. Un plafon gros dar corect e o afirmație slabă și onestă; unul îndreptat greșit e o afirmație falsă. R53 rămâne deschisă pe condiția ei (rezolvarea la nivel de **funcție**), neatinsă azi.
- **ce s-a marcat, nu rescris**: la cererea lui Costin, loturile 1–5 **nu** se rescriu. Cele 11 rute afectate din ele poartă în `TRASEE_VERIFICARI.md` un rând care spune ce s-a șters din adnotare și de ce. Din verificările scrise sub ele, **două** stăteau pe partea ștearsă: la `nota-inventariere` — *„mișcările de stoc au aceeași dată cu nota"* — rămâne **fără obiect**, fiindcă ruta nu produce nicio mișcare de stoc; la `achizitie-neinregistrat`, rândul avea condiția scrisă în față (*„dacă atinge stocul prin modul"*), iar condiția e acum cunoscută falsă.
- **ce NU vede măsurătoarea**: câte dintre verificările celor **117** adnotări stătute au fost scrise pe forma mai tare (`scrie` în loc de `poate atinge`). N-am numărat-o — cere citit fiecare rând, nu comparat două șiruri. Iar `main.py` e singurul fișier măsurat: dacă alt fișier cu rute are aceeași umbrire, gardul anti-vacuu nu se uită acolo.
- **CONDIȚIA ÎNDEPLINITĂ 26.08.2026.** Costin: *„LE RESCRII TU. Toate cinci. Adnotarea corectă e a ta, iar verificarea trebuie scrisă pe ce e adevărat, nu pe ce credeam eu.”* Rescrise, cu precizarea lui pe fiecare: la `nota-inventariere` verificarea s-a mutat pe ce FACE ruta (nota de plus/minus, ieșirea mijlocului fix), iar absența mișcării de stoc s-a consemnat separat — **R64**, nu ca rând nul aici; la `achizitie-neinregistrat` și `achizitie-ic` a ieșit condiția pe stoc și a rămas restul, iar `firma_profil` are acum răspunsul scris (contorul de numerotare din `facturi_api`); la `decontare-valuta` rândul nul a ieșit, iar în locul lui a intrat unul care se poate verifica — **ziua cursului se calculează și se aruncă**; la `vanzare-ic` s-a adăugat absența, care e cea mai vizibilă.
- **condiția de deblocare**: *(îndeplinită azi, vezi rândul de deasupra; textul rămâne ca să se vadă pe ce s-a închis)* Costin confirmă sau rescrie verificările care stăteau pe adnotări schimbate — cele **două** numite mai sus, plus cele trei rute din lotul 6 al căror plafon s-a schimbat (`decontare-valuta`, `achizitie-ic`, `vanzare-ic`, în fișierul lui). Se închide când niciun loc de verificare nu mai stă pe o descriere a efectului care s-a schimbat, iar asta nu e mecanic: garda nouă spune când adnotarea diverge, dar **nu** spune dacă propoziția scrisă sub ea mai are obiect.

### R61 — Raportul Z tastat de om nu are verificare de duplicat, iar nota lui intră direct ca evidență

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T24 · interdicția 15 · **PRAG 2** *(măsurat, nu presupus: **zero** note cu sursa `horeca_z` sau `amef` pe toate cele 17 scheme — ecranul nu e folosit azi)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `b86be82`
- **rezolvată pe commit**: `70b20f9`
- **măsurat la**: 2026-08-26 · **pe commit**: `b86be82`
- **planul**: **NEACOPERIT.** Citit `PLAN_ARHITECTURA.md` după *raport Z*, *horeca*, *AMEF*, *duplicat*, *dublare*, *storno*, *ciornă*, *evidență*. Cel mai aproape e **Partea IV — ciclul de viață al unui document**, care începe cu *„INTRARE: date brute → evidență, cu proveniență și grad de certitudine”* și care spune, mai jos, *„emiterea e idempotentă și repetabilă — nicio schemă nu interzice al doilea exemplar”*. Dar regula aia e despre **EMITERE**: al doilea exemplar al **aceluiași** document. Aici a doua apăsare nu produce un al doilea exemplar, ci **o a doua evidență** — alt venit, nu altă copie. Planul n-are nicăieri regula de idempotență la **INTRARE**, iar **P15** (*„după închiderea unei perioade, nu se modifică; se stornează”*) privește perioada închisă, nu ziua repetată. (METODA §25)
- **ce blochează**: `POST /tenants/{tenant_id}/horeca/raport-z` scrie nota cu `status='validata'` **direct** și cu numărul `Z-{data}`, fără să întrebe dacă mai există una pe aceeași dată. Un al doilea apel produce **a doua notă validată cu același număr**: venitul zilei se contabilizează de două ori, direct în evidență, sărind etapa de ciornă. Ruta pereche — `POST /horeca/import-amef` — **are** verificarea (pe `sursa='amef'` și numărul `Z-{NUI}-{nr_raport}`, cu 409 la a doua încercare), iar ea produce doar o **ciornă**. Deci verificarea există exact acolo unde greșeala ar fi fost reparabilă, și lipsește acolo unde nu e.
- **A DOUA ASIMETRIE, în aceeași pereche**: `import-amef` **nu** cheamă `_cere_luna_deschisa`; `raport-z` îl cheamă. Ruta fără rol e și cea fără poarta de perioadă închisă — poate scrie o notă într-o lună închisă. Se consemnează aici fiindcă e aceeași pereche de rute și aceeași citire; dacă se decide altfel, se desface în restanță proprie.
- **de unde a ieșit**: din întrebarea lui Costin la lotul 6 — *„ce deosebește `horeca/raport-z` de `horeca/import-amef`"*. Deosebirile sunt patru (sursa datelor: fișier AMEF parsat vs. tastat · starea notei: ciornă vs. validată · cotele: din XML vs. 11 și 21 fixe în cod, prin suta mărită · cheia de duplicat: verificată vs. neverificată), iar **rolul e explicat corect în cod** — comentariul `[R55, 26.08.2026]` spune că `raport-z` cere rol fiindcă scrie `validata` direct. Întrebarea era despre rol; răspunsul e că **cele două asimetrii care contează merg invers decât rolul**.
- **schimbarea de contract, ACCEPTATĂ (Costin, 26.08.2026), fără perioadă tolerantă**: *„zero note pe 17 firme, deci nimeni nu e afectat. O perioadă tolerantă ar însemna să acceptăm azi note fără cheie, pe care mâine nu le-am putea deduplica retroactiv. Costul toleranței e permanent; costul refuzului e zero.”*
- **ce NU e**: nu e o restanță de rol, și nu e o instanță nouă de R55 — R55 e deja aplicată aici, corect. E despre ce **nu** verifică ruta după ce a primit rolul.
- **ce NU vede măsurătoarea**: zero note **azi** nu înseamnă că ecranul nu se poate folosi mâine; înseamnă doar că efectul nu e produs. Precedentul contrar e R22/R26, unde zero cazuri au primit totuși prag 1 fiindcă **calea de generare era vie și producea o cifră greșită la cerere**. Aici pragul l-a numit Costin înainte de măsurătoare — *„prag 1 dacă ecranul e folosit, prag 2 dacă nu"* — iar clasa e alta: nu o valoare falsă emisă către autoritate, ci o dublare care cere un al doilea act al omului.
- **APLICAT 26.08.2026 — varianta (a), plus poarta.** Decizia lui: *„raportul Z e un document al casei de marcat, unic pe zi și pe aparat. Două rapoarte Z pe aceeași dată nu există în realitate, deci nici în evidență.”* Iar cheia **nu e data**, tot el: `Z-{NUI}-{nr_raport}`, ca la `import-amef` — *„o firmă cu două case de marcat are două rapoarte Z pe zi, legitim.”* Ce s-a construit: `_cere_z_unic` caută în **amândouă** sursele (`horeca_z` și `amef`), deci un raport importat nu se mai poate tasta și invers — altfel ar fi fost jumătate de poartă; `raport-z` cere acum NUI + numărul raportului, iar refuzul **numește nota existentă și spune ce se face cu ea**; `import-amef` a primit `_cere_luna_deschisa`, fiindcă *„o notă într-o lună închisă e aceeași clasă indiferent că e ciornă”*. Ecranul cere cele două câmpuri, cu unde se găsesc pe bonul tipărit. Gard: `core/test_raport_z_unic.py` — 4 teste, pe **structură** (apelul există ȘI e înaintea scrierii), cu calibrare negativă pe ambele forme ale greșelii: apel absent, și apel după scriere. **Schimbare de contract, declarată**: `nui` și `nr_raport` sunt obligatorii pe `POST /horeca/raport-z`; un client vechi care nu le trimite primește 400 cu îndrumare.
- **condiția de deblocare**: decizia lui Costin între **(a)** ruta refuză a doua notă pe aceeași dată, ca `import-amef` (409, cu numărul existent numit); **(b)** o acceptă, dar prima se stornează explicit, iar actul se consemnează; **(c)** raportul Z tastat produce **ciornă**, ca importul, iar validarea rămâne un act separat — ceea ce ar face și rolul de prisos. Se închide când a doua notă pe aceeași dată ori e imposibilă, ori e un act consemnat — cu gard, plus poarta de lună închisă pe `import-amef`.

### R62 — Clientul își schimbă adresa de autentificare fără confirmare, iar cabinetul nu află nici asta, nici cine a primit acces

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T35 · interdicția 46 · P13 · **PRAG 1** *(ridicat de Costin, 26.08.2026, după măsurătoare: „ce face pragul nu e gravitatea, e că se poate atinge azi. Un om deschide portalul, vede butoane, apasă, primește 403 pe un mesaj care îi spune că nu e titularul. Aia e afirmația falsă din P13, în forma cea mai directă: ecranul spune una, serverul face alta.” Precedentul: R22, prag 1 pe zero depuneri, fiindcă **calea era vie**; aici calea e vie ȘI omul e real — #8284, firma #8396)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `57656a6`
- **rezolvată pe commit**: `e564e3d`
- **măsurat la**: 2026-08-26 · **pe commit**: `57656a6`
- **planul**: **NEACOPERIT.** Citit `PLAN_ARHITECTURA.md` după *portal*, *identitate*, *autentificare*, *acces*, *confirmare*. Secțiunea **„Reguli de acces”** e despre accesul la **registrul legislativ**, nu la aplicație — nu răspunde. Cel mai aproape ca formă e **interdicția 46** (*„o presupunere devenită fapt fără confirmare consemnată”*, P20) împreună cu Partea III — *„fiecare valoare din afară poartă sursa și gradul de certitudine; devine sigură prin **confirmare explicită**”*. Forma se potrivește exact (o adresă venită din afară devine fapt fără confirmare), dar planul o scrie despre **valori fiscale**, nu despre **identitatea unui om**. Planul n-are nicăieri regula de schimbare a identității. (METODA §25)
- **ce blochează**: **fața întâi — `PUT /portal/acces-cont/email`.** Face `UPDATE public.users SET email=%s` **imediat**. Nu există confirmare pe adresa nouă, nu pleacă nicio notificare pe cea veche, nu se consemnează nicăieri de la ce la ce. Iar adresa aia **este** identitatea de autentificare (intrarea se face prin magic-link pe email), deci cine are o sesiune deschisă mută contul. Singurele verificări: doar patronul o poate face, și adresa nouă să nu fie a altui utilizator.
- **și o divergență tăcută, în aceeași rută**: pachetul lunar **nu** pleacă la `users.email`, ci la `firma_profil.patron_email` (sau `firma_profil.email`) — `core/pachete_api.py`. Deci după schimbare, adresa cu care clientul intră în portal și adresa la care primește pachetul sunt **două lucruri diferite**, iar nimic nu le confruntă. Verificarea scrisă de Costin la lotul 7 — *„cabinetul vede că adresa clientului s-a schimbat, altfel pachetele merg în altă parte”* — are răspunsul invers decât presupunea: pachetele **nu** urmează schimbarea, rămân pe vechea adresă din `firma_profil`.
- **fața a doua — `POST /portal/acces-cont/acces`**: ruta refuză o adresă care aparține unui utilizator **activ** sau unuia care nu e `client`. Dar dacă adresa aparține unui cont de client **dezactivat**, intră pe ramura `if ex:` și îl **reactivează** — `UPDATE users SET activ=true, nume=%s` — apoi îl leagă de firmă. Contul își păstrează `accounting_firm_id`-ul **vechi**, care poate fi al **altui cabinet**: aplicația are azi **2 cabinete distincte** pe cele 17 firme și **1 cont de client dezactivat**. Rezultatul ar fi un utilizator care aparține, după coloană, cabinetului A, având acces la o firmă a cabinetului B.
- **și partea care lipsește la amândouă: cabinetul nu vede nimic.** Nici la schimbarea adresei, nici la crearea unui utilizator de către client, nu se scrie niciun rând de audit, nu pleacă nicio notificare, nu se atinge `solicitari_client`. Singurul email care pleacă la adăugarea de acces merge la **noul utilizator**. Iar contul nou se creează cu `accounting_firm_id` luat din `tenants.accounting_firm_id` — adică **sub cabinet**, fără ca el să afle. A treia întrebare a lui Costin (*„cabinetul vede că s-a întâmplat”*) are răspunsul **nu**, la sursă.
- **de unde a ieșit**: din cele trei lucruri pe care Costin le-a lăsat de citit la lotul 7 — *„`POST /portal/acces-cont/acces` merită cea mai multă atenție… trei întrebări decid dacă e sigur”* și *„`PUT /portal/acces-cont/email` fără confirmare pe adresa nouă ar permite mutarea unui cont de pe o sesiune deschisă”*. Prima dintre cele trei întrebări — *accesul nu depășește pe al celui care îl dă* — are răspunsul **da**, prin construcție: rolul e fixat literal `client`, iar `user_tenants` primește exact firma rezolvată din accesul dătătorului. A doua și a treia sunt cele de mai sus.
- **ce NU vede măsurătoarea**: `principal_client_id` e 0 pe 17 azi, dar nu știu **de ce** — dacă e o coloană nouă necompletată încă, sau una abandonată. Diferența contează: în primul caz cele trei rute se aprind în ziua în care cineva o completează, în al doilea sunt cod mort. N-am măsurat nici dacă vreun ecran o scrie.
- **APLICAT 26.08.2026, în ORDINEA cerută de Costin — iar ordinea e argumentul.** **(2) întâi**: un cont de client dezactivat al altui cabinet se **refuză**, pe **amândouă** căile (a clientului și a cabinetului) — *„e singura cale prin care date ale unui cabinet ajung la altul, iar aia nu e o chestiune de urmă, e izolarea din P12.”* Gardul repară clasa: dacă ar fi stat doar pe ruta din care a ieșit constatarea, calea prin cabinet rămânea deschisă. **(1) al doilea**: adresa nu se mai scrie direct. Cererea intră în `public.schimbari_email` (token doar ca hash, 48h), pleacă un link de confirmare pe adresa **nouă** și o notificare pe cea **veche**, iar adresa se reconfruntă cu `users` **la confirmare** — între cele două momente altcineva o poate lua. Nu *„nu se poate face din portal deloc”*, ci **nu instant**, cum a cerut. **(3) al treilea**: `public.urme_portal`, append-only, cu `actiune` dintr-o listă închisă **în bază** și `detaliu` care nu poate fi gol, scrisă la toate patru actele (acces dat / retras, de client sau de cabinet) plus cererea și confirmarea adresei; citibilă prin `GET /tenants/{id}/urme-portal`.
- **CORECȚIE 26.08.2026 seara, după proba lui Costin**: afirmația de mai sus era pe jumătate. Urma e citibilă **de rută**, nu **de om**: `grep` pe tot `static/` nu găsește niciun ecran care s-o ceară. Deci punctul **(3)** — *cabinetul vede că s-a întâmplat* — **rămâne nesatisfăcut**, și nu prin lipsa urmei, ci prin **lipsa căii de citire**. Lecția din R58 (*o urmă care nu se poate citi e scrisă degeaba*) se aplică aici la mine: am construit ruta și am declarat lecția respectată. E a doua față a lui **R70** — acolo o rută de scriere fără apelant, aici una de citire.
- **unde stă ruta de confirmare, și de ce nu unde ai crede**: `POST /public/confirma-email`, nu sub `/portal/`. Toate rutele care se dovedesc cu un **token** și nu cu o sesiune stau sub `/public/` — `activare`, `magic-login`, `reset-parola/seteaza`. O rută fără gardă ascunsă între cele `/portal/*`, care sunt toate pe `cere_client`, ar fi fost a patra instanță în șapte loturi a aceleiași forme: aceeași clasă, tratament diferit. Gard: `core/test_portal_acces.py`, 6 teste, cu calibrare pe forma exactă a greșelii de reparat (o cale gardată, cealaltă nu).
- **MĂSURAT 26.08.2026, ȘI CONTRAZICE ÎNCADRAREA DE MAI SUS — a mea, nu a lui Costin.** El a cerut verificarea: *„nu știu dacă vreun ecran scrie `principal_client_id`, și aia e chiar prima parte a răspunsului — verifică tu.”* Verificat: coloana apare, în tot repo-ul, **numai** ca definiție + cheie străină în `bootstrap_public.sql` și în **patru SELECT-uri** din `main.py`. **Zero scrieri**: niciun `INSERT`, niciun `UPDATE`, niciun ecran (`grep` pe tot `static/` — nimic), iar `tenant_provisioning` inserează `(schema_name, nume, cui, accounting_firm_id, activ)`, fără ea. Deci **nu e o coloană care așteaptă date: e o coloană fără cale de scriere**. Cele trei rute de portal nu sunt *cod care așteaptă date*, sunt cod inaccesibil prin construcție.
- **ȘI E MAI RĂU DECÂT ATÂT: citirea are FALLBACK, scrierile nu.** `GET /portal/acces-cont` face `principal = next((c for c in conturi if c.id == pid), conturi[0])` — pe `pid` NULL ia **primul cont de client** și întoarce `eu_principal=true`. Ecranul îi spune omului *„ești titularul”* și îi arată butoanele; cele trei rute compară cu `tenants.principal_client_id`, care e NULL, deci îi răspund **403: „doar patronul poate…”**. Nu e o funcționalitate care așteaptă, e o **afirmație falsă pe ecran**, azi. **Măsurat cine o vede: o singură firmă — #8396 ALFA MICRO — și un singur om, utilizatorul #8284.**
- **PROPUNERE DE RECLASIFICARE LA PRAG 1, de confirmat de Costin.** Criteriul pragului 1 e *efect greșit la un om ACUM*. Nu e o cifră falsă, e o **afirmație falsă despre ce poate face**, iar precedentul e R22: acolo o afirmație falsă a urcat la prag 1 deși **zero** depuneri erau afectate, fiindcă *calea era vie*. Aici calea e vie și omul e unul real. Reclasificarea e a lui, nu a mea — de-aia câmpul `unde intră` rămâne neschimbat până răspunde.
- **APLICAT 26.08.2026 — varianta (b), decizia lui Costin.** Întrebarea *cine e titularul* se pune altfel: **primul cont de client al firmei** — regula pe care **citirea o folosea deja**. *„Dacă citirea folosește o regulă și scrierea alta, divergența e chiar defectul de azi. Alinierea lor nu adaugă nimic — scoate o inconsistență.”* Toate patru rutele o iau acum din **același loc**, `_titular_client`, iar citirea și-a pierdut fallback-ul: helperul **este** regula, deci n-are pe ce să cadă. Refuzul spune regula, nu doar că n-ai voie — altfel omul nu poate ști pe cine să întrebe. Gard: `test_cele_patru_rute_raspund_LA_FEL_la_cine_e_titularul`.
- **și `principal_client_id` S-A SCOS**, cu motivul lui: *„o coloană cu drum de citire și fără drum de scriere e chiar ce am găsit azi; a o lăsa înseamnă a lăsa a treia cale prin care întrebarea se poate pune altfel mâine.”* Coloana și cheia ei străină, scoase prin `core/migrare_portal.py` (sursă unică) și din oglinda din `bootstrap_public.sql`, ca o bază nouă să nu le recreeze. Ștergerea nu pierde nicio valoare: era goală pe toate cele 17 scheme, și n-avea cum să nu fie.
- **SE POATE EXERCITA, verificat 26.08.2026 la cererea lui Costin** (*„îmi trebuie să știu ce ecran creează un cont de client — dacă există unul”*): **există două căi**, deci nu e a patra instanță a formei. Ecranul e **Firme › firmă › Acces client** (*„Invită clientul în portal”*), care cheamă `POST /tenants/{id}/client-acces`; iar la **crearea firmei** există un câmp opțional de email al clientului, care cheamă aceeași rută. Deci R62 se poate proba pe o firmă de test, fără a atinge date reale.
- **și NU s-a exercitat, deliberat.** Costin: *„o probă care trimite emailuri la o adresă reală și mută identitatea unui om nu e o probă, e o operațiune.”* Firma #8396 și utilizatorul #8284 sunt reali. Rămâne de făcut pe o firmă de test, cu o adresă pe care o controlează el.
- **decizia de produs, asumată explicit de Costin**: *„«titular = primul venit» e într-adevăr o decizie de produs, și o iau: pentru o firmă mică, primul care primește acces la portal e patronul sau administratorul. Nu e o presupunere riscantă. Iar dacă vreodată se dovedește greșită, se repară printr-o cale de schimbare a titularului — care e altă funcționalitate, nu o coloană completată la provisionare.”*
- **condiția de deblocare**: se schimbă, tot din măsurătoare. Nu mai e *„la primul client cu acces la portal”* — nu se poate ajunge acolo, fiindcă nimic nu scrie coloana. E, în ordine: **(0)** se hotărăște dacă `principal_client_id` se completează (și de unde: la provisionare? la prima invitație de client? dintr-un ecran?) **sau** dacă întrebarea *cine e titularul* se pune altfel — de exemplu *primul cont de client al firmei*, chiar regula pe care o folosește deja citirea, și atunci scrierile trebuie s-o folosească și ele, ca cele două să nu mai spună lucruri diferite; **(1)** abia apoi se exercită cele trei reparații pe o firmă reală. Până atunci gardul rămâne pe cod, iar asta se spune.
- **condiția de deblocare (formularea dinainte de măsurătoare)**: la primul client cu acces la portal — pe motivul, al lui Costin, că `principal_client_id` ar fi o coloană necompletată, nu una abandonată. Măsurătoarea a arătat că nu e nici una, nici alta. Se închide când cele trei se exercită pe o firmă reală: un cont refuzat fiindcă e al altui cabinet, o schimbare de adresă care NU se aplică până la confirmare, și un cabinet care vede amândouă în `urme-portal`. Până atunci gardul e pe cod, iar asta se spune — e forma din [punctul orb e FIRMA, nu ecranul].

### R63 — Aceeași persoană are două adrese în aplicație, iar nimic nu le confruntă

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T35 · **PRAG 2** *(nicio cifră falsă; ce se poate pierde e un pachet lunar trimis la o adresă pe care n-o mai citește nimeni)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `203fd31`
- **măsurat la**: 2026-08-26 · **pe commit**: `203fd31`
- **planul**: **NEACOPERIT.** Citit `PLAN_ARHITECTURA.md` după *identitate*, *autentificare*, *portal*, *patron_email* — niciun rezultat pe niciunul. Planul definește ciclul unui **document** și regulile registrului, dar nu spune nicăieri câte adrese are un om și care dintre ele e cea care contează. Aceeași lipsă ca la R62, alt capăt al ei. (METODA §25)
- **ce blochează**: autentificarea în portal se face pe `public.users.email`. Pachetul lunar pleacă la `firma_profil.patron_email` (sau `firma_profil.email`) — `core/pachete_api.py`. Sunt **două câmpuri diferite, în două locuri diferite**, pentru aceeași persoană, iar nicio rută nu le compară. După o schimbare de adresă din portal, clientul intră cu adresa nouă și primește pachetul pe cea veche — fără ca vreunul din cei doi să afle.
- **de unde a ieșit**: Costin, verificând lotul 7: *„divergența `users.email` ↔ `firma_profil.patron_email` deschide-o separat. Două identități pentru aceeași persoană, care se pot desincroniza fără ca nimeni să afle — nu e parte din R62, e o constatare proprie.”* Verificarea pe care o scrisese la lotul 7 — *„cabinetul vede că adresa clientului s-a schimbat, altfel pachetele merg în altă parte”* — presupunea că pachetele **urmează** schimbarea. Nu o urmează.
- **ce NU vede măsurătoarea**: n-am numărat pe câte firme cele două adrese diferă azi. Cu `principal_client_id` gol pe 17 din 17, schimbarea din portal n-a putut fi făcută niciodată, deci divergența de acolo e zero; dar cele două câmpuri se completează și pe alte căi (profilul firmei, invitația din cabinet), iar pe alea n-am măsurat.
- **DECIS ȘI APLICAT 26.08.2026 — varianta (c).** Costin: *„rămân două, fiindcă înseamnă lucruri diferite… cine intră în portal și cine primește pachetul lunar chiar pot fi persoane diferite — administratorul firmei și contabilul intern, sau patronul și asistenta. A le uni ar forța o realitate pe care produsul n-o are.”* Ce s-a schimbat: **numele**. În portal — *Adresa de autentificare* și *Adresa la care primești pachetul lunar*, amândouă afișate, iar formularul de schimbare spune explicit că **pachetul nu urmează schimbarea**. În cabinet, câmpul care se numea *E-mail* se numește *E-mail firmă (aici se trimite pachetul lunar)*. Iar **când coincid, se spune** — cerința lui: *„un ecran care arată aceeași adresă în două câmpuri fără să spună că sunt distincte produce chiar presupunerea greșită.”*
- **CIFRA, cerută de el, și e mai ciudată decât întrebarea**: pe **0** din 17 firme cele două adrese diferă — dar nu fiindcă ar fi egale. **Pe niciuna nu există amândouă**: 12 firme au adresa de pachet și niciun cont de portal · 2 au cont de portal și nicio adresă de pachet · 3 n-au niciuna. Deci divergența nu e nici teoretică, nici curentă: e **nemăsurabilă azi**, iar prima firmă care le va avea pe amândouă e și prima care o poate produce.
- **și o a doua coloană fără cale de scriere, găsită pe drum**: `patron_email` are **precedență** în `pachete_api` (`coalesce(patron_email, email)`), dar **niciun ecran nu o scrie** — `grep` pe tot `static/`: zero. E aceeași formă cu `principal_client_id` de la R62, a doua în aceeași tură. Azi nu se vede, fiindcă `coalesce` cade pe `email`; se va vedea în ziua în care cineva o completează din afara aplicației.
- **condiția de deblocare**: decizia lui Costin între **(a)** o singură adresă, iar cealaltă devine derivată; **(b)** rămân două, dar se confruntă și divergența se **arată** — la cabinet și la client; **(c)** rămân două fiindcă înseamnă lucruri diferite (cine intră vs. cine primește), și atunci se **numesc** diferit în interfață, ca nimeni să nu creadă că sunt aceeași. Se închide când nu mai există o pereche care poate diverge tăcut — cu gard.

### R64 — Contabilitatea și stocul sunt două evidențe disjuncte, iar niciun document nu le leagă

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T20 · T28 · **PRAG 2** *(măsurat: evidența cantitativă e abia folosită — 13 mișcări de stoc pe 2 firme din 17, 12 articole; **0 NIR-uri pe toate cele 17**)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `203fd31`
- **măsurat la**: 2026-08-26 · **pe commit**: `203fd31`
- **planul**: **NEACOPERIT.** Citit `PLAN_ARHITECTURA.md` după *stoc*, *gestiune*, *cantitativ*: un singur rezultat, și ăla despre altceva (*„un verdict stocat ca frază”*, interdicția 27). Partea IV descrie ciclul unui **document**, nu relația dintre două **evidențe** care descriu același bun. Planul nu spune dacă mișcarea de stoc e un efect al documentului contabil sau un act separat — și chiar aia e întrebarea. (METODA §25)
- **ce blochează**: **măsurat pe toate rutele care produc intrări sau ieșiri de bunuri: 8 mișcă stocul, 18 nu.** Cele 8 sunt exclusiv rutele `/stocuri/*` (intrare, ieșire, transfer, inventar, reclasificare) plus rețetele — toate prin `stocuri_cv_api`, singurul modul care scrie `miscari_stoc`. Cele 18 sunt fluxurile operaționale: `achizitie-ic`, `vanzare-ic`, `achizitie-taxare-inversa`, `achizitie-agricultor`, `achizitie-neinregistrat`, `import-extracomunitar`, `export-extracomunitar`, `nota-inventariere`, `nota-productie`, `nota-perisabilitati`, vânzările cu marjă — **și, cel mai greu de explicat, `stocuri/nir` și `stocuri/descarcare`**, care cheamă `stocuri_api`: un modul care scrie `nir` și `nir_linii`, **nu** `miscari_stoc`.
- **și tabela aia nu e citită de nimeni**: `nir_linii` apare, în tot `core/`, doar în `stocuri_api` — modulul care o scrie. `miscari_stoc` e citită de `rapoarte_comerciale_api`, `retete_api`, `articole_import_api`. Deci recepția — documentul canonic prin care marfa intră în firmă — scrie într-un al treilea loc, pe care nu-l consultă nimic. **Măsurat pe date: `nir` și `nir_linii` au 0 rânduri pe toate cele 17 scheme.**
- **răspunsul la a treia întrebare a lui Costin** — *„dacă separarea ar fi voită, ar exista o cale prin care mișcarea se face separat. Există?”* — **DA, există**: cele cinci rute `/stocuri/*`. Deci nu e o absență pe două rute, cum arăta din adnotare; e o **separare structurală**: contabilitatea și gestiunea sunt două evidențe paralele, iar trecerea dintr-una în alta e un act manual, neconsemnat ca atare și neverificat de nimic. Primele două motive ale lui rămân însă în picioare: o livrare intracomunitară de bunuri scoate marfa din firmă în contabilitate și o lasă în gestiune, iar `achizitie-ic` chiar cheamă `facturi_api` fără să cheme vreun modul de stoc.
- **ce NU vede măsurătoarea**: dacă separarea e o decizie de produs (gestiune ținută separat, ca în multe cabinete) sau o legătură nefăcută. Costin: *„nu știu dacă e intenționat, și nu decid fără să știu ce s-a gândit atunci.”* Și n-am măsurat câte firme folosesc efectiv ambele evidențe — cu 13 mișcări pe 2 firme, întrebarea nu s-a pus încă pe date reale.
- **DECIS 26.08.2026 — varianta (a), și motivul e chiar măsurătoarea.** Costin: *„`nir_linii` are zero rânduri pe 17 scheme și zero cititori. Nu e o a doua evidență — e o evidență care nu există. A o păstra separată ar însemna să declarăm ca separare ceva ce nu s-a construit niciodată.”* Varianta (b) ar fi construit o reconciliere între o evidență reală și una goală; (c) ar fi fost onestă doar dacă amândouă erau folosite. Deci: NIR-ul, descărcarea, vânzarea și achiziția produc mișcare de stoc prin `stocuri_cv_api`, iar rutele `/stocuri/*` rămân pentru corecții și pentru ce n-are document. **`nir` și `nir_linii` NU se șterg** — *„un NIR e un document… ce se mută e mișcarea de stoc, nu documentul.”*
- **MĂSURĂTOAREA DINAINTEA REPARAȚIEI, cerută de el (*„ce s-ar rupe?”*), și răspunsul are două jumătăți.** Ce s-ar rupe: **aproape nimic.** `stocuri_api` e chemat dintr-un **singur** loc de producție — `main.py`, cele două rute — plus un test și instrumentul de inventar. `nir_linii` e atins doar de `stocuri_api` însuși. Deci suprafața de mutat e mică. **Ce trebuie construit înainte, și n-a fost întrebat:** `nir_linii` are coloanele `(id, nir_id, denumire, cantitate, pret_achizitie, pret_vanzare, cota_tva)` — **denumire ca text liber, fără `articol_id`**. O linie de NIR nu poate produce o mișcare de stoc până nu se leagă de un articol; **asta e costul real al variantei (a)**, nu mutarea apelului.
- **și partea care face varianta (a) mai ușoară decât pare**: `miscari_stoc` are deja coloanele `inregistrare_id` **și** `factura_id`. Legătura dintre mișcare, nota contabilă și factură e **proiectată în schemă** și nescrisă în cod — deci (a) are unde ateriza, nu cere o tabelă nouă.
- **ce mai atârnă de `miscari_stoc`, ca să se vadă miza**: `rapoarte_comerciale_api`, `retete_api`, `articole_import_api` — și **D406/SAF-T** (`test_d406`, `seed_alfa_d406`). Adică marfa intrată prin NIR nu apare azi în raportarea SAF-T de stocuri, fiindcă NIR-ul nu scrie acolo.
- **CUM SE LEAGĂ LINIA DE NIR, decis 26.08.2026**: **coloană nouă `articol_id`, cu rezolvare LA RECEPȚIE — omul alege articolul.** Nu creare automată din denumire, iar motivul e al lui Costin: *„e felul de «auto» care produce dubluri, iar un articol dublat în nomenclator nu se mai poate desface — toate mișcările lui rămân împărțite.”* Momentul e cel potrivit fiindcă *„cine primește marfa are factura în față și știe ce e”*: un ecran care propune articolele existente și cere confirmare, cu posibilitatea de a crea unul nou **explicit**, nu incidental. Iar `denumire` **rămâne** — e ce scrie pe factura furnizorului, și poate diferi de denumirea internă a articolului: *„sunt două lucruri, nu unul”*.
- **coloana și calea ei de scriere intră ÎMPREUNĂ**, și asta e lecția zilei, nu o preferință: `articol_id` adăugat singur ar fi **a treia** coloană fără cale de scriere din aceeași tură, după `principal_client_id` (R62) și `patron_email` (R65). De aceea migrarea nu s-a făcut azi.
- **condiția de deblocare**: decizia e luată; se închide când cele 18 rute produc mișcare de stoc — **eșalonat, nu într-o zi**, cum a spus el — iar înainte de prima se leagă linia de NIR de articol. Se face cu gard, și cu o măsurătoare pe fiecare etapă: câte din cele 18 au trecut. *(Textul dinainte de decizie, păstrat fiindcă e istoricul întrebării:)* decizia lui Costin între **(a)** documentele operaționale produc mișcarea de stoc, iar `/stocuri/*` rămân pentru corecții; **(b)** rămân separate, dar există o **reconciliere** care arată divergența (e chiar instrumentul #5 din roadmap, nefăcut); **(c)** rămân separate și se **spune** că sunt, în aplicație, ca nimeni să nu creadă că balanța de stoc urmează contabilitatea. Se închide când cele două evidențe ori se leagă, ori divergența lor e vizibilă — cu gard. **Primul pas e făcut**: măsurătoarea de mai sus, cerută chiar de el.

### R65 — `patron_email` are precedență la trimiterea pachetului și nicio cale de scriere

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T35 · **PRAG 3** *(măsurat: **0 din 17** firme o au completată, deci `coalesce` cade azi pe `email` și nimic nu pleacă greșit. Ce lipsește e o cale, nu o corectitudine)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **deschisă pe commit**: `60fd000`
- **rezolvată pe commit**: `3afa338`
- **măsurat la**: 2026-08-26 · **pe commit**: `60fd000`
- **planul**: **NEACOPERIT**, aceeași lipsă ca la R62 și R63: `PLAN_ARHITECTURA.md` nu spune nicăieri câte adrese are un om, care dintre ele contează, și cine o scrie. Citit după *patron_email*, *identitate*, *portal*: zero rezultate pe primul, iar celelalte duc la reguli despre **valori fiscale**, nu despre persoane. (METODA §25)
- **ce blochează**: `core/pachete_api.py` trimite pachetul lunar la `coalesce(patron_email, email)` din `firma_profil` — deci `patron_email` are **precedență**. Dar **niciun ecran nu o scrie**: `grep` pe tot `static/` întoarce zero, iar ecranul de date ale firmei are un singur câmp de email, care scrie `email`. E a doua coloană cu drum de citire și fără drum de scriere găsită în aceeași tură, după `principal_client_id`.
- **ce o deosebește de R62, și de-aia e restanță proprie** *(Costin: „sunt aceeași formă, dar `patron_email` are ceva ce `principal_client_id` n-are”)*: un `coalesce` **care o ascunde azi și o activează mâine**. La R62, coloana goală producea un refuz — vizibil. Aici, coloana goală produce comportamentul corect, iar completarea ei — dintr-un import, dintr-un seed, dintr-un `UPDATE` manual — **mută pachetele fără ca vreun ecran s-o arate**.
- **măsurat înainte de decizie, cum a cerut Costin** (*„verifică dacă vreo firmă o are completată azi, din import sau din seed. Dacă da, pachetele merg deja altundeva decât crede cineva.”*): **0 din 17**, toate goale. Deci nu, nu merg. Bomba e armată, nu declanșată.
- **ce NU vede măsurătoarea**: n-am căutat *cine ar putea* completa coloana — importuri de migrare, seeduri, scripturi de-ale mele. Am măsurat starea, nu căile.
- **APLICAT 26.08.2026 — a doua variantă: IESE DIN `coalesce`, iar coloana se scoate.** Decizia lui: *„un al doilea câmp de email pe firmă cere explicat când îl folosești — iar dacă nu se poate explica în două cuvinte pe ecran, întrebarea nu e a produsului, e a noastră.”* Plus argumentul care leagă de R63: acolo tocmai se stabilise că există **două** adrese care înseamnă lucruri diferite — cine intră și cine primește; `patron_email` ar fi fost a treia, *„și nu știu ce ar însemna”*. Pachetul pleacă acum la o singură adresă, `firma_profil.email`, cea care de azi se numește pe ecran *E-mail firmă (aici se trimite pachetul lunar)*. Coloana s-a scos din **17 din 17** scheme (`core/migrare_patron_email.py`, sursă unică) și din `tenant_template.sql`, ca o firmă nouă să n-o primească. Nu s-a pierdut nicio valoare: era goală peste tot.
- **și ce NU s-a lăsat deschis**: *„dacă vreodată apare nevoia reală — un patron care vrea pachetul la altă adresă decât cea a firmei — se construiește atunci, cu ecran și cu explicație. Nu se lasă o coloană care așteaptă o nevoie ipotetică.”*
- **condiția de deblocare**: decizia lui Costin, deja formulată ca alternativă strictă — **fie** `patron_email` primește cale de scriere (un câmp în ecranul de date ale firmei, lângă cel existent, cu numele care spune ce e), **fie** se scoate din `coalesce` și pachetul pleacă doar la `email`. *„Nu poate rămâne cu precedență și fără scriitor.”* Se închide când una din cele două e făcută, cu gard.

### R66 — `patron_nume` intră în adeverințe și contracte, și nu-l scrie nimic

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE T15 · interdicția 20 · **PRAG 2** *(nu produce o cifră falsă, dar produce un **document cu un gol** — adeverința și contractul îl tipăresc)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `56275cb`
- **măsurat la**: 2026-08-26 · **pe commit**: `56275cb`
- **planul**: **NEACOPERIT**, a patra oară în aceeași zi pe aceeași lipsă: `PLAN_ARHITECTURA.md` nu spune cine scrie datele de identificare ale firmei, doar ce se face cu ele. Cel mai aproape e **interdicția 20** (*artefacte de un octet cu nume de declarație*) — un document care se produce cu un câmp gol e aceeași clasă, dar planul o scrie despre corpus, nu despre firmă. (METODA §25)
- **ce blochează**: `firma_profil.patron_nume` e citită de **trei** module — `core/adeverinta.py`, `core/contracte_api.py`, `core/pachete_api.py` — și **nu e scrisă de nimic**: căutat în tot `*.py` și tot `static/`, apare exclusiv în `SELECT`-uri. E **a treia instanță** a formei găsite azi (coloană cu drum de citire și fără drum de scriere), după `principal_client_id` (R62, scoasă) și `patron_email` (R65, scoasă) — dar **nu se poate scoate ca ele**: primele două aveau un înlocuitor, asta e tipărită pe un document care ajunge la un om.
- **de unde a ieșit**: Costin, după R65: *„dacă `patron_nume` are cale de scriere și `patron_email` nu, aia e mai interesantă decât dacă amândouă n-au: două câmpuri alăturate, unul scriibil, celălalt nu.”* Măsurat: **niciunul** nu avea.
- **ȘI INSTRUMENTUL CERUT PENTRU CLASĂ A PICAT CALIBRAREA — se scrie, ca următoarea încercare să nu repete.** Costin a cerut măsurarea clasei: *„câte coloane din schemă sunt citite de cod și scrise de nimic?”* Am construit-o (schemă din `tenant_template.sql` × scan pe fragmentele SQL) și a dat **17**. Am calibrat-o pe un caz **cunoscut rezolvat** — `salariati.data_incetare`, R51 — și a raportat-o ca nescrisă. **E fals**: se scrie, dar printr-o **listă de coloane generată** din `_CAMPURI_API`. Deci instrumentul greșește și în direcția zgomotoasă, nu doar în cea tăcută; **n-are plafon** (METODA §22), iar cifra 17 nu se publică.
- **de ce nu e o reparație de instrument, ci o limită**: în codul ăsta calea de scriere se **asamblează la rulare** — `UPDATE firma_profil SET " + ", ".join(seturi)`, liste de coloane construite din constante. *Cine scrie coloana* nu e un fapt textual. Un instrument corect ar trebui să **observe** scrierile la nivel de bază, nu să le citească în cod.
- **ce NU vede măsurătoarea**: dacă `patron_nume` se completează din import sau din seed. N-am măsurat pe date câte firme îl au — doar că aplicația nu-l scrie.
- **APLICAT 26.08.2026 — (a) ȘI (c), în ordinea cerută.** Decizia lui: *„numele administratorului e un fapt al firmei, ca denumirea și CUI-ul. Nu se derivă din nimic — nu e în ONRC-ul pe care îl avem, nu e în vector, nu e în contul de utilizator, fiindcă cine ține evidența nu e neapărat cine semnează.”* **(a)**: `patron_nume` a intrat în `CAMPURI_FISCALE`, deci în lista generată care alimentează și `SELECT`-ul, și `UPDATE`-ul lui `salveaza_date`; ecranul **Date firmă** are câmpul *Nume administrator*, cu ajutorul care spune unde apare. **(c)**: `firma_profil_api.cere_administrator` — un loc unic — e chemat din `adeverinta` și din `contracte_api`, iar rutele îl convertesc în **422**. Refuzul **numește documentul și unde se completează**: *„Adeverința nu se poate emite: lipsește numele administratorului. Completează-l în Date firmă › Nume administrator.”*
- **ordinea a fost și argumentul**: *„un refuz e onest doar dacă omul poate completa. Deci (a) e precondiția, iar (c) devine consecință firească.”* Amândouă în aceeași tură — **coloana și calea ei intră împreună**.
- **ce a prins reparația, imediat**: `core/test_perioada_indisponibila.py` emitea o adeverință pe o schemă efemeră fără `patron_nume`. Fixtura o pune acum — și era important s-o pună, fiindcă testul ăla are un `pytest.raises(ValueError)` pe altceva (golul de tichet din 2025): fără fixtură, ar fi trecut pe refuzul greșit, adică **verde pe motivul nepotrivit**.
- **condiția de deblocare**: decizia lui Costin între **(a)** primește câmp în ecranul de date ale firmei, lângă celelalte date de identificare; **(b)** se derivă din altceva care se scrie (titularul contului? un asociat?); **(c)** documentele care-l tipăresc **refuză** să se producă fără el, în loc să lase un gol — care e chiar forma din interdicția 20. Se închide când niciun document care ajunge la un om nu se mai poate produce cu câmpul ăsta gol, **fără ca cineva să fi putut să-l completeze**.

### R67 — Suita de teste rulează pe baza de PRODUCȚIE, iar izolarea e o convenție, nu o barieră

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · METODA §22 · P12 · **PRAG 2** *(nicio pierdere măsurată azi: cele 9 schemei orfane erau efemere și goale de date reale, iar cele 17 scheme de firmă sunt intacte. Ce lipsește e bariera, nu corectitudinea de până acum)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `3a2b9bd`
- **măsurat la**: 2026-08-26 · **pe commit**: `3a2b9bd`
- **planul**: **NEACOPERIT.** Citit `PLAN_ARHITECTURA.md` după *test*, *izolare*, *mediu*: planul descrie ce trebuie să fie adevărat despre DATE, nu despre unde rulează suita care le verifică. `P12` (izolarea între cabinete) e cea mai apropiată ca formă — izolare ca proprietate garantată, nu ca disciplină — dar e scrisă despre tenanți, nu despre teste. (METODA §25)
- **ce blochează**: `conftest.py` sursează `~/.iconta/db.env` — **datele de conectare ale producției**. Măsurat: suita rulează pe baza `iconta_v2`, ca utilizatorul `iconta_user`, adică exact baza și exact contul aplicației. Nu există o bază de test. Izolarea e obținută de **fiecare test în parte**: schemă efemeră `test_*`/`ztest_*` din `tenant_template.sql`, apoi `rollback()` sau `DROP SCHEMA` în `finally`. **Măsurat: 9 fișiere fac `CREATE SCHEMA`; 8 sunt teste și toate 8 au curățare — singurul fără e `tenant_provisioning.py`, cod de producție, care are dreptate s-o facă.**
- **și disciplina e best-effort, nu garanție** — dovada e că a eșuat: **9 scheme orfane** au supraviețuit în producție (`test_d100_profit`, `test_d112_cadou`, `test_d112_ded_supl`, `test_d301_zero_ruptura`, `test_d390_nota1`, `test_ded_generalizare`, `ztest_cresa`, `ztest_cultural`, `ztest_exces_van_d112`), **49 de tabele fiecare, 441 în total**. Verificat una câte una: **toate nouă vin din teste care AU curățare în `finally`**. Deci nu lipsa regulii le-a produs, ci faptul că `finally` nu rulează când procesul moare. Șterse azi, la cererea lui Costin, după ce s-a stabilit cauza.
- **ce e mai grav decât orfanii, și e constatarea lui**: *„un test care poate crea o schemă în producție poate scrie și în alta.”* Confirmat: nimic la nivel de bază nu-l oprește — același utilizator, aceleași drepturi, `db.get_conn(schema)` acceptă orice nume care trece de `schema_valida()`, iar aia verifică **forma numelui**, nu apartenența. Măsurat: **18 teste numesc literal o schemă de firmă reală** (`tenant_001`, `002`, `003`, `013`, `014`, `016`) — toate pentru citire, dar bariera care le-ar opri să scrie nu există.
- **ce NU vede măsurătoarea**: n-am verificat fiecare din cele 18 dacă scrie; am verificat că regexul nu găsește `INSERT/UPDATE/DELETE` calificat cu numele schemei — dar scrierile se fac prin `get_conn(schema)` + SQL necalificat, exact forma pe care un scan pe text n-o vede. E aceeași limită ca la R66: calea de scriere se asamblează la rulare.
- **DECIS 26.08.2026 — varianta (b): utilizator de test cu drepturi doar pe `test_*` și `ztest_*`.** Motivul lui: *„e singura care pune bariera unde nu depinde de disciplina fiecărui test. Iar disciplina a fost prezentă — toate opt aveau `finally` — și n-a fost de ajuns.”* Varianta (c) a fost respinsă cu argumentul măsurătorii de ieri: *„e o măsurătoare pe cod, iar tu tocmai ai arătat că un scan pe text nu vede scrierile prin `get_conn(schema)`. Ar da verde fals pe exact forma pe care o urmărim.”* Iar **(a) rămâne ținta**, ca pas următor, cu condiția *„când cele 18 nu mai depind de firme reale”*.
- **MĂSURAT ÎNAINTE DE REPARAȚIE, cum a cerut — și cifra mea de ieri era greșită.** *„Măsoară întâi câte din cele 18 chiar au nevoie de datele acelea și câte le folosesc din comoditate.” Cele **18** erau un **grep naiv** — exact clasa de fals-pozitive pe care o numește docstringul gărzii din 29.07 (`test_teste_decuplate.py`): *un nume pasat ca STRING unei funcții pure nu e cuplare*. Trei încercări succesive au dat **18 → 6 → 4**, fiecare over-raportând, fiindcă fiecare număra **proza** (comentarii, docstringuri) sau numele **stubuite** cu `monkeypatch`. Cifra reală s-a obținut **citind**, nu scanând: **3**.
- **cele trei, numite**: `core/test_d406_active_duk.py` (citește `mijloace_fixe` din `tenant_013`, cu `SET search_path` + SQL necalificat) · `core/test_d390_reconciliere.py` (baseline **declarat** pe `tenant_013` și `tenant_016`, prin `get_conn(schema)` cu schema venită din `parametrize`) · `core/test_artefacte_pastrate.py` (citește catalogul pentru `tenant_001` — depinde de **existența** firmei, nu de datele ei; exact modul de eșec pentru care s-a scris garda: *după un wipe, sar tăcut sau pică*).
- **ȘI GARDA PERMANENTĂ DIN 29.07 LE RATEAZĂ PE TOATE TREI — raportează ZERO.** Criteriul ei prinde `get_conn("tenant_0XX")` **ca literal** și SQL **calificat** `FROM tenant_0XX.`. Cele trei folosesc o **variabilă sau o constantă** (`_SCHEMA`, `schema` din `parametrize`, parametru cu implicit) plus `SET search_path` cu SQL **necalificat**. Nu e o gardă slabă: e aceeași limită ca la instrumentul de ieri și ca la `_siruri` alaltăieri — **calea nu e un fapt textual**. A treia oară în trei ture, iar a treia oară s-a aprins într-un instrument scris de mine **după** ce clasa fusese numită.
- **ce înseamnă asta pentru varianta (b)**: cele trei vor pica la trecerea pe utilizatorul restrâns, și **e corect să pice** — Costin: *„NU le da drepturi de citire ca să treacă — aia ar reintroduce gaura. Fac parte din aceeași reparație: ori își creează propriile date, ori se declară ca teste pe date de producție, cu motivul.”* Dintre ele, `d390_reconciliere` **se declară deja** în docstring (*„pe firmele reale (4163)”*), deci pentru ea decizia e doar dacă declarația e suficientă.
- **condiția de deblocare**: decizia lui Costin între **(a)** o bază de test separată, iar `conftest` refuză să pornească suita pe `iconta_v2`; **(b)** un utilizator de test cu drepturi doar pe schemele `test_*`/`ztest_*`, deci bariera e în bază, nu în disciplină; **(c)** rămâne convenție, dar capătă gardă — un test care atinge o schemă din afara prefixului lui pică. Se închide când *„un test poate scrie într-o schemă de firmă”* nu mai e adevărat, sau nu mai e posibil fără ca ceva să se aprindă.

### R68 — Suita n-are bază proprie; separarea rămâne de făcut după ce testele se decuplează

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · P12 · **PRAG 3** *(nu produce nimic fals azi; e ținta de după R67)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `9cea90a`
- **măsurat la**: 2026-08-26 · **pe commit**: `9cea90a`
- **planul**: **NEACOPERIT**, aceeași lipsă ca la R67: planul descrie ce trebuie să fie adevărat despre DATE, nu despre unde rulează suita care le verifică. (METODA §25)
- **ce blochează**: `conftest.py` sursează datele de conectare ale producției; suita rulează pe `iconta_v2` ca `iconta_user`. **R67** pune bariera în drepturi (utilizator de test pe `test_*` / `ztest_*`), ceea ce se poate face acum. Baza separată — ținta reală — nu se poate, cât timp **3 teste** depind de firme persistente: `test_d406_active_duk.py`, `test_d390_reconciliere.py`, `test_artefacte_pastrate.py`.
- **de ce restanță SEPARATĂ de R67** *(decizia lui Costin)*: *„(a) și (b) au condiții diferite și se deblochează diferit. (b) se face acum; (a) se face când cele 3 nu mai depind de firme reale. Iar dacă rămân în aceeași restanță, închiderea lui (b) ar face-o să pară rezolvată — sau ar ține (b) deschisă până se face (a), care e altă muncă.”*
- **și o declarație NU e de ajuns** — tot el, despre `d390_reconciliere`, care își scrie în docstring că rulează *pe firmele reale*: *„o declarație spune că testul depinde de firme reale, nu îl împiedică să scrie în ele.”* Deci cele trei se decuplează, nu se documentează.
- **ce NU vede măsurătoarea**: cifra **3** s-a obținut **citind**, după ce trei scanuri succesive au dat 18 → 6 → 4. Dacă apare un al patrulea test cuplat, niciun instrument de azi nu-l va vedea — nici garda din 29.07, nici scanurile mele. Asta e chiar motivul pentru care bariera trebuie să fie în **drepturi**, nu în măsurătoare.
- **condiția de deblocare**: **când cele 3 nu mai depind de firme reale** — fiecare ori își construiește subiectul (schemă efemeră din `tenant_template.sql`), ori dispare. Abia atunci baza separată devine posibilă fără a pierde acoperire. Se închide când `conftest` poate refuza să pornească pe `iconta_v2` și suita rămâne verde.

### R69 — O declarație depusă pe un regim care s-a schimbat între timp nu contrazice pe nimeni

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · **P18** · TRASEE X.8 și XI · **PRAG 2** *(nimic fals afișat azi, dar efectul e producibil pe **6 firme din 17**, cu **55 de declarații depuse**)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `dfc129d`
- **măsurat la**: 2026-08-26 · **pe commit**: `dfc129d`
- **planul**: **ACOPERIT, și acoperirea e chiar formularea restanței.** `PLAN_ARHITECTURA.md`: *„O modificare cu efect retroactiv declanșează **P18**”*, iar P18 cere ca efectul asupra a ce s-a depus să producă **contradicție vizibilă**, nu aplicare tăcută. Planul nu cere o poartă aici — cere o afirmație care se arată. De aceea nu e o a doua jumătate a lui R46, ci altă clasă. (METODA §25)
- **ce blochează**: `POST /firma-profil/regim-tva` și `PUT /vector` schimbă ce se datorează. Din 26.08 refuză peste o **perioadă închisă** (R46). Dar o declarație se poate depune pe o lună care **nu** e închisă — iar atunci schimbarea trece, iar declarația rămâne depusă pe un regim care nu mai există, fără ca nimic să spună asta.
- **de ce e clasa mai mare, măsurat**: poarta de la R46 se aplică unde există perioade închise — **1 firmă din 17**. Contradicția de aici se aplică unde există declarații depuse — **6 firme din 17, cu 55 de declarații** (20 · 20 · 12 · 1 · 1 · 1). Deci partea neacoperită de R46 nu era o rămășiță: era **majoritatea cazului**.
- **ce trebuie, în cuvintele lui Costin**: *„la schimbarea vectorului sau a regimului, se determină declarațiile deja depuse în intervalul atins, iar fiecare devine vizibilă ca «depusă pe un regim care s-a schimbat între timp». Iar decizia de a rectifica rămâne a omului, cum spune planul.”* **Nu e o poartă — e o contradicție care se arată.** Distincția e aceeași cu cea din R58: `inchidere_luna` afirmă, `perioade_blocate` oprește; aici avem nevoie de prima, nu de a doua.
- **de ce restanță proprie și nu condiție rămasă în R46** *(decizia lui)*: *„e o clasă diferită, nu o jumătate rămasă. Poarta pe perioada închisă apără trecutul consemnat ca închis. Cealaltă apără trecutul DEPUS.”* Plus regula generală pe care a numit-o: *„o restanță care rămâne deschisă pentru altceva decât ce numește devine o listă de lucruri neterminate, nu o restanță.”*
- **ce NU vede măsurătoarea**: câte schimbări de vector s-au făcut **deja** peste declarații depuse. `firma_profil` n-are istoric al vectorului — se scrie peste — deci întrebarea *s-a întâmplat vreodată?* nu se poate pune pe date. Dacă răspunsul contează, istoricul trebuie să existe înainte, iar aia e o construcție separată.
- **condiția de deblocare**: la schimbarea vectorului sau a regimului, declarațiile depuse din intervalul atins sunt **numite** — nu numărate — iar starea lor devine vizibilă acolo unde se vede declarația, nu doar în răspunsul rutei. Se închide când o schimbare de regim pe o firmă cu declarații depuse produce o contradicție pe care contabilul o vede fără s-o caute, cu gard.

### R70 — O rută poate fi scrisă, gardată și verde, fără ca nimic s-o cheme

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · TRASEE · METODA §22 · **PRAG 2** *(măsurat: **5 din 193** de pași n-au apelant în `static/`; unul e declarat în cod ca intenționat, patru nu)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `0851725`
- **măsurat la**: 2026-08-26 · **pe commit**: `0851725`
- **planul**: **NEACOPERIT.** `PLAN_ARHITECTURA.md` descrie ciclul unui **document** și regulile registrului; nu spune nicăieri că o cale de cod trebuie să fie **ajunsă**. Cel mai aproape ca formă e **P13** (*ecranul spune una, serverul face alta*), dar acolo cele două există și se contrazic; aici a doua nu e chemată deloc. (METODA §25)
- **ce blochează**: instanța e a mea și e de ieri. Ruta `POST /public/confirma-email` a fost scrisă, i s-a construit **gardul** (`test_portal_acces.py` verifică că aplică schimbarea și că reconfruntă adresa), a trecut **toată** suita, a intrat prin poarta verde — și **nimic n-o chema**. Linkul din email ducea în SPA cu fragmentul `#email-nou=`, pe care `app.js` nu-l cunoștea; SPA randa pagina publică, iar tokenul rămânea neconsumat. Verificat pe date după probă: `schimbari_email.confirmat_la` = **NULL**, `users.email` neschimbat, `urme_portal` cu `email_cerut` și fără `email_confirmat`.
- **de ce n-a văzut-o nicio gardă**: toate gărzile pe care le-am construit verifică ce face ruta **dacă e chemată**. Niciuna nu întreabă **dacă e chemată**. E aceeași formă cu *coloana și calea ei de scriere*, mutată un nivel mai sus: **ruta și calea ei de apelare intră împreună**.
- **măsurat, ca să nu rămână la instanță**: din cele **193** de rute care schimbă date, **5** n-au niciun apelant în `static/` — `banca/parse-extras`, `calcul-cm`, `import-efactura`, `s1003-valideaza`, `s1005-valideaza`. Prima e **declarată** în cod: *`[api_intern_v1] parsare extras la upload - fara UI inca, pastrat deliberat`*. Celelalte patru nu spun nimic. Deci clasa are membri legitimi, iar un instrument are nevoie de o cale de **declarare**, ca `NEDOCUMENTARE` la trasee — altfel ar cere ștergerea a ce e păstrat intenționat.
- **ce NU vede măsurătoarea**: caută ultimul segment al căii în textul din `static/`. O rută chemată printr-o cale **compusă la rulare** (`"/tenants/" + id + sufix`) n-ar fi găsită — deci cifra 5 e un **plafon superior** al celor fără apelant, nu un număr exact. Aceeași limită ca la celelalte scanuri pe text din zilele astea, a patra oară.
- **REPARAT ȘI CONFIRMAT PE DATE 26.08.2026, 20:04.** `app.js` prinde fragmentul, cheamă ruta și **spune** ce s-a întâmplat. Costin a apăsat linkul; verificat imediat în bază: `schimbari_email.confirmat_la` = **20:04:39** (era NULL), `users.email` = adresa **nouă** (era cea veche), iar `urme_portal` are acum `email_confirmat` cu *de la ce, la ce*. **Confirmarea e a lui, nu a mea** — reparația nu se putea proba din partea mea: cere apăsarea unui link dintr-un email la care n-am acces. Gărzile erau verzi și înainte, și după.
- **CEALALTĂ JUMĂTATE, măsurată 26.08 seara la cererea lui Costin**: rutele de **citire**. Din **169** de GET-uri care nu sunt pași, **13** n-au apelant după căutarea brută — dar citirea le reduce la **6**. Patru erau **fals-pozitive** ale ancorei mele (`kpi`, `facturi-primite`, `chitante/…/pdf`, `facturi/…/pdf` — căi compuse la rulare, găsite sub o ancoră mai scurtă), iar trei sunt cerute de **browser**, nu de JS (`favicon.ico`, `robots.txt`, `sitemap.xml`) — legitime prin construcție. **A cincea oară** când un scan pe text over-raportează și citirea corectează.
- **~~cele șase reale~~ — CORECTAT 26.08 seara, și corecția e a mea.** Am scris că `s1003-xml`/`s1005-xml` fac pereche cu rutele de validare și că *o funcționalitate întreagă are rute și niciun ecran*. **E fals.** Ecranul există — *Firme › Bilanț anual*, card cu descrierea *„S1005 micro / S1003 mici, validare ANAF”* — iar el cheamă `` `/tenants/${t.id}/${tip()}-valideaza` ``: segmentul se **compune dintr-o variabilă**, deci literalul `s1003-valideaza` nu apare nicăieri. La fel `d406-active`/`d406-stocuri` (`declaratii.js`), `stat-plata/*` și `perioade-blocate/istoric`. **A șaptea oară** când un scan pe text acuză pe nedrept.
- **ce rămâne, după verificare prin citire**: **cinci** rute pe care nu le cheamă nimic — `urme-portal` (a mea, de ieri, cea care lasă punctul (3) din R62 nesatisfăcut) · `jurnal-marja` · `calcul-cm` · `import-efactura` · `banca/parse-extras` (singura **declarată** în cod ca intenționată). Nu 13, nu 6: **5**, dintre care 4 nedeclarate.
- **ȘI RESTANȚA CERUTĂ PENTRU `s1003`/`s1005` NU SE DESCHIDE.** Costin a cerut-o pe premisa pe care i-am dat-o eu (*patru rute, o funcționalitate întreagă, niciun ecran*). Premisa e falsă, deci restanța n-are obiect. **A patra oară azi când un raport cade pe o premisă — primele trei erau ale lui, asta e a mea.**
- **GARD CONSTRUIT 26.08 seara, cu domeniul îngust cerut**: `core/test_ruta_fara_apelant.py` — *o rută **nouă** fără apelant nu trece*; cele existente rămân într-un `_BASELINE` declarat, clichet pe **mulțime**, nu poartă retroactivă. Baseline-ul e descris în antet ca **fotografie, nu listă de vinovați**: conține și rutele reale (cele cinci de mai sus) și artefactele detectorului, iar fiecare intrare primește motivul **când e atinsă**.
- **antetul gardului scrie toate cele patru detectoare încercate și cum greșește fiecare** — ultimul segment (ratează căile compuse) · bucăți cu `/` (ratează dispecerizarea prin tabel) · segmente separate (trece orice) · bucăți fără `/` (forma de azi, ratează încă compunerea pe grup). *A patra e cea mai puțin greșită, nu cea corectă* — de aceea gardul asertează pe mulțime, unde un fals-pozitiv rămâne fără să mintă despre altceva. Calibrare pe ambele direcții, cu instanța reală: dispecerizarea prin tabel (`ruta: "nota-sgr"`) **nu** e raportată, iar o rută inventată fără ecran **e**.
- **CORECTAT 27.08.2026 — și corecția e tot a mea, a doua pe aceeași restanță.** Am scris de două ori că *„celelalte patru nu spun nimic"*. **E fals: nedeclarate erau DOUĂ.** `jurnal-marja` (`main.py:7815`) și `calcul-cm` (`main.py:7947`) purtau deja **exact** marcajul lui `banca/parse-extras` — `[api_intern_v1] … fara UI inca, pastrat deliberat`. Mai mult: **registrul ăsta îl citase deja** pe primul, în tabelul artefactelor L3 (*„ruta `/tenants/{id}/jurnal-marja` există, cu comentariul propriu"*). Deci cele două afirmații se contraziceau **în același fișier**, iar eu am scris-o pe cea greșită fără să caut a doua. Cifra care rămâne: **5 rute fără ecran, din care 3 declarate dinainte și 2 nedeclarate.** *(Felul greșelii, fără contor: nu un scan care a acuzat pe nedrept — de data asta instrumentul n-a fost implicat. Am scris o afirmație despre cod fără să caut ce era deja scris despre el, în chiar fișierul în care scriam. Nu numesc «a câta oară»: n-am un instrument care să numere clasa, iar o cifră care nu se poate recalcula e o amintire, nu o măsurătoare.)*
- **DECLARATE 27.08.2026, fiecare cu propoziția ei** *(Costin: „se declară, dar nu toate la fel — cere fiecare o propoziție diferită")*:
  - `banca/parse-extras`, `calcul-cm`, `jurnal-marja` — **declarate dinainte**, rămân cum sunt. Ultimele două nu sunt rămășițe: `calcul-cm` are producător întreg (`core/baza_cm.py`, gardat de `core/test_baza_cm.py`) și temei (OUG 158/2005 art. 10 al. 4), iar `jurnal-marja` are temei (CF art. 311/312 + norme pct. 86) și e trecut în registru la **prag 2.6** ca *absență de randare, cu producătorul scris*. Amândouă sunt **flux neterminat pe partea de ecran**, nu rest de șters.
  - `urme-portal` — declarată cu propoziția lui Costin: *„scrisă, necitită de om; punctul (3) din R62 rămâne nesatisfăcut"*. Iese din listă când se construiește ecranul.
  - `import-efactura` — declarată **după verificare**, nu după presupunere. Costin: *„un import se poate declanșa dintr-un job."* Căutat pe 27.08 în `static/`, în tot `*.py`, în `crontab -l` și în **timerele systemd**: **niciun apelant**. Calea automată există, dar **nu trece pe rută** — `core/spv_receive.py` cheamă direct `_factura_din_parsat`, aceeași conductă, alt capăt. Ruta e **upload manual XML/ZIP fără buton în UI**.
- **GARD PE DECLARAȚIA ÎNSĂȘI, 27.08.2026**: `test_cele_cinci_reale_isi_declara_lipsa_ecranului` din `core/test_ruta_fara_apelant.py` — cele cinci rute fără ecran trebuie să poarte marcajul `[api_intern_v1]` **pe linia decoratorului**. O declarație care se poate șterge tăcut e o promisiune, nu o declarație. Asertează pe **prezența marcajului**, nu pe textul motivului (ar fi gardă pe text — METODA §23). RED-proof: cu o rută care **are** ecran în listă, gardul pică.
- **~~ce NU face nici acum: declararea e de mână~~ — FĂCUT 27.08.2026**, la cererea lui Costin (*„leagă baseline-ul de marcaje […] iar când o faci, spune ce se schimbă în semantica gardului"*). **Ieri gardul verifica o LISTĂ, azi verifică un MARCAJ.** `_BASELINE` ținea amestecate două lucruri diferite, iar despărțirea lor e chiar câștigul:
  - **`declarate()`** — **derivat din cod**: decoratorul se citește ca **nod de AST** (`app.<metodă>("cale")`), iar marcajul `[api_intern_v1]` se caută **pe linia lui**, aflată din `lineno`. Un comentariu rătăcit la 50 de linii distanță nu poate declara nimic — calibrat pe direcția asta. **7 rute** azi. O rută care primește ecran și pierde marcajul **iese singură** din mulțime; jumătatea derivată n-are nevoie de clichet.
  - **`_ARTEFACTE`** — cele **25** rămase, grupate pe **felul greșelii detectorului**: (a) contract extern chemat de integratori · (b) cerute de browser · (c) cale compusă la rulare · (d) fără ecran, pe suprafață declarată. Aici lista de mână e legitimă: descrie **limitele instrumentului**, nu intenția codului.
  - **regula care se poate citi de la distanță**, scrisă în antet: *o intrare nouă în `_ARTEFACTE` e o mărturisire despre detector; un marcaj nou în `main.py` e o decizie despre produs.* Nu se mai pot confunda.
  - **RED-proof**: cu marcajul scos de pe `calcul-cm` (în memorie, fișierul neatins), ruta **iese** din mulțimea derivată — deci ar fi raportată. Plus anti-vacuu: dacă `declarate()` s-ar goli, gardul pică.
- **condiția de deblocare**: decizia lui Costin între **(a)** gard cu clichet pe 5 și cale de declarare pentru cele intenționate — cele patru nedeclarate se declară sau se scot; **(b)** doar cele patru se lămuresc acum, iar gardul se face după; **(c)** altceva. Se închide când *o rută nouă fără apelant* nu mai poate trece poarta tăcut.

### R71 — Ce a scos prima exercitare pe date: șapte lucruri pe care nicio gardă nu le vede

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · TRASEE T35 · DS cap.6 · **PRAG 3** *(niciunul nu produce o cifră falsă; toate produc un om care nu înțelege ce s-a întâmplat)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `0851725`
- **măsurat la**: 2026-08-26 · **pe commit**: `0851725`
- **planul**: **ACOPERIT ca principiu, neacoperit ca listă.** `DESIGN_SYSTEM cap.6` cere validări preventive **cu mesaj explicativ**, iar P13 cere ca ecranul și serverul să spună același lucru. Cele șapte sunt instanțe, nu o clasă nouă. (METODA §25)
- **ce blochează**: Costin a parcurs cei opt pași ai probei R62 pe o firmă de test și a adus **șapte observații**, consemnate aici ca listă închisă, în ordinea în care le-a întâlnit:
  1. **Refuzul despre email apare sub câmpul de CUI** la crearea firmei — omul se uită la câmpul greșit.
  2. **Lista nu confirmă crearea firmei**, iar contorul rămâne pe cifra veche până la reîncărcare. *(~~REPARAT 26.08~~ — **reparația din 26.08 NU FUNCȚIONA**; reparată și **probată** abia pe 27.08, vezi mai jos.)*
  3. **Ghidul de bun venit apare și în portalul clientului**, cu pașii cabinetului (migrare, vector fiscal, solduri, salariați). Clientul nu face niciunul.
  4. **Fereastra „Acces cont” se deschide parțial sub marginea ecranului** — butoanele nu se văd fără micșorarea paginii.
  5. **Mesajul „link expirat sau folosit” nu distinge două lucruri diferite** — cine l-a folosit deja crede că a pierdut cele 48 de ore.
  6. **Emailul de confirmare a adresei nu spune că linkul e de unică folosință**, deși cel de logare o spune. Mențiunea lipsește exact unde contează mai mult.
  7. ~~Butonul „Trimis ✓” nu se resetează~~ — **RETRASĂ de Costin, 26.08 seara**: *„butonul chiar trimite, starea «Trimis ✓» e răspunsul, nu una rămasă de la o cerere anterioară. Am greșit încadrarea.”* Rămâne în listă tăiată, nu ștearsă: o observație retrasă se poate reîntoarce, iar cine citește trebuie să vadă că a fost cântărită.
  8. **„Dacă emailul există, ai primit linkul de logare” nu distinge trei lucruri**: adresa nu e în sistem · adresa s-a schimbat între timp · trimiterea a eșuat. Formularea e corectă ca **anti-enumerare**, dar în proba din 26.08 a ascuns exact ce se întâmplase. Adăugată de Costin, în locul celei retrase. *(Partea despre înghițirea excepției s-a desprins de aici la cererea lui — nu e o formulare, e o defecțiune care nu se poate diagnostica: **R73**.)*
- **5 și 6 merg împreună** *(Costin)*: mesajul care distinge *folosit* de *expirat*, și mențiunea în email că linkul e de unică folosință.
- **ȘI O REÎNCADRARE, măsurată pe date**: ce părea *al doilea defect* — *firma se creează în ciuda refuzului afișat* — **nu e asta**. Poarta de duplicat **există și funcționează**: `tenant_provisioning` refuză cu `ValueError` → 400, per cabinet. Verificat pe date: cele două firme `PROBA PORTAL SRL` au CUI-uri **diferite** (`14399840` la 18:58:07 și `2816464` la 19:02:26), amândouă sub cabinetul 1968 — deci a doua **nu era** un duplicat. Reconstituirea: prima apăsare a creat firma **în tăcere** (observația 2), omul n-a putut ști că a mers, a apăsat din nou, iar poarta a refuzat **corect** — dar refuzul a **arătat** ca și cum ar fi fost ignorat, fiindcă firma exista deja. **Cauza nu e poarta, e tăcerea de după succes.** Reparat azi: crearea se confirmă, iar lista se reîncarcă înainte de confirmare.
- **ce NU vede măsurătoarea**: n-am reprodus fiecare din cele șapte pe cont propriu — sunt observațiile lui, notate ca atare. Trei dintre ele (1, 4, 7) sunt de așezare sau de stare a ecranului, iar acolo verificatorul nu ajunge — clasa e declarată nemăsurabilă în CLAUDE.md.
- **CE A SCOS REPROBAREA din 26.08 seara**, și e o lecție despre măsurători, nu despre cod: Costin a reprobat pasul 5 și a raportat **două defecte noi** — *ruta respinge un rând valid* și *linkul de logare nu ajunge, prag 1*. **Niciunul nu există.** Amândouă stăteau pe o premisă care se schimbase sub el: confirmarea **reușise** la 20:04:39, iar adresa de autentificare devenise cea nouă. Rândul nu mai e valid fiindcă e **confirmat**; linkul de logare n-a ajuns fiindcă `+proba` **nu mai e adresa nimănui** (`SELECT id FROM users WHERE email=%s AND activ` → niciun rând → niciun token → niciun email; verificat și în `tokene_activare`, unde ultimul rând e de la 19:33). **Măsurătoarea mea de «confirmat_la = NULL» era corectă când am făcut-o și depășită 40 de minute mai târziu** — iar el a citit-o ca stare curentă. O cifră fără momentul ei nu e o măsurătoare, e o amintire.
- **condiția de deblocare**: se închide când toate șapte sunt **reparate sau retrase, una câte una** — nu ca grup. Costin a cerut explicit: *„consemnează-le. Nu le repara acum.”* Prima (2) e închisă **abia acum**, cu probă în ambele direcții — vezi mai jos.

- **CORECȚIE 27.08.2026, și e a mea: reparația observației (2) din 26.08 nu funcționa.** Codul chema `incarca()` după creare. Funcția aia **nu există în scopul acela**: e declarată în `ecranBanca` (`firme.js`, ~2.000 de linii mai jos), alt scop de nivel superior. Deci la fiecare creare de firmă se arunca `ReferenceError`, **prins de `catch`-ul de alături** — lista nu se reîncărca și bannerul de confirmare nu apărea. **Am raportat-o reparată, iar Costin a acceptat-o.** N-a găsit-o nicio gardă: `ruff` nu urmărește scopuri în JS, iar suita nu deschidea ecranul.
- **de unde a ieșit**: lucram exact pe funcția aia pentru R72. Nu dintr-un instrument — dintr-o citire.
- **REPARATĂ ȘI PROBATĂ 27.08.2026, în ambele direcții**, cu Playwright, fără să atingă baza (răspunsul la `POST /tenants` e servit din browser): cu fișierul real, bannerul apare — *„Firma … a fost creată și apare în listă."* — și pagina nu aruncă nimic; cu **bugul repus** (`incarcaFirme` → `incarca`, servit modificat din memorie), bannerul **nu** apare. Fără direcția a doua, proba verde n-ar fi spus nimic. *Și un amănunt care explică de ce a trecut neobservată: în varianta stricată nu apare nicio eroare de pagină — `catch`-ul o înghite.*

### R72 — O firmă adăugată din greșeală nu se poate scoate

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · **P17** · interdicția 39 · **PRAG 2** *(instanța e reală și e a noastră: două firme `PROBA PORTAL SRL` create azi, care rămân în portofoliu fiindcă nu există cale de a le scoate)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `3391371`
- **deschisă pe commit**: `9ece318`
- **măsurat la**: 2026-08-26 · **pe commit**: `9ece318`
- **planul**: **ACOPERIT pe jumătatea grea, neacoperit pe cea ușoară.** `PLAN_ARHITECTURA.md` tratează **P17 — retenție**: *„ce categorie de dată se păstrează, cât, pe ce temei, **ce împiedică ștergerea**”*, iar **interdicția 39** oprește *o ștergere care atinge date aflate sub obligație de păstrare*. Deci planul spune deja de ce o firmă **cu evidență** nu se șterge. Ce nu spune: ce se face cu una **fără** evidență, adăugată din greșeală acum două ore. (METODA §25)
- **ce blochează**: nu există **nicio** rută de ștergere a unei firme. Căutat în tot `main.py`: `DELETE /tenants/{id}` nu există. Singura cale e `core/gdpr_sterge.py`, care șterge un **cabinet întreg** — schemele lui, rândurile din `public`, fișierele de pe disc. Un cabinet care adaugă o firmă din greșeală nu are ce apăsa.
- **cele două lucruri de decis, în ordinea lor** *(Costin)*: **(1)** *„ștergerea unei firme trebuie să curețe tot ce depinde de ea, altfel produce orfanii din R44”* — instanța e la îndemână: dacă aș fi șters azi firmele de probă, `urme_portal` și `schimbari_email` ar fi rămas legate de un tenant inexistent; **(2)** *„o firmă cu evidență nu se șterge — se dezactivează. Distincția dintre cele două cazuri e prima decizie.”*
- **de unde a ieșit**: din cerința de a șterge cele două firme de probă după confirmarea reparației. Confirmarea a venit; ștergerea n-a fost posibilă. **Restanța nu e despre firmele noastre** — ele rămân până există o cale curată — ci despre lipsa căii.
- **ȘI DUPLICATUL A COSTAT DEJA, în aceeași zi**: la pasul 8 al probei, Costin a deschis ecranul *Acces client* pe firma cu **CUI 14399840** — duplicatul accidental — și a citit *„Niciun cont de client încă”* ca pe o **afirmație falsă de prag 1**. Verificat pe date: firma aia are **0** conturi de client, iar cele două (`+portal`, `+client2`) sunt pe cealaltă, **CUI 2816464**. Ecranul spunea adevărul, iar interogarea rutei e corectă. **Două firme cu același nume au făcut un ecran corect să se citească drept fals** — deci duplicatul nu e dezordine, e o sursă de diagnostic greșit. E al treilea raport de defect al zilei care cade pe o premisă, și singurul a cărui cauză se poate scoate din produs.
- **ce NU vede măsurătoarea**: n-am numărat **ce anume** depinde de un `tenant_id` în `public` (`user_tenants`, `urme_portal`, `schimbari_email`, `declaratii_depuse`, `solicitari_client`, coada…). Lista aia e chiar prima parte a reparației, nu a măsurătorii.
- **MĂSURAT 27.08.2026, ÎNAINTE de orice rută** *(Costin: „măsoară întâi, arată-mi lista, apoi construim ruta pe ea. Nu scrie `DELETE` pe o listă pe care n-o avem.")*. Interogări **numai SELECT**, pe baza de producție.
  - **13 tabele din `public` poartă `tenant_id`** (rânduri la măsurătoare): `alerte_control_emise` 15 · `anunturi_cabinet` 0 · `audit_log` 117.252 · `declaratii_coada` 2 · `declaratii_depuse` 55 · `pachet_povestea` 0 · `reges_chei` 0 · `reges_mesaje` 0 · `schimbari_email` 1 · `solicitari_client` 0 · `spv_token` 0 · `urme_portal` 4 · `user_tenants` 23. Căutat pe **orice** coloană cu `tenant` în nume, nu doar pe `tenant_id`: în plus iese doar `declaratii_depuse_curente` (VIEW, deci derivată) și `gdpr_stergeri.nr_tenanti` (un contor, nu o referință).
  - **CONSTATAREA SEPARATĂ pe care a cerut-o**: **10 din 13 poartă `tenant_id` FĂRĂ cheie străină** — `alerte_control_emise`, `audit_log`, `declaratii_coada`, `declaratii_depuse`, `pachet_povestea`, `reges_chei`, `reges_mesaje`, `schimbari_email`, `spv_token`, `urme_portal`. Nimic nu le leagă, deci nimic nu le-ar opri să rămână în urmă. Doar **3** au FK: `user_tenants` (ON DELETE **CASCADE**), `anunturi_cabinet` și `solicitari_client` (ON DELETE **NO ACTION**).
  - **ȘI DE-AICI IESE UN DEFECT AL CĂII EXISTENTE, nu al celei viitoare**: `core/gdpr_sterge.py` — singura ștergere din aplicație — atinge **2 din cele 13** (`audit_log`, `user_tenants`) și apoi face `DELETE FROM public.tenants`. Celelalte **11** rămân. Iar două dintre ele au FK cu **NO ACTION**: în ziua în care un cabinet are o `solicitare_client` sau un `anunt`, ștergerea GDPR **se oprește cu eroare de cheie străină**, la mijloc. Azi n-a lovit fiindcă amândouă tabelele au **0** rânduri — deci calea n-a fost niciodată exercitată pe un caz cu conținut.
  - **CEI 67 DE ORFANI, identificați**: `audit_log` **65** (tenant 14963: 44 · tenant 13245: 21) + `alerte_control_emise` **2** (tenant 13245, 15–16.08). Sunt exact cei rămași după dispariția firmelor-fantomă. *(Distinct de `audit_log.tenant_id IS NULL` — 108.945 de rânduri care nu privesc nicio firmă; alea nu sunt orfani.)* **R44 și R50 stăteau pe necunoscuta asta.**
  - **ȘI UN AL DOILEA FEL DE ORFAN, pe care nu-l vede nicio coloană**: **28** de scheme non-sistem față de **19** rânduri în `tenants` → **9 scheme fără firmă** (`test_d100_profit`, `test_d112_cadou`, `test_d112_ded_supl`, `test_d301_zero_ruptura`, `test_d390_nota1`, `test_ded_generalizare`, `ztest_cresa`, `ztest_cultural`, `ztest_exces_van_d112`). Rezidul suitei care rulează pe baza de producție — **R67**. Invers, 0: nicio firmă fără schemă.
  - **PENTRU PUNCTUL (2), jumătatea deja construită**: `tenants.activ` **există și e respectat la citire** — `auth_api.tenantii_userului` filtrează `activ = true` pe toate trei rolurile. Ce lipsește e **scrierea**: nimic nu pune `activ=false` nicăieri, coloana e scrisă doar la INSERT. Deci *dezactivarea* nu e o construcție nouă, e o coloană cu jumătate de cale — aceeași formă ca `patron_nume` din R66.
- **ce NU vede măsurătoarea asta**: (a) **fișierele de pe disc** — `gdpr_sterge` șterge directoare per cabinet; ce ține de o singură firmă n-am numărat; (b) **ce înseamnă „are evidență"** — n-am pus niciun criteriu, fiindcă e chiar decizia (2) a lui Costin; (c) tabelele **din schema firmei** nu intră aici: ele pleacă odată cu `DROP SCHEMA`.
- **CONSTRUITĂ 27.08.2026 pe deciziile lui, punct cu punct** (`core/tenant_stergere.py`):
  - **(2) „are evidență"** = un rând în `declaratii_depuse` **sau** `declaratii_coada` **sau** orice document emis din schema firmei. Cele patru numite de el (notă contabilă · factură · stat de plată · artefact păstrat) plus **trei adăugate cu motivul**: chitanțe, e-Factura și e-Transport au **plecat** din firmă la fel de tare ca o factură — prima la un om, ultimele două deja la ANAF. Adăugarea împinge în direcția **prudentă**: mai multe firme refuzate, niciuna ștearsă din greșeală.
  - **și o tabelă LIPSĂ din schemă nu se numără ca zero**: `evidenta` întoarce *„nu pot decide"* și **refuză**. Un zero tăcut ar transforma o redenumire de tabelă într-o firmă ștearsă fără urmă — chiar clasa pe care modulul există s-o oprească.
  - **(1) toate cele 13**, plus schema, în **ordinea cerută**: `public` → `DROP SCHEMA` → rândul din `tenants`. Totul într-o singură tranzacție, deci eșecul dă înapoi tot; ordinea rămâne cea cerută fiindcă e singura care lasă o stare **reluabilă** dacă tranzacția se sparge vreodată în bucăți.
  - **(3) `gdpr_sterge` cheamă ACEEAȘI funcție** pentru fiecare firmă a cabinetului, cu `motiv="gdpr_cabinet"`. Nu mai are listă proprie. *(Costin: „altfel avem două căi de ștergere care se vor rupe separat — iar una din ele e deja ruptă.")*
  - **confirmarea e pe CUI, nu pe nume** — instanța care a produs restanța sunt două firme cu **același nume**. O confirmare pe nume ar fi acceptat ștergerea celeilalte.
  - **urma**: `public.firme_scoase`, append-only, scrisă **înainte** de ștergeri (numele, CUI-ul și schema dispar odată cu rândul din `tenants`). Poartă `tenant_id` și **nu** se șterge — declarată în `NU_SE_STERG` cu motivul, iar garda verifică declarația. *O urmă ștearsă de propriul act nu e o urmă.*
  - **dezactivarea**: `tenants.activ` primește în sfârșit o cale de scriere, **în ambele sensuri**, iar lista se poate cere cu `inactive=true`. O ușă cu sens unic ar fi fost o pierdere, nu o ordonare.
- **PROBATĂ PE DATE, nu doar gardată** — două probe pe firme **sintetice**, curățate după ele, pe baza de producție:
  1. **ștergerea**: refuză pe evidență · refuză pe confirmare greșită · pe firma goală curăță toate cele 13 + schema + rândul, lasă urma cu numărătoarea corectă (`audit_log: 2, urme_portal: 1, alerte_control_emise: 1`), și **nu mișcă nimic din afara firmei** (19 firme înainte, 19 după, toate totalurile neschimbate).
  2. **GDPR**: calea **VECHE** rulată într-un `SAVEPOINT`, pe un cabinet cu o solicitare de client — **eșuează**, exact cum scria citirea de cod: *„violates foreign key constraint `solicitari_client_tenant_id_fkey`"*, **după** ce `DROP SCHEMA` rulase deja. Calea nouă trece și curăță tot. **Deci defectul nu era o deducție, era reproductibil.**
- **ECRANUL, parcurs cu Playwright pe amândouă ramurile** (nu e unul din cele 5 din `nav_ecrane`, deci scanul de acoperire nu ajunge la el — l-am parcurs explicit): firma cu evidență primește refuzul **cu ce s-a găsit** enumerat; firma fără evidență primește câmpul de confirmare, iar butonul rămâne inactiv pe CUI gol și pe CUI greșit și se activează **numai** pe cel corect. **axe: 0 încălcări** pe desktop și pe Pixel 5; fără revărsare orizontală; nicio țintă de atingere sub 24px.
- **ce NU face, declarat**: nu șterge backupul off-site (limită deja scrisă la GDPR) · nu repară orfanii deja existenți din R50 (n-au tenant, deci nu se pot scoate pe firmă) · **nu decide singur** dacă o firmă „merită" ștearsă — refuză și **spune ce a găsit**.
- **ȘI UN ORFAN GĂSIT ÎNAINTE DE PRIMA APĂSARE REALĂ, 27.08.2026** — cerut de Costin: *„începe cu 2816464 — cea cu cele două conturi de client. Aia probează și curățarea lor."* Măsurat înainte de a-i da pașii: ștergerea firmei ia rândurile din `user_tenants`, dar **nu** rândul din `users`. Cele două conturi (`+portal`, `+client2`) ar fi rămas **active, fără nicio firmă** — pot cere în continuare un link de logare, intră în portal și nu văd nimic. **E orfanul din R44/R50 mutat pe un OM.** Clasa era **goală** (0 clienți fără firmă); prima apăsare i-ar fi produs pe primii doi.
- **reparat înainte de apăsare, nu după**: un cont de client rămas fără nicio firmă se **dezactivează**, nu se șterge — *identitatea unui om nu e proprietatea unei firme*, chiar lecția din R62, iar `activ=false` închide magic-link-ul, singura ușă a portalului. Un cabinetist nu intră în regulă: el ține de cabinet. **Previzualizarea îi numește pe nume**, cu email cu tot, ca omul să vadă înainte de a confirma.
- **probat în trei direcții** (firme și clienți sintetici, curățate după): clientul legat **numai** de firma ștearsă → dezactivat · clientul care mai are o firmă → **neatins** · cabinetistul → **neatins** · și niciun rând din `users` **șters**. Plus un invariant pe date în gardă: *niciun cont de client activ fără nicio firmă*, azi 0.
- **ȘI URMA A DEVENIT CITIBILĂ, 27.08.2026 — a doua instanță a clasei declarate în aceeași dimineață.** `public.firme_scoase` a fost construită seara ca urmă care supraviețuiește ștergerii… și n-o citea niciun ecran. Adică **exact** ce declarasem la `urme-portal` cu douăsprezece ore înainte: *scrisă, necitită de om*. Am numit-o eu, înainte s-o găsească Costin; el a ales varianta (a): *„o urmă pe care n-o poate deschide nimeni fără `psql` nu e urmă pentru cabinet, e urmă pentru administratorul serverului."* Construit: `GET /firme-scoase` + ecranul **„Firme scoase"**, lângă „Firme dezactivate", cu ce s-a curățat, cine a apăsat și urmele păstrate.
- **URMELE PORTALULUI SUPRAVIEȚUIESC SCOATERII — dar NU unei ștergeri GDPR.** Costin, înainte de prima apăsare: *„cele 4 rânduri din `urme_portal` se păstrează. Sunt singura dovadă că traseul R62 a fost parcurs pe date. Registrul spune ce am făcut; alea arată ce a înregistrat aplicația."* Se copiază în `firme_scoase.urme_pastrate` (jsonb) **înainte** de ștergeri: cele 4 din `urme_portal` **plus** rândul din `schimbari_email`, fiindcă acela e cealaltă jumătate a aceleiași dovezi (confirmarea de la 20:04:39).
- **și jumătatea care nu era în cerere**: urmele conțin **adrese de email**, deci date personale. La `gdpr_cabinet` **nu se copiază nimic** — acolo scopul actului e chiar dispariția datelor, iar un log care le-ar păstra ar anula ștergerea pe care o consemnează. Regula e condiționată de `motiv`, iar garda o verifică **structural**, pe nodul de comparație, nu pe text: un apel necondiționat n-ar trece. **Probat în ambele direcții** pe firme sintetice: la scoatere urmele ajung întregi în `urme_pastrate` (cu conținut cu tot) și dispar din tabela originală; la GDPR coloana rămâne `NULL`.
- **cele două firme `PROBA PORTAL` rămân neatinse.** Calea există; apăsarea e a lui.
- **condiția de deblocare**: *(cea de atunci)* decizia lui Costin pe cele două puncte, apoi o cale care le respectă. Se închide când o firmă adăugată din greșeală se poate scoate, iar una cu evidență **nu** se poate — cu gard pe amândouă direcțiile. **Îndeplinită**: `core/test_tenant_stergere.py`, 13 teste.

### R73 — Patru trimiteri de email sunt înghițite tăcut, iar trei dintre ele sunt singura cale de intrare

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · P13 · **PRAG 2** *(nu se poate demonstra că un eșec s-a produs — chiar asta e problema. Efectul e producibil oricând serverul de mail pică, iar atunci ecranul afirmă fals la fiecare cerere)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `9ece318`
- **măsurat la**: 2026-08-26 · **pe commit**: `9ece318`
- **planul**: **ACOPERIT.** `PLAN_ARHITECTURA.md`, secțiunea despre **text care afirmă fals**, dă chiar tiparul: *„«Vector necompletat» pe firme cu vectorul complet. «Patru-ochi e dezactivat» pe o politică doar suspendată.”* La fel: *„ai primit linkul de logare”* pe o trimitere care a eșuat. Planul nu cere o decizie nouă — cere ca afirmația să nu fie falsă. (METODA §25)
- **ce blochează**: `except Exception: pass` în jurul lui `trimite_email_html`, în **patru** locuri: emailul de bun venit la înregistrarea cabinetului (`main.py:1106`), **resetarea de parolă** (1424), **linkul de logare fără parolă** (1473), **invitația de asistent** (5938). Ultimele trei sunt **căi de intrare**: dacă serverul de mail pică, aplicația spune *„ai primit linkul”* la fiecare cerere, iar nimeni nu află — nici clientul, nici cabinetul. Costin: *„aia nu e formulare, e o defecțiune care nu se poate diagnostica.”*
- **MĂSURAT clasa, cum a cerut, înainte de încadrare**: **32** de `except …: pass` în codul de producție (`main.py` + `core/`), din care **5** în jurul unei operațiuni care atinge exteriorul. Citite una câte una: **4 sunt reale** (cele de email de mai sus) și **1 e declarată** — `anaf_api.py:101`, unde docstringul spune de ce (*„NU ridică: nu blochează emiterea facturii pe ANAF-jos”*) și unde eșecul are o **valoare vizibilă** în locul lui: `fallback`. Deci clasa are 4 membri, nu 5 — iar diferența dintre ei e că unul **spune** ce face.
- **ȘI REMEDIUL EXISTĂ DEJA, din 27.07.2026**: `observare.esec_secundar(eticheta, eroare, alerta=False)` — *„un efect secundar a eșuat. Operația principală continuă, dar eroarea NU dispare.” Construit exact pentru clasa asta (*„15 locuri aveau `except: pass` peste un query”*), și folosit azi în **zeci** de locuri, cu comentariul *„înghițit, dar nu tăcut”*. **Cele patru trimiteri de email n-au fost trecute pe el.** Nu e o regulă care lipsește; e o regulă care are instrument și n-a fost aplicată acolo unde costul tăcerii e cel mai mare.
- **ce NU vede măsurătoarea**: dacă vreo trimitere **a eșuat** vreodată. Prin construcție nu se poate ști — nu există urmă. Asta face imposibilă și încadrarea la prag 1: nu pot arăta un om păgubit, pot arăta doar că nimeni n-ar afla dacă ar exista.
- **GARD CONSTRUIT 27.08.2026, pe argumentul lui Costin dat înapoi**: *„o lipsă declarată rămâne lipsă. Iar reparația e o schimbare de apel — o revenire la `except: pass` n-ar pica nimic."* `core/test_esec_trimitere_email.py`, **12 teste**, structural pe AST (METODA §23): nodurile `Try`/`ExceptHandler` din `main.py` + `core/`, nu textul.
  - **REGULA 1**, fără listă de excepții: un `except` care prinde un `trimite_email_html` cheamă `esec_secundar`. Se poate aplica **peste tot** fiindcă a fost măsurată întâi: din **17** apeluri, **4** sunt prinse de un `try` cu `except` — exact cele patru reparate; **12** lasă excepția să urce; **1** stă într-un `try/finally` fără handler. Zero excepții de declarat.
  - **REGULA 2**: cele **trei** căi de acces alertează, bun-venitul **nu**. Ambele direcții, și a doua e la fel de reală: o alertă pe fiecare bun-venit face alertele să nu mai fie citite, ceea ce ascunde tot un om blocat afară.
  - **CALIBRAREA cerută, cu forma subtilă**: `except Exception: log(...)` fără `esec_secundar` **e prinsă** — *„arată ca disciplină și tace la fel"*. La fel `print(...)`. Direcția inversă, ca gardul să nu raporteze tot: forma reparată, un `except:` gol-de-tip dar cu `esec_secundar`, și `try/finally`-ul fără handler din `sinteza_zilnica.py` **nu** sunt raportate.
  - **RED-PROOF pe SURSA REALĂ**, nu doar pe șabloane: `main.py` mutat în memorie (fișierul de pe disc neatins), patru mutații, patru roșii — `pass` înapoi pe linkul de logare · `print(...)` în locul urmei · `alerta=True` pierdută pe resetarea de parolă · subiectul redenumit (anti-vacuu).
  - **ANTI-VACUU**: domeniul e ancorat pe **subiectul emailului** — un argument al apelului protejat, nu un număr de linie. Dacă subiectul se schimbă, gardul **pică** în loc să se uite în gol.
- **ce NU face, declarat**: **niciun clichet pe cele 28 de `except …: pass` rămase.** Costin, explicit: *„pe alea nu le-am măsurat și nu știm care sunt legitime."* Și nu verifică dacă emailul chiar pleacă — doar că, dacă nu pleacă, rămâne urmă.
- **condiția de deblocare**: decizia lui Costin între **(a)** toate patru trec pe `esec_secundar`, cu `alerta=True` pe cele trei căi de intrare — tăcerea acolo are cost de acces, ceea ce docstringul lui numește drept criteriu; **(b)** doar log, fără alertă, pe toate patru; **(c)** mesajul de pe ecran se schimbă și el, ca să nu mai afirme trimiterea. Se închide când un eșec de trimitere lasă urmă, cu gard.

### R75 — Joburile de fundal au deadman; procesul care servește ecranele, nu

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · P13 · **PRAG 3** *(azi nu minte nimic pe ecran — dar o cădere a serviciului web nu lasă nicio urmă pe care s-o vadă cineva, iar a doua oară va arăta tot ca un accident izolat)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `8e02a76`
- **măsurat la**: 2026-08-27 · **pe commit**: `8e02a76`
- **planul**: **NEACOPERIT.** `PLAN_ARHITECTURA.md` cere ca ecranul și serverul să nu spună lucruri diferite (P13), dar nu spune nimic despre **disponibilitatea** procesului care le servește. `core/cron.py` scrie principiul — *„un job care nu pornește deloc arată exact ca unul care n-a avut ce face"* — și îl aplică **numai joburilor de fundal**. (METODA §25)
- **ce blochează**: *(primul punct — Costin: „aia e o lipsă, nu o observație")* — **deadman-ul nu acoperă serviciul web.** `cron.RITMURI` supraveghează 11 joburi — 8 din `crontab`, 3 din timere systemd (R74). `iconta-nou.service`, procesul care servește **toate** ecranele, nu e supravegheat de nimic: nici de `verifica_batai` (n-are cum să bată), nici de o sondă externă. `Restart=always` îl ridică înapoi, dar **nu spune nimănui că a căzut.**
- **instanța, și e de azi**: procesul s-a oprit la **06:45:01** și a revenit în trei secunde. În `uvicorn.log` scrie **„Shutting down"** — oprire curată, pe semnal, nu crash. În `journalctl` **nu există niciun `sudo systemctl` la ora aia** (singurul de azi e post-commit-ul de la 05:37). Efectul măsurabil: scanul vizual care rula chiar atunci a raportat `ERR_CONNECTION_REFUSED` pe jumătate din ecrane — **singurul motiv pentru care am aflat.** Dacă n-ar fi rulat nimic, căderea ar fi trecut fără urmă.
- **ce NU vede măsurătoarea**: **cauza opririi.** `journalctl -u iconta-nou` n-are intrări (unitatea scrie în fișier), iar `dmesg` nu e accesibil din contul care rulează aplicația. Nu se poate spune dacă a fost OOM, un semnal extern, sau altceva. *Restanța nu se deschide ca să fie investigată acum — se deschide ca să existe unde se adune, dacă se mai întâmplă.*
- **de ce e o clasă, nu o instanță**: e a treia oară în două zile când forma e aceeași — **ceva funcționează sau nu, și nimeni nu întreabă**. La R70 o rută pe care n-o cheamă nimic; la R74 un job care nu pornește; aici procesul care servește tot. Gărzile verifică ce face lucrul **dacă** rulează.
- **condiția de deblocare**: decizia lui Costin între **(a)** o sondă **externă** (ping de la un serviciu terț care alertează la lipsa semnalului) — singura care acoperă și cazul „serverul e jos", limită deja scrisă în `cron.verifica_batai`; **(b)** o supraveghere **locală** (`OnFailure=` pe unitate + un job care compară `ActiveEnterTimestamp` cu ultima valoare știută) — mai ieftină, dar oarbă exact când contează; **(c)** se declară acceptat că o cădere scurtă trece nevăzută, cu motivul scris. Se închide când o oprire a serviciului web lasă o urmă pe care o vede cineva fără să fi rulat din întâmplare altceva.


### R74 — Trei joburi de fundal sunt oprite de o lună, iar deadman-ul nu se uită la ele

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · P13 · **PRAG 3** *(azi nu minte nimic pe ecran: `spv_token` are 0 rânduri, deci nicio firmă n-are SPV conectat. Devine prag 1 în ziua în care prima firmă îl conectează — atunci facturile furnizorilor nu mai intră, iar nimeni nu află)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `8e02a76`
- **deschisă pe commit**: `3fb126e`
- **măsurat la**: 2026-08-27 · **pe commit**: `3fb126e`
- **planul**: **ACOPERIT ca principiu.** `PLAN_ARHITECTURA.md` cere, la **P13**, ca ecranul și serverul să nu spună lucruri diferite; iar `core/cron.py` scrie deja principiul în antet: *„un job care nu pornește deloc arată exact ca unul care n-a avut ce face"*. Ce lipsește nu e regula, e **acoperirea** ei: deadman-ul a fost construit pentru joburile din `crontab`, iar astea nu sunt acolo. (METODA §25)
- **ce blochează**: `spv-poll`, `spv-receive` și `spv-refresh` (timere systemd, la 30 min / 30 min / zilnic) rulează `ExecStart=/opt/iconta/venv/bin/python3`. **Calea nu mai există** — `/opt/` are doar `duk/`. Toate trei ies cu **status 203** (exec eșuat) la fiecare declanșare. Ultima linie din `spv_receive.log` și `spv_poll.log` e din **2026-07-27 12:17**; `/opt` a fost modificat în aceeași zi la 15:29. Deci: **~31 de zile × ~48 de porniri pe zi, toate eșuate, în tăcere.**
- **de ce n-a văzut-o nimic**: `cron.RITMURI` — lista deadman-ului — are **8 joburi, toate din `crontab`**. Cele trei timere systemd **nu sunt în ea**, deci lipsa bătăii lor nu e o lipsă pentru nimeni. Iar gardul care păzește lista, `test_fiecare_job_din_crontab_are_prag`, compară `RITMURI` cu un set **scris de mână în test** — nu citește nici `crontab`, nici `/etc/systemd/system/*.timer`. **E un gard care se compară cu propria copie a răspunsului**: forma din [[gard-care-nu-se-verifica-pe-sine]], a doua instanță în trei zile.
- **aceeași clasă cu R70, un nivel mai jos**: acolo, *o rută scrisă, gardată și verde, pe care n-o cheamă nimic*. Aici, *un job scris, programat și verde în `systemctl list-timers`, care nu pornește*. În amândouă, gărzile verifică ce face lucrul **dacă** rulează; niciuna nu întreabă **dacă** rulează.
- **ce NU vede măsurătoarea**: dacă vreo factură de furnizor s-a pierdut. Nu se poate ști din aplicație — SPV nu ține evidența a ce n-am cerut. Ce se poate spune: în ultimele rulări reușite (27.07), toate cele trei firme cu CIF răspundeau *„Nu aveti drept in SPV pentru CIF=…"*, deci nici atunci nu venea nimic. Absența e explicabilă — dar explicația vine din log, nu din vreo gardă.
- **DECIS 27.08.2026: varianta (a).** Costin corectează unitățile (cere `sudo`); eu am făcut jumătatea mea, în același commit:
  - cele trei joburi intră în `cron.RITMURI` (praguri 2 / 2 / 50 ore) **și** trec prin `cron.ruleaza` — până azi săreau peste ambalaj, deci **nici când rulau nu spuneau nimănui că au rulat**;
  - `core/test_joburi_supravegheate.py` citește lista **din sistem** (`crontab -l` + `/etc/systemd/system/*.timer` → serviciul lor → `ExecStart`), nu dintr-o copie. Am rescris și testul vechi din `test_heartbeat.py`, care compara `RITMURI` cu un set bătut în test;
  - **și verifică dacă interpretorul fiecărei unități există pe disc** — asta ar fi prins defectul în ziua 1. Cele trei stricate stau într-un baseline cu clichet în **ambele** direcții: când se repară, testul devine ROȘU și cere scoaterea lor;
  - `NESUPRAVEGHEATE` declară ce **nu** intră, cu motivul: `cron` (heartbeat-ul însuși — cere deadman EXTERN) și `iconta-backup` (shell, nu modul; își alertează singur eșecurile).
  - **de la commitul `3391371`, heartbeat-ul alertează la fiecare 6 ore** că cele trei n-au bătut niciodată. E corect — chiar n-au. Se oprește când unitățile sunt reparate.
- **REZOLVATĂ 27.08.2026 — Costin a rulat comanda, cu toate patru verificările:**
  1. `ExecStart` pe toate trei arată acum `/home/costin/iconta_nou/venv/bin/python`;
  2. `Result=success`, `ExecMainStatus=0` la toate trei — erau **203** de ~31 de zile;
  3. logurile au linii de azi, iar la final *„job OK: spv_poll (0.0s)"* și *„job OK: spv_receive (0.1s)"* — deci trec **și** prin `cron.ruleaza`, adică alertează la eșec și **bat** la reușită. În `spv_receive`: *„SKIP auth: nu are token SPV activ"*, 19 tenanți — normal, niciun cabinet n-a conectat SPV;
  4. `cron.verifica_batai()` întoarce `[]` — **deadman-ul nu mai are ce reclama.** Înainte întorcea exact cele trei.
- **ȘI CLICHETUL S-A APRINS ÎN A DOUA DIRECȚIE, la prima reparație.** `test_baseline_de_unitati_stricate_NU_pastreaza_morti` a devenit ROȘU cu chiar mesajul scris pentru cazul ăsta: *„unități din `_INTERPRETOARE_LIPSA` care NU mai sunt stricate: […] — scoate-le din baseline."* Costin: *„clichetul a funcționat în ambele direcții — a doua, cea care nu păstrează morți, s-a aprins la prima reparație."* Baseline-ul e acum **gol, nu șters**: o mulțime goală spune *„azi nicio unitate nu e stricată"*, ceea ce e o afirmație; absența listei n-ar spune nimic.
- **ce NU s-a rezolvat, și a devenit R75**: joburile de fundal au acum deadman; **procesul care servește ecranele, nu.**
- **condiția de deblocare**: *(cea de atunci, ÎNDEPLINITĂ)* decizia lui Costin între **(a)** cele trei unități se corectează pe `venv`-ul real **și** cele trei joburi intră în `cron.RITMURI` cu pragul lor, iar gardul citește lista din sistem în loc s-o copieze; **(b)** joburile SPV se mută în `crontab`, unde deadman-ul ajunge deja; **(c)** se opresc deliberat până există o firmă cu SPV conectat, **declarat** — o oprire declarată nu e o oprire tăcută. Corectarea unităților cere `sudo`, deci mâna lui. Se închide când un job de fundal care nu pornește nu mai poate trece o lună neobservat.


### R40 — Nicio declarație depusă prin aplicație, deci lanțul de apărare nu e exercitat niciodată

- **felul**: VERIFICARE
- **cine deblochează**: EXTERN
- **unde intră**: E1 · interdicția 32 · interdicția 19 · **PRAG 3** *(nimic fals pe ecran azi; ce lipsește e proba, nu corectitudinea)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `bf16f32`
- **ce blochează**: toate cele **54** de depuneri înregistrate vin din **importul istoric**, care nu captează valorile. Calea care le persistă (`coada_api.py:300`) e scrisă și gardată, dar **n-a fost folosită niciodată** — coada are 3 elemente, toate în `la_senior`. Deci lanțul *poziție depusă → cont → note → document* n-a fost parcurs nici măcar o dată pe date reale, iar sonda care-l parcurge întoarce **zero** dintr-un motiv care nu se poate deosebi mecanic de „totul e în regulă".
- **ce s-a făcut totuși, ca absența să nu treacă drept sănătate**: **toate cele trei** verificări care compară o declarație preferă acum ce s-a **depus**, și, când regenerează, **își declară limita** — în temei și în `limita` afișată. Erau **1 din 3** (doar `verifica_d390`). La `verifica_tva`, cheia depunerii **nu e luna curentă**, ci **ultima lună a ferestrei TVA**: coada scrie eticheta decontului (3/6/9/12 pentru trimestriali), deci o căutare pe `luna` ar fi ratat **sistematic și tăcut** exact firmele trimestriale, căzând liniștit înapoi pe regenerare cu un temei care pretinde că s-a căutat. Gardat structural în `core/test_compara_ce_s_a_depus.py`, cu RED-proof pe chiar mutația aia.
- **condiția de deblocare**: **trebuie** o **primă depunere reală prin coadă** — aprobare de senior + depunere efectivă — **de la** Costin sau de la un contabil care folosește aplicația, **pentru ca** sonda de lanț să aibă ce parcurge. Fără ea, lanțul *poziție depusă → cont → note → document* **blochează** măsurarea interdicției 32 la nivelul ei, iar sonda întoarce zero dintr-un motiv care nu se poate deosebi mecanic de „totul e în regulă" (interdicția 19). O firmă de test e suficientă. Până atunci, orice afirmație despre „lanțul funcționează" e despre cod, nu despre date.

### R39 — Coloana pe care se sprijină verificarea D112 nu se scrie de nicăieri

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · interdicția 32 · interdicția 10 · **PRAG 3** *(azi mesajul nimerește adevărul; devine fals în ziua în care R33 se leagă)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `0a96ebf`
- **ce blochează**: `inregistrari.document_ref` e scrisă de **0 din 48** de căi de INSERT, dar citită de `note_salarii_ciorna()`, care de aceea întoarce **0 prin construcție**. Ramura „note în ciornă, așteaptă validare" din `compara_d112` e **cod mort**. Ca să încete să fie, cineva trebuie să **scrie** coloana la crearea notei statului de plată — iar calea aia nu există încă (`salarii_contare` nelegat, R33), și **cine o creează** e chiar întrebarea din **R36**.
- **ce s-a făcut totuși, ca minciuna să nu aștepte deblocarea**: `note_salarii_ciorna` întoarce de azi **`None` = necunoscut** când coloana e goală pe toată schema, iar `compara_d112` nu mai **afirmă cauza** pe un necunoscut — spune ce vede și numește **amândouă** acțiunile posibile. Gardat de `core/test_document_ref_necunoscut.py`.
- **condiția de deblocare**: se răspunde la **R36** (cine și când contabilizează), fiindcă abia atunci se știe **cine scrie** `document_ref` pe nota statului de plată. Când calea aia se leagă, filtrul redevine o măsurătoare și ramura „ciornă" redevine vie — **în aceeași tură**, nu după.

### R38 — Lista de cote din ecranul de NIR e scrisă de mână, fiindcă serverul n-o poate da

- **felul**: ORDINE
- **cine deblochează**: DECIZIE
- **unde intră**: E3 · interdicția 1 · **PRAG 3** *(azi ambele valori sunt corecte — e o listă care VA îmbătrâni, nu una greșită)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `2636004`
- **ce blochează**: partea din **R29** care nu era o valoare implicită, ci o **decizie de formă**. Selectorul de cotă din ecranul de NIR (`firme.js`) își construiește opțiunile din literalul `[21, 11]`. **Nu e o cifră greșită** — 21% standard și 11% redusă sunt corecte azi (Legea 141/2025) — dar lista trebuie ținută la zi cu mâna. Iar serverul **nu o poate da**: `cote_valide()` din `core/cote_tva.py` **a fost ștearsă pe 20.08.2026**, cu motivul scris acolo — *„lista [21, 11, 0] FĂRĂ dată, cu ZERO consumatori"*. Deci nu e un apel lipsă: e o capabilitate care a fost scoasă deliberat fiindcă nu purta data, și care ar trebui reconstruită **period-aware** ca să fie de folos.
- **ce s-a făcut totuși, ca lista să nu îmbătrânească tăcut**: valorile ei intră de azi în `core/test_valori_fiscale_js.py` (tabelul confruntat cu registrul, 10 → 12 situri). Dacă o cotă se schimbă în `COTE`, testul devine roșu **și numește ecranul**. Forma rămâne scrisă de mână; **corectitudinea ei nu mai depinde de memoria nimănui**.
- **condiția de deblocare**: se scrie **care** dintre două, și **de ce** — *(a)* se reconstruiește o sursă de cote **pe dată** (`cote_valide(la_data)`), iar ecranul o cere de la server; *(b)* lista rămâne în ecran, iar gardul de mai sus e considerat suficient, cu motivul scris. Se închide când decizia e în `DECIZII.md` cu varianta respinsă numită.

### R31 — Anul e scris în cerere, deci ecranul nu poate ajunge la anul curent

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · interdicția 1 · **PRAG 2** *(cifră corectă, dar a anului trecut)*
- **reluări**: 0
- **stare**: REZOLVATĂ
- **rezolvată pe commit**: `f846370`
- **deschisă pe commit**: `fa3330c`
- **cum s-a închis**: condiția era *„`CLICHET` din `core/test_an_hardcodat.py` coboară la 0"* — și a coborât. `rip_ecran.js` cere acum `/rip/d212/${an}`, cu anul din starea ecranului, iar eticheta citește `${d.an}` și `${bani(d.salariu_minim)}` din payload: **ecranul nu mai știe nici anul, nici reperul.** Partea de server era condiția reală: `rip_api.fisa_d212` refuza orice an ≠ 2025 și folosea constanta `PLAFOANE_VENIT_2025`, deci **fișa nu putea fi produsă decât pe anul trecut, pentru orice PFA** — iar `PLAFOANE_VENIT_2026`, verificat la sursă pe 03.08.2026, nu era chemat de nimeni (clasa **R33**, la nivel de funcție). Acum plafoanele se derivă cu `plafoane_an(an)`, iar refuzul rămâne legat de **dovadă**: `d212_engine.ANI_VERIFICATI = (2025, 2026)`, cu 2027 refuzat în continuare — **nu s-a lărgit dincolo de ce e verificat la sursă.** Gardat de `core/test_d212_an_verificat.py` (9 teste), RED-probat pe 6 mutații; una a arătat o gaură a gardului: cerea doar ca un an *neverificat* să fie refuzat, nu și ca unul *verificat* să treacă, deci o revenire la `an != 2025` ar fi rămas verde. Direcția inversă a fost adăugată.
- **ce NU s-a închis, și e o corectură a premisei**: `4.050` **nu era o valoare expirată**, deși arăta ca una. Reperul D212 e salariul minim la **1 ianuarie al anului de venit**, fix pe an — majorarea la 4.325 (HG 146/2026, de la 1 iulie) **nu-l atinge**, iar pentru venituri 2026 reperul e tot 4.050. Pinat în `core/test_d212_an_verificat.py`, ca un gard viitor să nu „corecteze" o valoare corectă. Defectul era **anul înghețat**, nu cifra.
- **ce blochează**: *(istoric — rezolvat; se păstrează fiindcă o restanță fără „ce blochează" nu poate fi scrisă)* `rip_ecran.js:142` cerea `/rip/d212/**2025**` — anul scris literal în URL. Butonul *«Fișa D212»* aduce, în august 2026, fișa de calcul pe **2025**: CAS, CASS, impozit, total datorat. Eticheta spune cinstit *«venituri 2025 (sm 4.050 lei)»*, iar **4.050 e valoarea corectă pentru 2025** — deci nu e o cifră falsă. E altceva: **ecranul nu poate ajunge la anul curent, niciodată**, iar valoarea din etichetă va rămâne corectă pentru un an care se îndepărtează. Ecranul are deja variabila `an` în stare (o folosește la importul din casă), deci reparația URL-ului e mecanică; partea de etichetă cere ca serverul să întoarcă anul și salariul minim al lui, nu ecranul să le știe.
- **condiția de deblocare**: `CLICHET` din `core/test_an_hardcodat.py` coboară la **0** — momentul în care nicio cerere din `static/js/` nu mai poartă un an literal. Gardul are deja aserțiunea care **pică dacă clichetul rămâne peste realitate**, deci nu poate fi uitat deschis.

### R32 — Date de test al căror antet își contrazice propriile linii

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · **PRAG 3** *(nicio cifră greșită la un om — dar orice confruntare antet↔linii minte pe ele)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `f9e0f29`
- **ce blochează**: din cele **41** de facturi din bază, **3** au TVA-ul de pe antet în dezacord cu suma calculată din propriile linii: `tenant_004 COER-T5` și `tenant_009 COER-T5` (antet **2.000**, din linii **0** — linia are `cota_tva = 0`) și `tenant_007 COER-T6` (antet **0**, din linii **8.400** — linia are `cota_tva = 21`). Toate trei sunt din `date_test/seed/transa2_coerenta_tva.py`, seria `COER`, scrise **direct în tabele**: antetul cu o valoare fixată de scenariu, liniile cu alta. **Nu e un defect al aplicației** — nicio factură emisă prin ecran nu diverge. E un defect al **datelor pe care se măsoară**.
- **de ce contează totuși**: e aceeași clasă cu campania **#2** (CUI/CNP de test care nu treceau cifra de control) — *un instrument calibrat pe date invalide raportează despre o lume care nu există*. Aici efectul e ascuțit: orice gard viitor care confruntă **antetul cu liniile** — exact felul de verificare încrucișată pe care se sprijină D394 și D300 — ar găsi trei „defecte" care sunt de fapt fixturi, sau ar fi calibrat să le tolereze și ar deveni orb pe cazul real.
- **condiția de deblocare**: seeder-ul scrie antetul **din linii**, nu pe lângă ele — sau, dacă divergența e intenționată pentru un scenariu anume, o declară explicit (o coloană, un marcaj) ca să poată fi deosebită de una reală. Se închide când recalcularea din linii coincide pe toate cele 41, **sau** când cele 3 sunt marcate ca divergente-cu-intenție și un test le numără.

### R33 — Module de verificare care n-au fost NICIODATĂ legate

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E3 · P7 · **PRAG 2** *(nu produce o cifră greșită — produce o verificare care nu se întâmplă)*
- **notă de dependență**: legarea e INTERNĂ (un apel lipsă), dar **unde** se leagă `echilibru_perioada` cere o **decizie**. **CORECTAT 25.08.2026:** propoziția de aici spunea *„azi există două implementări ale echilibrului, iar cea legată e `verificatoare.verifica_balanta`"* — falsificată de măsurătoarea de mai jos: cele două au moduri de eșec **disjuncte**, deci nu sunt două implementări ale aceleiași verificări. Nota nu se gardează — nu decide nimic singură (`PLAN_LUCRU`, „CINE deblochează").
- **reluări**: 1
- **stare**: DESCHISĂ
- **planul**: NEACOPERIT. Căutat în PLAN_ARHITECTURA la **P11** (*«unde textul nu determină rezultatul, nu se alege — se cere decizia»* — confirmă că se cere, nu spune care), la **interdicția 47** (*un blocaj fără cale de trecere pentru om* — constrânge CUM poate arăta un blocaj, nu DACĂ se blochează) și la **P6 aplicat la date** (Partea 0: *un rezultat calculat peste date incomplete nu e gata, e gata-cu-ce-am-avut* — cel mai aproape de răspuns, dar vorbește despre VERDICT, nu despre unde apare verificarea pe ecran). Planul nu așază verificări pe ecrane. (METODA §25)
- **deschisă pe commit**: `88bc33b`
- **măsurat la**: 2026-08-24 · **pe commit**: `88bc33b`
- **ce blochează**: **4 module de producție din `core/` au funcții publice, teste care trec, și ZERO importatori în afara testelor.** Clasa, formulată de Costin: *„nu s-a stricat, n-a fost niciodată legat."* Ce o face invizibilă: **testele le țin verzi**, deci nimic nu semnalează. Un modul mort care pică ar fi fost găsit demult; unul mort care trece nu se deosebește de unul viu.

  | modul | publice | ce e |
  |---|---|---|
  | `core/echilibru_perioada.py` | 3 | **verificare** — `echilibru_perioada(linii)`, `orfani(...)`, `echilibru_perioada_db(...)` |
  | `core/salarii_contare.py` | 3 | **verificare** — `control_coerenta(note, ...)`, notă contabilă vs declarație |
  | `core/compensare.py` | 5 | `pull(conn, schema)`, `propune_compensari(...)`, `necesita_sistem_electronic(...)` |
  | `core/fisa_cont.py` | 3 | `fisa_cont(...)`, `conturi_cu_miscare(...)` |

- **CELE DOUĂ FAPTE CARE TAIE, amândouă găsite pentru că măsurătoarea e pe AST, nu pe text.** *(1)* `core/salarizare.py:296` **numește** `salarii_contare.control_coerenta` — *„incrucisat nota-vs-declaratie"* — dar e un **COMENTARIU**. Proza descrie o legătură care nu există, iar un `grep` ar fi raportat modulul ca legat. Aceeași clasă cu **R16** (proza care descrie codul poate fi falsă de la naștere). *(2)* `main.py:4389` chiar calculează „echilibru", dar prin `verificatoare.verifica_balanta` — deci `echilibru_perioada` nu e doar cod nelegat, e **a doua implementare a aceleiași verificări**, cea care n-a fost aleasă. Asta o mută lângă P7 și lângă interdicția „reparație reală, fără logică paralelă".
- **URCAT LA PRAG 1 (Costin, 24.08.2026, autorizat dinainte): `salarii_contare.control_coerenta`.** Criteriul dat: *„dacă mai e vreunul care verifică o ieșire care ajunge la ANAF, urcă la prag 1."* Verificat la sursă, și e îndeplinit: funcția cheamă `d112.genereaza`, scoate totalurile din **XML-ul real** (`control_incrucisat.totaluri_d112_din_xml`) și le confruntă cu rulajul creditor al notei propuse, cont cu cont, pe `COD_CONT_D112`, cu toleranța `toleranta_d112(nr_salariati)`. Întoarce divergențele numind **ambele valori**. **D112 se depune la ANAF** — deci asta e o verificare a unei ieșiri depuse, scrisă, testată, și pe care **nu o cheamă nimeni**. Restul celor trei rămân prag 2: `echilibru_perioada` și `fisa_cont` privesc evidența internă, `compensare` produce note și un test de obligație (`necesita_sistem_electronic`), niciuna nu confruntă un artefact depus.
- **DECIZIA, 25.08.2026 (Costin) — jumătatea de PRAG 1, `salarii_contare.control_coerenta`.** *„La propunerea notei, și SEMNALEAZĂ, nu blochează. LOCUL: la propunere — e singurul moment în care omul poate face ceva cu informația; la închiderea lunii e prea târziu, iar pe suprafața de control fiscal e o constatare despre trecut. COMPORTAMENTUL: semnalează, cu cifra divergenței și cu ce diferă. Motivul: aplicația compară o propunere cu o declarație generată din alte date. Când cele două diferă, nu se știe care greșește — poate declarația e veche, poate nota e corectă. Un blocaj ar presupune că declarația are dreptate. Iar 10 din 40 diverg: un blocaj pe un sfert din cazuri, fără să știm cine greșește, oprește munca și nu spune nimic."*

- **CE S-A GĂSIT LEGÂND-O, și e mai mare decât spunea restanța.** Modulul era nelegat **în întregime**, nu doar verificarea: `note_lunare` — contabilizarea statului de plată — n-avea niciun apelant. **Salariile nu deveneau niciodată notă contabilă în aplicație.** Restanța număra funcții publice fără importatori; ce nu spunea e că lipsea chiar **actul**, nu doar verificarea lui.

- **ȘI A DOUA INSTANȚĂ DE R16 ÎN ACELAȘI FIȘIER.** Docstringul modulului promitea: *„nota se scrie DOAR dacă totalul ei coincide cu XML-ul D112… Dacă nu coincide, refuzăm să scriem și spunem de ce."* **Nimic nu scria și nimic nu refuza.** Prima instanță era comentariul din `salarizare.py:296` care numește `control_coerenta`; a doua e chiar promisiunea de garanție a modulului. Amândouă treceau verzi, fiindcă testele cheamă funcțiile direct. Docstringul e rescris pe ce face codul — și pe decizia de acum, care spune explicit că **nu** refuză.

- **APLICAT — actul, semnalul, și forma semnalului.**
  - `POST /tenants/{}/salarii-contare/propunere` — nota pe care ar scrie-o statul de plată **plus** divergențele. Nu scrie nimic (probat structural: niciun INSERT/UPDATE/DELETE, niciun commit).
  - `POST /tenants/{}/salarii-contare` — scrie nota **ciornă** (patru-ochi rămâne), cu verificarea de lună închisă de la R42(a), idempotentă pe `document_ref`.
  - **Divergențele sunt OBIECTE, nu proză**: `{eticheta, cont, nota, declaratie, diferenta, toleranta}`. Forma veche întorcea fraze — iar cifrele nu se pot compune înapoi dintr-o frază. Textul îl compune ecranul (DS cap.13).
  - **Divergența nu se stinge prin ignorare**: se recalculează la fiecare deschidere și se întoarce **și** pe ramura «există deja», deci rămâne vizibilă după contare.

- **PROBAT PE PROCESUL VIU** (nu doar pe AST — METODA §24), desktop și Pixel 5, după restart: butonul există, propunerea răspunde, tabelul de divergențe are coloane pentru **notă** și pentru **D112**, iar butonul *Scrie nota ciornă* rămâne **apăsabil**. Pe `ALFA MICRO` semnalul a găsit o divergență reală: **impozit pe venit — nota ar scrie 161,12 în 444, D112 declară 204,00, diferență 42,88.** Prima probă a dat zero fiindcă înlocuia intrări în `sys.modules`, iar `from core import d112` citește atributul de pe pachet: măsura funcția reală pe o bază inexistentă.

- **GARDA**: `core/test_coerenta_salarii.py` — 10 teste, **6 mutații** probate (divergența redevine proză · scrierea blochează · nota intră validată · luna închisă nu mai e verificată · propunerea scrie · propunerea nu mai întoarce semnalul), fișierele restaurate identic.

- **CE RĂMÂNE DESCHIS, cu cifra: 3 din 4 module.** `compensare` și `fisa_cont` sunt prag 2 și INTERNE (le lipsește un apelant). `echilibru_perioada` rămâne **decizie**: e a doua implementare a unei verificări care există deja legată (`verificatoare.verifica_balanta`, `main.py:4389`) — deci nu e „cod nelegat", e **logică paralelă**, iar care dintre cele două rămâne e o alegere, nu o cablare.

- **NU e redundantă cu reconcilierea existentă, verificat:** `control_incrucisat._thunk_d112` compară **sursa** cu declarația (`d112_reconciliere.reconciliaza`); `control_coerenta` compară **nota contabilă propusă** cu declarația. Perechi diferite, întrebări diferite — a doua nu se poate deduce din prima.
- **CE LIPSEȘTE ca prag 1 să se poată executa, și de ce nu s-a legat în tura asta:** *unde* apare verificarea e o decizie de produs, nu o corectură — la propunerea notei, la închiderea lunii, sau pe suprafața de control fiscal; iar pe divergență, blochează contarea sau doar o semnalează? Amândouă schimbă ce înseamnă ecranul, deci intră sub „reorganizare de ecran = STOP" și sub P11. Ce nu mai e în discuție e prioritatea: e prag 1, nu prag 2. **RĂSPUNS 25.08.2026** — vezi „DECIZIA, 25.08.2026” mai jos: la propunere, semnalează, nu blochează. *(Marcajul „Decizie cerută” a rămas aici o zi după ce decizia fusese luată și scrisă la două paragrafe distanță; l-a prins garda antetului, nu eu.)*
- **CUM S-A MĂSURAT, și ce NU vede.** `core/scan_module_nelegate.py` (instrument nou), pe AST: **839** de fișiere `.py`, **361** de module ne-test cu funcții publice. Modurile de eșec sunt scrise în antetul instrumentului **înaintea** primei măsurători (interdicția 76): **E1** import dinamic prin șir — raportat separat, nu înghițit (singurul din `main.py` e `__import__("time")`); **E2** puncte de intrare cu `__main__` — 77, excluse, dar **sub-detectate**: un script fără gardă `__main__` cade greșit în listă, iar instanța e chiar `core/scan_valori_afisate.py`, ținută în clichet ca **fals pozitiv declarat**; **E3** module încărcate de altceva decât un import Python — `main.py`, pe care uvicorn îl încarcă; **E4** **NEACOPERIT** — un modul *importat* ale cărui funcții publice nu se cheamă niciodată; sonda e la nivel de **modul**, nu de funcție; **E5** module fără suprafață publică.
- **CALIBRARE NEGATIVĂ, în gardă, nu doar în proză.** `control_incrucisat`, `common`, `d300`, `control_fiscal_api`, `verificatoare` — toate au importatori de producție și niciunul nu apare în listă. `control_incrucisat` e acolo **deliberat**: pe 24.08 a fost presupus nelegat, iar măsurătoarea a arătat **6 importatori de producție** (`main.py:4358`, `control_fiscal_api` ×3, `d301.py:370`, `salarii_contare.py:74`, `alerte_control_fiscal.py:52`) și data nașterii **15.07.2026**, nu „acum patru zile".
- **gardat**: `core/test_module_nelegate.py` — clichet ancorat pe **NUME**, nu pe număr (o înlocuire cap-la-cap ar fi trecut printr-un contor), bidirecțional: pică și când intră unul nou, și când unul se leagă și rămâne în pin. Fiecare intrare poartă **motivul** scris. RED-probat pe trei mutații, dintre care una pe **instrument**: sonda pusă să numere proza ca apel → gardul devine roșu.
- **condiția de deblocare**: fiecare dintre cele **patru** primește ori un apelant în producție, ori o declarație scrisă de ce rămâne nelegat. Se închide când `PIN` din `core/test_module_nelegate.py` nu mai conține niciun modul marcat `PRODUCTIE, nelegat`. **26.08.2026: mai e UNUL — `compensare`.** **REFORMULATĂ 25.08.2026**, fiindcă măsurătoarea de mai sus a scos partea care spunea *„care dintre cele două implementări ale echilibrului rămâne, fiindcă a le păstra pe amândouă e chiar logica paralelă"* — cele două au moduri de eșec disjuncte, deci nu sunt două implementări, iar a alege una **șterge** o verificare. Ce rămâne de decis nu mai e *care iese*, ci **unde se leagă `echilibru_perioada` și ce se face cu jumătatea tautologică din `verifica_balanta`** — decizie de produs (schimbă ce vede contabilul pe `GET /firme/{tenant_id}/verificari`), deci §2.3 pct.2.
- **CONSECINȚA PRACTICĂ, cerută de Costin 24.08.2026:** *„la orice schimbare de valoare fiscală, JS-ul se caută explicit, ca al treilea loc după registru și cod."* Regula **exista deja** — `METODA_VERIFICARE.md` **§18**, scrisă pe 24.08 — deci nu se dublează aici; ce se adaugă e **ordinea celor trei locuri**, scrisă acolo. Motivul e măsurat: din 10 situri de cotă literală în `static/js/`, **4 nu erau confruntate cu registrul** până la inventarul din aceeași zi, iar niciuna dintre campaniile de până atunci nu le atinsese — *nimeni nu le căuta acolo*.
- **INSTANȚĂ NOUĂ, la nivel de FUNCȚIE, reparată 24.08.2026:** `d212_engine.PLAFOANE_VENIT_2026` — verificat la sursă pe 03.08.2026 (Legea 239/2025 art. XII pct. 19, CASS 72 sm) — **nu era chemat de nimeni**, fiindcă `rip_api.fisa_d212` refuza orice an ≠ 2025. Modulul era legat; **capabilitatea nu.** E chiar modul de eșec **E4** al sondei, declarat înainte de măsurătoare și găsit apoi **de mână**, nu de instrument. Vezi R31 (închisă) și `METODA` §19.
- **REMĂSURAT 24.08.2026 pe `eddc2c0`, cu domeniul lărgit cerut explicit — REZULTAT IDENTIC: 5** (4 module de producție + `scan_valori_afisate.py`, fals pozitiv declarat). Cifra nu s-a mișcat fiindcă **domeniul era deja cel cerut**: sonda n-a filtrat niciodată pe „verificare", ci pe *orice modul ne-test cu funcții publice și zero importatori de producție*. Lărgirea cerută era deja în vigoare de la prima măsurătoare. **Ce ar schimba cifra e coborârea la nivel de FUNCȚIE (E4), nu lărgirea pe module** — și aia rămâne neconstruită.
- **Verificat odată cu remăsurarea, pe criteriul „atinge o ieșire care se depune"**: dintre cele patru, doar `salarii_contare` îl îndeplinește (D112) — **deja urcat la prag 1**. `echilibru_perioada` și `fisa_cont` privesc evidența internă și registrele obligatorii (care se prezintă la control, nu se depun); `compensare` produce note și un test de obligație. **Nicio escaladare nouă.**
- **REÎNCADRAREA CLASEI (Costin, 24.08.2026), consemnată ca diferență de domeniu:** numele restanței spune *„module de verificare"*, dar sonda n-a fost niciodată îngustată la verificare — `core/scan_module_nelegate.py` măsoară **orice** modul ne-test cu funcții publice și zero importatori de producție. Din cele 4 găsite, doar 2 sunt verificare; `compensare` produce note, `fisa_cont` produce un artefact. Deci clasa reală e mai largă și se numește mai bine **„module scrise pentru fluxuri care nu s-au construit"** — iar `METODA` §20 e chiar despre asta. **Ce limitează domeniul nu e cuvântul „verificare", ci modul de eșec E4** (nivelul funcție), care rămâne neacoperit. *Remăsurarea cu domeniul lărgit nu cere un instrument nou — cere ca sonda să coboare la funcție. Consemnat, nefăcut.*
- **MĂSURAT 25.08.2026 pe `d312bf8` — premisa „logică paralelă" e FALSIFICATĂ: nu sunt două implementări ale aceleiași verificări.** Cerut de Costin: *„înainte de a o lega: rulează amândouă pe aceleași date și spune-mi dacă dau același rezultat. Dacă diferă, aia e o măsurătoare, nu o alegere."* S-a rulat, în două feluri.

  **(a) Pe date reale — acord total, dar pe ZERO instanțe.** Toate cele 17 firme, toate perioadele cu linii de evidență: **7 firme · 12 perioade · 50 de linii** (din care **42** pe note `validata`). Amândouă spun OK peste tot. Acordul nu dovedește nimic, fiindcă nu există niciun rând pe care vreuna să poată pica: **0 linii cu o parte lipsă · 0 orfani · 0 solduri inițiale dezechilibrate**. Asta e chiar **interdicția 19** — un verdict favorabil pe zero rânduri nu e un rezultat. Sonda a fost read-only, probat: 51 de tabele numărate înainte și după, zero diferențe.

  **(b) Pe modurile de eșec ale fiecăreia** (METODA §22, interdicția 76 — un instrument se calibrează pe felul în care POATE greși). Același set de linii, dat amândurora:

  | cazul dat amândurora | `echilibru_perioada` | `verificatoare.verifica_balanta` |
  |---|---|---|
  | partidă dublă corectă (control pozitiv) | OK | OK |
  | linie cu `cont_debit` NULL | **PRINDE** — Sd 1000 ≠ Sc 1500 | **CRAPĂ** — `TypeError` în `balanta()`, la `sorted()` peste `None` |
  | linie cu `cont_credit` NULL | **PRINDE** | **CRAPĂ**, la fel |
  | linie cu cont **șir gol** `''` | **PRINDE** — Sd 1000 ≠ Sc 1500 | **RATEAZĂ TĂCUT** — `ok=True` |
  | `inregistrare_id` inexistent (orfan) | **PRINDE** — `orfani()`, 1 linie | **RATEAZĂ** — n-are conceptul |
  | solduri inițiale dezechilibrate (SI 5000 fără contrapartidă) | **RATEAZĂ** — nu citește `solduri_initiale` | **PRINDE** — `BALANTA_SI_DEZECHILIBRATA` |

  **Concluzia, și e o măsurătoare, nu o preferință: modurile de eșec sunt DISJUNCTE.** Fiecare prinde exact ce cealaltă ratează. Niciuna nu „face mai mult"; nu există o alegere care să nu **șteargă o verificare fără înlocuitor**. Premisa restanței — *„a doua implementare a aceleiași verificări"* — a fost scrisă din numele funcțiilor, nu din ce fac ele.

  **De ce sunt diferite prin construcție**, nu din întâmplare: domenii diferite (`echilibru_perioada_db` = **o lună**, doar note `validata`; lanțul din `main` = **cumulativ** de la începutul evidenței, **toate** statusurile, plus soldurile inițiale) și obiecte diferite (linii brute de ledger vs. obiect balanță deja agregat).

  **A treia constatare, care taie mai adânc: jumătatea `BALANTA_INEGALA` a lui `verifica_balanta` e TAUTOLOGICĂ pe intrarea pe care i-o dă `main.py`.** `balanta()` adaugă **aceeași** sumă pe `rulaj_d[debit]` și pe `rulaj_c[credit]`, deci totalul debitor și cel creditor sunt egale prin construcție. Probat pe **2000** de seturi aleatoare (inclusiv cu conturi NULL și goale): **0** cazuri în care ar putea diferi. Ce rămâne operant din funcție e **doar** a doua jumătate, cea pe soldurile inițiale. Aceeași clasă cu **R18** (porți verzi care nu pot deveni roșii).

  **CÂT E DE ATINGIBIL, măsurat — ca să nu se umfle.** `cont_debit` și `cont_credit` sunt **NOT NULL** pe toate cele **26** de scheme, deci cele două rânduri cu `TypeError` **nu se pot atinge prin bază**. Ce **se poate** atinge e rândul cu **șir gol**: nu există **niciun CHECK** pe tabelă, iar azi sunt **0** astfel de linii — deci e o gaură deschisă, nu un defect viu.

  **Corectură de referință:** blocurile de mai sus scriu `main.py:4389`; azi apelul e la **`main.py:4634`**, iar balanța se construiește la **`main.py:4597`**, în `_verificari_contabile`, servit de `GET /firme/{tenant_id}/verificari`.

  **Și nu sunt două, sunt trei — plus una nechemată.** `core/audit_preluare.py:142` are o **a treia** funcție numită tot `verifica_balanta(conn, schema)`, LIVE (chemată din `audit_preluare.py:387`), dar pe **alt obiect**: balanța de **deschidere** (`solduri_initiale`), prin `solduri_api.verifica_echilibru`. Iar `verificatoare.echilibru_nota` — echilibrul unei **note** — n-are niciun apelant în afara testelor, deci e o instanță de R33 la nivel de **funcție**, adică chiar modul de eșec **E4** declarat ca neacoperit.

  **CE NU VEDE MĂSURĂTOAREA ASTA:** rulează pe **50 de linii de evidență** în toată instalarea, toate de test — deci partea (a) e un plafon inferior din construcție, nu o acoperire; partea (b) e pe cazuri **sintetice**, deci spune ce prinde fiecare funcție, nu cât de des apare cazul în viață; și nu s-a măsurat dacă vreun scriitor din cod **poate** produce un cont șir-gol — s-a măsurat doar că baza îl permite. Numitorul acelei măsurători e cunoscut și e mare: **52 de situri de scriere** în `inregistrari_linii` în producție (41 în `main.py`, 11 în `core/`), fiecare de citit separat. **Nu e o limită, e muncă neîncepută** — se numește aici cu cifra ei ca să nu se piardă.

- **APLICAT 26.08.2026 — varianta b′′, decisă de Costin.** *„E singura care nu lasă în urmă o ramură verde prin construcție. O ramură care nu poate pica e mai rea decât o verificare absentă: absența se vede, tautologia raportează."*

  | ce s-a făcut | unde |
  |---|---|
  | `echilibru_perioada` e **legat** — un apel real, nu un import | `main.py` `_verificari_contabile` |
  | `BALANTA_INEGALA` **scos**, cu motivul scris pe locul ramurii | `core/verificatoare.py`, `core/common.py` (codul e scos și din registrul de coduri) |
  | cele două se compun într-**un singur** verdict `echilibru`, **la construcție** | `echilibru_perioada.verdict_echilibru` (pură) |
  | contabilul vede **un rând**, cu ce a găsit fiecare | `static/js/ecrane/firme.js`, `randEchilibru` |
  | gardă pe **non-tautologie** | `core/test_echilibru_legat.py`, 14 teste, **5 mutații** probate |

  **Ce s-a găsit legând-o, și nu era în decizie: orbirea la contul format din SPAȚII.** `echilibru_perioada` testa `if l.get("cont_debit")`, iar `"   "` e adevărat în Python — deci un cont alb numara drept prezent și dezechilibrul devenea invizibil. Nu e ipotetic: măsurat pe AST, **19 situri** scriau contul cu tiparul `str(corp.get("cont_x") or "<implicit>")`, **fără `strip()`**. Probat pe schemă efemeră: `NOT NULL` nu-l oprește, un `CHECK (cont <> '')` **nu l-ar fi oprit**, și niciuna din cele două verificări nu-l vedea. Reparat la sursă (R54), și verificarea îl vede acum.

  **`neverificat` nu se rotunjește la „în regulă".** Dacă motorul de ledger crapă, verdictul compus **nu** poate fi verde — P6, cablat în `verdict_echilibru` și probat prin mutație.

- **CE RĂMÂNE din cele patru module: UNUL.** `salarii_contare` (prag 1, legat 25.08) și `echilibru_perioada` (azi) sunt închise. `fisa_cont` are **declarație scrisă** de ce rămâne nelegat (PRODUCĂTOR FĂRĂ LIVRARE, METODA §20), ceea ce satisface condiția. Rămâne **`compensare`** — singurul încă fără apelant și fără declarație.

- **INSTANȚĂ NOUĂ la nivel de FUNCȚIE (E4), găsită în treacăt:** `verificatoare.echilibru_nota` — echilibrul unei note — n-are niciun apelant în afara testelor. Modulul e legat; **funcția nu**. Consemnată, nereparată.

- **ce NU închide**: nivelul FUNCȚIE (E4). Un modul importat pentru o funcție, cu alte trei moarte, trece neatins. Aia e o măsurătoare separată, mai scumpă, și n-a fost făcută.

### R34 — Nota contabilă de salarii contrazice D112-ul depus, pe 10 din 40 de perechi

- **felul**: VERIFICARE
- **cine deblochează**: DECIZIE
- **unde intră**: E5 · P7 · interdicțiile 11–12 · **PRAG 1** *(o cifră care ar intra în evidență contrazice una depusă la ANAF)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `6097d5a`
- **măsurat la**: 2026-08-24 · **pe commit**: `6097d5a`
- **ce blochează**: Întrebarea lui Costin — *„când le legi, ce găsesc pe datele existente? Dacă una raportează diferențe pe o firmă de test, aia nu e o gardă nouă care merge — e un defect care aștepta să fie văzut."* **Rulat, fără să leg nimic: 40 de perechi (firmă × lună) verificate, 29 de divergențe pe 10 perechi.** Nota pe care ar scrie-o aplicația diferă de D112-ul pe care îl declară, pe pozițiile 444 (impozit), 4315 (CAS), 4316 (CASS), 436 (CAM). Cea mai mare: `tenant_001` 2026-06 — CAS **24.114,54** în notă vs **28.539** declarat (**4.424,46** lei), CASS **9.645,81** vs **13.629** (**3.983,19**), impozit **5.719,89** vs **9.027** (**3.307,11**). Nu e o gardă care merge: e o divergență care exista și pe care nimic nu o putea arăta.
- **de ce e PRAG 1 pe citirea de atingibilitate**: toate cele 17 firme sunt **de test** (măsurat 23.08), deci nimeni n-a fost lovit. Dar pragul se citește ca **atingibilitate** (lămurirea din 23.08): *dacă un contabil ar folosi aplicația azi*, ar contabiliza salariile cu alte cifre decât cele pe care le-a depus. Aceeași formă cu cele trei instanțe din primul triaj.
- **ce NU spune măsurătoarea, și e partea grea**: **care dintre cele două are dreptate.** `d112.pull` calculează salariatul, iar `salarii_contare.note_lunare` îl **recalculează** prin `salarizare.calcul_salariu` — deși comentariul lui spune *„NU recalculăm: al doilea calcul ar fi a doua cifră"*. Deci sunt două căi care produc aceeași cifră și nu coincid: **P7**, iar P7 spune că întrebarea se duce la arbitru, **nu se aliniază una la cealaltă**. Nu se repară până nu e scris care e sursa.
- **efect azi: NICIUNUL, și de asta n-a fost văzut.** `salarii_contare` nu e chemat de nimeni (R33), deci nota nu se scrie niciodată din calea asta. Divergența devine vizibilă exact în clipa în care modulul se leagă — adică reparația cerută la R33 **produce 29 de constatări roșii în prima rulare**. Ordinea corectă e: mai întâi se decide care cale are dreptate, apoi se leagă.
- **două lucruri găsite pe drum, de sondă**: `tenant_003` are pontajul neconfirmat pe **10 luni**, iar D112 e blocat corect cu mesaj explicit (garda funcționează); `tenant_016` are un salariat cu brut **1.000** lei sub salariul minim 4.050 pe normă întreagă, respins de calea a doua ca *„date corupte, nu caz fiscal legitim"* — aceeași clasă cu **R32** (date de test invalide).
- **sonda NU a scris**: instantaneu `pg_stat_user_tables` înainte/după, zero inserări/actualizări/ștergeri pe toate tabelele. *(A treia formă a sondei; primele două au raportat „0 divergențe" pe **0 rulări** — rezultat favorabil pe vid, interdicția 19, produs de mine în chiar instrumentul cu care măsuram clasa asta.)*
- **condiția de deblocare**: se scrie **care cale e sursa** pentru contribuțiile din nota de salarii — `d112.pull` sau `salarizare.calcul_salariu` — cu motivul; apoi cealaltă o citește, nu o recalculează. Se închide când sonda de mai sus întoarce **0 divergențe pe cele 40 de perechi**, iar `control_coerenta` e legat.

### R35 — Verdict VERDE pe o lună cu factură necontabilizată, cunoscută în chiar payload-ul verdictului

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · P6 · interdicțiile **10** și **19** · **PRAG 1** *(un verdict favorabil pe ecran, peste un necunoscut pe care verdictul îl are în mână)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `8a10080`
- **măsurat la**: 2026-08-24 · **pe commit**: `8a10080`
- **ce blochează**: Întrebarea lui Costin — *„verde pe date reale sau verde pe zero? Interdicția 19 e chiar asta."* **Măsurat pe 9 perechi firmă × lună, cu `control_incrucisat.verifica_tva` chemat pe datele reale: 6 sunt roșii corect, iar 3 sunt VERZI deși payload-ul lor poartă `facturi_necontabilizate = 1`.** `tenant_004` 2026-06, `tenant_017` 2026-11 și `tenant_017` 2026-09 afișează *„TVA colectată: D300 și contul 4427 coincid"* — pe o lună în care **există o factură care nu e în evidență**. Cele două cifre coincid fiindcă sunt **amândouă zero**: verdele nu vine dintr-o potrivire, ci din absența ambilor termeni.
- **de ce e PRAG 1, nu igienă de gardă**: nu e „o verificare raportează greșit". E o **afirmație falsă pe ecran**: contabilul citește *„TVA-ul lunii coincide"* pe o lună în care o factură emisă stă în afara conturilor. **P6**: absența unei contradicții nu e o verificare, iar *necunoscutul domină favorabilul*. Verdictul are necunoscutul **în mână** — `facturi_necontabilizate` e în același payload — și îl ignoră la culoare. Asta e chiar **interdicția 10** (verdict favorabil care coexistă cu necunoscut nedeclarat), suprapusă peste **19** (favorabil pe zero rânduri).
- **contextul măsurat, care arată că nu e un caz izolat**: din **43** de facturi declarabile pe 17 scheme (stările declarabile din `nomenclator_status_factura`: `de_preluat`, `emisa`, `importata`), **28 nu sunt contate deloc** — **65%** — purtând **102.260,00 lei** TVA, pe **10 firme din 17**. Nu e o firmă cu date incomplete: e majoritatea. Două firme (`tenant_013`, `tenant_014`) au zero necontate, deci nici tiparul invers nu e universal.
- **și de ce nu e o restanță despre `de_preluat`**: decizia din 22.08.2026 (`nomenclator_status_factura`) e **întreagă pe partea ei** — D300 și `d300_reconciliere` citesc amândouă nomenclatorul, `de_preluat` e declarabilă, iar `_STATUS_FINAL` vine din sursa unică. Ce nu există e o legătură în **cealaltă** direcție: contarea unei facturi e o rută **manuală, per document** (`main.py`, `INSERT INTO inregistrari ... 'ciorna'`), care **nu consultă nomenclatorul** și nu e declanșată de nimic. Deci nu e „o tranziție care nu se mai întâmplă" — **nu există nicio tranziție**: contarea e un act al omului, iar declararea nu-l așteaptă.
- **ce e corect și trebuie spus**: garda **funcționează** pe majoritatea cazurilor — 6 din 9 luni sunt roșii, cu **ambele valori numite** (*„D300 declară 3.150,00 lei, contul 4427 are 0,00 lei"*). Defectul e strict la **culoarea verdictului când ambii termeni sunt zero**, nu la mecanism.
- **condiția de deblocare**: un verdict nu poate fi **verde** cât timp `facturi_necontabilizate > 0` pe perioada lui — devine **gri** (necunoaștere, cu domeniul ei) sau roșu, după caz. Se închide când sonda de mai sus întoarce **zero perechi verzi cu necontabilizate nenule**, iar gardul care o probează are în domeniu toate cele 17 scheme.
- **sonda NU a scris**: instantaneu `pg_stat_user_tables` înainte/după, zero inserări/actualizări/ștergeri.

### R36 — Cum ajung faptele economice în contabilitate nu e o alegere DECLARATĂ nicăieri

- **felul**: ARTEFACT
- **cine deblochează**: DECIZIE
- **unde intră**: E1 · E3 · **P11** · interdicția **21** · **PRAG 2** *(nu o cifră greșită — o alegere de arhitectură luată prin scriere de cod, fără să fi fost cerută)*
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `37c5fa6`
- **măsurat la**: 2026-08-24 · **pe commit**: `37c5fa6`
- **ce blochează**: Întrebarea lui Costin, și e cea care mută tot restul: *„aplicația a fost proiectată să contabilizeze automat facturile, sau să primească notele din altă parte?"* **Căutat în `DECIZII.md`, `PLAN_ARHITECTURA.md`, `DESIGN_SYSTEM.md` și `CONFORMITATE.md`: nicio decizie, niciun principiu, nicio regulă de produs care să spună care dintre cele două e modelul.** Alegerea nu e luată — e **nimerită**, prin ce s-a scris. Exact P11: *„unde textul nu determină rezultatul, nu se alege — se cere decizia"*, iar aici nici măcar nu era vorba de un text de lege, ci de forma produsului.
- **CE EXISTĂ, măsurat pe toate cele 17 scheme** — 41 de facturi, **34 de note**:

  | sursa notei | note | ce înseamnă |
  |---|---|---|
  | `(null)` | **19** | fără sursă declarată — fixturi scrise direct în tabele |
  | `banca` | 6 | din reconcilierea extrasului |
  | `casa` | 5 | din registrul de casă |
  | **`facturi`** | **3** | **singura cale document → notă, pe toată instalarea** |
  | `amortizare` | 1 | |

  Și: **15** note poartă `factura_id`, **19** nu poartă niciunul.

- **Deci răspunsul e „nici una, nici alta, complet".** Există o cale document→notă, dar e o **rută manuală, per factură**, apăsată de om, care a produs **3 note** în toată instalarea. Nu există niciun mecanism care să contabilizeze un lot, nicio declanșare la emitere, nicio coadă. Iar restul evidenței vine din alte trei căi (bancă, casă, amortizare) plus 19 note fără nicio proveniență. **Nu e „lipsește un modul întreg" și nu e „notele vin din altă parte": e că nu s-a hotărât care din două, iar codul le are pe amândouă pe jumătate.**
- **De ce contează mai mult decât pare**: `P14` cere ca orice cifră să se desfacă până la documentul care o justifică. O notă fără `factura_id` și fără `sursa` **nu se poate desface** — și sunt 19 din 34, adică **56%** din evidența existentă. Iar `P20` cere proveniență pe orice valoare din afară. Ambele sunt încălcate nu de un defect, ci de **absența alegerii**.
- **LIMITĂ DECLARATĂ, și e importantă pentru verdictele fazei 1**: baza pe care s-a măsurat orice despre evidența contabilă e **41 de facturi și 34 de note, pe 17 firme, toate de test**. E o bază **subțire**, iar un verdict de fază 1 dat pe ea poartă incertitudinea asta. Nu se poate spune „aplicația produce evidența corect" pe 34 de note — se poate spune doar ce s-a văzut. *Consemnat ca limită, nu ca cifră: procentele derivate din baza asta se citesc ca plafoane, nu ca proporții.*
- **MĂSURAT 24.08.2026 pe `29b04a3` — ambele jumătăți ale fluxului EXISTĂ, iar asta schimbă întrebarea.** *(a)* **Propunerea automată există**: `POST /tenants/{id}/facturi/{id}/contabilizeaza` (`main.py:6745`), al cărei docstring **declară chiar modelul** — *„Notă ciornă din factură (**AI propune, contabilul validează**). Idempotent: refuză dacă există deja înregistrare."* Nu primește niciun corp: **omul nu vede nimic înainte.** Generează singură notele prin `core/facturi.factura_emisa` / `factura_primita`, grupate pe `(cont_venit, cotă)`, cu `tva_la_incasare` respectat, și le scrie ca **ciornă**. Confirmarea e **în aval** — validarea ciornei — nu o aprobare înainte. *(b)* **Maparea document→conturi există, și e amplă**: pe lângă `core/facturi.py`, sunt ~50 de rute în `main.py` și 8 module în `core/` care produc note, fiecare cu `sursa` proprie: `bon`, `amef`, `horeca_z`, `amortizare`, `casa`, `banca`, `retete`, `stocuri`, `reconciliere`. **Nu e nimic de construit.** *(c)* **Fluxul manual există și el, complet**: `POST /tenants/{id}/jurnal` → `core/jurnal_api.py`, cu validare linie cu linie (debit, credit, sumă > 0), scriind `sursa='manual'`, `status='ciorna'`.
- **ȘI ATUNCI CE LIPSEȘTE: FOLOSIREA.** Pe toate cele 17 scheme, notele au sursele `(null)`=19, `banca`=6, `casa`=5, `facturi`=3, `amortizare`=1. **`manual` apare de ZERO ori.** Iar cele 19 fără sursă nu pot veni din nicio rută — toate scriu o `sursa` explicită — deci sunt **scrise de seedere** (`date_test/seed/firma_grea_audit.py`, `transa3_d300_b1.py`, care inserează direct în `inregistrari`). **Concluzia: fluxul automat a fost exercitat de 3 ori, cel manual de 0 ori, iar 56% din evidență e fixtură.** Nu e „o funcționalitate lipsă" și nu e „un modul întreg": e un flux construit pe amândouă căile și nefolosit pe niciuna.
- **Ce INFIRMĂ măsurătoarea asta**: ipoteza că *„jumătatea de sus a fluxului nu s-a construit niciodată"* — s-a construit, de două ori (automat și manual). Și ipoteza că *„familia A măsoară registre al căror conținut nu are cum să existe"* — conținutul **are cum** să existe; pur și simplu nu a fost produs pe datele de test. Marcajul corect al fazei 1 rămâne cel din antetul E1: **bază subțire, cifre citite ca plafon** — nu „conținut imposibil".

- **CRITERIU DE ACCEPTARE al propunerii automate (Costin, 24.08.2026)** — de aplicat când se decide declanșarea, nu după: *„propunerea automată trebuie să fie cel puțin la nivelul celui care o folosește; altfel adaugă muncă de verificare, nu economisește."* E același test ca P22 și Anexa D — *un contabil care nu poate avea încredere într-o cifră ori o crede orbește, ori o reface în altă parte, și amândouă sunt eșecuri ale produsului* — dar mutat pe **propunere**: o notă propusă pe care contabilul o verifică oricum cont cu cont nu i-a economisit nimic, i-a adăugat un pas.
- **Observația care l-a produs, și e măsurată**: notele existente au conturi **corecte** — cele 8 conturi literale din ecrane sunt toate în planul tuturor celor 17 firme, iar cele 34 de note reale n-au produs nicio constatare de cont inexistent. Cine a ținut evidența știa planul de conturi. **Deci ștacheta propunerii automate nu e „să nimerească ceva plauzibil", e „să nu fie sub omul care o citește".** Consecință practică pentru decizia de declanșare: dacă propunerea se face la **emitere**, ea trebuie să fie corectă fără context uman; dacă se face la **validare** sau la **închidere**, poate cere context, fiindcă omul e deja acolo. *Momentul și ștacheta nu sunt independente.*
- **condiția de deblocare**: se scrie, ca **decizie de produs** în `DECIZII.md`, care e modelul — *(a)* aplicația contabilizează documentele automat, și atunci ruta manuală devine excepția declarată; *(b)* contabilul introduce notele, și atunci contarea automată nu se construiește, iar D300 nu mai poate declara ce evidența n-are fără să semnaleze; *(c)* hibrid, cu granița scrisă. Se închide când alegerea, varianta respinsă și motivul sunt scrise, iar `R35` și `R34` se re-citesc pe ea — amândouă atârnă de răspuns.
- **ce NU e**: nu e o reformulare a lui R35. R35 e un **verdict fals pe ecran** (verde peste o factură necontabilizată cunoscută), prag 1, măsurat pe 9 perechi — rămâne cum e. R36 e cauza din spatele lui, și e o **absență**, nu un defect: de aceea prag 2, nu 1.

### R37 — Nota contabilă n-are autor, iar `sursa` ei e un nomenclator de fapt, scris în 48 de locuri

- **felul**: VERIFICARE
- **cine deblochează**: INTERN
- **unde intră**: E3 · P16 · P13 · interdicțiile **17**, **28**, **37** · **PRAG 2**
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `6091024`
- **măsurat la**: 2026-08-24 · **pe commit**: `6091024`
- **ce blochează**: **(1) Nicio înregistrare contabilă nu poartă autor.** `core/jurnal_api.py` și `core/casa_api.py` scriu în `inregistrari` fără `creat_de`, `user_id` sau `autor` — verificat, câmpurile nu există. Consecința măsurabilă: **nu se poate deosebi o notă introdusă de un om prin ecran de una scrisă de un script care cheamă ruta.** Întrebarea a fost pusă explicit (Costin, 24.08) și **nu are răspuns din date, prin construcție**. Iar nota alimentează D300 și D112, care se depun — deci e **interdicția 37**: act cu efect juridic extern, fără autor identificat. Prin contrast, `state_plata` **are** autor (`emis_de`, `motiv_de`), deci tiparul corect există deja în casă.
- **(2) `sursa` e un nomenclator care nu există ca registru**: șir liber, scris **literal în 48 de locuri**, cu **9 valori distincte** — `facturi` (28×), `banca` (6), `stocuri` (5), `casa` (4), plus câte una pentru `manual`, `horeca_z`, `bon`, `amortizare`, `amef`. Nicio listă închisă, nicio validare, niciun loc unic. **Interdicțiile 17 și 28.** O valoare scrisă greșit într-o rută nouă nu e prinsă de nimic, iar orice raport care grupează pe `sursa` ar tăcea despre ea.
- **ce NU e**: nu e un nomenclator de TIPURI DE NOTĂ. Așa ceva **nu există** — `NOTE_TIP` a fost căutat, zero potriviri. Iar absența lui **nu blochează** propunerea automată: maparea document→conturi există deja **per tip de operațiune**, în ~50 de rute, fiecare știindu-și conturile. Nu e nevoie de un strat tip-factură → tip-notă. *Vezi R36: singurul gol e declanșarea.*
- **și un rezultat NEGATIV, care merită scris fiindcă infirmă o predicție**: conturile scrise literal în ecrane au fost confruntate cu planul de conturi al fiecărei firme — **8 conturi** (`2131`, `2133`, `2813`, `301`, `371`, `401`, `4111`, `446`), **toate prezente în planul tuturor celor 17 firme. Zero greșite.** Deci **nu** e a cincea instanță de valoare expirată în ecran. *Calibrare, ca numărătoarea să nu fie reluată greșit:* o căutare fără filtru de context ar fi dat și `121`/`103` din `declaratii.js` — care sunt **coduri de obligație ANAF**, nu conturi — și `101` din `etransport_ecran.js`, care e cod de tip de document. Trei fals-pozitive din unsprezece.
- **condiția de deblocare**: `sursa` devine nomenclator închis, într-un loc unic, cu validare la scriere (după modelul `nomenclator_status_factura`); și `inregistrari` primește autor, pe regulile lui `state_plata`. Se închide când un scan pe `INSERT INTO ... inregistrari` găsește **zero** literale de `sursa` în afara nomenclatorului, iar coloana de autor e nenulă pe orice notă nouă.

## E1 — SETUL COMPLET (faza 1 din PLAN_INVESTIGATII.md)

Faza 1 e singura care răspunde la afirmația „aplicația face contabilitate conformă". Ce urmează nu
sunt interdicții, sunt măsurătorile fazei — dar poartă aceleași câmpuri, fiindcă o cifră fără dată și
fără commit îmbătrânește la fel de tăcut aici ca oriunde.

- **măsurat la**: 2026-08-22
- **pe commit**: `84f77c4` (HEAD la momentul măsurării)

> **⚠ BAZA DE EVIDENȚĂ, marcată 24.08.2026 — orice măsurătoare de aici despre evidența contabilă se
> citește ca PLAFON, nu ca proporție.** Măsurat pe `b17efea`, pe toate cele 17 scheme: **41 de facturi
> și 34 de note**, din care **3** produse pe calea document→notă (`sursa='facturi'`), **19** fără nicio
> proveniență și fără `factura_id`. Cu o bază atât de subțire, un verdict de fază 1 despre evidență nu
> spune *„aplicația produce evidența corect"*, ci doar *ce s-a văzut pe 34 de note*. **Nu e o cifră
> invalidată — e o cifră al cărei numitor e declarat**, iar deosebirea contează: nu se corectează, se
> **remăsoară** după ce modelul de intrare a faptelor e decis (**R36**) și aplicat. Până atunci,
> secțiunile de mai jos care ating evidența contabilă **nu se citează ca verdict**. Cauza, cu vorbele
> **PRECIZARE 24.08.2026 (Costin), și schimbă ce înseamnă marcajul:** motivul nu e că *nu se produce
> contabilitate* — se produce, pe ~50 de căi (**R36**). E că **notele se introduc printr-un act uman,
> iar firmele de test n-au avut cine să-l facă**: fluxul automat a fost apăsat de 3 ori, cel manual de
> 0 ori. **Consecința, și e cea care contează: artefactele familiei A pot fi perfect corecte pe o firmă
> cu evidență ținută — asta nu s-a măsurat niciodată.** Marcajul nu spune *artefactele sunt greșite*,
> spune *n-au fost văzute pe date reale*. Remăsurarea cere **o firmă cu evidență ținută, nu un
> instrument nou.**
> lui Costin: *„întrebarea corectă era dacă notele acoperă documentele"* — iar `METODA` §16 spune de ce
> se ratează: verificarea se face unde e nevoie, nu unde e vizibilă.

### Operațiunea 1 — câte regimuri acoperă aplicația (MĂSURATĂ)

**Nu trei.** Regimul nu e un câmp: e un PRODUS de nouă dimensiuni din vectorul fiscal, plus cinci
regimuri speciale de TVA care nu se văd deloc în vector — ele se manifestă prin note contabile.

| dimensiune | ce cunoaște codul | ce oferă interfața | firme, din 17 |
|---|---|---|---|
| `tip_firma` | `srl`, `pfa` (CHECK în `01_ddl_tip_firma.sql`) | — nu se alege din UI | **srl 17 · pfa 0** |
| `regim_fiscal` | `micro`, `profit` | ambele | micro 10 · profit 7 |
| `platitor_tva` | da / nu | ambele | da 11 · nu 6 |
| `tip_decont` | L/T/S/A prin `common.perioada_tva_tip` | **doar lunar și trimestrial** | lunar 9 · trimestrial 7 · gol 1 · **semestrial 0 · anual 0** |
| `operatiuni_ic` | da / nu | ambele | da 5 · nu 12 |
| `inreg_art317` | da / nu | ambele | **da 1** (t006) · nu 16 |
| `tva_la_incasare` | da / nu | ambele | **da 0** · nu 17 |
| `pro_rata` | numeric sau NULL | câmp liber | **completat 0** · NULL 17 |
| `baza_contabila` | `A` plus celelalte, mapate în `d406.plan_oficial` | — | **A pe toate 17** |

**Combinațiile purtate efectiv de firme: 9.**

| # | tip · regim · TVA · periodicitate · IC · art. 317 | firme |
|---|---|---|
| 1 | srl · micro · TVA · lunar | t015 |
| 2 | srl · micro · TVA · lunar · IC | t013, t016, t017 |
| 3 | srl · micro · TVA · trimestrial | t003, t012 |
| 4 | srl · micro · fără TVA · trimestrial | t002, t009, t011 |
| 5 | srl · micro · fără TVA · trimestrial · IC · art. 317 | t006 |
| 6 | srl · profit · TVA · lunar | t001, t007, t008, t010 |
| 7 | srl · profit · TVA · lunar · IC | t004 |
| 8 | srl · profit · TVA · trimestrial | t005 |
| 9 | srl · profit · fără TVA · fără periodicitate | t014 |

**Regimurile speciale de TVA: modul, rută, ecran — și zero firme exercitate.**

| regim | motor | rută | firma „purtătoare" | exercitat pe date? |
|---|---|---|---|---|
| marjă second-hand, art. 312 | `core/tva_marja.py` | `POST /tenants/{id}/vanzare-marja` | t008 „Second Hand Marja SRL" | **NU** — t008 n-are niciun rând pe nicio tabelă purtătoare |
| marjă agenții de turism, art. 311 | `core/tva_marja_turism.py` | `.../vanzare-marja-turism` | t007 „Agentie Turism Marja SRL" | **NU** — o factură, zero note de marjă |
| aur de investiții, art. 313 | `core/tva_aur.py` | `.../vanzare-aur-investitii` | **niciuna** | **NU** |
| agricultori (compensare 8%), art. 315^1 | `core/tva_agricultori.py` | `.../achizitie-agricultor`, `.../vanzare-agricultor` | t009 „Ferma Agricultor Forfetar SRL" | **NU** — o factură în regim normal (TVA 2000) |
| TVA la încasare, art. 282 | `core/tva_incasare.py` | `.../nota-tva-incasare` + `d300` | **niciuna** (`tva_la_incasare=false` pe toate 17) | latura **furnizor**: DA, pe t004 (`furnizor_tva_incasare`, deducere amânată); latura proprie: **NU** |

Toate cinci au ecran: `static/js/ecrane/operatiuni_ecran.js`, categoria „TVA regimuri speciale".

**Cum s-a măsurat, și ce nu vede măsurătoarea.** Regimurile speciale n-au marcaj în `firma_profil`;
rutele lor scriu note în `inregistrari` / `inregistrari_linii` — verificat la sursă în `main.py`, ruta
`vanzare-marja` (`INSERT INTO {schema}.inregistrari ... 'ciorna'`). Deci sonda a citit **toate cele 34
de note contabile existente pe cei 17 tenanți**, nu un eșantion, și le-a confruntat cu unsprezece
tipare („marj", „art. 312", „art. 311", „aur", „agricultor", „turism", „compensare", …):
**zero potriviri**. **Ce nu vede:** un regim exercitat prin import, nu prin rută · o notă a cărei
descriere a fost rescrisă de om. Iar „zero note" nu spune că motorul e greșit — spune că **nimeni n-a
produs artefactul cu el**.

**Taxare inversă internă (art. 331): exercitată.** 2 facturi din 41, pe t005 (construcții) și t007;
coloanele `facturi.taxare_inversa` și `facturi.categorie_331` sunt populate. Pe t013 există o factură
cu `categorie_331` completată și `taxare_inversa = false` — de privit la 1b.

**Ce s-a verificat și NU e defect** (ca să nu se redeschidă): `tip_decont` e stocat în două convenții,
`L`/`T` (seed vechi) și `lunar`/`trimestrial`. Nu e o divergență vie — parsarea trece printr-un singur
punct, `common.perioada_tva_tip`, iar `tip_decont_lung` normalizează la granița UI. Citit în cod, nu
presupus.

**Semnalele care ies din operațiunea 1** — nu sunt încă defecte, sunt întrebări pentru 1b:

1. **PFA / partidă simplă: 0 firme din 17**, deși `tip_firma` acceptă `pfa` și există `core/d212.py` +
   `core/d212_engine.py`. Regimul cu cele mai multe artefacte proprii nu e exercitat de nicio firmă.
2. **Periodicitatea semestrială și anuală**: motorul le cunoaște, interfața oferă două. Un regim pe
   care codul îl poate calcula și omul nu-l poate alege.
3. **Trei firme fără nicio dată**: t008 (second-hand), t011, t012. Două poartă chiar regimul din numele
   lor. `MODEL_AUDIT_TENANT.md` numește t011 și t012 „SUB-EXERCITATE"; **t008 nu e în acea listă**, și e
   goală — o declarație de perimetru care nu acoperă tot ce e gol (atinge interdicția 20).
4. **`pro_rata` și `tva_la_incasare`: zero firme.** Două regimuri cu efect direct în D300.
5. **`baza_contabila` = A pe toate 17.** Celelalte planuri de conturi, mapate în `d406`, nu sunt atinse.

### Pasul 1a — ce cere legea (temei ADUS, citat verbatim, cu vigoarea verificată)

**Din lege, cu temei.** Fiecare rând a fost găsit prin căutare în `anaf_surse/`, iar numărul
articolului a fost citit mergând înapoi la titlul lui — nu presupus. **Vigoarea a fost verificată la
sursa externă** (Portalul Legislativ, Ministerul Justiției), pe FORMA CONSOLIDATĂ LA ZI, cu
`scripts/vigoare_articol.py`.

**Ce a scos la iveală aducerea actelor** — două lucruri pe care corpusul le ascundea:

1. **Legea 82/1991 nu era în corpus.** Erau doar două documente „modificări aduse de OUG 115/2023 /
   OUG 138/2024", emise de o direcție regională ANAF — nivel 2. **Decizia lui Costin: se aduce actul.**
   *„Un ordin care spune «potrivit prevederilor legii contabilității» nu e temeiul, e o trimitere la el.
   A cita art. 20 prin OMFP 2634/2015 e exact interdicția 53: citatul nu conține regula, o referă."*
   Adusă: `anaf_surse/legea_82_1991_consolidat.{html,txt}`, amprentă
   `4490a223cfe5982232331763d9984f90449e3c75074861005d20bd238ddab152`, forma consolidată la 04.02.2025.
2. **OMFP 2634/2015 era în corpus DOAR cu Anexa nr. 1.** De aceea „registrul de casă" nu se găsea:
   nomenclatorul din copia veche sare de la 14-4-4 la 14-4-13. Aduse acum toate trei anexele, din MO
   910 și 910 bis / 9.12.2015, forma consolidată la 01.08.2024. **Un act incomplet în corpus nu se
   deosebește de un act care nu spune ce cauți** — e o formă de orbire prin construcție care nu era în
   tabelul din METODA.

**A. Registre de contabilitate obligatorii**

| artefact | temei, citat verbatim | vigoare, verificată la sursă | firme |
|---|---|---|---|
| **Registrul-jurnal · Registrul-inventar · Cartea mare** | **Legea 82/1991 art. 20**: „Registrele de contabilitate obligatorii sunt: Registrul-jurnal, Registrul-inventar și Cartea mare. Întocmirea, editarea și păstrarea registrelor de contabilitate se efectuează conform normelor elaborate de Ministerul Finanțelor Publice." | ÎN VIGOARE, fără marcaj de modificare | 17 |
| formele și codurile (14-1-1, 14-1-2, 14-1-3) | OMFP 2634/2015, **Anexa nr. 1** pct. 44–47 | act consolidat 01.08.2024 | 17 |
| **Balanța de verificare, LUNAR** | **Legea 82/1991 art. 22**: „Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare." | ÎN VIGOARE; **modificat la 05-12-2024** (înainte: „cel puțin la încheierea exercițiului financiar") | 17 |
| **Registrul-jurnal de încasări și plăți** (14-1-1/b) + **Registrul-inventar** (14-1-2/b) | OMFP 2634/2015 Anexa nr. 1 pct. 48, care trimite la OMFP 170/2015 | act consolidat 01.08.2024 | **0** (niciun PFA) |

**B. Situații financiare anuale**

| ce | temei, citat verbatim | vigoare |
|---|---|---|
| obligația de a le întocmi | **Legea 82/1991 art. 28** alin. (1): „Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să întocmească situații financiare anuale." | ÎN VIGOARE; alin. (1) modificat 01-01-2015, alin. (1^1) 26-02-2021 |
| **termenele de depunere** | **Legea 82/1991 art. 36** alin. (1): societățile reglementate de Legea 31/1990 ș.a. — **până la 31 mai** inclusiv a exercițiului financiar următor; **celelalte persoane juridice — până la 30 aprilie** | ÎN VIGOARE; alin. (1) **modificat 05-12-2024** |
| componența, pe categorii de mărime | Reglementările contabile (anexa OMFP 1802/2014) pct. 20 alin. (1) — micro · pct. 20 alin. (2) — mici: bilanț prescurtat, cont de profit și pierdere, note · pct. 21 — mijlocii/mari și interes public: plus situația modificărilor capitalului propriu și situația fluxurilor de trezorerie | citite pe **forma consolidată la zi** (adusă 22.08.2026, consolidare 19.11.2025); vigoarea PE PUNCT rămâne restanța **R2** |
| **criteriile de mărime — CORECTATE 22.08.2026** | Reglementările contabile pct. 9: **micro** — total active **2.250.000 lei**, cifră de afaceri netă **4.500.000 lei**, număr mediu de salariați **10**; **mici** — **25.000.000 lei**, **50.000.000 lei**, **50** de salariați; **mijlocii și mari** — cele care DEPĂȘESC cel puțin două dintre aceleași trei. Două criterii din trei, la data bilanțului | **modificate de ORDIN 4.164/2024, în vigoare 23-08-2024**, citite pe forma consolidată |

**O cifră falsă a intrat în registru dimineață, și a ieșit după-amiaza.** Scrisesem criteriile în EUR
— 350.000 / 700.000 / 4.000.000 / 8.000.000 — citite din copia din corpus a Reglementărilor contabile.
Copia aia e **forma inițială 2014**, iar `anaf_surse/gen_index.py` chiar o marca așa
(`„forma initiala 2014; NU include Ordinul 1239/2021…"`). Nu m-am uitat la marcaj. Valorile la zi sunt
în **lei**, modificate de ORDIN 4.164/2024. Actul era complet, corect și în vigoare; **forma** era
veche. Forma nouă a fost adusă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.{html,txt}`,
amprentă `7636b1e1…d9cfe`. Clasa e scrisă în METODA, la formele de orbire prin construcție.

**Rămâne deschis la B:** **categoria de mărime nu există ca dimensiune în aplicație** — nu e câmp în
`firma_profil`, nu apare în vectorul fiscal. Pentru niciuna dintre cele 17 firme nu se poate spune, din
date, ce set de situații financiare datorează. E precondiția lui 1b pentru toată familia B.

**C. Declarații fiscale.** Toate articolele de mai jos au fost verificate pe **forma consolidată la zi a
Codului fiscal (consolidare 08.08.2026)**, respectiv a Codului de procedură fiscală (08.08.2026).

| declarație | temei | vigoare la sursă | firme |
|---|---|---|---|
| **D100** | CF **art. 56** „Plata impozitului și depunerea declarațiilor fiscale" | ÎN VIGOARE (alin. 1^1 abrogat 01-01-2024) | 10 |
| **D101** | CF **art. 42** alin. (1) — „până la data de **25 iunie** inclusiv a anului următor" | ÎN VIGOARE; **modificat 25-02-2026** (OUG 8/2026) | 7 |
| **D112** | CF **art. 81** (obligația plătitorilor de salarii) și **art. 147** (depunerea) | ambele ÎN VIGOARE (art. 81 mod. 01-01-2017; art. 147 alin. 1^1 mod. 01-01-2024) | de numărat la 1b |
| **D205** | **CF art. 132** „Obligații declarative ale plătitorilor de venituri cu reținere la sursă" — depunere „până în **ultima zi a lunii februarie** inclusiv a anului curent" | ÎN VIGOARE; alin. (2) modificat 18-12-2021 | de numărat la 1b |
| **D212** | **CF art. 122** „Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice" — „până la data de **25 mai** inclusiv a anului următor"; plus art. 116 pentru venituri din alte surse | ÎN VIGOARE | **0** (niciun PFA) |
| **D300** | CF **art. 323** „Decontul de taxă" | ÎN VIGOARE, fără marcaj | 11 |
| **D301** | CF **art. 324** „Decontul special de taxă și alte declarații" | ÎN VIGOARE; alin. (5) mod. 03-02-2020 | 1 confirmat (t006) |
| **D390** | CF **art. 325** „Declarația recapitulativă" | ÎN VIGOARE; partea introductivă a alin. (1) mod. 01-07-2024 | 5 |
| **D394** | nu e în Codul fiscal — **OPANAF 3769/2015 art. 1**: „Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii și achizițiile de bunuri și servicii realizate pe teritoriul României" | ÎN VIGOARE, fără marcaj (consolidare 17.09.2025) | 11 |
| **D406** | **Cod procedură fiscală art. 59^1** „Obligația de depunere a fișierului standard de control fiscal"; forma declarației: **OPANAF 1783/2021 art. 2** — „Fișierul standard de control fiscal (SAF-T) se transmite … prin intermediul Declarației informative D406" | ambele ÎN VIGOARE; art. 59^1 introdus 01-01-2022, ordinul consolidat 08.04.2025 | de stabilit la 1b |

**D. Evidențe speciale**

| evidență | temei, citat verbatim | vigoare |
|---|---|---|
| **Evidența operațiunilor de TVA** | CF **art. 321** „Evidența operațiunilor": „Persoanele impozabile stabilite în România trebuie să țină evidențe corecte și complete ale tuturor operațiunilor efectuate în desfășurarea activității lor economice." | ÎN VIGOARE, fără marcaj |
| **Jurnale pentru vânzări / borderouri de încasări** și **jurnale de cumpărări separate** | HG 1/2016 (norme), la regimul special al agențiilor de turism | act, nu articol — neverificată |
| **Evidența operațiunilor în regim special de marjă** | CF **art. 312** „Regimuri speciale pentru bunurile second-hand, opere de artă, obiecte de colecție și antichități": „să țină evidența operațiunilor pentru care se aplică regimul special" | ÎN VIGOARE |
| **Registrul de evidență fiscală** | CF **art. 19** (impozit pe profit) și CF **art. 68** (venit net în sistem real) | ambele ÎN VIGOARE (art. 68 alin. 1 mod. 01-01-2026) |
| **Registrul de casă** (cod **14-4-7A**, varianta **14-4-7/bA**, în valută **14-4-7/aA** și **14-4-7/cA**) | **OMFP 2634/2015, Anexa nr. 2** („Norme specifice de utilizare a documentelor financiar-contabile", MO 910 bis/9.12.2015), poz. 27–29 din nomenclator; modelul în **Anexa nr. 3** | act consolidat 01.08.2024 |
| plafoanele de numerar | Legea 70/2015 (în corpus, deja citată în cod cu `Temei` structurat) | verificată anterior (09.08.2026) |

**Cele patru căutări nerezolvate din prima trecere: ÎNCHISE, toate patru.** D205 → CF art. 132 ·
registrul de casă → OMFP 2634/2015 Anexa nr. 2 · D212 → CF art. 122 · D406 → CPF art. 59^1.

**Ce a rămas neverificat — și o afirmație de-a mea, corectată.** Spusesem că „cele cinci acte sunt
structurate pe puncte". **Nu sunt cinci, sunt două.** Verificat deschizându-le: OPANAF 3769/2015 are 23
de articole, OPANAF 1783/2021 are 15 — amândouă intră azi sub instrumentul de articol, și au fost
verificate în aceeași tură. Rămân **pe puncte**: Reglementările contabile (anexa OMFP 1802/2014, 58 de
marcaje pe punct) și Normele OMFP 2634/2015 — restanța **R2**. Rămâne neverificat și **OPANAF
2194/2025**, a cărui pagină de act nu expune articole (conținutul stă în anexe), deci cere altă cale.

### Pasul 1b — ce produce aplicația (FAMILIA A: registrele)

**Măsurat pe date reale, nu pe rute.** *„Există ruta" nu e „produce artefactul"* — deci fiecare
registru a fost cerut efectiv, pe firmele care au note contabile: t013 (21 note), t014 (5), t016 (2),
t003 (3), t005 (1), t017 (1).

| artefact | temei | se produce azi? | pe ce s-a probat |
|---|---|---|---|
| **Balanța de verificare, LUNAR** | L82 art. 22 | **DA, ȘI SE ÎNCHIDE** — vezi proba de mai jos | t013 08/2026 → 26 rânduri · t014 → 16 · t016 → 7 |
| **Registrul-jurnal** (14-1-1) | L82 art. 20 · OMFP 2634 Anexa 1 pct. 45 | **NU, în sensul normei** — iese ca listă de note, dar elementele cerute de pct. 45 **lipsesc din DATE**, nu din randare. Vezi Q2 | t013 08/2026, plus toți cei 6 tenanți cu note |
| **Registrul-inventar** (14-1-2) | L82 art. 20 · OMFP 2634 Anexa 1 pct. 46 | **NU** — niciun producător pentru partidă dublă | căutare pe `registru.?inventar`, `14-1-2` în `core/`, `main.py`, `static/js/`: singura potrivire e `rip_api.registru_inventar`, care e varianta **14-1-2/b**, de partidă simplă |
| **Cartea mare** (14-1-3) | L82 art. 20 · OMFP 2634 Anexa 1 pct. 47 | **NU** — motorul există (`core/motor.py:32 carte_mare`), **zero consumatori în tot repo-ul**, nicio rută | grep pe `carte_mare`: o singură apariție, definiția |
| **Registrul-jurnal de încasări și plăți** (14-1-1/b) + **Registrul-inventar** (14-1-2/b) | OMFP 2634 Anexa 1 pct. 48 · OMFP 170/2015 | **DA, dar neexercitat** — `core/rip_api.py` + ecran `rip_ecran.js` | **0 firme PFA** din 17, deci artefactul n-a fost produs niciodată pe date |


**Q1 — proba balanței: „DA" era mai slab decât „valid".** Familia C are arbitru extern (DUKIntegrator);
balanța n-are, deci „se produce" nu e o probă de aceeași tărie. Proba potrivită e **că se închide**:

| firmă | SI D = SI C | rulaje D = C | SF D = C | pe fiecare cont, SI + rulaj = SF |
|---|---|---|---|---|
| t013 (26 conturi) | 26.050,00 = 26.050,00 | 41.223,00 = 41.223,00 | 51.914,00 = 51.914,00 | **DA, toate** |
| t014 (16 conturi) | 19.760,00 = 19.760,00 | 20.222,00 = 20.222,00 | 30.163,00 = 30.163,00 | **DA, toate** |
| t016 (7 conturi) | 6.050,00 = 6.050,00 | 5.100,00 = 5.100,00 | 7.520,00 = 7.520,00 | **DA, toate** |

Deci „DA" pe balanță are acum o probă a artefactului, nu doar a rutei. **Ce nu spune proba:** că soldurile
sunt CORECTE — o balanță greșită se poate închide perfect. Spune că e coerentă cu sine.

**Q2 — documentul justificativ lipsește din DATE, nu din randare, și asta mută verdictul.**
`inregistrari` are coloanele `numar`, `factura_id` și **`document_ref`**. Pe date reale, toți cei șase
tenanți cu note (33 în total):

| coloană | populată |
|---|---|
| `document_ref` | **0 din 33** |
| `numar` | **1 din 33** (doar nota de amortizare, `AMORT-2026-08`) |
| `factura_id` | 14 din 33 |

Iar în cod, **nimic nu scrie `inregistrari.document_ref`**: singurele apariții sunt o CITIRE în
`control_incrucisat.py:491` (care caută `document_ref = 'SAL LL/AAAA'`, deci așteaptă o valoare pe care
n-o scrie nimeni) și `registratura_api.py`, care lucrează pe **altă tabelă**.

**Consecința, scrisă ca atare:** cele 19 note fără nicio legătură la un document nu se pot desface până
la documentul care le justifică. **Asta nu e o coloană de adăugat la randare — e P14**, iar PARȚIAL era
prea blând. Registrul-jurnal trece în **lista 3**, cu cauza „iese, dar nu ca artefactul cerut de normă".
**Ridică și interdicția 32** („o poziție de declarație care nu se poate desface până la document"), care
e NEÎNCEPUTĂ — aici are o primă instanță, măsurată pe date.


**Răspunderea, după P23:** niciunul dintre cazurile de mai sus nu e „lipsesc date". Datele există —
t013 are 21 de note și o balanță de 26 de rânduri din ele. Registrul-inventar și Cartea mare **nu se
pot produce indiferent de date**, adică rândul al treilea din tabelul P23: **a aplicației**.

**Ce nu vede măsurătoarea:** un producător care ar exista sub alt nume decât cele căutate · un export
generic (rapoarte configurabile) care ar putea reconstitui un registru fără să-l numească · și nu
spune nimic despre **corectitudinea** balanței, doar că iese cu rânduri pe date reale.


### Pasul 1b — ce produce aplicația (FAMILIA C: declarațiile)

**Instrumentul e al aplicației, nu unul nou:** aceleași rute pe care le folosește F2 din
`frontend_test/audit_tenant.py` — `/declaratii/tipuri`, `/control-fiscal/{id}`,
`POST /declaratii/{tip}/valideaza`, care **generează și trece prin DUKIntegrator**. Ruta întoarce
`stare` ∈ {valid, erori, gri}, plus `operatiuni` — numărul de operațiuni din declarație, poarta care
face ca o declarație golită de un query rupt să nu arate ca una legitim goală.

**Măsurat pe 08/2026, pe trei firme cu date:** t013 (micro · TVA lunar · IC — cea mai bogată),
t016 (același regim, firmă de test cu defecte deliberate), t003 (micro · TVA trimestrial).

| declarație | t013 | t016 | t003 |
|---|---|---|---|
| **D100** | **valid**, 1 op. | REFUZ: *„nu se depune pe zero: venituri 70x = 0. Există 3 facturi emise ne…"* | REFUZ, aceeași cauză (2 facturi) |
| **D101** | **valid** | **valid** | **valid** |
| **D112** | **valid** | REFUZ: *„A DOUA CALE: SUSPECTE … salariat 2: brut 1000 SUB salariul minim 4325"* | REFUZ: *„PERIOADA_BLOCATĂ: pontajul lunii nu e CONFIRMAT"* |
| **D205** | **valid**, 1 op. | REFUZ: *„fără niciun beneficiar de venit"* | REFUZ, aceeași cauză |
| **D300** | **valid**, 18 op. | **valid**, 8 op. | **valid, 0 op.** |
| **D301** | REFUZ: *„pe zero, DAR există 1 achiziție intracomunitară înregistrată ca FACTURI în perioadă"* | REFUZ: *„nu se generează pe zero … OPANAF 592/2016"* | REFUZ, aceeași cauză |
| **D390** | **valid**, 3 op. | **valid**, 1 op. | REFUZ: *„nu se depune pe zero: luna n-are nicio operațiune IC"* |
| **D394** | **valid**, 1 op. | **valid**, 1 op. | **valid**, 1 op. |
| **D406** | **valid**, 19 op. | **valid**, 4 op. | **valid**, 2 op. |

**Rezultatul principal: pe firma cu date complete (t013), 8 din 9 declarații se produc ȘI trec
arbitrul oficial, cu zero erori.** Nu „există ruta" — DUKIntegrator a rulat pe XML-ul generat.

**Refuzurile NU sunt toate același lucru.** Trei feluri, iar distincția e chiar cea din P23:

1. **Refuz corect, cu contradicția numită** — t013 D301 și t016/t003 D100. Aplicația **nu produce un
   „nu se datorează" peste o absență cunoscută**: spune că există achiziții IC înregistrate ca
   facturi, sau facturi emise necontabilizate. Asta e interdicția 67 funcționând, nu un defect.
2. **Refuz pe date lipsă** — t003 D112: *„pontajul lunii nu e CONFIRMAT"*, pe **șapte** perioade
   (12/2025 – 07/2026). Îl deschisesem ca **candidat pentru interdicția 68** — o lipsă semnalată abia
   în ziua depunerii. **RĂSPUNS, în aceeași tură: NU e 68.** Confirmarea se cere **la introducere**,
   pe ecranul unde omul lucrează, nu doar la generare: ecranul de pontaj arată *„Pontaj neconfirmat —
   informativ; calculele din aval (tichete, statul de plată) se blochează până la confirmare"* plus
   butonul „Confirmă pontajul lunii" (`firme.js:670`), iar statul de plată repetă avertismentul pe
   lună și pe fiecare salariat, cu „tichete blocate" (`firme.js:775-819`). Deci lipsa a fost cerută
   **când datele mai puteau fi obținute** — exact pragul din P23. **Merge în lista 2 a verdictului:
   nu iese, fiindcă lipsesc date cerute la timp — a omului, nu a aplicației.**
3. **Refuz pe absență legitimă** — D205 „fără niciun beneficiar", D301/D390 „pe zero". Corect.

**Un semnal fin, de privit, nu de concluzionat:** pe t003, **D300 iese `valid` cu 0 operațiuni**, în
timp ce **D100 refuză pe aceeași firmă** fiindcă „veniturile contabilizate 70x = 0, deși există 2
facturi emise necontabilizate". Același fapt — facturi neintrate în contabilitate — produce
**refuz** la un motor și **declarație goală validă** la altul. Nu spun care are dreptate; spun că nu
pot avea amândoi.

**Ce nu vede măsurătoarea:** o singură lună (08/2026) · trei firme din 17 · nu verifică dacă cifrele
din declarație sunt CORECTE, doar că declarația iese și trece arbitrul · D212 și declarațiile fără
interfață n-au fost atinse (sunt în afara perimetrului, prin decizie).

**Sonda a scris, și o declar:** `audit_log` +30 (o citire de date personale lasă urmă — excepția
scrisă în Partea II). `declaratii_coada` și `declaratii_depuse`: **neatinse**, verificat prin snapshot
înainte/după.

### Pasul 1b — ce produce aplicația (FAMILIA B: situațiile financiare)

**Măsurată abia acum, fiindcă R3 părea s-o blocheze. Nu o bloca — o bloca doar parțial.**

| artefact | temei | se produce azi? | proba |
|---|---|---|---|
| **Bilanț (S1005)** și **Cont de profit și pierdere (F20 / S1003)** | Reglementările contabile pct. 20–21 | **producător DA, dar NU ajunge la om** — `core/bilant_api.genereaza(conn, schema, an)` produce XML pe date reale: **1065 octeți pe t013**, cu două avertismente proprii, cinstite („F20 an precedent necompletat"; „F(rd15)=4947 != J(rd49)=22210 — datorii>1an/provizioane pot explica diferența"). `core/bilant.py` are `xml_s1005`, `xml_s1003`, `f10_din_balanta`, `f20_complet_din_rulaje` | **zero rute** în `main.py` (grep pe `bilant` în declarațiile de rută: nicio potrivire), deci nici ecran |
| **Note explicative** | pct. 20 alin. (2) și pct. 21 le cer în ambele seturi | **NU** — zero potriviri pe `note explicative` în `core/` și `main.py` | — |
| **categoria de mărime**, care decide CARE set se datorează | pct. 9 | **derivabilă din date, dar nederivată nicăieri** | vezi mai jos |

**Categoria de mărime: datele EXISTĂ.** Derivată de probă pe **toate cele 17 firme**, din
`inregistrari_linii` (active pe clasele 2/3/5 la debit, cifră de afaceri pe 70x) și din `salariati`,
cu regula „nu depășește limitele a cel puțin **două din trei**". Toate ies *microentitate* — dar asta
e o proprietate a datelor de test (sume mici), nu a metodei. **Ce nu spune proba:** `active` calculat
pe rulaje e o **aproximare**, nu totalul din bilanț; servește ca să arate că datele sunt acolo, nu ca
să dea cifra oficială.

**Verdictul familiei B, după decizia pe lista 3:**
- **bilanțul și CPP** → **lista 3**, cauza *„producătorul există, dar nu ajunge la om"* — aceeași
  formă ca jurnalul regim marjă, tot vina aplicației, nu a datelor;
- **notele explicative** → **lista 3**, cauza *„nu există producător"*;
- **categoria de mărime** rămâne precondiția care spune CARE set se datorează — dar nu mai e o
  necunoscută, e un **calcul nefăcut**.

### Pasul 1b — ce produce aplicația (FAMILIA D: evidențele speciale)

| evidență | temei | se produce azi? | proba |
|---|---|---|---|
| **Registrul de casă** (14-4-7A) | OMFP 2634 Anexa 2 | **DA** — motor pur `core/casa.py:44 registru_casa`, API `core/casa_api.py:71 registru`, rută `/tenants/{id}/casa/registru`, ecran în `firme.js` | lanț complet, de la motor la ecran |
| **Jurnal regim marjă** (art. 312) | CF art. 312 | **producător DA, ecran NU** — ruta `/tenants/{id}/jurnal-marja` există, cu comentariul propriu: *„raport regim marjă — fără UI încă, păstrat deliberat"* | `main.py:7061` |
| **Evidența operațiunilor de TVA** (jurnale de vânzări / cumpărări) | CF art. 321 | **NU ca artefact** | căutat pe `jurnal_vanzari`, `jurnal_cumparari`, `jurnale_tva`, `jurnal_tva`, apoi pe `jurnal (de) vânzări/cumpărări`, `raport tva`, `situatie tva`, `registru tva` — **zero potriviri**; rutele cu „tva" în nume sunt două, și niciuna nu e un jurnal. Datele agregate există (d300, d394), **documentul nu** |
| **Registrul de evidență fiscală** | CF art. 19 (profit) · art. 68 (venit real) | **NU** | zero potriviri pe `registru_evidenta_fiscala`, `evidenta_fiscala` |

**Q1 — jurnalul regim marjă: absență DECLARATĂ sau UITATĂ?** Verificat: `ISTORIC_TENANTI.md` conține
declarații de perimetru pentru **două firme** — t006 (regim N1) și t001 (celula S4). **t007 („Agentie
Turism Marja") și t008 („Second Hand Marja") n-au niciuna.** Singurul loc unde absența ecranului e
scrisă e **comentariul rutei** (`main.py:7061`): *„raport regim marjă — fără UI încă, păstrat
deliberat"*. **Un comentariu în cod nu e o declarație de perimetru** — nu se citește de nimeni care se
uită unde suntem, nu are stare și nu se aprinde când devine neadevărat. Deci: **absență uitată în
registru, declarată doar lângă cod.** Rămâne prag 2, dar cauza e scrisă acum.

**Q2 — evidența TVA: lipsește doar documentul, sau și datele?** Verificat pe t003, la nivelul cerut de
art. 321: `facturi` are `data_emitere`, `numar`, `serie`, `directie`, `tert_nume`, `tert_cui`, `total`,
`tva`, `taxare_inversa`, `categorie_331`, `tip_operatiune`; `factura_linii` are `descriere`, `um`,
`cantitate`, `pret_unitar`, **`cota_tva`**, `cont_venit`. **Baza și TVA pe cotă sunt derivabile pe
fiecare linie, cu partener și cod.** Deci **absență simplă — lipsește documentul, nu substanța**, și
rămâne la pragul 2, nu e a doua instanță de P14. **O rezervă, măsurată:** una din cele trei facturi
ale lui t003 are `tert_cui = NULL` — completitudinea datelor de partener e o chestiune separată, de
1b, nu a structurii.

**Verdictul familiei D, după decizia de azi:** registrul de casă în **lista 1**; jurnalul de marjă,
evidența TVA și registrul de evidență fiscală în **lista 3**, cu cauza *„nu există producător"* —
pentru jurnalul de marjă, cauza e mai exact *„producătorul există, dar nu ajunge la om"*, ceea ce e
tot vina aplicației, nu a datelor.

**Ce nu vede măsurătoarea:** un producător sub un nume pe care nu l-am căutat (termenii sunt scriși
mai sus, ca să se poată contrazice) · un raport configurabil care ar reconstitui un jurnal fără să-l
numească · faptul că, pentru trei din cele patru firme din matrice cu operațiuni de TVA, nu s-a cerut
efectiv artefactul, ci s-a căutat producătorul lui.

### DECIS 22.08.2026 (Costin): lista 3 se lărgește, nu se adaugă a șasea

Tabelul P23 din 1b are **trei** cauze pentru un artefact care nu iese: date lipsă **cerute la timp**
(a omului) · date lipsă **necerute sau cerute prea târziu** (a aplicației) · **artefactul nu se poate
produce indiferent de date** (a aplicației).

Cele cinci liste ale verdictului 1d au loc doar pentru primele două: lista 2 („nu ies, fiindcă lipsesc
date cerute la timp") și lista 3 („nu ies, fiindcă lipsesc date necerute sau cerute prea târziu").
**A treia cauză n-are listă** — iar ea e exact cazul găsit la familia A: Registrul-inventar și Cartea
mare nu ies, și nu din lipsă de date.

**Decizia, cu motivul ei:** *„Lista 3 e «nu iese, din vina aplicației»; un artefact care nu se poate
produce indiferent de date e **forma extremă a aceleiași cauze**, nu altă natură."*

Deci **lista 3 se citește de acum ca „nu iese, din vina aplicației"**, cu două forme: *lipsesc date pe
care aplicația nu le-a cerut la timp* și *nu există producător, indiferent de date*. **Cauza se scrie
lângă artefact**, ca să nu se piardă distincția în interiorul listei.

**Clasificate acum, în lista 3:**

| artefact | cauza scrisă |
|---|---|
| **Registrul-inventar** (14-1-2) | **nu există producător** pentru partidă dublă — nu „lipsesc date" |
| **Cartea mare** (14-1-3) | **nu există producător**: motorul `core/motor.py:32` există, cu zero consumatori |
| **Registrul-jurnal** (14-1-1) | **iese ca listă, dar nu ca artefactul cerut de normă** — vezi Q2 mai jos: elementele din pct. 45 lipsesc **din date**, nu din randare |


### Pasul 1c — se poate verifica pe ecran (interdicțiile 63–66)

**Măsurat pe 22.08.2026, pe commit `4033a14`**, pe eșantionul cerut de plan: netul de pe fluturaș, o poziție din
decont, un rând din D112. Cifrele stau în secțiunile 63–66; aici e forma pe care o dau împreună.

**Forma repetată: verificarea EXISTĂ și se oprește înainte de ecran.** Nu e o aplicație care n-a
făcut munca — e una care a făcut-o și n-a predat-o. Componentele deducerii sunt calculate și desfăcute
(`baza`/`tineri`/`copii`), apoi colapsate la un total. Cele 57 de obiecte `Temei` leagă normă de
implementare și niciunul nu ajunge pe ecran ca obiect. `registru_interpretari.py` ține alegerile pe
care legea le-a lăsat deschise, cu varianta respinsă lângă fiecare — zero potriviri în tot JS-ul.
Reconcilierile D300/D205 verifică pe a doua cale și blochează la divergență, dar nu spun nimic omului.
**A doua cale e construită pentru mașină, nu pentru contabil.**

**Ce se poate verifica azi, onest:** fluturașul PDF e singurul loc unde o cifră își arată componentele.
Nu ecranul — hârtia.

#### Reparație de PRAGUL 1, făcută la aceeași trecere

Măsurătoarea lui 63 a scos ceva ce nu e lipsă, ci **afirmație falsă pe un document care ajunge la
salariat**: randul fluturașului scria **„Deducere personala"** și tipărea `deducere['total']`, care
include și deducerile **suplimentare** (CF art.77 alin.(4^1) tineri sub 26; alin.(4^2) copii
școlarizați). Pe un tânăr la salariul minim din iulie 2026: eticheta „Deducere personala", cifra
**1.513,75**, deducerea personală **865,00**. Numea un lucru și arăta altul.

- **măsurat înainte de reparație**: **3 din 5** cazuri obișnuite produc eticheta falsă · **2 din 24**
  de salariați de test activi la 01.07.2026 sunt în situația asta (`tenant_017`: TANAR SUB26, PARINTE
  SCOALA). Cuvântul `tineri` nu apărea **deloc** în `stat_plata_api.py`: deducerea pentru tineri n-avea
  nume nicăieri pe drumul spre hârtie.
- **reparat**: `randuri_deducere(r)` întoarce randuri NUMITE, unul per deducere din lege; `stat_plata`
  duce mai departe `deducere_baza` / `deducere_tineri` / `deducere_copii`. `deducere` rămâne TOTALUL,
  deci **D112 nu se atinge** (raportează totalul, corect). Un exemplar înghețat fără componente nu
  împrumută eticheta greșită — își spune pe nume: „Deducere personala si suplimentare (total)".
- **verificat pe date reale**: TANAR SUB26 → 583,88 personală + 648,75 tineri (PDF 43.969 octeți);
  PARINTE SCOALA → 367,63 + 200,00 copii (43.972); salariații neafectați rămân la un rând (43.919).
- **gardat**: `core/test_fluturas_eticheta.py`, 13 teste. **RED-proof de două ori**, din copie de
  siguranță: (1) revenirea la randul unic → **4 roșii**, exact cele trei cazuri care mint plus testul
  de numire; (2) o componentă care există în calcul și n-are rand → **4 roșii**, printre care
  aserțiunea anti-vacuu. Garda nu apără instanța, ci **corespondența 1:1 pe NUME** între deducerile din
  calcul și randurile de pe hârtie: o deducere nouă adăugată de lege și netipărită o face să cadă.

**Ce NU s-a reparat acum, și de ce:** absența motivată (interdicția 64) — că PARINTE NEDECL primește
0,00 fiindcă îi lipsește declarația, și hârtia tace — **nu e prag 1**: cifra e corectă și nicio
afirmație nu e falsă. Intră la triaj cu celelalte.

### Pasul 1d — VERDICTUL: cele cinci liste

**Măsurat pe 2026-08-22, pe commit `4033a14`.** Nimic nou măsurat aici: 1d **clasifică** ce au scos 1a
(ce cere legea), 1b (ce produce aplicația) și 1c (se poate verifica pe ecran). Unde clasificarea a
cerut o cifră pe care n-o aveam, e măsurată și numită mai jos.

**Criteriul listei 1 e conjuncție de trei**, nu de două: *iese* ȘI *se validează* ȘI *se poate verifica
pe ecran*. Al treilea a fost măsurat abia la 1c — și el mută aproape tot.

#### Lista 1 — ies, se validează ȘI se pot verifica pe ecran

| artefact | de ce trece toate trei |
|---|---|
| **Registrul de casă** (14-4-7A) | iese pe lanț complet (motor → API → ecran); se vede **întreg pe ecran**, operațiune cu operațiune: dată, sumă, **sold curent după fiecare**, partener, document, categorie; iar avertismentele lui poartă **temei pe ecran** (`firme.js:1798`). Singurul artefact din tot inventarul unde o cifră își arată componentele fără să descarci nimic |

**Un singur artefact din 23.** Iar el arată că aplicația **știe** să facă lista 1 — a făcut-o o dată,
complet. Restul nu e o problemă de capacitate, e una de nepredare.

#### Lista 2 — nu ies, fiindcă lipsesc date CERUTE LA TIMP (a omului, nu a aplicației)

| artefact | firma | ce lipsește, și dovada că a fost cerut la timp |
|---|---|---|
| **D112** | t003 | pontajul lunii neconfirmat, pe 7 perioade (12/2025–07/2026). Cerut **pe ecranul unde omul lucrează**, nu la generare: ecranul de pontaj („calculele din aval se blochează până la confirmare" + buton „Confirmă pontajul lunii", `firme.js:670`), plus statul de plată, care repetă avertismentul pe lună **și pe fiecare salariat** |
| **D100**, **D205** | t016, t003 | facturi emise necontabilizate / niciun beneficiar de venit — refuzuri cu **contradicția numită**, nu tăcere. Interdicția 67 funcționând |
| **D301**, **D390** | t013, t016, t003 | „pe zero", cu temei citat (OPANAF 592/2016) sau cu contradicția numită („există 1 achiziție IC înregistrată ca facturi") |

**Lista 2 poate avea conținut fără ca aplicația să fie defectă** — asta măsoară ea. Toate cele de mai
sus refuză **spunând de ce**, ceea ce e chiar comportamentul cerut.

#### Lista 3 — nu ies, DIN VINA APLICAȚIEI (lărgită prin decizia de mai sus; cauza scrisă lângă fiecare)

| artefact | cauza |
|---|---|
| **Registrul-inventar** (14-1-2) | **nu există producător** pentru partidă dublă (singura potrivire e varianta 14-1-2/b, de partidă simplă) |
| **Cartea mare** (14-1-3) | **nu există producător**: motorul `core/motor.py:32 carte_mare` există, cu **zero consumatori** în tot repo-ul |
| **Registrul-jurnal** (14-1-1) | **iese ca listă, dar nu ca artefactul cerut de normă** — elementele din OMFP 2634 Anexa 1 pct. 45 lipsesc **din date**: `document_ref` 0/33, `numar` 1/33, și **nimic în cod nu scrie `document_ref`** |
| **Note explicative** | **nu există producător** — zero potriviri în `core/` și `main.py` |
| **Bilanț (S1005)** și **CPP (F20/S1003)** | **producătorul există și produce pe date reale** (1065 octeți pe t013), dar are **zero rute** — nu ajunge la om |
| **Jurnal regim marjă** (art. 312) | **producătorul există, ecranul nu** — absență declarată doar într-un comentariu de cod (`main.py:7061`), care nu e declarație de perimetru |
| **Evidența operațiunilor de TVA** (art. 321) | **nu există producător ca artefact** — substanța e derivabilă pe fiecare linie (bază și TVA pe cotă, cu partener și cod), lipsește documentul |
| **Registrul de evidență fiscală** (art. 19 · art. 68) | **nu există producător** — zero potriviri |
| **categoria de mărime** (precondiție, pct. 9) | **nu se calculează** — datele există, derivarea s-a probat pe toate 17 firmele, dar nimeni n-o face și nimic n-o stochează (R3, îngustată) |

#### Lista 4 — ies, dar NU se validează

**Goală.** Pe firma cu date complete (t013), **8 din 9** declarații trec DUKIntegrator cu zero erori;
a noua (D301) refuză corect, deci e în lista 2, nu aici. **Ce nu spune golul ăsta:** s-a măsurat o
singură lună (08/2026), pe trei firme din 17, iar arbitrul verifică **forma**, nu dacă cifrele sunt
corecte. Lista 4 e goală **pe ce s-a măsurat**, nu pe tot.

#### Lista 5 — ies și se validează, dar NU se pot verifica pe ecran

**Aici a ajuns aproape tot ce funcționează.** Măsurat la 1c, plus o măsurătoare cerută de clasificare:

| artefact | ce se poate verifica azi |
|---|---|
| **D100 · D101 · D112 · D205 · D300 · D301 · D390 · D394 · D406** | **cele nouă module au 7.009 linii și 0 obiecte `Temei(` — toate nouă.** Nicio rută nu desface o poziție de declarație în ce a compus-o; `POST /declaratii/{tip}/valideaza` întoarce `stare` și **numărul** de operațiuni, nu operațiunile. Contabilul vede că declarația e validă și nu poate vedea din ce e făcută |
| **Balanța de verificare** | **nu se vede pe ecran deloc.** Ecranul are titlu, navigare pe lună și **un buton „Descarcă PDF"** (`firme.js:2652`) — atât. Balanța se închide (probat: SI D=C, rulaje D=C, SF D=C, și SI+rulaj=SF pe fiecare cont, pe t013/t014/t016), dar din PDF nu se poate merge la notele din spatele unui cont |
| **netul de pe fluturaș** | componentele se văd **doar în PDF-ul descărcat**; pe ecranul statului nu ajung `deducere`, `facilitate`, `cas_suprataxa`, `cass_suprataxa`. Cuvintele „deducere"/„facilitate" apar în tot JS-ul **numai ca etichete pe formulare de introducere** |

**Ce NU e în nicio listă, și de ce:** **RIP** (14-1-1/b, 14-1-2/b) și **D212** — zero firme purtătoare
(niciun PFA din 17). Nu sunt „gata" și nu sunt „defecte": n-au fost exercitate niciodată. Se numesc
aici ca să nu fie confundate cu lista 1. Iar **jurnalele de vânzări pentru agențiile de turism**
(HG 1/2016) au temei **neverificat la sursă** — act, nu articol; nu se clasifică pe un temei nemăsurat.

#### Ce spune verdictul, citit ca răspuns la întrebarea fazei 1

**Criteriul de gata al aplicației — listele 3, 4 și 5 goale — NU e îndeplinit.** Lista 4 e goală pe ce
s-a măsurat; listele 3 și 5 nu sunt.

Dar cele două nu sunt același fel de datorie, și confundarea lor ar duce munca în locul greșit:

- **lista 3 (9 artefacte)** e muncă de **construit** — producători care nu există, rute care lipsesc,
  o coloană pe care n-o scrie nimeni;
- **lista 5 (11 artefacte)** e muncă de **predat** — totul e deja calculat, verificat pe a doua cale și
  valid; se oprește înainte de ecran. Cele 57 de obiecte `Temei` există și niciunul nu ajunge la om;
  `registru_interpretari.py` ține alegerile pe care legea le-a lăsat deschise, cu varianta respinsă
  lângă fiecare, și are **zero potriviri în tot JS-ul**; reconcilierile blochează la divergență și nu
  spun nimic.

**Cea mai ieftină mișcare nu e în lista 3.** Registrul de casă arată că lista 1 e atinsă când cifra își
arată operațiunile și avertismentul își poartă temeiul — mecanismul e scris o dată și nu e reutilizat.

**Ce nu vede verdictul:** clasificarea moștenește limitele măsurătorilor pe care le rezumă — o lună,
trei firme din 17 pentru familia C, un ecran pentru fluturaș, iar pentru corectitudinea cifrelor
**nicio măsurătoare**: „valid la DUKIntegrator" e o afirmație despre formă. Verdictul spune ce ajunge
la om și în ce stare, **nu** că cifrele sunt corecte.

#### DECIS 23.08.2026 (Costin): ordinea nu e L3 înaintea lui L5

**Listele rămân separate, dar ordinea se inversează.** Motivul, scris cu cuvintele deciziei: *„L3 e
construcție — lucruri care nu există. L5 e predare — totul e făcut, se oprește înainte de ecran. Un
artefact din L5 costă ore; unul din L3 costă zile."* Iar pentru propoziția din Partea 00 — *contabilul
depune din aplicație fără să recalculeze* — **L5 contează mai mult: o cifră corectă pe care n-o poate
verifica e o cifră pe care o reface.**

**La punctul de decizie 2, L5 intră înaintea lui L3** — cu **excepția** artefactelor din L3 obligatorii
prin lege: **Cartea mare**, **Registrul-inventar**, **registrul de evidență fiscală**. Acelea nu pot
aștepta: *absența lor nu e neplăcută, e neconformă.*

**O corecție la justificarea mea, cerută de întrebarea 3.** Am scris că „L5 costă ore". **Nu e adevărat
pentru tot L5.** Zece dintre cele unsprezece intrări sunt calculate și nepredate — acolo ține. A
unsprezecea, **interdicția 65** (diferența față de luna anterioară), **nu e calculată deloc**: 0
mecanisme în Python, 0 în JS. Artefactul stă în L5 fiindcă listele clasifică **artefacte**, iar
fluturașul iese și se validează; dar **munca** e de tip L3. Deci:

| în L5 | ce fel de muncă | de ce |
|---|---|---|
| balanța pe ecran · componentele fluturașului | **predare** — ore | balanța se produce (PDF descărcabil), iar `deducere`/`deducere_baza`/`deducere_tineri`/`deducere_copii` sunt deja în răspunsul API (`core/stat_plata_api.py:109–114`) |
| temeiul pe ecran (9 declarații) · desfacerea unei poziții | **construcție** — zile *(corectat 23.08)* | cele 57 de obiecte `Temei` sunt în `common.py`/`salarizare.py`; **modulele de declarație au zero**, iar desfacerea n-are producător. Numărătoarea de 57 măsura alt domeniu decât cel despre care afirma |
| **interdicția 65** — explicația diferenței față de luna anterioară | **construcție** — zile | nimic nu compară două perioade; nu e nepredat, e nescris |

**Lista nu se schimbă; ordinea în interiorul ei, da.** Cele patru de sus intră primele, fiindcă acolo
ține argumentul de cost care a decis ordinea.


#### CORECȚIE 23.08.2026 — „salariați reali" era cuvântul greșit

**Întrebarea lui Costin:** *„care 24? Dacă sunt ai unei firme reale, cineva a primit o hârtie pe care
scria «Deducere personală 1.513,75» și nu era deducerea personală."*

**Măsurat, la sursă:** cei 24 de salariați activi la 01.07.2026 sunt **fixturi de test**, toți — numele
sunt descrieri de scenariu: `MINIM EXACT`, `PESTE MINIM`, `PARTTIME SUBFLOOR`, `CM COD01`, `TANAR
SUB26`, `PARINTE NEDECL`. Și **toate cele 17 firme sunt de test**: `Coafor Micro Neplatitor SRL`,
`Second Hand Marja SRL`, `GAMA DEFECT-MIGRARE`, `Firma Grea Audit SRL`. **Niciun client real.**

**Deci nimeni n-a primit hârtia greșită.** „Reali" însemna la mine „existenți în baza de date"; cuvântul
corect e **„de test"**. Corectat unde l-am scris: la interdicția 64 și în blocul 1c.

**Ce ridică asta, și nu decid eu.** Pragul 1 e definit ca *„produce efect greșit la un om ACUM"*. Pe
instalarea asta nu există niciun om — deci, citit literal, **pragul 1 e gol prin construcție**, iar
cele trei instanțe consemnate în `PLAN_LUCRU.md` (TVA-ul din D300 „la 3 plătitori", codul de concediu,
eticheta de pe fluturaș) n-ar fi trebuit să-l atingă. Citit ca **atingibilitate** — *ar produce, la
prima firmă reală aflată în acea stare* — toate trei rămân corecte, iar pragul rămâne util.

**Nu aleg între cele două citiri**, fiindcă e o ambiguitate a planului, nu a măsurătorii, iar regula e
că planurile nu se interpretează. **DECIS 23.08.2026 (Costin): se citește ca ATINGIBILITATE** — lămurirea și motivul, în `PLAN_LUCRU.md`. Până atunci, cele trei reparații rămân făcute:
niciuna n-a stricat ceva, toate au gardă și RED-proof.


#### Ce alte cifre au fost măsurate cu `graf_temei` (întrebarea 6)

**Cinci locuri**, și cel mai important nu e o cifră:

| unde | ce | stare |
|---|---|---|
| `core/test_agenda.py:384` | `STALE_BAZA_BASELINE = 14` | **INVALIDATĂ** — nu se corectează, se re-măsoară pe graful calificat |
| `TESTE.md:193` | `depinde_de("salariu_minim") = 12 funcții` | **INVALIDATĂ** — aceeași cauză |
| `TESTE.md:491` | „29 clustere structurale · 40 fiscale, majoritatea zero în graf" | **INVALIDATĂ** — cifrele au fost citite de pe graful conflat |
| `TESTE.md:332` | **secvența persistată** — ordinea deterministă a celor 64 de clustere, sortată topologic pe `graf_clustere` | **INVALIDATĂ ca ordine.** Nu e o cifră: e ordinea în care s-a executat campania din 03–04.08. Nu spune că verificările sunt greșite — spune că **ordinea lor n-a fost cea calculată** |
| `CONFORMITATE.md`, interdicția **1** | `131` brut (din care ~100 reale, pe eșantion de 30) | **INVALIDATĂ 23.08.2026** — nu se corectează, se re-măsoară. Termenii ei (`A+C+E−43`) au fost recalculați pe un domeniu **lărgit** (`scan_constante`, calibrarea negativă), deci descompunerea nu se mai poate reface, iar cifra nu se poate crede ca atare. *O cifră ai cărei termeni nu se mai pot reconstitui se invalidează, nu se corectează* — aceeași regulă ca la `STALE_BAZA_BASELINE` |
| `TESTE.md:284` | `clustere_indirect(act)` — instrumentul care răspunde *„ce se atinge când se schimbă o lege"* | **INVALIDAT ca instrument.** Cel mai grav consumator: e unealta de propagare a modificărilor legislative |

**Formularea, ca regulă:** o cifră măsurată cu un instrument despre care s-a dovedit ulterior că vede
greșit **nu se corectează, se invalidează** — se re-măsoară de la zero, fiindcă nu se știe în ce
direcție greșea. Marcate ca atare mai sus; nu sunt șterse, ca să rămână urma.


#### De când există `graf_temei` și ce s-a decis pe el (întrebarea 1)

**Din 01.08.2026** — commit `e516a23`, *„Model de temei ETAPA 3: graful de dependențe fiscale, extras
din cod"*. Deci a fost conflat **22 de zile**, iar în intervalul ăsta a stat sub el mai mult decât
cele cinci cifre din registru:

- **campania Sesiunii A, 03–04.08.2026** — cele 64 de clustere verificate „în ordine deterministă,
  sortare topologică pe `graf_clustere`". **Verificările în sine NU sunt invalidate**: fiecare cluster
  a fost confruntat la sursă, iar dovada e în `TESTE.md` lângă fiecare. **Ordinea lor este** — a fost
  calculată pe un graf care lega greșit clusterele între ele. Consecința practică e mică, fiindcă
  s-au făcut *toate*; ar fi contat dacă s-ar fi oprit la jumătate.
- **`clustere_indirect(act)`** — unealta care răspunde *„ce se atinge când se schimbă o lege"*, prin
  `cote_cluster`. **Asta e cea gravă**, și acum are cifra ei: pe `salariu_minim`, graful vedea **12**
  funcții din **83**. Orice modificare legislativă propagată cu unealta asta în cele 22 de zile a
  primit o listă de locuri de actualizat **de șapte ori mai scurtă decât realitatea**.
- **`STALE_BAZA_BASELINE`** a fost ridicat 3 → 6 → 14 pe 02.08 și 07.08, cu motive scrise — dar toate
  trei cifrele au fost citite de pe graful conflat.

**Ce NU s-a decis pe el:** nicio valoare fiscală, niciun temei, nicio cifră de declarație. Graful
răspunde la *„ce depinde de ce"*, nu la *„cât e"*. Daunele sunt de **acoperire a verificării**, nu de
conținut — iar asta se repară re-măsurând, ceea ce s-a și făcut.


#### A fost `graf_temei` calibrat vreodată? — și de ce contează pentru faza 4

**Da, din prima zi — și tocmai de asta e instructiv că a supraviețuit 22 de zile conflat.**
`core/test_graf_temei.py` există din `e516a23` (01.08.2026) și are calibrare **în ambele direcții**:

- **pozitivă** — `depinde_de("salariu_minim")` trebuie să conțină `deducere_personala` și
  `calcul_salariu`, iar variantele datate să apară `direct`; `_calcul_salariu_2018` trebuie să ceară
  `salariu_minim`, `facilitate_salariu_minim` și `plafon_facilitate_salariu_minim`;
- **negativă** — `test_graf_reflecta_codul_nu_o_lista_manuala`: o funcție care **nu** cheamă `cota()`
  (`_q`, rotunjirea) **nu are voie** să apară ca dependență directă.

**Deci n-a lipsit calibrarea. A lipsit calibrarea pe MODUL ÎN CARE INSTRUMENTUL PUTEA GREȘI.** Cele
patru afirmații pozitive și cea negativă trec la fel de bine pe graful conflat ca pe cel reparat,
fiindcă toate cinci privesc **spina `salarizare`**, unde numele erau unice. Nicio afirmație nu punea
întrebarea *„ce se întâmplă dacă două fișiere definesc aceeași funcție"* — și exact acolo era defectul.

**Regula, pentru criteriul lărgit al fazei 4:** *„instrumentul a fost calibrat" nu e o întrebare
binară.* Se întreabă **pe ce a fost calibrat**, și dacă printre cazuri se află **modul de eșec propriu
construcției lui**. Un instrument care cheie pe nume se calibrează pe o coliziune de nume; unul care
citește marcaje se calibrează pe două marcaje lipite — cum s-a văzut la `vigoare_punct` în aceeași zi.
Calibrarea care atinge doar cazul fericit e o probă că unealta pornește, nu că vede.

#### Cele trei întrebări de la punctul de decizie 1 (23.08.2026, commit `241acf4`)

**1. „Verificările nu sunt invalidate, ordinea lor este." Ce înseamnă practic?**

**Ordinea NU era doar succesiunea muncii.** Regula scrisă în `TESTE.md` e semantică: *„Clusterul A vine
după B dacă o funcție din A folosește o valoare care APARȚINE lui B"* — adică **verifici întâi
proprietarul valorii, apoi consumatorul**. Un consumator verificat înaintea proprietarului și-a
sprijinit verificarea pe o valoare încă neverificată.

Măsurat pe graful reparat, comparând datele reale de verificare din inventar:

| pe ce dovadă | muchii | în ordine | VIOLĂRI |
|---|---|---|---|
| orice funcție atinsă — regula folosită de gardă azi | 960 | 579 | **381 (40%)** |
| doar funcții cu **proprietar unic** — dovadă tare | 111 | 86 | **25 (23%)** |

**Cifra care contează e 25, nu 381** — restul e R19 de mai jos, nu dezordine reală. **Și 25 e tot un
plafon superior**, dintr-un motiv pe care instrumentul nu-l poate depăși: inventarul ține **ultima**
dată de verificare, nu prima. Un cluster verificat pe 04.08 și „dependența" lui datată 15.08 poate
însemna că dependența a fost **re-verificată** mai târziu, nu că era neverificată atunci.

**Deci: campania NU trebuie refăcută.** Ce merită privit sunt cele ~25 de perechi, dintre care cele
mai clare stau în familia salarizare (*facilitate salariu minim* și *suprataxare part-time*, verificate
pe 31.07 și 02.08, înaintea lui *deducere personala*, verificat pe 06.08). O verificare la sursă a
fiecăreia dintre cele trei ar închide întrebarea, și e muncă de o tură, nu de o campanie.

**2. Cei 83 conțin dependențe false din supra-aproximare?**

**Aproape deloc.** Graful strict — care **taie** orice muchie printr-un nume ambiguu către alt fișier —
dă **81** în loc de 83. Deci **cel mult 2 din 83 pot fi false** (`d390.py::genereaza`,
`declaratii_api.py::_d390`), adică **2%**. Pe alte chei: `tva_standard` 179 → 165 (cel mult 14, 8%);
`impozit_micro` 48 → 48 (**zero**).

**Răspunsul la întrebarea pusă:** cele 12 erau prea puține cu un ordin de mărime; **83 sunt prea multe
cu cel mult 2**. Intervalul onest e **81–83**. Rămâne separată observația de la punctul 3 de mai jos:
37 dintre ele sunt rutare.

**3. `common.py::__init__` — benignă sau pe un drum care contează?**

**Benignă, și se poate arăta de ce.** Cele două definiții sunt constructorii a două clase de excepție:
`PerioadaIndisponibila` (linia 533) și `PlafonCulturalIndisponibil` (linia 555). Nodul păstrat în graf
are **zero cote directe**, **nu e pe drumul niciunei chei** (verificat pe `salariu_minim`), iar în graf
**nicio funcție nu-l cheamă** — `raise Cls(...)` e un apel pe **numele clasei**, nu pe `__init__`. Deci
coliziunea nu poate muta nicio muchie.

#### `clustere_indirect(act)` — unealta nu există (verificat, cerut la punctul de decizie 1)

**Nu s-a folosit între 01 și 23.08, fiindcă nu s-a construit niciodată.** Căutare în `core/` și
`scripts/`: **zero potriviri** pe `clustere_indirect`, `clustere_direct`, `INTEROGARE`. Trăiește doar
ca **descriere** în `TESTE.md` (§282–287), scrisă la forma prezentului, ca și cum ar fi o interogare
disponibilă. **Semnalat ca trimitere la ceva inexistent** (regula D dintre cele cinci permanente).

**Dar întrebarea din spate rămâne validă, și are un răspuns măsurat.** Modificările legislative din
fereastră au fost propagate **de mână**, iar graful reparat poate spune dacă propagarea a fost
completă. Sondaj pe cazul din **16.08.2026** — *„temeiul cotei CAM corectat art.220^1 → art.220^3"*:

- `cam` are, pe graful reparat, **61 de funcții dependente în 10 fișiere**;
- corectarea a ajuns în **`common.py`** (registrul, cu `Temei` structurat și `verificat_la=2026-08-16`)
  și în **`d112.py`**;
- **`salarizare.py` citează încă `art.220^1`** ca temei al cotei CAM, în **trei locuri** (liniile 3,
  153, 369) — iar `salarizare.py` e unul dintre cele 10 fișiere care depind de `cam`.

**Deci propagarea de mână a fost incompletă, și e prima instanță măsurată a clasei.** (`d114.py:5`
citează `art.220^1..220^7` ca **interval de capitol** — acela e corect și nu intră la socoteală.)

**Nereparat acum, cu motivul:** nu atinge pragul 1 nici pe citirea de atingibilitate — cota 2,25% e
corectă, doar articolul citat e greșit, și trăiește în comentarii, nu pe ecran. Intră la **faza 2
(temeiurile)**, care e chiar următoarea în ordinea decisă.


### Ce lipsește ca să se termine E1

1. ~~**1b — ce produce aplicația**~~ — FĂCUT (22.08.2026), pe toate cele patru familii.
2. ~~**1c — se poate verifica pe ecran**~~ — FĂCUT (22.08.2026), interdicțiile 63–66 măsurate.
3. ~~**1d — verdictul**~~ — FĂCUT (22.08.2026). **Faza 1 e completă.** Criteriul de gata NU e
   îndeplinit: lista 3 are 9 artefacte (de construit), lista 5 are 11 (de predat), lista 4 e goală pe
   ce s-a măsurat.
4. **Categoria de mărime**: se poate deriva (probat pe toate 17 firmele), dar nu se calculează
   nicăieri — R3, îngustată.
4. **Vigoarea pentru cele cinci acte structurate pe puncte** (mai sus), care cere altă unitate de
   verificare decât articolul.

## FAZA 4 — INSTRUMENTELE (începută 23.08.2026, pe commit `d26f0c5`)

**Urcată aici prin decizia de la punctul de decizie 1.** Se măsoară cele patru întrebări din plan
(dovada din proză · a rulat pe date nenule · mutația e reproductibilă azi · scrisă înainte sau după
fix), **plus a cincea, adăugată de Costin**: *pe ce instrument stă fiecare gardă, și instrumentul acela
a fost calibrat.*

**Instrument:** `scripts/scan_instrumente.py`, gardat de `core/test_scan_instrumente.py` (5 teste).

**Prima formă a instrumentului era greșită, și o scriu fiindcă e chiar clasa pe care faza 4 o
numără.** Căuta cuvântul „calibrare" în docstring și raporta **`graf_temei` cu ZERO calibrări**, deși
are patru afirmații pozitive și una negativă scrise din 01.08. Adică **instrumentul care numără gărzi
ce-și iau dovada din proză își lua dovada din proză.** Prins pe un caz cunoscut, nu la recitire. Forma
a doua recunoaște calibrarea **structural**, pe AST: o aserțiune al cărei capăt așteptat e un literal
concret pinează un CAZ; una fără literal (`assert rez`) e o proprietate.

**Denominator: 2.230 de funcții de test în 367 de fișiere**, dintre care 2.131 au cel puțin o

**CORECȚIE LA DENOMINATOR, 23.08.2026.** Toate cifrele de mai sus au fost măsurate pe `core/`. Există
**44 de fișiere de test în rădăcina repo-ului, cu 324 de gărzi** — **12,6% din total** — pe care
**niciunul dintre cele două instrumente nu le vede**: `scan_garzi.fisiere_garda` primește `RAD/core`,
iar globul meu era `core/test_*.py`. Denominatorul real e **412 fișiere / 2.563 de gărzi**, nu 368 /
2.239. Cifrele pașilor 1–4 rămân valabile **pe domeniul lor**, care e scris acum; nu se extrapolează.

aserțiune.

### Pasul 1 — pe ce instrument stă fiecare gardă, și e calibrat

**CORECTAT 23.08.2026, în aceeași tură. Prima formă a măsurătorii era greșită pe trei axe**, iar
cifrele pe care le-am raportat din ea — *„6 din 16 instrumente n-au test propriu"*, *„`scan_ancore`
n-a fost niciodată calibrat"* — **erau false**. Le scriu, fiindcă toate trei sunt aceeași familie:
**o formă de suprafață luată drept fapt** — chiar clasa pe care faza 4 o numără.

| forma greșită | ce raporta | de ce era fals |
|---|---|---|
| calibrarea căutată după **cuvântul** „calibrare" în docstring | `graf_temei` cu **0** calibrări | are patru afirmații pozitive și una negativă din 01.08. **Instrumentul care numără gărzi ce-și iau dovada din proză își lua dovada din proză** |
| legătura gardă↔instrument căutată prin **numele fișierului** (`test_<modul>.py`) | `scan_ancore` „fără test propriu" | garda lui există din **21.08** și se numește `core/test_ancore_in_cod.py`, cu clichet de acoperire și cu cele trei cazuri cunoscute scrise în ea |
| „testul **atinge** instrumentul" căutat prin pomenirea numelui de modul | `graf_temei` cu **0** teste | testele lui importă numele **direct** (`from core.graf_temei import depinde_de`) și cheamă `depinde_de(...)` fără prefix |

**Forma de acum e structurală pe AST**: fișierul e legat de instrument dacă **importă** din el (orice
formă, inclusiv `importlib` pe cale); se adună **numele aduse** de acel import; o funcție **atinge**
instrumentul dacă referă vreunul; **calibrează** dacă atinge și pinează un **literal concret**.

**Cifrele corecte:**

| instrument | fișiere-gardă | teste | calib+ | calib− |
|---|---|---|---|---|
| `audit_preluare.py` | 2 | 16 | **31** | **4** |
| `graf_temei.py` | 4 | 9 | 20 | 1 |
| `vigoare_punct.py` | 2 | 11 | 18 | 0 |
| `agenda.py` | 2 | 14 | 5 | 0 |
| `audit_schema.py` | 1 | 11 | 7 | 0 |
| `scan_afirmatii.py` | 2 | 7 | 9 | **3** |
| `scan_ancore.py` | 3 | 3 | 3 | **5** |
| `scan_citate.py` · `scan_respingeri.py` | 1 | 2 | 2 · 1 | 0 |
| `scan_constante.py` | 1 | 2 | **0** | 0 |
| `agenda_drift` · `audit_retentie` · `scan_garzi_culegere` · `scan_garzi_subiect` · `vigoare_articol` | **0** | 0 | 0 | 0 |

**Ce iese, după corecție:**

1. **`scan_ancore` e cel mai bine calibrat NEGATIV din tot inventarul — 5 cazuri care NU trebuie
   găsite.** Exact opusul a ce raportasem. Instrumentul clasei „dovada din proză" e, de fapt, singurul
   care a fost calibrat pe felul în care putea greși: să găsească ceva unde nu e.
2. **`scan_constante.py` are gardă, dar ZERO calibrare pozitivă** — 2 teste, niciunul nu pinează un caz
   concret. E instrumentul clichetului de constante nesursate, deci al unei cifre care se citește
   des (93 în clasa C).
3. **Cinci instrumente n-au nicio gardă**: `agenda_drift`, `audit_retentie`, `scan_garzi_culegere`,
   `scan_garzi_subiect`, `vigoare_articol`. Două sunt ajutoare importate de `scan_garzi`, unul e CLI,
   unul e unealtă periodică declarată în `CLAUDE.md`. **Niciunul nu e cod mort** — verificat.
4. **`scan_garzi.py` însuși — instrumentul interdicțiilor 18 și 19, construit pe 22.08 — e importat
   de un singur fișier: garda scrisă azi.** Instrumentul fazei 4 n-avea, până acum, nicio gardă.
5. **Doar 4 din 12 instrumente cu gărzi au calibrare NEGATIVĂ.** Iar negativa e cea care prinde un
   instrument **prea larg** — adică felul în care s-a orbit un scan pe 22.08, și felul în care mi-au
   greșit azi toate trei formele de mai sus.

**Ce nu vede măsurătoarea, declarat:** „calibrare" înseamnă aici *o aserțiune care pinează un literal
concret*. Un test care pinează un caz prin altă formă — o valoare calculată dintr-o fixtură, un
golden file — **nu se numără**. Deci `calib+` e plafon inferior, iar zero pe `scan_constante` cere
citire, nu concluzie.

### Pasul 2 — câte gărzi pot raporta verde pe zero rânduri (interdicția 19)

**Am construit un al doilea instrument pentru o clasă care avea deja unul, și l-am retras.** Îl scriu
aici fiindcă e chiar interdicția pe care metoda o numește *reparație reală: fără logică paralelă*.

`core/scan_garzi.py` există din **22.08.2026**, construit pentru **exact** interdicțiile 18 și 19, cu
patru sub-instrumente și cu `--calibrare <rev>` ca să poată măsura o revizie din istoric. Măsurătoarea
mea proprie de azi dădea **255 din 2.131**. Confruntate, a lui e mai bine fundamentată pe două axe:

- **restrânge la testele care își CULEG subiectul** (fișiere plimbate, rânduri interogate) — doar
  acolo mulțimea poate fi goală; un test unitar pe intrare construită n-are risc de vid;
- **ține cont de un CONTROL POZITIV în același modul** — atenuare, nu excepție.

**Cifra care rămâne e a lui: 175 vid posibil, din 730 care culeg, din 2.409 gărzi cu aserțiuni**
(163 dintre ele au control pozitiv în modul). Măsurătoarea mea e **retrasă**, iar axa deleagă acum la
instrumentul existent — cu gardă pe delegare, ca logica paralelă să nu reapară.

**Ce arată totuși sub-instrumentele lui, rulate azi:**

| axă | cifra |
|---|---|
| **A** tipare moarte (zero potriviri pe tot corpusul) | **5 din 353** (+26 construite dinamic, neextractibile; 25 cu zero potriviri dar subiect=RULARE) |
| **B** vid posibil | **175 din 730** care culeg |
| **C** gărzi care citesc sursa fără să scoată proza | **14** |
| **D** scrisă odată cu fixul / singură | **329 / 49** |

**ORBIREA COMUNĂ, și e cea care contează.** Niciunul dintre cele două instrumente nu prinde o gardă
care se apără cu `return` devreme — exact **cele două teste de secvență din R18**, care trec pe zero
rânduri de 19 zile. Le-am găsit **de mână**, urmărind altceva. Deci: **instrumentul interdicției 19 nu
prinde cea mai ascuțită instanță a interdicției 19 pe care o avem.** Nu e o cifră greșită, e o cifră
care nu vede o formă — și forma e declarată acum, în ambele locuri.

**Axa D merită citită încet:** **329 de gărzi scrise odată cu fixul, 49 singure.** Regula scrisă e
„gardă înainte de reparație". Planul spune că *dacă majoritatea gărzilor sunt scrise după fix și
totuși prind regresii reale, atunci regula e mai slabă decât credem* — iar 329 din 378 e mai mult
decât majoritate. **Nu concluzionez**: „odată cu fixul" nu e „după fix", iar instrumentul nu distinge
încă între ele. Aia e prima măsurătoare a pasului următor.

### Pasul 3 — gărzi care își iau dovada din proză (interdicția 18)

**Nu s-a construit niciun instrument nou.** Clasa are deja două, complementare, iar întrebarea se
răspunde din ele — lecția zilei fiind exact că un al treilea ar fi fost logică paralelă.

| instrument | ce măsoară | cifra, azi |
|---|---|---|
| `core/scan_ancore.py` (21.08) | ancore de forma `"ȘIR" in <sursă citită>`: șirul există în **cod**, sau doar în comentariu/docstring? | **44 de ancore**: 13 în **cod** · **0 în PROZĂ** · 16 **ambiguu** · 15 **nerezolvat** |
| `core/scan_garzi.py`, axa C (22.08) | gărzi care **deschid un fișier sursă și caută în text fără să scoată proza** | **14** |

**Cele două nu se contrazic — măsoară lucruri diferite**, și amândouă trebuie citite ca să nu iasă un
răspuns fals liniștitor:

- `scan_ancore` spune **zero gărzi ancorate în proză**, dar **poate decide doar pentru 13 din 44**
  (29%). Restul de 31 sunt raportate ca *ambiguu* sau *nerezolvat* — **nu ca trecute**, și asta e o
  onestitate construită în instrument, nu o omisiune: *„absența unei verificări nu e o verificare"*.
  Cifra corectă de citit **nu e „0 în proză"**, ci **„0 din 13 verificabile"**.
- `scan_garzi` axa C spune **14 gărzi citesc sursa fără să scoată proza** — adică sunt **expuse** la
  clasă, chiar dacă ancora lor de azi se întâmplă să fie în cod. Ele sunt suprafața pe care clasa
  poate reapărea la prima editare.

**Ce iese:** clasa **nu are azi nicio instanță dovedită**, dar **acoperirea verificării e 29%**, iar
**14 gărzi stau pe forma care a produs-o de patru ori** în istoric. Nu e „curat"; e „curat pe cât se
vede", iar cât se vede e scris.

**Ce ar închide-o, și e ieftin:** `scan_ancore` are deja clichet de acoperire
(`ACOPERIRE_BASELINE = 12`, ridicat la 13 azi prin măsurătoare). Clasa se închide când clichetul urcă
suficient încât *ambiguu* + *nerezolvat* să scadă sub o cifră declarată — nu când „PROZA" rămâne zero,
fiindcă zero pe 29% acoperire nu e o afirmație despre restul.

### Pasul 4 — scrisă înainte, odată cu, sau după fix (axa D, despicată)

**Planul își pune singur testul de falsificare aici:** *„dacă majoritatea gărzilor sunt scrise după fix
și totuși prind regresii reale, atunci regula «gardă înainte de reparație» e mai slabă decât credem."*
Ca să se poată răspunde, cifra brută a instrumentului — **327 „odată cu fixul" / 49 „singură"** — nu
ajunge: `scan_garzi` își declară singur limita în docstring, *„singură (înainte, SAU pe cod existent)"*.
Amândouă categoriile ascund câte două lucruri.

**Despicat 23.08.2026** (definiții și parametri declarați mai jos):

| categorie | cifra | ce înseamnă |
|---|---|---|
| „odată cu fixul", commit de **REPARAȚIE** | **67** | garda a venit **împreună** cu reparația — regula e respectată |
| „odată cu fixul", commit de **ADUCERE** | **260** | garda a venit împreună cu **cod nou** — regula nici nu se aplică |
| „singură", **după** o reparație a subiectului (≤14 zile) | **18** | **singura categorie suspectă** |
| „singură", fără reparație recentă a subiectului | 13 | gardă pe cod existent |
| „singură", fără modul `core` identificabil | 18 | subiectul nu se poate stabili din importuri |

**Răspunsul la testul planului: NU se confirmă.** Candidate la *„scrisă după fix"*: **18 din 376 —
4,8%**. Majoritatea nu e scrisă după fix, deci ipoteza care ar fi slăbit regula nu ține.

**Dar cifra spune altceva, mai interesant, și n-o trec sub tăcere: 260 din 327 de gărzi au venit cu o
funcționalitate NOUĂ, nu cu o reparație.** Adică modul dominant al populației de gărzi **nu e** „gardă
care apără un fix" — doar **98 din 376** (67 + 18 + 13) au vreo legătură cu o reparație. Regula *„gardă
înainte de reparație"* guvernează **un sfert** din gărzi; restul de trei sferturi sunt acoperire venită
odată cu codul. **Nu e un defect** — dar înseamnă că regula nu poate fi judecată după populația totală,
iar cifra „378 de gărzi" nu e o măsură a disciplinei de reparație.

**Cele 18 suspecte, câteva pe nume:** `test_audit_campuri_oficiale` (după reparația limitei ANAF de 75
de caractere în `d100`) · `test_cai_fisiere_date` (după corectarea unui claim pe `d406`) ·
`test_izolare_structurala` și `test_izolare_incrucisata` (amândouă după un fix pe `auth_api`) ·
`test_d394` (după CORECȚIA #91 pe `common`). Ele **nu sunt greșite** — sunt gărzile care ar fi trebuit
să existe înainte.

**Ce NU măsoară asta, declarat de trei ori fiindcă e ușor de citit greșit:**
1. **Nu există în date legătura „garda X păzește fixul Y".** Se măsoară proximitatea în timp și
   subiectul prin importuri — indiciu, nu identitate.
2. **„Reparație" e un proxy pe mesajul de commit** (`repar`, `fix`, `corect`, `neconformitate`, `bug`,
   `greșit`). Un fix cu mesaj neutru nu se vede.
3. **Fereastra de 14 zile e o alegere**, nu o constantă a lumii. La 7 zile cifra scade, la 30 crește.
   E scrisă ca să poată fi contrazisă.

**Și jumătatea a doua a întrebării din plan rămâne nemăsurată:** *„și totuși prind regresii reale"*.
Dacă o gardă a prins vreodată ceva **nu se poate afla din git** — un test roșu nu lasă urmă în istoric,
doar reparația care i-a urmat, iar aceea nu-l citează. Am verificat deja pe cele 7 gărzi ale grafului:
în 22 de zile, **niciun commit în care să fi picat și să fi cauzat o reparație**. Ca să se poată
răspunde în general, ar trebui ca poarta să **consemneze** ce test a picat — ceea ce azi nu face.

#### Cele trei întrebări de la interdicția 76 (23.08.2026)

**1. „0 din 13 verificabile, din 44" — care e cifra de închidere, și cine o declară?**

**O declar aici, ca să existe un criteriu de oprire.** Clichetul de acoperire al lui `scan_ancore` nu
poate urca la nesfârșit fără țintă, iar „ambiguu + nerezolvat = 0" nu e o țintă atinsă vreodată: 16
sunt funcții care citesc **mai multe surse** (nu se știe care aserțiune se referă la care), 15 au căi
construite dinamic. Ambele forme sunt legitime în cod.

**Criteriul de închidere, scris: zero ancore NEDECLARATE.** Adică fiecare dintre cele 44 e ori
**rezolvată** (13 azi), ori poartă o **declarație scrisă** de ce nu poate fi — o linie lângă gardă,
nu o cifră globală. Clasa se închide când `ambiguu + nerezolvat` **rămân doar cele declarate**, iar
clichetul măsoară atunci **numărul de nedeclarate, care trebuie să fie 0** — nu procentul de acoperire,
care nu are prag natural.

**De ce așa:** un prag procentual („80% acoperire") ar fi o cifră inventată. „Zero nedeclarate" e
verificabil mecanic și nu cere să ghicim cât e destul. Dacă nu ești de acord cu criteriul, el e scris
într-un singur loc și se schimbă într-o linie.

**2. Instrumentele vechi au fost calibrate negativ vreodată?**

**Nu, și mai rău: n-au fost calibrate deloc.** `verificator_conformitate.py` și `verificator_sageti.py`
sunt din **09.07.2026** — cele mai vechi instrumente din proiect. **Niciunul nu e importat de vreun
test.** Zero gărzi, zero calibrare.

**Deci ai avut dreptate: cifra 4 din 12 e despre instrumentele NOI.** Cele vechi n-au fost în domeniul
măsurătorii — iar `verificator_conformitate` rulează la **fiecare poartă**, e citat în fiecare raport
(„verificator: TOTAL 0") și pe el stau gărzi mai vechi decât tot ce am măsurat azi.

**Și clasa era deja scrisă, de 23 de zile.** `core/test_datorie.py:283`, xfail(strict) din 31.07: după
ce verificatorul a produs **13 fals-pozitive prin propriul bug** (regexul de rute rata `async def`),
datoria spune *„instrumentul care MĂSOARĂ conformitatea nu e el însuși măsurat"* și cere fixturi
known-good / known-bad. **Nu s-a făcut.** Interdicția 76 nu deschide clasa — o ridică din datorie în
regulă.

**3. Dintre cele scrise după fix, câte au prins vreodată o regresie reală?**

**Nu se poate afla din istoric, și motivul e în construcția porții — nu în lipsa datelor.**

Căutat în **1.725 de commituri**: doar **4** citează un test și poartă vocabular de reparație, și
**toate patru repară testul însuși** (import greșit, conftest, ordine de import), niciunul nu descrie
o gardă care a prins o regresie în producție.

**Zero nu înseamnă că nu s-a întâmplat.** Poarta rulează **înainte** de commit: un test roșu
**oprește** commitul, omul repară, și ce ajunge în istorie e deja verde. **Prin construcție, o gardă
care prinde o regresie nu lasă urmă.** Istoria conține doar succesele.

**Dovada că clasa nu e goală o am din ziua asta, și e din afara istoricului:** azi, două gărzi au
prins probleme reale și au **blocat poarta** — `test_bifele_nu_stau_pe_o_baza_schimbata` (a prins
conflatarea grafului, sărind 14 → 35) și `test_verificarile_A_nu_sunt_in_urma_codului` (a prins o bifă
rămasă în urma codului, și a cerut reverificarea la sursă, care s-a făcut). **Niciuna dintre cele două
nu apare nicăieri în git.**

**Deci întrebarea are răspuns doar dacă poarta consemnează ce test a picat.** Azi nu o face. Asta e o
observație, nu o propunere — hook-ul e al lui Costin.

### Pasul 5 — mutația care probează garda e reproductibilă azi?

**Măsurat pe domeniul COMPLET: 409 fișiere, 2.563 de gărzi** — inclusiv cele 44 din rădăcină, pe care
pașii 1–4 le-au ratat.

O gardă se dovedește printr-un RED-proof: strici codul, garda se aprinde. Întrebarea planului nu e
*dacă s-a făcut*, ci **dacă se mai poate face azi** — adică dacă dovada mai există, sau a rămas o
afirmație despre trecut. Nu se pot rula 2.563 de mutații; dar există o formă în care mutația e
reproductibilă **prin construcție**: garda are un **tovarăș în suită**, un al doilea test care
construiește intrarea stricată și arată că mecanismul o prinde. Acela nu e o afirmație despre trecut —
**e o mutație care rulează la fiecare poartă.**

**Măsurat pe două definiții, și confruntate** (o singură definiție ar fi fost o opinie):

| definiție | cifra | ce prinde |
|---|---|---|
| **convenție** — tovarășul se numește `_prinde_` / `_detectează_` / `_respinge_` | **41, în 32 de fișiere — 1,6%** | doar tovarășii **numiți** ca atare |
| **structural** — test cu intrare construită local, care cheamă același ajutor ca alt test din fișier | 720, în 212 fișiere — 28,1% | și tovarășii nenumiți, **dar și teste unitare obișnuite** care împart un ajutor |

**Diferență de 17,6×** — deci cea largă **nu se poate raporta**: e un plafon superior contaminat.
**Cifra care se raportează e cea strictă: 41 din 2.563, adică 1,6%.**

**Calibrarea trece:** cele trei cazuri cunoscute de tovarăși reali — `test_secventa_prinde_inversiune`,
`test_fisiere_coloana_completa_prinde_gol`, `test_garzi_si_duplicat_prind_defectul` — sunt **toate
găsite** de definiția strictă.

**Ce înseamnă: pentru 98,4% dintre gărzi, mutația nu trăiește în suită.** Dacă RED-proof-ul s-a făcut,
el există într-un docstring sau într-un mesaj de commit — adică **o afirmație despre trecut, pe care
nimeni n-o mai poate rula**. **377 din 409 fișiere n-au niciun tovarăș.**

**Instanța de azi, ca să nu pară o cifră despre alții:** am făcut **două** RED-proof-uri pe garda
fluturașului — revenirea la rândul unic (4 roșii) și o componentă fără rând (alte 4). Amândouă au
funcționat, amândouă sunt scrise în mesajul de commit, și **niciuna nu se poate reproduce de altcineva
fără să refacă mutația de mână.** Garda mea e printre cele 98,4%.

**Ce NU spune măsurătoarea:** că mutația celorlalte **nu** s-ar mai reproduce — n-am rulat-o. Spune
doar că **nu e mecanizată**, deci nu se poate ști fără să o refaci. Distincția e chiar cea dintre „s-a
verificat" și „se verifică".

### Faza 4 — ce a ieșit, întreg

| pas | cifra | limita declarată |
|---|---|---|
| 1 · instrument ↔ calibrare | **4 din 12** instrumente cu gărzi au calibrare **negativă**; cele două cele mai vechi (09.07) n-au **nicio** gardă | „calibrare" = aserțiune care pinează un literal; fixturile nu se numără |
| 2 · verde pe zero rânduri | **175 din 730** care culeg | nu prinde gărzile care se apără cu `return` devreme — exact **R18** |
| 3 · dovada din proză | **0 instanțe dovedite, pe 29% acoperire**; 14 gărzi expuse la clasă | „0 în proză" e o afirmație despre 13 din 44 |
| 4 · înainte / odată cu / după fix | **18 din 376 — 4,8%** scrise după fix; testul de falsificare al planului **nu se confirmă** | „reparație" e proxy pe mesajul de commit; fereastra de 14 zile e o alegere |
| 5 · mutația reproductibilă | **41 din 2.563 — 1,6%** au mutația în suită | nu s-a testat dacă restul s-ar reproduce, doar că nu e mecanizat |

**Rezultatul fazei, într-o propoziție:** instrumentele nu mint pe cifrele lor, dar **aproape niciunul
nu e apărat de propriul mod de eșec** — 4 din 12 au calibrare negativă, 1,6% dintre gărzi își au
mutația în suită, iar cele mai vechi două instrumente n-au fost verificate niciodată. **De aceea
interdicția 76**, și de aceea faza a urcat prima.

**Ce a scos faza, dincolo de cifre:** patru instanțe ale interdicției 76 într-o zi, toate la
instrumente scrise de mine · două restanțe noi (**R18**, **R19**) · o corecție de denominator de 12,6%
· și confirmarea că testul de falsificare al planului nu ține, deci regula „gardă înainte de reparație"
rămâne — dar guvernează **un sfert** din gărzi, nu toate.


## 1 — O valoare fiscală scrisă în afara registrului

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `25b07c0`
- **cifra**: **131 — INVALIDATĂ 23.08.2026** (vezi tabelul cifrelor invalidate). Era: **131** brut, din care ~23% zgomot pe eșantionul de 30 → **~100 reale** *(cifra brută e de pe 22.08, `ffbcb74`, pe domeniul VECHI al celuilalt instrument — nu s-a re-măsurat)*. Confruntare cu al doilea instrument, **re-măsurată 23.08 după calibrarea negativă a lui `scan_constante`**: clasa **C urcă de la 93 la 104**, **A de la 48 la 60**, **E de la 33 la 37**, fiindcă domeniul scanului s-a lărgit de la o listă de nume la *„nume fiscal SAU modulul citează legea"* — patru module care construiesc `Temei` erau invizibile. **Datoria n-a crescut, a devenit vizibilă.** Diferența de definiție rămâne: clasa A e tot în afara registrului, fiindcă un `Temei` lângă o valoare nu e registrul. **Descompunerea veche (131 = A+C+E−43) NU se mai poate reface**: termenii ei sunt pe două domenii diferite, iar a-i scădea ar fi exact greșeala pe care registrul a mai făcut-o o dată (cifra *162 fără amprentă*, la 52).
- **instanțe**: concentrate în `salarizare.py` 33 · `d212_engine.py` 13 · `d394.py` 9 · `d101.py` 8 · `d406.py` 7 · `d406_active.py` 7 · `d300.py` 5 · `d300_reconciliere.py` 5 · `d403.py` 5 · `d104.py` 4 · `scadente.py` 4 · `tva_marja_turism.py` 4 · restul câte 1–3, în 16 fișiere. Lista completă: `./venv/bin/python -m core.scan_constante`.
- **calibrare**: GĂSIT — cotele TVA scrise ca literal în `d300.py:41-42`, `d394.py:69`, `cote_tva.py:19`; CAS 0.25 în `salarizare.py:497` și `salariati_api.py:497`. Caz negativ NEraportat: valorile din `common.py` (43) au fost excluse corect — acolo E locul lor.
- **ce nu vede**: o valoare construită din altele (`sm * 3`) apare doar dacă un operand e literal · o valoare citită din baza de date (parametru per firmă) · o valoare ascunsă într-un șir formatat („cota 21%") · testele, scanurile și migrările (excluse deliberat). Zgomot identificat pe eșantion: numere de act citite ca valori (`158` din OUG 158/2005), constante de precizie (`0.0001`), coduri interne.
- **unde ajunge efectul**: un adevăr scris în două locuri produce două răspunsuri la aceeași întrebare; divergența apare pe cifra dată contabilului sau declarată la ANAF


## 2 — O interogare a registrului fără dată

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-22
- **pe commit**: `ffbcb74`
- **cifra**: **3** apeluri fără dată, din 45 (42 corecte). **O CAUZĂ UNICĂ**: `common.cota(nume, la_data=None)` — defaultul e *azi*. Interdicția 2 e posibilă doar fiindcă interdicția 14 e prezentă în punctul de intrare al registrului; scos defaultul, devine imposibilă prin construcție.
- **instanțe**: `core/salariati_api.py:129` `cota('tichet_masa_plafon')` · `main.py:4528` `cota('tva_standard')` · `main.py:4529` `cota('tva_redusa')`.
- **calibrare**: GĂSIT — toate trei confirmate la sursă, cu semnătura `cota(nume, la_data=None, strict=True)` citită direct. Caz negativ NEraportat: cele 42 de apeluri cu dată (poziţională sau `la_data=`) n-au intrat în listă.
- **ce nu vede**: un apel prin variabilă (`f = cota; f(...)`) · un apel prin `getattr` · o interogare a registrului printr-o altă funcție decât `cota()`.
- **unde ajunge efectul**: o valoare citită pe data de azi face ca recalcularea unei perioade trecute să dea alt rezultat decât prima calculare — adeverințe și rectificative devin nereproductibile


## 3 — Un calcul fiscal care citește data curentă

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: un calcul care citește ceasul nu mai e o funcție de aceleași intrări: aceeași lună, recalculată în două zile diferite, dă două rezultate. Spre deosebire de 2, defectul e ÎN motor, deci nu se repară scoțând un default din registru

## 4 — O regulă fiscală implementată în stratul de prezentare

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-24
- **pe commit**: `e325f7c`
- **cifra**: **3 locuri** în stratul de prezentare calculează TVA, și **toate trei afișează cifra**: `emitere_ecran.js:300` (totalul facturii în lucru) · `facturi_ecran.js:432` (defalcarea pe cote din detaliul facturii) · `declaratii.js:447` (previzualizarea D301, cu textul *«se stochează»*). Din 15.125 de rânduri de JS, doar acestea combină un nume fiscal cu o cotă literală
- **instanțe**: **una dintre ele producea o cifră GREȘITĂ, dovedit cu numere.** Serverul rotunjește **pe linie** (`Decimal.quantize`, ROUND_HALF_UP), iar ecranul aduna în `float` și rotunjea o singură dată, la afișare. Pe o factură obișnuită de **50 de rânduri × 3 × 19,99 la 21%**: serverul salvează **629,50**, ecranul arăta **629,69** — **19 bani** pe care contabilul îi vedea și factura nu-i avea. Pe 20 de rânduri mici: **+9 bani**. **REPARAT în aceeași tură** (rotunjire pe linie, ca la server), fiindcă o cifră greșită arătată unui om e prag 1 — criteriul lui Costin, aplicat consecvent cu R22 și R26. `declaratii.js` **nu s-a atins**: rotunjește la leu întreg, iar D301 stochează întregi — de verificat separat, nu de presupus
- **calibrare**: cazul cunoscut **GĂSIT**, și e chiar reparația: forma veche a aritmeticii e păstrată în gardă (`_ecran_vechi`) ca să se poată proba că datele de test **chiar despart** cele două aritmetici (`METODA` §15). **Plus calibrarea DETECTORULUI, măsurată prin relaxarea fiecărui filtru pe rând — interdicția 76 aplicată instrumentului, nu doar reparației:**

  | filtrul relaxat | candidate | ce aduce în plus |
  |---|---|---|
  | *(bază)* | **3** | cele trei formule |
  | fără cerința de **cotă literală** | 34 | **+30, niciuna formulă** — toate sunt text afișat (etichete, opțiuni, ajutoare). Dar scoate o **clasă nouă**, vezi mai jos |
  | fără cerința de **nume fiscal** | 11 | +7, aritmetică generică pe procente |
  | fără **limita de lungime** | 3 | **zero** |
  | inclusiv fișierele **`.html`** | 3 | **zero** — nu există formule în `<script>` inline |

  **Ce a scos relaxarea, și n-ar fi apărut altfel:** `rip_ecran.js:148–150` scrie cotele ca **text în etichetă** — *«CAS (25%)»*, *«CASS (10%)»*, *«Impozit (10%)»* — lângă valori care vin **calculate de la server** (`d.cas.cas`). Nu e o formulă și nu produce o cifră greșită azi (toate trei se potrivesc cu registrul: `cas` 0,25 CF art.138 · `cass` 0,10 CF art.156 · `impozit_venit` 0,10 CF art.78). Dar e aceeași clasă structurală: **la o schimbare de cotă, cifra vine corectă de la server și eticheta de lângă ea minte.** Prag 3, structură — consemnat, nu reparat.

  **Și un fals pozitiv al meu, numit:** tiparul de cotă include `121` (pentru suta mărită 21/121) și prinde din întâmplare **codul de obligație 121** din `declaratii.js:512`. Filtrul pe numărul de ghilimele îl elimină — deci cifra 3 e curată, dar filtrul acela **nu e o regulă fiscală, e o euristică**, și ar putea ascunde o formulă scrisă într-un șablon.
- **ce nu vede**: **măsurat, nu presupus** (vezi tabelul de la calibrare): lungimea liniei și fișierele `.html` **nu ascund nimic** — relaxate, adaugă zero. Ce ascunde cu adevărat cerința de **cotă literală** nu sunt formule, ci **cote scrise ca text**. Rămân neacoperite: o regulă fiscală **fără nicio cifră** (un prag, o condiție de scutire exprimată doar prin nume), o formulă întinsă pe **mai multe rânduri**, și una scrisă într-un **șablon** cu multe ghilimele — pe care filtrul euristic o taie. Iar gardul **nu scoate regula din prezentare**: oprește divergența, nu duplicarea. Cifra **3** e un **plafon inferior**
- **unde ajunge efectul**: o regulă fiscală ajunsă în interfață nu e nici testată, nici gardată, nici versionată pe dată: pragul din ecran rămâne la valoarea de anul trecut mult după ce registrul s-a actualizat, iar nimeni nu se uită acolo
- **CALIBRARE A DOUA, 24.08.2026 — pe întrebarea lui Costin: «vede o formulă scrisă pe nume neutre — `a`, `val`, `x`?»** Relaxarea F2 de ieri dăduse **+7**, dar le **numărasem**, nu le **citisem** — iar o cifră necitită nu e un răspuns. Rulat acum pe toate cele **42** de fișiere `.js`, cu comentariile **și** șirurile scoase (o formulă e cod, nu text afișat), împărțit în două: cu nume fiscal pe linie **1**, fără nume fiscal **2**. **Cele 2 sunt aritmetică pe date calendaristice** — `api.js:288` (`slice(0, 10)` peste o potrivire de dată) și `facturi_ecran.js:388` (`Date.now() + 30 * 864e5`). **Zero formule fiscale scrise pe nume neutre.** Deci lacuna numită ieri **există ca posibilitate, dar nu are instanță** — și acum se știe, nu se presupune.
- **BUG PROPRIU, prins la prima rulare a acestei calibrări.** Funcția care taie comentariile **colapsa liniile**, deci numerele de linie raportate erau ale **altor** linii — instrumentul ar fi trimis un om la locul greșit. Reparat (newline-urile se păstrează) și **prins de o aserțiune anti-derapaj** care cere ca sursa curățată să aibă exact același număr de linii ca originalul. *Interdicția 76 pe instrumentul care măsura interdicția 76.*
- **ȘI CE A SCOS, deși nu asta căuta:** `firme.js:1649/1660/1738` — cota de TVA scrisă de **trei ori** ca valoare implicită în ecranul de NIR. Vezi **R29**: e prag 1, și e chiar clasa pe care R26 o declarase golită.
- **CE FACE `recalc()` CU VALOAREA — întrebat de Costin 24.08.2026, măsurat: SE AFIȘEAZĂ ȘI SE PIERDE.** `baza`, `tva`, `total` sunt **variabile locale**; singurul lor efect e `innerHTML` pe `#em-total`. Nu ating modelul `linii`, nu intră în niciun câmp. Iar corpul trimis la `/facturi/emite` poartă **doar** `descriere · cantitate · pret_unitar · cota_tva · articol_id` — **niciun total**. Serverul îi calculează singur și îi întoarce (`{ok, factura_id, numar, serie, total, tva}`). **Deci divergența reparată pe 23.08 n-a atins niciodată evidența** — a fost, tot timpul, o cifră pe ecran.
- **Și verificat pe DATE, nu doar pe cod** (24.08.2026, `SELECT` curat, fără apel de API): **41 de facturi** pe **12 firme** din 17. TVA-ul stocat pe fiecare, recalculat din linii cu rotunjire pe linie: **38 se potrivesc la bani**. Cele **3** care nu — seria `COER`, descrierea *«coerenta R3»* — sunt **puse de seeder** (`date_test/seed/transa2_coerenta_tva.py`), nu emise prin ecran: antetul lor a fost scris direct, iar liniile separat. Vezi **R32**.

## 5 — Un strat care cheamă în sus sau ocolește un nivel

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — se verifică mecanic **o singură direcție** din două, iar cealaltă e numită mai jos
- **măsurat la**: 2026-08-23
- **pe commit**: `60a7b15`
- **cifra**: **107 muchii de import în `static/js/`**, clasificate pe straturi: **46 ecran → infrastructură** (în jos, normal) · **7 infrastructură → ecran**, toate din `app.js` și `navigator.js`, adică **routerul**, care prin definiție cunoaște ecranele — nu e o încălcare · **47 ecran → ecran** (lateral) · 7 infra → infra. **Zero încălcări dovedite pe verticală.** Pe partea Python: **0** module din `core/` importă din stratul de prezentare — cele trei potriviri sunt **comentarii**, iar una dintre ele (`pdf_util.py`) declară deschis o duplicare: *«Python al bani()/dataRo() din static/js/api.js: o singură regulă, două limbaje»*
- **instanțe**: **niciuna pe verticală. Dar cele 47 de muchii laterale nu se pot împărți mecanic** în compunere legitimă și cuplare încrucișată: `admin.js → admin_analytics.js` e un ecran care își compune panourile; `termene.js → firme.js` și `capacitate.js → asistenti.js` sunt altceva — un panou care cheamă un ecran întreg. **Diferența cere un nivel declarat pe fișier, care nu există.** Iar interdicția 4, măsurată azi, e aceeași clasă pe alt drum: regula fiscală a ajuns în prezentare nu printr-un import, ci prin **rescriere** — trei formule de TVA scrise a doua oară în JS, care nu apar în niciun graf de importuri
- **calibrare**: **nu are, și de-aia rămâne PARȚIAL.** Cifra 0 pe verticală e credibilă doar dacă scanul chiar ar vedea o încălcare — și asta nu s-a probat pe un caz construit. *Prima formă a acestei secțiuni, scrisă azi, afirma că «JS-ul n-are `import`, deci graful nu există de măsurat». **Fals: are 107 muchii.** Am scris-o înainte s-o verific, iar verificarea rulată alături a contrazis-o în aceeași tură — a șaptea instanță a lui `METODA` §16 și singura prinsă înainte de a intra în poartă*
- **ce nu vede**: **ce anume rămâne neverificabil, exact** — răspunsul la întrebarea pusă: (a) **duplicarea prin rescriere**, nu prin import — un ecran care recalculează o regulă n-are nicio muchie (măsurat: 3 cazuri la interdicția 4); (b) **apelul în sus prin HTTP** — JS-ul cheamă rute, iar un ecran care ocolește un nivel chemând direct o rută de nivel jos nu apare în importuri; (c) **împărțirea celor 47 de muchii laterale** în compunere și cuplare, care cere un **nivel declarat pe fișier**. Deci nu e adevărat că mecanica «cheamă în sus prin natura ei»: pe importuri se vede, și e curată. Ce nu se vede sunt celelalte două drumuri. Cifra 0 e un **plafon inferior**
- **unde ajunge efectul**: dependența care curge în ambele sensuri face ca un nivel să nu mai poată garanta nimic: ce apără stratul de jos se poate ocoli de sus, iar o schimbare într-un strat cere atinse toate celelalte — exact ce face imposibilă livrarea în 48 de ore

## 6 — O cerere de citire care modifică date de business

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **0 rute GET care scriu în starea de business, din 172** de rute `@app.get` în `main.py`. O singură excepție, și e **mecanică pe numele tabelei**, nu o listă de rute: `public.audit_log` — jurnalul de acces GDPR, care trebuie să existe **tocmai** fiindcă e un GET
- **instanțe**: **niciuna azi.** Instanța care a produs gardul e reparată și se numește, fiindcă e cea mai instructivă: `GET /tenants/{id}/stat-plata` chema un helper cu `INSERT ... ON CONFLICT DO UPDATE` + `commit()` și lăsase **24 de rânduri** în `stat_plata` la auditul tenant_001 — de unde media pe 6 luni a indemnizației de concediu medical depindea de ce luni deschisese cineva în interfață (**409,09 lei/zi pe 2 luni vs 425,06 pe cele 6 reale**, salariat 55)
- **calibrare**: cazul cunoscut **găsit**: mutația care repune apelul la `_snapshot_stat_plata` într-un GET (din copia de backup a lui `main.py`) face gardul roșu **și numește ruta**. Nu e o calibrare pe nume: mutația e chiar defectul istoric
- **ce nu vede**: analizează `main.py` — deci o scriere al cărei text SQL trăiește în alt modul se vede doar dacă apelul e urmăribil de acolo. Cifra **0** e un **plafon inferior** al defectelor existente, nu o dovadă că niciun GET din aplicație nu scrie
- **unde ajunge efectul**: o citire care scrie transformă orice privire în modificare: un raport deschis de două ori lasă evidența altfel decât a găsit-o, iar o sondă de audit devine ea însăși sursa datelor pe care le măsoară

## 7 — Un document emis care se rescrie

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: un document dat unui om care se rescrie sau nu se poate corecta printr-un al doilea exemplar rupe legătura dintre ce s-a predat și ce arată aplicația
- **transferul retrospectiv 3a (2026-08-23)**: **rămâne NEÎNCEPUTĂ, și se spune de ce.** `PLAN_INVESTIGATII.md` §3a o dădea ca măsurată («statul append-only»), dar căutarea în `GARZI.md` și `TESTE.md` n-a găsit **nicio cifră pe domeniu** — doar proză despre instanțe și un modul de migrare (`core/migrare_declaratii_depuse_versiune.py`). Regula transferului spune: *ce nu se reconstituie onest rămâne NEÎNCEPUTĂ*. Nu se inventează o cifră ca să scadă contorul

## 8 — O schemă care interzice al doilea exemplar

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o schemă care interzice al doilea exemplar face corecția imposibilă: eroarea dintr-un document deja predat nu se mai poate îndrepta printr-un document nou, deci singura ieșire rămâne rescrierea celui vechi — adică interdicția 7, forțată de structură
- **transferul retrospectiv 3a (2026-08-23)**: **rămâne NEÎNCEPUTĂ.** Nota din §3a («`UNIQUE` ridicat») descrie o **reparație**, nu o măsurătoare: nu există nicăieri o numărătoare a constrângerilor care ar interzice al doilea exemplar, pe niciun domeniu. Un `UNIQUE` ridicat undeva nu spune câte au mai rămas

## 9 — O afirmație fără domeniu sau fără surse

- **stare**: PARȚIAL
- **felul limitei**: ORBIRE — scanul recunoaște afirmațiile după **tipar sintactic**, iar tiparele pe care nu le recunoaște nu lasă urmă — nu se poate spune ce ratează
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **80 de afirmații găsite, din care 4 tipate.** În domeniul interdicției — clasele `A_verdict` și `C_import` — **14 netipate, în 10 fișiere** (`raportari_ai.py` 3 · `articole_import_api.py` 2 · `main.py` 2 · alte șapte cu câte una)
- **instanțe**: cele 14. Netipate înseamnă: afirmația e un șir, deci **nu poartă nici domeniul, nici sursele** ca atribute — se poate cita corect și rămâne fără domeniu
- **calibrare**: `core/afirmatii.py` + `core/test_afirmatii_tipate.py` țin clasa tipată; scanul e `core/scan_afirmatii.py`. **Calibrare pe propriul mod de eșec: nu are** — de aceea starea e PARȚIAL, nu MĂSURATĂ, conform regulii de transfer din §3a
- **ce nu vede**: scanul recunoaște afirmațiile după tipar sintactic, pe patru clase; o afirmație scrisă altfel nu intră în numărătoare. Cifra e un **plafon inferior**: 14 e cât s-a văzut, nu cât există
- **unde ajunge efectul**: o afirmație fără domeniu se citește peste șase luni ca adevăr permanent

## 10 — Un verdict favorabil care coexistă cu necunoscut nedeclarat

- **stare**: PARȚIAL
- **felul limitei**: ORBIRE — măsoară **precondiția** (verdictul e obiect), nu interdicția; un verdict tipat care tace despre necunoscut n-ar fi văzut de nimic
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **9 afirmații de clasa `A_verdict` netipate**, din cele 80 găsite — un verdict netipat nu poate purta câmpul «ce n-a fost verificat», deci coexistența cu necunoscutul nu se poate nici declara, nici verifica
- **instanțe**: cele 9
- **calibrare**: **nu are calibrare proprie** — scanul măsoară *tiparea*, nu *coexistența cu necunoscutul nedeclarat*. E cel mai slab dintre cele transferate azi, și se scrie ca atare
- **ce nu vede**: măsoară o **precondiție** a interdicției (verdictul e obiect, deci poate purta necunoscutul), nu interdicția însăși. Un verdict tipat care **tace** despre necunoscut ar trece neobservat. Cifra e un **plafon inferior**
- **unde ajunge efectul**: un verdict favorabil care ascunde necunoscutul îl face pe contabil să creadă că e verificat ce n-a fost verificat

## 11 — Un verificator care importă modulul verificat

- **stare**: PARȚIAL
- **felul limitei**: ORBIRE — nu s-a probat că un `test_non_tautologie` ar deveni roșu dacă a doua cale ar începe să importe prima — deci nu se știe dacă gardul ar prinde chiar defectul lui
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **9 din 9** module de reconciliere («a doua cale») au fiecare câte un `test_non_tautologie_*`: d100, d101, d112, d205, d300, d301, d390, d394, d406
- **instanțe**: **niciuna pe reconcilieri.** Instanța istorică, reparată, e în antetul modulelor: a doua cale n-are voie să împartă sursa cu prima
- **calibrare**: gardul e per-modul și e viu în suită. **Calibrare pe propriul mod de eșec: neverificată** — nu s-a probat că un `test_non_tautologie` ar deveni roșu dacă a doua cale ar începe să importe prima
- **ce nu vede**: acoperă **doar reconcilierile de declarație**. Verificatoarele care nu sunt reconcilieri (verificator de conformitate, gărzile de registru) nu sunt în domeniu. Cifra 9/9 e un **plafon inferior** al acoperirii reale: e completă pe o formă declarată, nu pe toți verificatorii
- **unde ajunge efectul**: o a doua cale care copiază prima nu mai verifică nimic — confirmă greșeala în loc s-o prindă

## 12 — O modificare simultană verificator/verificat fără decizie scrisă

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: cele două căi se aliniază de aceeași mână, în același commit, iar divergența dispare fără să fi fost explicată. Instanță reală: pe 06.08 calea a doua a fost aliniată la prima, și semnalul care contrazicea podeaua part-time a tăcut două săptămâni
- **transferul retrospectiv 3a (2026-08-23)**: **rămâne NEÎNCEPUTĂ.** Instanța din 06.08 e consemnată în «unde ajunge efectul» și e reală, dar **o instanță nu e o cifră**: nu există nicăieri o numărătoare a commiturilor care ating simultan verificatorul și verificatul. Ar fi măsurabilă mecanic din git — și tocmai de asta n-o declar transferată: măsurătoarea nu s-a făcut

## 13 — Un refuz cu nume interne sau fără diacritice

- **stare**: PARȚIAL
- **felul limitei**: ORBIRE — semnalul e `snake_case`; un nume intern **fără underscore** (`codO`, `denO`) e invizibil, și nimic nu măsoară cât de des apare forma asta
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **274 de mesaje în 31 de fișiere** expun nume interne de câmp, sub clichet **per-fișier** (`core/test_mesaje_generare_fara_camp_intern.py`, `_BASELINE`). Niciun fișier nu poate crește; un fișier nou intră cu 0. `d301` e deja pe 0, reparat
- **instanțe**: cele 274, fiecare cu fișierul ei în clichet
- **calibrare**: clichetul e viu și pică pe creștere. **Calibrarea pe propriul mod de eșec — dacă semnalul ratează un nume intern — nu s-a făcut**, deci PARȚIAL
- **ce nu vede**: semnalul e un **token `snake_case` într-un șir de mesaj**, în funcțiile de validare ale generatoarelor. Un nume intern **fără underscore** (`codO`, `denO`, `Data_A`) nu se vede prin acest semnal, iar mesajele din afara generatoarelor sunt în alt gard. Cifra 274 e un **plafon inferior**
- **unde ajunge efectul**: contabilul primește un refuz pe care nu-l poate acționa: un nume intern nu-i spune ce să completeze, iar mesajul arată ca un defect al aplicației. Efectul nu e o cifră greșită, e o cerere de ajutor către noi pentru ceva ce el putea rezolva singur

## 14 — Un parametru cu valoare implicită într-o funcție de calcul fiscal

- **stare**: PARȚIAL
- **felul limitei**: ORBIRE — numără **forma** (`=None` în semnătură), nu **efectul**; nu există instrument care să spună câți apelanți chiar omit parametrul
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **43 constante fiscale ca DEFAULT DE PARAMETRU**, în **27 de module** *(a treia recifrare a zilei — vezi mai jos; era 19 în 15 module, pe domeniul de dinaintea celei de-a patra reguli)*, dintre care **25 sunt cota de TVA 21** — dintre care **10 sunt cota de TVA 21** (`import_export`, `lichidare`, `perisabilitati`, `stocuri`, `taxare_inversa`, `tva_marja` ×2, `tva_marja_turism` ×3), 2 sunt cota forfetară de 8% a agricultorilor, iar restul impozitul pe dobândă de 10%, remunerația minimă și altele. **RECIFRATĂ 23.08.2026, a doua oară în aceeași zi, și motivul contează:** cifra transferată dimineața — *129 de definiții cu cel puțin un parametru `=None`* — măsura **forma**, nu clasa. Era **prea largă** (mai toate `=None` sunt legitime: forțează apelantul să dea valoarea) și **prea îngustă** (rata exact defaultul periculos — cel cu **valoare**, care furnizează tăcut o cotă greșită). Cifra nouă vine din `scan_constante`, casa **H3**, pe domeniul lărgit. *Cele 19 se numără **și** la interdicția 1 (valoare fiscală în afara registrului): sunt două interdicții despre aceleași instanțe, nu o dublare.*
- **instanțe**: nedesfăcute pe instanțe: numărătoarea e pe **definiții**, nu pe parametri, și nu separă defaultul legitim de cel care ascunde o cale netestată
- **calibrare**: **nu are.** Măsurătoarea veche din §3a — *25 din 78 de parametri cu default `None` care n-au fost NICIODATĂ `None`* (`GARZI.md`) — are **alt domeniu și alt criteriu**, deci nu se poate compara cu 129 și **nu s-a transferat ca atare**. Cele două cifre nu se adună și nu se scad
- **ce nu vede**: numără forma (`=None` în semnătură), nu efectul (dacă apelantul chiar omite parametrul). Cifra e un **plafon inferior** al defectelor și un **plafon superior** al gravității: multe dintre cele 129 sunt defaults legitimi
- **unde ajunge efectul**: un default ascunde o cale netestată: apelantul care uită parametrul primește tăcut valoarea comodă, iar defectul nu se vede la apel, ci mult mai târziu, în cifra rezultată. E cauza interdicției 2, dar și a oricărei alte valori implicite din motor — de trei ori într-o singură zi

## 15 — Reguli diferite la previzualizare față de salvare

- **stare**: PARȚIAL
- **felul limitei**: ORBIRE — nu există scan al clasei — cele trei instanțe au venit din audituri de tenant, deci a patra ar fi invizibilă până la următorul audit
- **măsurat la**: 2026-08-22
- **pe commit**: `1eaecbb`
- **cifra**: **3 instanțe cunoscute, toate REPARATE** — găsite incidental, la audituri de tenant, nu de un instrument. **Cifra e un plafon inferior**, nu un total: nu s-a rulat niciun scan al clasei.
- **instanțe**: (1) **checksum VIES la introducerea D301** (19.08, audit 006/R24.1) — codul `DE 811234567` era acceptat tăcut la introducere și respins abia de DUK; calea derivată din d301 nu trecea prin `_facturi_ic`. Reparat, gardat de `test_d301_vies_la_introducere`. (2) **indicatorul patru-ochi** (20.08) — `aproba` folosea `activ ∧ posibil`, iar `GET /eu/patru-ochi` întorcea doar flagul brut, deci UI-ul decidea pe altă definiție. Reparat prin sursă unică `coada_api.patru_ochi_stare`. (3) **divergență front↔back** pe aceeași familie (`DECIZII.md:9747`). Toate trei sunt consemnate în `GARZI.md` / `ISTORIC.md` / `ISTORIC_TENANTI.md` — **și niciuna nu ajunsese în secțiunea asta**, care spunea „nemăsurată, niciun caz".
- **calibrare**: nu s-a rulat un instrument, deci nu există calibrare în sensul metodei. Cele trei au apărut la audituri de tenant; **de aceea starea e PARȚIAL, nu MĂSURATĂ**, iar cifra e plafon inferior.
- **ce nu vede**: nu există scan al clasei — o a patra instanță ar fi invizibilă până la următorul audit de tenant. Clasa generală („instanțe reparate care nu ajung în secțiunea interdicției lor") e transferul retrospectiv din faza **3a**
- **unde ajunge efectul**: o regulă fiscală în stratul de prezentare se rescrie separat de motor: previzualizarea și salvarea ajung să spună lucruri diferite

## 16 — Un nomenclator derivat dintr-o sursă secundară

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-22
- **pe commit**: `ffbcb74`
- **cifra**: **39** nomenclatoare ancorate pe sursă secundară, din 93 la nivel de modul (39 SECUNDAR · 39 NECITAT · 15 NORMATIV).
- **instanțe**: `d390.TARI_UE`/`TIPURI` · `d301.VALUTE` · `d394.TIPURI`/`TIP_COTA_ZERO`/`OP1_CU_TVA`/`JUDETE_SIRUTA`/`_TARI_UE`/`_TARI_NONUE`/`CODPR_CEREALE` · `d402._STATE_UE` · `d406.UOM_UNECE`/`MISCARI_STOC`/`METODE_PLATA_ANAF`/`TAB_VALORI`/`_UE_NON_RO` · `d120.ACCIZE_FIELDS`/`_HEADER_OPT` · `d101._COD_OBLIGATIE_D101`/`_NENEG_D101` · `d300._TIP_COD` · `d307._TIP_VALIDE` · `d311._INTRARE` · `d390_reconciliere._TARI_UE`/`_EMISA_TIPURI` · `d600._SUM_KEYS` · `duk.CHEIE_DUK` · `salarizare._CM_COD_NEIMPOZABIL` · `salariati_import_api.JUDETE_CASA` · restul până la 39, listabile cu scanul de nomenclatoare.
- **calibrare**: GĂSIT — `d390.TIPURI`/`TARI_UE` clasificate SECUNDAR, cu proza lor citată verbatim („nomenclatoare confirmate pe VALIDATORUL instalat D390_11 ... nu doar pe pdf-ul de structură 2020"). Caz negativ NEraportat: cele 15 NORMATIVE (care citează OPANAF/OUG/CF art.) n-au intrat în listă.
- **ce nu vede**: un nomenclator construit la rulare (citit din fișier sau din DB) · o sursă citată la trei funcții distanță de declarație (proza se citește doar din blocul de deasupra + docstringul modulului) · nomenclatoarele din JavaScript (`CM_CODURI` din `flux_concediu.js` nu e în domeniu).
- **unde ajunge efectul**: **DECIS 22.08 (Costin): nu e o tensiune cu P8, e o distincție care lipsea din plan.** Nomenclatorul se ia din sursa NORMATIVĂ; dacă validatorul acceptă altceva sau mai puțin, aia e o **constrângere a arbitrului**, nu o sursă alternativă — și se declară ca interpretare cu dezacord marcat. Cazul D390 e chiar exemplul: XSD-ul are 15 coduri, Nomenclatorul 9 are 20, iar validatorul acceptă coduri pe care XSD-ul le respinge. **Deci cele 39 nu sunt nici datorie curată, nici aplicare corectă a lui P8: sunt nomenclatoare ancorate pe locul greșit, cu o constrângere reală deasupra.** Efectul concret, deja vizibil: un D112 cu cod de boală legal (16/17/51) era blocat de o validare ancorată pe enumerarea XSD `01..15`.

  **REPARAT 22.08.2026** (excepția din PLAN_INVESTIGATII: un defect care produce cifre greșite azi se repară pe loc). Arbitrul întrebat direct, pe declarație generată: **`D_9=91` → DUK VALID**, deși codul nu e în enumerarea XSD; `D_9=51` → `S101.1` și `D_9=17` → `S97`, adică reguli de **fond** pe cod, deci coduri cunoscute. Documentul de structură ANAF cere `Nomenclator 9 – cod 01-17` plus regulile explicite pe 51/91/92. Deci enumerarea XSD e mai îngustă decât **validatorul însuși**. Sursa a devenit `core/nomenclator_cm.py` (20 de coduri, fiecare cu temeiul lui); `d112` întreabă nomenclatorul, iar fallback-ul pe intervalul GHICIT `1..15` a dispărut — când XSD-ul nu se poate citi, răspunsul e „nu știu", nu un interval inventat. XSD-ul rămâne citit ca **a doua constrângere**, vizibilă, prin `nomenclator_cm.doar_in_xsd()`. Gardat de `core/test_cod_boala_nomenclator.py`, care probează **poarta folosită de generator** (`d112._cod_boala_acceptat`), nu doar nomenclatorul — altfel `d112` ar fi putut păstra o a doua logică, paralelă


## 17 — Un adevăr din registru, re-declarat în alt modul

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-22
- **pe commit**: `ffbcb74`
- **cifra**: **17a — 42** valori de registru rescrise ca literal, în 16 fișiere (~18% zgomot → ~34 reale). **17b — 1** formulă repetată, în **3 module**.
- **instanțe**: **17a**: `d406.py` 6 · `d300.py` 5 · `d300_reconciliere.py` 5 · `d394.py` 5 · `tva_marja_turism.py` 4 · `d101.py` 3 · `cote_tva.py` 2 · `salarizare.py` 2 · `tva_agricultori.py` 2 · `tva_marja.py` 2 · restul câte 1. **17b**: podeaua part-time `sm − facilitate` în `d112.py:690`, `d112_reconciliere.py:195` și `:217`, `salarizare.py:309`. **Instanță nouă, 22.08.2026, de alt fel decât cele 42 de mai sus:** nu o VALOARE re-declarată, ci un **ÎNȚELES** — starea `de_preluat` a unei facturi e definită în două module cu conținut opus. `core/d300.py:50` o clasează ca **staging** și o exclude din decont; `core/export_winmentor.py:17` scrie *„'de_preluat' e starea NORMALĂ a facturii emise, nu una de exclus"*; iar `core/facturi_api.py:311` **creează facturile noi exact în starea asta**. Măsurat: **4 facturi emise, la 3 plătitori de TVA, cu 3.052,00 lei TVA colectată, nu intră în D300**. **Potrivirea cu interdicția 17 e imperfectă și o declar** — 17 vorbește despre un adevăr *din registru*, iar înțelesul unei stări nu e în registru; cel mai apropiat vecin e 30 („două stări distincte cu aceeași etichetă"), care e oglinda cazului. Instanța stă aici fiindcă mecanismul e același — **un adevăr scris în două locuri produce două răspunsuri** — iar reparația e la **pragul 1, poziția 1.1**.
- **calibrare**: GĂSIT — podeaua part-time, exact în trei module, prin semnătură STRUCTURALĂ a expresiei (`SM Sub FAC`), nu prin potrivire de text: `sm - fac` și `sm - facilitate_val` sunt aceeași formulă. Caz negativ NEraportat: nicio altă formulă pe valori de registru nu apare în ≥2 module — deci semnătura nu se aprinde pe orice scădere.
- **ce nu vede**: o valoare re-declarată cu altă reprezentare (`21/100` scris ca operație) · o formulă rescrisă algebric (`-(fac - sm)`) · o valoare care ajunge în cod prin baza de date. **Prima formă a măsurătorii 17a a dat 1167 — 90% zgomot**, fiindcă discriminatorul „literal egal cu o valoare de registru" e prea slab: orice `10` se potrivea cu CASS 10%, orice `9` cu TVA 9%. Refăcută pe detectorul de context deja calibrat din `scan_constante`, în loc de al doilea detector inventat.
- **unde ajunge efectul**: un adevăr scris în două locuri produce două răspunsuri la aceeași întrebare. **Instanță reală, nu ipotetică**: între 06 și 20.08.2026 podeaua part-time a avut două valori, iar fluturașul și D112 au declarat sume diferite pentru același salariat (70,25 lei/lună)


## 18 — O gardă care își ia dovada din proză

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-24
- **pe commit**: `ad504f8`
- **cifra**: **DOUĂ CLASE, nu două cifre pentru același lucru** (24.08.2026, `core/scan_garzi_pe_text.py`). ① **ÎNGUSTĂ** — *gărzi care își iau dovada din **documentația codului***: **13** (14 minus una exclusă prin natura ei), măsurat ad-hoc la faza 4 pe 22.08, pe 369 de fișiere-gardă. Cifra aia **n-a lăsat niciun instrument în urmă** și nu se poate recalcula: azi sunt 397 de fișiere. ② **LARGĂ** — *orice aserțiune care poate trece **dintr-un motiv străin***: **369 de aserțiuni**, în **111 fișiere**, din 1339 de forme `"șir" in X` găsite. **Clasa largă n-a fost măsurată până azi.** Ea se desface în trei, numărate separat fiindcă nu sunt același defect: **sursa 113** (se caută în codul păzit — nu deosebește *implementat* de *descris*) · **randare 6** (se caută în HTML — un `<div>` dintr-un comentariu trece la fel) · **reprezentare 250** (`"x" in str(d)` — *arată ca apartenență la o cheie și e sub-șir pe reprezentare*; cea mai insidioasă, și cea mai mare). **369 e PLAFON INFERIOR**: 899 de aserțiuni (67%) rămân `nedeterminat` — nu s-a putut rezolva ce stă în dreapta lui `in` — și **nu** se raportează ca trecute. Clichetul e **pe fișier**, în `core/clichet_garzi_pe_text.json`, fiindcă un plafon global pe fișiere nu constrânge nimic înăuntru: un fișier nou cu 40 de aserțiuni ar urca numărul cu unu. Un fișier nou pornește de la **zero**.
- **instanțe**: poate ascunde o gaură — `test_golden_xsd.py:47` caută `from core import <mod>` în textul testelor, deci un docstring care pomenește modulul face un test inexistent să pară prezent (exact clasa care a lăsat d402 fără nicio probă). Pot doar raporta în plus — `test_upsert_motivat.py:25` (`"DO UPDATE"` dintr-un comentariu), `test_harta_ecrane.py:29` (`fa-*` dintr-un comentariu devine ecran fantomă). Neprivite: `test_gard_masca_zero`, `test_masti`, `test_mesaje_valueerror_publicat`, `test_nomenclatoare_ancorate`, `test_reconciliere_vie`, `test_refuz_generator_422`, `verificator_conformitate` și încă 3.
- **calibrare**: GĂSIT, în ambele direcții. Pozitiv: `test_schema_coloane.py` la revizia `5d46d4f` (înainte de reparație) e raportat; pe HEAD, unde folosește `scan_ancore.domenii_docstring`, **nu mai e**. Negativ NEraportat: `test_proprietate_coaja.py`, care are propriul `_fara_comentarii()` — recunoscut mecanic, pe arbore (o operație peste un marcaj de comentariu), nu după numele funcției. **Prima formă a instrumentului a RATAT cazul canonic**: scutea orice modul care folosea `tokenize` sau `ast.parse`. Amândouă sunt scutiri false — tokenizarea *colectează* string-urile (docstringul e un token de string), iar `ast.parse` lasă docstringurile ca noduri `Constant`. Chiar asta era natura bug-ului lui `test_schema_coloane`. Lista de scutiri prea largă orbește la fel de bine ca un tipar mort.
- **ce nu vede**: o gardă care își ia dovada din proză prin altă poartă decât citirea unui fișier sursă — dintr-un `.md`, dintr-un răspuns HTTP, din baza de date · o gardă care citește sursă printr-un ajutor din alt modul · **direcția**: instrumentul spune că proza AJUNGE la comparație, nu că a schimbat vreodată un verdict. Ca să știi dacă ascunde sau raportează în plus, trebuie citită — de-aia cifra e însoțită de „3 privite din 13".
- **unde ajunge efectul**: o gardă care nu se poate încălca decât în aparență lasă clasa deschisă și dă încredere falsă. Instanțe reale, toate din 20–21.08: TEMA D se aprindea pe propria explicație · `lit.` se aprindea pe „po-LIT-e)" · `test_schema_coloane` a inventat coloane numite `document`, `aplicația` dintr-un docstring · gardul de clasificare a prozei s-a aprins pe propriul meu comentariu. Instrumentul din `core/scan_garzi.py` (sub-instrumentul C) reproduce cifra


> **CELE DOUĂ CLASE NU SUNT DISJUNCTE (24.08.2026, `081c4e7`).** O aserțiune pe text e permisivă
> în **două direcții simultan**: trece **pe proză** (motiv străin — clasa asta) *și* trece **pe listă
> goală** (interdicția **19**). Nu sunt două defecte care se întâmplă să coexiste, sunt aceeași
> slăbiciune văzută din două părți: *aserțiunea nu-și verifică propria premisă*.
>
> **Măsurat: 221 din 1339** de aserțiuni (**17%**) trăiesc într-un context care **dispare pe
> iterabil gol** — `all(… for x in L)` sau corpul unui `for x in L:` — deci trec și fără să compare
> nimic.
>
> **Unde stau contează mai mult decât cifra.** Doar **18** sunt în clasa clasificată (369); **202
> sunt în `nedeterminat`**. Rata e **5% în clasă** față de **22% în nedeterminat** — de peste patru
> ori mai mare. *Deci `nedeterminat` nu e un rest neutru: e exact locul unde se adună cele mai slabe
> aserțiuni.*
>
> **Și e aceeași gaură, nu două.** Într-un `all("x" in l for l in lista)`, dreapta lui `in` e
> **variabila de buclă** — pe care clasificatorul o dă `nedeterminat`. Deci tocmai formele vacue
> ieșeau din clasă **înainte** de a putea fi numărate. Prima măsurătoare de azi a raportat **18**
> fiindcă filtra pe clasă înainte de a verifica vacuitatea; a fost prinsă de **propria calibrare
> pozitivă**, care cerea ca un `all(...)` peste o listă filtrată să fie recunoscut și nu era.
> Vacuitatea se măsoară acum peste **toate** aserțiunile, fiindcă e ortogonală pe categorie.
>
> **Rămâne PLAFON INFERIOR**: o listă golită de un `parametrize`, de un filtru care nu potrivește
> nimic, sau de o fixtură care întoarce `[]` nu se vede structural de aici.
>
> **ȘI E O PROPRIETATE, NU UN PROCENT.** *O aserțiune pe text trece pe date goale — cu excepția
> celor care caută un **mesaj de eroare**, adică ceva ce apare **doar când ceva merge prost**. Restul
> caută ceva ce apare **oricum**.* Nu e o observație despre un eșantion, e o proprietate a formei:
> `"X" in ceva` întreabă *există X undeva*, nu *s-a întâmplat ce trebuia*. Măsurat cu direcția erorii
> scrisă (`fel_ancorei`): **119 din 1341 (8,9%)** ancorează pe un semn de rău, **1222** pe ceva ce
> apare oricum — iar clasificatorul supraevaluează semnul de rău, deci **119 e plafon SUPERIOR** și
> **1222 plafon INFERIOR**.
>
> **Consecința pentru următoarea măsurătoare pe 18**: nu are voie să presupună disjuncția. Un
> instrument care numără „gărzi pe proză" și unul care numără „gărzi pe zero rânduri" raportează, în
> parte, **aceleași aserțiuni** — iar adunarea celor două cifre ar supraestima, în timp ce tratarea
> lor ca alternative exclusive ar ascunde exact instanțele cele mai slabe: cele care cad în amândouă.

## 19 — O gardă care raportează favorabil pe zero rânduri

- **stare**: MĂSURATĂ (două forme, măsurate cu instrumente diferite)
- **măsurat la**: 2026-08-22
- **pe commit**: `84f77c4`
- **cifra**: **19a — 3** tipare care nu pot potrivi nimic, din 339 extrase. **19b — 157** teste care CULEG și n-au nicio aserțiune de existență, din 696 care culeg (din 2072 cu aserțiuni); dintre ele **145 au un control pozitiv în modul** (atenuare), deci **12 n-au nici în test, nici în modul**. Zgomot măsurat pe 29 de rezultate privite: ~1/3 înainte de ultima corecție a instrumentului, adus la aproape zero prin recunoașterea aserțiunilor care fixează o valoare concretă.
- **instanțe**: **19a** — `test_garzi_tacere_ui.py:47`, `test_import_motiv_vizibil.py:27`, `verificator_conformitate.py:996`. Toate trei sunt de forma `assert not <găsite>`: zero potriviri poate însemna „lumea e curată" SAU „tiparul e orb", iar instrumentul nu le desparte. **19b, cele 12 fără nicio atenuare** — `test_cui_cnp_test_valid:36` · `test_d112_mesaje_afisate:10` · `test_declarant_warn:14` · `test_fixturi_shared_period:18` · `test_garzi_mesaje_afisabile:25` · `test_ghiduri_servite:14` · `test_golden_xsd:33` · `test_harta_ecrane:33` și `:40` · `test_import_mesaje_afisate:15` · `test_rotunjire_fiscala:24` · `test_rute_model_body:19`. **Cinci dintre ele sunt gărzi pe care le-am construit eu în campaniile din 19–21.08** — nu e o observație despre codul moștenit.
- **calibrare**: GĂSIT, ambele. **19a** — gardul R4 cu octetul `0x08` în regex (`test_temei_termene.py:29`, `\x08(OUG|OG|Legea|...)`) apare la revizia `29bd752` și **dispare** pe HEAD, unde a fost reparat. **19b** — `test_verificarea_nu_scrie_nimic`, care număra pe o lună fără nicio contradicție: nu există ca revizie (a fost reparat în același commit cu introducerea), deci a fost **RECONSTRUIT** din forma descrisă în GARZI.md; apare la reconstruire (158) și nu apare pe HEAD (157), iar diferența e exact testul numit. Caz negativ NEraportat: cele 25 de tipare cu zero potriviri al căror subiect e un artefact produs la RULARE — corpusul nu poate spune nimic despre ele, deci instrumentul tace.
- **ce nu vede**: **19a** — tiparele construite dinamic (24, f-string sau concatenare) nu se pot extrage · un tipar mort *față de subiectul lui* dar care potrivește altundeva în repo nu e prins (implicația merge într-o singură direcție, cea sigură) · nimic despre tiparele aplicate pe artefacte de rulare. **19b** — o mulțime culeasă poate fi goală **la rulare** fără ca instrumentul s-o știe: el citește forma aserțiunii, nu execuția. Cifra e un **plafon inferior** pentru „ar trece pe o lume goală" și un plafon superior pentru „chiar trece". Iar controlul de modul e o atenuare, nu o dovadă — a fost mai întâi o EXCEPȚIE tăcută în instrument, și chiar ea a înghițit cazul de calibrare.
- **suprapunere cu 18 și cu §23, măsurată 24.08.2026**: **221 de aserțiuni** din cele 1339 măsurate la interdicția 18 (`core/scan_garzi_pe_text.vacue()`) sunt **și** instanțe de 19 — din care doar 18 în clasa clasificată și **202 în `nedeterminat`**, adică 22% acolo față de 5% în clasă — trăiesc într-un `all(… for x in L)` sau în corpul unui `for`, deci trec pe iterabil gol. **Nu sunt numărate în 19a/19b**, fiindcă instrumentele de acolo caută altceva: tipare moarte și teste fără aserțiune de existență. Deci cifrele lui 19 sunt **plafoane inferioare**, iar clasele **nu sunt disjuncte**.
- **unde ajunge efectul**: o gardă care raportează favorabil pe zero rânduri e datorie eternă indistinctibilă de datorie reală — nu poate deveni verde prin reparație, fiindcă e deja verde. Instanțe reale: gardul R4 a stat verde pe un regex care nu putea potrivi niciodată, iar `verificarea nu scrie` ar fi trecut și dacă verificarea emitea singură corecții. Reproducerea cifrelor: `./venv/bin/python -m core.scan_garzi`


## 20 — O declarație de perimetru devenită neadevărată

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — regiunea lăsată afară e **numită**: compută din `MODEL_AUDIT_TENANT.md`, deci vede perimetrul declarat, nu lumea. Gardul are caz de calibrare găsit
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **4 fațete din 9** sunt declarate neacoperite — §5 calculat = **{F3, F4, F5, F7}**, computat din `MODEL_AUDIT_TENANT.md` de `core/test_perimetru_calculat.py`, nu scris de mână
- **instanțe**: cele 4 fațete. Ce face gardul imposibil: ca §5 să rămână gol când o fațetă își pierde acoperirea
- **calibrare**: cazul cunoscut **găsit**: gardul cere ca fiecare fațetă marcată GARDAT să numească fișiere care **există** (`test_gardat_numeste_fisiere_care_exista`), iar §5 e pinat pe baseline — o fațetă care își pierde tăcut gardul mută §5 și pică
- **ce nu vede**: compută din **model**, deci vede perimetrul declarat, nu lumea: o zonă care nu e nici măcar o fațetă în `MODEL_AUDIT_TENANT.md` rămâne invizibilă. Cifra 4/9 e un **plafon inferior** al neacoperirii reale
- **unde ajunge efectul**: un perimetru neadevărat face ca o zonă neacoperită să pară acoperită

## 21 — O interpretare care apare ca și cum ar fi text de lege

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — regiunea e numită: **alegerile care nu iau forma unei comparații** (codificări, ordine de aplicare, rotunjiri). Calibrare găsită, cu caz negativ neraportat
- **măsurat la**: 2026-08-23
- **pe commit**: `2fe86ae`
- **cifra**: **15** candidate (egalități stricte pe o valoare de registru), din care **4 confirmate** la citire pe context — **erau 2, iar cele două noi vin din reluarea lui R8** (`d406.py:1436` și `:1465`, alegerea codului de taxă pe `cota == 0`). Cifra rămâne **plafon inferior**: `d223.py:159` e încă necitit la sursă. Raport: 56 de inegalități pe aceleași valori, care de regulă sunt chiar textul legii („nu depășește").
- **instanțe**: confirmate — `salarizare.py:221` `vbt == sm` și `d112_reconciliere.py:207` `brut == sm` (aceeași interpretare, în două module: și interdicția 17). Ambele **marcate** acum cu `# interpretare: incadrat_la_minim`. Re-deschise, nerezolvate: `d223.py:159` (regula „100% doar cu un singur asociat" — în lege sau citirea noastră?), `d406.py:1338` și `:1367` (alegerea codului fiscal `300101` pentru cota zero e o mapare aleasă). Zgomot sigur: `cota == cota.to_integral_value()` ×4 (formatare), `cota == 0` ×2, `prag == 0/1` (stare internă), `k[0] == tp` (cheie de dicționar).
- **calibrare**: GĂSIT — `vbt == sm` din `salarizare.py`, cazul din anexa planului. Caz negativ NEraportat: cele 56 de inegalități n-au intrat în listă, deci discriminatorul chiar deosebește `==` de `<=`.
- **ce nu vede**: alegerile care NU iau forma unei comparații — codificarea trimestrială `09`, ordinea de aplicare a scăzămintelor, felul de rotunjire, alegerea unui default. Niciuna n-ar apărea vreodată. **Cifra e un plafon inferior, nu un total.** Și: prima citire a celor 15 a fost la nivel de LINIE; pe context, trei dintre cele numite zgomot merită a doua privire — corectat aici.
- **unde ajunge efectul**: o alegere de-a noastră care poartă marcajul legii devine imposibil de repus în discuție. Instanță reală: egalitatea strictă la salariul minim costă salariatul ~82 lei la un leu peste minim, iar alegerea a trăit doi ani într-o comparație


## 22 — O interpretare fără variantele posibile enumerate

- **stare**: NEMĂSURABILĂ
- **măsurat la**: 2026-08-22
- **pe commit**: `ffbcb74`
- **cifra**: — și **nu se cere una**. Motivul, decis împreună cu Costin pe 22.08: măsurătoarea **nu are numitor**. O interpretare nemarcată e indistinguibilă de un calcul obișnuit; se poate număra ce poartă un marcaj, dar nu ce n-a fost recunoscut niciodată ca alegere. Orice cifră ar însemna „cele găsite de cine a căutat", nu „câte sunt".
- **instanțe**: cele **2** declarate în `core/registru_interpretari.py` (`incadrat_la_minim`, `podea_part_time_minus_facilitate`) au variantele enumerate, deci nu încalcă. Câte NU sunt declarate rămâne necunoscut prin construcție.
- **calibrare**: GĂSIT (pe direcția pozitivă) — `salarizare.py:305` enumeră explicit „Alternativa A", deci o interpretare cu variante *poate* fi recunoscută în proză. Caz negativ NEraportat: niciun număr, fiindcă niciun număr nu e apărabil aici.
- **ce nu vede**: totul, în afară de ce poartă marcaj. **Nu e o slăbiciune a instrumentului, e forma problemei.**
- **unde ajunge efectul**: o decizie fără varianta respinsă numită nu se mai poate contesta: peste un an nu se știe între ce s-a ales, deci revizuirea deliberată din P24 n-are pe ce lucra, iar o interpretare greșită supraviețuiește ca fapt. **Ce s-a făcut în loc de a măsura** — `core/interpretare.py` face interpretarea DECLARABILĂ, cu variantele obligatorii (minim două: „dacă nu poți numi cealaltă variantă, legea nu lăsa loc"), iar `core/test_comparatii_clasificate.py` închide clasa **NECLASIFICAT** — nu clasa *greșit clasificat*


## 23 — Un dezacord cu arbitrul, stins prin aliniere fără decizie

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — regiunea e numită și declarată în docstringul gardului: **alinierea tăcută**, care nu lasă amprentă textuală. Ambele colțuri ale gardului sunt exercitate
- **măsurat la**: 2026-08-22
- **pe commit**: `ffbcb74`
- **cifra**: **0** instanțe curente. Gardat de `core/test_cale_a_doua.py` din 20.08, care trece.
- **instanțe**: niciuna activă. Instanța istorică — 06.08.2026, podeaua part-time schimbată în `d112.py` **și în același commit** în `d112_reconciliere.py`, cu motivul scris pe linie „Aliniat cu d112.pull prag_pt" — e citată în cod cu marcajul `istoric-aliniere-ok:`, ca să nu se piardă istoricul fără să reaprindă gardul.
- **calibrare**: GĂSIT — gardul are două colțuri, ambele exercitate: (1) fără limbaj de aliniere în modulele de verificare, zero admis; (2) co-modificarea `X.py` + `X_reconciliere.py` cere `DECIZII.md` schimbat în aceeași tură. Caz negativ NEraportat: co-modificarea legitimă (o schimbare de lege chiar cere ambele căi) NU e interzisă — doar cere motivul scris.
- **ce nu vede**: **o aliniere TĂCUTĂ** — schimbi formula fără s-o spui — nu lasă amprentă textuală. Gardul își declară singur limita în docstring. Colțul 2 e plasa, iar arbitrul rămâne judecătorul final. **Cifra 0 e un plafon inferior**: zero pe forma scrisă, necunoscut pe forma tăcută.
- **unde ajunge efectul**: alegerea tăcută între lege și validator ajunge direct în cifra depusă, iar dezacordul dispare din vedere: nu se mai știe că a existat, deci nimeni nu-l mai poate decide. Instanță reală: podeaua part-time, aleasă în cod contra structurii publicate, cu raționamentul scris într-un comentariu


## 24 — O interogare fără contextul firmei

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: datele unei firme ajung la altcineva

## 25 — Un drept verificat numai în interfață

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: ecranul ascunde scurgerea, nu o oprește: interogarea întoarce în continuare datele, iar orice altă poartă spre ea — API, export, raport — le dă mai departe. Un drept verificat doar în interfață se pierde exact acolo unde nu există interfață

## 26 — O decizie luată comparând sau clasificând text

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — regiunea e numită: închide clasa **NECLASIFICAT**, nu clasa *greșit clasificat*. Are aserțiune anti-orbire proprie (cel puțin 10 comparații văzute)
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **13 comparații neclasificate** pe valori de registru, sub clichet în ambele direcții (`core/test_comparatii_clasificate.py`, `BASELINE_NECLASIFICATE`) — nu poate crește, și nu poate scădea fără să cobori clichetul conștient
- **instanțe**: cele 13
- **calibrare**: cazul cunoscut **găsit**, și e chiar aserțiunea anti-orbire: gardul cere să vadă **cel puțin 10** comparații (*«doar %d comparații văzute — detectorul a orbit, nu codul s-a curățat»*) și cere ca `core/salarizare.py` să fie printre fișierele văzute. Un detector care orbește pică
- **ce nu vede**: închide clasa **NECLASIFICAT**, nu clasa *greșit clasificat* — o comparație clasificată prost trece. Și acoperă comparațiile pe **valori de registru**, nu orice decizie luată pe text. Cifra 13 e un **plafon inferior**
- **unde ajunge efectul**: o decizie luată pe text se rupe la prima reformulare, tăcut

## 27 — Un verdict stocat ca frază, nu ca structură

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: un verdict ținut ca frază nu se poate interoga, agrega sau contrazice: se citește ca adevăr, iar remediul nu se poate deriva din el. Când starea se schimbă, fraza rămâne — și afirmă fals despre firmă

## 28 — O denumire de nomenclator oficial scrisă ca literal în cod

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată; **o instanță cunoscută nu e o cifră** — a intrat prin citire, nu prin scan, deci nu spune nimic despre mărimea clasei)
- **instanțe**: **una cunoscută, ÎN LISTA DE REPARAT, nereparată deliberat** — `static/js/ecrane/flux_concediu.js:6`, `CM_CODURI`: 18 coduri de indemnizație cu etichetele scrise de mână, în timp ce sursa e `core/nomenclator_cm.py` (20 de coduri, fiecare cu temeiul lui). **Decizia lui Costin, 22.08.2026: lista se ia din `nomenclator_cm.optiuni()`.** Divergența e deja reală, nu doar duplicare: ecranul NU oferă `11` (trecere temporară în altă muncă), `91` și `92` (situații speciale de îngrijire), pe care nomenclatorul le are cu temei. Consecința pentru reparație, de dus la decizie odată cu ea: etichetele din JS poartă și procentele („01 — Boală obișnuită (55/65/75%)"), iar `nomenclator_cm` le ține deliberat afară, fiindcă procentele au altă sursă (OUG 158/2005) și altă dată de valabilitate. Deci `optiuni()` singur schimbă ce vede contabilul pe ecran.
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat; instanța de mai sus nu ține loc de calibrare — a fost adusă de o citire, nu găsită de un instrument)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele. Când se construiește, domeniul lui trebuie să cuprindă **JavaScript-ul**: e chiar punctul orb declarat la interdicția 16, iar singura instanță cunoscută a clasei trăiește acolo)
- **unde ajunge efectul**: o denumire oficială scrisă ca literal se rupe tăcut de sursă — și nu doar la reformulare, ci și la **completare**: nomenclatorul crește cu un cod, iar ecranul rămâne cu lista veche. Instanța confirmă forma: trei coduri legale nu se pot alege din interfață, deși aplicația le acceptă

  **DECIS 22.08.2026 (Costin), CUM se repară:** procentele **rămân pe ecran**, dar nu scrise de mână — sunt o valoare fiscală cu temei (**OUG 158/2005 art. 17**, modificat de Legea 141/2025; verificat la sursă: ÎN VIGOARE, alin. (1) modificat la 01-08-2025), deci intră sub **interdicția 1** la fel ca orice cotă. **Eticheta se compune la randare:** denumirea din nomenclator, procentul din registru, **pe data certificatului**. Niciuna dintre cele două nu se scrie în JS. Vezi `DECIZII.md` D3 pentru ordinea reparației. Rămâne NEREPARAT în tura asta

## 29 — O frază fixă de interfață fără cheie și loc unic

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — regiunea lăsată afară e **numită și probată**: etichetele de un singur cuvânt, frazele prin concatenare, textul din `.html`. Fiecare are un caz în calibrare
- **măsurat la**: 2026-08-23
- **pe commit**: `9af74be`
- **cifra**: **1.785 de fraze de interfață** în `static/js/` (37 de fișiere, 15.125 de rânduri), din care **143 apar în MAI MULTE LOCURI** — adică fără «loc unic». Vârfurile: *«Se încarcă…»* în **26** de locuri · *«Eroare la salvare.»* în **22** · *«Cotă TVA %»* în **12**. Cifra e un **plafon inferior**: nu vede etichetele de un cuvânt, nici frazele concatenate, nici textul din `.html`
- **instanțe**: cele 143. Cea mai instructivă nu e cea mai frecventă: *«Se încarcă...»* (cu trei puncte) și *«Se încarcă…»* (cu puncte de suspensie) sunt **două fraze pentru scan și una singură pentru om** — 26 de locuri într-o formă, 14 în cealaltă. Exact efectul scris la interdicție: *se schimbă într-un loc și rămâne veche în celelalte*
- **calibrare**: **GĂSITĂ, și scrisă ÎNAINTE de prima măsurătoare** — prima dată când interdicția 76 se aplică înainte, nu după. Cele șase moduri de eșec ale unui scan care citește JavaScript sunt enumerate în antetul instrumentului, iar fiecare are un caz în `core/test_scan_js_texte.py` (**17 teste**): backtick cu `${}` normalizat · comentariu care nu se numără · **`//` dintr-un șir care NU începe un comentariu** (cazul pe care un regex îl greșește pe orice URL) · ghilimele dintr-un comentariu care nu deschid un șir · zgomotul (selectoare, clase, chei, markup) · anti-vacuu pe numărul de fraze și de fișiere. **Prima formă a euristicii a fost prea largă** — lăsa să treacă fragmente de markup — și s-a strâns **înainte** de a raporta cifra, nu după
- **ce nu vede**: **trei moduri NEACOPERITE, fiecare probat printr-un test, nu doar declarat**: (a) fraza construită prin **concatenare** — scanul vede bucata, nu fraza; (b) eticheta de **un singur cuvânt**, fiindcă euristica cere un spațiu; (c) textul din **`.html`**, în afara domeniului, deci o duplicare reală poate fi raportată drept «loc unic». Cifra e un **plafon inferior**. *Un mod de eșec declarat și demonstrat e o limită; unul declarat și nedemonstrat e o speranță.*
- **unde ajunge efectul**: aceeași frază se schimbă într-un loc și rămâne veche în celelalte: două ecrane spun altceva despre aceeași stare, iar contabilul nu poate ști care e cel actualizat

## 30 — Două stări distincte cu aceeași etichetă

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: contabilul nu mai poate deosebi „nu s-a verificat" de „e în regulă", fiindcă ambele arată la fel. E P6 mutat pe ecran: eticheta comună face necunoscutul să se citească drept favorabil

## 31 — O etichetă aleasă de cine randează, nu derivată din stare

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: eticheta poate contrazice starea, și o face tăcut. Instanțe reale: „Vector necompletat" pe firme cu vectorul complet, „Patru-ochi e dezactivat" pe o politică doar suspendată — ecranul a afirmat fals despre datele firmei

## 32 — O poziție de declarație care nu se poate desface până la document

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — regiunea e numită: nu urmărește lanțul de la înregistrare spre poziția din declarație. Calibrare găsită, pozitiv și negativ
- **măsurat la**: 2026-08-24
- **pe commit**: `bf16f32`
- **cifra**: **19 din 33 de note contabile** nu au nicio legătură către documentul care le justifică. Măsurat **un nivel mai jos decât spune interdicția** — pe înregistrare, nu pe poziția din declarație — fiindcă acolo se rupe lanțul întâi: o poziție nu se poate desface până la document dacă nici înregistrarea din spatele ei nu poate. **Cifra e un plafon inferior**: nu s-a măsurat câte poziții de declarație sunt afectate, ci câte note nu pot fi desfăcute.
- **instanțe**: pe toți cei șase tenanți cu note (t003, t005, t013, t014, t016, t017): `document_ref` populat **0 din 33** · `numar` **1 din 33** (doar `AMORT-2026-08`) · `factura_id` **14 din 33**. Coloana `inregistrari.document_ref` **există și nu o scrie nimeni**: singurele apariții în cod sunt o CITIRE în `core/control_incrucisat.py:491` (caută `document_ref = 'SAL LL/AAAA'`, o valoare pe care n-o produce nimic) și `core/registratura_api.py`, care lucrează pe altă tabelă.
- **calibrare**: GĂSIT — cazul pozitiv e nota de amortizare de pe t013 (`id=30`, `numar=AMORT-2026-08`), singura cu identificator propriu; cazul negativ NEraportat sunt cele 14 note cu `factura_id`, care **au** legătură și n-au intrat în cifră.
- **ce nu vede**: nu urmărește lanțul mai departe, de la înregistrare spre poziția din declarație și înapoi · nu spune dacă o notă **trebuie** să aibă document justificativ extern (amortizarea, de pildă, e o notă internă legitimă) — deci o parte din cele 19 pot fi corecte; de aceea cifra e plafon inferior și pentru datorie, nu doar pentru acoperire
- **unde ajunge efectul**: o cifră declarată care nu se poate desface până la document nu se poate apăra la control

> **RELUAT 24.08.2026 (pragul 3, poziția 2), pe commit `0a96ebf`** — de data asta pe **consumatorul**
> coloanei, nu pe date. Măsurătoarea de pe 22.08 spunea *„`document_ref` există și nu o scrie
> nimeni"*. Întrebarea care n-a fost pusă atunci: **ce face codul care o citește?**
>
> **1. Scriitori: 0 din 48.** Toate cele 48 de căi de `INSERT INTO …inregistrari` folosesc exact trei
> forme — `(data, descriere, sursa, status)` ×38, `(data, factura_id, …)` ×6, `(data, numar, …)` ×4.
> **Niciuna nu atinge `document_ref`.** Singurii care scriu numele coloanei în tot codul sunt
> `core/registratura_api.py` (**altă tabelă**) și `core/salarii_contare.document_ref(an, luna)`, care
> doar **compune** șirul `"SAL LL/AAAA"` — și e el însuși nelegat (R33).
>
> **2. Cititorul, și ce iese din el.** `core/control_incrucisat.py:483`, `note_salarii_ciorna()`,
> filtrează `… AND sursa = 'salarii' AND document_ref = 'SAL LL/AAAA'`. Cum nimic nu scrie coloana,
> funcția **întoarce 0 prin construcție** — pentru orice firmă, orice lună, orice date. *Nu e o cifră,
> e o constantă deghizată în măsurătoare.*
>
> **3. Unde ajunge acel 0.** La `:525` intră în `compara_d112(…, note_ciorna=ciorne, …)`. Acolo,
> ramura `elif note_ciorna:` — remediu **„sugerat"**, cauza *„N note de salarii în ciornă, așteaptă
> validare"*, acțiunea *„validează"* — e **cod mort: nu poate fi atinsă niciodată**. În locul ei se
> ia mereu prima ramură, care **afirmă o cauză**: *„Statul de plată nu este contabilizat: contul 4315
> nu are rulaj în lună"*, cu remediu **„executabil"**: *„Contabilizează statul de plată."*
>
> **4. De ce rămâne prag 3, și nu urcă azi.** Afirmația nu e falsă **pe datele de azi**: nicio cale nu
> creează nota statului de plată (`salarii_contare` e nelegat, R33), iar rulajul numără doar
> `status = 'validata'` (`rulaje_interval`). Deci azi „nu e contabilizat" nimerește adevărul.
> **Devine falsă în ziua în care R33 se leagă** — atunci aplicația îi va spune contabilului să facă
> exact lucrul pe care tocmai l-a făcut, ascunzându-i acțiunea reală („validează"). E o dependență de
> **ORDINE**, nu de timp: se repară *înainte sau odată cu* legarea lui `salarii_contare`, nu „mai
> târziu".
>
> **5. Ce e totuși greșit AZI, independent de R33 — și e altă interdicție.** Prima ramură nu descrie
> ce vede, ci **afirmă o cauză**, sprijinită pe `not note_ciorna`. Iar acel `0` **nu e informație**:
> nu poate fi altceva decât `0`. Un verdict care se sprijină pe un necunoscut nedeclarat e
> **interdicția 10**, pe cale vie, chiar dacă azi nimerește. Reparat în același commit: `None` =
> necunoscut, declarat ca atare.
>
> **6. Testul care apăra funcția, nu lanțul.** `test_d112_ciorna_da_sugerat_nu_executabil` trece de
> luni de zile — fiindcă îi dă `note_ciorna=1` **direct**. Funcția pură e corectă; **intrarea ei e
> moartă**. Un test unitar verde peste un lanț rupt e aceeași clasă cu gărzile de la §19: dovedește
> că mecanismul *poate* funcționa, nu că *funcționează*.
>
> **NIVELUL EI, în sfârșit (24.08.2026, `bf16f32`).** Ambele măsurători de până acum au fost **un
> nivel mai jos** — pe *înregistrare*. Interdicția vorbește despre **poziția de declarație**. Măsurat
> de acolo, pe date reale:
>
> **1. Ce s-a depus nu se păstrează — pe datele de azi.** `public.declaratii_depuse` **are**
> coloanele `xml` și `randuri`, dar sunt populate **0 din 54**. Motivul nu e că nu le scrie nimeni:
> `core/coada_api.py:300` **le persistă**. Toate cele 54 vin din **importul istoric**
> (`istoric_declaratii_import_api.py:207`), care consemnează *că* s-a depus, nu *ce* s-a depus —
> `sursa` e populată 54/54. Calea care păstrează **n-a fost încă folosită** de nicio firmă.
>
> **2. Deci lanțul n-are capăt de pornire.** O poziție nu se poate desface până la document dacă nici
> declarația nu se păstrează. Sonda care pornea din poziția depusă a găsit **0 poziții** de desfăcut
> — și **asta nu e un verde**, e chiar interdicția 19: absența datelor, nu absența defectului.
>
> **3. Cine compară ce.** Din patru verificări încrucișate, trei compară o declarație — și **una
> singură citea ce s-a depus** (`verifica_d390`, prin `_d300_depus_randuri`); celelalte două
> **regenerau**. *(A patra, `verifica_cota_tva`, nu compară o declarație, deci nu e în clasă.)*
> **Reparate amândouă, 24.08**: D112 și D300 preferă acum depusul. **3 din 3.** O verificare care regenerează compară *evidența de azi* cu *declarația care s-ar genera azi* —
> iar divergența care contează, între ce ține ANAF și ce spun registrele, **nu poate apărea în ea**.
>
> **4. Disciplina exista deja în casă.** `compara_d390_vs_d300` tratează corect `randuri is None`:
> **GRI**, cu temeiul *„absența datelor nu e divergență"*. Deci nu era o formă de inventat, ci una de
> **aplicat**. Reparat azi pe D112: preferă XML-ul **depus** când există, altfel regenerează **și o
> spune în temei** — *„nu s-a păstrat ce s-a depus, deci comparația e evidența de azi față de
> declarația care S-AR genera azi"*. Gardat de `core/test_d112_compara_ce_s_a_depus.py`.
>
> **Rămâne PARȚIAL, și se vede acum de ce**: coloana 3 a lanțului (înregistrare→document) e reparată
> prin derivare, capătul de sus (poziție→înregistrare) e reparat pe D112, dar **niciun capăt nu e
> exercitat pe date reale** cât timp nicio depunere nu trece prin coadă. **R40**.
>
> **Cifra de pe 22.08 rămâne validă și devine mai gravă**: `document_ref` 0 din 33 nu era doar o
> coloană goală, era o coloană goală **pe care se sprijină o decizie afișată**.

## 33 — Un lanț de justificare a cărui sumă nu dă valoarea declarată

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: lanțul există și e fals — se apără o cifră cu documente care n-o compun. E mai rău decât lipsa lanțului de la 32, fiindcă arată complet: la control nu se descoperă o lipsă, se descoperă o neconcordanță

## 34 — Modificarea unei înregistrări dintr-o perioadă închisă

- **stare**: PARȚIAL
- **felul limitei**: ORBIRE — numără **chemările porții**, nu scrierile; nu s-a numărat câte căi de scriere există, deci nu se știe câte o ocolesc
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: poarta perioadei închise (`perioade_blocate` / `PERIOADA_BLOCATA`) e chemată din **4 module de producție**: `core/perioada.py`, `core/common.py`, `core/control_incrucisat.py`, `main.py`
- **instanțe**: nedesfăcute: se știe **de unde se cheamă** poarta, nu **câte căi de scriere ocolesc**
- **calibrare**: gărzile vii sunt `core/test_perioada.py`, `core/test_perioada_indisponibila.py`, `core/test_refuz_generator_422.py`. **Calibrare pe propriul mod de eșec — o cale de scriere care ocolește poarta — nu există**, deci PARȚIAL
- **ce nu vede**: numără **chemările porții**, nu scrierile totale. Nu s-a numărat câte tabele de tenant se scriu în total, deci **nu se poate spune ce fracțiune e acoperită** — cifra 4 e un **plafon inferior** al acoperirii și nu spune nimic despre restul
- **unde ajunge efectul**: o perioadă închisă care se modifică rupe corespondența dintre ce s-a declarat și ce e în evidență

## 35 — Un număr de document reutilizat, sau o serie cu goluri

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: două documente cu același număr, sau un gol în serie care la control se citește ca document dispărut. Nu se poate dovedi nici că nu s-a emis nimic acolo, nici care exemplar e cel valabil

## 36 — O redeschidere de perioadă fără motiv consemnat

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: închiderea își pierde înțelesul: dacă se poate redeschide fără motiv consemnat, nu se mai poate spune DE CE evidența s-a schimbat după depunere — iar diferența față de declarația depusă rămâne fără explicație

## 37 — Un act cu efect juridic extern, fără autor identificat

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: un act cu efect juridic fără autor identificat nu poate fi imputat nimănui

## 38 — O urmă de audit care se poate edita sau șterge

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: urma nu mai probează nimic: ce trebuia să fie dovadă devine afirmație. Un audit care se poate edita apără exact pe cine ar trebui să identifice

## 39 — O ștergere care atinge date aflate sub obligație de păstrare

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: la un control lipsesc documente pe care legea obligă cabinetul să le păstreze, iar răspunderea e a lui, nu a celui care a cerut ștergerea. Efectul e ireversibil prin natura lui: nu se poate reface ce s-a șters

## 40 — O categorie de dată fără termen și temei de retenție

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: fără termen și temei scrise, nu se poate răspunde nici la o cerere de ștergere, nici la un control: nu se știe ce SE POATE șterge și ce NU. Ambele erori sunt posibile simultan, în aceeași firmă

## 41 — O modificare retroactivă aplicată fără lista perioadelor afectate

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o modificare retroactivă fără lista perioadelor atinse lasă declarații depuse pe reguli care nu mai există

## 42 — O regulă veche ștearsă din registru la înlocuire

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: recalculul unei perioade trecute folosește regula nouă, fiindcă cea veche nu mai există: documentele emise atunci nu se mai pot reproduce, iar diferența arată ca o eroare de calcul, nu ca o schimbare de lege

## 43 — O retrimitere automată dintr-o stare nelămurită

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: depunere dublă. O stare nelămurită retrimisă automat produce a doua înregistrare la autoritate, iar corectarea ei e o operațiune cu termen și cu risc de amendă

## 44 — O trimitere considerată confirmată fără identificator de la autoritate

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o trimitere considerată confirmată fără identificator poate fi de fapt nedepusă

## 45 — O valoare intrată din afară, fără sursă și grad de certitudine

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o valoare importată cântărește la fel ca una confirmată, fiindcă nimic nu le deosebește. Contabilul nu poate ști ce a verificat cineva și ce a intrat dintr-un fișier, deci verifică tot sau nimic

## 46 — O presupunere devenită fapt fără confirmare consemnată

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o presupunere devenită fapt intră în declarații ca și cum ar fi fost verificată

## 47 — Un blocaj fără cale de trecere pentru om, sau o trecere fără urmă

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: un blocaj fără cale de trecere oprește contabilul în ziua depunerii, când nu mai are alternativă; iar o trecere fără urmă face imposibil de aflat cine a forțat-o și pe ce motiv. Cele două defecte sunt opuse și amândouă ajung în același loc — o declarație depusă pe care nimeni nu și-o asumă

## 48 — O suprascriere concurentă fără avertisment

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: scrierea unuia dispare fără ca el să afle: contabilul vede „salvat" și pleacă, iar valoarea din evidență e a celuilalt. Nu se manifestă la scriere, ci la citirea de peste o lună

## 49 — Un articol folosit fără dată de verificare a vigorii

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `bfd9f10`
- **cifra**: **0 din 53.** Fiecare obiect `Temei()` construit în `core/` poartă `verificat_la`. La fel `nivel_sursa`: 0 fără. **16 din 53 n-au `url`** — nu pot fi confruntate cu un document, deci nici justificate; sunt aceleași 16 care n-au nici `text_citat` (vezi 53)
- **instanțe**: niciuna. Măsurat pe **AST**, nu la rulare: prima formă a inventarului a citit doar obiectele de la nivel de modul și a văzut 34 din `common` plus 34 din `expirare_cote` — adică **aceleași temeiuri numărate de două ori**, ratând pe cele construite în corpul funcțiilor. Domeniul corect e AST-ul: **53 de construcții `Temei()`**
- **calibrare**: cazul cunoscut **găsit**: cele 16 fără `url` sunt exact cele fără `text_citat` măsurate independent la interdicția 53 — două scanuri diferite, aceeași mulțime. Dacă instrumentul ar fi ratat câmpuri, cele două cifre n-ar fi coincis
- **ce nu vede**: numără **câmpul**, nu adevărul lui: un `verificat_la` scris fără ca verificarea să se fi făcut trece. Interdicția 49 e satisfăcută mecanic; dacă data e onestă ține de disciplină, și e chiar clasa pe care planul o declară nemăsurabilă retroactiv (51, 56, 57)
- **unde ajunge efectul**: o valoare care stă pe un articol nereverificat poate fi greșită de luni de zile fără ca nimic să semnaleze, și ajunge direct în cifra depusă — nimic din lanțul automat nu întreabă de când n-a mai fost verificat

## 50 — O valoare sprijinită pe un articol abrogat sau modificat, fără succesor citat

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `d115f28`
- **cifra**: **0 instanțe, din 16 perechi act-articol verificate la sursă** — și acoperirea e **completă pe registrul de cote**, nu parțială. Testul propriu-zis al interdicției nu e *ce spune articolul*, ci **e confirmarea ULTERIOARĂ ultimei lui modificări?** Rulat mecanic: **16 din 16 cu confirmarea ulterioară, 0 anterioare**
- **instanțe**: **niciuna.** Fiecare articol pe care stă o valoare din registru e **în vigoare**, iar textul confirmă valoarea **verbatim**: art. **17** → *cota de impozit pe profit … este de 16%* · art. **51** → *1%* · art. **138** → *25%* · art. **156** → *10%* · art. **220^3** → *2,25%* · art. **291** → *nivelul acesteia este 21%* și *cota redusă de 11%* · OUG 89/2025 art. **III** → 300/200 lei și 4.300/4.600 lei, cu perioadele exacte.

  **Blocajul de acum două ore s-a dizolvat, și nu prin portal.** Codul fiscal **nu e servit ca pagină unică** — verificat în JS-ul paginii: singurele apeluri sunt `actiuniSuferite`, `actiuniInduse`, `referaPe`, `referitDe`; niciunul nu aduce text. **Dar actul e deja în corpus, adus și amprentat**, iar copia poartă aceleași marcaje de consolidare. `vigoare_articol.py` a primit **mod de fișier local**: pe `cod_fiscal_227_2015_consolidat.txt` vede **2.552.897 de caractere și 1.849 de titluri de articol**, față de ciotul de 4.392 din portal. Amprenta rămâne garda — `test_corpus_amprenta` verifică la fiecare poartă că fișierul e cel adus

  **Cele 13 perechi rămase nu se pot verifica astfel, și motivul e STRUCTURAL, nu de volum:** `Temei` reține **actul care a schimbat regula** și **numărul articolului din actul schimbat** — două lucruri din acte diferite, în aceleași câmpuri. Căutând art. 97 în Legea 141/2025 sau în OG 16/2022 nu se găsește nimic, fiindcă **art. 97 e al Codului fiscal**; actele acelea doar îl modifică. E interdicția **59** văzută din alt unghi, și e cauza pentru care 50 n-a putut fi închisă azi
- **calibrare**: cazul cunoscut **găsit** în ambele direcții: instrumentul vede marcajul acolo unde este (OUG 89/2025 art. XXXVI, 16-08-2026) și **nu-l atribuie unde nu e** (art. III, care poartă valorile). Iar pe corpus, calibrarea e chiar mărimea: un act de 2,5 milioane de caractere cu 1.849 de titluri **nu poate fi confundat** cu ciotul de 4.392 pe care portalul îl dădea — și pe care instrumentul îl refuză explicit
- **ce nu vede**: **o observație de MODELARE, scrisă fiindcă schimbă cum se citește orice cifră de aici:** pentru 10 dintre perechi, `Temei` reține **actul care a schimbat regula** și **numărul articolului din actul schimbat** — `Legea 141/2025 art. 97` înseamnă *CF art. 97, așa cum l-a modificat Legea 141/2025*. Cele 10 se rezolvă la articole de Cod fiscal **deja verificate** (97, 28, 282, 291), deci nu sunt o lipsă de acoperire — dar un instrument care le-ar lua literal ar căuta art. 97 în Legea 141/2025 și n-ar găsi nimic. **Aceleași două câmpuri poartă lucruri din acte diferite.** · Verifică dacă articolul e **modificat**, nu dacă modificarea **atinge valoarea** — confruntarea cu textul s-a făcut de om, verbatim, și e scrisă mai sus. · Rămâne ambiguitatea `Ordin 484/2025` (două forme în portal), scrisă ca atare în `PORTAL_IDS.json`
- **unde ajunge efectul**: cifra depusă stă pe un text care nu mai e în vigoare. Instanța reală: OPANAF 394/2017, citat în nouă locuri, abrogat de OPANAF 705/2020 — găsit din întâmplare

## 51 — O regulă scrisă din memorie, când actul lipsește din corpus

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o regulă scrisă din memorie nu se poate verifica nici măcar la o reverificare, fiindcă nu există act de recitit. Eroarea e invizibilă prin construcție, nu prin neatenție

## 52 — Un act din corpus al cărui text s-a modificat după aducere

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `139bca5`
- **cifra**: **0 acte modificate după aducere, din 188 de amprente verificate** — iar acoperirea e acum **completă: 340 din 340 de fișiere de corpus au o clasă**, nu jumătate. Împărțirea: **188 AMPRENTATE** · **143 DERIVATE** dintr-un fișier amprentat · **9 ale noastre** (7 note scrise, 2 derivări manuale) · **0 nedeclarate**. *(Corpusul era 348 la măsurătoare; cele 8 artefacte de un octet au fost șterse în aceeași zi — vezi R20.)*
- **instanțe**: **niciuna.** Starea a trecut din PARȚIAL în MĂSURATĂ nu prin amprentarea a tot ce mișcă, ci prin **întrebarea corectă**. Formularea de dinainte era *«162 fără amprentă — 48% din corpus»*, cu concluzia firească *«se amprentează și restul, e mecanic»*. Măsurând **înainte** de a amprenta, s-au văzut trei lucruri:

  **(a) Cifra 162 era ea însăși greșită.** Se calculase `339 − 177`, dar 8 dintre cele 177 de amprente sunt pe fișiere din afara celor 339 (`.xsd`, `.zip`). Numărul real era **170**. Două instrumente numărau două domenii și se scădeau unul din altul.

  **(b) Amprentarea oarbă ar fi umflat acoperirea fără s-o crească.** Din cele 170, **151 sunt text derivat** dintr-un pdf/html/xsd care **are deja amprentă** — a le amprenta separat nu adaugă nimic despre act. Alte **7 sunt note scrise de noi** (istoricul cotei de dividende, diurna internă/externă, forma inițială a art. 291): o amprentă pe ele răspunde la *«nu l-am editat»*, pe care git îl răspunde deja — **nu** la *«actul s-a schimbat sub noi»*, care e întrebarea interdicției. Cifra ar fi ajuns la 100% fără ca vreun act în plus să fie păzit.

  **(c) Amprentele a două acte existau deja, dar într-o formă pe care nicio gardă n-o citea.** `anaf_surse/d402_surse_sha256.txt` — scris de mână pe 14.08 — conținea exact hash-urile celor două fișiere D402 neamprentate. Verificate pe 23.08: **ambele se potrivesc**, deci pentru ele răspunsul lui 52 e real, nu presupus: **neschimbate de 9 zile**. Promovate în `.sha256`, intră sub garda existentă.

  Amprentate efectiv: **11** — cele declarate `ADUS` (8 extrase de structură ANAF, 2 PDF-uri aduse, 1 XSD) și `ADUS_ADNOTAT` (3 structuri peste care am scris antet propriu «INVECHIT»; amprenta pinează **versiunea noastră**, și asta e scris, nu ascuns)
- **calibrare**: mecanismul de amprentă a fost construit pe 22.08 **pornind de la un caz real, găsit** (`legea_82_1991_consolidat.html`, modificat față de commit fără ca vreun script să-l scrie). Instrumentul nou, `core/scan_provenienta.py`, are **calibrare negativă** — cerută de interdicția 76: trei mutații care îl orbesc (pragul de gol, cererea de amprentă pe ADUS, detectorul de declarații orfane) au fost aplicate, și **fiecare a fost prinsă exact de testul construit pentru ea**. Partea care contează: **niciuna n-a fost prinsă de testele pe corpusul real**, fiindcă azi corpusul e curat — deci fără calibrarea negativă, gărzile ar fi dovedit doar că instrumentul găsește ce e deja în regulă. Gardat: `core/test_provenienta.py`, 12 teste, dintre care **6 de calibrare negativă** și unul anti-vacuu (un verde pe zero fișiere nu e o afirmație despre corpus)
- **ce nu vede**: nu spune că textul **de pe sursă** s-a schimbat — pentru asta ar trebui re-descărcat, iar pagina portalului nu e reproductibilă octet cu octet. · **Cele 151 de fișiere derivate nu sunt pinate ele însele**: o editare a lor n-ar fi prinsă de amprentă (git o arată, garda nu). · Clasa **DERIVAT se stabilește după NUME**, nu după conținut: un `x.txt` care nu provine din `x.pdf` ar fi clasat greșit. · Clasa declarată e o **afirmație de om** — instrumentul verifică doar că e scrisă și consecventă cu faptele mecanice, nu că e adevărată
- **unde ajunge efectul**: corpusul afirmă un text pe care sursa nu-l mai are, iar toate verificările de deasupra — vigoare, citat, ierarhie — moștenesc eroarea fără s-o poată vedea

## 53 — Un citat verbatim care nu conține valoarea pe care o justifică

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `045c53e`
- **cifra**: **34 din 34** de intrări din registrul de cote au valoarea **în substanța citatului propriu**. Zero nejustificate mecanic. **Dar domeniul e 34 din 53**: atâtea obiecte `Temei()` există în `core/`, iar instrumentul le vede doar pe cele din `common.py`. Din cele **19 din afară**, doar **3** au `text_citat` (în `salarizare.py`), iar **16 n-au deloc** — deci nu pot fi nici justificate, nici acuzate
- **instanțe**: **niciuna în domeniu.** Cifra e curată, și e curată *după* ce instrumentul a fost reparat — vezi calibrarea. **Instrumentul e NOU** (`core/scan_valoare_in_citat.py`, 23.08.2026), fiindcă `scan_citate` măsoară **altceva**, iar confundarea lor ar fi atribuit interdicției 53 o măsurătoare care nu e a ei: `scan_citate._verbatim` verifică dacă citatul **există** în documentul citat (*citatul e real*); 53 cere ca citatul să **conțină valoarea** (*citatul justifică*). Un citat poate fi perfect real și să nu justifice nimic
- **calibrare**: **cazul cunoscut a fost GĂSIT, și era al meu.** Prima formă a dat tot **34 din 34** — un rezultat prea curat ca să fie crezut fără să fie provocat. Inspectând contextul fiecărei potriviri: `impozit_micro` = `0.01` producea forma «1», care se potrivea în **«art.51 alin.(1)»** — adică în **adresa** articolului, nu în substanță. Reparat: adresele (`art.`, `alin.`, `lit.`, `pct.`, `nr.`, date, ani) se scot înainte de căutare. După reparație `impozit_micro` trece din motiv real, pe «...este de **1%**». Gardat: `core/test_valoare_in_citat.py`, 6 teste, dintre care **două pinează chiar modurile de eșec** — cifra din adresă, și subșirul de număr («2.250.000» în «12.250.000»)
- **ce nu vede**: **trei cauze pe care nu le deosebește**, dacă valoarea lipsește: citatul e localizator sau parafrază (formă legitimă, vezi `scan_citate`) · valoarea e exprimată în cuvinte («o pătrime») · citatul chiar nu justifică. Le pune pe toate în «nejustificat mecanic», **nu** în «greșit». · **Supra-tăiere:** tiparul de adrese taie și fragmente de cuvânt («ca**lit**atea» → «ca tea»); nu afectează potrivirea de numere, dar ar afecta o valoare scrisă în litere. · **Domeniul e registrul de cote**, unde perechea valoare↔temei e structurală; celelalte 19 obiecte `Temei` n-au valoare atașată mecanic, deci cer altă măsurătoare
- **unde ajunge efectul**: citarea e falsă chiar dacă actul e corect și în vigoare: o cotă sprijinită pe un citat în care valoarea nu apare. Trei instanțe cunoscute — facilitatea de 300 lei, cota de dividende, pragul mijloacelor fixe

## 54 — Un articol folosit cu verificarea vigorii expirată față de pragul lui

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `bfd9f10`
- **cifra**: **0 confirmări expirate.** Pragul **există** și e declarat: `CONFIRMARE_COTE_PRAG_LUNI`, implicit **6 luni**, în `core/expirare_cote.py`, rulat **lunar din cron** ca RAPORT, nu ca blocaj la calcul. Cea mai veche confirmare din registru are **16 zile**
- **instanțe**: niciuna. **Planul presupunea că pragul nu există** («azi nu există câmpurile»); măsurat, el există din 01.08.2026 și e chiar corectarea unui model greșit anterior: jobul de dinainte semnala apropierea de un `data_out` **inventat**, iar Modelul de temei l-a înlocuit cu vechimea confirmării — *o lege spune de CÂND intră în vigoare, nu până când*
- **calibrare**: cazul cunoscut a fost **găsit**, si e chiar acoperirea raportului, gardată mecanic: `acoperire_lipsa()` întoarce `([], [])` — fiecare cheie din registru are etichetă umană și fiecare etichetă are cheie. O valoare nouă fără etichetă ar produce un mesaj sărac; o etichetă rămasă fără cheie ar fi drift. Ambele ar apărea
- **ce nu vede**: pragul e **unic și global**. Nu distinge o cotă care se schimbă anual de o definiție care nu se schimbă niciodată — vezi interdicția 55, care e chiar despre asta. Deci „0 expirate” înseamnă „0 față de un prag care nu ține cont de natura articolului”
- **unde ajunge efectul**: data de verificare devine formalitate: un articol verificat acum doi ani poartă o dată, deci trece poarta, și poate fi rescris de un an

## 55 — Un articol din corpus fără categorie de reverificare atribuită

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `bfd9f10`
- **cifra**: **53 din 53 fără categorie de reverificare** — fiindcă **câmpul nu există**. Câmpurile unui `Temei` sunt: `tip`, `nr`, `an`, `art`, `alin`, `lit`, `data_in`, `data_out`, `url`, `verificat_la`, `de_cine`, `nivel_sursa`, `text_citat`, `lant_acte`. Niciunul nu e o categorie de reverificare
- **instanțe**: toate. **Există în schimb un prag global unic** (6 luni, vezi 54), aplicat identic tuturor articolelor. Asta **nu e** ce cere interdicția: o cotă de TVA care se poate schimba la fiecare rectificare bugetară și o definiție din Codul fiscal care n-a fost atinsă din 2015 au azi **același prag de reverificare**. Consecința e în ambele direcții: definițiile stabile se reconfirmă inutil, iar valorile volatile se reconfirmă prea rar

  **CATEGORIILE DECISE (23.08.2026, Costin), pe axa acceptată.** Axa: *frecvența istorică de
  modificare a **articolului**, ponderată de **consecința** unei valori expirate.* Volatilitatea
  **actului** a fost respinsă ca axă, cu motiv măsurat: OUG 89/2025 are șase marcaje de consolidare,
  iar art. III — cel care poartă valorile — **niciunul**. O axă pe act ar declara suspecte permanent
  toate valorile sprijinite pe acte mari, iar un semnal permanent se ignoră (vezi **59**).

  **Amândouă măsurile sunt mecanice** — asta e ce face categoriile calculabile, nu atribuibile:

  - **A. Frecvența articolului** se citește din marcajele de consolidare ale articolului în corpus,
    cu `scripts/vigoare_articol.py`, care le vede deja pe fiecare (mod de fișier local, 1.849 de
    titluri).
  - **B. Consecința** se citește din **unde ajunge** valoarea: `core/dependenti_act.py` dă funcțiile
    care o ating, iar modulul lor spune categoria — `d1xx`/`d3xx`/`d4xx` = intră într-o declarație.

  **A — frecvența articolului** (fereastra: **ultimii 3 ani, DECISĂ 23.08.2026** — *suficientă
  ca să prindă un articol modificat de două ori, scurtă cât să nu conteze modificări care n-au
  mai revenit*):

  | clasă | criteriu |
  |---|---|
  | **VOLATIL** | modificat în **cel puțin 2 din ultimii 3 ani** |
  | **MIȘCĂTOR** | modificat **o dată sau de două ori** în ultimii 3 ani, dar nu în cel puțin doi ani distincți |
  | **STABIL** | **niciun** marcaj în ultimii 3 ani |

  **B — consecința unei valori expirate**:

  | clasă | criteriu |
  |---|---|
  | **DEPUS** | valoarea intră într-o declarație generată — greșeala pleacă la ANAF |
  | **CALCULAT** | intră într-o cifră arătată omului (fluturaș, balanță, decont) fără să fie depusă |
  | **INFORMATIV** | apare pe ecran ca informație, nu intră în niciun calcul |

  **Pragul de reverificare, în luni** — nouă valori în loc de una singură:

  | | DEPUS | CALCULAT | INFORMATIV |
  |---|---|---|---|
  | **VOLATIL** | **1** | **3** | **6** |
  | **MIȘCĂTOR** | **3** | **6** | **12** |
  | **STABIL** | **6** | **12** | **18** |

  Pragul global de azi — **6 luni pentru tot** — e chiar căsuța din mijloc. Deci tabelul nu mută
  centrul, îl **desface**: strânge unde greșeala pleacă la ANAF pe un articol care se mișcă (de la 6
  luni la **una**), și slăbește unde nu se mișcă nimic și nu se depune nimic (de la 6 luni la **un an
  și jumătate**). Consecința măsurată la **54** — *definițiile stabile se reconfirmă inutil, iar valorile
  volatile se reconfirmă prea rar* — dispare în ambele direcții.

  **Coloana `INFORMATIV` are cifre PROPRII: 6 · 12 · 18** (23.08.2026, Costin — a doua formă a
  deciziei; prima, 3 · 6 · 12, coincidea cu `CALCULAT` și a fost corectată în aceeași zi). Motivul,
  verbatim: *„o valoare arătată unui contabil e citită și folosită în judecata lui, chiar dacă niciun
  calcul n-o atinge. Nu merită același prag ca una care intră într-o cifră, dar nici dublul."* Deci
  `INFORMATIV` **are voie să existe**, se reverifică mai rar decât `CALCULAT`, și **niciodată la doi
  ani** — plafonul a coborât de la 24 la 18.

  **CONFIRMAT 23.08.2026, după ce nepotrivirea a fost ridicată.** Raportat la `CALCULAT`, cifrele sunt
  dublu pe primele două rânduri (3→6, 6→12) și de o dată și jumătate pe al treilea (12→18) — ridicat,
  și **plafonul rămâne 18**. Costin: *„asta nu mă deranjează — ce voiam să evit era ca o valoare
  informativă să stea doi ani neverificată. Formularea mea era greșită, cifrele sunt bune."* Deci
  regula care guvernează nu e propoziția „nici dublul", ci **plafonul**: nicio valoare informativă nu
  stă doi ani neverificată. Punctul e închis, nu rămâne deschis.

  **Și o regulă care bate tabelul, pe tiparul „faptul bate vectorul":** un marcaj de modificare
  **pe articolul folosit**, apărut după ultima confirmare, cere reverificare **imediat**, indiferent
  de prag. Pragul e pentru ce nu s-a mișcat; ce s-a mișcat nu așteaptă.

  **PUNCTUL DESCHIS S-A ÎNCHIS ÎN ACEEAȘI ZI.** Prima formă a deciziei (3 · 6 · 12) coincidea
  casetă cu casetă cu `CALCULAT`, deci ștergea a treia clasă în loc s-o slăbească; ridicat la aplicare,
  cu cifrele puse totuși **așa cum fuseseră date**. A doua formă — **6 · 12 · 18** — îi dă cifre
  proprii. **Tabelul are din nou nouă căsuțe care spun ceva**, iar `INFORMATIV` e o clasă, nu o
  etichetă. *Costin, la corectare: „Aveam eu confuzia, nu tu."*

- **calibrare**: cazul cunoscut **găsit**, și e chiar registrul: `nivel_sursa` (`MO` / `REDARE` / `INTERPRETARE_OFICIALA` / `PRACTICA`) **arată că modelul știe deja să clasifice temeiuri** — dar clasifică **încrederea în sursă**, nu **frecvența de reverificare**. Deci lipsa nu e de concept, e de câmp
- **ce nu vede**: măsoară doar că nu există niciun câmp care să le poarte, și că pragul unic le înlocuiește prost. **Nu decide categoriile** — le-a propus, iar Costin le-a **decis pe 23.08** (axa, fereastra de 3 ani, coloana `INFORMATIV` cu cifre proprii, 6 · 12 · 18). Ce rămâne **nemăsurat, și e scris ca atare**: câte articole cad în fiecare căsuță — se poate calcula din marcajele articolului și din `dependenti_act`, dar încă nu s-a calculat. Până atunci tabelul e o regulă fără populație cunoscută
- **unde ajunge efectul**: fără categorie atribuită, pragul de reverificare nu se poate aplica, deci nici expirarea de la 54 nu se poate calcula. E interdicția care le face pe celelalte măsurabile

## 56 — O regulă scrisă când textul a fost citit dar nu înțeles, fără cerere specifică

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: se produce ceva plauzibil și se merge mai departe; plauzibil nu e corect. Instanța: „încadrat cu salariul de bază minim brut" — citit, neînțeles complet, interpretat în loc de întrebat, iar un leu peste minim costă salariatul optzeci și doi

## 57 — O valoare fără temei, intrată fără declarația „am căutat și nu am găsit"

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o valoare fără sursă arată identic cu una sursată. Fără declarația „am căutat în X, Y, Z și nu am găsit", absența temeiului nu se distinge de prezența lui

## 58 — O sursă de nivel inferior care contrazice una superioară, fără decizie

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — regiunea e numită: contradicția **se citește, nu se deduce** — scanul dă candidați, verdictul e al omului. Calibrare găsită
- **măsurat la**: 2026-08-23
- **pe commit**: `8477b17`
- **cifra**: **0 conflicte nedecise dintre cele CUNOSCUTE — plafon inferior**, fiindcă instrumentul vede doar conflictele deja recunoscute (vezi «ce nu vede»); și — măsurat separat, 23.08 — **29 de locuri unde s-a putut alege**, dintre care unul singur e consemnat ca decizie. Măsurat pe trei domenii: **(a) registrul de cote** — toate **34** de intrări la nivel **MO**, deci nicio sursă inferioară care să contrazică; **(b) registrul de interpretări** — **2** intrări, ambele decise, `deschise()` gol; **(c) codul** — **29 de blocuri** în **20 de fișiere** unde o citare legală și o autoritate de nivel inferior (structura ANAF, validatorul, XSD, jar) apar împreună
- **instanțe**: **niciuna deschisă dintre cele recunoscute**, iar cazul clasei e rezolvat și consemnat structurat: `forma="forma_publicata_difera_de_text"` — **podeaua part-time**, unde *structura publicată pune diminuarea ÎNĂUNTRUL formulei part_time, iar textul legii vorbește de normă întreagă*. Decizia poartă ambele variante, `ales`, `motiv`, `de_cine`, `la_data`, **arbitrul** (`DUK regula SP1B4_1`) cu ce spune el, `temei_legat`, și **consecința măsurată a alegerii inverse**: *între 06 și 20.08.2026, sume diferite pe fluturaș și pe D112 pentru același salariat — 70,25 lei/lună*.

  **Cele 29 de locuri nu sunt 29 de defecte** — sunt locurile unde cineva a ales între două niveluri de sursă, fie că a scris-o sau nu. Cele mai încărcate: `d101.py` (4), `d301.py` (3), `comodat_chirii.py`, `d112.py`, `d390.py`, `d406.py` (câte 2). **Unul singur din cele 29 are alegerea scrisă** — `d112_reconciliere.reconciliaza`. Restul de 28 sunt **de citit**, nu de reparat: două surse se pot întâlni fără să se contrazică, iar codul poate cita legea pentru regulă și structura pentru formatul raportării
- **calibrare**: cazul cunoscut a fost **găsit**, în `d112_reconciliere.reconciliaza`, cu fragmentul *OUG 156/2024 art.LXVI alin.(5) = OUG 89/2025 art.III: derogarea REDEFINEȘTE nivelul, 3750 în S1 / 4125 în S2*. **Prima formă a verificării mele îl declara RATAT** — îl căuta după art. 146 și art. 168, articolele din enunțul interdicției, pe când decizia citează actele care fac derogarea. **Verificarea era prea îngustă, nu scanul**; testul pinează acum LOCUL, nu cuvintele. Gardat: `core/test_conflicte_sursa.py`, 4 teste, cu anti-vacuu în ambele direcții — o listă goală ar însemna discriminator rupt, una uriașă ar însemna discriminator prea larg
- **ce nu vede**: **contradicția nu se deduce, se citește.** Scanul strânge locurile unde două niveluri de sursă se întâlnesc; dacă ele **spun altceva** e o citire de om. Deci cele 29 sunt **candidați**, iar *28 nescrise* nu înseamnă *28 de conflicte*. · Vede doar **proza** — comentarii și docstring — și doar în funcțiile de nivel de modul: o alegere făcută tăcut, fără nicio urmă scrisă, nu apare nicăieri. · Registrul de interpretări își declară singur aceeași limită: numărul de intrări e *numărul celor RECUNOSCUTE, nu numărul interpretărilor din aplicație*
- **unde ajunge efectul**: se alege tăcut sursa mai comodă. Instanța: podeaua part-time — legea spune una, structura publicată de autoritate spune alta, s-a ales în cod; divergența e 70,25 lei pe lună, pe fiecare salariat part-time sub minim

## 59 — Verificarea vigorii făcută pe act, nu pe articolul folosit

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `d115f28`
- **cifra**: **1 instanță demonstrată, cu ambele răspunsuri puse alături.** Pe OUG 89/2025: verificarea **pe ACT** spune *modificat 16-08-2026* și ar fi ridicat alarmă pe **3 valori** din registru; verificarea **pe ARTICOL** spune că art. III, cel care le poartă, **n-a fost atins**. Diferența dintre cele două răspunsuri e chiar interdicția
- **instanțe**: **una, dovedită pe date reale azi.** Nu e o instanță istorică reconstituită — e chiar verificarea pe care am făcut-o adineauri, și care ar fi produs o alarmă falsă dacă se oprea la nivelul actului. **Un act mare se modifică des**: OUG 89/2025 are marcaje din 27-02, 09-03, 13-03, 31-03, 08-05 și 16-08.2026. La nivel de act, orice valoare sprijinită pe el ar fi *suspectă* permanent — adică semnalul ar fi zgomot, iar zgomotul se ignoră
- **calibrare**: cazul cunoscut a fost **găsit**, și e chiar cel din plan: *art. LXX din OUG 156/2024, abrogat de OUG 29/2026, într-un act rămas în vigoare* — aceeași formă, act viu cu articol mort. Aici s-a demonstrat forma inversă, la fel de utilă: act atins, articol neatins
- **ce nu vede**: verificarea pe articol cere ca instrumentul să găsească **titlul** articolului, iar asta a cerut patru reparații azi (vezi 50). Pentru actele mari, forma consolidată stă la **alt id de portal**, care **nu e stocat nicăieri** — 0 din 529 de intrări din `INDEX.json`, 0 din 77 de fișiere `.html` aduse. Deci fiecare reverificare începe cu o **căutare**, iar legătura act-din-corpus ↔ pagina lui de pe portal nu există
- **unde ajunge efectul**: verificarea trece mereu, fiindcă actul e în vigoare permanent, în timp ce articolul folosit poate fi abrogat separat. Instanța: OUG 156/2024 e în vigoare, dar art. LXX a fost abrogat de OUG 29/2026

## 60 — O regulă, formulă sau structură care implementează o normă, fără articolul asociat

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `b3b6a89`
- **cifra**: **470 de elemente** care implementează o normă, dintre care **doar 96 poartă legătura — 20%**, și **doar 17 o poartă verificabil mecanic — 4%**. Restul de **374 (80%) nu poartă nimic**.

| categorie | total | STRUCTURAT | PROZĂ | NIMIC |
|---|---|---|---|---|
| nomenclator | 260 | 14 | 46 | **200** |
| structură de declarație | 97 | **0** | 11 | 86 |
| regulă de validare | 73 | **0** | 11 | 62 |
| formulă | 24 | 3 | 7 | 14 |
| termen | 16 | **0** | 4 | 12 |
| **TOTAL** | **470** | **17** | **79** | **374** |
- **instanțe**: **Structurile de declarație, termenele și regulile de validare au ZERO legături structurate — toate trei.** Adică exact ce prezicea planul: *azi doar valorile poartă temei*. Dar măsurătoarea **corectează** partea a doua a frazei: planul spune că celelalte *nu poartă nimic*; în realitate **20% poartă legătura ca PROZĂ** — un marcaj `TEMEI:` sau o citare `art.NN` în docstring. Diferența nu e cosmetică: o legătură în proză e verificabilă de un **om** care citește fișierul, dar nu răspunde la întrebarea *ce se atinge dacă se schimbă articolul* — vezi interdicția 61, unde unealta funcționează **doar** peste legăturile structurate
- **calibrare**: cele trei legături pe care planul le numește cunoscute au fost **găsite**, și una a rupt prima formă a scanului: **deducerea personală ↔ art. 77 alin. (4)** ieșea PROZĂ în loc de STRUCTURAT, fiindcă temeiul nu stă în corpul funcției, ci în **registrul de variante** (`_VARIANTE_X = [(dată, funcție, Temei(...))]`) — tiparul de versionare al casei, pe care `graf_temei` a trebuit și el să-l trateze special. Reparat, și pinat în gardă. Celelalte două: **podeaua part-time ↔ art. 146(5^6)/168(6^1)** → STRUCTURAT, tot prin registru; **nomenclatorul codurilor de indemnizație ↔ documentul de structură** → PROZĂ, cu rândul 98 citat. Gardat: `core/test_norma_implementare.py`, 6 teste, cu clichet pe cele 17 structurate
- **ce nu vede**: **numitorul e o ALEGERE, declarată ca să poată fi contrazisă**: cinci categorii, fiecare cu proxy mecanic — formulă (cere `cota()`), structură (`build_xml` / `calcul_dNNN`), nomenclator (constantă NUME_MARE de tip dict/tuple/set în modul fiscal), termen (`scadenta`/`termen` în nume), validare (`valideaza*`/`erori_generare`). Un element care implementează o normă fără să cadă în vreuna dintre ele **nu e numărat**, deci 470 e plafon inferior. · Nu spune că articolul citat e cel **potrivit** — asta e interdicția 53, măsurată separat. · Nu vede o legătură scrisă în alt fișier decât cel care implementează
- **unde ajunge efectul**: la o modificare de lege nu se știe ce cod trebuie atins: se pot determina perioadele afectate, dar nu implementările. Fără 60, P18 nu se poate executa

## 61 — Un articol din corpus fără lista dependenților, generabilă la cerere

- **stare**: PARȚIAL
- **felul limitei**: DOMENIU — regiunea e numită: vede doar articolele care apar într-un `Temei` **din registrul de cote**. Calibrare găsită de două ori, pe acte diferite
- **măsurat la**: 2026-08-23
- **pe commit**: `60c2370`
- **cifra**: **16 din 17.** Atâtea articole distincte citează temeiurile din registrul de cote, și pentru 16 dintre ele lista dependenților **se poate genera** (al 17-lea citează o cotă pe care nicio funcție n-o atinge prin `cota()`). **Cifra e un plafon superior pe un domeniu mic**: 17 articole, față de **339 de acte** pe disc și **53** de obiecte `Temei` în cod
- **instanțe**: **Planul spunea: se măsoară trivial azi, zero, legătura inversă nu există deloc. Nu mai e adevărat, și e consecința directă a reparației din aceeași zi:** R17 a făcut ca `depinde_de(cotă)` să vadă **83** de consumatori ai salariului minim în loc de 12, iar compunerea `articol → cote care-l citează → funcții care depind de ele` a devenit fiabilă. **Pe graful conflat, unealta ar fi dat răspunsuri scurte cu încredere — mai rău decât să lipsească.** Construită acum: `core/dependenti_act.py`, gardată de `core/test_dependenti_act.py` (6 teste). **Închide și o trimitere la ceva inexistent:** `TESTE.md` §282–287 descria `clustere_indirect(act)` la forma prezentului, ca interogare disponibilă, fără să existe nicăieri — semnalat azi ca regula D. Asta e implementarea ei, la nivel de funcții
- **calibrare**: cazul cunoscut a fost **găsit**, de două ori și pe acte diferite: **art. 291 CF** (cotele de TVA, schimbat prin Legea 227/2015 originar și Legea 141/2025 la zi) → 4 cote, **183 de funcții**, mai multe fișiere; **OUG 89/2025** → facilitatea salariului minim, 66 de funcții. Ambele pinate cu **cifre**, nu cu forme, fiindcă modul de eșec al uneltei e **tăcerea**: dacă una dintre cele două hărți se golește, răspunsul devine: nimic nu depinde de articolul ăsta — exact răspunsul greșit pe care nimeni nu-l verifică. Gardat și celălalt mod de eșec, potrivirea prea largă: un articol inexistent dă mulțimea vidă, iar un apel fără niciun câmp **ridică**, fiindcă un răspuns cu tot codebase-ul ar părea foarte util
- **ce nu vede**: vede doar articolele care apar într-un `Temei` **din registrul de cote**. Un articol citat prin `Temei` fără `url` (**16 din 53**) sau doar în proză nu e acolo. · Vede dependența doar prin `cota()` — un literal scris de mână ocolește graful, limită moștenită de la `graf_temei` și declarată acolo. · Lista e a **funcțiilor**, nu a testelor sau a ecranelor: răspunde la *ce cod calculează altfel*, nu la *ce trebuie retestat*. **Starea rămâne PARȚIAL** tocmai fiindcă domeniul e registrul de cote, nu corpusul
- **unde ajunge efectul**: întrebarea „ce depinde de OPANAF 394/2017?" nu are răspuns decât prin căutare, adică prin noroc. Cele nouă locuri au fost găsite abia când cineva a căutat anume

## 62 — O modificare de articol aplicată fără parcurgerea listei dependenților

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: după o modificare de articol rămân implementări care aplică regula veche, nedescoperite, iar declarațiile depuse între timp sunt greșite fără ca cineva să știe care

## 63 — O cifră afișată fără posibilitatea de a-i vedea, la cerere, componentele

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-22
- **pe commit**: `4033a14`
- **cifra**: pe eșantionul cerut de plan — netul de pe fluturaș, o poziție din decont, un rând din D112 — **1 din 3 are componentele la cerere, și doar parțial; 2 din 3 n-au niciuna**
- **instanțe**: **netul**: componentele se pot vedea DOAR descărcând PDF-ul fluturașului; pe ecranul statului de plată nu. Ecranul randează **27 din 37** de câmpuri ale răspunsului API — `deducere`, `facilitate`, `cas_suprataxa`, `cass_suprataxa` nu sunt printre ele. Cuvintele „deducere" și „facilitate" apar în TOT `static/js` doar ca **etichete pe formulare de introducere** (4 locuri: data nașterii, copii școlarizați, declarația părintelui), niciodată ca valoare afișată — verificat pe tot arborele, nu pe fereastra de randare. · **compoziția se pierde strat cu strat**: calculul întoarce 20 de câmpuri și are `deducere` desfăcută în `baza`/`tineri`/`copii`/`total`; API-ul o colapsează la `total`; hârtia o tipărea sub un singur nume — de aici a ieșit reparația de prag 1 de mai jos. · **D300** (1113 linii) și **D112** (820 linii): **0 câmpuri de detaliu/componente**, **nicio rută**. O poziție din decont n-are nicio cale spre facturile din spatele ei
- **calibrare**: cazul cunoscut: fluturașul PDF **chiar** arată componente (facilitate, deducere personală, suprataxa în nota de cost). Instrumentul l-a găsit — deci nu e orb la mecanismul „la cerere"; l-a găsit prezent pe hârtie și absent pe ecran
- **ce nu vede**: măsoară un singur ecran (statul de plată) pentru fluturaș, și caută câmpurile după `s.<nume>` — un câmp folosit sub alt nume ar fi numărat greșit ca absent. De aceea cele două care contează (`deducere`, `facilitate`) au fost confirmate prin căutare pe tot `static/js`, nu prin fereastra de randare. Celelalte ~30 de ecrane nu sunt măsurate: cifra e plafon inferior
- **unde ajunge efectul**: contabilul care nu poate desface o cifră are două opțiuni: să aibă încredere, sau s-o refacă în altă parte. A doua e mai frecventă, și atunci produsul nu i-a economisit munca, i-a adăugat una

## 64 — Un element care putea interveni și n-a intervenit, fără motiv și temei afișabile

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-22
- **pe commit**: `4033a14`
- **cifra**: numitorul cerut de plan — elemente care PUTEAU interveni pe un fluturaș obișnuit — e **5**. Dintre ele, **5/5 fără motiv afișabil** când nu intervin
- **instanțe**: **2 din 5 nu aveau nici măcar valoare distinctă nicăieri** — deducerea suplimentară pentru tineri sub 26 și cea pentru copii școlarizați erau topite într-un total (reparat azi, prag 1). · **1 din 5 are absența tăcută prin construcție**: nota despre suprataxă se tipărește doar `if _supra > 0`, deci când nu s-a aplicat nu scrie nimic. · `facilitate` și `deducere` apar pe PDF cu valoare, dar fără motiv când sunt 0. · **Instanță pe date reale**: `tenant_017` / **PARINTE SCOALA** vs **PARINTE NEDECL** — al doilea are copii școlarizați dar îi lipsește declarația de la art.77, deducerea pentru copii iese **0,00**, iar fluturașul nu spune de ce. Aplicația **știe** motivul (`declaratie_copii` e chiar câmpul care a decis), și nu-l scrie
- **calibrare**: tiparul „de ce nu" **există** pe același ecran, în **10 locuri**: tichete blocate pe pontaj neconfirmat, SEPA indisponibil fără IBAN, REGES fără chei, salariu de bază lipsă — ultimul chiar cu temei (art.146(5^6)/168(6^1)). Deci instrumentul nu e orb la tipar: l-a găsit prezent altundeva și absent exact pe deduceri
- **ce nu vede**: numitorul e cel scris în plan (5 elemente), nu toate elementele posibile din Codul fiscal. Scutirile sectoriale (construcții, IT, agricultură) n-au fost numărate fiindcă niciun salariat real nu le are — deci nu se putea observa dacă absența lor se explică. Cifra e plafon inferior
- **unde ajunge efectul**: o deducere neacordată, o facilitate pierdută, o scutire neaplicată sunt invizibile dacă ecranul arată doar ce s-a aplicat. O absență nemotivată nu se poate contesta, fiindcă nu se vede — și aici greșesc oamenii, nu la ce s-a calculat greșit

## 65 — O valoare diferită de perioada anterioară, fără explicația diferenței

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-22
- **pe commit**: `4033a14`
- **cifra**: **0 mecanisme de comparație între perioade** — 0 potriviri în `core/` + `main.py`, 0 în `static/js`. Navigarea „← luna / luna →" există; comparația nu
- **instanțe**: **calibrarea din plan, rulată exact așa cum e scrisă**: salariat la salariul minim, iunie vs iulie 2026, traversând 1 iulie. Net **2.574,75 → 2.699,63**, diferență **+124,88 lei**. Diferă **simultan 9 câmpuri** — brut, bază impozabilă, CAS, CASS, CAM, cost angajator, facilitate, impozit, net — plus deducerea, **810,00 → 865,00**. Cele **trei** surse pe care planul le prezicea sunt toate confirmate: salariul minim (4.050 → 4.325), facilitatea, deducerea. Contabilul vede doar netul schimbat
- **calibrare**: cazul prezis de plan a fost găsit, cu toate cele trei surse simultan — planul a numit cazul înainte de măsurătoare, măsurătoarea l-a confirmat cifră cu cifră
- **ce nu vede**: caută mecanisme **după nume** (`luna_anterioara`, `luna_precedenta`, `fata de luna`, `diferenta_luna`). O comparație scrisă cu alte cuvinte ar fi ratată — deci cifra 0 înseamnă „niciun mecanism numit așa", nu „niciun mecanism". Cazul de calibrare acoperă doar salariile, nu și decontul sau D112
- **unde ajunge efectul**: cel mai puternic instrument de verificare lipsește exact acolo unde ceva s-a mișcat: un contabil nu verifică o lună izolat, ci știind luna precedentă. Dacă un net diferă și nimeni nu spune de ce, verificarea se mută în afara aplicației

## 66 — O legătură normă↔implementare care există în cod, dar nu ajunge pe ecran

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-22
- **pe commit**: `4033a14`
- **cifra**: **57 de obiecte `Temei(...)` în `core/`. 0 ajung pe ecran ca obiect.**
- **instanțe**: **`core/registru_interpretari.py`** — alegerile pe care legea le-a lăsat deschise, fiecare cu motivul (`de_ce_lasa_loc`) și cu **varianta respinsă**: **0 potriviri în tot `static/js`**. Exact lucrul de care are nevoie cine verifică o cifră, și nu ajunge la el niciodată. · **`d300.py`** (1113 linii): **0 `Temei(`**; **`d112.py`** (820 linii): **0 `Temei(`** — cele două declarații cele mai folosite nu poartă niciun temei structurat. · Singurul temei de pe ecranul statului e **text liber** (`art.146(5^6)/168(6^1)`), nu obiect: nu i se poate verifica vigoarea și nu se leagă de corpus. · Reconcilierile D300/D205 rulează ca gardă internă cu hard-block, dar **nu produc nimic pentru om** — a doua cale există și se oprește înainte de ecran
- **calibrare**: cazul cunoscut, **găsit**: **43 de mențiuni `temei` în JS, pe 5 ecrane** (`termene`, `declaratii`, `firme`, `control_verdict`, `validat`) — deci instrumentul nu e orb la prezență. Citite pe cod, toate sunt temeiuri de **blocaj** (declarație dezactivată cu temeiul scurt, constatare de control, eșec de validare DUK), niciunul temeiul unei **cifre produse**. Distincția a fost citită, nu presupusă
- **ce nu vede**: numără obiecte `Temei(` și cuvântul `temei`; un temei ajuns pe ecran ca proză, fără cuvântul „temei", e prins doar dacă poartă forma `art.`. Deci **„0 ca obiect" e sigur**, iar „câte ajung ca proză" e sub-numărat
- **unde ajunge efectul**: temeiul există în cod și nu ajută pe cine verifică. O legătură normă↔implementare care nu ajunge pe ecran apără codul, nu contabilul

## 67 — Un rezultat produs peste date lipsă, fără ca lipsa să fi fost cerută

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: „nu se datorează" pe o firmă cu operațiuni neînregistrate arată identic cu „nu se datorează" pe o firmă curată. Aplicația a răspuns la ce avea, nu la ce trebuia să aibă

## 68 — O lipsă semnalată abia la generare, când datele nu mai pot fi obținute

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: lipsa e semnalată corect, dar în ziua depunerii, când datele nu mai pot fi obținute. Un semnal la timp e unul la introducere sau la închiderea perioadei, nu la generare

## 69 — Un verdict care nu distinge „gata" de „gata cu ce am avut"

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: un rezultat calculat peste date incomplete intră în decizie ca „gata". Distincția trebuie să fie în rezultat, nu într-o notă alăturată — e P6 aplicat la date, nu la verificări

## 70 — O interpretare care ajunge într-o cifră depusă, nerevizuită fără să fie declarată ca atare

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o interpretare greșită supraviețuiește tocmai fiindcă e bine documentată: nimic din lanțul automat n-o poate contrazice — nu sursa, fiindcă textul e chiar cel ambiguu; nu validatorul, fiindcă verifică structura; nu testele, fiindcă verifică ce s-a decis

## 71 — O copie de siguranță din care nu s-a restaurat niciodată

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: copia se dovedește nefolosibilă exact în ziua în care e singura care mai există. O copie din care nu s-a restaurat niciodată e o presupunere, nu o copie

## 72 — O restaurare care nu se poate dovedi identică cu originalul

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o restaurare fără amprentă e o afirmație: nu se poate spune dacă ce a ieșit e ce era, iar răspunderea juridică a cabinetului stă pe afirmația aia

## 73 — O copie care se poate pierde odată cu originalul

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o copie ștearsă odată cu originalul nu e copie. Efectul e total și tăcut până la incident

## 74 — Un export care rupe lanțul dintre declarație și documentele justificative

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: un export care rupe legătura dintre declarație și documentele justificative transferă date, nu evidență — iar firma care pleacă rămâne fără ce legea o obligă să păstreze

## 75 — Date care se pot lua doar cu intervenția noastră, sau într-un format închis

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: clientul nu-și poate lua evidența decât cu voia noastră, sau într-un format pe care doar noi îl citim. Un produs din care nu poți ieși e un produs de care te temi


## 76 — Un instrument de măsurare fără calibrare pe propriul mod de eșec

- **stare**: MĂSURATĂ
- **măsurat la**: 2026-08-23
- **pe commit**: `942e2c4`
- **cifra**: **4 din 12** instrumente cu gărzi au **calibrare NEGATIVĂ** (un caz care NU trebuie găsit): `audit_preluare` (4), `scan_ancore` (5), `scan_afirmatii` (3), `graf_temei` (1). **Plafon inferior**, fiindcă „calibrare" se recunoaște aici ca *aserțiune care pinează un literal concret* — un caz pinuit printr-o fixtură sau un golden file nu se numără.
- **instanțe**: patru într-o singură zi, toate la instrumente scrise în ultimele trei săptămâni — vezi tabelul din `PLAN_ARHITECTURA.md`. **Dar cea mai veche instanță are 23 de zile și era deja scrisă:** `core/test_datorie.py:283`, xfail(strict) din **31.07.2026**, o numește exact — *„unealtă care se înșală singură: `verificator_conformitate.py` a produs 13 fals-pozitive prin propriul bug… **instrumentul care MĂSOARĂ conformitatea nu e el însuși măsurat**… un gard cu fals-NEGATIVE tace pe un leak real"*. Clasa n-a fost descoperită azi; azi a primit cifră.
- **cele două instrumente cele mai vechi, măsurate la cerere**: `verificator_conformitate.py` și `verificator_sageti.py`, amândouă din **09.07.2026**. **Niciunul nu e importat de vreun test** — zero gărzi, zero calibrare, nici pozitivă nici negativă. Cele 5 fișiere care îl „pomenesc" pe primul îl citesc ca **text** (`open(...).read()`) sau îl numesc într-un `reason` de xfail; niciunul nu-i verifică analizorul. Iar `verificator_conformitate` **rulează la fiecare poartă** — e cel mai executat instrument din proiect și cel mai neverificat.
- **calibrare**: cazul cunoscut a fost **găsit**: `graf_temei` avea calibrare completă în ambele direcții din 01.08 și a trecut 22 de zile conflat — deci măsurătoarea distinge „are calibrare" de „are calibrarea potrivită", care e chiar întrebarea interdicției.
- **ce nu vede**: „calibrare negativă" se recunoaște ca aserțiune sub `not` / `not in` cu literal. Un instrument calibrat negativ prin altă formă — o fixtură known-bad, un golden care trebuie să difere — nu se numără. Iar domeniul măsurătorii a fost `core/` și `scripts/`: instrumentele din rădăcină au intrat abia la cererea din 23.08.
- **unde ajunge efectul**: un instrument necalibrat pe modul lui de eșec produce cifre care se citesc ca măsurători și sunt opinii. Efectul nu e o cifră greșită într-un raport — e că **toate măsurătorile care stau pe el moștenesc orbirea**, iar direcția tăcută (ratează, nu inventează) nu aprinde nimic. `graf_temei` a arătat 12 consumatori ai salariului minim în loc de 83, timp de 22 de zile, fără ca vreun test să pice

