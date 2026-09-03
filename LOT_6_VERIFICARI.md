# LOTUL 6 — verificări pentru 30 de pași

Fiecare verificare spune **ce trebuie să fie adevărat DUPĂ pas**, nu că pasul a mers.

Unde nu pot scrie o verificare fără să știu ceva ce nu am, o spun.

---

## Trei lucruri de citit înainte de pași

**26 din 30 poartă „PLAFON, nemăsurat pe rută", iar la 20 singurul efect cunoscut e cel presupus prin modul.** Verificările pentru alea sunt formulate pe **efect**, nu pe tabelă — nu pot afirma unde ajunge ceva ce nu s-a măsurat.

**Inconsecvența de rol se repetă:** `achizitie-ic` cere `admin_firma`, `vanzare-ic` nu — aceeași clasă, aceleași tabele. Iar `horeca/raport-z` cere rol, `horeca/import-amef` nu, deși ambele produc nota de raport Z.

**T31 e cea mai gravă grupă din lot.** Patru rute fără rol care scriu direct în ce intră în D300 și D301 — completări manuale la declarații. O linie adăugată acolo ajunge într-o declarație depusă, fără să treacă prin nicio evidență.

---

## T23 — Bonul de la client (1)

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/stinge`
*admin_firma · scrie bonuri, facturi · plafon: casa_operatiuni, inregistrari, inregistrari_linii*

- stingerea produce **o singură** operațiune de casă; o a doua apăsare nu produce a doua plată
- suma stinsă nu depășește soldul neplătit al bonului
- plafonul de plăți în numerar se verifică — ruta îl cheamă, verifică că refuză când e depășit
- soldul casei nu devine negativ
- bonul trece în „stins" și nu se mai poate stinge
- data operațiunii de casă e într-o perioadă deschisă

---

## T24 — Bonul fiscal și raportul Z (2)

### `POST /tenants/{tenant_id}/horeca/import-amef`
*FĂRĂ ROL · scrie inregistrari, inregistrari_linii*

- nota produsă e **ciornă** — verificat pe starea scrisă
- fișierul p7b e verificat ca semnătură, nu doar citit — altfel orice XML poate deveni raport Z
- totalurile din notă coincid cu cele din fișier: total încasări, TVA pe cote, număr de bonuri
- un fișier importat de două ori nu produce a doua notă — verificat pe conținut, nu pe nume
- data raportului Z e într-o perioadă deschisă

### `POST /tenants/{tenant_id}/horeca/raport-z`
*admin_firma · scrie inregistrari, inregistrari_linii*

- **nu pot scrie verificarea fără să știu ce o deosebește de `import-amef`.** Ambele produc nota de raport Z; una are rol, cealaltă nu
- dacă e introducere manuală a raportului Z, verifică: totalurile pe cote de TVA se adună la totalul general
- dacă e aceeași operațiune pe două căi, e interdicția 15 — iar rolul diferit o face vizibilă

---

## T26 — Registratura (1)

### `POST /tenants/{tenant_id}/registratura`
*FĂRĂ ROL · plafon: registratura*

- numărul de înregistrare e **din serie, fără goluri** — registratura e un registru, nu o listă
- data înregistrării nu e în viitor
- un document înregistrat nu se poate șterge; se anulează, cu numărul păstrat
- verifică dacă numerotarea se reia la începutul anului sau e continuă — amândouă sunt legitime, dar trebuie să fie una

---

## T28 — Operațiunile intracomunitare (5)

### `PUT /tenants/{tenant_id}/d390-clasificare/reclasificare`
*FĂRĂ ROL · plafon: d390_manual, d390_reclasificare*

- reclasificarea **schimbă ce se declară** — o operațiune mutată din tip L în tip T schimbă D390
- override-ul poartă motivul: de ce clasificarea automată era greșită
- o reclasificare pe o lună cu D390 deja depus produce contradicție vizibilă, nu rescriere tăcută
- codul de țară și codul de TVA rămân neschimbate — reclasificarea privește tipul, nu partenerul
- **fără rol, deși schimbă conținutul unei declarații**

### `POST /tenants/{tenant_id}/d390-clasificare/manual`
*FĂRĂ ROL · plafon: d390_manual, d390_reclasificare*

- linia manuală poartă **motivul** existenței ei: ce operațiune reprezintă și de ce nu vine din evidență
- codul de TVA e validat algoritmic pentru țara respectivă, la introducere
- tipul e din nomenclatorul oficial — după reancorarea pe normă, nu pe XSD
- o linie manuală pe o lună cu D390 depus produce contradicție
- **fără rol, deși adaugă direct într-o declarație**

### `DELETE /tenants/{tenant_id}/d390-clasificare/manual/{mid}`
*FĂRĂ ROL · plafon: d390_manual, d390_reclasificare*

- ștergerea unei linii dintr-o lună cu D390 depus produce contradicție — declarația depusă conținea linia
- ștergerea se consemnează: cine, când, ce conținea linia
- **fără rol** — iar ștergerea unei linii dintr-o declarație e mai gravă decât adăugarea: dispare fără urmă

### `POST /tenants/{tenant_id}/achizitie-ic`
*admin_firma · scrie inregistrari, inregistrari_linii · plafon: articole, factura_linii, facturi, firma_profil, miscari_stoc*

- taxarea inversă: TVA-ul se înregistrează simultan deductibil și colectat, iar cele două se anulează în decont
- cursul e cel de la data exigibilității, cerut din registru — nu introdus liber
- codul de TVA al furnizorului e validat algoritmic și, dacă se poate, în VIES
- operațiunea intră în D390 cu codul corect, și în D300 la rândurile de achiziții intracomunitare
- dacă atinge stocul prin modul, mișcarea are aceeași dată cu nota
- **ruta atinge `firma_profil` prin modul** — verifică ce schimbă acolo; un import care modifică profilul firmei e neașteptat

### `POST /tenants/{tenant_id}/vanzare-ic`
*FĂRĂ ROL · scrie inregistrari, inregistrari_linii · plafon: articole, miscari_stoc*

- livrarea intracomunitară e scutită cu drept de deducere; nu se colectează TVA
- scutirea cere **dovada transportului** și codul de TVA valid al clientului. Fără ele, operațiunea nu e scutită
- codul de TVA al clientului e verificat în VIES la data operațiunii, iar rezultatul se păstrează — o verificare care nu se păstrează nu se poate dovedi la control
- operațiunea intră în D390 cu cod L
- **fără rol, deși `achizitie-ic` — aceeași clasă — cere admin_firma**

---

## T30 — Operațiunile în valută (2)

### `POST /tenants/{tenant_id}/decontare-valuta`
*FĂRĂ ROL · scrie inregistrari, inregistrari_linii · plafon: articole, curs_bnr_zilnic, miscari_stoc*

- diferența de curs se calculează între cursul de la înregistrarea creanței și cel de la decontare
- cursul vine din `curs_bnr_zilnic`; dacă lipsește pentru data respectivă, se aduce sau se refuză — **nu se folosește cel mai apropiat fără să se spună**
- diferența favorabilă merge în 765, cea nefavorabilă în 665 — verifică semnul
- decontarea parțială stinge proporțional, iar diferența de curs se calculează pe partea decontată
- **ruta atinge `articole` și `miscari_stoc` prin modul** — o decontare nu ar trebui să atingă stocul. Verifică de ce

### `POST /tenants/{tenant_id}/reevaluare-valuta`
*FĂRĂ ROL · scrie inregistrari, inregistrari_linii · plafon: curs_bnr_zilnic*

- reevaluarea se face la **finalul lunii**, pe soldurile în valută rămase — verifică dacă ruta o poate rula la orice dată
- cursul e cel din ultima zi bancară a lunii
- reevaluarea se aplică tuturor soldurilor în valută, nu doar celor selectate — o reevaluare parțială lasă bilanțul greșit
- o a doua reevaluare pe aceeași lună nu produce a doua notă — sau, dacă o produce, prima se stornează

---

## T31 — Completările manuale la declarații (4)

**Grupa cea mai gravă din lot: patru rute fără rol care scriu direct în ce intră în D300 și D301.**

### `POST /tenants/{tenant_id}/d301-operatiuni`
*FĂRĂ ROL · plafon: d301_operatiuni*

- `temei_307` e obligatoriu pentru operațiunile de tip 4 — construit pe 22.08, verifică că refuză fără el
- cursul e cel de la data documentului, cerut din registru
- valuta e din nomenclatorul de 20, iar limita e declarată — o valută legală din afara listei nu se poate depune
- o operațiune adăugată pe o lună cu D301 depus produce contradicție vizibilă
- **fără rol, deși scrie direct într-o declarație**

### `DELETE /tenants/{tenant_id}/d301-operatiuni/{op_id}`
*FĂRĂ ROL · plafon: d301_operatiuni*

- ștergerea pe o lună cu D301 depus produce contradicție — declarația conținea operațiunea
- ștergerea se consemnează cu ce conținea operațiunea
- **fără rol** — o operațiune ștearsă din declarație dispare fără urmă

### `POST /tenants/{tenant_id}/d300-manual`
*FĂRĂ ROL · plafon: d300_manual*

- rândul manual e din nomenclatorul de rânduri D300 — unul inexistent se refuză
- baza și TVA-ul sunt coerente cu cota rândului respectiv
- rândul manual poartă **motivul**: ce reprezintă și de ce nu vine din evidență
- suma rândurilor manuale plus cele derivate = totalul declarat; verifică că nu se dublează cu ce vine din facturi
- **fără rol, deși scrie direct în decontul de TVA**

### `DELETE /tenants/{tenant_id}/d300-manual/{rid}`
*FĂRĂ ROL · plafon: d300_manual*

- ștergerea pe o lună cu D300 depus produce contradicție
- ștergerea se consemnează cu ce conținea rândul
- **fără rol**

---

## T32 — Registrul de încasări și plăți (5)

**Partida simplă. Verificări comune celor cinci:**

- firma e în partidă simplă — altfel RIP nu se aplică
- data operațiunii e într-o perioadă deschisă
- numerotarea în registru nu are goluri

### `POST /tenants/{tenant_id}/rip/operatiuni`
*FĂRĂ ROL · plafon: rip_operatiuni*

- operațiunea e **încasare sau plată efectivă**, nu angajament — în partidă simplă contează fluxul, nu factura
- încasările impozabile se disting de cele neimpozabile; plățile deductibile de cele nedeductibile
- fiecare operațiune poartă documentul justificativ
- operațiunea intră în D212 la rândul corespunzător

### `PUT /tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza`
*FĂRĂ ROL · plafon: rip_operatiuni*

- **validarea transformă o ciornă în evidență** — după ea, operațiunea nu se mai editează
- validarea verifică înainte: document justificativ prezent, dată în perioadă deschisă, categorie fiscală atribuită
- cine a validat se consemnează
- **fără rol, iar aceasta e ruta care produce evidența în partidă simplă** — echivalentul lui `jurnal/{id}/valideaza`

### `DELETE /tenants/{tenant_id}/rip/operatiuni/{op_id}`
*FĂRĂ ROL · plafon: rip_operatiuni*

- o operațiune **validată** nu se șterge — se stornează
- ștergerea pe o lună cu D212 depus produce contradicție
- **fără rol**

### `POST /tenants/{tenant_id}/rip/import-banca`
*FĂRĂ ROL · plafon: rip_operatiuni*

- fiecare tranzacție din extras produce **o singură** operațiune RIP
- un extras importat de două ori nu dublează — verificat pe conținut
- operațiunile importate intră ca **ciorne**, nu validate; categoria fiscală se atribuie de om
- tranzacțiile care nu s-au putut clasifica se numesc, nu se sar

### `POST /tenants/{tenant_id}/rip/import-casa`
*FĂRĂ ROL · plafon: rip_operatiuni*

- aceleași ca la bancă
- **verifică dacă o operațiune de casă poate ajunge în RIP de două ori** — o dată din registrul de casă, o dată din import

---

## T33 — Exportul contabil (2)

### `POST /tenants/{tenant_id}/facturi/export-saga`
*admin_firma · plafon: artefacte_produse*

- fișierul exportat se păstrează ca artefact: conținut, moment, autor, amprentă, exemplar
- numărul de facturi din fișier = numărul de facturi din perioada exportată, iar cele excluse se numesc cu motivul
- codificarea fișierului e cea cerută de SAGA — verifică diacriticele
- o factură exportată de două ori nu creează două intrări la destinație — sau, dacă poate, se avertizează

### `POST /tenants/{tenant_id}/facturi/export-winmentor`
*admin_firma · plafon: artefacte_produse*

- aceleași ca la SAGA
- `Facturi.txt` și `Articole.txt` sunt coerente între ele: fiecare articol referit în facturi există în fișierul de articole
- codificarea Windows-1250 nu pierde diacritice — verifică pe un partener cu ș, ț, ă
- cele două fișiere sunt în același zip și au aceeași perioadă

---

## T34 — Rapoarte salvate și centre de cost (5)

### `POST /tenants/{tenant_id}/rapoarte-salvate`
*FĂRĂ ROL · plafon: rapoarte_salvate*

- raportul salvat păstrează **criteriile**, nu rezultatul — altfel devine o fotografie care se învechește
- dacă păstrează rezultatul, poartă data la care a fost calculat, iar la deschidere se spune că e vechi

### `DELETE /tenants/{tenant_id}/rapoarte-salvate/{vid}`
*FĂRĂ ROL · plafon: rapoarte_salvate*

- ștergerea nu atinge datele din care raportul se calculează
- un raport partajat cu altcineva din cabinet — verifică cine îl poate șterge

### `POST /tenants/{tenant_id}/centre-cost`
*FĂRĂ ROL · plafon: bugete, centre_cost*

- codul centrului e unic în firmă
- centrul nou nu atinge repartizările deja făcute

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}`
*FĂRĂ ROL · plafon: bugete, centre_cost*

- redenumirea unui centru nu schimbă repartizările istorice
- dezactivarea unui centru cu cheltuieli repartizate nu-l șterge — verifică ce se întâmplă

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}/buget`
*FĂRĂ ROL · plafon: bugete, centre_cost*

- bugetul e pe an; modificarea unui an încheiat se refuză, sau se consemnează
- bugetul nu constrânge cheltuielile reale — e o referință, nu o limită. Verifică dacă blochează ceva, ceea ce ar fi greșit
- suma bugetelor pe centre nu trebuie să dea un total impus — nu e o repartizare

---

## T35 — Accesul clientului (3)

### `POST /tenants/{tenant_id}/client-acces`
*admin_firma, verificat-în-corp · scrie user_tenants, users · plafon: firma_profil, tenants*

- **ruta creează un utilizator** — verifică ce drepturi primește: doar pe firma respectivă, doar citire, doar portalul
- un utilizator existent legat de altă firmă nu primește acces la asta fără o operațiune explicită
- parola inițială nu se trimite prin canal nesigur, și se schimbă la prima intrare
- **atinge `tenants` prin modul** — verifică de ce: crearea unui acces de client n-ar trebui să atingă tabela de firme
- crearea se consemnează: cine a dat accesul, când, cui

### `DELETE /tenants/{tenant_id}/client-acces/{user_id}`
*admin_firma · scrie users*

- retragerea accesului e imediată — sesiunile active se închid, sau se spune că nu se închid
- utilizatorul nu se șterge; se dezactivează. Ce a făcut rămâne în urmă cu autorul identificabil
- retragerea se consemnează

### `POST /tenants/{tenant_id}/acces-portal`
*admin_firma, angajat, verificat-în-corp · token de previzualizare*

- tokenul e **read-only** și expiră — verifică ambele, nu doar că e declarat așa
- tokenul e legat de firmă și de utilizatorul care l-a emis
- emiterea se consemnează: cine, când, pentru ce firmă
- un token expirat nu mai dă acces, iar reînnoirea e o operațiune nouă, nu o prelungire tăcută

---

## Ce am observat scriind lotul

**T31 e grupa care mă îngrijorează cel mai mult:** patru rute fără rol care scriu direct în conținutul lui D300 și D301. O linie adăugată acolo ajunge într-o declarație fără să treacă prin evidență, iar una ștearsă dispare fără urmă.

Criteriul de la R55 le prinde — schimbă ce datorează firma — dar gardul mecanic nu, fiindcă nu scriu `validata`. E aceeași situație cu `firma-profil/date`: a doua axă.

**`rip/operatiuni/{id}/valideaza` fără rol** e echivalentul lui `jurnal/{id}/valideaza`, pentru partida simplă. Aceeași operațiune — transformarea unei ciorne în evidență — pe alt regim.

**Două rute ating tabele neașteptate prin modul:** `decontare-valuta` atinge `articole` și `miscari_stoc`; `client-acces` atinge `tenants`. Amândouă merită verificate — nu ca defecte, ci pentru că efectul e mai larg decât numele rutei.

**O rută cere completare din cod:** ce deosebește `horeca/raport-z` de `horeca/import-amef`. Rolul diferit sugerează că nu sunt același lucru, dar produc aceeași notă.
