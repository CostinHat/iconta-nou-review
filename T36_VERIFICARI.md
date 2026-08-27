# T36 — verificări pentru cele patru sloturi

Ciclul de viață al firmei: creare · identitate · dezactivare/reactivare · scoatere.

Fiecare verificare spune **ce trebuie să fie adevărat DUPĂ pas**, nu că pasul a mers.

---

## Ce e diferit la traseul ăsta

Cele patru rute nu schimbă date **ale** unei firme — schimbă **existența** ei. Iar trei dintre ele sunt ireversibile în feluri diferite: crearea consumă un CUI, ștergerea distruge schema, iar schimbarea identității rescrie ce s-a declarat sub numele vechi.

Verificările de mai jos pornesc de aici, nu de la tabelele atinse.

---

### `POST /tenants`
*garda `cere_rol` · rol:admin_firma*
*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): firma_profil (INSERT/UPDATE) · tenants (INSERT/UPDATE) · user_tenants (INSERT) — prin `tenant_provisioning`*

**Ce trebuie să fie adevărat după:**

- **CUI-ul e unic în cabinet.** Un CUI care există deja se refuză, iar refuzul spune care firmă îl poartă — altfel omul nu știe dacă e a lui sau a altui cabinet
- **Denumirea e unică în cabinet.** Nici Registrul Comerțului, nici ANAF nu permit două firme cu același nume; două rânduri identice în portofoliu sunt un fapt imposibil în realitate
- CUI-ul trece cifra de control **înainte** de interogarea la ANAF — altfel se cheltuie un apel extern pe o valoare invalidă
- firma creată are **schemă proprie**, iar rândul din `tenants` și schema există amândouă. O firmă fără schemă e o afirmație falsă despre lume — e cauza rândului 2020
- dacă crearea schemei eșuează, rândul din `tenants` nu rămâne. Tranzacția e întreagă sau nu e deloc
- `user_tenants` leagă firma de cabinetul care a creat-o, nu de utilizatorul care a apăsat
- ce s-a preluat de la ANAF — adresă, CAEN, Reg.Com., stare TVA — e consemnat **cu momentul preluării**, ca la o reverificare să se știe ce era atunci
- **denumirea preluată de la ANAF nu se suprascrie tăcut cu ce a tastat omul, și nici invers.** Dacă cele două diferă, se arată amândouă și se cere alegerea
- ecranul confirmă crearea. O listă care se reîncarcă fără mesaj lasă omul să deducă — iar aia a ascuns trei zile un defect

**Refuzul, în orice caz de mai sus:** spune **ce** e greșit și **unde** se corectează, sub câmpul la care se referă — nu sub primul câmp al formularului.

---

### `PUT /tenants/{tenant_id}`
*garda `cere_rol` · rol:admin_firma*
*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): firma_profil (INSERT/UPDATE) · tenants (INSERT/UPDATE) · user_tenants (INSERT) — prin `tenant_provisioning`*

**Ce trebuie să fie adevărat după:**

- **CUI-ul unei firme cu declarații depuse nu se schimbă.** Se refuză, cu numărul declarațiilor. Un CUI schimbat rupe corespondența cu tot ce s-a depus, iar ANAF nu se poate corecta din aplicație
- dacă nu are declarații, schimbarea de CUI cere **reconfirmare la ANAF** — noul CUI e validat ca la creare
- schimbarea de denumire păstrează **denumirea veche cu perioada** în care a fost valabilă. Un document emis sub numele vechi trebuie să se poată explica
- denumirea nouă e unică în cabinet, ca la creare
- **ce s-a emis nu se rescrie.** Facturile, declarațiile și statele emise poartă identitatea de la momentul emiterii, nu pe cea de azi
- modificarea se consemnează: cine, când, de la ce la ce — pe fiecare câmp schimbat, nu global
- `user_tenants (INSERT)` la o rută de modificare e neașteptat — verifică ce leagă, și dacă o modificare poate crea o legătură nouă

**Iar întrebarea de fond, care decide restul:** de ce se poate schimba denumirea unei firme cu CUI validat la ANAF? Dacă numele vine din registru, singura schimbare legitimă e cea care urmează o schimbare la registru — iar atunci se reia validarea, nu se editează câmpul.

---

### `POST /tenants/{tenant_id}/activare`
*garda `cere_rol` · rol:admin_firma*
*ce face: [R72] Dezactivează / reactivează firma — poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firme_scoase (INSERT/UPDATE) · tenants (DELETE/UPDATE) · users (UPDATE) — prin `tenant_stergere`*

**Ce trebuie să fie adevărat după:**

- **dezactivarea nu șterge nimic.** Schema rămâne, datele rămân, documentele emise rămân accesibile
- firma dezactivată **nu mai apare** în listele de lucru, dar apare în „Firme dezactivate" — cu drumul de întoarcere vizibil
- **nu se mai poate scrie** în firma dezactivată: nicio notă, nicio factură, nicio declarație. Verifică pe toate căile de scriere, nu doar pe cele din ecran
- **se poate încă citi**: un control fiscal pe o perioadă veche cere accesul la documentele unei firme care nu mai e client
- conturile de client ale unei firme dezactivate **nu mai pot intra în portal** — sau pot, dar văd că firma e inactivă. Alege una și fă-o explicită
- reactivarea readuce firma exact în starea de dinainte — nimic pierdut, nimic recalculat
- amândouă se consemnează: cine, când, în ce sens
- **`tenants (DELETE)` pe ruta de activare e neașteptat.** Verifică de ce ruta de dezactivare poate șterge rândul firmei — dacă e o cale comună cu `tenant_stergere`, o dezactivare n-are ce căuta pe ea

**Iar întrebarea care contează:** ce distinge dezactivarea de scoatere, din punctul de vedere al omului? Dacă un cabinet nu știe pe care s-o aleagă, ecranul trebuie s-o spună — una e reversibilă, cealaltă nu.

---

### `DELETE /tenants/{tenant_id}`
*garda `cere_rol` · rol:admin_firma*
*ce face: [R72] Scoate din portofoliu o firmă FĂRĂ evidență — poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firme_scoase (INSERT/UPDATE) · tenants (DELETE/UPDATE) · users (UPDATE) — prin `tenant_stergere`*

**Ce trebuie să fie adevărat după:**

- **o firmă cu evidență nu se șterge.** Refuzul enumeră ce s-a găsit, nu spune doar „are documente"
- **o tabelă lipsă din schemă nu se numără ca zero.** Refuzul spune „nu pot decide" — o redenumire de tabelă ar transforma o firmă cu documente într-una ștearsă fără urmă
- toate cele 13 tabele din `public` care poartă `tenant_id` se curăță, **înainte** de `DROP SCHEMA`. Dacă una eșuează, schema rămâne și operațiunea se poate relua
- **nimic din afara firmei nu se mișcă.** Numărul de firme ale cabinetului scade cu unu; toate celelalte totaluri rămân
- un cont de client rămas fără nicio firmă **se dezactivează, nu se șterge** — identitatea unui om nu e proprietatea firmei
- urma din `firme_scoase` poartă: nume, CUI, schema, cine a apăsat, când, ce s-a curățat tabelă cu tabelă, și urmele păstrate
- **urma e citibilă de om**, din ecranul „Firme scoase" — nu doar din `psql`
- previzualizarea arată **ce dispare și ce se păstrează**, înainte de confirmare. Cifrele din previzualizare corespund cu ce se șterge efectiv
- confirmarea se cere **pe CUI, nu pe nume** — numele se repetă, iar chiar asta a produs restanța
- **la ștergerea unui cabinet întreg (GDPR), nu se păstrează nimic.** Un log care păstrează ce trebuia să dispară anulează ștergerea pe care o consemnează

---

## Ce am observat scriind sloturile

**Trei dintre cele patru rute sunt ireversibile în feluri diferite**, iar ecranul nu spune care e care. Crearea consumă un CUI. Ștergerea distruge schema. Schimbarea identității rescrie ce s-a declarat sub numele vechi.

Doar dezactivarea are drum de întoarcere — și e singura care nu pare periculoasă.

**Două rute ating tabele neașteptate:** `activare` poate face `tenants (DELETE)`, iar `PUT` poate face `user_tenants (INSERT)`. Amândouă sunt plafon nemăsurat pe rută, deci pot fi artefacte ale instrumentului — dar merită verificate.

**Iar întrebarea de fond a traseului**, pe care n-o pot decide singur: de ce se poate schimba denumirea unei firme cu CUI validat la ANAF?

Dacă numele vine din registru, editarea liberă a câmpului e chiar cauza duplicatelor. Iar duplicatul a costat deja — pe el a căzut diagnosticul de la pasul 8 al probei R62.
