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
        linii.append({
            "descriere": _txt(ln, "cac:Item/cbc:Name"),
            "cantitate": _txt(ln, "cbc:InvoicedQuantity") or "1",
            "pret_unitar": _txt(ln, "cac:Price/cbc:PriceAmount") or "0",
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
