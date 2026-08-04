# -*- coding: utf-8 -*-
"""NECONFORMITATE ACTIVA reparata (04.08): operatiunile de achizitie (achizitie_ic, achizitie_taxare_inversa)
emit un rand `facturi` (directie=primita) + contabilizeaza cu factura_id legat, ca sa ajunga in D390/D394.
Probe end-to-end pe schema scratch din template (gated DB): handler real -> facturi + factura_id -> declaratie
-> operatiunea E ACOLO -> DUK valid. + GARD anti-regresie de CLASA: nicio inregistrare de achizitie fara factura_id."""
import pytest


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
_SCH = "efemer_achizitii_factura"


def _scratch(cur):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
    sql = open("tenant_template.sql", encoding="utf-8").read().replace("TENANT_PLACEHOLDER", _SCH)
    cur.execute(sql)   # template isi creeaza schema + tabelele, calificate cu _SCH
    cur.execute("SET search_path TO %s" % _SCH)
    cur.execute("""INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, email, telefon, caen,
                   declarant_nume, declarant_prenume, declarant_functie, platitor_tva, operatiuni_ic)
                   VALUES (1,'TEST SRL','RO14399840','Str 1','Buc','B','e@x.ro','0722','4690',
                           'P','I','ADMIN', true, true)""")


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_achizitie_ic_emite_factura_ajunge_in_d390_duk_valid(monkeypatch):
    import main
    from core import db, d390, duk
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _scratch(cur)
            conn.commit()
        monkeypatch.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: _SCH)
        # handler REAL
        r = main.achizitie_ic(1, {"data": "2026-06-20", "valoare": 1000, "cont_destinatie": "371",
                                   "tip": "bunuri", "cota": 21, "cod_tva_furnizor": "DE811569869",
                                   "numar": "F-DE-77", "furnizor_nume": "LIEFERANT GMBH"},
                              {"uid": 1})
        assert r.get("factura_id"), r
        # rand facturi (primita, furnizor UE) + inregistrare LEGATA (factura_id)
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SET search_path TO %s" % _SCH)
            cur.execute("SELECT directie, tert_cui, total, tva FROM facturi WHERE id=%s", (r["factura_id"],))
            f = cur.fetchone()
            assert f == ("primita", "DE811569869", 1000, 0), f
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (r["inregistrare_id"],))
            assert cur.fetchone()[0] == r["factura_id"], "inregistrare ORFANA (fara factura_id)"
        # D390: operatiunea E ACOLO + DUK valid
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO %s" % _SCH)
            prof, facturi = d390.pull(conn, _SCH, 2026, 6)
        assert any((x.get("cui") or "").startswith("DE") for x in facturi), \
            "achizitia IC NU e in facturi citite de D390: %r" % facturi
        res = d390.calcul_d390(prof, 2026, 6, facturi)
        assert res.total_baza >= 1000, res.total_baza
        if duk.poate_valida("d390"):
            xml = d390.build_xml(res)
            verdict = duk.valideaza(xml, "d390", an=2026, luna=6)
            assert verdict["stare"] == "valid", "DUK a respins D390: %s" % verdict.get("erori")
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            conn.commit()


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_achizitie_taxare_inversa_emite_factura_ajunge_in_d394_duk_valid(monkeypatch):
    import main
    from core import db, d394, duk
    from core.common import Perioada
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _scratch(cur)
            conn.commit()
        monkeypatch.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: _SCH)
        r = main.achizitie_taxare_inversa(1, {"data": "2026-06-15", "categorie": "deseuri", "valoare": 5000,
                                              "cont_destinatie": "371", "cota": 21, "furnizor_platitor_tva": True,
                                              "furnizor_cui": "RO14399840", "furnizor_nume": "FURNIZOR RO",
                                              "numar": "F-RO-1"}, {"uid": 1})
        assert r.get("factura_id"), r
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SET search_path TO %s" % _SCH)
            cur.execute("SELECT directie, tert_cui, taxare_inversa, categorie_331 FROM facturi WHERE id=%s",
                        (r["factura_id"],))
            assert cur.fetchone() == ("primita", "RO14399840", True, "deseuri")
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (r["inregistrare_id"],))
            assert cur.fetchone()[0] == r["factura_id"], "inregistrare ORFANA (fara factura_id)"
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO %s" % _SCH)
            xml, res = d394.genereaza(conn, _SCH, Perioada(2026, luna=6))
        assert 'codPR="22"' in xml, "taxare inversa (deseuri->codPR 22) NU e in D394: op11 lipsa"
        if duk.poate_valida("d394"):
            verdict = duk.valideaza(xml, "d394", an=2026, luna=6)
            assert verdict["stare"] == "valid", "DUK a respins D394: %s" % verdict.get("erori")
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            conn.commit()
