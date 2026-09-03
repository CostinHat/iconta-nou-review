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
