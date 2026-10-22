# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.1 (verbatim în DECIZII „Comanda 11.1”), subagentul Q — C86: o factură EMISĂ venită din XML-ul e-Factura
(`/import-efactura`, `uc_tenants._factura_importata`; `facturi.xml` îl scrie numai importul) a fost emisă și transmisă în SPV în altă parte.

  (1) nu se mai trimite în SPV: serverul refuză numit (`efactura_trimitere.refuz_din_efactura`, poarta 0 a lui `trimite`, verificată și de
      ruta `uc_tenants.factura_trimite_spv` înaintea conexiunii SPV), iar detaliul și lista o poartă cu `din_efactura` (eticheta de pe ecran,
      în locul butonului „Trimite în SPV”), fără „netrimisă · termen depășit”;
  (2) stornarea ei poartă pe fiecare linie `valoare_neta = −BT-131` (`facturi_api.storneaza` -> `creeaza_factura`), deci nota, D300, D394,
      D406 și XML-ul e-Factura al stornării iau exact −100,50 (nu 3,333 × 30,15 = −100,49).

Temei. Normă: OUG 120/2021 art.4 alin.(3) „Factura electronică se transmite de către emitent în sistemul național privind factura
electronică RO e-Factura.”; alin.(6) „Exemplarul original al facturii electronice se consideră fișierul de tip XML însoțit de sigiliul
electronic al Ministerului Finanțelor.” (anaf_surse/oug_120_2021.txt) — originalul există, o a doua încărcare ar fi o dublură în SPV (regulă
de produs; legea nu are un text „o singură dată”). CF art.330 alin.(1) lit.b): factura de corecție cuprinde „informațiile din factura
inițială, numărul și data facturii corectate, valorile cu semnul minus” (anaf_surse/cod_fiscal_227_2015_consolidat.txt). Structură (EN 16931,
regulă de validator, nu normă): BR-DEC-23 „The allowed maximum number of decimals for the Invoice line net amount (BT-131) is 2.”
Schemă efemeră din tenant_template, în tranzacție anulată. CUI-urile: cifra de control verificată în `test_cui_de_test_valid`."""
import contextlib
import io
import os
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from core import db as _db
from core import efactura_import as _ef
from core import tenant_provisioning as _tp

_SCHEMA = "tenant_test_lot11_q"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_D = Decimal
_CUI_FIRMA, _CUI_TERT = "9010105", "14399840"
_NS = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
       "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}


def _cui_valid(cui):   # CLAUDE.md „Date de test — CUI/CNP”: algoritmul oficial al cifrei de control
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = (sum(int(corp[i]) * ch[i] for i in range(9)) * 10) % 11
    return (0 if r == 10 else r) == ctrl


def test_cui_de_test_valid():
    assert _cui_valid(_CUI_FIRMA) and _cui_valid(_CUI_TERT)


def _xml(numar, furnizor, client):
    """XML e-Factura minim (UBL 2.1 / CIUS-RO), o linie: 3,333 bucăți, BT-131 = 100,50 lei (preț 30,1530…), TVA 21% = 21,11."""
    cm = 'currencyID="RON"'
    parte = ('<cac:%s><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>'
             '</cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>%s</cbc:RegistrationName></cac:PartyLegalEntity></cac:Party>'
             '</cac:%s>')
    return "".join([
        '<?xml version="1.0" encoding="UTF-8"?><Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        'xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" '
        'xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">',
        "<cbc:ID>%s</cbc:ID><cbc:IssueDate>2026-07-10</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>" % numar,
        parte % ("AccountingSupplierParty", furnizor[0], furnizor[1], "AccountingSupplierParty"),
        parte % ("AccountingCustomerParty", client[0], client[1], "AccountingCustomerParty"),
        "<cac:TaxTotal><cbc:TaxAmount %s>21.11</cbc:TaxAmount><cac:TaxSubtotal><cbc:TaxableAmount %s>100.50</cbc:TaxableAmount>"
        "<cbc:TaxAmount %s>21.11</cbc:TaxAmount><cac:TaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent><cac:TaxScheme><cbc:ID>VAT"
        "</cbc:ID></cac:TaxScheme></cac:TaxCategory></cac:TaxSubtotal></cac:TaxTotal>" % (cm, cm, cm),
        "<cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount %s>100.50</cbc:TaxExclusiveAmount><cbc:TaxInclusiveAmount %s>121.61"
        "</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>" % (cm, cm),
        '<cac:InvoiceLine><cbc:ID>1</cbc:ID><cbc:InvoicedQuantity unitCode="H87">3.333</cbc:InvoicedQuantity><cbc:LineExtensionAmount %s>'
        "100.50</cbc:LineExtensionAmount><cac:Item><cbc:Name>Marfa Q</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21"
        "</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory></cac:Item><cac:Price>"
        "<cbc:PriceAmount %s>30.1530</cbc:PriceAmount></cac:Price></cac:InvoiceLine></Invoice>" % (cm, cm)])


_FIRMA, _TERT = (_CUI_FIRMA, "Q SRL"), (_CUI_TERT, "DANTE INTERNATIONAL SA")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    """Conexiunea fixturii dată codului care deschide singur conexiuni (`db.get_conn`): commit-ul lui nu iese din tranzacția anulată."""
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def rollback(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def conn_q():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, regim_fiscal, platitor_tva, tip_decont, "
                    "tva_la_incasare, platitor_tva_anaf_inceput, declarant_nume, declarant_prenume, declarant_functie, forma_juridica, "
                    "capital_subscris, telefon, reg_com, serie_factura) VALUES (1,'Q SRL',%s,'Str Test 1','Sector 1','B','4690','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'lunar',false,'2025-01-01','Popescu','Ion','ADMINISTRATOR','SRL',200,'0712345678',"
                    "'J40/1/2020','QF')", (_CUI_FIRMA,))
            yield _FaraCommit(conn)
        finally:
            conn.rollback()


def _importa(conn, xml):
    """Drumul importului (`uc_tenants._factura_importata`, cel al rutei `/import-efactura`). Datele de pornire pe care XML-ul minim nu le
    are (adresa clientului, statutul lui de TVA) se pun pe factură, ca stornarea să poată pleca în e-Factura (BR-RO-110) și în D394."""
    from core import uc_tenants
    f = _ef.parseaza_xml(xml.encode(), _CUI_FIRMA)
    with conn.cursor() as cur:
        fid, nou = uc_tenants._factura_importata(cur, _SCHEMA, f)
        assert nou
        cur.execute("UPDATE facturi SET tert_platitor_tva = true, tert_adresa = 'Str. Test 2', tert_oras = 'Sector 2', tert_judet = 'B' "
                    "WHERE id = %s", (fid,))
    return fid


def _emisa_din_aplicatie(conn):
    from core import facturi_api
    r = facturi_api.creeaza_factura(conn, "QF7", "2026-07-11", "emisa", [{"descriere": "Marfa A", "cantitate": 1, "pret_unitar": 100,
                                    "cota_tva": 21, "um": "buc", "cont_venit": "707"}], tert_nume="DANTE INTERNATIONAL SA",
                                    tert_cui="RO14399840", tert_adresa="Str. Test 2", tert_oras="Sector 2", tert_judet="B", status="emisa")
    return r["factura_id"]


def _conn_ca_pool(monkeypatch, modul, conn):
    """`modul.db.get_conn()` dă conexiunea fixturii (schema efemeră e vizibilă numai în tranzacția ei)."""
    @contextlib.contextmanager
    def _gc(*_a, **_k):
        yield conn
    monkeypatch.setattr(modul.db, "get_conn", _gc)


# ── (1) trimiterea în SPV ────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_refuzul_numeste_factura_emisa_venita_din_xml(conn_q):
    from core import efactura_trimitere as _eft
    emisa_xml = _importa(conn_q, _xml("Q-EMISA-1", _FIRMA, _TERT))
    primita_xml = _importa(conn_q, _xml("Q-PRIMITA-1", _TERT, _FIRMA))
    din_aplicatie = _emisa_din_aplicatie(conn_q)
    r = _eft.refuz_din_efactura(conn_q, _SCHEMA, emisa_xml)
    # OUG 120/2021 art.4 alin.(3) + (6): factura a fost transmisă de emitent, originalul e XML-ul ei — nu a doua oară
    # [lotul 11, AT] refuzul e o afirmație tipată: câmpurile contractului lui `trimite` / al rutei rămân (stare, cod, mesaj), plus felul
    assert (r["fel"], r["stare"], r["cod"], r["mesaj"]) == ("fapt", "din_efactura", "FACTURA_DIN_EFACTURA", _eft.MESAJ_DIN_EFACTURA), r
    assert _eft.MESAJ_DIN_EFACTURA == ("Factura a venit din e-Factura: e deja transmisă în SPV de programul care a emis-o (aplicația are "
                                       "XML-ul ei). Nu se mai trimite de aici — XML-ul s-ar reface din cantitate × preț, iar aceeași factură "
                                       "ar ajunge de două ori în SPV.")
    assert _eft.refuz_din_efactura(conn_q, _SCHEMA, din_aplicatie) is None   # emisă în aplicație: se trimite ca până acum
    assert _eft.refuz_din_efactura(conn_q, _SCHEMA, primita_xml) is None     # primită: nu e a firmei de trimis (nici n-ar ajunge aici)
    print("refuz:", r["cod"], "|", r["mesaj"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_trimite_se_opreste_la_poarta_0_fara_token_si_fara_xml_refacut(conn_q, monkeypatch):
    """`efactura_trimitere.trimite` (orchestrarea, orice apelant): poarta 0 înaintea tokenului, a generării XML-ului și a încărcării."""
    from core import efactura_send as _es, efactura_trimitere as _eft, spv_conector
    fid = _importa(conn_q, _xml("Q-EMISA-2", _FIRMA, _TERT))
    _conn_ca_pool(monkeypatch, _eft, conn_q)

    def _interzis(*_a, **_k):
        raise AssertionError("factura venită din e-Factura a trecut de poarta 0")
    monkeypatch.setattr(spv_conector, "ia_token_activ", _interzis)
    monkeypatch.setattr(_es, "genereaza_xml", _interzis)
    monkeypatch.setattr(_es, "upload_ubl", _interzis)
    r = _eft.trimite(_SCHEMA, fid, principal=("firm", 1), mediu="test")
    assert r["stare"] == "din_efactura" and r["cod"] == "FACTURA_DIN_EFACTURA", r
    with conn_q.cursor() as cur:
        cur.execute("SELECT count(*) FROM efactura_trimiteri WHERE factura_id = %s", (fid,))
        assert cur.fetchone()[0] == 0   # niciun rând «pregătit»: nimic n-a plecat spre ANAF
    print("trimite:", r["stare"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ruta_refuza_numit_inaintea_conexiunii_spv(conn_q, monkeypatch):
    """`uc_tenants.factura_trimite_spv` (ruta `POST /facturi/{id}/trimite-spv`): 409 cu codul, înainte de principalul SPV; factura emisă în
    aplicație trece de verificare și ajunge la principalul SPV, ca până acum."""
    from core import auth_api, efactura_trimitere as _eft, erori as _erori, uc_tenants
    imp = _importa(conn_q, _xml("Q-EMISA-3", _FIRMA, _TERT))
    app = _emisa_din_aplicatie(conn_q)
    _conn_ca_pool(monkeypatch, uc_tenants, conn_q)
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: _SCHEMA)

    class _Principal(Exception):
        pass

    def _principal(ctx):
        raise _Principal()
    monkeypatch.setattr(uc_tenants._spv_rute, "spv_principal", _principal)
    with pytest.raises(_erori.Conflict) as e:
        uc_tenants.factura_trimite_spv(1, imp, {"uid": 1})
    assert (e.value.detaliu["cod"], e.value.detaliu["mesaj"]) == ("FACTURA_DIN_EFACTURA", _eft.MESAJ_DIN_EFACTURA), e.value.detaliu
    with pytest.raises(_Principal):
        uc_tenants.factura_trimite_spv(1, app, {"uid": 1})
    print("ruta:", e.value.detaliu["cod"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_detaliul_si_lista_poarta_eticheta_fara_termen_spv(conn_q):
    """Detaliul (`facturi_api.detalii_factura`) și lista (`lista_facturi`): factura venită din XML are `din_efactura` = eticheta de pe ecran
    (în locul butonului „Trimite în SPV”) și nu mai e „netrimisă în SPV · termen … (depășit)”; factura emisă în aplicație rămâne cum era."""
    from core import efactura_trimitere as _eft, facturi_api
    imp = _importa(conn_q, _xml("Q-EMISA-4", _FIRMA, _TERT))
    app = _emisa_din_aplicatie(conn_q)
    d = facturi_api.detalii_factura(conn_q, imp)
    assert d["din_efactura"] == _eft.ETICHETA_DIN_EFACTURA == "a venit din e-Factura: e deja transmisă în SPV" and d["stare_spv"] is None, (
        d["din_efactura"], d["stare_spv"])
    a = facturi_api.detalii_factura(conn_q, app)
    assert a["din_efactura"] is None and a["stare_spv"]["stare"] == "netrimisa", a["stare_spv"]
    lista = {f["id"]: f for f in facturi_api.lista_facturi(conn_q, 2026, 7)}
    assert (lista[imp]["din_efactura"], lista[imp]["stare_spv"]) == (_eft.ETICHETA_DIN_EFACTURA, None)
    assert lista[app]["din_efactura"] is None and lista[app]["stare_spv"]["stare"] == "netrimisa"


# ── (2) stornarea ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _storno(conn):
    from core import facturi_api
    fid = _importa(conn, _xml("Q-EMISA-5", _FIRMA, _TERT))
    s = facturi_api.storneaza(conn, fid)
    return fid, s


def _note(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.factura_id = %s ORDER BY l.id", (fid,))
        return [(a, b, _D(c)) for a, b, c in cur.fetchall()]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_stornarea_poarta_minus_bt131_pe_linie_si_in_nota(conn_q):
    fid, s = _storno(conn_q)
    with conn_q.cursor() as cur:
        cur.execute("SELECT cantitate, pret_unitar, valoare_neta FROM factura_linii WHERE factura_id = %s", (s["factura_id"],))
        linie = cur.fetchone()
        cur.execute("SELECT total, tva FROM facturi WHERE id = %s", (s["factura_id"],))
        antet = cur.fetchone()
    # CF art.330 alin.(1) lit.b): valorile facturii inițiale, cu semnul minus — BT-131 = 100,50, nu 3,333 × 30,15 = 100,49
    assert linie == (_D("-3.333"), _D("30.15"), _D("-100.50")), linie
    assert antet == (_D("-121.61"), _D("-21.11")), antet   # TVA 100,50 × 21% = 21,105 -> 21,11 (din 100,49: 21,10)
    note = _note(conn_q, s["factura_id"])
    sume = sorted(abs(x) for _a, _b, x in note)
    assert sume == [_D("21.11"), _D("100.50")], note   # nota stornării: −100,50 venit, −21,11 TVA (nu −100,49 / −21,10)
    print("stornarea: linia", tuple(str(x) for x in linie), "| antet", tuple(str(x) for x in antet), "| nota",
          [(a, b, str(x)) for a, b, x in note])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_stornarea_in_d300_d394_d406_ia_exact_minus_100_50(conn_q):
    import datetime as _dt
    from core import d300, d394, d406
    from core.common import Perioada
    _fid, s = _storno(conn_q)
    with conn_q.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata', document_ref = COALESCE(NULLIF(document_ref, ''), 'Q') "
                    "WHERE status <> 'validata'")
    azi = _dt.date.today()   # stornarea se emite azi (`facturi_api.storneaza`)
    _x, res = d300.genereaza(conn_q, _SCHEMA, Perioada(azi.year, luna=azi.month))
    # D300 rd.9 (livrări 21%): −100,50 -> −101 / −21,11 -> −21 (din cantitate × preț: −100,49 -> −100)
    assert (res.R.get("R9_1"), res.R.get("R9_2")) == (-101, -21), res.R
    _x394, r394 = d394.genereaza(conn_q, _SCHEMA, Perioada(azi.year, luna=azi.month))
    l394 = {c: (int(v["bazaL"]), int(v["tvaL"])) for c, v in r394.rezumat2.items() if v.get("bazaL") or v.get("tvaL")}
    assert l394 == {21: (-101, -21)}, l394
    x406, _r = d406.genereaza(conn_q, _SCHEMA, azi.year, azi.month)
    loc = lambda t: t.rsplit("}", 1)[-1]   # noqa: E731
    sume = [_D(e.text) for inv in ET.fromstring(x406.encode("utf-8")).iter() if loc(inv.tag) == "SalesInvoices"
            for ln in inv.iter() if loc(ln.tag) == "InvoiceLineAmount" for e in ln if loc(e.tag) == "Amount"]
    assert sume and all(abs(x) == _D("100.50") for x in sume), sume   # D406 SalesInvoices: InvoiceLine Amount = BT-131 al stornării
    print("D300 R9:", (res.R.get("R9_1"), res.R.get("R9_2")), "| D394 L:", l394, "| D406 Amount:", [str(x) for x in sume])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_xml_e_factura_al_stornarii_are_bt131_minus_100_50(conn_q):
    """Stornarea e o factură nouă, emisă în aplicație: pleacă în SPV (OUG 120/2021 art.4 alin.(10) — „Factura electronică corectată se
    transmite în cadrul aceluiași sistem național privind factura electronică RO e-Factura”), cu BT-131 din contabilitate (−100,50)."""
    from core import efactura_trimitere as _eft
    _fid, s = _storno(conn_q)
    assert _eft.refuz_din_efactura(conn_q, _SCHEMA, s["factura_id"]) is None   # stornarea nu vine din XML: se trimite
    xml, _f = _eft.genereaza_din_factura(conn_q, _SCHEMA, s["factura_id"])
    rad = ET.fromstring(xml.encode("utf-8"))
    linie = rad.find("cac:InvoiceLine", _NS)
    assert linie.findtext("cbc:LineExtensionAmount", namespaces=_NS) == "-100.50", xml   # BR-DEC-23: BT-131 = cel din contabilitate
    assert rad.findtext("cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount", namespaces=_NS) == "-100.50"
    assert rad.findtext("cac:TaxTotal/cbc:TaxAmount", namespaces=_NS) == "-21.11"
    assert rad.findtext("cac:LegalMonetaryTotal/cbc:PayableAmount", namespaces=_NS) == "-121.61"
    print("XML stornare: BT-131", linie.findtext("cbc:LineExtensionAmount", namespaces=_NS), "| BT-110",
          rad.findtext("cac:TaxTotal/cbc:TaxAmount", namespaces=_NS))


# ── garda ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_garda_incarcarea_in_spv_trece_numai_prin_trimite_dupa_poarta_0():
    """GARDA: orice încărcare în SPV (`efactura_send.upload_ubl`) din codul de producție stă numai în `efactura_trimitere.trimite`, iar acolo
    poarta 0 (`refuz_din_efactura`) e chemată înaintea tokenului, a generării XML-ului și a încărcării. Un drum nou de trimitere (retrimitere,
    trimitere în masă, o coadă) care ar încărca în SPV ocolind poarta pică aici."""
    import ast
    gasite = []
    for d, _sub, fisiere in os.walk(_RAD):
        if any(p in d for p in ("/venv", "/.git", "/node_modules", "/frontend_test", "/anaf_surse", "/ghid")):
            continue
        for n in fisiere:
            if not n.endswith(".py") or n.startswith("test_") or n == "conftest.py":
                continue
            cale = os.path.join(d, n)
            try:
                arb = ast.parse(io.open(cale, encoding="utf-8").read())
            except (SyntaxError, UnicodeDecodeError):
                continue
            for fn in ast.walk(arb):
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for x in ast.walk(fn):
                    if isinstance(x, ast.Call) and getattr(x.func, "attr", getattr(x.func, "id", None)) == "upload_ubl":
                        gasite.append((os.path.relpath(cale, _RAD), fn.name))
    assert sorted(set(gasite)) == [("core/efactura_trimitere.py", "trimite")], sorted(set(gasite))
    arb = ast.parse(io.open(os.path.join(_RAD, "core/efactura_trimitere.py"), encoding="utf-8").read())
    fn = next(x for x in arb.body if isinstance(x, ast.FunctionDef) and x.name == "trimite")
    linii = {}
    for x in ast.walk(fn):
        if isinstance(x, ast.Call):
            nume = getattr(x.func, "attr", getattr(x.func, "id", None))
            linii.setdefault(nume, x.lineno)
    assert set(linii) >= {"refuz_din_efactura"}, "poarta 0 a dispărut din `trimite`"
    for dupa in ("ia_token_activ", "genereaza_xml", "upload_ubl", "insereaza_trimitere_pregatita"):
        assert linii["refuz_din_efactura"] < linii[dupa], (dupa, linii)
