"""
core/adeverinta.py — F136: adeverinta de salariat (generica), PDF.

Temei legal: art. 34 alin. (5) + art. 40 alin. (2) lit. h) Codul muncii (Legea 53/2003).
Modelul e la latitudinea angajatorului (nu exista format impus, nu se inregistreaza la
ITM). Continut MINIM obligatoriu (art. 34(5)), nu poate lipsi: activitatea desfasurata,
durata activitatii, salariul, vechimea in munca/meserie/specialitate.

Date AUTO (din DB): firma (denumire/CUI/adresa), salariat (nume/CNP/COR/data angajare/
brut), net (calcul_salariu). Date de INTRARE (contabilul, in formular): serie/nr CI,
nr/data CIM, tip contract, departament, vechime, scop, mentiuni, nr. iesire.

NU e "adeverinta pentru banca": bancile au formulare proprii tipizate si din 2026
verifica veniturile direct la ANAF. Ecranul spune asta onest. Cazuri reale: gradinita/
scoala, viza, notar, inchiriere, medic de familie, instanta - niciunul cu format impus.
"""
from io import BytesIO
from datetime import date
from core import salarizare
from core.pdf_fonturi import init_fonturi, font


def _d_ro(d):
    if not d:
        return ""
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d[:10])
        except Exception:
            return d
    return "%02d.%02d.%04d" % (d.day, d.month, d.year)


def date_auto(conn, schema, salariat_id, an, luna):
    """Datele care se completeaza AUTOMAT din DB. None daca salariatul nu exista."""
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, patron_nume, declarant_nume, "
                    "declarant_functie FROM firma_profil WHERE id = 1")
        f = cur.fetchone() or (None,) * 6
        cur.execute("SELECT nume, prenume, cnp, cor, data_angajare, salariu_brut, "
                    "part_time, persoane_intretinere FROM salariati WHERE id = %s", (salariat_id,))
        s = cur.fetchone()
    if not s:
        return None
    brut = float(s[5] or 0)
    calc = salarizare.calcul_salariu(brut, persoane=s[7] or 0, la_data=date(an, luna, 1),
                                     norma_intreaga=not s[6], venit_brut_total=brut)
    return {
        "firma_nume": f[0] or "", "firma_cui": f[1] or "", "firma_adresa": f[2] or "",
        "reprezentant": f[3] or f[4] or "Administrator", "repr_functie": f[5] or "Administrator",
        "sal_nume": ("%s %s" % (s[0] or "", s[1] or "")).strip(), "cnp": s[2] or "",
        "cor": s[3] or "", "data_angajare": s[4], "brut": brut, "net": float(calc["net"]),
    }


def pdf(conn, schema, salariat_id, campuri):
    """Genereaza PDF-ul adeverintei. campuri = dict cu datele de intrare + an/luna.
    Intoarce bytes sau None (salariat inexistent). Design System cap.7 (reportlab)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT

    c = dict(campuri or {})
    an = int(c.get("an") or date.today().year)
    luna = int(c.get("luna") or date.today().month)
    a = date_auto(conn, schema, salariat_id, an, luna)
    if not a:
        return None

    init_fonturi()
    fr, fb = font("sans")
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm)
    S = getSampleStyleSheet()
    p = ParagraphStyle("p", parent=S["Normal"], fontName=fr, fontSize=11, leading=17)
    meta = ParagraphStyle("meta", parent=p, fontSize=10, textColor=colors.HexColor("#555555"))
    titlu = ParagraphStyle("t", parent=p, fontName=fb, fontSize=15, alignment=TA_CENTER, leading=20)
    dr = ParagraphStyle("dr", parent=p, alignment=TA_RIGHT)

    nr = c.get("nr_iesire") or ""
    data_ies = c.get("data_iesire") or date.today().isoformat()
    tip = "nedeterminată" if (c.get("tip_contract") or "nedeterminata").startswith("nedet") else "determinată"

    # antet firma + nr. iesire
    el = [Paragraph("<b>%s</b>" % a["firma_nume"], p),
          Paragraph("CUI %s%s" % (a["firma_cui"], (" · " + a["firma_adresa"]) if a["firma_adresa"] else ""), meta),
          Paragraph("Nr. %s / %s" % (nr or "____", _d_ro(data_ies)), dr),
          Spacer(1, 10 * mm), Paragraph("ADEVERINȚĂ", titlu), Spacer(1, 8 * mm)]

    ci = ""
    if c.get("serie_ci") or c.get("nr_ci"):
        ci = ", legitimat(ă) cu C.I. seria %s nr. %s" % (c.get("serie_ci") or "—", c.get("nr_ci") or "—")
    dept = (", în cadrul departamentului %s" % c["departament"]) if c.get("departament") else ""
    cim = ""
    if c.get("nr_cim") or c.get("data_cim"):
        cim = " nr. %s din %s" % (c.get("nr_cim") or "—", _d_ro(c.get("data_cim")))
    functie = a["cor"] and ("în funcția de %s (cod COR %s)" % (c.get("functie") or "___", a["cor"])) \
        or ("în funcția de %s" % (c.get("functie") or "___"))

    corp = ("Prin prezenta se adeverește că doamna/domnul <b>%s</b>, CNP <b>%s</b>%s, "
            "este angajat(ă) al/a <b>%s</b> %s%s, în baza contractului individual de muncă%s, "
            "încheiat pe durată <b>%s</b>, începând cu data de <b>%s</b>."
            % (a["sal_nume"], a["cnp"], ci, a["firma_nume"], functie, dept, cim, tip,
               _d_ro(a["data_angajare"])))
    el.append(Paragraph(corp, p)); el.append(Spacer(1, 4 * mm))
    el.append(Paragraph("Salariul de bază brut lunar este de <b>%s lei</b>, iar salariul "
                        "net lunar este de <b>%s lei</b>." % (_bani(a["brut"]), _bani(a["net"])), p))
    el.append(Spacer(1, 4 * mm))
    vm = c.get("vechime_munca") or "—"
    vs = c.get("vechime_specialitate") or "—"
    el.append(Paragraph("Vechimea în muncă: <b>%s</b>. Vechimea în meserie/specialitate: <b>%s</b>." % (vm, vs), p))

    optionale = []
    if c.get("venit_an_precedent"):
        optionale.append("Venitul brut realizat în anul precedent: %s lei." % _bani(c["venit_an_precedent"]))
    if c.get("sporuri"):
        optionale.append("Sporuri: %s." % c["sporuri"])
    if c.get("retineri"):
        optionale.append("Rețineri/popriri: %s." % c["retineri"])
    if optionale:
        el.append(Spacer(1, 4 * mm)); el.append(Paragraph(" ".join(optionale), p))

    el.append(Spacer(1, 4 * mm))
    scop = c.get("scop") or "a-i servi acolo unde este necesar"
    el.append(Paragraph("Prezenta adeverință a fost eliberată pentru a-i servi la <b>%s</b>." % scop, p))
    if c.get("mentiuni"):
        el.append(Spacer(1, 3 * mm)); el.append(Paragraph(c["mentiuni"], p))
    el.append(Spacer(1, 3 * mm))
    el.append(Paragraph("Prezenta produce efecte conform art. 34 alin. (5) din Legea nr. 53/2003 "
                        "(Codul muncii).", meta))
    el.append(Spacer(1, 14 * mm))
    el.append(Paragraph("%s<br/><br/>%s,<br/>%s" % (_d_ro(data_ies), a["repr_functie"], a["reprezentant"]), dr))

    doc.build(el)
    return buf.getvalue()


def _bani(x):
    from core.pdf_util import bani as _b
    return _b(x)
