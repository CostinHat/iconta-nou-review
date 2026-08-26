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

*ce face: scrie declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [x] declarația intră în coadă **numai cu verdict de validare păstrat** — altfel ruta refuză și spune de ce
- rândul din coadă poartă: tip, perioadă, firmă, cine a pregătit, momentul
- nu se creează rând în `declaratii_depuse` la intrarea în coadă — depunerea nu s-a întâmplat

### `POST /coada/{coada_id}/aproba`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [x] cine aprobă e consemnat, și e diferit de cine a pregătit dacă patru ochi e activ **și** posibil
- dacă patru ochi e activ și imposibil (un singur validator), ruta refuză cu motivul, nu tace
- starea trece în „aprobată", nu direct în „depusă"

### `POST /coada/{coada_id}/depune`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [x] ruta refuză o declarație fără verdict de validare păstrat, sau cu verdict pe altă amprentă decât fișierul curent
- se scrie în `declaratii_depuse`: tip, perioadă, momentul, autorul autorizării, amprenta fișierului, indexul de la autoritate dacă există
- dacă indexul lipsește, starea nu e „confirmată" — e „nelămurită", conform P19
- declarația iese din coadă numai după ce rândul de depunere există

### `POST /coada/{coada_id}/respinge`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie declaratii_coada (INSERT/UPDATE) · declaratii_depuse (INSERT) — prin `coada_api`*

- [x] respingerea poartă **motivul**, obligatoriu
- declarația nu dispare din coadă — rămâne, cu starea „respinsă" și motivul vizibil
- cine a pregătit vede respingerea; nu se stinge prin ignorare

### `POST /declaratii/{tip}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: intoarce {avertismente, note_rezultat, operatiuni, tip, xml}*

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

*ce face: scrie declaratii_depuse (DELETE/INSERT) — prin `istoric_declaratii_import_api`*

- [x] același conținut ca la pasul de încărcare — ce s-a văzut la previzualizare e ce s-a salvat
- o a doua rulare cu același fișier nu dublează rândurile

### `POST /tenants/{tenant_id}/istoric-declaratii-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie declaratii_depuse (DELETE/INSERT) · migrare_status (INSERT) — prin `istoric_declaratii_import_api`, `migrare_api`*

- [x] fiecare declarație din fișier are un rând în `declaratii_depuse`, cu tip, perioadă și dată de depunere
- numărul de rânduri scrise = numărul de declarații din fișier, minus cele respinse, iar respinsele sunt numite
- un `DELETE/INSERT` nu lasă în urmă rânduri din import-ul anterior care nu mai sunt în fișier — sau, dacă le lasă, se spune care
- `migrare_status` marchează stratul ca parcurs, cu momentul

## T02 — Factura emisă — creare, contabilizare, ieșiri

*clasa MECANIC · 19 rute · 13 schimba date · 12 firme il pot exercita azi*

*citiri (nu schimba nimic): `/api/v1/firme/{tenant_id}/facturi`, `/tenants/{tenant_id}/facturi`, `/tenants/{tenant_id}/facturi-recurente`, `/tenants/{tenant_id}/facturi/numerotare`, `/tenants/{tenant_id}/facturi/{factura_id:int}`, `/tenants/{tenant_id}/facturi/{factura_id}/pdf`*

### `POST /api/v1/firme/{tenant_id}/facturi`

*garda `cere_api_key` · **fara rol***

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

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

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] **nu pot scrie verificarea fără să știu ce o deosebește de `/facturi/emite`.** Creează ciornă? Emite direct? De completat din cod
- dacă emite, se aplică verificările de la `emite`
- **completat din cod (26.08.2026): ce o deosebește de `/facturi/emite`.** `/facturi` cheamă `creeaza_factura(numar, data_emitere, directie, …)` — **numărul vine de la apelant**, iar `directie` poate fi `emisa` sau **`primita`**. E calea prin care se ÎNREGISTREAZĂ o factură care există deja (inclusiv una primită). `/facturi/emite` cheamă `emite_factura(…)` — **aplicația dă numărul din serie**, cere numele beneficiarului, are poarta „pleacă marfa acum?” și citește `platitor_tva` din `firma_profil`. E calea prin care se EMITE una nouă.
- starea implicită diferă, și e chiar **R14**: `creeaza_factura` pune `emisa`, `emite_factura` pune `de_preluat`. Două populații în aceeași firmă, iar starea nu se mai schimbă niciodată
- deci verificarea corectă pentru `/facturi` **nu** e cea de la `emite`: aici numărul e dat de om, deci se verifică **unicitatea în serie** și că nu creează goluri; la `emite` se verifică că numărul vine din serie

### `POST /tenants/{tenant_id}/facturi-recurente`

*garda `cere_context` · **fara rol***

*ce face: scrie facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [x] șablonul recurent nu emite nimic singur — emiterea trece prin `facturi/emite`, cu regulile ei
- modificarea unui șablon nu atinge facturile deja emise din el
- ștergerea nu atinge facturile emise; dacă șablonul are facturi, se spune câte
- data următoarei emiteri se recalculează la modificare, iar dacă ar cădea în trecut se refuză
- *(verificările sunt scrise de Costin o singura data, pentru toate trei rutele de sablon recurent)*

### `DELETE /tenants/{tenant_id}/facturi-recurente/{sid}`

*garda `cere_context` · **fara rol***

*ce face: scrie facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [x] șablonul recurent nu emite nimic singur — emiterea trece prin `facturi/emite`, cu regulile ei
- modificarea unui șablon nu atinge facturile deja emise din el
- ștergerea nu atinge facturile emise; dacă șablonul are facturi, se spune câte
- data următoarei emiteri se recalculează la modificare, iar dacă ar cădea în trecut se refuză

### `PUT /tenants/{tenant_id}/facturi-recurente/{sid}`

*garda `cere_context` · **fara rol***

*ce face: scrie facturi_recurente (DELETE/INSERT/UPDATE) — prin `facturi_recurente`*

- [x] șablonul recurent nu emite nimic singur — emiterea trece prin `facturi/emite`, cu regulile ei
- modificarea unui șablon nu atinge facturile deja emise din el
- ștergerea nu atinge facturile emise; dacă șablonul are facturi, se spune câte
- data următoarei emiteri se recalculează la modificare, iar dacă ar cădea în trecut se refuză
- *(verificările sunt scrise de Costin o singura data, pentru toate trei rutele de sablon recurent)*

### `POST /tenants/{tenant_id}/facturi/emite`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie articole (INSERT/UPDATE) · factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `facturi_api`, `stocuri_cv_api`*

- [x] factura primește **următorul număr din serie**, fără goluri; două emiteri simultane nu produc același număr
- exemplarul se îngheață cu amprenta; o regenerare ulterioară produce alt exemplar, nu îl rescrie pe primul
- nota contabilă generată respectă partida dublă, iar conturile vin din mapare, nu din literali
- mișcările de stoc au aceeași dată cu factura
- factura fără cod fiscal de partener se refuză — nu intră în D394 și nu se corelează în VIES

### `PUT /tenants/{tenant_id}/facturi/numerotare`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] schimbarea seriei sau a numărului de start **nu poate produce un număr deja folosit** — se refuză, cu numărul care ar fi intrat în conflict
- numerotarea nu se poate reduce sub ultimul număr emis
- schimbarea se consemnează: cine, când, de la ce la ce. E P15 — seria nu are goluri și nu se reia

### `DELETE /tenants/{tenant_id}/facturi/{factura_id}`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] **o factură emisă nu se șterge.** Se stornează. Ștergerea ar produce un gol în serie
- o factură cu notă contabilă nu se șterge — se rupe lanțul P14
- dacă ștergerea e permisă pe ciorne, verifică ce o deosebește de o factură emisă; iar dacă nu există distincția, aia e constatarea

### `POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Nota ciorna din factura (AI propune, contabilul valideaza) — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] nota produsă e **ciornă**, nu evidență validată — descrierea o spune, verifică structural
- propunerea de conturi vine din maparea corectată; nu se ghicește din denumire
- ciorna poartă legătura către factura din care a ieșit
- o factură contabilizată de două ori nu produce două note
- **fără rol, deși scrie în `inregistrari`** — R55, iar aici e cea mai vizibilă instanță
- **Măsurat 26.08.2026: nota E ciornă** — verificat pe `INSERT`-ul din corpul rutei, nu pe descriere. Deci nu produce evidență, iar poarta e la validare (`admin_firma` de azi). Din **40** de rute care scriu în `inregistrari_linii` în corpul lor, **36 scriu `ciorna`**; singurele trei care scriau `validata` direct — `amortizare`, `bonuri/{id}/aproba`, `horeca/raport-z` — au primit rol azi.

### `POST /tenants/{tenant_id}/facturi/{factura_id}/email`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`, `firma_profil_api`*

- [x] trimiterea e un **eveniment de predare**: cui, când, la ce adresă, cu ce atașament
- se trimite exemplarul emis, cu amprenta lui — nu o regenerare la momentul trimiterii
- o a doua trimitere e un al doilea eveniment, nu suprascrie primul
- eșecul trimiterii e o stare, nu o eroare pierdută: factura rămâne netrimisă și se vede

### `PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare`

*garda `cere_rol` · rol:admin_firma*

*ce face: F131: supapa per factura — scrie facturi (UPDATE) · firma_profil (UPDATE) — prin `scadentar`*

- [x] oprirea notificărilor pe o factură nu schimbă scadența și nu afectează calculul de întârziere
- starea se consemnează cu autorul — e o decizie despre relația cu clientul

### `POST /tenants/{tenant_id}/facturi/{factura_id}/storno`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] stornarea e un **document nou**, care o referă pe cea stornată. Factura originală rămâne, cu numărul ei
- suma stornată nu depășește suma facturii
- nota de stornare inversează exact nota originală — nu o șterge
- o factură deja stornată nu se stornează a doua oară

### `POST /tenants/{tenant_id}/facturi/{factura_id}/transforma`

*garda `cere_rol` · rol:admin_firma · scrie in facturi*

*ce face: Transforma proforma/aviz in factura fiscala (numerotare noua, nota se genereaza normal). — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) — prin `facturi_api`*

- [x] proforma sau avizul devine factură fiscală cu **numerotare nouă**, din seria de facturi, nu cu numărul proformei
- documentul original rămâne, cu starea „transformat" și legătura către factura rezultată
- nota contabilă se generează la transformare, nu la emiterea proformei — proforma nu e document contabil

## T03 — Statul de plată și fluturașul

*clasa MECANIC · 6 rute · 3 schimba date · 2 firme il pot exercita azi*

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

*ce face: corp: {salariat_id, an, luna} — scrie state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

- [x] corecția e **al doilea exemplar**, cu referință la primul. Primul rămâne
- diferența față de exemplarul corectat e vizibilă, pe fiecare cifră schimbată
- corecția nu poate atinge o lună închisă fără redeschidere consemnată

### `POST /tenants/{tenant_id}/stat-plata/emite`

*garda `cere_rol` · rol:admin_firma*

*ce face: corp: {an, luna} — scrie state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

- [x] statul se îngheață cu amprentă, exemplar numerotat, autor, moment
- cifrele emise nu se mai recalculează la citire; un recalcul care diferă produce contradicție vizibilă, nu rescriere
- emiterea e idempotentă: a doua apăsare produce **al doilea exemplar**, nu suprascrie primul
- pontajul trebuie confirmat; fără el, tichetele nu se acordă, iar statul o spune

### `POST /tenants/{tenant_id}/stat-plata/motiv`

*garda `cere_cabinet` · **fara rol***

*ce face: corp: {exemplar_id, motiv} — scrie state_plata (INSERT/UPDATE) — prin `stat_plata_emis`*

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

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] codul de indemnizație e din nomenclatorul oficial; unul din afară se refuză
- pentru codurile care cer CNP-ul persoanei îngrijite — 09, 17, 91, 92 — câmpul e obligatoriu la introducere, nu la generarea D112
- un certificat „în continuare" poartă seria, numărul și data celui inițial; fără ele se refuză
- perioada nu se suprapune cu alt certificat al aceluiași salariat
- stagiul de asigurare e verificat, sau codul e dintre cele exceptate — altfel se semnalează
- durata cumulată pe an nu depășește plafoanele: 183 de zile, 45 pentru codul 09, 45 pentru codul 17

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] **un certificat care a intrat într-un stat de plată emis nu se șterge** — se corectează prin exemplar nou
- ștergerea recalculează episodul: dacă certificatul șters era inițial, procentul celorlalte din episod se schimbă
- ștergerea unui certificat dintr-o lună declarată în D112 produce contradicție vizibilă

## T05 — Nota contabilă — de la document la registrul-jurnal

*clasa MECANIC · 28 rute · 24 schimba date · 17 firme il pot exercita azi*

*citiri (nu schimba nimic): `/api/v1/firme/{tenant_id}/balanta`, `/tenants/{tenant_id}/documente/balanta`, `/tenants/{tenant_id}/jurnal`, `/tenants/{tenant_id}/plan-conturi`*

### `POST /tenants/{tenant_id}/jurnal`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [x] nota respectă partida dublă la creare, nu la validare
- conturile există în plan — acum se refuză
- data notei e într-o perioadă deschisă
- documentul justificativ e cerut: felul, numărul, data. Fără el, nota nu se poate desface — P14
- **fără rol** — R55
- **RĂMÂNE fără rol, cu motivul măsurat (26.08.2026).** Citite la sursă, `jurnal_api.editeaza` și `.sterge` refuză orice notă care nu e `ciorna`, iar `creeaza` scrie tot `ciorna`. O ciornă **nu schimbă ce datorează firma** — deci criteriul lui Costin nu o prinde. Poarta e la validare, care de azi cere `admin_firma`.

### `DELETE /tenants/{tenant_id}/jurnal/{nota_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [x] o notă validată nu se șterge — se stornează. Ștergerea ar rupe lanțul către documentul justificativ
- ștergerea unei ciorne nu atinge documentul din care a ieșit
- **fără rol** — R55

### `PUT /tenants/{tenant_id}/jurnal/{nota_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

- [x] o notă **validată** nu se editează — se stornează
- editarea unei ciorne păstrează partida dublă
- editarea nu poate muta nota într-o perioadă închisă
- **fără rol** — R55

### `POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie ai_corectii (INSERT) · casa_operatiuni (DELETE) · extras_linii (UPDATE) · inregistrari (DELETE/INSERT/UPDATE) · inregistrari_linii (DELETE/INSERT) — prin `jurnal_api`*

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
- mișcările de stoc au aceeași dată cu nota
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-leasing`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, tip primire|rata|reziduala|operational, descriere?, cota?, + campuri pe tip: primire{valoare_capital, dobanda_totala, cont_imobilizare?}; rata{capital, doban — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] financiar sau operațional — cele două au tratamente contabile opuse. Verifică dacă ruta le distinge, sau presupune unul
- la leasing financiar, bunul intră ca imobilizare și se amortizează; rata se desface în principal și dobândă
- la operațional, rata e cheltuială integral
- dobânda din rată e separată de principal, nu topită în cheltuială
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

### `POST /tenants/{tenant_id}/nota-lichidare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie vanzare_activ|partaj, descriere?, + vanzare_activ{pret, valoare_bruta, amortizare_cumulata, conturi?, cota?}; partaj{capital_social, rezerve?, profi — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] lichidarea închide conturile; verifică ordinea: se sting datoriile, apoi se distribuie asociaților
- impozitul pe dividende se aplică la distribuirea din lichidare
- verifică dacă ruta permite lichidarea unei firme cu datorii nestinse
- **Masurat 26.08.2026, raspuns la intrebarea ta:** ruta CALCULEAZA. Toate cele 19 rute `nota-*` cheama un motor pur din `core/`, iar unde intervine cota o cer din REGISTRU (`cota_ceruta`/`common.cota`), nu din corpul cererii. Zero rute care doar scriu ce li se da. Deci verificarile scrise aici au ce sa verifice.

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

*ce face: Trimite o factura emisa in SPV (F126/F160) — scrie efactura_trimiteri (INSERT/UPDATE) — prin `efactura_send`*

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

*ce face: scrie extras_linii (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `reconciliere_api`*

- [x] fiecare tranzacție importată produce **o singură** linie de extras
- un extras importat de două ori nu dublează liniile — verifică pe numărul extrasului și pe conținut
- liniile importate poartă **sursa** (extras bancar) și gradul de certitudine
- potrivirea automată cu facturi e o **propunere**, nu un fapt: verifică dacă rezultatul e ciornă sau evidență
- soldul contului de bancă după import = soldul din extras

### `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie extras_linii (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `reconciliere_api`*

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

*clasa MECANIC · 2 rute · 1 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/stocuri/nir`*

### `POST /tenants/{tenant_id}/stocuri/nir`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · nir (INSERT) · nir_linii (INSERT) — prin `stocuri_api`*

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

*ce face: scrie casa_operatiuni (DELETE/INSERT) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [x] **soldul casei nu poate deveni negativ** — o plată peste sold se refuză
- plafonul de plăți în numerar către o persoană juridică se verifică pe zi și pe operațiune
- plafonul de încasări în numerar de la o persoană se verifică la fel
- operațiunea produce o linie în registrul de casă, cu numărul curent
- data operațiunii e într-o perioadă deschisă

### `DELETE /tenants/{tenant_id}/casa/operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie casa_operatiuni (DELETE/INSERT) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [x] **o operațiune de casă dintr-o zi închisă nu se șterge** — registrul de casă se închide zilnic
- ștergerea recalculează soldul; dacă soldul ar deveni negativ la vreo operațiune ulterioară, se refuză
- numerotarea nu se reia după ștergere — rămâne golul, sau se renumerotează? Verifică și spune care
- dacă operațiunea are notă validată, se refuză
- **completat din cod (26.08.2026): numerotarea casei nu se rupe, fiindcă NU EXISTĂ.** `casa_operatiuni` are coloanele `id, data, tip, categorie, document, partener, cui, suma, inregistrare_id, creat_la` — **niciun număr curent**. Iar `casa.registru_casa()` calculează doar **soldul rulant**, nu un rând numerotat. Deci ștergerea nu poate lăsa un gol într-o serie care nu există
- **ce face ștergerea, verificat:** `casa_api.sterge` șterge operațiunea **și nota legată**, dar **doar dacă nota e ciornă** — pe una validată refuză cu *„nota legată e validată; nu se mai poate șterge”*. Deci lanțul către evidență nu se rupe
- **constatarea de fond:** Registrul de casă (cod 14-4-7A, OMFP 2634/2015) e un registru obligatoriu, iar registrele obligatorii poartă număr curent — la fel ca Registrul-jurnal 14-1-1, unde numărul curent a fost **derivat la citire** pe 24.08 după confruntarea cu norma. **N-am confruntat cu actul** dacă 14-4-7A îl cere; dacă îl cere, e aceeași clasă și aceeași reparație
- verificarea care rămâne: după ștergere, soldul rulant al zilei se recalculează, iar soldul de la sfârșitul zilei nu depășește plafonul de casierie

## T10 — Inventarierea

*clasa MECANIC · 5 rute · 1 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/d406-active`, `/tenants/{tenant_id}/d406-stocuri`, `/tenants/{tenant_id}/rip/inventar/{an}`, `/tenants/{tenant_id}/verificare-stocuri`*

### `POST /tenants/{tenant_id}/stocuri/inventar`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [x] inventarul compară **stocul faptic** cu cel scriptic; diferența e plus sau minus, nu se ajustează tăcut
- fiecare diferență produce o mișcare de stoc, iar suma mișcărilor = diferența totală
- minusul se compară cu limita de perisabilitate pe categorie; ce depășește e nedeductibil
- inventarul se face la o dată, iar mișcările de după acea dată nu-l afectează
- un articol care nu apare în listă rămâne cu stocul scriptic sau se consideră zero? Verifică — diferența e mare

## T11 — Închiderea lunii

*clasa MECANIC · 6 rute · 4 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi/perioada`, `/tenants/{tenant_id}/perioade-blocate`*

### `POST /tenants/{tenant_id}/facturi/perioada/confirma`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Declara luna INCHISA pe facturi: evidenta ei devine autoritativa, iar semaforul se poate sprijini pe ea cand spune ca o declaratie nu se datoreaza*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/perioada/redeschide`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Redeschide luna (o corectie de facturi cere redeschiderea)*

- [ ] 

### `DELETE /tenants/{tenant_id}/perioade-blocate`

*garda `cere_rol` · rol:admin_firma · scrie in perioade_blocate*

*ce face: scrie perioade_blocate (DELETE)*

- [x] redeschiderea e act consemnat, cu **motiv obligatoriu** — P15
- redeschiderea marchează documentele emise din acea perioadă ca fiind **sub rezervă**
- declarațiile depuse pentru perioada redeschisă produc contradicție vizibilă, nu se rescriu
- o perioadă nu se poate redeschide dacă cea următoare e închisă
- **redeschiderea nu consemnează nimic** — vezi pasul de închidere. `DELETE` șterge rândul, deci nu rămâne nici cine a redeschis, nici când, nici de ce. Interdicția 36 + P15
- verificarea care ar trebui să fie adevărată după pas — și azi nu poate fi: **există o urmă care spune că perioada a fost închisă de X la momentul T și redeschisă de Y la momentul U, cu motivul Z**

### `POST /tenants/{tenant_id}/perioade-blocate`

*garda `cere_rol` · rol:admin_firma · scrie in perioade_blocate*

*ce face: scrie perioade_blocate (INSERT)*

- [x] închiderea e un act deliberat, cu **autor și moment** consemnate
- după închidere, nicio scriere în perioada aceea nu mai trece — verificat pe toate cele 39 de operațiuni, nu doar pe cele testate
- închiderea verifică întâi că perioada e coerentă: balanța se închide, notele sunt validate, nu există ciorne. Sau, dacă nu verifică, se spune ce nu verifică
- o perioadă nu se poate închide dacă cea anterioară e deschisă
- **verificat la sursă (26.08.2026): NU verifică nimic. Ai presupus corect, și e mai rău.** `POST /perioade-blocate` face **un singur `INSERT`** în `perioade_blocate (an, luna, blocat_de)`. Nicio verificare de ciorne rămase, de echilibru, de orfani. **Măsurat azi: dacă s-ar închide luna curentă pe `tenant_013`, ar rămâne 5 ciorne închise înăuntru** (`tenant_003`: 1)
- **și sunt DOUĂ acte de închidere, dintre care doar unul verifică.** `core/inchidere_luna.py` (21.08) verifică un blocaj real — e-Facturi primite și neînregistrate — și **refuză motivat**, iar o modificare **de-confirmă automat**. Dar el scrie în `perioada`, pe domeniul `facturi`: e o **afirmație** despre completitudine. **Poarta care oprește scrierile e `perioade_blocate`** (citită de `_cere_luna_deschisa` la fiecare notă) — și aceea nu verifică nimic. **Verificarea există, dar nu e pe poartă.**
- **redeschiderea nu lasă urmă.** `DELETE /perioade-blocate` **șterge rândul**: dispare și `blocat_de`, și `blocat_la`, și faptul că perioada a fost vreodată închisă. Tabela n-are coloană de motiv. Asta e **interdicția 36** („o redeschidere de perioadă fără motiv consemnat”) și **P15** („redeschiderea e act consemnat, cu motiv”) — direct, nu prin analogie
- **cifra care încadrează:** o singură perioadă e blocată azi, pe toate cele 17 firme (`tenant_001`). Deci efectul n-a fost produs — e prag 2, cauză unică, dovedită

## T12 — Închiderea anului și situațiile financiare

*clasa PARTIAL · 4 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/s1003-xml`, `/tenants/{tenant_id}/s1005-xml`*

### `POST /tenants/{tenant_id}/s1003-valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie artefacte_produse (INSERT) — prin `artefacte`*

- [x] aceleași ca mai sus
- **plus:** un artefact produs pe regimul greșit e conform ca formă și fals ca fond. Ruta refuză, sau spune că nu poate verifica regimul

### `POST /tenants/{tenant_id}/s1005-valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie artefacte_produse (INSERT) — prin `artefacte`*

- [x] artefactul se păstrează cu: conținutul, momentul, autorul, amprenta, numărul exemplarului
- verdictul validării se păstrează cu artefactul, nu separat
- **verificare de fond:** situațiile financiare cerute depind de categoria de mărime a firmei. Dacă aceasta nu există ca dimensiune, ruta nu poate ști ce datorează firma — se declară, nu se presupune

## T13 — Trecerea de regim fiscal

*clasa MECANIC · 8 rute · 4 schimba date · 17 firme il pot exercita azi*

*citiri (nu schimba nimic): `/migrare/vector`, `/tenants/{tenant_id}/firma-profil`, `/tenants/{tenant_id}/firma-profil/date`, `/tenants/{tenant_id}/vector`*

### `POST /tenants/{tenant_id}/firma-profil/date`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie firma_profil (UPDATE) — prin `firma_profil_api`*

- [ ] 

### `POST /tenants/{tenant_id}/firma-profil/model`

*garda `cere_context` · **fara rol***

*ce face: scrie firma_profil (UPDATE) — prin `firma_profil_api`*

- [ ] 

### `POST /tenants/{tenant_id}/firma-profil/regim-tva`

*garda `cere_context` · **fara rol** · scrie in firma_profil*

*ce face: scrie firma_profil (UPDATE) — prin `firma_profil_api`*

- [ ] 

### `POST /tenants/{tenant_id}/vector`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie firma_profil (INSERT/UPDATE) · migrare_status (INSERT) — prin `firma_profil_api`, `migrare_api`, `vector_fiscal_api`*

- [ ] 

## T14 — Preluarea unei firme

*clasa MECANIC · 32 rute · 21 schimba date · 5 firme il pot exercita azi*

*citiri (nu schimba nimic): `/migrare/asociati`, `/migrare/istoric-declaratii`, `/migrare/mijloace-fixe`, `/migrare/parteneri`, `/migrare/plan-conturi`, `/migrare/salariati`, `/migrare/solduri`, `/migrare/status`, `/migrare/straturi`, `/tenants/{tenant_id}/parteneri`, `/tenants/{tenant_id}/solduri`*

### `POST /control-fiscal/{tenant_id}/audit-preluare`

*garda `cere_rol` · rol:admin_firma*

*ce face: F183: audit de PRELUARE firma — coerenta INTERNA a pachetului preluat de la contabilul anterior (balanta echilibrata, defalcare parteneri vs sintetic, solduri fiscale vs  — scrie artefacte_produse (INSERT) — prin `artefacte`*

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

*ce face: Creează câte un tenant pentru fiecare firmă selectată — scrie firma_profil (INSERT/UPDATE) · migrare_status (INSERT) · tenants (INSERT/UPDATE) · user_tenants (INSERT) — prin `migrare_api`, `tenant_provisioning`*

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

*ce face: Marchează un strat 'gata' sau 'in_lucru' (cu notă obligatorie la in_lucru). — scrie migrare_status (INSERT) — prin `migrare_api`*

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

*ce face: scrie articole (INSERT) · miscari_stoc (INSERT) — prin `articole_import_api`*

- [x] ce s-a văzut la previzualizare e ce s-a importat — același număr, aceleași articole
- articolele cu cod duplicat în fișier se semnalează, nu se suprascriu între ele
- fiecare articol importat cu stoc inițial produce o mișcare de stoc, iar suma mișcărilor = stocul declarat
- un import repetat cu același fișier nu dublează nici articolele, nici mișcările

### `POST /tenants/{tenant_id}/articole-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT) · miscari_stoc (INSERT) — prin `articole_import_api`*

- [x] **previzualizarea scrie în stoc?** Dacă `articole` și `miscari_stoc` se scriu la încărcare, nu e previzualizare — e import. Verifică și spune care e
- articolele cu cod duplicat în fișier se semnalează, nu se suprascriu între ele

### `POST /tenants/{tenant_id}/asociati-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie asociati (DELETE/INSERT) — prin `asociati_import_api`*

- [x] `DELETE/INSERT` — verifică ce se întâmplă cu asociații care nu mai sunt în fișier: se șterg, iar aia e o schimbare de structură a firmei, nu un import

### `POST /tenants/{tenant_id}/asociati-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie asociati (DELETE/INSERT) · migrare_status (INSERT) — prin `asociati_import_api`, `migrare_api`*

- [x] previzualizarea nu salvează
- suma procentelor de participare = 100, sau se semnalează

### `POST /tenants/{tenant_id}/mijloace-fixe-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie mijloace_fixe (DELETE/INSERT) — prin `mijloace_fixe_import_api`*

- [x] ce s-a văzut la previzualizare e ce s-a importat
- amortizarea cumulată la data preluării nu depășește valoarea de intrare
- un mijloc fix complet amortizat intră cu valoare rămasă zero, nu se respinge

### `POST /tenants/{tenant_id}/mijloace-fixe-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie migrare_status (INSERT) · mijloace_fixe (DELETE/INSERT) — prin `migrare_api`, `mijloace_fixe_import_api`*

- [x] **nu scrie nimic** — verificat structural, nu prin absența efectului
- durata de amortizare a fiecărui mijloc fix e confruntată cu catalogul; cele din afara intervalului se numesc, cu rândul lor
- valoarea de intrare sub pragul de mijloc fix se semnalează — e obiect de inventar, nu mijloc fix

### `POST /tenants/{tenant_id}/parteneri`

*garda `cere_rol` · rol:admin_firma*

*ce face: Salveaza soldurile partenerilor unei firme (inlocuieste ce era). — scrie solduri_parteneri (DELETE/INSERT) — prin `solduri_parteneri_api`*

- [x] ce s-a văzut la previzualizare e ce s-a salvat
- divergența față de balanță, dacă a existat, rămâne vizibilă după salvare — nu se stinge prin acceptare

### `POST /tenants/{tenant_id}/parteneri/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parseaza fisierul de parteneri si intoarce preview + verificare coerenta vs balanta. — scrie migrare_status (INSERT) · solduri_parteneri (DELETE/INSERT) — prin `migrare_api`, `solduri_parteneri_api`*

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

*ce face: Import registru incasari-plati la preluarea unui PFA — scrie migrare_status (INSERT) · rip_operatiuni (INSERT) — prin `migrare_api`, `rip_migrare_api`*

- [x] **nu pot scrie verificarea fără să știu ce e RIP.** Registrul de inventar și producție? Registrul imobilizărilor? De completat din cod, ca la `retete-import`
- **completat din cod (26.08.2026), cum ai cerut** — **RIP = Registrul de Încasări și Plăți** (partidă simplă, PFA). `core/rip_migrare_api.py`: partida simplă **nu are balanță de deschidere**; registrul e CRONOLOGIC, deci la preluare se importă operațiunile anului curent de la 1 ianuarie până la data preluării, iar soldul e implicit din sumă, nu un rând
- operațiunile importate intră cu `status='validata'` — sunt istoric preluat, nu ciornă de verificat. Verificarea care contează: **preluarea nu certifică** corectitudinea contabilului anterior, iar limita e declarată în antetul modulului
- sumele se citesc cu parserul din `solduri_api` (paranteze = negativ, format contabil RO/EN, sufixe RON/lei) — un singur loc pentru interpretarea sumelor
- numărul de operațiuni importate = numărul de linii din fișier minus cele respinse, iar respinsele sunt numite cu rândul lor

### `POST /tenants/{tenant_id}/salariati-import`

*garda `cere_rol` · rol:admin_firma*

*ce face: Importa salariatii cu CNP valid (upsert pe CNP) — scrie salariati (INSERT) — prin `salariati_import_api`*

- [x] upsert-ul nu suprascrie date existente fără să spună ce a schimbat
- un salariat existent cu alt nume la același CNP e o divergență, nu o actualizare tăcută

### `POST /tenants/{tenant_id}/salariati-import/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parseaza exportul de salariati si intoarce preview cu validare CNP (nu salveaza). — scrie migrare_status (INSERT) · salariati (INSERT) — prin `migrare_api`, `salariati_import_api`*

- [x] **previzualizarea nu salvează** — aceeași verificare structurală ca la solduri
- CNP-urile nevalide se numesc, cu rândul lor din fișier
- un CNP valid dar implauzibil ca dată de naștere se semnalează separat

### `POST /tenants/{tenant_id}/solduri`

*garda `cere_rol` · rol:admin_firma*

*ce face: Salvează soldurile inițiale ale unei firme (înlocuiește ce era). — scrie plan_conturi (INSERT) · solduri_initiale (DELETE/INSERT) — prin `solduri_api`*

- [x] ce s-a văzut la previzualizare e ce s-a salvat
- „înlocuiește ce era" — verifică ce se întâmplă cu soldurile anterioare: se șterg, sau se păstrează ca versiune?
- conturile din balanță care nu există în plan se creează sau se semnalează — nu se ignoră

### `POST /tenants/{tenant_id}/solduri/incarca`

*garda `cere_cabinet` · **fara rol***

*ce face: Parsează o balanță și întoarce preview (nu salvează). — scrie migrare_status (INSERT) · plan_conturi (INSERT) · solduri_initiale (DELETE/INSERT) — prin `migrare_api`, `solduri_api`*

- [x] **previzualizarea nu salvează** — ruta spune că întoarce preview; verifică structural că nu scrie în `solduri_initiale`
- dacă totuși scrie (numele tabelelor sugerează că da), atunci previzualizarea nu e previzualizare, iar aia e o constatare
- balanța încărcată **se închide**: total debit = total credit. Dacă nu, se spune, nu se salvează tăcut

## T15 — Salariatul — angajare, contract, adeverință, REGES

*clasa MANUAL · 17 rute · 12 schimba date · 8 firme il pot exercita azi*

*citiri (nu schimba nimic): `/contracte/marcaje`, `/cor`, `/tenants/{tenant_id}/contracte/sabloane`, `/tenants/{tenant_id}/salariati`, `/tenants/{tenant_id}/salariati/{salariat_id}`*

### `POST /tenants/{tenant_id}/contracte/genereaza`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

- [x] contractul generat se păstrează cu momentul, autorul, amprenta, numărul exemplarului
- toate marcajele din șablon sunt înlocuite; unul rămas necompletat oprește generarea, nu produce un contract cu paranteze
- datele din contract coincid cu fișa salariatului la data generării, nu cu cea de azi

### `POST /tenants/{tenant_id}/contracte/sabloane`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

- [x] șablonul salvat conține marcajele declarate; unul necunoscut se semnalează la salvare, nu la generare
- un șablon cu același nume nu se suprascrie tăcut

### `DELETE /tenants/{tenant_id}/contracte/sabloane/{sid}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie contracte_sabloane (DELETE/INSERT/UPDATE) — prin `contracte_api`*

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

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] CNP-ul trece cifra de control; unul care nu trece se refuză cu motivul, nu se salvează
- un CNP care există deja în firmă se refuză — nu se creează al doilea salariat cu același CNP
- data angajării nu e în viitor față de perioada deschisă
- salariul de bază nu e sub minimul aplicabil la data angajării, proratat cu norma. Dacă e, se refuză cu cifra minimului

### `DELETE /tenants/{tenant_id}/salariati/{salariat_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

- [x] **un salariat cu stat de plată emis nu se șterge.** Se marchează încetat, cu data. Ștergerea ar rupe lanțul către documentele emise
- dacă ștergerea e permisă, verifică ce rămâne în urmă: fluturași, note contabile, rânduri în D112 deja depuse
- încetarea se propagă în REGES — sau, dacă nu, se spune

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie concedii_medicale (DELETE/INSERT/UPDATE) · pontaj (DELETE) · salariati (DELETE/INSERT/UPDATE) · salariu_istoric (DELETE) — prin `salariati_api`*

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

*ce face: [F133 Faza 2a] beneficiu one-off pe luna (vacanta/cadou/cultural) — scrie beneficii_lunare (DELETE/INSERT) — prin `beneficii_api`*

- [x] beneficiul intră cu perioada lui, nu cu „de acum înainte"
- plafonul neimpozabil aplicabil e cel de la data lunii, nu de la data introducerii
- ce depășește plafonul devine venit impozabil, iar partea impozabilă e vizibilă separat — nu se topește în brut

## T16 — Pontajul

*clasa MECANIC · 4 rute · 2 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/salariati/{salariat_id}/pontaj`, `/util/zile-lucratoare`*

### `POST /tenants/{tenant_id}/pontaj/confirma`

*garda `cere_rol` · rol:admin_firma*

*ce face: [cap.23] Confirma pontajul lunii -> devine AUTORITATIV pentru salarizare (tichete pe zile efectiv lucrate)*

- [ ] 

### `PUT /tenants/{tenant_id}/salariati/{salariat_id}/pontaj`

*garda `cere_context` · **fara rol***

*ce face: F135: seteaza starea unei zile (stare goala/prezent = sterge exceptia). — scrie pontaj (DELETE/INSERT) — prin `pontaj`*

- [ ] 

## T17 — Plata salariilor — fișierul către bancă

*clasa PARTIAL · 2 rute · 1 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/plata-salarii-preview`*

### `POST /tenants/{tenant_id}/plata-salarii-fisier`

*garda `cere_rol` · rol:admin_firma*

*ce face: [F134] Fisierul SEPA/ISO 20022 pain.001.001.03 de plata a salariilor NET pe card (download) — scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

## T18 — Chitanța și încasarea

*clasa MANUAL · 6 rute · 3 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/public/plata/{ref}`, `/tenants/{tenant_id}/chitante`, `/tenants/{tenant_id}/chitante/{chitanta_id}/pdf`*

### `POST /public/plata/{ref}/confirma`

*garda `FARA GARDA` · **fara rol***

*ce face: scrie facturi (UPDATE) — prin `plati`*

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

*ce face: Emite chitanta (cod 14-4-1, Ordin 2634/2015) pentru incasare in numerar: numerotare pe serie per firma + operatiune in Registrul de casa prin casa_api (5311=4111, nota ci — scrie casa_operatiuni (DELETE/INSERT) · chitante (INSERT) · facturi (UPDATE) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [x] chitanța se păstrează cu numărul exemplarului, momentul, autorul, amprenta
- **numerotarea nu are goluri și nu se reia** — o chitanță anulată își păstrează numărul
- suma chitanței nu depășește soldul neîncasat al facturii la care se leagă
- dacă nu se leagă de nicio factură, se spune la ce se leagă

### `POST /tenants/{tenant_id}/facturi/{factura_id}/link-plata`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie facturi (UPDATE) — prin `plati`*

- [x] link-ul poartă suma exactă a facturii, nu una editabilă de plătitor
- link-ul expiră; expirarea e o stare, nu o eroare
- un al doilea link pe aceeași factură invalidează primul, sau se refuză — nu coexistă două

## T19 — Scadențarul și notificările de scadență

*clasa MECANIC · 2 rute · 1 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/scadentar`*

### `PUT /tenants/{tenant_id}/scadentar/opt-in`

*garda `cere_rol` · rol:admin_firma*

*ce face: F131: activeaza/dezactiveaza notificarile email de scadenta pt firma (default OFF). — scrie facturi (UPDATE) · firma_profil (UPDATE) — prin `scadentar`*

- [ ] 

## T20 — Mișcarea de stoc — intrare, ieșire, transfer, reclasificare

*clasa MECANIC · 12 rute · 7 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/stocuri/analitica`, `/tenants/{tenant_id}/stocuri/articole`, `/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa`, `/tenants/{tenant_id}/stocuri/barcode/{cod}`, `/tenants/{tenant_id}/stocuri/locatii`*

### `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/descarcare`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · nir (INSERT) · nir_linii (INSERT) — prin `stocuri_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/iesire`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/intrare`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/reclasificare`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

### `POST /tenants/{tenant_id}/stocuri/transfer`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie articole (INSERT/UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) — prin `stocuri_cv_api`*

- [ ] 

## T21 — Rețeta și producția

*clasa MECANIC · 9 rute · 7 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/produse`, `/tenants/{tenant_id}/retete`*

### `POST /tenants/{tenant_id}/produse`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [ ] 

### `POST /tenants/{tenant_id}/produse/potriveste`

*garda `cere_context` · **fara rol***

*ce face: scrie produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/produse/{produs_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/produse/{produs_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie produse (DELETE/INSERT/UPDATE) — prin `produse_api`*

- [ ] 

### `POST /tenants/{tenant_id}/retete`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [ ] 

### `POST /tenants/{tenant_id}/retete/descarca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/retete/{reteta_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT) · miscari_stoc (INSERT) · retete (DELETE/INSERT/UPDATE) · retete_linii (DELETE/INSERT) — prin `retete_api`*

- [ ] 

## T22 — Mijlocul fix și amortizarea

*clasa MECANIC · 3 rute · 2 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/mijloace-fixe`*

### `POST /tenants/{tenant_id}/amortizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Genereaza nota de amortizare lunara: 6811 = cont_amortizare, per MF activ. — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/reevaluare-imobilizare`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, operatie reevaluare|surplus, + reevaluare{mijloc_fix_id, valoare_justa, sold_105_activ?, pierdere_655_anterioara?} | surplus{suma}} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

## T23 — Bonul de la client — portalul și decontul

*clasa MECANIC · 9 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/portal/bon/{bon_id}/imagine/{n}`, `/tenants/{tenant_id}/bonuri/de-verificat`, `/tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate`, `/tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}`*

### `POST /portal/bon`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Extrage datele bonului cu AI si salveaza ca DRAFT (status='extras') + pozele pe disc — scrie bonuri (DELETE/INSERT)*

- [ ] 

### `DELETE /portal/bon/{bon_id}`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Clientul reface poza -> draftul (status='extras') si pozele lui se sterg. — scrie bonuri (DELETE)*

- [ ] 

### `POST /portal/bon/{bon_id}/confirma`

*garda `cere_context` · **fara rol** · scrie in bonuri*

*ce face: Clientul confirma ca poza e intreaga si lizibila -> bonul intra la contabil. — scrie bonuri (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/aproba`

*garda `cere_cabinet` · **fara rol** · scrie in bonuri, inregistrari, inregistrari_linii*

*ce face: scrie bonuri (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/bonuri/{bon_id}/stinge`

*garda `cere_rol` · rol:admin_firma · scrie in bonuri, facturi*

*ce face: Chitanta certificata de contabil: plata furnizor prin Registrul de casa (casa_api.adauga -> 401=5311 ciorna + operatiune casa + verificare plafon) — scrie bonuri (UPDATE) · casa_operatiuni (DELETE/INSERT) · facturi (UPDATE) · inregistrari (DELETE/INSERT) · inregistrari_linii (INSERT) — prin `casa_api`*

- [ ] 

## T24 — Bonul fiscal și raportul Z (AMEF, horeca)

*clasa MECANIC · 2 rute · 2 schimba date · nu se poate sti din date*

### `POST /tenants/{tenant_id}/horeca/import-amef`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Upload p7b/XML AMEF (OPANAF 146/2018 II.7) -> nota Raport Z CIORNA — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

### `POST /tenants/{tenant_id}/horeca/raport-z`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

## T25 — Comanda din magazinul online (WooCommerce)

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

*ce face: scrie facturi (UPDATE) · firma_profil (UPDATE) — prin `woocommerce`*

- [x] fiecare comandă sincronizată produce **o singură** factură; o a doua rulare nu dublează
- cota de TVA vine din articol sau din configurație — **nu se ghicește din denumire**
- comenzile care nu s-au putut transforma în factură se numesc, cu motivul; nu se sar tăcut
- ultima sincronizare reușită se păstrează, ca următoarea să știe de unde continuă

## T26 — Registratura

*clasa MECANIC · 2 rute · 1 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/registratura`*

### `POST /tenants/{tenant_id}/registratura`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie registratura (INSERT) — prin `registratura_api`*

- [ ] 

## T27 — e-Transport

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

*ce face: Trimite notificarea UIT in SPV (F121): genereaza XML + trimite() cu PORTI in ordine (garda de timp -> idempotency -> validare pe TEST -> upload) — scrie etransport_trimiteri (INSERT/UPDATE) — prin `etransport_send`*

- [x] cele patru porți rulează **în ordine**: garda de timp → idempotență → validare pe TEST → încărcare. O poartă sărită e un defect, nu o optimizare
- codul UIT primit se păstrează; fără el, starea e „nelămurită"
- garda de timp refuză o trimitere după termenul legal — și spune care e termenul
- idempotența e pe conținut, nu pe moment: același transport trimis de două ori e prins chiar dacă a trecut timp

## T28 — Operațiunile intracomunitare, VIES și Intrastat

*clasa MECANIC · 10 rute · 5 schimba date · 2 firme il pot exercita azi*

*citiri (nu schimba nimic): `/public/verifica-cui/{cui}`, `/tenants/{tenant_id}/d390-clasificare`, `/tenants/{tenant_id}/intrastat-praguri`, `/tenants/{tenant_id}/verifica-cui/{cui}`, `/tenants/{tenant_id}/verifica-vies`*

### `POST /tenants/{tenant_id}/achizitie-ic`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: AIC bunuri/servicii primite (art — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `facturi_api`*

- [ ] 

### `POST /tenants/{tenant_id}/d390-clasificare/manual`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga linie pur manuala: {an, luna, tip, tara, cod, den, baza}. — scrie d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/d390-clasificare/manual/{mid}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/d390-clasificare/reclasificare`

*garda `cere_cabinet` · **fara rol***

*ce face: Override tip pe o operatiune auto: {an, luna, directie, tara, cod, tip}. — scrie d390_manual (DELETE/INSERT) · d390_reclasificare (DELETE/INSERT) — prin `d390_clasificare_api`*

- [ ] 

### `POST /tenants/{tenant_id}/vanzare-ic`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: LIC bunuri (art — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [ ] 

## T29 — Regimurile speciale de TVA — marjă, aur, agricultori, taxare inversă

*clasa MECANIC · 11 rute · 10 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/jurnal-marja`*

### `POST /tenants/{tenant_id}/achizitie-agricultor`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare (fara taxa), cont_cheltuiala, agricultor_in_registru, agricultor?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] compensația în cotă forfetară se calculează pe cota în vigoare la data operațiunii
- agricultorul e verificat că e în regimul special — altfel e o achiziție obișnuită
- compensația plătită e deductibilă la cumpărător; verifică unde ajunge în D300

### `POST /tenants/{tenant_id}/achizitie-necorporala`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii, mijloace_fixe*

*ce face: corp: {data, denumire, valoare (fara TVA), tip software|licenta|brevet| dezvoltare|constituire, dnf_luni?, cota?, cod?} — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) · mijloace_fixe (INSERT) — prin `facturi_api`*

- [x] durata normală de funcționare vine din catalog pentru tipul respectiv; `dnf_luni` din corp nu o poate coborî sub minim
- valoarea sub pragul de imobilizare nu produce mijloc fix — e cheltuială. Verifică pragul la data operațiunii
- rândul din `mijloace_fixe` și nota din `inregistrari` au aceeași valoare de intrare
- amortizarea începe din luna următoare punerii în funcțiune, nu din luna achiziției

### `POST /tenants/{tenant_id}/achizitie-neinregistrat`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: Achizitie de la persoana fizica NEINREGISTRATA in scop TVA -> op N in D394 (pct.216 tip_partener=2) — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `facturi_api`*

- [x] operațiunea apare în D394 ca tip N, cu `tip_partener=2` — verificat pe declarația generată, nu pe intenția din cod
- persoana fizică nu are cod fiscal, deci nu se cere; dar se cere o identificare, altfel operațiunea n-are partener
- TVA-ul nu se deduce — achiziția de la neînregistrat nu poartă TVA deductibilă
- dacă atinge stocul prin modul, mișcarea de stoc are aceeași dată cu nota

### `POST /tenants/{tenant_id}/achizitie-taxare-inversa`

*garda `cere_rol` · rol:admin_firma · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, categorie, valoare (fara TVA), cont_destinatie, cota?, furnizor_platitor_tva, descriere?} — scrie factura_linii (INSERT) · facturi (DELETE/INSERT/UPDATE) · firma_profil (UPDATE) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `facturi_api`*

- [x] bunul sau serviciul e din lista art. 331 — altfel taxarea inversă nu se aplică
- pragul de 22.500 lei pentru telefoane, tablete, laptopuri, console e verificat pe factură, nu pe operațiune
- TVA-ul se înregistrează simultan ca deductibil și colectat, iar cele două se anulează în decont
- furnizorul e înregistrat în scopuri de TVA — altfel regimul nu se aplică

### `POST /tenants/{tenant_id}/export-extracomunitar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare, tara_client, dovada_export, cont_venit?, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] exportul e scutit cu drept de deducere; nu se colectează TVA
- scutirea cere **dovada exportului** — declarația vamală de export. Fără ea, operațiunea nu e scutită, iar ruta primește `dovada_export` ca text liber
- verifică ce se întâmplă când `dovada_export` lipsește sau e o frază: se refuză, sau se scutește pe încredere?
- țara clientului e din afara UE — o țară din UE face operațiunea livrare intracomunitară, nu export
- **fără rol, deși scrie evidență** — R55

### `POST /tenants/{tenant_id}/import-extracomunitar`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: corp: {data, valoare_vamala (RON), procent_taxa_vamala?, accize?, accesorii?, cota?, certificat_amanare?, cont_destinatie, descriere?} — scrie inregistrari (INSERT) · inregistrari_linii (INSERT)*

- [x] baza de TVA la import = valoarea vamală + taxa vamală + accize + accesorii până la primul loc de destinație. Verifică pe cifre, nu pe formulă
- cu certificat de amânare, TVA-ul nu se plătește în vamă: se înregistrează simultan colectat și deductibil, iar cele două se anulează în decont
- fără certificat, TVA-ul plătit în vamă e deductibil pe baza declarației vamale, nu a facturii furnizorului
- cota aplicată e cea de la data operațiunii, cerută din registru
- **fără rol, deși scrie evidență** — R55

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

*clasa MECANIC · 2 rute · 2 schimba date · nu se poate sti din date*

### `POST /tenants/{tenant_id}/decontare-valuta`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Incasare creanta / plata datorie in valuta cu diferenta de curs 665/765 — scrie curs_bnr_zilnic (INSERT) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `curs_bnr`*

- [ ] 

### `POST /tenants/{tenant_id}/reevaluare-valuta`

*garda `cere_cabinet` · **fara rol** · scrie in inregistrari, inregistrari_linii*

*ce face: Reevaluare lunara solduri valuta (OMFP 1802 pct — scrie curs_bnr_zilnic (INSERT) · inregistrari (INSERT) · inregistrari_linii (INSERT) — prin `curs_bnr`*

- [ ] 

## T31 — Completările manuale la o declarație (D300, D301)

*clasa MECANIC · 6 rute · 4 schimba date · 3 firme il pot exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/d300-manual`, `/tenants/{tenant_id}/d301-operatiuni`*

### `POST /tenants/{tenant_id}/d300-manual`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga/actualizeaza un rand manual D300: {an, luna, rand, baza, tva, descriere}. — scrie d300_manual (DELETE/INSERT) — prin `d300_manual_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/d300-manual/{rid}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie d300_manual (DELETE/INSERT) — prin `d300_manual_api`*

- [ ] 

### `POST /tenants/{tenant_id}/d301-operatiuni`

*garda `cere_cabinet` · **fara rol***

*ce face: Adauga o operatiune: {an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, cota}. — scrie d301_operatiuni (DELETE/INSERT) — prin `d301_operatiuni_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/d301-operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie d301_operatiuni (DELETE/INSERT) — prin `d301_operatiuni_api`*

- [ ] 

## T32 — Registrul de încasări și plăți (partida simplă)

*clasa MECANIC · 7 rute · 5 schimba date · nicio firma nu-l poate exercita azi*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/rip/d212/{an}`, `/tenants/{tenant_id}/rip/registru`*

### `POST /tenants/{tenant_id}/rip/import-banca`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

### `POST /tenants/{tenant_id}/rip/import-casa`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

### `POST /tenants/{tenant_id}/rip/operatiuni`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/rip/operatiuni/{op_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rip_operatiuni (DELETE/INSERT/UPDATE) — prin `rip_api`*

- [ ] 

## T33 — Exportul contabil (SAGA, WinMentor)

*clasa PARTIAL · 3 rute · 2 schimba date · nu se poate sti din date*

*citiri (nu schimba nimic): `/tenants/{tenant_id}/facturi/{factura_id}/export-saga`*

### `POST /tenants/{tenant_id}/facturi/export-saga`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

### `POST /tenants/{tenant_id}/facturi/export-winmentor`

*garda `cere_rol` · rol:admin_firma*

*ce face: Export WinMENTOR: Facturi.txt + Articole.txt (Windows-1250) co-locate intr-un zip — scrie artefacte_produse (INSERT) — prin `artefacte`*

- [ ] 

## T34 — Rapoartele comerciale, centrele de cost și rapoartele salvate

*clasa MECANIC · 14 rute · 5 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/ansamblu`, `/api/v1/firme/{tenant_id}/kpi`, `/cabinet/consolidare`, `/tenants/{tenant_id}/centre-cost`, `/tenants/{tenant_id}/centre-cost/raport`, `/tenants/{tenant_id}/centre-cost/varianta`, `/tenants/{tenant_id}/rapoarte-comerciale`, `/tenants/{tenant_id}/rapoarte-comerciale/fisa`, `/tenants/{tenant_id}/rapoarte-salvate`*

### `POST /tenants/{tenant_id}/centre-cost`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/centre-cost/{centru_id}/buget`

*garda `cere_cabinet` · **fara rol***

*ce face: Seteaza bugetul anual (cheltuieli + venituri) al unui centru pe un an. — scrie bugete (INSERT) · centre_cost (INSERT/UPDATE) — prin `centre_cost_api`*

- [ ] 

### `POST /tenants/{tenant_id}/rapoarte-salvate`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rapoarte_salvate (DELETE/INSERT) — prin `rapoarte_comerciale_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/rapoarte-salvate/{vid}`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie rapoarte_salvate (DELETE/INSERT) — prin `rapoarte_comerciale_api`*

- [ ] 

## T35 — Pachetul lunar către client și solicitările lui

*clasa MECANIC · 36 rute · 15 schimba date · 1 firme il pot exercita azi*

*citiri (nu schimba nimic): `/pachete/{tenant_id}/poveste`, `/pachete/{tenant_id}/preview`, `/pachete/{tenant_id}/rezumat`, `/portal/acasa`, `/portal/acces-cont`, `/portal/cashflow`, `/portal/declaratii`, `/portal/documente/balanta`, `/portal/documente/luni`, `/portal/facturi`, `/portal/firma`, `/portal/firme`, `/portal/kpi`, `/portal/povesti`, `/portal/recomanda/preview`, `/portal/solicitari`, `/portal/solicitari/contor`, `/tenants/{tenant_id}/client-acces`, `/tenants/{tenant_id}/clienti`, `/tenants/{tenant_id}/clienti/{client_id}`, `/tenants/{tenant_id}/solicitari`*

### `POST /pachete/{tenant_id}/genereaza`

*garda `cere_cabinet` · **fara rol***

*ce face: scrie pachet_povestea (INSERT) — prin `pachete_api`*

- [ ] 

### `POST /pachete/{tenant_id}/poveste`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie pachet_povestea (INSERT) — prin `pachete_api`*

- [ ] 

### `POST /pachete/{tenant_id}/trimite`

*garda `cere_rol` · rol:admin_firma*

*ce face: scrie pachet_povestea (INSERT) — prin `pachete_api`*

- [ ] 

### `POST /portal/acces-cont/acces`

*garda `cere_client` · rol:verificat-în-corp · scrie in user_tenants, users*

*ce face: scrie user_tenants (INSERT) · users (INSERT/UPDATE)*

- [ ] 

### `DELETE /portal/acces-cont/acces/{user_id}`

*garda `cere_client` · **fara rol** · scrie in user_tenants, users*

*ce face: scrie user_tenants (DELETE) · users (UPDATE)*

- [ ] 

### `PUT /portal/acces-cont/email`

*garda `cere_client` · **fara rol** · scrie in users*

*ce face: scrie users (UPDATE)*

- [ ] 

### `POST /portal/recomanda`

*garda `cere_client` · **fara rol***

*ce face: intoarce {ok, rezultate}*

- [ ] 

### `POST /portal/solicitari`

*garda `cere_client` · **fara rol** · scrie in solicitari_client*

*ce face: scrie notificari (INSERT/UPDATE) · solicitari_client (INSERT) — prin `notificari_api`*

- [ ] 

### `POST /tenants/{tenant_id}/acces-portal`

*garda `cere_rol` · rol:admin_firma,angajat,verificat-în-corp*

*ce face: Emite un token de PREVIZUALIZARE (read-only, tab-local) pentru portalul clientului firmei*

- [ ] 

### `POST /tenants/{tenant_id}/client-acces`

*garda `cere_rol` · rol:admin_firma,verificat-în-corp · scrie in user_tenants, users*

*ce face: scrie firma_profil (INSERT/UPDATE) · tenants (INSERT/UPDATE) · user_tenants (INSERT) · users (INSERT/UPDATE) — prin `tenant_provisioning`*

- [ ] 

### `DELETE /tenants/{tenant_id}/client-acces/{user_id}`

*garda `cere_rol` · rol:admin_firma · scrie in users*

*ce face: scrie users (UPDATE)*

- [ ] 

### `POST /tenants/{tenant_id}/clienti`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

- [ ] 

### `DELETE /tenants/{tenant_id}/clienti/{client_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

- [ ] 

### `PUT /tenants/{tenant_id}/clienti/{client_id}`

*garda `cere_rol` · rol:admin_firma,angajat*

*ce face: scrie clienti (DELETE/INSERT/UPDATE) — prin `clienti_api`*

- [ ] 

### `POST /tenants/{tenant_id}/solicitari`

*garda `cere_rol` · rol:admin_firma · scrie in solicitari_client*

*ce face: scrie solicitari_client (INSERT)*

- [ ] 

