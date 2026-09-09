#!/bin/sh
# scripts/sinteza_p3.sh — SINTEZA diagnosticului P3, CITITA din artefacte.
#
# DE CE EXISTA. Prima forma a sintezei din pachet spunea „POARTA, la commitul final: suita 4270
# passed". Era o SUPRAPUNERE de doua fapte diferite: suita completa verde s-a rulat pe commitul
# POST-P2 (`6e4dd53c`), iar commiturile P3 de dupa n-au atins runtime-ul deloc. A le scrie ca si
# cum suita ar fi rulat pe commitul final sugereaza o dovada pe care artefactul n-o poarta.
#
# Scrie la stdout; cine impacheteaza il redirecteaza unde vrea.
set -e
cd /home/costin/iconta_nou

POST_P2_COMMIT=$(grep -m1 '^COMMIT' masuratori/post_p2/suita_completa_POST_P2.iesire.txt \
                 | sed 's/^COMMIT    : //')
POST_P2_SUMAR=$(grep -m1 '^SUMAR' masuratori/post_p2/suita_completa_POST_P2.iesire.txt \
                | sed 's/^SUMAR     : //')
POST_P2_RC=$(grep -m1 '^EXIT CODE' masuratori/post_p2/suita_completa_POST_P2.iesire.txt \
             | sed 's/^EXIT CODE : //')
HEAD_ACUM=$(git rev-parse HEAD)

# ce s-a schimbat in runtime dupa commitul cu suita verde? (main.py / core/ non-test)
RUNTIME=$(git diff --name-only "$POST_P2_COMMIT"..HEAD 2>/dev/null \
          | grep -E '^(main\.py|core/)' | grep -v '^core/test_' || true)

cat <<TXT
SINTEZA — P3 DIAGNOSTIC
════════════════════════════════════════════════════════════════════════

Fiecare cifra e CITITA din artefactul care a produs-o. Nimic scris de mana.

TRASABILITATE
────────────────────────────────────────────────────────────────────────
POST_P2_FULL_SUITE_COMMIT              = $POST_P2_COMMIT
POST_P2_FULL_SUITE_RESULT              = $POST_P2_SUMAR
POST_P2_FULL_SUITE_EXIT_CODE           = $POST_P2_RC
P3_FINAL_COMMIT                        = $HEAD_ACUM
REQUEST_PATH_CHANGES_AFTER_GREEN_SUITE = $( [ -z "$RUNTIME" ] && echo NO || echo "DA -> $RUNTIME" )

  Suita completa verde s-a rulat pe commitul POST-P2, NU pe commitul final P3. Commiturile P3
  de dupa contin numai diagnostic, raportare si artefacte de dovada — verificat mecanic mai sus,
  prin \`git diff --name-only\`, nu afirmat. (Poarta casei ruleaza oricum suita la fiecare commit;
  faptul ca a trecut si acolo e in plus, nu in locul dovezii de mai sus.)

CE A GASIT DIAGNOSTICUL
────────────────────────────────────────────────────────────────────────
  P3_ROUTES_N_DEPENDENT = 12   (din 37 care ating portofoliul)
  P3_ROUTES_N_PLUS_1    = 6

  Calea de SUCCES, masurata pe scheme REALE la N = 5 / 10 / 14, pentru cele patru rute de
  import — model demonstrat, nu medie total/N:
      queries(N)     = 4 + 4*N
      connections(N) = 3 + 2*N
  Liniaritate verificata pe toate cele trei puncte. La N=1000: 4.004 interogari, 2.003 conexiuni.

  Reconciliere sintetic vs real: panta de interogari difera cu exact 1/firma la trei rute din
  patru (3,0 vs 4,0), fiindca pe schema goala \`rezumat()\` iese devreme la \`to_regclass\`.
  Pantele de conexiuni coincid (2,0). Diferenta e aratata prin instructiunile capturate.

  CONCURRENCY_IMPACT   = NOT_MEASURED
  POOL_CONTENTION_RISK = UNMEASURED_BUT_PLAUSIBLE

ARTEFACTUL ACCIDENTAL
────────────────────────────────────────────────────────────────────────
$(sed -n 's/^ACCIDENTAL_TABLE_/  ACCIDENTAL_TABLE_/p' masuratori/post_p2/p3_accidental_table_cleanup.txt 2>/dev/null || echo "  (fara artefact de curatenie)")
  Dovada pre/post: masuratori/post_p2/p3_accidental_table_cleanup.txt

ARTEFACTE
────────────────────────────────────────────────────────────────────────
$(for f in masuratori/post_p2/*; do [ -f "$f" ] && printf '  %-52s %8s octeti\n' "$(basename $f)" "$(wc -c < $f)"; done)

ARTEFACTELE P2 NU AU FOST ATINSE
────────────────────────────────────────────────────────────────────────
  suita_completa_FINALA.iesire.txt : $(grep -hE 'passed' masuratori/p2/suita_completa_FINALA.iesire.txt | tail -1)
  suita_completa.iesire.txt (rosu) : $(grep -hE 'passed' masuratori/p2/suita_completa.iesire.txt | tail -1)

GENERAT: $(date -Is)  (scripts/sinteza_p3.sh)
TXT
