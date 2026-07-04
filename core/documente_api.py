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

def balanta_pdf(conn, schema, an, luna, nume_firma=""):
    randuri = balanta(conn, schema, an, luna)
    init_fonturi()
    _fr, _fb = font("sans")
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    lat, inalt = A4
    y = inalt - 20*mm
    c.setFont(_fb, 13)
    c.drawString(15*mm, y, f"Balanta de verificare — {luna:02d}/{an}")
    y -= 6*mm
    c.setFont(_fr, 10)
    c.drawString(15*mm, y, nume_firma)
    y -= 10*mm
    c.setFont(_fb, 8)
    cap = ["Cont", "Denumire", "SI D", "SI C", "Rulaj D", "Rulaj C", "SF D", "SF C"]
    pozx = [15, 30, 95, 115, 135, 155, 175, 195]
    for t, x in zip(cap, pozx):
        c.drawString(x*mm, y, t)
    y -= 5*mm
    c.setFont(_fr, 7.5)
    tot = [0]*6
    for r in randuri:
        if y < 20*mm:
            c.showPage(); y = inalt - 20*mm; c.setFont(_fr, 7.5)
        vals = [r["si_d"], r["si_c"], r["rul_d"], r["rul_c"], r["sf_d"], r["sf_c"]]
        for i, v in enumerate(vals): tot[i] += v
        c.drawString(15*mm, y, str(r["cont"]))
        c.drawString(30*mm, y, (r["denumire"] or "")[:38])
        for v, x in zip(vals, pozx[2:]):
            c.drawRightString((x+15)*mm, y, f"{v:,.2f}")
        y -= 4*mm
    y -= 2*mm
    c.setFont(_fb, 8)
    c.drawString(30*mm, y, "TOTAL")
    for v, x in zip(tot, pozx[2:]):
        c.drawRightString((x+15)*mm, y, f"{v:,.2f}")
    c.save()
    return buf.getvalue()

def declaratii_depuse(conn, tenant_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT an, luna, tip, data_depunere
            FROM public.declaratii_depuse
            WHERE tenant_id = %s
            ORDER BY an DESC, luna DESC, tip
        """, (tenant_id,))
        return [{"an": a, "luna": l, "tip": t, "data": d.isoformat()} for a, l, t, d in cur.fetchall()]
