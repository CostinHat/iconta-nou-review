# -*- coding: utf-8 -*-
"""scripts/whatsapp_meta.py — pașii o singură dată ai contului WhatsApp Business (lotul 7 pct.2.4, comanda Costin 17.10.2026, verbatim în
DECIZII „Lotul 6 închis”): „Înregistrează numărul prin API (PIN-ul ți-l dau eu [...]), webhooks, șabloanele de mesaje pregătite pentru
aprobare.”

Cere în mediu (`~/.iconta/api_keys.env`): `WHATSAPP_TOKEN` (tokenul permanent al unui utilizator de sistem, cu
`whatsapp_business_messaging` + `whatsapp_business_management`). Nimic nu se trimite fără el.

  python scripts/whatsapp_meta.py stare               -> starea numărului (numai citire), JSON
  python scripts/whatsapp_meta.py sabloane            -> arată definițiile celor trei șabloane (fără trimitere)
  python scripts/whatsapp_meta.py sabloane --trimite  -> le trimite spre aprobare (POST /<WABA>/message_templates), câte unul, în ordinea
                                                         iconta_alerta_lot, iconta_cod_confirmare, iconta_notificare
  python scripts/whatsapp_meta.py sabloane --stare    -> numele, starea, categoria și limba șabloanelor contului (numai citire)
  python scripts/whatsapp_meta.py inregistreaza       -> POST /<PHONE_NUMBER_ID>/register; PIN-ul de 6 cifre se ia din WHATSAPP_PIN, nu din argumente
  python scripts/whatsapp_meta.py aboneaza            -> POST /<WABA>/subscribed_apps (evenimentele contului pe webhook)
  python scripts/whatsapp_meta.py webhook             -> scrie adresa și tokenul de verificare pentru panoul Meta (WA_WEBHOOK_FISIER, 600) și
                                                         verifică local și public răspunsul la provocarea Meta

`inregistreaza`, `aboneaza` și `sabloane --trimite` au garda de încercări: cel mult o încercare a fiecăreia la 72 de ore (WA_INCERCARI_LOG;
Meta admite 10 cereri de înregistrare în 72 de ore); a doua încercare se refuză înainte de orice cerere.

Webhook-ul: adresa `https://iconta.eu/whatsapp/webhook` și tokenul de verificare (`WHATSAPP_VERIFY_TOKEN`) se scriu în panoul aplicației
Meta (WhatsApp -> Configuration), câmpul „messages”; semnătura se verifică cu `WHATSAPP_APP_SECRET`.
"""
import datetime
import json
import os
import random
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alerta_whatsapp  # noqa: E402
from core import whatsapp as wa  # noqa: E402
from core.common import cfg  # noqa: E402

ADRESA_WEBHOOK = "https://iconta.eu/whatsapp/webhook"
ADRESA_LOCALA = "http://127.0.0.1:8010/whatsapp/webhook"
ORE_GARDA = 72


def _acasa(*parti):
    return os.path.join(os.path.expanduser("~"), *parti)


def _cale_incercari():
    return os.environ.get("WA_INCERCARI_LOG") or _acasa(".iconta", "wa_incercari.log")


def _acum():
    return datetime.datetime.now().astimezone()


def _garda(actiune):
    """Refuză (ValueError -> «REFUZ: …») dacă același tip de acțiune a fost încercat în ultimele 72 de ore."""
    try:
        linii = open(_cale_incercari(), encoding="utf-8").read().splitlines()
    except OSError:
        return
    limita = _acum() - datetime.timedelta(hours=ORE_GARDA)
    for linie in linii:
        camp = linie.split("\t")
        if len(camp) < 2 or camp[1] != actiune:
            continue
        try:
            ora = datetime.datetime.fromisoformat(camp[0])
        except ValueError:
            continue
        if ora.tzinfo is None:
            ora = ora.astimezone()
        if ora > limita:
            raise ValueError("%s încercată la %s; cel mult o încercare la %d de ore (Meta admite 10 cereri de înregistrare în 72 de ore)"
                             % (actiune, camp[0], ORE_GARDA))


def _noteaza(actiune, rezultat, text):
    """Rândul încercării (ajunsă la Meta): «<ora ISO>\\t<acțiune>\\t<ok|refuz>\\t<rezultat scurt fără secrete>»."""
    text = alerta_whatsapp._ascunde(" ".join(str(text).split()))[:100]
    cale = _cale_incercari()
    os.makedirs(os.path.dirname(cale) or ".", exist_ok=True)
    with open(cale, "a", encoding="utf-8") as f:
        f.write("%s\t%s\t%s\t%s\n" % (_acum().isoformat(timespec="seconds"), actiune, rezultat, text))


def _incercare(actiune, functie):
    """Garda, apoi apelul; o încercare ajunsă la Meta (reușită sau `Refuzat`) intră în fișier, una căzută înainte (`Neconfigurat`) nu."""
    _garda(actiune)
    try:
        r = functie()
    except wa.Refuzat as e:
        _noteaza(actiune, "refuz", e)
        raise
    _noteaza(actiune, "ok", json.dumps(r, ensure_ascii=False) if isinstance(r, (dict, list)) else r)
    return r


def _pin():
    pin = cfg("WHATSAPP_PIN")
    if not re.fullmatch(r"[0-9]{6}", pin):
        raise ValueError("PIN-ul din WHATSAPP_PIN lipsește sau nu are exact 6 cifre")
    return pin


def _toate_sabloanele():
    return list(alerta_whatsapp.SABLOANE_ALERTA) + list(wa.SABLOANE)


def _sabloane_stare():
    token = cfg("WHATSAPP_TOKEN")
    if not token:
        raise wa.Neconfigurat("Trimiterea pe WhatsApp nu e configurată pe server.")
    url = "https://graph.facebook.com/%s/%s/message_templates?fields=name,status,category,language&limit=50" % (
        wa.VERSIUNE_GRAPH, cfg("WHATSAPP_WABA_ID", wa.WABA_ID))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": "Bearer " + token}), timeout=15) as r:
            date = json.load(r)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", {})
        except ValueError:
            err = {}
        raise wa._refuz(e.code, err)
    return ["%s %s %s %s" % (s.get("name"), s.get("status"), s.get("category"), s.get("language")) for s in date.get("data", [])]


def _linie_sablon(nume, e=None):
    if e is None:
        return "%s ok" % nume
    m = re.search(r"HTTP (\d+), cod ([0-9/?]+)", str(e))
    return "%s refuz HTTP %s cod %s" % (nume, m.group(1) if m else "?", m.group(2) if m else "?")


def _trimite_sabloane():
    """Cele trei șabloane, pe rând; un refuz nu oprește trimiterea celorlalte. -> liniile rezultatelor."""
    linii, refuzuri = [], 0
    for s in _toate_sabloanele():
        try:
            wa.trimite_sablon_spre_aprobare(s)
            linii.append(_linie_sablon(s["name"]))
        except wa.Refuzat as e:
            refuzuri += 1
            linii.append(_linie_sablon(s["name"], e))
    cale = os.environ.get("WA_SABLOANE_TRIMISE") or _acasa(".iconta", "sabloane_trimise.txt")
    os.makedirs(os.path.dirname(cale) or ".", exist_ok=True)
    with open(cale, "w", encoding="utf-8") as f:
        f.write("\n".join(linii) + "\n")
    for l in linii:
        print(l)
    if refuzuri:
        return "refuz", "; ".join(linii)
    return "ok", "; ".join(linii)


def _get(url):
    """-> (cod HTTP, corp) al unui GET; `None` ca cod dacă nu s-a ajuns la server."""
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError):
        return None, ""


def _webhook():
    token = cfg("WHATSAPP_VERIFY_TOKEN")
    if not token:
        raise ValueError("WHATSAPP_VERIFY_TOKEN lipsește")
    cale = os.environ.get("WA_WEBHOOK_FISIER") or _acasa("ghid_incoming", "whatsapp_webhook_pentru_costin.txt")
    fd = os.open(cale, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("%s\n%s\n" % (ADRESA_WEBHOOK, token))
    for eticheta, baza in (("locală", ADRESA_LOCALA), ("publică", ADRESA_WEBHOOK)):
        provocare = str(random.randint(10000000, 99999999))
        cod, corp = _get("%s?%s" % (baza, urllib.parse.urlencode({"hub.mode": "subscribe", "hub.verify_token": token, "hub.challenge": provocare})))
        print("verificare %s: %s" % (eticheta, "ok" if cod == 200 and corp.strip() == provocare else "refuz %s" % (cod if cod is not None else "-")))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "stare" and len(argv) == 1:
        print(json.dumps(wa.stare_numar(), ensure_ascii=False, indent=1))
        return 0
    if cmd == "sabloane":
        if "--stare" in argv:
            for l in _sabloane_stare():
                print(l)
            return 0
        if "--trimite" in argv:
            _garda("sabloane --trimite")
            rez, text = _trimite_sabloane()
            _noteaza("sabloane --trimite", rez, text)
            return 0
        for s in _toate_sabloanele():
            print(json.dumps(s, ensure_ascii=False, indent=1))
        return 0
    if cmd == "inregistreaza":
        if len(argv) > 1:
            raise ValueError("PIN-ul se ia din WHATSAPP_PIN, nu din argumente")
        pin = _pin()
        print(_incercare("inregistreaza", lambda: wa.inregistreaza_numarul(pin)))
        return 0
    if cmd == "aboneaza":
        print(_incercare("aboneaza", wa.aboneaza_aplicatia))
        return 0
    if cmd == "webhook":
        _webhook()
        return 0
    print(__doc__)
    return 2


def cli(argv):
    try:
        return main(argv)
    except (wa.Neconfigurat, wa.Refuzat, ValueError) as e:
        print("REFUZ: %s" % alerta_whatsapp._ascunde(str(e)))
        return 1


if __name__ == "__main__":
    sys.exit(cli(sys.argv[1:]))
