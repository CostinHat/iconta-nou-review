# LOTUL 4 — verificări pentru 31 de pași

Fiecare verificare spune **ce trebuie să fie adevărat DUPĂ pas**, nu că pasul a mers.

Unde nu pot scrie o verificare fără să știu ceva ce nu am, o spun.

---

## Premisa lotului

Cele 20 de note din T05 scriu **ciornă**. Măsurătoarea ta pe stare a arătat că „fără rol" acolo nu e o gaură spre evidență. Iau asta ca dată — **nicio verificare de mai jos nu conține „lipsește rolul"** pentru rutele nota-*.

Ce rămâne de verificat la ele e altceva: că nota propusă e corectă înainte de a ajunge la cineva care o validează.

**Verificări comune tuturor celor 20:**

- nota respectă partida dublă: total debit = total credit
- conturile există în planul firmei — se refuză, prin `cont_valid`
- data notei e într-o perioadă deschisă
- nota intră ca **ciornă**, nu ca evidență — verificat pe starea scrisă, nu pe intenție
- documentul justificativ e cerut, sau se spune de ce lipsește
- o a doua propunere pe același fapt nu produce a doua ciornă

Mai jos, doar ce e specific fiecăreia.

---

## T05 — Nota contabilă (20)

### `nota-tva-incasare`
- TVA-ul se colectează la **încasare**, nu la facturare — nota se leagă de plată, nu de factură
- firma e în regimul de TVA la încasare la data operațiunii; altfel regimul nu se aplică
- plafonul de aplicare a regimului e verificat pe cifra de afaceri, la data operațiunii

### `nota-leasing`
- financiar sau operațional — cele două au tratamente contabile opuse. Verifică dacă ruta le distinge, sau presupune unul
- la leasing financiar, bunul intră ca imobilizare și se amortizează; rata se desface în principal și dobândă
- la operațional, rata e cheltuială integral
- dobânda din rată e separată de principal, nu topită în cheltuială

### `nota-credit`
- rambursarea se desface în principal și dobândă; principalul stinge datoria, dobânda e cheltuială
- comisioanele au tratament propriu — verifică dacă se disting
- creditul în valută produce diferențe de curs la fiecare rambursare

### `nota-avans`
- avansul încasat **nu e venit** — e datorie până la livrare
- TVA-ul se colectează la încasarea avansului, dacă firma e plătitoare
- la livrare, avansul se stinge, iar TVA-ul nu se colectează a doua oară pe partea avansată

### `nota-provizion`
- provizionul deductibil fiscal e limitat prin lege; ce depășește e cheltuială nedeductibilă
- verifică dacă ruta distinge deductibil de nedeductibil, sau lasă totul deductibil
- provizionul se reia când motivul dispare — verifică dacă există calea inversă

### `nota-productie`
- costul de producție cuprinde materialele, manopera și cota de indirecte — verifică ce cuprinde efectiv
- produsul finit intră în stoc la cost, nu la preț de vânzare
- mișcarea de stoc are aceeași dată cu nota

### `nota-obiect-inventar`
- valoarea e **sub pragul** de mijloc fix la data operațiunii — altfel e imobilizare, nu obiect de inventar
- pragul se cere din registru, pe dată
- darea în folosință e o operațiune distinctă de achiziție — verifică dacă se disting

### `nota-asociati`
- distincția între aport, împrumut și retragere e obligatorie: au tratamente fiscale diferite
- retragerea de bani fără temei e chiar cazul din ghidul „bani din firmă fără temei" — verifică dacă ruta o permite fără să semnaleze
- împrumutul de la asociat poartă dobândă deductibilă limitat; verifică dacă se aplică plafonul

### `nota-sponsorizare`
- creditul fiscal e minimul dintre 0,75% din cifra de afaceri și 20% din impozit — verifică dacă se calculează, sau se ia suma integral
- beneficiarul e în Registrul entităților; altfel sponsorizarea nu dă credit fiscal
- sponsorizarea intră în D107 — verifică legătura

### `nota-subventie`
- subvenția pentru investiții se recunoaște la venit **pe măsura amortizării**, nu integral la încasare
- subvenția de exploatare e venit în perioada în care se acoperă cheltuiala
- verifică dacă cele două se disting

### `nota-chirie`
- chiria plătită unei persoane fizice atrage impozit și, uneori, CASS — verifică dacă se rețin
- chiria în valută produce diferențe de curs
- chiria plătită în avans se eșalonează pe perioada acoperită, nu e cheltuială integral

### `nota-decont-deplasare`
- diurna neimpozabilă e plafonată; ce depășește e venit asimilat salariilor
- plafonul intern și cel extern sunt diferite, iar cel extern diferă pe țară — verifică dacă se cere din registru
- cheltuielile de transport și cazare sunt separate de diurnă

### `nota-bacsis`
- bacșișul are regim fiscal propriu din 2023 — venit al salariatului, cu impozit reținut, fără contribuții
- verifică dacă se distinge de venit al firmei
- bacșișul încasat prin card trece prin casă sau prin bancă — verifică traseul

### `nota-sgr`
- garanția de ambalaje **nu e venit și nu e cheltuială** — e datorie, respectiv creanță
- TVA-ul nu se aplică garanției
- returnarea stinge datoria, nu produce venit
- temeiul e HG 1074/2021, adus în corpus pe 24.08

### `nota-perisabilitati`
- limita legală de perisabilitate e pe categorie de produs; ce depășește e cheltuială nedeductibilă
- verifică dacă limita se cere din registru sau e literal
- perisabilitățile se constată la inventar, nu în orice moment

### `nota-contract-special`
- **nu pot scrie verificarea fără să știu ce contract.** De completat din cod

### `nota-inventariere`
- plusul de inventar e venit; minusul e cheltuială, deductibilă doar în limita perisabilităților
- minusul imputabil se recuperează de la gestionar — verifică dacă se distinge de cel neimputabil
- nota atinge și `mijloace_fixe`: verifică ce se întâmplă cu un mijloc fix lipsă la inventar
- mișcările de stoc au aceeași dată cu nota

### `nota-lichidare`
- lichidarea închide conturile; verifică ordinea: se sting datoriile, apoi se distribuie asociaților
- impozitul pe dividende se aplică la distribuirea din lichidare
- verifică dacă ruta permite lichidarea unei firme cu datorii nestinse

### `nota-ong`
- activitatea fără scop patrimonial e separată de cea economică — verifică dacă se disting
- veniturile neimpozabile ale ONG au plafon; peste el se impozitează
- verifică dacă se aplică cele două plafoane cumulate

---

## T07 — Extrasul bancar (5)

### `POST /tenants/{tenant_id}/banca/parse-extras`
*întoarce {nr, tranzactii}*

- **nu scrie nimic** — verificat structural
- fiecare tranzacție din fișier apare în răspuns; cele care nu s-au putut citi se numesc, cu rândul lor
- soldul final din extras = soldul inițial + suma tranzacțiilor. Dacă nu, fișierul e incomplet și se spune
- data valutei și data operațiunii sunt distincte — verifică dacă se citesc amândouă

### `POST /tenants/{tenant_id}/banca/reconciliere/import`
*PLAFON: extras_linii, inregistrari, inregistrari_linii*

- fiecare tranzacție importată produce **o singură** linie de extras
- un extras importat de două ori nu dublează liniile — verifică pe numărul extrasului și pe conținut
- liniile importate poartă **sursa** (extras bancar) și gradul de certitudine
- potrivirea automată cu facturi e o **propunere**, nu un fapt: verifică dacă rezultatul e ciornă sau evidență
- soldul contului de bancă după import = soldul din extras

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza`
*PLAFON: extras_linii, inregistrari, inregistrari_linii*

- nota produsă respectă partida dublă și folosește conturi existente
- linia de extras trece în starea „contată" și nu se mai poate conta a doua oară
- dacă linia se leagă de o factură, suma nu depășește soldul neîncasat
- data notei e data operațiunii din extras, nu data contării

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora`
*scrie extras_linii (UPDATE)*

- ignorarea poartă **motivul** — o linie ignorată fără motiv e o sumă care dispare din reconciliere
- linia rămâne vizibilă în listă, cu starea „ignorată", nu dispare
- soldul de reconciliat include liniile ignorate, sau le exclude explicit — verifică ce face și dacă se vede

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza`
*scrie extras_linii (UPDATE)*

- reactivarea unei linii contate anulează nota produsă? Sau doar pe cele ignorate se poate?
- dacă anulează o notă validată, se refuză — se stornează
- reactivarea se consemnează: cine, când

---

## T08 — NIR (1)

### `POST /tenants/{tenant_id}/stocuri/nir`
*PLAFON: inregistrari, inregistrari_linii, nir, nir_linii*

- NIR-ul primește **număr din serie**, fără goluri
- cantitățile recepționate nu depășesc cantitățile de pe factură — sau diferența e consemnată ca minus la recepție
- adaosul comercial, dacă se aplică, e calculat pe cotă, nu introdus liber
- mișcarea de stoc are aceeași dată cu NIR-ul
- nota contabilă și NIR-ul au aceeași valoare totală
- un NIR pe o factură deja recepționată se refuză, sau produce recepție parțială — verifică ce face

---

## T09 — Casa (2)

### `POST /tenants/{tenant_id}/casa/operatiuni`
*PLAFON: casa_operatiuni, inregistrari, inregistrari_linii*

- **soldul casei nu poate deveni negativ** — o plată peste sold se refuză
- plafonul de plăți în numerar către o persoană juridică se verifică pe zi și pe operațiune
- plafonul de încasări în numerar de la o persoană se verifică la fel
- operațiunea produce o linie în registrul de casă, cu numărul curent
- data operațiunii e într-o perioadă deschisă

### `DELETE /tenants/{tenant_id}/casa/operatiuni/{op_id}`
*PLAFON: casa_operatiuni, inregistrari, inregistrari_linii*

- **o operațiune de casă dintr-o zi închisă nu se șterge** — registrul de casă se închide zilnic
- ștergerea recalculează soldul; dacă soldul ar deveni negativ la vreo operațiune ulterioară, se refuză
- numerotarea nu se reia după ștergere — rămâne golul, sau se renumerotează? Verifică și spune care
- dacă operațiunea are notă validată, se refuză

---

## T10 — Inventarierea (1)

### `POST /tenants/{tenant_id}/stocuri/inventar`
*PLAFON: articole, inregistrari, inregistrari_linii, miscari_stoc*

- inventarul compară **stocul faptic** cu cel scriptic; diferența e plus sau minus, nu se ajustează tăcut
- fiecare diferență produce o mișcare de stoc, iar suma mișcărilor = diferența totală
- minusul se compară cu limita de perisabilitate pe categorie; ce depășește e nedeductibil
- inventarul se face la o dată, iar mișcările de după acea dată nu-l afectează
- un articol care nu apare în listă rămâne cu stocul scriptic sau se consideră zero? Verifică — diferența e mare

---

## T11 — Închiderea lunii (2)

### `POST /tenants/{tenant_id}/perioade-blocate`
*cere_rol · rol:admin_firma · scrie perioade_blocate*

- închiderea e un act deliberat, cu **autor și moment** consemnate
- după închidere, nicio scriere în perioada aceea nu mai trece — verificat pe toate cele 39 de operațiuni, nu doar pe cele testate
- închiderea verifică întâi că perioada e coerentă: balanța se închide, notele sunt validate, nu există ciorne. Sau, dacă nu verifică, se spune ce nu verifică
- o perioadă nu se poate închide dacă cea anterioară e deschisă

### `DELETE /tenants/{tenant_id}/perioade-blocate`
*cere_rol · rol:admin_firma · scrie perioade_blocate*

- redeschiderea e act consemnat, cu **motiv obligatoriu** — P15
- redeschiderea marchează documentele emise din acea perioadă ca fiind **sub rezervă**
- declarațiile depuse pentru perioada redeschisă produc contradicție vizibilă, nu se rescriu
- o perioadă nu se poate redeschide dacă cea următoare e închisă

---

## Ce am observat scriind lotul

**Cele 20 de note ridică aceeași întrebare de 20 de ori:** ruta calculează tratamentul fiscal corect, sau doar scrie ce i se dă? Am scris verificările presupunând că ar trebui să calculeze — dacă nu calculează, fiecare devine „nu verifică nimic din ce ar trebui".

Aia ar fi o cifră, nu o notă: 20 de rute care par să propună o notă și doar transcriu.

**Trei rute cer completare din cod:** `nota-contract-special` (ce contract?), `banca/reconciliere/{id}/reactiveaza` (ce anulează?), și numerotarea după ștergere la casă.

**`perioade-blocate` e singura pereche din lot cu rol, și e cea mai importantă.** Dacă închiderea nu verifică coerența perioadei înainte de a o închide, se închide o lună cu ciorne nevalidate și balanță neechilibrată — iar aia nu se mai poate repara decât prin redeschidere.
