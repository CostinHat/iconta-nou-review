#!/bin/sh
# publica_lot.sh — SINGURA cale de publicare (comanda 16.1, pct.4). Din worktree-ul lotului, pe ramura lui, după rularea completă finală VERDE:
#   1. începutul fazei „publicare” în jurnal; 2. ZIP + verificări + verdictul PASS/STOP (scripts/publica_lot.py); 3. fast-forward pe `main` din ~/iconta_nou
#   (hook-ul reference-transaction cere VERDE și PASS) + post-commit (push pe origin/public/backup, restart, four-way); 4. sfârșitul fazei „publicare”, după push.
# Pe STOP: nu mută nimic și cheamă scripts/incheie_lot.sh <lot> nepublicat (fișierul-semnal OPRIT_<lot>.txt). Backup-ul bazei de producție și migrările rămân ale operatorului (CLAUDE.md §6).
# 16.1-C3, pct.7: după push urmează pasul „restart” (scripts/publica_prod.sh: refuză fără PASS pentru HEAD; statica, restartul, four-way) înaintea sfârșitului fazei „publicare”;
# post-commit nu mai repornește nimic. Pct.4: la sfârșit (publicat, STOP sau eșec) scripts/incheie_lot.sh scrie fișierul-semnal pe care îl citește coada.
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
PY=./venv/bin/python; [ -x "$PY" ] || PY=python3
LOT=$("$PY" scripts/jurnal_lot.py lot-curent)
SHA=$(git rev-parse HEAD)
RAM=$(git symbolic-ref --short HEAD)
[ "$RAM" = "main" ] && { echo "[publica_lot] REFUZ: se publică de pe ramura lotului."; exit 1; }
[ -n "$(git status --porcelain --untracked-files=normal)" ] && { echo "[publica_lot] REFUZ: arbore murdar."; exit 1; }
ID=$("$PY" scripts/jurnal_lot.py inceput "$LOT" publicare "script_sha256=$(sha256sum "$0" | cut -c1-16)")
# [17.5-U, U.5] ieșirea lui publica_lot.py într-un fișier temporar (sh e dash: fără pipefail și fără PIPESTATUS, deci fără tee): codul se citește din $? imediat după, fișierul se afișează,
# iar motivul opririi pentru alertă îl scoate scripts/motiv_oprire.py (linia „OPRIT — gata: <lot> nepublicat, <motiv>”; fără ea, motivul de rezervă cu codul de ieșire)
IES=$(mktemp) || exit 1
"$PY" scripts/publica_lot.py > "$IES" 2>&1; RP=$?
cat "$IES"
if [ "$RP" != 0 ]; then
    MOTIV=$("$PY" scripts/motiv_oprire.py "$IES" "$RP")
    rm -f "$IES"
    "$PY" scripts/jurnal_lot.py sfarsit "$LOT" publicare "$ID" stop; sh scripts/incheie_lot.sh "$LOT" nepublicat - "$MOTIV"; exit 1
fi
rm -f "$IES"
PRINCIPAL=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
(cd "$PRINCIPAL" && git merge --ff-only "$RAM" && sh scripts/githooks/post-commit) || { "$PY" scripts/jurnal_lot.py sfarsit "$LOT" publicare "$ID" esec_publicare; echo "[publica_lot] publicarea a eșuat după PASS."; sh scripts/incheie_lot.sh "$LOT" nepublicat - "publicarea a eșuat după PASS"; exit 1; }
IDR=$("$PY" scripts/jurnal_lot.py inceput "$LOT" restart)
(cd "$PRINCIPAL" && sh scripts/publica_prod.sh); RS=$?
"$PY" scripts/jurnal_lot.py sfarsit "$LOT" restart "$IDR" "$([ "$RS" = 0 ] && echo ok || echo esec)"
[ "$RS" = 0 ] || { "$PY" scripts/jurnal_lot.py sfarsit "$LOT" publicare "$ID" esec_restart; echo "[publica_lot] restartul producției nu s-a făcut (vezi mai sus)."; sh scripts/incheie_lot.sh "$LOT" nepublicat - "restartul producției nu s-a făcut"; exit 1; }
if [ "$(git -C "$PRINCIPAL" rev-parse HEAD)" = "$SHA" ] && [ "$(git -C "$PRINCIPAL" rev-parse origin/main)" = "$SHA" ]; then R=publicat; else R=incomplet; fi
"$PY" scripts/jurnal_lot.py sfarsit "$LOT" publicare "$ID" "$R"
echo "[publica_lot] $R $SHA"
if [ "$R" = publicat ]; then sh scripts/incheie_lot.sh "$LOT" publicat "$SHA"; else sh scripts/incheie_lot.sh "$LOT" nepublicat - "publicare incompletă"; fi
[ "$R" = publicat ]
