# Git hooks iConta (poarta mecanica)

`.git/hooks` NU intra in git, deci hook-urile traiesc aici (versionat). **Instalare, o singura data per clona:**

    git config core.hooksPath scripts/githooks

## pre-commit

Ruleaza la FIECARE commit **suita intreaga** (`pytest`) + `verificator_conformitate.py`, MEREU,
fara argumente si fara subset. Respinge commit-ul daca:
- `pytest` nu iese cu 0 (suita rosie), sau
- verificatorul nu da `TOTAL: 0`.

### De ce

Pe 31.07.2026 un `pytest && git commit` a lasat sa treaca un commit ROSU pentru ca `pytest`
rulase pe un SUBSET (doar `core/`, ratand un test la radacina). O poarta care depinde de ce
comanda tastezi nu e poarta - hook-ul ruleaza mereu tot.

### Durata

~32s per commit (suita intreaga). Deliberat: un commit rosu pe o aplicatie fiscala costa mai
mult decat 32s. Daca devine o frana reala, se discuta - dar NU e optional din start.

## post-commit (cablat 07.08.2026)
Publica automat pe origin/main SI pe backup/lant-<data> dupa fiecare commit pe `main` (pre-commit a trecut deja poarta verde).
Fast-forward, NICIODATA `--force`. Daca origin/main a avansat sub tine -> se opreste si cere `pull --rebase`.
Esec de publicare -> banner + sentinela (`.git/PUSH_MAIN_ESUAT`, `.git/PUSH_BACKUP_ESUAT`; vizibil, nu tacut).
Backup: fast-forward, FARA --force, creeaza ramura zilei daca nu exista. Cableaza CLAUDE.md §2.3 pct.8.
