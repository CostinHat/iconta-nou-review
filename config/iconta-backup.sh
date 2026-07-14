#!/bin/bash
# [iconta_backup_v1] dump zilnic iconta_v2, retentie 7 zile
set -euo pipefail
DIR=/var/backups/iconta
TS=$(date +%Y%m%d_%H%M%S)
OUT="$DIR/iconta_v2_$TS.dump"
pg_dump -d iconta_v2 -Fc -f "$OUT"
# retentie: sterge dump-urile mai vechi de 7 zile
find "$DIR" -name 'iconta_v2_*.dump' -mtime +7 -delete
echo "$(date -Is) backup OK: $OUT ($(du -h "$OUT" | cut -f1))"
