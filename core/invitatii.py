# -*- coding: utf-8 -*-
"""core/invitatii.py — invitațiile pentru un cont NOU de cabinet (comanda Costin 14.10.2026, pct.3: „Înregistrarea liberă se închide:
în pilot, conturile noi se creează numai prin invitație.”; verbatim în DECIZII „Lotul 2”).

- superadminul invită un EMAIL; tokenul (aleator, 32 de octeți) pleacă numai în link, în bază stă hash-ul lui (sha256);
- invitația e valabilă VALABILITATE_ZILE zile și se folosește O SINGURĂ dată;
- contul se creează numai cu emailul invitat (`consuma`, în aceeași tranzacție cu contul).
Tabela: `public.invitatii_cabinet` (core/migrare_invitatii_cabinet.py). Gard: core/test_invitatii.py.
"""
import datetime
import hashlib
import secrets

from core import afirmatii as _af

VALABILITATE_ZILE = 14

# [15.10.2026, lotul 4] o singură sursă: modul „numai prin invitație” al comutatorului (core/setari_platforma.py)
from core.setari_platforma import MESAJ_NUMAI_INVITATIE as MESAJ_FARA_INVITATIE  # noqa: E402,F401 — re-export: numele vechi al mesajului (teste, contractul P7)


def _hash(token):
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()


def creeaza(cur, email, creat_de, acum=None):
    """Tokenul invitației (se trimite o singură dată, în link). Emailul se normalizează (litere mici, fără spații)."""
    tok = secrets.token_urlsafe(32)
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    cur.execute("INSERT INTO public.invitatii_cabinet (email, token_hash, creat_de, expira_la) VALUES (%s, %s, %s, %s)",
                (str(email).strip().lower(), _hash(tok), creat_de, acum + datetime.timedelta(days=VALABILITATE_ZILE)))
    return tok


#: Regula pe care o încalcă o invitație nefolosibilă (afirmația tipată `neconformitate`, `core/afirmatii.py`).
REGULA = "Invitația e valabilă %d zile, se folosește o singură dată și numai cu emailul invitat." % VALABILITATE_ZILE


def _refuz(cod, motiv, email):
    return _af.afirmatie("neconformitate", "invitatie", motiv, unde=("invitația pentru %s" % email) if email else "linkul primit",
                         regula=REGULA, cod=cod)


def stare(cur, token, acum=None):
    """`{valida, email, refuz}` — fără să consume invitația (ecranul de înregistrare își ia emailul de aici). `refuz` = afirmația
    tipată `neconformitate` (cu `cod`: INEXISTENTA / FOLOSITA / EXPIRATA), sau None când invitația e valabilă."""
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    cur.execute("SELECT email, expira_la, folosita_la FROM public.invitatii_cabinet WHERE token_hash = %s", (_hash(token),))
    r = cur.fetchone()
    if not r:
        return {"valida": False, "email": None, "refuz": _refuz("INEXISTENTA", "Invitația nu există. Folosește linkul din emailul "
                                                                 "primit.", None)}
    email, expira, folosita = r[0], r[1], r[2]
    if folosita is not None:
        return {"valida": False, "email": email, "refuz": _refuz("FOLOSITA", "Invitația a fost folosită deja: contul cabinetului "
                                                                  "există. Intră în cont.", email)}
    if expira < acum:
        return {"valida": False, "email": email, "refuz": _refuz("EXPIRATA", "Invitația a expirat. Cere-ne una nouă la "
                                                                  "contact@iconta.eu.", email)}
    return {"valida": True, "email": email, "refuz": None}


def consuma(cur, token, email, firm_id, acum=None):
    """Marchează invitația folosită pentru contul `firm_id`. `ValueError` cu motivul, dacă nu e validă sau e pentru alt email.
    Rândul se blochează (`FOR UPDATE`): două înregistrări simultane cu același token nu trec amândouă."""
    cur.execute("SELECT id FROM public.invitatii_cabinet WHERE token_hash = %s FOR UPDATE", (_hash(token),))
    s = stare(cur, token, acum)
    if not s["valida"]:
        raise ValueError(s["refuz"]["motiv"])
    if s["email"] != str(email or "").strip().lower():
        raise ValueError("Invitația e pentru alt email (%s). Contul se creează numai cu emailul invitat." % s["email"])
    cur.execute("UPDATE public.invitatii_cabinet SET folosita_la = now(), firm_id = %s WHERE token_hash = %s",
                (firm_id, _hash(token)))


def lista(cur):
    """Invitațiile, cele mai noi întâi: {email, creat_la, expira_la, folosita_la} (fără token, fără hash)."""
    cur.execute("SELECT email, creat_la, expira_la, folosita_la FROM public.invitatii_cabinet ORDER BY creat_la DESC LIMIT 200")
    return [{"email": a, "creat_la": b.isoformat(), "expira_la": c.isoformat(), "folosita_la": d.isoformat() if d else None}
            for a, b, c, d in cur.fetchall()]
