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
- **Export către programul contabilului — SAGA (F171) + WinMentor (F187) LIVRATE; Ciel BLOCAT pe spec.**
  SAGA (F171 18.07): facturi emise în XML propriu, format de la manual.sagasoft.ro topic-76.
  WinMentor (F187 19.07 LIVE): două fișiere INI (Facturi.txt + Articole.txt) co-locate, structură de la
  sursa OFICIALĂ (download.winmentor.ro/.../22 Structuri import, Facturi clienti.pdf Rev.1.2 + Articole noi.pdf),
  encoding Windows-1250 cu gard, cod articol derivat consecvent. NU e self-contained ca SAGA — dependență de
  config nomenclator WinMentor al cabinetului (clasă/gestiune/UM); v1=servicii, stoc complex=v2. Vezi DECIZII 19.07.
  LIMITA (ambele): round-trip real (import efectiv) pending cabinet real — cod+spec verificate, necolorat verde live.
- **Ciel — BLOCAT PE SPECIFICAȚIE (NU planificat orb).** 3 necunoscute verificate la sursă 19.07: (1) versiune —
  Ciel v6/v7/NextUp au formate DIFERITE (facturis.ro); (2) spec neclar publică (nu există portal oficial ca
  WinMentor); (3) cere coduri ANALITICE pe care iConta poate să nu le aibă la granularitatea Ciel. Se deblochează
  DOAR cu specificația de la sursa Ciel / un cabinet real care importă în Ciel. NU se construiește pe sursă
  secundară (ar rupe importul, ca BR-RO). [BLOCAT]
- **Igienă cont gratuit / CUI dublu emitent — ACOPERIT de F092 (coliziune_gratuit_v1) + F185 (gardul invers).**
  Verificat la sursă 19.07. Preluarea tenant = create-new e CORECT (contul gratuit e unealtă de emitere, nu sursă
  contabilă; datele reale vin prin migrare — DECIZII commit afd67d9, retenție 1 an). Riscul „același CUI emite din
  două locuri (gratuit + cabinet)" e DETECTAT + gestionat, NU restanță deschisă:
  - **F092 (18.07, direcția gratuit→cabinet):** la crearea tenantului de cabinet pe un CUI care are cont gratuit
    activ, se SEMNALEAZĂ cabinetului (tenant_creeaza + migrare_importa). Poartă enforcement: cont gratuit suspendat
    (activ=false) nu poate fi selectat/emite (auth_api.py:335). Închidere = superadmin (/admin/conturi-gratuite/
    {id}/suspenda). Auto-close RESPINS explicit (GDPR — deținătorul decide).
  - **F185 (19.07, direcția inversă cabinet→gratuit):** register gratuit pe un CUI deja sub cabinet → semnal
    simetric la înregistrare (inregistreaza_cont_gratuit), tot fără blocaj/auto-close.
  REZIDUAL: vizibilitate persistentă (raport superadmin de coliziuni active) = PLANIFICAT mai jos, nu gard critic.
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
> NOTA numerotare (19.07): sursa de adevar pentru F-numbers = FUNCTIONALITATI.csv (registrul canonic).
> Planurile de mai jos primisera informal F162/F163/F164/F169, dar registrul foloseste deja acele numere
> pentru features LIVRATE (F162=D112, F163=D390, F164=push control fiscal, F169=control incrucisat TVA).
> Re-numerotate aici la F180+ (peste max registru=179) ca sa nu coliza. Istoria (ISTORIC.md) ramane neatinsa.
- F180 (re-numerotat din F162 — coliziune cu F162=D112 din registru): platitor_tva editat manual vs ANAF -> avertisment la salvare vector fiscal + semafor rosu Control fiscal la divergenta [PLANIFICAT]
- F182 (re-numerotat din F164 — coliziune cu F164=push control fiscal din registru): cont_venit_implicit setabil din UI (Setari cont/profil firma), acum doar din DB [PLANIFICAT]
- F165: auditor conformitate schema tenant vs template + auto-ALTER (drift recurent pe tenant_003/004: link_plata, sursa_externa lipseau); rulat la provisionare + verificabil on-demand [PLANIFICAT]
- F168: la lansare publica, email automat catre conturile create in perioada beta (site in lucru); sterge BETA_COD_ACCES din env pt acces public [PLANIFICAT]
- F181 (re-numerotat din F163 — coliziune cu F163=D390 din registru): control incrucisat RAMAS D101 / D100 / D394. LIVRAT 19.07: D112=F162, D390=F163 (vezi registru). Text tehnic pastrat: extindere control incrucisat la D112 / D101 / D100 / D390 / D394; acelasi tipar ca TVA. CONSTATARE 15.07 (analiza la sursa): D300 intoarce (xml, res) cu res['R'] = randurile -> comparabil direct. D112 intoarce doar (xml, avertismente) si isi tine agregatele in variabile de structura XML (c2_d14/d15/d16...), NU expune totaluri contabile. Doua cai: (a) parsare XML = fragil, se rupe tacut la schimbare de structura ANAF; (b) d112.genereaza sa intoarca si totalurile (CAS/CASS/impozit/CAM) = refactor pe modul validat DUKIntegrator. Recalcularea paralela din salarizare.calcul_salariu NU e echivalenta (ar compara contabilitatea cu propriul calcul, nu cu ce se declara efectiv - un bug in D112 ar trece neobservat). Conturi tinta (verificate in salarizare.py): CAS=4315, CASS=4316, impozit=444, CAM=436, brut=421. Decizie de arhitectura, nu extindere mecanica [PLANIFICAT]
- F166: parser MT940 (SWIFT) - LIVE 14.07 in banca_parser (marker :61:/:20:). RAMAS: validare pe fisier MT940 real din banca (campul :86: variaza per banca)
- F167: Open Banking automat prin Enable Banking (AIS EU; tier gratuit Restricted Production pt conturi proprii = dogfooding; productie = contract + KYB + cost pe conexiuni). Dupa MT940. Automatizeaza ADUCEREA extrasului, nu doar citirea [PLANIFICAT-etapa-2]
- F183 (re-numerotat din F169 — coliziune cu F169=control incrucisat TVA din registru): audit de PRELUARE firma - acelasi motor control_incrucisat aplicat la migrare: inventar transparent (ce pot/nu pot verifica), raport datat cu trei categorii (coerent / divergent / NEVERIFICAT-lipsa document), repetabil pe masura ce apar documentele. Acoperire profesionala la preluarea raspunderii [PLANIFICAT]
- F186: raport superadmin de coliziuni CUI active (CUI cu cont gratuit + tenant de cabinet, ambele activ=true) -
  vizibilitate PERSISTENTA pentru follow-up (superadmin vede lista si poate suspenda). Complement la semnalele de la
  creare (F092 gratuit->cabinet, F185 cabinet->gratuit), care sunt EFEMERE (doar la momentul actiunii). Rezolva
  handoff-ul: semnalul apare la cabinet/registrant, dar inchiderea o face superadmin - fara raport, superadmin nu
  afla ce coliziuni pendinte exista. NU gard critic (riscul primar e deja detectat+gated); imbunatatire de proces [PLANIFICAT]
- GARD preventiv teste (INAINTE de primul client real): testele NU pot DROP SCHEMA fara prefix de test explicit
  (test_*) sau tid dintr-un range rezervat. Motiv: la testul F185 (19.07), un cont gratuit provizionat de test a
  primit numele reutilizat 'tenant_003' (max-existing+1, nu id-based) - DROP-ul de curatare a fost corect (schema
  FRESH, verificat inainte), dar numele reutilizabil poate induce in eroare. Azi toate datele sunt de test -> fara
  risc; devine OBLIGATORIU la primul cabinet real, cand un DROP gresit ar sterge date reale. [PLANIFICAT]
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

## Actualizare 18.07.2026 — SPV/OAuth complet (e-Factura + e-Transport LIVE); ce ramane

Clusterul SPV/OAuth construit si testat izolat (ISTORIC 18.07 partile 5-7): e-Factura (F126/F160/F176-F179)
+ e-Transport (F044/F121). F126, F044, F121 -> LIVRAT. Ce ramane, separat pe DE PROBAT (blocat pe drept)
vs DE CONSTRUIT (munca reala):

### DE PROBAT (blocat pe drept SPV — nu de construit, de dovedit cu un patron real)
- **Dus-intors LIVE e-Factura (trimite recipisa + primeste factura reala)**: cod complet (F160 send + F178
  poll + F179 receive + four-eyes), NEDOVEDIT live. Dev token (certificat admin) n-are drept SPV pe niciun
  CIF real. Se probeaza doar cu primul patron real cu certificat inrolat pe CIF-ul LUI. Necolorat verde (ca F176).
- **Dus-intors LIVE e-Transport (upload UIT + primeste codul UIT de la ANAF)**: cod complet (F121 mecanism +
  UI, garda de timp), NEDOVEDIT live - pending drept e-Transport pe CIF real (acelasi token, drept unificat).
  Ecran testat cu notificare injectata + poarta validare pe TEST.
- La primul caz real, **de confirmat LA SURSA** (parsarea defensiva e in cod, formele sunt din docs, nu live):
  formatul exact JSON + structura ZIP din raspunsul stareMesaj/descarcare; cuota ZILNICA ANAF; timpul normal
  de prelucrare (pragul de 2 zile pt starea 'investigatie' e conservator).

### DE CONSTRUIT (munca reala ramasa)
- **F127/F128 — AMANATE**: pendinte pe ANAF adaugand OAuth la SPVWS2. Deadline review 17.08.2026 (raspuns
  asteptat de la spv.webservice@mfinante.ro). Fara raspuns pana atunci -> raman AMANATE.
- **v2 F163 — persistarea randurilor decontului D300 depus** (coloana/tabel la generare/depunere) -> abia atunci
  D-vs-D real D390<->D300. Prerechizit: persistarea decontului depus, utila si pentru alte controale intre
  declaratii. Azi doar declaratii_depuse (jurnal gol: tenant/an/luna/tip/data, fara valori de randuri/XML) exista.
  Motiv (verificat la sursa 19.07, in DECIZII.md): randurile intracom R1_1/R5_1 ale D300 sunt manual-only si
  nepersistate -> pana la persistare, F163 = D390 vs evidenta validata, nu D-vs-D. [PLANIFICAT]
- **v2 F164 — digest email Brevo** (rezumat zilnic/saptamanal al rosurilor de control fiscal DESCHISE per cabinet,
  pentru contabilii care nu intra zilnic in app). Completeaza v1 (clopotel in-app + click, LIVE 19.07): v1 rezolva
  restanta 17.07 (alerta ajunge in app); digestul acopera cazul "contabil care nu intra zilnic". De construit CAND
  exista semnal real ca se rateaza alerte, NU speculativ. Infra Brevo gata (5 module: observare.trimite_email_html/
  _trimite_brevo, folosita de monitor_fiscal/spv_refresh/sinteza_zilnica/notificari_scadenta/pachete). [PLANIFICAT]
- **v2 F184 — declansator COTE-driven proactiv (re-verificare instant la depasirea unei date de valabilitate din
  common.COTE): RESPINS.** Temei: cotele traiesc IN COD (common.COTE); o cota noua cere oricum editare + deploy
  manual; cronul zilnic (F184 v1) prinde firmele neconforme a doua zi. Declansatorul instant n-ar castiga nimic
  real fata de un eveniment care deja implica deploy. Decalajul de o zi = nesemnificativ. [RESPINS]

### LIVRAT 18.07 (mutat din backlog; detaliu in ISTORIC + FUNCTIONALITATI.csv)
- **F126 e-Factura cap-coada**: SEND (model principal cabinet XOR gratuit + F160 + F178 poll recipisa) +
  RECEIVE (F179 cron listaMesajeFactura filtru=P -> efactura_primite, dedup + anti-scurgere cif_beneficiar) +
  FOUR-EYES (ecran validare, cont sugerat confirmat de om, cross-control TVA existent). listaMesajeFactura
  verificat la sursa oficiala (mfinante API). Ramane doar dus-intorsul LIVE (mai sus, DE PROBAT).
- **F044 + F121 e-Transport cap-coada**: F044 (generator XML UIT) -> LIVRAT (XML-ul merge la API, nu doar
  manual); F121 (trimitere) -> LIVRAT: mecanism upload_uit/stare_uit/lista_uit pe spv_principal (drept
  UNIFICAT) + garda de timp UIT (3z inainte, 5z/15z valabilitate) + UI (buton Trimite UIT, 2 semafoare
  timp/trimitere). Endpoint ETRANSPORT/ws/v1 la sursa. Ramane doar dus-intorsul LIVE (mai sus, DE PROBAT).
- Cele 3 rute OAuth moarte din main.py — sterse la pas 1 conector (f3a33f3). Daca mai apar in vreo lista, scoate-le.
