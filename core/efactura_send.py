# -*- coding: utf-8 -*-
"""
core/efactura_send.py — e-Factura TRIMITERE: generator XML UBL 2.1 / CIUS-RO (F126/F160).

PASUL 1 (FAZA constructie e-Factura): generator PUR de XML + loader pe schema CURENTA +
config host FCTEL intr-o singura constanta. NU face retea aici (upload/stare = pasul 2).

Reutilizeaza STRUCTURA XML dovedita in build-ul vechi (_efx_build_xml), dar:
  - loader rescris pe schema curenta (facturi.tert_*, factura_linii, firma_profil) -
    build-ul vechi citea dintr-un tabel `clienti` care nu mai exista;
  - rotunjire fiscala explicita (Decimal + ROUND_HALF_UP, regula iConta), nu round().

HOST e-Factura (DECIZIE 18.07, DECIZII.md): baza REST corecta =
  https://webserviceapl.anaf.ro/{prod|test}/FCTEL/rest
NU api.anaf.ro (host ISTORIC din /opt/iconta, stale). Sursa autoritate = listarea oficiala
ANAF (static.anaf.ro/.../url_eFactura.html), nu build-ul vechi. O SINGURA constanta aici;
upload/stare/descarcare (pasul 2) o refolosesc, nu rescriu host prin apeluri.

LIMITE v1 (de confirmat pe TEST la pasul 2, NU ghicite aici):
  - Cumparatorul are in schema doar tert_nume/tert_cui/tert_adresa (adresa libera);
    CIUS-RO cere oras (BT-52). Pana cand formularul de factura capteaza orasul separat,
    CityName = oras (daca vine) altfel adresa libera - fallback documentat, TEST confirma.
  - Doar factura standard cu TVA (categorii S/Z). taxare_inversa (AE), neplatitor TVA (O),
    storno/nota de credit (381) NU sunt tratate in v1 - se adauga dupa confirmare pe TEST.
"""
import os
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import escape as _xml_escape

# ============================================================
#  CONFIG HOST — o singura constanta (env-overridable)
# ============================================================
FCTEL_BASE_TPL = os.environ.get(
    "EFACTURA_FCTEL_BASE", "https://webserviceapl.anaf.ro/%s/FCTEL/rest")


def fctel_base(mode="prod"):
    """Baza REST e-Factura pentru mode 'prod'/'test'. SINGURA sursa a host-ului."""
    mode = (mode or "prod").strip().lower()
    if mode not in ("prod", "test"):
        mode = "prod"
    return FCTEL_BASE_TPL % mode


# CIUS-RO: structura romaneasca peste EN16931 (valoare din build vechi, de confirmat pe TEST)
CUSTOMIZATION_ID = "urn:cen.eu:en16931:2017#compliant#urn:efactura.mfinante.ro:CIUS-RO:1.0.1"

_D0 = Decimal("0.00")

# Judet -> cod ISO 3166-2:RO (cbc:CountrySubentity)
_JUD = {
    "alba": "RO-AB", "arad": "RO-AR", "arges": "RO-AG", "bacau": "RO-BC", "bihor": "RO-BH",
    "bistrita-nasaud": "RO-BN", "bistrita nasaud": "RO-BN", "botosani": "RO-BT", "braila": "RO-BR",
    "brasov": "RO-BV", "bucuresti": "RO-B", "buzau": "RO-BZ", "calarasi": "RO-CL",
    "caras-severin": "RO-CS", "caras severin": "RO-CS", "cluj": "RO-CJ", "constanta": "RO-CT",
    "covasna": "RO-CV", "dambovita": "RO-DB", "dolj": "RO-DJ", "galati": "RO-GL", "giurgiu": "RO-GR",
    "gorj": "RO-GJ", "harghita": "RO-HR", "hunedoara": "RO-HD", "ialomita": "RO-IL", "iasi": "RO-IS",
    "ilfov": "RO-IF", "maramures": "RO-MM", "mehedinti": "RO-MH", "mures": "RO-MS", "neamt": "RO-NT",
    "olt": "RO-OT", "prahova": "RO-PH", "salaj": "RO-SJ", "satu mare": "RO-SM", "sibiu": "RO-SB",
    "suceava": "RO-SV", "teleorman": "RO-TR", "timis": "RO-TM", "tulcea": "RO-TL", "valcea": "RO-VL",
    "vaslui": "RO-VS", "vrancea": "RO-VN",
}
_CODURI_JUD = {v[3:] for v in _JUD.values()}

# UM iConta -> cod UN/ECE Rec 20
_UM = {
    "buc": "H87", "bucata": "H87", "bucati": "H87", "ora": "HUR", "ore": "HUR", "h": "HUR",
    "kg": "KGM", "g": "GRM", "l": "LTR", "litru": "LTR", "ml": "MLT", "m": "MTR", "mp": "MTK",
    "m2": "MTK", "mc": "MTQ", "m3": "MTQ", "km": "KMT", "luna": "MON", "luni": "MON", "zi": "DAY",
    "zile": "DAY", "set": "SET", "pereche": "PR", "kwh": "KWH", "to": "TNE", "tona": "TNE",
}


def _norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.strip().lower()


def _jud(judet):
    n = _norm(judet)
    if not n:
        return ""
    v = _JUD.get(n)
    if v:
        return v
    u = n.upper().replace(" ", "")
    if u.startswith("RO-"):
        u = u[3:]
    return ("RO-" + u) if u in _CODURI_JUD else ""


def _um(um):
    return _UM.get(_norm(um)) or "C62"


def _D(x):
    return Decimal(str(x if x not in (None, "") else 0))


def _bani(x):
    """Rotunjire fiscala: 2 zecimale, ROUND_HALF_UP (regula iConta, nu round())."""
    return _D(x).quantize(_D("0.01"), rounding=ROUND_HALF_UP)


def _num(x):
    return str(_bani(x))


def _e(s):
    return _xml_escape(str(s)) if s is not None else ""


def _vatid(cui):
    """CUI -> RO+cifre (identificator VAT, pentru platitor TVA)."""
    digits = "".join(ch for ch in str(cui or "") if ch.isdigit())
    return ("RO" + digits) if digits else ""


# ============================================================
#  LOADER — din schema CURENTA
# ============================================================
def incarca_factura(conn, schema, factura_id):
    """
    Citeste factura + linii + emitent (firma_profil) + cumparator (tert_* pe factura),
    pe schema curenta. Intoarce (factura, linii, furnizor, client) - dict-uri simple.
    Cumparatorul e denormalizat pe factura (tert_nume/tert_cui/tert_adresa); nu mai
    exista tabelul `clienti` cu adresa structurata din build-ul vechi.
    """
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"""SELECT id, numar, serie, data_emitere, data_scadenta, moneda,
                               tert_nume, tert_cui, tert_adresa, taxare_inversa,
                               tip, storno_din_id, total, tva
                          FROM {schema}.facturi WHERE id = %s""", (int(factura_id),))
        factura = cur.fetchone()
        if not factura:
            raise ValueError("factura %s inexistenta in %s" % (factura_id, schema))
        cur.execute(f"""SELECT descriere, um, cantitate, pret_unitar, cota_tva
                          FROM {schema}.factura_linii WHERE factura_id = %s ORDER BY id""",
                    (int(factura_id),))
        linii = cur.fetchall()
        cur.execute(f"""SELECT nume, cui, reg_com, adresa, oras, judet, cod_postal, iban,
                               platitor_tva
                          FROM {schema}.firma_profil WHERE id = 1""")
        furnizor = cur.fetchone()
    if not furnizor:
        raise ValueError("firma_profil (emitent) neconfigurat in %s" % schema)
    if not linii:
        raise ValueError("factura %s nu are linii" % factura_id)
    client = {
        "nume": factura.get("tert_nume"),
        "cui": factura.get("tert_cui"),
        "adresa": factura.get("tert_adresa"),
        "oras": None, "judet": None, "cod_postal": None,   # nestructurat in schema (limita v1)
    }
    return dict(factura), [dict(l) for l in linii], dict(furnizor), client


# ============================================================
#  GENERATOR XML — PUR (fara DB/retea)
# ============================================================
def genereaza_xml(factura, linii, furnizor, client):
    """
    Construieste XML-ul UBL 2.1 / CIUS-RO dintr-o factura + linii + emitent + cumparator.
    Pur: nu atinge DB/retea. Rotunjire fiscala ROUND_HALF_UP. Vezi LIMITE v1 in docstring.
    """
    if factura.get("taxare_inversa"):
        raise NotImplementedError("taxare inversa (categorie AE) - netratat in v1, se adauga dupa TEST")
    moneda = (factura.get("moneda") or "RON").strip() or "RON"
    numar_complet = "%s%s" % (factura.get("serie") or "", factura.get("numar") or "")

    # --- calcule pe linii, grupate pe cota ---
    line_net = []
    grup = {}  # cota (str) -> baza
    for l in linii:
        cota = _D(l.get("cota_tva") if l.get("cota_tva") is not None else 0)
        net = _bani(_D(l.get("cantitate")) * _D(l.get("pret_unitar")))
        line_net.append((l, cota, net))
        grup[str(cota)] = grup.get(str(cota), _D0) + net

    line_ext = _bani(sum((n for _, _, n in line_net), _D0))
    tax_subtotals = []
    tax_total = _D0
    for cota_s, baza in grup.items():
        cota = _D(cota_s)
        taxa = _bani(baza * cota / _D("100"))
        tax_total += taxa
        cat = "S" if cota > 0 else "Z"   # v1: doar standard (S) / cota zero (Z)
        tax_subtotals.append((_bani(baza), taxa, cat, cota))
    tax_total = _bani(tax_total)
    tax_incl = _bani(line_ext + tax_total)

    sup_vat = _vatid(furnizor.get("cui")) if furnizor.get("platitor_tva") else ""
    cli_vat = _vatid(client.get("cui"))
    sup_jud = _jud(furnizor.get("judet"))

    P = []
    P.append('<?xml version="1.0" encoding="UTF-8"?>')
    P.append('<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
             'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
             'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">')
    P.append('<cbc:CustomizationID>%s</cbc:CustomizationID>' % CUSTOMIZATION_ID)
    P.append('<cbc:ID>%s</cbc:ID>' % _e(numar_complet))
    P.append('<cbc:IssueDate>%s</cbc:IssueDate>' % _e(factura.get("data_emitere")))
    if factura.get("data_scadenta"):
        P.append('<cbc:DueDate>%s</cbc:DueDate>' % _e(factura.get("data_scadenta")))
    P.append('<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>')
    P.append('<cbc:DocumentCurrencyCode>%s</cbc:DocumentCurrencyCode>' % _e(moneda))

    # --- Furnizor (emitent) ---
    P.append('<cac:AccountingSupplierParty><cac:Party>')
    P.append('<cac:PostalAddress>')
    P.append('<cbc:StreetName>%s</cbc:StreetName>' % _e(furnizor.get("adresa") or "-"))
    P.append('<cbc:CityName>%s</cbc:CityName>' % _e(furnizor.get("oras") or "-"))
    if furnizor.get("cod_postal"):
        P.append('<cbc:PostalZone>%s</cbc:PostalZone>' % _e(furnizor.get("cod_postal")))
    if sup_jud:
        P.append('<cbc:CountrySubentity>%s</cbc:CountrySubentity>' % sup_jud)
    P.append('<cac:Country><cbc:IdentificationCode>RO</cbc:IdentificationCode></cac:Country>')
    P.append('</cac:PostalAddress>')
    if sup_vat:
        P.append('<cac:PartyTaxScheme><cbc:CompanyID>%s</cbc:CompanyID>'
                 '<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>' % _e(sup_vat))
    P.append('<cac:PartyLegalEntity>')
    P.append('<cbc:RegistrationName>%s</cbc:RegistrationName>' % _e(furnizor.get("nume") or "-"))
    if furnizor.get("reg_com"):
        P.append('<cbc:CompanyID>%s</cbc:CompanyID>' % _e(furnizor.get("reg_com")))
    P.append('</cac:PartyLegalEntity>')
    P.append('</cac:Party></cac:AccountingSupplierParty>')

    # --- Cumparator ---
    # LIMITA v1: schema are doar adresa libera (tert_adresa). CityName = oras daca vine,
    # altfel adresa libera (fallback documentat) ca BT-52 sa nu fie gol; TEST confirma.
    P.append('<cac:AccountingCustomerParty><cac:Party>')
    P.append('<cac:PostalAddress>')
    P.append('<cbc:StreetName>%s</cbc:StreetName>' % _e(client.get("adresa") or "-"))
    P.append('<cbc:CityName>%s</cbc:CityName>' % _e(client.get("oras") or client.get("adresa") or "-"))
    if client.get("cod_postal"):
        P.append('<cbc:PostalZone>%s</cbc:PostalZone>' % _e(client.get("cod_postal")))
    if _jud(client.get("judet")):
        P.append('<cbc:CountrySubentity>%s</cbc:CountrySubentity>' % _jud(client.get("judet")))
    P.append('<cac:Country><cbc:IdentificationCode>RO</cbc:IdentificationCode></cac:Country>')
    P.append('</cac:PostalAddress>')
    if cli_vat:
        P.append('<cac:PartyTaxScheme><cbc:CompanyID>%s</cbc:CompanyID>'
                 '<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>' % _e(cli_vat))
    P.append('<cac:PartyLegalEntity>')
    P.append('<cbc:RegistrationName>%s</cbc:RegistrationName>' % _e(client.get("nume") or "-"))
    P.append('</cac:PartyLegalEntity>')
    P.append('</cac:Party></cac:AccountingCustomerParty>')

    # --- PaymentMeans (IBAN) ---
    if furnizor.get("iban"):
        P.append('<cac:PaymentMeans><cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>'
                 '<cac:PayeeFinancialAccount><cbc:ID>%s</cbc:ID></cac:PayeeFinancialAccount>'
                 '</cac:PaymentMeans>' % _e(furnizor.get("iban")))

    # --- TaxTotal ---
    P.append('<cac:TaxTotal>')
    P.append('<cbc:TaxAmount currencyID="%s">%s</cbc:TaxAmount>' % (moneda, _num(tax_total)))
    for baza, taxa, cat, cota in tax_subtotals:
        P.append('<cac:TaxSubtotal>')
        P.append('<cbc:TaxableAmount currencyID="%s">%s</cbc:TaxableAmount>' % (moneda, _num(baza)))
        P.append('<cbc:TaxAmount currencyID="%s">%s</cbc:TaxAmount>' % (moneda, _num(taxa)))
        P.append('<cac:TaxCategory><cbc:ID>%s</cbc:ID><cbc:Percent>%s</cbc:Percent>'
                 '<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory>'
                 % (cat, _num(cota)))
        P.append('</cac:TaxSubtotal>')
    P.append('</cac:TaxTotal>')

    # --- LegalMonetaryTotal ---
    P.append('<cac:LegalMonetaryTotal>')
    P.append('<cbc:LineExtensionAmount currencyID="%s">%s</cbc:LineExtensionAmount>' % (moneda, _num(line_ext)))
    P.append('<cbc:TaxExclusiveAmount currencyID="%s">%s</cbc:TaxExclusiveAmount>' % (moneda, _num(line_ext)))
    P.append('<cbc:TaxInclusiveAmount currencyID="%s">%s</cbc:TaxInclusiveAmount>' % (moneda, _num(tax_incl)))
    P.append('<cbc:PayableAmount currencyID="%s">%s</cbc:PayableAmount>' % (moneda, _num(tax_incl)))
    P.append('</cac:LegalMonetaryTotal>')

    # --- Linii ---
    for idx, (l, cota, net) in enumerate(line_net, start=1):
        cat = "S" if cota > 0 else "Z"
        P.append('<cac:InvoiceLine>')
        P.append('<cbc:ID>%d</cbc:ID>' % idx)
        P.append('<cbc:InvoicedQuantity unitCode="%s">%s</cbc:InvoicedQuantity>'
                 % (_um(l.get("um")), _e(l.get("cantitate"))))
        P.append('<cbc:LineExtensionAmount currencyID="%s">%s</cbc:LineExtensionAmount>' % (moneda, _num(net)))
        P.append('<cac:Item><cbc:Name>%s</cbc:Name>' % _e(l.get("descriere") or "-"))
        P.append('<cac:ClassifiedTaxCategory><cbc:ID>%s</cbc:ID><cbc:Percent>%s</cbc:Percent>'
                 '<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory>'
                 % (cat, _num(cota)))
        P.append('</cac:Item>')
        P.append('<cac:Price><cbc:PriceAmount currencyID="%s">%s</cbc:PriceAmount></cac:Price>'
                 % (moneda, _num(l.get("pret_unitar"))))
        P.append('</cac:InvoiceLine>')

    P.append('</Invoice>')
    return "\n".join(P)


def genereaza_din_factura(conn, schema, factura_id):
    """Convenienta: loader + generator intr-un pas. Intoarce (xml, factura)."""
    factura, linii, furnizor, client = incarca_factura(conn, schema, factura_id)
    return genereaza_xml(factura, linii, furnizor, client), factura
