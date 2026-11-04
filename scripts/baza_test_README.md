# baza_test.sh — snapshotul bazei de TEST `iconta_test` (comanda 16.0)

Comenzi: `salveaza` (pg_dump -Fc), `restaureaza`, `stare` (amprenta), `verifica` (precondițiile F017). Conexiunea vine numai din `~/.iconta/test.env`
(rolul de test nu are CONNECT pe producție). **Refuz mecanic:** numele bazei se citește din conexiune (`SELECT current_database()`); orice nume diferit de
`iconta_test` = refuz (încercare cu ținta producției: `REFUZ: baza conexiunii este 'iconta_v2'`). Serverul 8019 (`scripts/e2e_poarta.py`) refuză la fel să pornească.

## Ce intră în snapshot
- **Scheme:** `public` (tabelele comune: toate cele din `iconta_test`, vezi mai jos) și schemele de firmă din `iconta_test`: copiile firmelor cabinetului de test
  `tenant_9049`…`tenant_9055`, `tenant_9057` (F1–F7, FISCALOS; făcute cu `scripts/dovada_firme_test.py --cloneaza`, care citește din producție numai schemele cabinetului
  „Cabinet Test Sesiunea B SRL” și refuză orice altă schemă) și schemele create de suita pytest (`tenant_001`…`tenant_018`, `tenant_045`, `tenant_048`, `tenant_9731`).
- **Exclus explicit:** schema cabinetului real și a firmelor lui (CLAUDE.md §7) — nu există în `iconta_test` și nu se copiază; nicio dată a cabinetului real nu intră în snapshot.
  Producția nu e atinsă de nicio comandă a scriptului (nici de teste, nici de verificator).
- **Valorile secvențelor:** în dump (setval); amprenta `stare` le include (hash pe `pg_sequences`).
- **Ceasul înghețat:** `core.ceas_proba.DATA_REF` = 03.11.2026 (11/2026) face parte din snapshot: o altă dată cere snapshot nou.
- **Directoare:** toate fișierele serverului de lucru stau sub `E2E_TEMP` (implicit `/tmp/e2e_poarta`: `fisiere`, `bonuri`, `cutie_email`, `ai_simulat`, `anaf_simulat`,
  `whatsapp_simulat`) — GENERATE, nu fixture: `restaureaza` le șterge întregi (e2e_poarta le recreează la pornire). Fixture-uri păstrate pe disc: niciunul (răspunsurile
  simulate le pun testele). Directoarele producției (`~/iconta_date/...`) nu se ating.
- **Cozi golite la restaurare:** `public.declaratii_coada`, `declaratii_in_asteptare`, `inregistrari_in_asteptare`, `login_esecuri`, `reset_parola_token`, `tokene_activare`, `telefon_coduri`.
  Sesiunile: aplicația nu are tabel de sesiuni (nu se păstrează nimic). Cache-ul aplicației: în proces, dispare la repornirea serverului.
- **Excluse din amprentă:** `cron_batai`, `metrici_sanatate` (se schimbă singure la fiecare tură).
- **Integrările externe** pe `iconta_test`: nu există chei de trimitere în mediul de probă (`e2e_poarta._env_test` scoate Brevo/Postmark/WhatsApp); ANAF = `ICONTA_ANAF_SIMULAT`,
  AI = `ICONTA_AI_SIMULAT`, WhatsApp = `ICONTA_WHATSAPP_SIMULAT`, emailul = `ICONTA_EMAIL_CUTIE` (fișiere în `E2E_TEMP`); BNR din `public.curs_bnr_zilnic` (copiat în snapshot);
  SPV: neactivat (F126/F176/F179 în afara plasei).

## Restaurarea
`pg_terminate_backend` pe toate conexiunile la `iconta_test` → `pg_restore --clean --if-exists` → ștergerea `E2E_TEMP` → golirea cozilor → lucrătorul de recalculare
(`python -m core.firma_rezumat`, sincron, pornit numai de script; rezumatele firmelor, 723) ca Termene și Control fiscal să fie la zi. Niciun proces de fundal nu atinge
`iconta_test` în afara scriptului. Serverul 8019 pornit în timpul restaurării: conexiunile lui sunt terminate; își reface pool-ul la prima cerere (sau se repornește:
`verificator_design.py porneste`); după fiecare restaurare plasa și verificatorul pornesc oricum un server nou (browser nou).
`public.cod_aplicatie_viu`: snapshotul îl are GOL (făcut înainte de orice pornire a serverului); lucrătorul sincron al restaurării calculează atunci cu codul de pe disc (723 refuză
numai când un cod viu diferit e înregistrat). Serverul de lucru își scrie codul la pornire (`inregistreaza_cod_viu`); o restaurare golește iar rândul, deci după restaurare nu rămâne
niciun „serviciul rulează X” al unei versiuni vechi și nu apare „în recalculare” fals.
Durata: ~80 s (peste ținta de 2 minute nu e).

## Dovada de identitate
`stare` = hash pe fiecare tabel (count + md5 al rândurilor sortate, independent de ordinea fizică) + hash pe valorile secvențelor + hash pe inventarul fișierelor generate.
Identitatea snapshotului: `docs/dovezi/16_0/snapshot.json`.
