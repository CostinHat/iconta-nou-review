#!/bin/sh
# SINTEZA_POST_P2_HARDENING.txt — derivata EXACT din artefactele post-hardening.
# Nu se scrie de mana: fiecare cifra se citeste din fisierul care a produs-o.
set -e
cd /home/costin/iconta_nou

M=masuratori/post_p2
A="$M/suita_completa_POST_P2.iesire.txt"
S="$M/SINTEZA_POST_P2_HARDENING.txt"

[ -f "$A" ] || { echo "lipseste $A"; exit 1; }

COMMIT=$(grep -m1 '^COMMIT    :' "$A" | sed 's/^COMMIT    : //')
CMD=$(grep -m1 '^COMANDA   :' "$A" | sed 's/^COMANDA   : //')
TS=$(grep -m1 '^TIMESTAMP :' "$A" | sed 's/^TIMESTAMP : //')
SUMAR=$(grep -m1 '^SUMAR     :' "$A" | sed 's/^SUMAR     : //')
RC=$(grep -m1 '^EXIT CODE :' "$A" | sed 's/^EXIT CODE : //')

{
  echo "SINTEZA — POST-P2 HARDENING"
  echo "════════════════════════════════════════════════════════════════════════"
  echo
  echo "Cifrele de mai jos sunt CITITE din artefactele din \`masuratori/post_p2/\`, nu scrise de"
  echo "mana. Prima forma a acestui fisier repeta sumarul suitei de la P2 — corect pentru P2,"
  echo "gresit pentru hardening: descria alta rulare decat cea pe care o insotea."
  echo
  echo "COMMIT    : $COMMIT"
  echo "COMANDA   : $CMD"
  echo "TIMESTAMP : $TS"
  echo "SUMAR     : $SUMAR"
  echo "EXIT CODE : $RC"
  echo
  echo "ARTEFACTE POST-HARDENING (masuratori/post_p2/)"
  echo "────────────────────────────────────────────────────────────────────────"
  for f in "$M"/*; do
    [ -f "$f" ] || continue
    printf '  %-44s %8s octeti\n' "$(basename "$f")" "$(wc -c < "$f")"
  done
  echo
  echo "ARTEFACTELE P2 NU AU FOST ATINSE (masuratori/p2/)"
  echo "────────────────────────────────────────────────────────────────────────"
  echo "  suita_completa_FINALA.iesire.txt : $(grep -hE 'passed' masuratori/p2/suita_completa_FINALA.iesire.txt | tail -1)"
  echo "  suita_completa.iesire.txt (rosu) : $(grep -hE 'passed' masuratori/p2/suita_completa.iesire.txt | tail -1)"
  echo "  benchmark_FINAL.log              : $(grep -m1 '^EXIT CODE' masuratori/p2/benchmark_FINAL.log)"
  echo "  paritate_FINAL.log               : $(grep -m1 '^EXIT CODE' masuratori/p2/paritate_FINAL.log)"
  echo
  echo "BENCHMARKUL NU S-A REEXECUTAT, si e o decizie:"
  echo "  niciuna dintre cele sase ajustari de hardening nu atinge calea de cerere."
  echo "  Ce ruleaza in suita si acopera cerinta: \`test_p2_endpoint_query_count\` si"
  echo "  \`test_contract_6_...\` — 5 firme vs 50, pe toate cele cinci endpointuri — plus"
  echo "  \`test_verificarea_de_drift_nu_intra_in_calea_de_cerere\`."
  echo
  echo "GENERAT   : $(date -Is)  (scripts/sinteza_post_p2.sh)"
} > "$S"

echo "scris: $S"
echo
cat "$S"
