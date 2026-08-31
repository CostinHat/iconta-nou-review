#!/bin/bash
# verificator_neconformitati.sh — verifica MECANIC fiecare NC din jurnal, pe serverul real
# Rulare: bash verificator_neconformitati.sh
#
# ─── TREI REZULTATE, NU DOUA (31.08.2026, cerut de Costin) ────────────────────────────────────
#
# DE UNDE VINE, cu instanta ei. Scriptul tiparea `FAIL NC-07 JWT_SECRET lipseste din proces!` cand
# `sudo` nu e disponibil neinteractiv. Secretul ERA acolo; ce lipsea era dreptul de a te uita.
# *Un blocaj care afirma absenta cand de fapt n-a putut verifica e blocaj fara temei* — aceeasi
# clasa cu „un necunoscut nu se rotunjeste la «stiu ca nu»" (interdictia 32/10, R39). Norma:
# CONFORMITATE.md 77.
#
# REPARATIA E UN AL TREILEA REZULTAT, NU MAI MULTE DREPTURI. Setul de sudoers ramane INGUST,
# deliberat: un verificator care are nevoie de mai multe drepturi ca sa spuna adevarul cere sa fie
# crezut pe incredere. Cand nu poate citi, SPUNE ca nu poate citi.
#
#   PASS     verificat, si e conform
#   FAIL     verificat, si NU e conform
#   NEVERIF  nu s-a putut verifica — cu motivul scris pe acelasi rand
#
# COD DE IESIRE (inainte era 0 chiar si peste `FAIL: 3` — a treia fata a aceleiasi boli):
#   0  totul verificat, totul conform
#   1  cel putin un FAIL
#   2  zero FAIL, dar cel putin un NEVERIF — o rulare oarba NU are voie sa arate verde
#
# CELE PATRU FORME DE ORBIRE, toate acoperite (masurate pe 31.08: una VIE, trei LATENTE):
#   VIE      NC-07: `sudo` indisponibil -> raporta absenta secretului
#   LATENTA  interogarea care nu ruleaza -> sir gol, care nu e „0", deci FAIL
#   LATENTA  fisierul care lipseste -> `grep` esueaza, deci FAIL
#   LATENTA  globul care nu potriveste nimic -> `wc -l` da 0, deci **PASS** (directia inversa,
#            si mai rea: un zero pe multime goala arata identic cu un zero real — METODA §22)
# Plus ANCORA MOARTA: un marker scos de o rescriere legitima nu e neconformitate, e o verificare
# care si-a pierdut obiectul. Se raporteaza NEVERIF, cu motivul — nu FAIL pe vecie.

E=~/iconta_nou/static/js/ecrane
RAD=~/iconta_nou
ok=0; fail=0; neverif=0

pass()    { echo "PASS     $1  $2"; ok=$((ok+1)); }
esec()    { echo "FAIL     $1  $2"; fail=$((fail+1)); }
# neverif NC "descriere" COD "motiv" — COD-ul e stabil si se poate proba; motivul e pentru om.
# Fara cod, doua ramuri diferite dau acelasi verdict, iar o mutatie care scoate una dintre ele
# ramane VERDE: exact ce s-a intamplat la prima proba prin mutatie (2 din 7 neprobate).
neverif() { echo "NEVERIF  $1  $2  [$3] — nu s-a putut verifica: $4"; neverif=$((neverif+1)); }

# psqlv: ecou pe stdout; rc!=0 daca interogarea NU A RULAT. Diferenta fata de forma veche, care
# inghitea eroarea si intorcea sir gol — indistinguibil de un rezultat gol legitim.
psqlv() {
    local out
    out=$(sudo -n -u postgres psql iconta_v2 -tAc "$1" 2>/dev/null) || return 1
    [ -n "$out" ] || return 1
    printf '%s' "$out"
}

# db0 NC "descriere" "SQL" — asteapta rezultatul "0"
db0() {
    local nc="$1" desc="$2" sql="$3" out
    if ! out=$(psqlv "$sql"); then
        neverif "$nc" "$desc" "interogare-neexecutata" "interogarea nu a rulat (psql sau sudo -u postgres indisponibil)"
        return
    fi
    if [ "$out" = "0" ]; then pass "$nc" "$desc"; else esec "$nc" "$desc (gasite: $out)"; fi
}

# marker NC "descriere" MARKER FISIER — deosebeste patru stari, nu doua
marker() {
    local nc="$1" desc="$2" m="$3" f="$4"
    if [ ! -r "$f" ]; then
        neverif "$nc" "$desc" "fisier-ilizibil" "fisierul $f nu exista sau nu se poate citi"
        return
    fi
    if grep -q -e "$m" "$f"; then
        pass "$nc" "$desc"
    # ATENTIE la forma comenzii: `grep -rq -- "$m" "$RAD" --include=...` NU merge — `--` opreste
    # parsarea optiunilor, deci `--include` devine NUME DE FISIER, iar cautarea intra in `.git`
    # si potriveste in packfile-uri. Prima forma a acestei functii facea exact asta si raporta
    # „ancora s-a mutat" despre un marker care nu mai exista nicaieri. Prins masurand, nu citind.
    elif ! grep -rq --include='*.py' --include='*.js' --exclude-dir=venv --exclude-dir=.git \
             -e "$m" "$RAD" 2>/dev/null; then
        neverif "$nc" "$desc" "ancora-moarta" "ancora '$m' nu mai exista NICAIERI in cod — verificarea si-a pierdut obiectul; nu codul si-a pierdut conformitatea"
    else
        esec "$nc" "$desc (ancora exista in alt fisier decat cel verificat)"
    fi
}

# fara_tipar NC "descriere" TIPAR [EXCLUDE] — zero aparitii in ecrane, cu ANTI-VACUU pe glob
fara_tipar() {
    local nc="$1" desc="$2" tipar="$3" excl="$4" n gasite
    n=$(ls "$E"/*.js 2>/dev/null | wc -l)
    if [ "$n" -eq 0 ]; then
        neverif "$nc" "$desc" "glob-gol" "niciun fisier .js in $E — un zero pe multime goala arata identic cu un zero real"
        return
    fi
    if [ -n "$excl" ]; then
        gasite=$(grep -h -e "$tipar" "$E"/*.js 2>/dev/null | grep -vc -e "$excl")
    else
        gasite=$(grep -hc -e "$tipar" "$E"/*.js 2>/dev/null | paste -sd+ | bc)
    fi
    [ -n "$gasite" ] || gasite=0
    if [ "$gasite" = "0" ]; then pass "$nc" "$desc ($n fisiere scanate)"
    else esec "$nc" "$desc (gasite: $gasite)"; fi
}

# env_proces NC CHEIE — secretul e in mediul procesului VIU
env_proces() {
    local nc="$1" cheie="$2" pid mediu
    pid=$(pgrep -f "uvicorn main:app.*8010" | head -1)
    if [ -z "$pid" ]; then
        neverif "$nc" "$cheie in procesul viu" "proces-negasit" "procesul uvicorn nu a fost gasit — nu se poate afirma nimic despre mediul lui"
        return
    fi
    if ! sudo -n true 2>/dev/null; then
        neverif "$nc" "$cheie in procesul viu" "sudo-indisponibil" "citirea /proc/$pid/environ cere sudo, indisponibil neinteractiv; setul de sudoers ramane INGUST, deliberat"
        return
    fi
    if ! mediu=$(sudo -n cat "/proc/$pid/environ" 2>/dev/null); then
        neverif "$nc" "$cheie in procesul viu" "proc-necitibil" "sudo raspunde, dar /proc/$pid/environ nu s-a putut citi"
        return
    fi
    if printf '%s' "$mediu" | tr '\0' '\n' | grep -q "^$cheie="; then
        pass "$nc" "$cheie incarcat in procesul viu (pid $pid)"
    else
        esec "$nc" "$cheie LIPSESTE din mediul procesului viu (pid $pid)"
    fi
}

# Sursabil pentru gard: `VERIF_NC_DOAR_FUNCTII=1 source verificator_neconformitati.sh` defineste
# functiile fara sa ruleze nimic. Gardul e core/test_verificator_al_treilea_rezultat.py.
if [ "${VERIF_NC_DOAR_FUNCTII:-0}" = "1" ]; then
    return 0 2>/dev/null || exit 0
fi

echo "== Verificare mecanica neconformitati (jurnal 09.07.2026) =="
# NC-01/02: zero dublari de serie in date + fixuri prezente
db0 "NC-01" "date chitante fara MD-MD" "SELECT count(*) FROM tenant_003.chitante WHERE reprezentand LIKE '%MD-MD%'"
db0 "NC-02" "descrieri contare fara MD-MD" "SELECT count(*) FROM tenant_003.inregistrari WHERE descriere LIKE '%MD-MD%'"
marker "NC-02" "fix generator contare (marker)" "fix_serie_contare_v1" "$RAD/main.py"
marker "NC-01" "fix generator chitante (marker)" "chitante_emise_v2_reprezentand" "$RAD/main.py"
# NC-03: etichete PDF explicite
marker "NC-03" "PDF factura / PDF chitanta" "PDF factur" "$E/facturi_ecran.js"
# NC-04..06: lista + side-by-side + rotire
marker "NC-04" "sosire pe rand (e7b)" "bon_flux_e7b_v1" "$E/firme.js"
marker "NC-05" "side-by-side (e8)" "bon_flux_e8_v1" "$E/firme.js"
marker "NC-06" "rotire libera (e9b)" "bon_flux_e9b_v1" "$E/firme.js"
marker "NC-06" "lupa X+Esc (e9c)" "bon_flux_e9c_v1" "$RAD/static/js/api.js"
# NC-07: procesul uvicorn ARE secretele in mediu
env_proces "NC-07" "JWT_SECRET"
env_proces "NC-07" "ANTHROPIC_API_KEY"
# NC-08/09: login doua cai + butoane camera
marker "NC-08" "login doua cai" "ux_login_camera_v1" "$E/login.js"
marker "NC-09" "butoane camera/galerie" "ux_login_camera_v1" "$E/portal.js"
# NC-10/11: zero dialoguri de browser
fara_tipar "NC-10" "zero alert() in ecrane" "alert(" ".bak"
fara_tipar "NC-11" "zero confirm() de browser" "confirm(" "confirmaCaseta"
# NC-12: ergonomie sesizari
marker "NC-12" "Trimite primar + Adauga secundar" 'buton-secundar" id="rap-add-poza' "$E/raporteaza.js"
# NC-13/14/15: navigator + emitere
marker "NC-13" "sageata doar cu drum (navigator)" "sageata_dinamica_v1" "$RAD/static/js/navigator.js"
marker "NC-14" "emitere respecta opt.inapoi" "emitere_inapoi_v1" "$E/emitere_ecran.js"
marker "NC-15" "traseu automat (nav.mergi)" "traseu_automat_v1" "$RAD/static/js/navigator.js"
# NC-15 supliment: zero setInapoi(undefined) in AFARA vaarfului de fereastra nu e verificabil prin grep simplu — acoperit de analiza din 09.07
# NC-16: comentariile corectate
marker "NC-16" "comentariu antet aliniat" "UN PAS ÎNAPOI pe traseul parcurs" "$RAD/static/js/navigator.js"
# NC-17: email optional
marker "NC-17" "email optional la Adauga firma" "firma_email_optional_v1" "$E/firme.js"
# NC-18: DESCHISA — verific ca problema INCA exista (etichete lipsa in emitere)
if [ ! -r "$E/emitere_ecran.js" ]; then
    echo "INFO     NC-18  nu se poate reevalua: $E/emitere_ecran.js nu se poate citi"
elif grep -q 'placeholder="CUI beneficiar' "$E/emitere_ecran.js"; then
    echo "INFO     NC-18  DESCHISA (confirmat: campuri doar cu placeholder) — planificata R2"
else
    echo "INFO     NC-18  de reevaluat (ancora negasita; textul 'CUI beneficiar' exista, dar nu in forma 'placeholder=\"CUI beneficiar')"
fi
echo "=============================================="
echo "PASS: $ok   FAIL: $fail   NEVERIF: $neverif"
if [ "$neverif" -gt 0 ]; then
    echo "ATENTIE: $neverif verificari NU S-AU PUTUT FACE. Rularea NU e completa — motivele sunt pe randurile NEVERIF."
    echo "         Un NEVERIF nu e o neconformitate; e absenta unei probe. Nu se stinge largind drepturile."
fi
echo "Neverificabile mecanic PRIN NATURA LOR (cer om): NC-13/14 (2 click-uri), NC-12/17 (vizual), NC-19 (email ajuns?)"

if [ "$fail" -gt 0 ]; then exit 1; fi
if [ "$neverif" -gt 0 ]; then exit 2; fi
exit 0
