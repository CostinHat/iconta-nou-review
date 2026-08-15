Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Stare la 2026-08-15. HEAD = **c8d3947** (D300 remediere: gard de regresie B1-B3).
RUNNING pe **c8d3947** (systemd iconta-nou ExecMainStartTimestamp 2026-08-15 14:18:53 > commit 14:10:57; ActiveState
active). Publicare origin/main + backup/lant-2026-08-15 prin post-commit (ritual neconditionat - restart la fiecare
commit). Poarta verde la fiecare din cele 4 commituri ale campaniei (pre-commit: suita + verificator TOTAL 0).
Proba RUNNING = start-time > commit (citita, nu presupusa). App pe 127.0.0.1:8010. Verificare la predare:
`/admin/versiune` (superadmin) sau `git log -1` + systemd ExecMainStartTimestamp.
NB: actualizarea registrelor (ISTORIC/GARZI/DECIZII/TESTE/FUNCTIONALITATI.csv + acest fisier) e NEcomisa in arborele
de lucru - o comite Costin prin poarta.

## (b) Fronturi deschise
1. **GHID - 19 fisiere .md PARCATE.** In ~/ghid_pending/ (mutate din ghid/ ca sa NU sparga test_ghiduri_servite -
   suita e verde acum, N=N). ASTEAPTA de la Costin blocul cu cele 19 titluri/descrieri VERBATIM ca sa li se puna
   front-matter, apoi: restaurare in ghid/, test_ghiduri_servite (N=N), sitemap, publicare. Doua dintre ele -
   `compensare-datorii-terti` si `ro-e-tva-decont-precompletat` - descriu functionalitati FARA ecran accesibil (de
   nereparat acolo, DOAR de raportat: fara ecran, functionalitatea nu exista - regula permanenta 9).
2. **D300 dependent de ANAF, RAPORTAT SEPARAT, NEreparat in app** (vezi GARZI 15.08):
   - import non-UE (primita non-UE 0%) ramane pe R26 - TVA vamala / deferment de import depinde de raspunsul ANAF;
   - bunuri vs servicii IC - nu exista camp discriminator pe factura -> conventie bunuri-implicit (R1 / R5+R18) +
     avertisment de reclasificare; serviciile (R3 / R7+R20) raman reclasificare MANUALA de contabil.
   Gard care apara comportamentele reparate: core/test_d300_b1_rutare.py (8 teste).
3. **Fronturi mostenite, NEMISCATE** (motivul mai jos, sect. (c)):
   - D406 F035/F036/F037 PARTIAL: F035 = Payments neemis (asteapta sursa maparei); F036 = amortizare doar liniara
     (art.28 degresiva/accelerata neimplementate) + fragment; F037 = fragment (nu in AuditFile lunar). Scope Costin.
   - F116 headere de securitate: HSTS lung ramas optional - decizie INFRA Costin.
   - D101G: schema v2 (OPANAF 206/2025) neinstalata in DecValidation pe server -> test xfail(strict); se probeaza
     cand se instaleaza DecValidation care cunoaste d101g v2.

## (c) Ce e in lucru acum
Nimic in lucru. Campania **D300 remediere completa e INCHISA** (4 commituri: 05ad538 B1 campuri+generator, 5f88f23
B2+B3 rand manual persistat + campuri UI, 569ecbc B4 firma grea tenant_017, c8d3947 gard 8 teste). De ce niciun alt
front nu s-a miscat: lantul a fost dedicat INTEGRAL D300 (audit 8263a4b -> B1-B4 -> gard), o campanie cu raza fixa
ceruta; fronturile mostenite (ghid, D406, F116, D101G) asteapta fiecare o DECIZIE sau un INPUT de la Costin (blocul de
19 titluri pentru ghid; scope pentru D406/F116; instalare DecValidation v2 pentru D101G) - niciunul nu s-a atins in
aceasta tura ca sa nu se amestece raze de decizie.

## (d) Ce urmeaza
La cererea/decizia lui Costin:
1. **Ghid**: livrarea blocului cu cele 19 titluri/descrieri -> front-matter -> restaurare in ghid/ -> test_ghiduri_
   servite (N=N) -> sitemap -> publicare.
2. **D300 ANAF-dependent**: la raspunsul ANAF pe TVA vamala/deferment -> tratarea importului non-UE dincolo de R26;
   optional, un camp bunuri/servicii pe factura ca sa se discrimineze automat IC (azi conventie + avertisment).
3. **Mostenite**: D406 (sursa Payments; amortizare degresiva/accelerata + fragment AuditFile); F116 HSTS; D101G la
   instalarea DecValidation v2.

## Unelte
- D300 remediere: generator core/d300.py; rute rand manual core/d300_manual_api.py; UI static/js/ecrane/declaratii.js
  (randezaManualD300) + emitere_ecran.js/facturi_ecran.js; API core/facturi_api.py. Migrari: core/migrare_d300_b1.py
  (campuri factura + backfill tert_tara din VIES), core/migrare_d300_manual.py (tabel d300_manual). Seed firma grea:
  date_test/seed/firma_grea_audit.py + date_test/seed/transa3_d300_b1.py. Reconciliere a-doua-cale: core/d300_reconciliere.py.
- Playwright D300 (probe reale de ecran): frontend_test/proba_fields_emit_prim.py (campuri emitere/primite),
  frontend_test/proba_primita_checkbox.py (checkbox furnizor la incasare). Capturi: frontend_test/d300_*.png,
  emit_campuri_noi.png, primite_detaliu_*.png. Creds browser: ~/.iconta/fe_test.env (cabinet 4163).
- Migrare coloana pe DB: `set -a; . ~/.iconta/db.env; set +a; PYTHONPATH=$PWD venv/bin/python3 -m core.migrare_d300_b1`.
- Registru: 5 garduri in core/test_registru_*; inventar A + anti-stale in core/test_agenda.py (bifa √ ancorata la
  commitul in care fisierul de test intra in git - comit INTAI fisierul, apoi bifa; redenumire = re-ancorare + bump).
- Poarta verde: commit ruleaza pytest (~6min) + verificator (0); post-commit publica origin/main + backup/lant-<data>;
  apoi restart iconta-nou NECONDITIONAT (cablat in post-commit, gardat de
  core/test_publicare_restart_neconditionat) -> four-way RUNNING==HEAD.
