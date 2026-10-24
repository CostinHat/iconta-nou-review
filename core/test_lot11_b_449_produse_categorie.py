# -*- coding: utf-8 -*-
"""[lotul 11, subagentul b, deficiența 449 — comanda Costin 11.1 pct.10, verbatim] „la cota TVA a produsului lipsesc taxarea inversă
(art. 331), scutit cu drept de deducere (art. 294) și neimpozabil. Verifică la sursă dacă taxarea inversă pentru cereale e în vigoare în
2026.”

Cauza: nomenclatorul Produse ținea numai cota (21 / 11 / „scutit / fără TVA (art. 292)”), fără categoria cotei 0%; factura emisă o cere pe
linie (274b), deci un produs cu taxare inversă sau scutit cu drept de deducere nu-și putea spune natura. Acum: `produse.categorie_tva`
(subsetul de produs din `categorii_tva`) și `produse.categorie_331` (bunul cu taxare inversă, codul din D394 — la cereale, subcodul NC),
propuse pe factură de `propunere_pentru_linie`.

TEMEI (verbatim, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, forma consolidată a Portalului Legislativ, istoricul până la 08.08.2026):
- CF art.331 alin.(2) lit.c): „livrarea de cereale și plante tehnice, inclusiv semințe oleaginoase și sfeclă de zahăr, care nu sunt în
  principiu destinate ca atare consumatorilor finali. Prin normele metodologice se stabilesc codurile NC corespunzătoare acestor bunuri”;
- CF art.331 alin.(6): „Prevederile alin. (2) lit. c)-f) și i)-l) se aplică până la data de 31 decembrie 2026 inclusiv.” (modificat de
  OUG 85/2022 art.IV pct.1, MO 594/17.06.2022) -> taxarea inversă pentru cereale E în vigoare în 2026;
- HG 1/2016 pct.109 alin.(7) (`anaf_surse/hg_1_2016_norme_cod_fiscal.txt`): codurile NC (1001 Grâu și meslin ... 121291 Sfeclă de zahăr);
- categoriile și codurile UBL / rândurile D300: `core/categorii_tva.py` (Ghidul MF e-Factura v2.9 cap.3; OPANAF 174/2026 rd.13 / 14 / 15).
"""
import io
import os
import xml.etree.ElementTree as ET

import psycopg2
import pytest

from core import categorii_tva as ct, d394, produse_api as pa
from core import db as _db, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCH = "efemer_lot11_b_449"
NS = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
      "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}


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
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCH)   # pe tranzacție: nu rămâne pe conexiunea din pool (core/test_lot10_search_path_pool.py)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,serie_factura) VALUES (1,'CAT SRL',"
                            "'14399840','Str 1','Cluj-Napoca','CJ','4621','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar','Popescu',"
                            "'Ion','ADMINISTRATOR','SRL',200,'CAT')")
            # [lotul 12, 472] corectura cotei se consemnează cu utilizatorul cererii (`produse_api._corectura`): testul o face ca un om
            from core import autor_cerere
            tok = autor_cerere.seteaza(990449)
            try:
                yield c
            finally:
                autor_cerere.reseteaza(tok)
        finally:
            c.rollback()


# ── nomenclatorul ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_449_categoriile_produsului_sunt_cele_din_categorii_tva_iar_cerealele_au_codul_nc():
    """Sursa unică: etichetele vin din `categorii_tva`, codurile bunurilor din `d394.CODPR`, cerealele pe subcodurile NC din HG 1/2016
    pct.109 alin.(7) — aceleași ca `d394.CODPR_CEREALE`; migrarea și șablonul admit exact aceste valori."""
    from core import migrare_produse_categorie_tva as m
    assert set(pa.CATEGORII_PRODUS) <= set(ct.CATEGORII) and m.CATEGORII == pa.CATEGORII_PRODUS
    assert set(pa.NC_CEREALE) == set(d394.CODPR_CEREALE)   # HG 1/2016 pct.109 alin.(7)
    assert set(m.CODURI_331) == set(pa.coduri_331()) == (set(d394.CODPR) - {"cereale"}) | set(d394.CODPR_CEREALE)
    sablon = io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    assert sablon.count("categorie_331 IN (%s)" % ", ".join("'%s'" % v for v in m.CODURI_331)) == 1
    assert [c["eticheta"] for c in pa.categorii_pentru_ecran()] == [ct.CATEGORII[c]["eticheta"] for c in pa.CATEGORII_PRODUS]


@pytest.mark.parametrize("cota, cat, c331, bun", [
    (0, "taxare_inversa", "1001", True), (0, "taxare_inversa", None, False), (0, "taxare_inversa", "cereale", False),
    (0, "scutit_cu_drept", None, True), (0, "in_afara_sferei", None, True), (0, "scutit_fara_drept", None, True),
    (21, "scutit_cu_drept", None, False), (0, "livrare_ic", None, False), (0, "scutit_cu_drept", "deseuri", False), (0, None, None, True)])
def test_449_verificarea_categoriei(cota, cat, c331, bun):
    """Categoria numai la cota 0%; taxarea inversă cere bunul (CF art.331 alin.(2)), la cereale codul NC (HG 1/2016 pct.109 alin.(7));
    livrarea IC / exportul țin de client, nu de produs. MUTAȚIE: verificarea cotei 0% scoasă -> „21% scutit cu drept” trece -> pică."""
    assert (pa.verifica_categoria(cota, cat, c331) is None) is bun, pa.verifica_categoria(cota, cat, c331)


def test_449_produsul_isi_pastreaza_categoria_si_o_propune_pe_factura(conn):
    """„Grâu” 0% cu taxare inversă, NC 1001 -> nomenclatorul îl ține, propunerea liniei de factură îl dă (cota, categoria, bunul); la
    neplătitor nu se propune categoria (vine din regim, O). Refuzul: cota 21 cu categorie -> nimic scris. Baza o refuză și ea (CHECK)."""
    r = pa.creeaza(conn, "Grâu", um="kg", cota_tva=0, categorie_tva="taxare_inversa", categorie_331="1001", confirmat=True)
    assert r["ok"] and (r["categorie_tva"], r["categorie_331"]) == ("taxare_inversa", "1001"), r
    p = pa.propunere_pentru_linie(conn, "grau")
    assert (p["cota"], p["categorie_tva"], p["categorie_331"], p["sursa"]) == (0, "taxare_inversa", "1001", "nomenclator"), p
    assert pa.propunere_pentru_linie(conn, "grau", platitor_tva=False)["categorie_tva"] is None
    assert pa.creeaza(conn, "Servicii", cota_tva=21, categorie_tva="scutit_cu_drept")["cod"] == "CATEGORIE_TVA"
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT s")
        with pytest.raises(psycopg2.errors.CheckViolation):
            cur.execute("INSERT INTO produse (denumire, cota_tva, categorie_tva) VALUES ('X', 21, 'taxare_inversa')")
        cur.execute("ROLLBACK TO SAVEPOINT s")
    # cota schimbată pe 21 golește categoria cotei 0%
    assert pa.actualizeaza(conn, r["id"], cota_tva=21)["ok"]
    assert pa.cauta_dupa_denumire(conn, "Grâu")["categorie_tva"] is None
    assert pa.actualizeaza(conn, r["id"], categorie_tva="scutit_cu_drept")["cod"] == "CATEGORIE_TVA"


def test_449_categoria_din_nomenclator_ajunge_in_xml_si_in_d300(conn):
    """Capăt la capăt pe server: produsele cu taxare inversă (deșeuri), scutit cu drept și neimpozabil -> factura emisă cu categoria
    propusă de nomenclator -> XML e-Factura AE / E / E (Ghidul MF v2.9 cap.3) -> D300 rd.13 / rd.14, neimpozabilul fără rând (OPANAF
    174/2026) -> D300 valid pe DUK."""
    from core import facturi_api as fa, efactura_send as ef, d300 as _d300, duk as _duk
    from core.common import Perioada
    for den, cat, c331 in (("Deșeuri fier", "taxare_inversa", "deseuri"), ("Transport export", "scutit_cu_drept", None),
                           ("Penalitate", "in_afara_sferei", None)):
        assert pa.creeaza(conn, den, cota_tva=0, categorie_tva=cat, categorie_331=c331, confirmat=True)["ok"]
    linii, c331 = [], None
    for den, suma in (("Deșeuri fier", 400), ("Transport export", 1000), ("Penalitate", 50)):
        p = pa.propunere_pentru_linie(conn, den)   # ce pune ecranul de emitere pe linie, din nomenclator
        linii.append({"descriere": den, "um": "buc", "cantitate": 1, "pret_unitar": suma, "cota_tva": p["cota"],
                      "categorie_tva": p["categorie_tva"]})
        c331 = c331 or p["categorie_331"]
    linii.append({"descriere": "Marfă", "um": "buc", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "categorie_tva": None})
    r = fa.creeaza_factura(conn, "P1", "2026-09-10", "emisa", linii, tert_nume="CLIENT SRL", tert_cui="18547290", categorie_331=c331,
                           status="emisa")
    f = fa.detalii_factura(conn, r["factura_id"])
    x = ET.fromstring(ef.genereaza_xml({"numar": "P1", "serie": "CAT", "data_emitere": "2026-09-10", "moneda": "RON"}, f["linii"],
                                       {"nume": "CAT SRL", "cui": "14399840", "reg_com": "J12/1/2020", "adresa": "Str 1", "oras": "Cluj-Napoca",
                                        "judet": "CJ", "iban": "RO49AAAA1B31007593840000", "platitor_tva": True},
                                       {"nume": "CLIENT SRL", "cui": "18547290", "adresa": "Str 2", "oras": "Cluj-Napoca", "judet": "CJ",
                                        "tara": "RO"}))
    assert [c.text for c in x.findall("cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory/cbc:ID", NS)] == ["AE", "E", "E", "S"]
    xml, res = _d300.genereaza(conn, _SCH, Perioada(2026, luna=9))
    # OPANAF 174/2026: rd.13 = livrări cu măsurile de simplificare art.331; rd.14 = scutite cu drept de deducere; neimpozabilul: fără rând
    assert (res.R.get("R13_1"), res.R.get("R14_1"), res.R.get("R9_1"), res.R.get("R9_2")) == (400, 1000, 100, 21), res.R
    if _duk.poate_valida("d300"):
        v = _duk.valideaza(xml, "d300", an=2026, luna=9)
        assert v["stare"] == "valid", v
