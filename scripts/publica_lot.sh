#!/bin/sh
# publica_lot.sh — SINGURA cale de publicare (comanda 16.1, pct.4). Din worktree-ul lotului, pe ramura lui, după rularea completă finală VERDE:
#   1. începutul fazei „publicare” în jurnal; 2. ZIP + verificări + verdictul PASS/STOP (scripts/publica_lot.py); 3. fast-forward pe `main` din ~/iconta_nou
#   (hook-ul reference-transaction cere VERDE și PASS) + post-commit (push pe origin/public/backup, restart, four-way); 4. sfârșitul fazei „publicare”, după push.
# Pe STOP: nu mută nimic, scrie „OPRIT — gata: <lot> nepublicat, <motiv>”. Backup-ul bazei de producție și migrările rămân ale operatorului (CLAUDE.md §6).
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
PY=./venv/bin/python; [ -x "$PY" ] || PY=python3
LOT=$("$PY" scripts/jurnal_lot.py lot-curent)
SHA=$(git rev-parse HEAD)
RAM=$(git symbolic-ref --short HEAD)
[ "$RAM" = "main" ] && { echo "[publica_lot] REFUZ: se publică de pe ramura lotului."; exit 1; }
[ -n "$(git status --porcelain --untracked-files=normal)" ] && { echo "[publica_lot] REFUZ: arbore murdar."; exit 1; }
ID=$("$PY" scripts/jurnal_lot.py inceput "$LOT" publicare "script_sha256=$(sha256sum "$0" | cut -c1-16)")
"$PY" scripts/publica_lot.py || { "$PY" scripts/jurnal_lot.py sfarsit "$LOT" publicare "$ID" stop; exit 1; }
PRINCIPAL=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
(cd "$PRINCIPAL" && git merge --ff-only "$RAM" && sh scripts/githooks/post-commit) || { "$PY" scripts/jurnal_lot.py sfarsit "$LOT" publicare "$ID" esec_publicare; echo "[publica_lot] publicarea a eșuat după PASS."; exit 1; }
if [ "$(git -C "$PRINCIPAL" rev-parse HEAD)" = "$SHA" ] && [ "$(git -C "$PRINCIPAL" rev-parse origin/main)" = "$SHA" ]; then R=publicat; else R=incomplet; fi
"$PY" scripts/jurnal_lot.py sfarsit "$LOT" publicare "$ID" "$R"
echo "[publica_lot] $R $SHA"
[ "$R" = publicat ]
