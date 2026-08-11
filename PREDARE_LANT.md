Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
HEAD = origin/main = backup/lant-2026-08-11 = RUNNING = b0ccc40 (runtime: main.py/auth_api.py schimbate ->
restart efectuat, start 11.08 19:52 > commit 19:46). App pe 127.0.0.1:8010.

## (b) Fronturi deschise
0. **CAMPANIE "AJUTOR DE ANSAMBLU" (Costin, 11.08) — COMPLETA.** Pagina de bun-venit la prima logare (prezentare
   schematica: firul de intrare 9 pasi + 7 grupe + 45 "?" contextuale) o singura data (flag server
   users.bun_venit_vazut_la) + semn "?" GENERAL permanent in bara de stare (.nav-ghid, distinct de .ajutor-btn)
   care redeschide ansamblul. Continut DERIVAT (STRATURI + repartizeaza + coloana ajutor). Backend: /ansamblu,
   /cont/bun-venit-vazut, flag in payload login. RAPORT UNIC §2.2 livrat 11.08. Probat backend + browser.
1-N. **Fronturi mostenite**: ajutor contextual (47 ajutoare, 44 "?", commit f764347/5eb5b35); certificare-comportament
   (import class reparat 38dbb06); Decizii §6 (0304128 + INPUT_NECONFORM createElement 29d29aa); F116 headere
   securitate (64e8b1b, ramas optional HSTS lung); D406 PARTIAL (F035-037); test-debt import (proba pozitiva).

## (c) Ce e in lucru acum
Nimic in lucru. Campania ajutor de ansamblu inchisa cu raport unic.

## (d) Ce urmeaza
1. La cererea lui Costin: rafinari (ex. buton "?" general si pe portalul clientului daca se doreste; screenshot).
2. Fronturi mostenite (mai sus) daca le redeschide Costin.

## Unelte
- Ajutor de ansamblu: core/ajutor.py + genereaza_grupe_functii.repartizeaza (grupe) + STRATURI (migrare.js, firul).
  Migrare coloana: `set -a; . ~/.iconta/db.env; set +a; PYTHONPATH=$PWD venv/bin/python3 -m core.migrare_bun_venit`.
  Reset flag test (welcome reapare): UPDATE public.users SET bun_venit_vazut_la=NULL WHERE email='fir-intrare@prisma-cont.test'.
  Nota: modificarea TEXTULUI ajutor (CSV) cere restart (cache core/ajutor.py); plasarea "?" (JS) nu.
- Browser: creds ~/.iconta/fe_test.env (cabinet 4163; login POST /auth/login -> sessionStorage token+user).
- DUK declaratii: PYTHONPATH=$PWD frontend_test/valideaza_duk.py. Registru: 5 garduri in core/test_registru_*.
- Poarta verde: commit ruleaza pytest (~6min) + verificator (0); post-commit publica origin/main + backup/lant-<data>;
  apoi restart iconta-nou DACA s-a schimbat runtime/CSV (four-way: RUNNING > commit).
