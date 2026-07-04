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
