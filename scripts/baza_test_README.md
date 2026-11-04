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

## Tabelele comune (schema `public`) — lista exactă
Criteriul: toate tabelele din `public` pe care codul aplicației le citește pentru cabinetul de test (utilizatori, registrul cabinetelor și firmelor, notificări, cozi,
`cod_aplicatie_viu`, rezumate). Lista a fost găsită prin căutare în cod (`FROM|JOIN|INTO|UPDATE|TABLE|EXISTS public.<tabel>`); în dreapta, fișierele cu cele mai multe referiri.
Tabele **recalculate** (excluse din amprentă; le rescrie lucrătorul de recalculare sau pornirea serverului): `firma_rezumat`, `firma_aspect_sursa`, `firma_sursa_versiune`,
`supervizor_rezultat`, `supervizor_sursa`, `sursa_supervizor`, `cod_aplicatie_viu`, `cron_batai`, `metrici_sanatate`.

| tabel | fișiere |
|---|---|
| `accounting_firms` | `core/migrare_intocmitor_bilant.py`, `core/auth_api.py` |
| `acord_termeni` | `core/repo_utilizatori.py` |
| `alerte_acces_dedup` | `core/alerta_acces.py` |
| `alerte_control_emise` | `core/migrare_alerte_control_emise.py`, `core/alerte_control_fiscal.py` |
| `alerte_cooldown` | `core/stare_partajata.py` |
| `alerte_emise` | `core/repo_monitor_fiscal.py` |
| `alerte_fiscale` | `core/repo_monitor_fiscal.py`, `core/migrare_anunturi_trimiteri.py` |
| `anunturi_cabinet` | `core/migrare_anunturi_trimiteri.py`, `core/repo_admin.py` |
| `api_chei` | `core/api_public.py` |
| `audit_log` | `core/repo_admin.py`, `core/tenant_stergere.py` |
| `cereri_ritm` | `core/stare_partajata.py` |
| `ciorne_formular` | `core/migrare_ciorne_formular.py`, `core/repo_ciorne_formular.py` |
| `cod_aplicatie_viu` | `core/firma_rezumat.py` |
| `cor_ocupatii` | `core/cor_api.py` |
| `cron_batai` | `core/cron.py`, `core/sonda_web.py` |
| `curs_bnr_zilnic` | `core/migrare_curs_precizie.py`, `core/curs_bnr.py` |
| `declaratii_coada` | `core/coada_api.py`, `core/migrare_verdict_validare.py` |
| `declaratii_depuse` | `core/migrare_declaratii_depuse_versiune.py`, `core/coada_api.py` |
| `declaratii_in_asteptare` | `core/migrare_declaratii_asteptare.py`, `core/repo_declaratii.py` |
| `emailuri_dezabonate` | `core/migrare_emailuri_dezabonate.py`, `core/dezabonare.py` |
| `eveniment_public` | `core/migrare_eveniment_public.py`, `core/repo_admin.py` |
| `firma_aspect_sursa` | `core/firma_rezumat.py` |
| `firma_rezumat` | `core/firma_rezumat.py` |
| `firma_sursa_versiune` | `core/firma_rezumat.py` |
| `firma_tip` | `core/firma_rezumat.py`, `core/auth_api.py` |
| `firme_scoase` | `core/migrare_firme_scoase.py`, `core/tenant_stergere.py` |
| `fisiere_private` | `core/migrare_fisiere_private.py`, `core/gdpr_sterge.py` |
| `gdpr_cereri_stergere` | `core/gdpr_cerere.py` |
| `gdpr_stergeri` | `core/gdpr_sterge.py` |
| `inregistrari_in_asteptare` | `core/inregistrare_libera.py`, `core/migrare_inregistrari_email.py` |
| `instante` | `core/instante.py` |
| `instante_lider` | `core/instante.py` |
| `invitatii_cabinet` | `core/invitatii.py`, `core/migrare_invitatii_cabinet.py` |
| `invitatii_cont` | — (neatins de cod în afara migrărilor) |
| `login_esecuri` | `core/stare_partajata.py` |
| `metrici_sanatate` | `core/migrare_sanatate_load15.py`, `core/repo_main.py` |
| `migrare_status` | `core/migrare_api.py` |
| `migrari_rulate` | `core/migrari_registru.py`, `core/migrare_notificari_solicitare_client.py` |
| `notificari` | `core/migrare_canal_notificari.py`, `core/migrare_decizii_0810.py` |
| `notificari_jurnal` | `core/migrare_canal_notificari.py`, `core/repo_notificari_livrare.py` |
| `pachet_povestea` | `core/pachete_api.py`, `core/migrare_poveste_amprenta.py` |
| `plata_referinte` | `core/migrare_plata_referinte.py`, `core/plati.py` |
| `raportari` | `core/raportari_api.py`, `core/migrare_fisiere_private.py` |
| `raportari_mesaje` | `core/raportari_api.py`, `core/migrare_fisiere_private.py` |
| `reges_chei` | `core/repo_salariati.py` |
| `reges_mesaje` | `core/repo_salariati.py` |
| `reset_parola_token` | `core/migrare_reset_parola.py`, `core/reset_parola.py` |
| `schimbari_email` | `core/migrare_portal.py`, `core/repo_utilizatori.py` |
| `setari_platforma` | `core/setari_platforma.py`, `core/migrare_inregistrare_libera.py` |
| `solicitari_client` | `core/repo_portal.py` |
| `sonda_izolare` | — (neatins de cod în afara migrărilor) |
| `spv_cui_acoperit` | `core/migrare_mesaje_spv_tehnice.py`, `core/migrare_spv_citiri.py` |
| `spv_token` | `core/migrare_spv_token_principal.py`, `core/spv_conector.py` |
| `supervizor_confirmari` | `core/migrare_supervizor_confirmari.py`, `core/supervizor.py` |
| `supervizor_rezultat` | `core/supervizor_cache.py` |
| `supervizor_sursa` | `core/supervizor_cache.py`, `core/firma_rezumat.py` |
| `sursa_supervizor` | `core/firma_rezumat.py` |
| `suspendari_cabinet` | `core/migrare_suspendari_cabinet.py`, `core/repo_admin.py` |
| `telefon_coduri` | `core/repo_cont_notificari.py`, `core/migrare_canal_notificari.py` |
| `tenants` | `core/tenant_provisioning.py`, `core/auth_api.py` |
| `tokene_activare` | `core/repo_utilizatori.py`, `core/repo_main.py` |
| `urme_portal` | `core/migrare_portal.py`, `core/repo_utilizatori.py` |
| `user_tenants` | `core/repo_utilizatori.py`, `core/auth_api.py` |
| `users` | `core/migrare_canal_notificari.py`, `core/repo_utilizatori.py` |

## Schemele din `iconta_test` (copiate din producție numai pentru cabinetul de test)
`public`, `tenant_9049`…`tenant_9055`, `tenant_9057` (copiile F1–F7 + FISCALOS), plus schemele create de suita pytest: `tenant_001`…`tenant_018`, `tenant_045`, `tenant_048`, `tenant_9731`.
Nu există nicio schemă a cabinetului real.

## Calea directoarelor (copia de lucru, nu producția)
`E2E_TEMP` = `/tmp/e2e_poarta` (generat de `scripts/e2e_poarta.py`; șters la fiecare restaurare). Serverul de lucru 8019: `scripts/porneste_8019.sh` (mediul `~/.iconta/test.env`).
Punctul de intrare sincron al lucrătorului de recalculare (723): `python -m core.firma_rezumat` (`core/firma_rezumat.py::main`).
Variabila ceasului înghețat: nu există variabilă de mediu — `core.ceas_proba.DATA_REF` (constantă Python, 03.11.2026) o folosesc testele de browser; aplicația citește ceasul real.
Cod de produs care ar permite o dată înghețată în aplicație: **imposibil fără cod de produs** (de notat pentru un lot de produs).
