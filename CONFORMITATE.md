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
- **pasul curent**: faza 1, pasul **1b** — **toate cele patru familii** (A, B, C, D) sunt măsurate pe date reale. Urmează **1c** (se poate verifica pe ecran — interdicțiile 63–66), apoi verdictul **1d** pe cele cinci liste.
- **criteriul de terminare**: există lista artefactelor cerute de lege — din lege, cu temei — pe **regimurile reale** (nu pe trei alese arbitrar), iar fiecare artefact e clasificat în una din cele cinci liste ale verdictului 1d. Aplicația e gata pe acest criteriu când listele 3, 4 și 5 sunt goale pe fiecare regim; lista 2 poate avea conținut, fiindcă măsoară ce n-a completat contabilul, nu ce n-a făcut aplicația.
- **ce lipsește**: operațiunea 1 (câte regimuri), pasul **1a** (ce cere legea) și pasul **1b** (ce produce aplicația, pe **toate cele patru familii** — A, B, C, D) sunt MĂSURATE. Mai lipsesc, ca să se termine E1: **1c** (se poate verifica pe ecran — interdicțiile 63–66) · verdictul **1d** pe cele cinci liste · plus restanțele de mai jos — **numărul lor e derivat, nu scris aici**, fiindcă altfel ar fi al doilea loc unde trăiește aceeași stare. Cele care blochează cel mai mult: **R5** și **R6** (încrederea în corpusul pe care stă tot 1a). **R3 nu mai e pe listă** — se credea că blochează toată familia B; măsurătoarea din 22.08 a arătat că n-o bloca, iar restanța s-a îngustat la „nu se calculează”.
- **decizii care blochează**: **niciuna deschisă** — cea de la 1b (cele cinci liste vs cele trei cauze din P23) a fost luată pe 22.08: **lista 3 se lărgește**, nu se adaugă a șasea; cauza se scrie lângă artefact.
- **avertisment la cifre**: **NEÎNCEPUTE include interdicții măsurate în campanii anterioare, netransferate — vezi 3a din `PLAN_INVESTIGATII.md`.** Cel puțin zece au cifre în `GARZI.md` și `TESTE.md` și scriu NEÎNCEPUTĂ aici. Cifra e adevărată, dar arată mai multă muncă rămasă decât e.
- **ultima actualizare**: 2026-08-22
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
| **1.1** | **`de_preluat` înseamnă două lucruri opuse, iar D300 omite tăcut facturi emise** — GĂSIT AZI, prin experimentul de la R12 | **cifră greșită într-o declarație depusă.** `core/d300.py:50-52` tratează `de_preluat` ca **staging** și îl exclude din decont; `core/export_winmentor.py:17` scrie explicit *„'de_preluat' e starea NORMALĂ a facturii emise, nu una de exclus"*; iar `core/facturi_api.py:311` **creează facturile noi exact cu `status="de_preluat"`**. Măsurat: **4 facturi emise, la 3 plătitori de TVA, cu TVA colectată de 3.052,00 lei, nu intră în D300** (t003: 2 facturi / 889,00 · t005: 1 / 2.100,00 · t013: 1 / 63,00). Pe t013 decontul **nu e gol, e incomplet** — iese cu 18 operațiuni și o omite pe a 19-a, ceea ce e mai greu de văzut decât un zero |
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
- **stare**: DESCHISĂ
- **deschisă pe commit**: `45f15ab`
- **ce blochează**: Reglementările contabile (anexa OMFP 1802/2014) și Normele OMFP 2634/2015 sunt structurate pe **puncte**; `scripts/vigoare_articol.py` delimitează pe articole. Deci pentru familia B din 1a se cunoaște doar data consolidării actului, nu starea punctului folosit.
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

- **felul**: SURSĂ
- **cine deblochează**: DECIZIE
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
- **condiția de deblocare**: **două lucruri, în ordinea asta.** (1) Se decide dacă cele două funcții trebuie să producă **aceeași** stare — și atunci una dintre valori dispare — sau dacă distincția e reală și trebuie **numită** în nomenclator, nu dedusă din care funcție a fost chemată. (2) **Migrarea populațiilor existente**, care nu e opțională odată ce (1) s-a luat: pe cele trei firme amestecate, facturile din starea care dispare trebuie mutate, altfel decizia e adevărată doar pentru facturile viitoare. Se închide când ambele s-au făcut, nu doar prima.

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

---

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


### Ce lipsește ca să se termine E1

1. **1b — ce produce aplicația**, pe date reale, pentru fiecare artefact de mai sus, cu despicarea din
   P23 (date cerute la timp / necerute / artefact imposibil).
2. **1c — se poate verifica pe ecran** (interdicțiile 63–66).
3. **Categoria de mărime**, precondiție pentru familia B: nu există în aplicație.
4. **Vigoarea pentru cele cinci acte structurate pe puncte** (mai sus), care cere altă unitate de
   verificare decât articolul.

---

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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

## 8 — O schemă care interzice al doilea exemplar

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o schemă care interzice al doilea exemplar face corecția imposibilă: eroarea dintr-un document deja predat nu se mai poate îndrepta printr-un document nou, deci singura ieșire rămâne rescrierea celui vechi — adică interdicția 7, forțată de structură

## 9 — O afirmație fără domeniu sau fără surse

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o afirmație fără domeniu se citește peste șase luni ca adevăr permanent

## 10 — Un verdict favorabil care coexistă cu necunoscut nedeclarat

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: un verdict favorabil care ascunde necunoscutul îl face pe contabil să creadă că e verificat ce n-a fost verificat

## 11 — Un verificator care importă modulul verificat

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

## 13 — Un refuz cu nume interne sau fără diacritice

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: contabilul primește un refuz pe care nu-l poate acționa: un nume intern nu-i spune ce să completeze, iar mesajul arată ca un defect al aplicației. Efectul nu e o cifră greșită, e o cerere de ajutor către noi pentru ceva ce el putea rezolva singur

## 14 — Un parametru cu valoare implicită într-o funcție de calcul fiscal

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o valoare care stă pe un articol nereverificat poate fi greșită de luni de zile fără ca nimic să semnaleze, și ajunge direct în cifra depusă — nimic din lanțul automat nu întreabă de când n-a mai fost verificat

## 50 — O valoare sprijinită pe un articol abrogat sau modificat, fără succesor citat

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: corpusul afirmă un text pe care sursa nu-l mai are, iar toate verificările de deasupra — vigoare, citat, ierarhie — moștenesc eroarea fără s-o poată vedea

## 53 — Un citat verbatim care nu conține valoarea pe care o justifică

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: citarea e falsă chiar dacă actul e corect și în vigoare: o cotă sprijinită pe un citat în care valoarea nu apare. Trei instanțe cunoscute — facilitatea de 300 lei, cota de dividende, pragul mijloacelor fixe

## 54 — Un articol folosit cu verificarea vigorii expirată față de pragul lui

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: data de verificare devine formalitate: un articol verificat acum doi ani poartă o dată, deci trece poarta, și poate fi rescris de un an

## 55 — Un articol din corpus fără categorie de reverificare atribuită

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: se alege tăcut sursa mai comodă. Instanța: podeaua part-time — legea spune una, structura publicată de autoritate spune alta, s-a ales în cod; divergența e 70,25 lei pe lună, pe fiecare salariat part-time sub minim

## 59 — Verificarea vigorii făcută pe act, nu pe articolul folosit

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: verificarea trece mereu, fiindcă actul e în vigoare permanent, în timp ce articolul folosit poate fi abrogat separat. Instanța: OUG 156/2024 e în vigoare, dar art. LXX a fost abrogat de OUG 29/2026

## 60 — O regulă, formulă sau structură care implementează o normă, fără articolul asociat

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: la o modificare de lege nu se știe ce cod trebuie atins: se pot determina perioadele afectate, dar nu implementările. Fără 60, P18 nu se poate executa

## 61 — Un articol din corpus fără lista dependenților, generabilă la cerere

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: contabilul care nu poate desface o cifră are două opțiuni: să aibă încredere, sau s-o refacă în altă parte. A doua e mai frecventă, și atunci produsul nu i-a economisit munca, i-a adăugat una

## 64 — Un element care putea interveni și n-a intervenit, fără motiv și temei afișabile

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: o deducere neacordată, o facilitate pierdută, o scutire neaplicată sunt invizibile dacă ecranul arată doar ce s-a aplicat. O absență nemotivată nu se poate contesta, fiindcă nu se vede — și aici greșesc oamenii, nu la ce s-a calculat greșit

## 65 — O valoare diferită de perioada anterioară, fără explicația diferenței

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
- **unde ajunge efectul**: cel mai puternic instrument de verificare lipsește exact acolo unde ceva s-a mișcat: un contabil nu verifică o lună izolat, ci știind luna precedentă. Dacă un net diferă și nimeni nu spune de ce, verificarea se mută în afara aplicației

## 66 — O legătură normă↔implementare care există în cod, dar nu ajunge pe ecran

- **stare**: NEÎNCEPUTĂ
- **măsurat la**: —
- **pe commit**: —
- **cifra**: — (nemăsurată)
- **instanțe**: — (nemăsurate)
- **calibrare**: — (nu s-a rulat nicio măsurătoare, deci niciun caz cunoscut n-a fost găsit sau ratat)
- **ce nu vede**: — (nu există încă instrument, deci nu i se pot declara limitele)
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

