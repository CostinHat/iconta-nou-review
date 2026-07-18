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

### Cere Costin singur [C] — DONE 14.07
Rulate 14.07 (vezi jos "Actualizare 14.07" → RAMASE): P1.1, P1.4, P1.5 (simulat), P2.9-P2.11, P5.24.
Backup automat LIVE (systemd timer zilnic 03:00, retentie 7z). Raman deschise doar [D] si [T].

### Cere telefon [T] — după HTTPS (nou.iconta.eu e sus)
- P4.18 PWA: (FACUT iOS 14.07 - standalone+offline OK) ramas doar Android, verificare secundara
- P4.19 Pozează bon: cameră, multi-imagine, flux până la notă
- P4.20/21 Responsive portal <400px, landing <900px/<560px

## 2. Blocate — DUK / desktop ANAF
- (REZOLVAT, arhivat 17.07) D394 valideaza acum headless prin core/duk.py (jar, nu GUI desktop) —
  blocajul "validare desktop" nu mai exista (duk.py:154 "dovedit 15.07", CLAUDE.md status 16.07).
  Nimic blocat pe desktop-DUK azi. (e-Transport prin API SPV = blocaj extern SPVWS2, tracked in CARENTE.)

## 3. Sesiune desktop (Word, nu SSH)
- (PARTIAL) Audit design 12.07: INCHISE (canonic + verificator TOTAL 0 pe toate 30 ecrane): formatare bani/data/procent, culori-card, iconite, tipografie, culori/borduri/raza. Design System v2.9 + verificator 9 reguli, la zi.
- RAMAS DIN AUDIT DESIGN (nefacut):
  1. Verificare VIZUALA doar ~10/30 ecrane. De vazut cu ochii restul ~20 (declaratii, control, termene, setari, recomanda, admin*, etransport, produse, tipare, semafor, validat, pachete, capacitate) - verificatorul e curat pe ele dar nu prinde tot.
  2. Categorii NEATACATE: spacing/padding/gap inline (fara inventar inca); wrapper alb pe formulare (cap.2 - verificatorul n-are regula, prins doar 1 manual); aliniere tabele (cap.4 sume la dreapta, neverificata sistematic); anatomia ferestrei (cap.1 entitate-antet/titlu-h2-corp, neauditata vizual).
  3. TASK 0a mai vechi (cerut 10.07, inca nefacut): audit cod mort + functionalitati ascunse ad-hoc fara conditie documentata + diferente cabinet/client inconsecvente.

## CARENTE — inventar (consolidat 13.07.2026, curatat 17.07.2026)
Curatenie 17.07: 7 intrari confirmate rezolvate prin verificare la sursa (grep/test) mutate in
ISTORIC.md, sectiunea "REZOLVARI CONFIRMATE 17.07 (verificate retroactiv)". Raman deschise, cu
starea reverificata azi:
1. **e-Transport — trimitere directa prin API SPV**: exista generarea XML pentru upload MANUAL in
   SPV (core/etransport.py: xml_notificare); trimiterea directa prin API SPV NU exista — blocaj
   extern SPVWS2 (acelasi blocant ca restul apelurilor SPV). Verificat 17.07: etransport.py are
   doar xml_notificare, nicio functie de trimitere.
2. **Testare pilot P1-P5**: partial. [C] (Costin) rulate 14.07 (P1.1/P1.4/P1.5-simulat/P2.9-2.11/
   P5.24) + PWA iOS (P4.18). RAMAN: [D] validare fiscala cu Daniela (P1.2/P1.3/P2.6-2.8) + [T] telefon
   (P4.19 pozeaza bon, P4.20/21 responsive, Android). Checklist manual, neverificabil prin cod.
3. **Audit design ramas**: spacing/padding inline (inchis explicit ca datorie acceptata), migrare
   paleta iconite (decizie amanata), anatomia ferestrei + alinierea tabelelor nesistematizate vizual
   (~20/30 ecrane nevazute cu ochii; verificatorul e curat pe ele dar nu prinde asezarea).

## 4. Infra
- **Reboot kernel** — inca necesar (verificat 17.07: /var/run/reboot-required prezent; ruleaza
  6.8.0-117, in asteptare 6.8.0-124/-134). Fereastra linistita (downtime clienti, Daniela pilot).
  (systemd 8010 REZOLVAT 13.07 — arhivat, vezi ISTORIC:17 "iconta-nou.service enabled".)

## 5. Iterații viitoare (nu urgente)
- **Mesaje de eroare `.mig-gol` -> `arataMesaj`: FACUT 18.07 (48/53).** Cele ~50 utilizari `.mig-gol` din blocuri catch/validare/loading convertite la `arataMesaj(zona, txt, tip)` (eroare/avert/info) in rip_ecran/operatiuni/etransport/cabinet/migrare/firme/facturi_ecran. RAMAN 5 template-embedded (NU catch, HTML in template - lasate deliberat, nu se ghiceste): asistenti.js:330 (ternar in render), firme.js:428 (eroare conditionala inline in panou), :1315 (ramura ternar `${r.mesaj}`), :1343 (lista .map de mesaje - continut, nu feedback), :1689 (nota permanenta 'Atentie: nota legata de factura'). Verificator TOTAL 0. LIMITA: caile de eroare din catch nu au fost declansate runtime (greu de atins) - conversie mecanica + node-check + aliniere cu tiparul arataMesaj existent in app.
- **Export către programul contabilului — PARȚIAL: SAGA LIVRAT (F171 18.07), WinMentor/Ciel rămân.**
  SAGA: export facturi emise în XML propriu (Diverse → Import date), rută read-only, format verificat
  la sursă (manual.sagasoft.ro topic-76). Puntea care face posibilă poziționarea „firma emite în iConta,
  contabilul rămâne pe SAGA" (DECIZII.md 18.07). RĂMÂNE: WinMentor și Ciel (alt generator, altă
  structură — codul e structurat pe format ca să le primească). LIMITA SAGA declarată: neconfirmat pe
  import real (encoding UTF-8 vs Windows-1250 + clasificare ieșire = ochi uman). NU depinde de OAuth ANAF.
- **Igienă la migrare: contul gratuit vechi rămâne activ după preluarea firmei de un cabinet** (adăugat
  18.07, punct de VERIFICAT, nu gol). Preluarea tenant = create-new e comportament CORECT (contul
  gratuit e unealtă de emitere, nu sursă de adevăr contabil; datele reale vin prin fluxul de migrare
  al contabilului — decis în DECIZII.md commit afd67d9, cu retenție 1 an). RĂMÂNE de verificat: după
  ce contabilul aduce firma în cabinet, contul gratuit vechi (același CUI) rămâne activ → firma ar
  putea emite din două locuri cu același CUI. De închis contul gratuit la migrare = igienă. Doar de
  verificat/tratat la migrare, nu acum.
- Cod 10 CM (reducere timp muncă, art. 19) — INTEGRAT, nu mai e iterație viitoare (corectat 17.07:
  nota veche "exclus din dropdown, `calcul_cm_cod10` neintegrat" era contrazisă de cod). Dovadă:
  `calcul_cm_cod10` definit (salarizare.py:208) + apelat în flux real (salariati_api.py:222) + în
  dropdown (flux_concediu.js:14) + câmp venit condiționat (:105) + testat (test_salarizare.py).
  Vezi ISTORIC "REZOLVĂRI CONFIRMATE 17.07".
- raporteaza.js — verifică vizual data "cu_ora" în feed (migrat azi).
- Verifică date CM de test invalide în alte tenant-uri (CCMAD corupt deja șters din tenant_002).

---

## ANEXA — Inventar functionalitati
Stersa 17.07: era duplicat al FUNCTIONALITATI.csv (registru canonic din 16.07, 164 pozitii cu
ID / Stare / Sursa cod / Temei legal / Testat). Doua inventare = drift garantat. Sursa unica:
**FUNCTIONALITATI.csv**.

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
   (D394-absent din semafor: REZOLVAT 18.07 - semafor faza 3 conecteaza D394+D406, acum 9/9.)

RAMAS — cere ochii/telefonul, NU SSH: **vezi CHECKLIST_BROWSER.md** (PWA P4.18-19, responsive
P4.20-21, audit vizual ~12 ecrane ramase). Grup fiscal/D101G si ONG: lasate deoparte (fara cod nou).

### REZULTAT INVENTAR (17.07.2026) - comparatie mecanica cu lista oficiala ANAF
Sursa: static.anaf.ro/static/10/Anaf/Declaratii_R/descarcare_declaratii.htm

CONSTRUITE (10 motoare + bilanturi): D100, D101, D112, D205, D212 (prin rip_api,
flux separat de declaratii_api), D300, D301, D390, D394, D406 (+ _active, _stocuri),
bilanturi S1005/S1003.

LIPSA - NIVEL 2 (rutina de cabinet, MERITA construite):
  D230 - redirectionare 3.5% impozit. Anual, multi salariati.
  D307 - ajustare TVA la transfer de active.
  (D106 RESPINS 18.07 - eroare de inventar: NU e "cea mai frecventa", e in afara publicului iConta.
   "Declaratie informativa privind dividendele cuvenite actionarilor" se depune DOAR de societatile
   nationale / companiile nationale / firmele cu capital de stat (OPANAF 1292/2014 + instr_106_2014,
   potrivit OG 64/2001). Clientii iConta = firme PRIVATE (SRL/PFA/micro) -> zero utilizatori.
   Dividendele private sunt acoperite de D205 (LIVE). Vezi DECIZII.md 18.07.)

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

CONCLUZIE: "toate tipurile de declaratii" = 2 motoare reale (D230, D307), nu 40
(D106 RESPINS 18.07 - firme de stat, in afara publicului). Restul = respingeri
motivate. Mentenanta creste cu 2 abonamente, nu cu 30.

REGULA PERMANENTA: orice declaratie noua intra in monitorul fiscal ODATA cu ea.
Construita si nemonitorizata = datorie, nu functionalitate.

### RESTANTE DIN 17.07.2026 (consemnate ca sa nu se piarda)

1. COD MORT OAUTH in main.py (~liniile 4953-5015): 3 rute scrise orb, netestate:
   /anaf/oauth/start, /efactura/callback, /anaf/oauth/stare.
   Dovada ca n-au rulat: public.anaf_tokens NU EXISTA in iconta_v2 (psql: relation
   does not exist), iar CREATE TABLE era in handler. Zero consumatori in *.js/*.html.
   /efactura/callback NU corespunde cu ce e inregistrat la ANAF (/anaf/oauth/callback).
   SE STERG la construirea conectorului (regula 0a). E in BRIEF_CODE_CONECTOR_SPV.md.

2. ALERTELE FISCALE NU AJUNG LA OM. Constatat 17.07: alerta monitor_fiscal despre
   OPANAF 138/2026 (modificare D204) a stat 6 zile necitita in inboxul personal,
   printre 104 mesaje. Monitorul PRINDE corect - dar mesajul se pierde.
   Alertele fiscale trebuie sa apara IN APLICATIE (unde se uita contabilul oricum),
   nu doar pe email. De verificat ce exista deja (F103 are banner/anunturi?) inainte
   de a construi ceva nou.
   NOTA: alerta asta a fost declansatorul intregului inventar declarativ. Monitorul
   si-a facut treaba; canalul de livrare e problema.

3. D212 IESE DIN TIPAR: merge prin core/rip_api.py + core/d212_engine.py, in afara
   core/declaratii_api.py, unde sunt toate celelalte 9 (d100...d406).
   INTREBARE DESCHISA pentru Costin: e intentionat (D212 = PF/PFA, alt regim) sau
   e drift de arhitectura? Daca e intentionat -> se scrie motivul. Daca nu -> se aliniaza.
   Pana la raspuns, NU se atinge.
