# documente_api.py - Documente portal client: balanta PDF generata automat + declaratii depuse.
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from core.pdf_fonturi import init_fonturi, font

def luni_disponibile(conn, schema):
    """Lunile cu miscari contabile, desc."""
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT DISTINCT date_trunc('month', i.data)::date AS luna
            FROM {schema}.inregistrari i
            ORDER BY luna DESC
        """)
        return [r[0].isoformat() for r in cur.fetchall()]

def balanta(conn, schema, an, luna):
    """Balanta: sold initial + rulaje cumulate pana la finalul lunii (an, luna)."""
    sfarsit = date(an + (luna == 12), (luna % 12) + 1, 1)
    with conn.cursor() as cur:
        cur.execute(f"""
            WITH si AS (
                SELECT cont, MAX(denumire) AS denumire,
                       SUM(sold_debitor) AS sd, SUM(sold_creditor) AS sc
                FROM {schema}.solduri_initiale GROUP BY cont
            ),
            rulaje AS (
                SELECT l.cont_debit AS cont, SUM(l.suma) AS deb, 0::numeric AS cred
                FROM {schema}.inregistrari_linii l
                JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                WHERE i.data < %s GROUP BY l.cont_debit
                UNION ALL
                SELECT l.cont_credit, 0, SUM(l.suma)
                FROM {schema}.inregistrari_linii l
                JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                WHERE i.data < %s GROUP BY l.cont_credit
            ),
            r AS (SELECT cont, SUM(deb) AS deb, SUM(cred) AS cred FROM rulaje GROUP BY cont)
            SELECT COALESCE(si.cont, r.cont) AS cont,
                   COALESCE(si.denumire, pc.denumire, '') AS denumire,
                   COALESCE(si.sd,0) AS sd, COALESCE(si.sc,0) AS sc,
                   COALESCE(r.deb,0) AS deb, COALESCE(r.cred,0) AS cred
            FROM si FULL OUTER JOIN r ON r.cont = si.cont
            LEFT JOIN {schema}.plan_conturi pc ON pc.simbol = COALESCE(si.cont, r.cont)
            ORDER BY 1
        """, (sfarsit, sfarsit))
        randuri = []
        for cont, den, sd, sc, deb, cred in cur.fetchall():
            tsd = float(sd) + float(deb)
            tsc = float(sc) + float(cred)
            fin_d = tsd - tsc if tsd > tsc else 0
            fin_c = tsc - tsd if tsc > tsd else 0
            if not den:
                from core.plan_omfp import denumire_omfp
                den = denumire_omfp(cont)
            randuri.append({"cont": cont, "denumire": den,
                            "si_d": float(sd), "si_c": float(sc),
                            "rul_d": float(deb), "rul_c": float(cred),
                            "sf_d": round(fin_d, 2), "sf_c": round(fin_c, 2)})
        return randuri

# Cele trei perechi pe care o balanta de verificare trebuie sa le inchida. Constanta, nu literale
# imprastiate: gardul citeste MULTIMEA, nu cauta un sir intr-un text (METODA §23).
PERECHI_BALANTA = (("sold initial", "si_d", "si_c"),
                   ("rulaje", "rul_d", "rul_c"),
                   ("sold final", "sf_d", "sf_c"))

# Sub un ban nu e o divergenta, e zgomot de virgula mobila: sumele se aduna din float-uri.
TOLERANTA_BALANTA = 0.01


def totaluri_balanta(randuri):
    """Totalurile pe cele sase coloane. O SINGURA sursa - le citesc si PDF-ul, si ruta de date.

    Erau calculate inauntrul lui `balanta_pdf`, deci existau numai pe hartie. A doua adunare, scrisa
    in JS pentru ecran, ar fi fost al doilea calcul al aceluiasi lucru - clasa pe care fluturasul a
    platit-o deja (vezi `stat_plata_api.rand_fluturas`).
    """
    return {c: round(sum(float(r.get(c) or 0) for r in randuri), 2)
            for c in ("si_d", "si_c", "rul_d", "rul_c", "sf_d", "sf_c")}


def inchidere_balanta(randuri):
    """„Se inchide balanta?" - ca OBIECT cu atribute, nu ca propozitie (DS cap.25.5).

    TREI stari, nu doua, si a treia e cea care conteaza: pe o balanta FARA RANDURI nu se poate
    spune ca „se inchide" - nu s-a verificat nimic. Un necunoscut nu se rotunjeste la „stiu ca da"
    mai putin decat la „stiu ca nu" (interdictia 32).

    Egalitatile sunt cele din norma: debitul si creditul se inchid pe soldul initial, pe rulaje si
    pe soldul final. Ce intoarce e destul ca omul sa VADA de ce, nu doar verdictul: fiecare pereche
    isi poarta cele doua sume si diferenta lor.
    """
    tot = totaluri_balanta(randuri)
    perechi = [{"ce": ce, "debit": tot[d], "credit": tot[c],
                "diferenta": round(tot[d] - tot[c], 2),
                "inchisa": abs(tot[d] - tot[c]) < TOLERANTA_BALANTA}
               for ce, d, c in PERECHI_BALANTA]
    if not randuri:
        stare = "nimic_de_verificat"
    elif all(p["inchisa"] for p in perechi):
        stare = "se_inchide"
    else:
        stare = "nu_se_inchide"
    return {"stare": stare, "perechi": perechi, "randuri": len(randuri)}


def balanta_pdf(conn, schema, an, luna, nume_firma=""):
    """Design System cap.7: reportlab Table cu colWidths explicite (ca factura_pdf.py),
    nu drawString manual. Sume in format romanesc via pdf_util.bani()."""
    from reportlab.lib.pagesizes import A4 as _A4
    from reportlab.lib.units import mm as _mm
    from reportlab.lib import colors as _colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT
    from core.pdf_util import bani as _bani

    randuri = balanta(conn, schema, an, luna)
    with conn.cursor() as _cur:
        _cur.execute(f"SELECT culoare_factura, font_factura FROM {schema}.firma_profil WHERE id = 1")
        _prof = _cur.fetchone()
    _cul_profil, _font_profil = (_prof if _prof else (None, None))
    init_fonturi()
    fr, fb = font(_font_profil or "sans")
    try:
        ac = _colors.HexColor(_cul_profil or "#1d4ed8")
    except Exception:
        ac = _colors.HexColor("#1d4ed8")

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=_A4,
        leftMargin=18 * _mm, rightMargin=18 * _mm,
        topMargin=16 * _mm, bottomMargin=16 * _mm,
    )
    stil = getSampleStyleSheet()
    st_titlu = ParagraphStyle("titlu", parent=stil["Normal"], fontName=fb, fontSize=13, textColor=ac, leading=16)
    st_meta = ParagraphStyle("meta", parent=stil["Normal"], fontName=fr, fontSize=10, textColor=_colors.HexColor("#555555"))
    st_cell = ParagraphStyle("cell", parent=stil["Normal"], fontName=fr, fontSize=7.5, leading=9)
    st_cell_r = ParagraphStyle("cellr", parent=st_cell, alignment=TA_RIGHT)
    st_cap = ParagraphStyle("cap", parent=stil["Normal"], fontName=fb, fontSize=8, textColor=_colors.white)
    st_cap_r = ParagraphStyle("capr", parent=st_cap, alignment=TA_RIGHT)

    el = [
        Paragraph(f"Balan\u021ba de verificare \u2014 {luna:02d}/{an}", st_titlu),
        Paragraph(nume_firma, st_meta),
        Spacer(1, 8),
    ]

    cap = ["Cont", "Denumire", "SI D", "SI C", "Rulaj D", "Rulaj C", "SF D", "SF C"]
    date_tab = [[Paragraph(c, st_cap) if i < 2 else Paragraph(c, st_cap_r) for i, c in enumerate(cap)]]
    _t = totaluri_balanta(randuri)  # sursa unica: aceleasi totaluri le vede si ecranul
    tot = [_t["si_d"], _t["si_c"], _t["rul_d"], _t["rul_c"], _t["sf_d"], _t["sf_c"]]
    for r in randuri:
        vals = [r["si_d"], r["si_c"], r["rul_d"], r["rul_c"], r["sf_d"], r["sf_c"]]
        date_tab.append([
            Paragraph(str(r["cont"]), st_cell),
            Paragraph((r["denumire"] or "")[:42], st_cell),
        ] + [Paragraph(_bani(v), st_cell_r) for v in vals])
    date_tab.append([
        Paragraph("", st_cell), Paragraph("TOTAL", ParagraphStyle("totlbl", parent=st_cell, fontName=fb)),
    ] + [Paragraph(_bani(v), ParagraphStyle("totval", parent=st_cell_r, fontName=fb)) for v in tot])

    tabel = Table(date_tab, colWidths=[20 * _mm, 55 * _mm, 20 * _mm, 20 * _mm, 20 * _mm, 20 * _mm, 20 * _mm, 20 * _mm], repeatRows=1)
    n_last = len(date_tab) - 1
    tabel.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ac),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, _colors.HexColor("#dddddd")),
        ("LINEABOVE", (0, n_last), (-1, n_last), 1, ac),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    el.append(tabel)
    doc.build(el)
    return buf.getvalue()

def declaratii_depuse(conn, tenant_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT an, luna, tip, data_depunere
            FROM public.declaratii_depuse_curente
            WHERE tenant_id = %s
            ORDER BY an DESC, luna DESC, tip
        """, (tenant_id,))
        return [{"an": a, "luna": l, "tip": t, "data": d.isoformat()} for a, l, t, d in cur.fetchall()]
