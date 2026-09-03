# LOTUL 2 — verificări pentru 30 de pași

Fiecare verificare spune **ce trebuie să fie adevărat DUPĂ pas**, nu că pasul a mers.

Unde nu pot scrie o verificare fără să știu ceva ce nu am, o spun.

---

## Trei lucruri de citit înainte de pași

**1. Regimurile speciale de TVA au roluri inconsecvente.** Șase rute scriu în `inregistrari` și `inregistrari_linii` pentru aceeași clasă de operațiune. Una cere `admin_firma` — `achizitie-taxare-inversa`. Celelalte cinci nu cer niciun rol.

Nu e o verificare de pas, e o constatare: aceeași operațiune, roluri diferite, fără motiv vizibil. De consemnat separat.

**2. `POST /public/plata/{ref}/confirma` — FĂRĂ GARDĂ.** Singura rută din lot fără nicio verificare de acces. Confirmă o plată. Merită tratată separat de restul.

**3. Verificările de mai jos disting „scrie" de „poate atinge prin modul".** Unde eticheta spune PLAFON sau „prin modul", verificarea e formulată pe efect, nu pe tabelă — fiindcă tabela e presupusă, nu măsurată.

---

## T14 — Preluarea unei firme (5)

### `POST /tenants/{tenant_id}/articole-import`
*rol:admin_firma · scrie articole, miscari_stoc*

- ce s-a văzut la previzualizare e ce s-a importat — același număr, aceleași articole
- articolele cu cod duplicat în fișier se semnalează, nu se suprascriu între ele
- fiecare articol importat cu stoc inițial produce o mișcare de stoc, iar suma mișcărilor = stocul declarat
- un import repetat cu același fișier nu dublează nici articolele, nici mișcările

### `POST /tenants/{tenant_id}/mijloace-fixe-import/incarca`
*fără rol · previzualizare*

- **nu scrie nimic** — verificat structural, nu prin absența efectului
- durata de amortizare a fiecărui mijloc fix e confruntată cu catalogul; cele din afara intervalului se numesc, cu rândul lor
- valoarea de intrare sub pragul de mijloc fix se semnalează — e obiect de inventar, nu mijloc fix

### `POST /tenants/{tenant_id}/mijloace-fixe-import`
*rol:admin_firma*

- ce s-a văzut la previzualizare e ce s-a importat
- amortizarea cumulată la data preluării nu depășește valoarea de intrare
- un mijloc fix complet amortizat intră cu valoare rămasă zero, nu se respinge

### `POST /tenants/{tenant_id}/rip-import/incarca`
*rol:admin_firma*

- **nu pot scrie verificarea fără să știu ce e RIP.** Registrul de inventar și producție? Registrul imobilizărilor? De completat din cod, ca la `retete-import`

### `POST /control-fiscal/{tenant_id}/audit-preluare`
*rol:admin_firma*

- auditul spune ce a găsit **și pe ce s-a uitat** — o firmă preluată fără evidență completă nu primește verdict favorabil, primește „nu pot verifica" cu lista domeniilor
- fiecare constatare poartă domeniul și perioada la care se referă
- absența unei categorii de date nu se convertește în „conform" — e P6

---

## T15 — Salariați și contracte (13)

### `POST /tenants/{tenant_id}/salariati`
*fără rol · scrie salariati*

- CNP-ul trece cifra de control; unul care nu trece se refuză cu motivul, nu se salvează
- un CNP care există deja în firmă se refuză — nu se creează al doilea salariat cu același CNP
- data angajării nu e în viitor față de perioada deschisă
- salariul de bază nu e sub minimul aplicabil la data angajării, proratat cu norma. Dacă e, se refuză cu cifra minimului

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}`
*fără rol*

- o modificare de salariu produce **istoric**, nu suprascriere: valoarea veche rămâne, cu perioada în care a fost valabilă
- modificarea nu atinge lunile pentru care s-a emis deja stat de plată — sau, dacă le atinge, produce contradicție vizibilă
- schimbarea normei recalculează pragul minim; dacă noul salariu cade sub el, se refuză

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar`
*fără rol*

- beneficiul intră cu perioada lui, nu cu „de acum înainte"
- plafonul neimpozabil aplicabil e cel de la data lunii, nu de la data introducerii
- ce depășește plafonul devine venit impozabil, iar partea impozabilă e vizibilă separat — nu se topește în brut

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}`
*fără rol*

- **un salariat cu stat de plată emis nu se șterge.** Se marchează încetat, cu data. Ștergerea ar rupe lanțul către documentele emise
- dacă ștergerea e permisă, verifică ce rămâne în urmă: fluturași, note contabile, rânduri în D112 deja depuse
- încetarea se propagă în REGES — sau, dacă nu, se spune

### `POST /tenants/{tenant_id}/salariati/{salariat_id}/adeverinta`
*rol:admin_firma · artefact predat*

- adeverința se păstrează: conținutul, momentul, autorul, amprenta, numărul exemplarului
- cifrele din adeverință coincid cu statele de plată emise pentru perioada acoperită — nu se recalculează la emitere
- dacă o lună din perioadă n-are stat emis, adeverința spune asta, nu o completează din recalcul

### `POST /tenants/{tenant_id}/contracte/sabloane`
*fără rol*

- șablonul salvat conține marcajele declarate; unul necunoscut se semnalează la salvare, nu la generare
- un șablon cu același nume nu se suprascrie tăcut

### `DELETE /tenants/{tenant_id}/contracte/sabloane/{sid}`
*fără rol*

- ștergerea unui șablon nu atinge contractele generate din el — acelea sunt documente emise
- dacă șablonul e folosit de contracte existente, se spune câte

### `POST /tenants/{tenant_id}/contracte/genereaza`
*rol:admin_firma · artefact predat*

- contractul generat se păstrează cu momentul, autorul, amprenta, numărul exemplarului
- toate marcajele din șablon sunt înlocuite; unul rămas necompletat oprește generarea, nu produce un contract cu paranteze
- datele din contract coincid cu fișa salariatului la data generării, nu cu cea de azi

### `POST /tenants/{tenant_id}/prapastie-salariu`
*fără rol · calcul*

- răspunsul conține **ambele cifre** — netul la salariul actual și netul la cel propus — plus diferența, nu doar „se pierde facilitatea"
- pragul de la care netul revine la nivelul actual e calculat, nu aproximat
- cifrele sunt calculate cu toate elementele salariatului: persoane în întreținere, tip de contract, normă
- dacă vreun element lipsește și cifra n-ar fi exactă, se spune — nu se dă o cifră parțială ca exactă

### `POST /tenants/{tenant_id}/reges-config`
*fără rol · scrie reges_chei*

- **cheile nu se întorc niciodată în răspuns**, nici mascate, nici parțial
- o cheie salvată e verificată că funcționează, sau se spune că n-a fost verificată
- suprascrierea unei chei existente e consemnată: cine, când

### `POST /tenants/{tenant_id}/reges-trimite-salariat`
*rol:admin_firma · scrie reges_mesaje*

- starea trimiterii e explicită: în curs / confirmată / respinsă / **nelămurită**
- fără identificator de la REGES, starea nu e „confirmată"
- o a doua trimitere pentru același salariat și aceeași modificare nu se face fără avertisment
- ce s-a trimis se păstrează, nu doar că s-a trimis — la o neconcordanță, contează conținutul

### `POST /tenants/{tenant_id}/reges-poll`
*fără rol · scrie reges_mesaje*

- răspunsul de la REGES se păstrează cu momentul, nu doar starea derivată din el
- o trimitere fără răspuns după un interval rămâne „nelămurită", nu trece în „confirmată" prin lipsă de veste
- polling-ul nu schimbă starea unei trimiteri deja confirmate

---

## T18 — Încasări (3)

### `POST /tenants/{tenant_id}/chitante`
*fără rol · artefact predat*

- chitanța se păstrează cu numărul exemplarului, momentul, autorul, amprenta
- **numerotarea nu are goluri și nu se reia** — o chitanță anulată își păstrează numărul
- suma chitanței nu depășește soldul neîncasat al facturii la care se leagă
- dacă nu se leagă de nicio factură, se spune la ce se leagă

### `POST /tenants/{tenant_id}/facturi/{factura_id}/link-plata`
*rol:admin_firma*

- link-ul poartă suma exactă a facturii, nu una editabilă de plătitor
- link-ul expiră; expirarea e o stare, nu o eroare
- un al doilea link pe aceeași factură invalidează primul, sau se refuză — nu coexistă două

### `POST /public/plata/{ref}/confirma`
*FĂRĂ GARDĂ · fără rol*

**Aceasta e singura rută din lot fără nicio verificare de acces. Verificările de mai jos presupun că asta e intenționat — o rută publică apelată de procesatorul de plăți.**

- confirmarea se acceptă **numai** dacă e semnată de procesator, cu semnătura verificată. Altfel oricine cu referința poate marca o factură ca plătită
- referința e imposibil de ghicit — nu incrementală, nu derivată din numărul facturii
- o confirmare pe o referință deja confirmată nu produce a doua încasare
- suma confirmată se compară cu suma din link; o diferență nu se acceptă tăcut
- încasarea produsă poartă sursa „plată online", nu se confundă cu una introdusă manual

**Dacă semnătura nu se verifică azi, aceasta e prima verificare de scris — și e prag 1: oricine cu referința poate declara o factură plătită.**

---

## T25 — Magazin online (2)

### `PUT /tenants/{tenant_id}/woocommerce/config`
*fără rol · scrie firma_profil*

- cheile de acces nu se întorc în răspuns
- schimbarea configurației nu atinge facturile deja sincronizate
- o configurație salvată e verificată că se conectează, sau se spune că n-a fost verificată

### `POST /tenants/{tenant_id}/woocommerce/sincronizeaza`
*rol:admin_firma · scrie facturi (UPDATE), firma_profil (UPDATE) — prin modul*

- fiecare comandă sincronizată produce **o singură** factură; o a doua rulare nu dublează
- cota de TVA vine din articol sau din configurație — **nu se ghicește din denumire**
- comenzile care nu s-au putut transforma în factură se numesc, cu motivul; nu se sar tăcut
- ultima sincronizare reușită se păstrează, ca următoarea să știe de unde continuă

---

## T27 — e-Transport (2)

### `POST /tenants/{tenant_id}/etransport-xml`
*fără rol · generare*

- XML-ul generat conține toate câmpurile obligatorii; unul lipsă oprește generarea cu numele lui
- codurile din nomenclatoare — scop, tip de operațiune, unități — vin din registru, nu din literali
- greutatea și valoarea sunt cele din documentul de transport, nu recalculate

### `POST /tenants/{tenant_id}/etransport/trimite`
*rol:admin_firma · scrie etransport_trimiteri*

- cele patru porți rulează **în ordine**: garda de timp → idempotență → validare pe TEST → încărcare. O poartă sărită e un defect, nu o optimizare
- codul UIT primit se păstrează; fără el, starea e „nelămurită"
- garda de timp refuză o trimitere după termenul legal — și spune care e termenul
- idempotența e pe conținut, nu pe moment: același transport trimis de două ori e prins chiar dacă a trecut timp

---

## T29 — Regimuri speciale de TVA (6)

**Constatare comună celor șase:** aceeași clasă de operațiune, cinci fără rol, una cu `admin_firma`. Inconsecvența e ea însăși de consemnat.

**Verificări comune tuturor:**

- nota produsă respectă partida dublă: total debit = total credit, pe fiecare notă
- conturile folosite există în planul firmei
- perioada nu e închisă — altfel se refuză, cu motivul
- baza și TVA-ul din notă coincid cu ce va apărea în declarație, sau divergența se arată cu ambele cifre

### `POST /tenants/{tenant_id}/vanzare-marja`
*fără rol · art. 312*

- marja se calculează ca preț de vânzare minus preț de cumpărare, iar TVA-ul se aplică **pe marjă**, nu pe preț
- o marjă negativă nu produce TVA negativă — se tratează ca marjă zero, sau se semnalează
- prețul de cumpărare vine de la achiziția legată, nu se introduce liber

### `POST /tenants/{tenant_id}/vanzare-marja-turism`
*fără rol · art. 311*

- aceleași ca la marjă, plus: locul prestării e România pentru ca regimul să se aplice
- serviciile prestate de terți în afara UE au tratament distinct — verifică dacă se disting

### `POST /tenants/{tenant_id}/vanzare-aur-investitii`
*fără rol · art. 313*

- operațiunea e scutită fără drept de deducere; nu se colectează TVA
- dacă firma a optat pentru taxare, opțiunea e consemnată și verificată la fiecare operațiune
- aurul de investiții e definit prin puritate și formă — verifică dacă se validează, sau se acceptă orice

### `POST /tenants/{tenant_id}/achizitie-agricultor`
*fără rol · art. 315^1*

- compensația în cotă forfetară se calculează pe cota în vigoare la data operațiunii
- agricultorul e verificat că e în regimul special — altfel e o achiziție obișnuită
- compensația plătită e deductibilă la cumpărător; verifică unde ajunge în D300

### `POST /tenants/{tenant_id}/vanzare-agricultor`
*fără rol*

- **nu pot scrie verificarea fără să știu ce reprezintă.** O vânzare CĂTRE un agricultor în regim special, sau o vânzare FĂCUTĂ de firmă dacă ea e agricultorul? Cele două au tratamente opuse. De completat din cod

### `POST /tenants/{tenant_id}/achizitie-taxare-inversa`
*rol:admin_firma · art. 331*

- bunul sau serviciul e din lista art. 331 — altfel taxarea inversă nu se aplică
- pragul de 22.500 lei pentru telefoane, tablete, laptopuri, console e verificat pe factură, nu pe operațiune
- TVA-ul se înregistrează simultan ca deductibil și colectat, iar cele două se anulează în decont
- furnizorul e înregistrat în scopuri de TVA — altfel regimul nu se aplică

---

## Ce am observat scriind lotul

**Trei rute cer completare din cod:** `rip-import` (nu știu ce e RIP), `vanzare-agricultor` (nu știu în ce sens), și verificarea semnăturii la `/public/plata`.

**Șase rute care scriu în evidența contabilă nu cer niciun rol** — cele cinci regimuri speciale plus `achizitie-agricultor`. Iar a șaptea, din aceeași clasă, cere `admin_firma`.

**Trei rute manipulează chei sau plăți fără rol:** `reges-config`, `reges-poll`, `woocommerce/config`. Cheile de acces la sisteme externe nu sunt date de firmă — sunt credențiale.

**`/public/plata/{ref}/confirma` fără gardă e cea mai gravă poziție din lot.** Dacă semnătura procesatorului nu se verifică, oricine cu referința poate marca o factură ca încasată.
