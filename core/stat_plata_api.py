# stat_plata_api.py - Stat de plata lunar + fluturas PDF.
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from core.pdf_fonturi import init_fonturi, font
from core import salarizare

def stat_plata(conn, schema, an, luna):
    """Calcul salarii pentru toti salariatii activi, la data de referinta (an, luna)."""
    ref = date(an, luna, 1)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT id, nume, prenume, salariu_brut, persoane_intretinere, part_time, ore_zi
            FROM {schema}.salariati WHERE activ = true ORDER BY nume, prenume
        """)
        randuri = cur.fetchall()
    # CM-uri pe luna
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT salariat_id, COALESCE(SUM(zile),0), COALESCE(SUM(net),0), COALESCE(SUM(brut_ang+brut_fnuass),0)
            FROM {schema}.concedii_medicale WHERE an = %s AND luna = %s GROUP BY salariat_id
        """, (an, luna))
        cm = {r[0]: {"zile": int(r[1]), "net": float(r[2]), "brut": float(r[3])} for r in cur.fetchall()}
    stat = []
    for sid, nume, prenume, brut, pers, part_time, ore_zi in randuri:
        c_cm = cm.get(sid)
        import calendar as _cal
        zile_luna = sum(1 for z in range(1, _cal.monthrange(an, luna)[1] + 1)
                        if date(an, luna, z).weekday() < 5)
        if c_cm and c_cm["zile"] > 0:
            brut_lucrat = float(brut or 0) * max(zile_luna - c_cm["zile"], 0) / zile_luna
        else:
            brut_lucrat = float(brut or 0)
        calc = salarizare.calcul_salariu(brut_lucrat, persoane=pers or 0, la_data=ref,
                                         norma_intreaga=not part_time,
                                         venit_brut_total=float(brut or 0))
        stat.append({
            "id": sid,
            "nume": f"{nume or ''} {prenume or ''}".strip(),
            "brut": float(calc["brut"]), "cas": float(calc["cas"]),
            "cass": float(calc["cass"]), "impozit": float(calc["impozit"]),
            "deducere": float(calc["deducere"]["total"]),
            "net": float(calc["net"]), "cam": float(calc["cam"]),
            "cas_suprataxa": float(calc.get("cas_suprataxa", 0)),
            "cass_suprataxa": float(calc.get("cass_suprataxa", 0)),
            "cost": float(calc["cost_angajator"]),
            "cm_zile": c_cm["zile"] if c_cm else 0,
            "cm_brut": c_cm["brut"] if c_cm else 0,
        })
    return stat

def fluturas_pdf(conn, schema, salariat_id, an, luna, nume_firma=""):
    """Design System cap.7: reportlab Table, nu drawString manual. Sume in format romanesc."""
    from reportlab.lib.pagesizes import A4 as _A4
    from reportlab.lib.units import mm as _mm
    from reportlab.lib import colors as _colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_RIGHT
    from core.pdf_util import bani as _bani

    ref = date(an, luna, 1)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT nume, prenume, salariu_brut, persoane_intretinere, part_time
            FROM {schema}.salariati WHERE id = %s
        """, (salariat_id,))
        r = cur.fetchone()
    if not r:
        return None
    nume, prenume, brut, pers, part_time = r
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT COALESCE(SUM(zile),0), COALESCE(SUM(net),0), COALESCE(SUM(brut_ang+brut_fnuass),0)
            FROM {schema}.concedii_medicale WHERE salariat_id = %s AND an = %s AND luna = %s
        """, (salariat_id, an, luna))
        zc, cm_net, cm_brut = cur.fetchone()
    import calendar as _cal
    zile_luna = sum(1 for z in range(1, _cal.monthrange(an, luna)[1] + 1)
                    if date(an, luna, z).weekday() < 5)
    brut_lucrat = float(brut or 0) * max(zile_luna - int(zc or 0), 0) / zile_luna if zc else float(brut or 0)
    calc = salarizare.calcul_salariu(brut_lucrat, persoane=pers or 0, la_data=ref,
                                     norma_intreaga=not part_time,
                                     venit_brut_total=float(brut or 0))

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
    st_titlu = ParagraphStyle("titlu", parent=stil["Normal"], fontName=fb, fontSize=14, textColor=ac, leading=17)
    st_meta = ParagraphStyle("meta", parent=stil["Normal"], fontName=fr, fontSize=10, textColor=_colors.HexColor("#555555"))
    st_lbl = ParagraphStyle("lbl", parent=stil["Normal"], fontName=fr, fontSize=10)
    st_val = ParagraphStyle("val", parent=stil["Normal"], fontName=fr, fontSize=10, alignment=TA_RIGHT)
    st_lbl_b = ParagraphStyle("lblb", parent=st_lbl, fontName=fb, fontSize=11)
    st_val_b = ParagraphStyle("valb", parent=st_val, fontName=fb, fontSize=11)

    el = [
        Paragraph(f"Fluturas de salariu \u2014 {luna:02d}/{an}", st_titlu),
        Paragraph(nume_firma, st_meta),
        Paragraph(f"Salariat: {nume or ''} {prenume or ''}", st_meta),
        Spacer(1, 10),
    ]

    linii = [
        ("Salariu brut", calc["brut"]),
        ("Facilitate salariu minim (netaxabil)", calc["facilitate"]),
        ("CAS (25%)", -calc["cas"]),
        ("CASS (10%)", -calc["cass"]),
        ("Deducere personala", calc["deducere"]["total"]),
        ("Impozit pe venit", -calc["impozit"]),
        ("SALARIU NET", calc["net"]),
    ]
    if zc:
        linii.insert(1, (f"Zile concediu medical: {int(zc)}", None))
        linii.insert(len(linii) - 1, ("Indemnizatie CM (neta)", cm_net))

    rows = []
    for eticheta, val in linii:
        bold = eticheta == "SALARIU NET"
        lbl_st = st_lbl_b if bold else st_lbl
        val_st = st_val_b if bold else st_val
        val_txt = _bani(val, "lei") if val is not None else ""
        rows.append([Paragraph(eticheta, lbl_st), Paragraph(val_txt, val_st)])

    tabel = Table(rows, colWidths=[100 * _mm, 40 * _mm])
    n_last = len(rows) - 1
    tabel.setStyle(TableStyle([
        ("LINEABOVE", (0, n_last), (-1, n_last), 1, ac),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    el.append(tabel)
    el.append(Spacer(1, 8))
    el.append(Paragraph(
        f"Cost total angajator (inclusiv CAM 2.25%): {_bani(calc['cost_angajator'], 'lei')}",
        ParagraphStyle("cost", parent=stil["Normal"], fontName=fr, fontSize=9, textColor=_colors.HexColor("#555555")),
    ))
    doc.build(el)
    return buf.getvalue()
