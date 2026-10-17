# -*- coding: utf-8 -*-
"""scripts/whatsapp_meta.py — pașii o singură dată ai contului WhatsApp Business (lotul 7 pct.2.4, comanda Costin 17.10.2026, verbatim în
DECIZII „Lotul 6 închis”): „Înregistrează numărul prin API (PIN-ul ți-l dau eu [...]), webhooks, șabloanele de mesaje pregătite pentru
aprobare.”

Cere în mediu (`~/.iconta/api_keys.env`): `WHATSAPP_TOKEN` (tokenul permanent al unui utilizator de sistem, cu
`whatsapp_business_messaging` + `whatsapp_business_management`). Nimic nu se trimite fără el.

  python scripts/whatsapp_meta.py sabloane            -> arată definițiile (fără trimitere)
  python scripts/whatsapp_meta.py sabloane --trimite  -> le trimite spre aprobare (POST /<WABA>/message_templates)
  python scripts/whatsapp_meta.py inregistreaza <PIN> -> POST /<PHONE_NUMBER_ID>/register (cel mult 10 cereri în 72 de ore)
  python scripts/whatsapp_meta.py aboneaza            -> POST /<WABA>/subscribed_apps (evenimentele contului pe webhook)

Webhook-ul: adresa `https://iconta.eu/whatsapp/webhook` și tokenul de verificare (`WHATSAPP_VERIFY_TOKEN`) se scriu în panoul aplicației
Meta (WhatsApp -> Configuration), câmpul „messages”; semnătura se verifică cu `WHATSAPP_APP_SECRET`.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import whatsapp as wa  # noqa: E402


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "sabloane":
        for s in wa.SABLOANE:
            print(json.dumps(s, ensure_ascii=False, indent=1))
            if "--trimite" in argv:
                print(" ->", wa.trimite_sablon_spre_aprobare(s))
        return 0
    if cmd == "inregistreaza" and len(argv) == 2:
        print(wa.inregistreaza_numarul(argv[1]))
        return 0
    if cmd == "aboneaza":
        print(wa.aboneaza_aplicatia())
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (wa.Neconfigurat, wa.Refuzat, ValueError) as e:
        print("REFUZ: %s" % e)
        sys.exit(1)
