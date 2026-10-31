#!/bin/sh
# poarta_lot.sh — POARTA IMPLICITĂ (comanda 15.G, 30.10.2026). Mecanică: rulează NUMAI
#   1. testele picate la ultima rulare (pytest --lf; plasa e2e: fișierele din poarta_e2e_cazute.txt),
#   2. testele fișierelor atinse de la ultima publicare (scripts/poarta_selectie.py),
#   3. scenariile deficiențelor: core/test_lot*scenariu* și plasa e2e numai din scenarii_<comanda>.txt (POARTA_COMANDA) + fluxurile atinse
#      (scripts/poarta_harta.txt) + cele picate la ultima rulare,
#   4. nucleul fiscal și de calcul (declarații, TVA, solduri, stocuri, salarii),
#   5. verificatorul (verificator_conformitate.py).
# Nimic altceva. Marcajul POARTA_SARE (scripts/poarta.env) sare peste testele din scripts/poarta_sare.txt și poarta_forma.txt.
# Rularea completă (tot pytest + toată plasa e2e) există numai ca scripts/poarta_completa.sh, cu cheie de la arhitect.
# Refuză: fără ramură; arbore murdar; un SHA deja VERDE sau ROȘU. PE `main` (15.G2) rulează informativ, măsurat: fără verdict scris, fără refuz
# pentru SHA deja VERDE. Scrie `VERDE|ROSU <sha> <ramura> <data>` în
# `<git-common-dir>/poarta_verdicte.log` (îl cere scripts/githooks/reference-transaction la mutarea lui `main`) și durata la final.
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
[ -n "$1" ] && { echo "[poarta lot] REFUZ: poarta implicita nu are argumente (primit: $1)."; exit 1; }
COMUN=$(git rev-parse --path-format=absolute --git-common-dir) || exit 1
JV="$COMUN/poarta_verdicte.log"
RAM=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ -z "$RAM" ]; then
    echo "[poarta lot] REFUZ: poarta ruleaza pe o ramura (acum: HEAD detasat)."
    exit 1
fi
MURDAR=$(git status --porcelain --untracked-files=normal)
if [ -n "$MURDAR" ]; then
    echo "[poarta lot] REFUZ: arborele nu e curat — poarta judeca COMMITUL lotului; comite tot ce intra in lot, intai:"
    echo "$MURDAR" | head -20 | sed 's/^/    /'
    exit 1
fi
SHA=$(git rev-parse HEAD)
[ "$RAM" != "main" ] && grep -q "^VERDE $SHA " "$JV" 2>/dev/null && { echo "[poarta lot] REFUZ: $SHA are deja poarta VERDE."; exit 1; }
[ "$RAM" != "main" ] && grep -q "^ROSU $SHA " "$JV" 2>/dev/null && { echo "[poarta lot] REFUZ: $SHA are deja poarta ROSIE — pe rosu se repara codul (commit nou) si se ruleaza din nou."; exit 1; }
PY=./venv/bin/python
[ -x "$PY" ] || PY=python3
J=${POARTA_JURNALE:-/tmp}
CAPTURI="$J/e2e_poarta_capturi"
CAZUTE_E2E="$COMUN/poarta_e2e_cazute.txt"
NW=${POARTA_PROCESE:-3}
export POARTA_SARE=1
ROSII=""
rosu() { ROSII="$ROSII $1"; echo "[poarta lot] ROSU: $1"; }
T0=$(date +%s)
echo "[poarta lot] $RAM, commit $SHA: poarta implicita (marcaj POARTA_SARE=1)"

"$PY" scripts/poarta_selectie.py > "$J/poarta_selectie.json" || { echo "[poarta lot] selectia a esuat"; exit 1; }
"$PY" - "$J/poarta_selectie.json" "$J" <<'PYE'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
open(sys.argv[2] + "/poarta_pytest_fisiere.txt", "w").write("\n".join(d["pytest"]) + "\n")
open(sys.argv[2] + "/poarta_e2e_fisiere.txt", "w").write("\n".join(d["e2e"]) + "\n")
print("[poarta lot] selectie: %d fisiere pytest, %d fisiere e2e; perimetru incert (nu extinde): %s" % (len(d["pytest"]), len(d["e2e"]), d["incerte"] or "nimic"))
open(sys.argv[2] + "/poarta_flux_harta.txt", "w").write("\n".join(d["flux_harta"]) + "\n")   # lista completa a fluxurilor din harta (raport, D)
print("[poarta lot] fluxuri atinse (b): %d fisiere din harta%s; lista completa: %s/poarta_flux_harta.txt" % (len(d["flux_harta"]),
      " — peste 20: inlocuite cu cele numite sub FLUXURI in scenarii" if d["flux_inlocuit"] else "", sys.argv[2]))
PYE

# POARTA_DOAR_PLASA=<sha>: rerularea numai a plasei e2e, dupa o rulare in care pytest si verificatorul au fost VERZI pe <sha> (verdict compus, 15.1).
# Permis numai daca diferenta <sha>..HEAD atinge exclusiv fisiere ale portii, CLAUDE.md sau registre (nicio schimbare de aplicatie).
DOAR_PLASA="${POARTA_DOAR_PLASA:-}"
if [ -n "$DOAR_PLASA" ]; then
    ALTELE=$(git diff --name-only "$DOAR_PLASA" HEAD | grep -vE '^(scripts/poarta|CLAUDE\.md$|DECIZII\.md$|DEFICIENTE\.md$|PREDARE_LANT\.md$)' )
    if [ -n "$ALTELE" ]; then
        echo "[poarta lot] REFUZ: POARTA_DOAR_PLASA=$DOAR_PLASA, dar de atunci s-au schimbat si alte fisiere:"; echo "$ALTELE" | head -10 | sed 's/^/    /'
        exit 1
    fi
    echo "[poarta lot] DOAR PLASA e2e (pytest si verificatorul sunt verzi pe $DOAR_PLASA; fisiere schimbate de atunci: numai ale portii / registre)"
fi

# Ordinea treptelor (regula 15.1, 31.10.2026): 1. verificatorul de design, 2. pytest țintit, 3. plasa e2e. Prima treaptă ROȘIE oprește poarta și
# scrie ROȘU imediat (fără să continue), ca timpul să nu se piardă pe treptele de după.
final() {   # scrie verdictul și iese
    DUR="verificator ${T_VERIF:-0}s · pytest ${T_PYTEST:-0}s · plasa e2e ${T_E2E:-0}s · total $(( $(date +%s) - T0 ))s"
    if [ -z "$ROSII" ]; then V=VERDE; RCF=0; else V=ROSU; RCF=1; fi
    [ "$RAM" != "main" ] && echo "$V $SHA $RAM $(date -Is)" >> "$JV"
    echo "    DURATE: $(date -Is) $V ·$ROSII · poarta implicita · $DUR" >> "$ROOT/.poarta_jurnal.log"
    echo "[poarta lot] $V $SHA ($RAM) -> $JV · $DUR"
    exit $RCF
}
T_VERIF=0; T_PYTEST=0; T_E2E=0
if [ -z "$DOAR_PLASA" ]; then
    # 1. verificatorul de design
    T_V0=$(date +%s)
    "$PY" verificator_conformitate.py > "$J/poarta_verificator.log" 2>&1
    T_VERIF=$(( $(date +%s) - T_V0 ))
    TOT=$(grep -i "TOTAL" "$J/poarta_verificator.log")
    echo "[poarta lot] verificator: $TOT (${T_VERIF}s)"
    case "$TOT" in *"TOTAL: 0"*) ;; *) rosu "verificator"; final ;; esac
    # 2. pytest țintit (întâi cele picate la ultima rulare)
    T_P0=$(date +%s)
    "$PY" -m pytest -q --lf --lfnf=none > "$J/poarta_pytest_lf.log" 2>&1
    RC=$?
    case "$RC" in 0|5) ;; *) rosu "pytest --lf (picate la ultima rulare)" ;; esac
    tail -1 "$J/poarta_pytest_lf.log"
    if [ -z "$ROSII" ]; then
        xargs "$PY" -m pytest -q -n "$NW" --dist loadfile < "$J/poarta_pytest_fisiere.txt" > "$J/poarta_pytest.log" 2>&1
        RC=$?
        [ "$RC" -ne 0 ] && rosu "pytest (atinse + nucleu + scenarii)"
        tail -1 "$J/poarta_pytest.log"
    fi
    T_PYTEST=$(( $(date +%s) - T_P0 ))
    [ -n "$ROSII" ] && final
fi

# plasa e2e: scenariile + fisierele atinse + cele cazute la rularea anterioara; dupa pytest (aceeasi baza de test)
E2E="$(cat "$J/poarta_e2e_fisiere.txt")"
[ -f "$CAZUTE_E2E" ] && E2E="$E2E
$(cat "$CAZUTE_E2E")"
ARG=""
for f in $(echo "$E2E" | sort -u); do [ -n "$f" ] && ARG="$ARG --doar=$f"; done
T_E0=$(date +%s)
rm -f "$CAPTURI/pytest.log"
if [ -n "$ARG" ]; then
    # shellcheck disable=SC2086
    "$PY" scripts/e2e_poarta.py $ARG "$CAPTURI" > "$J/poarta_e2e.log" 2>&1
    RC=$?
    tail -1 "$J/poarta_e2e.log"
    [ "$RC" -ne 0 ] && rosu "plasa e2e"
    # cazutele plasei raman pentru urmatoarea rulare (echivalentul lui --lf)
    grep -hE "^(FAILED|ERROR) " "$CAPTURI/pytest.log" "$J/poarta_e2e.log" 2>/dev/null | sed -E 's#^(FAILED|ERROR) ([^: ]*/)?([^:/ ]+\.py).*#\3#' | grep "\.py$" | sort -u > "$CAZUTE_E2E"
    [ "$RC" -eq 0 ] && : > "$CAZUTE_E2E"
fi
T_E2E=$(( $(date +%s) - T_E0 ))

if [ "$(git rev-parse HEAD)" != "$SHA" ] || [ -n "$(git diff --name-only)" ]; then
    echo "[poarta lot] arborele/HEAD s-au schimbat cat a rulat poarta — verdictul nu mai e despre $SHA."
    rosu "arbore schimbat"
fi
final
