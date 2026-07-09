# -*- coding: utf-8 -*-
"""Chitante emise (cod 14-4-1, Ordin 2634/2015): suma in litere + PDF.
Logica pura; DB si rute in main.py. Emiterea trece prin casa_api (5311=4111)."""

_UNITATI = ["", "unu", "doi", "trei", "patru", "cinci", "șase", "șapte", "opt", "nouă",
            "zece", "unsprezece", "doisprezece", "treisprezece", "paisprezece",
            "cincisprezece", "șaisprezece", "șaptesprezece", "optsprezece", "nouăsprezece"]
_ZECI = ["", "", "douăzeci", "treizeci", "patruzeci", "cincizeci",
         "șaizeci", "șaptezeci", "optzeci", "nouăzeci"]
_UNITATI_F = {1: "una", 2: "două"}  # acord feminin pentru sute/mii

def _sub_o_mie(n, feminin_final=False):
    parti = []
    sute = n // 100
    rest = n % 100
    if sute:
        if sute == 1:
            parti.append("una sută")
        elif sute == 2:
            parti.append("două sute")
        else:
            parti.append(_UNITATI[sute] + " sute")
    if rest:
        if rest < 20:
            u = _UNITATI_F.get(rest) if feminin_final and rest in _UNITATI_F else _UNITATI[rest]
            parti.append(u)
        else:
            z = _ZECI[rest // 10]
            u = rest % 10
            if u:
                uf = _UNITATI_F.get(u) if feminin_final and u in _UNITATI_F else _UNITATI[u]
                parti.append(z + " și " + uf)
            else:
                parti.append(z)
    return " ".join(parti)

def _grup(n, singular, plural, feminin):
    """ex: 1->'una mie', 2->'două mii', 21->'douăzeci și una de mii'.
    feminin = acordul la singular (una mie / un milion); pluralul lui 2 e mereu 'două'."""
    if n == 1:
        return ("una " if feminin else "un ") + singular
    text = _sub_o_mie(n, feminin_final=True)
    if n < 20:
        return text + " " + plural
    return text + " de " + plural

def suma_in_litere(suma):
    """1419.50 -> 'una mie patru sute nouăsprezece lei și cincizeci de bani'."""
    suma = round(float(suma), 2)
    lei = int(suma)
    bani = int(round((suma - lei) * 100))
    if lei == 0:
        text_lei = "zero lei"
    else:
        parti = []
        mil = lei // 1_000_000
        mii = (lei % 1_000_000) // 1000
        rest = lei % 1000
        if mil:
            parti.append(_grup(mil, "milion", "milioane", feminin=False))
        if mii:
            parti.append(_grup(mii, "mie", "mii", feminin=True))
        if rest:
            parti.append(_sub_o_mie(rest))
        cuv = " ".join(parti)
        if lei == 1:
            text_lei = "un leu"
        else:
            # "de lei" cand ultimele doua cifre NU sunt 1-19 (douazeci si unu DE lei, una suta DE lei, dar 219 lei)
            de = not (1 <= lei % 100 <= 19)
            text_lei = cuv + (" de lei" if de else " lei")
    if not bani:
        return text_lei
    if bani < 20:
        text_bani = (_UNITATI[bani] if bani != 1 else "un") + (" ban" if bani == 1 else " bani")
    else:
        text_bani = _sub_o_mie(bani) + " de bani"
    return text_lei + " și " + text_bani

def pdf_chitanta(emitent, ch):
    """emitent: {nume, cui, adresa?}; ch: {serie, numar, data, client_nume, client_cui, suma, reprezentand}.
    Intoarce bytes PDF. Tabel reportlab cu colWidths (regula cap. 7 Design System)."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A5
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os
    font = "Helvetica"
    for cale in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(cale):
            try:
                pdfmetrics.registerFont(TTFont("DejaVu", cale))
                font = "DejaVu"
            except Exception:
                pass
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A5,
                            leftMargin=14 * mm, rightMargin=14 * mm,
                            topMargin=12 * mm, bottomMargin=12 * mm)
    stiluri = getSampleStyleSheet()
    normal = ParagraphStyle("n", parent=stiluri["Normal"], fontName=font, fontSize=9.5, leading=13)
    titlu = ParagraphStyle("t", parent=stiluri["Normal"], fontName=font, fontSize=14, leading=18, spaceAfter=2)
    mic = ParagraphStyle("m", parent=stiluri["Normal"], fontName=font, fontSize=8.5, leading=11)
    suma = float(ch["suma"])
    suma_txt = ("%0.2f" % suma).replace(".", ",")
    # format romanesc cu separator de mii
    intreg, zec = suma_txt.split(",")
    intreg = "{:,}".format(int(intreg)).replace(",", ".")
    suma_txt = intreg + "," + zec
    corp = [
        Paragraph(emitent.get("nume") or "", normal),
        Paragraph("CUI: %s%s" % (emitent.get("cui") or "-",
                  (" · " + emitent["adresa"]) if emitent.get("adresa") else ""), mic),
        Spacer(1, 8 * mm),
        Paragraph("CHITANȚA seria %s nr. %s" % (ch["serie"], ch["numar"]), titlu),
        Paragraph("din data de %s" % ch["data"], mic),
        Spacer(1, 6 * mm),
        Paragraph("Am primit de la <b>%s</b>%s" % (
            ch.get("client_nume") or "................................",
            (" (CUI %s)" % ch["client_cui"]) if ch.get("client_cui") else ""), normal),
        Spacer(1, 2 * mm),
        Table([["Suma:", "%s lei" % suma_txt],
               ["adică:", suma_in_litere(suma)],
               ["reprezentând:", ch.get("reprezentand") or "-"]],
              colWidths=[26 * mm, 92 * mm],
              style=TableStyle([
                  ("FONTNAME", (0, 0), (-1, -1), font),
                  ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                  ("ALIGN", (1, 0), (1, 0), "LEFT"),
                  ("VALIGN", (0, 0), (-1, -1), "TOP"),
                  ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.Color(0.8, 0.83, 0.87)),
                  ("TOPPADDING", (0, 0), (-1, -1), 4),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
              ])),
        Spacer(1, 10 * mm),
        Paragraph("Casier,", normal),
        Paragraph("Semnătura ................................", mic),
    ]
    doc.build(corp)
    return buf.getvalue()
