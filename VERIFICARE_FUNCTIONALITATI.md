# VERIFICARE_FUNCTIONALITATI.md — ce face aplicația când primește date greșite

**Comanda** (Costin, 03.09.2026): *„Probează fiecare funcționalitate, întâi cu invalide, apoi cu
valide… La invalide se urmărește un singur lucru: **aplicația vorbește**. Tăcerea e defect, chiar
dacă valoarea n-a intrat. Refuzul spune care câmp, ce e greșit, în termeni de contabil, cu temei
acolo unde aplică o regulă fiscală. Nu cade, nu dă 500, nu pierde ce s-a tastat, și nu confundă «e
invalid» cu «n-am putut verifica»."*

**Mesajele sunt VERBATIM.** Copiate din răspunsul aplicației, nerescrise ca să arate bine. Unde
mesajul e lung, e tăiat cu `…` și se spune că e tăiat.

**Perimetrul etapei 1** *(tăiat de Costin, 03.09.2026)*: numai suprafața prin care un om introduce
date — cele 75 de ecrane și cele 289 de rute cu câmpuri de completat. **364 de unități** din 553.
Ce a ieșit e marcat în `LISTA_FUNCTIONALITATI.md` cu motivul.

**Cum se probează.** `frontend_test/proba_verificare_functionalitati.py` — cereri reale către
aplicație, cu token emis pentru un utilizator real. Subiect: cabinetul 1968 (`Cabinet Contabil
Prisma SRL`), utilizator `patron@prisma-cont.test` (rol `admin_firma`), firma **4838 `Comert Micro
TVA SRL`** — plătitor de TVA cu **perioadă fiscală trimestrială**, ceea ce contează pentru trei
dintre probe. Reprobarea de după reparații rulează pe o instanță proaspătă (`--port 8011`), fiindcă
procesul de producție ține codul vechi până la repornire.

---

## LOT 1 — T01, drumul declarației (22 de probe INVALIDE pe 11 unități)

*Unitățile `#7`, `#10`, `#11`, `#16`, `#19` din T01 nu sunt aici: sunt rute fără câmpuri de
completat, ieșite din perimetrul etapei 1.*

| # | funcționalitate | ecran / rută | câmp | ce s-a introdus | ce a făcut aplicația | mesajul verbatim | temei legal | reparat | rezultat după reparație |
|---|---|---|---|---|---|---|---|---|---|
| 4 | Lista cozii de declarații | `GET /coada` | `stare` | invalid: `stare=INEXISTENT` | **TĂCERE** — `200` cu listă goală. „Nu există nimic în starea asta" arată identic cu „starea asta nu există" | `{"coada":[]}` | — | **DA** — `main.py:coada_lista` verifică filtrul contra `coada_api.STARI`, derivate din tabela de tranziții (nu o a doua listă scrisă de mână) | `422` · `{"detail":"stare necunoscută: 'INEXISTENT' (stările cozii: aprobata, depusa, la_senior, respinsa)"}` |
| 5 | Adăugare în coadă | `POST /coada` | `tenant_id` | invalid: `999999` | `404`, spune ce e | `{"detail":"tenant inexistent sau fără acces"}` | — | nu — răspunsul e corect și nu afirmă o cauză pe care n-o poate ști | neschimbat |
| 5 | Adăugare în coadă | `POST /coada` | `luna` | invalid: `luna=13` | **NUMEA ALT CÂMP** — se plângea de trimestrul pe care omul nu-l trimisese, și tăcea despre luna 13 | `{"detail":"trimestru invalid: None (aștept 1-4)"}` | regulă fiscală: perioada fiscală TVA (lunar/trimestrial) — **necitată**, vezi nota de sub tabel | **DA** — `declaratii_api`: o valoare **trimisă** și greșită se spune pe numele ei, indiferent de periodicitatea firmei; iar nepotrivirea de periodicitate primește propriul mesaj | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12); firma depune d300 TRIMESTRIAL: trimite trimestrul (1-4), nu luna"}` |
| 5 | Adăugare în coadă | `POST /coada` | `tip` | invalid: `tip=d999` | `422`, enumeră ce se poate | `{"detail":"tip declarație necunoscut: 'd999' (suportate: d100, d101, d107, d112, d177, d205, d207, d300, d301, d307, d311, d390, d394, d406, d710)"}` | — | nu — mesajul numește câmpul și dă lista completă | neschimbat |
| 5 | Adăugare în coadă | `POST /coada` | tot corpul | lipsă: `{}` | `422` cu răspunsul brut al bibliotecii: engleză, formă de structură, fără ce-i de făcut | `{"detail":[{"type":"missing","loc":["body","tenant_id"],"msg":"Field required","input":{}},{"type":"missing","loc":["body","tip"],…]}` *(tăiat)* | — | **DA** — `main.py`: refuzul de validare vorbește românește și numește câmpul, în forma pe care ecranul o știe deja citi (`detail = {mesaj, erori_campuri}`, contractul din `static/js/api.js`) | `422` · `{"detail":{"mesaj":"Cererea nu poate fi acceptată, 3 câmpuri: tenant_id — lipsește; tip — lipsește; an — lipsește.","erori_campuri":[{"camp":"tenant_id","mesaj":"lipsește"},{"camp":"tip","mesaj":"lipsește"},{"camp":"an","mesaj":"lipsește"}]}}` |
| 6 | Aprobarea unei declarații din coadă | `POST /coada/{id}/aproba` | `coada_id` | invalid: `999999` | `404`, dar mesajul era **codul intern**, nu o propoziție | `{"detail":"INEXISTENT"}` | — | **DA** — `coada_api`: cele patru locuri care întorceau codul gol poartă acum un mesaj | `404` · `{"detail":"declarația nu mai e în coadă (id 999999): a fost ștearsă, depusă de altcineva, sau id-ul e greșit"}` |
| 8 | Depunerea unei declarații | `POST /coada/{id}/depune` | `coada_id` | invalid: `999999` | **`403`** — „n-ai voie" în loc de „nu există", plus codul intern ca mesaj. Aceeași cerere pe `/aproba` răspundea `404`: două coduri pentru aceeași stare | `{"detail":"INEXISTENT"}` | — | **DA** — `main.py`: `INEXISTENT` cade pe `404`, ca la aprobare | `404` · `{"detail":"declarația nu mai e în coadă (id 999999): a fost ștearsă, depusă de altcineva, sau id-ul e greșit"}` |
| 9 | Respingerea unei declarații | `POST /coada/{id}/respinge` | `motiv` | invalid: `""` (șir gol) | `400`, spune și **de ce** e nevoie de motiv | `{"detail":"respingerea necesită un motiv (contabilul trebuie să știe ce să corecteze)"}` | — | nu — e chiar forma cerută: câmpul, ce e greșit, și pentru cine contează | neschimbat |
| 9 | Respingerea unei declarații | `POST /coada/{id}/respinge` | `motiv` | lipsă: câmp absent | `422` brut, în engleză | `{"detail":[{"type":"missing","loc":["body","motiv"],"msg":"Field required","input":{}}]}` | — | **DA** — același handler de validare | `422` · `{"detail":{"mesaj":"Cererea nu poate fi acceptată: motiv — lipsește.","erori_campuri":[{"camp":"motiv","mesaj":"lipsește"}]}}` |
| 12 | Ce declarații datorează o firmă | `GET /declaratii/tipuri` | `tenant_id` | invalid: `999999` | `404`, corect | `{"detail":"tenant inexistent sau fără acces"}` | — | nu | neschimbat |
| 13 | Generarea unei declarații | `POST /declaratii/{tip}` | `tip` | invalid: `d999` | `422`, enumeră ce se poate | `{"detail":"tip declarație necunoscut: 'd999' (suportate: d100, d101, …, d710)"}` *(tăiat)* | — | nu | neschimbat |
| 13 | Generarea unei declarații | `POST /declaratii/{tip}` | `luna` | invalid: `13` | numea alt câmp (v. `#5`) | `{"detail":"trimestru invalid: None (aștept 1-4)"}` | perioada fiscală TVA — **necitată** | **DA** — aceeași reparație | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12); firma depune d300 TRIMESTRIAL: trimite trimestrul (1-4), nu luna"}` |
| 13 | Generarea unei declarații | `POST /declaratii/{tip}` | `an` | invalid: `1900` | `422` — partea despre an era corectă, dar urma zgomotul despre trimestru | `{"detail":"an invalid: 1900 (aștept întreg 2020-2100); trimestru invalid: None (aștept 1-4)"}` | — | **DA** — indirect, prin aceeași reparație: a doua propoziție spune acum ce se așteaptă, nu că lipsește ceva ce omul n-a trimis | `422` · `{"detail":"an invalid: 1900 (aștept întreg 2020-2100); firma depune d300 TRIMESTRIAL: trimite trimestrul (1-4), nu luna"}` |
| 13 | Generarea unei declarații | `POST /declaratii/{tip}` | `an` | invalid: `"douamiidouazecisisase"` | `422` brut, în engleză | `{"detail":[{"type":"int_parsing","loc":["body","an"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"douamiidouazecisisase"}]}` | — | **DA** — handlerul de validare | `422` · `{"detail":{"mesaj":"Cererea nu poate fi acceptată: an — aștept un număr întreg, am primit 'douamiidouazecisisase'.","erori_campuri":[{"camp":"an","mesaj":"aștept un număr întreg, am primit 'douamiidouazecisisase'"}]}}` |
| 13 | Generarea unei declarații | `POST /declaratii/{tip}` | `tenant_id` | invalid: `999999` | **AFIRMAȚIE FALSĂ** — `403` cu „Nu ai acces la această firmă. Cere-i administratorului cabinetului să ți-o atribuie.": firma nu există, iar omul e trimis să ceară o atribuire imposibilă | `{"detail":"Nu ai acces la această firmă. Cere-i administratorului cabinetului să ți-o atribuie."}` | — | **DA** — `core/mesaje.FARA_ACCES_TENANT` nu mai afirmă o cauză pe care ruta n-o poate ști | `403` · `{"detail":"Firma nu există în portofoliu sau nu ți-e atribuită. Dacă există și ar trebui să lucrezi pe ea, cere-i administratorului cabinetului să ți-o atribuie."}` |
| 14 | Generare + validare la DUK | `POST /declaratii/{tip}/valideaza` | `luna` | invalid: `13` | numea alt câmp | `{"detail":"trimestru invalid: None (aștept 1-4)"}` | perioada fiscală TVA — **necitată** | **DA** — aceeași reparație | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12); firma depune d300 TRIMESTRIAL: trimite trimestrul (1-4), nu luna"}` |
| 14 | Generare + validare la DUK | `POST /declaratii/{tip}/valideaza` | `tip` | invalid: `d999` | `422`, corect | `{"detail":"tip declarație necunoscut: 'd999' (suportate: …)"}` *(tăiat)* | — | nu | neschimbat |
| 15 | Verificările contabile ale unei firme | `GET /firme/{id}/verificari` | `an`, `luna` | lipsă: ambii parametri | `422` brut | `{"detail":[{"type":"missing","loc":["query","an"],…},{"type":"missing","loc":["query","luna"],…}]}` *(tăiat)* | — | **DA** — handlerul de validare | `422` · `{"detail":{"mesaj":"Cererea nu poate fi acceptată, 2 câmpuri: an — lipsește; luna — lipsește.","erori_campuri":[{"camp":"an","mesaj":"lipsește"},{"camp":"luna","mesaj":"lipsește"}]}}` |
| 15 | Verificările contabile ale unei firme | `GET /firme/{id}/verificari` | `luna` | invalid: `13` | **A CONFUNDAT „E INVALID" CU „N-AM PUTUT VERIFICA"** — `200`, stare `gri`, „necunoaștere", *„NU pot verifica TVA: decontul nu se poate calcula (D300 lunar: luna invalidă: 13)"*, plus fereastra inventată *„trimestrul 5/2026"*. O intrare greșită îmbrăcată în risc neacoperit | `{"tva_incrucisat":{"an":2026,"luna":13,"stare":"gri","constatari":[{"fel":"necunoastere","tip":"d300","motiv":"NU pot verifica TVA: decontul nu se poate calcula (D300 lunar: luna invalidă: 13).",…}]},"d390_incrucisat":{…"fereastra":"trimestrul 5/2026"…}}` *(tăiat)* | — | **DA** — `main.py:firma_verificari` respinge `luna` în afara lui 1-12 și `an` în afara lui 2020-2100 **înainte** de a chema verificările | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 17 | Import istoric de declarații depuse | `POST /tenants/{id}/istoric-declaratii-import` | `randuri` | lipsă: `[]` | **PIERDERE DE DATE RAPORTATĂ CA SUCCES** — `200 {"importati":0}`. Lista goală trecea de verificare, ajungea la `DELETE … WHERE sursa='migrare'` și **ștergea tot istoricul importat al firmei**, fără să insereze nimic și fără să spună | `{"importati":0}` | — | **DA** — `istoric_declaratii_import_api.importa` refuză lista goală, și spune ce s-ar fi pierdut | `422` · `{"detail":"nu ai trimis niciun rând. Importul ar fi șters istoricul de declarații încărcat până acum pentru firma asta și n-ar fi pus nimic în loc. Dacă chiar vrei să golești istoricul importat, e altă operațiune."}` |
| 17 | Import istoric de declarații depuse | `POST /tenants/{id}/istoric-declaratii-import` | `randuri[0]` | invalid: `[{}]` | **CIFRĂ FALSĂ ÎN REFUZ** — un singur rând, iar mesajul spunea „2 rânduri nu pot intra" (număra erorile, nu rândurile). Omul caută al doilea rând | `{"detail":"2 rânduri nu pot intra: rand 2: ?: anul 0 e în afara intervalului; rand 2: ?: luna 0 (așteptat 1-12). Istoricul declarațiilor stă la baza termenelor și a controlului fiscal."}` | — | **DA** — se numără rândurile distincte, cu acordul gramatical | `422` · `{"detail":"Un rând nu poate intra: rand 2: ?: anul 0 e în afara intervalului; rand 2: ?: luna 0 (așteptat 1-12). Istoricul declarațiilor stă la baza termenelor și a controlului fiscal."}` |
| 18 | Încărcarea fișierului cu istoricul | `POST /tenants/{id}/istoric-declaratii-import/incarca` | `fisier` | invalid: `.txt` cu o linie de proză | `400`, spune ce coloană caută | `{"detail":"nu găsesc coloana cu tipul declarației (tip/declarație/formular) - fișier nerecunoscut"}` | — | nu — numește ce lipsește și cu ce nume o caută | neschimbat |

---

## LOT 1b — aceeași clasă: importurile care goleau la intrare vidă

**Cerut de Costin după lotul 1**, verbatim: *„Al optulea e altă clasă și se repară acum, nu la
final: `randuri=[]` nu e o listă de importat, e o cerere fără conținut. Se refuză, nu se execută. Un
import care nu aduce nimic nu are voie să șteargă ce era acolo, iar «importati: 0» arată identic cu
un import inofensiv — contabilul nu are cum să afle că a pierdut istoricul. Verifică apoi dacă mai
există alte căi de import sau de înlocuire care golesc la intrare vidă."*

**Cum le-am căutat, mecanic:** `DELETE FROM <tabel>` **fără `WHERE`** în modulele care importă. Sunt
**patru în tot `core/`** — cea din lotul 1 plus cele trei de mai jos. Restul ștergerilor poartă un
`WHERE id=…` sau `WHERE tenant_id=…`, deci sunt țintite, nu golesc.

**Toate trei aveau exact aceeași gaură, și una în plus față de prima:** parserul de fișier are deja
o pază pe fișierul gol, dar `extrage()` întoarce `[]` și pentru un fișier **numai cu antet** — iar de
acolo până la `DELETE` nu mai era nimic. Plus calea de API, care primește lista direct.

| # | funcționalitate | ecran / rută | câmp | ce s-a introdus | ce a făcut aplicația | mesajul verbatim | temei legal | reparat | rezultat după reparație |
|---|---|---|---|---|---|---|---|---|---|
| 148 | Import asociați (migrare) | `POST /tenants/{id}/asociati-import` | `randuri` | lipsă: `[]` | **ștergea toți asociații firmei** (`DELETE FROM asociati`) și raporta import reușit cu zero rânduri | *(înainte de reparație: `200` cu rezultatul importului, fără niciun cuvânt despre ștergere)* | — | **DA** — gardă la intrarea în `importa`, cu ce s-ar fi pierdut scris în mesaj | `422` · `{"detail":"nu ai trimis niciun rând. Importul ar fi șters lista de asociați a firmei, cu cotele lor de participare, și n-ar fi pus nimic în loc. Dacă chiar vrei să golești lista, e altă operațiune."}` |
| 150 | Import mijloace fixe (migrare) | `POST /tenants/{id}/mijloace-fixe-import` | `randuri` | lipsă: `[]` | **ștergea registrul mijloacelor fixe** (`DELETE FROM mijloace_fixe`) — cel pe care stă amortizarea | *(idem)* | — | **DA** | `422` · `{"detail":"nu ai trimis niciun rând. Importul ar fi șters registrul mijloacelor fixe al firmei — cel pe care stă amortizarea — și n-ar fi pus nimic în loc. Dacă chiar vrei să golești registrul, e altă operațiune."}` |
| 153 | Salvarea soldurilor de parteneri | `POST /tenants/{id}/parteneri` | `randuri` | lipsă: `[]` | **ștergea soldurile inițiale ale partenerilor** (`DELETE FROM solduri_parteneri`). Docstringul rutei spune „înlocuiește ce era" — dar o înlocuire cu nimic e o ștergere, nu o înlocuire | *(idem)* | — | **DA** | `422` · `{"detail":"nu ai trimis niciun rând. Importul ar fi șters soldurile inițiale ale partenerilor și n-ar fi pus nimic în loc. Dacă chiar vrei să le golești, e altă operațiune."}` |

**De ce n-am scris mesajul verbatim „înainte" pentru cele trei:** nu le-am probat înainte de
reparație. Le-am găsit citind codul, pe clasa dată de Costin, iar o probă „înainte" ar fi însemnat să
**șterg efectiv** asociații, mijloacele fixe și soldurile firmei de probă ca să constat ce știam deja
din cod. Ce s-a probat, și e scris mai sus, e **starea de după**. *Portofoliul e fictiv și n-aveam
ce ocroti — dar o ștergere pe care o pot prezice din cod nu devine mai adevărată dacă o fac.*

**Clasa, scrisă ca să se recunoască data viitoare:** *o operațiune de înlocuire care primește un set
vid nu are voie să execute partea de ștergere.* Semnul ei în cod e `DELETE` fără `WHERE` urmat de un
`INSERT` într-o buclă peste ceva ce poate fi gol; semnul ei în răspuns e un succes care nu numește
ce a dispărut.

### Ce a rămas nereparat din lotul ăsta, și de ce

1. **Temeiul legal al periodicității nu e citat.** Mesajul *„firma depune d300 TRIMESTRIAL"* aplică o
   regulă fiscală — perioada fiscală a TVA —, iar comanda cere temei acolo unde se aplică una. Nu am
   pus niciun articol, fiindcă **nu l-am verificat la sursă în tura asta**, iar un temei citat din
   memorie e mai rău decât unul absent: intră în corpus ca fapt. Rămâne de făcut la prima trecere
   prin lotul de declarații, cu verificarea la sursă.
2. **`403` la firmă inexistentă pe `/declaratii/{tip}`, `404` pe `/coada`.** Mesajul nu mai minte pe
   niciuna, dar codul rămâne diferit pentru aceeași stare. N-am uniformizat: alegerea între „nu
   divulg dacă firma există" (`403`) și „nu există" (`404`) e transversală, atinge zeci de rute și
   testele lor, și nu se ia dintr-un lot de 22 de probe.
3. **`rand 2` pentru primul rând trimis prin API.** Numerotarea pornește de la 2 fiindcă drumul
   normal e un fișier cu antet, unde „rândul 2" e chiar prima linie de date. Pe calea JSON arată
   ciudat, dar corectarea ar strica mesajul pe calea care se folosește de fapt.

### Cifre

- probe INVALIDE rulate: **22**, pe **11 unități** · defecte găsite: **8** · reparate: **8** ·
  reprobate: **8**, toate schimbate.
- clase de defect: tăcere (1) · cod intern ca mesaj (2) · mesaj care numește alt câmp (4 probe, o
  cauză) · afirmație falsă (1) · „invalid" confundat cu „n-am putut verifica" (1) · cifră falsă în
  refuz (1) · **pierdere de date raportată ca succes (1)** · răspuns brut al bibliotecii (4 probe, o
  cauză).
- niciun `500`, nicio cădere, nicio cerere fără răspuns.

---

## LOT 2 — T02, factura emisă (37 de probe INVALIDE pe 11 unități)

*Unitățile `#24`, `#26`, `#29`, `#32`, `#33`, `#36`, `#37`, `#38`, `#39` din T02 nu sunt aici: sunt
rute fără câmpuri de completat, ieșite din perimetrul etapei 1.*

**Ce s-a lăsat în urmă, măsurat:** nimic. Numerotarea firmei se citește înainte și se pune la loc
în `finally`; cheia de API se emite prin `POST /cabinet/api-chei` (lanțul aplicației, nu un
`INSERT`), se revocă și rândul ei se șterge. Verificat după ultima trecere: `facturi` = 3 (aceleași
id-uri 1, 2, 3), `serie=CMT`, `urmator_numar=150`, `public.api_chei` = 0 — exact starea de dinainte.

**Prima trecere a lăsat, însă, urme — și au fost refăcute.** Trei probe *au trecut* (cota 99% de
două ori, numărul duplicat o dată) și au creat facturile 5, 6, 7 cu notele lor; iar refacerea
numerotării a eșuat tăcut (v. „defectele hamului", mai jos), lăsând firma fără serie și cu contorul
la 101. Cele trei facturi s-au șters **din bază**, nu prin aplicație: `DELETE /facturi/{id}` le
refuză — corect — fiindcă au notă, iar stornarea ar fi adăugat alte trei documente false într-o
firmă care e subiect de măsurătoare.

| # | funcționalitate | ecran / rută | câmp | ce s-a introdus | ce a făcut aplicația | mesajul verbatim | temei legal | reparat | rezultat după reparație |
|---|---|---|---|---|---|---|---|---|---|
| 22 | Lista facturilor | `GET /tenants/{id}/facturi` | `luna` | invalid: `an=2026&luna=13` | **A CĂZUT** — `500`. Intervalul se construia ca „2026-13-01 … 2026-14-01" și pica în driver | `Internal Server Error` | — | **DA** — `facturi_api.lista_facturi` verifică filtrele înainte de a atinge SQL-ul; ruta traduce `ValueError` în `422` | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 22 | Lista facturilor | `GET /tenants/{id}/facturi` | `limit` | invalid: `limit=-5` | **A CĂZUT** — `500`. Ajungea în `LIMIT -5`, refuzat de Postgres | `Internal Server Error` | — | **DA** — aceeași gardă de filtre | `422` · `{"detail":"limit invalid: -5 (aștept un număr pozitiv, sau nimic pentru tot)"}` |
| 22 | Lista facturilor | `GET /tenants/{id}/facturi` | `directie` | invalid: `directie=lateral` | **TĂCERE** — `200` cu listă goală. „Nu există facturi așa" arăta identic cu „direcția asta nu există"; exact clasa scoasă din `GET /coada` în lotul 1 | `{"facturi":[]}` | — | **DA** — filtrul respinge acum exact ce respinge și crearea: nomenclatorul `DIRECTII`, o singură sursă | `422` · `{"detail":"direcție necunoscută: 'lateral' (direcțiile facturii: emisa, primita)"}` |
| 22 | Lista facturilor | `GET /tenants/{id}/facturi` | `an` | invalid: `an=anul-trecut` | `422` românește, prin handlerul din lotul 1 | `{"detail":{"mesaj":"Cererea nu poate fi acceptată: an — aștept un număr întreg, am primit 'anul-trecut'.",…}}` | — | nu | neschimbat |
| 23 | Crearea unei facturi | `POST /tenants/{id}/facturi` | tot corpul | lipsă: `{}` | `422`, enumeră cele patru câmpuri | `{"detail":{"mesaj":"Cererea nu poate fi acceptată, 4 câmpuri: numar — lipsește; data_emitere — lipsește; directie — lipsește; linii — lipsește.",…}}` | — | nu | neschimbat |
| 23 | Crearea unei facturi | `POST /tenants/{id}/facturi` | `linii` | invalid: `[]` | `422`, corect | `{"detail":"factura trebuie să aibă cel puțin o linie"}` | — | nu | neschimbat |
| 23 | Crearea unei facturi | `POST /tenants/{id}/facturi` | `directie` | invalid: `lateral` | `422`, corect | `{"detail":"Direcția facturii trebuie să fie 'emisă' sau 'primită'."}` | — | nu | neschimbat |
| 23 | Crearea unei facturi | `POST /tenants/{id}/facturi` | `data_emitere` | invalid: `2026-02-31` | **A CĂZUT** — `500`. Data mergea neatinsă până în `INSERT`; o zi care nu există în calendar e o greșeală de tastare, nu o cădere | `Internal Server Error` | — | **DA** — `_data_ceruta` verifică ambele date și spune care câmp | `422` · `{"detail":"data emiterii: '2026-02-31' nu e o dată din calendar. Aștept forma AAAA-LL-ZZ, cu o zi care există în luna aia."}` |
| 23 | Crearea unei facturi | `POST /tenants/{id}/facturi` | `linii[].cota_tva` | invalid: `99` | **VALOARE FISCALĂ INEXISTENTĂ, ACCEPTATĂ ȘI CONTABILIZATĂ** — `200`: factura s-a creat *și* și-a primit nota, cu `4427 = 99,00 lei`. O cotă care nu există în legea română intra în evidență fără o vorbă | `{"ok":true,"factura_id":5,"total":199.0,"tva":99.0,"contare":{…"linii":[{"debit":"4111","credit":"4427","suma":"99.00"}]}}` | **art. 291 Cod fiscal**, prin registrul `common.COTE` — period-aware, nu o listă scrisă de mână | **DA** — `common.cote_tva_in_vigoare(data)` derivă cotele din registru, cu temeiurile lor; `creeaza_factura` refuză ce nu era în lege **la data facturii** | `422` · `{"detail":"Linia 'consultanta' are cota de TVA 99.0%, care nu există în legea română la data facturii (2026-09-03). Cotele de atunci: 0%, 11.00%, 21.00%. Temei: Legea 141/2025 art.291 alin.(1); Legea 141/2025 art.291 alin.(2); Legea 141/2025 art.291 alin.(3)."}` |
| 23 | Crearea unei facturi | `POST /tenants/{id}/facturi` | `numar` | invalid: `CMT149`, deja pe factura 3 | **AL DOILEA DOCUMENT CU ACELAȘI NUMĂR** — `200`. Două facturi emise cu numărul CMT149 | `{"ok":true,"factura_id":6,"total":121.0,…}` | **OMFP 2634/2015, Anexa 1, pct. 24** — verificat la sursă în corpus, verbatim | **DA** — un număr deja folosit pe o factură **emisă** se refuză și se spune pe ce e | `422` · `{"detail":"Numărul CMT149 e deja pe factura #3. Două documente emise cu același număr rup secvența cerută de OMFP 2634/2015 art.anexa 1 lit.pct. 24. Dacă documentul dinainte e greșit, se stornează — nu se reia numărul."}` |
| 25 | Șablon de factură recurentă | `POST /tenants/{id}/facturi-recurente` | tot corpul | lipsă: `{}` | `422`, dar mesajul era o notiță, nu un refuz: nu numea câmpul și nu spunea ce se pierde | `{"detail":"cel puțin o linie"}` | — | **DA** — mesaj întreg, cu câmpul field-keyed pentru ecran | `422` · `{"detail":{"mesaj":"Șablonul trebuie să aibă cel puțin o linie de facturat (denumire, cantitate, preț). Fără ele, factura lunară n-ar avea ce emite.","erori_campuri":[{"camp":"fr-linii","mesaj":"cel puțin o linie"}]}}` |
| 25 | Șablon de factură recurentă | `POST /tenants/{id}/facturi-recurente` | `zi_emitere` | invalid: `45` | `422`, corect | `{"detail":"Ziua emiterii trebuie să fie între 1 și 28."}` | — | nu | neschimbat |
| 25 | Șablon de factură recurentă | `POST /tenants/{id}/facturi-recurente` | `zi_emitere` | invalid: `"prima"` | **A CĂZUT** — `500`, din `int("prima")` | `Internal Server Error` | — | **DA** — un câmp completat cu litere e greșeală de tastare, nu cădere | `422` · `{"detail":{"mesaj":"Ziua emiterii: 'prima' nu e un număr. Aștept o zi între 1 și 28.","erori_campuri":[{"camp":"fr-zi_emitere","mesaj":"aștept un număr între 1 și 28"}]}}` |
| 27 | Comutarea unui șablon | `PUT /tenants/{id}/facturi-recurente/{sid}` | `activ` | lipsă | `422` românește | `{"detail":{"mesaj":"Cererea nu poate fi acceptată: activ — lipsește.",…}}` | — | nu | neschimbat |
| 27 | Comutarea unui șablon | `PUT /tenants/{id}/facturi-recurente/{sid}` | `activ` | invalid: `poate` | `422` românește | `{"detail":{"mesaj":"Cererea nu poate fi acceptată: activ — aștept da/nu, am primit 'poate'.",…}}` | — | nu | neschimbat |
| 27 | Comutarea unui șablon | `PUT /tenants/{id}/facturi-recurente/{sid}` | `sid` | invalid: `999999` | `404`, dar telegrafic și **fără diacritice** — text afișat scris ca marker | `{"detail":"sablon inexistent"}` | — | **DA** — propoziție, cu id-ul și cu ce s-a putut întâmpla | `404` · `{"detail":"Șablonul de factură recurentă cu id 999999 nu există (a fost șters, sau id-ul e greșit)."}` |
| 28 | Emiterea unei facturi | `POST /tenants/{id}/facturi/emite` | tot corpul | lipsă: `{}` | `422` românește | `{"detail":{"mesaj":"Cererea nu poate fi acceptată: linii — lipsește.",…}}` | — | nu | neschimbat |
| 28 | Emiterea unei facturi | `POST /tenants/{id}/facturi/emite` | `tert_nume` | invalid: `""` | `422`, corect | `{"detail":"Denumirea beneficiarului e obligatorie pe factură. Completeaz-o înainte de emitere."}` | — | nu | neschimbat |
| 28 | Emiterea unei facturi | `POST /tenants/{id}/facturi/emite` | `linii` | invalid: `[]` | **NUMEA ALT CÂMP** — refuzul vorbea despre codul fiscal al partenerului, fiindcă `cere_cod_partener` rula ÎNAINTE de a se uita la linii | `{"detail":"Factura nu se poate salva fără codul fiscal al partenerului (Proba SRL)…"}` *(tăiat)* | — | **DA** — ORDINEA: liniile întâi, codul de partener după. Aceeași clasă ca „trimestru invalid: None" din lotul 1 | `422` · `{"detail":"Factura trebuie să aibă cel puțin o linie."}` |
| 28 | Emiterea unei facturi | `POST /tenants/{id}/facturi/emite` | `linii[].cantitate` | invalid: `-5` | **NUMEA ALT CÂMP** — același refuz despre codul de partener | `{"detail":"Factura nu se poate salva fără codul fiscal al partenerului (Proba SRL)…"}` *(tăiat)* | — | **DA** — aceeași reparație de ordine | `422` · `{"detail":{"cod":"LINII_INCOMPLETE","mesaj":"Completează liniile: Linia 1: cantitate","campuri":[{"camp":"em-l0-cantitate","eticheta":"Linia 1: cantitate"}]}}` |
| 28 | Emiterea unei facturi | `POST /tenants/{id}/facturi/emite` | `moneda` | invalid: `XYZ` | **A CONFUNDAT „E INVALID" CU „N-AM PUTUT VERIFICA"** — `409`, *„Cursul BNR nu e disponibil momentan."* Pentru o monedă care nu există, „momentan" îl trimite pe contabil să reîncerce ceva ce nu va reuși niciodată — sau, mai rău, să introducă un **curs manual** și să bage factura în evidență pe o monedă inventată. *(Găsit abia la a doua trecere: prima probă era oarbă — v. mai jos)* | `{"detail":{"ok":false,"cod":"CURS_INDISPONIBIL","moneda":"XYZ","data":"2026-09-03","mesaj":"Cursul BNR nu e disponibil momentan."}}` | — | **DA** — `curs_bnr.MonedaNecotata` (subclasă, deci `except` de dinainte rămâne valabil) deosebește „moneda nu e în nomenclatorul BNR" de „cursul nu se poate lua acum"; ruta răspunde `422`, nu `409` | `422` · `{"detail":{"ok":false,"cod":"MONEDA_NECOTATA","moneda":"XYZ",…,"mesaj":"Moneda 'XYZ' nu e cotată de BNR, deci factura nu se poate exprima în lei. Verifică simbolul (trei litere, ex. EUR, USD). Monedele din ultimul nomenclator citit de la BNR: AED, AUD, …, ZAR."}}` *(tăiat)* |
| 30 | Seria și numărul facturilor | `PUT /tenants/{id}/facturi/numerotare` | tot corpul | lipsă: `{}` | `400` cu o notiță internă | `{"detail":"nimic de setat"}` | — | **DA** — propoziție | `400` · `{"detail":"Nu ai trimis nici seria, nici numărul de start, deci n-am ce schimba în numerotarea facturilor."}` |
| 30 | Seria și numărul facturilor | `PUT /tenants/{id}/facturi/numerotare` | `numar_start` | invalid: `-5` | **ACCEPTAT TĂCUT** — `200 {"ok":true}`. Numărul următoarei facturi devenea `-5` | `{"ok":true}` | **OMFP 2634/2015, Anexa 1, pct. 24** | **DA** | `400` · `{"detail":"Numărul de start trebuie să fie cel puțin 1; am primit -5. Numerotarea documentelor pornește de la 1, nu de la zero sau de la un număr negativ (OMFP 2634/2015 art.anexa 1 lit.pct. 24)."}` |
| 30 | Seria și numărul facturilor | `PUT /tenants/{id}/facturi/numerotare` | `numar_start` | invalid: `100`, sub cel atins (150) | **ACCEPTAT TĂCUT** — `200 {"ok":true}`. Contorul dat înapoi peste numere deja emise; **probat**: următoarea emitere prin API a produs documentul „100" | `{"ok":true}` | **OMFP 2634/2015, Anexa 1, pct. 24** | **DA** — un număr mai mic decât cel atins se refuză, cu ambele cifre în mesaj | `400` · `{"detail":"Numărul de start 100 e sub cel la care a ajuns seria (150). Dat înapoi, următoarea factură ar primi un număr deja emis, iar secvența cerută de OMFP 2634/2015 art.anexa 1 lit.pct. 24 s-ar rupe. Un număr mai mare sau egal se acceptă."}` |
| 30 | Seria și numărul facturilor | `PUT /tenants/{id}/facturi/numerotare` | `serie` | invalid: `"   "` | **PIERDERE TĂCUTĂ** — `200 {"ok":true}`, iar `strip() or None` ștergea seria firmei. Probat: factura emisă după avea `"serie":null` | `{"ok":true}` | — | **DA** — o serie goală nu se poate deosebi de o greșeală de tastare, deci nu se ghicește | `400` · `{"detail":"Seria e goală (numai spații). Nu se poate ghici dacă ai vrut s-o ștergi sau ai greșit tastarea, iar seria firmei e pe documentele deja emise."}` |
| 31 | Detaliile unei facturi | `GET /tenants/{id}/facturi/{fid}` | `factura_id` | invalid: `999999` | `404`, spune ce e | `{"detail":"factură inexistentă"}` | — | nu — v. observația de sub tabel | neschimbat |
| 34 | Trimiterea facturii pe email | `POST /tenants/{id}/facturi/{fid}/email` | `email` | invalid: `nu-e-o-adresa` | `422`, cu exemplu | `{"detail":"Adresă de email invalidă. Verifică formatul (exemplu: nume@exemplu.ro)."}` | — | nu | neschimbat |
| 34 | Trimiterea facturii pe email | `POST /tenants/{id}/facturi/{fid}/email` | `factura_id` | invalid: `999999`, adresă validă | `404` **înainte** de orice trimitere | `{"detail":"factură inexistentă"}` | — | nu | neschimbat |
| 35 | Supapa de notificare | `PUT /tenants/{id}/facturi/{fid}/notificare` | `factura_id` | invalid: `999999` | `404`, corect | `{"detail":"factură inexistentă"}` | — | nu | neschimbat |
| 35 | Supapa de notificare | `PUT /tenants/{id}/facturi/{fid}/notificare` | `amanata_pana` | invalid: `"maine"` | **A CĂZUT** — `500`. Data mergea neatinsă în `UPDATE` | `Internal Server Error` | — | **DA** — se verifică unde se poate spune care câmp | `422` · `{"detail":"data amânării: 'maine' nu e o dată din calendar. Aștept forma AAAA-LL-ZZ."}` |
| 20 | Lista facturilor, prin API | `GET /api/v1/firme/{id}/facturi` | antetul `X-Api-Key` | lipsă | `401`, spune ce lipsește | `{"detail":"lipsă X-Api-Key"}` | — | nu | neschimbat |
| 20 | Lista facturilor, prin API | `GET /api/v1/firme/{id}/facturi` | `X-Api-Key` | invalid: cheie inventată | `401`, și nu spune care din două | `{"detail":"cheie invalidă sau revocată"}` | — | nu | neschimbat |
| 20 | Lista facturilor, prin API | `GET /api/v1/firme/{id}/facturi` | `luna` | invalid: `13` | **A CĂZUT** — `500`, aceeași cauză ca `#22` | `Internal Server Error` | — | **DA** — aceeași gardă, plus traducerea `ValueError` → `422` și pe calea de API | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 20 | Lista facturilor, prin API | `GET /api/v1/firme/{id}/facturi` | `tenant_id` | firma **34061**, a altui cabinet | **AFIRMAȚIE FALSĂ** — `404` „firmă inexistentă", deși firma există; aceeași clasă scoasă din `FARA_ACCES_TENANT` în lotul 1 | `{"detail":"firmă inexistentă"}` | — | **DA** — forma de acum nu deosebește cele două stări, deci nici nu divulgă care e | `404` · `{"detail":"Firma nu există sau nu e în portofoliul cabinetului căruia îi aparține cheia de API folosită."}` |
| 21 | Emiterea prin API | `POST /api/v1/firme/{id}/facturi` | tot corpul | lipsă: `{}` | `422`, numește primul câmp lipsă | `{"detail":"Denumirea beneficiarului e obligatorie pe factură."}` | — | nu — v. observația de sub tabel | neschimbat |
| 21 | Emiterea prin API | `POST /api/v1/firme/{id}/facturi` | `linii` | invalid: `[]` | **A CĂZUT** — `500`. Ruta din ecran traducea de mult `ValueError` în `422`; asta, nu | `Internal Server Error` | — | **DA** — același contract de refuz ca ruta din ecran, inclusiv `LINII_INCOMPLETE` | `422` · `{"detail":"Factura trebuie să aibă cel puțin o linie."}` |
| 21 | Emiterea prin API | `POST /api/v1/firme/{id}/facturi` | `linii[].cota_tva` | invalid: `99` | **ACEEAȘI ACCEPTARE** ca la `#23`, pe a doua cale | `{"ok":true,"factura_id":7,…,"numar":"100","serie":null}` | art. 291 Cod fiscal | **DA** — reparația e în `creeaza_factura`, prin care trec amândouă căile | `422` · *(identic cu `#23`)* |

### Defectele HAMULUI, nu ale aplicației — se scriu, fiindcă amândouă au falsificat o măsurătoare

1. **Refacerea numerotării citea alte chei decât cele întoarse de rută** (`serie_factura` /
   `urmator_numar_factura`, numele coloanelor, în loc de `serie` / `urmator_numar`). Trimitea două
   `None`, primea „nimic de setat", **și tipărea că a pus la loc**. Firma a rămas fără serie și cu
   contorul la 101. Reparat, și `finally` verifică acum **starea**, nu că a trimis cererea: *un
   `finally` care raportează că a încercat, nu că a reușit, e chiar felul în care s-a pierdut seria.*
2. **Proba monedei era oarbă.** Trimitea `tert_nume` fără `tert_cui`, deci emiterea se oprea —
   legitim — la codul de partener, iar ce notasem ca „mesaj despre alt câmp" era răspunsul la altă
   întrebare. Cu codul completat, proba a ajuns la monedă și a scos al optulea defect din listă.
   *Aceeași clasă ca „sonda era oarbă: token de alt cabinet" din 31.08.*

### Ce a rămas nereparat din lotul ăsta, și de ce

1. **„factură inexistentă" nu poartă id-ul.** Apare în șapte locuri din `main.py`, e adevărat și
   numește obiectul, deci nu intră în niciuna dintre clasele comenzii. Ar fi mai bun cu id-ul, ca
   refuzul cozii din lotul 1 — dar e o îmbunătățire transversală, nu un defect al lotului.
2. **`POST /api/v1/.../facturi` cu corp gol numește un singur câmp** (beneficiarul), pe când ruta
   din ecran le enumeră pe toate. Nu e fals — beneficiarul chiar lipsește —, dar cele două căi
   răspund diferit la aceeași intrare. Nereparat: ordinea verificărilor de pe calea de API e o
   alegere, nu o scăpare, iar schimbarea ei atinge contractul integratorului.
3. **Fluxul XML al BNR nu mai răspunde** — măsurat azi: `nbrfxrates10days.xml` dă `302` către pagina
   de start, iar ultima zi din cache e **10.07.2026**. Consecința e mai mare decât lotul: nicio
   factură în valută nu-și mai poate lua cursul, iar pentru monedele din cache se folosește tăcut
   **cel mai recent curs de dinaintea datei**, adică unul vechi de aproape două luni. **Restanță
   EXTERNĂ**, scrisă în `CONFORMITATE.md`: cere aflarea noii adrese oficiale la sursă, la BNR.
4. **`core/facturi_api.py` refuză în 19 locuri fără să spună pe ce se sprijină** — măsurat azi,
   cu `scripts/scan_refuzuri`, fiindcă poarta l-a scos la iveală. Primul `Temei` scris în modul l-ar
   fi mutat din **umbră** în **datoria normei 77**, care sare de la 0 la **17**, iar norma cere ca un
   modul care *începe* să citeze legea să nu aibă niciunul. Temeiul numerotării a fost pus în
   `core/common.py` — locul canonic, unde stau toate celelalte (registrul `COTE`), și de unde
   `facturi_api` importă oricum cotele. *Cifra se scrie aici tocmai ca mutarea să nu treacă drept
   dispariție: cele 19 sunt în umbră, unde erau și înainte, și de acolo se pot plăti.*
5. **Garda de diacritice nu vede un `raise ValueError("…")` direct.** Două dintre mesajele reparate
   azi („factura trebuie sa aiba…", „sablon inexistent") erau text afișat fără diacritice și au
   trecut prin poartă. Garda se uită la `HTTPException`, la cheile de afișare din dicționare și la
   corpul **subclaselor** de excepție — nu la un `ValueError` ridicat direct, al cărui mesaj ajunge
   totuși la om prin `except ValueError → 422`. Consemnat, nu lărgit: lărgirea unei gărzi e o temă.

### Cifre

- probe INVALIDE rulate: **37**, pe **11 unități** · defecte găsite: **19** · reparate: **19** ·
  reprobate: **19**, toate schimbate. Cele 19 s-au arătat pe **21 de probe** (două cauze au câte
  două probe fiecare); al nouăsprezecelea — un mesaj afișat fără diacritice — n-a avut probă
  proprie: a ieșit la iveală pe **rezultatul unei reprobări**, adică pe textul cu care aplicația
  răspundea după prima reparație.
- distribuția răspunsurilor la ultima trecere: **26 × 422 · 5 × 404 · 4 × 400 · 2 × 401 · 0 × 500 ·
  0 × 200**. Înainte: **7 × 500** și **6 × 200** (dintre care trei scriau în baza de date).
- clase de defect: **cădere `500`** (7 probe, 6 cauze) · **tăcere** (1) · **valoare fiscală
  inexistentă acceptată și contabilizată** (2 probe, 1 cauză) · **al doilea document cu același
  număr** (1) · **numerotare primită fără verificare** (3) · **mesaj care numește alt câmp** (2
  probe, 1 cauză) · **afirmație falsă** (2) · **refuz telegrafic sau fără diacritice** (4).
- două dintre reparații poartă **temei verificat la sursă în tura asta**: cotele de TVA prin
  registrul `common.COTE` (art. 291 Cod fiscal) și numerotarea secvențială prin
  `anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt`, pct. 24, citit verbatim.
