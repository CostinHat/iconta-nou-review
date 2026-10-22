# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 401 — comanda Costin 10.2 pct.7a, verbatim] „sub nota borderoului, textul zice «factura de achiziție BA-1» și
trimite la Facturi.”

Cauza: textul de sub nota derivată se compunea din „factura ” + eticheta documentului tăiată la primul cuvânt („Borderou de achiziție
BA-1 din …” -> „de achiziție BA-1 din …”), iar locul corecturii era al facturii („în Facturi: corectezi factura (stornare …)”). Aceeași
compunere la „stinge …” al chitanței (`jurnal_api.facturi_stinse`). Temei: OMFP 2634/2015 anexa 2, „Borderou de achiziție (cod
14-4-13)” — documentul justificativ al cumpărării de la persoana fizică, distinct de factură. Schemă efemeră, tranzacție anulată."""
import contextlib
import io

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_401_nota_borderou"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _P:
    def __init__(s, c): s._c = c
    def commit(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@pytest.fixture
def conn(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                            "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
            from core import auth_api, uc_comun, uc_tenants
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_P(c)))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
            yield c
        finally:
            c.rollback()


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _locurile_refuzului(txt):
    """(documentul din care e derivată nota, locul corecturii) — cele două locuri ale refuzului `note_derivate.mesaj_refuz`:
    „Nota <n> e derivată din <document>: se corectează numai de acolo — <locul>. Dacă …”. Locul gol = refuzul n-are forma asta."""
    nota_doc, _sep, rest = txt.partition(": se corectează numai de acolo — ")
    return nota_doc.partition(" e derivată din ")[2], rest.partition(". Dacă")[0]


def test_def_401_sub_nota_borderoului_scrie_borderoul_si_nu_trimite_la_facturi(conn):
    from core import note_derivate as nd, uc_tenants
    r = uc_tenants.achizitie_neinregistrat(1, {"data": "2026-10-19", "furnizor_nume": "Ion Popescu", "furnizor_adresa": "Str. Florilor 1",
                                               "furnizor_act": "PH 123456", "valoare": 200, "cont_cheltuiala": "371", "articol": "grâu", "articol_nou": True,
                                               "cantitate": 100, "um": "kg"}, {"uid": 1})
    with conn.cursor() as cur:
        doc = nd.documentul_sursa(cur, SCH, r["inregistrare_id"])
        assert doc[0] == "borderou" and doc[1] == "BA-1 din 19.10.2026", doc
        txt = nd.mesaj_refuz(r["inregistrare_id"], doc)
        sursa, unde = _locurile_refuzului(txt)
        # comanda 10.2 pct.7a: nu „factura de achiziție BA-1”, nu trimiterea la Facturi; borderoul (OMFP 2634/2015, cod 14-4-13)
        assert sursa == "borderoul de achiziție BA-1 din 19.10.2026", txt
        assert unde.startswith("în Stocuri › „Borderou de achiziție”") and "în Facturi:" not in txt, txt   # [lotul 11, patch B P9]
        # nota borderoului (ciornă) nu se șterge din jurnal: borderoul rămâne (statusul „importată”, ca factura primită)
        assert nd.se_sterge(cur, SCH, doc, r["inregistrare_id"]) is False


def test_def_401_stinge_numeste_borderoul_nu_factura():
    """Chitanța / plata care stinge un borderou: „stinge borderoul de achiziție BA-1 din …”, nu „factura de achiziție BA-1 …”."""
    from core import jurnal_api as j
    assert j.eticheta_factura_in_text("borderou", None, "BA-1", "2026-10-19") == "borderoul de achiziție BA-1 din 19.10.2026"
    assert j.eticheta_factura_in_text("factura", "FCT", "FCT12", "2026-10-05") == "factura FCT nr. 12 din 05.10.2026"   # [443] separat
    assert j.eticheta_factura_in_text(None, None, "7", "2026-10-05") == "factura 7 din 05.10.2026"
