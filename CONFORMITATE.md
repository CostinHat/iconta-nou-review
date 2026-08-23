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

- **etapa**: E1 — SETUL COMPLET (faza 1 din `PLAN_INVESTIGATII.md`)
- **pasul curent**: **FAZA 2 — TEMEIURILE: încheiată.** Toate interdicțiile măsurabile sunt măsurate, iar **50 e acum MĂSURATĂ, nu PARȚIAL**: **16 din 16** perechi act-articol au confirmarea **ulterioară** ultimei modificări, **zero instanțe**, iar fiecare valoare e confirmată **verbatim** în textul articolului ei. Blocajul Codului fiscal s-a dizolvat: actul **nu e servit ca pagină unică** de portal, dar e **deja în corpus, amprentat** — `vigoare_articol.py` a primit mod de fișier local și vede **2,5 milioane de caractere, 1.849 de articole**. **52 e și ea închisă** (23.08, `7663e87`), dar nu prin amprentarea a tot ce mișcă: cifra *162 fără amprentă* era ea însăși greșită — scădea două domenii diferite (real 170) — iar amprentarea mecanică ar fi umflat acoperirea fără s-o crească, fiindcă **151** sunt text derivat din fișiere deja amprentate și **7** sunt note scrise de noi. Domeniul e acum complet — **348 din 348 clasificate** — prin declarație de proveniență, nu prin hash-uri. Rămâne **61** (domeniu mic) ca PARȚIAL. **TRIAJUL E PORNIT** (23.08, decizia lui Costin): pragul 2 s-a golit pe trei sferturi într-o zi — rămân `R19` și `scan_constante`, amândouă din familia *instrument fără calibrare pe propriul mod de eșec* (interdicția 76). Pragul 3 începe cu **cele trei artefacte obligatorii prin lege** — Cartea mare, Registrul-inventar, registrul de evidență fiscală. Din cele trei poziții care cereau decizie, **două s-au închis pe 23.08**: **categoriile lui 55** (axa, fereastra de **3 ani**, coloana `INFORMATIV` cu cifre proprii, **6 · 12 · 18**) și **R14**, care nu mai e decizie de nomenclator ci **migrare, la reparații**; **R18 rămâne deschisă prin decizie**, până există date care generează clustere. **Triajul a produs și o corectare a lui însuși**: pozițiile se atribuiseră după *numele* funcțiilor, nu după ce produc — **patru artefacte reclasificate, în ambele direcții** — **Transferul retrospectiv 3a e FĂCUT** (23.08, înaintea continuării triajului): din cele douăsprezece, **1 MĂSURATĂ · 8 PARȚIAL · 3 rămân NEÎNCEPUTE** — deci NEÎNCEPUTELE scad de la 50 la **41**, iar triajul nu mai ordonează pe poziții necunoscute. **Poziția 2 a triajului, verificată**: *„totul e calculat"* e adevărat pe jumătate — temeiul pe ecran și desfacerea unei poziții sunt **construcție**, nu predare, deci ordinea *L5 înaintea lui L3* se îngustează la cele două intrări care chiar sunt predare. Restanțe: **R21** (forma de înregistrare) **s-a închis în ziua în care s-a deschis** — Fișa de cont înlocuiește Cartea mare în ambele forme; în locul ei, **R22**: jurnalul de origine pleacă la ANAF ca literalul `GENERAL`.
- **criteriul de terminare**: există lista artefactelor cerute de lege — din lege, cu temei — pe **regimurile reale** (nu pe trei alese arbitrar), iar fiecare artefact e clasificat în una din cele cinci liste ale verdictului 1d. Aplicația e gata pe acest criteriu când listele 3, 4 și 5 sunt goale pe fiecare regim; lista 2 poate avea conținut, fiindcă măsoară ce n-a completat contabilul, nu ce n-a făcut aplicația.
- **ce lipsește**: faza 1 nu mai are pași, iar cele două restanțe care blocau punctul de decizie 1 (R17, R2) sunt închise. Rămân restanțele de mai jos — **numărul lor e derivat, nu scris aici**. Cele care blochează cel mai mult sunt acum **R5** și **R6** (încrederea în corpusul pe care stă tot 1a).
- **decizii care blochează**: **niciuna deschisă.** Cea de la pragul 1 (literal vs atingibilitate), deschisă azi-dimineață, a fost **luată în aceeași zi**: se citește ca **atingibilitate**, cu motivul scris în `PLAN_LUCRU.md` — *un prag care nu se poate atinge nu ordonează nimic*.
- **avertisment la cifre**: **Transferul retrospectiv 3a e FĂCUT (23.08.2026)**, deci avertismentul de dinainte nu se mai aplică în bloc: din cele douăsprezece, nouă au trecut (una MĂSURATĂ, opt PARȚIAL). Rămân **trei** care scriu NEÎNCEPUTĂ deși §3a le dădea ca măsurate — **7, 8, 12** — și rămân **prin regulă, nu din uitare**: pentru ele nu există cifră pe domeniu, ci proză despre instanțe, iar *ce nu se reconstituie onest rămâne NEÎNCEPUTĂ*.
- **ultima actualizare**: 2026-08-23
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
| **R19** — `graf_clustere` tratează utilitarele partajate ca proprietate | filtrul exclude partajarea **cu sine**, nu **între alții** | **deschis — următorul la rând** |
| **`scan_constante` — gardă cu ZERO calibrare pozitivă** | 2 teste, niciunul nu pinează un caz concret | **deschis** |

**Pragul 2 s-a golit pe trei sferturi într-o zi.** Rămân două, amândouă din aceeași familie — *un
instrument pe care stau măsurători, fără calibrare pe propriul mod de eșec* (**interdicția 76**).
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

**Ce a rezistat verificării, și se spune la fel de explicit:** **registrul de evidență fiscală** are
într-adevăr **zero** potriviri în `.py`, `.js`, `.html` — apare doar în corpusul de acte. Și
**evidența TVA** n-are producător sub niciun nume de jurnal: `calcul_d300` agregă direct din
`facturi`, deci **datele există, artefactul nu**. Amândouă rămân unde erau.

**REGULA, scrisă în tabel:** *o poziție de triaj se atribuie după *ce produce* modulul, confruntat cu
norma — nu după numele funcției și nu după existența rutei.* Greșeala merge în **ambele** direcții:
un nume potrivit a creditat un motor inexistent, iar lipsa unui nume căutat a ascuns două artefacte
care există. Costul de a nu o respecta nu e simetric: prima direcție amână o construcție necesară, a
doua o pornește degeaba.

#### CORECTARE 23.08 (a doua) — poziția 2 verificată: «totul e calculat» e adevărat pe jumătate

Întrebarea lui Costin: *„Cele 11 artefacte din L5 au fost clasificate pe același criteriu care a greșit
de patru ori? Dacă da, «L5 costă ore» — argumentul pe care am ordonat L5 înaintea lui L3 — s-ar putea
să nu țină."* **Da, și pe una dintre cele patru intrări e chiar aceeași numărătoare de nume.**

| intrarea din L5 | ce spunea justificarea | măsurat 23.08 | verdict |
|---|---|---|---|
| **temeiul pe ecran** (9 declarații) | *«valorile există: 57 de obiecte `Temei`»* | cele **57** trăiesc în `core/common.py` (**35**), `core/salarizare.py` (**10**) și module mici; **cele nouă module de declarație au ZERO** — `d101` chiar importă numele (`Temei as _Tm`) fără să construiască vreunul | **construcție** |
| **desfacerea unei poziții** | *(se subînțelegea din aceeași frază)* | **niciun producător**: nicio funcție care, dată o casetă, să întoarcă operațiunile care au compus-o; `valideaza` întoarce `stare` și **numărul** de operațiuni | **construcție** |
| **balanța pe ecran** | *«balanța se produce»* | adevărat: se produce și se descarcă PDF (`firme.js:2652`); lipsește doar drumul de la cifră la notele din spate | **predare** — ține |
| **componentele fluturașului** | *«`deducere`/`facilitate` sunt în răspunsul API»* | adevărat, verificat pe cod: `core/stat_plata_api.py:109–114` întoarce deja `deducere`, `deducere_baza`, `deducere_tineri`, `deducere_copii` | **predare** — ține |

**Numărătoarea de 57 măsura alt domeniu decât cel despre care afirma** — exact defectul de la poziția 1,
în aceeași formă: o cifră adevărată despre motor și salarizare, folosită ca dovadă despre declarații.
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

**Contorul NU se scrie**: se derivă din git — câte commituri au atins `CONFORMITATE.md` de când s-a
deschis restanța. **Numără commituri, nu ture** — o tură poate produce mai multe, deci contorul urcă
mai repede decât ziua; e ce poate da git fără să inventez o noțiune de „tură". O restanță cu contorul
peste unu a supraviețuit cel puțin unei porți verzi și se arată ca atare în secțiunea B.

**Pragul, scris ca să nu rămână doar în cap (Costin, 22.08.2026).** Restanțele se deschid ca să fie
rezolvate, nu ca să fie colectate. **Punctul de control: închiderea lui 1b.** Dacă la acel moment
niciuna dintre restanțele deschise nu s-a mișcat — nici rezolvată, nici măcar măsurată — atunci
procedura colectează în loc să rezolve, iar asta se vede exact aici, în contoare. Nu e o regulă cu
gardă; e un prag de citit, la un moment numit.

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
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `07d5351`
- **ce blochează**: **măsurat înainte de a fi scris, nu presupus.** Din **529** de fișiere în `INDEX.json`, **47 poartă cel puțin un marcaj** (21 `forma_la_data` · 9 `consolidat_la_zi` · 11 detectate ca formă inițială · 2 abrogate · 2 cu text neextractibil), iar **18** dintre ele sunt legate de cote. **Patru poartă o notă explicită** — avertismente scrise de om: *„forma initiala 2014; NU include Ordinul 1239/2021…"* (`omfp_1802_2014.pdf` — chiar fișierul care a produs cifra falsă) · *„consolidare 2018, nu la zi"* · *„sursa legex.ro, neoficiala"* · *„abrogat de HG 773/2019 … HG 773/2019 nu e in corpus"*. **Cine citește marcajele: doar `gen_index.py` însuși și două gărzi.** Nimic la punctul de folosire — cine deschide fișierul ca să ia o valoare nu vede nimic. Asta nu e o instanță, e clasa din care instanța a ieșit.
- **condiția de deblocare**: marcajul ajunge la folosire, nu doar în manifest. Se închide când citirea unei valori CURENTE dintr-un fișier marcat `forma_la_data` sau cu notă e **imposibilă sau zgomotoasă prin construcție** — nu doar nerecomandată. Forma minimă acceptabilă: o gardă care leagă fiecare `Temei` de forma fișierului lui și pică pe combinația „valoare fără succesor + sursă marcată ca formă veche". Până atunci, cele 4 note se citesc manual înainte de orice valoare luată din acele fișiere.

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
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `1eaecbb`
- **ce blochează**: la prima citire, cele 15 potriviri ale interdicției 21 au fost triate **pe linie**; trei dintre cele numite zgomot merită a doua privire, **pe context**. Verificate azi, toate trei există în cod: `core/d223.py:159` — `len(asociati) == 1 and cota == Decimal(100)` (regula „100% doar cu un singur asociat"); `core/d406.py:1338` și `:1367` — `cota_l == 0` / `cota == 0` decid codul fiscal `300101` vs `300501`. Dacă vreuna e o **interpretare**, nu o regulă de lege, e o alegere făcută la scriere — adică exact interdicția 21, iar cifra „2 reale" rămâne plafon inferior. **Consemnate până azi doar în proză**, în patru locuri (`GARZI.md`, `ISTORIC.md`, `PREDARE_LANT.md`, câmpul „ce nu vede" al secțiunii 21) — nicăieri cu stare și condiție.
- **condiția de deblocare**: **la reluarea interdicției 21**, sau mai devreme, la primul commit care atinge `d223.py` ori `d406.py`. Se citește fiecare pe context, se spune dacă e lege sau interpretare, iar cifra secțiunii 21 se corectează în consecință.

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
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `1eaecbb`
- **ce blochează**: cele **patru** cerințe din „Ce se gardează" (`PLAN_LUCRU.md`), cu starea fiecăreia la 22.08.2026 — **răspuns la întrebarea 5**: (1) *„un raport care nu enumeră restanțele deschise nu trece"* — **realizată în forma posibilă**: secțiunea B le enumeră, derivat din registru; **negardabilă mecanic**, fiindcă rapoartele nu trăiesc pe disc, iar asta se declară, nu se ascunde. (2) *„o restanță fără «ce o închide» nu poate fi scrisă"* — **implementată**, câmpul e obligatoriu. (3) *„o etapă nu se poate declara terminată dacă are restanțe deschise care îi aparțin"* — **implementată azi**, cu anti-vacuu. (4) *„o restanță cu blocaj EXTERN fără cerere specifică formulată nu trece"* — **NEIMPLEMENTATĂ, și singura rămasă**. **Răspuns la întrebarea 4: SE POATE GARDA, nu e o consecință acceptată.** Împăcarea a mutat EXTERN pe axa „cine deblochează", care azi e o notă în proză — dar nimic nu obligă să rămână așa: dacă devine **câmp** (`cine deblochează`: EXTERN / INTERN / DECIZIE), garda se scrie în trei rânduri, pe același tipar cu celelalte: valoarea EXTERN cere, în `condiția de deblocare`, cele trei elemente ale unei cereri specifice — **ce trebuie · de unde · pentru ce**. Deci rămâne restanță de muncă, cu condiția de deblocare acum concretă, nu limită declarată.
- **condiția de deblocare**: cele două gărzi există, RED-probate. Prima are nevoie de `unde intră` pe fiecare restanță — **există de azi**, deci nu mai e blocată de nimic tehnic; a doua are nevoie de o formă scrisă a cererii specifice.

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

- **felul**: ARTEFACT
- **cine deblochează**: INTERN
- **unde intră**: E1 · faza 1, pasul 1b
- **reluări**: 0
- **stare**: DESCHISĂ
- **deschisă pe commit**: `44d30cf`
- **ce blochează**: măsurat la Q2 (evidența TVA): pe t003, **una din trei facturi are `tert_cui = NULL`** (CMT149, către „Agentie Turism Marja SRL"). Un jurnal de vânzări și D394 cer partenerul cu codul lui; fără el, operațiunea nu se poate raporta pe partener. Nu e o lipsă de structură — coloana există — ci de **completitudine a datelor**, deci se rezolvă altfel decât o absență de producător.
- **condiția de deblocare**: se măsoară **câte** facturi din matrice n-au cod de partener, pe direcție și pe plătitor de TVA, și se stabilește dacă lipsa e legitimă (persoană fizică) sau nu. Abia apoi se decide dacă aplicația trebuie să ceară codul la introducere (P23) sau doar să-l semnaleze.

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
- **stare**: DESCHISĂ
- **deschisă pe commit**: `241acf4`
- **ce blochează**: al **doilea** defect al aceluiași instrument, distinct de R17 și nereparat de el. `graf_clustere` declară că o funcție e „deținută" de clusterul ale cărui teste o cheamă. Propriul docstring spune *„funcție partajată = CO-LOCAȚIE, nu dependență"*, dar filtrul aplicat e doar `if f in own: continue` — adică exclude partajarea **cu sine**, nu partajarea **între alții**. Un utilitar chemat de testele a cinci clustere e „deținut" de toate cinci, iar orice al șaselea cluster care îl atinge tranzitiv capătă **cinci muchii de dependență**.

  **MĂSURAT 23.08.2026 pe graful reparat:** din **154** de funcții deținute, **70 sunt deținute de 2+ clustere**. `duk.py::valideaza` — de **21 de clustere**; `rip_migrare_api.py::get` — de 19; `duk.py::poate_valida` — de 11.

  **Efectul asupra cifrelor:** cu regula de azi, harta are **960 de muchii** între clustere. Cerând ca dovada să fie o funcție cu **proprietar unic**, rămân **111**. Adică **aproape 9 din 10 muchii sunt co-locație, nu dependență** — de acolo vin absurdități ca *„facilitate salariu minim depinde de «edge canonic www/HEAD (crawler)»"*.
- **condiția de deblocare**: proprietatea se decide altfel decât „testul o cheamă" — fie funcția aparține modulului pe care clusterul îl verifică, fie proprietarul se declară explicit în inventar. Se închide când numărul de muchii sprijinite pe funcții multi-proprietar e **zero**, iar cifra de 111 se re-măsoară — nu se moștenește cea de 960.

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
- **stare**: DESCHISĂ
- **deschisă pe commit**: `936aeb3`
- **ce blochează**: OMFP 2634/2015, Anexa 1, **pct. 58 lit. i)** cere ca programul să asigure, printre elementele constitutive ale **fiecărei** înregistrări contabile, *„jurnalul de origine în care se regăsesc înregistrările contabile"* — citit verbatim din corpus. Cerința e **independentă de forma de înregistrare**, deci nu dispare odată cu R21. Măsurat: `core/d406.py:832` scrie `<JournalID>GENERAL</JournalID>` **literal**, aceeași valoare pentru orice înregistrare, în declarația care pleacă la ANAF. Elementul **există** ca etichetă și **nu poartă nicio informație**: nu se poate răspunde la *„din ce jurnal provine rândul ăsta"*, care e chiar întrebarea pentru care norma cere câmpul. **Și datele pentru un răspuns real există deja**: coloana `inregistrari.sursa` poartă azi valori care sunt exact jurnale de origine — `casa` (`core/sgr.py:36`, `core/ong.py:27`, `core/contracte_speciale.py:90`), `salarii` (`core/control_incrucisat.py:485`), `migrare` și `iconta` (`core/istoric_declaratii_import_api.py`). Deci nu lipsește informația, lipsește legătura dintre ea și SAF-T.
- **condiția de deblocare**: o **decizie**, fiindcă nu e determinată de text — (a) `JournalID` se derivă din `inregistrari.sursa`, cu o mapare scrisă și un temei pentru fiecare valoare, și atunci elementul devine informativ; sau (b) se **declară scris** că firma ține un singur jurnal general, cu temeiul care permite asta, și atunci constanta e adevărată, nu o umplutură. **Ce nu e acceptabil e starea de azi**: un câmp cerut de normă, completat cu o constantă, fără ca undeva să scrie că firma chiar ține un singur jurnal. Se închide când `JournalID` ori poartă originea, ori are în spate o declarație scrisă că e unic.

## E1 — SETUL COMPLET (faza 1 din PLAN_INVESTIGATII.md)

Faza 1 e singura care răspunde la afirmația „aplicația face contabilitate conformă". Ce urmează nu
sunt interdicții, sunt măsurătorile fazei — dar poartă aceleași câmpuri, fiindcă o cifră fără dată și
fără commit îmbătrânește la fel de tăcut aici ca oriunde.

- **măsurat la**: 2026-08-22
- **pe commit**: `84f77c4` (HEAD la momentul măsurării)

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
- **măsurat la**: 2026-08-22
- **pe commit**: `ffbcb74`
- **cifra**: **131** brut, din care ~23% zgomot pe eșantionul de 30 → **~100 reale**. Confruntare cu al doilea instrument: `core/scan_constante` raportează 93 „nesursate" (clasa C); diferența e de definiție — clasa A (48 de valori CU obiect `Temei`) e tot în afara registrului, fiindcă un `Temei` lângă o valoare nu e registrul. 131 = A(48) + C(93) + E(33) − 43 aflate chiar în `common.py`/`temeiuri.py`.
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o regulă fiscală ajunsă în interfață nu e nici testată, nici gardată, nici versionată pe dată: pragul din ecran rămâne la valoarea de anul trecut mult după ce registrul s-a actualizat, iar nimeni nu se uită acolo

## 5 — Un strat care cheamă în sus sau ocolește un nivel

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **80 de afirmații găsite, din care 4 tipate.** În domeniul interdicției — clasele `A_verdict` și `C_import` — **14 netipate, în 10 fișiere** (`raportari_ai.py` 3 · `articole_import_api.py` 2 · `main.py` 2 · alte șapte cu câte una)
- **instanțe**: cele 14. Netipate înseamnă: afirmația e un șir, deci **nu poartă nici domeniul, nici sursele** ca atribute — se poate cita corect și rămâne fără domeniu
- **calibrare**: `core/afirmatii.py` + `core/test_afirmatii_tipate.py` țin clasa tipată; scanul e `core/scan_afirmatii.py`. **Calibrare pe propriul mod de eșec: nu are** — de aceea starea e PARȚIAL, nu MĂSURATĂ, conform regulii de transfer din §3a
- **ce nu vede**: scanul recunoaște afirmațiile după tipar sintactic, pe patru clase; o afirmație scrisă altfel nu intră în numărătoare. Cifra e un **plafon inferior**: 14 e cât s-a văzut, nu cât există
- **unde ajunge efectul**: o afirmație fără domeniu se citește peste șase luni ca adevăr permanent

## 10 — Un verdict favorabil care coexistă cu necunoscut nedeclarat

- **stare**: PARȚIAL
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **9 afirmații de clasa `A_verdict` netipate**, din cele 80 găsite — un verdict netipat nu poate purta câmpul «ce n-a fost verificat», deci coexistența cu necunoscutul nu se poate nici declara, nici verifica
- **instanțe**: cele 9
- **calibrare**: **nu are calibrare proprie** — scanul măsoară *tiparea*, nu *coexistența cu necunoscutul nedeclarat*. E cel mai slab dintre cele transferate azi, și se scrie ca atare
- **ce nu vede**: măsoară o **precondiție** a interdicției (verdictul e obiect, deci poate purta necunoscutul), nu interdicția însăși. Un verdict tipat care **tace** despre necunoscut ar trece neobservat. Cifra e un **plafon inferior**
- **unde ajunge efectul**: un verdict favorabil care ascunde necunoscutul îl face pe contabil să creadă că e verificat ce n-a fost verificat

## 11 — Un verificator care importă modulul verificat

- **stare**: PARȚIAL
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
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **274 de mesaje în 31 de fișiere** expun nume interne de câmp, sub clichet **per-fișier** (`core/test_mesaje_generare_fara_camp_intern.py`, `_BASELINE`). Niciun fișier nu poate crește; un fișier nou intră cu 0. `d301` e deja pe 0, reparat
- **instanțe**: cele 274, fiecare cu fișierul ei în clichet
- **calibrare**: clichetul e viu și pică pe creștere. **Calibrarea pe propriul mod de eșec — dacă semnalul ratează un nume intern — nu s-a făcut**, deci PARȚIAL
- **ce nu vede**: semnalul e un **token `snake_case` într-un șir de mesaj**, în funcțiile de validare ale generatoarelor. Un nume intern **fără underscore** (`codO`, `denO`, `Data_A`) nu se vede prin acest semnal, iar mesajele din afara generatoarelor sunt în alt gard. Cifra 274 e un **plafon inferior**
- **unde ajunge efectul**: contabilul primește un refuz pe care nu-l poate acționa: un nume intern nu-i spune ce să completeze, iar mesajul arată ca un defect al aplicației. Efectul nu e o cifră greșită, e o cerere de ajutor către noi pentru ceva ce el putea rezolva singur

## 14 — Un parametru cu valoare implicită într-o funcție de calcul fiscal

- **stare**: PARȚIAL
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **129 de definiții de funcție** cu cel puțin un parametru `=None` în modulele fiscale (`core/d1xx`–`d4xx`, `salarizare.py`, `motor.py`, `common.py`)
- **instanțe**: nedesfăcute pe instanțe: numărătoarea e pe **definiții**, nu pe parametri, și nu separă defaultul legitim de cel care ascunde o cale netestată
- **calibrare**: **nu are.** Măsurătoarea veche din §3a — *25 din 78 de parametri cu default `None` care n-au fost NICIODATĂ `None`* (`GARZI.md`) — are **alt domeniu și alt criteriu**, deci nu se poate compara cu 129 și **nu s-a transferat ca atare**. Cele două cifre nu se adună și nu se scad
- **ce nu vede**: numără forma (`=None` în semnătură), nu efectul (dacă apelantul chiar omite parametrul). Cifra e un **plafon inferior** al defectelor și un **plafon superior** al gravității: multe dintre cele 129 sunt defaults legitimi
- **unde ajunge efectul**: un default ascunde o cale netestată: apelantul care uită parametrul primește tăcut valoarea comodă, iar defectul nu se vede la apel, ci mult mai târziu, în cifra rezultată. E cauza interdicției 2, dar și a oricărei alte valori implicite din motor — de trei ori într-o singură zi

## 15 — Reguli diferite la previzualizare față de salvare

- **stare**: PARȚIAL
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
- **măsurat la**: 2026-08-22
- **pe commit**: `84f77c4`
- **cifra**: **14** gărzi citesc sursă (`.py`/`.js`) fără să scoată proza — din 369 de fișiere-gardă. Una (`test_octeti_invizibili`) e **exclusă prin natura ei**: un octet invizibil dintr-un comentariu e tot un defect, deci trebuie să citească textul brut. Rămân **13 candidate**, din care **3 privite pe context**: 1 poate ASCUNDE o gaură, 2 pot doar să RAPORTEZE ÎN PLUS. Restul de 10, neprivite.
- **instanțe**: poate ascunde o gaură — `test_golden_xsd.py:47` caută `from core import <mod>` în textul testelor, deci un docstring care pomenește modulul face un test inexistent să pară prezent (exact clasa care a lăsat d402 fără nicio probă). Pot doar raporta în plus — `test_upsert_motivat.py:25` (`"DO UPDATE"` dintr-un comentariu), `test_harta_ecrane.py:29` (`fa-*` dintr-un comentariu devine ecran fantomă). Neprivite: `test_gard_masca_zero`, `test_masti`, `test_mesaje_valueerror_publicat`, `test_nomenclatoare_ancorate`, `test_reconciliere_vie`, `test_refuz_generator_422`, `verificator_conformitate` și încă 3.
- **calibrare**: GĂSIT, în ambele direcții. Pozitiv: `test_schema_coloane.py` la revizia `5d46d4f` (înainte de reparație) e raportat; pe HEAD, unde folosește `scan_ancore.domenii_docstring`, **nu mai e**. Negativ NEraportat: `test_proprietate_coaja.py`, care are propriul `_fara_comentarii()` — recunoscut mecanic, pe arbore (o operație peste un marcaj de comentariu), nu după numele funcției. **Prima formă a instrumentului a RATAT cazul canonic**: scutea orice modul care folosea `tokenize` sau `ast.parse`. Amândouă sunt scutiri false — tokenizarea *colectează* string-urile (docstringul e un token de string), iar `ast.parse` lasă docstringurile ca noduri `Constant`. Chiar asta era natura bug-ului lui `test_schema_coloane`. Lista de scutiri prea largă orbește la fel de bine ca un tipar mort.
- **ce nu vede**: o gardă care își ia dovada din proză prin altă poartă decât citirea unui fișier sursă — dintr-un `.md`, dintr-un răspuns HTTP, din baza de date · o gardă care citește sursă printr-un ajutor din alt modul · **direcția**: instrumentul spune că proza AJUNGE la comparație, nu că a schimbat vreodată un verdict. Ca să știi dacă ascunde sau raportează în plus, trebuie citită — de-aia cifra e însoțită de „3 privite din 13".
- **unde ajunge efectul**: o gardă care nu se poate încălca decât în aparență lasă clasa deschisă și dă încredere falsă. Instanțe reale, toate din 20–21.08: TEMA D se aprindea pe propria explicație · `lit.` se aprindea pe „po-LIT-e)" · `test_schema_coloane` a inventat coloane numite `document`, `aplicația` dintr-un docstring · gardul de clasificare a prozei s-a aprins pe propriul meu comentariu. Instrumentul din `core/scan_garzi.py` (sub-instrumentul C) reproduce cifra


## 19 — O gardă care raportează favorabil pe zero rânduri

- **stare**: MĂSURATĂ (două forme, măsurate cu instrumente diferite)
- **măsurat la**: 2026-08-22
- **pe commit**: `84f77c4`
- **cifra**: **19a — 3** tipare care nu pot potrivi nimic, din 339 extrase. **19b — 157** teste care CULEG și n-au nicio aserțiune de existență, din 696 care culeg (din 2072 cu aserțiuni); dintre ele **145 au un control pozitiv în modul** (atenuare), deci **12 n-au nici în test, nici în modul**. Zgomot măsurat pe 29 de rezultate privite: ~1/3 înainte de ultima corecție a instrumentului, adus la aproape zero prin recunoașterea aserțiunilor care fixează o valoare concretă.
- **instanțe**: **19a** — `test_garzi_tacere_ui.py:47`, `test_import_motiv_vizibil.py:27`, `verificator_conformitate.py:996`. Toate trei sunt de forma `assert not <găsite>`: zero potriviri poate însemna „lumea e curată" SAU „tiparul e orb", iar instrumentul nu le desparte. **19b, cele 12 fără nicio atenuare** — `test_cui_cnp_test_valid:36` · `test_d112_mesaje_afisate:10` · `test_declarant_warn:14` · `test_fixturi_shared_period:18` · `test_garzi_mesaje_afisabile:25` · `test_ghiduri_servite:14` · `test_golden_xsd:33` · `test_harta_ecrane:33` și `:40` · `test_import_mesaje_afisate:15` · `test_rotunjire_fiscala:24` · `test_rute_model_body:19`. **Cinci dintre ele sunt gărzi pe care le-am construit eu în campaniile din 19–21.08** — nu e o observație despre codul moștenit.
- **calibrare**: GĂSIT, ambele. **19a** — gardul R4 cu octetul `0x08` în regex (`test_temei_termene.py:29`, `\x08(OUG|OG|Legea|...)`) apare la revizia `29bd752` și **dispare** pe HEAD, unde a fost reparat. **19b** — `test_verificarea_nu_scrie_nimic`, care număra pe o lună fără nicio contradicție: nu există ca revizie (a fost reparat în același commit cu introducerea), deci a fost **RECONSTRUIT** din forma descrisă în GARZI.md; apare la reconstruire (158) și nu apare pe HEAD (157), iar diferența e exact testul numit. Caz negativ NEraportat: cele 25 de tipare cu zero potriviri al căror subiect e un artefact produs la RULARE — corpusul nu poate spune nimic despre ele, deci instrumentul tace.
- **ce nu vede**: **19a** — tiparele construite dinamic (24, f-string sau concatenare) nu se pot extrage · un tipar mort *față de subiectul lui* dar care potrivește altundeva în repo nu e prins (implicația merge într-o singură direcție, cea sigură) · nimic despre tiparele aplicate pe artefacte de rulare. **19b** — o mulțime culeasă poate fi goală **la rulare** fără ca instrumentul s-o știe: el citește forma aserțiunii, nu execuția. Cifra e un **plafon inferior** pentru „ar trece pe o lume goală" și un plafon superior pentru „chiar trece". Iar controlul de modul e o atenuare, nu o dovadă — a fost mai întâi o EXCEPȚIE tăcută în instrument, și chiar ea a înghițit cazul de calibrare.
- **unde ajunge efectul**: o gardă care raportează favorabil pe zero rânduri e datorie eternă indistinctibilă de datorie reală — nu poate deveni verde prin reparație, fiindcă e deja verde. Instanțe reale: gardul R4 a stat verde pe un regex care nu putea potrivi niciodată, iar `verificarea nu scrie` ar fi trecut și dacă verificarea emitea singură corecții. Reproducerea cifrelor: `./venv/bin/python -m core.scan_garzi`


## 20 — O declarație de perimetru devenită neadevărată

- **stare**: PARȚIAL
- **măsurat la**: 2026-08-23
- **pe commit**: `936aeb3`
- **cifra**: **4 fațete din 9** sunt declarate neacoperite — §5 calculat = **{F3, F4, F5, F7}**, computat din `MODEL_AUDIT_TENANT.md` de `core/test_perimetru_calculat.py`, nu scris de mână
- **instanțe**: cele 4 fațete. Ce face gardul imposibil: ca §5 să rămână gol când o fațetă își pierde acoperirea
- **calibrare**: cazul cunoscut **găsit**: gardul cere ca fiecare fațetă marcată GARDAT să numească fișiere care **există** (`test_gardat_numeste_fisiere_care_exista`), iar §5 e pinat pe baseline — o fațetă care își pierde tăcut gardul mută §5 și pică
- **ce nu vede**: compută din **model**, deci vede perimetrul declarat, nu lumea: o zonă care nu e nici măcar o fațetă în `MODEL_AUDIT_TENANT.md` rămâne invizibilă. Cifra 4/9 e un **plafon inferior** al neacoperirii reale
- **unde ajunge efectul**: un perimetru neadevărat face ca o zonă neacoperită să pară acoperită

## 21 — O interpretare care apare ca și cum ar fi text de lege

- **stare**: PARȚIAL
- **măsurat la**: 2026-08-22
- **pe commit**: `ffbcb74`
- **cifra**: **15** candidate (egalități stricte pe o valoare de registru), din care **2 confirmate** la citire pe context. Raport: 56 de inegalități pe aceleași valori, care de regulă sunt chiar textul legii („nu depășește").
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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
- **măsurat la**: 2026-08-22
- **pe commit**: `cbf7b67`
- **cifra**: **19 din 33 de note contabile** nu au nicio legătură către documentul care le justifică. Măsurat **un nivel mai jos decât spune interdicția** — pe înregistrare, nu pe poziția din declarație — fiindcă acolo se rupe lanțul întâi: o poziție nu se poate desface până la document dacă nici înregistrarea din spatele ei nu poate. **Cifra e un plafon inferior**: nu s-a măsurat câte poziții de declarație sunt afectate, ci câte note nu pot fi desfăcute.
- **instanțe**: pe toți cei șase tenanți cu note (t003, t005, t013, t014, t016, t017): `document_ref` populat **0 din 33** · `numar` **1 din 33** (doar `AMORT-2026-08`) · `factura_id` **14 din 33**. Coloana `inregistrari.document_ref` **există și nu o scrie nimeni**: singurele apariții în cod sunt o CITIRE în `core/control_incrucisat.py:491` (caută `document_ref = 'SAL LL/AAAA'`, o valoare pe care n-o produce nimic) și `core/registratura_api.py`, care lucrează pe altă tabelă.
- **calibrare**: GĂSIT — cazul pozitiv e nota de amortizare de pe t013 (`id=30`, `numar=AMORT-2026-08`), singura cu identificator propriu; cazul negativ NEraportat sunt cele 14 note cu `factura_id`, care **au** legătură și n-au intrat în cifră.
- **ce nu vede**: nu urmărește lanțul mai departe, de la înregistrare spre poziția din declarație și înapoi · nu spune dacă o notă **trebuie** să aibă document justificativ extern (amortizarea, de pildă, e o notă internă legitimă) — deci o parte din cele 19 pot fi corecte; de aceea cifra e plafon inferior și pentru datorie, nu doar pentru acoperire
- **unde ajunge efectul**: o cifră declarată care nu se poate desface până la document nu se poate apăra la control

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

  *Notat fiindcă registrul nu ascunde nepotriviri, oricât de mici: raportat la `CALCULAT`, cifrele sunt
  dublu pe primele două rânduri (3→6, 6→12) și de o dată și jumătate pe al treilea (12→18). Regula
  aplicată e cea care se citește din tabel — „informativul se reverifică mai rar decât calculatul,
  niciodată la doi ani" — nu propoziția „nici dublul", care ține doar pe rândul STABIL.*

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

