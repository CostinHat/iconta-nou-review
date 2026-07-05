# -*- coding: utf-8 -*-
"""Incredere + invatare pentru propunerile AI.
Context = cheie text (CUI partener sau descriere normalizata).
Invatare: contul validat de contabil pentru acelasi context devine propunerea viitoare."""
import re


def normalizeaza(text):
    """Descriere -> cheie context: lowercase, fara cifre/punctuatie, max 60."""
    t = re.sub(r"[0-9]+", "", str(text or "").lower())
    t = re.sub(r"[^a-z\u0103\u00e2\u00ee\u0219\u021b ]", " ", t)
    return " ".join(t.split())[:60]


def inregistreaza(conn, schema, context, cont_propus, cont_final):
    """Salveaza rezultatul validarii. corectat = contabilul a schimbat contul."""
    ctx = normalizeaza(context)
    if not ctx:
        return {"ok": False}
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.ai_corectii (context, cont_propus, cont_final, corectat)
                        VALUES (%s,%s,%s,%s)""",
                    (ctx, cont_propus, cont_final, (cont_propus or "") != (cont_final or "")))
    conn.commit()
    return {"ok": True}


def sugestie(conn, schema, context):
    """Intoarce {cont, incredere, istoric} pentru un context.
    incredere: 'sigur' (>=3 validari, 0 corectii recente), 'probabil' (istoric mixt/putin), 'de_verificat' (corectii dese)."""
    ctx = normalizeaza(context)
    if not ctx:
        return None
    with conn.cursor() as cur:
        cur.execute(f"""SELECT cont_final, corectat FROM {schema}.ai_corectii
                        WHERE context=%s ORDER BY id DESC LIMIT 10""", (ctx,))
        rows = cur.fetchall()
    if not rows:
        return None
    return evalueaza([{"cont_final": r[0], "corectat": r[1]} for r in rows])


def evalueaza(istoric):
    """PURA: istoric (recent primul) -> {cont, incredere, validari, corectii}."""
    if not istoric:
        return None
    cont = istoric[0]["cont_final"]
    consecvente = sum(1 for h in istoric if h["cont_final"] == cont)
    corectii = sum(1 for h in istoric if h["corectat"])
    if consecvente >= 3 and not any(h["corectat"] for h in istoric[:3]):
        nivel = "sigur"
    elif corectii >= len(istoric) / 2:
        nivel = "de_verificat"
    else:
        nivel = "probabil"
    return {"cont": cont, "incredere": nivel,
            "validari": len(istoric), "corectii": corectii}
