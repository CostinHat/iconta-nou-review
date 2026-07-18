# -*- coding: utf-8 -*-
"""core/export_saga.py — F171: export facturi EMISE catre SAGA (XML propriu SAGA).

SAGA importa facturi din XML propriu (Diverse -> Import date din fisiere generate).
Structura si regulile verificate la sursa 18.07.2026 (manual.sagasoft.ro/sagac/topic-76
+ forum oficial SAGA) - vezi BRIEF_CODE_EXPORT_SAGA.md.

Reguli SAGA critice:
  1. DIRECTIA se decide prin CIF: SAGA claseaza in "Iesiri" cand CIF-ul firmei apare la
     <FurnizorCIF>. Pentru facturi EMISE de firma: Furnizor = firma, Client = partener.
     NU se marcheaza directia explicit.
  2. Numele fisierului: F_<cif>_<numar>_<data>.xml (altfel SAGA nu-l vede).
  3. Data zz.ll.aaaa; moneda RON; sume/cota cu 2 zecimale, separator PUNCT.

Cod structurat pe format (un generator per format) - SAGA-only acum; WinMentor/Ciel later.
Read-only: citeste factura existenta, produce XML. Fara schema, fara UPDATE.
"""
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import escape as _xesc

FORMAT = "saga"


def _q(x):
    return Decimal(str(x or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _num(d):
    """Numar cu 2 zecimale, separator punct (ex. 1234.56)."""
    return f"{_q(d):.2f}"


def _cant(c):
    """Cantitate: pana la 3 zecimale, fara zerouri inutile (ex. 1, 2.5, 0.125)."""
    v = Decimal(str(c or 0)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP).normalize()
    s = format(v, "f")
    return s if s not in ("", "-0") else "0"


def _d_ro(d):
    """Data -> zz.ll.aaaa. Accepta date sau string ISO."""
    if not d:
        return ""
    if hasattr(d, "day"):
        return "%02d.%02d.%04d" % (d.day, d.month, d.year)
    s = str(d)[:10]
    if len(s) == 10 and s[4] == "-":
        return "%s.%s.%s" % (s[8:10], s[5:7], s[0:4])
    return s


def _t(tag, val):
    """<tag>continut-escapat</tag>. Gol permis (SAGA accepta tag-uri goale)."""
    return "<%s>%s</%s>" % (tag, _xesc("" if val is None else str(val)), tag)


def nume_fisier(cif, numar, data_emitere):
    """F_<cif>_<numar>_<data>.xml. Sanitizeaza cif/numar (SAGA + filesystem)."""
    def _s(x):
        return "".join(ch for ch in str(x or "") if ch.isalnum())
    return "F_%s_%s_%s.xml" % (_s(cif), _s(numar), _d_ro(data_emitere))


def xml_factura(firma, factura, linii):
    """Genereaza XML-ul SAGA pentru o factura EMISA. Pur (dict-uri -> str).
    firma: {nume,cui,reg_com,adresa,iban,banca,tva_la_incasare}
    factura: {numar,data_emitere,data_scadenta,taxare_inversa,moneda,tert_nume,tert_cui,tert_adresa}
    linii: [{descriere,um,cantitate,pret_unitar,cota_tva}]
    Furnizor = firma-client (facturi emise), Client = partener -> SAGA claseaza ca iesire."""
    total_val = Decimal("0")
    total_tva = Decimal("0")
    linii_xml = []
    for i, l in enumerate(linii, start=1):
        cant = Decimal(str(l.get("cantitate") or 0))
        pret = Decimal(str(l.get("pret_unitar") or 0))
        cota = Decimal(str(l.get("cota_tva") or 0))
        valoare = _q(cant * pret)                 # valoare neta a liniei
        tva = _q(valoare * cota / Decimal(100))   # TVA aritmetic (ROUND_HALF_UP)
        total_val += valoare
        total_tva += tva
        linii_xml.append(
            "<Linie>" +
            _t("LinieNrCrt", i) + _t("Descriere", l.get("descriere")) +
            _t("CodArticolFurnizor", "") + _t("CodArticolClient", "") +
            _t("CodBare", "") + _t("InformatiiSuplimentare", "") +
            _t("UM", l.get("um")) + _t("Cantitate", _cant(cant)) +
            _t("Pret", _num(pret)) + _t("Valoare", _num(valoare)) + _t("TVA", _num(tva)) +
            "</Linie>")
    # cota din antet = cota primei linii (SAGA o recalculeaza oricum pe linii)
    cota_antet = _num(linii[0].get("cota_tva")) if linii else "0.00"
    antet = (
        "<Antet>" +
        _t("FurnizorNume", firma.get("nume")) + _t("FurnizorCIF", firma.get("cui")) +
        _t("FurnizorNrRegCom", firma.get("reg_com")) + _t("FurnizorCapital", "") +
        _t("FurnizorAdresa", firma.get("adresa")) + _t("FurnizorBanca", firma.get("banca")) +
        _t("FurnizorIBAN", firma.get("iban")) + _t("FurnizorInformatiiSuplimentare", "") +
        _t("ClientNume", factura.get("tert_nume")) + _t("ClientInformatiiSuplimentare", "") +
        _t("ClientCIF", factura.get("tert_cui")) + _t("ClientNrRegCom", "") +
        _t("ClientAdresa", factura.get("tert_adresa")) + _t("ClientBanca", "") +
        _t("ClientIBAN", "") +
        _t("FacturaNumar", factura.get("numar")) + _t("FacturaData", _d_ro(factura.get("data_emitere"))) +
        _t("FacturaScadenta", _d_ro(factura.get("data_scadenta"))) +
        _t("FacturaTaxareInversa", "Da" if factura.get("taxare_inversa") else "Nu") +
        _t("FacturaTVAIncasare", "Da" if firma.get("tva_la_incasare") else "Nu") +
        _t("FacturaInformatiiSuplimentare", "") +
        _t("FacturaMoneda", factura.get("moneda") or "RON") +
        _t("FacturaCotaTVA", cota_antet) + _t("FacturaGreutate", "") +
        "</Antet>")
    total = _q(total_val + total_tva)
    corp = (
        "<Factura>" + antet +
        "<Detalii><Continut>" + "".join(linii_xml) + "</Continut></Detalii>" +
        "<Sumar>" + _t("TotalValoare", _num(total_val)) + _t("TotalTVA", _num(total_tva)) +
        _t("Total", _num(total)) + "</Sumar>" +
        "<Observatii>" + _t("txtObservatii", "") + _t("SoldClient", "") + "</Observatii>" +
        "</Factura>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<Facturi>' + corp + "</Facturi>"


# ---- acces DB (citeste factura reala din schema tenantului) ----

def _firma(conn, schema):
    with conn.cursor() as cur:
        cur.execute(f"SELECT nume, cui, reg_com, adresa, iban, banca, tva_la_incasare "
                    f"FROM {schema}.firma_profil WHERE id=1")
        r = cur.fetchone() or (None,) * 7
    return {"nume": r[0], "cui": r[1], "reg_com": r[2], "adresa": r[3],
            "iban": r[4], "banca": r[5], "tva_la_incasare": r[6]}


def date_factura(conn, schema, factura_id):
    """(firma, factura, linii) pentru o factura EMISA. None daca inexistenta sau nu e emisa."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT id, numar, data_emitere, data_scadenta, taxare_inversa, moneda,
                        tert_nume, tert_cui, tert_adresa, directie, tip
                        FROM {schema}.facturi WHERE id=%s""", (factura_id,))
        f = cur.fetchone()
        if not f or f[9] != "emisa":
            return None
        cur.execute(f"""SELECT descriere, um, cantitate, pret_unitar, cota_tva
                        FROM {schema}.factura_linii WHERE factura_id=%s ORDER BY id""", (factura_id,))
        linii = [{"descriere": l[0], "um": l[1], "cantitate": l[2],
                  "pret_unitar": l[3], "cota_tva": l[4]} for l in cur.fetchall()]
    factura = {"id": f[0], "numar": f[1], "data_emitere": f[2], "data_scadenta": f[3],
               "taxare_inversa": f[4], "moneda": f[5], "tert_nume": f[6], "tert_cui": f[7],
               "tert_adresa": f[8]}
    return _firma(conn, schema), factura, linii


def facturi_emise_luna(conn, schema, an, luna):
    """Id-urile facturilor EMISE (tip factura) dintr-o luna."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT id FROM {schema}.facturi
                        WHERE directie='emisa' AND tip='factura'
                          AND EXTRACT(YEAR FROM data_emitere)=%s
                          AND EXTRACT(MONTH FROM data_emitere)=%s
                        ORDER BY data_emitere, id""", (an, luna))
        return [r[0] for r in cur.fetchall()]
