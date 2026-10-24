# -*- coding: utf-8 -*-
"""GARDA C138 (lotul 12, scenariul pilot `frontend_test/e2e/e2e_pilot_luna.py::test_pilot_07`): propunerea NIR-ului „fără factură”
când transportul e facturat de ACELAȘI furnizor, pe factura mărfii.

DEFECTUL (văzut pe ecran în prima rulare a scenariului): NIR nr. 1 — 20 × 150,00 + transport 200,00 = cost 3.200,00, fără factură
(371 = 408). Factura furnizorului MF-901 are marfa ȘI transportul: net 3.200,00. La validare, aplicația scria „Niciun NIR nu are costul
facturii” și nu propunea nimic: compara netul facturii (3.200) numai cu costul fără accesorii al NIR-ului (3.000). Decizia Costin
08.10.2026 pct.2 (verbatim în `core/nir_legare.py`): „se propune legarea cu NIR-ul nelegat de la același furnizor (preselecție permisă —
dedusă din date, vizibilă, modificabilă)”.

CE FACE IMPOSIBIL: ca NIR-ul în forma nouă (datoria pe 408) al cărui cost COMPLET (marfa + transportul + taxele) e netul facturii să nu
fie propus; propunerea pe costul fără accesorii (transportul facturat de altcineva) rămâne; un cost diferit nu se propune.

Schemă efemeră din `tenant_template.sql`, ștearsă la ieșire; date în 2099. Nimic în tabele partajate.
"""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot12_pilot_nir"
CUI_A = "14399840"   # CUI real (cel din `core/test_nir_legare_inversa.py`), cifra de control verificată (CLAUDE.md)
_L = {"cantitate": 20, "pret_achizitie": 150, "cota_tva": 21, "denumire": "Marfa pilot", "pret_vanzare": 250}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, metoda_stoc) "
                        "VALUES (1, 'NIR PILOT SRL', 'RO14399840', true, 'global_valoric')")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _nir_cu_transport(conn):
    """NIR „fără factură” (forma nouă: 371 = 408, TVA pe 4428.01 = 408): 20 × 150,00 + transport 200,00 cu TVA 21% -> cost 3.200,00."""
    from core import stocuri_api as s
    r = s.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-09-02", "furnizor": "FURNIZOR", "cui": CUI_A, "linii": [dict(_L)],
                                 "factura_sosita": False, "transport": 200, "cota_tva_transport": 21})
    assert "eroare" not in r, r
    return r


def _factura(conn, numar, linii):
    from core import facturi_api as fa
    r = fa.creeaza_factura(conn, numar, "2099-09-03", "primita",
                           [{"descriere": d, "cantitate": c, "pret_unitar": p, "cota_tva": 21} for d, c, p in linii],
                           tert_nume="FURNIZOR", tert_cui="RO" + CUI_A)
    return r["factura_id"] if isinstance(r, dict) else r


def _refuzul(conn, fid):
    """Contarea fără alegere: refuzul structurat (`NIR_DE_LEGAT`) cu candidații și propunerea."""
    from core import contare_facturi as cf, nir_legare as nl
    with cf.cursor_dict(conn) as cur, pytest.raises(cf.RefuzContare) as e:
        cf.contabilizeaza(cur, SCH, fid, automat=False)
    assert e.value.cod == nl.COD_DE_ALES
    return e.value.detalii


def test_def_c_pilot_1_transportul_pe_factura_marfii_propune_nir_ul(conn):
    """C138. Factura mărfii cu transportul pe ea (net 3.000 + 200 = 3.200 = costul complet al NIR-ului) -> NIR-ul e PROPUS, iar
    eticheta spune și accesoriul; legat, factura închide 408 întreg (408 = 401 3.200 + 672) și trece TVA-ul în deductibil
    (4426 = 4428.01 672) — OMFP 1802/2014, funcțiunea contului 408; CF art.299 alin.(1) lit.a (deducerea cere factura).
    MUTAȚIE: în `nir_legare.candidati`, `acelasi = cost == net` (fără ramura accesoriului) -> `propus` None -> pică."""
    from core import contare_facturi as cf
    n = _nir_cu_transport(conn)
    fid = _factura(conn, "MF-901", [("Marfa pilot", 20, 150), ("Transport marfă", 1, 200)])
    d = _refuzul(conn, fid)
    assert d["propus"] == n["id"], d
    (c,) = d["candidati"]
    assert (c["cost"], c["acelasi_cost"], c["forma_noua"]) == ("3000.00", True, True), c
    assert c["eticheta"].endswith("· cost 3000.00 lei (+ transport și taxe 200.00 lei)"), c["eticheta"]
    with cf.cursor_dict(conn) as cur:
        r = cf.contabilizeaza(cur, SCH, fid, automat=False, nir_legat=d["propus"])
    # costul complet din NIR (3.000 + 200) + TVA-ul lui (630 + 42) = 3.872 pe 408 = 401; TVA-ul 672 trece 4428.01 -> 4426
    assert r["linii"] == [{"debit": "408", "credit": "401", "suma": "3872.00"},
                          {"debit": "4426", "credit": "4428.01", "suma": "672.00"}], r["linii"]


def test_def_c_pilot_1_transportul_facturat_de_altcineva_ramane_propus(conn):
    """C138, cealaltă jumătate: transportul facturat de un transportator (factura furnizorului are numai marfa, net 3.000 = costul
    fără accesorii) -> NIR-ul rămâne propus, ca înainte."""
    n = _nir_cu_transport(conn)
    d = _refuzul(conn, _factura(conn, "MF-902", [("Marfa pilot", 20, 150)]))
    assert d["propus"] == n["id"], d


def test_def_c_pilot_1_alt_cost_nu_se_propune(conn):
    """C138: un net care nu e nici costul fără accesorii (3.000), nici costul complet (3.200) -> nicio propunere (alegerea e a
    omului: „Niciun NIR nu are costul facturii”)."""
    _nir_cu_transport(conn)
    d = _refuzul(conn, _factura(conn, "MF-903", [("Marfa pilot", 20, 150), ("Transport marfă", 1, 100)]))
    assert d["propus"] is None and [c["acelasi_cost"] for c in d["candidati"]] == [False], d
