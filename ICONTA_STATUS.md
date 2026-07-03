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
