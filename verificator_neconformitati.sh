#!/bin/bash
# verificator_neconformitati.sh — verifica MECANIC fiecare NC din jurnal, pe serverul real
# Rulare: bash verificator_neconformitati.sh
E=~/iconta_nou/static/js/ecrane
ok=0; fail=0
v() { # v "NC" "descriere" comanda...
  local nc="$1"; local desc="$2"; shift 2
  if "$@" >/dev/null 2>&1; then echo "PASS  $nc  $desc"; ok=$((ok+1));
  else echo "FAIL  $nc  $desc"; fail=$((fail+1)); fi
}
psqlv() { sudo -u postgres psql iconta_v2 -tAc "$1" 2>/dev/null; }

echo "== Verificare mecanica neconformitati (jurnal 09.07.2026) =="
# NC-01/02: zero dublari de serie in date + fixuri prezente
[ "$(psqlv "SELECT count(*) FROM tenant_003.chitante WHERE reprezentand LIKE '%MD-MD%'")" = "0" ] && echo "PASS  NC-01 date chitante fara MD-MD" && ok=$((ok+1)) || { echo "FAIL  NC-01"; fail=$((fail+1)); }
[ "$(psqlv "SELECT count(*) FROM tenant_003.inregistrari WHERE descriere LIKE '%MD-MD%'")" = "0" ] && echo "PASS  NC-02 descrieri contare fara MD-MD" && ok=$((ok+1)) || { echo "FAIL  NC-02"; fail=$((fail+1)); }
v "NC-02" "fix generator contare (marker)" grep -q "fix_serie_contare_v1" ~/iconta_nou/main.py
v "NC-01" "fix generator chitante (marker)" grep -q "chitante_emise_v2_reprezentand" ~/iconta_nou/main.py
# NC-03: etichete PDF explicite
v "NC-03" "PDF factura / PDF chitanta" grep -q "PDF factur" $E/facturi_ecran.js
# NC-04..06: lista + side-by-side + rotire
v "NC-04" "sosire pe rand (e7b)" grep -q "bon_flux_e7b_v1" $E/firme.js
v "NC-05" "side-by-side (e8)" grep -q "bon_flux_e8_v1" $E/firme.js
v "NC-06" "rotire libera (e9b)" grep -q "bon_flux_e9b_v1" $E/firme.js
v "NC-06" "lupa X+Esc (e9c)" grep -q "bon_flux_e9c_v1" ~/iconta_nou/static/js/api.js
# NC-07: procesul uvicorn ARE secretele in mediu
PID=$(pgrep -f "uvicorn main:app.*8010" | head -1)
[ -n "$PID" ] && sudo cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | grep -q "^JWT_SECRET=" && echo "PASS  NC-07 JWT_SECRET incarcat in procesul live" && ok=$((ok+1)) || { echo "FAIL  NC-07 JWT_SECRET lipseste din proces!"; fail=$((fail+1)); }
[ -n "$PID" ] && sudo cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | grep -q "^ANTHROPIC_API_KEY=" && echo "PASS  NC-07 ANTHROPIC_API_KEY in proces" && ok=$((ok+1)) || { echo "FAIL  NC-07 ANTHROPIC_API_KEY lipseste!"; fail=$((fail+1)); }
# NC-08/09: login doua cai + butoane camera
v "NC-08" "login doua cai" grep -q "ux_login_camera_v1" $E/login.js
v "NC-09" "butoane camera/galerie" grep -q "ux_login_camera_v1" $E/portal.js
# NC-10/11: zero dialoguri de browser
[ "$(grep -h "alert(" $E/*.js 2>/dev/null | grep -v ".bak" | wc -l)" = "0" ] && echo "PASS  NC-10 zero alert() in ecrane" && ok=$((ok+1)) || { echo "FAIL  NC-10"; fail=$((fail+1)); }
[ "$(grep -h "confirm(" $E/*.js 2>/dev/null | grep -v "confirmaCaseta" | wc -l)" = "0" ] && echo "PASS  NC-11 zero confirm() de browser" && ok=$((ok+1)) || { echo "FAIL  NC-11"; fail=$((fail+1)); }
# NC-12: ergonomie sesizari
v "NC-12" "Trimite primar + Adauga secundar" grep -q 'buton-secundar" id="rap-add-poza' $E/raporteaza.js
# NC-13/14/15: navigator + emitere
v "NC-13" "sageata doar cu drum (navigator)" grep -q "sageata_dinamica_v1" ~/iconta_nou/static/js/navigator.js
v "NC-14" "emitere respecta opt.inapoi" grep -q "emitere_inapoi_v1" $E/emitere_ecran.js
v "NC-15" "traseu automat (nav.mergi)" grep -q "traseu_automat_v1" ~/iconta_nou/static/js/navigator.js
# NC-15 supliment: zero setInapoi(undefined) in AFARA vaarfului de fereastra nu e verificabil prin grep simplu — acoperit de analiza din 09.07
# NC-16: comentariile corectate
v "NC-16" "comentariu antet aliniat" grep -q "UN PAS ÎNAPOI pe traseul parcurs" ~/iconta_nou/static/js/navigator.js
# NC-17: email optional
v "NC-17" "email optional la Adauga firma" grep -q "firma_email_optional_v1" $E/firme.js
# NC-18: DESCHISA — verific ca problema INCA exista (etichete lipsa in emitere)
if grep -q 'placeholder="CUI beneficiar' $E/emitere_ecran.js 2>/dev/null; then echo "INFO  NC-18 DESCHISA (confirmat: campuri doar cu placeholder) — planificata R2"; else echo "INFO  NC-18 de reevaluat (ancora negasita)"; fi
echo "=============================================="
echo "PASS: $ok   FAIL: $fail"
echo "Neverificabile mecanic (cer om): NC-13/14 (2 click-uri), NC-12/17 (vizual), NC-19 (email ajuns?)"
