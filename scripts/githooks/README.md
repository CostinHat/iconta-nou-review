# Git hooks iConta (poarta mecanica)

`.git/hooks` NU intra in git, deci hook-urile traiesc aici (versionat). **Instalare, o singura data per clona:**

    git config core.hooksPath scripts/githooks

## Locul porții (15.10.2026, comanda Costin, verbatim în DECIZII „Poarta o dată pe lot”; supersedează ordinea din 08.10)

„Poarta completă: o singură dată pe lot, la închiderea lotului, înainte de publicarea pe producție. [...] main acceptă un commit doar
dacă jurnalul porții îl arată verde.”

1. `pre-commit` — `ruff` (nume nedefinite) + refuzul commitului direct pe `main`. Secunde.
2. `commit-msg` -> `verifica-mesaj` — fișierele noi numite, defectul cu loc, `# diff-citit:`, curățenia declarată, octeții de control.
   **Atât.** Commitul nu mai rulează suita.
3. **Închiderea lotului:** `sh scripts/poarta_lot.sh` (arbore curat, pe ramura lotului) -> `poarta-suita` (prospețimea, pytest pe
   `POARTA_PROCESE` procese, verificatorul, cifrele F1–F5, plasa e2e) -> verdictul `VERDE|ROSU <sha> <ramura> <data>` în
   `<git-common-dir>/poarta_verdicte.log`. Refuză: `main`, arbore murdar, SHA deja VERDE, un SHA deja ROȘU (regula 3d, comanda 11.2: pe roșu se repară codul — commit nou — și se rulează din nou, până la verde).
4. **Publicarea:** `reference-transaction` mută `main` numai la un SHA cu aprobarea scrisă (`APROBARE_MAIN`) **și** `VERDE <sha>`.

Între comenzi: `scripts/poarta_scurta.py` (rularea țintită; incert -> suita întreagă, nu poarta).
Gărzi: `core/test_poarta_ordine.py`, `core/test_poarta_lot.py`, `core/test_garda_main.py`.

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
Publica automat pe origin/main SI pe backup/lant-<data> dupa mutarea lui `main` (din 15.10: numai la un SHA cu poarta VERDE a lotului).
Fast-forward, NICIODATA `--force`. Daca origin/main a avansat sub tine -> se opreste si cere `pull --rebase`.
Esec de publicare -> banner + sentinela (`.git/PUSH_MAIN_ESUAT`, `.git/PUSH_BACKUP_ESUAT`; vizibil, nu tacut).
Backup: fast-forward, FARA --force, creeaza ramura zilei daca nu exista. Cableaza CLAUDE.md §2.3 pct.8.
