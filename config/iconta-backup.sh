#!/bin/bash
# [iconta_backup_v2] backup zilnic iconta_v2:
#   1) LOCAL (SACRU) - pg_dump -Fc in /var/backups/iconta, retentie 7 zile. Ruleaza
#      MEREU si primul; esecul lui pica scriptul (vizibil in systemd), cum trebuie.
#   2) OFF-SITE - copie pe Hetzner Storage Box prin rsync-over-SSH (cheie dedicata,
#      port 23), retentie 30 zile (mai lunga ca local). FAIL-SAFE: orice esec off-site
#      NU pica backup-ul local; se numara esecurile consecutive; la N -> email Brevo.
#   Off-site care esueaza TACIT e mai rau decat lipsa lui -> se logheaza + alerteaza.
set -euo pipefail

DIR=/var/backups/iconta
TS=$(date +%Y%m%d_%H%M%S)
OUT="$DIR/iconta_v2_$TS.dump"

# ---- 1) BACKUP LOCAL (SACRU) ----
pg_dump -d iconta_v2 -Fc -f "$OUT"
find "$DIR" -name 'iconta_v2_*.dump' -mtime +7 -delete
echo "$(date -Is) backup LOCAL OK: $OUT ($(du -h "$OUT" | cut -f1))"

# ---- 2) COPIE OFF-SITE (fail-safe) ----
SB_KEY=/var/lib/postgresql/.ssh/iconta-storagebox
SB_HOST=u634788@u634788.your-storagebox.de
SB_PORT=23
SB_DIR=iconta/db
SB_RETENTIE_ZILE=30
FAIL_FILE="$DIR/.offsite_esecuri"
FAIL_PRAG=2   # email dupa N esecuri consecutive
SSH_OPT="-p${SB_PORT} -i ${SB_KEY} -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=20 -o UserKnownHostsFile=/var/lib/postgresql/.ssh/known_hosts"

_sftp() { sftp -P"${SB_PORT}" -i "${SB_KEY}" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/var/lib/postgresql/.ssh/known_hosts "${SB_HOST}" 2>/dev/null; }

offsite() {
  local baza; baza=$(basename "$OUT")
  # upload dump nou
  rsync -a -e "ssh ${SSH_OPT}" "$OUT" "${SB_HOST}:${SB_DIR}/" || return 1
  # confirmare remote: fisierul apare + dimensiune (coloana 5 din ls -l)
  local linie; linie=$(printf 'ls -l %s\n' "${SB_DIR}" | _sftp | grep -F "$baza" || true)
  [ -n "$linie" ] || return 1
  local dim; dim=$(echo "$linie" | awk '{print $5}')
  echo "$(date -Is) backup OFF-SITE OK: ${SB_DIR}/${baza} (remote ${dim} octeti)"
  # retentie off-site 30 zile: sterge dupa DATA din NUME (nu mtime remote, pe care
  # shell-ul limitat Storage Box nu-l expune fiabil prin find)
  local cutoff; cutoff=$(date -d "-${SB_RETENTIE_ZILE} days" +%Y%m%d)
  local nume; nume=$(printf 'ls -1 %s\n' "${SB_DIR}" | _sftp | grep -oE 'iconta_v2_[0-9]{8}_[0-9]{6}\.dump' || true)
  local rmbatch=""
  for f in $nume; do
    local d; d=$(echo "$f" | sed -E 's/iconta_v2_([0-9]{8})_.*/\1/')
    if [ "$d" -lt "$cutoff" ]; then rmbatch+="rm ${SB_DIR}/${f}"$'\n'; fi
  done
  if [ -n "$rmbatch" ]; then
    printf '%s' "$rmbatch" | _sftp || true
    echo "$(date -Is) retentie off-site: sters $(printf '%s' "$rmbatch" | grep -c '^rm') dump-uri > ${SB_RETENTIE_ZILE}z"
  fi
  return 0
}

# `if offsite` suspenda set -e in corpul functiei -> esecul off-site NU pica scriptul
if offsite; then
  echo 0 > "$FAIL_FILE"
else
  n=$(( $(cat "$FAIL_FILE" 2>/dev/null || echo 0) + 1 ))
  echo "$n" > "$FAIL_FILE"
  echo "$(date -Is) backup OFF-SITE ESUAT (esec consecutiv #${n}) - LOCAL e OK" >&2
  # FAZA 2: email Brevo la N esecuri consecutive (acelasi canal ca core/observare.py).
  # BREVO_API_KEY vine prin EnvironmentFile in systemd (citit ca root, injectat inainte
  # de drop la postgres). curl direct = acelasi endpoint Brevo, fara dependenta de codul
  # app pe care userul postgres nu-l poate accesa.
  if [ "$n" -ge "$FAIL_PRAG" ] && [ -n "${BREVO_API_KEY:-}" ]; then
    curl -s -X POST https://api.brevo.com/v3/smtp/email \
      -H "api-key: ${BREVO_API_KEY}" -H "content-type: application/json" \
      -d "{\"sender\":{\"email\":\"contact@iconta.eu\",\"name\":\"iConta Alerte\"},\"to\":[{\"email\":\"${ICONTA_ALERTA_EMAIL:-contact@iconta.eu}\"}],\"subject\":\"[iConta] Backup off-site esuat (${n} rulari consecutive)\",\"textContent\":\"Backup-ul off-site catre Storage Box a esuat ${n} rulari consecutive. Backup-ul LOCAL functioneaza (nu s-au pierdut date). Verifica cheia SSH / reteaua / spatiul Storage Box.\"}" >/dev/null 2>&1 \
      && echo "$(date -Is) alerta email trimisa (esec off-site #${n})" \
      || echo "$(date -Is) alerta email NETRIMISA (Brevo indisponibil)" >&2
  fi
fi
