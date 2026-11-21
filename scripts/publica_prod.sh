#!/bin/sh
# publica_prod.sh — SINGURA cale de restart a producției (comanda 16.1-C3, pct.7), chemată de scripts/publica_lot.sh după push, ca pas „restart”. Rulează în depozitul principal (~/iconta_nou), pe `main`.
# REFUZ fără verdictul `PASS <HEAD>` în <git-common-dir>/publica_verdicte.log (scris numai de scripts/publica_lot.py). Ordinea: verificarea migrărilor (singura condiție a restartului), statica
# publicată, restartul, four-way. Mutat din scripts/githooks/post-commit (pasul 2b și 3), cu aceeași formă a liniilor (gardul core/test_publicare_restart_neconditionat.py o citește de aici).
# PUBLICA_PROD_PASS_LOG și PUBLICA_PROD_RESTART există numai pentru calibrare (serverul de lucru 8019 în loc de producție); PASS se cere oricum, înainte de orice altceva.
# [17.5-P0, B.4 și D.8] Două moduri. Fără argumente (prima publicare, din scripts/publica_lot.sh): cu o operație de migrare declarată deschisă pentru HEAD,
# `verifica --publicare` iese 75 NUMAI pe așteptarea demonstrată (perechea fișier/SHA a planului singura nerulată, deriva limitată la coloana declarată);
# atunci nu se publică statica, nu se repornește și nu se scrie nicio sentinelă: iese 75. Cu `--ref-migrare <E> <operație>` (numai continuarea oficială
# `sh scripts/publica_lot.sh --confirma-migrare <lot> <E>`): `verifica --confirmare <operație>` cere rândul exact (fișier, amprentă, rulata, E) și schema
# la zi, iar four-way primește aceleași argumente (ref-ul inițial al backupului Git, toți workerii). Orice alt cod rămâne eșec, cu motivul.
set -u
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
[ "$(git symbolic-ref --short HEAD 2>/dev/null)" = "main" ] || { echo "[publica_prod] REFUZ: restartul producției se face de pe main (depozitul principal)."; exit 1; }
HEAD_SHA=$(git rev-parse HEAD)
case "$#" in
  0) MOD_VERIFICA="--publicare"; ARG_4W="" ;;
  3) [ "$1" = "--ref-migrare" ] && [ "$2" = "$HEAD_SHA" ] || { echo "[publica_prod] REFUZ: --ref-migrare <E=HEAD> <operație>"; exit 2; }
     MOD_VERIFICA="--confirmare $3"; ARG_4W="--ref-migrare $2 $3"
     PUBLICA_OPERATIE_MIGRARE="$2 $3"; export PUBLICA_OPERATIE_MIGRARE ;;
  *) echo "[publica_prod] REFUZ: argumente: nimic sau --ref-migrare <E> <operație>"; exit 2 ;;
esac
PASS_LOG="${PUBLICA_PROD_PASS_LOG:-$(git rev-parse --path-format=absolute --git-common-dir)/publica_verdicte.log}"
RESTART_CMD="${PUBLICA_PROD_RESTART:-sudo -n systemctl restart iconta-nou}"

banner() {   # $1=tinta  $2=sentinela  $3=motiv  $4=remediu
    echo ""
    echo "############################################################"
    echo "## [publica_prod] RESTART/PUBLICARE pe $1 NEFACUT: $3"
    echo "## Rezolva ACUM: $4"
    echo "## Sentinela $2 scrisa - raportul NU e 'incheiat' cat timp exista."
    echo "############################################################"
    echo ""
    printf '%s\n' "$3" > "$2"
}

# ---------- 2b. PUBLICAREA STATICULUI (R118) — făcută la pasul 3, NUMAI odată cu restartul ----------
# CE SE SERVESTE nu mai e CE E IN LUCRU: /static se monteaza din ../iconta_publicat/static, scris
# de aici, din HEAD. Deci un .js ajunge la un browser DOAR dupa ce a trecut poarta si a intrat in
# commit. Publicarea are propria poarta de sintaxa (node --check pe fiecare .js) si REFUZA sa
# inlocuiasca ce se serveste daca vreunul nu se parseaza.
#
# ORDINEA CONTEAZA: publicarea vine INAINTE de restart. Invers, procesul nou ar porni pe statica
# veche, iar Python-ul si JS-ul ar descrie doua versiuni diferite ale aplicatiei. Esec = sentinela
# + banner, ca la push-uri; NICIODATA tacut.
# [10.10.2026, lotul „Retestul plasei”] ...si se publică NUMAI când procesul viu preia același commit: cu restartul oprit de o migrare
# nerulată, statica nouă ajungea peste backendul vechi (văzut la 445f9932: JS-ul commitului servit de procesul pe 60c716d1). Cu
# restartul oprit, statica rămâne a commitului care rulează; rulatorul migrărilor o publică înaintea restartului lui.
S_PS=".git/PUBLICARE_STATIC_ESUATA"; rm -f "$S_PS"
publica_statica() {
    if "$PWD/venv/bin/python" scripts/publica_static.py > /tmp/publica_static.log 2>&1; then
        echo "[publica_prod] static publicat: $(tail -1 /tmp/publica_static.log)"
    else
        banner "static publicat" "$S_PS" "publicarea staticului a esuat: $(tail -1 /tmp/publica_static.log 2>/dev/null)"            "citeste /tmp/publica_static.log (de obicei: un .js care nu se parseaza), repara, apoi: ./venv/bin/python scripts/publica_static.py"
    fi
}

# ---------- 3. restart NECONDITIONAT: procesul viu preia HEAD dupa ORICE publicare ----------
# NU se inspecteaza tipul commitului (runtime / docs / CSV / JS). Conditionarea pe tip a produs
# divergenta RUNNING != HEAD (un commit de docs a lasat procesul pe commitul anterior). Regula
# CLAUDE.md §2.3 pct.10: dupa orice publicare din lant, procesul viu incarca HEAD - fara exceptii,
# fara liste de tipuri. Gardat de core/test_publicare_restart_neconditionat.py (cade daca reapare
# orice conditionare pe continut). Esec = sentinela + banner, niciodata tacut (ca push-urile).
#
# [09.10.2026, comanda Costin pct.2 — PIVOT, singura conditie admisa] „Daca un commit contine o migrare nerulata pe productie,
# aplicatia nu reporneste.” Conditia NU e pe tipul commitului, ci pe STAREA productiei: `core.migrari_registru verifica` confrunta
# migrarile din HEAD cu registrul `public.migrari_rulate` si schemele firmelor cu `tenant_template.sql` din HEAD. FAIL-CLOSED: daca
# nu se poate sti, nu reporneste. Rulatorul (`... ruleaza --productie <fisier>`) reporneste el, dupa ultima migrare lipsa.
# Gardat de core/test_publicare_restart_neconditionat.py (verificarea e singura conditie; alta reaparuta -> pica).
S_RS=".git/RESTART_ESUAT"; rm -f "$S_RS"
S_MG=".git/RESTART_OPRIT_MIGRARE"; rm -f "$S_MG"
# [16.1, pct.4] restartul producției refuză fără verdictul PASS al lui scripts/publica_lot.sh pentru acest SHA (scriptul de restart = acest hook; rulatorul migrărilor
# din core/ reporneste el însuși și nu e păzit de acest rând — limită declarată în raportul 16.1).
if ! grep -q "^PASS $HEAD_SHA " "$PASS_LOG" 2>/dev/null; then
    banner "iconta-nou (restart REFUZAT)" "$S_RS" "fără verdictul PASS al lui scripts/publica_lot.sh pentru $HEAD_SHA" "sh scripts/publica_lot.sh din ramura lotului"
elif "$PWD/venv/bin/python" -m core.migrari_registru verifica "$HEAD_SHA" $MOD_VERIFICA > /tmp/migrari_verifica.log 2>&1; then
    publica_statica   # statica commitului, înaintea restartului (pasul 2b)
    if $RESTART_CMD > /tmp/restart_iconta.log 2>&1; then
        echo "[publica_prod] iconta-nou restartat -> procesul viu preia $(git rev-parse --short HEAD)"
    else
        banner "iconta-nou (restart)" "$S_RS" "restart a esuat: $(tail -1 /tmp/restart_iconta.log 2>/dev/null)" \
               "verifica sudoers (systemctl restart iconta-nou), apoi ruleaza: sudo systemctl restart iconta-nou"
    fi
else
    RC_MIGRARI=$?
    cat /tmp/migrari_verifica.log
    if [ "$RC_MIGRARI" = 75 ] && [ -z "$ARG_4W" ]; then
        # așteptarea demonstrată a migrării declarate: nimic publicat, nimic repornit; operatorul preia (B.4)
        echo "[publica_prod] AȘTEAPTĂ MIGRAREA: static nepublicat, restart nefăcut; procesul viu rămâne pe commitul anterior până la confirmarea operatorului"
        exit 75
    fi
    echo "[publica_prod] static NEpublicat: procesul viu ramane pe commitul anterior pana la migrare; rulatorul publica statica inaintea restartului"
    banner "iconta-nou (restart OPRIT)" "$S_MG" "productia nu are inca migrarile commitului (lista de mai sus)" \
           "ruleaza fiecare migrare listata: ./venv/bin/python -m core.migrari_registru ruleaza --productie <fisier> — dupa ultima, rulatorul reporneste aplicatia"
fi


# ---------- four-way: confirmarea celor patru brațe, după restart (scriptul e al lui post-commit și al rulatorului migrărilor; scrie sau șterge .git/FOUR_WAY_NEINCHIS) ----------
if [ -e "$S_RS" ] || [ -e "$S_MG" ] || [ -e "$S_PS" ]; then
    echo "[publica_prod] restartul producției NU s-a făcut ($(cat "$S_RS" "$S_MG" "$S_PS" 2>/dev/null | head -1)); four-way nu se rulează."
    exit 1
fi
sh "$ROOT/scripts/githooks/four-way" $ARG_4W || exit 1
[ -e .git/FOUR_WAY_NEINCHIS ] && exit 1
exit 0
