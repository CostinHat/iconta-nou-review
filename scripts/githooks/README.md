# Git hooks iConta (poarta mecanica)

`.git/hooks` NU intra in git, deci hook-urile traiesc aici (versionat). **Instalare, o singura data per clona:**

    git config core.hooksPath scripts/githooks

## Locul porții (15.10.2026, comanda Costin, verbatim în DECIZII „Poarta o dată pe lot”; 23.10.2026, CLAUDE.md §5 și §6, DECIZII „Comanda 12.1”)

CLAUDE.md §5: „La închiderea lotului, poarta completă rulează o singură dată (scripts/poarta_lot.sh). Un test care a trecut deja pe
exact același commit nu se mai rulează a doua oară. Dacă poarta pică: se repară cauza, apoi se rulează testele căzute și tot ce depinde
de reparație. Poarta completă se reia numai dacă reparația a atins piese folosite în mai multe locuri sau dacă perimetrul ei nu e sigur.
Verdictul pentru commitul reparat se compune din rularea completă anterioară plus rerularea țintită.” §6: „După poarta verde, Code
publică imediat, fără să aștepte confirmare”.

1. `pre-commit` — `ruff` (nume nedefinite) + refuzul commitului direct pe `main`. Secunde.
2. `commit-msg` -> `verifica-mesaj` — fișierele noi numite, defectul cu loc, `# diff-citit:`, curățenia declarată, octeții de control.
   **Atât.** Commitul nu rulează suita.
3. **Închiderea lotului — rularea completă:** `sh scripts/poarta_lot.sh` (arbore curat, pe ramura lotului) -> `poarta-suita`:
   prospețimea, pytest pe `POARTA_PROCESE` procese (verificatorul și cifrele F1–F5 rulează cât rulează pytest), apoi plasa e2e (nu peste
   pytest: aceeași bază de test). **Toate părțile rulează și după una roșie** (din 23.10; până atunci poarta se oprea la prima), ca să se
   știe toate testele căzute; poarta iese 1 dacă vreuna e roșie. Refuz imediat rămâne numai arborele ≠ indexul. La final:
   `<git-common-dir>/poarta_rulari/<sha>.json` — per parte `rc`, `durata_s`, `cazute` (nodurile `FAILED`/`ERROR` din pytest și din
   plasă), `cazute_complete` (lista are atâtea rânduri câte căzute numără rezumatul pytest) — și linia `DURATE` în `.poarta_jurnal.log`.
   Verdictul: `VERDE|ROSU <sha> <ramura> <data>` în `<git-common-dir>/poarta_verdicte.log`.
4. **După o rulare completă roșie — poarta compusă:** reparația se comite, apoi `sh scripts/poarta_lot.sh --compus`. X = ultima
   rulare completă ROȘIE de pe ramură; `scripts/poarta_scurta.py --compus=X` rulează nodurile căzute în X + perimetrul reparației
   (`git diff X`, nivelul `integrare`), e2e-ul căzut + cel derivat (`scripts/e2e_poarta.py --doar=…`, din index), prospețimea,
   verificatorul și cifrele F1–F5, fiecare cu durata măsurată. Verdictul: `VERDE|ROSU <sha> <ramura> <data> compus:<X>`. **Refuză**
   (exit 2, niciun verdict — se rulează poarta completă) când compunerea nu e sigură: înregistrarea lui X lipsește / nu e completă /
   are arborele schimbat / are căzute nenumărabile; X nu e strămoș al lui HEAD; diff gol; orice motiv `incerte` al derivării; un
   fișier pe care nu-l numește niciun test; plasa atinsă integral; perimetru gol; o piesă folosită în multe locuri (perimetrul ≥ ½ din
   fișierele de test); un nod căzut al cărui fișier nu mai există.
   Ambele moduri refuză: `main` / HEAD detașat, arbore murdar, un SHA deja VERDE, un SHA deja ROȘU (regula 3d, comanda 11.2: pe roșu
   se repară codul — commit nou — și se rulează din nou, până la verde).
5. **Publicarea:** `reference-transaction` mută `main` numai la un SHA cu `VERDE <sha>` (complet sau compus). Aprobarea scrisă
   `APROBARE_MAIN` (14.10–23.10.2026) e RADIATĂ: după poarta verde publicarea urmează imediat (CLAUDE.md §6).

Între comenzi: `scripts/poarta_scurta.py` (rularea țintită; incert -> suita întreagă, nu poarta); `--fata-de=<commit>` ia atinsele din
diff-ul față de acel commit (tot din git, nu din argumente de fișier).
Gărzi: `core/test_poarta_ordine.py`, `core/test_poarta_lot.py`, `core/test_garda_main.py`, `core/test_poarta_scurta.py`.

### De ce (istoric)

Pe 31.07.2026 un `pytest && git commit` a lăsat să treacă un commit ROȘU pentru că `pytest` rulase pe un SUBSET: de atunci suita
rula la fiecare commit (din 08.10 după mesaj, în `commit-msg`). Din 15.10 poarta e tot mecanică, dar legată de ce publică — mutarea
lui `main` — nu de fiecare commit: un SHA fără verdict VERDE nu ajunge în producție, oricâte commituri are lotul.

### Durata

~71 de minute (lotul 4, 15.10.2026: pytest 3074 s · plasa 1215 s). Cifra vie e în `.poarta_jurnal.log` (`DURATE`).

## Verdictul privește commitul — arborele = indexul (15.10.2026)

pytest și verificatorul citesc ARBORELE DE LUCRU, commitul înregistrează INDEXUL. `poarta-suita` respinge deci, la pornire, orice
modificare nepusă la index și orice fișier nou neadăugat (`git diff --name-only` + `git ls-files --others --exclude-standard`), iar
la sfârșit, înaintea verdictului, orice fișier urmărit schimbat cât a rulat poarta. Prins după lotul 1: `fdb20bd6` a trecut poarta
verde, iar exportul lui pica 9 gărzi. Consecință practică: **cât rulează poarta (~70 de minute) nu se editează arborele** (din 15.10 lansatorul cere oricum arbore curat) — lucrul
în paralel se face în altă copie. Gard: `core/test_poarta_ordine.py::test_arborele_diferit_de_index_e_respins_inainte_de_suita`.

## Garda pe `main` — `reference-transaction` + `pre-commit` (15.10.2026, regim pilot; 23.10.2026, CLAUDE.md §6)
`main` din `~/iconta_nou` e versiunea publicată. **Orice mutare a lui `refs/heads/main`** (commit, fast-forward, reset, pull) e
refuzată de `reference-transaction` dacă `<git-common-dir>/poarta_verdicte.log` nu are `VERDE <SHA-ul țintă> …`; ștergerea lui `main`
e refuzată mereu. (14.10–23.10.2026 se cerea și aprobarea scrisă `APROBARE_MAIN`, consumată la reușită — radiată 23.10.2026: un fișier
rămas nu mai e citit.) Un commit DIRECT pe `main` e refuzat din prima secundă de `pre-commit` (SHA-ul lui nu poate avea verdict
dinainte). Lucrul: pe o ramură, în worktree. Publicarea, imediat după poarta verde: backup al bazei -> `git merge --ff-only <ramura>` în
`~/iconta_nou` (un fast-forward NU rulează `post-commit`) -> `sh scripts/githooks/post-commit` -> migrările cerute
(`core.migrari_registru ruleaza --productie`) -> four-way. Gard: `core/test_garda_main.py`.

## post-commit (cablat 07.08.2026)
Publica automat pe origin/main SI pe backup/lant-<data> dupa mutarea lui `main` (din 15.10: numai la un SHA cu poarta VERDE a lotului — completa sau compusa).
Fast-forward, NICIODATA `--force`. Daca origin/main a avansat sub tine -> se opreste si cere `pull --rebase`.
Esec de publicare -> banner + sentinela (`.git/PUSH_MAIN_ESUAT`, `.git/PUSH_BACKUP_ESUAT`; vizibil, nu tacut).
Backup: fast-forward, FARA --force, creeaza ramura zilei daca nu exista. Cableaza CLAUDE.md §2.3 pct.8.
