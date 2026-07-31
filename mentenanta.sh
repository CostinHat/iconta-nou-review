#!/bin/bash
# Comuta mentenanta site-ului iconta.eu.  Uz:  ./mentenanta.sh on | off
#   on  = doar IP-ul allowlisted (Costin, 92.180.8.247) vede aplicatia; restul vad pagina de mentenanta.
#   off = normal pentru toti.
# Mecanism: symlink /etc/nginx/conf.d/maintenance.conf -> /etc/nginx/maintenance/{on,off}.conf + reload.
# Nu reface configuratia - doar comuta symlinkul.
set -e
case "$1" in
  on)  sudo ln -sf /etc/nginx/maintenance/on.conf  /etc/nginx/conf.d/maintenance.conf ;;
  off) sudo ln -sf /etc/nginx/maintenance/off.conf /etc/nginx/conf.d/maintenance.conf ;;
  *)   echo "uz: $0 on|off"; exit 2 ;;
esac
sudo nginx -t && sudo systemctl reload nginx && echo "mentenanta -> $1"
