# -*- coding: utf-8 -*-
"""278 — Casă: dispoziția legată de factură, avansul de la client, plafonul Legii 70/2015 (comanda Costin 16.10.2026, „Lotul 6, comanda 1”
pct.3, verbatim în DECIZII).

Cazul din comandă: încasare de 6.000 lei „Încasare factura F1A4”, factura are 242,00. Înainte: nota 5311 = 4111 fără factură (factura
rămânea neîncasată), cei 5.758 lei nesemnalați, plafonul numai după salvare.

Temei (verificat la sursă, anaf_surse/):
- CF art.282 alin.(2) lit.b: „la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine
  faptul generator” — exigibilitatea TVA a avansului.
- CF art.319 alin.(16): „trebuie să emită o factură pentru suma avansurilor încasate [...] cel târziu până în cea de-a 15-a zi a lunii
  următoare celei în care a încasat avansurile”.
- OMFP 1802/2014, funcțiunea contului 419: „În creditul contului 419 [...] se înregistrează: sumele facturate clienților reprezentând
  avansuri pentru livrări de bunuri sau prestări de servicii (411)”.
- Legea 70/2015 art.3 alin.(1) lit.a (5.000 lei / zi de la o persoană juridică), art.4 alin.(1) (10.000 lei / zi, persoană fizică).
Schemă efemeră din template, ștearsă la ieșire.
"""
import datetime
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core import casa_api as _ca

_SCH = "efemer_casa_avans"


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
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,declarant_nume,declarant_prenume,
                           declarant_functie,platitor_tva) VALUES (1,'F1 SRL','RO14399840','s','B','B','e@x.ro','07','4690','P','I','A',true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


CUI_CLIENT = "55229657"   # din comandă (FISCALOS ICONTA SRL)


def _factura(conn, numar="4", serie="F1A", total="242.00", directie="emisa", tip="normal", cui=CUI_CLIENT, data="2026-10-16"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, total, tva, tert_nume, tert_cui, status, tip_operatiune) "
                    "VALUES (%s,%s,%s,%s,%s,0,'FISCALOS ICONTA SRL',%s,'emisa',%s) RETURNING id",
                    (serie, serie + numar, data, directie, Decimal(total), cui, tip))
        return cur.fetchone()[0]


def _sold(conn, fid):
    from core import reconciliere_api as _rec
    return {f["id"]: f["sold"] for f in _rec.facturi_deschise(conn, _SCH)}.get(fid, Decimal(0))


def test_278_incasarea_leaga_factura_si_separa_avansul(conn):
    fid = _factura(conn)
    op = {"data": "2026-10-16", "categorie": "incasare_client", "suma": 6000, "partener": "FISCALOS ICONTA SRL", "cui": CUI_CLIENT,
          "document": "DI-1", "facturi": [{"factura_id": fid, "suma": "242.00"}]}
    r = _ca.adauga(conn, _SCH, op)
    assert not r.get("eroare"), r
    assert [(o["suma"], o["factura_id"], o["avans"]) for o in r["operatiuni"]] == [("242.00", fid, False), ("5758.00", None, True)]
    assert _sold(conn, fid) == 0, "factura F1A4 a devenit încasată (nota legată de ea)"
    assert (r["avans"]["fel"], r["avans"]["tip"], r["avans"]["suma"], r["avans"]["termen"]) == ("fapt", "avans_numerar", "5758.00",
                                                                                                "2026-11-15"), r["avans"]
    with conn.cursor() as cur:
        cur.execute("SELECT i.factura_id, i.descriere, l.cont_debit, l.cont_credit, l.suma::text FROM inregistrari i "
                    "JOIN inregistrari_linii l ON l.inregistrare_id = i.id ORDER BY i.id")
        note = cur.fetchall()
    assert [(n[0], n[2], n[3], n[4]) for n in note] == [(fid, "5311", "4111", "242.00"), (None, "5311", "4111", "5758.00")]
    assert [n[1] for n in note] == ["Încasare de la client — document DI-1 — factura F1A4 din 16.10.2026 — FISCALOS ICONTA SRL",
                                    "Încasare de la client — document DI-1 — avans de la client — FISCALOS ICONTA SRL"], note


def test_278_fara_factura_aleasa_semnaleaza_factura_deschisa_si_avansul(conn):
    _factura(conn)
    p = _ca.previzualizare(conn, _SCH, {"data": "2026-10-16", "categorie": "incasare_client", "suma": 6000, "cui": "RO" + CUI_CLIENT})
    assert [f["numar"] for f in p["facturi"]] == ["F1A4"], p["facturi"]
    assert p["avans"]["suma"] == "5758.00", p["avans"]
    assert p["semnale"] == ["Clientul are 1 factură deschisă (de 242,00 lei). Dispoziția nu e legată de niciuna, deci rămân neîncasate: "
                            "alege factura încasată."], p["semnale"]


def test_278c_plafonul_apare_din_formular_si_se_socoteste_corect(conn):
    p = _ca.previzualizare(conn, _SCH, {"data": "2026-10-16", "categorie": "incasare_client", "suma": 6000, "partener": "X SRL",
                                        "cui": CUI_CLIENT})
    assert [a["cod"] for a in p["avertismente"]] == ["PLAFON_INCASARE_PJ"], p["avertismente"]
    # ridicarea de numerar din bancă NU e încasare de la o persoană (înainte: avertisment fals)
    p = _ca.previzualizare(conn, _SCH, {"data": "2026-10-16", "categorie": "ridicare_banca", "suma": 20000})
    assert [a["cod"] for a in p["avertismente"] if a["cod"] != "PLAFON_SOLD_CASA"] == [], p["avertismente"]
    # persoana fizică (CNP): plafonul de 10.000 lei (Legea 70/2015 art.4 alin.(1)), nu cel de 5.000
    cnp = "1800101420010"
    assert _ca.previzualizare(conn, _SCH, {"data": "2026-10-16", "categorie": "incasare_client", "suma": 8000, "cui": cnp,
                                           "partener": "Ion"})["avertismente"] == []
    assert [a["cod"] for a in _ca.previzualizare(conn, _SCH, {"data": "2026-10-16", "categorie": "incasare_client", "suma": 12000,
                                                              "cui": cnp, "partener": "Ion"})["avertismente"]] == ["PLAFON_PF"]


def test_278_avansul_se_leaga_de_factura_de_avans_iar_nota_validata_nu(conn):
    r = _ca.adauga(conn, _SCH, {"data": "2026-10-16", "categorie": "incasare_client", "suma": 1210, "cui": CUI_CLIENT, "avans": True})
    assert r["operatiuni"][0]["avans"] is True and r["avans"]["suma"] == "1210.00"
    fav = _factura(conn, numar="5", total="1210.00", tip="avans", data="2026-10-20")
    assert _ca.leaga(conn, _SCH, r["id"], fav) == {"ok": True, "factura": "F1A5"}
    assert _sold(conn, fav) == 0
    assert _ca.leaga(conn, _SCH, r["id"], fav)["cod"] == _ca.COD_DEJA_LEGATA
    r2 = _ca.adauga(conn, _SCH, {"data": "2026-10-16", "categorie": "incasare_client", "suma": 100, "cui": CUI_CLIENT, "avans": True,
                                 "document": "DI-2"})
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (r2["inregistrare_id"],))
    assert _ca.leaga(conn, _SCH, r2["id"], _factura(conn, numar="6", total="100.00"))["cod"] == _ca.COD_NOTA_VALIDATA


def test_278_stornarea_redeschide_factura(conn):
    fid = _factura(conn)
    r = _ca.adauga(conn, _SCH, {"data": "2026-10-16", "categorie": "incasare_client", "suma": 242, "cui": CUI_CLIENT,
                                "facturi": [{"factura_id": fid, "suma": "242"}]})
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (r["inregistrare_id"],))
    assert _sold(conn, fid) == 0
    assert not _ca.storneaza(conn, _SCH, r["id"], datetime.date(2026, 10, 17)).get("eroare")
    assert _sold(conn, fid) == Decimal("242.00"), "nota în roșu stinge aceeași factură, în minus"


def test_278_alocarea_refuza_ce_nu_se_poate(conn):
    fid = _factura(conn)
    base = {"data": "2026-10-16", "categorie": "incasare_client", "suma": 300, "cui": CUI_CLIENT}
    assert _ca.adauga(conn, _SCH, dict(base, facturi=[{"factura_id": fid, "suma": "250"}]))["cod"] == _ca.COD_PESTE_SOLD
    prim = _factura(conn, numar="9", directie="primita")
    assert _ca.adauga(conn, _SCH, dict(base, facturi=[{"factura_id": prim, "suma": "10"}]))["cod"] == _ca.COD_FACTURA_NEPOTRIVITA
    assert _ca.adauga(conn, _SCH, dict(base, categorie="ridicare_banca", facturi=[{"factura_id": fid, "suma": "10"}]))["cod"] \
        == _ca.COD_FARA_FACTURI


def test_278b_factura_de_avans_se_conteaza_pe_419(conn):
    """MUTAȚIE: ramura `tip_operatiune in (avans, regularizare_avans)` scoasă din `contare_facturi.genereaza_note` -> 4111 = 707 -> pică."""
    from psycopg2.extras import RealDictCursor
    from core import contare_facturi as _cf
    fav = _factura(conn, numar="7", total="1210.00", tip="avans")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) VALUES (%s,'avans',1,1000,21)", (fav,))
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM facturi WHERE id = %s", (fav,))
        note = _cf.genereaza_note(cur, _SCH, dict(cur.fetchone()), False, "707")
    assert [(n["debit"], n["credit"], str(n["suma"])) for n in note] == [("4111", "419", "1000.00"), ("4111", "4427", "210.00")], note
