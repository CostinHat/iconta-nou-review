# -*- coding: utf-8 -*-
"""ETAPA 2 — ajutoarele comune ale probelor de lanț: sesiune, cereri, citirea rândurilor din XML.

Un singur loc pentru ce folosesc toate loturile: tokenul (pe calea aplicației, `sesiune_pentru_user`),
cererea HTTP către instanța probată, și **citirea rândurilor dintr-un XML de declarație** — fiindcă
proba cerută de comandă e pe RÂND și pe SUMĂ, nu pe verdictul validatorului:

    *„DUK verde nu e proba — el confirmă forma; o cifră în rândul greșit trece la fel de bine."*
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/home/costin/iconta_nou")

from core import auth_api, db  # noqa: E402

BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8010")
EMAIL = os.environ.get("PROBA_EMAIL", "patron@prisma-cont.test")


def context(nume_firma):
    """(token, tenant_id, schema) pentru firma dată — nimic scris în cod."""
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (EMAIL,))
            uid = cur.fetchone()[0]
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE nume=%s", (nume_firma,))
            r = cur.fetchone()
            if not r:
                raise SystemExit("firma %r nu există în bază" % nume_firma)
        s = auth_api.sesiune_pentru_user(conn, uid)
        conn.rollback()
    return s["token"], r[0], r[1]


def cere(metoda, cale, corp, tok, timeout=120):
    req = urllib.request.Request(
        BAZA + cale, method=metoda,
        data=json.dumps(corp).encode() if corp is not None else None,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            b = r.read().decode()
            return r.status, (json.loads(b) if b.strip().startswith(("{", "[")) else b)
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        try:
            return e.code, json.loads(b)
        except Exception:  # noqa: BLE001
            return e.code, b[:600]


_ATRIB = re.compile(r'(\b[A-Za-z_][A-Za-z0-9_.]*)\s*=\s*"([^"]*)"')


def randuri_xml(xml):
    """{nume_atribut: valoare} din elementul rădăcină al declarației.

    Declarațiile ANAF își poartă rândurile ca ATRIBUTE pe rădăcină (`R9_1="..."`), nu ca noduri —
    deci citirea e pe atribut, nu pe text. Se întorc TOATE, ca proba să poată cere exact rândul
    despre care a scris așteptarea, și să vadă și ce s-a mișcat pe lângă el.
    """
    cap = xml.split(">", 1)[0] if ">" in xml else xml
    return {k: v for k, v in _ATRIB.findall(cap)}


def numar(v):
    """Valoarea unui rând ca întreg; „" și lipsa înseamnă 0 — dar se deosebesc de zero SCRIS."""
    if v in (None, ""):
        return 0
    try:
        return int(float(str(v).replace(",", ".")))
    except ValueError:
        return None


def diferente(inainte, dupa):
    """{rând: (înainte, după)} — numai ce s-a mișcat. Ce NU s-a mișcat contează la fel de mult:
    o cifră care apare într-un rând la care nu te așteptai e chiar defectul pe care îl caută etapa 2."""
    chei = set(inainte) | set(dupa)
    return {k: (inainte.get(k, "—"), dupa.get(k, "—")) for k in sorted(chei)
            if inainte.get(k) != dupa.get(k)}
