# -*- coding: utf-8 -*-
"""core/contracte_api.py — F147: generare contracte din sabloane (mail-merge).

Firma isi scrie propriul text de contract cu marcaje {{...}}; generarea completeaza datele
partenerului (din clienti) + firmei (firma_profil) si scoate PDF (tiparul adeverinta.py,
DS cap.7 reportlab). NU autoram continut legal. Contractul NU se stocheaza (doar descarcare).
Vocabular de marcaje FIX, verificat la scriere (previne marcaje orfane). Vezi DECIZII.md 17.07.
"""
import re
from io import BytesIO
from datetime import date
from psycopg2.extras import RealDictCursor
from core.pdf_fonturi import init_fonturi, font

# Vocabular FIX de marcaje (marcaj -> descriere pentru UI). Un marcaj in afara listei =
# orfan (ramane necompletat) -> se respinge la scrierea sablonului.
MARCAJE = {
    "partener_nume": "Numele partenerului",
    "partener_cui": "CUI / CNP partener",
    "partener_adresa": "Adresa partenerului",
    "partener_email": "Email partener",
    "partener_telefon": "Telefon partener",
    "firma_nume": "Numele firmei",
    "firma_cui": "CUI firma",
    "firma_adresa": "Adresa firmei",
    "reprezentant": "Reprezentantul firmei",
    "data": "Data curenta (zz.ll.aaaa)",
}

_MARCAJ_RX = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _marcaje_folosite(text):
    return set(_MARCAJ_RX.findall(text or ""))


def lista_sabloane(conn, schema):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, nume, continut FROM {schema}.contracte_sabloane ORDER BY nume")
        return [{"id": r["id"], "nume": r["nume"], "continut": r["continut"]} for r in cur.fetchall()]


def salveaza_sablon(conn, schema, sablon_id, nume, continut, creat_de):
    """Creeaza (sablon_id None) sau actualizeaza un sablon. Vocabular verificat: orice marcaj
    necunoscut -> MARCAJ_INVALID. Nume unic -> NUME_EXISTA. Coduri: NUME_GOL/CONTINUT_GOL."""
    nume = (nume or "").strip()
    continut = (continut or "").strip()
    if not nume:
        return {"ok": False, "cod": "NUME_GOL"}
    if not continut:
        return {"ok": False, "cod": "CONTINUT_GOL"}
    necunoscute = _marcaje_folosite(continut) - set(MARCAJE)
    if necunoscute:
        return {"ok": False, "cod": "MARCAJ_INVALID", "marcaj": sorted(necunoscute)[0]}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id FROM {schema}.contracte_sabloane WHERE nume=%s AND id<>%s",
                    (nume, sablon_id or -1))
        if cur.fetchone():
            return {"ok": False, "cod": "NUME_EXISTA"}
        if sablon_id:
            cur.execute(f"UPDATE {schema}.contracte_sabloane SET nume=%s, continut=%s WHERE id=%s RETURNING id",
                        (nume, continut, sablon_id))
            row = cur.fetchone()
            if not row:
                return {"ok": False, "cod": "INEXISTENT"}
            return {"ok": True, "id": row["id"]}
        cur.execute(f"INSERT INTO {schema}.contracte_sabloane (nume, continut, creat_de) "
                    f"VALUES (%s,%s,%s) RETURNING id", (nume, continut, creat_de))
        return {"ok": True, "id": cur.fetchone()["id"]}


def sterge_sablon(conn, schema, sablon_id):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.contracte_sabloane WHERE id=%s", (sablon_id,))
        return {"ok": cur.rowcount > 0}


def _date_firma(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, patron_nume, declarant_nume FROM firma_profil WHERE id=1")
        f = cur.fetchone() or (None,) * 5
    return {"firma_nume": f[0] or "", "firma_cui": f[1] or "", "firma_adresa": f[2] or "",
            "reprezentant": f[3] or f[4] or ""}


def _date_partener(conn, schema, client_id, manual):
    """Datele partenerului: din clienti (daca client_id) suprascrise de campurile manuale."""
    d = {"partener_nume": "", "partener_cui": "", "partener_adresa": "",
         "partener_email": "", "partener_telefon": ""}
    if client_id:
        with conn.cursor() as cur:
            cur.execute(f"SELECT nume, cui, adresa, email, telefon FROM {schema}.clienti WHERE id=%s",
                        (client_id,))
            c = cur.fetchone()
        if c:
            d.update({"partener_nume": c[0] or "", "partener_cui": c[1] or "",
                      "partener_adresa": c[2] or "", "partener_email": c[3] or "",
                      "partener_telefon": c[4] or ""})
    for k in list(d):
        v = (manual or {}).get(k)
        if v:
            d[k] = v
    return d


def _completeaza(text, date_dict):
    return _MARCAJ_RX.sub(lambda m: str(date_dict.get(m.group(1), m.group(0))), text)


def genereaza_pdf(conn, schema, sablon_id, corp):
    """Genereaza PDF-ul contractului. corp: {client_id?, partener?{...}}. Intoarce bytes,
    sau None daca sablonul nu exista."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT nume, continut FROM {schema}.contracte_sabloane WHERE id=%s", (sablon_id,))
        row = cur.fetchone()
    if not row:
        return None
    _nume, continut = row
    date_dict = {}
    date_dict.update(_date_firma(conn, schema))
    date_dict.update(_date_partener(conn, schema, corp.get("client_id"), corp.get("partener")))
    date_dict["data"] = "%02d.%02d.%04d" % (date.today().day, date.today().month, date.today().year)
    text = _completeaza(continut, date_dict)

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    init_fonturi()
    fr, fb = font("sans")
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm)
    S = getSampleStyleSheet()
    p = ParagraphStyle("p", parent=S["Normal"], fontName=fr, fontSize=11, leading=17)
    from xml.sax.saxutils import escape as _esc
    el = []
    for linie in text.split("\n"):
        if linie.strip():
            el.append(Paragraph(_esc(linie), p))
        else:
            el.append(Spacer(1, 6 * mm))
    doc.build(el)
    return buf.getvalue()
