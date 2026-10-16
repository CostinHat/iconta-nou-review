# -*- coding: utf-8 -*-
"""274b — categoria de TVA pe orice linie cu 0% (decizia Costin 16.10.2026, răspunsul la raportul lotului 6 pct.1, verbatim în DECIZII):
„taxare inversă (AE), scutit cu drept de deducere (E), scutit fără drept de deducere (E), livrare intracomunitară scutită (K), export (G),
în afara sferei TVA. «Neplătitor» (O) nu e opțiune în listă; vine automat din regimul firmei neplătitoare.”

Temeiul fiecărei corespondențe (BT-151, rândul D300) e citat în `core/categorii_tva.py` (Ghidul MF e-Factura v2.9 cap.3; OPANAF 174/2026,
D300 rd.1, 13, 14, 15). Aici: (1) emiterea refuză linia 0% fără categorie și categoria nepotrivită cu țara clientului; (2) XML-ul poartă
categoria, motivul (BT-120) și codul VATEX (BT-121), O fără cotă și fără codurile de TVA ale părților, K cu livrarea; (3) D300 pune linia
pe rândul categoriei ei, iar o factură de dinainte rămâne cum era; (4) D300 generat cu rd.13 / 14 / 15 e valid pe DUK.
"""
import io
import xml.etree.ElementTree as ET

import pytest

from core import categorii_tva as ct
from core import efactura_send as ef
from core import db as _db, tenant_provisioning as _tp, d300 as _d300, duk as _duk
from core.common import Perioada

NS = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
      "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
FURN = {"nume": "FURNIZOR SRL", "cui": "14399840", "reg_com": "J40/1/2020", "adresa": "Str 1", "oras": "Cluj-Napoca", "judet": "CJ",
        "iban": "RO49AAAA1B31007593840000", "platitor_tva": True}
RO = {"nume": "CLIENT SRL", "cui": "18547290", "adresa": "Str 2", "oras": "Cluj-Napoca", "judet": "CJ", "tara": "RO"}
IE = {"nume": "GOOGLE IRELAND LIMITED", "cui": "IE6388047V", "adresa": "Gordon House", "oras": "Dublin", "judet": "Dublin", "tara": "IE"}
US = {"nume": "CUSTOMER INC", "cui": "US123456789", "adresa": "1 Main St", "oras": "New York", "judet": None, "tara": "US"}


def _linie(cat, cota=0):
    return {"descriere": "x", "um": "buc", "cantitate": 1, "pret_unitar": 100, "cota_tva": cota, "categorie_tva": cat}


# ── (1) emiterea ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_274b_linia_0_fara_categorie_se_refuza_pe_campul_ei():
    """MUTAȚIE: `if cat not in CATEGORII:` -> `if False:` -> linia 0% trece fără categorie -> pică."""
    linii = [_linie(None, 21), _linie(None)]
    rele = ct.verifica_linii(linii, True, "RO")
    assert [(r["camp"], r["cod"]) for r in rele] == [("em-l1-categorie", ct.COD_LIPSA)]
    assert linii[0]["categorie_tva"] is None, "linia taxabilă n-are categorie"


def test_274b_neplatitorul_primeste_O_automat_si_nu_alege():
    linii = [_linie(None), _linie("export")]
    assert ct.verifica_linii(linii, False, "RO") == []
    assert [l["categorie_tva"] for l in linii] == ["neplatitor", "neplatitor"]
    assert "neplatitor" not in [c["cod"] for c in ct.pentru_formular(True)] and ct.pentru_formular(False) == []


@pytest.mark.parametrize("cat, tara, bun", [("livrare_ic", "IE", True), ("livrare_ic", "RO", False), ("livrare_ic", "US", False),
                                            ("export", "US", True), ("export", "IE", False), ("taxare_inversa", "RO", True),
                                            ("taxare_inversa", "IE", False), ("scutit_cu_drept", "US", True)])
def test_274b_categoria_se_potriveste_cu_tara_clientului(cat, tara, bun):
    rele = ct.verifica_linii([_linie(cat)], True, tara)
    assert (rele == []) is bun and (bun or rele[0]["cod"] == "CATEGORIE_TVA_TARA"), rele


# ── (2) XML-ul e-Factura ───────────────────────────────────────────────────────────────────────────────────────────────────────
def _x(linii, client=RO, furnizor=FURN):
    return ET.fromstring(ef.genereaza_xml({"numar": "F1", "serie": "F", "data_emitere": "2026-10-16", "moneda": "RON"},
                                          linii, furnizor, client))


def _defalcare(root):
    return sorted((s.findtext("cac:TaxCategory/cbc:ID", namespaces=NS), s.findtext("cac:TaxCategory/cbc:Percent", namespaces=NS),
                   s.findtext("cac:TaxCategory/cbc:TaxExemptionReasonCode", namespaces=NS))
                  for s in root.findall("cac:TaxTotal/cac:TaxSubtotal", NS))


def test_274b_xml_poarta_categoria_motivul_si_codul_vatex():
    """MUTAȚIE: `d = _ct.descriere(...) or {...}` -> `d = {"ubl": "Z", ...}` -> toate liniile 0% ies „Z” -> pică.
    Probat pe validatorul ANAF FACT1 (16.10.2026): AE, E (trei), K, G, O — stare=ok (raportul lotului 6)."""
    r = _x([_linie("taxare_inversa"), _linie(None, 21), _linie("scutit_cu_drept"), _linie("scutit_fara_drept"),
            _linie("in_afara_sferei")])
    assert _defalcare(r) == [("AE", "0.00", "VATEX-EU-AE"), ("E", "0.00", None), ("E", "0.00", None), ("E", "0.00", None),
                             ("S", "21.00", None)], _defalcare(r)
    motive = sorted(s.findtext("cac:TaxCategory/cbc:TaxExemptionReason", namespaces=NS) or ""
                    for s in r.findall("cac:TaxTotal/cac:TaxSubtotal", NS))
    assert motive == sorted(["", ct.CATEGORII["taxare_inversa"]["mentiune"], ct.CATEGORII["scutit_cu_drept"]["mentiune"],
                             ct.CATEGORII["scutit_fara_drept"]["mentiune"], ct.CATEGORII["in_afara_sferei"]["mentiune"]])
    assert [c.text for c in r.findall("cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory/cbc:ID", NS)] == ["AE", "S", "E", "E", "E"]


def test_274b_livrarea_intracomunitara_are_livrarea_si_codul_de_tva_al_clientului():
    """MUTAȚIE: blocul `<cac:Delivery>` scos -> BR-IC-11 / BR-IC-12 -> pică."""
    r = _x([_linie("livrare_ic")], IE)
    assert _defalcare(r) == [("K", "0.00", "VATEX-EU-IC")]
    adr = r.find("cac:Delivery/cac:DeliveryLocation/cac:Address", NS)
    assert [adr.findtext("cbc:%s" % k, namespaces=NS) for k in ("StreetName", "CityName", "CountrySubentity")] == \
        ["Gordon House", "Dublin", "Dublin"] and adr.findtext("cac:Country/cbc:IdentificationCode", namespaces=NS) == "IE"
    cli = r.find("cac:AccountingCustomerParty/cac:Party", NS)
    assert cli.findtext("cac:PartyTaxScheme/cbc:CompanyID", namespaces=NS) == "IE6388047V"
    with pytest.raises(ef.EDateIncomplete):     # fără localitatea / regiunea clientului: spus, nu ghicit
        _x([_linie("livrare_ic")], dict(IE, judet=None))


def test_274b_exportul_si_neplatitorul_identifica_partile_fara_cod_de_tva():
    """MUTAȚIE: identificatorul legal al cumpărătorului (BT-47) scos -> validatorul ANAF răspunde BR-RO-120 / ERRIdentif -> pică."""
    g = _x([_linie("export")], US)
    assert _defalcare(g) == [("G", "0.00", "VATEX-EU-G")]
    cli = g.find("cac:AccountingCustomerParty/cac:Party", NS)
    assert cli.find("cac:PartyTaxScheme", NS) is None and cli.findtext("cac:PartyLegalEntity/cbc:CompanyID", namespaces=NS) == "US123456789"
    o = _x([_linie("neplatitor")], RO, dict(FURN, platitor_tva=False))
    assert _defalcare(o) == [("O", None, "VATEX-EU-O")], "O: fără cotă (BT-152)"
    furn = o.find("cac:AccountingSupplierParty/cac:Party", NS)
    cli = o.find("cac:AccountingCustomerParty/cac:Party", NS)
    assert furn.find("cac:PartyTaxScheme", NS) is None and cli.find("cac:PartyTaxScheme", NS) is None, "O: fără codurile de TVA"
    assert (furn.findtext("cac:PartyLegalEntity/cbc:CompanyID", namespaces=NS),
            cli.findtext("cac:PartyLegalEntity/cbc:CompanyID", namespaces=NS)) == ("14399840", "18547290")


# ── (3) D300, pur ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
_PROF = {"nume": "F SRL", "cui": "14399840", "platitor_tva": True, "tip_decont": "lunar", "tva_la_incasare": False}


def _f(linii, ti=False):
    return {"id": 1, "numar": "F1", "directie": "emisa", "taxare_inversa": ti, "tert_tara": "RO", "moneda": "RON", "curs_bnr": 1,
            "total": 0, "tva": 0, "linii": linii}


def test_274b_d300_pune_fiecare_categorie_pe_randul_ei():
    """MUTAȚIE: ramura `elif cat in _CAT_RAND:` scoasă -> liniile cad la „nu se clasifică automat” -> pică."""
    facturi = [_f([(1, 1000, 0, "taxabil", "scutit_cu_drept"), (1, 300, 0, "taxabil", "scutit_fara_drept"),
                   (1, 50, 0, "taxabil", "in_afara_sferei"), (1, 200, 21, "taxabil", None)]),
               _f([(1, 400, 0, "taxabil", "taxare_inversa"), (1, 100, 21, "taxabil", None)], ti=True)]
    res = _d300.calcul_d300(_PROF, Perioada(2026, luna=10), facturi)
    assert (res.R.get("R14_1"), res.R.get("R15_1"), res.R.get("R13_1"), res.R.get("R9_1"), res.R.get("R9_2")) == \
        (1000, 300, 400, 300, 63), res.R
    assert not [a for a in res.avertismente if "nu se clasifică automat" in a], res.avertismente
    assert [n for n in res.note_rezultat if "în afara sferei" in n], res.note_rezultat


def test_274b_factura_de_dinainte_ramane_cum_era():
    """Fără categorie pe linii: taxarea inversă de pe antet acoperă toate liniile (rd.13), iar linia 0% e semnalată ca până acum."""
    res = _d300.calcul_d300(_PROF, Perioada(2026, luna=10), [_f([(1, 500, 21, "taxabil")], ti=True), _f([(1, 70, 0, "taxabil")])])
    assert (res.R.get("R13_1"), res.R.get("R9_1", 0)) == (500, 0), res.R
    assert [a for a in res.avertismente if "nu se clasifică automat" in a], res.avertismente


# ── (4) emiterea pe o firmă efemeră + D300 pe DUK ───────────────────────────────────────────────────────────────────────────────
_SCH = "efemer_274b"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
                cur.execute("SET search_path TO %s, public" % _SCH)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,serie_factura) VALUES (1,'CAT SRL','14399840','Str 1','Cluj-Napoca','CJ',"
                            "'4669','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar','Popescu','Ion','ADMINISTRATOR','SRL',200,'CAT')")
            yield c
        finally:
            c.rollback()


def test_274b_emiterea_scrie_categoria_si_taxarea_inversa(conn):
    """MUTAȚIE: verificarea din `creeaza_factura` scoasă -> linia 0% fără categorie intră -> pică."""
    from core import facturi_api as fa
    with pytest.raises(ValueError) as e:
        fa.creeaza_factura(conn, "C1", "2026-10-16", "emisa", [_linie(None)], tert_nume="CLIENT SRL", tert_cui="18547290")
    assert e.value.cod == ct.COD_LIPSA
    with pytest.raises(ValueError) as e:
        fa.creeaza_factura(conn, "C2", "2026-10-16", "emisa", [_linie("taxare_inversa")], tert_nume="CLIENT SRL", tert_cui="18547290")
    assert e.value.cod == "CATEGORIE_331_DE_COMPLETAT"
    r = fa.creeaza_factura(conn, "C3", "2026-10-16", "emisa", [_linie("taxare_inversa"), _linie(None, 21)],
                           tert_nume="CLIENT SRL", tert_cui="18547290", categorie_331="deseuri")
    with conn.cursor() as cur:
        cur.execute("SELECT f.taxare_inversa, f.categorie_331, array_agg(l.categorie_tva ORDER BY l.id) FROM facturi f "
                    "JOIN factura_linii l ON l.factura_id = f.id WHERE f.id = %s GROUP BY f.id", (r["factura_id"],))
        assert cur.fetchone() == (True, "deseuri", ["taxare_inversa", None])
    s = fa.storneaza(conn, r["factura_id"])
    with conn.cursor() as cur:
        cur.execute("SELECT array_agg(categorie_tva ORDER BY id) FROM factura_linii WHERE factura_id = %s", (s["factura_id"],))
        assert cur.fetchone()[0] == ["taxare_inversa", None], "stornarea aterizează în aceeași categorie"


@pytest.mark.skipif(not _duk.poate_valida("d300"), reason="validatorul DUK lipsește")
def test_274b_d300_cu_randurile_13_14_15_e_valid_pe_duk(conn):
    """D300 generat din facturi emise cu categorii -> rd.13, rd.14, rd.15 și DUK „valid” (judecătorul final, CLAUDE.md)."""
    from core import facturi_api as fa
    for i, (cat, suma) in enumerate((("scutit_cu_drept", 1000), ("scutit_fara_drept", 300), ("taxare_inversa", 400))):
        # factura cu taxare inversă e MIXTĂ: și o linie de 21% (rd.9), pe care și calea 2 (d300_reconciliere) o vede colectată
        fa.creeaza_factura(conn, "D%d" % i, "2026-09-10", "emisa", [dict(_linie(cat), pret_unitar=suma)] + (
            [dict(_linie(None, 21), pret_unitar=100)] if cat == "taxare_inversa" else []), tert_nume="CLIENT SRL",
            tert_cui="18547290", categorie_331="deseuri" if cat == "taxare_inversa" else None, status="emisa")
    xml, res = _d300.genereaza(conn, _SCH, Perioada(2026, luna=9))
    assert (res.R.get("R13_1"), res.R.get("R14_1"), res.R.get("R15_1"), res.R.get("R9_1"), res.R.get("R9_2")) == \
        (400, 1000, 300, 100, 21), res.R
    v = _duk.valideaza(xml, "d300", an=2026, luna=9)
    assert v["stare"] == "valid", v
