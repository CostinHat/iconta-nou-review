# iConta — ISTORIC

**Trecutul: ce s-a facut, cand, ce commit. Pentru ce e DE FACUT vezi DE_FACUT.md. Planul de teste (business P1-P5): ICONTA_TESTARE.md. Sursa de adevar pentru cod: git.**

---

# PARTEA 1: JURNAL STARE (fost ICONTA_STATUS.md)

# ICONTA_STATUS — starea build-ului nou (iconta_v2, port 8010)

Actualizat: 03.07.2026

---
## 13.07.2026 — Partea 4: systemd + audit vizual COMPLET + registrul functionalitatilor + analiza concurentei
~60 commit-uri. Verificator TOTAL 0 permanent.

**INFRA:** iconta-nou.service (systemd, enabled, Restart=always). Restart canonic: sudo systemctl restart iconta-nou.

**Features:** Declaratii per firma LIVE; card Produse reconectat (+cautare+esc); De validat cu numele pregatitorului (JOIN pe creat_de_id).

**Gardieni/tokeni:** HEX_SEMAFOR extins; FIX bug DIACRITICE (finditer); --galben-fundal, --gri-semafor, --gri-fundal-semafor; pct() canonic.

**Fix-uri arhitectura:** navigator h2 auto pe titluCurent (dublarea entitatii); Migrare: inapoiPas dupa Salveaza (firul nu mai acumuleaza); grila-doc min-width; dialecte eliminate (dec-*, cf-gol, asi-echipa-btn, breadcrumb fals ecran Firme); 91 patch-uri moarte sterse (0a).

**HOTFIX-uri (bug-urile mele, prinse de Costin):** fila alba (pct inexistent); interpolare selector firma (escape template imbricat). Lectii: 0c si la frontend, ambele ramuri; screenshot-ul se CITESTE.

**AUDIT VIZUAL COMPLET - toata aplicatia:** fisa firmei 21/21, desktop cabinet integral (retrecut metodic; Asistenti: dialect asi-echipa-btn + flex-wrap + 3 diacritice), Migrare 9 straturi, rol asistent (breadcrumb fals + hotfix interpolare + landing diacritice), admin 5/5 (semafor Sanatate pe tokeni). Parola test Gica: asistent@gmail.com/Test1234!.

**REGISTRUL FUNCTIONALITATILOR (FUNCTIONALITATI.csv, canonic):** 149 pozitii - 112 LIVE + 7 PARTIAL + 30 PLANIFICAT; fiecare cu descriere exacta din citirea modulului, ID stabil Fnnn, nivel, acces UI, sursa, temei legal, stare, testat. Sortat: LIVE primele. REGULA: nicio functionalitate nu traieste in afara listei. + FUNCTIONALITATI_inventar_core.txt (127 module).

**CARENTE consolidate in DE_FACUT:** 10 pozitii cu diagnostic (F103 alerte programate convenite ~03.07 - PARTIAL: lipseste data_afisare + flux monitor->anunt; cod 10 CM; D394 DUK; PWA; retetar GV re-verificare; e-Transport API; pilot P1-P5; spacing).

**ANALIZA CONCURENTEI (CONCURENTA.csv):** 7 competitori, 84 capabilitati confruntate cu registrul. Goluri majore: e-Factura SPV complet (toti), depunere ANAF cu recipise, open banking PSD2, mesaje SPV, tichete de masa, centre de cost+bugete (4 confirmari). 24 pozitii noi PLANIFICAT din concurenta. Pericol strategic: Keez (acelasi model, 7000+ clienti).

---

## 13.07.2026 — Audit DS (partea 3) + Control fiscal per firma (LIVE)
Continuare audit + primul feature din colturile inactive. ~25 commit-uri. Verificator TOTAL 0.

**Audit DS (ecrane de lucru + portal client):**
- Raporteaza/Recomanda/Setari cont: sistem `.set-*` -> canonic (`.panou`/`.camp`/`.camp-input`/`.cap-titlu`); mesaje prin `arataMesaj` (DS cap.6); diacritice; CSS `.set-*` mort eliminat (`.set-bifa` pastrat).
- FIX real `dataRo`: stilul `cu_ora` nu mai afiseaza mereu 00:00 (slice(0,10) taia ora).
- Portal client complet (10 carduri): Facturi 680px (scos lat:larg); hex->tokeni Cifre; dublu scroll eliminat Solicitari.
- Salariati/firme.js: hex semafor -> tokeni. Token nou `--rosu-semafor` #ff3b30 (distinct de `--rosu` sobru #b3261e).

**Reguli noi:** DS cap.2b carduri inactive (activ:false explicit, estompat, "in curand", camp activ obligatoriu). DE_FACUT.md sectiunea 6 (ecrane firma neconstruite + dependenta vector fiscal, persistenta intre sesiuni).

**Control fiscal per firma — CONSTRUIT SI LIVE (commit dfa4be9):**
- Card activat firme.js + `ecranControlFirma`: semafor + declaratii lipsa cu termene + verificari coerenta. Cheama `/control-fiscal/{tenant_id}`; backend `control_fiscal_api.py` exista deja.
- Vector fiscal = `firma_profil` (schema tenant), NU public. Tabel `public.vector_fiscal` creat gresit -> sters (regula de aur).
- Testat live KAI: rosu 7 datorate/3 depuse, D112 x4 luni, verificari OK.

**In curs:** Declaratii per firma — backend `declaratii_api.py` exista (`tipuri`/`periodicitate`/`genereaza`; rute `/declaratii/tipuri`, `/declaratii/{tip}`). De construit ecran + activat card, identic cu Control fiscal.

**Lot deschis:** `#ff3b30` inca hardcodat in stil.css + alte JS (~10 locuri) -> `--rosu-semafor` (lot dedicat).

---

## 12.07.2026 — Audit design & conformitate (DS v2.0 -> v2.9, 11 commit-uri)
Campanie sistematica de audit vizual pe iconta_v2. Tipar recurent: functie/dictionar canonic unic + eliminarea copiilor divergente + regula in verificator. verificator_conformitate.py la TOTAL 0, fiecare pas confirmat vizual in browser.

**Canonizat:**
- FORMATARE: bani(v) = singurul formator monetar (2 zecimale); baniRotund(v) NOU = cifre de ansamblu rotunjite la leu (cockpit cabinet, cifrele firmei client); dataRo(d,stil) = singurul formator de data (stiluri noi zi_luna="12.07" numeric + zi_luna_text="25 feb" pt termene portal client); pct separat pt procente. Eliminat 7x fmt local + _bani + lei local + fmtZi/fmtD/fmtTermen + inline-uri. Date ISO brute afisate (r/f/b/det/m2.data) -> dataRo.
- CULORI CARD (DS cap.12): 35 nuante divergente -> 7 culori-concept in CULORI_CARD (api.js): albastru/verde/teal/violet/piersica/chihlimbar/ardezie. Normalizate 31 definitii card in 5 ecrane.
- ICONITE (cap.13): dictionar canonic unic ICOANE (api.js, 22 iconite, 5 noi: anunturi/server/suport/consolidare/activitate). Eliminat 3 dictionare locale divergente (cabinet/admin/asistent). 8 carduri report generic -> iconite distincte. Fix brief (sinteza) sa nu duplice settings. Fiecare card = triada culoare+denumire+iconita.
- TIPOGRAFIE (cap.14): 6 tokeni dimensiune + 7 clase de tip (.tip-*). Eliminat toate font-size literale inline (18 in 9 ecrane).
- CULORI/BORDURI/RAZA din cod (cap.15): 3 borduri + 6 culori ad-hoc -> var() canonice; 4 border-radius -> var(--raza). Landing (pagina-*/login) pastrat sistem separat (marketing).
- BUTOANE: eliminat clasa buton-ingust (JS+CSS+lista alba verificator). Marcaje .oblig + structura label canonica in flux_concediu + rip_ecran. 37x mig-text -> camp-input (contrast invizibil pe alb).
- BACKEND: validare data_operatiune goala in rip_api.py (testata functional).

**Verificator - 9 reguli-gardian noi permanente:** BANI_NEFORMATATI (toFixed), MIG_TEXT, FMT_LOCAL (orice const X=toLocaleString), DATA_DIALECT, DATA_BRUTA, BUTOANE (strict), ICOANE_LOCAL, FONT_INLINE, RADIUS_INLINE.

**Design System:** migrat complet docx->md (editabil SSH), la v2.9, 15 capitole normative pe server (~/iconta_nou/DESIGN_SYSTEM.md).

Commit-uri: 85dab20 996ce3c ac2baae 865d93c 9596488 6a9da3b 150a218 aa7937a 12c23a6 a134b5e 1b69ca1.


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

## CORECTIE 11.07 — observatia "curs BNR gresit" era FALSA ALARMA
Verificat la sursa (cursbnr.ro): EUR real 2026 = interval 5.08-5.27 lei (mediu 5.148,
max 5.2688 pe 6.05, min 5.0871 pe 8.01). Valorile pe care le marcasem "gresite"
(4.9755, 5.2409) sunt CORECTE - 5.2409 e in interval; 4.9755 era cursul mediu 2024,
pe care l-am confundat din memorie cu cel actual. Diferenta intre apeluri = zile
diferite (cache vs fallback live), nu aleator. curs_bnr.py e CORECT: cache-first,
multiplier tratat bine (val/mult), curs_din_harta determinist (cel mai recent Cube
<= data). NU e bug. Observatia anterioara din REGISTRU se ANULEAZA.
LECTIE (regula de aur, iar): am declarat "curs gresit" pe baza unei cifre din MEMORIE
(EUR ~4.97) fara sa verific la sursa. Exact tiparul pe care regula il previne.
#131/#132 emitere valuta: CONFIRMAT CORECT (curs real aplicat, tva_lei corect).

## NC-27 partea 2 (regula verificator XSS) — AMANAT deliberat
Detector XSS incercat in verificator_conformitate.py -> RETRAS (restaurat la baseline
TOTAL:6). Motiv: pattern-ul ${camp.entitate} neescapat prinde prea multe false pozitive
greu de exclus mecanic: (a) deja-escapate ${escV(...)}/${escS(...)} - exista 7 variante
locale esc/escB/escC/escJ/escS/escV/escapeHtml, (b) fals-prieteni "esc" in numele
deschide*() (deschideCard/Modal/Lupa contin "esc"), (c) context atribut vs innerHTML vs
dialog confirmaCaseta. Un detector imperfect polueaza verificatorul (trebuie TOTAL:0 la
commit) -> mai bine amanat decat pe jumatate (regula 0a).
DAR detectorul a scos la iveala VECTORI XSS REALI in plus fata de partea 1 (firme.js+
portal.js reparate): asistenti.js:153 ${f.nume}${f.cui}, admin.js:79 ${c.nume} in option,
firme.js:1176 ${r.data} import Z, si posibil altele. => NC-27 partea 1 a acoperit 4 locuri
dar escaparea e inconsistenta pe MAI MULTE ecrane. AUDIT XSS COMPLET ramane task real:
(1) unifica cele 7 variante esc* locale intr-un singur esc() din api.js; (2) aplica pe
TOATE ecranele (grep dupa .nume/.email/.denumire/.cui/.tert_nume in innerHTML); (3) apoi
detector in verificator cu excludere corecta (deja-escapate + deschide* + atribute).

## NC-27 partea 3 — INVENTAR COMPLET vectori XSS (harta gata pt audit dedicat)
Grep sistematic ${...camp user} neescapat (exclus deja-escapate): ~50 vectori pe ~10 fisiere.
PRIORITIZARE PE RISC (sursa datelor):
- RISC REAL (date de la parti mai putin de incredere - portal client, input liber):
  cele 4 din partea 1 (firme.js 463/1723, portal.js 116/457) - DEJA REPARATE.
  De adaugat: asistenti.js 153/408 (nume+cui firma), admin_activitate.js 45/74/75/105,
  admin_gratuite.js 39/65, control.js 62/94, facturi_ecran.js 91/645 (tert_nume), login.js
  369/372 (denumire ANAF), cabinet.js 561.
- RISC MIC (date din Excel cabinet / ANAF, nu atacator extern): migrare.js ~30 vectori
  (nume/cui firme importate), firme.js 108/109/1176/1468.
EXECUTIE (task dedicat, mecanic, potrivit Sonnet dupa tipar): pentru fiecare, import esc din
api.js + inlocuire ${x.camp} -> ${esc(x.camp)}. ATENTIE la template nested (asistenti.js:153
${f.cui ? ` · ${f.cui}` : ""}) - esc doar pe valoare, nu rupe ternarul. Verifica anchor x1,
node --input-type=module --check dupa fiecare fisier, restart la final.
NU s-a facut in graba la finalul sesiunii 11.07 (50 editari obosit = risc regresie).
Harta de mai sus e completa - se executa curat intr-o sesiune proprie.


## SESIUNE 11.07 (seara) — inchidere restante cod/securitate + testare zone 11/12/15

### REZOLVAT azi (6 commit-uri + config nginx)
- 4baafee NC-27b: esc lipsea din import in asistenti.js -> ReferenceError runtime
  (rupea listele de firme + vizualizare actor) + 5 vectori XSS nume in innerHTML/confirmaCaseta.
- 6f1fea2 NC-27c: 47 vectori XSS escapati in migrare.js (nume firma/cont/denumire/
  salariati/asociati din import ANAF+upload) + esc in import. RISC MIC inchis.
- b0ced83 NC-27d: unificat _esc local (nu escapa apostrof) cu esc canonic din api.js (16 apeluri).
- 12dd215: UI verificator D205 vs cont 457 randat in ecranul Verificari (semafor verde/rosu). #97 complet (backend+wiring+UI+test real).
- 3011b4d: gitignore log_arhiva/.
- CONFIG NGINX (in afara repo, backup nou-iconta.bak_SECHDR): adaugate 4 headere securitate
  (Strict-Transport-Security HSTS, X-Frame-Options SAMEORIGIN, X-Content-Type-Options nosniff,
  Referrer-Policy). Verificate live pe https://nou.iconta.eu. #141 reparat.
- Audit esc: niciun alt fisier nu foloseste esc/_esc fara import/definitie (asistenti.js era singurul).
- Menaj: recurente.log + woocommerce.log arhivate in log_arhiva/ si golite (erorile ISTORICE pacaleau la tail).

### TESTAT azi — zone complete PASS
- Zona 11 (Asistenti) 5/5: #111 competente-fara-firme (aplica_regula_zero_firme: angajat->dezactivat,
  admin->doar iese din procesatori), #112 semafor echipa, #113 patru-ochi (=#86), #114 capacitate, #115 tipare/bara.
- Zona 12 (Admin iConta) 6/6: toate 11 rutele /admin au guard rol='superadmin' (verificat cu script),
  testat functional #116 activitate+guard 403, #118/119 suspenda/reactiveaza.
- Zona 15 (Securitate) 7/7: #138/139 rate limiting (auth 5r/min, gen 20r/s, 429), #140 fail2ban activ,
  #141 headere (REPARAT azi), #142 zero secrete in git + zero chei hardcodate, #143 SQL parametrizat (%s),
  #144 XSS (acoperit NC-27 a-d).

### RESTANTE RAMASE (nu se pot face din server / sesiune proprie)
1. REBOOT KERNEL — "System restart required" pe server. Decizie Costin, fereastra linistita (downtime clienti, Daniela pilot activ).
2. Zona 16 PWA (#145-148) — manifest, service worker, instalare Android/iOS. Se testeaza in browser DevTools + telefon. NU prin SSH.
3. D394 pe DUKIntegrator — validare in aplicatia desktop ANAF. NU prin SSH.
4. CM (concedii medicale) — DE FAPT mai putin gata decat credeam (verificat la sursa 11.07):
   motorul de calcul e COMPLET si testat (calcul_cm + procent_cm in salarizare.py, reparate NC-28, pytest 9/9),
   DAR: (a) NU exista ruta HTTP care sa-l expuna (calcul_cm apelat doar din teste, nu din main.py),
   (b) NU exista ecran UI. De construit: ruta /tenants/.../concedii-medicale + ecran nou.
   Design System ACUM pe server + in repo (0592eac) -> regula 0 se poate respecta din SSH.
   Ramas de facut in sesiune CM: (1) ruta HTTP care expune calcul_cm, (2) ecran nou conform Design System
   (cap.2 nimic vizibil decat la selectie, cap.4 casete date, cap.1 butoane), (3) decizie plasare flux
   (sub salariati / ecran propriu / sub-tab operatiuni) - intrebare pt Costin la start.
5. Gap numerotare KAI-162 (cosmetic, din curatarea unei facturi de test API). Recuperabil manual daca se doreste.

### NOTA
Toate restantele de COD REAL si SECURITATE sunt inchise. Ce ramane cere ochii/mainile lui Costin
(browser, telefon, DUK) sau o sesiune dedicata (CM UI). Vechea nota XSS de mai sus (migrare.js ~30 vectori)
este ACUM REZOLVATA (6f1fea2).

## SESIUNE 11.07 (noapte) — MODUL CONCEDII MEDICALE complet + consolidare data/escape

### Modul CM (concedii medicale) — LIVE, commit b3b8a8f + ceed5ca + a18394b
- Backend: taxe_cm (CAS 0; CASS doar cod 01/07/10 verif ANAF art.17(2) OUG 34/2024; impozit 10%) + salveaza/lista/sterge_concediu + 3 rute HTTP /tenants/{id}/salariati/{sid}/concedii. Motor calcul_cm (deja existent, NC-28) testat end-to-end.
- UI: modul flux_concediu.js, buton "Concediu" pe randul salariatului (ecranSalariati din firme.js). Form certificat + calcul afisat + lista + stergere.
- Auto-calcul zile lucratoare (luni-vineri) din data inceput/sfarsit; contabilul poate suprascrie.
- Validare: refuza salvare daca venituri 6 luni <= 0 (altfel brut 0 dar net pozitiv = imposibil).
- Cod 10 (reducere timp munca) EXCLUS din dropdown - formula speciala calcul_cm_cod10, iteratie viitoare.

### REGULI DESIGN SYSTEM noi (stabilite azi - DE ADAUGAT IN docx la sesiune desktop)
1. dataRo(d, stil) din api.js = SINGURA formatare data. Stiluri: implicit "zz.ll.aaaa", "cu_ora" (zz.ll.aaaa HH:MM), "lung" (11 iulie 2026). INTERZIS toLocaleDateString ad-hoc, date ISO brute, functii locale de data. [commit 082c9fb: eliminat 7 functii duplicate + migrat 11 fisiere]
2. .camp-ajutor (albastru #3d8fd6) = ghidaj preventiv sub camp: de unde ia utilizatorul valoarea. Niciun camp obligatoriu gol fara context.
3. .oblig (asterisc rosu #ff3b30) = marcaj camp obligatoriu langa eticheta. Campurile optionale nu se marcheaza.
4. .buton-secundar bordura #b9c2cf (nu var(--linie) care era invizibil pe alb).
5. Formularele NU se invelesc in caseta alba (background:#fff). Stau pe fundalul ferestrei; doar campurile (input) sunt albe cu bordura #b9c2cf. Wrapper alb pe fundal gri-deschis = caseta invizibila.
6. esc canonic din api.js (escapeaza & < > " ') = SINGURA functie escape. INTERZISE variante locale (_esc/escB/escV/escS/escC/escJ) care omit apostroful -> risc XSS in atribute cu ghilimele simple. [commit 082c9fb + 8eb3aae: 6 variante eliminate din firme.js/facturi]
7. confirm()/alert()/prompt() native INTERZISE. Confirmari via confirmaCaseta(); input via formular in-ecran (nu prompt). [commit 8eb3aae: prompt REGES inlocuit]

### RESTANTE ACTUALIZATE
- Design System docx: regulile 1-7 de mai sus DE ADAUGAT in docx (sesiune desktop cu Word - NU prin SSH, risc corupere binar).
- raporteaza.js: format data "11 iul" (scurt cu luna) migrat la dataRo cu_ora - de verificat vizual ca nu deranjeaza feed-ul.
- Reboot kernel (decizie Costin, fereastra linistita).
- Zona 16 PWA (#145-148) + D394 DUK - browser/telefon/desktop, nu prin SSH.

---

# PARTEA 2: JURNAL NECONFORMITATI (fost JURNAL_NECONFORMITATI.md)


## NC-22 (10.07.2026) — CAMP_DIALECT in rip_ecran.js
6 campuri construite ca <label>text<br>input (linii 61-70), in loc de structura
canonica .camp + .camp-eticheta (Design System v1.1, regula stabilita la #61).
Detectat mecanic de verificator (categorie noua CAMP_DIALECT). De migrat pe canonic.

## NC-23 (10.07.2026) — DIACRITICE in etichetele REGISTRU (operatiuni_ecran.js)
Etichetele afisate din configuratia REGISTRU (titluri operatiuni, etichete campuri,
optiuni select) sunt fara diacritice ("Suma incasata/platita", "Incasare de la client").
Incalca regula 6. Verificatorul nu le prinde: scaneaza doar linii cu </placeholder,
REGISTRU e configuratie pura. De reparat: diacritice in etichete + extindere detector.

## NC-24 (10.07.2026) — R4 nav.setInapoi: lista completa ecrane nemigrate
19 fisiere fara setInapoi (verificat grep -L): activitate_cabinet, admin_gratuite,
admin, admin_sanatate, asistenti, asistent, cabinet, capacitate, control,
etransport_ecran, login, produse_ecran, raporteaza, recomanda, rip_ecran, semafor,
termene, tipare, validat. operatiuni_ecran migrat acum (patch 61b), scos din lista.
De migrat R4 (Sonnet), conform planului Faza B.

## NC-25 (10.07.2026) — Operatiuni speciale: test functional "Genereaza nota" neexecutat
Patch-urile 61a-61d (aliniere campuri + nav.mergi cu scroll memorat + fix corp stale
+ fix .closest(".camp")) verificate sintactic si vizual (navigare stabila, scroll
memorat). Ramane de rulat: generare efectiva a unei note (ex. TVA la incasare) si
verificare ciorna in Registru jurnal — pt validarea end-to-end a fix-ului closest.

## Test #62 (10.07.2026) — Amortizare MF liniara: PASS
Verificat pe KAI PERFORMANCE (tenant_002), luna 07/2026: 3 linii generate
(Laptop Dell 166.67, Dacia Duster 1250.00, Laptop test 166.67), total 1583.34 lei.
Aritmetica validata manual (formula liniara, start luna urmatoare PIF, stop la DNF)
- coincide exact cu rezultatul din baza. ERP test corect exclus (PIF in luna curenta).
Cont 6811/2813 monografie corecta.
JURNAL_OKcat

## Test #64 (10.07.2026) — Stocuri: fise CV + CMP: PASS
11/11 teste unitare pytest (core/test_stocuri_cv.py). Verificare end-to-end pe
tenant_002 (KAI), 2 articole, 5 miscari: CMP recalculat corect la intrare (5.00,
7.00 lei), neschimbat la iesiri succesive, sold cantitate/valoare exact la fiecare
linie. Surse diverse (inventar, reteta) alimenteaza corect aceeasi fisa - integrare
reala confirmata, nu doar motor izolat.

## Test #65 (10.07.2026) — Operatiuni speciale (30, ecran generic): PASS
Testat end-to-end operatiunea "sponsorizare" (POST /tenants/2/nota-sponsorizare):
1000 lei mod contract -> nota 6582=401 corecta, status ciorna, descriere pastrata.
Numar gol la generare e comportament normal (populat abia la validare); Registru
jurnal are deja fallback descriere||numar||#id (firme.js:1172), afisare corecta.
Nota de test stearsa dupa verificare. Include si fix-urile de aliniere/navigare
din aceasta sesiune (patch 61a-61d): structura .camp, nav.mergi cu scroll memorat.

## Test #66 (10.07.2026) — Perioada blocata: FAIL initial -> PASS dupa reparatie
Bug real gasit: doar 3 din 39 puncte de inserare in {schema}.inregistrari verificau
perioada blocata (doar editare/stergere/validare nota manuala). Toate cele 30 module
+ crearea de nota noua + amortizarea ocoleau blocarea complet (testat empiric:
amortizare generata cu succes pe luna blocata, status validata direct).
REPARATIE: trigger SQL (verifica_perioada_blocata) pe INSERT/UPDATE/DELETE, aplicat
pe toate cele 6 scheme tenant existente + tenant_template.sql (tenanti noi). Exception
handler specific (nu Exception generic - doar traduce PERIOADA_BLOCATA) -> 423 curat.
Testat: amortizare pe luna blocata->423, luna libera->200 (flux normal nestricat),
creare nota manuala pe luna blocata->423 (cazul gaurii reale, acum acoperit).

## Test #67 (10.07.2026) — PFA partida simpla + RIP: PASS
Motor complet testat end-to-end pe AMZUICĂ (tenant_004, id=13): adaugare incasare
5000+plata deductibila 800 (sold 4200 exact), validare, fisa D212 pe 2025 cu date
reale (venit 80000, cheltuiala 15000): CAS 12150 (baza fixa 12x4050, 25%), CASS
6500 (baza=venit net, regula 2025), impozit 4635 (10%), total 23285 - aritmetica
verificata manual, exacta. Motorul refuza corect calculul pt alt an decat 2025
(plafoane neverificate) - comportament defensiv corect, nu bug.
Gaura similara cu #66 gasita si reparata: rip_operatiuni nu avea trigger perioada
blocata. Extins acelasi tipar (trigger pe data_operatiune) pe toate 6 scheme +
tenant_template.sql. Testat: 423 pe luna blocata, 200 pe luna libera.

## Test #68 (10.07.2026) — Salariat nou + contract: FAIL -> construit + PASS
Gaura reala: UI de adaugare salariat individual lipsea complet (doar import bulk
migrare exista). Backend (POST /tenants/{id}/salariati) era gata dar neapelat.
Construit ecran nou "Salariat nou" in ecranSalariati (firme.js), structura canonica
.camp + grila-campuri (identic tipar #61), nav.mergi pentru scroll.

Bug de sistem critic gasit in constructie: salariati_api.py folosea coloana
tip_norma (text) peste tot, dar DB are part_time (boolean) - redenumita intr-o
migrare anterioara (03.07.2026) fara actualizarea codului. TOATA lista de
salariati era stricata (500) pentru orice tenant - bug preexistent, invizibil
pana acum (nimeni nu testase GET /salariati). Reparat: traducere API<->DB la
granita (tip_norma<->part_time), contract API neschimbat. Confirmat: KAI avea
deja 2 salariati (Ionescu Maria, Popescu Ion) ascunsi de eroare, acum vizibili.

2 bug-uri UX gasite si reparate live cu Costin: (1) Ore/zi permitea valori
negative (fara min pe input number) - fix min="0" pe toate campurile numerice.
(2) step=0.01 aplicat uniform gresit (bani vs ore vs persoane) - diferentiat:
ore_zi=0.5, persoane_intretinere=1, salariu_brut=0.01. (3) Dupa salvare iesea
din formular direct la lista (nav.inapoi() inchidea toata fereastra) - fix:
ramane pe formular golit cu mesaj confirmare + buton separat "Gata, inapoi la
lista" (nav.inapoiPas(), nu nav.inapoi()).

## Test #69 (10.07.2026) — Stat de plata: calcul brut-net: PARTIAL (confirmat)
Motor calcul_salariu() verificat corect pe cazul de baza (normă întreagă, brut peste
minim, fara persoane): aritmetica exacta (Popescu Ion brut 4500 -> CAS 1125, CASS 450,
impozit 212.49, net 2712.51 - identic UI si rulare directa a functiei).

BUG FISCAL confirmat la sursa oficiala (legislatie.just.ro + CECCAR, OUG 89/2025 art.
III): facilitatea 200/300 lei cere CUMULATIV: (a) norma intreaga, (b) functie de baza,
(c) salariul de baza EGAL cu minimul (nu doar <=), (d) venit brut total (fara tichete)
<= 4300 lei S1 / 4600 lei S2 2026. Codul actual (core/salarizare.py, calcul_salariu)
aplica facilitatea oricui are brut<=sm, IGNORAND toate cele 4 conditii - orice norma
partiala cu brut mic primeste incorect facilitatea (confirmat empiric: Ionescu Maria,
part-time 4h/zi, brut 1956.52, a primit facilitate=200 incorect).

Gasit si un mecanism SEPARAT, mai vechi (Cod fiscal, podea CAS/CASS la nivelul
salariului minim pentru norma partiala) mentionat de avocatnet.ro dar neverificat
inca la sursa oficiala si neimplementat deloc in motor.

DECIZIE: fix marcat ca "logica fiscala noua" (regula model: Opus 4.8, nu Sonnet).
De facut sesiunea urmatoare cu Opus: (1) adauga parametri norma_intreaga + venit_brut_total
in calcul_salariu, conditie eligibilitate completa (a-d), (2) cerceteaza la sursa oficiala
mecanismul podea CAS/CASS norma partiala, (3) verifica toate D112-urile deja generate
pe clienti reali pentru norma partiala - posibil facilitate aplicata gresit retroactiv.

## Completare #69 — locatie exacta pt sesiunea Opus
core/stat_plata_api.py: part_time CITIT din DB (linia 27, unpacking randuri) dar
NICIODATA transmis catre salarizare.calcul_salariu() (liniile 36 si 80 - apelat doar
cu persoane=pers, la_data=ref, fara part_time/sub_26/copii_scoala/functie_baza).
De asemenea zero verificare venit_brut_total <= plafon (4300/4600) inainte de a
acorda facilitatea. Ambele apeluri (linia 36 traseu normal, linia 80 alt traseu -
probabil fisa individuala) trebuie corectate identic.

## NC-26 (10.07.2026) — AUDIT FISCAL LA SURSA cerut, nefacut inca pe scara larga
Azi (10.07) s-a verificat la sursa oficiala (legislatie.just.ro + CECCAR) DOAR
facilitatea 200 lei din calcul_salariu (#69) - a iesit bug real. Restul motorului
de salarizare (deducere personala, plafoane, CAS/CASS, art. 77 CF) NU a fost
reverificat azi, desi a fost testat doar aritmetic-intern (cod se leaga cu el
insusi, nu neaparat cu legea curenta). Similar #62 (amortizare, DNF vs Catalogul
HG 2139/2004), #65 (credit fiscal sponsorizare D177), #67 (regula "12x salariul
minim" pt CAS PFA, valabila 2025 - de reconfirmat neschimbata).

DE FACUT: audit fiscal dedicat la sursa oficiala (Opus, model_selection: logica
fiscala/verificare sursa) pe intreg core/salarizare.py, nu doar facilitatea 200 lei:
- deducere_personala(): plafoane si procente (art. 77 CF) - sursa curenta 2026
- CAS/CASS/impozit cote - confirmate deja general (25%/10%/10%) dar verifica
  praguri si exceptii (motiv_exceptare, scutit_contrib_minim)
- CAM 2.25% - baza de calcul corecta (brut intreg, fara facilitate - de confirmat)
- amortizare: DNF-urile din configurarea MF vs Catalogul mijloacelor fixe actual
- sponsorizare: formula credit fiscal D177 la sursa
- PFA/RIP: plafoane D212 2025 (CAS baza fixa 12x minim) - valabilitate neschimbata
De facut inainte de a declara oricare din #62/65/67/68/69 "PASS fiscal complet" -
in prezent sunt doar "PASS aritmetic intern".

## Test #69 (11.07.2026) — Stat de plata brut-net: PARTIAL -> PASS (2 bug-uri fiscale reparate)
Sesiune Opus, verificare la sursa oficiala (legislatie.just.ro + CECCAR + mfinante.gov.ro):

BUG 1 (facilitate acordata gresit) - REPARAT: OUG 89/2025 art.III cere CUMULATIV:
norma intreaga + functie baza + brut EXACT=salariul minim + venit brut total<=plafon
(4300 S1/4600 S2). Cod vechi: doar "b<=sm". Adaugat cota noua plafon_facilitate_salariu_minim
(common.py) + conditii complete in calcul_salariu. Part-time exclus explicit de la facilitate.

BUG 2 (suprataxare part-time lipsa) - IMPLEMENTAT: art.146 alin.5^7 Cod fiscal - pt
part-time cu brut<(minim-facilitate), angajatorul suporta CAS/CASS suplimentar pe
diferenta pana la baza-podea (4125 in S2). Retinerea angajatului ramane pe venit real.
Monografie: 6451=4315 (CAS unitate) + 6453=4316 (CASS unitate), conditionate. Exceptii:
elev/student<26, pensionar, multi-contract (param exceptat_suprataxare).

Verificat end-to-end pe KAI (an 2026 luna 8): Ionescu Maria (part-time 2500) - suprataxa
cas 406.25 + cass 162.50, cost angajator 3125 (era subevaluat cu ~569 lei/luna inainte).
Popescu/Georgescu (norma intreaga) neafectati. 6 cazuri de test unitare verificate manual.

Semnatura calcul_salariu extinsa append-only (norma_intreaga=True default) - apelantii
existenti (d112.py, stat_plata vechi) merg neschimbat.

RAMAS PE BACKLOG (NC-27): D112 pentru part-time - declararea/plata catre buget se face
la baza-podea intreaga (nu doar diferenta pe cheltuieli). d112.py:323 apeleaza cu
norma_intreaga=True default - de verificat si corectat separat pt part-time. Plus:
verificare retroactiva D112-uri deja depuse pt part-time (CAS/CASS subevaluat).

## Test #70 (11.07.2026) — Deducere personala + suplimentara: PASS (fix rotunjire)
Audit complet la sursa oficiala (art.77 Cod fiscal - Lege5/Ordonanta 16/2022 + SD Worx):
TOATE procentele si pragurile CORECTE: 20% baza, +5%/persoana (max 4), 15% tineri<26,
100 lei/copil scoala, plafon minim+2000, degresie -0.5%/50 lei, conditie tineri (brut>2000).

BUG confirmat si reparat: deducerea NU era rotunjita la 10 lei in sus. Legea (art.77 +
SD Worx) cere rotunjire la 10 lei in favoarea contribuabilului. Cod vechi intorcea total
cu 2 zecimale -> impozit usor supraevaluat sistematic la orice salariat cu deducere
degresiva. Ex: brut 4500 -> deducere 800.13 (gresit) vs 810 (corect), impozit -0.99 lei,
net +0.99 lei in favoarea salariatului. Rotunjirea aplicata la TOTAL (art.77 alin.2:
deducerea = baza+suplimentara ca intreg), o singura data.

Verificat end-to-end pe KAI (luna 8): deduceri acum multipli de 10 (Georgescu 160,
Ionescu 1090, Popescu 810), impozite scazute corect. Aritmetica validata manual pe
6 cazuri (minim, degresie, tineri, copii, peste plafon).

## Test #71 (11.07.2026) — Facilitate 200 lei S2 2026: PASS
Acoperit de fix-ul #69 (conditii cumulative facilitate). Verificat explicit pe cazul S2:
- S1 (martie, minim 4050): facilitate 300 corect
- S2 (august, minim 4325): facilitate 200 corect (tranzitia 300->200 pe data functioneaza)
- plafon S2: venit total 4650>4600 -> facilitate 0; venit 4600 exact -> facilitate 200 (<=)
Tranzitia semestriala gestionata de cotele datate, plafon corect la granita.

## Test #72 (11.07.2026) — Concediu medical coduri + procente: PARTIAL (split reparat)
Sesiune Opus, verificare la sursa (OUG 158/2005 + OUG 91/2025 + Legea 64/2026 +
Ordinul 506/1030/2026, textul oficial cnas.ro art.78^4). CM e BACKEND-ONLY (endpoint
main.py:5130 + motor calcul_cm, ZERO UI inca).

CORECTE la sursa: procente cod 01 (55/65/75 progresiv), maternitate 85%, coduri 100%,
perioada diminuarii (01.02.2026-31.12.2027), regula "o data per episod".

BUG SPLIT reparat: zile_ang = min(zile_platite, max(5-diminuare,0)) dadea 4 zile
angajatorului cand diminuare=1. Oficial: angajatorul suporta zilele 2-6 = 5 zile
lucratoare PLATITE, FNUASS din ziua 7. Prima zi diminuata e neplatita, NU reduce
plafonul de 5. Impact real: dosarele de recuperare CNAS erau respinse (alocare
eronata perioada angajator). Reparat: zile_ang = min(zile_platite, 5). Verificat 5 cazuri.

RAMAS PARTIAL (piesa dedicata Opus - aliniere nomenclator CM la CNAS inainte de fix):
1. Nomenclatorul iConta (51=izolare, 06=urgente) DIFERA de cel oficial CNAS
   (07=carantina/izolare, 14=oncologic/neoplazii, 12/13/14=PNS). De aliniat intai.
2. Excepatii diminuare gresite (dupa nomenclatorul corect): cod 06 (urgente) exceptat
   gresit - NU e in lista oficiala; cod 14 (oncologic) LIPSESTE din exceptii - ar
   trebui adaugat. Lista oficiala exceptii (art.78^4, de la 01.06.2026): maternitate
   (c), oncologic (d1), risc maternal (e), PNS (12/13/14), spitalizare, +accidente
   munca (L346/2002) + izolare (L136/2020).

## Test #73 (11.07.2026) — Part-time: PASS
Verificare dedicata la sursa (art.146 Cod fiscal + art.77 + Pluxee/zarinacrm). Acoperit
in mare de fix-ul #69, verificat explicit pe 6 colturi neatestate:
- PT cu persoane intretinere: deducere pe VENIT REAL (nu podea) - confirmat corect la
  sursa (Pluxee: deducerea part-time proportional cu venitul brut real)
- PT sub 26 exceptat: deducere tineri + fara suprataxare - corect
- granita EXACT la podea 4125: fara suprataxare (corect, nu se suprataxeaza la egalitate)
- PT peste podea (4200): fara facilitate, fara suprataxa - corect
- pensionar exceptat: suprataxa 0 - corect
Aritmetica validata manual pe toate cazurile.

LIMITARE CUNOSCUTA (notata, nu bug): deducerea NU se acorda la part-time care nu e
functia de baza (al doilea job) - codul are param functie_baza, dar stat_plata trateaza
toti salariatii ca functie de baza implicit. Rezonabil pt firme mici, de rafinat pt
multi-contract (impreuna cu exceptat_suprataxare, care necesita si el declaratie).

## Test #74 (11.07.2026) — Fluturasi PDF: PASS
Fluturasul afiseaza corect perspectiva ANGAJATULUI (brut, facilitate, CAS, CASS,
deducere, impozit, net) - suprataxa part-time NU apare in retineri (corect, e cost
angajator, nu afecteaza netul salariatului). Costul total angajator (jos) include deja
suprataxa via calc['cost_angajator'] (fix #69). Imbunatatire: cand exista suprataxa,
nota de cost o mentioneaza explicit (transparenta - altfel apareau bani "din senin").
Bug prins in constructie: _dec nu era importat in stat_plata_api - inlocuit cu float.
Verificat end-to-end: PDF valid generat pt Ionescu (PT, "suprataxa part-time 568,75 lei"
in cost) si Popescu (NI, fara mentiune). Ambele HTTP 200, PDF-uri valide.

## Test #75 (11.07.2026) — Contracte speciale (zilieri, cenzori, mandat): PASS
Verificare la sursa (Legea 52/2011 + art.76(2) lit.r/g/i Cod fiscal + ANAF regim_zilieri
+ infotva 2025/2026). Motor contracte_speciale.py corect pt regimul ACTUAL:
- ZILIERI: impozit 10% pe (brut-CAS), CAS 25% pe brut, FARA CASS, FARA CAM. Confirmat
  la sursa (art.139(1)s + art.76(2)r CF: din mai 2019 zilierii datoreaza CAS 25%; nu
  sunt asigurati in sanatate deci fara CASS). Codul e aliniat la regimul actual, nu la
  cel vechi ("fara contributii" - depasit). Impozit 10% (nu 16% din textul original L52,
  suprascis de art.76(2)r CF). Monografie: 641=421, 421=4315, 421=444, 421=5311 (fara CASS).
- MANDAT/CENZOR: CAS 25% + CASS 10% + impozit 10% pe (brut-CAS-CASS), fara CAM. Corect.
Aritmetica verificata manual: zilier 500 -> net 337.50; mandat 2000 -> net 1170.
OBSERVATIE minora (nu bug): remuneratie_minima_zilier foloseste 165.33 ore/luna ->
orar 26.16, vs minimul orar oficial 25.95 (166.667 ore/luna). Rezultat conservator
(peste minim), de aliniat divizorul daca se doreste precizie la minimul orar exact.

## Test #76 (11.07.2026) — Tips HoReCa (bacsis): PASS
Verificare la sursa (Legea 376/2022 + art.115 CF + OUG 28/1999 art.2^3 + juridice.ro +
avocatnet/Rapcencu). Motor bacsis.py corect:
- REGIM FISCAL (partea de conformitate): impozit 10% "venituri din alte surse" retinut
  la sursa la distribuire, FARA CAS/CASS, FARA TVA, nu se recalifica salarial, restaurantul
  nu inregistreaza nici venit nici cheltuiala. Declarare D100 (impozit) + D205 informativ.
  TOATE confirmate la sursa oficiala.
- MONOGRAFIE: iConta foloseste 461/462 (Debitori/Creditori diversi) - convenție VALIDA.
  Expert contabil Rapcencu (avocatnet) confirma explicit: "462 Creditori diversi SAU 4281
  Alte datorii cu personalul, in functie de rationamentul profesional al fiecaruia". SAGA +
  Nexus ERP folosesc tot 462. Nu e bug - e alegere profesionala acceptata.
Aritmetica verificata: bacsis 1000 -> impozit 100, net 900. Monografie corecta.
OBSERVATIE minora (nu bug): contul-punte de incasare e 461 (Debitori) - mai atipic vs
4111 (Clienti), dar valid ca terti. De rafinat daca se doreste alinierea la 4111.

## Sesiunea 13.07.2026 partea 5 — Restanțe PARTIAL: 4 închise
**Curățenii date test (tenant_003):** orfanii [TEST-GV] ștersi în ordinea FK
(retete_linii → retete → miscari_stoc → articole; referentul era [TEST-GV] Pizza,
linia „mozzarella" potrivită parțial pe articolul vechi id=2); seed [T150] curățat
complet — 0 markere de test rămase.

**F150 Import rețete HoReCa → LIVE (a932cb3):** retest potrivire OK după curățenie
(Pizza valid, potrivire unică); UI pas 11 „Rețete (HoReCa)" în migrare per-firmă,
clonă structurală F151; cache-bust import migrare.js (firme.js + cabinet.js);
test vizual complet în KAI: ambele ramuri (2 valide importate, 1 sărită cu motiv),
persistență confirmată în date (Pizza 3 linii, Paste 2).

**Reparație DS cap.6 pe F150 + F151 (78f458a, 615b50f):** mesajele de stare din
ambii pași de import (progres/eroare/succes) mutate de pe innerHTML ad-hoc pe
arataMesaj (info/eroare/ok) — 4+4 înlocuiri. Lecție reconfirmată: clonarea unui
pattern existent NU scuză abaterile DS din el; cod nou = conform de la prima linie.

**F076 Rețetar GV → LIVE (6a3798d, ec3cf08):** test complet cu date reale în
tenant_002 — food cost 3,44/porție (11,5%) confirmat matematic, descărcare 10
porții la CMP (34,40, notă ciornă 601=302), stoc insuficient blocat, fișe sănătoase,
23 pytest. **BUG REAL găsit și reparat [gv_crono]:** descarca valida doar stocul
TOTAL, nu cronologic la data descărcării — o ieșire antedatată (15.06, înainte de
intrări) trecea și corupea fișa de magazie (orice replay ulterior pica). Reparație:
validare prin replay complet fisa_magazie cu ieșirea inserată cronologic (prinde
și spargerea mișcărilor ulterioare) + CMP la data descărcării; zero logică duplicată.
Nota coruptă #92 ștearsă; 07/2026 deblocat în tenant_002 (reziduu test 12.07).
UI retete_v1 din firme.js: 6 mesaje de stare mutate pe arataMesaj (DS cap.6).
Bonus: blocarea perioadei s-a autovalidat în test (PERIOADA_BLOCATA a oprit corect
prima încercare pe 07/2026).

**F060 + F103 Alerte legislative programate → LIVE (ef968d3):** descoperire —
funcționalitatea era deja construită integral (DDL data_afisare, emitere 7/3/0
cu jurnal alerte_emise, cron 9:00 --doar-emitere, propuneri monitor în admin,
afișare condiționată de dată); statusul PARTIAL era rămas în urmă. Testat integral
cu alertă sintetică [T103]: emitere prag 3 către cabinetele active, idempotență
(a doua rulare 0), anunț cu data_afisare viitoare invizibil azi, curățenie.
Design clarificat: automat 7/3/0 DOAR pentru alertele cu data_vigoare extrasă de
AI; restul rămân propuneri manuale (superadminul alege data). **Fix propuneri:**
markerele de idempotență anaf_buletin („N modificări relevante") excluse din
/admin/alerte-fiscale (rămân în tabelă pentru _procesat); 20 markere istorice
marcate văzut, 18 propuneri reale rămase.

**Bilanț restanțe:** din 6 PARTIAL la începutul părții 5 → rămân 2: F113 PWA
(cere telefon + HTTPS) și blocatele extern F034 (DUK desktop) / F044 (API SPV).
Igienă: 17 fișiere .bak_* șterse din static/js/ecrane/ (contra 0a).
Commits: a932cb3, 78f458a, 615b50f, 6a3798d, ec3cf08, ef968d3 + închiderea.

## 14.07.2026 (zi plina: F113, F152, F153 gratuit, regresie template, audit vizual ~22 ecrane)

**F113 PWA -> LIVE** (`df00efe`): manifest+SW v2, testat iPhone/Safari (instalare, standalone, offline).

**Descrieri FUNCTIONALITATI.csv 103/103** (loturi 2-7): toate pozitiile LIVE cu descrieri verificate la sursa.

**TASK 0a audit cod mort**: 3 functii JS moarte sterse; dosarul rutelor nelegate INCHIS azi (`651a20d`): vanzare-agricultor + achizitie-necorporala LEGATE in registrul Operatiuni speciale (testate real), d112-valideaza/xml + marcheaza-citit STERSE, 6 rute marcate [api_intern_v1].

**F152 Triaj AI sesizari -> LIVE** (`8cb9a3b`): sesizarile trec prin Claude Haiku (baza = FUNCTIONALITATI.csv LIVE); intrebari de folosire -> raspuns AI in fir (~5-8s, polling 3s); bug/fiscal/incert -> escaladare cu confirmare; replica dupa AI = escaladare. Buline rosu/verde (DS cap.8), contor pe stare noua. + inchidere_v1 (`b0795a8`): sesizarile se inchid (nu se sterg), filtru istoric, redeschidere la mesaj; titlu fir din primul mesaj.

**REGRESIE MAJORA REPARATA** (`364d41c`): tenant_template.sql avea {schema} neparametrizat in triggerele perioadelor blocate — provisionarea ORICARUI tenant nou era rupta. Corectat pe TENANT_PLACEHOLDER.

**F153 Cont de facturare gratuita -> LIVE** (gratuit_v1+v2, `36cacbc`+`22021f4`): canal public de achizitie. Register dedicat pe landing (CUI unic, denumirea se goleste la schimbare CUI, sesiune curatata), user client FARA cabinet + tenant propriu (CHECK relaxat). Portal pe masura: 3 carduri, breadcrumb Facturare gratuita, fara elemente de contabil. Poarta Configurare emitere: numerotare + regim TVA (ruta noua regim-tva; FIX bug numerotare_configurata — coloana lipsea din DB, DDL + migrare 6 scheme + template). Regula DS v2.11: cota TVA din nomenclator, nu tastata; avertisment raspundere cota la emitere. 2 facturi reale emise. **IZOLARE GDPR VERIFICATA**: scanare mecanica 161 rute tenant (toate cu bariera) + test practic token ostil = 404/403. Roadmap F154-F161 PLANIFICATE (proforme, recurente, WooCommerce, chitante, model, link plata, e-Factura SPV, Vreau contabil).

**Audit vizual ~22 ecrane** (loturi V1 admin + V2 cabinet + marunt):
- Raportari admin: master-detail restaurat, esc canonic, selector CSS orfan reparat (4 butoane rupte), copiaza tot verificat
- Activitate cabinete (`02528d3`): jurnal grupat pe categorii-toggle, traducere actiuni RO, esc, rezumat cifre, panou full-width, cautare live, fix debordare sol-fir
- Sanatate server (`c075daf`): buton test alerta legat (ruta orfana; email livrat real), etichete grafice cu ziua, esc erori
- Anunturi (`ecc1e5d`): reproiectat pe meniu+pasi navigator (cap.2a), segmente Cabinete/Facturare gratuita cu bife+cautare, selectie directa, tenant_id in anunturi_cabinet, banner la conturile gratuite, fereastra larga
- Lot V2 (`fc89bab`): de_plata tradus, perioada nowrap, nume lung Consolidare pe 2 randuri; 13 ecrane conforme
- Marunt: e-Transport, Produse, Tipare, Asistenti — conforme

Fisiere de test: test.gratuit@example.com / Gratuit2026! (tenant 18) + contul QUANTUM al lui Costin (tenant_009, serie asf232, platitor TVA).

## 14.07.2026 — Partea 2: VIES, backup automat, MT940, gardieni fiscali, poarta beta
14 commit-uri (822358d -> 6f918c3). Verificator TOTAL 0 permanent. Sesiune de testare [C]/[D] + infra critica.

**VIES in emitere** (822358d): prefix stat UE (!=RO) la CUI beneficiar -> verifica-vies in loc de ANAF, autocompletare nume/adresa (filtru "---" pt state ca DE care nu divulga), auth aliniat cere_context (mergea doar pe cabinet). Buton "Verifica" (nu "la ANAF"). Testat IE valid / DE invalid / RO neatins.

**BACKUP AUTOMAT DB — mecanism inlocuit** (iconta_backup_v1, 6f918c3 include): CORECTIE 15.07: consemnarea initiala ('gaura critica') era FALSA. Backup automat EXISTA din 02.06 prin /etc/cron.d/iconta-backup (dump .sql.gz zilnic 03:00, root) si functiona neintrerupt 29.06-14.07 — nu fusese verificat /etc/cron.d/ (incalcare regula de aur). Scriptul original a fost suprascris accidental la 14.07 20:48 (pierdut; rezultatele .sql.gz raman). Cronul vechi sters la 15.07 (rula scriptul nou ca root -> fisier 0 bytes). Mecanismul actual (systemd timer) e superior si ramane: dump -Fc (restore selectiv), ruleaza ca postgres, retentie automata, versionat in git. /usr/local/bin/iconta-backup.sh (pg_dump -Fc iconta_v2 -> /var/backups/iconta, retentie 7 zile) + iconta-backup.service + iconta-backup.timer (systemd, zilnic 03:00, Persistent=true, enabled). Dump/restore validat pe DB temp (11 tenanti/15 useri/date intacte). NB: service+timer traiesc in /etc/systemd/system, de salvat in sertarul config desktop.

**Parser MT940 (SWIFT)** (79f9384, F166): ramura noua in banca_parser detectata dupa marker :61:/:20:, produce aceeasi structura {data,detalii,suma} ca parserul grid. Acoperire majoritatea bancilor RO printr-un fisier standard, cost zero. Model de automatizare maxima. RAMAS: validare pe fisier MT940 real (camp :86: variaza per banca). F167 Open Banking prin Enable Banking notat pt etapa 2 (tier gratuit Restricted Production pt conturi proprii; productie=contract+KYB+cost).

**POARTA BETA -> LIVE** (beta_gate_v1, 6f918c3): BETA_COD_ACCES in env opreste accesul public la login + signup gratuit; conturile se salveaza REAL (lead capture), mesaj "Site in lucru, vei primi email cand devine functional". Testerii intra cu cod (camp nou "Cod acces" la login). Cod actual: ICONTA2026. Golirea env-ului = lansare publica. F168: email automat la lansare catre conturile create in beta.

**Teste [C] DONE** (plan pilot): P1.1 end-to-end (register->firma->factura->contare->status), P1.4 recurente (sablon->cron->factura emisa), P1.5 WooCommerce (simulat complet cu WC fake local, import+idempotenta), P2.9-2.11 (KPI portal / consolidare=suma firmelor / tipare AI), P5.24 backup/restore.

**Teste [D] majoritatea DONE cu GARDIENI scrisi** (module fiscale critice care erau FARA test):
- P1.3 salarizare: test_salarizare.py 15 teste (brut->net, deduceri degresive art.77, facilitate minim, part-time suprataxa art.146, CM prima-zi/split-FNUASS/CASS-coduri/cod10), valori la sursa 2026 (0db51e6)
- P2.6 TVA la incasare: test_tva_incasare.py 6 teste (suta marita proportionala 4428->4427, cote 21/11, alocari mixte, plafoane OUG 8/2026) (9b197f5)
- P2.7 operatiuni speciale: test_operatiuni_speciale.py 9 teste (sponsorizari plafon dublu+D177+micro, avans TVA, leasing financiar cap/dobanda, provizioane art.26) (4be2105)
- MT940: test_banca_parser_mt940.py 4 teste (79f9384)
- Total 34 teste noi. RAMAS: P1.2 (flux lunar complet e-Factura->reconciliere->jurnal->balanta->D300->ANAF).

**BUG-URI REALE prinse prin dogfooding (9):**
1. platitor_tva gresit la signup gratuit (ANAF nefolosit) -> preluat din ANAF la register (gratuit_tva_anaf_v1, 5dd57a9)
2. drift schema tenant_004: 4 coloane link-plata lipsa -> ALTER + verificat template
3. drift schema tenant_003+004: sursa_externa lipsa -> ALTER
4. buton "Conteaza" fantoma pe factura deja contata -> flag contabilizata (lista+detaliu) (0e0d892)
5. status "de preluat" mincinos dupa contare -> eticheta din flag contabilizata
6. cont venit 707 hardcodat (consultanta pe marfuri) -> firma_profil.cont_venit_implicit (707/704) (26775e4)
7. #fr-back null rupea formularul sablon recurent -> eliminat handler mort (2d26568)
8. search_path nesetat in sincronizarea Woo -> SET search_path (wc_searchpath_v1, 8af00f6)
9. (infra) niciun backup automat -> construit

**FIX DS**: detaliu factura titlu "Factura N" (entitate scoasa din titlu, prins de ENTITATE_IN_TITLU); eticheta stare .fd-stare (DS cap.6, clasa fac-storno-tag era fantoma fara CSS) (0e0d892).

**DE_FACUT nou**: F162 (avertisment platitor_tva vs ANAF), F164 (cont_venit din UI), F165 (auditor drift schema tenant vs template - drift recurent), F166 (MT940, in lucru), F167 (Open Banking Enable Banking), F168 (email lansare beta).

## 15.07.2026 — Control incrucisat: promisiunea "control fiscal" capata acoperire
Commits: 43dcc5f (motor+teste), b73b464 (UI), 12dac6f (remediu executabil).

**CORECTIE de proces (a doua zi la rand):** consemnarea "backup - gaura critica" din 14.07 era
FALSA (vezi corectia in sectiunea 14.07). Azi, la fel: notarile F166/F167 din DE_FACUT scrise
ieri NU erau acolo - replace-ul esuase tacut, iar commit-ul declara altceva. LECTIE dura:
dupa orice scriere in fisier normativ, VERIFIC ca s-a scris (grep), nu declar din intentie.

**F169 Control incrucisat declaratie vs contabilitate (TVA) -> LIVE.** Descoperire: promisiunea
din landing ("Control fiscal automat: verifica D112 vs contabilitate, TVA vs declaratii") NU
avea acoperire in cod. Verificatoarele existente lucrau in INTERIORUL unei surse
(verificatoare.py pe balanta: 4427 vs 4426 = coerenta interna; control_fiscal_api pe termene:
CE declaratii sunt datorate, nu cifrele). Puntea INTRE surse lipsea (exista doar d205_vs_457).
Construit core/control_incrucisat.py: D300 (R17_2/R31_2, calculat din facturile lunii - fapt
generator art. 281 CF) vs rulaje lunare 4427/4426. Atentie: balanta e CUMULATIVA, D300 e lunar
-> query propriu de rulaje pe luna, altfel alarme false la orice firma cu istoric.

**PRINCIPII stabilite cu Costin (scrise in modul, aparate de teste):**
1. TREI stari: verde / rosu / GRI (nu am putut verifica). Un audit care nu poate spune "nu stiu"
   nu e audit; verdele tacit peste date lipsa e minciuna prin omisiune. Gri-ul E feature-ul.
2. Fiecare constatare isi declara TEMEIUL (ce sursa, ce rand, ce cont, ce perioada) si LIMITA
   ("NEVERIFICAT: daca D300 depus efectiv la ANAF coincide - necesita SPV").
3. Remediu in trei feluri: executabil (cauza DOVEDITA mecanic), sugerat, investigatie.
   NICIODATA "ajusteaza contul ca sa dea verde" - verdele se castiga prin adevar. Un sistem care
   invata contabilul sa forteze semaforul e mai rau decat lipsa lui. Aparat de test dedicat.
4. Rolul: sistemul face verificarea incrucisata pe care omul NU o poate face realist (12 luni x
   5 declaratii x mii de linii). Increderea vine din recunoasterea limitelor, nu din putere.

**Bucla completa, dovedita pe date reale (tenant_004, iulie):** D300 declara 95 lei TVA colectata,
contul 4427 are 21 -> ROSU, diferenta 74. Cauza dovedita: 2 facturi emise necontabilizate, TVA-ul
lor 73.50 explica exact diferenta -> remediu EXECUTABIL, buton "Contabilizeaza facturile" ->
creeaza note CIORNA prin endpoint existent (patru-ochi intact) -> reincarca -> VERDE. Verificat in
DB: 3 facturi contate 4111=704 + 4111=4427, toate ciorna, conturi corecte.

**UI (Control fiscal):** sectiune "Declaratie vs contabilitate" in detaliul firmei (bulina stare +
mesaj cu cifre + temei gri + remediu galben cu buton), escaladare la rosu in portofoliu. Clase
proprii cf-incr-* : regula 0b a prins ca .cf-rand-decl e grid 3 coloane, incompatibil cu structura
verticala. Starea "gri" exista deja in DS (cf. CULORI din control.js) - nu a trebuit inventata.

**Registru:** F166 (MT940) si F169 (control incrucisat) adaugate in FUNCTIONALITATI.csv ca LIVE.
F163 (extindere la D112/D101/D100), F167 (Open Banking), F169-audit-preluare notate in DE_FACUT.

---

# REZOLVARI CONFIRMATE 17.07 (verificate retroactiv)

Curatenie fisiere normative (BRIEF_CODE_CURATENIE.md, Pasul 1). Intrari din sectiunea CARENTE
(inventar 13.07) confirmate rezolvate azi prin verificare la sursa (grep/test), mutate aici cu
data originala a evenimentului, marcate "arhivat 17.07". Codul ramane sursa de adevar.

- **F103+F060 alerte legislative programate** (eveniment original 13.07 seara, arhivat 17.07) —
  LIVE. Dovada: FUNCTIONALITATI.csv:119 — DDL data_afisare + flux monitor->propunere anunt in admin
  + afisare conditionata de data + cron zilnic 9:00, testat (emitere praguri 7/3/0, idempotenta,
  filtru data viitoare). core/monitor_fiscal.py + anunturi_cabinet.
- **Cod 10 CM (reducere timp munca, art. 19)** (eveniment original 13.07 seara, arhivat 17.07) —
  integrat. Dovada: salarizare.py:208 calcul_cm_cod10 definit + salariati_api.py:222 apelat in flux
  real + flux_concediu.js:14 in dropdown + camp venit conditionat (:105) + test_salarizare.py pass.
  NOTA: DE_FACUT.md sectiunea 5 ("exclus din dropdown, calcul_cm_cod10 neintegrat") e o intrare
  veche contrazisa de cod — de tratat la Pasul 2.
- **D394 pe DUKIntegrator** (gasit rezolvat 15-16.07, netaguit, arhivat 17.07) — validat FARA ERORI.
  Dovada: core/duk.py:15 versiune D394_31 + duk.py:154 "dovedit 15.07.2026 pe D394" + CLAUDE.md
  status 16.07 (D394 in cele 9 declaratii confirmate valide) + core/test_d394.py pass. Blocajul
  "validare desktop" ocolit prin jar headless (core/duk.py valideaza()), nu prin GUI DUK.
- **PWA testat pe iPhone** (eveniment original 14.07, arhivat 17.07) — instalare/standalone/offline.
  Dovada: static/manifest.json + static/sw.js prezente. (Testarea pe device = verificare manuala
  raportata atunci; livrabilul de cod exista.)
- **F076 retetar GV, bug gv_crono (antedatare)** (eveniment original 13.07 partea 5, arhivat 17.07)
  — reparat, LIVE. Dovada: retete_api.py:40-41 + :126 [gv_crono] ("iesirea la data ei nu are voie
  sa sparga fisa"; replay cronologic prinde spargerea miscarilor ulterioare de o iesire antedatata).
- **Descrieri FUNCTIONALITATI.csv complete** (eveniment original 14.07, arhivat 17.07) — confirmat.
  Dovada: 0 pozitii LIVE cu descriere <15 caractere (verificat cu csv reader). Scurte raman doar
  pozitiile PLANIFICATE (scop propus, nu cod) — legitim.
- **Admin auditat complet** (eveniment original 13.07 seara, arhivat 17.07) — 5/5 sub-ecrane.
  Dovada: admin.js:19-33 sub-ecrane — Raportari, Activitate cabinete, Facturare gratuita, Anunturi,
  Sanatate server. CORECTIE eticheta: semaforul "Sanatate server" e pe CPU/RAM/disk/uptime/DB/erori
  500+ (admin_sanatate.js), NU "pe tokeni" cum spunea eticheta din CARENTE.

## Curatenie normative Pasul 2 (17.07) — markere REZOLVAT scoase din DE_FACUT.md

Sectiuni din DE_FACUT.md verificate la sursa si curatate. Faptele erau deja jurnalizate aici, deci
NU s-au duplicat entries — s-au scos doar markerele stale din backlog, cu trimitere la acoperirea
existenta:
- **§2 Blocate — D394 desktop**: rezolvat, valideaza headless prin core/duk.py (nu GUI). Acelasi
  fapt ca "REZOLVARI CONFIRMATE 17.07" de mai sus. In DE_FACUT ramane doar o nota de rezolvare.
- **§4 Infra — systemd 8010**: (REZOLVAT 13.07) scos din backlog; deja acoperit la ISTORIC:17
  ("iconta-nou.service, systemd, enabled, Restart=always"). Verificat 17.07: systemctl enabled+active.
  RAMAS deschis: reboot kernel (/var/run/reboot-required inca prezent, 6.8.0-124/-134 in asteptare).
- **§5 Iteratii — cod 10 CM**: nota "neintegrat" era contrazisa de cod; rand CORECTAT in DE_FACUT
  (nu sters, la cererea lui Costin), cu dovada. Vezi "REZOLVARI CONFIRMATE 17.07" pt integrare.
- **§6 Ecrane firma neconstruite**: (REZOLVAT 13.07) sectiune scoasa din DE_FACUT; deja acoperita la
  ISTORIC:19 + :37-53 (Control fiscal per firma LIVE commit dfa4be9, Declaratii per firma decl_firma_v1).
  Verificat 17.07: firme.js:12/253 + declaratii.js:25 [decl_firma_v1], vector_fiscal_api.py, bilant_api.py.
- **ANEXA Inventar functionalitati** (DE_FACUT): stersa ca duplicat al FUNCTIONALITATI.csv (registru
  canonic din 16.07, 164 pozitii). Doua inventare = drift. In DE_FACUT ramane doar pointer la CSV.


---

# AUDIT BACKUP 17.07 (verificat la sursa)

Pornit de la F170 marcat PLANIFICAT in FUNCTIONALITATI.csv. Verificarea la sursa a
aratat ca jumatate din F170 era deja LIVE, nejurnalizat.

- **Backup automat DB — LIVE** (activ din ~29.06, arhivat 17.07). Dovada:
  `systemctl list-timers` -> iconta-backup.timer, OnCalendar 03:00, Persistent=true;
  /etc/systemd/system/iconta-backup.service -> User=postgres,
  ExecStart=/usr/local/bin/iconta-backup.sh; scriptul face `pg_dump -d iconta_v2 -Fc`
  (baza intreaga, nu doar public), retentie 7 zile prin `find -mtime +7 -delete`,
  log in /var/backups/iconta/backup.log. `crontab -l` root = gol (cron-urile
  aplicatiei sunt in crontab-ul lui costin, nu root).
- **Restaurare verificata — CONFIRMAT 17.07**. Dovada: createdb iconta_restore_test ->
  pg_restore din iconta_v2_20260717_030000.dump -> ambele scheme tenant reaparute ->
  dropdb. Fara erori. Baza vie neatinsa.
  LIMITA DECLARATA: testul dovedeste ca dump-ul se restaureaza si schemele revin;
  NU a numarat randurile. Verificare pe continut = alta tema.
- **Alarma falsa investigata**: dump-ul a scazut 1.2M (15.07) -> 244K (16.07), -79%.
  Cauza dovedita: stergerea firmelor de test dupa campania F124 (16.07), NU pierderea
  schemelor. Dovada: `pg_restore -l | grep -c "SCHEMA - tenant"` = 2 pe dump-ul din
  17.07, iar baza VIE are tot 2 (information_schema.schemata) - dump-ul reflecta
  realitatea. Dump-ul din 15.07 (12 scheme) pastrat ca PASTRAT_20260715.dump, scos
  de sub retentia de 7 zile (find cauta doar `iconta_v2_*.dump`).
- **Fisiere moarte**: iconta-*.sql.gz (root, ~628K, identice, oprite 14.07) = backup
  al bazei vechi `iconta` (port 8000). Nu backup activ.

**RAMAS DESCHIS (F170): off-site.** /var/backups sta pe acelasi disc Hetzner ca baza.
Apara de stergere accidentala, NU de moartea discului. Date fiscale ale clientilor
reali. Decizie de scop (Storage Box vs S3) — cere Costin.

**Registru necinstit gasit**: F170 = PLANIFICAT, desi backupul automat e LIVE din
~29.06. Al treilea rand contrazis de cod azi, dupa randurile "de testat P1.4/P1.5"
(F047/F110/F102/F111/F097) pe care F124 le declara testate pe 16.07. De tratat.


---

# 18.07.2026 — Cont gratuit: STRATEGIE + puntea SAGA (preponderent decizii, putin cod)

Ziua a fost preponderent STRATEGIE, nu cod. Deciziile-cheie au temei complet in DECIZII.md;
aici doar POINTER, fara a duplica continutul.

## Strategie (contul gratuit ca produs)
- **Cont gratuit = varf de lance comercial contra SmartBill.** Firma emite singura, comod, gratis;
  contabilul ei ramane pe SAGA. iConta ocoleste SAGA pe partea slaba (emitere catre firma). Filtru
  pt orice functie de cont gratuit: firma o face singura, fara contabil, fara a atinge partida dubla.
  -> DECIZII.md commit 8d96eda.
- **F161 "vreau contabil" NU e conversie.** Contul gratuit e o firma care are DEJA contabil; iConta
  nu aloca clienti catre cabinete (nu e agentie de matchmaking). Butonul de conversie/acceptare nu
  exista ca atare. Ramane doar intrebarea tehnica de preluare tenant (leaga vs create-new). -> 8d96eda.
- **Retentie cont gratuit inactiv = 1 an** (GDPR storage limitation; exceptia contabila nu se aplica
  contului gratuit; stergere din backup + preaviz). -> DECIZII.md commit afd67d9.
- **Paritate atinsa vs concurenta; SPV direct (F160) = SINGURUL gol care conteaza,** blocat pe OAuth
  ANAF. Fara SPV, iConta e sub FGO -> SPV e PRAGUL sub care oferta nu exista in piata. -> 8d96eda.
- **Export catre programul contabilului = gol strategic** (verificat absent la sursa, si in buildul
  vechi /opt/iconta). Puntea care face pozitionarea posibila. -> DECIZII.md 69ac61e + DE_FACUT.md.

## Cod livrat azi
- **Lot 7 cont gratuit** — investigatie la sursa: contul gratuit primeste {gratuit:true} = meniul
  complet, deci 4 pozitii erau DEJA functionale, marcate gresit PLANIFICAT. Corectate retroactiv LIVE:
  F154 proforme/avize, F157 chitante, F158 model factura, F159 link plata. F155 recurente = buton mort
  reparat (gate-fix cere_cabinet->cere_context). F156 WooCommerce = ecranMagazin extras in woo_ecran.js
  (reutilizat cabinet+gratuit) + gate-fix + optiune in meniul gratuit. Commits 37449d1, 5e81536.
- **Determinare gratuit-vs-cabinet la nivel de TENANT** (reparatie securitate) — _eGratuit era pe
  user.firm (NULL la orice client), nu distingea gratuit de client-portal gestionat. Mutat pe
  tenant_are_cabinet (din tenant.accounting_firm_id). Dovada: 0 useri rol=client in prod -> 0
  reclasificari; test ROLLBACK pe ambele directii. Commit cb3891f. (Deblocheaza F161 tehnic, dar F161
  nu se construieste - vezi strategie.)
- **F171 Export facturi emise catre SAGA — LIVE.** XML propriu SAGA (Diverse -> Import date din
  fisiere generate), ruta READ-ONLY, fara schema, fara atingere pe emitere. Furnizor=firma-client ->
  SAGA claseaza iesire prin CIF; nume fisier F_<cif>_<nr>_<data>.xml; sume net + TVA aritmetic
  (Decimal ROUND_HALF_UP). Buton pe factura (single XML) + zip pe luna; merge si in cont gratuit.
  Format verificat la sursa (manual.sagasoft.ro topic-76 + forum oficial). Testat: XML cap-coada pe
  factura reala tenant_002 (F_14399840_1_10.06.2026.xml, net 10000 + TVA 2100 = 12100). Commit 54e85f5.
  **LIMITA: NECONFIRMAT pe import real in SAGA** — encoding UTF-8 vs Windows-1250 + clasificarea ca
  iesire cer verificare cu OCHI UMAN, nu se pot testa in cod.


---

# 18.07.2026 (partea 2 — dupa-amiaza): semafor fact-aware + puntea factura->stoc

Continuarea zilei (dimineata: cont gratuit + F171 SAGA + Tema A). Deciziile au temei complet in
DECIZII.md; aici doar POINTER.

## Semafor fiscal B (F022) — 9/9 real
D205 si D301 conectate FACT-AWARE controlat: nu se datoreaza pe vector ci pe FAPT, citit printr-o
PUNTE din note validate (D205 = rulaj cont 457; D301 = tabelul d301_operatiuni pe luna). Motoarele
raman SEPARATE (semaforul cheama functia de fapt, n-o absoarbe) - varianta B, fuziunea C respinsa.
Plus: fiecare verdict poarta MOTIVUL pe ORICE culoare, inclusiv verde ("D300 depusa 24.04, la termen")
si neaplicabil ("D205 nu se datoreaza - niciun rulaj 457"). Puntea generala `rulaje_interval` extrasa
din control_incrucisat (rulaj pe cont, interval; refolosibila). -> DECIZII.md commit 898482a.
Cod: commit c377746 (control_fiscal_api + control_incrucisat + UI control.js/firme.js).

## Punte factura->stoc (F172) + profit-pe-produs (F144 LIVE la CV)
Vanzarea si descarcarea gestiunii erau acte deconectate (factura_linii fara articol_id, miscari_stoc
fara factura_id). Decizia: intrebarea reala nu e "ce document descarca" ci "CAND pleaca marfa"
(factura poate fi avans/serviciu/custodie). POARTA OBLIGATORIE la emitere: "Pleaca marfa acum? DA/NU".
DA -> descarca gestiunea pe liniile cu articol (miscari_stoc legat prin factura_id); NU -> factura pur
fiscala. Refoloseste iesire() existent (param aditivi commit/factura_id) + rulaje_interval - o punte,
nu doua. Contul gratuit EXCLUS (nu tine gestiune; adevarul e la contabil pe SAGA). Schema aditiva:
articol_id pe factura_linii, factura_id pe miscari_stoc (NULL-able, FK ON DELETE SET NULL).
Profit-pe-produs (F144, decizie deschisa din 17.07) INCHISA pentru CV: join venit(factura_linii)<->
cost(miscari_stoc la CMP). -> DECIZII.md commit 7894f7b. Cod: commit-uri f366f5a (schema+backend) +
2fa69ab (poarta emitere + profit).
GRIJA MAXIMA (atinge emiterea LIVE): emiterea FARA marfa (NU/serviciu/gratuit) ramane IDENTICA cu azi;
poarta e aditiva, aprinsa doar la firma cabinet CV cu linie de articol.
LIMITA declarata: la GLOBAL-VALORIC profit-pe-produs ramane GRI (cost pe articol inexistent prin
constructie); descarcarea GV ramane global-valorica lunara. Stoc insuficient -> raportat, nu rupe factura.

## Design System a crescut cu doua reguli intr-o zi
- v2.13 (dimineata): stare goala canonica `.stare-goala` (gol + cauza + iesire).
- v2.14 (dupa-amiaza): caseta-poarta `.caseta-poarta` - intrebare obligatorie inainte de o actiune
  consecventa, doua alegeri care merg amandoua inainte (distinct de confirmaCaseta). Motivata de
  poarta "pleaca marfa acum?". Ambele in verificator (STARE_GOALA, POARTA_INLINE).


---

# 18.07.2026 (partea 3 — seara): inventar declarativ nivel 2 + pachet igiena (4 teme)

Continuarea zilei. Deciziile au temei complet in DECIZII.md; aici doar POINTER.

## Inventar declarativ nivel 2 — 3 declaratii verificate la sursa, niciuna nu se construieste
- **D106 RESPINS** (OPANAF 1292/2014, instr_106_2014.pdf) — se depune DOAR de societatile nationale /
  firme de stat pentru varsaminte la buget; clientii iConta = cabinete cu firme PRIVATE. In afara
  publicului. -> DECIZII.md commit 929735b.
- **D230 RESPINS** — declaratie PERSONALA a salariatului (redirectionare 3.5% impozit), nu a firmei;
  PFA merge prin D212. Nu apartine platformei de cabinet. -> DECIZII.md commit da1b3ed.
- **D307 AMANAT** (prioritate joasa) — ajustare TVA la anularea codului de TVA, exceptie rara; se
  reia la primul caz real. -> DECIZII.md commit da1b3ed.
- Registru: D106/D230 RESPINS, D307 AMANAT in FUNCTIONALITATI.csv (F173/F174/F175).

## Registru corectat la sursa
- **F034 (D394) PARTIAL -> LIVE.** Motivul stale ("absent din control_fiscal_api.declaratii_datorate")
  era contrazis de cod: grep D394 in control_fiscal_api.py = 6 hituri, conectat de semafor faza 3
  (commit 3cc1455 din 17.07). Dovada grep in commit. -> commit b00e04f.
- **Curatenie DE_FACUT.md**: CARENTE#4 (dubla introducere CV) inchis, D394-absent inchis, SAGA marcat
  PARTIAL. -> commit 14077da.

## Pachet BRIEF_CODE_PACHET_18IUL — 4 teme de igiena, executie in ordine
- **Tema 0 (fara cod): harta de prioritati in DECIZII.md** — urgent (backup off-site F170); blocat pe
  ANAF (cluster SPV F121/F126/F160, se deblocheaza la OAuth); la semnal, nu preventiv (integrari
  PSD2/plati, concurenta tichete/COR/cost, F161, F307); cere om (SAGA import real, audit vizual ~20
  ecrane, pilot Daniela). Miezul e complet; ce ramane = expansiune la cerere. -> commit a22b4b6.
- **Tema 1 (URGENTA): backup off-site pe Hetzner Storage Box** — vezi partea 4 (executata dupa
  provizionarea Storage Box de catre Costin).
- **Tema 2 (igiena): mig-gol -> arataMesaj** — 48/53 aparitii mig-gol care erau de fapt mesaje de
  EROARE/validare/loading in blocuri catch (nu stari goale) convertite la arataMesaj(zona, msg, tip)
  cu tipul corect (eroare/avert/info). 5 template-embedded lasate deliberat si raportate (nu ghicite).
  verificator TOTAL 0, node --check pe 7 fisiere. -> commit c86c9a3.
- **Tema 3 (verificare + optiunea A): igiena preluarii tenant** — verificat la sursa (grep): cand un
  cabinet adauga o firma cu CUI-ul unui cont gratuit VECHI, contul gratuit ramanea activ=true, logabil,
  EMITENT cu acelasi CUI din alt loc (emitere dubla). Poarta de enforcement (auth refuza tenant gratuit
  inactiv) si mecanismul de inchidere (/admin/conturi-gratuite/{id}/suspenda) EXISTAU deja; lipsea
  declansarea + vizibilitatea. Costin a ales optiunea A: SEMNAL la creare, nu suspendare automata
  (inchiderea unui cont = decizie umana). Cod: provision_tenant detecteaza coliziunea (match pe cifre
  CUI, prinde prefix RO), firme.js + migrare_importa semnaleaza cabinetului. Test functional real pe
  Postgres in tranzactie ROLLBACK (detectie pozitiva + non-match + CUI inexistent). -> DECIZII.md +
  commit 5953ecc.


---

# 18.07.2026 (partea 4 — seara): backup OFF-SITE pe Storage Box (Tema 1, F170 LIVE)

Poarta Tema 1 s-a deschis: Costin a provizionat Hetzner Storage Box. Executata cap-coada.
Temeiul complet + deciziile tehnice sunt in DECIZII.md; aici POINTER + dovada.

## Ce era
Backup LOCAL exista si mergea (iconta-backup.timer zilnic 03:00, pg_dump -Fc, retentie 7z,
restaurare confirmata) - dar /var/backups sta pe ACELASI disc ca baza. Apara de stergere
accidentala, NU de moartea discului. Lipsea copia off-site.

## Ce s-a facut
- **Cheie dedicata pe server** (nu parola, nu cheia de laptop): generata pentru userul postgres
  (/var/lib/postgresql/.ssh/iconta-storagebox), publica instalata in Storage Box cu parola one-time
  folosita O SINGURA DATA (install-ssh-key). Accesul e acum doar pe cheie.
- **iconta-backup.sh v2** (config/ versionat + deployat /usr/local/bin): dupa dump-ul LOCAL (neatins,
  SACRU), sincronizeaza pe Storage Box prin rsync-over-SSH port 23, confirma remote (sftp ls +
  dimensiune), retentie off-site 30z (dupa data din nume, nu mtime remote). FAIL-SAFE: off-site ruleaza
  sub `if` (suspenda set -e) -> esecul lui logheaza + numara, dar nu pica localul. La 2 esecuri
  consecutive -> email Brevo (curl direct la acelasi endpoint ca observare.py; BREVO_API_KEY via systemd
  EnvironmentFile citit ca root inainte de drop la postgres).
- **Serviciul** iconta-backup.service: adaugat EnvironmentFile pentru cheia Brevo.

## Dovada (test real, nu doar sintaxa)
- Rulare completa: LOCAL OK + OFF-SITE OK; dump confirmat independent pe Storage Box prin sftp
  (iconta_v2_20260718_143838.dump, 290870 octeti). Counter esecuri = 0.
- Fail-safe: cheie stricata temporar -> 2 rulari cu off-site esuat, LOCAL a reusit de fiecare data,
  counter -> 2, email Brevo TRIMIS la pragul 2; cheie restaurata -> off-site OK, counter -> 0.
- -> FUNCTIONALITATI.csv F170 PLANIFICAT -> LIVE; DECIZII.md (temei + 4 decizii tehnice + alternative
  respinse + limita).

## Restaurare din off-site — testata cap-coada (aceeasi zi)
Descarcat ultimul dump off-site prin sftp -> pg_restore intr-o baza de test (iconta_restore_offsite_test):
pg_restore exit 0, 0 erori; scheme identice cu iconta_v2 (public+tenant_001+tenant_002), public.tenants
2=2, tenant_002.facturi=5 -> dropdb. Baza vie iconta_v2 neatinsa, off-site remote intact. Off-site-ul nu
doar se urca, ci se si RESTAUREAZA cap-coada.

## Limita ramasa
Storage Box = single-provider (nu geo-redundanta intre furnizori).


---

# 18.07.2026 (partea 5 — seara/noapte): e-Factura — fundatie SEND completa cap-coada

Fundatia e-Factura construita cap-coada (mai putin round-trip-ul LIVE, pending drept SPV - ca F176).
Deciziile au temei complet in DECIZII.md; aici POINTER + commit-uri.

## Host corectat la sursa (LIVE), anuland corectia din 18.07
Trei metode, trei host-uri (verificat live, dovada reproductibila): OAuth upload/stare/descarcare ->
api.anaf.ro; validare structura (fara auth) -> webservicesp.anaf.ro; metoda cu certificat (mTLS) ->
webserviceapl.anaf.ro (TLS handshake FAILURE fara cert). Nota din 18.07 care pusese webserviceapl pt
upload = anulata cu dovada handshake. -> DECIZII.md + commit-uri 2407f4e, d486284.

## Generator XML SEND (a95ec8e, 2407f4e)
core/efactura_send.py — UBL 2.1 / CIUS-RO, reutilizeaza structura din build vechi dar loader rescris pe
schema curenta (facturi.tert_*). DOVEDIT LA SURSA prin validare/FACT1 -> {"stare":"ok"}. Rotunjire fiscala
ROUND_HALF_UP. Descoperiri BR-RO (la validator, nu ghicite): BR-RO-110 (BT-54 judet cumparator obligatoriu
-> coloane facturi.tert_judet + tert_oras), BR-RO-100 (Bucuresti -> CityName SECTOR1..6 -> helper
_localitate() strict: fara sector clar -> blocheaza "completeaza sectorul", nu inventeaza).

## efactura_trimiteri (954a59f)
Tabel PER-TENANT de urmarire trimiteri (masina de stari) + garda de idempotenta pe PROD (index unic
partial: un singur send viu per factura - upload ANAF nu e idempotent).

## spv_token = PRINCIPAL cabinet XOR gratuit (233d0af decizie, 8c21db7 cod)
Tokenul apartine unui principal, nu unei tabele de firme. tenant_id XOR accounting_firm_id, CHECK in DB,
resolver UNIC spv_principal(context) + _principal_sql. Connectorul refactorizat pe Principal; connect gratuit
din UI (/spv/autorizare pe cere_context, cu proprietate). 4 garduri (XOR-DB, resolver unic, capcana F177
prinsa cu test, poarta cu proprietate). Cabinet neafectat (apel_anaf(principal_firm(1)) live 200, token 21 intact).

## F177 cron refresh 90z (9876da1) — LIVE
Golul #1: reimprospatare automata a token-urilor sub marja 15z, prin acelasi reimprospateaza_token (rotatie).
Fail-safe per token + email Brevo. F177 selecteaza pe principal (prinde si tokenele gratuite).

## F160 ruta + buton (de73f9e reguli, 3bb6ec8 veriga) — SEND LIVE
Ruta POST /tenants/{tid}/facturi/{fid}/trimite-spv cu 4 PORTI in ordine fixa (token viu -> validare/FACT1 ->
idempotency -> upload pe token propriu) + GET trimiteri-spv (semafor) + buton "Trimite in SPV" per factura emisa
(semafor gri/galben/verde/rosu, confirmaCaseta, fara confirm/alert). Dovedit prin HTTP cap-coada (auth ->
spv_principal -> 4 porti -> upload live -> ExecutionStatus=1 "fara drept", asteptat pe dev token).

## F178 cron poll — jumatatea de PRIMIRE (1fe542b) — LIVE
core/spv_poll.py — stareMesaj/descarcare pe timer (30 min). Fara el o factura urcata ramanea blocata in
incarcat la infinit (masina de stari incompleta). 6 garduri: reutilizeaza apel_anaf pe principal; scope strict
(terminale ne-repollate); token expirat -> refresh sau SKIP (auth-fail != respinsa); timeout -> investigatie
(gri); parsare defensiva (log brut, neasteptat -> gri); rata conservatoare. 9 teste.

## Registru
F160 (trimite) -> LIVE; F177 (refresh) -> LIVE; F178 (poll) -> LIVE; recipisa LIVE = in asteptarea dreptului
SPV (ca F176 - dev token n-are drept pe CIF real; se probeaza cu primul patron real cu certificat inrolat).
F126/F127/F128 raman AMANATE.

## LIMITA (onest, necolorat verde)
Round-trip-ul LIVE (upload->stareMesaj->descarcare recipisa) NU e dovedit - dev token n-are drept SPV pe niciun
CIF real. Fundatia e completa si testata izolat (generator, validare, tracking, principal, porti, poll); doar
proba live asteapta un CIF cu drept. Cuota zilnica ANAF + timpul de prelucrare = de confirmat la sursa.


---

# 18.07.2026 (partea 6 — noapte): F126 e-Factura LIVE cap-coada (jumatatea de PRIMIRE + four-eyes)

Send-ul era acoperit de modelul principal (partea 5). Aici jumatatea de PRIMIRE + interfata cu patru
ochi -> F126 LIVE cap-coada. Deciziile au temei in DECIZII.md; aici POINTER + commit-uri.

## Params listaMesajeFactura verificati la SURSA OFICIALA (5354c6d)
mfinante.gov.ro doc API (NU SmartBill, NU build vechi): filtru optional E=erori/T=trimisa/P=PRIMITA/
R=mesaj cumparator -> primire = filtru=P; zile 1..60 obligatoriu; limita 1500/zi/CUI; host OAuth
api.anaf.ro. Raspuns: id (descarcare), id_solicitare, data_creare, tip, cif_emitent, cif_beneficiar.
Persistat in ARHITECTURA_SPV.md ("verifica aici intai"). Functia efactura_send.lista_mesaje.

## F179 cron receive (48d0d6b) — tabel efactura_primite + pull
Tabel PER-TENANT efactura_primite: id_mesaj_anaf UNIC (dedup), cif_emitent/cif_beneficiar, xml_brut+sha,
status, factura_id NULL pana la four-eyes. Cron spv-receive.timer (30 min) listeaza filtru=P per tenant,
descarca facturile noi, insereaza CIORNA. TREI garduri: dedup ON CONFLICT DO NOTHING (fereastra suprapusa);
cif_beneficiar VALIDAT la insert (== CIF tenant, altfel SKIP anti-scurgere INTRE CHIRIASI); token mort ->
SKIP (auth-fail != eroare). Reutilizeaza lista_mesaje/descarca prin apel_anaf pe principal (partajat cu
F178, fara client paralel); principal_pentru_schema extras DRY. 4 teste + rulare reala prin stack.

## F126 pasul 5 — four-eyes (1838d7f) — LIVE
Ecran de validare (facturi_ecran.js, anatomia bonului OCR): date PARSATE + cont sugerat confirmat de om ->
Valideaza (creeaza cheltuiala + leaga factura_id) / Respinge (motiv, nu sterge). Rute in main.py, gard =
rol/acces la tenant + status=validata actiune umana explicita; idempotent FOR UPDATE.
FOUR-EYES la primite = MASINA (cron F179 = ochiul 1) vs OM (contabil = ochiul 2), NU doi useri fizici -
clarificat azi cu Costin. Grep INAINTE a confirmat ca regula creat_de != aprobat_de (doi oameni) traieste
DOAR pe declaratii_coada (corecta acolo), NU s-a propagat la primite. Cabinet cu UN contabil poate valida.
Conducta UNICA: valideaza reutilizeaza _factura_din_parsat (acelasi INSERT ca /import-efactura upload manual,
extras DRY) -> factura directie=primita -> intra AUTOMAT in verificatorul TVA existent (D300 vs 4426), nu
orfana. Coloane noi: motiv_respins, cont_cheltuiala. Backend dovedit HTTP cap-coada; ecran node+verificator 0.

## Registru
F126 -> LIVE (cap-coada: send + receive + four-eyes). F179 -> LIVE. F127/F128 raman AMANATE.

## LIMITA (onest, ca F176)
Round-trip-ul LIVE (trimite recipisa + primeste factura reala) se dovedeste doar cu un patron real cu CIF
cu drept SPV. Ecranul four-eyes testat cu ciorna INJECTATA (factura parsata, factura_id NULL). Necolorat verde.


---

# 18.07.2026 (partea 7 — noapte): e-Transport LIVE (F044+F121); clusterul SPV/OAuth complet

Continuarea aceleiasi zile. Dupa e-Factura cap-coada, e-Transport prin acelasi conector.
Deciziile au temei in DECIZII.md + ARHITECTURA_SPV.md; aici POINTER + commit-uri.

## F044 -> LIVE + F121 -> LIVE (commit-uri 5a12361 mecanism, 5a3c247 UI)
- F044 (generator XML UIT v2) -> LIVE: XML-ul merge acum la API prin F121, nu doar upload manual.
- F121 (trimitere prin API SPV) -> LIVE: mecanism (upload_uit/stare_uit/lista_uit prin apel_anaf pe
  spv_principal, fara client paralel) + orchestrator trimite (porti: timp -> idempotency -> validare pe
  TEST -> upload) + UI pe cardul F044 (buton Trimite UIT, avertisment de fereastra, lista UIT-uri).

## Drept UNIFICAT (verificat la sursa)
Acelasi token SPV acopera si e-Transport: JWT-ul poarta ambele roluri de serviciu (EFACTURA+ETRANSPORT);
OMFP 660/2017 = accesul SPV acopera toate serviciile. spv_principal REUTILIZAT, NU principal separat
(optiunea a). Per-CIF drept ramane empiric (403/fara drept). Vezi ARHITECTURA_SPV.md.

## Garda de timp UIT — specifica (diferenta de fond fata de factura)
fereastra_uit: declarare max 3 zile INAINTE de miscare; UIT valabil 5 zile (national) / 15 zile
(intracomunitar = AIC/tip 10). Folosire dupa expirare = BLOCATA. UI: DOUA semafoare distincte - de TIMP
(valabilitate) SEPARAT de cel de TRIMITERE (o notificare poate fi trimisa=verde dar cu UIT aproape
expirare=galben). Butonul Trimite blocat in afara ferestrei cu motiv (backend re-verifica autoritar).
Tabel etransport_trimiteri (dedup xml_sha256 pe prod - upload ANAF nu e idempotent).

## Endpoint-uri e-Transport (la sursa, DIFERITE de e-Factura)
Host OAuth api.anaf.ro, path ETRANSPORT/ws/v1, PARAMETRII IN PATH: upload/ETRANSP/{cif}/{versiune=2},
stareMesaj/{id}, lista/{zile}/{cif} - NU FCTEL/rest cu query ca e-Factura. NU exista validator fara auth
(ca validare/FACT1) -> poarta pre-trimitere = validare pe TEST (mediu=test). Persistat in ARHITECTURA_SPV.md.

## CLUSTERUL SPV/OAuth COMPLET
e-Factura: F176 (conector OAuth) + F177 (refresh) + F178 (poll recipise) + F179 (receive) + F126/F160
(send + four-eyes). e-Transport: F044 (generator) + F121 (trimitere). Un singur conector principal
(cabinet XOR gratuit), doua servicii, drept unificat. Restanta transversala UNICA: proba live pe CIF cu
drept SPV real (e-Factura si e-Transport) - cod complet + testat, necolorat verde in direct (ca F176).

# 19.07.2026 — Control incrucisat INTRE declaratii: F163 (D390) LIVE + F162 (D112) deorfanizat + F164 (alerte pull->push) + F184 (punte legislatie->re-verificare) + F185 (gard coliziune CUI invers) + F187 (export WinMentor) + verificator DS intarit (2 gardieni) + F188 (pre-completare ANAF v9)

Zi noua. Dupa clusterul SPV/e-Factura/e-Transport de ieri, intoarcere pe motorul de control fiscal.
Deciziile au temei in DECIZII.md (intrarea 19.07 F163); aici POINTER + commit-uri.

## F163 -> LIVE: D390 (bunuri IC) vs evidenta contabila validata (commit-uri 8c81ab5 engine, bba9f14 UI)
Extinde motorul control_incrucisat (D-vs-contabilitate, ca verifica_tva/verifica_d112) pe o pereche noua,
NU modul paralel. Bazele intracomunitare de BUNURI din D390 (livrari L / achizitii A, auto din facturi) vs
evidenta contabila VALIDATA a acelorasi facturi (nota validata; ciorna nu e dovada). Fereastra aliniata la
periodicitatea TVA (tip_decont): lunar 1 luna, trimestrial 3 luni insumate (D390 e mereu lunar).
REGULA DIRECTIONALA (VIES = sursa mai autoritara, partenerul a raportat pe latura lui):
- declarat la VIES DAR absent din evidenta validata = ROSU (remediu sugerat: contabilizeaza SAU corecteaza
  recapitulativa - omul confirma, nu e mecanic)
- invers (in evidenta, neraportat la VIES) = GRI (decalaj de perioada posibil)
- ambele>0 cifre diferite = GRI (decalaj exigibilitate art.284, regularizari, rotunjire = legitim - niciodata
  rosu pe cifre); ambele 0 = tacut.

## Descoperire de scop: D-vs-D real NU e fezabil azi (in DECIZII.md, verificat la sursa)
Randurile intracom ale D300 (R1_1 livrari, R5_1 achizitii) sunt MANUAL-ONLY (d300.calcul_d300 le ia doar din
'manual', prin body la declaratii_api.py) si NEPERSISTATE: declaratii_depuse (coada_api.py) e jurnal gol
(tenant/an/luna/tip/data, fara valori de randuri, fara XML depus). Un D300 regenerat ar da mereu 0 -> rosu pe
orice firma cu IC (zgomot); reconstruit din aceleasi facturi ca D390 -> verde trivial. Deci controlul INTRE
declaratii = D-vs-EVIDENTA-validata pana se persista decontul depus. v2 (prerechizit: persistarea randurilor
declaratiilor depuse -> abia atunci D-vs-D real; util si altor controale). Servicii IC (P/S) tot v2 (d300 nu
expune R3_1_1/R7_1_1).

## F162 -> LIVE: D112 (salarii) vs contabilitate — deorfanizat (commit bba9f14)
verifica_d112 exista de mai demult ca engine + teste, dar era ORFAN: 0 apeluri in UI, 0 randuri in registru
(confirmat prin grep). Un engine de control fara UI nu produce valoare pentru contabil. Deorfanizat: rand nou
F162 in FUNCTIONALITATI.csv + conectat in ecranul de control fiscal in aceeasi miscare cu F163.

## Ecran: grup "Declaratie vs contabilitate" (TVA + D112 + D390 la un loc)
Sectiunea din control.js itereaza peste toti 3 verificatorii D-vs-contabilitate sub un singur grup (contabilul
vede toate controalele intr-un loc), aceeasi anatomie: dot semafor + mesaj + temei + limita + remediu. Gri se
AFISEAZA gri (nu ascuns) - filozofia control_incrucisat: gri e informatie, nu absenta. In portofoliu, toti trei
ridica firma la ROSU (OR logic, consecvent cu tva) - altfel un stat de plata necontabilizat (d112 rosu) ar fi
invizibil la nivel de firma, exact riscul pe care portofoliul trebuie sa-l ridice. Filtrare anti-dublura pe
etichete (findarile apar o singura data). Reutilizare totala a claselor existente (cf-grup-titlu/cf-decl/
cf-incr-*) si a tokenilor de semafor (cap.8 DS) -> zero regula UI noua, verificator DS 0 candidate.

## Verificat
34/34 teste engine fara regresie (11 noi F163 pe cele 4 directii + 13 D112 + restul); verificator DS 0;
node --check ESM OK; restart serviciu -> HTTP 200, zero erori la boot. Functional real tenant_002 iunie 2026:
tva verde, D390 verde (IT livrare 5000 + DE achizitie 2000 contabilizate; rosu-sugerat pe aceleasi
necontabilizate; RO exclus corect), D112 ROSU real (282 impozit/1250 CAS/500 CASS declarate, dar
444/4315/4316=0 -> stat de plata necontabilizat - risc care inainte era invizibil la nivel de firma).

## F164 -> LIVE: alerte control fiscal pull->push in clopotelul existent (commit 7d1e02b)
Restanta 17.07 ("alertele fiscale nu ajung la om"): findingurile ROSII din control_incrucisat (tva/d112/d390)
se calculau DOAR la deschiderea manuala a ecranului (pull) - un stat de plata necontabilizat (D112 rosu)
ramanea invizibil daca nimeni nu deschidea ecranul. Diagnostic la sursa: problema NU era lipsa canalului
(clopotelul in-app exista, badge+panou+read-state) ci lipsa stratului de PUSH - findingurile nu erau conectate.
SOLUTIE (core/alerte_control_fiscal.py): NU canal nou. Cron zilnic AGATAT de core.notificari_scadenta (ruleaza
deja 08:00 - nu timer nou) itereaza firmele, si pentru fiecare cu ROSU nou/reaparut scrie O notificare AGREGATA
("Firma X: N controale in rosu (D112, D390)", link=control-fiscal:{tid}) in clopotelul CONTABILILOR
(validatorii_cabinetului - ei corecteaza, nu patronul). Doar ROSU se pusheaza; gri ramane pull (informatie, nu
actiune). NU atinge engine-ul si NU atinge ecranul (ramane pull, sursa de adevar).

## Gardul critic - dedup pe persistenta (public.alerte_control_emise, pattern alerte_emise/F103)
Cheie (tenant, verificator, perioada). Un rosu care PERSISTA neschimbat = O SINGURA alerta, nu una pe zi (altfel
spam zilnic pana la rezolvare -> contabilul dezactiveaza canalul). Re-notifica DOAR la verificator rosu NOU pe
firma SAU rosu rezolvat-apoi-reaparut (rezolvat -> sters din jurnal -> reaparitia conteaza ca nou). Doua rulari
aceeasi zi = o alerta (idempotent). Jurnalizeaza doar ce s-a LIVRAT efectiv (0 contabili -> retry cand apar
validatori, nu marca fals - descoperit pe tenant_002, al carui cabinet n-avea validatori). Tabel creat prin
superuser (owner iconta_user, ca notificari - PG15+ revoca CREATE public de la rolul aplicatiei).

## Routing pe click: notificarea deschide ecranul FIRMEI (commit 65c5eb1)
Click pe notificare (link=control-fiscal:{tid}) deschide ecranul de control fiscal FILTRAT pe firma respectiva,
nu portofoliul general (contabilul a dat click pe "Firma X are N rosii", vrea firma X). Param optional
randeazaControl(corp, nav, tidAuto) -> auto-drill in detaliul firmei reutilizand EXACT click-ul de rand
(detaliuFirma, obiect firma complet, aceeasi stiva). tid malformat -> log + fallback, nu ecran alb.

## Reparatie cauza-radacina: window._navGlobal era cod mort
Routing-ul clopotelului se facea prin window._navGlobal, dar acesta NU era atribuit NICAIERI -> cazul 'validat'
era cod mort (click nu ruta nimic). Handler-ul clopotelului e functie de modul, in afara closure-ului unde
traieste `nav`. Reparat minimal: window._navGlobal = nav la crearea navigatorului (realizeaza pattern-ul deja
presupus de cod), + cazul nou langa 'validat' (nu rescriu dispatcher-ul). Efect secundar intentionat: click pe
notificarea 'de_validat' acum chiar duce acasa (inainte nu facea nimic).

## Verificat (F164)
9 teste dedup PURE (rosu nou notifica; persistent NU; verificator nou notifica; rezolvat se sterge; rezolvat->
reaparut notifica; gri/verde zero push; doua rulari o alerta; text agregat) + 43/43 fara regresie. Functional
REAL tenant_002 iunie 2026 cu curatare (validator temporar): rulare1 livreaza 1 notif, rulare2 aceeasi zi 0
(DEDUP), rezolvat->reaparut a 2-a notif, gri 0 push. Routing: 7/7 parsare link in node (malformat->fallback;
'validat' intact) + curl HTTP real (token cabinet) /control-fiscal/2 = ruta deschisa de click intoarce firma
CORECTA (DANTE). node --check ESM + verificator DS 0 + rute existente byte-identice (cabinet.js/asistent.js neatinsi).

## F184 -> LIVE: punte legislatie->re-verificare v1 - conformitate cota TVA pe perioada (commit df0f450)
Ideea: cand o VALOARE legislativa se schimba, firmele afectate sa devina rosii - nu doar "legea s-a schimbat"
generic (monitor_fiscal). Diagnostic la sursa (FAZA 0): valorile fiscale sunt PARAMETRIZATE cu DATA in
common.COTE (cota() period-aware), NU hardcodate - deci fezabil. DAR verificatorii control_incrucisat (tva/d112/
d390 din push F164) NU consuma cota() -> re-rularea lor dupa o schimbare de valoare nu produce nimic (compara
declaratie vs contabilitate, ambele cu aceeasi cota). Golul = conecteaza checkuri VALUE-AWARE la push, nu re-rula.
SOLUTIE v1: verifica_tva_pe_cota (verificatoare.py) era PRIMITIVA ORFANA (zero apelanti), per-tranzactie,
period-aware, BLOCANT pe cota gresita. Deorfanizata printr-un wrapper la nivel de firma (control_incrucisat.
verifica_cota_tva + constatare_cota_tva PURA), NU rescrisa. Itereaza liniile facturilor EMISE ale lunii, cheama
primitiva per linie. Prinde cota veche folosita dupa schimbare (ex. 19% dupa 01.08.2025 cand standard = 21%,
Legea 141/2025). Declansator = cota() period-aware pe data facturii (COTE-driven).

## Gard anti-fals-pozitiv (F184)
Se verifica DOAR liniile la o cota din FAMILIA STANDARD (istoricul tva_standard, {19,21}). Cotele reduse (9/5) si
scutit NU depind de schimbarea cotei standard -> ignorate; altfel 9% ar aparea mereu "gresit" fata de 21% = rosu
fals pe orice firma cu cota redusa. Rosu doar pe cota clar gresita PENTRU PERIOADA; gri daca nu pot citi
facturile; verde/tacit daca toate liniile standard au cota corecta. Remediu sugerat (corecteaza cota - stornare+
reemitere/factura de corectie - omul confirma, nu se ajusteaza automat).

## Wiring F184 (reutilizare, nu paralel)
Pull: grup SEPARAT "Conformitate facturi emise" in ecran - NU declaratie-vs-contabilitate, ci conformitate a
facturii (aditiv, nu reorganizare -> DS 0). Push: verificator nou in alerte_control_fiscal, intra AUTOMAT in
dedup-ul F164 (decide() e verificator-agnostic pe seturi de chei). Cron zilnic EXISTENT (notificari_scadenta
08:00), portofoliu ridica firma la rosu. Declansator zilnic; COTE-driven proactiv la depasirea unei date = v2
separat (poate inutil - de decis dupa ce v1 merge).

## Igiena: reconciliere coliziune numere F
FUNCTIONALITATI.csv = sursa de adevar pt F-numbers (registrul canonic). Planurile din DE_FACUT "Iteratii viitoare"
primisera informal F162/F163/F164/F169, dar registrul foloseste deja acele numere pt features livrate azi/anterior
(F162=D112, F163=D390, F164=push, F169=control incrucisat TVA). Re-numerotate planurile care coliza la F180-183
(platitor_tva->F180, extindere control ramas D101/D100/D394->F181, cont_venit_implicit->F182, audit preluare->F183).
Comentariile stale din cod ("(F163)" pt D112 = F162 canonic) corectate. ISTORIA (aceasta) neatinsa - log datat.

## Limita onesta (F184, in DECIZII)
Nu verifica clasificarea de PRODUS (daca produsul chiar cere cota standard), doar coerenta de PERIOADA. Declansator
zilnic, nu instant - rosu apare a doua zi dupa schimbare (v2 daca instant conteaza). Cotele traiesc in COD
(common.COTE) - o lege noua tot cere editare + deploy, nu update de config. monitor_fiscal (text) ramane deconectat
de COTE (valori structurate) - proza informativa separata, nu declansator.

## Verificat (F184)
7 teste PURE constatare_cota_tva cu date reale via primitive period-aware (19% dupa 01.08.2025->rosu; 21%->verde;
19% inainte de schimbare->verde period-corect; 9% redus->NU fals-pozitiv; scutit->ignorat; mix->doar linia gresita;
temei+limita) + 50/50 fara regresie. Functional REAL tenant_002 cu curatare: factura emisa test 19% in 09/2025 ->
verifica_cota_tva ROSU-sugerat pe factura corecta; verificatori_rosii din push include 'cota_tva'; endpoint HTTP
/control-fiscal/2 (token cabinet) expune cota_tva_conformitate. Restart HTTP activ. node --check ESM + verificator DS 0.

## F185 -> LIVE: gard coliziune CUI directia inversa (cabinet->gratuit) (commit b8a598e)
Igiena cont gratuit / "CUI dublu emitent" (nota veche din DE_FACUT). Diagnostic la sursa (FAZA 0): NU e bug
deschis - riscul "acelasi CUI emite din doua locuri (cont gratuit + tenant de cabinet)" e deja DETECTAT de F092
(coliziune_gratuit_v1, 18.07): semnal la crearea tenantului de cabinet, poarta enforcement (cont suspendat nu
emite, auth_api:335), inchidere superadmin, auto-close RESPINS (GDPR - detinatorul decide). Tokenul SPV NU e
vulnerabil (apartine unui PRINCIPAL cabinet-XOR-gratuit, fiecare emite prin tokenul lui - nu cross-emisie).
ASIMETRIE gasita: F092 acopera doar gratuit->cabinet. inregistreaza_cont_gratuit (auth_api:301) verifica doar
conturile gratuite (un CUI = un cont gratuit), NU si daca CUI-ul e sub un cabinet -> un CUI gestionat de un
cabinet isi putea deschide cont gratuit self-serve NESEMNALAT.
REPARAT (F185, simetric): inregistreaza_cont_gratuit verifica si accounting_firm_id IS NOT NULL (reutilizeaza
pattern-ul F092 - regexp_replace pe cifrele CUI, activ=true) -> coliziune_cabinet; register_gratuit il propaga;
landing (login.js) opreste + avertizeaza ("acest CUI e deja gestionat de un cabinet contabil"). DOAR SEMNAL, NU
blocaj, NU auto-inchidere (aceeasi disciplina GDPR ca 18.07). Privacy: expune doar EXISTENTA (boolean), nu
numele/detaliile cabinetului.

## Reconciliere nota + rezidual
Nota stale "igiena cont gratuit / CUI dublu emitent" din DE_FACUT (era "punct de VERIFICAT") marcata ACOPERITA de
F092 (gratuit->cabinet) + F185 (cabinet->gratuit), nu falsa restanta deschisa. Rezidual: vizibilitate persistenta
(raport superadmin de coliziuni active - CUI cu gratuit + cabinet ambele activ=true) = F186 PLANIFICAT, complement
la semnalele EFEMERE de la creare, nu gard critic.

## Verificat (F185)
Functional REAL cu curatare verificata: (A) inregistreaza_cont_gratuit pe CUI-ul lui tenant_002 (sub cabinet) ->
coliziune_cabinet=True, contul SE CREEAZA (nu blocat); curatat (DROP schema provizionata + delete tenant+user),
verificat ca revine la tenant_001/002 (schema nou-creata era tenant_003 FRESH, nu cea istorica - fals alarma
verificata la sursa inainte de a continua). (B) CUI liber valid -> False. (C) CUI cu cont gratuit existent ->
CUI_EXISTA neschimbat. py_compile + node --check ESM login.js + restart HTTP 200.

## F187 -> LIVE: export contabil WinMENTOR (commit f4b6bbb)
Al doilea format de export catre programul contabilului, dupa SAGA (F171). Puntea "firma emite in iConta,
contabilul ramane pe programul lui". Serializer INI: DOUA fisiere text co-locate intr-un zip - Facturi.txt
([InfoPachet]/[Factura_N]/[Items_N]) + Articole.txt ([ArticoleNoi_<cod>]). WinMentor cauta articolul in
nomenclatorul lui; daca lipseste, in Articole.txt co-locat; altfel importul ESUEAZA (NU auto-creeaza) - de
aceea ambele fisiere. Cod articol DERIVAT determinist din descriere (A+sha1[:11]), CONSECVENT intre cele doua
fisiere (daca diverg, WinMentor nu gaseste articolul). Encoding Windows-1250 cu GARD: s/t moderne (virgula,
U+0219/021B) NU sunt in cp1250 -> normalizate la s/t cedila (forma legacy WinMentor), apoi encode STRICT;
caracter tot neencodabil -> 422 (nu byte gresit tacit - riscul BR-RO). Reutilizeaza conducta SAGA
(date_factura/facturi_emise_luna/_firma) ADITIV - date_factura extins cu serie/tert_oras, facturi_emise_luna cu
status optional; SAGA neschimbat. Endpoint /tenants/{tid}/facturi/export-winmentor -> zip.

## Verificare la SURSA OFICIALA (nu blog)
Structura extrasa cu pdftotext din PDF-urile OFICIALE WinMentor (download.winmentor.ro/.../22 Structuri import
din alte aplicatii/, Facturi clienti.pdf Rev.1.2 + Articole noi.pdf). Regula de aur a platit: BLOGUL GRESEA -
zicea ca denumireUM e in Articole.txt; spec oficial (linia 99-100): "Unitatea de masura implicita va fi preluata
din tranzactia importata" - UM vine din linia Facturi.txt, NU din Articole.txt. La fel, Clasa/GestiuneImplicita
apar GOALE in exemplele oficiale -> optionale. GATE corectat la sursa: facturi.status nu are 'validata' (ala e
pt note/e-Factura primite); valorile reale sunt 'emisa'/'de_preluat'/'anulata' -> gard = status='emisa'.

## Limita DECLARATA (in DECIZII, nu ascunsa)
WinMentor NU e self-contained ca SAGA (care era un XML cu descrieri libere). Dependenta de config nomenclator
WinMentor al cabinetului: clasa, gestiune, UM trebuie sa PRE-EXISTE; constanta "cod partener=cod fiscal" pt
CodClient=CIF. v1 = facturi de SERVICII + articole simple (Serviciu=D, ContServiciu=704, Clasa/Gestiune goale =
spec-valid). Stoc complex cu gestiune = v2/dependent de cabinet real. Daca un cabinet emite marfuri, se semnaleaza
ca exportul cere config, NU ca "merge automat". Round-trip real (import efectiv in WinMentor) = pending cabinet
real cu nomenclator configurat, ca proba SPV - cod+spec verificate, necolorat verde live.

## Bug latent reparat colateral (F171 SAGA month)
Ruta /tenants/{tid}/facturi/{factura_id} era NETIPATA -> capta literalele /facturi/export-saga si
/facturi/export-winmentor (factura_id="export-..." -> 422 int_parsing), umbrindu-le. Exportul-zip pe LUNA la SAGA
era nereachable inca de la F171 (18.07) - nimeni nu-l lovise (UI folosea export single-invoice). Fix: {factura_id:int}
-> literalele trec la rutele lor. Confirmat: WinMentor month 404-ruta-merge, SAGA month 200-reparat, detaliu factura
int 200-fara regresie.

## Ciel -> BLOCAT pe specificatie (nu planificat orb)
3 necunoscute verificate la sursa 19.07: (1) versiune - Ciel v6/v7/NextUp au formate DIFERITE (facturis.ro); (2)
spec neclar publica (nu exista portal oficial ca WinMentor); (3) cere coduri ANALITICE pe care iConta poate sa nu
le aiba la granularitatea Ciel. Se deblocheaza DOAR cu spec de la sursa Ciel / cabinet real care importa in Ciel.
NU se construieste pe sursa secundara (ar rupe importul, ca BR-RO). Notat [BLOCAT] in DE_FACUT.

## Verificat (F187)
11 teste (cod determinist+consecvent intre Facturi/Articole; structura ambelor fisiere camp cu camp contra spec
oficial; Item=cod;UM;cant;pret + Item_TVA; UM absent din Articole.txt; dedup articole pe cod; config override; gard
cp1250 s/t->cedila + caracter neencodabil->exceptie) + functional REAL tenant_002 cu curatare (factura status=emisa
cu diacritice -> ambele fisiere corecte, cod consecvent AD2090A939D5, cp1250 corect) + HTTP fara regresie. Restart activ.

## Verificator DS intarit: 2 gardieni noi (26->28), 3 candidati respinsi (commit ece61da)
Inventar DS (harta acoperit-automat vs manual): verificatorul = regex pe linii, scaneaza DOAR static/js/ecrane/
*.js -> prinde SEMNATURA TEXTUALA a unei abateri, NU randarea/asezarea/comportamentul. Mutat 2 reguli din manual
in automat (verificat o data, prins pe veci, protejeaza contra regresiei):
- ESC_LOCAL (cap.10, SECURITATE - prioritate): prinde variante locale de escaping (_esc/escB/escV/escS/escC/escJ)
  in loc de esc() canonic din api.js. Variantele omit apostroful -> risc XSS in atribute cu ghilimele simple.
  Cod 0 acum (curatat anterior), dar era NEPROTEJAT contra regresiei - un fisier nou cu _esc ar fi trecut.
- CASETA_ATENTIE (cap.5): #fdf3f3 inline in loc de clasa .caseta-atentie, simetric cu CASETA_INFO/POARTA_INLINE.
  Rafinat la sursa: exclus #fdeef2 (ala e zebra/landing - login.js pagina-card-mare, exclus DS cap.15) ca sa nu
  dea fals-pozitiv pe cod legitim.
TOTAL ramane 0 (ambii gardieni curati - nu introduc candidati falsi).

## 3 candidati de gardian RESPINSI ca neautomatizabili (fals-pozitive dovedite la rulare)
Principiu (ca la controlul fiscal): un gardian care aprinde pe cod CORECT e mai rau ca lipsa lui - erodeaza
increderea, ca un rosu pe diferenta legitima. Unde regex-ul pe linii nu distinge cert legitim-vs-gresit, se
raporteaza, NU se automatizeaza:
- card-inactiv fara 'activ' (cap.2b): gardianul a aprins 9 candidati in migrare.js care sunt PASI DE WIZARD
  (nr:, .mig-pasi), NU carduri firme-optiune - semnatura {cheie:...desc:...} e partajata intre tipuri de card,
  regex-ul nu distinge cert fara euristici fragile.
- panou gri-pe-gri (cap.16): "invizibil" depinde de PARINTE (panou alb vs corp gri) + prezenta bordurii - context
  de randare pe care regex-ul nu-l stie.
- background/border hex ad-hoc (cap.15): extinderea CULORI_HARDCODATE de la color: la background:/border: ar prinde
  prea multe bg-uri inline legitime -> zgomot.

## Ce ramane verificare vizuala manuala (neautomatizabil)
9 reguli DS randate/comportamentale: aliniere tabele (cap.4), anatomia ferestrei (cap.9), contrast randat gri-pe-gri
(cap.16/5), nimic-vizibil-decat-la-selectie (cap.2), navigare/setInapoi (cap.3), feedback butoane (cap.1), structura
semafor (cap.8), mesaje de stare semantice (cap.6), tabele PDF (cap.7). ~20-30 ecrane post-14.07 NEVERIFICATE vizual
(control fiscal, e-Transport, SPV, gratuit, WinMentor UI). Verificatorul e curat pe ele, dar nu prinde asezarea.
DE PRIVIT VIZUAL (nu confirmate violari): 3 background:var(--fundal) borderline - operatiuni_ecran:266 si portal:424
au bordura (vizibile), firme:1187 <pre> erori ambiguu - merita un ochi, nu clar gresite.

## F188 -> LIVE: pre-completare date firma din ANAF v9 la onboarding (commit 21ce813)
Scop: userul introduce CUI-ul la inregistrare -> iConta pre-completeaza automat datele firmei din API-ul PUBLIC
ANAF v9 (PlatitorTvaRest/v9/tva), userul confirma/corecteaza, nu tasteaza tot. Legal: datele propriei firme a
userului. Doua puncte de conectare: register-gratuit (F160, self-serve) + adaugare firma-client la cabinet.
Pre-completate: denumire (in formular), adresa/CAEN/nrRegCom/status TVA/TVA-incasare/activ (in firma_profil la
creare). ~80%% infra exista deja (anaf_api.valideaza_cui + endpoint /public/verifica-cui + /tenants/{tid}/verifica-cui
+ coloane firma_profil) - munca = extindere parser (2 campuri: nrRegCom + RTVAI.statusTvaIncasare) + gard
non-suprascriere + stocare in profil la creare (register_gratuit + tenant_creeaza).

## Garduri F188 (masina sugereaza, omul decide - ca four-eyes)
- NON-SUPRASCRIERE: ce a tastat userul manual NU se pierde (completeaza doar campul gol sau neatins de la ultima
  pre-completare ANAF). La stocare COALESCE: gol ANAF nu suprascrie existentul; 'nume' setat de user neatins.
  Datele ANAF pot fi stale -> campuri EDITABILE, userul corecteaza.
- DEGRADARE GRATIOASA: CUI invalid / ANAF 404 / ANAF jos -> valideaza_cui intoarce {gasit:False} (HTTP 200, nu
  exceptie) -> mesaj discret "completeaza manual", formular INTACT, nu crapa, nu sterge ce a tastat.
- DEBOUNCE 500ms: un apel per CUI complet, nu pe fiecare tasta (rate limit ANAF 1/sec).

## Bug latent reparat (F188) + campuri manuale
Parserul valideaza_cui citea 'codCAEN', dar v9 real intoarce 'cod_CAEN' (underscore) -> CAEN era GOL pe date reale.
Descoperit la apelul REAL pe 14399840 (regula de aur - verificat structura raspunsului real, nu presupus). Reparat
(citeste cod_CAEN cu fallback codCAEN). RAMAN MANUALE (v9 nu le are): telefon, email, IBAN, cod postal - marcaj UX
clar pre-completat vs de completat. Cod TVA intracom = VIES (serviciu SEPARAT, verifica_vies), NU amestecat in v9.

## Deviatie onesta (F188, in DECIZII)
NU am reorganizat UI-ul existent: register-gratuit foloseste buton "Verifica la ANAF" (pre-existent), cabinet
foloseste blur (pre-existent) - ambele pre-completeaza, dar DS zice reorganizarea existentului = STOP. oras/judet
NU se extrag inca din adresa structurata (adresa_sediu_social exista in v9) - flat adresa in v1, structurat = v2.

## F127/F128 re-check (20.07, consemnat ARHITECTURA_SPV.md)
Status NESCHIMBAT: SPVWS2 (/SPVWS2/rest/cerere) exista dar e READ-ONLY (interogare, fara depunere) -> F127 blocat;
auth SPVWS2 ramane mTLS certificat LOCAL (PKCS#11), incompatibil cloud/OAuth -> F128 blocat pe adaugarea OAuth de
catre ANAF, nu pe absenta API-ului de citire; niciun anunt ANAF de la 17.07; reevaluarea 17.08 ramane valida; nu e
gaura competitiva (nici SmartBill n-are mesaje SPV).

## Verificat (F188)
3 garduri dovedite FUNCTIONAL: (a) stocare pe tenant_002 cu ANAF real (14399840) - blank->UPDATE->verify->RESTORE
non-distructiv (caen=4754, reg_com=J2002000372404, adresa populate); (b) degradare gratioasa: /public/verifica-cui/99
-> {gasit:False} HTTP 200; (c) non-suprascriere (node): user tastat->NU se pierde, gol->completeaza, re-verificare->
update. Parser real intoarce nr_reg_com+tva_la_incasare noi + cod_caen reparat. node --check ESM ambele formulare +
verificator DS 0 + restart activ.

# 20.07.2026 — F133 tichete/bilete de valoare: Faza 1 (masa) + Faza 2a (vacanta) + Faza 2b1 (cadou)
Tratamentul fiscal 2026 verificat LA SURSA (nu din memorie - regulile s-au schimbat). Temeiul, alternativele
si limitele fiecarei faze in DECIZII.md (intrari 20.07 F133); aici POINTER + commit-uri + ce e LIVE.

**Faza 1 — tichete de masa (LIVE):** plafon (45 lei) in common.COTE cu data+temei; nr tichete = zile lucrate
(pontajul F135 e informativ - premisa "0 fara pontaj" RASTURNATA la sursa, step 3); CASS 10% + impozit 10% pe
valoarea nominala, in calcul_salariu; stat+fluturas+monografie (642=5328 acordare, 421=4316 CASS retinut);
D112 include tichetele, VALIDAT DUK izolat + real. Commits 1e40782, 73ea4ab, 9e71f37, 4204544.

**Faza 2a — tichete de vacanta (LIVE):** suma one-off/luna (beneficii_lunare), acelasi tratament fiscal ca masa
(CASS+impozit, FARA CAS/CAM); plafon neimpozabil informativ 6 salarii minime/an -> semnal "peste plafon anual";
stat/fluturas/monografie + UI "+ vacanta"; D112 include vacanta, VALIDAT DUK. Commits a3c901e, 66e4260, 16afca4, 2cf770b.

**Faza 2b (cadou) SPARTA:** 2b1 (neimpozabil <=300, cazul comun) acum; 2b2 (taxarea diferentei peste prag CA
SALARIU - CAS+CASS+CAM+impozit adaugat la brut, chirurgie pe calcul_salariu+D112) = AMANAT la caz real (rar).

**Faza 2b1 step 1 (model, cd3a487):** beneficii_lunare + coloana eveniment (4 legale: paste/craciun/8martie/1iunie
+ 'altul'), unique extins (salariat,an,luna,tip,eveniment) - un cadou per eveniment; beneficii_api: seteaza cu
eveniment + validare, lista_luna agregat (SUM/salariat), cadou_detalii_luna (per eveniment + flag taxabil).

**Faza 2b1 step 2 (stat/monografie/UI, ea3aee4) — DE AZI:** cadoul e NEIMPOZABIL (<=300/eveniment legal) -> NU
atinge calcul_salariu/D112. Facut vizibil: (a) stat_plata cadou total/salariat + flag cadou_taxabil (>300 sau
nelegal), inclus in total_disponibil (primit pe card, ca vacanta), FARA a atinge net/taxe; (b) fluturas: linie
"Tichete cadou (neimpozabil, pe card separat)" + in TOTAL DISPONIBIL, retinerea ramane doar pt masa/vacanta;
(c) monografie note_lunare: cheltuiala cadou 642=5328 pe valoarea TOTALA, adaugata separat de calcul_salariu
(5328 nu e cont D112 -> nu rupe control_coerenta); (d) firme.js: afisaj "cadou <suma>" + semnal ROSU "taxabil"
+ buton "+ cadou" cu selector eveniment + valoare. Test functional tenant_002: paste300+craciun500+altul100=900
-> taxabil True, net NEATINS, total_disponibil +900; doar paste300 -> taxabil False; nota 642=5328=300; fluturas
PDF valid cu cadou. LIVE (restart activ). RAMAS: Faza 2b2 (taxare peste prag) la caz real.

# 20.07.2026 — F134 plata salariilor pe card: fisier SEPA / ISO 20022 pain.001.001.03 (LIVE, fazat)
Din inventarul de deschideri (7 PLANIFICAT), atacat F134 - se sprijina pe salarizarea tocmai inchisa
(F133), dimensiune medie, fara dependente externe. Format ales de Costin (STOP, DECIZII 20.07 F134):
SEPA pain.001.001.03, NU proprietar pe banca - standard PUBLICAT verificabil la sursa, bank-agnostic.

**Step 1 (prereq IBAN, commit a93e4f3):** salariati.iban varchar(34) pe toate tenant-urile + template
(07_ddl_iban_salariat.sql). salariati_api.iban_valid() PURA - IBAN romanesc (RO + 24) + cifra de control
mod-97 (ISO 13616/7064), aceeasi disciplina ca CUI/CNP (un IBAN gresit trimite banii altcuiva). iban in
_CAMPURI_API + SELECT-uri + valideaza_salariat; SalariatIn/Edit. UI: camp in formular salariat + buton
"IBAN ✓/⚠" pe stat (editor inline, semnal cand lipseste). Test tenant_002: iban_valid pe exemplul standard
RO49AAAA1B31007593840000 -> True; corupt/scurt/non-RO/gol -> False; update+respingere IBAN gresit (422)+golire.

**Step 2 (generator, commit f240054):** core/plata_salarii.py genereaza_pain001(conn,schema,an,luna) ->
(xml, meta). SUMA = NET cash (aceeasi cifra ca D112); tichetele (masa/vacanta/cadou) NU se aduna - card de
beneficii SEPARAT, nu transfer bancar. Doar salariatii cu IBAN valid + net>0; cei fara IBAN -> EXCLUSI si
RAPORTATI (meta['fara_iban']), nu platiti tacit; firma fara IBAN / niciun IBAN -> ValueError. Diacritice
transliterate la charset SEPA; suma 2 zecimale HALF_UP. GARANTIA: XML validat pe XSD-ul OFICIAL
(sepa_surse/pain.001.001.03.xsd, de pe iso20022.org) INAINTE de download - refuz daca banca l-ar respinge,
ca DUK la declaratii. main.py: GET plata-salarii-preview (cati/total/cine fara IBAN) + plata-salarii-fisier
(download), auth ca stat-plata, ValueError->422. firme.js: buton "Fisier plata card (SEPA)" pe stat ->
preview cu avertisment rosu -> "Descarca". Gardian core/test_plata_salarii.py (11 teste pure: mod-97 +
charset SEPA + rotunjire) PASS. E2E autentificat HTTP tenant_002: preview {nr_plati:1,total:2968}, download
valid pe XSD, debtor!=creditor; izolat: multi-plata (2), fara_iban raportat, cai de eroare. tenant_002 curatat.
LIMITA (in DE_FACUT): fisier valid pe XSD-ul ISO, dar importul REAL intr-o banca anume (round-trip pe platforma
corporate) = de dovedit cu cont bancar real - aceeasi natura ca SAGA/WinMentor. Doar RON domestic (RO IBAN).

# 20.07.2026 — F137 coduri COR pe contracte: nomenclator national validat (LIVE), commit bf9cbd3
Al treilea item din inventarul de deschideri atacat azi (dupa F134). COR era free-text nevalidat; REGES
respinge un cod inexistent -> devine nomenclator VALIDAT la sursa. Temei/decizii in DECIZII 20.07 F137.

SURSA (STOP procurare - data.gov.ro inaccesibil din mediul de build, timeout; GitHub merge): Costin a
descarcat fisierul OFICIAL de pe data.gov.ro (dataset Clasificarea Ocupatiilor din Romania, lista alfabetica,
Ordin 573/180/2024, MO 344/12.04.2024) in cor_surse/cor2024.xml. Alternativa (copie GitHub) RESPINSA - regula
de aur cere oficialul. Fisierul e doc Word "Flat OPC" XML; lista in /word/document.xml = paragrafe alternand
cod (6 cifre) -> denumire. cor_incarca.py: 4422 ocupatii unice, auto-validat (refuza daca structura/cifrele difera).

MODEL: nomenclator NATIONAL -> tabel GLOBAL public.cor_ocupatii (08_ddl_cor_ocupatii.sql), NU per-tenant.
core/cor_api.py: cauta (cod prefix / denumire substring, diacritic-insensitiv pe coloana normalizata
denumire_cauta - numele au ă/î/ș/ț, userul tasteaza fara), exista, denumire. main.py GET /cor (orice user logat).
salariati_api._verifica_cor: codul se valideaza la creare+editare salariat (inexistent -> 422); import bulk ramane
lax (date migrare). REGES foloseste codul (deja validat) + versiune 10 (COR 2010/ISCO-08).

UI (firme.js): camp lookup "Ocupatie (COR)" in formularul salariat (cauti -> selectezi din lista, codul se
seteaza DOAR prin selectie, nu free-text) + buton "COR ✓/⚠" pe stat (editor inline pt angajatii existenti,
refoloseste acelasi lookup). stat_plata expune cor. Corectat token bordura inline (--linie, nu --bordura inexistent).

Test: core/test_cor.py (4 teste normalizare diacritice, de care depinde cautarea) + loader auto-valideaza 4422
coduri + E2E HTTP: /cor cauta dupa cod+denumire, validare creare/editare (263501 acceptat, 999999 respins), stat
include cor. 39 teste PASS (0 regresii), verificator DS 0 nou. LIMITA (DE_FACUT): nomenclatorul e SNAPSHOT (Ordin
573/180/2024) - la un ordin nou de actualizare se reruleaza cor_incarca.py; fluxul REGES AdaugareContract inca necablat.

# 21.07.2026 — F125 clasificare manuala D390: reclasificare + adaugare (LIVE, fazat)
Al patrulea item din inventarul de deschideri atacat (dupa F134, F137). Era doar avertisment; clasificarea
serviciilor (P/S) si triangulatiei (T/R) se facea IN AFARA aplicatiei. Temei/decizii in DECIZII 21.07 F125.

DECIZIE MODEL (STOP, Costin): RECLASIFICARE + adaugare, NU add-only. Constatare la sursa: d390.calcul_d390
mapeaza ORICE factura IC pe bunuri (emisa->L, primita->A); pt firme cu servicii IC facturate, add-only ar DUBLA
numararea. Alternativa "marcaj tip_d390 pe factura" (cea mai curata) amanata - atinge modelul facturi + emiterea.

Step 1 (model+backend, commit 6ead435): 2 tabele per tenant/an/luna - d390_reclasificare (override tip pe o
operatiune auto, per directie+partener: emisa L/T/P/R, primita A/S - INLOCUIESTE, nu adauga) + d390_manual (linii
pur manuale P/S/T/R fara factura). 09_ddl (owner iconta_user) + template. d390.calcul_d390(...reclasificari=)
aplica override-ul; genereaza AUTO-TRAGE din DB cand nu-s date explicit -> toate caile (wizard, pachet, control
incrucisat verifica_d390) vad aceleasi clasificari (rezolva nota veche "P/S raman v2"). _facturi_ic = sursa unica
a filtrului IC (calcul + operatiuni_auto, fara dublura). d390_clasificare_api: stare/salveaza_reclasificare
(valideaza tranzitia)/manual_adauga/sterge. main.py: 4 endpoint-uri /tenants/{id}/d390-clasificare.
DOVADA (regula de aur): XML cu reclasificare L->P + linie manuala S = stare VALID pe DUK (d390), fara erori.

Step 2 (UI, commit ff272aa): panou "Clasificare intracomunitara" pe PASUL 2 al declaratiei D390 (declaratii.js,
doar pt d390, additiv - nu reorganizez wizardul generic): lista operatiunilor auto cu selector de tip +
adaugare/stergere linii manuale + "Regenereaza D390". Fix endpoint: d390.pull are nume necalificate -> rezolv
schema cu o conexiune, apoi db.get_conn(schema) pozitionat (nu get_conn() simplu - dadea 500 pe stare). Formular
manual cu .camp + .camp-eticheta (regula DS ETICHETE_LIPSA), verificator DS 0 nou.
Test: test_d390.py 8 teste (+4 F125) PASS + E2E autentificat tenant_002 (reclasificare emisa IT->P reflectata in
stare, tranzitie ilegala emisa->A respinsa 422, reset sterge override, manual add + tara non-UE respinsa). curatat.

# 21.07.2026 — F120 educatie AI pe tipare: strat generativ peste F094 (LIVE)
Al cincilea item din inventarul de deschideri atacat (dupa F134, F137, F125). Stratul AI era prevazut inca de
la F094 (tipare_api docstring: "materia prima pentru viitorul strat AI ... AI-ul (stratul 5) va citi exact aceste
agregate"). Acum LIVE. Temei/decizii in DECIZII 21.07 F120.

Ce face: buton "Genereaza analiza AI" pe ecranul G (Tipare de erori, doar patron) -> Claude citeste agregatele
deterministe de respingere (motive/tipuri/firme, din tipare()) si intoarce o explicatie a tiparelor + 3-5
recomandari concrete. tipare_api.analiza_ai(conn, cabinet_id) + main.py GET /tipare/ai + tipare.js (buton + zona).

DECIZII cheie: (a) REFOLOSIRE core.ai_client, nu client paralel - model ales DELIBERAT de proiect
(claude-sonnet-4-6, "echilibru calitate/cost pentru narativ"); NU l-am suprascris cu opus fiindca alegerea de
model e o decizie deja in cod (skill claude-api: default opus e pt cod NOU, aici e conventie stabilita). (b)
GROUNDING (regula de aur pe AI): promptul da DOAR agregatele reale, sistemul interzice inventarea cifrelor/
firmelor/motivelor, temperatura 0.4. (c) ON-DEMAND: apel platit -> doar la buton, nu automat la deschidere;
fallback curat daca ai_client.disponibil()==False sau lipsa date (mesaj, nu eroare).

Test (regula de aur): apel Claude REAL pe cabinet cu respingeri fabricate -> analiza structurata in romana (tipare
+ 5 recomandari), GROUNDING confirmat (mentioneaza CUI/CAS + firma din datele reale, nu inventeaza); fallback fara
date ("nu exista respingeri") + cheie lipsa. Date de test curatate din declaratii_coada. verificator DS 0 nou.
LIMITA (DE_FACUT): analiza e SUGESTIE AI, nu verdict (contabilul o cantareste); nu se persista (regenerare la cerere).

# 21.07.2026 — F187 UI: butonul WinMentor cablat (drift de registru corectat)
Iesit la iveala din auditul vizual al celor 4 ecrane post-14.07: F187 (export WinMentor, LIVE 19.07 in backend -
export_winmentor.py + endpoint + 11 teste + spec oficiala) NU avea buton in frontend - zero "winmentor" in
static/js/. Registrul (FUNCTIONALITATI.csv F187) afirma totusi "Facturi (buton export luna)" = buton FANTOMA.
Drift: registru LIVE-cu-UI vs realitate LIVE-doar-backend; exportul inaccesibil din aplicatie. Decizie Costin
(varianta c): cablez butonul SI aliniez registrul, un commit. Vezi DECIZII 21.07 F187.

Buton "Export WinMentor luna" langa "Export SAGA luna" (Istoric facturi). Pattern identic cu SAGA (buton-secundar,
fetch zip cu Bearer, download, 404->info, mesaj ok cu calea import MENTOR->INTERNE->Facturi iesire) + feedback async
cap.1 CORECT (dezactivare + "Se genereaza..." - pe care SAGA nu-l face). Registrul F187 acces UI aliniat la realitate.
DOVADA prin fluxul butonului: flip temporar factura tenant_002 la emisa+diacritice -> export prin URL-ul exact al
butonului = HTTP 200, zip Facturi.txt+Articole.txt, cp1250 valid, ș/ț->cedila legacy ("Consultanţă ŞI mentenanţă"),
caracter neencodabil (emoji)->422; factura restaurata, tenant_002 curat. node-check + verificator DS 0 nou. Restart activ.
RAMAS din audit: control fiscal / e-Transport / SPV+gratuit inca de privit cu ochii (checklist dat 21.07); WinMentor
UI acum EXISTA de verificat. LIMITA: round-trip real import WinMentor pending cabinet configurat.

# 21.07.2026 — Audit vizual 4 ecrane (partea automatizabila) + 2 findings ISO/bani reparate
Auditul celor 4 ecrane post-14.07 (control fiscal / e-Transport / SPV+gratuit / WinMentor): partea automatizabila
= grep pe sursele JS care produc DOM-ul (SPA client-side -> curl da doar shell-ul, nu DOM randat) + date API.
Rezultat baseline: empty-state .stare-goala prezent pe toate 4; ICOANE rezolva (shield etc.); WinMentor buton+async+
nume fisier OK; portal client = doar ecrane read-only (zero actiuni cabinet); dedup alerte control IMPLEMENTAT
(dejaInIncrucisat). DOUA findings reale prinse de grep (DS cap.4, nu prinse de verificator - string calculat, nu
${x.data} in innerHTML), reparate acum:

1. e-Transport (etransport_ecran.js): date ISO brute in loc de dataRo. Mesajele time-gate (:22 transport ${dataTransport},
   :23/:24 valabilPana.toISOString()) + lista "UIT-uri trimise" (:186 u.data_transport) -> toate prin dataRo() (zz.ll.aaaa).
   Extins la :22 (acelasi dataTransport brut, aceeasi clasa - altfel 1 din 3 branse ramanea ISO). import + dataRo.
2. Control fiscal per-firma (firme.js:457): sold_contabil / valoare_fise_cv / diferenta afisate RAW -> prin bani()
   (1.234,50 nu 1234.5), pe verificarea "Stocuri contabil vs fise CV".

Cache-bust: etransport_ecran.js?v=1->2 (firme.js), firme.js?v=4->5 (cabinet.js + asistent.js). DOVADA (regula de aur):
dataRo/bani rulate VERBATIM (sursa api.js) pe intrarile reale -> "2026-07-24"->24.07.2026 (si cu ora), 1234.5->1.234,50,
-89.9->-89,90, 1234567.8->1.234.567,80. node-check 4 fisiere + verificator DS 0 nou. Fara restart (doar frontend).
RAMAS strict pentru ochi (Edge, negrepabil): aliniere/spacing, contrast gri-pe-gri, culorile efective ale semaforului,
.buton-activ pe toggle, fereastra fara scroll orizontal - vezi checklist-ul 21.07.

VERIFICARE VIZUALA (Costin, Edge) — e-Transport INCHIS: (a) rand UM/greutati era cu baseline rupt (input "Greutate
bruta" mai jos) - cauza: grid inline pe .camp flex-column cu eticheta lunga rupta pe 2 randuri, input coborat. Fix:
randBun -> clasa canonica "grila-campuri grila-campuri-compacta" (DS cap.9/16, pattern operatiuni_ecran.js:310) -
.grila-campuri .camp {justify-content:flex-end} aliniaza inputurile jos + fundal alb (era gri-linie). align-items:start
NU rezolva (aliniaza varfurile celulelor, nu inputurile). (b) simetrie etichete: "Greutate neta/bruta (kg)" -> "Gr.
neta/bruta (kg)" (ambele, doar in e-Transport - grep confirmat neregasite altundeva) ca sa incapa pe un rand.
Data transport zz.ll.aaaa confirmata. Confirmat vizual. Cache-bust etransport?v=2->4.

VERIFICARE VIZUALA — Control fiscal INCHIS: blocul "Verificari contabile (N)" din drill-down-ul firmei (control.js:193,
dashboard cabinet - NU ecranControlFirma/firme.js care e curat) randa problemele ("solduri creditoare trezorerie" etc.)
cu clase imprumutate din ecranul de migrare solduri: .mig-sold-cont (color var(--albastru)+bold+monospace = arata ca
link) + .mig-sold-rand (grid de solduri, context gresit). FARA handler -> buton mort din cauza stilului, nu drill-down.
Decizie: text informativ, nu drill-down (remediul actionabil = butonul cf-incr-btn, separat, cablat) -> scos stilul de
link, aliniat la pattern-ul canonic de constatare (cf-incr-rand + cf-incr-cap + punct rosu CULORI.rosu.dot + text normal),
esc(p) adaugat, clase mig-sold-* eliminate. Confirmat vizual (text cu buline rosii, nu link). Cache-bust control.js?v=1.

# 21.07.2026 — F197 previzualizare portal client din cabinet (feature nou, decizie iunie neonorata)
Diagnostic (la cerere): "Acces Client" preview (buton -> portal in tab nou, #acces, ruta acces-portal) N-A existat
niciodata (git -S zero); in iunie s-a construit INVITATIA email ("Acces client", card in meniul firmei), alt mecanism.
Costin a cerut sa livram acum preview-ul. Temei/decizii in DECIZII 21.07 F197.

MODEL: token client REAL al firmei, marcat preview=True in payload (auth_api.construieste_payload/context_din_token).
Ruta NOUA POST /tenants/{id}/acces-portal (cere admin_firma/angajat) -> gaseste userul client activ al firmei
(user_tenants, rol=client), emite token preview; firma fara client -> 400 cu indrumare. NU refolosire client-acces
(alea-s pt clientul real). READ-ONLY PE BACKEND: middleware _preview_readonly_guard - token preview + metoda mutanta
-> 403, GET permis (bypass-proof, nu ascuns butoane). Frontend: sesiune.intraPreview (token IN-MEMORY, nu sessionStorage
-> sesiunea cabinet intacta; logout = window.close()); app.js #acces=<token> (regex cu punct, e JWT) -> cade in switch
(client -> portal); buton "Previzualizeaza portalul" in ecranul Acces client (fisa firmei, nu card nou); banner
.caseta-info in desktopPortal cand estePreview() (DS cap.5 - info neutra albastra, nu rosu).

DOVADA (regula de aur): E2E autentificat pe user client temporar (tenant 2) - cabinet emite preview (HTTP 200,
preview=True), GET /portal/firme 200, POST mutatie 403 ("Previzualizare - doar vizualizare"), firma fara client (tenant
1) 400; user temporar sters. node-check 6 fisiere JS + PY OK + verificator DS 0 nou. Cache-bust portal?v=9, firme?v=6;
app.js + sesiune.js neversionate intentionat (singleton) -> hard-refresh o data. Restart activ. F197 LIVE in registru.

# 21.07.2026 — INFRA nginx: /static/ scutit de rate limit pe nou-iconta (fals-alarma "bug preview")
Pagina alba pe prod (nou.iconta.eu) la load portal: console 429 pe module ES. NU bug de cod - rate limiting nginx.
Regresie de config: config vechi iconta avea "location /static/" fara limit_req; config nou nou-iconta l-a pierdut ->
/static/ cadea sub "location /" (zona iconta_gen 20r/s burst 60, pt API). SPA cere zeci de module in rafala/load +
_StaticNoCache (no-cache -> revalidare) + preview deschide tab nou (dubla rafala) -> bucket golit -> 429 -> alb.
FIX: adaugat "location /static/ { proxy_pass 127.0.0.1:8010; }" FARA limit_req inainte de "location /" (mirror config
vechi). Procedura prod: backup nou-iconta.bak-21iul -> insert (python, nu sed) -> nginx -t TRECE -> systemctl reload
nginx (zero downtime) -> verificat 40x /static/js/app.js = 40x200/0x429, API inca trece. Detaliu + de ce in DECIZII 21.07.
DE_FACUT (secundar): Cache-Control immutable pe ?v=. NOTA: nginx e INFRA (nu in repo) - decizia+procedura raman aici.

# 21.07.2026 — F197 FIX: preview portal spargea read-only (token in-memory fragil) + banner lipsa
BUG critic raportat de Costin (test vizual): in preview a putut trimite o solicitare (scriere client reusita) +
bannerul lipsea. Diagnostic la sursa (reprodus): BACKEND-UL E CORECT - POST /portal/solicitari cu token preview -> 403,
cu client real -> 200. Bug in FRONTEND: bannerul lipsea -> estePreview()=false -> intraPreview nu pusese tokenul
preview -> tab-ul folosea alt token (in-memory _tokenPreview pierdut la re-render/reload -> fallback pe sessionStorage
copiat de window.open -> non-preview -> mutatia trecea). FIX: token preview mutat de la in-memory la CHEIE PROPRIE in
sessionStorage (iconta_pv_token, per-tab izolat, precedenta absoluta) -> determinist, supravietuieste reload, tab-ul
preview foloseste DOAR tokenul preview. Banner: .caseta-info -> .caseta-atentie (rosu, proeminent, cerut vizibil).
Backend-ul (guard _preview_readonly_guard) e backstop-ul. DOVADA: reprodus 403 preview / 200 client; node-check +
verificator 0. Cache-bust portal?v=10; sesiune.js/app.js no-cache (nginx serveste /static/ dupa fix-ul de azi).

# 21.07.2026 — F197 FIX (2): preview cadea pe portalul GRATUIT (context de tenant lipsa)
Dupa fix-ul de read-only/banner (F197 FIX 1), a doua carenta vizuala: preview-ul DANTE arata portalul de
FACTURARE GRATUITA (4 carduri, "firma ta") in loc de portalul client gestionat (9 zone: Solicitari/Documente/
Povestea lunii, nume "DANTE INTERNATIONAL SA"). Diagnostic la sursa: _eGratuit() (portal.js:21) = rol==="client"
&& !tenant_are_cabinet. Preview fabrica user {rol:"client"} fara tenant_are_cabinet -> !undefined=true -> gratuit.
FIX (3 fisiere): (1) main.py acces-portal intoarce {token, user:{rol, nume_tenant, tenant_are_cabinet}}, calculat
din public.tenants pe tenantul previzualizat (nume + accounting_firm_id), la fel ca la login (_tenant_client).
(2) firme.js: userul trece prin URL catre tab-ul nou (URLSearchParams #acces=<token>&u=<json>) — necesar fiindca
window.open cara doar URL-ul, nu obiectul din raspunsul POST. (3) app.js: citeste u din URL, il paseaza la intraPreview
(fallback {rol:"client"} daca lipseste). DOVADA: curl real pe endpoint (tenant 2) -> nume_tenant="DANTE INTERNATIONAL
SA", tenant_are_cabinet=true; scriere cu token preview=403, citire=200 (guard intact); node --check ambele JS OK;
verificator DS fara neconformitati noi. De ce prin URL si nu doar prin raspuns -> DECIZII 21.07 F197.

# 21.07.2026 — F187 FIX: Export WinMentor lunar nu descarca nimic (filtru status gresit)
BUG (Costin, DANTE iunie 2026): "Export SAGA luna" descarca zip, "Export WinMentor luna" nu face nimic la click.
Diagnostic la sursa (curl real, acelasi tenant/luna): SAGA 200/zip, WinMentor 404 "nicio factura emisa". Frontend
identic (facturi_ecran.js 216 vs 229) — ambele lovesc ruta corecta, dar WinMentor 404 -> handler arata mesaj "info",
zero download. Cauza in DB: cele 2 facturi emise DANTE (ALTEX/AUCHAN) au status='de_preluat', dar export_winmentor
cerea facturi_emise_luna(status='emisa') -> 0. 'emisa' ca STATUS nu se seteaza nicaieri (grep); 'de_preluat' e
starea normala a facturii emise. FIX: scos filtrul status='emisa' din export_winmentor.export_luna -> paritate cu
SAGA (aceleasi facturi in ambele). Actualizate docstring-uri + mesajul 404. DOVADA: curl DANTE dupa fix -> 200, zip
cu Facturi.txt (2 facturi ALTEX+AUCHAN) + Articole.txt; pytest 13 passed (11 vechi + 2 regresie: status nefiltrat,
factura de_preluat inclusa). SAGA neatins. De ce + limita (anulata/storno neexcluse in ambele) -> DECIZII 21.07 F187-fix.

# ============================================================
# === Sfârșit de zi 21.07.2026 (recap consolidat) ===
# ============================================================
# Sinteză peste intrările per-task de mai sus (F125, F120, F187 UI, audit vizual, F197, nginx, F187-fix).
# ICONTA_STATUS.md NU se recreează — e înglobat aici (CLAUDE.md, o singură sursă). Detaliul + commit-urile
# fiecărui task rămân în intrările proprii de mai sus și în git log; aici doar CE s-a închis, grupat.

## ÎNCHIS AZI (verificat)

1. AUDIT VIZUAL 4/4 — findings prinse DOAR cu ochiul/mâna pe buton, nu de grep/verificator/teste:
   - e-Transport: rând UM/greutăți re-aliniat + simetrie etichete (dd8a6e8, cf9d7ae).
   - Control fiscal: „Verificări contabile" nu mai arată ca link mort → text clar (0cffaf9, cf9d7ae).
   - SPV/gratuit: preview portal + guard read-only + banner (parte din F197, vezi 3).
   - WinMentor UI: butonul „Export WinMentor lună" cablat (drift de registru corectat, 9b52388).
   META-LECȚIE: cele 11 teste unitare F187 treceau fără să atingă DB → butonul real pica pe date reale
   (DANTE, status='de_preluat'). Auditul vizual cu mâna pe buton a fost SINGURUL care a prins-o. De aici
   regula: după orice feature cu buton→rută→date, o probă vizuală pe date reale, nu doar teste unitare verzi.

2. F197 PREVIZUALIZARE PORTAL CLIENT din cabinet (feature nou, decizie iunie neonorată → onorată):
   buton „Previzualizează portalul" pe fișa firmei (Acces client), guard read-only pe BACKEND (token
   preview → 403 pe orice scriere, confirmat curl 403/200), banner PREVIZUALIZARE proeminent, și fix-ul
   de context tenant (userul cu nume_tenant+tenant_are_cabinet trece prin URL → portal client corect, nu
   cădere pe „Facturare gratuită"). Commit-uri: f065cda, d90b1e5, 9096ac9.

3. REGRESIE INFRA nginx /static/ (429 pe prod): config nou-iconta aplica rate limit și pe modulele ES →
   429 → pagină albă (fals-diagnosticat inițial ca „bug preview"). Exceptare limit_req pe /static/
   restaurată (da89307). Infra, nu în repo — procedura + de ce în DECIZII/ISTORIC 21.07.

4. WINMENTOR STATUS-FIX (F187-fix): filtrul status='emisa' excludea facturile 'de_preluat' (starea NORMALĂ
   a facturii emise) → 404 pe toate facturile reale, deși SAGA le exporta. Scos filtrul → paritate SAGA.
   Dovadă: curl DANTE 200 + zip (ALTEX+AUCHAN); pytest 13 (11+2 regresie). Commit 7c67aec, DECIZII 21.07.

## DESCHIS (mutat în DE_FACUT.md, nu se pierde)
- Cache-Control immutable pe asset-uri versionate ?v= (deja în DE_FACUT §4, optimizare, nu blocant).
- Breadcrumb/subtitlu preview „Facturare gratuită" — de privit vizual pe cazul gratuit real.
- Nume fișier la descărcarea balanțelor — uniformizat cu tiparul export_<tip>_<an>_<luna>.

## STARE GRUPURI
- GRUP C ÎNCHIS: e-Transport + Control fiscal + SPV/gratuit + WinMentor — toate confirmate vizual.

## RESPINS azi (zero cod, verificat la sursă)
- Exclude 'anulata'/'storno' din exporturile SAGA+WinMentor — RESPINS: facturile n-au acel status (doar
  emisa/de_preluat), iar excluderea notei de credit (storno = factură negativă cu storno_din_id) dintr-un
  export de DOCUMENTE ar rupe contabilitatea din programul destinație (reversarea n-ar mai intra în cărți).
  Temei complet + limita (dacă apare vreodată anulare-ca-status) în DECIZII 21.07.

# 21.07.2026 — F182 LIVE: cont venit implicit setabil din UI (Date firma > Cont contabil)
Enhancement Grup D (UI+DB, non-core). Pana acum cont_venit_implicit (folosit la contabilizarea facturii,
main.py:5853 COALESCE(...,'707')) se putea schimba doar direct in DB. F182 adauga:
- BACKEND (firma_profil_api.py): CONTURI_VENIT derivat din plan_omfp (clasa 70: 701/704/705/706/707/708),
  cont_venit_valid() (respinge 76x/74x/78x + typos), citeste_date intoarce valoarea + optiunile, salveaza_date
  valideaza la sursa (cont invalid -> 422). Motorul contabil NEATINS (citea deja coloana).
- FRONTEND (date_firma.js): sectiune noua "Cont contabil" cu select (pattern canonic .camp/.grila-doc, DS cap.6/9),
  APENDAT dupa Vector fiscal (nu reorganizare). Salvarea trimite cont_venit_implicit prin /firma-profil/date existent.
DOVADA (HTTP end-to-end tenant_002): GET intoarce cont+optiuni; set 704 -> 200, persista la GET; invalid 999 -> 422
cu mesaj clar; query exact de la emitere intoarce 704 dupa set; restore 707. node --check ESM OK; verificator DS 0.
Registru: F182 LIVE. De ce clasa 70 si nu toata clasa 7 -> DECIZII 21.07 F182.

# 21.07.2026 — F186 LIVE: raport coliziuni CUI active (superadmin), complement persistent la F092/F185
Enhancement Grup D (non-core, GDPR signal-not-block). F092 (gratuit->cabinet) si F185 (cabinet->gratuit)
semnaleaza coliziunea de CUI DOAR la momentul evenimentului (efemer); superadmin n-avea unde vedea lista curenta.
- BACKEND (main.py): GET /admin/coliziuni-cui (guard superadmin) - self-join pe public.tenants cu match pe
  cifrele CUI (aceeasi conventie regexp ca F092/F185), gratuit (accounting_firm_id NULL, activ) x cabinet
  (NOT NULL, activ), + nume cabinet + nr facturi emise din gratuit. Live read, zero materializare (zero drift).
- FRONTEND (admin_gratuite.js): sectiune .dec-avert sus in ecranul Facturare gratuita; buton "Suspenda gratuitul"
  reutilizeaza ruta existenta /admin/conturi-gratuite/{id}/suspenda pe contul gratuit. Report-only, nimic automat.
DOVADA: detectie SQL cu coliziune fabricata in tranzactie ROLLBACK -> 1 rand cu numele cabinetului (AMZUICA...),
0 randuri ramase dupa rollback (zero mutatie persistata); endpoint 200 superadmin {coliziuni:[]} pe date curate,
403 non-superadmin (guard); node --check ESM + verificator DS 0. Registru: F186 LIVE. De ce live+report-only -> DECIZII 21.07.

# 22.07.2026 — F183 audit de preluare LIVE + fix login bounce tacit + clasa BACKEND_UI_BRUT inchisa (canonice backend + garda .py)
Patru fire: un feature nou (F183), un bug de UX prins de Costin (login), o clasa de abateri DS inchisa la sursa
(sume/date brute in backend), si doi candidati JS reziduali. Commit-uri: 8d0eae2, 75eae8e, 6e23954 (F183);
9de75ea (login); cd988a6, 73b0094, b919d81 (BACKEND_UI_BRUT); 4e3c0a3 (firme.js); 301a6bc (F183 regim).

**F183 audit de PRELUARE firma (LIVE, core/audit_preluare.py).** Cand un cabinet preia o firma cu istoric de la
alt contabil, verifica COERENTA INTERNA a pachetului importat si raporteaza transparent ce se poate / nu se poate
verifica (3 stari: coerent/divergent/NEVERIFICAT). Motor SEPARAT de control_incrucisat (nu "acelasi motor la
migrare" cum era conceput in DE_FACUT): la preluare ambele surse sunt EXTERNE (documente de la contabilul
anterior), nu declaratie-generata-in-iConta vs note-iConta; ruland control_incrucisat pe luna preluata rulaje=0
-> rosu fals pe tot. Reutilizeaza doar ANATOMIA (stari+temei+remediu) + solduri_api.verifica_echilibru +
solduri_parteneri_api.coerenta. SCOP v1 (DA gate): balanta echilibrata + Sigma parteneri=sold sintetic + solduri
fiscale vs istoric declaratii (SEMNAL gri, nu rosu) + RIP PFA (sold implicit ne-negativ + operatiuni clasificate).
Locatie: fisa firmei > Control fiscal > buton "Audit de preluare", REPETABIL, regenerat la cerere (fara tabel
snapshot - derivabil din documente, zero drift). ANTET: "Firma in iConta din <data>" (creat_la, proxy preluare,
NU data legala de preluare) + "Audit rulat <data cu ora>" (doua rulari/zi se disting). RAMIFICARE PE REGIM
(rafinare aceeasi zi, gate Costin optiunea 1): audit() citeste tip_firma via migrare_api.straturi_pentru (SURSA
UNICA regim->straturi, zero drift) - PFA (partida simpla) ruleaza DOAR RIP; verificarile de partida dubla NU apar
(un gri "importa balanta" ar fi remediu IMPOSIBIL la partida simpla). Aparare: core/test_audit_preluare.py (12
teste pe nucleele PURE + test PFA doar-RIP + non-regresie SRL); E2E rollback tenant_002. Registru F183 LIVE.
De ce motor separat + scop + ramificare regim -> DECIZII 22.07.

**Fix login bounce TACIT (9de75ea).** Credentiale gresite pe login -> intoarcere in ecranul de logare FARA mesaj
(refuz tacit, incalca "nimic nu se blocheaza fara motiv"). Cauza la sursa (api.js): ORICE 401 declansa
sesiune.iesi() + arunca "sesiune expirata" generic. Dar /auth/login intoarce LEGITIM 401 la credentiale gresite
({"detail":"email sau parola gresite"}); la login NU e sesiune de expirat -> iesi() re-randa ecranul, detasand
nodul unde login.js scria mesajul (scriere in nod mort = bounce tacit), iar mesajul real era ARUNCAT si inlocuit.
FIX: 401 declanseaza logout DOAR daca s-a trimis un token (aveam sesiune): `if (r.status===401 && token)`. Fara
token -> cade pe handlerul normal care citeste date.detail. Toate caile de esec au acum mesaj explicit (credentiale
/ cont inactiv / cabinet suspendat / rate limit 429 prietenos / server 5xx). Verificat la sursa: curl 401 corect
dintotdeauna, doar frontendul il inghitea. Confirmat vizual de Costin.

**Clasa BACKEND_UI_BRUT inchisa (cd988a6, 73b0094, b919d81; DESIGN_SYSTEM v2.15 cap.4).** Diagnostic la sursa:
garzile DS (BANI/DATA/DIACRITICE) scaneaza DOAR .js (verificator os.listdir cu endswith('.js')) -> text formatat
in backend care ajunge la user scapa COMPLET (dovada: F183 arata "40800.00 lei" brut). PASUL 1: reparate ~20 situri
de sume - control_incrucisat (16, ecranul Declaratie-vs-contabilitate), common.problema (central, bani pe MONEDA_
CAMP -> toate alertele plafon/TVA/balanta "5.000,00 lei"), d112/taxare_inversa/main. FALS-POZITIV corectat: d300:273
era deja formatat (_f cu separator de mii) -> revertit. PASUL 2: canonic NOU pdf_util.data_ro (oglinda Python a
dataRo din api.js, langa bani) adoptat unde se formatau date pentru user (sinteza_zilnica email, scadente, chitanta);
GARDA BACKEND_UI_BRUT scaneaza .py dupa sume/date brute in campuri user-facing (mesaj/temei/cauza/motiv/avert/
descriere/actiune), cu heuristici anti-fals-pozitiv: SUME doar f-string/%-format (sabloanele .format din CODURI
formatate central), DATE doar strftime("%d...") = display uman (isoformat/%Y = ISO/XML/JSON/log excluse), "%s lei"
= pre-formatat. EXCEPTII documentate: XML/SAF-T (etransport, d406), export_winmentor, unitati :g, comentarii. Norma
simultan in DESIGN_SYSTEM v2.15 + verificator + DECIZII 22.07. Diacriticele audit_preluare.py corectate (cd988a6).

**2 candidati JS reziduali din firme.js (4e3c0a3) -> verificator TOTAL 0.** :2048 <input type=date value=${aziIso}>
= FALS-POZITIV (value pe input type=date TREBUIE ISO, cerinta HTML; default pe filtru raport = UX corect) -> rafinat
PRECOMPLETARI sa excluda input-urile native de data/timp. :2038 <input placeholder> fara label = BUG REAL a11y
(placeholder dispare la tastare, nu e eticheta accesibila) -> fix aria-label. verificator TOTAL 0.

**Fir 5: test_spv_conector rosu permanent inchis (65c8baf).** test_url_autorizare_contine_parametrii picase
constant in suita completa (dar trecea IZOLAT). Cauza reala (verificata la sursa - NU env lipsa cum paruse):
spv_conector citeste ANAF_CLIENT_ID/REDIRECT_URI la IMPORT (constante de modul, :39-46); setdefault-ul din
test_spv_conector.py rula PREA TARZIU cand alt test importa modulul tranzitiv (via main) INAINTE -> constanta
inghetase goala. FIX: cele 4 setdefault (SPV_FERNET_KEY/JWT_SECRET/ANAF_CLIENT_ID/ANAF_REDIRECT_URI) mutate in
core/conftest.py (incarcat de pytest INAINTEA colectarii -> inaintea oricarui import de modul, indiferent de
ordinea testelor). Placeholdere, NU secrete (redirect_uri = URL public de callback ARHITECTURA_SPV.md, client_id
fictiv). NU skip - testul RULEAZA, acoperirea pe construcția URL-ului de autorizare pastrata; duplicarea din test
curatata (os/Fernet neutilizate scoase). DOVADA: suita completa 438 passed, 0 failed (era 1 rosu permanent) +
mutatie negativa (ANAF_REDIRECT_URI gresit -> assertion FAILS), deci verifica real, nu trece vacuu.

BLOCK NOTABIL: verificatorul acopera acum si backendul (BACKEND_UI_BRUT), nu doar .js - o clasa intreaga de drift
(sume/date brute in Python) care putea reintra tacit e inchisa mecanic; suita de teste ramane VERDE complet (438,
zero rosu permanent). Ramas (DE_FACUT): ramura PFA a auditului vazuta doar prin teste+E2E, nu in UI reala (primul
PFA real); fus orar "cu_ora" = ora server (global). [test_spv rosu permanent -> REZOLVAT, fir 5.]

## 22.07.2026 fir 6 — config lazy (DE_FACUT item 5): env citit la APEL, nu la import

Aceeasi clasa de fragilitate care a produs item 4 (env inghetat la primul import, ordine accidentala; merge
in productie pe systemd, capcana sub pytest). Verificare la sursa a TUTUROR 19 variabilelor inainte de orice
conversie (grep pe fiecare constanta + unde e folosita valoarea + depinde ceva de stabilitatea in-proces):
concluzie ca env inghetat de systemd -> citire-la-import == citire-la-apel bit-cu-bit, nimeni nu compara cu un
snapshot, niciun consumator extern nu importa bindingul. Decizia "15+1 sters vs 17, si de ce raman JWT" -> DECIZII 22.07.

FACUT: helper `cfg(cheie, default="", cast=str)` in common.py (o singura definitie, citire la apel + cast la
tipul real). CONVERTITE 15, in ordinea gate-uita cu suita dupa FIECARE fisier:
  1. observare.py (6): praguri float (ICONTA_PRAG_QUERY_SEC/POOL_PCT/THROTTLE_MIN) + emailuri + BREVO_KEY;
     `os` devenit mort -> scos; email implicit factorizat in _EMAIL_IMPLICIT (o sursa).
  2. efactura_send.py (2): FCTEL_BASE_TPL + FCTEL_VALIDARE_TPL -> accesori fctel_base()/fctel_validare_url()
     (simetrici, single-source per host); test_efactura actualizat (nu mai lovea atribute de modul).
  3. etransport_send.py (2): ETRANSPORT_BASE (host) + ETRANSPORT_VERSIUNE (cast int, atentie tip real).
  4. spv_conector.py (5 non-secret): CLIENT_ID/SECRET, REDIRECT_URI, AUTHORIZE_URL, TOKEN_URL; test_spv
     actualizat (assert pe _AUTHORIZE_URL_DEFAULT, nu pe atribut). STERS: REVOKE_URL (declarat, NEFOLOSIT
     nicaieri in tot repo -> cod mort, regula "reparatie reala").
RAMAS DESCHIS (3 var, read-la-import intentionat, DE_FACUT item 5): auth_api.SECRET + DURATA_TOKEN_SEC
(fisier neatins - contine SECRET, semnare pe toate sesiunile) + spv_conector.STATE_SECRET (state generat la
/authorize, verificat la /callback - cereri diferite, potential peste restart). Se fac separat, cu test dedicat
(JWT_SECRET setat dupa import + token semnat valideaza) si DA gate.

DOVADA: suita completa 438 passed 0 failed dupa FIECARE din cele 4 fisiere (baseline stabilit intai cu
db.env sursat: fara el, 1 rosu de mediu "pool neinitializat" - shell interactiv n-are env-ul DB pe care
systemd il injecteaza serviciului, exact patologia temei). verificator DS = 0 candidate. Test functional:
env setat DUPA import schimba comportamentul pe toate 4 modulele (prag, URL authorize, host efactura, versiune).

## 22.07.2026 fir 7 — F180: avertisment regim TVA vs ANAF + semafor rosu Control fiscal

Verificare la sursa INAINTE de cod (regula 7 + regula 3): (1) platitor_tva traieste in firma_profil (2 rute de
editare manuala: /firma-profil/regim-tva + /vector); (2) F188 SUPRASCRIE aceeasi coloana la onboarding -> azi NU
exista valoare ANAF de comparat; (3) niciun mecanism de comparare profil-vs-ANAF existent (control_incrucisat =
doar declaratie-vs-contabilitate); (4) /control-fiscal itereaza TOATE firmele -> live-per-firma acolo neviabil.
FISCAL la sursa (apel v9 raw pe CUI 14399840): scpTVA = boolean "platitor la data interogarii" (perioade_TVA =
trail, nu valoare); TVA la incasare (RTVAI) si SplitTVA = fatete SEPARATE -> comparatie apples-to-apples, zero
fals-pozitiv din granularitate. DECIZIE (Costin): snapshot separat + live la salvare, signal-not-block. DECIZII 22.07.

CONSTRUIT in felii, cu suita verde dupa fiecare:
  - SCHEMA: firma_profil + platitor_tva_anaf boolean + platitor_tva_anaf_data date (nullable=fara snapshot->gri).
    core/migrare_platitor_tva_anaf.py (tipar migrare_*: idempotent, loop schemata) + mirror tenant_template.sql.
    Rulat: 2/2 scheme OK.
  - firma_profil_api: stare_tva_anaf (verde/rosu/gri, PURA) + avertisment_tva_anaf (PURA) + citeste_tva +
    seteaza_snapshot_tva.
  - RUTE (regim-tva + vector): apel ANAF live pe CUI INAINTE de a tine conexiunea pe schema (helper _anaf_tva_check
    in main, nu ridica niciodata); reimprospateaza snapshot + intoarce avertisment la divergenta (salveaza oricum).
  - PREFILL F188 (ambele cai register): populeaza si snapshot-ul = valoarea ANAF la onboarding (local==snapshot->verde).
  - CONTROL FISCAL: control_fiscal_api.constatare_regim_tva (PURA, contract stare/temei/limita/remediu=investigatie)
    integrata in evalueaza_firma (escaladeaza stare la rosu); ruta portofoliu adauga motiv in `contabil` (randat deja).
  - TESTE: 9 pure (test_firma_profil_api nou + test_control_fiscal extins).

DOVADA: suita 447 verde + verificator DS 0 + FUNCTIONALITATI.csv F180 LIVE + test FUNCTIONAL REAL pe tenant_002
(live ANAF: local!=ANAF -> avertisment, == -> none; gri fara snapshot; cale ROSIE end-to-end cu divergenta fortata
in tranzactie ROLLBACK -> regim_tva_anaf.stare=rosu + stare firma=rosu + remediu=investigatie, tenant_002 NEATINS).
LIMITA (DE_FACUT): firma needitata la care ANAF s-a schimbat post-onboarding ramane verde pana la un cron periodic
(F184-style) de reimprospatare snapshot — enhancement viitor, nu blocant.

## 22.07.2026 fir 8 — reparare rand F183 in FUNCTIONALITATI.csv + garda automata (test)

BUG gasit (dupa F180): randul F183 avea 10 campuri in loc de 9. Cauza (verificat cu csv.reader): campul Acces UI
"Control fiscal > Detaliu firma > Audit de preluare (buton, repetabil)" era scris FARA ghilimele -> virgula din
"(buton, repetabil)" il spargea in doua -> toate campurile decalate cu 1. IMPACT REAL: raportari_ai.py (F152)
filtreaza pe r[7].startswith("LIVE") -> cu decalajul r[7] era "OMFP 1802/2014..." (nu "LIVE") -> F183 EXCLUS
TACIT din baza de cunostinte AI. AI-ul nu stia ca "Audit de preluare" e LIVE. FIX chirurgical: ghilimele pe Acces UI
(o linie). Verificat: 193 randuri = 9 campuri; scan santinela (ID=F\\d+, Stare pe col 7) curat; F183 reapare in baza
AI (177 LIVE); triaj AI LIVE prin F152 pe 2 intrebari reale -> raspunde (nu escaladeaza), il recunoaste LIVE, acces
corect.

GARDA AUTOMATA (DA Costin): core/test_registru_functionalitati.py in suita, NU in verificator (verificatorul iese
mereu 0 = raportor, nu gate; suita e verde-obligatoriu). Doua checkuri: (1) nr campuri == header pe fiecare rand
(checkul de aur, prinde clasa F183); (2) ID = F\\d+ (prinde decalaje care totalizeaza fortuit N campuri). Citeste
cu csv.reader utf-8-sig EXACT ca raportari_ai.py. Mesaj de esec explicit (ce rand, cate campuri vs asteptat, de ce
conteaza). Respins checkul 3 (vocabular de stari) - cupleaza la lista extensibila, rosu fals la stare noua. De ce
test si nu verificator -> DECIZII 22.07. DOVADA: 2 teste + mutatie negativa (reintrodus bug F183 pe copie -> prins);
suita 449 verde.

## 22.07.2026 fir 9 — F165: auditor conformitate schema tenant vs tenant_template.sql

Verificare la sursa INAINTE de cod: (1) tenant_provisioning aplica template-ul INTEGRAL la tenantii NOI (replace
TENANT_PLACEHOLDER pe tot fisierul -> consistenti prin constructie); driftul loveste doar EXISTENTII cand
template-ul se schimba fara un migrare_*. (2) exista 14 migrare_*.py idempotente - convenția REPARA driftul dar pe
DISCIPLINA, nimic nu-l PRINDE mecanic (cauza link_plata). (3) DIAGNOSTIC REAL rulat (ref din template in ROLLBACK
vs fiecare tenant): drift CURENT = ZERO. tenant_001/002 conforme; link_plata/sursa_externa deja backfill-uite (2/2
coloane). Inventarul DE_FACUT ("tenant_003/004") era GRESIT - doar 001/002 exista. Cele 6 "tip-diferit" din prima
rulare = fals-pozitive integral (numele schemei in nextval('schema.seq'); normalizat). Cele 2 "tabele extra" pe
tenant_002 (d301_operatiuni=lazy prin d301.py, d205_beneficiari=legacy fara CREATE in cod) = benigne, gardate
to_regclass. CONCLUZIE: valoarea F165 e PREVENTIVA (garda), nu cleanup.

DECIZIE (Costin): audit + poarta + SUGEREAZA SQL, fara auto-ALTER, fara ecran. DECIZII 22.07.
CONSTRUIT: core/audit_schema.py - motor (ref din template in ROLLBACK + introspectie information_schema, filosofia
DUK: lucrul real e judecatorul; normalizeaza zgomotul nextval) + compara (directia HARD template->tenant: tabela/
coloana lipsa, tip, nullable; directia INFORMATIV tenant->template: extra, NU pica -> zero whitelist) +
sugereaza_alter (corp migrare_* ADD COLUMN IF NOT EXISTS, avertisment pe NOT NULL fara default) + CLI _main
(python3 -m core.audit_schema, exit code, suggest, NU aplica). test_audit_schema.py: 9 pure + poarta reala (toti
tenantii conform) + mutatie negativa (coloana scoasa din ref real -> HARD).

DOVADA: suita 460 verde + verificator DS 0 + CLI arata 0/2 drift HARD (cele 2 tabele extra = info adnotat) +
E2E: DROP link_plata REAL pe tenant_002 in ROLLBACK -> drift HARD detectat + SQL sugerat corect
('ALTER TABLE "tenant_002".facturi ADD COLUMN IF NOT EXISTS link_plata text;') + tenant_002 NEATINS dupa rollback.
Suggest-don't-apply: repararea ramane un migrare_* numit + mirror template, revizuit de om (nu gaura in migrari).

## 22.07.2026 fir 10 — F163v2: persistarea declaratiei depuse (xml + randuri jsonb) in public.declaratii_depuse

Verificare la sursa INAINTE de cod (3 constatari care au contrazis premisa "res e deja in payload, doar il scriem"):
(1) la main.py:2715 payload-ul retinea {xml, avertismente} si ARUNCA restul lui res - docstring adauga_in_coada:63
MINTEA ("xml + rezultat"). (2) res NU e uniform: 8/9 declaratii intorc un @dataclass, dar d112 intoarce
(xml, LISTA-avertismente) - fara totaluri structurate. (3) PK public.declaratii_depuse=(tenant_id,an,luna,tip) +
ON CONFLICT DO NOTHING: D710 (rectificativa D100) e tip separat -> coexista; dar re-depunerea ACELUIASI tip pe
aceeasi perioada e ignorata tacit (first-write-wins, non-distructiv). Plus: coloana `sursa` fusese adaugata LAZY
(asigura_coloana_sursa) fiindca migrare_* nu acopera schema PUBLIC.

CONSTRUIT (5 decizii, DECIZII 22.07 F163v2):
  - migrare_declaratii_depuse_randuri.py: prima migrare "ca lumea" pe PUBLIC (un ALTER, fara bucla tenant) -
    ADD COLUMN IF NOT EXISTS xml text + randuri jsonb (nullable);
  - coada_api.randuri_din_res: asdict + default=str (Decimal->str, round-trip valoric); d112/lista -> None cu temei;
  - main.py 2712 (singurul call-site care face enqueue): payload pastreaza `randuri` (res intreg); docstring corectat;
  - coada_api.marcheaza_depusa: INSERT scrie si xml + randuri (ON CONFLICT DO NOTHING pastrat, append-only);
  - d112 -> randuri NULL, FARA refactor d112.genereaza (F181 - risc pe modul validat DUK).

RESPINS: refactor d112 (F181); ON CONFLICT DO UPDATE / versionare rectificative acelasi tip (asteapta DA - schimba
PK/semantica; DE_FACUT). Item nou DE_FACUT: F165 NU acopera schema public (nici template, nici audit, nici migrare_*
- de construit template+audit public sau conventie de migrari public).

DOVADA: 6 teste + E2E prin marcheaza_depusa REAL (payload->coada->depunere->declaratii_depuse, Decimal 4427.50
pastrat valoric, tenant_id sintetic 990163 in ROLLBACK + curatat complet). migrare public aplicata OK. Suita 466
verde + verificator DS 0. F165 neafectat (declaratii_depuse e public, nu in template-ul tenant).

## 22.07.2026 fir 11 — F163v2 varianta A: versionarea depunerilor + GRANT CREATE pe public + eliminare workaround lazy

Continuare F163v2: rectificativa de acelasi tip pe aceeasi perioada era ignorata tacit (ON CONFLICT DO NOTHING) ->
fals fiscal odata ce persistam VALORI (ar compara cu actul inlocuit). Varianta A (DA Costin): nr_depunere in PK +
vedere "curente".

BLOCAJ INFRA verificat la sursa: ADD PRIMARY KEY pe public creeaza index -> iconta_user (owner tabel, putea ADD
COLUMN) n-avea CREATE pe schema public (PG16 revoca implicit de la PUBLIC). Tranzactie rollback curata. DECIZIE
(DA Costin): GRANT CREATE ON SCHEMA public TO iconta_user, o data ca postgres -> migrarile public devin first-class
ca app-user (dovada: migrare_versiune a rulat CA iconta_user). De ce GRANT si nu one-off privilegiat: fara mecanism,
fiecare DDL public cere superuser -> de acolo a venit ALTER-ul lazy. Tratam cauza. Contraargument PG15 shadowing
considerat si respins (iconta_user detine deja tabelele public + creeaza scheme tenant; risc intra-rol, nu cross-rol;
reversibil prin REVOKE). Vezi DECIZII 22.07 [INFRA].

CONSTRUIT:
  - migrare_declaratii_depuse_versiune.py (public, idempotent): ADD nr_depunere NOT NULL DEFAULT 1 (backfill la 1)
    -> DROP PK vechi -> ADD PK (tenant,an,luna,tip,nr_depunere) -> CREATE OR REPLACE VIEW declaratii_depuse_curente
    (DISTINCT ON per perioada, nr_depunere DESC). Verificat: FARA FK spre declaratii_depuse (PK sigur de refacut).
  - coada_api.marcheaza_depusa: ON CONFLICT ELIMINAT; INSERT ... SELECT nr_depunere=COALESCE(MAX,0)+1 (PK = garda
    la cursa, conflictul nu se inghite tacut).
  - 6 cititori de logica -> vedere (control_fiscal_api, documente_api, portal_api, pachete_api, audit_preluare,
    main.py:2025). Verificat la sursa fiecare vrea "curenta"; count-migrare (istoric:142) RAMANE pe tabel (bookkeeping).
  - WORKAROUND LAZY ELIMINAT: asigura_coloana_sursa sters (functie + 2 apeluri); `sursa` mutata in
    migrare_declaratii_depuse_randuri (ADD COLUMN IF NOT EXISTS sursa NOT NULL DEFAULT 'iconta'). Fara cod mort.

DOVADA: testul care justifica tema - versionare prin marcheaza_depusa REAL: re-depunere acelasi tip -> 2 randuri
(nr 1/2) cu xml/randuri proprii, vederea "curente" da valorile NOI (<RECTIFICAT/>, colectata 200), initiala
(<INITIAL/>, 100) citibila in tabel. Verificat ux_coada_activa partial (exclude 'depusa') -> rectificativa in coada
dupa depunerea initiala. Suita 466 verde + verificator DS 0 + vederea interogabila de iconta_user. DE_FACUT:
"conventie migrari public" REZOLVAT; "F165 nu acopera public" ramane dar acum realizabil (blocaj privilegii ridicat).

## ═══ ÎNCHIDERE DE ZI 22.07.2026 (recap complet al firului) ═══

Arc de o zi, în ordine (fiecare cu fir/commit propriu mai sus + DECIZII):
1. **F183 audit preluare** — antet (firma în iConta din data, ora la audit), abateri DS în raport
   (sume RO + diacritice), ramificare pe REGIM (PFA rulează doar RIP). [commits 75eae8e..301a6bc]
2. **Fix login bounce** — refuz tăcut la credențiale greșite: 401 pe login nu mai declanșează logout. [9de75ea]
3. **BACKEND_UI_BRUT** — canonice backend (bani + data_ro) + gardă .py în verificator (sume/date brute în text
   destinat userului, construit în Python, scăpau garzilor .js). Verificator TOTAL 0. [73b0094..4e3c0a3]
4. **Config lazy** (DE_FACUT item 5) — env citit la APEL prin common.cfg (15 din 19 var, 4 fișiere; REVOKE_URL
   mort șters). Cele 3 JWT rămân la import (separat). [bde2e52]
5. **F180** — avertisment regim TVA vs ANAF (snapshot separat + live la salvare) + semafor roșu Control fiscal.
   Verificat fiscal la sursă (v9 scpTVA boolean). [b8f931e]
6. **Bug registru F183** — Acces UI neescapat (virgulă) spărgea rândul (10 câmpuri) -> F163... nu, F183 invizibil
   pentru AI (F152). Reparat + **gardă de integritate registru în suită** (nr câmpuri + ID=F\d+). [f96ea3e, be7def9]
7. **F165** — auditor conformitate schemă tenant vs template (detect + SUGEREAZĂ SQL, nu aplică) + poartă în suită.
   Drift curent = zero (preventiv). [6ccabef]
8. **F198 / F163v2** — persistarea declarației depuse (xml + randuri jsonb) în public.declaratii_depuse +
   **versionare varianta A** (nr_depunere în PK + vedere declaratii_depuse_curente; ON CONFLICT eliminat). [6604ff4, 9cc77c4]
9. **[INFRA] GRANT CREATE ON SCHEMA public + ownership 100% iconta_user** (14 ALTER OWNER) + curățare DDL runtime
   (ensure_tabela mort șters, DDL_JURNAL -> migrare, workaround lazy sursa eliminat). Public 28 tabele + 18 secv +
   1 vedere, toate iconta_user. [9e154d4, df3268b]
10. **infra/bootstrap_public.sql** — genesis reproductibil al schemei public (filtrat: exclude ce are CREATE în git;
    declaratii_depuse la genesis), idempotent, testat pe bază temporară locală. [908459e]
11. **F163 D-vs-D real** (D390 vs D300 depus) — a treia comparație în verifica_d390, deblocată de F198. [defa535]
12. **PRIMA depunere D300 reală prin app** — fluxul coada->aproba->depune nu fusese exercitat NICIODATĂ (coada goală,
    toate depunerile = migrare). Parcurs cap-coadă pe tenant_002 (test) -> primul d300 cu sursa=iconta + randuri;
    F163 verde corect pe date reale. Semantica 'depusă' = stare internă (nu transmite ANAF). [59de8f1]

13. **BUG tip-case** — canonizare `tip` la LOWERCASE (cheie de join) + CHECK pe declaratii_depuse/coada;
    upper DOAR la randare (3 motiv backend + 4 ecrane UI). Prins de prima depunere reală (app lowercase vs
    semafor uppercase -> depusă apărea nedepusă). Forma ANAF trăiește în CHEIE_DUK, nu în coloană. [bd8cff2]
14. **Ramura PFA audit (F183)** parcursă REAL (tenant_003 PFA prin flux HTTP + RIP prin rute) + **limită/NEVERIFICAT
    ramificate pe regim** (PFA nu mai vede termeni de partidă dublă) + RIP-gol -> gri cu temei. [01f491e]
15. **[SECURITATE] Vuln JWT default gol** — SECRET/STATE_SECRET aveau `os.environ.get("JWT_SECRET","")` folosit tăcut
    prin HMAC = bypass complet de auth dacă env lipsește. Reparat pe 3 straturi: gardă cripto (nucleu raise pe secret
    gol), cfg_secret (excepție dură), fail-fast la boot (verifica_secrete_obligatorii). [14df3e7]
16. **Fus orar** — gardă boot verifica_fus_orar (OS TZ + PG timezone = Europe/Bucharest, invariantă) + azi_ro() în
    verdictele de zi (semafor, e-Transport UIT, cron alerte, termene) + data_depunere AT TIME ZONE. Server ERA deja
    Bucharest (premisa veche "UTC pe Hetzner" infirmată); risc latent + dublu închis. [a9d6590, 4f87f60]
17. **db.env**: `idb()` în ~/.bashrc (psql ca iconta_user din db.env, fără parole în bashrc/git). [pt "role costin"].

ÎNCHIS azi: config lazy (partial - JWT tratate ca securitate) · F180 · registru F183 + gardă · F165 · F198/F163v2
persistare+versionare · GRANT+ownership public 100% · bootstrap_public.sql · F163 D-vs-D + prima depunere reală ·
bug tip-case · convenție migrări public · ramura PFA + limită ramificată · **vuln JWT (3 straturi)** · fus orar
(verdicte) · idb() psql · test_spv_conector.

RĂMÂNE DESCHIS (grupat): INFRA — runbook deploy server nou; F165-pe-public; pytest depinde de db.env (conftest/runner).
PRODUS — fricțiune onboarding competențe depunere; fus display browser-local (low-prio). SPV (blocat pe drept) —
dus-întors LIVE e-Factură/e-Transport; F127/F128 (deadline ANAF 17.08). FISCAL — F164v2 digest Brevo; F163 servicii
IC v3; D230/D307; obs4 neclasificat RIP doar prin import. VIZUAL (cere ochii, NU SSH) — CHECKLIST_BROWSER (PWA,
responsive, ~12 ecrane). RESPINSE — F149/F161/F184/D106/D101G.

LECȚIE CONSEMNATĂ — cele 3 bug-uri au ieșit la iveală PARCURGÂND CĂI REALE, nu citind cod: (1) **tip-case** — prima
depunere reală D300 prin app (fluxul niciodată exercitat) a arătat că semaforul n-o recunoaște (lowercase vs
uppercase); (2) **texte PFA** — primul audit real pe un PFA a arătat că limita comunică un PFA concepte de partidă
dublă (conținut fals la adresa lui); (3) **JWT default gol** — analiza înainte de a converti lazy a scos o
vulnerabilitate PRE-EXISTENTĂ (bypass de auth) care nu era pe radar. Tiparul: un flux/ramură/config care "merge pe
prod doar fiindcă mediul e norocos" (env setat, server Bucharest, toate depunerile uppercase din migrare) ascunde
fragilitatea până la primul parcurs real. Regula întărită: exercită calea reală (depune real, creează PFA real,
analizează secretul), nu presupune din cod că merge.

STARE FINALĂ: suită 490 verde, verificator DS 0, ownership public 100% iconta_user, garde de boot active
(JWT_SECRET + fus orar), verdictele de zi robuste la OS TZ, prima depunere reală în jurnal (append-only).

## 23.07.2026 — Ecran poziția 2 din lista C (CHECKLIST_BROWSER) — Control fiscal — închis pe SRL și PFA
Comituri: ac5ab4f → 3b7aaa9 → cb1f831 → f9198b5 → 34e4d86 → 8d8e9c7 (matrice de stări 32) → 732f976 (Pasul B:
D300/D394 mărginite la înregistrarea TVA din ANAF v9 + D390 neplătitor=gri + matrice 64) → f7ce7e8 (Pasul C:
prezentare — temei nedublat, antet complet, ordine decizională, restanțe veche-prima) + commitul C4 de acum.

**CORECȚIE la o declarație prematură:** commitul de închidere de zi 4e9aea6 a declarat „ecran 1/12 închis" la
34e4d86 — PREMATUR. Ecranul NU era închis: au urmat Pasul B (matricea de stări a scos că înregistrarea TVA la
mijloc de an nu era modelată → D300/D394 mărginite la data înregistrării, fapt ANAF v9; D390 la neplătitor devenit
gri cu temei) și Pasul C (prezentarea). Lecția e chiar constatarea de proces de mai jos: o poartă statică verde
NU înseamnă ecran închis; abia parcurgerea reală (matricea de stări + auditul de prezentare) l-a închis efectiv.

**LANȚUL CAUZAL (partea importantă — UN SINGUR defect, 7 manifestări, 4 straturi):**
`tip_firma` DEFAULT 'srl' tăcut + needitabil post-creare
→ firma cabinetului (AMZUICĂ BOGDAN-FLORIAN, cabinet individual / profesie liberală) creată ca SRL-micro
→ semafor Control fiscal cu restanțe INVENTATE D100/D101/D406 (persoană juridică, pe o persoană fizică)
→ aceeași boală în BACKEND: `regim_fiscal or "micro"` (termene_api) fabrica D100 pe un PFA
→ primitivele `regim_contabil()` / `regim_efectiv()` / `tip_firma_nrm()` în `migrare_api` — faptul într-un SINGUR
   loc, contract strict (KeyError pe cheie absentă, fără `.get`, fără fallback)
→ gardă `DEFAULT_FISCAL_TACIT` în verificator + DESIGN_SYSTEM cap.17 (interzice fallback pe literal fiscal)
→ aceeași boală în FRONTEND, pe care garda `.py` n-o vedea: **BLOCAJ REAL** — un PFA nu putea completa pasul
   Vector fiscal deloc (fallback "micro" pre-selectat, butoanele n-au deselect → `getRegim()` mereu ne-gol → 400
   necondiționat de la `salveaza`)
→ gardă extinsă pe `.js` (v2.17) + frontendul folosește FAPTUL expus de backend (`regim_contabil`), nu ghicește
→ al 4-lea câmp: `tip_decont || "trimestrial"` defaulta pe EXCEPȚIE, nu pe regulă → obligatoriu la migrare, cu
   criteriul art. 322 afișat prin `.camp-ajutor`; garda extinsă (v2.18); `termene_api` nu mai ghicește periodicitatea.

**VERIFICAT LA SURSĂ:**
- **OPANAF 407/2025**, MO 310/08.04.2025 — înlocuiește Anexa 5 la OPANAF 1783/2021. Cabinet individual / profesie
  liberală → excludere D406 la Anexa 5 **pct.4 lit.q)**. Temeiul din cod corectat (era "1783/2021 pct.4" generic).
- **Art. 322 Cod fiscal**: alin.(1) LUNA = regula; alin.(2) TRIMESTRUL = excepția, sub 100.000 € (curs BNR 31.12)
  ȘI fără achiziții intracomunitare de bunuri.

**DECIZII (în DECIZII.md):**
- **D406 la PFA în partidă DUBLĂ: RESPINS cu temei** (Anexa 5 pct.4 lit.a — enumerare necondiționată a persoanelor
  fizice; condiția de partidă dublă e DOAR la lit.n pentru asociații fără scop patrimonial; pct.3 lit.s vizează
  doar persoane juridice). Atributul de „mod de organizare a contabilității" **NU se construiește**. Răstoarnă
  limita deschisă consemnată anterior (care presupunea că un PFA în partidă dublă ar datora D406).

**CONSTATARE DE PROCES (cea mai importantă):**
Blocajul de onboarding pe TOT regimul PFA a existat de la lansarea sprintului PFA (F189, 20.07), cu **518 teste
verzi și verificator TOTAL 0 pe toată perioada**. Toate porțile sunt statice sau unitare; NICIUNA nu parcurge un
flux complet ca PFA. Regula „test funcțional după modificare de backend" a fost respectată — dar defectul era
frontend→backend (fallback UI needeselectabil + gardă doar pe `.py`), pe care nici testele unitare, nici garda,
nici verdictul-pe-cod nu-l vedeau. Lecția: o gardă statică + teste unitare verzi NU dovedesc că un REGIM întreg
poate parcurge un flux; doar un parcurs real cap-la-cap o dovedește.

**CHECKLIST_BROWSER — NUMEROTARE CANONICĂ (corecție la „1/12"):** N/12 urmează ordinea listei din secțiunea C,
NU ordinea de atac. Canonic: 1=Declarații, **2=Control fiscal (ÎNCHIS azi, SRL+PFA, comituri ac5ab4f→9693c1f)**,
3=Termene, 4=Setări cont, 5=Recomandă, 6=Admin*, 7=e-Transport, 8=Produse, 9=Tipare, 10=Semafor, 11=Pachete
lunare, 12=Capacitate. „1/12" din commitul de închidere a fost impropriu — Control fiscal e **poziția 2**, nu
prima. Ordinea DE ATAC o dă Costin, independent de poziție. Următorul atacat (alegerea lui Costin): **poziția 3
(Termene)**. Rămân 11 poziții (1 și 3–12).

## 23.07.2026 — Ecran poziția 3 (Termene): pregătire + T1–T4 (consolidare pe motorul semaforului)
Pregătire (raport, fără cod) → 4 teme, un commit fiecare. Ecranul avea **zero teste** înainte (modulul
`termene_api` reimplementa singur maparea „cine ce declarație datorează", exact tiparul care fabricase D100
pe PFA). Dovadă după fiecare: pytest complet + verificator TOTAL 0. Capturile vizuale le face Costin.

**SCHIMBARE VIZIBILĂ PENTRU UTILIZATOR (T2) — corecție de sub-raportare în Termene:** până acum ecranul
Termene NU afișa deloc **D394, D406 și D101** — le rata complet, fiindcă maparea locală emitea numai
D300/D112/D100/D390. După consolidarea pe motorul unic al semaforului, un plătitor de TVA vede acum și
scadențele D394/D406 (lunar/trimestrial, după decont), iar o firmă pe profit vede D101 anual — când termenul
cade în fereastra de 60 de zile și declarația nu e depusă. Nu e detaliu de refactor: sunt scadențe reale care
lipseau din ochiul contabilului. Termenele noilor declarații vin din `_termen` partajat (→ `scadente.py`),
verificate la sursă.

- **T1** (`fix(termene): firma neevaluabila NU dispare tacut`): ruta `/termene` avea `except: continue` la
  nivel de firmă → o firmă care crapă dispărea din scadențar (minciună prin omisiune). Acum: canal `neevaluate`
  (gri cu temei), afișat inclusiv când nu există scadențe. Aceeași doctrină ca semaforul (23.07).
- **T2** (`refactor(termene): motor unic de emitere`): `control_fiscal_api.obligatii_datorate(vector, are_sal,
  azi, *, jos, sus_zile)` = sursa UNICĂ a mapării; `declaratii_datorate` = wrapper (jos=None, 7z, semafor
  NESCHIMBAT — matricea de 64 trece intactă); `termene_firma` = wrapper (jos=azi, 60z). Duplicarea eliminată.
- **T3** (inclus în T2): D390 la neplătitor cu operațiuni IC intră în `neclar` (gri art. 317), NU în `datorate`
  → nu mai apare ca scadență fermă în Termene. Termene adoptă verdictul semaforului, nu-l fabrică.
- **T4** (inclus în T2): perioadele candidate extinse la an+1 (fereastra de 60z poate trece în anul următor);
  filtrul `[jos, sus]` pe termen = sursă unică. Testat explicit la `15.12` (perioada dec via termen în ian) și
  `28.12` (trage perioada ian-an+1, pe care bucla veche `an=azi.year` o rata).
- **§4 (marginirea la înregistrarea TVA) neatins**, cum s-a decis: ruta `/termene` NU aduce
  `platitor_tva_anaf_inceput` în vector → `tva_data_inceput=None` → Termene nu mărginește (rămâne pentru proba
  vizuală a lui Costin). Motorul știe să mărginească; termene doar nu-l hrănește cu data.

## 23.07.2026 — Ecran poz.3 (Termene): D390 pe fapt, regresie UndefinedTable, d301 canonizat, d205 legacy eliminat
Continuare poz.3. Comituri: ee09fcc/6cce866 (D390 pe fapt lunar + §4 marginire), 444dc53 (operatiuni_ic obligatoriu),
01b353b (fapt primeaza + semnal contradictie), 91b9051 (regresie UndefinedTable - poarta D390=platitor + d301 scos
din primitiva) + commitul de canonizare d301/d205 de acum.

**CORECTIE la o afirmatie FALSA din raportul anterior (91b9051):** am scris "generarea D301 e rupta pentru
majoritatea tenantilor (toti in afara de tenant_002)". NEADEVARAT. `d301.py:ensure_tabel` facea CREATE TABLE IF
NOT EXISTS lazy (gardat) -> D301 se auto-vindeca la prima folosire; dovedit functional pe tenant_001 (pull creeaza
tabela, 0 crash). Cauza reala a crash-ului din /termene: `d390_are_operatiuni` interoga `d301_operatiuni` FARA garda
pe care `d301.py` si `control_incrucisat.py` o au. Deja reparat (91b9051: d301 scos din primitiva + poarta D390=platitor).

**Canonizare (decizie Costin):** d301_operatiuni mutat din CREATE lazy in tenant_template.sql (ensure_tabel ELIMINAT
= o singura sursa, aliniat cu 22.07 anti-lazy) + backfill idempotent tenant_003. d205_beneficiari = cod mort eliminat
(zero writeri; unicul consumator era verificarea d205_vs_457 care citea o tabela mereu goala -> rosu fals pe firme cu
dividende) - sters din main.py/verificatoare.py/firme.js/whitelist F165; tabela ramane pe tenant_002 neatinsa, fara
consumatori. D205-vs-457 real traieste in semafor (declaratii_fapt pe rulaj 457). Vezi DECIZII 23.07.

**CONSTATARE DE PROCES (item 5, formularea corecta):** 945 teste verzi cu crash-ul din /termene neprins NU inseamna
ca provisioning-ul era netestat in consecinte (lazy-create se auto-vindeca, D301 nu era rupt). Inseamna ca exista o
CALE DE COD NEGARDATA (d390_are_operatiuni pe un neplatitor de partida simpla) pe care NICIO poarta n-a parcurs-o:
matricea de 64 rula cu d390_fapt=None (nu atingea DB), niciun test de RUTA nu evalua portofoliul pe un tenant real.
Testul care ar fi prins-o = unul de ruta pe portofoliu (/termene sau /control-fiscal pe tenanti reali), NU de
provisioning. Aserția adaugata (test_matrice.test_d390_fapt_consultat_doar_la_platitor) prinde clasa la nivel de
logica. A DOUA oara azi cand portile verzi acopera o cale reala neparcursa - prima a fost blocajul de onboarding PFA
(vezi 23.07 ecran poz.2, "o poarta statica + teste unitare verzi NU dovedesc ca un REGIM intreg poate parcurge un flux").

**Verificat la sursa:** d301_operatiuni NU are writer nicaieri (nici INSERT/ruta/UI) - D301 genereaza XML dintr-o
tabela populata doar manual/extern (feature-completeness gap raportat, nu blocant). F165 (item 4) marca DEJA
tabele_lipsa (template->tenant) ca HARD - nimic de construit acolo.

**CONSTATARE PROPRIE — d205_vs_457 producea ROSU FALS (a TREIA oara azi, poarta verde peste un fals vizibil
utilizatorului):** verificarea "D205 vs cont 457" din _verificari_contabile citea suma D205 din tabela
d205_beneficiari care e goala peste TOT (zero writeri) -> SUM=0. Deci pe ORICE firma cu dividende repartizate
(rulaj 1171->457 > 0) checkul dadea buline ROSIE "D205: 0 lei vs 457: X lei" - o acuzatie falsa de dividende
nedeclarate, chiar daca D205 era depusa (prin d205.py, cont 457). NU e curatenie de cod mort - e aceeasi clasa cu
restantele INVENTATE de dimineata (D100 pe PFA, poz.2): o poarta verde (945 teste) acoperea un verdict fals VIZIBIL
in panoul de verificari al firmei. Cele trei de azi: (1) blocajul onboarding PFA - cale reala neparcursa; (2) crash
/termene - cale de cod negardata; (3) d205_vs_457 - verdict fals randat. Tiparul comun: verdele mecanic nu dovedeste
corectitudinea unei cai pe care nicio poarta n-o exercita pe date reale. Reparat: verificarea eliminata integral (D205
-vs-457 pe FAPT traieste in semafor, declaratii_fapt pe rulaj 457).

**CONSTATARE DE PROCES — al 5-lea caz azi (toate portile trec, interactiunea reala cade):** P2 (navigare din
Termene la fisa firmei) a trecut de pytest 945 + verificator 0 + node --check + curl pe ruta, dar CLICK-ul real pe
rand crapa fisa: deschideFirma trimitea {id, nume, cui} iar meniuFirma:241 cere `t.tip_firma.toLowerCase()` (contract
strict, fara fallback) -> undefined.toLowerCase() -> "eroare neasteptata". Cauza: tenantii_userului NU intoarce
tip_firma (doar id/nume/schema/cui/activ); obiectul partial rupea contractul fisei. Reparat la sursa: tip_firma
adaugat in payload-ul /termene (il aveam deja din firma_profil, vector[tip_firma]) -> {id, nume, cui, tip_firma}
complet. TIPARUL COMUN al celor 5 de azi: nicio poarta nu APASA un buton / nu parcurge o interactiune reala pe date
reale. Cele 5: (1) onboarding PFA - regim intreg neparcurs; (2) crash /termene - cale de cod negardata; (3)
d205_vs_457 - verdict fals randat; (4) 5 formatoare locale de data - gaura de gard; (5) P2 - obiect partial care
crapa la randare. Verdele mecanic (sintaxa, tipul, ruta care curge) NU dovedeste ca o INTERACTIUNE reala merge.
Ce ar fi prins-o: un test de interactiune (jsdom/headless care apasa rand-firma) SAU un contract explicit al
obiectului-firma (deschideFirma sa valideze {id,nume,cui,tip_firma} si sa arunce clar). Ambele = workstream separat.

## 23.07.2026 — Ecran poziția 3 din lista C (CHECKLIST_BROWSER) — TERMENE — ÎNCHIS
Comituri: 80c260b → a5f889a → 792f8d8 → 5f5c1b5 → 238b427 → cb8618a → ee09fcc → 6cce866 → 01b353b →
444dc53 → 91b9051 → 84db870 → 6a8d1c3 → d735c33 + d236cf6 → b3fb563 (fix P2, tip_firma în payload).

**CE S-A REPARAT, în ordine de gravitate:**
1. **Sub-raportare: D394/D406/D101 nu apăreau DELOC în Termene.** Cauză: `termene_firma` reimplementa inline
   maparea „cine ce datorează". Consolidat într-o primitivă unică (`obligatii_datorate`) cu fereastră
   parametrizabilă (7z semafor / 60z termene). Efect: matricea de 64 acoperă acum și Termene, care avea zero acoperire.
2. **D390 tratat ca obligație lunară fixă pe flag static.** Corectat: fapt lunar din facturi IC + `d390_manual`.
   Temei: instrucțiuni completare D390, anexa OPANAF 394/2017 pct.1.2. Poarta inversată: faptul primează, flag-ul
   decide doar pe perioadă deschisă. Costuri asimetrice: înapoi decidem pe fapt (restanță falsă = acuzație
   nefondată), înainte afișăm pe incertitudine (termen ascuns = amendă).
3. **d205_vs_457 producea ROȘU FALS pe orice firmă cu dividende** (tabelă goală peste tot, SUM=0 vs cont 457).
   Cod mort eliminat complet: citire (main.py) + funcție (verificatoare.py) + randare (firme.js) + whitelist F165.
4. **Firma neevaluabilă dispărea tăcut** (`try/except: continue`). Canal `neevaluate`, gri cu temei — a prins
   regresia de la pct.5 în aceeași zi.
5. **Regresie proprie:** `d390_are_operatiuni` interoga `d301_operatiuni` fără garda pe care `d301.py` și
   `control_incrucisat.py` o au → cabinetul dispărea din toate termenele. Poarta corectă = `platitor_tva`.
6. **§4:** ruta `/termene` nu aducea `platitor_tva_anaf_inceput` → fără mărginire la data înregistrării TVA.
   Asimetrie cu semaforul, închisă.
7. **Edge decembrie:** `an = azi.year` fix → perioadele an+1 nu se generau. Teste la 15.12 și 28.12.
8. **dataLunga = formator local**, încălcare DATA_DIALECT (DS cap.4). Garda avea gaură; extinsă, a prins 5
   formatoare locale pe tot frontendul (2 reale — cabinet, portal — reparate înainte să ajungem la acele ecrane).

**CONSTATARE DE PROCES — de cinci ori azi toate porțile au trecut și interacțiunea reală a căzut:** (1) onboarding
PFA, (2) crash /termene, (3) d205_vs_457, (4) 5 formatoare locale, (5) P2 obiect parțial. Tiparul: verde mecanic
(sintaxă, tip, rută care curge) nu dovedește că o interacțiune reală merge. Niciun test nu apasă un buton.

**NOTĂ pe cazul 5:** `meniuFirma` cere `tip_firma` cu contract strict fiindcă am eliminat azi `|| "srl"` de acolo.
Fallback-ul mort masca lipsa câmpului. Nu e argument să-l punem înapoi — e ilustrarea că un default tacit nu previne
bug-uri, ci le transformă în date greșite tăcute. Aici a apărut imediat, ca eroare, și s-a reparat prin completarea
contractului (`{id, nume, cui, tip_firma}`).

**DECIZII:** eticheta de perioadă poartă anul doar când diferă de anul curent (decizie de conținut, nu format DS).
Netestat vizual — se va vedea abia în decembrie, când fereastra traversează anul.

**DE_FACUT:** gap D301 (tabelă fără writer — contabilul nu poate introduce operațiuni IC din aplicație). Test de
interacțiune (headless care apasă) sau contract explicit al obiectului-firmă — consemnat ca workstream separat, NEDECIS.

**CHECKLIST_BROWSER: pozițiile 2 și 3 închise. Rămân 10** (1, 4–12).

## 23.07.2026 — Ecran poziția 1 (Declarații) — ÎNCHIS + gardă IMPORT_VERSIUNE + antet explicit
Comituri: 497c83c → d17fab0 → b3f011d → 29aff0c → a552a78 (Declarații / carduri pe firmă) +
d6485f4 (versiune de modul consecventă + gardă IMPORT_VERSIUNE) + ac288ea (antet explicit `meniuFirma`).

**POZIȚIA 1 (Declarații) — verificată vizual, ÎNCHISĂ:** dropdown cu D100/D101/D406 dezactivate + temei
pe PFA; cardul Declarații vizibil la PFA; filtrarea cardurilor pe `regim_contabil` confirmată pe 3 firme
(2 PFA + 1 SRL).

**CE S-A REPARAT la poziția 1:**
1. **G1: `neaplicabile_forma`** — o singură mapare „ce nu se aplică formei fiscale", trei consumatori, poartă
   backend 422. A eliminat a treia sursă paralelă la aceeași întrebare.
2. **`DOAR_SRL` pe cardul Declarații = fals negativ** — PFA nu putea genera D112/D300/D394/D301/D390 din fișă.
   Oglinda bug-ului de dimineață (declarații scoase din `DOAR_SRL`, 29aff0c).
3. **A patra sursă paralelă la „ce se aplică regimului X" eliminată** (a552a78): listele `DOAR_SRL`/`DOAR_PFA`
   șterse; fiecare card declară `regim` OBLIGATORIU, vizibilitatea derivă prin `regim_contabil` (o singură sursă).
   Gardă CARD_REGIM. DS cap.18.
4. G2 eroare surfacată; G3 etichete → `dataRo` + gardă DATA_DIALECT extinsă; G4 panoul de clasificare D390 în clase.

**BUG DE CACHE/INSTANȚĂ (surfacat la verificarea vizuală a poziției 1):** antetul montat de `firme.js` apărea pe
calea FIRME dar lipsea pe calea TERMENE. Cauză: `termene.js` importa `./firme.js` FĂRĂ versiune, restul `?v=7` →
browserul instanția DOUĂ copii ale modulului ES (`/firme.js` ≠ `/firme.js?v=7`); a doua (calea Termene) nu vedea
starea primei. **NU era regresie din a552a78** — instanță veche a modulului. Reparat (d6485f4): versiuni aliniate +
**gardă IMPORT_VERSIUNE** (grupare pe calea REZOLVATĂ relativ la fișierul care importă, nu pe basename; >1 token
distinct de versiune = eroare; acoperă și `import()` dinamic). Garda a prins o **A DOUA divergență** pe care
sweep-ul manual grep o ratase (nu prindea `import()` dinamic): `navigator.js` deschidea `./ecrane/control.js`
dinamic FĂRĂ versiune vs `?v=1` din cabinet/asistent. DS cap.19 nou (v2.23). A șaptea gaură de gardă găsită azi.

**ÎNTĂRIRE (ac288ea, commit SEPARAT, NU fix):** `meniuFirma` randează antetul EXPLICIT (`<h2 class="pf-titlu">`
cu `nume · CUI`, text identic cu titlul ferestrei, prin `esc()`) în loc să depindă de auto-h2 din navigator
(`_steaza`: prepend prin MutationObserver + euristica „fără h2" + timing). Rezultat vizual identic, determinist.
Condiția `!querySelector("h2")` din `_steaza` devine falsă → nu se dublează. DS cap.9.

**NEREPARAT, consemnat:**
- **Casă = „ambele" la card**, dar contarea 5311 din interior e partidă dublă. Temei vizibilitate: Legea 70/2015
  art.1 alin.(1), plafoane numerar fără excepție pentru PFA/II/IF. Se filtrează fin în interior, NU se ascunde cardul.
- **Datorie de style inline (v2.11, acceptată):** extinderea gărzii display/flex/gap = workstream separat, netouchat.
- **D710 LIVE dar inaccesibil din UI.** **D301 fără writer** (contabilul nu poate introduce operațiuni IC din app).

**DE_FACUT:** inventar declarații LIVE vs. accesibile din UI (D710 LIVE fără intrare UI, D301 fără writer).

**CHECKLIST_BROWSER: pozițiile 1, 2, 3 închise. Rămân 9** (4–12).

## 24.07.2026 — Ecran poziția 2 (Control fiscal): consolidare renderer verdict + gardă VERDICT_PARITATE
Comituri: 4e43254 (renderer unic + gardă cu 2 parități) + ac7e135 (paritate de randare extinsă la ecranVerificari).

**BUG DE CLASĂ, nu caz izolat.** Patru suprafețe consumă payload-ul de control fiscal: lista de portofoliu (feed
`contabil`, exhaustiv — NU în clasă), detaliul (`control.js`), cardul din fișă (`firme.js/ecranControlFirma`) și
`ecranVerificari`. Ultimele TREI alegeau chei din `verificari_contabile` pe NUME; fiecare omitea tăcut alt subset.
Simptom prins vizual pe DANTE: cele 4 roșii pe salarii (D112 vs contabilitate) + 5121 sold creditor nu apăreau pe
cardul din fișă, deși același endpoint (`/control-fiscal/{id}`) le trimitea. Omisiunea s-a repetat **INDEPENDENT de
trei ori** → semn de CLASĂ, nu caz. Regula „verde nu poate acoperi blocant" (23.07) nu o acoperea: e omisiune de
câmp în frontend, nu colaps de literal în backend.

**CONSOLIDARE.** `control_verdict.js` nou — renderer UNIC al corpului verdictului (`randeazaCorpVerdict`) + paletă
de semafor unică (a înlocuit `CULORI` din control.js + `_CF_CUL` din firme.js, două copii). Detaliul și cardul din
fișă delegă amândouă (doar anteta proprie rămâne locală). **−267/+94** linii. `ecranVerificari` NU se consolidează
(scop propriu, endpoint separat — vezi DECIZII 24.07), dar intră sub gardă prin inventar declarat.

**GARDĂ VERDICT_PARITATE — partea care repară CLASA.** Două parități mecanice, pe cheile PRODUSE parsate din
`_verificari_contabile` (nu hardcodate — o cheie nouă e prinsă automat):
- **RANDARE:** fiecare cheie vc ∈ inventarul declarat al fiecărui consumator care alege pe nume — `VC_RANDATE`
  (control_verdict.js) ȘI `VC_VERIFICARI` (firme.js/ecranVerificari: randat / IGNORAT-cu-motiv).
- **SEVERITATE:** fiecare cheie vc fie pliată în `contabil` (→ `pastila_firma`), fie în `VC_FARA_SEVERITATE`
  (main.py) cu motiv. Prinde scurgerea inversă (roșu în corp, header verde) — ce garda 23.07 n-o vedea.

**DS cap.20 nou (v2.24 + v2.25):** secțiunile pot diferi LEGITIM între ecrane (altă altitudine), cheile dintr-o
secțiune randată NU. Sortare C4 (restanțe pe termen) în renderer.

**DOVEZI:** verificator TOTAL 0, VERDICT_PARITATE 0, IMPORT_VERSIUNE 0. Garda se declanșează pe AMBII consumatori
(cheie vc nedeclarată → erori randare + severitate; `d112_incrucisat` scos din VC_VERIFICARI → eroare
`firme.js/ecranVerificari`; revin la 0 la restaurare). Test funcțional node (payload cu constatările DANTE):
`mod:"fisa"` randează acum salarii roșu 266 / CAS 1250 + 5121 sold creditor + secțiunile Declarație vs
contabilitate / Verificări contabile. node --check × 3, py_compile main.py + verificator. Nimic vizual nu s-a
schimbat pe „Verificări" (doar declarație + gardă).

**DE_FACUT (colateral, neatins):** antetul `ecranVerificari` formatează perioada cu `padStart(luna)/${an}` — ocolește
DATA_DIALECT (cap.4), garda nu-l prinde (nu e forma `luni[]`/`toLocaleDateString`). CARENTE 5, cu două opțiuni scrise.

**CHECKLIST_BROWSER: poziția 2 (Control fiscal) — consolidare 24.07 peste închiderea 23.07. Rămân 9** (4–12).
