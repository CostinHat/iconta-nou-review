# -*- coding: utf-8 -*-
"""GARD — factura emisă pe baza bonului fiscal, în toate ieșirile către terți (punctul 3, decizia Costin 03.10.2026).

Decizia: „nu A (factura ar dispărea din evidența externă). Se exportă cu marca «din bon», dacă formatul de import al
programului are câmp pentru asta; dacă nu, într-un fișier separat … Nicio factură pierdută, nicio vânzare dublată.”
Ambele formate AU câmp (verificat la sursă), iar generalizarea clasei („factura din bon tratată ca factură obișnuită”)
a mai găsit trei ieșiri: D406, e-Factura și starea de încasare (notificarea de scadență pleacă la client).

Surse:
  * SAGA — manual.sagasoft.ro topic-76 „Import date”: `<FacturaTip>` „(Opţional. Tipul de document din Saga …)”;
    topic-32 „Iesiri - lei”: „f - factură cu bon fiscal”.
  * WinMentor — „Facturi clienti.pdf” Rev.1.2 (11.09.2024): `ClasificareSAFT` „Factura storno: 381 … Cu factura la bon:
    751”; `CasaDeMarcat=D` „în cazul facturilor de tip «InfoCM»”; `NumarBonuri`.
  * D406 — d406_schema_anaf.xlsx, nota din nomenclatorul Livrări (v4.1.9): „pentru vanzarile efectuate … pe baza de bon
    fiscal, se emit facturi la cererea clientului, la raportarea acestor facturi este relevant codul: 310327”.
  * e-Factura — Ministerul Finanțelor, Ghidul codurilor tipurilor de facturi RO e-Factura v2.9, pct.2.5: codul 751
    pentru „Evidența livrărilor bazate pe bonuri fiscale”, cu mențiunea „Factura încasată cu bon fiscal ….”.
  * Încasarea — HG 1/2016 pct.97 alin.(1): „facturile emise și achitate pe bază de bonuri fiscale”.
"""
import xml.etree.ElementTree as ET

import pytest

from core import db as _db
from core import efactura_send as _ef
from core import export_saga as _xs
from core import export_winmentor as _wm
from core import tenant_provisioning as _tp

FIRMA = {"nume": "BON SRL", "cui": "14399840", "reg_com": "J40/1/2020", "adresa": "Str. 1", "iban": "", "banca": "",
         "tva_la_incasare": False}
LINIE = {"descriere": "Meniu zilei", "um": "buc", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}


def _fact(**k):
    f = {"id": 1, "numar": "F-1", "serie": "F", "data_emitere": "2026-10-02", "data_scadenta": "2026-10-17",
         "taxare_inversa": False, "moneda": "RON", "tert_nume": "CLIENT SRL", "tert_cui": "RO14399840",
         "tert_adresa": "Str. 2", "tert_oras": "Sector 1", "bon_fiscal_nr": None, "bon_fiscal_data": None,
         "storno_din_id": None}
    f.update(k)
    return f


DIN_BON = {"bon_fiscal_nr": "0042", "bon_fiscal_data": "2026-10-02"}


# ── SAGA ────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("marca,asteptat", [(DIN_BON, "f"), ({}, None), ({"storno_din_id": 7}, None)])
def test_saga_facturatip_doar_pe_factura_din_bon(marca, asteptat):
    # topic-32: „f - factură cu bon fiscal”; fără tag = factură (implicit SAGA). MUTAȚIE: `_din_bon` mereu False -> pică
    rad = ET.fromstring(_xs.xml_factura(FIRMA, _fact(**marca), [dict(LINIE)]).split("?>", 1)[1])
    tip = rad.find("Factura/Antet/FacturaTip")
    assert (tip.text if tip is not None else None) == asteptat


# ── WinMentor ───────────────────────────────────────────────────────────────────────────────────────────────
def _sectiuni(txt):
    out, cur = {}, None
    for l in txt.splitlines():
        if l.startswith("["):
            cur = out.setdefault(l.strip("[]"), {})
        elif "=" in l and cur is not None:
            k, v = l.split("=", 1)
            cur[k] = v
    return out


@pytest.mark.parametrize("marca,cls,infocm", [(DIN_BON, "751", ("D", "1")), ({}, "380", (None, None)),
                                              ({"storno_din_id": 7}, "381", (None, None)),
                                              (dict(DIN_BON, storno_din_id=7), "751", ("D", "1"))])
def test_winmentor_clasificare(marca, cls, infocm):
    # „Facturi clienti.pdf” Rev.1.2: 380 inițială / 381 storno / 751 cu factura la bon (stornarea unei facturi din bon
    # moștenește marca — decizia A 02.10). MUTAȚIE: ClasificareSAFT=380 fix -> pică (era codul de până azi)
    s = _sectiuni(_wm.facturi_txt(FIRMA, [(_fact(**marca), [dict(LINIE)])], 2026, 10))["Factura_1"]
    assert s["ClasificareSAFT"] == cls
    assert (s.get("CasaDeMarcat"), s.get("NumarBonuri")) == infocm


# ── e-Factura ───────────────────────────────────────────────────────────────────────────────────────────────
_NS = {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
_FURN = {"nume": "BON SRL", "cui": "14399840", "platitor_tva": True, "adresa": "Str. 1 Sector 1", "oras": "Sector 1",
         "judet": "B"}
_CLI = {"nume": "CLIENT SRL", "cui": "RO14399840", "adresa": "Str. 2", "oras": "Sector 1", "judet": "B"}


@pytest.mark.parametrize("marca,cod,nota", [
    (DIN_BON, "751", "Factura încasată cu bon fiscal — conform bon fiscal nr. 0042/02.10.2026"),
    ({}, "380", None)])
def test_efactura_751_si_mentiunea_pe_factura_din_bon(marca, cod, nota):
    # Ghidul MF v2.9 pct.2.5. MUTAȚIE: 380 fix (codul de până azi) -> pică
    f = dict(_fact(**marca), directie="emisa")
    rad = ET.fromstring(_ef.genereaza_xml(f, [dict(LINIE)], _FURN, _CLI).split("?>", 1)[1])
    assert rad.find("cbc:InvoiceTypeCode", _NS).text == cod
    n = rad.find("cbc:Note", _NS)
    assert (n.text if n is not None else None) == nota


# ── D406 + încasarea + „nicio factură pierdută”, pe schemă efemeră (ROLLBACK) ───────────────────────────────
_SCHEMA = "ztest_export_din_bon"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def lume():
    from core import facturi_api
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, declarant_nume, "
                    "declarant_prenume, declarant_functie, platitor_tva, tip_decont, regim_fiscal, forma_juridica, "
                    "capital_subscris) VALUES (1, 'BON SRL', '14399840', 'Str. Testul 1', 'Sector 1', 'B', '5610', 'BCR', "
                    "'RO49BCRA0000000000000000', 'POPESCU', 'GHEORGHE', 'ADMINISTRATOR', true, 'L', 'real', 'SRL', 200)")
            ids = {}
            for et, marca in (("obisnuita", {}), ("din_bon", DIN_BON)):
                r = facturi_api.creeaza_factura(conn, "PROBA-%s" % et.upper(), "2026-10-02", "emisa",
                                                [dict(LINIE, cont_venit="707")], tert_nume="CLIENT SRL",
                                                tert_cui="RO14399840", data_scadenta="2026-10-17", status="emisa", **marca)
                ids[et] = r["factura_id"]
            yield conn, ids
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d406_taxcode_310327_pe_factura_din_bon(lume):
    from core import d406
    conn, ids = lume
    # nota nomenclatorului Livrări. MUTAȚIE: ramura `din_bon` scoasă din pull -> 310344 -> pică
    xml, res = d406.genereaza(conn, _SCHEMA, 2026, 10)
    coduri = {f.nr: {l.tva_cod for l in f.linii} for f in res.facturi_vanzare}
    assert coduri == {"PROBA-OBISNUITA": {"310344"}, "PROBA-DIN_BON": {"310327"}}
    # codul referit pe linie e regăsit în TaxTable — singurul adăugat peste tabela standard
    assert {c.cod for c in res.cote_tva} - {c.cod for c in d406.COTE_TVA_STANDARD} == {"310327"}
    try:
        from core import duk
        ok = duk.poate_valida("d406")
    except Exception:
        ok = False
    if ok:
        v = duk.valideaza(xml, "d406", an=2026, luna=10, timeout=300)
        assert v.get("stare") == "valid", v.get("erori")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_din_bon_se_naste_incasata_si_nu_primeste_notificare(lume):
    from core import repo_notificari_scadenta as _rns
    conn, ids = lume
    # HG 1/2016 pct.97 alin.(1) „emise și achitate pe bază de bonuri fiscale”. MUTAȚIE: platita_la None -> pică
    with conn.cursor() as cur:
        cur.execute("SELECT id, platita_la::date FROM facturi WHERE id = ANY(%s) ORDER BY id", (list(ids.values()),))
        platite = dict(cur.fetchall())
        de_notificat = {r[0] for r in _rns.select_facturi(cur, "2026-12-31")}
    assert (platite[ids["obisnuita"]], str(platite[ids["din_bon"]])) == (None, "2026-10-02")
    assert ids["din_bon"] not in de_notificat and ids["obisnuita"] in de_notificat


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nicio_factura_pierduta_in_exporturi(lume):
    # decizia Costin: „Nicio factură pierdută” — factura din bon e în ambele exporturi, marcată, nu omisă
    conn, ids = lume
    luna = _xs.facturi_emise_luna(conn, _SCHEMA, 2026, 10)
    assert sorted(luna) == sorted(ids.values())
    sect = _sectiuni(_wm.export_luna(conn, _SCHEMA, 2026, 10)["Facturi.txt"].decode("cp1250"))
    facturi = {s["NrDoc"]: s["ClasificareSAFT"] for k, s in sect.items() if k.startswith("Factura_")}
    assert facturi == {"PROBA-OBISNUITA": "380", "PROBA-DIN_BON": "751"}
    assert sect["InfoPachet"]["TotalFacturi"] == "2"
