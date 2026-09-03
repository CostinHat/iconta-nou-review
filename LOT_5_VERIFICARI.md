# LOTUL 5 — verificări pentru 30 de pași

Fiecare verificare spune **ce trebuie să fie adevărat DUPĂ pas**, nu că pasul a mers.

Unde nu pot scrie o verificare fără să știu ceva ce nu am, o spun.

---

## Cele trei observații din gardă, luate ca dată

**`firma-profil/date` fără rol, iar `firma-profil/regim-tva` cu rol.** Datele fiscale de acolo intră în declarații. Verificările de mai jos o tratează ca poziție, nu ca notă.

**Cele 14 rute de stoc și rețete sunt toate fără rol**, toate ating `inregistrari` prin modul — plafon, nemăsurat pe rută. Verificările sunt formulate pe efect, nu pe tabelă.

**Rutele de portal sunt pe `cere_context` fiindcă actorul e clientul.** Acolo „fără rol" e corect prin construcție. Verificările lor sunt despre ce poate clientul, nu despre ce lipsește.

---

## T11 — Închiderea lunii (2)

### `POST /tenants/{tenant_id}/facturi/perioada/confirma`
*admin_firma · scrie perioade_blocate*

- **nu pot scrie verificarea fără să știu ce o deosebește de `POST /perioade-blocate`.** Sunt două acte de închidere pe aceeași tabelă? De completat din cod
- dacă e închiderea pe domeniul facturi, verifică ce se întâmplă când unul e închis și celălalt nu — o perioadă parțial închisă e o stare sau o inconsistență?

### `POST /tenants/{tenant_id}/facturi/perioada/redeschide`
*admin_firma*

- redeschiderea poartă **motiv obligatoriu** — P15
- urma închiderii nu se șterge: cine a închis, când, rămân. E interdicția 36
- documentele emise din perioada redeschisă se marchează sub rezervă
- verifică relația cu `DELETE /perioade-blocate`: dacă cele două redeschid același lucru pe căi diferite, una poate ocoli verificările celeilalte

---

## T13 — Trecerea de regim (4)

### `PUT /tenants/{tenant_id}/firma-profil/regim-tva`
*admin_firma*

- schimbarea regimului are **dată de la care se aplică**, nu se aplică retroactiv tăcut
- perioadele închise sub regimul vechi rămân sub el — recalcularea lor produce contradicție, nu rescriere
- trecerea de la plătitor la neplătitor cere ajustarea TVA la bunuri de capital; verifică dacă se semnalează
- declarațiile datorate se recalculează din noul regim, iar cele generate sub cel vechi se marchează

### `PUT /tenants/{tenant_id}/firma-profil/date`
*FĂRĂ ROL*

- **datele fiscale de aici intră în declarații** — CUI, denumire, adresă, capital. O modificare fără rol schimbă ce se depune
- CUI-ul modificat: verifică dacă e permis deloc. Un CUI schimbat pe o firmă cu declarații depuse rupe corespondența cu tot ce s-a depus
- modificarea se consemnează: cine, când, de la ce la ce
- **poziție, nu notă:** ruta cere rol pe regim-tva și nu pe datele care ajung în același loc

### `PUT /tenants/{tenant_id}/firma-profil/model`
*FĂRĂ ROL*

- **nu pot scrie verificarea fără să știu ce e „model".** Model de firmă? De document? De contare? De completat din cod

### `PUT /tenants/{tenant_id}/vector`
*admin_firma*

- vectorul decide ce declarații datorează firma — o schimbare produce declarații noi datorate și altele care nu mai sunt
- schimbarea are dată de la care se aplică; perioadele anterioare rămân sub vectorul vechi
- o declarație deja generată pentru o poziție scoasă din vector se marchează, nu dispare
- vectorul se confruntă cu faptele: dacă firma are operațiuni intracomunitare și vectorul nu are D390, se semnalează — e chiar cazul de la 006

---

## T16 — Pontajul (2)

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/pontaj`
*FĂRĂ ROL*

- zilele pontate nu depășesc zilele lucrătoare din lună
- pontajul nu se poate modifica pentru o lună cu stat de plată emis — sau, dacă se poate, produce contradicție vizibilă
- concediile medicale și cele de odihnă se scad din zilele lucrate, nu se adună separat
- pontajul unei luni închise se refuză

### `POST /tenants/{tenant_id}/pontaj/confirma`
*admin_firma*

- confirmarea e ce **deblochează tichetele** — fără ea, statul nu le acordă. Verifică că blocajul e real, nu doar semnalat
- confirmarea poartă autorul și momentul
- după confirmare, pontajul nu se mai modifică fără o operațiune de deconfirmare consemnată
- confirmarea verifică întâi coerența: toți salariații activi au pontaj, sau se spune cine lipsește

---

## T17 — Plata salariilor (1)

### `POST /tenants/{tenant_id}/plata-salarii-fisier`
*admin_firma · artefact predat (SEPA)*

- fișierul se păstrează: conținutul, momentul, autorul, amprenta, numărul exemplarului
- sumele din fișier coincid cu **netul din statul de plată emis** — nu se recalculează la generare
- fiecare salariat din fișier are IBAN valid; cei fără IBAN se numesc, iar fișierul nu se generează parțial fără să spună
- totalul fișierului = suma neturilor, verificat explicit
- un fișier generat de două ori pentru aceeași lună produce al doilea exemplar, nu suprascrie primul — iar dublarea plății e riscul, deci se avertizează

---

## T19 — Scadențarul (1)

### `POST /tenants/{tenant_id}/scadentar/opt-in`
*admin_firma*

- opt-in-ul poartă autorul și momentul — e o decizie despre comunicarea cu clienții firmei
- verifică ce se trimite: notificări către clienți în numele firmei, sau doar către cabinet?
- dacă merge către clienți, opt-out-ul trebuie să existe și să fie la fel de simplu

---

## T20 — Stocuri (7)

**Verificări comune celor șapte:**

- mișcarea de stoc are aceeași dată cu nota contabilă produsă
- stocul nu devine negativ — o ieșire peste stoc se refuză, cu cantitatea disponibilă
- perioada nu e închisă
- nota respectă partida dublă, conturile există

### `POST /tenants/{tenant_id}/stocuri/descarcare`
*FĂRĂ ROL · plafon*

- descărcarea se leagă de un document — factură, bon, consum. O descărcare fără document rupe lanțul P14
- metoda de evaluare la ieșire (FIFO, CMP) e cea configurată pe firmă, nu aleasă la operațiune
- costul descărcat vine din intrări, nu se introduce liber

### `POST /tenants/{tenant_id}/stocuri/intrare`
*FĂRĂ ROL · plafon*

- intrarea se leagă de un document — NIR, producție, transfer
- costul de intrare cuprinde ce trebuie: preț, transport, taxe nedeductibile. Verifică ce cuprinde efectiv
- o intrare pe un articol inexistent creează articolul sau se refuză — verifică ce face

### `POST /tenants/{tenant_id}/stocuri/iesire`
*FĂRĂ ROL · plafon*

- **nu pot scrie verificarea fără să știu ce o deosebește de `descarcare`.** De completat din cod
- dacă sunt aceeași operațiune pe două rute, e interdicția 15

### `POST /tenants/{tenant_id}/stocuri/transfer`
*FĂRĂ ROL · plafon*

- transferul între gestiuni nu schimbă valoarea totală a stocului — suma iese dintr-o gestiune și intră în alta, la același cost
- transferul nu produce venit sau cheltuială
- gestiunea sursă și cea destinație există și sunt diferite

### `POST /tenants/{tenant_id}/stocuri/reclasificare`
*FĂRĂ ROL · plafon*

- reclasificarea schimbă categoria, nu cantitatea și nu valoarea
- verifică dacă poate muta un articol între categorii cu tratamente fiscale diferite — marfă în materie primă schimbă contul, deci nota

### `PUT /tenants/{tenant_id}/articole/{articol_id}/nivel-minim`
*FĂRĂ ROL*

- nivelul minim e o alertă, nu o restricție — verifică dacă blochează ieșirile sub el, ceea ce ar fi greșit
- modificarea nu atinge stocul

### `PUT /tenants/{tenant_id}/articole/{articol_id}/barcode`
*FĂRĂ ROL*

- un cod de bare duplicat în firmă se refuză — altfel scanarea devine ambiguă
- modificarea nu atinge stocul și nu produce mișcare

---

## T21 — Rețete și produse (7)

### `POST /tenants/{tenant_id}/produse/potriveste`
*FĂRĂ ROL*

- potrivirea e o **propunere**, nu o legătură creată — verifică structural că nu scrie
- fiecare potrivire propusă poartă gradul de certitudine; una slabă nu se prezintă ca sigură

### `POST /tenants/{tenant_id}/produse`
*FĂRĂ ROL*

- codul produsului e unic în firmă
- produsul cu rețetă are cost calculat din componente, nu introdus liber

### `PUT /tenants/{tenant_id}/produse/{produs_id}`
*FĂRĂ ROL*

- modificarea rețetei unui produs **nu recalculează costul producțiilor trecute** — acelea au costul de la momentul lor
- dacă recalculează, produce contradicție cu notele deja scrise

### `DELETE /tenants/{tenant_id}/produse/{produs_id}`
*FĂRĂ ROL*

- un produs cu mișcări de stoc nu se șterge — se dezactivează
- ștergerea nu atinge producțiile trecute

### `POST /tenants/{tenant_id}/retete`
*FĂRĂ ROL*

- componentele rețetei există ca articole
- cantitățile sunt pozitive, iar unitatea de măsură a componentei coincide cu cea a articolului

### `DELETE /tenants/{tenant_id}/retete/{reteta_id}`
*FĂRĂ ROL*

- o rețetă folosită într-o producție nu se șterge — se dezactivează
- ștergerea nu schimbă costul producțiilor trecute

### `POST /tenants/{tenant_id}/retete/descarca`
*FĂRĂ ROL · plafon*

- descărcarea pe rețetă scoate din stoc **componentele**, la cantitățile din rețetă, înmulțite cu cantitatea produsă
- produsul finit intră în stoc la costul componentelor descărcate
- suma valorii componentelor ieșite = valoarea produsului intrat
- dacă o componentă nu are stoc suficient, operațiunea se refuză întreagă — nu descarcă parțial

---

## T22 — Mijloc fix (2)

### `POST /tenants/{tenant_id}/amortizare`
*admin_firma · scrie validata direct*

- amortizarea lunară se calculează din valoarea de intrare și durata rămasă, la data lunii
- un mijloc fix complet amortizat nu mai produce amortizare
- amortizarea contabilă și cea fiscală pot diferi — verifică dacă se disting, sau se calculează una singură
- **scrie `validata` direct**, deci a primit rol azi. Verifică că nu se poate rula de două ori pe aceeași lună

### `POST /tenants/{tenant_id}/reevaluare-imobilizare`
*FĂRĂ ROL*

- reevaluarea schimbă valoarea de intrare, deci **schimbă amortizarea viitoare** — dar nu pe cea trecută
- diferența din reevaluare merge la rezervă, nu la venit — verifică unde ajunge
- reevaluarea în minus sub valoarea contabilă e cheltuială, nu rezervă negativă
- **fără rol, deși schimbă o bază de calcul care intră în declarația de profit** — poziție, nu notă

---

## T23 — Bonul de la client (4)

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/aproba`
*admin_firma · scrie validata direct*

- aprobarea produce evidență — de aceea a primit rol azi
- bonul aprobat poartă legătura către imaginea din care a ieșit
- cifrele aprobate coincid cu cele citite din imagine, sau diferența e consemnată ca modificată de om
- un bon aprobat de două ori nu produce două note

### `POST /tenants/{tenant_id}/portal/bon`
*cere_context · actorul e CLIENTUL*

- clientul poate încărca doar pe firma lui — verificat pe context, nu pe rol
- bonul intră ca **nevalidat**; clientul nu produce evidență
- imaginea se păstrează, nu doar datele citite din ea

### `POST /tenants/{tenant_id}/portal/bon/{bon_id}/confirma`
*cere_context · actorul e CLIENTUL*

- confirmarea clientului nu e aprobare — bonul rămâne de validat de cabinet
- verifică ce poate schimba clientul la confirmare: dacă poate modifica sumele, cabinetul trebuie să vadă ce a modificat

### `DELETE /tenants/{tenant_id}/portal/bon/{bon_id}`
*cere_context · actorul e CLIENTUL*

- clientul poate șterge doar bonuri **neaprobate** — unul aprobat a devenit evidență
- ștergerea nu lasă în urmă imaginea orfană, sau o lasă și se spune
- ștergerea se consemnează — un bon care dispare fără urmă e o cheltuială care nu se mai poate reconstitui

---

## Ce am observat scriind lotul

**Trei rute cer completare din cod:** `facturi/perioada/confirma` (ce o deosebește de `perioade-blocate`?), `firma-profil/model` (ce e „model"?), `stocuri/iesire` (ce o deosebește de `descarcare`?).

**Două dintre ele sunt posibile perechi duplicate.** Dacă `facturi/perioada/confirma` și `perioade-blocate` închid același lucru, una poate ocoli verificările celeilalte — iar R58 tocmai a arătat că doar una verifică ceva. Iar dacă `iesire` și `descarcare` sunt aceeași operațiune, e interdicția 15.

**`firma-profil/date` fără rol e cea mai gravă poziție din lot.** Datele fiscale de acolo intră în declarații, iar ruta vecină — `regim-tva` — cere admin_firma. Aceeași suprafață, două tratamente.

**`reevaluare-imobilizare` fără rol** schimbă baza de amortizare, deci cheltuiala deductibilă, deci impozitul pe profit. Nu scrie `validata`, deci criteriul de la R55 n-o prinde — dar efectul ei ajunge în declarație.
