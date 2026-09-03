# LOTUL 7 — verificări pentru 12 pași

**Ultimul lot. Cu el, 192 din 192.**

Fiecare verificare spune **ce trebuie să fie adevărat DUPĂ pas**, nu că pasul a mers.

Unde nu pot scrie o verificare fără să știu ceva ce nu am, o spun.

---

## Trei lucruri de citit înainte de pași

**8 din 12 sunt `cere_client`** — actorul e clientul firmei, nu cabinetul. Acolo „fără rol" e corect prin construcție. Verificările lor sunt despre **ce poate clientul**, nu despre ce lipsește.

**`POST /portal/acces-cont/acces` e singura rută de client care creează utilizatori.** Un client dă acces altui client. E poziția cea mai delicată din lot, și e cea care merită cea mai multă atenție.

**`pachete/genereaza` fără rol, lângă `poveste` și `trimite` care cer admin_firma** — toate trei ating `pachet_povestea` prin același modul. A treia oară în șapte loturi când aceeași clasă are roluri diferite.

---

## T35 — Clienții firmei (3)

**Nu știu dacă „clienți" înseamnă aici partenerii comerciali ai firmei sau persoanele de contact care primesc pachetul lunar.** Verificările de mai jos sunt scrise pentru a doua interpretare, fiindcă traseul e T35 — pachetul lunar. Dacă sunt parteneri comerciali, verificările se schimbă: atunci codul fiscal e obligatoriu, iar legătura cu facturile contează.

### `POST /tenants/{tenant_id}/clienti`
*admin_firma, angajat · plafon: clienti*

- adresa de email e validată la introducere, nu la prima trimitere — un pachet trimis la o adresă greșită se pierde tăcut
- un client cu aceeași adresă în aceeași firmă se refuză, sau se spune că există
- clientul nou nu primește automat acces la portal — accesul e o operațiune separată
- crearea se consemnează: cine, când

### `PUT /tenants/{tenant_id}/clienti/{client_id}`
*admin_firma, angajat · plafon: clienti*

- schimbarea adresei de email **nu retrimite pachetele anterioare** și nu schimbă la cine au ajuns
- dacă clientul are acces la portal, schimbarea adresei aici schimbă și adresa de autentificare? Verifică — dacă da, cineva poate prelua un cont schimbând un câmp
- modificarea se consemnează cu valoarea veche

### `DELETE /tenants/{tenant_id}/clienti/{client_id}`
*admin_firma, angajat · plafon: clienti*

- un client care a primit pachete nu se șterge — se dezactivează. Istoricul trimiterilor rămâne cu destinatarul identificabil
- dacă are acces la portal, ștergerea îl retrage? Sau rămâne un cont fără client? Verifică
- ștergerea se consemnează

---

## T35 — Pachetul lunar (3)

### `POST /pachete/{tenant_id}/genereaza`
*cere_cabinet · FĂRĂ ROL · plafon: pachet_povestea*

- pachetul generat conține **cifrele lunii închise**, nu recalculul de azi — dacă luna nu e închisă, se spune
- generarea nu trimite nimic; e o previzualizare până la `trimite`
- o a doua generare pe aceeași lună produce a doua versiune, nu suprascrie prima — sau, dacă suprascrie, se spune
- **fără rol, deși `poveste` și `trimite` cer admin_firma, iar toate trei ating aceeași tabelă**

### `POST /pachete/{tenant_id}/poveste`
*admin_firma · plafon: pachet_povestea*

- textul scris de contabil se păstrează cu autorul și momentul
- textul nu conține cifre calculate de el — sau, dacă le conține, ele nu se confruntă cu cele din pachet, iar aia e o divergență posibilă
- modificarea poveștii după trimitere produce o a doua versiune; ce s-a trimis rămâne

### `POST /pachete/{tenant_id}/trimite`
*admin_firma · artefact predat · plafon: pachet_povestea*

- **trimiterea e un eveniment de predare**: cui, când, la ce adresă, cu ce conținut
- se trimite versiunea generată, cu amprenta ei — nu o regenerare la momentul trimiterii
- o a doua trimitere e un al doilea eveniment, nu suprascrie primul
- eșecul trimiterii e o stare vizibilă, nu o eroare pierdută — pachetul rămâne netrimis
- clienții fără adresă validă se numesc înainte de trimitere, nu după

---

## T35 — Portalul clientului (5)

**Actorul e clientul. `cere_client` verifică identitatea, nu rolul — corect prin construcție.**

### `PUT /portal/acces-cont/email`
*cere_client · FĂRĂ ROL · scrie users (UPDATE)*

- schimbarea adresei de autentificare cere **confirmare pe adresa nouă** înainte de a intra în vigoare — altfel cineva cu sesiunea deschisă poate muta contul
- adresa veche primește o notificare despre schimbare
- schimbarea se consemnează: când, de la ce la ce
- cabinetul vede că adresa clientului s-a schimbat — altfel pachetele merg în altă parte fără ca nimeni să afle

### `POST /portal/acces-cont/acces`
*cere_client · rol verificat-în-corp · scrie user_tenants, users*

**Cea mai delicată rută din lot: un client creează un utilizator și îi dă acces la firma lui.**

- accesul dat nu poate depăși accesul celui care îl dă — un client nu poate acorda mai mult decât are
- accesul e **doar pe firma lui**, verificat pe rândul din `user_tenants`, nu pe ce trimite în corp
- utilizatorul creat primește acces la portal, nu la aplicația cabinetului — verifică pe drepturile efective, nu pe intenție
- dacă adresa aparține unui utilizator existent — al altei firme, sau al cabinetului — ruta refuză, sau leagă contul existent? A doua variantă e o cale de escaladare
- crearea se consemnează cu cine a dat accesul, iar **cabinetul vede** că un client a adăugat pe cineva
- parola inițială nu se trimite prin canal nesigur

### `DELETE /portal/acces-cont/acces/{user_id}`
*cere_client · FĂRĂ ROL · scrie user_tenants (DELETE), users (UPDATE)*

- clientul poate retrage doar accese pe **firma lui** — verificat pe rândul șters, nu pe ce cere
- clientul nu se poate retrage pe sine, sau, dacă poate, firma rămâne fără niciun acces de client
- `user_tenants` se șterge, dar utilizatorul rămâne — ce a făcut nu devine anonim
- retragerea e imediată: sesiunile active se închid, sau se spune că nu se închid
- retragerea se consemnează, iar cabinetul o vede

### `POST /portal/recomanda`
*cere_client · FĂRĂ ROL · întoarce {ok, rezultate}*

- **nu pot scrie verificarea fără să știu ce recomandă.** Recomandă cabinetul altcuiva? Recomandă clientului ce să facă? De completat din cod
- oricare ar fi: nu scrie nimic, deci verificarea e că **nu scrie nimic** — verificat structural

### `POST /portal/solicitari`
*cere_client · FĂRĂ ROL · scrie solicitari_client · plafon: notificari*

- solicitarea e legată de firma clientului, verificat pe context, nu pe ce trimite
- textul solicitării nu poate schimba date — e o cerere, nu o comandă
- cabinetul primește notificare; dacă notificarea eșuează, solicitarea rămâne, iar cineva o vede
- clientul își vede propriile solicitări și starea lor

---

## T35 — Solicitările, dinspre cabinet (1)

### `POST /tenants/{tenant_id}/solicitari`
*admin_firma · scrie solicitari_client*

- **nu pot scrie verificarea fără să știu ce face cabinetul aici.** Răspunde la o solicitare? Creează una în numele clientului?
- dacă creează în numele clientului, verifică că se distinge de una făcută de client — altfel istoricul devine ambiguu
- dacă răspunde, verifică unde ajunge răspunsul: pe solicitare, sau ca notificare separată

---

## Ce am observat scriind lotul

**`POST /portal/acces-cont/acces` merită cea mai multă atenție din tot lotul.** Un client creează un utilizator. Trei întrebări decid dacă e sigur: accesul nu depășește pe al celui care îl dă · adresa existentă nu leagă un cont străin · cabinetul vede că s-a întâmplat.

**`PUT /portal/acces-cont/email` fără confirmare pe adresa nouă** ar permite mutarea unui cont de pe o sesiune deschisă. Merită verificat dacă există confirmarea.

**Două rute cer completare din cod:** `portal/recomanda` (ce recomandă?) și `tenants/{id}/solicitari` (ce face cabinetul acolo?).

**`pachete/genereaza` fără rol** e a treia instanță în șapte loturi a aceleiași forme: aceeași clasă de operațiune, roluri diferite, fără motiv vizibil. Primele două: `vanzare-ic` vs `achizitie-ic`, `import-amef` vs `raport-z`.

---

## Cu asta, 192 din 192

Ce rămâne de făcut cu ele nu mai e scriere, ci ce am scris la începutul lui TRASEE: **un traseu se parcurge, nu se citește.** Verificările există; niciuna n-a fost încă rulată pe date.
