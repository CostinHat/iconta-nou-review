# -*- coding: utf-8 -*-
"""
Teste D406 (SAF-T) — core/d406.py.

Apara explicit regresiile gasite si reparate pe 16.07.2026 (toate confirmate pe
validatorul oficial DUK, tenant_002/iunie 2026 = stare valid):
  1. Transaction cere CustomerID SI SupplierID (minOccurs=1 in XSD) - lipseau complet.
  2. Fiecare TransactionLine cere AMBELE (CustomerID + SupplierID) - se emitea doar unul.
  3. Liniile fara partener (707, 4427, banca) primesc codul PROPRIU pe ambele, nu "0"/"0"
     (regula GL.28/GL.29 nota [17]); niciodata ambele "0" (regula sintactica).
  4. SourceDocuments: sub-sectiunile goale se OMIT; MovementOfGoods e gol self-closed.

Testul de VALIDARE ruleaza pe un profil MINIM construit manual (nu pe datele unei
firme reale) - "valid pe un caz real incomplet" nu dovedeste structura completa
(CLAUDE.md, metoda de investigare fiscala pct. 3). CUI-urile folosite sunt reale si
deja acceptate de validator (DANTE 14399840, ALTEX 4221306) - nu inventate.
"""
import os
from decimal import Decimal
from datetime import date
import pytest
from core import d406 as m

# --- profil minim izolat, toate campurile completate ---
PROF = {"cui": "14399840", "nume": "FIRMA TEST SRL", "adresa": "Str. Test 1",
        "oras": "Bucuresti", "cod_postal": "010101", "baza_contabila": "A",
        "platitor_tva": True}

CUI_CLIENT = "004221306"     # 00 + ALTEX (RO4221306), format S.C.1

def _conturi():
    return [m.Cont(id="4111", descriere="Clienti", cont_standard="4111", tip="Activ"),
            m.Cont(id="707", descriere="Venituri marfuri", cont_standard="707", tip="Pasiv"),
            m.Cont(id="4427", descriere="TVA colectata", cont_standard="4427", tip="Pasiv"),
            m.Cont(id="401", descriere="Furnizori", cont_standard="401", tip="Pasiv"),
            m.Cont(id="371", descriere="Marfuri", cont_standard="371", tip="Activ"),
            m.Cont(id="4426", descriere="TVA deductibila", cont_standard="4426", tip="Activ")]

def _client():
    return [m.Partener(id=CUI_CLIENT, nume="ALTEX ROMANIA SRL", cui="RO4221306", oras="Bucuresti")]

def _nota_client():
    # nota cu partener real pe 4111 si linii fara partener pe 707/4427
    return m.Nota(id="1", data=date(2026, 6, 10), descriere="Contare factura 1", linii=[
        m.LinieNota(record_id="1", cont="4111", descriere="", debit=Decimal("1210"),
                    credit=Decimal("0"), cont_partener_id=CUI_CLIENT),
        m.LinieNota(record_id="2", cont="707", descriere="", debit=Decimal("0"),
                    credit=Decimal("1000"), cont_partener_id=CUI_CLIENT),
        m.LinieNota(record_id="3", cont="4427", descriere="", debit=Decimal("0"),
                    credit=Decimal("210"), cont_partener_id=CUI_CLIENT)])

def _factura_vanzare():
    linie = m.LinieFactura(nr=1, cont="707", descriere="Marfa", cantitate=Decimal("1"),
                           pret_unitar=Decimal("1000"), valoare=Decimal("1000"), sens="C",
                           tva_cod="310344", tva_procent=Decimal("21"), tva_suma=Decimal("210"))
    return m.Factura(nr="1", data=date(2026, 6, 10), partener_id=CUI_CLIENT,
                     partener_nume="ALTEX ROMANIA SRL", tip="380", cont="4111", linii=[linie])

def _res(note=None, fv=None, fc=None, plati=None):
    return m.construieste(PROF, 2026, 6, _conturi(), _client(), [],
                          note=note or [], facturi_vanzare=fv or [],
                          facturi_cumparare=fc or [], plati=plati or [])

def _xml(**kw):
    return m.build_xml(_res(**kw))


# ---------- regresie 1: CustomerID+SupplierID la nivel Transaction ----------
def test_transaction_are_ambele_id():
    xml = _xml(note=[_nota_client()])
    tx = xml.split("<Transaction>")[1].split("<TransactionLine>")[0]
    assert "<CustomerID>" in tx and "<SupplierID>" in tx

# ---------- regresie 2: fiecare TransactionLine are AMBELE ----------
def test_fiecare_linie_are_ambele_id():
    xml = _xml(note=[_nota_client()])
    linii = xml.split("<TransactionLine>")[1:]
    assert len(linii) == 3
    for l in linii:
        corp = l.split("</TransactionLine>")[0]
        assert corp.count("<CustomerID>") == 1, corp
        assert corp.count("<SupplierID>") == 1, corp

# ---------- regresie 3a: linia de client -> partener + supplier "0" ----------
def test_linie_client_partener_si_zero():
    xml = _xml(note=[_nota_client()])
    l4111 = [l for l in xml.split("<TransactionLine>")[1:] if "<AccountID>4111<" in l][0]
    assert "<CustomerID>%s</CustomerID>" % CUI_CLIENT in l4111
    assert "<SupplierID>0</SupplierID>" in l4111

# ---------- regresie 3b: linia fara partener -> cod PROPRIU pe ambele, nu 0/0 ----------
def test_linie_fara_partener_cod_propriu():
    xml = _xml(note=[_nota_client()])
    l707 = [l for l in xml.split("<TransactionLine>")[1:] if "<AccountID>707<" in l][0]
    cod = "00" + PROF["cui"]   # 0014399840
    assert "<CustomerID>%s</CustomerID>" % cod in l707
    assert "<SupplierID>%s</SupplierID>" % cod in l707
    # niciodata ambele "0"
    assert not ("<CustomerID>0</CustomerID>" in l707 and "<SupplierID>0</SupplierID>" in l707)

# ---------- regresie 4a: sectiunile goale se omit ----------
def test_sectiuni_goale_omise():
    xml = _xml(note=[_nota_client()])   # fara facturi, fara plati
    assert "<SalesInvoices>" not in xml
    assert "<PurchaseInvoices>" not in xml
    assert "<Payments>" not in xml

def test_sales_invoices_prezent_cand_exista():
    xml = _xml(note=[_nota_client()], fv=[_factura_vanzare()])
    assert "<SalesInvoices>" in xml
    assert "<InvoiceNo>1</InvoiceNo>" in xml

# ---------- regresie 4b: MovementOfGoods gol self-closed ----------
def test_movementofgoods_gol():
    xml = _xml(note=[_nota_client()])
    assert "<MovementOfGoods/>" in xml
    assert "<NumberOfMovementLines>" not in xml

# ---------- InvoiceType = cod, nu text ----------
def test_invoicetype_cod():
    xml = _xml(note=[_nota_client()], fv=[_factura_vanzare()])
    assert "<InvoiceType>380</InvoiceType>" in xml


# ---------- luna fara miscari: GL gol self-closed, depunere "pe zero" ----------
def test_luna_goala_gl_self_closed():
    xml = _xml()   # zero note, zero facturi
    assert "<GeneralLedgerEntries/>" in xml
    # nu fabricam nimic: fara Journal/Transaction partiale
    assert "<Journal>" not in xml and "<Transaction>" not in xml


# ---------- VALIDARE OFICIALA pe profil minim izolat (metoda pct. 3) ----------
def test_valid_pe_validatorul_oficial_profil_minim():
    from core import duk
    if not os.path.exists(duk.JAR_SAFT):
        pytest.skip("Validatorul SAF-T (DUKIntegrator_AnLunaUI.jar) nu e instalat.")
    xml = _xml(note=[_nota_client()], fv=[_factura_vanzare()])
    rez = duk.valideaza(xml, "d406", an=2026, luna=6)
    assert rez["stare"] == "valid", rez.get("erori")

def test_valid_luna_goala_pe_zero():
    """Luna fara nicio miscare -> D406 'pe zero' valid pe validatorul oficial."""
    from core import duk
    if not os.path.exists(duk.JAR_SAFT):
        pytest.skip("Validatorul SAF-T (DUKIntegrator_AnLunaUI.jar) nu e instalat.")
    xml = _xml()   # profil minim, zero miscari
    rez = duk.valideaza(xml, "d406", an=2026, luna=6)
    assert rez["stare"] == "valid", rez.get("erori")
