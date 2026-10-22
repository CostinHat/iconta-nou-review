# -*- coding: utf-8 -*-
"""[lotul 11, comanda Costin 11.1 pct.23, verbatim] „«sursa: facturile» pe nota borderoului” — și, pe același ecran, ciorna depășită (451)
arătată pe rândul ei din Registrul jurnal.

Cauza: `jurnal_api.eticheta_sursa` primea numai `inregistrari.sursa`; sursa `facturi` o scriu și notele borderoului (`facturi.tip =
'borderou'`: „Achiziție de la neînregistrat”, stornarea borderoului). Eticheta se ia acum și după documentul legat. Registrul jurnal
(`uc_tenants.tenant_jurnal`) îi dă tipul documentului; garda pică dacă rândul ar pierde din nou tipul.

Schemă efemeră din template, în tranzacție anulată; `db.get_conn` și accesul la firmă sunt legate de conexiunea testului (tiparul
`test_lot10b_434_borderou_numerotare`). Date în 2099."""
import contextlib
import io
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot11_s_sursa"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


class _P:
    def __init__(s, c): s._c = c
    def commit(s): pass
    def rollback(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@pytest.fixture
def conn(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'SURSA SRL', '14399840', 'cantitativ_valoric') "
                            "ON CONFLICT (id) DO UPDATE SET metoda_stoc = 'cantitativ_valoric'")
            from core import auth_api, coada_api, uc_tenants
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_P(c)))
            monkeypatch.setattr(auth_api, "schema_tenant_citire", lambda *a, **k: SCH)
            monkeypatch.setattr(coada_api, "stari_note", lambda *a, **k: {})
            yield c
        finally:
            c.rollback()


def test_eticheta_sursei_dupa_documentul_legat():
    from core import jurnal_api as j
    assert j.eticheta_sursa("facturi", "borderou") == "borderoul de achiziție"   # OMFP 2634/2015, cod 14-4-13: borderoul nu e factură
    assert j.eticheta_sursa("facturi", "factura") == j.eticheta_sursa("facturi") == "facturile"
    assert j.eticheta_sursa("stocuri", "borderou") == "gestiunea stocurilor"   # tipul schimbă eticheta numai unde schimbă felul sursei
    assert all(s in j.ETICHETE_SURSA for s, _t in j.ETICHETE_SURSA_DUPA_DOCUMENT)


def test_def_23_registrul_jurnal_arata_sursa_borderoului_si_ciorna_depasita(conn, monkeypatch):
    """Nota borderoului: „sursa: borderoul de achiziție”. Ciorna ieșirii de pe Z scrisă cu regula veche (bonul de consum): rândul poartă
    `depasita` (mesajul și refacerea), aceeași verificare ca la validare. MUTAȚIE: `f_tip` scos din apelul din `tenant_jurnal` -> pică."""
    from core import facturi_api as fa, repo_contabilitate as rc, stocuri_cv_api as cva, uc_tenants
    fid = fa.creeaza_factura(conn, numar="BA-1", data_emitere="2099-10-19", directie="primita",
                             linii=[{"descriere": "grau - Ion", "cantitate": 1, "pret_unitar": "100", "cota_tva": 0}],
                             tert_nume="Ion", tert_cui="", status="importata", tert_platitor_tva=False, tert_pf=True, tip="borderou")["factura_id"]
    with conn.cursor() as cur:
        nb = rc.nota_facturi_cu_factura(cur, SCH, "2099-10-19", fid, "Achizitie de la neinregistrat - Ion")[0]
        rc.adauga_linie_furnizor(cur, SCH, nb, "371", 100)
        zid = rc.nota_horeca_z_ciorna(cur, SCH, "2099-10-20", "Z-8000000001-0042", "Raport Z", "Raport Z nr 0042 din 20.10.2099 (casa 8000000001)")[0]
        rc.adauga_linie_3(cur, SCH, zid, "5311", "707", 121)
        rc.adauga_z_amef(cur, SCH, zid, "8000000001", 3)
    a = cva.intrare(conn, SCH, {"denumire": "Marfa A", "um": "buc", "data": "2099-10-01", "cantitate": 10, "pret_unitar": "5",
                                "document": "NIR nr 1 din 01.10.2099"})
    monkeypatch.setattr(cva, "document_iesire", lambda cur, schema, d, z: str(d or "").strip() or None)   # regula de dinainte de 438
    ies = cva.iesire(conn, SCH, {"articol_id": a["articol_id"], "data": "2099-10-20", "cantitate": 1, "z_id": zid})
    monkeypatch.undo()
    from core import auth_api, coada_api
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_P(conn)))
    monkeypatch.setattr(auth_api, "schema_tenant_citire", lambda *a, **k: SCH)
    monkeypatch.setattr(coada_api, "stari_note", lambda *a, **k: {})
    r = uc_tenants.tenant_jurnal(1, 2099, 10, {"uid": 0, "rol": "patron", "firm": 0})
    note = {n["id"]: n for n in r["note"]}
    assert note[nb]["sursa_eticheta"] == "borderoul de achiziție", note[nb]
    dep = note[ies["inregistrare_id"]].get("depasita")
    assert dep and dep["refacere"]["eticheta"] == "Refă nota din mișcarea de stoc", dep
    import datetime as _dt
    azi = _dt.date.today()
    assert dep["mesaj"] == (   # mesajul întreg (core/test_garzi_pe_text.py); „generată pe” = ziua în care testul a scris nota
        "Nota din 20.10.2099 a fost generată pe %02d.%02d.%d după o regulă care s-a schimbat de atunci: acum raportul Z ar scrie documentul "
        "justificativ «Raport Z nr 0042 din 20.10.2099 (casa 8000000001)» (pe ciornă: «Bon de consum nr 1 din 20.10.2099»). Nota e "
        "depășită și nu se validează — refă-o din raportul Z („Refă nota din mișcarea de stoc”), apoi valideaz-o."
        % (azi.day, azi.month, azi.year)), dep["mesaj"]
    assert "depasita" not in note[zid] and "depasita" not in note[nb]
