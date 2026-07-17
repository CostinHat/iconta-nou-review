# iConta — DE FĂCUT

**Doar viitorul: ce e deschis. Când termini, ștergi rândul. Trecutul e în ISTORIC.md + git log.**
Ultima actualizare: 13.07.2026 seara (partea 5)

---

## 1. Testare pentru pilot (din planul P1-P5, orientat business)

### Prin SSH — deja acoperit tehnic (NU relua): zonele 8,9,11,12,13,14,15

### Cere Daniela [D] — validare fiscală, sesiuni 2h
- P1.2 Flux lunar complet pe KAI: e-Factura + extras → reconciliere → jurnal → balanță → D300 → validare ANAF
- P1.3 Salarizare: salariat nou → stat plată → **fluturaș → D112 validat** (acum și cu Concediu Medical nou!)
- P2.6 TVA la încasare: factură + încasare parțială → 4428→4427 proporțional
- P2.7 Operațiuni speciale (5 eșantion): leasing, avansuri, sponsorizare, dividende, provizioane
- P2.8 Partidă simplă: import bancă → Fișă D212 (vs calcul manual)

### Cere Costin singur [C]
- P1.1 Creează cont nou end-to-end: înregistrare → firmă → factură → contare → validare → balanță
- P1.4 Recurente: șablon → cron → factură emisă
- P1.5 WooCommerce: comandă demo → sincronizare → factură + contare
- P2.9 KPI+forecast portal vs balanță; P2.10 Consolidare = suma firmelor; P2.11 AI learning
- P5.24 Backup/restore: pg_dump → restore pe DB temp → login OK

### Cere telefon [T] — după HTTPS (nou.iconta.eu e sus)
- P4.18 PWA: (FACUT iOS 14.07 - standalone+offline OK) ramas doar Android, verificare secundara
- P4.19 Pozează bon: cameră, multi-imagine, flux până la notă
- P4.20/21 Responsive portal <400px, landing <900px/<560px

## 2. Blocate — DUK / desktop ANAF
- **D394** pe DUKIntegrator (validare desktop)

## 3. Sesiune desktop (Word, nu SSH)
- (PARTIAL) Audit design 12.07: INCHISE (canonic + verificator TOTAL 0 pe toate 30 ecrane): formatare bani/data/procent, culori-card, iconite, tipografie, culori/borduri/raza. Design System v2.9 + verificator 9 reguli, la zi.
- RAMAS DIN AUDIT DESIGN (nefacut):
  1. Verificare VIZUALA doar ~10/30 ecrane. De vazut cu ochii restul ~20 (declaratii, control, termene, setari, recomanda, admin*, etransport, produse, tipare, semafor, validat, pachete, capacitate) - verificatorul e curat pe ele dar nu prinde tot.
  2. Categorii NEATACATE: spacing/padding/gap inline (fara inventar inca); wrapper alb pe formulare (cap.2 - verificatorul n-are regula, prins doar 1 manual); aliniere tabele (cap.4 sume la dreapta, neverificata sistematic); anatomia ferestrei (cap.1 entitate-antet/titlu-h2-corp, neauditata vizual).
  3. TASK 0a mai vechi (cerut 10.07, inca nefacut): audit cod mort + functionalitati ascunse ad-hoc fara conditie documentata + diferente cabinet/client inconsecvente.

## CARENTE — inventar consolidat 13.07.2026 (functionalitati partiale/promise)
1. (REZOLVAT 13.07 partea 5) F103+F060 alerte programate: testate integral, fix propuneri (markere buletin excluse). LIVE.
2. (REZOLVAT 13.07 seara) Cod 10 CM integrat: dropdown + venit realizat + art.19 + FNUASS integral, testat.
3. **D394 pe DUKIntegrator**: generatorul exista, validarea desktop blocata (sectiunea 2).
4. (REZOLVAT 14.07) PWA testat pe iPhone: instalare, standalone, offline. Android secundar.
5. (REZOLVAT 13.07 partea 5) F076 retetar GV: testat cu date reale, bug gv_crono (antedatare) reparat. LIVE.
6. **e-Transport**: XML pentru upload MANUAL in SPV; trimiterea directa prin API SPV nu exista.
7. (REZOLVAT 14.07) Descrieri FUNCTIONALITATI.csv complete: loturile 2-7 + F113, toate verificate la sursa; scurte raman doar pozitiile PLANIFICATE (legitim - scop propus, nu cod).
8. (REZOLVAT 13.07 seara) Admin auditat complet: 5/5 sub-ecrane, semafor Sanatate pe tokeni.
9. **Testare pilot**: sectiunea 1 (P1-P5) intacta — niciun punct bifat.
10. **Audit design ramas**: spacing inline (inchis explicit ca datorie acceptata), paleta iconite migrare (decizie amanata azi), anatomie/aliniere tabele nesistematizate.

## 4. Infra
- **Reboot kernel** — "System restart required". Fereastră liniștită (downtime clienți, Daniela pilot).
- (REZOLVAT 13.07) systemd pentru 8010: iconta-nou.service creat, enabled la boot, EnvironmentFile db.env+api_keys.env, Restart=always. Testat functional (login 401 corect din DB). Restart: sudo systemctl restart iconta-nou. Unit in repo: config_referinta_iconta-nou.service.

## 5. Iterații viitoare (nu urgente)
- Cod 10 CM (reducere timp muncă) — exclus din dropdown; `calcul_cm_cod10` neintegrat în flux.
- raporteaza.js — verifică vizual data "cu_ora" în feed (migrat azi).
- Verifică date CM de test invalide în alte tenant-uri (CCMAD corupt deja șters din tenant_002).

## 6. (REZOLVAT 13.07) Ecrane firma neconstruite
- Control fiscal per firma: LIVE (partea 3). Declaratii per firma: LIVE (partea 4, decl_firma_v1). Vector fiscal: exista in firma_profil + ecran in Migrare. Card Produse: reconectat (partea 4). Sectiunea inchisa.

---

## ANEXA — Inventar functionalitati (referinta pentru testare)
(mutat din ICONTA_TESTARE.md ca sa avem DOUA documente, nu trei)

## A. INVENTAR FUNCTIONALITATI

### 1. Cont & acces
- Landing + inregistrare cabinet (CUI verificat ANAF, provisioning tenant automat)
- Login (cabinet/client/superadmin), magic-link client
- Suspendare cabinet (blocare instant per-request)
- Chei API publice per cabinet (Setari cont)

### 2. Portal client
- Acasa: semafor ANAF colapsabil
- Facturi (istoric, emitere, detalii, storno, model)
- Declaratii depuse, Documente (balanta PDF + declaratii)
- Solicitari (chat bidirectional + email), Povestea lunii, Recomanda
- Pozeaza bon (multi-imagine, camera pe mobil)
- Cifrele firmei: KPI YTD + Previziune bani 8 saptamani
- PWA: manifest + service worker (test pe HTTPS)

### 3. Facturare
- Emitere inteligenta (CUI ANAF, cote AI pe linii, numerotare auto)
- Proforme + avize (contoare separate, transformare in factura)
- Facturi recurente (sabloane, cron 07:00, UI lista/adaugare/toggle)
- Storno, contare automata (ciorna), TVA la incasare
- Regim marja art. 312 / turism art. 311
- WooCommerce: import comenzi -> facturi (config per firma, cron 07:30, idempotent)

### 4. Contabilitate
- Registru jurnal: ciorna/validata, editor linii, validare
- Reconciliere bancara: import extras (XLS/CSV), matching exact/combo/FIFO,
  ignora/readu, contare, AI sugestie invatata + semafor incredere
- AI learning: ai_corectii per tenant (validari + corectii contabil)
- Casa, Stocuri GV+CV, Retetar HoReCa, Raport Z, Amortizare MF
- Period locking (perioade blocate, 423 la scriere)
- Balanta de verificare (cabinet + portal), fallback denumiri OMFP
- Operatiuni speciale (28): curs valutar, leasing, credite, avansuri,
  necorporale, reevaluare, provizioane, productie, obiecte inventar,
  decontari asociati, sponsorizari, subventii, comodat/chirii, deconturi,
  bacsis, SGR, perisabilitati, zilieri, inventariere, lichidare, ONG etc.
- Partida simpla PFA/II/IF: rip_operatiuni, import banca/casa, Fisa D212,
  Registru-inventar

### 5. Salarizare
- Salariati CRUD, stat de plata, fluturasi PDF
- Concedii medicale (Ordinul 506/1030/2026)
- D112 cu CM (validat DUKIntegrator)

### 6. Declaratii & raportari
- D100, D101, D112, D205, D300, D301, D390, D394, D406 (dispatch core)
- Bilant anual S1005/S1003 (XML validat)
- e-Transport v1 (XML pentru upload manual)
- Verificatoare: echilibru, trezorerie, TVA, coerenta stocuri
- Control fiscal (semafor cross-portofoliu), Termene

### 7. Cabinet
- Firme (fisa cu ~18 module), De validat, Asistenti (competente, 4 ochi)
- Sinteza zilei, Activitate, Capacitate, Pachete lunare
- Consolidare portofoliu (KPI toate firmele + total)
- Setari cont (profil, parola, cabinet, competente, chei API)

### 8. API public (/api/v1, X-Api-Key)
- GET firme / facturi / kpi / balanta

### 9. Admin iConta (superadmin)
- Raportari, Activitate cabinete (+suspendare), Sanatate server
  (metrici 5 min, grafice SVG, alerte email Brevo)

### 10. Migrare (7 straturi, testate)
Firme, solduri initiale, solduri parteneri, salariati, asociati, MF, istoric declaratii

## Actualizare 14.07.2026 (sfarsitul zilei)
- INCHISE azi: F113, F152, F153 (gratuit v1+v2), descrieri CSV 103/103, dosarul rutelor 0a, audit vizual complet (~22 ecrane), regresia tenant_template
- F162: platitor_tva editat manual vs ANAF -> avertisment la salvare vector fiscal + semafor rosu Control fiscal la divergenta [PLANIFICAT]
- F164: cont_venit_implicit setabil din UI (Setari cont/profil firma), acum doar din DB [PLANIFICAT]
- F165: auditor conformitate schema tenant vs template + auto-ALTER (drift recurent pe tenant_003/004: link_plata, sursa_externa lipseau); rulat la provisionare + verificabil on-demand [PLANIFICAT]
- F168: la lansare publica, email automat catre conturile create in perioada beta (site in lucru); sterge BETA_COD_ACCES din env pt acces public [PLANIFICAT]
- F163: extindere control incrucisat la D112 / D101 / D100 / D390 / D394; acelasi tipar ca TVA. CONSTATARE 15.07 (analiza la sursa): D300 intoarce (xml, res) cu res['R'] = randurile -> comparabil direct. D112 intoarce doar (xml, avertismente) si isi tine agregatele in variabile de structura XML (c2_d14/d15/d16...), NU expune totaluri contabile. Doua cai: (a) parsare XML = fragil, se rupe tacut la schimbare de structura ANAF; (b) d112.genereaza sa intoarca si totalurile (CAS/CASS/impozit/CAM) = refactor pe modul validat DUKIntegrator. Recalcularea paralela din salarizare.calcul_salariu NU e echivalenta (ar compara contabilitatea cu propriul calcul, nu cu ce se declara efectiv - un bug in D112 ar trece neobservat). Conturi tinta (verificate in salarizare.py): CAS=4315, CASS=4316, impozit=444, CAM=436, brut=421. Decizie de arhitectura, nu extindere mecanica [PLANIFICAT]
- F166: parser MT940 (SWIFT) - LIVE 14.07 in banca_parser (marker :61:/:20:). RAMAS: validare pe fisier MT940 real din banca (campul :86: variaza per banca)
- F167: Open Banking automat prin Enable Banking (AIS EU; tier gratuit Restricted Production pt conturi proprii = dogfooding; productie = contract + KYB + cost pe conexiuni). Dupa MT940. Automatizeaza ADUCEREA extrasului, nu doar citirea [PLANIFICAT-etapa-2]
- F169: audit de PRELUARE firma - acelasi motor control_incrucisat aplicat la migrare: inventar transparent (ce pot/nu pot verifica), raport datat cu trei categorii (coerent / divergent / NEVERIFICAT-lipsa document), repetabil pe masura ce apar documentele. Acoperire profesionala la preluarea raspunderii [PLANIFICAT]
- RAMASE: teste [C] DONE 14.07 (P1.1/P1.4/P1.5-simulat/P2.9-2.11/P5.24); backup automat LIVE (systemd timer zilnic 03:00, retentie 7z); [D] raman ca teste proprii; blocate extern: F034 D394 DUK, F044 e-Transport API SPV; F154-F161 roadmap gratuit PLANIFICATE; parse-extras de clarificat vs rip/import-banca

## Actualizare 16.07.2026 — re-testare completa a aplicatiei (portiunea SSH)

Toate testele pe date INVENTATE verificate la sursa oficiala (lege/structuri ANAF/DUK),
zero opinii de contabil. Suita: 555 teste verzi. 8 commit-uri.

INCHISE azi:
- **Declaratii 9/9 + bilanturi S1005/S1003 VALID** pe validatorul oficial DUK, izolat SI pe
  date reale (d68dbfc, 6813537, 2d0a943). Vezi git log pentru fiecare.
- **Audit migrare firme noi** cap-coada: 3 arhetipuri (micro/profit/neplatitor), toate
  declaratiile datorate valide. Bug D100 micro reparat (09183e6: cod_oblig era pozitia 5,
  nu codul 121 + cota lipsa).
- **Re-testare zone marcate PASS** (ghidata de churn git, nu incredere oarba): gasite si
  reparate 2 bug-uri exact in cod nou/schimbat de la ultimul PASS:
  - validare cifra de control CUI LIPSEA la inregistrare (9b2dde6) - CUI malformat devenea
    tenant real cand ANAF era jos.
  - control_incrucisat compara D300 R31_2 (ajustare pro-rata, gol) in loc de R27_2 (TVA
    deductibila) -> rosu fals pe orice firma cu achizitii (0a0c3a0).
- **Infrastructura teste**: suita nu putea rula (test_bilant import gresit) - reparat (3578be5).
- **D212 (PFA)** intrat in plasa de regresie (8a9021b) - testele erau doar in __main__.
- Verificat OK fara reparatii: Facturare (numerotare/TVA/storno/contare), Securitate
  (0 rute neprotejate din 313, poarta beta, izolare tenant), Admin (13/13 guard superadmin),
  Cron recurente (scadenta+idempotenta), reconciliere/MT940/WooCommerce (acoperite de suita).

BUG-URI DE FOND notate separat (NU in scopul re-testarii de azi, de investigat):
1. **An fiscal modificat** (necalendaristic): lipsa coloana; stocuri_api.py/d101.py presupun
   calendaristic (date(an,1,1) hardcodat). Firma cu exercitiu modificat nu e suportata.
2. **D394 absent din control_fiscal_api.declaratii_datorate**: modulul exista si valideaza,
   dar nu apare in motorul de obligatii fiscale.

RAMAS — cere ochii/telefonul, NU SSH: **vezi CHECKLIST_BROWSER.md** (PWA P4.18-19, responsive
P4.20-21, audit vizual ~12 ecrane ramase). Grup fiscal/D101G si ONG: lasate deoparte (fara cod nou).

### REZULTAT INVENTAR (17.07.2026) - comparatie mecanica cu lista oficiala ANAF
Sursa: static.anaf.ro/static/10/Anaf/Declaratii_R/descarcare_declaratii.htm

CONSTRUITE (10 motoare + bilanturi): D100, D101, D112, D205, D212 (prin rip_api,
flux separat de declaratii_api), D300, D301, D390, D394, D406 (+ _active, _stocuri),
bilanturi S1005/S1003.

LIPSA - NIVEL 2 (rutina de cabinet, MERITA construite):
  D106 - dividende cuvenite actionarilor. Orice SRL care distribuie profit.
         Cea mai frecventa din tot ce lipseste.
  D230 - redirectionare 3.5% impozit. Anual, multi salariati.
  D307 - ajustare TVA la transfer de active.

LIPSA - NIVEL 3 (nisa, de decis explicit; nu se cara nedecise):
  D204 (asocieri fara pers. juridica), D104/D107 (ONG), D108 (reprezentante),
  D180 (nota certificare consultant fiscal), D223, D209, D221.

LIPSA - NIVEL 4 (RESPINS: administrative, nu se genereaza din evidenta contabila;
contabilul le face direct in SPV la infiintare/mentiuni):
  D010, D017, D060, D093.

LIPSA - marginale (de respins sau amanat cu motiv):
  D393, D395, D711, D089, D600, D603, D200, D201, D220, D224.

DECIZIE DEJA LUATA, documentata in cod (core/d101.py:43): D101G (grup fiscal) -
"se adauga cand apare un caz real care le cere". NU e gaura, e scop.

CONCLUZIE: "toate tipurile de declaratii" = 3 motoare reale (D106, D230, D307),
nu 40. Restul = respingeri motivate. Mentenanta creste cu 3 abonamente, nu cu 30.

REGULA PERMANENTA: orice declaratie noua intra in monitorul fiscal ODATA cu ea.
Construita si nemonitorizata = datorie, nu functionalitate.
