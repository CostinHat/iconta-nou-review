"""
core/factura_pdf.py — genereaza PDF-ul unei facturi (reportlab).
Intrare: profil (dict din firma_profil_api.citeste_profil) + factura (dict din
facturi_api.detalii_factura). Iesire: bytes (PDF).
Personalizare: logo (data URI base64 PNG/JPG), culoare accent, font (sans/serif/mono).
"""
from __future__ import annotations
import base64
import io as _io
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image,
)
from reportlab.lib.enums import TA_RIGHT, TA_LEFT

MODUL = "factura_pdf"

# fonturi PDF din sursa unica (core/pdf_fonturi.py) — diacritice garantate.
from core.pdf_fonturi import init_fonturi as _init_fonturi, FONTURI as _FONTURI


def _culoare(hexs, implicit="#1d4ed8"):
    try:
        return colors.HexColor(hexs or implicit)
    except Exception:
        return colors.HexColor(implicit)


from core.pdf_util import bani as _bani  # sursa unica cap.7


def _data_ro(iso):
    if not iso:
        return ""
    p = str(iso).split("-")
    return f"{p[2]}.{p[1]}.{p[0]}" if len(p) == 3 else str(iso)


def _logo_flowable(logo_uri, latime_mm=32):
    """Construieste un Image din data URI base64 (PNG/JPG). None daca nu se poate."""
    if not logo_uri or not str(logo_uri).startswith("data:"):
        return None
    try:
        cap, b64 = str(logo_uri).split(",", 1)
        if "svg" in cap.lower():
            return None  # SVG neacceptat in reportlab nativ
        raw = base64.b64decode(b64)
        bio = _io.BytesIO(raw)
        img = Image(bio)
        # scalez la latimea data, pastrez proportia
        ratio = img.imageHeight / float(img.imageWidth) if img.imageWidth else 0.4
        img.drawWidth = latime_mm * mm
        img.drawHeight = latime_mm * mm * ratio
        return img
    except Exception:
        return None


#: [lot 19 pct.4d] Trimiterea la scutire pe factura unui emitent neplătitor de TVA (CF art.319 alin.(20) lit.l)).
MENTIUNE_NEPLATITOR = ("Scutit de TVA — regim special de scutire pentru întreprinderile mici, "
                       "art. 310 din Codul fiscal (Legea nr. 227/2015).")


# [comanda Costin 05.10.2026 pct.5] CF art.319 alin.(20) lit.d) și f): pe factură stă „codul de înregistrare în scopuri de TVA
# sau, după caz, codul de identificare fiscală”; CF art.318 alin.(1): „Codul de înregistrare în scopuri de TVA, atribuit conform
# art. 316 și 317, are prefixul RO”. Deci: plătitor -> „Cod TVA: RO…”; neplătitor -> „CIF: …”; stare necunoscută -> codul așa cum
# a fost scris (nu se ghicește).
def cod_fiscal_pe_factura(cui, platitor_tva):
    """(eticheta, valoarea) pentru codul furnizorului / beneficiarului pe factură; (None, None) fără cod."""
    brut = (cui or "").strip()
    cifre = "".join(ch for ch in brut if ch.isdigit())
    if not cifre:
        return None, None
    if platitor_tva is True:
        return "Cod TVA", "RO" + cifre
    if platitor_tva is False:
        return "CIF", cifre
    return ("Cod TVA", brut.upper()) if brut.upper().startswith("RO") else ("CUI", brut)


def serie_si_numar(serie, numar):
    """„Seria FCT nr. 12” (art.319 alin.(20) lit.a): `facturi.numar` conține deja seria (`{serie}{numar}`)."""
    numar = str(numar or "-")
    if serie and numar.startswith(serie):
        return "Seria %s nr. %s" % (serie, numar[len(serie):])
    return ("Seria %s nr. %s" % (serie, numar)) if serie else ("Nr. %s" % numar)


def genereaza_pdf(profil, factura):
    """profil, factura = dict-uri. Intoarce bytes (PDF)."""
    _init_fonturi()
    profil = profil or {}
    factura = factura or {}
    ac = _culoare(profil.get("culoare_factura"))
    font, font_b = _FONTURI.get(profil.get("font_factura"), _FONTURI["sans"])
    mon = factura.get("moneda") or "RON"
    este_valuta = str(mon).upper() != "RON"

    buf = _io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        # [pct.5] fără titlu, reportlab scria „(anonymous)” — exact ce arăta vizualizatorul
        title="Factura %s" % serie_si_numar(factura.get("serie"), factura.get("numar")).replace("Seria ", ""),
        author=profil.get("nume") or "iConta",
    )
    stil = getSampleStyleSheet()
    st_nume = ParagraphStyle("nume", parent=stil["Normal"], fontName=font_b,
                             fontSize=15, textColor=ac, leading=18)
    st_mic = ParagraphStyle("mic", parent=stil["Normal"], fontName=font,
                            fontSize=8, textColor=colors.HexColor("#555555"), leading=11)
    st_titlu = ParagraphStyle("titlu", parent=stil["Normal"], fontName=font_b,
                              fontSize=16, textColor=ac, alignment=TA_RIGHT, leading=19)
    st_nr = ParagraphStyle("nr", parent=stil["Normal"], fontName=font_b,
                           fontSize=11, textColor=colors.HexColor("#333333"), alignment=TA_RIGHT)
    st_cell = ParagraphStyle("cell", parent=stil["Normal"], fontName=font, fontSize=9, leading=11)
    st_meta = ParagraphStyle("meta", parent=stil["Normal"], fontName=font, fontSize=9,
                             textColor=colors.HexColor("#333333"), leading=13)

    el = []

    # ---- ANTET: logo + firma (stanga) | FACTURA + numar (dreapta) ----
    adr = ", ".join([x for x in (profil.get("adresa"), profil.get("oras"),
                                 profil.get("judet")) if x])
    firma_txt = [Paragraph(profil.get("nume") or "Firma mea SRL", st_nume)]
    _et, _cod = cod_fiscal_pe_factura(profil.get("cui"), profil.get("platitor_tva"))
    det = ("%s: %s" % (_et, _cod)) if _cod else "CIF: -"   # [pct.5] art.319 lit.d) + art.318 alin.(1)
    if profil.get("reg_com"):
        det += " · " + profil["reg_com"]
    firma_txt.append(Paragraph(det, st_mic))
    # [lot 19 d12] Legea 31/1990 art.74 alin.(3): capitalul social (SRL) / subscris și vărsat (SA, SCA)
    from core import capital_social as _cs
    _cap = _cs.text_factura(profil) if not _cs.lipsa(profil) else None
    if _cap:
        firma_txt.append(Paragraph(_cap, st_mic))
    if adr:
        firma_txt.append(Paragraph(adr, st_mic))
    if profil.get("iban"):
        firma_txt.append(Paragraph("IBAN " + profil["iban"] +
                                   (" · " + profil["banca"] if profil.get("banca") else ""), st_mic))

    logo = _logo_flowable(profil.get("logo"))
    stanga = []
    if logo:
        stanga = [[logo], firma_txt]
        stanga_flow = Table([[logo]] + [[f] for f in firma_txt], colWidths=[90 * mm])
        stanga_flow.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (0, 0), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
        ]))
    else:
        stanga_flow = Table([[f] for f in firma_txt], colWidths=[90 * mm])
        stanga_flow.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))

    dreapta = [Paragraph("FACTUR\u0102", st_titlu),
               Paragraph(serie_si_numar(factura.get("serie"), factura.get("numar")), st_nr)]   # [pct.5] art.319 lit.a)
    dreapta_flow = Table([[dreapta[0]], [dreapta[1]]], colWidths=[70 * mm])
    dreapta_flow.setStyle(TableStyle([
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))

    antet = Table([[stanga_flow, dreapta_flow]], colWidths=[100 * mm, 74 * mm])
    antet.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("LINEBELOW", (0, 0), (-1, -1), 1.4, ac),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    el.append(antet)
    el.append(Spacer(1, 8))

    # ---- META: data, scadenta, partener ----
    dir_txt = "Emis\u0103" if factura.get("directie") in ("emisa", "iesire") else "Primit\u0103"
    # [pct.5] art.319 alin.(20) lit.b) „data emiterii facturii” — o dată, nu o stare („Emisă - …”)
    meta_linii = ["Data emiterii: " + _data_ro(factura.get("data_emitere"))]
    if factura.get("data_scadenta"):
        meta_linii.append("Data scaden\u021bei: " + _data_ro(factura.get("data_scadenta")))
    part = factura.get("tert_nume")
    if part:
        etich = "C\u0103tre" if dir_txt.startswith("Emis") else "De la"
        _et_t, _cod_t = cod_fiscal_pe_factura(factura.get("tert_cui"), factura.get("tert_platitor_tva"))
        meta_linii.append(f"{etich}: {part}" + (f" - {_et_t}: {_cod_t}" if _cod_t else ""))   # [pct.5] art.319 lit.f)
        adr_tert = (factura.get("tert_adresa") or "").strip()
        if adr_tert:
            meta_linii.append(adr_tert)
    for m in meta_linii:
        el.append(Paragraph(m, st_meta))
    el.append(Spacer(1, 10))

    # ---- TABEL LINII ----
    linii = factura.get("linii") or []
    # [lot 19 pct.4d, 02.10.2026] Emitent NEplătitor de TVA (regim special de scutire): documentul nu menționează taxa —
    # CF art.310 alin.(10) lit.b) („nu are voie să menționeze taxa pe factură sau pe alt document”) — dar poartă
    # trimiterea la scutire — CF art.319 alin.(20) lit.l) („trimiterea la dispozițiile aplicabile din prezentul titlu …
    # din care să rezulte că livrarea … face obiectul unei scutiri”). Profil fără statut = plătitor (fără default tăcut).
    neplatitor = (factura.get("directie") in ("emisa", "iesire")) and (profil or {}).get("platitor_tva") is False
    cap = ["Denumire", "Cant", "UM", "Pre\u021b"] + ([] if neplatitor else ["Cot\u0103"]) + ["Valoare"]
    date_tab = [[Paragraph(f"<b>{c}</b>", ParagraphStyle(
        "th", parent=st_cell, textColor=colors.white, fontName=font_b))
        for c in cap]]
    peCota = {}
    for l in linii:
        cant = Decimal(str(l.get("cantitate") or 0))
        pret = Decimal(str(l.get("pret_unitar") or 0))
        _ct = l.get("cota_tva")
        if _ct is None:
            raise ValueError("Linia %r nu are cotă de TVA, deci factura nu se poate tipări. "
                             "Completează cota pe linie — 0 (scutit) e o valoare validă, dar "
                             "absența nu se poate ghici." % (l.get("descriere") or "",))
        cota = Decimal(str(_ct))
        baza = cant * pret
        tva = baza * cota / 100
        peCota.setdefault(cota, [Decimal(0), Decimal(0)])
        peCota[cota][0] += baza
        peCota[cota][1] += tva
        date_tab.append([
            Paragraph(str(l.get("descriere") or ""), st_cell),
            Paragraph(f"{cant:,.3f}".rstrip("0").rstrip(".").replace(",", "."), st_cell),
            Paragraph(str(l.get("um") or "buc"), st_cell),
            Paragraph(_bani(pret), st_cell),
        ] + ([] if neplatitor else [Paragraph(f"{cota:.2f}".rstrip("0").rstrip(".") + "%", st_cell)]) + [
            Paragraph(_bani(baza, mon), ParagraphStyle("rval", parent=st_cell, alignment=TA_RIGHT)),
        ])
    tabel = Table(date_tab, colWidths=([78 * mm, 22 * mm, 14 * mm, 26 * mm, 34 * mm] if neplatitor else
                                       [60 * mm, 22 * mm, 14 * mm, 26 * mm, 18 * mm, 34 * mm]))
    tabel.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ac),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    el.append(tabel)
    el.append(Spacer(1, 10))

    # ---- TOTALURI defalcate pe cote ----
    tot_rows = []
    for cota in ([] if neplatitor else sorted(peCota.keys(), reverse=True)):
        b, t = peCota[cota]
        tot_rows.append(["Baz\u0103 %g%%" % cota, _bani(b, mon)])
        tot_rows.append(["TVA %g%%" % cota, _bani(t, mon)])
    tot_rows.append(["Total", _bani(factura.get("total"), mon)])
    tot_tab = Table(
        [[Paragraph(r[0], st_cell),
          Paragraph(r[1], ParagraphStyle("tr", parent=st_cell, alignment=TA_RIGHT))]
         for r in tot_rows],
        colWidths=[40 * mm, 34 * mm], hAlign="RIGHT")
    n_last = len(tot_rows) - 1
    tot_tab.setStyle(TableStyle([
        ("LINEABOVE", (0, n_last), (-1, n_last), 1, ac),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (1, 0), (1, -1), 6),
        ("FONTNAME", (0, n_last), (-1, n_last), font_b),
        ("TEXTCOLOR", (1, n_last), (1, n_last), ac),
        ("FONTSIZE", (0, n_last), (-1, n_last), 11),
    ]))
    el.append(tot_tab)
    if neplatitor:
        el.append(Spacer(1, 8))
        el.append(Paragraph(MENTIUNE_NEPLATITOR, st_cell))
    from core import facturi as _fc
    if _fc.e_din_bon_fiscal(factura):
        # [decizia A 02.10] HG 1/2016 pct.97 alin.(1): „fiind suficientă mențiunea «conform bon fiscal nr./data»”
        el.append(Spacer(1, 8))
        el.append(Paragraph(_fc.mentiune_bon(factura), st_cell))

    # ---- BLOC VALUTA (art. 319) ----
    if este_valuta and factura.get("tva_lei") is not None:
        el.append(Spacer(1, 10))
        sursa = "curs BNR" if factura.get("curs_sursa") == "bnr" else "curs introdus manual"
        curs = factura.get("curs_bnr")
        curs_s = (f"{Decimal(str(curs)):.4f}".replace(".", ",")) if curs else ""
        vb = [
            [Paragraph("<b>Conversie în lei (art. 319 Cod fiscal)</b>",
                       ParagraphStyle("vt", parent=st_cell, fontName=font_b))],
        ] + ([] if neplatitor else [
            [Paragraph("TVA \u00een lei: <b>%s</b>" % _bani(factura.get("tva_lei"), "lei"), st_cell)],
        ]) + [
            [Paragraph("Total \u00een lei: %s" % _bani(factura.get("total_lei"), "lei"), st_cell)],
            [Paragraph("%s %s - %s" % (sursa, curs_s, _data_ro(factura.get("data_curs"))),
                       ParagraphStyle("vs", parent=st_cell, fontSize=8,
                                      textColor=colors.HexColor("#666666")))],
        ]
        vtab = Table(vb, colWidths=[100 * mm], hAlign="RIGHT")
        vtab.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#cccccc")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7f8fa")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        el.append(vtab)

    doc.build(el)
    return buf.getvalue()
