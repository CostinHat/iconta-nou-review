Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
Ajutor contextual: batch 6 (f764347) si batch 7 sunt JS-only (static, servit de pe disc, fara restart).
Ultimul commit CSV/runtime = d5d87af (batch 5). Four-way ancorat acolo: HEAD = origin/main = backup/lant-2026-08-11 (=f764347 dupa b6);
RUNNING (start 11.08 18:31:04) > d5d87af (18:25:02) -> serveste CSV proaspat (/ajutor/F061 din b5 -> 200). App pe 127.0.0.1:8010. Ramura backup: backup/lant-2026-08-11.

## (b) Fronturi deschise
0. **CAMPANIE "AJUTOR CONTEXTUAL" (Costin, 11.08) — COMPLETA.** Coloana noua `ajutor` in FUNCTIONALITATI.csv (a 11-a),
   text pentru contabil in 7 sectiuni, separata de descrierea tehnica. Semn "?" atasat la functionalitatile cu
   continut non-evident (regula fiscala / preconditie / consecinta). BILANT: 47 ajutoare scrise; 44 functionalitati
   cu "?" (20 statice + 24 dinamice: 10 declaratii + 14 operatiuni speciale). NEplast intentionat: F014 Capacitate
   (management fara continut fiscal, auto-explicativ) + CRUD evident + infra fara UI. Infra: core/ajutor.py (cache),
   GET /ajutor/{fid}, semnAjutor()+modal, .ajutor-btn (DS+verificator). RAPORT UNIC §2.2 livrat 11.08.
1-N. **Fronturi mostenite**: certificare-comportament (import class reparat 38dbb06, harness browser-DS partial);
   Decizii §6 executate (0304128: refactor .camp-input + gard INPUT_NECONFORM extins createElement 29d29aa);
   F116 headere securitate DEPLOYATE (64e8b1b, ramas optional HSTS lung); D406 PARTIAL (F035-037, scope Costin);
   test-debt import (proba pozitiva pe fisier bun -> N randuri, per functionalitate).

## (c) Ce e in lucru acum
Nimic in lucru. Campania ajutor contextual inchisa cu raport unic.

## (d) Ce urmeaza
1. La cererea lui Costin: extindere ajutor (F133 tichete / F136-deja / restul stocurilor detaliat) daca vrea mai mult.
2. Fronturi mostenite (mai sus) daca le redeschide Costin.

## Unelte
- Ajutor contextual: core/ajutor.py (pentru(fid)/cu_ajutor()); GET /ajutor/{fid}; semnAjutor(fid) in api.js;
  IMPORTANT: modificarea TEXTULUI ajutor (CSV) cere restart (cache); plasarea "?" (JS) nu.
- DUK declaratii: PYTHONPATH=$PWD frontend_test/valideaza_duk.py. Registru: 5 garduri in core/test_registru_*.
- Browser-DS: frontend_test/cert_ds_browser.py (login sessionStorage token; NU in poarta verde). Creds
  ~/.iconta/fe_test.env (cabinet 4163; tenants 8396 ALFA/8397 BETA/8398 GAMA/8399 DELTA).
- Poarta verde: commit ruleaza pytest suita (~6min) + verificator (0); post-commit publica origin/main +
  backup/lant-<data>; apoi restart iconta-nou daca s-a schimbat runtime/CSV (four-way).
