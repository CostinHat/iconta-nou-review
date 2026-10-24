# -*- coding: utf-8 -*-
"""Incredere + invatare pentru propunerile AI.
Context = cheie text (CUI partener sau descriere normalizata).

Invatare: contul validat de contabil pentru acelasi context devine propunerea viitoare."""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
import re


def normalizeaza(text):
    """Descriere -> cheie context: lowercase, fara cifre/punctuatie, max 60."""
    t = re.sub(r"[0-9]+", "", str(text or "").lower())
    t = re.sub(r"[^a-z\u0103\u00e2\u00ee\u0219\u021b ]", " ", t)
    return " ".join(t.split())[:60]


#: [lotul 12, deficiența 479] conturile de trezorerie (bancă 512x, casă 531x): ele sunt partea ÎNSĂȘI a unei încasări / plăți, nu
#: contrapartida ei. Pe o încasare nota e 5121 = 4111 — „debitul primei linii” învățat de aici era 5121, iar sugestia pentru linia de
#: extras următoare cu aceeași descriere ieșea 5121 = 5121 (F1, 22.10.2026). OMFP 1802/2014, funcțiunea contului 512: „În debitul contului
#: 512 «Conturi curente la bănci» se înregistrează: – disponibilitățile [...] depuse”; contrapartida e contul care se stinge sau se încasează.
TREZORERIE = ("512", "531")


def e_trezorerie(cont):
    return str(cont or "").strip().startswith(TREZORERIE)


def cont_de_invatat(debit, credit):
    """PURĂ. Contul învățat dintr-o linie de notă: contrapartida trezoreriei — creditul, când debitul e bancă / casă (încasarea 5121 = 4111
    învață 4111), altfel debitul (plata 401 = 5121 învață 401, ca până azi). None când și contrapartida e de trezorerie (5121 = 5311)."""
    c = credit if e_trezorerie(debit) else debit
    return None if not str(c or "").strip() or e_trezorerie(c) else str(c).strip()


def inregistreaza(conn, schema, context, cont_propus, cont_final):
    """Salveaza rezultatul validarii. corectat = contabilul a schimbat contul."""
    ctx = normalizeaza(context)
    if not ctx:
        return {"ok": False}
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.ai_corectii (context, cont_propus, cont_final, corectat)
                        VALUES (%s,%s,%s,%s)""",
                    (ctx, cont_propus, cont_final, (cont_propus or "") != (cont_final or "")))
    return {"ok": True}


def sugestie(conn, schema, context):
    """Intoarce {cont, incredere, istoric} pentru un context.
    incredere: 'sigur' (>=3 validari, 0 corectii recente), 'probabil' (istoric mixt/putin), 'de_verificat' (corectii dese)."""
    ctx = normalizeaza(context)
    if not ctx:
        return None
    with conn.cursor() as cur:
        # [479] rândurile învățate înainte de reparație cu contul de trezorerie (5121 de pe încasări) nu sunt o propunere: se sar
        cur.execute(f"""SELECT cont_final, corectat FROM {schema}.ai_corectii
                        WHERE context=%s AND split_part(cont_final, '.', 1) !~ '^(512|531)'
                        ORDER BY id DESC LIMIT 10""", (ctx,))
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
