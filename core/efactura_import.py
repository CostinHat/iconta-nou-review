# -*- coding: utf-8 -*-
"""Import e-Factura (UBL 2.1 / CIUS-RO) - parser PUR.
Extrage: numar (cbc:ID), data (cbc:IssueDate), scadenta (cbc:DueDate),
furnizor/client (nume + CUI din cac:AccountingSupplierParty/CustomerParty),
total cu TVA (cbc:TaxInclusiveAmount), TVA (cac:TaxTotal/cbc:TaxAmount),
moneda (cbc:DocumentCurrencyCode), linii (cac:InvoiceLine).
Directia se decide comparand CUI furnizor cu CUI-ul firmei:
furnizor = firma -> emisa; altfel -> primita."""
import re
import zipfile
import io
import xml.etree.ElementTree as ET

NS = {
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}

def _txt(el, cale):
    g = el.find(cale, NS)
    return (g.text or "").strip() if g is not None and g.text else ""

def _cui_norm(cui):
    return re.sub(r"^RO", "", (cui or "").strip().upper()).strip()

def _pret_efectiv(cant, pret, baza_linie, baza_qty):
    """[A10, 18.09.2026] Prețul unitar EFECTIV al liniei, ca `cantitate × pret` să dea baza REALĂ.
    UBL: `LineExtensionAmount` e netul liniei DUPĂ `AllowanceCharge` și cu `BaseQuantity` deja aplicat —
    e sursa autoritară. Dacă e prezent, întoarce `LineExtensionAmount / cantitate`. Dacă lipsește, cade
    pe `PriceAmount / BaseQuantity` (prețul e per `BaseQuantity` unități, nu per unitate). Fără asta, o
    reducere pe linie sau un preț „la 1000 buc" supradeclară baza în D300/D394 (linia = cantitate × preț)."""
    from decimal import Decimal, InvalidOperation

    def _d(x):
        try:
            return Decimal(str(x))
        except (InvalidOperation, ValueError, TypeError):
            return None
    q = _d(cant)
    if q is None or q == 0:
        q = Decimal(1)
    le = _d(baza_linie)
    if le is not None:
        return str(le / q)
    p = _d(pret) or Decimal(0)
    bq = _d(baza_qty)
    if bq is not None and bq != 0:
        p = p / bq
    return str(p)


def _parte(el, tag):
    """Nume + CUI dintr-un cac:AccountingSupplierParty/AccountingCustomerParty."""
    p = el.find(f"cac:{tag}/cac:Party", NS)
    if p is None:
        return "", ""
    nume = (_txt(p, "cac:PartyLegalEntity/cbc:RegistrationName")
            or _txt(p, "cac:PartyName/cbc:Name"))
    cui = (_txt(p, "cac:PartyTaxScheme/cbc:CompanyID")
           or _txt(p, "cac:PartyLegalEntity/cbc:CompanyID"))
    return nume, cui

def parseaza_xml(continut, cui_firma):
    """continut: bytes/str XML UBL. Returneaza dict factura sau ValueError."""
    if isinstance(continut, bytes):
        continut = continut.decode("utf-8-sig", errors="replace")
    try:
        root = ET.fromstring(continut)
    except ET.ParseError as e:
        raise ValueError(f"XML invalid: {e}")
    if not root.tag.endswith("}Invoice"):
        raise ValueError("nu este factura UBL (root != Invoice)")
    numar = _txt(root, "cbc:ID")
    data = _txt(root, "cbc:IssueDate")
    if not numar or not data:
        raise ValueError("lipsesc cbc:ID sau cbc:IssueDate")
    furn_nume, furn_cui = _parte(root, "AccountingSupplierParty")
    cli_nume, cli_cui = _parte(root, "AccountingCustomerParty")
    total = _txt(root, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount") or "0"
    tva = _txt(root, "cac:TaxTotal/cbc:TaxAmount") or "0"
    moneda = _txt(root, "cbc:DocumentCurrencyCode") or "RON"
    scadenta = _txt(root, "cbc:DueDate") or None
    emisa = _cui_norm(furn_cui) == _cui_norm(cui_firma)
    tert = (cli_nume, cli_cui) if emisa else (furn_nume, furn_cui)
    linii = []
    for ln in root.findall("cac:InvoiceLine", NS):
        cant = _txt(ln, "cbc:InvoicedQuantity") or "1"
        linii.append({
            "descriere": _txt(ln, "cac:Item/cbc:Name"),
            "cantitate": cant,
            # [A10] pret EFECTIV: baza = LineExtensionAmount (net dupa AllowanceCharge/BaseQuantity),
            # nu cantitate x PriceAmount brut. Vezi `_pret_efectiv`.
            "pret_unitar": _pret_efectiv(
                cant, _txt(ln, "cac:Price/cbc:PriceAmount") or "0",
                _txt(ln, "cbc:LineExtensionAmount"), _txt(ln, "cac:Price/cbc:BaseQuantity")),
            "cota_tva": _txt(ln, "cac:Item/cac:ClassifiedTaxCategory/cbc:Percent") or "0",
        })
    return {
        "numar": numar, "data_emitere": data, "data_scadenta": scadenta,
        "directie": "emisa" if emisa else "primita",
        "tert_nume": tert[0], "tert_cui": tert[1],
        "total": total, "tva": tva, "moneda": moneda,
        "linii": linii, "xml": continut,
    }

def extrage_fisiere(nume, continut):
    """Un upload: .xml -> [continut]; .zip -> toate .xml din arhiva (fara semnatura)."""
    if nume.lower().endswith(".zip"):
        out = []
        with zipfile.ZipFile(io.BytesIO(continut)) as z:
            for n in z.namelist():
                if n.lower().endswith(".xml") and "semnatura" not in n.lower():
                    out.append((n, z.read(n)))
        return out
    return [(nume, continut)]
