# -*- coding: utf-8 -*-
"""Import e-Factura (UBL 2.1 / CIUS-RO) - parser PUR.
Extrage: numar (cbc:ID), data (cbc:IssueDate), scadenta (cbc:DueDate),
furnizor/client (nume + CUI din cac:AccountingSupplierParty/CustomerParty),
total cu TVA (cbc:TaxInclusiveAmount), TVA (cac:TaxTotal/cbc:TaxAmount),
moneda (cbc:DocumentCurrencyCode), linii (cac:InvoiceLine).
Directia se decide comparand CUI furnizor cu CUI-ul firmei:
furnizor = firma -> emisa; altfel -> primita."""
import zipfile
import io
import xml.etree.ElementTree as ET

from core import cui_forma as _forma_cui

NS = {
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}

def _txt(el, cale):
    g = el.find(cale, NS)
    return (g.text or "").strip() if g is not None and g.text else ""

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

def _tax_total_document(root, moneda):
    """`cac:TaxTotal` cu BT-110 (TVA-ul facturii în moneda documentului, cu defalcarea BG-23), sau None. EN 16931, legarea UBL: BT-110 =
    `TaxTotal/TaxAmount` cu `currencyID` = moneda documentului (BT-5); BT-111 = alt `TaxTotal`, în moneda de contabilizare a TVA-ului
    (BT-6), fără `TaxSubtotal`. Ordinea lor în fișier nu e impusă, deci se aleg după monedă (apoi după defalcare)."""
    tts = root.findall("cac:TaxTotal", NS)
    for tt in tts:
        ta = tt.find("cbc:TaxAmount", NS)
        if ta is not None and (ta.get("currencyID") or moneda) == moneda:
            return {"el": tt, "tva": (ta.text or "").strip()}
    for tt in tts:
        if tt.find("cac:TaxSubtotal", NS) is not None:
            return {"el": tt, "tva": _txt(tt, "cbc:TaxAmount")}
    return {"el": tts[0], "tva": _txt(tts[0], "cbc:TaxAmount")} if tts else None


def tva_lei_din_xml(root, moneda):
    """[lotul 11, C81] BT-111 — TVA-ul total al facturii în moneda de contabilizare a TVA-ului (BT-6, `cbc:TaxCurrencyCode`), când aceea
    e leul și factura e în altă monedă; altfel None. Ghidul MF al e-Factura (anaf_surse/mf_ghid_coduri_facturi_efactura_v2_9.txt): când
    moneda facturii (BT-5) e alta decât „RON”, „este necesară completarea elementului BT-6 – codul monedei de contabilizare, cu respectarea
    următoarei reguli: «dacă este menţionat codul monedei de contabilizare a TVA (BT-6), atunci trebuie să se indice totalul TVA al facturii
    în moneda de contabilizare (BT-111)»” (EN 16931 BR-53). În UBL, BT-111 = `cac:TaxTotal/cbc:TaxAmount` cu `currencyID` = BT-6.
    E TVA-ul „exprimat în lei” pe care CF art.319 alin.(20) lit.j îl cere facturii — sursa TVA-ului în lei al facturii primite."""
    bt6 = (_txt(root, "cbc:TaxCurrencyCode") or "").strip().upper()
    if bt6 != "RON" or (moneda or "RON").strip().upper() == "RON":
        return None
    for tt in root.findall("cac:TaxTotal", NS):
        ta = tt.find("cbc:TaxAmount", NS)
        if ta is not None and (ta.get("currencyID") or "").strip().upper() == "RON" and (ta.text or "").strip():
            return ta.text.strip()
    return None


def linii_nivel_document(root):
    """[lotul 11, C80] Reducerile (BG-20) și taxele suplimentare (BG-21) la nivelul FACTURII, ca linii ale facturii, fiecare pe categoria și
    cota ei de TVA. EN 16931 (artefactele de validare CEN, `EN16931-model.sch`, regulă de structură, nu normă):
      BR-CO-13 „Invoice total amount without VAT (BT-109) = Σ Invoice line net amount (BT-131) - Sum of allowances on document level (BT-107)
      + Sum of charges on document level (BT-108).”
      BR-S-08 „[...] the VAT category taxable amount (BT-116) [...] shall equal the sum of Invoice line net amounts (BT-131) plus the sum of
      document level charge amounts (BT-99) minus the sum of document level allowance amounts (BT-92) where the VAT category code (BT-151,
      BT-102, BT-95) is "Standard rated" and the VAT rate (BT-152, BT-103, BT-96) equals the VAT category rate (BT-119).”
    Deci baza fiecărei cote e a liniilor ei MINUS reducerile ei PLUS taxele ei: ca linie (cantitate 1, valoare −BT-92 / +BT-99, cota
    BT-96 / BT-103, categoria BT-95 / BT-102), reducerea intră în baza cotei pe TOATE drumurile care citesc liniile (contare, D300, D394,
    D406), iar Σ liniilor = BT-109. Înainte, importul citea numai `cac:InvoiceLine`: baza din linii ≠ BT-109, iar 401 nu închidea BT-112.
    UBL: `cac:AllowanceCharge` copil direct al `Invoice` (cel de pe linie e al liniei, inclus deja în BT-131), `cbc:ChargeIndicator`
    false = reducere / true = taxă, `cbc:Amount`, `cbc:AllowanceChargeReason`, `cac:TaxCategory/cbc:ID` + `cbc:Percent`."""
    from decimal import Decimal
    out = []
    for ac in root.findall("cac:AllowanceCharge", NS):
        taxa = (_txt(ac, "cbc:ChargeIndicator") or "").strip().lower() == "true"
        suma = (_txt(ac, "cbc:Amount") or "").strip()
        if not suma:
            continue
        motiv = _txt(ac, "cbc:AllowanceChargeReason") or _txt(ac, "cbc:AllowanceChargeReasonCode")
        val = str(Decimal(suma) if taxa else -Decimal(suma))
        out.append({
            "descriere": ("Taxă suplimentară" if taxa else "Reducere") + " la nivelul facturii" + (": %s" % motiv if motiv else ""),
            "cantitate": "1", "pret_unitar": val, "valoare_neta": val,
            "cota_tva": _txt(ac, "cac:TaxCategory/cbc:Percent") or "0",
            "categorie_tva": (_txt(ac, "cac:TaxCategory/cbc:ID") or "").strip().upper() or None,
            "nivel_document": True,
        })
    return out


def tva_cote_din_xml(continut):
    """[lotul 11, C79] TVA-ul FACTURII pe cote, cum l-a scris furnizorul — nu recalculat din baze.

    CF art.319 alin.(20) lit.j: factura cuprinde „indicarea cotei de taxă aplicate și a sumei taxei colectate, exprimate în lei, în
    funcție de cotele taxei”; CF art.299 alin.(1) lit.a: deducerea cere ca beneficiarul „să dețină o factură emisă în conformitate cu
    prevederile art. 319” — taxa dedusă e deci cea înscrisă pe factură. În XML-ul e-Factura (EN 16931) ea stă în defalcarea TVA BG-23
    (`cac:TaxTotal/cac:TaxSubtotal`, unul pe categorie și cotă): BT-116 baza, BT-117 TVA-ul, BT-118 categoria, BT-119 cota.

    Întoarce [{"categorie", "cota", "baza", "tva", "sursa"}] (sume și cotă ca text zecimal, în moneda documentului):
      * cu BG-23: un rând pe `TaxSubtotal` (sursa „BG-23”); cota lipsă (categoriile fără cotă, ex. „O”) = „0”;
      * fără BG-23 (XML în afara EN 16931 BR-CO-18, „An Invoice shall at least have one VAT breakdown group (BG-23)”) și cu O SINGURĂ cotă pe
        linii: BT-110 pe cota aceea (sursa „BT-110”) — e singura cotă căreia îi poate aparține —, cu baza de pe factură: BT-109 (totalul fără
        TVA), altfel Σ BT-131 (valorile nete ale liniilor, tot de pe factură);
      * altfel []: fără defalcare, pe mai multe cote, TVA-ul facturii nu se poate împărți fără a ghici — contarea și D300 rămân pe liniile
        facturii (regula unică, `core/tva_calcul.py`).
    `continut` = textul / octeții XML-ului, sau rădăcina deja citită (`parseaza_xml`)."""
    if isinstance(continut, (bytes, bytearray)):
        continut = continut.decode("utf-8-sig", errors="replace")
    root = ET.fromstring(continut) if isinstance(continut, str) else continut
    moneda = _txt(root, "cbc:DocumentCurrencyCode") or "RON"
    tt = _tax_total_document(root, moneda)
    if tt is None:
        return []
    out = []
    for st in tt["el"].findall("cac:TaxSubtotal", NS):
        out.append({"categorie": (_txt(st, "cac:TaxCategory/cbc:ID") or "").strip().upper() or None,
                    "cota": _txt(st, "cac:TaxCategory/cbc:Percent") or "0",
                    "baza": _txt(st, "cbc:TaxableAmount") or "0",
                    "tva": _txt(st, "cbc:TaxAmount") or "0", "sursa": "BG-23"})
    if out:
        return out
    linii = root.findall("cac:InvoiceLine", NS)
    doc = linii_nivel_document(root)   # [lotul 11, C80] reducerile / taxele de document au și ele cota lor (BT-96 / BT-103)
    cote = {_txt(ln, "cac:Item/cac:ClassifiedTaxCategory/cbc:Percent") or "0" for ln in linii} | {d["cota_tva"] for d in doc}
    if len(cote) == 1 and tt["tva"]:
        from decimal import Decimal
        cat = {(_txt(ln, "cac:Item/cac:ClassifiedTaxCategory/cbc:ID") or "").strip().upper() or None for ln in linii}
        # BT-109, altfel BR-CO-13: Σ BT-131 − Σ BT-92 + Σ BT-99 (tot de pe factură)
        baza = (_txt(root, "cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount")
                or str(sum((Decimal(_txt(ln, "cbc:LineExtensionAmount") or "0") for ln in linii), Decimal(0))
                       + sum((Decimal(d["valoare_neta"]) for d in doc), Decimal(0))))
        return [{"categorie": cat.pop() if len(cat) == 1 else None, "cota": cote.pop(), "baza": baza, "tva": tt["tva"],
                 "sursa": "BT-110"}]
    return []


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
    moneda = _txt(root, "cbc:DocumentCurrencyCode") or "RON"
    # [lotul 11, C79] BT-110 = `TaxTotal/TaxAmount` în MONEDA DOCUMENTULUI; un al doilea `TaxTotal` (BT-111, în `TaxCurrencyCode`, fără
    # defalcare) poate sta înaintea lui. Înainte se lua primul, oricare ar fi fost.
    tva = (_tax_total_document(root, moneda) or {}).get("tva") or "0"
    scadenta = _txt(root, "cbc:DueDate") or None
    # [lotul 11, decizia Costin 10.3 pct.4] furnizorul = firma? — codul în forma păstrată, pe ambele părți (`cui_forma.stocare`)
    emisa = (_forma_cui.stocare(furn_cui) or "") == (_forma_cui.stocare(cui_firma) or "")
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
            # [lotul 6 pct.7c, 273] codul categoriei de TVA al liniei (BT-151): S / E / AE / O … — ghidul MF al codurilor e-Factura
            # (anaf_surse/mf_ghid_coduri_facturi_efactura_v2_9.txt, cap.3): „AE” = taxare inversă (art.331 Cod fiscal)
            "categorie_tva": (_txt(ln, "cac:Item/cac:ClassifiedTaxCategory/cbc:ID") or "").strip().upper() or None,
            # [lotul 11, C82] BT-131, valoarea netă a liniei de pe factură, păstrată exact (`factura_linii.valoare_neta`): prețul unitar
            # de mai sus se ține la 2 zecimale, iar pe o cantitate neîntreagă cantitate × preț nu mai reface BT-131 la ban
            "valoare_neta": _txt(ln, "cbc:LineExtensionAmount") or None,
        })
    # [lotul 11, C80] reducerile / taxele la nivelul facturii (BG-20 / BG-21), ca linii pe cota lor: Σ liniilor = BT-109 (BR-CO-13)
    linii += linii_nivel_document(root)
    # [deficiența 418a] BT-31, codul de TVA al vânzătorului (`PartyTaxScheme` cu schema VAT): îl are numai vânzătorul înregistrat în scopuri
    # de TVA (EN 16931 BR-S-02: factura cu TVA standard cere BT-31)
    furn_cod_tva = None
    for pts in root.findall("cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme", NS):
        if (_txt(pts, "cac:TaxScheme/cbc:ID") or "").strip().upper() == "VAT":
            furn_cod_tva = (_txt(pts, "cbc:CompanyID") or "").strip() or None
    return {
        "numar": numar, "data_emitere": data, "data_scadenta": scadenta,
        "furnizor_cod_tva": furn_cod_tva,
        "directie": "emisa" if emisa else "primita",
        "tert_nume": tert[0], "tert_cui": tert[1],
        "total": total, "tva": tva, "moneda": moneda,
        # [lotul 11, C79] TVA-ul FACTURII pe cote (BG-23), cum l-a scris furnizorul — sursa TVA-ului deductibil (`tva_cote_din_xml`)
        "tva_cote": tva_cote_din_xml(root),
        # [lotul 11, C81] BT-111: TVA-ul facturii în lei, scris de furnizor (factura în valută cu BT-6 = RON), sau None
        "tva_lei_xml": tva_lei_din_xml(root, moneda),
        # [273] o factură primită cu linii „AE” e cu taxare inversă: la beneficiar 4426 = 4427 (art.331), în D300 rd.12 / rd.25
        "taxare_inversa": any(l["categorie_tva"] == "AE" for l in linii),
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
