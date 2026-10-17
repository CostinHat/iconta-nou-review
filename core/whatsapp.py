# -*- coding: utf-8 -*-
"""core/whatsapp.py — WhatsApp Cloud API (Meta): trimiterea unui șablon, codul de confirmare a numărului, webhook-ul.

Comanda Costin 17.10.2026, lotul 7 pct.2.1 și 2.4 (verbatim în DECIZII „Lotul 6 închis”): „Notificări WhatsApp [...]: mesaj scurt, fără
conținut fiscal, cu link în aplicație.” Contul: WhatsApp Business 1658480942307403, numărul +40 759 638 499, Phone Number ID
1396364810224559, aplicația 1815754089771073.

Sursa (documentația Meta, citită 17.10.2026):
- trimiterea: `POST https://graph.facebook.com/<v>/<PHONE_NUMBER_ID>/messages`, `messaging_product: "whatsapp"`, `type: "template"`;
  șablonul de autentificare cu buton „copiază codul” primește codul ȘI în corp, ȘI în butonul `url` (`index: "0"`);
- înregistrarea numărului: `POST /<PHONE_NUMBER_ID>/register` cu `messaging_product` și `pin` (6 cifre; cel mult 10 cereri în 72 de ore);
- webhook-ul: verificarea `hub.mode` / `hub.verify_token` / `hub.challenge`; semnătura `X-Hub-Signature-256: sha256=<HMAC-SHA256 al
  corpului cu App Secret>`; răspunsul 200.

Configurare (`~/.iconta/api_keys.env`, NIMIC în cod): `WHATSAPP_TOKEN` (tokenul permanent al unui utilizator de sistem, cu
`whatsapp_business_messaging` + `whatsapp_business_management`), `WHATSAPP_APP_SECRET` (semnătura webhook-ului), `WHATSAPP_VERIFY_TOKEN`
(ales de noi, scris și în panoul aplicației). Fără token, `configurat()` e fals și trimiterea refuză NUMIT (`Neconfigurat`) — notificarea
pleacă atunci pe email (`core/notificari.py`), nu se pierde.
"""
import hashlib
import hmac
import json
import re
import urllib.error
import urllib.request

from core.common import cfg

VERSIUNE_GRAPH = "v25.0"
PHONE_NUMBER_ID = "1396364810224559"
WABA_ID = "1658480942307403"
APP_ID = "1815754089771073"
NUMAR_AFISAT = "+40 759 638 499"

#: șabloanele (numele și limba) — definițiile complete, pentru aprobare, în `SABLOANE`
SABLON_COD = "iconta_cod_confirmare"
SABLON_NOTIFICARE = "iconta_notificare"
LIMBA = "ro"
#: minutele de valabilitate ale codului (subsolul șablonului de autentificare și expirarea din `telefon_coduri`)
COD_MINUTE = 10

#: definițiile trimise spre aprobare (`POST /<WABA_ID>/message_templates`, `scripts/whatsapp_meta.py sabloane`). Notificarea e UTILITY:
#: o etichetă scurtă, fără conținut fiscal (ce s-a întâmplat, nu cifre), și butonul spre locul din aplicație. Codul e AUTHENTICATION
#: (textul corpului îl fixează Meta: „<cod> is your verification code”, în limba șablonului).
SABLOANE = [
    {"name": SABLON_COD, "language": LIMBA, "category": "AUTHENTICATION",
     "components": [{"type": "BODY", "add_security_recommendation": True},
                    {"type": "FOOTER", "code_expiration_minutes": COD_MINUTE},
                    {"type": "BUTTONS", "buttons": [{"type": "OTP", "otp_type": "COPY_CODE", "text": "Copiază codul"}]}]},
    {"name": SABLON_NOTIFICARE, "language": LIMBA, "category": "UTILITY",
     "components": [{"type": "BODY", "text": "Ai o notificare nouă în iConta.eu: {{1}}. Detaliile sunt în aplicație.",
                     "example": {"body_text": [["o sesizare nouă de la un cabinet"]]}},
                    {"type": "BUTTONS", "buttons": [{"type": "URL", "text": "Deschide iConta.eu", "url": "https://iconta.eu/deschide/{{1}}",
                                                     "example": ["https://iconta.eu/deschide/raportari"]}]}]},
]


class Neconfigurat(RuntimeError):
    """Lipsește tokenul (sau secretul) — trimiterea nu se încearcă."""


class Refuzat(RuntimeError):
    """Meta a refuzat cererea (cod HTTP + mesajul ei)."""


def configurat():
    return bool(cfg("WHATSAPP_TOKEN"))


def _pnid():
    return cfg("WHATSAPP_PHONE_NUMBER_ID", PHONE_NUMBER_ID)


def _cere(cale, corp):
    token = cfg("WHATSAPP_TOKEN")
    if not token:
        raise Neconfigurat("Trimiterea pe WhatsApp nu e configurată pe server.")
    req = urllib.request.Request("https://graph.facebook.com/%s/%s" % (VERSIUNE_GRAPH, cale), data=json.dumps(corp).encode(),
                                 headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", {})
        except ValueError:
            err = {}
        raise Refuzat("Meta a refuzat cererea (HTTP %d, cod %s): %s" % (e.code, err.get("code", "?"), err.get("message", "")[:300]))


def normalizeaza(telefon):
    """PURĂ. Numărul în forma internațională `+<cod țară><număr>`, sau None dacă nu e un număr de telefon. Numerele românești se pot
    scrie local (07xx xxx xxx): primesc +40. Spațiile, punctele, cratimele și parantezele se scot."""
    t = re.sub(r"[\s.\-()/]", "", telefon or "")
    if t.startswith("00"):
        t = "+" + t[2:]
    elif re.fullmatch(r"0[1-9][0-9]{8}", t):
        t = "+40" + t[1:]
    return t if re.fullmatch(r"\+[1-9][0-9]{7,14}", t) else None


def _mesaj_id(r):
    return ((r or {}).get("messages") or [{}])[0].get("id")


def trimite_cod(telefon, cod):
    """Codul de confirmare a numărului (șablonul de autentificare). Întoarce id-ul mesajului."""
    p = [{"type": "text", "text": cod}]
    return _mesaj_id(_cere("%s/messages" % _pnid(), {
        "messaging_product": "whatsapp", "recipient_type": "individual", "to": telefon, "type": "template",
        "template": {"name": SABLON_COD, "language": {"code": LIMBA},
                     "components": [{"type": "body", "parameters": p},
                                    {"type": "button", "sub_type": "url", "index": "0", "parameters": p}]}}))


def trimite_notificare(telefon, eticheta, cheie):
    """Notificarea scurtă: eticheta (fără conținut fiscal) + butonul spre `https://iconta.eu/deschide/<cheie>`.
    Întoarce id-ul mesajului."""
    return _mesaj_id(_cere("%s/messages" % _pnid(), {
        "messaging_product": "whatsapp", "recipient_type": "individual", "to": telefon, "type": "template",
        "template": {"name": SABLON_NOTIFICARE, "language": {"code": LIMBA},
                     "components": [{"type": "body", "parameters": [{"type": "text", "text": eticheta}]},
                                    {"type": "button", "sub_type": "url", "index": "0",
                                     "parameters": [{"type": "text", "text": cheie}]}]}}))


def inregistreaza_numarul(pin):
    """`POST /<PHONE_NUMBER_ID>/register` — o singură dată, cu PIN-ul de 6 cifre (Costin)."""
    if not re.fullmatch(r"[0-9]{6}", pin or ""):
        raise ValueError("PIN-ul are exact 6 cifre")
    return _cere("%s/register" % _pnid(), {"messaging_product": "whatsapp", "pin": pin})


def trimite_sablon_spre_aprobare(definitie):
    """`POST /<WABA_ID>/message_templates` — șablonul intră în revizuirea Meta."""
    return _cere("%s/message_templates" % cfg("WHATSAPP_WABA_ID", WABA_ID), definitie)


def aboneaza_aplicatia():
    """`POST /<WABA_ID>/subscribed_apps` — aplicația primește evenimentele contului (stările mesajelor) pe webhook."""
    return _cere("%s/subscribed_apps" % cfg("WHATSAPP_WABA_ID", WABA_ID), {})


def verificare_webhook(mod, token, provocare):
    """Răspunsul la verificarea webhook-ului: `provocare` dacă tokenul e al nostru, altfel None (refuz)."""
    asteptat = cfg("WHATSAPP_VERIFY_TOKEN")
    if mod == "subscribe" and asteptat and hmac.compare_digest(token or "", asteptat):
        return provocare
    return None


def semnatura_valida(corp, antet):
    """`X-Hub-Signature-256` = `sha256=` + HMAC-SHA256(corp, App Secret). Fără secret configurat: nevalidă (fail-closed)."""
    secret = cfg("WHATSAPP_APP_SECRET")
    if not secret or not (antet or "").startswith("sha256="):
        return False
    calculat = hmac.new(secret.encode(), corp, hashlib.sha256).hexdigest()
    return hmac.compare_digest(calculat, antet[len("sha256="):])


#: stările Meta -> stările jurnalului (`notificari_jurnal.stare`)
STARI = {"sent": "trimis", "delivered": "livrat", "read": "citit", "failed": "esuat"}


def stari_din_webhook(payload):
    """PURĂ. [(id mesaj, stare jurnal, detaliu)] din notificarea webhook-ului (`entry[].changes[].value.statuses[]`)."""
    out = []
    for e in (payload or {}).get("entry") or []:
        for ch in e.get("changes") or []:
            for s in (ch.get("value") or {}).get("statuses") or []:
                stare = STARI.get(s.get("status"))
                if stare and s.get("id"):
                    err = (s.get("errors") or [{}])[0]
                    detaliu = ("%s %s" % (err.get("code", ""), err.get("title") or err.get("message") or "")).strip() or None
                    out.append((s["id"], stare, detaliu))
    return out
