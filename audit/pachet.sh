#!/bin/bash
# PACHETUL DE AUDIT INDEPENDENT — se asambleaza de aici, nu cu mana.
#
# De ce e in depozit: pachetul afirma despre sine ca e reproductibil. Daca scriptul care il
# construieste ar trai in /tmp, afirmatia n-ar avea cum sa fie verificata de nimeni din afara.
#
# Rulare, PE SERVER, din radacina depozitului, cu mediul de test incarcat:
#     set -a && . ~/.iconta/test.env && set +a && bash audit/pachet.sh
set -e
cd "$(dirname "$0")/.."

ZI=$(date +%F)
CAP=$(git rev-parse HEAD)
RAD=/tmp/pachet_AUDIT/iconta_AUDIT_$ZI

rm -rf /tmp/pachet_AUDIT
mkdir -p "$RAD"/{01_COMMIT,02_REGISTRE,03_PROBAT,04_NEVERIFICAT,05_FISCAL,06_ARTEFACTE,07_RAPOARTE}

# ── 01. COMMITUL ─────────────────────────────────────────────────────────────
{
  echo "COMMIT: $CAP"
  git log -1 --format='data:    %ci%nautor:   %an%nsubiect: %s'
  echo
  echo "=== git status (trebuie sa fie GOL) ==="
  git status --porcelain || true
  echo "(gol de mai sus = arborele e curat)"
  echo
  echo "=== --stat al commitului ==="
  git show --stat --format='' "$CAP" | tail -40
  echo
  echo "=== ultimele 20 de commituri ==="
  git log --oneline -20
} > "$RAD/01_COMMIT/COMMIT.txt"

./venv/bin/pip freeze > "$RAD/01_COMMIT/DEPENDENTE.txt" 2>/dev/null || true

URL_PUBLIC=https://github.com/CostinHat/iconta-nou-review.git
{
  echo "# OGLINDA PUBLICĂ"
  echo
  echo 'Depozitul se publică automat, de hook-ul `post-commit`, la FIECARE commit, cu contract'
  echo 'fast-forward (niciodată `--force`). Pentru audit se folosește oglinda **publică**:'
  echo
  echo "    $URL_PUBLIC"
  echo
  echo '(`origin` e depozitul PRIVAT; nu-l poți clona și nu e nevoie.)'
  echo
  echo '**Commitul de referință al pachetului:**'
  echo
  echo "    $CAP"
  echo
  echo '## Verifică singur, fără să ne crezi'
  echo
  echo "    git ls-remote $URL_PUBLIC refs/heads/main"
  echo
  echo 'Rulat ANONIM (fără chei, `GIT_TERMINAL_PROMPT=0`) la data pachetului, a răspuns:'
  echo
  GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/true timeout 40 git ls-remote "$URL_PUBLIC" \
      refs/heads/main 2>/dev/null | sed 's/^/    /' || echo '    (nu s-a putut interoga acum)'
  echo
  echo '## Cele patru referințe, pe același commit'
  echo
  echo 'Four-way-ul închis de `post-commit` cere ca HEAD, `origin/main`, copia de siguranță a zilei'
  echo 'și **toate** procesele vii de producție să poarte același commit. La data pachetului:'
  echo
  for r in HEAD origin/main public/main "origin/backup/lant-$ZI"; do
    printf '    %-44s %s\n' "$r" "$(git rev-parse "$r" 2>/dev/null || echo '(nerezolvat)')"
  done
  echo
  echo 'Ultimele rânduri ale porții care a produs commitul — inclusiv `FOUR-WAY INCHIS` — sunt în'
  echo '`06_ARTEFACTE/`.'
} > "$RAD/01_COMMIT/OGLINDA_PUBLICA.md"

cp audit/CUM_RULEZI_POARTA.md "$RAD/01_COMMIT/"

# ── 02. REGISTRELE ───────────────────────────────────────────────────────────
for f in PLAN_ARHITECTURA.md DECIZII.md GARZI.md TESTE.md CONFORMITATE.md \
         METODA_VERIFICARE.md LISTA_FUNCTIONALITATI.md VERIFICARE_FUNCTIONALITATI.md \
         PREDARE_LANT.md CLAUDE.md PLAN_LUCRU.md ISTORIC.md; do
  [ -f "$f" ] && cp "$f" "$RAD/02_REGISTRE/$f"
done

# ── 03. CE E PROBAT ──────────────────────────────────────────────────────────
cp audit/deriva_cifrele.py "$RAD/03_PROBAT/"
PYTHONPATH=. ./venv/bin/python audit/deriva_cifrele.py > "$RAD/03_PROBAT/INVENTAR.txt" 2>&1 || true

# ── 04. CE NU E VERIFICAT ────────────────────────────────────────────────────
cp audit/deriva_neverificatul.py audit/CE_NU_SE_POATE_VERIFICA.md audit/scan_secrete.py \
   "$RAD/04_NEVERIFICAT/"
PYTHONPATH=. ./venv/bin/python audit/deriva_neverificatul.py \
   > "$RAD/04_NEVERIFICAT/NEVERIFICAT.txt" 2>&1 || true

# ── 05. FISCAL ───────────────────────────────────────────────────────────────
cp INVENTAR_A.md "$RAD/05_FISCAL/" 2>/dev/null || true
cp INVENTAR_A_OVERLAY.tsv "$RAD/05_FISCAL/" 2>/dev/null || true
{
  echo "CORPUSUL DE ACTE — anaf_surse/, cu amprenta fiecarui fisier"
  echo "=========================================================="
  echo "Actele oficiale ANAF/lege pe care se sprijina valorile din INVENTAR_A.md."
  echo "Amprenta e SHA-256: un act schimbat se vede, nu se presupune."
  echo
  find anaf_surse -maxdepth 2 -type f ! -name '*.pyc' 2>/dev/null | sort | while read -r f; do
    printf '%s  %s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$f"
  done
  echo
  echo "TOTAL: $(find anaf_surse -maxdepth 2 -type f ! -name '*.pyc' 2>/dev/null | wc -l) fisiere."
  echo
  echo "PROVENIENTA fiecaruia (AMPRENTAT / DERIVAT / ADUS / SCRIS ...) e gardata de"
  echo "core/test_provenienta.py si traieste in anaf_surse/PROVENIENTA.json, inclus mai jos."
} > "$RAD/05_FISCAL/CORPUS_ACTE.txt"
cp anaf_surse/PROVENIENTA.json anaf_surse/INDEX.json "$RAD/05_FISCAL/" 2>/dev/null || true

# ── 06. ARTEFACTE BRUTE ──────────────────────────────────────────────────────
cp .poarta_jurnal.log "$RAD/06_ARTEFACTE/poarta_jurnal_COMPLET.log" 2>/dev/null || true
for l in /tmp/commit1.log /tmp/commit3.log /tmp/commit5.log /tmp/commit6.log /tmp/commit7.log \
         /tmp/commit8.log /tmp/commit9.log /tmp/commit10.log /tmp/commit_consemnare.log \
         /tmp/commit_stare.log; do
  [ -f "$l" ] && cp "$l" "$RAD/06_ARTEFACTE/poarta_$(basename "$l")"
done
cp frontend_test/proba_e2_lot_i_d406.json "$RAD/06_ARTEFACTE/" 2>/dev/null || true
cp frontend_test/vizual/acoperire_vizuala.json "$RAD/06_ARTEFACTE/" 2>/dev/null || true
PYTHONPATH=. ./venv/bin/python scripts/raport_b.py \
   > "$RAD/06_ARTEFACTE/raport_b_STAREA_DERIVATA.txt" 2>&1 || true
PYTHONPATH=. ./venv/bin/python scripts/scan_trasee.py --md \
   > "$RAD/06_ARTEFACTE/scan_trasee.txt" 2>&1 || true

# ── 07. RAPOARTELE ULTIMEI SERII ─────────────────────────────────────────────
for d in /tmp/pachet_R59/iconta_R59 /tmp/pachet_R191/iconta_R191 \
         /tmp/pachet_RUTE8/iconta_RUTE8 /tmp/pachet_DUK8/iconta_DUK8; do
  [ -d "$d" ] || continue
  n=$(basename "$d")
  for f in "$d"/RAPORT_*.md "$d"/MASURATORI_*.txt "$d"/COMMIT_*.txt; do
    [ -f "$f" ] && cp "$f" "$RAD/07_RAPOARTE/${n}__$(basename "$f")"
  done
done
[ -f /tmp/pachet_src/RAPORT_115_192.md ] && cp /tmp/pachet_src/RAPORT_115_192.md "$RAD/07_RAPOARTE/"

# ── INDEXUL ──────────────────────────────────────────────────────────────────
cp audit/INDEX.md "$RAD/INDEX.md"

# ── SCANUL DE SECRETE — ULTIMUL pas inainte de manifest, fiindca scaneaza tot ce s-a asamblat ──
PYTHONPATH=. ./venv/bin/python audit/scan_secrete.py "$RAD" --fata-de public/main \
   > "$RAD/04_NEVERIFICAT/SCAN_SECRETE.txt" 2>&1 || true
echo "scan de secrete: $(grep -c . "$RAD/04_NEVERIFICAT/SCAN_SECRETE.txt") randuri; \
TOTAL potriviri = $(grep -oP 'TOTAL potriviri: \K\d+' "$RAD/04_NEVERIFICAT/SCAN_SECRETE.txt")"

# ── MANIFESTUL ───────────────────────────────────────────────────────────────
cd "$RAD"
find . -type f ! -name 'MANIFEST.sha256' | sed 's|^\./||' | sort | while read -r f; do
  sha256sum "$f"
done > MANIFEST.sha256
sha256sum -c MANIFEST.sha256 > /tmp/manifest_check.txt 2>&1 || true
echo "MANIFEST: $(wc -l < MANIFEST.sha256) fisiere; \
verificare: $(grep -c ': OK$' /tmp/manifest_check.txt) OK, \
$(grep -c 'FAILED' /tmp/manifest_check.txt) esuate"

# ── ZIP-UL ───────────────────────────────────────────────────────────────────
cd /tmp/pachet_AUDIT
zip -qr "iconta_AUDIT_$ZI.zip" "iconta_AUDIT_$ZI"
echo
echo "CALEA:   /tmp/pachet_AUDIT/iconta_AUDIT_$ZI.zip"
echo "MARIME:  $(du -h "iconta_AUDIT_$ZI.zip" | cut -f1)"
echo "SHA256:  $(sha256sum "iconta_AUDIT_$ZI.zip" | awk '{print $1}')"
echo "FISIERE: $(find "iconta_AUDIT_$ZI" -type f | wc -l)"
