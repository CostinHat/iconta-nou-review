# INVENTAR LIVE — 179 poziții (din FUNCTIONALITATI.csv)

*Generat automat din `FUNCTIONALITATI.csv` (doar `Stare = LIVE`). Coloana `Testat` redată ca atare, neinterpretată. Gruparea pe zone e dedusă din modulul-sursă + denumire.*

## Rezumat pe zone
- **SPV / e-Factura / e-Transport** — 12
- **Declaratii fiscale** — 22
- **Salarizare & HR** — 11
- **Stocuri & gestiune** — 14
- **Banca & reconciliere** — 6
- **Casa & bonuri/chitante** — 5
- **TVA & curs valutar** — 12
- **Facturare & documente** — 17
- **Contabilitate & note** — 9
- **Operatiuni contabile speciale** — 14
- **Control fiscal** — 8
- **Portal client** — 8
- **Migrare & import** — 6
- **AI & asistenta** — 1
- **Autentificare & sesiuni** — 4
- **Notificari** — 3
- **Integrari (Woo/recurente)** — 2
- **Administrare cabinet & useri** — 7
- **Firme & parteneri** — 3
- **Rapoarte & documente comerciale** — 4
- **Infrastructura & sistem** — 9
- **Altele / transversal** — 2

**TOTAL LIVE: 179**

## SPV / e-Factura / e-Transport (12)
- `F020` | Comodat, chirii, refacturari | Testat: pytest
- `F035` | D406 SAF-T lunar | Testat: DUKIntegrator 0 erori end-to-end
- `F036` | D406 Active (SAF-T anual) | Testat: pe XSD oficial
- `F043` | Import e-Factura (UBL) | Testat: (gol)
- `F044` | Notificare e-Transport | Testat: vizual + backend HTTP (POST etransport/trimite: poarta de timp blocheaza prea-devreme; GET trimiteri: semafor timp separat de trimitere)
- `F121` | Trimitere e-Transport prin API SPV | Testat: 8 teste unit + backend HTTP (blocat_timp prea-devreme; GET trimiteri 2 semafoare verde/galben/rosu); node+verificator 0; migrare 2/2
- `F126` | e-Factura SPV complet | Testat: backend HTTP dovedit: GET lista (preview parsat + cont sugerat), valideaza -> factura_id legat + status validata + cont, idempotent (deja_validata), respinge+motiv (ramane in istoric), 422 fara motiv; ecran node+verificator 0. LIMITA: import/recipisa LIVE pending drept (dev token, ca F176) - four-eyes testat cu ciorna injectata (factura parsata, factura_id NULL)
- `F160` | e-Factura SPV pentru contul gratuit | Testat: stiva completa HTTP: login->POST trimite-spv factura reala -> auth+spv_principal(firm 1)+4 porti+upload live -> ExecutionStatus=1 'fara drept' (asteptat). 31 teste + toate portile dovedite (fara_token/validare/deja_trimisa/upload); node+verificator 0
- `F176` | Conector OAuth SPV/ANAF | Testat: test_spv_conector.py (12 mock) + validare reala productie 18.07 (hello 200; listaMesajeFactura per-CIF 200+eroare drept; token criptat/decriptat confirmat)
- `F177` | Cron refresh token SPV (90 zile) | Testat: real 18.07 pe token_id=21 (dev): refresh fortat prin driver -> access_expira avansat 90z + reimprospatat_la setat + cifertext rotit + decriptabil, serial identic; selectie marja 15z=0 pe token proaspat; rotatia acoperita si de test_spv_conector (mock)
- `F178` | Cron poll e-Factura (stareMesaj + descarcare recipisa) | Testat: 9 teste (6 clasificator pe forme documentate stareMesaj: in-prelucrare/ok/nok/erori/timeout->investigatie/gunoi->neasteptat; 3 integrare DB+mock: ok+descarca recipisa salvata, skip-auth NU marcheaza randul, terminal ne-repollat); rulare reala + timer activ. LIMITA: round-trip incarcat->ok pending drept (nedovedit fara CIF cu drept, ca F176)
- `F179` | Cron receive e-Factura (facturi furnizori din SPV) | Testat: 4 teste (anti-scurgere cif_beneficiar, ciorna daca parsabila cu factura_id NULL, descarcata fallback neparsabil, dedup nu reimporta) + 23 teste SPV fara regresie; rulare reala prin stack (listaMesajeFactura prod filtru=P -> ANAF verdict fara drept, asteptat). RAMAS F126 complet: UI four-eyes (pasul 5). LIMITA: import live pending drept (ca F176)

## Declaratii fiscale (22)
- `F013` | Bilant anual S1005/S1003 | Testat: validator ANAF
- `F019` | Coada de validare patru-ochi | Testat: 403 dovedit pe self-approval
- `F026` | Declaratia D100 | Testat: DUKIntegrator
- `F027` | Declaratia D101 + IMCA | Testat: DUKIntegrator
- `F028` | Declaratia D112 | Testat: DUKIntegrator cap-coada
- `F029` | Declaratia D205 + distribuire dividende | Testat: DUKIntegrator + ANAF
- `F030` | Motor D212 (PFA/II/IF) | Testat: pytest
- `F031` | Declaratia D300 | Testat: DUKIntegrator
- `F032` | Declaratia D301 | Testat: DUKIntegrator
- `F033` | Declaratia D390 (VIES) | Testat: DUKIntegrator
- `F034` | Declaratia D394 | Testat: generator complet; valideaza FARA ERORI pe DUK headless (core/duk.py); conectat in semafor faza 3 (control_fiscal_api.declaratii_datorate - grep D394 = 5 linii; commit 3cc1455)
- `F037` | D406 Stocuri (la cerere) | Testat: pe XSD oficial
- `F038` | Dispatch declaratii | Testat: (gol)
- `F051` | Verificator praguri Intrastat | Testat: (gol)
- `F053` | Import istoric declaratii (migrare) | Testat: (gol)
- `F125` | Trimitere D390 clasificari manuale | Testat: core/test_d390.py (8 teste, +4 F125: reclasificare fara dubla numarare, operatiuni_auto) + DUK stare VALID pe XML cu reclasificare L->P + linie manuala S + E2E autentificat (reclasificare, tranzitii ilegale 422, persistenta)
- `F133` | Tichete de masa + vacanta + cadou in stat plata (Faza 1 + 2a + 2b1) | Testat: test functional + DUK (D112 masa+vacanta valid FARA ERORI) + verificat vizual cadou; non-regresie
- `F162` | Control incrucisat: D112 (salarii) vs contabilitate | Testat: pytest 13 teste (parsare XML, coerent verde, suprataxa part-time 458->4315, cod lipsa=0 declarat, stat necontabilizat->executabil, ciorna->sugerat, divergenta partiala->investigatie fara ajustare, toleranta creste cu efectivul, rotunjire CAM nu da rosu fals pe 40 salariati, temei declara toleranta) + functional real tenant_002 iunie 2026 (rosu real: D112 declara 282 impozit / 1250 CAS / 500 CASS, dar 444/4315/4316 = 0 lei -> stat de plata necontabilizat). UI: conectat in ecranul Control fiscal (sectiunea Declaratie vs contabilitate, langa TVA si D390), aceeasi anatomie; restart HTTP 200
- `F163` | Control incrucisat: D390 (bunuri IC) vs evidenta validata + D300 depus (D-vs-D real F198) | Testat: pytest 11 teste (4 directii: rosu pe declarat-la-VIES-absent-din-evidenta, gri pe invers, gri pe cifre diferite, tacut pe ambele zero; + verde coerent, toleranta rotunjire leu, ciorna nu e dovada, temei+limita pe fiecare, 3 fereastra lunar/trimestrial) + functional real tenant_002 iunie 2026 (verde pe IT livrare 5000 + DE achizitie 2000 contabilizate; rosu-sugerat pe aceleasi necontabilizate; RO exclus corect). UI: conectat in ecranul Control fiscal (sectiunea Declaratie vs contabilitate, langa TVA si D112), aceeasi anatomie semafor + temei + limita + remediu sugerat; gri se afiseaza gri (nu ascuns); _verificari_contabile pe tenant_002 iunie 2026 expune toti 3 verificatorii; restart serviciu HTTP 200; node --check ESM + verificator DS 0 candidate. D-VS-D (F198, 22.07): 9 teste (rosu real D390 5000 vs D300 fara R1_1; verde ambele 5000; gri cifre diferite; gri randuri NULL; gri zero depuneri; tacut ambele 0; achizitii R5_1; + 2 DB _d300_depus_randuri prin depunere d300 FABRICATA in ROLLBACK) + E2E verifica_d390 pe tenant_002 (d300 fabricat -> a treia comparatie curge: verde livrari + rosu achizitii, stare rosu). UI + push F164 verificator-agnostice (findings curg in bucketul d390, zero cod nou). DOVEDIT PE DATE REALE 22.07: PRIMUL parcurs cap-coada al fluxului de depunere prin app (coada era complet goala; cele 5 depuneri istorice = sursa=migrare) - D300 depus real pe tenant_002 2026/06 (sursa=iconta, R1_1=5000/R5_1=2000 coerente cu D390) -> F163 VERDE corect pe ambele (coincid). 'depusa' = stare interna jurnal (spv_index NULL, nu transmite la ANAF). Limita 'doar depunere fabricata' RIDICATA. Ramas: divergenta reala (rosu) inca doar pe fabricat/E2E; fricțiune permisiuni (admin default nu poate depune) = DE_FACUT.
- `F169` | Control incrucisat: declaratie vs contabilitate (TVA) | Testat: pytest (7 teste) + verificat pe date reale tenant_004
- `F192` | Declaratia D710 (rectificativa D100) | Testat: pytest test_d710.py (25 teste) + DUK valid FARA ERORI
- `F198` | Persistarea declaratiei depuse (xml + randuri) - F163v2 | Testat: 6 teste (randuri_din_res dataclass cu Decimal / d112-lista->None, round-trip Decimal prin jsonb, d112 NULL in DB, VERSIONARE prin marcheaza_depusa real - 2 randuri nr 1/2 cu xml/randuri proprii + vederea da valorile NOI, D710 coexista cu D100) + migrari public aplicate (randuri+sursa, versiune). Suita 466 verde + verificator DS 0

## Salarizare & HR (11)
- `F021` | Contracte de munca speciale | Testat: pytest
- `F075` | Client REGES-ONLINE | Testat: (gol)
- `F078` | Salariati (CRUD) | Testat: bug tip_norma reparat
- `F079` | Import salariati (migrare) | Testat: (gol)
- `F080` | Calcul salarizare (brut->net) | Testat: 285 pytest pe core + DUK pe D112
- `F087` | Stat de plata + fluturasi | Testat: vizual + parte din D112 DUK
- `F122` | Cod 10 CM in flux | Testat: —
- `F134` | Plata salariilor pe card (fisier bancar) | Testat: core/test_plata_salarii.py (11 teste: iban_valid mod-97 + charset SEPA + rotunjire) + E2E autentificat pe tenant_002 (preview+download, fisier valid pe XSD oficial, multi-plata, fara_iban, cai de eroare)
- `F135` | Pontaj angajati | Testat: pytest (5) + functional
- `F136` | Adeverinte salariati | Testat: pytest (3) + functional
- `F137` | Coduri COR pe contracte | Testat: core/test_cor.py (4 teste normalizare diacritice) + loader auto-valideaza (4422 coduri unice/6 cifre) + E2E: /cor cautare cod+denumire, validare creare/editare (cod inexistent respins), 35 teste non-regresie

## Stocuri & gestiune (14)
- `F052` | Inventariere anuala | Testat: pytest
- `F063` | Obiecte de inventar | Testat: pytest
- `F076` | Retetar HoReCa (GV) | Testat: pytest 23 + date reale
- `F088` | Stocuri global-valorice | Testat: pytest
- `F089` | Stocuri cantitativ-valorice (CMP) | Testat: pytest
- `F138` | Transfer intre gestiuni | Testat: core/stocuri_cv_api.py (transfer/reclasificare/stoc_pe_locatii); test functional pe Postgres
- `F139` | Landed cost pe NIR | Testat: core/stocuri.py (nir_gv landed) + core/test_stocuri.py (6 teste landed); test functional pe Postgres
- `F140` | Analitica de stoc | Testat: core/stocuri_cv_api.py (analitica/set_nivel_minim); test functional pe Postgres
- `F141` | Coduri de bare in gestiune | Testat: core/stocuri_cv_api.py (gaseste_barcode/set_barcode); test functional pe Postgres (unicitate + reutilizare dupa stergere)
- `F142` | Inventar pe mobil | Testat: static/js firme.js (mod inventar mobil) + core/stocuri_cv_api.py inventar(); test functional pe Postgres
- `F150` | Import retete la migrare | Testat: —
- `F151` | Import articole si stoc initial CV | Testat: —
- `F172` | Punte factura -> stoc (descarcare la emitere) | Testat: functional real tenant_002 (DA stoc 100->97 legat factura_id; NU neatins; serviciu fara poarta; gratuit exclus)
- `F187` | Export facturi emise catre WinMENTOR | Testat: pytest 11 teste (cod determinist+consecvent Facturi/Articole; structura ambelor fisiere camp cu camp contra spec oficial; Item=cod;UM;cant;pret + Item_TVA; UM absent din Articole.txt; dedup articole pe cod; config override serviciu/gestiune/clasa; gard encoding cp1250 s/t->cedila + caracter neencodabil->exceptie) + functional REAL tenant_002 cu curatare (factura status=emisa cu diacritice -> ambele fisiere corecte, cod consecvent AD2090A939D5, cp1250 corect) + HTTP: /export-winmentor 404-nicio-factura (ruta), SAGA month 200 (bug reparat), detaliu int 200 (fara regresie). Nu avem WinMentor live -> conformitate la spec, riguroasa.

## Banca & reconciliere (6)
- `F002` | Incredere si invatare AI | Testat: pytest
- `F011` | Contabilizare extras de cont | Testat: pytest
- `F012` | Parser extras bancar | Testat: validat la leu pe ING
- `F024` | Credite bancare si garantii | Testat: pytest
- `F073` | Reconciliere bancara (matching) | Testat: pytest
- `F166` | Import extras bancar MT940 (SWIFT) | Testat: pytest (4 teste)

## Casa & bonuri/chitante (5)
- `F003` | Import Raport Z din AMEF | Testat: date reale de re-verificat
- `F015` | Registru de casa + plafoane | Testat: pytest
- `F017` | Chitante emise | Testat: (gol)
- `F023` | Regula cotelor de TVA | Testat: pytest
- `F157` | Chitante in contul gratuit | Testat: cod: buton negated + ruta cere_context; click-through gratuit recomandat

## TVA & curs valutar (12)
- `F025` | Curs valutar BNR | Testat: pytest
- `F041` | Diferente de curs valutar | Testat: pytest
- `F046` | Contare facturi + TVA + storno | Testat: pytest
- `F070` | Nomenclator produse + cota AI | Testat: vizual (reconectat 13.07)
- `F091` | Taxare inversa interna | Testat: pytest
- `F095` | Regim special agricultori | Testat: pytest
- `F096` | Regim special aur de investitii | Testat: pytest
- `F097` | TVA la incasare | Testat: pytest; de testat P2.6
- `F098` | Regim special marja (second-hand) | Testat: pytest
- `F099` | Regim special agentii de turism | Testat: pytest
- `F180` | Avertisment regim TVA vs ANAF + semafor Control fiscal | Testat: 9 teste pure (stare_tva_anaf + avertisment_tva_anaf + constatare_regim_tva: verde/rosu/gri, contract remediu=investigatie/limita) + functional REAL pe tenant_002 (live ANAF 14399840: local!=ANAF->avertisment, ==->none; gri fara snapshot; cale ROSIE end-to-end cu divergenta fortata in tranzactie ROLLBACK, tenant_002 neatins) + migrare 2/2 scheme + suita 447 verde + verificator DS 0
- `F184` | Conformitate cota TVA facturi emise (punte legislatie->re-verificare v1) | Testat: pytest 7 teste PURE constatare_cota_tva cu date reale via primitive period-aware (19%% dupa 01.08.2025->ROSU; 21%% corect->verde; 19%% inainte de schimbare->verde period-corect; 9%% redus->NU fals-pozitiv; scutit 0->ignorat; mix->doar linia gresita; temei+limita declarate) + 50/50 fara regresie. Functional REAL tenant_002 cu curatare: factura emisa test 19%% in 09/2025 -> engine verifica_cota_tva ROSU-sugerat pe factura corecta (19%% in loc de 21%%); verificatori_rosii din push include 'cota_tva'; endpoint HTTP /control-fiscal/2 (token cabinet) expune cheia cota_tva_conformitate. node --check ESM + verificator DS 0. Dedup mostenit din F164 (decide() e verificator-agnostic pe seturi de chei).

## Facturare & documente (17)
- `F004` | Validare CUI la ANAF | Testat: (gol)
- `F018` | Parteneri (clienti/furnizori) | Testat: (gol)
- `F045` | PDF factura | Testat: (gol)
- `F047` | Facturi recurente | Testat: de testat cap-coada P1.4
- `F048` | Profil firma + model factura | Testat: (gol)
- `F050` | Operatiuni intracomunitare | Testat: pytest
- `F067` | Link de plata pe factura | Testat: pytest
- `F110` | Cron facturi recurente | Testat: de testat P1.4
- `F131` | Notificari de plata si alerte neplatnici | Testat: pytest (18) + functional
- `F153` | Cont de facturare gratuita | Testat: test date reale + vizual + test izolare
- `F154` | Proforme si avize in contul gratuit | Testat: cod: ruta cere_context + UI la gratuit; click-through gratuit recomandat
- `F155` | Facturi recurente in contul gratuit | Testat: cod: gate-fix 4 rute; click-through gratuit recomandat
- `F156` | Import WooCommerce in contul gratuit | Testat: node --check + verificator 0; click-through gratuit recomandat
- `F158` | Model factura in contul gratuit | Testat: cod: card mereu afisat + ruta cere_context; click-through gratuit recomandat
- `F159` | Link de plata in contul gratuit | Testat: cod: buton negated + ruta cere_context; click-through gratuit recomandat
- `F171` | Export facturi emise catre SAGA | Testat: XML real tenant_002 (F_14399840_1_10.06.2026.xml; net 10000 + TVA 2100 = 12100; structura cap-coada) + verificator 0
- `F186` | Raport coliziuni CUI active (superadmin) | Testat: HTTP + SQL: detectie cu coliziune fabricata in tranzactie ROLLBACK -> 1 rand cu numele cabinetului, 0 randuri ramase (zero mutatie); endpoint 200 superadmin {coliziuni:[]}, 403 non-superadmin; node --check ESM + verificator DS 0

## Contabilitate & note (9)
- `F054` | Editor note contabile | Testat: (gol)
- `F061` | Motor contabil (carte mare + inchidere) | Testat: pytest (bug nota neechilibrata prins la rescriere)
- `F077` | Registru incasari/plati (partida simpla) | Testat: vizual
- `F084` | Import solduri initiale (migrare) | Testat: (gol)
- `F085` | Import solduri parteneri (migrare) | Testat: (gol)
- `F108` | Inregistrare cabinet self-service | Testat: (gol)
- `F118` | Blocare perioade | Testat: (gol)
- `F143` | Centre de cost + bugete (management accounting intern) | Testat: test functional real (CRUD centre, tagare nota, raport realizat/nealocat, buget upsert, varianta buget vs realizat)
- `F185` | Gard coliziune CUI cabinet->gratuit (semnal invers F092) | Testat: Functional REAL cu curatare completa: (A) inregistreaza_cont_gratuit pe CUI-ul lui tenant_002 (sub cabinet 1) -> ok=True, coliziune_cabinet=True, contul SE CREEAZA (nu blocat); curatat (DROP SCHEMA provizionata + delete tenant+user); verificat ca starea revine la tenant_001/002 (schema nou-creata era tenant_003 fresh, nu cea istorica). (B) CUI liber fabricat valid -> coliziune_cabinet=False. (C) CUI cu cont gratuit existent -> comportament neschimbat (CUI_EXISTA). py_compile + node --check ESM login.js.

## Operatiuni contabile speciale (14)
- `F009` | Avansuri furnizori/clienti | Testat: pytest
- `F010` | Bacsis HoReCa | Testat: pytest
- `F039` | Decontari asociati | Testat: pytest
- `F040` | Deconturi deplasare si diurna | Testat: pytest
- `F056` | Leasing financiar si operational | Testat: pytest
- `F057` | Lichidare/radiere societate | Testat: pytest
- `F059` | Import mijloace fixe (migrare) | Testat: (gol)
- `F064` | Contabilitate ONG | Testat: pytest
- `F066` | Perisabilitati si scazaminte | Testat: pytest
- `F069` | Productie in curs si produse finite | Testat: pytest
- `F074` | Reevaluare imobilizari | Testat: pytest
- `F082` | SGR (garantie-returnare) | Testat: pytest
- `F086` | Sponsorizari si credit fiscal | Testat: pytest
- `F090` | Subventii | Testat: pytest

## Control fiscal (8)
- `F022` | Semafor conformare fiscala | Testat: core/test_control_fiscal.py (teste) + control_incrucisat 23 + functional real tenant_002 (D205 pe fapt 457, motiv pe fiecare linie, 0 fara motiv)
- `F081` | Calculul scadentelor | Testat: (gol)
- `F094` | Educatie pe tipare de erori | Testat: vizual
- `F100` | Vector fiscal per firma | Testat: vizual
- `F101` | Verificatoare de coerenta | Testat: pytest
- `F120` | Educatie AI pe tipare (varianta generativa) | Testat: apel real Claude verificat (analiza structurata romana + grounding pe date reale CUI/CAS) + fallback fara date/fara cheie; verificator DS 0 nou
- `F164` | Push in-app findinguri rosii control fiscal (pull->push) | Testat: pytest 9 teste dedup PURE (rosu nou notifica; persistent NU re-notifica; verificator nou pe firma deja alertata notifica; rezolvat se sterge din jurnal fara notificare; rezolvat-apoi-reaparut notifica din nou; gri/verde zero push; doua rulari aceeasi zi o singura alerta; text agregat singular/plural) + functional REAL tenant_002 iunie 2026 cu curatare (validator temporar): rulare1 livreaza 1 notif (D112 rosu real, jurnal={d112}); rulare2 aceeasi zi = 0 notif nou (DEDUP); rezolvat->reaparut = a 2-a notif; gri 2025/01 = 0 push; text+link corecte ('DANTE...: 1 control fiscal in rosu (D112)', control-fiscal:2). Tabel creat prin superuser (owner iconta_user, ca notificari - PG15+ revoca CREATE public de la app). 43/43 fara regresie. ROUTING click (gard #4, test real nu doar node --check): 7/7 parsare link in node (control-fiscal:2->tid=2; malformat ':'/':abc'->fallback fara crash; 'validat'->acasa intact; solicitari/null->neatinse) + curl HTTP real cu token cabinet (user 34): /control-fiscal contine firma tid=2 (randeazaControl o gaseste), /control-fiscal/2 (ruta deschisa de click) intoarce firma CORECTA (DANTE, rosu, d112 rosu). node --check ESM ambele fisiere + verificator DS 0 + apelantii existenti (cabinet.js/asistent.js, 2 args) intacti.
- `F183` | Audit de preluare firma | Testat: 11 teste unitare pe nucleele PURE (constatare_parteneri/istoric_fiscal/rip + orchestrator fara-documente->gri) + functional REAL pe tenant_002 (rosu: defalcare parteneri 401/4111 divergenta fata de balanta, gri istoric neimportat) + ruta 401 fara auth (inregistrata); node --check ESM control.js + py_compile + verificator DS 0; restart activ. RAFINAT 22.07: audit() ramifica pe REGIM (tip_firma via migrare_api.straturi_pentru, sursa unica) - PFA (partida simpla) ruleaza DOAR verificarea RIP, verificarile de partida dubla (balanta/parteneri/istoric) NU apar (un gri 'importa balanta' ar fi remediu imposibil la partida simpla); SRL neschimbat. 12 teste (test_pfa_ruleaza_doar_rip + non-regresie); E2E rollback tenant_002 (tip_firma='pfa' -> doar RIP). Vezi DECIZII 22.07

## Portal client (8)
- `F016` | Forecast cash-flow 8 saptamani | Testat: pytest
- `F042` | Documente pentru portal | Testat: (gol)
- `F055` | KPI client (portal) | Testat: pytest
- `F065` | Povestea lunii (pachet lunar) | Testat: vizual
- `F068` | API portal (read-only, izolat) | Testat: privacy-bug reparat 10.07
- `F072` | Canal de sesizari (Raporteaza) | Testat: vizual
- `F113` | PWA (aplicatie instalabila) | Testat: —
- `F197` | Previzualizare portal client din cabinet (Acces Client) | Testat: E2E autentificat: cabinet emite token preview (HTTP 200, preview=True), GET /portal/firme 200, POST mutatie 403 (middleware read-only), firma fara client 400; node-check 6 fisiere JS + verificator DS 0 nou | FIX 21.07 (bug scriere in preview): guard reprodus (POST /portal/solicitari preview 403, client real 200 - backend corect); cauza = token preview in-memory fragil -> mutat pe cheie sessionStorage iconta_pv_token (per-tab, precedenta absoluta, determinist); banner .caseta-info -> .caseta-atentie (vizibil).

## Migrare & import (6)
- `F007` | Import asociati (migrare) | Testat: (gol)
- `F049` | Import/export extracomunitar | Testat: pytest
- `F058` | Starea migrarii pe straturi | Testat: vizual (9 straturi)
- `F189` | Regim firma SRL/PFA (carduri + straturi migrare filtrate) | Testat: functional (provision PFA+SRL + rollback pe prod)
- `F190` | Import RIP la preluarea unui PFA | Testat: functional (2 valide+1 respins, reimport idempotent, rollback pe prod)
- `F191` | Meniu migrare filtrat pe regim firmă (SRL/PFA) | Testat: functional (straturi_pentru pfa/srl + filtrare pași)

## AI & asistenta (1)
- `F001` | Client AI (Claude) | Testat: (gol)

## Autentificare & sesiuni (4)
- `F008` | Autentificare si sesiuni | Testat: (gol)
- `F105` | Sesiune per-tab | Testat: reparat+verificat 12.07
- `F107` | Magic-link (login fara parola) | Testat: (gol)
- `F188` | Pre-completare date firma din ANAF v9 la onboarding | Testat: Functional REAL: (a) stocare pe tenant_002 cu date ANAF reale (14399840) - blank->UPDATE->verify->RESTORE non-distructiv: caen=4754, reg_com=J2002000372404, adresa=MUNICIPIUL BUCURESTI... populate; (b) degradare gratioasa: /public/verifica-cui/99 -> {gasit:False} HTTP 200 (nu 500), formular intact; (c) non-suprascriere (node, gardul): camp gol->completeaza, user tastat manual->NU se pierde, re-verificare->update. Parser: valideaza_cui(14399840) intoarce nr_reg_com+tva_la_incasare noi + cod_caen REPARAT. py_compile + node --check ESM ambele formulare + verificator DS 0 + restart HTTP activ.

## Notificari (3)
- `F062` | Notificari pe evenimente | Testat: (gol)
- `F093` | Scadente viitoare pe portofoliu | Testat: vizual
- `F115` | Notificari in-app + email | Testat: (gol)

## Integrari (Woo/recurente) (2)
- `F102` | Conector WooCommerce | Testat: pytest; de testat P1.5
- `F111` | Cron WooCommerce | Testat: pytest; de testat P1.5

## Administrare cabinet & useri (7)
- `F005` | Chei API publice per cabinet | Testat: pytest
- `F006` | Management actori de cabinet | Testat: vizual
- `F014` | Panou Capacitate | Testat: vizual
- `F103` | Alerte legislative programate | Testat: test date reale + vizual
- `F109` | Suspendare cabinet | Testat: (gol)
- `F117` | Alerte sanatate server | Testat: vizual partial
- `F152` | Triaj AI al sesizarilor | Testat: test date reale + vizual

## Firme & parteneri (3)
- `F092` | Provisioning tenant (schema per firma) | Testat: bug template gol reparat 10.07; coliziune_gratuit_v1 testat real 18.07 (detectie pozitiva pe rand gratuit temporar cu prefix RO in tranzactie rollback; non-match si CUI inexistent -> None)
- `F119` | Provisioning tenant | Testat: bug template gol reparat 10.07
- `F182` | Cont venit implicit setabil din UI | Testat: HTTP end-to-end tenant_002: set 704 persista (GET), invalid 999 -> 422 mesaj clar, emiterea citeste 704 (query exact main.py:5853), restore 707; node --check ESM + verificator DS 0

## Rapoarte & documente comerciale (4)
- `F144` | Rapoarte comerciale | Testat: functional real tenant_002 (Widget X: venit 100 - cost 60 = profit 40)
- `F145` | Rapoarte configurabile salvabile | Testat: —
- `F146` | Registratura documente | Testat: functional real tenant_002 (serie 1-2-3, resetare pe an, validari, ROLLBACK)
- `F147` | Generare contracte | Testat: functional real tenant_002 (marcaj orfan respins, dup, substitutie, PDF %PDF-, ROLLBACK)

## Infrastructura & sistem (9)
- `F060` | Monitor fiscal (noutati legislative) | Testat: pytest + test date reale
- `F083` | Sinteza zilnica pe email | Testat: vizual
- `F104` | Navigator ferestre cu traseu | Testat: vizual
- `F106` | Design System + verificator | Testat: rulat la fiecare tema
- `F112` | Cron monitor fiscal | Testat: pytest
- `F116` | Securitate perimetru | Testat: (gol)
- `F124` | Testare pilot P1-P5 | Testat: —
- `F165` | Auditor conformitate schema tenant vs template | Testat: 11 teste (9 pure compara/sugereaza_alter/normalizare nextval + poarta reala 'toti tenantii conform' + mutatie negativa din ref real) + DOVADA E2E: DROP link_plata REAL pe tenant_002 in tranzactie ROLLBACK -> drift HARD detectat + SQL sugerat corect + tenant neatins. CLI: 0/2 drift HARD (2 tabele extra lazy/legacy = info adnotat). Drift curent verificat = ZERO. Suita 460 verde + verificator DS 0
- `F170` | Backup automat + restaurare baza de date | Testat: real 18.07: LOCAL+OFF-SITE OK (dump confirmat pe Storage Box, 290870 octeti); fail-safe testat (cheie stricata -> LOCAL reuseste, counter 2, email Brevo trimis, restaurare cheie -> counter 0); RESTAURARE DIN OFF-SITE testata cap-coada 18.07 (descarcat ultimul dump prin sftp -> pg_restore in baza de test -> scheme identice cu iconta_v2 (public+tenant_001+tenant_002), tenants 2=2, tenant_002.facturi=5 -> dropdb; baza vie neatinsa)

## Altele / transversal (2)
- `F071` | Provizioane si ajustari | Testat: pytest
- `F114` | API public v1 | Testat: pytest
