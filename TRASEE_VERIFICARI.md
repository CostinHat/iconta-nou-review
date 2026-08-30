# TRASEE — CE TREBUIE SA FIE ADEVARAT DUPA FIECARE PAS

Al cincilea document, si singurul care NU se genereaza. `TRASEE.md` Partea XII spune
**ce face** fiecare pas — extras din cod. Aici se scrie **ce trebuie sa fie adevarat
dupa el** — iar aia nu se poate extrage din cod: codul spune ce s-a schimbat, nu ce
*trebuia* sa se schimbe.

**Cum se completeaza.** Sub fiecare pas e un rand care incepe cu `- [ ]`. Se inlocuieste
cu propozitia care trebuie sa fie adevarata dupa pasul ala. Diferenta care conteaza
(`TRASEE.md` VII.5): *«butonul a functionat, coada a trecut de la 3 la 2»* e o
observatie; *«declaratia are stare depusa, cu autor si moment, iar verdictul de
validare e pastrat»* e o verificare.

**Ce pazeste instrumentul aici:** ca niciun pas sa nu ramana fara loc. `--verificari`
NU rescrie ce s-a scris — listeaza doar ce lipseste. Un pas nou (o ruta noua) apare ca
lipsa in `core/test_trasee.py`, nu suprascrie nimic.

---

## T01 — Declarația — generare, validare, coadă, aprobare, depunere

*clasa MECANIC · 15 rute · 8 schimba date · 7 firme il pot exercita azi*

*citiri (nu schimba nimic): `/coada`, `/coada/{coada_id}/continut`, `/control-fiscal`, `/control-fiscal/{tenant_id}`, `/declaratii/tipuri`, `/firme/{tenant_id}/verificari`, `/termene`*

### `POST /coada`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [x] declarația intră în coadă **numai cu verdict de validare păstrat** — altfel ruta refuză și spune de ce
- rândul din coadă poartă: tip, perioadă, firmă, cine a pregătit, momentul
- nu se creează rând în `declaratii_depuse` la intrarea în coadă — depunerea nu s-a întâmplat

### `POST /coada/{coada_id}/aproba`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [x] cine aprobă e consemnat, și e diferit de cine a pregătit dacă patru ochi e activ **și** posibil
- dacă patru ochi e activ și imposibil (un singur validator), ruta refuză cu motivul, nu tace
- starea trece în „aprobată", nu direct în „depusă"

### `POST /coada/{coada_id}/depune`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [x] ruta refuză o declarație fără verdict de validare păstrat, sau cu verdict pe altă amprentă decât fișierul curent
- se scrie în `declaratii_depuse`: tip, perioadă, momentul, autorul autorizării, amprenta fișierului, indexul de la autoritate dacă există
- dacă indexul lipsește, starea nu e „confirmată" — e „nelămurită", conform P19
- declarația iese din coadă numai după ce rândul de depunere există

### `POST /coada/{coada_id}/respinge`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [x] respingerea poartă **motivul**, obligatoriu
- declarația nu dispare din coadă — rămâne, cu starea „respinsă" și motivul vizibil
- cine a pregătit vede respingerea; nu se stinge prin ignorare

### `POST /declaratii/{tip}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: intoarce {avertismente, componente, note_rezultat, operatiuni, tip, xml}*

- [x] fiecare operațiune din evidență care ar trebui să apară în declarație, apare — absența nu e vizibilă în structură
- `operatiuni` conține și cele excluse, cu motivul și temeiul excluderii, nu doar cele incluse
- `avertismente` e gol înseamnă „nimic de semnalat", nu „n-am verificat"
- două generări succesive pe aceleași date produc același XML — altfel amprenta din verdict nu poate fi de încredere

### `POST /declaratii/{tip}/valideaza`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: Genereaza declaratia si o trece prin validatorul OFICIAL ANAF (DUKIntegrator)*

- [x] verdictul se **păstrează**, cu momentul, versiunea validatorului și **amprenta fișierului validat**
- un verdict pe un XML regenerat între timp nu mai e verdict — dacă amprenta diferă, se marchează stătut
- respingerea validatorului e o stare a documentului, nu o eroare a aplicației: se păstrează cu ce a spus validatorul

### `POST /tenants/{tenant_id}/istoric-declaratii-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): declaratii_depuse (DELETE/INSERT) — prin `istoric_declaratii_import_api`*

- [x] același conținut ca la pasul de încărcare — ce s-a văzut la previzualizare e ce s-a salvat
- o a doua rulare cu același fișier nu dublează rândurile

### `POST /tenants/{tenant_id}/istoric-declaratii-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): declaratii_depuse (DELETE/INSERT) · migrare_status (INSERT) — prin `istoric_declaratii_import_api`, `migrare_api`*

- [x] fiecare declarație din fișier are un rând în `declaratii_depuse`, cu tip, perioadă și dată de depunere
- numărul de rânduri scrise = numărul de declarații din fișier, minus cele respinse, iar respinsele sunt numite
- un `DELETE/INSERT` nu lasă în urmă rânduri din import-ul anterior care nu mai sunt în fișier — sau, dacă le lasă, se spune care
- `migrare_status` marchează stratul ca parcurs, cu momentul

## T02 — Factura emisă — creare, contabilizare, ieșiri

*clasa MECANIC · 20 rute · 14 schimba date · 12 firme il pot exercita azi*

*citiri (nu schimba nimic): `/api/v1/firme/{tenant_id}/facturi`, `/tenants/{tenant_id}/facturi`, `/tenants/{tenant_id}/facturi-recurente`, `/tenants/{tenant_id}/facturi/numerotare`, `/tenants/{tenant_id}/facturi/{factura_id:int}`, `/tenants/{tenant_id}/facturi/{factura_id}/pdf`*

### `POST /api/v1/firme/{tenant_id}/facturi`

*garda `cere_api_key` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `facturi_api`, `stocuri_cv_api`*

- [x] ruta cu cheie de API aplică **aceleași reguli** ca ruta din interfață: numerotare, cod fiscal obligatoriu, notă cu conturi valide
- o cheie de API nu are rol, deci nu poate face ce cere admin_firma pe ruta echivalentă — verifică dacă asta e adevărat sau dacă cheia ocolește restricția
- **dacă ocolește: e prag 1.** Un integrator cu cheie ar putea emite facturi pe care un asistent nu le poate emite
- **verificat la sursă (26.08.2026): DA, ocolește rolul — dar nu e escaladare, și NU e prag 1.** `cere_api_key` verifică doar cheia și întoarce `{firm}`; nu există utilizator, deci nu există rol. Ruta cheamă **aceeași** `emite_factura` ca `/facturi/emite`, care cere `admin_firma`.
- **de ce nu e escaladare:** cheia se creează doar prin `POST /cabinet/api-chei`, care cere `admin_firma`. Un `angajat` nu-și poate face singur o cheie, deci nu se poate ridica singur. E **delegare explicită** de la un admin, nu ocolire. Iar `_api_schema` verifică apartenența firmei la cabinetul cheii, deci izolarea per firmă se păstrează.
- **de ce nu e prag 1, măsurat:** `public.api_chei` = **0**. Nicio cheie n-a fost creată vreodată, deci efectul n-a fost produs. Aceeași încadrare ca R43, pe același criteriu.
- **CE AM GĂSIT ÎN SCHIMB, și era mai grav decât rolul — reparat azi.** Ruta lua **`platitor_tva` din CORPUL CERERII**, cu implicit `True`, în timp ce ruta din ecran îl citește din `firma_profil`. Valoarea intră în `_potriveste_linii` → `cote_tva.potriveste_cota`, deci **decide cota de pe liniile facturii**: un integrator care nu-l trimitea ar fi facturat cu TVA o firmă **neplătitoare**. E interdicția 45 (P20) — o valoare din afară peste un fapt pe care îl știm. Acum se citește din firmă, ca în ecran.
- **a doua diferență, tot reparată:** numele beneficiarului nu era cerut, deși ruta din ecran îl refuză explicit. O factură fără beneficiar nu e factură.
- **ce RĂMÂNE diferit, declarat:** poarta „pleacă marfa acum?” (descărcarea gestiunii) nu se poate pune pe o cale neinteractivă fără să alegem în locul integratorului. E decizie de produs, consemnată, nu diferență tehnică.

### `POST /tenants/{tenant_id}/facturi`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] **nu pot scrie verificarea fără să știu ce o deosebește de `/facturi/emite`.** Creează ciornă? Emite direct? De completat din cod
- dacă emite, se aplică verificările de la `emite`
- **completat din cod (26.08.2026): ce o deosebește de `/facturi/emite`.** `/facturi` cheamă `creeaza_factura(numar, data_emitere, directie, …)` — **numărul vine de la apelant**, iar `directie` poate fi `emisa` sau **`primita`**. E calea prin care se ÎNREGISTREAZĂ o factură care există deja (inclusiv una primită). `/facturi/emite` cheamă `emite_factura(…)` — **aplicația dă numărul din serie**, cere numele beneficiarului, are poarta „pleacă marfa acum?” și citește `platitor_tva` din `firma_profil`. E calea prin care se EMITE una nouă.
- starea implicită diferă, și e chiar **R14**: `creeaza_factura` pune `emisa`, `emite_factura` pune `de_preluat`. Două populații în aceeași firmă, iar starea nu se mai schimbă niciodată
- deci verificarea corectă pentru `/facturi` **nu** e cea de la `emite`: aici numărul e dat de om, deci se verifică **unicitatea în serie** și că nu creează goluri; la `emite` se verifică că numărul vine din serie

### `POST /tenants/{tenant_id}/facturi-recurente`

*garda `cere_context` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [x] șablonul recurent nu emite nimic singur — emiterea trece prin `facturi/emite`, cu regulile ei
- modificarea unui șablon nu atinge facturile deja emise din el
- ștergerea nu atinge facturile emise; dacă șablonul are facturi, se spune câte
- data următoarei emiteri se recalculează la modificare, iar dacă ar cădea în trecut se refuză
- *(verificările sunt scrise de Costin o singura data, pentru toate trei rutele de sablon recurent)*

### `DELETE /tenants/{tenant_id}/facturi-recurente/{sid}`

*garda `cere_context` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [x] șablonul recurent nu emite nimic singur — emiterea trece prin `facturi/emite`, cu regulile ei
- modificarea unui șablon nu atinge facturile deja emise din el
- ștergerea nu atinge facturile emise; dacă șablonul are facturi, se spune câte
- data următoarei emiteri se recalculează la modificare, iar dacă ar cădea în trecut se refuză

### `PUT /tenants/{tenant_id}/facturi-recurente/{sid}`

*garda `cere_context` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [x] șablonul recurent nu emite nimic singur — emiterea trece prin `facturi/emite`, cu regulile ei
- modificarea unui șablon nu atinge facturile deja emise din el
- ștergerea nu atinge facturile emise; dacă șablonul are facturi, se spune câte
- data următoarei emiteri se recalculează la modificare, iar dacă ar cădea în trecut se refuză
- *(verificările sunt scrise de Costin o singura data, pentru toate trei rutele de sablon recurent)*

### `POST /tenants/{tenant_id}/facturi/emite`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `facturi_api`, `stocuri_cv_api`*

- [x] factura primește **următorul număr din serie**, fără goluri; două emiteri simultane nu produc același număr
- exemplarul se îngheață cu amprenta; o regenerare ulterioară produce alt exemplar, nu îl rescrie pe primul
- nota contabilă generată respectă partida dublă, iar conturile vin din mapare, nu din literali
- mișcările de stoc au aceeași dată cu factura
- factura fără cod fiscal de partener se refuză — nu intră în D394 și nu se corelează în VIES

### `PUT /tenants/{tenant_id}/facturi/numerotare`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] schimbarea seriei sau a numărului de start **nu poate produce un număr deja folosit** — se refuză, cu numărul care ar fi intrat în conflict
- numerotarea nu se poate reduce sub ultimul număr emis
- schimbarea se consemnează: cine, când, de la ce la ce. E P15 — seria nu are goluri și nu se reia

### `DELETE /tenants/{tenant_id}/facturi/{factura_id}`

*garda `cere_rol` · rol:admin_firma*

*ce face: [EEE2] Refuzul e EXPLICAT, nu o eroare de bază: `409`, cu numărul notei și cu ieșirea numită (storno) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] **o factură emisă nu se șterge.** Se stornează. Ștergerea ar produce un gol în serie
- o factură cu notă contabilă nu se șterge — se rupe lanțul P14
- dacă ștergerea e permisă pe ciorne, verifică ce o deosebește de o factură emisă; iar dacă nu există distincția, aia e constatarea

### `POST /tenants/{tenant_id}/facturi/{factura_id}/recunoaste`

*garda `cere_rol` · rol:admin_firma*

*ce face: RECUNOAȘTEREA unei facturi EMISE venite prin import — actul care îi scrie nota — scrie facturi (UPDATE)*

- [x] înainte de act, factura adusă prin import stă în starea `de_recunoscut` și **n-are nicio notă** — sosirea documentului nu e faptul economic
- [x] **și totuși e DECLARABILĂ**: apare în D300 pe luna emiterii chiar nerecunoscută, fiindcă TVA-ul e datorat la emitere (art. 281 CF). *Verificarea asta e cea care apără defectul 1.1 din 22.08.2026*
- [x] după act, factura are **exact o notă**, în stare `ciorna`, cu `sursa='facturi'` și cu `factura_id` care trimite la ea — patru-ochi rămâne neatins (R47)
- [x] documentul justificativ derivat din notă numește factura originală, cu numărul și data ei
- [x] factura trece pe `emisa`: după recunoaștere e o factură ca oricare alta
- [x] a doua chemare a actului e **no-op** (`deja_recunoscuta`), nu eroare, și nu adaugă a doua notă
- [x] pe o factură care **n-a venit prin import** actul refuză cu `422` — nu e o ciornă de recunoaștere
- [x] contabilizarea manuală, chemată după recunoaștere, întoarce `deja_contata`: în jurnal rămâne o singură notă
- [x] pe o lună închisă actul refuză cu `423`, iar factura rămâne `de_recunoscut`
- **BIFATE PE RULARE, 29.08.2026 — nu pe citirea codului.** Executate de `scripts/proba_verificari_trasee.py`, ca la pasul de dezlegare. **9 din 9 confirmate.** *Rândul despre declarabilitate se măsoară ca DIFERENȚĂ în D300 (bază +1.000, TVA +210), nu ca total: decontul cumulează și celelalte facturi ale lunii, iar o egalitate pe total ar fi presupus o fixtură izolată.*
- ce NU acoperă lista: actul n-are ecran, deci rândurile se exercită prin API — la fel ca `POST /import-efactura`, calea care aduce documentul (R70).

### `POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: RUTA MANUALĂ de contare — **a doua cale, declarată** (R87, decizia lui Costin 29.08.2026, varianta (ii)+(iii) din AAA4)*

- [x] nota produsă e **ciornă**, nu evidență validată — descrierea o spune, verifică structural
- propunerea de conturi vine din maparea corectată; nu se ghicește din denumire
- ciorna poartă legătura către factura din care a ieșit
- o factură contabilizată de două ori nu produce două note
- **fără rol, deși scrie în `inregistrari`** — R55, iar aici e cea mai vizibilă instanță
- **Măsurat 26.08.2026: nota E ciornă** — verificat pe `INSERT`-ul din corpul rutei, nu pe descriere. Deci nu produce evidență, iar poarta e la validare (`admin_firma` de azi). Din **40** de rute care scriu în `inregistrari_linii` în corpul lor, **36 scriu `ciorna`**; singurele trei care scriau `validata` direct — `amortizare`, `bonuri/{id}/aproba`, `horeca/raport-z` — au primit rol azi.

### `POST /tenants/{tenant_id}/facturi/{factura_id}/email`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`, `firma_profil_api`*

- [x] trimiterea e un **eveniment de predare**: cui, când, la ce adresă, cu ce atașament
- se trimite exemplarul emis, cu amprenta lui — nu o regenerare la momentul trimiterii
- o a doua trimitere e un al doilea eveniment, nu suprascrie primul
- eșecul trimiterii e o stare, nu o eroare pierdută: factura rămâne netrimisă și se vede

### `PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare`

*garda `cere_rol` · rol:admin_firma*

*ce face: F131: supapa per factura — poate atinge, prin modul (PLAFON, nemasurat pe ruta): facturi (UPDATE) · firma_profil (UPDATE) — prin `scadentar`*

- [x] oprirea notificărilor pe o factură nu schimbă scadența și nu afectează calculul de întârziere
- starea se consemnează cu autorul — e o decizie despre relația cu clientul

### `POST /tenants/{tenant_id}/facturi/{factura_id}/storno`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] stornarea e un **document nou**, care o referă pe cea stornată. Factura originală rămâne, cu numărul ei
- suma stornată nu depășește suma facturii
- nota de stornare inversează exact nota originală — nu o șterge
- o factură deja stornată nu se stornează a doua oară

### `POST /tenants/{tenant_id}/facturi/{factura_id}/transforma`

*garda `cere_rol` · rol:admin_firma · scrie in facturi*

*ce face: Transforma proforma/aviz in factura fiscala (numerotare noua, nota se genereaza normal). — scrie facturi (UPDATE) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] proforma sau avizul devine factură fiscală cu **numerotare nouă**, din seria de facturi, nu cu numărul proformei
- documentul original rămâne, cu starea „transformat" și legătura către factura rezultată
- nota contabilă se generează la transformare, nu la emiterea proformei — proforma nu e document contabil

## T03 — Statul de plată și fluturașul

*clasa MECANIC · 8 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/fluturas/{salariat_id}`, `/tenants/{tenant_id}/stat-plata`, `/tenants/{tenant_id}/stat-plata/emis`*

### `POST /tenants/{tenant_id}/salarii-contare/propunere`

*garda `cere_cabinet` · nu scrie nimic*

*ce face: Nota pe care ar scrie-o statul de plata + divergentele fata de D112, cu ambele cifre.*

- [x] propunerea arată **ambele cifre** la fiecare divergență față de D112 — nu doar că există una
- nu scrie nimic; verificat structural
- dacă statul de plată nu e emis pentru luna cerută, se spune, nu se calculează din recalcul

### `POST /tenants/{tenant_id}/salarii-contare`

*garda `cere_cabinet` · scrie nota ciorna a statului de plata*

*ce face: Scrie nota ciorna a statului de plata — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] nota e ciornă, iar totalurile coincid cu propunerea văzută înainte
- divergența față de D112, dacă a existat la propunere, rămâne consemnată pe notă — nu se stinge prin salvare
- o a doua contare pe aceeași lună nu produce a doua notă
- **fără rol** — R55
- **Măsurat: nota e ciornă** (R33 a reparat-o pe 25.08; antetul modulului spune de ce — forma veche scria `validata` direct și *„ocolea patru-ochi”*). Deci „fără rol” aici nu e o gaură spre evidență: e o propunere, iar poarta e la validare.

### `POST /tenants/{tenant_id}/stat-plata/corectie`

*garda `cere_cabinet` · **fara rol***

*ce face: corp: {salariat_id, an, luna} — poate atinge, prin modul (PLAFON, nemasurat pe ruta): state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

- [x] corecția e **al doilea exemplar**, cu referință la primul. Primul rămâne
- diferența față de exemplarul corectat e vizibilă, pe fiecare cifră schimbată
- corecția nu poate atinge o lună închisă fără redeschidere consemnată

### `POST /tenants/{tenant_id}/stat-plata/emite`

*garda `cere_rol` · rol:admin_firma*

*ce face: corp: {an, luna} — poate atinge, prin modul (PLAFON, nemasurat pe ruta): state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

- [x] statul se îngheață cu amprentă, exemplar numerotat, autor, moment
- cifrele emise nu se mai recalculează la citire; un recalcul care diferă produce contradicție vizibilă, nu rescriere
- emiterea e idempotentă: a doua apăsare produce **al doilea exemplar**, nu suprascrie primul
- pontajul trebuie confirmat; fără el, tichetele nu se acordă, iar statul o spune

### `POST /tenants/{tenant_id}/stat-plata/motiv`

*garda `cere_cabinet` · **fara rol***

*ce face: corp: {exemplar_id, motiv} — poate atinge, prin modul (PLAFON, nemasurat pe ruta): state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

- [x] motivul marchează contradicția ca **asumată**, nu o stinge — rândul rămâne în listă, cu motivul, cine și când
- un motiv gol se refuză

## T04 — Concediul medical

*clasa MECANIC · 5 rute · 3 schimba date · 4 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/concedii/coduri`, `/tenants/{tenant_id}/salariati/{salariat_id}/concedii`*

### `POST /tenants/{tenant_id}/calcul-cm`

*garda `cere_cabinet` · **fara rol***

*ce face: corp: {salariat_id, an, luna (luna certificatului), zile_lucratoare_cm, cod?, zile_episod?, prima_zi_din_episod?, spitalizare?, data_certificat?}*

- [x] media zilnică se calculează din veniturile a 6 luni, **din sursă**, nu dintr-un tabel intermediar
- lunile lipsă din bază se numesc, cu numărul lor — nu produc tăcut o medie mai mică
- procentul se determină pe **episod cumulat**, nu pe certificat
- diminuarea cu o zi lucrătoare se aplică o dată pe episod, cu excepția codului 51
- plafonul de 12 salarii minime se verifică la media lunară
- regimul aplicabil e cel de la data certificatului **inițial** al episodului, nu de la data calculului

### `POST /tenants/{tenant_id}/salariati/{salariat_id}/concedii`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] codul de indemnizație e din nomenclatorul oficial; unul din afară se refuză
- pentru codurile care cer CNP-ul persoanei îngrijite — 09, 17, 91, 92 — câmpul e obligatoriu la introducere, nu la generarea D112
- un certificat „în continuare" poartă seria, numărul și data celui inițial; fără ele se refuză
- perioada nu se suprapune cu alt certificat al aceluiași salariat
- stagiul de asigurare e verificat, sau codul e dintre cele exceptate — altfel se semnalează
- durata cumulată pe an nu depășește plafoanele: 183 de zile, 45 pentru codul 09, 45 pentru codul 17

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] **un certificat care a intrat într-un stat de plată emis nu se șterge** — se corectează prin exemplar nou
- ștergerea recalculează episodul: dacă certificatul șters era inițial, procentul celorlalte din episod se schimbă
- ștergerea unui certificat dintr-o lună declarată în D112 produce contradicție vizibilă

## T05 — Nota contabilă — de la document la registrul-jurnal

*clasa MECANIC · 34 rute · 26 schimba date · 19 firme il pot exercita azi*

*citiri (nu schimba nimic): `/api/v1/firme/{tenant_id}/balanta`, `/tenants/{tenant_id}/balanta`, `/tenants/{tenant_id}/documente/balanta`, `/tenants/{tenant_id}/fisa-cont`, `/tenants/{tenant_id}/jurnal`, `/tenants/{tenant_id}/plan-conturi`, `/tenants/{tenant_id}/registru-inventar`, `/tenants/{tenant_id}/registru-inventar/propunere`*

### `POST /tenants/{tenant_id}/jurnal`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [x] nota respectă partida dublă la creare, nu la validare
- conturile există în plan — acum se refuză
- data notei e într-o perioadă deschisă
- documentul justificativ e cerut: felul, numărul, data. Fără el, nota nu se poate desface — P14
- **fără rol** — R55
- **RĂMÂNE fără rol, cu motivul măsurat (26.08.2026).** Citite la sursă, `jurnal_api.editeaza` și `.sterge` refuză orice notă care nu e `ciorna`, iar `creeaza` scrie tot `ciorna`. O ciornă **nu schimbă ce datorează firma** — deci criteriul lui Costin nu o prinde. Poarta e la validare, care de azi cere `admin_firma`.

### `DELETE /tenants/{tenant_id}/jurnal/{nota_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [x] o notă validată nu se șterge — se stornează. Ștergerea ar rupe lanțul către documentul justificativ
- ștergerea unei ciorne nu atinge documentul din care a ieșit
- **fără rol** — R55

### `PUT /tenants/{tenant_id}/jurnal/{nota_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [x] o notă **validată** nu se editează — se stornează
- editarea unei ciorne păstrează partida dublă
- editarea nu poate muta nota într-o perioadă închisă
- **fără rol** — R55

### `POST /tenants/{tenant_id}/jurnal/{nota_id}/dezleaga`

*garda `cere_rol` · rol:admin_firma*

*ce face: RUPE legătura notă↔factură, cu URMĂ*

- [x] nota nu mai poartă `factura_id`, dar **rămâne în evidență** cu aceleași linii și aceeași sumă — actul rupe legătura, nu șterge nota
- [x] factura reapare ca **neîncasată, cu soldul întreg**: `reconciliere_api.facturi_deschise` o listează din nou, cu exact suma care fusese stinsă de nota dezlegată
- [x] actul a lăsat o **urmă proprie** în `public.audit_log` (`DEZLEGARE nota-factura`), cu nota, factura, motivul scris de om, autorul și momentul — și e o afirmație tipată, nu proză într-un dicționar
- [x] fără motiv actul **nu se produce**: răspuns `422` cu `cod=MOTIV_OBLIGATORIU`, iar nota rămâne legată — se citește în bază, nu doar pe ecran
- [x] pe o notă de **CONTARE** actul refuză (`E_NOTA_DE_CONTARE`), trimite la **storno**, iar nota rămâne legată: evidența unei facturi nu se poate desface
- [x] pe o **lună închisă** actul refuză cu `423`, nota rămâne legată, iar în `audit_log` **nu** apare niciun rând `DEZLEGARE nota-factura` — refuzul se produce înaintea urmei. *(Rândul de acces `POST <cale>` apare oricum: middleware-ul îl scrie pentru orice mutație, reușită sau nu.)*
- [x] fără rol de `admin_firma` actul nu se poate exercita
- [x] **după** dezlegare, ștergerea facturii — care înainte refuza cu `ARE_NOTA_LEGATA` — reușește; iar pe o factură cu notă de contare ștergerea refuză și numește storno
- [x] o **a doua** dezlegare pe aceeași notă refuză cu `NOTA_NELEGATA` și nu adaugă un al doilea rând `DEZLEGARE nota-factura`
- **BIFATE PE RULARE, 29.08.2026 — nu pe citirea codului.** Fiecare rând a fost executat ca pas distinct de `scripts/proba_verificari_trasee.py`: schemă efemeră din `tenant_template.sql`, chemarea **funcțiilor de rută** din `main.py` (deci prin verificarea de rol, poarta de perioadă, tranzacție și urmă), cu dovada tipărită. **9 din 9 confirmate.** *A bifa citind codul care le-a produs ar fi fost o tautologie: gardul și afirmația ar fi venit din același loc.*
- ce NU acoperă lista: actul **n-are ecran**, deci toate rândurile se exercită prin API — la fel ca `DELETE /facturi/{id}`, care n-are nici el (R70). O verificare „cu ochii, pe ecran" nu e posibilă azi pentru pasul ăsta.

### `POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [x] validarea verifică **înainte** de a marca: partidă dublă, conturi existente, perioadă deschisă, document justificativ prezent
- nota validată intră în evidență; din acel moment nu se mai editează și nu se șterge
- cine a validat se consemnează
- **fără rol, iar aceasta e ruta care transformă o ciornă în evidență.** E instanța cea mai gravă din cele patru — R55
- **REZOLVAT 26.08.2026, în aceeași tură: ruta cere acum `admin_firma`.** Motivul, al lui Costin: *„validarea unei note e ce transformă o ciornă în evidență”*. Rândul „fără rol” de mai sus descrie starea de dinainte.

### `POST /tenants/{tenant_id}/nota-asociati`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie dividend|regularizare|imprumut, descriere?, + dividend{brut, interimar?, cu_plata?}; regularizare{total_interimar, dividend_anual}; imprumut{suma, f — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] distincția între aport, împrumut și retragere e obligatorie: au tratamente fiscale diferite
- retragerea de bani fără temei e chiar cazul din ghidul „bani din firmă fără temei" — verifică dacă ruta o permite fără să semnaleze
- împrumutul de la asociat poartă dobândă deductibilă limitat; verifică dacă se aplică plafonul
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-avans`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie avans_platit|regularizare_platit|avans_incasat| regularizare_incasat, suma (fara TVA), cota?, destinatie? (platit: stocuri|servicii|imobilizari|imob — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] avansul încasat **nu e venit** — e datorie până la livrare
- TVA-ul se colectează la încasarea avansului, dacă firma e plătitoare
- la livrare, avansul se stinge, iar TVA-ul nu se colectează a doua oară pe partea avansată
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-bacsis`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel incasare|distribuire, suma, sursa card|numerar (incasare) / banca|casa (distribuire), descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] bacșișul are regim fiscal propriu din 2023 — venit al salariatului, cu impozit reținut, fără contribuții
- verifică dacă se distinge de venit al firmei
- bacșișul încasat prin card trece prin casă sau prin bancă — verifică traseul
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-chirie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel comodat|chirie_platita|chirie_incasata|refacturare, descriere?, cota?, + comodat{valoare, moment primire|restituire}; chirie_platita{chirie, proprietar p — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] chiria plătită unei persoane fizice atrage impozit și, uneori, CASS — verifică dacă se rețin
- chiria în valută produce diferențe de curs
- chiria plătită în avans se eșalonează pe perioada acoperită, nu e cheltuială integral
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-contract-special`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel zilier|cenzor|mandat, brut, sursa casa|banca, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] **nu pot scrie verificarea fără să știu ce contract.** De completat din cod
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.
- **completat din cod (26.08.2026), cum ai cerut.** Sunt **contractele de munca speciale**, trei feluri, prin motorul pur `core/contracte_speciale.py`, cu temeiurile citate in antet: **zilieri** (Legea 52/2011) - impozit 10% + CAS 25%, **fara CASS si fara CAM** (art. 9^1), impozit pe (brut - CAS), remuneratia orara minima = salariul minim orar, max 90 zile/an la acelasi beneficiar (120 in agricultura); **cenzori / mandat administrator fara CIM** (art. 76 alin. 2 lit. g/i CF, venituri asimilate salariilor) - CAS 25% + CASS 10% + impozit 10% pe (brut - CAS - CASS), **fara CAM**, fiindca nu exista raport de munca
- deci verificarea de fond: **cele trei feluri nu au aceleasi contributii**, iar daca aplicatia le-ar trata la fel, un zilier ar plati CASS pe care legea nu i-o cere. Se verifica pe cifre, per fel, nu pe existenta notei
- nota difera si ea: zilieri `641.zilieri = 421`; cenzori/mandat `621 = 421`. Contul de cheltuiala spune ce fel de raport e - daca e acelasi, informatia s-a pierdut
- declararea in D112 e obligatorie pentru toate trei; verifica plafonul de zile la zilieri, fiindca depasirea il scoate din regim

### `POST /tenants/{tenant_id}/nota-credit`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie primire|dobanda|plata|restanta|garantie, tip lung|scurt, descriere?, + pe operatie: primire{suma}; dobanda{dobanda}; plata{rata?, dobanda?, comision — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] rambursarea se desface în principal și dobândă; principalul stinge datoria, dobânda e cheltuială
- comisioanele au tratament propriu — verifică dacă se disting
- creditul în valută produce diferențe de curs la fiecare rambursare
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-decont-deplasare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel avans|decont|plafon, descriere?, sursa casa|banca, + avans{suma}; decont{avans, diurna?, transport?, cazare?, cota?}; plafon{diurna_pe_zi, zile, salariu_ — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] diurna neimpozabilă e plafonată; ce depășește e venit asimilat salariilor
- plafonul intern și cel extern sunt diferite, iar cel extern diferă pe țară — verifică dacă se cere din registru
- cheltuielile de transport și cazare sunt separate de diurnă
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-inventariere`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii, mijloace_fixe*

*ce face: corp: {data, operatie plus|plus_mf|minus|casare, descriere?, + plus{valoare, cont_stoc?}; plus_mf{valoare, cont_imobilizare?}; minus{valoare, cont_stoc?, imputabil?, valo — scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · mijloace_fixe (INSERT/UPDATE)*

- [x] plusul de inventar e venit; minusul e cheltuială, deductibilă doar în limita perisabilităților
- minusul imputabil se recuperează de la gestionar — verifică dacă se distinge de cel neimputabil
- nota atinge și `mijloace_fixe`: verifică ce se întâmplă cu un mijloc fix lipsă la inventar
- plusul și minusul se scriu pe conturile lor, iar suma notei se închide — nota nu rămâne dezechilibrată dacă o categorie lipsește
- mijlocul fix constatat lipsă iese din `mijloace_fixe` cu dată și motiv, nu doar din notă
- **stocul NU se ajustează de aici, iar asta e o absență, nu o verificare** — un inventar care nu mișcă stocul lasă evidența cantitativă și cea contabilă să divergeze. Consemnat separat (R64); aici nu se poate verifica, fiindcă ruta n-o face
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul. Verificarea *«mișcările de stoc au aceeași dată cu nota»* rămâne **fără obiect**: ruta nu produce nicio mișcare de stoc. Că o notă de inventariere nu mișcă stocul e o absență care merită întrebată separat — dar nu se mai poate verifica aici. Restul rândurilor, inclusiv cel despre `mijloace_fixe`, stau pe scrierea PROPRIE a rutei și rămân.

### `POST /tenants/{tenant_id}/nota-leasing`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, tip primire|rata|reziduala|operational, descriere?, cota?, + campuri pe tip: primire{valoare_capital, dobanda_totala, cont_imobilizare?}; rata{capital, doban — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] financiar sau operațional — cele două au tratamente contabile opuse. Verifică dacă ruta le distinge, sau presupune unul
- la leasing financiar, bunul intră ca imobilizare și se amortizează; rata se desface în principal și dobândă
- la operațional, rata e cheltuială integral
- dobânda din rată e separată de principal, nu topită în cheltuială
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/nota-lichidare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie vanzare_activ|partaj, descriere?, + vanzare_activ{pret, valoare_bruta, amortizare_cumulata, conturi?, cota?}; partaj{capital_social, rezerve?, profi — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] lichidarea închide conturile; verifică ordinea: se sting datoriile, apoi se distribuie asociaților
- impozitul pe dividende se aplică la distribuirea din lichidare
- verifică dacă ruta permite lichidarea unei firme cu datorii nestinse
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/registru-inventar`

*garda `cere_cabinet` · **fara rol***

*ce face: Inscrie un rand — poate atinge, prin modul (PLAFON, nemasurat pe ruta): registru_inventar (INSERT) — prin `registru_inventar`*

Al treilea dintre registrele obligatorii ale art. 20 din Legea 82/1991. Spre deosebire de jurnal si
de Cartea mare, NU se deriva din `inregistrari`: coloana 4 (valoarea de inventar) vine din numararea
faptica, pe baza listelor de inventariere.

- **coloana 4 nu se completeaza singura din coloana 3**: apasa „Adu soldurile din balanta", du un
  cont in formular si verifica faptul ca valoarea de inventar ramane GOALA. Daca s-ar completa,
  registrul ar iesi cu zero diferente pe toate conturile — o inventariere perfecta care nu s-a facut
- **o diferenta fara cauza e refuzata**: pune valori diferite pe coloanele 3 si 4, lasa cauza goala,
  si citeste refuzul — trebuie sa spuna ca EXISTA o diferenta, nu doar ca lipseste un camp
- **un rand fara diferenta NU cere cauza**: perechea de mai sus; altfel registrul ar fi imposibil de
  completat pe conturile care se potrivesc
- **diferenta se calculeaza, nu se tasteaza**: coloana 5 e, prin norma, coloana 3 minus coloana 4.
  Verifica semnul: contabil 100 / inventar 80 e un MINUS de 20
- **numarul curent curge pe moment**, nu global: doua randuri la sfarsit de exercitiu primesc 1 si 2,
  iar primul rand la incetarea activitatii primeste tot 1
- **registrul gol nu inseamna «totul se potriveste»**: citeste ce scrie pe ecranul gol — trebuie sa
  spuna ca nu s-a inscris nicio inventariere
- **fara rol, desi scrie intr-un registru obligatoriu** — aceeasi absenta ca la celelalte doua
  registre adaugate azi, consemnata ca sa nu treaca drept intentie

### `POST /tenants/{tenant_id}/nota-obiect-inventar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie achizitie|dare_folosinta|scoatere, valoare, cota?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] valoarea e **sub pragul** de mijloc fix la data operațiunii — altfel e imobilizare, nu obiect de inventar
- pragul se cere din registru, pe dată
- darea în folosință e o operațiune distinctă de achiziție — verifică dacă se disting
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-ong`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie venit|scutire, descriere?, + venit{suma, fel cotizatie|contributie|donatie|sponsorizare|financiar| fonduri|ocazional|alte, sursa casa|banca}; scutir — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] activitatea fără scop patrimonial e separată de cea economică — verifică dacă se disting
- veniturile neimpozabile ale ONG au plafon; peste el se impozitează
- verifică dacă se aplică cele două plafoane cumulate
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-perisabilitati`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare_intrari, procent_limita (coef — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] limita legală de perisabilitate e pe categorie de produs; ce depășește e cheltuială nedeductibilă
- verifică dacă limita se cere din registru sau e literal
- perisabilitățile se constată la inventar, nu în orice moment
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/nota-productie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie obtinere|pic|vanzare, descriere?, + obtinere{cost_standard, cost_efectiv?}; pic{suma, moment constatare|reluare}; vanzare{pret_vanzare, cost_standar — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] costul de producție cuprinde materialele, manopera și cota de indirecte — verifică ce cuprinde efectiv
- produsul finit intră în stoc la cost, nu la preț de vânzare
- mișcarea de stoc are aceeași dată cu nota
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-provizion`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel creanta|provizion|stoc, actiune constituire|reluare, suma, descriere?, + creanta{zile_depasire?, garantata?, afiliata?, faliment?} | provizion{tip litigi — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] provizionul deductibil fiscal e limitat prin lege; ce depășește e cheltuială nedeductibilă
- verifică dacă ruta distinge deductibil de nedeductibil, sau lasă totul deductibil
- provizionul se reia când motivul dispare — verifică dacă există calea inversă
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/nota-sgr`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie achizitie|vanzare|restituire|autofactura|virare, descriere?, + nr_ambalaje|suma, sursa casa|banca, + autofactura{garantii_returnate, tarif_gestionar — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] garanția de ambalaje **nu e venit și nu e cheltuială** — e datorie, respectiv creanță
- TVA-ul nu se aplică garanției
- returnarea stinge datoria, nu produce venit
- temeiul e HG 1074/2021, adus în corpus pe 24.08
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-sponsorizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, suma, mod contract|plata, descriere?, + optional pentru calcul credit: cifra_afaceri, impozit_profit, tip_impozit profit|micro, beneficiar_in_registru} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] creditul fiscal e minimul dintre 0,75% din cifra de afaceri și 20% din impozit — verifică dacă se calculează, sau se ia suma integral
- beneficiarul e în Registrul entităților; altfel sponsorizarea nu dă credit fiscal
- sponsorizarea intră în D107 — verifică legătura
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-subventie`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, fel exploatare|investitii|reluare, descriere?, + exploatare/investitii{suma, moment drept|incasare}; reluare{valoare_activ, subventie, amortizare_lunara}}. — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] subvenția pentru investiții se recunoaște la venit **pe măsura amortizării**, nu integral la încasare
- subvenția de exploatare e venit în perioada în care se acoperă cheltuiala
- verifică dacă cele două se disting
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/nota-tva-incasare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, sens incasare|plata, suma_incasata, cota?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] TVA-ul se colectează la **încasare**, nu la facturare — nota se leagă de plată, nu de factură
- firma e în regimul de TVA la încasare la data operațiunii; altfel regimul nu se aplică
- plafonul de aplicare a regimului e verificat pe cifra de afaceri, la data operațiunii
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/plan-conturi`

*garda `cere_context` · **fara rol** · scrie in plan_conturi*

*ce face: scrie plan_conturi (INSERT)*

- [x] contul adăugat respectă structura planului general: clasa, grupa, sintetic de gradul I și II
- un cont care nu există în planul general de conturi se refuză, sau se marchează ca analitic al unui sintetic existent
- un cont duplicat se refuză
- **fără rol, iar aceasta e ruta care poate anula refuzul lui `cont_valid`.** Cine adaugă un cont face să treacă orice notă cu el — R55, prima instanță de rezolvat
- **REZOLVAT 26.08.2026, în aceeași tură: ruta cere acum `admin_firma`.** Observația de mai sus — *cine adaugă un cont face să treacă orice notă cu el* — a fost criteriul, iar Costin a numit-o prima instanță de rezolvat din R55. Rândul „fără rol” de mai sus descrie starea de dinainte și rămâne ca să se vadă ce s-a schimbat.

## T06 — Importul de e-Factura și transmiterea prin SPV

*clasa MANUAL · 7 rute · 4 schimba date · 0 firme il pot exercita azi*

*clasa MANUAL · 7 rute · 4 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi-primite`, `/tenants/{tenant_id}/facturi-primite/{primita_id}/xml`, `/tenants/{tenant_id}/trimiteri-spv`*

### `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge`

*garda `cere_context` · **fara rol** · scrie in efactura_primite, factur, validata*

*ce face: Respinge o factura primita: status=respinsa + motiv — scrie efactura_primite (UPDATE)*

- [x] respingerea poartă motivul, obligatoriu
- ciorna rămâne, cu starea „respinsă" — nu se șterge; e o urmă a ceea ce a sosit

### `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza`

*garda `cere_rol` · rol:admin_firma · scrie in efactura_primite, factur, facturi, validata*

*ce face: FOUR-EYES: omul valideaza ciorna importata de cron -> creeaza cheltuiala (factura primita) + leaga factura_id + status=validata — scrie efactura_primite (UPDATE) · facturi (UPDATE)*

- [x] cine validează e consemnat, și e diferit de cine a importat dacă patru ochi e activ și posibil
- factura creată poartă legătura către ciorna din care a ieșit — lanțul nu se rupe
- valorile confirmate nu mai poartă „grad de certitudine": confirmarea e explicită și consemnată
- dacă a ieșit și o cheltuială, aceasta e legată de factură, nu independentă

### `POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv`

*garda `cere_rol` · rol:admin_firma*

*ce face: Trimite o factura emisa in SPV (F126/F160) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): efactura_trimiteri (INSERT/UPDATE) — prin `efactura_send`*

- [x] rândul poartă starea explicită: în curs / confirmată / respinsă / **nelămurită**
- fără identificator de la autoritate, starea nu e „confirmată"
- o a doua apăsare pe aceeași factură nu produce o a doua trimitere fără avertisment — dublarea la autoritate nu se repară

### `POST /tenants/{tenant_id}/import-efactura`

*garda `cere_cabinet` · **fara rol***

*ce face: Upload XML/ZIP e-Factura*

- [x] fiecare factură din fișier ajunge în `efactura_primite` ca **ciornă**, nu ca factură validată
- valorile preluate poartă **sursa** (e-Factura) și **gradul de certitudine** — nimic nu devine fapt fără confirmare
- ce nu s-a putut citi din XML se numește, nu se ghicește: data, cota, partenerul
- un fișier importat de două ori nu creează ciorne duplicate

## T07 — Extrasul bancar și potrivirea

*clasa MECANIC · 7 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/banca/reconciliere`, `/tenants/{tenant_id}/banca/reconciliere/facturi-deschise`*

### `POST /tenants/{tenant_id}/banca/parse-extras`

*garda `cere_cabinet` · **fara rol***

*ce face: intoarce {nr, tranzactii}*

- [x] **nu scrie nimic** — verificat structural
- fiecare tranzacție din fișier apare în răspuns; cele care nu s-au putut citi se numesc, cu rândul lor
- soldul final din extras = soldul inițial + suma tranzacțiilor. Dacă nu, fișierul e incomplet și se spune
- data valutei și data operațiunii sunt distincte — verifică dacă se citesc amândouă

### `POST /tenants/{tenant_id}/banca/reconciliere/import`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): extras_linii (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `reconciliere_api`*

- [x] fiecare tranzacție importată produce **o singură** linie de extras
- un extras importat de două ori nu dublează liniile — verifică pe numărul extrasului și pe conținut
- liniile importate poartă **sursa** (extras bancar) și gradul de certitudine
- potrivirea automată cu facturi e o **propunere**, nu un fapt: verifică dacă rezultatul e ciornă sau evidență
- soldul contului de bancă după import = soldul din extras

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): extras_linii (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `reconciliere_api`*

- [x] nota produsă respectă partida dublă și folosește conturi existente
- linia de extras trece în starea „contată" și nu se mai poate conta a doua oară
- dacă linia se leagă de o factură, suma nu depășește soldul neîncasat
- data notei e data operațiunii din extras, nu data contării

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora`

*garda `cere_cabinet` · **fara rol** · scrie in extras_linii*

*ce face: scrie extras_linii (UPDATE)*

- [x] ignorarea poartă **motivul** — o linie ignorată fără motiv e o sumă care dispare din reconciliere
- linia rămâne vizibilă în listă, cu starea „ignorată", nu dispare
- soldul de reconciliat include liniile ignorate, sau le exclude explicit — verifică ce face și dacă se vede

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza`

*garda `cere_cabinet` · **fara rol** · scrie in extras_linii*

*ce face: scrie extras_linii (UPDATE)*

- [x] reactivarea unei linii contate anulează nota produsă? Sau doar pe cele ignorate se poate?
- dacă anulează o notă validată, se refuză — se stornează
- reactivarea se consemnează: cine, când
- **completat din cod (26.08.2026).** Ruta readuce o linie de extras din `ignorat` în `nou` — un singur `UPDATE extras_linii SET status='nou' WHERE id=%s AND status='ignorat'`. Dacă linia nu e `ignorat`, **refuză 422** („linia nu e ignorata”). **Nu atinge nicio notă** și nu poate reactiva o linie deja contată
- **ce NU face, și e constatarea:** nu consemnează **cine** și **când** a reactivat. Ignorarea și reactivarea sunt decizii despre ce intră în evidență, iar amândouă sunt reversibile fără urmă. Perechea `ignora`/`reactiveaza` e o stare care se poate plimba oricâte ori, fără istoric
- verificarea care rămâne de exercitat: după reactivare, linia reapare în lista de potrivit cu aceleași sume ca înainte de ignorare — ignorarea nu e o modificare de conținut

## T08 — NIR și recepția

*clasa MECANIC · 2 rute · 1 schimba date · 0 firme il pot exercita azi*

*clasa MECANIC · 2 rute · 1 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/stocuri/nir`*

### `POST /tenants/{tenant_id}/stocuri/nir`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): inregistrari (INSERT) · inregistrari_linii (INSERT) · nir (INSERT) · nir_linii (INSERT) — prin `stocuri_api`*

- [x] NIR-ul primește **număr din serie**, fără goluri
- cantitățile recepționate nu depășesc cantitățile de pe factură — sau diferența e consemnată ca minus la recepție
- adaosul comercial, dacă se aplică, e calculat pe cotă, nu introdus liber
- mișcarea de stoc are aceeași dată cu NIR-ul
- nota contabilă și NIR-ul au aceeași valoare totală
- un NIR pe o factură deja recepționată se refuză, sau produce recepție parțială — verifică ce face

## T09 — Casa și registrul de casă

*clasa MECANIC · 3 rute · 2 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/casa/registru`*

### `POST /tenants/{tenant_id}/casa/operatiuni`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): casa_operatiuni (DELETE/INSERT) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [x] **soldul casei nu poate deveni negativ** — o plată peste sold se refuză
- plafonul de plăți în numerar către o persoană juridică se verifică pe zi și pe operațiune
- plafonul de încasări în numerar de la o persoană se verifică la fel
- operațiunea produce o linie în registrul de casă, cu numărul curent
- data operațiunii e într-o perioadă deschisă

### `DELETE /tenants/{tenant_id}/casa/operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): casa_operatiuni (DELETE/INSERT) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [x] **o operațiune de casă dintr-o zi închisă nu se șterge** — registrul de casă se închide zilnic
- ștergerea recalculează soldul; dacă soldul ar deveni negativ la vreo operațiune ulterioară, se refuză
- numerotarea nu se reia după ștergere — rămâne golul, sau se renumerotează? Verifică și spune care
- dacă operațiunea are notă validată, se refuză
- **completat din cod (26.08.2026): numerotarea casei nu se rupe, fiindcă NU EXISTĂ.** `casa_operatiuni` are coloanele `id, data, tip, categorie, document, partener, cui, suma, inregistrare_id, creat_la` — **niciun număr curent**. Iar `casa.registru_casa()` calculează doar **soldul rulant**, nu un rând numerotat. Deci ștergerea nu poate lăsa un gol într-o serie care nu există
- **ce face ștergerea, verificat:** `casa_api.sterge` șterge operațiunea **și nota legată**, dar **doar dacă nota e ciornă** — pe una validată refuză cu *„nota legată e validată; nu se mai poate șterge”*. Deci lanțul către evidență nu se rupe
- **constatarea de fond:** Registrul de casă (cod 14-4-7A, OMFP 2634/2015) e un registru obligatoriu, iar registrele obligatorii poartă număr curent — la fel ca Registrul-jurnal 14-1-1, unde numărul curent a fost **derivat la citire** pe 24.08 după confruntarea cu norma. **N-am confruntat cu actul** dacă 14-4-7A îl cere; dacă îl cere, e aceeași clasă și aceeași reparație
- verificarea care rămâne: după ștergere, soldul rulant al zilei se recalculează, iar soldul de la sfârșitul zilei nu depășește plafonul de casierie

## T10 — Inventarierea

*clasa MECANIC · 5 rute · 1 schimba date · ? firme il pot exercita azi*

*clasa MECANIC · 5 rute · 1 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/d406-active`, `/tenants/{tenant_id}/d406-stocuri`, `/tenants/{tenant_id}/rip/inventar/{an}`, `/tenants/{tenant_id}/verificare-stocuri`*

### `POST /tenants/{tenant_id}/stocuri/inventar`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [x] inventarul compară **stocul faptic** cu cel scriptic; diferența e plus sau minus, nu se ajustează tăcut
- fiecare diferență produce o mișcare de stoc, iar suma mișcărilor = diferența totală
- minusul se compară cu limita de perisabilitate pe categorie; ce depășește e nedeductibil
- inventarul se face la o dată, iar mișcările de după acea dată nu-l afectează
- un articol care nu apare în listă rămâne cu stocul scriptic sau se consideră zero? Verifică — diferența e mare

## T11 — Închiderea lunii

*clasa MECANIC · 7 rute · 4 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi/perioada`, `/tenants/{tenant_id}/perioade-blocate`*

### `POST /tenants/{tenant_id}/facturi/perioada/confirma`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Declara luna INCHISA pe facturi: evidenta ei devine autoritativa, iar semaforul se poate sprijini pe ea cand spune ca o declaratie nu se datoreaza*

- [x] **nu pot scrie verificarea fără să știu ce o deosebește de `POST /perioade-blocate`.** Sunt două acte de închidere pe aceeași tabelă? De completat din cod
- dacă e închiderea pe domeniul facturi, verifică ce se întâmplă când unul e închis și celălalt nu — o perioadă parțial închisă e o stare sau o inconsistență?
- **completat din cod (26.08.2026): NU e duplicat cu `perioade-blocate` — sunt obiecte diferite, iar grija ta era exact cea potrivită.** `facturi/perioada/confirma` cheamă `inchidere_luna.confirma`, care scrie în `perioada`, pe domeniul `facturi`: e o **AFIRMAȚIE** despre completitudine, pe care se sprijină semaforul când spune că o declarație nu se datorează. **Nu oprește nicio scriere.** `perioade-blocate` e **poarta** — o citește `_cere_luna_deschisa` la fiecare notă
- **și da, una putea ocoli verificările celeilalte** — până azi. `confirma` refuza motivat pe e-Facturi neînregistrate; `perioade-blocate` nu verifica nimic. **R58 a mutat verificarea pe poartă**: închiderea cheamă acum `inchidere_luna.blocaj`, plus refuză pe ciorne nevalidate
- verificarea care rămâne: după confirmare, `stare()` întoarce `confirmat=True` cu autorul și momentul, iar o **modificare de facturi de-confirmă automat** (`facturi_api` cheamă `perioada.deconfirma`) — o confirmare care supraviețuiește unei modificări ar spune „complet” despre alte date

### `POST /tenants/{tenant_id}/facturi/perioada/redeschide`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Redeschide luna (o corectie de facturi cere redeschiderea)*

- [x] redeschiderea poartă **motiv obligatoriu** — P15
- urma închiderii nu se șterge: cine a închis, când, rămân. E interdicția 36
- documentele emise din perioada redeschisă se marchează sub rezervă
- verifică relația cu `DELETE /perioade-blocate`: dacă cele două redeschid același lucru pe căi diferite, una poate ocoli verificările celeilalte

### `DELETE /tenants/{tenant_id}/perioade-blocate`

*garda `cere_rol` · rol:admin_firma · scrie in perioade_blocate*

*ce face: scrie perioade_blocate (DELETE) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): perioade_inchideri (INSERT) — prin `migrare_inchideri`*

- [x] redeschiderea e act consemnat, cu **motiv obligatoriu** — P15
- redeschiderea marchează documentele emise din acea perioadă ca fiind **sub rezervă**
- declarațiile depuse pentru perioada redeschisă produc contradicție vizibilă, nu se rescriu
- o perioadă nu se poate redeschide dacă cea următoare e închisă
- **redeschiderea nu consemnează nimic** — vezi pasul de închidere. `DELETE` șterge rândul, deci nu rămâne nici cine a redeschis, nici când, nici de ce. Interdicția 36 + P15
- verificarea care ar trebui să fie adevărată după pas — și azi nu poate fi: **există o urmă care spune că perioada a fost închisă de X la momentul T și redeschisă de Y la momentul U, cu motivul Z**

### `POST /tenants/{tenant_id}/perioade-blocate`

*garda `cere_rol` · rol:admin_firma · scrie in perioade_blocate*

*ce face: scrie perioade_blocate (INSERT) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): perioade_inchideri (INSERT) — prin `migrare_inchideri`*

- [x] închiderea e un act deliberat, cu **autor și moment** consemnate
- după închidere, nicio scriere în perioada aceea nu mai trece — verificat pe toate cele 39 de operațiuni, nu doar pe cele testate
- închiderea verifică întâi că perioada e coerentă: balanța se închide, notele sunt validate, nu există ciorne. Sau, dacă nu verifică, se spune ce nu verifică
- o perioadă nu se poate închide dacă cea anterioară e deschisă
- **verificat la sursă (26.08.2026): NU verifică nimic. Ai presupus corect, și e mai rău.** `POST /perioade-blocate` face **un singur `INSERT`** în `perioade_blocate (an, luna, blocat_de)`. Nicio verificare de ciorne rămase, de echilibru, de orfani. **Măsurat azi: dacă s-ar închide luna curentă pe `tenant_013`, ar rămâne 5 ciorne închise înăuntru** (`tenant_003`: 1)
- **și sunt DOUĂ acte de închidere, dintre care doar unul verifică.** `core/inchidere_luna.py` (21.08) verifică un blocaj real — e-Facturi primite și neînregistrate — și **refuză motivat**, iar o modificare **de-confirmă automat**. Dar el scrie în `perioada`, pe domeniul `facturi`: e o **afirmație** despre completitudine. **Poarta care oprește scrierile e `perioade_blocate`** (citită de `_cere_luna_deschisa` la fiecare notă) — și aceea nu verifică nimic. **Verificarea există, dar nu e pe poartă.**
- **redeschiderea nu lasă urmă.** `DELETE /perioade-blocate` **șterge rândul**: dispare și `blocat_de`, și `blocat_la`, și faptul că perioada a fost vreodată închisă. Tabela n-are coloană de motiv. Asta e **interdicția 36** („o redeschidere de perioadă fără motiv consemnat”) și **P15** („redeschiderea e act consemnat, cu motiv”) — direct, nu prin analogie
- **cifra care încadrează:** o singură perioadă e blocată azi, pe toate cele 17 firme (`tenant_001`). Deci efectul n-a fost produs — e prag 2, cauză unică, dovedită

## T12 — Închiderea anului și situațiile financiare

*clasa MECANIC · 5 rute · 2 schimba date · ? firme il pot exercita azi*

*clasa PARTIAL · 4 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/s1003-xml`, `/tenants/{tenant_id}/s1005-xml`*

### `POST /tenants/{tenant_id}/s1003-valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): artefacte_produse (INSERT) — prin `artefacte`*

- [x] aceleași ca mai sus
- **plus:** un artefact produs pe regimul greșit e conform ca formă și fals ca fond. Ruta refuză, sau spune că nu poate verifica regimul

### `POST /tenants/{tenant_id}/s1005-valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): artefacte_produse (INSERT) — prin `artefacte`*

- [x] artefactul se păstrează cu: conținutul, momentul, autorul, amprenta, numărul exemplarului
- verdictul validării se păstrează cu artefactul, nu separat
- **verificare de fond:** situațiile financiare cerute depind de categoria de mărime a firmei. Dacă aceasta nu există ca dimensiune, ruta nu poate ști ce datorează firma — se declară, nu se presupune

## T13 — Trecerea de regim fiscal

*clasa MECANIC · 8 rute · 4 schimba date · 19 firme il pot exercita azi*

*citiri (nu schimba nimic): `/migrare/vector`, `/tenants/{tenant_id}/firma-profil`, `/tenants/{tenant_id}/firma-profil/date`, `/tenants/{tenant_id}/vector`*

### `POST /tenants/{tenant_id}/firma-profil/date`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): firma_profil (UPDATE) — prin `firma_profil_api`*

- [x] **datele fiscale de aici intră în declarații** — CUI, denumire, adresă, capital. O modificare fără rol schimbă ce se depune
- CUI-ul modificat: verifică dacă e permis deloc. Un CUI schimbat pe o firmă cu declarații depuse rupe corespondența cu tot ce s-a depus
- modificarea se consemnează: cine, când, de la ce la ce
- **poziție, nu notă:** ruta cere rol pe regim-tva și nu pe datele care ajung în același loc
- **MASURAT 26.08.2026, la cererea ta: da, datele intra in declaratii — si e mai mult decat pare.** `firma_profil_api.OBLIGATORII` mapeaza fiecare camp la declaratiile care il cer: `cui` -> **8 declaratii** (D100, D101, D205, D300, D301, D390, D394, D406) · `declarant_nume` si `declarant_functie` -> **9 fiecare** (cele de mai sus + D112 + Bilant) · `nume` -> 7 · `caen` -> 3 · `adresa` -> 3 · `banca` si `iban` -> 2 · `telefon` -> D394 · `reg_com` -> Bilant
- **deci o ruta fara niciun rol scrie campurile pe care se sprijina noua declaratii**, alaturi de `regim-tva`, care cere `admin_firma`. Criteriul tau de la R55 — *ce schimba ce datoreaza firma* — o prinde; criteriul MECANIC al gardului (scrie `validata`) nu, fiindca ruta scrie in `firma_profil`. **Punct orb al gardului, numit**
- ce face ruta corect: refuza un camp obligatoriu golit, cu mesaj care **numeste declaratiile** care nu se mai pot depune fara el; iar `cont_venit_implicit` se refuza daca nu e clasa 70
- *(antetul din lot spune `PUT`; ruta reala e `POST`)*

### `POST /tenants/{tenant_id}/firma-profil/model`

*garda `cere_context` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): firma_profil (UPDATE) — prin `firma_profil_api`*

- [x] **nu pot scrie verificarea fără să știu ce e „model".** Model de firmă? De document? De contare? De completat din cod
- **completat din cod (26.08.2026): „model” e MODELUL VIZUAL AL FACTURII** — `font`, `culoare`, `logo`, prin `firma_profil_api.salveaza_model`. Nu e model de date si nu e regim fiscal: e aspectul PDF-ului predat clientului. De aceea e pe `cere_context` — o preferinta de prezentare, nu o decizie despre ce datoreaza firma
- verificarea care ramane: schimbarea modelului **nu atinge facturile deja emise** — acelea sunt exemplare inghetate cu amprenta (P4); o regenerare cu alt logo ar produce **alt** document
- *(antetul din lot spune `PUT`; ruta reala e `POST` — notat, nu corectat in tacere)*

### `POST /tenants/{tenant_id}/firma-profil/regim-tva`

*garda `cere_context` · **fara rol** · scrie in firma_profil*

*ce face: scrie firma_profil (UPDATE) — prin `firma_profil_api`*

- [x] schimbarea regimului are **dată de la care se aplică**, nu se aplică retroactiv tăcut
- perioadele închise sub regimul vechi rămân sub el — recalcularea lor produce contradicție, nu rescriere
- trecerea de la plătitor la neplătitor cere ajustarea TVA la bunuri de capital; verifică dacă se semnalează
- declarațiile datorate se recalculează din noul regim, iar cele generate sub cel vechi se marchează

### `POST /tenants/{tenant_id}/vector`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): firma_profil (INSERT/UPDATE) · migrare_status (INSERT) — prin `firma_profil_api`, `migrare_api`, `vector_fiscal_api`*

- [x] vectorul decide ce declarații datorează firma — o schimbare produce declarații noi datorate și altele care nu mai sunt
- schimbarea are dată de la care se aplică; perioadele anterioare rămân sub vectorul vechi
- o declarație deja generată pentru o poziție scoasă din vector se marchează, nu dispare
- vectorul se confruntă cu faptele: dacă firma are operațiuni intracomunitare și vectorul nu are D390, se semnalează — e chiar cazul de la 006

## T14 — Preluarea unei firme

*clasa MECANIC · 32 rute · 21 schimba date · 5 firme il pot exercita azi*

*citiri (nu schimba nimic): `/migrare/asociati`, `/migrare/istoric-declaratii`, `/migrare/mijloace-fixe`, `/migrare/parteneri`, `/migrare/plan-conturi`, `/migrare/salariati`, `/migrare/solduri`, `/migrare/status`, `/migrare/straturi`, `/tenants/{tenant_id}/parteneri`, `/tenants/{tenant_id}/solduri`*

### `POST /control-fiscal/{tenant_id}/audit-preluare`

*garda `cere_rol` · rol:admin_firma*

*ce face: F183: audit de PRELUARE firma — coerenta INTERNA a pachetului preluat de la contabilul anterior (balanta echilibrata, defalcare parteneri vs sintetic, solduri fiscale vs  — poate atinge, prin modul (PLAFON, nemasurat pe ruta): artefacte_produse (INSERT) — prin `artefacte`*

- [x] auditul spune ce a găsit **și pe ce s-a uitat** — o firmă preluată fără evidență completă nu primește verdict favorabil, primește „nu pot verifica" cu lista domeniilor
- fiecare constatare poartă domeniul și perioada la care se referă
- absența unei categorii de date nu se convertește în „conform" — e P6

### `POST /migrare/fisier`

*garda `cere_cabinet` · **fara rol***

*ce face: Primește un CSV/XLSX, extrage CUI-urile și le validează la ANAF.*

- [x] numărul de CUI-uri extrase = numărul de rânduri din fișier, minus cele nevalide, iar nevalidele sunt numite cu rândul lor
- un CUI care nu trece cifra de control se semnalează la extragere, nu la interogare

### `POST /migrare/importa`

*garda `cere_rol` · rol:admin_firma*

*ce face: Creează câte un tenant pentru fiecare firmă selectată — poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firma_profil (INSERT/UPDATE) · migrare_status (INSERT) · tenants (INSERT/UPDATE) · user_tenants (INSERT) — prin `migrare_api`, `tenant_provisioning`*

- [x] fiecare firmă selectată primește **schemă proprie**, iar `tenants` are rândul ei — o firmă fără schemă e o afirmație falsă despre lume
- `user_tenants` leagă firma de cabinetul care a importat-o
- o firmă importată de două ori nu creează două scheme
- dacă crearea schemei eșuează, rândul din `tenants` nu rămâne — sau, dacă rămâne, e marcat incomplet

### `POST /migrare/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Primește un fișier (.csv/.xlsx), extrage CUI-urile și le validează la ANAF.*

- [x] ce se vede la previzualizare e ce se importă la pasul următor — aceleași reguli, același rezultat

### `POST /migrare/status`

*garda `cere_rol` · rol:admin_firma*

*ce face: Marchează un strat 'gata' sau 'in_lucru' (cu notă obligatorie la in_lucru). — poate atinge, prin modul (PLAFON, nemasurat pe ruta): migrare_status (INSERT) — prin `migrare_api`*

- [x] trecerea în „in_lucru" cere notă, cum spune ruta — verifică că o refuză fără ea
- starea poartă cine a marcat-o și când

### `POST /migrare/valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: Verifică o listă de CUI-uri la ANAF; întoarce denumirea + status.*

- [x] fiecare CUI primește un răspuns explicit: găsit / negăsit / **nu s-a putut verifica**
- „nu s-a putut verifica" nu se convertește în „negăsit" — sunt stări diferite
- răspunsul de la ANAF se păstrează cu momentul, altfel se reinterogează la fiecare pas

### `POST /tenants/{tenant_id}/articole-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT) · miscari_stoc (INSERT) — prin `articole_import_api`*

- [x] ce s-a văzut la previzualizare e ce s-a importat — același număr, aceleași articole
- articolele cu cod duplicat în fișier se semnalează, nu se suprascriu între ele
- fiecare articol importat cu stoc inițial produce o mișcare de stoc, iar suma mișcărilor = stocul declarat
- un import repetat cu același fișier nu dublează nici articolele, nici mișcările

### `POST /tenants/{tenant_id}/articole-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT) · miscari_stoc (INSERT) — prin `articole_import_api`*

- [x] **previzualizarea scrie în stoc?** Dacă `articole` și `miscari_stoc` se scriu la încărcare, nu e previzualizare — e import. Verifică și spune care e
- articolele cu cod duplicat în fișier se semnalează, nu se suprascriu între ele

### `POST /tenants/{tenant_id}/asociati-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): asociati (DELETE/INSERT) — prin `asociati_import_api`*

- [x] `DELETE/INSERT` — verifică ce se întâmplă cu asociații care nu mai sunt în fișier: se șterg, iar aia e o schimbare de structură a firmei, nu un import

### `POST /tenants/{tenant_id}/asociati-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): asociati (DELETE/INSERT) · migrare_status (INSERT) — prin `asociati_import_api`, `migrare_api`*

- [x] previzualizarea nu salvează
- suma procentelor de participare = 100, sau se semnalează

### `POST /tenants/{tenant_id}/mijloace-fixe-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): mijloace_fixe (DELETE/INSERT) — prin `mijloace_fixe_import_api`*

- [x] ce s-a văzut la previzualizare e ce s-a importat
- amortizarea cumulată la data preluării nu depășește valoarea de intrare
- un mijloc fix complet amortizat intră cu valoare rămasă zero, nu se respinge

### `POST /tenants/{tenant_id}/mijloace-fixe-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): migrare_status (INSERT) · mijloace_fixe (DELETE/INSERT) — prin `migrare_api`, `mijloace_fixe_import_api`*

- [x] **nu scrie nimic** — verificat structural, nu prin absența efectului
- durata de amortizare a fiecărui mijloc fix e confruntată cu catalogul; cele din afara intervalului se numesc, cu rândul lor
- valoarea de intrare sub pragul de mijloc fix se semnalează — e obiect de inventar, nu mijloc fix

### `POST /tenants/{tenant_id}/parteneri`

*garda `cere_rol` · rol:admin_firma*

*ce face: Salveaza soldurile partenerilor unei firme (inlocuieste ce era). — poate atinge, prin modul (PLAFON, nemasurat pe ruta): solduri_parteneri (DELETE/INSERT) — prin `solduri_parteneri_api`*

- [x] ce s-a văzut la previzualizare e ce s-a salvat
- divergența față de balanță, dacă a existat, rămâne vizibilă după salvare — nu se stinge prin acceptare

### `POST /tenants/{tenant_id}/parteneri/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parseaza fisierul de parteneri si intoarce preview + verificare coerenta vs balanta. — poate atinge, prin modul (PLAFON, nemasurat pe ruta): migrare_status (INSERT) · solduri_parteneri (DELETE/INSERT) — prin `migrare_api`, `solduri_parteneri_api`*

- [x] verificarea de coerență față de balanță: suma soldurilor partenerilor = soldul contului corespondent. Diferența se arată cu **ambele cifre**, nu ca „există o divergență"
- un partener fără cod fiscal se semnalează la încărcare — nu intră în D394 și nu se corelează în VIES

### `POST /tenants/{tenant_id}/retete-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: intoarce ce da `retete_import_api.importa()`*

- [x] ce s-a văzut la previzualizare e ce s-a importat
- **nu pot scrie mai mult fără să știu ce scrie `importa()`** — ruta întoarce ce dă funcția, iar funcția nu e descrisă. De completat din cod
- **completat din cod (26.08.2026), cum ai cerut** — `retete_import_api.importa()` creeaza prin `retete_api.salveaza` DOAR retetele marcate `valid`, si sare peste restul; intoarce `{create, sarite}`, unde fiecare sarita e un OBIECT de refuz (`respinge(...)`), nu o fraza
- conservarea numarului: `create + len(sarite)` = numarul de retete din previzualizare — nicio reteta nu dispare tacut
- o reteta a carei denumire exista deja (potrivire pe `lower(denumire)`) NU se suprascrie si NU se dubleaza: se sare, cu motivul `deja_exista`
- fiecare reteta creata poarta pretul si liniile ei (`articol_id`, `cantitate`); o reteta fara linii valide nu se creeaza

### `POST /tenants/{tenant_id}/retete-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: intoarce {retete, rezumat}*

- [x] previzualizare pură: nu scrie nimic, verificat structural
- `rezumat` numește ce nu s-a putut citi, nu doar câte s-au citit

### `POST /tenants/{tenant_id}/rip-import/incarca`

*garda `cere_rol` · rol:admin_firma*

*ce face: Import registru incasari-plati la preluarea unui PFA — poate atinge, prin modul (PLAFON, nemasurat pe ruta): migrare_status (INSERT) · rip_operatiuni (INSERT) — prin `migrare_api`, `rip_migrare_api`*

- [x] **nu pot scrie verificarea fără să știu ce e RIP.** Registrul de inventar și producție? Registrul imobilizărilor? De completat din cod, ca la `retete-import`
- **completat din cod (26.08.2026), cum ai cerut** — **RIP = Registrul de Încasări și Plăți** (partidă simplă, PFA). `core/rip_migrare_api.py`: partida simplă **nu are balanță de deschidere**; registrul e CRONOLOGIC, deci la preluare se importă operațiunile anului curent de la 1 ianuarie până la data preluării, iar soldul e implicit din sumă, nu un rând
- operațiunile importate intră cu `status='validata'` — sunt istoric preluat, nu ciornă de verificat. Verificarea care contează: **preluarea nu certifică** corectitudinea contabilului anterior, iar limita e declarată în antetul modulului
- sumele se citesc cu parserul din `solduri_api` (paranteze = negativ, format contabil RO/EN, sufixe RON/lei) — un singur loc pentru interpretarea sumelor
- numărul de operațiuni importate = numărul de linii din fișier minus cele respinse, iar respinsele sunt numite cu rândul lor

### `POST /tenants/{tenant_id}/salariati-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: Importa salariatii cu CNP valid (upsert pe CNP) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): salariati (INSERT) — prin `salariati_import_api`*

- [x] upsert-ul nu suprascrie date existente fără să spună ce a schimbat
- un salariat existent cu alt nume la același CNP e o divergență, nu o actualizare tăcută

### `POST /tenants/{tenant_id}/salariati-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parseaza exportul de salariati si intoarce preview cu validare CNP (nu salveaza). — poate atinge, prin modul (PLAFON, nemasurat pe ruta): migrare_status (INSERT) · salariati (INSERT) — prin `migrare_api`, `salariati_import_api`*

- [x] **previzualizarea nu salvează** — aceeași verificare structurală ca la solduri
- CNP-urile nevalide se numesc, cu rândul lor din fișier
- un CNP valid dar implauzibil ca dată de naștere se semnalează separat

### `POST /tenants/{tenant_id}/solduri`

*garda `cere_rol` · rol:admin_firma*

*ce face: Salvează soldurile inițiale ale unei firme (înlocuiește ce era). — poate atinge, prin modul (PLAFON, nemasurat pe ruta): plan_conturi (INSERT) · solduri_initiale (DELETE/INSERT) — prin `solduri_api`*

- [x] ce s-a văzut la previzualizare e ce s-a salvat
- „înlocuiește ce era" — verifică ce se întâmplă cu soldurile anterioare: se șterg, sau se păstrează ca versiune?
- conturile din balanță care nu există în plan se creează sau se semnalează — nu se ignoră

### `POST /tenants/{tenant_id}/solduri/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parsează o balanță și întoarce preview (nu salvează). — poate atinge, prin modul (PLAFON, nemasurat pe ruta): migrare_status (INSERT) · plan_conturi (INSERT) · solduri_initiale (DELETE/INSERT) — prin `migrare_api`, `solduri_api`*

- [x] **previzualizarea nu salvează** — ruta spune că întoarce preview; verifică structural că nu scrie în `solduri_initiale`
- dacă totuși scrie (numele tabelelor sugerează că da), atunci previzualizarea nu e previzualizare, iar aia e o constatare
- balanța încărcată **se închide**: total debit = total credit. Dacă nu, se spune, nu se salvează tăcut

## T15 — Salariatul — angajare, contract, adeverință, REGES

*clasa MANUAL · 17 rute · 12 schimba date · 8 firme il pot exercita azi*

*citiri (nu schimba nimic): `/contracte/marcaje`, `/cor`, `/tenants/{tenant_id}/contracte/sabloane`, `/tenants/{tenant_id}/salariati`, `/tenants/{tenant_id}/salariati/{salariat_id}`*

### `POST /tenants/{tenant_id}/contracte/genereaza`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

- [x] contractul generat se păstrează cu momentul, autorul, amprenta, numărul exemplarului
- toate marcajele din șablon sunt înlocuite; unul rămas necompletat oprește generarea, nu produce un contract cu paranteze
- datele din contract coincid cu fișa salariatului la data generării, nu cu cea de azi

### `POST /tenants/{tenant_id}/contracte/sabloane`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

- [x] șablonul salvat conține marcajele declarate; unul necunoscut se semnalează la salvare, nu la generare
- un șablon cu același nume nu se suprascrie tăcut

### `DELETE /tenants/{tenant_id}/contracte/sabloane/{sid}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

- [x] ștergerea unui șablon nu atinge contractele generate din el — acelea sunt documente emise
- dacă șablonul e folosit de contracte existente, se spune câte

### `POST /tenants/{tenant_id}/prapastie-salariu`

*garda `cere_cabinet` · **fara rol***

*ce face: intoarce ce da `_pr.prapastie()`*

- [x] răspunsul conține **ambele cifre** — netul la salariul actual și netul la cel propus — plus diferența, nu doar „se pierde facilitatea"
- pragul de la care netul revine la nivelul actual e calculat, nu aproximat
- cifrele sunt calculate cu toate elementele salariatului: persoane în întreținere, tip de contract, normă
- dacă vreun element lipsește și cifra n-ar fi exactă, se spune — nu se dă o cifră parțială ca exactă

### `POST /tenants/{tenant_id}/reges-config`

*garda `cere_cabinet` · **fara rol** · scrie in reges_chei*

*ce face: corp: {username, parola, mediu test|prod} — scrie reges_chei (INSERT)*

- [x] **cheile nu se întorc niciodată în răspuns**, nici mascate, nici parțial
- o cheie salvată e verificată că funcționează, sau se spune că n-a fost verificată
- suprascrierea unei chei existente e consemnată: cine, când

### `POST /tenants/{tenant_id}/reges-poll`

*garda `cere_cabinet` · **fara rol** · scrie in reges_mesaje*

*ce face: Citeste+consuma un mesaj din coada REGES; salveaza referintele in reges_mesaje. — scrie reges_mesaje (UPDATE)*

- [x] răspunsul de la REGES se păstrează cu momentul, nu doar starea derivată din el
- o trimitere fără răspuns după un interval rămâne „nelămurită", nu trece în „confirmată" prin lipsă de veste
- polling-ul nu schimbă starea unei trimiteri deja confirmate

### `POST /tenants/{tenant_id}/reges-trimite-salariat`

*garda `cere_rol` · rol:admin_firma · scrie in reges_mesaje*

*ce face: corp: {salariat_id, adresa, contract {numar, data_contract, data_inceput, salariu, cor, ...}?} — scrie reges_mesaje (INSERT)*

- [x] starea trimiterii e explicită: în curs / confirmată / respinsă / **nelămurită**
- fără identificator de la REGES, starea nu e „confirmată"
- o a doua trimitere pentru același salariat și aceeași modificare nu se face fără avertisment
- ce s-a trimis se păstrează, nu doar că s-a trimis — la o neconcordanță, contează conținutul

### `POST /tenants/{tenant_id}/salariati`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] CNP-ul trece cifra de control; unul care nu trece se refuză cu motivul, nu se salvează
- un CNP care există deja în firmă se refuză — nu se creează al doilea salariat cu același CNP
- data angajării nu e în viitor față de perioada deschisă
- salariul de bază nu e sub minimul aplicabil la data angajării, proratat cu norma. Dacă e, se refuză cu cifra minimului

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] **un salariat cu stat de plată emis nu se șterge.** Se marchează încetat, cu data. Ștergerea ar rupe lanțul către documentele emise
- dacă ștergerea e permisă, verifică ce rămâne în urmă: fluturași, note contabile, rânduri în D112 deja depuse
- încetarea se propagă în REGES — sau, dacă nu, se spune

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] o modificare de salariu produce **istoric**, nu suprascriere: valoarea veche rămâne, cu perioada în care a fost valabilă
- modificarea nu atinge lunile pentru care s-a emis deja stat de plată — sau, dacă le atinge, produce contradicție vizibilă
- schimbarea normei recalculează pragul minim; dacă noul salariu cade sub el, se refuză

### `POST /tenants/{tenant_id}/salariati/{salariat_id}/adeverinta`

*garda `cere_rol` · rol:admin_firma*

*ce face: F136: adeverinta de salariat (art*

- [x] adeverința se păstrează: conținutul, momentul, autorul, amprenta, numărul exemplarului
- cifrele din adeverință coincid cu statele de plată emise pentru perioada acoperită — nu se recalculează la emitere
- dacă o lună din perioadă n-are stat emis, adeverința spune asta, nu o completează din recalcul

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: [F133 Faza 2a] beneficiu one-off pe luna (vacanta/cadou/cultural) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): beneficii_lunare (DELETE/INSERT) — prin `beneficii_api`*

- [x] beneficiul intră cu perioada lui, nu cu „de acum înainte"
- plafonul neimpozabil aplicabil e cel de la data lunii, nu de la data introducerii
- ce depășește plafonul devine venit impozabil, iar partea impozabilă e vizibilă separat — nu se topește în brut

## T16 — Pontajul

*clasa MECANIC · 4 rute · 2 schimba date · 0 firme il pot exercita azi*

*clasa MECANIC · 4 rute · 2 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/salariati/{salariat_id}/pontaj`, `/util/zile-lucratoare`*

### `POST /tenants/{tenant_id}/pontaj/confirma`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Confirma pontajul lunii -> devine AUTORITATIV pentru salarizare (tichete pe zile efectiv lucrate)*

- [x] confirmarea e ce **deblochează tichetele** — fără ea, statul nu le acordă. Verifică că blocajul e real, nu doar semnalat
- confirmarea poartă autorul și momentul
- după confirmare, pontajul nu se mai modifică fără o operațiune de deconfirmare consemnată
- confirmarea verifică întâi coerența: toți salariații activi au pontaj, sau se spune cine lipsește

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/pontaj`

*garda `cere_context` · **fara rol***

*ce face: F135: seteaza starea unei zile (stare goala/prezent = sterge exceptia). — poate atinge, prin modul (PLAFON, nemasurat pe ruta): pontaj (DELETE/INSERT) — prin `pontaj`*

- [x] zilele pontate nu depășesc zilele lucrătoare din lună
- pontajul nu se poate modifica pentru o lună cu stat de plată emis — sau, dacă se poate, produce contradicție vizibilă
- concediile medicale și cele de odihnă se scad din zilele lucrate, nu se adună separat
- pontajul unei luni închise se refuză

## T17 — Plata salariilor — fișierul către bancă

*clasa MECANIC · 2 rute · 1 schimba date · ? firme il pot exercita azi*

*clasa PARTIAL · 2 rute · 1 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/plata-salarii-preview`*

### `POST /tenants/{tenant_id}/plata-salarii-fisier`

*garda `cere_rol` · rol:admin_firma*

*ce face: [F134] Fisierul SEPA/ISO 20022 pain.001.001.03 de plata a salariilor NET pe card (download) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): artefacte_produse (INSERT) — prin `artefacte`*

- [x] fișierul se păstrează: conținutul, momentul, autorul, amprenta, numărul exemplarului
- sumele din fișier coincid cu **netul din statul de plată emis** — nu se recalculează la generare
- fiecare salariat din fișier are IBAN valid; cei fără IBAN se numesc, iar fișierul nu se generează parțial fără să spună
- totalul fișierului = suma neturilor, verificat explicit
- un fișier generat de două ori pentru aceeași lună produce al doilea exemplar, nu suprascrie primul — iar dublarea plății e riscul, deci se avertizează

## T18 — Chitanța și încasarea

*clasa MANUAL · 6 rute · 3 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/public/plata/{ref}`, `/tenants/{tenant_id}/chitante`, `/tenants/{tenant_id}/chitante/{chitanta_id}/pdf`*

### `POST /public/plata/{ref}/confirma`

*garda `FARA GARDA` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): facturi (UPDATE) — prin `plati`*

- [x] confirmarea se acceptă **numai** dacă e semnată de procesator, cu semnătura verificată. Altfel oricine cu referința poate marca o factură ca plătită
- referința e imposibil de ghicit — nu incrementală, nu derivată din numărul facturii
- o confirmare pe o referință deja confirmată nu produce a doua încasare
- suma confirmată se compară cu suma din link; o diferență nu se acceptă tăcut
- încasarea produsă poartă sursa „plată online", nu se confundă cu una introdusă manual
- **verificat la sursă (26.08.2026): SEMNĂTURA NU SE VERIFICĂ — dar nu există procesator care s-o dea.** `plati.provider_activ()` întoarce `mock` cât timp lipsesc `STRIPE_SECRET_KEY`/`NETOPIA_API_KEY`, iar `genereaza_link` **ridică `NotImplementedError`** pentru orice alt provider. `confirma_plata(conn, schema, ref)` primește **doar `ref`** și face `UPDATE facturi SET platita_la=now()`
- **și totuși NU e prag 1, măsurat**: `plata_ref` e **0 pe toate cele 17 firme** — niciun link n-a fost generat vreodată, deci efectul n-a fost produs. Iar `ref` e `secrets.token_urlsafe(16)`, adică 128 de biți: *cine are referința* înseamnă *cine a primit linkul*, nu *oricine*. E **R43**, deschisă, prag 2, blocată EXTERN pe cheile unui procesator real
- problema e **semantica, nu secretul**: aplicația nu deosebește *clientul a apăsat butonul de demo* de *banii au intrat*. Pagina spune literal *„Apăsați pentru a simula plata”*, dar `platita_la` care rezultă arată identic cu unul real
- ruta **parcurge toate schemele de firme** căutând `ref` — nu e o scurgere (nu întoarce nimic din alte firme), dar e o căutare care ar trebui să plece de la firma din `ref`
- **confirmarea nu produce nicio încasare în evidență** — niciun rând în `casa_operatiuni`, niciun `inregistrari`. Marchează factura, atât

### `POST /tenants/{tenant_id}/chitante`

*garda `cere_rol` · rol:admin_firma · scrie in chitante, facturi*

*ce face: Emite chitanta (cod 14-4-1, Ordin 2634/2015) pentru incasare in numerar: numerotare pe serie per firma + operatiune in Registrul de casa prin casa_api (5311=4111, nota ci — scrie chitante (INSERT) · facturi (UPDATE) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): casa_operatiuni (DELETE/INSERT) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [x] chitanța se păstrează cu numărul exemplarului, momentul, autorul, amprenta
- **numerotarea nu are goluri și nu se reia** — o chitanță anulată își păstrează numărul
- suma chitanței nu depășește soldul neîncasat al facturii la care se leagă
- dacă nu se leagă de nicio factură, se spune la ce se leagă

### `POST /tenants/{tenant_id}/facturi/{factura_id}/link-plata`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): facturi (UPDATE) — prin `plati`*

- [x] link-ul poartă suma exactă a facturii, nu una editabilă de plătitor
- link-ul expiră; expirarea e o stare, nu o eroare
- un al doilea link pe aceeași factură invalidează primul, sau se refuză — nu coexistă două

## T19 — Scadențarul și notificările de scadență

*clasa MECANIC · 2 rute · 1 schimba date · 0 firme il pot exercita azi*

*clasa MECANIC · 2 rute · 1 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/scadentar`*

### `PUT /tenants/{tenant_id}/scadentar/opt-in`

*garda `cere_rol` · rol:admin_firma*

*ce face: F131: activeaza/dezactiveaza notificarile email de scadenta pt firma (default OFF). — poate atinge, prin modul (PLAFON, nemasurat pe ruta): facturi (UPDATE) · firma_profil (UPDATE) — prin `scadentar`*

- [x] opt-in-ul poartă autorul și momentul — e o decizie despre comunicarea cu clienții firmei
- verifică ce se trimite: notificări către clienți în numele firmei, sau doar către cabinet?
- dacă merge către clienți, opt-out-ul trebuie să existe și să fie la fel de simplu

## T20 — Mișcarea de stoc — intrare, ieșire, transfer, reclasificare

*clasa MECANIC · 12 rute · 7 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/stocuri/analitica`, `/tenants/{tenant_id}/stocuri/articole`, `/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa`, `/tenants/{tenant_id}/stocuri/barcode/{cod}`, `/tenants/{tenant_id}/stocuri/locatii`*

### `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [x] un cod de bare duplicat în firmă se refuză — altfel scanarea devine ambiguă
- modificarea nu atinge stocul și nu produce mișcare

### `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [x] nivelul minim e o alertă, nu o restricție — verifică dacă blochează ieșirile sub el, ceea ce ar fi greșit
- modificarea nu atinge stocul

### `POST /tenants/{tenant_id}/stocuri/descarcare`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): inregistrari (INSERT) · inregistrari_linii (INSERT) · nir (INSERT) · nir_linii (INSERT) — prin `stocuri_api`*

- [x] descărcarea se leagă de un document — factură, bon, consum. O descărcare fără document rupe lanțul P14
- metoda de evaluare la ieșire (FIFO, CMP) e cea configurată pe firmă, nu aleasă la operațiune
- costul descărcat vine din intrări, nu se introduce liber

### `POST /tenants/{tenant_id}/stocuri/iesire`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [x] **nu pot scrie verificarea fără să știu ce o deosebește de `descarcare`.** De completat din cod
- dacă sunt aceeași operațiune pe două rute, e interdicția 15
- **completat din cod (26.08.2026): NU e duplicat cu `stocuri/descarcare`, și nu e nici măcar același fel de lucru.** `iesire` = **o mișcare pe UN articol**, din corpul cererii (`articol_id`, cantitate), valoare la **CMP**, notă ciornă `cont_cheltuiala = cont_stoc`. `descarcare` = **descărcarea gestiunii pe LUNĂ** (`an`, `luna`, fără corp), calculată din **rulajele reale ale notelor validate**, cumulat de la 1 ianuarie (OMFP 1802), pe conturile 371/378/4428, cu soldurile inițiale preluate din `solduri_initiale`
- deci nu e **interdicția 15**: nu sunt două intrări pentru aceeași operațiune, ci o mișcare de articol și un calcul de perioadă. Granularitate diferită, module diferite (`stocuri_cv_api` vs `stocuri_api`), obiecte diferite
- verificarea de fond care REZULTĂ din asta: **suma mișcărilor de articol dintr-o lună trebuie să se regăsească în descărcarea lunii**. Dacă cele două nu se leagă, una din ele minte — iar asta e o verificare pe care nimeni n-o face azi

### `POST /tenants/{tenant_id}/stocuri/intrare`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [x] intrarea se leagă de un document — NIR, producție, transfer
- costul de intrare cuprinde ce trebuie: preț, transport, taxe nedeductibile. Verifică ce cuprinde efectiv
- o intrare pe un articol inexistent creează articolul sau se refuză — verifică ce face

### `POST /tenants/{tenant_id}/stocuri/reclasificare`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [x] reclasificarea schimbă categoria, nu cantitatea și nu valoarea
- verifică dacă poate muta un articol între categorii cu tratamente fiscale diferite — marfă în materie primă schimbă contul, deci nota

### `POST /tenants/{tenant_id}/stocuri/transfer`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [x] transferul între gestiuni nu schimbă valoarea totală a stocului — suma iese dintr-o gestiune și intră în alta, la același cost
- transferul nu produce venit sau cheltuială
- gestiunea sursă și cea destinație există și sunt diferite

## T21 — Rețeta și producția

*clasa MECANIC · 9 rute · 7 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/produse`, `/tenants/{tenant_id}/retete`*

### `POST /tenants/{tenant_id}/produse`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [x] codul produsului e unic în firmă
- produsul cu rețetă are cost calculat din componente, nu introdus liber

### `POST /tenants/{tenant_id}/produse/potriveste`

*garda `cere_context` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [x] potrivirea e o **propunere**, nu o legătură creată — verifică structural că nu scrie
- fiecare potrivire propusă poartă gradul de certitudine; una slabă nu se prezintă ca sigură

### `DELETE /tenants/{tenant_id}/produse/{produs_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [x] un produs cu mișcări de stoc nu se șterge — se dezactivează
- ștergerea nu atinge producțiile trecute

### `PUT /tenants/{tenant_id}/produse/{produs_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [x] modificarea rețetei unui produs **nu recalculează costul producțiilor trecute** — acelea au costul de la momentul lor
- dacă recalculează, produce contradicție cu notele deja scrise

### `POST /tenants/{tenant_id}/retete`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [x] componentele rețetei există ca articole
- cantitățile sunt pozitive, iar unitatea de măsură a componentei coincide cu cea a articolului

### `POST /tenants/{tenant_id}/retete/descarca`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [x] descărcarea pe rețetă scoate din stoc **componentele**, la cantitățile din rețetă, înmulțite cu cantitatea produsă
- produsul finit intră în stoc la costul componentelor descărcate
- suma valorii componentelor ieșite = valoarea produsului intrat
- dacă o componentă nu are stoc suficient, operațiunea se refuză întreagă — nu descarcă parțial

### `DELETE /tenants/{tenant_id}/retete/{reteta_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [x] o rețetă folosită într-o producție nu se șterge — se dezactivează
- ștergerea nu schimbă costul producțiilor trecute

## T22 — Mijlocul fix și amortizarea

*clasa MECANIC · 3 rute · 2 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/mijloace-fixe`*

### `POST /tenants/{tenant_id}/amortizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Genereaza nota de amortizare lunara: 6811 = cont_amortizare, per MF activ. — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] amortizarea lunară se calculează din valoarea de intrare și durata rămasă, la data lunii
- un mijloc fix complet amortizat nu mai produce amortizare
- amortizarea contabilă și cea fiscală pot diferi — verifică dacă se disting, sau se calculează una singură
- **scrie `validata` direct**, deci a primit rol azi. Verifică că nu se poate rula de două ori pe aceeași lună

### `POST /tenants/{tenant_id}/reevaluare-imobilizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie reevaluare|surplus, + reevaluare{mijloc_fix_id, valoare_justa, sold_105_activ?, pierdere_655_anterioara?} | surplus{suma}} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] reevaluarea schimbă valoarea de intrare, deci **schimbă amortizarea viitoare** — dar nu pe cea trecută
- diferența din reevaluare merge la rezervă, nu la venit — verifică unde ajunge
- reevaluarea în minus sub valoarea contabilă e cheltuială, nu rezervă negativă
- **fără rol, deși schimbă o bază de calcul care intră în declarația de profit** — poziție, nu notă
- **MĂSURAT 26.08.2026, la cererea ta — și răspunsul e altul decât presupuneai, în direcția mai proastă.** Ruta **NU schimbă baza de amortizare**: citește valoarea și amortizarea cumulată din `mijloace_fixe` (`SELECT … WHERE id=%s AND activ=true`) și scrie **doar o notă ciornă**. Niciun `UPDATE` pe `mijloace_fixe` — verificat pe tot corpul rutei
- **deci reevaluarea schimbă valoarea contabilă, dar registrul care conduce amortizarea rămâne pe valoarea veche** — iar `POST /amortizare` calculează „per MF activ” din exact acel registru. Docstringul o recunoaște: *„actualizeaza valoarea/dnf ramane manual (raport evaluator)”*. Nu e o scăpare tăcută; e o limită declarată. Dar consecința e că **nota și registrul spun două lucruri diferite despre același activ**
- deci verificarea de fond nu e „cere rol”, ci: **după reevaluare, amortizarea lunii următoare se calculează pe valoarea reevaluată** — sau, dacă nu, aplicația o spune. Azi nu o spune nicăieri
- iar despre rol: criteriul de la R55 (scrie `validata`) **nu o prinde**, corect — scrie ciornă. Dar dacă registrul ar începe să fie actualizat aici, ar deveni o schimbare imediată de bază fiscală, iar atunci criteriul ar trebui reaplicat

## T23 — Bonul de la client — portalul și decontul

*clasa MECANIC · 9 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/portal/bon/{bon_id}/imagine/{n}`, `/tenants/{tenant_id}/bonuri/de-verificat`, `/tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate`, `/tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}`*

### `POST /portal/bon`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Extrage datele bonului cu AI si salveaza ca DRAFT (status='extras') + pozele pe disc — scrie bonuri (DELETE/INSERT)*

- [x] clientul poate încărca doar pe firma lui — verificat pe context, nu pe rol
- bonul intră ca **nevalidat**; clientul nu produce evidență
- imaginea se păstrează, nu doar datele citite din ea

### `DELETE /portal/bon/{bon_id}`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Clientul reface poza -> draftul (status='extras') si pozele lui se sterg. — scrie bonuri (DELETE)*

- [x] clientul poate șterge doar bonuri **neaprobate** — unul aprobat a devenit evidență
- ștergerea nu lasă în urmă imaginea orfană, sau o lasă și se spune
- ștergerea se consemnează — un bon care dispare fără urmă e o cheltuială care nu se mai poate reconstitui

### `POST /portal/bon/{bon_id}/confirma`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Clientul confirma ca poza e intreaga si lizibila -> bonul intra la contabil. — scrie bonuri (UPDATE)*

- [x] confirmarea clientului nu e aprobare — bonul rămâne de validat de cabinet
- verifică ce poate schimba clientul la confirmare: dacă poate modifica sumele, cabinetul trebuie să vadă ce a modificat

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/aproba`

*garda `cere_cabinet` · **fara rol** · scrie in bonuri, inregistrari, inregistrari_linii*

*ce face: scrie bonuri (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] aprobarea produce evidență — de aceea a primit rol azi
- bonul aprobat poartă legătura către imaginea din care a ieșit
- cifrele aprobate coincid cu cele citite din imagine, sau diferența e consemnată ca modificată de om
- un bon aprobat de două ori nu produce două note

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/stinge`

*garda `cere_rol` · rol:admin_firma · scrie in bonuri, facturi*

*ce face: Chitanta certificata de contabil: plata furnizor prin Registrul de casa (casa_api.adauga -> 401=5311 ciorna + operatiune casa + verificare plafon) — scrie bonuri (UPDATE) · facturi (UPDATE) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): casa_operatiuni (DELETE/INSERT) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [x] stingerea produce **o singură** operațiune de casă; o a doua apăsare nu produce a doua plată
- suma stinsă nu depășește soldul neplătit al bonului
- plafonul de plăți în numerar se verifică — ruta îl cheamă, verifică că refuză când e depășit
- soldul casei nu devine negativ
- bonul trece în „stins" și nu se mai poate stinge
- data operațiunii de casă e într-o perioadă deschisă

---

## T24 — Bonul fiscal și raportul Z (AMEF, horeca)

*clasa MECANIC · 2 rute · 2 schimba date · ? firme il pot exercita azi*

*clasa MECANIC · 2 rute · 2 schimba date · nu se poate sti din date*

### `POST /tenants/{tenant_id}/horeca/import-amef`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Upload p7b/XML AMEF (OPANAF 146/2018 II.7) -> nota Raport Z CIORNA — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] nota produsă e **ciornă** — verificat pe starea scrisă
- fișierul p7b e verificat ca semnătură, nu doar citit — altfel orice XML poate deveni raport Z
- totalurile din notă coincid cu cele din fișier: total încasări, TVA pe cote, număr de bonuri
- un fișier importat de două ori nu produce a doua notă — verificat pe conținut, nu pe nume
- data raportului Z e într-o perioadă deschisă

### `POST /tenants/{tenant_id}/horeca/raport-z`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] **nu pot scrie verificarea fără să știu ce o deosebește de `import-amef`.** Ambele produc nota de raport Z; una are rol, cealaltă nu
- dacă e introducere manuală a raportului Z, verifică: totalurile pe cote de TVA se adună la totalul general
- dacă e aceeași operațiune pe două căi, e interdicția 15 — iar rolul diferit o face vizibilă

---

## T25 — Comanda din magazinul online (WooCommerce)

*clasa MANUAL · 3 rute · 2 schimba date · ? firme il pot exercita azi*

*clasa MANUAL · 3 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/woocommerce/config`*

### `PUT /tenants/{tenant_id}/woocommerce/config`

*garda `cere_context` · **fara rol** · scrie in firma_profil*

*ce face: scrie firma_profil (UPDATE)*

- [x] cheile de acces nu se întorc în răspuns
- schimbarea configurației nu atinge facturile deja sincronizate
- o configurație salvată e verificată că se conectează, sau se spune că n-a fost verificată

### `POST /tenants/{tenant_id}/woocommerce/sincronizeaza`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): facturi (UPDATE) · firma_profil (UPDATE) — prin `woocommerce`*

- [x] fiecare comandă sincronizată produce **o singură** factură; o a doua rulare nu dublează
- cota de TVA vine din articol sau din configurație — **nu se ghicește din denumire**
- comenzile care nu s-au putut transforma în factură se numesc, cu motivul; nu se sar tăcut
- ultima sincronizare reușită se păstrează, ca următoarea să știe de unde continuă

## T26 — Registratura

*clasa MECANIC · 2 rute · 1 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/registratura`*

### `POST /tenants/{tenant_id}/registratura`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): registratura (INSERT) — prin `registratura_api`*

- [x] numărul de înregistrare e **din serie, fără goluri** — registratura e un registru, nu o listă
- data înregistrării nu e în viitor
- un document înregistrat nu se poate șterge; se anulează, cu numărul păstrat
- verifică dacă numerotarea se reia la începutul anului sau e continuă — amândouă sunt legitime, dar trebuie să fie una

---

## T27 — e-Transport

*clasa MANUAL · 3 rute · 2 schimba date · 0 firme il pot exercita azi*

*clasa MANUAL · 3 rute · 2 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/etransport/trimiteri`*

### `POST /tenants/{tenant_id}/etransport-xml`

*garda `cere_cabinet` · **fara rol***

*ce face: intoarce {nota, xml}*

- [x] XML-ul generat conține toate câmpurile obligatorii; unul lipsă oprește generarea cu numele lui
- codurile din nomenclatoare — scop, tip de operațiune, unități — vin din registru, nu din literali
- greutatea și valoarea sunt cele din documentul de transport, nu recalculate

### `POST /tenants/{tenant_id}/etransport/trimite`

*garda `cere_rol` · rol:admin_firma*

*ce face: Trimite notificarea UIT in SPV (F121): genereaza XML + trimite() cu PORTI in ordine (garda de timp -> idempotency -> validare pe TEST -> upload) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): etransport_trimiteri (INSERT/UPDATE) — prin `etransport_send`*

- [x] cele patru porți rulează **în ordine**: garda de timp → idempotență → validare pe TEST → încărcare. O poartă sărită e un defect, nu o optimizare
- codul UIT primit se păstrează; fără el, starea e „nelămurită"
- garda de timp refuză o trimitere după termenul legal — și spune care e termenul
- idempotența e pe conținut, nu pe moment: același transport trimis de două ori e prins chiar dacă a trecut timp

## T28 — Operațiunile intracomunitare, VIES și Intrastat

*clasa MECANIC · 12 rute · 6 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/public/verifica-cui/{cui}`, `/tenants/{tenant_id}/d390-clasificare`, `/tenants/{tenant_id}/registre-art321/{fel}`, `/tenants/{tenant_id}/intrastat-praguri`, `/tenants/{tenant_id}/verifica-cui/{cui}`, `/tenants/{tenant_id}/verifica-vies`*

### `POST /tenants/{tenant_id}/achizitie-ic`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: AIC bunuri/servicii primite (art — scrie inregistrari (INSERT) · inregistrari_linii (INSERT) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] taxarea inversă: TVA-ul se înregistrează simultan deductibil și colectat, iar cele două se anulează în decont
- cursul e cel de la data exigibilității, cerut din registru — nu introdus liber
- codul de TVA al furnizorului e validat algoritmic și, dacă se poate, în VIES
- operațiunea intră în D390 cu codul corect, și în D300 la rândurile de achiziții intracomunitare
- **`firma_profil` se atinge, și se știe de ce**: `facturi_api` face `UPDATE firma_profil SET urmator_numar_factura` — contorul de numerotare a facturii. Verifică-l pe efect: două achiziții consecutive primesc numere consecutive, iar un refuz nu consumă un număr
- **stocul nu se mișcă de aici** — ruta cheamă `facturi_api` și `intracomunitar`, niciun modul de stoc. Pentru o achiziție intracomunitară de bunuri asta e o absență, consemnată la R64

### `POST /tenants/{tenant_id}/registre-art321/{fel}`

*garda `cere_cabinet` · **fara rol***

*ce face: Inscrie un rand — poate atinge, prin modul (PLAFON, nemasurat pe ruta): registre_art321 (INSERT) — prin `registre_art321`*

Singurul pas de scriere al traseului care NU deriva din alta evidenta: un nontransfer e o miscare
de bunuri fara vanzare, deci nu exista factura din care sa iasa. Normele art. 321 alin. (4) CF
(HG 1/2016): lit. e) nontransferuri, lit. f) bunuri primite pentru lucrari.

- **numarul de ordine se DERIVA, nu se primeste**: doua inscrieri consecutive pe acelasi registru
  primesc numere consecutive, iar cele doua registre isi numara separat
- **un camp cerut de norma nu poate lipsi, iar refuzul NUMESTE campul**: incearca fara adresa
  partenerului si citeste ce scrie pe ecran — trebuie sa spuna care camp, si sa marcheze inputul
- **`valoare` e ceruta la lit. e) si NU la lit. f)**: comuta registrul si vezi ca formularul se
  schimba. Daca ar cere valoare si la bunuri primite, ar refuza o inscriere pe care legea o accepta
- **cele cinci exceptii se ARATA, nu se aplica**: scrie in descriere „computer portabil" si verifica
  faptul ca aplicatia inscrie randul oricum. Decizia ca o scutire se aplica e a contabilului
- **un camp doar cu spatii nu trece drept completat** — altfel evidenta e completa la vedere si
  goala in fapt
- **fara rol, desi scrie intr-un registru fiscal** — aceeasi absenta ca la `d390-clasificare/manual`,
  consemnata aici ca sa nu treaca drept intentie

### `POST /tenants/{tenant_id}/d390-clasificare/manual`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga linie pur manuala: {an, luna, tip, tara, cod, den, baza}. — poate atinge, prin modul (PLAFON, nemasurat pe ruta): d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [x] linia manuală poartă **motivul** existenței ei: ce operațiune reprezintă și de ce nu vine din evidență
- codul de TVA e validat algoritmic pentru țara respectivă, la introducere
- tipul e din nomenclatorul oficial — după reancorarea pe normă, nu pe XSD
- o linie manuală pe o lună cu D390 depus produce contradicție
- **fără rol, deși adaugă direct într-o declarație**

### `DELETE /tenants/{tenant_id}/d390-clasificare/manual/{mid}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [x] ștergerea unei linii dintr-o lună cu D390 depus produce contradicție — declarația depusă conținea linia
- ștergerea se consemnează: cine, când, ce conținea linia
- **fără rol** — iar ștergerea unei linii dintr-o declarație e mai gravă decât adăugarea: dispare fără urmă

### `PUT /tenants/{tenant_id}/d390-clasificare/reclasificare`

*garda `cere_cabinet` · **fara rol***

*ce face: Override tip pe o operatiune auto: {an, luna, directie, tara, cod, tip}. — poate atinge, prin modul (PLAFON, nemasurat pe ruta): d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [x] reclasificarea **schimbă ce se declară** — o operațiune mutată din tip L în tip T schimbă D390
- override-ul poartă motivul: de ce clasificarea automată era greșită
- o reclasificare pe o lună cu D390 deja depus produce contradicție vizibilă, nu rescriere tăcută
- codul de țară și codul de TVA rămân neschimbate — reclasificarea privește tipul, nu partenerul
- **fără rol, deși schimbă conținutul unei declarații**

### `POST /tenants/{tenant_id}/vanzare-ic`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: LIC bunuri (art — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] livrarea intracomunitară e scutită cu drept de deducere; nu se colectează TVA
- scutirea cere **dovada transportului** și codul de TVA valid al clientului. Fără ele, operațiunea nu e scutită
- codul de TVA al clientului e verificat în VIES la data operațiunii, iar rezultatul se păstrează — o verificare care nu se păstrează nu se poate dovedi la control
- operațiunea intră în D390 cu cod L
- **fără rol, deși `achizitie-ic` — aceeași clasă — cere admin_firma**
- **livrarea nu scoate bunurile din stoc** — ruta cheamă `intracomunitar` și `cont_valid`, niciun modul de stoc. La o livrare de BUNURI asta e cea mai vizibilă formă a absenței de la R64: marfa pleacă din firmă în contabilitate și rămâne în evidența cantitativă

---

## T29 — Regimurile speciale de TVA — marjă, aur, agricultori, taxare inversă

*clasa MECANIC · 11 rute · 10 schimba date · ? firme il pot exercita azi*

*clasa MECANIC · 11 rute · 10 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/jurnal-marja`*

### `POST /tenants/{tenant_id}/achizitie-agricultor`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare (fara taxa), cont_cheltuiala, agricultor_in_registru, agricultor?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] compensația în cotă forfetară se calculează pe cota în vigoare la data operațiunii
- agricultorul e verificat că e în regimul special — altfel e o achiziție obișnuită
- compensația plătită e deductibilă la cumpărător; verifică unde ajunge în D300
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/achizitie-necorporala`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii, mijloace_fixe*

*ce face: corp: {data, denumire, valoare (fara TVA), tip software|licenta|brevet| dezvoltare|constituire, dnf_luni?, cota?, cod?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · mijloace_fixe (INSERT) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] durata normală de funcționare vine din catalog pentru tipul respectiv; `dnf_luni` din corp nu o poate coborî sub minim
- valoarea sub pragul de imobilizare nu produce mijloc fix — e cheltuială. Verifică pragul la data operațiunii
- rândul din `mijloace_fixe` și nota din `inregistrari` au aceeași valoare de intrare
- amortizarea începe din luna următoare punerii în funcțiune, nu din luna achiziției

### `POST /tenants/{tenant_id}/achizitie-neinregistrat`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: Achizitie de la persoana fizica NEINREGISTRATA in scop TVA -> op N in D394 (pct.216 tip_partener=2) — scrie inregistrari (INSERT) · inregistrari_linii (INSERT) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] operațiunea apare în D394 ca tip N, cu `tip_partener=2` — verificat pe declarația generată, nu pe intenția din cod
- persoana fizică nu are cod fiscal, deci nu se cere; dar se cere o identificare, altfel operațiunea n-are partener
- TVA-ul nu se deduce — achiziția de la neînregistrat nu poartă TVA deductibilă
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul. Verificarea *«dacă atinge stocul prin modul, mișcarea de stoc are aceeași dată cu nota»* avea condiția scrisă în față; condiția e acum cunoscută **falsă**, deci rândul rămâne fără obiect. Restul stau pe `facturi_api`, care e real.

### `POST /tenants/{tenant_id}/achizitie-taxare-inversa`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, categorie, valoare (fara TVA), cont_destinatie, cota?, furnizor_platitor_tva, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] bunul sau serviciul e din lista art. 331 — altfel taxarea inversă nu se aplică
- pragul de 22.500 lei pentru telefoane, tablete, laptopuri, console e verificat pe factură, nu pe operațiune
- TVA-ul se înregistrează simultan ca deductibil și colectat, iar cele două se anulează în decont
- furnizorul e înregistrat în scopuri de TVA — altfel regimul nu se aplică
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/export-extracomunitar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare, tara_client, dovada_export, cont_venit?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] exportul e scutit cu drept de deducere; nu se colectează TVA
- scutirea cere **dovada exportului** — declarația vamală de export. Fără ea, operațiunea nu e scutită, iar ruta primește `dovada_export` ca text liber
- verifică ce se întâmplă când `dovada_export` lipsește sau e o frază: se refuză, sau se scutește pe încredere?
- țara clientului e din afara UE — o țară din UE face operațiunea livrare intracomunitară, nu export
- **fără rol, deși scrie evidență** — R55
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/import-extracomunitar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare_vamala (RON), procent_taxa_vamala?, accize?, accesorii?, cota?, certificat_amanare?, cont_destinatie, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] baza de TVA la import = valoarea vamală + taxa vamală + accize + accesorii până la primul loc de destinație. Verifică pe cifre, nu pe formulă
- cu certificat de amânare, TVA-ul nu se plătește în vamă: se înregistrează simultan colectat și deductibil, iar cele două se anulează în decont
- fără certificat, TVA-ul plătit în vamă e deductibil pe baza declarației vamale, nu a facturii furnizorului
- cota aplicată e cea de la data operațiunii, cerută din registru
- **fără rol, deși scrie evidență** — R55
- **ADNOTARE SCHIMBATĂ 26.08.2026 — R60.** Din rândul `ce face` s-a ȘTERS *«poate atinge, prin modul: `articole`, `miscari_stoc` — prin `stocuri_cv_api`»*. Nu ruta s-a schimbat, ci instrumentul: `scan_trasee.py` rezolva aliasul `_cv` prin harta altcuiva, iar aici `_cv` e `cont_valid` — care doar confruntă contul cu planul firmei și nu scrie nimic. Verificările de mai sus rămân valabile **ca intenție**; ce nu se mai poate afirma e unde ajunge efectul.

### `POST /tenants/{tenant_id}/vanzare-agricultor`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, pret (fara taxa), descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] **nu pot scrie verificarea fără să știu ce reprezintă.** O vânzare CĂTRE un agricultor în regim special, sau o vânzare FĂCUTĂ de firmă dacă ea e agricultorul? Cele două au tratamente opuse. De completat din cod
- **completat din cod (26.08.2026) — și răspunsul contrazice docstringul.** Contarea e `4111 = 704` pentru **preț** ȘI pentru **compensație**, iar corpul cere doar `{data, pret, descriere?}`: **nicio identificare a agricultorului, niciun `in_registru`** — spre deosebire de `achizitie-agricultor`, care le cere. Deci **firma E agricultorul** în regim special și vinde; clientul îi datorează preț + compensație de 8%, iar compensația e **venitul ei**, nu TVA. Descrierea generată — *„Livrare produse agricole”* — spune la fel
- **docstringul rutei spune „Client agricultor regim special”, adică exact pe dos.** A treia instanță de R16 (proza care descrie codul poate fi falsă de la naștere) — și e chiar cea care ți-a produs întrebarea. Docstringul e corectat în același commit
- compensația se calculează pe cota în vigoare la data operațiunii, din `tva_agricultori` (8%, art. 315^1 alin. 2) — nu dintr-un literal în rută
- **ce NU am verificat**: dacă tratamentul contabil `4111=704` pentru compensație e cel corect fiscal. Am citit ce FACE codul și ce spune modulul; **n-am confruntat cu actul** dacă vânzătorul în regim special contează compensația ca venit sau altfel

### `POST /tenants/{tenant_id}/vanzare-aur-investitii`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, tip lingou|plancheta|moneda, puritate, an_emisie?, pret_unitar?, valoare_aur?, suma, optiune_taxare?, calitate_client PF|PJ, client_identificare, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] operațiunea e scutită fără drept de deducere; nu se colectează TVA
- dacă firma a optat pentru taxare, opțiunea e consemnată și verificată la fiecare operațiune
- aurul de investiții e definit prin puritate și formă — verifică dacă se validează, sau se acceptă orice

### `POST /tenants/{tenant_id}/vanzare-marja`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, pret_vanzare, pret_cumparare, cota?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] marja se calculează ca preț de vânzare minus preț de cumpărare, iar TVA-ul se aplică **pe marjă**, nu pe preț
- o marjă negativă nu produce TVA negativă — se tratează ca marjă zero, sau se semnalează
- prețul de cumpărare vine de la achiziția legată, nu se introduce liber

### `POST /tenants/{tenant_id}/vanzare-marja-turism`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, calitate_client PF|PJ, locuri [RO|UE|NONUE], optiune_normal?, intermediar?, cota?, descriere?} + per regim: special: incasat, cost_ue, cost_non_ue? | normal: — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] aceleași ca la marjă, plus: locul prestării e România pentru ca regimul să se aplice
- serviciile prestate de terți în afara UE au tratament distinct — verifică dacă se disting

## T30 — Operațiunile în valută

*clasa MECANIC · 2 rute · 2 schimba date · ? firme il pot exercita azi*

*clasa MECANIC · 2 rute · 2 schimba date · nu se poate sti din date*

### `POST /tenants/{tenant_id}/decontare-valuta`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Incasare creanta / plata datorie in valuta cu diferenta de curs 665/765 — scrie inregistrari (INSERT) · inregistrari_linii (INSERT) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): curs_bnr_zilnic (INSERT) — prin `curs_bnr`*

- [x] diferența de curs se calculează între cursul de la înregistrarea creanței și cel de la decontare
- cursul vine din `curs_bnr_zilnic`; dacă lipsește pentru data respectivă, se aduce sau se refuză — **nu se folosește cel mai apropiat fără să se spună**
- diferența favorabilă merge în 765, cea nefavorabilă în 665 — verifică semnul
- decontarea parțială stinge proporțional, iar diferența de curs se calculează pe partea decontată
- **cursul folosit se SPUNE, nu doar se aplică**: regula legală e *cel mai recent curs cu data ≤ data operațiunii*, iar `curs_din_harta` chiar o aplică și întoarce ziua cursului — dar ruta aruncă ziua aia (`_dcurs`) și nu o pune nici în descriere, nici în răspuns. Verifică pe o dată de weekend: nota trebuie să spună din ce zi e cursul

### `POST /tenants/{tenant_id}/reevaluare-valuta`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Reevaluare lunara solduri valuta (OMFP 1802 pct — scrie inregistrari (INSERT) · inregistrari_linii (INSERT) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): curs_bnr_zilnic (INSERT) — prin `curs_bnr`*

- [x] reevaluarea se face la **finalul lunii**, pe soldurile în valută rămase — verifică dacă ruta o poate rula la orice dată
- cursul e cel din ultima zi bancară a lunii
- reevaluarea se aplică tuturor soldurilor în valută, nu doar celor selectate — o reevaluare parțială lasă bilanțul greșit
- o a doua reevaluare pe aceeași lună nu produce a doua notă — sau, dacă o produce, prima se stornează

---

## T31 — Completările manuale la o declarație (D300, D301)

*clasa MECANIC · 8 rute · 5 schimba date · 3 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/d300-manual`, `/tenants/{tenant_id}/d301-operatiuni`*

### `POST /tenants/{tenant_id}/d300-manual`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga/actualizeaza un rand manual D300: {an, luna, rand, baza, tva, descriere}. — poate atinge, prin modul (PLAFON, nemasurat pe ruta): d300_manual (DELETE/INSERT) — prin `d300_manual_api`*

- [x] rândul manual e din nomenclatorul de rânduri D300 — unul inexistent se refuză
- baza și TVA-ul sunt coerente cu cota rândului respectiv
- rândul manual poartă **motivul**: ce reprezintă și de ce nu vine din evidență
- suma rândurilor manuale plus cele derivate = totalul declarat; verifică că nu se dublează cu ce vine din facturi
- **fără rol, deși scrie direct în decontul de TVA**

### `DELETE /tenants/{tenant_id}/d300-manual/{rid}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): d300_manual (DELETE/INSERT) — prin `d300_manual_api`*

- [x] ștergerea pe o lună cu D300 depus produce contradicție
- ștergerea se consemnează cu ce conținea rândul
- **fără rol**

---

### `POST /tenants/{tenant_id}/registru-evidenta-fiscala`

*garda `cere_cabinet` · **fara rol***

*ce face: Înscrie un rând în varianta PERSOANE FIZICE — singura care se completează — poate atinge, prin modul (PLAFON, nemasurat pe ruta): registru_fiscal_pf (INSERT) — prin `registru_evidenta_fiscala`*

Constatarea de la care a pornit e scrisa in cod, in `core/d212.py`, in `pull()`: *«D212 e MANUALA pe
persoana fizica; firma nu are registru PF»*. Venitul brut si cheltuielile deductibile se introduc
direct in declaratie si nu se pastreaza nicaieri — ori tocmai asta cere art. 2 din OMFP 3254/2017:
registrul tine informatiile CARE STAU LA BAZA declaratiei.

- **la norma de venit, campul de cheltuieli nu se poate completa**: alege «norma de venit» la modul
  de stabilire si verifica faptul ca ecranul ASCUNDE campul. Un camp care se poate completa si apoi
  e respins invata omul ca aplicatia e capricioasa, cand de fapt norma e clara (art. 1 alin. (2))
- **la drepturi de proprietate intelectuala, cheltuielile sunt OPTIONALE** (art. 1 alin. (3)) — un
  rand fara ele trebuie sa treaca
- **in sistem real, ZERO e un raspuns valid si GOL nu e**: incearca amandoua. Zero inseamna «nu s-au
  avut cheltuieli»; gol inseamna «nu s-a stabilit inca», iar intr-un registru din care iese venitul
  net cele doua duc la aceeasi cifra si la doua adevaruri diferite
- **numerotarea curge pe SURSA din cadrul categoriei**, nu global: doua randuri pe aceeasi sursa
  primesc 1 si 2, iar primul rand pe alta sursa primeste tot 1
- **pierderea neta se arata ca pierdere, nu ca zero**: pune cheltuieli mai mari decat venitul brut.
  «Pierdere neta anuala» e chiar termenul ordinului, deci taierea la zero ar sterge o informatie pe
  care declaratia o cere
- **varianta pe profit NU are formular**, si asta se vede pe ecran: comuta pe «impozit pe profit» si
  verifica faptul ca nu apare niciun camp de completat. Cifrele ei sunt cele din D101 pe acelasi an
  — un al doilea calcul ar putea contrazice declaratia pe care registrul exista ca s-o justifice
- **totalizarea pe trimestru se REFUZA cu motiv**, nu se calculeaza cu formule anuale: cere-o si
  citeste ce scrie. Un registru lipsa se vede; unul gresit nu
- **fara rol, desi scrie intr-un registru fiscal** — a treia oara azi, consemnata ca sa nu treaca
  drept intentie

### `POST /tenants/{tenant_id}/d301-operatiuni`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga o operatiune: {an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, cota}. — poate atinge, prin modul (PLAFON, nemasurat pe ruta): d301_operatiuni (DELETE/INSERT) — prin `d301_operatiuni_api`*

**Din lotul în care s-a scris, valabil pentru tot traseul:** **Grupa cea mai gravă din lot: patru rute fără rol care scriu direct în ce intră în D300 și D301.**

- [x] `temei_307` e obligatoriu pentru operațiunile de tip 4 — construit pe 22.08, verifică că refuză fără el
- cursul e cel de la data documentului, cerut din registru
- valuta e din nomenclatorul de 20, iar limita e declarată — o valută legală din afara listei nu se poate depune
- o operațiune adăugată pe o lună cu D301 depus produce contradicție vizibilă
- **fără rol, deși scrie direct într-o declarație**

### `DELETE /tenants/{tenant_id}/d301-operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): d301_operatiuni (DELETE/INSERT) — prin `d301_operatiuni_api`*

- [x] ștergerea pe o lună cu D301 depus produce contradicție — declarația conținea operațiunea
- ștergerea se consemnează cu ce conținea operațiunea
- **fără rol** — o operațiune ștearsă din declarație dispare fără urmă

## T32 — Registrul de încasări și plăți (partida simplă)

*clasa MECANIC · 7 rute · 5 schimba date · 0 firme il pot exercita azi*

*clasa MECANIC · 7 rute · 5 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/rip/d212/{an}`, `/tenants/{tenant_id}/rip/registru`*

### `POST /tenants/{tenant_id}/rip/import-banca`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [x] fiecare tranzacție din extras produce **o singură** operațiune RIP
- un extras importat de două ori nu dublează — verificat pe conținut
- operațiunile importate intră ca **ciorne**, nu validate; categoria fiscală se atribuie de om
- tranzacțiile care nu s-au putut clasifica se numesc, nu se sar

### `POST /tenants/{tenant_id}/rip/import-casa`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [x] aceleași ca la bancă
- **verifică dacă o operațiune de casă poate ajunge în RIP de două ori** — o dată din registrul de casă, o dată din import

---

### `POST /tenants/{tenant_id}/rip/operatiuni`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

**Din lotul în care s-a scris, valabil pentru tot traseul:** **Partida simplă. Verificări comune celor cinci:** - firma e în partidă simplă — altfel RIP nu se aplică - data operațiunii e într-o perioadă deschisă - numerotarea în registru nu are goluri

- [x] operațiunea e **încasare sau plată efectivă**, nu angajament — în partidă simplă contează fluxul, nu factura
- încasările impozabile se disting de cele neimpozabile; plățile deductibile de cele nedeductibile
- fiecare operațiune poartă documentul justificativ
- operațiunea intră în D212 la rândul corespunzător

### `DELETE /tenants/{tenant_id}/rip/operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [x] o operațiune **validată** nu se șterge — se stornează
- ștergerea pe o lună cu D212 depus produce contradicție
- **fără rol**

### `PUT /tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [x] **validarea transformă o ciornă în evidență** — după ea, operațiunea nu se mai editează
- validarea verifică înainte: document justificativ prezent, dată în perioadă deschisă, categorie fiscală atribuită
- cine a validat se consemnează
- **fără rol, iar aceasta e ruta care produce evidența în partidă simplă** — echivalentul lui `jurnal/{id}/valideaza`

## T33 — Exportul contabil (SAGA, WinMentor)

*clasa MECANIC · 3 rute · 2 schimba date · ? firme il pot exercita azi*

*clasa PARTIAL · 3 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi/{factura_id}/export-saga`*

### `POST /tenants/{tenant_id}/facturi/export-saga`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): artefacte_produse (INSERT) — prin `artefacte`*

- [x] fișierul exportat se păstrează ca artefact: conținut, moment, autor, amprentă, exemplar
- numărul de facturi din fișier = numărul de facturi din perioada exportată, iar cele excluse se numesc cu motivul
- codificarea fișierului e cea cerută de SAGA — verifică diacriticele
- o factură exportată de două ori nu creează două intrări la destinație — sau, dacă poate, se avertizează

### `POST /tenants/{tenant_id}/facturi/export-winmentor`

*garda `cere_rol` · rol:admin_firma*

*ce face: Export WinMENTOR: Facturi.txt + Articole.txt (Windows-1250) co-locate intr-un zip — poate atinge, prin modul (PLAFON, nemasurat pe ruta): artefacte_produse (INSERT) — prin `artefacte`*

- [x] aceleași ca la SAGA
- `Facturi.txt` și `Articole.txt` sunt coerente între ele: fiecare articol referit în facturi există în fișierul de articole
- codificarea Windows-1250 nu pierde diacritice — verifică pe un partener cu ș, ț, ă
- cele două fișiere sunt în același zip și au aceeași perioadă

---

## T34 — Rapoartele comerciale, centrele de cost și rapoartele salvate

*clasa MECANIC · 14 rute · 5 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/ansamblu`, `/api/v1/firme/{tenant_id}/kpi`, `/cabinet/consolidare`, `/tenants/{tenant_id}/centre-cost`, `/tenants/{tenant_id}/centre-cost/raport`, `/tenants/{tenant_id}/centre-cost/varianta`, `/tenants/{tenant_id}/rapoarte-comerciale`, `/tenants/{tenant_id}/rapoarte-comerciale/fisa`, `/tenants/{tenant_id}/rapoarte-salvate`*

### `POST /tenants/{tenant_id}/centre-cost`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [x] codul centrului e unic în firmă
- centrul nou nu atinge repartizările deja făcute

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [x] redenumirea unui centru nu schimbă repartizările istorice
- dezactivarea unui centru cu cheltuieli repartizate nu-l șterge — verifică ce se întâmplă

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}/buget`

*garda `cere_cabinet` · **fara rol***

*ce face: Seteaza bugetul anual (cheltuieli + venituri) al unui centru pe un an. — poate atinge, prin modul (PLAFON, nemasurat pe ruta): bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [x] bugetul e pe an; modificarea unui an încheiat se refuză, sau se consemnează
- bugetul nu constrânge cheltuielile reale — e o referință, nu o limită. Verifică dacă blochează ceva, ceea ce ar fi greșit
- suma bugetelor pe centre nu trebuie să dea un total impus — nu e o repartizare

---

### `POST /tenants/{tenant_id}/rapoarte-salvate`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): rapoarte_salvate (DELETE/INSERT) — prin `rapoarte_comerciale_api`*

- [x] raportul salvat păstrează **criteriile**, nu rezultatul — altfel devine o fotografie care se învechește
- dacă păstrează rezultatul, poartă data la care a fost calculat, iar la deschidere se spune că e vechi

### `DELETE /tenants/{tenant_id}/rapoarte-salvate/{vid}`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): rapoarte_salvate (DELETE/INSERT) — prin `rapoarte_comerciale_api`*

- [x] ștergerea nu atinge datele din care raportul se calculează
- un raport partajat cu altcineva din cabinet — verifică cine îl poate șterge

## T35 — Pachetul lunar către client și solicitările lui

*clasa MECANIC · 38 rute · 16 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/pachete/{tenant_id}/poveste`, `/pachete/{tenant_id}/preview`, `/pachete/{tenant_id}/rezumat`, `/portal/acasa`, `/portal/acces-cont`, `/portal/cashflow`, `/portal/declaratii`, `/portal/documente/balanta`, `/portal/documente/luni`, `/portal/facturi`, `/portal/firma`, `/portal/firme`, `/portal/kpi`, `/portal/povesti`, `/portal/recomanda/preview`, `/portal/solicitari`, `/portal/solicitari/contor`, `/tenants/{tenant_id}/client-acces`, `/tenants/{tenant_id}/clienti`, `/tenants/{tenant_id}/clienti/{client_id}`, `/tenants/{tenant_id}/solicitari`*

### `POST /pachete/{tenant_id}/genereaza`

*garda `cere_cabinet` · **fara rol***

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): pachet_povestea (INSERT) — prin `pachete_api`*

- [x] pachetul generat conține **cifrele lunii închise**, nu recalculul de azi — dacă luna nu e închisă, se spune
- generarea nu trimite nimic; e o previzualizare până la `trimite`
- o a doua generare pe aceeași lună produce a doua versiune, nu suprascrie prima — sau, dacă suprascrie, se spune
- **fără rol, deși `poveste` și `trimite` cer admin_firma, iar toate trei ating aceeași tabelă**

### `POST /pachete/{tenant_id}/poveste`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): pachet_povestea (INSERT) — prin `pachete_api`*

- [x] textul scris de contabil se păstrează cu autorul și momentul
- textul nu conține cifre calculate de el — sau, dacă le conține, ele nu se confruntă cu cele din pachet, iar aia e o divergență posibilă
- modificarea poveștii după trimitere produce o a doua versiune; ce s-a trimis rămâne

### `POST /pachete/{tenant_id}/trimite`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): pachet_povestea (INSERT) — prin `pachete_api`*

- [x] **trimiterea e un eveniment de predare**: cui, când, la ce adresă, cu ce conținut
- se trimite versiunea generată, cu amprenta ei — nu o regenerare la momentul trimiterii
- o a doua trimitere e un al doilea eveniment, nu suprascrie primul
- eșecul trimiterii e o stare vizibilă, nu o eroare pierdută — pachetul rămâne netrimis
- clienții fără adresă validă se numesc înainte de trimitere, nu după

---

### `POST /portal/acces-cont/acces`

*garda `cere_client` · rol:verificat-în-corp · scrie in user_tenants, users*

*ce face: scrie user_tenants (INSERT) · users (INSERT/UPDATE)*

- [x] accesul dat nu poate depăși accesul celui care îl dă — un client nu poate acorda mai mult decât are
- accesul e **doar pe firma lui**, verificat pe rândul din `user_tenants`, nu pe ce trimite în corp
- utilizatorul creat primește acces la portal, nu la aplicația cabinetului — verifică pe drepturile efective, nu pe intenție
- dacă adresa aparține unui utilizator existent — al altei firme, sau al cabinetului — ruta refuză, sau leagă contul existent? A doua variantă e o cale de escaladare
- crearea se consemnează cu cine a dat accesul, iar **cabinetul vede** că un client a adăugat pe cineva
- parola inițială nu se trimite prin canal nesigur

### `DELETE /portal/acces-cont/acces/{user_id}`

*garda `cere_client` · **fara rol** · scrie in user_tenants, users*

*ce face: scrie user_tenants (DELETE) · users (UPDATE)*

- [x] clientul poate retrage doar accese pe **firma lui** — verificat pe rândul șters, nu pe ce cere
- clientul nu se poate retrage pe sine, sau, dacă poate, firma rămâne fără niciun acces de client
- `user_tenants` se șterge, dar utilizatorul rămâne — ce a făcut nu devine anonim
- retragerea e imediată: sesiunile active se închid, sau se spune că nu se închid
- retragerea se consemnează, iar cabinetul o vede

### `PUT /portal/acces-cont/email`

*garda `cere_client` · **fara rol** · scrie in users*

*ce face: scrie schimbari_email (DELETE/INSERT)*

**Din lotul în care s-a scris, valabil pentru tot traseul:** **Actorul e clientul. `cere_client` verifică identitatea, nu rolul — corect prin construcție.**

- [x] schimbarea adresei de autentificare cere **confirmare pe adresa nouă** înainte de a intra în vigoare — altfel cineva cu sesiunea deschisă poate muta contul
- adresa veche primește o notificare despre schimbare
- schimbarea se consemnează: când, de la ce la ce
- cabinetul vede că adresa clientului s-a schimbat — altfel pachetele merg în altă parte fără ca nimeni să afle

### `POST /public/confirma-email`

*garda `FARA GARDA` · **fara rol** · scrie in oarb, schimbari_email, users*

*ce face: [R62 (1)] Confirmarea schimbarii de adresa — scrie schimbari_email (UPDATE) · users (UPDATE)*

- [x] **confirmarea e dovada că adresa nouă e citită de om, nu că sesiunea e deschisă** — ruta nu cere sesiune, deliberat; tokenul ajunge doar pe adresa nouă
- până la confirmare, `users.email` e neatins: cine intră cu adresa veche intră în continuare
- tokenul expiră (48h) și e de unică folosință — o a doua deschidere a linkului nu mai schimbă nimic
- adresa nouă se reconfruntă cu `users` **la confirmare**, nu doar la cerere: între cele două momente altcineva poate lua adresa
- confirmarea lasă urmă cu **de la ce, la ce** — o urmă care spune doar „s-a schimbat” nu permite nimănui să vadă ce s-a pierdut
- cabinetul vede în `urme-portal` **amândouă** actele: cererea și confirmarea. O cerere neconfirmată rămâne vizibilă — e chiar semnalul că cineva a încercat

### `POST /portal/recomanda`

*garda `cere_client` · **fara rol***

*ce face: intoarce {ok, rezultate}*

- [x] **nu pot scrie verificarea fără să știu ce recomandă.** Recomandă cabinetul altcuiva? Recomandă clientului ce să facă? De completat din cod
- oricare ar fi: nu scrie nimic, deci verificarea e că **nu scrie nimic** — verificat structural

### `POST /portal/solicitari`

*garda `cere_client` · **fara rol** · scrie in solicitari_client*

*ce face: scrie solicitari_client (INSERT) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): notificari (INSERT/UPDATE) — prin `notificari_api`*

- [x] solicitarea e legată de firma clientului, verificat pe context, nu pe ce trimite
- textul solicitării nu poate schimba date — e o cerere, nu o comandă
- cabinetul primește notificare; dacă notificarea eșuează, solicitarea rămâne, iar cineva o vede
- clientul își vede propriile solicitări și starea lor

---

### `POST /tenants/{tenant_id}/acces-portal`

*garda `cere_rol` · rol:admin_firma,angajat,verificat-în-corp*

*ce face: Emite un token de PREVIZUALIZARE (read-only, tab-local) pentru portalul clientului firmei*

- [x] tokenul e **read-only** și expiră — verifică ambele, nu doar că e declarat așa
- tokenul e legat de firmă și de utilizatorul care l-a emis
- emiterea se consemnează: cine, când, pentru ce firmă
- un token expirat nu mai dă acces, iar reînnoirea e o operațiune nouă, nu o prelungire tăcută

---

### `POST /tenants/{tenant_id}/client-acces`

*garda `cere_rol` · rol:admin_firma,verificat-în-corp · scrie in user_tenants, users*

*ce face: scrie user_tenants (INSERT) · users (INSERT/UPDATE) — poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firma_profil (INSERT/UPDATE) · tenants (INSERT/UPDATE) — prin `tenant_provisioning`*

- [x] **ruta creează un utilizator** — verifică ce drepturi primește: doar pe firma respectivă, doar citire, doar portalul
- un utilizator existent legat de altă firmă nu primește acces la asta fără o operațiune explicită
- parola inițială nu se trimite prin canal nesigur, și se schimbă la prima intrare
- **atinge `tenants` prin modul** — verifică de ce: crearea unui acces de client n-ar trebui să atingă tabela de firme
- crearea se consemnează: cine a dat accesul, când, cui

### `DELETE /tenants/{tenant_id}/client-acces/{user_id}`

*garda `cere_rol` · rol:admin_firma · scrie in users*

*ce face: scrie users (UPDATE)*

- [x] retragerea accesului e imediată — sesiunile active se închid, sau se spune că nu se închid
- utilizatorul nu se șterge; se dezactivează. Ce a făcut rămâne în urmă cu autorul identificabil
- retragerea se consemnează

### `POST /tenants/{tenant_id}/clienti`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

**Din lotul în care s-a scris, valabil pentru tot traseul:** **Nu știu dacă „clienți" înseamnă aici partenerii comerciali ai firmei sau persoanele de contact care primesc pachetul lunar.** Verificările de mai jos sunt scrise pentru a doua interpretare, fiindcă traseul e T35 — pachetul lunar. Dacă sunt parteneri comerciali, verificările se schimbă: atunci codul fiscal e obligatoriu, iar legătura cu facturile contează.

- [x] adresa de email e validată la introducere, nu la prima trimitere — un pachet trimis la o adresă greșită se pierde tăcut
- un client cu aceeași adresă în aceeași firmă se refuză, sau se spune că există
- clientul nou nu primește automat acces la portal — accesul e o operațiune separată
- crearea se consemnează: cine, când

### `DELETE /tenants/{tenant_id}/clienti/{client_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

- [x] un client care a primit pachete nu se șterge — se dezactivează. Istoricul trimiterilor rămâne cu destinatarul identificabil
- dacă are acces la portal, ștergerea îl retrage? Sau rămâne un cont fără client? Verifică
- ștergerea se consemnează

---

### `PUT /tenants/{tenant_id}/clienti/{client_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

- [x] schimbarea adresei de email **nu retrimite pachetele anterioare** și nu schimbă la cine au ajuns
- dacă clientul are acces la portal, schimbarea adresei aici schimbă și adresa de autentificare? Verifică — dacă da, cineva poate prelua un cont schimbând un câmp
- modificarea se consemnează cu valoarea veche

### `POST /tenants/{tenant_id}/solicitari`

*garda `cere_rol` · rol:admin_firma · scrie in solicitari_client*

*ce face: scrie solicitari_client (INSERT)*

- [x] **nu pot scrie verificarea fără să știu ce face cabinetul aici.** Răspunde la o solicitare? Creează una în numele clientului?
- dacă creează în numele clientului, verifică că se distinge de una făcută de client — altfel istoricul devine ambiguu
- dacă răspunde, verifică unde ajunge răspunsul: pe solicitare, sau ca notificare separată

---

## T36 — Ciclul de viață al firmei — creare, identitate, dezactivare, scoatere

*clasa MECANIC · 9 rute · 5 schimba date · ? firme il pot exercita azi*

*clasa MECANIC · 8 rute · 4 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/firme-scoase`, `/tenants`, `/tenants/{tenant_id}`, `/tenants/{tenant_id}/scoatere`*

**Ce e diferit la traseul ăsta.** Cele patru rute nu schimbă date **ale** unei firme — schimbă **existența** ei. Iar trei dintre ele sunt ireversibile în feluri diferite: crearea consumă un CUI, ștergerea distruge schema, iar schimbarea identității rescrie ce s-a declarat sub numele vechi. Verificările de mai jos pornesc de aici, nu de la tabelele atinse.

### `POST /tenants/{tenant_id}/activare`

*garda `cere_rol` · rol:admin_firma*

*ce face: [R72] Dezactivează / reactivează firma — poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firme_scoase (INSERT/UPDATE) · tenants (DELETE/UPDATE) · users (UPDATE) — prin `tenant_stergere`*

**Ce trebuie să fie adevărat după:**

- [x] **dezactivarea nu șterge nimic.** Schema rămâne, datele rămân, documentele emise rămân accesibile
- firma dezactivată **nu mai apare** în listele de lucru, dar apare în „Firme dezactivate" — cu drumul de întoarcere vizibil
- **nu se mai poate scrie** în firma dezactivată: nicio notă, nicio factură, nicio declarație. Verifică pe toate căile de scriere, nu doar pe cele din ecran
- **se poate încă citi**: un control fiscal pe o perioadă veche cere accesul la documentele unei firme care nu mai e client
- conturile de client ale unei firme dezactivate **nu mai pot intra în portal** — sau pot, dar văd că firma e inactivă. Alege una și fă-o explicită
- reactivarea readuce firma exact în starea de dinainte — nimic pierdut, nimic recalculat
- amândouă se consemnează: cine, când, în ce sens
- **`tenants (DELETE)` pe ruta de activare e neașteptat.** Verifică de ce ruta de dezactivare poate șterge rândul firmei — dacă e o cale comună cu `tenant_stergere`, o dezactivare n-are ce căuta pe ea

**Iar întrebarea care contează:** ce distinge dezactivarea de scoatere, din punctul de vedere al omului? Dacă un cabinet nu știe pe care s-o aleagă, ecranul trebuie s-o spună — una e reversibilă, cealaltă nu.

### `DELETE /tenants/{tenant_id}`

*garda `cere_rol` · rol:admin_firma*

*ce face: [R72] Scoate din portofoliu o firmă FĂRĂ evidență — poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firme_scoase (INSERT/UPDATE) · tenants (DELETE/UPDATE) · users (UPDATE) — prin `tenant_stergere`*

**Ce trebuie să fie adevărat după:**

- [x] **o firmă cu evidență nu se șterge.** Refuzul enumeră ce s-a găsit, nu spune doar „are documente"
- **o tabelă lipsă din schemă nu se numără ca zero.** Refuzul spune „nu pot decide" — o redenumire de tabelă ar transforma o firmă cu documente într-una ștearsă fără urmă
- toate cele 13 tabele din `public` care poartă `tenant_id` se curăță, **înainte** de `DROP SCHEMA`. Dacă una eșuează, schema rămâne și operațiunea se poate relua
- **nimic din afara firmei nu se mișcă.** Numărul de firme ale cabinetului scade cu unu; toate celelalte totaluri rămân
- un cont de client rămas fără nicio firmă **se dezactivează, nu se șterge** — identitatea unui om nu e proprietatea firmei
- urma din `firme_scoase` poartă: nume, CUI, schema, cine a apăsat, când, ce s-a curățat tabelă cu tabelă, și urmele păstrate
- **urma e citibilă de om**, din ecranul „Firme scoase" — nu doar din `psql`
- previzualizarea arată **ce dispare și ce se păstrează**, înainte de confirmare. Cifrele din previzualizare corespund cu ce se șterge efectiv
- confirmarea se cere **pe CUI, nu pe nume** — numele se repetă, iar chiar asta a produs restanța
- **la ștergerea unui cabinet întreg (GDPR), nu se păstrează nimic.** Un log care păstrează ce trebuia să dispară anulează ștergerea pe care o consemnează

### `POST /tenants/{tenant_id}/nume-ales`

*garda `cere_rol` · rol:admin_firma*

*ce face: [R77] Alegerea între denumirea din aplicație și cea de la ANAF — poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firma_profil (INSERT/UPDATE) · tenants (INSERT/UPDATE) · user_tenants (INSERT) — prin `tenant_provisioning`*

**Ce trebuie să fie adevărat după:**

- [x] **amândouă căile scriu.** „Păstrez denumirea mea" nu e absența unui act — dacă a păstra pe a ta înseamnă a nu apăsa nimic, nu e o alegere, e o moștenire
- [x] **niciuna nu e implicită.** Niciun buton primar, niciun bifat dinainte. Un răspuns sugerat e tot un răspuns dat în locul omului
- [x] **alegerea se datează și își știe autorul.** Altfel, peste un an, „denumirea asta e cea corectă" n-are pe ce sta
- [x] **întrebarea nu se pune la infinit**: cine a răspuns nu mai e întrebat
- [x] **și nici o singură dată**: o citire ANAF mai nouă decât alegerea o redeschide. Alegerea de azi nu acoperă o denumire schimbată la registru mâine
- [x] **a lua denumirea de la ANAF trece prin aceleași porți ca o redenumire** — inclusiv unicitatea în cabinet. Altfel calea asta ar fi o ușă din spate pentru un duplicat
- **ce se întâmplă cu documentele emise sub denumirea veche.** O declarație depusă poartă numele de atunci; ecranul nu spune azi nimic despre asta
- **ce se întâmplă dacă ANAF răspunde cu o denumire goală sau evident greșită** — refuzul există în cod, dar n-a fost exercitat pe un răspuns real
- **cine are voie să aleagă.** Azi: `admin_firma`. De verificat dacă un asistent care lucrează în firmă ar trebui măcar să vadă că există o divergență nerezolvată

**Iar întrebarea care contează, și e a lui Costin:** de ce se poate schimba denumirea unei firme cu CUI validat la ANAF? Alegerea de aici tratează **simptomul** — face divergența vizibilă și decizia consemnată. Nu răspunde de ce identitatea e editabilă după ce a fost confirmată la sursă.

### `POST /tenants`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firma_profil (INSERT/UPDATE) · tenants (INSERT/UPDATE) · user_tenants (INSERT) — prin `tenant_provisioning`*

**Ce trebuie să fie adevărat după:**

- [x] **CUI-ul e unic în cabinet.** Un CUI care există deja se refuză, iar refuzul spune care firmă îl poartă — altfel omul nu știe dacă e a lui sau a altui cabinet
- **Denumirea e unică în cabinet.** Nici Registrul Comerțului, nici ANAF nu permit două firme cu același nume; două rânduri identice în portofoliu sunt un fapt imposibil în realitate
- CUI-ul trece cifra de control **înainte** de interogarea la ANAF — altfel se cheltuie un apel extern pe o valoare invalidă
- firma creată are **schemă proprie**, iar rândul din `tenants` și schema există amândouă. O firmă fără schemă e o afirmație falsă despre lume — e cauza rândului 2020
- dacă crearea schemei eșuează, rândul din `tenants` nu rămâne. Tranzacția e întreagă sau nu e deloc
- `user_tenants` leagă firma de cabinetul care a creat-o, nu de utilizatorul care a apăsat
- ce s-a preluat de la ANAF — adresă, CAEN, Reg.Com., stare TVA — e consemnat **cu momentul preluării**, ca la o reverificare să se știe ce era atunci
- **denumirea preluată de la ANAF nu se suprascrie tăcut cu ce a tastat omul, și nici invers.** Dacă cele două diferă, se arată amândouă și se cere alegerea
- ecranul confirmă crearea. O listă care se reîncarcă fără mesaj lasă omul să deducă — iar aia a ascuns trei zile un defect

**Refuzul, în orice caz de mai sus:** spune **ce** e greșit și **unde** se corectează, sub câmpul la care se referă — nu sub primul câmp al formularului.

### `PUT /tenants/{tenant_id}`

*garda `cere_rol` · rol:admin_firma*

*ce face: poate atinge, prin modul (PLAFON, nemasurat pe ruta): audit_log (INSERT) · firma_profil (INSERT/UPDATE) · tenants (INSERT/UPDATE) · user_tenants (INSERT) — prin `tenant_provisioning`*

**Ce trebuie să fie adevărat după:**

- [x] **CUI-ul unei firme cu declarații depuse nu se schimbă.** Se refuză, cu numărul declarațiilor. Un CUI schimbat rupe corespondența cu tot ce s-a depus, iar ANAF nu se poate corecta din aplicație
- dacă nu are declarații, schimbarea de CUI cere **reconfirmare la ANAF** — noul CUI e validat ca la creare
- schimbarea de denumire păstrează **denumirea veche cu perioada** în care a fost valabilă. Un document emis sub numele vechi trebuie să se poată explica
- denumirea nouă e unică în cabinet, ca la creare
- **ce s-a emis nu se rescrie.** Facturile, declarațiile și statele emise poartă identitatea de la momentul emiterii, nu pe cea de azi
- modificarea se consemnează: cine, când, de la ce la ce — pe fiecare câmp schimbat, nu global
- `user_tenants (INSERT)` la o rută de modificare e neașteptat — verifică ce leagă, și dacă o modificare poate crea o legătură nouă

**Iar întrebarea de fond, care decide restul:** de ce se poate schimba denumirea unei firme cu CUI validat la ANAF? Dacă numele vine din registru, singura schimbare legitimă e cea care urmează o schimbare la registru — iar atunci se reia validarea, nu se editează câmpul.

**Ce a observat Costin scriind sloturile.** **Trei dintre cele patru rute sunt ireversibile în feluri diferite**, iar ecranul nu spune care e care. Crearea consumă un CUI. Ștergerea distruge schema. Schimbarea identității rescrie ce s-a declarat sub numele vechi. Doar dezactivarea are drum de întoarcere — și e singura care nu pare periculoasă. **Două rute ating tabele neașteptate:** `activare` poate face `tenants (DELETE)`, iar `PUT` poate face `user_tenants (INSERT)`. Amândouă sunt plafon nemăsurat pe rută, deci pot fi artefacte ale instrumentului — dar merită verificate. **Iar întrebarea de fond a traseului**, pe care n-o pot decide singur: de ce se poate schimba denumirea unei firme cu CUI validat la ANAF? Dacă numele vine din registru, editarea liberă a câmpului e chiar cauza duplicatelor. Iar duplicatul a costat deja — pe el a căzut diagnosticul de la pasul 8 al probei R62.
