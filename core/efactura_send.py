# -*- coding: utf-8 -*-
"""
core/efactura_send.py — e-Factura TRIMITERE: generator XML UBL 2.1 / CIUS-RO (F126/F160).

PASUL 1 (FAZA constructie e-Factura): generator PUR de XML + loader pe schema CURENTA +
config host FCTEL intr-o singura constanta. NU face retea aici (upload/stare = pasul 2).

Reutilizeaza STRUCTURA XML dovedita in build-ul vechi (_efx_build_xml), dar:
  - loader rescris pe schema curenta (facturi.tert_*, factura_linii, firma_profil) -
    build-ul vechi citea dintr-un tabel `clienti` care nu mai exista;
  - rotunjire fiscala explicita (Decimal + ROUND_HALF_UP, regula iConta), nu round().

HOST-uri e-Factura (VERIFICAT LIVE 18.07 - trei metode, trei host-uri; DECIZII.md):
  - UPLOAD/stare/descarcare prin OAuth (Bearer)  -> api.anaf.ro/{prod|test}/FCTEL/rest
    (TLS standard, accepta token; DOVADA: 200 cu token, 401 fara).
  - VALIDARE structura (fara token/drept)         -> webservicesp.anaf.ro/prod/FCTEL/rest/validare/{std}
  - Metoda cu CERTIFICAT (mTLS)                    -> webserviceapl.anaf.ro (cere cert client;
    DOVADA: TLS handshake FAILURE fara certificat - inutilizabil server-side pe OAuth).
Corectie fata de nota 18.07 care pusese webserviceapl pentru upload (aia e ruta mTLS).
Fiecare host = o SINGURA constanta; upload/stare/descarcare o refolosesc, nu o rescriu.

LIMITE v1 (de confirmat pe TEST la pasul 2, NU ghicite aici):
  - Cumparatorul are in schema doar tert_nume/tert_cui/tert_adresa (adresa libera);
    CIUS-RO cere oras (BT-52). Pana cand formularul de factura capteaza orasul separat,
    CityName = oras (daca vine) altfel adresa libera - fallback documentat, TEST confirma.
  - Doar factura standard cu TVA (categorii S/Z). taxare_inversa (AE), neplatitor TVA (O),
    storno/nota de credit (381) NU sunt tratate in v1 - se adauga dupa confirmare pe TEST.
"""
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import escape as _xml_escape

from core.common import cfg

# ============================================================
#  CONFIG HOST — env citit LA APEL (cfg), o singura sursa per host
# ============================================================
def fctel_base(mode="prod"):
    """Baza REST e-Factura (OAuth) pentru mode 'prod'/'test'. SINGURA sursa a host-ului.
    Host din EFACTURA_FCTEL_BASE (implicit api.anaf.ro/%s/FCTEL/rest), citit la apel."""
    mode = (mode or "prod").strip().lower()
    if mode not in ("prod", "test"):
        mode = "prod"
    return cfg("EFACTURA_FCTEL_BASE", "https://api.anaf.ro/%s/FCTEL/rest") % mode


def fctel_validare_url(standard="FACT1"):
    """URL validator de structura (schematron CIUS-RO), FARA token. SINGURA sursa.
    Din EFACTURA_VALIDARE_URL (implicit webservicesp.anaf.ro/.../validare/%s), citit la apel."""
    return cfg("EFACTURA_VALIDARE_URL",
               "https://webservicesp.anaf.ro/prod/FCTEL/rest/validare/%s") % standard


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


_SECTOR_RE = re.compile(r"sector\s*([1-6])", re.IGNORECASE)


class EDateIncomplete(ValueError):
    """Date de factura insuficiente pentru un XML valid (ex. sector Bucuresti lipsa).
    Butonul de trimitere blocheaza cu mesajul asta, NU trimite structura falsa."""


def _localitate(judet_code, oras, adresa="", eticheta="firma"):
    """CityName (BT-37 vanzator / BT-52 cumparator). eFactura regula BR-RO-100 (validator ANAF):
    in Bucuresti (RO-B) localitatea trebuie sa fie SECTOR1..6, NU 'Bucuresti'. In rest = orasul.
    STRICT (funcționalitatea F160): daca e Bucuresti dar NU se extrage clar sectorul din oras+adresa, NU
    inventa unul -> ridica EDateIncomplete. Sector gresit derivat = nok sau, mai rau, factura
    acceptata cu date gresite. Filozofia control_incrucisat: gri (nu pot determina) nu se
    falsifica in verde."""
    if judet_code == "RO-B":
        m = _SECTOR_RE.search("%s %s" % (oras or "", adresa or ""))
        if m:
            return "SECTOR" + m.group(1)
        raise EDateIncomplete(
            "Localitate incompleta (%s): firma e in Bucuresti dar lipseste sectorul "
            "(SECTOR1..6) in adresa. Completeaza sectorul inainte de trimitere." % eticheta)
    return oras or "-"


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
                               tert_nume, tert_cui, tert_adresa, tert_oras, tert_judet,
                               taxare_inversa, tip, storno_din_id, total, tva
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
        "oras": factura.get("tert_oras"),
        "judet": factura.get("tert_judet"),
        "cod_postal": None,   # cod postal cumparator: inca nestructurat (optional BT-53)
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
    P.append('<cbc:CityName>%s</cbc:CityName>' % _e(_localitate(sup_jud, furnizor.get("oras"), furnizor.get("adresa"), "vanzator")))
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

    # --- Cumparator --- (BT-52 oras, BT-54 judet - obligatorii pt RO, vezi eFactura regula BR-RO-110 / eFactura regula BR-RO-100)
    cli_jud = _jud(client.get("judet"))
    P.append('<cac:AccountingCustomerParty><cac:Party>')
    P.append('<cac:PostalAddress>')
    P.append('<cbc:StreetName>%s</cbc:StreetName>' % _e(client.get("adresa") or "-"))
    P.append('<cbc:CityName>%s</cbc:CityName>' % _e(_localitate(cli_jud, client.get("oras"), client.get("adresa"), "cumparator")))
    if client.get("cod_postal"):
        P.append('<cbc:PostalZone>%s</cbc:PostalZone>' % _e(client.get("cod_postal")))
    if cli_jud:
        P.append('<cbc:CountrySubentity>%s</cbc:CountrySubentity>' % cli_jud)
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


def valideaza(xml, standard="FACT1"):
    """
    Valideaza STRUCTURA XML pe validatorul oficial ANAF (schematron CIUS-RO), FARA token si
    FARA drept pe CIF - validare pura, publica. E judecatorul de structura (ca DUK pentru
    declaratii): sursa de adevar, nu presupunerea din memorie. Intoarce (ok: bool, mesaje: list).
    Apel direct (nu apel_anaf): endpoint fara autentificare, nu e un apel SPV.
    """
    import requests
    r = requests.post(fctel_validare_url(standard), data=xml.encode("utf-8"),
                      headers={"Content-Type": "text/plain"}, timeout=45)
    try:
        j = r.json()
    except ValueError:
        return False, ["raspuns non-JSON de la validator: %s" % (r.text or "")[:400]]
    ok = (j.get("stare") == "ok")
    mesaje = [m.get("message", "") for m in (j.get("Messages") or [])]
    return ok, mesaje


# ============================================================
#  TRIMITERE SPV — prin apel_anaf (pasul 2). TOATE apelurile ANAF trec prin conector.
# ============================================================
import hashlib
from core import db
from core import spv_conector


def _parse_upload(text):
    """Din raspunsul XML al /upload: (execution_status, index_incarcare, [errorMessage...])."""
    t = text or ""
    ex = re.search(r'ExecutionStatus="(\d+)"', t)
    idx = re.search(r'index_incarcare="(\d+)"', t)
    errs = re.findall(r'errorMessage="([^"]*)"', t)
    return (int(ex.group(1)) if ex else None,
            idx.group(1) if idx else None, errs)


def _parse_stare(text):
    """Din raspunsul /stareMesaj: (stare, id_descarcare)."""
    t = text or ""
    st = re.search(r'stare="([^"]*)"', t)
    idd = re.search(r'id_descarcare="(\d+)"', t)
    return (st.group(1) if st else None, idd.group(1) if idd else None)


def upload_ubl(principal, cif, xml, mediu="test"):
    """POST /upload?standard=UBL&cif=X prin apel_anaf (pe tokenul principalului). Intoarce Response."""
    url = "%s/upload?standard=UBL&cif=%s" % (fctel_base(mediu), cif)
    return spv_conector.apel_anaf(principal, "POST", url, data=xml.encode("utf-8"),
                                  headers={"Content-Type": "application/xml"}, timeout=60)


def stare_mesaj(principal, index_incarcare, mediu="test"):
    """GET /stareMesaj?id_incarcare=N prin apel_anaf. Intoarce Response."""
    url = "%s/stareMesaj?id_incarcare=%s" % (fctel_base(mediu), index_incarcare)
    return spv_conector.apel_anaf(principal, "GET", url, timeout=30)


def descarca(principal, id_descarcare, mediu="test"):
    """GET /descarcare?id=N prin apel_anaf. Intoarce Response (ZIP in .content).
    Partajata intre F178 (poll recipise) si primirea F126 (facturi furnizori) - un singur client."""
    url = "%s/descarcare?id=%s" % (fctel_base(mediu), id_descarcare)
    return spv_conector.apel_anaf(principal, "GET", url, timeout=120)


def principal_pentru_schema(conn, schema):
    """Token owner (Principal) pentru o schema tenant: cabinet daca accounting_firm_id setat, altfel
    gratuit (tenant). Partajat de cr-oanele SPV (poll F178 + receive F179) - un singur loc."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name=%s", (schema,))
        r = cur.fetchone()
    if not r:
        raise ValueError("schema %s fara tenant public" % schema)
    tid, afid = r
    return spv_conector.principal_firm(afid) if afid is not None else spv_conector.principal_tenant(tid)


def lista_mesaje(principal, cif, mediu="test", zile=3, filtru="P"):
    """
    GET listaMesajeFactura?zile=N&cif=X&filtru=F prin apel_anaf (pe tokenul principalului).
    Intoarce (mesaje, eroare): mesaje = lista de dict-uri cu campurile ANAF (id = id de descarcare,
    id_solicitare = indexul incarcarii, data_creare, tip, cif_emitent, cif_beneficiar, detalii);
    eroare = textul din campul 'eroare' (ex. fara mesaje / fara drept) sau None.

    Parametri VERIFICATI LA SURSA OFICIALA (mfinante.gov.ro, doc API e-Factura; vezi ARHITECTURA_SPV.md):
      - zile: 1..60 OBLIGATORIU (fereastra); cif: numeric OBLIGATORIU.
      - filtru (optional): E=erori, T=trimisa, P=PRIMITA (facturi de la furnizori), R=mesaj cumparator.
    Limita: listaMesajeFactura = 1500 apeluri/zi/CUI.

    GARD PENTRU APELANT (cron receive, la construcTie): filtru=P intoarce ce a marcat ANAF ca 'primita',
    dar dedup+import TREBUIE sa confirme cif_beneficiar == CIF-ul tenantului (nu doar tip=P). Pe un token
    de cabinet care acopera N CIF-uri, factura importata se leaga de tenantul al carui CIF e cif_beneficiar,
    nu de primul din bucla - altfel scurgere intre chiriasi.
    """
    zile = max(1, min(int(zile), 60))
    cifn = "".join(c for c in str(cif) if c.isdigit())
    url = "%s/listaMesajeFactura?zile=%d&cif=%s&filtru=%s" % (fctel_base(mediu), zile, cifn, filtru)
    r = spv_conector.apel_anaf(principal, "GET", url, timeout=60)
    try:
        j = r.json()
    except ValueError:
        return [], "raspuns non-JSON de la listaMesajeFactura: %s" % (r.text or "")[:300]
    if isinstance(j, dict) and j.get("eroare"):
        return [], j.get("eroare")
    if isinstance(j, dict):
        return (j.get("mesaje") or []), None
    return [], "forma neasteptata listaMesajeFactura: %s" % str(j)[:200]


def trimite(schema, factura_id, principal, mediu="test"):
    """
    Trimite o factura in SPV cu PORTILE IN ORDINE FIXA (niciuna sarita):
      1) TOKEN VIU: principalul are token activ? altfel stare='fara_token' (conecteaza ANAF intai).
      2) VALIDARE/FACT1 (Regula 1): structura valida la validatorul ANAF? altfel stare='nevalidat'
         + erorile BR-RO, FARA upload. Diferentiatorul vs SmartBill: nu trimitem gunoi.
      3) IDEMPOTENCY: exista deja send VIU (incarcat/in_prelucrare/ok) pe factura+mediu? altfel
         stare='deja_trimisa'. Upload-ul ANAF NU e idempotent - dubla trimitere = dubla factura.
      4) UPLOAD prin apel_anaf pe tokenul principalului -> scrie randul INDIFERENT de rezultat
         (ok/eroare_upload + error_message integral).
    Poll-ul (stareMesaj/descarcare) ramane pe cron, NU sincron aici. Intoarce {stare, ...}.
    genereaza_din_factura poate ridica EDateIncomplete (sector Bucuresti lipsa) / NotImplementedError
    (taxare inversa) - apelantul (ruta) le mapeaza la 422.
    """
    # P0: genereaza XML (poate ridica EDateIncomplete/NotImplementedError -> prinse de ruta)
    with db.get_conn() as conn:
        # POARTA 1: token viu?
        if spv_conector.ia_token_activ(conn, principal) is None:
            return {"stare": "fara_token", "mesaj": "Conectează ANAF (SPV) înainte de a trimite factura."}
        xml, _factura = genereaza_din_factura(conn, schema, factura_id)
        with conn.cursor() as cur:
            cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
            cif = "".join(c for c in str(cur.fetchone()[0] or "") if c.isdigit())
    sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()

    # POARTA 2: validare structura pe validatorul ANAF - FARA upload daca nok
    val_ok, val_msg = valideaza(xml)
    if not val_ok:
        return {"stare": "nevalidat", "validare_ok": False, "validare_mesaje": val_msg}

    # POARTA 3: idempotency (send viu existent) + insert 'pregatit' in aceeasi tranzactie
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""SELECT id, stare FROM {schema}.efactura_trimiteri
                WHERE factura_id=%s AND mediu=%s AND stare IN ('incarcat','in_prelucrare','ok')
                LIMIT 1""", (factura_id, mediu))
            viu = cur.fetchone()
            if viu:
                return {"stare": "deja_trimisa", "trimitere_id": viu[0], "stare_existenta": viu[1]}
            cur.execute(f"""INSERT INTO {schema}.efactura_trimiteri
                (factura_id, mediu, stare, xml_trimis, xml_sha256, trimis_la)
                VALUES (%s,%s,'pregatit',%s,%s, now()) RETURNING id""",
                        (factura_id, mediu, xml, sha))
            tid = cur.fetchone()[0]

    rez = {"trimitere_id": tid, "cif": cif, "xml_sha256": sha, "mediu": mediu, "validare_ok": True}

    # POARTA 4: upload real prin apel_anaf (scrie randul indiferent de rezultat)
    try:
        r = upload_ubl(principal, cif, xml, mediu)
        text = r.text or ""
        ex, index, errs = _parse_upload(text)
        rez.update({"http": r.status_code, "execution_status": ex,
                    "index_incarcare": index, "errors": errs, "raspuns": text})
        if r.status_code == 200 and ex == 0 and index:
            stare, errmsg = "incarcat", None
        else:
            stare, errmsg = "nok", ("\n".join(errs) if errs else text[:4000])
    except spv_conector.EroareSpvFaraDrept as e:
        # 403 = certificatul nu are drept (CIF/serviciu) - NU e eroare de structura
        rez.update({"http": 403, "execution_status": None, "index_incarcare": None,
                    "errors": [], "raspuns": str(e), "fara_drept": True})
        stare, errmsg, index, ex = "eroare_upload", "403 fara drept SPV: %s" % e, None, None
    except Exception as e:
        rez.update({"http": None, "execution_status": None, "index_incarcare": None,
                    "errors": [], "raspuns": str(e)})
        stare, errmsg, index, ex = "eroare_upload", "exceptie upload: %s" % str(e)[:2000], None, None

    # 3) scrie rezultatul complet (commit) - INDIFERENT de rezultat
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE {schema}.efactura_trimiteri
                SET stare=%s, index_incarcare=%s, execution_status=%s, error_message=%s,
                    actualizat_la=now(),
                    finalizat_la=CASE WHEN %s IN ('nok','eroare_upload') THEN now() ELSE finalizat_la END
                WHERE id=%s""",
                        (stare, index, ex, errmsg, stare, tid))
    rez["stare"] = stare
    return rez
