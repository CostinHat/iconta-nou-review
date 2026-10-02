# -*- coding: utf-8 -*-
"""GARD — factura emisă de o firmă NEplătitoare de TVA nu poartă taxa (lot 19 pct.4d, 02.10.2026).

Defectul: `/produse/potriveste` primea `platitor_tva` din corpul cererii, cu implicit True, iar ecranul de emitere nu-l
trimitea — deci unui neplătitor i se propunea 21% (sau 11%), cota pleca explicit la `/facturi/emite`, iar emiterea o
păstra (completarea după profil rula doar pe liniile FĂRĂ cotă). PDF-ul tipărea apoi „TVA 0%” chiar și la cota 0.

Temei (Codul fiscal, forma consolidată din corpus):
  · CF art.310 alin.(10) lit.b): persoana impozabilă care aplică regimul special de scutire „nu are voie să menționeze
    taxa pe factură sau pe alt document”;
  · CF art.319 alin.(20) lit.l): „în cazul în care este aplicabilă o scutire de taxă, trimiterea la dispozițiile
    aplicabile din prezentul titlu … sau orice altă mențiune din care să rezulte că livrarea de bunuri ori prestarea de
    servicii face obiectul unei scutiri”.
"""
import contextlib

import pytest

from core import db as _db, tenant_provisioning as _tp

_SCHEMA = "test_neplatitor_emitere"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


def _schema(cur, platitor):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,"
                "tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'MICA SRL','14399840',"
                "'Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001','micro',%s,'L','Pop','Ion','administrator')",
                (platitor,))


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_propunerea_de_cota_citeste_statutul_din_profil_nu_din_cerere(conn, monkeypatch):
    from core import uc_tenants, uc_comun
    with conn.cursor() as cur:
        _schema(cur, False)
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_FaraCommit(conn)))
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: _SCHEMA)
    r = uc_tenants.produse_potriveste(1, "Cafea boabe 1 kg", {"uid": 1})
    # CF art.310 alin.(10) lit.b): neplătitorul nu menționează taxa -> cota propusă e 0, nu 11/21
    assert r["ok"] and r["cota"] == 0 and r["categorie"] == "neplatitor_tva"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_emiterea_refuza_tva_la_neplatitor_si_accepta_cota_zero(conn):
    from core import facturi_api
    with conn.cursor() as cur:
        _schema(cur, False)
    linie = {"descriere": "Consultanta", "cantitate": 1, "pret_unitar": 1000, "um": "buc", "cont_venit": "704"}
    # CF art.310 alin.(10) lit.b): o linie cu 21% pe factura unui neplătitor se REFUZĂ, numită, cu temeiul
    with pytest.raises(ValueError) as e:
        facturi_api.creeaza_factura(conn, "MS1", "2026-07-10", "emisa", [dict(linie, cota_tva=21)], tert_nume="Client PF",
                                    tert_pf=True)
    assert (e.value.cod, e.value.temei, e.value.linie) == ("EMITENT_NEPLATITOR_TVA", "CF art.310 alin.(10) lit.b)", "Consultanta")
    r = facturi_api.creeaza_factura(conn, "MS2", "2026-07-10", "emisa", [dict(linie, cota_tva=0)], tert_nume="Client PF",
                                    tert_pf=True)
    assert r["ok"] and float(r["tva"]) == 0.0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_completarea_automata_da_zero_la_neplatitor_nu_cota_din_catalog(conn):
    from core import facturi_api
    with conn.cursor() as cur:
        _schema(cur, False)
        # un produs salvat cândva cu 21% în catalog nu are voie să readucă TVA-ul
        cur.execute("INSERT INTO produse (denumire, um, pret_unitar, cota_tva) VALUES ('Consultanta','buc',1000,21)")
    out = facturi_api._potriveste_linii(conn, [{"descriere": "Consultanta", "cantitate": 1, "pret_unitar": 1000,
                                                "cota_tva": None, "cont_venit": "704"}], platitor_tva=False)
    assert out[0]["cota_tva"] == 0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_emiterea_la_platitor_ramane_neschimbata(conn):
    from core import facturi_api
    with conn.cursor() as cur:
        _schema(cur, True)
    r = facturi_api.creeaza_factura(conn, "P1", "2026-07-10", "emisa",
                                    [{"descriere": "Consultanta", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21,
                                      "cont_venit": "704"}], tert_nume="Client PF", tert_pf=True)
    assert r["ok"] and float(r["tva"]) == 210.0


def _paragrafe(monkeypatch, profil, factura):
    """Textele paragrafelor din care se construiește PDF-ul — lista lor, nu un text extras din PDF (structură)."""
    from core import factura_pdf
    texte, Orig = [], factura_pdf.Paragraph

    def P(text, *a, **k):
        texte.append(text)
        return Orig(text, *a, **k)
    monkeypatch.setattr(factura_pdf, "Paragraph", P)
    factura_pdf.genereaza_pdf(profil, factura)
    return texte


def _factura(cota):
    return {"numar": "MS2", "directie": "emisa", "data_emitere": "2026-07-10", "moneda": "RON", "tert_nume": "Client PF",
            "total": 1000 if cota == 0 else 1210, "tva": 0 if cota == 0 else 210,
            "linii": [{"descriere": "Consultanta", "cantitate": 1, "um": "buc", "pret_unitar": 1000, "cota_tva": cota}]}


def test_pdf_neplatitor_fara_taxa_cu_trimiterea_la_art_310(monkeypatch):
    from core import factura_pdf
    texte = _paragrafe(monkeypatch, {"nume": "MICA SRL", "cui": "14399840", "platitor_tva": False}, _factura(0))
    # CF art.310 alin.(10) lit.b): nicio mențiune a taxei — fără rândul „TVA x%” și fără coloana „Cotă”
    assert [t for t in texte if t.startswith("TVA ")] == [] and texte.count("<b>Cot\u0103</b>") == 0
    # CF art.319 alin.(20) lit.l): trimiterea la dispoziția care scutește, ca paragraf al documentului
    assert texte.count(factura_pdf.MENTIUNE_NEPLATITOR) == 1


def test_pdf_platitor_pastreaza_defalcarea_pe_cote(monkeypatch):
    from core import factura_pdf
    texte = _paragrafe(monkeypatch, {"nume": "X SRL", "cui": "14399840", "platitor_tva": True}, _factura(21))
    assert texte.count("TVA 21%") == 1 and texte.count(factura_pdf.MENTIUNE_NEPLATITOR) == 0
