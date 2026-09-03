# LOTUL 1 — verificări pentru 30 de pași

Fiecare verificare spune **ce trebuie să fie adevărat DUPĂ pas**, nu că pasul a mers.

Unde nu pot scrie o verificare fără să știu ceva ce nu am, o spun — nu inventez.

---

## T01 — Declarația

### `POST /tenants/{tenant_id}/istoric-declaratii-import/incarca`
*scrie declaratii_depuse, migrare_status*

- fiecare declarație din fișier are un rând în `declaratii_depuse`, cu tip, perioadă și dată de depunere
- numărul de rânduri scrise = numărul de declarații din fișier, minus cele respinse, iar respinsele sunt numite
- un `DELETE/INSERT` nu lasă în urmă rânduri din import-ul anterior care nu mai sunt în fișier — sau, dacă le lasă, se spune care
- `migrare_status` marchează stratul ca parcurs, cu momentul

### `POST /tenants/{tenant_id}/istoric-declaratii-import`
*scrie declaratii_depuse*

- același conținut ca la pasul de încărcare — ce s-a văzut la previzualizare e ce s-a salvat
- o a doua rulare cu același fișier nu dublează rândurile

### `POST /coada`
*scrie declaratii_coada, declaratii_depuse*

- declarația intră în coadă **numai cu verdict de validare păstrat** — altfel ruta refuză și spune de ce
- rândul din coadă poartă: tip, perioadă, firmă, cine a pregătit, momentul
- nu se creează rând în `declaratii_depuse` la intrarea în coadă — depunerea nu s-a întâmplat

### `POST /coada/{coada_id}/aproba`
*scrie declaratii_coada, declaratii_depuse*

- cine aprobă e consemnat, și e diferit de cine a pregătit dacă patru ochi e activ **și** posibil
- dacă patru ochi e activ și imposibil (un singur validator), ruta refuză cu motivul, nu tace
- starea trece în „aprobată", nu direct în „depusă"

### `POST /coada/{coada_id}/respinge`
*scrie declaratii_coada, declaratii_depuse*

- respingerea poartă **motivul**, obligatoriu
- declarația nu dispare din coadă — rămâne, cu starea „respinsă" și motivul vizibil
- cine a pregătit vede respingerea; nu se stinge prin ignorare

### `POST /coada/{coada_id}/depune`
*scrie declaratii_coada, declaratii_depuse*

- ruta refuză o declarație fără verdict de validare păstrat, sau cu verdict pe altă amprentă decât fișierul curent
- se scrie în `declaratii_depuse`: tip, perioadă, momentul, autorul autorizării, amprenta fișierului, indexul de la autoritate dacă există
- dacă indexul lipsește, starea nu e „confirmată" — e „nelămurită", conform P19
- declarația iese din coadă numai după ce rândul de depunere există

### `POST /declaratii/{tip}/valideaza`
*trece prin validatorul oficial ANAF*

- verdictul se **păstrează**, cu momentul, versiunea validatorului și **amprenta fișierului validat**
- un verdict pe un XML regenerat între timp nu mai e verdict — dacă amprenta diferă, se marchează stătut
- respingerea validatorului e o stare a documentului, nu o eroare a aplicației: se păstrează cu ce a spus validatorul

### `POST /declaratii/{tip}`
*întoarce {avertismente, note_rezultat, operatiuni, tip, xml}*

- fiecare operațiune din evidență care ar trebui să apară în declarație, apare — absența nu e vizibilă în structură
- `operatiuni` conține și cele excluse, cu motivul și temeiul excluderii, nu doar cele incluse
- `avertismente` e gol înseamnă „nimic de semnalat", nu „n-am verificat"
- două generări succesive pe aceleași date produc același XML — altfel amprenta din verdict nu poate fi de încredere

---

## T06 — Importul de e-Factura și SPV

### `POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv`
*scrie efactura_trimiteri*

- rândul poartă starea explicită: în curs / confirmată / respinsă / **nelămurită**
- fără identificator de la autoritate, starea nu e „confirmată"
- o a doua apăsare pe aceeași factură nu produce o a doua trimitere fără avertisment — dublarea la autoritate nu se repară

### `POST /tenants/{tenant_id}/import-efactura`
*upload XML/ZIP*

- fiecare factură din fișier ajunge în `efactura_primite` ca **ciornă**, nu ca factură validată
- valorile preluate poartă **sursa** (e-Factura) și **gradul de certitudine** — nimic nu devine fapt fără confirmare
- ce nu s-a putut citi din XML se numește, nu se ghicește: data, cota, partenerul
- un fișier importat de două ori nu creează ciorne duplicate

### `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza`
*FOUR-EYES; scrie efactura_primite, facturi*

- cine validează e consemnat, și e diferit de cine a importat dacă patru ochi e activ și posibil
- factura creată poartă legătura către ciorna din care a ieșit — lanțul nu se rupe
- valorile confirmate nu mai poartă „grad de certitudine": confirmarea e explicită și consemnată
- dacă a ieșit și o cheltuială, aceasta e legată de factură, nu independentă

### `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge`
*scrie efactura_primite*

- respingerea poartă motivul, obligatoriu
- ciorna rămâne, cu starea „respinsă" — nu se șterge; e o urmă a ceea ce a sosit

---

## T12 — Închiderea anului și situațiile financiare

### `POST /tenants/{tenant_id}/s1005-valideaza`
*scrie artefacte_produse*

- artefactul se păstrează cu: conținutul, momentul, autorul, amprenta, numărul exemplarului
- verdictul validării se păstrează cu artefactul, nu separat
- **verificare de fond:** situațiile financiare cerute depind de categoria de mărime a firmei. Dacă aceasta nu există ca dimensiune, ruta nu poate ști ce datorează firma — se declară, nu se presupune

### `POST /tenants/{tenant_id}/s1003-valideaza`
*scrie artefacte_produse*

- aceleași ca mai sus
- **plus:** un artefact produs pe regimul greșit e conform ca formă și fals ca fond. Ruta refuză, sau spune că nu poate verifica regimul

---

## T14 — Preluarea unei firme

### `POST /migrare/valideaza`
*verifică CUI-uri la ANAF*

- fiecare CUI primește un răspuns explicit: găsit / negăsit / **nu s-a putut verifica**
- „nu s-a putut verifica" nu se convertește în „negăsit" — sunt stări diferite
- răspunsul de la ANAF se păstrează cu momentul, altfel se reinterogează la fiecare pas

### `POST /migrare/fisier`
*CSV/XLSX → CUI-uri validate la ANAF*

- numărul de CUI-uri extrase = numărul de rânduri din fișier, minus cele nevalide, iar nevalidele sunt numite cu rândul lor
- un CUI care nu trece cifra de control se semnalează la extragere, nu la interogare

### `POST /migrare/incarca`
*idem*

- ce se vede la previzualizare e ce se importă la pasul următor — aceleași reguli, același rezultat

### `POST /migrare/importa`
*scrie firma_profil, migrare_status, tenants, user_tenants*

- fiecare firmă selectată primește **schemă proprie**, iar `tenants` are rândul ei — o firmă fără schemă e o afirmație falsă despre lume
- `user_tenants` leagă firma de cabinetul care a importat-o
- o firmă importată de două ori nu creează două scheme
- dacă crearea schemei eșuează, rândul din `tenants` nu rămâne — sau, dacă rămâne, e marcat incomplet

### `POST /migrare/status`
*scrie migrare_status*

- trecerea în „in_lucru" cere notă, cum spune ruta — verifică că o refuză fără ea
- starea poartă cine a marcat-o și când

### `POST /tenants/{tenant_id}/solduri/incarca`
*scrie migrare_status, plan_conturi, solduri_initiale*

- **previzualizarea nu salvează** — ruta spune că întoarce preview; verifică structural că nu scrie în `solduri_initiale`
- dacă totuși scrie (numele tabelelor sugerează că da), atunci previzualizarea nu e previzualizare, iar aia e o constatare
- balanța încărcată **se închide**: total debit = total credit. Dacă nu, se spune, nu se salvează tăcut

### `POST /tenants/{tenant_id}/solduri`
*scrie plan_conturi, solduri_initiale*

- ce s-a văzut la previzualizare e ce s-a salvat
- „înlocuiește ce era" — verifică ce se întâmplă cu soldurile anterioare: se șterg, sau se păstrează ca versiune?
- conturile din balanță care nu există în plan se creează sau se semnalează — nu se ignoră

### `POST /tenants/{tenant_id}/parteneri/incarca`
*scrie migrare_status, solduri_parteneri*

- verificarea de coerență față de balanță: suma soldurilor partenerilor = soldul contului corespondent. Diferența se arată cu **ambele cifre**, nu ca „există o divergență"
- un partener fără cod fiscal se semnalează la încărcare — nu intră în D394 și nu se corelează în VIES

### `POST /tenants/{tenant_id}/parteneri`
*scrie solduri_parteneri*

- ce s-a văzut la previzualizare e ce s-a salvat
- divergența față de balanță, dacă a existat, rămâne vizibilă după salvare — nu se stinge prin acceptare

### `POST /tenants/{tenant_id}/salariati-import/incarca`
*scrie migrare_status, salariati*

- **previzualizarea nu salvează** — aceeași verificare structurală ca la solduri
- CNP-urile nevalide se numesc, cu rândul lor din fișier
- un CNP valid dar implauzibil ca dată de naștere se semnalează separat

### `POST /tenants/{tenant_id}/salariati-import`
*scrie salariati (upsert pe CNP)*

- upsert-ul nu suprascrie date existente fără să spună ce a schimbat
- un salariat existent cu alt nume la același CNP e o divergență, nu o actualizare tăcută

### `POST /tenants/{tenant_id}/asociati-import/incarca`
*scrie asociati, migrare_status*

- previzualizarea nu salvează
- suma procentelor de participare = 100, sau se semnalează

### `POST /tenants/{tenant_id}/asociati-import`
*scrie asociati*

- `DELETE/INSERT` — verifică ce se întâmplă cu asociații care nu mai sunt în fișier: se șterg, iar aia e o schimbare de structură a firmei, nu un import

### `POST /tenants/{tenant_id}/retete-import/incarca`
*întoarce {retete, rezumat}*

- previzualizare pură: nu scrie nimic, verificat structural
- `rezumat` numește ce nu s-a putut citi, nu doar câte s-au citit

### `POST /tenants/{tenant_id}/retete-import`
*retete_import_api.importa()*

- ce s-a văzut la previzualizare e ce s-a importat
- **nu pot scrie mai mult fără să știu ce scrie `importa()`** — ruta întoarce ce dă funcția, iar funcția nu e descrisă. De completat din cod

### `POST /tenants/{tenant_id}/articole-import/incarca`
*scrie articole, miscari_stoc*

- **previzualizarea scrie în stoc?** Dacă `articole` și `miscari_stoc` se scriu la încărcare, nu e previzualizare — e import. Verifică și spune care e
- articolele cu cod duplicat în fișier se semnalează, nu se suprascriu între ele

---

## Ce am observat scriind lotul

**Patru rute de „încărcare" scriu în tabele de date**, nu doar în `migrare_status`: solduri, parteneri, salariați, articole. Ori previzualizarea salvează, ori numele tabelelor din inventar sunt inexacte.

Nu pot decide care din cod — dar dacă previzualizarea salvează, „ce s-a văzut e ce s-a salvat" nu mai e o verificare, e o tautologie, iar utilizatorul crede că se uită înainte de a decide.

**Trei pași cer o verificare pe care aplicația n-o poate face azi:** categoria de mărime la S1005/S1003, și verdictul păstrat la coadă. Le-am scris ca verificări, nu ca limite — dacă nu se pot face, aia e o cifră pentru lista 3.
