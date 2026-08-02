# stat_plata_api.py - Stat de plata lunar + fluturas PDF.
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from core.pdf_fonturi import init_fonturi, font
from core import pontaj as _pontaj
from core import perioada as _per
from core import salarizare
from core import scadente as _scad
from core import beneficii_api as _ben
from core import common as _common

def stat_plata(conn, schema, an, luna):
    """Calcul salarii pentru toti salariatii activi, la data de referinta (an, luna)."""
    ref = date(an, luna, 1)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT id, nume, prenume, salariu_brut, persoane_intretinere, part_time, ore_zi,
                   tichet_masa_valoare, iban, cor, data_angajare, data_incetare
            FROM {schema}.salariati
            WHERE data_incetare IS NULL OR data_incetare >= %s
            ORDER BY nume, prenume
        """, (date(an, luna, 1),))
        randuri = cur.fetchall()
    # CM-uri pe luna
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT salariat_id, COALESCE(SUM(zile),0), COALESCE(SUM(net),0), COALESCE(SUM(brut_ang+brut_fnuass),0)
            FROM {schema}.concedii_medicale WHERE an = %s AND luna = %s GROUP BY salariat_id
        """, (an, luna))
        cm = {r[0]: {"zile": int(r[1]), "net": float(r[2]), "brut": float(r[3])} for r in cur.fetchall()}
    # [F133 Faza 2a] tichete de vacanta acordate in luna (one-off, din beneficii_lunare)
    vac_luna = _ben.lista_luna(conn, schema, an, luna, "vacanta")
    cult_luna = _ben.lista_luna(conn, schema, an, luna, "cultural")  # [tichete culturale]
    plafon_vac_an = 6 * float(_common.cota("salariu_minim", ref)[0])  # 6 salarii minime/an
    # [F133 Faza 2b1] tichete cadou acordate in luna: NEIMPOZABIL (nu atinge calcul_salariu/D112).
    # total/salariat (SUM evenimente) + flag taxabil (>300 sau eveniment nelegal -> semnal, tratare la 2b2).
    cadou_luna = _ben.lista_luna(conn, schema, an, luna, "cadou")
    cadou_det = _ben.cadou_detalii_luna(conn, schema, an, luna)
    stat = []
    import calendar as _cal
    from core import salariu_istoric as _si  # [tranzitie 29.07.2026] salariul contractual DATE-AWARE, nu salariati.salariu_brut
    _ultima_luna = date(an, luna, _cal.monthrange(an, luna)[1])
    _cs_sal = conn.cursor()
    for sid, nume, prenume, brut, pers, part_time, ore_zi, tichet_val, iban, cor, data_ang, data_inc in randuri:
        brut = _si.salariu_la(_cs_sal, schema, sid, _ultima_luna)  # salariul contractual din istoric
        _zlm, _zll = _si.zile_la_minim(_cs_sal, schema, sid, an, luna, data_ang, data_inc)
        _fac_prorata = (_zlm / _zll) if _zll else 0.0  # lit.a): zile ACTIVE si LA MINIM
        c_cm = cm.get(sid)
        # zile lucratoare FARA sarbatori (OUG 158/2005 art.10) - numitorul proratarii CM
        zile_luna = _scad.zile_lucratoare_luna(an, luna)
        cm_zile = c_cm["zile"] if (c_cm and c_cm["zile"] > 0) else 0
        # [D2 02.08] tichete de masa pe zile EFECTIV lucrate (HG 1045/2018 art.10(3)): zile lucratoare
        # - CM (evidenta) - CO/delegatie/absente/invoire (pontaj). Reversarea decuplarii 20.07 (DECIZII 02.08).
        # [D2/cap.23] tichetele cer pontaj CONFIRMAT (nu se ghiceste zile efectiv lucrate dintr-o luna necompletata)
        if float(tichet_val or 0) > 0 and not _per.e_confirmat(conn, schema, an, luna, "pontaj")["confirmat"]:
            raise _per.PerioadaNeconfirmata("Tichetele de masa", an, luna, "pontaj", "HG 1045/2018 art.10(3)")
        _fara_tichet = _pontaj.zile_fara_tichet(conn, schema, sid, an, luna) if float(tichet_val or 0) > 0 else 0
        tichet_zile = max(zile_luna - cm_zile - _fara_tichet, 0)
        if cm_zile > 0:
            brut_lucrat = float(brut or 0) * max(zile_luna - cm_zile, 0) / zile_luna
        else:
            brut_lucrat = float(brut or 0)
        vac = vac_luna.get(sid, 0)  # [F133 Faza 2a] tichete vacanta acordate in luna
        cult = cult_luna.get(sid, 0)  # [tichete culturale] acordate in luna (lunar + ocazional)
        # [D3 02.08] exces vacanta peste plafonul anual (6 sm) -> venit salarial in brut (cumulat an)
        _cum_c3 = float(_ben.total_an(conn, schema, sid, an, "vacanta", pana_luna=luna) or 0)
        _cum_a3 = float(_ben.total_an(conn, schema, sid, an, "vacanta", pana_luna=luna - 1) or 0) if luna > 1 else 0.0
        _exces_v3 = _ben.exces_vacanta_luna(_cum_c3, _cum_a3, plafon_vac_an)
        calc = salarizare.calcul_salariu(brut_lucrat, persoane=pers or 0, la_data=ref,
                                         norma_intreaga=not part_time,
                                         venit_brut_total=float(brut or 0),
                                         data_angajare=data_ang,
                                         data_incetare=data_inc,
                                         facilitate_prorata=_fac_prorata,
                                         tichet_valoare=float(tichet_val or 0), tichet_zile=tichet_zile,
                                         tichet_vacanta=max(float(vac or 0) - _exces_v3, 0.0),
                                         tichet_vacanta_exces=_exces_v3,
                                         tichet_cultural=float(cult or 0))
        # semnal la depasirea plafonului anual de vacanta (6 sal.minime) - cumulat pana la luna curenta
        vac_an = _ben.total_an(conn, schema, sid, an, "vacanta", pana_luna=luna) if vac else 0
        cadou = cadou_luna.get(sid, 0)  # [F133 Faza 2b1] total cadou (neimpozabil in 2b1)
        cadou_taxabil = any(d["taxabil"] for d in cadou_det.get(sid, []))  # >300 sau nelegal
        stat.append({
            "id": sid,
            "nume": f"{nume or ''} {prenume or ''}".strip(),
            "brut": float(calc["brut"]), "cas": float(calc["cas"]),
            "cass": float(calc["cass"]), "impozit": float(calc["impozit"]),
            "deducere": float(calc["deducere"]["total"]),
            "net": float(calc["net"]), "cam": float(calc["cam"]),
            "cas_suprataxa": float(calc.get("cas_suprataxa", 0)),
            "cass_suprataxa": float(calc.get("cass_suprataxa", 0)),
            "tichete_nominal": float(calc.get("tichete_nominal", 0)),
            "tichete_zile": tichet_zile if float(tichet_val or 0) > 0 else 0,
            "tichete_vacanta": float(calc.get("tichete_vacanta", 0)),
            "vacanta_peste_plafon": bool(vac and vac_an > plafon_vac_an),
            "cadou": float(cadou or 0),  # [F133 Faza 2b1] neimpozabil, primit pe card
            "cadou_taxabil": bool(cadou_taxabil),  # semnal: >300 sau eveniment nelegal (2b2)
            "iban": (iban or "").strip(),  # [F134] cont beneficiar pt plata pe card ('' = lipsa -> semnal)
            "cor": (cor or "").strip(),  # [F137] cod ocupatie COR ('' = lipsa -> semnal, necesar REGES)
            "data_incetare": (str(data_inc) if data_inc else ""),  # PASUL 1: data incetarii contractului (gol = activ)
            "cass_tichete": float(calc.get("cass_tichete", 0)),
            "impozit_tichete": float(calc.get("impozit_tichete", 0)),
            # [F133] pt afisaj transparent: impozit salariu (fara tichete), retinerea pe tichete,
            # valoarea totala a tichetelor si totalul disponibil (cash net + tichete pe card separat).
            "impozit_salariu": float(calc["impozit"]) - float(calc.get("impozit_tichete", 0)),
            "retinut_tichete": float(calc.get("cass_tichete", 0)) + float(calc.get("impozit_tichete", 0)),
            "valoare_tichete": float(calc.get("tichete_nominal", 0)) + float(calc.get("tichete_vacanta", 0)) + float(cadou or 0),
            "total_disponibil": float(calc["net"]) + float(calc.get("tichete_nominal", 0)) + float(calc.get("tichete_vacanta", 0)) + float(cadou or 0),
            "cost": float(calc["cost_angajator"]),
            "cm_zile": cm_zile,
            "cm_brut": c_cm["brut"] if c_cm else 0,
        })
    _cs_sal.close()
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
            SELECT nume, prenume, salariu_brut, persoane_intretinere, part_time, tichet_masa_valoare, data_angajare, data_incetare
            FROM {schema}.salariati WHERE id = %s
        """, (salariat_id,))
        r = cur.fetchone()
    if not r:
        return None
    nume, prenume, brut, pers, part_time, tichet_val, data_ang, data_inc = r
    import calendar as _cal2
    from core import salariu_istoric as _si  # [tranzitie] date-aware, nu salariati.salariu_brut
    _um = date(an, luna, _cal2.monthrange(an, luna)[1])
    with conn.cursor() as _csf:
        brut = _si.salariu_la(_csf, schema, salariat_id, _um)
        _zlm, _zll = _si.zile_la_minim(_csf, schema, salariat_id, an, luna, data_ang, data_inc)
    _fac_prorata = (_zlm / _zll) if _zll else 0.0
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT COALESCE(SUM(zile),0), COALESCE(SUM(net),0), COALESCE(SUM(brut_ang+brut_fnuass),0)
            FROM {schema}.concedii_medicale WHERE salariat_id = %s AND an = %s AND luna = %s
        """, (salariat_id, an, luna))
        zc, cm_net, cm_brut = cur.fetchone()
    # zile lucratoare FARA sarbatori (OUG 158/2005 art.10)
    zile_luna = _scad.zile_lucratoare_luna(an, luna)
    cm_zile = int(zc or 0)
    tichet_zile = max(zile_luna - cm_zile, 0)  # [F133] aceleasi zile ca proratarea salariului
    brut_lucrat = float(brut or 0) * max(zile_luna - cm_zile, 0) / zile_luna if zc else float(brut or 0)
    vac = _ben.lista_luna(conn, schema, an, luna, "vacanta").get(salariat_id, 0)  # [F133 Faza 2a]
    cult = _ben.lista_luna(conn, schema, an, luna, "cultural").get(salariat_id, 0)  # [tichete culturale]
    cadou = _ben.lista_luna(conn, schema, an, luna, "cadou").get(salariat_id, 0)  # [F133 Faza 2b1] neimpozabil
    calc = salarizare.calcul_salariu(brut_lucrat, persoane=pers or 0, la_data=ref,
                                     norma_intreaga=not part_time,
                                     venit_brut_total=float(brut or 0),
                                     data_angajare=data_ang,
                                     data_incetare=data_inc,
                                     facilitate_prorata=_fac_prorata,
                                     tichet_valoare=float(tichet_val or 0), tichet_zile=tichet_zile,
                                     tichet_vacanta=float(vac or 0),
                                     tichet_cultural=float(cult or 0))

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

    # [F133] impozitul din calc e TOTAL (salariu+tichete); pe fluturas il aratam separat
    imp_tichete = calc.get("impozit_tichete", 0)
    imp_salariu = calc["impozit"] - imp_tichete
    linii = [
        ("Salariu brut", calc["brut"]),
        ("Facilitate salariu minim (netaxabil)", calc["facilitate"]),
        ("CAS (25%)", -calc["cas"]),
        ("CASS (10%)", -calc["cass"]),
        ("Deducere personala", calc["deducere"]["total"]),
        ("Impozit pe venit", -imp_salariu),
        ("SALARIU NET", calc["net"]),
    ]
    if zc:
        linii.insert(1, (f"Zile concediu medical: {int(zc)}", None))
        linii.insert(len(linii) - 1, ("Indemnizatie CM (neta)", cm_net))
    # [F133] tichete: doar TAXA (CASS+impozit) se retine din salariul CASH -> reduce NET-ul,
    # deci ramane INAINTE de SALARIU NET (coloana reconciliaza la net). Valoarea tichetelor se
    # primeste PE CARD SEPARAT (nu cash) -> se arata DUPA net, + total disponibil = net + tichete.
    are_masa = float(calc.get("tichete_nominal", 0) or 0) > 0
    are_vac = float(calc.get("tichete_vacanta", 0) or 0) > 0
    are_cadou = float(cadou or 0) > 0  # [F133 Faza 2b1] cadou neimpozabil - fara retinere, primit pe card
    if are_masa or are_vac or are_cadou:
        # retinerea (CASS+impozit) apare DOAR pt masa/vacanta (taxabile); cadoul e neimpozabil in 2b1
        if are_masa or are_vac:
            i = len(linii) - 1  # inaintea SALARIU NET
            linii.insert(i, ("  CASS tichete (10%) - retinut din salariu", -calc["cass_tichete"])); i += 1
            linii.insert(i, ("  Impozit tichete (10%) - retinut din salariu", -imp_tichete))
        val_tichete = float(calc.get("tichete_nominal", 0)) + float(calc.get("tichete_vacanta", 0)) + float(cadou or 0)
        if are_masa:
            linii.append((f"Tichete masa ({tichet_zile} zile x {float(tichet_val):g} lei, pe card)", calc["tichete_nominal"]))
        if are_vac:
            linii.append(("Tichete vacanta (pe card separat)", calc["tichete_vacanta"]))
        if are_cadou:
            linii.append(("Tichete cadou (neimpozabil, pe card separat)", float(cadou)))
        linii.append(("TOTAL DISPONIBIL (net + tichete)", float(calc["net"]) + val_tichete))

    rows = []
    for eticheta, val in linii:
        bold = eticheta in ("SALARIU NET", "TOTAL DISPONIBIL (net + tichete)")
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
    _supra = float(calc.get("cas_suprataxa", 0) or 0) + float(calc.get("cass_suprataxa", 0) or 0)
    _nota_cost = "Cost total angajator (inclusiv CAM 2.25%"
    if _supra > 0:
        _nota_cost += f" + suprataxa part-time {_bani(_supra, 'lei')}"
    _nota_cost += f"): {_bani(calc['cost_angajator'], 'lei')}"
    el.append(Paragraph(
        _nota_cost,
        ParagraphStyle("cost", parent=stil["Normal"], fontName=fr, fontSize=9, textColor=_colors.HexColor("#555555")),
    ))
    doc.build(el)
    return buf.getvalue()
