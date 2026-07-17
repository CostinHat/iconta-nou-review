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

