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
        calc = salarizare.calcul_salariu(brut_lucrat, persoane=pers or 0, la_data=ref)
        stat.append({
            "id": sid,
            "nume": f"{nume or ''} {prenume or ''}".strip(),
            "brut": float(calc["brut"]), "cas": float(calc["cas"]),
            "cass": float(calc["cass"]), "impozit": float(calc["impozit"]),
            "deducere": float(calc["deducere"]["total"]),
            "net": float(calc["net"]), "cam": float(calc["cam"]),
            "cost": float(calc["cost_angajator"]),
            "cm_zile": c_cm["zile"] if c_cm else 0,
            "cm_brut": c_cm["brut"] if c_cm else 0,
        })
    return stat

def fluturas_pdf(conn, schema, salariat_id, an, luna, nume_firma=""):
    ref = date(an, luna, 1)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT nume, prenume, salariu_brut, persoane_intretinere
            FROM {schema}.salariati WHERE id = %s
        """, (salariat_id,))
        r = cur.fetchone()
    if not r:
        return None
    nume, prenume, brut, pers = r
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
    calc = salarizare.calcul_salariu(brut_lucrat, persoane=pers or 0, la_data=ref)
    init_fonturi()
    fr, fb = font("sans")
    buf = BytesIO()
    cnv = canvas.Canvas(buf, pagesize=A4)
    lat, inalt = A4
    y = inalt - 25*mm
    cnv.setFont(fb, 14)
    cnv.drawString(20*mm, y, f"Fluturas de salariu — {luna:02d}/{an}")
    y -= 7*mm
    cnv.setFont(fr, 10)
    cnv.drawString(20*mm, y, nume_firma)
    y -= 6*mm
    cnv.drawString(20*mm, y, f"Salariat: {nume or ''} {prenume or ''}")
    y -= 12*mm
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
        linii.insert(1, (f"Zile concediu medical: {int(zc)}", 0))
        linii.insert(len(linii)-1, ("Indemnizatie CM (neta)", cm_net))
    for eticheta, val in linii:
        bold = eticheta == "SALARIU NET"
        cnv.setFont(fb if bold else fr, 11 if bold else 10)
        cnv.drawString(20*mm, y, eticheta)
        cnv.drawRightString(120*mm, y, f"{float(val):,.2f} lei")
        y -= 7*mm
    y -= 4*mm
    cnv.setFont(fr, 9)
    cnv.drawString(20*mm, y, f"Cost total angajator (inclusiv CAM 2.25%): {float(calc['cost_angajator']):,.2f} lei")
    cnv.save()
    return buf.getvalue()
