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
    """Balanta de verificare cu cinci egalitati pe luna (an, luna) - OMFP 2634/2015 anexa 2, cod 14-6-30/a.

    Norma (citata in `anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt`): „Balanța de verificare cuprinde
    următoarele elemente: simbolul și denumirea conturilor; soldurile inițiale debitoare și creditoare; totalul
    sumelor debitoare și creditoare ale lunii precedente, după caz; rulajele curente debitoare și creditoare; …
    totalul sumelor debitoare și creditoare; soldurile finale debitoare sau creditoare.”

    [08.10.2026, decizia Costin W1, verbatim in DECIZII] „Jurnalul și balanța trebuie să arate aceleași note pentru
    același utilizator … balanța nu poate conține ce jurnalul nu arată.” Pana acum `rul_*` aduna TOATE notele de
    dinaintea sfarsitului lunii (fara limita de jos): F2 pe 10/2026 arata „rulaje” 7.750 din note de septembrie, iar
    registrul-jurnal pe octombrie avea 0 note. Acum:
      * `rul_*` = RULAJELE CURENTE = notele lunii, exact multimea registrului-jurnal pe luna (acelasi predicat de
        status - vezi `scan_populatii_registre`, nici unul nu filtreaza pe autor sau pe drept);
      * `prec_*` = SUMELE PRECEDENTE = notele din 1 ianuarie pana la inceputul lunii;
      * `si_*` = soldul inceputului anului: soldurile initiale introduse + notele anilor anteriori, net (norma: balanta
        la 1 ianuarie se completeaza cu soldurile finale ale lui decembrie); fara note in anii anteriori, ramane exact
        soldul introdus;
      * `tot_*` = TOTALUL SUMELOR = si + prec + rul; `sf_*` = soldul final, din totalul sumelor.
    """
    inceput_an = date(an, 1, 1)
    inceput = date(an, luna, 1)
    sfarsit = date(an + (luna == 12), (luna % 12) + 1, 1)
    with conn.cursor() as cur:
        cur.execute(f"""
            WITH si AS (
                SELECT cont, MAX(denumire) AS denumire,
                       SUM(sold_debitor) AS sd, SUM(sold_creditor) AS sc
                FROM {schema}.solduri_initiale GROUP BY cont
            ),
            linii AS (
                SELECT l.cont_debit AS cont, l.suma AS deb, 0::numeric AS cred, i.data
                FROM {schema}.inregistrari_linii l JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                WHERE i.data < %s
                UNION ALL
                SELECT l.cont_credit, 0, l.suma, i.data
                FROM {schema}.inregistrari_linii l JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                WHERE i.data < %s
            ),
            r AS (SELECT cont,
                         SUM(deb) FILTER (WHERE data < %s) AS ant_d, SUM(cred) FILTER (WHERE data < %s) AS ant_c,
                         SUM(deb) FILTER (WHERE data >= %s AND data < %s) AS prec_d,
                         SUM(cred) FILTER (WHERE data >= %s AND data < %s) AS prec_c,
                         SUM(deb) FILTER (WHERE data >= %s) AS rul_d, SUM(cred) FILTER (WHERE data >= %s) AS rul_c
                  FROM linii GROUP BY cont)
            SELECT COALESCE(si.cont, r.cont) AS cont,
                   COALESCE(si.denumire, pc.denumire, '') AS denumire,
                   COALESCE(si.sd,0), COALESCE(si.sc,0), COALESCE(r.ant_d,0), COALESCE(r.ant_c,0),
                   COALESCE(r.prec_d,0), COALESCE(r.prec_c,0), COALESCE(r.rul_d,0), COALESCE(r.rul_c,0)
            FROM si FULL OUTER JOIN r ON r.cont = si.cont
            LEFT JOIN {schema}.plan_conturi pc ON pc.simbol = COALESCE(si.cont, r.cont)
            ORDER BY 1
        """, (sfarsit, sfarsit, inceput_an, inceput_an, inceput_an, inceput, inceput_an, inceput, inceput, inceput))
        randuri = []
        for cont, den, sd, sc, ant_d, ant_c, prec_d, prec_c, rul_d, rul_c in cur.fetchall():
            sd, sc = float(sd), float(sc)
            if ant_d or ant_c:   # notele anilor anteriori: soldul de la 1 ianuarie, net
                net = sd + float(ant_d) - sc - float(ant_c)
                sd, sc = (round(net, 2), 0.0) if net > 0 else (0.0, round(-net, 2))
            tot_d = sd + float(prec_d) + float(rul_d)
            tot_c = sc + float(prec_c) + float(rul_c)
            if not den:
                from core.plan_omfp import denumire_omfp
                den = denumire_omfp(cont)
            randuri.append({"cont": cont, "denumire": den,
                            "si_d": sd, "si_c": sc,
                            "prec_d": float(prec_d), "prec_c": float(prec_c),
                            "rul_d": float(rul_d), "rul_c": float(rul_c),
                            "tot_d": round(tot_d, 2), "tot_c": round(tot_c, 2),
                            "sf_d": round(tot_d - tot_c, 2) if tot_d > tot_c else 0,
                            "sf_c": round(tot_c - tot_d, 2) if tot_c > tot_d else 0})
        return randuri


def note_lunii(conn, schema, an, luna):
    """Cate note are luna - aceeasi multime ca registrul-jurnal pe luna si ca rulajele curente ale balantei (W1)."""
    sfarsit = date(an + (luna == 12), (luna % 12) + 1, 1)
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {schema}.inregistrari WHERE data >= %s AND data < %s", (date(an, luna, 1), sfarsit))
        r = cur.fetchone()
    return int(list(r.values())[0] if isinstance(r, dict) else r[0])


def rulaje_cumulate(r, parte):
    """Rulajul de la 1 ianuarie pana la finalul lunii (sume precedente + rulaje curente), pe 'd' sau 'c'.

    Pentru cititorii care voiau cumulatul anului (KPI, cash-flow): inainte il luau din `rul_*`, cand `rul_*` era
    cumulat; acum `rul_*` e luna, deci cumulatul se cere pe nume."""
    return r["prec_" + parte] + r["rul_" + parte]

# Cele trei perechi pe care o balanta de verificare trebuie sa le inchida. Constanta, nu literale
# imprastiate: gardul citeste MULTIMEA, nu cauta un sir intr-un text (METODA §23).
PERECHI_BALANTA = (("sold initial", "si_d", "si_c"),
                   ("sume precedente", "prec_d", "prec_c"),
                   ("rulaje curente", "rul_d", "rul_c"),
                   ("total sume", "tot_d", "tot_c"),
                   ("sold final", "sf_d", "sf_c"))

# Sub un ban nu e o divergenta, e zgomot de virgula mobila: sumele se aduna din float-uri.
TOLERANTA_BALANTA = 0.01


def totaluri_balanta(randuri):
    """Totalurile pe coloanele balantei (cele cinci perechi). O SINGURA sursa - le citesc si PDF-ul, si ruta de date.

    Erau calculate inauntrul lui `balanta_pdf`, deci existau numai pe hartie. A doua adunare, scrisa
    in JS pentru ecran, ar fi fost al doilea calcul al aceluiasi lucru - clasa pe care fluturasul a
    platit-o deja (vezi `stat_plata_api.rand_fluturas`).
    """
    return {c: round(sum(float(r.get(c) or 0) for r in randuri), 2)
            for _ce, d, c_ in PERECHI_BALANTA for c in (d, c_)}


def inchidere_balanta(randuri):
    """„Se inchide balanta?" - ca OBIECT cu atribute, nu ca propozitie (DS cap.25.5).

    TREI stari, nu doua, si a treia e cea care conteaza: pe o balanta FARA RANDURI nu se poate
    spune ca „se inchide" - nu s-a verificat nimic. Un necunoscut nu se rotunjeste la „stiu ca da"
    mai putin decat la „stiu ca nu" (interdictia 32).

    Egalitatile sunt cele din norma (cinci egalitati, cod 14-6-30/a): debitul si creditul se inchid pe soldul
    initial, pe sumele precedente, pe rulajele curente, pe totalul sumelor si pe soldul final. Ce intoarce e destul ca omul sa VADA de ce, nu doar verdictul: fiecare pereche
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
    from reportlab.lib.pagesizes import A4 as _A4, landscape as _landscape
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
        buf, pagesize=_landscape(_A4),   # zece coloane de sume (cinci egalitati) nu incap pe portret
        leftMargin=10 * _mm, rightMargin=10 * _mm,
        topMargin=16 * _mm, bottomMargin=16 * _mm,
        title="Balanța de verificare %02d/%d%s" % (luna, an, (" — " + nume_firma) if nume_firma else ""), author="iConta",   # [05.10.2026]
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

    cap = ["Cont", "Denumire", "SI D", "SI C", "Prec. D", "Prec. C", "Rulaj D", "Rulaj C", "Total D", "Total C", "SF D", "SF C"]
    _col = [c for _ce, d, c_ in PERECHI_BALANTA for c in (d, c_)]
    date_tab = [[Paragraph(c, st_cap) if i < 2 else Paragraph(c, st_cap_r) for i, c in enumerate(cap)]]
    _t = totaluri_balanta(randuri)  # sursa unica: aceleasi totaluri le vede si ecranul
    tot = [_t[c] for c in _col]
    for r in randuri:
        vals = [r[c] for c in _col]
        date_tab.append([
            Paragraph(str(r["cont"]), st_cell),
            Paragraph((r["denumire"] or "")[:60], st_cell),
        ] + [Paragraph(_bani(v), st_cell_r) for v in vals])
    date_tab.append([
        Paragraph("", st_cell), Paragraph("TOTAL", ParagraphStyle("totlbl", parent=st_cell, fontName=fb)),
    ] + [Paragraph(_bani(v), ParagraphStyle("totval", parent=st_cell_r, fontName=fb)) for v in tot])

    tabel = Table(date_tab, colWidths=[16 * _mm, 61 * _mm] + [20 * _mm] * len(_col), repeatRows=1)
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
