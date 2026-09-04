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

---

## LOT 3 — T05, nota contabilă (53 de probe INVALIDE pe 32 de unități)

*Unitățile `#59` și `#62` din T05 nu sunt aici: sunt rute fără câmpuri de completat, ieșite din
perimetrul etapei 1. Rămân **32 din 34**.*

**Cum s-a probat o suprafață atât de largă.** Nouăsprezece dintre cele 32 sunt note speciale —
`POST /tenants/{id}/nota-<fel>` —, toate cu aceeași formă: corp liber cu `data` plus un discriminator
(`operatie` sau `fel`), toate trecând prin același `_cere_luna_deschisa`. Proba de bază e aceeași
pentru toate nouăsprezece, tocmai fiindcă **un defect în punctul comun se vede numai probându-le pe
toate**; patru dintre ele au primit și probe de adâncime (dată invalidă, discriminator inexistent,
sumă negativă). Restul de 13 unități — balanțe, jurnal, fișă de cont, registru-inventar, plan de
conturi — au fost probate una câte una.

**Ce s-a lăsat în urmă:** nimic. Verificat după ultima trecere: `facturi` 3, `inregistrari` 4,
`plan_conturi` 185, `api_chei` 0 — exact starea de dinainte. Prima trecere lăsase **o notă** (`#58`)
și **un cont „ABC" în planul firmei** (`#83`), amândouă produse de probe care AU TRECUT; s-au șters
din bază și se spune aici că s-au șters.

| # | funcționalitate | ecran / rută | câmp | ce s-a introdus | ce a făcut aplicația | mesajul verbatim | temei legal | reparat | rezultat după reparație |
|---|---|---|---|---|---|---|---|---|---|
| 57 | Registrul-jurnal, pe lună | `GET /tenants/{id}/jurnal` | `luna` | invalid: `13` | **A CĂZUT** — `500` | `Internal Server Error` | — | **DA** — `_cere_perioada`, ajutor comun pentru toate cele șapte rute care primesc o perioadă | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 57 | Registrul-jurnal, pe lună | `GET /tenants/{id}/jurnal` | `an` | invalid: `1900` | **TĂCERE** — `200`, jurnal gol. „Nu s-a înregistrat nimic în 1900" arăta identic cu „1900 nu e un an de lucru" | `{"note":[],"total_debit":0.0,"total_credit":0.0,"note_fara_document":0}` | — | **DA** — același ajutor | `422` · `{"detail":"an invalid: 1900 (aștept 1990-2100)"}` |
| 54 | Balanța ca date | `GET /tenants/{id}/balanta` | `luna` | invalid: `13` | **TĂCERE CU AFIRMAȚIE** — `200`, balanță goală, **și** `"stare":"nimic_de_verificat"` cu trei perechi „închise". O lună care nu există primea un verdict de echilibru | `{"randuri":[],"totaluri":{…},"inchidere":{"stare":"nimic_de_verificat","perechi":[{"ce":"sold initial",…"inchisa":true},…]}}` *(tăiat)* | — | **DA** | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 55 | Balanța ca document | `GET /tenants/{id}/documente/balanta` | `luna` | invalid: `0` | **A GENERAT UN PDF** — `200`, `%PDF-1.4`. Un document contabil, tipăribil, pentru luna zero | *(corpul e un PDF)* | — | **DA** | `422` · `{"detail":"luna invalidă: 0 (aștept 1-12)"}` |
| 53 | Balanța, prin API | `GET /api/v1/firme/{id}/balanta` | `luna` | invalid: `13` | **TĂCERE** — `200` `{"balanta":[]}` | `{"balanta":[]}` | — | **DA** — aceeași gardă și pe calea integratorului | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 84 | Registrul-inventar | `GET /tenants/{id}/registru-inventar` | `exercitiu` | invalid: `1900` | **TĂCERE CU TEMEI CITAT** — `200`, registru gol, cu `temei_obligatie: "Lege 82/1991 art.20"` și `temei: "OMFP 2634/2015…"` lângă el. Un artefact legal despre un exercițiu inexistent | `{"fel":"fapt","tip":"registru_inventar","motiv":"Registrul-inventar (cod 14-1-2), tinut potrivit art. 20 din Legea 82/1991",…"an":1900,…}` *(tăiat)* | — | **DA** | `422` · `{"detail":"exercițiu invalid: 1900 (aștept 1990-2100)"}` |
| 86 | Propunerea pentru registrul-inventar | `GET /tenants/{id}/registru-inventar/propunere` | `luna` | invalid: `13` | **TĂCERE** — `200`, și **repeta luna 13 înapoi**, ca și cum ar fi o perioadă goală | `{"an":2026,"luna":13,"randuri":[]}` | — | **DA** | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 56 | Fișa de cont (Cartea mare) | `GET /tenants/{id}/fisa-cont` | `cont` | invalid: `9999` | **AFIRMAȚIE DESPRE UN CONT INEXISTENT** — `200`, cu fișă, sold zero, și un `temei_completitudine` scris **despre contul 9999**. Aceeași aplicație îl refuză explicit la `POST /jurnal` (*„contul 9999 nu exista in planul de conturi al firmei"*): știa răspunsul, dar nu și aici | `{"an":2026,…"fisa":{"motiv":"Fisa de cont pentru operatiuni diverse (cod 14-6-22), contul 9999","temei_completitudine":"toate liniile din `inregistrari_linii` care ating contul 9999…","sold_final":0.0,…}}` *(tăiat)* | — | **DA** — `cont_valid.cere_cont`, aceeași funcție care păzește nota; ridică `ValueError`, deci intră în `try`-ul existent | `422` · refuzul cu contul cerut și conturile apropiate din planul firmei |
| 63–81 | **Cele nouăsprezece note speciale** | `POST /tenants/{id}/nota-<fel>` | discriminatorul | lipsă: `{}` | **ENUMERARE FĂRĂ VERB, în 13 rute și 11 module** — spune ce se acceptă, dar nu că lipsește ceva, nici de ce câmpul n-are valoare implicită | `{"detail":"operatie: dividend|regularizare|imprumut"}` · `{"detail":"fel: incasare|distribuire"}` · `{"detail":"tip: primire|rata|reziduala|operational"}` … | — | **DA** — `common.nomenclator_cerut`, un singur mesaj, **31 de locuri rescrise mecanic** | `422` · `{"detail":"Câmpul \`operatie\` lipsește sau nu e una dintre valorile pe care le cunoaște operațiunea: dividend, regularizare, imprumut. Nu are valoare implicită — felul operațiunii se consemnează, nu se ghicește."}` |
| 67 · 74 · 75 · 63 | Note speciale, alt drum | `POST /tenants/{id}/nota-<fel>` | un câmp obligatoriu | lipsă | **COD INTERN CA MESAJ** — `str(KeyError)`, adică numele câmpului între ghilimele simple. Aceeași clasă scoasă din coadă în lotul 1, găsită aici pe altă cale | `{"detail":"'brut'"}` · `{"detail":"'suma'"}` · `{"detail":"'valoare_intrari'"}` | — | **DA** — `_mesaj_intrare`, în locul comun: **35 de locuri** cu `except (ValueError, KeyError) → str(e)` | `422` · `{"detail":"Lipsește câmpul \`brut\` din cererea trimisă. Operațiunea nu se poate consemna fără el."}` |
| 64 | Nota de avans | `POST /tenants/{id}/nota-avans` | `operatie` | lipsă, și invalid | **NUMEA ALT CÂMP** — toate trei probele (corp gol, operație inexistentă, sumă negativă) primeau mesajul despre **cotă**, fiindcă `cota_ceruta` rula înaintea dispecerului. **A treia instanță a clasei**, după lotul 1 („trimestru invalid: None") și lotul 2 (`cere_cod_partener`) | `{"detail":"cotă TVA obligatorie: operațiunea trebuie să declare explicit cota…"}` | — | **DA** — felul operațiunii se verifică primul | `422` · `{"detail":"Câmpul \`operatie\` lipsește sau nu e una dintre valorile pe care le cunoaște operațiunea: avans_platit, regularizare_platit, avans_incasat, regularizare_incasat…"}` |
| 83 | Adăugarea unui cont în plan | `POST /tenants/{id}/plan-conturi` | `simbol` | invalid: `ABC` | **ACCEPTAT** — `200`, iar contul „ABC" **a intrat în planul firmei**. De acolo putea ajunge pe o notă, într-o balanță și într-o declarație | `{"ok":true,"simbol":"ABC"}` | criteriu **derivat din nomenclatorul propriu**, nu dintr-un act: planul general seed-uit are peste 700 de conturi, toate începând cu o cifră de clasă | **DA** — simbolul începe cu 1-9 și se scrie din cifre, cu separator de analitic | `422` · `{"detail":"Simbolul contului începe cu cifra clasei (1-9), ca toate conturile din planul general — am primit 'ABC'. Dacă e un analitic, scrie-l după contul sintetic (de exemplu 4111.01)."}` |
| 58 | Nota nouă în registrul-jurnal | `POST /tenants/{id}/jurnal` | `data`, `linii`, conturile | patru probe | `400` de fiecare dată, **cu temei structurat** — cea mai bună formă întâlnită în toată campania | `{"detail":{"fel":"neconformitate","tip":"nota_contabila","motiv":"linia 1 are suma -100: o inregistrare consemneaza o operatiune efectuata, deci suma ei e strict pozitiva","regula":"Lege 82/1991 art.6 alin.(1)","camp":"suma","linia":1,…}}` | Lege 82/1991 art.6 alin.(1) | nu — e chiar forma cerută: câmpul, linia, ce e greșit, și temeiul | neschimbat |
| 60 · 61 | Editarea și dezlegarea unei note | `PUT /jurnal/{id}` · `POST /jurnal/{id}/dezleaga` | `nota_id` | invalid: `999999` | `404` / `422`, corecte; dezlegarea cere motivul, cu de ce | `{"detail":"notă inexistentă"}` · `{"detail":{"tip":"MOTIV_OBLIGATORIU","motiv":"Scrie motivul dezlegării: actul repară o potrivire greșită, iar peste șase luni urma fără motiv…"}}` | — | nu | neschimbat |
| 85 · 82 | Înscrierea în registrul-inventar · căutarea în plan | `POST /registru-inventar` · `GET /plan-conturi` | corp gol · `q` gol | | `400` cu câmpul numit · `200` cu tot planul (căutare fără filtru — corect) | `{"detail":{"mesaj":"Nu am înscris rândul: lipsește exercițiul financiar.","erori_campuri":[{"camp":"exercitiu","mesaj":"cerut, nu poate lipsi"}]}}` | — | nu | neschimbat |

### O schimbare de comportament, declarată pentru că n-a fost cerută

`GET /firme/{id}/verificari` accepta anii **2020–2100**, prin verificarea scrisă de mână acolo în
lotul 1. Ajutorul comun cere **1990–2100**, iar ruta a trecut pe el. *Pragul 2020 n-avea motiv scris,
iar registrele contabile pot privi ani mai vechi; consecvența între cele șapte rute valorează mai
mult decât un prag ales fără temei.* Dacă 2020 era voit, se pune înapoi ca parametru.

### Defectele PROBEI, nu ale aplicației — trei, toate consemnate

1. **„Notă dezechilibrată" e imposibilă prin construcție.** Schema ține debit, credit și suma pe
   **aceeași linie**, deci o notă nu poate fi dezechilibrată — clasă deja consemnată pe 31.08, și
   uitată de mine aici. Ce trimiteam era un câmp `suma_totala` care nu există în contractul rutei
   (`descriere`, `data`, `linii`), deci a fost ignorat, pe drept. Proba s-a înlocuit cu întrebarea
   care are sens: o notă **fără linii**.
2. **`POST /plan-conturi` probat pe câmpul greșit** — trimiteam `cont`, câmpul se numește `simbol`,
   iar răspunsul „simbol — lipsește" era corect. Corectat; abia atunci s-a văzut defectul real.
3. **Probele de „sumă negativă" erau oarbe pe trei din patru note.** Trimiteau discriminatorul
   `dividend` la toate patru, deci pe `avans`, `bacsis` și `credit` se opreau la discriminator.
   Corectate cu valoarea validă a fiecărei note. *A doua oară în două loturi când o probă măsoară
   altă întrebare decât cea scrisă în eticheta ei.*

### Ce a rămas nereparat din lotul ăsta, și de ce

1. **Mesajul `nomenclator_cerut` nu spune ce s-a primit — și RĂMÂNE așa, prin decizie.**
   Înlocuirea celor 31 de locuri s-a făcut **mecanic**, iar numele variabilei care poartă valoarea
   diferă de la un modul la altul (`op`, `fel`, `tip`, `moment`, `actiune`); a le lega pe toate ar
   cere rescrierea fiecărui apel cu mâna. **Costin, 04.09.2026:** *„Mesajul numește câmpul și
   valorile acceptate — atât e nevoie ca să corectezi. Repetarea valorii trimise e o îmbunătățire
   mică, iar 31 de locuri cu nume diferite de variabilă înseamnă risc real de a lega greșit unul.
   Consemnează, nu lucra la ea."* — `DECIZII.md` (27). *Nu e o restanță; e o limită decisă.*
2. **Proba de „sumă negativă" pe `nota-asociati` măsoară un câmp lipsă, nu o sumă.** Nota de dividend
   cere `brut`, nu `suma`; răspunsul („Lipsește câmpul `brut`") e corect, dar întrebarea despre
   semnul sumei rămâne neprobată acolo. Se reia la o trecere cu date valide.

### Cifre

- probe INVALIDE rulate: **53**, pe **32 de unități** · defecte găsite: **11** · reparate: **11** ·
  reprobate: **11**, toate schimbate.
- distribuția răspunsurilor la ultima trecere: **41 × 422 · 10 × 400 · 1 × 404 · 1 × 200** (căutarea
  în planul de conturi fără filtru — corect) · **0 × 500**. Înainte: **1 × 500** și **9 × 200**,
  dintre care două scriau în baza de date.
- clase de defect: **perioadă imposibilă acceptată sau căzută** (7 probe, 6 rute) · **afirmație
  despre un cont inexistent** (1) · **refuz telegrafic** (13 probe, 31 de locuri rescrise) · **cod
  intern ca mesaj** (4 probe, 35 de locuri) · **mesaj care numește alt câmp** (3 probe, 1 cauză) ·
  **valoare fără formă acceptată în nomenclator** (1).
- **cea mai bună formă de refuz din toată campania** e tot în lotul ăsta: `POST /jurnal` răspunde cu
  `fel`, `tip`, `motiv`, `regula`, `camp`, `linia` și temeiul — *Lege 82/1991 art.6 alin.(1)*.

---

## LOT 4 — T03 + T04, statul de plată și concediul medical (30 de probe INVALIDE pe 12 unități)

*Unitatea `#52` (ștergerea unui concediu) nu e aici: rută fără câmpuri de completat. Rămân **12 din
13** — opt din T03, patru din T04.*

**Lotul ăsta a scos cel mai grav defect al campaniei**, și nu e o cădere: e o **cifră fiscală
calculată pe o intrare imposibilă**. `POST /calcul-cm` cu `cod=99` — un cod care nu există în
nomenclatorul concediilor medicale — răspundea `200`, cu `"procent": 75.0` și `"brut": 714.0`.
Aceeași cifră o primea și `cod="ABC"`. *Indemnizația aia intră în statul de plată, în D112 și în
decontul cu CNAS.*

**Ce s-a lăsat în urmă:** nimic. Patru dintre unități scriu (`#41` nota ciornă, `#44` corecția,
`#46` emiterea, `#51` concediul); toate au fost refuzate. Verificat după: `facturi` 3,
`inregistrari` 4, `plan_conturi` 185, `state_plata` 2 (din 19–21.08, preexistente),
`concedii_medicale` 0, `salariati` 2.

| # | funcționalitate | ecran / rută | câmp | ce s-a introdus | ce a făcut aplicația | mesajul verbatim | temei legal | reparat | rezultat după reparație |
|---|---|---|---|---|---|---|---|---|---|
| 48 | Calculul indemnizației de CM | `POST /tenants/{id}/calcul-cm` | `cod` | invalid: `99` | **COTĂ FISCALĂ INVENTATĂ** — `200`, cu `procent 75%` și indemnizație calculată. Cauza, la sursă: `_procent_cm_l141_2025` se termină cu `return Decimal("0.75")  # 13, 15, rest`. „Restul" înseamnă, pentru nomenclator, șapte coduri reale — și, pentru orice altceva, o cifră pe care n-o cere nicio normă. E chiar interdicția **fără default fiscal tăcut**, pe cea mai scumpă cale | `{"baza":30000.0,"media_zilnica":238.1,"procent":75.0,"zile_platite":4,"brut":714.0,…}` *(tăiat)* | nomenclatorul `core/nomenclator_cm.CODURI` — 20 de coduri, fiecare cu temeiul lui | **DA** — codul se confruntă cu nomenclatorul **în dispecer**, deci amândouă variantele datate ale formulei sunt apărate deodată, iar cele șapte coduri reale rămân la 75% | `422` · `{"detail":"Codul de indemnizație '99' nu există în nomenclatorul concediilor medicale. Codurile cunoscute: 01, 02, …, 91, 92."}` |
| 48 | Calculul indemnizației de CM | `POST /tenants/{id}/calcul-cm` | `luna` | invalid: `13` | **INDEMNIZAȚIE PENTRU O LUNĂ CARE NU EXISTĂ** — `200`, `brut 454.0`, și cu **altă bază** (26.625 în loc de 30.000): luna 13 mutase fereastra de 6 luni | `{"baza":26625.0,"media_zilnica":206.4,"procent":55.0,"zile_platite":4,"brut":454.0,…}` *(tăiat)* | — | **DA** — `_cere_perioada`, același ajutor ca la lotul 3 | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 48 | Calculul indemnizației de CM | `POST /tenants/{id}/calcul-cm` | `zile_lucratoare_cm` | invalid: `-5` | **ACCEPTAT TĂCUT** — `200`, `zile_platite 0`, `brut 0`. Rezultatul e zero, dar nimeni nu spune că intrarea era imposibilă | `{"baza":30000.0,…"zile_platite":0,"brut":0.0,…}` *(tăiat)* | — | **DA** | `422` · `{"detail":"Zilele de concediu medical nu pot fi negative (am primit -5). Se numără zilele lucrătoare acoperite de certificat."}` |
| 48 | Calculul indemnizației de CM | `POST /tenants/{id}/calcul-cm` | tot corpul | lipsă: `{}` | **A CĂZUT** — `500`. `int(corp["an"])` era **în afara** try-ului care traduce `KeyError` | `Internal Server Error` | — | **DA** — aceeași reparație, un singur bloc de parsare | `422` · `{"detail":"Lipsește câmpul \`an\` din cererea trimisă. Operațiunea nu se poate consemna fără el."}` |
| 40 | Fluturașul de salariu | `GET /tenants/{id}/fluturas/{sid}` | `luna` | invalid: `13` | **A CĂZUT** — `500` | `Internal Server Error` | — | **DA** | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 41 | Nota ciornă a statului | `POST /tenants/{id}/salarii-contare` | `luna` | invalid: `13` | **A CĂZUT** — `500` | `Internal Server Error` | — | **DA** | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 43 | Statul de plată | `GET /tenants/{id}/stat-plata` | `luna` | invalid: `13` | **A CĂZUT** — `500` | `Internal Server Error` | — | **DA** | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 45 | Exemplarele emise | `GET /tenants/{id}/stat-plata/emis` | `luna` | invalid: `13` | **A CĂZUT** — `500` | `Internal Server Error` | — | **DA** | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 42 | Propunerea de notă | `POST /tenants/{id}/salarii-contare/propunere` | `luna` | invalid: `0` | **MESAJ ÎN ENGLEZĂ, DIN BIBLIOTECĂ** — `422` cu textul lui `datetime`. Cod intern ca mesaj, pe altă cale decât `str(KeyError)` din lotul 3 | `{"detail":"month must be in 1..12"}` | — | **DA** — garda de perioadă răspunde înainte ca luna să ajungă la bibliotecă | `422` · `{"detail":"luna invalidă: 0 (aștept 1-12)"}` |
| 50 | Lista concediilor unui salariat | `GET /tenants/{id}/salariati/{sid}/concedii` | `salariat_id` | invalid: `999999` | **TĂCERE, ȘI INCONSECVENȚĂ** — `200` `{"concedii":[]}`. „Salariatul n-are concedii" arăta identic cu „salariatul nu există" — iar `GET /fluturas`, pe **același id inexistent**, răspunde `404 salariat inexistent`. Aplicația știa deosebirea într-un loc și n-o făcea în celălalt | `{"concedii":[]}` | — | **DA** — aceeași verificare ca la fluturaș | `404` · `{"detail":"salariat inexistent"}` |
| 50 | Lista concediilor unui salariat | `GET /tenants/{id}/salariati/{sid}/concedii` | `an` | invalid: `1900` | **TĂCERE** — `200`, listă goală | `{"concedii":[]}` | — | **DA** | `422` · `{"detail":"an invalid: 1900 (aștept 1990-2100)"}` |
| 51 | Salvarea unui concediu | `POST /tenants/{id}/salariati/{sid}/concedii` | `cod`, datele | trei probe: cod `99` · sfârșit înaintea începutului · `data_inceput=2026-02-31` | **NUMEA ALT CÂMP** — toate trei primeau mesajul despre **veniturile pe 6 luni**, fiindcă verificarea bazei de calcul rula înaintea formei câmpurilor. **A patra instanță a clasei**, după loturile 1, 2 și 3 | `{"detail":"Veniturile brute pe 6 luni lipsesc sau sunt 0 - completeaza baza de calcul din statele de plata."}` | — | **DA** — forma întâi: codul contra nomenclatorului, datele contra calendarului, sfârșitul după început; apoi ce lipsește din dosarul firmei | `422` · trei mesaje distincte, fiecare despre câmpul lui: codul necunoscut · *„Concediul se sfârșește (2026-08-03) înaintea zilei în care începe (2026-08-07)."* · *„data inceput: '2026-02-31' nu e o dată din calendar."* |
| 51 | Salvarea unui concediu | `POST /tenants/{id}/salariati/{sid}/concedii` | `salariat_id` | invalid: `999999` | Mesajul despre venituri — **nu e fals** (veniturile chiar lipsesc, fiindcă omul nu e în firmă), dar nu numește starea reală, și trimite contabilul să completeze statele de plată ale cuiva inexistent | `{"detail":"Veniturile brute pe 6 luni lipsesc sau sunt 0 …"}` | — | **DA** — a treia rută despre același salariat, acum cu același răspuns ca celelalte două | `404` · `{"detail":"salariat inexistent"}` |
| 44 | Corecția pe stat | `POST /tenants/{id}/stat-plata/corectie` | corp gol · `salariat_id` · `luna` | trei probe | `422` / `409` / `422`, toate corecte, cu propoziții întregi | `{"detail":"lipsesc an și luna"}` · `{"detail":"salariatul 999999 nu are stat emis pe 2026-08 — nu există ce corecta"}` · `{"detail":"luna trebuie să fie între 1 și 12"}` | — | nu | neschimbat |
| 46 · 47 | Emiterea statului · motivul unui exemplar | `POST /stat-plata/emite` · `POST /stat-plata/motiv` | corp gol · motiv gol · exemplar inexistent | | `422` de fiecare dată, cu **de ce** contează câmpul | `{"detail":"motivul nu poate fi gol: o contradicție se asumă cu o rațiune scrisă"}` · `{"detail":"exemplarul 999999 nu există — nu are ce să asume nimeni"}` | — | nu — e forma cerută | neschimbat |
| 41 · 49 | Nota ciornă, pe an vechi · codurile de indemnizație | `POST /salarii-contare` · `GET /concedii/coduri` | `an=1900` · `la_data` invalidă | | `422` motivate — primul prin chiar mecanismul `PerioadaIndisponibila` | `{"detail":"PERIOADA_BLOCATA: 1900-01-01 nu poate fi calculată: valoarea 'salariu_minim' nu e definită înainte de 2025-01-01 (nu a fost verificată la sursă…)"}` · `{"detail":"Data trebuie să fie în formatul AAAA-LL-ZZ."}` | — | nu | neschimbat |

### Cifre

- probe INVALIDE rulate: **30**, pe **12 unități** · defecte găsite: **10** · reparate: **10** ·
  reprobate: **10**, toate schimbate. Cele 10 s-au arătat pe **16 probe**.
- distribuția răspunsurilor la ultima trecere: **26 × 422 · 3 × 404 · 1 × 409** · **0 × 500** ·
  **0 × 200**. Înainte: **5 × 500** și **5 × 200**.
- clase de defect: **cădere `500`** (5 probe, 5 rute) · **cotă fiscală inventată pentru un cod
  inexistent** (1) · **cifră calculată pe o lună imposibilă** (1) · **valoare negativă acceptată
  tăcut** (1) · **tăcere pe un subiect inexistent** (2 probe, 1 rută) · **mesaj care numește alt
  câmp** (4 probe, 1 cauză) · **mesaj de bibliotecă, în engleză** (1).
- **niciun defect al probei** în lotul ăsta — spre deosebire de loturile 2 și 3. Ce s-a schimbat:
  am pus în ham un `SALARIAT` care **există în firma de probă**, tocmai fiindcă de două ori la rând
  probele se opriseră mai devreme decât scria în eticheta lor.

---

## LOT 5 — facturile PRIMITE și achizițiile (29 de probe INVALIDE pe 11 unități)

**Nu e un traseu, e o suprafață — și asta s-a aflat căutând.** Comanda spunea *„traseul facturilor
primite și al achizițiilor, **oricare i-ar fi numărul**"*, cu alternativa *„dacă traseul nu există ca
atare sau e deja acoperit, ia banca și casa"*. Căutat în inventar: **nu există** un traseu cu numele
ăsta. Ce există e suprafața prin care intră **TVA-ul deductibil**, împrăștiată în patru trasee:

| trasee | unități |
|---|---|
| **T06** — factura primită prin e-Factura | `#88` respinge · `#89` validează · `#92` import |
| **T08** — recepția | `#101` lista NIR · `#102` NIR nou |
| **T28** — achiziția intracomunitară | `#238` |
| **T29** — regimurile speciale pe achiziții | `#249` agricultor · `#250` necorporală · `#251` de la neînregistrat · `#252` taxare inversă · `#254` import extracomunitar |

**Unsprezece unități.** N-am trecut la bancă și casă: alternativa era pentru cazul în care suprafața
nu există sau e acoperită — ea există și era neprobată. S-a adăugat o **a doua trecere** pe `#23`
(`POST /facturi`), pe direcția **primită** — probată în lotul 2 numai pe emisă —, fiindcă ea e chiar
poarta prin care o factură de achiziție ajunge în evidență. *Nu se numără ca unitate nouă.*

**Ce s-a lăsat în urmă:** nimic. Trei probe **au trecut** la a doua trecere și au scris în evidență
(înregistrările 29, 30, 31 și facturile 22, 23); s-au șters din bază după reparație. Verificat la
final: `facturi` 3, `inregistrari` 4.

| # | funcționalitate | ecran / rută | câmp | ce s-a introdus | ce a făcut aplicația | mesajul verbatim | temei legal | reparat | rezultat după reparație |
|---|---|---|---|---|---|---|---|---|---|
| 238 | Achiziția intracomunitară | `POST /tenants/{id}/achizitie-ic` | `cota` | invalid: `99` | **COTĂ INVENTATĂ, ÎN EVIDENȚĂ** — `200`, `"tva":"990.00"` la o bază de 1.000, cu taxare inversă. Intră în **D300** și în **D390**. `common.cota_ceruta` cerea doar ca **să existe** o cotă, nu ca ea să fie una din lege — iar prin funcția aia trec **35 de operațiuni** | `{"inregistrare_id":30,"factura_id":23,"valoare":"1000","tva":"990.00"}` | art. 291 Cod fiscal, prin registrul `common.COTE` | **DA** — `cota_ceruta` verifică acum și apartenența, la **data operațiunii**, luată din corp (`data` e numele uniform). Zero apelanți modificați, 35 de operațiuni apărate deodată | `422` · `{"detail":"Cota de TVA 99% nu există în legea română la data operațiunii (2026-09-04). Cotele de atunci: 0%, 11.00%, 21.00%. Temei: Legea 141/2025 art.291 alin.(1); …"}` |
| 238 | Achiziția intracomunitară | `POST /tenants/{id}/achizitie-ic` | `tip` | invalid: `altceva` | **ÎNCADRARE TĂCUTĂ** — `200`, achiziția a intrat ca **bunuri**. Codul era `"servicii" if corp.get("tip") == "servicii" else bunuri`: orice altă valoare devenea bunuri. *Tipul decide încadrarea în D390 și temeiul citat pe notă* | `{"inregistrare_id":29,"factura_id":22,"valoare":"1000","tva":"210.00"}` | — | **DA** | `422` · `{"detail":"Câmpul \`tip\` lipsește sau nu e una dintre valorile pe care le cunoaște operațiunea: bunuri, servicii…"}` |
| 254 | Importul extracomunitar | `POST /tenants/{id}/import-extracomunitar` | `procent_taxa_vamala` | invalid: `500` | **PROCENT DE 500% ACCEPTAT** — `200`: taxă vamală **5.000** la o valoare în vamă de **1.000**, bază TVA 6.000, TVA 1.260 | `{"inregistrare_id":31,"taxa_vamala":"5000.00","baza_tva":"6000.00","tva":"1260.00","mod_tva":"vama"}` | — | **DA** | `422` · `{"detail":"Procentul taxei vamale e între 0 și 100 — am primit 500. Taxa vamală e o parte din valoarea în vamă, nu un multiplu al ei."}` |
| 101 | Lista notelor de recepție | `GET /tenants/{id}/stocuri/nir` | `luna` | invalid: `13` | **A CĂZUT** — `500` | `Internal Server Error` | — | **DA** — `_cere_perioada`, al optulea apelant al aceluiași ajutor | `422` · `{"detail":"luna invalidă: 13 (aștept 1-12)"}` |
| 101 | Lista notelor de recepție | `GET /tenants/{id}/stocuri/nir` | `an` | invalid: `1900` | **TĂCERE** — `200` `{"nir":[]}` | `{"nir":[]}` | — | **DA** | `422` · `{"detail":"an invalid: 1900 (aștept 1990-2100)"}` |
| 102 | Nota de recepție | `POST /tenants/{id}/stocuri/nir` | tot corpul | lipsă: `{}` | **COD INTERN CA MESAJ** — `str(KeyError)`. A scăpat reparației din lotul 3 fiindcă ruta NIR nu folosește `except (ValueError, KeyError)`, ci contractul `{"eroare", "erori_campuri"}` | `{"detail":"'linii'"}` | — | **DA** — un NIR fără articole se refuză explicit, cu ce n-ar avea ce înregistra | `422` · `{"detail":{"mesaj":"Nota de recepție n-are niciun articol. O recepție consemnează ce a intrat efectiv în gestiune — fără articole n-ar avea ce înregistra, nici ce trece în jurnalul de cumpărări.","erori_campuri":[{"camp":"nir-linii",…}]}}` |
| 250 | Achiziția necorporală | `POST /tenants/{id}/achizitie-necorporala` | `tip` | lipsă, și invalid | **ENUMERARE FĂRĂ VERB** — a scăpat reparației din lotul 3 fiindcă e `HTTPException`, nu `ValueError`; regexul de atunci căuta numai `ValueError` | `{"detail":"tip: software|licenta|brevet|dezvoltare|constituire"}` | — | **DA** — `nomenclator_cerut`, plus a doua instanță găsită cu aceeași căutare (`"mediu: test|prod"`) | `422` · `{"detail":"Câmpul \`tip\` lipsește sau nu e una dintre valorile pe care le cunoaște operațiunea: software, licenta, brevet, dezvoltare, constituire…"}` |
| 238 | Achiziția intracomunitară | `POST /tenants/{id}/achizitie-ic` | `valoare` | invalid: `-1000` | **NUME CARE NU E AL CERERII** — „baza" nu e un câmp al corpului trimis | `{"detail":"baza invalida"}` | — | **DA** | `422` · `{"detail":"Valoarea achiziției trebuie să fie un număr pozitiv — o achiziție consemnează o operațiune efectuată. Pentru o corecție în minus se face o stornare, nu o valoare negativă."}` |
| 249 | Achiziția de la agricultor | `POST /tenants/{id}/achizitie-agricultor` | `valoare` | invalid: `-500` | **IDEM** — „pret/procent" nu sunt câmpuri ale cererii | `{"detail":"pret/procent invalid"}` | — | **DA** | `422` · `{"detail":"Prețul achiziției și procentul de compensare trebuie să fie numere pozitive — o achiziție consemnează o operațiune efectuată."}` |
| 254 | Importul extracomunitar | `POST /tenants/{id}/import-extracomunitar` | `valoare_vamala` | invalid: `-1000` | **IDEM** | `{"detail":"valoare vamala invalida"}` | — | **DA** | `422` · `{"detail":"Valoarea în vamă trebuie să fie un număr pozitiv — ea e baza pe care se calculează taxa vamală, accizele și TVA-ul la import."}` |
| 88 · 89 | Factura primită — respingere și validare | `POST /facturi-primite/{id}/respinge` · `/valideaza` | `primita_id`, `motiv` | `999999` · motiv gol | `404` / `422`, corecte | `{"detail":"factură primită inexistentă"}` · `{"detail":"motivul respingerii e obligatoriu"}` | — | nu | neschimbat |
| 251 · 252 | De la neînregistrat · taxarea inversă | `POST /achizitie-neinregistrat` · `/achizitie-taxare-inversa` | furnizor · categorie | gol · inexistentă | `422`, cu **de ce** contează câmpul, și cu nomenclatorul întreg | `{"detail":"nume furnizor obligatoriu (persoana fizica - apare in denP si in avertisment)"}` · `{"detail":"categorie necunoscuta (deseuri\|masa_lemnoasa\|cereale\|…)"}` | — | nu | neschimbat |
| 23 | Crearea unei facturi — **a doua trecere, direcția PRIMITĂ** | `POST /tenants/{id}/facturi` | `cota_tva`, `data_emitere` | `99` · `2026-02-31` | `422` de fiecare dată — **reparațiile din lotul 2 țin și pe direcția primită**, inclusiv condiția scrisă atunci: cota se verifică pe primite doar când `tert_tara=RO` | `{"detail":"Linia 'marfa' are cota de TVA 99.0%, care nu există în legea română la data facturii (2026-09-04)…"}` | art. 291 Cod fiscal | nu | neschimbat |

### Defectele PROBEI — patru grupuri, și de data asta era o clasă, nu un accident

Rutele de achiziție cer mai multe câmpuri obligatorii, iar prima formă a probelor trimitea corpuri
**incomplete**: se opreau la primul câmp lipsă și măsurau altă întrebare decât cea din eticheta lor.
`#102` folosea numele de câmp de la **factură** (`descriere`, `pret_unitar`) în loc de cele ale
**NIR-ului** (`denumire`, `pret_achizitie`); `#238` n-avea `cod_tva_furnizor`; `#252` n-avea CUI-ul
furnizorului; `#254` n-avea cota. **Abia după corectare au ieșit la iveală cele trei defecte grave de
mai sus** — până atunci, toate trei arătau ca niște refuzuri cuminți.

**Regula hamului, scrisă acum ca regulă:** *corp de bază **valid**, minus o singură abatere — cea
probată.* E a treia oară în campanie când o probă măsoară altceva decât scrie în eticheta ei (lotul
2: monedă; lotul 3: sumă negativă; lotul 5: patru grupuri deodată).

### Ce a rămas nereprobat, și de ce

**Data și cota per linie pe `POST /stocuri/nir`.** După trei încercări, proba tot nu ajunge acolo:
NIR-ul cere o cotă și la nivel de notă, nu doar pe linie, iar refuzul care vine (*„Cota de TVA nu s-a
dat. Nu se folosește o valoare implicită…"*) e **corect și motivat** — dar despre alt câmp decât cel
probat. M-am oprit după a treia rundă: ruta nu cade și nu tace, iar întrebarea rămâne deschisă pentru
o trecere cu date valide. *Se scrie ce s-a măsurat, nu ce am vrut să măsor.*

### Cifre

- probe INVALIDE rulate: **29**, pe **11 unități** (plus 2 pe a doua trecere a lui `#23`) · defecte
  găsite: **10** · reparate: **10** · reprobate: **10**, toate schimbate.
- distribuția la ultima trecere: **26 × 422 · 2 × 404 · 1 × 400** · **0 × 500** · **0 × 200**.
  Înainte: **1 × 500** și **1 × 200**; iar după corectarea probelor oarbe, **3 × 200** în plus —
  toate trei scriind în evidență.
- clase de defect: **cifră fiscală pe intrare imposibilă** (3: cotă inventată · încadrare tăcută ·
  procent de 500%) · **cădere `500`** (1) · **tăcere** (1) · **cod intern ca mesaj** (1) · **refuz
  telegrafic** (2 locuri, `HTTPException`) · **nume care nu e al cererii** (3).
- **cea mai largă reparație a campaniei**: `common.cota_ceruta` verifică acum cota la data
  operațiunii — **35 de operațiuni** apărate deodată, fără niciun apelant modificat.

---

## LOT 6 — OPT trasee într-unul singur (63 de probe INVALIDE pe 45 de unități)

**Costin, 04.09.2026:** *„Mărește lotul: grupează mai multe trasee într-unul singur, nu unul-două.
Ținta e cât încape într-o sesiune fără `/clear`, nu cât încape într-o oră. O singură poartă și o
singură scriere de registre pe lot, la sfârșit."* Lotul ăsta e primul de mărimea cerută.

| traseu | unități | ce e |
|---|---|---|
| **T-SPV** | 3 | conectorul SPV/ANAF |
| **T07** | 4 | extrasul bancar și potrivirea |
| **T09** | 2 | casa și registrul de casă |
| **T10** | 3 | inventarierea |
| **T11** | 6 | închiderea lunii |
| **T12** | 5 | închiderea anului și situațiile financiare |
| **T13** | 4 | trecerea de regim fiscal |
| **T14** | 18 | preluarea unei firme |

*T08 nu apare: unitățile lui au fost probate în lotul 5, ca parte a suprafeței achizițiilor.*

**Probele s-au scris pe CLASE, nu una câte una.** La 45 de unități, scrisul de mână ar fi fost el
însuși o sursă de greșeli: trei generatoare — perioadă imposibilă, import JSON cu `randuri` gol,
încărcare a aceluiași `.txt` care nu e tabel — acoperă 33 din cele 63 de probe.

**Ce s-a lăsat în urmă:** nimic — **dar o probă a schimbat CUI-ul firmei** și a trebuit pus la loc
cu mâna (v. mai jos). Verificat la final: `facturi` 3, `inregistrari` 4, `plan_conturi` 185,
`articole` 9, `salariati` 2, `firma_profil.cui` = `public.tenants.cui` = `95141537`, `api_chei` 0.

### Cel mai grav: CUI-ul firmei — nicio verificare, și scris într-un singur loc din două

| # | rută | ce s-a introdus | ce a făcut aplicația | reparat |
|---|---|---|---|---|
| 126 | `POST /tenants/{id}/firma-profil/date` | `{"cui": "RO1234567890"}` — cifră de control greșită | **`200`, ȘI L-A SCRIS.** Măsurat imediat după: `firma_profil.cui` devenise `RO1234567890`, iar `public.tenants.cui` rămăsese `95141537` | **DA**, în două părți |

**Două lucruri deodată, și al doilea nu era numit nicăieri:**

1. **Niciun control** — deși aplicația **știe** să valideze un CUI: `solduri_parteneri_api.valideaza_cui`
   verifică cifra de control a **partenerilor**. Firma proprie n-avea niciun control. *A cincea
   instanță a clasei „știe într-un loc și nu și în celălalt", după cont/fișă (lot 3),
   salariat/concediu (lot 4) și celelalte.*
2. **SORA LUI R81.** CUI-ul firmei stă în **două locuri** — `public.tenants.cui` și
   `{schema}.firma_profil.cui` — iar ecranul „Date firmă" scria numai în al doilea. R81 a închis
   exact clasa asta pentru **denumire**, cu un scriitor unic care atinge amândouă locurile în
   aceeași tranzacție; **CUI-ul a rămas afară, și nimeni n-o numise.** Acum are `alege_cui`, scris
   lângă `alege_denumirea`, cu aceeași regulă: nu comite, fiindcă simetria **este** proprietatea
   tranzacției.

*CUI-ul firmei intră în fiecare declarație depusă. Unul greșit nu se oprește la noi — îl respinge
ANAF, după depunere.* Refuzul de acum: `422` · *„CUI-ul RO1234567890 nu e valid (cifra de control).
CUI-ul firmei intră în fiecare declarație depusă — unul greșit nu se oprește aici, îl respinge ANAF,
după depunere."*

### Restul, pe clase

| clasă | unde | ce era | ce e acum |
|---|---|---|---|
| **cădere `500`** | `#105` `casa/registru?luna=13` · `#103` `casa/operatiuni` cu `data=2026-02-31` · `#112` `perioada/confirma?luna=13` | `Internal Server Error` | `422`, cu câmpul numit |
| **afirmație despre o perioadă care nu există** | `#111` `facturi/perioada?luna=13` | `200` · `{"confirmat":false,"poate_confirma":true}` — **un verdict despre închiderea lunii 13** | `422` · *„luna invalidă: 13"* |
| **tăcere pe perioadă** | `#105` `an=1900` · `#117` istoric (×2) · `#118` categorie-mărime · `#120`/`#122` XML-urile de bilanț | `200` cu listă goală, sau un artefact cu **motiv scris** despre exercițiul 1900 | `422`, prin `_cere_perioada` — al **cincisprezecelea** apelant al aceluiași ajutor |
| **„am făcut" despre ce nu există** | `#113` `perioada/redeschide?luna=13` | `200` · `{"ok":true}` — a *redeschis* luna 13 | `422` |
| **tăcere pe nomenclator** | `#95` `banca/reconciliere?status=INEXISTENT` · `#144` `migrare/straturi?tip_firma=inexistent` | `200` cu listă goală · `200` cu **lista întreagă**, ca și cum ar fi răspunsul pentru tipul cerut | `422`, cu nomenclatorul enumerat |
| **actul absent raportat ca rezultatul lui** | `#109` `stocuri/inventar` cu corp gol | `200` · `{"rezultate":[]}` — „am inventariat și n-am găsit diferențe" despre o numărătoare care nu s-a făcut | `422` · *„Un inventar fără linii nu e o inventariere fără diferențe — e o inventariere care nu s-a făcut."* |
| **document oficial pe o perioadă imposibilă** | `#107` `d406-stocuri` cu sfârșit înaintea începutului | `200` cu **XML SAF-T generat** | `422`, plus mesajul de dată care spune acum **care** din cele două e greșită |
| **valoare fără formă, acceptată** | `#127` `firma-profil/model` cu `culoare="ceva-ce-nu-e-culoare"` | `200` — și culoarea ajunge în PDF-ul facturii, unde generatorul o citește ca hex | `422`, cu forma cerută și un exemplu |
| **cerere fără conținut raportată ca succes** | `#146` `articole-import` · `#158` `salariati-import`, cu `randuri=[]` | `200` · `{"create":0}` / `{"importati":0}` | `422` — **a doua și a treia cale** a clasei închise în lotul 1b |
| **cifră falsă în refuz** | `#158` `salariati-import` cu un rând fără câmpuri | *„**2 rânduri** nu pot intra"* pentru **un** rând — numără erorile, nu rândurile | *„Un rând nu poate intra…"* — **a doua instanță** a defectului reparat în lotul 1, cu aceleași cuvinte |
| **fișier necitit raportat ca fișier gol** | `#133` `migrare/fisier` · `#135` `migrare/incarca` · `#154` `parteneri/incarca` | `200` cu rezultate goale, pe un `.txt` cu o linie de proză | `422` · *„un fișier necitit nu e un fișier gol"*. Ruta `istoric-declaratii-import/incarca` refuza deja, din lotul 1 — **a șasea instanță** a clasei „știe într-un loc, nu și în celălalt" |
| **mesaj care nu numește câmpul** | `#103` `categorie necunoscută: None` · `#107` `date format YYYY-MM-DD` | telegrafic, fără nomenclator și fără să spună care dată | propoziții, cu valorile posibile enumerate |

### Trei `500` introduse de reparațiile MELE, prinse la reprobare

Reprobarea a scos trei căderi noi, toate ale mele: refuzul importului de articole ieșea ca `500`
(ruta nu prindea `ValueError`), iar cele două refuzuri de fișier aveau `%%s` într-un șir interpolat.
*Reprobarea nu e o formalitate de confirmare — e a doua probă, și a găsit ce prima n-avea cum.*

### Ce n-a fost defect, deși a răspuns `200`

- **`#2` `spv/autorizare`** întoarce URL-ul de autorizare — asta e treaba ei; **`#3` `spv/stare`**
  spune `{"conectat": false}`, corect.
- **`#1` `anaf/oauth/callback`** cu un cod inventat redirecționează la pagina de retur **cu
  `?eroare=`** — verificat în cod, nu dedus din codul HTTP.
- **`#109`** cu articol inexistent sau cantitate negativă răspunde `200`, dar cu `eroare` **pe
  linie** (`cvi-a999999-faptic`) — contractul field-keyed al ecranului. Refuzul există, la nivelul
  la care ecranul îl poate arăta.
- **`#126`** cu corp gol răspunde `200` cu profilul neschimbat. Un „salvează" fără câmpuri e un
  no-op; `{"ok": true}` e discutabil, dar nu afirmă nimic fals.
- **`#119` / `#121`** (validarea bilanțului) refuză `an=1900` — dar pentru **alt motiv**: lipsește
  numărul de la registrul comerțului, verificat mai devreme. Refuzul e corect și motivat; anul nu
  ajunge să fie evaluat. *Se scrie ce s-a măsurat.*

### Cifre

- probe INVALIDE rulate: **63**, pe **45 de unități**, în **opt trasee** · defecte găsite: **20** ·
  reparate: **20** · reprobate: **20**, toate schimbate.
- distribuția la ultima trecere: **40 × 422 · 15 × 400 · 2 × 404 · 6 × 200** (toate șase explicate
  mai sus) · **0 × 500**. Înainte: **3 × 500** și **24 × 200**.
- **niciun defect al probei** — a doua oară la rând, după ce regula „corp de bază valid, minus o
  singură abatere" a intrat în ham la lotul 5.
- `_cere_perioada`, ajutorul scris în lotul 3 pentru **patru** rute, are acum **cincisprezece**
  apelanți. *Fiecare lot îl găsește într-un loc nou.*

---

## LOT 7 — TREISPREZECE trasee (61 de probe INVALIDE pe 49 de unități)

T15 salariatul · T16 pontajul · T17 plata salariilor · T18 chitanța · T19 scadențarul · T20 mișcarea
de stoc · T21 rețeta și producția · T22 mijlocul fix · T23 bonul de la client · T24 bonul fiscal ·
T25 magazinul online · T26 registratura · T27 e-Transport.

**Proba de deschidere a fost corpul gol, pe toate cele 28 de căi care primesc unul.** E cea mai
ieftină probă și cea care scoate contractul la iveală: *ce răspunde o rută când nu primește nimic
arată ce consideră ea obligatoriu — iar acolo unde răspunde `200`, întrebarea e ce a făcut fără să i
se ceară.* Din cele 28, **șase au căzut cu `500`** și **una a oprit un canal**.

**Ce s-a lăsat în urmă:** nimic. Verificat: `facturi` 3, `inregistrari` 4, `salariati` 2,
`articole` 9, `produse` 0, `chitante` 0; `firma_profil.cui` = `95141537`, `wc_url` și `wc_ck` = NULL
(cum erau).

| # | rută | ce s-a introdus | ce a făcut aplicația | reparat |
|---|---|---|---|---|
| 170 · 201 · 202 · 204 · 205 · 213 | `reges-config` · `stocuri/iesire` · `stocuri/intrare` · `stocuri/reclasificare` · `stocuri/transfer` · `retete/descarca` | corp gol | **A CĂZUT** — `500` de șase ori. `corp["x"]` cu `KeyError` neprins | **DA** — refuzul iese acum ca mesaj, prin ajutorul comun din lotul 3 |
| 180 | `POST /pontaj/confirma` | `luna=13` | **A CĂZUT** — `500` | **DA** — `_cere_perioada` |
| 215 | `POST /amortizare` | `luna=13` | **A CĂZUT** — `500`, **și ruta asta scrie nota direct ca `validata`**, deci o lună imposibilă ar fi ajuns în evidență, nu într-o ciornă | **DA** |
| 177 | `PUT /salariati/{id}` | `salariat_id=999999` | **`200` · `{"ok":true}`** — „am actualizat" despre cineva care nu e în firmă. **A treia oară** în campanie când o rută despre un salariat nu verifică dacă el există (lotul 4: concediile, de două ori) | **DA** — `404 salariat inexistent`, ca celelalte trei rute |
| 230 | `PUT /woocommerce/config` | corp gol | **A OPRIT CANALUL, TĂCUT** — scria `NULL` în `wc_url`, `wc_ck`, `wc_cs` și răspundea `{"ok":true}`. Chiar comentariul de deasupra o spune: *„cu ele pline canalul e pornit, golite îl oprește"*. **Aceeași clasă ca importurile din lotul 1b**: o operațiune de înlocuire care primește un set vid nu are voie să execute partea de ștergere | **DA** — oprirea rămâne posibilă, dar **cerută**, nu dedusă din tăcere |
| 183 | `GET /util/zile-lucratoare` | `end < start` | **`200` · `{"zile": 0}`** — o cifră, adică un răspuns. Iar cifra asta intră în **auto-calculul indemnizației de concediu medical** (OUG 158/2005 art. 10): *„0 zile lucrătoare" și „intervalul e scris invers" nu sunt același lucru* | **DA** |
| 232 | `GET /registratura` | `an=1900` | `200` cu registru gol | **DA** — `_cere_perioada` |
| 203 | `GET /stocuri/locatii` | `articol_id=999999` | `200` · `{"locatii":[]}` — „articolul nu e nicăieri" arăta identic cu „articolul nu există" | **DA** — `404`, ca la salariat (lot 4) și la cont (lot 3) |

### Ce a răspuns bine, și merită scris

Cele mai bune refuzuri din lot n-au avut nevoie de reparație: **e-Transport** (`#234`, `#235`)
răspunde cu `{"cod":"CAMPURI_LIPSA","mesaj":"Câmpuri obligatorii lipsă (schema eTransport): Tip
operațiune; Cel puțin un bun…"}` — numește schema, câmpurile și ce lipsește; **reevaluarea**
(`#217`) spune *„mijloc fix inexistent/inactiv"*; **rețetele** (`#212`) — *„Denumirea rețetei e
obligatorie."*

### Defectele PROBEI — patru grupuri, și trei feluri diferite de a fi oarbă

1. **Parametri care nu există în semnătură.** `#188` (chitanțe), `#194` (analitică) și `#173`
   (salariați) nu *ignoră* `luna` — **n-o primesc deloc**; FastAPI lasă parametrii necunoscuți să
   treacă. Probele mele măsurau o întrebare pe care rutele n-o puseseră niciodată.
2. **Locul greșit al parametrului.** `#215` cere `an`/`luna` ca **parametri de adresă**, nu în corp;
   prima formă îi trimitea în corp și primea „an lipsește". *Abia după corectare a ieșit `500`-ul.*
3. **Rolul greșit.** `#219`–`#221` sunt rute de **portal** și cer rol `client`; cu tokenul de cabinet
   se opreau la poarta de contexte („Alegeți firma"), nu la bonul inexistent.

*A patra oară în campanie când probele măsoară altceva decât scrie în eticheta lor — dar de data asta
fiecare fel a fost prins la prima reprobare, iar două dintre defectele reale ale lotului (`#215`,
`#230`) s-au văzut **numai** după corectare.*

### Cifre

- probe INVALIDE rulate: **61**, pe **49 de unități**, în **treisprezece trasee** · defecte găsite:
  **13** · reparate: **13** · reprobate: **13**, toate schimbate.
- distribuția la ultima trecere: **41 × 422 · 11 × 404 · 5 × 400 · 2 × 200** (căutări în COR fără
  rezultate — corect) · **0 × 500**. Înainte: **7 × 500** și **10 × 200**.
- **opt din cele treisprezece defecte au fost căderi `500`** — cea mai mare proporție din campanie,
  și toate pe **corpul gol**. *La 28 de căi probate cu aceeași intrare, șase au căzut: nu e un
  accident, e o clasă — rutele care citesc `corp["camp"]` fără să treacă prin nicio validare.*
- `_cere_perioada` are acum **optsprezece** apelanți.

---

## LOT 8 — ȘAPTE trasee (50 de probe INVALIDE pe 43 de unități)

T28 operațiunile intracomunitare · T29 regimurile speciale de TVA · T30 operațiunile în valută ·
T31 completările manuale la declarații · T32 partida simplă · T33 exportul contabil · T34 rapoartele
comerciale și centrele de cost.

**Ce s-a lăsat în urmă:** nimic — toate probele au fost refuzate.

| # | rută | ce s-a introdus | ce a făcut aplicația | reparat |
|---|---|---|---|---|
| 246 | `POST /vanzare-ic` | corp gol | **`502` · *„VIES indisponibil: 'cod_tva_client'"*** — două lucruri într-un singur mesaj: o **afirmație falsă despre un serviciu extern** (contabilul crede că VIES e picat, când de fapt n-a completat un câmp) și **`str(KeyError)`**, adică numele câmpului între ghilimele simple. Cauza: citirea câmpului era **înăuntrul** `try`-ului care prinde `Exception` | **DA** — *ce nu s-a trimis nu se află de la VIES* |
| 239 · 262 · 265 · 268 | `d390-clasificare` · `d300-manual` · `d301-operatiuni` · `registru-evidenta-fiscala` | `luna=13` / `an=1900` | **AU CĂZUT** — `500` de patru ori | **DA** — `_cere_perioada` |
| 260 · 261 | `decontare-valuta` · `reevaluare-valuta` | `moneda=XYZ` | **A CĂZUT** — `500`. Rutele prind `(ValueError, KeyError)`, dar `MonedaNecotata` e subclasă de `CursIndisponibil`, care e `Exception`. **Reparația din lotul 2** — care deosebește „moneda nu există" de „cursul nu se poate lua acum" — trăia **numai pe calea facturii**; celelalte două căi n-o vedeau | **DA**, pe amândouă: `422` pentru monedă inexistentă, `409` pentru curs indisponibil |
| 243 · 276 · 281 · 282 · 286 | `intrastat-praguri` · `rip/registru` · `api/v1/kpi` · `cabinet/consolidare` · `centre-cost/varianta` | `an=1900` / `luna=13` | **TĂCERE** — `200`. `api/v1/kpi` întorcea chiar `{"an":2026,"luna":13,...}`, repetând luna imposibilă înapoi; `cabinet/consolidare` întorcea **firmele cabinetului**, cu KPI calculat pe luna 13 | **DA** |
| 289 | `GET /rapoarte-comerciale` | `pana < de` | `200` cu raport gol — „n-ai vândut nimic în perioada asta" arăta identic cu „perioada e scrisă invers". **A treia instanță** a clasei, după SAF-T (lot 6) și zilele lucrătoare (lot 7) | **DA** |

### Ce a răspuns `200` și **nu** e defect

- **`#258` `POST /vanzare-marja`** cu preț de vânzare **sub** cel de cumpărare: `200`, cu
  `"motiv": "marja negativa/zero - fara TVA, se reporteaza in jurnalul de marja"`. **E corect
  fiscal** — regimul de marjă permite vânzarea în pierdere, iar marja negativă nu produce TVA, se
  raportează. *Aplicația nu doar acceptă: explică de ce.*
- **`#291` `GET /rapoarte-salvate`** fără parametri: listă goală, care e chiar răspunsul.

### Trei probe oarbe, același fel ca la lotul 7

`#283` (centre de cost) n-are `an` în semnătură, `#286` are `an` dar nu `luna`, iar `#289` primește
un **interval** (`de`/`pana`), nu an/lună. Corectate; **`#286` și `#289` au devenit defecte reale
abia după corectare.**

### Cifre

- probe INVALIDE rulate: **50**, pe **43 de unități**, în **șapte trasee** · defecte găsite: **14** ·
  reparate: **14** · reprobate: **14**.
- distribuția la ultima trecere: **39 × 422 · 6 × 400 · 3 × 404 · 2 × 200** (ambele explicate mai
  sus) · **0 × 500** · **0 × 502**. Înainte: **5 × 500**, **1 × 502**, **9 × 200**.
- clase: **cădere pe perioadă** (4) · **cădere pe monedă inexistentă** (2 căi) · **afirmație falsă
  despre un serviciu extern** (1) · **tăcere pe perioadă** (5) · **interval inversat** (1).
- `_cere_perioada` are acum **treizeci și șapte** de apelanți. *Fiecare lot îl găsește într-un loc
  nou — iar asta e chiar măsura clasei: nu era o scăpare, era o lipsă de sistem.*

---

## LOT 9 — pachetul lunar și ciclul de viață al firmei (72 de probe INVALIDE pe 72 de rute)

T35 (pachetul lunar către client, 30) + **rutele** din T36 (ciclul de viață al firmei, 42).
**Cele 75 de ECRANE din T36 nu sunt aici**: nu se probează cu cereri HTTP, ci prin Playwright — altă
unealtă, deci alt lot.

**Două excluderi DELIBERATE, declarate înainte de probare:** `DELETE /tenants/{id}` și
`POST /gdpr/sterge-cabinet/{id}/executa` s-au probat **numai pe `999999`**. Sunt cele mai
distructive două acte ale aplicației; pe un id real, o probă care „trece" ar șterge o firmă sau un
cabinet întreg. *Nu se probează cu date valide ce nu se poate reface.*

### Două cereri GOALE care au produs efecte reale

| # | rută | ce a făcut | reparat |
|---|---|---|---|
| 382 | `POST /eu/competente` | **A SCOS TOATE DREPTURILE.** `CompetenteIn` avea toate cele trei câmpuri cu implicit `False`, deci un corp gol însemna *„scoate-mi tot"*. Probat, și s-a întâmplat: patronul **1968** — cel care depusese o declarație prin interfață cu o zi înainte — a rămas fără `poate_depune`. **Refăcut cu mâna** | **DA** — câmpurile n-au implicit: cine setează competențe le declară pe toate trei, iar cine nu trimite nimic primește un refuz, nu o golire |
| 369 | `POST /cabinet/api-chei` | **A CREAT O CHEIE FĂRĂ NUME**, rămasă activă. Cheia se arată **o singură dată**, la creare; una fără nume nu se mai poate recunoaște în listă ca s-o revoci. **Ștearsă** | **DA** — numele e obligatoriu, cu motivul scris în refuz |

*Amândouă sunt aceeași clasă ca `woocommerce/config` din lotul 7 și ca importurile din lotul 1b:
**o cerere fără conținut nu e o cerere de golire**.*

### Restul

| clasă | unde | ce era | ce e acum |
|---|---|---|---|
| **perioadă imposibilă** | `#295` `#297` `#298` pachetul lunar, cu `luna=13` | `200` — iar `#297` **genera HTML-ul pachetului** pentru luna 13 | `422`; gardat și `#296` (scrierea poveștii), care n-a fost probat dar are aceeași semnătură |
| **număr de zile negativ** | `#356` erori · `#358` semafor, cu `zile=-5` | `200`, iar `#356` repeta `"zile": -5` înapoi | `422` |
| **interval inversat** | `#355` centralizator · `#357` jurnal · `#380` calitate | `200` cu raport gol, **și cu intervalul inversat repetat înapoi** în răspuns. **A cincea, a șasea și a șaptea instanță** a clasei, după SAF-T (lot 6), zilele lucrătoare (lot 7), rapoartele comerciale și centrele de cost (lot 8) | `422` |
| **refuz deghizat în răspuns** | `#328` `PUT /clienti/999999` | `200` · `{"ok": false}` — fără motiv, fără cod. *„N-am putut actualiza" și „clientul ăsta nu există" nu sunt același lucru* | `404 client inexistent` |
| **parametru ignorat tăcut, pe o rută GDPR** | `#400` `GET /gdpr/export-cabinet?cabinet_id=X` | `200` cu **arhiva cabinetului TĂU**, oricare ar fi fost `cabinet_id`. Nu e o scurgere — dar pe o rută GDPR, „am exportat" despre alt cabinet decât cel cerut e cea mai proastă formă de tăcere: *arhiva pleacă mai departe cu numele greșit în minte* | `403`, cu ambele numere în mesaj |

### Ce a răspuns `200` și **nu** e defect

Cele **12 citiri de portal** (`#300`–`#318`), probate cu rol `client` și fără parametri, răspund
normal — n-au parametri obligatorii. `#337` `PUT /tenants/{id}` cu corp gol spune
`{"ok":true,"neschimbat":true}` — *declară că n-a schimbat nimic*, ceea ce e chiar forma bună.
`#324` cu căutare goală întoarce lista goală.

### Probele oarbe — a cincea oară, aceeași clasă

Șase probe trimiteau parametri **care nu există în semnătura rutei** (`#355`, `#357`, `#380` au
`de`/`pana`, nu an/lună; `#358` are `zile`; `#400` are `cabinet_id`; `#403` are `doar_necitite`;
`#333` are `inactive`). FastAPI lasă parametrii necunoscuți să treacă fără să se plângă nimeni.
**Patru dintre defectele reale ale lotului au ieșit la iveală numai după corectare.**

### Cifre

- probe INVALIDE rulate: **72**, pe **72 de rute**, în **două trasee** · defecte găsite: **13** ·
  reparate: **13** · reprobate: **13**.
- distribuția la ultima trecere: **40 × 422 · 14 × 403 · 3 × 404 · 1 × 400 · 14 × 200** (12 citiri
  de portal + două explicate mai sus) · **0 × 500**. Înainte: **28 × 200**.
- **cele 14 × `403`** sunt rutele de administrare (`/admin/*`, `/asistenti/*`, `/gdpr/*`) refuzate
  utilizatorului de probă — poarta de rol ține, și se vede.
- *Lotul ăsta n-a avut nicio cădere `500`. A avut, în schimb, **două cereri goale care au schimbat
  starea** — iar asta e mai greu de văzut decât o cădere: `200` arată ca un succes.*

---

## LOT 10 — ECRANUL: refuzul serverului ajunge la om, sau se pierde pe drum?

Primul lot care nu se probează cu cereri HTTP. Cele 75 de unități rămase din T36 sunt **ecrane**,
iar întrebarea campaniei are pe ele altă formă: *serverul a răspuns bine — dar ce citește omul?*

**Ce s-a lăsat în urmă:** nimic. Sonda de ecran a scris de două ori un centru de cost și un raport
salvat, ambele numite `«»@#$%`; **amândouă șterse**, verificat `centre_cost` 0 și
`rapoarte_salvate` 0. Toate celelalte 50 de tabele ale schemei, neatinse.

### Defectul de clasă: cele 13 descărcări care aruncau motivul serverului

Un răspuns binar (PDF, XML, ZIP, imagine) nu poate trece prin `api.get`, deci ecranele care
descarcă un fișier chemau `fetch` direct — și ocoleau `_refuzNevazut`, bannerul care din 27.08
garantează că un refuz la scriere nu rămâne nevăzut. **Măsurat cu `core/scan_descarcare_muta.py`:
toate 13 aveau aceeași formă** — `if (!r.ok) throw new Error("eroare " + r.status)`.

| ce spunea serverul | ce citea omul |
|---|---|
| `chitanță inexistentă` | **„Eroare — reîncearcă"** |
| `factură inexistentă` | **„Eroare — reîncearcă"** |
| `sablon inexistent` | „eroare 404" |
| `luna invalidă: 13 (aștept 1-12)` | „Nu am putut genera fluturașul." |
| `nicio factură emisă în luna aleasă` | „eroare 404" |

Cele două *„Eroare — reîncearcă"* sunt cel mai rău caz: **un sfat care nu poate reuși niciodată**,
fiindcă factura tot nu există la a doua apăsare. Omul apasă din nou, și din nou.

**Reparația e UNA, în `api.js`** — `cereBlob` / `descarca` / `deschide` —, nu treisprezece,
formular cu formular. Aceeași formă ca `refuz_vazut_v1`. Un `fetch` direct care descarcă un fișier
trece acum prin același loc care citește `detail` și pune bannerul. *Un GET pe care omul l-a cerut
apăsând un buton nu e o citire de fundal: excepția „GET-urile tac" e pentru contoare și badge-uri,
nu pentru un fișier care nu vine.*

A patrusprezecea instanță — importul extrasului bancar — a intrat pe `api.postForm`, care era deja
instrumentat.

### Cele trei defecte de SERVER, găsite probând aceleași căi

| # | rută | ce era | ce e acum |
|---|---|---|---|
| 456 | `POST /salariati/{id}/adeverinta` | pentru un salariat **inexistent** răspundea *„lipsește numele administratorului. Completează-l în Date firmă"*. Precondiția firmei se cerea **înaintea** căutării subiectului — un drum de reparat care nu duce nicăieri: și după ce-l completezi, salariatul tot nu există | `404 salariat inexistent`. *Ordinea întrebărilor E răspunsul.* |
| 456 | `POST /plata-salarii-fisier` cu `luna=13` | **`422 "month must be in 1..12"`** — mesajul bibliotecii, în engleză, ajuns până la contabil. Aceeași clasă cu `str(KeyError)` din lotul 8 | `422 luna invalidă: 13 (aștept 1-12)` |
| 487 | `GET /portal/documente/balanta` cu `luna=13` | **`200` cu PDF-ul tipărit** pentru luna 13. Calea de cabinet (`/tenants/{id}/documente/balanta`) o refuză din lotul 3; calea de portal, care produce **același document** pentru client, n-a aflat niciodată | `422`. **A opta instanță** a clasei „aplicația știe într-un loc și nu știe în altul" |

### Infrastructura vizuală trăia pe bytecode

`frontend_test/w_auth.py` — tokenul mințit și navigarea la firmă, de care atârnă `interactiune_scan`,
`axe_scan`, `mobil_scan` și `nav_ecrane` — **fusese șters de pe disc pe 26.08**, odată cu `b87dad49`
(„Scoate din urmărire cele 234 de artefacte măturate din greșeală"). Timp de nouă zile, **24 de
fișiere** s-au importat dintr-un `.pyc` de 4,6 KB rămas în `__pycache__`. Nimic n-a devenit roșu:
Python încarcă bytecode fără să-i ceară sursa. *Un `find -name __pycache__ -delete` — curățenia
obișnuită, cea care e chiar regulă în casă — ar fi oprit tăcut toată infrastructura vizuală.*

Sursa e **reconstruită din bytecode** (dezasamblare, funcție cu funcție) și verificată rulând
scanurile. `core/test_infra_vizuala.py` cerea fișiere **dintr-o listă**, iar `w_auth` nu era în ea
și nici măcar în același director; acum **derivă** ce trebuie să existe din chiar `import`-urile
uneltelor. Calibrat pe viu: mutat `w_auth.py`, garda cade numind modulul; pus la loc, trece.

### Ce a răspuns bine, și merită scris

Cele **8 butoane de scriere** apăsate cu formularul umplut cu date imposibile (`«»@#$%`,
`-99999999`, `1899-02-30`) — **toate 8 vorbesc**, zero tăceri. Cele mai bune sunt cele care
colectează *toate* câmpurile lipsă odată și marchează fiecare cu `aria-invalid`, nu doar pe primul:
vectorul fiscal și planul de conturi. Iar planul de conturi răspunde la un simbol imposibil cu
*„Simbolul contului începe cu cifra clasei (1-9), ca toate conturile din planul general — am primit
'«»@#$%'"* — numește regula, clasa și ce a primit.

### Instrumentul a greșit în ambele direcții, și de două ori

1. **Prima variantă a scanului** clasa forma din `app.js` (`.then((r) => r.json().then(...))`) drept
   „fără ramură de eșec", deși tratează refuzul corect. *Un instrument care pune un caz bun într-o
   categorie greșită minte și când nu acuză pe nedrept.*
2. **Prima variantă a sondei de ecran** căuta semnele refuzului după clasele din convenție
   (`.msg-eroare`, `[role=alert]`) și a raportat **„TACE" despre patru butoane**. Trei minciuni în
   una: `migrare.js` își scrie eroarea într-un `.mig-eroare` (clasă proprie — instrumentul care
   caută convenția nu vede ecranele care n-o urmează), iar alte două **nu tăceau, ci reușeau** —
   scriseseră în baza de date. Sonda măsoară acum **text nou vizibil**, nu clase, și numără starea
   tuturor celor 52 de tabele înainte și după fiecare apăsare. Verdictele sunt trei, nu două:
   **a vorbit** · **a scris** · **TACE**. *O sondă „de citire" scrie până n-o dovedești.*

### Cifre

- probe INVALIDE rulate: **13** pe rute de descărcare · **8** pe butoane de ecran, în **15 ecrane**
  parcurse · **1** probă pe viu în browser (5 aserțiuni) · defecte găsite: **5** · reparate: **5** ·
  reprobate: **5**.
- clasa mare: **14 locuri** care aruncau motivul serverului → **0**, măsurat de
  `core/scan_descarcare_muta.py`; 15 cereri directe tratează acum refuzul, 1 excepție declarată
  (telemetria `keepalive`), 1 fișier exceptat cu motiv (`versiune.js`, cerere către un fișier static).
- pe ecran: **8 butoane probate, 8 vorbesc, 0 tac, 0 scrieri rămase, 0 erori JS**.
- gărzi noi: `core/test_descarcare_muta.py` (8 teste, din care **6 de calibrare** — două forme mute
  injectate, două forme bune care nu trebuie acuzate, una pe propriul mod de eșec) +
  `core/test_infra_vizuala.py` (2 teste noi, unul anti-vacuu).
- `_cere_perioada` are acum **patruzeci și doi** de apelanți.
- *Lotul ăsta n-a găsit nicio cădere `500`. A găsit, în schimb, un strat întreg care înlocuia
  răspunsul serverului cu al lui — și o infrastructură de testare care mergea fiindcă nimeni nu
  ștersese încă un director temporar.*

### Ce a scos POARTA lotului 10, și nu era despre ecrane

Poarta a respins de opt ori, și una singură merită scrisă aici: *„scrieri NOI care pot refuza fără
să spună motivul: **18 > 16**"*, cu două intrări noi în `ecrane/facturi_ecran.js`. Citit ca atare,
lotul stricase două ecrane.

**Măsurat înainte de reparat, pe un worktree detașat la `277e4300`** — commitul de dinaintea
lotului, deci fără nicio schimbare a lotului în el —, cu cititorul reparat: **18 și acolo**. Lotul
n-a adăugat nicio scriere mută. A **mutat o linie de cod** din `facturi_ecran.js` în `api.js` —
`cd.match(/filename="([^"]+)"/)`, chiar reparația R131 —, iar odată cu ea s-a mutat **orbirea
instrumentului**: a treia ghilimea deschidea un „șir" care înghițea sute de rânduri.

Cele două clichete care stau pe cititorul acela se mișcaseră în **direcții opuse** în aceeași zi:
unul prea mic (16 în loc de 18), celălalt prea mare (2 în loc de 1). *Asta e semnul, și e scris în
METODA §22: un instrument care greșește în amândouă direcțiile n-are niciun plafon.* Reparația și
cifrele, la **R133**.

*Nu e o lecție despre ecrane. E despre ce se întâmplă când mesajul unei porți respinse se citește
ca diagnostic: „18 > 16" spune că sunt 18, nu că lotul a făcut două.*

### Ce a rămas nereparat din lotul ăsta, și de ce

1. **Cele 18 scrieri care refuză fără să spună motivul rămân mute la locul lor.** Plasa din
   `api.js` le prinde pe toate — un refuz nu rămâne nevăzut —, dar un mesaj lângă butonul apăsat
   e mai bun decât un banner. Clichetul e ca să nu **crească**, nu ca să fie declarată rezolvată;
   asta scrie în `core/test_refuz_tacut.py` din 27.08 și nu s-a schimbat. *Ce s-a schimbat azi e
   doar cifra: 16 era greșită, 18 e măsurată.*
2. **Două din cele 18 nu sunt defecte deloc, și nu se pot deosebi automat.** Una cheamă o funcție
   proprie care afișează (`plaseazaErori`), cealaltă e o căutare de fundal la tastare — un `POST`
   folosit ca citire. Sunt exact modurile de eșec 1 și 3 pe care instrumentul și le declară în
   antet: nu execută JS, și deosebește citirea de scriere după **metodă**. *Ca să se poată
   deosebi, instrumentul ar trebui să știe ce face funcția chemată — adică să fie un alt
   instrument.*
3. **Cele 9 ecrane parcurse cu `campuri=0` n-au fost probate cu adevărat.** Formularul lor cere un
   pas înainte — alegerea unei luni, a unui partener, deschiderea unei ferestre. Sonda le-a
   parcurs și n-a avut ce completa, deci „a tăcut" nu se poate afirma despre ele. *Cer o cale de
   navigare scrisă de mână, și aia e construcția lotului 11.*
4. **Cititorul nou nu recunoaște o expresie regulată scrisă imediat după `}`** (`if(x){}/re/`).
   `}` nu e în mulțimea de dinaintea unui regex fiindcă `{…}` e și obiect, iar `obj/2` e împărțire.
   Direcția ratării e cea sigură — expresia rămâne vizibilă ca și cod, nu dispare cod real —, și e
   scrisă ca modul de eșec 1 în `core/cititor_js.py`. *Zero instanțe în corpusul de azi; se
   consemnează fiindcă e o alegere, nu o scăpare.*

---

## LOT 11 — cele 21 de ecrane de firmă rămase, și formularul care se deschide abia după o apăsare

Lotul 10 a parcurs 15 ecrane și a raportat, pentru **nouă** din ele, `campuri=0`. Citit repede, asta
înseamnă „ecran parcurs". Nu însemna: formularul lor trăiește într-o **fereastră** care se deschide
după o apăsare — «+ Salariat nou», «+ Notă nouă», «+ Șablon nou» —, iar sonda ajungea pe ecran și
n-avea ce completa. *Un `campuri=0` era un ecran NEPROBAT purtând numele unuia probat.*

**Ce s-a construit:** navigare pentru cele 21 de ecrane `fa-*` care nu erau în nicio listă
(`nav_ecrane.ECRANE_CAMPANIE`), și un pas de **deschidere** în sondă: dacă nu se găsește niciun câmp,
se caută un deschizător, se apasă, și se recontrolează. Ce s-a deschis se scrie în artefact
(`deschis_cu`) — ca să nu se confunde niciodată un ecran care n-are formular cu unul al cărui
formular n-a fost găsit.

**Măsurat, cap la cap:** 36 de ecrane parcurse (15 + 21) · **16 butoane apăsate** pe formulare umplute
cu date imposibile · **15 au vorbit** · **1 a cerut un fișier** · **0 TAC**. Butoanele au crescut de la
8 la 16, iar `stat_plata` a trecut de la `campuri=0` la **14 câmpuri**, prin deschizător.

### Ce a scos ecranul «Date firmă» — trei defecte, pe același drum

| # | ce era | ce e acum |
|---|---|---|
| **R134** | `PUT /tenants/{id}` răspundea **`500 Internal Server Error`** la ORICE refuz. Porțile puse pe 27.08 (cifra de control a CUI-ului, unicitatea) refuză ridicând `ValueError`, iar ruta nu-l prindea. Mesajele scrise cu grijă n-au ajuns niciodată la un contabil | `422`, cu motivul întreg |
| **R135** | aceeași rută accepta **`«»@#$%` ca denumire de firmă** și o scria în amândouă locurile. De acolo pleacă pe `den` din D394 și pe antetul facturii | refuz, din scriitorul UNIC, deci fără cale de ocolire |
| **R136** | ecranul trimitea **trei scrieri înlănțuite**, cu redenumirea PRIMA. Măsurat în `audit_log`: `PUT /tenants/4838` `200`, apoi `POST /firma-profil/date` `422` — refuz pe ecran, firmă redenumită în date | se scrie întâi ce poate fi refuzat; iar dacă denumirea cade după, mesajul o spune pe litere |

*Al doilea nu se putea vedea cât timp exista primul: cu orice refuz ieșind `500`, nimeni n-ar fi
deosebit „poarta lipsește" de „poarta a căzut".*

### Ce a scos SONDA despre ea însăși (R137)

Sonda declara starea schemei ca `count(*)` pe fiecare tabel. Un ecran de **date** nu inserează —
**modifică**. Deci, când a redenumit firma, sonda a raportat *„SCHIMBĂRI DE STARE: niciuna"*. S-a
văzut abia indirect: următoarele 14 ecrane au dat „navigare eșuată", fiindcă navigarea caută firma
**după nume**, iar numele nu mai era al ei. Numele vechi s-a refăcut citindu-l din D394-urile
**depuse**, nu din memorie.

Reparat pe trei direcții: starea e acum `count/amprentă` · verdictele sunt **patru**, al patrulea
fiind *„a cerut un fișier"* (butonul care deschide selectorul de fișiere **nu tăcea**) · iar
curățenia de după probă e o unealtă cu **granița scrisă** — un `INSERT` se desface, un `UPDATE` nu,
și acolo instrumentul refuză în loc să șteargă date reale.

### Cele trei acceptări care NU sunt defecte

`rapoarte_salvate`, `centre_cost` și `contracte_sabloane` au primit `«»@#$%` și l-au **scris**, cu
mesaj de reușită. Sunt corecte: toate trei sunt **nume libere alese de contabil** — o variantă de
raport, un centru de cost, un șablon de contract. Nu pleacă în nicio declarație. *Un instrument care
ar refuza aici ar fi mai rău decât unul care acceptă.* Rândurile au fost șterse după probă, verificat.

### Ce a rămas nereparat din lotul ăsta, și de ce

1. **`fa-rip` n-a fost probat: cardul nu se randează pe firma campaniei.** `Comert Micro TVA SRL` e
   SRL, iar Registrul de Inventar și Plăți e al partidei simple. Sonda a raportat „navigare eșuată",
   nu „fără defect". *Decizia lui Costin (`DECIZII.md` 31): lotul 12 rulează și pe o firmă de partidă
   simplă, și numai pe ce nu se randează acum.* **Punctul orb e FIRMA, nu ecranul.**
2. **Opt ecrane au formular, dar niciun buton de salvare**: `acces`, `bilant`, `fisacont`, `marja`,
   `regfiscal`, `reginventar`, `registre321`, `solicitari`. Câmpurile lor sunt **filtre** (lună, an,
   cont), nu date de înregistrat — n-au ce refuza. Sunt scrise „parcurse", nu „probate": deosebirea e
   chiar ce a costat lotul 10 nouă ecrane.
3. **Paisprezece ecrane au `campuri=0` și după deschizător.** Formularul lor cere **doi** pași
   (alege luna → deschide fereastra), iar sonda încearcă cel mult trei deschizătoare, fiecare de un
   singur pas. Declarat ca mod de eșec în antetul sondei.
4. **R136 e îngustată, nu închisă.** Dacă redenumirea — acum ultima — cade după ce profilul și
   vectorul au trecut, ele rămân salvate. Un singur act ar cere o rută care unește trei căi cu
   **roluri diferite** și un apel ANAF live: o construcție, nu o reparație de lot.
5. **Sonda umple numai ce e în `.fereastra`.** Un formular randat inline, în corpul ecranului, nu e
   completat — și atunci `campuri=0` rămâne onest: „n-am avut ce completa", nu „nu refuză".

---

## LOT 12 — ecranele care nu sunt ale unei firme, și prima firmă de partidă simplă

Cele 33 de unități rămase la nivel de FIȘIER (`#462`–`#501`) sunt de altă natură decât tot ce a fost
până acum: trăiesc pe **desktopul unui rol** — cabinet, admin — și nu se ajunge la ele prin nicio
firmă. Plus o a doua firmă, cerută de `DECIZII.md` 31.

### Ce a trebuit construit înainte de a putea proba ceva

1. **`w_auth` emite sesiune pentru orice rol, pe calea aplicației.** Până azi construia dicționarul
   `iconta_user` câmp cu câmp, și **trei** câmpuri erau inventate: `nume_tenant: None`,
   `tenant_are_cabinet: False`, `bun_venit_vazut: True`. Pe `admin_firma` se nimereau adevărate, deci
   nimic n-a căzut vreodată. Măsurat pe rolul `client`: adevărul e `nume_tenant: "ALFA MICRO SRL"`,
   `tenant_are_cabinet: true` — iar `navigator.contextBara` randează chiar `nume_tenant` în bară.
   *O sondă care își fabrică singură intrarea dovedește că ecranul merge pe intrarea pe care i-o dai
   TU (R125).* Acum sesiunea vine din `auth_api.sesiune_pentru_user`, funcția pe care o cheamă
   aplicația la magic-link: același `SELECT`, aceleași câmpuri, aceeași verificare de `activ`.
2. **Un context de browser per ROL.** `app.js` alege desktopul din `sesiune.rol()` **la pornire**,
   deci rolul nu e un parametru al navigării: e o proprietate a filei.
3. **Navigare scrisă pentru 22 de ecrane** (`nav_ecrane.ECRANE_CABINET`), cu contul lângă fiecare.
   *Aserțiunea anti-vacuu a listelor a prins, la prima rulare, o coliziune reală: `fa-control`
   (ecranul UNEI firme, #436) și cardul de portofoliu «Control fiscal» (#474) purtau același nume
   scurt — două ecrane diferite care ar fi apărut ca unul.*
4. **Firma nu mai e scrisă în cod.** `deschide_firma` avea „Comert Micro TVA" hardcodat, deci orice
   unealtă vizuală vedea numai stările pe care le produc datele acelei firme.

### Prima firmă de partidă simplă din bază

**Măsurat înainte de a construi ceva: toate cele 19 firme erau `srl`.** Cardul `#fa-rip` se randează
numai la `regim_contabil == "simpla"` — deci nu era un ecran neprobat, era un ecran pe care nimeni
nu-l putuse deschide vreodată, și toată ramura de partidă simplă cu el.

Firma s-a făcut **prin lanțul aplicației** — `POST /tenants` cu `tip_firma: "pfa"` —, nu printr-un
`INSERT`, la cabinetul declarat de TEST (4163) ca să nu miște numărătoarea firmelor reale, cu CUI
care trece cifra de control ANAF (verificat cu trei validatoare din corpus).

Măsurat pe ea, cardurile: **31 pe partidă dublă · 22 pe partidă simplă · 21 comune**. Singurul card
exclusiv partidei simple e **`#fa-rip`** — deci „doar ce nu se randează pe firma curentă" înseamnă,
măsurat, exact un ecran. Ce **dispare** la partida simplă sunt zece carduri deja parcurse pe dublă
(`balanta`, `bilant`, `centrecost`, `fisacont`, `jurnal`, `marja`, `mijloace`, `operatiuni`,
`reginventar`, `stocuri`).

### Cele trei defecte, toate găsite apăsând

| | ce era | unde ajungea |
|---|---|---|
| **R138** | `«»@#$%` **conține** un `@`, iar patru rute verificau doar `"@" not in email` | `POST /asistenti` ar fi făcut `INSERT` în `public.users` cu emailul `«»@#$%`, rol `angajat`, **și ar fi trimis emailul de activare** |
| **R139** | refuzul de pe linia facturii punea lângă câmp chiar **eticheta** câmpului, iar rezumatul spunea *„Completează"* despre un câmp completat | emitere + facturi recurente |
| **R140** | cele opt refuzuri ale registrului de partidă simplă vorbeau limba programatorului (`suma trebuie să fie > 0`, `valuta != RON: suma_valuta si curs_valutar`); șapte din opt fără diacritice | singura cale de refuz a partidei simple |

**R138 e cel care contează cel mai mult, și motivul e o măsurătoare, nu impresia:** din **cele șase**
locuri care refuză cu `EMAIL_INVALID`, **unul singur** verifica formatul. Patru se mulțumeau cu un
`@` — și toate patru **creează un cont** sau **dau un acces**. Regexul corect trăia deja în
`main.py`, și copiat în `notificari_scadenta.py`. *Aceeași aplicație știa răspunsul într-un loc și
nu-l avea în altul.*

*Butonul care a găsit R138 nu se putea apăsa înainte de reparație: apăsarea lui ar fi produs chiar
contul și emailul pe care le descrie defectul. S-a citit întâi ruta, s-a reparat, apoi s-a apăsat.*

### Ce a măsurat sonda, cap la cap

23 de ecrane parcurse, pe **trei conturi** · **0 navigări eșuate** · **8 butoane apăsate** (7 pe
formular umplut) · **5 au vorbit** · **1 a cerut un fișier** · **0 TAC** · **0 scrieri** — amprenta
tuturor celor **103** tabele ale celor două scheme, identică înainte și după.

### Instrumentul a fost reparat în timpul lotului, și în direcția OPUSĂ celei de data trecută

Lotul 10 a reparat **sub-numărarea**: „a vorbit" se măsoară pe text nou vizibil, nu pe clasele din
convenție. Lotul 12 a găsit **supra-numărarea**: din șase „a vorbit" la prima rulare, **trei** erau
text nou care nu răspundea la nimic — o fereastră care s-a închis, o navigare către alt ecran, un
buton care a mai adăugat o linie de formular. *Același instrument greșea în amândouă direcțiile,
deci n-avea **niciun** plafon (METODA §22).*

Deosebirea nu se poate face pe text, și nu se face pe text: se numără câmpurile care mai poartă
**valoarea-santinelă** pe care am scris-o eu, înainte și după apăsare. Dacă formularul umplut nu mai
e acolo și nimic nu s-a scris, butonul nu mi-a răspuns — m-a dus în altă parte. Verdictele noi:
**a plecat de pe formular** · **a crescut formularul** · **sărit: e deschizătorul**.

Calibrat în amândouă direcțiile pe date reale: cele trei false „a vorbit" s-au reclasificat, iar cele
două adevărate (`flux_concediu`, `admin_anunturi`) **au rămas** „a vorbit".

### Trei granițe ale sondei, mutate — fiecare fiindcă ar fi produs o afirmație falsă

- **Câmpurile nu se mai caută doar în `.fereastra`.** Un desktop de rol nu e o fereastră: acolo
  `campuri=0` n-ar fi însemnat „n-are formular", ci „n-am știut unde să mă uit". Domeniul ales se
  scrie în artefact.
- **Selecturile se aleg, și sunt declarate ca VALIDE.** Într-un `<select>` nu se poate tasta
  `«»@#$%`. Alegerea e **pasul care deschide formularul**, nu obiectul probei.
- **Starea se măsoară pe TOATE schemele atinse.** Ecranul RIP trăiește pe altă schemă; o sondă care
  numără `tenant_003` în timp ce apasă pe `tenant_048` ar fi raportat „n-a scris nimic" despre
  scrieri pe care nu le vede. *A treia instanță a clasei „sonda era oarbă" — și singura prinsă
  ÎNAINTE de a raporta.* Curățenia de după probă a fost lărgită la fel: un „STARE CURATĂ" despre o
  schemă neprivită e chiar gardul care nu se verifică pe sine.

### Două butoane pe care instrumentul le-a oprit, și de ce contează

- **«Generează cu AI» / «Generează analiză AI»** — verificat la sursă: `/tipare/ai` cheamă
  `core.ai_client`, iar `/pachete/{}/genereaza` trece prin `genereaza_poveste`. **Ies din
  aplicație**, contra cost, exact ca `depune`/`trimite`. Oprite pe același temei, nu pe altul.
- **«Trimite alertă de test»** (Sănătate server) — ar fi trimis o alertă REALĂ prin Brevo. Oprit de
  regula existentă, și bine că era acolo.

Iar unul a fost **deblocat**, cu ruta citită și numită: «Trimite» de pe ecranul de anunțuri face un
`INSERT` în `public.anunturi_cabinet` (main.py:676) și atât. *Lista `OPRITE` decide după NUME, iar
numele nu spune unde ajunge acțiunea — fără excepție, singurul formular din `admin.js` ar fi rămas
neprobat, iar raportul ar fi spus „fără defect" despre un ecran pe care nu l-am apăsat.* Excepția se
cere pe textul ÎNTREG, nu pe bucată: „trimite" ca substring ar fi deblocat și «Trimite invitația»,
care chiar pleacă prin email.

### Cifre

- unități mutate din `neprobat`: **12** (8 probate prin apăsare · 4 verificate prin citire).
  Campania: **322 probate · 42 rămase** din 364.
- defecte găsite: **3** · reparate: **3** · reprobate: **3**.
- clichetele refuzurilor, măsurate înainte și după R140: **n-au mișcat**.

### Ce a rămas nereparat din lotul ăsta, și de ce

1. **`TVA 0,00 RON` se afișează pe ecranul de emitere când cota nu se știe.** `recalc()` face
   `l.cota_tva || 0`, deci o cotă necunoscută devine zero, iar «Total» ajunge egal cu «Bază» pe o
   firmă plătitoare de TVA. Arată ca interdicția 32 (*un necunoscut nu se rotunjește la „știu că
   nu"*) — **dar nu e**: garda R29 declară explicit în afara domeniului ei „defaultul pe ZERO
   (`cota or 0`) — altă clasă, legitimă în aritmetică, **18 instanțe reale**". A repara aici ar
   însemna deschiderea acelei clase, adică o **temă**, nu o reparație de prag 1. *Se consemnează cu
   măsurătoarea, ca să nu fie regăsită ca nouă.*
2. **`«Emite factură»` deschide întâi poarta de stoc** («Pleacă marfa acum?»), deci apăsarea din
   sondă se oprește acolo. Refuzul propriu-zis a fost probat pe rută și în probă țintită, nu prin
   sondă. *Un răspuns care vorbește despre alt lucru decât cel probat nu se notează ca răspuns la
   proba mea.*
3. **`asistent.js` (#470) n-are subiect viu.** Desktopul asistentului cere rolul `angajat`, iar
   singurul cont cu rolul ăsta din bază e **inactiv** — `sesiune_pentru_user` îl refuză. Nu e „fără
   defect", e un ecran fără cont. Se probează după reactivarea lui **prin calea aplicației**
   (`/asistenti/{id}/reactiveaza`), nu printr-un `UPDATE`.
4. **Trei formulare n-au putut fi apăsate fără să iasă ceva real din aplicație**: `recomanda`
   («Trimite invitația» = email), `raporteaza` («Trimite sesizarea» = email), `pachete` («Generează
   cu AI» = furnizor extern). Câmpurile lor s-au umplut; butonul nu s-a apăsat. Declarat, nu ascuns
   într-un „fără defect".
5. **Cele 14 rute marcate `403` în lotul 9 rămân „fără defect" pe temeiul unui refuz de ROL, nu al
   verificărilor lor proprii.** Lotul 9 o scrie corect (*„poarta de rol ține, și se vede"*), dar
   rândurile din listă spun doar „fără defect". `POST /asistenti` era una dintre ele — și avea R138.
   *O rută refuzată de poarta de rol n-a ajuns la gărzile ei; ce s-a măsurat acolo e poarta, nu ruta.*
   Nu se corectează în lotul ăsta: sunt 14 rânduri de reprobat cu un token de rol potrivit, adică un
   lot, nu o notă.
6. **`"suma trebuie să fie > 0"` mai trăiește în `core/casa_api.py` și în `main.py`** (chitanța).
   Sunt pe calea partidei duble, deja probată în alte loturi; rescrierea lor fără reprobare ar fi o
   schimbare nemăsurată.
7. **Douăzeci și unu de ecrane rămân `neprobat — parcurs`**, cu motivul scris pe fiecare rând: fără
   niciun câmp în DOM (afișare pură), sau cu formularul la doi pași de deschizător. *Un `campuri=0`
   nu e „fără defect".*

### După raport — cele patru decizii ale lui Costin, aplicate

**(1) Garda de LOC** — construită în `core/test_conformitate.py`, pe structură: compară mulțimea
antetelor `### Rn` din tot documentul cu cea văzută de `_restante()`. **Mutație dovedită pe date
reale**, nu doar pe document sintetic: cu R141 scos din secțiune, garda o numește exact pe ea.

**(2) Cele „14" rute — sunt CINCI, și cifra era a mea.** O scrisesem în raport dedusă din proza
lotului 9, fără s-o măsor. Măsurat la sursă și confirmat prin reapăsare: `403` real pe
`/admin/analytics` · `POST /admin/anunturi` · `/gdpr/sterge-cabinet/{}/executa` ·
`/admin/activitate/cabinet/{}` · `/admin/sanatate/istoric`. Celelalte nouă cer `admin_firma` sau
`cere_cabinet` — rol pe care utilizatorul probei îl avea, iar patru dintre ele **chiar au găsit
defecte**, ceea ce dovedește că au ajuns la logica lor. Cele cinci sunt acum `neprobat`, cu motivul
pe rând; se reprobează în lotul 14.

*Și o corectură despre `POST /asistenti`:* R138 n-a scăpat printr-o poartă de rol — ruta era
accesibilă. Lotul 9 a probat-o cu **corp gol** și a primit un refuz corect. A scăpat fiindcă
valoarea trimisă nu era greșită **în felul care conta**: `«»@#$%` conține un `@`.

**(3) Desktopul asistentului (#470), probat pe cont reactivat prin ruta aplicației.** 7 carduri,
**0 câmpuri și 0 selecturi**, 0 erori JS; bara a treia — motivațională, doar la rolul `angajat` — se
randează cu cifre reale. Contul a fost dezactivat la loc în `finally`, iar starea **recitită din
bază**: `False` → `True` → `False`. Cardurile lui deschid ecrane deja probate pe contul de cabinet.

**(4) Cota necunoscută nu se mai afișează ca zero (R142).** Pe o linie cu valoare și fără cotă
stabilită, «TVA» și «Total» sunt acum `—`, cu o notă care spune de unde vine cota. O linie de
valoare zero **nu** blochează totalul: la valoare zero TVA-ul e zero oricare ar fi cota.

*Calibrat în amândouă direcțiile, în browser:* linie goală → «Total 0,00» · linie cu valoare, cotă
neștiută → «—» + notă · **după ce cota se propune (21%) → «TVA 420,00 · Total 2.420,00»**. A treia
direcție e cea care contează: reparația nu supra-refuză.

*Și o corectură a propriei reparații, prinsă reprobând:* prima formă a notei spunea *„Alege
articolul, **sau cota**"* — și nu există niciun control de cotă; coloana e un `<span>`, iar valoarea
vine numai din `POST /produse/potriveste`, propusă din denumire. **Un refuz care trimite omul să
facă ceva ce nu poate face e mai rău decât unul scurt.**

**Ce a costat reparația, și n-a fost prevăzut:** R142 a atins JS-ul ecranului, deci regula casei l-a
mutat în inventarul porții vizuale — iar `axe` a găsit imediat **două violări preexistente**, una
CRITICĂ: `select-name` pe `#em-moneda` (etichetă fără `for=`) și pe `#em-tip`, selectorul care alege
FACTURĂ / PROFORMĂ / AVIZ. Plus contrast sub prag pe două reguli. Reparate (**R143**), ecranul e acum
în inventar cu **zero** violări. *Regula „un ecran atins primește cele trei unelte" și-a arătat în
aceeași tură și prețul, și rostul.*

### Cifrele campaniei, după aplicarea deciziilor

**317 probate · 47 rămase** din 364. Scăderea față de 322/42 nu e o regresie: sunt cele **cinci** rute
mutate din „fără defect" în „neprobat", fiindcă așa e adevărat.

---

## LOT 13 — «Operațiuni speciale»: treizeci și două de formulare sub un singur rând de listă

### Ce a arătat măsurarea populației

Cele 42 de ecrane rămase nu sunt un rest omogen. Grupate mecanic, după motivul scris pe fiecare
rând: **12** fără niciun câmp în DOM (afișare pură) · **13** cu formularul la doi pași de
deschizător · **7** numai cu câmpuri de FILTRU · **3** al căror buton iese din aplicație · **7**
neîncadrate, între care patru neparcurse niciodată.

Diagnosticul grupei celei mari a răsturnat presupunerea: ecranele cu `campuri=0` **nu sunt „fără
formular" — sunt MENIURI.** Formularul e cu un nivel mai jos.

### Descinderea prin meniuri aduce puțin — cu o excepție care aduce mult

Măsurat pe zece ecrane: `facturi` are 6 opțiuni, dintre care **una** duce la un formular (emiterea,
deja probată la #478) · `verificari` are 6, toate rezultate, nu formulare · `jurnal` are 4 rânduri de
listă · `mijloace` are **zero** — și nu e stricat: e o **stare goală**, cu un mesaj care numește chiar
calea de adăugare (*„Se adaugă la migrare sau prin Operațiuni speciale → Inventariere anuală"*).
*Punctul orb e FIRMA: firma campaniei n-are mijloace fixe.*

Excepția e **«Operațiuni speciale»**: **32 de feluri de operațiune**, fiecare cu formularul lui și cu
propriul buton «Generează nota (ciornă)» — toate sub **un singur rând** al listei (`#447`). Un
„probat" pe rândul acela ar fi spus, până azi, ceva despre **unul din 32**.

### A treia oară în aceeași tură când propriul meu instrument a raportat fals

Prima enumerare a celor 32 a apăsat pe **poziția din DOM** (`data-op="i"`), după o re-navigare — iar
pozițiile se re-atribuie, deci clicurile cădeau alături. Rezultatul arăta ca o descoperire:
*„niciun formular nu se deschide, 0 din 32"*. Probat cu grijă pe un singur caz, «Leasing» deschide un
formular întreg. Se navighează pe **NUME**.

*(Celelalte două din tura asta: „a vorbit" acordat unui text nou care nu răspundea la nimic, și cifra
„14 rute" dedusă din proză. Toate trei prinse înainte de a fi raportate ca fapt.)*

### Și a patra: santinela de dată nu ateriza

La prima rulare reală, **toate cele 32** au răspuns identic: *„Camp obligatoriu: Data"*. Cauza nu era
aplicația: `1899-02-30` **nu e o zi din calendar**, deci `input[type=date]` refuză valoarea în
browser și câmpul rămâne **gol**. Proba măsura un câmp LIPSĂ, nu o dată imposibilă — și o făcea așa
**din lotul 10 încoace**, pe fiecare câmp de dată al campaniei. Înlocuită cu `1899-01-01`: o zi care
există, și e la fel de imposibilă ca dată contabilă.

*Abia atunci cele 32 de formulare au fost probate cu adevărat.*

### Rezultatul: 32 au vorbit, 0 au scris, 0 au tăcut

Iar calitatea mesajelor se vede acum, nu se presupune. Cele bune numesc câmpul, spun ce e greșit și
citează temeiul:

- *„Contul «»@#$% nu există în planul firmei (câmpul „cont_imobilizare")."* — Leasing
- *„Procentul taxei vamale e între 0 și 100 — am primit -99999999."* — Import extracomunitar
- *„Cota 1000 nu e o cotă în vigoare (art. 291 Cod fiscal) la data operațiunii (2026-09-01). Cotele
  de atunci: 0%, 11.00%, 21.00%."* — apărut la reprobare, și e exemplar

### Cele două defecte, amândouă de prag 1

**R144 — «Aur de investiții (art. 313)» cădea cu `500`.** `Decimal(str("«»@#$%"))` ridică
`decimal.InvalidOperation`, care e `ArithmeticError`, **nu** `ValueError` — iar ruta prinde numai
`ValueError`. Deci textul tastat de un om ieșea ca eroare de server, iar contabilul citea *„eroare
500"* în loc să afle ce câmp e greșit. **Aceeași clasă ca R134.** Reparat în motorul pur, pe
contractul lui — și pe **toate patru** intrările numerice, nu doar pe cea care a căzut: *a repara
doar instanța ar fi lăsat trei uși deschise pe același hol.*

**R145 — «Chirii / comodat / refacturări» nu putea reuși NICIODATĂ din ecran.** Formularul colecta un
singur câmp, «Suma», și îl trimitea așa; ruta cere nume **diferite după `fel`** — `valoare` la
comodat, `chirie` la chirii, iar la refacturare **două** sume (`total_factura` + `parte_refacturata`).
Confirmat cu **date perfect valide**: răspunsul era *„Lipsește câmpul `valoare` din cererea
trimisă"*. *Întrebarea nu era dacă refuză, ci dacă poate reuși vreodată.*

Reparat în ecran, cu `cond` — mecanismul exista deja acolo. Iar reparația a scos un al doilea defect,
al ei: câmpul `chirie` e cerut la **două** feluri, iar declarat de două ori producea **două elemente
cu același `id`**, deci valoarea nu se mai colecta pe al doilea. Condiția acceptă acum o listă de
valori.

**Reprobat pe toate patru felurile, cu date valide:** comodat → 1 notă · chirie plătită → 1 · chirie
încasată → 1 · refacturare → **2** (cum spune contractul ei). Cele 6 note ale probei s-au șters
**prin ruta aplicației** (`DELETE /tenants/{}/jurnal/{}`), iar starea s-a recitit din bază.

### Ce a rămas nereparat din lotul ăsta, și de ce

1. **Șase din cele 32 de refuzuri vorbesc încă limba programatorului**: *„suma incasata trebuie sa
   fie pozitiva"* · *„bacsis invalid"* · *„mijloc fix inexistent/inactiv"* · *„valoare invalidă"*
   (nu spune care) · *„tara '' nu este stat membru UE (VIES)"* · *„nicio varianta de formula valabila
   la 1899-01-01"*. Aceeași clasă ca R140, cu precedentul deciziei lui Costin — dar fiecare cere
   reparație **și** reprobare proprie. Măsurate și numite; se repară în lotul următor.
2. **Cele 32 de formulare au etichete fără diacritice** („Tip operatiune", „Valoare reziduala",
   „Dobanda totala"). Text afișat, aceeași clasă pe care garda de diacritice n-o vede.
3. **Ecranul de operațiuni a intrat în inventarul porții vizuale** (regula: un ecran al cărui JS se
   atinge), și trece **fără nicio violare** — spre deosebire de emitere, care a avut două.
4. **Restul celor 42**: 12 fără câmp în DOM și 7 numai cu filtre așteaptă un **verdict**, nu o probă
   — dar verdictul trebuie dat pe un criteriu mecanic, nu pe eyeball, fiindcă „0 câmpuri" poate
   însemna și „firma asta nu produce starea" (v. `mijloace`). Instrumentul care deosebește cele două
   nu e construit.

### Cifre

- unități mutate: **2** (`#447`, `#485`). Campania: **319 probate · 45 rămase** din 364.
- formulare probate efectiv: **32**, sub un singur rând de listă.
- defecte găsite: **2** · reparate: **2** · reprobate: **2**.
- instrumentul propriu, corectat de **două** ori în timpul lotului: navigarea pe nume, și santinela
  de dată care nu ateriza.

### După lotul 13 — cele trei răspunsuri ale lui Costin, aplicate

**(1) Cele șase mesaje, reparate (R147).** Toate șase reprobate pe ecran, în context:
*„Suma încasată trebuie să fie mai mare decât zero: din ea se extrage TVA-ul exigibil, prin suta
mărită."* · *„Bacșișul încasat trebuie să fie o sumă mai mare decât zero…"* · *„Mijlocul fix ales nu
există în registrul firmei sau a fost casat. Alege-l din listă."* · *„Codul de TVA al partenerului
lipsește. El începe cu prefixul de țară (RO, DE, FR…)…"* · *„Pentru data 1899-01-01 nu există nicio
regulă de calcul cunoscută de aplicație…"* · *„Valoarea operațiunii trebuie să fie un număr mai mare
decât zero."*

Două lucruri ies din reparație și merită scrise:

- **`bacsis invalid` era în DOUĂ locuri, cu același text și înțelesuri diferite** — la încasare e
  bacșișul primit, la distribuire e cel BRUT, din care se reține impozitul. Deosebite, nu copiate.
- **`valoare invalidă` era în PATRU locuri.** Am reparat toate patru, nu doar pe cel găsit apăsând —
  lecția lui R144: *a repara doar instanța lasă trei uși deschise pe același hol.*
- Și o greșeală a mea, prinsă de `ruff`: un `str.replace` cu șablonul de 20 de spații a lovit și
  înăuntrul liniei de 24, stricând indentarea. **Capcana 1 din predare, pe pielea mea** — un
  `replace` fără aserțiune nu e o modificare, e o speranță.

**(2) Verdictul celor 19, prin citirea șablonului — și criteriul a răsturnat propria mea grupare.**

| ce arată șablonul | câte | ce înseamnă |
|---|---|---|
| niciun `<input>`/`<textarea>`/`<select>` | **13** | **fără suprafață de intrare** — verdict |
| numai câmpuri de filtru | **2** | filtrele aleg ce se afișează, nu se înregistrează — verdict |
| câmpuri care NU sunt filtre | **5** | **au formular real** — verdictul NU se aplică |

Cele cinci: `fa-bilant` (`bl-tip`) · `fa-marja` (`jm-tip`) · `fa-regfiscal` (**`rf-venit_brut`,
`rf-cheltuieli_deductibile`** — sume fiscale!) · `fa-reginventar` (`ri-moment`, `ri-cauza`,
`ri-data_inventariere`, plus un câmp pe fiecare rând) · `fa-registre321` (`r3-fel`, plus pe rând).

*Le clasificasem drept „numai filtre" citind DOM-ul. Criteriul cerut — pe ȘABLON — le-a scos la
iveală. Exact deosebirea pe care decizia o cere: „0 câmpuri în DOM" nu e același lucru cu „n-are
câmpuri".*

**(3) Cota față de perioadă — măsurat, apoi reparat la margine (R146).**

Măsurat înainte: **17** locuri validează o cotă · **0** compară cu o listă fixă de valori · **17**
compară cu perioada, prin `cote_tva_in_vigoare(data)` · **9** funcții de prag/plafon au parametru de
perioadă. **Regula era deja implementată acolo unde se validează.**

Gaura era la marginea ei, și era scrisă în cod ca limită acceptată: `cota_ceruta` spunea *„un corp
fără `data` nu se poate verifica … se cere să existe, atât"*, iar poarta comună de lună avea
`if not data: return`. **Fix când verificarea devenea imposibilă, se renunța la ea.** Măsurat: **19
rute** cădeau apoi cu `500` (`KeyError: 'data'`) la scriere.

Reparat în două locuri. Verificat: coloana „fără dată" a trecut de la **19 × `500`** la **33 ×
refuz cu mesaj**.

### Ce a rămas nereparat

1. **Exigibilitatea.** Decizia spune *„data operațiunii decide — sau exigibilitatea, unde diferă"*.
   La TVA la încasare (art. 282) cota se aplică la data exigibilității, nu a facturii, iar
   `cota_ceruta` citește `corp["data"]` fără să întrebe care dintre cele două e. Nu s-a atins: cere
   o citire a fiecărei rute care are ambele date.
2. **`categorie_marime.prag(categorie, criteriu)`** n-are parametru de perioadă, iar pragurile de
   mărime se schimbă prin lege. E chiar subiectul restanței **R3**, deschisă; nu se deschide aici.
3. **Cele 5 ecrane cu formular real** așteaptă probarea. Nu sunt „rămase" în același sens ca înainte:
   acum se știe ce e în ele.

### Cifre

**334 probate · 30 rămase** din 364 — 25 de ecrane + 5 rute de rol. Cele 15 verdicte n-au fost
probe: sunt citiri, pe criteriul scris.
