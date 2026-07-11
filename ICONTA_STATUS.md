# ICONTA_STATUS — starea build-ului nou (iconta_v2, port 8010)

Actualizat: 03.07.2026

## FUNCTIONAL, TESTAT LIVE

### Portal client (complet)
- Acasa: semafor ANAF colapsabil (lista doar la click — fix `.pa-lista[hidden]`)
- Facturi (refoloseste facturi_ecran.js), Declaratii depuse
- Solicitari: chat bidirectional client<->cabinet, clopotel + email
- Povestea lunii: cu delta fata de luna anterioara; email la aprobare
- Recomanda: helper unificat _trimite_recomandari, preview colapsabil
- PENDING: Documente (gol complet)

### Migrare (toate 7 straturile testate)
Firme, Solduri initiale, Solduri parteneri, Salariati, Asociati,
Mijloace fixe, Istoric declaratii.
Fix aplicat: constrangere salariati_cnp_uniq scoped pe current_schema();
tenant_template.sql regenerat. Import salariati foloseste part_time (boolean).

### Admin iConta (superadmin, 3 carduri)
1. Raportari — chat sesizari, imagini, tab utilizatori/AI
2. Activitate cabinete — zebra roz/bleu, firme/angajati/facturi/declaratii/
   recomandari/ultima activitate; Suspenda/Reactiveaza (login blocat la suspendat)
3. Sanatate server — load/RAM/disc/uptime/DB/erori 500+ (24h),
   grafice SVG din public.metrici_sanatate (instantanee la 5 min),
   alerte email (praguri: RAM/disc 75%, load 0.7xCPU, conexiuni DB 20,
   erori 500+ in 10 min; cooldown 1h/categorie)
- audit_log: middleware logheaza toate cererile autentificate
- subbara superadmin = centralizator live (cabinete/firme/angajati/facturi/declaratii/recomandari)

### Landing / Login (rescris complet — login.js)
- Bara sus: logo + Acces (dreapta); fara tagline
- Hero: "Un singur sistem.<br>Toate procesele." (Segoe UI Variable Display 56px/60px)
  + subtitlu 20px #6B7280
- Card mare "Facturare gratuita" (roz, buton Acces albastru #0f6cbd -> direct
  formular inregistrare) stanga + 2 randuri (3+4 carduri) dreapta
- Bara incredere jos: Date securizate / Acces de oriunde / Suport dedicat / Fara costuri
- Modal Acces: 2 carduri (Intra in cont / Client nou)
- Client nou: CUI + Verifica la ANAF (endpoint public /public/verifica-cui/{cui},
  cod_caen extras, avertizare non-blocanta CAEN!=6920, mesaj calm la esec, mesaj PFI),
  Denumire cabinet de contabilitate/contabil (autocompletat), Nume administrator
  (camp unic, split pe ultimul spatiu), Email (autocomplete=off, placeholder),
  Parola + Confirma parola (validare client)

### Declaratii
Toate portate in core/: d100, d101, d112, d205, d300, d301, d390, d394, d406
+ dispatch in declaratii_api.genereaza(). Nimic de portat din legacy.

## PENDING
1. Documente (portal client) — nimic construit
2. Test flux complet "Creeaza cont" (submit end-to-end)
3. Responsive landing (<900px netestat)
4. Test suspendare cabinet live
5. Alerte email sanatate — netestate (praguri nedepasite)
6. G — Educatie AI pe tipare (amanat, asteapta date reale)

## PROBLEME CUNOSCUTE
- Paste-uri lungi se corup in terminal -> heredoc mic sau scp fisier
- Cache agresiv module ES -> versionare import (?v=N) sau golire cache "Tot timpul"
- CSS display:flex suprascrie [hidden] -> mereu adauga [hidden]{display:none!important}
- fer-larg are overflow:hidden -> foloseste fer-larg-simplu pt ecrane admin
- Delogare repetata Edge (Claude+Gmail simultan) — cauza neidentificata inca;
  clearBrowsingDataOnClose verificat OK; test: inchidere/redeschidere Edge

## CREDENTIALE TEST (parola Test1234!)
- superadmin: costin.hateganu@gmail.com
- admin_firma: nistor@gmail.com (NISTOR si Asociatii, firm=2)
- client: costin.hateganu+client@gmail.com (KAI PERFORMANCE, tenant_002)


## Sesiunea 03.07.2026 — 8 module noi (commit-uri a06cc5b..991a582+)

**Standard UI permanent:** butoane (.btn/.btn-secundar/.btn-sters/.btn-nav portocaliu #f97316/.btn-link), semafoare LED 16px gradient+glow (verde #16b364/galben #ffb020/rosu #ff2d20), aplicate global prin clase in stil.css (STANDARD_BUTOANE + STANDARD_SEMAFOR_V2/V3). Culorile hardcodate din control.js convertite.

**Module noi:**
1. Documente portal: balanta PDF + declaratii depuse (core/documente_api.py)
2. Verificatoare: echilibru/trezorerie/TVA per firma per luna (core/verificatoare.py, ecran in fisa firmei)
3. Salarizare: stat de plata lunar + fluturasi PDF (core/stat_plata_api.py); calcul_cm verificat la sursa (Ordinul 506/1030/2026: diminuare 1 zi PER EPISOD; test oficial 442 lei TRECUT); CM integrat in stat+fluturas (brut proportional pe zile lucratoare reale)
4. Banca: parser XLS/XLSX/CSV magic-bytes (core/banca_parser.py), ruta parse-extras, ecran upload; _numar cu ultimul-separator-zecimal
5. HoReCa Raport Z: totaluri pe cote → nota 5311/5125=707 + 707=4427 (suta marita); cote verificate: restaurant 11%, alcool+NC2202 21%
6. Registru jurnal: note+linii per luna, navigare, ecran in fisa firmei
7. Pozeaza bon flux complet patru-ochi: client pozeaza (multi-imagine) → AI citeste articole+cote istorice+cont propus (6022/623/604/628) → asistent corecteaza+certifica → nota (valori cu TVA inclus, factor proportional); tabela {schema}.bonuri + tenant_template.sql
8. Amortizare MF: 6811=cont_amortizare per MF activ, rata liniara, idempotenta AMORT-an-luna, buton in Registru jurnal

**Reguli noi:** fiecare patch incepe cu assert marcaj-not-in (idempotenta obligatorie — duplicarile de azi au dat pagina alba de 2 ori). Credentiale test: costin.hateganu+nistor@gmail.com / Test1234! (admin_firma), +client@gmail.com (client).

**Document:** iConta_functionalitati.docx — inventar complet existente + lipsa + regimuri speciale (30 puncte).

**Urmatoarele:** e-Factura SPV (asteapta CUI), stocuri/NIR, casa UI, bilant anual, reconciliere bancara, teste end-to-end (Creeaza cont, suspendare, alerte email), pilot Daniela.
## 04.07.2026 — Reconciliere bancară + validare jurnal

**Reconciliere bancară (complet, testat pe extras real):**
- DDL `extras_linii` per tenant (alocari jsonb, status nou/potrivit/contat/ignorat) + în tenant_template.sql (regenerat din tenant_001)
- `core/reconciliere.py` — motor pur, 13 teste pytest: match exact (o factură / combo 2–4), FIFO parțial, consum secvențial solduri, CUI normalizat, toleranță 0.01
- `core/reconciliere_api.py` — facturi_deschise (sold = total − decontat + storno legate prin storno_din_id, facturile-storno excluse), importa_extras, lista, conteaza, facturi_deschise_detalii
- 4 endpoint-uri: import / lista / conteaza / facturi-deschise
- UI în ecranBanca (firme.js): badge-uri culori canonice + etichetă text, Contează pe match, picker facturi cu alocare FIFO, contare generică din nota_propusa (627=5121 etc.) pe linii fără CUI

**Principiu respectat:** AI propune, contabilul validează — toate notele din bancă intră `ciorna`.

**Validare jurnal (nou):**
- `core/jurnal_api.py` — editeaza/sterge/valideaza, DOAR pe ciorne
- 3 endpoint-uri PUT/DELETE/POST valideaza
- UI ecranJurnal: badge Ciornă (galben) / Validată (verde), contor "N de validat", editor inline linii (debit/credit/sumă, +/− linii)

**Fix-uri pe parcurs:** Decimal în json.dumps (default=str), data dd.mm.yyyy→ISO, tip strict după semn, scroll la picker.

**De făcut (Următoarele):**
- Editare notă cu factura_id desincronizează soldul facturii — avertisment sau recalcul la editare
- Buton Ignoră pe linii de extras (status ignorat există în DDL, fără endpoint)
- Sold negativ rezidual (KAI-148 la −800 după editarea notei) — de curățat datele de test
- Sincronizare copii Windows (reconciliere_api.py cu fix-urile de pe server)

**Comenzi git:** 0d99847 (reconciliere+jurnal), a64aef1 (template), + commit-ul de azi
# iConta STATUS — 04.07.2026 (build nou, iconta_v2)

## Finalizate azi (≈27 commit-uri pe main)

**Bancă / reconciliere**
- Reconciliere bancară completă: motor matching (exact/combo/FIFO), persistență, UI cu badge-uri status.
- Ignoră + undo („readu", endpoint `reactiveaza`).
- TVA la încasare (art. 282 + OUG 8/2026, plafon 5M de la 01.03.2026): motor `core/tva_incasare.py` (6 teste), la contarea încasării/plății pe factură se adaugă automat 4428=4427 / 4426=4428 proporțional (sută mărită). Bifă `firma_profil.tva_la_incasare`. D300 pe exigibilitate = etapa 2.

**Facturi**
- Contare automată: `POST /facturi/{id}/contabilizeaza` → notă ciornă (emisă 4111=70x+4427/4428), idempotent, buton „Contează" în Istoric facturi. Fix: cota din DB e procent → fracție.
- Regim marjă art. 312 (second-hand): `core/tva_marja.py` (3 teste), endpoint `/vanzare-marja` → ciornă 4111=707cost+707marjă netă+4427; marjă negativă → 0, report.
- Regim marjă turism art. 311: endpoint `/vanzare-marja-turism` (704) — patch scris, **de aplicat** (patch_main_marja_turism.py).

**Stocuri / HoReCa**
- Stocuri CV: ieșire la CMP prin UI, inventar (plus 371=607 / minus 607=371 la CMP).
- Rețetar: rețete+ingrediente, food cost %, descărcare pe rețetă la CMP → ciornă agregată. UI în ecran Stocuri.
- Raport Z → buton descărcare gestiune GV a lunii (ciornă).
- Verificator coerență stocuri: sold contabil vs fișe CV per cont, în ecranul Verificări.

**Declarații / raportări**
- D112 cu CM portat în `core/d112.py` — „Validare fara erori" DUKIntegrator pe server (headless, ~/duk/dist), endpoint xml+valideaza.
- Bilanț S1005 (micro) și S1003 (mici) — XML validat cu validatoarele oficiale (namespace v15 pt 2025, tipBIL UU/BS, F30 minimal); UI card „Bilanț anual". Mapare v1 — test pe balanță reală obligatoriu înainte de depunere.
- e-Transport v1: generator XML notificare v2 (structura oficială MF), endpoint pt upload manual SPV. API = etapa 2 (după OAuth).

**Infrastructură**
- OAuth2 ANAF pregătit: /anaf/oauth/start + /efactura/callback + tokens per cabinet; nginx rutează callback-ul pe 8010. Autorizare reală blocată: client_id respins („invalid_client") — de verificat la pfinternet.anaf.ro săptămâna viitoare (cu CUI/certificat).
- Curățenie date test tenant_002 (sold KAI-148 = 0, duplicate șterse).

## Blocate pe terți
- Raport Z automat din AMEF: fișier .p7b real de la Daniela (testele vechi pierdute).
- OAuth ANAF: certificat + verificare profil client_id.
- PSD2, e-commerce, REGES: chei/contracte externe.

## Următoarele (lista mare, în ordine)
Aplicare marjă turism → taxare inversă internă art. 331 (legare la contare) → operațiuni IC/VIES → import/DVI → Intrastat → multi-valută 665/765 → leasing → avansuri 409/419 → restul listei.

## 04.07.2026 — Maraton module contabile (sesiunea 2)

21 module noi, fiecare cu motor pur `core/*.py` + pytest + endpoint + smoke validat:

- `9294f4b` diferente curs 665/765 + reevaluare solduri valuta (curs BNR auto)
- `be230e8` leasing financiar/operational (167, D8051/C8051)
- `29b8d7c` credite bancare + garantii extracontabile 8011/8021
- `973adf5` avansuri 4091-4094/419
- necorporale: soft 36 luni fix, licenta dnf obligatoriu (endpoint achizitie-necorporala)
- `a9b81f3` reevaluare imobilizari 105/755/655 (amortizare auto din registru MF)
- `ac3187a` provizioane + ajustari creante 0/30/100% art. 26
- `19cde4c` productie 345/711/348 + PIC 331
- `5e15af4` obiecte inventar 303 + prag MF 5000 (OUG 8/2026) + 8035
- `a7df658` decontari asociati: dividende anuale/interimare 463, cota 16%/2026, imprumut 4551
- `527a374` sponsorizari: credit fiscal min(0.75%CA, 20%imp), D177, micro fara facilitate
- `0ff7934` subventii exploatare/investitii 445/4751/7584
- `84208cf` comodat 8038, chirii PJ/PF, refacturare utilitati (structura comisionar, 2 note)
- `f8893d7` deconturi deplasare + diurna: plafon min(2.5x bugetar; 3 salarii/zl)
- `fcdbffd` bacsis HoReCa L376/2022: 461/462, impozit 10% retinut
- `0c43fcf` SGR HG 1074/2021: garantie 0.50 fara TVA, autofactura RetuRO
- `5fb4a55` perisabilitati HG 831/2004: split deductibil + ajustare TVA
- `a0be936` zilieri (10%+CAS, fara CASS, validat ANAF) / cenzori / mandat
- `e176d89` inventariere: plus/minus imputabil-neimputabil, casare MF auto
- `fb598d7` lichidare OMFP 897/2015: valorificare + partaj cu impozit dividend
- ONG OMFP 3103/2017: venituri grupa 73, scutire economica art. 15(3)

Toate valorile fiscale verificate la sursa oficiala. Toate notele intra `ciorna`.

URMATORUL: PFA/II/IF partida simpla + Registru incasari/plati + D212 (OMFP 170/2015, tabel nou rip_operatiuni).
## Sesiune 04.07.2026 (seara) — Partidă simplă PFA/II/IF + pending-uri mici

### Module noi
**Partidă simplă (PFA/II/IF) — complet:**
- `rip_operatiuni` per tenant (DDL aplicat tenant_001/002, în tenant_template.sql)
- `core/d212_engine.py` — motor CAS/CASS/impozit, praguri venituri 2025 verificate la sursă (sm 4.050, CAS 12/24 sm, CASS liniar 6–60 sm, impozit 10%); 7 teste passed. Atenție: pt venituri 2026 → plafon CASS 72 sm (Legea 141/2025), de verificat înainte de folosire.
- `core/rip_api.py` — CRUD (convenția conn+schema), validare ciornă→validată, import idempotent bancă (`extras_linii`, sens din `el.tip`) și casă (`casa_operatiuni`), Fișa D212 doar din validate (avertisment cheltuieli limitate + ciorne), Registru-inventar 14-1-2/b (MF valoare rămasă liniară + disponibilități RIP cumulat).
- Rute: `/tenants/{id}/rip/*` (registru, operatiuni, valideaza, import-banca, import-casa, d212/{an}, inventar/{an})
- UI: `static/js/ecrane/rip_ecran.js` — card „Incasari/plati" în fișa firmei, ecran cu import/validare/ștergere, Fișa D212, Registru-inventar. Testat end-to-end pe KAI.

### Pending-uri rezolvate
- **Responsive landing** <900px și <560px (media queries pagina-*)
- **E2E Creează cont** — register→login→provisioning tenant testat; a scos bug: template regenerat cu pg_dump 16.14 conținea `\restrict` + owner postgres → provisioning pica. Fix: regenerare cu sed pe `\restrict`/`\unrestrict` + `OWNER TO postgres`→`iconta_user`, păstrat `tenant_001` literal (convenția parametrizare!). NU folosi `__SCHEMA__` în template.
- **Suspendare cabinet live** — gap securitate găsit: tokenul existent rămânea valid după suspendare. Fix: `cere_cabinet` verifică `accounting_firms.activ` în DB per request. Testat: suspendare blochează instant, reactivare restabilește.
- **Alerte email sănătate** — livrare Brevo confirmată (email primit în inbox). Endpoint permanent de test: `POST /admin/sanatate/test-alerta` (superadmin).
- **Fallback denumiri OMFP** — `core/plan_omfp.py` (179 conturi OMFP 1802, cădere 4→3 cifre), integrat în balanță când planul tenantului e gol.
- **Balanță pentru cabinet** — gap real: balanța exista doar în portal client. Rută nouă `/tenants/{id}/documente/balanta` + card „Balanță de verificare" în fișa firmei. PDF verificat: denumiri OMFP OK, echilibrată.
- Fix: handler bRip era în interiorul blocului `if (bCasa)` — mutat corect.
- Curățenie: 44 fișiere .bak șterse, module restante committate (d406_stocuri, efactura_import, ong + teste).

### Commit-uri (9)
527d65a partidă simplă backend · d84ffeb UI RIP + fix sens · e2d0625 Registru-inventar · c6859f3 responsive landing · 4141660 fix template tenant · dd2458b suspendare live · 07933ab test alertă sănătate · 3731c10 fallback OMFP + balanță cabinet · f032d21 module restante

### Rămase pe backlog
- Educație AI pe tipare erori (amânat conștient: întâi documentația)
- Stratul 5 AI triage reclamații (după knowledge base)
- Cont 733 apărut în balanță KAI — nu există în OMFP, de verificat notele de test

## URMARIRE — validator D112 nou (Ordin 605/2026)
Cod actualizat pt facilitate 200 lei (01.07.2026). Validatorul ANAF (22.04.2026)
inca aplica 300 → atentionare SP1B4_1 fals pozitiva pe iulie. Cand ANAF publica
validatorul nou (inainte de 25 aug): descarca D112Validator de pe
static.anaf.ro/static/10/Anaf/Declaratii_R/112.html → ~/duk/dist/lib/ → revalideaza.

## DE FACUT — Anunturi programate + alerta "in vigoare de azi"
1. Tabel public.anunturi (mesaj, activ, de_la, pana_la, destinatar) + banner pe landing (inainte de login) + UI administrare in Admin iConta.
2. Legatura cu monitor_fiscal: alerta fiscala cu data intrarii in vigoare -> in ziua respectiva, banner automat "De azi este in vigoare: <modificarea>" pentru cabinete.

## REGULA PERMANENTA — mesaje utilizator
Helper global arataMesaj(el, txt, tip) in api.js; tipuri: eroare (rosu bold), avert (galben), info (gri).
Orice actiune esuata AFISEAZA mesaj (e.mesaj || e.message) — niciodata tacere. Clase: .msg-eroare/.msg-avert/.msg-info.

## SESIUNE 05.07 (partea 2) — testare + flux client
FACUT: monitor fiscal live (cron luni 08:00, email OK), conformitate exhaustiva (4 fixuri: micro 1%, sm 4325, IMCA 0.5%, D112), Excel 190 teste, landing actualizat (carduri+diacritice), Recomanda card mic (cabinet+portal), portal layout v2, Adauga firma (CUI+ANAF+email client obligatoriu, invitatie automata), Acces client (invitatie/activare link 48h/revocare), conventie globala mesaje, login fullscreen (Bitwarden OK), token 24h.
URMEAZA: testare pe 8 firme profile diferite in cabinetul AMZUICA. Firma 1 MARKET DUNAV (comert, micro, TVA) creata; fisiere test generate (f1_achizitie.xml, extras_iulie.csv, raport_z_0207.csv) — de descarcat din chat. Primul test maine: import XML factura in Facturi.

## SESIUNE 06.07 — refactor arhitectura UI + standardizare
FACUT: cache automat (no-cache pe static, eliminat ?v= peste tot), fereastra prin navigator cu optiuni {lat:"larg"}, sageata mereu + scroll memorat la revenire, titlu h2 primeste automat " · firma" (observer), stelute * rosii automate (observer, #e11d1d), input file stilizat global, form-rand flex standard (Casa, e-Transport normalizate), sageti duble scoase din ecrane (wc + altele), Magazin online prin nav.deschide, borduri carduri 1px #d5dbe3, butoane max-width 400px.
DE FACUT IMEDIAT (chat nou): semafoare LED global — ETALONUL e semaforul din Control fiscal (mari, efect LED); butoanele "← luna / luna →" neconforme de standardizat; commit git al refactorului.
TESTARE: MARKET DUNAV creat (comert, micro, TVA), fisiere test generate in chat vechi (f1_achizitie.xml, extras_iulie.csv, raport_z_0207.csv) — REDESCARCA sau regenereaza in chatul nou. Urmeaza: import XML factura.

## SESIUNE 10.07 (partea 2, dupa-amiaza) — testare Portal client + Migrare + bug-uri reale

### Zona 3 Portal client (#19-32) — COMPLETA
Toate 14 teste verificate. 6 bug-uri reale gasite si reparate pe parcurs:
- Contează/Storniează vizibile pe portalul clientului (limbaj de contabil) → ascunse via flag opt.client, functii comune cabinet+portal
- Lista facturi fara limita (toata istoria intr-un request) → paginare pe luna, limit=10 + buton "vezi mai vechi"
- Card Facturi recurente cauza crash JS pe portal (403 la cere_cabinet + null.addEventListener) → ascuns pe portal, backend ramane intentionat doar-cabinet
- Pachete lunare (Genereaza cu AI) dadea 500: KeyError 'debit' — `_note_lunii` in pachete_api.py construia note cu chei cont_debit/cont_credit, dar motor.agrega_conturi() astepta debit/credit (conventia canonica din motor.py). Fix + testat functional (iunie 700 lei, iulie 6.75 lei rezultat).
- **Scurgere de notificari intre clienti diferiti ai aceluiasi cabinet** (bug real de privacy): notificarea de mesaj nou la solicitari client mergea la TOTI users cu accounting_firm_id potrivit, indiferent de rol — includea alti CLIENTI (nu doar cabinet). Filtrat explicit rol IN admin_firma/angajat.

### Card Solicitari + badge — NEREZOLVAT, revenit la baseline
3 incercari de a adauga badge rosu (necitite) pe cardul Solicitari din portal — toate au stricat structura HTML a cardului (divurile interioare dispareau, text plat inclusiv badge concatenat). Cauza exacta NEIDENTIFICATA dupa investigatie extinsa (verificat: cod corect scris, navigator nu re-randeaza la deschidere/inchidere fereastra, niciun alt cod din app nu atinge cardul). Revert complet la starea functionala dinainte de orice patch (commit 9dc6359). **De reluat cu alta metoda** (poate console.log/debugger live in browser) inainte de a incerca din nou.

### Strat 9 de migrare: Plan de conturi (functionalitate noua)
Cabinetul poate cauta planul existent si adauga conturi analitice/nestandard per firma (rezolva gap gasit la D406: conturi IFRS nestandard nemapate). Backend: 3 endpointuri (`GET /migrare/plan-conturi`, `GET/POST /tenants/{id}/plan-conturi`) + model PlanContIn. Frontend: wizardPlanConturi + importPlanConturiFirma, tipar identic wizardSolduri.

### Bug radacina gasit + reparat: plan_conturi niciodata populat
`tenant_template.sql` avea doar structura tabelei plan_conturi, ZERO date — toate cele 6 firme existente aveau planul complet gol (nu doar KAI). Backfill imediat (185 conturi OMFP fiecare, din core/plan_omfp.py). Fix radacina: tenant_template.sql acum contine INSERT-urile (185 randuri), testat pe schema temporara reala — orice firma noua va avea planul populat automat, fara interventie manuala.

### Card "Import date" pe fisa firmei (functionalitate noua)
Deschide toate cele 8 straturi de migrare direct pentru firma curenta, fara re-selectarea firmei la fiecare strat. Functie noua exportata `meniuMigrarePerFirma()` in migrare.js, reutilizeaza exact functiile per-firma existente.

### Nota contabila manuala (functionalitate noua, test #54)
Buton "+ Nota noua" in Registru jurnal, reutilizeaza exact editorul existent. Backend: `jurnal_api.creeaza()` + `POST /tenants/{id}/jurnal`, aceeasi validare ca la editare. Testat functional: creare+verificare DB+curatenie+validare eroare.

### Fix-uri mici Registru jurnal
- Format data ISO (2026-07-05) → fmtDataCab existent (DD/MM/YYYY), identic cu 4 alte fisiere
- Butoane Valideaza/Editeaza/Sterge: stivuite vertical, aliniate dreapta (flex-direction:column), inlocuieste flex-wrap inconsecvent

### Zona 6 Contabilitate & module firma — PARTIAL
#53 Plan de conturi: rezolvat prin constructia stratului 9 de mai sus
#54 Nota manuala: rezolvat prin constructia de mai sus
#56 Balanta pe luna: PASS (aritmetica verificata linie cu linie, format romanesc corect)
#57 Import balanta initiala: PASS (echilibru validat corect, import fidel sursei)
#58 Import extras bancar: PASS (5 linii, matching automat pe CUI+suma, contare propusa corecta)
#59 e-Factura import: NETESTAT (fara fisier XML de test disponibil)
#60 Auto-contare factura: PASS (dupa fix format data gasit pe parcurs)
#61 TVA la incasare (art. 282): IN CURS — formular functional, bug de aliniere vizuala gasit (eticheta "Suma incasata/platita (cu TVA)" se rupe pe 2 randuri, caseta nu se aliniaza cu Data/Sens) — de reparat in sesiunea urmatoare, cautam functia renderer generica de campuri in operatiuni_ecran.js.

### Regula de proces noua stabilita azi (10.07, in timpul sesiunii)
"O singura comanda per mesaj" — Costin a cerut explicit dupa confuzii repetate cu blocuri multiple de comenzi in acelasi mesaj (patch-uri care nu se scriau efectiv pe disc pentru ca doar a doua comanda dintr-un bloc era rulata).

### Ramase pe backlog (actualizat)
- Zonele 7-17 din planul de teste — complet netestate
- Card Solicitari badge — reluat cu alta metoda de debug
- #59 e-Factura — necesita fisier XML de test
- #61 aliniere vizuala campuri operatiuni_ecran.js — in curs, neterminat

## SESIUNE 10.07 (partea 3, seara) — inchidere zona 6 + deschidere zona 7 Salarizare

### #61 TVA la incasare — INCHIS
Structura canonica .camp + .camp-eticheta stabilita ca regula noua (Design System
v1.1): eliminat dialectul <label>text<br>input din operatiuni_ecran.js. Grila noua
.grila-campuri (casete aliniate jos, eticheta lunga urca pe 2 randuri deasupra).
Verificator extins cu categoria CAMP_DIALECT (detecteaza dialectul vechi mecanic) +
fix vecini bidirectionali la ETICHETE (fals-pozitive eliminate). NC-22 jurnalizat
(rip_ecran.js are 6 campuri neconforme, ramase pt migrare ulterioara).

Bug de navigare gasit si reparat pe acelasi ecran: sageata din antet nu functiona
(operatiuni_ecran.js nu folosea deloc nav.setInapoi/nav.mergi — parte din cele 19
ecrane nemigrate pe navigatorul nou, jurnalizat NC-24 cu lista completa pt R4).
Migrat pe nav.mergi (nu setInapoi) ca sa beneficieze de scroll memorat automat
(mecanism deja existent in navigator.js, scroll_memorat_v1). 2 regresii proprii
gasite si reparate in acelasi patch: corp stale dupa randare noua a navigatorului
(nav.mergi paseaza container DOM nou de fiecare data) + el.closest("label") ramas
dupa schimbarea structurii in .camp (trebuia .closest(".camp")).

### Zona 6 Contabilitate & module firma — COMPLETA (#53-67, minus #59 blocat)
#62 Amortizare MF liniara: PASS (KAI, 3 linii, 1583.34 lei, aritmetica exacta,
    formula start luna urmatoare PIF / stop DNF confirmata pe date reale)
#63 Raport Z HoReCa/AMEF: PASS (deja confirmat anterior)
#64 Stocuri fise CV+CMP: PASS (11/11 teste unitare + end-to-end pe 2 articole,
    CMP recalculat corect, surse diverse inventar/reteta integrate corect)
#65 Operatiuni speciale (30, ecran generic): PASS (sponsorizare testata end-to-end,
    monografie 6582=401 corecta)
#66 Perioada blocata: FAIL -> PASS dupa reparatie. BUG CRITIC: doar 3 din 39 puncte
    de inserare in {schema}.inregistrari verificau perioada blocata (doar edit/
    sterge/valideaza nota manuala) — toate cele 30 module + amortizarea + crearea
    de nota noua OCOLEAU blocarea complet (confirmat empiric). Reparat la nivel de
    baza de date: trigger SQL pe INSERT/UPDATE/DELETE, aplicat pe toate 6 scheme +
    tenant_template.sql (tenanti noi). Exception handler specific -> 423 curat.
#67 PFA partida simpla + RIP: PASS (motor testat end-to-end pe AMZUICĂ, D212 2025
    aritmetica validata manual exact: CAS 12150, CASS 6500, impozit 4635). Aceeasi
    gaura ca #66 gasita si reparata pe rip_operatiuni (alta tabela, acelasi tipar).
#59 e-Factura import: ramane NETESTAT (fara fisier XML de test)

### Zona 7 Salarizare — DESCHISA
#68 Salariat nou + contract: FAIL -> construit + PASS. UI complet lipsa (doar
    import bulk migrare exista, backend POST /salariati gata dar neapelat).
    Construit ecran nou in ecranSalariati (firme.js), structura canonica.
    BUG CRITIC DE SISTEM gasit si reparat: salariati_api.py folosea tip_norma
    (text) peste tot, DB are part_time (boolean) - redenumita intr-o migrare
    anterioara (03.07) fara actualizare cod. TOATA lista de salariati era stricata
    (500) pt orice tenant, invizibil pana acum. Reparat: traducere API<->DB la
    granita, contract API neschimbat. 3 fix-uri UX gasite live cu Costin: min=0
    pe campuri numerice, step diferentiat (ore=0.5, persoane=1, bani=0.01),
    ramane pe formular dupa salvare (nu mai iese la lista, foloseste nav.inapoiPas
    nu nav.inapoi).

#69 Stat de plata: calcul brut-net: PARTIAL (confirmat, netratat inca)
    Motor calcul_salariu() corect pe cazul de baza (verificat exact pe date reale).
    BUG FISCAL confirmat la sursa oficiala (legislatie.just.ro + CECCAR, OUG 89/2025
    art. III): facilitatea 200/300 lei cere cumulativ (a) norma intreaga (b) functie
    de baza (c) brut EGAL cu minimul (d) venit brut total <=4300/4600 lei. Codul
    actual ignora toate 4 conditiile, aplica facilitatea oricui brut<=minim -
    confirmat empiric ca norma partiala primeste incorect facilitatea. Plus un
    mecanism separat (podea CAS/CASS la minim pt norma partiala) mentionat de sursa
    dar neverificat inca oficial, neimplementat deloc.
    DECIZIE: marcat "logica fiscala noua" -> Opus 4.8 pt sesiunea urmatoare (nu
    Sonnet). Locatii exacte: core/stat_plata_api.py liniile 36+80 (part_time citit
    dar niciodata transmis catre calcul_salariu), core/salarizare.py functia
    calcul_salariu (conditie facilitate linia ~74).

### Regula de proces noua stabilita azi (10.07, seara)
0a REGULA REPARATIE REALA, 0b REGULA GLOBALA-INTAI, 0c REGULA VERIFICARE
FUNCTIONALA — toate 3 adaugate in memoria permanenta, aplicate consecvent azi.

### Ramase pe backlog (actualizat)
- #69 Stat de plata: fix fiscal facilitate 200 lei — SESIUNE URMATOARE CU OPUS
- #70-76 zona Salarizare — netestate (Deducere, Facilitate 200 S2, CM, Part-time,
  Fluturasi PDF, Contracte speciale, Tips HoReCa)
- Zonele 8-17 din planul de teste — complet netestate
- Card Solicitari badge (portal) — reluat cu alta metoda de debug
- #59 e-Factura — necesita fisier XML de test
- NC-22 (rip_ecran.js, 6 campuri CAMP_DIALECT) si NC-23 (diacritice REGISTRU
  operatiuni_ecran.js) — jurnalizate, nereparate
- R4 nav.setInapoi migrare — 18 ecrane ramase (lista completa in NC-24)

## SESIUNE 11.07.2026 — testare zona 8 (Declaratii) + zona 9 (Verificari), pe Opus 4.8

### Context de start
Zona 7 Salarizare declarata COMPLETA (#68-76 PASS, cu fix-urile fiscale la sursa
din sesiunea 10-11.07: facilitate 200 lei pe 4 conditii cumulative, suprataxa PT,
rotunjire deducere la 10 lei, split CM angajator/FNUASS). NC-26 (audit salarizare.py)
inchis prin acele fix-uri. Ramas din #72: nomenclator coduri CNAS + exceptii
diminuare (cod 06/14) — in REGISTRU.

### ZONA 8 — DECLARATII: inchisa (mai putin #78 D394)
- #77 D300, #79 D100/D101 IMCA, #80 D112, #81 D205, #82 D406, #83 Bilant:
  PASS din sesiunile DUKIntegrator anterioare (nemodificate).
- #78 D301+D390 PASS (DUK). D394 RAMANE de reconfirmat separat cu DUK la Costin.
- #84 D212 PFA — PASS AZI. Motor core/d212_engine.py auditat LA SURSA (regula #3):
  Legea 141/2025, art.68/148/154/170 CF, instructiuni formular 212. VERIFICAT:
  reper plafoane D212 = salariu minim la 1 ian 2026 = 4050 lei FIX pe tot anul
  (majorarea la 4325 din 01.07 NU atinge plafoanele D212). Plafon CASS 60->72 sm
  confirmat pt venituri 2026. Comentariul de incertitudine din cod inlocuit cu
  decizie datata. Aritmetica confirmata pe 6 oracle-uri contra surse: CAS trepte
  12/24 sm, CASS liniar 6/60(2025) si 6/72(2026), impozit pe net-CAS-CASS.
  CASS max 2025=24300 vs 2026=29160 aplicat corect pe an.
- #85 Semafor conformare per firma — PASS AZI. control_fiscal_api.evalueaza_firma
  rulat pe toate 6 tenanturile. Aritmetica confirmata pe tenant_002: 7 datorate,
  3 depuse corect scazute, 4 lipsa, stare=rosu. Termene cu zi lucratoare corecte.
  Prag urmarire 7 zile viu (limiteaza orizontul, nu polueaza galbenul).
- #86 Patru-ochi — PASS AZI (end-to-end useri reali): id=3==pregatitor -> REFUZ
  cod PATRU_OCHI; id=2 validator distinct -> APROBA. Rollback, nimic persistat.
- #87 Flux validare — PASS AZI cu BUG REAL REPARAT: respingerea fara motiv era
  acceptata (contabilul ramanea fara explicatie). Fix la sursa in 3 straturi:
  (1) coada_api.respinge guard MOTIV_LIPSA pe None/whitespace [motiv_obligatoriu_v1];
  (2) ruta main.py mapare 400 pt MOTIV_LIPSA [motiv_lipsa_400_v1];
  (3) UI validat.js dialogInput are deja obligatoriu:true + trim (verificat, corect).
  Guard STARE_GRESITA confirmat. Retest end-to-end OK.

### ZONA 9 — VERIFICARI & CONTROL: partial
- #88 echilibru balanta — PASS AZI (include si soldurile initiale).
- #89 trezorerie — PASS AZI. Caz real prins: tenant_002 cont 5311 sold creditor
  -334.43 -> TREZORERIE_NEGATIVA blocant, temei OMFP 1802/2014.
- #90 TVA de plata/recuperat — PASS AZI. tenant_002 de_recuperat 51.60 cont 4424;
  tenant_003 de_plata cont 4423. Aritmetica confirmata.
- #93 navigare luni — PASS AZI. Recalcul corect: luna 12 = 52 note cumulativ vs 3
  la luna 3/5, TVA flip de_recuperat 51.60 -> de_plata 1030.41.
- #91 stocuri contabil vs fise — ABSENT. verificare_stocuri APELATA in /control-fiscal
  dar NEDEFINITA -> esueaza silentios in try/except pass. De construit.
- #92 Intrastat praguri — ABSENT. intrastat_praguri apelata dar nedefinita, prinsa
  tacut. De construit (praguri cumulate + luna depasirii; PRAG de verificat LA SURSA).
- #94 lista sortata / #95 drill-down — ruta exista (/control-fiscal + /{id}), NETESTAT.
- #96 verificator TVA drill / #97 D205 vs 457 — fara functie dedicata gasita. NETESTAT.

### REGISTRU (observatii noi, nereparate)
- declaratii_datorate itereaza doar an=azi.year; in ian-feb rateaza restantele lunii
  decembrie an precedent. Edge-case sezonier -> sesiune Opus dedicata.
- coerenta_tva: nota.suma afiseaza doar baza colectata, poate parea inselator. Cosmetic.
- verificare_stocuri + intrastat_praguri apelate in /control-fiscal dar nedefinite (=#91,#92).

### Ramase pe backlog (actualizat)
- #78 D394 — reconfirmare DUKIntegrator la Costin (grupat cu alta validare DUK)
- #91, #92 — de CONSTRUIT (stocuri, Intrastat), logica noua + surse
- #94-97 — de testat functional / de confirmat existenta
- Zonele 10-17 din planul de teste — netestate
- Din #72: nomenclator coduri CM la CNAS + exceptii diminuare (cod 06/14)
- NC-22, NC-23, NC-24 (R4 nav 18 ecrane), #59 e-Factura XML test — deschise anterior

## SESIUNE 11.07.2026 (continuare) — zona 9 #94-97
- #94 control fiscal lista sortata — PASS AZI. Ruta /control-fiscal agrega
  evalueaza_firma pe portofoliu + sumar {verde,galben,rosu,gri}. Sortare
  rosu->galben->verde->gri verificata. Testat pe cabinet Nistor (uid2) si Amzuica
  (uid7). Tranzitie de stare demonstrata end-to-end: tenant_003 rosu (lipsa D100 T1)
  -> depunere in tranzactie -> VERDE (lipsa goala) -> rollback -> revine rosu. Nimic
  persistat. (Toate firmele de test sunt rosu pe date reale; verdele fortat controlat.)
- #95 drill-down firma — PASS AZI. Ruta /control-fiscal/{tid} = evalueaza_firma +
  verificari_contabile. tenant_003: lipsa = D100 T1 termen 27.04.2026. Corect.
- #96 verificator coerenta TVA drill-down — ABSENT in build curent. Exista doar
  coerenta_tva de baza (suma de_plata/de_recuperat, testat #90), FARA drill-down pe
  facturi nepostate. Aparea ca livrat in istoric — probabil in build vechi /opt/iconta
  neportat la reconstructia iconta_v2. De confirmat + reconstruit.
- #97 D205 vs 457 — ABSENT in build curent. Doar o nota 457=463 (regularizare
  dividende, main.py 6118), FARA verificator dedicat D205-vs-457. Acelasi caz ca #96.

### ZONA 9 — concluzie
Testabil epuizat. CONSTRUITE+PASS: #88,89,90,93,94,95. ABSENTE (de construit,
workstream separat de dezvoltare): #91 stocuri, #92 Intrastat, #96 TVA drill, #97 D205-457.

### REGISTRU (adaugat)
- #96, #97 apar ca livrate in istoric dar lipsesc din build iconta_v2. Ipoteza: erau
  in /opt/iconta vechi, neportate. De verificat daca merita reconstruite sau erau
  inlocuite de alte mecanisme (control fiscal + verificari_contabile acopera partial).

## ADDENDUM 11.07 (fix cron #122/#123 EXECUTAT, commit 1574bfe)
#122 facturi_recurente: REPARAT. CREATE TABLE + seq (structura exacta din template) pe
tenant_003 si tenant_004. Cron ruleaza curat ("nimic de emis"). + adaugat DEJA in template.
#123 woocommerce: REPARAT. ADD COLUMN wc_url/wc_ck/wc_cs(text)+wc_ultima_sinc(date) pe
tenant_003/004/005/006 firma_profil, SI in tenant_template.sql (liniile 494-497, firme
noi). Cron ruleaza curat ("0 importate, 0 sarite"). Coloanele wc_ erau adaugate candva
manual doar pe 001/002, lipseau din template - acum reproductibil.
ZONA 13 CRON-URI: COMPLETA 4/4 PASS.
Punctele 1-2 din "DE REPARAT DATA VIITOARE" (addendum anterior) SUNT REZOLVATE.

## SESIUNE 11.07 (continuare) — ZONA 14 API public
PASS: #126 (cheie ick_+token_urlsafe, stocat DOAR sha256, afisata o data), #127 GET firme,
#128 GET facturi, #129 KPI, #130 balanta, #131 POST factura (RON numerotare auto TVA 21%
corect + EUR cu curs BNR aplicat, tva_lei corect), #133 cheie gresita->401, #134 cheie
revocata->401, #135 firma alt cabinet->404 (IZOLARE intre cabinete - critic, confirmat),
#136 ultima_folosire actualizata la fiecare apel. Testat prin HTTP real pe 8010.
PARTIAL #132: valuta fara curs->422 - calea CU curs disponibil merge; calea 422 (curs
lipsa) de testat cu valuta necotata BNR.
NETESTAT #137: UI chei in Setari (necesita browser).
Curatenie: facturile de test (id 3,4,5 tenant_001) STERSE, cheile de test sterse/revocate.

### REGISTRU - observatie curs BNR (de investigat, potential real)
Cursul valutar vine din core/curs_bnr.py: live de la bnr.ro XML + cache public.
curs_bnr_zilnic (coloane: data, moneda, curs, luat_la). RON->1.0. Cache-ul de test are
ultima data 01.07.2026. La emitere factura EUR cu data 11.07 (fara curs in cache), fallback-ul
live a intors cursuri EUR VARIABILE si GRESITE intre apeluri (4.9755 apoi 5.2409; EUR real
~4.97). Pe productie cronul BNR umple cache-ul zilnic deci calea live nu se declanseaza
normal - DAR daca cronul rateaza o zi, facturile valuta ar primi curs gresit -> TVA lei
gresit. DE INVESTIGAT: de ce calea live (parse_xml/curs_pentru) da EUR gresit cand cache gol.

## SESIUNE 11.07 (continuare) — ZONA 15 Securitate
PASS: #138 client pe ruta cabinet->403, #139 cabinet pe firma altui cabinet->404 (izolare
web, confirmat Nistor pe tenant_13 Amzuica), #140 token invalid->401, #141 suspendare live
(cere_cabinet verifica af.activ la FIECARE request, cod confirmat), #142 patru-ochi (=#86).
#143 SQL: PROTEJAT (psycopg2 parametrizat %s peste tot).

## NC-27 SECURITATE XSS (gasit 11.07, NEREPARAT) - PRIORITAR
Escaparea HTML (replace(/[<>&]/) EXISTA si e folosita in 7 fisiere JS (cabinet.js, admin.js,
capacitate.js, tipare.js, recomanda.js, raporteaza.js, navigator.js) DAR NU peste tot.
firme.js (liniile 39-41 ${f.nume}, 349 ${nume}, 463 ${s.nume}, 1723 ${c.email}/${c.nume})
si portal.js (116 ${c.email}/${c.nume}, 457 ${x.email}, 542 ${nume}) pun date user in
innerHTML FARA escapare -> XSS stocat posibil (nume firma/client cu <script>).
Escapare INCONSISTENTA = nonconformitate 0a. FIX corect: functie de escapare GLOBALA (una
singura, in util comun) aplicata la TOATE randarile de date user in innerHTML, + regula in
verificator_conformitate.py care detecteaza ${...} de date user in innerHTML neescapat.
NU petice punctuale. Audit sistematic necesar (toate ecranele). Atinge date reale afisate
contabililor -> prioritate mare.

## ADDENDUM 11.07 — NC-27 XSS REPARAT (partea 1: vectorii reali)
Reevaluare la sursa: NC-27 era supraevaluat. Vectori XSS REALI (date user in innerHTML)
= doar 4 locuri, nu raspandit: firme.js 463 (${s.nume} salariat), firme.js 1723
(${c.email}+${c.nume} client); portal.js 116 (${c.email}+${c.nume}), portal.js 457
(${x.email}). Linia firme.js 349 ${nume} si portal.js 542 ${nume} = text controlat de
cod (etichete verificare/modul), NU date user -> nu-s vectori.
FIX: functie canonica esc() adaugata + exportata in static/js/api.js [esc_canonic_v1]
(escapare completa & < > " '). Importata in firme.js si portal.js, aplicata pe cele 4
locuri. node --input-type=module --check OK pe toate 3 fisiere. Server restart, health 200,
esc servit live. LECTIE 0c: node --check simplu esueaza pe ESM (fals "eroare"); +
scriptul initial a raportat gresit "esc deja in import" portal.js -> era nedefinit,
prins inainte de restart (altfel portalul client crapa la afisare lista).
RAMAS NC-27 (partea 2): regula in verificator_conformitate.py care detecteaza automat
${dateUser} neescapat in innerHTML (pattern de finete: distinge date user de text de cod).
