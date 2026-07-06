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
