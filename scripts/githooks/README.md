# Git hooks iConta (poarta mecanica)

`.git/hooks` NU intra in git, deci hook-urile traiesc aici (versionat). **Instalare, o singura data per clona:**

    git config core.hooksPath scripts/githooks

## Ordinea (08.10.2026, decizia Costin pct.3: „Verificarea commit-msg rulează înaintea pytest, nu după.”)

1. `pre-commit` — `ruff` (nume nedefinite). Rapid.
2. `commit-msg` -> `verifica-mesaj` — fisierele noi numite, defectul cu loc, fisierele normative citite (`# diff-citit:`),
   curatenia declarata, octetii de control. Un mesaj respins costa secunde, nu o rulare de suita.
3. `commit-msg` -> `poarta-suita` — **suita intreaga** (`pytest`) + `verificator_conformitate.py`, MEREU, fara argumente si
   fara subset (sarita numai la un commit de curatenie, decis de `scripts/curatenie.py` din index). Respinge commit-ul daca:
   - `pytest` nu iese cu 0 (suita rosie), sau
   - verificatorul nu da `TOTAL: 0`.

Gard: `core/test_poarta_ordine.py`. Pana pe 08.10 suita statea in `pre-commit`, inaintea mesajului: un mesaj fara
`# diff-citit:` arunca o rulare verde de ~55 de minute (06.10, 08.10).

### De ce

Pe 31.07.2026 un `pytest && git commit` a lasat sa treaca un commit ROSU pentru ca `pytest`
rulase pe un SUBSET (doar `core/`, ratand un test la radacina). O poarta care depinde de ce
comanda tastezi nu e poarta - hook-ul ruleaza mereu tot.

### Durata

~55 de minute per commit (suita intreaga; 08.10.2026: 3286 s pe 7.637 de teste). Deliberat: un commit rosu pe o aplicatie
fiscala costa mai mult. Cifra vie e in `poarta-suita` si in `.poarta_jurnal.log`.

## Verdictul privește commitul — arborele = indexul (15.10.2026)

pytest și verificatorul citesc ARBORELE DE LUCRU, commitul înregistrează INDEXUL. `poarta-suita` respinge deci, la pornire, orice
modificare nepusă la index și orice fișier nou neadăugat (`git diff --name-only` + `git ls-files --others --exclude-standard`), iar
la sfârșit, înaintea verdictului, orice fișier urmărit schimbat cât a rulat poarta. Prins după lotul 1: `fdb20bd6` a trecut poarta
verde, iar exportul lui pica 9 gărzi. Consecință practică: **cât rulează poarta (~70 de minute) nu se editează arborele** — lucrul
în paralel se face în altă copie. Gard: `core/test_poarta_ordine.py::test_arborele_diferit_de_index_e_respins_inainte_de_suita`.

## Garda pe `main` — `reference-transaction` + `pre-commit` (15.10.2026, regim pilot)
Comanda Costin 14.10.2026, pct.2: „Garda pe main în ~/iconta_nou (commit refuzat fără aprobare scrisă): da.” (verbatim în DECIZII).
`main` din `~/iconta_nou` e versiunea publicată. **Orice mutare a lui `refs/heads/main`** (commit, fast-forward, reset, pull, ștergere)
e refuzată de `reference-transaction` dacă `<git-common-dir>/APROBARE_MAIN` nu are `sha: <SHA-ul țintă, complet>` și
`aprobat: <textul aprobării lui Costin>`; la reușită aprobarea se consumă (`APROBARE_MAIN.folosita-<sha>`). Un commit DIRECT pe `main`
e refuzat din prima secundă de `pre-commit` (SHA-ul lui nu poate fi aprobat dinainte). Lucrul: pe o ramură, în worktree
(`/home/costin/iconta_lucru`). Publicarea: aprobarea scrisă -> `git merge --ff-only <ramura>` în `~/iconta_nou` (un fast-forward NU
rulează `post-commit`) -> `sh scripts/githooks/post-commit` -> migrările cerute (`core.migrari_registru ruleaza --productie`) ->
four-way. Gard: `core/test_garda_main.py`.

## post-commit (cablat 07.08.2026)
Publica automat pe origin/main SI pe backup/lant-<data> dupa fiecare commit pe `main` (commit-msg a trecut deja poarta verde).
Fast-forward, NICIODATA `--force`. Daca origin/main a avansat sub tine -> se opreste si cere `pull --rebase`.
Esec de publicare -> banner + sentinela (`.git/PUSH_MAIN_ESUAT`, `.git/PUSH_BACKUP_ESUAT`; vizibil, nu tacut).
Backup: fast-forward, FARA --force, creeaza ramura zilei daca nu exista. Cableaza CLAUDE.md §2.3 pct.8.
